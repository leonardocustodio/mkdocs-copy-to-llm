# MkDocs Copy to LLM Plugin

[![Tests](https://github.com/leonardocustodio/mkdocs-copy-to-llm/actions/workflows/tests.yml/badge.svg)](https://github.com/leonardocustodio/mkdocs-copy-to-llm/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/leonardocustodio/mkdocs-copy-to-llm/branch/main/graph/badge.svg)](https://codecov.io/gh/leonardocustodio/mkdocs-copy-to-llm)
[![PyPI version](https://badge.fury.io/py/mkdocs-copy-to-llm.svg)](https://badge.fury.io/py/mkdocs-copy-to-llm)
[![Python versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://pypi.org/project/mkdocs-copy-to-llm/)

A MkDocs plugin that adds "Copy to LLM" buttons to your documentation, making it easy to copy code blocks and entire pages in formats optimized for Large Language Models (LLMs).

This package was inspired by [Docus](https://github.com/nuxtlabs/docus) by NuxtLabs and made for [Polkadot Documentation](https://docs.polkadot.com).

## Features

- **Copy entire page** — Adds a split button at the top of each page with multiple copy options:
  - Copy page content as Markdown
  - Copy markdown link
  - Open in ChatGPT
  - Open in Claude
  - View raw markdown
- **Smart formatting** — Automatically formats content with proper context for LLM consumption
- **Visual feedback** — Shows success indicators and toast notifications
- **Mobile responsive** — Works seamlessly on all device sizes

## Installation

Install the plugin using pip:

```bash
pip install mkdocs-copy-to-llm
```

### Optional Dependencies

For asset minification in production builds:

```bash
pip install mkdocs-copy-to-llm[minify]
# or separately:
pip install jsmin csscompressor
```

## Configuration

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - copy-to-llm
```

That's it! The plugin will automatically add copy buttons to all your pages and code blocks.

### Configuration Options (Optional)

#### Color Customization

You can customize the colors to match your theme:

```yaml
plugins:
  - copy-to-llm:
      button_bg_color: "#ffffff"        # Button background color
      button_hover_color: "#0969da"     # Button hover color
      toast_bg_color: "#0969da"         # Toast notification background
      toast_text_color: "#ffffff"       # Toast notification text color
```

Colors can be specified as:
- Hex values: `#0969da` or `#09d`
- RGB values: `rgb(9, 105, 218)` or `rgba(9, 105, 218, 0.5)`
- CSS color names: `blue`, `red`, `darkslategray`, etc.
- CSS variables: `var(--md-primary-fg-color)`

The plugin validates all color values and will show an error if an invalid format is provided.

Example configurations for popular themes:

**Material for MkDocs:**
```yaml
plugins:
  - copy-to-llm:
      button_hover_color: "var(--md-primary-fg-color)"
      toast_bg_color: "var(--md-primary-fg-color)"
```

**MkDocs Default Theme:**
```yaml
plugins:
  - copy-to-llm:
      button_bg_color: "#f5f5f5"
      button_hover_color: "#3f51b5"
      toast_bg_color: "#3f51b5"
```

#### Repository URL Configuration

For the "Copy Markdown link" and "Open in ChatGPT/Claude" features to work correctly, you can specify your repository's raw content URL:

```yaml
plugins:
  - copy-to-llm:
      repo_url: "https://raw.githubusercontent.com/owner/repo/branch"
```

If not configured, the plugin will try to:
1. Detect the repository URL from edit links in your theme
2. Use repository links found on the page
3. Fall back to constructing URLs based on the current path

**Note**: The URL should point to the raw content base URL without the trailing slash. For GitHub repositories, this is typically `https://raw.githubusercontent.com/owner/repo/branch`.

#### Asset Minification

The plugin can automatically minify JavaScript and CSS files in production builds when the optional dependencies are installed:

```bash
# Install minification dependencies (optional)
pip install jsmin csscompressor
```

```yaml
plugins:
  - copy-to-llm:
      minify: true  # Default is true
```

Minification is automatically disabled when running `mkdocs serve` for easier debugging. If the minification libraries are not installed, the plugin will work normally but without minification.

#### Analytics Integration

Track copy events to understand how users interact with your documentation:

```yaml
plugins:
  - copy-to-llm:
      analytics: true  # Default is false
```

When enabled, the plugin will send copy events to your analytics platform (if configured):
- **Event name**: `copy_to_llm`
- **Event category**: `engagement`
- **Event label**: `code_block`, `page_content`, `markdown_content`, or `markdown_link`
- **Event value**: Length of copied content

Supported analytics platforms:
- Google Analytics (gtag.js)
- Plausible Analytics

**Important**: Analytics tracking is opt-in and disabled by default. The plugin will only track events when:
1. The `analytics` option is explicitly set to `true` in your configuration
2. An analytics platform is already configured on your site

This ensures user privacy is respected and no tracking occurs without explicit consent.

## How It Works

The plugin automatically:
1. Injects the necessary JavaScript and CSS files
2. Adds a split button to the main page title
3. Handles all copy operations with proper formatting

## Customization

The plugin uses CSS variables from your MkDocs theme. It integrates seamlessly with the Material theme for MkDocs.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/leonardocustodio/mkdocs-copy-to-llm.git
cd mkdocs-copy-to-llm

# Install development dependencies
make install-dev
```

### Available Commands

```bash
make help          # Show all available commands
make test          # Run tests with coverage
make lint          # Run linting checks
make format        # Format code with Ruff
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
pre-commit install  # Install hooks (done automatically by make install-dev)
pre-commit run --all-files  # Run all hooks manually
```

## Accessibility

The plugin is designed with accessibility in mind:

- All buttons have proper ARIA labels
- Full keyboard navigation support
- Screen reader friendly
- Focus management for dropdown menus
- Escape key closes dropdowns

## License

Apache License 2.0
