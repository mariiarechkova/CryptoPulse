from enum import Enum


class TariffCode(str, Enum):
    FREE = "free"
    PAID_MONTH = "paid_month"
    PAID_YEAR = "paid_year"


class PaymentProvider(str, Enum):
    CRYPTOBOT = "cryptobot"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    APPLIED = "applied"
    EXPIRED = "expired"
    FAILED = "failed"