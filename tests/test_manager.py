from notify_mn import NotificationManager
from notify_mn.repositories.device_tokens import InMemoryTokenRepository
from notify_mn.repositories.notification_logs import InMemoryLogRepository


class FakeProvider:
    def send(self, token: str, payload) -> dict:
        return {
            "success": True,
            "provider": "fake",
            "token": token,
            "title": payload.title,
            "body": payload.body,
            "message_id": "test-message-id",
        }


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