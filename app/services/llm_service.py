from typing import AsyncIterator
from app.core.config import settings
from app.core.exceptions import LLMError

RAG_SYSTEM_PROMPT = """You are a helpful assistant. Answer the user's question using ONLY the context provided below.
If the context does not contain enough information to answer, say so clearly.
Do not make up information. Cite the source filename when relevant.

Context:
{context}"""


async def generate_answer(question: str, context: str) -> str:
    if settings.LLM_PROVIDER == "gemini" and settings.GOOGLE_API_KEY:
        return await _gemini_generate(question, context)
    if settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        return await _anthropic_generate(question, context)
    if settings.OPENAI_API_KEY:
        return await _openai_generate(question, context)
    raise LLMError("No LLM provider configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY in .env")


async def stream_answer(question: str, context: str) -> AsyncIterator[str]:
    if settings.LLM_PROVIDER == "gemini" and settings.GOOGLE_API_KEY:
        async for token in _gemini_stream(question, context):
            yield token
    elif settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        async for token in _anthropic_stream(question, context):
            yield token
    elif settings.OPENAI_API_KEY:
        async for token in _openai_stream(question, context):
            yield token
    else:
        raise LLMError("No LLM provider configured.")


# ── OpenAI ──────────────────────────────────────────────────────────────────

async def _openai_generate(question: str, context: str) -> str:
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": RAG_SYSTEM_PROMPT.format(context=context)},
                {"role": "user", "content": question},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        raise LLMError(f"OpenAI error: {e}") from e


async def _openai_stream(question: str, context: str) -> AsyncIterator[str]:
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        stream = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": RAG_SYSTEM_PROMPT.format(context=context)},
                {"role": "user", "content": question},
            ],
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        raise LLMError(f"OpenAI stream error: {e}") from e


# ── Anthropic ────────────────────────────────────────────────────────────────

async def _anthropic_generate(question: str, context: str) -> str:
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = await client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=1024,
            system=RAG_SYSTEM_PROMPT.format(context=context),
            messages=[{"role": "user", "content": question}],
        )
        return message.content[0].text
    except Exception as e:
        raise LLMError(f"Anthropic error: {e}") from e


async def _anthropic_stream(question: str, context: str) -> AsyncIterator[str]:
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        async with client.messages.stream(
            model=settings.LLM_MODEL,
            max_tokens=1024,
            system=RAG_SYSTEM_PROMPT.format(context=context),
            messages=[{"role": "user", "content": question}],
        ) as stream:
            async for text in stream.text_stream:
                yield text
    except Exception as e:
        raise LLMError(f"Anthropic stream error: {e}") from e


# ── Google Gemini ────────────────────────────────────────────────────────────

async def _gemini_generate(question: str, context: str) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel(settings.LLM_MODEL)
        prompt = RAG_SYSTEM_PROMPT.format(context=context) + "\n\nUser question: " + question
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        raise LLMError(f"Gemini error: {e}") from e


async def _gemini_stream(question: str, context: str) -> AsyncIterator[str]:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel(settings.LLM_MODEL)
        prompt = RAG_SYSTEM_PROMPT.format(context=context) + "\n\nUser question: " + question
        response = await model.generate_content_async(prompt, stream=True)
        async for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        raise LLMError(f"Gemini stream error: {e}") from e
