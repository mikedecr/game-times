#!/usr/bin/env python3
"""Compare two game_results CSV files to check parsing improvements."""

import csv
import sys


def read_csv(path):
    with open(path) as f:
        return {(row["game"], row["round"], row["play_time"]): row["avg_time"] for row in csv.DictReader(f)}


def main(before_path, after_path):
    before = read_csv(before_path)
    after = read_csv(after_path)

    common_keys = before.keys() & after.keys()

    diffs = []
    for key in common_keys:
        if before[key] != after[key]:
            diffs.append((key, before[key], after[key]))

    print(f"Total records before: {len(before)}")
    print(f"Total records after: {len(after)}")
    print(f"Common keys: {len(common_keys)}")
    print(f"Changed avg_time values: {len(diffs)}")

    if diffs:
        print("\nChanges:")
        for key, b, a in diffs:
            print(f"  {key}: '{b}' -> '{a}'")
    else:
        print("\nNo changes to previously parsed avg_time values - golden test PASSED")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <before.csv> <after.csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
