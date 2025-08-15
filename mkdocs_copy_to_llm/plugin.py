import os
import shutil
from typing import Any, Optional

from mkdocs import utils
from mkdocs.config import Config, config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin

from .exceptions import (
    AssetNotFoundError,
    AssetProcessingError,
    BuildError,
    CopyToLLMError,
)
from .minify import minify_css, minify_js, should_minify
from .validation import sanitize_css_value, validate_color, validate_url


class CopyToLLMPluginConfig(Config):
    button_bg_color = config_options.Type(str, default="")
    button_hover_color = config_options.Type(str, default="")
    toast_bg_color = config_options.Type(str, default="")
    toast_text_color = config_options.Type(str, default="")
    repo_url = config_options.Type(str, default="")
    minify = config_options.Type(bool, default=True)
    analytics = config_options.Type(bool, default=False)
    buttons = config_options.Type(
        dict,
        default={
            "copy_page": True,
            "copy_markdown_link": True,
            "view_as_markdown": True,
            "open_in_chatgpt": True,
            "open_in_claude": True,
        },
    )


class CopyToLLMPlugin(BasePlugin[CopyToLLMPluginConfig]):
    """
    MkDocs plugin to add 'Copy to LLM' buttons to documentation
    """

    def __init__(self) -> None:
        self.js_path: str = ""
        self.css_path: str = ""

    def _validate_config(self) -> None:
        """Validate plugin configuration."""
        # Validate color configurations
        if self.config.get("button_bg_color"):
            validate_color(self.config["button_bg_color"], "button_bg_color")

        if self.config.get("button_hover_color"):
            validate_color(self.config["button_hover_color"], "button_hover_color")

        if self.config.get("toast_bg_color"):
            validate_color(self.config["toast_bg_color"], "toast_bg_color")

        if self.config.get("toast_text_color"):
            validate_color(self.config["toast_text_color"], "toast_text_color")

        # Validate repository URL
        if self.config.get("repo_url") and not validate_url(self.config["repo_url"]):
            raise BuildError(f"Invalid repository URL: {self.config['repo_url']}")

    def on_config(self, config: MkDocsConfig) -> Optional[MkDocsConfig]:
        """
        Called after the user configuration is loaded
        """
        try:
            # Validate configuration
            self._validate_config()

            # Add our JS to extra_javascript if it exists
            if "extra_javascript" not in config:
                config["extra_javascript"] = []

            # Add our CSS to extra_css if it exists
            if "extra_css" not in config:
                config["extra_css"] = []

            # We'll inject these paths later when we copy the files
            self.js_path = "assets/copy-to-llm/copy-to-llm.js"
            self.css_path = "assets/copy-to-llm/copy-to-llm.css"

            config["extra_javascript"].append(self.js_path)
            config["extra_css"].append(self.css_path)

            # Add custom CSS if colors are configured
            custom_css = self._generate_custom_css()
            if custom_css:
                # Add custom CSS after our main CSS
                config["extra_css"].append("assets/copy-to-llm/copy-to-llm-custom.css")

            return config

        except Exception as e:
            utils.log.error(f"Copy to LLM plugin configuration error: {e}")
            raise

    def _generate_custom_css(self) -> str:
        """Generate custom CSS based on configuration"""
        css_parts = []

        if self.config.get("button_bg_color"):
            color = sanitize_css_value(self.config["button_bg_color"])
            css_parts.append(f"--copy-to-llm-button-bg: {color};")

        if self.config.get("button_hover_color"):
            color = sanitize_css_value(self.config["button_hover_color"])
            css_parts.append(f"--copy-to-llm-button-hover: {color};")

        if self.config.get("toast_bg_color"):
            color = sanitize_css_value(self.config["toast_bg_color"])
            css_parts.append(f"--copy-to-llm-toast-bg: {color};")

        if self.config.get("toast_text_color"):
            color = sanitize_css_value(self.config["toast_text_color"])
            css_parts.append(f"--copy-to-llm-toast-text: {color};")

        if css_parts:
            return f":root {{\n  {' '.join(css_parts)}\n}}"
        return ""

    def on_pre_build(self, config: MkDocsConfig) -> None:
        """
        Called before the build process starts
        """
        try:
            # Copy our assets to the docs directory so they're included in the build
            docs_dir: str = config["docs_dir"]
            plugin_dir: str = os.path.dirname(os.path.abspath(__file__))

            # Create an assets directory in docs
            assets_dir: str = os.path.join(docs_dir, "assets", "copy-to-llm")
            os.makedirs(assets_dir, exist_ok=True)

            # Process JS file
            js_src: str = os.path.join(plugin_dir, "assets", "js", "copy-to-llm.js")
            if not os.path.exists(js_src):
                raise AssetNotFoundError(f"JavaScript file not found: {js_src}")

            js_dest: str = os.path.join(assets_dir, "copy-to-llm.js")

            try:
                # Read and optionally minify JS
                with open(js_src, encoding="utf-8") as f:
                    js_content = f.read()

                # Process button visibility by modifying the JS
                buttons_config = self.config.get("buttons", {})

                # Replace the button visibility checks based on config
                if buttons_config.get("open_in_chatgpt") is False:
                    # Replace the ChatGPT button block with a comment
                    js_content = js_content.replace(
                        "if (true) { // open_in_chatgpt button",
                        "if (false) { // open_in_chatgpt button disabled",
                    )

                if buttons_config.get("open_in_claude") is False:
                    # Replace the Claude button block with a comment
                    js_content = js_content.replace(
                        "if (true) { // open_in_claude button",
                        "if (false) { // open_in_claude button disabled",
                    )

                if buttons_config.get("copy_markdown_link") is False:
                    js_content = js_content.replace(
                        "if (true) { // copy_markdown_link button",
                        "if (false) { // copy_markdown_link button disabled",
                    )

                if buttons_config.get("view_as_markdown") is False:
                    js_content = js_content.replace(
                        "if (true) { // view_as_markdown button",
                        "if (false) { // view_as_markdown button disabled",
                    )

                if buttons_config.get("copy_page") is False:
                    js_content = js_content.replace(
                        "if (false) { // copy_page button disabled check",
                        "if (true) { // copy_page button disabled",
                    )

                if self.config.get("minify", True) and should_minify(dict(config)):
                    js_content = minify_js(js_content)
                    utils.log.info("Minified Copy to LLM JavaScript")

                with open(js_dest, "w", encoding="utf-8") as f:
                    f.write(js_content)

                utils.log.info(f"Processed Copy to LLM JS to {js_dest}")
            except Exception as e:
                raise AssetProcessingError(f"Failed to process JavaScript: {e}") from e

            # Process CSS file
            css_src: str = os.path.join(plugin_dir, "assets", "css", "copy-to-llm.css")
            if not os.path.exists(css_src):
                raise AssetNotFoundError(f"CSS file not found: {css_src}")

            css_dest: str = os.path.join(assets_dir, "copy-to-llm.css")

            try:
                # Read and optionally minify CSS
                with open(css_src, encoding="utf-8") as f:
                    css_content = f.read()

                if self.config.get("minify", True) and should_minify(dict(config)):
                    css_content = minify_css(css_content)
                    utils.log.info("Minified Copy to LLM CSS")

                with open(css_dest, "w", encoding="utf-8") as f:
                    f.write(css_content)

                utils.log.info(f"Processed Copy to LLM CSS to {css_dest}")
            except Exception as e:
                raise AssetProcessingError(f"Failed to process CSS: {e}") from e

            # Create a custom CSS file if needed
            custom_css = self._generate_custom_css()
            if custom_css:
                custom_css_path = os.path.join(assets_dir, "copy-to-llm-custom.css")
                try:
                    with open(custom_css_path, "w", encoding="utf-8") as f:
                        f.write(custom_css)
                    utils.log.info(f"Created custom CSS file at {custom_css_path}")
                except Exception as e:
                    raise AssetProcessingError(
                        f"Failed to create custom CSS: {e}"
                    ) from e

        except CopyToLLMError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            raise BuildError(f"Error during pre-build: {e}") from e

    def on_page_content(
        self, html: str, page: Any, config: MkDocsConfig, files: Any
    ) -> str:
        """
        Called after the page content is rendered
        """
        meta_tags = []

        if self.config.get("repo_url"):
            # Inject repository URL as a meta tag
            repo_url = self.config["repo_url"]
            meta_tags.append(
                f'<meta name="mkdocs-copy-to-llm-repo-url" content="{repo_url}">'
            )

        # Always inject the site name
        site_name = config.get("site_name", "")
        meta_tags.append(f'<meta name="mkdocs-site-name" content="{site_name}">')

        # Inject analytics configuration
        analytics_enabled = "true" if self.config.get("analytics", False) else "false"
        meta_tags.append(
            f'<meta name="mkdocs-copy-to-llm-analytics" content="{analytics_enabled}">'
        )

        # Insert all meta tags after <head> tag
        meta_tags_str = "\n".join(meta_tags)
        html = html.replace("<head>", f"<head>\n{meta_tags_str}", 1)

        return html

    def on_post_build(self, config: MkDocsConfig) -> None:
        """
        Called after the build is complete - clean up temporary files
        """
        # Clean up the temporary assets we copied to docs_dir
        docs_dir: str = config["docs_dir"]
        assets_dir: str = os.path.join(docs_dir, "assets", "copy-to-llm")

        if os.path.exists(assets_dir):
            shutil.rmtree(assets_dir)
            utils.log.info("Cleaned up temporary Copy to LLM assets")
