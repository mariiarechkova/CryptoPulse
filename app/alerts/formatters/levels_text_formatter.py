class LevelsPlainFormatter:
    def format(self, levels: dict[str, list[dict]]) -> str:
        supports = levels["supports"]
        resistances = levels["resistances"]

        lines: list[str] = []

        lines.append("")
        lines.append("↧ Ближайшие уровни поддержки:")
        if supports:
            for i, lvl in enumerate(supports, start=1):
                lines.append(f"{i}) {lvl['avg_price']:.2f}")
        else:
            lines.append("—")

        lines.append("")
        lines.append("↥ Ближайшие уровни сопротивления:")
        if resistances:
            for i, lvl in enumerate(resistances, start=1):
                lines.append(f"{i}) {lvl['avg_price']:.2f}")
        else:
            lines.append("—")

        return "\n".join(lines)
