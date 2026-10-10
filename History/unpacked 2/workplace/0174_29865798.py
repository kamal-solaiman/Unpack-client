# coding: ascii

import ui
import uitooltip
import uiRenderTarget
import localeinfo
import item
import player
import net
import app
from _weakref import proxy


class BundleBoxWindow(ui.NewBoardWithTitleBar):

	SLOT          = 32
	SLOT_GAP      = 8
	ITEMS_PER_ROW = 7
	ROW_PITCH     = SLOT + SLOT_GAP
	CONTENT_WIDTH = ITEMS_PER_ROW * ROW_PITCH - SLOT_GAP
	CONTENT_PAD   = 16
	TITLE_BAR_H   = 32
	CAT_GAP       = 10
	BOTTOM_PAD    = 12
	BTN_GAP       = 8
	PREVIEW_W     = 130
	PREVIEW_H     = 190
	BACKDROP_PAD  = 8
	SLOT_BG_IMAGE = "d:/ymir work/ui/public/slot_base.sub"

	def __init__(self):
		ui.NewBoardWithTitleBar.__init__(self)

		self.interface = None
		self.nonce = "0"
		self.boxVnum = 0
		self.categories = {}
		self.guaranteed = []
		self.selected = {}
		self.previewOpen = False

		self.__ClearBuilt()

		self.tooltipItem = uitooltip.ItemToolTip()
		self.tooltipItem.Hide()

		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetCloseEvent(ui.__mem_func__(self.Close))

	def __del__(self):
		ui.NewBoardWithTitleBar.__del__(self)

	def SetInterface(self, interface):
		self.interface = proxy(interface)

	def __ClearBuilt(self):
		self.catSlotWnd = {}
		self.guarSlotWnd = None
		self.contentBoard = None
		self.confirmBtn = None
		self.previewBtn = None
		self.previewBoard = None
		self.previewRender = None
		self.slotBgImages = []
		self.stripBgWnd = []

	def Destroy(self):
		self.__ClearBuilt()
		if getattr(self, "tooltipItem", None):
			self.tooltipItem.Hide()
		self.tooltipItem = None

	# --- Feed: accumulates S/C/G lines, builds + opens on E -----------------

	def Feed(self, payload):
		if not payload:
			return

		parts = payload.split("|")
		op = parts[0]

		if op == "S":
			self.nonce = parts[1]
			self.boxVnum = int(parts[2])
			self.categories = {}
			self.guaranteed = []
			self.selected = {}
			self.previewOpen = False

		elif op == "C":
			idx = int(parts[1])
			cat = self.categories.setdefault(idx, {"label": parts[2], "pick": int(parts[3]), "items": []})
			for entry in parts[4].split(","):
				if ":" in entry:
					v, c = entry.split(":")
					cat["items"].append((int(v), int(c)))

		elif op == "G":
			for entry in parts[1].split(","):
				if ":" in entry:
					v, c = entry.split(":")
					self.guaranteed.append((int(v), int(c)))

		elif op == "E":
			self.__Build()
			self.Open()

	# --- Build ---------------------------------------------------------------

	def __ItemHeightCells(self, vnum):
		item.SelectItem(vnum)
		(_w, h) = item.GetItemSize()
		h = int(h)
		if h < 1:
			h = 1
		elif h > 3:
			h = 3
		return h

	def __AddSlotBackground(self, parent, x, y, cellHeight):
		for cell in xrange(cellHeight):
			bg = ui.ImageBox()
			bg.SetParent(parent)
			bg.AddFlag("not_pick")
			bg.LoadImage(self.SLOT_BG_IMAGE)
			bg.SetPosition(int(x), int(y + cell * self.SLOT))
			bg.Show()
			self.slotBgImages.append(bg)

	def __BuildStrip(self, items, y, rtl, contentX):
		itemCount = len(items)
		itemsPerRow = self.ITEMS_PER_ROW

		heights = [self.__ItemHeightCells(vnum) for (vnum, _count) in items]
		maxHeight = max(heights) if heights else 1
		lineHeight = maxHeight * self.SLOT

		rowCount = 1
		if itemCount:
			rowCount = (itemCount + itemsPerRow - 1) // itemsPerRow
		stripHeight = int(max(self.SLOT, rowCount * lineHeight))

		# Background art rides a plain ui.Window sibling, NOT a child of the
		# SlotWindow. CSlotWindow::OnRender (PythonSlotWindow.cpp) manually
		# renders its own m_pChildList before drawing item icons, but the
		# generic CWindow::Render wrapper (PythonWindow.cpp) ALSO renders
		# every child again, unconditionally, AFTER OnRender() (icons
		# included) returns -- so a child parented directly into a
		# SlotWindow gets drawn twice, and the second pass paints over the
		# icon. A same-rect sibling created (and SetParent'd) before the
		# SlotWindow renders once, in creation order, underneath it.
		bgWnd = ui.Window()
		bgWnd.SetParent(self)
		bgWnd.AddFlag("not_pick")
		bgWnd.SetPosition(int(contentX), int(y))
		bgWnd.SetSize(int(self.CONTENT_WIDTH), stripHeight)
		bgWnd.Show()
		self.stripBgWnd.append(bgWnd)

		slotWnd = ui.SlotWindow()
		slotWnd.SetParent(self)
		slotWnd.SetPosition(int(contentX), int(y))
		slotWnd.SetSize(int(self.CONTENT_WIDTH), stripHeight)
		slotWnd.Show()

		for i, (vnum, count) in enumerate(items):
			line = i // itemsPerRow
			col = i % itemsPerRow
			rowItems = min(itemsPerRow, itemCount - line * itemsPerRow)
			rowOffset = (self.CONTENT_WIDTH - (rowItems * self.ROW_PITCH - self.SLOT_GAP)) // 2
			dispCol = (rowItems - 1 - col) if rtl else col

			itemHeight = heights[i]
			pixHeight = int(itemHeight * self.SLOT)
			cellX = int(rowOffset + dispCol * self.ROW_PITCH)
			cellY = int(line * lineHeight + (lineHeight - pixHeight) // 2)

			self.__AddSlotBackground(bgWnd, cellX, cellY, itemHeight)

			slotWnd.AppendSlot(i, cellX, cellY, self.SLOT, pixHeight)
			slotWnd.SetItemSlot(i, vnum, count if count and count > 1 else 0)

		return slotWnd, stripHeight

	def __Build(self):
		self.__ClearBuilt()

		rtl = localeinfo.IsARABIC()

		showPreview = bool(app.ENABLE_RENDER_TARGET and self.__BuildPreviewSlots())
		paneWidth = (self.PREVIEW_W + self.CONTENT_PAD) if showPreview else 0
		panelWidth = int(self.CONTENT_WIDTH + self.CONTENT_PAD * 2 + paneWidth)

		contentX = self.CONTENT_PAD + (paneWidth if rtl else 0)
		previewX = self.CONTENT_PAD if rtl else (self.CONTENT_PAD + self.CONTENT_WIDTH + self.CONTENT_PAD)

		self.contentBoard = ui.ThinBoard("UI", 2)
		self.contentBoard.SetParent(self)
		self.contentBoard.Show()

		y = self.TITLE_BAR_H + self.CONTENT_PAD
		backdropTop = y - self.BACKDROP_PAD

		for catIdx in sorted(self.categories.keys()):
			cat = self.categories[catIdx]

			slotWnd, stripHeight = self.__BuildStrip(cat["items"], y, rtl, contentX)
			slotWnd.SetOverInItemEvent(ui.__mem_func__(self.__OnCatOverIn), catIdx + 1)
			slotWnd.SetOverOutItemEvent(ui.__mem_func__(self.__OnOverOut))
			slotWnd.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnCatPick), catIdx + 1)
			self.catSlotWnd[catIdx] = slotWnd

			y += stripHeight + self.CAT_GAP

		if self.guaranteed:
			guarSlotWnd, stripHeight = self.__BuildStrip(self.guaranteed, y, rtl, contentX)
			guarSlotWnd.SetOverInItemEvent(ui.__mem_func__(self.__OnGuarOverIn))
			guarSlotWnd.SetOverOutItemEvent(ui.__mem_func__(self.__OnOverOut))
			guarSlotWnd.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnGuarPick))
			self.guarSlotWnd = guarSlotWnd

			y += stripHeight + self.CAT_GAP

		if showPreview:
			# a short box must still leave room for the model
			y = max(y, backdropTop + self.PREVIEW_H + self.BACKDROP_PAD * 2)

		self.contentBoard.SetPosition(int(contentX - self.BACKDROP_PAD), int(backdropTop))
		self.contentBoard.SetSize(int(self.CONTENT_WIDTH + self.BACKDROP_PAD * 2), int(y - backdropTop))

		if showPreview:
			self.previewBoard = ui.ThinBoard("UI", 2)
			self.previewBoard.SetParent(self)
			self.previewBoard.SetPosition(int(previewX - self.BACKDROP_PAD), int(backdropTop))
			self.previewBoard.SetSize(int(self.PREVIEW_W + self.BACKDROP_PAD * 2), int(y - backdropTop))
			self.previewBoard.Show()

			renderY = int(backdropTop + ((y - backdropTop) - self.PREVIEW_H) // 2)
			self.previewRender = uiRenderTarget.SetPreviewRender(self, int(previewX), renderY, self.PREVIEW_W, self.PREVIEW_H, True)
			self.previewRender.SetEvent(ui.__mem_func__(self.__OnPreviewClick), "mouse_click")

		y += 6

		self.confirmBtn = ui.Button()
		self.confirmBtn.SetParent(self)
		self.confirmBtn.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.confirmBtn.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.confirmBtn.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.confirmBtn.SetDisableVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.confirmBtn.SetText(getattr(localeinfo, "BUNDLEBOX_CONFIRM", "Open Box"))
		self.confirmBtn.SAFE_SetEvent(self.__OnConfirm)
		self.confirmBtn.Show()

		buttonRow = [self.confirmBtn]
		if showPreview:
			self.previewBtn = ui.Button()
			self.previewBtn.SetParent(self)
			self.previewBtn.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			self.previewBtn.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
			self.previewBtn.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
			self.previewBtn.SetDisableVisual("d:/ymir work/ui/public/large_button_03.sub")
			self.previewBtn.SetText(getattr(localeinfo, "BUNDLEBOX_PREVIEW", "Preview Set"))
			self.previewBtn.SAFE_SetEvent(self.__OnPreview)
			self.previewBtn.Show()
			buttonRow.insert(0, self.previewBtn)

		if rtl:
			buttonRow.reverse()

		rowWidth = sum([btn.GetWidth() for btn in buttonRow]) + self.BTN_GAP * (len(buttonRow) - 1)
		btnX = int((panelWidth - rowWidth) // 2)
		for btn in buttonRow:
			btn.SetPosition(btnX, int(y))
			btnX += btn.GetWidth() + self.BTN_GAP

		y += self.confirmBtn.GetHeight() + self.BOTTOM_PAD

		self.SetSize(panelWidth, int(y))

		item.SelectItem(self.boxVnum)
		title = item.GetItemName()
		if not title:
			title = getattr(localeinfo, "BUNDLEBOX_DEFAULT_TITLE", "Bundle Box")
		self.SetTitleName(title)

		self.__RefreshSelection()

	# --- Hover -> shared private tooltip -------------------------------------

	def __ShowItemTooltip(self, vnum):
		if not self.tooltipItem or not vnum:
			return
		metinSlot = [0 for _i in xrange(player.METIN_SOCKET_MAX_NUM)]
		attrSlot = [(0, 0) for _i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
		self.tooltipItem.ClearToolTip()
		self.tooltipItem.AddItemData(vnum, metinSlot, attrSlot)
		self.tooltipItem.ShowToolTip()

	def __OnCatOverIn(self, slotIndex, catIdxPlusOne):
		cat = self.categories.get(catIdxPlusOne - 1)
		if not cat or slotIndex < 0 or slotIndex >= len(cat["items"]):
			return
		self.__ShowItemTooltip(cat["items"][slotIndex][0])

	def __OnGuarOverIn(self, slotIndex):
		if slotIndex < 0 or slotIndex >= len(self.guaranteed):
			return
		self.__ShowItemTooltip(self.guaranteed[slotIndex][0])

	def __OnOverOut(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	# --- Selection -------------------------------------------------------------

	def __PreviewClickHandled(self, vnum):
		if not app.ENABLE_RENDER_TARGET:
			return False
		if not app.IsPressed(app.DIK_LSHIFT):
			return False
		if uiRenderTarget.IsCanShowItems(vnum) and self.interface:
			self.interface.OpenRenderTargetWindow(0, vnum)
		return True

	def __OnGuarPick(self, slotIndex):
		if slotIndex < 0 or slotIndex >= len(self.guaranteed):
			return
		self.__PreviewClickHandled(self.guaranteed[slotIndex][0])

	def __OnCatPick(self, slotIndex, catIdxPlusOne):
		catIdx = catIdxPlusOne - 1
		cat = self.categories.get(catIdx)
		if not cat:
			return
		items = cat["items"]
		if slotIndex < 0 or slotIndex >= len(items):
			return

		vnum = items[slotIndex][0]
		if self.__PreviewClickHandled(vnum):
			return
		if cat["pick"] <= 0:
			return

		picks = self.selected.setdefault(catIdx, [])
		if vnum in picks:
			picks.remove(vnum)
		elif cat["pick"] == 1:
			del picks[:]
			picks.append(vnum)
		elif len(picks) < cat["pick"]:
			picks.append(vnum)

		self.__RefreshSelection()

	# --- Set preview ---------------------------------------------------------

	# What the character would be wearing right now: real picks first, then the
	# guaranteed items, then the first wearable of each still-unpicked category so
	# the look is never half-empty. Mount/pet entries drop out via GetWearableSlot.
	def __BuildPreviewSlots(self):
		slots = {}

		def claim(vnum):
			slotName = uiRenderTarget.GetWearableSlot(vnum)
			if slotName and slotName not in slots:
				slots[slotName] = vnum

		for catIdx in sorted(self.categories.keys()):
			for vnum in self.selected.get(catIdx, []):
				claim(vnum)

		for (vnum, _count) in self.guaranteed:
			claim(vnum)

		for catIdx in sorted(self.categories.keys()):
			if self.selected.get(catIdx):
				continue
			for (vnum, _count) in self.categories[catIdx]["items"]:
				if uiRenderTarget.GetWearableSlot(vnum):
					claim(vnum)
					break

		return slots

	def __OnPreview(self):
		if not self.interface:
			return
		slots = self.__BuildPreviewSlots()
		if not slots:
			return
		self.previewOpen = bool(self.interface.OpenRenderTargetWindowSet(slots))

	def __OnPreviewClick(self, *args):
		self.__OnPreview()

	def __RefreshPreview(self):
		if not self.previewRender and not self.previewOpen:
			return

		slots = self.__BuildPreviewSlots()

		if self.previewRender:
			self.previewRender.SetSlots(slots, net.GetMainActorRace())

		if self.previewOpen and self.interface:
			# stops re-dressing once the player closes the render window
			self.previewOpen = bool(self.interface.RefreshRenderTargetWindowSet(slots))

	def __RefreshSelection(self):
		for catIdx, slotWnd in self.catSlotWnd.items():
			cat = self.categories.get(catIdx)
			if not cat:
				continue
			picks = self.selected.get(catIdx, [])
			for i, (vnum, count) in enumerate(cat["items"]):
				if vnum in picks:
					slotWnd.ActivateSlot(i)
				else:
					slotWnd.DeactivateSlot(i)
		self.__SetConfirmEnabled(self.__AllPicked())
		self.__RefreshPreview()

	def __AllPicked(self):
		for catIdx, cat in self.categories.items():
			need = min(cat["pick"], len(cat["items"]))
			if need > 0 and len(self.selected.get(catIdx, [])) != need:
				return False
		return True

	def __SetConfirmEnabled(self, enabled):
		if not self.confirmBtn:
			return
		if enabled:
			self.confirmBtn.Enable()
		else:
			self.confirmBtn.Disable()

	def __OnConfirm(self):
		if not self.__AllPicked():
			return

		pairs = []
		for catIdx in sorted(self.selected.keys()):
			for vnum in self.selected[catIdx]:
				pairs.append("%d:%d" % (int(catIdx), int(vnum)))

		net.SendChatPacket("/bundlebox_confirm %s|%s" % (self.nonce, ",".join(pairs)))

	# --- Lifecycle -------------------------------------------------------------

	def OnDone(self):
		self.Close()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Open(self):
		if self.previewRender:
			self.previewRender.Show()
			self.__RefreshPreview()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		if getattr(self, "tooltipItem", None):
			self.tooltipItem.HideToolTip()
		self.previewOpen = False
		if self.previewRender:
			# a hidden bundle box must stop feeding a model to the render loop
			self.previewRender.Hide()
		self.Hide()
