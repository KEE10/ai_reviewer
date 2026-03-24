from shared.database import session_maker
from .service import handle_pr_viewed as service_handle_pr_viewed

async def handle_pr_viewed(payload: dict) -> None:
    async with session_maker() as session:
        await service_handle_pr_viewed(session, payload)