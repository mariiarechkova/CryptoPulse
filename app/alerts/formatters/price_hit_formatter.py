class PriceHitFormatter:
    def format(
        self,
        *,
        symbol: str,
        target_price: float,
        current_price: float,
        direction: str | None,
    ) -> str:
        if direction == "up":
            verb = "поднялся выше ценового уровня алерта"
        elif direction == "down":
            verb = "опустился ниже ценового уровня алерта"
        else:
            verb = "достиг ценового уровня алерта"

        return (
            f"{symbol} {verb} {target_price:,.2f}\n"
            f"Текущая цена: {current_price:,.2f}"
        )
