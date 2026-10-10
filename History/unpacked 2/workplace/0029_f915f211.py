# coding: latin_1
#
# Biologist wiki page: section nav (clickable, scrolls to the section),
# NPC banner, item overview rows and the missions table. Static copy lives in
# locale keys; mission rows come from uibiologmanager.BIOLOG_MISSION_GROUPS
# (single source with the biolog window) merged with the baked
# biolog_wiki.json (cooldown/chance -- generated from the live player-DB dump
# by tools/"wiki server to client"/gen_biolog_wiki.py, never hand-edited).

import app
import dbg
import ui
import item
import localeinfo
import ingamewikidungeon

LocaleText = ingamewikidungeon.LocaleText

_ART = "d:/ymir work/ui/wiki/wiki_new/dungeons/"
_JSON_NAME = "biolog_wiki.json"

_COL_NAME = 0xffffffff
_COL_ITEM_TITLE = 0xffcabdab
_COL_DESC = 0xffa09080
_COL_RULE = 0xffc7c7c7
_COL_LEVEL = 0xffffe6a0
_COL_REWARD = 0xffb0dfb4
_COL_NAV = 0xffcabdab
_COL_NAV_HOVER = 0xffffe6a0

# Support items ship in two variants (default / zodiac, per
# BiologSystemManager.cpp); the overview rows alternate between them.
_CHANCE_ITEMS = (59919, 59920)
_TIME_ITEMS = (59917, 59918)
_FALLBACK_MISSION_ITEM = 30006

_missionMeta = None
_infoRequested = False


def _LoadMissionMeta():
	global _missionMeta
	if _missionMeta is not None:
		return _missionMeta
	_missionMeta = {}
	txt = ingamewikidungeon._ReadJsonText(_JSON_NAME)
	if not txt:
		return _missionMeta
	try:
		data = eval(txt, dict(ingamewikidungeon._JSON_GLOBALS))
		_missionMeta = data.get("missions", {}) or {}
	except Exception:
		try:
			dbg.TraceError("[wikibiolog] failed to parse %s" % _JSON_NAME)
		except:
			pass
		_missionMeta = {}
	return _missionMeta


def Reload():
	global _missionMeta
	_missionMeta = None
	return _LoadMissionMeta()


class _NavRow(ui.Window):
	# Click/hover catcher over one brush stripe of title_list_3.png. A plain
	# pickable Window: the engine dispatches the On* handlers directly, which
	# sidesteps the image-box MOUSE_LEFT_DOWN string-event trap.
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
		# Down, not Up: an unhandled Down propagates to an ancestor which
		# then captures the matching Up, so plain windows never see Up
		# (search-list headers and the redesign scrollbar act on Down too).
		ev = getattr(self, "navEvent", None)
		if ev:
			ev(self.navKey)
		return True


