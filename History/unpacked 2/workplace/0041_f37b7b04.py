# coding: latin_1
#
# Gaya Shop wiki page: market rules, the full rotating catalog grouped by
# market row, and the two crafting steps that end in Gaya. Catalog rows come
# from the baked gem_shop.json -- the same catalog the server reads
# (CGemShopManager), copied byte-identical into the client data tree, so the
# page can never drift from what the trader actually offers.

import app
import dbg
import ui
import item
import localeinfo
import ingamewikidungeon
import ingamewikibiolog

LocaleText = ingamewikidungeon.LocaleText
_NavRow = ingamewikibiolog._NavRow

_ART = "d:/ymir work/ui/wiki/wiki_new/dungeons/"
_GAYA_ICON = "d:/ymir work/ui/gemshop/gemshop_gemicon.sub"
_JSON_NAME = "gem_shop.json"

_COL_NAME = 0xffffffff
_COL_ITEM_TITLE = 0xffcabdab
_COL_DESC = 0xffa09080
_COL_NAV = 0xffcabdab
_COL_PRICE = 0xffffe6a0

# Mirrors of the server-side gem.txt scalars: the market's unlock/refresh items
# and the crafting-chain vnums. Material counts live here rather than in the
# locale copy so they render as icon badges and cannot falsify the text.
_GEM_EXPANSION = 39064
_GEM_REFRESH = 39063
_GAYA_MATERIAL = 31094
_GLIMMERSTONE = 50926
_GLIMMERASHE = 51926
_CRAFT_COUNT = 10
_PROB_GEM = 60
_COST_YANG = 100000
_GIVE_GEM = 1
_GRADE_STONE = 3
_BATCH_MIN = 5
_BATCH_MAX = 500

_catalog = None


def _LoadCatalog():
	global _catalog
	if _catalog is not None:
		return _catalog
	_catalog = []
	txt = ingamewikidungeon._ReadJsonText(_JSON_NAME)
	if not txt:
		try:
			dbg.TraceError("[wikigemshop] missing or empty %s" % _JSON_NAME)
		except:
			pass
		return _catalog
	try:
		data = eval(txt, dict(ingamewikidungeon._JSON_GLOBALS))
	except Exception:
		try:
			dbg.TraceError("[wikigemshop] failed to parse %s" % _JSON_NAME)
		except:
			pass
		return _catalog
	if type(data) is list:
		_catalog = data
	else:
		try:
			dbg.TraceError("[wikigemshop] %s is not a list" % _JSON_NAME)
		except:
			pass
	return _catalog


def Reload():
	global _catalog
	_catalog = None
	return _LoadCatalog()


def _RowEntries(row):
	# (vnum, count, price) for one market row, in catalog order. A malformed
	# entry drops out instead of breaking the page.
	entries = []
	for e in _LoadCatalog():
		try:
			if int(e["row"]) != int(row):
				continue
			entries.append((int(e["vnum"]), int(e.get("count", 1)), int(e.get("price", 0))))
		except (AttributeError, KeyError, TypeError, ValueError):
			continue
	return entries


def GetMarketEntries(vnum):
	# (count, price, row) offers of this vnum -- the item-origin panel's
	# source for its [Gaya Market] row.
	try:
		vnum = int(vnum)
	except (TypeError, ValueError):
		return []
	offers = []
	for e in _LoadCatalog():
		try:
			if int(e["vnum"]) != vnum:
				continue
			offers.append((int(e.get("count", 1)), int(e.get("price", 0)), int(e.get("row", 0))))
		except (AttributeError, KeyError, TypeError, ValueError):
			continue
	return offers


def GetMarketRowText():
	return "%s %s" % (LocaleText("WIKI_ORIGIN_GEMSHOP_TAG", "[Gaya Market]"),
					  LocaleText("WIKI_GEMSHOP_TITLE", "Gaya Shop"))


