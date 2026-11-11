"""Validated request models. The authenticated identity always comes from the JWT."""
from pydantic import BaseModel, ConfigDict, Field

class SafeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

class JobDescriptionRequest(SafeRequest):
    jd_text: str = Field(min_length=20, max_length=10000)

class ProjectRecommendationRequest(SafeRequest):
    jd_text: str = Field(min_length=20, max_length=10000)
    current_skills: list[str] | None = Field(default=None, max_length=30)

class ImplementationPlanRequest(SafeRequest):
    project_title: str = Field(min_length=3, max_length=150)
    project_description: str | None = Field(default=None, max_length=4000)
    tech_stack: str | None = Field(default=None, max_length=500)

class ProjectUpgradeRequest(SafeRequest):
    project_description: str = Field(min_length=20, max_length=6000)
    current_tech_stack: str | None = Field(default=None, max_length=500)
