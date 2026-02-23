from pathlib import Path
from typing import Annotated

import exiftool
import polars as pl
from typer import Option

from .app import app


@app.command()
def exif(
    read_dir: Annotated[Path, Option("-p", "--path", help="Source directory")],
    output_dir: Annotated[Path, Option("-o", "--output", help="Output directory")],
):
    """help text"""
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(read_dir.iterdir())
    df = pl.from_dicts(metadata)
    output_dir.mkdir(parents=True, exist_ok=True)
    df.write_csv(output_dir / "exif.csv")
    print(f"Wrote {output_dir / 'exif.csv'}")
