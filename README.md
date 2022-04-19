# data-utils
![version](https://img.shields.io/badge/version-0.2.0-blue) ![version](https://img.shields.io/badge/python-3.8-blue.svg?&logo=python&logoColor=yellow)

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