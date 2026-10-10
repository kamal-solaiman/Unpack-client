# coding: latin_1
#
# Daily Alchemy Ore "Help" popup (the ore-system explainer) -- binder.
#
# Layout chrome lives in uiscript/alchemyorehelpwindow.py; the explanation itself is
# built here from a ui.Table grid (tables are inherently code-built, like the in-game
# wiki and the buffi Companion help) using the shared project table colour scheme.
# Content is static, so it is built once on first open and the board is resized to fit.
#
# Design brief: explain the SYSTEM, not the loot. Five icon rows, <=5 words each. The
# only place loot is shown is row 5 -- a single reward icon that cycles through the pool
# (goal item 51501 first). Opened by the reward InfoWindow's "?" button.
#
# Item-icon tooltips only (uitooltip.ItemToolTip is self-contained) -> no interfacemodule
# wiring and no skill back-ref, unlike the buffi build.
import ui
import item
import localeinfo
import uitooltip

# Same wheel art dir the InfoWindow loads its chrome from (info_bg / arrows / "?").
IMG_DIR = "spin_wheel/"

# ui.Table colour scheme: [lineColor, headerBg, rowBg, headerText, cellText] (0xAARRGGBB).
# Line colour is OPAQUE so the grid lines render; matches the buffi help palette.
SCHEME = [0xff756657, 0xff281f1a, 0xff1a1615, 0xffcabdab, 0xffc7c7c7]

# Row 5's rotating reward icon: the JSON reward pool, goal item 51501 first.
CYCLE_VNUMS = [51501, 51511, 51512, 51513, 51514, 51515, 51516, 51508, 51509, 51510]
CYCLE_TICKS = 45   # frames between icon swaps (~1s at 45 fps)


