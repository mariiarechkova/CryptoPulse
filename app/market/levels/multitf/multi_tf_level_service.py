from dataclasses import dataclass

from app.market.levels.atr_calculator import ATRCalculator
from app.market.levels.multitf.merger import merge_levels_to_zones
from app.market.levels.multitf.zones import LevelPoint, MergedZone
from app.market.models import Candle, Timeframe
from app.market.services.candle_service import CandleService
from app.workflows.levels_workflow import LevelsWorkflow


@dataclass(frozen=True, slots=True)
class MultiTFLevelsContext:
    symbol: str
    current_price: float
    merge_tol: float
    supports: list[MergedZone]
    resistances: list[MergedZone]
    nearest_support: MergedZone | None
    nearest_resistance: MergedZone | None


class MultiTFLevelsService:
    def __init__(
        self,
        *,
        candle_service: CandleService,
        workflows_by_tf: dict[Timeframe, LevelsWorkflow],
        atr_calculator: ATRCalculator,
    ) -> None:
        self._candles = candle_service
        self._wf_by_tf = workflows_by_tf
        self._atr = atr_calculator

    async def build_context(self, *, symbol: str, current_price: float) -> MultiTFLevelsContext:
        candles_by_tf = {
            Timeframe.H1: await self._candles.get_for_levels(symbol=symbol, timeframe=Timeframe.H1),
            Timeframe.H4: await self._candles.get_for_levels(symbol=symbol, timeframe=Timeframe.H4),
            Timeframe.D1: await self._candles.get_for_levels(symbol=symbol, timeframe=Timeframe.D1),
        }

        merge_tol = self._calc_merge_tol(
            candles_h1=candles_by_tf[Timeframe.H1],
            current_price=current_price,
        )

        points: list[LevelPoint] = []

        for tf, candles in candles_by_tf.items():
            wf = self._wf_by_tf[tf]
            levels = wf.get_levels_for_price(candles, current_price)

            for lvl in levels.get("supports", []):
                points.append(_to_point(tf=tf, kind="support", lvl=lvl))

            for lvl in levels.get("resistances", []):
                points.append(_to_point(tf=tf, kind="resistance", lvl=lvl))

        zones = merge_levels_to_zones(points=points, merge_tol=merge_tol)

        supports = [z for z in zones if z.kind == "support"]
        resistances = [z for z in zones if z.kind == "resistance"]

        nearest_support = _pick_nearest_support(supports, current_price)
        nearest_resistance = _pick_nearest_resistance(resistances, current_price)

        return MultiTFLevelsContext(
            symbol=symbol,
            current_price=current_price,
            merge_tol=merge_tol,
            supports=supports,
            resistances=resistances,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
        )

    def _calc_merge_tol(self, *, candles_h1: list[Candle], current_price: float) -> float:
        floor_tol = current_price * 0.003
        cap_tol = current_price * 0.01

        try:
            atr = self._atr.calculate(candles_h1, period=14)
        except ValueError:
            return floor_tol

        atr_based = atr * 0.8
        return max(floor_tol, min(atr_based, cap_tol))


def _to_point(*, tf: Timeframe, kind: str, lvl: dict) -> LevelPoint:
    return LevelPoint(
        tf=tf,
        kind=kind,
        min_price=float(lvl["min_price"]),
        max_price=float(lvl["max_price"]),
        avg_price=float(lvl["avg_price"]),
        touches=int(lvl.get("touches", 0)),
    )


def _pick_nearest_support(zones: list[MergedZone], price: float) -> MergedZone | None:
    candidates = [z for z in zones if z.avg_price < price]
    if not candidates:
        return None
    return min(candidates, key=lambda z: abs(price - z.avg_price))


def _pick_nearest_resistance(zones: list[MergedZone], price: float) -> MergedZone | None:
    candidates = [z for z in zones if z.avg_price > price]
    if not candidates:
        return None
    return min(candidates, key=lambda z: abs(price - z.avg_price))
