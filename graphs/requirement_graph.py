from agents.docx_generator import generate_product_blueprint
import os

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graphs.state import GraphState
from docs.sprint_plan_generator import generate_sprint_plan_docx
from agents.sprint_planner_agent import SprintPlannerAgent
from agents.requirement_agent import RequirementAgent
from agents.product_strategy_agent import ProductStrategyAgent
from agents.technical_architect_agent import TechnicalArchitectAgent
from agents.validation_agent import ValidationAgent

requirement_agent = RequirementAgent()
strategy_agent = ProductStrategyAgent()
architect_agent = TechnicalArchitectAgent()
validation_agent = ValidationAgent()
sprint_planner_agent = SprintPlannerAgent()


def requirement_node(state: GraphState):
    print("\n" + "=" * 60)
    print("RUNNING: REQUIREMENT AGENT")

    result = requirement_agent.run(
        user_idea=state["user_idea"],
        feedback=state.get("validation_feedback", [])
    )

    return {
        "requirements": result
    }


def strategy_node(state: GraphState):
    print("\n" + "=" * 60)
    print("RUNNING: PRODUCT STRATEGY AGENT")
    print("=" * 60)

    result = strategy_agent.run(
        requirements=state["requirements"],
        feedback=state.get("validation_feedback", [])
    )

    return {
        "strategy": result
    }


def architect_node(state: GraphState):
    print("\n" + "=" * 60)
    print("RUNNING: TECHNICAL ARCHITECT AGENT")
    print(f"CURRENT LOOP: {state['loop_count']}")
    print("=" * 60)

    result = architect_agent.run(
        requirements=state["requirements"],
        strategy=state["strategy"],
        feedback=state.get("validation_feedback", [])
    )

    return {
        "architecture": result
    }


def validation_node(state: GraphState):
    print("\n" + "=" * 60)
    print("RUNNING: VALIDATION AGENT")
    print(f"CURRENT LOOP: {state['loop_count']}")
    print("=" * 60)

    current_count = state.get("loop_count", 0) + 1

    result = validation_agent.run(
        original_idea=state["user_idea"],
        requirements=state["requirements"].model_dump(),
        strategy=state["strategy"].model_dump(),
        architecture=state["architecture"].model_dump()
    )

    return {
        "is_approved": result.is_approved,
        "validation_feedback": result.feedback,
        "target_node": result.target_node,
        "loop_count": current_count
    }


def document_node(state: GraphState):
    print("\n" + "=" * 60)
    print("GENERATING PRODUCT BLUEPRINT")
    print("=" * 60)

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    output_path = "outputs/Product_Blueprint.docx"

    generate_product_blueprint(
        requirements=state["requirements"],
        strategy=state["strategy"],
        architecture=state["architecture"],
        output_path=output_path
    )

    return {
        "document_path": output_path
    }

def sprint_planner_node(state: GraphState):
    print("\n" + "=" * 60)
    print("RUNNING: SPRINT PLANNER")
    print("=" * 60)

    result = sprint_planner_agent.run(
        requirements=state["requirements"],
        strategy=state["strategy"],
        architecture=state["architecture"]
    )

    output_path = "outputs/Sprint_Plan.docx"

    generate_sprint_plan_docx(
        sprint_plan=result,
        output_path=output_path
    )

    return {
        "sprint_plan": result,
        "sprint_plan_path": output_path
    }

def route_after_requirement(state: GraphState):

    if state["requirements"].needs_clarification:
        return END

    return "strategy_node"


def route_after_validation(state: GraphState):

    print("\n" + "=" * 60)
    print("VALIDATION ROUTER")
    print("=" * 60)

    print(
        f"Current Loop Count: {state.get('loop_count', 0)}"
    )

    if state.get("loop_count", 0) >= 5:

        print(
            "Circuit breaker triggered: "
            "Maximum validation loops reached."
        )

        return END

    if state.get("is_approved", False):

        print("Validation Approved")
        print("Routing To: document_node")

        return "document_node"

    target = state.get(
        "target_node",
        "none"
    )

    print("Validation Rejected")
    print(f"Routing To: {target}")

    if target == "requirement":
        return "requirement_node"

    if target == "strategy":
        return "strategy_node"

    if target == "architect":
        return "architect_node"

    print("No valid target found. Ending workflow.")

    return END

workflow = StateGraph(GraphState)

workflow.add_node(
    "requirement_node",
    requirement_node
)

workflow.add_node(
    "strategy_node",
    strategy_node
)

workflow.add_node(
    "architect_node",
    architect_node
)

workflow.add_node(
    "validation_node",
    validation_node
)

workflow.add_node(
    "document_node",
    document_node
)

workflow.add_node(
    "sprint_planner_node",
    sprint_planner_node
)

workflow.set_entry_point(
    "requirement_node"
)

workflow.add_conditional_edges(
    "requirement_node",
    route_after_requirement,
    {
        END: END,
        "strategy_node": "strategy_node"
    }
)

workflow.add_edge(
    "strategy_node",
    "architect_node"
)

workflow.add_edge(
    "architect_node",
    "validation_node"
)

workflow.add_conditional_edges(
    "validation_node",
    route_after_validation,
    {
        "requirement_node": "requirement_node",
        "strategy_node": "strategy_node",
        "architect_node": "architect_node",
        "document_node": "document_node",
        END: END
    }
)

workflow.add_edge(
    "document_node",
    "sprint_planner_node"
)

workflow.add_edge(
    "sprint_planner_node",
    END
)
memory = MemorySaver()

graph = workflow.compile(
    checkpointer=memory
)