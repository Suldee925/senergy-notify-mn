from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    firebase_service_account_path: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            firebase_service_account_path=os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH"),
        )