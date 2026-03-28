from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator
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
    oauth_token: Optional[str] = Field(
        None,
        description=(
            "OAuth access token for Google Services. Optional when "
            "oauth_session_id is provided."
        )
    )
    oauth_session_id: Optional[str] = Field(
        None,
        max_length=64,
        description="Optional server-side OAuth session identifier."
    )
    refresh_token: Optional[str] = Field(
        None,
        description="Optional OAuth refresh token for server-side token refresh."
    )
    client_id: Optional[str] = Field(
        None,
        description="OAuth client_id used with refresh_token flow."
    )
    client_secret: Optional[str] = Field(
        None,
        description="OAuth client_secret used with refresh_token flow."
    )
    token_uri: str = Field(
        "https://oauth2.googleapis.com/token",
        description="OAuth token endpoint used for refresh operations."
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

    @field_validator("oauth_token")
    @classmethod
    def validate_oauth_token(cls, value: Optional[str]) -> Optional[str]:
        """Reject obviously invalid token payloads early."""
        if value is None:
            return value
        token = value.strip()
        if not token:
            raise ValueError("oauth_token cannot be empty.")
        if any(ch.isspace() for ch in token):
            raise ValueError("oauth_token cannot contain whitespace.")
        return token

    @field_validator("oauth_session_id")
    @classmethod
    def validate_oauth_session_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("oauth_session_id cannot be empty.")
        if any(ch.isspace() for ch in normalized):
            raise ValueError("oauth_session_id cannot contain whitespace.")
        return normalized

    @field_validator("refresh_token", "client_id", "client_secret", "token_uri")
    @classmethod
    def validate_optional_auth_fields(cls, value: Optional[str]) -> Optional[str]:
        """Normalize optional auth fields and reject whitespace-only values."""
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("OAuth field cannot be empty when provided.")
        if any(ch.isspace() for ch in normalized):
            raise ValueError("OAuth field cannot contain whitespace.")
        return normalized

    @model_validator(mode="after")
    def validate_refresh_flow_dependencies(self):
        """Require client credentials when refresh token is provided."""
        if not self.oauth_token and not self.oauth_session_id:
            raise ValueError(
                "Either oauth_token or oauth_session_id must be provided."
            )
        if self.refresh_token and (not self.client_id or not self.client_secret):
            raise ValueError(
                "client_id and client_secret are required when refresh_token is provided."
            )
        return self


class OAuthSessionCreateInput(BaseModel):
    """Input for creating a persisted server-side OAuth session."""
    oauth_token: str = Field(
        ...,
        description="OAuth access token to persist server-side."
    )
    refresh_token: Optional[str] = Field(
        None,
        description="Optional OAuth refresh token."
    )
    client_id: Optional[str] = Field(
        None,
        description="OAuth client_id used with refresh_token flow."
    )
    client_secret: Optional[str] = Field(
        None,
        description="OAuth client_secret used with refresh_token flow."
    )
    token_uri: str = Field(
        "https://oauth2.googleapis.com/token",
        description="OAuth token endpoint used for refresh operations."
    )
    label: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional human-readable label for this session."
    )

    @field_validator("oauth_token")
    @classmethod
    def validate_oauth_token(cls, value: str) -> str:
        token = value.strip()
        if not token:
            raise ValueError("oauth_token cannot be empty.")
        if any(ch.isspace() for ch in token):
            raise ValueError("oauth_token cannot contain whitespace.")
        return token

    @field_validator("refresh_token", "client_id", "client_secret", "token_uri")
    @classmethod
    def validate_optional_auth_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("OAuth field cannot be empty when provided.")
        if any(ch.isspace() for ch in normalized):
            raise ValueError("OAuth field cannot contain whitespace.")
        return normalized

    @model_validator(mode="after")
    def validate_refresh_flow_dependencies(self):
        if self.refresh_token and (not self.client_id or not self.client_secret):
            raise ValueError(
                "client_id and client_secret are required when refresh_token is provided."
            )
        return self


class OAuthSessionCreateOutput(BaseModel):
    """Output for session creation endpoint."""
    session_id: str
    created_at: str
    label: Optional[str] = None


class OAuthSessionDeleteOutput(BaseModel):
    """Output for session deletion endpoint."""
    session_id: str
    deleted: bool


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
    oauth_status: Optional[str] = Field(
        None,
        description="OAuth lifecycle status (ACCESS_TOKEN_ONLY, REFRESH_SUCCESS, REFRESH_FAILED)."
    )
    token_refreshed: Optional[bool] = Field(
        None,
        description="True when access token was refreshed server-side."
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
