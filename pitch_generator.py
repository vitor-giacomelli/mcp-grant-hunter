import os
import logging
from google import genai
from pydantic_models import PitchGenerateInput, PitchGenerateOutput

# Configure logging
logger = logging.getLogger(__name__)


class PitchGenerator:
    """Generate personalized funding pitches using Gemini API"""

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = 'gemini-2.0-flash'

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("GEMINI_API_KEY not found - will use template pitch")

    def generate_pitch(
        self,
        input_data: PitchGenerateInput
    ) -> PitchGenerateOutput:
        """Generate a personalized funding pitch"""
        try:
            if not self.client:
                logger.info(
                    "Gemini client not initialized, using template pitch"
                )
                return self._generate_template_pitch(
                    input_data,
                    "Template (No API Key)"
                )

            # Triple-Horizon Prompt
            prompt = self._create_triple_horizon_prompt(input_data)

            # Try Primary Model
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                pitch_text = response.text
                return PitchGenerateOutput(
                    pitch_draft=pitch_text,
                    model_used=self.model_name,
                    status="SUCCESS"
                )
            except Exception as e:
                logger.warning(f"Failed with {self.model_name}: {str(e)}")

                # Fallback to gemini-2.0-flash-lite
                fallback_model = "gemini-2.0-flash-lite"
                logger.info(f"Attempting fallback to {fallback_model}")
                try:
                    response = self.client.models.generate_content(
                        model=fallback_model,
                        contents=prompt
                    )
                    pitch_text = response.text
                    return PitchGenerateOutput(
                        pitch_draft=pitch_text,
                        model_used=fallback_model,
                        status="SUCCESS"
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback failed: {str(fallback_error)}")
                    raise fallback_error

        except Exception as e:
            logger.error(f"Error generating pitch with Gemini: {str(e)}")
            logger.info("Falling back to template pitch")
            return self._generate_template_pitch(
                input_data,
                "Template (Fallback)"
            )

    def _create_triple_horizon_prompt(
        self,
        input_data: PitchGenerateInput
    ) -> str:
        """Create the Triple-Horizon Framework prompt"""
        return f"""
        You are an expert grant writer. Generate a compelling 150-word pitch \
for the following startup and grant opportunity.

        STARTUP: {input_data.startup_name}
        FOCUS AREA: {input_data.focus_area}
        GRANT: {input_data.grant_title}

        Your pitch MUST adhere to the Triple-Horizon Framework:
        1. Acute Pain Point: Clearly state the urgent problem the startup \
solves.
        2. Technical Deviation: Explain the unique, innovative technical \
approach that sets them apart.
        3. Geopolitical/Macro-Economic Lock: Connect the solution to broader \
national or global strategic priorities (e.g., supply chain resilience, \
climate goals).

        Keep it concise, professional, and persuasive.
        """

    def _generate_template_pitch(
        self,
        input_data: PitchGenerateInput,
        model_used: str
    ) -> PitchGenerateOutput:
        """Generate a template pitch when LLM is not available"""
        pitch = f"""
        To the Grant Review Committee,

        I am writing to propose {input_data.startup_name} for the \
{input_data.grant_title}. We are focused on {input_data.focus_area}, \
addressing critical challenges in this sector.

        Our innovative approach offers a unique solution that aligns with \
the objectives of this funding opportunity. By leveraging our technical \
expertise, we aim to deliver significant impact and drive advancement \
in our field.

        This grant would be instrumental in accelerating our development \
and bringing our solution to market. We are committed to executing on \
our vision and contributing to the broader goals of the program.

        Thank you for your consideration.
        """
        return PitchGenerateOutput(
            pitch_draft=pitch.strip(),
            model_used=model_used,
            status="FALLBACK"
        )
