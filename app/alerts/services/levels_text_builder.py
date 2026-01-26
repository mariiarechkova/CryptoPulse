import logging

from app.market.models import Timeframe
from app.workflows.levels_workflow import LevelsWorkflow

logger = logging.getLogger(__name__)


class LevelsBuildError(Exception):
    pass


class LevelsTextBuilder:
    def __init__(
        self,
        *,
        market_data_workflow,
        workflows_by_tf: dict[Timeframe, LevelsWorkflow],
        levels_formatter,
    ) -> None:
        self._market = market_data_workflow
        self._wf_by_tf = workflows_by_tf
        self._fmt = levels_formatter

    async def build_for_symbol(self, *, symbol: str, timeframe: Timeframe) -> str:
        candles = await self._market.get_candles_for_levels(symbol=symbol, timeframe=timeframe)

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
            timeframe,
            len(candles),
            current_price,
        )

        wf = self._wf_by_tf.get(timeframe)
        if wf is None:
            raise LevelsBuildError("UNSUPPORTED_TIMEFRAME")

        levels = wf.get_levels_for_price(candles, current_price, 3)
        return self._fmt.format(symbol, timeframe.value, levels)
