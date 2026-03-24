from typing import List, Optional
from sqlalchemy import select, asc, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ReviewModel, ReviewCommentModel


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_review(
        self,
        pull_request_id: int,
        ai_model: str,
        summary: Optional[str] = None,
        details: Optional[dict] = None
    ) -> ReviewModel:
        review = ReviewModel(
            pull_request_id=pull_request_id,
            status="created",
            ai_model=ai_model,
            summary=summary,
            details=details
        )
        self.session.add(review)
        await self.session.flush()  
        return review

    async def get_reviews(
        self,
        page: int = 1,
        limit: int = 10,
        order_by: str = "created_at",
        order: str = "desc"
    ) -> List[ReviewModel]:
        stmt = select(ReviewModel)

        if order_by == "created_at":
            order_func = desc if order == "desc" else asc
            stmt = stmt.order_by(order_func(ReviewModel.created_at))
        elif order_by == "status":
            order_func = desc if order == "desc" else asc
            stmt = stmt.order_by(order_func(ReviewModel.status))
        else:
            stmt = stmt.order_by(desc(ReviewModel.created_at))  # Default

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_review(self, review_id: str) -> Optional[dict]:
        stmt = (
            select(ReviewModel, ReviewCommentModel)
            .join(ReviewCommentModel, ReviewModel.id == ReviewCommentModel.review_id)
            .where(ReviewModel.id == review_id)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        if not rows:
            return None, None

        review = rows[0][0]
        comments = [row[1] for row in rows]

        return review, comments

    async def update_review(self, review_id: str, **kwargs) -> bool:
        stmt = (
            update(ReviewModel)
            .where(ReviewModel.id == review_id)
            .values(**kwargs)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def add_review_comment(
        self,
        review_id: str,
        file_path: Optional[str],
        line_number: Optional[int],
        severity: Optional[str],
        message: Optional[str]
    ) -> ReviewCommentModel:
        comment = ReviewCommentModel(
            review_id=review_id,
            file_path=file_path,
            line_number=line_number,
            severity=severity,
            message=message
        )
        self.session.add(comment)
        await self.session.flush()
        return comment

    async def add_review_comments(
        self,
        review_id: str,
        comments: List[dict]
    ) -> List[ReviewCommentModel]:
        comment_objects = [
            ReviewCommentModel(
                review_id=review_id,
                file_path=comment.get("file_path"),
                line_number=comment.get("line_number"),
                severity=comment.get("severity"),
                message=comment.get("message")
            )
            for comment in comments
        ]
        self.session.add_all(comment_objects)
        await self.session.flush()
        return comment_objects
