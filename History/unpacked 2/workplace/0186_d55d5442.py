# coding: latin_1

import app
import net
import player
import ui
import mousemodule
import snd
import item
import chat
import grp
import uiscriptlocale
import uirefine
import uiattachmetin
import uicommon
import uiprivateshopbuilder
import localeinfo
import constinfo
import ime
import wndMgr
import uitooltip


class ChangeLookWindow(ui.ScriptWindow):
	CHANGELOOK_SLOT_LEFT = 0
	CHANGELOOK_SLOT_RIGHT = 1
	CHANGELOOK_SLOT_MAX = 2

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.isloded = 0
		self.toolTipItem = None
		self.xChangeLookWindowStart = 0
		self.yChangeLookWindowStart = 0
		self.ChangeLookToolTipButton = None
		self.ChangeLookToolTip = None
		self.pop = None
		
		self.ChangeLookCost = None
		self.ChangeLookToolTipList = [
			localeinfo.CHANGE_TOOLTIP_LINE1,
			localeinfo.CHANGE_TOOLTIP_LINE2,
			localeinfo.CHANGE_TOOLTIP_LINE3,
			localeinfo.CHANGE_TOOLTIP_LINE4,
			localeinfo.CHANGE_TOOLTIP_LINE5,
			localeinfo.CHANGE_TOOLTIP_LINE6
		]
		self.ChangeLookMountToolTipList = [
			localeinfo.CHANGE_TOOLTIP2_LINE1, 
			localeinfo.CHANGE_TOOLTIP2_LINE2,
			localeinfo.CHANGE_TOOLTIP2_LINE3,
			localeinfo.CHANGE_TOOLTIP2_LINE4,
			localeinfo.CHANGE_TOOLTIP2_LINE5
		]

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		self.isloded = 0
		self.toolTipItem = None
		self.pop = None
		self.ChangeLookToolTipButton = None
		self.ChangeLookToolTip = None
		self.ChangeLookCost = None
		
	def __LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/ChangeLookWindow.py")
		except:
			import exception
			exception.Abort("ChangeLookWindow.__LoadWindow.UIScript/ChangeLookWindow.py")

		try:
			wndItem = self.GetChild("ChangeLookSlot")
			wndPassItem = self.GetChild("ChangeLookSlot_PassYangItem")

			self.GetChild("CancelButton").SetEvent(ui.__mem_func__(self.Close))
			self.GetChild("AcceptButton").SetEvent(ui.__mem_func__(self.Accept))
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))

			self.TitleName = self.GetChild("TitleName")
			self.ChangeLookCost = self.GetChild("Cost")
		except:
			import exception
			exception.Abort("ChangeLookWindow.__LoadWindow.ChangeLookSlot")

		wndItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		wndItem.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndItem.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndItem.Show()
		self.wndItem = wndItem
		
		wndPassItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItemFreeYang))
		wndPassItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		wndPassItem.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlotFreepass))
		wndPassItem.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlotFreepass))
		wndPassItem.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlotFreepass))
		wndPassItem.Show()
		self.wndPassItem = wndPassItem

		self.ChangeLookToolTipButton = self.GetChild("ChangeLookToolTIpButton")

	def __CreateGameTypeToolTip(self, title, descList):
		toolTip = uitooltip.ToolTip()
		toolTip.SetTitle(title)
		toolTip.AppendSpace(7)

		for desc in descList:
			toolTip.AutoAppendTextLine(desc)

		toolTip.AlignHorizonalCenter()
		toolTip.SetTop()
		return toolTip

	def OnUpdate(self):
		(x, y, z) = player.GetMainCharacterPosition()
		if abs(x - self.xChangeLookWindowStart) > player.SHOW_UI_WINDOW_LIMIT_RANGE or abs(y - self.yChangeLookWindowStart) > player.SHOW_UI_WINDOW_LIMIT_RANGE:
			self.Close()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Open(self, type):
		if self.isloded == 0:
			self.isloded = 1
			self.__LoadWindow()
		
		self.SetCenterPosition()
		self.SetTop()
		ui.ScriptWindow.Show(self)

		(self.xChangeLookWindowStart, self.yChangeLookWindowStart, z) = player.GetMainCharacterPosition()
		player.SetChangeLookWindow(True)
		player.SetChangeLookWindowType(int(type))

		self.SetChangeLookType(type)
		self.RefreshChangeLookWindow()

	def SetChangeLookType(self, type):
		self.RefreshGameTypeToolTip(type)
		self.ChangeLookCost.SetText(localeinfo.CHANGE_LOOK_COST % (localeinfo.NumberToMoneyString(player.GetChangeChangeLookPrice())))

	def RefreshGameTypeToolTip(self, type):
		if int(type) == player.CHANGE_LOOK_TYPE_MOUNT:
			self.TitleName.SetText(localeinfo.CHANGE_LOOK_TITLE2)
			self.ChangeLookToolTip = self.__CreateGameTypeToolTip(localeinfo.CHANGE_TOOLTIP_TITLE, self.ChangeLookMountToolTipList)
		else:
			self.TitleName.SetText(localeinfo.CHANGE_LOOK_TITLE)
			self.ChangeLookToolTip = self.__CreateGameTypeToolTip(localeinfo.CHANGE_TOOLTIP_TITLE, self.ChangeLookToolTipList)

		self.ChangeLookToolTip.SetTop()
		self.ChangeLookToolTipButton.SetToolTipWindow(self.ChangeLookToolTip)

	def Close(self):
		self.Hide()
		net.SendChangeLookCanCle()
		player.SetChangeLookWindow(False)

	def Accept(self):
		leftVnum = player.GetChangeLookItemID(self.CHANGELOOK_SLOT_LEFT)
		rightVnum = player.GetChangeLookItemID(self.CHANGELOOK_SLOT_RIGHT)
		if leftVnum == 0 or rightVnum == 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_INSERT_ITEM)
		else:
			popup = uicommon.QuestionDialog()
			popup.SetText(localeinfo.CHANGE_LOOK_CHANGE_ITEM)
			popup.SetAcceptEvent(self.SendAccept)
			popup.SetCancelEvent(self.OnCloseEvent)
			popup.Open()
			self.pop = popup

	def SendAccept(self):
		self.pop.Close()
		self.pop = None
		net.SendChangeLookAccept()

	def SetItemToolTip(self, tooltip):
		self.toolTipItem = tooltip

	def __ShowToolTip(self, slotIndex):
		if self.toolTipItem:
			self.toolTipItem.SetChangeLookWindowItem(slotIndex)

	def OverInItem(self, slotIndex):
		self.wndItem.SetUsableItem(False)
		self.__ShowToolTip(slotIndex)

	def OverOutItem(self):
		self.wndItem.SetUsableItem(False)
		if self.toolTipItem:
			self.toolTipItem.HideToolTip()

	def OverInItemFreeYang(self, slotIndex):
		self.wndItem.SetUsableItem(False)
		self.__ShowToolTip_FreeItem(player.GetChangeLookFreeYangInvenSlotPos())	

	def __ShowToolTip_FreeItem(self, slotIndex):
		if self.toolTipItem:
			self.toolTipItem.SetInventoryItem(slotIndex, player.INVENTORY)

	def OverInItemFreeYang(self, slotIndex):
		self.wndItem.SetUsableItem(False)
		self.__ShowToolTip_FreeItem(player.GetChangeLookFreeYangInvenSlotPos())	

	def __ShowToolTip_FreeItem(self, slotIndex):
		if self.toolTipItem:
			self.toolTipItem.SetInventoryItem(slotIndex, player.INVENTORY)

	def UseItemSlotFreepass(self, slotIndex):
		mousemodule.mouseController.DeattachObject()
		net.SendChangeLookCheckOutFreeYangItem()
		
		if app.USE_ACCE_SYSTEM:
			leftVnum = player.GetChangeLookItemID(self.CHANGELOOK_SLOT_LEFT)
			if leftVnum:
				item.SelectItem(leftVnum)
				
				if item.GetItemType() == item.ITEM_TYPE_COSTUME and\
					item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
					self.ChangeLookCost.SetText(localeinfo.CHANGE_LOOK_COST % (localeinfo.NumberToMoneyString(0)))
					return
		
		self.ChangeLookCost.SetText(localeinfo.CHANGE_LOOK_COST % (localeinfo.NumberToMoneyString(player.GetChangeChangeLookPrice())))

	def SelectEmptySlotFreepass(self, selectedSlotPos):
		if mousemodule.mouseController.isAttached():
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)
			itemVnum = player.GetItemIndex(attachedSlotPos)
			
			if item.IsChangeLookFreePassYangItem(itemVnum) == 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_DO_NOT_REGISTER_ITEM)
				return
			
			if app.USE_ACCE_SYSTEM:
				leftVnum = player.GetChangeLookItemID(self.CHANGELOOK_SLOT_LEFT)
				if leftVnum == 0:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_ADD_SOURCE)
					return
				
				if player.GetChangeLookItemID(self.CHANGELOOK_SLOT_RIGHT) == 0:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_ADD_TARGET)
					return
				
				leftVnum = player.GetChangeLookItemID(self.CHANGELOOK_SLOT_LEFT)
				if leftVnum:
					item.SelectItem(leftVnum)
					
					if item.GetItemType() == item.ITEM_TYPE_COSTUME and\
						item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
						
						if itemVnum != item.CHANGE_LOOK_TICKET_ACCE:
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_DO_NOT_REGISTER_ITEM)
							return
					else:
						if itemVnum == item.CHANGE_LOOK_TICKET_ACCE:
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_DO_NOT_REGISTER_ITEM)
							return
			
			net.SendChangeLookCheckInFreeYangItem(attachedInvenType, attachedSlotPos)
			mousemodule.mouseController.DeattachObject()
			self.ChangeLookCost.SetText(localeinfo.CHANGE_LOOK_COST % (localeinfo.NumberToMoneyString(0)))

	def SelectEmptySlot(self, selectedSlotPos):
		if mousemodule.mouseController.isAttached():

			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			ItemVNum = player.GetItemIndex(attachedSlotPos)

			if attachedSlotPos > player.EQUIPMENT_SLOT_START - 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_DO_NOT_EQUIP_ITEM)
				return

			if selectedSlotPos == self.CHANGELOOK_SLOT_LEFT:
				if item.IsPossibleChangeLookLeft(ItemVNum) == 0:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_DO_NOT_CHANGE_LOOK_ITEM)
					return
			else:
				if player.GetChangeLookItemID(self.CHANGELOOK_SLOT_LEFT) == 0:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_INSERT_CHANGE_LOOK_ITEM)
					return
				if item.IsPossibleChangeLookRight(player.GetChangeLookItemID(self.CHANGELOOK_SLOT_LEFT), ItemVNum) == 0:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_DO_NOT_REGISTER_ITEM)
					return

			if player.SLOT_TYPE_CHANGE_LOOK != attachedSlotType:
				attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)
				if player.RESERVED_WINDOW == attachedInvenType:
					return

				if selectedSlotPos == self.CHANGELOOK_SLOT_LEFT:
					net.SendChangeLookCheckIn(attachedInvenType, attachedSlotPos, selectedSlotPos)
				else:
					if app.ENABLE_SOUL_BIND_SYSTEM:
						if player.GetItemSealDate(player.INVENTORY, attachedSlotPos) == -1 or player.GetItemSealDate(player.INVENTORY, attachedSlotPos) > 0:
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_DO_NOT_SEAL_ITEM)
							return

					if player.GetChangeLookItemInvenSlot(self.CHANGELOOK_SLOT_LEFT) == attachedSlotPos:
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_ALREADY_REGISTER)
						return

					net.SendChangeLookCheckIn(attachedInvenType, attachedSlotPos, selectedSlotPos)
					popup = uicommon.PopupDialog()
					popup.SetText(localeinfo.CHANGE_LOOK_DEL_ITEM)
					popup.SetAcceptEvent(self.__OnClosePopupDialog)
					popup.Open()
					self.pop = popup

			
			mousemodule.mouseController.DeattachObject()

	def UseItemSlot(self, slotIndex):
		if slotIndex == self.CHANGELOOK_SLOT_LEFT:
			if player.GetChangeLookItemID(self.CHANGELOOK_SLOT_RIGHT) == 0:
				mousemodule.mouseController.DeattachObject()
				net.SendChangeLookCheckOut(slotIndex)
			else:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_CHECK_OUT_REGISTER_ITEM)
		else:
			mousemodule.mouseController.DeattachObject()
			net.SendChangeLookCheckOut(slotIndex)

	def SelectItemSlot(self, selectedSlotPos):
		if mousemodule.mouseController.isAttached():
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			if player.SLOT_TYPE_INVENTORY == attachedSlotType:
				attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
				snd.PlaySound("sound/ui/drop.wav")
			mousemodule.mouseController.DeattachObject()
		else:
			curCursorNum = app.GetCursor()
			if app.SELL == curCursorNum:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SAFEBOX_SELL_DISABLE_SAFEITEM)
			elif app.BUY == curCursorNum:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SHOP_BUY_INFO)
			else:
				if selectedSlotPos == self.CHANGELOOK_SLOT_LEFT:
					if player.GetChangeLookItemID(self.CHANGELOOK_SLOT_RIGHT) == 0:
						selectedItemID = player.GetChangeLookItemID(selectedSlotPos)
						mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_CHANGE_LOOK, selectedSlotPos, selectedItemID)
						snd.PlaySound("sound/ui/pick.wav")
					else:
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_CHECK_OUT_REGISTER_ITEM)
				else:
					selectedItemID = player.GetChangeLookItemID(selectedSlotPos)
					mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_CHANGE_LOOK, selectedSlotPos, selectedItemID)
					snd.PlaySound("sound/ui/pick.wav")

	def RefreshChangeLookWindow(self):
		if not self.wndItem:
			return

		if not player.GetChangeLookWindowOpen():
			return

		setChangeLookItem = self.wndItem.SetItemSlot
		getChangeLookItem = player.GetChangeLookItemID

		for i in xrange(self.CHANGELOOK_SLOT_MAX):
			ChangeLookSlotVnum = getChangeLookItem(i)
			if not ChangeLookSlotVnum == player.ITEM_SLOT_COUNT:
				setChangeLookItem(i, ChangeLookSlotVnum, 1)
			else:
				setChangeLookItem(i, 0, 1)

			changelookvnum = player.GetChangeWIndowChangeLookVnum(i)
			if not changelookvnum == 0:
				self.wndItem.SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")
			else:
				self.wndItem.EnableSlotCoverImage(i, False)

		self.wndItem.RefreshSlot()

		ChangeLookFreeItemVnum = player.GetChangeLookFreeYangItemID()
		if not ChangeLookFreeItemVnum == 0:
			self.wndPassItem.SetItemSlot(0, ChangeLookFreeItemVnum, 1)
		else:
			self.ChangeLookCost.SetText(localeinfo.CHANGE_LOOK_COST % (localeinfo.NumberToMoneyString(player.GetChangeChangeLookPrice())))
			self.wndPassItem.SetItemSlot(0, 0, 1)

	def OnCloseEvent(self):
		self.pop.Close()
		self.pop = None

	def __OnClosePopupDialog(self):
		self.popup = None
