"""Window code for ReStreamLocal - ReStreamLocal provides an easy-to-use locally hosted alternative to restream.io. Simply Open the program in the background and setup your OBS or Streamlabs to stream into it and it will take care of redistributing your stream..

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

import subprocess
import sys
import tempfile
import tkinter as tk
import zipfile
from importlib.abc import Traversable
from io import BytesIO
from pathlib import Path
from shelve import Shelf
from sys import platform
from typing import cast, Callable, List, Tuple

from ._assets import RESOURCES
from .windows_utils import get_project_local_appdata_dir


# yes, these functions should probably not be in a closure. i do not care!!!! el oh el
# mona process handling
def get_mona_server_zip() -> Traversable:
    if platform != "win32":
        raise NotImplementedError("Only Windows is supported for now.")
    python_is_64_bit = sys.maxsize > 2 ** 32  # https://stackoverflow.com/questions/1405913/how-do-i-determine-if-my-python-shell-is-executing-in-32bit-or-64bit
    if python_is_64_bit:
        # If the python is 64 bit, the system must be as well
        return RESOURCES / "MonaServer_Win64.zip"
    else:
        # While the python is 32 bit, the system could be 32 or 64 bit, use 32 bit which works on both
        return RESOURCES / "MonaServer_Win32.zip"


def get_mona_server_directory() -> Path:
    # first, see if we already made a mona server tempdir
    mona_server_dir = Path(tempfile.gettempdir()) / "mona_server"
    mona_server_dir.mkdir(exist_ok=True, parents=True)  # for some reason, just using the local appdata directory always returns true
    mona_server_executable = mona_server_dir / "MonaServer.exe"
    if mona_server_dir.exists() and mona_server_executable.exists():
        print("Using existing MonaServer")
        print(mona_server_dir)
        return mona_server_dir

    # if we didn't, make one
    mona_server_zip = get_mona_server_zip()

    # all of the files of the zip are top level, just extract straight
    if mona_server_zip.is_file():
        with zipfile.ZipFile(cast(Path, mona_server_zip), "r") as zip_ref:
            zip_ref.extractall(mona_server_dir)
    else:
        with BytesIO() as zip_data:
            zip_data.write(mona_server_zip.read_bytes())
            zip_data.seek(0)
            with zipfile.ZipFile(zip_data, "r") as zip_ref:
                zip_ref.extractall(mona_server_dir)

    print("Successfully extracted MonaServer")
    print(mona_server_dir)

    return mona_server_dir


def kill_all_monaservers() -> None:
    """Kills all MonaServer instances using taskkill, even if we have lost track of them."""
    # a little bit of a hack, but it will work for us

    # taskkill /IM MonaServer.exe /F

    subprocess.run(["taskkill", "/IM", "MonaServer.exe", "/F"], shell=True)


def build_stream_url(host: str, port: str) -> str:
    return f"rtmp://{host}:{port}/live"


def overwrite_clipboard(window: tk.Tk, *args, **kwargs) -> None:
    window.clipboard_clear()
    window.clipboard_append(*args, **kwargs)


def pack_monaserver_widgets(window: tk.Tk) -> tuple[Callable[[], str], Callable[[], str], Callable[[], None]]:
    """
    Returns a tuple of functions:
    - get_stream_url: returns the stream URL
    - get_stream_key: returns the stream key
    - stop_mona_server: stops the MonaServer
    """

    # We don't bother to expose options for the host & port, most people won't care at all.
    # Label for local host in a frame
    local_host_frame = tk.Frame(window)
    local_host_label = tk.Label(local_host_frame, text="Local Host")
    local_host_label.pack(side=tk.LEFT)
    local_host_entry = tk.Entry(local_host_frame)
    local_host_entry.insert(0, "127.0.0.1")
    local_host_entry.configure(state=tk.DISABLED)  # have to do this after we insert the text
    local_host_entry.pack(side=tk.RIGHT)
    local_host_frame.pack()

    # Label for local port
    local_host_frame = tk.Frame(window)
    local_port_label = tk.Label(local_host_frame, text="Local Port")
    local_port_label.pack(side=tk.LEFT)
    local_port_entry = tk.Entry(local_host_frame)
    local_port_entry.insert(0, "1935")
    local_port_entry.configure(state=tk.DISABLED)  # have to do this after we insert the text
    local_port_entry.pack(side=tk.RIGHT)
    local_host_frame.pack()

    get_stream_url = lambda: build_stream_url(local_host_entry.get(), local_port_entry.get())

    # Stream key
    stream_key_frame = tk.Frame(window)
    stream_key_label = tk.Label(stream_key_frame, text="Stream Key")
    stream_key_label.pack(side=tk.LEFT)
    stream_key_entry = tk.Entry(stream_key_frame)
    stream_key_entry.insert(0, "stream")
    stream_key_entry.configure(state=tk.DISABLED)  # have to do this after we insert the text
    stream_key_entry.pack(side=tk.RIGHT)
    stream_key_frame.pack()

    # Button to start server, copy URL, & stream key
    mona_button_frame = tk.Frame(window)
    start_server_button = tk.Button(mona_button_frame, text="Start/Restart Server")
    start_server_button.bind("<Button-1>", lambda _: start_mona_server())
    start_server_button.pack(side=tk.LEFT)
    copy_url_button = tk.Button(mona_button_frame, text="Copy Stream URL")
    copy_url_button.bind("<Button-1>", lambda _: overwrite_clipboard(window, get_stream_url()))
    copy_url_button.pack(side=tk.LEFT)
    copy_key_button = tk.Button(mona_button_frame, text="Copy Stream Key")
    copy_key_button.bind("<Button-1>", lambda _: overwrite_clipboard(window, stream_key_entry.get()))
    copy_key_button.pack(side=tk.LEFT)
    mona_button_frame.pack()

    # Status
    status_label = tk.Label(window, text="Server not running")
    status_label.pack()

    current_mona_subprocess: subprocess.Popen | None = None

    def stop_mona_server() -> None:
        nonlocal current_mona_subprocess
        if current_mona_subprocess is not None:
            status_label.configure(text="Stopping server")
            current_mona_subprocess.kill()  # this is sometimes ineffective, hence the above
            current_mona_subprocess.wait()
            kill_all_monaservers()
            current_mona_subprocess = None
            status_label.configure(text="Server not running")
            print("Stopping server")

    def start_mona_server():
        nonlocal current_mona_subprocess
        stop_mona_server()

        status_label.configure(text="Server starting")
        mona_server_directory = get_mona_server_directory()
        mona_server_executable = mona_server_directory / "MonaServer.exe"
        mona_server_executable_str = str(mona_server_executable)

        print(f"Starting {mona_server_executable_str}")
        current_mona_subprocess = subprocess.Popen(
            [mona_server_executable_str],
            cwd=mona_server_directory,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )

        # the following is kinda hacky, but it works
        try:
            # we really should be looking to see if the server printed out "Server Running", but thats complicated
            stdout, stderr = current_mona_subprocess.communicate(timeout=1)
            current_mona_subprocess = None
        except subprocess.TimeoutExpired:
            pass
        else:
            status_label.configure(text="Server failed to start, see console")
            for line in stdout.splitlines():
                print(line)
            for line in stderr.splitlines():
                print(line)
            return

        status_label.configure(text="Server running")

    return get_stream_url, lambda: stream_key_entry.get(), stop_mona_server


REMOTE_HOST_TYPE = tuple[str, str]


def pack_remote_host_adding_widgets(window: tk.Tk, config: Shelf) -> Callable[[], list[Callable[[], REMOTE_HOST_TYPE]]]:
    """
    Returns a function that returns a list of functions that return a remote url, stream key, and any aditional info
    """

    # Remote hosts
    remote_host_header_frame = tk.Frame(window)

    # Label to add/remove remote hosts
    remote_host_label = tk.Label(remote_host_header_frame, text="Remote Hosts")
    remote_host_label.pack(side=tk.LEFT)
    number_of_remote_hosts = config.get("num_remote_hosts", 1)  # volatile variable to keep track of the number of remote hosts
    remote_host_tuple_getters: list[Callable[
        [], tuple[str, str]]] = []  # list of functions that return a remote url, stream key, and any aditional info
    # +/- buttons
    remote_host_button_frame = tk.Frame(remote_host_header_frame)

    def handle_add_host(_: tk.Event[tk.Button]) -> None:
        nonlocal number_of_remote_hosts
        number_of_remote_hosts += 1
        store_all_remote_hosts()
        render_remote_host_entry()

    add_remote_host_button = tk.Button(remote_host_button_frame, text="+")
    add_remote_host_button.pack(side=tk.LEFT)
    add_remote_host_button.bind("<Button-1>", handle_add_host)

    def handle_remove_host(_: tk.Event[tk.Button]) -> None:
        nonlocal number_of_remote_hosts
        if number_of_remote_hosts > 1:
            number_of_remote_hosts -= 1
        store_all_remote_hosts()
        render_remote_host_entry()

    remove_remote_host_button = tk.Button(remote_host_button_frame, text="-")
    remove_remote_host_button.pack(side=tk.RIGHT)
    remove_remote_host_button.bind("<Button-1>", handle_remove_host)
    remote_host_button_frame.pack(side=tk.RIGHT)
    remote_host_header_frame.pack()
    # Remote host entries
    remote_host_frame = tk.Frame(window)

    def save_all_remote_hosts(*args) -> None:
        nonlocal remote_host_tuple_getters, number_of_remote_hosts
        config["remote_hosts"] = [getter() for getter in remote_host_tuple_getters]
        config["num_remote_hosts"] = number_of_remote_hosts

    def store_all_remote_hosts() -> None:
        save_all_remote_hosts()
        config.sync()

    def render_remote_host_entry() -> None:
        nonlocal remote_host_tuple_getters
        remote_host_tuple_getters.clear()
        saved_remote_hosts = config.get("remote_hosts", [])
        for widget in remote_host_frame.winfo_children():
            widget.destroy()
        for i in range(number_of_remote_hosts):
            remote_host_i_frame = tk.Frame(remote_host_frame)

            remote_host_url_frame = tk.Frame(remote_host_i_frame)
            remote_host_label = tk.Label(remote_host_url_frame, text=f"Remote Host {i + 1}")
            remote_host_label.pack(side=tk.LEFT)
            remote_host_stringvar = tk.StringVar()
            remote_host_entry = tk.Entry(remote_host_url_frame, textvariable=remote_host_stringvar)
            remote_host_stringvar.trace_add("write", save_all_remote_hosts)
            remote_host_entry.pack(side=tk.RIGHT)
            remote_host_url_frame.pack(side=tk.LEFT)

            remote_host_key_frame = tk.Frame(remote_host_i_frame)
            remote_host_key_label = tk.Label(remote_host_key_frame, text="Stream Key")
            remote_host_key_label.pack(side=tk.LEFT)
            remote_host_key_stringvar = tk.StringVar()
            remote_host_key_entry = tk.Entry(remote_host_key_frame, textvariable=remote_host_key_stringvar)
            remote_host_key_stringvar.trace_add("write", save_all_remote_hosts)
            remote_host_key_entry.pack(side=tk.RIGHT)
            remote_host_key_frame.pack(side=tk.RIGHT)

            if i < len(saved_remote_hosts):
                remote_host_entry.insert(0, saved_remote_hosts[i][0])
                remote_host_key_entry.insert(0, saved_remote_hosts[i][1])

            # remote_host_entry gets reassigned, we have to be clever with our closures
            def remote_host_tuple_getter_factory() -> Callable[[], tuple[str, str]]:
                this_remote_host_entry = remote_host_entry
                this_remote_host_key_entry = remote_host_key_entry
                return lambda: (this_remote_host_entry.get(), this_remote_host_key_entry.get())

            remote_host_tuple_getters.append(remote_host_tuple_getter_factory())

            remote_host_i_frame.pack()

    def get_host_tuple_getters() -> list[Callable[[], REMOTE_HOST_TYPE]]:
        store_all_remote_hosts()
        return remote_host_tuple_getters

    render_remote_host_entry()
    remote_host_frame.pack()

    return get_host_tuple_getters


def get_ffmpeg_executable() -> Path:
    ffmpeg_traversable = RESOURCES / "ffmpeg.exe"
    if ffmpeg_traversable.is_file():
        return cast(Path, ffmpeg_traversable)

    # we need to check to see if we already made a tempdir
    project_appdata_dir = Path(tempfile.gettempdir()) / "restreamlocal"
    project_appdata_dir.mkdir(exist_ok=True)
    ffmpeg_executable = project_appdata_dir / "ffmpeg.exe"
    if ffmpeg_executable.exists():
        print("Using existing ffmpeg")
        print(ffmpeg_executable)
        return ffmpeg_executable

    # if we didn't, make one
    with open(ffmpeg_executable, "wb") as f:
        f.write(ffmpeg_traversable.read_bytes())

    return ffmpeg_executable


def pack_ffmpeg_client_widgets(window: tk.Tk, config: Shelf, get_stream_url: Callable[[], str], get_stream_key: Callable[[], str]) -> Callable[[], None]:
    """
    Returns a function that stops the ffmpeg process
    """

    get_remote_host_tuple_getters = pack_remote_host_adding_widgets(window, config)

    # Button to start streams
    start_streams_button = tk.Button(window, text="Start/Restart Streams")
    start_streams_button.bind("<Button-1>", lambda _: start_ffmpeg_process())
    start_streams_button.pack()
    # Stream status
    stream_status_label = tk.Label(window, text="Streams not running")
    stream_status_label.pack()
    # ffmpeg process handling
    current_ffmpeg_subprocess: subprocess.Popen | None = None

    def stop_ffmpeg_process() -> None:
        nonlocal current_ffmpeg_subprocess
        if current_ffmpeg_subprocess is not None:
            stream_status_label.configure(text="Stopping streams")
            current_ffmpeg_subprocess.kill()
            current_ffmpeg_subprocess.wait()
            current_ffmpeg_subprocess = None
            stream_status_label.configure(text="Streams not running")
            print("Stopping streams")

    def start_ffmpeg_process() -> None:
        nonlocal current_ffmpeg_subprocess
        stop_ffmpeg_process()

        ffmpeg_executable = get_ffmpeg_executable()
        ffmpeg_executable_str = str(ffmpeg_executable)

        # we need to assemble the URL of each remote host
        remote_host_urls = []
        for remote_host_tuple_getter in get_remote_host_tuple_getters():
            remote_host_url, remote_stream_key = remote_host_tuple_getter()
            remote_host_urls.append(f"{remote_host_url}/{remote_stream_key}")

        # we need to assemble the command

        tee_filter = "|".join([f"[f=flv]{url}" for url in remote_host_urls])

        print(f"Starting {ffmpeg_executable_str}")
        current_ffmpeg_subprocess = subprocess.Popen(
            [
                ffmpeg_executable_str,
                "-i",
                f"{get_stream_url()}/{get_stream_key()}",
                "-c:v",
                "copy",  # no reencoding
                "-c:a",
                "copy",
                "-map",
                "0",
                "-f",
                "tee",
                tee_filter
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stream_status_label.configure(text=f"{len(remote_host_urls)} Streams running")

    return stop_ffmpeg_process


def create_restream_window(config: Shelf) -> tk.Tk:
    # overall idea borrowed from https://obsproject.com/forum/resources/obs-studio-stream-to-multiple-platforms-or-channels-at-once.932/
    window = tk.Tk()

    # Set the window title
    window.title("ReStreamLocal")

    # Description
    description = tk.Label(window,
                           text="ReStreamLocal provides an easy-to-use locally hosted alternative to restream.io.")
    description.pack()
    # more_info = tk.Label(window, text="To use ReStreamLocal, you must have the following two pieces of software installed: \n"
    #                                   "1. MonaServer (https://sourceforge.net/projects/monaserver/)\n"
    #                                   "2. ffmpeg (https://ffmpeg.org/)")
    # more_info.pack()
    usage = tk.Label(window, text="To use ReStreamLocal, do the following.\n"
                                  "1. Open ReStreamLocal, adding any configurations.\n"
                                  "2. Copy your Stream Key & Stream URL into OBS.\n"
                                  "3. Press \"Start/Restart Server\" in ReStreamLocal.\n"
                                  "4. Start streaming in OBS.\n"
                                  "5. Add your remote hosts in ReStreamLocal, along with their stream keys.\n"
                                  "6. Press \"Start/Restart Streams\" in ReStreamLocal.\n"
                                  "If everything is green, your stream will be live on all platforms.\n"
                                  "Remember to update the stream descriptions on all platforms, as this will not do that for you.")
    usage.pack()

    # Spacing
    spacing = tk.Label(window, text="")
    spacing.pack()

    get_stream_url, get_stream_key, stop_mona_server = pack_monaserver_widgets(window)

    # Spacing
    spacing2 = tk.Label(window, text="")
    spacing2.pack()

    stop_ffmpeg_process = pack_ffmpeg_client_widgets(window, config, get_stream_url, get_stream_key)

    # Spacing
    spacing3 = tk.Label(window, text="")
    spacing3.pack()

    # By regulad
    attribution = tk.Label(window, text="Built with OSS<3 by regulad\n"
                                        "https://t.regulad.xyz")
    attribution.pack()

    def cleanup():
        stop_ffmpeg_process()
        stop_mona_server()
        config.sync()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", cleanup)
    window.bind("<Control-c>", lambda _: cleanup())

    return window


__all__ = ("create_restream_window",)
