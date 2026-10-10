# coding: latin_1
#
# Buffi wiki page: two-column section nav + banner header, then the six
# system sections (overview / buffs & skills / evolution & leveling /
# intelligence & ore / name & premium / duration & recharge). Everything
# is bridges-only: evolution numbers come from app.GetBuffiEvolveInfo
# (srcs/share/buffi.hpp -- the same rows the server consumes), item facts
# (ore INT, recharge days) are read live from the client proto, and the
# live strips read the constinfo cache that every buffi status push
# refreshes -- no JSON, nothing to drift.
#
# Owner direction 2026-08-19: tables over text. Sections carry their data
# tables and live strips; explanatory copy is kept to the bare minimum a
# player needs to read the tables.
#
# Subclasses WikiGrowthPetWindow for its generic machinery only (marquee
# _CellText, _TableLayout/_TableHeader/_TableGrid, _ItemEffectTable,
# _SectionTitle, nav rows, sig-gated OnUpdate) -- every pet-specific
# method is overridden here.

import app
import ui
import item
import skill
import player
import constinfo
import localeinfo
import ingamewikidungeon
import ingamewikigrowthpet

LocaleText = ingamewikidungeon.LocaleText
_NavRow = ingamewikigrowthpet._NavRow

_ART = "d:/ymir work/ui/wiki/wiki_new/dungeons/"

_COL_NAME = 0xffffffff
_COL_ITEM_TITLE = 0xffcabdab
_COL_DESC = 0xffa09080
_COL_LEVEL = 0xffffe6a0
_COL_OK = 0xff8ab98e
_COL_STOP = 0xffc98a8a
_COL_NAV = 0xffcabdab
_COL_NAV_HOVER = 0xffffe6a0

_ORE_ITEM = 91121
_NAME_ITEM = 91120
_BOOK_MASTER = 50351
_BOOK_GRAND = 91125
_RECHARGE_ITEMS = (91126, 91122, 91123)   # duration days = proto value0
_PERMANENT_ITEM = 91124

_SKILL_VNUMS = (163, 164, 165, 166)
_SKILL_SLOT_START = 130
_PREMIUM_SKILLS = (165, 166)
_ORE_SLOTS = 3
_ORE_INT_EACH = 3

# Mirrors of the buffi.hpp evolution tables, used only when the
# __BUFFI_EVOLUTION__ bridge is unavailable; the live bridge wins.
_FB_STAGE_INT = (80, 100, 140, 180)
_FB_REQ_LEVEL = (0, 40, 80, 105)
_FB_CHANCE = (0, 80, 60, 35)
_FB_PITY = 3


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


def _ItemValue(vnum, idx):
	try:
		item.SelectItem(vnum)
		return int(item.GetValue(idx))
	except Exception:
		return 0


def _SummonItem():
	try:
		vnums = constinfo.BUFFI_SUMMON_VNUMS
		if vnums:
			return vnums[0]
	except Exception:
		pass
	return 91110


def _EvolInfo(stage):
	# (int, reqLevel, yang, chance, pity, [(vnum, count), ...])
	try:
		if hasattr(app, "GetBuffiEvolveInfo"):
			return app.GetBuffiEvolveInfo(stage)
	except Exception:
		pass
	return None


def _SkillName(vnum):
	try:
		name = skill.GetSkillName(vnum)
		if name:
			return name
	except Exception:
		pass
	return str(vnum)


def _GradeText(vnum):
	try:
		grade = player.GetSkillGradeNew(vnum)
		level = player.GetSkillLevelNew(vnum)
	except Exception:
		return "-"
	if 1 == grade:
		return "M%d" % level
	if 2 == grade:
		return "G%d" % level
	if 3 == grade:
		return "P"
	return str(level) if level else "-"


def _SharedSkillTip():
	try:
		import systemSetting
		return getattr(systemSetting.GetInterfaceHandler(), "tooltipSkill", None)
	except Exception:
		return None


