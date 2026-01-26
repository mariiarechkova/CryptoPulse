from decimal import ROUND_HALF_UP, Decimal


def format_price(value: float | Decimal) -> str:
    v = Decimal(str(value))

    if v < Decimal("10"):
        q = Decimal("0.0001")
    else:
        q = Decimal("0.01")

    return f"{v.quantize(q, rounding=ROUND_HALF_UP):f}"
