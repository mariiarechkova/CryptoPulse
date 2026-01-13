import logging

from app.market.models import Timeframe

logger = logging.getLogger(__name__)

class LevelsBuildError(Exception):
    pass

class LevelsTextBuilder:
    def __init__(
        self,
        *,
        market_data_workflow,
        levels_workflow,
        levels_formatter,
    ) -> None:
        self._market = market_data_workflow
        self._levels = levels_workflow
        self._fmt = levels_formatter

    async def build_for_symbol(self, *, symbol: str) -> str:
        candles = await self._market.get_or_load_candles_for_levels(
            symbol=symbol,
            timeframe=Timeframe.D1,
        )

        if not candles:
            logger.warning("levels.no_candles symbol=%s", symbol)
            raise LevelsBuildError("NO_CANDLES")


        last_close = getattr(candles[-1], "close", None)
        if last_close is None:
            logger.error("levels.no_last_close symbol=%s candle=%s", symbol)
            raise LevelsBuildError("NO_LAST_CLOSE")

        current_price = float(last_close)

        logger.info(
            "levels.button_input symbol=%s tf=%s candles=%d last_close=%s",
            symbol,
            Timeframe.D1,
            len(candles),
            current_price,
        )

        levels = self._levels.get_levels_for_price(candles, current_price)
        return self._fmt.format(levels)