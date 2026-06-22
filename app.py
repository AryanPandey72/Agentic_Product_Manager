import streamlit as st
import uuid
from graphs.requirement_graph import graph

st.set_page_config(
    page_title="Agentic Product Manager",
    layout="wide"
)

st.title("Agentic Product Manager")

# Initialize a unique thread ID in session state if it doesn't exist
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())


def get_config():
    """Helper function to dynamically build the graph config with the latest thread_id."""
    return {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        }
    }


def run_autonomous_agent(payload_or_none):
    current_config = get_config()
    
    with st.status(
        "Starting Agent Workflow...",
        expanded=True
    ) as status:

        for event in graph.stream(
            payload_or_none,
            config=current_config
        ):

            if "requirement_node" in event:
                status.update(
                    label=(
                        "Requirement Agent: "
                        "Analyzing business requirements..."
                    ),
                    state="running"
                )

            elif "clarification_node" in event:
                status.update(
                    label=(
                        "Requirement Agent: "
                        "Additional clarification required..."
                    ),
                    state="running"
                )

            elif "strategy_node" in event:
                status.update(
                    label=(
                        "Product Strategy Agent: "
                        "Building product strategy..."
                    ),
                    state="running"
                )

            elif "architect_node" in event:
                status.update(
                    label=(
                        "Technical Architect Agent: "
                        "Designing architecture..."
                    ),
                    state="running"
                )

            elif "validation_node" in event:
                validation_result = event["validation_node"]

                loop_count = validation_result.get(
                    "loop_count",
                    1
                )

                is_approved = validation_result.get(
                    "is_approved",
                    False
                )

                target_node = validation_result.get(
                    "target_node",
                    "none"
                )

                if not is_approved:
                    route_name = {
                        "requirement": "Requirement Agent",
                        "strategy": "Product Strategy Agent",
                        "architect": "Technical Architect Agent"
                    }.get(
                        target_node,
                        target_node
                    )

                    status.update(
                        label=(
                            f"Validation Agent: "
                            f"Rejected (Loop #{loop_count}) → "
                            f"Routing back to {route_name}"
                        ),
                        state="running"
                    )

                else:
                    status.update(
                        label=(
                            f"Validation Agent: "
                            f"Approved after "
                            f"{loop_count} cycle(s)"
                        ),
                        state="running"
                    )

            elif "document_node" in event:
                status.update(
                    label=(
                        "Document Generator: "
                        "Creating Product Blueprint..."
                    ),
                    state="running"
                )

            elif "sprint_planner_node" in event:
                status.update(
                    label=(
                        "Sprint Planner: "
                        "Creating Sprint Plan..."
                    ),
                    state="running"
                )

        status.update(
            label="Workflow Completed",
            state="complete"
        )

    # Capture the latest snapshot after streaming ends
    st.session_state["current_state"] = graph.get_state(current_config)
    st.rerun()


idea = st.text_area("Describe your product idea", height=200)

if st.button("Analyze Idea", use_container_width=True):
    st.session_state["thread_id"] = str(uuid.uuid4())
    
    if "current_state" in st.session_state:
        del st.session_state["current_state"]
        
    run_autonomous_agent({
        "user_idea": idea,
        "clarification_answers": {},
        "loop_count": 0
    })

# --- DUMB UI LOGIC ---
if "current_state" in st.session_state:
    current_config = get_config()
    state = graph.get_state(current_config)

    # 1. CHECK IF GRAPH IS PAUSED (WAITING FOR HUMAN)
    if state.next and "requirement_node" in state.next:
        st.subheader("Requirement Agent Needs Clarification")

        questions = state.values.get("clarification_questions", [])
        answers = {}

        for i, q in enumerate(questions):
            answers[q] = st.text_input(q, key=f"q_{i}_{state.values.get('loop_count', 0)}")

        if st.button("Submit Answers", use_container_width=True):
            # Inject the answers into the frozen state
            graph.update_state(
                current_config,
                {"clarification_answers": answers}
            )
            
            # Resume the graph with a payload of None. 
            # LangGraph knows exactly where it left off!
            run_autonomous_agent(None)

    # 2. CHECK IF GRAPH REACHED THE END
    elif not state.next and "document_path" in state.values:
        st.success("Workflow Completed Successfully")
        final_loops = state.values.get("loop_count", 1)
        st.info(f"Validation completed after {final_loops} cycle(s).")

        st.subheader("Generated Deliverables")

        if state.values.get("document_path"):
            with open(state.values["document_path"], "rb") as file:
                st.download_button(
                    label="📄 Download Product Blueprint",
                    data=file.read(),
                    file_name="Product_Blueprint.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        if state.values.get("sprint_plan_path"):
            with open(state.values["sprint_plan_path"], "rb") as file:
                st.download_button(
                    label="📄 Download Sprint Plan",
                    data=file.read(),
                    file_name="Sprint_Plan.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )