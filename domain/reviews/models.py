from sqlalchemy import BigInteger, Column, ForeignKey, Index, JSON, Text, TIMESTAMP, func
from shared.database import Base


class ReviewModel(Base):
    """Model representing a review for a pull request.

    Stores AI-generated reviews with status, summary, detailed feedback,
    and metadata about the AI model used.
    """

    __tablename__ = "reviews"
    __table_args__ = (
        Index(
            "idx_reviews_pr_id_status",
            "pull_request_id",
            "status",
            postgresql_include=["details", "ai_model", "created_at", "summary"]
        ),
    )

    id = Column(BigInteger, primary_key=True, doc="Unique identifier for the review")
    pull_request_id = Column(
        BigInteger,
        ForeignKey("pull_requests.id"),
        nullable=False,
        doc="Foreign key to the associated pull request"
    )
    status = Column(
        Text,
        nullable=False,
        server_default="created",
        doc="Current status of the review"
    )
    summary = Column(Text, nullable=True, doc="Brief summary of the review")
    details = Column(
        JSON,
        nullable=True,
        doc="Detailed review data in JSON format"
    )
    ai_model = Column(
        Text,
        nullable=False,
        doc="Name or identifier of the AI model used for the review"
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the review was created"
    )


class ReviewCommentModel(Base):
    """Model representing individual comments within a review.

    Each comment is tied to a specific file, line, and severity level,
    providing granular feedback on code changes.
    """

    __tablename__ = "review_comments"
    __table_args__ = (
        Index(
            "idx_review_comments_rv_id",
            "review_id",
            postgresql_include=["file_path", "line_number", "severity", "message"]
        ),
    )

    id = Column(BigInteger, primary_key=True, doc="Unique identifier for the review comment")
    review_id = Column(
        BigInteger,
        ForeignKey("reviews.id"),
        nullable=False,
        doc="Foreign key to the associated review"
    )
    file_path = Column(Text, nullable=False, doc="Path to the file being commented on")
    line_number = Column(BigInteger, nullable=False, doc="Line number in the file")
    severity = Column(Text, nullable=False, doc="Severity level")
    message = Column(Text, nullable=False, doc="The comment message")
