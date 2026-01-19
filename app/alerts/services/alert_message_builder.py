import logging

logger = logging.getLogger(__name__)


class AlertMessageBuilder:
    def __init__(
        self,
        price_hit_formatter,
        multi_tf_levels_formatter,
        multi_tf_levels_service,
        llm_service=None,
    ) -> None:
        self._base_fmt = price_hit_formatter
        self._mtf_fmt = multi_tf_levels_formatter
        self._multi_tf = multi_tf_levels_service
        self._llm = llm_service

    async def build_price_hit_message(self, alert, current_price: float) -> str:
        text = self._base_fmt.format(
            symbol=alert.symbol,
            target_price=alert.target_price,
            current_price=current_price,
            direction=alert.direction,
        )

        try:
            ctx = await self._multi_tf.build_context(
                symbol=alert.symbol,
                current_price=current_price,
            )
            text += self._mtf_fmt.format(ctx)
        except Exception:
            logger.exception(
                "Failed to append multi-tf levels for alert=%s", getattr(alert, "id", None)
            )

        # if self._llm is not None:
        #     text = await self._llm.explain_alert(text)

        return text
