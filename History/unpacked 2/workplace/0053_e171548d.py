# coding: latin_1

import app

if app.ENABLE_INGAME_WIKI:
	import ui
	import grp
	import item as itemModule
	import wiki as wikiModule
	import localeinfo
	import ingamewikiconfig


	# ----------------------------------------------------------------
	# Tunables
	# ----------------------------------------------------------------

	SEARCH_ROW_HEIGHT		= 15
	SEARCH_HEADER_HEIGHT	= 16
	SEARCH_MAX_VISIBLE_ROWS	= 10
	SEARCH_RESULT_CAP		= 40
	SEARCH_MIN_QUERY		= 1

	ROW_PAD					= 8

	# ----------------------------------------------------------------
	# Colors
	# ----------------------------------------------------------------

	# Dropdown body: near-opaque dark.
	COL_BACKGROUND			= 0xF0181818

	# Section header: dark band with a subtle warm tone, gold text.
	COL_HEADER_BAND			= 0xFF2C211B
	COL_HEADER_TEXT			= 0xFFE6B450

	# Result row hover: subtle blue tint that stays readable behind white text.
	COL_ROW_HOVER			= 0x70304870

	# Result row text.
	COL_NAME				= 0xFFFFFFFF
	COL_MATCH				= 0xFFFFE066	# yellow highlight on the matched substring
	COL_FOOTER				= 0xFFA8A8A8


	# ================================================================
	# Section header row
	# ================================================================

	class WikiSearchSectionHeader(ui.ListBoxEx.Item):
		# Non-clickable section divider rendered inside the same ListBoxEx as
		# result rows. The "Items" / "Monsters" band that groups results.

		def __init__(self):
			ui.ListBoxEx.Item.__init__(self)

			# Children must be not_pick so clicks fall through to the header
			# itself -- without this, the engine's recursive PickWindow returns
			# the band/label (a pickable child with no handler) and the
			# header's OnMouseLeftButtonDown never fires.
			self.band = ui.Bar()
			self.band.SetParent(self)
			self.band.AddFlag("not_pick")
			self.band.SetPosition(0, 0)
			self.band.SetColor(COL_HEADER_BAND)
			self.band.Show()

			self.label = ui.TextLine()
			self.label.SetParent(self)
			self.label.AddFlag("not_pick")
			self.label.SetHorizontalAlignCenter()
			self.label.SetPackedFontColor(COL_HEADER_TEXT)
			self.label.Show()

		def SetSectionLabel(self, text, rowWidth):
			self.label.SetText(text or "")
			self.band.SetSize(int(rowWidth), SEARCH_HEADER_HEIGHT)
			self.label.SetPosition(int(rowWidth) / 2, 1)

		def OnMouseLeftButtonDown(self):
			# Pure divider; consume the click silently so the listbox never
			# selects a header.
			pass

		def OnMouseOverIn(self):
			# Don't show any hover state.
			pass

		def OnMouseOverOut(self):
			pass

		def OnRender(self):
			# Skip the inherited selected-state highlight bar.
			pass

		def IsHeader(self):
			return True


	# ================================================================
	# Result row
	# ================================================================

	class WikiSearchResultRow(ui.ListBoxEx.Item):
		# A single clickable search result. The section header above the rows
		# indicates type, so the row itself shows just the name (with the
		# matched query substring highlighted on LTR locales).
		#
		# Highlight state is owned by the parent WikiSearchResults so that
		# arrow-key navigation and mouse hover share one source of truth.
		# Each row keeps a back-reference (self.owner) and routes
		# OnMouseOverIn through it. OnMouseOverOut is a no-op so the
		# highlight stays "sticky" after the mouse leaves -- otherwise the
		# row that the keyboard moved to would un-highlight when the cursor
		# drifts.

		def __init__(self):
			ui.ListBoxEx.Item.__init__(self)
			self.vnum  = 0
			self.isMob = False
			self.name = ""
			self.rowWidth = 0
			self.owner = None

			# Highlight bar -- shown when this row is the current highlight
			# (either via keyboard nav or mouse hover). Drawn behind the
			# text because Bar is added before the TextLines.
			#
			# Every child must be not_pick so mouse clicks fall through to the
			# row's own OnMouseLeftButtonDown (inherited from ListBoxEx.Item,
			# which calls self.parent.SelectItem). Without not_pick, the
			# engine's recursive PickWindow returns whichever TextLine the
			# cursor lands on -- a pickable child with no handler -- and the
			# click silently no-ops. (Keyboard Tab/Enter bypass the click
			# path so they kept working; mouse picks were broken.)
			self.hoverBar = ui.Bar()
			self.hoverBar.SetParent(self)
			self.hoverBar.AddFlag("not_pick")
			self.hoverBar.SetPosition(0, 0)
			self.hoverBar.SetColor(COL_ROW_HOVER)
			self.hoverBar.Hide()

			self.namePre = ui.TextLine()
			self.namePre.SetParent(self)
			self.namePre.AddFlag("not_pick")
			self.namePre.Show()

			self.nameHit = ui.TextLine()
			self.nameHit.SetParent(self)
			self.nameHit.AddFlag("not_pick")
			self.nameHit.Show()

			self.namePost = ui.TextLine()
			self.namePost.SetParent(self)
			self.namePost.AddFlag("not_pick")
			self.namePost.Show()

		def SetRowWidth(self, w):
			self.rowWidth = int(w)
			self.hoverBar.SetSize(self.rowWidth, SEARCH_ROW_HEIGHT)

		def SetEntry(self, vnum, name, isMob, queryLower):
			self.vnum  = int(vnum)
			self.isMob = bool(isMob)
			self.name = name or ""
			self._Layout(name or "", queryLower)

		def _Layout(self, name, queryLower):
			if localeinfo.IsARABIC():
				# Arabic letters shape based on neighbors -- splitting the
				# word breaks the rendering. Single TextLine, right-aligned.
				self.namePre.SetText(name)
				self.namePre.SetPackedFontColor(COL_NAME)
				self.namePre.SetPosition(self.rowWidth - ROW_PAD, 1)
				self.namePre.SetHorizontalAlignLeft()

				self.nameHit.SetText("")
				self.namePost.SetText("")
				return

			# LTR: split the name so the matched substring can be highlighted.
			nameLower = name.lower()
			idx = nameLower.find(queryLower) if queryLower else -1

			if idx < 0:
				pre, hit, post = name, "", ""
			else:
				pre  = name[:idx]
				hit  = name[idx:idx + len(queryLower)]
				post = name[idx + len(queryLower):]

			self.namePre.SetText(pre)
			self.namePre.SetPackedFontColor(COL_NAME)

			self.nameHit.SetText(hit)
			self.nameHit.SetPackedFontColor(COL_MATCH)

			self.namePost.SetText(post)
			self.namePost.SetPackedFontColor(COL_NAME)

			self.namePre.SetPosition(ROW_PAD, 1)
			preW = self.namePre.GetTextSize()[0]
			self.nameHit.SetPosition(ROW_PAD + preW, 1)
			hitW = self.nameHit.GetTextSize()[0]
			self.namePost.SetPosition(ROW_PAD + preW + hitW, 1)

		def OnMouseOverIn(self):
			# Route highlight changes through the dropdown so keyboard nav
			# and mouse hover share one state.
			if self.owner is not None:
				self.owner._SetHighlightByRow(self)
			else:
				self.hoverBar.Show()

		def OnMouseOverOut(self):
			# Keep the highlight sticky: don't hide here. The dropdown's
			# _SetHighlightByRow / _SetHighlight is the only place that
			# moves the highlight.
			pass

		def ShowHighlight(self, on):
			if on:
				self.hoverBar.Show()
			else:
				self.hoverBar.Hide()

		def OnRender(self):
			# Suppress the inherited blue selection bar. The hoverBar is
			# the only row-level visual feedback we use.
			pass

		def GetVnum(self):
			return self.vnum

		def IsMob(self):
			return self.isMob

		def IsHeader(self):
			return False


	# ================================================================
	# Dropdown
	# ================================================================

	class WikiSearchResults(ui.ThinBoard):
		# Dropdown shown below the wiki search edit box.
		# Layout (matches the target design):
		#   +------------------------------------+
		#   |               Items                |   <- section header band
		#   |  Demon Blade+0                     |   <- result row, hover-highlighted
		#   |  Demon Fan+0                       |
		#   |  ...                               |
		#   |              Monsters              |   <- section header band
		#   |  Demon Soldier                     |
		#   |  ...                               |
		#   +------------------------------------+

		def __init__(self, width, itemsOnly=False):
			ui.ThinBoard.__init__(self)

			self.width = int(width)
			self.itemsOnly = itemsOnly
			self.onPickCallback = None
			self.itemIndex = None
			self.mobIndex = None
			self.lastQueryLower = ""

			# Keyboard / hover highlight state (single source of truth).
			self.highlightIndex = -1
			# Edge-detect arrow keys so a long-hold doesn't sprint through
			# the whole list in one frame.
			self.lastUpPressed   = False
			self.lastDownPressed = False

			# Provisional size; resized to fit content on Refresh.
			self.SetSize(self.width, SEARCH_ROW_HEIGHT * SEARCH_MAX_VISIBLE_ROWS + 22)

			# Opaque interior so the dropdown reads cleanly over the wiki page.
			self.backdrop = ui.Bar()
			self.backdrop.SetParent(self)
			self.backdrop.SetPosition(4, 4)
			self.backdrop.SetSize(self.width - 8, SEARCH_ROW_HEIGHT * SEARCH_MAX_VISIBLE_ROWS + 14)
			self.backdrop.SetColor(COL_BACKGROUND)
			self.backdrop.Show()

			self.listbox = ui.ListBoxEx()
			self.listbox.SetParent(self)
			# Listbox left edge matches backdrop left edge (x=4) so the row
			# hover bar reaches flush with the dropdown's interior fill --
			# otherwise a 2px dark sliver shows on each side of the highlight.
			#
			# Arabic shim: ListBoxEx.GetItemViewCoord offsets every row by
			# -10 px under ARABIC (ui.py: "self.GetWidth() - itemWidth - 10").
			# That margin is intended for right-aligned items inside a wider
			# listbox; with itemWidth == listbox width (our layout) it just
			# pushes the row 10 px left of the listbox origin and creates a
			# big dark sliver on the right. Shifting the listbox itself by
			# +10 px cancels the row offset so rows land flush at x=4 again.
			if localeinfo.IsARABIC():
				self.listbox.SetPosition(14, 6)
			else:
				self.listbox.SetPosition(4, 6)
			# SetItemSize / SetItemStep call __UpdateSize which uses
			# viewItemCount, so SetViewItemCount must come first.
			self.listbox.SetViewItemCount(SEARCH_MAX_VISIBLE_ROWS)
			self.listbox.SetItemStep(SEARCH_ROW_HEIGHT)
			self.listbox.SetItemSize(self.width - 8, SEARCH_ROW_HEIGHT)
			self.listbox.SetSelectEvent(ui.__mem_func__(self._OnRowSelect))
			self.listbox.Show()

			self.emptyLabel = ui.TextLine()
			self.emptyLabel.SetParent(self)
			self.emptyLabel.SetPosition(100, 8)
			self.emptyLabel.SetText(localeinfo.WIKI_SEARCH_NO_RESULTS)
			self.emptyLabel.SetPackedFontColor(COL_FOOTER)
			self.emptyLabel.Hide()

			self.footerLabel = ui.TextLine()
			self.footerLabel.SetParent(self)
			self.footerLabel.SetPackedFontColor(COL_FOOTER)
			self.footerLabel.Hide()

			self.Hide()

		def SetPickEvent(self, callback):
			self.onPickCallback = callback

		# ------------------------------------------------------------
		# Index build
		# ------------------------------------------------------------

		def _BuildIndexLazy(self):
			# Build item / mob lookup tables once, lazily. Both come from the
			# C++ wiki module (PythonWikiModule.cpp -- wikiGetItemList /
			# wikiGetMobList).
			if self.itemIndex is None:
				self.itemIndex = []
				itemBlacklist = set()
				for entry in getattr(ingamewikiconfig, "ITEM_BLACKLIST", []):
					# ITEM_BLACKLIST mixes plain ints with range() lists.
					try:
						for v in entry:
							itemBlacklist.add(int(v))
					except TypeError:
						try:
							itemBlacklist.add(int(entry))
						except (TypeError, ValueError):
							pass
				try:
					for entry in wikiModule.GetItemList():
						try:
							vnum = int(entry[0])
							name = entry[1] or ""
						except Exception:
							continue
						if not name or vnum in itemBlacklist:
							continue
						self.itemIndex.append((vnum, name, name.lower()))
				except Exception:
					pass

			if self.mobIndex is None and not self.itemsOnly:
				# Note: deliberately NOT applying MOB_WHITELIST here. The whitelist
				# is for the wiki's curated mob/boss/stone *category* pages -- when
				# a player searches, they should be able to find any mob that
				# exists, even if it's not in the curated category list (e.g.
				# event mobs, niche metin stones). Same reasoning as letting the
				# search box hit vnums directly.
				self.mobIndex = []
				try:
					for entry in wikiModule.GetMobList():
						try:
							vnum = int(entry[0])
							name = entry[1] or ""
						except Exception:
							continue
						if not name:
							continue
						self.mobIndex.append((vnum, name, name.lower()))
				except Exception:
					pass

		# ------------------------------------------------------------
		# Refresh
		# ------------------------------------------------------------

		def Refresh(self, query):
			query = (query or "").strip()
			self.lastQueryLower = query.lower()

			self.listbox.RemoveAllItems()
			self.emptyLabel.Hide()
			self.footerLabel.Hide()

			if len(query) < SEARCH_MIN_QUERY:
				self.Hide()
				return

			self._BuildIndexLazy()

			itemMatches = []   # list of (vnum, name)
			mobMatches  = []   # list of (vnum, name)
			totalFound  = 0

			if query.isdigit():
				vnumQ = int(query)
				for (vnum, name, _) in self.itemIndex or []:
					if vnum == vnumQ:
						itemMatches.append((vnum, name))
						break
				if not itemMatches:
					for (vnum, name, _) in self.mobIndex or []:
						if vnum == vnumQ:
							mobMatches.append((vnum, name))
							break
				totalFound = len(itemMatches) + len(mobMatches)
			else:
				q = self.lastQueryLower
				for (vnum, name, nameLower) in self.itemIndex or []:
					if q in nameLower:
						totalFound += 1
						if len(itemMatches) + len(mobMatches) < SEARCH_RESULT_CAP:
							itemMatches.append((vnum, name))
				for (vnum, name, nameLower) in self.mobIndex or []:
					if q in nameLower:
						totalFound += 1
						if len(itemMatches) + len(mobMatches) < SEARCH_RESULT_CAP:
							mobMatches.append((vnum, name))

				shownCount = len(itemMatches) + len(mobMatches)
				if totalFound > shownCount:
					self.footerLabel.SetText(localeinfo.WIKI_SEARCH_MORE_RESULTS % (totalFound - shownCount))
					self.footerLabel.SetPosition(100, SEARCH_ROW_HEIGHT * SEARCH_MAX_VISIBLE_ROWS + 6)
					self.footerLabel.SetHorizontalAlignCenter()
					self.footerLabel.Show()

			if not itemMatches and not mobMatches:
				self.emptyLabel.Show()
				self._ResizeForRows(0)
				self.Show()
				self.SetTop()
				return

			# Matches the listbox's item width (set in __init__) so the
			# hover bar and section header band span flush to the backdrop's
			# interior fill -- no dark slivers at the left/right edges.
			rowWidth = self.width - 8
			rowsAdded = 0
			firstResultIndex = -1

			if itemMatches:
				header = WikiSearchSectionHeader()
				header.SetSectionLabel(localeinfo.WIKI_SEARCH_SECTION_ITEMS, rowWidth)
				self.listbox.AppendItem(header)
				rowsAdded += 1
				for (vnum, name) in itemMatches:
					row = WikiSearchResultRow()
					row.owner = self
					row.SetRowWidth(rowWidth)
					row.SetEntry(vnum, name, False, self.lastQueryLower)
					self.listbox.AppendItem(row)
					if firstResultIndex < 0:
						firstResultIndex = rowsAdded
					rowsAdded += 1

			if mobMatches:
				header = WikiSearchSectionHeader()
				header.SetSectionLabel(localeinfo.WIKI_SEARCH_SECTION_MOBS, rowWidth)
				self.listbox.AppendItem(header)
				rowsAdded += 1
				for (vnum, name) in mobMatches:
					row = WikiSearchResultRow()
					row.owner = self
					row.SetRowWidth(rowWidth)
					row.SetEntry(vnum, name, True, self.lastQueryLower)
					self.listbox.AppendItem(row)
					if firstResultIndex < 0:
						firstResultIndex = rowsAdded
					rowsAdded += 1

			# Reset highlight then apply to the first result row. We don't
			# use ListBoxEx.SelectIndex because that fires onSelectItemEvent
			# which would trigger the pick callback on Refresh.
			self.highlightIndex = -1
			if firstResultIndex >= 0:
				self._SetHighlight(firstResultIndex)
			self._ResizeForRows(rowsAdded)
			self.Show()
			# Bring dropdown above sibling widgets (category sidebar, etc).
			self.SetTop()

		def _ResizeForRows(self, rowCount):
			visible = min(max(rowCount, 1), SEARCH_MAX_VISIBLE_ROWS)
			h = SEARCH_ROW_HEIGHT * visible + 12
			if self.footerLabel.IsShow():
				h += 14
			self.SetSize(self.width, h)
			self.backdrop.SetSize(self.width - 8, h - 8)

		# ------------------------------------------------------------
		# Highlight (keyboard nav + sticky mouse hover)
		# ------------------------------------------------------------

		def _GetItems(self):
			try:
				return self.listbox.itemList or []
			except Exception:
				return []

		def _IsHeader(self, item):
			try:
				return item.IsHeader()
			except AttributeError:
				return True

		def _SetHighlight(self, idx):
			items = self._GetItems()
			if not items:
				self.highlightIndex = -1
				return
			# Clear previous row's highlight, if any.
			prev = self.highlightIndex
			if 0 <= prev < len(items):
				try:
					items[prev].ShowHighlight(False)
				except AttributeError:
					pass
			# Show new highlight.
			if 0 <= idx < len(items) and not self._IsHeader(items[idx]):
				try:
					items[idx].ShowHighlight(True)
					self.highlightIndex = idx
					return
				except AttributeError:
					pass
			self.highlightIndex = -1

		def _SetHighlightByRow(self, row):
			items = self._GetItems()
			for i, it in enumerate(items):
				if it is row:
					self._SetHighlight(i)
					return

		def _MoveHighlight(self, delta):
			items = self._GetItems()
			if not items:
				return
			n = len(items)
			# Find the first valid (non-header) index by stepping `delta`
			# from the current highlight (or from -1/0 if no highlight yet).
			if self.highlightIndex < 0:
				start = -1 if delta > 0 else n
			else:
				start = self.highlightIndex
			for _ in range(n):
				start = (start + delta) % n
				if not self._IsHeader(items[start]):
					self._SetHighlight(start)
					return

		# ------------------------------------------------------------
		# Keyboard polling (arrow keys)
		# ------------------------------------------------------------

		def OnUpdate(self):
			# Only react while the dropdown is showing; otherwise we'd be
			# stealing arrow keys when the search edit isn't focused.
			if not self.IsShow():
				self.lastUpPressed   = False
				self.lastDownPressed = False
				return

			downNow = app.IsPressed(app.DIK_DOWN)
			if downNow and not self.lastDownPressed:
				self._MoveHighlight(1)
			self.lastDownPressed = downNow

			upNow = app.IsPressed(app.DIK_UP)
			if upNow and not self.lastUpPressed:
				self._MoveHighlight(-1)
			self.lastUpPressed = upNow

		# ------------------------------------------------------------
		# Selection / pick
		# ------------------------------------------------------------

		def _OnRowSelect(self, row):
			# Mouse-click on a row -- headers consume the click silently
			# (their OnMouseLeftButtonDown is a no-op) so this only ever
			# fires for a real result row.
			if row is None or self.onPickCallback is None:
				return
			try:
				if row.IsHeader():
					return
				self.onPickCallback(row.GetVnum(), row.IsMob())
			except AttributeError:
				return

		def GetTopPrefixCompletion(self):
			# Returns the full name of the first index entry whose lowercased
			# name starts with the last query, or None. Used by the wiki
			# search edit to render the inline ghost-text completion and to
			# resolve Tab -> autocomplete. Prefix-only (not substring) so the
			# ghost can be appended after what the user typed.
			if not self.lastQueryLower:
				return None
			self._BuildIndexLazy()
			q = self.lastQueryLower
			for (vnum, name, nameLower) in self.itemIndex or []:
				if nameLower.startswith(q):
					return name
			for (vnum, name, nameLower) in self.mobIndex or []:
				if nameLower.startswith(q):
					return name
			return None

		def GetHighlightedVnum(self):
			# vnum of the currently highlighted result row (0 if none). Used for Tab-fill.
			items = self._GetItems()
			if not items:
				return 0
			idx = self.highlightIndex
			if 0 <= idx < len(items) and not self._IsHeader(items[idx]):
				try:
					return items[idx].GetVnum()
				except AttributeError:
					return 0
			return 0

		def GetHighlightedName(self):
			# full name of the highlighted result row ("" if none). Used for Tab-fill.
			items = self._GetItems()
			if not items:
				return ""
			idx = self.highlightIndex
			if 0 <= idx < len(items) and not self._IsHeader(items[idx]):
				return getattr(items[idx], "name", "") or ""
			return ""

		def PickFirst(self):
			# Enter key from the search edit. Picks the currently
			# highlighted row, falling back to the first result if no
			# highlight is set (shouldn't happen after Refresh).
			if self.onPickCallback is None:
				return False
			items = self._GetItems()
			if not items:
				return False
			idx = self.highlightIndex
			if 0 <= idx < len(items) and not self._IsHeader(items[idx]):
				it = items[idx]
				try:
					self.onPickCallback(it.GetVnum(), it.IsMob())
					return True
				except AttributeError:
					pass
			# Fallback: first non-header row.
			for it in items:
				if it is None:
					continue
				try:
					if not it.IsHeader():
						self.onPickCallback(it.GetVnum(), it.IsMob())
						return True
				except AttributeError:
					continue
			return False
