# coding: latin_1
#
# Companion "Help" popup (the buffi-system explainer) -- binder.
#
# Layout chrome lives in uiscript/companionhelpwindow.py; the explanation itself is
# built here from ui.Table grids (tables are inherently code-built, like the in-game
# wiki) using the shared project table colour scheme. Content is static, so it is
# built once on first open and the board is resized to fit.
#
# The evolution numbers (level / INT / success%) are pulled live from
# app.GetBuffiEvolveInfo(stage) -- the single-source shared header -- so they never
# drift from the server's actual tuning. The ore / name facts are descriptive text.
#
# Opened by the Companion window's "?" button -> interface.OpenCompanionHelp().
import ui
import app
import item
import skill
import player
import localeinfo
import uitooltip

# ui.Table colour scheme: [lineColor, headerBg, rowBg, headerText, cellText] (0xAARRGGBB).
# Line colour is OPAQUE (0xff..) so the grid lines actually render -- this window has no scroll
# clip mask, so ui.Table's own CLine borders draw fine (the wiki must redraw them as Bars only
# because its table lives inside a clipped scrollBoard). Rest matches the buffi UI palette.
SCHEME = [0xff756657, 0xff281f1a, 0xff1a1615, 0xffcabdab, 0xffc7c7c7]

# Item vnums shown as real icons (item_proto data).
ORE_VNUM         = 91121   # "Buffi Ore (+3 INT)"  -> ITEM_BUFFI / BUFFI_ORE
NAME_SCROLL_VNUM = 91120   # the rename scroll      -> ITEM_BUFFI / BUFFI_NAME
# Buff skills the name scroll unlocks (the 2 premium buffi skills): 165 = Kwaesok (move/atk speed),
# 166 = Jeungryeok (attack power). skill.GetIconImage(vnum) gives the icon path (USE_V1).
SKILL_SPEED  = 165
SKILL_ATTACK = 166


