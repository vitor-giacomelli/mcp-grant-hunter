from pydantic import BaseModel, Field
from typing import Optional, List

# --- Input Models ---


class GrantsQueryInput(BaseModel):
    """Input for /query_grants endpoint."""
    keyword: str = Field(
        ...,
        max_length=150,
        description="Primary search term for grants."
    )
    max_results: int = Field(
        20,
        ge=1,
        le=50,
        description="Maximum number of grant opportunities to return."
    )
    focus_area: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional secondary filter (e.g., 'Clean Energy')."
    )


class PitchGenerateInput(BaseModel):
    """Input for /generate_pitch endpoint."""
    startup_name: str = Field(..., max_length=100)
    focus_area: str = Field(..., max_length=100)
    grant_title: str = Field(..., max_length=200)


class GoogleServicesInput(BaseModel):
    """Input for /manage_google_services endpoint."""
    grant_title: str = Field(..., max_length=200)
    deadline_date: str = Field(
        ...,
        description="Date string for the grant deadline."
    )
    oauth_token: str = Field(
        ...,
        description="OAuth access token for Google Services."
    )


# --- Output Models ---


class GrantOpportunity(BaseModel):
    """Standardized output structure for a single grant."""
    id: str
    title: str
    agency: str
    close_date: str
    status: str
    data_status: str = Field(
        "COMPLETE",
        description="Indicates if data is complete or INCOMPLETE_SYNOPSIS_ONLY."
    )


class GrantsQueryOutput(BaseModel):
    """Output for /query_grants endpoint."""
    results: List[GrantOpportunity]
    total_count: int
    execution_time_ms: float


class PitchGenerateOutput(BaseModel):
    """Output for /generate_pitch endpoint."""
    pitch_draft: str
    model_used: str
    status: str

    model_config = {
        "protected_namespaces": ()
    }
