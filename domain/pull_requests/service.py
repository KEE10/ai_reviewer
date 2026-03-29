import hashlib
import hmac
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from shared.exceptions import (
    WebhookAlreadyProcessedException,
    PRNotReadyForReview,
    PublishReviewGithubFailedException,
)
from shared.clients import httpx_client
from .repository import PullRequestRepository
from .schemas import WebhookPayload, Action


def verify_signature(payload: dict, github_signature: str):
    secret = settings.github_secret.encode("utf-8")
    expected_signature = (
        "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    )

    return hmac.compare_digest(github_signature, expected_signature)


async def atomic_insert_pull_request_and_review(
    pr_repository: PullRequestRepository, webhook_payload: WebhookPayload
) -> None:
    try:
        pr = await pr_repository.insert_pull_request(webhook_payload)
    except WebhookAlreadyProcessedException:
        raise

    if webhook_payload.action not in [
        Action.opened,
        Action.ready_for_review,
        Action.synchronize,
    ]:
        raise PRNotReadyForReview

    review = await pr_repository.insert_review(webhook_payload, pr.id)
    await pr_repository.session.commit()
    return pr, review


async def handle_pr_reviewed(session: AsyncSession, payload: dict) -> None:
    pr_id = payload["pr_id"]
    details = payload["details"]

    await publish_to_github(pr_id, details)


# move to github_service.py
async def publish_to_github(pr_id: str, details: dict) -> None:
    # Extract repo and PR number from pr_id (format: "owner/repo#123@commit")
    repo_fullname = pr_id.split("#")[0]
    pr_number = int(pr_id.split("#")[1].split("@")[0])

    ai_response = details.get("ai_response", {})
    summary = ai_response.get("summary", "AI review completed")
    comments = ai_response.get("comments", [])

    review_comments = []
    for comment in comments:
        review_comment = {
            "path": comment.get("file_path", ""),
            "line": comment.get("line_number"),
            "body": f"**{comment.get('severity').title()}**: {comment.get('message')}",
        }
        if review_comment["path"]:
            review_comments.append(review_comment)

    review_payload = {
        "body": f"**AI Code Review**\n\n{summary}",
        "event": "COMMENT",
        "comments": review_comments,
    }

    url = f"https://api.github.com/repos/{repo_fullname}/pulls/{pr_number}/reviews"
    headers = {
        "Authorization": f"token {settings.github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = await httpx_client.post(url, json=review_payload, headers=headers)
    try:
        response.raise_for_status()
    except Exception as e:
        raise PublishReviewGithubFailedException(
            message=f"Failed to publish review to GitHub PR {repo_fullname}#{pr_number}",
            payload={
                "pr_id": pr_id,
                "repo_fullname": repo_fullname,
                "pr_number": pr_number,
                "status_code": response.status_code,
                "response_text": response.text,
                "error": str(e),
            },
        )
