def parse_create_alert_message(text: str) -> tuple[str, float, str]:
    raw = (text or "").strip()
    parts = raw.split()

    if len(parts) != 3:
        raise ValueError("Неверный формат. Используй, например: BTCUSDT 105000 up/down")

    symbol_raw, price_raw, direction_raw = parts

    symbol = symbol_raw.upper()
    direction = direction_raw.lower()

    if len(symbol) < 5 or not symbol.isalnum():
        raise ValueError("Некорректный тикер (например: BTCUSDT).")

    try:
        price = float(price_raw)
        if price <= 0:
            raise ValueError
    except ValueError as err:
        raise ValueError("Цена должна быть положительным числом.") from err

    if direction not in ("up", "down"):
        raise ValueError("Направление должно быть 'up' или 'down'")

    return symbol, price, direction
