from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from datetime import datetime

from domain.reviews.schemas import ReviewResponse


class Action(str, Enum):
    ready_for_review = "ready_for_review"
    synchronize = "synchronize"
    opened = "opened"


class PullRequest(BaseModel):
    id: int
    title: str
    draft: bool
    body: str | None = None
    head: dict
    base: dict


class Repository(BaseModel):
    id: int
    name: str
    full_name: str


class Sender(BaseModel):
    id: int
    login: str


class WebhookPayload(BaseModel):
    action: Action
    number: int
    pull_request: PullRequest
    repository: Repository
    sender: Sender


class PullRequestWithReviewsResponse(BaseModel):
    pull_request_id: str
    repository_owner: str
    repository_name: str
    title: str
    description: Optional[str]
    created_at: datetime
    reviews: List[ReviewResponse]
