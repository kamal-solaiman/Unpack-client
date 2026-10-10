# coding: latin_1
#
# Party Finder "Help" popup -- binder.
#
# Layout chrome lives in uiscript/partyfinderhelpwindow.py; the explanation itself is
# built here from ui.Table grids (tables are inherently code-built, like the in-game
# wiki) using the shared project table colour scheme. Content is static, so it is
# built once on first open and the board is resized to fit.
#
# Party Finder has no item/skill icons to show, so every section is a single-column
# bullet table (title bar + one short line per row) instead of an Item|Effect grid.
#
# Owned directly by PartyFinderWindow (uipartyfinder.py) -- opened by its "?" button.
import ui
import localeinfo

# ui.Table colour scheme: [lineColor, headerBg, rowBg, headerText, cellText] (0xAARRGGBB).
# Line colour is OPAQUE so the grid lines actually render -- this window has no scroll
# clip mask, so ui.Table's own CLine borders draw fine.
SCHEME = [0xff756657, 0xff281f1a, 0xff1a1615, 0xffcabdab, 0xffc7c7c7]


class PartyFinderHelpWindow(ui.ScriptWindow):

	WINDOW_WIDTH = 440
	M            = 12            # left/right page margin
	CONTENT_W    = WINDOW_WIDTH - 2 * M
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
		self.tables   = []     # built ui.Table grids + grid-line Bars (held so they aren't GC'd)
		self.built    = 0

	def Destroy(self):
		self.tables = []
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
		pyScrLoader.LoadScriptFile(self, "uiscript/partyfinderhelpwindow.py")

		try:
			self.board = self.GetChild("board")
			self.board.SetTitleName(self.__L("PF_HELP_TITLE", "Party Finder - Help"))
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
		except:
			import dbg
			dbg.TraceError("PartyFinderHelpWindow.__LoadWindow - bind failed")

	# ------------------------------------------------------------------
	# Content (built once, lazily, from ui.Table grids)
	# ------------------------------------------------------------------
	def __DrawGrid(self, x, y, widths, rowHeights):
		# Redraw the full grid (outer border + inner dividers) as ui.Bar ON TOP of the table.
		# ui.Table draws its dividers as Line widgets, but each row's opaque background bar is
		# created AFTER the previous row's lines and covers them -> inner lines vanish. Bars
		# drawn last sit on top and always show. (Same fix the in-game wiki uses.)
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

	def __Build(self):
		if self.built or not self.board:
			return
		self.built = 1
		y = 32   # below the titlebar

		browseLines = [
			self.__L("PF_HELP_BROWSE_1", "Board lists same-empire parties recruiting on ALL channels."),
			self.__L("PF_HELP_BROWSE_2", "Filter by category, 'Fits my level', or sort order."),
			self.__L("PF_HELP_BROWSE_3", "Click Request on a card - the leader gets notified."),
			self.__L("PF_HELP_BROWSE_4", "The result comes back as a chat message."),
			self.__L("PF_HELP_BROWSE_5", "One request per listing; a decline locks it briefly."),
		]
		y = self.__AddBullets(self.__L("PF_HELP_BROWSE_TITLE", "Browsing & Joining"), browseLines, y)

		postLines = [
			self.__L("PF_HELP_POST_1", "Solo players and party leaders may post one listing."),
			self.__L("PF_HELP_POST_2", "Choose a category, level range (your level +/-30), a note."),
			self.__L("PF_HELP_POST_3", "Listings expire after 20 minutes - Post/Update to refresh."),
			self.__L("PF_HELP_POST_4", "Auto-closes when full, disbanded, or leadership changes."),
		]
		y = self.__AddBullets(self.__L("PF_HELP_POST_TITLE", "Posting"), postLines, y)

		reqLines = [
			self.__L("PF_HELP_REQ_1", "Incoming requests appear on the right side of this window."),
			self.__L("PF_HELP_REQ_2", "Window closed? You get a popup question instead."),
			self.__L("PF_HELP_REQ_3", "Accept adds the applicant to your party."),
			self.__L("PF_HELP_REQ_4", "Unanswered requests expire after 60 seconds."),
		]
		y = self.__AddBullets(self.__L("PF_HELP_REQ_TITLE", "Requests (Leader)"), reqLines, y)

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
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
