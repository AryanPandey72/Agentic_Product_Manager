from schemas.sprint_schema import SprintPlanSchema

from tools.llm_factory import get_llm


class SprintPlannerAgent:

    def __init__(self):

        self.llm = get_llm("reasoning")

    def run(
        self,
        requirements,
        strategy,
        architecture,
        feedback=None
    ):

        feedback_text = ""

        if feedback:
            feedback_text = "\n".join(feedback)

        system_instructions = """
        You are a Senior Agile Product Manager and Delivery Lead.

        Your responsibility is to convert validated product requirements,
        strategy, architecture and user clarifications(if given) into a realistic MVP delivery plan.

        RULES:

        1. ONLY plan features contained within the MVP Scope.
        2. Do not invent future roadmap features.
        3. Organize the work into sequential Sprints.
        4. Each Sprint must have:
            - sprint_number
            - sprint_goal
            - one or more Epics
        5. Earlier Sprints should contain foundational capabilities required by later Sprints.
        6. Consider technical and business dependencies when assigning work to Sprints.
        7. Create logical Epics representing major product capabilities.
        8. Each Epic must contain multiple User Stories whenever appropriate.
        9. Every User Story must:
            - Follow the format:
            "As a <user>, I want <goal>, so that <benefit>"
            - Include clear acceptance criteria.
        10. Acceptance Criteria must be testable.
        11. Use Requirements, Strategy, Architecture, API Specifications, Database Design, and Feature Mappings when generating stories.
        12. Focus on business functionality, not engineering implementation tasks.
        13. Do not create stories for infrastructure, deployment, CI/CD, monitoring, logging, observability, or internal technical work.
        14. The output should represent a realistic implementation sequence for a software team.
        15. Do not place all Epics into a single Sprint.
        16. Distribute work across multiple Sprints based on dependencies.
        17. Authentication, user management, core data entities, and platform foundations should generally appear before
        advanced capabilities such as forecasting, recommendations, analytics, or optimization.

        If feedback is provided, revise the sprint plan accordingly.
        """
        user_prompt = f"""
        REQUIREMENTS

        {requirements.model_dump_json(indent=2)}

        USER CLARIFICATIONS
        {qa_context}

        PRODUCT STRATEGY

        {strategy.model_dump_json(indent=2)}

        TECHNICAL ARCHITECTURE

        {architecture.model_dump_json(indent=2)}

        VALIDATION FEEDBACK

        {feedback_text}
        """

        response = self.llm.with_structured_output(
            SprintPlanSchema
        ).invoke(
            [
                {
                    "role": "system",
                    "content": system_instructions
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        return response