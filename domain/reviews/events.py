from shared.database import session_maker
from .service import handle_pr_created as service_handle_pr_created

async def handle_pr_created(payload: dict) -> None:
    async with session_maker() as session:
        await service_handle_pr_created(session, payload)