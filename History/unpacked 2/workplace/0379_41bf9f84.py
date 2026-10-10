import app
import ui
import wndMgr
import player
import item
import net
import chat
import localeinfo

PATH_QT = "d:/ymir work/ui/game/quicktransfer/"

QT_WIDTH = 299
QT_HEIGHT = 482
QT_BG_X = 8
QT_BG_Y = 36
QT_BOARD_W = QT_WIDTH + QT_BG_X * 2
QT_BOARD_H = QT_HEIGHT + QT_BG_Y + 8
QT_ROW_WIDTH = 247
QT_ROW_HEIGHT = 112
QT_ROW_X = QT_BG_X + 26
QT_VIEW_Y = QT_BG_Y + 206
QT_VIEW_H = 226
QT_ROW_STEP = QT_ROW_HEIGHT + 2
QT_SCROLL_STEP = QT_ROW_STEP // 2
QT_SLOT_W = 36
QT_SLOT_H = 108

QT_CONFIRM_W = 279
QT_CONFIRM_H = 350

QT_COLOR_TITLE = 0xffE8D5A3
QT_COLOR_PRICE = 0xffFFD86C
QT_COLOR_ATTR = 0xff86E57F
QT_COLOR_ENCHANT = 0xffFFC800
QT_COLOR_CAPTION = 0xffE8D5A3
QT_COLOR_MESSAGE = 0xffC87878
QT_COLOR_EMPTY = 0xffB4B4B4
QT_TINT_HOVER = 0x1eFFC873
QT_TINT_SELECTED = 0x46FFC873


def _QTGetCost():
	return getattr(app, "QUICK_ATTR_TRANSFER_GOLD_COST", 50000000)


def _QTMoneyString(value):
	if hasattr(localeinfo, "NumberToMoneyString"):
		return localeinfo.NumberToMoneyString(value)
	return str(value)


def _QTGetAffectString(affectType, affectValue):
	if 0 == affectType or 0 == affectValue:
		return None
	import uitooltip
	if hasattr(uitooltip, "GET_AFFECT_STRING"):
		return uitooltip.GET_AFFECT_STRING(affectType, affectValue)
	try:
		affectString = uitooltip.ItemToolTip.AFFECT_DICT[affectType]
	except KeyError:
		return None
	if type(affectString) != str:
		return affectString(affectValue)
	if affectString.find("%d") != -1:
		return affectString % affectValue
	return affectString


