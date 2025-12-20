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
            verb = "пробил уровень"
        elif direction == "down":
            verb = "упал ниже уровня"
        else:
            verb = "достиг твоего уровня"

        return (
            f"{symbol} {verb} уровень {target_price:,.2f}\n" f"Текущая цена: {current_price:,.2f}"
        )
