from tools.llm_factory import get_llm
from schemas.strategy_schema import ProductStrategySchema

class ProductStrategyAgent:
    def __init__(self):
        # Using the reasoning tier for complex market and business logic analysis
        self.llm = get_llm(tier="reasoning")

    def run(self, requirements: dict, feedback: list | None = None) -> ProductStrategySchema:
        structured_llm = self.llm.with_structured_output(ProductStrategySchema)
        
        # Normalize inputs (support Pydantic models)
        if hasattr(requirements, "model_dump"):
            finalized_requirements = requirements.model_dump()
        else:
            finalized_requirements = requirements

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
        """

        prompt = f"""
        {system_instructions}
        
        Validated Product Requirements:
        {finalized_requirements}

        {feedback_context}
        """

        response = structured_llm.invoke(prompt)
        return response