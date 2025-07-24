# MkDocs Copy to LLM Plugin

A MkDocs plugin that adds "Copy to LLM" buttons to your documentation, making it easy to copy code blocks and entire pages in formats optimized for Large Language Models (LLMs).

## Features

- **Copy to LLM buttons for code blocks** - Adds a button next to each code block to copy the code with context
- **Copy entire page** - Adds a split button at the top of each page with multiple copy options:
  - Copy page content as markdown
  - Copy markdown link
  - Open in ChatGPT
  - Open in Claude
  - View raw markdown
- **Smart formatting** - Automatically formats content with proper context for LLM consumption
- **Visual feedback** - Shows success indicators and toast notifications
- **Mobile responsive** - Works seamlessly on all device sizes

## Installation

Install the plugin using pip:

```bash
pip install mkdocs-copy-to-llm
```

## Configuration

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - search
  - copy-to-llm
```

### Options

The plugin supports the following configuration options:

```yaml
plugins:
  - copy-to-llm:
      enabled: true  # Enable/disable the plugin (default: true)
      code_blocks: true  # Add buttons to code blocks (default: true)
      page_button: true  # Add button to page headers (default: true)
```

## How It Works

The plugin automatically:
1. Injects the necessary JavaScript and CSS files
2. Adds copy buttons to code blocks
3. Adds a split button to the main page title
4. Handles all copy operations with proper formatting

## Customization

The plugin uses CSS variables from your MkDocs theme. It integrates seamlessly with Material for MkDocs theme.

## License

Apache License 2.0