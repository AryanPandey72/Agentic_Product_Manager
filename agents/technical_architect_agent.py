from tools.llm_factory import get_llm
from schemas.architecture_schema import ArchitectureSchema

class TechnicalArchitectAgent:

    def __init__(self):
        self.llm = get_llm(tier="reasoning")

    # FIXED: Added clarification_answers to the parameters
    def run(
        self,
        requirements: dict,
        strategy: dict,
        clarification_answers: dict | None = None,
        feedback: list | None = None
    ) -> ArchitectureSchema:

        structured_llm = self.llm.with_structured_output(ArchitectureSchema)

        if hasattr(requirements, "model_dump"):
            finalized_requirements = requirements.model_dump()
        else:
            finalized_requirements = requirements

        if hasattr(strategy, "model_dump"):
            product_strategy = strategy.model_dump()
        else:
            product_strategy = strategy

        # FIXED: Build the Q&A transcript
        qa_context = "No additional clarifications provided."
        if clarification_answers:
            qa_lines = [f"Q: {q}\nA: {ans}" for q, ans in clarification_answers.items()]
            qa_context = "\n\n".join(qa_lines)

        feedback_context = ""
        if feedback:
            feedback_context = f"""
            Validation Feedback:

            {feedback}

            Apply every correction requested by the validator.
            """

        system_instructions = """
        You are a Principal Software Architect.

        Your responsibility is to transform validated
        business requirements and product strategy into
        a production-ready technical architecture.

        GENERAL RULES

        - Design RESTful API endpoints.
        - Create a normalized database schema.
        - Recommend an appropriate technology stack.
        - Define infrastructure requirements.
        - Define security requirements.
        - Ensure architecture supports all MVP features.

        FEATURE TRACEABILITY RULE (CRITICAL)

        The Product Strategy contains an MVP Scope.

        Every MVP feature MUST be implemented.

        For EACH MVP feature:

        1. Identify supporting database tables.
        2. Identify supporting API endpoints.
        3. Create a FeatureMapping object.

        Every MVP feature must appear exactly once inside
        feature_mappings.

        Every FeatureMapping must reference:

        - feature_name
        - database_tables
        - api_endpoints

        COVERAGE RULE

        No MVP feature may be left unmapped.

        If an MVP feature exists in strategy but is not
        represented inside feature_mappings,
        the architecture is considered incomplete.

        CONSISTENCY RULE

        Every table referenced inside feature_mappings
        must exist inside database_schema.

        Every endpoint referenced inside feature_mappings
        must exist inside api_specifications.

        SECURITY RULE

        Authentication and authorization mechanisms
        must align with the target users and
        sensitivity of the business domain.

        OUTPUT QUALITY RULE

        Do not generate placeholder names.

        Bad:
        - table1
        - api1

        Good:
        - candidates
        - applications
        - job_postings

        Think like a Principal Architect preparing
        a design review document for engineering leadership.
        """


        # FIXED: Inject USER CLARIFICATIONS into the prompt
        prompt = f"""
        {system_instructions}

        USER CLARIFICATIONS
        {qa_context}

        VALIDATED REQUIREMENTS
        {finalized_requirements}

        PRODUCT STRATEGY
        {product_strategy}

        {feedback_context}
        """

        return structured_llm.invoke(prompt)
    






    