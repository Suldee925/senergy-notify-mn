class NotificationError(Exception):
    pass


class TemplateNotFoundError(NotificationError):
    pass


class ProviderRetryableError(NotificationError):
    pass


class InvalidDeviceTokenError(NotificationError):
    pass