# coding: latin_1

import app
import net
import player

import ui
import grp
import snd
import item
import chat
import acce
import uitooltip
import localeinfo
import uiinventory
import mousemodule
import uiscriptlocale

from _weakref import proxy

if app.WJ_ENABLE_TRADABLE_ICON:
	INVENTORY_PAGE_SIZE = player.INVENTORY_PAGE_SIZE
	if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
		SPECIAL_INVENTORY_PAGE_SIZE = player.SPECIAL_INVENTORY_PAGE_SIZE

class CombineWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.interface = None
			self.inven = None

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				self.invenSpecial = None

			self.ItemListIdx = []

		self.isLoaded = 0
		self.PositionOut = 0
		self.PositionStartX = 0
		self.PositionStartY = 0

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.interface = None
			self.inven = None

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				self.invenSpecial = None

			self.ItemListIdx = []

		self.ClearDictionary()
		self.titleBar = None
		self.btnAccept = None
		self.btnCancel = None
		self.acceSlot = None
		self.cost = None
		self.Result = None
		self.PositionOut = 0
		self.PositionStartX = 0
		self.PositionStartY = 0
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.ItemListIdx = []

	def LoadWindow(self):
		if self.isLoaded:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/acce_combinewindow.py")

		except:
			import exception
			exception.Abort("Acce_CombineWindow.LoadDialog.LoadScript")

		try:
			self.titleBar = self.GetChild("TitleBar")
			self.btnAccept = self.GetChild("AcceptButton")
			self.btnCancel = self.GetChild("CancelButton")
			self.cost = self.GetChild("Cost")
			self.Result = self.GetChild("Result")
			self.acceSlot = self.GetChild("AcceSlot")
		except:
			import exception
			exception.Abort("Acce_CombineWindow.LoadDialog.BindObject")

		self.acceSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.OnSelectEmptySlot))
		self.acceSlot.SetUnselectItemSlotEvent(ui.__mem_func__(self.OnSelectItemSlot))
		self.acceSlot.SetUseSlotEvent(ui.__mem_func__(self.OnSelectItemSlot))
		self.acceSlot.SetOverInItemEvent(ui.__mem_func__(self.OnOverInItem))
		self.acceSlot.SetOverOutItemEvent(ui.__mem_func__(self.OnOverOutItem))
		self.titleBar.SetCloseEvent(ui.__mem_func__(self.OnClose))
		self.btnCancel.SetEvent(ui.__mem_func__(self.OnClose))
		self.btnAccept.SetEvent(ui.__mem_func__(self.OnAccept))
		self.tooltipItem = None

	def SetItemToolTip(self, itemTooltip):
		self.tooltipItem = itemTooltip

	def IsOpened(self):
		if self.IsShow() and self.isLoaded:
			return True

		return False

	def Open(self):
		self.PositionOut = 0
		(self.PositionStartX, self.PositionStartY, z) = player.GetMainCharacterPosition()
		self.cost.SetText(localeinfo.ACCE_ABSORB_COST % (acce.GetPrice()))
		for i in xrange(acce.WINDOW_MAX_MATERIALS + 1):
			self.acceSlot.ClearSlot(i)

		player.SetAcceRefineWindowOpen(2)
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

		if app.WJ_ENABLE_TRADABLE_ICON:
			if self.interface:
				self.interface.SetOnTopWindow(player.ON_TOP_WND_ACCE_COMBINE)
				self.interface.RefreshMarkInventoryBag()

	def Close(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

		self.Hide()

	def OnClose(self):
		self.Close()
		player.SetAcceRefineWindowOpen(0)
		acce.SendCloseRequest()

		if app.WJ_ENABLE_TRADABLE_ICON:
			if self.interface:
				self.interface.SetOnTopWindow(player.ON_TOP_WND_NONE)
				self.interface.RefreshMarkInventoryBag()

			self.ItemListIdx = None

	def OnPressEscapeKey(self):
		self.OnClose()
		return True

	def OnAccept(self):
		acce.SendRefineRequest()

	if app.WJ_ENABLE_TRADABLE_ICON:
		def BindInterface(self, interface):
			if interface:
				self.interface = proxy(interface)

		def SetInven(self, inven):
			if inven:
				self.inven = proxy(inven)

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			def SetSpecialInven(self, invenSpecial):
				if invenSpecial:
					self.invenSpecial = proxy(invenSpecial)

		def CantTradableItem(self, slotIndex):
			itemIndex = player.GetItemIndex(slotIndex)

			if itemIndex:
				item.SelectItem(itemIndex)

				if app.ENABLE_SOUL_BIND_SYSTEM:
					if player.GetItemSealDate(player.INVENTORY, slotIndex) == -1 or player.GetItemSealDate(player.INVENTORY, slotIndex) > 0:
						return True

				if (item.GetItemType() != item.ITEM_TYPE_COSTUME or item.GetItemSubType() != item.COSTUME_TYPE_ACCE):
					return True

			return False

		def OnTop(self):
			self.tooltipItem.SetTop()
			if not self.interface:
				return

			self.interface.SetOnTopWindow(player.ON_TOP_WND_ACCE_COMBINE)
			self.interface.RefreshMarkInventoryBag()

		def AcceItemMouseEvent(self):
			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				if not self.inven or not self.invenSpecial:
					return
			else:
				if not self.inven:
					return

			if not self.ItemListIdx:
				return

			page = self.inven.GetInventoryPageIndex() # range 0 ~ 1
			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				special_page = self.invenSpecial.GetInventoryPageIndex()

			for i in self.ItemListIdx:
				if (page * INVENTORY_PAGE_SIZE) <= i < ((page + 1) * INVENTORY_PAGE_SIZE): # range 0 ~ 44, 45 ~ 89
					lock_idx = i - (page * INVENTORY_PAGE_SIZE)
					self.inven.wndItem.SetCantMouseEventSlot(lock_idx)

				if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
					if self.invenSpecial.GetInventoryType() == 0:
						if (item.SKILL_BOOK_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.SKILL_BOOK_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.SKILL_BOOK_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)

					if self.invenSpecial.GetInventoryType() == 1:
						if (item.UPGRADE_ITEMS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.UPGRADE_ITEMS_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.UPGRADE_ITEMS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)

					if self.invenSpecial.GetInventoryType() == 2:
						if (item.STONE_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.STONE_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.STONE_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)

					if self.invenSpecial.GetInventoryType() == 3:
						if (item.GIFT_BOX_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.GIFT_BOX_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.GIFT_BOX_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)


					if self.invenSpecial.GetInventoryType() == 4:
						if (item.ENCHANT_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.ENCHANT_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.ENCHANT_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)

					if self.invenSpecial.GetInventoryType() == 5:
						if (item.POTS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.POTS_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.POTS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)


	def OnUpdate(self):
		LIMIT_RANGE = acce.LIMIT_RANGE
		(x, y, z) = player.GetMainCharacterPosition()
		if abs(x - self.PositionStartX) >= LIMIT_RANGE or abs(y - self.PositionStartY) >= LIMIT_RANGE:
			if not self.PositionOut:
				self.PositionOut += 1
				
				self.OnClose()

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.AcceItemMouseEvent()

	def OnSelectEmptySlot(self, selectedSlotPos):
		isAttached = mousemodule.mouseController.isAttached()
		if not isAttached or selectedSlotPos == acce.WINDOW_MAX_MATERIALS:
			return

		attachedSlotType = mousemodule.mouseController.GetAttachedType()
		attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
		attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)

		if player.GetItemSealDate(player.INVENTORY, attachedSlotPos) == -1 or player.GetItemSealDate(player.INVENTORY, attachedSlotPos) > 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.ACCE_NOT_SEALITEM)
			return

		mousemodule.mouseController.DeattachObject()
		if attachedSlotType == player.SLOT_TYPE_INVENTORY and attachedInvenType == player.INVENTORY:
			acce.Add(attachedInvenType, attachedSlotPos, selectedSlotPos)

	def OnSelectItemSlot(self, selectedSlotPos):
		if selectedSlotPos == acce.WINDOW_MAX_MATERIALS:
			return

		mousemodule.mouseController.DeattachObject()
		acce.Remove(selectedSlotPos)

	def OnOverInItem(self, selectedSlotPos):
		if self.tooltipItem:
			if selectedSlotPos == acce.WINDOW_MAX_MATERIALS:
				(isHere, iCell) = acce.GetAttachedItem(0)
				if isHere:
					self.tooltipItem.SetAcceResultItem(iCell)
			else:
				(isHere, iCell) = acce.GetAttachedItem(selectedSlotPos)
				if isHere:
					self.tooltipItem.SetInventoryItem(iCell)

	def OnOverOutItem(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def Refresh(self, iAct):
		self.cost.SetText(localeinfo.ACCE_ABSORB_COST % (acce.GetPrice()))
		self.acceSlot.ClearSlot(acce.WINDOW_MAX_MATERIALS)

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.ItemListIdx = []

		anyMaterialBound = False

		for i in xrange(acce.WINDOW_MAX_MATERIALS):
			self.acceSlot.ClearSlot(i)

			(isHere, iCell) = acce.GetAttachedItem(i)
			if isHere:
				self.acceSlot.SetItemSlot(i, player.GetItemIndex(iCell), 0)

				if app.WJ_ENABLE_TRADABLE_ICON:
					self.ItemListIdx.append(iCell)

				# ENABLE_ACCOUNT_BIND_ITEMS — show lock overlay on bound materials
				# AND on the result preview since output inherits bind.
				if app.ENABLE_ACCOUNT_BIND_ITEMS:
					if player.IsItemAccountBound(player.INVENTORY, iCell):
						self.acceSlot.SetSlotCoverImage(i, "icon/item/account_locked.png")
						anyMaterialBound = True
					else:
						self.acceSlot.EnableSlotCoverImage(i, False)

				if i == int(acce.WINDOW_MAX_MATERIALS - 1):
					(itemVnum, MinAbs, MaxAbs) = acce.GetResultItem()
					if not itemVnum:
						break

					self.acceSlot.SetItemSlot(i + 1, itemVnum, 0)
					if app.ENABLE_ACCOUNT_BIND_ITEMS:
						if anyMaterialBound:
							self.acceSlot.SetSlotCoverImage(i + 1, "icon/item/account_locked.png")
						else:
							self.acceSlot.EnableSlotCoverImage(i + 1, False)
					break

class AbsorbWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.interface = None
			self.inven = None

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				self.invenSpecial = None

			self.ItemListIdx = []

		self.isLoaded = 0
		self.PositionOut = 0
		self.PositionStartX = 0
		self.PositionStartY = 0

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.interface = None
			self.inven = None

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				self.invenSpecial = None

			self.ItemListIdx = []

		self.ClearDictionary()
		self.titleBar = None
		self.btnAccept = None
		self.btnCancel = None
		self.acceSlot = None
		self.PositionOut = 0
		self.PositionStartX = 0
		self.PositionStartY = 0

	def LoadWindow(self):
		if self.isLoaded:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/acce_absorbwindow.py")
		except:
			import exception
			exception.Abort("Acce_AbsorbtionWindow.LoadDialog.LoadScript")

		try:
			self.titleBar = self.GetChild("TitleBar")
			self.btnAccept = self.GetChild("AcceptButton")
			self.btnCancel = self.GetChild("CancelButton")
			self.acceSlot = self.GetChild("AcceSlot")
		except:
			import exception
			exception.Abort("Acce_AbsorbtionWindow.LoadDialog.BindObject")

		self.acceSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.OnSelectEmptySlot))
		self.acceSlot.SetUnselectItemSlotEvent(ui.__mem_func__(self.OnSelectItemSlot))
		self.acceSlot.SetUseSlotEvent(ui.__mem_func__(self.OnSelectItemSlot))
		self.acceSlot.SetOverInItemEvent(ui.__mem_func__(self.OnOverInItem))
		self.acceSlot.SetOverOutItemEvent(ui.__mem_func__(self.OnOverOutItem))
		self.titleBar.SetCloseEvent(ui.__mem_func__(self.OnClose))
		self.btnCancel.SetEvent(ui.__mem_func__(self.OnClose))
		self.btnAccept.SetEvent(ui.__mem_func__(self.OnAccept))

		self.tooltipItem = None

	def SetItemToolTip(self, itemTooltip):
		self.tooltipItem = itemTooltip

	def IsOpened(self):
		if self.IsShow() and self.isLoaded:
			return True

		return False

	def Open(self):
		self.PositionOut = 0
		(self.PositionStartX, self.PositionStartY, z) = player.GetMainCharacterPosition()
		for i in xrange(acce.WINDOW_MAX_MATERIALS + 1):
			self.acceSlot.ClearSlot(i)

		player.SetAcceRefineWindowOpen(1)
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

		if app.WJ_ENABLE_TRADABLE_ICON:
			if self.interface:
				self.interface.SetOnTopWindow(player.ON_TOP_WND_ACCE_ABSORB)
				self.interface.RefreshMarkInventoryBag()

	def Close(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

		self.Hide()

	def OnClose(self):
		player.SetAcceRefineWindowOpen(0)
		acce.SendCloseRequest()

		if app.WJ_ENABLE_TRADABLE_ICON:
			if self.interface:
				self.interface.SetOnTopWindow(player.ON_TOP_WND_NONE)
				self.interface.RefreshMarkInventoryBag()

			self.ItemListIdx = None

	def OnPressEscapeKey(self):
		self.OnClose()
		return True

	def OnAccept(self):
		acce.SendRefineRequest()

	if app.WJ_ENABLE_TRADABLE_ICON:
		def BindInterface(self, interface):
			if interface:
				self.interface = proxy(interface)

		def SetInven(self, inven):
			if inven:
				self.inven = proxy(inven)

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			def SetSpecialInven(self, invenSpecial):
				if invenSpecial:
					self.invenSpecial = proxy(invenSpecial)

		def CantTradableItem(self, slotIndex):
			itemIndex = player.GetItemIndex(slotIndex)

			if itemIndex:
				item.SelectItem(itemIndex)

				if app.ENABLE_SOUL_BIND_SYSTEM:
					if player.GetItemSealDate(player.INVENTORY, slotIndex) == -1 or player.GetItemSealDate(player.INVENTORY, slotIndex) > 0:
						return True

				if ((item.GetItemType() != item.ITEM_TYPE_ARMOR or item.GetItemSubType() != item.ARMOR_BODY) and item.GetItemType() != item.ITEM_TYPE_WEAPON and (item.GetItemType() != item.ITEM_TYPE_COSTUME or item.GetItemSubType() != item.COSTUME_TYPE_ACCE)):
					return True

			return False

		def OnTop(self):
			self.tooltipItem.SetTop()
			if not self.interface:
				return

			self.interface.SetOnTopWindow(player.ON_TOP_WND_ACCE_ABSORB)
			self.interface.RefreshMarkInventoryBag()

		def AcceItemMouseEvent(self):
			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				if not self.inven or not self.invenSpecial:
					return
			else:
				if not self.inven:
					return

			if not self.ItemListIdx:
				return

			page = self.inven.GetInventoryPageIndex() # range 0 ~ 1
			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				special_page = self.invenSpecial.GetInventoryPageIndex()

			for i in self.ItemListIdx:
				if (page * INVENTORY_PAGE_SIZE) <= i < ((page + 1) * INVENTORY_PAGE_SIZE): # range 0 ~ 44, 45 ~ 89
					lock_idx = i - (page * INVENTORY_PAGE_SIZE)
					self.inven.wndItem.SetCantMouseEventSlot(lock_idx)

				if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
					if self.invenSpecial.GetInventoryType() == 0:
						if (item.SKILL_BOOK_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.SKILL_BOOK_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.SKILL_BOOK_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)

					if self.invenSpecial.GetInventoryType() == 1:
						if (item.UPGRADE_ITEMS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.UPGRADE_ITEMS_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.UPGRADE_ITEMS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)

					if self.invenSpecial.GetInventoryType() == 2:
						if (item.STONE_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.STONE_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.STONE_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)

					if self.invenSpecial.GetInventoryType() == 3:
						if (item.GIFT_BOX_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.GIFT_BOX_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.GIFT_BOX_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)

					if self.invenSpecial.GetInventoryType() == 4:
						if (item.ENCHANT_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.ENCHANT_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.ENCHANT_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)

					if self.invenSpecial.GetInventoryType() == 5:
						if (item.POTS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.POTS_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							lock_idx = i - (item.POTS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)


	def OnUpdate(self):
		LIMIT_RANGE = acce.LIMIT_RANGE
		(x, y, z) = player.GetMainCharacterPosition()
		if abs(x - self.PositionStartX) >= LIMIT_RANGE or abs(y - self.PositionStartY) >= LIMIT_RANGE:
			if not self.PositionOut:
				self.PositionOut += 1
				
				self.OnClose()

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.AcceItemMouseEvent()

	def OnSelectEmptySlot(self, selectedSlotPos):
		isAttached = mousemodule.mouseController.isAttached()
		if not isAttached or selectedSlotPos == acce.WINDOW_MAX_MATERIALS:
			return

		attachedSlotType = mousemodule.mouseController.GetAttachedType()
		attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
		attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)

		if player.GetItemSealDate(player.INVENTORY, attachedSlotPos) == -1 or player.GetItemSealDate(player.INVENTORY, attachedSlotPos) > 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.ACCE_NOT_SEALITEM)
			return

		mousemodule.mouseController.DeattachObject()
		if attachedSlotType == player.SLOT_TYPE_INVENTORY and attachedInvenType == player.INVENTORY:
			acce.Add(attachedInvenType, attachedSlotPos, selectedSlotPos)

	def OnSelectItemSlot(self, selectedSlotPos):
		if selectedSlotPos == acce.WINDOW_MAX_MATERIALS:
			return

		mousemodule.mouseController.DeattachObject()
		acce.Remove(selectedSlotPos)

	def OnOverInItem(self, selectedSlotPos):
		if self.tooltipItem:
			if selectedSlotPos == acce.WINDOW_MAX_MATERIALS:
				(isHere1, iCell1) = acce.GetAttachedItem(0)
				(isHere2, iCell2) = acce.GetAttachedItem(1)
				if isHere1 and isHere2:
					self.tooltipItem.SetAcceResultAbsItem(iCell1, iCell2)
			else:
				(isHere, iCell) = acce.GetAttachedItem(selectedSlotPos)
				if isHere:
					self.tooltipItem.SetInventoryItem(iCell)

	def OnOverOutItem(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def Refresh(self, iAct):
		self.acceSlot.ClearSlot(acce.WINDOW_MAX_MATERIALS)

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.ItemListIdx = []

		anyMaterialBound = False

		for i in xrange(acce.WINDOW_MAX_MATERIALS):
			self.acceSlot.ClearSlot(i)

			(isHere, iCell) = acce.GetAttachedItem(i)
			if isHere:
				self.acceSlot.SetItemSlot(i, player.GetItemIndex(iCell), 0)

				if app.WJ_ENABLE_TRADABLE_ICON:
					self.ItemListIdx.append(iCell)

				# ENABLE_ACCOUNT_BIND_ITEMS — lock overlay on bound materials
				# and on the result preview (output inherits bind).
				if app.ENABLE_ACCOUNT_BIND_ITEMS:
					if player.IsItemAccountBound(player.INVENTORY, iCell):
						self.acceSlot.SetSlotCoverImage(i, "icon/item/account_locked.png")
						anyMaterialBound = True
					else:
						self.acceSlot.EnableSlotCoverImage(i, False)

				if i == int(acce.WINDOW_MAX_MATERIALS - 1):
					(itemVnum, MinAbs, MaxAbs) = acce.GetResultItem()
					if not itemVnum:
						break

					self.acceSlot.SetItemSlot(i + 1, itemVnum, 0)
					if app.ENABLE_ACCOUNT_BIND_ITEMS:
						if anyMaterialBound:
							self.acceSlot.SetSlotCoverImage(i + 1, "icon/item/account_locked.png")
						else:
							self.acceSlot.EnableSlotCoverImage(i + 1, False)
					break
