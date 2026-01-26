import logging

logger = logging.getLogger(__name__)


class AlertMessageBuilder:
    def __init__(
        self,
        price_hit_formatter,
        h1_levels_formatter,
        h1_levels_service,
        llm_service=None,
    ) -> None:
        self._base_fmt = price_hit_formatter
        self._h1_fmt = h1_levels_formatter
        self._h1 = h1_levels_service
        self._llm = llm_service

    async def build_price_hit_message(self, alert, current_price: float) -> str:
        text = self._base_fmt.format(
            symbol=alert.symbol,
            target_price=alert.target_price,
            current_price=current_price,
            direction=alert.direction,
        )

        try:
            ctx = await self._h1.get_raw(symbol=alert.symbol, current_price=current_price)
            text += self._h1_fmt.format(ctx)
        except Exception:
            logger.exception(
                "Failed to append multi-tf levels for alert=%s", getattr(alert, "id", None)
            )

        # if self._llm is not None:
        #     try:
        #         comment = await self._llm.explain_alert(text)
        #         if comment:
        #             text += "\n" + comment.strip() + "\n"
        #     except Exception:
        #         logger.exception("Failed to build LLM comment for alert=%s", getattr(alert, "id", None))

        return text
