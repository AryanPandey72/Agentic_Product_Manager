from pprint import pprint

from graphs.requirement_graph import graph


result = graph.invoke(
    {
        "user_idea": "Build an AI recruiting system",

        "clarification_answers": {},

        "requirements": None,

        "questions": [],

        "next_step": ""
    }
)

pprint(result)