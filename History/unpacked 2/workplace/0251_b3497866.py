# coding: latin_1

import app
import net
import player

import exchange
import time
import localeinfo
import chat
import item
import playersettingmodule
import uicommon
import ui
import grp
import mousemodule
import wndMgr
if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget
if app.USE_OFFLINESHOP:
	import uiofflineshop_ae

import systemSetting

from time import strftime
import datetime

if app.USE_LOG_EXCHANGE:
	# from time import strftime
	# import datetime
	import math

from _weakref import proxy

###################################################################################################
## Exchange
if app.WJ_ENABLE_TRADABLE_ICON:
	INVENTORY_PAGE_SIZE = player.INVENTORY_PAGE_SIZE
	if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
		SPECIAL_INVENTORY_PAGE_SIZE = player.SPECIAL_INVENTORY_PAGE_SIZE

class ExchangeDialog(ui.ScriptWindow):
	FACE_IMAGE_DICT = {
						playersettingmodule.RACE_WARRIOR_M : "icon/face/warrior_m.tga",
						playersettingmodule.RACE_WARRIOR_W : "icon/face/warrior_w.tga",
						playersettingmodule.RACE_ASSASSIN_M : "icon/face/assassin_m.tga",
						playersettingmodule.RACE_ASSASSIN_W : "icon/face/assassin_w.tga",
						playersettingmodule.RACE_SURA_M : "icon/face/sura_m.tga",
						playersettingmodule.RACE_SURA_W : "icon/face/sura_w.tga",
						playersettingmodule.RACE_SHAMAN_M : "icon/face/shaman_m.tga",
						playersettingmodule.RACE_SHAMAN_W : "icon/face/shaman_w.tga",
						playersettingmodule.RACE_WOLFMAN_M : "icon/face/wolfman_m.tga",
	}

	#app.USE_LOG_EXCHANGE: @view
	def __init__(self, is_view = False):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.inven = None

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				self.invenSpecial = None

			self.ItemListIdx = []

		self.TitleName = 0
		self.tooltipItem = None
		self.xStart = 0
		self.yStart = 0
		self.questionDialog = None

		self.is_view = is_view

		if self.is_view:
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				self.tooltipItem = interfaceHandler.tooltipItem

		if app.USE_LOG_EXCHANGE:
			self.ownerToolTipInfoDict = {}
			self.targetToolTipInfoDict = {}

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	class Item(ui.ListBoxEx.Item):
		def __init__(self,parent, text, value=0):
			ui.ListBoxEx.Item.__init__(self)
			self.textBox=ui.TextLine()
			self.textBox.SetParent(self)
			self.textBox.SetText(text)
			self.textBox.Show()
			self.value = value

		def GetValue(self):
			return self.value

		def __del__(self):
			ui.ListBoxEx.Item.__del__(self)

	def LoadDialog(self):
		PythonScriptLoader = ui.PythonScriptLoader()
		if app.ENABLE_NEW_EXCHANGE_WINDOW:
			PythonScriptLoader.LoadScriptFile(self, "UIScript/exchangedialog_new.py")
		else:
			PythonScriptLoader.LoadScriptFile(self, "UIScript/exchangedialog.py")

		self.OwnerSlot = self.GetChild("Owner_Slot")

		if self.is_view:
			self.OwnerSlot.SetSlotBaseImage("d:/ymir work/ui/public/slot_base.sub", 0.3500, 0.8500, 0.3500, 1.0)
		else:
			self.OwnerSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectOwnerEmptySlot))
			self.OwnerSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectOwnerItemSlot))

		self.OwnerSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInOwnerItem))
		self.OwnerSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		self.OwnerMoney = self.GetChild("Owner_Money_Value")

		if not app.ENABLE_NEW_EXCHANGE_WINDOW:
			self.OwnerAcceptLight = self.GetChild("Owner_Accept_Light")

			if self.is_view:
				self.OwnerAcceptLight.Enable()
			else:
				self.OwnerAcceptLight.Disable()

		self.OwnerMoneyButton = self.GetChild("Owner_Money")

		if not app.ENABLE_CHEQUE_SYSTEM:
			if not self.is_view:
				self.OwnerMoneyButton.SetEvent(ui.__mem_func__(self.OpenPickMoneyDialog))

		## Target
		self.TargetSlot = self.GetChild("Target_Slot")

		self.TargetSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInTargetItem))
		self.TargetSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		if self.is_view:
			self.TargetSlot.SetSlotBaseImage("d:/ymir work/ui/public/slot_base.sub", 0.3500, 0.8500, 0.3500, 1.0)
		else:
			if app.ENABLE_RENDER_TARGET:
				self.TargetSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectTargetItemSlot))

		self.TargetMoney = self.GetChild("Target_Money_Value")

		if not app.ENABLE_NEW_EXCHANGE_WINDOW:
			self.TargetAcceptLight = self.GetChild("Target_Accept_Light")

			if self.is_view:
				self.TargetAcceptLight.Enable()
			else:
				self.TargetAcceptLight.Disable()

		if app.ENABLE_CHEQUE_SYSTEM:
			self.OwnerCheque = self.GetChild("Owner_Cheque_Value")
			self.OwnerChequeButton = self.GetChild("Owner_Cheque")

			if not self.is_view:
				self.OwnerMoneyButton.SetEvent(ui.__mem_func__(self.OpenPickMoneyDialog), 0)
				self.OwnerChequeButton.SetEvent(ui.__mem_func__(self.OpenPickMoneyDialog), 1)

			self.TargetCheque = self.GetChild("Target_Cheque_Value")

		self.pickMoneyDialog = uicommon.PickMoneyDialog()
		self.pickMoneyDialog.SetAcceptEvent(ui.__mem_func__(self.OnPickMoney))
		self.pickMoneyDialog.SetTitleName(localeinfo.EXCHANGE_MONEY)

		## Button
		self.AcceptButton = self.GetChild("Owner_Accept_Button")

		if not self.is_view:
			self.AcceptButton.SetToggleDownEvent(ui.__mem_func__(self.AcceptExchange))

		if app.ENABLE_NEW_EXCHANGE_WINDOW:
			self.TargetAcceptButton = self.GetChild("Target_Accept_Button")

		self.TitleName = self.GetChild("TitleName")

		if self.is_view:
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.CloseDialog))
		else:
			self.GetChild("TitleBar").SetCloseEvent(net.SendExchangeExitPacket)

		if app.ENABLE_NEW_EXCHANGE_WINDOW:
			if self.is_view:
				self.GetChild("ExchangeLogs").Hide()
				self.SetSize(self.GetWidth(), self.GetHeight() - 30)

				self.LogsDropList = None
				self.LogsScrollBar = None

				self.AcceptButton.Disable()
				self.AcceptButton.Down()

				self.TargetAcceptButton.Disable()
				self.TargetAcceptButton.Down()
			else:
				self.ExchangeLogs = self.GetChild("ExchangeLogs")
				self.LogsScrollBar = ui.ThinScrollBar()
				self.LogsScrollBar.SetParent(self.ExchangeLogs)
				self.LogsScrollBar.SetPosition(9, 17)
				self.LogsScrollBar.SetScrollBarSize(50)
				self.LogsScrollBar.Show()
				self.LogsDropList = ui.ListBoxEx()
				self.LogsDropList.SetParent(self.ExchangeLogs)
				self.LogsDropList.itemHeight = 12
				self.LogsDropList.itemStep = 13
				self.LogsDropList.SetPosition(200+325, 27)
				self.LogsDropList.SetSize(0, 45)
				self.LogsDropList.SetScrollBar(self.LogsScrollBar)
				self.LogsDropList.SetViewItemCount(3)
				self.LogsDropList.Show()
				self.LogsScrollBar.Show()
				self.listOwnerSlot = []
				self.listTargetSlot = []

	def Destroy(self):
		if app.USE_LOG_EXCHANGE:
			self.ownerToolTipInfoDict = {}
			self.targetToolTipInfoDict = {}

		if self.pickMoneyDialog:
			self.pickMoneyDialog.Destroy()
			del self.pickMoneyDialog
			self.pickMoneyDialog = None

		#print "---------------------------------------------------------------------------- DESTROY EXCHANGE"

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.ItemListIdx = []

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.inven = None

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				self.invenSpecial = None

		self.ClearDictionary()

		self.OwnerSlot = 0
		self.OwnerMoney = 0

		if not app.ENABLE_NEW_EXCHANGE_WINDOW:
			self.OwnerAcceptLight = 0

		self.OwnerMoneyButton = 0
		self.TargetSlot = 0
		self.TargetMoney = 0

		if not app.ENABLE_NEW_EXCHANGE_WINDOW:
			self.TargetAcceptLight = 0

		self.TitleName = 0
		self.AcceptButton = 0
		self.tooltipItem = None

		if app.ENABLE_CHEQUE_SYSTEM:
			self.OwnerCheque = 0
			self.OwnerChequeButton = 0
			self.TargetCheque = 0

		if app.ENABLE_NEW_EXCHANGE_WINDOW:
			self.TargetAcceptButton = 0

			if self.LogsDropList:
				self.LogsDropList.RemoveAllItems()

			if self.LogsScrollBar:
				self.LogsScrollBar = None

	#app.USE_LOG_EXCHANGE: @name @level
	def OpenDialog(self, name = "", level = 0, src_gold = 0, trg_gold = 0, src_cheque = 0, trg_cheque = 0):
		if localeinfo.IsEUROPE() or localeinfo.IsYMIR():
			if self.is_view:
				self.TitleName.SetText(localeinfo.EXCHANGE_TITLE % (name, level))
			else:
				self.TitleName.SetText(localeinfo.EXCHANGE_TITLE % (exchange.GetNameFromTarget(), exchange.GetLevelFromTarget()))
		else:
			if self.is_view:
				self.TitleName.SetText(localeinfo.EXCHANGE_TITLE % (name))
			else:
				self.TitleName.SetText(localeinfo.EXCHANGE_TITLE % (exchange.GetNameFromTarget()))

		if self.is_view:
			if app.ENABLE_CHEQUE_SYSTEM:
				self.OwnerCheque.SetText(str(src_cheque))
				self.TargetCheque.SetText(str(trg_cheque))
				self.OwnerMoney.SetText(localeinfo.NumberToMoneyString(src_gold))
				self.TargetMoney.SetText(localeinfo.NumberToMoneyString(trg_gold))
			else:
				self.OwnerMoney.SetText(localeinfo.NumberToMoneyString(src_gold))
				self.TargetMoney.SetText(localeinfo.NumberToMoneyString(trg_gold))
		else:
			self.AcceptButton.Enable()
			self.AcceptButton.SetUp()

		self.SetTop()
		self.Show()

		if not self.is_view:
			if app.ENABLE_NEW_EXCHANGE_WINDOW:
				self.TargetAcceptButton.Disable()
				self.TargetAcceptButton.SetUp()
				self.LogsDropList.RemoveAllItems()
				self.LogsDropList.AppendItem(self.Item(self, localeinfo.NEW_EXCHANGE_YOU_READY % (str(time.strftime("[%H:%M:%S]"))), 0))

			(self.xStart, self.yStart, z) = player.GetMainCharacterPosition()

			if app.WJ_ENABLE_TRADABLE_ICON:
				self.ItemListIdx = []

	def CloseDialog(self):
		if not self.is_view:
			# wndMgr.OnceIgnoreMouseLeftButtonUpEvent()
			if app.WJ_ENABLE_TRADABLE_ICON:
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler:
					interfaceHandler.SetOnTopWindow(player.ON_TOP_WND_NONE)
					interfaceHandler.RefreshMarkInventoryBag()

		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

		if self.pickMoneyDialog:
			self.pickMoneyDialog.Close()

		self.Hide()

		if self.questionDialog:
			self.questionDialog.Close()
			self.questionDialog = None

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.ItemListIdx = []

	def AppendInformation(self, unixTime, info, error = False):
		if not error:
			chatType = chat.WHISPER_TYPE_SYSTEM

		time = datetime.datetime.fromtimestamp(unixTime).timetuple()

		chat.AppendWhisper(chatType, "$EXCHANGE_CHAT$", "["+strftime("%H:%M:%S", time) + "] "+info)

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def OnPickMoney(self, yang, cheque = 0):
		if app.ENABLE_CHEQUE_SYSTEM:
			net.SendExchangeElkAddPacket(yang)
			net.SendExchangeChequeAddPacket(cheque)
		else:
			net.SendExchangeElkAddPacket(yang)

	def OpenPickMoneyDialog(self, num = 0):
		if exchange.GetElkFromSelf() > 0 or (app.ENABLE_CHEQUE_SYSTEM and exchange.GetChequeFromSelf() > 0):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.EXCHANGE_CANT_EDIT_MONEY)
			return

		if app.ENABLE_CHEQUE_SYSTEM:
			self.pickMoneyDialog.Open(player.GetElk(), 2000000000, player.GetCheque(), 999)
		else:
			self.pickMoneyDialog.Open(player.GetElk(), 2000000000)

		self.pickMoneyDialog.SetFocus(num)

	def AcceptExchange(self):
		if app.ENABLE_NEW_EXCHANGE_WINDOW:
			atLeastOneItem = 0
			atLeastOneYang = 0
			atLeastOneWon = 0
			for i in xrange(exchange.EXCHANGE_ITEM_MAX_NUM):
				itemCount = exchange.GetItemCountFromTarget(i)
				if itemCount >= 1:
					atLeastOneYang = 1
					atLeastOneWon = 1
					break
			
			if exchange.GetElkFromTarget() >= 1:
				atLeastOneYang = 1	
				
			if exchange.GetChequeFromTarget() >= 1:
				atLeastOneWon = 1
			
			if atLeastOneItem or atLeastOneYang	or atLeastOneWon:
				net.SendExchangeAcceptPacket()
				self.AcceptButton.Disable()
			else:
				atLeastOneItem = 0
				atLeastOneYang = 0
				atLeastOneWon = 0
				for i in xrange(exchange.EXCHANGE_ITEM_MAX_NUM):
					itemCount = exchange.GetItemCountFromSelf(i)
					if itemCount >= 1:
						atLeastOneYang = 1
						atLeastOneWon = 1
						break
				
				if exchange.GetElkFromSelf() >= 1:
					atLeastOneYang = 1	
					
				if exchange.GetChequeFromSelf() >= 1:
					atLeastOneWon = 1
		
				if atLeastOneItem or atLeastOneYang	or atLeastOneWon:
					self.questionDialog = uicommon.QuestionDialog2()
					self.questionDialog.SetText1(localeinfo.NEW_EXCHANGE_ALERT1)
					self.questionDialog.SetText2(localeinfo.NEW_EXCHANGE_ALERT2)
					self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.AcceptQuestion))
					self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
					self.questionDialog.Open()
				else:
					net.SendExchangeAcceptPacket()
					self.AcceptButton.Disable()
		else:
			net.SendExchangeAcceptPacket()
			self.AcceptButton.Disable()

	if app.ENABLE_NEW_EXCHANGE_WINDOW:
		def AcceptQuestion(self):
			net.SendExchangeAcceptPacket()
			self.AcceptButton.Disable()
			if self.questionDialog:
				self.questionDialog.Close()
			
			self.questionDialog = None

		def OnCloseQuestionDialog(self):
			if self.questionDialog:
				self.questionDialog.Close()
			
			self.questionDialog = None
			self.AcceptButton.Enable()
			self.AcceptButton.SetUp()

	def SelectOwnerEmptySlot(self, SlotIndex):
		if False == mousemodule.mouseController.isAttached():
			return

		if app.USE_ACCE_SYSTEM:
			if player.GetAcceRefineWindowOpen() == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.ACCE_NOT_WINDOWOPEN)
				return

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if player.GetChangeLookWindowOpen() == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_OPEN_OTHER_WINDOW)
				return

		if mousemodule.mouseController.IsAttachedMoney():
			if app.ENABLE_CHEQUE_SYSTEM:
				net.SendExchangeElkAddPacket(mousemodule.mouseController.GetAttachedMoneyAmount(), mousemodule.mouseController.GetCheque())
			else:
				net.SendExchangeElkAddPacket(mousemodule.mouseController.GetAttachedMoneyAmount())
		else:
			attachedSlotType = mousemodule.mouseController.GetAttachedType()

			if (player.SLOT_TYPE_INVENTORY == attachedSlotType
				or player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedSlotType
				or player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedSlotType
				or player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedSlotType
				or player.SLOT_TYPE_STONE_INVENTORY == attachedSlotType
				or player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedSlotType
				or player.SLOT_TYPE_ENCHANT_INVENTORY == attachedSlotType
				or player.SLOT_TYPE_POTS_INVENTORY == attachedSlotType):

				attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)

				if app.USE_OFFLINESHOP:
					if uiofflineshop_ae.IsBuildingShop() and\
						uiofflineshop_ae.IsSaleSlot(attachedInvenType, mousemodule.mouseController.GetAttachedSlotNumber()):
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
						return

				SrcSlotNumber = mousemodule.mouseController.GetAttachedSlotNumber()
				DstSlotNumber = SlotIndex

				itemID = player.GetItemIndex(attachedInvenType, SrcSlotNumber)
				item.SelectItem(itemID)

				#if player.IsAntiFlagBySlot(SrcSlotNumber, item.ANTIFLAG_GIVE):
				if item.IsAntiFlag(item.ANTIFLAG_GIVE):
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.EXCHANGE_CANNOT_GIVE)
					mousemodule.mouseController.DeattachObject()
					return

				net.SendExchangeItemAddPacket(attachedInvenType, SrcSlotNumber, DstSlotNumber)
				if app.WJ_ENABLE_TRADABLE_ICON:
					self.ItemListIdx.append(SrcSlotNumber)

		mousemodule.mouseController.DeattachObject()

	if app.ENABLE_RENDER_TARGET:
		def SelectTargetItemSlot(self, SlotIndex):
			if app.IsPressed(app.DIK_LSHIFT):
				if uiRenderTarget.IsCanShowItems(exchange.GetItemVnumFromTarget(SlotIndex)):
					interfaceHandler = systemSetting.GetInterfaceHandler()
					if interfaceHandler:
						itemTransmutedVnum = exchange.GetChangeLookVnumFromTarget(SlotIndex)
						interfaceHandler.OpenRenderTargetWindow(0, itemTransmutedVnum if itemTransmutedVnum else exchange.GetItemVnumFromTarget(SlotIndex))

	def SelectOwnerItemSlot(self, SlotIndex):
		if app.IsPressed(app.DIK_LSHIFT):
			if uiRenderTarget.IsCanShowItems(exchange.GetItemVnumFromSelf(SlotIndex)):
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler:
					itemTransmutedVnum = exchange.GetChangeLookVnumFromSelf(SlotIndex)
					interfaceHandler.OpenRenderTargetWindow(0, itemTransmutedVnum if itemTransmutedVnum else exchange.GetItemVnumFromSelf(SlotIndex))
					return

		if player.ITEM_MONEY == mousemodule.mouseController.GetAttachedItemIndex():
			money = mousemodule.mouseController.GetAttachedItemCount()
			net.SendExchangeElkAddPacket(money)

		if app.ENABLE_CHEQUE_SYSTEM:
			if player.ITEM_CHEQUE == mousemodule.mouseController.GetAttachedItemIndex():
				cheque = mousemodule.mouseController.GetAttachedItemCount()
				net.SendExchangeChequeAddPacket(cheque)

	def RefreshOwnerSlot(self):
		for i in xrange(exchange.EXCHANGE_ITEM_MAX_NUM):
			itemIndex = exchange.GetItemVnumFromSelf(i)
			itemCount = exchange.GetItemCountFromSelf(i)
			if 1 == itemCount:
				itemCount = 0
			self.OwnerSlot.SetItemSlot(i, itemIndex, itemCount)
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				changelookvnum = exchange.GetChangeLookVnumFromSelf(i)
				if not changelookvnum == 0:
					self.OwnerSlot.SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")
				else:
					self.OwnerSlot.EnableSlotCoverImage(i, False)

		self.OwnerSlot.RefreshSlot()

	def RefreshTargetSlot(self):
		for i in xrange(exchange.EXCHANGE_ITEM_MAX_NUM):
			itemIndex = exchange.GetItemVnumFromTarget(i)
			itemCount = exchange.GetItemCountFromTarget(i)
			if 1 == itemCount:
				itemCount = 0
			self.TargetSlot.SetItemSlot(i, itemIndex, itemCount)
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				changelookvnum = exchange.GetChangeLookVnumFromTarget(i)
				if not changelookvnum == 0:
					self.TargetSlot.SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")
				else:
					self.TargetSlot.EnableSlotCoverImage(i, False)

		self.TargetSlot.RefreshSlot()

	def Refresh(self):
		self.RefreshOwnerSlot()
		self.RefreshTargetSlot()

		if app.ENABLE_CHEQUE_SYSTEM:
			self.OwnerCheque.SetText(str(exchange.GetChequeFromSelf()))
			self.TargetCheque.SetText(str(exchange.GetChequeFromTarget()))
			self.OwnerMoney.SetText(localeinfo.NumberToMoneyString(exchange.GetElkFromSelf()))
			self.TargetMoney.SetText(localeinfo.NumberToMoneyString(exchange.GetElkFromTarget()))
		else:
			self.OwnerMoney.SetText(str(exchange.GetElkFromSelf()))
			self.TargetMoney.SetText(str(exchange.GetElkFromTarget()))

		if exchange.GetAcceptFromSelf() == True:
			if not app.ENABLE_NEW_EXCHANGE_WINDOW:
				self.OwnerAcceptLight.Down()
			else:
				self.OwnerSlot.SetSlotBaseImage("d:/ymir work/ui/public/slot_base.sub", 0.3500, 0.8500, 0.3500, 1.0)
				self.LogsDropList.AppendItem(self.Item(self, localeinfo.NEW_EXCHANGE_YOU_ACCEPT % (str((time.strftime("[%H:%M:%S]")))), 0))
		else:
			if self.AcceptButton.IsDown() == True:
				self.LogsDropList.AppendItem(self.Item(self, localeinfo.NEW_EXCHANGE_YOU_ABORT % (str((time.strftime("[%H:%M:%S]")))), 0))
			
			self.AcceptButton.Enable()
			self.AcceptButton.SetUp()
			if not app.ENABLE_NEW_EXCHANGE_WINDOW:
				self.OwnerAcceptLight.SetUp()
			else:
				self.OwnerSlot.SetSlotBaseImage("d:/ymir work/ui/public/slot_base.sub", 1.0, 1.0, 1.0, 1.0)
		
		if exchange.GetAcceptFromTarget() == True:
			if not app.ENABLE_NEW_EXCHANGE_WINDOW:
				self.TargetAcceptLight.Down()
			else:
				self.TargetAcceptButton.Down()
				self.TargetSlot.SetSlotBaseImage("d:/ymir work/ui/public/slot_base.sub", 0.3500, 0.8500, 0.3500, 1.0)
				self.LogsDropList.AppendItem(self.Item(self, localeinfo.NEW_EXCHANGE_ACCEPT % (str((time.strftime("[%H:%M:%S]"))), exchange.GetNameFromTarget()), 0))
		else:
			if not app.ENABLE_NEW_EXCHANGE_WINDOW:
				self.TargetAcceptLight.SetUp()
			else:
				if self.TargetAcceptButton.IsDown() == True:
					self.LogsDropList.AppendItem(self.Item(self, localeinfo.NEW_EXCHANGE_ABORT % (str((time.strftime("[%H:%M:%S]"))), exchange.GetNameFromTarget()), 0))
				
				self.TargetAcceptButton.SetUp()
				self.TargetSlot.SetSlotBaseImage("d:/ymir work/ui/public/slot_base.sub", 1.0, 1.0, 1.0, 1.0)

	def OverInOwnerItem(self, slotIndex):
		if self.tooltipItem:
			if self.is_view:
				if self.ownerToolTipInfoDict.has_key(slotIndex):
					self.tooltipItem.ClearToolTip()

					self.tooltipItem.AddItemData(self.ownerToolTipInfoDict[slotIndex][0],\
													self.ownerToolTipInfoDict[slotIndex][1],\
													self.ownerToolTipInfoDict[slotIndex][2],\
													apply_random_list = self.ownerToolTipInfoDict[slotIndex][3])

					self.tooltipItem.ShowToolTip()
			else:
				self.tooltipItem.SetExchangeOwnerItem(slotIndex)

	def OverInTargetItem(self, slotIndex):
		if self.tooltipItem:
			if self.is_view:
				if self.targetToolTipInfoDict.has_key(slotIndex):
					self.tooltipItem.ClearToolTip()

					self.tooltipItem.AddItemData(self.targetToolTipInfoDict[slotIndex][0],\
													self.targetToolTipInfoDict[slotIndex][1],\
													self.targetToolTipInfoDict[slotIndex][2],\
													apply_random_list = self.targetToolTipInfoDict[slotIndex][3])

					self.tooltipItem.ShowToolTip()
			else:
				self.tooltipItem.SetExchangeTargetItem(slotIndex)

	def OverOutItem(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OnUpdate(self):
		if not self.IsShow():
			return

		if self.is_view:
			return

		USE_EXCHANGE_LIMIT_RANGE = 1000

		(x, y, z) = player.GetMainCharacterPosition()
		if abs(x - self.xStart) > USE_EXCHANGE_LIMIT_RANGE or abs(y - self.yStart) > USE_EXCHANGE_LIMIT_RANGE:
			(self.xStart, self.yStart, z) = player.GetMainCharacterPosition()
			
			net.SendExchangeExitPacket()

		if app.WJ_ENABLE_TRADABLE_ICON:
			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				if not self.inven or not self.invenSpecial:
					return
			else:
				if not self.inven:
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


	if app.WJ_ENABLE_TRADABLE_ICON:
		def CantTradableItem(self, slotIndex):
			itemIndex = player.GetItemIndex(slotIndex)

			if itemIndex:
				if app.ENABLE_SOUL_BIND_SYSTEM:
					if player.GetItemSealDate(player.INVENTORY, slotIndex) == -1 or player.GetItemSealDate(player.INVENTORY, slotIndex) > 0:
						return True

				return player.IsAntiFlagBySlot(slotIndex, item.ANTIFLAG_GIVE)

			return False

		def OnTop(self):
			if self.tooltipItem:
				self.tooltipItem.SetTop()

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.SetOnTopWindow(player.ON_TOP_WND_EXCHANGE)
				interfaceHandler.RefreshMarkInventoryBag()

		def SetInven(self, inven):
			if inven:
				self.inven = proxy(inven)

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			def SetSpecialInven(self, invenSpecial):
				if invenSpecial:
					self.invenSpecial = proxy(invenSpecial)

		def AddExchangeItemSlotIndex(self, idx):
			self.ItemListIdx.append(idx)
	else:
		def OnTop(self):
			if self.tooltipItem:
				self.tooltipItem.SetTop()

	def OnPressEscapeKey(self):
		if self.is_view:
			self.CloseDialog()
			return True

		return False

if app.USE_LOG_EXCHANGE:
	class ExchangeLog(ui.ScriptWindow):
		SUB_CHILDREN_DICT_KEY_DATE_WND = 0
		SUB_CHILDREN_DICT_KEY_DATE_TXT = 1
		SUB_CHILDREN_DICT_KEY_DATE_SPLIT = 2
		SUB_CHILDREN_DICT_KEY_IPV4_WND = 3
		SUB_CHILDREN_DICT_KEY_IPV4_TXT = 4
		SUB_CHILDREN_DICT_KEY_IPV4_SPLIT = 5
		SUB_CHILDREN_DICT_KEY_NAME_WND = 6
		SUB_CHILDREN_DICT_KEY_NAME_TXT = 7
		SUB_CHILDREN_DICT_KEY_NAME_SPLIT = 8
		SUB_CHILDREN_DICT_KEY_SRC_GOLD_WND = 9
		SUB_CHILDREN_DICT_KEY_SRC_GOLD_TXT = 10
		SUB_CHILDREN_DICT_KEY_SRC_GOLD_SPLIT = 11
		SUB_CHILDREN_DICT_KEY_SRC_CHEQUE_WND = 12
		SUB_CHILDREN_DICT_KEY_SRC_CHEQUE_TXT = 13
		SUB_CHILDREN_DICT_KEY_SRC_CHEQUE_SPLIT = 14
		SUB_CHILDREN_DICT_KEY_TRG_GOLD_WND = 15
		SUB_CHILDREN_DICT_KEY_TRG_GOLD_TXT = 16
		SUB_CHILDREN_DICT_KEY_TRG_GOLD_SPLIT = 17
		SUB_CHILDREN_DICT_KEY_TRG_CHEQUE_WND = 18
		SUB_CHILDREN_DICT_KEY_TRG_CHEQUE_TXT = 19
		SUB_CHILDREN_DICT_KEY_TRG_CHEQUE_SPLIT = 20
		SUB_CHILDREN_DICT_KEY_BTN_WND = 21
		SUB_CHILDREN_DICT_KEY_BTN = 22

		def __GotoPage(self, page):
			if page > 0 and page != self.actual_page and page <= self.max_page:
				if self.pagesCache.has_key(page):
					self.Clear(page, self.max_page, False)

					for log in self.pagesCache[page]:
						self.Load(log[0], log[1], log[2], log[3], log[4], log[5], log[6], log[7], log[8], True)

					self.RefreshPages()
				else:
					net.SendChatPacket("/log_exchange load {}".format(page))

		def __NextPage(self):
			if self.max_page > 1:
				page = self.actual_page + 1
				if page > self.max_page:
					page = 1

				if self.pagesCache.has_key(page):
					self.Clear(page, self.max_page, False)

					for log in self.pagesCache[page]:
						self.Load(log[0], log[1], log[2], log[3], log[4], log[5], log[6], log[7], log[8], True)

					self.RefreshPages()
				else:
					net.SendChatPacket("/log_exchange load {}".format(page))

		def __PrevPage(self):
			if self.max_page > 1:
				page = self.actual_page - 1
				if page < 1:
					page = self.max_page

				if self.pagesCache.has_key(page):
					self.Clear(page, self.max_page, False)

					for log in self.pagesCache[page]:
						self.Load(log[0], log[1], log[2], log[3], log[4], log[5], log[6], log[7], log[8], True)

					self.RefreshPages()
				else:
					net.SendChatPacket("/log_exchange load {}".format(page))

		def __LastPage(self):
			if self.max_page > 1:
				page = self.max_page
				if page == self.actual_page:
					return

				if self.pagesCache.has_key(page):
					self.Clear(page, self.max_page, False)

					for log in self.pagesCache[page]:
						self.Load(log[0], log[1], log[2], log[3], log[4], log[5], log[6], log[7], log[8], True)

					self.RefreshPages()
				else:
					net.SendChatPacket("/log_exchange load {}".format(page))

		def __FirstPage(self):
			if self.max_page > 1:
				page = 1
				if page == self.actual_page:
					return

				if self.pagesCache.has_key(page):
					self.Clear(page, self.max_page, False)

					for log in self.pagesCache[page]:
						self.Load(log[0], log[1], log[2], log[3], log[4], log[5], log[6], log[7], log[8], True)

					self.RefreshPages()
				else:
					net.SendChatPacket("/log_exchange load {}".format(page))

		def RefreshPages(self):
			currentPaginationPage = int(math.ceil(float(self.actual_page) / 5.0))
			shownPages = min(self.max_page - (5 * (currentPaginationPage - 1)), 5)

			for i in xrange(len(self.pageBtnsList)):
				currentPage = (i + ((currentPaginationPage - 1) * 5) + 1)
				self.pageBtnsList[i].SetUp()
				self.pageBtnsList[i].SetText("%d" % currentPage)
				self.pageBtnsList[i].SetEvent(ui.__mem_func__(self.__GotoPage), currentPage)

			map(ui.Button.Hide, self.pageBtnsList)
			map(ui.Button.Enable, self.pageBtnsList)

			for i in xrange(shownPages):
				self.pageBtnsList[i].Show()

			self.pageBtnsList[(self.actual_page - ((currentPaginationPage - 1) * 5)) - 1].Down()
			self.pageBtnsList[(self.actual_page - ((currentPaginationPage - 1) * 5)) - 1].Disable()

			if self.max_page <= 1:
				if self.max_page == 1:
					self.pageBtnsList[0].Hide()

				self.firstPageBtn.Hide()
				self.prevPageBtn.Hide()
				self.nextPageBtn.Hide()
				self.lastPageBtn.Hide()
			else:
				s = shownPages + 4
				t = (s * self.btnPageWidth) + ((s - 1) * 4)

				x, y = self.pages_content.GetLocalPosition()
				f = x + (self.pages_content.GetWidth() / 2)

				self.btnWnd.SetSize(t, self.btnPageHeight)
				self.btnWnd.SetPosition(f - (t / 2), y + 4)

				x, y = self.btnWnd.GetLocalPosition()

				self.firstPageBtn.SetPosition(x - 450, y)
				x += self.btnPageWidth + 4

				self.prevPageBtn.SetPosition(x - 450, y)
				x += self.btnPageWidth + 4

				for i in xrange(shownPages):
					self.pageBtnsList[i].SetPosition(x - 450, y)
					x += self.btnPageWidth + 4

				self.nextPageBtn.SetPosition(x - 450, y)
				x += self.btnPageWidth + 4

				self.lastPageBtn.SetPosition(x - 450, y)

				self.firstPageBtn.Show()
				self.prevPageBtn.Show()
				self.nextPageBtn.Show()
				self.lastPageBtn.Show()

		def Open(self, refresh):
			if refresh and not self.IsShow():
				return

			self.RefreshPages()

			self.Show()

		def Close(self):
			if self.wndExchangeView:
				self.wndExchangeView.CloseDialog()

			self.Hide()

		def OnPressEscapeKey(self):
			self.Close()
			return True

		def Clear(self, actual_page, max_page, refresh):
			if refresh:
				self.pagesCache = {}

			self.actual_page = actual_page
			self.max_page = max_page

			for children in self.childrensList:
				children.Hide()

			self.idx = 0

		def __LogDetails(self, ex_id):
			if self.exchangeCache.has_key(ex_id):
				if self.exchangeCache[ex_id][0][0] == True:
					if self.ex_id == ex_id:
						if self.wndExchangeView and self.wndExchangeView.IsShow():
							self.wndExchangeView.Hide()
						else:
							self.wndExchangeView.Show()
							self.wndExchangeView.SetTop()

						return

					self.ex_id = ex_id
					self.View_Open()
					return

			net.SendChatPacket("/log_exchange view {}".format(ex_id))

		def View_Clear(self, ex_id):
			self.ex_id = ex_id

			if self.exchangeCache.has_key(ex_id):
				self.exchangeCache[ex_id][0][0] = True

		def View_Load(self, ex_id,\
							own,\
							pos,\
							vnum,\
							count,\
							soul_bind,\
							transmutation_vnum,\
							socket1,\
							socket2,\
							socket3,\
							socket4,\
							socket5,\
							apply_random_type1,\
							apply_random_value1,\
							apply_random_path1,\
							apply_random_type2,\
							apply_random_value2,\
							apply_random_path2,\
							apply_random_type3,\
							apply_random_value3,\
							apply_random_path3,\
							apply_random_type4,\
							apply_random_value4,\
							apply_random_path4,\
							attr_type1,\
							attr_value1,\
							attr_path1,\
							attr_type2,\
							attr_value2,\
							attr_path2,\
							attr_type3,\
							attr_value3,\
							attr_path3,\
							attr_type4,\
							attr_value4,\
							attr_path4,\
							attr_type5,\
							attr_value5,\
							attr_path5,\
							attr_type6,\
							attr_value6,\
							attr_path6,\
							attr_type7,\
							attr_value7,\
							attr_path7,\
							backup_mode,\
							backup_attr_type1,\
							backup_attr_value1,\
							backup_attr_path1,\
							backup_attr_type2,\
							backup_attr_value2,\
							backup_attr_path2,\
							backup_attr_type3,\
							backup_attr_value3,\
							backup_attr_path3,\
							backup_attr_type4,\
							backup_attr_value4,\
							backup_attr_path4,\
							backup_attr_type5,\
							backup_attr_value5,\
							backup_attr_path5,\
							backup_attr_type6,\
							backup_attr_value6,\
							backup_attr_path6,\
							backup_attr_type7,\
							backup_attr_value7,\
							backup_attr_path7,\
							enchant_type1,\
							enchant_value1,\
							enchant_path1,\
							enchant_type2,\
							enchant_value2,\
							enchant_path2,\
							enchant_type3,\
							enchant_value3,\
							enchant_path3,\
							enchant_type4,\
							enchant_value4,\
							enchant_path4,\
							set_value):
			if self.exchangeCache.has_key(ex_id):
				self.exchangeCache[ex_id].append([own,\
													pos,\
													vnum,\
													count,\
													soul_bind,\
													transmutation_vnum,\
													socket1,\
													socket2,\
													socket3,\
													socket4,\
													socket5,\
													apply_random_type1,\
													apply_random_value1,\
													apply_random_path1,\
													apply_random_type2,\
													apply_random_value2,\
													apply_random_path2,\
													apply_random_type3,\
													apply_random_value3,\
													apply_random_path3,\
													apply_random_type4,\
													apply_random_value4,\
													apply_random_path4,\
													attr_type1,\
													attr_value1,\
													attr_path1,\
													attr_type2,\
													attr_value2,\
													attr_path2,\
													attr_type3,\
													attr_value3,\
													attr_path3,\
													attr_type4,\
													attr_value4,\
													attr_path4,\
													attr_type5,\
													attr_value5,\
													attr_path5,\
													attr_type6,\
													attr_value6,\
													attr_path6,\
													attr_type7,\
													attr_value7,\
													attr_path7,\
													backup_mode,\
													backup_attr_type1,\
													backup_attr_value1,\
													backup_attr_path1,\
													backup_attr_type2,\
													backup_attr_value2,\
													backup_attr_path2,\
													backup_attr_type3,\
													backup_attr_value3,\
													backup_attr_path3,\
													backup_attr_type4,\
													backup_attr_value4,\
													backup_attr_path4,\
													backup_attr_type5,\
													backup_attr_value5,\
													backup_attr_path5,\
													backup_attr_type6,\
													backup_attr_value6,\
													backup_attr_path6,\
													backup_attr_type7,\
													backup_attr_value7,\
													backup_attr_path7,\
													enchant_type1,\
													enchant_value1,\
													enchant_path1,\
													enchant_type2,\
													enchant_value2,\
													enchant_path2,\
													enchant_type3,\
													enchant_value3,\
													enchant_path3,\
													enchant_type4,\
													enchant_value4,\
													enchant_path4,\
													set_value])

		def View_Open(self):
			if self.wndExchangeView:
				self.wndExchangeView.CloseDialog()

			if not self.exchangeCache.has_key(self.ex_id):
				return

			if not self.wndExchangeView:
				self.wndExchangeView = ExchangeDialog(True)
				self.wndExchangeView.LoadDialog()
				self.wndExchangeView.Hide()

			for i in xrange(self.wndExchangeView.OwnerSlot.GetSlotCount()):
				self.wndExchangeView.OwnerSlot.ClearSlot(i)

			for i in xrange(self.wndExchangeView.TargetSlot.GetSlotCount()):
				self.wndExchangeView.TargetSlot.ClearSlot(i)

			self.wndExchangeView.ownerToolTipInfoDict = {}
			self.wndExchangeView.targetToolTipInfoDict = {}

			x, y = self.GetLocalPosition()
			self.wndExchangeView.SetPosition(x + 4, y + self.GetHeight() - self.wndExchangeView.GetHeight())

			j = 0
			for item in self.exchangeCache[self.ex_id]:
				j += 1
				if j == 1:
					continue

				wndSlot = self.wndExchangeView.OwnerSlot if item[0] == 1 else self.wndExchangeView.TargetSlot
				wndSlot.SetItemSlot(item[1], item[2], 0 if item[3] == 1 else item[3])

				dictToolTip = self.wndExchangeView.ownerToolTipInfoDict if item[0] == 1 else self.wndExchangeView.targetToolTipInfoDict
				dictToolTip[item[1]] = [\
											item[2],\
											[\
												item[6],\
												item[7],\
												item[8],\
												item[9],\
												item[10],\
											],\
											[\
												[\
													item[23],\
													item[24],\
												],\
												[\
													item[25],\
													item[26],\
												],\
												[\
													item[27],\
													item[28],\
												],\
												[\
													item[29],\
													item[30],\
												],\
												[\
													item[31],\
													item[32],\
												],\
												[\
													item[33],\
													item[34],\
												],\
												[\
													item[35],\
													item[36],\
												],\
											],\
											[\
												[\
													item[11],\
													item[12],\
												],\
												[\
													item[14],\
													item[15],\
												],\
												[\
													item[17],\
													item[18],\
												],\
												[\
													item[20],\
													item[21],\
												],\
											]\
										]

			self.wndExchangeView.OpenDialog(self.exchangeCache[self.ex_id][0][1],\
											self.exchangeCache[self.ex_id][0][2],\
											self.exchangeCache[self.ex_id][0][3],\
											self.exchangeCache[self.ex_id][0][4],\
											self.exchangeCache[self.ex_id][0][5],\
											self.exchangeCache[self.ex_id][0][6])

		def Load(self, ex_id, unix_time, src_ip, trg_name, trg_level, src_gold, trg_gold, src_cheque, trg_cheque, cached = False):
			if not cached:
				if not self.pagesCache.has_key(self.actual_page):
					self.pagesCache[self.actual_page] = []

				self.pagesCache[self.actual_page].append([ex_id, unix_time, src_ip, trg_name, trg_level, src_gold, trg_gold, src_cheque, trg_cheque])

			if not self.exchangeCache.has_key(ex_id):
				self.exchangeCache[ex_id] = []
				self.exchangeCache[ex_id].append([False, trg_name, trg_level, src_gold, trg_gold, src_cheque, trg_cheque])

			self.subChildrensDict[self.idx + 1][self.SUB_CHILDREN_DICT_KEY_DATE_TXT].SetText(datetime.datetime.fromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S"))
			self.subChildrensDict[self.idx + 1][self.SUB_CHILDREN_DICT_KEY_IPV4_TXT].SetText(src_ip)
			self.subChildrensDict[self.idx + 1][self.SUB_CHILDREN_DICT_KEY_NAME_TXT].SetText(trg_name)
			self.subChildrensDict[self.idx + 1][self.SUB_CHILDREN_DICT_KEY_SRC_GOLD_TXT].SetText(localeinfo.NumberToStringDotted(src_gold))
			self.subChildrensDict[self.idx + 1][self.SUB_CHILDREN_DICT_KEY_SRC_CHEQUE_TXT].SetText(localeinfo.NumberToStringDotted(src_cheque))
			self.subChildrensDict[self.idx + 1][self.SUB_CHILDREN_DICT_KEY_TRG_GOLD_TXT].SetText(localeinfo.NumberToStringDotted(trg_gold))
			self.subChildrensDict[self.idx + 1][self.SUB_CHILDREN_DICT_KEY_TRG_CHEQUE_TXT].SetText(localeinfo.NumberToStringDotted(trg_cheque))
			self.subChildrensDict[self.idx + 1][self.SUB_CHILDREN_DICT_KEY_BTN].SetEvent(ui.__mem_func__(self.__LogDetails), ex_id)
			self.childrensList[self.idx].Show()
			self.idx += 1

		def __LoadScript(self):
			PythonScriptLoader = ui.PythonScriptLoader()
			if localeinfo.IsARABIC():
				PythonScriptLoader.LoadScriptFile(self, "uiscript/ae_exchangelog_window.py")
			else:
				PythonScriptLoader.LoadScriptFile(self, "uiscript/exchangelog_window.py")

			self.board_content = self.GetChild("board_content_ui")

			self.board = self.GetChild("board_ui")
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))

			self.pagesCache = {}
			self.exchangeCache = {}

			self.actual_page = 0
			self.max_page = 0

			self.idx = 0

			self.childrensList = []
			self.subChildrensDict = {}

			for i in xrange(10):
				children = ui.Bar()
				children.SetParent(self.board_content)
				children.SetPosition(2, (i * 31) + 2)
				children.SetSize(800 - 20 - 14 - 4, 30)
				children.SetColor(0x57FFFFFF)
				self.childrensList.append(children)

			for i in xrange(10):
				subChildrenDict = {}
