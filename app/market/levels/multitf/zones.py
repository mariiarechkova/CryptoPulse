from dataclasses import dataclass

from app.market.models import Timeframe


@dataclass(frozen=True, slots=True)
class LevelPoint:
    tf: Timeframe
    kind: str  # "support" | "resistance"
    min_price: float
    max_price: float
    avg_price: float
    touches: int


@dataclass(frozen=True, slots=True)
class MergedZone:
    kind: str  # "support" | "resistance"
    min_price: float
    max_price: float
    avg_price: float
    touches_total: int
    tfs: tuple[Timeframe, ...]
    score: float
