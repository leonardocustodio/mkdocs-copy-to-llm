"""Test cases for validation functions."""

import pytest

from mkdocs_copy_to_llm.exceptions import ColorValidationError
from mkdocs_copy_to_llm.validation import (
    sanitize_css_value,
    validate_color,
    validate_minify_option,
    validate_url,
)


class TestColorValidation:
    """Test color validation function."""

    def test_valid_hex_colors(self) -> None:
        """Test valid hex color formats."""
        assert validate_color("#FFFFFF", "test") is True
        assert validate_color("#ffffff", "test") is True
        assert validate_color("#123456", "test") is True
        assert validate_color("#ABC", "test") is True
        assert validate_color("#abc", "test") is True
        assert validate_color("#F0F", "test") is True

    def test_valid_rgb_colors(self) -> None:
        """Test valid RGB color formats."""
        assert validate_color("rgb(255, 255, 255)", "test") is True
        assert validate_color("rgb(0,0,0)", "test") is True
        assert validate_color("rgb( 128 , 128 , 128 )", "test") is True
        assert validate_color("rgba(255, 0, 0, 0.5)", "test") is True

    def test_valid_css_variables(self) -> None:
        """Test valid CSS variable formats."""
        assert validate_color("var(--primary-color)", "test") is True
        assert validate_color("var(--md-primary-fg-color)", "test") is True
        assert validate_color("var(--theme-color-main)", "test") is True

    def test_valid_color_names(self) -> None:
        """Test valid CSS color names."""
        assert validate_color("red", "test") is True
        assert validate_color("blue", "test") is True
        assert validate_color("darkslategray", "test") is True
        assert validate_color("transparent", "test") is True

    def test_empty_color(self) -> None:
        """Test that empty string is valid."""
        assert validate_color("", "test") is True

    def test_invalid_colors(self) -> None:
        """Test invalid color formats."""
        with pytest.raises(ColorValidationError) as exc_info:
            validate_color("#GGGGGG", "test_field")
        assert "test_field" in str(exc_info.value)
        assert "#GGGGGG" in str(exc_info.value)

        with pytest.raises(ColorValidationError):
            validate_color("#12345", "test")  # Wrong length

        with pytest.raises(ColorValidationError):
            validate_color(
                "rgb(256, 0, 0)", "test"
            )  # Will pass basic regex but is invalid

        with pytest.raises(ColorValidationError):
            validate_color("var(invalid)", "test")  # Missing --

        with pytest.raises(ColorValidationError):
            validate_color("not-a-color()", "test")


class TestURLValidation:
    """Test URL validation function."""

    def test_valid_urls(self) -> None:
        """Test valid URL formats."""
        assert validate_url("https://github.com/user/repo") is True
        assert validate_url("http://example.com") is True
        assert validate_url("https://raw.githubusercontent.com/user/repo/main") is True
        assert validate_url("https://example.com:8080/path") is True
        assert validate_url("https://sub.domain.com/path/to/file") is True

    def test_empty_url(self) -> None:
        """Test that empty string is valid."""
        assert validate_url("") is True

    def test_invalid_urls(self) -> None:
        """Test invalid URL formats."""
        assert validate_url("not-a-url") is False
        assert validate_url("ftp://example.com") is False  # Only http(s)
        assert validate_url("//example.com") is False  # Missing protocol
        assert validate_url("https://") is False  # Missing domain


class TestCSSValueSanitization:
    """Test CSS value sanitization."""

    def test_valid_css_values(self) -> None:
        """Test that valid CSS values are preserved."""
        assert sanitize_css_value("#FFFFFF") == "#FFFFFF"
        assert sanitize_css_value("rgb(255, 255, 255)") == "rgb(255, 255, 255)"
        assert sanitize_css_value("var(--color)") == "var(--color)"
        assert sanitize_css_value("blue") == "blue"

    def test_dangerous_values_removed(self) -> None:
        """Test that dangerous values are sanitized."""
        assert "javascript:" not in sanitize_css_value("javascript:alert(1)")
        assert "expression" not in sanitize_css_value("expression(alert(1))")
        assert "@import" not in sanitize_css_value("@import url(evil.css)")
        assert "script" not in sanitize_css_value("</script>")
        assert "style" not in sanitize_css_value("<style>")

    def test_special_characters_removed(self) -> None:
        """Test that special characters are removed."""
        # Semicolons indicate CSS injection attempts, so everything after is removed
        assert sanitize_css_value("color; hack: value") == "color"
        assert sanitize_css_value("color/*comment*/") == "colorcomment"
        assert sanitize_css_value("url('evil')") == "url(evil)"

    def test_empty_value(self) -> None:
        """Test empty value handling."""
        assert sanitize_css_value("") == ""
        assert sanitize_css_value(None) is None


class TestMinifyValidation:
    """Test minify option validation."""

    def test_valid_boolean_values(self) -> None:
        """Test valid boolean values."""
        assert validate_minify_option(True) is True
        assert validate_minify_option(False) is True

    def test_invalid_values(self) -> None:
        """Test invalid values."""
        assert validate_minify_option("true") is False
        assert validate_minify_option(1) is False
        assert validate_minify_option(None) is False
