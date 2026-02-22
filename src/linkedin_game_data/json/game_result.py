from dataclasses import dataclass


@dataclass
class GameResult:
    game: str | None = None
    round: str | None = None
    play_time: str | None = None
    avg_time: str | None = None
