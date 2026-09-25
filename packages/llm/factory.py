"""
LLM / AI Provider Factory for ApplyForge
"""
from packages.llm.base import LLMProvider
from packages.llm.mock_provider import MockLLMProvider
from packages.ai.openai_provider import OpenAIProvider
from packages.shared.config import settings

def get_llm_provider() -> LLMProvider:
    provider_name = settings.LLM_PROVIDER.lower()
    if provider_name == "openai" or (provider_name != "mock" and settings.OPENAI_API_KEY):
        return OpenAIProvider()
    return MockLLMProvider()
