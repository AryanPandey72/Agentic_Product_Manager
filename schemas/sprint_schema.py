from pydantic import BaseModel
from typing import List


class UserStory(BaseModel):
    title: str
    description: str
    acceptance_criteria: List[str]


class Epic(BaseModel):
    title: str
    description: str
    stories: List[UserStory]


class Sprint(BaseModel):
    sprint_number: int
    sprint_goal: str
    epics: List[Epic]


class SprintPlanSchema(BaseModel):
    sprints: List[Sprint]