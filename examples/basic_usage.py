from notify_mn import FCMProvider, NotificationManager, NotificationService
from notify_mn.repositories import InMemoryLogRepository, InMemoryTokenRepository


def main():
    firebase_path = "firebase-service-account.json"

    provider = FCMProvider(service_account_path=firebase_path)
    token_repo = InMemoryTokenRepository()
    log_repo = InMemoryLogRepository()

    manager = NotificationManager(
        provider=provider,
        token_repo=token_repo,
        log_repo=log_repo,
        max_retries=2,
    )
    service = NotificationService(manager)

    service.register_device_token(
        user_id=1,
        token="sample-device-token",
        platform="android",
    )

    result = service.send_charging_completed(
        user_id=1,
        session_id="SESSION-123",
    )

    print(result)


if __name__ == "__main__":
    main()