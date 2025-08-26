# AIXpert

----------------------------------------------------------------------------------------

[![code checks](https://github.com/VectorInstitute/AIXpert/actions/workflows/code_checks.yml/badge.svg)](https://github.com/VectorInstitute/AIXpert/actions/workflows/code_checks.yml)
[![unit tests](https://github.com/VectorInstitute/AIXpert/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/VectorInstitute/AIXpert/actions/workflows/unit_tests.yml)
[![integration tests](https://github.com/VectorInstitute/AIXpert/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/VectorInstitute/AIXpert/actions/workflows/integration_tests.yml)
[![docs](https://github.com/VectorInstitute/AIXpert/actions/workflows/docs.yml/badge.svg)](https://github.com/VectorInstitute/AIXpert/actions/workflows/docs.yml)


<!-- TODO: Uncomment this with the right credentials once codecov is set up for this repo.
[![codecov](https://codecov.io/github/VectorInstitute/AIXpert/graph/badge.svg?token=83MYFZ3UPA)](https://codecov.io/github/VectorInstitute/AIXpert)
-->
<!-- TODO: Uncomment this when the repository is made public
![GitHub License](https://img.shields.io/github/license/VectorInstitute/AIXpert)
-->

<!--
TODO: Add picture / logo
-->

<!--
TODO: Add introduction about AIXpert here
-->


## 🧑🏿‍💻 Installation

### Installing dependencies

The development environment can be set up using
[uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation).
Instructions for installing uv can be found [here](https://docs.astral.sh/uv/getting-started/installation/).


Once installed, run:

```bash
uv sync
source .venv/bin/activate
```
Note that uv supports [optional dependency groups](https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-groups)
which helps to manage dependencies for different parts of development such as
`documentation`, `testing`, etc.
The core dependencies are installed using the command `uv sync`

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
