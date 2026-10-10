# coding: latin_1

import app
import chr
import net
import player

import ui
import snd
import shop
import mousemodule
import uicommon
import localeinfo
import chat
import item
import systemSetting

if app.ENABLE_EXTENDED_BLEND_AFFECT:
	import osfinfo

from _weakref import proxy

g_isBuildingPrivateShop = False
g_itemPriceDict = {}
g_privateShopAdvertisementBoardDict = {}

def Clear():
	global g_itemPriceDict
	global g_isBuildingPrivateShop
	g_itemPriceDict = {}
	g_isBuildingPrivateShop = False

def IsPrivateShopItemPriceList():
	global g_itemPriceDict
	if g_itemPriceDict:
		return True
	else:
		return False

def IsBuildingPrivateShop():
	global g_isBuildingPrivateShop
	if player.IsOpenPrivateShop() or g_isBuildingPrivateShop:
		return True
	else:
		return False

if app.WJ_ENABLE_TRADABLE_ICON:
	INVENTORY_PAGE_SIZE = player.INVENTORY_PAGE_SIZE
	if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
		SPECIAL_INVENTORY_PAGE_SIZE = player.SPECIAL_INVENTORY_PAGE_SIZE

if app.ENABLE_CHEQUE_SYSTEM:
	PRIVATE_SHOP_YANG = 0
	PRIVATE_SHOP_WON = 1

	def SetPrivateShopItemPrice(itemVNum, itemPrice, itemCheque):
		global g_itemPriceDict
		g_itemPriceDict[int(itemVNum)] = [itemPrice, itemCheque]

	def GetPrivateShopItemCheque(itemVNum):
		try:
			global g_itemPriceDict
			return g_itemPriceDict[itemVNum][PRIVATE_SHOP_WON]
		except KeyError:
			return 0

	def GetPrivateShopItemPrice(itemVNum):
		try:
			global g_itemPriceDict
			return g_itemPriceDict[itemVNum][PRIVATE_SHOP_YANG]
		except KeyError:
			return 0
else:
	def SetPrivateShopItemPrice(itemVNum, itemPrice):
		global g_itemPriceDict
		g_itemPriceDict[int(itemVNum)]=itemPrice

	def GetPrivateShopItemPrice(itemVNum):
		try:
			global g_itemPriceDict
			return g_itemPriceDict[itemVNum]
		except KeyError:
			return 0

def UpdateADBoard():
	for key in g_privateShopAdvertisementBoardDict.keys():
		if app.ENABLE_GRAPHIC_ON_OFF:
			if IsShowSalesRange(key):
				g_privateShopAdvertisementBoardDict[key].Show()
			else:
				g_privateShopAdvertisementBoardDict[key].Hide()
		else:
			g_privateShopAdvertisementBoardDict[key].Show()

def DeleteADBoard(vid):
	if not g_privateShopAdvertisementBoardDict.has_key(vid):
		return

	del g_privateShopAdvertisementBoardDict[vid]

if app.ENABLE_GRAPHIC_ON_OFF:
	def IsShowSalesRange(vid):
		if not vid:
			return False

		try:
			VIEW_RANGE = 0

			(xShop, yShop, zShop) = chr.GetPixelPosition(vid)
			(x, y, z) = player.GetMainCharacterPosition()

			if systemSetting.GetPrivateShopLevel() == 1: VIEW_RANGE = 5000
			elif systemSetting.GetPrivateShopLevel() == 2: VIEW_RANGE = 2500
			elif systemSetting.GetPrivateShopLevel() == 3: VIEW_RANGE = 1000
			elif systemSetting.GetPrivateShopLevel() == 4: VIEW_RANGE = 500

			if (abs(x - xShop) < VIEW_RANGE and abs(y - yShop) < VIEW_RANGE) or systemSetting.GetPrivateShopLevel() < 1:
				return True
			else:
				return False
		except:
			return False

