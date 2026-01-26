import random

from app.alerts.formatters.price_formatter import format_price
from app.alerts.services.h1_levels_service import H1LevelsRaw

UP_TEMPLATES = [
    "⬆️ long:\nЗакрепление цены выше {r1} может привести к движению к {r2}.",
    "⬆️ long:\nПри удержании цены выше уровня {r1} фокус смещается к {r2}.",
    "⬆️ long:\nВыход цены выше {r1} открывает пространство для движения к {r2}.",
]

DOWN_TEMPLATES = [
    "⬇️ short:\nСнижение цены ниже поддержки {s1} может привести к движению к {s2}.",
    "⬇️ short:\nПробой уровня {s1} открывает пространство для движения к {s2}.",
    "⬇️ short:\nЕсли поддержка {s1} не удержится, фокус сместится к {s2}.",
]


class H1LevelsFormatter:
    def format(self, raw: H1LevelsRaw) -> str:
        s1 = raw.supports[0] if len(raw.supports) > 0 else None
        s2 = raw.supports[1] if len(raw.supports) > 1 else None

        r1 = raw.resistances[0] if len(raw.resistances) > 0 else None
        r2 = raw.resistances[1] if len(raw.resistances) > 1 else None

        dist_s = self._dist_to_support_pct(raw.current_price, s1)
        dist_r = self._dist_to_resistance_pct(raw.current_price, r1)
        nearer = self._pick_nearer(dist_s, dist_r)

        lines: list[str] = []

        lines.append("\n<b>Ближайшие уровни</b> (1H)")

        lines.append(f"🟢 Поддержка: {self._fmt_one(s1) if s1 is not None else '—'}")
        lines.append(f"🔴 Сопротивление: {self._fmt_one(r1) if r1 is not None else '—'}")

        dist_parts: list[str] = []
        if dist_s is not None:
            dist_parts.append(f"до поддержки ~{dist_s:.2f}%")
        if dist_r is not None:
            dist_parts.append(f"до сопротивления ~{dist_r:.2f}%")
        if dist_parts:
            lines.append(f"📏 Дистанция: {', '.join(dist_parts)}")

        if nearer is not None:
            lines.append(
                f"🎯 Ближе сейчас: {'поддержка' if nearer == 'support' else 'сопротивление'}"
            )

        lines.append("")

        lines.append("<b>Сценарии</b>")

        # up
        if r1 is not None:
            r2_text = self._fmt_one(r2) if r2 is not None else "зоне выше по графику"
            tpl = random.choice(UP_TEMPLATES)
            lines.append(tpl.format(r1=self._fmt_one(r1), r2=r2_text))

        lines.append("")

        # down
        if s1 is not None:
            s2_text = self._fmt_one(s2) if s2 is not None else "зоне ниже по графику"
            tpl = random.choice(DOWN_TEMPLATES)
            lines.append(tpl.format(s1=self._fmt_one(s1), s2=s2_text))

        return "\n".join(lines).rstrip() + "\n"

    def _fmt_one(self, v: float) -> str:
        return format_price(v)

    def _dist_to_support_pct(self, price: float, support: float | None) -> float | None:
        if support is None:
            return None
        dist = max(0.0, price - support)
        return (dist / price) * 100.0

    def _dist_to_resistance_pct(self, price: float, resistance: float | None) -> float | None:
        if resistance is None:
            return None
        dist = max(0.0, resistance - price)
        return (dist / price) * 100.0

    def _pick_nearer(self, dist_s: float | None, dist_r: float | None) -> str | None:
        if dist_s is None and dist_r is None:
            return None
        if dist_s is None:
            return "resistance"
        if dist_r is None:
            return "support"
        return "support" if dist_s <= dist_r else "resistance"
