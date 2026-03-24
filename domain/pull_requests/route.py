from fastapi import APIRouter, Header, HTTPException, Depends, Path, Query, status, Request
from typing import Annotated, List, Optional


from shared.database import get_db_session
from shared.events import emit
from sqlalchemy.ext.asyncio import AsyncSession

from .service import verify_signature, atomic_insert_pull_request_and_review
from .repository import PullRequestRepository
from domain.pull_requests.schemas import PullRequestModel, WebhookPayload,PullRequestWithReviewsResponse
from domain.reviews.schemas import ReviewResponse
from shared.exceptions import PRNotReadyForReview, WebhookAlreadyProcessedException


router = APIRouter()

def get_pull_request_repository(session: AsyncSession = Depends(get_db_session)):
    return PullRequestRepository(session)

@router.post("/webhook/github", status_code=status.HTTP_202_ACCEPTED)
async def handle_webhook(
    request: Request,
    webhook_payload: WebhookPayload,
    x_hub_signature_256: Annotated[str | None, Header(alias="X-Hub-Signature-256")] = None,
    pr_repository: PullRequestRepository = Depends(get_pull_request_repository)
):
    gh_payload = await request.body()
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    if not verify_signature(gh_payload, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    if webhook_payload.pull_request.draft == True:
        return {"status": "PR not ready for review"}

    try:
        pr, review = await atomic_insert_pull_request_and_review(pr_repository, webhook_payload)
    except WebhookAlreadyProcessedException:
        return {"status": "already_processed"}
    except PRNotReadyForReview:
        return {"status": "PR not ready for review"}
     
    await emit("pr.created", {
        "pr_id": pr.pull_request_id,
        "review_id": review.id,
        "action": webhook_payload.action.value,
        "repository": webhook_payload.repository.full_name,
    })

    return {"status": "processed"}


@router.get("/pull_requests/{pull_request_id}", response_model=PullRequestWithReviewsResponse)
async def get_pull_request(
    pull_request_id: Annotated[str, Path(alias="pull_request_id")],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    order_by: Annotated[str, Query(enum=["created_at", "status"])] = "created_at",
    order: Annotated[str, Query(enum=["asc", "desc"])] = "desc",
    pr_repository: PullRequestRepository = Depends(get_pull_request_repository)
):
    rows = await pr_repository.get_pull_request_reviews(pull_request_id, page, limit, order, order_by)
    
    if not rows:
        raise HTTPException(status_code=404, detail="Pull request not found")
    
    pr = rows[0][0] 
    reviews = [
        ReviewResponse(
            id=row[1].id,
            status=row[1].status,
            created_at=row[1].created_at,
        )
        for row in rows
    ]
    
    return PullRequestWithReviewsResponse(
        pull_request_id=pr.pull_request_id,
        repository_owner=pr.repo_owner,
        repository_name=pr.repo_name,
        title=pr.title,
        description=pr.description,
        created_at=pr.created_at,
        reviews=reviews,
    )

@router.get("/pull_requests/{pull_request_id}/review", response_model=ReviewResponse)
async def get_pull_request_last_review(
    pull_request_id: Annotated[str, Path(alias="pull_request_id")],
    pr_repository: PullRequestRepository = Depends(get_pull_request_repository)
):
    pr = await pr_repository.get_pull_request(pull_request_id)
    if not pr:
        raise HTTPException(status_code=404, detail="Pull request not found")
    
    review = await pr_repository.get_pull_request_last_review(pr)
    if not review:
        raise HTTPException(status_code=404, detail="No reviews found for this pull request")
    
    return ReviewResponse(
        id=review.id,
        status=review.status,
        created_at=review.created_at,
    )

