"""
Process response json from glm-ocr output iles
"""

import datetime
import json
import logging
import re
from enum import Enum
from functools import cached_property
from pathlib import Path

from PIL import Image

from .xmp import get_rdf_datetime

log = logging.getLogger(__name__)


__all__ = ["ResponseData", "LinkedInGame", "ExcludedGame"]


# maybe some other module...
class LinkedInGame(Enum):
    Queens = 1
    Tango = 2


class ExcludedGame(Enum):
    Pinpoint = 1
    Crossclimb = 2
    Zip = 3


class ResponseData:
    data: dict[str, str | dict]
    file_path: Path

    @classmethod
    def from_file(cls, path: Path | str):
        self = cls()
        with open(path, "r") as f:
            self.file_path = Path(path).resolve()
            self.data = json.load(f)
        return self

    @cached_property
    def image(self) -> Image.Image:
        for parent in self.file_path.parents:
            if parent.name == "data":
                source_path = self.file_path.relative_to(parent).parent
                break
        file = Path("data") / source_path
        for file in file.parent.iterdir():
            if file.stem == source_path.stem:
                img = Image.open(file)
                return img

    @cached_property
    def datetime(self) -> datetime.datetime:
        return get_rdf_datetime(self.image)

    @cached_property
    def text(self) -> str:
        return self.data["message"]["content"]

    @cached_property
    def lines(self) -> list[str]:
        lines = []
        for line in self.text.split("\n"):
            stripped = line.strip()
            if stripped:
                lines.append(stripped)
        return lines

    @cached_property
    def game(self) -> LinkedInGame | None:
        for line in self.lines:
            for game in ExcludedGame:
                if game.name.lower() in line.lower():
                    log.error("Excluding game %s", game)
                    return
            for game in LinkedInGame:
                if game.name.lower() in line.lower():
                    return game
        log.warning("No game found in %s", self.lines)

    @cached_property
    def game_number(self) -> int | None:
        if not (game := self.game):
            return
        name = game.name
        pattern = re.compile(rf"\s*{name}\s+#\d+")
        for line in self.lines:
            if name.lower() not in line.lower():
                continue
            match = pattern.search(line)
            if not match:
                continue
            return int(match.group(0).split("#")[1])

    @cached_property
    def game_time(self) -> str:
        # copy for mutation
        lines = self.lines.copy()
        # drop first line, this is going to be the time-of-day from the phone
        lines.pop(0)
        # looking for a (X)X:YY time pattern, not matching "avg: (X)X:YY"
        pattern = re.compile(r"(\d+):(\d+)")
        for line in lines:
            if "avg" in line.lower():
                log.warning("skipping avg time line %s", line)
                continue
            match = pattern.search(line)
            if not match:
                continue
            # early return bc. some later lines may show us "best score" and stuff
            return f"{match.group(1)}:{match.group(2)}"

    @cached_property
    def avg_time(self) -> str:
        pattern = re.compile(r".*Today's avg: (\d+):(\d+)\s*.*")
        for line in self.lines:
            match = pattern.search(line)
            if not match:
                continue
            return f"{match.group(1)}:{match.group(2)}"

    @cached_property
    def record(self) -> dict[str, str]:
        record: dict[str, str] = {"image_name": self.file_path.parent.name}
        for attr in ("game", "game_number", "game_time", "avg_time", "datetime"):
            value = getattr(self, attr)
            if not value:
                continue
            if isinstance(value, Enum):
                value = value.name
            record[attr] = str(value)
        return record


if __name__ == "__main__":
    import polars as pl

    directory = Path("build/ocr/data/photos")
    files = list(f for d in directory.iterdir() for f in d.glob("*.json"))

    records = []
    for file in files:
        rd = ResponseData.from_file(file)
        records.append(rd.record)

    df = pl.DataFrame(records)

    write_file = Path("build/sheet/rough.csv")
    write_file.parent.mkdir(parents=True, exist_ok=True)
    df.write_csv(write_file)
    breakpoint()
