from dataclasses import dataclass

import pytest

from app.market.levels.atr_calculator import ATRCalculator


@dataclass(frozen=True)
class Candle:
    high: float
    low: float
    close: float


@pytest.fixture
def candles_14_flat_range():
    candles = []
    close = 100.0

    for _ in range(14):
        low = close - 1.0
        high = close + 1.0
        candles.append(Candle(high=high, low=low, close=close))
        close += 0.1

    return candles


def test_atr_calculates_correct_value(candles_14_flat_range):
    atr = ATRCalculator().calculate(candles_14_flat_range)
    assert atr == pytest.approx(2.0)


def test_atr_raises_error_if_not_enough_candles():
    candles = [Candle(high=101, low=99, close=100) for _ in range(13)]
    with pytest.raises(ValueError):
        ATRCalculator().calculate(candles)
