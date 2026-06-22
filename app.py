import streamlit as st
from graphs.requirement_graph import graph

st.set_page_config(
    page_title="Agentic Product Manager",
    layout="wide"
)

st.title("Agentic Product Manager")

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = "session_1"

config = {
    "configurable": {
        "thread_id": st.session_state["thread_id"]
    }
}


def run_autonomous_agent(payload_or_none):

    with st.status(
        "Starting Agent Workflow...",
        expanded=True
    ) as status:

        for event in graph.stream(
            payload_or_none,
            config=config
        ):

            if "requirement_node" in event:

                status.update(
                    label=(
                        "Requirement Agent: "
                        "Analyzing business requirements..."
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

    st.session_state["current_state"] = graph.get_state(
        config
    )

    st.rerun()


idea = st.text_area(
    "Describe your product idea",
    height=200
)

if st.button(
    "Analyze Idea",
    use_container_width=True
):

    run_autonomous_agent(
        {
            "user_idea": idea,
            "clarification_answers": {}
        }
    )


if "current_state" in st.session_state:

    state = graph.get_state(config)

    if state.next == ("clarification",):

        st.subheader(
            "Requirement Agent Needs Clarification"
        )

        questions = (
            state.values["requirements"]
            .clarification_questions
        )

        answers = {}

        for i, q in enumerate(questions):

            answers[q] = st.text_input(
                q,
                key=f"q_{i}"
            )

        if st.button("Submit Answers"):

            graph.update_state(
                config,
                {
                    "clarification_answers": answers
                }
            )

            run_autonomous_agent(None)

    elif not state.next and "architecture" in state.values:

        st.success(
            "Workflow Completed Successfully"
        )

        final_loops = state.values.get(
            "loop_count",
            1
        )

        st.info(
            f"Validation completed after "
            f"{final_loops} cycle(s)."
        )

        st.subheader(
            "Generated Deliverables"
        )

        if (
            "document_path" in state.values
            and state.values["document_path"]
        ):

            with open(
                state.values["document_path"],
                "rb"
            ) as file:

                st.download_button(
                    label="📄 Download Product Blueprint",
                    data=file.read(),
                    file_name="Product_Blueprint.docx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    )
                )

        if (
            "sprint_plan_path" in state.values
            and state.values["sprint_plan_path"]
        ):

            with open(
                state.values["sprint_plan_path"],
                "rb"
            ) as file:

                st.download_button(
                    label="📄 Download Sprint Plan",
                    data=file.read(),
                    file_name="Sprint_Plan.docx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    )
                )

        with st.expander(
            "Requirements"
        ):

            st.json(
                state.values["requirements"]
                .model_dump()
            )

        with st.expander(
            "Product Strategy"
        ):

            st.json(
                state.values["strategy"]
                .model_dump()
            )

        with st.expander(
            "Technical Architecture"
        ):

            st.json(
                state.values["architecture"]
                .model_dump()
            )

        if "sprint_plan" in state.values:

            with st.expander(
                "Sprint Plan"
            ):

                st.json(
                    state.values["sprint_plan"]
                    .model_dump()
                )