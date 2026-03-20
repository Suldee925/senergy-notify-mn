from __future__ import annotations

from .error_policy import ERROR_POLICY
from .exceptions import InvalidDeviceTokenError, TemplateNotFoundError
from .models import NotificationPayload
from .retry import retry_call
from .templates import TEMPLATES


class NotificationManager:
    def __init__(self, provider, token_repo, log_repo, *, max_retries: int = 2):
        self.provider = provider
        self.token_repo = token_repo
        self.log_repo = log_repo
        self.max_retries = max_retries

    def send(
        self,
        user_id: int,
        title: str,
        body: str,
        data: dict | None = None,
        *,
        priority: str = "normal",
        notification_type: str = "general",
    ) -> list[dict]:
        tokens = self.token_repo.get_user_tokens(user_id)

        if not tokens:
            return [{"success": False, "error": "NO_DEVICE_TOKENS"}]

        payload = NotificationPayload(
            user_id=user_id,
            title=title,
            body=body,
            data=data or {},
            priority=priority,
            notification_type=notification_type,
        )

        results: list[dict] = []

        for token in tokens:
            result = self._send_to_token(token=token, payload=payload)

            self.log_repo.save(
                user_id=user_id,
                token=token,
                title=title,
                body=body,
                result=result,
                priority=priority,
                notification_type=notification_type,
            )
            results.append(result)

        return results

    def send_template(self, user_id: int, template_key: str, **kwargs) -> list[dict]:
        if template_key not in TEMPLATES:
            raise TemplateNotFoundError(f"Template not found: {template_key}")

        template = TEMPLATES[template_key]
        title = template["title"].format(**kwargs)
        body = template["body"].format(**kwargs)

        return self.send(
            user_id=user_id,
            title=title,
            body=body,
            data={"template": template_key, **kwargs},
            priority=template.get("priority", "normal"),
            notification_type=template.get("type", template_key),
        )

    def send_error_notification(self, user_id: int, error: Exception) -> list[dict]:
        error_name = error.__class__.__name__
        policy = ERROR_POLICY.get(error_name)

        if not policy or not policy["should_notify"]:
            return []

        return self.send(
            user_id=user_id,
            title=policy["title"],
            body=policy["body"],
            priority=policy.get("priority", "normal"),
            notification_type=policy.get("type", "error_notification"),
            data={
                "type": policy.get("type", "error_notification"),
                "group": policy["group"],
                "error_name": error_name,
                "description": getattr(error, "description", str(error)),
            },
        )

    def _send_to_token(self, *, token: str, payload: NotificationPayload) -> dict:
        try:
            return retry_call(
                lambda: self.provider.send(token, payload),
                max_retries=self.max_retries,
            )

        except InvalidDeviceTokenError as exc:
            self.token_repo.deactivate_token(token, reason=str(exc))
            return {
                "success": False,
                "provider": getattr(self.provider, "name", "provider"),
                "token": token,
                "title": payload.title,
                "body": payload.body,
                "priority": payload.priority,
                "notification_type": payload.notification_type,
                "error": str(exc),
                "token_deactivated": True,
            }

        except Exception as exc:
            return {
                "success": False,
                "provider": getattr(self.provider, "name", "provider"),
                "token": token,
                "title": payload.title,
                "body": payload.body,
                "priority": payload.priority,
                "notification_type": payload.notification_type,
                "error": str(exc),
                "token_deactivated": False,
            }