# coding: latin_1
"""Drop editor widgets and dispatch for the in-game wiki.

Test-server / GM-only; gated by app.ENABLE_DROP_EDITOR. Provides the editable
row widgets, item picker, and ack-routing glue used by ingamewikiui.py when
GM Edit Mode is toggled on. See docs/superpowers/plans/2026-05-14-gm-drop-editor.md
phases 9-12 for the design.
"""

import app
import net
import ui
import item
import dbg
import chat
import localeinfo

try:
	import wiki
except Exception:
	wiki = None

try:
	import uicommon
except Exception:
	uicommon = None

try:
	import uitooltip
except Exception:
	uitooltip = None


# -----------------------------------------------------------------------------
# C-side enums mirrored here (must stay in sync with packet_drop_editor.h /
# Batch 5 net.SendDropEditor argument order).
# -----------------------------------------------------------------------------

FK_MOB_DROP = 0
FK_SPECIAL  = 1

SUB_CG_SET_ROW = 0
SUB_CG_ADD_ROW = 1
SUB_CG_DEL_ROW = 2
SUB_CG_SAVE    = 3
SUB_CG_DISCARD = 4
SUB_CG_FETCH   = 5

SUB_GC_OK            = 0
SUB_GC_ERR           = 1
SUB_GC_GROUP_REFRESH = 2

DROP_EDITOR_NEED_SIZE  = 2
DROP_EDITOR_MAX_ROWS   = 12
DROP_EDITOR_ROW_HEIGHT = 17.5


# -----------------------------------------------------------------------------
# Refresh subscription registry. Keyed by (file_kind, group_vnum, group_name).
# -----------------------------------------------------------------------------

_RefreshSubscribers = {}


def Subscribe(file_kind, group_vnum, group_name, cb):
	_RefreshSubscribers[(int(file_kind), int(group_vnum), str(group_name or ""))] = cb


def Unsubscribe(file_kind, group_vnum, group_name):
	_RefreshSubscribers.pop((int(file_kind), int(group_vnum), str(group_name or "")), None)


def UnsubscribeAll():
	_RefreshSubscribers.clear()


def RouteAck(sub, file_kind, group_vnum, group_name, err_text, rows):
	"""Called by ingamewikiui.OnDropEditorAckPyCb on every HEADER_GC_DROP_EDITOR_ACK."""
	try:
		if sub == SUB_GC_ERR:
			chat.AppendChat(chat.CHAT_TYPE_INFO,
							"[DropEditor] Error: %s" % (err_text or "unknown"))
			return
		if sub == SUB_GC_OK:
			chat.AppendChat(chat.CHAT_TYPE_INFO,
							"[DropEditor] OK%s" % (": " + err_text if err_text else ""))
			return
		if sub == SUB_GC_GROUP_REFRESH:
			# The group's drops changed server-side -- drop the client's cached
			# wiki entry for this vnum so the read-only wiki page re-fetches it
			# (otherwise it serves the stale cache until a client restart).
			# Harmless on a plain fetch: the re-fetch just re-reads the same
			# data. hasattr guard keeps this working on an older client build
			# that lacks wiki.InvalidateCache.
			try:
				if wiki is not None and hasattr(wiki, "InvalidateCache"):
					wiki.InvalidateCache(int(group_vnum),
										 int(file_kind) == FK_MOB_DROP)
			except Exception:
				pass
			cb = _RefreshSubscribers.get(
				(int(file_kind), int(group_vnum), str(group_name or "")))
			if cb:
				cb(rows or [])
	except Exception:
		import traceback
		dbg.TraceError("DropEditor.RouteAck: " + traceback.format_exc())


# -----------------------------------------------------------------------------
# DropRowEdit — one editable drop row: [icon] [name] [count] [pct] [x]
# -----------------------------------------------------------------------------

