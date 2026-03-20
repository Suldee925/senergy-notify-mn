class BaseTokenRepository:
    def register_token(
        self,
        *,
        user_id: int,
        token: str,
        platform: str,
        is_active: bool = True,
    ) -> None:
        raise NotImplementedError

    def get_user_tokens(self, user_id: int) -> list[str]:
        raise NotImplementedError

    def deactivate_token(self, token: str, *, reason: str | None = None) -> None:
        raise NotImplementedError


class BaseLogRepository:
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
        raise NotImplementedError