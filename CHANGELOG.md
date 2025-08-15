# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] - 2025-01-15

### Fixed
- Fixed button visibility configuration not working properly when `open_in_chatgpt` or `open_in_claude` were set to `false`
- Improved boolean parsing in JavaScript to handle string values ("false", "0") in addition to boolean values
- The configuration parser now correctly recognizes multiple falsy representations ensuring buttons are properly hidden

## [0.2.2] - Previous Release

### Added
- Button visibility configuration options
- Support for hiding individual buttons in the dropdown menu

## [0.2.1] - Previous Release

### Added
- Initial support for customizable buttons
- Copy to LLM functionality
- ChatGPT and Claude integration buttons