def GetMarketTooltipLines(vnum):
	rowKeys = {
		1: ("WIKI_GEMSHOP_ROW1", "First Row"),
		2: ("WIKI_GEMSHOP_ROW2", "Second Row"),
		3: ("WIKI_GEMSHOP_ROW3", "Third Row"),
	}
	priceFmt = LocaleText("WIKI_ORIGIN_GEMSHOP_PRICE", "%dx for %d Gaya")
	lines = []
	for count, price, row in GetMarketEntries(vnum):
		try:
			text = priceFmt % (count, price)
		except (TypeError, ValueError):
			text = "%dx %d" % (count, price)
		key, default = rowKeys.get(row, (None, None))
		if key:
			text = "%s - %s" % (text, LocaleText(key, default))
		lines.append((text, False))
	return lines


def OpenWikiPage():
	try:
		import systemSetting
		iface = systemSetting.GetInterfaceHandler()
	except Exception:
		iface = None
	if not iface:
		return
	try:
		iface.OpenWikiToGemShop()
	except Exception:
		pass


class WikiGemShopWindow(ingamewikidungeon.WikiDungeonWindow):
	# Inherits the dungeon page's scroll plumbing, widget factories, _ItemIcon
	# (hover tooltip + click-through) and history OpenWindow support.

	_NAV_ROW_CENTERS = (21, 57, 93)
	_TBL_X0 = 40
	_TBL_W = 476
	_TBL_HEADER_H = 24
	_ROW_H = 34
	_COLS = (48, 62, 74)   # icon / amount / price; the name column gets the rest
	_CHAIN_CELL = 32
	_CHAIN_GAP = 16
	_CHAIN_ARROW = 24

	def OpenPage(self):
		self._ClearContent()
		self._sectionAnchors = {}

		y = 4
		y = self._RenderHeader(y)
		self._sectionAnchors["overview"] = y
		y = self._RenderOverviewSection(y)
		self._sectionAnchors["craft"] = y
		y = self._RenderCraftSection(y)
		self._sectionAnchors["catalog"] = y
		y = self._RenderRowSection(1, "WIKI_GEMSHOP_ROW1", "First Row", y)
		y = self._RenderRowSection(2, "WIKI_GEMSHOP_ROW2", "Second Row", y)
		y = self._RenderRowSection(3, "WIKI_GEMSHOP_ROW3", "Third Row", y)

		deco = self._Img(_ART + "page_end_deco.png", 0, y)
		self._FitWide(deco)
		y += 19 + 8

		self.scrollBoard.SetSize(self.peekWindow.GetWidth(), max(y, self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, 0)
		self.ChangeScrollbar()
		self.Show()

	# -- shared bits ---------------------------------------------------------

	def _FitWide(self, img):
		w = img.GetWidth() or 1
		pw = self.peekWindow.GetWidth()
		if w > pw:
			s = float(pw) / w
			img.SetScale(s, s)

	def _RTL(self):
		# Arabic TextLine glyphs anchor at the given x and flow LEFT, so the
		# RTL layout mirrors block positions; alignment modes stay unchanged.
		try:
			return localeinfo.IsARABIC()
		except:
			return 0

	def _SectionTitle(self, y, label):
		self._Img(_ART + "subtitle.png", (556 - 495) / 2, y)
		self._Text(label, 447 if self._RTL() else 108, y + 11, _COL_NAME)
		return y + 48

	def _OnNavClick(self, key):
		anchors = getattr(self, "_sectionAnchors", None) or {}
		target = anchors.get(key)
		if target is None:
			return
		span = self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()
		if span <= 0:
			return
		self.scrollBoard.SetPosition(0, -min(max(int(target) - 6, 0), span))
		self.ChangeScrollbar()

	def _ItemName(self, vnum):
		try:
			item.SelectItem(vnum)
			name = item.GetItemName()
		except Exception:
			name = ""
		return name or str(vnum)

	# -- header: section nav + the crafting-chain items ----------------------

	def _RenderHeader(self, y):
		rtl = self._RTL()
		pw = self.peekWindow.GetWidth()
		navX = (pw - 200 - 8) if rtl else 8
		labelX = (navX + 152) if rtl else (navX + 48)

		self._Img(_ART + "title_list_3.png", navX, y + 2)
		navs = (
			("overview", LocaleText("WIKI_GEMSHOP_OVERVIEW", "Overview")),
			("craft", LocaleText("WIKI_GEMSHOP_CRAFT_HEADER", "Crafting")),
			("catalog", LocaleText("WIKI_GEMSHOP_CATALOG", "Offers")),
		)
		for i in xrange(len(navs)):
			key, label = navs[i]
			rowCy = y + 2 + self._NAV_ROW_CENTERS[i]
			t = self._Text(label, labelX, rowCy - 8, _COL_NAV)
			row = _NavRow()
			row.SetParent(self.scrollBoard)
			# No "attach": FLAG_ATTACH redirects button events to GetRoot(), so
			# an attached row hovers but never receives clicks.
			row.SetSize(200, 30)
			row.SetPosition(navX, rowCy - 15)
			row.SetNav(t, ui.__mem_func__(self._OnNavClick), key)
			row.Show()
			self.elements.append(row)

		chainVnums = (_GAYA_MATERIAL, _GLIMMERASHE, _GLIMMERSTONE)
		chainW = len(chainVnums) * 62
		chainX = 8 if rtl else (pw - 8 - chainW)
		circleY = y + 2 + 34
		for i in xrange(len(chainVnums)):
			cx = chainX + i * 62
			circle = self._Img(_ART + "itemcircle1.png", cx, circleY)
			circle.SetScale(0.68, 0.68)
			self._ItemIcon(chainVnums[i], cx + 8, circleY + 10, cellW=32, cellH=32)

		deco = self._Img(_ART + "page_title_deco.png", 0, y + 139)
		self._FitWide(deco)
		return y + 139 + 20 + 8

	# -- Overview ------------------------------------------------------------

	def _RenderOverviewSection(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_GEMSHOP_OVERVIEW", "Overview"))

		rows = (
			(_GEM_EXPANSION, LocaleText("WIKI_GEMSHOP_UNLOCK_DESC", "Unlocks one of the locked shop slots for good")),
			(_GEM_REFRESH, LocaleText("WIKI_GEMSHOP_REFRESH_DESC", "Draws a new offer into every slot right away")),
		)
		rtl = self._RTL()
		pw = self.peekWindow.GetWidth()
		circleX = (pw - 44 - 48) if rtl else 44
		textX = (circleX - 8) if rtl else 116

		rowY = top
		for vnum, desc in rows:
			circle = self._Img(_ART + "itemcircle1.png", circleX, rowY)
			circle.SetScale(0.68, 0.68)
			self._ItemIcon(vnum, circleX + 8, rowY + 10, cellW=32, cellH=32)
			self._Text(self._ItemName(vnum), textX, rowY + 8, _COL_ITEM_TITLE)
			self._Text(desc, textX, rowY + 26, _COL_DESC)
			rowY += 58

		rowY += 6
		rules = (
			("WIKI_GEMSHOP_RULE1_A", "The Gaya trader offers nine items at a time, in three rows of three."),
			("WIKI_GEMSHOP_RULE1_B", "Each row is drawn from its own pool of items."),
			("WIKI_GEMSHOP_RULE2_A", "The offers are drawn at random, and rarer items appear less often."),
			("WIKI_GEMSHOP_RULE2_B", "All nine offers are replaced again every five hours."),
			("WIKI_GEMSHOP_RULE3_A", "Only the first row is open from the start. The six slots below it"),
			("WIKI_GEMSHOP_RULE3_B", "stay locked until you unlock each of them."),
		)
		lead = [LocaleText("WIKI_GEMSHOP_HEADER", "Everything the trader offers is paid for with Gaya, never with yang.")]
		return self._RuleTable(rowY, rules, lead=lead) + 12

	# -- Catalog: one table per market row -----------------------------------

	def _RenderRowSection(self, row, titleKey, titleDefault, y):
		entries = _RowEntries(row)
		if not entries:
			return y
		top = self._SectionTitle(y, LocaleText(titleKey, titleDefault))

		x0 = self._TBL_X0
		fixed = self._COLS
		colW = [fixed[0], self._TBL_W - sum(fixed), fixed[1], fixed[2]]
		COL_ICON, COL_NAME, COL_COUNT, COL_PRICE = 0, 1, 2, 3
		order = (COL_ICON, COL_NAME, COL_COUNT, COL_PRICE)
		# RTL flips the visual column order; colX stays keyed by logical column.
		seq = tuple(reversed(order)) if self._RTL() else order
		colX = {}
		x = x0
		for li in seq:
			colX[li] = x
			x += colW[li]

		headers = (
			"",
			LocaleText("WIKI_GEMSHOP_COL_ITEM", "Item"),
			LocaleText("WIKI_GEMSHOP_COL_COUNT", "Amount"),
			LocaleText("WIKI_GEMSHOP_PRICE", "Price"),
		)
		self._Bar(x0, top, self._TBL_W, self._TBL_HEADER_H, self._COL_TABLE_HEADER_BG)
		for li in seq:
			if headers[li]:
				self._Text(headers[li], colX[li] + colW[li] / 2, top + 6, ingamewikidungeon._COL_TAN, align="center")

		rowY = top + self._TBL_HEADER_H
		bounds = []
		for vnum, count, price in entries:
			self._Bar(x0, rowY, self._TBL_W, self._ROW_H, self._COL_TABLE_ROW_BG)
			textY = rowY + self._ROW_H / 2 - 7
			self._ItemIcon(vnum, colX[COL_ICON] + (colW[COL_ICON] - 32) / 2, rowY + (self._ROW_H - 32) / 2, cellW=32, cellH=32)
			self._Text(self._ItemName(vnum), colX[COL_NAME] + colW[COL_NAME] / 2, textY, self._COL_TABLE_VALUE, align="center")
			self._Text(str(count), colX[COL_COUNT] + colW[COL_COUNT] / 2, textY, self._COL_TABLE_VALUE, align="center")
			self._Text(str(price), colX[COL_PRICE] + colW[COL_PRICE] / 2, textY, _COL_PRICE, align="center")
			rowY += self._ROW_H
			bounds.append(rowY)

		self._TableGrid(top, rowY, seq, colX, colW, bounds)
		return rowY + 12

	def _TableGrid(self, top, bottom, seq, colX, colW, bounds, headerH=None):
		x0 = self._TBL_X0
		tableH = bottom - top
		hh = self._TBL_HEADER_H if headerH is None else headerH
		for li in seq[:-1]:
			self._Bar(colX[li] + colW[li], top, 1, tableH, self._COL_TABLE_BORDER)
		self._Bar(x0, top, self._TBL_W, 1, self._COL_TABLE_BORDER)
		if hh:
			self._Bar(x0, top + hh, self._TBL_W, 1, self._COL_TABLE_BORDER)
		for by in bounds:
			self._Bar(x0, by, self._TBL_W, 1, self._COL_TABLE_BORDER)
		self._Bar(x0, top, 1, tableH, self._COL_TABLE_BORDER)
		self._Bar(x0 + self._TBL_W - 1, top, 1, tableH, self._COL_TABLE_BORDER)

	# -- Crafting chain ------------------------------------------------------

	def _FmtText(self, key, default, args=()):
		# A mistranslated placeholder must degrade to the English default, never
		# take the page down.
		fmt = LocaleText(key, default)
		for candidate in (fmt, default):
			try:
				return candidate % args if args else candidate
			except (TypeError, ValueError):
				continue
		return default

	def _RenderCraftSection(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_GEMSHOP_CRAFT_HEADER", "Crafting"))

		try:
			yangText = localeinfo.NumberToMoneyString(_COST_YANG)
		except Exception:
			yangText = str(_COST_YANG)

		steps = (
			(
				((_GAYA_MATERIAL, 1),),
				_GLIMMERASHE,
				(
					self._FmtText("WIKI_GEMSHOP_CRAFT_ASHE_A", "The Gaya trader turns Stone Shards into Glimmerashe, in batches of %d to %d.", (_BATCH_MIN, _BATCH_MAX)),
					self._FmtText("WIKI_GEMSHOP_CRAFT_ASHE_B", "Each attempt uses one shard, costs %s and succeeds %d%% of the time.", (yangText, _PROB_GEM)),
				),
			),
			(
				((_GLIMMERSTONE, _CRAFT_COUNT), (_GLIMMERASHE, _CRAFT_COUNT)),
				0,
				(
					self._FmtText("WIKI_GEMSHOP_CRAFT_GAYA_A", "Her craft window fuses %d Glimmerstones and %d Glimmerashes into %d Gaya.", (_CRAFT_COUNT, _CRAFT_COUNT, _GIVE_GEM)),
					self._FmtText("WIKI_GEMSHOP_CRAFT_GAYA_B", "You also place a metin stone up to +%d and pay %s; the chance is %d%%.", (_GRADE_STONE, yangText, _PROB_GEM)),
					self._FmtText("WIKI_GEMSHOP_CRAFT_GAYA_C", "Glimmerashe comes from the step above; Glimmerstones drop from bosses."),
				),
			),
		)

		x0 = self._TBL_X0
		rowY = top
		bounds = []
		for mats, result, lines in steps:
			rowH = 46 + len(lines) * 16 + 6
			self._Bar(x0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			self._CraftChain(rowY + 8, mats, result)
			lineY = rowY + 46
			for line in lines:
				self._Text(line, x0 + self._TBL_W / 2, lineY, ingamewikidungeon._COL_TAN, align="center")
				lineY += 16
			rowY += rowH
			bounds.append(rowY)

		self._TableGrid(top, rowY, (0,), {0: x0}, {0: self._TBL_W}, bounds, headerH=0)
		return rowY + 12

	def _CraftChain(self, y, mats, result):
		cell = self._CHAIN_CELL
		gap = self._CHAIN_GAP
		rtl = self._RTL()
		width = len(mats) * cell + (len(mats) - 1) * gap + self._CHAIN_ARROW + cell
		x = self._TBL_X0 + (self._TBL_W - width) / 2

		entries = list(mats)
		if rtl:
			entries.reverse()
		for i in xrange(len(entries)):
			vnum, count = entries[i]
			self._ItemIcon(vnum, x, y, count=count, cellW=cell, cellH=cell)
			x += cell
			if i < len(entries) - 1:
				self._Text("+", x + gap / 2, y + 8, _COL_ITEM_TITLE, align="center")
				x += gap

		self._Text("<" if rtl else ">", x + self._CHAIN_ARROW / 2, y + 8, _COL_ITEM_TITLE, align="center")
		x += self._CHAIN_ARROW
		if result:
			self._ItemIcon(result, x, y, cellW=cell, cellH=cell)
		else:
			self._GayaIcon(x, y, cell)

	def _GayaIcon(self, x, y, cell):
		# Gaya is a currency, not an item, so the market window's own icon
		# stands in for it at the end of the chain.
		img = self._Img(_GAYA_ICON, x, y)
		w = img.GetWidth() or cell
		h = img.GetHeight() or cell
		scale = min(float(cell) / w, float(cell) / h, 1.0)
		if scale < 1.0:
			img.SetScale(scale, scale)
			w = int(w * scale)
			h = int(h * scale)
		img.SetPosition(int(x) + (cell - w) / 2, int(y) + (cell - h) / 2)
		if app.USE_CLIP_MASK:
			try:
				img.SetSubClippingMaskWindow(self.peekWindow)
			except:
				pass
		return img
