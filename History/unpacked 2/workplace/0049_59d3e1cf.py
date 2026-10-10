# coding: latin_1
#
# Premium origin sources for the wiki item detail page: the Dragon Coin Item
# Shop (ENABLE_ITEMSHOP) and the Wheel of Fortune (USE_WHEEL_OF_FORTUNE).
#
# Neither catalog is baked into the client -- both arrive from the server on
# demand, so this module owns:
#   - the prefetch (fired once, when the wiki window is first built)
#   - the prefetch of both catalogs, each over a dedicated read-only command
#   - the two reverse indices (item vnum -> shop entries / wheel entries)
#   - the click actions for both row types
#
# Everything here is fail-soft: a missing module, an empty catalog or a
# malformed row contributes nothing rather than raising. The wiki must open
# even when the item shop is unreachable.

import app

if app.ENABLE_INGAME_WIKI:
	import net
	import item as itemModule
	import localeinfo


	def LocaleText(key, default):
		# localeinfo's wrapper returns "Locale not found: KEY" instead of raising,
		# so a bare getattr default never fires. Covers the window between a code
		# ship and the locale .epk repack.
		value = getattr(localeinfo, key, default)
		if not value or value.startswith("Locale not found"):
			return default

		return value


	# ================================================================
	# Prefetch
	# ================================================================
	#
	# Both requests are read-only and have no effect on the shop or wheel UI:
	# the server answers them on paths that touch neither window.

	_prefetched = False


	def Prefetch():
		"""Ask the server for the item shop catalog and the wheel odds. Called
		once, from InGameWiki.__init__ -- the wiki window is built lazily on
		first open, so players who never open it never pay for this."""
		global _prefetched
		if _prefetched:
			return
		_prefetched = True

		if app.ENABLE_ITEMSHOP:
			# Dedicated read-only catalog push. NOT "/ishop data" -- that is the
			# player's command and carries side effects a silent prefetch must not
			# trigger: it consumes the per-character "itemshop.load" one-shot (which
			# left the player's own shop stuck on its loading spinner with stale
			# Dragon Coins until the next warp), pushes PrizeProgress, and its reply
			# drives ItemShopHideLoading plus ItemShopOpenMainPage once PER CATEGORY.
			# ITEMSHOP_WIKI_LOAD answers this one by filling the cache and nothing else.
			try:
				net.SendChatPacket("/ishop wikidata")
			except Exception:
				pass

		if app.USE_WHEEL_OF_FORTUNE:
			try:
				net.SendChatPacket("/wheel_of_fortune odds")
			except Exception:
				pass


	# ================================================================
	# Item shop index
	# ================================================================
	#
	# uiitemshop.itemshopData layout:
	#   {categoryIndex: [ [entry, ...] * 10 subcategories ]}
	# entry = [itemID, itemVnum, itemPrice, itemDiscount, itemOffertime,
	#          itemTopSelling, itemAddedTime, itemSellingCount,
	#          weekLimit, monthLimit, globalMonthLimit]

	_E_ID, _E_VNUM, _E_PRICE, _E_DISCOUNT, _E_OFFERTIME = 0, 1, 2, 3, 4
	_E_WEEK_LIMIT, _E_MONTH_LIMIT = 8, 9

	_itemShopIndex = None
	_itemShopStamp = None


	def _BuildItemShopIndex():
		global _itemShopIndex, _itemShopStamp

		try:
			import uiitemshop
		except Exception:
			return {}

		# Rebuild whenever the server's catalog timestamp moves.
		if _itemShopIndex is not None and _itemShopStamp == uiitemshop.UPDATE_TIME:
			return _itemShopIndex

		idx = {}
		for _category, subLists in (uiitemshop.itemshopData or {}).items():
			if not subLists:
				continue
			for entries in subLists:
				for entry in (entries or []):
					if not entry or len(entry) <= _E_VNUM:
						continue
					try:
						vnum = int(entry[_E_VNUM])
					except (TypeError, ValueError):
						continue
					if not vnum:
						continue
					idx.setdefault(vnum, []).append(entry)

		_itemShopIndex = idx
		_itemShopStamp = uiitemshop.UPDATE_TIME

		return idx


	def GetItemShopEntries(vnum):
		"""Raw item shop rows selling this vnum (empty until the catalog lands)."""
		try:
			return list(_BuildItemShopIndex().get(int(vnum), []))
		except (TypeError, ValueError):
			return []


	def GetItemShopTooltipLines(vnum):
		"""[(text, isDim), ...] describing the cheapest listing of this item."""
		entries = GetItemShopEntries(vnum)
		if not entries:
			return []

		def price_of(e):
			try:
				return long(e[_E_PRICE])
			except (TypeError, ValueError, IndexError):
				return 0

		entry = min(entries, key=price_of)
		lines = []

		price = price_of(entry)
		discount = 0
		try:
			discount = int(entry[_E_DISCOUNT])
		except (TypeError, ValueError, IndexError):
			discount = 0
		if discount > 0:
			price = price - (price * discount / 100)

		lines.append((LocaleText("WIKI_ITEMSHOP_TIP_PRICE", "Price: %s DC")
					  % _Thousands(price), False))
		if discount > 0:
			lines.append((LocaleText("WIKI_ITEMSHOP_TIP_DISCOUNT", "Discount: %d%%")
						  % discount, False))

		try:
			offerTime = int(entry[_E_OFFERTIME])
		except (TypeError, ValueError, IndexError):
			offerTime = 0
		if offerTime > 0:
			lines.append((LocaleText("WIKI_ITEMSHOP_TIP_OFFER_UNTIL", "Offer until: %s")
						  % _DateText(offerTime), True))

		for slot, key, default in (
			(_E_WEEK_LIMIT,  "WIKI_ITEMSHOP_TIP_WEEK_LIMIT",  "Weekly limit: %d"),
			(_E_MONTH_LIMIT, "WIKI_ITEMSHOP_TIP_MONTH_LIMIT", "Monthly limit: %d"),
		):
			try:
				limit = int(entry[slot])
			except (TypeError, ValueError, IndexError):
				limit = 0
			if limit > 0:
				lines.append((LocaleText(key, default) % limit, True))

		return lines


	def _Thousands(value):
		try:
			s = str(long(value))
		except (TypeError, ValueError):
			return str(value)
		out = ""
		while len(s) > 3:
			out = "," + s[-3:] + out
			s = s[:-3]
		return s + out


	def _DateText(stamp):
		try:
			import time
			tm = time.localtime(int(stamp))
			return "%02d/%02d/%04d" % (tm.tm_mday, tm.tm_mon, tm.tm_year)
		except Exception:
			return str(stamp)


	# ================================================================
	# Wheel index
	# ================================================================
	#
	# uiitemshop mirrors the WheelOdds* push at module level (the window's own
	# copy is per-instance and reset on every open):
	#   wikiWheelOddsTiers = {rarity: {"chanceBp": bp, "items": [(vnum, count, bp), ...]}}

	_wheelIndex = None
	_wheelStamp = None


	def _BuildWheelIndex():
		global _wheelIndex, _wheelStamp

		try:
			import uiitemshop
			tiers = uiitemshop.wikiWheelOddsTiers or {}
			stamp = uiitemshop.wikiWheelOddsSerial
		except Exception:
			return {}

		if _wheelIndex is not None and _wheelStamp == stamp:
			return _wheelIndex

		idx = {}
		for rarity, tier in tiers.items():
			if not isinstance(tier, dict):
				continue
			for row in (tier.get("items") or []):
				if not row or len(row) < 3:
					continue
				try:
					vnum = int(row[0])
				except (TypeError, ValueError):
					continue
				if not vnum:
					continue
				idx.setdefault(vnum, []).append((rarity, int(row[1]), int(row[2])))

		_wheelIndex = idx
		_wheelStamp = stamp
		return idx


	def GetWheelEntries(vnum):
		"""[(rarity, count, chanceBp), ...] for this vnum on the wheel."""
		try:
			return list(_BuildWheelIndex().get(int(vnum), []))
		except (TypeError, ValueError):
			return []


	WHEEL_TIER_NAME_KEYS = (
		"WHEEL_ODDS_TIER_0",
		"WHEEL_ODDS_TIER_1",
		"WHEEL_ODDS_TIER_2",
	)
	WHEEL_TIER_NAME_DEFAULTS = ("Common", "Rare", "Legendary")


	def GetWheelTooltipLines(vnum):
		"""[(text, isDim), ...] describing this item's wheel tiers + odds."""
		entries = GetWheelEntries(vnum)
		if not entries:
			return []

		try:
			import uiitemshop
			fmt = uiitemshop.FormatWheelOdds
		except Exception:
			fmt = lambda bp: "%d.%02d%%" % (bp // 100, bp % 100)

		lines = []
		for (rarity, _count, chanceBp) in entries:
			if 0 <= rarity < len(WHEEL_TIER_NAME_KEYS):
				tierName = LocaleText(WHEEL_TIER_NAME_KEYS[rarity],
									  WHEEL_TIER_NAME_DEFAULTS[rarity])
			else:
				tierName = str(rarity)
			lines.append((LocaleText("WIKI_WHEEL_TIP_TIER", "Tier: %s") % tierName, False))
			lines.append((LocaleText("WIKI_WHEEL_TIP_CHANCE", "Chance: %s") % fmt(chanceBp), True))

		return lines


	# ================================================================
	# Row labels
	# ================================================================

	def GetItemShopRowText():
		return "%s %s" % (LocaleText("WIKI_ORIGIN_ITEMSHOP_TAG", "[Item Shop]"),
						  LocaleText("WIKI_ORIGIN_ITEMSHOP_NAME", "Dragon Coin Shop"))


	def GetWheelRowText():
		return "%s %s" % (LocaleText("WIKI_ORIGIN_WHEEL_TAG", "[Wheel]"),
						  LocaleText("WIKI_ORIGIN_WHEEL_NAME", "Wheel of Fortune"))


	# ================================================================
	# Click actions
	# ================================================================

	def _Interface():
		# Same accessor the rest of the wiki uses for cross-window jumps.
		try:
			import systemSetting
			return systemSetting.GetInterfaceHandler()
		except Exception:
			return None


	def OpenItemShopSearch(vnum):
		"""Open the shop with its search field pre-filled with this item's name."""
		iface = _Interface()
		if not iface:
			return
		try:
			itemModule.SelectItem(int(vnum))
			name = itemModule.GetItemName()
		except Exception:
			name = ""
		try:
			iface.OpenItemShopToSearch(name)
		except Exception:
			pass


	def OpenWheelView():
		"""Open the wheel. The live wheel is the view embedded in the item shop
		window -- uiwheeloffortune.py and uispinwheel.py are the dead copies."""
		iface = _Interface()
		if not iface:
			return
		try:
			iface.OpenItemShopToWheel()
		except Exception:
			pass