class AlchemyOreHelpWindow(ui.ScriptWindow):

	WINDOW_WIDTH = 300
	M            = 12                       # left/right page margin
	CONTENT_W    = WINDOW_WIDTH - 2 * M     # 276 -> table width
	ICON_W       = 60                       # icon column width
	HEAD_H       = 22
	ROW_H        = 40                       # tall enough for a 32px icon
	GAP          = 8

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Initialize()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		self.isLoaded  = 0
		self.board     = None
		self.tables    = []      # built ui.Table grids + grid Bars (held so they aren't GC'd)
		self.icons     = []      # injected icon images (held so they aren't GC'd)
		self.itemTip   = None    # lazily-created item tooltip (hover)
		self.built     = 0
		self.cycleIcon = None    # row 5's rotating reward ExpandedImageBox
		self.cycleIdx  = 0
		self.cycleVnum = CYCLE_VNUMS[0]
		self.cycleTick = 0
		self.cycleHover = 0
		self.cycleCW = 0
		self.cycleCHH = 0

	def Destroy(self):
		if self.itemTip:
			self.itemTip.HideToolTip()
		self.tables = []
		self.icons  = []
		self.cycleIcon = None
		self.ClearDictionary()
		self.Initialize()

	def __L(self, key, default):
		# Help strings live in new_locale_game.txt (loaded into localeinfo); fall back to
		# English so the popup works even before the locale pack is rebuilt.
		return getattr(localeinfo, key, default)

	# ------------------------------------------------------------------
	# Load + bind
	# ------------------------------------------------------------------
	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/alchemyorehelpwindow.py")

		try:
			self.board = self.GetChild("board")
			self.board.SetTitleName(self.__L("ALCHEMY_HELP_TITLE", "Alchemy Ore - Help"))
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
		except:
			import dbg
			dbg.TraceError("AlchemyOreHelpWindow.__LoadWindow - bind failed")

	# ------------------------------------------------------------------
	# Table primitives (copied from the buffi Companion help)
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

	def __AddIntro(self, lines, y):
		# A short centred description above the "How it works" grid (plain TextLines, no border).
		for ln in lines:
			t = ui.TextLine()
			t.SetParent(self)
			t.AddFlag("attach")
			t.SetPosition(self.WINDOW_WIDTH / 2, y)
			t.SetHorizontalAlignCenter()
			t.SetText(ln)
			t.SetPackedFontColor(0xffcabdab)
			t.Show()
			self.tables.append(t)
			y += 17
		return y + self.GAP

	def __DrawGrid(self, x, y, widths, rowHeights):
		# Redraw the full grid (outer border + inner dividers) as ui.Bar ON TOP of the table.
		# ui.Table draws dividers as Line widgets, but each row's opaque background bar is
		# created AFTER the previous row's lines and covers them -> inner lines vanish. Bars
		# drawn last sit on top and always show. (Same fix the in-game wiki / buffi help use.)
		LINE_C = 0xff756657
		totalW = sum(widths)
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

	# ------------------------------------------------------------------
	# The one content table: a 2-column "Icon | What" grid, wiki-style.
	# A cell = (text, iconKind, vnumOrPath) where iconKind is None / "item" / "img" / "cycle".
	# Columns mirror right-to-left for Arabic, like the wiki.
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
		for ri, row in enumerate(data):
			texts  = [c[0] for c in row]
			aligns = ["all:center"] * len(row)
			tbl.add_row(texts, self.ROW_H, None, aligns, None)
			for ci, c in enumerate(row):
				if c[1]:
					self.__InjectIcon(tbl._tchildren.get("row_%d_c%d" % (ri, ci)), c[1], c[2])
		tbl.Show()
		tbl.SetWindowHorizontalAlignLeft()
		tbl.SetPosition(self.M, y)
		self.tables.append(tbl)
		self.__DrawGrid(self.M, y, w, [self.ROW_H] * len(data))
		return y + tbl.GetHeight() + self.GAP

	def __LoadItemIcon(self, ico, vnum):
		# Real item icon (gr2 models fall back to a generic icon), as in the buffi help.
		item.SelectItem(vnum)
		nm = item.GetIconImageFileName()
		if nm and nm.find("gr2") == -1:
			ico.LoadImage(nm)
		else:
			ico.LoadImage("icon/item/27995.tga")

	def __CenterIcon(self, ico, cw, chh):
		ico.SetScale(1.0, 1.0)
		iw, ih = ico.GetWidth(), ico.GetHeight()
		SIDE = 32
		if iw > 0 and ih > 0 and (iw > SIDE or ih > SIDE):
			sc = min(float(SIDE) / iw, float(SIDE) / ih)
			ico.SetScale(sc, sc)
			iw, ih = int(iw * sc), int(ih * sc)
		ico.SetPosition((cw - iw) / 2, (chh - ih) / 2)

	def __InjectIcon(self, cellWnd, kind, vnum):
		# A pickable, centred icon inside a table cell, with a hover tooltip.
		if not cellWnd:
			return
		cw, chh = cellWnd.GetWidth(), cellWnd.GetHeight()
		ico = ui.ExpandedImageBox()
		ico.SetParent(cellWnd)
		if kind == "item":
			if not vnum:
				return
			self.__LoadItemIcon(ico, vnum)
			ico.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OnOverItem, vnum)
			ico.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OnOverOut)
		elif kind == "cycle":
			# Row 5's rotating reward icon: OnUpdate swaps it through CYCLE_VNUMS.
			self.__LoadItemIcon(ico, self.cycleVnum)
			ico.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OnOverCycleIn)
			ico.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OnOverCycleOut)
			self.cycleIcon = ico
			self.cycleCW, self.cycleCHH = cw, chh
		else:   # "img" -- a raw wheel PNG (decorative reinforcement of the row text)
			ico.LoadImage(IMG_DIR + vnum)   # vnum carries the filename for "img"
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

	def __OnOverOut(self):
		if self.itemTip:
			self.itemTip.HideToolTip()

	def __OnOverCycleIn(self):
		self.cycleHover = 1
		self.__OnOverItem(self.cycleVnum)

	def __OnOverCycleOut(self):
		self.cycleHover = 0
		self.__OnOverOut()

	# ------------------------------------------------------------------
	# Content (built once, lazily)
	# ------------------------------------------------------------------
	def __Build(self):
		if self.built or not self.board:
			return
		self.built = 1
		y = 30   # below the titlebar

		y = self.__AddIntro([
			self.__L("ALCHEMY_HELP_INTRO1", "Shared by all your chars on this PC"),
			self.__L("ALCHEMY_HELP_INTRO2", "Toggle drops on / off anytime"),
		], y)

		headers = ["", self.__L("ALCHEMY_HELP_HDR", "How it works")]
		widths  = [self.ICON_W, self.CONTENT_W - self.ICON_W]
		rows = [
			[("", "item", 99411),           (self.__L("ALCHEMY_HELP_R1", "Hunt mobs -> Ore"),          None, 0)],
			[("", "img",   "available.png"), (self.__L("ALCHEMY_HELP_R2", "Lv 30+ - toggle drops"),     None, 0)],
			[("", "img",   "full.png"),      (self.__L("ALCHEMY_HELP_R3", "300 / day - resets 00:00"),  None, 0)],
			[("", "img",   "jackpot.png"),   (self.__L("ALCHEMY_HELP_R4", "Full bar -> free Spin"),      None, 0)],
			[("", "cycle", 0),               (self.__L("ALCHEMY_HELP_R5", "Win 51501 & bonuses"),        None, 0)],
		]
		y = self.__AddInfoTable(headers, widths, rows, y)

		total = y + 4
		self.board.SetSize(self.WINDOW_WIDTH, total)
		self.SetSize(self.WINDOW_WIDTH, total)

	# ------------------------------------------------------------------
	# Rotating reward icon
	# ------------------------------------------------------------------
	def OnUpdate(self):
		if not self.IsShow():
			return
		if not self.cycleIcon:
			return
		self.cycleTick += 1
		if self.cycleTick < CYCLE_TICKS:
			return
		self.cycleTick = 0
		self.cycleIdx = (self.cycleIdx + 1) % len(CYCLE_VNUMS)
		self.cycleVnum = CYCLE_VNUMS[self.cycleIdx]
		self.__LoadItemIcon(self.cycleIcon, self.cycleVnum)
		self.__CenterIcon(self.cycleIcon, self.cycleCW, self.cycleCHH)
		if self.cycleHover:
			self.__OnOverItem(self.cycleVnum)   # keep the tooltip in sync while hovered

	# ------------------------------------------------------------------
	# Lifecycle
	# ------------------------------------------------------------------
	def OpenAt(self, owner):
		self.__Build()
		placed = 0
		try:
			ox, oy = owner.GetGlobalPosition()
			ow = owner.GetWidth()
			if localeinfo.IsARABIC():
				x = ox - self.GetWidth() - 4
			else:
				x = ox + ow + 4
			if x < 0:
				x = 0
			self.SetPosition(x, oy)
			placed = 1
		except:
			placed = 0
		if not placed:
			self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Open(self):
		self.OpenAt(None)

	def Close(self):
		if self.itemTip:
			self.itemTip.HideToolTip()
		self.cycleHover = 0
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
