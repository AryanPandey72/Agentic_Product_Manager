from tools.llm_factory import get_llm
from pydantic import BaseModel, Field
from typing import Literal

class ValidationResult(BaseModel):
    is_approved: bool = Field(description="True if the entire stack is perfect. False otherwise.")
    target_node: Literal["requirement", "strategy", "architect", "none"] = Field(
        description="If rejected, which agent is responsible for the root cause? Use 'none' if approved."
    )
    feedback: list[str] = Field(description="Specific, actionable feedback for the target node.")

class ValidationAgent:
    def __init__(self):
        self.llm = get_llm(tier="reasoning") 

    # FIXED: Removed the redundant clarification_questions parameter
    def run(self, original_idea: str, clarification_answers: dict, requirements: dict, strategy: dict, architecture: dict) -> ValidationResult:
        structured_llm = self.llm.with_structured_output(ValidationResult)

        # FIXED: Bulletproof and clean dictionary iteration
        qa_context = "No additional clarifications provided."
        if clarification_answers:
            qa_lines = [f"Q: {q}\nA: {ans}" for q, ans in clarification_answers.items()]
            qa_context = "\n\n".join(qa_lines)

        system_instructions = """
        You are a Principal Staff Engineer and strict system reviewer.
        Evaluate the entire product payload against the ORIGINAL USER IDEA and any USER CLARIFICATIONS.
        
        CRITIQUE & ROUTING CRITERIA:
        
        1. CONTEXT RETENTION CHECK (Target: "requirement" or "strategy")
        - Review the ORIGINAL IDEA and USER CLARIFICATIONS. 
        - The requirements and strategy MUST incorporate all specific requests, features, or constraints provided by the user.
        - If the agents hallucinated features not requested, or if they dropped specific features the user explicitly asked for, set target_node="requirement" and reject.

        2. ARCHITECTURE CHECK (Target: "architect")
        - Constraints: Does the tech stack violate any stated business constraints?
        - Data Flow: Does every API endpoint have a corresponding database table?
        - If technically flawed, set target_node="architect" and list the technical corrections.

        3. MVP FEATURE COVERAGE CHECK (Target: "architect")
        - Review the MVP Scope from Product Strategy.
        - Every MVP feature must have a FeatureMapping entry.
        - Every FeatureMapping must reference supporting API endpoints.
        - Every FeatureMapping must reference supporting database tables.
        - Verify that all MVP features are represented in the architecture.
        - If any MVP feature is missing implementation, reject the architecture.
        - Set target_node="architect".
        - Provide explicit feedback identifying the missing feature and required implementation.
        
        4. DOMAIN CAPABILITY VALIDATION CHECK (Target: "architect")
        -Review the Original Idea, Requirements, and Product Strategy.
        -Identify the core capabilities the product claims to provide.
        -Determine whether the architecture contains the necessary mechanisms to realistically deliver those capabilities.
        -Do not require specific technologies, frameworks, vendors, or implementation patterns.
        -Focus on outcomes.
        -Ask:
        'Can this architecture realistically deliver the value promised by the product?'
        If a critical capability cannot be explained by the architecture: Reject.
        Set target_node="architect".
        Provide explicit feedback describing the missing capability and the missing architectural support.

        If flawless, set is_approved=True and target_node="none".
        """

        prompt = f"""
        {system_instructions}
        
        NOTE: The user provided additional clarifications below. Treat these as an extension of their ORIGINAL IDEA.

        === ORIGINAL IDEA ===
        {original_idea}

        === USER CLARIFICATIONS ===
        {qa_context}
        
        === REQUIREMENTS ===
        {requirements}
        
        === STRATEGY ===
        {strategy}
        
        === ARCHITECTURE ===
        {architecture}
        """
        
        return structured_llm.invoke(prompt)