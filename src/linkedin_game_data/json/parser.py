import logging
import re

from fuzzysearch import find_near_matches

from .game_names import VALID_GAMES
from .game_result import GameResult

logger = logging.getLogger(__name__)

GAME_ROUND_PATTERN = re.compile(r"([A-Za-z]+(?:\s+\w+)?)\s*#(\d+)")
AVG_TIME_PATTERN = re.compile(r"avg\.?\s*:?\s*(\d+:\d{2})")
TIME_PATTERN = re.compile(r"^(\d{1,2}:\d{2})$")

MAX_FUZZY_DIST = 1


def _fuzzy_match_game(ocr_text: str) -> str | None:
    """
    Try to match a valid game name within the OCR'd text.
    Uses fuzzy search to find game names even with OCR errors.
    """
    for game_name in VALID_GAMES:
        matches = find_near_matches(game_name, ocr_text, max_l_dist=MAX_FUZZY_DIST)
        if matches:
            return game_name
    return None


def parse_game_result(lines: list[str]) -> GameResult:
    result = GameResult()

    game_round_line_idx = -1

    for i, line in enumerate(lines):
        game_match = GAME_ROUND_PATTERN.search(line)
        if game_match:
            ocr_name = game_match.group(1)
            matched_name = _fuzzy_match_game(line)
            if matched_name:
                result.game = matched_name
                result.round = game_match.group(2)
                game_round_line_idx = i
                break
            else:
                logger.warning(
                    f"Found game name '{ocr_name}' but fuzzy match failed (max_l_dist={MAX_FUZZY_DIST})"
                )

    if game_round_line_idx == -1:
        logger.warning("No game name found in any line")

    avg_time_line_idx = -1
    avg_match = AVG_TIME_PATTERN.search("\n".join(lines))
    if avg_match:
        result.avg_time = avg_match.group(1)
        line_start = 0
        for i, line in enumerate(lines):
            line_end = line_start + len(line) + 1
            if line_start <= avg_match.start() < line_end:
                avg_time_line_idx = i
                break
            line_start = line_end
    else:
        logger.warning("No average time found (this may be normal for some screens)")

    standalone_times = []
    for i, line in enumerate(lines):
        if i == avg_time_line_idx:
            continue
        line_clean = line.strip()
        if TIME_PATTERN.match(line_clean):
            standalone_times.append((i, line_clean))

    if not standalone_times:
        logger.warning("No play time found")
        return result

    if len(standalone_times) > 1:
        logger.warning(
            f"Multiple potential play times found: {[t[1] for t in standalone_times]}"
        )

    if standalone_times:
        result.play_time = standalone_times[0][1]

    return result