## view button 
				children = ui.Window()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 200 + 1 + 2 + 70 + 1 + 2 + 70 + 1 + 2 + 70 + 1 + 2 + 70 + 1 + 2, 1)
				children.SetSize(92, 30)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_BTN_WND] = children

				children = ui.MakeButton(subChildrenDict[self.SUB_CHILDREN_DICT_KEY_BTN_WND], 2, 4, "", "d:/ymir work/ui/game/exchange_log/btn/", "view_0.tga", "view_1.tga", "view_2.tga")
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_BTN] = children
##
## NAME
				children = ui.Window()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 200 + 1 + 2 + 70 + 1 + 2 + 70 + 1 + 2, 1)
				children.SetSize(150, 30)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_NAME_WND] = children

				children = ui.TextLine()
				children.SetParent(subChildrenDict[self.SUB_CHILDREN_DICT_KEY_NAME_WND])
				children.SetPosition(0, 0)
				children.SetOutline()
				children.SetHorizontalAlignCenter()
				children.SetVerticalAlignCenter()
				children.SetWindowHorizontalAlignCenter()
				children.SetWindowVerticalAlignCenter()
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_NAME_TXT] = children

				children = ui.Bar()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 200 + 1 + 2 + 70 + 1 + 2 + 70 + 1 + 2, 2)
				children.SetSize(1, 28)
				children.SetColor(0x37FFFFFF)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_NAME_SPLIT] = children
