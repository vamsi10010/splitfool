"""Currency handling utilities using Decimal for precision."""

from decimal import Decimal, getcontext, ROUND_HALF_UP


# Set global precision for currency calculations
getcontext().prec = 10
getcontext().rounding = ROUND_HALF_UP


def format_currency(amount: Decimal) -> str:
    """Format Decimal as currency string.

    Args:
        amount: Decimal amount to format

    Returns:
        Formatted currency string (e.g., "$12.34")

    Examples:
        >>> format_currency(Decimal('12.345'))
        '$12.35'
        >>> format_currency(Decimal('0.5'))
        '$0.50'
    """
    return f"${amount.quantize(Decimal('0.01'))}"


def parse_currency(value: str) -> Decimal:
    """Parse user input string to Decimal.

    Args:
        value: String representation of currency amount

    Returns:
        Decimal value

    Raises:
        ValueError: If string cannot be parsed as Decimal

    Examples:
        >>> parse_currency("$12.34")
        Decimal('12.34')
        >>> parse_currency("12.34")
        Decimal('12.34')
        >>> parse_currency("1,234.56")
        Decimal('1234.56')
    """
    # Remove currency symbols and commas
    cleaned = value.replace("$", "").replace(",", "").strip()
    return Decimal(cleaned)


def validate_positive_decimal(value: Decimal, field_name: str = "value") -> None:
    """Validate that a decimal value is positive.

    Args:
        value: Decimal value to validate
        field_name: Name of field for error message

    Raises:
        ValueError: If value is not positive
    """
    if value <= Decimal("0"):
        raise ValueError(f"{field_name} must be positive, got {value}")
