from dataclasses import dataclass

import structlog

from ..config import settings
from ..metrics import MODEL_REQUESTS


logger = structlog.get_logger(__name__)


SYSTEM_PROMPT = """You are Gita GPT, a calm reflective guide grounded only in the supplied passages.
Answer the seeker's actual question. Distinguish the text from your practical interpretation.
Use source labels such as [Source 1] when grounding a claim. Never invent verse numbers.
Do not present yourself as medical, legal, financial, or crisis support. If the context is
insufficient, say so plainly. Structure the answer as: Reflection, Gita perspective, Practice."""


@dataclass(frozen=True)
class GenerationResult:
    text: str
    provider: str


class GeminiProvider:
    name = "gemini"

    def __init__(self):
        from google import genai

        self.client = genai.Client(api_key=settings.google_api_key)

    def generate(self, prompt: str) -> str:
        from google.genai import types

        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.25,
                max_output_tokens=1100,
            ),
        )
        return (response.text or "").strip()


class GroqProvider:
    name = "groq"

    def __init__(self):
        from groq import Groq

        self.client = Groq(
            api_key=settings.groq_api_key,
            timeout=settings.model_timeout_seconds,
            max_retries=1,
        )

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=settings.groq_model,
            temperature=0.25,
            max_tokens=1100,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return (response.choices[0].message.content or "").strip()


class LocalProvider:
    name = "local"

    def generate(self, prompt: str) -> str:
        context = prompt.split("CONTEXT:\n", 1)[-1].split("\n\nQUESTION:", 1)[0].strip()
        excerpt = context[:1400].strip()
        return (
            "### Reflection\n"
            "Your question points to the tension between what you can guide and what you cannot control. "
            "A useful first step is to name the next right action without demanding certainty about its result.\n\n"
            "### Gita perspective\n"
            f"The retrieved passages emphasize disciplined action and steadiness: {excerpt} [Source 1]\n\n"
            "### Practice\n"
            "Write down one duty that is yours today, one outcome that is not yours to command, and one small "
            "action you can complete with full attention. Revisit the distinction before making the next decision."
        )


class ProviderChain:
    def __init__(self):
        providers = []
        if settings.google_api_key:
            try:
                providers.append(GeminiProvider())
            except Exception:
                logger.exception("gemini_provider_initialization_failed")
        if settings.groq_api_key:
            try:
                providers.append(GroqProvider())
            except Exception:
                logger.exception("groq_provider_initialization_failed")
        providers.append(LocalProvider())
        self.providers = providers

    @property
    def names(self) -> list[str]:
        return [provider.name for provider in self.providers]

    def generate(self, prompt: str) -> GenerationResult:
        for provider in self.providers:
            try:
                text = provider.generate(prompt)
                if not text:
                    raise ValueError("provider returned an empty response")
                MODEL_REQUESTS.labels(provider.name, "success").inc()
                return GenerationResult(text=text, provider=provider.name)
            except Exception as exc:
                MODEL_REQUESTS.labels(provider.name, "failure").inc()
                logger.warning("model_provider_failed", provider=provider.name, error=type(exc).__name__)
        raise RuntimeError("No answer provider is available")


def build_grounded_prompt(question: str, intention: str, sources: list[dict]) -> str:
    blocks = []
    for index, source in enumerate(sources, start=1):
        page = f", page {source['page_number']}" if source.get("page_number") else ""
        blocks.append(f"[Source {index}] {source['title']}{page}\n{source['excerpt']}")
    context = "\n\n".join(blocks)
    return (
        f"SEEKER INTENTION: {intention or 'Not specified'}\n\n"
        f"CONTEXT:\n{context}\n\nQUESTION:\n{question}\n\n"
        "Answer using only the context above and cite the source labels."
    )
