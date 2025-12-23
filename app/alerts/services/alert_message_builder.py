import logging

from app.market.models import Timeframe

logger = logging.getLogger(__name__)


class AlertMessageBuilder:
    def __init__(
        self,
        price_hit_formatter,
        levels_formatter,
        candle_service,
        levels_workflow,
        llm_service=None
    ) -> None:
        self._base_fmt = price_hit_formatter
        self._levels_fmt = levels_formatter
        self._candles = candle_service
        self._levels = levels_workflow
        self._llm = llm_service

    async def build_price_hit_message(self, alert, current_price: float) -> str:
        text = self._base_fmt.format(
            symbol=alert.symbol,
            target_price=alert.target_price,
            current_price=current_price,
            direction=alert.direction,
        )

        try:
            candles = await self._candles.get_for_levels(
                symbol=alert.symbol,
                timeframe=Timeframe.D1,
            )

            logger.info(
                "levels.input symbol=%s tf=%s candles=%d first=%s last=%s",
                alert.symbol,
                Timeframe.D1,
                len(candles),
                candles[0].open_time if candles else None,
                candles[-1].open_time if candles else None,
            )
            levels = self._levels.get_levels_for_price(candles, current_price)
            text += self._levels_fmt.format(levels)
        except Exception:
            logger.exception("Failed to append levels for alert=%s", getattr(alert, "id", None))

        if self._llm is not None:
            text = await self._llm.explain_alert(text)

        return text
