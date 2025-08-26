# AI Engineering template (with uv)

----------------------------------------------------------------------------------------

[![code checks](https://github.com/VectorInstitute/aieng-template-uv/actions/workflows/code_checks.yml/badge.svg)](https://github.com/VectorInstitute/aieng-template-uv/actions/workflows/code_checks.yml)
[![integration tests](https://github.com/VectorInstitute/aieng-template-uv/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/VectorInstitute/aieng-template-uv/actions/workflows/integration_tests.yml)
[![docs](https://github.com/VectorInstitute/aieng-template-uv/actions/workflows/docs.yml/badge.svg)](https://github.com/VectorInstitute/aieng-template-uv/actions/workflows/docs.yml)
[![codecov](https://codecov.io/github/VectorInstitute/aieng-template-uv/graph/badge.svg?token=83MYFZ3UPA)](https://codecov.io/github/VectorInstitute/aieng-template-uv)
![GitHub License](https://img.shields.io/github/license/VectorInstitute/aieng-template-uv)

A template repo for AI Engineering projects (using ``python``) and ``uv``. This
template is like our original AI Engineering [template](https://github.com/VectorInstitute/aieng-template),
however, unlike how that template uses poetry, this one uses uv for dependency
management (as well as packaging and publishing).

## 🧑🏿‍💻 Developing

### Installing dependencies

The development environment can be set up using
[uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation). Hence, make sure it is
installed and then run:

```bash
uv sync
source .venv/bin/activate
```

In order to install dependencies for testing (codestyle, unit tests, integration tests),
run:

```bash
uv sync --dev
source .venv/bin/activate
```

In order to exclude installation of packages from a specific group (e.g. docs),
run:

```bash
uv sync --no-group docs
```

## Getting Started

## Features / Components

## Examples

## Contributing
If you are interested in contributing to the library, please see
[CONTRIBUTING.MD](CONTRIBUTING.MD). This file contains many details around contributing
to the code base, including development practices, code checks, tests, and more.

<!--
TODO:

## Acknowledgements

## Citation

-->
