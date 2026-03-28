import os
import time
import asyncio
import logging
import uuid
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# Load environment variables from the script's directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if os.path.exists(env_path):
    logger.info(f"Loading .env from: {env_path}")
else:
    logger.warning(f".env file NOT found at: {env_path}")

if os.getenv('GEMINI_API_KEY'):
    logger.info("GEMINI_API_KEY found in environment.")
else:
    logger.error("GEMINI_API_KEY NOT found in environment.")

# Import Models
from pydantic_models import (
    GrantsQueryInput,
    GrantsQueryOutput,
    GrantOpportunity,
    PitchGenerateInput,
    PitchGenerateOutput,
    GoogleServicesInput,
    GoogleServicesOutput,
    OAuthSessionCreateInput,
    OAuthSessionCreateOutput,
    OAuthSessionDeleteOutput,
    ErrorEnvelope,
)

# Import Modules
from grants_gov_api import GrantsGovAPI
from pitch_generator import PitchGenerator
from google_services_manager import GoogleServicesManager
from oauth_session_store import OAuthSessionStore

app = FastAPI(title="Grant Hunter MCP")

# Instantiate Services
grants_api = GrantsGovAPI()
pitch_generator = PitchGenerator()
google_services_manager = GoogleServicesManager()
oauth_session_store = OAuthSessionStore(
    os.getenv("OAUTH_SESSION_DB_PATH")
)


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Attach and return a request correlation id for traceability."""
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id
    start = time.perf_counter()

    response: Response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["x-request-id"] = request_id

    logger.info(
        "request_completed request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy"}


def error_response(
    code: str,
    message: str,
    status_code: int,
    details: dict | None = None
) -> JSONResponse:
    """Build a standardized machine-readable error payload."""
    payload = ErrorEnvelope(
        code=code,
        message=message,
        details=details
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(exclude_none=True)
    )


def _matches_focus_area(grant: dict, focus_area: str | None) -> bool:
    """Apply optional focus-area filtering over title/description/category."""
    if not focus_area:
        return True

    focus = focus_area.lower().strip()
    haystack = " ".join(
        [
            str(grant.get("title", "")),
            str(grant.get("description", "")),
            str(grant.get("category", "")),
            str(grant.get("agency", "")),
        ]
    ).lower()
    return focus in haystack


def _resolve_google_services_input(
    input_data: GoogleServicesInput
) -> GoogleServicesInput:
    """Resolve session-backed credentials when oauth_session_id is provided."""
    if not input_data.oauth_session_id or input_data.oauth_token:
        return input_data

    session = oauth_session_store.get_session(input_data.oauth_session_id)
    if not session:
        raise LookupError(
            f"OAuth session not found: {input_data.oauth_session_id}"
        )

    return GoogleServicesInput(
        grant_title=input_data.grant_title,
        deadline_date=input_data.deadline_date,
        oauth_session_id=input_data.oauth_session_id,
        oauth_token=session["oauth_token"],
        refresh_token=session.get("refresh_token"),
        client_id=session.get("client_id"),
        client_secret=session.get("client_secret"),
        token_uri=session.get("token_uri")
        or "https://oauth2.googleapis.com/token",
    )


@app.post(
    "/oauth_sessions",
    response_model=OAuthSessionCreateOutput,
    responses={
        400: {"model": ErrorEnvelope, "description": "Invalid input."},
        502: {"model": ErrorEnvelope, "description": "Session storage failure."},
    },
)
async def create_oauth_session(input_data: OAuthSessionCreateInput):
    """Create a persisted server-side OAuth session."""
    try:
        created = await asyncio.to_thread(
            oauth_session_store.create_session,
            input_data.oauth_token,
            input_data.refresh_token,
            input_data.client_id,
            input_data.client_secret,
            input_data.token_uri,
            input_data.label,
        )
        return OAuthSessionCreateOutput(**created)
    except ValueError as e:
        return error_response(
            code="OAUTH_SESSION_INPUT_ERROR",
            message="Invalid OAuth session input.",
            status_code=400,
            details={"error": str(e)},
        )
    except Exception as e:
        logger.error("Failed creating oauth session: %s", str(e))
        return error_response(
            code="OAUTH_SESSION_CREATE_FAILURE",
            message="Failed to create OAuth session.",
            status_code=502,
            details={"error": str(e)},
        )


@app.delete(
    "/oauth_sessions/{session_id}",
    response_model=OAuthSessionDeleteOutput,
    responses={
        400: {"model": ErrorEnvelope, "description": "Invalid input."},
        404: {"model": ErrorEnvelope, "description": "Session not found."},
        502: {"model": ErrorEnvelope, "description": "Session storage failure."},
    },
)
async def delete_oauth_session(session_id: str):
    """Delete a persisted server-side OAuth session."""
    if not session_id.strip():
        return error_response(
            code="OAUTH_SESSION_INPUT_ERROR",
            message="session_id cannot be empty.",
            status_code=400,
        )

    try:
        deleted = await asyncio.to_thread(
            oauth_session_store.delete_session,
            session_id,
        )
        if not deleted:
            return error_response(
                code="OAUTH_SESSION_NOT_FOUND",
                message="OAuth session not found.",
                status_code=404,
                details={"session_id": session_id},
            )
        return OAuthSessionDeleteOutput(session_id=session_id, deleted=True)
    except Exception as e:
        logger.error("Failed deleting oauth session: %s", str(e))
        return error_response(
            code="OAUTH_SESSION_DELETE_FAILURE",
            message="Failed to delete OAuth session.",
            status_code=502,
            details={"error": str(e)},
        )


@app.post(
    "/query_grants",
    response_model=GrantsQueryOutput,
    responses={
        502: {
            "model": ErrorEnvelope,
            "description": "Upstream query and fallback failure."
        }
    }
)
async def query_grants(input_data: GrantsQueryInput):
    """
    Query Grants.gov for opportunities.
    """
    start_time = time.time()

    try:
        raw_results = await grants_api.search_grants(
            input_data.keyword, limit=input_data.max_results
        )
    except Exception as e:
        logger.error("query_grants upstream failure: %s", str(e))
        return error_response(
            code="QUERY_GRANTS_UPSTREAM_FAILURE",
            message="Failed to query grants upstream service.",
            status_code=502,
            details={"error": str(e)},
        )

    # Filter by focus area when provided.
    filtered_results = [
        r for r in raw_results
        if _matches_focus_area(r, input_data.focus_area)
    ]

    try:
        # Detect fallback-like source by known mock IDs.
        mock_ids = {
            g.get("opportunity_number", "")
            for g in GrantsGovAPI.MOCK_GRANTS
        }

        # Map to GrantOpportunity model
        grant_opportunities = []
        for r in filtered_results:
            grant_opportunities.append(
                GrantOpportunity(
                    id=r.get('opportunity_number', 'UNKNOWN'),
                    title=r.get('title', 'Unknown'),
                    agency=r.get('agency', 'Unknown'),
                    close_date=r.get('close_date', 'Unknown'),
                    status="Open",
                    data_status="COMPLETE"
                )
            )

        execution_time = (time.time() - start_time) * 1000
        result_ids = {g.id for g in grant_opportunities}
        fallback_used = bool(result_ids) and result_ids.issubset(mock_ids)

        return GrantsQueryOutput(
            results=grant_opportunities,
            total_count=len(grant_opportunities),
            execution_time_ms=execution_time,
            fallback_used=fallback_used,
            data_source="mock_fallback" if fallback_used else "grants_gov"
        )

    except Exception as e:
        logger.error("query_grants mapping failure: %s", str(e))
        return error_response(
            code="QUERY_GRANTS_MAPPING_FAILURE",
            message="Failed to map grants response.",
            status_code=502,
            details={"error": str(e)},
        )


@app.post(
    "/generate_pitch",
    response_model=PitchGenerateOutput,
    responses={
        400: {"model": ErrorEnvelope, "description": "Invalid input."},
        502: {
            "model": ErrorEnvelope,
            "description": "Pitch generation service failure."
        }
    }
)
async def generate_pitch(input_data: PitchGenerateInput):
    """
    Generate a funding pitch using Gemini or fallback template.
    """
    try:
        return pitch_generator.generate_pitch(input_data)
    except ValueError as e:
        return error_response(
            code="PITCH_INPUT_ERROR",
            message="Invalid pitch generation input.",
            status_code=400,
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(f"Unhandled error in generate_pitch: {e}")
        return error_response(
            code="PITCH_GENERATION_FAILURE",
            message="Failed to generate pitch.",
            status_code=502,
            details={"error": str(e)}
        )


@app.post(
    "/manage_google_services",
    response_model=GoogleServicesOutput,
    responses={
        400: {"model": ErrorEnvelope, "description": "Invalid input."},
        404: {"model": ErrorEnvelope, "description": "OAuth session not found."},
        502: {
            "model": ErrorEnvelope,
            "description": "Google services execution failure."
        }
    }
)
async def manage_google_services(input_data: GoogleServicesInput):
    """
    Manage Google Services: Create Gmail draft and Calendar event.
    """
    try:
        resolved_input = _resolve_google_services_input(input_data)
        result = await asyncio.to_thread(
            google_services_manager.execute_services,
            resolved_input
        )

        resolved_token = result.get("resolved_oauth_token")
        if resolved_input.oauth_session_id and resolved_token:
            await asyncio.to_thread(
                oauth_session_store.update_access_token,
                resolved_input.oauth_session_id,
                resolved_token,
            )

        result.pop("resolved_oauth_token", None)
        if result.get("status") == "CRITICAL_FAILURE":
            return error_response(
                code="GOOGLE_SERVICES_CRITICAL_FAILURE",
                message="Google services execution failed critically.",
                status_code=502,
                details={"error": result.get("error")}
            )
        return GoogleServicesOutput(**result)
    except LookupError as e:
        return error_response(
            code="OAUTH_SESSION_NOT_FOUND",
            message="OAuth session not found.",
            status_code=404,
            details={"error": str(e)},
        )
    except ValueError as e:
        return error_response(
            code="GOOGLE_SERVICES_INPUT_ERROR",
            message="Invalid Google services input.",
            status_code=400,
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(f"Unhandled error in manage_google_services: {e}")
        return error_response(
            code="GOOGLE_SERVICES_FAILURE",
            message="Failed to execute Google services operation.",
            status_code=502,
            details={"error": str(e)}
        )
