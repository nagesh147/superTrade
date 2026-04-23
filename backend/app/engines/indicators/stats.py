from __future__ import annotations

from typing import Iterable


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def signed_unit(value: float, scale: float) -> float:
    if scale == 0:
        return 0.0
    x = value / scale
    return max(-1.0, min(1.0, x))


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0
