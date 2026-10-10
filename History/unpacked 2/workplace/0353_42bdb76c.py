# coding: latin_1
#
# Pet "Upgrade Help" popup (growth pet rework) -- binder.
#
# Layout chrome lives in uiscript/petupgradehelpwindow.py; the explanation itself
# is built here from ui.Table grids (the buffi-help pattern, uicompanionhelp.py).
#
# TWO MODES, one per Upgrade-window tab (user feedback 2026-07-06: Evolution and
# Type upgrade are DIFFERENT systems -- one combined page was misleading):
#   MODE_EVOLVE -> level-gate grid + full-EXP note + per-stage material tables
#   MODE_TYPE   -> the Type-ladder mechanics (caps / costs / pity / evo gate)
# The "?" opens the mode of the ACTIVE tab and switching tabs re-syncs an open
# help window. Content rebuilds on every Open (the pages carry LIVE numbers);
# GC-push refreshes are SIGNATURE-GATED so pet EXP/point deltas never rebuild
# (RefreshCompanionPetPage fires per kill while farming).
#
# The Evolution materials region is SCROLLABLE -- a clip viewport + a masked
# content board moved by a ui.ScrollBarNew (the Companion bonus-list / wiki
# scrollBoard pattern). SetClippingMaskWindow propagates to every descendant
# (PythonWindow.cpp recurses existing children and AddChild stamps later ones).
# Inside the board each evolution stage renders as its OWN title bar + rows
# table. Picking is NOT mask-aware, so the icon hover handler additionally
# gates on the mouse being inside the viewport.
#
# ENGINE GOTCHA (why SCROLL_SCHEME exists): CBar::OnRender clamps its rect to the
# clip mask, but CLine::OnRender does NOT (PythonWindow.cpp) -- ui.Table's own
# Line dividers render OUTSIDE the viewport (seen in test 2026-07-06: grid lines
# leaking below the board). Every table inside the mask therefore uses an
# ALPHA-0 line colour (the wiki's trick) and the visible grid is drawn
# exclusively with mask-aware Bars (__DrawGridOn).
#
# Live single-sources (never drift from the server):
#   evolve levels    = interface.wndPetInfoWindow.GetEvolInfo (40/80/81)
#   evolve materials = uipetinfo.EVOLVE_MATERIALS_DICT (the dialog + Upgrade
#                      window read the SAME dict)
#   Type pity max    = player.GetPetTypeInfo()[4] when a pet is summoned
#   stat potions     = uicompanion.PET_STAT_POTION_VNUMS (the pet page's
#                      clickable stat rows read the SAME table)
#
# Opened by the pet Upgrade window's "?" button -> interface.OpenPetUpgradeHelp(tab).
import ui
import app
import item
import player
import localeinfo
import uitooltip
import uipetinfo
import uicompanion

# Mode indices MATCH uipetupgrade's TAB_EVOLVE / TAB_TYPE (the tab index is
# passed straight through interface.OpenPetUpgradeHelp).
MODE_EVOLVE = 0
MODE_TYPE   = 1

# ui.Table colour scheme: [lineColor, headerBg, rowBg, headerText, cellText] (0xAARRGGBB).
SCHEME        = [0xff756657, 0xff281f1a, 0xff1a1615, 0xffcabdab, 0xffc7c7c7]
# Inside the clip mask: engine Line widgets cannot clip -> alpha-0 lines, Bars draw the grid.
SCROLL_SCHEME = [0x00756657, 0xff281f1a, 0xff1a1615, 0xffcabdab, 0xffc7c7c7]


class PetUpgradeHelpWindow(ui.ScriptWindow):

	WINDOW_WIDTH = 360
	M            = 12            # left/right page margin
	CONTENT_W    = WINDOW_WIDTH - 2 * M   # 336
	HEAD_H       = 22
	ROW_H        = 22
	GAP          = 8             # vertical gap between stacked tables
	# Scrollable materials region: 32px icons + padding per row; the view shows
	# exactly ONE full stage block (its title bar + 4 material rows).
	MAT_ROW      = 36
	MAT_VIEW_H   = 22 + 4 * 36   # HEAD_H + 4*MAT_ROW
	SB_W         = 16            # scrollbar column (12px bar + gap)
	POTION_CYCLE_SEC = 1.0       # stat-potion strip: seconds each size (S/M/L) stays shown

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Initialize()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		self.isLoaded  = 0
		self.board     = None
		self.tables    = []    # built ui.Table grids / bars / notes (held so they aren't GC'd)
		self.icons     = []    # injected item icon images (held so they aren't GC'd)
		self.itemTip   = None  # lazily-created item tooltip (material hover)
		self.interface = None  # back-ref (set by interfacemodule) -> evolve-level single source
		self.builtMode = None  # which mode's content is currently built (None = nothing yet)
		self.liveSig   = None  # live-data signature of the built content (Refresh gate)
		# Scrollable materials region state (MODE_EVOLVE only).
		self.matViewport    = None
		self.matScrollBoard = None
		self.matScroll      = None
		self.matContentH    = 0
		self.matOverflow    = 0
		# Stat-potion strip state (MODE_TYPE only): each cell cycles S -> M -> L.
		self.potionIcons     = []    # [{"icos","vnums","cur"}] per stat cell
		self.potionHover     = None  # strip index under the cursor (tooltip re-sync)
		self.potionCycleIdx  = 0
		self.potionNextCycle = 0

	def Destroy(self):
		self.tables = []
		self.icons  = []
		self.ClearDictionary()
		self.Initialize()

	def GetMode(self):
		return self.builtMode

	def __L(self, key, default):
		# Help strings live in new_locale_game.txt; fall back to English so the
		# popup works even before the locale pack is rebuilt.
		return getattr(localeinfo, key, default)

	# ------------------------------------------------------------------
	# Load + bind
	# ------------------------------------------------------------------
	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/petupgradehelpwindow.py")

		try:
			self.board = self.GetChild("board")
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
		except:
			import dbg
			dbg.TraceError("PetUpgradeHelpWindow.__LoadWindow - bind failed")

	# ------------------------------------------------------------------
	# Table builders (the uicompanionhelp.py helpers, + the scroll variant)
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

	def __DrawGridOn(self, parent, x, y, widths, rowHeights, headH):
		# Redraw the full grid (outer border + inner dividers) as ui.Bar ON TOP of the
		# table -- ui.Table's own Line dividers get covered by the later rows' opaque
		# background bars (and, inside the clip mask, would not clip at all: CLine's
		# render is not mask-aware while CBar's is). Parent-relative so the scrolled
		# variant clips + moves with its content board. headH=0 -> headerless.
		LINE_C = 0xff756657
		totalW = sum(widths)
		ys = [y]
		cum = y
		if headH > 0:
			cum += headH
			ys.append(cum)
		for h in rowHeights:
			cum += h
			ys.append(cum)
		totalH = cum - y
		for yy in ys:
			bar = ui.Bar()
			bar.SetParent(parent)
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
			bar.SetParent(parent)
			bar.AddFlag("attach")
			bar.AddFlag("not_pick")
			bar.SetPosition(xx, y)
			bar.SetSize(1, totalH + 1)
			bar.SetColor(LINE_C)
			bar.Show()
			self.tables.append(bar)

	def __AddGrid(self, headers, widths, rows, y):
		# Multi-column data grid, centred cells (RTL-neutral); Arabic reverses the
		# column order so the table reads right-to-left (wiki pattern).
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
		self.__DrawGridOn(self, self.M, y, w, [self.ROW_H] * len(data), self.HEAD_H)
		return y + tbl.GetHeight() + self.GAP

	def __AddBullets(self, title, lines, y):
		# A single-column table: header = section title, one row per fact line.
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
		self.__DrawGridOn(self, self.M, y, [self.CONTENT_W], [self.ROW_H] * len(lines), self.HEAD_H)
		return y + tbl.GetHeight() + self.GAP

	def __AddNote(self, text, y):
		# A borderless one-liner between tables (window-centre anchored: RTL-safe).
		note = ui.TextLine()
		note.SetParent(self)
		note.AddFlag("attach")
		note.AddFlag("not_pick")
		note.SetPackedFontColor(0xffd1b183)
		note.SetHorizontalAlignCenter()
		note.SetPosition(self.WINDOW_WIDTH / 2, y)
		note.SetText(text)
		note.Show()
		self.tables.append(note)
		return y + 16 + self.GAP

	# ------------------------------------------------------------------
	# Scrollable materials region: fixed column header outside the mask, then
	# ONE TABLE PER EVOLUTION STAGE (title bar + rows) inside the masked board.
	# ------------------------------------------------------------------
	def __AddScrollStages(self, headers, widths, stages, y, iconCol):
		# stages = [(stageTitle, [(vnum, name, count), ...]), ...]
		rtl = localeinfo.IsARABIC()
		h = list(headers)
		w = list(widths)
		if rtl and len(h) > 1:
			h.reverse()
			w.reverse()
			iconColR = len(w) - 1 - iconCol
		else:
			iconColR = iconCol
		tableW = sum(w)
		hx = self.M + (self.SB_W if rtl else 0)   # scrollbar sits on the outer edge

		# Fixed column header (never scrolls; outside the mask -> opaque lines OK).
		head = ui.Table(tableW, self.HEAD_H, SCHEME)
		head.SetParent(self)
		head.AddFlag("attach")
		head.set_columns(h, w)
		head.Show()
		head.SetWindowHorizontalAlignLeft()
		head.SetPosition(hx, y)
		self.tables.append(head)
		self.__DrawGridOn(self, hx, y, w, [], self.HEAD_H)
		y += self.HEAD_H

		contentH = 0
		for (title, rows) in stages:
			contentH += self.HEAD_H + len(rows) * self.MAT_ROW
		viewH = min(contentH, self.MAT_VIEW_H)

		# Viewport + masked content board (the Companion bonus-list pattern).
		viewport = ui.Window()
		viewport.SetParent(self)
		viewport.AddFlag("attach")
		viewport.AddFlag("not_pick")
		viewport.SetPosition(hx, y)
		viewport.SetSize(tableW + 1, viewH)
		viewport.Show()
		self.matViewport = viewport
		self.tables.append(viewport)

		scrollBoard = ui.Window()
		scrollBoard.SetParent(viewport)
		scrollBoard.AddFlag("attach")
		scrollBoard.AddFlag("not_pick")
		if app.USE_CLIP_MASK:
			scrollBoard.SetClippingMaskWindow(viewport)
		scrollBoard.SetPosition(0, 0)
		scrollBoard.SetSize(tableW, contentH)
		scrollBoard.Show()
		self.matScrollBoard = scrollBoard
		self.tables.append(scrollBoard)

		# Per-stage blocks: a title bar + a headerless rows table, all SCROLL_SCHEME
		# (alpha-0 engine lines) with the visible grid drawn by mask-aware Bars.
		aligns = ["all:center"] * len(w)
		yy = 0
		for (title, rows) in stages:
			ttl = ui.Table(tableW, self.HEAD_H, SCROLL_SCHEME)
			ttl.SetParent(scrollBoard)
			ttl.AddFlag("attach")
			ttl.set_columns([title], [tableW])
			ttl.Show()
			ttl.SetWindowHorizontalAlignLeft()
			ttl.SetPosition(0, yy)
			self.tables.append(ttl)
			self.__DrawGridOn(scrollBoard, 0, yy, [tableW], [], self.HEAD_H)
			yy += self.HEAD_H

			data = []
			for (vnum, name, count) in rows:
				r = ["", name, count]   # icon cell text stays blank
				if rtl:
					r.reverse()
				data.append(r)
			tbl = ui.Table(tableW, 0, SCROLL_SCHEME)   # head_height 0 = headerless
			tbl.SetParent(scrollBoard)
			tbl.AddFlag("attach")
			tbl.set_columns([""] * len(w), w)
			for r in data:
				tbl.add_row(r, self.MAT_ROW, None, aligns, None)
			tbl.Show()
			tbl.SetWindowHorizontalAlignLeft()
			tbl.SetPosition(0, yy)
			self.tables.append(tbl)
			for ri, (vnum, name, count) in enumerate(rows):
				if vnum:
					self.__InjectIcon(tbl._tchildren.get("row_%d_c%d" % (ri, iconColR)), vnum)
			self.__DrawGridOn(scrollBoard, 0, yy, w, [self.MAT_ROW] * len(rows), 0)
			yy += len(rows) * self.MAT_ROW

		# Scrollbar on the outer edge; hidden when the content fits.
		self.matContentH = contentH
		self.matOverflow = max(0, contentH - viewH)
		scroll = ui.ScrollBarNew()
		scroll.SetParent(self)
		scroll.AddFlag("attach")
		# CRITICAL: ScrollBarNew's own OnRunMouseWheel has NO position gate and the
		# engine traversal reaches children first -- left enabled it would consume
		# wheel events GLOBALLY (and shadow this window's gated handler). Disabled,
		# the popup's OnRunMouseWheel below is the single wheel path (uishopsearch
		# house pattern).
		scroll.allow_on_run_mouse_wheel = False
		scroll.SetScrollBarSize(viewH)
		scroll.SetPosition(self.M if rtl else hx + tableW + 4, y)
		self.matScroll = scroll
		self.tables.append(scroll)
		if self.matOverflow > 0:
			scroll.SetMiddleBarSize(float(viewH) / float(contentH))
			# One wheel notch / arrow step ~= one material row.
			scroll.SetScrollStep(float(self.MAT_ROW) / float(self.matOverflow))
			scroll.SetScrollEvent(ui.__mem_func__(self.__OnMatScroll))
			scroll.SetPos(0.0)
			scroll.Show()
		else:
			scroll.Hide()

		return y + viewH + self.GAP

	def __OnMatScroll(self):
		if not self.matScrollBoard or not self.matScroll:
			return
		if self.matOverflow <= 0:
			self.matScrollBoard.SetPosition(0, 0)
			return
		self.matScrollBoard.SetPosition(0, -int(self.matOverflow * self.matScroll.GetPos()))

	def OnRunMouseWheel(self, nLen):
		# Wheel anywhere over the popup drives the materials scroller (the engine
		# walks the pointed-window chain calling OnRunMouseWheel until True).
		if not self.matScroll or self.matOverflow <= 0:
			return False
		if not self.IsInPosition():
			return False
		if nLen > 0:
			self.matScroll.OnUp()
		elif nLen < 0:
			self.matScroll.OnDown()
		return True

	# ------------------------------------------------------------------
	# Icons + tooltips
	# ------------------------------------------------------------------
	def __InjectIcon(self, cellWnd, vnum):
		# A pickable, centred item icon inside a table cell, with a hover tooltip.
		if not cellWnd or not vnum:
			return
		cw, chh = cellWnd.GetWidth(), cellWnd.GetHeight()
		ico = ui.ExpandedImageBox()
		ico.SetParent(cellWnd)
		item.SelectItem(vnum)
		nm = item.GetIconImageFileName()
		if nm and nm.find("gr2") == -1:
			ico.LoadImage(nm)
		else:
			ico.LoadImage("icon/item/27995.tga")
		ico.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OnOverMatItem, vnum)
		ico.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OnOverOut)
		if app.ENABLE_INGAME_WIKI:
			ico.SAFE_SetEvent(self.__OnClickMatItem, "mouse_click", vnum)
		iw, ih = ico.GetWidth(), ico.GetHeight()
		SIDE = 32
		if iw > 0 and ih > 0 and (iw > SIDE or ih > SIDE):
			sc = min(float(SIDE) / iw, float(SIDE) / ih)
			ico.SetScale(sc, sc)
			iw, ih = int(iw * sc), int(ih * sc)
		ico.SetPosition((cw - iw) / 2, (chh - ih) / 2)
		ico.Show()
		self.icons.append(ico)

	def __OnOverMatItem(self, vnum):
		# In-viewport guard: picking is NOT mask-aware, so an icon scrolled out of
		# the clip still has a live rect -- ignore hovers landing outside the view.
		vp = self.matViewport
		if vp and not vp.IsInPosition():
			return
		if not self.itemTip:
			self.itemTip = uitooltip.ItemToolTip()
		self.itemTip.ClearToolTip()
		self.itemTip.SetItemToolTip(vnum)
		if app.ENABLE_INGAME_WIKI:
			self.itemTip.DeclareShortcut(("key_lclick",), self.__L("HELP_TIP_WIKI", "- Left click to open Wiki |Eemoji/key_lclick|e"))
			self.itemTip.ShowToolTip()

	def __OnClickMatItem(self, eventType, vnum):
		# Same in-viewport guard as the hover: picking is not mask-aware, so an
		# icon scrolled out of the clip still has a live rect.
		vp = self.matViewport
		if vp and not vp.IsInPosition():
			return
		self.__OpenItemWiki(vnum)

	def __OpenItemWiki(self, vnum):
		# Fail-silent hyperlink jump: the interface API builds the wiki lazily
		# under FAST_WARP_UI and no-ops before it exists.
		iface = getattr(self, "interface", None)
		if not iface or not hasattr(iface, "OpenWikiToItem"):
			return
		if self.itemTip:
			self.itemTip.HideToolTip()
		iface.OpenWikiToItem(vnum)

	def __OnOverOut(self):
		if self.itemTip:
			self.itemTip.HideToolTip()

	# ------------------------------------------------------------------
	# Stat-potion strip (MODE_TYPE, pure visual): one bordered row with the
	# three stat potions; each cell cycles S -> M -> L. All size-class icons
	# are PRE-LOADED per cell and the cycle is Show/Hide only -- LoadImage at
	# runtime would debug-print "LOAD IMAGE" every swap (ImageBox.LoadImage
	# prints for any widget with events already bound) and reload the texture.
	# Vnums come from uicompanion.PET_STAT_POTION_VNUMS -- the SAME table the
	# pet page's clickable stat rows use, so shipping the real vnums there
	# updates this strip for free.
	# ------------------------------------------------------------------
	def __AddPotionRow(self, y):
		families = []
		for fam in getattr(uicompanion, "PET_STAT_POTION_VNUMS", ()):
			fam = [v for v in fam if v]
			if fam:
				families.append(fam)
		if not families:
			return y
		if localeinfo.IsARABIC():
			families.reverse()   # stat reading order follows the text direction
		n = len(families)
		w = [self.CONTENT_W / n] * n
		w[-1] = self.CONTENT_W - sum(w[:-1])
		tbl = ui.Table(self.CONTENT_W, 0, SCHEME)   # head_height 0 = headerless
		tbl.SetParent(self)
		tbl.AddFlag("attach")
		tbl.set_columns([""] * n, w)
		tbl.add_row([""] * n, self.MAT_ROW, None, ["all:center"] * n, None)
		tbl.Show()
		tbl.SetWindowHorizontalAlignLeft()
		tbl.SetPosition(self.M, y)
		self.tables.append(tbl)
		self.__DrawGridOn(self, self.M, y, w, [self.MAT_ROW], 0)
		for i in range(n):
			cell = tbl._tchildren.get("row_0_c%d" % i)
			if not cell:
				continue
			pos = len(self.potionIcons)
			icos = []
			for vnum in families[i]:
				ico = self.__MakePotionIcon(cell, vnum, pos)
				icos.append(ico)
				self.icons.append(ico)
			icos[0].Show()
			self.potionIcons.append({"icos": icos, "vnums": families[i], "cur": families[i][0]})
		self.potionCycleIdx  = 0
		self.potionNextCycle = app.GetTime() + self.POTION_CYCLE_SEC
		return y + self.MAT_ROW + self.GAP

	def __MakePotionIcon(self, cell, vnum, pos):
		# One pre-loaded, hidden size-class icon, centred in its cell. ORDER
		# MATTERS: LoadImage runs BEFORE the hover events are bound (see the
		# strip comment above). NOTE: item.SelectItem substitutes item 60001
		# for unknown vnums, so placeholder potion vnums render 60001's icon
		# until the real ones land in PET_STAT_POTION_VNUMS.
		ico = ui.ExpandedImageBox()
		ico.SetParent(cell)
		nm = ""
		try:
			item.SelectItem(vnum)
			nm = item.GetIconImageFileName()
		except:
			pass
		if nm and nm.find("gr2") == -1:
			ico.LoadImage(nm)
		else:
			ico.LoadImage("icon/item/27995.tga")
		iw, ih = ico.GetWidth(), ico.GetHeight()
		SIDE = 32
		if iw > 0 and ih > 0 and (iw > SIDE or ih > SIDE):
			sc = min(float(SIDE) / iw, float(SIDE) / ih)
			ico.SetScale(sc, sc)
			iw, ih = int(iw * sc), int(ih * sc)
		ico.SetPosition((cell.GetWidth() - iw) / 2, (cell.GetHeight() - ih) / 2)
		# A plain int index -- storing the entry dict in the icon's event args
		# would close an ico->args->entry->ico ref cycle, and py2's GC never
		# collects cycles through __del__ (ui.Window has one).
		ico.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OnOverPotion, pos)
		ico.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OnOverPotionOut)
		if app.ENABLE_INGAME_WIKI:
			ico.SAFE_SetEvent(self.__OnClickPotion, "mouse_click", pos)
		ico.Hide()
		return ico

	def __OnOverPotion(self, pos):
		if pos < 0 or pos >= len(self.potionIcons):
			return
		self.potionHover = pos
		if not self.itemTip:
			self.itemTip = uitooltip.ItemToolTip()
		self.itemTip.ClearToolTip()
		self.itemTip.SetItemToolTip(self.potionIcons[pos]["cur"])
		if app.ENABLE_INGAME_WIKI:
			self.itemTip.DeclareShortcut(("key_lclick",), self.__L("HELP_TIP_WIKI", "- Left click to open Wiki |Eemoji/key_lclick|e"))
			self.itemTip.ShowToolTip()

	def __OnClickPotion(self, eventType, pos):
		# The strip cycles S -> M -> L, so the jump follows the icon on screen.
		if pos < 0 or pos >= len(self.potionIcons):
			return
		self.__OpenItemWiki(self.potionIcons[pos]["cur"])

	def __OnOverPotionOut(self):
		self.potionHover = None
		if self.itemTip:
			self.itemTip.HideToolTip()

	def OnUpdate(self):
		# Drives the potion strip's S -> M -> L cycling (the list is empty
		# outside MODE_TYPE). Show/Hide swaps only -- never drop a widget ref
		# from inside OnUpdate (wndMgr teardown rule).
		if not self.potionIcons:
			return
		now = app.GetTime()
		if now < self.potionNextCycle:
			return
		self.potionNextCycle = now + self.POTION_CYCLE_SEC
		self.potionCycleIdx += 1
		for pos, entry in enumerate(self.potionIcons):
			icos = entry["icos"]
			if len(icos) < 2:
				continue
			k = self.potionCycleIdx % len(icos)
			for j, ico in enumerate(icos):
				if j == k:
					ico.Show()
				else:
					ico.Hide()
			entry["cur"] = entry["vnums"][k]
			# Keep the tooltip honest when the icon changes under a stationary
			# cursor (the engine only re-picks on mouse move).
			if pos == self.potionHover and self.itemTip and self.itemTip.IsShow():
				self.itemTip.ClearToolTip()
				self.itemTip.SetItemToolTip(entry["cur"])

	# ------------------------------------------------------------------
	# Content data (live single-sources with shipped fallbacks)
	# ------------------------------------------------------------------
	def __GetEvolRequiredLevel(self, evolLevel, fallback):
		iface = getattr(self, "interface", None)
		petWnd = getattr(iface, "wndPetInfoWindow", None) if iface else None
		if petWnd:
			try:
				lvl = petWnd.GetEvolInfo(evolLevel)
				if lvl:
					return lvl
			except:
				pass
		return fallback

	def __EvoRows(self):
		fmt = self.__L("PET_UP_HELP_STAGE_FMT", "Evo %d")
		rows = []
		for evol, fallback in ((1, 40), (2, 80), (3, 81)):
			rows.append([fmt % evol, str(self.__GetEvolRequiredLevel(evol, fallback))])
		return rows

	def __MatStages(self):
		# [(stageTitle, [(vnum, itemName, countText), ...]), ...] -- one block per
		# evolution stage. Same dict the evolve dialog + Upgrade window read.
		stages = []
		matsDict = getattr(uipetinfo, "EVOLVE_MATERIALS_DICT", None)
		if not matsDict:
			return stages
		fmt = self.__L("PET_UP_HELP_STAGE_FMT", "Evo %d")
		for evol in sorted(matsDict.keys()):
			rows = []
			for pair in matsDict[evol]:
				vnum = pair[0]
				count = pair[1]
				if not vnum:
					continue
				name = ""
				try:
					item.SelectItem(vnum)
					name = item.GetItemName()
				except:
					pass
				rows.append((vnum, name, str(count)))
			if rows:
				stages.append((fmt % evol, rows))
		return stages

	def __GetPityMax(self):
		try:
			if hasattr(player, "GetPetTypeInfo") and player.GetActivePetItemId():
				info = player.GetPetTypeInfo()
				if len(info) >= 5 and info[4] > 0:
					return info[4]
		except:
			pass
		return 3   # shipped default (server GROWTH_PET_TYPE pity)

	def __GetTypeMax(self):
		if hasattr(player, "GetPetTypeInfo"):
			try:
				info = player.GetPetTypeInfo()
				if info[1]:
					return info[1]
			except:
				pass
		return 6

	def __TypeCapRows(self):
		# Per-Type stat caps from the LIVE GC ladder push; "(current)" marks the
		# summoned pet's Type. Returns [] when no data arrived yet (no pet / old
		# build) so the caller skips the grid instead of showing zeros.
		if not hasattr(player, "GetPetTypeLadderRung"):
			return []
		curType = 0
		if hasattr(player, "GetPetTypeInfo"):
			try:
				curType = player.GetPetTypeInfo()[0]
			except:
				pass
		fmtType   = self.__L("PET_UP_HELP_TYPE_FMT", "Type %d")
		curSuffix = self.__L("PET_UP_HELP_TYPE_CURRENT", " (current)")
		rows = []
		for t in range(1, self.__GetTypeMax() + 1):
			rung = player.GetPetTypeLadderRung(t)
			cap = rung[0]
			if not cap:
				return []   # ladder not pushed yet -> no live data
			label = fmtType % t
			if t == curType:
				label += curSuffix
			rows.append([label, "%.1f%%" % (cap / 10.0)])
		return rows

	def __TypeLadderStages(self):
		# [(rungTitle, [(vnum, name, count), ...]), ...] from the LIVE ladder push:
		# title = "Type N-1 -> N (chance%)" plus the evolution gate when one applies;
		# rows = the rung's materials + a Yang line. Server tuning reaches this with
		# no client patch (the GC push carries the whole table).
		if not hasattr(player, "GetPetTypeLadderRung"):
			return []
		fmt    = self.__L("PET_UP_HELP_RUNG_FMT",     "Type %d -> %d   (%d%% success)")
		fmtEvo = self.__L("PET_UP_HELP_RUNG_EVO_FMT", "Type %d -> %d   (%d%% - needs Evo %d)")
		yangLabel = self.__L("PET_UP_HELP_YANG", "Yang")
		stages = []
		for t in range(2, self.__GetTypeMax() + 1):
			rung = player.GetPetTypeLadderRung(t)
			chance = rung[1]
			evoReq = rung[2]
			yang   = rung[3]
			rows = []
			for (vnum, count) in rung[4:9]:
				if not vnum:
					continue
				name = ""
				try:
					item.SelectItem(vnum)
					name = item.GetItemName()
				except:
					pass
				rows.append((vnum, name, str(count)))
			if yang > 0:
				rows.append((0, "%s: %s" % (yangLabel, localeinfo.NumberToMoneyStringNoUnit(yang)), ""))
			if not rows:
				continue
			if evoReq > 1:
				title = fmtEvo % (t - 1, t, chance, evoReq)
			else:
				title = fmt % (t - 1, t, chance)
			stages.append((title, rows))
		return stages

	# ------------------------------------------------------------------
	# Build (always rebuilds -- the pages carry live numbers; Refresh gates
	# on __LiveSig so only RELEVANT changes trigger it)
	# ------------------------------------------------------------------
	def __LiveSig(self, mode):
		# Everything live the pages render: Type info (type/pity/chance/caps),
		# the pet's evolution level, and the pet identity. Pet EXP/lifetime
		# deltas do NOT enter the signature, so per-kill pushes are no-ops.
		sig = (mode,)
		try:
			if hasattr(player, "GetPetTypeInfo"):
				sig += tuple(player.GetPetTypeInfo())
		except:
			pass
		try:
			petID = player.GetActivePetItemId()
			sig += (petID,)
			if petID:
				sig += (player.GetPetItem(petID)[1],)   # evolution level
		except:
			pass
		return sig

	def __Build(self, mode):
		# ALWAYS rebuilds: the Type page carries live numbers (current-Type marker,
		# pity, pity-floored chance) that change with every upgrade attempt, and a
		# rebuild is ~40 lightweight widgets -- caching would only serve staleness.
		if not self.board:
			return
		# Tear down the previous content: dropping the refs GC-destroys the widgets
		# (safe here -- called from Open/Refresh, never from a child's dispatch).
		if self.itemTip:
			self.itemTip.HideToolTip()   # a hovered icon dies with the rebuild
		self.tables = []
		self.icons  = []
		self.matViewport    = None
		self.matScrollBoard = None
		self.matScroll      = None
		self.matContentH    = 0
		self.matOverflow    = 0
		self.potionIcons     = []
		self.potionHover     = None
		self.potionCycleIdx  = 0
		self.potionNextCycle = 0
		self.builtMode = mode
		y = 32   # below the titlebar

		if mode == MODE_TYPE:
			# ===== UPGRADE TYPE help (the Type tab's own page) =====
			# Everything numeric is LIVE (GC ladder push / GetPetTypeInfo): the cap
			# grid, the per-rung chance / evolution gates / materials / Yang.
			self.board.SetTitleName(self.__L("PET_UP_HELP_TITLE_TYPE", "Upgrade Type - Help"))
			pity = self.__GetPityMax()
			lines = [
				self.__L("PET_UP_HELP_TYPE_CAPS", "Each Type (1-6) raises the stat caps."),
				self.__L("PET_UP_HELP_TYPE_COST", "Every attempt consumes materials and Yang."),
				self.__L("PET_UP_HELP_TYPE_PITY", "Can fail - guaranteed after %s failed tries.") % pity,
			]
			y = self.__AddBullets(self.__L("PET_UP_HELP_TYPE_TITLE", "Upgrade Type"), lines, y)
			# The three stat potions, each icon cycling S -> M -> L (pure visual).
			y = self.__AddPotionRow(y)
			# Stat cap per Type ("(current)" marks the summoned pet's Type).
			capRows = self.__TypeCapRows()
			if capRows:
				headers = [
					self.__L("PET_UP_HELP_COL_TYPE", "Type"),
					self.__L("PET_UP_HELP_COL_CAP",  "Stat cap"),
				]
				y = self.__AddGrid(headers, [168, 168], capRows, y)
			# The full upgrade ladder: one block per rung (chance + evo gate in the
			# title; the rung's materials + Yang as rows), scrolled like the
			# evolution materials.
			rungs = self.__TypeLadderStages()
			if rungs:
				y = self.__AddTitle(self.__L("PET_UP_HELP_LADDER_TITLE", "Upgrade Costs"), y)
				headers = [
					self.__L("PET_UP_HELP_COL_ITEM",  "Item"),
					self.__L("PET_UP_HELP_COL_NAME",  "Material"),
					self.__L("PET_UP_HELP_COL_COUNT", "Count"),
				]
				y = self.__AddScrollStages(headers, [52, 194, 70], rungs, y, 0)
		else:
			# ===== EVOLUTION help (the Evolve tab's own page) =====
			self.board.SetTitleName(self.__L("PET_UP_HELP_TITLE_EVO", "Evolution - Help"))
			y = self.__AddTitle(self.__L("PET_UP_HELP_EVO_TITLE", "Evolution"), y)
			headers = [
				self.__L("PET_UP_HELP_COL_STAGE", "Evolution"),
				self.__L("PET_UP_HELP_COL_LEVEL", "Pet Lv."),
			]
			y = self.__AddGrid(headers, [168, 168], self.__EvoRows(), y)
			y = self.__AddNote(self.__L("PET_UP_HELP_EVO_FULLEXP", "Needs a FULL EXP bar and the materials below."), y)
			stages = self.__MatStages()
			if stages:
				y = self.__AddTitle(self.__L("PET_UP_HELP_MAT_TITLE", "Evolution Materials"), y)
				headers = [
					self.__L("PET_UP_HELP_COL_ITEM",  "Item"),
					self.__L("PET_UP_HELP_COL_NAME",  "Material"),
					self.__L("PET_UP_HELP_COL_COUNT", "Count"),
				]
				# widths sum = CONTENT_W - SB_W - 4 (scrollbar column + gap)
				y = self.__AddScrollStages(headers, [52, 194, 70], stages, y, 0)

		# Fit the board to the generated content.
		total = y + 4
		self.board.SetSize(self.WINDOW_WIDTH, total)
		self.SetSize(self.WINDOW_WIDTH, total)
		self.liveSig = self.__LiveSig(mode)

	# ------------------------------------------------------------------
	# Lifecycle
	# ------------------------------------------------------------------
	def Open(self, mode = MODE_EVOLVE):
		alreadyShown = self.IsShow()
		self.__Build(mode)
		if not alreadyShown:
			self.SetCenterPosition()   # keep the user's position on tab re-syncs
		self.SetTop()
		self.Show()

	def Refresh(self):
		# GC push landed. Rebuild ONLY when something the pages actually render
		# changed (type/pity/chance/caps/evolution) -- RefreshCompanionPetPage
		# also fires per pet EXP/point delta while farming, and a rebuild there
		# would cost ~50 widgets per kill AND snap the ladder scroll to top.
		if self.builtMode is None or not self.IsShow():
			return
		if self.__LiveSig(self.builtMode) == getattr(self, "liveSig", None):
			return
		self.__Build(self.builtMode)

	def Close(self):
		if self.itemTip:
			self.itemTip.HideToolTip()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
