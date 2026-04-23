from __future__ import annotations

from dataclasses import dataclass

from app.engines.indicators.stats import clamp


@dataclass(slots=True)
class ScoreBundle:
    macro: float
    signal_long: float
    signal_short: float
    pullback: float
    continuation: float


def macro_regime_score(f1: float, f2: float, f3: float, f4: float, f5: float) -> float:
    return 30 * f1 + 20 * f2 + 15 * f3 + 20 * f4 + 15 * f5


def directional_signal_score(g1: float, g2: float, g3: float, g4: float, g5: float, bullish: bool) -> float:
    polarity = max(g4, 0.0) if bullish else max(-g4, 0.0)
    return 30 * g1 + 20 * g2 + 15 * g3 + 20 * polarity + 15 * g5


def pullback_score(p1: float, p2: float, p3: float, p4: float, p5: float) -> float:
    return 30 * p1 + 25 * p2 + 15 * p3 + 15 * p4 + 15 * (1.0 - p5)


def continuation_score(c1: float, c2: float, c3: float, c4: float, c5: float) -> float:
    return 25 * c1 + 20 * c2 + 20 * c3 + 20 * (1.0 - c4) + 15 * c5


def normalize_spread_pct(spread_pct: float, good: float = 0.01, bad: float = 0.04) -> float:
    if spread_pct <= good:
        return 1.0
    if spread_pct >= bad:
        return 0.0
    return 1.0 - (spread_pct - good) / (bad - good)


def normalize_ratio(value: float, good: float, bad: float) -> float:
    if value <= good:
        return 1.0
    if value >= bad:
        return 0.0
    return 1.0 - (value - good) / (bad - good)


def normalize_positive(value: float, good: float) -> float:
    if good <= 0:
        return 0.0
    return clamp(value / good)
