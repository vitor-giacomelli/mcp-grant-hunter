from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any

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

    @field_validator("deadline_date")
    @classmethod
    def validate_deadline_date(cls, value: str) -> str:
        """Accept only supported deadline date formats."""
        supported_formats = ("%B %d, %Y", "%Y-%m-%d")
        for fmt in supported_formats:
            try:
                datetime.strptime(value, fmt)
                return value
            except ValueError:
                continue
        raise ValueError(
            "deadline_date must match '%B %d, %Y' or '%Y-%m-%d'."
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
    fallback_used: bool = Field(
        False,
        description="True when results come from fallback data instead of live upstream."
    )
    data_source: str = Field(
        "grants_gov",
        description="Source of data for this response (e.g., grants_gov, mock_fallback)."
    )


class PitchGenerateOutput(BaseModel):
    """Output for /generate_pitch endpoint."""
    pitch_draft: str
    model_used: str
    status: str

    model_config = {
        "protected_namespaces": ()
    }


class GoogleServicesOutput(BaseModel):
    """Typed output for /manage_google_services endpoint."""
    gmail_status: Optional[str] = Field(
        None,
        description="Status for Gmail operation (SUCCESS, FAILED, AUTH_ERROR, SKIPPED)."
    )
    calendar_status: Optional[str] = Field(
        None,
        description="Status for Calendar operation (SUCCESS, FAILED, AUTH_ERROR, SKIPPED)."
    )
    draft_link: Optional[str] = Field(
        None,
        description="Link to created Gmail draft when available."
    )
    event_link: Optional[str] = Field(
        None,
        description="Link to created Calendar event when available."
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Operation-level errors captured during execution."
    )
    status: Optional[str] = Field(
        None,
        description="Top-level status for critical failures."
    )
    error: Optional[str] = Field(
        None,
        description="Top-level critical error message when present."
    )


class ErrorEnvelope(BaseModel):
    """Standardized machine-readable error contract."""
    code: str = Field(..., description="Stable machine-readable error code.")
    message: str = Field(..., description="Human-readable summary of the error.")
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional diagnostic details for clients."
    )
