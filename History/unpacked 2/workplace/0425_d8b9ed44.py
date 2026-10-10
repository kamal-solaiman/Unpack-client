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
import uiattachmetin
import uicommon
import uiquicksell
import uiprivateshopbuilder
import localeinfo
import constinfo
import osfinfo
import ime
import wndMgr
import interfacemodule
if app.USE_ACCE_SYSTEM:
	import acce

import systemSetting

if app.USE_OFFLINESHOP:
	import offlineshop
	import uiofflineshop_ae

if app.ENABLE_CHEQUE_SYSTEM:
	import uitooltip

if app.ITEM_CHECKINOUT_UPDATE:
	import exchange

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

from _weakref import proxy

ITEM_MALL_BUTTON_ENABLE = True
ITEM_FLAG_APPLICABLE = 1 << 14

class SpecialInventoryWindow(ui.ScriptWindow):
	USE_TYPE_TUPLE = (
		"USE_CLEAN_SOCKET",
		"USE_CHANGE_ATTRIBUTE",
		"USE_ADD_ATTRIBUTE",
		"USE_ADD_ATTRIBUTE2",
		"USE_ADD_ACCESSORY_SOCKET",
		"USE_PUT_INTO_ACCESSORY_SOCKET",
		"USE_PUT_INTO_BELT_SOCKET",
		"USE_PUT_INTO_RING_SOCKET",
		"USE_CHANGE_COSTUME_ATTR",
		"USE_RESET_COSTUME_ATTR",
		"USE_REMOVE_ENCHANT"
	)

	# sellingSlotNumber = -1
	# isLoaded = 0

	# interface = None

	# inventoryPageIndex = 0

	# if app.ENABLE_GROWTH_PET_SYSTEM:
		# petHatchingWindow = None
		# petFeedWindow = None
		# petNameChangeWindow = None

		# PetItemQuestionDlg = None
		# PetSkillDelDlg = None

	# if app.ENABLE_INGAME_WIKI:
		# wndWiki = None

	# if app.ENABLE_SORT_INVENTORY or app.USE_STACK_INVENTORY:
		# organizeDlg = None

	# questionDialog = None
	# pick_item_dialog = None
	# tooltipItem = None
	# wndItem = None

	# wndExpandOptionTitleBar = None
	# separateButton = None
	# StackButton = None
	# ActiveButton = None
	# DeactiveButton = None
	# wndEditLineName = None
	# slotBarExpandOption = None
	# boardExpandOption = None

	if app.ENABLE_SORT_INVENTORY or app.USE_STACK_INVENTORY:
		def __CloseOrganizeDlg(self):
			if self.organizeDlg:
				self.organizeDlg.Close()

		def __SortOrganizeDlg(self):
			net.SendChatPacket("/sort_special_inventory %d" % self.inventoryType)
			snd.PlaySound("sound/ui/pickup_item_in_inventory.wav")

			self.__CloseOrganizeDlg()

		def __StackOrganizeDlg(self):
			net.SendChatPacket("/stack_items %d" % (self.inventoryType))
			snd.PlaySound("sound/ui/pickup_item_in_inventory.wav")

			self.__CloseOrganizeDlg()

		def __OrganizeInventory(self):
			if not self.organizeDlg:
				tmp = uicommon.OrganizeItemsDialog()
				tmp.SetCancelEvent(ui.__mem_func__(self.__CloseOrganizeDlg))
				tmp.SetCloserEvent(ui.__mem_func__(self.__CloseOrganizeDlg))
				if app.ENABLE_SORT_INVENTORY:
					tmp.SetSortEvent(ui.__mem_func__(self.__SortOrganizeDlg))

				if app.USE_STACK_INVENTORY:
					tmp.SetStackEvent(ui.__mem_func__(self.__StackOrganizeDlg))

				self.organizeDlg = tmp

			if not self.organizeDlg:
				return

			self.organizeDlg.SetOnPotion(True if self.inventoryType == 5 else False)
			self.organizeDlg.Open()

	def __init__(self):
		self.isLoaded = 0

		self.sellingSlotNumber = -1
		self.inventoryPageIndex = 0

		if app.ENABLE_GROWTH_PET_SYSTEM:
			self.petHatchingWindow = None
			self.petFeedWindow = None
			self.petNameChangeWindow = None

			self.PetItemQuestionDlg = None
			self.PetSkillDelDlg = None

		if app.ENABLE_INGAME_WIKI:
			self.wndWiki = None

		if app.ENABLE_SORT_INVENTORY or app.USE_STACK_INVENTORY:
			self.organizeDlg = None

		self.questionDialog = None
		self.pick_item_dialog = None
		self.tooltipItem = None
		self.wndItem = None

		self.wndExpandOptionTitleBar = None
		self.separateButton = None
		self.StackButton = None
		self.ActiveButton = None
		self.DeactiveButton = None
		self.wndEditLineName = None
		self.slotBarExpandOption = None
		self.boardExpandOption = None

		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
			self.SetAnimationPreset("popup")

		self.interface = None

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "SPECIAL_INVENTORY")
		self.RefreshItemSlot()
		wndMgr.Show(self.hWnd)

	def BindInterfaceClass(self, interface):
		if interface:
			self.interface = proxy(interface)

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/specialinventorywindow.py")
		except:
			import exception
			exception.Abort("SpecialInventoryWindow.LoadWindow.LoadObject")

		try:
			self.titleBar = self.GetChild("TitleBar")
			self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))

			self.board = self.GetChild("ui_board")

			wndItem = self.GetChild("ItemSlot")
			self.titleName = self.GetChild("TitleName")

			if app.ENABLE_SORT_INVENTORY or app.USE_STACK_INVENTORY:
				tmp = self.GetChild2("SortInventoryButton")
				tmp.SetEvent(ui.__mem_func__(self.__OrganizeInventory))
				self.itemsBtn = tmp
			else:
				self.GetChild2("SortInventoryButton").Hide()

			self.SkillBookButton = self.GetChild("SkillBookButton")
			self.UpgradeItemsButton = self.GetChild("UpgradeItemsButton")
			self.stoneButton = self.GetChild("StoneButton")
			self.GiftBoxButton = self.GetChild("GiftBoxButton")
			if app.NEW_SPECIAL_INV:
				self.SwitcherButton = self.GetChild("SwitcherButton")
				self.PotsButton = self.GetChild("PotsButton")

			self.inventoryTab = []
			self.inventoryTab.append(self.GetChild("Inventory_Tab_01"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_02"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_03"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_04"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_05"))

			self.dlgQuestion = uicommon.QuestionDialog2()
			self.dlgQuestion.Close()

			if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
				self.listHighlightedSlot = []
		except:
			import exception
			exception.Abort("SpecialInventoryWindow.LoadWindow.BindObject")

		self.original_height = self.board.GetHeight()

		## Item
		wndItem.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndItem.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndItem.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		self.SkillBookButton.SetEvent(lambda arg=0: self.SetInventoryType(arg))
		self.UpgradeItemsButton.SetEvent(lambda arg=1: self.SetInventoryType(arg))
		self.stoneButton.SetEvent(lambda arg=2: self.SetInventoryType(arg))
		self.GiftBoxButton.SetEvent(lambda arg=3: self.SetInventoryType(arg))
		if app.NEW_SPECIAL_INV:
			self.SwitcherButton.SetEvent(lambda arg=4: self.SetInventoryType(arg))
			self.PotsButton.SetEvent(lambda arg=5: self.SetInventoryType(arg))

		self.SkillBookButton.Down()

		## AttachMetinDialog
		self.attachMetinDialog = uiattachmetin.AttachMetinDialog()
		self.attachMetinDialog.Hide()

		if app.USE_ACCE_SYSTEM:
			self.listHighlightedAcceSlot = []

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			self.listHighlightedChangeLookSlot = []

		for inven_index in range(player.SPECIAL_INVENTORY_PAGE_COUNT):
			self.inventoryTab[inven_index].SetEvent(lambda arg=inven_index: self.SetInventoryPage(arg))
		self.inventoryTab[0].Down()

		self.wndItem = wndItem

		self.MakeNewTitleBarOptions()

		if app.ENABLE_GROWTH_PET_SYSTEM:
			self.PetItemQuestionDlg = uicommon.QuestionDialog()
			self.PetItemQuestionDlg.Close()

			self.PetSkillDelDlg = uicommon.QuestionDialog2()
			self.PetSkillDelDlg.Close()
			self.PetSkillAllDelBookIndex = -1

		## Refresh
		self.SetInventoryType(0)
		self.SetInventoryPage(0)

		self.RefreshItemSlot()

	def MakeNewTitleBarOptions(self):
		for invTab in self.inventoryTab:
			invTab.posOriginal = invTab.GetLocalPosition()

		for catTab in [self.SkillBookButton, self.UpgradeItemsButton, self.stoneButton, self.GiftBoxButton, self.SwitcherButton, self.PotsButton]:
			catTab.posOriginal = catTab.GetLocalPosition()

		self.wndItem.posOriginal = self.wndItem.GetLocalPosition()

		self.wndExpandOptionTitleBar = self.itemsBtn
		self.wndExpandOptionTitleBar.isExpanded = False
		self.wndExpandOptionTitleBar.SetEvent(ui.__mem_func__(self.OnExpandTitleBar))

		self.boardExpandOption = ui.BorderA()
		self.boardExpandOption.SetParent(self)
		self.boardExpandOption.SetPosition(10, 30)
		self.boardExpandOption.SetSize(self.GetWidth() - 18, 30)
		self.boardExpandOption.Hide()

		ROOT_PATH = "d:/ymir work/ui/game/inv_manage/"
		self.separateButton = ui.MakeButton(self.boardExpandOption, 4, 6, uiscriptlocale.ITEM_SORT_OPTION, ROOT_PATH, "btn-sort-1.png", "btn-sort-2.png", "btn-sort-3.png")
		self.separateButton.SetEvent(ui.__mem_func__(self.__SortOrganizeDlg))

		self.StackButton = ui.MakeButton(self.boardExpandOption, 28, 6, uiscriptlocale.ITEM_STACK_OPTION, ROOT_PATH, "btn-stack-1.png", "btn-stack-2.png", "btn-stack-3.png")
		self.StackButton.SetEvent(ui.__mem_func__(self.__StackOrganizeDlg))

		self.ActiveButton = ui.MakeButton(self.boardExpandOption, 4, 6 + 20, uiscriptlocale.ITEM_AUTO_ACTIVATE_POTION_OPTION, ROOT_PATH, "btn-pots-1.png", "btn-pots-2.png", "btn-pots-3.png")
		self.ActiveButton.SetEvent(ui.__mem_func__(self.DoActivePots))

		self.DeactiveButton = ui.MakeButton(self.boardExpandOption, 28, 6 + 20, uiscriptlocale.ITEM_AUTO_DEACTIVATE_POTION_OPTION, ROOT_PATH, "btn-dispots-1.png", "btn-dispots-2.png", "btn-dispots-3.png")
		self.DeactiveButton.SetEvent(ui.__mem_func__(self.DoDeactivePots))

		self.ActiveButton.Hide()
		self.DeactiveButton.Hide()

		self.slotBarExpandOption = ui.MakeImageBox(self.boardExpandOption, "neue/input.png", 52, 6)
		self.wndEditLineName = ui.EditLine()
		self.wndEditLineName.SetParent(self.slotBarExpandOption)
		self.wndEditLineName.SetPosition(4, 4)
		self.wndEditLineName.SetSize(self.slotBarExpandOption.GetWidth() - 4, self.slotBarExpandOption.GetHeight() - 4)
		self.wndEditLineName.SetMax(20)
		self.wndEditLineName.SetOverlayTextNew(localeinfo.OFFLINESHOP_SEARCH_NAME)
		self.wndEditLineName.OnIMEUpdate = ui.__mem_func__(self.OnValueUpdateSearch)
		self.wndEditLineName.SetEscapeEvent(ui.__mem_func__(self.OnEditLineName))
		self.wndEditLineName.Show()

	def DoActivePots(self):
		net.SendChatPacket("/autouse_blend_items 1")

	def DoDeactivePots(self):
		net.SendChatPacket("/autouse_blend_items 0")

	def OnEditLineName(self):
		if len(self.wndEditLineName.GetText()) == 0:
			self.Close()
			return True
			
		self.wndEditLineName.SetText("")
		self.OnValueUpdateSearch(True)
		return True

	def OnValueUpdateSearch(self, skipIme = False):
		if self.IsShow() == False:
			return

		if self.boardExpandOption.IsShow() == False:
			return

		if skipIme == False:
			if self.wndEditLineName.IsFocus() == False:
				return

			ui.EditLine.OnIMEUpdate(self.wndEditLineName)

		self.RefreshBagSlotWindow()

	def OnExpandTitleBar(self):
		self.wndExpandOptionTitleBar.isExpanded = not self.wndExpandOptionTitleBar.isExpanded
		
		SET_SIZE_HEIGHT = 30
		
		self.ActiveButton.Hide()
		self.DeactiveButton.Hide()
		
		if self.inventoryType == 5:
			self.ActiveButton.Show()
			self.DeactiveButton.Show()
			SET_SIZE_HEIGHT = 53

		self.boardExpandOption.SetSize(self.boardExpandOption.GetWidth(), SET_SIZE_HEIGHT)
		
		if not self.wndExpandOptionTitleBar.isExpanded:
			self.boardExpandOption.Hide()
			self.board.SetSize(self.GetWidth(), self.original_height)

			for invTab in self.inventoryTab:
				invTab.SetPosition(*invTab.posOriginal)
				
			for catTab in [self.SkillBookButton, self.UpgradeItemsButton, self.stoneButton, self.GiftBoxButton, self.SwitcherButton, self.PotsButton]:
				catTab.SetPosition(*catTab.posOriginal)
			
			self.wndItem.SetPosition(*self.wndItem.posOriginal)
		else:
			self.boardExpandOption.Show()
			self.board.SetSize(self.GetWidth(), self.original_height + SET_SIZE_HEIGHT)
			
			for invTab in self.inventoryTab:
				invTab.SetPosition(invTab.posOriginal[0], invTab.posOriginal[1] + SET_SIZE_HEIGHT)

			# for catTab in [self.SkillBookButton, self.UpgradeItemsButton, self.stoneButton, self.GiftBoxButton, self.SwitcherButton, self.PotsButton]:
				# catTab.SetPosition(catTab.posOriginal[0], catTab.posOriginal[1] - (SET_SIZE_HEIGHT))

			self.wndItem.SetPosition(self.wndItem.posOriginal[0], self.wndItem.posOriginal[1] + SET_SIZE_HEIGHT)
			
		self.wndEditLineName.SetText("")
	
		self.SetSize(self.board.GetWidth(), self.board.GetHeight())
		self.UpdateRect()

	def Destroy(self):
		if self.pick_item_dialog:
			self.pick_item_dialog.Destroy()
			del self.pick_item_dialog
			self.pick_item_dialog = None

		if app.ENABLE_SORT_INVENTORY or app.USE_STACK_INVENTORY:
			if self.itemsBtn:
				self.itemsBtn.SetEvent(None)
				self.itemsBtn = None

			if self.organizeDlg:
				self.organizeDlg.Destroy()
				del self.organizeDlg
				self.organizeDlg = None

		if app.ENABLE_INGAME_WIKI:
			self.wndWiki = None

		self.SkillBookButton.SetEvent(None)
		self.SkillBookButton = None

		self.UpgradeItemsButton.SetEvent(None)
		self.UpgradeItemsButton = None

		self.stoneButton.SetEvent(None)
		self.stoneButton = None

		self.GiftBoxButton.SetEvent(None)
		self.GiftBoxButton = None

		if app.NEW_SPECIAL_INV:
			self.SwitcherButton.SetEvent(None)
			self.SwitcherButton = None

			self.PotsButton.SetEvent(None)
			self.PotsButton = None

		for btn in self.inventoryTab:
			btn.SetEvent(None)

		self.inventoryTab = None

		self.inventoryPageIndex = None

		self.attachMetinDialog.Close()
		self.attachMetinDialog.Destroy()
		del self.attachMetinDialog
		self.attachMetinDialog = None

		if self.questionDialog:
			self.questionDialog.Close()
			del self.questionDialog
			self.questionDialog = None

		if app.ENABLE_GROWTH_PET_SYSTEM:
			self.petHatchingWindow = None
			self.petFeedWindow = None
			self.petNameChangeWindow = None 

			self.PetItemQuestionDlg.Close()
			del self.PetItemQuestionDlg
			self.PetItemQuestionDlg = None

			self.PetSkillDelDlg.Close()
			del self.PetSkillDelDlg
			self.PetSkillDelDlg = None

		self.tooltipItem = None

		self.wndItem.SetSelectEmptySlotEvent(None)
		self.wndItem.SetSelectItemSlotEvent(None)
		self.wndItem.SetUnselectItemSlotEvent(None)
		self.wndItem.SetUseSlotEvent(None)
		self.wndItem.SetOverInItemEvent(None)
		self.wndItem.SetOverOutItemEvent(None)
		self.wndItem = None

		self.wndExpandOptionTitleBar.SetEvent(None)
		self.wndExpandOptionTitleBar = None

		self.separateButton.SetEvent(None)
		self.separateButton = None

		self.StackButton.SetEvent(None)
		self.StackButton = None

		self.ActiveButton.SetEvent(None)
		self.ActiveButton = None

		self.DeactiveButton.SetEvent(None)
		self.DeactiveButton = None

		if self.wndEditLineName.IsFocus():
			self.wndEditLineName.KillFocus()

		self.wndEditLineName.SetEscapeEvent(None)
		del self.wndEditLineName
		self.wndEditLineName = None

		del self.slotBarExpandOption
		self.slotBarExpandOption = None

		del self.boardExpandOption
		self.boardExpandOption = None

		if app.USE_ACCE_SYSTEM:
			self.listHighlightedAcceSlot = None

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			self.listHighlightedChangeLookSlot = None

		self.board = None

		self.titleBar.SetCloseEvent(None)
		self.titleBar = None

		self.titleName = None

		self.interface = None

		self.ClearDictionary()

	def Hide(self):
		self.OverOutItem()

		if self.wndEditLineName and self.wndEditLineName.IsFocus():
			self.wndEditLineName.KillFocus()

		if self.pick_item_dialog:
			self.pick_item_dialog.Close()

		# if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS():
		self.OnCloseQuestionDialog()
			# return

		if app.ENABLE_SORT_INVENTORY or app.USE_STACK_INVENTORY:
			self.__CloseOrganizeDlg()

		if app.ENABLE_GROWTH_PET_SYSTEM:
			if self.PetItemQuestionDlg:
				self.PetItemQuestionDlg.Close()

			if self.PetSkillDelDlg:
				self.PetSkillDelDlg.Close()

		wndMgr.Hide(self.hWnd)

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "SPECIAL_INVENTORY")
		self.Hide()

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("SPECIAL_INVENTORY", x, y)

	def SetInventoryPage(self, page):
		self.inventoryPageIndex = page

		for index in range(len(self.inventoryTab)):
			if index == page:
				continue
			self.inventoryTab[index].SetUp()

		self.RefreshBagSlotWindow()

	def SetInventoryType(self, type):
		self.inventoryType = int(type)

		if self.wndExpandOptionTitleBar.isExpanded:
			self.OnExpandTitleBar()

		if type == 0:
			self.SkillBookButton.Over()
			self.UpgradeItemsButton.SetUp()
			self.stoneButton.SetUp()
			self.GiftBoxButton.SetUp()
			if app.NEW_SPECIAL_INV:
				self.SwitcherButton.SetUp()
				self.PotsButton.SetUp()
			self.titleName.SetText(localeinfo.SPECIAL_INVENTORY_SKILL_BOOK)

		elif type == 2:
			self.stoneButton.Over()
			self.GiftBoxButton.SetUp()
			self.UpgradeItemsButton.SetUp()
			self.SkillBookButton.SetUp()
			if app.NEW_SPECIAL_INV:
				self.SwitcherButton.SetUp()
				self.PotsButton.SetUp()
			self.titleName.SetText(localeinfo.SPECIAL_INVENTORY_STONE)

		elif type == 3:
			self.GiftBoxButton.Over()
			self.stoneButton.SetUp()
			self.UpgradeItemsButton.SetUp()
			self.SkillBookButton.SetUp()
			if app.NEW_SPECIAL_INV:
				self.SwitcherButton.SetUp()
				self.PotsButton.SetUp()
			self.titleName.SetText(localeinfo.SPECIAL_INVENTORY_CHEST)

		elif type == 4 and app.NEW_SPECIAL_INV:
			self.SwitcherButton.Over()
			self.PotsButton.SetUp()
			self.GiftBoxButton.SetUp()
			self.stoneButton.SetUp()
			self.UpgradeItemsButton.SetUp()
			self.SkillBookButton.SetUp()
			self.titleName.SetText(localeinfo.SPECIAL_INVENTORY_SWITCHERS)

		elif type == 5 and app.NEW_SPECIAL_INV:
			self.PotsButton.Over()
			self.SwitcherButton.SetUp()
			self.GiftBoxButton.SetUp()
			self.stoneButton.SetUp()
			self.UpgradeItemsButton.SetUp()
			self.SkillBookButton.SetUp()
			self.titleName.SetText(localeinfo.SPECIAL_INVENTORY_POTS)

		else:
			self.UpgradeItemsButton.Over()
			self.SkillBookButton.SetUp()
			self.stoneButton.SetUp()
			self.GiftBoxButton.SetUp()
			if app.NEW_SPECIAL_INV:
				self.SwitcherButton.SetUp()
				self.PotsButton.SetUp()
			self.titleName.SetText(localeinfo.SPECIAL_INVENTORY_MATERIAL)

		self.RefreshBagSlotWindow()

	def __CanAddItemAttr(self, dstSlotPos):
		if dstSlotPos >= item.SKILL_BOOK_INVENTORY_SLOT_START:
			return False

		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
			return False

		attrCount = 0
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
				attrCount += 1

		if attrCount < 4:
			return True

		return False

	def __CanResetCostumeAttr(self, dstSlotPos):
		if dstSlotPos >= item.SKILL_BOOK_INVENTORY_SLOT_START:
			return False

		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if item.GetItemType() != item.ITEM_TYPE_COSTUME:
			return False

		if app.USE_ACCE_SYSTEM:
			if item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
				return False

		if app.USE_MOUNT_COSTUME_SYSTEM:
			if item.GetItemSubType() == item.COSTUME_TYPE_MOUNT:
				return False

		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
				return True

		return False

	def __CanChangeItemAttrList(self, dstSlotPos):
		if dstSlotPos >= item.SKILL_BOOK_INVENTORY_SLOT_START:
			return False

		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
			return False

		attrCount = 0
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
				attrCount += 1

		if attrCount > 0:
			return True

	def OnPickItem(self, itemSlot, splitCount, splitAuto):
		if app.USE_AUTO_SPLIT_ITEMS and splitAuto:
			net.SendChatPacket("/split_item {} {} {}".format(self.inventoryType, itemSlot, splitCount))
			return

		if app.USE_OFFLINESHOP and uiofflineshop_ae.IsBuildingShop() and uiofflineshop_ae.IsSaleSlot(player.INVENTORY, itemSlot):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
			return

		itemVnum = player.GetItemIndex(itemSlot)
		if itemVnum:
			if self.inventoryType == 0:
				mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_SKILL_BOOK_INVENTORY, itemSlot, itemVnum, splitCount)
			elif self.inventoryType == 1:
				mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY, itemSlot, itemVnum, splitCount)
			elif self.inventoryType == 2:
				mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_STONE_INVENTORY, itemSlot, itemVnum, splitCount)
			elif self.inventoryType == 3:
				mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_GIFT_BOX_INVENTORY, itemSlot, itemVnum, splitCount)
			elif app.NEW_SPECIAL_INV and self.inventoryType == 4:
				mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_ENCHANT_INVENTORY, itemSlot, itemVnum, splitCount)
			elif app.NEW_SPECIAL_INV and self.inventoryType == 5:
				mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_POTS_INVENTORY, itemSlot, itemVnum, splitCount)

		if app.ENABLE_REMEMBER_LAST_SPLIT:
			systemSetting.SetLastSplitData(splitCount)

	def __InventoryLocalSlotPosToGlobalSlotPos(self, local):
		if self.inventoryType == 0:
			return self.inventoryPageIndex * player.SPECIAL_INVENTORY_PAGE_SIZE + local + item.SKILL_BOOK_INVENTORY_SLOT_START
		elif self.inventoryType == 1:
			return self.inventoryPageIndex * player.SPECIAL_INVENTORY_PAGE_SIZE + local + item.UPGRADE_ITEMS_INVENTORY_SLOT_START
		elif self.inventoryType == 2:
			return self.inventoryPageIndex * player.SPECIAL_INVENTORY_PAGE_SIZE + local + item.STONE_INVENTORY_SLOT_START
		elif self.inventoryType == 3:
			return self.inventoryPageIndex * player.SPECIAL_INVENTORY_PAGE_SIZE + local + item.GIFT_BOX_INVENTORY_SLOT_START
		elif self.inventoryType == 4 and app.NEW_SPECIAL_INV:
			return self.inventoryPageIndex * player.SPECIAL_INVENTORY_PAGE_SIZE + local + item.ENCHANT_INVENTORY_SLOT_START
		elif self.inventoryType == 5 and app.NEW_SPECIAL_INV:
			return self.inventoryPageIndex * player.SPECIAL_INVENTORY_PAGE_SIZE + local + item.POTS_INVENTORY_SLOT_START


	def RefreshBagSlotWindow(self):
		if not self.wndItem:
			return

		onTopWindow = None

		if app.WJ_ENABLE_TRADABLE_ICON and self.interface:
			onTopWindow = self.interface.GetOnTopWindow()

		for i in xrange(self.wndItem.GetSlotCount()):
			self.wndItem.DeactivateSlot(i)

			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
			itemVnum = player.GetItemIndex(slotNumber)

			if itemVnum and self.wndEditLineName.GetText() and self.wndExpandOptionTitleBar.isExpanded:
				item.SelectItem(itemVnum)
				stName = item.GetItemName()

				if itemVnum == 50300: # IS_SKILLBOOK
					import skill
					stName = skill.GetSkillName(player.GetItemMetinSocket(slotNumber, 0))

				text = self.wndEditLineName.GetText()
				if len(stName) >= len(text) and stName[:len(text)].lower() == text.lower():
					pass
				else:
					self.wndItem.ClearSlot(i)
					continue

			if onTopWindow != None or (app.USE_OFFLINESHOP and uiofflineshop_ae.IsBuildingShop()):
				if itemVnum:
					if self.interface.MarkUnusableInvenSlotOnTopWnd(onTopWindow, slotNumber):
						self.wndItem.SetUnusableSlotOnTopWnd(i)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(i)
				else:
					self.wndItem.SetUsableSlotOnTopWnd(i)

			itemCount = player.GetItemCount(slotNumber)
			if not itemVnum or not itemCount:
				self.wndItem.ClearSlot(i)
				continue
			elif 1 == itemCount:
				itemCount = 0

			self.wndItem.SetItemSlot(i, itemVnum, itemCount)

			changeLookVnum = 0
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				changeLookVnum = player.GetChangeLookVnum(player.INVENTORY, slotNumber)
				if not changeLookVnum:
					self.wndItem.EnableSlotCoverImage(i, False)
				else:
					self.wndItem.SetSlotCoverImage(i, "icon/item/ingame_convert_mark.tga")

			if app.NEW_SPECIAL_INV:
				wasActivated = 0

				if constinfo.IS_AUTO_POTION(itemVnum):
					if player.GetItemMetinSocket(slotNumber, 0):
						self.wndItem.ActivateSlot(i)
						wasActivated = 1

																				#(osfinfo.IS_BLEND_POTION(itemVnum) or osfinfo.IS_EXTENDED_BLEND_POTION(itemVnum)):
				if wasActivated == 0 and app.ENABLE_EXTENDED_BLEND_AFFECT and item.GetItemTypeByVnum(itemVnum) == item.ITEM_TYPE_BLEND:
					if player.GetItemMetinSocket(slotNumber, 3):
						self.wndItem.ActivateSlot(i)
						wasActivated = 1

						if osfinfo.IS_EXTENDED_BLEND_POTION(itemVnum):
							self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_RED)
						elif osfinfo.NORMAL_BLEND_COLOR(itemVnum):
							self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_PURPLE)
						elif osfinfo.DRAGON_GOD_COLOR(itemVnum):
							self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_ORANGE)
						elif osfinfo.OTHER_ITEMS_COLOR(itemVnum):
							self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_DARK_BLUE)
						else:
							self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_DARK_BLUE)

					if not changeLookVnum:
						if osfinfo.IS_EXTENDED_BLEND_POTION(itemVnum):
							self.wndItem.SetSlotCoverImage(i, "d:/ymir work/ui/acce/ingame_convert_mark_02.tga")
						elif osfinfo.IS_BLEND_POTION(itemVnum) and itemVnum not in (39217, 39218, 39219, 39220, 39224, 39225):
							self.wndItem.SetSlotCoverImage(i, "icon/item/trade.tga")
						else:
							self.wndItem.EnableSlotCoverImage(i, False)

				# ENABLE_ACCOUNT_BIND_ITEMS — override cover image for bound items.
				fishVnum = itemVnum
				if fishVnum >= 37863 and fishVnum <= 37892:
					self.wndItem.SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")

				if app.ENABLE_ACCOUNT_BIND_ITEMS and player.IsItemAccountBound(player.INVENTORY, slotNumber):
					self.wndItem.SetSlotCoverImage(i, "icon/item/account_locked.png")

		if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
			self.__HighlightSlot_Refresh()

		self.wndItem.RefreshSlot()
		if app.QUICK_SELL_SYSTEM:
			self.RefreshQuickSellMarks()


	def RefreshItemSlot(self):
		self.RefreshBagSlotWindow()

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def SellItem(self):
		if app.USE_OFFLINESHOP:
			if uiofflineshop_ae.IsBuildingShop() and uiofflineshop_ae.IsSaleSlot(player.INVENTORY, self.sellingSlotNumber):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				return

		if self.sellingSlotitemIndex == player.GetItemIndex(self.sellingSlotNumber):
			if self.sellingSlotitemCount == player.GetItemCount(self.sellingSlotNumber):
				net.SendShopSellPacketNew(self.sellingSlotNumber, self.questionDialog.count, player.INVENTORY)
				snd.PlaySound("sound/ui/money.wav")
		
		self.OnCloseQuestionDialog()

	def OnDetachMetinFromItem(self):
		if None == self.questionDialog:
			return

		self.__SendUseItemToItemPacket(self.questionDialog.sourcePos, self.questionDialog.targetPos)
		self.OnCloseQuestionDialog()

	def OnCloseQuestionDialog(self):
		if not self.questionDialog:
			return

		self.questionDialog.Close()
		self.questionDialog = None
		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	def SelectEmptySlot(self, selectedSlotPos):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		selectedSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(selectedSlotPos)

		if mousemodule.mouseController.isAttached():
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			attachedItemCount = mousemodule.mouseController.GetAttachedItemCount()
			attachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()

			if app.USE_OFFLINESHOP:
				if uiofflineshop_ae.IsBuildingShop() and uiofflineshop_ae.IsSaleSlot(player.SlotTypeToInvenType(attachedSlotType),attachedSlotPos):
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
					return

			if player.SLOT_TYPE_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_STONE_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_ENCHANT_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_POTS_INVENTORY == attachedSlotType:

				itemCount = player.GetItemCount(attachedSlotPos)
				attachedCount = mousemodule.mouseController.GetAttachedItemCount()

				self.__SendMoveItemPacket(attachedSlotPos, selectedSlotPos, attachedCount)

				if item.IsRefineScroll(attachedItemIndex):
					self.interface.SetUseItemMode(False)

			elif player.SLOT_TYPE_PRIVATE_SHOP == attachedSlotType:
				mousemodule.mouseController.RunCallBack("INVENTORY")
			elif player.SLOT_TYPE_SHOP == attachedSlotType:
				net.SendShopBuyPacket(attachedSlotPos)

			elif player.SLOT_TYPE_SAFEBOX == attachedSlotType:
				if player.ITEM_MONEY == attachedItemIndex:
					net.SendSafeboxWithdrawMoneyPacket(mousemodule.mouseController.GetAttachedItemCount())
					snd.PlaySound("sound/ui/money.wav")
				else:
					net.SendSafeboxCheckoutPacket(attachedSlotPos, selectedSlotPos)

			elif player.SLOT_TYPE_MALL == attachedSlotType:
				net.SendMallCheckoutPacket(attachedSlotPos, selectedSlotPos)

			mousemodule.mouseController.DeattachObject()

	def SelectItemSlot(self, itemSlotIndex):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		itemSlotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(itemSlotIndex)

		if mousemodule.mouseController.isAttached():
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			attachedItemVID = mousemodule.mouseController.GetAttachedItemIndex()

			if player.SLOT_TYPE_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_STONE_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_ENCHANT_INVENTORY == attachedSlotType or\
				player.SLOT_TYPE_POTS_INVENTORY == attachedSlotType:

				self.__DropSrcItemToDestItemInInventory(attachedItemVID, attachedSlotPos, itemSlotIndex)

			mousemodule.mouseController.DeattachObject()
		else:
			curCursorNum = app.GetCursor()

			if app.SELL == curCursorNum:
				self.__SellItem(itemSlotIndex)

			elif app.BUY == curCursorNum:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SHOP_BUY_INFO)

			elif app.IsPressed(app.DIK_LALT):
				link = player.GetItemLink(itemSlotIndex)
				ime.PasteString(link)

			elif app.IsPressed(app.DIK_LSHIFT):
				itemCount = player.GetItemCount(itemSlotIndex)
				if itemCount > 1:
					if not self.pick_item_dialog:
						self.pick_item_dialog = uicommon.PickItemDialog()
						self.pick_item_dialog.SetAcceptEvent(ui.__mem_func__(self.OnPickItem))

					self.pick_item_dialog.Open(itemSlotIndex, itemCount)
			elif app.IsPressed(app.DIK_LCONTROL):
				itemIndex = player.GetItemIndex(itemSlotIndex)

				if True == item.CanAddToQuickSlotItem(itemIndex):
					player.RequestAddToEmptyLocalQuickSlot(player.SLOT_TYPE_INVENTORY, itemSlotIndex)
				else:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.QUICKSLOT_REGISTER_DISABLE_ITEM)
			else:
				if app.IsPressed(app.DIK_TAB):
					if app.QUICK_SELL_SYSTEM:
						self.interface.ToggleQuickSellSlot(player.INVENTORY, itemSlotIndex)
						self.RefreshBagSlotWindow()
						return

					itemCount = player.GetItemCount(itemSlotIndex)
					import shop
					if shop.IsOpen():
						#if not shop.IsPrivateShop():
						net.SendShopSellPacketNew(itemSlotIndex, itemCount, player.INVENTORY)
						snd.PlaySound("sound/ui/money.wav")
						return
				
				selectedItemVNum = player.GetItemIndex(itemSlotIndex)
				itemCount = player.GetItemCount(itemSlotIndex)
				if app.ENABLE_GROWTH_PET_SYSTEM:
					if self.__CanAttachGrowthPetItem(selectedItemVNum, itemSlotIndex):
						mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_INVENTORY, itemSlotIndex, selectedItemVNum, itemCount)
				else:
					mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_INVENTORY, itemSlotIndex, selectedItemVNum, itemCount)

				if self.__IsUsableItemToItem(selectedItemVNum, itemSlotIndex):
					self.interface.SetUseItemMode(True)
				else:
					self.interface.SetUseItemMode(False)

				snd.PlaySound("sound/ui/pick.wav")

	def __DropSrcItemToDestItemInInventory(self, srcItemVID, srcItemSlotPos, dstItemSlotPos):
		if srcItemSlotPos == dstItemSlotPos:
			return
	
		## ???? ?? ?????
		## ??? ?? ??.
		if app.USE_ACCE_SYSTEM:
			if player.GetAcceRefineWindowOpen() == 1:
				return

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if player.GetChangeLookWindowOpen() == 1:
				return

		if app.USE_OFFLINESHOP:
			if uiofflineshop_ae.IsBuildingShop() and uiofflineshop_ae.IsSaleSlot(player.INVENTORY, srcItemSlotPos):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				return

		## [MT-462]
		player.GetItemIndex(srcItemSlotPos)
		if player.GetItemIndex(srcItemSlotPos) == player.GetItemIndex(dstItemSlotPos) \
			and (player.GetItemFlags(srcItemSlotPos) & item.ITEM_FLAG_STACKABLE) \
			and player.IsEquipmentSlot(dstItemSlotPos) == False:
			self.__SendMoveItemPacket(srcItemSlotPos, dstItemSlotPos, 0)
			return

		if app.ENABLE_SOUL_BIND_SYSTEM:
			# cyh itemseal 2013 11 08
			if item.IsSealScroll(srcItemVID):
				if player.CanSealItem(srcItemVID, player.INVENTORY, dstItemSlotPos):
					self.__OpenQuestionDialog(srcItemSlotPos, dstItemSlotPos)

			if app.ENABLE_SET_ITEM:
				if item.IsSetItemScroll(srcItemVID):
					if player.CanSetItemClearItem(srcItemVID, player.INVENTORY, dstItemSlotPos):
						self.__OpenQuestionDialog(srcItemSlotPos, dstItemSlotPos)
						return

		if item.IsRefineScroll(srcItemVID):
			self.RefineItem(srcItemSlotPos, dstItemSlotPos)
			self.interface.SetUseItemMode(False)

		elif item.IsMetin(srcItemVID):
			self.AttachMetinToItem(srcItemSlotPos, dstItemSlotPos)

		elif item.IsDetachScroll(srcItemVID):
			self.DetachMetinFromItem(srcItemSlotPos, dstItemSlotPos)

		elif item.IsKey(srcItemVID):
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		elif (player.GetItemFlags(srcItemSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		elif item.GetUseType(srcItemVID) in self.USE_TYPE_TUPLE:
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		else:
			if app.ENABLE_GROWTH_PET_SYSTEM:
				if self.__IsPetItem(srcItemVID):
					if self.__SendUsePetItemToItemPacket(srcItemVID, srcItemSlotPos, dstItemSlotPos):
						return

			self.__SendMoveItemPacket(srcItemSlotPos, dstItemSlotPos, 0)

	def __SellItem(self, itemSlotPos):
		if app.USE_OFFLINESHOP:
			if uiofflineshop_ae.IsBuildingShop():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				return

		self.sellingSlotNumber = itemSlotPos
		itemIndex = player.GetItemIndex(itemSlotPos)
		itemCount = player.GetItemCount(itemSlotPos)

		self.sellingSlotitemIndex = itemIndex
		self.sellingSlotitemCount = itemCount

		item.SelectItem(itemIndex)
		## 20140220
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

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def __OnClosePopupDialog(self):
		self.pop = None

	def DetachMetinFromItem(self, scrollSlotPos, targetSlotPos):
		scrollIndex = player.GetItemIndex(scrollSlotPos)
		targetIndex = player.GetItemIndex(targetSlotPos)

		if not player.CanDetach(scrollIndex, targetSlotPos):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_METIN_INSEPARABLE_ITEM)
			return

		self.questionDialog = uicommon.QuestionDialog()
		self.questionDialog.SetText(localeinfo.REFINE_DO_YOU_SEPARATE_METIN)
		self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnDetachMetinFromItem))
		self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
		self.questionDialog.Open()
		self.questionDialog.sourcePos = scrollSlotPos
		self.questionDialog.targetPos = targetSlotPos

	def AttachMetinToItem(self, metinSlotPos, targetSlotPos):
		metinIndex = player.GetItemIndex(metinSlotPos)
		targetIndex = player.GetItemIndex(targetSlotPos)

		item.SelectItem(metinIndex)
		itemName = item.GetItemName()

		result = player.CanAttachMetin(metinIndex, targetSlotPos)

		if player.ATTACH_METIN_NOT_MATCHABLE_ITEM == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_CAN_NOT_ATTACH(itemName))

		if player.ATTACH_METIN_NO_MATCHABLE_SOCKET == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_NO_SOCKET(itemName))

		elif player.ATTACH_METIN_NOT_EXIST_GOLD_SOCKET == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_NO_GOLD_SOCKET(itemName))

		elif player.ATTACH_METIN_CANT_ATTACH_TO_EQUIPMENT == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_EQUIP_ITEM)

		if player.ATTACH_METIN_OK != result:
			return

		self.attachMetinDialog.Open(metinSlotPos, targetSlotPos)

	def OverOutItem(self):
		if self.wndItem:
			self.wndItem.SetUsableItem(False)

		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OverInItem(self, overSlotPos):
		if not self.wndItem:
			return

		if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
			overInvenSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(overSlotPos)
			self.wndItem.SetUsableItem(False)

			getItemVNum = player.GetItemIndex
			itemVnum = getItemVNum(overInvenSlotPos)
			self.DelHighlightSlot(overInvenSlotPos)

			if mousemodule.mouseController.isAttached():
				attachedItemType = mousemodule.mouseController.GetAttachedType()

				if player.SLOT_TYPE_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_STONE_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_ENCHANT_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_POTS_INVENTORY == attachedItemType:

					attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
					attachedItemVNum = mousemodule.mouseController.GetAttachedItemIndex()

					try:
						if self.__CanUseSrcItemToDstItem(attachedItemVNum, attachedSlotPos, overInvenSlotPos):
							self.wndItem.SetUsableItem(True)
							self.ShowToolTip(overInvenSlotPos)
							return
					except RuntimeError:
						pass

			self.ShowToolTip(overInvenSlotPos)
		else:
			overSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(overSlotPos)
			self.wndItem.SetUsableItem(False)

			if mousemodule.mouseController.isAttached():
				attachedItemType = mousemodule.mouseController.GetAttachedType()

				if player.SLOT_TYPE_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_STONE_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_ENCHANT_INVENTORY == attachedItemType or\
					player.SLOT_TYPE_POTS_INVENTORY == attachedItemType:

					attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
					attachedItemVNum = mousemodule.mouseController.GetAttachedItemIndex()

					if self.__CanUseSrcItemToDstItem(attachedItemVNum, attachedSlotPos, overSlotPos):
						self.wndItem.SetUsableItem(True)
						self.ShowToolTip(overSlotPos)
						return

			self.ShowToolTip(overSlotPos)

	def __IsUsableItemToItem(self, srcItemVNum, srcSlotPos):
		if item.IsRefineScroll(srcItemVNum):
			return True
		elif item.IsMetin(srcItemVNum):
			return True
		elif item.IsDetachScroll(srcItemVNum):
			return True
		elif item.IsKey(srcItemVNum):
			return True
		elif (player.GetItemFlags(srcSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
			return True
		else:
			if app.ENABLE_GROWTH_PET_SYSTEM:
				if self.__IsUsablePetItem(srcItemVNum):
					return True
			if app.ENABLE_SET_ITEM:
				if item.IsSetItemScroll(srcItemVNum):
					return True
			if item.GetUseType(srcItemVNum) in self.USE_TYPE_TUPLE:
				return True

		return False

	def __CanUseSrcItemToDstItem(self, srcItemVNum, srcSlotPos, dstSlotPos):
		if srcSlotPos == dstSlotPos:
			return False

		if item.IsRefineScroll(srcItemVNum):
			if player.REFINE_OK == player.CanRefine(srcItemVNum, dstSlotPos):
				return True
		elif item.IsMetin(srcItemVNum):
			if player.ATTACH_METIN_OK == player.CanAttachMetin(srcItemVNum, dstSlotPos):
				return True
		elif item.IsDetachScroll(srcItemVNum):
			if player.DETACH_METIN_OK == player.CanDetach(srcItemVNum, dstSlotPos):
				return True
		elif item.IsKey(srcItemVNum):
			if player.CanUnlock(srcItemVNum, dstSlotPos):
				return True
		elif (player.GetItemFlags(srcSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
			return True
		else:
			if app.ENABLE_GROWTH_PET_SYSTEM:
				if self.__CanUseSrcPetItemToDstPetItem(srcItemVNum, srcSlotPos, dstSlotPos):
					return True
			if app.ENABLE_SET_ITEM:
				if item.IsSetItemScroll(srcItemVNum):
					if player.CanSetItemClearItem(srcItemVNum, srcSlotPos, dstSlotPos):
						return True

			useType=item.GetUseType(srcItemVNum)

			if "USE_CLEAN_SOCKET" == useType:
				if self.__CanCleanBrokenMetinStone(dstSlotPos):
					return True
			elif "USE_CHANGE_ATTRIBUTE" == useType:
				if srcItemVNum == 39929:
					return False

				if srcItemVNum == 39930:
					dstItemVNum = player.GetItemIndex(dstSlotPos)
					item.SelectItem(dstItemVNum)
					if item.GetItemType() != item.ITEM_TYPE_WEAPON:
						return False

				if self.__CanChangeItemAttrList(dstSlotPos):
					return True
			elif "USE_ADD_ATTRIBUTE" == useType:
				if self.__CanAddItemAttr(dstSlotPos):
					return True
			elif "USE_ADD_ATTRIBUTE2" == useType:
				if self.__CanAddItemAttr(dstSlotPos):
					return True
			elif "USE_ADD_ACCESSORY_SOCKET" == useType:
				if self.__CanAddAccessorySocket(dstSlotPos):
					return True
			elif "USE_PUT_INTO_ACCESSORY_SOCKET" == useType:
				if self.__CanPutAccessorySocket(dstSlotPos, srcItemVNum):
					return True;
			elif "USE_PUT_INTO_BELT_SOCKET" == useType:
				dstItemVNum = player.GetItemIndex(dstSlotPos)
				if not dstItemVNum:
					return False

				item.SelectItem(dstItemVNum)

				if item.ITEM_TYPE_BELT == item.GetItemType():
					return True
			elif "USE_CHANGE_COSTUME_ATTR" == useType:
				if self.__CanChangeCostumeAttrList(dstSlotPos):
					return True
			elif "USE_RESET_COSTUME_ATTR" == useType:
				if self.__CanResetCostumeAttr(dstSlotPos):
					return True
			else:
				pass

		return False

	def ShowToolTip(self, slotIndex):
		if self.tooltipItem:
			vnum = player.GetItemIndex(slotIndex)
			if not vnum:
				return

			self.tooltipItem.SetInventoryItem(slotIndex)
			#dream
			if self.inventoryType == 5:
				self.tooltipItem.DeclareShortcut(("key_shift", "key_c"), localeinfo.TOOLTIP_QUICKACTIVE_ALL)
				self.tooltipItem.DeclareShortcut(("key_shift", "key_c"), localeinfo.TOOLTIP_QUICKDEACTIVE_ALL)
			i = 0
			if app.ENABLE_INGAME_WIKI:
				if app.USE_MULTIPLE_OPENING:
					if vnum != 27987:
						view = item.CanBeMultipleOpened(vnum)
					else:
						view = 0
				else:
					item.SelectItem(vnum)
					view = 1 if vnum != 27987 and item.GetItemType() in (item.ITEM_TYPE_GIFTBOX, item.ITEM_TYPE_GACHA) else 0

				if view:
					self.tooltipItem.DeclareShortcut(("key_shift", "key_rclick"), localeinfo.TOOLTIP_VIEW_CHEST_CONTENT)
					i = 1

					if app.USE_MULTIPLE_OPENING:
						if player.GetItemCount(slotIndex) > 1:
							self.tooltipItem.DeclareShortcut(("key_ctrl", "key_rclick"), localeinfo.TOOLTIP_OPEN_ALL_CHETS)
				else:
					self.tooltipItem.DeclareShortcut(("key_shift", "key_rclick"), localeinfo.TOOLTIP_WIKI_HOVER)
					i = 1
			
			elif player.GetItemCount(slotIndex) > 1:
				if app.USE_MULTIPLE_OPENING:
					view = item.CanBeMultipleOpened(vnum)
					if view:
						self.tooltipItem.DeclareShortcut(("key_ctrl", "key_rclick"), localeinfo.TOOLTIP_OPEN_ALL_CHETS)
						i = 1

			if app.USE_OFFLINESHOP:
				if uiofflineshop_ae.IsBuildingShop():
					self.__AddTooltipSaleMode(slotIndex)
				else:
					self.tooltipItem.DeclareShortcut(("key_alt", "key_rclick"), localeinfo.TOOLTIP_QUICKSEARCH_OFFLINESHOP)

	if app.USE_OFFLINESHOP:
		def __AddTooltipSaleMode(self, slot):
			if player.IsEquipmentSlot(slot):
				return

			itemIndex = player.GetItemIndex(slot)
			if itemIndex !=0:
				item.SelectItem(itemIndex)
				if item.IsAntiFlag(item.ANTIFLAG_MYSHOP) or item.IsAntiFlag(item.ANTIFLAG_GIVE):
					return
				
				self.tooltipItem.AddRightClickForSale()

	def OnTop(self):
		if None != self.tooltipItem:
			self.tooltipItem.SetTop()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def UseItemSlot(self, slotIndex):
		curCursorNum = app.GetCursor()
		if app.SELL == curCursorNum:
			return
		elif constinfo.GET_ITEM_QUESTION_DIALOG_STATUS():
			return
		elif player.IsActingEmotion():
			return

		slotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(slotIndex)

		if app.USE_OFFLINESHOP and uiofflineshop_ae.IsBuildingShop():
			itemIndex = player.GetItemIndex(slotIndex)
			if itemIndex:
				item.SelectItem(itemIndex)

				if not item.IsAntiFlag(item.ANTIFLAG_GIVE) and\
					not item.IsAntiFlag(item.ANTIFLAG_MYSHOP):
					offlineshop.ShopBuilding_AddItem(player.INVENTORY, slotIndex)
				else:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				
				return

		itemVnum = player.GetItemIndex(slotIndex)
		if not itemVnum:
			return

		if app.USE_OFFLINESHOP and not uiofflineshop_ae.IsBuildingShop() and\
			(app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT)):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				wndShopOffline = interfaceHandler.wndShopOffline
				if wndShopOffline:
					wndSearchShop = wndShopOffline.wndSearchShop
					if wndSearchShop:
						item.SelectItem(itemVnum)
						wndSearchShop.SearchByName(item.GetItemName())
						return

		if app.ITEM_CHECKINOUT_UPDATE:
			if player.IsOpenSafeBox():
				net.SendSafeboxCheckinPacket(slotIndex)
				return

			if exchange.isTrading():
				net.SendExchangeItemAddPacket(player.INVENTORY, slotIndex, -1)
				return

		if app.USE_MULTIPLE_OPENING and (app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL)):
			if itemVnum > 0:
				itemCount = player.GetItemCount(slotIndex)
				if item.CanBeMultipleOpened(itemVnum) and itemCount > 1:
					net.SendMultipleOpening(player.INVENTORY, slotIndex, itemCount)
				else:
					self.__UseItem(slotIndex)
		else:
			self.__UseItem(slotIndex)

		mousemodule.mouseController.DeattachObject()
		self.OverOutItem()

	def __UseItem(self, slotIndex):
		ItemVNum = player.GetItemIndex(slotIndex)
		if not ItemVNum:
			return

		item.SelectItem(ItemVNum)

		# if app.QUICK_SELL_SYSTEM:
			# if app.IsPressed(app.DIK_TAB):
				# if slotIndex in constinfo.QUICK_SELL_ITEMS:
					# self.interface.RemoveSellSlot(slotIndex)
					# self.RefreshBagSlotWindow()
					# return
				# else:
					# self.interface.AppendSellSlot(slotIndex)
					# self.RefreshBagSlotWindow()
					# return

		if app.USE_OFFLINESHOP:
			if uiofflineshop_ae.IsBuildingShop() and uiofflineshop_ae.IsSaleSlot(player.INVENTORY, slotIndex):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				return

		if app.ENABLE_GROWTH_PET_SYSTEM:
			itemType = item.GetItemType()
			
			if self.interface.wndPetInfoWindow.AttachItemToPetWindow(player.INVENTORY, slotIndex):
				return
				
			if self.PetSkillDelDlg and self.PetSkillDelDlg.IsShow():
				self.__PetSkillDeleteQuestionDialogCancel()

			if item.ITEM_TYPE_PET == itemType:
				self.__UseItemPet(slotIndex)
				return

		if app.WJ_ENABLE_TRADABLE_ICON:
			if self.interface.AttachInvenItemToOtherWindowSlot(slotIndex):
				return

		if item.IsFlag(item.ITEM_FLAG_CONFIRM_WHEN_USE):
			self.questionDialog = uicommon.QuestionDialog()
			self.questionDialog.SetText(localeinfo.INVENTORY_REALLY_USE_ITEM2)

			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnAccept))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnCancel))
			self.questionDialog.Open()
			self.questionDialog.slotIndex = slotIndex

			constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)
			return

		if app.ENABLE_INGAME_WIKI and app.IsPressed(app.DIK_LSHIFT):
			if not self.wndWiki:
				return

			if app.USE_MULTIPLE_OPENING:
				view = item.CanBeMultipleOpened(ItemVNum)
			else:
				item.SelectItem(ItemVNum)
				view = 1 if item.GetItemType() in (item.ITEM_TYPE_GIFTBOX, item.ITEM_TYPE_GACHA) else 0

			if view:
				if not self.wndWiki.IsShow():
					net.ToggleWikiWindow()

				self.wndWiki.CloseBaseWindows()
				self.wndWiki.mainChestWindow.Show([ItemVNum,])
			else:
				if not self.wndWiki.IsShow():
					net.ToggleWikiWindow()

				self.wndWiki.CloseBaseWindows()
				self.wndWiki.OpenSpecialPage(None, ItemVNum, False)
			return

		self.__SendUseItemPacket(slotIndex)

	def __UseItemQuestionDialog_OnCancel(self):
		self.OnCloseQuestionDialog()

	def __UseItemQuestionDialog_OnAccept(self):
		self.__SendUseItemPacket(self.questionDialog.slotIndex)
		self.OnCloseQuestionDialog()

	def __SendUseItemToItemPacket(self, srcSlotPos, dstSlotPos):
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.USE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		if self.interface.IsShowDlgQuestionWindow():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
			return

		net.SendItemUseToItemPacket(srcSlotPos, dstSlotPos)

	def __SendUseItemPacket(self, slotPos):
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.USE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		if self.interface.IsShowDlgQuestionWindow():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
			return

		net.SendItemUsePacket(slotPos)

	def __SendMoveItemPacket(self, srcSlotPos, dstSlotPos, srcItemCount):
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.MOVE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		if self.interface.IsShowDlgQuestionWindow():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
			return

		net.SendItemMovePacket(srcSlotPos, dstSlotPos, srcItemCount)


	if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
		def HighlightSlot(self, slot):
			if not slot in self.listHighlightedSlot:
				self.listHighlightedSlot.append(slot)

		def DelHighlightSlot(self, inventorylocalslot):
			if inventorylocalslot in self.listHighlightedSlot:
				if inventorylocalslot >= player.SPECIAL_INVENTORY_PAGE_SIZE:
					self.wndItem.DeactivateSlot(inventorylocalslot - (self.inventoryPageIndex * player.SPECIAL_INVENTORY_PAGE_SIZE))
				else:
					self.wndItem.DeactivateSlot(inventorylocalslot)

				self.listHighlightedSlot.remove(inventorylocalslot)

				self.RefreshBagSlotWindow() # hot fix

		def __HighlightSlot_Refresh(self):
			for i in xrange(self.wndItem.GetSlotCount()):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
				if slotNumber in self.listHighlightedSlot:
					self.wndItem.ActivateSlot(i)

		def __HighlightSlot_Clear(self):
			for i in xrange(self.wndItem.GetSlotCount()):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
				if slotNumber in self.listHighlightedSlot:
					self.wndItem.DeactivateSlot(i)
					self.listHighlightedSlot.remove(slotNumber)

	def IsDlgQuestionShow(self):
		if self.dlgQuestion.IsShow():
			return True
		else:
			return False

	def SetUseItemMode(self, bUse):
		self.wndItem.SetUseMode(bUse)

	def CancelDlgQuestion(self):
		self.__Cancel()

	def GetInventoryPageIndex(self):
		return self.inventoryPageIndex

	def GetInventoryType(self):
		return self.inventoryType

	if app.ENABLE_GROWTH_PET_SYSTEM:
		def __UseItemPet(self, slotIndex):
			itemSubType = item.GetItemSubType()		
			if item.PET_EGG == itemSubType:
				self.petHatchingWindow.HatchingWindowOpen(player.INVENTORY, slotIndex)
				
			elif item.PET_UPBRINGING == itemSubType:
				if self.__CanUseGrowthPet(slotIndex):
					self.__SendUseItemPacket(slotIndex)
						
			elif item.PET_BAG == itemSubType:
				if self.__CanUsePetBagItem(slotIndex):
					if self.questionDialog:
						self.questionDialog.Close()
						
					self.questionDialog = uicommon.QuestionDialog()
					self.questionDialog.SetText(localeinfo.INVENTORY_REALLY_USE_PET_BAG_TAKE_OUT)
					self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnAccept))
					self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnCancel))
					self.questionDialog.slotIndex = slotIndex
					self.questionDialog.Open()

			elif item.PET_STAT_POTION == itemSubType:
				self.__SendUseItemPacket(slotIndex)

			if item.PET_SKILL_ALL_DEL_BOOK == itemSubType:
				pet_id = player.GetActivePetItemId()
				if 0 == pet_id:
					return
				(skill_count, pet_skill1, pet_skill_level1, pet_skill_cool1, pet_skill2, pet_skill_level2, pet_skill_cool2, pet_skill3, pet_skill_level3, pet_skill_cool3) = player.GetPetSkill(pet_id)
				if 0 == pet_skill1 and 0 == pet_skill2 and 0 == pet_skill3:
					popup = uicommon.PopupDialog()
					popup.SetText(localeinfo.PET_EMPTY_SKILL_SLOT_USE_ITEM)
					popup.SetAcceptEvent(self.__OnClosePopupDialog)
					popup.Open()
					self.pop = popup
					return
			
				self.PetSkillAllDelBookIndex = slotIndex
				self.SetCantMouseEventSlot( self.PetSkillAllDelBookIndex )
				
				self.PetSkillDelDlg.SetAcceptEvent(ui.__mem_func__(self.__PetSkillDeleteQuestionDialogAccept))
				self.PetSkillDelDlg.SetCancelEvent(ui.__mem_func__(self.__PetSkillDeleteQuestionDialogCancel))
				
				self.PetSkillDelDlg.SetText1( localeinfo.PET_SKILL_DELETE_QUESTION_DLG_MSG1 )
				self.PetSkillDelDlg.SetText2( localeinfo.PET_SKILL_DELETE_QUESTION_DLG_MSG2 )
				(w,h) = self.PetSkillDelDlg.GetTextSize1()
				self.PetSkillDelDlg.SetWidth(w+100)
				self.PetSkillDelDlg.Open()
				
		def __OnClosePopupDialog(self):
			self.pop = None

		def __ActivePetHighlightSlot(self, slotNumber):
			active_id = player.GetActivePetItemId()
			
			if active_id == player.GetItemMetinSocket(player.INVENTORY, slotNumber, 2):
				
				if slotNumber >= player.INVENTORY_PAGE_SIZE:
					slotNumber -= (self.inventoryPageIndex * player.INVENTORY_PAGE_SIZE)
			
				self.wndItem.ActivateSlot(slotNumber)
			else:
				if slotNumber >= player.INVENTORY_PAGE_SIZE:
					slotNumber -= (self.inventoryPageIndex * player.INVENTORY_PAGE_SIZE)
					
				self.wndItem.DeactivateSlot(slotNumber)

		def __SetCoolTimePetItemSlot(self, slotNumber, itemVnum):
		
			item.SelectItem(itemVnum)
			itemSubType = item.GetItemSubType()
		
			if itemSubType not in [item.PET_UPBRINGING, item.PET_BAG]:
				return
				
			if itemSubType == item.PET_BAG:
				id = player.GetItemMetinSocket(player.INVENTORY, slotNumber, 2)
				if id == 0:
					return
			
			(limitType, limitValue) = item.GetLimit(0)

			if itemSubType == item.PET_UPBRINGING:
				limitValue = player.GetItemMetinSocket(player.INVENTORY, slotNumber, 1)
					
			if limitType in [item.LIMIT_REAL_TIME, item.LIMIT_REAL_TIME_START_FIRST_USE]:
								
				sock_time   = player.GetItemMetinSocket(player.INVENTORY, slotNumber, 0)
				
				remain_time = max(0, sock_time - app.GetGlobalTimeStamp())
			
				if slotNumber >= player.INVENTORY_PAGE_SIZE:
					slotNumber -= (self.inventoryPageIndex * player.INVENTORY_PAGE_SIZE)

				self.wndItem.SetSlotCoolTimeInverse(slotNumber, limitValue, limitValue - remain_time)

		def __IsPetItem(self, srcItemVID):
			item.SelectItem(srcItemVID)
			
			if item.GetItemType() == item.ITEM_TYPE_PET:
				return True
			
			return False

		def __SendUsePetItemToItemPacket(self, srcItemVID, srcItemSlotPos, dstItemSlotPos):
			if self.__CanUseSrcPetItemToDstPetItem(srcItemVID, srcItemSlotPos, dstItemSlotPos):
				srcItemVnum		= player.GetItemIndex(srcItemSlotPos)
				item.SelectItem( srcItemVnum )
				srcItemType		= item.GetItemType()
				srcItemSubType	= item.GetItemSubType()
				
				if item.ITEM_TYPE_PET == srcItemType:					
					if srcItemSubType in [item.PET_FEEDSTUFF, item.PET_BAG]:
						self.__OpenPetItemQuestionDialog(srcItemSlotPos, dstItemSlotPos)
					elif item.PET_NAME_CHANGE == srcItemSubType:
						self.__UseItemPetNameChange(srcItemSlotPos, dstItemSlotPos)
				return True
				
			return False
			
		def __UseItemPetNameChange(self, srcSlotPos, dstSlotPos):
			if self.petNameChangeWindow:
				self.petNameChangeWindow.NameChangeWindowOpen(srcSlotPos, dstSlotPos)

		def __IsUsablePetItem(self, srcItemVNum):
			item.SelectItem(srcItemVNum)
			srcItemType		= item.GetItemType()
			srcItemSubType	= item.GetItemSubType()

			if srcItemType != item.ITEM_TYPE_PET:
				return False
			
			if srcItemSubType not in [item.PET_UPBRINGING, item.PET_FEEDSTUFF, item.PET_BAG, item.PET_NAME_CHANGE]:
				return False
			
			return True

		def __CanUseSrcPetItemToDstPetItem(self, srcItemVNum, srcSlotPos, dstSlotPos):
			item.SelectItem(srcItemVNum)
			srcItemType		= item.GetItemType()
			srcItemSubType	= item.GetItemSubType()
			
			if srcItemType != item.ITEM_TYPE_PET:
				return False
			
			if srcItemSubType == item.PET_FEEDSTUFF:		
				detIndex = player.GetItemIndex(dstSlotPos)
				item.SelectItem(detIndex)
				
				dstItemType		= item.GetItemType()
				dstItemSubType	= item.GetItemSubType()
				
				if dstItemType != item.ITEM_TYPE_PET:
					return False
					
				if dstItemSubType not in [item.PET_UPBRINGING]:
					return False
					
				if dstItemSubType == item.PET_BAG:
					incaseTime = player.GetItemMetinSocket(dstSlotPos, 1)
					if incaseTime == 0:
						return False
			
			elif srcItemSubType == item.PET_BAG:
				detIndex = player.GetItemIndex(dstSlotPos)
				item.SelectItem(detIndex)
				
				dstItemType		= item.GetItemType()
				dstItemSubType	= item.GetItemSubType()
				
				if dstItemType != item.ITEM_TYPE_PET:
					return False
					
				if dstItemSubType not in [item.PET_UPBRINGING, item.PET_BAG]:
					return False
			
				lifeTime = player.GetItemMetinSocket(dstSlotPos, 0)
					
				if dstItemSubType == item.PET_UPBRINGING:
					if lifeTime < app.GetGlobalTimeStamp():
						return False

					srcIncase = player.GetItemMetinSocket(srcSlotPos, 1)
					if srcIncase != 0:
						return False
					
				elif dstItemSubType == item.PET_BAG:
					if lifeTime > app.GetGlobalTimeStamp():
						return False
						
					srcIncase = player.GetItemMetinSocket(srcSlotPos, 1)
					if srcIncase != 0:
						return False
					
					destIncase = player.GetItemMetinSocket(dstSlotPos, 1)
					if destIncase == 0:
						return False
						
			elif srcItemSubType == item.PET_NAME_CHANGE:
				detIndex = player.GetItemIndex(dstSlotPos)
				item.SelectItem(detIndex)
				
				dstItemType		= item.GetItemType()
				dstItemSubType	= item.GetItemSubType()
				
				if dstItemType != item.ITEM_TYPE_PET:
					return False
					
				if dstItemSubType not in [item.PET_UPBRINGING]:
					return False
					
			else:
				return False
			
			return True

		def __CanUseGrowthPet(self, slotIndex):
			if not player.GetItemMetinSocket(player.INVENTORY, slotIndex, 2):
				return False
				
			(limitType, limitValue) = item.GetLimit(0)
			remain_time = 999
			if item.LIMIT_REAL_TIME == limitType:
				sock_time   = player.GetItemMetinSocket(player.INVENTORY, slotIndex, 0)
				if app.GetGlobalTimeStamp() > sock_time:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_SUMMON_BECAUSE_LIFE_TIME_END)
					return False
					
			return True

		def __CanUsePetBagItem(self, slotIndex):
			if not player.GetItemMetinSocket(player.INVENTORY, slotIndex, 2):
				return False
				
			(limitType, limitValue) = item.GetLimit(0)
			remain_time = 999
			if item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
				sock_time   = player.GetItemMetinSocket(player.INVENTORY, slotIndex, 0)
				use_cnt	    = player.GetItemMetinSocket(player.INVENTORY, slotIndex, 1)
				
				if use_cnt:
					if app.GetGlobalTimeStamp() > sock_time:
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_USE_BAG)
						return False;
						
			return True

		def __CanAttachGrowthPetItem(self, itemVNum, itemSlotIndex):
			activePetId = player.GetActivePetItemId()
			if activePetId == 0:
				return True
			
			item.SelectItem(itemVNum)
			itemType	= item.GetItemType()
			itemSubType = item.GetItemSubType()
			
			if item.ITEM_TYPE_PET == itemType and itemSubType == item.PET_UPBRINGING:
				petId = player.GetItemMetinSocket(itemSlotIndex, 2)
				if petId == activePetId:
					return False
					
					
			return True

		def SetPetHatchingWindow(self, window):
			self.petHatchingWindow = window

		def SetPetNameChangeWindow(self, window):
			self.petNameChangeWindow = window

		def SetPetFeedWindow(self, window):
			self.petFeedWindow = window

		def ItemMoveFeedWindow(self, slotWindow, slotIndex):
			if not self.petFeedWindow:
				return
				
			self.petFeedWindow.ItemMoveFeedWindow(slotWindow, slotIndex)

		def __OpenPetBagQuestionDialog(self, srcItemSlotPos, dstItemSlotPos):
			if self.interface.IsShowDlgQuestionWindow():
				self.interface.CloseDlgQuestionWindow()

		def __OpenPetItemQuestionDialog(self, srcItemPos, dstItemPos):
			if self.interface.IsShowDlgQuestionWindow():
				self.interface.CloseDlgQuestionWindow()
			
			getItemVNum=player.GetItemIndex
			self.srcItemPos = srcItemPos
			self.dstItemPos = dstItemPos

			srcItemVnum = getItemVNum(srcItemPos)
			dstItemVnum = getItemVNum(dstItemPos)
			
			item.SelectItem( srcItemVnum )
			src_item_name = item.GetItemName( srcItemVnum )
			srcItemType		= item.GetItemType()
			srcItemSubType	= item.GetItemSubType()
			
			item.SelectItem( dstItemVnum )
			dst_item_name = item.GetItemName( getItemVNum(dstItemPos) )
			
			self.PetItemQuestionDlg.SetAcceptEvent(ui.__mem_func__(self.__PetItemAccept))
			self.PetItemQuestionDlg.SetCancelEvent(ui.__mem_func__(self.__PetItemCancel))
			
			if item.ITEM_TYPE_PET == srcItemType:
				if item.PET_FEEDSTUFF == srcItemSubType:
					self.PetItemQuestionDlg.SetText( localeinfo.INVENTORY_REALLY_USE_PET_FEEDSTUFF_ITEM % ( src_item_name, dst_item_name ) )
					self.PetItemQuestionDlg.Open()
				
				elif item.PET_BAG == srcItemSubType:
					self.PetItemQuestionDlg.SetText( localeinfo.INVENTORY_REALLY_USE_PET_BAG_ITEM )
					self.PetItemQuestionDlg.Open()			
				
		def __PetItemAccept(self):
			self.PetItemQuestionDlg.Close()
			self.__SendUseItemToItemPacket(self.srcItemPos, self.dstItemPos)
			self.srcItemPos = (0, 0)
			self.dstItemPos = (0, 0)
			self.srcItemWindow = None
			self.dstItemWindow = None

		def __PetItemCancel(self):
			self.srcItemPos = (0, 0)
			self.dstItemPos = (0, 0)
			self.PetItemQuestionDlg.Close()

		def __PetSkillDeleteQuestionDialogAccept(self):
			net.SendPetDeleteAllSkill( self.PetSkillAllDelBookIndex )	
			self.__PetSkillDeleteQuestionDialogCancel()
			
		def __PetSkillDeleteQuestionDialogCancel(self):
			self.PetSkillDelDlg.Close()
			self.SetCanMouseEventSlot( self.PetSkillAllDelBookIndex )
			self.PetSkillAllDelBookIndex = -1
			
		def SetCanMouseEventSlot(self, inven_slot_index):
			if inven_slot_index >= player.INVENTORY_PAGE_SIZE:
				page = self.GetInventoryPageIndex() # range 0,1,2,3
				inven_slot_index -= (page * player.INVENTORY_PAGE_SIZE)
			self.wndItem.SetCanMouseEventSlot(inven_slot_index)
			
		def SetCantMouseEventSlot(self, inven_slot_index):
			if inven_slot_index >= player.INVENTORY_PAGE_SIZE:
				page = self.GetInventoryPageIndex() # range 0,1,2,3
				inven_slot_index -= (page * player.INVENTORY_PAGE_SIZE)
			self.wndItem.SetCantMouseEventSlot(inven_slot_index)

	if app.QUICK_SELL_SYSTEM:
		# Runs last in RefreshBagSlotWindow so the cart mark wins over the other cover images.
		# Deliberately set-only: the account-bound and convert covers are applied earlier in the
		# same refresh, so clearing here would wipe them. Deselected marks are cleared by the
		# ENABLE_CHANGE_LOOK_SYSTEM reset pass above - SetItemSlot itself keeps the cover when the
		# slot's vnum is unchanged. Turning that flag off would strand marks here.
		def RefreshQuickSellMarks(self):
			if not self.wndItem:
				return

			for k in xrange(self.wndItem.GetSlotCount()):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(k)
				if uiquicksell.IsSelected(player.INVENTORY, slotNumber):
					self.wndItem.SetSlotCoverImage(k, uiquicksell.SELECTED_COVER_IMAGE)
