# Contributing

## Local developer loop

```bash
uv sync --all-extras
uv run pytest
```

## Style and quality

The project uses Ruff and pytest as part of the development extras.

## Suggested contribution workflow

1. Add or update tests first.
2. Implement code changes.
3. Run tests and check generated result files if behavior changed.
4. Update docs for user-visible features (CLI flags, metrics, exports).

For repository policies and release process, see `CONTRIBUTING.md` and `CHANGELOG.md` in the project root.
