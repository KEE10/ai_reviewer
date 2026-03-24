from sqlalchemy import BigInteger, Column, Index, Text, TIMESTAMP, func

from shared.database import Base


class PullRequestModel(Base):
    __tablename__ = "pull_requests"
    __table_args__ = (
        Index("idx_pull_requests_repo", "repo_owner"),
    )

    id = Column(BigInteger, primary_key=True)
    pull_request_id = Column(Text, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    repo_owner = Column(Text, nullable=False)
    repo_name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
