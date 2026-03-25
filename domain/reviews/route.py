from fastapi import APIRouter, Path, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from .schemas import ReviewComment, Reviews, ReviewResponse, Review
from .repository import ReviewRepository
from shared.database import get_db_session

router = APIRouter()


def get_review_repository(session: AsyncSession = Depends(get_db_session)):
    return ReviewRepository(session)


@router.get("/reviews", response_model=Reviews)
async def get_reviews(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    order: Annotated[str, Query(enum=["asc", "desc"])] = "desc",
    order_by: Annotated[str, Query(enum=["created_at", "status"])] = "created_at",
    review_repo: ReviewRepository = Depends(get_review_repository),
):
    reviews = await review_repo.get_reviews(page, limit, order_by, order)

    return Reviews(
        reviews=[
            Review(
                review_id=review.id,
                pull_request_id=review.pull_request_id,
                status=review.status,
                summary=review.summary,
                ai_model=review.ai_model,
                created_at=review.created_at,
            )
            for review in reviews
        ]
        if reviews
        else []
    )


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: Annotated[int, Path(alias="review_id")],
    review_repo: ReviewRepository = Depends(get_review_repository),
):
    review, review_comments = await review_repo.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, details="Review not found")
    return ReviewResponse(
        created_at=review.created_at,
        status=review.status,
        ai_model=review.ai_model,
        pull_request_id=review.pull_request_id,
        summary=review.summary,
        review_comments=[
            ReviewComment(
                path_file=review_comment.path_file,
                line_number=review_comment.line_number,
                severity=review_comment.severity,
                message=review_comment.message,
            )
            for review_comment in review_comments
        ],
    )
