import glob
import json
import logging
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from linkedin_game_data.json import parse_game_result

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s",
)


def main() -> None:
    pattern = "build/ocr/data/photos/*/response.json"
    files = glob.glob(pattern)

    if not files:
        print(f"No files found matching pattern: {pattern}")
        return

    records = []
    failures: dict[str, int] = {
        "game": 0,
        "round": 0,
        "play_time": 0,
        "avg_time": 0,
    }

    for filepath in files:
        with open(filepath) as f:
            data = json.load(f)

        content = data.get("message", {}).get("content", "")
        if not content:
            print(f"WARNING: No message.content in {filepath}")
            continue

        lines = content.split("\n")
        result = parse_game_result(lines)

        records.append({
            "source_file": filepath,
            "game": result.game,
            "round": result.round,
            "play_time": result.play_time,
            "avg_time": result.avg_time,
        })

        if result.game is None:
            failures["game"] += 1
        if result.round is None:
            failures["round"] += 1
        if result.play_time is None:
            failures["play_time"] += 1
        if result.avg_time is None:
            failures["avg_time"] += 1

    df = pl.DataFrame(records)
    output_path = "build/table/game_results.csv"
    df.write_csv(output_path)

    print(f"\nProcessed {len(files)} files")
    print(f"Wrote {len(df)} records to {output_path}")
    print("Failures per field:")
    for field, count in failures.items():
        print(f"  {field}: {count}")


if __name__ == "__main__":
    main()
