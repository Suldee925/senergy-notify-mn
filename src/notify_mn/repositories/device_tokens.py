from .base import BaseTokenRepository


class InMemoryTokenRepository(BaseTokenRepository):
    def __init__(self, token_map: dict[int, list[str]] | None = None):
        self.records: list[dict] = []

        if token_map:
            for user_id, tokens in token_map.items():
                for token in tokens:
                    self.records.append(
                        {
                            "user_id": user_id,
                            "token": token,
                            "platform": "unknown",
                            "is_active": True,
                            "deactivate_reason": None,
                        }
                    )

    def register_token(
        self,
        *,
        user_id: int,
        token: str,
        platform: str,
        is_active: bool = True,
    ) -> None:
        for record in self.records:
            if record["token"] == token:
                record["user_id"] = user_id
                record["platform"] = platform
                record["is_active"] = is_active
                record["deactivate_reason"] = None
                return

        self.records.append(
            {
                "user_id": user_id,
                "token": token,
                "platform": platform,
                "is_active": is_active,
                "deactivate_reason": None,
            }
        )

    def get_user_tokens(self, user_id: int) -> list[str]:
        return [
            record["token"]
            for record in self.records
            if record["user_id"] == user_id and record["is_active"]
        ]

    def deactivate_token(self, token: str, *, reason: str | None = None) -> None:
        for record in self.records:
            if record["token"] == token:
                record["is_active"] = False
                record["deactivate_reason"] = reason
                return