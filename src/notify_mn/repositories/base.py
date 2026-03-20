class BaseTokenRepository:
    def get_user_tokens(self, user_id: int) -> list[str]:
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
    ) -> None:
        raise NotImplementedError