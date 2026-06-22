from agents.requirement_agent import RequirementAgent
from pprint import pprint

agent = RequirementAgent()

ideas = [
    "Build a fleet management platform for logistics companies"
]

for idea in ideas:

    print("\n" + "="*60)

    print(f"\nINPUT:\n{idea}\n")

    result = agent.run(idea)

    pprint(result.model_dump())