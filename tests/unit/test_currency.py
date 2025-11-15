"""Unit tests for currency utilities."""

from decimal import Decimal

import pytest

from splitfool.utils.currency import format_currency, parse_currency, validate_positive_decimal


def test_format_currency_rounds_to_cents() -> None:
    """Test that format_currency rounds to 2 decimal places."""
    assert format_currency(Decimal("12.345")) == "$12.35"
    assert format_currency(Decimal("12.344")) == "$12.34"


def test_format_currency_adds_trailing_zeros() -> None:
    """Test that format_currency adds trailing zeros."""
    assert format_currency(Decimal("12")) == "$12.00"
    assert format_currency(Decimal("12.5")) == "$12.50"


def test_format_currency_handles_negative() -> None:
    """Test that format_currency handles negative values."""
    assert format_currency(Decimal("-12.34")) == "$-12.34"


def test_parse_currency_removes_dollar_sign() -> None:
    """Test that parse_currency removes dollar sign."""
    assert parse_currency("$12.34") == Decimal("12.34")


def test_parse_currency_handles_no_dollar_sign() -> None:
    """Test that parse_currency handles input without dollar sign."""
    assert parse_currency("12.34") == Decimal("12.34")


def test_parse_currency_removes_commas() -> None:
    """Test that parse_currency removes commas."""
    assert parse_currency("1,234.56") == Decimal("1234.56")
    assert parse_currency("$1,234,567.89") == Decimal("1234567.89")


def test_parse_currency_roundtrip() -> None:
    """Test that format/parse roundtrip preserves value."""
    original = Decimal("123.45")
    formatted = format_currency(original)
    parsed = parse_currency(formatted)
    assert parsed == original


def test_validate_positive_decimal_accepts_positive() -> None:
    """Test that validate_positive_decimal accepts positive values."""
    validate_positive_decimal(Decimal("0.01"))
    validate_positive_decimal(Decimal("100.00"))


def test_validate_positive_decimal_rejects_zero() -> None:
    """Test that validate_positive_decimal rejects zero."""
    with pytest.raises(ValueError, match="must be positive"):
        validate_positive_decimal(Decimal("0"))


def test_validate_positive_decimal_rejects_negative() -> None:
    """Test that validate_positive_decimal rejects negative values."""
    with pytest.raises(ValueError, match="must be positive"):
        validate_positive_decimal(Decimal("-1.00"))


def test_validate_positive_decimal_custom_field_name() -> None:
    """Test that validate_positive_decimal uses custom field name in error."""
    with pytest.raises(ValueError, match="cost must be positive"):
        validate_positive_decimal(Decimal("0"), field_name="cost")
