# 🤝 Contributing to **vector-AIXpert**

Thank you for your interest in contributing to **vector-AIXpert**, an open-source toolkit for **fair, explainable, and accountable generative AI**.
We welcome contributions from developers, researchers, and practitioners of all experience levels.

---

## 🧭 Code of Conduct

By participating in this project, you agree to follow the [Vector Institute Code of Conduct](./CODE_OF_CONDUCT.md).
Please treat all contributors with respect and professionalism.

---

## 🚀 Getting Started

Before you begin, ensure your environment is properly configured.

### 1️⃣ Fork and clone the repository

```bash
git clone https://github.com/VectorInstitute/vector-aixpert.git
cd vector-aixpert
```

### 2️⃣ Create a virtual environment using [uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
uv sync --dev
source .venv/bin/activate
```

### 3️⃣ Install pre-commit hooks

```bash
pre-commit install
```

This ensures all code quality checks run locally before each commit.

---

## 🧑🏿‍💻 What Contributions Are Welcome?

We welcome contributions of all sizes, including:

1. 🐛 **Bug Fixes** — Help improve stability and correctness.
   Look for issues tagged `good first issue` or `bug`.

2. 🧩 **New Features** — Extend vector-AIXpert’s capabilities in fairness evaluation, multimodal generation, or explainability.
   Please open an issue first to discuss your idea.

3. 🧠 **Documentation** — Improve tutorials, usage guides, or API references under `docs/`.

4. 🧪 **Tests & Benchmarks** — Increase test coverage or add evaluation scripts for new datasets or models.

5. 🎓 **Examples & Use Cases** — Share practical examples, Jupyter notebooks, or integrations.

---

## 🔀 Development Workflow

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** following the [Coding Guidelines](#-coding-guidelines) below.

3. **Run pre-commit checks**

   ```bash
   pre-commit run --all-files
   ```

4. **Test your changes**

   ```bash
   pytest
   ```

5. **Commit your work**

   ```bash
   git commit -m "Add feature: short description"
   ```

6. **Push and open a Pull Request**

   ```bash
   git push origin feature/your-feature-name
   ```

Each PR should:

* Reference related issues (`Fixes #42`)
* Pass all CI checks
* Include updated documentation (if applicable)

---

## 🧩 Coding Guidelines

We follow consistent, standards-based practices to ensure code quality and reproducibility.

| Category                 | Tool / Standard                                                       | Description                                    |
| ------------------------ | --------------------------------------------------------------------- | ---------------------------------------------- |
| **Code style**           | [PEP 8](https://peps.python.org/pep-0008/)                            | Follow Python community conventions            |
| **Formatting & linting** | [ruff](https://docs.astral.sh/ruff/)                                  | Enforces style, Flake8, and import order rules |
| **Type checking**        | [mypy](https://mypy.readthedocs.io/en/stable/)                        | Static type analysis                           |
| **Docstrings**           | [NumPy format](https://numpydoc.readthedocs.io/en/latest/format.html) | Used throughout `src/aixpert`                  |
| **Testing**              | [pytest](https://docs.pytest.org/en/stable/)                          | For all unit and integration tests             |
| **Docs build**           | [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)       | Live site generation                           |

> 🧠 **Tip:** Use [autoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) in VS Code to generate compliant docstrings automatically.

### Type hints

* Use Python 3.10+ modern typing:

  ```python
  def generate_metadata(items: list[str]) -> dict[str, int]:
      ...
  ```
* Use `|` syntax for union and optional types:

  ```python
  def load_config(path: str | None = None) -> dict[str, str]:
      ...
  ```

---

## 🧰 Pre-commit Hooks

We use [pre-commit](https://pre-commit.com/) to ensure local and remote consistency.

Run locally before committing:

```bash
pre-commit run --all-files
```
or using `uvx`:

```bash
uvx pre-commit run --all-files
```

Common checks:

* `ruff` → formatting + linting
* `mypy` → static type checks
* `typos` → spell check
* `nbQA` → notebook linting

These same checks are executed in CI for every pull request.

---

## ⚙️ GitHub Actions

Automated CI workflows ensure stability and reproducibility across commits.

| Workflow                                                             | Purpose                             |
| -------------------------------------------------------------------- | ----------------------------------- |
| [**code_checks.yml**](.github/workflows/code_checks.yml)             | Linting, formatting, and unit tests |
| [**integration_tests.yml**](.github/workflows/integration_tests.yml) | Full integration and pipeline tests |
| [**docs.yml**](.github/workflows/docs.yml)                           | Build and deploy documentation      |
| [**publish.yml**](.github/workflows/publish.yml)                     | Publish releases to PyPI            |

All must pass before merging to `main`.

---

## 🧪 Testing

All tests reside in the `tests/` directory and use `pytest`.

```bash
# Run all tests
pytest .

# Run a specific test
pytest tests/data_generation/test_images.py
```

> ✅ **Tip:** VS Code users can enable the built-in testing UI by setting `"python.testing.pytestEnabled": true` in `.vscode/settings.json`.

---

## 🧱 Documentation Development

If you are modifying docs:

```bash
uv run mkdocs serve
```

This starts a live preview server at [http://127.0.0.1:8000](http://127.0.0.1:8000).

Ensure:

* All markdown files under `docs/` build correctly.
* API references (`api.md`) regenerate automatically.
* Screenshots or assets go under `docs/assets/`.

---

## 🔍 Code Review & Merge Process

1. At least **one core team member** must review and approve all PRs.
2. All **tests, checks, and docs builds** must pass before merging.
3. PRs are merged via **Squash and Merge** to keep history clean.
4. Significant PRs may require multiple reviewers or design discussion in an issue.

---

## 📬 Communication & Support

* 💬 Open a [GitHub Issue](https://github.com/VectorInstitute/AIXpert/issues) for bugs or feature requests.
* 🧵 Use **GitHub Discussions** for design or research ideas.
* 🌐 Visit [AIXpert Project Website](https://aixpert-project.eu/) for consortium details.

---

## 🪪 License & Attribution

By contributing to **vector-AIXpert**, you agree that your contributions will be licensed under the repository’s [MIT License](LICENSE).

If you use **vector-AIXpert** in academic work, please cite our [technical report](https://vectorinstitute.github.io/vector-aixpert/) or publications listed in the README.
<!-- TODO: Edit the technical report link above when available -->

---

## ✨ Final Words

Every contribution — whether fixing a typo, refining a fairness metric, or expanding a generation pipeline — helps make AI **more transparent and trustworthy**.

Thank you for helping advance responsible and explainable AI research! 💙
