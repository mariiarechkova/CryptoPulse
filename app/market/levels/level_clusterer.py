class LevelClusterer:
    def build_levels(self, pivot_prices, tolerance: float, min_touches: int = 2):
        if tolerance <= 0:
            raise ValueError("tolerance must be > 0")
        if not pivot_prices:
            return []

        prices = sorted(pivot_prices)

        clusters: list[list[float]] = []
        current: list[float] = [prices[0]]
        current_sum = prices[0]

        for price in prices[1:]:
            center = current_sum / len(current)

            if abs(price - center) <= tolerance:
                current.append(price)
                current_sum += price
            else:
                clusters.append(current)
                current = [price]
                current_sum = price

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