class WikiBuffiWindow(ingamewikigrowthpet.WikiGrowthPetWindow):

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
		self._sectionAnchors["skills"] = y
		y = self._RenderSkills(y)
		self._sectionAnchors["evolution"] = y
		y = self._RenderEvolution(y)
		self._sectionAnchors["intellect"] = y
		y = self._RenderIntellect(y)
		self._sectionAnchors["name"] = y
		y = self._RenderName(y)
		self._sectionAnchors["duration"] = y
		y = self._RenderDuration(y)

		deco = self._Img(_ART + "page_end_deco.png", 0, y)
		self._FitWide(deco)
		y += 19 + 8

		self.scrollBoard.SetSize(self.peekWindow.GetWidth(), max(y, self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, 0)
		self.ChangeScrollbar()
		self.Show()

	# -- live-state signature gate ------------------------------------------

	def _LiveSig(self):
		parts = [
			int(getattr(constinfo, "BUFFI_SUMMONED", 0)),
			int(getattr(constinfo, "BUFFI_TT_LEVEL", 0)),
			int(getattr(constinfo, "BUFFI_TT_INT", 0)),
			str(getattr(constinfo, "BUFFI_TT_NAME", "")),
			tuple(getattr(constinfo, "BUFFI_TT_ORES", (0, 0, 0))),
			int(getattr(constinfo, "BUFFI_TT_EXPIRE", 0)),
		]
		try:
			sk = []
			for v in _SKILL_VNUMS:
				sk.append((player.GetSkillGradeNew(v), player.GetSkillLevelNew(v)))
			parts.append(tuple(sk))
		except Exception:
			pass
		return tuple(parts)

	def _HasBuffi(self):
		return int(getattr(constinfo, "BUFFI_TT_LEVEL", 0)) > 0

	def _LiveStage(self):
		if not self._HasBuffi():
			return -1
		intVal = int(getattr(constinfo, "BUFFI_TT_INT", 0))
		if intVal <= 0:
			return -1
		oreInt = 0
		for v in getattr(constinfo, "BUFFI_TT_ORES", (0, 0, 0)):
			if v:
				oreInt += min(_ItemValue(v, 0), _ORE_INT_EACH)
		base = intVal - oreInt
		for s in xrange(4):
			info = _EvolInfo(s)
			stageInt = info[0] if info else _FB_STAGE_INT[s]
			if int(stageInt) == base:
				return s
		return -1

	# -- header --------------------------------------------------------------

	def _RenderHeader(self, y):
		rtl = self._RTL()
		pw = self.peekWindow.GetWidth()
		leftX = 8
		rightX = pw - 200 - 8

		navCols = (
			(
				("overview", LocaleText("WIKI_BUFFI_NAV_OVERVIEW", "Overview")),
				("skills", LocaleText("WIKI_BUFFI_NAV_SKILLS", "Buffs & Skills")),
				("evolution", LocaleText("WIKI_BUFFI_NAV_EVOLUTION", "Evolution & Leveling")),
			),
			(
				("intellect", LocaleText("WIKI_BUFFI_NAV_INT", "Intelligence & Ore")),
				("name", LocaleText("WIKI_BUFFI_NAV_NAME", "Name & Premium")),
				("duration", LocaleText("WIKI_BUFFI_NAV_DURATION", "Duration & Recharge")),
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
		banner = self._Img(_ART + "banners/31.png", 0, y)
		banner.SetScale(scale, scale)
		bw = int(204 * scale)
		bh = int(133 * scale)
		banner.SetPosition((pw - bw) / 2, y + 2 + (127 - bh) / 2)

		deco = self._Img(_ART + "page_title_deco.png", 0, y + 133)
		self._FitWide(deco)
		return y + 133 + 20 + 8

	# -- shared bits ---------------------------------------------------------

	def _SkillIcon(self, vnum, x, y):
		path = ""
		try:
			path = skill.GetIconImage(vnum)
		except Exception:
			path = ""
		if not path:
			return None
		ico = ui.ExpandedImageBox()
		ico.SetParent(self.scrollBoard)
		ico.AddFlag("attach")
		try:
			ico.LoadImage(path)
		except Exception:
			return None
		iw = ico.GetWidth() or 32
		ih = ico.GetHeight() or 32
		scale = min(32.0 / iw, 32.0 / ih, 1.0)
		if scale < 1.0:
			ico.SetScale(scale, scale)
			iw = int(iw * scale)
			ih = int(ih * scale)
		ico.SetPosition(int(x) + (32 - iw) / 2, int(y) + (32 - ih) / 2)
		if app.USE_CLIP_MASK:
			try:
				ico.SetSubClippingMaskWindow(self.peekWindow)
			except Exception:
				pass
		ico.SAFE_SetStringEvent("MOUSE_OVER_IN", self._OnSkillOver, vnum)
		ico.SAFE_SetStringEvent("MOUSE_OVER_OUT", self._OnSkillOut)
		ico.Show()
		self.elements.append(ico)
		return ico

	def _OnSkillOver(self, vnum):
		tip = _SharedSkillTip()
		if not tip:
			return
		try:
			slot = _SKILL_SLOT_START + (vnum - _SKILL_VNUMS[0])
			tip.SetSkillNew(slot, vnum, player.GetSkillGradeNew(vnum), player.GetSkillLevelNew(vnum))
		except Exception:
			pass

	def _OnSkillOut(self):
		tip = _SharedSkillTip()
		if tip:
			try:
				tip.HideToolTip()
			except Exception:
				pass

	def _MixedEffectTable(self, top, rows):
		# _ItemEffectTable shape, but a row's icon may be an item OR a skill:
		# rows = ((kind, id, effectText), ...) with kind "item" / "skill".
		widths = (48, 150, 278)
		COL_ICON, COL_NAME, COL_EFFECT = 0, 1, 2
		seq, colX = self._TableLayout(widths, (COL_ICON, COL_NAME, COL_EFFECT))
		headers = (
			"",
			LocaleText("PET_UP_HELP_COL_ITEM", "Item"),
			LocaleText("WIKI_PET_COL_EFFECT", "Effect"),
		)
		self._TableHeader(top, seq, colX, widths, headers)
		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for kind, vnum, effect in rows:
			rowH = 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			textY = rowY + rowH / 2 - 7
			iconX = colX[COL_ICON] + (widths[COL_ICON] - 32) / 2
			iconY = rowY + (rowH - 32) / 2
			if "skill" == kind:
				self._SkillIcon(vnum, iconX, iconY)
				name = _SkillName(vnum)
			else:
				self._ItemIcon(vnum, iconX, iconY, cellW=32, cellH=32)
				name = self._ItemName(vnum)
			self._CellText(name, colX[COL_NAME], widths[COL_NAME], textY, ingamewikidungeon._COL_TAN)
			self._CellText(effect, colX[COL_EFFECT], widths[COL_EFFECT], textY, self._COL_TABLE_VALUE)
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)
		return rowY

	# -- Overview ------------------------------------------------------------

	def _RenderOverview(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_BUFFI_NAV_OVERVIEW", "Overview"))
		rtl = self._RTL()
		pw = self.peekWindow.GetWidth()
		circleX = (pw - 44 - 48) if rtl else 44
		textX = (circleX - 8) if rtl else 116

		rows = (
			((_SummonItem(),), LocaleText("WIKI_BUFFI_OV_SUMMON", "Summons the Buffi - it follows you and keeps you buffed")),
			((_ORE_ITEM,), LocaleText("WIKI_BUFFI_OV_ORE", "Socket into the Buffi for extra Intelligence")),
			((_NAME_ITEM,), LocaleText("WIKI_BUFFI_OV_NAME", "Names the Buffi and unlocks the two premium buffs")),
			((_BOOK_MASTER, _BOOK_GRAND), LocaleText("WIKI_BUFFI_OV_BOOKS", "Skill books - raise the four buffs up to Perfect")),
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

		if self._HasBuffi():
			name = str(getattr(constinfo, "BUFFI_TT_NAME", "")) or LocaleText("COMPANION_DEFAULT_NAME", "Buffi")
			line = LocaleText("WIKI_BUFFI_LIVE_FMT", "Your Buffi: %s - Lv. %s - %s INT") % (
				name,
				int(getattr(constinfo, "BUFFI_TT_LEVEL", 0)),
				int(getattr(constinfo, "BUFFI_TT_INT", 0)))
			rowY += 6
			self._Bar(self._TBL_X0, rowY, self._TBL_W, 26, self._COL_TABLE_HEADER_BG)
			self._CellText(line, self._TBL_X0, self._TBL_W, rowY + 6, _COL_LEVEL)
			rowY += 26

		return rowY + 12

	# -- Buffs & Skills --------------------------------------------------------

	def _RenderSkills(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_BUFFI_NAV_SKILLS", "Buffs & Skills"))

		widths = (44, 120, 136, 96, 80)
		COL_ICON, COL_BUFF, COL_EFFECT, COL_UNLOCK, COL_YOURS = 0, 1, 2, 3, 4
		seq, colX = self._TableLayout(widths, (COL_ICON, COL_BUFF, COL_EFFECT, COL_UNLOCK, COL_YOURS))
		headers = (
			"",
			LocaleText("WIKI_BUFFI_COL_BUFF", "Buff"),
			LocaleText("WIKI_PET_COL_EFFECT", "Effect"),
			LocaleText("WIKI_BUFFI_COL_UNLOCK", "Unlock"),
			LocaleText("WIKI_BUFFI_COL_YOURS", "Yours"),
		)
		self._TableHeader(top, seq, colX, widths, headers)

		effects = (
			LocaleText("WIKI_BUFFI_SK_EFFECT0", "Melee resistance"),
			LocaleText("WIKI_BUFFI_SK_EFFECT1", "Critical hit chance"),
			LocaleText("WIKI_BUFFI_SK_EFFECT2", "Movement speed"),
			LocaleText("WIKI_BUFFI_SK_EFFECT3", "Attack value"),
		)
		freeText = LocaleText("WIKI_BUFFI_SK_FREE", "Free")
		namedText = LocaleText("WIKI_BUFFI_SK_NAMED", "Buffi name")

		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for i in xrange(len(_SKILL_VNUMS)):
			vnum = _SKILL_VNUMS[i]
			rowH = 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			textY = rowY + rowH / 2 - 7
			iconX = colX[COL_ICON] + (widths[COL_ICON] - 32) / 2
			self._SkillIcon(vnum, iconX, rowY + (rowH - 32) / 2)
			self._CellText(_SkillName(vnum), colX[COL_BUFF], widths[COL_BUFF], textY, ingamewikidungeon._COL_TAN)
			self._CellText(effects[i], colX[COL_EFFECT], widths[COL_EFFECT], textY, self._COL_TABLE_VALUE)
			premium = vnum in _PREMIUM_SKILLS
			self._CellText(namedText if premium else freeText,
				colX[COL_UNLOCK], widths[COL_UNLOCK], textY,
				_COL_LEVEL if premium else _COL_OK)
			grade = _GradeText(vnum)
			gradeColor = _COL_OK if grade.startswith("P") else (self._COL_TABLE_VALUE if "-" == grade else _COL_LEVEL)
			self._Text(grade, colX[COL_YOURS] + widths[COL_YOURS] / 2, textY, gradeColor, align="center")
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)

		rowY += 14
		self._Text(LocaleText("WIKI_BUFFI_SK_BOOKS_TITLE", "Skill Books"), self._TBL_X0 + self._TBL_W / 2, rowY, _COL_ITEM_TITLE, align="center")
		rowY += 20
		rowY = self._ItemEffectTable(rowY, (
			(_BOOK_MASTER, LocaleText("WIKI_BUFFI_SK_BOOK_M", "Read to level Master-grade buffs up to Grand Master")),
			(_BOOK_GRAND, LocaleText("WIKI_BUFFI_SK_BOOK_G", "Read to level Grand Master buffs up to Perfect")),
		))

		return rowY + 12

	# -- Evolution & Leveling --------------------------------------------------

	def _RenderEvolution(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_BUFFI_NAV_EVOLUTION", "Evolution & Leveling"))

		info3 = _EvolInfo(3)
		capLevel = info3[1] if info3 else _FB_REQ_LEVEL[3]
		pity = info3[4] if info3 and len(info3) >= 5 else _FB_PITY
		leadCap = LocaleText("WIKI_BUFFI_EVO_LEAD_CAP", "The Buffi levels up to %s by hunting at your side.") % capLevel
		leadPity = LocaleText("WIKI_BUFFI_EVO_LEAD_PITY", "After %s failed attempts the next one is guaranteed.") % pity
		top = self._RuleTable(top, (
			("WIKI_BUFFI_EVO_RULE1_A", "Each attempt consumes the materials and the Yang -"),
			("WIKI_BUFFI_EVO_RULE1_B", "whether it succeeds or fails."),
		), lead=[leadCap, leadPity]) + 6

		stageKeys = ("WIKI_BUFFI_STAGE0", "WIKI_BUFFI_STAGE1", "WIKI_BUFFI_STAGE2", "WIKI_BUFFI_STAGE3")
		stageDefs = ("Default", "Evolution 1", "Evolution 2", "Evolution 3")
		liveStage = self._LiveStage()

		# Simple INT ladder first: Stage -> INT, nothing else.
		self._Text(LocaleText("WIKI_BUFFI_EVO_INT_TITLE", "Intelligence per Stage"), self._TBL_X0 + self._TBL_W / 2, top, _COL_ITEM_TITLE, align="center")
		top += 20
		iWidths = (238, 238)
		I_STAGE, I_INT = 0, 1
		iSeq, iColX = self._TableLayout(iWidths, (I_STAGE, I_INT))
		iHeaders = (
			LocaleText("WIKI_BUFFI_COL_STAGE", "Stage"),
			LocaleText("WIKI_BUFFI_COL_INT", "INT"),
		)
		self._TableHeader(top, iSeq, iColX, iWidths, iHeaders)
		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for s in xrange(4):
			info = _EvolInfo(s)
			stageInt = info[0] if info else _FB_STAGE_INT[s]
			rowH = 26
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			if s == liveStage:
				self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, 0x1effe6a0)
			textY = rowY + rowH / 2 - 7
			stageColor = _COL_LEVEL if s == liveStage else ingamewikidungeon._COL_TAN
			self._CellText(LocaleText(stageKeys[s], stageDefs[s]), iColX[I_STAGE], iWidths[I_STAGE], textY, stageColor)
			self._Text(str(stageInt), iColX[I_INT] + iWidths[I_INT] / 2, textY, _COL_OK, align="center")
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, iSeq, iColX, iWidths, rowBounds)

		# Full requirements table: level gate, success roll, materials, Yang.
		top = rowY + 14
		self._Text(LocaleText("WIKI_BUFFI_EVO_REQ_TITLE", "Evolution Requirements"), self._TBL_X0 + self._TBL_W / 2, top, _COL_ITEM_TITLE, align="center")
		top += 20
		widths = (80, 50, 44, 54, 178, 70)
		COL_STAGE, COL_LV, COL_INT, COL_CHANCE, COL_MATS, COL_YANG = 0, 1, 2, 3, 4, 5
		seq, colX = self._TableLayout(widths, (COL_STAGE, COL_LV, COL_INT, COL_CHANCE, COL_MATS, COL_YANG))
		headers = (
			LocaleText("WIKI_BUFFI_COL_STAGE", "Stage"),
			LocaleText("WIKI_BUFFI_COL_LV", "Buffi Lv."),
			LocaleText("WIKI_BUFFI_COL_INT", "INT"),
			LocaleText("WIKI_BUFFI_COL_CHANCE", "Success"),
			LocaleText("WIKI_PET_COL_MATS", "Materials"),
			LocaleText("PET_UP_HELP_YANG", "Yang"),
		)
		self._TableHeader(top, seq, colX, widths, headers)

		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for s in xrange(4):
			info = _EvolInfo(s)
			stageInt = info[0] if info else _FB_STAGE_INT[s]
			reqLevel = info[1] if info else _FB_REQ_LEVEL[s]
			yang = info[2] if info else 0
			chance = info[3] if info and len(info) >= 4 else _FB_CHANCE[s]
			mats = info[5] if info and len(info) >= 6 else []
			rowH = 26 if 0 == s else 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			if s == liveStage:
				self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, 0x1effe6a0)
			textY = rowY + rowH / 2 - 7
			stageColor = _COL_LEVEL if s == liveStage else ingamewikidungeon._COL_TAN
			self._CellText(LocaleText(stageKeys[s], stageDefs[s]), colX[COL_STAGE], widths[COL_STAGE], textY, stageColor)
			self._Text(str(reqLevel) if s else "-", colX[COL_LV] + widths[COL_LV] / 2, textY, _COL_LEVEL if s else self._COL_TABLE_VALUE, align="center")
			self._Text(str(stageInt), colX[COL_INT] + widths[COL_INT] / 2, textY, self._COL_TABLE_VALUE, align="center")
			self._Text(("%d%%" % chance) if s else "-", colX[COL_CHANCE] + widths[COL_CHANCE] / 2, textY, self._COL_TABLE_VALUE, align="center")
			if 0 == s:
				self._CellText(LocaleText("WIKI_BUFFI_STAGE_START", "(start)"), colX[COL_MATS], widths[COL_MATS], textY, self._COL_TABLE_VALUE)
				self._Text("-", colX[COL_YANG] + widths[COL_YANG] / 2, textY, self._COL_TABLE_VALUE, align="center")
			else:
				self._MatStrip(mats, colX[COL_MATS], widths[COL_MATS], rowY, rowH)
				self._CellText(_Money(yang) if yang else "-", colX[COL_YANG], widths[COL_YANG], textY, self._COL_TABLE_VALUE)
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)

		return rowY + 12

	# -- Intelligence & Ore ----------------------------------------------------

	def _RenderIntellect(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_BUFFI_NAV_INT", "Intelligence & Ore"))

		oreEach = min(_ItemValue(_ORE_ITEM, 0), _ORE_INT_EACH) or _ORE_INT_EACH
		oreMax = oreEach * _ORE_SLOTS
		info3 = _EvolInfo(3)
		maxInt = (info3[0] if info3 else _FB_STAGE_INT[3]) + oreMax
		leadMax = LocaleText("WIKI_BUFFI_INT_MAX_FMT", "Fully evolved and fully socketed: up to %s INT.") % maxInt
		top = self._RuleTable(top, (
			("WIKI_BUFFI_INT_RULE1_A", "Higher Intelligence = stronger buffs. Evolution sets the"),
			("WIKI_BUFFI_INT_RULE1_B", "base INT, socketed ore adds on top."),
		), lead=[leadMax]) + 6

		oreFmt = LocaleText("WIKI_BUFFI_ORE_GIVE_FMT", "+%s INT each - up to +%s with all 3 sockets")
		rowY = self._ItemEffectTable(top, (
			(_ORE_ITEM, oreFmt % (oreEach, oreMax)),
		))

		rowY += 8
		rowY = self._RuleTable(rowY, (
			("WIKI_BUFFI_ORE_RULE1_A", "Ores are consumed when socketed and disappear after a"),
			("WIKI_BUFFI_ORE_RULE1_B", "limited real time - they cannot be taken out."),
		))

		return rowY + 12

	# -- Name & Premium ---------------------------------------------------------

	def _RenderName(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_BUFFI_NAV_NAME", "Name & Premium"))

		rowY = self._MixedEffectTable(top, (
			("item", _NAME_ITEM, LocaleText("WIKI_BUFFI_NAME_GIVE", "Custom name + bonus damage against bosses (7 days)")),
			("skill", _PREMIUM_SKILLS[0], LocaleText("WIKI_BUFFI_NAME_UNLOCK_SPEED", "Unlocked while named: the movement speed buff")),
			("skill", _PREMIUM_SKILLS[1], LocaleText("WIKI_BUFFI_NAME_UNLOCK_ATT", "Unlocked while named: the attack value buff")),
		))

		liveName = str(getattr(constinfo, "BUFFI_TT_NAME", ""))
		if liveName:
			line = LocaleText("WIKI_BUFFI_NAME_LIVE_FMT", "Nickname active: %s") % liveName
			rowY += 6
			self._Bar(self._TBL_X0, rowY, self._TBL_W, 26, self._COL_TABLE_HEADER_BG)
			self._CellText(line, self._TBL_X0, self._TBL_W, rowY + 6, _COL_LEVEL)
			rowY += 26

		return rowY + 12

	# -- Duration & Recharge -----------------------------------------------------

	def _FormatRemain(self, sec):
		sec = int(sec)
		if sec >= 86400:
			return LocaleText("COMPANION_DURATION_LEFT_FMT", "%dd %dh") % (sec / 86400, (sec % 86400) / 3600)
		return LocaleText("COMPANION_DURATION_LEFT_MS_FMT", "%dm %ds") % (sec / 60, sec % 60)

	def _RenderDuration(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_BUFFI_NAV_DURATION", "Duration & Recharge"))

		addFmt = LocaleText("WIKI_BUFFI_DUR_ADD_FMT", "+%s days of duration")
		addGen = LocaleText("WIKI_BUFFI_DUR_ADD_GEN", "Adds extra duration")
		rows = []
		for vnum in _RECHARGE_ITEMS:
			days = _ItemValue(vnum, 0)
			rows.append((vnum, (addFmt % days) if days > 0 else addGen))
		rows.append((_PERMANENT_ITEM, LocaleText("WIKI_BUFFI_DUR_PERMA", "Permanent - the Buffi never expires again")))
		rowY = self._ItemEffectTable(top, tuple(rows))

		expire = int(getattr(constinfo, "BUFFI_TT_EXPIRE", 0))
		if expire:
			if 0xFFFFFFFF == expire:
				state = LocaleText("COMPANION_DURATION_PERMANENT", "Permanent")
			else:
				try:
					now = app.GetGlobalTimeStamp()
				except Exception:
					now = 0
				remain = expire - now
				if now and remain > 0:
					state = self._FormatRemain(remain)
				else:
					state = LocaleText("COMPANION_DURATION_EXPIRED", "Expired")
			line = LocaleText("WIKI_BUFFI_DUR_LIVE_FMT", "Your Buffi's duration: %s") % state
			rowY += 6
			self._Bar(self._TBL_X0, rowY, self._TBL_W, 26, self._COL_TABLE_HEADER_BG)
			self._CellText(line, self._TBL_X0, self._TBL_W, rowY + 6, _COL_LEVEL)
			rowY += 26

		return rowY + 12
