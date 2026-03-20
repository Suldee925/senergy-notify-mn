from .base import BaseLogRepository


class InMemoryLogRepository(BaseLogRepository):
    def __init__(self):
        self.logs: list[dict] = []

    def save(
        self,
        *,
        user_id: int,
        token: str,
        title: str,
        body: str,
        result: dict,
        priority: str,
        notification_type: str,
    ) -> None:
        self.logs.append(
            {
                "user_id": user_id,
                "token": token,
                "title": title,
                "body": body,
                "result": result,
                "priority": priority,
                "notification_type": notification_type,
            }
        )