class PrivateShopAdvertisementBoard(ui.ThinBoard):
	def __init__(self):
		ui.ThinBoard.__init__(self, "UI_BOTTOM")
		self.vid = None
		self.__MakeTextLine()

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def __MakeTextLine(self):
		self.textLine = ui.TextLine()
		self.textLine.SetParent(self)
		self.textLine.SetWindowHorizontalAlignCenter()
		self.textLine.SetWindowVerticalAlignCenter()
		self.textLine.SetHorizontalAlignCenter()
		self.textLine.SetVerticalAlignCenter()
		self.textLine.Show()

	def Open(self, vid, text):
		self.vid = vid

		self.textLine.SetText(text)
		self.textLine.UpdateRect()
		self.SetSize(len(text)*6 + 10*2, 20)
		self.Show()

		g_privateShopAdvertisementBoardDict[vid] = self

	def OnMouseLeftButtonUp(self):
		if not self.vid:
			return

		net.SendOnClickPacket(self.vid)

		return True

	def OnUpdate(self):
		if not self.vid:
			return

		if systemSetting.IsShowSalesText():
			if app.ENABLE_GRAPHIC_ON_OFF:
				if IsShowSalesRange(self.vid):
					self.Show()
				else:
					self.Hide()

				x, y = chr.GetProjectPosition(self.vid, 220)
				self.SetPosition(x - self.GetWidth()/2, y - self.GetHeight()/2)
			else:
				self.Show()
				x, y = chr.GetProjectPosition(self.vid, 220)
				self.SetPosition(x - self.GetWidth()/2, y - self.GetHeight()/2)
		else:
			for key in g_privateShopAdvertisementBoardDict.keys():
				if player.GetMainCharacterIndex() == key:
					g_privateShopAdvertisementBoardDict[key].Show()
					x, y = chr.GetProjectPosition(player.GetMainCharacterIndex(), 220)
					g_privateShopAdvertisementBoardDict[key].SetPosition(x - self.GetWidth()/2, y - self.GetHeight()/2)
				else:
					g_privateShopAdvertisementBoardDict[key].Hide()

