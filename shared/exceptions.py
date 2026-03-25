from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass
class AppException(Exception):
    message: str
    code: str = "error"
    payload: Optional[Mapping[str, Any]] = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class InvalidDataInWebhookException(AppException):
    def __init__(
        self,
        message: str = "Invalid webhook payload",
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code="invalid_webhook_data", payload=payload)


class WebhookAlreadyProcessedException(AppException):
    def __init__(
        self,
        message: str = "Webhook already processed",
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message, code="webhook_already_processed", payload=payload
        )


class WebhookSignatureMissingException(AppException):
    def __init__(
        self,
        message: str = "Webhook signature missing",
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message, code="webhook_signature_missing", payload=payload
        )


class WebhookWrongSignatureException(AppException):
    def __init__(
        self,
        message: str = "Webhook wrong signature",
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message, code="webhook_wrong_signature", payload=payload
        )


class PRNotReadyForReview(AppException):
    def __init__(
        self,
        message: str = "PR not ready for review",
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message, code="pr_not_ready_for_review", payload=payload
        )


class GithubAuthenticationFailedException(AppException):
    def __init__(
        self,
        message: str = "GitHub authentication failed",
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code="github_auth_failed", payload=payload)


class DiffFetchFailedException(AppException):
    def __init__(
        self,
        message: str = "Failed to fetch diff",
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code="diff_fetch_failed", payload=payload)


class AiProviderAuthenticationFailedException(AppException):
    def __init__(
        self,
        message: str = "AI provider authentication failed",
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message, code="ai_provider_auth_failed", payload=payload
        )


class AiProviderReviewException(AppException):
    def __init__(
        self,
        message: str = "AI provider review failed",
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message, code="ai_provider_review_failed", payload=payload
        )


class PublishReviewGithubFailedException(AppException):
    def __init__(
        self,
        message: str = "Failed to publish review to GitHub",
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message, code="publish_review_github_failed", payload=payload
        )


class ReviewNotFoundException(AppException):
    def __init__(
        self,
        message: str = "Review not found",
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code="review_not_found", payload=payload)
