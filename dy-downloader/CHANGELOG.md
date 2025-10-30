# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release of dy-downloader as an independent package
- Complete async architecture using aiohttp, aiofiles, and aiosqlite
- Single video and batch video download support
- User profile download with pagination support
- Gallery/image post download support
- Incremental download mechanism with SQLite database tracking
- Rich CLI interface with progress display
- Flexible configuration system (YAML file, environment variables, CLI arguments)
- Cookie management system
- Rate limiting and intelligent retry mechanisms
- Configurable concurrent downloads with queue management
- Metadata export to JSON
- Download filtering by time range
- XBogus signature generation for API requests (Apache 2.0 licensed code from Evil0ctal)
- Comprehensive logging system with configurable log levels
- File organization with configurable folder structure
- Support for downloading video covers, music, and avatars
- Automatic short URL resolution

### Features
- **Packaging**: Proper Python package with pyproject.toml
- **Entry Points**: Multiple ways to run (`python -m dy_downloader`, `dy-downloader` command, `run.py`)
- **Configuration**: Log level, timeout, and filename length are now configurable
- **Cookie Storage**: Cookies now saved to `config/cookies.json` by default instead of root
- **Error Handling**: Improved error handling with specific exception types
- **Validation**: Better input validation for URLs, filenames, and date formats
- **Documentation**: Comprehensive README with installation and usage instructions
- **Testing**: Unit tests with pytest covering core functionality

### Technical Details
- Python 3.8+ support
- Async/await throughout for performance
- Template Method and Factory design patterns
- Modular architecture with clear separation of concerns
- SQLite for download history and deduplication
- Apache 2.0 license (compatible with XBogus implementation)

## [Unreleased]

### Planned Features
- Additional downloader types (collections, playlists, live streams)
- Proxy support
- Resume interrupted downloads
- Web UI interface
- Multi-account support
- Cloud storage integration
- Docker deployment support
- More comprehensive integration tests

