from .base import BaseTokenRepository


class InMemoryTokenRepository(BaseTokenRepository):
    def __init__(self, token_map: dict[int, list[str]] | None = None):
        self.token_map = token_map or {}

    def get_user_tokens(self, user_id: int) -> list[str]:
        return self.token_map.get(user_id, [])