"""Ollama client for local AI inference."""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any

from opensati.config.settings import get_settings


@dataclass
class OllamaClient:
    """
    Client for local Ollama inference.

    All AI processing happens locally - no cloud calls.
    """

    model: str = ""
    vision_model: str = ""
    timeout: int = 10

    # Internal state
    _available: bool | None = None

    def __post_init__(self) -> None:
        """Initialize with settings if not provided."""
        settings = get_settings()
        if not self.model:
            self.model = settings.ai.model
        if not self.vision_model:
            self.vision_model = settings.ai.vision_model
        if self.timeout == 10:
            self.timeout = settings.ai.timeout

    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        if self._available is not None:
            return self._available

        try:
            import ollama

            # Try to list models
            models = ollama.list()
            available_models = [m["name"] for m in models.get("models", [])]

            # Check if our models are available
            has_text = any(self.model in m for m in available_models)
            has_vision = any(self.vision_model in m for m in available_models)

            self._available = has_text or has_vision

            if not self._available:
                print(f"⚠️ Models not found. Run: ollama pull {self.model}")

            return self._available

        except ImportError:
            print("⚠️ Ollama package not installed")
            self._available = False
            return False
        except Exception as e:
            print(f"⚠️ Could not connect to Ollama: {e}")
            self._available = False
            return False

    def chat(self, prompt: str, system: str | None = None) -> str | None:
        """
        Send a text prompt to the local LLM.

        Returns response text or None on failure.
        """
        if not self.is_available():
            return None

        try:
            import ollama

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={"timeout": self.timeout},
            )

            return response["message"]["content"]

        except Exception as e:
            print(f"⚠️ Ollama chat failed: {e}")
            return None

    def analyze_image(
        self, image_bytes: bytes, prompt: str, system: str | None = None
    ) -> str | None:
        """
        Analyze an image with the vision model.

        Returns response text or None on failure.
        """
        if not self.is_available():
            return None

        try:
            import ollama

            # Encode image as base64
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append(
                {"role": "user", "content": prompt, "images": [image_b64]}
            )

            response = ollama.chat(
                model=self.vision_model,
                messages=messages,
                options={"timeout": self.timeout * 2},  # Vision takes longer
            )

            return response["message"]["content"]

        except Exception as e:
            print(f"⚠️ Ollama vision failed: {e}")
            return None

    def check_intent_match(
        self, intent: str, image_bytes: bytes
    ) -> tuple[bool, str]:
        """
        Check if screen content matches user's stated intent.

        Returns (matches, explanation).
        """
        prompt = f"""The user said they are working on: "{intent}"

Look at this screenshot. Is the content related to their stated work?

Answer with:
1. YES or NO
2. Brief explanation (one sentence)

Format: YES/NO: explanation"""

        system = """You are a focus assistant. Be lenient - if the content could 
reasonably be related to work (research, documentation, tutorials), say YES.
Only say NO for obvious distractions like social media, games, or unrelated videos."""

        response = self.analyze_image(image_bytes, prompt, system)

        if not response:
            return (True, "Could not analyze")  # Fail open

        response = response.strip().upper()
        matches = response.startswith("YES")
        explanation = response.split(":", 1)[-1].strip() if ":" in response else response

        return (matches, explanation)

    def analyze_sentiment(self, text: str) -> tuple[str, str | None]:
        """
        Analyze sentiment of text and suggest reframe if aggressive.

        Returns (sentiment, suggested_reframe).
        Sentiment: "neutral", "positive", "negative", "aggressive"
        """
        prompt = f"""Analyze this text for emotional tone:

"{text}"

If the tone is aggressive, passive-aggressive, or could damage relationships,
provide a more constructive alternative using Non-Violent Communication principles.

Format:
SENTIMENT: [neutral/positive/negative/aggressive]
REFRAME: [suggested alternative or "none"]"""

        response = self.chat(prompt)

        if not response:
            return ("neutral", None)

        lines = response.strip().split("\n")
        sentiment = "neutral"
        reframe = None

        for line in lines:
            if line.startswith("SENTIMENT:"):
                sentiment = line.split(":", 1)[-1].strip().lower()
            elif line.startswith("REFRAME:"):
                reframe_text = line.split(":", 1)[-1].strip()
                if reframe_text.lower() != "none":
                    reframe = reframe_text

        return (sentiment, reframe)
