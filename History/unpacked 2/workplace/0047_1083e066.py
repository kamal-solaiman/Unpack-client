# coding: latin_1
# -----------------------------------------------------------------------------
# Wiki Item Builder -- a dev/test authoring aid for [DOC] wiki pages.
#
# Reworked to a switchbot-style fixed-row editor: pick an item, then fill up to
# ATTR_SLOT_COUNT always-visible attribute rows (each = a clickable type field +
# a value box). Clicking a row's type opens the reusable searchable popup
# (uiswitchbot.SearchListWindow: live filter + scroll). Stones + frame + a live
# token preview; "Append to page" writes the [item=...; apply=type:val|...]
# markup into the current loose UserData/wiki page and live-reloads.
#
# Gated behind SimpleTextLoader._WikiDevMode(); never shown in production.
#
# NOTE on alignment in this RTL/Arabic client: TextLines default to RIGHT text
# alignment (so a left-positioned label flows off the left edge). English UI
# labels therefore call SetHorizontalAlignLeft(); Arabic content (item / attr
# names) uses SetWindowHorizontalAlignRight() for correct RTL direction.
# -----------------------------------------------------------------------------
import ui
import item
import player
import chat
import wiki
import localeinfo
import uitooltip

try:
	import dbg
except Exception:
	dbg = None

ATTR_ROWS = 7
SOCKET_ROWS = 3

_instance = None


def Open(loader):
	global _instance
	try:
		if _instance is None:
			_instance = WikiItemBuilder()
		_instance.Bind(loader)
		_instance.Open()
	except Exception:
		if dbg:
			import traceback
			dbg.TraceError("WikiItemBuilder.Open: " + traceback.format_exc())


class ItemSearchPopup(ui.BoardWithTitleBar):
	# Roomy type-ahead item search. The wiki item table is huge, so we query it
	# as the user types and show the top matches in a wide, full-row list (long
	# item names fit). Opened from the builder's item card magnifier.
	WIDTH  = 330
	HEIGHT = 388
	MARGIN = 10
	ROWH   = 16
	MAXR   = 16

	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		self.AddFlag("movable")
		self.AddFlag("float")
		self.items  = []
		self.onPick = None
		self.idx    = []
		self._Build()

	def _Build(self):
		M = self.MARGIN
		W = self.WIDTH
		self.SetSize(W, self.HEIGHT)
		self.SetTitleName(localeinfo.WIKI_BUILDER_ITEM)
		self.SetCloseEvent(ui.__mem_func__(self.Close))

		self._frame = ui.ThinBoard()
		self._frame.SetParent(self)
		self._frame.SetPosition(M, 30)
		self._frame.SetSize(W - 2 * M, 24)
		self._frame.Show()
		self.edit = ui.EditLine()
		self.edit.SetParent(self._frame)
		self.edit.SetPosition(8, 6)
		self.edit.SetSize(W - 2 * M - 16, 14)
		self.edit.SetMax(48)
		self.edit.SetText("")
		self.edit.SetReturnEvent(ui.__mem_func__(self._Refresh))
		self.edit.SetEscapeEvent(ui.__mem_func__(self.Close))
		self.edit.OnIMEUpdate = ui.__mem_func__(self._OnIME)
		self.edit.Show()

		self._bg = ui.ThinBoard()
		self._bg.SetParent(self)
		self._bg.SetPosition(M, 58)
		self._bg.SetSize(W - 2 * M, self.HEIGHT - 58 - 12)
		self._bg.Show()
		self.listbox = ui.ListBox()
		self.listbox.SetParent(self._bg)
		self.listbox.SetPosition(6, 6)
		self.listbox.SetSize(W - 2 * M - 12, self.HEIGHT - 58 - 24)
		self.listbox.SetEvent(ui.__mem_func__(self._OnSelect))
		self.listbox.Show()

	def Open(self, items, onPick):
		self.items = items or []
		self.onPick = onPick
		self.edit.SetText("")
		self.Show()
		self.SetCenterPosition()
		self.SetTop()
		try:
			self.edit.SetFocus()
		except Exception:
			pass
		self._Refresh()

	def _OnIME(self):
		try:
			ui.EditLine.OnIMEUpdate(self.edit)
		except Exception:
			pass
		self._Refresh()

	def _Refresh(self):
		txt = self.edit.GetText() or ""
		self.idx = []
		try:
			self.listbox.ClearItem()
		except Exception:
			pass
		row = 0
		if txt.isdigit():
			v = int(txt)
			for (vnum, nm) in self.items:
				if vnum == v:
					self.idx.append(vnum)
					self.listbox.InsertItem(0, nm)
					row = 1
					break
		else:
			lo = txt.lower()
			for (vnum, nm) in self.items:
				if not txt or (nm or "").lower().find(lo) != -1:
					self.idx.append(vnum)
					self.listbox.InsertItem(row, nm)
					row += 1
					if row >= self.MAXR:
						break

	def _OnSelect(self, key, name):
		try:
			k = int(key)
		except Exception:
			k = -1
		if 0 <= k < len(self.idx) and self.onPick:
			self.onPick(int(self.idx[k]), name)
		self.Close()

	def Close(self):
		try:
			self.Hide()
		except Exception:
			pass

	def OnPressEscapeKey(self):
		self.Close()
		return True


