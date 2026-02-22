from pathlib import Path
from typing import Annotated

import typer
from ollama import ChatResponse, chat
from tqdm import tqdm

MODEL = "glm-ocr"


app = typer.Typer(name="ocr", invoke_without_command=False)


def llm_read_text(image_path: Path) -> ChatResponse:
    """Read text from an image using OCR model"""
    msg = {"role": "user", "images": [image_path]}
    return chat(model=MODEL, messages=[msg])


@app.command()
def ocr(
    path: Annotated[
        str,
        typer.Option("-p", "--path", help="Source directory"),
    ],
    force: Annotated[
        bool,
        typer.Option("-f", "--force", help="Force overwrite existing files"),
    ] = False,
):
    """help text"""
    if Path(path).is_dir():
        files = Path(path).iterdir()
    elif Path(path).is_file():
        files = [Path(path)]
    else:
        raise ValueError(f"Invalid path: {path}")
    for file in tqdm(sorted(list(files))):
        if not file.suffix.lower() == ".png":
            print(f"Skipping {file}, unrecognized file type")
            continue
        # setup output filepath
        parent = file.parent
        stem = file.stem
        relpath = (parent / stem).relative_to(Path("."))
        write_dir = Path("build/ocr") / relpath
        write_dir.mkdir(parents=True, exist_ok=True)
        write_path = write_dir / "response.json"
        # output data
        if not force and write_path.exists():
            print(f"{write_path} exists, skipping {file}")
            continue
        response = llm_read_text(file)
        json = response.model_dump_json(indent=2)
        Path(write_dir / "response.json").write_text(json)
        print(f"processed {file}")


if __name__ == "__main__":
    app()
