# coding: latin_1
#
# Wiki redesign -- Phase 1 (skeleton).
#
# Landscape Wikipedia-style layout. Gated by app.ENABLE_WIKI_REDESIGN.
# ingamewiki.py branches to this module's InitMainWindow/BuildBaseMain when
# the flag is on; otherwise the legacy portrait wiki in ingamewikiui.py keeps
# running unchanged. Nothing in this file ever touches legacy windows.
#
# What Phase 1 builds:
#   - 794x477 background board (wiki_new/bg.png)
#   - movable title bar with close button + "Wikipedia" header label
#   - search field (with X-clear button, magnifier button, ghost-text hint)
#   - "Exact Search" checkbox
#   - prev/next navigation arrows
#   - empty content area placeholder
#
# What Phase 1 does NOT build (intentionally deferred):
#   - the collapsible category sidebar (Phase 2)
#   - any item / monster / chest / craft / shop sub-page (Phase 3+)
#   - the inline search dropdown wiring (kept legacy class; new positions only)
#
# Page-window attributes that InGameWiki touches (mainWeaponWindow, categ, ...)
# are set to _RedesignStub no-op objects so legacy plumbing in ingamewiki.py
# (CloseBaseWindows, GoToLanding, OpenSpecialWikiPage) cannot crash during the
# Phase 1 window. They get replaced with real widgets in later phases.

import app
import ui
import wndMgr
import wiki
import localeinfo
import item
import ingamewikiconfig
import ingamewikisearch
import ingamewikiui as _legacyWiki
import nonplayer
import types
import grp
import ingamewikireverse as _legacyReverse
import ingamewikidungeon
import ingamewikibiolog
import ingamewikidragonsoul
import ingamewikigrowthpet
import ingamewikigrowthmount
import ingamewikigemshop
import ingamewikibuffi


