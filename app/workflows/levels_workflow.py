import logging
from dataclasses import dataclass

from app.market.levels.atr_calculator import ATRCalculator
from app.market.levels.level_classifier import LevelClassifier
from app.market.levels.level_clusterer import LevelClusterer
from app.market.levels.pivot_detector import PivotDetector
from app.market.models import Candle

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class LevelsWorkflowConfig:
    atr_mult: float = 0.5
    left: int = 2
    right: int = 2
    min_touches: int = 2
    min_candles_for_atr: int = 14
    top_n: int = 3


class LevelsWorkflow:
    def __init__(
        self,
        atr_calculator: ATRCalculator,
        pivot_detector: PivotDetector,
        level_clusterer: LevelClusterer,
        level_classifier: LevelClassifier,
        config: LevelsWorkflowConfig | None = None,
    ) -> None:
        self._atr = atr_calculator
        self._pivots = pivot_detector
        self._clusterer = level_clusterer
        self._classifier = level_classifier
        self._cfg = config or LevelsWorkflowConfig()

    def get_levels_for_price(self, candles: list[Candle], current_price: float) -> dict[str, list]:
        result: dict[str, list] = {"supports": [], "resistances": []}

        logger.info("levels: candles=%d", len(candles))
        logger.debug("levels: start candles=%d price=%s", len(candles), current_price)

        if len(candles) < self._cfg.min_candles_for_atr:
            logger.debug(
                "levels.skip_not_enough_candles candles=%s min=%s",
                len(candles),
                self._cfg.min_candles_for_atr,
            )
            return result

        atr = self._atr.calculate(candles)
        tolerance = atr * self._cfg.atr_mult
        price_cap = current_price * 0.01  # 1% price

        tolerance = min(tolerance, price_cap)

        logger.debug("levels: atr=%s tolerance=%s", atr, tolerance)

        pivot_prices = self._pivots.find_pivots(candles, left=self._cfg.left, right=self._cfg.right)
        logger.info("levels: pivots=%d sample=%s", len(pivot_prices), pivot_prices[:5])
        logger.debug(
            "levels: pivots=%d left=%d right=%d", len(pivot_prices), self._cfg.left, self._cfg.right
        )
        if not pivot_prices:
            logger.debug(
                "levels.no_pivots candles=%s left=%s right=%s",
                len(candles),
                self._cfg.left,
                self._cfg.right,
            )
            return result

        levels = self._clusterer.build_levels(
            pivot_prices,
            tolerance=tolerance,
            min_touches=self._cfg.min_touches,
        )
        logger.info("levels: clusters=%d sample=%s", len(levels), levels[:3])
        logger.debug("levels: clusters=%d min_touches=%d", len(levels), self._cfg.min_touches)

        if not levels:
            logger.debug(
                "levels.no_levels pivots=%s tolerance=%s min_touches=%s",
                len(pivot_prices),
                tolerance,
                self._cfg.min_touches,
            )
            return result

        classified = self._classifier.classify(levels, current_price)
        logger.info(
            "levels: classified supports=%d resistances=%d",
            len(classified["supports"]),
            len(classified["resistances"]),
        )

        n = self._cfg.top_n
        result["supports"] = classified["supports"][:n]
        result["resistances"] = classified["resistances"][:n]

        logger.debug(
            "levels: done supports=%d resistances=%d",
            len(result["supports"]),
            len(result["resistances"]),
        )
        return result
