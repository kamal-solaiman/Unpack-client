# coding: latin_1
#
# Reverse-lookup panels for the wiki item detail page (no-content fallback).
# For materials / consumables / ingredients (items that aren't weapons, armor,
# or chests), the wiki used to show a mostly-empty bottom half. Now it shows
# three columns -- all three list ITEMS (not NPCs), all answer "what does
# this item LEAD to":
#   - "Used for Refining"   (output items whose refine recipe uses this item)
#   - "Used for Crafting"   (output items whose cube recipe uses this item)
#   - "Used for Purchase"   (items that can be bought USING this item as currency)
#
# Column titles are embedded in detail_itemnocontent2.png by the bg artist --
# the panel widget does NOT draw any header text.
#
# Data sources for v1:
#   - Crafting:  game_data.craftingDict (already shipped via cl_craft_item.json)
#   - Purchase:  game_data.shopDict     (already shipped via shops.txt)
#                Walks each shop entry's currency list (entry[3]) and indexes
#                the SOLD item against every non-yang currency vnum.
#   - Refining:  NOT WIRED -- refine_proto is DB-only today; will populate after
#                refine_proto.txt migration. Left as an empty placeholder column.

import app

if app.ENABLE_INGAME_WIKI:
	import ui
	import item as itemModule
	import nonplayer
	import player
	import wiki as wikiModule
	import localeinfo
	import game_data
	import uitooltip


	# ----------------------------------------------------------------
	# Tunables
	# ----------------------------------------------------------------

	# Space reserved at the top of each panel for the title text that's
	# embedded in the bg image (detail_itemnocontent2.png). Rows start
	# immediately below this band.
	PANEL_TOP_PAD			= 22
	PANEL_BOTTOM_PAD		= 4
	PANEL_ROW_HEIGHT		= 16
	PANEL_ROW_PAD			= 4

	# Scrollbar geometry. Matches the existing WikiScrollBar style used by
	# WikiItemOriginInfo so the look feels consistent.
	SCROLLBAR_WIDTH			= 7
	SCROLL_SPEED			= 25

	# ----------------------------------------------------------------
	# Colors
	# ----------------------------------------------------------------

	COL_ROW_TEXT			= 0xFFD0D0D0	# soft white
	COL_ROW_TEXT_HOVER		= 0xFFFFE066	# yellow on hover (matches search match)
	COL_EMPTY_TEXT			= 0xFF808080	# dim grey for empty / "(coming soon)"
	COL_HINT_TEXT			= 0xFFB0B0B0	# slightly brighter grey for tooltip footer hint

	# ----------------------------------------------------------------
	# Tooltip modes
	# ----------------------------------------------------------------
	#
	# Refine + Crafting columns show the full item tooltip (icon, name,
	# stats) of whatever item the row points to. The Shop column will use
	# a different mode (TBD by user) -- that's why this is configurable
	# per panel via SetTooltipMode().

	TOOLTIP_MODE_ITEM		= "item"
	TOOLTIP_MODE_NONE		= "none"


	# ================================================================
	# Module-level reverse-index cache
	# ================================================================
	#
	# Built lazily on first access. Pure-Python scans of dicts already
	# loaded by game_data.Load(), so no network or disk i/o.

	_cubeReverseIndex = None		# material_vnum  -> [output_vnum, ...]
	_shopReverseIndex = None		# currency_vnum  -> [sold_item_vnum, ...]
	_bundleReverseIndex = None		# item_vnum      -> [box_vnum, ...]


	def _BuildCubeReverseIndex():
		global _cubeReverseIndex
		if _cubeReverseIndex is not None:
			return _cubeReverseIndex

		idx = {}
		# craftingDict layout (per cl_craft_item.json):
		#   { npc_vnum: { recipe_idx: { 'material_list': [v,c,v,c,...],
		#                               'reward_item':   [v, c], ... } } }
		for npc_vnum, recipes in (getattr(game_data, "craftingDict", {}) or {}).items():
			if not isinstance(recipes, dict):
				continue
			for recipe in recipes.values():
				if not isinstance(recipe, dict):
					continue
				reward = recipe.get("reward_item")
				if not reward:
					continue
				try:
					output_vnum = int(reward[0])
				except (TypeError, ValueError, IndexError):
					continue
				if not output_vnum:
					continue
				mat_list = recipe.get("material_list") or []
				# Walk in pairs (vnum, count). Index the OUTPUT against each material.
				for i in range(0, len(mat_list), 2):
					try:
						mat_vnum = int(mat_list[i])
					except (TypeError, ValueError, IndexError):
						continue
					if not mat_vnum:
						continue
					bucket = idx.setdefault(mat_vnum, [])
					if output_vnum not in bucket:
						bucket.append(output_vnum)

		_cubeReverseIndex = idx
		return idx


	def _BuildShopReverseIndex():
		# Index: currency_vnum -> [sold_item_vnums...]
		# i.e. "what items can be bought USING this item as currency".
		#
		# Shop entry layout from shops.txt:
		#   [sold_item_vnum, count, price_type, [[currency_vnum, price], ...]]
		# When currency_vnum is 0, the payment is yang (gold) -- we skip it.
		# Any non-zero currency_vnum is an item vnum acting as currency, and
		# the sold item is indexed against it.
		global _shopReverseIndex
		if _shopReverseIndex is not None:
			return _shopReverseIndex

		idx = {}
		for npc_vnum, shops in (getattr(game_data, "shopDict", {}) or {}).items():
			if not isinstance(shops, dict):
				continue
			for tab in shops.values():
				if not isinstance(tab, dict):
					continue
				items = tab.get("items") or []
				for entry in items:
					if not entry or len(entry) < 4:
						continue
					try:
						sold_vnum = int(entry[0])
					except (TypeError, ValueError, IndexError):
						continue
					if not sold_vnum:
						continue
					price_list = entry[3] or []
					for price_entry in price_list:
						if not price_entry:
							continue
						try:
							currency_vnum = int(price_entry[0])
						except (TypeError, ValueError, IndexError):
							continue
						# 0 = yang; not item-as-currency.
						if currency_vnum <= 0:
							continue
						bucket = idx.setdefault(currency_vnum, [])
						if sold_vnum not in bucket:
							bucket.append(sold_vnum)

		_shopReverseIndex = idx
		return idx


	def GetCubeUsages(vnum):
		"""Items whose cube recipe uses this vnum as a material."""
		try:
			return list(_BuildCubeReverseIndex().get(int(vnum), []))
		except (TypeError, ValueError):
			return []


	def GetPurchasableWith(vnum):
		"""Items that can be bought using this vnum as currency."""
		try:
			return list(_BuildShopReverseIndex().get(int(vnum), []))
		except (TypeError, ValueError):
			return []


	def GetRefineUsages(vnum):
		"""Items whose refine recipe uses this vnum as a material.
		   Backed by game_data.refineReverseDict, which is populated only
		   when USE_REFINE_PROTO_TXT is enabled AND the baker has produced
		   cl_refine_reverse.json. With the flag off, returns []."""
		if not app.USE_REFINE_PROTO_TXT:
			return []
		try:
			return list(getattr(game_data, "refineReverseDict", {}).get(int(vnum), []))
		except (TypeError, ValueError):
			return []


	def _BuildBundleReverseIndex():
		global _bundleReverseIndex
		if _bundleReverseIndex is not None:
			return _bundleReverseIndex

		idx = {}
		# bundleBoxDict layout (per cl_bundle_box.json, Task 6 bake):
		#   { box_vnum: {"categories": [{"items": [[vnum,count,sex,job], ...], ...}, ...],
		#                "guaranteed": [[vnum,count], ...]} }
		# Index every item vnum that can come OUT of a box (category picks
		# union guaranteed rolls) against that box's vnum.
		for box_vnum, data in (getattr(game_data, "bundleBoxDict", {}) or {}).items():
			if not isinstance(data, dict):
				continue
			seen = {}
			for cat in (data.get("categories") or []):
				if not isinstance(cat, dict):
					continue
				for row in (cat.get("items") or []):
					if not row:
						continue
					try:
						seen[int(row[0])] = 1
					except (TypeError, ValueError, IndexError):
						continue
			for row in (data.get("guaranteed") or []):
				if not row:
					continue
				try:
					seen[int(row[0])] = 1
				except (TypeError, ValueError, IndexError):
					continue

			try:
				box_vnum_i = int(box_vnum)
			except (TypeError, ValueError):
				continue
			for item_vnum in seen.keys():
				bucket = idx.setdefault(item_vnum, [])
				if box_vnum_i not in bucket:
					bucket.append(box_vnum_i)

		_bundleReverseIndex = idx
		return idx


	def GetBundleSources(vnum):
		"""Bundle-box vnums that can hand out this item (category pick or
		   guaranteed roll)."""
		try:
			return list(_BuildBundleReverseIndex().get(int(vnum), []))
		except (TypeError, ValueError):
			return []


	# ================================================================
	# Hover tooltip
	# ================================================================
	#
	# Tiny popup shown while hovering a reverse-lookup row. We deliberately
	# DO NOT use uitooltip.ItemToolTip here -- that renders the full stats
	# tooltip with no icon, which is exactly the wrong tradeoff for this
	# spot (the player is on the wiki to browse; they don't need the full
	# stats blob, they need a quick visual ID + a clickability cue).
	#
	# Layout:
	#   +----------------+
	#   |     [icon]     |
	#   |   item name    |
	#   | Open Wikipedia |
	#   +----------------+

	class WikiHoverTip(uitooltip.ToolTip):
		WIDTH				= 150
		TOP_PAD				= 6

		def __init__(self):
			uitooltip.ToolTip.__init__(self, self.WIDTH)

		def SetItemVnum(self, vnum):
			"""Populate with the given item's icon + name + click hint.
			Caller is responsible for ShowToolTip()/HideToolTip()."""
			self.ClearToolTip()
			try:
				itemModule.SelectItem(int(vnum))
				iconPath = itemModule.GetIconImageFileName()
				name = itemModule.GetItemName() or ("#%d" % vnum)
			except Exception:
				return False

			# Icon, centered. The image's intrinsic dimensions drive layout
			# (jewelry icons are 32x32, armor/weapons are 32x64, etc).
			if iconPath:
				self.AppendSpace(self.TOP_PAD)
				icon = ui.ImageBox()
				icon.SetParent(self)
				icon.LoadImage(iconPath)
				iconW = icon.GetWidth() or 32
				iconH = icon.GetHeight() or 32
				icon.SetPosition((self.toolTipWidth - iconW) / 2, self.toolTipHeight)
				icon.Show()
				self.childrenList.append(icon)
				self.toolTipHeight += iconH
				self.ResizeToolTip()

			# Item name (uses the tooltip base's default FONT_COLOR + center
			# alignment so it follows the project's tooltip styling).
			self.AppendSpace(4)
			self.AppendTextLine(name)

			# Footer: "Open Wikipedia" in a dimmer color.
			self.AppendSpace(2)
			self.AppendTextLine(localeinfo.WIKI_OPEN_HINT, COL_HINT_TEXT)
			return True

		def SetTextBlock(self, title, lines):
			"""Populate with a plain text block. Used by rows that describe an
			upgrade STEP rather than an item, so there is no icon to show."""
			self.ClearToolTip()
			self.AppendSpace(self.TOP_PAD / 2)
			self.AppendTextLine(title, COL_ROW_TEXT_HOVER)
			for (text, dim) in (lines or []):
				self.AppendTextLine(text, COL_HINT_TEXT if dim else COL_ROW_TEXT)
			return True


	# ================================================================
	# Reverse-lookup panel widget
	# ================================================================

	class WikiReverseLookupPanel(ui.Window):
		"""One column of the item detail page's bottom row. A scrollable list
		of item names. Click a row to navigate to that item's wiki page.

		No header text -- titles are part of the bg image
		(detail_itemnocontent2.png)."""

		def __init__(self, width, height):
			ui.Window.__init__(self)
			self.SetSize(int(width), int(height))

			self.elements = []
			# row index -> zero-arg callable. Kept off the event system because
			# __mem_func__ cannot carry a callable argument.
			self._rowActions = {}
			# row index -> (title, [(text, dim), ...]) for rows that describe an
			# upgrade step instead of an item, so there is no vnum to preview.
			self._rowTips = {}
			self.entryWidth = int(width) - SCROLLBAR_WIDTH - 4

			# Visible / clip area below the bg's embedded title band.
			self.peekWindow = ui.Window()
			self.peekWindow.SetParent(self)
			self.peekWindow.AddFlag("attach")
			self.peekWindow.AddFlag("not_pick")
			self.peekWindow.SetSize(self.entryWidth, int(height) - PANEL_TOP_PAD - PANEL_BOTTOM_PAD)
			self.peekWindow.SetPosition(2, PANEL_TOP_PAD)

			if not app.USE_CLIP_MASK:
				self.peekWindow.SetInsideRender(True)

			self.peekWindow.Show()

			# Content area; can extend beyond peekWindow's height. Rows live
			# on this. The scrollbar moves it vertically by changing its Y.
			self.scrollBoard = ui.Window()
			self.scrollBoard.SetParent(self.peekWindow)
			self.scrollBoard.AddFlag("attach")
			self.scrollBoard.AddFlag("not_pick")
			if app.USE_CLIP_MASK:
				self.scrollBoard.SetClippingMaskWindow(self.peekWindow)
			self.scrollBoard.Show()

			# Empty / placeholder text shown when there are zero rows.
			self.placeholder = ui.TextLine()
			self.placeholder.SetParent(self.peekWindow)
			self.placeholder.AddFlag("not_pick")
			self.placeholder.SetHorizontalAlignCenter()
			self.placeholder.SetPosition(self.entryWidth / 2, 6)
			self.placeholder.SetPackedFontColor(COL_EMPTY_TEXT)
			self.placeholder.Hide()

			# Scrollbar lives on the right side. Created lazily on first row
			# fill (avoids importing ingamewikiui at module-load time -- that
			# would be a circular dependency).
			self.scrollBar = None

			# Hover tooltip shown when the cursor is over a row. WikiHoverTip
			# is a top-level window (not a child of `self`) so positioning +
			# cursor-follow work even when the cursor is near the panel edge.
			# Mode controls what gets rendered; default = the same icon +
			# name + "Open Wikipedia" layout for every column (refine, cube,
			# shop). The mode hook remains so a future shop spec can swap in
			# a richer layout without touching the row plumbing.
			self.tooltipMode = TOOLTIP_MODE_ITEM
			self.toolTip = WikiHoverTip()
			self.toolTip.Hide()

		def __del__(self):
			ui.Window.__del__(self)

		# ------------------------------------------------------------
		# Public API
		# ------------------------------------------------------------

		def SetEmptyPlaceholder(self, text):
			"""Configure the text shown when the panel has zero rows."""
			self.placeholder.SetText(text or "")

		def SetTooltipMode(self, mode):
			"""Switch which tooltip the panel shows on row hover.
			   TOOLTIP_MODE_ITEM = full item tooltip (default, used by
			       refine + crafting columns).
			   TOOLTIP_MODE_NONE = no hover tooltip."""
			self.tooltipMode = mode
			self._HideTooltip()

		def SetItems(self, vnums, isMonster = False):
			"""Populate with a list of clickable rows for these vnums.
			isMonster=True if rows are mob/npc names; default False (items)."""
			rows = []
			for vnum in (vnums or []):
				try:
					vnum_i = int(vnum)
				except (TypeError, ValueError):
					continue
				rows.append((self._ResolveName(vnum_i, isMonster), vnum_i, None))

			# self.SetRows, not SetRows -- the redesign layer monkeypatches the
			# method, so the call has to go through the instance.
			self.SetRows(rows, isMonster)

		def SetRows(self, rows, isMonster = False):
			"""Populate with pre-labelled rows:
			[(label, vnum, click_action, tip_lines), ...] -- the last two optional.
			`vnum` drives the hover tooltip and the default click (that item's wiki
			page); `click_action`, when given, replaces the click entirely;
			`tip_lines` ([(text, dim), ...]), when given, replaces the item
			tooltip with a text block (rows that describe a step, not an item)."""
			self._ClearRows()

			if not rows:
				self.placeholder.Show()
				self._UpdateScrollBar()
				return

			for row_data in rows:
				if not row_data:
					continue

				label = row_data[0]
				try:
					vnum_i = int(row_data[1]) if len(row_data) > 1 else 0
				except (TypeError, ValueError):
					vnum_i = 0
				action = row_data[2] if len(row_data) > 2 else None
				tipLines = row_data[3] if len(row_data) > 3 else None

				# Index off self.elements, not enumerate() -- a skipped row would
				# otherwise slide every later row's hover index out of step with
				# the list _OnRowOver indexes into.
				i = len(self.elements)
				if action is not None:
					self._rowActions[i] = action
				if tipLines is not None:
					self._rowTips[i] = (label, tipLines)

				row = ui.Window()
				row.SetParent(self.scrollBoard)
				# Full-width row inside the peekWindow (mirrors
				# WikiItemOriginInfo.AddItem so Arabic centers correctly).
				row.SetSize(self.entryWidth, PANEL_ROW_HEIGHT)
				row.SetPosition(0, i * PANEL_ROW_HEIGHT)

				row.txt = ui.TextLine()
				row.txt.SetParent(row)
				row.txt.AddFlag("not_pick")
				row.txt.SetText(label)
				row.txt.SetPackedFontColor(COL_ROW_TEXT)
				# Center alignment renders correctly in both LTR (en) and
				# RTL (ae) locales. Left/default anchors render Arabic
				# off-screen to the left of x=2.
				row.txt.SetHorizontalAlignCenter()
				row.txt.SetPosition(row.GetWidth() / 2, 0)
				if app.USE_CLIP_MASK:
					row.txt.SetSubClippingMaskWindow(self.peekWindow)
				row.txt.Show()

				# NB: SetOverInEvent / SetOverOutEvent, not the "Mouse" prefixed
				# variants. The base ui.Window.OnMouseOverIn dispatches via the
				# `overInEvent` slot (Set*Mouse*OverInEvent stores into a
				# different slot that the base class never reads).
				row.SetOverInEvent(ui.__mem_func__(self._OnRowOver),  i, True,  vnum_i)
				row.SetOverOutEvent(ui.__mem_func__(self._OnRowOver), i, False, vnum_i)
				row.SetMouseLeftButtonDownEvent(
					ui.__mem_func__(self._OnRowClick), i, vnum_i, isMonster)

				row.Show()
				self.elements.append(row)

			self.scrollBoard.SetSize(self.entryWidth, len(self.elements) * PANEL_ROW_HEIGHT)
			self._UpdateScrollBar()

		# ------------------------------------------------------------
		# Internals
		# ------------------------------------------------------------

		def _ResolveName(self, vnum, isMonster):
			if isMonster:
				try:
					return nonplayer.GetMonsterName(vnum) or ("#%d" % vnum)
				except Exception:
					return "#%d" % vnum
			try:
				itemModule.SelectItem(vnum)
				return itemModule.GetItemName() or ("#%d" % vnum)
			except Exception:
				return "#%d" % vnum

		def _ClearRows(self):
			for row in self.elements:
				try:
					row.SetMouseLeftButtonDownEvent(None)
					row.SetOverInEvent(None)
					row.SetOverOutEvent(None)
				except Exception:
					pass
				try:
					row.Hide()
				except Exception:
					pass
			self.elements = []
			self._rowActions = {}
			self._rowTips = {}
			self.placeholder.Hide()
			self.scrollBoard.SetSize(0, 0)
			self.scrollBoard.SetPosition(0, 0)
			# Tear down any tooltip leftover from the previous fill -- otherwise
			# a tooltip from a stale row could stay on-screen while we repopulate.
			self._HideTooltip()

		# ------------------------------------------------------------
		# Scrollbar (lazy)
		# ------------------------------------------------------------

		def _EnsureScrollBar(self):
			if self.scrollBar is not None:
				return
			# Lazy import: ingamewikiui defines WikiScrollBar near the top
			# and is fully loaded by the time SpecialPageWindow instantiates
			# us (SpecialPageWindow.__init__ does `import ingamewikireverse`
			# itself, so we're past module init by now).
			import ingamewikiui
			self.scrollBar = ingamewikiui.WikiScrollBar()
			self.scrollBar.SetParent(self)
			self.scrollBar.SetPosition(self.GetWidth() - SCROLLBAR_WIDTH - 2, PANEL_TOP_PAD)
			self.scrollBar.SetSize(SCROLLBAR_WIDTH, self.peekWindow.GetHeight())
			self.scrollBar.SetScrollEvent(self.OnScrollBar)
			self.scrollBar.SetScrollSpeed(SCROLL_SPEED)

		def _UpdateScrollBar(self):
			# Show/hide + size the scrollbar based on whether content overflows
			# the visible peekWindow. Same math the existing WikiItemOriginInfo
			# uses.
			self._EnsureScrollBar()
			if not self.scrollBar:
				return

			visibleH = self.peekWindow.GetHeight()
			contentH = self.scrollBoard.GetHeight()

			if contentH <= visibleH:
				self.scrollBar.Hide()
				return

			from operator import truediv
			self.scrollBar.SetScale(visibleH, contentH)
			boardY = self.scrollBoard.GetLocalPosition()[1]
			self.scrollBar.SetPosScale(truediv(abs(boardY), (contentH - visibleH)))
			self.scrollBar.Show()

		def OnScrollBar(self, fScale):
			# Drag callback from WikiScrollBar. Translate fScale in [0, 1] into
			# a Y offset on scrollBoard.
			visibleH = self.peekWindow.GetHeight()
			contentH = self.scrollBoard.GetHeight()
			if contentH <= visibleH:
				return
			curr = min(0, max(int((contentH - visibleH) * fScale * -1.0),
			                  -contentH + visibleH))
			self.scrollBoard.SetPosition(0, curr)

		def OnRunMouseWheel(self, length):
			# Wheel handler. The engine invokes this with `length` = raw
			# Windows wheel delta (+120 per notch up, -120 per notch down).
			# Same scaling factor (length * 0.01 * SCROLL_SPEED) the existing
			# WikiItemOriginInfo uses so wheel feel matches across the wiki.
			# Returns True to consume the event; False lets it bubble to the
			# parent (so the wiki's outer scroll still works when the mouse
			# is outside our peekWindow).
			if not self.scrollBar or not self.scrollBar.IsShow():
				return False
			if not self.peekWindow.IsInPosition():
				return False
			self._ScrollByDelta(int((length * 0.01) * SCROLL_SPEED))
			return True

		def _ScrollByDelta(self, delta):
			# Move scrollBoard by `delta` px (positive = scroll content up,
			# i.e. board Y increases toward 0). Clamps to [-overflow, 0] and
			# re-syncs the scrollbar handle to the new position.
			visibleH = self.peekWindow.GetHeight()
			contentH = self.scrollBoard.GetHeight()
			if contentH <= visibleH:
				return
			boardY = self.scrollBoard.GetLocalPosition()[1]
			curr = min(0, max(boardY + delta, -contentH + visibleH))
			if curr == boardY:
				return
			self.scrollBoard.SetPosition(0, curr)
			from operator import truediv
			self.scrollBar.SetPosScale(truediv(abs(curr), (contentH - visibleH)))

		# ------------------------------------------------------------
		# Row events
		# ------------------------------------------------------------

		def _OnRowOver(self, idx, hovering, vnum):
			if idx < 0 or idx >= len(self.elements):
				return
			row = self.elements[idx]
			try:
				row.txt.SetPackedFontColor(COL_ROW_TEXT_HOVER if hovering else COL_ROW_TEXT)
			except AttributeError:
				pass

			if hovering:
				self._ShowTooltip(idx, vnum)
			else:
				self._HideTooltip()

		def _OnRowClick(self, idx, vnum, isMonster):
			action = self._rowActions.get(idx)
			if action:
				action()
				return

			if not vnum:
				return

			wikiBase = wikiModule.GetBaseClass()
			if not wikiBase:
				return
			try:
				wikiBase.OpenSpecialPage(None, int(vnum), bool(isMonster))
			except Exception:
				pass

		# ------------------------------------------------------------
		# Tooltip
		# ------------------------------------------------------------

		def _ShowTooltip(self, idx, vnum):
			"""Populate + show the hover tooltip for the given row, picking
			the layout dictated by self.tooltipMode."""
			if not self.toolTip or self.tooltipMode == TOOLTIP_MODE_NONE:
				return
			if idx in self._rowTips:
				(title, lines) = self._rowTips[idx]
				self.toolTip.SetTextBlock(title, lines)
				self.toolTip.ShowToolTip()
				return
			if self.tooltipMode == TOOLTIP_MODE_ITEM:
				self._BuildItemTooltip(vnum)
			# Other modes (shop, ...) wired in once spec lands.

		def _BuildItemTooltip(self, vnum):
			# Compact icon + name + "Open Wikipedia" hint. Implementation
			# lives in WikiHoverTip; we just feed it the vnum and reveal.
			if not self.toolTip.SetItemVnum(vnum):
				self._HideTooltip()
				return
			self.toolTip.ShowToolTip()

		def _HideTooltip(self):
			if not self.toolTip:
				return
			try:
				self.toolTip.HideToolTip()
			except AttributeError:
				try:
					self.toolTip.Hide()
				except Exception:
					pass
