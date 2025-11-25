"""Test cases for the Copy to LLM plugin."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from mkdocs.config import Config

from mkdocs_copy_to_llm.exceptions import (
    AssetNotFoundError,
    AssetProcessingError,
    BuildError,
    ColorValidationError,
)
from mkdocs_copy_to_llm.plugin import CopyToLLMPlugin, CopyToLLMPluginConfig


class TestCopyToLLMPlugin:
    """Test cases for CopyToLLMPlugin."""

    def test_plugin_initialization(self) -> None:
        """Test that the plugin initializes correctly."""
        plugin = CopyToLLMPlugin()
        assert plugin.js_path == ""
        assert plugin.css_path == ""

    def test_config_defaults(self) -> None:
        """Test that the config has correct defaults."""
        config = CopyToLLMPluginConfig()
        assert config.button_bg_color == ""
        assert config.button_hover_color == ""
        assert config.toast_bg_color == ""
        assert config.toast_text_color == ""
        assert config.repo_url == ""
        assert config.base_path == ""
        assert config.minify is True
        assert config.analytics is False

    def test_on_config(self) -> None:
        """Test the on_config hook."""
        plugin = CopyToLLMPlugin()
        config = Config(schema=())

        # Call on_config
        result = plugin.on_config(config)

        # Check that extra_javascript and extra_css were added
        assert "extra_javascript" in result
        assert "extra_css" in result
        assert "assets/copy-to-llm/copy-to-llm.js" in result["extra_javascript"]
        assert "assets/copy-to-llm/copy-to-llm.css" in result["extra_css"]

    def test_custom_css_generation(self) -> None:
        """Test custom CSS generation with color configuration."""
        plugin = CopyToLLMPlugin()
        plugin.config = {
            "button_bg_color": "#ffffff",
            "button_hover_color": "#0969da",
            "toast_bg_color": "#0969da",
            "toast_text_color": "#ffffff",
        }

        css = plugin._generate_custom_css()
        assert "--copy-to-llm-button-bg: #ffffff;" in css
        assert "--copy-to-llm-button-hover: #0969da;" in css
        assert "--copy-to-llm-toast-bg: #0969da;" in css
        assert "--copy-to-llm-toast-text: #ffffff;" in css

    def test_custom_css_generation_empty(self) -> None:
        """Test custom CSS generation with no color configuration."""
        plugin = CopyToLLMPlugin()
        plugin.config = {}

        css = plugin._generate_custom_css()
        assert css == ""

    def test_on_post_page_with_repo_url(self) -> None:
        """Test the on_post_page hook with repo URL configuration.

        Issue #18 fix: Changed from on_page_content to on_post_page hook.
        This ensures meta tags are injected after the full page HTML is rendered,
        which is necessary for themes like Material for MkDocs that don't provide
        the <head> tag at the on_page_content stage.
        """
        plugin = CopyToLLMPlugin()
        plugin.config = {"repo_url": "https://raw.githubusercontent.com/test/repo/main"}

        html = "<head></head><body>Test</body>"
        config = Config(schema=())
        config["site_name"] = "Test Site"

        result = plugin.on_post_page(html, None, config)

        assert 'meta name="mkdocs-copy-to-llm-repo-url"' in result
        assert 'content="https://raw.githubusercontent.com/test/repo/main"' in result
        assert 'meta name="mkdocs-site-name"' in result
        assert 'content="Test Site"' in result

    def test_on_post_page_without_repo_url(self) -> None:
        """Test the on_post_page hook without repo URL configuration.

        Issue #18 fix: Verifies backward compatibility - the plugin should work
        without a repo_url configured, just without the repo URL meta tag.
        """
        plugin = CopyToLLMPlugin()
        plugin.config = {}

        html = "<head></head><body>Test</body>"
        config = Config(schema=())
        config["site_name"] = "Test Site"

        result = plugin.on_post_page(html, None, config)

        assert 'meta name="mkdocs-copy-to-llm-repo-url"' not in result
        assert 'meta name="mkdocs-site-name"' in result
        assert 'content="Test Site"' in result

    def test_on_post_page_with_base_path(self) -> None:
        """Test the on_post_page hook with base_path configuration.

        Issue #18 fix: New base_path config option allows sites deployed to
        subdirectories (e.g., /docs/) to strip that prefix when constructing
        repository URLs. This test verifies the base_path meta tag is injected.
        """
        plugin = CopyToLLMPlugin()
        plugin.config = {
            "repo_url": "https://raw.githubusercontent.com/test/repo/main",
            "base_path": "/docs/",
        }

        html = "<head></head><body>Test</body>"
        config = Config(schema=())
        config["site_name"] = "Test Site"

        result = plugin.on_post_page(html, None, config)

        assert 'meta name="mkdocs-copy-to-llm-base-path"' in result
        assert 'content="/docs/"' in result
        assert 'meta name="mkdocs-copy-to-llm-repo-url"' in result

    def test_on_post_page_without_base_path(self) -> None:
        """Test the on_post_page hook without base_path configuration.

        Issue #18 fix: Verifies that base_path is optional and the plugin works
        correctly when it's not configured (no base_path meta tag injected).
        """
        plugin = CopyToLLMPlugin()
        plugin.config = {"repo_url": "https://raw.githubusercontent.com/test/repo/main"}

        html = "<head></head><body>Test</body>"
        config = Config(schema=())
        config["site_name"] = "Test Site"

        result = plugin.on_post_page(html, None, config)

        assert 'meta name="mkdocs-copy-to-llm-base-path"' not in result
        assert 'meta name="mkdocs-copy-to-llm-repo-url"' in result

    def test_on_pre_build(self) -> None:
        """Test the on_pre_build hook."""
        plugin = CopyToLLMPlugin()
        plugin.config = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Call on_pre_build
            plugin.on_pre_build(config)

            # Check that the assets directory was created
            assets_dir = Path(tmpdir) / "assets" / "copy-to-llm"
            assert assets_dir.exists()

    def test_on_post_build(self) -> None:
        """Test the on_post_build hook."""
        plugin = CopyToLLMPlugin()

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Create a test assets directory
            assets_dir = Path(tmpdir) / "assets" / "copy-to-llm"
            assets_dir.mkdir(parents=True, exist_ok=True)

            # Create a test file
            test_file = assets_dir / "test.txt"
            test_file.write_text("test")

            assert assets_dir.exists()

            # Call on_post_build
            plugin.on_post_build(config)

            # Check that the assets directory was removed
            assert not assets_dir.exists()

    def test_color_validation_error(self) -> None:
        """Test that invalid colors raise validation errors."""
        plugin = CopyToLLMPlugin()
        plugin.config = {"button_bg_color": "#INVALID"}

        with pytest.raises(ColorValidationError) as exc_info:
            plugin._validate_config()

        assert "button_bg_color" in str(exc_info.value)
        assert "#INVALID" in str(exc_info.value)

    def test_invalid_repo_url(self) -> None:
        """Test that invalid repository URLs raise errors."""
        plugin = CopyToLLMPlugin()
        plugin.config = {"repo_url": "not-a-url"}

        with pytest.raises(BuildError) as exc_info:
            plugin._validate_config()

        assert "Invalid repository URL" in str(exc_info.value)

    def test_on_config_with_validation_error(self) -> None:
        """Test on_config with validation error."""
        plugin = CopyToLLMPlugin()
        plugin.config = {"button_hover_color": "invalid-color"}
        config = Config(schema=())

        with pytest.raises(ColorValidationError):
            plugin.on_config(config)

    def test_on_pre_build_missing_assets(self) -> None:
        """Test on_pre_build when assets are missing."""
        plugin = CopyToLLMPlugin()
        plugin.config = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Mock the plugin directory to a non-existent path
            with patch("os.path.dirname") as mock_dirname:
                mock_dirname.return_value = "/non/existent/path"

                with pytest.raises(AssetNotFoundError) as exc_info:
                    plugin.on_pre_build(config)

                assert "JavaScript file not found" in str(exc_info.value)

    def test_css_sanitization(self) -> None:
        """Test that CSS values are sanitized."""
        plugin = CopyToLLMPlugin()
        plugin.config = {
            "button_bg_color": "#FFFFFF; malicious: code",
            "toast_bg_color": "rgb(255, 0, 0)",
        }

        css = plugin._generate_custom_css()

        # Check that malicious code is removed
        assert "malicious" not in css
        assert "#FFFFFF" in css
        assert "rgb(255, 0, 0)" in css

    def test_analytics_meta_tag_enabled(self) -> None:
        """Test that analytics meta tag is injected when enabled."""
        plugin = CopyToLLMPlugin()
        plugin.config = {"analytics": True}

        html = "<head></head><body>Test</body>"
        config = Config(schema=())

        result = plugin.on_post_page(html, None, config)

        assert 'meta name="mkdocs-copy-to-llm-analytics"' in result
        assert 'content="true"' in result

    def test_analytics_meta_tag_disabled(self) -> None:
        """Test that analytics meta tag shows false when disabled."""
        plugin = CopyToLLMPlugin()
        plugin.config = {"analytics": False}

        html = "<head></head><body>Test</body>"
        config = Config(schema=())

        result = plugin.on_post_page(html, None, config)

        assert 'meta name="mkdocs-copy-to-llm-analytics"' in result
        assert 'content="false"' in result

    def test_color_validation_all_fields(self) -> None:
        """Test validation of all color fields."""
        plugin = CopyToLLMPlugin()

        # Test valid colors for all fields
        plugin.config = {
            "button_bg_color": "#123456",
            "button_hover_color": "rgb(255, 0, 0)",
            "toast_bg_color": "var(--primary)",
            "toast_text_color": "blue",
        }

        # Should not raise any errors
        plugin._validate_config()

    def test_color_validation_individual_fields(self) -> None:
        """Test that each color field is validated when present."""
        plugin = CopyToLLMPlugin()

        # Test button_hover_color validation
        plugin.config = {"button_hover_color": "#INVALID"}
        with pytest.raises(ColorValidationError) as exc_info:
            plugin._validate_config()
        assert "button_hover_color" in str(exc_info.value)

        # Test toast_bg_color validation
        plugin.config = {"toast_bg_color": "not-a-color-123"}
        with pytest.raises(ColorValidationError) as exc_info:
            plugin._validate_config()
        assert "toast_bg_color" in str(exc_info.value)

        # Test toast_text_color validation
        plugin.config = {"toast_text_color": "rgb(256, 256, 256)"}  # Invalid RGB
        with pytest.raises(ColorValidationError) as exc_info:
            plugin._validate_config()
        assert "toast_text_color" in str(exc_info.value)

    def test_on_config_error_handling(self) -> None:
        """Test on_config error handling and logging."""
        plugin = CopyToLLMPlugin()
        plugin.config = {"button_bg_color": "#INVALID"}
        config = Config(schema=())

        # Mock the logger to check error logging
        with patch("mkdocs_copy_to_llm.plugin.utils.log.error") as mock_log_error:
            with pytest.raises(ColorValidationError):
                plugin.on_config(config)

            # Check that error was logged
            mock_log_error.assert_called_once()
            assert "Copy to LLM plugin configuration error" in str(
                mock_log_error.call_args
            )

    def test_custom_css_generation_with_custom_css_file(self) -> None:
        """Test that custom CSS file path is added when custom CSS exists."""
        plugin = CopyToLLMPlugin()
        plugin.config = {"button_bg_color": "#FF0000"}
        config = Config(schema=())

        result = plugin.on_config(config)

        # Check that custom CSS file is added
        assert "assets/copy-to-llm/copy-to-llm-custom.css" in result["extra_css"]

    def test_on_pre_build_with_minification_disabled(self) -> None:
        """Test on_pre_build when minification is disabled."""
        plugin = CopyToLLMPlugin()
        plugin.config = {"minify": False}

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Create source files
            plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
            js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"
            css_src = plugin_dir / "assets" / "css" / "copy-to-llm.css"

            if js_src.exists() and css_src.exists():
                with (
                    patch("mkdocs_copy_to_llm.plugin.minify_js") as mock_minify_js,
                    patch("mkdocs_copy_to_llm.plugin.minify_css") as mock_minify_css,
                ):
                    plugin.on_pre_build(config)

                    # Minification should not be called when disabled
                    mock_minify_js.assert_not_called()
                    mock_minify_css.assert_not_called()

    def test_on_pre_build_css_file_not_found(self) -> None:
        """Test on_pre_build when CSS file is not found."""
        plugin = CopyToLLMPlugin()
        plugin.config = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Mock js file exists but css doesn't
            with patch("os.path.exists") as mock_exists:
                mock_exists.side_effect = lambda path: "copy-to-llm.js" in path

                with pytest.raises(AssetNotFoundError) as exc_info:
                    plugin.on_pre_build(config)

                assert "CSS file not found" in str(exc_info.value)

    def test_on_pre_build_js_processing_error(self) -> None:
        """Test on_pre_build when JS processing fails."""
        plugin = CopyToLLMPlugin()
        plugin.config = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # First create the assets directory
            assets_dir = Path(tmpdir) / "assets" / "copy-to-llm"
            assets_dir.mkdir(parents=True, exist_ok=True)

            # Create a mock scenario where file exists but reading fails
            with (
                patch("os.path.exists", return_value=True),
                patch("builtins.open", side_effect=OSError("Permission denied")),
            ):
                with pytest.raises(AssetProcessingError) as exc_info:
                    plugin.on_pre_build(config)

                assert "Failed to process JavaScript" in str(exc_info.value)

    def test_on_pre_build_css_processing_error(self) -> None:
        """Test on_pre_build when CSS processing fails."""
        plugin = CopyToLLMPlugin()
        plugin.config = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir
            assets_dir = Path(tmpdir) / "assets" / "copy-to-llm"
            assets_dir.mkdir(parents=True, exist_ok=True)

            # Create real JS file but mock CSS processing
            plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
            js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"
            css_src = plugin_dir / "assets" / "css" / "copy-to-llm.css"

            if js_src.exists() and css_src.exists():
                # Mock file operations
                with patch("os.path.exists") as mock_exists:
                    mock_exists.return_value = True  # All files exist

                    original_open = open

                    def open_side_effect(path, *args, **kwargs):
                        path_str = str(path)
                        path_obj = Path(path)
                        # Allow JS operations to succeed
                        if (
                            "copy-to-llm.js" in path_str
                            and "assets/copy-to-llm" in path_str
                        ):
                            # This is writing the JS file, let it succeed
                            return original_open(path, *args, **kwargs)
                        elif path_obj == js_src:
                            # This is reading the JS source, let it succeed
                            return original_open(path, *args, **kwargs)
                        # Fail CSS operations
                        elif "copy-to-llm.css" in path_str:
                            if path_obj == css_src:
                                # Allow reading CSS source
                                return original_open(path, *args, **kwargs)
                            else:
                                # Fail writing CSS
                                raise OSError("CSS write failed")
                        return original_open(path, *args, **kwargs)

                    with patch("builtins.open", side_effect=open_side_effect):
                        with pytest.raises(AssetProcessingError) as exc_info:
                            plugin.on_pre_build(config)

                        assert "Failed to process CSS" in str(exc_info.value)

    def test_on_pre_build_custom_css_creation_error(self) -> None:
        """Test on_pre_build when custom CSS file creation fails."""
        plugin = CopyToLLMPlugin()
        plugin.config = {"button_bg_color": "#FF0000"}  # This triggers custom CSS

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Create source files
            plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
            js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"
            css_src = plugin_dir / "assets" / "css" / "copy-to-llm.css"

            if js_src.exists() and css_src.exists():
                # Make regular file operations succeed but custom CSS creation fail
                original_open = open
                call_count = 0

                def open_side_effect(path, *args, **kwargs):
                    nonlocal call_count
                    call_count += 1
                    if "copy-to-llm-custom.css" in str(path):
                        raise OSError("Cannot create custom CSS")
                    return original_open(path, *args, **kwargs)

                with patch("builtins.open", side_effect=open_side_effect):
                    with pytest.raises(AssetProcessingError) as exc_info:
                        plugin.on_pre_build(config)

                    assert "Failed to create custom CSS" in str(exc_info.value)

    def test_on_pre_build_unexpected_error(self) -> None:
        """Test on_pre_build with unexpected error."""
        plugin = CopyToLLMPlugin()
        plugin.config = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Raise an unexpected error
            with patch("os.makedirs", side_effect=RuntimeError("Unexpected error")):
                with pytest.raises(BuildError) as exc_info:
                    plugin.on_pre_build(config)

                assert "Error during pre-build" in str(exc_info.value)
                assert "Unexpected error" in str(exc_info.value)

    def test_custom_css_generation_with_specific_fields(self) -> None:
        """Test CSS generation with specific color fields only."""
        plugin = CopyToLLMPlugin()

        # Test with only hover color
        plugin.config = {"button_hover_color": "#00FF00"}
        css = plugin._generate_custom_css()
        assert "--copy-to-llm-button-hover: #00FF00;" in css
        assert "--copy-to-llm-button-bg:" not in css

        # Test with only toast colors
        plugin.config = {
            "toast_bg_color": "rgb(100, 100, 100)",
            "toast_text_color": "white",
        }
        css = plugin._generate_custom_css()
        assert "--copy-to-llm-toast-bg: rgb(100, 100, 100);" in css
        assert "--copy-to-llm-toast-text: white;" in css
        assert "--copy-to-llm-button-bg:" not in css
        assert "--copy-to-llm-button-hover:" not in css

    def test_on_config_with_existing_extra_assets(self) -> None:
        """Test on_config when extra_javascript and extra_css already exist."""
        plugin = CopyToLLMPlugin()
        config = Config(schema=())

        # Pre-populate extra_javascript and extra_css
        config["extra_javascript"] = ["existing.js"]
        config["extra_css"] = ["existing.css"]

        # Call on_config
        result = plugin.on_config(config)

        # Check that our assets were appended
        assert "existing.js" in result["extra_javascript"]
        assert "existing.css" in result["extra_css"]
        assert "assets/copy-to-llm/copy-to-llm.js" in result["extra_javascript"]
        assert "assets/copy-to-llm/copy-to-llm.css" in result["extra_css"]

        # Verify order - existing assets should come first
        assert result["extra_javascript"].index("existing.js") < result[
            "extra_javascript"
        ].index("assets/copy-to-llm/copy-to-llm.js")
        assert result["extra_css"].index("existing.css") < result["extra_css"].index(
            "assets/copy-to-llm/copy-to-llm.css"
        )

    def test_on_post_page_without_head_tag(self) -> None:
        """Test on_post_page when HTML has no head tag."""
        plugin = CopyToLLMPlugin()
        plugin.config = {"repo_url": "https://example.com", "analytics": True}

        html = "<body>Test content</body>"
        config = Config(schema=())
        config["site_name"] = "Test Site"

        result = plugin.on_post_page(html, None, config)

        # Should return original HTML unchanged
        assert result == html
        assert "<head>" not in result
        assert "mkdocs-copy-to-llm-repo-url" not in result

    def test_on_post_build_with_missing_assets_dir(self) -> None:
        """Test on_post_build when assets directory doesn't exist."""
        plugin = CopyToLLMPlugin()

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Assets dir doesn't exist
            assets_dir = Path(tmpdir) / "assets" / "copy-to-llm"
            assert not assets_dir.exists()

            # Call on_post_build - should not raise any errors
            plugin.on_post_build(config)

            # Still doesn't exist
            assert not assets_dir.exists()

    def test_on_pre_build_with_custom_css_success(self) -> None:
        """Test on_pre_build successfully creates custom CSS file."""
        plugin = CopyToLLMPlugin()
        plugin.config = {
            "button_bg_color": "#FF0000",
            "button_hover_color": "#CC0000",
            "toast_bg_color": "#00FF00",
            "toast_text_color": "#FFFFFF",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Create source files first
            plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
            js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"
            css_src = plugin_dir / "assets" / "css" / "copy-to-llm.css"

            # Only run test if source files exist
            if js_src.exists() and css_src.exists():
                # Call on_pre_build
                plugin.on_pre_build(config)

                # Check that custom CSS file was created
                assets_dir = Path(tmpdir) / "assets" / "copy-to-llm"
                custom_css_path = assets_dir / "copy-to-llm-custom.css"

                assert custom_css_path.exists()

                # Verify content
                content = custom_css_path.read_text()
                assert "--copy-to-llm-button-bg: #FF0000;" in content
                assert "--copy-to-llm-button-hover: #CC0000;" in content
                assert "--copy-to-llm-toast-bg: #00FF00;" in content
                assert "--copy-to-llm-toast-text: #FFFFFF;" in content

    def test_on_pre_build_with_button_config_processing(self) -> None:
        """Test that JS file is modified based on button configuration during build."""
        plugin = CopyToLLMPlugin()
        plugin.config = {
            "minify": False,  # Disable minification to test string replacements
            "buttons": {
                "open_in_chatgpt": False,
                "open_in_claude": False,
                "copy_markdown_link": False,
                "view_as_markdown": False,
                "copy_page": False,
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Create source files first
            plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
            js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"
            css_src = plugin_dir / "assets" / "css" / "copy-to-llm.css"

            # Only run test if source files exist
            if js_src.exists() and css_src.exists():
                # Call on_pre_build
                plugin.on_pre_build(config)

                # Check that JS file was created and modified
                assets_dir = Path(tmpdir) / "assets" / "copy-to-llm"
                js_dest = assets_dir / "copy-to-llm.js"

                assert js_dest.exists()

                # Verify that button conditionals were replaced
                content = js_dest.read_text()

                # Check that the ChatGPT button block is disabled
                assert "if (false) { // open_in_chatgpt button disabled" in content
                # Check that the Claude button block is disabled
                assert "if (false) { // open_in_claude button disabled" in content
                # Check that copy markdown link is disabled
                assert "if (false) { // copy_markdown_link button disabled" in content
                # Check that view as markdown is disabled
                assert "if (false) { // view_as_markdown button disabled" in content
                # Check that copy page is disabled
                assert "if (true) { // copy_page button disabled" in content

    def test_on_pre_build_with_partial_button_config_processing(self) -> None:
        """Test that only specified buttons are modified in JS file."""
        plugin = CopyToLLMPlugin()
        plugin.config = {
            "minify": False,  # Disable minification to test string replacements
            "buttons": {
                "open_in_chatgpt": False,
                "open_in_claude": False,
                # Other buttons not specified, should not be modified
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Create source files first
            plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
            js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"
            css_src = plugin_dir / "assets" / "css" / "copy-to-llm.css"

            # Only run test if source files exist
            if js_src.exists() and css_src.exists():
                # Call on_pre_build
                plugin.on_pre_build(config)

                # Check that JS file was created and modified
                assets_dir = Path(tmpdir) / "assets" / "copy-to-llm"
                js_dest = assets_dir / "copy-to-llm.js"

                assert js_dest.exists()

                # Verify that only specified button conditionals were replaced
                content = js_dest.read_text()

                # Check that the ChatGPT button block is disabled
                assert "if (false) { // open_in_chatgpt button disabled" in content
                # Check that the Claude button block is disabled
                assert "if (false) { // open_in_claude button disabled" in content

                # Check that other buttons are NOT modified (still have default)
                assert "if (true) { // copy_markdown_link button" in content
                assert "if (true) { // view_as_markdown button" in content
                # copy_page uses different logic (false means not disabled)
                assert "if (false) { // copy_page button disabled check" in content

    def test_on_pre_build_with_no_button_config(self) -> None:
        """Test that JS file is not modified when no button config is provided."""
        plugin = CopyToLLMPlugin()
        plugin.config = {
            "minify": False
        }  # No buttons configuration, but disable minification

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Create source files first
            plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
            js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"
            css_src = plugin_dir / "assets" / "css" / "copy-to-llm.css"

            # Only run test if source files exist
            if js_src.exists() and css_src.exists():
                # Call on_pre_build
                plugin.on_pre_build(config)

                # Check that JS file was created
                assets_dir = Path(tmpdir) / "assets" / "copy-to-llm"
                js_dest = assets_dir / "copy-to-llm.js"

                assert js_dest.exists()

                # Verify that button conditionals were NOT replaced
                content = js_dest.read_text()

                # Check that original conditionals are preserved
                assert "if (true) { // open_in_chatgpt button" in content
                assert "if (true) { // open_in_claude button" in content
                assert "if (true) { // copy_markdown_link button" in content
                assert "if (true) { // view_as_markdown button" in content
                assert "if (false) { // copy_page button disabled check" in content

                # Check that no buttons were disabled (no "disabled" replacements)
                assert "open_in_chatgpt button disabled" not in content
                assert "open_in_claude button disabled" not in content
                assert "copy_markdown_link button disabled" not in content
                assert "view_as_markdown button disabled" not in content
                assert (
                    'copy_page button disabled"' not in content
                )  # Note: different format

    def test_on_pre_build_with_mixed_button_config(self) -> None:
        """Test JS file modification with mixed true/false button values."""
        plugin = CopyToLLMPlugin()
        plugin.config = {
            "minify": False,  # Disable minification to test string replacements
            "buttons": {
                "open_in_chatgpt": False,
                "open_in_claude": True,  # Explicitly true, should not be modified
                "copy_markdown_link": False,
                "view_as_markdown": True,
                "copy_page": True,
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(schema=())
            config["docs_dir"] = tmpdir

            # Create source files first
            plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
            js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"
            css_src = plugin_dir / "assets" / "css" / "copy-to-llm.css"

            # Only run test if source files exist
            if js_src.exists() and css_src.exists():
                # Call on_pre_build
                plugin.on_pre_build(config)

                # Check that JS file was created and modified
                assets_dir = Path(tmpdir) / "assets" / "copy-to-llm"
                js_dest = assets_dir / "copy-to-llm.js"

                assert js_dest.exists()

                # Verify the modifications
                content = js_dest.read_text()

                # Check that false buttons are disabled
                assert "if (false) { // open_in_chatgpt button disabled" in content
                assert "if (false) { // copy_markdown_link button disabled" in content

                # Check that true buttons are NOT modified
                assert "if (true) { // open_in_claude button" in content
                assert "if (true) { // view_as_markdown button" in content
                # copy_page logic is inverted - true means don't modify
                assert "if (false) { // copy_page button disabled check" in content

    def test_javascript_dom_selector_fallbacks_function_exists(self) -> None:
        """Test that JavaScript includes getMainContentElement function.

        Issue #19 fix: The "Copy Page" button was failing when the DOM selector
        '.md-content__inner .md-typeset' didn't match different Material theme versions.

        This test verifies that a new helper function getMainContentElement() exists
        which will try multiple fallback selectors instead of just one.

        Context for next developer: This function is critical for supporting
        different Material for MkDocs theme versions, each of which may use
        different DOM structures.
        """
        plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
        js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"

        if js_src.exists():
            js_content = js_src.read_text()

            # The function should be defined in the JavaScript
            assert "function getMainContentElement()" in js_content
            # The function should be called somewhere in the code
            assert "getMainContentElement" in js_content

    def test_javascript_dom_selector_fallbacks_selectors(self) -> None:
        """Test that JavaScript includes all fallback selectors.

        Issue #19 fix: Implements multiple fallback selectors to support different
        Material theme versions. The selectors are tried in order of preference:

        1. '.md-content__inner .md-typeset' - Primary Material theme selector
        2. '.md-content__inner' - Material theme without typeset class
        3. 'article.md-content__inner' - Material theme using article tag
        4. 'main .md-typeset' - Material theme with main tag
        5. 'article' - Generic article fallback
        6. '.md-content' - Material theme content class
        7. 'main' - Final fallback to main tag

        Context for next developer: These selectors were determined by analyzing
        different versions of Material for MkDocs theme. If a new version changes
        the DOM structure, add additional selectors here in order of specificity.
        """
        plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
        js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"

        if js_src.exists():
            js_content = js_src.read_text()

            # Check for all the fallback selectors
            # These must match the selectors in getMainContentElement()
            required_selectors = [
                ".md-content__inner .md-typeset",  # Primary
                ".md-content__inner",  # Fallback 1
                "article.md-content__inner",  # Fallback 2
                "main .md-typeset",  # Fallback 3
                "article",  # Fallback 4
                ".md-content",  # Fallback 5
                "main",  # Fallback 6 (final)
            ]

            for selector in required_selectors:
                assert selector in js_content, f"Missing selector: {selector}"

    def test_javascript_dom_selector_fallbacks_usage(self) -> None:
        """Test that getMainContentElement is used instead of direct querySelector.

        Issue #19 fix: The original code used direct document.querySelector() calls
        which would fail silently if the selector didn't match. Now we use
        getMainContentElement() which tries multiple selectors.

        This test ensures that the old direct selector pattern has been replaced
        with calls to getMainContentElement() in all the places where we need to
        get the main article content (copy button handlers, dropdown handlers, etc.).

        Context for next developer: If you add new features that need to access
        the main content element, always use getMainContentElement() instead of
        document.querySelector() to ensure compatibility across theme versions.
        """
        plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
        js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"

        if js_src.exists():
            js_content = js_src.read_text()

            # Should use getMainContentElement() for getting article content
            assert "getMainContentElement()" in js_content

            # Verify the old pattern is not used in copy handlers
            # Split by function definition to check code after the function exists
            parts = js_content.split("function getMainContentElement()")
            if len(parts) > 1:
                # Check that the old direct selector pattern is replaced
                remaining_code = parts[1]
                # The old hardcoded selector should not be used
                old_pattern = (
                    "articleContent = document.querySelector("
                    "'.md-content__inner .md-typeset')"
                )
                assert old_pattern not in remaining_code, (
                    "Old selector pattern still in use - "
                    "should use getMainContentElement()"
                )

    def test_javascript_dom_selector_fallbacks_error_handling(self) -> None:
        """Test that JavaScript includes error handling for missing elements.

        Issue #19 fix: When no DOM element could be found, the old code would
        fail silently, leaving users confused. Now we log errors to help debug
        and optionally alert users in debug mode.

        This test verifies that:
        1. Errors are logged to console when no element is found
        2. The function returns null (not undefined) for proper error handling
        3. Error messages include helpful information about what selectors were tried

        Context for next developer: The error logging is always active, but the
        alert() is only shown when window.copyToLLMDebug is true. This prevents
        annoying users while still providing debugging capabilities for developers
        and users troubleshooting issues.
        """
        plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
        js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"

        if js_src.exists():
            js_content = js_src.read_text()

            # Should have error logging with helpful message
            assert "console.error" in js_content
            assert "Could not find content element" in js_content, (
                "Missing error message for debugging"
            )

            # Should explicitly return null when no element found
            assert "return null" in js_content, (
                "Function should return null for proper error handling"
            )

    def test_javascript_dom_selector_fallbacks_debug_logging(self) -> None:
        """Test that JavaScript includes optional debug logging.

        Issue #19 fix: To help users troubleshoot DOM structure issues,
        we added optional debug logging that can be enabled by setting
        window.copyToLLMDebug = true in the browser console.

        When enabled, the debug logging shows:
        1. Which selector successfully found the content element
        2. Alert messages when no element can be found

        This test verifies that debug logging is:
        1. Conditional (only runs when window.copyToLLMDebug is true)
        2. Informative (shows which selector was used)

        Context for next developer: Users can enable debug mode by opening browser
        console and typing: window.copyToLLMDebug = true
        This will help diagnose issues with new theme versions or custom themes.
        """
        plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
        js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"

        if js_src.exists():
            js_content = js_src.read_text()

            # Should check for debug flag before logging
            assert "window.copyToLLMDebug" in js_content, "Missing debug flag check"

            # Should have informative debug logging
            assert "Found content using selector" in js_content, (
                "Missing debug message showing which selector worked"
            )

    def test_javascript_base_path_meta_tag_selector(self) -> None:
        """Test that JavaScript reads base_path from meta tag.

        Issue #18 fix: Validates that the JavaScript code includes logic to read
        the base_path from the mkdocs-copy-to-llm-base-path meta tag.
        """
        plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
        js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"

        if js_src.exists():
            js_content = js_src.read_text()

            # Should contain code to read the base_path meta tag
            assert 'meta[name="mkdocs-copy-to-llm-base-path"]' in js_content
            assert "metaBasePath" in js_content

    def test_javascript_base_path_stripping_logic(self) -> None:
        """Test that JavaScript contains base path stripping logic.

        Issue #18 fix: Validates that the JavaScript includes path manipulation
        logic to strip the base_path prefix, normalize slashes, and ensure paths
        start with / after stripping.
        """
        plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
        js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"

        if js_src.exists():
            js_content = js_src.read_text()

            # Should contain logic to strip base path from pathname
            assert "startsWith" in js_content
            assert "slice" in js_content

            # Should handle both with and without trailing slashes
            assert "endsWith('/')" in js_content

            # Should normalize paths to ensure they start with /
            assert "startsWith('/')" in js_content or 'startsWith("/")' in js_content

    def test_javascript_base_path_comments(self) -> None:
        """Test that JavaScript has comments explaining base path handling.

        Issue #18 fix: Ensures the JavaScript code includes explanatory comments
        about why base path stripping is needed (for sites deployed to subdirectories).
        """
        plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
        js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"

        if js_src.exists():
            js_content = js_src.read_text()

            # Should have comments explaining the base path logic
            # Look for keywords in comments that explain why we're doing this
            assert (
                "subdirectory" in js_content.lower() or "deployed" in js_content.lower()
            )

    def test_javascript_base_path_conditional_logic(self) -> None:
        """Test that base path stripping is conditional on meta tag presence.

        Issue #18 fix: Validates that the JavaScript only strips the base path
        when the meta tag is present, ensuring backward compatibility for sites
        that don't configure base_path.
        """
        plugin_dir = Path(__file__).parent.parent / "mkdocs_copy_to_llm"
        js_src = plugin_dir / "assets" / "js" / "copy-to-llm.js"

        if js_src.exists():
            js_content = js_src.read_text()
            lines = js_content.split("\n")

            # Find lines mentioning base path meta tag
            meta_base_path_lines = [
                i
                for i, line in enumerate(lines)
                if "mkdocs-copy-to-llm-base-path" in line
            ]

            # Should have at least one reference to the meta tag
            assert len(meta_base_path_lines) > 0

            # Check that there's conditional logic after reading the meta tag
            for line_num in meta_base_path_lines:
                nearby_lines = lines[line_num : line_num + 20]
                nearby_text = "\n".join(nearby_lines)
                # Should have conditional logic to check if meta tag exists
                if "metaBasePath" in nearby_text:
                    assert "if" in nearby_text
                    break