class DropRowEdit(ui.Window):
	WIDTH      = 380
	SLOT_PIX   = 32
	PAD        = 5
	CONTROLS_H = 20      # height of the count / pct / delete control band

	def __init__(self, file_kind, group_vnum, group_name, row_index,
				 item_vnum, count, pct_x10000, rare_pct):
		ui.Window.__init__(self)
		self.file_kind   = int(file_kind)
		self.group_vnum  = int(group_vnum)
		self.group_name  = str(group_name or "")
		self.row_index   = int(row_index)
		self.item_vnum   = int(item_vnum)
		self.rare_pct    = int(rare_pct)
		self._count_value = int(count) if count else 1
		self._pct_x10000  = int(pct_x10000) if pct_x10000 else 0

		# Item slot footprint (1..4). Multi-slot armors/weapons have tall icons
		# that otherwise overlap the next row, so the row -- and its frame --
		# are sized to the item.
		size_x, size_y = 1, 1
		try:
			item.SelectItem(self.item_vnum)
			(sx, sy) = item.GetItemSize()
			size_x = max(1, min(4, int(sx)))
			size_y = max(1, min(4, int(sy)))
		except Exception:
			pass
		self.itemSizeX = size_x
		self.itemSizeY = size_y

		icon_w = size_x * self.SLOT_PIX
		icon_h = size_y * self.SLOT_PIX
		self.HEIGHT = max(icon_h, self.CONTROLS_H) + self.PAD * 2
		self.SetSize(self.WIDTH, self.HEIGHT)

		# Per-row ThinBoard V3 frame -- gives each row its own readable block
		# (the per-item background pattern from notification_history.py).
		self.frame = ui.OutlineWindow()
		self.frame.SetParent(self)
		self.frame.MakeOutlineWindow(self.WIDTH - 4, self.HEIGHT - 4)
		self.frame.SetPosition(0, 0)
		self.frame.Show()

		band_y = self.PAD

		# Icon -- top-left, natural size, extends downward for multi-slot items.
		self.icon = ui.ImageBox()
		self.icon.SetParent(self)
		try:
			item.SelectItem(self.item_vnum)
			icon_path = item.GetIconImageFileName()
			if icon_path:
				self.icon.LoadImage(icon_path)
		except Exception:
			pass
		self.icon.SetPosition(self.PAD + 2, band_y)
		self.icon.Show()

		# Item name -- in the control band at the top, right of the icon.
		self.name_text = ui.TextLine()
		self.name_text.SetParent(self)
		try:
			item.SelectItem(self.item_vnum)
			nm = item.GetItemName()
		except Exception:
			nm = "?"
		self.name_text.SetText(nm)
		self.name_text.SetPosition(self.PAD + 2 + icon_w + 8, band_y + 3)
		self.name_text.SetHorizontalAlignRight()
		self.name_text.Show()

		# Count + chance, shown read-only. Editing goes through the Edit button
		# (RowEditDialog) -- the inline EditLines were too cramped to use.
		self.count_text = ui.TextLine()
		self.count_text.SetParent(self)
		self.count_text.SetText("x%d" % self._count_value)
		self.count_text.SetPosition(200, band_y + 3)
		self.count_text.SetHorizontalAlignRight()
		self.count_text.Show()

		self.pct_text = ui.TextLine()
		self.pct_text.SetParent(self)
		self.pct_text.SetText("%.4f%%" % (self._pct_x10000 / 10000.0))
		self.pct_text.SetPosition(250, band_y + 3)
		self.pct_text.SetHorizontalAlignRight()
		self.pct_text.Show()

		# Edit button -- opens RowEditDialog for this row's count / chance.
		self.edit_btn = ui.Button()
		self.edit_btn.SetParent(self)
		self.edit_btn.SetUpVisual("d:/ymir work/ui/chat/btn_option01_default.tga")
		self.edit_btn.SetOverVisual("d:/ymir work/ui/chat/btn_option01_over.tga")
		self.edit_btn.SetDownVisual("d:/ymir work/ui/chat/btn_option01_down.tga")
		self.edit_btn.SetPosition(322, band_y + 3)
		self.edit_btn.SetEvent(ui.__mem_func__(self._OnEdit))
		self.edit_btn.Show()

		# Delete button (x)
		self.del_btn = ui.Button()
		self.del_btn.SetParent(self)
		self.del_btn.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")
		self.del_btn.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")
		self.del_btn.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")
		self.del_btn.SetPosition(345, band_y + 3)
		self.del_btn.SetEvent(ui.__mem_func__(self._OnDelete))
		self.del_btn.Show()

		self._confirm    = None
		self._editDialog = None

	def _OnEdit(self):
		# Open the count / chance edit dialog for this row.
		try:
			if self._editDialog is not None and self._editDialog.IsShow():
				self._editDialog.SetTop()
				return
			self._editDialog = RowEditDialog(
				self.file_kind, self.group_vnum, self.group_name,
				self.row_index, self.item_vnum, self._count_value,
				self._pct_x10000, self.rare_pct)
			self._editDialog.Open()
		except Exception:
			import traceback
			dbg.TraceError("DropEditor.DropRowEdit._OnEdit: "
						   + traceback.format_exc())

	def _OnDelete(self):
		# Confirmation dialog (uicommon.QuestionDialog).
		if uicommon is None:
			# Fallback: fire delete immediately if uicommon is unavailable.
			self._DoDelete()
			return

		try:
			q = uicommon.QuestionDialog()
			q.SetText(localeinfo.DROP_EDITOR_DEL % self.row_index)
			q.SetAcceptEvent(ui.__mem_func__(self._DoDelete))
			q.SetCancelEvent(ui.__mem_func__(self._CancelDelete))
			q.Open()
			self._confirm = q
		except Exception:
			import traceback
			dbg.TraceError("DropEditor._OnDelete: " + traceback.format_exc())
			self._DoDelete()

	def _CancelDelete(self):
		try:
			if self._confirm:
				self._confirm.Close()
		except Exception:
			pass
		self._confirm = None

	def _DoDelete(self):
		try:
			if self._confirm:
				self._confirm.Close()
		except Exception:
			pass
		self._confirm = None
		net.SendDropEditor(SUB_CG_DEL_ROW, self.file_kind, self.group_vnum,
						   self.group_name, self.row_index, 0, 0, 0, 0)


