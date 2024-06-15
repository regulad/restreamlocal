"""Windows utilities for ReStreamLocal - ReStreamLocal provides an easy-to-use locally hosted alternative to restream.io. Simply Open the program in the background and setup your OBS or Streamlabs to stream into it and it will take care of redistributing your stream..

Copyright (C) 2024  Parker Wahle

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""  # noqa: E501, B950
from __future__ import annotations

from pathlib import Path
import os

from ._metadata import __title__


def get_appdata_dir() -> Path:
    return Path(os.getenv("APPDATA"))


def get_local_appdata_dir() -> Path:
    return Path(os.getenv("LOCALAPPDATA"))


def get_project_appdata_dir() -> Path:
    return get_appdata_dir() / __title__.lower()


def get_project_local_appdata_dir() -> Path:
    return get_local_appdata_dir() / __title__.lower()


__all__ = ("get_appdata_dir", "get_local_appdata_dir", "get_project_appdata_dir", "get_project_local_appdata_dir")
