from app.core.config import settings
from app.core.exceptions import EmbeddingError


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using OpenAI, Anthropic, or Google Gemini."""
    if settings.LLM_PROVIDER == "gemini" and settings.GOOGLE_API_KEY:
        return await _gemini_embed(texts)
    if settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        return await _anthropic_embed(texts)
    if settings.OPENAI_API_KEY:
        return await _openai_embed(texts)
    raise EmbeddingError(
        "No embedding backend configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY in .env"
    )


async def embed_query(text: str) -> list[float]:
    results = await embed_texts([text])
    return results[0]


async def _openai_embed(texts: list[str]) -> list[list[float]]:
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        raise EmbeddingError(f"OpenAI embedding error: {e}") from e


async def _anthropic_embed(texts: list[str]) -> list[list[float]]:
    """Use Anthropic's API for embeddings (via third-party)."""
    try:
        from openai import AsyncOpenAI
        # Use Anthropic's compatibility layer
        client = AsyncOpenAI(
            api_key=settings.ANTHROPIC_API_KEY,
            base_url="https://api.anthropic.com/openai/",
        )
        response = await client.embeddings.create(
            model="claude-3-5-sonnet-20241022",
            input=texts,
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        raise EmbeddingError(f"Anthropic embedding error: {e}") from e


async def _gemini_embed(texts: list[str]) -> list[list[float]]:
    """Use Google Gemini API for embeddings."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        embeddings = []
        for text in texts:
            result = await genai.embed_content_async(
                model=settings.EMBEDDING_MODEL,
                content=text,
            )
            embeddings.append(result["embedding"])
        return embeddings
    except Exception as e:
        raise EmbeddingError(f"Gemini embedding error: {e}") from e
