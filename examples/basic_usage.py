from notify_mn import NotificationManager
from notify_mn.providers import FCMProvider
from notify_mn.repositories.device_tokens import InMemoryTokenRepository
from notify_mn.repositories.notification_logs import InMemoryLogRepository


class InsufficientBalanceError(Exception):
    description = "Balance insufficient"


class ChargePointOfflineError(Exception):
    description = "Charge point offline"


def main():
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

    print("=== TEMPLATE NOTIFICATION ===")
    results = manager.send_template(
        user_id=1,
        template_key="charging_completed",
    )
    for item in results:
        print(item)

    print("\n=== ERROR NOTIFICATION: BALANCE ===")
    results = manager.send_error_notification(
        user_id=1,
        error=InsufficientBalanceError(),
    )
    for item in results:
        print(item)

    print("\n=== ERROR NOTIFICATION: CHARGING ===")
    results = manager.send_error_notification(
        user_id=1,
        error=ChargePointOfflineError(),
    )
    for item in results:
        print(item)

    print("\n=== LOGS ===")
    for log in log_repo.logs:
        print(log)


if __name__ == "__main__":
    main()