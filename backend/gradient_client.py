"""
DigitalOcean Gradient AI client wrapper.
Uses the OpenAI-compatible API endpoint provided by Gradient.
"""
import os
from openai import AsyncOpenAI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gradient_api_key: str = ""
    gradient_base_url: str = "https://inference.do-ai.run/v1"
    gradient_model: str = "claude-sonnet-4-6"  # Available on DO Gradient as of Feb 2026

    # Optional: pre-created Gradient agent/KB IDs
    gradient_agent_id: str = ""
    gradient_knowledge_base_id: str = ""


settings = Settings()


def get_gradient_client() -> AsyncOpenAI:
    """Return an AsyncOpenAI client pointed at DigitalOcean Gradient inference."""
    return AsyncOpenAI(
        api_key=settings.gradient_api_key,
        base_url=settings.gradient_base_url,
    )
