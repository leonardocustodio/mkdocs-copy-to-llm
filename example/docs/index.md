# MkDocs Copy to LLM example

Welcome to our example documentation showcasing the **MkDocs Copy to LLM** plugin! This documentation demonstrates how the plugin enhances your documentation with AI-friendly copy capabilities.

## Features Demo

Try the copy buttons at the top of this page! You'll see options to:

- 📄 **Copy entire page** as markdown
- 🔗 **Copy markdown link** to this page
- 👁️ **View as markdown** in a new window
- 🤖 **Open in ChatGPT** with context
- 🧠 **Open in Claude** with context

## What is MkDocs Copy to LLM?

The MkDocs Copy to LLM plugin adds intelligent copy functionality to your documentation, making it easy for users to share content with Large Language Models (LLMs) like ChatGPT and Claude.

### Key Benefits

- **🚀 One-click copying** - Users can copy entire pages or specific sections with proper formatting
- **🎯 Context preservation** - Automatically includes page title, section, and URL for better LLM understanding
- **📱 Mobile friendly** - Responsive design works on all devices
- **🎨 Customizable** - Match your documentation theme with custom colors
- **📊 Analytics ready** - Track how users interact with your documentation

## Installation

Installing the plugin is straightforward:

```bash
# Install the plugin
pip install mkdocs-copy-to-llm

# Optional: Install with minification support
pip install mkdocs-copy-to-llm[minify]
```

Then add it to your `mkdocs.yml`:

```yaml
plugins:
  - copy-to-llm:
      button_bg_color: "#3f51b5"
      button_hover_color: "#1976d2"
      toast_bg_color: "#4caf50"
      toast_text_color: "#ffffff"
```

## Why This Matters

In the age of AI assistants, making documentation AI-friendly is crucial. This plugin bridges the gap between traditional documentation and modern AI workflows by:

1. **Preserving context** when copying content
2. **Formatting for LLMs** automatically
3. **Reducing friction** in the user workflow
4. **Enabling better AI responses** with proper context

## Community

Join our community and contribute:

- 🐛 [Report Issues](https://github.com/leonardocustodio/mkdocs-copy-to-llm/issues)
- 🤝 [Contribute](https://github.com/leonardocustodio/mkdocs-copy-to-llm/pulls)

---

!!! tip "Pro Tip"
    Use the keyboard shortcut `Ctrl+Shift+C` (or `Cmd+Shift+C` on Mac) to quickly copy the current page!

!!! info "Note"
    This example documentation is using the Material for MkDocs theme with the Copy to LLM plugin enabled. The copy buttons you see are added automatically by the plugin!
