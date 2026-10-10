# coding: latin_1
#
# Dragon Stone Alchemy wiki page: twin section navs flanking a ring of the
# seven stone types, then Overview / Class / Clarity / Level / Bonuses /
# Set Bonus / Customize sections. All refine fees, chances, caps, bonus
# lists and set-point tables come from the baked dragonsoul_wiki.json
# (generated from the live dragon_soul_table.txt by
# tools/"wiki server to client"/gen_dragonsoul_wiki.py, never hand-edited).

import math
import app
import dbg
import ui
import item
import localeinfo
import uiScriptLocale
import ingamewikidungeon
import ingamewikibiolog

LocaleText = ingamewikidungeon.LocaleText
_NavRow = ingamewikibiolog._NavRow

_ART = "d:/ymir work/ui/wiki/wiki_new/dungeons/"
_JSON_NAME = "dragonsoul_wiki.json"

_COL_NAME = 0xffffffff
_COL_GOLD = 0xffffe6a0
_COL_ITEM_TITLE = 0xffcabdab
_COL_DESC = 0xffa09080
_COL_RULE = 0xffc7c7c7
_COL_REWARD = 0xffb0dfb4
_COL_NAV = 0xffcabdab

_COR_MAIN = 51501
_COR_COLORS = (51511, 51512, 51513, 51514, 51515, 51516)
_COR_LEGENDARY = 51510
_ALCHEMY_ORE = 99411
_TIME_ELIXIRS = (100000, 100001, 100002)
_BEANS = (100300, 100400, 100500)
_FLAMES = (100701, 100700)
_FLAME_SHARD = 100702

_GRADE_MYTH = 5
_STEP_HIGHEST = 4
_ROMAN = ("I", "II", "III", "IV", "V", "VI")

_GRADE_DEFAULTS = ("Rough", "Cut", "Rare", "Antique", "Legendary", "Mythic")
_STEP_DEFAULTS = ("Matt", "Clear", "Flawless", "Brilliant", "Excellent")
_TYPE_DEFAULTS = {
	11: "Dragon Diamond", 12: "Dragon Ruby", 13: "Dragon Jade",
	14: "Dragon Sapphire", 15: "Dragon Garnet", 16: "Dragon Onyx",
}

_meta = None


def _LoadMeta():
	global _meta
	if _meta is not None:
		return _meta
	_meta = {}
	txt = ingamewikidungeon._ReadJsonText(_JSON_NAME)
	if not txt:
		return _meta
	try:
		_meta = eval(txt, dict(ingamewikidungeon._JSON_GLOBALS)) or {}
	except Exception:
		try:
			dbg.TraceError("[wikidragonsoul] failed to parse %s" % _JSON_NAME)
		except:
			pass
		_meta = {}
	return _meta


def Reload():
	global _meta
	_meta = None
	return _LoadMeta()


def _InterfaceText(key, default):
	value = getattr(uiScriptLocale, key, default)
	try:
		if not value or value.startswith("Locale not found"):
			return default
	except AttributeError:
		return default
	return value


def _GradeName(i):
	return _InterfaceText("DRAGONSOUL_PAGE_BUTTON_%d" % (i + 1), _GRADE_DEFAULTS[i])


def _StepName(i):
	return LocaleText("WIKI_DS_STEP_%d" % (i + 1), _STEP_DEFAULTS[i])


def _MoneyShort(n):
	try:
		n = int(n)
	except (TypeError, ValueError):
		return "-"
	if n <= 0:
		return "-"
	if n >= 1000000 and n % 1000000 == 0:
		return "%dM" % (n / 1000000)
	if n >= 1000:
		return "%dk" % (n / 1000)
	return str(n)


def _StoneVnum(dsType, grade, step, strength=0):
	return dsType * 10000 + grade * 1000 + step * 100 + strength * 10


