def parse_levels_message(text: str) -> str:
    raw = (text or "").strip()
    parts = raw.split()

    if len(parts) != 1:
        raise ValueError("Неверный формат. Используй, например: BTCUSDT")

    symbol_raw = parts[0]
    symbol = symbol_raw.upper()

    if len(symbol) < 5 or not symbol.isalnum():
        raise ValueError("Некорректный тикер (например: BTCUSDT).")

    if not symbol.endswith("USDT"):
        raise ValueError("Поддерживаются только пары к USDT.")

    return symbol