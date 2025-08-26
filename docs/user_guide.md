# Documentation

This section of the repository contains source artifacts for building the docs for
`AIXpert`.

What follow's next in this README is a guide for those who are interested in building
and serving the docs locally. You may be interested to do so if you are contributing
to AIXpert and need to make appropriate changes to the documentation.

## Build Docs
This repository uses [MkDocs](https://www.mkdocs.org/) with the
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.

In order to build the documentation, install the documentation dependencies as mentioned
in the README, then run the command:

```bash
mkdocs build
```

If you're making changes to the docs, and want to serve them locally on your machine,
then you can use this command instead:

```bash
mkdocs serve
```

The above will launch the docs locally on `http://127.0.0.1:8000`, which you can
enter into your browser of choice. Conveniently, this process also watches for any
changes you make to the docs and will update them as they occur.

You can configure the documentation by updating the `mkdocs.yml` file at the root of
your repository. The markdown files in the `docs` directory can be updated to reflect
the project's documentation.
