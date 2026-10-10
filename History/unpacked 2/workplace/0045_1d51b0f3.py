# coding: latin_1
#
# Growth Pet wiki page: two-column section nav + banner header, then the six
# system sections (overview / base stats & potions / Type ladder / evolution /
# skills & books / leveling & lifetime). Static tables read the shared C++
# tables through the app bridges (growth_pet_tables.hpp -- the same rows the
# server consumes, no pet needs to be summoned); live rows use the player pet
# getters and rebuild through a signature gate so per-kill EXP pushes never
# touch the page.

import app
import ui
import wndMgr
import item
import skill
import player
import localeinfo
import ingamewikidungeon

LocaleText = ingamewikidungeon.LocaleText

_ART = "d:/ymir work/ui/wiki/wiki_new/dungeons/"

_COL_NAME = 0xffffffff
_COL_ITEM_TITLE = 0xffcabdab
_COL_DESC = 0xffa09080
_COL_RULE = 0xffc7c7c7
_COL_LEVEL = 0xffffe6a0
_COL_OK = 0xff8ab98e
_COL_STOP = 0xffc98a8a
_COL_NAV = 0xffcabdab
_COL_NAV_HOVER = 0xffffe6a0

# Mirrors of server constants (growth_pet.cpp s_petTypeStatCapPercent /
# s_petEvoMaxType inverse / GROWTH_PET_TYPE_PITY). Used only when no pet is
# summoned -- a summoned pet overrides them with the live GC201 ladder push.
# Retuning the server tables means retuning these too.
_TYPE_CAP_PERCENT = {1: 3, 2: 5, 3: 8, 4: 10, 5: 10, 6: 15}
_TYPE_EVO_REQ = {2: 1, 3: 2, 4: 2, 5: 3, 6: 4}
_TYPE_PITY = 3
_EVOL_REQ_LEVEL = {2: 40, 3: 80, 4: 81}

# The distributed skill books = the Book Shop stock (shop_table_ex.txt vnum
# 3340, opened by right-clicking the token item; 100M Yang + 10 tokens each).
# Skill id = DB dwSkillVnum = book Value0 -- NOT the client EPetSkill enum
# (7/8 and 21/22 are swapped there); everything in this module stays in the
# DB id space.
_SKILL_BOOKS = (
	(55014, 5),    # Att Stone
	(55015, 6),    # Berserker
	(55017, 8),    # Haste
	(55018, 9),    # Drill
	(55022, 13),   # Bulwark
	(55034, 19),   # Att Warrior
	(55035, 20),   # Att Sura
	(55036, 21),   # Eagle Eyes
	(55037, 22),   # Att Boss
	(55039, 24),   # Att Ninja
	(55040, 25),   # Att Shaman
)

_TOKEN_ITEM = 55009
_FEEDSTUFF_ITEM = 55001
_PET_BAG_ITEM = 55002
_EXPFOOD_ITEM = 55028
_EGG_ITEM = 55401
_PET_SKIN_ITEMS = (53250, 34341, 53001, 53277)
_PET_SKIN_ENCHANT = 79771
# Timed AFFECT_PET_EXP boosters (char_item.cpp:5900): battle-EXP divisor
# 16 -> 8 while active = double pet EXP. (vnum, fallback duration seconds).
_EXP_BOOST_ITEMS = ((99104, 1800), (99102, 3600), (99103, 10800))

_OVERVIEW_ITEM_PET = 55701
_OVERVIEW_ITEM_POTION = 55107
_OVERVIEW_ITEM_BOOK = 55014


def _Money(n):
	try:
		n = int(n)
	except (TypeError, ValueError):
		return str(n)
	s = str(n)
	out = ""
	while len(s) > 3:
		out = "," + s[-3:] + out
		s = s[:-3]
	return s + out


def _Pct(p):
	return ("%g" % p) + "%"


def _SkillValueText(skillId, value, actPct, durDeci):
	# Compact per-cell values (the sentence formats in PetSkillToolTip are for
	# tooltips; the book icon hover still shows those). Special shapes mirror
	# uitooltip.__PetSkillBookValueText, keyed by DB id.
	if not value and not actPct:
		return "-"
	if 23 == skillId:
		return "%d%% / %d-%d" % (actPct, value, value * 2)
	if 17 == skillId:
		return "%d%% / %.1fs" % (actPct, value / 10.0)
	if 10 == skillId:
		return "%d%% / +%d HP" % (actPct, value)
	if 18 == skillId:
		return "%d%%" % actPct
	return "%d%%" % value


def _SkillName(skillId):
	try:
		name = skill.GetPetSkillInfo(skillId)[0]
		if name:
			return name
	except Exception:
		pass
	return str(skillId)


def _StageName(evol):
	name = getattr(localeinfo, "PET_INFORMATION_STAGE%d" % max(1, min(4, int(evol))), "")
	if not name or str(name).startswith("Locale not found"):
		return ""
	return name


def _ActivePetId():
	try:
		return player.GetActivePetItemId()
	except Exception:
		return 0


def _PetTypeInfo():
	# (type, typeMax, evoCeiling, failCount, pityMax, chance, capPermille,
	# nextCapPermille); zeros until the summon push arrives.
	try:
		info = player.GetPetTypeInfo()
		if info and info[0]:
			return info
	except Exception:
		pass
	return None


class _NavRow(ui.Window):
	# Click/hover catcher over one brush stripe of title_list_3.png (clone of
	# the biolog page's row: plain pickable Window, no "attach" -- FLAG_ATTACH
	# would send the button events to GetRoot() and clicks would die silently).
	def __init__(self):
		ui.Window.__init__(self)
		self.navText = None
		self.navEvent = None
		self.navKey = None

	def SetNav(self, textLine, event, key):
		self.navText = textLine
		self.navEvent = event
		self.navKey = key

	def OnMouseOverIn(self):
		t = getattr(self, "navText", None)
		if t:
			t.SetPackedFontColor(_COL_NAV_HOVER)

	def OnMouseOverOut(self):
		t = getattr(self, "navText", None)
		if t:
			t.SetPackedFontColor(_COL_NAV)

	def OnMouseLeftButtonDown(self):
		ev = getattr(self, "navEvent", None)
		if ev:
			ev(self.navKey)
		return True