class WikiItemBuilder(ui.BoardWithTitleBar):
	WIDTH       = 400
	HEIGHT      = 524
	MARGIN      = 14
	MAX_RESULTS = 7
	ROWH        = 17
	ATTR_ROWH   = 24
	TYPEW       = 224
	VALW        = 110

	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		self.AddFlag("movable")
		self.AddFlag("float")

		self.loader        = None
		self.selected_vnum = 0
		self.frameStyle    = "square"
		self.attrSearchRow = -1
		self.search        = None
		self._stoneList    = None

		self.ITEM_LIST = self._BuildItemList()
		self.ATTR_LIST = self._BuildAttrList()
		self.attrRows   = []
		self.socketRows = []
		self.stoneRow   = -1
		self.itemSearch = None

		self.toolTip = None
		try:
			self.toolTip = uitooltip.ItemToolTip()
		except Exception:
			self.toolTip = None

		self._Build()

	# -- data sources ---------------------------------------------------------
	def _BuildItemList(self):
		out = []
		try:
			if hasattr(wiki, "GetItemList"):
				for entry in wiki.GetItemList():
					try:
						out.append((int(entry[0]), entry[1]))
					except Exception:
						continue
		except Exception:
			pass
		return out

	def _BuildAttrList(self):
		out = []
		try:
			d = uitooltip.ItemToolTip.AFFECT_DICT
			for t in d.keys():
				if not t:
					continue
				try:
					label = uitooltip.GET_AFFECT_STRING(t, 0)
				except Exception:
					label = None
				if not label:
					label = "APPLY[%d]" % int(t)
				out.append((int(t), label))
		except Exception:
			pass
		out.sort(key=lambda e: e[1])
		return out

	# -- widget helpers -------------------------------------------------------
	def _LabelL(self, text, x, y):
		# English UI label: left text-align so it flows RIGHT from x (otherwise
		# the RTL default right-aligns it off the left edge).
		t = ui.TextLine()
		t.SetParent(self)
		t.SetPosition(x, y)
		t.SetHorizontalAlignLeft()
		t.SetText(text)
		t.Show()
		return t

	def _Thin(self, parent, x, y, w, h):
		b = ui.ThinBoard()
		b.SetParent(parent)
		b.SetPosition(x, y)
		b.SetSize(w, h)
		b.Show()
		return b

	def _SmallBtn(self, text, x, y, handler):
		b = ui.Button()
		b.SetParent(self)
		b.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		b.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		b.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		b.SetText(text)
		b.SetPosition(x, y)
		b.SAFE_SetEvent(handler)
		b.Show()
		return b

	# -- UI build -------------------------------------------------------------
	def _Build(self):
		M  = self.MARGIN
		CW = self.WIDTH - M * 2
		self.SetSize(self.WIDTH, self.HEIGHT)
		self.SetTitleName(localeinfo.WIKI_BUILDER_TITLE)
		self.SetCloseEvent(ui.__mem_func__(self.Close))

		# ----- item: a magnifier that opens the roomy search popup, + a wide
		# preview card (full width so long item names fit). No inline dropdown.
		self.itemPickBtn = ui.Button()
		self.itemPickBtn.SetParent(self)
		self.itemPickBtn.SetUpVisual("d:/ymir work/ui/switchbot/search_attr_01.sub")
		self.itemPickBtn.SetOverVisual("d:/ymir work/ui/switchbot/search_attr_02.sub")
		self.itemPickBtn.SetDownVisual("d:/ymir work/ui/switchbot/search_attr_03.sub")
		self.itemPickBtn.SetPosition(M, 30)
		self.itemPickBtn.SAFE_SetEvent(self.OnPickItem)
		self.itemPickBtn.Show()
		self._LabelL(localeinfo.WIKI_BUILDER_ITEM, M + 28, 34)

		self._prevFrame = self._Thin(self, M, 54, CW, 48)
		self.preview_icon = ui.ImageBox()
		self.preview_icon.SetParent(self._prevFrame)
		self.preview_icon.SetPosition(8, 8)
		self.preview_icon.Hide()
		self.preview_name = ui.TextLine()
		self.preview_name.SetParent(self._prevFrame)
		self.preview_name.SetWindowHorizontalAlignRight()
		self.preview_name.SetPosition(10, 9)
		self.preview_name.SetText(localeinfo.WIKI_BUILDER_NO_ITEM)
		self.preview_name.Show()
		self.preview_vnum = ui.TextLine()
		self.preview_vnum.SetParent(self._prevFrame)
		self.preview_vnum.SetWindowHorizontalAlignRight()
		self.preview_vnum.SetPosition(10, 28)
		self.preview_vnum.SetPackedFontColor(0xFF888888)
		self.preview_vnum.SetText("")
		self.preview_vnum.Show()

		# ----- attribute rows -----
		self._LabelL(localeinfo.WIKI_BUILDER_ATTRIBUTE, M, 106)
		self._LabelL(localeinfo.WIKI_BUILDER_VALUE, M + self.TYPEW + 28, 106)
		self.attrCounter = ui.TextLine()
		self.attrCounter.SetParent(self)
		self.attrCounter.SetHorizontalAlignRight()
		self.attrCounter.SetPosition(self.WIDTH - M, 106)
		self.attrCounter.SetPackedFontColor(0xFF888888)
		self.attrCounter.Show()

		top = 124
		i = 0
		while i < ATTR_ROWS:
			ry = top + i * self.ATTR_ROWH
			frame = self._Thin(self, M, ry, self.TYPEW, 22)
			txt = ui.TextLine()
			txt.SetParent(frame)
			txt.AddFlag("not_pick")
			txt.SetWindowHorizontalAlignLeft()
			txt.SetPosition(10, 5)
			txt.SetText(localeinfo.WIKI_BUILDER_CHOOSE)
			txt.SetPackedFontColor(0xFF888888)
			txt.Show()
			# ThinBoard has no click event in this fork; a small magnifier Button
			# (switchbot's search art) is the per-row "choose attribute" trigger.
			pick = ui.Button()
			pick.SetParent(self)
			pick.SetUpVisual("d:/ymir work/ui/switchbot/search_attr_01.sub")
			pick.SetOverVisual("d:/ymir work/ui/switchbot/search_attr_02.sub")
			pick.SetDownVisual("d:/ymir work/ui/switchbot/search_attr_03.sub")
			pick.SetPosition(M + self.TYPEW + 2, ry - 1)
			pick.SetEvent(ui.__mem_func__(self._OpenAttrSearch), i)
			pick.Show()
			vframe = self._Thin(self, M + self.TYPEW + 28, ry, self.VALW, 22)
			vedit = ui.EditLine()
			vedit.SetParent(vframe)
			vedit.SetPosition(8, 5)
			vedit.SetSize(self.VALW - 16, 14)
			vedit.SetMax(7)
			vedit.SetText("")
			vedit.SetReturnEvent(ui.__mem_func__(self._RebuildToken))
			vedit.Show()
			self.attrRows.append({"type": 0, "frame": frame, "text": txt, "pick": pick, "vframe": vframe, "val": vedit})
			i = i + 1

		# ----- sockets (metin stones): same row+picker style as attributes -----
		sy = top + ATTR_ROWS * self.ATTR_ROWH + 8
		self._LabelL(localeinfo.WIKI_BUILDER_STONES, M, sy)
		stop = sy + 18
		j = 0
		while j < SOCKET_ROWS:
			ry = stop + j * self.ATTR_ROWH
			sframe = self._Thin(self, M, ry, CW - 28, 22)
			stext = ui.TextLine()
			stext.SetParent(sframe)
			stext.AddFlag("not_pick")
			stext.SetWindowHorizontalAlignLeft()
			stext.SetPosition(10, 5)
			stext.SetText(localeinfo.WIKI_BUILDER_EMPTY_SOCKET)
			stext.SetPackedFontColor(0xFF888888)
			stext.Show()
			spick = ui.Button()
			spick.SetParent(self)
			spick.SetUpVisual("d:/ymir work/ui/switchbot/search_attr_01.sub")
			spick.SetOverVisual("d:/ymir work/ui/switchbot/search_attr_02.sub")
			spick.SetDownVisual("d:/ymir work/ui/switchbot/search_attr_03.sub")
			spick.SetPosition(M + CW - 24, ry - 1)
			spick.SetEvent(ui.__mem_func__(self._OpenStoneSearch), j)
			spick.Show()
			self.socketRows.append({"vnum": 0, "frame": sframe, "text": stext, "pick": spick})
			j = j + 1

		fy = stop + SOCKET_ROWS * self.ATTR_ROWH + 10
		self.frameBtn = self._SmallBtn(self._FrameLabel(), M, fy, self.OnToggleFrame)

		# ----- token + actions -----
		ty = fy + 30
		self._LabelL(localeinfo.WIKI_BUILDER_TOKEN, M, ty)
		self.token_view = ui.TextLine()
		self.token_view.SetParent(self)
		self.token_view.SetHorizontalAlignLeft()
		self.token_view.SetPosition(M, ty + 16)
		self.token_view.SetPackedFontColor(0xFFFFD200)
		self.token_view.SetText("")
		self.token_view.Show()

		by = ty + 40
		self.appendBtn = ui.Button()
		self.appendBtn.SetParent(self)
		self.appendBtn.SetUpVisual("d:/ymir work/ui/coupon/enter_1.png")
		self.appendBtn.SetOverVisual("d:/ymir work/ui/coupon/enter_2.png")
		self.appendBtn.SetDownVisual("d:/ymir work/ui/coupon/enter_3.png")
		self.appendBtn.SetText(localeinfo.WIKI_BUILDER_APPEND)
		self.appendBtn.SetPosition(M + 40, by)
		self.appendBtn.SAFE_SetEvent(self.OnAppend)
		self.appendBtn.Show()

		self.closeBtn = ui.Button()
		self.closeBtn.SetParent(self)
		self.closeBtn.SetUpVisual("d:/ymir work/ui/coupon/cancel_1.png")
		self.closeBtn.SetOverVisual("d:/ymir work/ui/coupon/cancel_2.png")
		self.closeBtn.SetDownVisual("d:/ymir work/ui/coupon/cancel_3.png")
		self.closeBtn.SetText(localeinfo.WIKI_BUILDER_CLOSE)
		self.closeBtn.SetPosition(M + 210, by)
		self.closeBtn.SAFE_SetEvent(self.Close)
		self.closeBtn.Show()

		self.statusLine = ui.TextLine()
		self.statusLine.SetParent(self)
		self.statusLine.SetHorizontalAlignLeft()
		self.statusLine.SetPosition(M, by + 26)
		self.statusLine.SetPackedFontColor(0xFF80FF80)
		self.statusLine.SetText("")
		self.statusLine.Show()

		self.SetCenterPosition()
		self._RebuildToken()

	def _FrameLabel(self):
		if self.frameStyle == "circle":
			s = localeinfo.WIKI_BUILDER_FRAME_CIRCLE
		else:
			s = localeinfo.WIKI_BUILDER_FRAME_SQUARE
		return "%s: %s" % (localeinfo.WIKI_BUILDER_FRAME, s)

	def _Status(self, text):
		try:
			self.statusLine.SetText(text or "")
		except Exception:
			pass

	# -- item search (substring, inline) --------------------------------------
	def OnPickItem(self):
		if self.itemSearch is None:
			self.itemSearch = ItemSearchPopup()
		self.itemSearch.Open(self.ITEM_LIST, ui.__mem_func__(self._OnItemPicked))

	def _OnItemPicked(self, vnum, name):
		self._SetPreview(int(vnum))
		self._RebuildToken()

	def _SetPreview(self, vnum):
		self.selected_vnum = int(vnum)
		nm = "?"
		try:
			item.SelectItem(self.selected_vnum)
			nm = item.GetItemName()
			icon = item.GetIconImageFileName()
			if icon and icon.find("gr2") == -1:
				self.preview_icon.LoadImage(icon)
				self.preview_icon.Show()
			else:
				self.preview_icon.Hide()
		except Exception:
			self.preview_icon.Hide()
		self.preview_name.SetText(nm or "?")
		self.preview_vnum.SetText("vnum: %d" % self.selected_vnum)

	# -- attribute rows (click type -> searchable popup) ----------------------
	def _OpenSearch(self, items, acceptFunc, title):
		# Shared searchable popup (reused for attributes AND stones): rebinds the
		# accept handler + repopulates each open.
		try:
			import uiswitchbot
			if self.search is None:
				self.search = uiswitchbot.SearchListWindow()
				self.search.MakeWindow(300, 360)
				self.search.SetAcceptArgsType("KEY_VALUE")
			try:
				self.search.SetTitleName(title)
			except Exception:
				pass
			self.search.SetAcceptEvent(ui.__mem_func__(acceptFunc))
			self.search.RemoveAllItems()
			for (k, label) in items:
				self.search.AppendItem(k, label)
			self.search.SetCenterPosition()
			self.search.Open()
			self.search.SetTop()
		except Exception:
			if dbg:
				import traceback
				dbg.TraceError("WikiItemBuilder._OpenSearch: " + traceback.format_exc())

	def _OpenAttrSearch(self, rowIdx):
		self.attrSearchRow = int(rowIdx)
		items = [(0, localeinfo.WIKI_BUILDER_CLEAR)]
		for (t, label) in self.ATTR_LIST:
			items.append((t, label))
		self._OpenSearch(items, self._OnAttrPicked, localeinfo.WIKI_BUILDER_SEARCH_ATTR)

	def _StoneList(self):
		# Metin stones only (ITEM_TYPE_METIN), built once on first use + cached.
		if self._stoneList is not None:
			return self._stoneList
		out = []
		for (vnum, nm) in self.ITEM_LIST:
			try:
				item.SelectItem(vnum)
				if item.GetItemType() == item.ITEM_TYPE_METIN:
					out.append((vnum, nm))
			except Exception:
				pass
		self._stoneList = out
		return out

	def _OpenStoneSearch(self, socketIdx):
		self.stoneRow = int(socketIdx)
		items = [(0, localeinfo.WIKI_BUILDER_CLEAR)]
		for (vnum, nm) in self._StoneList():
			items.append((vnum, nm))
		self._OpenSearch(items, self._OnStonePicked, localeinfo.WIKI_BUILDER_STONES)

	def _OnStonePicked(self, key, value):
		i = self.stoneRow
		if i < 0 or i >= len(self.socketRows):
			return
		row = self.socketRows[i]
		v = 0
		try:
			v = int(key)
		except Exception:
			v = 0
		row["vnum"] = v
		if v == 0:
			row["text"].SetWindowHorizontalAlignLeft()
			row["text"].SetPosition(10, 5)
			row["text"].SetText(localeinfo.WIKI_BUILDER_EMPTY_SOCKET)
			row["text"].SetPackedFontColor(0xFF888888)
		else:
			row["text"].SetWindowHorizontalAlignRight()
			row["text"].SetPosition(8, 5)
			row["text"].SetText(value)
			row["text"].SetPackedFontColor(0xFFFFE2A0)
		self._RebuildToken()

	def _OnAttrPicked(self, key, value):
		i = self.attrSearchRow
		if i < 0 or i >= len(self.attrRows):
			return
		row = self.attrRows[i]
		t = 0
		try:
			t = int(key)
		except Exception:
			t = 0
		row["type"] = t
		if t == 0:
			row["text"].SetWindowHorizontalAlignLeft()
			row["text"].SetPosition(10, 5)
			row["text"].SetText(localeinfo.WIKI_BUILDER_CHOOSE)
			row["text"].SetPackedFontColor(0xFF888888)
			row["val"].SetText("")
		else:
			row["text"].SetWindowHorizontalAlignRight()
			row["text"].SetPosition(8, 5)
			row["text"].SetText(value)
			row["text"].SetPackedFontColor(0xFFFFE2A0)
			try:
				row["val"].SetFocus()
			except Exception:
				pass
		self._RebuildToken()

	# -- stones / frame -------------------------------------------------------
	def OnToggleFrame(self):
		self.frameStyle = "circle" if self.frameStyle == "square" else "square"
		try:
			self.frameBtn.SetText(self._FrameLabel())
		except Exception:
			pass
		self._RebuildToken()

	def _StoneStr(self):
		out = []
		for row in self.socketRows:
			if row["vnum"] > 0:
				out.append(str(row["vnum"]))
		return "|".join(out)

	def _RowValue(self, row):
		try:
			return int(row["val"].GetText() or "0")
		except Exception:
			return 0

	# -- token ----------------------------------------------------------------
	def _RebuildToken(self):
		applies = []
		count = 0
		for row in self.attrRows:
			if row["type"] > 0:
				count += 1
				applies.append("%d:%d" % (row["type"], self._RowValue(row)))
		self.attrCounter.SetText("%d/%d" % (count, ATTR_ROWS))
		if not self.selected_vnum:
			self.token_view.SetText("")
			return ""
		parts = ["item=%d" % self.selected_vnum]
		if self.frameStyle == "circle":
			parts.append("style=circle")
		stones = self._StoneStr()
		if stones:
			parts.append("socket=%s" % stones)
		if applies:
			parts.append("apply=%s" % "|".join(applies))
		token = "[" + "; ".join(parts) + "]"
		self.token_view.SetText(token)
		return token

	# -- append to the live page ---------------------------------------------
	def OnAppend(self):
		if not self.selected_vnum:
			self._Status(localeinfo.WIKI_BUILDER_PICK_FIRST)
			return
		token = self._RebuildToken()
		loader = self.loader
		fn = getattr(loader, "currentFile", None) if loader is not None else None
		if not fn:
			self._Status(localeinfo.WIKI_BUILDER_OPEN_PAGE_FIRST)
			return
		text = ""
		try:
			(path, f) = loader._ResolveWikiSource(fn)
			try:
				text = "".join(f.readlines())
			finally:
				try:
					f.close()
				except Exception:
					pass
		except Exception:
			text = ""
		text = text.replace("\r\n", "\n").replace("\r", "\n")
		while text.endswith("\n"):
			text = text[:-1]
		if text.strip():
			body = text + "\n" + token
		else:
			body = "[DOC]\n" + token
		body = body.replace("\n", "\r\n") + "\r\n"
		userPath = "UserData/wiki/%s" % fn
		try:
			out = open(userPath, "wb")
			try:
				out.write(body)
			finally:
				out.close()
			try:
				loader.ReloadCurrent()
			except Exception:
				pass
			self._Status(localeinfo.WIKI_BUILDER_APPENDED % fn)
		except Exception:
			if dbg:
				import traceback
				dbg.TraceError("WikiItemBuilder.OnAppend: " + traceback.format_exc())
			self._Status(localeinfo.WIKI_BUILDER_WRITE_FAIL)
			try:
				chat.AppendChat(chat.CHAT_TYPE_INFO, token)
			except Exception:
				pass

	# -- lifecycle ------------------------------------------------------------
	def Bind(self, loader):
		self.loader = loader

	def Open(self):
		self.Show()
		try:
			self.SetTop()
		except Exception:
			pass
		self._RebuildToken()

	def Close(self):
		if self.itemSearch is not None:
			try:
				self.itemSearch.Close()
			except Exception:
				pass
		if self.search is not None:
			try:
				self.search.Close()
			except Exception:
				pass
		if self.toolTip is not None:
			try:
				self.toolTip.HideToolTip()
			except Exception:
				pass
		try:
			self.Hide()
		except Exception:
			pass

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnUpdate(self):
		# Keep the token preview live as values are typed (cheap; no per-edit
		# event needed).
		try:
			self._RebuildToken()
		except Exception:
			pass
		if self.toolTip is None:
			return
		try:
			if (self.selected_vnum
					and self.preview_icon.IsShow()
					and self.preview_icon.IsIn()):
				self.toolTip.SetItemToolTip(self.selected_vnum)
			else:
				self.toolTip.HideToolTip()
		except Exception:
			pass
