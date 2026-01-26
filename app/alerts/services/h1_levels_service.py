from dataclasses import dataclass

from app.market.models import Timeframe


@dataclass(frozen=True, slots=True)
class H1LevelsRaw:
    symbol: str
    current_price: float
    supports: list[float]
    resistances: list[float]


class H1LevelsService:
    TOP_N = 2

    def __init__(self, *, market_data_workflow, levels_workflow) -> None:
        self._market = market_data_workflow
        self._levels = levels_workflow

    async def get_raw(self, *, symbol: str, current_price: float) -> H1LevelsRaw:
        if current_price <= 0:
            raise ValueError("BAD_CURRENT_PRICE")

        candles = await self._market.get_candles_for_levels(symbol=symbol, timeframe=Timeframe.H1)
        if not candles:
            raise RuntimeError("NO_CANDLES")

        levels = self._levels.get_levels_for_price(candles, current_price, self.TOP_N)

        supports_raw = levels.get("supports") or []
        resistances_raw = levels.get("resistances") or []

        supports = [float(lvl["avg_price"]) for lvl in supports_raw]
        resistances = [float(lvl["avg_price"]) for lvl in resistances_raw]

        return H1LevelsRaw(
            symbol=symbol,
            current_price=current_price,
            supports=supports,
            resistances=resistances,
        )
