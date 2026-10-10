# coding: latin_1
#
# Companion pet-page help popups (growth pet rework H2a/H2b) -- binder.
#
# Layout chrome lives in uiscript/pethelpwindow.py; the explanation itself is
# built here from ui.Table grids (the buffi-help pattern, uicompanionhelp.py).
#
# TWO MODES, one per "?" button on the Companion pet page (user design
# 2026-07-06: the general page and the leveling journey are separate popups):
#   MODE_GENERAL -> lifetime / feedstuff charge+revive / stat potions
#                   (the titlebar "?", pet page only)
#   MODE_EXP     -> the leveling journey level 1 -> max as ONE icon-led grid
#                   (the "?" beside the EXP section header). User feedback
#                   2026-07-06: bullets version was "too much words, too few
#                   icons" and the standalone Evolution->Type matrix confused
#                   even a system-literate reader -> stop rows now carry the
#                   LIVE evolution-material icon and the Types they open.
# Content rebuilds on every Open (live numbers); GC-push refreshes are
# SIGNATURE-GATED so per-kill pet EXP deltas never rebuild.
#
# Live single-sources (never drift from the server):
#   evolve levels     = interface.wndPetInfoWindow.GetEvolInfo (40/80/81)
#   item-EXP start /  = player.PET_UI_ITEM_EXP_START_LEVEL / PET_UI_MAX_LEVEL /
#   max level / age     PET_UI_LAST_EVOL_MIN_DAYS (GameType.h mirrors of the
#                       server enums in server/common/length.h)
#   Type gates        = player.GetPetTypeLadderRung (the GC201 ladder push)
#   lifetime cap      = player.GetPetLifeTime maxTime (when a pet is summoned)
#   current stat cap  = player.GetPetTypeInfo capPermille
#   stat potions      = uicompanion.PET_STAT_POTION_VNUMS (the pet page's
#                       clickable stat rows read the SAME table)
#
# Opened by interface.OpenPetHelp(mode) from the two "?" buttons.
import ui
import app
import item
import player
import localeinfo
import uitooltip
import uipetinfo
import uicompanion

# Mode indices (interface.OpenPetHelp passes them straight through).
MODE_GENERAL = 0
MODE_EXP     = 1

# ui.Table colour scheme: [lineColor, headerBg, rowBg, headerText, cellText] (0xAARRGGBB).
SCHEME = [0xff756657, 0xff281f1a, 0xff1a1615, 0xffcabdab, 0xffc7c7c7]


