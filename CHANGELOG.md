# Changelog

All notable changes to this project are documented in this file.

The format is inspired by Keep a Changelog and follows Semantic Versioning.

## [1.1.0] - 2026-03-27

### Added
- Added a new `cli run` command to execute evaluation experiments directly from the CLI.
- Added static dashboard export support through `cli dashboard --static`.
- Added parallel experiment execution support for running multiple evaluation files.

### Changed
- Simplified metric discovery and selection workflow.
- Migrated project setup to full `uv` + `pyproject.toml` workflow.
- Updated citation metadata (authors/version) and project publication metadata.

### Fixed
- Fixed dashboard metric display issues.
- Added endpoint availability checks during SPARQL endpoint backend initialization.
- Added QCan BLEU dependency checks to fail early when required resources are missing.

### Docs
- Added Zenodo DOI to project documentation.

## [1.0.2] - 2026-03-16

### Changed
- Updated README with installation and usage improvements.
- Removed unused packages from project setup.
- Refreshed repository presentation (logo and badges).

### Fixed
- Fixed dashboard behavior when no data is available.

## [1.0.0] - 2026-03-12

### Added
- Initial public release of T2S-Metrics.
- Modular evaluation toolkit for text-to-SPARQL with configurable metrics.
- Query execution backends for local RDF files and SPARQL endpoints.
- Dashboard entry point via CLI for visual analysis of result files.
- Dataset/evaluation scaffolding for benchmark experiments.
