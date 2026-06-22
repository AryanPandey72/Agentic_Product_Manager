from tools.llm_factory import get_llm
from schemas.requirement_schema import RequirementSchema
from prompts.requirement_prompt import REQUIREMENT_PROMPT


class RequirementAgent:

    def __init__(self):
        self.llm = get_llm()

    def run(
        self,
        user_idea: str,
        clarification_answers: dict | None = None,
        feedback: list | None = None
    ):

        structured_llm = self.llm.with_structured_output(
            RequirementSchema
        )

        clarification_context = ""
        feedback_context = ""

        if clarification_answers:
            clarification_context = f"""

            Additional User Clarifications:

            {clarification_answers}

            Use these clarifications to improve and refine
            the requirements.

            """

        if feedback:
            feedback_context = f"""

            Validation Feedback (revise the requirements using these points):

            {feedback}

            """

        response = structured_llm.invoke(
            f"""
            {REQUIREMENT_PROMPT}

            Business Idea:
            {user_idea}

            {clarification_context}

            {feedback_context}
            """
        )

        return response