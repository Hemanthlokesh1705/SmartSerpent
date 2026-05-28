from datetime import datetime, timezone
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.llm.base_model import SnakeResponse
from src.llm.system_prompt import SYSTEM_PROMPT


load_dotenv()


class GeminiModel:
    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        api_key = os.getenv("GOOGLE_API_KEY")
        gemini_enabled = os.getenv("SMARTSERPENT_ENABLE_GEMINI", "false").lower() == "true"
        if not api_key or not gemini_enabled:
            return

        llm = ChatGoogleGenerativeAI(model=self.model_name, google_api_key=api_key)
        self.model = llm.with_structured_output(SnakeResponse)

    def _fallback_response(self, snake_name: str) -> SnakeResponse:
        now = datetime.now(timezone.utc).isoformat()
        normalized = snake_name.strip().title()
        venomous = "yes" if "cobra" in normalized.lower() or "viper" in normalized.lower() else "unknown"
        emergency = "immediate hospital" if venomous == "yes" else "urgent hospital"

        return SnakeResponse(
            input_label=snake_name,
            canonical_name=normalized,
            scientific_name="Unknown",
            habitat="Please verify habitat with a trusted field guide or wildlife database.",
            venomous=venomous,
            venom_type="unknown" if venomous == "yes" else None,
            first_aid=[
                "Move away from the snake and avoid handling it.",
                "Keep the bitten person calm and limit movement.",
                "Remove rings or tight items near swelling.",
                "Seek professional medical help immediately.",
            ],
            emergency_priority=emergency,
            safety_info=[
                "Do not attempt to catch or kill the snake.",
                "Use a flashlight and boots in snake-prone areas.",
                "Keep distance and contact local wildlife rescue if needed.",
            ],
            confidence_note="Generated from fallback guidance because Gemini output was unavailable.",
            verify_sources=[
                "Local poison control or emergency services",
                "Regional forest or wildlife department",
                "Hospital toxicology guidance",
            ],
            timestamp=now,
        )

    def generate_output(self, snake_name: str) -> SnakeResponse:
        cleaned_name = snake_name.strip()
        if not cleaned_name:
            raise ValueError("Please pass a valid snake name.")

        if self.model is None:
            return self._fallback_response(cleaned_name)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=cleaned_name),
        ]

        try:
            return self.model.invoke(messages)
        except Exception:
            return self._fallback_response(cleaned_name)