# -----------------------------------------------------------------------------
# RowEditDialog -- edits an existing drop row's count and drop chance. Opened
# by DropRowEdit's Edit button; sends SUB_CG_SET_ROW on save.
# -----------------------------------------------------------------------------

class RowEditDialog(ui.BoardWithTitleBar):
	WIDTH  = 340
	HEIGHT = 178
	MARGIN = 10

	def __init__(self, file_kind, group_vnum, group_name, row_index,
				 item_vnum, count, pct_x10000, rare_pct):
		ui.BoardWithTitleBar.__init__(self)
		self.AddFlag("movable")
		self.AddFlag("float")

		self.file_kind    = int(file_kind)
		self.group_vnum   = int(group_vnum)
		self.group_name   = str(group_name or "")
		self.row_index    = int(row_index)
		self.item_vnum    = int(item_vnum)
		self.rare_pct     = int(rare_pct)
		self._count_value = int(count) if count else 1
		self._pct_x10000  = int(pct_x10000) if pct_x10000 else 0

		self.SetSize(self.WIDTH, self.HEIGHT)
		self.SetTitleName("Edit drop row")
		self.SetCloseEvent(ui.__mem_func__(self.Close))

		M  = self.MARGIN
		cw = self.WIDTH - M * 2

		# --- item preview (icon + name + vnum) -------------------------------
		self._previewFrame = ui.ThinBoard()
		self._previewFrame.SetParent(self)
		self._previewFrame.SetSize(cw, 56)
		self._previewFrame.SetPosition(M, 32)
		self._previewFrame.Show()

		self.icon = ui.ImageBox()
		self.icon.SetParent(self)
		try:
			item.SelectItem(self.item_vnum)
			icon_path = item.GetIconImageFileName()
			if icon_path:
				self.icon.LoadImage(icon_path)
		except Exception:
			pass
		self.icon.SetPosition(M + 12, 45)
		self.icon.Show()

		self.name_text = ui.TextLine()
		self.name_text.SetParent(self)
		try:
			item.SelectItem(self.item_vnum)
			nm = item.GetItemName()
		except Exception:
			nm = "?"
		self.name_text.SetText(nm or "?")
		self.name_text.SetPosition(M + 58, 40)
		self.name_text.SetHorizontalAlignRight()
		self.name_text.Show()

		self.vnum_text = ui.TextLine()
		self.vnum_text.SetParent(self)
		self.vnum_text.SetText("vnum: %d" % self.item_vnum)
		self.vnum_text.SetPackedFontColor(0xFF888888)
		self.vnum_text.SetHorizontalAlignRight()
		self.vnum_text.SetPosition(M + 58, 62)
		self.vnum_text.Show()

		# --- count / chance inputs ------------------------------------------
		self._inputsFrame = ui.ThinBoard()
		self._inputsFrame.SetParent(self)
		self._inputsFrame.SetSize(cw, 38)
		self._inputsFrame.SetPosition(M, 96)
		self._inputsFrame.Show()

		self._countLabel = ui.TextLine()
		self._countLabel.SetParent(self)
		self._countLabel.SetText(localeinfo.RANKING_CAT_COUNT)
		self._countLabel.SetHorizontalAlignRight()
		self._countLabel.SetPosition(M + 120, 108)
		self._countLabel.Show()

		self.count_edit = ui.EditLine()
		self.count_edit.SetParent(self)
		self.count_edit.SetSize(40, 16)
		self.count_edit.SetPosition(M + 54, 107)
		self.count_edit.SetMax(4)
		self.count_edit.SetNumberMode()
		self.count_edit.SetText(str(self._count_value))
		self.count_edit.SetReturnEvent(ui.__mem_func__(self._OnSave))
		self.count_edit.SetEscapeEvent(ui.__mem_func__(self.Close))
		self.count_edit.Show()

		self._pctLabel = ui.TextLine()
		self._pctLabel.SetParent(self)
		self._pctLabel.SetText(localeinfo.DROP_EDITOR_CHANCE)
		self._pctLabel.SetPosition(M + 250, 108)
		self._pctLabel.SetHorizontalAlignRight()
		self._pctLabel.Show()

		self.pct_edit = ui.EditLine()
		self.pct_edit.SetParent(self)
		self.pct_edit.SetSize(70, 16)
		self.pct_edit.SetPosition(M + 180, 107)
		self.pct_edit.SetMax(10)
		self.pct_edit.SetText("%.4f" % (self._pct_x10000 / 10000.0))
		self.pct_edit.SetReturnEvent(ui.__mem_func__(self._OnSave))
		self.pct_edit.SetEscapeEvent(ui.__mem_func__(self.Close))
		self.pct_edit.Show()

		# --- buttons ---------------------------------------------------------
		self.btn_cancel = ui.Button()
		self.btn_cancel.SetParent(self)
		self.btn_cancel.SetUpVisual("d:/ymir work/ui/coupon/cancel_1.png")
		self.btn_cancel.SetOverVisual("d:/ymir work/ui/coupon/cancel_2.png")
		self.btn_cancel.SetDownVisual("d:/ymir work/ui/coupon/cancel_3.png")
		self.btn_cancel.SetText(localeinfo.RANKING_DONATE_CANCEL)
		self.btn_cancel.SetPosition(M + 60, 144)
		self.btn_cancel.SAFE_SetEvent(self.Close)
		self.btn_cancel.Show()

		self.btn_save = ui.Button()
		self.btn_save.SetParent(self)
		self.btn_save.SetUpVisual("d:/ymir work/ui/coupon/enter_1.png")
		self.btn_save.SetOverVisual("d:/ymir work/ui/coupon/enter_2.png")
		self.btn_save.SetDownVisual("d:/ymir work/ui/coupon/enter_3.png")
		self.btn_save.SetText(localeinfo.SWITCHBOT_SAVE)
		self.btn_save.SetPosition(M + 170, 144)
		self.btn_save.SAFE_SetEvent(self._OnSave)
		self.btn_save.Show()

		self.SetCenterPosition()

	def _OnSave(self):
		try:
			cnt = int(self.count_edit.GetText() or "1")
		except Exception:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "[DropEditor] Bad count")
			return
		try:
			pct = float(self.pct_edit.GetText() or "0")
		except Exception:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "[DropEditor] Bad pct")
			return
		pct_x = int(pct * 10000)
		if pct_x <= 0 or pct_x > 1000000:
			chat.AppendChat(chat.CHAT_TYPE_INFO,
							"[DropEditor] Pct out of range (0 < pct <= 100)")
			return
		if cnt < 1:
			cnt = 1
		net.SendDropEditor(SUB_CG_SET_ROW, self.file_kind, self.group_vnum,
						   self.group_name, self.row_index, self.item_vnum,
						   cnt, pct_x, self.rare_pct)
		self.Close()

	def Open(self):
		self.Show()
		try:
			self.SetTop()
		except Exception:
			pass

	def Close(self):
		try:
			self.Hide()
		except Exception:
			pass

	def OnPressEscapeKey(self):
		self.Close()
		return True


