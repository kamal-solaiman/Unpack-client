# coding: latin_1

import ui
import app
import net
import item
import player
import chat
import snd
import localeinfo
import constinfo

if app.USE_OFFLINESHOP:
	import uiofflineshop_ae

# Must match QUICK_SELL_MAX_BATCH in srcs/share/m2_length.hpp - the server drops a larger batch.
MAX_BATCH = 90
MAX_CART = MAX_BATCH * 2

SELECTED_COVER_IMAGE = "icon/item/selected_icon.png"

PANEL_WIDTH = 180
LABEL_WIDTH = PANEL_WIDTH - 24
LABEL_HEIGHT = 17

MONEY_ICON_WIDTH = 16
MONEY_ICON_GAP = 4


def IsSelected(windowType, slotIndex):
	return (windowType, slotIndex) in constinfo.QUICK_SELL_ITEMS


def GetSelectedCount():
	return len(constinfo.QUICK_SELL_ITEMS)


def ClearSelection():
	constinfo.QUICK_SELL_ITEMS.clear()


def LocaleText(key, default):
	# LocaleInfoWrapper.__getattr__ answers a missing key with the string
	# "Locale not found: KEY" rather than raising, so getattr's own default never fires.
	value = getattr(localeinfo, key, default)
	if not value or value.startswith("Locale not found"):
		return default

	return value


def PlaceMoneyIcon(icon, label):
	# The coin has to be a sibling of the label - it is placed in the label's coordinate
	# space. Under the arabic codepage a TextLine anchors on its rect's RIGHT edge and the
	# glyphs grow leftwards from there (CTextLine::OnChangePosition), so the coin, which is
	# a plain ltr image, has to swap to the other end of the text.
	x, y = label.GetLocalPosition()
	textWidth = label.GetTextWidth()

	if localeinfo.IsARABIC():
		x += label.GetWidth() - textWidth - MONEY_ICON_GAP - MONEY_ICON_WIDTH
	else:
		x += textWidth + MONEY_ICON_GAP

	icon.SetPosition(x, y + 1)
	icon.Show()


def GetSellPrice(itemVnum, itemCount):
	# mirrors CShopManager::SellBatch: truncate per item, and never divide by a zero price
	item.SelectItem(itemVnum)
	itemPrice = item.GetISellItemPrice()

	if item.Is1GoldItem():
		if itemPrice <= 0:
			itemPrice = itemCount
		else:
			itemPrice = itemCount / itemPrice
	else:
		itemPrice = itemPrice * itemCount

	return itemPrice / 5


def CanSell(windowType, slotIndex):
	itemVnum = player.GetItemIndex(windowType, slotIndex)
	if not itemVnum:
		return False

	if player.INVENTORY == windowType:
		if player.IsEquipmentSlot(slotIndex):
			return False
	elif player.DRAGON_SOUL_INVENTORY != windowType:
		return False

	if app.ENABLE_ACCOUNT_BIND_ITEMS and player.IsItemAccountBound(windowType, slotIndex):
		return False

	if app.USE_OFFLINESHOP:
		if uiofflineshop_ae.IsBuildingShop() and uiofflineshop_ae.IsSaleSlot(windowType, slotIndex):
			return False

	item.SelectItem(itemVnum)

	if item.IsAntiFlag(item.ITEM_ANTIFLAG_SELL):
		return False

	if item.GetItemType() in (item.ITEM_TYPE_BLEND, item.ITEM_TYPE_PET):
		return False

	return True


# >>> QUICK_SELL auto-select BEGIN - the "Select junk" button was dropped on request; every item
# now enters the cart by hand and is reviewed on the confirm page. Kept verbatim in case the
# auto-sweep is wanted back. docs/QUICK_SELL_SYSTEM.md
# def HasUpgrades(windowType, slotIndex):
#	for i in xrange(player.METIN_SOCKET_MAX_NUM):
#		if player.GetItemMetinSocket(windowType, slotIndex, i):
#			return True
#
#	for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
#		if player.GetItemAttribute(windowType, slotIndex, i)[0]:
#			return True
#
#	return False
#
#
# def IsJunk(windowType, slotIndex):
#	# dragon souls are a currency, never swept automatically - TAB still selects them by hand
#	if player.DRAGON_SOUL_INVENTORY == windowType:
#		return False
#
#	if not CanSell(windowType, slotIndex):
#		return False
#
#	if HasUpgrades(windowType, slotIndex):
#		return False
#
#	itemVnum = player.GetItemIndex(windowType, slotIndex)
#	item.SelectItem(itemVnum)
#
#	# refinable gear occupies a +0..+9 vnum block, so only the block head is unenchanted;
#	# an item outside such a block simply never auto-selects, which is the safe direction
#	if item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
#		if itemVnum % 10:
#			return False
#
#	return True
# <<< QUICK_SELL auto-select END


