from openai import OpenAI
from typing import Optional
from app.config import settings

_client: OpenAI = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_BASE_URL,
        )
    return _client


def chat(
    system: str,
    user: str,
    max_tokens: int = None,
    temperature: float = 0.3,
) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content


def classify(prompt: str) -> str:
    return chat(
        system="你是一个医疗对话分类助手，只输出分类标签，不输出任何解释。",
        user=prompt,
        temperature=0,
    )