# -----------------------------------------------------------------------------
# ItemPicker -- the "Add drop row" window. A framed BoardWithTitleBar with a
# search field, a results listbox, a selected-item preview (icon + name + vnum;
# hover the icon for the full item tooltip), and count / chance inputs.
# Prefix-match search logic modeled on uioxevent.py.
# -----------------------------------------------------------------------------

class ItemPicker(ui.BoardWithTitleBar):
	WIDTH       = 360
	HEIGHT      = 386
	MARGIN      = 10
	MAX_RESULTS = 7

	def __init__(self, file_kind, group_vnum, group_name):
		ui.BoardWithTitleBar.__init__(self)
		# Standalone, draggable top-level window (see DropEditorWindow for the
		# float/movable rationale -- a window outside its parent's rect is not
		# click-pickable, so it must be its own top-level "float" window).
		self.AddFlag("movable")
		self.AddFlag("float")

		self.file_kind  = int(file_kind)
		self.group_vnum = int(group_vnum)
		self.group_name = str(group_name or "")

		self.ITEM_LIST     = self._BuildItemList()
		self.vnumIndex     = []
		self.selected_vnum = 0

		self.toolTip = None
		if uitooltip is not None:
			try:
				self.toolTip = uitooltip.ItemToolTip()
			except Exception:
				self.toolTip = None

		self.SetSize(self.WIDTH, self.HEIGHT)
		self.SetTitleName("Add drop row")
		self.SetCloseEvent(ui.__mem_func__(self.Close))

		M  = self.MARGIN
		cw = self.WIDTH - M * 2

		# --- search field ----------------------------------------------------
		self._searchLabel = ui.TextLine()
		self._searchLabel.SetParent(self)
		self._searchLabel.SetText(localeinfo.DROP_EDITOR_SEARCH)
		self._searchLabel.SetPosition(M + 40, 32)
		self._searchLabel.SetHorizontalAlignRight()
		self._searchLabel.Show()

		self._searchFrame = ui.ThinBoard()
		self._searchFrame.SetParent(self)
		self._searchFrame.SetSize(cw, 32)
		self._searchFrame.SetPosition(M, 48)
		self._searchFrame.Show()

		self.name_edit = ui.EditLine()
		self.name_edit.SetParent(self)
		self.name_edit.SetSize(cw - 20, 16)
		self.name_edit.SetPosition(M + 10, 56)
		self.name_edit.SetMax(64)
		self.name_edit.SetText("")
		self.name_edit.SetReturnEvent(ui.__mem_func__(self._RefreshResults))
		self.name_edit.SetEscapeEvent(ui.__mem_func__(self.Close))
		self.name_edit.OnIMEUpdate = ui.__mem_func__(self._OnIMEUpdate)
		self.name_edit.Show()

		# --- results listbox -------------------------------------------------
		resultsTop = 86
		resultsH   = int(DROP_EDITOR_ROW_HEIGHT * self.MAX_RESULTS) + 12
		self._resultsFrame = ui.ThinBoard()
		self._resultsFrame.SetParent(self)
		self._resultsFrame.SetSize(cw, resultsH)
		self._resultsFrame.SetPosition(M, resultsTop)
		self._resultsFrame.Show()

		self._listW  = cw - 12
		self.listbox = ui.ListBox()
		self.listbox.SetParent(self)
		self.listbox.SetPosition(M + 6, resultsTop + 6)
		self.listbox.SetSize(self._listW, 0)
		self.listbox.SetEvent(ui.__mem_func__(self.OnSelect))
		self.listbox.Hide()

		# --- selected-item preview ------------------------------------------
		previewTop = resultsTop + resultsH + 8
		self._previewFrame = ui.ThinBoard()
		self._previewFrame.SetParent(self)
		self._previewFrame.SetSize(cw, 70)
		self._previewFrame.SetPosition(M, previewTop)
		self._previewFrame.Show()

		self.preview_icon = ui.ImageBox()
		self.preview_icon.SetParent(self)
		self.preview_icon.SetPosition(M + 12, previewTop + 13)
		self.preview_icon.Hide()

		self.preview_name = ui.TextLine()
		self.preview_name.SetParent(self)
		self.preview_name.SetPosition(M + 58, previewTop + 16)
		self.preview_name.SetText(localeinfo.DROP_EDITOR_NO_ITEM)
		self.preview_name.SetHorizontalAlignRight()
		self.preview_name.Show()

		self.preview_vnum = ui.TextLine()
		self.preview_vnum.SetParent(self)
		self.preview_vnum.SetPosition(M + 58, previewTop + 38)
		self.preview_vnum.SetText("")
		self.preview_vnum.SetPackedFontColor(0xFF888888)
		self.preview_name.SetHorizontalAlignRight()
		self.preview_vnum.Show()

		# --- count / chance --------------------------------------------------
		inputsTop = previewTop + 70 + 8
		self._inputsFrame = ui.ThinBoard()
		self._inputsFrame.SetParent(self)
		self._inputsFrame.SetSize(cw, 36)
		self._inputsFrame.SetPosition(M, inputsTop)
		self._inputsFrame.Show()

		self._countLabel = ui.TextLine()
		self._countLabel.SetParent(self)
		self._countLabel.SetText(localeinfo.RANKING_CAT_COUNT)
		self._countLabel.SetPosition(M + 120, inputsTop + 12)
		self._countLabel.SetHorizontalAlignRight()
		self._countLabel.Show()

		self.count_edit = ui.EditLine()
		self.count_edit.SetParent(self)
		self.count_edit.SetSize(40, 16)
		self.count_edit.SetPosition(M + 54, inputsTop + 11)
		self.count_edit.SetMax(4)
		self.count_edit.SetNumberMode()
		self.count_edit.SetText("1")
		self.count_edit.Show()

		self._pctLabel = ui.TextLine()
		self._pctLabel.SetParent(self)
		self._pctLabel.SetText(localeinfo.DROP_EDITOR_CHANCE)
		self._pctLabel.SetPosition(M + 250, inputsTop + 12)
		self._pctLabel.SetHorizontalAlignRight()
		self._pctLabel.Show()

		self.pct_edit = ui.EditLine()
		self.pct_edit.SetParent(self)
		self.pct_edit.SetSize(70, 16)
		self.pct_edit.SetPosition(M + 180, inputsTop + 11)
		self.pct_edit.SetMax(10)
		self.pct_edit.SetText("0.5000")
		self.pct_edit.Show()

		# --- buttons ---------------------------------------------------------
		btnTop = inputsTop + 36 + 10
		self.btn_cancel = ui.Button()
		self.btn_cancel.SetParent(self)
		self.btn_cancel.SetUpVisual("d:/ymir work/ui/coupon/cancel_1.png")
		self.btn_cancel.SetOverVisual("d:/ymir work/ui/coupon/cancel_2.png")
		self.btn_cancel.SetDownVisual("d:/ymir work/ui/coupon/cancel_3.png")
		self.btn_cancel.SetText(localeinfo.RANKING_DONATE_CANCEL)
		self.btn_cancel.SetPosition(M + 70, btnTop)
		self.btn_cancel.SAFE_SetEvent(self.Close)
		self.btn_cancel.Show()

		self.btn_add = ui.Button()
		self.btn_add.SetParent(self)
		self.btn_add.SetUpVisual("d:/ymir work/ui/coupon/enter_1.png")
		self.btn_add.SetOverVisual("d:/ymir work/ui/coupon/enter_2.png")
		self.btn_add.SetDownVisual("d:/ymir work/ui/coupon/enter_3.png")
		self.btn_add.SetText(localeinfo.DROP_EDITOR_ADD)
		self.btn_add.SetPosition(M + 190, btnTop)
		self.btn_add.SAFE_SetEvent(self.OnConfirm)
		self.btn_add.Show()

		self.SetCenterPosition()

	# -- item list / search ---------------------------------------------------
	def _BuildItemList(self):
		out = []
		try:
			if wiki is not None and hasattr(wiki, "GetItemList"):
				for entry in wiki.GetItemList():
					try:
						vnum, name = int(entry[0]), entry[1]
					except Exception:
						continue
					out.append({"index": vnum, "name": name})
		except Exception:
			import traceback
			dbg.TraceError("DropEditor.ItemPicker._BuildItemList: "
						   + traceback.format_exc())
		return out

	def _OnIMEUpdate(self):
		try:
			ui.EditLine.OnIMEUpdate(self.name_edit)
		except Exception:
			pass
		self._RefreshResults()

	def _RefreshResults(self):
		txt = self.name_edit.GetText() or ""
		self.vnumIndex = []
		try:
			self.listbox.ClearItem()
		except Exception:
			pass

		if len(txt) < DROP_EDITOR_NEED_SIZE:
			self.listbox.Hide()
			return

		row = 0
		if txt.isdigit():
			try:
				v = int(txt)
			except Exception:
				v = 0
			for entry in self.ITEM_LIST:
				if entry["index"] == v:
					self.vnumIndex.append(v)
					self.listbox.InsertItem(0, entry["name"])
					row = 1
					break
		else:
			lo = txt.lower()
			tlen = len(txt)
			for entry in self.ITEM_LIST:
				nm = entry["name"] or ""
				if len(nm) >= tlen and nm[:tlen].lower() == lo:
					self.vnumIndex.append(entry["index"])
					self.listbox.InsertItem(row, nm)
					row += 1
					if row >= self.MAX_RESULTS:
						break

		try:
			n = self.listbox.GetItemCount()
		except Exception:
			n = row
		self.listbox.SetSize(self._listW, int(DROP_EDITOR_ROW_HEIGHT * n))
		if n > 0:
			self.listbox.Show()
		else:
			self.listbox.Hide()

	def OnSelect(self, key, name):
		try:
			k = int(key)
		except Exception:
			k = -1
		if 0 <= k < len(self.vnumIndex):
			self._SetPreview(int(self.vnumIndex[k]))
			try:
				self.name_edit.SetText(name)
			except Exception:
				pass
		self.listbox.Hide()

	# -- preview --------------------------------------------------------------
	def _SetPreview(self, vnum):
		self.selected_vnum = int(vnum)
		nm = "?"
		try:
			item.SelectItem(self.selected_vnum)
			nm = item.GetItemName()
			icon_path = item.GetIconImageFileName()
			if icon_path:
				self.preview_icon.LoadImage(icon_path)
				self.preview_icon.Show()
		except Exception:
			self.preview_icon.Hide()
		self.preview_name.SetText(nm or "?")
		self.preview_vnum.SetText("vnum: %d" % self.selected_vnum)

	def OnUpdate(self):
		# Frame poll: show the full item tooltip while the cursor is over the
		# preview icon (the uioxevent.py pattern).
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

	# -- confirm / lifecycle --------------------------------------------------
	def OnConfirm(self):
		if self.selected_vnum == 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO,
							"[DropEditor] Pick an item first")
			return
		try:
			cnt = int(self.count_edit.GetText() or "1")
		except Exception:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "[DropEditor] Bad count")
			return
		try:
			pct = float(self.pct_edit.GetText() or "0.5")
		except Exception:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "[DropEditor] Bad pct")
			return
		pct_x = int(pct * 10000)
		if pct_x <= 0 or pct_x > 1000000:
			chat.AppendChat(chat.CHAT_TYPE_INFO,
							"[DropEditor] Pct out of range (0 < pct <= 100)")
			return
		if cnt < 1:
			cnt = 1

		net.SendDropEditor(SUB_CG_ADD_ROW, self.file_kind, self.group_vnum,
						   self.group_name, 0, self.selected_vnum,
						   cnt, pct_x, 0)
		self.Close()

	def Open(self):
		self.Show()
		try:
			self.SetTop()
		except Exception:
			pass

	def Close(self):
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