##
## your gold (giving)
				children = ui.Window()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 200 + 1 + 2 + 75 , 1)
				children.SetSize(70, 30)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_SRC_GOLD_WND] = children

				children = ui.TextLine()
				children.SetParent(subChildrenDict[self.SUB_CHILDREN_DICT_KEY_SRC_GOLD_WND])
				children.SetPosition(0, 0)
				children.SetPackedFontColor(0xffff7675)
				children.SetOutline()
				children.SetHorizontalAlignCenter()
				children.SetVerticalAlignCenter()
				children.SetWindowHorizontalAlignCenter()
				children.SetWindowVerticalAlignCenter()
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_SRC_GOLD_TXT] = children

				children = ui.Bar()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 200 + 1 + 2 + 70 + 1, 2)
				children.SetSize(1, 28)
				children.SetColor(0x37FFFFFF)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_SRC_GOLD_SPLIT] = children
## your won (giving)
				children = ui.Window()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 200 + 1 + 2 + 7, 1)
				children.SetSize(70, 30)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_SRC_CHEQUE_WND] = children

				children = ui.TextLine()
				children.SetParent(subChildrenDict[self.SUB_CHILDREN_DICT_KEY_SRC_CHEQUE_WND])
				children.SetPosition(0, 0)
				children.SetPackedFontColor(0xffff7675)
				children.SetOutline()
				children.SetHorizontalAlignCenter()
				children.SetVerticalAlignCenter()
				children.SetWindowHorizontalAlignCenter()
				children.SetWindowVerticalAlignCenter()
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_SRC_CHEQUE_TXT] = children

				children = ui.Bar()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 200 + 1 + 2 + 10, 2)
				children.SetSize(1, 28)
				children.SetColor(0x37FFFFFF)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_SRC_CHEQUE_SPLIT] = children
