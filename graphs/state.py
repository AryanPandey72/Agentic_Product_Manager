from typing import TypedDict, Annotated
import operator

from schemas.requirement_schema import RequirementSchema
from schemas.strategy_schema import ProductStrategySchema
from schemas.architecture_schema import ArchitectureSchema
from schemas.sprint_schema import SprintPlanSchema


class GraphState(TypedDict, total=False):

    user_idea: str

    clarification_questions: list[str]
    clarification_answers: dict

    requirements: RequirementSchema | None
    strategy: ProductStrategySchema | None
    architecture: ArchitectureSchema | None
    sprint_plan: SprintPlanSchema | None

    document_path: str | None
    sprint_plan_path: str | None

    validation_feedback: Annotated[
        list[str],
        operator.add
    ]

    is_approved: bool
    target_node: str
    loop_count: int