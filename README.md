# ReStreamLocal

[![PyPI](https://img.shields.io/pypi/v/restreamlocal.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/restreamlocal.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/restreamlocal)][pypi status]
[![License](https://img.shields.io/pypi/l/restreamlocal)][license]

[![Read the documentation at https://restreamlocal.readthedocs.io/](https://img.shields.io/readthedocs/restreamlocal/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/regulad/restreamlocal/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/regulad/restreamlocal/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/restreamlocal/
[read the docs]: https://restreamlocal.readthedocs.io/
[tests]: https://github.com/regulad/restreamlocal/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/regulad/restreamlocal
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

![Screenshot 2024-06-11 190449.png](./Screenshot%202024-06-11%20190449.png)

## Features

- Stream to multiple destinations without sending your data to a website like Restream.io
- Entirely local
- No account required
- No limits on the number of destinations
- Alternative to https://github.com/sorayuki/obs-multi-rtmp which is not maintained in English and requires a plugin
- Runs entirely separately of OBS Studio, can be used with any program.
- TODO: Sort the main entrypoint into different files, although i avoided spaghetti code, it's still a bit of a mess.
- TODO: Preserve settings between runs

## Requirements

- Currently only supports Windows. Some binaries are bundled and loaded at runtime.
  - https://sourceforge.net/projects/monaserver
  - ffmpeg (although; this does work on linux. this project is rather thrown together, possibly later?)
- VS 2013 redistributable (https://www.microsoft.com/en-us/download/details.aspx?id=40784)

## Installation

You can install _ReStreamLocal_ via [pip] from [PyPI]:

```console
$ pip install restreamlocal
```

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [GPL 3.0 license][license],
_ReStreamLocal_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@regulad]'s [neopy] template.

[@regulad]: https://github.com/regulad
[pypi]: https://pypi.org/
[neopy]: https://github.com/regulad/cookiecutter-neopy
[file an issue]: https://github.com/regulad/restreamlocal/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/regulad/restreamlocal/blob/main/LICENSE
[contributor guide]: https://github.com/regulad/restreamlocal/blob/main/CONTRIBUTING.md
[command-line reference]: https://restreamlocal.readthedocs.io/en/latest/usage.html
