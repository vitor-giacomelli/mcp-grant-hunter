from pitch_generator import PitchGenerator
from pydantic_models import PitchGenerateInput


def build_input() -> PitchGenerateInput:
    return PitchGenerateInput(
        startup_name="Acme Climate",
        focus_area="Clean Energy",
        grant_title="DOE Innovation Grant",
    )


def test_generate_pitch_uses_template_when_no_client(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    generator = PitchGenerator()

    result = generator.generate_pitch(build_input())

    assert result.status == "FALLBACK"
    assert "Acme Climate" in result.pitch_draft


def test_generate_pitch_falls_back_when_models_fail(monkeypatch):
    generator = PitchGenerator()

    class FailingModels:
        def generate_content(self, model, contents):
            raise RuntimeError(f"{model} unavailable")

    class FailingClient:
        models = FailingModels()

    generator.client = FailingClient()

    result = generator.generate_pitch(build_input())

    assert result.status == "FALLBACK"
    assert result.model_used == "Template (Fallback)"


def test_prompt_contains_triple_horizon_sections():
    generator = PitchGenerator()
    prompt = generator._create_triple_horizon_prompt(build_input())

    assert "Acute Pain Point" in prompt
    assert "Technical Deviation" in prompt
    assert "Geopolitical/Macro-Economic Lock" in prompt
