from app.alerts.formatters.price_formatter import format_price


class LevelsPlainFormatter:
    def format(self, symbol: str, timeframe: str, levels: dict[str, list[dict]]) -> str:
        supports = levels["supports"]
        resistances = levels["resistances"]

        lines: list[str] = []
        lines.append(f"<b>{symbol} • Уровни ({timeframe})</b>")
        lines.append("")

        lines.append("🟢 Ближайшие уровни поддержки:")
        if supports:
            for i, lvl in enumerate(supports, start=1):
                lines.append(f"{i}) {format_price(lvl['avg_price'])}")
        else:
            lines.append("—")

        lines.append("")
        lines.append("🔴 Ближайшие уровни сопротивления:")
        if resistances:
            for i, lvl in enumerate(resistances, start=1):
                lines.append(f"{i}) {format_price(lvl['avg_price'])}")
        else:
            lines.append("—")

        return "\n".join(lines)
