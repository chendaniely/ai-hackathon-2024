# from:
# https://github.com/jcheng5/multimodal/blob/4d1013f3dd1b09dd28f292d6a445e4b39131dfc9/media_extractor/__init__.py#L23-L34

from __future__ import annotations

import base64
import contextlib
import mimetypes
import os
import re
import shutil
import tempfile
from pathlib import Path, PurePath
from typing import Generator

import ffmpeg

__all__ = (
    "from_file",
    "from_bytes",
    "parse",
    "as_tempfile",
)


def split_video(video_uri_or_file: str, fps: int = 2) -> tuple[str, list[str]]:
    if shutil.which("ffmpeg") is None:
        raise FileNotFoundError("ffmpeg not found in PATH")

    if not video_uri_or_file.startswith("data:"):
        video_uri = from_file(video_uri_or_file)
    else:
        video_uri = video_uri_or_file

    with tempfile.TemporaryDirectory() as outdir:
        audio = PurePath(outdir) / "audio.mp3"
        with as_tempfile(video_uri) as video_file:
            (
                ffmpeg.input(video_file)
                .output(
                    str(audio),
                    loglevel="error",
                    **{
                        # Use 64k bitrate for smaller file
                        "b:a": "64k",
                        # Only output one channel, again for smaller file
                        "ac": "1",
                    },
                )
                .run()
            )
            (
                ffmpeg.input(video_file)
                .output(
                    str(PurePath(outdir) / "frame-%04d.jpg"),
                    loglevel="error",
                    **{
                        # Use fps as specified, scale image to fit within 512x512
                        "vf": f"fps={fps},scale='if(gt(iw,ih),512,-1)':'if(gt(ih,iw),512,-1)'",
                        "q:v": "20",
                    },
                )
                .run()
            )
        images = list(Path(outdir).glob("*.jpg"))
        images.sort()
        return from_file(audio), [from_file(image) for image in images]


def from_file(file_path, mime_type=None) -> str:
    if mime_type is None:
        mime_type = mimetypes.guess_type(file_path)[0]
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded_string}"


def from_bytes(bytes: bytes, mime_type: str) -> str:
    encoded_string = base64.b64encode(bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_string}"


def parse(data_uri: str) -> tuple[bytes, str]:
    match = re.match(
        r"data:(?P<mime_type>.*?);base64,(?P<encoded_string>.*)", data_uri
    )
    if match is None:
        raise ValueError("Invalid data URI")
    return (
        base64.b64decode(match["encoded_string"]),
        match["mime_type"].split(";")[0].strip(),
    )


@contextlib.contextmanager
def as_tempfile(data_uri: str) -> Generator[str, None, None]:
    bytes, mime_type = parse(data_uri)
    with tempfile.NamedTemporaryFile(
        suffix=mimetypes.guess_extension(mime_type), delete=False
    ) as file:
        file.write(bytes)
        try:
            yield file.name
        finally:
            file.close()
            os.unlink(file.name)
