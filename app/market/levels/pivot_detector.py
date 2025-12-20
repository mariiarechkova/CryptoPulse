class PivotDetector:
    def find_pivots(self, candles, left: int = 2, right: int = 2):
        n = len(candles)
        if n < left + right + 1:
            return []

        pivots = []

        for i in range(left, n - right):
            center = candles[i]
            window = candles[i - left : i] + candles[i + 1 : i + 1 + right]

            if all(c.high < center.high for c in window):
                pivots.append(center.high)

            if all(c.low > center.low for c in window):
                pivots.append(center.low)

        return pivots
