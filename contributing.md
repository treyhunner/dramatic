# Contributing to dramatic

## Prerequisites

- [hatch](https://hatch.pypa.io/) for environment and dependency management
- [just](https://github.com/casey/just) for task running

## Getting Started

Install dependencies:

```console
just setup
```

## Running Tests

Run tests:

```console
just test
```

Run tests with coverage and generate report:

```console
just test-cov
```

Run HTML code coverage report and open in a web browser:

```console
just test-html
```

Run tests on all supported Python versions:

```console
just test-all
```

Run tests on all supported Python versions in parallel:

```console
just test-all-parallel
```

## Code Quality

Run linting and auto-format code:

```console
just fmt
```

Run all quality checks and tests:

```console
just check
```

## Tools Used

These tools are configured in the project:

- [hatch](https://hatch.pypa.io/) for environment and build management
- [pytest](https://docs.pytest.org/) for testing
- [ruff](https://docs.astral.sh/ruff/) for linting & auto-formatting Python code
- [coverage](https://coverage.readthedocs.io) for measuring code coverage

## Development Workflow

The typical development workflow is:

1. Make your changes
2. Run `just check` to format and lint and run tests on all supported Python versions
3. Commit your changes