class PetHelpWindow(ui.ScriptWindow):

	WINDOW_WIDTH = 360
	M            = 12            # left/right page margin
	CONTENT_W    = WINDOW_WIDTH - 2 * M   # 336
	HEAD_H       = 22
	ROW_H        = 22
	GAP          = 8             # vertical gap between stacked tables
	STRIP_ROW    = 36            # potion strip / journey icon row height (icons + padding)
	POTION_CYCLE_SEC = 1.0       # stat-potion strip: seconds each size (S/M/L) stays shown
	# The pet page's own EXP-orb fill art: marks the battle/item-EXP journey rows.
	ORB_IMAGE    = "d:/ymir work/ui/game/companion/progress.png"

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
		self.itemTip   = None  # lazily-created item tooltip (potion hover)
		self.interface = None  # back-ref (set by interfacemodule) -> evolve-level single source
		self.builtMode = None  # which mode's content is currently built (None = nothing yet)
		self.liveSig   = None  # live-data signature of the built content (Refresh gate)
		# Stat-potion strip state (MODE_GENERAL only): each cell cycles S -> M -> L.
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
		pyScrLoader.LoadScriptFile(self, "uiscript/pethelpwindow.py")

		try:
			self.board = self.GetChild("board")
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
		except:
			import dbg
			dbg.TraceError("PetHelpWindow.__LoadWindow - bind failed")

	# ------------------------------------------------------------------
	# Table builders (the uipetupgradehelp.py helpers, no scroll region here)
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

	def __DrawGridOn(self, x, y, widths, rowHeights, headH):
		# Redraw the full grid (outer border + inner dividers) as ui.Bar ON TOP of the
		# table -- ui.Table's own Line dividers get covered by the later rows' opaque
		# background bars. headH=0 -> headerless.
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
		self.__DrawGridOn(self.M, y, w, [self.ROW_H] * len(data), self.HEAD_H)
		return y + tbl.GetHeight() + self.GAP

	def __AddJourney(self, headers, widths, rows, icons, y):
		# The leveling-journey grid: level column centred, "what happens" column
		# carries a LEADING ICON (ui.Table cell_icons: int = item vnum, str =
		# image path; icons are not_pick/decorative). Icon cells need a
		# horizontal align -- "right" doubles as the Arabic reading-edge anchor
		# (this engine's RTL text anchors at the given x and flows glyphs left).
		rtl = localeinfo.IsARABIC()
		h = list(headers)
		w = list(widths)
		if rtl:
			h.reverse()
			w.reverse()
		txtAlign = "horizontal:right" if rtl else "horizontal:left"
		tbl = ui.Table(sum(w), self.HEAD_H, SCHEME)
		tbl.SetParent(self)
		tbl.AddFlag("attach")
		tbl.set_columns(h, w)
		rowHs = []
		for ri in range(len(rows)):
			r = list(rows[ri])
			aligns = ["all:center", txtAlign]
			cicons = [None, icons[ri]]
			if rtl:
				r.reverse()
				aligns.reverse()
				cicons.reverse()
			rh = self.STRIP_ROW if icons[ri] else self.ROW_H
			tbl.add_row(r, rh, None, aligns, cicons, 28)
			rowHs.append(rh)
			if isinstance(icons[ri], (int, long)):
				self.__BindRowIcon(tbl._tchildren.get("row_%d_i%d" % (ri, 0 if rtl else 1)), icons[ri])
		tbl.Show()
		tbl.SetWindowHorizontalAlignLeft()
		tbl.SetPosition(self.M, y)
		self.tables.append(tbl)
		self.__DrawGridOn(self.M, y, w, rowHs, self.HEAD_H)
		return y + tbl.GetHeight() + self.GAP

	def __BindRowIcon(self, ico, vnum):
		# ui.Table builds its own cell icons decorative (not_pick); the journey's
		# evolution-material icons are REAL items, so they get the same hover
		# tooltip + wiki jump as every other item icon in the help popups.
		if not ico or not vnum:
			return
		ico.RemoveFlag("not_pick")
		ico.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OnOverItem, vnum)
		ico.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OnOverItemOut)
		if app.ENABLE_INGAME_WIKI:
			ico.SAFE_SetEvent(self.__OnClickItem, "mouse_click", vnum)

	def __OnOverItem(self, vnum):
		if not self.itemTip:
			self.itemTip = uitooltip.ItemToolTip()
		self.itemTip.ClearToolTip()
		self.itemTip.SetItemToolTip(vnum)
		if app.ENABLE_INGAME_WIKI:
			self.itemTip.DeclareShortcut(("key_lclick",), self.__L("HELP_TIP_WIKI", "- Left click to open Wiki |Eemoji/key_lclick|e"))
			self.itemTip.ShowToolTip()

	def __OnOverItemOut(self):
		if self.itemTip:
			self.itemTip.HideToolTip()

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
		self.__DrawGridOn(self.M, y, [self.CONTENT_W], [self.ROW_H] * len(lines), self.HEAD_H)
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
	# Stat-potion strip (MODE_GENERAL, pure visual): one bordered row with the
	# three stat potions; each cell cycles S -> M -> L. All size-class icons
	# are PRE-LOADED per cell and the cycle is Show/Hide only -- LoadImage at
	# runtime would debug-print "LOAD IMAGE" every swap (ImageBox.LoadImage
	# prints for any widget with events already bound) and reload the texture.
	# Vnums come from uicompanion.PET_STAT_POTION_VNUMS -- the SAME table the
	# pet page's clickable stat rows use, so shipping the real vnums there
	# updates this strip for free. (Same code as uipetupgradehelp's strip.)
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
		tbl.add_row([""] * n, self.STRIP_ROW, None, ["all:center"] * n, None)
		tbl.Show()
		tbl.SetWindowHorizontalAlignLeft()
		tbl.SetPosition(self.M, y)
		self.tables.append(tbl)
		self.__DrawGridOn(self.M, y, w, [self.STRIP_ROW], 0)
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
		return y + self.STRIP_ROW + self.GAP

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
		# outside MODE_GENERAL). Show/Hide swaps only -- never drop a widget
		# ref from inside OnUpdate (wndMgr teardown rule).
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

	def __ItemExpStartLevel(self):
		return getattr(player, "PET_UI_ITEM_EXP_START_LEVEL", 55)

	def __MaxLevel(self):
		return getattr(player, "PET_UI_MAX_LEVEL", 105)

	def __HeroMinDays(self):
		return getattr(player, "PET_UI_LAST_EVOL_MIN_DAYS", 1)

	def __GetTypeMax(self):
		if hasattr(player, "GetPetTypeInfo"):
			try:
				info = player.GetPetTypeInfo()
				if info[1]:
					return info[1]
			except:
				pass
		return 6

	def __CurCapPermille(self):
		# The summoned pet's CURRENT Type stat-cap; 0 when no pet / no data.
		if hasattr(player, "GetPetTypeInfo"):
			try:
				info = player.GetPetTypeInfo()
				if info[0]:
					return info[6]
			except:
				pass
		return 0

	def __LifetimeCapDays(self):
		# Max lifetime in whole days from the summoned pet's live gauge data;
		# 0 when no pet is summoned (the caller then skips the note).
		try:
			petID = player.GetActivePetItemId()
			if petID:
				(endTime, maxTime) = player.GetPetLifeTime(petID)
				if maxTime > 0:
					return maxTime / 86400
		except:
			pass
		return 0

	def __EvolveMatIcon(self, evol):
		# First material of the evolution stage (the SAME dict the evolve dialog
		# reads) -- the journey's stop rows show the item you will need there.
		# None when unknown -> that row renders as plain text.
		matsDict = getattr(uipetinfo, "EVOLVE_MATERIALS_DICT", None)
		if not matsDict or evol not in matsDict:
			return None
		for pair in matsDict[evol]:
			if pair[0]:
				return pair[0]
		return None

	def __EvolveTypeSpans(self):
		# {evolutionGate: "newly opened Types"} from the LIVE GC ladder push,
		# e.g. {1: "3-4", 2: "5", 3: "6"}: evolving at gate N (evo N -> N+1)
		# raises the Type ceiling from maxType(N) to maxType(N+1). Empty when
		# the ladder has not arrived (no pet / old build) -> rows show no
		# "opens Type" suffix instead of wrong zeros.
		if not hasattr(player, "GetPetTypeLadderRung"):
			return {}
		evoReq = {}
		for t in range(2, self.__GetTypeMax() + 1):
			rung = player.GetPetTypeLadderRung(t)
			if not rung[1]:      # chance 0 -> ladder not pushed yet
				return {}
			evoReq[t] = rung[2]
		if not evoReq:
			return {}
		def maxTypeAt(e):
			best = 1
			for t in evoReq:
				if evoReq[t] <= e and t > best:
					best = t
			return best
		spans = {}
		for e in range(1, max(evoReq.values())):
			lo = maxTypeAt(e) + 1
			hi = maxTypeAt(e + 1)
			if hi == lo:
				spans[e] = "%d" % lo
			elif hi > lo:
				spans[e] = "%d-%d" % (lo, hi)
		return spans

	def __JourneyRows(self):
		# The full leveling road as (rows, icons), every number live: evolution
		# stops from GetEvolInfo (their MATERIAL icon from the evolve dict, the
		# Types they open from the ladder push), the item-EXP start level / max
		# level / hero age from the PET_UI_* constants (server length.h mirrors).
		evo1 = self.__GetEvolRequiredLevel(1, 40)
		evo2 = self.__GetEvolRequiredLevel(2, 80)
		evo3 = self.__GetEvolRequiredLevel(3, 81)
		itemLv = self.__ItemExpStartLevel()
		maxLv  = self.__MaxLevel()
		spans = self.__EvolveTypeSpans()
		opensFmt  = self.__L("PET_HELP_EXP_ROW_OPENS_FMT", " - opens Type %s")
		evolveTxt = self.__L("PET_HELP_EXP_ROW_EVOLVE", "Evolve here")
		heroTxt   = self.__L("PET_HELP_EXP_ROW_HERO2_FMT", "Final evolution (%d+ days)") % self.__HeroMinDays()
		def stop(base, gate):
			s = spans.get(gate)
			if s:
				return base + (opensFmt % s)
			return base
		rows  = []
		icons = []
		rows.append(["1 - %d" % evo1, self.__L("PET_HELP_EXP_ROW_HUNT", "Hunt - battle EXP only")])
		icons.append(self.ORB_IMAGE)
		rows.append(["%d" % evo1, stop(evolveTxt, 1)])
		icons.append(self.__EvolveMatIcon(1))
		rows.append(["%d" % itemLv, self.__L("PET_HELP_EXP_ROW_ITEM3", "Optional: feed food/gear to level faster")])
		icons.append(self.ORB_IMAGE)
		rows.append(["%d" % evo2, stop(evolveTxt, 2)])
		icons.append(self.__EvolveMatIcon(2))
		rows.append(["%d" % evo3, stop(heroTxt, 3)])
		icons.append(self.__EvolveMatIcon(3))
		rows.append(["%d - %d" % (evo3, maxLv), self.__L("PET_HELP_EXP_ROW_TAIL", "EXP cost rises sharply per level")])
		icons.append(self.ORB_IMAGE)
		rows.append(["%d" % maxLv, self.__L("PET_HELP_EXP_ROW_MAX", "Maximum level")])
		icons.append(None)
		return (rows, icons)

	# ------------------------------------------------------------------
	# Build (always rebuilds -- the pages carry live numbers; Refresh gates
	# on __LiveSig so only RELEVANT changes trigger it)
	# ------------------------------------------------------------------
	def __LiveSig(self, mode):
		# Everything live the pages render: Type info (current cap / typeMax /
		# ladder identity), the pet identity + evolution level, the lifetime
		# cap. Pet EXP/lifetime COUNTDOWN deltas do NOT enter the signature,
		# so per-kill / per-second pushes are no-ops.
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
				sig += (self.__LifetimeCapDays(),)
		except:
			pass
		return sig

	def __Build(self, mode):
		if not self.board:
			return
		# Tear down the previous content: dropping the refs GC-destroys the widgets
		# (safe here -- called from Open/Refresh, never from a child's dispatch).
		if self.itemTip:
			self.itemTip.HideToolTip()   # a hovered icon dies with the rebuild
		self.tables = []
		self.icons  = []
		self.potionIcons     = []
		self.potionHover     = None
		self.potionCycleIdx  = 0
		self.potionNextCycle = 0
		self.builtMode = mode
		y = 32   # below the titlebar

		if mode == MODE_EXP:
			# ===== EXP JOURNEY help (the "?" beside the EXP header) =====
			# ONE icon-led grid + two thin notes (user feedback 2026-07-06: the
			# bullets version was word-heavy and the standalone Evolution->Type
			# matrix was confusing -> unlocks now read inline on the stop rows).
			self.board.SetTitleName(self.__L("PET_HELP_TITLE_EXP", "Pet EXP - Help"))
			headers = [
				self.__L("PET_HELP_EXP_COL_LEVEL", "Pet Lv."),
				self.__L("PET_HELP_EXP_COL_WHAT",  "What happens"),
			]
			(rows, icons) = self.__JourneyRows()
			# 58px fits the widest level cell ("81 - 105"); every spare pixel goes
			# to the text column -- the longest row ("Final evolution (1+ days) -
			# opens Type 6") is within ~15px of its budget (audit 2026-07-06).
			y = self.__AddJourney(headers, [58, 278], rows, icons, y)
			y = self.__AddNote(self.__L("PET_HELP_EXP_OWNER", "The pet never levels above YOUR level."), y)
			y = self.__AddNote(self.__L("PET_HELP_EXP_TYPES_NOTE", "Costs & chances: the ? in the Upgrade window."), y)
		else:
			# ===== GENERAL help (the pet page titlebar "?") =====
			self.board.SetTitleName(self.__L("PET_HELP_TITLE_GEN", "Companion Pet - Help"))
			lines = [
				self.__L("PET_HELP_GEN_LIFE",  "Your pet has a lifetime - at zero it dies."),
				self.__L("PET_HELP_GEN_FEED",  "Feedstuff items add days and revive a dead pet."),
				self.__L("PET_HELP_GEN_LEVEL", "It levels by hunting - never above your level."),
			]
			y = self.__AddBullets(self.__L("PET_HELP_GEN_TITLE", "Your Companion"), lines, y)
			capDays = self.__LifetimeCapDays()
			if capDays > 0:
				y = self.__AddNote(self.__L("PET_HELP_GEN_LIFECAP_FMT", "Lifetime cap: %d days") % capDays, y)
			# Stat potions: the cycling S/M/L strip + how the two ceilings work.
			y = self.__AddTitle(self.__L("PET_HELP_GEN_POTIONS_TITLE", "Stat Potions"), y)
			y = self.__AddPotionRow(y)
			lines = [
				self.__L("PET_HELP_GEN_POT_STEP",  "Each potion boosts one stat - guaranteed, no fail."),
				self.__L("PET_HELP_GEN_POT_SIZES", "S / M / L only differ in how HIGH they can push."),
				self.__L("PET_HELP_GEN_POT_CAP",   "The pet's Type sets the real cap - upgrade it."),
				self.__L("PET_HELP_GEN_POT_USE",   "Click a stat row on the pet page to use them."),
			]
			y = self.__AddBullets(self.__L("PET_HELP_GEN_POT_TITLE", "How they work"), lines, y)
			cap = self.__CurCapPermille()
			if cap > 0:
				y = self.__AddNote(self.__L("PET_HELP_GEN_CURCAP_FMT", "Your pet's current stat cap: %.1f%%") % (cap / 10.0), y)

		# Fit the board to the generated content.
		total = y + 4
		self.board.SetSize(self.WINDOW_WIDTH, total)
		self.SetSize(self.WINDOW_WIDTH, total)
		self.liveSig = self.__LiveSig(mode)

	# ------------------------------------------------------------------
	# Lifecycle
	# ------------------------------------------------------------------
	def Open(self, mode = MODE_GENERAL):
		alreadyShown = self.IsShow()
		self.__Build(mode)
		if not alreadyShown:
			self.SetCenterPosition()   # keep the user's position on re-targets
		self.SetTop()
		self.Show()

	def Refresh(self):
		# GC push landed. Rebuild ONLY when something the pages actually render
		# changed (type/caps/evolution/pet identity) -- RefreshCompanionPetPage
		# also fires per pet EXP/point delta while farming.
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
