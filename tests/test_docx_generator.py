from pprint import pprint
from graphs.requirement_graph import graph
config = {
    "configurable": {
        "thread_id": "test_docx"
    }
}
result = graph.invoke(
    {
        "user_idea": (
            "Build a supply chain optimization platform "
            "that tracks inventory across warehouses, "
            "forecasts demand, identifies potential shortages, "
            "and recommends inventory redistribution strategies."
        ),
        "loop_count": 0
    },
    config=config
)
pprint(result)