class CompanionHelpWindow(ui.ScriptWindow):

	WINDOW_WIDTH = 360
	M            = 12            # left/right page margin
	CONTENT_W    = WINDOW_WIDTH - 2 * M   # 336 -> table width
	HEAD_H       = 22
	ROW_H        = 22
	GAP          = 8            # vertical gap between stacked tables

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Initialize()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		self.isLoaded = 0
		self.board    = None
		self.tables   = []     # built ui.Table grids (held so they aren't GC'd)
		self.icons    = []     # injected item/skill icon images (held so they aren't GC'd)
		self.itemTip  = None   # lazily-created item tooltip (ore / name-scroll hover)
		self.interface = None  # back-ref (set by interfacemodule) -> shared skill tooltip
		self.built    = 0

	def Destroy(self):
		self.tables = []
		self.icons  = []
		self.ClearDictionary()
		self.Initialize()

	def __L(self, key, default):
		# Help strings live in new_locale_game.txt (loaded dynamically into localeinfo);
		# fall back to English so the popup works even before the locale pack is rebuilt.
		return getattr(localeinfo, key, default)

	# ------------------------------------------------------------------
	# Load + bind
	# ------------------------------------------------------------------
	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/companionhelpwindow.py")

		try:
			self.board = self.GetChild("board")
			self.board.SetTitleName(self.__L("COMPANION_HELP_TITLE", "Buffi - Help"))
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
		except:
			import dbg
			dbg.TraceError("CompanionHelpWindow.__LoadWindow - bind failed")

	# ------------------------------------------------------------------
	# Content (built once, lazily, from ui.Table grids)
	# ------------------------------------------------------------------
	def __AddTitle(self, title, y):
		# A header-only table = a single full-width section bar (header bg + centred title).
		tbl = ui.Table(self.CONTENT_W, self.HEAD_H, SCHEME)
		tbl.SetParent(self)
		tbl.AddFlag("attach")
		tbl.set_columns([title], [self.CONTENT_W])
		tbl.Show()
		tbl.SetWindowHorizontalAlignLeft()
		tbl.SetPosition(self.M, y)
		self.tables.append(tbl)
		return y + tbl.GetHeight() + self.GAP

	def __DrawGrid(self, x, y, widths, rowHeights):
		# Redraw the full grid (outer border + inner dividers) as ui.Bar ON TOP of the table.
		# ui.Table draws its dividers as Line widgets, but each row's opaque background bar is
		# created AFTER the previous row's lines and covers them -> inner lines vanish. Bars
		# drawn last sit on top and always show. (Same fix the in-game wiki uses.)
		LINE_C = 0xff756657
		totalW = sum(widths)
		# horizontal lines: top, under-header, then under every row.
		ys = [y, y + self.HEAD_H]
		cum = y + self.HEAD_H
		for h in rowHeights:
			cum += h
			ys.append(cum)
		totalH = cum - y
		for yy in ys:
			bar = ui.Bar()
			bar.SetParent(self)
			bar.AddFlag("attach")
			bar.AddFlag("not_pick")
			bar.SetPosition(x, yy)
			bar.SetSize(totalW + 1, 1)
			bar.SetColor(LINE_C)
			bar.Show()
			self.tables.append(bar)
		# vertical lines: every column boundary, full height.
		cx = x
		xs = [cx]
		for w in widths:
			cx += w
			xs.append(cx)
		for xx in xs:
			bar = ui.Bar()
			bar.SetParent(self)
			bar.AddFlag("attach")
			bar.AddFlag("not_pick")
			bar.SetPosition(xx, y)
			bar.SetSize(1, totalH + 1)
			bar.SetColor(LINE_C)
			bar.Show()
			self.tables.append(bar)

	def __AddGrid(self, headers, widths, rows, y):
		# Multi-column data grid. Cells are centred (RTL-neutral); for Arabic the column
		# order is reversed so the table reads right-to-left, mirroring the in-game wiki.
		rtl = localeinfo.IsARABIC()
		h = list(headers)
		w = list(widths)
		data = [list(r) for r in rows]
		if rtl and len(h) > 1:
			h.reverse()
			w.reverse()
			for r in data:
				r.reverse()
		aligns = ["all:center"] * len(h)
		tbl = ui.Table(sum(w), self.HEAD_H, SCHEME)
		tbl.SetParent(self)
		tbl.AddFlag("attach")
		tbl.set_columns(h, w)
		for r in data:
			tbl.add_row(r, self.ROW_H, None, aligns, None)
		tbl.Show()
		tbl.SetWindowHorizontalAlignLeft()
		tbl.SetPosition(self.M, y)
		self.tables.append(tbl)
		self.__DrawGrid(self.M, y, w, [self.ROW_H] * len(data))
		return y + tbl.GetHeight() + self.GAP

	def __AddBullets(self, title, lines, y):
		# A single-column table: header = section title, one row per fact line. Lines align
		# to the reading edge (right for Arabic, left otherwise).
		rtl = localeinfo.IsARABIC()
		align = "horizontal:right" if rtl else "horizontal:left"
		tbl = ui.Table(self.CONTENT_W, self.HEAD_H, SCHEME)
		tbl.SetParent(self)
		tbl.AddFlag("attach")
		tbl.set_columns([title], [self.CONTENT_W])
		for ln in lines:
			tbl.add_row([ln], self.ROW_H, None, [align], None)
		tbl.Show()
		tbl.SetWindowHorizontalAlignLeft()
		tbl.SetPosition(self.M, y)
		self.tables.append(tbl)
		self.__DrawGrid(self.M, y, [self.CONTENT_W], [self.ROW_H] * len(lines))
		return y + tbl.GetHeight() + self.GAP

	# ------------------------------------------------------------------
	# Explanation tables (Ore / Name): a 2-column "Item | Effect" grid, wiki-style.
	# Each row pairs a REAL icon (item or unlocked-skill) with a short line, with
	# visible grid lines and a hover tooltip on every icon -- an explanation, not
	# a wall of words. Columns mirror right-to-left for Arabic, like the wiki.
	# A cell = (text, iconKind, vnum) where iconKind is None / "item" / "skill".
	# ------------------------------------------------------------------
	def __AddInfoTable(self, headers, widths, rows, y):
		rtl = localeinfo.IsARABIC()
		h = list(headers)
		w = list(widths)
		data = [list(r) for r in rows]
		if rtl:
			h.reverse()
			w.reverse()
			for r in data:
				r.reverse()
		tbl = ui.Table(sum(w), self.HEAD_H, SCHEME)
		tbl.SetParent(self)
		tbl.AddFlag("attach")
		tbl.set_columns(h, w)
		ROW = 40   # tall enough for a 32px icon
		for ri, row in enumerate(data):
			texts  = [c[0] for c in row]
			aligns = ["all:center"] * len(row)   # both icon + text cells centred
			tbl.add_row(texts, ROW, None, aligns, None)
			for ci, c in enumerate(row):
				if c[1]:
					self.__InjectIcon(tbl._tchildren.get("row_%d_c%d" % (ri, ci)), c[1], c[2])
		tbl.Show()
		tbl.SetWindowHorizontalAlignLeft()
		tbl.SetPosition(self.M, y)
		self.tables.append(tbl)
		self.__DrawGrid(self.M, y, w, [ROW] * len(data))
		return y + tbl.GetHeight() + self.GAP

	def __InjectIcon(self, cellWnd, kind, vnum):
		# A pickable, centred icon inside a table cell, with a hover tooltip (wiki _TableItemCell style).
		if not cellWnd or not vnum:
			return
		cw, chh = cellWnd.GetWidth(), cellWnd.GetHeight()
		ico = ui.ExpandedImageBox()
		ico.SetParent(cellWnd)
		if kind == "item":
			item.SelectItem(vnum)
			nm = item.GetIconImageFileName()
			if nm and nm.find("gr2") == -1:
				ico.LoadImage(nm)
			else:
				ico.LoadImage("icon/item/27995.tga")
			ico.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OnOverItem, vnum)
			ico.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OnOverOut)
			if app.ENABLE_INGAME_WIKI:
				ico.SAFE_SetEvent(self.__OnClickItem, "mouse_click", vnum)
		else:   # "skill"
			path = ""
			try:
				path = skill.GetIconImage(vnum)
			except:
				path = ""
			if not path:
				return
			ico.LoadImage(path)
			ico.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OnOverSkill, vnum)
			ico.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OnOverSkillOut)
		iw, ih = ico.GetWidth(), ico.GetHeight()
		SIDE = 32
		if iw > 0 and ih > 0 and (iw > SIDE or ih > SIDE):
			sc = min(float(SIDE) / iw, float(SIDE) / ih)
			ico.SetScale(sc, sc)
			iw, ih = int(iw * sc), int(ih * sc)
		ico.SetPosition((cw - iw) / 2, (chh - ih) / 2)
		ico.Show()
		self.icons.append(ico)

	# --- icon hover tooltips ---
	def __OnOverItem(self, vnum):
		if not self.itemTip:
			self.itemTip = uitooltip.ItemToolTip()
		self.itemTip.ClearToolTip()
		self.itemTip.SetItemToolTip(vnum)
		if app.ENABLE_INGAME_WIKI:
			self.itemTip.DeclareShortcut(("key_lclick",), self.__L("HELP_TIP_WIKI", "- Left click to open Wiki |Eemoji/key_lclick|e"))
			self.itemTip.ShowToolTip()

	def __OpenItemWiki(self, vnum):
		# Fail-silent hyperlink jump: the interface API builds the wiki lazily
		# under FAST_WARP_UI and no-ops before it exists.
		iface = getattr(self, "interface", None)
		if not iface or not hasattr(iface, "OpenWikiToItem"):
			return
		if self.itemTip:
			self.itemTip.HideToolTip()
		iface.OpenWikiToItem(vnum)

	def __OnClickItem(self, eventType, vnum):
		self.__OpenItemWiki(vnum)

	def __OnOverOut(self):
		if self.itemTip:
			self.itemTip.HideToolTip()

	def __OnOverSkill(self, vnum):
		# Reuse the shared skill tooltip (same as the Companion window). The buffi skills are
		# registered into client slots 130+ (index = vnum-163); pass that slot so the tooltip's
		# efficiency lookup matches. Falls back silently if the interface isn't wired.
		iface = self.interface
		if not iface or not getattr(iface, "tooltipSkill", None):
			return
		slot  = 130 + (vnum - 163)
		grade = player.GetSkillGradeNew(vnum)
		level = player.GetSkillLevelNew(vnum)
		iface.tooltipSkill.SetSkillNew(slot, vnum, grade, level)

	def __OnOverSkillOut(self):
		iface = self.interface
		if iface and getattr(iface, "tooltipSkill", None):
			iface.tooltipSkill.HideToolTip()

	def __AddOreCard(self, y):
		headers = [self.__L("COMPANION_HELP_COL_ITEM", "Item"), self.__L("COMPANION_HELP_COL_EFFECT", "Effect")]
		widths  = [80, self.CONTENT_W - 80]
		rows = [
			[("", "item", ORE_VNUM), (self.__L("COMPANION_HELP_ORE_GIVE", "Adds +3 INT each (up to +9 with 3 slots)."), None, 0)],
			[("", None, 0),          (self.__L("COMPANION_HELP_ORE_TEMP", "Temporary - disappears when it runs out."), None, 0)],
		]
		y = self.__AddTitle(self.__L("COMPANION_HELP_ORE_TITLE", "Buffi Ore"), y)
		return self.__AddInfoTable(headers, widths, rows, y)

	def __AddNameCard(self, y):
		headers = [self.__L("COMPANION_HELP_COL_ITEM", "Item"), self.__L("COMPANION_HELP_COL_EFFECT", "Effect")]
		widths  = [80, self.CONTENT_W - 80]
		rows = [
			[("", "item",  NAME_SCROLL_VNUM), (self.__L("COMPANION_HELP_NAME_GIVE",   "Custom name + 10% boss damage (7 days)."), None, 0)],
			[("", "skill", SKILL_SPEED),      (self.__L("COMPANION_HELP_NAME_SPEED",  "Unlocks the Speed buff."), None, 0)],
			[("", "skill", SKILL_ATTACK),     (self.__L("COMPANION_HELP_NAME_ATTACK", "Unlocks the Attack Power buff."), None, 0)],
		]
		y = self.__AddTitle(self.__L("COMPANION_HELP_NAME_TITLE", "Buffi Name"), y)
		return self.__AddInfoTable(headers, widths, rows, y)

	def __EvoRows(self):
		# Stage 0 (Default) + the 3 evolutions, pulled from the shared header so the numbers
		# match the server. Each app.GetBuffiEvolveInfo(stage) = (int, reqLevel, yang, chance, ...).
		def info(stage):
			try:
				if hasattr(app, "GetBuffiEvolveInfo"):
					return app.GetBuffiEvolveInfo(stage)
			except:
				pass
			return None

		rows = []
		# Default stage: INT only (no level gate / success roll).
		stage0Int = "80"
		i0 = info(0)
		if i0 and len(i0) >= 1:
			stage0Int = str(i0[0])
		rows.append([self.__L("COMPANION_HELP_STAGE0", "Default"), "1", stage0Int, "-"])

		nameKeys = ("COMPANION_HELP_STAGE1", "COMPANION_HELP_STAGE2", "COMPANION_HELP_STAGE3")
		nameDefs = ("Evo 1", "Evo 2", "Evo 3")
		fbLvl    = ("40", "80", "105")
		fbInt    = ("100", "140", "180")
		fbWin    = ("80%", "60%", "35%")
		for s in range(1, 4):
			lvl, intv, win = fbLvl[s - 1], fbInt[s - 1], fbWin[s - 1]
			i = info(s)
			if i and len(i) >= 4:
				intv = str(i[0])
				lvl  = str(i[1])
				win  = "%d%%" % i[3]
			rows.append([self.__L(nameKeys[s - 1], nameDefs[s - 1]), lvl, intv, win])
		return rows

	def __Build(self):
		if self.built or not self.board:
			return
		self.built = 1
		y = 32   # below the titlebar

		# --- Evolution & Intelligence ---
		y = self.__AddTitle(self.__L("COMPANION_HELP_EVO_TITLE", "Evolution & Intelligence"), y)
		headers = [
			self.__L("COMPANION_HELP_COL_STAGE", "Stage"),
			self.__L("COMPANION_HELP_COL_LEVEL", "Lv."),
			self.__L("COMPANION_HELP_COL_INT",   "INT"),
			self.__L("COMPANION_HELP_COL_WIN",   "Win%"),
		]
		widths = [126, 60, 70, 80]   # sum = CONTENT_W (336)
		y = self.__AddGrid(headers, widths, self.__EvoRows(), y)

		# --- Buffi Ore (icon card: the real ore item icon + 2 short facts) ---
		y = self.__AddOreCard(y)

		# --- Buffi Name (icon card: the name scroll + the 2 skill icons it unlocks) ---
		y = self.__AddNameCard(y)

		# Fit the board to the generated content.
		total = y + 4
		self.board.SetSize(self.WINDOW_WIDTH, total)
		self.SetSize(self.WINDOW_WIDTH, total)

	# ------------------------------------------------------------------
	# Lifecycle
	# ------------------------------------------------------------------
	def Open(self):
		self.__Build()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		if self.itemTip:
			self.itemTip.HideToolTip()
		self.__OnOverSkillOut()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
