def total(items):
    """Sum of price * qty for (price, qty) pairs."""
    return sum(p * q for p, q in items)


def apply_discount(price, pct):
    """Return price after a percentage discount (pct=10 means 10% off)."""
    return price - price * pct / 100


def with_tax(amount, rate_pct):
    """Return amount plus tax (rate_pct=10 means 10% tax)."""
    return amount + amount * rate_pct / 100
