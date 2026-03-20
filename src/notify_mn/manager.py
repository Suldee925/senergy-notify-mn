from __future__ import annotations

from .exceptions import TemplateNotFoundError
from .models import NotificationPayload
from .templates import TEMPLATES


class NotificationManager:
    def __init__(self, provider, token_repo, log_repo):
        self.provider = provider
        self.token_repo = token_repo
        self.log_repo = log_repo

    def send(self, user_id: int, title: str, body: str, data: dict | None = None) -> list[dict]:
        tokens = self.token_repo.get_user_tokens(user_id)
        payload = NotificationPayload(
            user_id=user_id,
            title=title,
            body=body,
            data=data or {},
        )

        results = []

        for token in tokens:
            try:
                result = self.provider.send(token, payload)
            except Exception as exc:
                result = {
                    "success": False,
                    "provider": "fcm",
                    "token": token,
                    "title": title,
                    "body": body,
                    "error": str(exc),
                }

            self.log_repo.save(
                user_id=user_id,
                token=token,
                title=title,
                body=body,
                result=result,
            )
            results.append(result)

        return results

    def send_template(self, user_id: int, template_key: str, **kwargs) -> list[dict]:
        if template_key not in TEMPLATES:
            raise TemplateNotFoundError(f"Template not found: {template_key}")

        body = TEMPLATES[template_key].format(**kwargs)

        return self.send(
            user_id=user_id,
            title="Senergy",
            body=body,
            data={"template": template_key, **kwargs},
        )