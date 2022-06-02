# data-utils
![version](https://img.shields.io/badge/version-1.2.0-blue) ![version](https://img.shields.io/badge/python-3.8-blue.svg?&logo=python&logoColor=yellow)

`data-utils` is a library to support the work of the Data Team at Our World in Data.

## Install
Currently no release has been published. You can install the version under development directly from GitHub:
```
pip install git+https://github.com/owid/data-utils-py
```


## Development

### Pre-requisites
You need Python 3.8+, `poetry` and `make` installed. 

```
# Install poetry
pip install poetry
```

### Install in development mode

```
poetry install
```

### Test the code
Run:

```
# run all unit tests and CI checks
make test
```

### Other useful commands

#### Coverage

```
make coverage
```

This will print how much of the source code is covered by the implemented tests. Additionally, it generates an HTML
directory (`.report-coverage`), which provides a frendly view of the source code coverage.


#### Linting

```
make linting
```

Check if the source code passes all flake8 styling tests. Additionally, it generages an HTML directory
(`.report-linting`), which provides a friendly view of the style issues (if any).

Flake8 configuration can be tweaked in [.flake8](.flake8) file.