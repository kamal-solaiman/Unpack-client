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
import uiquicksell
import uiprivateshopbuilder
import localeinfo
import constinfo
import ime
import uiinventory
import sys
import dragon_soul_refine_settings

if app.USE_OFFLINESHOP:
	import offlineshop
	import uiofflineshop_ae

if app.ENABLE_DS_GRADE_MYTH:
	import wndMgr
	import uitooltip

import systemSetting

from _weakref import proxy

ITEM_FLAG_APPLICABLE = 1 << 14

class DragonSoulWindow(ui.ScriptWindow):
	KIND_TAP_TITLES = [
		uiscriptlocale.DRAGONSOUL_TAP_TITLE_1,
		uiscriptlocale.DRAGONSOUL_TAP_TITLE_2,
		uiscriptlocale.DRAGONSOUL_TAP_TITLE_3,
		uiscriptlocale.DRAGONSOUL_TAP_TITLE_4,
		uiscriptlocale.DRAGONSOUL_TAP_TITLE_5,
		uiscriptlocale.DRAGONSOUL_TAP_TITLE_6,
		uiscriptlocale.DRAGONSOUL_TAP_TITLE_7
	]

	if app.ENABLE_DS_GRADE_MYTH:
		PAGE_TAB_TITLES = [
			uiscriptlocale.DRAGONSOUL_PAGE_BUTTON_1,
			uiscriptlocale.DRAGONSOUL_PAGE_BUTTON_2,
			uiscriptlocale.DRAGONSOUL_PAGE_BUTTON_3,
			uiscriptlocale.DRAGONSOUL_PAGE_BUTTON_4,
			uiscriptlocale.DRAGONSOUL_PAGE_BUTTON_5,
			uiscriptlocale.DRAGONSOUL_PAGE_BUTTON_6
		]

	SET_BONUS_ROMAN = ["I", "II", "III", "IV", "V", "VI"]

	DSS_ART_PATH = "d:/ymir work/ui/game/dragonsoul/"
	SET_BONUS_HELP_CHECK = "d:/ymir work/ui/public/check_image.sub"

	SET_BONUS_HELP_KEYS = [
		("DRAGONSOUL_SET_HELP_1", "Wear Legendary or Myth souls to earn set points."),
		("DRAGONSOUL_SET_HELP_2", "Higher grade and step give more points."),
		("DRAGONSOUL_SET_HELP_3", "Myth souls are worth far more than Legendary."),
		("DRAGONSOUL_SET_HELP_4", "Reach a threshold to unlock the next tier."),
		("DRAGONSOUL_SET_HELP_5", "A full final-step Myth set reaches the top tier."),
		("DRAGONSOUL_SET_HELP_6", "Only your active deck counts."),
	]

	if app.ENABLE_MAILBOX:
		interface = None

	def AutoDS(self, on):
		if on:
			if not self.isActivated:
				if self.__CanActivateDeck():
					net.SendChatPacket("/dragon_soul activate " + str(self.deckPageIndex))
				else:
					bkDeckPageIndex = self.deckPageIndex
					if bkDeckPageIndex == 1:
						self.SetDeckPage(0)
					else:
						self.SetDeckPage(1)

					if self.__CanActivateDeck():
						net.SendChatPacket("/dragon_soul activate " + str(self.deckPageIndex))
					else:
						self.SetDeckPage(bkDeckPageIndex)

						self.isActivated = False
						self.activateButton.SetUp()
		else:
			if self.isActivated:
				net.SendChatPacket("/dragon_soul deactivate")

	def __init__(self):
		self.dsSetPoints = 0
		self.dsSetTier = -1
		self.dsSetNextThreshold = -1
		self.dsSetApplys = []
		self.dsSetInitialized = False
		self.setBonusGlow = None
		self.setBonusInfoButton = None
		self.setBonusInfoImage = None
		self.setBonusToolTip = None
		self.setBonusToolTipWidgets = []
		self.setBonusLastRenderedState = None
		self.setBonusHelpToolTip = None
		self.setBonusHelpWidgets = []

		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.interface = None
		self.wndDragonSoulRefine = None

		self.questionDialog = None
		self.tooltipItem = None
		if app.ENABLE_DS_GRADE_MYTH:
			self.toolTip = uitooltip.ToolTip()
		self.sellingSlotNumber = -1
		self.isLoaded = 0
		self.isActivated = False
		self.DSKindIndex = 0
		self.tabDict = None
		self.tabButtonDict = None
		self.deckPageIndex = 0
		self.inventoryPageIndex = 0
		self.refineSlots = []

		self.SetWindowName("DragonSoulWindow")
		self.__LoadWindow()

		if app.ENABLE_DS_SET:
			self.setGrade = 0

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()

		ui.ScriptWindow.Show(self)
		self.SetTop()

		if app.ENABLE_MAILBOX:
			self.RefreshItemSlot()
		if app.ENABLE_DS_REFINE_ALL:
			dragon_soul_refine_settings.ds_type_page = self.DSKindIndex
			dragon_soul_refine_settings.ds_grade_page = self.inventoryPageIndex

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return
		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "dragonsoulwindow.py")

		except:
			import exception
			exception.Abort("dragonsoulwindow.LoadWindow.LoadObject")

		try:
			if localeinfo.IsARABIC():
				self.board = self.GetChild("Equipment_Base")
				self.board.SetScale(-1.0, 1.0)
				self.board.SetRenderingRect(-1.0, 0.0, 1.0, 0.0)
				self.board = self.GetChild("Tab_01")
				self.board.SetScale(-1.0, 1.0)
				self.board.SetRenderingRect(-1.0, 0.0, 1.0, 0.0)
				self.board = self.GetChild("Tab_02")
				self.board.SetScale(-1.0, 1.0)
				self.board.SetRenderingRect(-1.0, 0.0, 1.0, 0.0)
				self.board = self.GetChild("Tab_03")
				self.board.SetScale(-1.0, 1.0)
				self.board.SetRenderingRect(-1.0, 0.0, 1.0, 0.0)
				self.board = self.GetChild("Tab_04")
				self.board.SetScale(-1.0, 1.0)
				self.board.SetRenderingRect(-1.0, 0.0, 1.0, 0.0)
				self.board = self.GetChild("Tab_05")
				self.board.SetScale(-1.0, 1.0)
				self.board.SetRenderingRect(-1.0, 0.0, 1.0, 0.0)
				self.board = self.GetChild("Tab_06")
				self.board.SetScale(-1.0, 1.0)
				self.board.SetRenderingRect(-1.0, 0.0, 1.0, 0.0)
				self.board = self.GetChild("Tab_07")
				self.board.SetScale(-1.0, 1.0)
				self.board.SetRenderingRect(-1.0, 0.0, 1.0, 0.0)

			wndItem = self.GetChild("ItemSlot")
			wndEquip = self.GetChild("EquipmentSlot")
			self.activateButton = self.GetChild("activate")
			if app.__ENABLE_RANGE_ALCHEMY__:
				self.shopButton = self.GetChild("shop_open")
				
			if app.__ENABLE_REFINE_ALCHEMY__:
				self.refineButton = self.GetChild("refine_window_open")
			self.deckTab = []
			self.deckTab.append(self.GetChild("deck1"))
			self.deckTab.append(self.GetChild("deck2"))
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
			self.inventoryTab = []
			self.inventoryTab.append(self.GetChild("Inventory_Tab_01"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_02"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_03"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_04"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_05"))
			if app.ENABLE_DS_GRADE_MYTH:
				self.inventoryTab.append(self.GetChild("Inventory_Tab_06"))
			self.tabDict = {
				0 : self.GetChild("Tab_01"),
				1 : self.GetChild("Tab_02"),
				2 : self.GetChild("Tab_03"),
				3 : self.GetChild("Tab_04"),
				4 : self.GetChild("Tab_05"),
				5 : self.GetChild("Tab_06"),
				6 : self.GetChild("Tab_07"),
			}
			self.tabButtonDict = {
				0 : self.GetChild("Tab_Button_01"),
				1 : self.GetChild("Tab_Button_02"),
				2 : self.GetChild("Tab_Button_03"),
				3 : self.GetChild("Tab_Button_04"),
				4 : self.GetChild("Tab_Button_05"),
				5 : self.GetChild("Tab_Button_06"),
				6 : self.GetChild("Tab_Button_07"),
			}
			self.tabText = self.GetChild("tab_text_area")

		except:
			import exception
			exception.Abort("InventoryWindow.LoadWindow.BindObject")

		## DragonSoul Kind Tap
		for (tabKey, tabButton) in self.tabButtonDict.items():
			tabButton.SetEvent(ui.__mem_func__(self.SetDSKindIndex), tabKey)

		## Item
		wndItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		wndItem.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndItem.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndItem.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))

		## Equipment
		wndEquip.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptyEquipSlot))
		wndEquip.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectEquipItemSlot))
		wndEquip.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseEquipItemSlot))
		wndEquip.SetUseSlotEvent(ui.__mem_func__(self.UseEquipItemSlot))
		wndEquip.SetOverInItemEvent(ui.__mem_func__(self.OverInEquipItem))
		wndEquip.SetOverOutItemEvent(ui.__mem_func__(self.OverOutEquipItem))

		## Deck
		self.deckTab[0].SetToggleDownEvent(ui.__mem_func__(self.SetDeckPage), 0)
		self.deckTab[1].SetToggleDownEvent(ui.__mem_func__(self.SetDeckPage), 1)
		self.deckTab[0].SetToggleUpEvent(ui.__mem_func__(self.__DeckButtonDown), 0)
		self.deckTab[1].SetToggleUpEvent(ui.__mem_func__(self.__DeckButtonDown), 1)
		self.deckTab[0].Down()

		## Grade button
		self.inventoryTab[0].SetEvent(ui.__mem_func__(self.SetInventoryPage), 0)
		self.inventoryTab[1].SetEvent(ui.__mem_func__(self.SetInventoryPage), 1)
		self.inventoryTab[2].SetEvent(ui.__mem_func__(self.SetInventoryPage), 2)
		self.inventoryTab[3].SetEvent(ui.__mem_func__(self.SetInventoryPage), 3)
		self.inventoryTab[4].SetEvent(ui.__mem_func__(self.SetInventoryPage), 4)
		if app.ENABLE_DS_GRADE_MYTH:
			self.inventoryTab[5].SetEvent(ui.__mem_func__(self.SetInventoryPage), 5)
		self.inventoryTab[0].Down()

		## Etc
		self.wndItem = wndItem
		self.wndEquip = wndEquip

		self.dlgQuestion = uicommon.QuestionDialog2()
		self.dlgQuestion.Close()

		self.activateButton.SetToggleDownEvent(ui.__mem_func__(self.ActivateButtonClick))
		self.activateButton.SetToggleUpEvent(ui.__mem_func__(self.ActivateButtonClick))
		
		
		if app.__ENABLE_RANGE_ALCHEMY__:
			self.shopButton.SetEvent(ui.__mem_func__(self.__OpenShopWindow))
			
		if app.__ENABLE_REFINE_ALCHEMY__:
			self.refineButton.SetEvent(ui.__mem_func__(self.__OpenRefineAlchemyWindow))
		
		self.wndPopupDialog = uicommon.PopupDialog()

		##
		self.listHighlightedSlot = []

		## Refresh
		self.SetInventoryPage(0)
		self.RefreshItemSlot()
		self.RefreshEquipSlotWindow()
		self.RefreshBagSlotWindow()
		self.SetDSKindIndex(0)
		self.activateButton.Enable()
		self.deckTab[self.deckPageIndex].Down()
		self.activateButton.SetUp()

		self.__CreateSetBonusWidgets()

	def Destroy(self):
		self.interface = None
		self.wndDragonSoulRefine = None

		self.ClearDictionary()
		self.tooltipItem = None
		if app.ENABLE_DS_GRADE_MYTH:
			self.toolTip = None
		self.wndItem = None
		self.wndEquip = None
		self.activateButton = None
		if app.__ENABLE_RANGE_ALCHEMY__:
			self.shopButton = None

		if app.__ENABLE_REFINE_ALCHEMY__:
			self.refineButton = None

		self.questionDialog = None
		self.mallButton = None
		self.inventoryTab = []
		self.deckTab = []
		self.equipmentTab = []
		self.tabDict = None
		self.tabButtonDict = None
		self.setBonusGlow = None
		self.setBonusInfoButton = None
		self.setBonusInfoImage = None
		self.setBonusToolTip = None
		self.setBonusToolTipWidgets = []
		self.setBonusLastRenderedState = None
		self.setBonusHelpToolTip = None
		self.setBonusHelpWidgets = []

	def Close(self):
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

		if app.ENABLE_DS_GRADE_MYTH:
			if None != self.toolTip:
				self.toolTip.Hide()

		self.Hide()

	def __DeckButtonDown(self, deck):
		self.deckTab[deck].Down()

	def SetInventoryPage(self, page):
		if self.inventoryPageIndex != page:
			self.__HighlightSlot_ClearCurrentPage()
		self.inventoryPageIndex = page
		if app.ENABLE_DS_GRADE_MYTH:
			self.inventoryTab[(page+1)%6].SetUp()
			self.inventoryTab[(page+2)%6].SetUp()
			self.inventoryTab[(page+3)%6].SetUp()
			self.inventoryTab[(page+4)%6].SetUp()
			self.inventoryTab[(page+5)%6].SetUp()
		else:
			self.inventoryTab[(page+1)%5].SetUp()
			self.inventoryTab[(page+2)%5].SetUp()
			self.inventoryTab[(page+3)%5].SetUp()
			self.inventoryTab[(page+4)%5].SetUp()
		
		self.RefreshBagSlotWindow()
		if app.ENABLE_DS_REFINE_ALL:
			dragon_soul_refine_settings.ds_grade_page = self.inventoryPageIndex

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def RefreshItemSlot(self):
		self.RefreshBagSlotWindow()
		self.RefreshEquipSlotWindow()

	if app.ENABLE_DS_GRADE_MYTH:
		def OverInInventoryTab(self, page):
			if self.toolTip:
				tooltip = self.PAGE_TAB_TITLES[page]
				arglen = len(tooltip)
				pos_x, pos_y = wndMgr.GetMousePosition()
				self.toolTip.ClearToolTip()
				self.toolTip.SetThinBoardSize(11 * arglen)
				self.toolTip.AppendTextLine(tooltip)
				self.toolTip.Show()

		def OverOutInventoryTab(self, page):
			if self.toolTip:
				self.toolTip.Hide()

		def OnUpdate(self):
			if self.toolTip:
				for i in xrange(len(self.PAGE_TAB_TITLES)):
					if self.inventoryTab[i].IsIn():
						self.OverInInventoryTab(i)
						break
					else:
						self.OverOutInventoryTab(i)

	def RefreshEquipSlotWindow(self):
		if self.wndEquip is None:
			return

		for i in xrange(7):
			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(player.INVENTORY, player.DRAGON_SOUL_EQUIPMENT_SLOT_START + i)
			itemVnum = player.GetItemIndex(slotNumber)
			self.wndEquip.SetItemSlot(player.DRAGON_SOUL_EQUIPMENT_SLOT_START + i, itemVnum, 0)
			self.wndEquip.EnableSlot(player.DRAGON_SOUL_EQUIPMENT_SLOT_START + i)

			if itemVnum != 0:
				item.SelectItem(itemVnum)
				for j in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(j)

					remain_time = 999
					if item.LIMIT_REAL_TIME == limitType:
						remain_time = player.GetItemMetinSocket(player.INVENTORY, slotNumber, 0) - app.GetGlobalTimeStamp()
					elif item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
						remain_time = player.GetItemMetinSocket(player.INVENTORY, slotNumber, 0) - app.GetGlobalTimeStamp()
					elif item.LIMIT_TIMER_BASED_ON_WEAR == limitType:
						remain_time = player.GetItemMetinSocket(player.INVENTORY, slotNumber, 0)

					if remain_time <= 0:
						self.wndEquip.DisableSlot(player.DRAGON_SOUL_EQUIPMENT_SLOT_START + i)
						break

		self.wndEquip.RefreshSlot()

	def ActivateEquipSlotWindow(self, deck):
		for i in xrange(7):
			if deck == 2:
				plusCount = 7
			else:
				plusCount = 0
			self.wndEquip.ActivateSlot(player.DRAGON_SOUL_EQUIPMENT_SLOT_START + i + plusCount)

	def DeactivateEquipSlotWindow(self):
		for i in xrange(14):
			self.wndEquip.DeactivateSlot(player.DRAGON_SOUL_EQUIPMENT_SLOT_START + i)

	def RefreshStatus(self):
		self.RefreshItemSlot()

	def __InventoryLocalSlotPosToGlobalSlotPos(self, window_type, local_slot_pos):
		if player.INVENTORY == window_type:
			return self.deckPageIndex * player.DRAGON_SOUL_EQUIPMENT_FIRST_SIZE + local_slot_pos

		if app.ENABLE_DS_GRADE_MYTH:
			return (self.DSKindIndex * 6 * player.DRAGON_SOUL_PAGE_SIZE) + self.inventoryPageIndex * player.DRAGON_SOUL_PAGE_SIZE + local_slot_pos
		else:
			return (self.DSKindIndex * 5 * player.DRAGON_SOUL_PAGE_SIZE) + self.inventoryPageIndex * player.DRAGON_SOUL_PAGE_SIZE + local_slot_pos



	def __InventoryGlobalSlotPosToLocalSlotPos(self, window_type, global_slot_pos):
		if player.INVENTORY == window_type:
			return global_slot_pos - self.deckPageIndex * player.DRAGON_SOUL_EQUIPMENT_FIRST_SIZE

		return global_slot_pos - (self.DSKindIndex * 6 * player.DRAGON_SOUL_PAGE_SIZE) - self.inventoryPageIndex * player.DRAGON_SOUL_PAGE_SIZE

	def __RefreshBagSlot(self, i):
		getItemVNum=player.GetItemIndex
		getItemCount=player.GetItemCount
		setItemVnum=self.wndItem.SetItemSlot
		if app.ENABLE_MAILBOX:
			if self.interface:
				onTopWindow = self.interface.GetOnTopWindow()

		self.wndItem.ClearSlot(i)
		self.wndItem.EnableSlot(i)
		#<- dragon soul kind
		slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(player.DRAGON_SOUL_INVENTORY, i)

		itemCount = getItemCount(player.DRAGON_SOUL_INVENTORY, slotNumber)
		if 0 == itemCount:
			self.wndItem.ClearSlot(i)
			return
		elif 1 == itemCount:
			itemCount = 0

		diffuseColor = (1.0, 1.0, 1.0, 1.0)
		if slotNumber in self.refineSlots:
			diffuseColor = (1.0, 1.0, 1.0, 0.5)

		itemVnum = getItemVNum(player.DRAGON_SOUL_INVENTORY, slotNumber)
		setItemVnum(i, itemVnum, itemCount, diffuseColor = diffuseColor)

		if itemVnum != 0:
			item.SelectItem(itemVnum)
			for j in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(j)

				# ????? remain_time?? ???????? u? ??? ?????? ?????? ????? ????
				remain_time = 999
				if item.LIMIT_REAL_TIME == limitType:
					remain_time = player.GetItemMetinSocket(player.DRAGON_SOUL_INVENTORY, slotNumber, 0)
				elif item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
					remain_time = player.GetItemMetinSocket(player.DRAGON_SOUL_INVENTORY, slotNumber, 0)
				elif item.LIMIT_TIMER_BASED_ON_WEAR == limitType:
					remain_time = player.GetItemMetinSocket(player.DRAGON_SOUL_INVENTORY, slotNumber, 0)
			
				if remain_time <= 0:
					self.wndItem.DisableSlot(i)
					break

			if app.ENABLE_MAILBOX:
				if itemVnum and self.interface and onTopWindow:
					if self.interface.MarkUnusableDSInvenSlotOnTopWnd(onTopWindow, slotNumber):
						self.wndItem.SetUnusableSlotOnTopWnd(i)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(i)
				else:
					self.wndItem.SetUsableSlotOnTopWnd(i)

	def RefreshSingleBagSlot(self, cell):
		if self.wndItem is None:
			return

		slotNumber = self.__InventoryGlobalSlotPosToLocalSlotPos(player.DRAGON_SOUL_INVENTORY, cell)
		if slotNumber < 0 or slotNumber >= player.DRAGON_SOUL_PAGE_SIZE:
			return

		self.__RefreshBagSlot(slotNumber)
		self.wndItem.RefreshSlot()

	def RefreshBagSlotWindow(self):
		if self.wndItem is None:
			return

		getItemVNum=player.GetItemIndex
		getItemCount=player.GetItemCount
		setItemVnum=self.wndItem.SetItemSlot
		for i in xrange(player.DRAGON_SOUL_PAGE_SIZE):
			self.__RefreshBagSlot(i)

		self.__HighlightSlot_RefreshCurrentPage()

		if app.QUICK_SELL_SYSTEM:
			self.RefreshQuickSellMarks()

		self.wndItem.RefreshSlot()

	def ShowToolTip(self, window_type, slotIndex):
		if None != self.tooltipItem:
			if player.INVENTORY == window_type:
				if app.ENABLE_DS_SET and player.IsDSEquipmentSlot(window_type, slotIndex):
					self.tooltipItem.SetInventoryItem(slotIndex, player.EQUIPMENT)
				else:
					self.tooltipItem.SetInventoryItem(slotIndex)
			else:
				self.tooltipItem.SetInventoryItem(slotIndex, player.DRAGON_SOUL_INVENTORY)
			
			if app.USE_OFFLINESHOP:
				if uiofflineshop_ae.IsBuildingShop():
					self.__AddTooltipSaleMode(window_type, slotIndex)
				else:
					self.tooltipItem.DeclareShortcut(("key_shift", "key_c"), localeinfo.TOOLTIP_QUICKACTIVE_ALL)
					self.tooltipItem.DeclareShortcut(("key_shift", "key_c"), localeinfo.TOOLTIP_QUICKDEACTIVE_ALL)
					self.tooltipItem.DeclareShortcut(("key_alt", "key_rclick"), localeinfo.TOOLTIP_QUICKSEARCH_OFFLINESHOP)
	if app.USE_OFFLINESHOP:
		def __AddTooltipSaleMode(self, window_type, slot):
			if player.IsEquipmentSlot(slot):
				return
			
			itemIndex = player.GetItemIndex(window_type, slot)
			if itemIndex !=0:
				item.SelectItem(itemIndex)
				if item.IsAntiFlag(item.ANTIFLAG_MYSHOP) or item.IsAntiFlag(item.ANTIFLAG_GIVE):
					return
				
				self.tooltipItem.AddRightClickForSale()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnTop(self):
		if None != self.tooltipItem:
			self.tooltipItem.SetTop()

	def OverOutItem(self):
		self.wndItem.SetUsableItem(False)
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OverInItem(self, overSlotPos):
		self.wndItem.DeactivateSlot(overSlotPos)
		overSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(player.DRAGON_SOUL_INVENTORY, overSlotPos)

		try:
			self.listHighlightedSlot.remove(overSlotPos)
		except:
			pass

		if mousemodule.mouseController.isAttached():
			attachedItemType = mousemodule.mouseController.GetAttachedType()
			if player.SLOT_TYPE_INVENTORY == attachedItemType:
				attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
				attachedItemVNum = mousemodule.mouseController.GetAttachedItemIndex()
				if item.IsItemUsedForDragonSoul(attachedItemVNum, player.DRAGON_SOUL_INVENTORY):
					self.wndItem.SetUsableItem(True)

		self.ShowToolTip(player.DRAGON_SOUL_INVENTORY, overSlotPos)

	def __UseItem(self, slotIndex):
		ItemVNum = player.GetItemIndex(player.DRAGON_SOUL_INVENTORY, slotIndex)
		if 0 == player.GetItemMetinSocket(player.DRAGON_SOUL_INVENTORY, slotIndex, 0):
			self.wndPopupDialog.SetText(localeinfo.DRAGON_SOUL_EXPIRED)
			self.wndPopupDialog.Open()
			return

		self.__EquipItem(slotIndex)

	def __EquipItem(self, slotIndex):
		ItemVNum = player.GetItemIndex(player.DRAGON_SOUL_INVENTORY, slotIndex)
		item.SelectItem(ItemVNum)
		subType = item.GetItemSubType()
		equipSlotPos = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + self.deckPageIndex * player.DRAGON_SOUL_EQUIPMENT_FIRST_SIZE + subType
		srcItemPos = (player.DRAGON_SOUL_INVENTORY, slotIndex)

		dstItemPos = (player.INVENTORY, equipSlotPos)

		self.__OpenQuestionDialog_DS_Equip(True, srcItemPos, dstItemPos)

	def SelectItemSlot(self, itemSlotIndex):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		itemSlotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(player.DRAGON_SOUL_INVENTORY, itemSlotIndex)

		if mousemodule.mouseController.isAttached():
			if self.wndDragonSoulRefine.IsShow():
				mousemodule.mouseController.DeattachObject()
				return

			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			attachedItemVID = mousemodule.mouseController.GetAttachedItemIndex()

			attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)

			if player.RESERVED_WINDOW != attachedInvenType:
				if item.IsItemUsedForDragonSoul(attachedItemVID, player.DRAGON_SOUL_INVENTORY):
					self.__OpenQuestionDialog(attachedInvenType, attachedSlotPos, player.DRAGON_SOUL_INVENTORY, itemSlotIndex)

			mousemodule.mouseController.DeattachObject()
		else:
			curCursorNum = app.GetCursor()

			if app.QUICK_SELL_SYSTEM and app.IsPressed(app.DIK_TAB):
				self.interface.ToggleQuickSellSlot(player.DRAGON_SOUL_INVENTORY, itemSlotIndex)
				self.RefreshBagSlotWindow()
			elif app.SELL == curCursorNum:
				self.__SellItem(itemSlotIndex)
			elif app.BUY == curCursorNum:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SHOP_BUY_INFO)
			elif app.IsPressed(app.DIK_LALT):
				link = player.GetItemLink(player.DRAGON_SOUL_INVENTORY, itemSlotIndex)
				ime.PasteString(link)
			else:
				selectedItemVNum = player.GetItemIndex(player.DRAGON_SOUL_INVENTORY, itemSlotIndex)
				itemCount = player.GetItemCount(player.DRAGON_SOUL_INVENTORY, itemSlotIndex)
				mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_DRAGON_SOUL_INVENTORY, itemSlotIndex, selectedItemVNum, itemCount)
				self.interface.SetUseItemMode(False)
				snd.PlaySound("sound/ui/pick.wav")

	if app.ENABLE_MAILBOX:
		def SetCantMouseEventSlot(self, index):
			slot_index = index
			if app.ENABLE_DS_GRADE_MYTH:
				slot_index = index - (self.DSKindIndex * player.DRAGON_SOUL_PAGE_COUNT * player.DRAGON_SOUL_PAGE_SIZE) - self.inventoryPageIndex * player.DRAGON_SOUL_PAGE_SIZE
			else:
				slot_index = index - (self.DSKindIndex * 5 * player.DRAGON_SOUL_PAGE_SIZE) - self.inventoryPageIndex * player.DRAGON_SOUL_PAGE_SIZE

			if slot_index < 0 or slot_index >= player.DRAGON_SOUL_PAGE_SIZE:
				return

			self.wndItem.SetCantMouseEventSlot(slot_index)

	def __SellItem(self, itemSlotPos):
		if not player.IsDSEquipmentSlot(player.DRAGON_SOUL_INVENTORY, itemSlotPos):
			self.sellingSlotNumber = itemSlotPos
			itemIndex = player.GetItemIndex(player.DRAGON_SOUL_INVENTORY, itemSlotPos)
			itemCount = player.GetItemCount(player.DRAGON_SOUL_INVENTORY, itemSlotPos)

			item.SelectItem(itemIndex)

			if item.IsAntiFlag(item.ANTIFLAG_SELL):
				popup = uicommon.PopupDialog()
				popup.SetText(localeinfo.SHOP_CANNOT_SELL_ITEM)
				popup.SetAcceptEvent(self.__OnClosePopupDialog)
				popup.Open()
				self.popup = popup
				return

			itemPrice = item.GetISellItemPrice()

			if item.Is1GoldItem():
				itemPrice = itemCount / itemPrice / 5
			else:
				itemPrice = itemPrice * itemCount / 5

			item.GetItemName(itemIndex)
			itemName = item.GetItemName()

			self.questionDialog = uicommon.QuestionDialog()
			self.questionDialog.SetText(localeinfo.DO_YOU_SELL_ITEM(itemName, itemCount, itemPrice))
			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.SellItem))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
			self.questionDialog.Open()
			self.questionDialog.count = itemCount

	def SellItem(self):
		if app.USE_OFFLINESHOP:
			if uiofflineshop_ae.IsBuildingShop() and\
				uiofflineshop_ae.IsSaleSlot(player.DRAGON_SOUL_INVENTORY, self.sellingSlotNumber):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				return

		net.SendShopSellPacketNew(self.sellingSlotNumber, self.questionDialog.count, player.DRAGON_SOUL_INVENTORY)
		snd.PlaySound("sound/ui/money.wav")
		self.OnCloseQuestionDialog()

	def OnCloseQuestionDialog(self):
		if self.questionDialog:
			self.questionDialog.Close()

		self.questionDialog = None

	def __OnClosePopupDialog(self):
		self.pop = None

	def SelectEmptySlot(self, selectedSlotPos):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		selectedSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(player.DRAGON_SOUL_INVENTORY, selectedSlotPos)
		if mousemodule.mouseController.isAttached():
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			attachedItemCount = mousemodule.mouseController.GetAttachedItemCount()
			attachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()

			attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)

			if app.USE_OFFLINESHOP:
				if uiofflineshop_ae.IsBuildingShop() and\
					uiofflineshop_ae.IsSaleSlot(player.SlotTypeToInvenType(attachedSlotType),attachedSlotPos):
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
					return

			if player.SLOT_TYPE_PRIVATE_SHOP == attachedSlotType:
				mousemodule.mouseController.RunCallBack("INVENTORY")
			elif player.SLOT_TYPE_SHOP == attachedSlotType:
				net.SendShopBuyPacket(attachedSlotPos)
			elif player.SLOT_TYPE_SAFEBOX == attachedSlotType:
				if player.ITEM_MONEY == attachedItemIndex:
					net.SendSafeboxWithdrawMoneyPacket(mousemodule.mouseController.GetAttachedItemCount())
					snd.PlaySound("sound/ui/money.wav")
				else:
					net.SendSafeboxCheckoutPacket(attachedSlotPos, player.DRAGON_SOUL_INVENTORY, selectedSlotPos)
			elif player.SLOT_TYPE_MALL == attachedSlotType:
				net.SendMallCheckoutPacket(attachedSlotPos, player.DRAGON_SOUL_INVENTORY, selectedSlotPos)
			elif player.RESERVED_WINDOW != attachedInvenType:
				if player.IsDSEquipmentSlot(attachedInvenType, attachedSlotPos):
					srcItemPos = (attachedInvenType, attachedSlotPos)
					dstItemPos = (player.DRAGON_SOUL_INVENTORY, selectedSlotPos)
					self.__OpenQuestionDialog_DS_Equip(False, srcItemPos, dstItemPos)
				else:
					itemCount = player.GetItemCount(attachedInvenType, attachedSlotPos)
					attachedCount = mousemodule.mouseController.GetAttachedItemCount()

					self.__SendMoveItemPacket(attachedInvenType, attachedSlotPos, player.DRAGON_SOUL_INVENTORY, selectedSlotPos, attachedCount)

			mousemodule.mouseController.DeattachObject()

	def UseItemSlot(self, slotIndex):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS():
			return
		elif player.IsActingEmotion():
			return

		if app.USE_BL_FISH_EVENT:
			if mousemodule.mouseController.isAttached():
				if player.SLOT_TYPE_FISH_EVENT == mousemodule.mouseController.GetAttachedType():
					return

		slotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(player.DRAGON_SOUL_INVENTORY, slotIndex)
		
		if app.USE_OFFLINESHOP and\
			uiofflineshop_ae.IsBuildingShop():
			itemIndex = player.GetItemIndex(player.DRAGON_SOUL_INVENTORY, slotIndex)
			if itemIndex:
				item.SelectItem(itemIndex)
				if not item.IsAntiFlag(item.ANTIFLAG_GIVE) and\
					not item.IsAntiFlag(item.ANTIFLAG_MYSHOP):
					offlineshop.ShopBuilding_AddItem(player.DRAGON_SOUL_INVENTORY, slotIndex)
				else:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				
				return
		
		try:
			if self.wndDragonSoulRefine.IsShow():
				if uiprivateshopbuilder.IsBuildingPrivateShop():
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.USE_ITEM_FAILURE_PRIVATE_SHOP)
					return
				
				if self.interface.IsShowDlgQuestionWindow():
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
					return
				
				self.wndDragonSoulRefine.AutoSetItem((player.DRAGON_SOUL_INVENTORY, slotIndex), 1)
				return
		except:
			pass
		
		if app.USE_OFFLINESHOP and\
			not uiofflineshop_ae.IsBuildingShop() and\
			(app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT)):

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				wndShopOffline = interfaceHandler.wndShopOffline
				if wndShopOffline:
					wndSearchShop = wndShopOffline.wndSearchShop
					if wndSearchShop:
						itemVnum = player.GetItemIndex(player.DRAGON_SOUL_INVENTORY, slotIndex)
						item.SelectItem(itemVnum)
						wndSearchShop.SearchByName(item.GetItemName())
						return

		self.__UseItem(slotIndex)
		mousemodule.mouseController.DeattachObject()
		self.OverOutItem()

	def __SendMoveItemPacket(self, srcSlotWindow, srcSlotPos, dstSlotWindow, dstSlotPos, srcItemCount):
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.MOVE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		if self.interface.IsShowDlgQuestionWindow():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
			return

		net.SendItemMovePacket(srcSlotWindow , srcSlotPos, dstSlotWindow, dstSlotPos, srcItemCount)

	def OverOutEquipItem(self):
		self.OverOutItem()

	def OverInEquipItem(self, overSlotPos):
		overSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(player.INVENTORY, overSlotPos)

		if mousemodule.mouseController.isAttached():
			attachedItemType = mousemodule.mouseController.GetAttachedType()
			if player.SLOT_TYPE_INVENTORY == attachedItemType:
				attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
				attachedItemVNum = mousemodule.mouseController.GetAttachedItemIndex()
				if item.IsItemUsedForDragonSoul(attachedItemVNum, player.INVENTORY):
					self.wndItem.SetUsableItem(True)

		self.ShowToolTip(player.INVENTORY, overSlotPos)

	def UseEquipItemSlot(self, slotIndex):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS():
			return

		if app.USE_BL_FISH_EVENT:
			if mousemodule.mouseController.isAttached():
				if player.SLOT_TYPE_FISH_EVENT == mousemodule.mouseController.GetAttachedType():
					return

		slotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(player.INVENTORY, slotIndex)

		self.__UseEquipItem(slotIndex)
		mousemodule.mouseController.DeattachObject()
		self.OverOutEquipItem()

	def __UseEquipItem(self, slotIndex):
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.USE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		self.__OpenQuestionDialog_DS_Equip(False, (player.INVENTORY, slotIndex), (player.DRAGON_SOUL_INVENTORY, 1))

	def SelectEquipItemSlot(self, itemSlotIndex):
		curCursorNum = app.GetCursor()
		if app.SELL == curCursorNum:
			return
		elif app.BUY == curCursorNum:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SHOP_BUY_INFO)
			return

		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		itemSlotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(player.INVENTORY, itemSlotIndex)

		if mousemodule.mouseController.isAttached():
			if self.wndDragonSoulRefine.IsShow():
				mousemodule.mouseController.DeattachObject()
				return

			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			attachedItemVID = mousemodule.mouseController.GetAttachedItemIndex()

			attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)
			if player.RESERVED_WINDOW != attachedInvenType:
				if item.IsItemUsedForDragonSoul(attachedItemVID, player.INVENTORY):
					self.__OpenQuestionDialog(attachedInvenType, attachedSlotPos, player.INVENTORY, itemSlotIndex)

			mousemodule.mouseController.DeattachObject()
		else:
			if app.IsPressed(app.DIK_LALT):
				link = player.GetItemLink(player.INVENTORY, itemSlotIndex)
				ime.PasteString(link)
			else:
				selectedItemVNum = player.GetItemIndex(player.INVENTORY, itemSlotIndex)
				itemCount = player.GetItemCount(player.INVENTORY, itemSlotIndex)
				mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_INVENTORY, itemSlotIndex, selectedItemVNum, itemCount)
				self.interface.SetUseItemMode(False)
				snd.PlaySound("sound/ui/pick.wav")

	def SelectEmptyEquipSlot(self, selectedSlot):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		selectedSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(player.INVENTORY, selectedSlot)

		if mousemodule.mouseController.isAttached():
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			attachedItemCount = mousemodule.mouseController.GetAttachedItemCount()
			attachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()

			if player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedSlotType:
				if 0 == player.GetItemMetinSocket(player.DRAGON_SOUL_INVENTORY, attachedSlotPos, 0):
					self.wndPopupDialog.SetText(localeinfo.DRAGON_SOUL_EXPIRED)
					self.wndPopupDialog.Open()
					return

				item.SelectItem(attachedItemIndex)
				subType = item.GetItemSubType()
				if subType != (selectedSlot - player.DRAGON_SOUL_EQUIPMENT_SLOT_START):
					self.wndPopupDialog.SetText(localeinfo.DRAGON_SOUL_UNMATCHED_SLOT)
					self.wndPopupDialog.Open()
				else:
					srcItemPos = (player.DRAGON_SOUL_INVENTORY, attachedSlotPos)

					dstItemPos = (player.INVENTORY, selectedSlotPos)
					self.__OpenQuestionDialog_DS_Equip(True, srcItemPos, dstItemPos)

			mousemodule.mouseController.DeattachObject()

	def __OpenQuestionDialog_DS_Equip(self, Equip, srcItemPos, dstItemPos):
		NeededGold = 500000;
		if self.interface.IsShowDlgQuestionWindow():
			self.interface.CloseDlgQuestionWindow()

		self.srcItemPos = srcItemPos
		self.dstItemPos = dstItemPos

		self.dlgQuestion.SetAcceptEvent(ui.__mem_func__(self.__Accept_DS_Equip))
		self.dlgQuestion.SetCancelEvent(ui.__mem_func__(self.__Cancel))

		if Equip:
			self.dlgQuestion.SetText1(localeinfo.DRAGON_SOUL_EQUIP_WARNING1)
			self.dlgQuestion.SetText2(localeinfo.DRAGON_SOUL_EQUIP_WARNING2)
		else:
			self.dlgQuestion.SetText1(localeinfo.DRAGON_SOUL_UNEQUIP_WARNING1 % (localeinfo.NumberToDecimal(NeededGold)))
			self.dlgQuestion.SetText2(localeinfo.DRAGON_SOUL_UNEQUIP_WARNING2)

		self.dlgQuestion.Open()

	def __Accept_DS_Equip(self):
		self.dlgQuestion.Close()
		if (-1, -1) == self.dstItemPos:
			net.SendItemUsePacket(*self.srcItemPos)
		else:
			self.__SendMoveItemPacket(*(self.srcItemPos + self.dstItemPos + (0,)))

	def __OpenQuestionDialog(self, srcItemInvenType, srcItemPos, dstItemInvenType, dstItemPos):
		if self.interface.IsShowDlgQuestionWindow():
			self.interface.CloseDlgQuestionWindow()

		if srcItemInvenType == dstItemInvenType:
			if srcItemPos == dstItemPos:
				return

		self.srcItemPos = (srcItemInvenType, srcItemPos)
		self.dstItemPos = (dstItemInvenType, dstItemPos)

		self.dlgQuestion.SetAcceptEvent(ui.__mem_func__(self.__Accept))
		self.dlgQuestion.SetCancelEvent(ui.__mem_func__(self.__Cancel))

		getItemVNum = player.GetItemIndex
		self.dlgQuestion.SetText1("%s" % item.GetItemNameByVnum(getItemVNum(self.srcItemPos[0],self.srcItemPos[1])) )
		self.dlgQuestion.SetText2(localeinfo.INVENTORY_REALLY_USE_ITEM)

		self.dlgQuestion.Open()

	def __Accept(self):
		self.dlgQuestion.Close()
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.USE_ITEM_FAILURE_PRIVATE_SHOP)
			return
		
		if self.interface.IsShowDlgQuestionWindow():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
			return
		
		net.SendItemUseToItemPacket(self.srcItemPos[0], self.srcItemPos[1], self.dstItemPos[0], self.dstItemPos[1])
		self.srcItemPos = (0, 0)
		self.dstItemPos = (0, 0)

	def __Cancel(self):
		self.srcItemPos = (0, 0)
		self.dstItemPos = (0, 0)
		self.dlgQuestion.Close()

	def SetDSKindIndex(self, kindIndex):
		if self.DSKindIndex != kindIndex:
			self.__HighlightSlot_ClearCurrentPage()

		self.DSKindIndex = kindIndex

		for (tabKey, tabButton) in self.tabButtonDict.items():
			if kindIndex!=tabKey:
				tabButton.SetUp()

		for tabValue in self.tabDict.itervalues():
			tabValue.Hide()

		self.tabDict[kindIndex].Show()
		self.tabText.SetText(DragonSoulWindow.KIND_TAP_TITLES[kindIndex])

		self.RefreshBagSlotWindow()
		if app.ENABLE_DS_REFINE_ALL:
			dragon_soul_refine_settings.ds_type_page = kindIndex

	def SetDeckPage(self, page):
		if page == self.deckPageIndex:
			return

		if self.isActivated:
			self.DeactivateDragonSoul()
			net.SendChatPacket("/dragon_soul deactivate")
		self.deckPageIndex = page
		self.deckTab[page].Down()
		self.deckTab[(page+1)%2].SetUp()

		self.RefreshEquipSlotWindow()

	if app.ENABLE_DS_SET:
		def SetDSSetGrade(self, grade):
			self.setGrade = grade

		def GetDSSetGrade(self):
			if not self.isActivated:
				return 0

			return self.setGrade

	def SetSetBonusInfo(self, points, tier, nextThreshold, stats):
		try:
			oldTier = self.dsSetTier
			self.dsSetPoints = int(points)
			self.dsSetTier = int(tier)
			self.dsSetNextThreshold = int(nextThreshold)
			self.dsSetApplys = []
			if stats and stats != "-":
				for pair in stats.split(","):
					t, v = pair.split(":")
					self.dsSetApplys.append((int(t), int(v)))
			self.__UpdateSetBonusView()
			if self.dsSetInitialized and self.dsSetTier > oldTier and self.dsSetTier >= 0:
				self.__ShowSetBonusTierUp(self.dsSetTier)
			self.dsSetInitialized = True
		except Exception, e:
			import dbg
			dbg.TraceError("DragonSoul SetSetBonusInfo parse failed: %s" % str(e))

	def GetSetBonusState(self):
		return (self.dsSetTier, self.dsSetPoints, self.dsSetNextThreshold, list(self.dsSetApplys))

	def __ShowSetBonusTierUp(self, tier):
		try:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DRAGONSOUL_SET_TIERUP % (tier + 1,))
		except Exception, e:
			import dbg
			dbg.TraceError("DragonSoul tier-up chat failed: %s" % str(e))

	def __CreateSetBonusWidgets(self):
		centerX, centerY = 144, 140
		emblemW, emblemH = 38, 34
		emblemX = centerX - emblemW / 2
		emblemY = centerY - emblemH / 2
		if localeinfo.IsARABIC():
			emblemX = self.GetWidth() - emblemX - emblemW

		# Central emblem button, shown only while a set bonus is active. Its own
		# hover-pulse supplies the glow; hovering opens the "what you get now" tooltip.
		self.setBonusGlow = ui.Button()
		self.setBonusGlow.SetParent(self)
		self.setBonusGlow.SetPosition(int(emblemX), int(emblemY))
		try:
			self.setBonusGlow.SetUpVisual(self.DSS_ART_PATH + "dss_inventory_button_01.tga")
			self.setBonusGlow.SetOverVisual(self.DSS_ART_PATH + "dss_inventory_button_02.tga")
			self.setBonusGlow.SetDownVisual(self.DSS_ART_PATH + "dss_inventory_button_03.tga")
			self.setBonusGlow.EnableHoverPulse()
			self.setBonusGlow.SetHoverPulseSpeed(1.5)
		except:
			pass
		self.setBonusGlow.SetOverEvent(ui.__mem_func__(self.__OnSetBonusOverIn))
		self.setBonusGlow.SetOverOutEvent(ui.__mem_func__(self.__OnSetBonusOverOut))
		self.setBonusGlow.Hide()

		# Always-available info button -> "how the set bonus works" help tooltip.
		infoSize = 32
		infoX = self.GetWidth() - infoSize - 12
		infoY = 30
		if localeinfo.IsARABIC():
			infoX = 12
		self.setBonusInfoButton = ui.Window()
		self.setBonusInfoButton.SetParent(self)
		self.setBonusInfoButton.SetPosition(int(infoX), int(infoY))
		self.setBonusInfoButton.SetSize(infoSize, infoSize)
		self.setBonusInfoButton.SetOverInEvent(ui.__mem_func__(self.__OnSetBonusInfoOverIn))
		self.setBonusInfoButton.SetOverOutEvent(ui.__mem_func__(self.__OnSetBonusInfoOverOut))
		self.setBonusInfoButton.Show()

		self.setBonusInfoImage = ui.ExpandedImageBox()
		self.setBonusInfoImage.SetParent(self.setBonusInfoButton)
		self.setBonusInfoImage.SetPosition(0, 0)
		try:
			self.setBonusInfoImage.LoadImage(self.DSS_ART_PATH + "info_normal.tga")
		except:
			pass
		self.setBonusInfoImage.AddFlag("not_pick")
		self.setBonusInfoImage.Show()

		self.__UpdateSetBonusView()

	def __OnSetBonusOverIn(self):
		self.__RefreshSetBonusToolTipIfDirty()
		if self.setBonusToolTip is not None:
			self.__PositionSetBonusToolTip()
			self.setBonusToolTip.SetTop()
			self.setBonusToolTip.Show()

	def __OnSetBonusOverOut(self):
		if self.setBonusToolTip is not None:
			self.setBonusToolTip.Hide()

	def __OnSetBonusInfoOverIn(self):
		if self.setBonusInfoImage is not None:
			try:
				self.setBonusInfoImage.LoadImage(self.DSS_ART_PATH + "info_hover.tga")
			except:
				pass
		self.__BuildSetBonusHelpToolTip()
		if self.setBonusHelpToolTip is not None:
			self.__PositionSetBonusHelpToolTip()
			self.setBonusHelpToolTip.SetTop()
			self.setBonusHelpToolTip.Show()

	def __OnSetBonusInfoOverOut(self):
		if self.setBonusInfoImage is not None:
			try:
				self.setBonusInfoImage.LoadImage(self.DSS_ART_PATH + "info_normal.tga")
			except:
				pass
		if self.setBonusHelpToolTip is not None:
			self.setBonusHelpToolTip.Hide()

	def __AddHelpTitle(self, board, boardWidth, yPos, text, color):
		line = ui.TextLine()
		line.SetParent(board)
		line.SetOutline()
		line.SetPackedFontColor(color)
		line.SetText(text)
		line.SetPosition(int(boardWidth) / 2, int(yPos))
		line.SetHorizontalAlignCenter()
		line.AddFlag("not_pick")
		line.Show()
		self.setBonusHelpWidgets.append(line)

	def __AddHelpRow(self, board, boardWidth, yPos, text, color):
		# check-glyph icon + label per line (mirrors the casual-buff explanation rows).
		iconW = 16
		pad = 12
		textX = pad + iconW + 6

		icon = ui.ImageBox()
		icon.SetParent(board)
		icon.AddFlag("not_pick")
		try:
			icon.LoadImage(self.SET_BONUS_HELP_CHECK)
		except:
			pass

		line = ui.TextLine()
		line.SetParent(board)
		line.SetOutline()
		line.SetPackedFontColor(color)
		line.SetText(text)
		line.SetHorizontalAlignLeft()
		line.AddFlag("not_pick")

		if localeinfo.IsARABIC():
			icon.SetPosition(int(boardWidth) - pad - iconW, int(yPos))
			line.SetPosition(int(boardWidth) - textX, int(yPos) + 1)
		else:
			icon.SetPosition(pad, int(yPos))
			line.SetPosition(textX, int(yPos) + 1)

		icon.Show()
		line.Show()
		self.setBonusHelpWidgets.append(icon)
		self.setBonusHelpWidgets.append(line)

	def __BuildSetBonusHelpToolTip(self):
		if self.setBonusHelpToolTip is not None:
			return
		board = ui.ThinBoard("UI", 1)
		board.SetParent(self)
		board.AddFlag("not_pick")
		board.Hide()
		self.setBonusHelpToolTip = board

		width = 330
		rowHeight = 19
		yPos = 12

		title = getattr(localeinfo, "DRAGONSOUL_SET_HELP_TITLE", "Dragon Soul Set Bonus")
		self.__AddHelpTitle(board, width, yPos, title, 0xffffd700)
		yPos += rowHeight + 5

		for key, default in self.SET_BONUS_HELP_KEYS:
			text = getattr(localeinfo, key, default)
			self.__AddHelpRow(board, width, yPos, text, 0xffe4e4e4)
			yPos += rowHeight

		yPos += 10
		board.SetSize(int(width), int(yPos))

	def __PositionSetBonusHelpToolTip(self):
		boardWidth = self.GetWidth()
		if localeinfo.IsARABIC():
			x = -self.setBonusHelpToolTip.GetWidth() - 6
		else:
			x = boardWidth + 6
		self.setBonusHelpToolTip.SetPosition(int(x), 20)

	def __GetSetBonusStateKey(self):
		return (self.dsSetPoints, self.dsSetTier, self.dsSetNextThreshold, tuple(self.dsSetApplys))

	def __RefreshSetBonusToolTipIfDirty(self):
		stateKey = self.__GetSetBonusStateKey()
		if self.setBonusToolTip is not None and self.setBonusLastRenderedState == stateKey:
			return
		self.__RebuildSetBonusToolTip(stateKey)

	def __ClearSetBonusToolTipContent(self):
		for widget in self.setBonusToolTipWidgets:
			try:
				widget.Hide()
			except Exception:
				pass
		self.setBonusToolTipWidgets = []

	def __AddSetBonusToolTipLine(self, boardWidth, yPos, text, color):
		line = ui.TextLine()
		line.SetParent(self.setBonusToolTip)
		line.SetOutline()
		line.SetPackedFontColor(color)
		line.SetText(text)
		if localeinfo.IsARABIC():
			line.SetPosition(int(boardWidth) - 8, int(yPos))
			line.SetHorizontalAlignLeft()
		else:
			line.SetPosition(8, int(yPos))
		line.AddFlag("not_pick")
		line.Show()
		self.setBonusToolTipWidgets.append(line)
		return line

	def __RebuildSetBonusToolTip(self, stateKey):
		if self.setBonusToolTip is None:
			self.setBonusToolTip = ui.ThinBoard("UI", 1)
			self.setBonusToolTip.SetParent(self)
			self.setBonusToolTip.AddFlag("not_pick")
			self.setBonusToolTip.Hide()

		self.__ClearSetBonusToolTipContent()

		toolTipWidth = 190
		lineHeight = 16
		yPos = 8

		normalColor = 0xffe4e4e4
		titleColor = 0xffffd700
		disabledColor = 0xff9a9a9a

		self.__AddSetBonusToolTipLine(toolTipWidth, yPos, localeinfo.DRAGONSOUL_SET_TITLE, titleColor)
		yPos += lineHeight

		if self.dsSetTier < 0:
			self.__AddSetBonusToolTipLine(toolTipWidth, yPos, localeinfo.DRAGONSOUL_SET_NONE, disabledColor)
			yPos += lineHeight
		else:
			if 0 <= self.dsSetTier < len(self.SET_BONUS_ROMAN):
				tierLabel = self.SET_BONUS_ROMAN[self.dsSetTier]
			else:
				tierLabel = str(self.dsSetTier + 1)
			tierText = localeinfo.DRAGONSOUL_SET_TIER_NAME % (self.dsSetTier + 1,)
			self.__AddSetBonusToolTipLine(toolTipWidth, yPos, tierText + " (" + tierLabel + ")", normalColor)
			yPos += lineHeight

		if self.dsSetNextThreshold < 0:
			pointsText = "%d %s" % (self.dsSetPoints, localeinfo.DRAGONSOUL_SET_MAX)
		else:
			pointsText = "%d / %d" % (self.dsSetPoints, self.dsSetNextThreshold)
		self.__AddSetBonusToolTipLine(toolTipWidth, yPos, pointsText, normalColor)
		yPos += lineHeight

		if self.dsSetTier >= 0 and self.tooltipItem is not None:
			for (applyType, applyValue) in self.dsSetApplys:
				affectString = self.tooltipItem.GetAffectString(applyType, applyValue)
				if affectString:
					affectColor = self.tooltipItem.GetChangeTextLineColor(applyValue)
					self.__AddSetBonusToolTipLine(toolTipWidth, yPos, affectString, affectColor)
					yPos += lineHeight

		if self.dsSetNextThreshold >= 0:
			nextText = localeinfo.DRAGONSOUL_SET_NEXT % (self.dsSetNextThreshold,)
			self.__AddSetBonusToolTipLine(toolTipWidth, yPos, nextText, disabledColor)
			yPos += lineHeight

		yPos += 6
		self.setBonusToolTip.SetSize(int(toolTipWidth), int(yPos))
		self.setBonusLastRenderedState = stateKey

	def __PositionSetBonusToolTip(self):
		boardWidth = self.GetWidth()
		if localeinfo.IsARABIC():
			x = -self.setBonusToolTip.GetWidth() - 6
		else:
			x = boardWidth + 6
		y = 90
		self.setBonusToolTip.SetPosition(int(x), int(y))

	def __UpdateSetBonusView(self):
		active = self.dsSetTier >= 0

		if self.setBonusGlow is not None:
			if active:
				self.setBonusGlow.Show()
			else:
				self.setBonusGlow.Hide()
				if self.setBonusToolTip is not None:
					self.setBonusToolTip.Hide()

		if active and self.setBonusToolTip is not None and self.setBonusToolTip.IsShow():
			self.__OnSetBonusOverIn()

	def ActivateDragonSoulByExtern(self, deck):
		self.ActivateEquipSlotWindow(deck)
		self.isActivated = True
		self.activateButton.Down()
		self.deckPageIndex = deck
		self.deckTab[deck].Down()
		self.deckTab[(deck+1)%2].SetUp()
		self.RefreshEquipSlotWindow()

		if app.ENABLE_DSS_ACTIVE_EFFECT_BUTTON:
			if self.interface:
				self.interface.UseDSSButtonEffect(self.isActivated)

	def DeactivateDragonSoul(self):
		self.DeactivateEquipSlotWindow()
		self.isActivated = False
		self.activateButton.SetUp()

		if app.ENABLE_DSS_ACTIVE_EFFECT_BUTTON:
			if self.interface:
				self.interface.UseDSSButtonEffect(self.isActivated)

	if app.__ENABLE_RANGE_ALCHEMY__:
		def __OpenShopWindow(self):
			net.SendChatPacket("/open_range_npc " + str(51))
			
	if app.__ENABLE_REFINE_ALCHEMY__:
		def __OpenRefineAlchemyWindow(self):
			net.SendChatPacket("/open_refine_window_alchemy ")

	def ActivateButtonClick(self):
		self.isActivated = self.isActivated ^ True
		if self.isActivated:
			if self.__CanActivateDeck():
				net.SendChatPacket("/dragon_soul activate " + str(self.deckPageIndex))
			else:
				self.isActivated = False
				self.activateButton.SetUp()
		else:
			net.SendChatPacket("/dragon_soul deactivate")

	def __CanActivateDeck(self):
		canActiveNum = 0
		for i in xrange(7):
			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(player.INVENTORY, player.DRAGON_SOUL_EQUIPMENT_SLOT_START + i)
			itemVnum = player.GetItemIndex(slotNumber)

			if itemVnum != 0:
				item.SelectItem(itemVnum)
				isNoLimit = True
				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)

					if item.LIMIT_TIMER_BASED_ON_WEAR == limitType:
						isNoLimit = False

						remain_time = player.GetItemMetinSocket(player.INVENTORY, slotNumber, 0)

						if 0 != remain_time:
							canActiveNum += 1
							break
				if isNoLimit:
					canActiveNum += 1

		return canActiveNum > 0

	def __HighlightSlot_ClearCurrentPage(self):
		if self.wndItem is None:
			return

		for i in xrange(self.wndItem.GetSlotCount()):
			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(player.DRAGON_SOUL_INVENTORY, i)
			if slotNumber in self.listHighlightedSlot:
				self.wndItem.DeactivateSlot(i)
				self.listHighlightedSlot.remove(slotNumber)

	def __HighlightSlot_RefreshCurrentPage(self):
		if self.wndItem is None:
			return

		for i in xrange(self.wndItem.GetSlotCount()):
			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(player.DRAGON_SOUL_INVENTORY, i)
			if slotNumber in self.listHighlightedSlot:
				self.wndItem.ActivateSlot(i)

	def HighlightSlot(self, slot):
		if not slot in self.listHighlightedSlot:
			self.listHighlightedSlot.append(slot)

	def SetDragonSoulRefineWindow(self, DragonSoulRefine):
		if DragonSoulRefine:
			self.wndDragonSoulRefine = proxy(DragonSoulRefine)

	if app.QUICK_SELL_SYSTEM:
		def RefreshQuickSellMarks(self):
			if self.wndItem is None:
				return

			for k in xrange(player.DRAGON_SOUL_PAGE_SIZE):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(player.DRAGON_SOUL_INVENTORY, k)
				# Unlike the inventory windows this one has no other cover-image user and no
				# reset pass, so it clears its own marks.
				if uiquicksell.IsSelected(player.DRAGON_SOUL_INVENTORY, slotNumber):
					self.wndItem.SetSlotCoverImage(k, uiquicksell.SELECTED_COVER_IMAGE)
				else:
					self.wndItem.EnableSlotCoverImage(k, False)

	def BindInterfaceClass(self, interface):
		if interface:
			self.interface = proxy(interface)

	def IsDlgQuestionShow(self):
		if self.dlgQuestion.IsShow():
			return True
		else:
			return False

	def CancelDlgQuestion(self):
		self.__Cancel()

	def SetUseItemMode(self, bUse):
		if self.wndItem is None:
			return

		self.wndItem.SetUseMode(bUse)

