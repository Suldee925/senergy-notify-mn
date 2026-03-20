from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import firebase_admin
from firebase_admin import credentials, messaging

from notify_mn.exceptions import InvalidDeviceTokenError, ProviderRetryableError


INVALID_TOKEN_MARKERS = (
    "registration-token-not-registered",
    "requested entity was not found",
    "not a valid fcm registration token",
    "registration token is not valid",
    "unregistered",
    "invalid registration token",
)

RETRYABLE_MARKERS = (
    "internal",
    "server unavailable",
    "quota exceeded",
    "temporarily unavailable",
    "deadline exceeded",
    "timeout",
    "timed out",
)


@dataclass(slots=True)
class ProviderErrorContext:
    message: str
    is_invalid_token: bool = False
    is_retryable: bool = False


class FCMProvider:
    name = "fcm"

    def __init__(self, service_account_path: str):
        if not service_account_path:
            raise ValueError("service_account_path is required")

        self.service_account_path = service_account_path

        if not firebase_admin._apps:
            cred = credentials.Certificate(self.service_account_path)
            firebase_admin.initialize_app(cred)

    def send(self, token: str, payload) -> dict[str, Any]:
        try:
            message = messaging.Message(
                token=token,
                notification=messaging.Notification(
                    title=payload.title,
                    body=payload.body,
                ),
                data={k: str(v) for k, v in (payload.data or {}).items()},
                android=messaging.AndroidConfig(
                    priority=self._android_priority(payload.priority)
                ),
                apns=messaging.APNSConfig(
                    headers={"apns-priority": self._apns_priority(payload.priority)}
                ),
            )

            message_id = messaging.send(message)

        except Exception as exc:  # pragma: no cover
            context = self.classify_error(exc)

            if context.is_invalid_token:
                raise InvalidDeviceTokenError(context.message) from exc

            if context.is_retryable:
                raise ProviderRetryableError(context.message) from exc

            raise RuntimeError(context.message) from exc

        return {
            "success": True,
            "provider": self.name,
            "token": token,
            "title": payload.title,
            "body": payload.body,
            "priority": payload.priority,
            "notification_type": payload.notification_type,
            "message_id": message_id,
        }

    def classify_error(self, error: Exception) -> ProviderErrorContext:
        message = str(error)
        lowered = message.lower()

        return ProviderErrorContext(
            message=message,
            is_invalid_token=any(marker in lowered for marker in INVALID_TOKEN_MARKERS),
            is_retryable=any(marker in lowered for marker in RETRYABLE_MARKERS),
        )

    @staticmethod
    def _android_priority(priority: str) -> str:
        return "high" if priority == "high" else "normal"

    @staticmethod
    def _apns_priority(priority: str) -> str:
        return "10" if priority == "high" else "5"