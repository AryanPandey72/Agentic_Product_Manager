from pprint import pprint

from agents.requirement_agent import RequirementAgent

agent = RequirementAgent()

user_idea = "Build an AI recruiting system"

clarification_answers = {
    "Who are the target users?":
    "Recruiters",

    "Which recruiting tasks should AI support?":
    "Resume screening and candidate ranking",

    "What types of roles or industries will the system focus on?":
    "Technology roles"
}

result = agent.run(
    user_idea,
    clarification_answers
)

pprint(
    result.model_dump()
)