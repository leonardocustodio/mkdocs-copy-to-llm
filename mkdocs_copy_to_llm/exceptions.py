"""Custom exceptions for the MkDocs Copy to LLM plugin."""


class CopyToLLMError(Exception):
    """Base exception for all Copy to LLM plugin errors."""

    pass


class ConfigurationError(CopyToLLMError):
    """Raised when plugin configuration is invalid."""

    pass


class AssetError(CopyToLLMError):
    """Raised when there are issues with plugin assets."""

    pass


class AssetNotFoundError(AssetError):
    """Raised when required plugin assets are not found."""

    pass


class AssetProcessingError(AssetError):
    """Raised when asset processing (e.g., minification) fails."""

    pass


class ValidationError(CopyToLLMError):
    """Raised when input validation fails."""

    pass


class ColorValidationError(ValidationError):
    """Raised when color format validation fails."""

    def __init__(self, color: str, field: str) -> None:
        super().__init__(
            f"Invalid color format '{color}' for {field}. "
            f"Expected hex (#RGB or #RRGGBB), rgb(r,g,b), CSS color name, "
            f"or CSS variable (var(--name))."
        )
        self.color = color
        self.field = field


class BuildError(CopyToLLMError):
    """Raised when there are issues during the build process."""

    pass