# ---------------------------------------------------------------------------
# Redesign restyle hooks for the legacy panel classes.
#
# The wiki redesign is a PURE RESTYLE -- behavior, data fetch, scroll and
# refine plumbing all stay in the legacy ingamewikiui.WikiMain*Window
# classes. We only swap the few visual constants those classes consult:
#
#   - WikiBuildGrid.LoadGrid          : backdrop image per refine-mat count
#   - WikiMainWeaponWindow.WikiItem   : ROW_START_Y so the yang row sits at
#                                       the top of each refine column
#                                       (matches the new detail_item.png art)
#   - WikiMainWeaponWindow.WikiItem   : hide goldText / upgradeText -- those
#                                       labels are pre-drawn in the new
#                                       backdrop, so the runtime labels
#                                       would be duplicates.
#
# All patches are gated on app.ENABLE_WIKI_REDESIGN so the legacy wiki path
# stays byte-identical when the flag is off.
# ---------------------------------------------------------------------------
if app.ENABLE_WIKI_REDESIGN:
	_NEW_GRID_DIR = "d:/ymir work/ui/wiki/wiki_new/grid/"

	def _LoadGridRedesign(self, size):
		# Map "size" (= number of material rows the legacy code wants to
		# draw) to one of the four new backdrop variants. Anything beyond
		# 5 mats falls back to detail_item_5.png; we don't ship taller art.
		self.CleanOldGrid()
		if size <= 2:
			grid_image = _NEW_GRID_DIR + "detail_item.png"      # 541x149
		elif size == 3:
			grid_image = _NEW_GRID_DIR + "detail_item_3.png"    # 545x194
		elif size == 4:
			grid_image = _NEW_GRID_DIR + "detail_item_4.png"    # 545x234
		else:
			grid_image = _NEW_GRID_DIR + "detail_item_5.png"    # 545x277

		grid_element = ui.ExpandedImageBox()
		grid_element.SetParent(self.backgroundParent)
		grid_element.AddFlag("attach")
		grid_element.AddFlag("not_pick")
		grid_element.LoadImage(grid_image)
		grid_element.SetPosition(0, 0)
		grid_element.Show()
		self.grid_elements.append(grid_element)
		self.SetBackgroundGridSize((self.GRID_WIDTH, grid_element.GetHeight()))

	_legacyWiki.WikiBuildGrid.IMAGES_PATH = _NEW_GRID_DIR
	_legacyWiki.WikiBuildGrid.LoadGrid    = _LoadGridRedesign

	# Per-size row Y layout. Each detail_item_*.png backdrop has its slot
	# rows drawn at backdrop-specific Y positions, so a single shared
	# ROW_START_Y can't satisfy every size. Tune the entries below to
	# match each backdrop's drawn cells -- updates here propagate
	# automatically to ROW_START_Y (size 2) and ROW_HEIGHTS_EXPANDED
	# (sizes 3..N).
	#
	# Format per size:
	#   {
	#     'header_y': col-local Y of the +N header strip,
	#     'yang_y':   col-local Y of the yang/cost row,
	#     'mat_ys':   list of col-local Y for each material row,
	#   }
	# Legacy heights are kept (header=21, mat0=44, mat_mid=47, mat_last=42,
	# yang=22) so the icon center math (start_y + h/2 - icon_h/2) stays
	# byte-identical to the legacy formula. Only the start Y values
	# change per backdrop.
	# Initial values measured from each detail_item_*.png backdrop's
	# dark cell positions (brightness scan at X=155 in the +0 column).
	# Cell tops at base Y=72, 113, 154, 195, 236 -> col-local 51, 92,
	# 133, 174, 215 (column window sits at base Y=21). useStart is
	# back-solved so the legacy icon formula
	#     icon_top = useStart + useHeight / 2 - 16
	# centers a 32 px icon in each cell; the legacy useHeights vary
	# per slot (mat0=44, mid mats=47, last mat=42), so the useStart
	# values shift slightly per size to compensate.
	# mat_x_deltas is an OPTIONAL per-row X nudge added to the legacy
	# col-local X=5. Each entry shifts that material row's icons left
	# (-) or right (+) by that many px in EVERY refine column. Sizes
	# without a mat_x_deltas key keep the legacy X=5 unchanged.
	_REDESIGN_ROW_LAYOUT = {
		2: {'header_y': 0, 'yang_y': 21,
			'mat_ys': [44, 84],
			'mat_x_deltas': [-2, -2]},
		3: {'header_y': 0, 'yang_y': 21,
			'mat_ys': [44, 84, 127],
			'mat_x_deltas': [0, -2, -2]},
		4: {'header_y': 0, 'yang_y': 21, 'mat_ys': [44, 84, 125, 168]},
		5: {'header_y': 0, 'yang_y': 21, 'mat_ys': [44, 84, 125, 166, 209]},
	}

	# Apply size=2 directly to ROW_START_Y (the legacy default arrays
	# used when materialCount <= STARTING_MAT_COUNT).
	_l2 = _REDESIGN_ROW_LAYOUT[2]
	_legacyWiki.WikiMainWeaponWindow.WikiItem.ROW_START_Y = [
		_l2['header_y'],    # index 0: header
		_l2['mat_ys'][0],   # index 1: mat0
		_l2['mat_ys'][1],   # index 2: mat1
		_l2['yang_y'],      # index 3: yang (= STARTING_MAT_COUNT+1)
	]

	# Build ROW_HEIGHTS_EXPANDED (sizes 3..N) from the per-size layout.
	# The dict format the legacy reads is
	#   expanded[size] = (heights, starts)
	# where index 0 = header, 1..size = mats, size+1 = yang/money.
	def _BuildYangTopExpanded():
		expanded = {}
		starting = _legacyWiki.WikiMainWeaponWindow.WikiItem.STARTING_MAT_COUNT
		for idx in range(starting + 1, wiki.REFINE_MATERIAL_MAX_NUM + 1):
			# Reproduce the legacy heights array for this material count:
			# base [21, 44, 42, 22] with 47 inserted at pos (2+i) per
			# extra material beyond STARTING_MAT_COUNT.
			heights = [21, 44, 42, 22]
			for inserts in xrange(idx - starting):
				heights.insert((2 + inserts), 47)
			# Pull this size's tuned Y values from _REDESIGN_ROW_LAYOUT,
			# falling back to the largest authored size for any size we
			# don't have explicit numbers for.
			layout = _REDESIGN_ROW_LAYOUT.get(idx)
			if layout is None:
				layout = _REDESIGN_ROW_LAYOUT[max(_REDESIGN_ROW_LAYOUT.keys())]
			yang_idx = idx + 1
			starts = [0] * len(heights)
			starts[0]        = layout['header_y']
			starts[yang_idx] = layout['yang_y']
			for m in xrange(idx):
				# Fall back to last authored mat Y if this size has more
				# mat rows than the layout entry covers.
				if m < len(layout['mat_ys']):
					starts[1 + m] = layout['mat_ys'][m]
				else:
					starts[1 + m] = layout['mat_ys'][-1]
			expanded[idx] = (heights, starts)
		return expanded

	_legacyWiki.WikiMainWeaponWindow.WikiItem.ROW_HEIGHTS_EXPANDED = _BuildYangTopExpanded()

	# The yang-on-top reorder also breaks SetExpandedRow's column-height
	# calculation:
	#     tmp.SetSize(tmp.GetWidth(), useStart[-1] - 2 + useHeight[-1])
	# That formula assumes useStart is monotonic and useStart[-1] is the
	# bottom -- true for legacy yang-at-bottom, false for us. Replace the
	# whole SetExpandedRow with a redesign-aware version that:
	#   - computes column height as max(start + height) over all rows
	#   - skips the legacy goldText repositioning (we hide goldText below)
	#   - keeps every other piece of legacy behavior identical
	def _SetExpandedRowRedesign(self, materialCount):
		(useHeight, useStart) = self.ROW_HEIGHTS_EXPANDED[materialCount]
		oldSize = self.base.GetHeight()

		self.base.SetGridSize(materialCount)
		self.SetSize(self.base.GetWidth(), self.base.GetHeight())

		# Correct col height: max bottom across all rows. With yang on top
		# the last index no longer has the largest Y.
		col_height = 0
		for i in xrange(len(useStart)):
			bottom = useStart[i] + useHeight[i]
			if bottom > col_height:
				col_height = bottom

		for tmp in self.cols:
			tmp.SetSize(tmp.GetWidth(), col_height)

			tmp.refineMat = []
			tmp.refineMatText = []
			tmp.refineMatNum = []

			for j in xrange(materialCount):
				tmp.refineMat.append(ui.ExpandedImageBox())
				tmp.refineMat[j].SetParent(tmp)
				tmp.refineMat[j].Show()

				tmp.refineMatNum.append(ui.NumberLine())
				tmp.refineMatNum[j].SetParent(tmp)
				tmp.refineMatNum[j].SetHorizontalAlignRight()
				tmp.refineMatNum[j].Hide()

				tmp.refineMatText.append(ui.TextLine())
				tmp.refineMatText[j].SetParent(tmp)
				tmp.refineMatText[j].SetText("-")
				tmp.refineMatText[j].SetPosition(
					tmp.GetWidth() / 2 - tmp.refineMatText[j].GetTextSize()[0] / 2,
					useStart[j + 1] + useHeight[j + 1] / 2
						- tmp.refineMatText[j].GetTextSize()[1] / 2 - 1)
				tmp.refineMatText[j].Show()

			tmp.moneyText = ui.TextLine()
			tmp.moneyText.SetParent(tmp)
			tmp.moneyText.SetText("-")
			tmp.moneyText.SetPosition( 
			tmp.GetWidth() / 2 - tmp.moneyText.GetTextSize()[0] / 2,
				useStart[(materialCount + 1)] + useHeight[(materialCount + 1)] / 2
					- tmp.moneyText.GetTextSize()[1] / 2 + 8)
			tmp.moneyText.Show()

		# Skip self.goldText.SetPosition -- we Hide() it in the init wrapper
		# so its Y doesn't matter.
		self.itemImage.SetPosition(
			1 + 47 / 2 - self.itemImage.GetWidth() / 2,
			10 + (self.base.GetHeight() / 2) - (self.itemImage.GetHeight() / 2))

		if self.parent:
			self.parent.ChangeElementSize(self, self.base.GetHeight() - oldSize)

	_legacyWiki.WikiMainWeaponWindow.WikiItem.SetExpandedRow = _SetExpandedRowRedesign

	# Swap class-filter button art to the redesign's larger 128x44 set
	# under wiki_new/class_buttons/. The legacy uses ~24 px tall buttons
	# under d:/ymir work/ui/wiki/; the redesign ones are taller, so the
	# peekWindow Y in _AttachLegacyStubs also pushes the refine list down.
	_NEW_CB_PATH = "d:/ymir work/ui/wiki/wiki_new/class_buttons/"
	_legacyWiki.WikiMainWeaponWindow.CLASS_BUTTONS = [
		[item.ITEM_ANTIFLAG_WARRIOR,
			_NEW_CB_PATH + "class_w_normal.png",
			_NEW_CB_PATH + "class_w_hover.png",
			_NEW_CB_PATH + "class_w_selected.png"],
		[item.ITEM_ANTIFLAG_ASSASSIN,
			_NEW_CB_PATH + "class_n_normal.png",
			_NEW_CB_PATH + "class_n_hover.png",
			_NEW_CB_PATH + "class_n_selected.png"],
		[item.ITEM_ANTIFLAG_SHAMAN,
			_NEW_CB_PATH + "class_s_normal.png",
			_NEW_CB_PATH + "class_s_hover.png",
			_NEW_CB_PATH + "class_s_selected.png"],
		[item.ITEM_ANTIFLAG_SURA,
			_NEW_CB_PATH + "class_su_normal.png",
			_NEW_CB_PATH + "class_su_hover.png",
			_NEW_CB_PATH + "class_su_selected.png"],
	]

	# Only the "Yang Costs" runtime label is hidden -- the new backdrop has
	# its own yang strip drawn at the top. The "Upgrade Costs" / "Item
	# Level" label (upgradeText) STAYS visible because the new layout
	# expects it as the row label above the +N column headers.
	def _HideCol0Dashes(wikiItem):
		# cols[0] is the unused "+0" column -- ProcessRetInfo only fills
		# cols[1..MAX_REFINE_COUNT], so its placeholder "-" entries for
		# moneyText and refineMatText[j] are never replaced with real
		# data. They render as a vertical strip of dashes left of the
		# +1 column. The redesign hides them entirely; the "+0" header
		# label (refineText on titleWnd) stays visible.
		if not getattr(wikiItem, 'cols', None):
			return
		c0 = wikiItem.cols[0]
		money = getattr(c0, 'moneyText', None)
		if money is not None:
			money.Hide()
		texts = getattr(c0, 'refineMatText', None)
		if texts:
			for t in texts:
				t.Hide()

	# yang.png replaces the hidden "-" placeholder in cols[0]'s yang
	# slot. Native size is 60x42 -- the cell is ~40 wide, so the icon
	# overflows a little to the sides but reads as a small gold coin
	# stamp centered on the yang row.
	_YANG_ICON_PATH = "d:/ymir work/ui/wiki/wiki_new/yang.png"

	def _AddCol0YangIcon(wikiItem):
		if not getattr(wikiItem, 'cols', None):
			return
		c0 = wikiItem.cols[0]
		if getattr(c0, '_yangIconAdded', False):
			return
		icon = ui.ImageBox()
		icon.SetParent(c0)
		icon.AddFlag("not_pick")
		try:
			icon.LoadImage(_YANG_ICON_PATH)
		except Exception:
			return
		# Center on the yang row. _REDESIGN_ROW_LAYOUT['yang_y'] is the
		# col-local Y of the yang row top; place the icon vertically
		# centered around the middle of that row's drawn cell.
		# Tuning log: +10 down 2026-06-21 ("its way up").
		yang_y = _REDESIGN_ROW_LAYOUT[2]['yang_y']
		icon_w, icon_h = icon.GetWidth(), icon.GetHeight()
		col_w = c0.GetWidth()
		icon.SetPosition((col_w - icon_w) // 2, yang_y - (icon_h // 2) + 14)
		icon.Show()
		c0._yangIcon = icon
		c0._yangIconAdded = True

	# Text styling: OUTLINE on every visible text in the card so it
	# reads against the busy backdrop, plus a warm gold tint on the
	# moneyText (yang values) per the design spec.
	_YANG_TEXT_COLOR = 0xFFFAD390   # legacy levelText warm gold

	def _ApplyTextStyling(wikiItem):
		# Per-column texts.
		for col in getattr(wikiItem, 'cols', []):
			rt = getattr(col, 'refineText', None)
			if rt is not None:
				rt.SetOutline()
			mt = getattr(col, 'moneyText', None)
			if mt is not None:
				mt.SetOutline()
				mt.SetPackedFontColor(_YANG_TEXT_COLOR)
			mtxts = getattr(col, 'refineMatText', None)
			if mtxts:
				for t in mtxts:
					t.SetOutline()
		# Top-of-card labels.
		for attr in ('itemNameText', 'levelText', 'upgradeText'):
			t = getattr(wikiItem, attr, None)
			if t is not None:
				t.SetOutline()

	_origWikiItemInit = _legacyWiki.WikiMainWeaponWindow.WikiItem.__init__

	def _WikiItemInitRedesign(self, vnum, parent, allow_special_page=True, isUpgradable=True):
		_origWikiItemInit(self, vnum, parent, allow_special_page, isUpgradable)
		if hasattr(self, "goldText"):
			self.goldText.Hide()
		_HideCol0Dashes(self)
		_AddCol0YangIcon(self)
		_ApplyTextStyling(self)

	_legacyWiki.WikiMainWeaponWindow.WikiItem.__init__ = _WikiItemInitRedesign

	# Per-row X nudges -- applied AFTER the legacy NoticeMe pipeline
	# positions every material icon. ProcessRetInfo hardcodes the
	# material X at col-local 5; this wrapper walks cols[1..MAX] once
	# the data is in and adds _REDESIGN_ROW_LAYOUT[size]['mat_x_deltas']
	# to each row's X. The "-" placeholder text is centered by the
	# legacy code and intentionally left alone.
	_origWikiItemNoticeMe = _legacyWiki.WikiMainWeaponWindow.WikiItem.NoticeMe

	def _WikiItemNoticeMeRedesign(self, noticeType=[False, 0]):
		_origWikiItemNoticeMe(self, noticeType)
		# SetExpandedRow recreates cols[0]'s placeholder "-" entries
		# when materialCount > STARTING_MAT_COUNT -- rehide them, make
		# sure the yang icon survives, and re-apply outline/gold on the
		# freshly-created moneyText / refineMatText widgets.
		_HideCol0Dashes(self)
		_AddCol0YangIcon(self)
		_ApplyTextStyling(self)
		try:
			# Material count == len of the per-cell refineMat list on
			# any populated refine column (cols[1] is always populated
			# when retInfo arrived; cols[0] is the unused +0 column).
			if len(self.cols) < 2 or not hasattr(self.cols[1], 'refineMat'):
				return
			size = len(self.cols[1].refineMat)
			layout = _REDESIGN_ROW_LAYOUT.get(size)
			if layout is None or 'mat_x_deltas' not in layout:
				return
			deltas = layout['mat_x_deltas']
			for col in self.cols[1:]:
				mats = getattr(col, 'refineMat', None)
				if not mats:
					continue
				for j, mat in enumerate(mats):
					if j >= len(deltas):
						break
					if deltas[j] == 0:
						continue
					px, py = mat.GetLocalPosition()
					mat.SetPosition(px + deltas[j], py)
		except Exception:
			import traceback, dbg
			dbg.TraceError(
				"wiki redesign mat-X post-shift:\n" + traceback.format_exc())

	_legacyWiki.WikiMainWeaponWindow.WikiItem.NoticeMe = _WikiItemNoticeMeRedesign

	# SpecialPageWindow backdrop swap. The legacy loads
	#   d:/ymir work/ui/wiki/detail_monster_new.png          (isMonster=True)
	#   d:/ymir work/ui/wiki/detail_monster.png              (isMonster=False)
	#   d:/ymir work/ui/wiki/detail_itemnocontent2.png       (no-content items)
	# Redirect each to its wiki_new/ counterpart so the redesign art is
	# used. Chest special pages reuse the item backdrop (same 553x354
	# slot layout: modelView icon + originInfo "drops from" panel +
	# bonusInfo content area) -- the wiki_new/detail_chest.png file is
	# the per-card list backdrop (541x89), NOT a full-page backdrop,
	# and using it here would only paint the top-left and leave the
	# rest of the page empty.
	_DETAIL_ITEM_PATH       = "d:/ymir work/ui/wiki/wiki_new/detail_item.png"
	_DETAIL_MONSTER_PATH    = "d:/ymir work/ui/wiki/wiki_new/detail_monster_new.png"
	_DETAIL_NOCONTENT_PATH  = "d:/ymir work/ui/wiki/wiki_new/detail_itemnocontent2.png"

	_origSpecPageInit = _legacyWiki.SpecialPageWindow.__init__

	def _SpecialPageInitRedesign(self, vnum, isMonster):
		_origSpecPageInit(self, vnum, isMonster)
		# The legacy __init__ has now set self.isNoContent / isUpgradable
		# / isChest. Pick the matching redesign backdrop and swap.
		try:
			if getattr(self, 'isNoContent', False):
				new_bg = _DETAIL_NOCONTENT_PATH
			elif isMonster:
				new_bg = _DETAIL_MONSTER_PATH
			else:
				# Items AND chests: same backdrop. Legacy SpecialPage
				# layout for chests parallels items (icon + drops-from
				# + bonusInfo holding the chest contents card).
				new_bg = _DETAIL_ITEM_PATH
			self.bg.UnloadImage()
			self.bg.LoadImage(new_bg)
			self.SetSize(self.bg.GetWidth(), self.bg.GetHeight())
		except Exception:
			import traceback, dbg
			dbg.TraceError(
				"wiki redesign SpecialPageWindow bg swap:\n"
				+ traceback.format_exc())

		# Reposition reverse-lookup panels (no-content item page) using
		# _REVERSE_PANEL_POSITIONS above. Legacy SpecialPageWindow set
		# them at (0,173), (185,173), (370,173); we overwrite here so
		# tuning lives in the redesign module instead of legacy.
		try:
			panels = getattr(self, 'reverseLookupPanels', None) or []
			for i, p in enumerate(panels):
				if i < len(_REVERSE_PANEL_POSITIONS):
					px, py = _REVERSE_PANEL_POSITIONS[i]
					p.SetPosition(px, py)
		except Exception:
			import traceback, dbg
			dbg.TraceError(
				"wiki redesign reverse-lookup reposition:\n"
				+ traceback.format_exc())

		# Refine card clip fix. SpecialPageWindow.__init__ sets a
		# primary clip on bonusScrollBoard at line 5468, but legacy
		# inits the clip when bonusPeekWindow is still 0x0 (size
		# happens later at line 5485) so the engine never gets a real
		# clip rect. Then WikiItem.SetExpandedRow grows bonusInfo to
		# its full expanded size (e.g. 234 px) while peekWindow stays
		# at the small initial size, and bonusInfo renders past the
		# wiki bg.
		#
		# Fix: cap bonusPeekWindow to the room left in the bg, then
		# re-establish the clip mask on both bonusScrollBoard and
		# bonusInfo using sub-clip (the codebase-blessed pattern --
		# see WikiItemOriginInfo line 4045-4051: primary clip here
		# blocks the wiki outer primary propagation, sub-clip stacks
		# on top of it). Sub-clip on bonusInfo because primary clip
		# on the scrollBoard does not cascade to its children in
		# this engine.
		try:
			bpw = getattr(self, 'bonusPeekWindow', None)
			bsb = getattr(self, 'bonusScrollBoard', None)
			bi  = getattr(self, 'bonusInfo',        None)
			if bpw and getattr(self, 'bg', None):
				local_y = bpw.GetLocalPosition()[1]
				bg_h    = self.bg.GetHeight()
				avail_h = bg_h - local_y - _BONUS_PEEK_BOTTOM_MARGIN
				if avail_h > 0:
					bpw.SetSize(bpw.GetWidth(), avail_h)
					if app.USE_CLIP_MASK:
						if bsb:
							try:
								bsb.SetSubClippingMaskWindow(bpw)
							except Exception:
								pass
						if bi:
							try:
								bi.SetSubClippingMaskWindow(bpw)
							except Exception:
								pass
		except Exception:
			import traceback, dbg
			dbg.TraceError(
				"wiki redesign bonusPeekWindow cap:\n"
				+ traceback.format_exc())


	_legacyWiki.SpecialPageWindow.__init__ = _SpecialPageInitRedesign

	# The legacy ingamewikiui reuses ONE "detail_chest.png" 541x89 card
	# backdrop for every list-view entry:
	#   - WikiMainChestWindow.WikiItem        (chests)
	#   - WikiMainBossWindow.WikiItem         (bosses + monsters + stones,
	#                                          all routed through this class
	#                                          via mob-type Show args)
	# Swap them all to the wiki_new variant in one shot. detail_chest2.png
	# (used when fromSpecialPage=True on the chest WikiItem, line 2024)
	# has no wiki_new equivalent so it's left alone.
	_NEW_DETAIL_CHEST_CARD = "d:/ymir work/ui/wiki/wiki_new/detail_chest.png"

	_origChestWikiItemInit = _legacyWiki.WikiMainChestWindow.WikiItem.__init__
	def _ChestWikiItemInitRedesign(self, vnum, parent, fromSpecialPage=False):
		_origChestWikiItemInit(self, vnum, parent, fromSpecialPage)
		if app.USE_EXTENDED_WIKI and fromSpecialPage:
			return
		try:
			self.base.UnloadImage()
			self.base.LoadImage(_NEW_DETAIL_CHEST_CARD)
		except Exception:
			import traceback, dbg
			dbg.TraceError(
				"wiki redesign Chest WikiItem bg swap:\n"
				+ traceback.format_exc())
	_legacyWiki.WikiMainChestWindow.WikiItem.__init__ = _ChestWikiItemInitRedesign

	_origBossWikiItemInit = _legacyWiki.WikiMainBossWindow.WikiItem.__init__
	def _BossWikiItemInitRedesign(self, vnum, parent):
		_origBossWikiItemInit(self, vnum, parent)
		try:
			self.base.UnloadImage()
			self.base.LoadImage(_NEW_DETAIL_CHEST_CARD)
		except Exception:
			import traceback, dbg
			dbg.TraceError(
				"wiki redesign Boss WikiItem bg swap:\n"
				+ traceback.format_exc())
	_legacyWiki.WikiMainBossWindow.WikiItem.__init__ = _BossWikiItemInitRedesign

	# WikiMainBossWindow.Show(mobtypes, fromlvl, tolvl) -- accept a
	# manual vnum list as a single arg too. The metin-stone sub-cats
	# (Field Low/Med/High, Chaos, Event) pass tuples of (vnums_list,)
	# instead of (mobtype, fromlvl, tolvl). When the redesigned Show
	# detects that shape it bypasses wiki.LoadClassMobs entirely and
	# feeds each vnum through AddItem directly, so the lists in
	# ingamewikiconfig.STONE_*_VNUMS are authoritative -- no engine
	# filtering interferes.
	# IMPORTANT: explicit positional args (NOT *args). ui.__mem_func__
	# inspects mfunc.im_func.func_code.co_argcount > 1 (ui.py:159) to
	# decide whether to forward call args or drop them. *args is
	# varargs and doesn't count toward co_argcount, so a signature of
	# (self, *args) collapses to co_argcount=1 and __mem_func__ wraps
	# us in __noarg_call__ -- every apply(clickEvent, ...) silently
	# dropped its args, _BossShowRedesign got self only, the legacy
	# fallback path got `_origBossShow(self)` and crashed with
	# "Show() takes exactly 4 arguments (1 given)".
	_origBossShow = _legacyWiki.WikiMainBossWindow.Show
	def _BossShowRedesign(self, a=None, b=None, c=None):
		# Manual vnum-list form: a=list/tuple, b and c left as default.
		# Used by the metin-stone sub-cats. Anything else falls through
		# to the legacy 3-arg (mobtypes, fromlvl, tolvl) signature.
		if isinstance(a, (list, tuple)) and b is None and c is None:
			vnums = list(a)
			wndMgr.Show(self.hWnd)
			marker = ("__manual__", tuple(vnums))
			cur_marker = (getattr(self, "mobtypes", None),
			              getattr(self, "fromlvl",  None))
			if marker == cur_marker:
				return
			self.mobtypes = marker[0]
			self.fromlvl  = marker[1]
			self.tolvl    = None
			del self.elements[:]
			if self.scrollBoard:
				self.scrollBoard.SetSize(0, 0)
			self.UpdateScrollbar()
			self.loadFrom = 0
			self.loadTo   = 0
			self.isOpened = True
			# Flatten one level so STONE_*_VNUMS can mix bare vnums with
			# range(...) entries the way ALT_CHEST_VNUMS does -- matches
			# WikiMainChestWindow.OnUpdate's flatten at
			# ingamewikiui.py:2360-2364.
			for entry in vnums:
				if isinstance(entry, (list, tuple)):
					for v in entry:
						try:
							self.AddItem(int(v))
						except Exception:
							import traceback, dbg
							dbg.TraceError(
								"wiki redesign manual Boss AddItem inner vnum=%s:\n%s"
								% (v, traceback.format_exc()))
				else:
					try:
						self.AddItem(int(entry))
					except Exception:
						import traceback, dbg
						dbg.TraceError(
							"wiki redesign manual Boss AddItem vnum=%s:\n%s"
							% (entry, traceback.format_exc()))
			return
		# Legacy path -- forward whatever the caller actually passed.
		return _origBossShow(self, a, b, c)
	_legacyWiki.WikiMainBossWindow.Show = _BossShowRedesign

	# Sort direction: legacy AddItem (ingamewikiui.py:2735-2772) sorts
	# entries descending by vnum (insert before the first SMALLER vnum)
	# so bosses / monsters / stones all render high-tier first. Flip to
	# ascending so low-vnum (typically low-tier) entries lead the list.
	def _BossAddItemAscending(self, vnum):
		for i in self.elements:
			if vnum == i.vnum:
				return None

		tmp = self.WikiItem(vnum, self)
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")

		addPadding = 0
		totalElem = len(self.elements)

		if totalElem > 0:
			lastIndex = 0
			for i in xrange(totalElem):
				# CHANGED vs legacy: > instead of < -- insert BEFORE
				# the first element with a HIGHER vnum, so the list
				# ends up sorted ascending.
				if self.elements[i].vnum > tmp.vnum:
					break
				lastIndex += 1

			self.elements.insert(lastIndex, tmp)
			totalElem += 1

			for i in xrange(lastIndex, totalElem):
				self.elements[i].SetPosition(0,
					(0 if i == 0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))

			addPadding = self.ELEM_PADDING
		else:
			self.elements.append(tmp)

		tmp.Show()

		self.scrollBoard.SetSize(tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.UpdateScrollbar()

		return tmp
	_legacyWiki.WikiMainBossWindow.AddItem = _BossAddItemAscending

	# WikiMainCostumeWindow.WikiItem (the per-item card in costume,
	# mount, shining and item-shop lists -- WikiMainShopItemWindow
	# subclasses WikiMainCostumeWindow at ingamewikiui.py:6734 so it
	# reuses the same WikiItem) hard-codes
	# "d:/ymir work/ui/wiki/detail_item_small.png" at line 6372. Swap
	# to wiki_new/item_window.png. Legacy is 127x141, new is 127x144
	# (3 px taller, same width); legacy centering math uses 125/2 so
	# the text position is a hair off, but per the user that's fine
	# until the per-card layout gets retuned.
	_NEW_ITEM_WINDOW_CARD = "d:/ymir work/ui/wiki/wiki_new/item_window.png"

	_origCostumeWikiItemInit = _legacyWiki.WikiMainCostumeWindow.WikiItem.__init__
	def _CostumeWikiItemInitRedesign(self, vnum, parent):
		_origCostumeWikiItemInit(self, vnum, parent)
		try:
			self.base.UnloadImage()
			self.base.LoadImage(_NEW_ITEM_WINDOW_CARD)
			# Resize self so the outer rect matches the new bg height,
			# otherwise the costume window's element-stride math reads
			# the original 141 and rows overlap by 3 px each.
			self.SetSize(self.base.GetWidth(), self.base.GetHeight())
		except Exception:
			import traceback, dbg
			dbg.TraceError(
				"wiki redesign Costume WikiItem bg swap:\n"
				+ traceback.format_exc())
	_legacyWiki.WikiMainCostumeWindow.WikiItem.__init__ = _CostumeWikiItemInitRedesign

	# Tutorial/custom pages: suppress banner image loading.
	#
	# Each tutorial text file under wiki/<file>.txt starts with a
	# "[banner_img=...]" token that the legacy SimpleTextLoader.LoadFile
	# routes to wikiBase.header.LoadImage / .Show (ingamewikiui.py:6020).
	# The redesign removed the legacy header strip, so those calls would
	# either crash (no .header attribute) or pollute the top of the wiki
	# window with stale banner art. Strip the key from every ParseToken
	# result before LoadFile sees it -- one surgical wrap instead of
	# rewriting the entire LoadFile body.
	_origParseToken = _legacyWiki.SimpleTextLoader.ParseToken
	def _ParseTokenNoBanner(self, data):
		ret, container, rest = _origParseToken(self, data)
		if container:
			container.pop("banner_img", None)
		return (ret, container, rest)
	_legacyWiki.SimpleTextLoader.ParseToken = _ParseTokenNoBanner

	# Reposition the special page to land inside contentArea instead of
	# at the legacy mainBoardPos (which overlaps our sidebar). The legacy
	# OpenSpecialPage in ingamewiki.py does
	#     newSpec.SetPosition(mainBoardPos[0] + 7, mainBoardPos[1] + 7)
	# so backing the values out by 7 from contentArea (241, 103) gives
	# the position used below. Mutating the list rather than rebinding
	# keeps every reader (including legacy paths we don't hit in
	# redesign mode) on the same object.
	_legacyWiki.mainBoardPos[0] = 224   # 234 + 7 = contentArea X
	_legacyWiki.mainBoardPos[1] = 106    # 96 + 7  = contentArea Y

	# Trim the item-page "drops from" panel height (the 351x142 window
	# beside the item icon) to fit the redesign art's slot for that
	# panel. List is shared with all WikiItemOriginInfo readers; mutate
	# in place so they stay on the same object.
	_legacyWiki.itemOriginPageSize[1] = 135

	# Resize the three bottom reverse-lookup panels on the no-content
	# item page (Used-for-Refining / Used-for-Crafting / Purchasable-with)
	# to match the redesign art slots. SpecialPageWindow's no-content
	# branch hard-codes (185, 173) inline; we override the panel's own
	# __init__ to ignore those args and build at the new size so all the
	# derived state (entryWidth, peekWindow size, scrollBoard size)
	# stays consistent.
	_REVERSE_PANEL_W = 178
	_REVERSE_PANEL_H = 170
	_origReversePanelInit = _legacyReverse.WikiReverseLookupPanel.__init__
	def _ReversePanelInitRedesign(self, width, height):
		_origReversePanelInit(self, _REVERSE_PANEL_W, _REVERSE_PANEL_H)
	_legacyReverse.WikiReverseLookupPanel.__init__ = _ReversePanelInitRedesign

	# Bottom margin (px) under the refine card's bonusPeekWindow inside
	# the SpecialPageWindow. The legacy code sizes bonusPeekWindow to
	# the FULL content height, so tall refine tables overflow past the
	# wiki bg. The cap applied in _SpecialPageInitRedesign reserves
	# this many px between the peekWindow's bottom and the bg's bottom.
	_BONUS_PEEK_BOTTOM_MARGIN = 6

	# Reverse-lookup panel POSITIONS (no-content item page).
	#
	# === TUNE THESE TO MOVE THE 3 BOTTOM COLUMNS ===
	#
	# Index matches the legacy column order:
	#   [0] = Used for Refining
	#   [1] = Used for Crafting (Cube)
	#   [2] = Purchasable with
	#
	# Legacy values were (0,173), (185,173), (370,173) -- the 185-px
	# stride no longer matches the new 178-wide panels, so the values
	# below pack them tight. Adjust freely.
	_REVERSE_PANEL_POSITIONS = [
		(  0, 182),
		(188, 184),
		(373, 184),
	]


# ---------------------------------------------------------------------------
# Asset roots
# ---------------------------------------------------------------------------
ASSET_ROOT = "d:/ymir work/ui/wiki/wiki_new/"

BG_PATH                = ASSET_ROOT + "bg.png"
SEARCHFIELD_PATH       = ASSET_ROOT + "searchfield.png"
CHECKBOX_BG_PATH       = ASSET_ROOT + "wiki_check_box_clean.png"
CHECKBOX_TICK_PATH     = ASSET_ROOT + "check_1.tga"
SEARCH_BTN_NORMAL      = ASSET_ROOT + "search_normal.png"
SEARCH_BTN_HOVER       = ASSET_ROOT + "search_hover.png"
SEARCH_BTN_DOWN        = ASSET_ROOT + "search_down.png"
X_BTN_NORMAL           = ASSET_ROOT + "x_norm.png"
X_BTN_HOVER            = ASSET_ROOT + "x_hover.png"
X_BTN_DOWN             = ASSET_ROOT + "x_down.png"
BACK_BTN_NORMAL        = ASSET_ROOT + "back_normal.png"
BACK_BTN_HOVER         = ASSET_ROOT + "back_hover.png"
BACK_BTN_DOWN          = ASSET_ROOT + "back_down.png"
FORWARD_BTN_NORMAL     = ASSET_ROOT + "forward_normal.png"
FORWARD_BTN_HOVER      = ASSET_ROOT + "forward_hover.png"
FORWARD_BTN_DOWN       = ASSET_ROOT + "forward_down.png"

# Phase 2 -- sidebar category buttons.
CATEG_BTN_NORMAL       = ASSET_ROOT + "btn_categ_norm.png"
CATEG_BTN_HOVER        = ASSET_ROOT + "btn_categ_hover.png"
CATEG_BTN_DOWN         = ASSET_ROOT + "btn_categ_down.png"
SUBCATEG_BTN_NORMAL    = ASSET_ROOT + "subcategory_normal.png"
SUBCATEG_BTN_HOVER     = ASSET_ROOT + "subcategory_hover.png"
SUBCATEG_BTN_DOWN      = ASSET_ROOT + "subcategory_down.png"
CHEVRON_PATH           = ASSET_ROOT + "arrow_down.png"
CATEG_ICON_ROOT        = ASSET_ROOT + "category/"
CATEG_ICON_DEFAULT     = CATEG_ICON_ROOT + "general_items.png"


# ---------------------------------------------------------------------------
# Layout constants (Phase 1 -- skeleton only)
# ---------------------------------------------------------------------------
# bg.png is 794x477. Coordinates below are all relative to the baseBoard.
WINDOW_W            = 794
WINDOW_H            = 477

TITLEBAR_X          = 8
TITLEBAR_Y          = 7
TITLEBAR_H          = 24

# Search row sits just under the title bar.
SEARCH_ROW_Y        = 38
SEARCH_BG_W         = 208               # searchfield.png native width
SEARCH_BG_H         = 25                # searchfield.png native height
SEARCH_BG_X         = 12

# Exact-search checkbox + nav arrows go to the right of the search field.
EXACT_CHECK_GAP     = 14
NAV_GAP             = 8
NAV_BTN_W           = 13
NAV_BTN_H           = 14

# Sidebar -- collapsible category tree on the left.
# Pushed past SEARCH_ROW_Y + SEARCH_BG_H + the second-row band that holds
# the Exact-Search checkbox + prev/next nav (which sit at y=77 with
# height ~14). +12 gap so the first parent button doesn't touch the nav.
SIDEBAR_X           = 13
SIDEBAR_Y           = 103
SIDEBAR_W           = 220                                # 200px button + gap + AdvScrollBar (7px) + breathing
SIDEBAR_H           = WINDOW_H - SIDEBAR_Y - 12
SCROLLBAR_W         = 7                                  # matches AdvScrollBar.SCROLLBAR_WIDTH (copied from uiadvancedgameoptions)

# Content panel placeholder (Phase 3+ paints the actual sub-page here).
CONTENT_X           = SIDEBAR_X + SIDEBAR_W + 8
CONTENT_Y           = SIDEBAR_Y
CONTENT_W           = WINDOW_W - CONTENT_X - 13
CONTENT_H           = SIDEBAR_H

# Sidebar widget metrics.
CATEG_BTN_W         = 200
CATEG_BTN_H         = 35
SUBCATEG_BTN_W      = 200
SUBCATEG_BTN_H      = 20
SIDEBAR_ROW_GAP     = 2     # vertical pixels between rows


# ---------------------------------------------------------------------------
# _RedesignStub: silent no-op stand-in for the legacy page windows.
#
# ingamewiki.py was written against the portrait wiki and reaches into
# self.mainWeaponWindow / self.mainChestWindow / self.categ / ... in several
# places (CloseBaseWindows, GoToLanding, OpenSpecialWikiPage). Phase 1 hasn't
# built those panels yet, but the legacy code path is still alive, so we
# attach stub objects so .Hide() / .NotifyCategorySelect() / .LoadFile() /
# .Show([vnum,]) calls don't AttributeError-out.
# ---------------------------------------------------------------------------
class _RedesignStub(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.SetSize(1, 1)
		self.Hide()

	# Match the legacy categ API surface used by ingamewiki.py
	def NotifyCategorySelect(self, *a, **kw): pass
	def AddCategory(self, *a, **kw): return self
	def AddSubCategory(self, *a, **kw): pass
	def RegisterScrollBar(self, *a, **kw): pass

	# Match the legacy custom-page API
	def LoadFile(self, *a, **kw): pass

	# Match the legacy header (ExpandedImageBox) API so any leftover
	# wikiBase.header.LoadImage / SetStringEvent call from the legacy
	# WikiCategory.OnSelectSubCategory path no-ops instead of crashing.
	def LoadImage(self, *a, **kw): pass
	def UnloadImage(self, *a, **kw): pass
	def SetStringEvent(self, *a, **kw): pass

	# Match the legacy chest-window Show([vnum,]) signature explicitly so
	# OpenSpecialWikiPage's call doesn't fall through to ui.Window.Show().
	def Show(self, *a, **kw):
		# Stay hidden. Phase 1 has no chest panel to display.
		pass

	def NoticeMe(self, *a, **kw): pass


# ---------------------------------------------------------------------------
# Category icon lookup -- maps the locale-resolved category label to its
# 24x24 icon under wiki_new/category/. Lazy because localeinfo.WIKI_CATEGORY_*
# values are runtime-loaded strings; building the dict at module import time
# would race the locale init in some entry paths.
# ---------------------------------------------------------------------------
_CATEG_ICON_CACHE = None

def _BuildCategoryIconMap():
	# Tolerant of missing locale keys (some legacy categories aren't shipped in
	# every locale build) -- skip the entry instead of raising at import time.
	m = {}
	def add(localeAttr, iconName):
		text = getattr(localeinfo, localeAttr, None)
		if text:
			m[text] = CATEG_ICON_ROOT + iconName
	add("WIKI_CATEGORY_EQUIPEMENT",  "equipment.png")
	add("WIKI_CATEGORY_CHESTS",      "chests.png")
	add("WIKI_CATEGORY_BOSSES",      "bosses.png")
	add("WIKI_CATEGORY_MONSTERS",    "general_items.png")
	add("WIKI_CATEGORY_METINSTONES", "metinstone.png")
	add("WIKI_CATEGORY_COSTUMES",    "equipment.png")
	add("WIKI_CATEGORY_EFFECTS",     "equipment.png")
	add("WIKI_CATEGORY_GUIDES",      "general_items.png")
	add("WIKI_CATEGORY_SYSTEMS",     "settings.png")
	add("WIKI_CATEGORY_DUNGEONS",    "dungeons.png")
	add("WIKI_CATEGORY_CRAFTING",    "crafting.png")
	add("WIKI_CATEGORY_SHOP",        "general_items.png")
	return m

def _IconForCategory(label):
	global _CATEG_ICON_CACHE
	if _CATEG_ICON_CACHE is None:
		_CATEG_ICON_CACHE = _BuildCategoryIconMap()
	return _CATEG_ICON_CACHE.get(label, CATEG_ICON_DEFAULT)


# ---------------------------------------------------------------------------
# WikiSubCategoryRow: one sub-item leaf (label-only button).
# ---------------------------------------------------------------------------
class WikiSubCategoryRow(ui.Window):
	def __init__(self, label, args_tuple, owner, parent_row=None):
		ui.Window.__init__(self)
		self._label = label
		self._args = args_tuple
		self._owner = owner       # back-ref to WikiCategoriesNew for click routing
		self._parent_row = parent_row    # WikiParentRow this sub belongs to;
		                                  # routes clicks to parent.clickEvent
		                                  # (mirrors legacy apply(parent.clickEvent, sub_args))

		self.btn = ui.Button()
		self.btn.SetParent(self)
		self.btn.SetUpVisual(SUBCATEG_BTN_NORMAL)
		self.btn.SetOverVisual(SUBCATEG_BTN_HOVER)
		self.btn.SetDownVisual(SUBCATEG_BTN_DOWN)
		self.btn.SetPosition(0, 0)
		self.btn.SAFE_SetEvent(self.OnClick)
		self.btn.Show()

		self.labelText = ui.TextLine()
		self.labelText.SetParent(self.btn)
		self.labelText.AddFlag("not_pick")
		self.labelText.SetText(label or "")
		if localeinfo.IsARABIC():
			# Arabic: anchor at the right edge of the button, glyphs flow leftward.
			self.labelText.SetPosition(SUBCATEG_BTN_W - 12, 2)
			self.labelText.SetHorizontalAlignLeft()
		else:
			self.labelText.SetPosition(18, 3)
		self.labelText.Show()

		self.SetSize(SUBCATEG_BTN_W, SUBCATEG_BTN_H)

	def OnClick(self):
		if self._owner is not None:
			self._owner._OnSubCategoryClicked(self)

	def GetLabel(self):      return self._label
	def GetArgs(self):       return self._args
	def GetParentRow(self):  return self._parent_row


# ---------------------------------------------------------------------------
# WikiParentRow: collapsible category header (icon + label + chevron) plus
# its list of sub-items. Click on the header toggles expand / collapse.
# ---------------------------------------------------------------------------
class WikiParentRow(ui.Window):
	def __init__(self, label, owner):
		ui.Window.__init__(self)
		self._label = label
		self._owner = owner            # WikiCategoriesNew
		self._index = -1                # set by WikiCategoriesNew.AddCategory; used for
		                                # proxy-immune identity in _OnParentToggled
		self._subRows = []
		self._expanded = False
		self.clickEvent = None          # legacy compat -- set by populate loop

		# Header button (35px tall).
		self.btn = ui.Button()
		self.btn.SetParent(self)
		self.btn.SetUpVisual(CATEG_BTN_NORMAL)
		self.btn.SetOverVisual(CATEG_BTN_HOVER)
		self.btn.SetDownVisual(CATEG_BTN_DOWN)
		self.btn.SetPosition(0, 0)
		self.btn.SAFE_SetEvent(self.OnToggle)
		self.btn.Show()

		# Icon.
		self.iconImg = ui.ImageBox()
		self.iconImg.SetParent(self.btn)
		self.iconImg.AddFlag("not_pick")
		self.iconImg.LoadImage(_IconForCategory(label))
		# Center vertically inside the 35px button; tuck against the
		# left (LTR) or right (RTL) edge.
		iconY = (CATEG_BTN_H - 24) // 2
		if localeinfo.IsARABIC():
			self.iconImg.SetPosition(CATEG_BTN_W - 24 - 6, iconY)
		else:
			self.iconImg.SetPosition(6, iconY + 5)
		self.iconImg.Show()

		# Label.
		self.labelText = ui.TextLine()
		self.labelText.SetParent(self.btn)
		self.labelText.AddFlag("not_pick")
		self.labelText.SetText(label or "")
		if localeinfo.IsARABIC():
			# Label anchored just left of the icon column; glyphs flow leftward.
			self.labelText.SetPosition(CATEG_BTN_W - 24 - 12 - 10, 10)
			self.labelText.SetHorizontalAlignLeft()
		else:
			self.labelText.SetPosition(36, 11)
		self.labelText.Show()

		# Chevron -- expand/collapse indicator. Sits on the opposite edge
		# from the icon (right for LTR, left for RTL).
		self.chevron = ui.ImageBox()
		self.chevron.SetParent(self.btn)
		self.chevron.AddFlag("not_pick")
		self.chevron.LoadImage(CHEVRON_PATH)
		chevronY = (CATEG_BTN_H - 10) // 2
		if localeinfo.IsARABIC():
			self.chevron.SetPosition(8, chevronY)
		else:
			self.chevron.SetPosition(CATEG_BTN_W - 22, chevronY)
		self.chevron.Show()

		self.SetSize(CATEG_BTN_W, CATEG_BTN_H)
		# Windows default to m_bShow=false; without this the row's children
		# never render even though their own Show() bits are flipped.
		self.Show()

	def AddSubCategory(self, index, sub_data):
		# sub_data is [label, args_tuple, banner_path] per ingamewikiconfig.
		# Sub-rows are NOT children of the parent row -- they're parented to
		# the sidebar's rowBoard (clipped container) and positioned by the
		# sidebar's layout pass. Nesting them under the parent row caused
		# two bugs:
		#   - picks failed because sub-rows lived outside the parent row's
		#     35-px header rect;
		#   - resizing the parent row on expand didn't reliably propagate
		#     children's screen rects in this engine build.
		label = sub_data[0]
		args = sub_data[1] if len(sub_data) > 1 else ()
		row = WikiSubCategoryRow(label, args_tuple=args,
			owner=self._owner, parent_row=self)
		row.SetParent(self._owner.rowBoard)
		row.Hide()                    # initially collapsed
		self._subRows.append(row)

	def OnToggle(self):
		self._expanded = not self._expanded
		for row in self._subRows:
			if self._expanded:
				row.Show()
			else:
				row.Hide()
		if self._owner is not None:
			# Pass our row index (not self) because SAFE_SetEvent wrapped
			# the OnToggle callback in a weakref proxy -- by the time we
			# get here, `self` is a proxy and `proxy is real` is always
			# False. The owner uses the index to skip us during the
			# "collapse siblings" pass; attribute reads through the proxy
			# DO reach the real instance, so _expanded etc. work fine.
			self._owner._OnParentToggled(self._index)
		# Parent-row click opens the first sub-category's panel as the
		# default content for the category. The legacy panel Show
		# methods all require args (mainWeaponWindow.Show(categID),
		# mainChestWindow.Show(vnums), mainBossWindow.Show(mobtypes,
		# from, to), customPageWindow.LoadFile(filename)), so we route
		# through the first sub's args_tuple defined in
		# ingamewikiconfig.WIKI_CATEGORIES -- that gives "click Weapons
		# = open the Sword sub by default" without us hard-coding any
		# per-panel defaults. Runs AFTER _OnParentToggled so the
		# CloseBaseWindows pass inside it doesn't immediately close the
		# panel we're about to open. Skipped on collapse (we only want
		# to open when expanding).
		if self._expanded and self.clickEvent and self._subRows:
			try:
				apply(self.clickEvent, self._subRows[0].GetArgs())
			except Exception:
				import traceback, dbg
				dbg.TraceError(
					"WikiParentRow.clickEvent (first-sub default):\n"
					+ traceback.format_exc())

	def Collapse(self):
		self._expanded = False
		for row in self._subRows:
			row.Hide()

	def GetTotalHeight(self):
		if self._expanded and self._subRows:
			return CATEG_BTN_H + SIDEBAR_ROW_GAP + len(self._subRows) * SUBCATEG_BTN_H
		return CATEG_BTN_H

	def GetSubRows(self):
		return self._subRows

	def IsExpanded(self):
		return self._expanded


# ---------------------------------------------------------------------------
# AdvScrollBar -- verbatim copy of the ScrollBarNew class defined inside
# uiadvancedgameoptions.py (lines 2548-2714), NOT ui.ScrollBarNew. The
# advanced-options module rolled its own narrower scrollbar (width 7,
# different XDIST/YDIST, dedicated art under
# d:/ymir work/ui/game/advanced_game_options/scrollbar/) and that's the
# look the wiki redesign wants -- using ui.ScrollBarNew gave a wider
# 12px bar with the stock thin-line track + visible-thumb-only look.
# ---------------------------------------------------------------------------
_ADV_IMG_DIR = "d:/ymir work/ui/game/advanced_game_options/"

class AdvScrollBar(ui.Window):
	SCROLLBAR_WIDTH = 7
	SCROLL_BTN_XDIST = 1
	SCROLL_BTN_YDIST = 1

	class MiddleBar(ui.DragButton):
		def __init__(self):
			ui.DragButton.__init__(self)
			self.AddFlag("movable")
			self.SetWindowName("scrollbar_middlebar")

		def MakeImage(self):
			top = ui.ExpandedImageBox()
			top.SetParent(self)
			top.LoadImage(_ADV_IMG_DIR + "scrollbar/scrollbar_top.tga")
			top.AddFlag("not_pick")
			top.Show()
			topScale = ui.ExpandedImageBox()
			topScale.SetParent(self)
			topScale.SetPosition(0, top.GetHeight())
			topScale.LoadImage(_ADV_IMG_DIR + "scrollbar/scrollbar_scale.tga")
			topScale.AddFlag("not_pick")
			topScale.Show()
			bottom = ui.ExpandedImageBox()
			bottom.SetParent(self)
			bottom.LoadImage(_ADV_IMG_DIR + "scrollbar/scrollbar_bottom.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()
			bottomScale = ui.ExpandedImageBox()
			bottomScale.SetParent(self)
			bottomScale.LoadImage(_ADV_IMG_DIR + "scrollbar/scrollbar_scale.tga")
			bottomScale.AddFlag("not_pick")
			bottomScale.Show()
			middle = ui.ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage(_ADV_IMG_DIR + "scrollbar/scrollbar_mid.tga")
			middle.AddFlag("not_pick")
			middle.Show()
			self.top = top
			self.topScale = topScale
			self.bottom = bottom
			self.bottomScale = bottomScale
			self.middle = middle

		def SetSize(self, height):
			minHeight = self.top.GetHeight() + self.bottom.GetHeight() + self.middle.GetHeight()
			height = max(minHeight, height)
			ui.DragButton.SetSize(self, 10, height)
			scale = (height - minHeight) / 2
			extraScale = 0
			if (height - minHeight) % 2 == 1:
				extraScale = 1
			self.topScale.SetRenderingRect(0, 0, 0, scale - 1)
			self.middle.SetPosition(0, self.top.GetHeight() + scale)
			self.bottomScale.SetPosition(0, self.middle.GetBottom())
			self.bottomScale.SetRenderingRect(0, 0, 0, scale - 1 + extraScale)
			self.bottom.SetPosition(0, height - self.bottom.GetHeight())

	def __init__(self):
		ui.Window.__init__(self)
		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = None
		self.eventArgs = None
		self.lockFlag = False
		self.CreateScrollBar()
		self.SetScrollBarSize(0)
		self.scrollStep = 0.4
		self.SetWindowName("AdvScrollBar")

	def __del__(self):
		ui.Window.__del__(self)

	def CreateScrollBar(self):
		topImage = ui.ExpandedImageBox()
		topImage.SetParent(self)
		topImage.AddFlag("not_pick")
		topImage.LoadImage(_ADV_IMG_DIR + "scrollbar/scroll_top.tga")
		topImage.Show()
		bottomImage = ui.ExpandedImageBox()
		bottomImage.SetParent(self)
		bottomImage.AddFlag("not_pick")
		bottomImage.LoadImage(_ADV_IMG_DIR + "scrollbar/scroll_bottom.tga")
		bottomImage.Show()
		middleImage = ui.ExpandedImageBox()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, topImage.GetHeight())
		middleImage.LoadImage(_ADV_IMG_DIR + "scrollbar/scroll_mid.tga")
		middleImage.Show()
		self.topImage = topImage
		self.bottomImage = bottomImage
		self.middleImage = middleImage
		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(ui.__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(12)
		self.middleBar = middleBar

	def Destroy(self):
		self.eventScroll = None
		self.eventArgs = None

	def SetScrollEvent(self, event, *args):
		self.eventScroll = event
		self.eventArgs = args

	def SetMiddleBarSize(self, pageScale):
		self.middleBar.SetSize(int(pageScale * float(self.GetHeight() - (self.SCROLL_BTN_YDIST * 2))))
		realHeight = self.GetHeight() - (self.SCROLL_BTN_YDIST * 2) - self.middleBar.GetHeight()
		self.pageSize = realHeight

	def SetScrollBarSize(self, height):
		self.SetSize(self.SCROLLBAR_WIDTH, height)
		self.pageSize = height - self.SCROLL_BTN_YDIST * 2 - self.middleBar.GetHeight()
		middleImageScale = float((height - self.SCROLL_BTN_YDIST * 2) - self.middleImage.GetHeight()) / float(self.middleImage.GetHeight())
		self.middleImage.SetRenderingRect(0, 0, 0, middleImageScale)
		self.bottomImage.SetPosition(0, height - self.bottomImage.GetHeight())
		self.middleBar.SetRestrictMovementArea(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST,
			self.middleBar.GetWidth(), height - self.SCROLL_BTN_YDIST * 2)
		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST)

	def SetScrollStep(self, step):
		self.scrollStep = step

	def OnUp(self):
		self.SetPos(self.curPos - self.scrollStep)

	def OnDown(self):
		self.SetPos(self.curPos + self.scrollStep)

	def GetScrollStep(self):
		return self.scrollStep

	def GetPos(self):
		return self.curPos

	def SetPos(self, pos, moveEvent=True):
		pos = max(0.0, pos)
		pos = min(1.0, pos)
		newPos = float(self.pageSize) * pos
		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, int(newPos) + self.SCROLL_BTN_YDIST)
		if moveEvent == True:
			self.OnMove()

	def OnMove(self):
		if self.lockFlag:
			return
		if 0 == self.pageSize:
			return
		(xLocal, yLocal) = self.middleBar.GetLocalPosition()
		self.curPos = float(yLocal - self.SCROLL_BTN_YDIST) / float(self.pageSize)
		if self.eventScroll:
			apply(self.eventScroll, self.eventArgs)

	def OnMouseLeftButtonDown(self):
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		newPos = float(yMouseLocalPosition) / float(self.GetHeight())
		self.SetPos(newPos)

	def LockScroll(self):
		self.lockFlag = True

	def UnlockScroll(self):
		self.lockFlag = False

	def OnRunMouseWheel(self, nLen):
		# Default convention in this codebase (see ui.py:ScrollBar) is to
		# gate wheel handling on the scrollbar's own rect. Without this
		# the engine's wheel routing can deliver events to a hidden /
		# off-cursor bar and scroll it from another panel.
		if not self.IsInPosition():
			return False
		if nLen > 0:
			self.OnUp()
			return True
		elif nLen < 0:
			self.OnDown()
			return True
		return False


# ---------------------------------------------------------------------------
# WikiAdvScrollBar: AdvScrollBar's look behind WikiScrollBar's API.
#
# The legacy weapon / chest / boss / etc. windows call self.scrollBar.
# SetScale / SetPosScale / SetSize / SetScrollEvent / SetScrollSpeed --
# the WikiScrollBar surface. AdvScrollBar exposes a different surface
# (SetMiddleBarSize / SetPos / SetScrollBarSize / SetScrollEvent that
# fires apply(event, args)). This wrapper translates between the two so
# we can drop AdvScrollBar in wherever the legacy code constructs a
# WikiScrollBar.
#
# Wheel behaviour is also corrected here: AdvScrollBar.OnRunMouseWheel
# is unconditional, so when multiple panels share the same parent the
# bar would scroll regardless of cursor position. We gate the wheel on
# self.IsInPosition() to match the legacy WikiScrollBar convention --
# but more importantly the *enclosing* panel (mainWeaponWindow etc.)
# also checks its own peekWindow.IsInPosition() before calling us, so
# the wheel only fires for whichever panel the cursor is currently over.
# ---------------------------------------------------------------------------
class WikiAdvScrollBar(ui.Window):
	def __init__(self, horizontal_scroll=False):
		ui.Window.__init__(self)
		self._adv = AdvScrollBar()
		self._adv.SetParent(self)
		self._adv.SetPosition(0, 0)
		# m_bShow defaults to False for new Windows in this engine; the
		# inner AdvScrollBar would never render even when our outer
		# wrapper is Show()'d. Flip the inner explicitly here so it
		# tracks the outer's visibility from now on.
		self._adv.Show()
		self._cb = None
		self.scrollSpeed = 1
		# Route AdvScrollBar's "thumb moved" event back to the legacy
		# WikiScrollBar callback signature (fScale in 0..1).
		self._adv.SetScrollEvent(ui.__mem_func__(self._OnAdvMove))

	def _OnAdvMove(self):
		if self._cb:
			self._cb(self._adv.GetPos())

	# ---- WikiScrollBar API surface ----
	# Cap the thumb at 50% of the track height. When content barely
	# overflows, the proportional formula (viewport/full) gets close to
	# 1.0 and the thumb's stretchable middle art balloons into a single
	# bright slab that fills the bar -- the "scrollbar looks strange"
	# regression we saw on the SpecialPage drop list. Capping keeps a
	# visible affordance of room-to-scroll and matches how the sidebar
	# bar looks in normal use.
	THUMB_MAX_SCALE = 0.5

	def SetScale(self, viewportSize, fullSize):
		# WikiScrollBar: shrink thumb proportional to viewport/full.
		if fullSize > 0:
			scale = float(viewportSize) / float(fullSize)
			if scale > self.THUMB_MAX_SCALE:
				scale = self.THUMB_MAX_SCALE
			self._adv.SetMiddleBarSize(scale)

	def SetPosScale(self, pos):
		self._adv.SetPos(pos)

	def SetSize(self, w, h):
		ui.Window.SetSize(self, w, h)
		self._adv.SetScrollBarSize(h)

	def SetScrollEvent(self, func):
		self._cb = ui.__mem_func__(func)

	def SetScrollSpeed(self, speed):
		self.scrollSpeed = speed

	def OnRunMouseWheel(self, length):
		# Engine routes wheel through the parent chain. The enclosing
		# panel (e.g. WikiMainWeaponWindow.OnRunMouseWheel) already gates
		# on its own peekWindow.IsInPosition() before calling us; this
		# self.IsInPosition() match the WikiScrollBar convention so the
		# bar doesn't grab events from cursor positions outside the bar.
		if not self.IsInPosition():
			# Still let the enclosing panel scroll us via OnUp/OnDown
			# directly when the wheel was meant for the panel area.
			return False
		if length > 0:
			self._adv.OnUp()
			return True
		elif length < 0:
			self._adv.OnDown()
			return True
		return False

	def OnUp(self):
		self._adv.OnUp()

	def OnDown(self):
		self._adv.OnDown()


# ---------------------------------------------------------------------------
# WikiCategoriesNew: the sidebar container. Exposes the same shape the
# legacy InGameWiki expects (AddCategory / NotifyCategorySelect /
# RegisterScrollBar / hideWindowsEvent attribute) so ingamewiki.py doesn't
# need branch-aware calls.
# ---------------------------------------------------------------------------
class WikiCategoriesNew(ui.Window):
	WHEEL_STEP = 24

	def __init__(self):
		ui.Window.__init__(self)
		self._parents = []
		self._scrollBar = None
		self.hideWindowsEvent = None   # set by InGameWiki -- closes current sub-page
		self._subPickEvent = None       # set by Phase 3 wiring; Phase 2: log to chat
		self._scrollY = 0
		self._totalH = 0
		self._suppressScrollEvent = False
		self.SetSize(SIDEBAR_W, SIDEBAR_H)

		# Architecture matches uiadvancedgameoptions.py: rows live in their
		# own container (rowBoard) that carries the clip mask, while the
		# scrollbar is a sibling so its SetRenderingRect-stretched mid
		# track doesn't inherit a clip and render broken.
		self.rowBoard = ui.Window()
		self.rowBoard.SetParent(self)
		self.rowBoard.SetPosition(0, 0)
		self.rowBoard.SetSize(SIDEBAR_W - SCROLLBAR_W - 4, SIDEBAR_H)
		self.rowBoard.Show()
		if hasattr(self.rowBoard, "SetClippingMaskWindow"):
			try:
				self.rowBoard.SetClippingMaskWindow(self.rowBoard)
			except Exception:
				pass

		# Visible scrollbar -- AdvScrollBar (copied verbatim from
		# uiadvancedgameoptions.py's local ScrollBarNew class). 7 px wide
		# track with its own dedicated art. Sibling of rowBoard so it's
		# outside the clip mask.
		self._sideBar = AdvScrollBar()
		self._sideBar.SetParent(self)
		self._sideBar.SetPosition(202, 0)
		self._sideBar.SetScrollBarSize(SIDEBAR_H)
		self._sideBar.SetScrollEvent(ui.__mem_func__(self._OnScrollBarMoved))
		self._sideBar.Hide()

	# -------- legacy categ API surface (ingamewiki.py touches these) --------
	def AddCategory(self, label):
		# Parent rows attach to rowBoard (the clipped container) so they
		# inherit the clip mask via AddChild propagation. Sub-rows do the
		# same in WikiParentRow.AddSubCategory.
		row = WikiParentRow(label, owner=self)
		row.SetParent(self.rowBoard)
		row._index = len(self._parents)   # proxy-immune identity for _OnParentToggled
		self._parents.append(row)
		self._Relayout()
		return row

	def NotifyCategorySelect(self, _which):
		# Called by InGameWiki.GoToLanding to reset the sidebar. Collapse all.
		for p in self._parents:
			p.Collapse()
		self._scrollY = 0
		self._Relayout()

	def RegisterScrollBar(self, scrollBar):
		# Scroll wiring deferred. Stash the ref so a later phase can hook up
		# clipping + SetScrollEvent without re-touching the populate path.
		self._scrollBar = scrollBar

	# -------- internal layout / event routing --------
	def _LayoutPass(self):
		# Stack parent headers, interleaving each expanded parent's sub-rows
		# directly beneath its header. Sub-rows are siblings of the parents
		# inside this sidebar so picking + rendering work uniformly without
		# the parent-row-resize hack we had before.
		y = -self._scrollY
		for p in self._parents:
			p.SetPosition(0, y)
			y += CATEG_BTN_H + SIDEBAR_ROW_GAP
			if p.IsExpanded():
				for sub in p.GetSubRows():
					sub.SetPosition(0, y)
					y += SUBCATEG_BTN_H
				y += SIDEBAR_ROW_GAP
		return y + self._scrollY    # total content height regardless of scroll

	def _Relayout(self):
		self._totalH = self._LayoutPass()
		# Clamp scroll if collapse shrank the content past current offset.
		maxScroll = max(0, self._totalH - SIDEBAR_H)
		if self._scrollY > maxScroll:
			self._scrollY = maxScroll
			self._totalH = self._LayoutPass()
		# Sync the visible scrollbar -- thumb-size ratio + thumb position +
		# show/hide based on whether the content overflows. Setting
		# scrollbar pos fires our SetScrollEvent callback; guard against
		# re-entry so the scrollbar doesn't immediately drive us back.
		self._UpdateScrollBar()

	def _UpdateScrollBar(self):
		if not self._sideBar:
			return
		maxScroll = max(0, self._totalH - SIDEBAR_H)
		if maxScroll <= 0:
			# No overflow -- park and hide.
			self._suppressScrollEvent = True
			try:
				self._sideBar.SetPos(0)
			finally:
				self._suppressScrollEvent = False
			self._sideBar.Hide()
			return
		# Thumb size relative to viewport / content (0..1).
		ratio = float(SIDEBAR_H) / float(self._totalH)
		self._sideBar.SetMiddleBarSize(ratio)
		# Position is 0..1 mapped from scrollY / maxScroll.
		pos = float(self._scrollY) / float(maxScroll)
		self._suppressScrollEvent = True
		try:
			self._sideBar.SetPos(pos)
		finally:
			self._suppressScrollEvent = False
		self._sideBar.Show()

	def _OnScrollBarMoved(self):
		# User dragged the scrollbar thumb (or wheel ran through it).
		# Ignore the echo from our own SetPos calls.
		if self._suppressScrollEvent:
			return
		maxScroll = max(0, self._totalH - SIDEBAR_H)
		pos = self._sideBar.GetPos() if self._sideBar else 0.0
		self._scrollY = int(pos * maxScroll)
		# Reposition rows for the new offset, but don't re-run
		# _UpdateScrollBar here (it would clobber the user's drag).
		self._LayoutPass()

	def OnRunMouseWheel(self, length):
		# Wheel must only scroll the sidebar when the cursor is actually
		# over the sidebar -- otherwise wheel events from the weapon /
		# chest / etc. panels on the right end up driving this bar
		# instead of their own. Gate on self.IsInPosition() (the sidebar
		# rect) and call OnUp/OnDown directly so the scrollbar advances
		# even when the cursor sits on a category button (off the 7 px
		# bar itself).
		if not self.IsInPosition():
			return False
		if not (self._sideBar and self._sideBar.IsShow()):
			return False
		if length > 0:
			self._sideBar.OnUp()
		elif length < 0:
			self._sideBar.OnDown()
		return True

	def _OnParentToggled(self, parentIdx):
		# Collapse siblings so only one branch is open at a time -- mimics
		# the visual rhythm of the design mockups.
		# Identity by index because SAFE_SetEvent wraps the caller in a
		# weakref proxy and `p is parent` always fails (proxy != real).
		for i, p in enumerate(self._parents):
			if i != parentIdx and p._expanded:
				p.Collapse()
		self._Relayout()
		# Close any currently-open sub-page when the user changes branch.
		if self.hideWindowsEvent:
			try:
				self.hideWindowsEvent()
			except Exception:
				import traceback, dbg
				dbg.TraceError("WikiCategoriesNew.hideWindowsEvent:\n" + traceback.format_exc())

	def _OnSubCategoryClicked(self, row):
		# Mirror the legacy WikiCategory.OnSubCategorySelect dispatch:
		#     1. Close any panel that was open (hideWindowsEvent ->
		#        InGameWiki.CloseBaseWindows). Without this, two panels
		#        would stack inside contentArea on consecutive picks.
		#     2. apply(parent.clickEvent, sub_args). parent.clickEvent was
		#        set in _BuildSidebar from the funclist (one entry per
		#        WIKI_CATEGORIES index pointing at the matching legacy
		#        mainWeaponWindow.Show / mainChestWindow.Show / etc.).
		if self.hideWindowsEvent:
			try:
				self.hideWindowsEvent()
			except Exception:
				import traceback, dbg
				dbg.TraceError("WikiCategoriesNew sub-pick hide:\n"
					+ traceback.format_exc())

		parent_row = row.GetParentRow()
		if parent_row is not None and parent_row.clickEvent is not None:
			try:
				apply(parent_row.clickEvent, row.GetArgs())
				return
			except Exception:
				import traceback, dbg
				dbg.TraceError("WikiCategoriesNew sub-pick dispatch:\n"
					+ traceback.format_exc())

		# Optional Phase 3 hook -- still respected if anyone registered one.
		if self._subPickEvent is not None:
			try:
				self._subPickEvent(row.GetLabel(), row.GetArgs())
				return
			except Exception:
				import traceback, dbg
				dbg.TraceError("WikiCategoriesNew sub pick:\n"
					+ traceback.format_exc())

		# Final fallback -- a category with no clickEvent wired (text guides,
		# craft/shop branches when the matching app.USE_* is off). Note in
		# chat so the click is visible during development.
		try:
			import chat
			chat.AppendChat(1, "[Wiki] %s" % (row.GetLabel() or ""))
		except Exception:
			pass

	def SetSubPickEvent(self, callback):
		self._subPickEvent = callback


# ---------------------------------------------------------------------------
# _CheckBox: tiny purpose-built two-state checkbox for the redesign.
#
# ui.InGameWikiCheckBox hard-codes the legacy asset paths and bundles a label
# we don't want here -- this widget paints the background, toggles a tick
# overlay on click, and emits a single Python event.
# ---------------------------------------------------------------------------
class _CheckBox(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)

		self.bg = ui.ImageBox()
		self.bg.SetParent(self)
		self.bg.AddFlag("not_pick")
		self.bg.LoadImage(CHECKBOX_BG_PATH)
		self.bg.SetPosition(0, 0)
		self.bg.Show()

		self.tick = ui.ImageBox()
		self.tick.SetParent(self)
		self.tick.AddFlag("not_pick")
		self.tick.LoadImage(CHECKBOX_TICK_PATH)
		# Tick image (check_1.tga 14x12) sits visually inside the 14x14 box.
		self.tick.SetPosition(0, 1)
		self.tick.Hide()

		self.SetSize(self.bg.GetWidth(), self.bg.GetHeight())

		self._checked = False
		self._onToggle = None

	def IsChecked(self):
		return self._checked

	def SetChecked(self, flag):
		self._checked = bool(flag)
		if self._checked:
			self.tick.Show()
		else:
			self.tick.Hide()

	def SetToggleEvent(self, func):
		self._onToggle = func

	def OnMouseLeftButtonUp(self):
		self.SetChecked(not self._checked)
		if self._onToggle:
			try:
				self._onToggle(self._checked)
			except Exception:
				import traceback, dbg
				dbg.TraceError("WikiRedesign _CheckBox toggle:\n" + traceback.format_exc())


# ---------------------------------------------------------------------------
# Public entry points used by ingamewiki.py
# ---------------------------------------------------------------------------
def InitMainWindow(self):
	"""Mirror of the legacy InitMainWindow: register blacklists + build the
	wiki search list. The C++ side reads these tables on every search query;
	leaving them empty would break the existing reverse-search work even
	though Phase 1 doesn't surface a category sidebar yet."""
	self.AddFlag('movable')
	self.AddFlag('float')

	for i in ingamewikiconfig.ITEM_BLACKLIST:
		if type(i) == types.ListType:
			for k in i:
				wiki.RegisterItemBlacklist(k)
		else:
			wiki.RegisterItemBlacklist(i)

	for i in ingamewikiconfig.MOB_WHITELIST:
		if type(i) == types.ListType:
			for k in i:
				wiki.RegisterMonsterBlacklist(k)
		else:
			wiki.RegisterMonsterBlacklist(i)

	nonplayer.BuildWikiSearchList()


def BuildBaseMain(self):
	"""Build the Phase 1 skeleton window. See module docstring for scope."""

	# Some legacy config (shop dicts, craft dicts) is loaded lazily and is
	# needed by InGameWiki's CloseBaseWindows even though Phase 1 doesn't
	# draw shop/craft panels. Keep the legacy load path.
	if app.USE_EXTENDED_WIKI_CRAFT or app.USE_EXTENDED_WIKI_SHOP or app.ENABLE_ITEM_SHOPS:
		ingamewikiconfig.Load()

	# -- Background ----------------------------------------------------------
	self.baseBoard = ui.ExpandedImageBox()
	self.baseBoard.AddFlag("attach")
	self.baseBoard.SetParent(self)
	self.baseBoard.LoadImage(BG_PATH)
	self.baseBoard.SetWindowName("InGameWikiBoard")
	self.baseBoard.Show()

	self.SetSize(self.baseBoard.GetWidth(), self.baseBoard.GetHeight())

	# -- Title bar (movable handle + close button) ---------------------------
	self.titleBar = ui.TitleBar()
	self.titleBar.SetParent(self.baseBoard)
	self.titleBar.MakeTitleBar(0, "red")
	self.titleBar.SetWidth(self.GetWidth() - 15)
	self.titleBar.SetPosition(TITLEBAR_X, TITLEBAR_Y)
	self.titleBar.SetCloseEvent(self.Close)
	self.titleBar.Show()

	self.titleName = ui.TextLine()
	self.titleName.SetParent(self.titleBar)
	self.titleName.SetPosition(0, 4)
	self.titleName.SetWindowHorizontalAlignCenter()
	self.titleName.SetHorizontalAlignCenter()
	self.titleName.SetText(localeinfo.WIKI_TITLENAME)
	self.titleName.Show()

	# -- Search row (search field + buttons + exact-match + nav) -------------
	_BuildSearchRow(self)

	# -- Empty content panel placeholder -------------------------------------
	# An invisible window reserves the rectangle Phase 2/3 will populate. We
	# don't paint anything inside it yet -- the bg.png provides the framing.
	self.contentArea = ui.Window()
	self.contentArea.SetParent(self.baseBoard)
	self.contentArea.AddFlag("attach")
	self.contentArea.AddFlag("not_pick")
	self.contentArea.SetPosition(CONTENT_X, CONTENT_Y)
	self.contentArea.SetSize(CONTENT_W, CONTENT_H)
	self.contentArea.Show()

	# -- Legacy-compat stubs -------------------------------------------------
	# ingamewiki.py touches these attributes from methods we still want to
	# work (CloseBaseWindows, GoToLanding, OpenSpecialWikiPage). Replaced
	# with real widgets in later phases.
	_AttachLegacyStubs(self)

	# -- Sidebar (Phase 2) -- collapsible category tree on the left ----------
	# Replaces the _RedesignStub categ attached above.
	_BuildSidebar(self)


# ---------------------------------------------------------------------------
# Search row
# ---------------------------------------------------------------------------
def _BuildSearchRow(self):
	# Background pill for the search edit + X button.
	self.searchBG = ui.ExpandedImageBox()
	self.searchBG.SetParent(self.baseBoard)
	self.searchBG.LoadImage(SEARCHFIELD_PATH)
	self.searchBG.SetPosition(SEARCH_BG_X, SEARCH_ROW_Y)
	self.searchBG.Show()

	# X-clear button on the right edge of the search field.

	self.searchClearBtn = ui.Button()
	self.searchClearBtn.SetParent(self.searchBG)
	self.searchClearBtn.SetUpVisual(X_BTN_NORMAL)
	self.searchClearBtn.SetOverVisual(X_BTN_HOVER)
	self.searchClearBtn.SetDownVisual(X_BTN_DOWN)
	self.searchClearBtn.SetPosition(163,5)
	# SAFE_SetEvent wraps with __mem_func__ internally -- don't double-wrap.
	self.searchClearBtn.SAFE_SetEvent(self.OnPressNameEscapeKey)
	self.searchClearBtn.Show()

	# Edit line -- everything left of the X button.
	self.searchEdit = ui.EditLine()
	self.searchEdit.SetParent(self.searchBG)
	self.searchEdit.SetMax(50)
	editW = SEARCH_BG_W - self.searchClearBtn.GetWidth() - 32
	self.searchEdit.SetSize(editW, 15)
	self.searchEdit.SetPosition(0, 5)
	if app.USE_GRAPHIC_TEXT_SEARCH_BOX_WIDTH_LIMIT:
		self.searchEdit.SetSearchBoxLimitWidth(self.searchEdit.GetWidth())
	self.searchEdit.SetEscapeEvent(ui.__mem_func__(self.OnPressNameEscapeKey))
	self.searchEdit.SetReturnEvent(ui.__mem_func__(self.StartSearch))
	self.searchEdit.SetUpdateEvent(ui.__mem_func__(self.Search_RefreshResults))
	self.searchEdit.SetTabEvent(ui.__mem_func__(self.OnPressSearchTab))
	self.searchEdit.SetOutline()
	self.searchEdit.SetOverlayTextNew(localeinfo.WIKI_SEARCH_OVERLAY_TEXT)
	self.searchEdit.Show()

	# Inline ghost-text prediction (gray suffix shown right after typed text).
	# Positioned + Show/Hide'd dynamically by _UpdateSearchHint in ingamewiki.py.
	self.searchHint = ui.TextLine()
	self.searchHint.SetParent(self.searchBG)
	self.searchHint.SetPackedFontColor(0xFF808080)
	self.searchHint.Hide()

	# Magnifier button -- sits to the right of the search pill.
	magnifierX = 194
	magnifierY = 37     # 27 = search_normal.png height
	self.searchButton = ui.Button()
	self.searchButton.SetParent(self.baseBoard)
	self.searchButton.SetUpVisual(SEARCH_BTN_NORMAL)
	self.searchButton.SetOverVisual(SEARCH_BTN_HOVER)
	self.searchButton.SetDownVisual(SEARCH_BTN_DOWN)
	self.searchButton.SetPosition(magnifierX, magnifierY)
	self.searchButton.SAFE_SetEvent(self.StartSearch)
	self.searchButton.Show()

	# Exact-search checkbox + label, sits left of the search pill.
	self.exactSearch = _CheckBox()
	self.exactSearch.SetParent(self.baseBoard)
	exactX = 105
	exactY = 77
	self.exactSearch.SetPosition(exactX, exactY)
	self.exactSearch.Show()

	self.exactSearchLabel = ui.TextLine()
	self.exactSearchLabel.SetParent(self.baseBoard)
	if localeinfo.IsARABIC():
		# Arabic: anchor right of the box, glyphs flow leftward.
		self.exactSearchLabel.SetPosition(
			exactX - 4,
			exactY - 4)
		#self.exactSearchLabel.SetHorizontalAlignRight()
	else:
		self.exactSearchLabel.SetPosition(
			exactX + self.exactSearch.GetWidth() + 4,
			exactY)
	self.exactSearchLabel.SetText(localeinfo.WIKI_EXACT_SEARCH_TEXT)
	self.exactSearchLabel.Show()

	# Prev / Next nav arrows -- right of the magnifier.
	navBaseX = 167
	navY = 77

	self.prevButt = ui.Button()
	self.prevButt.SetParent(self.baseBoard)
	self.prevButt.SetUpVisual(BACK_BTN_NORMAL)
	self.prevButt.SetOverVisual(BACK_BTN_HOVER)
	self.prevButt.SetDownVisual(BACK_BTN_DOWN)
	self.prevButt.SetDisableVisual(BACK_BTN_DOWN)
	self.prevButt.SetPosition(navBaseX, navY)
	self.prevButt.SAFE_SetEvent(self.OnPressPrevButton)
	self.prevButt.Show()
	self.prevButt.Disable()

	self.nextButt = ui.Button()
	self.nextButt.SetParent(self.baseBoard)
	self.nextButt.SetUpVisual(FORWARD_BTN_NORMAL)
	self.nextButt.SetOverVisual(FORWARD_BTN_HOVER)
	self.nextButt.SetDownVisual(FORWARD_BTN_DOWN)
	self.nextButt.SetDisableVisual(FORWARD_BTN_DOWN)
	self.nextButt.SetPosition(navBaseX + NAV_BTN_W + 6, navY)
	self.nextButt.SAFE_SetEvent(self.OnPressNextButton)
	self.nextButt.Show()
	self.nextButt.Disable()

	# Search results dropdown -- reuses the legacy module unchanged. Anchored
	# below the search pill, parented to the wiki window itself so SetTop()
	# lifts it above the entire wiki frame (same trick the legacy build uses).
	self.searchResults = ingamewikisearch.WikiSearchResults(
		width=max(SEARCH_BG_W + 5, 175))
	self.searchResults.SetParent(self)
	self.searchResults.SetPosition(
		SEARCH_BG_X,
		SEARCH_ROW_Y + SEARCH_BG_H + 2)
	self.searchResults.SetPickEvent(ui.__mem_func__(self.OnSearchResultPicked))


# ---------------------------------------------------------------------------
# Legacy compatibility stubs
# ---------------------------------------------------------------------------
def _AttachLegacyStubs(self):
	# Categories sidebar -- Phase 2 builds the real collapsible tree.
	self.categ = _RedesignStub()
	self.categ.SetParent(self.baseBoard)

	# Header stub. The legacy InGameWiki has a self.header ExpandedImageBox
	# (ingamewikiui.py:6913) that other classes poke at -- WikiCategory.
	# OnSelectSubCategory and SimpleTextLoader.LoadFile both call
	# wikiBase.header.LoadImage / .Show / .Hide. The redesign doesn't
	# render a header strip, but those calls still need a safe sink so
	# they don't AttributeError on a missing attribute. _RedesignStub
	# already absorbs LoadImage / Show / Hide / NotifyCategorySelect
	# via *a, **kw on each.
	self.header = _RedesignStub()
	self.header.SetParent(self.baseBoard)
	self.header.Hide()

	# Sub-pages.
	# Weapons: REAL legacy WikiMainWeaponWindow, just reparented into our
	# contentArea + resized to the landscape rectangle. All the data-fetch
	# / refine-grid / scroll plumbing stays in the legacy class; the visual
	# restyle happens via the monkey-patches at the top of this module
	# (WikiBuildGrid backdrop swap + WikiItem ROW_START_Y / label hides).
	self.mainWeaponWindow = _legacyWiki.WikiMainWeaponWindow()
	self.mainWeaponWindow.SetParent(self.contentArea)
	# Card backdrop (detail_item*.png) is 541-545 px wide; contentArea is
	# only 540 px. Shift the whole weapon window LEFT so the card visual
	# clears the right-edge gutter where the scrollbar sits, then make
	# the window slightly oversized to keep the scrollbar inside the
	# contentArea rectangle.
	_MW_X      = -15
	_MW_W      = 555
	_PEEK_X    = 5
	_PEEK_Y    = 65       # was 50 -- pushed down to clear 44 px class buttons
	_PEEK_W    = 541      # full backdrop width
	_SCROLL_X  = _PEEK_X + _PEEK_W + 1   # = 547, just past the card
	_SCROLL_W  = 7

	self.mainWeaponWindow.SetPosition(_MW_X, 0)
	self.mainWeaponWindow.SetSize(_MW_W, CONTENT_H)

	_mw = self.mainWeaponWindow
	_mw.peekWindow.SetPosition(_PEEK_X, _PEEK_Y)
	_mw.peekWindow.SetSize(_PEEK_W, _mw.GetHeight() - _PEEK_Y - 10)

	# Swap the legacy WikiScrollBar for WikiAdvScrollBar -- same visual
	# language as the sidebar, exposes the same API surface so
	# ChangeScrollbar / OnScrollBar / UpdateScrollbar all keep working.
	# ui.py's SetParent(None) crashes (it does `parent.hWnd`), so we just
	# Hide() the legacy bar and park it off-screen; it stays parented to
	# mainWeaponWindow but is invisible and out of the cursor path.
	if _mw.scrollBar:
		_mw.scrollBar.Hide()
		_mw.scrollBar.SetPosition(-9999, -9999)
	_new_sb = WikiAdvScrollBar()
	_new_sb.SetParent(_mw)
	_new_sb.SetPosition(_SCROLL_X, _PEEK_Y)
	_new_sb.SetSize(_SCROLL_W, _mw.peekWindow.GetHeight())
	_new_sb.SetScrollEvent(_mw.OnScrollBar)
	_new_sb.SetScrollSpeed(_mw.SCROLL_SPEED)
	_new_sb.Hide()
	_mw.scrollBar = _new_sb

	self.mainWeaponWindow.Hide()

	# Real legacy panels for the remaining categories. Each is parented
	# into contentArea (NOT baseBoard) so the same redesigned content
	# rectangle hosts every panel; per-panel positions are tuned via
	# _PANEL_POSITIONS below. AddFlag("attach") so the parent clip
	# carries through; styling is still legacy here (this is the first
	# pass that gets them rendering at all -- per-panel restyle is a
	# follow-up).
	#
	# === TUNE THESE TO MOVE EACH PANEL ===
	#   chest   = WikiMainChestWindow  (Chests parent)
	#   boss    = WikiMainBossWindow   (Bosses + Monsters parents)
	#   costume = WikiMainCostumeWindow (Costumes / Costume Weapons)
	#   custom  = SimpleTextLoader     (text guides, landing page)
	#   craft   = WikiItemCraftWindow  (Crafting recipes)
	#   shop    = WikiShopWindow       (Shop list)
	#   shopit  = WikiMainShopItemWindow (Item-shop list)
	_PANEL_POSITIONS = {
		"chest":   (-11, 5),
		"boss":    (-11, 5),
		"costume": (-11, 5),
		"craft":   (-11, 5),
		"shop":    (-11, 5),
		"shopit":  (-11, 5),
		"dungeon": (-11, 5),
		"biolog":  (-11, 5),
		"dragonsoul": (-11, 5),
		"growthpet": (-11, 5),
		"growthmount": (-11, 5),
		"gemshop": (-11, 5),
		"buffi":   (-11, 5),
		# NOTE: customPageWindow lives in _TUTORIAL_POSITIONS below --
		# it has extra knobs (inner peekWindow + scrollbar offsets) so
		# all of its layout sits in one dict.
	}

	# === TUTORIAL PAGE LAYOUT ===
	# customPageWindow (SimpleTextLoader) has more positional pieces
	# than the other panels (an inner peekWindow + a scrollbar inside
	# it), so it gets its own dict so all of its layout is tunable in
	# one place. All values are (x, y) tuples; None on an axis means
	# "leave the legacy default".
	_TUTORIAL_POSITIONS = {
		"outer":     (-11, 5),    # customPageWindow inside contentArea
		"peek":      (  5, 5),    # peekWindow inside customPageWindow
		"scrollbar": (None, None),  # scrollBar (x, y) -- None on either axis keeps legacy
	}

	def _attach_panel(w, key):
		px, py = _PANEL_POSITIONS.get(key, (0, 0))
		w.SetParent(self.contentArea)
		w.AddFlag("attach")
		w.SetPosition(px, py)
		w.Hide()

	def _apply_tutorial_layout(w):
		# outer (customPageWindow position inside contentArea)
		ox, oy = _TUTORIAL_POSITIONS["outer"]
		w.SetPosition(ox, oy)
		# inner peekWindow (clipped scroll viewport)
		pk = getattr(w, "peekWindow", None)
		if pk is not None:
			pxv, pyv = _TUTORIAL_POSITIONS["peek"]
			cur_pxv, cur_pyv = pk.GetLocalPosition()
			pk.SetPosition(cur_pxv if pxv is None else pxv,
			               cur_pyv if pyv is None else pyv)
		# inner scrollBar
		sb = getattr(w, "scrollBar", None)
		if sb is not None:
			sxv, syv = _TUTORIAL_POSITIONS["scrollbar"]
			cur_sxv, cur_syv = sb.GetLocalPosition()
			sb.SetPosition(cur_sxv if sxv is None else sxv,
			               cur_syv if syv is None else syv)

	self.mainChestWindow   = _legacyWiki.WikiMainChestWindow()
	_attach_panel(self.mainChestWindow,   "chest")
	self.mainBossWindow    = _legacyWiki.WikiMainBossWindow()
	_attach_panel(self.mainBossWindow,    "boss")
	self.costumePageWindow = _legacyWiki.WikiMainCostumeWindow()
	_attach_panel(self.costumePageWindow, "costume")
	# customPageWindow: parent + attach + hide like the others, then
	# layer the tutorial-specific layout on top via the dedicated
	# _TUTORIAL_POSITIONS dict.
	self.customPageWindow  = _legacyWiki.SimpleTextLoader()
	self.customPageWindow.SetParent(self.contentArea)
	self.customPageWindow.AddFlag("attach")
	self.customPageWindow.Hide()
	_apply_tutorial_layout(self.customPageWindow)

	if app.USE_EXTENDED_WIKI_CRAFT:
		self.craftItemPageWindow = _legacyWiki.WikiItemCraftWindow()
		_attach_panel(self.craftItemPageWindow, "craft")
	if app.USE_EXTENDED_WIKI_SHOP:
		self.shopPageWindow = _legacyWiki.WikiShopWindow()
		_attach_panel(self.shopPageWindow, "shop")
	if app.ENABLE_ITEM_SHOPS:
		self.shopItemPageWindow = _legacyWiki.WikiMainShopItemWindow()
		_attach_panel(self.shopItemPageWindow, "shopit")

	self.dungeonPageWindow = ingamewikidungeon.WikiDungeonWindow()
	_attach_panel(self.dungeonPageWindow, "dungeon")

	self.biologPageWindow = ingamewikibiolog.WikiBiologWindow()
	_attach_panel(self.biologPageWindow, "biolog")

	self.dragonSoulPageWindow = ingamewikidragonsoul.WikiDragonSoulWindow()
	_attach_panel(self.dragonSoulPageWindow, "dragonsoul")

	self.growthPetPageWindow = ingamewikigrowthpet.WikiGrowthPetWindow()
	_attach_panel(self.growthPetPageWindow, "growthpet")

	self.growthMountPageWindow = ingamewikigrowthmount.WikiGrowthMountWindow()
	_attach_panel(self.growthMountPageWindow, "growthmount")

	self.gemShopPageWindow = ingamewikigemshop.WikiGemShopWindow()
	_attach_panel(self.gemShopPageWindow, "gemshop")

	self.buffiPageWindow = ingamewikibuffi.WikiBuffiWindow()
	_attach_panel(self.buffiPageWindow, "buffi")


# ---------------------------------------------------------------------------
# _BuildSidebar -- replace the categ stub with the real Phase 2 sidebar and
# populate it from ingamewikiconfig.WIKI_CATEGORIES. Parent click events
# wire to the legacy panel-Show callbacks (currently RedesignStub no-ops);
# Phase 3 swaps those for the new content panels.
# ---------------------------------------------------------------------------
def _BuildSidebar(self):
	self.categ = WikiCategoriesNew()
	self.categ.SetParent(self.baseBoard)
	self.categ.AddFlag("attach")
	self.categ.SetPosition(SIDEBAR_X, SIDEBAR_Y)
	self.categ.hideWindowsEvent = ui.__mem_func__(self.CloseBaseWindows)
	self.categ.Show()

	# Same parallel-list pattern as the legacy build -- categories ordered
	# per ingamewikiconfig.WIKI_CATEGORIES, parent-click funclist mapped by
	# index. Mismatched lengths are tolerated (extra categories get no
	# parent-click action; clicking them only toggles expand/collapse).
	funclist = [
		ui.__mem_func__(self.mainWeaponWindow.Show),
		ui.__mem_func__(self.mainChestWindow.Show),
		ui.__mem_func__(self.mainBossWindow.Show),
		ui.__mem_func__(self.mainBossWindow.Show),
		ui.__mem_func__(self.mainBossWindow.Show),
		ui.__mem_func__(self.costumePageWindow.Show),
		ui.__mem_func__(self.costumePageWindow.Show),
		ui.__mem_func__(self.customPageWindow.LoadFile),
		ui.__mem_func__(self.customPageWindow.LoadFile),
		ui.__mem_func__(self.customPageWindow.LoadFile),
	]
	if app.USE_EXTENDED_WIKI_CRAFT:
		funclist.append(ui.__mem_func__(self.craftItemPageWindow.Show))
	if app.USE_EXTENDED_WIKI_SHOP:
		funclist.append(ui.__mem_func__(self.shopPageWindow.Show))
	if app.ENABLE_ITEM_SHOPS:
		funclist.append(ui.__mem_func__(self.shopItemPageWindow.Show))

	hiddenCategories = getattr(ingamewikiconfig, "WIKI_HIDDEN_CATEGORIES", [])

	for i in ingamewikiconfig.WIKI_CATEGORIES:
		if i[0] in hiddenCategories:
			continue

		parent = self.categ.AddCategory(i[0])
		for j in xrange(len(i[1])):
			parent.AddSubCategory(j, i[1][j])
		idx = ingamewikiconfig.WIKI_CATEGORIES.index(i)
		if idx < len(funclist):
			parent.clickEvent = funclist[idx]
		if i[0] == localeinfo.WIKI_CATEGORY_DUNGEONS:
			parent.clickEvent = ui.__mem_func__(self.OpenDungeonRoute)
		if i[0] == localeinfo.WIKI_CATEGORY_SYSTEMS:
			parent.clickEvent = ui.__mem_func__(self.OpenSystemRoute)


# ---------------------------------------------------------------------------
# WikiScrollBar tuning: keep the legacy code-drawn look (works at small
# track sizes that the AdvScrollBar texture set doesn't degrade to), and
#   1) recolor it to match AdvScrollBar's palette (sampled from the .tga
#      files: track = #423A38 warm dark brown, thumb = #B6A093 taupe);
#   2) cap the thumb at 50% of the track so a barely-overflowing list
#      doesn't collapse into a single solid slab.
#
# Both changes are class-attribute mutations on WikiScrollBar / its
# MiddleBar inner class, so every existing call site (main weapon panel,
# chest panel, boss panel, originInfo, etc.) picks up the new look with
# no per-site changes. Horizontal WikiScrollBar(True) keeps the legacy
# thumb sizing (the cap is irrelevant for horizontal).
#
# Background: an earlier pass tried to swap the 9-ui.Bar frame for the
# AdvScrollBar .tga texture stack itself. That set is designed for
# ~400 px sidebars; on the wiki's 60-140 px panels the fixed top/mid/
# bottom decorations fill the entire thumb and the stretchable "scale"
# pieces collapse to zero or negative, producing fragmented thumbs. The
# textures turned out to be flat solid colors anyway, so recoloring the
# code-drawn bars gives the same look without the small-size breakage.
# ---------------------------------------------------------------------------
if app.ENABLE_WIKI_REDESIGN:
	# Sampled directly from advanced_game_options/scrollbar/*.tga -- the
	# textures are flat single-color so this matches them pixel-for-pixel.
	_legacyWiki.WikiScrollBar.BASE_COLOR              = grp.GenerateColor(0.2588, 0.2275, 0.2196, 1.0)
	_legacyWiki.WikiScrollBar.CORNERS_AND_LINES_COLOR = grp.GenerateColor(0.2588, 0.2275, 0.2196, 1.0)
	_legacyWiki.WikiScrollBar.MiddleBar.MIDDLE_BAR_COLOR = grp.GenerateColor(0.7137, 0.6275, 0.5765, 1.0)

	_origMiddleBarSetSize = _legacyWiki.WikiScrollBar.MiddleBar.SetSize

	def _MiddleBarSetSizeCapped(self, selfSize, fullSize):
		if getattr(self, "horizontal_scroll", False):
			return _origMiddleBarSetSize(self, selfSize, fullSize)
		if fullSize <= 0:
			return _origMiddleBarSetSize(self, selfSize, fullSize)
		# Cap the viewport/full ratio at 0.5 so the thumb never grows
		# past half the track. We feed (cappedSize, selfSize) back into
		# the legacy SetSize so its own height math
		# ((selfSize/fullSize) * selfSize) yields cappedSize * selfSize /
		# selfSize = cappedSize. Floor at 12 px so the thumb stays
		# grabbable on very tall lists.
		ratio = float(selfSize) / float(fullSize)
		if ratio > 0.5:
			cappedSize = max(12, int(0.5 * selfSize))
			_origMiddleBarSetSize(self, cappedSize, selfSize)
		else:
			_origMiddleBarSetSize(self, selfSize, fullSize)

	_legacyWiki.WikiScrollBar.MiddleBar.SetSize = _MiddleBarSetSizeCapped


# ---------------------------------------------------------------------------
# SpecialPageWindow restyle (originInfo): switch the drop-list row text
# from centered to AlignLeft. LTR rows anchor at a small left padding;
# Arabic rows mirror that by anchoring at the right edge with
# SetHorizontalAlignLeft so glyphs grow leftward (per project memory:
# Align* names the direction text grows FROM the anchor).
#
# Scrollbar stays on the legacy WikiScrollBar widget (now thumb-capped
# above) -- the AdvScrollBar texture set degrades visually on the short
# tracks this panel uses, so the code-drawn look is preferred here.
# ---------------------------------------------------------------------------
if app.ENABLE_WIKI_REDESIGN:
	_ORIGIN_ROW_PAD       = 4
	_ORIGIN_MARK_PATH     = ASSET_ROOT + "mark_right.png"
	_ORIGIN_MARK_W        = 22
	_ORIGIN_MARK_H        = 13
	_ORIGIN_MARK_TEXT_GAP = 4

	def _ApplyOriginRowAlign(originInfo, tmp):
		if not tmp or not hasattr(tmp, "txt"):
			return
		try:
			rowWidth  = tmp.GetWidth()
			rowHeight = tmp.GetHeight()
			y         = tmp.txt.GetLocalPosition()[1]

			# Build the mark icon once per row. _ApplyOriginRowAlign is
			# also called from the ChangeScrollbar re-align hook, so we
			# guard with an attribute to avoid stacking copies.
			# NB: ExpandedImageBox (not plain ImageBox) -- only the
			# Expanded variant honors SetSubClippingMaskWindow in this
			# engine, which we need so rows scrolled past the visible
			# peekWindow don't bleed their marks into adjacent panels.
			mark = getattr(tmp, "_mark_img", None)
			if mark is None:
				mark = ui.ExpandedImageBox()
				mark.SetParent(tmp)
				mark.AddFlag("not_pick")
				mark.LoadImage(_ORIGIN_MARK_PATH)
				if app.USE_CLIP_MASK and hasattr(originInfo, "peekWindow"):
					try:
						mark.SetSubClippingMaskWindow(originInfo.peekWindow)
					except Exception:
						pass
				mark.Show()
				tmp._mark_img = mark

			mark_y       = max(0, (rowHeight - _ORIGIN_MARK_H) / 2)
			text_offset  = _ORIGIN_MARK_W + _ORIGIN_MARK_TEXT_GAP

			tmp.txt.SetHorizontalAlignLeft()
			if localeinfo.IsARABIC():
				# RTL: icon hugs the right edge; text anchors just to
				# its left and glyphs grow further left (AlignLeft on
				# a right-edge anchor per project memory).
				mark.SetPosition(rowWidth - _ORIGIN_MARK_W - _ORIGIN_ROW_PAD, mark_y)
				tmp.txt.SetPosition(rowWidth - _ORIGIN_ROW_PAD - text_offset, y)
			else:
				# LTR: icon at left edge, text after the icon.
				mark.SetPosition(_ORIGIN_ROW_PAD, mark_y)
				tmp.txt.SetPosition(_ORIGIN_ROW_PAD + text_offset, y)
		except Exception:
			pass

	# Origin-tag prefixes added by WikiItemOriginInfo.ParseTextlines.
	# Stripped from list-card embedded drops-from rows (chest list,
	# boss list, etc.) but kept on the main SpecialPage drops-from
	# panel. The widget tells which context it's in by self.parent:
	# embedded uses pass _parent=parent, main page passes None.
	_ORIGIN_TAG_PREFIXES = [
		getattr(localeinfo, "WIKI_ORIGIN_MONSTER_TAG", ""),
		getattr(localeinfo, "WIKI_ORIGIN_CHEST_TAG",   ""),
		getattr(localeinfo, "WIKI_ORIGIN_SHOP_TAG",    ""),
		getattr(localeinfo, "WIKI_ORIGIN_CUBE_TAG",    ""),
	]
	_ORIGIN_TAG_PREFIXES = [t for t in _ORIGIN_TAG_PREFIXES if t]

	def _StripOriginTag(text):
		try:
			s = text
			for prefix in _ORIGIN_TAG_PREFIXES:
				if s.startswith(prefix):
					return s[len(prefix):].lstrip()
			return s
		except Exception:
			return text

	_origOriginAddItem = _legacyWiki.WikiItemOriginInfo.AddItem
	def _OriginAddItemRedesign(self, text, *a, **kw):
		# Strip the [MONSTER]/[CHEST]/[SHOP]/[CUBE] prefix when this
		# widget is embedded inside a list card (parent is set). Main
		# SpecialPage drops-from panel (parent is None) keeps them.
		if getattr(self, "parent", None) is not None:
			text = _StripOriginTag(text)
		tmp = _origOriginAddItem(self, text, *a, **kw)
		_ApplyOriginRowAlign(self, tmp)
		return tmp
	_legacyWiki.WikiItemOriginInfo.AddItem = _OriginAddItemRedesign

	# ChangeScrollbar re-centers row text whenever the bar transitions from
	# hidden to shown (legacy line 4709). Re-align after that re-layout so
	# our left-alignment survives the first scrollbar appearance.
	_origOriginChangeScrollbar = _legacyWiki.WikiItemOriginInfo.ChangeScrollbar
	def _OriginChangeScrollbarRedesign(self):
		_origOriginChangeScrollbar(self)
		try:
			for tmp in self.elements.values():
				_ApplyOriginRowAlign(self, tmp)
		except Exception:
			pass
	_legacyWiki.WikiItemOriginInfo.ChangeScrollbar = _OriginChangeScrollbarRedesign

	# Reverse-lookup panels (no-content item page bottom row) get the
	# same row treatment -- AlignLeft text anchored at the row edge plus
	# a mark_right.png arrow icon. _ApplyOriginRowAlign works as-is
	# because both row types expose .txt and the parent has .peekWindow.
	# .elements is a list here (vs a dict on WikiItemOriginInfo), so we
	# iterate it directly.
	_origReverseSetRows = _legacyReverse.WikiReverseLookupPanel.SetRows
	def _ReverseSetRowsRedesign(self, rows, isMonster=False):
		_origReverseSetRows(self, rows, isMonster)
		try:
			for row in self.elements:
				_ApplyOriginRowAlign(self, row)
		except Exception:
			pass
	_legacyReverse.WikiReverseLookupPanel.SetRows = _ReverseSetRowsRedesign
