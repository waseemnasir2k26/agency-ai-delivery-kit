import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
from pricing import apply_discount

def test_ten_percent_off():
    assert apply_discount(1000, 10) == 900


def test_with_tax():
    from pricing import with_tax
    assert with_tax(200, 10) == 220


if __name__ == "__main__":          # run without pytest: python tests/test_pricing.py
    test_ten_percent_off(); test_with_tax()
    print("test_pricing: 2/2 passed")
