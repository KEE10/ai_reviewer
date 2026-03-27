from shared.database import session_maker
from .service import handle_pr_reviewed as service_handle_pr_reviewed


async def handle_pr_reviewed(payload: dict) -> None:
    async with session_maker() as session:
        await service_handle_pr_reviewed(session, payload)
