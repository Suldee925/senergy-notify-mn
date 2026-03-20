from dataclasses import dataclass, field
from typing import Any


@dataclass
class NotificationPayload:
    user_id: int
    title: str
    body: str
    data: dict[str, Any] = field(default_factory=dict)