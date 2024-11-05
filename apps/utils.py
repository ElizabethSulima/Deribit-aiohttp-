import os
from pathlib import Path
from typing import Any
from uuid import uuid4


def write_file(filename: str, content: bytes, dir_path: Path) -> str:
    file_name = Path(filename)
    new_file_name = f"{file_name.stem}{str(uuid4())}{file_name.suffix}"
    file_path = dir_path / new_file_name
    file_path.write_bytes(content)
    return str(file_path)


def make_image_data(
    file_path: str, file_title: str, resolution: str, uuid: str
) -> dict[str, Any]:
    size = os.stat(file_path).st_size
    dict_image = {
        "file_path": file_path,
        "title": str(file_title),
        "size": size,
        "resolution": resolution,
        "uuid": uuid,
    }
    return dict_image
