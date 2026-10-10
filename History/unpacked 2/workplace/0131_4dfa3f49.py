# coding: latin_1
# Dev-only unit test for shop_deal_rating.compute_deal_rating.
# NOT imported by the client at runtime. Run: python test_shop_deal_rating.py
from shop_deal_rating import compute_deal_rating


def _approx(a, b):
	return abs(a - b) < 1e-6


def run():
	# No data -> NODATA, no delta
	assert compute_deal_rating(100, 0) == ("NODATA", None)
	assert compute_deal_rating(100, None) == ("NODATA", None)
	assert compute_deal_rating(100, -5) == ("NODATA", None)

	# Half-open bands on p = price/avg*100; a value AT a boundary lands in the
	# higher (less-good) tier.
	assert compute_deal_rating(94, 100)[0] == "GREAT"
	assert compute_deal_rating(95, 100)[0] == "GOOD"
	assert compute_deal_rating(109, 100)[0] == "GOOD"
	assert compute_deal_rating(110, 100)[0] == "FAIR"
	assert compute_deal_rating(114, 100)[0] == "FAIR"
	assert compute_deal_rating(115, 100)[0] == "ABOVE"
	assert compute_deal_rating(119, 100)[0] == "ABOVE"
	assert compute_deal_rating(120, 100)[0] == "OVER"
	assert compute_deal_rating(500, 100)[0] == "OVER"

	# Delta sign + magnitude
	t, d = compute_deal_rating(95, 100)
	assert t == "GOOD" and _approx(d, -5.0)
	t, d = compute_deal_rating(108, 100)
	assert t == "GOOD" and _approx(d, 8.0)
	t, d = compute_deal_rating(100, 100)
	assert t == "GOOD" and _approx(d, 0.0)

	print("OK")


if __name__ == "__main__":
	run()