class PrivateShopBuilder(ui.ScriptWindow):
	def __init__(self):
		#print "NEW MAKE_PRIVATE_SHOP_WINDOW ----------------------------------------------------------------"
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.interface = None
			self.inven = None

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				self.invenSpecial = None

		self.__LoadWindow()
		self.itemStock = {}
		self.tooltipItem = None
		self.priceInputBoard = None
		self.title = ""

	def __del__(self):
		#print "------------------------------------------------------------- DELETE MAKE_PRIVATE_SHOP_WINDOW"
		ui.ScriptWindow.__del__(self)

	def __LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/PrivateShopBuilder.py")
		except:
			import exception
			exception.Abort("PrivateShopBuilderWindow.LoadWindow.LoadObject")

		try:
			GetObject = self.GetChild
			self.nameLine = GetObject("NameLine")
			self.itemSlot = GetObject("ItemSlot")
			self.btnOk = GetObject("OkButton")
			self.btnClose = GetObject("CloseButton")
			self.titleBar = GetObject("TitleBar")

			if app.ENABLE_MYSHOP_DECO:
				self.PrvShopTab = []
				self.PrvShopTab.append(GetObject("1st"))
				self.PrvShopTab.append(GetObject("2nd"))
				self.board_width = GetObject("board").GetWidth()

		except:
			import exception
			exception.Abort("PrivateShopBuilderWindow.LoadWindow.BindObject")

		self.btnOk.SetEvent(ui.__mem_func__(self.OnOk))
		self.btnClose.SetEvent(ui.__mem_func__(self.OnClose))
		self.titleBar.SetCloseEvent(ui.__mem_func__(self.OnClose))

		self.itemSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.OnSelectEmptySlot))
		self.itemSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.OnSelectItemSlot))
		self.itemSlot.SetOverInItemEvent(ui.__mem_func__(self.OnOverInItem))
		self.itemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OnOverOutItem))

		if app.ENABLE_MYSHOP_DECO:
			for i in xrange(len(self.PrvShopTab)):
				self.PrvShopTab[i].SetEvent(lambda arg=i: self.SetPrivateShopPage(arg))

			self.PrvShopTabRefresh()

		# __SetDefaultShopDecoPosition
		if localeinfo.IsARABIC():
			self.itemSlot.SetPosition(self.board_width - 12, 70)
			self.btnOk.SetPosition(self.board_width - 104, 380 - 40)
			self.btnClose.SetPosition(self.board_width - 21, 380 - 40)
		else:
			self.itemSlot.SetPosition(12, 70)
			self.btnOk.SetPosition(21, 380 - 40)
			self.btnClose.SetPosition(104, 380 - 40)

	def Destroy(self):
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.interface = None
			self.inven = None

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				self.invenSpecial = None

		self.ClearDictionary()

		self.nameLine = None
		self.itemSlot = None
		self.btnOk = None
		self.btnClose = None
		self.titleBar = None
		self.priceInputBoard = None

		if app.ENABLE_MYSHOP_DECO:
			self.PrvShopTab = []

	def Open(self, title):
		self.title = title

		if len(title) > 25:
			title = title[:22] + "..."

		self.itemStock = {}
		shop.ClearPrivateShopStock()
		self.nameLine.SetText(title)
		self.SetCenterPosition()
		self.Refresh()
		self.SetTop()
		self.Show()

		global g_isBuildingPrivateShop
		g_isBuildingPrivateShop = True

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.ItemListIdx = []

		if app.ENABLE_CHEQUE_SYSTEM:
			self.IsCashItem = False

		if app.ENABLE_MYSHOP_DECO:
			self.PrvShopTabRefresh()

	def Close(self):
		global g_isBuildingPrivateShop
		g_isBuildingPrivateShop = False

		if self.priceInputBoard:
			self.priceInputBoard.Close()

		self.title = ""
		self.itemStock = {}
		shop.ClearPrivateShopStock()
		self.priceInputBoard = None;
		self.Hide()

		if app.WJ_ENABLE_TRADABLE_ICON:
			if self.interface:
				self.interface.SetOnTopWindow(player.ON_TOP_WND_NONE)
				self.interface.RefreshMarkInventoryBag()

			self.ItemListIdx = None

		if app.ENABLE_CHEQUE_SYSTEM:
			self.IsCashItem = False

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			shop.SetNameDialogOpen(False)

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def Refresh(self):
		getitemVNum = player.GetItemIndex
		getItemCount = player.GetItemCount
		setitemVNum = self.itemSlot.SetItemSlot
		delItem = self.itemSlot.ClearSlot

		for i in xrange(shop.SHOP_SLOT_COUNT):
			idx = self.__GetRealIndex(i)

			if not self.itemStock.has_key(idx):
				delItem(i)
				continue

			type, pos = self.itemStock[idx]

			itemCount = getItemCount(type, pos)

			if itemCount <= 1:
				itemCount = 0

			setitemVNum(i, getitemVNum(type, pos), itemCount)

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if not player.GetChangeLookVnum(type, pos) == 0:
					self.itemSlot.SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")
				else:
					self.itemSlot.EnableSlotCoverImage(i, False)

			if app.ENABLE_EXTENDED_BLEND_AFFECT:
				if osfinfo.IS_EXTENDED_BLEND_POTION(getitemVNum(type, pos)):
					self.itemSlot.SetSlotCoverImage(i, "d:/ymir work/ui/acce/ingame_convert_mark_02.tga")
				elif osfinfo.IS_BLEND_POTION(getitemVNum(type, pos)):
					self.itemSlot.SetSlotCoverImage(i, "icon/item/trade.tga")
				else:
					self.itemSlot.EnableSlotCoverImage(i, False)

		self.itemSlot.RefreshSlot()

	def OnSelectEmptySlot(self, selectedSlotPos):
		if self.priceInputBoard:
			return

		isAttached = mousemodule.mouseController.isAttached()
		if isAttached:
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			mousemodule.mouseController.DeattachObject()

			if player.SLOT_TYPE_INVENTORY != attachedSlotType and player.SLOT_TYPE_DRAGON_SOUL_INVENTORY != attachedSlotType and\
				(player.SLOT_TYPE_SKILL_BOOK_INVENTORY != attachedSlotType and\
				player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY != attachedSlotType and\
				player.SLOT_TYPE_STONE_INVENTORY != attachedSlotType and\
				player.SLOT_TYPE_GIFT_BOX_INVENTORY != attachedSlotType and app.ENABLE_SPECIAL_INVENTORY_SYSTEM and\
				player.SLOT_TYPE_ENCHANT_INVENTORY != attachedSlotType and\
				player.SLOT_TYPE_POTS_INVENTORY != attachedSlotType):
				return

			attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)

			itemVNum = player.GetItemIndex(attachedInvenType, attachedSlotPos)
			item.SelectItem(itemVNum)

			if player.IsEquipmentSlot(attachedSlotPos):
				return

			if app.ENABLE_SOUL_BIND_SYSTEM:
				if player.GetItemSealDate(attachedInvenType, attachedSlotPos) == -1 or player.GetItemSealDate(attachedInvenType, attachedSlotPos) > 0: #????? ???.
					return True

			if item.IsAntiFlag(item.ANTIFLAG_GIVE) or item.IsAntiFlag(item.ANTIFLAG_MYSHOP):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PRIVATE_SHOP_CANNOT_SELL_ITEM)
				return

			priceInputBoard = uicommon.MoneyInputDialog()
			priceInputBoard.SetTitle(localeinfo.PRIVATE_SHOP_INPUT_PRICE_DIALOG_TITLE)
			priceInputBoard.SetAcceptEvent(ui.__mem_func__(self.AcceptInputPrice))
			priceInputBoard.SetCancelEvent(ui.__mem_func__(self.CancelInputPrice))
			priceInputBoard.Open()

			if app.ENABLE_CHEQUE_SYSTEM:
				if self.IsCashItem:
					itemPrice = GetPrivateShopItemPrice(itemVNum)
					itemCheque = GetPrivateShopItemCheque(itemVNum)

					if itemPrice > 0 or itemCheque > 0:
						priceInputBoard.SetCheque(itemCheque)
						priceInputBoard.SetValue(itemPrice)
			else:
				itemPrice = GetPrivateShopItemPrice(itemVNum)
				if itemPrice > 0:
					priceInputBoard.SetValue(itemPrice)

			self.priceInputBoard = priceInputBoard
			self.priceInputBoard.itemVNum = itemVNum
			self.priceInputBoard.sourceWindowType = attachedInvenType
			self.priceInputBoard.sourceSlotPos = attachedSlotPos
			self.priceInputBoard.targetSlotPos = selectedSlotPos

			if app.WJ_ENABLE_TRADABLE_ICON:
				self.ItemListIdx.append(attachedSlotPos)
				self.priceInputBoard.Socket = self.GetItemDataSocketValue(attachedInvenType, attachedSlotPos)

	def OnSelectItemSlot(self, selectedSlotPos):
		if app.ENABLE_MYSHOP_DECO:
			selectedSlotPos = self.__GetRealIndex(selectedSlotPos)

		isAttached = mousemodule.mouseController.isAttached()
		if isAttached:
			snd.PlaySound("sound/ui/loginfail.wav")
			mousemodule.mouseController.DeattachObject()
		else:
			if not selectedSlotPos in self.itemStock:
				return

			invenType, invenPos = self.itemStock[selectedSlotPos]
			shop.DelPrivateShopItemStock(invenType, invenPos)
			snd.PlaySound("sound/ui/drop.wav")

			del self.itemStock[selectedSlotPos]

			if app.WJ_ENABLE_TRADABLE_ICON:
				for i in xrange(len(self.ItemListIdx)):
					if self.ItemListIdx[i] == invenPos:
						del self.ItemListIdx[i]
						break

			self.Refresh()

	def AcceptInputPrice(self):
		if not self.priceInputBoard:
			return True

		if app.ENABLE_CHEQUE_SYSTEM:
			cheque_text = self.priceInputBoard.GetCheque()
			text = self.priceInputBoard.GetText()

			if not text or not cheque_text:
				return True

			if not text.isdigit() or not cheque_text.isdigit():
				return True

			if int(text) <= 0 and int(cheque_text) <= 0:
				return True
		else:
			text = self.priceInputBoard.GetText()

			if not text:
				return True

			if not text.isdigit():
				return True

			if int(text) <= 0:
				return True

		attachedInvenType = self.priceInputBoard.sourceWindowType
		sourceSlotPos = self.priceInputBoard.sourceSlotPos
		targetSlotPos = self.priceInputBoard.targetSlotPos

		if app.ENABLE_MYSHOP_DECO:
			targetSlotPos = self.__GetRealIndex(targetSlotPos)

		for privatePos, (itemWindowType, itemSlotIndex) in self.itemStock.items():
			if itemWindowType == attachedInvenType and itemSlotIndex == sourceSlotPos:
				shop.DelPrivateShopItemStock(itemWindowType, itemSlotIndex)
				del self.itemStock[privatePos]

		if app.ENABLE_CHEQUE_SYSTEM:
			price = int(self.priceInputBoard.GetText())
			cheque = int(self.priceInputBoard.GetCheque())

			if IsPrivateShopItemPriceList():
				SetPrivateShopItemPrice(self.priceInputBoard.itemVNum, price, cheque)

			shop.AddPrivateShopItemStock(attachedInvenType, sourceSlotPos, targetSlotPos, price, cheque)
		else:
			price = int(self.priceInputBoard.GetText())

			if IsPrivateShopItemPriceList():
				SetPrivateShopItemPrice(self.priceInputBoard.itemVNum, price)

			shop.AddPrivateShopItemStock(attachedInvenType, sourceSlotPos, targetSlotPos, price)

		self.itemStock[targetSlotPos] = (attachedInvenType, sourceSlotPos)
		snd.PlaySound("sound/ui/drop.wav")

		self.Refresh()

		#####

		self.priceInputBoard = None
		return True

	def CancelInputPrice(self):
		if app.WJ_ENABLE_TRADABLE_ICON:
			pos = self.priceInputBoard.sourceSlotPos
			for i in xrange(len(self.ItemListIdx)):
				if self.ItemListIdx[i] == pos:
					del self.ItemListIdx[i]
					break

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				if self.inven or self.invenSpecial:
					page = self.inven.GetInventoryPageIndex() # range 0 ~ 1
					special_page = self.invenSpecial.GetInventoryPageIndex()

					if (page * INVENTORY_PAGE_SIZE) <= pos < ((page + 1) * INVENTORY_PAGE_SIZE): # range 0 ~ 44, 45 ~ 89
						idx = pos - (page * INVENTORY_PAGE_SIZE)
						self.inven.wndItem.SetCanMouseEventSlot(idx)

					if self.invenSpecial.GetInventoryType() == 0:
						if (item.SKILL_BOOK_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= pos < (item.SKILL_BOOK_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							idx = pos - (item.SKILL_BOOK_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCanMouseEventSlot(idx)

					if self.invenSpecial.GetInventoryType() == 1:
						if (item.UPGRADE_ITEMS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= pos < (item.UPGRADE_ITEMS_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							idx = pos - (item.UPGRADE_ITEMS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCanMouseEventSlot(idx)

					if self.invenSpecial.GetInventoryType() == 2:
						if (item.STONE_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= pos < (item.STONE_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							idx = pos - (item.STONE_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCanMouseEventSlot(idx)

					if self.invenSpecial.GetInventoryType() == 3:
						if (item.GIFT_BOX_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= pos < (item.GIFT_BOX_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
							idx = pos - (item.GIFT_BOX_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
							self.invenSpecial.wndItem.SetCanMouseEventSlot(idx)

					if app.NEW_SPECIAL_INV:
						if self.invenSpecial.GetInventoryType() == 4:
							if (item.ENCHANT_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= pos < (item.ENCHANT_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
								idx = pos - (item.ENCHANT_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
								self.invenSpecial.wndItem.SetCanMouseEventSlot(idx)

						if self.invenSpecial.GetInventoryType() == 5:
							if (item.POTS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= pos < (item.POTS_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
								idx = pos - (item.POTS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
								self.invenSpecial.wndItem.SetCanMouseEventSlot(idx)

			else:
				if self.inven:
					page = self.inven.GetInventoryPageIndex() # range 0 ~ 1

					if (page * INVENTORY_PAGE_SIZE) <= pos < ((page + 1) * INVENTORY_PAGE_SIZE): # range 0 ~ 44, 45 ~ 89
						idx = pos - (page * INVENTORY_PAGE_SIZE)
						self.inven.wndItem.SetCanMouseEventSlot(idx)

		self.priceInputBoard = None
		return True

	def OnOk(self):
		if not self.title:
			return

		if 0 == len(self.itemStock):
			return

		shop.BuildPrivateShop(self.title)
		self.Close()

	def OnClose(self):
		self.Close()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnOverInItem(self, slotIndex):
		if app.ENABLE_MYSHOP_DECO:
			if self.tooltipItem:
				slotIndex = self.__GetRealIndex(slotIndex)
				if self.itemStock.has_key(slotIndex):
					self.tooltipItem.SetPrivateShopBuilderItem(*self.itemStock[slotIndex] + (slotIndex,))
		else:
			if self.tooltipItem:
				if self.itemStock.has_key(slotIndex):
					self.tooltipItem.SetPrivateShopBuilderItem(*self.itemStock[slotIndex] + (slotIndex,))

	def OnOverOutItem(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	if app.WJ_ENABLE_TRADABLE_ICON:
		def CantTradableItem(self, slotIndex):
			itemIndex = player.GetItemIndex(slotIndex)

			if itemIndex:
				if app.ENABLE_SOUL_BIND_SYSTEM:
					if player.GetItemSealDate(player.INVENTORY, slotIndex) == -1 or player.GetItemSealDate(player.INVENTORY, slotIndex) > 0: #????? ???.
						return True

				if itemIndex == 50200:
					return True

				if player.IsAntiFlagBySlot(slotIndex, item.ANTIFLAG_GIVE) or player.IsAntiFlagBySlot(slotIndex, item.ANTIFLAG_MYSHOP):
					return True

			return False

		def BindInterface(self, interface):
			if self.interface:
				self.interface = proxy(interface)

		def OnTop(self):
			if not self.interface:
				return

			self.interface.SetOnTopWindow(player.ON_TOP_WND_PRIVATE_SHOP)
			self.interface.RefreshMarkInventoryBag()

		def SetInven(self, inven):
			if inven:
				self.inven = proxy(inven)

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			def SetSpecialInven(self, invenSpecial):
				if invenSpecial:
					self.invenSpecial = proxy(invenSpecial)

		def OnUpdate(self):
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

					if app.NEW_SPECIAL_INV:
						if self.invenSpecial.GetInventoryType() == 4:
							if (item.ENCHANT_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.ENCHANT_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
								lock_idx = i - (item.ENCHANT_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
								self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)

						if self.invenSpecial.GetInventoryType() == 5:
							if (item.POTS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE)) <= i < (item.POTS_INVENTORY_SLOT_START + (((special_page + 1) * SPECIAL_INVENTORY_PAGE_SIZE))):
								lock_idx = i - (item.POTS_INVENTORY_SLOT_START + (special_page * SPECIAL_INVENTORY_PAGE_SIZE))
								self.invenSpecial.wndItem.SetCantMouseEventSlot(lock_idx)


		def GetItemDataSocketValue(self, winType, SlotPos):
			for i in xrange(item.LIMIT_MAX_NUM):

				(limitType, limitValue) = item.GetLimit(i)
				if limitType == item.LIMIT_REAL_TIME or limitType == item.LIMIT_REAL_TIME_START_FIRST_USE or limitType == item.LIMIT_TIMER_BASED_ON_WEAR:
					return 0

			return player.GetItemMetinSocket(winType, SlotPos, 0)

	if app.ENABLE_CHEQUE_SYSTEM:
		def SetIsCashItem(self, bCashItem):
			self.IsCashItem = bCashItem

	if app.ENABLE_MYSHOP_DECO:
		def __SetMyShopDecoPosition(self):
			if localeinfo.IsARABIC():
				self.itemSlot.SetPosition(self.board_width - 12, 60)
				self.btnOk.SetPosition(self.board_width - 104, 380 - 33)
				self.btnClose.SetPosition(self.board_width - 21, 380 - 33)
			else:
				self.itemSlot.SetPosition(12, 60)
				self.btnOk.SetPosition(21, 380 - 33)
				self.btnClose.SetPosition(104, 380 - 33)

		def __SetDefaultShopDecoPosition(self):
			if localeinfo.IsARABIC():
				self.itemSlot.SetPosition(self.board_width - 12, 70)
				self.btnOk.SetPosition(self.board_width - 104, 380 - 40)
				self.btnClose.SetPosition(self.board_width - 21, 380 - 40)
			else:
				self.itemSlot.SetPosition(12, 70)
				self.btnOk.SetPosition(21, 380 - 40)
				self.btnClose.SetPosition(104, 380 - 40)

		def SetTabCount(self, tabCnt):
			self.tabCnt = tabCnt;

			if self.tabCnt >= 2:
				for btn in self.PrvShopTab:
					btn.Show()

				self.__SetMyShopDecoPosition()
			else:
				for btn in self.PrvShopTab:
					btn.Hide()

				self.__SetDefaultShopDecoPosition()

		def SetPrivateShopPage(self, page):
			if self.priceInputBoard:
				for tab in self.PrvShopTab:
					tab.SetUp()
				self.PrvShopTab[self.page].Down()
				return

			self.page = page

			for tab in self.PrvShopTab:
				tab.SetUp()

			self.PrvShopTab[page].Down()

			self.Refresh()

		def __GetRealIndex(self, i):
			return self.page * shop.SHOP_SLOT_COUNT + i

		def PrvShopTabRefresh(self) :
			self.page = 0

			for tab in self.PrvShopTab:
				tab.SetUp()

			self.PrvShopTab[self.page].Down()

if app.ENABLE_MYSHOP_DECO :
	class PrivateShopTitleBar(ui.ShopDecoTitle):
		def __init__(self, type):
			ui.ShopDecoTitle.__init__(self, type - 1, "UI_BOTTOM")

			self.Show()

			self.type = type
			self.vid = None
			self.__MakeTextLine()
			self.__CalcFontColor()

		def __del__(self):
			ui.ShopDecoTitle.__del__(self)
			self.textLine = None

		def __CalcFontColor(self):
			if self.type != 0 :
				import uiMyShopDecoration
				COLOR = int(uiMyShopDecoration.DECO_SHOP_TITLE_LIST[self.type - 1][2], 16)

				RED = (COLOR & 0xFF0000) >> 16
				GREEN = (COLOR & 0x00FF00) >> 8
				BLUE = COLOR & 0x0000FF

				self.textLine.SetFontColor(float(RED) / 255.0, float(GREEN) / 255.0, float(BLUE) / 255.0)

		def __MakeTextLine(self):
			self.textLine = ui.TextLine()
			self.textLine.SetParent(self)
			self.textLine.SetWindowHorizontalAlignCenter()
			self.textLine.SetWindowVerticalAlignCenter()
			self.textLine.SetHorizontalAlignCenter()
			self.textLine.SetVerticalAlignCenter()
			self.textLine.Show()

		def Open(self, vid, text):
			self.vid = vid

			self.textLine.SetText(text)
			width = max(32, len(text)*6 + 20*2)
			self.SetSize(width, 32)

			self.Show()

			g_privateShopAdvertisementBoardDict[vid] = self

		def OnMouseLeftButtonUp(self):
			if not self.vid:
				return

			net.SendOnClickPacket(self.vid)

			return True

		def OnUpdate(self):
			if not self.vid:
				return

			if systemSetting.IsShowSalesText():
				self.Show()
				x, y = chr.GetProjectPosition(self.vid, 220)
				width = x - self.GetWidth()/2
				height = y - self.GetHeight()/2
				self.SetPosition(width, height)
			else:
				for key in g_privateShopAdvertisementBoardDict.keys():
					if player.GetMainCharacterIndex() == key:
						title_bar = g_privateShopAdvertisementBoardDict[key]

						title_bar.Show()

						x, y = chr.GetProjectPosition(player.GetMainCharacterIndex(), 220)

						width = x - title_bar.GetWidth()/2
						height = y - title_bar.GetHeight()/2

						title_bar.SetPosition(width, height)
					else:
						title_bar = g_privateShopAdvertisementBoardDict[key]
						title_bar.Hide()
