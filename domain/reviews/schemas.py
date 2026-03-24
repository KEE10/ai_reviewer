from pydantic import BaseModel
from typing import List
from datetime import datetime

class Review(BaseModel):
    review_id: int
    pull_request_id: str
    status: str
    created_at: datetime
    ai_model: str
    summary: str

class ReviewComment(BaseModel):
    file_path: str
    line_number: int
    severity: str
    message: str

class ReviewResponse(Review):
    review_comments: List[ReviewComment] = []

class Reviews(BaseModel):
    reviews: List[Review] = []