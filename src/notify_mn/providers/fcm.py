from __future__ import annotations

import os
from typing import Any

import firebase_admin
from firebase_admin import credentials, messaging


class FCMProvider:
    def __init__(self, service_account_path: str | None = None):
        self.service_account_path = service_account_path or os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

        if not self.service_account_path:
            raise ValueError(
                "FCM service account path is missing. "
                "Set FIREBASE_SERVICE_ACCOUNT_PATH or pass service_account_path."
            )

        if not firebase_admin._apps:
            cred = credentials.Certificate(self.service_account_path)
            firebase_admin.initialize_app(cred)

    def send(self, token: str, payload) -> dict[str, Any]:
        message = messaging.Message(
            token=token,
            notification=messaging.Notification(
                title=payload.title,
                body=payload.body,
            ),
            data={k: str(v) for k, v in (payload.data or {}).items()},
        )

        message_id = messaging.send(message)

        return {
            "success": True,
            "provider": "fcm",
            "token": token,
            "title": payload.title,
            "body": payload.body,
            "message_id": message_id,
        }

    def send_to_many(
        self,
        tokens: list[str],
        *,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        for token in tokens:
            payload = type(
                "Payload",
                (),
                {
                    "title": title,
                    "body": body,
                    "data": data or {},
                },
            )()

            try:
                result = self.send(token, payload)
                results.append(result)
            except Exception as exc:
                results.append(
                    {
                        "success": False,
                        "provider": "fcm",
                        "token": token,
                        "title": title,
                        "body": body,
                        "error": str(exc),
                    }
                )

        return results