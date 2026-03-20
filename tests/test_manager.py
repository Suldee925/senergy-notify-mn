from notify_mn import NotificationManager
from notify_mn.exceptions import InvalidDeviceTokenError, ProviderRetryableError
from notify_mn.repositories.device_tokens import InMemoryTokenRepository
from notify_mn.repositories.notification_logs import InMemoryLogRepository


class FakeProvider:
    name = "fake"

    def send(self, token: str, payload) -> dict:
        return {
            "success": True,
            "provider": "fake",
            "token": token,
            "title": payload.title,
            "body": payload.body,
            "priority": payload.priority,
            "notification_type": payload.notification_type,
            "message_id": "test-message-id",
        }


class RetryThenSuccessProvider:
    name = "fake"

    def __init__(self):
        self.calls = 0

    def send(self, token: str, payload) -> dict:
        self.calls += 1
        if self.calls < 2:
            raise ProviderRetryableError("temporary")
        return {
            "success": True,
            "provider": "fake",
            "token": token,
            "title": payload.title,
            "body": payload.body,
            "priority": payload.priority,
            "notification_type": payload.notification_type,
            "message_id": "retried-success",
        }


class InvalidTokenProvider:
    name = "fake"

    def send(self, token: str, payload) -> dict:
        raise InvalidDeviceTokenError("registration-token-not-registered")


class InsufficientBalanceError(Exception):
    description = "Balance insufficient"


class ChargePointOfflineError(Exception):
    description = "Charge point offline"


class InvalidCredentialsError(Exception):
    description = "Invalid credentials"


def test_send_template():
    token_repo = InMemoryTokenRepository({1: ["abc"]})
    log_repo = InMemoryLogRepository()
    provider = FakeProvider()

    manager = NotificationManager(provider, token_repo, log_repo)
    results = manager.send_template(user_id=1, template_key="charging_completed")

    assert len(results) == 1
    assert results[0]["success"] is True
    assert results[0]["provider"] == "fake"
    assert len(log_repo.logs) == 1
    assert log_repo.logs[0]["body"] == "Таны машин амжилттай цэнэглэгдэж дууслаа."


def test_send_template_no_tokens():
    token_repo = InMemoryTokenRepository({})
    log_repo = InMemoryLogRepository()
    provider = FakeProvider()

    manager = NotificationManager(provider, token_repo, log_repo)
    results = manager.send_template(user_id=999, template_key="charging_completed")

    assert results == [{"success": False, "error": "NO_DEVICE_TOKENS"}]
    assert len(log_repo.logs) == 0


def test_send_error_notification_should_notify():
    token_repo = InMemoryTokenRepository({1: ["abc"]})
    log_repo = InMemoryLogRepository()
    provider = FakeProvider()

    manager = NotificationManager(provider, token_repo, log_repo)
    results = manager.send_error_notification(user_id=1, error=InsufficientBalanceError())

    assert len(results) == 1
    assert results[0]["success"] is True
    assert results[0]["title"] == "Үлдэгдэл хүрэлцэхгүй байна"
    assert len(log_repo.logs) == 1


def test_send_error_notification_should_not_notify():
    token_repo = InMemoryTokenRepository({1: ["abc"]})
    log_repo = InMemoryLogRepository()
    provider = FakeProvider()

    manager = NotificationManager(provider, token_repo, log_repo)
    results = manager.send_error_notification(user_id=1, error=InvalidCredentialsError())

    assert results == []
    assert len(log_repo.logs) == 0


def test_send_error_notification_charging_station():
    token_repo = InMemoryTokenRepository({1: ["abc"]})
    log_repo = InMemoryLogRepository()
    provider = FakeProvider()

    manager = NotificationManager(provider, token_repo, log_repo)
    results = manager.send_error_notification(user_id=1, error=ChargePointOfflineError())

    assert len(results) == 1
    assert results[0]["success"] is True
    assert results[0]["title"] == "Цэнэглэгч ажиллахгүй байна"
    assert len(log_repo.logs) == 1


def test_retry_then_success():
    token_repo = InMemoryTokenRepository({1: ["abc"]})
    log_repo = InMemoryLogRepository()
    provider = RetryThenSuccessProvider()

    manager = NotificationManager(provider, token_repo, log_repo, max_retries=2)
    results = manager.send_template(user_id=1, template_key="charging_completed")

    assert len(results) == 1
    assert results[0]["success"] is True
    assert provider.calls == 2


def test_invalid_token_deactivates_token():
    token_repo = InMemoryTokenRepository({1: ["dead-token"]})
    log_repo = InMemoryLogRepository()
    provider = InvalidTokenProvider()

    manager = NotificationManager(provider, token_repo, log_repo)
    results = manager.send_template(user_id=1, template_key="charging_completed")

    assert len(results) == 1
    assert results[0]["success"] is False
    assert results[0]["token_deactivated"] is True
    assert token_repo.get_user_tokens(1) == []


def test_register_token_updates_repository():
    token_repo = InMemoryTokenRepository({})
    token_repo.register_token(
        user_id=7,
        token="new-token",
        platform="android",
        is_active=True,
    )

    assert token_repo.get_user_tokens(7) == ["new-token"]