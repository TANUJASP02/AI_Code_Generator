from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


OLLAMA_URL = "https://browsing-change-broaden.ngrok-free.dev"
MODEL_NAME = "gpt-oss:20b"


model = OpenAIChatModel(
    MODEL_NAME,
    provider=OpenAIProvider(
        base_url=f"{OLLAMA_URL}/v1",
        api_key="ollama"
    )
)