## target gold (taken)
				children = ui.Window()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 130 + 1 + 2, 1)
				children.SetSize(70, 30)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_TRG_GOLD_WND] = children

				children = ui.TextLine()
				children.SetParent(subChildrenDict[self.SUB_CHILDREN_DICT_KEY_TRG_GOLD_WND])
				children.SetPosition(0, 0)
				children.SetPackedFontColor(0xff00b894)
				children.SetOutline()
				children.SetHorizontalAlignCenter()
				children.SetVerticalAlignCenter()
				children.SetWindowHorizontalAlignCenter()
				children.SetWindowVerticalAlignCenter()
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_TRG_GOLD_TXT] = children

				children = ui.Bar()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 120 + 1 + 2, 2)
				children.SetSize(1, 28)
				children.SetColor(0x37FFFFFF)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_TRG_GOLD_SPLIT] = children
## target won 
				children = ui.Window()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 120 + 1 + 2 - 65, 1)
				children.SetSize(70, 30)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_TRG_CHEQUE_WND] = children

				children = ui.TextLine()
				children.SetParent(subChildrenDict[self.SUB_CHILDREN_DICT_KEY_TRG_CHEQUE_WND])
				children.SetPosition(0, 0)
				children.SetPackedFontColor(0xff00b894)
				children.SetOutline()
				children.SetHorizontalAlignCenter()
				children.SetVerticalAlignCenter()
				children.SetWindowHorizontalAlignCenter()
				children.SetWindowVerticalAlignCenter()
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_TRG_CHEQUE_TXT] = children

				children = ui.Bar()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 120 + 1 + 2 - 60, 2)
				children.SetSize(1, 28)
				children.SetColor(0x37FFFFFF)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_TRG_CHEQUE_SPLIT] = children

