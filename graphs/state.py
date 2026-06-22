from typing import TypedDict, Annotated
import operator
from schemas.requirement_schema import RequirementSchema
from schemas.strategy_schema import ProductStrategySchema
from schemas.architecture_schema import ArchitectureSchema 
from schemas.sprint_schema import SprintPlanSchema

class GraphState(TypedDict):
    # Core inputs
    user_idea: str
    clarification_answers: dict
    questions: list[str]
    next_step: str
    
    # Generated Assets
    requirements: RequirementSchema | None
    strategy: ProductStrategySchema | None
    architecture: ArchitectureSchema | None 
    sprint_plan: SprintPlanSchema | None
    document_path: str | None
    sprint_plan_path: str | None

    # Critique & Reject Loop Variables
    validation_feedback: Annotated[list[str], operator.add]
    is_approved: bool
    target_node: str # NEW: Directs the graph back to 'requirement', 'strategy', or 'architect'
    loop_count: int
    