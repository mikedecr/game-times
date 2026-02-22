import json
import re
from pathlib import Path
from typing import Iterable

from fuzzysearch import find_near_matches

from ...game_name import GameName
from ...utils import only

game_patterns = {k.value for k in GameName}


def fuzzy_find_game(lines: list[str], game_names: Iterable[str]) -> str | None:
    """
    Search through a list of text lines for one of `game_names`.
    Filter the lines by:
    - regex match for the ONE line containing a # glyph pattern
    - fuzzy matching the text in that line to a game name
    """
    pattern = re.compile(r".*[A-z] #[0-9]+.*")
    value = [line for line in lines if pattern.match(line)]
    if len(value) > 1:
        raise ValueError("non-unique matches in", value)
    if len(value) == 0:
        print("no matches in", file)
        return
    value = only(value)
    for name in game_patterns:
        if m := find_near_matches(name, value, max_l_dist=1):
            return only(m).matched
    print("couldn't fuzzy match name in", value)


if __name__ == "__main__":
    top_path = Path("build/ocr/data/photos")
    files = sorted(list(top_path.glob("**/response.json")))

    from .overrides import game_name_overrides

    results = {}
    for file in files:
        data = json.load(file.open())
        text = data.get("message", {}).get("content", "")
        lines = list(filter(len, text.splitlines()))
        if not lines:
            raise ValueError
        name = fuzzy_find_game(lines, game_patterns)
        if not name:
            imgname = file.parent.name
            name = game_name_overrides.get(imgname)
            if not name:
                print("not found", file)
                continue
            print("override for", file, name)
        results[file] = name

    assert all(f in results for f in files)
