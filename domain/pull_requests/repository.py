from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc

from .models import PullRequestModel
from domain.reviews.models import ReviewModel


class PullRequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_pull_request(self, pull_request_id: str) -> PullRequestModel:
        pr = await self.session.execute(
            select(PullRequestModel).where(
                PullRequestModel.pull_request_id == pull_request_id
            )
        )
        return pr.scalar_one_or_none()

    async def insert_pull_request(self, pull_request_id: str):
        pr_unique_id = f"{webhook_payload.repository.full_name}#{webhook_payload.number}@{webhook_payload.pull_request.head['sha']}"

        pr = PullRequestModel(
            pull_request_id=pr_unique_id,
            repository_owner=webhook_payload.repository.full_name.split("/")[0],
            repository_name=webhook_payload.repository.full_name.split("/")[1],
            title=webhook_payload.pull_request.title,
            description=webhook_payload.pull_request.body,
        )
        self.session.add(pr)
        await self.session.flush()

        return pr

    async def insert_review(self, webhook_payload, pull_request_id):
        review = ReviewModel(
            pull_request_id=pull_request_id,
            status="pending",
        )
        self.session.add(review)

        return review

    async def get_pull_request_reviews(
        self, pull_request_id: str, page: int, limit: int, order: str, order_by: str
    ):
        stmt = (
            select(PullRequestModel, ReviewModel)
            .join(ReviewModel, PullRequestModel.id == ReviewModel.pull_request_id)
            .where(PullRequestModel.pull_request_id == pull_request_id)
        )

        if order_by == "created_at":
            order_func = desc if order == "desc" else asc
            stmt = stmt.order_by(order_func(ReviewModel.created_at))
        elif order_by == "status":
            order_func = desc if order == "desc" else asc
            stmt = stmt.order_by(order_func(ReviewModel.status))

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        return result.all()

    async def get_pull_request_last_review(self, pull_request: PullRequestModel):
        review_stmt = (
            select(ReviewModel)
            .where(ReviewModel.pull_request_id == pull_request.id)
            .order_by(desc(ReviewModel.created_at))
            .limit(1)
        )
        review_result = await self.session.execute(review_stmt)
        review = review_result.scalar_one_or_none()
        return review
