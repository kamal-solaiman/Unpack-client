# coding: utf-8

import app
import net
import item
import chat
import player

import ui
import localeinfo
import mousemodule

class TransferWindow(ui.ScriptWindow):
	def __Close(self):
		if self.isUsable:
			self.isUsable = False

			net.SendChatPacket("/attrtransfer close")

		self.Close()

	def Clear(self):
		for i in xrange(4):
			if i > 0:
				self.combSlot.ClearSlot(i)
				net.SendChatPacket("/attrtransfer del %d" % (i))

		self.def_combSlot_1 = 999
		self.def_combSlot_2 = 999

	def __OnSelectEmptySlot(self, selectedSlotPos):
		isAttached = mousemodule.mouseController.isAttached()
		if not isAttached:
			return

		attachedSlotType = mousemodule.mouseController.GetAttachedType()
		if attachedSlotType != player.SLOT_TYPE_INVENTORY:
			return

		attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
		mousemodule.mouseController.DeattachObject()

		if player.IsEquipmentSlot(attachedSlotPos) or player.IsCostumeSlot(attachedSlotPos) or (app.ENABLE_NEW_EQUIPMENT_SYSTEM and player.IsBeltInventorySlot(attachedSlotPos)):
			return

		targetVnum = player.GetItemIndex(attachedSlotPos)
		if targetVnum == 0:
			return

		if selectedSlotPos == 0:
			item.SelectItem(targetVnum)
			if item.GetItemType() != item.ITEM_TYPE_TRANSFER_SCROLL:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_ALERT7)
				return

			if self.def_mediumSlot != 999:
				self.mediumSlot.ClearSlot(0)
				self.def_mediumSlot = 999

			self.mediumSlot.SetItemSlot(0, player.GetItemIndex(attachedSlotPos), player.GetItemCount(attachedSlotPos))
			net.SendChatPacket("/attrtransfer add %d %d" % (0, attachedSlotPos))
			self.def_mediumSlot = selectedSlotPos

			for slotPos, invenPos in self.itemInfo.items():
				if invenPos == attachedSlotPos:
					del self.itemInfo[slotPos]

			self.itemInfo[selectedSlotPos] = attachedSlotPos
			return

		if self.def_mediumSlot == 999:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_ALERT1)
			return

		if self.def_combSlot_1 == 999 and selectedSlotPos == 2:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_ALERT2)
			return

		item.SelectItem(targetVnum)
		itemType = item.GetItemType()
		itemSubType = item.GetItemSubType()
		if itemType != item.ITEM_TYPE_COSTUME:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_ALERT3)
			return

		if not itemSubType in (item.COSTUME_TYPE_BODY, item.COSTUME_TYPE_HAIR, item.COSTUME_TYPE_WEAPON):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_ALERT8)
			return

		haveAttr = False
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			if player.GetItemAttribute(attachedSlotPos, i)[0] != 0:
				haveAttr = True
				break

		if haveAttr == False:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_ALERT11)
			return

		if selectedSlotPos == 2:
			itemSlot1Vnum = player.GetItemIndex(self.def_combSlot_1)
			if not itemSlot1Vnum:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_ALERT9)
				return

			item.SelectItem(itemSlot1Vnum)
			if item.GetItemSubType() != itemSubType:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_ALERT6)
				return

			if (player.GetItemFlags(self.def_combSlot_1) & item.ITEM_CAN_BE_ENCHANTED) != (player.GetItemFlags(attachedSlotPos) & item.ITEM_CAN_BE_ENCHANTED):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_ALERT10)
				return

		self.combSlot.SetItemSlot(selectedSlotPos, player.GetItemIndex(attachedSlotPos), player.GetItemCount(attachedSlotPos))

		net.SendChatPacket("/attrtransfer add %d %d" % (selectedSlotPos, attachedSlotPos))

		if selectedSlotPos == 1:
			self.def_combSlot_1 = attachedSlotPos
		elif selectedSlotPos == 2:
			self.def_combSlot_2 = attachedSlotPos

		for slotPos, invenPos in self.itemInfo.items():
			if invenPos == attachedSlotPos:
				del self.itemInfo[slotPos]

		self.itemInfo[selectedSlotPos] = attachedSlotPos

		if selectedSlotPos == 2:
			self.combSlot.SetItemSlot(3, player.GetItemIndex(self.def_combSlot_1), 1)

	def __OnSelectItemSlot(self, selectedSlotPos):
		if selectedSlotPos == 3:
			return

		self.Clear()

		if selectedSlotPos == 0:
			if self.def_mediumSlot != 999:
				self.mediumSlot.ClearSlot(0)
				self.def_mediumSlot = 999

	def __OnOverInItem(self, slotIndex):
		if not self.toolTipItem:
			return

		if slotIndex == 3:
			if self.itemInfo.has_key(1) and self.itemInfo.has_key(2):
				self.toolTipItem.SetInventoryItemAttrTransfer(self.itemInfo[1], self.itemInfo[2])
		else:
			if self.itemInfo.has_key(slotIndex):
				self.toolTipItem.SetInventoryItem(self.itemInfo[slotIndex])

	def __OnOverOutItem(self):
		if self.toolTipItem:
			self.toolTipItem.HideToolTip()

	def OnPressEscapeKey(self):
		self.__Close()
		return True

	def OnUpdate(self):
		USE_SHOP_LIMIT_RANGE = 1000
		(x, y, z) = player.GetMainCharacterPosition()
		if abs(x - self.xShopStart) > USE_SHOP_LIMIT_RANGE or abs(y - self.yShopStart) > USE_SHOP_LIMIT_RANGE:
			self.__Close()

	def Open(self):
		self.Refresh()
		self.Show()

		self.isUsable = True
		(self.xShopStart, self.yShopStart, z) = player.GetMainCharacterPosition()
		for i in xrange(4):
			self.combSlot.ClearSlot(i)

		self.mediumSlot.ClearSlot(0)

		self.def_mediumSlot = 999
		self.def_combSlot_1 = 999
		self.def_combSlot_2 = 999

		self.itemInfo = {}

		self.SetCenterPosition()

	def Close(self):
		if self.toolTipItem and self.toolTipItem.IsShow():
			if self.IsIn(True):
				self.toolTipItem.HideToolTip()

		self.Hide()

	def Refresh(self):
		pass

	def Success(self):
		self.mediumSlot.ClearSlot(0)
		self.def_mediumSlot = 999

		self.Clear()

	def __Accept(self):
		net.SendChatPacket("/attrtransfer make")

	def __Load(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/attrtransferwindow.py")

			self.titleBar = self.GetChild("titlebar_ui")

			self.btnAccept = self.GetChild("acceptbutton_ui")
			self.btnCancel = self.GetChild("closebutton_ui")

			self.mediumSlot = self.GetChild("mediumslot_ui")
			self.combSlot = self.GetChild("combslot_ui")
		except:
			import exception
			exception.Abort("TransferWindow.LoadDialog.LoadScript")

		try:
			self.titleBar.SetCloseEvent(ui.__mem_func__(self.__Close))

			self.btnCancel.SetEvent(ui.__mem_func__(self.__Close))
			self.btnAccept.SetEvent(ui.__mem_func__(self.__Accept))

			self.mediumSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.__OnSelectEmptySlot))
			self.mediumSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnSelectItemSlot))
			self.mediumSlot.SetOverInItemEvent(ui.__mem_func__(self.__OnOverInItem))
			self.mediumSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OnOverOutItem))

			self.combSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.__OnSelectEmptySlot))
			self.combSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnSelectItemSlot))
			self.combSlot.SetOverInItemEvent(ui.__mem_func__(self.__OnOverInItem))
			self.combSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OnOverOutItem))
		except:
			import exception
			exception.Abort("TransferWindow.LoadDialog.BindObject")

		self.SLOT_SIZEX = 32
		self.SLOT_SIZEY = 32

		self.itemInfo = {}

	def __init__(self, itemToolTip):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.isUsable = False

		self.xShopStart = 0
		self.yShopStart = 0

		self.def_mediumSlot = 999
		self.def_combSlot_1 = 999
		self.def_combSlot_2 = 999

		if itemToolTip:
			from _weakref import proxy
			self.toolTipItem = proxy(itemToolTip)

		self.__Load()

	def Destroy(self):
		if self.titleBar:
			self.titleBar.SetCloseEvent(None)
			self.titleBar = None

		if self.mediumSlot:
			self.mediumSlot.SetSelectEmptySlotEvent(None)
			self.mediumSlot.SetSelectItemSlotEvent(None)
			self.mediumSlot.SetOverInItemEvent(None)
			self.mediumSlot.SetOverOutItemEvent(None)
			self.mediumSlot = None

		if self.combSlot:
			self.combSlot.SetSelectEmptySlotEvent(None)
			self.combSlot.SetSelectItemSlotEvent(None)
			self.combSlot.SetOverInItemEvent(None)
			self.combSlot.SetOverOutItemEvent(None)
			self.combSlot = None

		if self.btnAccept:
			self.btnAccept.SetEvent(None)
			self.btnAccept = None

		if self.btnCancel:
			self.btnCancel.SetEvent(None)
			self.btnCancel = None

		self.def_mediumSlot = 999
		self.def_combSlot_1 = 999
		self.def_combSlot_2 = 999

		if self.toolTipItem:
			self.toolTipItem = None

		self.ClearDictionary()

	def __del__(self):
		ui.ScriptWindow.__del__(self)
