"""Right Speech analyzer for detecting aggressive communication."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from opensati.ai.ollama_client import OllamaClient


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""

    sentiment: str = "neutral"  # neutral, positive, negative, aggressive
    original_text: str = ""
    suggested_reframe: str | None = None
    needs_reframe: bool = False


@dataclass
class SentimentAnalyzer:
    """
    Analyzes text sentiment and suggests constructive reframes.

    Privacy:
    - Text processed locally via Ollama
    - No content is stored or logged
    - Suggestions are ephemeral
    """

    # Configuration
    trigger_sentiments: list[str] | None = None

    # Callbacks
    on_aggressive_detected: Callable[[str, str], None] | None = None

    # Internal state
    _ollama: OllamaClient | None = None
    _enabled: bool = False

    def __post_init__(self) -> None:
        """Initialize components."""
        if self.trigger_sentiments is None:
            self.trigger_sentiments = ["aggressive", "negative"]

        self._ollama = OllamaClient()

    def start(self) -> bool:
        """Start sentiment analysis."""
        if not self._ollama.is_available():
            print("⚠️ Sentiment analyzer requires Ollama")
            return False

        self._enabled = True
        print("💬 Sentiment analyzer started")
        return True

    def stop(self) -> None:
        """Stop sentiment analysis."""
        self._enabled = False
        print("💬 Sentiment analyzer stopped")

    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze text and suggest reframe if needed.

        Returns SentimentResult with optional reframe suggestion.
        """
        if not self._enabled or not text.strip():
            return SentimentResult()

        # Skip very short text
        if len(text.split()) < 5:
            return SentimentResult(original_text=text)

        sentiment, reframe = self._ollama.analyze_sentiment(text)

        needs_reframe = sentiment in self.trigger_sentiments and reframe is not None

        if needs_reframe and self.on_aggressive_detected:
            self.on_aggressive_detected(text, reframe)

        return SentimentResult(
            sentiment=sentiment,
            original_text=text,
            suggested_reframe=reframe,
            needs_reframe=needs_reframe,
        )

    def get_quick_reframe(self, text: str) -> str | None:
        """
        Get a quick reframe suggestion without full analysis.

        Returns suggested text or None.
        """
        result = self.analyze(text)
        return result.suggested_reframe