# -----------------------------------------------------------------------------
# DropEditorWindow -- the drop-editor window. SpecialPageWindow creates one
# when the GM clicks "Edit drops" and owns its lifetime (see
# ingamewikiui.SpecialPageWindow._DropEditor_Mount).
#
# It is a standalone top-level ("float") window, NOT a child of the wiki: it
# opens beside the special page but sits outside the wiki's rect, and a child
# positioned outside its parent would not be click-pickable. It is therefore
# independently movable rather than docked to the wiki.
#
# Layout: title bar (caption + close X) -> ThinBoard list viewport with a
# ScrollBarNew down its right edge -> status line -> fixed footer
# (+ Add row / Discard / Save). Rows are DropRowEdit widgets of variable height
# (each sized to its item's slot footprint); all are created once and the
# subset that fits the viewport is shown/repositioned on scroll.
# -----------------------------------------------------------------------------

class DropEditorWindow(ui.BoardWithTitleBar):
	WIDTH        = 430
	HEIGHT       = 322
	MARGIN       = 10
	LIST_X       = 12
	LIST_TOP     = 32
	SCROLLBAR_W  = 12
	LIST_H       = 230                         # list viewport pixel height
	ROW_GAP      = 3                           # gap between row frames
	FOOTER_Y     = HEIGHT - 30                 # 292

	def __init__(self, file_kind, group_vnum, group_name, close_cb=None):
		ui.BoardWithTitleBar.__init__(self)
		# Standalone top-level window. It must NOT be a child of the wiki: it
		# sits to the right of the special page, outside the wiki's rect, and a
		# child positioned outside its parent is not click-pickable. "float"
		# makes it an independently pickable top-level window that also gets
		# OnPressEscapeKey; "movable" lets the GM drag it by the title bar.
		self.AddFlag("movable")
		self.AddFlag("float")
		self.file_kind  = int(file_kind)
		self.group_vnum = int(group_vnum)
		self.group_name = str(group_name or "")
		self._close_cb  = close_cb

		self._rows       = []
		self._basePos    = 0
		self._picker     = None
		self._subscribed = False

		self.SetSize(self.WIDTH, self.HEIGHT)
		self.SetTitleName("Editing %s drops" % (
			"monster" if self.file_kind == FK_MOB_DROP else "chest"))
		self.SetCloseEvent(ui.__mem_func__(self._OnClose))

		# List viewport frame (decorative) + the pickable row host inside it.
		self._listFrame = ui.ThinBoard()
		self._listFrame.SetParent(self)
		listFrameW = (self.WIDTH - self.LIST_X - self.SCROLLBAR_W - 4
					  - self.MARGIN)
		self._listFrame.SetSize(listFrameW, self.LIST_H)
		self._listFrame.SetPosition(self.LIST_X, self.LIST_TOP)
		self._listFrame.Show()

		self._rowHost = ui.Window()
		self._rowHost.SetParent(self._listFrame)
		self._rowHost.SetSize(listFrameW - 6, self.LIST_H - 6)
		self._rowHost.SetPosition(3, 3)
		self._rowHost.Show()

		# Scrollbar down the right edge of the viewport.
		self._scrollBar = ui.ScrollBarNew()
		self._scrollBar.SetParent(self)
		self._scrollBar.SetScrollBarSize(self.LIST_H)
		self._scrollBar.SetPosition(
			self.WIDTH - self.MARGIN - self.SCROLLBAR_W, self.LIST_TOP)
		self._scrollBar.SetScrollEvent(ui.__mem_func__(self._OnScroll))
		self._scrollBar.Hide()

		# Status line, just below the viewport.
		self._status = ui.TextLine()
		self._status.SetParent(self)
		self._status.SetPosition(self.LIST_X + 100,
								 self.LIST_TOP + self.LIST_H + 6)
		self._status.SetText("loading...")
		self._status.SetHorizontalAlignCenter()
		self._status.Show()

		# Footer: + Add row (left), Discard / Save (right). Fixed position --
		# never moved by the row count.
		self._addBtn = self._MakeFooterButton(
			localeinfo.DROP_EDITOR_ADD_ROW, 169, self._OnAddRow)
		self._discardBtn = self._MakeFooterButton(
			localeinfo.DROP_EDITOR_DISCARD, 56, self._OnDiscard)
		self._saveBtn = self._MakeFooterButton(
			localeinfo.DROP_EDITOR_SAVE, 280, self._OnSave)

		# Subscribe to GROUP_REFRESH acks, then ask the server for the rows.
		Subscribe(self.file_kind, self.group_vnum, self.group_name,
				  self._OnRowsRefresh)
		self._subscribed = True
		try:
			net.SendDropEditor(SUB_CG_FETCH, self.file_kind, self.group_vnum,
							   self.group_name, 0, 0, 0, 0, 0)
		except Exception:
			import traceback
			dbg.TraceError("DropEditor.DropEditorWindow fetch: "
						   + traceback.format_exc())

	def __del__(self):
		# Authoritative teardown is Close(); __del__ only unsubscribes as a
		# backstop, and only if Close() never ran. Unconditionally
		# unsubscribing here is unsafe: the registry is keyed by group, so a
		# deferred __del__ could pop a newer panel's callback.
		try:
			if getattr(self, "_subscribed", False):
				Unsubscribe(self.file_kind, self.group_vnum, self.group_name)
				self._subscribed = False
		except Exception:
			pass
		try:
			ui.BoardWithTitleBar.__del__(self)
		except Exception:
			pass

	def _MakeFooterButton(self, text, x, handler):
		btn = ui.Button()
		btn.SetParent(self)
		btn.SetUpVisual("d:/ymir work/ui/coupon/cancel_1.png")
		btn.SetOverVisual("d:/ymir work/ui/coupon/cancel_2.png")
		btn.SetDownVisual("d:/ymir work/ui/coupon/cancel_3.png")
		btn.SetText(text)
		btn.SetPosition(x, self.FOOTER_Y)
		btn.SAFE_SetEvent(handler)
		btn.Show()
		return btn

	# -- close ----------------------------------------------------------------
	def _OnClose(self):
		# SpecialPageWindow owns our lifetime; ask it to unmount us. If we were
		# somehow constructed without an owner, fall back to just hiding.
		if self._close_cb:
			try:
				self._close_cb()
			except Exception:
				import traceback
				dbg.TraceError("DropEditor.DropEditorWindow close: "
							   + traceback.format_exc())
		else:
			self.Hide()

	def Close(self):
		# Authoritative teardown -- SpecialPageWindow._DropEditor_Unmount calls
		# this before it drops us. Unsubscribe synchronously here (NOT only in
		# __del__): the refresh registry is keyed by group, so if a later panel
		# for the same group subscribes before this one is garbage-collected, a
		# deferred __del__ Unsubscribe would delete the new panel's callback and
		# leave it stuck on "loading...". Also drops the row widgets and the
		# item picker popup.
		if self._subscribed:
			try:
				Unsubscribe(self.file_kind, self.group_vnum, self.group_name)
			except Exception:
				pass
			self._subscribed = False
		self._ClearRows()
		try:
			if self._picker is not None:
				self._picker.Close()
				self._picker = None
		except Exception:
			pass
		self.Hide()

	def OnPressEscapeKey(self):
		# Escape closes the editor. Route through the owner so the
		# SpecialPageWindow clears its _dropEditorPanel reference.
		self._OnClose()
		return True

	# -- row list -------------------------------------------------------------
	def _ClearRows(self):
		for w in self._rows:
			try:
				w.Hide()
				w.SetParent(None)
			except Exception:
				pass
		self._rows = []

	def _OnRowsRefresh(self, rows):
		self._ClearRows()
		for r in rows:
			# Server sends 5-tuples (row_idx, vnum, count, pct_x10000,
			# rare_pct); tolerate extras / malformed entries.
			try:
				row_idx  = int(r[0])
				vnum     = int(r[1])
				count    = int(r[2])
				pct_x    = int(r[3])
				rare_pct = int(r[4]) if len(r) > 4 else 0
			except Exception:
				continue
			w = DropRowEdit(self.file_kind, self.group_vnum, self.group_name,
							row_idx, vnum, count, pct_x, rare_pct)
			w.SetParent(self._rowHost)
			w.Hide()
			self._rows.append(w)

		self._basePos = 0
		self._UpdateScrollBar()
		self._RefreshPositions()

		total = len(self._rows)
		if total == 0:
			self._status.SetText(localeinfo.DROP_EDITOR_NO_DROPS)
		else:
			self._status.SetText(localeinfo.DROP_EDITOR_ROWS % total)

	def _RefreshPositions(self):
		# Variable-height rows: stack from _basePos, showing each row that still
		# fits the viewport. The first row from _basePos is always shown, even
		# if it is taller than the viewport.
		viewport = self._rowHost.GetHeight()
		y = 0
		for i, w in enumerate(self._rows):
			if i < self._basePos:
				w.Hide()
				continue
			h = w.GetHeight()
			if y == 0 or y + h <= viewport:
				w.SetPosition(0, y)
				w.Show()
				y += h + self.ROW_GAP
			else:
				w.Hide()

	def _ContentHeight(self):
		h = 0
		for w in self._rows:
			h += w.GetHeight() + self.ROW_GAP
		return h

	def _ComputeMaxScroll(self):
		# Largest _basePos such that rows[_basePos:] still fit the viewport.
		viewport = self._rowHost.GetHeight()
		h = 0
		for i in xrange(len(self._rows) - 1, -1, -1):
			if h > 0:
				h += self.ROW_GAP
			h += self._rows[i].GetHeight()
			if h > viewport:
				return i + 1
		return 0

	def _UpdateScrollBar(self):
		maxScroll = self._ComputeMaxScroll()
		if maxScroll <= 0:
			self._scrollBar.Hide()
			return
		viewport = self._rowHost.GetHeight()
		total    = self._ContentHeight()
		frac     = 1.0
		if total > 0:
			frac = min(1.0, float(viewport) / float(total))
		self._scrollBar.SetMiddleBarSize(frac)
		self._scrollBar.SetPos(0.0, False)
		self._scrollBar.Show()

	def _OnScroll(self):
		maxScroll = self._ComputeMaxScroll()
		if maxScroll <= 0:
			self._basePos = 0
		else:
			self._basePos = min(
				maxScroll, int(round(self._scrollBar.GetPos() * maxScroll)))
		self._RefreshPositions()

	def OnRunMouseWheel(self, length):
		maxScroll = self._ComputeMaxScroll()
		if maxScroll <= 0:
			return False
		delta = -1 if length > 0 else 1     # wheel up -> show earlier rows
		self._basePos = max(0, min(maxScroll, self._basePos + delta))
		self._scrollBar.SetPos(float(self._basePos) / float(maxScroll), False)
		self._RefreshPositions()
		return True

	# -- footer actions -------------------------------------------------------
	def _OnAddRow(self):
		try:
			if self._picker is not None and self._picker.IsShow():
				self._picker.SetTop()
				return
			self._picker = ItemPicker(self.file_kind, self.group_vnum,
									  self.group_name)
			self._picker.Open()
		except Exception:
			import traceback
			dbg.TraceError("DropEditor.DropEditorWindow add: "
						   + traceback.format_exc())

	def _OnSave(self):
		net.SendDropEditor(SUB_CG_SAVE, 0, 0, "", 0, 0, 0, 0, 0)

	def _OnDiscard(self):
		net.SendDropEditor(SUB_CG_DISCARD, 0, 0, "", 0, 0, 0, 0, 0)