class WikiDragonSoulWindow(ingamewikidungeon.WikiDungeonWindow):
	# Inherits the dungeon page's scroll plumbing, widget factories, _ItemIcon
	# (hover tooltip + click-through) and history OpenWindow support.

	_TBL_X0 = 40
	_TBL_W = 476

	def __init__(self):
		ingamewikidungeon.WikiDungeonWindow.__init__(self)
		self._stoneType = 1  # ruby -- the red stone the reference design uses
		self._sectionAnchors = {}
		self._swapRows = []
		self._swapTick = -1

	def OpenPage(self):
		self._ClearContent()
		self._sectionAnchors = {}
		self._swapRows = []
		self._swapTick = -1
		meta = _LoadMeta()

		y = 4
		y = self._RenderHeader(y, meta)
		self._sectionAnchors["overview"] = y
		y = self._RenderOverviewSection(y)
		self._sectionAnchors["refine"] = y
		y = self._RenderClassSection(meta, y)
		y = self._RenderClaritySection(meta, y)
		y = self._RenderLevelSection(meta, y)
		self._sectionAnchors["bonuses"] = y
		y = self._RenderBonusSection(meta, y)
		self._sectionAnchors["set"] = y
		y = self._RenderSetSection(meta, y)
		self._sectionAnchors["customize"] = y
		y = self._RenderCustomizeSection(meta, y)

		deco = self._Img(_ART + "page_end_deco.png", 0, y)
		self._FitWide(deco)
		y += 19 + 8

		self.scrollBoard.SetSize(self.peekWindow.GetWidth(), max(y, self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, 0)
		self.ChangeScrollbar()
		self.Show()

	# -- shared helpers (biolog page conventions) ---------------------------

	def _FitWide(self, img):
		w = img.GetWidth() or 1
		pw = self.peekWindow.GetWidth()
		if w > pw:
			s = float(pw) / w
			img.SetScale(s, s)

	def _RTL(self):
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

	def _Types(self, meta):
		# Type 17 (amethyst / 7th slot) exists in the baked table but is not
		# player-facing -- keep it off the page.
		types = meta.get("types") if meta else None
		if not types:
			types = [[11, "diamond"], [12, "ruby"], [13, "jade"], [14, "sapphire"], [15, "garnet"], [16, "onyx"]]
		return [t for t in types if int(t[0]) != 17][:6]

	def _CurrentTypeNum(self, meta):
		types = self._Types(meta)
		self._stoneType = self._stoneType % len(types)
		return types[self._stoneType][0]

	def _ItemName(self, vnum, default=""):
		try:
			item.SelectItem(vnum)
			name = item.GetItemName()
		except Exception:
			name = ""
		return name or default

	def _StoneName(self, dsType, grade):
		name = self._ItemName(_StoneVnum(dsType, grade, 0))
		if name:
			return name
		typeName = LocaleText("WIKI_DS_TYPE_%d" % (dsType - 10), _TYPE_DEFAULTS.get(dsType, "Dragon Stone"))
		return "%s %s" % (_GradeName(grade), typeName)

	def _StoneIcon(self, vnum, x, y, cell, clickHandler, clickArg):
		# _ItemIcon variant whose click selects a stone type on this page
		# instead of jumping to the item's wiki page; hover tooltip shared.
		item.SelectItem(vnum)
		icon = ui.ExpandedImageBox()
		icon.SetParent(self.scrollBoard)
		icon.LoadImage(item.GetIconImageFileName())
		iw = icon.GetWidth() or cell
		ih = icon.GetHeight() or cell
		scale = min(float(cell) / iw, float(cell) / ih, 1.0)
		if scale < 1.0:
			icon.SetScale(scale, scale)
			iw = int(iw * scale)
			ih = int(ih * scale)
		icon.SetPosition(int(x) + (cell - iw) / 2, int(y) + (cell - ih) / 2)
		if app.USE_CLIP_MASK:
			try:
				icon.SetSubClippingMaskWindow(self.peekWindow)
			except:
				pass
		icon.SAFE_SetStringEvent("MOUSE_OVER_IN", self._OnDropOver, vnum)
		icon.SAFE_SetStringEvent("MOUSE_OVER_OUT", self._OnDropOut)
		icon.SAFE_SetEvent(clickHandler, "mouse_click", clickArg)
		icon.Show()
		self.elements.append(icon)
		return icon

	def _OnRingClick(self, eventType, typeIdx):
		self._stoneType = int(typeIdx)
		self.OpenPage()
		self._OnNavClick("bonuses")

	def _OnCycleStone(self, eventType, dummy):
		types = self._Types(_LoadMeta())
		self._stoneType = (self._stoneType + 1) % len(types)
		pos = self.scrollBoard.GetLocalPosition()[1]
		self.OpenPage()
		span = self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()
		if span > 0 and pos < 0:
			self.scrollBoard.SetPosition(0, max(pos, -span))
			self.ChangeScrollbar()

	def OnUpdate(self):
		if not self.IsShow():
			return
		rows = getattr(self, "_swapRows", None)
		if not rows:
			return
		tick = int(app.GetTime())
		if tick == getattr(self, "_swapTick", -1):
			return
		self._swapTick = tick
		for nameLine, entries in rows:
			idx = tick % len(entries)
			for i in xrange(len(entries)):
				if i == idx:
					entries[i][0].Show()
				else:
					entries[i][0].Hide()
			if nameLine:
				nameLine.SetText(entries[idx][1])

	# -- header: twin navs + stone ring -------------------------------------

	def _RenderHeader(self, y, meta):
		rtl = self._RTL()
		pw = self.peekWindow.GetWidth()
		xA, xB = 8, pw - 200 - 8
		if rtl:
			xA, xB = xB, xA

		navGroups = (
			(xA, (
				("overview", LocaleText("WIKI_DS_OVERVIEW", "Overview")),
				("refine", LocaleText("WIKI_DS_REFINE", "Refine")),
				("bonuses", LocaleText("WIKI_DS_BONUSES", "Bonuses")),
			)),
			(xB, (
				("set", LocaleText("WIKI_DS_SET", "Set Bonus")),
				("customize", LocaleText("WIKI_DS_CUSTOMIZE", "Customize")),
			)),
		)
		for navX, navs in navGroups:
			self._Img(_ART + "title_list_3.png", navX, y + 2)
			labelX = (navX + 152) if rtl else (navX + 48)
			for i in xrange(len(navs)):
				key, label = navs[i]
				rowCy = y + 2 + ingamewikibiolog.WikiBiologWindow._NAV_ROW_CENTERS[i]
				t = self._Text(label, labelX, rowCy - 8, _COL_NAV)
				row = _NavRow()
				row.SetParent(self.scrollBoard)
				row.SetSize(200, 30)
				row.SetPosition(navX, rowCy - 15)
				row.SetNav(t, ui.__mem_func__(self._OnNavClick), key)
				row.Show()
				self.elements.append(row)

		types = self._Types(meta)
		cx = pw / 2
		cy = y + 2 + 63
		for i in xrange(len(types)):
			ang = math.radians(-90.0 + i * (360.0 / max(len(types), 1)))
			ix = cx + int(46 * math.cos(ang)) - 13
			iy = cy + int(46 * math.sin(ang)) - 13
			self._StoneIcon(_StoneVnum(types[i][0], _GRADE_MYTH, _STEP_HIGHEST), ix, iy, 26, self._OnRingClick, i)

		deco = self._Img(_ART + "page_title_deco.png", 0, y + 139)
		self._FitWide(deco)
		return y + 139 + 20 + 8

	# -- generic flat table --------------------------------------------------

	def _RowTable(self, top, widths, headerCells, bodyRows, rowHs):
		# Cells: ("t", text, color) / ("i", vnum) / None. Caller pre-reverses
		# widths and every row for RTL; colX stays visual left-to-right.
		x0 = self._TBL_X0
		total = sum(widths)
		headerH = 20
		colX = []
		x = x0
		for w in widths:
			colX.append(x)
			x += w

		self._Bar(x0, top, total, headerH, self._COL_TABLE_HEADER_BG)
		for c in xrange(len(headerCells)):
			if headerCells[c]:
				self._Text(headerCells[c], colX[c] + widths[c] / 2, top + 4, ingamewikidungeon._COL_TAN, align="center")

		rowY = top + headerH
		bounds = []
		for r in xrange(len(bodyRows)):
			rh = rowHs[r]
			self._Bar(x0, rowY, total, rh, self._COL_TABLE_ROW_BG)
			row = bodyRows[r]
			for c in xrange(len(row)):
				cell = row[c]
				if not cell:
					continue
				if cell[0] == "t":
					color = cell[2] if len(cell) > 2 else self._COL_TABLE_VALUE
					self._Text(cell[1], colX[c] + widths[c] / 2, rowY + rh / 2 - 7, color, align="center")
				elif cell[0] == "i":
					self._ItemIcon(cell[1], colX[c] + (widths[c] - 32) / 2, rowY + (rh - 32) / 2, cellW=32, cellH=32)
			rowY += rh
			bounds.append(rowY)

		tableH = rowY - top
		for c in xrange(1, len(widths)):
			self._Bar(colX[c], top, 1, tableH, self._COL_TABLE_BORDER)
		self._Bar(x0, top, total, 1, self._COL_TABLE_BORDER)
		self._Bar(x0, top + headerH, total, 1, self._COL_TABLE_BORDER)
		for by in bounds:
			self._Bar(x0, by, total, 1, self._COL_TABLE_BORDER)
		self._Bar(x0, top, 1, tableH, self._COL_TABLE_BORDER)
		self._Bar(x0 + total - 1, top, 1, tableH, self._COL_TABLE_BORDER)
		return rowY

	def _SplitWidths(self, labelW, count):
		rest = self._TBL_W - labelW
		w = rest / count
		widths = [labelW] + [w] * count
		widths[-1] += rest - w * count
		return widths

	def _OrderRow(self, cells):
		if self._RTL():
			cells = list(cells)
			cells.reverse()
		return cells

	def _RuleLines(self, y, pairs):
		return self._RuleTable(y, pairs)

	def _ItemRows(self, top, rows):
		rtl = self._RTL()
		pw = self.peekWindow.GetWidth()
		circleX = (pw - 44 - 48) if rtl else 44
		textX = (circleX - 8) if rtl else 116
		rowY = top
		for vnums, desc in rows:
			circle = self._Img(_ART + "itemcircle1.png", circleX, rowY)
			circle.SetScale(0.68, 0.68)
			entries = []
			for vnum in vnums:
				icon = self._ItemIcon(vnum, circleX + 8, rowY + 10, cellW=32, cellH=32)
				entries.append((icon, self._ItemName(vnum, str(vnum))))
			nameLine = self._Text(entries[0][1], textX, rowY + 8, _COL_ITEM_TITLE)
			self._Text(desc, textX, rowY + 26, _COL_DESC)
			if len(entries) > 1:
				for e in entries[1:]:
					e[0].Hide()
				self._swapRows.append((nameLine, entries))
			rowY += 58
		return rowY

	def _ShowcaseStone(self, y, vnum, name, clickable=False):
		cx = self.peekWindow.GetWidth() / 2
		if clickable:
			self._StoneIcon(vnum, cx - 18, y, 36, self._OnCycleStone, 0)
		else:
			self._ItemIcon(vnum, cx - 18, y, cellW=36, cellH=36)
		self._Text(name, cx, y + 40, _COL_GOLD, align="center")
		return y + 58

	# -- Overview ------------------------------------------------------------

	def _RenderOverviewSection(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_DS_OVERVIEW", "Overview"))
		rows = (
			((_COR_MAIN,), LocaleText("WIKI_DS_COR_DESC", "Dropped by monsters. Contains one Cor Draconis of a random colour")),
			(_COR_COLORS, LocaleText("WIKI_DS_COLORCOR_DESC", "Open it to receive a Rough Dragon Stone of its colour")),
			((_COR_LEGENDARY,), LocaleText("WIKI_DS_LEGCOR_DESC", "A rare find that contains a Legendary Dragon Stone")),
			((_ALCHEMY_ORE,), LocaleText("WIKI_DS_ORE_DESC", "Collected while hunting - fill the daily gauge to win Cors")),
			(_TIME_ELIXIRS, LocaleText("WIKI_DS_ELIXIR_DESC", "Recharges the remaining wear time of a Dragon Stone")),
		)
		rowY = self._ItemRows(top, rows)
		rowY += 6
		rowY = self._RuleLines(rowY, (
			("WIKI_DS_RULE1_A", "Dragon Stones only give their bonuses while a deck is active"),
			("WIKI_DS_RULE1_B", "(Ctrl+O). Each stone holds 24 hours of active wear time."),
			("WIKI_DS_RULE2_A", "You must earn the alchemist's qualification before your first"),
			("WIKI_DS_RULE2_B", "activation. Stones live in the Dragon Stone Alchemy window."),
			("WIKI_DS_RULE3_A", "Removing a stone from a deck slot costs 500,000 Yang and"),
			("WIKI_DS_RULE3_B", "requires the deck to be deactivated first."),
			("WIKI_DS_RULE4_A", "The Tongs of Time extract a stone's remaining time into a Time"),
			("WIKI_DS_RULE4_B", "Elixir - higher classes keep a bigger share of the charge."),
			("WIKI_DS_RULE5_A", "Daily Alchemy: the ore drops while hunting (shared across your"),
			("WIKI_DS_RULE5_B", "PC, resets at midnight); a full gauge grants a free Cor reward."),
		))
		return rowY + 12

	# -- Refine: Class / Clarity / Level -------------------------------------

	def _RenderClassSection(self, meta, y):
		top = self._SectionTitle(y, LocaleText("WIKI_DS_CLASS", "Class"))
		top = self._RuleLines(top, (
			("WIKI_DS_CLASS_RULE1_A", "First upgrade: the Class. Combine 2 identical stones of the"),
			("WIKI_DS_CLASS_RULE1_B", "same colour and class at the Alchemist."),
			("WIKI_DS_CLASS_RULE2_A", "Success is guaranteed up to Legendary; Mythic is not"),
			("WIKI_DS_CLASS_RULE2_B", "guaranteed. Each failure adds +5% success (up to +30%)."),
			("WIKI_DS_CLASS_RULE3_A", "A failed attempt keeps the class but resets clarity and level"),
			("WIKI_DS_CLASS_RULE3_B", "and re-rolls the bonuses."),
		)) + 8

		tnum = self._CurrentTypeNum(meta)
		top = self._ShowcaseStone(top, _StoneVnum(tnum, _GRADE_MYTH, 0), self._StoneName(tnum, _GRADE_MYTH)) + 4

		gr = meta.get("grade_refine") or []
		widths = self._SplitWidths(64, 6)
		header = [""] + [_GradeName(g) for g in xrange(6)]
		icons = [None] + [("i", _StoneVnum(tnum, g, 0)) for g in xrange(6)]
		feeLabel = LocaleText("WIKI_DS_ROW_FEE", "Fee")
		succLabel = LocaleText("WIKI_DS_ROW_SUCCESS", "Success")
		fees = [("t", feeLabel, ingamewikidungeon._COL_TAN), ("t", "-")]
		succ = [("t", succLabel, ingamewikidungeon._COL_TAN), ("t", "-")]
		for g in xrange(1, 6):
			row = gr[g - 1] if g - 1 < len(gr) else None
			fees.append(("t", _MoneyShort(row[1]) if row else "-"))
			# The Mythic chance stays hidden (owner request) -- only the
			# guaranteed steps advertise a number.
			if g == 5:
				succ.append(("t", "-"))
			else:
				succ.append(("t", ("%d%%" % row[2]) if row else "-"))

		bottom = self._RowTable(top,
			self._OrderRow(widths), self._OrderRow(header),
			[self._OrderRow(icons), self._OrderRow(fees), self._OrderRow(succ)],
			[40, 18, 18])
		return bottom + 16

	def _RenderClaritySection(self, meta, y):
		top = self._SectionTitle(y, LocaleText("WIKI_DS_CLARITY", "Clarity"))
		top = self._RuleLines(top, (
			("WIKI_DS_CLARITY_RULE1_A", "Second upgrade: the Clarity. Combine 2 identical stones of the"),
			("WIKI_DS_CLARITY_RULE1_B", "same colour, class and clarity."),
			("WIKI_DS_CLARITY_RULE2_A", "60% success, +10% per failure (up to +30%). A failed attempt"),
			("WIKI_DS_CLARITY_RULE2_B", "resets the level and re-rolls the bonuses."),
		)) + 8

		tnum = self._CurrentTypeNum(meta)
		top = self._ShowcaseStone(top, _StoneVnum(tnum, _GRADE_MYTH, _STEP_HIGHEST), self._StoneName(tnum, _GRADE_MYTH)) + 4

		sr = meta.get("step_refine") or []
		widths = self._SplitWidths(64, 5)
		header = [""] + [_StepName(s) for s in xrange(5)]
		icons = [None] + [("i", _StoneVnum(tnum, _GRADE_MYTH, s)) for s in xrange(5)]
		feeLabel = LocaleText("WIKI_DS_ROW_FEE", "Fee")
		succLabel = LocaleText("WIKI_DS_ROW_SUCCESS", "Success")
		fees = [("t", feeLabel, ingamewikidungeon._COL_TAN), ("t", "-")]
		succ = [("t", succLabel, ingamewikidungeon._COL_TAN), ("t", "-")]
		for s in xrange(1, 5):
			row = sr[s - 1] if s - 1 < len(sr) else None
			fees.append(("t", _MoneyShort(row[1]) if row else "-"))
			succ.append(("t", ("%d%%" % row[2]) if row else "-"))

		bottom = self._RowTable(top,
			self._OrderRow(widths), self._OrderRow(header),
			[self._OrderRow(icons), self._OrderRow(fees), self._OrderRow(succ)],
			[40, 18, 18])
		return bottom + 16

	def _RenderLevelSection(self, meta, y):
		top = self._SectionTitle(y, LocaleText("WIKI_DS_LEVEL", "Level"))
		top = self._RuleLines(top, (
			("WIKI_DS_LEVEL_RULE1_A", "Third upgrade: the Level, up to +6. Refine the stone together"),
			("WIKI_DS_LEVEL_RULE1_B", "with a Dragon Bean at the Alchemist."),
			("WIKI_DS_LEVEL_RULE2_A", "On failure the level drops by 1; the bean and the fee are"),
			("WIKI_DS_LEVEL_RULE2_B", "always consumed."),
		)) + 8

		st = meta.get("strength_refine") or []
		widths = [52, 60]
		rest = self._TBL_W - 52 - 60
		w = rest / 6
		widths += [w] * 6
		widths[-1] += rest - w * 6
		header = [LocaleText("WIKI_DS_COL_ITEM", "Item"), LocaleText("WIKI_DS_COL_FEE", "Fee")] + ["+%d" % (i + 1) for i in xrange(6)]
		body = []
		for b in xrange(len(_BEANS)):
			row = st[b] if b < len(st) else None
			cells = [("i", _BEANS[b]), ("t", _MoneyShort(row[0]) if row else "-")]
			for i in xrange(6):
				cells.append(("t", ("%d%%" % row[1][i]) if row else "-"))
			body.append(self._OrderRow(cells))
		bottom = self._RowTable(top, self._OrderRow(widths), self._OrderRow(header), body, [36] * len(_BEANS))
		bottom += 10

		caps = meta.get("strength_max") or []
		if caps:
			rtl = self._RTL()
			labelX = (self.peekWindow.GetWidth() - 46) if rtl else 46
			self._Text(LocaleText("WIKI_DS_MAXLVL_LABEL", "Maximum level by class and clarity:"), labelX, bottom, _COL_ITEM_TITLE)
			bottom += 20
			widths = self._SplitWidths(88, 5)
			header = [""] + [_StepName(s) for s in xrange(5)]
			body = []
			for g in xrange(min(6, len(caps))):
				cells = [("t", _GradeName(g), ingamewikidungeon._COL_TAN)]
				for s in xrange(5):
					cells.append(("t", "+%d" % caps[g][s]))
				body.append(self._OrderRow(cells))
			bottom = self._RowTable(bottom, self._OrderRow(widths), self._OrderRow(header), body, [18] * len(body))
		return bottom + 16

	# -- Bonuses -------------------------------------------------------------

	def _ScaledApply(self, base, maxWeight):
		return int(math.ceil(base * maxWeight / 100.0 - 0.01))

	def _RenderBonusSection(self, meta, y):
		top = self._SectionTitle(y, LocaleText("WIKI_DS_BONUSES", "Bonuses"))
		tnum = self._CurrentTypeNum(meta)
		cx = self.peekWindow.GetWidth() / 2

		top = self._ShowcaseStone(top, _StoneVnum(tnum, _GRADE_MYTH, _STEP_HIGHEST), self._StoneName(tnum, _GRADE_MYTH), clickable=True)
		self._Text(LocaleText("WIKI_DS_CLICK_HINT", "Click the stone to change it"), cx, top, _COL_DESC, align="center")
		top += 15
		self._Text(LocaleText("WIKI_DS_MAXVAL_NOTE", "Values shown at the highest quality (Mythic, Excellent, +6)"), cx, top, _COL_DESC, align="center")
		top += 24

		rtl = self._RTL()
		lineX = (self.peekWindow.GetWidth() - 150) if rtl else 150
		mw = meta.get("max_weight", 160)
		basic = (meta.get("basic") or {}).get(str(tnum)) or []
		add = (meta.get("add") or {}).get(str(tnum)) or []

		self._Text(LocaleText("WIKI_DS_FIXED_LABEL", "Fixed bonuses:"), lineX, top, _COL_ITEM_TITLE)
		top += 17
		for applyType, base in basic:
			self._Text("- " + self._AffectText(applyType, self._ScaledApply(base, mw)), lineX, top, _COL_REWARD)
			top += 15
		top += 6
		self._Text(LocaleText("WIKI_DS_RANDOM_LABEL", "Possible extra bonuses (random):"), lineX, top, _COL_ITEM_TITLE)
		top += 17
		for applyType, base in add:
			self._Text("- " + self._AffectText(applyType, self._ScaledApply(base, mw)), lineX, top, _COL_REWARD)
			top += 15

		top += 8
		top = self._RuleLines(top, (
			("WIKI_DS_COUNT_NOTE_A", "A Rough stone starts with 1 fixed bonus; higher classes add"),
			("WIKI_DS_COUNT_NOTE_B", "more, up to 3 fixed and 3 random bonuses on Mythic."),
		))
		return top + 16

	# -- Set Bonus -----------------------------------------------------------

	def _SetBonusState(self):
		try:
			import systemSetting
			dsWnd = getattr(systemSetting.GetInterfaceHandler(), "wndDragonSoul", None)
			if dsWnd and hasattr(dsWnd, "GetSetBonusState"):
				return dsWnd.GetSetBonusState()
		except Exception:
			pass
		return None

	def _RenderSetSection(self, meta, y):
		top = self._SectionTitle(y, LocaleText("WIKI_DS_SET", "Set Bonus"))
		top = self._RuleLines(top, (
			("WIKI_DS_SET_RULE1_A", "Only Legendary and Mythic stones in your active deck earn set"),
			("WIKI_DS_SET_RULE1_B", "points; higher clarity earns more, the level does not count."),
			("WIKI_DS_SET_RULE2_A", "Reaching a points threshold unlocks the next tier of bonuses;"),
			("WIKI_DS_SET_RULE2_B", "points update instantly whenever your deck changes."),
		)) + 6

		state = self._SetBonusState()
		if state:
			tier, points, nextTh, applys = state
			tierText = _ROMAN[tier] if 0 <= tier < len(_ROMAN) else "-"
			fmt = LocaleText("WIKI_DS_SET_LIVE", "Your active deck: %d points (Tier %s)")
			try:
				line = fmt % (points, tierText)
			except (TypeError, ValueError):
				line = "Your active deck: %d points (Tier %s)" % (points, tierText)
			self._Text(line, self.peekWindow.GetWidth() / 2, top, _COL_GOLD, align="center")
			top += 22

		sp = meta.get("set_points") or []
		if sp:
			widths = self._SplitWidths(88, 5)
			header = [""] + [_StepName(s) for s in xrange(5)]
			body = []
			for gi in xrange(len(sp)):
				cells = [("t", _GradeName(4 + gi), ingamewikidungeon._COL_TAN)]
				for s in xrange(5):
					cells.append(("t", str(sp[gi][s])))
				body.append(self._OrderRow(cells))
			top = self._RowTable(top, self._OrderRow(widths), self._OrderRow(header), body, [18] * len(body)) + 10

		tiers = meta.get("set_tiers") or []
		if tiers:
			widths = [56, 64, self._TBL_W - 56 - 64]
			header = [
				LocaleText("WIKI_DS_COL_TIER", "Tier"),
				LocaleText("WIKI_DS_COL_POINTS", "Points"),
				LocaleText("WIKI_DS_COL_BONUS", "Bonuses"),
			]
			body = []
			for i in xrange(len(tiers)):
				threshold, applies = tiers[i]
				parts = []
				for applyType, value in applies:
					parts.append(self._AffectText(applyType, value))
				cells = [
					("t", _ROMAN[i] if i < len(_ROMAN) else str(i + 1)),
					("t", str(threshold)),
					("t", ", ".join(parts), _COL_REWARD),
				]
				body.append(self._OrderRow(cells))
			top = self._RowTable(top, self._OrderRow(widths), self._OrderRow(header), body, [20] * len(body))
		return top + 16

	# -- Customize (attribute change) ----------------------------------------

	def _RenderCustomizeSection(self, meta, y):
		top = self._SectionTitle(y, LocaleText("WIKI_DS_CUSTOMIZE", "Customize"))
		top = self._RuleLines(top, (
			("WIKI_DS_CUST_RULE1_A", "Re-rolls every bonus of a Legendary or Mythic stone at the"),
			("WIKI_DS_CUST_RULE1_B", "Alchemist. The stone itself is never lost."),
			("WIKI_DS_CUST_RULE2_A", "Each attempt costs 1 Flame of the Dragon plus a 500,000 Yang"),
			("WIKI_DS_CUST_RULE2_B", "fee; all bonuses are re-rolled at once."),
		)) + 8

		top = self._ItemRows(top, (
			(_FLAMES, LocaleText("WIKI_DS_FLAME_DESC", "Changes a stone's bonuses - 1 is needed per attempt")),
			((_FLAME_SHARD,), LocaleText("WIKI_DS_SHARD_DESC", "Collect 10 shards - they transform into a Flame of the Dragon")),
		))
		return top + 16
