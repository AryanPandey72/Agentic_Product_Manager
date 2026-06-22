from pprint import pprint

from graphs.requirement_graph import graph

config = {
    "configurable": {
        "thread_id": "full_pipeline_test"
    }
}

result = graph.invoke(
    {
        "user_idea": (
            "Build a clinic appointment management platform that allows patients "
            "to book appointments, doctors to manage schedules, receptionists to "
            "coordinate visits, and administrators to manage clinic operations. "
            "The platform should support appointment booking, doctor availability "
            "management, patient records, appointment reminders, billing summaries, "
            "and operational dashboards.\n\n"
            "Constraints:\n"
            "- Development team size: 5 people\n"
            "- Sprint duration: 2 weeks\n"
            "- MVP must be delivered within 8 weeks."
        ),
        "loop_count": 0
    },
    config=config
)

print("\n=== DOCUMENT PATH ===")
print(result.get("document_path"))

print("\n=== SPRINT PLAN PATH ===")
print(result.get("sprint_plan_path"))

print("\n=== EPICS GENERATED ===")
pprint(result["sprint_plan"])