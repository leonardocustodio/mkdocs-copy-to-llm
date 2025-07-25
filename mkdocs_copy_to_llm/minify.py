"""Asset minification utilities for the Copy to LLM plugin."""

from typing import Any

from mkdocs import utils


def minify_js(content: str) -> str:
    """
    Minify JavaScript content.

    Args:
        content: JavaScript content to minify

    Returns:
        Minified JavaScript content
    """
    try:
        from jsmin import jsmin  # type: ignore[import-untyped]

        return str(jsmin(content))
    except ImportError:
        utils.log.info("jsmin not installed. Install with: pip install jsmin")
        return content
    except Exception as e:
        utils.log.error(f"Error minifying JavaScript: {e}")
        return content


def minify_css(content: str) -> str:
    """
    Minify CSS content.

    Args:
        content: CSS content to minify

    Returns:
        Minified CSS content
    """
    try:
        from csscompressor import compress  # type: ignore[import-untyped]

        return str(compress(content))
    except ImportError:
        utils.log.info(
            "csscompressor not installed. Install with: pip install csscompressor"
        )
        return content
    except Exception as e:
        utils.log.error(f"Error minifying CSS: {e}")
        return content


def should_minify(config: dict[str, Any]) -> bool:
    """
    Check if minification should be performed based on configuration.

    Args:
        config: MkDocs configuration dictionary

    Returns:
        True if minification should be performed
    """
    # Check if we're in development mode
    if config.get("dev_addr"):
        return False

    # Check plugin-specific setting
    return bool(config.get("plugins", {}).get("copy-to-llm", {}).get("minify", True))
