from pydantic import BaseModel
from typing import List


class RequirementSchema(BaseModel):
    needs_clarification: bool
    
    clarification_questions: List[str]

    problem_statement: str

    target_users: List[str]

    business_goals: List[str]

    constraints: List[str]

    success_metrics: List[str]