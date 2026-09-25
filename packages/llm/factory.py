"""
LLM / AI Provider Factory for ApplyForge
"""
from packages.llm.base import LLMProvider
from packages.llm.mock_provider import MockLLMProvider
from packages.ai.openai_provider import OpenAIProvider
from packages.shared.config import settings

def get_llm_provider() -> LLMProvider:
    provider_name = getattr(settings, "LLM_PROVIDER", "mock").lower()
    openai_key = getattr(settings, "OPENAI_API_KEY", "")
    if provider_name == "openai" and openai_key:
        return OpenAIProvider()
    return MockLLMProvider()
