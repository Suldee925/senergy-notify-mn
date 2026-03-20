from __future__ import annotations


class NotificationService:
    def __init__(self, manager):
        self.manager = manager

    def register_device_token(self, *, user_id: int, token: str, platform: str) -> None:
        self.manager.token_repo.register_token(
            user_id=user_id,
            token=token,
            platform=platform,
            is_active=True,
        )

    def send_payment_failed(self, user_id: int, reason: str) -> list[dict]:
        return self.manager.send(
            user_id=user_id,
            title="Төлбөр амжилтгүй",
            body="Төлбөр хийх үед алдаа гарлаа. Дахин оролдоно уу.",
            priority="high",
            notification_type="payment_failed",
            data={
                "type": "payment_failed",
                "reason": reason,
            },
        )

    def send_payment_success(self, user_id: int, amount: int | float | str) -> list[dict]:
        return self.manager.send_template(
            user_id=user_id,
            template_key="payment_success",
            amount=amount,
        )

    def send_balance_low(self, user_id: int, current_balance: int | float | str) -> list[dict]:
        return self.manager.send(
            user_id=user_id,
            title="Үлдэгдэл бага байна",
            body="Таны үлдэгдэл дуусах дөхөж байна. Цэнэглэнэ үү.",
            priority="normal",
            notification_type="balance_low",
            data={
                "type": "balance_low",
                "current_balance": current_balance,
            },
        )

    def send_charging_completed(self, user_id: int, session_id: str) -> list[dict]:
        return self.manager.send(
            user_id=user_id,
            title="Цэнэглэлт дууслаа",
            body="Таны машин амжилттай цэнэглэгдэж дууслаа.",
            priority="normal",
            notification_type="charging_completed",
            data={
                "type": "charging_completed",
                "session_id": session_id,
            },
        )

    def send_charging_error(self, user_id: int, reason: str) -> list[dict]:
        return self.manager.send(
            user_id=user_id,
            title="Цэнэглэлтэд алдаа гарлаа",
            body="Цэнэглэж байх үед алдаа гарлаа. Оператор руу холбогдоно уу.",
            priority="high",
            notification_type="charging_error",
            data={
                "type": "charging_error",
                "reason": reason,
            },
        )

    def send_invoice_ready(self, user_id: int, invoice_id: str) -> list[dict]:
        return self.manager.send(
            user_id=user_id,
            title="Нэхэмжлэл бэлэн боллоо",
            body="Таны нэхэмжлэл бэлэн боллоо.",
            priority="normal",
            notification_type="invoice_ready",
            data={
                "type": "invoice_ready",
                "invoice_id": invoice_id,
            },
        )

    def send_error_from_exception(self, user_id: int, error: Exception) -> list[dict]:
        return self.manager.send_error_notification(user_id=user_id, error=error)