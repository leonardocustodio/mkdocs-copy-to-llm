"""Test cases for custom exceptions."""

from mkdocs_copy_to_llm.exceptions import (
    AssetError,
    AssetNotFoundError,
    AssetProcessingError,
    BuildError,
    ColorValidationError,
    ConfigurationError,
    CopyToLLMError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""

    def test_base_exception(self) -> None:
        """Test that CopyToLLMError is the base exception."""
        exc = CopyToLLMError("test error")
        assert isinstance(exc, Exception)
        assert str(exc) == "test error"

    def test_configuration_error(self) -> None:
        """Test ConfigurationError."""
        exc = ConfigurationError("config error")
        assert isinstance(exc, CopyToLLMError)
        assert str(exc) == "config error"

    def test_asset_errors(self) -> None:
        """Test asset-related errors."""
        exc1 = AssetError("asset error")
        assert isinstance(exc1, CopyToLLMError)

        exc2 = AssetNotFoundError("file not found")
        assert isinstance(exc2, AssetError)
        assert isinstance(exc2, CopyToLLMError)

        exc3 = AssetProcessingError("processing failed")
        assert isinstance(exc3, AssetError)
        assert isinstance(exc3, CopyToLLMError)

    def test_validation_errors(self) -> None:
        """Test validation errors."""
        exc1 = ValidationError("validation failed")
        assert isinstance(exc1, CopyToLLMError)

        exc2 = ColorValidationError("#invalid", "field_name")
        assert isinstance(exc2, ValidationError)
        assert isinstance(exc2, CopyToLLMError)
        assert "field_name" in str(exc2)
        assert "#invalid" in str(exc2)
        assert exc2.color == "#invalid"
        assert exc2.field == "field_name"

    def test_build_error(self) -> None:
        """Test BuildError."""
        exc = BuildError("build failed")
        assert isinstance(exc, CopyToLLMError)
        assert str(exc) == "build failed"


class TestColorValidationError:
    """Test ColorValidationError specific functionality."""

    def test_error_message_format(self) -> None:
        """Test that error message is properly formatted."""
        exc = ColorValidationError("not-a-color", "button_bg_color")
        error_msg = str(exc)

        assert "Invalid color format" in error_msg
        assert "not-a-color" in error_msg
        assert "button_bg_color" in error_msg
        assert "hex (#RGB or #RRGGBB)" in error_msg
        assert "rgb(r,g,b)" in error_msg
        assert "CSS color name" in error_msg
        assert "CSS variable (var(--name))" in error_msg

    def test_attributes(self) -> None:
        """Test that attributes are properly set."""
        exc = ColorValidationError("#GGG", "toast_bg_color")
        assert exc.color == "#GGG"
        assert exc.field == "toast_bg_color"