class QuickTransferRow(ui.Window):
	def __init__(self, parent, rowIndex, selectEvent, wheelEvent, overEvent, outEvent):
		ui.Window.__init__(self)
		self.rowIndex = rowIndex
		self.selectEvent = selectEvent
		self.wheelEvent = wheelEvent
		self.overEvent = overEvent
		self.outEvent = outEvent
		self.slotPos = -1
		self.selected = False
		self.hovered = False

		self.SetParent(parent)
		self.SetSize(QT_ROW_WIDTH, QT_ROW_HEIGHT)

		if localeinfo.IsARABIC():
			self.slotX = 6
			self.textCenterX = 144
		else:
			self.slotX = QT_ROW_WIDTH - QT_SLOT_W - 6
			self.textCenterX = 102

		self.bg = ui.ExpandedImageBox()
		self.bg.SetParent(self)
		self.bg.LoadImage(PATH_QT + "item_bg.png")
		self.bg.SetPosition(0, 0)
		self.bg.AddFlag("not_pick")
		self.bg.Show()

		self.slotImg = ui.ExpandedImageBox()
		self.slotImg.SetParent(self)
		self.slotImg.LoadImage(PATH_QT + "slot.png")
		self.slotImg.SetPosition(self.slotX, 2)
		self.slotImg.AddFlag("not_pick")
		self.slotImg.Show()

		self.icon = ui.ExpandedImageBox()
		self.icon.SetParent(self)
		self.icon.AddFlag("not_pick")
		self.icon.Hide()

		self.caption = ui.TextLine()
		self.caption.SetParent(self)
		self.caption.SetPosition(self.textCenterX, 5)
		self.caption.SetHorizontalAlignCenter()
		self.caption.SetPackedFontColor(QT_COLOR_CAPTION)
		self.caption.AddFlag("not_pick")
		self.caption.Hide()

		self.attrLines = []
		for i in xrange(5):
			line = ui.TextLine()
			line.SetParent(self)
			line.SetPosition(self.textCenterX, 18 + i * 16)
			line.SetHorizontalAlignCenter()
			line.SetPackedFontColor(QT_COLOR_ATTR)
			line.AddFlag("not_pick")
			line.Hide()
			self.attrLines.append(line)

		self.tint = ui.Bar()
		self.tint.SetParent(self)
		self.tint.SetPosition(0, 0)
		self.tint.SetSize(QT_ROW_WIDTH, QT_ROW_HEIGHT)
		self.tint.SetColor(QT_TINT_HOVER)
		self.tint.AddFlag("not_pick")
		self.tint.Hide()

	def Destroy(self):
		self.bg = None
		self.slotImg = None
		self.icon = None
		self.caption = None
		self.attrLines = []
		self.tint = None
		self.selectEvent = None
		self.wheelEvent = None
		self.overEvent = None
		self.outEvent = None

	def __del__(self):
		ui.Window.__del__(self)

	def __SetIcon(self, vnum):
		item.SelectItem(vnum)
		(w, h) = item.GetItemSize()
		if h < 1 or h > 3:
			h = 1
		self.icon.LoadImage(item.GetIconImageFileName())
		self.icon.SetPosition(self.slotX + 2, 2 + (QT_SLOT_H - 32 * h) // 2)
		self.icon.Show()

	def __LayoutLines(self, texts, colors, captionText):
		if captionText:
			self.caption.SetText(captionText)
			self.caption.Show()
			areaTop = 20
		else:
			self.caption.Hide()
			areaTop = 0

		offset = areaTop + (QT_ROW_HEIGHT - areaTop - len(texts) * 16) // 2
		for i in xrange(len(self.attrLines)):
			if i < len(texts):
				self.attrLines[i].SetText(texts[i])
				self.attrLines[i].SetPackedFontColor(colors[i])
				self.attrLines[i].SetPosition(self.textCenterX, offset + i * 16)
				self.attrLines[i].Show()
			else:
				self.attrLines[i].Hide()

	def SetItemData(self, slotPos, vnum, attrList, enchantList, captionText = None):
		self.slotPos = slotPos
		self.__SetIcon(vnum)

		texts = []
		colors = []
		for (affectType, affectValue) in attrList:
			text = _QTGetAffectString(affectType, affectValue)
			if text:
				texts.append(text)
				colors.append(QT_COLOR_ATTR)

		for (enchantType, enchantValue) in enchantList:
			text = _QTGetAffectString(enchantType, enchantValue)
			if text:
				texts.append(text)
				colors.append(QT_COLOR_ENCHANT)

		if len(texts) > len(self.attrLines):
			hidden = len(texts) - (len(self.attrLines) - 1)
			texts = texts[:len(self.attrLines) - 1]
			colors = colors[:len(self.attrLines) - 1]
			texts.append(getattr(localeinfo, "QUICKTRANSFER_MORE", "+ %d more bonuses") % hidden)
			colors.append(QT_COLOR_EMPTY)

		self.__LayoutLines(texts, colors, captionText)
		self.Show()

	def SetMessageData(self, slotPos, vnum, captionText, messageText):
		self.slotPos = slotPos
		self.__SetIcon(vnum)
		self.__LayoutLines([messageText], [QT_COLOR_MESSAGE], captionText)
		self.Show()

	def SetSelected(self, flag):
		self.selected = flag
		self.__UpdateTint()

	def __UpdateTint(self):
		if self.selected:
			self.tint.SetColor(QT_TINT_SELECTED)
			self.tint.Show()
		elif self.hovered:
			self.tint.SetColor(QT_TINT_HOVER)
			self.tint.Show()
		else:
			self.tint.Hide()

	def OnMouseOverIn(self):
		self.hovered = True
		self.__UpdateTint()
		if self.slotPos >= 0 and self.overEvent:
			self.overEvent(self.slotPos)

	def OnMouseOverOut(self):
		self.hovered = False
		self.__UpdateTint()
		if self.outEvent:
			self.outEvent()

	def OnMouseWheel(self, nLen):
		if self.wheelEvent:
			return self.wheelEvent(nLen)
		return False

	def OnMouseLeftButtonDown(self):
		if self.slotPos >= 0 and self.selectEvent:
			self.selectEvent(self.rowIndex)


class QuickTransferConfirmDialog(ui.BoardWithTitleBar):
	def __init__(self, tooltipItem, acceptEvent, cancelEvent):
		ui.BoardWithTitleBar.__init__(self)
		self.AddFlag("float")
		self.AddFlag("movable")
		self.SetSize(QT_CONFIRM_W, QT_CONFIRM_H)
		self.SetTitleName(getattr(localeinfo, "QUICKTRANSFER_CONFIRM_TITLE", "Confirm Bonus Transfer"))
		self.SetCloseEvent(ui.__mem_func__(self.OnCancelButton))
		self.tooltipItem = tooltipItem
		self.acceptEvent = acceptEvent
		self.cancelEvent = cancelEvent
		self.__CreateUI()
		self.Hide()

	def __CreateUI(self):
		self.destRow = QuickTransferRow(self, 0, None, None,
			ui.__mem_func__(self.OnRowOverIn),
			ui.__mem_func__(self.OnRowOverOut))
		self.destRow.SetPosition((QT_CONFIRM_W - QT_ROW_WIDTH) // 2, 40)
		self.destRow.Hide()

		self.srcRow = QuickTransferRow(self, 1, None, None,
			ui.__mem_func__(self.OnRowOverIn),
			ui.__mem_func__(self.OnRowOverOut))
		self.srcRow.SetPosition((QT_CONFIRM_W - QT_ROW_WIDTH) // 2, 160)
		self.srcRow.Hide()

		self.yangImg = ui.ExpandedImageBox()
		self.yangImg.SetParent(self)
		self.yangImg.LoadImage(PATH_QT + "yang.png")
		self.yangImg.SetPosition(QT_CONFIRM_W // 2 - 62, 283)
		self.yangImg.AddFlag("not_pick")
		self.yangImg.Show()

		self.costText = ui.TextLine()
		self.costText.SetParent(self)
		self.costText.SetPosition(QT_CONFIRM_W // 2 + 12, 282)
		self.costText.SetHorizontalAlignCenter()
		self.costText.SetPackedFontColor(QT_COLOR_PRICE)
		self.costText.AddFlag("not_pick")
		self.costText.Show()

		self.acceptButton = ui.Button()
		self.acceptButton.SetParent(self)
		self.acceptButton.SetPosition(QT_CONFIRM_W // 2 - 65, 306)
		self.acceptButton.SetUpVisual(PATH_QT + "button_accept_norm.png")
		self.acceptButton.SetOverVisual(PATH_QT + "button_accept_hover.png")
		self.acceptButton.SetDownVisual(PATH_QT + "button_accept_down.png")
		self.acceptButton.SetEvent(ui.__mem_func__(self.OnAcceptButton))
		self.acceptButton.Show()

		self.cancelButton = ui.Button()
		self.cancelButton.SetParent(self)
		self.cancelButton.SetPosition(QT_CONFIRM_W // 2 + 8, 306)
		self.cancelButton.SetUpVisual(PATH_QT + "button_cancel_norm.png")
		self.cancelButton.SetOverVisual(PATH_QT + "button_cancel_hover.png")
		self.cancelButton.SetDownVisual(PATH_QT + "button_cancel_down.png")
		self.cancelButton.SetEvent(ui.__mem_func__(self.OnCancelButton))
		self.cancelButton.Show()

	def Destroy(self):
		if self.destRow:
			self.destRow.Destroy()
		if self.srcRow:
			self.srcRow.Destroy()
		self.destRow = None
		self.srcRow = None
		self.yangImg = None
		self.costText = None
		self.acceptButton = None
		self.cancelButton = None
		self.tooltipItem = None
		self.acceptEvent = None
		self.cancelEvent = None

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def Open(self, destSlotPos, destVnum, attrList, enchantList, srcSlotPos, srcVnum):
		self.destRow.SetItemData(destSlotPos, destVnum, attrList, enchantList,
			getattr(localeinfo, "QUICKTRANSFER_RECEIVES", "Receives:"))
		self.destRow.SetSelected(False)

		self.srcRow.SetMessageData(srcSlotPos, srcVnum,
			getattr(localeinfo, "QUICKTRANSFER_LOSES", "Loses:"),
			getattr(localeinfo, "QUICKTRANSFER_LOSES_ALL", "All bonuses will be removed from this item."))
		self.srcRow.SetSelected(False)

		self.costText.SetText(_QTMoneyString(_QTGetCost()))

		self.SetPosition((wndMgr.GetScreenWidth() - QT_CONFIRM_W) // 2, (wndMgr.GetScreenHeight() - QT_CONFIRM_H) // 2)
		self.SetTop()
		self.Show()

	def Close(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()
		self.Hide()

	def OnRowOverIn(self, slotPos):
		if self.tooltipItem:
			self.tooltipItem.SetInventoryItem(slotPos)

	def OnRowOverOut(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OnAcceptButton(self):
		if self.acceptEvent:
			self.acceptEvent()

	def OnCancelButton(self):
		if self.cancelEvent:
			self.cancelEvent()
		else:
			self.Close()

	def OnPressEscapeKey(self):
		self.OnCancelButton()
		return True


class QuickTransferWindow(ui.BoardWithTitleBar):
	def __init__(self, tooltipItem = None, interface = None):
		ui.BoardWithTitleBar.__init__(self)
		self.AddFlag("float")
		self.AddFlag("movable")
		self.SetSize(QT_BOARD_W, QT_BOARD_H)
		self.SetTitleName(getattr(localeinfo, "QUICKTRANSFER_TITLE", "Quick Bonus Transfer"))
		self.SetCloseEvent(ui.__mem_func__(self.OnCancel))
		self.tooltipItem = tooltipItem
		self.interface = interface
		self.__Initialize()
		self.__CreateUI()
		self.Hide()

	def __Initialize(self):
		self.pendingSlotPos = -1
		self.destSlotPos = -1
		self.destVnum = 0
		self.destSubType = -1
		self.candidates = []
		self.scrollOffset = 0
		self.contentHeight = QT_VIEW_H
		self.selectedIdx = -1

	def __CreateUI(self):
		self.bg = ui.ExpandedImageBox()
		self.bg.SetParent(self)
		self.bg.LoadImage(PATH_QT + "bg_transfer.png")
		self.bg.SetPosition(QT_BG_X, QT_BG_Y)
		self.bg.AddFlag("not_pick")
		self.bg.Show()

		self.titleText = ui.TextLine()
		self.titleText.SetParent(self)
		self.titleText.SetPosition(QT_BG_X + QT_WIDTH // 2, QT_BG_Y + 11)
		self.titleText.SetHorizontalAlignCenter()
		self.titleText.SetPackedFontColor(QT_COLOR_TITLE)
		self.titleText.SetText(getattr(localeinfo, "QUICKTRANSFER_TITLE", "Quick Bonus Transfer"))
		self.titleText.AddFlag("not_pick")
		self.titleText.Show()

		self.destIcon = ui.ExpandedImageBox()
		self.destIcon.SetParent(self)
		self.destIcon.AddFlag("not_pick")
		self.destIcon.Hide()

		self.destHover = ui.Window()
		self.destHover.SetParent(self)
		self.destHover.SetPosition(QT_BG_X + (QT_WIDTH - QT_SLOT_W) // 2, QT_BG_Y + 42)
		self.destHover.SetSize(QT_SLOT_W, QT_SLOT_H)
		self.destHover.OnMouseOverIn = ui.__mem_func__(self.OnDestOverIn)
		self.destHover.OnMouseOverOut = ui.__mem_func__(self.OnTooltipOut)
		self.destHover.Show()

		self.yangImg = ui.ExpandedImageBox()
		self.yangImg.SetParent(self)
		self.yangImg.LoadImage(PATH_QT + "yang.png")
		self.yangImg.SetPosition(QT_BG_X + 66, QT_BG_Y + 171)
		self.yangImg.AddFlag("not_pick")
		self.yangImg.Show()

		self.priceText = ui.TextLine()
		self.priceText.SetParent(self)
		self.priceText.SetPosition(QT_BG_X + QT_WIDTH // 2 + 8, QT_BG_Y + 172)
		self.priceText.SetHorizontalAlignCenter()
		self.priceText.SetPackedFontColor(QT_COLOR_PRICE)
		self.priceText.AddFlag("not_pick")
		self.priceText.Show()

		self.listViewport = ui.Window()
		self.listViewport.SetParent(self)
		self.listViewport.SetPosition(QT_ROW_X, QT_VIEW_Y)
		self.listViewport.SetSize(QT_ROW_WIDTH, QT_VIEW_H)
		self.listViewport.OnMouseWheel = ui.__mem_func__(self.OnMouseWheel)
		self.listViewport.Show()

		self.listContent = ui.Window()
		self.listContent.SetParent(self.listViewport)
		self.listContent.SetPosition(0, 0)
		self.listContent.SetSize(QT_ROW_WIDTH, QT_VIEW_H)
		self.listContent.OnMouseWheel = ui.__mem_func__(self.OnMouseWheel)
		if getattr(app, "USE_CLIP_MASK", 0):
			self.listContent.SetClippingMaskWindow(self.listViewport)
		self.listContent.Show()

		self.rows = []

		self.emptyText = ui.TextLine()
		self.emptyText.SetParent(self)
		self.emptyText.SetPosition(QT_BG_X + QT_WIDTH // 2, QT_VIEW_Y + QT_VIEW_H // 2)
		self.emptyText.SetHorizontalAlignCenter()
		self.emptyText.SetPackedFontColor(QT_COLOR_EMPTY)
		self.emptyText.SetText(getattr(localeinfo, "QUICKTRANSFER_EMPTY", "No enchanted costume of this type was found."))
		self.emptyText.AddFlag("not_pick")
		self.emptyText.Hide()

		self.acceptButton = ui.Button()
		self.acceptButton.SetParent(self)
		self.acceptButton.SetPosition(QT_BG_X + 84, QT_BG_Y + 445)
		self.acceptButton.SetUpVisual(PATH_QT + "button_accept_norm.png")
		self.acceptButton.SetOverVisual(PATH_QT + "button_accept_hover.png")
		self.acceptButton.SetDownVisual(PATH_QT + "button_accept_down.png")
		self.acceptButton.SetEvent(ui.__mem_func__(self.OnAccept))
		self.acceptButton.Show()

		self.cancelButton = ui.Button()
		self.cancelButton.SetParent(self)
		self.cancelButton.SetPosition(QT_BG_X + 158, QT_BG_Y + 445)
		self.cancelButton.SetUpVisual(PATH_QT + "button_cancel_norm.png")
		self.cancelButton.SetOverVisual(PATH_QT + "button_cancel_hover.png")
		self.cancelButton.SetDownVisual(PATH_QT + "button_cancel_down.png")
		self.cancelButton.SetEvent(ui.__mem_func__(self.OnCancel))
		self.cancelButton.Show()

		self.confirmDialog = QuickTransferConfirmDialog(self.tooltipItem,
			ui.__mem_func__(self.OnConfirmAccept),
			ui.__mem_func__(self.OnConfirmCancel))

	def Destroy(self):
		self.__DestroyRows()
		if self.confirmDialog:
			self.confirmDialog.Destroy()
		self.confirmDialog = None
		self.bg = None
		self.titleText = None
		self.destIcon = None
		self.destHover = None
		self.yangImg = None
		self.priceText = None
		self.listViewport = None
		self.listContent = None
		self.emptyText = None
		self.acceptButton = None
		self.cancelButton = None
		self.tooltipItem = None
		self.interface = None
		self.__Initialize()

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def __DestroyRows(self):
		for row in self.rows:
			row.Hide()
			row.Destroy()
		self.rows = []

	def __GetAllowedSubTypes(self):
		allowed = [item.COSTUME_TYPE_BODY, item.COSTUME_TYPE_HAIR]
		for name in ("COSTUME_TYPE_WEAPON", "COSTUME_TYPE_MOUNT_SKIN", "COSTUME_TYPE_PET_SKIN"):
			value = getattr(item, name, -1)
			if value >= 0:
				allowed.append(value)
		return allowed

	def RequestOpen(self, destSlotPos):
		if not getattr(app, "USE_QUICK_ATTR_TRANSFER", 0):
			return

		if self.IsShow():
			return

		vnum = player.GetItemIndex(destSlotPos)
		if 0 == vnum:
			return

		item.SelectItem(vnum)
		if item.ITEM_TYPE_COSTUME != item.GetItemType() or\
			item.GetItemSubType() not in self.__GetAllowedSubTypes():
			chat.AppendChat(chat.CHAT_TYPE_INFO, getattr(localeinfo, "QUICKTRANSFER_ONLY_COSTUME", "Bonuses can only be transferred between costumes of the same type."))
			return

		self.pendingSlotPos = destSlotPos
		net.SendChatPacket("/quicktransfer open")

	def OpenConfirmed(self):
		if self.pendingSlotPos < 0:
			return

		destSlotPos = self.pendingSlotPos
		self.pendingSlotPos = -1

		vnum = player.GetItemIndex(destSlotPos)
		if 0 == vnum:
			net.SendChatPacket("/quicktransfer close")
			return

		item.SelectItem(vnum)
		self.destSlotPos = destSlotPos
		self.destVnum = vnum
		self.destSubType = item.GetItemSubType()

		(w, h) = item.GetItemSize()
		if h < 1 or h > 3:
			h = 1
		self.destIcon.LoadImage(item.GetIconImageFileName())
		self.destIcon.SetPosition(QT_BG_X + (QT_WIDTH - 32) // 2, QT_BG_Y + 42 + (QT_SLOT_H - 32 * h) // 2)
		self.destIcon.Show()

		self.priceText.SetText(_QTMoneyString(_QTGetCost()))

		self.__BuildCandidates()
		self.selectedIdx = -1
		self.__BuildRows()
		self.__RefreshList()
		self.__HighlightInventory()

		self.SetPosition((wndMgr.GetScreenWidth() - QT_BOARD_W) // 2, (wndMgr.GetScreenHeight() - QT_BOARD_H) // 2)
		self.SetTop()
		self.Show()

	def Close(self, sendClose = True):
		if self.confirmDialog:
			self.confirmDialog.Close()
		if self.interface and hasattr(self.interface, "ClearQuickTransferHighlightSlots"):
			self.interface.ClearQuickTransferHighlightSlots()
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()
		self.pendingSlotPos = -1
		wasShown = self.IsShow()
		self.Hide()
		if sendClose and wasShown:
			net.SendChatPacket("/quicktransfer close")

	def __GetActiveEnchants(self, cell):
		enchantList = []
		if not getattr(app, "USE_ENCHANT_COSTUMES", 0):
			return enchantList

		now = app.GetGlobalTimeStamp()
		for i in xrange(player.ENCHANT_SLOT_MAX_NUM):
			(enchantType, enchantValue, enchantTime) = player.GetItemEnchant(player.INVENTORY, cell, i)
			if 0 == enchantType or 0 == enchantValue or 0 == enchantTime:
				continue
			if enchantTime <= now:
				continue
			enchantList.append((enchantType, enchantValue))
		return enchantList

	def __BuildCandidates(self):
		self.candidates = []

		canBeEnch = getattr(item, "ITEM_CAN_BE_ENCHANTED", 0)
		destEnch = 0
		if canBeEnch:
			destEnch = player.GetItemFlags(self.destSlotPos) & canBeEnch

		cellMax = getattr(player, "INVENTORY_PAGE_SIZE", 45) * getattr(player, "INVENTORY_PAGE_COUNT", 2)
		for cell in xrange(cellMax):
			if cell == self.destSlotPos:
				continue

			vnum = player.GetItemIndex(cell)
			if 0 == vnum:
				continue

			item.SelectItem(vnum)
			if item.ITEM_TYPE_COSTUME != item.GetItemType():
				continue
			if item.GetItemSubType() != self.destSubType:
				continue

			if canBeEnch:
				if (player.GetItemFlags(cell) & canBeEnch) != destEnch:
					continue

			enchantList = self.__GetActiveEnchants(cell)
			if not enchantList:
				continue

			attrList = []
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				(attrType, attrValue) = player.GetItemAttribute(player.INVENTORY, cell, i)
				if 0 != attrType and 0 != attrValue:
					attrList.append((attrType, attrValue))

			self.candidates.append((cell, vnum, attrList, enchantList))

	def __BuildRows(self):
		self.__DestroyRows()

		count = len(self.candidates)
		self.contentHeight = max(QT_VIEW_H, count * QT_ROW_STEP - 2)
		self.listContent.SetSize(QT_ROW_WIDTH, self.contentHeight)
		self.scrollOffset = 0
		self.listContent.SetPosition(0, 0)

		for i in xrange(count):
			(cell, vnum, attrList, enchantList) = self.candidates[i]
			row = QuickTransferRow(self.listContent, i,
				ui.__mem_func__(self.OnSelectRow),
				ui.__mem_func__(self.OnMouseWheel),
				ui.__mem_func__(self.OnRowOverIn),
				ui.__mem_func__(self.OnTooltipOut))
			row.SetPosition(0, i * QT_ROW_STEP)
			row.SetItemData(cell, vnum, attrList, enchantList)
			self.rows.append(row)

	def __HighlightInventory(self):
		if self.interface and hasattr(self.interface, "SetQuickTransferHighlight"):
			redSlot = -1
			if 0 <= self.selectedIdx < len(self.candidates):
				redSlot = self.candidates[self.selectedIdx][0]
			self.interface.SetQuickTransferHighlight(self.destSlotPos, redSlot)

	def __RefreshList(self):
		for i in xrange(len(self.rows)):
			self.rows[i].SetSelected(i == self.selectedIdx)

		if self.candidates:
			self.emptyText.Hide()
		else:
			self.emptyText.Show()

	def __IsConfirmOpen(self):
		return self.confirmDialog and self.confirmDialog.IsShow()

	def OnSelectRow(self, rowIndex):
		if self.__IsConfirmOpen():
			return

		if rowIndex < len(self.candidates):
			self.selectedIdx = rowIndex
			self.__RefreshList()
			self.__HighlightInventory()

	def OnRowOverIn(self, slotPos):
		if self.tooltipItem:
			self.tooltipItem.SetInventoryItem(slotPos)

	def OnDestOverIn(self):
		if self.tooltipItem and self.destSlotPos >= 0:
			self.tooltipItem.SetInventoryItem(self.destSlotPos)

	def OnTooltipOut(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OnMouseWheel(self, nLen):
		if self.__IsConfirmOpen():
			return False

		maxOffset = self.contentHeight - QT_VIEW_H
		if maxOffset <= 0:
			return False

		if nLen > 0:
			self.scrollOffset = max(0, self.scrollOffset - QT_SCROLL_STEP)
		else:
			self.scrollOffset = min(maxOffset, self.scrollOffset + QT_SCROLL_STEP)

		self.listContent.SetPosition(0, -self.scrollOffset)
		return True

	def OnAccept(self):
		if self.__IsConfirmOpen():
			return

		if self.selectedIdx < 0 or self.selectedIdx >= len(self.candidates):
			chat.AppendChat(chat.CHAT_TYPE_INFO, getattr(localeinfo, "QUICKTRANSFER_SELECT_FIRST", "Select a source item first."))
			return

		cost = _QTGetCost()
		if player.GetElk() < cost:
			chat.AppendChat(chat.CHAT_TYPE_INFO, getattr(localeinfo, "QUICKTRANSFER_NEED_YANG", "You need %s Yang.") % _QTMoneyString(cost))
			return

		(srcCell, srcVnum, attrList, enchantList) = self.candidates[self.selectedIdx]
		self.confirmDialog.Open(self.destSlotPos, self.destVnum, attrList, enchantList, srcCell, srcVnum)

	def OnConfirmAccept(self):
		if self.selectedIdx < 0 or self.selectedIdx >= len(self.candidates):
			return
		if not hasattr(net, "SendQuickAttrTransferPacket"):
			chat.AppendChat(chat.CHAT_TYPE_INFO, getattr(localeinfo, "QUICKTRANSFER_UNAVAILABLE", "This feature is not available in this client build."))
			return
		(srcCell, srcVnum, attrList, enchantList) = self.candidates[self.selectedIdx]
		net.SendQuickAttrTransferPacket(self.destSlotPos, srcCell)

	def OnConfirmCancel(self):
		if self.confirmDialog:
			self.confirmDialog.Close()

	def OnCancel(self):
		if self.__IsConfirmOpen():
			self.OnConfirmCancel()
			return

		self.Close()

	def OnPressEscapeKey(self):
		self.OnCancel()
		return True
