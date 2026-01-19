class ATRCalculator:
    def calculate(self, candles, period: int = 14) -> float:
        if period <= 0:
            raise ValueError("ATR period must be > 0")

        if len(candles) < period + 1:
            raise ValueError(
                f"Need at least {period + 1} candles to calculate ATR(period={period})"
            )

        trs: list[float] = []
        prev_close = candles[0].close

        for c in candles[1:]:
            tr = max(
                c.high - c.low,
                abs(c.high - prev_close),
                abs(c.low - prev_close),
            )
            trs.append(tr)
            prev_close = c.close

        window = trs[-period:]
        return sum(window) / period
