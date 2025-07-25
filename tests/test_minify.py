"""Test cases for the minification utilities."""

from unittest.mock import MagicMock, patch

from mkdocs_copy_to_llm.minify import minify_css, minify_js, should_minify


class TestJavaScriptMinification:
    """Test cases for JavaScript minification."""

    def test_minify_js_with_jsmin_available(self) -> None:
        """Test JS minification when jsmin is available."""
        # Mock the jsmin import inside the function
        mock_jsmin = MagicMock(return_value="minified js")
        with patch.dict("sys.modules", {"jsmin": MagicMock(jsmin=mock_jsmin)}):
            result = minify_js("var x = 1;\nvar y = 2;")

            assert result == "minified js"
            mock_jsmin.assert_called_once_with("var x = 1;\nvar y = 2;")

    def test_minify_js_without_jsmin(self) -> None:
        """Test JS minification when jsmin is not available."""
        # Ensure jsmin is not in sys.modules
        with patch.dict("sys.modules", {"jsmin": None}):
            result = minify_js("var x = 1;\nvar y = 2;")

            # Should return original content
            assert result == "var x = 1;\nvar y = 2;"

    def test_minify_js_with_error(self) -> None:
        """Test JS minification when jsmin raises an error."""
        # Mock jsmin to raise an exception
        mock_jsmin = MagicMock(side_effect=Exception("Minification failed"))
        with patch.dict("sys.modules", {"jsmin": MagicMock(jsmin=mock_jsmin)}):
            result = minify_js("var x = 1;")

            # Should return original content on error
            assert result == "var x = 1;"


class TestCSSMinification:
    """Test cases for CSS minification."""

    def test_minify_css_with_csscompressor_available(self) -> None:
        """Test CSS minification when csscompressor is available."""
        # Mock the csscompressor import inside the function
        mock_compress = MagicMock(return_value="minified css")
        with patch.dict(
            "sys.modules", {"csscompressor": MagicMock(compress=mock_compress)}
        ):
            result = minify_css("body { color: red; }")

            assert result == "minified css"
            mock_compress.assert_called_once_with("body { color: red; }")

    def test_minify_css_without_csscompressor(self) -> None:
        """Test CSS minification when csscompressor is not available."""
        # Ensure csscompressor is not in sys.modules
        with patch.dict("sys.modules", {"csscompressor": None}):
            result = minify_css("body { color: red; }")

            # Should return original content
            assert result == "body { color: red; }"

    def test_minify_css_with_error(self) -> None:
        """Test CSS minification when csscompressor raises an error."""
        # Mock compress to raise an exception
        mock_compress = MagicMock(side_effect=Exception("Compression failed"))
        with patch.dict(
            "sys.modules", {"csscompressor": MagicMock(compress=mock_compress)}
        ):
            result = minify_css("body { color: red; }")

            # Should return original content on error
            assert result == "body { color: red; }"


class TestShouldMinify:
    """Test cases for should_minify function."""

    def test_should_not_minify_in_dev_mode(self) -> None:
        """Test that minification is disabled in development mode."""
        config = {"dev_addr": "127.0.0.1:8000"}

        assert should_minify(config) is False

    def test_should_minify_in_production_default(self) -> None:
        """Test that minification is enabled by default in production."""
        config = {}

        assert should_minify(config) is True

    def test_should_respect_plugin_minify_setting_true(self) -> None:
        """Test that plugin minify setting is respected when True."""
        config = {"plugins": {"copy-to-llm": {"minify": True}}}

        assert should_minify(config) is True

    def test_should_respect_plugin_minify_setting_false(self) -> None:
        """Test that plugin minify setting is respected when False."""
        config = {"plugins": {"copy-to-llm": {"minify": False}}}

        assert should_minify(config) is False

    def test_should_not_minify_in_dev_mode_even_with_plugin_setting(self) -> None:
        """Test that dev mode takes precedence over plugin setting."""
        config = {
            "dev_addr": "127.0.0.1:8000",
            "plugins": {"copy-to-llm": {"minify": True}},
        }

        assert should_minify(config) is False

    def test_should_handle_missing_plugins_config(self) -> None:
        """Test handling when plugins config is missing."""
        config = {"plugins": {}}

        assert should_minify(config) is True

    def test_should_handle_missing_copy_to_llm_config(self) -> None:
        """Test handling when copy-to-llm config is missing."""
        config = {"plugins": {"other-plugin": {}}}

        assert should_minify(config) is True
