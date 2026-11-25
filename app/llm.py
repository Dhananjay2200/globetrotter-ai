"""
LLM Provider and Factory Configuration.
Modular abstraction for NVIDIA NIM and other OpenAI-compatible endpoints using LangChain.
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from app.config import get_settings
from app.utils.logging import logger


def get_chat_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    timeout: Optional[int] = None,
) -> ChatOpenAI:
    """
    Factory function to instantiate the configured Chat LLM.
    Defaults to NVIDIA NIM via OpenAI-compatible API specifications.
    
    Can easily be swapped or redirected to local models (e.g., vLLM / Ollama)
    simply by updating the NVIDIA_BASE_URL and NVIDIA_MODEL_NAME settings.
    """
    settings = get_settings()

    selected_model = model_name or settings.NVIDIA_MODEL_NAME
    selected_temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
    selected_tokens = max_tokens or settings.LLM_MAX_TOKENS
    selected_timeout = timeout or settings.LLM_TIMEOUT

    logger.debug(
        f"Initializing ChatOpenAI instance: model={selected_model}, "
        f"base_url={settings.NVIDIA_BASE_URL}, temp={selected_temp}"
    )

    return ChatOpenAI(
        model=selected_model,
        api_key=settings.NVIDIA_API_KEY,
        base_url=settings.NVIDIA_BASE_URL,
        temperature=selected_temp,
        max_tokens=selected_tokens,
        timeout=selected_timeout,
        max_retries=2,
    )


async def check_llm_connection() -> dict:
    """
    Tests connectivity to the NVIDIA NIM endpoint by sending a minimal prompt.
    Returns status, latency in milliseconds, and the sample response.
    """
    import time

    settings = get_settings()

    if not settings.NVIDIA_API_KEY or settings.NVIDIA_API_KEY.startswith("nvapi-placeholder"):
        return {
            "status": "warning",
            "message": "NVIDIA_API_KEY is not configured or using default placeholder. Please set your key in .env file.",
            "configured_model": settings.NVIDIA_MODEL_NAME,
            "base_url": settings.NVIDIA_BASE_URL,
        }

    try:
        llm = get_chat_llm(max_tokens=32, temperature=0.1)
        start_time = time.perf_counter()
        
        # Simple test query
        response = await llm.ainvoke("Respond with exactly: 'GlobeTrotter AI LLM connection successful.'")
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "status": "connected",
            "model": settings.NVIDIA_MODEL_NAME,
            "base_url": settings.NVIDIA_BASE_URL,
            "latency_ms": latency_ms,
            "response_preview": response.content.strip()
        }
    except Exception as exc:
        logger.error(f"Failed to connect to NVIDIA NIM: {exc}")
        return {
            "status": "error",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "configured_model": settings.NVIDIA_MODEL_NAME,
            "base_url": settings.NVIDIA_BASE_URL,
        }
