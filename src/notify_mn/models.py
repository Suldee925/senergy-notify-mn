from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class NotificationPayload:
    user_id: int
    title: str
    body: str
    data: dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"
    notification_type: str = "general"