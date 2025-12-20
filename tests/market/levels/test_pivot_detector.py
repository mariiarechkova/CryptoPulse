from dataclasses import dataclass

from app.market.levels.pivot_detector import PivotDetector


@dataclass(frozen=True)
class Candle:
    high: float
    low: float
    close: float


def test_pivot_high():
    candles = [
        Candle(high=10, low=1, close=5),
        Candle(high=20, low=2, close=10),  # pivot high
        Candle(high=11, low=1, close=6),
    ]

    pivots = PivotDetector().find_pivots(candles, left=1, right=1)

    assert pivots == [20]


def test_pivot_low():
    candles = [
        Candle(high=12, low=5, close=7),
        Candle(high=11, low=1, close=6),  # pivot low only
        Candle(high=12, low=4, close=7),
    ]

    pivots = PivotDetector().find_pivots(candles, left=1, right=1)

    assert pivots == [1]
