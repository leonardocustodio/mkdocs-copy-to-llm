"""Input validation utilities for the MkDocs Copy to LLM plugin."""

import re
from typing import Any

from .exceptions import ColorValidationError


def validate_color(color: str, field_name: str) -> bool:
    """
    Validate color format.

    Args:
        color: Color value to validate
        field_name: Name of the configuration field for error messages

    Returns:
        True if color is valid

    Raises:
        ColorValidationError: If color format is invalid
    """
    if not color:  # Empty string is valid (uses default)
        return True

    # Define valid color patterns
    patterns = [
        r"^#[0-9A-Fa-f]{6}$",  # Hex 6-digit: #RRGGBB
        r"^#[0-9A-Fa-f]{3}$",  # Hex 3-digit: #RGB
        # RGB: rgb(r, g, b) with 0-255 values
        r"^rgb\(\s*(25[0-5]|2[0-4]\d|1?\d{1,2})\s*,\s*"
        r"(25[0-5]|2[0-4]\d|1?\d{1,2})\s*,\s*"
        r"(25[0-5]|2[0-4]\d|1?\d{1,2})\s*\)$",
        # RGBA with alpha 0-1
        r"^rgba\(\s*(25[0-5]|2[0-4]\d|1?\d{1,2})\s*,\s*"
        r"(25[0-5]|2[0-4]\d|1?\d{1,2})\s*,\s*"
        r"(25[0-5]|2[0-4]\d|1?\d{1,2})\s*,\s*"
        r"(0|1|0?\.\d+)\s*\)$",
        r"^var\(--[\w-]+\)$",  # CSS variable: var(--name)
        r"^[a-zA-Z]+$",  # CSS color name (basic check)
    ]

    for pattern in patterns:
        if re.match(pattern, color.strip()):
            return True

    raise ColorValidationError(color, field_name)


def validate_url(url: str) -> bool:
    """
    Validate repository URL format.

    Args:
        url: URL to validate

    Returns:
        True if URL is valid
    """
    if not url:  # Empty string is valid (no repo URL)
        return True

    # Basic URL validation - must start with http(s)://
    url_pattern = r"^https?://[\w\-.]+(:\d+)?(/.*)?$"
    return bool(re.match(url_pattern, url.strip()))


def sanitize_css_value(value: str) -> str:
    """
    Sanitize CSS value to prevent injection.

    Args:
        value: CSS value to sanitize

    Returns:
        Sanitized CSS value
    """
    if not value:
        return value

    # First, split by semicolon and take only the first part
    # This prevents CSS injection attempts
    value = value.split(";")[0].strip()

    # Remove any dangerous patterns with their content
    sanitized = value
    dangerous_patterns = [
        r"javascript:[^;]*",
        r"expression\s*\([^)]*\)",
        r"@import[^;]*",
        r"</?script[^>]*>?",
        r"</?style[^>]*>?",
    ]

    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

    # Then remove potentially dangerous characters
    # Allow alphanumeric, spaces, parentheses, commas, hyphens, #, and periods
    sanitized = re.sub(r"[^a-zA-Z0-9\s(),#.\-]", "", sanitized)

    return sanitized.strip()


def validate_minify_option(value: Any) -> bool:
    """
    Validate minify configuration option.

    Args:
        value: Value to validate

    Returns:
        True if value is a valid boolean
    """
    return isinstance(value, bool)
