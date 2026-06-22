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

    # NEW: Added original_idea to the parameters
    def run(self, original_idea: str, requirements: dict, strategy: dict, architecture: dict) -> ValidationResult:
        structured_llm = self.llm.with_structured_output(ValidationResult)

        system_instructions = """
        You are a Principal Staff Engineer and strict system reviewer.
        Evaluate the entire product payload against the ORIGINAL USER IDEA.
        
        CRITIQUE & ROUTING CRITERIA:
        
        1. CONTEXT RETENTION CHECK (Target: "requirement" or "strategy")
        - Look at the ORIGINAL IDEA. Did the user specify a company or industry (e.g., Toyota)? 
        - If YES: The requirements/strategy MUST use specific terminology for that domain. If it reverted to generic B2B fluff, set target_node="requirement" and reject.
        - If NO: The requirements/strategy should remain appropriately broad. If the agents hallucinated a specific industry that wasn't asked for, set target_node="requirement" and reject.

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

        # NEW: Injecting the original_idea into the prompt
        prompt = f"""
        {system_instructions}
        
        === ORIGINAL IDEA ===
        {original_idea}
        
        === REQUIREMENTS ===
        {requirements}
        
        === STRATEGY ===
        {strategy}
        
        === ARCHITECTURE ===
        {architecture}
        """
        
        return structured_llm.invoke(prompt)