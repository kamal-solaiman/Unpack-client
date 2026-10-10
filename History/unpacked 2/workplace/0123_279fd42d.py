# coding: latin_1
# shop_deal_rating.py -- pure deal-rating math for the offlineshop search price
# dashboard. NO engine imports (ui/app/item/localeinfo) so it is unit-testable
# under plain python and shared by uishopsearch_new.py.
#
# compute_deal_rating(price, avg) -> (tier, delta)
#   tier : "GREAT" | "GOOD" | "FAIR" | "ABOVE" | "OVER" | "NODATA"
#   delta: signed percent of price vs avg (price 5% below avg -> -5.0),
#          or None when tier == "NODATA".
# Half-open bands on p = price/avg*100 (value AT a boundary -> higher tier):
#   p<95 GREAT | 95<=p<110 GOOD | 110<=p<115 FAIR | 115<=p<120 ABOVE | p>=120 OVER


def compute_deal_rating(price, avg):
	if not avg or avg <= 0:
		return ("NODATA", None)
	p = price * 100.0 / avg
	delta = p - 100.0
	if p < 95:
		return ("GREAT", delta)
	if p < 110:
		return ("GOOD", delta)
	if p < 115:
		return ("FAIR", delta)
	if p < 120:
		return ("ABOVE", delta)
	return ("OVER", delta)
