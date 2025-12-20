class LevelClusterer:
    def build_levels(self, pivot_prices, tolerance: float, min_touches: int = 2):
        if tolerance <= 0:
            raise ValueError("tolerance must be > 0")
        if not pivot_prices:
            return []

        prices = sorted(pivot_prices)

        clusters = []
        current = [prices[0]]

        for price in prices[1:]:
            if abs(price - current[-1]) <= tolerance:
                current.append(price)
            else:
                clusters.append(current)
                current = [price]
        clusters.append(current)

        levels = []
        for cluster in clusters:
            if len(cluster) < min_touches:
                continue
            levels.append(
                {
                    "min_price": min(cluster),
                    "max_price": max(cluster),
                    "avg_price": sum(cluster) / len(cluster),
                    "touches": len(cluster),
                }
            )

        levels.sort(key=lambda x: x["touches"], reverse=True)
        return levels