class WikiBiologWindow(ingamewikidungeon.WikiDungeonWindow):
	# Inherits the dungeon page's scroll plumbing, widget factories, _ItemIcon
	# (hover tooltip + click-through) and history OpenWindow support.

	_NAV_X = 26
	_NAV_ROW_CENTERS = (21, 57, 93)   # stripe centers measured in title_list_3.png
	_TBL_X0 = 40
	_TBL_W = 476
	_TBL_HEADER_H = 24
	_TBL_COLS = (48, 52, 56, 68, 48)  # level / item / quantity / cooldown / status; reward gets the rest

	def OpenPage(self):
		self._ClearContent()
		self._sectionAnchors = {}
		self._swapRows = []
		self._swapPhase = -1
		self._infoItemAtRender = self._RequestBiologInfo()

		y = 4
		y = self._RenderHeader(y)
		self._sectionAnchors["overview"] = y
		y = self._RenderOverviewSection(y)
		self._sectionAnchors["missions"] = y
		y = self._RenderMissionSection(y)

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
		# Arabic TextLine glyphs anchor at the given x and flow LEFT, so the
		# RTL layout mirrors block positions; alignment modes stay unchanged.
		try:
			return localeinfo.IsARABIC()
		except:
			return 0

	# -- section nav --------------------------------------------------------

	def _RenderHeader(self, y):
		rtl = self._RTL()
		pw = self.peekWindow.GetWidth()
		navX = (pw - 200 - self._NAV_X) if rtl else self._NAV_X
		labelX = (navX + 152) if rtl else (navX + 48)

		self._Img(_ART + "title_list_3.png", navX, y + 2)
		navs = (
			("overview", LocaleText("WIKI_BIOLOG_OVERVIEW", "Overview")),
			("missions", LocaleText("WIKI_BIOLOG_MISSIONS", "Missions")),
		)
		for i in xrange(len(navs)):
			key, label = navs[i]
			rowCy = y + 2 + self._NAV_ROW_CENTERS[i]
			t = self._Text(label, labelX, rowCy - 8, _COL_NAV)
			row = _NavRow()
			row.SetParent(self.scrollBoard)
			# No "attach": FLAG_ATTACH redirects button events to GetRoot()
			# (PythonWindowManager::RunMouseLeftButtonDown), so an attached
			# row never receives clicks -- hover is unaffected, which is why
			# the highlight worked while clicks died.
			row.SetSize(200, 30)
			row.SetPosition(navX, rowCy - 15)
			row.SetNav(t, ui.__mem_func__(self._OnNavClick), key)
			row.Show()
			self.elements.append(row)

		self._Img(_ART + "banners/18.png", (pw - 204 - 318) if rtl else 318, y)

		deco = self._Img(_ART + "page_title_deco.png", 0, y + 139)
		self._FitWide(deco)
		return y + 139 + 20 + 8

	def _RequestBiologInfo(self):
		# The server pushes mission info only on a biolog-window open or a
		# delivery. If it never arrived this session, ask for it once, with
		# the game.py-side flag suppressing the biolog-window toggle the
		# reply normally triggers. Returns the item the page rendered with
		# so OnUpdate can rebuild when the reply lands.
		global _infoRequested
		try:
			import biologmgr
			item0 = biologmgr.GetInfoItem()[0]
		except Exception:
			return 0
		if not item0 and not _infoRequested:
			_infoRequested = True
			try:
				import net
				import constinfo
				constinfo.WIKI_BIOLOG_SILENT_INFO = 1
				biologmgr.SendPacket(net.BIOLOG_MANAGER_OPEN)
			except Exception:
				pass
		return item0

	def OnUpdate(self):
		if not self.IsShow():
			return
		# Rebuild once the silently requested mission info arrives, keeping
		# the scroll position.
		try:
			import biologmgr
			infoItem = biologmgr.GetInfoItem()[0]
		except Exception:
			infoItem = 0
		if infoItem != getattr(self, "_infoItemAtRender", infoItem):
			pos = self.scrollBoard.GetLocalPosition()[1]
			self.OpenPage()
			span = self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()
			if span > 0 and pos < 0:
				self.scrollBoard.SetPosition(0, max(pos, -span))
				self.ChangeScrollbar()
			return

		# Helper rows alternate between their item variants once a second;
		# name (and thereby hover/click target) swaps with the icon.
		rows = getattr(self, "_swapRows", None)
		if not rows:
			return
		phase = int(app.GetTime()) % 2
		if phase == getattr(self, "_swapPhase", -1):
			return
		self._swapPhase = phase
		for nameLine, entries in rows:
			idx = phase % len(entries)
			for i in xrange(len(entries)):
				if i == idx:
					entries[i][0].Show()
				else:
					entries[i][0].Hide()
			nameLine.SetText(entries[idx][1])

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

	# -- shared section bits ------------------------------------------------

	def _SectionTitle(self, y, label):
		self._Img(_ART + "subtitle.png", (556 - 495) / 2, y)
		self._Text(label, 447 if self._RTL() else 108, y + 11, _COL_NAME)
		return y + 48

	def _CurrentMissionId(self):
		# item 0 = info never pushed this session (the server only sends it on
		# a biolog-window open or a delivery) -> treat as nothing done, never
		# as all-done. A known item not in the map = genuinely past the table.
		try:
			import uibiologmanager
			import biologmgr
			item0 = biologmgr.GetInfoItem()[0]
			if not item0:
				return 0
			return uibiologmanager.BIOLOG_ITEM_TO_MISSION.get(item0, 99)
		except Exception:
			return 0

	# -- Overview -----------------------------------------------------------

	def _RenderOverviewSection(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_BIOLOG_OVERVIEW", "Overview"))

		missionItem = _FALLBACK_MISSION_ITEM
		try:
			import biologmgr
			v = biologmgr.GetInfoItem()[0]
			if v:
				missionItem = v
		except Exception:
			pass

		rows = (
			((missionItem,), LocaleText("WIKI_BIOLOG_ITEMS_DESC", "Deliver these items for permanent bonuses")),
			(_CHANCE_ITEMS, LocaleText("WIKI_BIOLOG_CHANCE_DESC", "Increases your success chance by 50% when delivering")),
			(_TIME_ITEMS, LocaleText("WIKI_BIOLOG_TIME_DESC", "Lets you deliver again without waiting for the cooldown")),
		)
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
				try:
					item.SelectItem(vnum)
					name = item.GetItemName()
				except Exception:
					name = str(vnum)
				entries.append((icon, name))
			nameLine = self._Text(entries[0][1], textX, rowY + 8, _COL_ITEM_TITLE)
			self._Text(desc, textX, rowY + 26, _COL_DESC)
			if len(entries) > 1:
				for e in entries[1:]:
					e[0].Hide()
				self._swapRows.append((nameLine, entries))
			rowY += 58

		rowY += 6
		rules = (
			("WIKI_BIOLOG_RULE1_A", "Deliver the required item. Each successful delivery increases the"),
			("WIKI_BIOLOG_RULE1_B", "counter by 1, on failure the item is still consumed."),
			("WIKI_BIOLOG_RULE2_A", "After each delivery you must wait a cooldown before you can deliver"),
			("WIKI_BIOLOG_RULE2_B", "again. The waiting time of each mission is shown in the table below."),
			("WIKI_BIOLOG_RULE3_A", "Once a mission is completed you receive a permanent bonus that"),
			("WIKI_BIOLOG_RULE3_B", "stays on your character forever."),
		)
		rowY = self._RuleTable(rowY, rules)

		return rowY + 12

	# -- Missions table -----------------------------------------------------

	def _RenderMissionSection(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_BIOLOG_MISSIONS", "Missions"))
		try:
			import uibiologmanager
			groups = uibiologmanager.BIOLOG_MISSION_GROUPS
		except Exception:
			groups = []
		if not groups:
			return top
		cur = self._CurrentMissionId()
		meta = _LoadMissionMeta()

		x0 = self._TBL_X0
		fixed = self._TBL_COLS
		colW = [fixed[0], fixed[1], fixed[2], fixed[3], self._TBL_W - sum(fixed), fixed[4]]
		COL_LEVEL, COL_ITEM, COL_QTY, COL_CD, COL_REWARD, COL_STATUS = 0, 1, 2, 3, 4, 5
		# RTL flips the visual column order (status leftmost, level rightmost);
		# colX stays keyed by the logical column.
		if self._RTL():
			seq = (COL_STATUS, COL_REWARD, COL_CD, COL_QTY, COL_ITEM, COL_LEVEL)
		else:
			seq = (COL_LEVEL, COL_ITEM, COL_QTY, COL_CD, COL_REWARD, COL_STATUS)
		colX = {}
		x = x0
		for li in seq:
			colX[li] = x
			x += colW[li]

		headers = (
			LocaleText("WIKI_BIOLOG_COL_LEVEL", "Level"),
			LocaleText("WIKI_BIOLOG_COL_ITEM", "Item"),
			LocaleText("WIKI_BIOLOG_COL_QTY", "Quantity"),
			LocaleText("WIKI_BIOLOG_COL_COOLDOWN", "Cooldown"),
			LocaleText("WIKI_BIOLOG_COL_REWARD", "Reward"),
			LocaleText("WIKI_BIOLOG_COL_STATUS", "Status"),
		)
		self._Bar(x0, top, self._TBL_W, self._TBL_HEADER_H, self._COL_TABLE_HEADER_BG)
		for c in xrange(6):
			self._Text(headers[c], colX[c] + colW[c] / 2, top + 6, ingamewikidungeon._COL_TAN, align="center")

		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for g in groups:
			main = g["main"]
			bonuses = main.get("bonuses") or []
			rowH = max(36, 12 + 15 * len(bonuses))
			done = cur > main["id"]

			self._Bar(x0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			textY = rowY + rowH / 2 - 7
			self._Text(str(g["level"]), colX[COL_LEVEL] + colW[COL_LEVEL] / 2, textY, _COL_LEVEL, align="center")

			iconX = colX[COL_ITEM] + (colW[COL_ITEM] - 32) / 2
			iconY = rowY + (rowH - 32) / 2
			self._ItemIcon(main["item"], iconX, iconY, cellW=32, cellH=32)

			mark = "checked.png" if done else "unchecked.png"
			img = self._Img("d:/ymir work/ui/game/common/" + mark, colX[COL_STATUS], rowY)
			img.SetPosition(colX[COL_STATUS] + (colW[COL_STATUS] - img.GetWidth()) / 2, rowY + (rowH - img.GetHeight()) / 2)

			self._Text(str(main.get("count", 0)), colX[COL_QTY] + colW[COL_QTY] / 2, textY, self._COL_TABLE_VALUE, align="center")
			self._Text(self._CooldownText(meta, main["id"]), colX[COL_CD] + colW[COL_CD] / 2, textY, self._COL_TABLE_VALUE, align="center")

			by = rowY + (rowH - 15 * len(bonuses)) / 2 + 1
			for applyType, value in bonuses:
				self._Text(self._AffectText(applyType, value), colX[COL_REWARD] + colW[COL_REWARD] / 2, by, _COL_REWARD, align="center")
				by += 15

			rowY += rowH
			rowBounds.append(rowY)

		tableH = rowY - top
		for li in seq[:-1]:
			self._Bar(colX[li] + colW[li], top, 1, tableH, self._COL_TABLE_BORDER)
		self._Bar(x0, top, self._TBL_W, 1, self._COL_TABLE_BORDER)
		self._Bar(x0, top + self._TBL_HEADER_H, self._TBL_W, 1, self._COL_TABLE_BORDER)
		for by in rowBounds:
			self._Bar(x0, by, self._TBL_W, 1, self._COL_TABLE_BORDER)
		self._Bar(x0, top, 1, tableH, self._COL_TABLE_BORDER)
		self._Bar(x0 + self._TBL_W - 1, top, 1, tableH, self._COL_TABLE_BORDER)

		return rowY + 12

	def _CooldownText(self, meta, missionId):
		try:
			cd = int((meta.get(str(missionId)) or {}).get("cooldown", 0))
		except (AttributeError, TypeError, ValueError):
			cd = 0
		if cd <= 0:
			return "-"
		m = cd / 60
		if m < 60:
			return "%dm" % m
		if m % 60:
			return "%dh %dm" % (m / 60, m % 60)
		return "%dh" % (m / 60)
