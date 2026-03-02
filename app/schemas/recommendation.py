"""Recommendation Pydantic schemas."""

from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    """Request schema for recommendation endpoint."""

    query: str = Field(..., min_length=1, description="Job query or description")
    top_k: int = Field(default=10, ge=1, le=20, description="Number of recommendations")
    # SHL catalog filters (Job Family, Job Level, Industry, Language, Job Category)
    job_family: list[str] = Field(default_factory=list, description="Filter by job family")
    job_level: list[str] = Field(default_factory=list, description="Filter by job level")
    industry: list[str] = Field(default_factory=list, description="Filter by industry")
    language: list[str] = Field(default_factory=list, description="Filter by language")
    job_category: list[str] = Field(default_factory=list, description="Filter by job category")


class RecommendationItem(BaseModel):
    """Single recommendation item."""

    assessment_name: str
    assessment_url: str
    score: float | None = None
    test_type: list[str] = Field(default_factory=list)


class RecommendResponse(BaseModel):
    """Response schema for recommendations."""

    recommendations: list[RecommendationItem]
