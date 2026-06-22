import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.docx_generator import generate_product_blueprint
from agents.clarification_agent import ClarificationAgent
from graphs.state import GraphState
from docs.sprint_plan_generator import generate_sprint_plan_docx
from agents.sprint_planner_agent import SprintPlannerAgent
from agents.requirement_agent import RequirementAgent
from agents.product_strategy_agent import ProductStrategyAgent
from agents.technical_architect_agent import TechnicalArchitectAgent
from agents.validation_agent import ValidationAgent

# Initialize agents
requirement_agent = RequirementAgent()
clarification_agent = ClarificationAgent()
strategy_agent = ProductStrategyAgent()
architect_agent = TechnicalArchitectAgent()
validation_agent = ValidationAgent()
sprint_planner_agent = SprintPlannerAgent()


def requirement_node(state: GraphState):
    print("\n" + "=" * 60)
    print("RUNNING: REQUIREMENT AGENT")
    print("=" * 60)

    result = requirement_agent.run(
        user_idea=state["user_idea"],
        clarification_answers=state.get("clarification_answers", {}),
        feedback=state.get("validation_feedback", [])
    )

    return {
        "requirements": result
    }


def clarification_node(state: GraphState):
    print("\n" + "=" * 60)
    print("RUNNING: CLARIFICATION AGENT")
    print("=" * 60)

    result = clarification_agent.run(state["requirements"])

    return {
        "clarification_questions": result["questions"]
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

    # FIXED: Just pass the answers dict directly. The agent will handle the rest.
    result = validation_agent.run(
        original_idea=state["user_idea"],
        clarification_answers=state.get("clarification_answers", {}),
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
    # ====================================================
    # NEW: TERMINAL DEBUG DUMP
    # ====================================================
    print("\n" + "=" * 80)
    print("🏁 FINAL AGENT PAYLOAD DUMP (BEFORE STOPPING)")
    print("=" * 80)

    print("\n[1] REQUIREMENT AGENT LATEST OUTPUT:")
    if state.get("requirements"):
        print(state["requirements"].model_dump_json(indent=2))
        
    print("\n[2] PRODUCT STRATEGY LATEST OUTPUT:")
    if state.get("strategy"):
        print(state["strategy"].model_dump_json(indent=2))
        
    print("\n[3] TECHNICAL ARCHITECT LATEST OUTPUT:")
    if state.get("architecture"):
        print(state["architecture"].model_dump_json(indent=2))

    print("\n[4] VALIDATION HISTORY:")
    if state.get("validation_feedback"):
        for i, item in enumerate(state["validation_feedback"]):
            print(f"  -> Rejection {i+1}:")
            print(f"     {item}\n")
    print("=" * 80 + "\n")

    # ====================================================
    # ORIGINAL DOCUMENT GENERATION LOGIC
    # ====================================================
    print("=" * 60)
    print("GENERATING PRODUCT BLUEPRINT")
    print("=" * 60)

    os.makedirs("outputs", exist_ok=True)
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
    # Check if we are in a validation loop (loop_count > 0)
    current_loop = state.get("loop_count", 0)
    
    if current_loop > 0:
        print("Bypassing Clarification: Agent is only allowed to ask questions on the first pass.")
        return "strategy_node"

    # Standard routing for the initial pass
    if state["requirements"].needs_clarification:
        return "clarification_node"
    
    return "strategy_node"


def route_after_validation(state: GraphState):
    print("\n" + "=" * 60)
    print("VALIDATION ROUTER")
    print("=" * 60)

    print(f"Current Loop Count: {state.get('loop_count', 0)}")

    if state.get("loop_count", 0) >= 5:
        print("Circuit breaker triggered: Maximum validation loops reached.")
        # FIXED: Route to document_node so the user still gets their files!
        return "document_node"

    if state.get("is_approved", False):
        print("Validation Approved")
        print("Routing To: document_node")
        return "document_node"

    # FIXED: Convert to string, lowercase it, and use 'in' for fuzzy matching.
    # This prevents routing errors if the LLM hallucinates an exact match.
    target = str(state.get("target_node", "none")).lower()
    
    print("Validation Rejected")
    print(f"Routing To: {target}")

    if "requirement" in target:
        return "requirement_node"
    if "strategy" in target:
        return "strategy_node"
    if "architect" in target:
        return "architect_node"

    print("No valid target found. Ending workflow.")
    return END


# Graph Structural Assembly
workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("requirement_node", requirement_node)
workflow.add_node("clarification_node", clarification_node)
workflow.add_node("strategy_node", strategy_node)
workflow.add_node("architect_node", architect_node)
workflow.add_node("validation_node", validation_node)
workflow.add_node("document_node", document_node)
workflow.add_node("sprint_planner_node", sprint_planner_node)

# Set Entry Point
workflow.set_entry_point("requirement_node")

# Routing after Requirement Analysis
workflow.add_conditional_edges(
    "requirement_node",
    route_after_requirement,
    {
        "clarification_node": "clarification_node",
        "strategy_node": "strategy_node"
    }
)

# Restore the internal loop. The graph should naturally flow back
# to the requirement_node after asking clarification questions.
workflow.add_edge(
    "clarification_node",
    "requirement_node"
)

# Standard Linear Pipeline flow
workflow.add_edge("strategy_node", "architect_node")
workflow.add_edge("architect_node", "validation_node")

# Evaluation / Quality Control Loop Routing
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

# Production Deliverables Compilation Execution
workflow.add_edge("document_node", "sprint_planner_node")
workflow.add_edge("sprint_planner_node", END)

# Checkpointer configuration & Compilation
memory = MemorySaver()

# The Native Breakpoint. This tells LangGraph to immediately pause
# execution as soon as the clarification_node finishes its work.
graph = workflow.compile(
    checkpointer=memory,
    interrupt_after=["clarification_node"]
)