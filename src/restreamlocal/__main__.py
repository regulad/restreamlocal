"""CLI for ReStreamLocal - ReStreamLocal provides an easy-to-use locally hosted alternative to restream.io. Simply Open the program in the background and setup your OBS or Streamlabs to stream into it and it will take care of redistributing your stream..

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

import shelve

import typer

from .windows_utils import get_project_appdata_dir
from .window import create_restream_window

cli = typer.Typer()


@cli.command()
def main() -> None:
    """Run the ReStreamLocal GUI."""
    appdata_dir = get_project_appdata_dir()
    appdata_dir.mkdir(parents=True, exist_ok=True)
    config_file = appdata_dir / "config"
    with shelve.open(str(config_file), writeback=True) as config:
        window = create_restream_window(config)
        window.mainloop()


if __name__ == "__main__":  # pragma: no cover
    cli()

__all__ = ("cli",)
