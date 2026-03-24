import httpx
from anthropic import AsyncAnthropic

from config import settings

httpx_client: httpx.AsyncClient | None = None
claude_client: AsyncAnthropic | None = None

async def init_clients():
    global httpx_client, claude_client
    httpx_client = httpx.AsyncClient()
    claude_client = AsyncAnthropic(api_key=settings.claude_api_key)

async def close_clients():
    global httpx_client, claude_client
    if httpx_client:
        await httpx_client.aclose()
    if claude_client:
        await claude_client.close()