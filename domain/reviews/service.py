import json
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy.ext.asyncio import AsyncSession


from shared.events import emit
from config import settings
from .repository import ReviewRepository
from shared.clients import httpx_client, claude_client


class ReviewService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ReviewRepository(session)

    # move to github_service.py
    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _fetch_pr_files(
        self, repo_fullname: str, pr_number: int
    ) -> Dict[str, Any]:
        url = f"https://api.github.com/repos/{repo_fullname}/pulls/{pr_number}/files"
        headers = {"Authorization": f"token {settings.github_token}"}
        response = await httpx_client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    # move to claude_service.py
    async def _call_claude_api(self, files_data: Dict[str, Any]) -> Dict[str, Any]:
        # prompt to be reviewed and tuned for a better output and context
        prompt = f"""Please review the following pull request changes and provide your analysis in JSON format.

Pull Request Files:
{json.dumps(files_data, indent=2)}

Please respond with a JSON object containing:
- "summary": A brief summary of the changes (1-2 sentences)
- "comments": An array of review comments, where each comment has:
  - "file_path": The file path being commented on
  - "line_number": The line number (if applicable, otherwise null)
  - "severity": "critical", "warning", "nice to have" or "positives"
  - "message": The review comment text

Example response format:
{{
  "summary": "This PR adds user authentication functionality with proper error handling.",
  "comments": [
    {{
      "file_path": "auth.py",
      "line_number": 15,
      "severity": "warning",
      "message": "Consider adding input validation for the password field"
    }}
  ]
}}

Respond only with valid JSON, no additional text."""

        message = await claude_client.messages.create(
            model=settings.claude_model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text if message.content else ""

        try:
            parsed_response = json.loads(response_text)
            return parsed_response
        except json.JSONDecodeError:
            # Fallback: return a basic structure if JSON parsing fails
            return {
                "summary": response_text[:500] if response_text else "Review completed",
                "comments": [],
            }

    async def process_pr_review(self, pr_id: str, repo_fullname: str, review_id: int):
        pr_number = int(pr_id.split("#")[1].split("@")[0])

        # Fetch PR files
        files_data = await self._fetch_pr_files(repo_fullname, pr_number)

        # Call Claude for review
        claude_response = await self._call_claude_api(files_data)

        summary = claude_response.get("summary", "No summary")
        details = {"ai_response": claude_response}
        comments = claude_response.get("comments", [])

        # Update review in DB
        review, _ = await self.repository.get_review(review_id)
        await self.repository.update_review(
            review.id, status="completed", summary=summary, details=details
        )

        if comments:
            await self.repository.add_review_comments(review.id, comments)

        await emit(
            "pr.reviewed", {"pr_id": pr_id, "status": "completed", "details": details}
        )


async def handle_pr_created(session: AsyncSession, payload: dict):
    pr_id = payload["pr_id"]
    review_id = payload["review_id"]
    repo_fullname = payload["repository"]

    service = ReviewService(session)
    await service.process_pr_review(pr_id, repo_fullname, review_id)