## IP 
				children = ui.Window()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 50, 1)
				children.SetSize(70, 30)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_IPV4_WND] = children

				children = ui.TextLine()
				children.SetParent(subChildrenDict[self.SUB_CHILDREN_DICT_KEY_IPV4_WND])
				children.SetPosition(0, 0)
				children.SetOutline()
				children.SetHorizontalAlignCenter()
				children.SetVerticalAlignCenter()
				children.SetWindowHorizontalAlignCenter()
				children.SetWindowVerticalAlignCenter()
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_IPV4_TXT] = children

				children = ui.Bar()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 35 + 1, 2)
				children.SetSize(1, 28)
				children.SetColor(0x37FFFFFF)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_IPV4_SPLIT] = children


## left (date)
				children = ui.Window()
				children.SetParent(self.childrensList[i])
				children.SetPosition(0, 1)
				children.SetSize(100 - 2, 30)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_DATE_WND] = children

				children = ui.TextLine()
				children.SetParent(subChildrenDict[self.SUB_CHILDREN_DICT_KEY_DATE_WND])
				children.SetPosition(20, 0)
				children.SetOutline()
				children.SetHorizontalAlignCenter()
				children.SetVerticalAlignCenter()
				children.SetWindowHorizontalAlignCenter()
				children.SetWindowVerticalAlignCenter()
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_DATE_TXT] = children

				children = ui.Bar()
				children.SetParent(self.childrensList[i])
				children.SetPosition(100 - 2 + 1 + 2 + 70 + 1 + 2 + 200 + 1 + 2 + 70 + 1 + 2 + 70 + 1 + 2 + 70 + 1 + 2 + 70 + 1, 2)
				children.SetSize(1, 28)
				children.SetColor(0x37FFFFFF)
				children.Show()
				subChildrenDict[self.SUB_CHILDREN_DICT_KEY_DATE_SPLIT] = children



				self.subChildrensDict[i + 1] = subChildrenDict

			self.btnWnd = ui.Window()
			self.btnWnd.SetParent(self)
			self.btnWnd.SetSize(0, 0)
			self.btnWnd.Hide()

			self.pages_content = self.GetChild("pages_content_ui")

			self.pageBtnsList = []

			for i in range(1, 6):
				tmp = self.GetChild("page%d_button_ui" % (i))

				if i == 1:
					tmp.Show()
					tmp.Down()
					tmp.Disable()
				else:
					tmp.Hide()

				self.pageBtnsList.append(tmp)

			self.nextPageBtn = self.GetChild("next_button_ui")
			self.nextPageBtn.SetEvent(ui.__mem_func__(self.__NextPage))

			self.prevPageBtn = self.GetChild("prev_button_ui")
			self.prevPageBtn.SetEvent(ui.__mem_func__(self.__PrevPage))

			self.lastPageBtn = self.GetChild("last_next_button_ui")
			self.lastPageBtn.SetEvent(ui.__mem_func__(self.__LastPage))

			self.firstPageBtn = self.GetChild("first_prev_button_ui")
			self.firstPageBtn.SetEvent(ui.__mem_func__(self.__FirstPage))

			self.btnPageWidth = self.firstPageBtn.GetWidth()
			self.btnPageHeight = self.firstPageBtn.GetHeight()

		def Destroy(self):
			if self.board:
				self.board.SetCloseEvent(None)
				self.board = None

			if self.wndExchangeView:
				self.wndExchangeView.Destroy()
				del self.wndExchangeView
				self.wndExchangeView = None

			for v in self.pageBtnsList:
				v.SetEvent(None)

			self.pageBtnsList = []

			if self.nextPageBtn:
				self.nextPageBtn.SetEvent(None)
				self.nextPageBtn = None

			if self.prevPageBtn:
				self.prevPageBtn.SetEvent(None)
				self.prevPageBtn = None

			if self.lastPageBtn:
				self.lastPageBtn.SetEvent(None)
				self.lastPageBtn = None

			if self.firstPageBtn:
				self.firstPageBtn.SetEvent(None)
				self.firstPageBtn = None

			for v in self.subChildrensDict.values():
				for k2, v2 in v.items():
					if k2 == self.SUB_CHILDREN_DICT_KEY_BTN:
						v2.SetEvent(None)

					del v2
					k2 = {}

			self.subChildrensDict = {}

			for children in self.childrensList:
				del children

			self.childrensList = []

			if self.btnWnd:
				del self.btnWnd
				self.btnWnd = None

			if self.pages_content:
				self.pages_content = None

			if self.board_content:
				self.board_content = None

		def __init__(self):
			self.wndExchangeView = None

			ui.ScriptWindow.__init__(self)
			self.__LoadScript()

		def __del__(self):
			ui.ScriptWindow.__del__(self)
