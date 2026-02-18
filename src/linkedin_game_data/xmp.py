import datetime
import logging
from typing import Any

from PIL.Image import Image

log = logging.getLogger(__name__)

__all__ = ["get_xmp_data", "get_rdf_datetime"]


def get_xmp_data(img: Image, *path_args) -> Any | None:
    data: dict[str, str] = img.getxmp()
    for key in path_args:
        data = data.get(key)
        if not data:
            log.warning("No XMP data at %s", key)
            return
    return data


def get_rdf_datetime(img: Image) -> datetime.datetime:
    xmp_path: tuple[str, ...] = ("xmpmeta", "RDF", "Description", "DateCreated")
    data: str | None = get_xmp_data(img, *xmp_path)
    if not data:
        log.warning("No RDF DateCreated data")
        return
    return datetime.datetime.fromisoformat(data)