class QuickSellConfirm(ui.ScriptWindow):
	CELL = 32
	GAP = 4
	PITCH = CELL + GAP

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.tooltipItem = None
		self.acceptEvent = None
		self.removeEvent = None
		self.pendingRemove = None
		self.board = None
		self.viewport = None
		self.scrollBarSlot = None
		self.hintLabel = None
		self.countLabel = None
		self.totalLabel = None
		self.moneyIcon = None
		self.acceptButton = None
		self.cancelButton = None
		self.scrollBoard = None
		self.itemGrid = None
		self.scrollBar = None
		self.entries = []
		self.overflow = 0
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadWindow(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "UIScript/QuickSellConfirm.py")

		self.board = self.GetChild("board")
		self.board.SetTitleName(LocaleText("QUICK_SELL_CONFIRM_TITLE", "Confirm Sale"))
		self.board.SetCloseEvent(ui.__mem_func__(self.Close))

		self.viewport = self.GetChild("Viewport")
		self.scrollBarSlot = self.GetChild("ScrollBarSlot")

		self.hintLabel = self.__SetupLabel("HintLabel")
		self.hintLabel.SetText(LocaleText("QUICK_SELL_CONFIRM_HINT", "Click an item to remove it."))

		self.countLabel = self.__SetupLabel("CountLabel")
		self.totalLabel = self.__SetupLabel("TotalLabel")

		# parked at the label's x until the first Open measures the text
		self.moneyIcon = self.GetChild("MoneyIcon")
		self.moneyIcon.Hide()

		self.acceptButton = self.GetChild("AcceptButton")
		self.acceptButton.SetToolTipText(LocaleText("UI_ACCEPT", "Accept"))
		self.acceptButton.SetEvent(ui.__mem_func__(self.__OnAccept))

		self.cancelButton = self.GetChild("CancelButton")
		self.cancelButton.SetToolTipText(LocaleText("UI_CANCEL", "Cancel"))
		self.cancelButton.SetEvent(ui.__mem_func__(self.Close))

	def __SetupLabel(self, childName):
		label = self.GetChild(childName)
		label.SetSize(self.GetWidth() - 32, LABEL_HEIGHT)
		return label

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def Open(self, entries, total, acceptEvent, removeEvent):
		self.acceptEvent = acceptEvent
		self.removeEvent = removeEvent

		self.Refresh(entries, total)

		self.SetCenterPosition()
		self.SetTop()
		self.Show()
		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	# taking an item out rebuilds the page in place: no re-centring, no SetTop, and
	# __BuildGrid carries the scroll offset over so the list does not jump to the top
	def Refresh(self, entries, total):
		self.entries = entries

		self.__BuildGrid()

		self.countLabel.SetText("%s %d" % (
			LocaleText("QUICK_SELL_SELECTED_ITEMS", "Items selected:"), len(entries)))
		self.totalLabel.SetText("%s %s" % (
			LocaleText("QUICK_SELL_TOTAL", "Total:"), localeinfo.NumberToMoneyString(total)))
		PlaceMoneyIcon(self.moneyIcon, self.totalLabel)

	def Close(self):
		self.__HideToolTip()
		self.__ReleaseGrid()
		self.entries = []
		self.acceptEvent = None
		self.removeEvent = None
		self.pendingRemove = None
		self.Hide()
		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnPressExitKey(self):
		self.Close()
		return True

	def Destroy(self):
		self.__ReleaseGrid()
		self.entries = []
		self.acceptEvent = None
		self.removeEvent = None
		self.pendingRemove = None
		self.tooltipItem = None
		self.board = None
		self.viewport = None
		self.scrollBarSlot = None
		self.hintLabel = None
		self.countLabel = None
		self.totalLabel = None
		self.moneyIcon = None
		self.acceptButton = None
		self.cancelButton = None
		ui.ScriptWindow.Destroy(self)

	def __ReleaseGrid(self):
		# dropping the last python ref is this framework's teardown path for code-made widgets
		self.itemGrid = None
		self.scrollBoard = None
		self.scrollBar = None
		self.overflow = 0

	def __PackEntries(self, cols):
		# An icon is drawn at the item's real proto height - 32 px per slot - so a 2- or
		# 3-slot item has to own that many cells or it covers the row beneath it, and its
		# count badge (anchored to byyPlacedItemSize) lands on the wrong icon. Tall items go
		# down first and the 1-slot ones drop into the gaps they leave.
		heights = []
		for entry in self.entries:
			item.SelectItem(entry[3])
			heights.append(max(1, item.GetItemSize()[1]))

		places = [None] * len(self.entries)
		rows = []
		rowCount = 0

		for i in sorted(range(len(heights)), key=lambda index: -heights[index]):
			height = heights[i]
			row = 0
			col = -1

			while col < 0:
				while len(rows) < row + height:
					rows.append([False] * cols)

				for c in xrange(cols):
					if all(not rows[row + k][c] for k in xrange(height)):
						col = c
						break

				if col < 0:
					row += 1

			for k in xrange(height):
				rows[row + k][col] = True

			places[i] = (col, row, height)
			rowCount = max(rowCount, row + height)

		return places, rowCount

	def __BuildGrid(self):
		scrollPos = self.scrollBar.GetPos() if self.scrollBar else 0.0
		self.__ReleaseGrid()

		cols = max(1, (self.viewport.GetWidth() + self.GAP) / self.PITCH)
		places, rowCount = self.__PackEntries(cols)

		contentHeight = max(self.CELL, rowCount * self.PITCH - self.GAP)
		viewHeight = self.viewport.GetHeight()

		# The masked board is what scrolls; the viewport is the mask. Slot icons AND their count
		# NumberLines are clip-mask aware in this fork (PythonSlotWindow.cpp), so rows outside the
		# viewport are not drawn. Slot base/cover images are NOT clipped - never set them here.
		scrollBoard = ui.Window()
		scrollBoard.SetParent(self.viewport)
		scrollBoard.AddFlag("attach")
		if app.USE_CLIP_MASK:
			scrollBoard.SetClippingMaskWindow(self.viewport)
		scrollBoard.SetPosition(0, 0)
		scrollBoard.SetSize(self.viewport.GetWidth(), contentHeight)
		scrollBoard.Show()
		self.scrollBoard = scrollBoard

		# no "attach" flag here: RunMouseLeftButtonDown re-routes a click on an attached
		# window to its ROOT, which would silently kill the click-to-remove while leaving
		# hover working. The clip mask is inherited through AddChild and does not need it.
		itemGrid = ui.SlotWindow()
		itemGrid.SetParent(scrollBoard)
		itemGrid.SetPosition(0, 0)
		itemGrid.SetSize(cols * self.PITCH - self.GAP, contentHeight)
		itemGrid.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnRemoveItem))
		itemGrid.SetOverInItemEvent(ui.__mem_func__(self.__OnOverInItem))
		itemGrid.SetOverOutItemEvent(ui.__mem_func__(self.__OnOverOutItem))
		itemGrid.Show()
		self.itemGrid = itemGrid

		# SetItemSlot must run with the grid already parented under the mask: the count
		# NumberLine takes its mask from the slot window's CURRENT pointers, so filling
		# slots before parenting bakes in maskless counts that float outside the viewport.
		for i, entry in enumerate(self.entries):
			col, row, height = places[i]
			itemGrid.AppendSlot(i, col * self.PITCH, row * self.PITCH,
				self.CELL, self.CELL * height)
			itemCount = entry[2]
			itemGrid.SetItemSlot(i, entry[3], itemCount if itemCount > 1 else 0)

		itemGrid.RefreshSlot()

		self.overflow = max(0, contentHeight - viewHeight)

		scrollBar = ui.ScrollBarNew()
		scrollBar.SetParent(self.scrollBarSlot)
		# ScrollBarNew's own wheel handler has no position gate and children are reached first,
		# so it would swallow the wheel globally; this window's gated handler is the only path.
		scrollBar.allow_on_run_mouse_wheel = False
		scrollBar.SetScrollBarSize(viewHeight)
		scrollBar.SetPosition(0, 0)
		self.scrollBar = scrollBar

		if self.overflow > 0:
			scrollBar.SetMiddleBarSize(float(viewHeight) / float(contentHeight))
			scrollBar.SetScrollStep(float(self.PITCH) / float(self.overflow))
			scrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
			scrollBar.SetPos(min(1.0, scrollPos))
			scrollBar.Show()
		else:
			scrollBar.Hide()

	def __OnScroll(self):
		if not self.scrollBoard or not self.scrollBar:
			return

		if self.overflow <= 0:
			self.scrollBoard.SetPosition(0, 0)
			return

		self.scrollBoard.SetPosition(0, -int(self.overflow * self.scrollBar.GetPos()))

	def OnRunMouseWheel(self, nLen):
		if not self.scrollBar or self.overflow <= 0:
			return False

		if not self.IsInPosition():
			return False

		if nLen > 0:
			self.scrollBar.OnUp()
		elif nLen < 0:
			self.scrollBar.OnDown()

		return True

	def __OnRemoveItem(self, slotIndex):
		# picking is NOT mask-aware, so a row scrolled out of the viewport still reports clicks
		if not self.viewport or not self.viewport.IsInPosition():
			return

		if slotIndex >= len(self.entries):
			return

		# the whole grid is rebuilt for the new layout, and the slot window dispatching this
		# click is part of it - hand the work to the next OnUpdate instead
		self.pendingRemove = self.entries[slotIndex]
		self.__HideToolTip()

	def OnUpdate(self):
		if self.pendingRemove is None:
			return

		entry = self.pendingRemove
		self.pendingRemove = None

		if self.removeEvent:
			self.removeEvent(entry[0], entry[1])

	def __OnOverInItem(self, slotIndex):
		# picking is NOT mask-aware, so a row scrolled out of the viewport still reports hovers
		if not self.viewport or not self.viewport.IsInPosition():
			return

		if not self.tooltipItem or slotIndex >= len(self.entries):
			return

		entry = self.entries[slotIndex]
		self.tooltipItem.SetInventoryItem(entry[1], entry[0])

	def __OnOverOutItem(self):
		self.__HideToolTip()

	def __HideToolTip(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def __OnAccept(self):
		acceptEvent = self.acceptEvent
		self.Close()

		if acceptEvent:
			acceptEvent()


class QuickSell(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.interface = None
		self.tooltipItem = None
		self.board = None
		self.countLabel = None
		self.totalLabel = None
		self.moneyIcon = None
		self.sellButton = None
		self.confirmWindow = None
		self.totalPrice = 0
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadWindow(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "UIScript/QuickSellWindow.py")

		self.board = self.GetChild("board")
		self.board.SetTitleName(LocaleText("QUICK_SELL_TITLE_NAME", "Quick Sell"))
		self.board.SetCloseEvent(ui.__mem_func__(self.Close))

		self.countLabel = self.__SetupLabel("CountLabel")
		self.totalLabel = self.__SetupLabel("TotalLabel")
		self.moneyIcon = self.GetChild("MoneyIcon")

		self.sellButton = self.GetChild("SellButton")
		self.sellButton.SetText(LocaleText("QUICK_SELL", "Quick Sell"))
		self.sellButton.SetEvent(ui.__mem_func__(self.__OnClickSell))

		self.__RefreshLabels(0, 0)

	def __SetupLabel(self, childName):
		# an unsized TextLine collapses both anchors onto x and draws out of the panel on ae
		label = self.GetChild(childName)
		label.SetSize(LABEL_WIDTH, LABEL_HEIGHT)
		return label

	def BindInterface(self, interface):
		self.interface = interface

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem
		if self.confirmWindow:
			self.confirmWindow.SetItemToolTip(tooltipItem)

	def Open(self):
		self.SetTop()
		self.Show()

	def Close(self):
		self.__CloseConfirm()
		ClearSelection()
		self.Hide()
		self.__RefreshLabels(0, 0)
		self.__RefreshBags()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnPressExitKey(self):
		self.Close()
		return True

	def Destroy(self):
		if self.confirmWindow:
			self.confirmWindow.Close()
			self.confirmWindow.Destroy()
			self.confirmWindow = None
		ClearSelection()
		self.interface = None
		self.tooltipItem = None
		self.board = None
		self.countLabel = None
		self.totalLabel = None
		self.moneyIcon = None
		self.sellButton = None
		self.totalPrice = 0
		ui.ScriptWindow.Destroy(self)

	def Toggle(self, windowType, slotIndex):
		key = (windowType, slotIndex)

		if key in constinfo.QUICK_SELL_ITEMS:
			del constinfo.QUICK_SELL_ITEMS[key]
		else:
			if not CanSell(windowType, slotIndex):
				return False

			if len(constinfo.QUICK_SELL_ITEMS) >= MAX_CART:
				chat.AppendChat(chat.CHAT_TYPE_INFO,
					LocaleText("QUICK_SELL_CART_FULL", "You can only quick-sell %s items at once.") % MAX_CART)
				return True

			constinfo.QUICK_SELL_ITEMS[key] = (
				player.GetItemIndex(windowType, slotIndex),
				player.GetItemCount(windowType, slotIndex),
			)

		self.Refresh()
		return True

	def Refresh(self):
		count, total = self.__Recount()
		self.__RefreshLabels(count, total)

		if count:
			if not self.IsShow():
				self.Open()
		elif self.IsShow():
			self.__CloseConfirm()
			self.Hide()

	def __Recount(self):
		count = 0
		total = 0

		# items() copies in py2, so dropping stale keys mid-walk is safe
		for key, data in constinfo.QUICK_SELL_ITEMS.items():
			windowType, slotIndex = key
			itemVnum = data[0]

			if player.GetItemIndex(windowType, slotIndex) != itemVnum:
				del constinfo.QUICK_SELL_ITEMS[key]
				continue

			itemCount = player.GetItemCount(windowType, slotIndex)
			if not itemCount:
				del constinfo.QUICK_SELL_ITEMS[key]
				continue

			constinfo.QUICK_SELL_ITEMS[key] = (itemVnum, itemCount)

			count += 1
			total += GetSellPrice(itemVnum, itemCount)

		self.totalPrice = total
		return count, total

	def __RefreshLabels(self, count, total):
		if self.countLabel:
			self.countLabel.SetText("%s %d" % (
				LocaleText("QUICK_SELL_SELECTED_ITEMS", "Items selected:"), count))

		if self.totalLabel:
			self.totalLabel.SetText("%s %s" % (
				LocaleText("QUICK_SELL_TOTAL", "Total:"), localeinfo.NumberToMoneyString(total)))
			PlaceMoneyIcon(self.moneyIcon, self.totalLabel)

	def __RefreshBags(self):
		if self.interface:
			self.interface.RefreshQuickSellMarks()

	def __BuildEntries(self):
		entries = []

		for key, data in constinfo.QUICK_SELL_ITEMS.items():
			windowType, slotIndex = key
			itemVnum = data[0]

			if player.GetItemIndex(windowType, slotIndex) != itemVnum:
				continue

			itemCount = player.GetItemCount(windowType, slotIndex)
			if not itemCount:
				continue

			entries.append((windowType, slotIndex, itemCount, itemVnum))

		return entries

	def __OnClickSell(self):
		if self.confirmWindow and self.confirmWindow.IsShow():
			return

		count, total = self.__Recount()
		self.__RefreshLabels(count, total)

		if not count:
			self.Close()
			return

		if not self.confirmWindow:
			self.confirmWindow = QuickSellConfirm()
			self.confirmWindow.SetItemToolTip(self.tooltipItem)

		self.confirmWindow.Open(self.__BuildEntries(), total,
			ui.__mem_func__(self.__OnAnswerSell), ui.__mem_func__(self.__OnRemoveEntry))

	def __OnRemoveEntry(self, windowType, slotIndex):
		key = (windowType, slotIndex)

		if key in constinfo.QUICK_SELL_ITEMS:
			del constinfo.QUICK_SELL_ITEMS[key]

		count, total = self.__Recount()
		self.__RefreshLabels(count, total)
		self.__RefreshBags()

		if not count:
			self.Close()
			return

		self.confirmWindow.Refresh(self.__BuildEntries(), total)

	def __CloseConfirm(self):
		if self.confirmWindow and self.confirmWindow.IsShow():
			self.confirmWindow.Close()

	def __OnAnswerSell(self):
		entries = self.__BuildEntries()

		if not entries:
			self.Close()
			return

		for start in xrange(0, len(entries), MAX_BATCH):
			net.SendQuickSellPacket(entries[start:start + MAX_BATCH])

		snd.PlaySound("sound/ui/money.wav")
		self.Close()

	def OnSellResult(self, sold, rejected, gold):
		if sold:
			chat.AppendChat(chat.CHAT_TYPE_INFO,
				LocaleText("QUICK_SELL_RESULT", "Sold %s items for %s.")
				% (sold, localeinfo.NumberToMoneyString(gold)))

		if rejected:
			chat.AppendChat(chat.CHAT_TYPE_INFO,
				LocaleText("QUICK_SELL_RESULT_REJECTED", "%s items could not be sold.") % rejected)
