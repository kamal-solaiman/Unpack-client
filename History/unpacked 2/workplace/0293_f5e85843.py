import app
import ui
import wndMgr
import localeinfo
import uicommon
import keybinds
import keyactions
import time
import math

ROW_H = 26
HEADER_H = 42
VISIBLE_ROWS = 13
LIST_H = 348
CELL_W = 195
CHIP_W = 88
CHIP_H = 18
LABEL_W = 90
ROOT = "d:/ymir work/ui/game/keyboard/"

class KeyChip(ui.ImageBox):
	def __init__(self, parent):
		ui.ImageBox.__init__(self)
		self.SetParent(parent)
		self.LoadImage(ROOT + "input_bg.png")
		self.text = ui.MakeTextLine(self)
		self.actionId = None
		self.slot = 0
		self.fixed = False
		self.capturing = False
		self.shownLabel = ""
		self.onClick = None
		self.onRightClick = None
		self.Show()

	def Setup(self, actionId, slot, label, fixed):
		self.actionId = actionId
		self.slot = slot
		self.fixed = fixed
		self.capturing = False
		self.SetDiffuseColor(1.0, 1.0, 1.0, 1.0)
		self._SetLabel(label)
		self.text.SetPackedFontColor(self._BaseColor())

	def _BaseColor(self):
		if self.fixed:
			return 0xFF888888
		return 0xFFFFFFFF

	def _SetLabel(self, label):
		self.text.SetText(label)
		if self.text.GetTextSize()[0] > CHIP_W - 6:
			cut = label
			while cut:
				cut = cut[:-1]
				self.text.SetText(cut + "..")
				if self.text.GetTextSize()[0] <= CHIP_W - 8:
					break
			label = cut + ".."
		self.shownLabel = label

	def SetCapturing(self, flag):
		self.capturing = flag
		if flag:
			self.text.SetText("...")
			self.text.SetPackedFontColor(0xFFFFC963)
		else:
			self.SetDiffuseColor(1.0, 1.0, 1.0, 1.0)
			self.text.SetText(self.shownLabel)
			self.text.SetPackedFontColor(self._BaseColor())

	def OnMouseOverIn(self):
		if self.fixed or self.capturing:
			return
		self.SetDiffuseColor(1.0, 0.85, 0.55, 1.0)
		self.text.SetPackedFontColor(0xFFFFE6A0)

	def OnMouseOverOut(self):
		if self.capturing:
			return
		self.SetDiffuseColor(1.0, 1.0, 1.0, 1.0)
		self.text.SetPackedFontColor(self._BaseColor())

	def OnMouseLeftButtonDown(self):
		if self.onClick:
			self.onClick(self)

	def OnMouseRightButtonDown(self):
		if self.onRightClick:
			self.onRightClick(self)

class RowWidget(object):
	def __init__(self, parent):
		self.base = ui.Window()
		self.base.SetParent(parent)
		self.base.SetSize(390, ROW_H)
		self.header = ui.ImageBox()
		self.header.SetParent(self.base)
		self.header.LoadImage(ROOT + "category_bg.png")
		self.header.AddFlag("not_pick")
		self.headerText = ui.MakeTextLine(self.header)
		self.cells = []
		for i in (0, 1):
			label = ui.TextLine()
			label.SetParent(self.base)
			label.SetFontName(localeinfo.UI_DEF_FONT)
			chip = KeyChip(self.base)
			self.cells.append((label, chip))
		self.base.Show()

	def SetHeader(self, text):
		self.base.SetSize(390, HEADER_H)
		self.header.SetPosition(1, 0)
		self.header.Show()
		self.headerText.SetText(text)
		for label, chip in self.cells:
			label.Hide()
			chip.Hide()

	def SetCells(self, cellDataList, arabic):
		self.base.SetSize(390, ROW_H)
		self.header.Hide()
		for i in (0, 1):
			label, chip = self.cells[i]
			if i < len(cellDataList):
				actionId, slot, name, chordText, fixed = cellDataList[i]
				colX = int(i * CELL_W)
				if arabic:
					colX = int((1 - i) * CELL_W)
					baseX = colX + CELL_W - 8
					label.SetPosition(baseX, 5)
					label.SetHorizontalAlignLeft()
					chip.SetPosition(colX + 4, 4)
				else:
					baseX = colX + 4
					label.SetPosition(baseX, 5)
					chip.SetPosition(colX + CELL_W - CHIP_W - 4, 4)
				self._SetLabelText(label, name, baseX)
				chip.Setup(actionId, slot, chordText, fixed)
				label.Show()
				chip.Show()
			else:
				label.Hide()
				chip.Hide()

	def _SetLabelText(self, label, name, baseX):
		label.baseX = baseX
		label.fullText = name
		label.SetText(name)
		w, h = label.GetTextSize()
		label.textW = w
		label.textH = h
		label.marqueeOver = w > LABEL_W
		if label.marqueeOver:
			cut = name
			while cut:
				cut = cut[:-1]
				label.SetText(cut + "..")
				if label.GetTextSize()[0] <= LABEL_W - 6:
					break
			label.shortText = cut + ".."
		else:
			label.shortText = name

class KeyBindWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.board = None
		self.titleBar = None
		self.searchInput = None
		self.searchBack = None
		self.resetButton = None
		self.listArea = None
		self.listScrollBar = None
		self.rows = []
		self.displayList = []
		self.scrollOffset = 0
		self.lastSearch = ""
		self.snapshot = None
		self.popup = None
		self.captureChip = None
		self.actionById = {}
		self.chipClickHandler = ui.__mem_func__(self._OnChipClick)
		self.chipRightClickHandler = ui.__mem_func__(self._OnChipRightClick)
		self.captureHandler = ui.__mem_func__(self._OnCapture)
		self.resetButtonHandler = ui.__mem_func__(self._OnReset)
		self.resetAcceptHandler = ui.__mem_func__(self._DoReset)
		self.resetCancelHandler = ui.__mem_func__(self._ClosePopup)
		self.dirtyAcceptHandler = ui.__mem_func__(self._ApplyAndClose)
		self.dirtyCancelHandler = ui.__mem_func__(self._DiscardAndClose)
		self.stealAcceptHandler = ui.__mem_func__(self._AcceptSteal)
		self.stealCancelHandler = ui.__mem_func__(self._CancelSteal)
		self.pendingBind = None
		self._fixedText = {
			"show_names" : keyactions.DikName(app.DIK_LALT),
			"next_target" : keyactions.DikName(app.DIK_TAB),
		}
		self.canClip = hasattr(ui.Window, "SetClippingMaskRect")
		self.marqueeHot = None
		self.marqueeSince = 0.0
		self.marqueeOffset = 0.0
		self.marqueeDone = False
		self.marqueeHitTime = 0.0
		self.marqueeLastTime = time.time()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadWindow(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/keybind_window.py")
		self.board = self.GetChild("board")
		self.titleBar = self.GetChild("TitleBar")
		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))
		self.searchInput = self.GetChild("SearchInput")
		self.searchInput.SetPlaceHolder(getattr(localeinfo, "KEYBIND_SEARCH", "Search key.."))
		self.searchInput.SetEscapeEvent(ui.__mem_func__(self._OnSearchEscape))
		self.searchBack = self.GetChild("SearchBack")
		self.searchBack.OnMouseLeftButtonDown = self._OnSearchFocus
		self.resetButton = self.GetChild("ResetButton")
		self.resetButton.SetEvent(self.resetButtonHandler)
		self.listArea = self.GetChild("ListArea")
		self.listScrollBar = self.GetChild("ListScrollBar")
		self.listScrollBar.SetScrollEvent(ui.__mem_func__(self._OnScroll))
		self.listScrollBar.SetScrollStep(0.2)
		self.rows = []
		for i in xrange(VISIBLE_ROWS):
			row = RowWidget(self.listArea)
			row.base.SetPosition(0, int(i * ROW_H))
			self.rows.append(row)

	def _OnSearchFocus(self):
		self.searchInput.SetFocus()

	def _OnSearchEscape(self):
		self.searchInput.KillFocus()

	def _BuildDisplayList(self, searchText):
		entries = []
		needle = searchText.strip().lower()
		for catConst, catLocale in keyactions.CATEGORIES:
			cells = []
			for act in keybinds.GetActions():
				if act.category != catConst:
					continue
				name = getattr(localeinfo, act.locale, act.id)
				if needle and name.lower().find(needle) < 0:
					continue
				binds = keybinds.GetBinds(act.id)
				for slot in xrange(act.slots):
					if act.fixed:
						chordText = self._fixedText.get(act.id, "")
					elif slot < len(binds) and binds[slot]:
						chordText = keybinds.ChordName(binds[slot][0], binds[slot][1])
					else:
						chordText = ""
					cells.append((act.id, slot, name, chordText, act.fixed))
			if not cells:
				continue
			entries.append(("header", getattr(localeinfo, catLocale, "")))
			for i in xrange(0, len(cells), 2):
				entries.append(("cells", cells[i:i+2]))
		return entries

	def _Rebuild(self):
		self._CancelCapture()
		self.actionById = {}
		for act in keybinds.GetActions():
			self.actionById[act.id] = act
		searchText = self.searchInput.GetText() if self.searchInput else ""
		searchChanged = searchText != self.lastSearch
		self.lastSearch = searchText
		self.displayList = self._BuildDisplayList(searchText)
		maxOffset = self._MaxOffset()
		if searchChanged:
			self.scrollOffset = 0
		elif self.scrollOffset > maxOffset:
			self.scrollOffset = maxOffset
		self._UpdateScrollBar()
		self._FillRows()

	def _ActionById(self, actionId):
		return self.actionById.get(actionId)

	def _EntryHeight(self, entry):
		if entry[0] == "header":
			return HEADER_H
		return ROW_H

	def _MaxOffset(self):
		total = len(self.displayList)
		used = 0
		count = 0
		i = total - 1
		while i >= 0:
			h = self._EntryHeight(self.displayList[i])
			if used + h > LIST_H:
				break
			used += h
			count += 1
			i -= 1
		return max(0, total - count)

	def _UpdateScrollBar(self):
		if not self.listScrollBar:
			return
		total = len(self.displayList)
		maxOffset = self._MaxOffset()
		if total <= 0:
			pageScale = 1.0
		else:
			pageScale = min(1.0, float(total - maxOffset) / float(total))
		self.listScrollBar.SetMiddleBarSize(pageScale)
		if maxOffset <= 0:
			pos = 0.0
		else:
			pos = float(self.scrollOffset) / float(maxOffset)
		self.listScrollBar.SetPos(pos, False)

	def _OnScroll(self):
		if self.captureChip:
			self._CancelCapture()
		maxOffset = self._MaxOffset()
		if maxOffset <= 0 or not self.listScrollBar:
			self.scrollOffset = 0
		else:
			pos = self.listScrollBar.GetPos()
			self.scrollOffset = int(round(pos * maxOffset))
		self._FillRows()

	def _FillRows(self):
		self._MarqueeRest()
		arabic = localeinfo.IsARABIC()
		total = len(self.displayList)
		idx = self.scrollOffset
		y = 0
		overflow = False
		for i in xrange(VISIBLE_ROWS):
			row = self.rows[i]
			kind = None
			if not overflow and idx < total:
				kind, data = self.displayList[idx]
				h = self._EntryHeight(self.displayList[idx])
				if y + h > LIST_H:
					overflow = True
					kind = None
			if kind is None:
				row.SetCells([], arabic)
				continue
			row.base.SetPosition(0, int(y))
			if kind == "header":
				row.SetHeader(data)
			else:
				row.SetCells(data, arabic)
				for label, chip in row.cells:
					chip.onClick = self.chipClickHandler
					chip.onRightClick = self.chipRightClickHandler
			y += h
			idx += 1

	def _OnChipClick(self, chip):
		if self.popup:
			return
		act = self._ActionById(chip.actionId)
		if act is None or act.fixed:
			return
		self._CancelCapture()
		self.searchInput.KillFocus()
		self.captureChip = chip
		chip.SetCapturing(True)
		keybinds.SetCaptureHandler(self.captureHandler)

	def _ActionName(self, actionId):
		act = self._ActionById(actionId)
		if act:
			return getattr(localeinfo, act.locale, actionId)
		return actionId

	def _OnCapture(self, mask, dik):
		chip = self.captureChip
		if not chip:
			self._CancelCapture()
			return
		if not keyactions.IsBindableDik(dik):
			return
		self._CancelCapture()
		ownerId = keybinds.FindOwner(mask, dik)
		if ownerId and ownerId != chip.actionId:
			if self.popup:
				return
			self.pendingBind = (chip.actionId, chip.slot, mask, dik)
			popup = uicommon.QuestionDialog()
			popup.SetText(getattr(localeinfo, "KEYBIND_STEAL_CONFIRM", "%s: move from %s to %s?") % (
				keybinds.ChordName(mask, dik),
				self._ActionName(ownerId),
				self._ActionName(chip.actionId)))
			popup.SetWidth(max(340, int(popup.textLine.GetTextSize()[0]) + 60))
			popup.SetAcceptEvent(self.stealAcceptHandler)
			popup.SetCancelEvent(self.stealCancelHandler)
			popup.Open()
			self.popup = popup
			return
		keybinds.SetBind(chip.actionId, chip.slot, mask, dik)
		self._Rebuild()

	def _AcceptSteal(self):
		self._ClosePopup()
		pend = self.pendingBind
		self.pendingBind = None
		if pend:
			keybinds.SetBind(pend[0], pend[1], pend[2], pend[3])
		self._Rebuild()

	def _CancelSteal(self):
		self._ClosePopup()
		self.pendingBind = None
		self._Rebuild()

	def _CancelCapture(self):
		keybinds.SetCaptureHandler(None)
		if self.captureChip:
			self.captureChip.SetCapturing(False)
		self.captureChip = None

	def _OnChipRightClick(self, chip):
		act = self._ActionById(chip.actionId)
		if act is None or act.fixed:
			return
		keybinds.ClearBind(chip.actionId, chip.slot)
		self._Rebuild()

	def OnRunMouseWheel(self, nLen):
		if not self.IsShow():
			return False
		if self.listScrollBar and self.listScrollBar.IsShow():
			if self.listScrollBar.IsInPosition() or (self.listArea and self.listArea.IsInPosition()):
				if nLen > 0:
					self.listScrollBar.OnUp()
				else:
					self.listScrollBar.OnDown()
				return True
		return False

	def OnUpdate(self):
		if not self.searchInput:
			return
		if not self.IsShow():
			return
		if self.searchInput.GetText() != self.lastSearch:
			self._Rebuild()
		now = time.time()
		if self.captureChip:
			pulse = 0.65 + 0.35 * math.sin(now * 6.0)
			self.captureChip.SetDiffuseColor(1.0, 0.8, 0.35, pulse)
		self._MarqueeUpdate(now)

	MARQUEE_SPEED = 60.0
	MARQUEE_DELAY = 0.4
	MARQUEE_HIT_INTERVAL = 0.1

	def _MarqueeHitTest(self):
		xm, ym = wndMgr.GetMousePosition()
		rtl = localeinfo.IsARABIC()
		for row in self.rows:
			for label, chip in row.cells:
				if not label.IsShow() or not getattr(label, "marqueeOver", False):
					continue
				x, y = label.GetGlobalPosition()
				h = getattr(label, "textH", 14)
				if rtl:
					inside = xm >= x - LABEL_W and xm < x + 12 and ym >= y and ym < y + h
				else:
					inside = xm >= x and xm < x + LABEL_W and ym >= y and ym < y + h
				if inside:
					return label
		return None

	def _MarqueeRest(self):
		label = self.marqueeHot
		self.marqueeHot = None
		self.marqueeOffset = 0.0
		self.marqueeDone = False
		if not label:
			return
		label.SetPosition(int(getattr(label, "baseX", 0)), 5)
		label.SetText(getattr(label, "shortText", ""))
		if self.canClip:
			label.SetClippingMaskRect(0, 0, wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())

	def _MarqueeMask(self, label, offset):
		if not self.canClip:
			return
		gx, gy = label.GetGlobalPosition()
		h = getattr(label, "textH", 14)
		if localeinfo.IsARABIC():
			base = gx - offset
			label.SetClippingMaskRect(int(base - LABEL_W), int(gy), int(base + 12), int(gy + h))
		else:
			base = gx + offset
			label.SetClippingMaskRect(int(base), int(gy), int(base + LABEL_W), int(gy + h))

	def _MarqueeUpdate(self, now):
		dt = now - self.marqueeLastTime
		self.marqueeLastTime = now
		if dt <= 0.0 or dt > 0.5:
			dt = 0.0
		if now - self.marqueeHitTime >= self.MARQUEE_HIT_INTERVAL:
			self.marqueeHitTime = now
			hot = self._MarqueeHitTest()
			if hot is not self.marqueeHot:
				self._MarqueeRest()
				if hot:
					self.marqueeHot = hot
					self.marqueeSince = now
		label = self.marqueeHot
		if not label:
			return
		if now - self.marqueeSince < self.MARQUEE_DELAY:
			return
		full = getattr(label, "fullText", "")
		if label.GetText() != full:
			label.SetText(full)
			self.marqueeOffset = 0.0
			self.marqueeDone = False
			self._MarqueeMask(label, 0.0)
			return
		travel = getattr(label, "textW", 0) - LABEL_W
		if travel <= 0:
			return
		if not self.marqueeDone:
			self.marqueeOffset += self.MARQUEE_SPEED * dt
			if self.marqueeOffset >= travel:
				self.marqueeOffset = float(travel)
				self.marqueeDone = True
			baseX = getattr(label, "baseX", 0)
			if localeinfo.IsARABIC():
				label.SetPosition(int(baseX + self.marqueeOffset), 5)
			else:
				label.SetPosition(int(baseX - self.marqueeOffset), 5)
		self._MarqueeMask(label, self.marqueeOffset)

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()
		self.snapshot = keybinds.Snapshot()
		self.lastSearch = ""
		self._Rebuild()

	def _OnReset(self):
		self._CancelCapture()
		if self.popup:
			return
		popup = uicommon.QuestionDialog()
		popup.SetText(getattr(localeinfo, "KEYBIND_RESET_CONFIRM", "Restore all keys to default?"))
		popup.SetAcceptEvent(self.resetAcceptHandler)
		popup.SetCancelEvent(self.resetCancelHandler)
		popup.Open()
		self.popup = popup

	def _DoReset(self):
		self._ClosePopup()
		keybinds.ResetDefaults()
		self._Rebuild()

	def _ClosePopup(self):
		if self.popup:
			self.popup.Close()
		self.popup = None

	def Close(self):
		self._CancelCapture()
		if self.snapshot is not None and keybinds.IsDirtySince(self.snapshot):
			if self.popup:
				return
			popup = uicommon.QuestionDialog()
			popup.SetText(getattr(localeinfo, "KEYBIND_DIRTY_CONFIRM", "Apply key changes?"))
			popup.SetAcceptText(getattr(localeinfo, "KEYBIND_APPLY", "Apply"))
			popup.SetCancelText(getattr(localeinfo, "KEYBIND_DISCARD", "Discard"))
			popup.SetAcceptEvent(self.dirtyAcceptHandler)
			popup.SetCancelEvent(self.dirtyCancelHandler)
			popup.Open()
			self.popup = popup
			return
		self._ReallyClose()

	def _ApplyAndClose(self):
		self._ClosePopup()
		keybinds.SaveFile()
		self._ReallyClose()

	def _DiscardAndClose(self):
		self._ClosePopup()
		if self.snapshot is not None:
			keybinds.Restore(self.snapshot)
		self._ReallyClose()

	def _ReallyClose(self):
		self._CancelCapture()
		self._ClosePopup()
		self.pendingBind = None
		self.snapshot = None
		self.Hide()

	def OnPressEscapeKey(self):
		if self.captureChip:
			self._CancelCapture()
			self._Rebuild()
		else:
			self.Close()
		return True
