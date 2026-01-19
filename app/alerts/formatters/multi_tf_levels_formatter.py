class MultiTFLevelsFormatter:
    def format(self, ctx) -> str:
        lines = []
        lines.append("\n<b>Уровни (Multi-TF)</b>")

        if ctx.nearest_support is not None:
            z = ctx.nearest_support
            lines.append(
                f"🟢 <b>Ближайшая поддержка:</b> {z.min_price:.6g}–{z.max_price:.6g} (~{z.avg_price:.6g})"
            )
        else:
            lines.append("🟢 <b>Ближайшая поддержка:</b> —")

        if ctx.nearest_resistance is not None:
            z = ctx.nearest_resistance
            lines.append(
                f"🔴 <b>Ближайшее сопротивление:</b> {z.min_price:.6g}–{z.max_price:.6g} (~{z.avg_price:.6g})"
            )
        else:
            lines.append("🔴 <b>Ближайшее сопротивление:</b> —")

        return "\n".join(lines) + "\n"