class WikiGrowthPetWindow(ingamewikidungeon.WikiDungeonWindow):
	# Inherits the dungeon page's scroll plumbing, widget factories, _ItemIcon
	# (hover tooltip + click-through) and history OpenWindow support.

	_NAV_ROW_CENTERS = (21, 57, 93)
	_TBL_X0 = 40
	_TBL_W = 476
	_TBL_HEADER_H = 24
	_SIG_POLL_INTERVAL = 0.5
	_MARQUEE_DELAY = 0.35
	_MARQUEE_SPEED = 40.0
	_MARQUEE_PAD = 4

	def OpenPage(self):
		self._ClearContent()
		self._sectionAnchors = {}
		self._liveSigAtRender = self._LiveSig()
		self._lastSigPoll = 0.0
		self._marqueeItems = []
		self._marqueeHot = None
		self._marqueeOffset = 0.0
		self._marqueeDone = False
		self._marqueeSince = 0.0
		self._marqueeTime = 0.0
		self._swapRows = []
		self._swapPhase = -1

		y = 4
		y = self._RenderHeader(y)
		self._sectionAnchors["overview"] = y
		y = self._RenderOverview(y)
		self._sectionAnchors["stats"] = y
		y = self._RenderStats(y)
		self._sectionAnchors["types"] = y
		y = self._RenderTypes(y)
		self._sectionAnchors["evolution"] = y
		y = self._RenderEvolution(y)
		self._sectionAnchors["skills"] = y
		y = self._RenderSkills(y)
		self._sectionAnchors["journey"] = y
		y = self._RenderJourney(y)

		deco = self._Img(_ART + "page_end_deco.png", 0, y)
		self._FitWide(deco)
		y += 19 + 8

		self.scrollBoard.SetSize(self.peekWindow.GetWidth(), max(y, self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, 0)
		self.ChangeScrollbar()
		self.Show()

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

	# -- live-state signature gate ------------------------------------------

	def _LiveSig(self):
		petId = _ActivePetId()
		if not petId:
			return (0,)
		parts = [petId]
		try:
			info = player.GetPetItem(petId)
			parts.append(int(info[0]))
			parts.append(int(info[1]))
			parts.append(int(info[4] * 10))
			parts.append(int(info[5] * 10))
			parts.append(int(info[6] * 10))
		except Exception:
			pass
		t = _PetTypeInfo()
		if t:
			parts.append(t[0])
			parts.append(t[3])
		try:
			lv = []
			for i in xrange(6):
				s = player.GetPetSkillByIndex(petId, i)
				lv.append((s[0], s[1]))
			parts.append(tuple(lv))
		except Exception:
			pass
		return tuple(parts)

	def OnUpdate(self):
		if not self.IsShow():
			return
		self._MarqueeTick()
		now = app.GetTime()

		# Rotating overview rows (biolog pattern): name and thereby the
		# hover/click target swaps together with the icon.
		rows = getattr(self, "_swapRows", None)
		if rows:
			phase = int(now)
			if phase != getattr(self, "_swapPhase", -1):
				self._swapPhase = phase
				for nameLine, entries in rows:
					idx = phase % len(entries)
					for i in xrange(len(entries)):
						if i == idx:
							entries[i][0].Show()
						else:
							entries[i][0].Hide()
					nameLine.SetText(entries[idx][1])

		if now - getattr(self, "_lastSigPoll", 0.0) < self._SIG_POLL_INTERVAL:
			return
		self._lastSigPoll = now
		sig = self._LiveSig()
		if sig == getattr(self, "_liveSigAtRender", sig):
			return
		pos = self.scrollBoard.GetLocalPosition()[1]
		self.OpenPage()
		span = self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()
		if span > 0 and pos < 0:
			self.scrollBoard.SetPosition(0, max(pos, -span))
			self.ChangeScrollbar()

	# -- header --------------------------------------------------------------

	def _RenderHeader(self, y):
		rtl = self._RTL()
		pw = self.peekWindow.GetWidth()
		leftX = 8
		rightX = pw - 200 - 8

		navCols = (
			(
				("overview", LocaleText("WIKI_PET_NAV_OVERVIEW", "Overview")),
				("stats", LocaleText("WIKI_PET_NAV_STATS", "Stats & Potions")),
				("types", LocaleText("WIKI_PET_NAV_TYPES", "Pet Types")),
			),
			(
				("evolution", LocaleText("WIKI_PET_NAV_EVOLUTION", "Evolution")),
				("skills", LocaleText("WIKI_PET_NAV_SKILLS", "Skills & Books")),
				("journey", LocaleText("WIKI_PET_NAV_JOURNEY", "Leveling & Lifetime")),
			),
		)
		for ci in xrange(2):
			navX = (leftX, rightX)[(1 - ci) if rtl else ci]
			labelX = (navX + 152) if rtl else (navX + 48)
			self._Img(_ART + "title_list_3.png", navX, y + 2)
			for i in xrange(len(navCols[ci])):
				key, label = navCols[ci][i]
				rowCy = y + 2 + self._NAV_ROW_CENTERS[i]
				t = self._Text(label, labelX, rowCy - 8, _COL_NAV)
				row = _NavRow()
				row.SetParent(self.scrollBoard)
				row.SetSize(200, 30)
				row.SetPosition(navX, rowCy - 15)
				row.SetNav(t, ui.__mem_func__(self._OnNavClick), key)
				row.Show()
				self.elements.append(row)

		gap = rightX - (leftX + 200)
		scale = min(0.62, float(gap - 8) / 204.0)
		banner = self._Img(_ART + "banners/12.png", 0, y)
		banner.SetScale(scale, scale)
		bw = int(204 * scale)
		bh = int(133 * scale)
		banner.SetPosition((pw - bw) / 2, y + 2 + (127 - bh) / 2)

		deco = self._Img(_ART + "page_title_deco.png", 0, y + 133)
		self._FitWide(deco)
		return y + 133 + 20 + 8

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

	# -- shared bits ---------------------------------------------------------

	def _SectionTitle(self, y, label):
		self._Img(_ART + "subtitle.png", (556 - 495) / 2, y)
		self._Text(label, 447 if self._RTL() else 108, y + 11, _COL_NAME)
		return y + 48

	def _RuleLines(self, y, rules):
		# rules: ((key, default), ...) A/B pairs, one bordered centred row per
		# pair (shared _RuleTable restyle).
		return self._RuleTable(y, rules)

	def _TableGrid(self, x0, top, w, seq, colX, colW, rowBounds):
		tableH = rowBounds[-1] - top
		for li in seq[:-1]:
			self._Bar(colX[li] + colW[li], top, 1, tableH, self._COL_TABLE_BORDER)
		self._Bar(x0, top, w, 1, self._COL_TABLE_BORDER)
		self._Bar(x0, top + self._TBL_HEADER_H, w, 1, self._COL_TABLE_BORDER)
		for by in rowBounds:
			self._Bar(x0, by, w, 1, self._COL_TABLE_BORDER)
		self._Bar(x0, top, 1, tableH, self._COL_TABLE_BORDER)
		self._Bar(x0 + w - 1, top, 1, tableH, self._COL_TABLE_BORDER)

	def _TableLayout(self, widths, order):
		# widths: logical-index tuple; order: logical indices in LTR visual
		# order. RTL reverses the visual order; colX stays keyed logically.
		seq = tuple(reversed(order)) if self._RTL() else tuple(order)
		colX = {}
		x = self._TBL_X0
		for li in seq:
			colX[li] = x
			x += widths[li]
		return seq, colX

	def _TableHeader(self, top, seq, colX, widths, headers):
		self._Bar(self._TBL_X0, top, self._TBL_W, self._TBL_HEADER_H, self._COL_TABLE_HEADER_BG)
		for li in seq:
			self._CellText(headers[li], colX[li], widths[li], top + 6, ingamewikidungeon._COL_TAN)

	def _CellText(self, s, cellX, cellW, y, color, align="center"):
		# Marquee-aware cell text (guild contract-card mechanism): text wider
		# than its cell anchors at the reading edge and, on hover, slides
		# inside a screen-space clip rect re-applied each tick by
		# _MarqueeTick. Fitting text renders exactly like a plain _Text.
		pad = self._MARQUEE_PAD
		rtl = self._RTL()
		if align == "center":
			t = self._Text(s, cellX + cellW / 2, y, color, align="center")
		else:
			t = self._Text(s, (cellX + cellW - pad) if rtl else (cellX + pad), y, color)
		if not s or not app.USE_CLIP_MASK:
			return t
		try:
			fullW = t.GetTextSize()[0]
		except Exception:
			return t
		viewW = cellW - pad * 2
		if fullW <= viewW:
			return t
		t.SetHorizontalAlignLeft()
		baseX = (cellX + cellW - pad) if rtl else (cellX + pad)
		t.SetPosition(int(baseX), int(y))
		self._marqueeItems.append({
			"obj": t,
			"baseX": int(baseX),
			"y": int(y),
			"boxX": int(cellX + pad),
			"viewW": int(viewW),
			"fullW": int(fullW),
			"rtl": rtl,
		})
		return t

	def _MarqueeTick(self):
		items = getattr(self, "_marqueeItems", None)
		if not items:
			return
		now = app.GetTime()
		dt = now - getattr(self, "_marqueeTime", 0.0)
		self._marqueeTime = now
		if dt <= 0.0 or dt > 0.5:
			dt = 0.0
		sbX, sbY = self.scrollBoard.GetGlobalPosition()
		pkX, pkY = self.peekWindow.GetGlobalPosition()
		pkR = pkX + self.peekWindow.GetWidth()
		pkB = pkY + self.peekWindow.GetHeight()
		mx, my = wndMgr.GetMousePosition()

		hot = None
		for e in items:
			bx = sbX + e["boxX"]
			by = sbY + e["y"] - 2
			if mx >= bx and mx < bx + e["viewW"] and my >= by and my < by + 18:
				hot = e
				break
		if hot is not getattr(self, "_marqueeHot", None):
			old = getattr(self, "_marqueeHot", None)
			if old is not None:
				old["obj"].SetPosition(old["baseX"], old["y"])
			self._marqueeHot = hot
			self._marqueeOffset = 0.0
			self._marqueeDone = False
			self._marqueeSince = now

		hot = self._marqueeHot
		if hot is not None and not self._marqueeDone and now - self._marqueeSince >= self._MARQUEE_DELAY:
			travel = hot["fullW"] - hot["viewW"]
			self._marqueeOffset += self._MARQUEE_SPEED * dt
			if self._marqueeOffset >= travel:
				self._marqueeOffset = float(travel)
				self._marqueeDone = True
			# Arabic text grows leftward from its anchor, so revealing the
			# hidden head means sliding the anchor the other way.
			if hot["rtl"]:
				hot["obj"].SetPosition(int(hot["baseX"] + self._marqueeOffset), hot["y"])
			else:
				hot["obj"].SetPosition(int(hot["baseX"] - self._marqueeOffset), hot["y"])

		# Masks are screen-space: re-clip every tick (the page scrolls and the
		# clip must also never exceed the peek viewport, or a slid line would
		# bleed outside the pane).
		for e in items:
			l = sbX + e["boxX"]
			r = l + e["viewW"]
			t = sbY + e["y"] - 2
			b = t + 18
			l = max(l, pkX)
			r = min(r, pkR)
			t = max(t, pkY)
			b = min(b, pkB)
			if r < l:
				r = l
			if b < t:
				b = t
			try:
				e["obj"].SetClippingMaskRect(int(l), int(t), int(r), int(b))
			except Exception:
				pass

	def _ItemEffectTable(self, top, rows):
		widths = (48, 150, 278)
		COL_ICON, COL_ITEM, COL_EFFECT = 0, 1, 2
		seq, colX = self._TableLayout(widths, (COL_ICON, COL_ITEM, COL_EFFECT))
		headers = (
			"",
			LocaleText("PET_UP_HELP_COL_ITEM", "Item"),
			LocaleText("WIKI_PET_COL_EFFECT", "Effect"),
		)
		self._TableHeader(top, seq, colX, widths, headers)
		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for vnum, effect in rows:
			rowH = 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			textY = rowY + rowH / 2 - 7
			iconX = colX[COL_ICON] + (widths[COL_ICON] - 32) / 2
			self._ItemIcon(vnum, iconX, rowY + (rowH - 32) / 2, cellW=32, cellH=32)
			self._CellText(self._ItemName(vnum), colX[COL_ITEM], widths[COL_ITEM], textY, ingamewikidungeon._COL_TAN)
			self._CellText(effect, colX[COL_EFFECT], widths[COL_EFFECT], textY, self._COL_TABLE_VALUE)
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)
		return rowY

	def _BoostDuration(self, vnum, fallbackSec):
		try:
			item.SelectItem(vnum)
			sec = item.GetValue(0) or fallbackSec
		except Exception:
			sec = fallbackSec
		sec = int(sec)
		if sec >= 3600 and sec % 3600 == 0:
			return "%dh" % (sec / 3600)
		return "%dm" % (sec / 60)

	def _MatStrip(self, mats, colXv, colWv, rowY, rowH):
		mats = [m for m in (mats or []) if m and m[0]]
		if not mats:
			self._Text("-", colXv + colWv / 2, rowY + rowH / 2 - 7, self._COL_TABLE_VALUE, align="center")
			return
		pitch = 34
		startX = colXv + (colWv - len(mats) * pitch) / 2 + 1
		iconY = rowY + (rowH - 32) / 2
		for i in xrange(len(mats)):
			try:
				cnt = int(mats[i][1])
			except (TypeError, ValueError, IndexError):
				cnt = 0
			self._ItemIcon(mats[i][0], startX + i * pitch, iconY, cnt, cellW=32, cellH=32)

	# -- Overview ------------------------------------------------------------

	def _RenderOverview(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_PET_NAV_OVERVIEW", "Overview"))
		rtl = self._RTL()
		pw = self.peekWindow.GetWidth()
		circleX = (pw - 44 - 48) if rtl else 44
		textX = (circleX - 8) if rtl else 116

		rows = (
			((_OVERVIEW_ITEM_PET,), LocaleText("WIKI_PET_OV_PET", "Hunts with you, levels up and grows on 3 axes")),
			((_OVERVIEW_ITEM_POTION,), LocaleText("WIKI_PET_OV_POTION", "Potions raise its base stats - guaranteed, no fail")),
			((_OVERVIEW_ITEM_BOOK,), LocaleText("WIKI_PET_OV_BOOK", "Books teach up to 6 skills at high pet level")),
			(_PET_SKIN_ITEMS, LocaleText("WIKI_PET_SKIN_DESC", "Changes the pet's look + own timed bonuses")),
			((_PET_SKIN_ENCHANT,), LocaleText("WIKI_PET_SKIN_ENCH_DESC", "Enchants a pet skin with extra timed bonuses")),
		)
		rowY = top
		for vnums, desc in rows:
			circle = self._Img(_ART + "itemcircle1.png", circleX, rowY)
			circle.SetScale(0.68, 0.68)
			entries = []
			for vnum in vnums:
				icon = self._ItemIcon(vnum, circleX + 8, rowY + 10, cellW=32, cellH=32)
				entries.append((icon, self._ItemName(vnum)))
			nameLine = self._Text(entries[0][1], textX, rowY + 8, _COL_ITEM_TITLE)
			self._Text(desc, textX, rowY + 26, _COL_DESC)
			if len(entries) > 1:
				for e in entries[1:]:
					e[0].Hide()
				self._swapRows.append((nameLine, entries))
			rowY += 58

		rowY += 6
		rowY = self._RuleLines(rowY, (
			("WIKI_PET_RULE1_A", "Open the Companion window (P) and switch to the Pet tab to"),
			("WIKI_PET_RULE1_B", "manage, feed and upgrade your pet."),
			("WIKI_PET_RULE2_A", "The pet gains battle EXP from your kills - it can never level"),
			("WIKI_PET_RULE2_B", "above your own character level."),
			("WIKI_PET_RULE3_A", "Level & Evolution are the spine: they unlock the Type ladder"),
			("WIKI_PET_RULE3_B", "(stat caps) and the skill slots."),
		))

		petId = _ActivePetId()
		if petId:
			try:
				info = player.GetPetItem(petId)
				t = _PetTypeInfo()
				stageName = _StageName(info[1])
				line = LocaleText("WIKI_PET_LIVE_FMT", "Your pet: %s - %s - Lv. %s - Type %s/%s") % (
					info[3], stageName, int(info[0]),
					t and t[0] or "?", t and t[1] or 6)
				rowY += 6
				self._Bar(self._TBL_X0, rowY, self._TBL_W, 26, self._COL_TABLE_HEADER_BG)
				self._CellText(line, self._TBL_X0, self._TBL_W, rowY + 6, _COL_LEVEL)
				rowY += 26
			except Exception:
				pass

		return rowY + 12

	# -- Base Stats & Potions ------------------------------------------------

	def _RenderStats(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_PET_NAV_STATS", "Stats & Potions"))

		petStats = (None, None, None)
		petId = _ActivePetId()
		if petId:
			try:
				info = player.GetPetItem(petId)
				# GetPetItem order is (hp, def, sp); display rows are
				# HP / Attack(sp) / Elemental(def) -- deliberate swap.
				petStats = (info[4], info[6], info[5])
			except Exception:
				pass

		widths = (170, 80, 96, 130)
		COL_STAT, COL_START, COL_STEP, COL_MY = 0, 1, 2, 3
		seq, colX = self._TableLayout(widths, (COL_STAT, COL_START, COL_STEP, COL_MY))
		headers = (
			LocaleText("WIKI_PET_COL_STAT", "Stat"),
			LocaleText("WIKI_PET_COL_START", "Start"),
			LocaleText("WIKI_PET_COL_STEP", "Per Potion"),
			LocaleText("WIKI_PET_COL_MY", "Your Pet"),
		)
		self._TableHeader(top, seq, colX, widths, headers)

		statNames = (
			LocaleText("COMPANION_PET_STAT_HP", "Max HP"),
			LocaleText("COMPANION_PET_STAT_ATT", "Attack PvM / PvP"),
			LocaleText("COMPANION_PET_STAT_ATTVALUE", "Elemental Power"),
		)
		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for i in xrange(3):
			rowH = 26
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			textY = rowY + rowH / 2 - 7
			self._CellText(statNames[i], colX[COL_STAT], widths[COL_STAT], textY, ingamewikidungeon._COL_TAN)
			self._Text("0.1%", colX[COL_START] + widths[COL_START] / 2, textY, self._COL_TABLE_VALUE, align="center")
			self._Text("+0.2%", colX[COL_STEP] + widths[COL_STEP] / 2, textY, _COL_OK, align="center")
			my = petStats[i]
			myText = ("%.1f%%" % my) if my is not None else "-"
			self._Text(myText, colX[COL_MY] + widths[COL_MY] / 2, textY, _COL_LEVEL if my is not None else self._COL_TABLE_VALUE, align="center")
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)

		rowY += 10
		pWidths = (90, 160, 226)
		COL_SIZE, COL_POTS, COL_UPTO = 0, 1, 2
		pSeq, pColX = self._TableLayout(pWidths, (COL_SIZE, COL_POTS, COL_UPTO))
		pHeaders = (
			LocaleText("WIKI_PET_COL_SIZE", "Size"),
			LocaleText("WIKI_PET_COL_POTIONS", "Potions"),
			LocaleText("WIKI_PET_COL_UPTO", "Raises up to"),
		)
		pTop = rowY
		self._TableHeader(pTop, pSeq, pColX, pWidths, pHeaders)

		try:
			import uicompanion
			families = uicompanion.PET_STAT_POTION_VNUMS
		except Exception:
			families = ((0, 0, 0),) * 3
		sizeRows = (
			(LocaleText("WIKI_PET_POT_S", "Small"), 0, 5),
			(LocaleText("WIKI_PET_POT_M", "Medium"), 1, 10),
			(LocaleText("WIKI_PET_POT_L", "Large"), 2, 15),
		)
		uptoFmt = LocaleText("WIKI_PET_POT_UPTO_FMT", "up to %s")
		rowY = pTop + self._TBL_HEADER_H
		rowBounds = []
		for label, sizeIdx, cap in sizeRows:
			rowH = 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			textY = rowY + rowH / 2 - 7
			self._CellText(label, pColX[COL_SIZE], pWidths[COL_SIZE], textY, ingamewikidungeon._COL_TAN)
			mats = []
			for fam in families:
				try:
					if fam[sizeIdx]:
						mats.append((fam[sizeIdx], 0))
				except (IndexError, TypeError):
					pass
			self._MatStrip(mats, pColX[COL_POTS], pWidths[COL_POTS], rowY, rowH)
			self._CellText(uptoFmt % _Pct(cap), pColX[COL_UPTO], pWidths[COL_UPTO], textY, self._COL_TABLE_VALUE)
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, pTop, self._TBL_W, pSeq, pColX, pWidths, rowBounds)

		rowY += 10
		rowY = self._RuleLines(rowY, (
			("WIKI_PET_STAT_RULE1_A", "Every potion adds exactly +0.2% to one stat - guaranteed,"),
			("WIKI_PET_STAT_RULE1_B", "there is no fail chance."),
			("WIKI_PET_STAT_RULE2_A", "The real ceiling is the LOWER of the potion size and your"),
			("WIKI_PET_STAT_RULE2_B", "pet's Type cap - see the Pet Types section."),
			("WIKI_PET_STAT_RULE3_A", "A potion that cannot raise the stat any further is refused,"),
			("WIKI_PET_STAT_RULE3_B", "not wasted."),
		))

		t = _PetTypeInfo()
		if t and t[6]:
			capFmt = LocaleText("PET_HELP_GEN_CURCAP_FMT", "Your pet's current stat cap: %.1f%%")
			try:
				self._Text(capFmt % (t[6] / 10.0), (self.peekWindow.GetWidth() - 46) if self._RTL() else 46, rowY + 2, _COL_LEVEL)
				rowY += 17
			except Exception:
				pass

		return rowY + 12

	# -- Pet Types -----------------------------------------------------------

	def _TypeLadderRung(self, target):
		# Live rung (pushed with a summoned pet) wins; the static app bridge
		# and the constant mirrors cover the no-pet case.
		cap = _TYPE_CAP_PERCENT.get(target, 0)
		evoReq = _TYPE_EVO_REQ.get(target, 0)
		chance, yang, mats = 0, 0, []
		try:
			(yang, chance, mats) = app.GetPetTypeUpgradeReq(target)
		except Exception:
			pass
		try:
			rung = player.GetPetTypeLadderRung(target)
			if rung and rung[0]:
				cap = rung[0] / 10.0
				chance = rung[1] or chance
				evoReq = rung[2] or evoReq
				yang = rung[3] or yang
				mats = [m for m in rung[4:] if m and m[0]] or mats
		except Exception:
			pass
		return cap, evoReq, chance, yang, mats

	def _RenderTypes(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_PET_NAV_TYPES", "Pet Types"))

		top = self._RuleLines(top, (
			("WIKI_PET_TYPE_RULE1_A", "Every pet hatches at Type 1. A higher Type raises the cap"),
			("WIKI_PET_TYPE_RULE1_B", "each base stat can be pushed to with potions."),
			("WIKI_PET_TYPE_RULE2_A", "Each attempt consumes the materials and Yang and can fail -"),
			("WIKI_PET_TYPE_RULE2_B", "after 3 failed tries the next attempt is guaranteed."),
			("WIKI_PET_TYPE_RULE3_A", "A Type 6 pet also masters its skills: level-20 skills gain"),
			("WIKI_PET_TYPE_RULE3_B", "an extra mastery value (see Skills & Books)."),
		)) + 6

		widths = (44, 56, 62, 56, 174, 84)
		COL_TYPE, COL_CAP, COL_EVO, COL_CHANCE, COL_MATS, COL_YANG = 0, 1, 2, 3, 4, 5
		seq, colX = self._TableLayout(widths, (COL_TYPE, COL_CAP, COL_EVO, COL_CHANCE, COL_MATS, COL_YANG))
		headers = (
			LocaleText("PET_UP_HELP_COL_TYPE", "Type"),
			LocaleText("PET_UP_HELP_COL_CAP", "Stat cap"),
			LocaleText("WIKI_PET_COL_EVO", "Needs Evo"),
			LocaleText("WIKI_PET_COL_CHANCE", "Success"),
			LocaleText("WIKI_PET_COL_MATS", "Materials"),
			LocaleText("PET_UP_HELP_YANG", "Yang"),
		)
		self._TableHeader(top, seq, colX, widths, headers)

		t = _PetTypeInfo()
		currentType = t and t[0] or 0

		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for target in xrange(1, 7):
			if 1 == target:
				cap = self._TypeLadderRung(1)[0]
				evoReq, chance, yang, mats = 0, 0, 0, []
				rowH = 26
			else:
				cap, evoReq, chance, yang, mats = self._TypeLadderRung(target)
				rowH = 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			if target == currentType:
				self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, 0x1effe6a0)
			textY = rowY + rowH / 2 - 7
			typeColor = _COL_LEVEL if target == currentType else ingamewikidungeon._COL_TAN
			self._Text(str(target), colX[COL_TYPE] + widths[COL_TYPE] / 2, textY, typeColor, align="center")
			self._Text(_Pct(cap), colX[COL_CAP] + widths[COL_CAP] / 2, textY, self._COL_TABLE_VALUE, align="center")
			self._Text(str(evoReq) if evoReq else "-", colX[COL_EVO] + widths[COL_EVO] / 2, textY, self._COL_TABLE_VALUE, align="center")
			self._Text(("%d%%" % chance) if chance else "-", colX[COL_CHANCE] + widths[COL_CHANCE] / 2, textY, self._COL_TABLE_VALUE, align="center")
			if 1 == target:
				self._CellText(LocaleText("WIKI_PET_TYPE_START", "(start)"), colX[COL_MATS], widths[COL_MATS], textY, self._COL_TABLE_VALUE)
				self._Text("-", colX[COL_YANG] + widths[COL_YANG] / 2, textY, self._COL_TABLE_VALUE, align="center")
			else:
				self._MatStrip(mats, colX[COL_MATS], widths[COL_MATS], rowY, rowH)
				self._CellText(_Money(yang), colX[COL_YANG], widths[COL_YANG], textY, self._COL_TABLE_VALUE)
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)

		rowY += 8
		if t and t[3]:
			pityFmt = LocaleText("WIKI_PET_TYPE_PITY_FMT", "Failed attempts so far: %s/%s - the next one is guaranteed after %s.")
			self._Text(pityFmt % (t[3], t[4] or _TYPE_PITY, t[4] or _TYPE_PITY),
				(self.peekWindow.GetWidth() - 46) if self._RTL() else 46, rowY, _COL_STOP)
			rowY += 17

		return rowY + 12

	# -- Evolution -----------------------------------------------------------

	def _RenderEvolution(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_PET_NAV_EVOLUTION", "Evolution"))

		try:
			import uipetinfo
			evolveMats = uipetinfo.EVOLVE_MATERIALS_DICT
		except Exception:
			evolveMats = {}

		widths = (120, 60, 116, 180)
		COL_STAGE, COL_LV, COL_REQ, COL_MATS = 0, 1, 2, 3
		seq, colX = self._TableLayout(widths, (COL_STAGE, COL_LV, COL_REQ, COL_MATS))
		headers = (
			LocaleText("PET_UP_HELP_COL_STAGE", "Evolution"),
			LocaleText("PET_UP_HELP_COL_LEVEL", "Pet Lv."),
			LocaleText("WIKI_PET_COL_REQ", "Requires"),
			LocaleText("WIKI_PET_COL_MATS", "Materials"),
		)
		self._TableHeader(top, seq, colX, widths, headers)

		stageFmt = LocaleText("PET_UP_HELP_STAGE_FMT", "Evo %d")
		reqExp = LocaleText("WIKI_PET_EVO_REQ_EXP", "Full EXP bar")
		reqAge = LocaleText("WIKI_PET_EVO_REQ_AGE", "Age 1+ day")

		petEvol = 0
		petId = _ActivePetId()
		if petId:
			try:
				petEvol = int(player.GetPetItem(petId)[1])
			except Exception:
				petEvol = 0

		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for target in (2, 3, 4):
			rowH = 40
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			if petEvol and target == petEvol + 1:
				self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, 0x1effe6a0)
			stageName = _StageName(target)
			cx = colX[COL_STAGE] + widths[COL_STAGE] / 2
			self._Text(stageFmt % target, cx, rowY + 5, ingamewikidungeon._COL_TAN, align="center")
			self._CellText(stageName, colX[COL_STAGE], widths[COL_STAGE], rowY + 21, self._COL_TABLE_VALUE)
			textY = rowY + rowH / 2 - 7
			self._Text(str(_EVOL_REQ_LEVEL[target]), colX[COL_LV] + widths[COL_LV] / 2, textY, _COL_LEVEL, align="center")
			self._CellText(reqAge if 4 == target else reqExp, colX[COL_REQ], widths[COL_REQ], textY, self._COL_TABLE_VALUE)
			self._MatStrip(evolveMats.get(target - 1), colX[COL_MATS], widths[COL_MATS], rowY, rowH)
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)

		rowY += 10
		rowY = self._RuleLines(rowY, (
			("WIKI_PET_EVO_RULE1_A", "Your pet stops leveling at 40 and 80 until you evolve it -"),
			("WIKI_PET_EVO_RULE1_B", "evolution itself is guaranteed, but resets the EXP bar."),
			("WIKI_PET_EVO_RULE2_A", "Each evolution raises the Type ceiling: Evo 1 allows Type 2,"),
			("WIKI_PET_EVO_RULE2_B", "Evo 2 allows Type 4, Evo 3 Type 5 and Evo 4 Type 6."),
			("WIKI_PET_EVO_RULE3_A", "The final evolution (Heroic) changes your pet's appearance"),
			("WIKI_PET_EVO_RULE3_B", "and is the gateway to the skill levels 90/105."),
		))

		return rowY + 12

	# -- Skills & Books ------------------------------------------------------

	def _LearnedSkills(self):
		petId = _ActivePetId()
		if not petId:
			return {}
		learned = {}
		try:
			for i in xrange(6):
				s = player.GetPetSkillByIndex(petId, i)
				if s[0] and s[1]:
					learned[s[0]] = s[1]
		except Exception:
			pass
		return learned

	def _RenderSkills(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_PET_NAV_SKILLS", "Skills & Books"))

		slotLv1 = getattr(player, "PET_GROWTH_SKILL_OPEN_LEVEL_1", 90)
		slotLv2 = getattr(player, "PET_GROWTH_SKILL_OPEN_LEVEL_2", 105)
		tier1 = getattr(player, "PET_GROWTH_SKILL_SLOT_TIER1_COUNT", 3)
		maxLevel = getattr(player, "PET_GROWTH_SKILL_LEVEL_MAX", 20)

		rule1 = LocaleText("WIKI_PET_SK_RULE1", "%s skill slots unlock at pet level %s, all 6 at level %s.") % (tier1, slotLv1, slotLv2)
		pw = self.peekWindow.GetWidth()
		top = self._RuleTable(top, (
			("WIKI_PET_SK_RULE2_A", "Learn a skill by dragging its Pet Skill Book onto an empty"),
			("WIKI_PET_SK_RULE2_B", "slot; a deletion book removes it again."),
			("WIKI_PET_SK_RULE3_A", "Upgrading to level 20 never fails and uses the same material"),
			("WIKI_PET_SK_RULE3_B", "ladder for every skill - the cost table is below."),
			("WIKI_PET_SK_RULE4_A", "Hover a book for the full effect text; click it to open the"),
			("WIKI_PET_SK_RULE4_B", "item's own wiki page."),
		), lead=[rule1]) + 8

		# Book Shop entry point: the token opens shop 3340 (stocking exactly
		# the books below, 100M Yang + 10 tokens each) and doubles as the
		# per-rung upgrade material.
		rtl = self._RTL()
		circleX = (pw - 44 - 48) if rtl else 44
		textX = (circleX - 8) if rtl else 116
		circle = self._Img(_ART + "itemcircle1.png", circleX, top)
		circle.SetScale(0.68, 0.68)
		self._ItemIcon(_TOKEN_ITEM, circleX + 8, top + 10, cellW=32, cellH=32)
		try:
			item.SelectItem(_TOKEN_ITEM)
			tokenName = item.GetItemName()
		except Exception:
			tokenName = str(_TOKEN_ITEM)
		self._Text(tokenName, textX, top + 8, _COL_ITEM_TITLE)
		self._Text(LocaleText("WIKI_PET_SK_SHOP_DESC", "Opens the Book Shop - books cost 100,000,000 Yang + 10 tokens"), textX, top + 26, _COL_DESC)
		top += 58
		top = self._RuleLines(top, (
			("WIKI_PET_SK_SHOP_SRC_A", "Tokens drop mainly from bosses, and every skill upgrade"),
			("WIKI_PET_SK_SHOP_SRC_B", "consumes one more (see the cost table)."),
		)) + 6

		widths = (48, 140, 82, 90, 116)
		COL_BOOK, COL_SKILL, COL_LV1, COL_LVMAX, COL_T6 = 0, 1, 2, 3, 4
		seq, colX = self._TableLayout(widths, (COL_BOOK, COL_SKILL, COL_LV1, COL_LVMAX, COL_T6))
		headers = (
			LocaleText("WIKI_PET_COL_BOOK", "Book"),
			LocaleText("WIKI_PET_COL_SKILL", "Skill"),
			LocaleText("WIKI_PET_COL_LV1", "Lv 1"),
			LocaleText("WIKI_PET_COL_LVMAX_FMT", "Lv %s") % maxLevel,
			LocaleText("WIKI_PET_COL_T6", "Type 6"),
		)
		self._TableHeader(top, seq, colX, widths, headers)

		learned = self._LearnedSkills()
		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for bookVnum, skillId in _SKILL_BOOKS:
			rowH = 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			textY = rowY + rowH / 2 - 7
			iconX = colX[COL_BOOK] + (widths[COL_BOOK] - 32) / 2
			self._ItemIcon(bookVnum, iconX, rowY + (rowH - 32) / 2, cellW=32, cellH=32)
			nameColor = _COL_OK if skillId in learned else ingamewikidungeon._COL_TAN
			self._CellText(_SkillName(skillId), colX[COL_SKILL], widths[COL_SKILL], textY, nameColor)
			curve = None
			try:
				curve = app.GetPetSkillCurve(skillId)
			except Exception:
				curve = None
			if curve:
				(v1, vMax, vT6, act1, actMax, dur1, durMax) = curve
				self._CellText(_SkillValueText(skillId, v1, act1, dur1), colX[COL_LV1], widths[COL_LV1], textY, self._COL_TABLE_VALUE)
				self._CellText(_SkillValueText(skillId, vMax, actMax, durMax), colX[COL_LVMAX], widths[COL_LVMAX], textY, self._COL_TABLE_VALUE)
				t6Text = _SkillValueText(skillId, vT6, actMax, durMax) if vT6 else "-"
				self._CellText(t6Text, colX[COL_T6], widths[COL_T6], textY, _COL_OK if vT6 else self._COL_TABLE_VALUE)
			else:
				for li in (COL_LV1, COL_LVMAX, COL_T6):
					self._Text("-", colX[li] + widths[li] / 2, textY, self._COL_TABLE_VALUE, align="center")
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)

		# -- the one skill-upgrade cost table (level 2..20) --
		rowY += 14
		cTop = rowY
		self._Text(LocaleText("WIKI_PET_SK_COST_TITLE", "Skill Upgrade Costs (every skill)"), self._TBL_X0 + self._TBL_W / 2, cTop, _COL_ITEM_TITLE, align="center")
		cTop += 20

		cWidths = (56, 336, 84)
		COL_TARGET, COL_CMATS, COL_CYANG = 0, 1, 2
		cSeq, cColX = self._TableLayout(cWidths, (COL_TARGET, COL_CMATS, COL_CYANG))
		cHeaders = (
			LocaleText("WIKI_PET_COL_TARGET", "Level"),
			LocaleText("WIKI_PET_COL_MATS", "Materials"),
			LocaleText("PET_UP_HELP_YANG", "Yang"),
		)
		self._TableHeader(cTop, cSeq, cColX, cWidths, cHeaders)

		totalYang = 0
		rowY = cTop + self._TBL_HEADER_H
		rowBounds = []
		for target in xrange(2, maxLevel + 1):
			yang, mats = 0, []
			try:
				(yang, mats) = app.GetPetSkillUpgradeReq(target)
			except Exception:
				pass
			totalYang += yang
			rowH = 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			textY = rowY + rowH / 2 - 7
			self._Text(str(target), cColX[COL_TARGET] + cWidths[COL_TARGET] / 2, textY, _COL_LEVEL, align="center")
			self._MatStrip(mats, cColX[COL_CMATS], cWidths[COL_CMATS], rowY, rowH)
			self._Text(_Money(yang), cColX[COL_CYANG] + cWidths[COL_CYANG] / 2, textY, self._COL_TABLE_VALUE, align="center")
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, cTop, self._TBL_W, cSeq, cColX, cWidths, rowBounds)

		rowY += 8
		if totalYang:
			totalFmt = LocaleText("WIKI_PET_SK_TOTAL_FMT", "Total for one skill, level 1 to %s: %s Yang")
			rowY = self._RuleTableRows(rowY, [[totalFmt % (maxLevel, _Money(totalYang))]])

		return rowY + 12

	# -- Leveling & Lifetime -------------------------------------------------

	def _ItemName(self, vnum):
		try:
			item.SelectItem(vnum)
			name = item.GetItemName()
			if name:
				return name
		except Exception:
			pass
		return str(vnum)

	def _RenderJourney(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_PET_NAV_JOURNEY", "Leveling & Lifetime"))

		# The Journey: one icon-led grid, milestone consequences inline on the
		# row where they happen (never a separate matrix).
		self._Text(LocaleText("PET_HELP_EXP_JOURNEY_TITLE", "The Journey"), self._TBL_X0 + self._TBL_W / 2, top, _COL_ITEM_TITLE, align="center")
		top += 20

		widths = (48, 60, 368)
		COL_ICON, COL_LV, COL_WHAT = 0, 1, 2
		seq, colX = self._TableLayout(widths, (COL_ICON, COL_LV, COL_WHAT))
		headers = (
			"",
			LocaleText("PET_HELP_EXP_COL_LEVEL", "Pet Lv."),
			LocaleText("PET_HELP_EXP_COL_WHAT", "What happens"),
		)
		self._TableHeader(top, seq, colX, widths, headers)

		rows = (
			(_EGG_ITEM, LocaleText("WIKI_PET_J_START_LV", "Start"), LocaleText("WIKI_PET_J_START", "Hatch an egg - the pet starts Young, Type 1"), _COL_LEVEL),
			(_OVERVIEW_ITEM_PET, "1-39", LocaleText("WIKI_PET_J_HUNT", "Hunt - your kills feed the pet battle EXP"), _COL_LEVEL),
			(55003, "40", LocaleText("WIKI_PET_J_40", "STOP: evolve to Wild - allows Type 3-4"), _COL_STOP),
			(_EXPFOOD_ITEM, "55", LocaleText("WIKI_PET_J_55", "Item EXP unlocks - feed EXP food or sacrifice gear"), _COL_LEVEL),
			(55004, "80", LocaleText("WIKI_PET_J_80", "STOP: evolve to Valiant - allows Type 5"), _COL_STOP),
			(55005, "81", LocaleText("WIKI_PET_J_81", "STOP: final evolution (age 1+ day) - allows Type 6"), _COL_STOP),
			(55014, "90", LocaleText("WIKI_PET_J_90", "Skill slots 1-3 unlock"), _COL_OK),
			(55040, "105", LocaleText("WIKI_PET_J_105", "Maximum level - skill slots 4-6 unlock"), _COL_OK),
		)
		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for iconVnum, lvText, what, lvColor in rows:
			rowH = 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			textY = rowY + rowH / 2 - 7
			if iconVnum:
				iconX = colX[COL_ICON] + (widths[COL_ICON] - 32) / 2
				self._ItemIcon(iconVnum, iconX, rowY + (rowH - 32) / 2, cellW=32, cellH=32)
			self._Text(lvText, colX[COL_LV] + widths[COL_LV] / 2, textY, lvColor, align="center")
			self._CellText(what, colX[COL_WHAT], widths[COL_WHAT], textY, self._COL_TABLE_VALUE, align="left")
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)

		rowY += 10
		rowY = self._RuleLines(rowY, (
			("WIKI_PET_X_RULE1_A", "The pet never levels above your character; from level 81 the"),
			("WIKI_PET_X_RULE1_B", "EXP need rises another +25% per level."),
			("WIKI_PET_X_RULE2_A", "Item EXP is optional (at most 10% of a level) - it only makes"),
			("WIKI_PET_X_RULE2_B", "leveling faster, hunting alone always works."),
		)) + 10

		# EXP boosters: timed AFFECT_PET_EXP items, duration read live from
		# the client proto (Value0 seconds).
		self._Text(LocaleText("WIKI_PET_BOOST_TITLE", "EXP Boosters"), self._TBL_X0 + self._TBL_W / 2, rowY, _COL_ITEM_TITLE, align="center")
		rowY += 20
		boostFmt = LocaleText("WIKI_PET_BOOST_FMT", "Doubles battle EXP for %s")
		rowY = self._ItemEffectTable(rowY, tuple(
			(vnum, boostFmt % self._BoostDuration(vnum, fallback))
			for vnum, fallback in _EXP_BOOST_ITEMS))
		rowY += 8
		rowY = self._RuleLines(rowY, (
			("WIKI_PET_BOOST_NOTE", "Only one booster can be active at a time."),
		)) + 10

		# Lifetime: item-led rows, then the hard rules.
		self._Text(LocaleText("WIKI_PET_L_TITLE", "Lifetime"), self._TBL_X0 + self._TBL_W / 2, rowY, _COL_ITEM_TITLE, align="center")
		rowY += 20
		rowY = self._ItemEffectTable(rowY, (
			(_FEEDSTUFF_ITEM, LocaleText("WIKI_PET_L_FEED_DESC", "+3 days lifetime (30-day cap); revives an expired pet")),
			(_PET_BAG_ITEM, LocaleText("WIKI_PET_L_BAG_DESC", "Packs the pet inside - store or trade it")),
		))

		rowY += 10
		rowY = self._RuleLines(rowY, (
			("WIKI_PET_L_RULE1_A", "A fresh pet starts with 3 days of lifetime; the clock also"),
			("WIKI_PET_L_RULE1_B", "runs while you are offline."),
			("WIKI_PET_L_RULE2_A", "A dead (expired) pet is not lost - feedstuff revives it, but"),
			("WIKI_PET_L_RULE2_B", "until then potions, Type and skill upgrades are blocked."),
		))

		return rowY + 12
