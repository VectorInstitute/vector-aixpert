# Contributing to AIXpert

Thanks for your interest in contributing to the AIXpert!

To submit PRs, please fill out the PR template along with the PR. If the PR
fixes an issue, don't forget to link the PR to the issue!

## Development Practices

We use the standard git development flow of branch and merge to main with PRs on GitHub.
 At least one member of the core team needs to approve a PR before it can be merged into
  main. As mentioned above, tests are run automatically on PRs with a merge target of
  main. Furthermore, a suite of static code checkers and formatters are also run on
  said PRs. These also need to pass for a PR to be eligible for merging into the main
  branch of the library.



## Coding guidelines

For code style, we recommend the [PEP 8 style guide](https://peps.python.org/pep-0008/).

For docstrings we use [numpy format](https://numpydoc.readthedocs.io/en/latest/format.html).

We use [ruff](https://docs.astral.sh/ruff/) for code formatting and static code
analysis. Ruff checks various rules including [flake8](https://docs.astral.sh/ruff/faq/#how-does-ruff-compare-to-flake8).
The pre-commit hooks show errors which you need to fix before submitting a PR.

Last but not the least, we use type hints in our code which is then checked using
[mypy](https://mypy.readthedocs.io/en/stable/).

### Pre-commit hooks

All of these checks and formatters are invoked by [pre-commit](https://pre-commit.com/)
hooks. These hooks are run remotely on GitHub.
In order to ensure that your code conforms to these standards, and,
therefore, passes the remote checks, you can install the pre-commit hooks to be run
locally. This is done by running (with your environment active):
```bash
pre-commit install
```
Once the python virtual environment is setup, you can run pre-commit hooks using:

```bash
pre-commit run --all-files
```

## github actions

The repository consists of the following github action continuous integration workflows:

- [code checks](https://github.com/VectorInstitute/AIXpert/blob/main/.github/workflows/code_checks.yml): Static code analysis, code formatting and unit tests
- [documentation](https://github.com/VectorInstitute/AIXpert/blob/main/.github/workflows/docs.yml): Project documentation including example API reference
- [integration tests](https://github.com/VectorInstitute/AIXpert/blob/main/.github/workflows/integration_tests.yml): Integration tests
- [publish](https://github.com/VectorInstitute/AIXpert/blob/main/.github/workflows/publish.yml):
Publishing python package to PyPI.
