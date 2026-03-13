# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.3] - 2026-03-09

### Added
- Comprehensive test suite achieving 100% code coverage
- Test coverage for `cli.py` module (21 tests)
- Test coverage for `logging.py` module (13 tests)
- Additional test coverage for `cloudflare_exporter.py` (edge cases)
- Test fixtures in `tests/data/` directory for better test data management
- Centralized pytest fixtures in `conftest.py`

### Changed
- Improved test architecture with proper fixture organization
- All test data now stored in JSON/YAML files rather than embedded in test code

### Testing
- Total test count: 94 tests
- Code coverage: 80% → 100%
  - `cli.py`: 0% → 100%
  - `logging.py`: 0% → 100%
  - `cloudflare_exporter.py`: 98% → 100%

## [0.4.2] - Previous Release

(See git history for earlier changes)
