import os
import time
import logging
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI, HTTPException

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
    GoogleServicesInput
)

# Import Modules
from grants_gov_api import GrantsGovAPI
from pitch_generator import PitchGenerator
from google_services_manager import GoogleServicesManager

app = FastAPI(title="Grant Hunter MCP")

# Instantiate Services
grants_api = GrantsGovAPI()
pitch_generator = PitchGenerator()
google_services_manager = GoogleServicesManager()


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy"}


@app.post("/query_grants", response_model=GrantsQueryOutput)
async def query_grants(input_data: GrantsQueryInput):
    """
    Query Grants.gov for opportunities.
    """
    start_time = time.time()

    try:
        # Use the keyword from input
        results = grants_api.search_grants(
            input_data.keyword, limit=input_data.max_results
        )

        # Map to GrantOpportunity model
        grant_opportunities = []
        for r in results:
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

        return GrantsQueryOutput(
            results=grant_opportunities,
            total_count=len(grant_opportunities),
            execution_time_ms=execution_time
        )

    except Exception as e:
        logger.error(f"Critical error in query_grants: {str(e)}")
        # Graceful degradation
        execution_time = (time.time() - start_time) * 1000

        # Return mock data with INCOMPLETE status if everything fails
        mock_results = []
        for m in GrantsGovAPI.MOCK_GRANTS:
            mock_results.append(
                GrantOpportunity(
                    id=m.get('opportunity_number', 'UNKNOWN'),
                    title=m.get('title', 'Unknown'),
                    agency=m.get('agency', 'Unknown'),
                    close_date=m.get('close_date', 'Unknown'),
                    status="Open",
                    data_status="INCOMPLETE_SYNOPSIS_ONLY"
                )
            )

        return GrantsQueryOutput(
            results=mock_results[:input_data.max_results],
            total_count=len(mock_results),
            execution_time_ms=execution_time
        )


@app.post("/generate_pitch", response_model=PitchGenerateOutput)
async def generate_pitch(input_data: PitchGenerateInput):
    """
    Generate a funding pitch using Gemini or fallback template.
    """
    return pitch_generator.generate_pitch(input_data)


@app.post("/manage_google_services")
async def manage_google_services(input_data: GoogleServicesInput):
    """
    Manage Google Services: Create Gmail draft and Calendar event.
    """
    return google_services_manager.execute_services(input_data)
