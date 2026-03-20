# notify-mn

Simple push notification library for Python.

## Features

- Template-based notifications
- Provider-based architecture
- Token repository abstraction
- Log repository abstraction

## Install

```bash
from notify_mn import FCMProvider, NotificationManager, NotificationService
from your_backend.repositories import DBTokenRepository, DBNotificationLogRepository

provider = FCMProvider(service_account_path=settings.FIREBASE_SERVICE_ACCOUNT_PATH)

manager = NotificationManager(
    provider=provider,
    token_repo=DBTokenRepository(db_session),
    log_repo=DBNotificationLogRepository(db_session),
    max_retries=2,
)

notification_service = NotificationService(manager)