#class DragonSoulRefineException(Exception):
	#pass

class DragonSoulRefineWindow(ui.ScriptWindow):
	REFINE_TYPE_GRADE, REFINE_TYPE_STEP, REFINE_TYPE_STRENGTH = xrange(3)
	DS_SUB_HEADER_DIC = {
		REFINE_TYPE_GRADE : player.DS_SUB_HEADER_DO_UPGRADE,
		REFINE_TYPE_STEP : player.DS_SUB_HEADER_DO_IMPROVEMENT,
		REFINE_TYPE_STRENGTH : player.DS_SUB_HEADER_DO_REFINE
	}

	REFINE_STONE_SLOT, DRAGON_SOUL_SLOT = xrange(2)
	INVALID_DRAGON_SOUL_INFO = -1
	if app.ENABLE_DS_CHANGE_ATTR:
		DS_REFINE_TYPE_NORMAL, DS_REFINE_TYPE_CHANGEATTR, DS_REFINE_TYPE_MAX = xrange(3)

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.wndInventory = None
		self.wndDragonSoul = None

		if app.ENABLE_DS_CHANGE_ATTR:
			self.refinetype = DragonSoulRefineWindow.DS_REFINE_TYPE_NORMAL
		
		if app.ENABLE_DS_REFINE_ALL:
			self.doRefineAllButton = None

		self.tooltipItem = None
		self.sellingSlotNumber = -1
		self.isLoaded = 0
		self.refineChoiceButtonDict = None
		self.doRefineButton = None
		self.wndMoney = None
		self.SetWindowName("DragonSoulRefineWindow")
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	if app.ENABLE_DS_CHANGE_ATTR:
		def ReloadType(self, refinetype):
			textNames = ["GradeSlotTitle", "StepSlotTitle", "RefineSlotTitle"]
			if refinetype == self.DS_REFINE_TYPE_CHANGEATTR:
				for idx, btn in self.refineChoiceButtonDict.items():
					if idx == self.REFINE_TYPE_STRENGTH:
						self.GetChild(textNames[idx]).SetText(uiscriptlocale.CHANGE_ATTR_SELECT)
						btn.Down()
					else:
						btn.SetUp()
						btn.Disable()
						self.GetChild(textNames[idx]).SetText("")
				
				self.GetChild("DoRefineButtonTitle").SetText(uiscriptlocale.DO_CHANGE_ATTR)
				self.GetChild("TitleName").SetText(uiscriptlocale.DRAGONSOUL_CHANGE_ATTR_WINDOW_TITLE)
				self.currentRefineType = DragonSoulRefineWindow.REFINE_TYPE_GRADE
				if app.ENABLE_DS_REFINE_ALL:
					self.doRefineAllButton.Hide()
			else:
				names = [uiscriptlocale.GRADE_SELECT,
						 uiscriptlocale.STEP_SELECT,
						 uiscriptlocale.STRENGTH_SELECT
				]
				
				for idx, btn in self.refineChoiceButtonDict.items():
					btn.Enable()
					if idx == 0:
						btn.Down()
					else:
						btn.SetUp()
					
					try:
						self.GetChild(textNames[idx]).SetText(names[idx])
					except Exception as e:
						import dbg
						dbg.TraceError(str(e))
						return 0
				
				self.GetChild("DoRefineButtonTitle").SetText(uiscriptlocale.DO_REFINE)
				self.GetChild("TitleName").SetText(uiscriptlocale.DRAGONSOUL_REFINE_WINDOW_TITLE)
				self.currentRefineType = self.REFINE_TYPE_GRADE
				if app.ENABLE_DS_REFINE_ALL:
					self.doRefineAllButton.Show()
			
			self.wndMoney.SetText(localeinfo.NumberToMoneyString(0))
			self.Refresh()
			self.refinetype = refinetype
			return 1

	def Open(self, refinetype):
		if app.ENABLE_DS_CHANGE_ATTR:
			try:
				refinetype = int(refinetype)
				if refinetype >= DragonSoulRefineWindow.DS_REFINE_TYPE_MAX:
					import dbg
					dbg.TraceError("Invalid refine type (%d)" % (refinetype))
					return
			except Exception as e:
				import dbg
				dbg.TraceError(str(e))
				return
		
		self.__LoadWindow()
		if app.ENABLE_DS_CHANGE_ATTR:
			if self.ReloadType(refinetype) == 1:
				ui.ScriptWindow.Show(self)
		else:
			self.currentRefineType = self.REFINE_TYPE_GRADE
			self.wndMoney.SetText(localeinfo.NumberToMoneyString(0))
			self.refineChoiceButtonDict[self.REFINE_TYPE_GRADE].Down()
			self.refineChoiceButtonDict[self.REFINE_TYPE_STEP].SetUp()
			self.refineChoiceButtonDict[self.REFINE_TYPE_STRENGTH].SetUp()
			self.Refresh()
			ui.ScriptWindow.Show(self)

	if app.ENABLE_DS_CHANGE_ATTR:
		def Show(self):
			self.Open(self.refinetype)

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return
		self.isLoaded = 1
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "dragonsoulrefinewindow.py")

		except:
			import exception
			exception.Abort("dragonsoulrefinewindow.LoadWindow.LoadObject")
		try:
			if app.ENABLE_DS_REFINE_ALL:
				self.doRefineAllButton = self.GetChild("DoRefineAllButton")
			
			if localeinfo.IsARABIC():
				self.board = self.GetChild("DragonSoulRefineWindowBaseImage")
				self.board.SetScale(-1.0, 1.0)
				self.board.SetRenderingRect(-1.0, 0.0, 1.0, 0.0)

			wndRefineSlot = self.GetChild("RefineSlot")
			wndResultSlot = self.GetChild("ResultSlot")
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
			self.refineChoiceButtonDict = {
				self.REFINE_TYPE_GRADE	: self.GetChild("GradeButton"),
				self.REFINE_TYPE_STEP: self.GetChild("StepButton"),
				self.REFINE_TYPE_STRENGTH	: self.GetChild("StrengthButton"),
			}
			self.doRefineButton = self.GetChild("DoRefineButton")
			self.wndMoney = self.GetChild("Money_Slot")

		except:
			import exception
			exception.Abort("DragonSoulRefineWindow.LoadWindow.BindObject")

		## Item Slots
		wndRefineSlot.SetOverInItemEvent(ui.__mem_func__(self.__OverInRefineItem))
		wndRefineSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OverOutItem))
		wndRefineSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.__SelectRefineEmptySlot))
		wndRefineSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.__SelectRefineItemSlot))
		wndRefineSlot.SetUseSlotEvent(ui.__mem_func__(self.__SelectRefineItemSlot))
		wndRefineSlot.SetUnselectItemSlotEvent(ui.__mem_func__(self.__SelectRefineItemSlot))

		wndResultSlot.SetOverInItemEvent(ui.__mem_func__(self.__OverInResultItem))
		wndResultSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OverOutItem))
		self.wndRefineSlot = wndRefineSlot
		self.wndResultSlot = wndResultSlot

		## Button
		if app.ENABLE_DS_REFINE_ALL:
			self.doRefineAllButton.SetEvent(ui.__mem_func__(self.__PressDoRefineAllButton))
		
		self.refineChoiceButtonDict[self.REFINE_TYPE_GRADE].SetToggleDownEvent(ui.__mem_func__(self.__ToggleDownGradeButton))
		self.refineChoiceButtonDict[self.REFINE_TYPE_STEP].SetToggleDownEvent(ui.__mem_func__(self.__ToggleDownStepButton))
		self.refineChoiceButtonDict[self.REFINE_TYPE_STRENGTH].SetToggleDownEvent(ui.__mem_func__(self.__ToggleDownStrengthButton))
		self.refineChoiceButtonDict[self.REFINE_TYPE_GRADE].SetToggleUpEvent(ui.__mem_func__(self.__ToggleUpButton), self.REFINE_TYPE_GRADE)
		self.refineChoiceButtonDict[self.REFINE_TYPE_STEP].SetToggleUpEvent(ui.__mem_func__(self.__ToggleUpButton), self.REFINE_TYPE_STEP)
		self.refineChoiceButtonDict[self.REFINE_TYPE_STRENGTH].SetToggleUpEvent(ui.__mem_func__(self.__ToggleUpButton), self.REFINE_TYPE_STRENGTH)
		self.doRefineButton.SetEvent(ui.__mem_func__(self.__PressDoRefineButton))

		## Dialog
		self.wndPopupDialog = uicommon.PopupDialog()

		self.currentRefineType = self.REFINE_TYPE_GRADE
		self.refineItemInfo = {}
		self.resultItemInfo = {}
		self.currentRecipe = {}

		self.wndMoney.SetText(localeinfo.NumberToMoneyString(0))
		self.refineChoiceButtonDict[self.REFINE_TYPE_GRADE].Down()

		self.__Initialize()

	def Destroy(self):
		self.wndInventory = None
		self.wndDragonSoul = None

		self.ClearDictionary()
		self.tooltipItem = None
		self.wndRefineSlot = None
		self.wndResultSlot = None
		self.refineChoiceButtonDict = None
		self.doRefineButton = None
		self.wndMoney = None
		if app.ENABLE_DS_REFINE_ALL:
			self.doRefineAllButton = None

		self.BeansInvenType = 0
		self.BeansInvenPos = 0
		self.soulInvenPos = 0

	def Close(self):
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

		self.__FlushRefineItemSlot()
		player.SendDragonSoulRefine(player.DRAGON_SOUL_REFINE_CLOSE)
		self.Hide()

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def __Initialize(self):
		self.currentRecipe = {}
		self.refineItemInfo = {}
		self.resultItemInfo = {}

		if self.REFINE_TYPE_STRENGTH == self.currentRefineType:
			self.refineSlotLockStartIndex = 2
		else:
			self.refineSlotLockStartIndex = 1

		for i in xrange(self.refineSlotLockStartIndex):
			self.wndRefineSlot.HideSlotBaseImage(i)

		self.wndMoney.SetText(localeinfo.NumberToMoneyString(0))

	def __FlushRefineItemSlot(self):
		## Item slot settings
		# ???? ????? ?????? ???? ???
		#for invenType, invenPos, itemCount in self.refineItemInfo.values():
			#remainCount = player.GetItemCount(invenType, invenPos)
			#player.SetItemCount(invenType, invenPos, remainCount + itemCount)

		self.wndDragonSoul.refineSlots = []
		self.wndDragonSoul.RefreshBagSlotWindow()

		self.__Initialize()

	def __ToggleUpButton(self, idx):
		#if self.REFINE_TYPE_GRADE == self.currentRefineType:
		self.refineChoiceButtonDict[idx].Down()

	def __ToggleDownGradeButton(self):
		if self.REFINE_TYPE_GRADE == self.currentRefineType:
			return
		
		if app.ENABLE_DS_REFINE_ALL:
			self.doRefineAllButton.Show()
		
		self.refineChoiceButtonDict[self.currentRefineType].SetUp()
		self.currentRefineType = self.REFINE_TYPE_GRADE
		self.__FlushRefineItemSlot()
		self.Refresh()

	def __ToggleDownStepButton(self):
		if self.REFINE_TYPE_STEP == self.currentRefineType:
			return
		
		if app.ENABLE_DS_REFINE_ALL:
			self.doRefineAllButton.Hide()
		
		self.refineChoiceButtonDict[self.currentRefineType].SetUp()
		self.currentRefineType = self.REFINE_TYPE_STEP
		self.__FlushRefineItemSlot()
		self.Refresh()

	def __ToggleDownStrengthButton(self):
		if self.REFINE_TYPE_STRENGTH == self.currentRefineType:
			return
		
		if app.ENABLE_DS_REFINE_ALL:
			self.doRefineAllButton.Hide()
		
		self.refineChoiceButtonDict[self.currentRefineType].SetUp()
		self.currentRefineType = self.REFINE_TYPE_STRENGTH
		self.__FlushRefineItemSlot()
		self.Refresh()

	def __PopUp(self, message):
		self.wndPopupDialog.SetText(message)
		self.wndPopupDialog.Open()

	def __SetItem(self, inven, dstSlotIndex, itemCount):
		invenType, invenPos = inven

		if dstSlotIndex >= self.refineSlotLockStartIndex:
			return False

		itemVnum = player.GetItemIndex(invenType, invenPos)
		maxCount = player.GetItemCount(invenType, invenPos)

		if itemCount > maxCount:
			raise Exception, ("Invalid attachedItemCount(%d). (base pos (%d, %d), base itemCount(%d))" % (itemCount, invenType, invenPos, maxCount))
			#return False

		if DragonSoulRefineWindow.REFINE_TYPE_STRENGTH == self.currentRefineType:
			if self.__IsDragonSoul(itemVnum):
				dstSlotIndex = 1
			else:
				dstSlotIndex = 0

		if dstSlotIndex in self.refineItemInfo:
			return False

		if app.ENABLE_DS_CHANGE_ATTR and self.refinetype == self.DS_REFINE_TYPE_CHANGEATTR:
			if dstSlotIndex == 0:
				if not ((itemVnum >= 114000 and itemVnum <= 115460) or\
						(itemVnum >= 124000 and itemVnum <= 125460) or\
						(itemVnum >= 134000 and itemVnum <= 135460) or\
						(itemVnum >= 144000 and itemVnum <= 145460) or\
						(itemVnum >= 154000 and itemVnum <= 155460) or\
						(itemVnum >= 164000 and itemVnum <= 165460) or\
						(itemVnum >= 174000 and itemVnum <= 175460)):
					return
				else:
					self.refineSlotLockStartIndex = 2
					self.wndMoney.SetText(localeinfo.NumberToMoneyString(500000))
			elif dstSlotIndex == 1:
				if itemVnum != 100700 and itemVnum != 100701:
					return
		
		if app.ENABLE_DS_CHANGE_ATTR and self.refinetype == self.DS_REFINE_TYPE_CHANGEATTR:
			pass
		else:
			if False == self.__CheckCanRefine(itemVnum, invenType, invenPos):
				return False
		
		# ????? ???? ?????? ??????? ???? ????? ?????? ???? ????
		#player.SetItemCount(invenType, invenPos, maxCount - itemCount)
		self.refineItemInfo[dstSlotIndex] = (invenType, invenPos, itemCount)
		self.Refresh()
		return True

	def __CheckCanRefine(self, vnum, invenType, invenPos):
		if self.REFINE_TYPE_GRADE == self.currentRefineType:
			return self.__CanRefineGrade(vnum, invenType, invenPos)

		elif self.REFINE_TYPE_STEP == self.currentRefineType:
			return self.__CanRefineStep(vnum, invenType, invenPos)
				
		elif self.REFINE_TYPE_STRENGTH == self.currentRefineType:
			return self.__CanRefineStrength(vnum, invenType, invenPos)
				
		else:
			return False
				
		return True

	def __CanRefineGrade(self, vnum, invenType, invenPos):
		ds_info = self.__GetDragonSoulTypeInfo(vnum)

		if DragonSoulRefineWindow.INVALID_DRAGON_SOUL_INFO == ds_info:
			self.__PopUp(localeinfo.DRAGON_SOUL_IS_NOT_DRAGON_SOUL)
			return False

		if self.currentRecipe:
			ds_type, grade, step, strength = ds_info
			cur_refine_ds_type, cur_refine_grade, cur_refine_step, cur_refine_strength = self.currentRecipe["ds_info"]
			if not (cur_refine_ds_type == ds_type and cur_refine_grade == grade):
				self.__PopUp(localeinfo.DRAGON_SOUL_INVALID_DRAGON_SOUL)
				return False
		else:
			self.currentRecipe = self.__GetRefineGradeRecipe(vnum)

			if self.currentRecipe:
				self.refineSlotLockStartIndex = self.currentRecipe["need_count"]
				self.wndMoney.SetText(localeinfo.NumberToMoneyString(self.currentRecipe["fee"]))
				return True
			else:
				self.__PopUp(localeinfo.DRAGON_SOUL_CANNOT_REFINE)
				return False

	def __CanRefineStep (self, vnum, invenType, invenPos):
		ds_info = self.__GetDragonSoulTypeInfo(vnum)

		if DragonSoulRefineWindow.INVALID_DRAGON_SOUL_INFO == ds_info:
			self.__PopUp(localeinfo.DRAGON_SOUL_IS_NOT_DRAGON_SOUL)
			return False

		if self.currentRecipe:
			ds_type, grade, step, strength = ds_info
			cur_refine_ds_type, cur_refine_grade, cur_refine_step, cur_refine_strength = self.currentRecipe["ds_info"]
			if not (cur_refine_ds_type == ds_type and cur_refine_grade == grade and cur_refine_step == step):
				self.__PopUp(localeinfo.DRAGON_SOUL_INVALID_DRAGON_SOUL)
				return False
		else:
			self.currentRecipe = self.__GetRefineStepRecipe(vnum)

			if self.currentRecipe:
				self.refineSlotLockStartIndex = self.currentRecipe["need_count"]
				self.wndMoney.SetText(localeinfo.NumberToMoneyString(self.currentRecipe["fee"]))
				return True
			else:
				self.__PopUp(localeinfo.DRAGON_SOUL_CANNOT_REFINE)
				return False

	def __CanRefineStrength (self, vnum, invenType, invenPos):
		# ??????? ???, ?? ??? strength ????? ?? ?? ?????? u??????.
		if self.__IsDragonSoul(vnum):
			ds_type, grade, step, strength = self.__GetDragonSoulTypeInfo(vnum)
			if strength >= dragon_soul_refine_settings.dragon_soul_refine_info[ds_type]["strength_max_table"][grade][step]:
				self.__PopUp(localeinfo.DRAGON_SOUL_CANNOT_REFINE_MORE)
				return False
			else:
				return True
		else:
			if self.currentRecipe:
				self.__PopUp(localeinfo.DRAGON_SOUL_IS_NOT_DRAGON_SOUL)
				return False
			else:
				refineRecipe = self.__GetRefineStrengthInfo(vnum)
				if refineRecipe:
					self.currentRecipe = refineRecipe
					self.wndMoney.SetText(localeinfo.NumberToMoneyString(self.currentRecipe["fee"]))
					return True
				else:
					self.__PopUp(localeinfo.DRAGON_SOUL_NOT_DRAGON_SOUL_REFINE_STONE)
					return False

	def __GetRefineGradeRecipe (self, vnum):
		ds_type, grade, step, strength = self.__GetDragonSoulTypeInfo(vnum)
		try:
			return {
				"ds_info"		: (ds_type, grade, step, strength),
				"need_count"	: dragon_soul_refine_settings.dragon_soul_refine_info[ds_type]["grade_need_count"][grade],
				"fee"			: dragon_soul_refine_settings.dragon_soul_refine_info[ds_type]["grade_fee"][grade]
					}
		except Exception as e:
			import dbg
			dbg.TraceError("DragonSoul recipe lookup failed: %s" % str(e))
			return None

	def __GetRefineStepRecipe (self, vnum):
		ds_type, grade, step, strength = self.__GetDragonSoulTypeInfo(vnum)
		try:
			return {
				"ds_info"		: (ds_type, grade, step, strength),
				"need_count"	: dragon_soul_refine_settings.dragon_soul_refine_info[ds_type]["step_need_count"][step],
				"fee"			: dragon_soul_refine_settings.dragon_soul_refine_info[ds_type]["step_fee"][step]
					}
		except Exception as e:
			import dbg
			dbg.TraceError("DragonSoul recipe lookup failed: %s" % str(e))
			return None

	def __GetRefineStrengthInfo (self, itemVnum):
		try:
			item.SelectItem(itemVnum)
			if not (item.ITEM_TYPE_MATERIAL == item.GetItemType() \
					and (item.MATERIAL_DS_REFINE_NORMAL <= item.GetItemSubType() and item.GetItemSubType() <= item.MATERIAL_DS_REFINE_HOLLY)):
				return None

			return { "fee" : dragon_soul_refine_settings.strength_fee[item.GetItemSubType()] }
		except:
			return None

	def __IsDragonSoul(self, vnum):
		item.SelectItem(vnum)
		return item.GetItemType() == item.ITEM_TYPE_DS

	def __GetDragonSoulTypeInfo(self, vnum):
		if not self.__IsDragonSoul(vnum):
			return DragonSoulRefineWindow.INVALID_DRAGON_SOUL_INFO 
		ds_type = vnum / 10000
		grade = vnum % 10000 /1000
		step = vnum % 1000 / 100
		strength = vnum % 100 / 10

		return (ds_type, grade, step, strength)

	def __MakeDragonSoulVnum(self, ds_type, grade, step, strength):
		return ds_type * 10000 + grade * 1000 + step * 100 + strength * 10

	def __SelectRefineEmptySlot(self, selectedSlotPos):
		try:
			if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
				return

			if selectedSlotPos >= self.refineSlotLockStartIndex:
				return

			if mousemodule.mouseController.isAttached():
				attachedSlotType = mousemodule.mouseController.GetAttachedType()
				attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
				attachedItemCount = mousemodule.mouseController.GetAttachedItemCount()
				attachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()
				mousemodule.mouseController.DeattachObject()

				if uiprivateshopbuilder.IsBuildingPrivateShop():
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.MOVE_ITEM_FAILURE_PRIVATE_SHOP)
					return

				attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)

				if player.INVENTORY == attachedInvenType and player.IsEquipmentSlot(attachedSlotPos):
					return

				# if player.INVENTORY != attachedInvenType and player.DRAGON_SOUL_INVENTORY != attachedInvenType:
					# return

				if True == self.__SetItem((attachedInvenType, attachedSlotPos), selectedSlotPos, attachedItemCount):
					self.Refresh()

		except Exception, e:
			import dbg
			dbg.TraceError("Exception : __SelectRefineEmptySlot, %s" % e)

	def __SelectRefineItemSlot(self, selectedSlotPos):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		try:
			if not selectedSlotPos in self.refineItemInfo:
				if mousemodule.mouseController.isAttached():
					attachedSlotType = mousemodule.mouseController.GetAttachedType()
					attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
					attachedItemCount = mousemodule.mouseController.GetAttachedItemCount()
					attachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()
					mousemodule.mouseController.DeattachObject()

					if uiprivateshopbuilder.IsBuildingPrivateShop():
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.MOVE_ITEM_FAILURE_PRIVATE_SHOP)
						return

					attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)

					if player.INVENTORY == attachedInvenType and player.IsEquipmentSlot(attachedSlotPos):
						return

					# if player.INVENTORY != attachedInvenType and player.DRAGON_SOUL_INVENTORY != attachedInvenType:
						# return

					self.AutoSetItem((attachedInvenType, attachedSlotPos), 1)
				return
			elif mousemodule.mouseController.isAttached():
				return

			attachedInvenType, attachedSlotPos, attachedItemCount = self.refineItemInfo[selectedSlotPos]
			selectedItemVnum = player.GetItemIndex(attachedInvenType, attachedSlotPos)
			
			invenType, invenPos, itemCount = self.refineItemInfo[selectedSlotPos]
			#remainCount = player.GetItemCount(invenType, invenPos)
			#player.SetItemCount(invenType, invenPos, remainCount + itemCount)
			del self.refineItemInfo[selectedSlotPos]
			if invenType == player.DRAGON_SOUL_INVENTORY:
				self.wndDragonSoul.refineSlots.remove(invenPos)
				self.wndDragonSoul.RefreshBagSlotWindow()

			if not self.refineItemInfo:
				self.__Initialize()
			else:
				item.SelectItem(selectedItemVnum)
				if (item.ITEM_TYPE_MATERIAL == item.GetItemType() \
					and (item.MATERIAL_DS_REFINE_NORMAL <= item.GetItemSubType() and item.GetItemSubType() <= item.MATERIAL_DS_REFINE_HOLLY)):
					self.currentRecipe = {}
					self.wndMoney.SetText(localeinfo.NumberToMoneyString(0))
				else:
					pass

		except Exception, e:
			import dbg
			dbg.TraceError("Exception : __SelectRefineItemSlot, %s" % e)

		self.Refresh()

	def __OverInRefineItem(self, slotIndex):
		if self.refineItemInfo.has_key(slotIndex):
			inven_type, inven_pos, item_count = self.refineItemInfo[slotIndex]
			srcVnum = player.GetItemIndex(inven_type, inven_pos)
			if srcVnum:
				self.tooltipItem.SetInventoryItem(inven_pos, inven_type)
			else:
				if self.tooltipItem:
					self.tooltipItem.HideToolTip()
		else:
			if self.tooltipItem:
				self.tooltipItem.HideToolTip()

	def __OverInResultItem(self, slotIndex):
		if self.resultItemInfo.has_key(slotIndex):
			inven_type, inven_pos, item_count = self.resultItemInfo[slotIndex]
			self.tooltipItem.SetInventoryItem(inven_pos, inven_type)

	def __OverOutItem(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def __InventoryLocalSlotPosToGlobalSlotPos(self, window_type, local_slot_pos):
		if player.INVENTORY == window_type:
			return self.deckPageIndex * player.DRAGON_SOUL_EQUIPMENT_FIRST_SIZE + local_slot_pos

		if app.ENABLE_DS_GRADE_MYTH:
			return (self.DSKindIndex * 6 * player.DRAGON_SOUL_PAGE_SIZE) + self.inventoryPageIndex * player.DRAGON_SOUL_PAGE_SIZE + local_slot_pos
		else:
			return (self.DSKindIndex * 5 * player.DRAGON_SOUL_PAGE_SIZE) + self.inventoryPageIndex * player.DRAGON_SOUL_PAGE_SIZE + local_slot_pos


	if app.ENABLE_DS_REFINE_ALL:
		def __PressDoRefineAllButton(self):
			player.SendDragonSoulRefineAll(self.DS_SUB_HEADER_DIC[self.currentRefineType], dragon_soul_refine_settings.ds_type_page, dragon_soul_refine_settings.ds_grade_page)

	def __PressDoRefineButton(self):
		for i in xrange(self.refineSlotLockStartIndex):
			if not i in self.refineItemInfo:
				if app.ENABLE_DS_CHANGE_ATTR and self.refinetype == self.DS_REFINE_TYPE_CHANGEATTR:
					return
				
				self.wndPopupDialog.SetText(localeinfo.DRAGON_SOUL_NOT_ENOUGH_MATERIAL)
				self.wndPopupDialog.Open()
				return
		
		#if app.ENABLE_DS_CHANGE_ATTR and self.refinetype == self.DS_REFINE_TYPE_CHANGEATTR:
		#	try:
		#		(invType, invPos, invItemCount) = self.refineItemInfo[0]
		#		srcVnum = player.GetItemIndex(invType, invPos)
		#		if srcVnum:
		#			itemName = item.GetItemName()
		#			ds_type, grade, step, strength = self.__GetDragonSoulTypeInfo(srcVnum)
		#			count = dragon_soul_refine_settings.default_change_attrcount[step]
		#			(invType2, invPos2, invItemCount2) = self.refineItemInfo[1]
		#			materialVnum = player.GetItemIndex(invType2, invPos2)
		#			if materialVnum:
		#				if invItemCount2 < count:
		#					self.wndPopupDialog.SetText(localeinfo.DRAGON_SOUL_NOT_ENOUGH_MATERIAL2 % (itemName, item.GetItemName(), count))
		#					self.wndPopupDialog.Open()
		#					return
		#	except:
		#		return
		
		if app.ENABLE_DS_CHANGE_ATTR and self.refinetype == self.DS_REFINE_TYPE_CHANGEATTR:
			player.SendDragonSoulRefine(player.DS_SUB_HEADER_DO_CHANGEATTR, self.refineItemInfo)
		else:
			player.SendDragonSoulRefine(DragonSoulRefineWindow.DS_SUB_HEADER_DIC[self.currentRefineType], self.refineItemInfo)

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Refresh(self):
		self.__RefreshRefineItemSlot()
		self.__ClearResultItemSlot()

	def __RefreshRefineItemSlot(self):
		try:
			for slotPos in xrange(self.wndRefineSlot.GetSlotCount()):
				self.wndRefineSlot.ClearSlot(slotPos)
				if slotPos < self.refineSlotLockStartIndex:
					if slotPos in self.refineItemInfo:
						invenType, invenPos, itemCount = self.refineItemInfo[slotPos]
						itemVnum = player.GetItemIndex(invenType, invenPos)
						if itemVnum:
							self.wndRefineSlot.SetItemSlot(slotPos, player.GetItemIndex(invenType, invenPos), itemCount)

							if invenType == player.DRAGON_SOUL_INVENTORY:
								self.wndDragonSoul.refineSlots.append(invenPos)
								self.wndDragonSoul.RefreshBagSlotWindow()
						else:
							del self.refineItemInfo[slotPos]

							if invenType == player.DRAGON_SOUL_INVENTORY:
								self.wndDragonSoul.refineSlots.remove(invenPos)
								self.wndDragonSoul.RefreshBagSlotWindow()

					# ?? ????? reference ???????? alpha 0.5?? ????.
					if not slotPos in self.refineItemInfo:
						try:
							reference_vnum = 0
							count = 0
							if DragonSoulRefineWindow.REFINE_TYPE_STRENGTH == self.currentRefineType:
								if DragonSoulRefineWindow.REFINE_STONE_SLOT == slotPos:
									reference_vnum = 100300
							else:
								if app.ENABLE_DS_CHANGE_ATTR and self.refinetype == self.DS_REFINE_TYPE_CHANGEATTR:
									(invType, invPos, invItemCount) = self.refineItemInfo[0]
									srcVnum = player.GetItemIndex(invType, invPos)
									if srcVnum:
										ds_type, grade, step, strength = self.__GetDragonSoulTypeInfo(srcVnum)
										reference_vnum = 100700
										count = dragon_soul_refine_settings.default_change_attrcount[step]
									else:
										reference_vnum = 0
								else:
									reference_vnum = self.__MakeDragonSoulVnum(*self.currentRecipe["ds_info"])
							
							if reference_vnum:
								item.SelectItem(reference_vnum)
								itemIcon = item.GetIconImage()
								(width, height) = item.GetItemSize()
								self.wndRefineSlot.SetSlot(slotPos, count, width, height, itemIcon, (1.0, 1.0, 1.0, 0.5))
								self.wndRefineSlot.SetSlotCount(slotPos, count)
						except:
							pass
					
					self.wndRefineSlot.HideSlotBaseImage(slotPos)
				else:
					if slotPos in self.refineItemInfo:
						#invenType, invenPos, itemCount = self.refineItemInfo[slotPos]
						#remainCount = player.GetItemCount(invenType, invenPos)
						#player.SetItemCount(invenType, invenPos, remainCount + itemCount)
						del self.refineItemInfo[slotPos]
					# refineSlotLockStartIndex ????? ?????? ???? ??????? ?????????.
					self.wndRefineSlot.ShowSlotBaseImage(slotPos)
			
			if not self.refineItemInfo:
				self.__Initialize()
			
			self.wndRefineSlot.RefreshSlot()
		except Exception, e:
			import dbg
			dbg.TraceError("Exception : __RefreshRefineItemSlot, %s" % e)

	def __GetEmptySlot(self, itemVnum = 0):
		if DragonSoulRefineWindow.REFINE_TYPE_STRENGTH == self.currentRefineType:
			if 0 == itemVnum:
				return -1

			if self.__IsDragonSoul(itemVnum):
				if not DragonSoulRefineWindow.DRAGON_SOUL_SLOT in self.refineItemInfo:
					return DragonSoulRefineWindow.DRAGON_SOUL_SLOT
			else:
				if not DragonSoulRefineWindow.REFINE_STONE_SLOT in self.refineItemInfo:
					return DragonSoulRefineWindow.REFINE_STONE_SLOT
		else:
			for slotPos in xrange(self.wndRefineSlot.GetSlotCount()):
				if not slotPos in self.refineItemInfo:
					return slotPos

		return -1

	def AutoSetItem(self, inven, itemCount):
		invenType, invenPos = inven
		itemVnum = player.GetItemIndex(invenType, invenPos)
		emptySlot = self.__GetEmptySlot(itemVnum)
		if -1 == emptySlot:
			return
		
		if app.ENABLE_DS_CHANGE_ATTR and self.refinetype == self.DS_REFINE_TYPE_CHANGEATTR:
			itemCount = player.GetItemCount(invenType, invenPos)
		
			if invenType == player.INVENTORY:
				self.BeansInvenType = invenType
				self.BeansInvenPos = invenPos
			else: self.soulInvenPos = invenPos

		self.__SetItem((invenType, invenPos), emptySlot, itemCount)

	def RefreshBeans(self):
		if self.BeansInvenType == player.INVENTORY:
			itemCount = player.GetItemCount(player.INVENTORY, self.BeansInvenPos)
			if itemCount > 0:
				self.AutoSetItem((player.DRAGON_SOUL_INVENTORY, self.soulInvenPos), 1)
				self.AutoSetItem((self.BeansInvenType, self.BeansInvenPos), itemCount)

	def __ClearResultItemSlot(self):
		self.wndResultSlot.ClearSlot(0)
		self.resultItemInfo = {}

	def RefineSucceed(self, inven_type, inven_pos):
		info = self.refineItemInfo.get(0, None)
		self.__FlushRefineItemSlot()
		self.__Initialize()
		self.Refresh()
		if app.ENABLE_DS_CHANGE_ATTR and self.refinetype == self.DS_REFINE_TYPE_CHANGEATTR:
			self.RefreshBeans()
		itemCount = player.GetItemCount(inven_type, inven_pos)
		if itemCount > 0:
			self.resultItemInfo[0] = (inven_type, inven_pos, itemCount)
			self.wndResultSlot.SetItemSlot(0, player.GetItemIndex(inven_type, inven_pos), itemCount)
			if self.currentRefineType == self.REFINE_TYPE_STRENGTH and info is not None:
				self.AutoSetItem((info[0], info[1]), 1)
				self.AutoSetItem((inven_type, inven_pos), 1)

	def	RefineFail(self, reason, inven_type, inven_pos):
		info = self.refineItemInfo.get(0, None)
		if net.DS_SUB_HEADER_REFINE_FAIL == reason:
			self.__FlushRefineItemSlot()
			self.__Initialize()
			self.Refresh()
			if app.ENABLE_DS_CHANGE_ATTR and self.refinetype == self.DS_REFINE_TYPE_CHANGEATTR:
				self.RefreshBeans()
			itemCount = player.GetItemCount(inven_type, inven_pos)
			if itemCount > 0:
				self.resultItemInfo[0] = (inven_type, inven_pos, itemCount)
				self.wndResultSlot.SetItemSlot(0, player.GetItemIndex(inven_type, inven_pos), itemCount)
				if self.currentRefineType == self.REFINE_TYPE_STRENGTH and info is not None:
					self.AutoSetItem((info[0], info[1]), 1)
					self.AutoSetItem((inven_type, inven_pos), 1)

		elif app.ENABLE_DS_CHANGE_ATTR and reason == net.DS_SUB_HEADER_REFINE_FAIL_NOT_ENOUGH_CHANGEATTR:
			try:
				srcVnum = player.GetItemIndex(inven_type, inven_pos)
				if srcVnum:
					itemName = item.GetItemName()
					ds_type, grade, step, strength = self.__GetDragonSoulTypeInfo(srcVnum)
					count = dragon_soul_refine_settings.default_change_attrcount[step]
					(invType2, invPos2, invItemCount2) = self.refineItemInfo[1]
					materialVnum = player.GetItemIndex(invType2, invPos2)
					if materialVnum:
						if invItemCount2 < count:
							self.wndPopupDialog.SetText(localeinfo.DRAGON_SOUL_NOT_ENOUGH_MATERIAL2 % (itemName, item.GetItemName(), count))
							self.wndPopupDialog.Open()
			except:
				pass
		
		self.Refresh()
		if app.ENABLE_DS_CHANGE_ATTR and self.refinetype == self.DS_REFINE_TYPE_CHANGEATTR:
			self.RefreshBeans()			

	def SetWindows(self, Inventory, DragonSoul):
		if Inventory:
			self.wndInventory = proxy(Inventory)

		if DragonSoul:
			self.wndDragonSoul = proxy(DragonSoul)
