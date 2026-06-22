from tools.llm_factory import get_llm
from schemas.strategy_schema import ProductStrategySchema

class ProductStrategyAgent:
    def __init__(self):
        self.llm = get_llm(tier="reasoning")

    # FIXED: Added clarification_answers to the parameters
    def run(self, requirements: dict, clarification_answers: dict | None = None, feedback: list | None = None) -> ProductStrategySchema:
        structured_llm = self.llm.with_structured_output(ProductStrategySchema)
        
        if hasattr(requirements, "model_dump"):
            finalized_requirements = requirements.model_dump()
        else:
            finalized_requirements = requirements

        # FIXED: Build the Q&A transcript
        qa_context = "No additional clarifications provided."
        if clarification_answers:
            qa_lines = [f"Q: {q}\nA: {ans}" for q, ans in clarification_answers.items()]
            qa_context = "\n\n".join(qa_lines)

        feedback_context = ""
        if feedback:
            feedback_context = f"""

            Validation Feedback (consider these when updating strategy):

            {feedback}

            """

        system_instructions = """
        You are a Principal Product Strategist. 
        Your job is to take a validated Product Requirements Document (PRD) payload and generate a lean, highly realistic business strategy.
        
        Rules:
        - Avoid fluff, buzzwords, or generic business text.
        - Enforce absolute minimalism: adhere strictly to the Max item limits specified in the schema.
        - Ensure monetization and GTM strategies match the target users and constraints provided.
        - Pay close attention to the explicitly stated USER CLARIFICATIONS if given.
        """

        # FIXED: Inject the USER CLARIFICATIONS into the prompt
        prompt = f"""
        {system_instructions}
        
        USER CLARIFICATIONS:
        {qa_context}
        
        Validated Product Requirements:
        {finalized_requirements}

        {feedback_context}
        """

        response = structured_llm.invoke(prompt)
        return response