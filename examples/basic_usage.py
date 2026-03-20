from notify_mn import NotificationManager
from notify_mn.providers import FCMProvider
from notify_mn.repositories.device_tokens import InMemoryTokenRepository
from notify_mn.repositories.notification_logs import InMemoryLogRepository


def main():
    # Энд жинхэнэ device token тавина
    token_repo = InMemoryTokenRepository({
        1: [
            "PASTE_REAL_FCM_DEVICE_TOKEN_HERE"
        ]
    })

    log_repo = InMemoryLogRepository()
    provider = FCMProvider()

    manager = NotificationManager(
        provider=provider,
        token_repo=token_repo,
        log_repo=log_repo,
    )

    results = manager.send_template(
        user_id=1,
        template_key="car_ready_soon",
    )

    print("RESULTS:")
    for item in results:
        print(item)

    print("\nLOGS:")
    for log in log_repo.logs:
        print(log)


if __name__ == "__main__":
    main()