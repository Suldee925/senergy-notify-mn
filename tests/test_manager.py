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


def test_send_template():
    token_repo = InMemoryTokenRepository({1: ["abc"]})
    log_repo = InMemoryLogRepository()
    provider = FakeProvider()

    manager = NotificationManager(provider, token_repo, log_repo)
    results = manager.send_template(user_id=1, template_key="charge_completed")

    assert len(results) == 1
    assert results[0]["success"] is True
    assert results[0]["provider"] == "fake"
    assert len(log_repo.logs) == 1
    assert log_repo.logs[0]["body"] == "Таны цэнэглэлт дууслаа."