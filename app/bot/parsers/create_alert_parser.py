import re

_SYMBOL_RE = re.compile(r"^[A-Z0-9]{5,}$")


def parse_symbol(text: str | None) -> str:
    raw = (text or "").strip().upper()
    if not _SYMBOL_RE.match(raw):
        raise ValueError("Некорректный тикер. Пример: BTCUSDT")
    return raw


def parse_price(text: str | None) -> float:
    raw = (text or "").strip().replace(" ", "").replace(",", ".")
    try:
        price = float(raw)
    except ValueError as err:
        raise ValueError("Цена должна быть числом. Пример: 89500 или 2950.5") from err

    if price <= 0:
        raise ValueError("Цена должна быть больше 0.")
    return price


def parse_direction_cb(callback_data: str | None) -> str:
    raw = (callback_data or "").strip()
    if not raw.startswith("alert_dir:"):
        raise ValueError("Некорректная кнопка направления.")
    direction = raw.split(":", 1)[1]
    if direction not in ("up", "down"):
        raise ValueError("Некорректное направление.")
    return direction
