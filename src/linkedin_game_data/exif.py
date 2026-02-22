from pathlib import Path
from typing import Iterable

import exiftool


def dir_exif_data(image_paths: Iterable[Path]) -> dict[str, str]:
    """
    Dict of {filename: datetimeOriginal} using the exif data from a list of images
    """
    with exiftool.ExifToolHelper() as et:
        metadata: list[dict[str, str]] = et.get_metadata(image_paths)
    return {
        data["SourceFile"]: data.get("EXIF:DateTimeOriginal", None) for data in metadata
    }
