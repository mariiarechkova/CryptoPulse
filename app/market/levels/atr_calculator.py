class ATRCalculator:
    def calculate(self, candles) -> float:
        if len(candles) < 14:
            raise ValueError("Need at least 14 candles to calculate ATR")

        trs = []
        prev_close = candles[0].close

        for c in candles[1:]:
            tr = max(
                c.high - c.low,
                abs(c.high - prev_close),
                abs(c.low - prev_close),
            )
            trs.append(tr)
            prev_close = c.close

        return sum(trs) / len(trs)
