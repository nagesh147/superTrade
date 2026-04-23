from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import uuid

from app.core.enums import Direction, SetupStatus, SetupType
from app.schemas.directional import DirectionalSignal, SetupEvent


@dataclass(slots=True)
class SetupConfig:
    setup_valid_bars: int = 3
    bar_minutes: int = 60
    early_score_threshold: float = 60.0
    confirmed_score_threshold: float = 70.0


class SetupEngine:
    def __init__(self, config: SetupConfig | None = None) -> None:
        self.config = config or SetupConfig()

    def create_or_update(self, signal: DirectionalSignal) -> SetupEvent | None:
        if signal.direction_state == Direction.NEUTRAL:
            return None
        if signal.direction_state == Direction.BULLISH:
            score = signal.score_long
            confirmed = signal.green_arrow and signal.alignment_strength == 3
        else:
            score = signal.score_short
            confirmed = signal.red_arrow and signal.alignment_strength == 3
        if confirmed and score >= self.config.confirmed_score_threshold:
            setup_type = SetupType.CONFIRMED
        elif score >= self.config.early_score_threshold:
            setup_type = SetupType.EARLY
        else:
            return None
        expires_at = signal.ts + timedelta(minutes=self.config.bar_minutes * self.config.setup_valid_bars)
        return SetupEvent(
            setup_id=str(uuid.uuid4()),
            setup_type=setup_type,
            direction=signal.direction_state,
            activated_at=signal.ts,
            expires_at=expires_at,
            bars_remaining=self.config.setup_valid_bars,
            status=SetupStatus.ACTIVE,
            signal=signal,
        )

    def decrement_window(self, setup: SetupEvent, latest_ts) -> SetupEvent:
        bars_elapsed = max(0, int((latest_ts - setup.activated_at).total_seconds() // (self.config.bar_minutes * 60)))
        remaining = max(0, self.config.setup_valid_bars - bars_elapsed)
        setup.bars_remaining = remaining
        if remaining == 0 and setup.status == SetupStatus.ACTIVE:
            setup.status = SetupStatus.EXPIRED
        return setup
