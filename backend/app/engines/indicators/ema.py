from __future__ import annotations

from typing import Iterable, List


def ema(values: Iterable[float], period: int) -> List[float]:
    values = list(values)
    if not values:
        return []
    if period <= 0:
        raise ValueError("period must be > 0")
    alpha = 2.0 / (period + 1.0)
    out = [values[0]]
    for v in values[1:]:
        out.append(alpha * v + (1.0 - alpha) * out[-1])
    return out
