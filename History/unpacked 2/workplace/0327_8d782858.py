# coding: latin_1

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import player
import net

import grp
import mousemodule
import offlineshop
import ui
import item
import dbg
import uicommon
import uitooltip
import localeinfo
import ime

import constinfo
import time
import chat

# >>> SECTION BEGIN offlineshop search UI redesign: swap in the new window module <<<
# import uishopsearch
import uishopsearch_new as uishopsearch
# >>> SECTION END <<<
import uiofflineshop_history
import uiofflineshop_deco
if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget
import math
from operator import truediv
from _weakref import proxy

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

try:
	app.WJ_ENABLE_TRADABLE_ICON
except Exception:
	app.WJ_ENABLE_TRADABLE_ICON = False

PAGE_MYSHOP = 0
PAGE_BUILDER = 1
PAGE_SAFEBOX = 2
PAGE_SHOP = 3

OFFLINESHOP_SLOT_COUNT = offlineshop.OFFLINESHOP_SLOTS_PAGE_COUNT
CACHE_ITEMS_ID = {}

PATH_SHOP = "cream/"
PATH_ROOT = "cream/shopeditor/"
PATH_ROOT_BUILD = "cream/shopbuilder/"
PATH_ROOT_SEARCH = "cream/searchshop/"

COLOR_TEXT_SHORTCUT = grp.GenerateColor(1.0,1.0,0.5,1.0)

PAGE_COUNT = 2

DEFAULT_PRICE = 100
MAX_PRICE = 99999999999

FOCUS_PRICE = 1

if app.USE_OFFLINESHOP_PRICE_AVERAGE:
	FOCUS_AVERAGE = 2

if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
	PAGE_COUNT += offlineshop.OFFLINESHOP_LOCKED_PAGES

def IsEditOrBuildMode():
	interface = offlineshop.GetOfflineshopBoard()
	if not interface:
		return False
	
	return interface.IsBuildingShop()

def IsBuildingShop():
	interface = offlineshop.GetOfflineshopBoard()
	if not interface:
		return False
	
	return interface.IsBuildingShop()

def IsSaleSlot(win,slot):
	interface = offlineshop.GetOfflineshopBoard()
	if not interface:
		return False

	return False

def MakeRadioButton(parent, x, y, path, up, over, down):
	button = ui.RadioButton()
	button.SetParent(parent)
	button.SetPosition(x, y)
	button.SetUpVisual(path + up)
	button.SetOverVisual(path + over)
	button.SetDownVisual(path + down)
	button.Show()
	return button

class OfflineShopDormantDialog(ui.BoardWithTitleBar):
	# Themed 'your shop is paused' prompt (replaces the plain uiCommon.QuestionDialog).
	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		self.reopenEvent = None
		self.closeShopEvent = None
		self.laterEvent = None
		self.__BuildWindow()

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def __BuildWindow(self):
		self.SetSize(360, 142)
		self.AddFlag("float")
		self.SetTitleName(localeinfo.OFFLINESHOP_DORMANT_TITLE)
		self.SetCloseEvent(ui.__mem_func__(self.OnLater))

		self.message = ui.TextLine()
		self.message.SetParent(self)
		self.message.SetWindowHorizontalAlignCenter()
		self.message.SetHorizontalAlignCenter()
		self.message.SetPosition(0, 48)
		self.message.Show()

		self.btnDiscard = ui.MakeButtonNew(self, 18, 96, localeinfo.OFFLINESHOP_DORMANT_CLOSE, PATH_ROOT_BUILD, "btn_norm.png", "btn_hover.png", "btn_down.png")
		self.btnDiscard.SetEvent(ui.__mem_func__(self.OnCloseShop))

		self.btnLater = ui.MakeButtonNew(self, 129, 96, localeinfo.OFFLINESHOP_DORMANT_LATER, PATH_ROOT_BUILD, "btn_norm.png", "btn_hover.png", "btn_down.png")
		self.btnLater.SetEvent(ui.__mem_func__(self.OnLater))

		self.btnReopen = ui.MakeButtonNew(self, 240, 96, localeinfo.OFFLINESHOP_DORMANT_REOPEN, PATH_ROOT_BUILD, "btn_norm.png", "btn_hover.png", "btn_down.png")
		self.btnReopen.SetEvent(ui.__mem_func__(self.OnReopen))

	def SetText(self, text):
		self.message.SetText(text)

	def SetReopenEvent(self, event):
		self.reopenEvent = event

	def SetCloseShopEvent(self, event):
		self.closeShopEvent = event

	def SetLaterEvent(self, event):
		self.laterEvent = event

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.Hide()

	def OnReopen(self):
		if self.reopenEvent:
			self.reopenEvent()

	def OnCloseShop(self):
		if self.closeShopEvent:
			self.closeShopEvent()

	def OnLater(self):
		if self.laterEvent:
			self.laterEvent()

class HistoryPopupWindow(ui.ScriptWindow):
	isLoaded = 0
	showTime = 3

	boardWidth = 0
	boardHeight = 0

	toolTipItem = None

	def OnOverIn(self):
		if not self.toolTipItem:
			self.toolTipItem = uitooltip.ItemToolTip()

		if self.toolTipItem:
			self.toolTipItem.ClearToolTip()

			if self.itemsDict.has_key(self.kB):
				sockets = [self.itemsDict[self.kB]["socket"][i] for i in xrange(player.METIN_SOCKET_MAX_NUM)]
				attrs = [(self.itemsDict[self.kB]["attr"][i]["type"], self.itemsDict[self.kB]["attr"][i]["value"]) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

				rands = []
				if app.ENABLE_APPLY_RANDOM_SHOP:
					rands = [(self.itemsDict[self.kB]["rand"][i]["type"], self.itemsDict[self.kB]["rand"][i]["value"], self.itemsDict[self.kB]["rand"][i]["path"]) for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]

				enchants = []
				if app.USE_ENCHANT_COSTUMES:
					enchants = [(self.itemsDict[self.kB]["enchant"][i]["type"], self.itemsDict[self.kB]["enchant"][i]["value"], self.itemsDict[self.kB]["enchant"][i]["time"]) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]

				trans = 0
				if app.ENABLE_CHANGE_LOOK_SYSTEM:
					trans = self.itemsDict[self.kB]["trans"]
				if app.ENABLE_SET_ITEM:
					setItem = 0
					setItem = self.itemsDict[self.kB]["setItem"]

				self.toolTipItem.AddItemData(self.itemsDict[self.kB]["vnum"], sockets, attrs, None, 0, 0, player.INVENTORY, -1, None, apply_random_list=rands, set_value=0, transmutation=trans, enchantList=enchants,iSetValue=setItem)
			else:
				self.toolTipItem.HideToolTip()

	def OnOverOut(self):
		if self.toolTipItem:
			self.toolTipItem.HideToolTip()

	def __LoadDialog(self):
		if self.isLoaded:
			return

		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/offlineshop_historypopupwindow.py")

		self.kA = 1
		self.kB = 0
		self.waitTime = 0
		self.itemsDict = {}

		import wndMgr
		self.SetPosition(-5, (wndMgr.GetScreenHeight() - self.GetHeight()) / 2)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : (-5, (Expr("SCREEN_HEIGHT") - self.GetHeight()) / 2)})

		self.boardWidth = self.GetWidth()
		self.boardHeight = self.GetHeight()

		self.descText1 = self.GetChild("ui_desc1_text")
		self.descText2 = self.GetChild("ui_desc2_text")
		self.descText3 = self.GetChild("ui_desc3_text")

		self.itemIcon = self.GetChild("ui_board_item_icon")
		self.itemIcon.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverIn))
		self.itemIcon.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOut))

		self.isCancel = 0
		self.cancelBtn = self.GetChild("ui_cancel_btn")
		self.cancelBtn.SetEvent(ui.__mem_func__(self.__OnCancel))

		self.board = self.GetChild("ui_board")
		self.board.Hide()

		self.SetSize(0, 0)

	def Destroy(self):
		self.isCancel = 0

		self.kA = 1
		self.kB = 0
		self.waitTime = 0
		self.itemsDict = {}

		self.descText1 = None
		self.descText2 = None
		self.descText3 = None
		self.itemIcon = None

		if self.cancelBtn:
			self.cancelBtn.SetEvent(None)
			self.cancelBtn = None

		self.board = None

		if self.toolTipItem:
			self.toolTipItem.ClearToolTip()
			del self.toolTipItem

		self.ClearDictionary()

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__LoadDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Build(self, k):
		itemVnum = self.itemsDict[k]["vnum"]
		if not itemVnum:
			return False

		self.itemIcon.UnloadImage()

		item.SelectItem(itemVnum)
		self.itemIcon.LoadImage(item.GetIconImageFileName())

		self.descText2.SetText(localeinfo.OFFLINESHOP_HISTORY_POPUP2 % (self.itemsDict[k]["count"], item.GetItemName()))

		buyerName = self.itemsDict[k]["who"]

		expired = 0
		if buyerName == "_sys":# and self.itemsDict[k]["expiration"] != 0:
			expired = 1

		if expired == 1:
			if self.descText1.IsShow():
				self.descText1.Hide()

			self.descText3.SetText(localeinfo.OFFLINESHOP_HISTORY_POPUP4)
		else:
			if not self.descText1.IsShow():
				self.descText1.Show()

			self.descText1.SetText(localeinfo.OFFLINESHOP_HISTORY_POPUP1 % (buyerName))
			self.descText3.SetText(localeinfo.OFFLINESHOP_HISTORY_POPUP3 % (localeinfo.NumberToStringDotted(self.itemsDict[k]["price"]), localeinfo.MONETARY_UNIT0))

		self.kB = k

		if self.toolTipItem and self.toolTipItem.IsShow():
			self.toolTipItem.OnOverIn()

		return True

	def Add(self, itemDict):
		self.itemsDict[self.kA] = itemDict
		self.kA += 1

		if not self.board.IsShow():
			if self.Build(list(self.itemsDict.keys())[0]):
				self.itemsDict[self.kB]["limit"] = app.GetGlobalTimeStamp() + self.showTime

				self.waitTime = 0

				self.SetSize(self.boardWidth, self.boardHeight)
				self.board.Show()
				self.Show()

	def __OnCancel(self):
		self.isCancel = 1
		del self.itemsDict[self.kB]

		self.kB = 0

		self.board.Hide()
		self.SetSize(0, 0)

		self.waitTime = 0

		self.isCancel = 0

	def Close(self):
		if self.toolTipItem:
			self.toolTipItem.ClearToolTip()
			self.toolTipItem.HideToolTip()

		self.Hide()

	def OnUpdate(self):
		if len(self.itemsDict) == 0:
			self.Close()
		else:
			if self.isCancel:
				return

			timeNow = app.GetGlobalTimeStamp()
			if self.waitTime != 0:
				if timeNow > self.waitTime:
					self.itemsDict[self.kB]["limit"] = timeNow + self.showTime

					self.SetSize(self.boardWidth, self.boardHeight)
					self.board.Show()

					self.waitTime = 0
			elif self.kB != 0:
				if timeNow > self.itemsDict[self.kB]["limit"]:
					del self.itemsDict[self.kB]

					self.kB = 0

					self.board.Hide()
					self.SetSize(0, 0)
			else:
				dictLen = len(self.itemsDict)
				if dictLen == 0:
					self.Close()
				else:
					if self.Build(list(self.itemsDict.keys())[0]):
						self.itemsDict[self.kB]["limit"] = timeNow + self.showTime
						self.waitTime = timeNow + 1

class OfflineShopRenewal(ui.ScriptWindow):
	wndHistoryPopup = None

	if app.USE_OFFLINESHOP_PRICE_AVERAGE:
		def Recv_PriceAverage(self, vnum, price):
			if self.wndOffShop:
				self.wndOffShop.Recv_PriceAverage(vnum, price)

	if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
		def Player_RefreshItemSlot(self):
			if self.wndOffShop:
				if self.wndOffShop.wBoard[PAGE_BUILDER].IsShow() or\
					self.wndOffShop.wBoard[PAGE_MYSHOP].IsShow():
					self.wndOffShop.RefreshItemSlot()

	def __init__(self, wndBind):
		ui.ScriptWindow.__init__(self)
		
		offlineshop.SetOfflineshopBoard(self)

		self.ShopSafeboxItems = []
		self.ShopSafeboxValuteAmount = 0
		self.ShopSafeboxValuteText = None

		self.ShopItemForSale = []
		self.soldItemsDict = {}
		self.soldItemDict = {}

		self.ShopOpenInfo = {}
		
		self.wndOffShop = wndBind

	def ShopFilterResult(self , size, total = None, page = None):
		self.wndOffShop.wndSearchShop.ShopFilterResult(size, total, page)

	def ShopFilterResultItem_Alloc(self):
		self.wndOffShop.wndSearchShop.ShopFilterResultItem_Alloc()

	def ShopFilterResultItem_SetValue( self,  key, index, *args):
		self.wndOffShop.wndSearchShop.ShopFilterResultItem_SetValue(key, index, *args)

	def ShopFilterResultItem_SetDict(self, index, d):
		self.wndOffShop.wndSearchShop.ShopFilterResultItem_SetDict(index, d)

	def ShopFilterResult_Show(self):
		self.wndOffShop.wndSearchShop.ShopFilterResult_Show()

	def SearchFilter_BuyFromSearch(self, ownerid, itemid):
		self.wndOffShop.wndSearchShop.SearchFilter_BuyFromSearch(ownerid, itemid)

	def OnPickedShop(self, _w, vid):
		offlineshop.SendOfflineshopOnClickShopEntity(vid)
		# self.BINARY_EnableRefreshSymbol()

	def IsBuildingShop(self):
		if not self.wndOffShop or\
			not self.wndOffShop.IsShow():
			return False
		
		if self.wndOffShop.wBoard[PAGE_BUILDER].IsShow() or\
			self.wndOffShop.wBoard[PAGE_MYSHOP].IsShow():
			return True
		
		return False

	def ShopBuilding_AddItem(self, win, slot):
		itemVnum = player.GetItemIndex(win, slot)
		if not itemVnum:
			return

		if win == player.INVENTORY and player.IsEquipmentSlot(slot):
			return

		if self.IsForSaleSlot(win, slot):
			return

		item.SelectItem(itemVnum)
		_, size = item.GetItemSize()

		page, pos = self.wndOffShop.GetEmptyPosition(size)
		if pos < 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_NO_EMPTY_SLOT)
			return

		if self.__IsSaleableSlot(win, slot):
			self.wndOffShop.OpenInputPriceDialog(win, slot, page, pos, False, False)

	def IsForSaleSlot(self,win,slot):
		if self.wndOffShop.IsShow() == False:
			return
		
		if self.wndOffShop.wBoard[PAGE_BUILDER].IsShow():
			if self.wndOffShop.priceInputDlg:
				if self.wndOffShop.priceInputDlg.sourceWindowType == win and self.wndOffShop.priceInputDlg.sourceSlotPos == slot:
					return True

			for page in xrange(4):
				for privatePos, (itemWindowType, itemSlotIndex, priceInfo) in self.wndOffShop.itemStockBuilder[page].items():
					if itemWindowType == win and itemSlotIndex == slot:
						return True
		elif self.wndOffShop.wBoard[PAGE_MYSHOP].IsShow():
			if self.wndOffShop.priceInputDlg:
				if self.wndOffShop.priceInputDlg.sourceWindowType == win and self.wndOffShop.priceInputDlg.sourceSlotPos == slot:
					return True

		return False

	def __IsSaleableSlot(self, win , pos):
		if win == player.INVENTORY:
			if player.IsEquipmentSlot(pos):
				return False

		if self.IsBuildingShop() and self.IsForSaleSlot(win, pos):
			return False

		if not win in (player.INVENTORY, player.DRAGON_SOUL_INVENTORY):
			return False

		itemIndex = player.GetItemIndex(win,pos)
		if itemIndex == 0:
			return False

		item.SelectItem(itemIndex)
		if item.IsAntiFlag(item.ITEM_ANTIFLAG_MYSHOP) or item.IsAntiFlag(item.ITEM_ANTIFLAG_GIVE):
			return False

		return True

	def Destroy(self):
		if self.wndHistoryPopup:
			self.wndHistoryPopup.Destroy()
			del self.wndHistoryPopup
			self.wndHistoryPopup = None

		self.ClearDictionary()

		self.wndOffShop = None
		offlineshop.SetOfflineshopBoard(None)

	def OpenShop( self, owner_id, duration, count, name):
		self.ShopItemForSale = []

		self.ShopOpenInfo["owner_id"]	= owner_id
		self.ShopOpenInfo["duration"]	= duration
		self.ShopOpenInfo["count"]		= count
		self.ShopOpenInfo["name"]		= name
		self.ShopOpenInfo["my_shop"]	= False

	def OpenShopItem_Alloc(self):
		self.ShopItemForSale.append({})

	def OpenShopItem_SetDict(self, index, d):
		# P5: C++ delivers the whole item as one dict (same shape OpenShopItem_SetValue builds).
		self.ShopItemForSale.append(d)

	def OpenShopItem_SetValue( self, key,	index,	*args):
		if key == "id":
			self.ShopItemForSale[index][key] = args[0]

		elif key == "vnum" or key == 'trans' or key == 'setItem':
			self.ShopItemForSale[index][key] = args[0]

		elif app.ENABLE_EQUIPMENT_RESTRICTION and key == "restrict":
			self.ShopItemForSale[index][key] = (args[0], args[1])

		elif key == "count":
			self.ShopItemForSale[index][key] = args[0]

		elif key == "attr":
			if not key in self.ShopItemForSale[index]:
				self.ShopItemForSale[index][key] = {}

			attr_index = args[0]
			attr_type  = args[1]
			attr_value = args[2]

			self.ShopItemForSale[index][key][attr_index] = {}
			self.ShopItemForSale[index][key][attr_index]["type"]  = attr_type
			self.ShopItemForSale[index][key][attr_index]["value"] = attr_value

		elif app.ENABLE_APPLY_RANDOM_SHOP and key=="rand":
			if not key in self.ShopItemForSale[index]:
				self.ShopItemForSale[index][key] = {}

			rand_index=args[0]
			rand_type=args[1]
			rand_value=args[2]
			rand_path=args[3]

			self.ShopItemForSale[index][key][rand_index] = {}
			self.ShopItemForSale[index][key][rand_index]["type"]=rand_type
			self.ShopItemForSale[index][key][rand_index]["value"]=rand_value
			self.ShopItemForSale[index][key][rand_index]["path"]=rand_path


		elif key == "socket":
			if not key in self.ShopItemForSale[index]:
				self.ShopItemForSale[index][key] = {}

			socket_index = args[0]
			socket_val	 = args[1]

			self.ShopItemForSale[index][key][socket_index] = socket_val

		elif key == "price":
			self.ShopItemForSale[index][key] = args[0]
		elif app.USE_ENCHANT_COSTUMES and key=="enchant":
			if not key in self.ShopItemForSale[index]:
				self.ShopItemForSale[index][key] = {}
			
			enchant_index=args[0]
			enchant_type=args[1]
			enchant_value=args[2]
			enchant_time=args[3]
			
			self.ShopItemForSale[index][key][enchant_index] = {}
			self.ShopItemForSale[index][key][enchant_index]["type"]=enchant_type
			self.ShopItemForSale[index][key][enchant_index]["value"]=enchant_value
			self.ShopItemForSale[index][key][enchant_index]["time"]=enchant_time

	def OpenShop_End(self):
		self.wndOffShop.RefreshOpenShopPage()
		
		if not self.wndOffShop.IsShow():
			self.wndOffShop.Show()

	# P2 item deltas: mutate the cached ShopItemForSale + reuse RefreshOpenShopPage (a client guests one shop at a time, so a received delta is always for the open shop).
	def ShopDeltaItem_AddBegin(self):
		self.ShopItemForSale.append({})
		self._deltaIdx = len(self.ShopItemForSale) - 1

	def ShopDeltaItem_SetValue(self, key, *args):
		self.OpenShopItem_SetValue(key, self._deltaIdx, *args)

	# render the right view for THIS client: owner stays on MyShop, guest on the buyer page
	def _DeltaRefresh(self):
		if self.ShopOpenInfo.get("my_shop"):
			self.wndOffShop.RefreshMyShopPage()
		else:
			self.wndOffShop.RefreshOpenShopPage()

	def ShopDeltaItem_AddEnd(self):
		self._DeltaRefresh()

	def ShopDeltaItem_Edit(self, itemId, price):
		for it in self.ShopItemForSale:
			if it.get("id") == itemId:
				it["price"] = price
				break
		self._DeltaRefresh()

	def ShopDeltaItem_Remove(self, itemId):
		self.ShopItemForSale = [it for it in self.ShopItemForSale if it.get("id") != itemId]
		self._DeltaRefresh()

	def ShopGone(self, ownerId):
		if self.ShopOpenInfo.get("owner_id") == ownerId:
			self.ShopItemForSale = []
			self.wndOffShop.RefreshOpenShopPage()

	def OpenShopOwner_Start( self, owner_id, duration , count , name):
		self.ShopItemForSale = []

		self.ShopOpenInfo["owner_id"]	= owner_id
		self.ShopOpenInfo["duration"]	= duration
		self.ShopOpenInfo["count"]		= count
		self.ShopOpenInfo["name"]		= name
		self.ShopOpenInfo["my_shop"]	= True
		if self.wndOffShop:
			self.wndOffShop.hasLiveShop = True

	def OpenShopOwner_End(self):
		self.wndOffShop.RefreshMyShopPage()

		if not self.wndOffShop.IsShow():
			self.wndOffShop.Show()

	def StartAppendHistory(self):
		self.soldItemsDict = {}

	def AppendHistory(self, k, v, *args):
		if not self.soldItemsDict.has_key(k):
			self.soldItemsDict[k] = {}

		if v == "attr":
			if not self.soldItemsDict[k].has_key(v):
				self.soldItemsDict[k][v] = {}

			self.soldItemsDict[k][v][args[0]] = {}
			self.soldItemsDict[k][v][args[0]]["type"] = args[1]
			self.soldItemsDict[k][v][args[0]]["value"] = args[2]


		elif app.ENABLE_APPLY_RANDOM_SHOP and v == "rand":
			if not self.soldItemsDict[k].has_key(v):
				self.soldItemsDict[k][v] = {}

			self.soldItemsDict[k][v][args[0]] = {}
			self.soldItemsDict[k][v][args[0]]["type"] = args[1]
			self.soldItemsDict[k][v][args[0]]["value"] = args[2]
			self.soldItemsDict[k][v][args[0]]["path"] = args[3]

		elif app.USE_ENCHANT_COSTUMES and v == "enchant":
			if not self.soldItemsDict[k].has_key(v):
				self.soldItemsDict[k][v] = {}

			self.soldItemsDict[k][v][args[0]] = {}
			self.soldItemsDict[k][v][args[0]]["type"] = args[1]
			self.soldItemsDict[k][v][args[0]]["value"] = args[2]
			self.soldItemsDict[k][v][args[0]]["time"] = args[3]
		elif v == "socket":
			if not self.soldItemsDict[k].has_key(v):
				self.soldItemsDict[k][v] = {}

			self.soldItemsDict[k][v][args[0]] = args[1]
		else:
			self.soldItemsDict[k][v] = args[0]

	def EndAppendHistory(self):
		if self.wndOffShop:
			wndHistory = self.wndOffShop.wndHistory
			if wndHistory:
				wndHistory.itemsDict = self.soldItemsDict

				wndHistory.Open(True)

		self.soldItemsDict = {}

	def StartAppendHistoryLive(self):
		self.soldItemDict = {}

	def AppendHistoryLive(self, v, *args):
		if v == "attr":
			if not self.soldItemDict.has_key(v):
				self.soldItemDict[v] = {}

			self.soldItemDict[v][args[0]] = {}
			self.soldItemDict[v][args[0]]["type"] = args[1]
			self.soldItemDict[v][args[0]]["value"] = args[2]

		elif app.ENABLE_APPLY_RANDOM_SHOP and v == "rand":
			if not self.soldItemDict.has_key(v):
				self.soldItemDict[v] = {}

			self.soldItemDict[v][args[0]] = {}
			self.soldItemDict[v][args[0]]["type"] = args[1]
			self.soldItemDict[v][args[0]]["value"] = args[2]
			self.soldItemDict[v][args[0]]["path"] = args[3]

		elif app.USE_ENCHANT_COSTUMES and v == "enchant":
			if not self.soldItemDict.has_key(v):
				self.soldItemDict[v] = {}

			self.soldItemDict[v][args[0]] = {}
			self.soldItemDict[v][args[0]]["type"] = args[1]
			self.soldItemDict[v][args[0]]["value"] = args[2]
			self.soldItemDict[v][args[0]]["time"] = args[3]
		elif v == "socket":
			if not self.soldItemDict.has_key(v):
				self.soldItemDict[v] = {}

			self.soldItemDict[v][args[0]] = args[1]
		else:
			self.soldItemDict[v] = args[0]

	def EndAppendHistoryLive(self):
		if self.wndOffShop:
			wndHistory = self.wndOffShop.wndHistory
			if wndHistory:
				wndHistory.Rebuild(self.soldItemDict)

		if not self.wndHistoryPopup:
			self.wndHistoryPopup = HistoryPopupWindow()

		if self.wndHistoryPopup:
			self.wndHistoryPopup.Add(self.soldItemDict)

		self.soldItemDict = {}

	def OpenShopOwnerItem_Alloc(self):
		self.ShopItemForSale.append({})

	def OpenShopOwnerItem_SetDict(self, index, d):
		# P5: C++ delivers the whole MyShop item as one dict (same shape OpenShopOwnerItem_SetValue builds).
		self.ShopItemForSale.append(d)

	def OpenShopOwnerItem_SetValue( self, key, index, *args):
		if key == "id":
			self.ShopItemForSale[index][key] = args[0]

		elif key == "vnum" or key == 'trans' or key == 'setItem':
			self.ShopItemForSale[index][key] = args[0]

		elif app.ENABLE_EQUIPMENT_RESTRICTION and key == "restrict":
			self.ShopItemForSale[index][key] = (args[0], args[1])

		elif key == "count":
			self.ShopItemForSale[index][key] = args[0]

		elif key == "attr":
			if not key in self.ShopItemForSale[index]:
				self.ShopItemForSale[index][key] = {}

			attr_index = args[0]
			attr_type  = args[1]
			attr_value = args[2]

			self.ShopItemForSale[index][key][attr_index] = {}
			self.ShopItemForSale[index][key][attr_index]["type"]  = attr_type
			self.ShopItemForSale[index][key][attr_index]["value"] = attr_value

		elif app.ENABLE_APPLY_RANDOM_SHOP and key == "rand":
			if not key in self.ShopItemForSale[index]:
				self.ShopItemForSale[index][key] = {}

			rand_index=args[0]
			rand_type=args[1]
			rand_value=args[2]
			rand_path=args[3]

			self.ShopItemForSale[index][key][rand_index] = {}
			self.ShopItemForSale[index][key][rand_index]["type"]=rand_type
			self.ShopItemForSale[index][key][rand_index]["value"]=rand_value
			self.ShopItemForSale[index][key][rand_index]["path"]=rand_path

		elif key == "socket":
			if not key in self.ShopItemForSale[index]:
				self.ShopItemForSale[index][key] = {}

			socket_index = args[0]
			socket_val	 = args[1]

			self.ShopItemForSale[index][key][socket_index] = socket_val

		elif key == "price":
			self.ShopItemForSale[index][key] = args[0]
		elif app.USE_ENCHANT_COSTUMES and key=="enchant":
			if not key in self.ShopItemForSale[index]:
				self.ShopItemForSale[index][key] = {}
			
			enchant_index=args[0]
			enchant_type=args[1]
			enchant_value=args[2]
			enchant_time=args[3]
			
			self.ShopItemForSale[index][key][enchant_index] = {}
			self.ShopItemForSale[index][key][enchant_index]["type"]=enchant_type
			self.ShopItemForSale[index][key][enchant_index]["value"]=enchant_value
			self.ShopItemForSale[index][key][enchant_index]["time"]=enchant_time

	def OpenShopOwnerNoShop(self):
		if self.wndOffShop:
			self.wndOffShop.hasLiveShop = False
		for v in self.wndOffShop.wBoard.values():
			v.Hide()

		self.wndOffShop.ResetCreateShopPage()
		
		if not self.wndOffShop.IsShow():
			self.wndOffShop.Show()

	def ShopSafebox_Clear(self):
		self.ShopSafeboxItems = []

	def ShopSafebox_SetValutes(self, yang):
		self.ShopSafeboxValuteAmount = yang
		self.wndOffShop.wndTextYang.SetText("|cFF20B2AA" + localeinfo.NumberToMoneyString(yang))

	def ShopSafebox_AllocItem(self):
		self.ShopSafeboxItems.append({})

	def ShopSafebox_SetDict(self, d):
		# P5: C++ delivers the whole safebox item as one dict (same shape ShopSafebox_SetValue builds).
		self.ShopSafeboxItems.append(d)

	def ShopSafebox_SetValue(self, key , *args):
		elm = self.ShopSafeboxItems[-1]

		if key in ("id", "vnum", "count", 'trans', 'setItem'):
			elm[key] = args[0]

		elif app.ENABLE_EQUIPMENT_RESTRICTION and key == "restrict":
			elm[key] = (args[0], args[1])

		elif key == "socket":
			if not key in elm:
				elm[key] = [0 for x in xrange(player.METIN_SOCKET_MAX_NUM)]
			elm[key][args[0]] = args[1]

		elif key in ("attr_type", "attr_value"):
			if not 'attr' in elm:
				elm['attr'] = {}

			if not args[0] in elm['attr']:
				elm['attr'][args[0]] = {}

			elm['attr'][args[0]][key.replace('attr_','')] = args[1]


		elif app.ENABLE_APPLY_RANDOM_SHOP and key in ("rand_type","rand_value","rand_path"):
			if not "rand" in elm:
				elm["rand"] = {}
			
			if not args[0] in elm["rand"]:
				elm["rand"][args[0]] = {}
			
			elm["rand"][args[0]][key.replace('rand_','')] = args[1]


		elif app.USE_ENCHANT_COSTUMES and key in ("enchant_type","enchant_value","enchant_time"):
			if not "enchant" in elm:
				elm["enchant"] = {}
			
			if not args[0] in elm["enchant"]:
				elm["enchant"][args[0]] = {}
			
			elm["enchant"][args[0]][key.replace('enchant_','')] = args[1]

	def ShopSafebox_RefreshEnd(self):
		self.wndOffShop.RefreshSafeboxPage()

class MoneyInputDialogNew(ui.ScriptWindow):
	PATH_ROOT = "cream/shopseller/"
	isLoaded = 0

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__LoadDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.itemVnum = 0
		self.itemCount = 0

		self.sourceWindowType = -1
		self.sourceSlotPos = -1
		self.targetSlotPos = -1
		self.page = -1
		self.CurrentPageGrid = False
		self.isEditMode = False

		if self.acceptButton:
			self.acceptButton.SetEvent(None)
			self.acceptButton = None

		if self.cancelButton:
			self.cancelButton.SetEvent(None)
			self.cancelButton = None

		if self.taxButton:
			self.taxButton.SetEvent(None)
			self.taxButton = None

		if self.inputValue:
			if app.USE_OFFLINESHOP_PRICE_AVERAGE:
				self.inputValue.SetTabEvent(None)

			self.inputValue.OnIMEReturn = None
			self.inputValue.OnPressEscapeKey = None
			self.inputValue = None

		self.itemBoardTitle = None
		self.boardSellIcon = None
		self.board = None
		self.price = 0
		self.old_price = 0
		self.fee = 0
		self.total_price = 0

		if app.USE_OFFLINESHOP_STACK_OPTION:
			self.firstOptionDesc = None
			self.equalStackBtn = None
			self.itemSize = 0

		if app.USE_OFFLINESHOP_PRICE_AVERAGE:
			if self.avgInput:
				self.avgInput.SetTabEvent(None)
				self.avgInput.OnIMEReturn = None
				self.avgInput.OnPressEscapeKey = None
				self.avgInput = None

			self.lastButton = -1
			self.origPrice = 0
			self.avgBtnsDict = {}
			self.averagePrice = 0
			self.averagePriceText = None

		self.afterTaxPrice = None

		self.ClearDictionary()

	def __LoadDialog(self):
		if self.isLoaded:
			return

		self.isLoaded = 1

		self.itemVnum = 0
		self.itemCount = 0

		self.sourceWindowType = -1
		self.sourceSlotPos = -1
		self.targetSlotPos = -1
		self.page = -1
		self.CurrentPageGrid = False
		self.isEditMode = False

		self.price = 0
		self.old_price = 0
		self.fee = 0

		if app.USE_OFFLINESHOP_PRICE_AVERAGE:
			self.averagePrice = 0

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/moneyinputdialog_new.py")

		self.board = self.GetChild("ui_board")
		self.acceptButton = self.GetChild("ui_accept_btn")
		self.cancelButton = self.GetChild("ui_cancel_btn")
		self.itemBoardTitle = self.GetChild("ui_itemboard_title")
		self.boardSellIcon = self.GetChild("ui_board_sell_icon")
		self.inputValue = self.GetChild("ui_input_value")

		if app.USE_OFFLINESHOP_STACK_OPTION:
			self.firstOptionDesc = self.GetChild("ui_board_option1_desc")
			self.itemSize = 0
			self.equalStackBtn = self.GetChild("ui_board_option1_tick")
		else:
			self.GetChild("ui_board_option1").Hide()

		if app.USE_OFFLINESHOP_PRICE_AVERAGE:
			self.averagePriceText = self.GetChild("ui_average_price")

			self.lastButton = -1
			self.origPrice = 0

			self.avgBtnsDict = {}
			self.avgBtnsDict[0] = self.GetChild("ui_board_option2_tick")
			self.avgBtnsDict[1] = self.GetChild("ui_board_option3_tick")
			self.avgBtnsDict[2] = self.GetChild("ui_board_option4_tick")

			self.avgInput = self.GetChild("ui_board_option4_input")
			self.avgInput.SetText("0")
			self.avgInput.OnIMEUpdate = ui.__mem_func__(self.__OnAvgValueUpdate)
			self.avgInput.SetTabEvent(ui.__mem_func__(self.SetFocusPrice))
		else:
			self.GetChild("ui_average_price").Hide()
			self.GetChild("ui_board_option2").Hide()
			self.GetChild("ui_board_option3").Hide()
			self.GetChild("ui_board_option4").Hide()

		self.afterTaxPrice = self.GetChild("ui_bg_aftertext_text")
		self.taxButton = self.GetChild("ui_tax_button")

		self.inputValue.SetText("0")
		self.inputValue.OnIMEUpdate = ui.__mem_func__(self.__OnValueUpdate)
		self.inputValue.OnPressEscapeKey = ui.__mem_func__(self.OnPressEscapeKey)

		if app.USE_OFFLINESHOP_PRICE_AVERAGE:
			self.inputValue.SetTabEvent(ui.__mem_func__(self.SetFocusAvg))

		if app.USE_OFFLINESHOP_PRICE_AVERAGE:
			for k, v in self.avgBtnsDict.items():
				v.SetToggleUpEvent(ui.__mem_func__(self.__OnPressAvgBtn), k, True)
				v.SetToggleDownEvent(ui.__mem_func__(self.__OnPressAvgBtn), k, False)

		self.taxButton.SetEvent(ui.__mem_func__(self.__OnPressTaxButton))

	def SetData(self, vnum, count):
		self.itemVnum = vnum
		self.itemCount = count

		if app.USE_OFFLINESHOP_STACK_OPTION:
			self.itemSize = 0

	def ClearPrice(self):
		self.price = 0
		self.old_price = 0
		self.fee = 0

	def SetAcceptEvent(self, event):
		self.acceptButton.SetEvent(event)
		self.inputValue.OnIMEReturn = event

		if app.USE_OFFLINESHOP_PRICE_AVERAGE:
			self.avgInput.OnIMEReturn = event

	def SetCancelEvent(self, event):
		self.cancelButton.SetEvent(event)
		self.inputValue.OnPressEscapeKey = event

		if app.USE_OFFLINESHOP_PRICE_AVERAGE:
			self.avgInput.OnPressEscapeKey = event

	def Open(self):
		if not self.itemVnum:
			return

		import item
		item.SelectItem(self.itemVnum)

		self.itemBoardTitle.SetText(item.GetItemName())

		self.boardSellIcon.LoadImage(item.GetIconImageFileName())

		if app.USE_OFFLINESHOP_STACK_OPTION:
			self.itemSize = item.GetItemSize()[1]
			self.equalStackBtn.SetUp()
			self.firstOptionDesc.SetText(localeinfo.OFFLINESHOP_OPTION1_DESC_B if self.isEditMode else localeinfo.OFFLINESHOP_OPTION1_DESC_A)

		if app.USE_OFFLINESHOP_PRICE_AVERAGE:
			for k, v in self.avgBtnsDict.items():
				v.SetUp()

			self.avgInput.SetText("0")
			self.averagePrice = 0
			offlineshop.RequestAveragePrice(self.itemVnum)

		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.sourceWindowType = -1
		self.sourceSlotPos = -1
		self.targetSlotPos = -1
		self.page = -1
		self.CurrentPageGrid = False
		self.isEditMode = False

		if app.ENABLE_INGAME_WIKI and self.boardSellIcon:
			self.boardSellIcon.UnloadImage()

		if app.USE_OFFLINESHOP_PRICE_AVERAGE:
			if self.avgInput.IsFocus():
				self.avgInput.KillFocus()

			if self.inputValue.IsFocus():
				self.inputValue.KillFocus()

		self.Hide()

	def IsEqualOn(self):
		if app.USE_OFFLINESHOP_STACK_OPTION and self.equalStackBtn:
			return self.equalStackBtn.IsDown()

		return False

	if app.USE_OFFLINESHOP_PRICE_AVERAGE:
		def SetFocusAvg(self):
			if self.inputValue.IsFocus():
				self.inputValue.KillFocus()

			self.avgInput.SetFocus()

		def SetFocusPrice(self):
			if self.avgInput.IsFocus():
				self.avgInput.KillFocus()

			self.inputValue.SetFocus()

		def __OnAvgValueUpdate(self):
			ui.EditLine.OnIMEUpdate(self.avgInput)

			if not self.avgBtnsDict[2].IsDown():
				return

			text = self.avgInput.GetText()
			if len(text) == 0:
				self.SetValue(self.averagePrice + ((self.averagePrice / 100) * 0), False, False)
				return

			if not text.isdigit():
				self.avgInput.SetText("0")
				ime.SetCursorPosition(-1)
				self.__OnAvgValueUpdate()
				return

			try:
				perc = int(text)
			except:
				perc = 0

			self.SetValue(self.averagePrice + ((self.averagePrice / 100) * perc), False, False)

		def __OnPressAvgBtn(self, arg, up = False):
			for k, v in self.avgBtnsDict.items():
				v.SetUp()

			if up:
				if self.avgInput.IsFocus():
					self.avgInput.KillFocus()

				if not self.inputValue.IsFocus():
					self.inputValue.SetFocus()

				self.SetValue(self.origPrice)
			else:
				if arg == 0:
					self.SetValue(self.averagePrice, False, False)
				elif arg == 1:
					self.SetValue(self.averagePrice + ((self.averagePrice / 100) * 10), False, False)

				self.avgBtnsDict[arg].Down()

				if arg == 2:
					if not self.avgInput.IsFocus():
						self.avgInput.SetFocus()

					self.__OnAvgValueUpdate()

		def OnRecvAveragePrice(self, price):
			if price == "...":
				self.averagePrice = 0
				self.averagePriceText.SetText(localeinfo.OFFLINESHOP_AVG_PRICE % (price))
			else:
				self.averagePrice = long(price * self.itemCount)
				self.averagePriceText.SetText(localeinfo.OFFLINESHOP_AVG_PRICE % (localeinfo.NumberToStringDotted(self.averagePrice)))

	def __OnValueUpdate(self, taxBtn = False, origPrice = True):
		ui.EditLine.OnIMEUpdate(self.inputValue)

		text = self.inputValue.GetText()
		if len(text) == 0:
			return

		val = 0
		if text.isdigit():
			try:
				val = min(MAX_PRICE, long(text))
			except:
				self.inputValue.SetText(str(DEFAULT_PRICE))
				ime.SetCursorPosition(-1)
				self.__OnValueUpdate()
				return
		else:
			origText = text
			newText = ""
			k = 0
			for l in text:
				if l.isdigit():
					newText += str(l)
					continue

				if l == "k" or l == "K":
					k += 1
					if k <= 4:
						newText += str(l)

					continue

			if newText != origText:
				self.inputValue.SetText(newText)
				ime.SetCursorPosition(-1)
				self.__OnValueUpdate()
				return
			else:
				text = text.replace("k", "000")

			try:
				val = min(MAX_PRICE, long(text))
			except:
				self.inputValue.SetText(str(DEFAULT_PRICE))
				ime.SetCursorPosition(-1)
				self.__OnValueUpdate()
				return

		if not taxBtn:
			self.fee = (val / 100) * 5
			self.price = val
			self.afterTaxPrice.SetText(localeinfo.OFFLINESHOP_AFTER_TAX % (localeinfo.NumberToStringDotted(self.price - self.fee)))

		if app.USE_OFFLINESHOP_PRICE_AVERAGE and origPrice:
			self.origPrice = self.price

	def SetValue(self, price, taxBtn = False, origPrice = True):
		try:
			price = min(MAX_PRICE, long(price))
		except:
			price = DEFAULT_PRICE

		wasFocus = FOCUS_PRICE

		if app.USE_OFFLINESHOP_PRICE_AVERAGE and wasFocus == FOCUS_PRICE:
			if self.avgBtnsDict[2].IsDown():
				if self.avgInput.IsFocus():
					self.avgInput.KillFocus()
					wasFocus = FOCUS_AVERAGE
			else:
				if self.avgInput.IsFocus():
					wasFocus = FOCUS_AVERAGE

		if wasFocus != FOCUS_PRICE:
			self.inputValue.SetFocus()

		self.inputValue.SetText(str(price))
		ime.SetCursorPosition(-1)
		self.__OnValueUpdate(taxBtn, origPrice)

		if wasFocus != FOCUS_PRICE:
			self.inputValue.KillFocus()

			if app.USE_OFFLINESHOP_PRICE_AVERAGE and wasFocus == FOCUS_AVERAGE:
				self.avgInput.SetFocus()

	def __OnPressTaxButton(self):
		if not self.price or not self.fee or self.price == self.old_price:
			return

		n = self.price + self.fee
		if n >= MAX_PRICE:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_SELL_MAX_WARN % (localeinfo.NumberToStringDotted(MAX_PRICE)))
			return

		self.afterTaxPrice.SetText(localeinfo.OFFLINESHOP_AFTER_TAX % (localeinfo.NumberToStringDotted(self.price)))

		self.old_price = n
		self.price = self.old_price
		self.SetValue(self.old_price, True)

	def OnPressEscapeKey(self):
		self.Close()
		return True

class HistoryWindow(ui.ScriptWindow):
	isLoaded = 0
	itemsDict = {}

	SCROLL_SPEED = 28

	KEY_ITEMNAME = 0
	KEY_BUYERNAME = 1
	KEY_PRICE = 2
	KEY_TIME = 3

	TEXT_LIMIT = 13

	toolTip = None
	toolTipItem = None

	class ScrollBar(ui.Window):
		BASE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
		CORNERS_AND_LINES_COLOR = grp.GenerateColor(0.3411, 0.3411, 0.3411, 1.0)
		BAR_NUMB = 9

		class MiddleBar(ui.DragButton):
			MIDDLE_BAR_COLOR = grp.GenerateColor(0.6470, 0.6470, 0.6470, 1.0)

			def __init__(self):
				ui.DragButton.__init__(self)
				self.AddFlag("movable")

				self.middle = ui.Bar()
				self.middle.SetParent(self)
				self.middle.AddFlag("attach")
				self.middle.AddFlag("not_pick")
				self.middle.SetColor(self.MIDDLE_BAR_COLOR)
				self.middle.SetSize(1, 1)
				self.middle.Show()

			def __del__(self):
				ui.DragButton.__del__(self)

			def SetStaticScale(self, size):
				(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
				ui.DragButton.SetSize(self, base_width, size)
				self.middle.SetSize(base_width, size)

			def SetSize(self, selfSize, fullSize):
				(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
				ui.DragButton.SetSize(self, base_width, truediv(int(selfSize), int(fullSize)) * selfSize)
				self.middle.SetSize(base_width, truediv(int(selfSize), int(fullSize)) * selfSize)

			def SetStaticSize(self, size):
				size = max(2, size)
				ui.DragButton.SetSize(self, size, self.middle.GetHeight())
				self.middle.SetSize(size, self.middle.GetHeight())

		def __init__(self):
			ui.Window.__init__(self)

			self.scrollEvent = None
			self.scrollSpeed = 1
			self.sizeScale = 1.0

			self.bars = []
			for i in xrange(self.BAR_NUMB):
				br = ui.Bar()
				br.SetParent(self)
				br.AddFlag("attach")
				br.AddFlag("not_pick")
				br.SetColor([self.CORNERS_AND_LINES_COLOR, self.BASE_COLOR][i == (self.BAR_NUMB - 1)])
				if not (i % 2 == 0): br.SetSize(1, 1)
				br.Show()

				self.bars.append(br)

			self.middleBar = self.MiddleBar()
			self.middleBar.SetParent(self)
			self.middleBar.SetMoveEvent(ui.__mem_func__(self.OnScrollMove))
			self.middleBar.Show()

		def __del__(self):
			ui.Window.__del__(self)

		def Destroy(self):
			for e in self.bars:
				del e

			self.bars = []

			if self.middleBar:
				del self.middleBar
				self.middleBar = None

		def OnScrollMove(self):
			if not self.scrollEvent:
				return

			arg = float(self.middleBar.GetLocalPosition()[1] - 1) / float(self.GetHeight() - 2 - self.middleBar.GetHeight())
			self.scrollEvent(arg)

		def ResetScrollEvent(self):
			self.scrollEvent = None

		def SetScrollEvent(self, func):
			self.scrollEvent = ui.__mem_func__(func)

		def SetScrollSpeed(self, speed):
			self.scrollSpeed = speed

		def OnRunMouseWheel(self, length):
			if self.IsInPosition():
				val = min(max(1, self.middleBar.GetLocalPosition()[1] - (length * 0.01) * self.scrollSpeed * self.sizeScale), self.GetHeight() - self.middleBar.GetHeight() - 1)
				self.middleBar.SetPosition(1, val)

				self.OnScrollMove()
				return True

			return False

		def OnMouseLeftButtonDown(self):
			(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
			if xMouseLocalPosition == 0 or xMouseLocalPosition == self.GetWidth():
				return

			y_pos = (yMouseLocalPosition - self.middleBar.GetHeight() / 2)
			self.middleBar.SetPosition(1, y_pos)

			self.OnScrollMove()

		def SetSize(self, w, h):
			(width, height) = (max(3, w), max(3, h))

			ui.Window.SetSize(self, width, height)

			self.bars[0].SetSize(1, (height - 2))
			self.bars[0].SetPosition(0, 1)
			self.bars[2].SetSize((width - 2), 1)
			self.bars[2].SetPosition(1, 0)
			self.bars[4].SetSize(1, (height - 2))
			self.bars[4].SetPosition((width - 1), 1)
			self.bars[6].SetSize((width - 2), 1)
			self.bars[6].SetPosition(1, (height - 1))
			self.bars[8].SetSize((width - 2), (height - 2))
			self.bars[8].SetPosition(1, 1)

			self.bars[1].SetPosition(0, 0)
			self.bars[3].SetPosition((width - 1), 0)
			self.bars[5].SetPosition((width - 1), (height - 1))
			self.bars[7].SetPosition(0, (height - 1))

			self.middleBar.SetStaticSize(width - 2)
			self.middleBar.SetSize(12, self.GetHeight())

			self.middleBar.SetRestrictMovementArea(1, 1, width - 2, height - 2)

		def SetScale(self, selfSize, fullSize):
			self.sizeScale = float(selfSize/fullSize)
			self.middleBar.SetSize(selfSize, fullSize)

		def SetStaticScale(self, r_size):
			self.middleBar.SetStaticScale(r_size)

		def SetPosScale(self, fScale):
			pos = (math.ceil((self.GetHeight() - 2 - self.middleBar.GetHeight()) * fScale) + 1)
			self.SetPos(pos)

		def SetPos(self, pos):
			wPos = (1, pos)
			self.middleBar.SetPosition(*wPos)

	class Item(ui.ExpandedImageBox):
		def OnOverIn(self, key):
			if key == HistoryWindow.KEY_ITEMNAME:
				if self.toolTipItem:
					self.toolTipItem.ClearToolTip()

				sockets = [self.infoDict["socket"][i] for i in xrange(player.METIN_SOCKET_MAX_NUM)]
				attrs = [(self.infoDict["attr"][i]["type"], self.infoDict["attr"][i]["value"]) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

				rands = []
				if app.ENABLE_APPLY_RANDOM_SHOP:
					rands = [(self.infoDict["rand"][i]["type"], self.infoDict["rand"][i]["value"], self.infoDict["rand"][i]["path"]) for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]

				enchants = []
				if app.USE_ENCHANT_COSTUMES:
					enchants = [(self.infoDict["enchant"][i]["type"], self.infoDict["enchant"][i]["value"], self.infoDict["enchant"][i]["time"]) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]

				trans = 0
				if app.ENABLE_CHANGE_LOOK_SYSTEM:
					trans = self.infoDict["trans"]
				if app.ENABLE_SET_ITEM:
					setItem = self.infoDict["setItem"]

				self.toolTipItem.AddItemData(self.infoDict["vnum"], sockets, attrs, None, 0, 0, player.INVENTORY, -1, None, apply_random_list = rands, set_value=0, transmutation = trans, enchantList = enchants,iSetValue=setItem)
			else:
				if self.toolTip:
					self.toolTip.ClearToolTip()

					textLen = len(self.origDict[key])
					if textLen == 0:
						return

					w = 11 * textLen
					self.toolTip.SetThinBoardSize(w)

					self.toolTip.AutoAppendTextLine(self.origDict[key])
					self.toolTip.AlignHorizonalCenter()
					self.toolTip.Show()

		def OnOverOut(self, key):
			if key == HistoryWindow.KEY_ITEMNAME:
				if self.toolTipItem:
					self.toolTipItem.HideToolTip()
			else:
				if self.toolTip:
					self.toolTip.HideToolTip()

		def __init__(self, toolTip, toolTipItem):
			ui.ExpandedImageBox.__init__(self)
			self.LoadImage("cream/shopseller/history_window_element.png")

			self.toolTip = proxy(toolTip)
			self.toolTipItem = proxy(toolTipItem)

			self.infoDict = {}
			self.origDict = {}
			self.imgDict1 = {}
			self.imgDict2 = {}
			self.textDict = {}

			tmp = ui.ExpandedImageBox()
			tmp.SetParent(self)
			tmp.LoadImage("cream/shopseller/itemnamewnd.png")
			tmp.SetPosition(3, 3)
			tmp.Show()
			self.imgDict1[HistoryWindow.KEY_ITEMNAME] = tmp

			tmp = ui.TextLine()
			tmp.SetParent(self.imgDict1[HistoryWindow.KEY_ITEMNAME])
			tmp.SetHorizontalAlignCenter()
			tmp.SetPosition(self.imgDict1[HistoryWindow.KEY_ITEMNAME].GetWidth() / 2, 6)
			tmp.Show()
			self.textDict[HistoryWindow.KEY_ITEMNAME] = tmp

			tmp = ui.ExpandedImageBox()
			tmp.SetParent(self.imgDict1[HistoryWindow.KEY_ITEMNAME])
			tmp.LoadImage("cream/shopseller/itemnamewnd.png")
			tmp.SetPosition(0, 0)
			tmp.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverIn), HistoryWindow.KEY_ITEMNAME)
			tmp.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOut), HistoryWindow.KEY_ITEMNAME)
			tmp.Show()
			self.imgDict2[HistoryWindow.KEY_ITEMNAME] = tmp

			tmp = ui.ExpandedImageBox()
			tmp.SetParent(self)
			tmp.LoadImage("cream/shopseller/buyernamewnd.png")
			tmp.SetPosition(100, 3)
			tmp.Show()
			self.imgDict1[HistoryWindow.KEY_BUYERNAME] = tmp

			tmp = ui.TextLine()
			tmp.SetParent(self.imgDict1[HistoryWindow.KEY_BUYERNAME])
			tmp.SetHorizontalAlignCenter()
			tmp.SetPosition(self.imgDict1[HistoryWindow.KEY_BUYERNAME].GetWidth() / 2, 6)
			tmp.Show()
			self.textDict[HistoryWindow.KEY_BUYERNAME] = tmp

			tmp = ui.ExpandedImageBox()
			tmp.SetParent(self.imgDict1[HistoryWindow.KEY_BUYERNAME])
			tmp.LoadImage("cream/shopseller/buyernamewnd.png")
			tmp.SetPosition(0, 0)
			tmp.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverIn), HistoryWindow.KEY_BUYERNAME)
			tmp.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOut), HistoryWindow.KEY_BUYERNAME)
			tmp.Show()
			self.imgDict2[HistoryWindow.KEY_BUYERNAME] = tmp

			tmp = ui.ExpandedImageBox()
			tmp.SetParent(self)
			tmp.LoadImage("cream/shopseller/pricewnd.png")
			tmp.SetPosition(199, 3)
			tmp.Show()
			self.imgDict1[HistoryWindow.KEY_PRICE] = tmp

			tmp = ui.TextLine()
			tmp.SetParent(self.imgDict1[HistoryWindow.KEY_PRICE])
			tmp.SetHorizontalAlignCenter()
			tmp.SetPosition(self.imgDict1[HistoryWindow.KEY_PRICE].GetWidth() / 2, 6)
			tmp.Show()
			self.textDict[HistoryWindow.KEY_PRICE] = tmp

			tmp = ui.ExpandedImageBox()
			tmp.SetParent(self.imgDict1[HistoryWindow.KEY_PRICE])
			tmp.LoadImage("cream/shopseller/pricewnd.png")
			tmp.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverIn), HistoryWindow.KEY_PRICE)
			tmp.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOut), HistoryWindow.KEY_PRICE)
			tmp.SetPosition(0, 0)
			tmp.Show()
			self.imgDict2[HistoryWindow.KEY_PRICE] = tmp

			tmp = ui.ExpandedImageBox()
			tmp.SetParent(self)
			tmp.LoadImage("cream/shopseller/timewnd.png")
			tmp.SetPosition(289, 3)
			tmp.Show()
			self.imgDict1[HistoryWindow.KEY_TIME] = tmp

			tmp = ui.TextLine()
			tmp.SetParent(self.imgDict1[HistoryWindow.KEY_TIME])
			tmp.SetHorizontalAlignCenter()
			tmp.SetPosition(self.imgDict1[HistoryWindow.KEY_TIME].GetWidth() / 2, 6)
			tmp.Show()
			self.textDict[HistoryWindow.KEY_TIME] = tmp

			tmp = ui.ExpandedImageBox()
			tmp.SetParent(self.imgDict1[HistoryWindow.KEY_TIME])
			tmp.LoadImage("cream/shopseller/timewnd.png")
			tmp.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverIn), HistoryWindow.KEY_TIME)
			tmp.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOut), HistoryWindow.KEY_TIME)
			tmp.SetPosition(0, 0)
			tmp.Show()
			self.imgDict2[HistoryWindow.KEY_TIME] = tmp

		def __del__(self):
			ui.ExpandedImageBox.__del__(self)

		def Destroy(self):
			self.toolTip = None
			self.toolTipItem = None

			self.infoDict = {}
			self.origDict = {}

			for v in self.textDict.values():
				del v

			self.textDict = {}

			for v in self.imgDict2.values():
				del v

			self.imgDict2 = {}

			for v in self.imgDict1.values():
				del v

			self.imgDict1 = {}

		def LoadInfo(self, info):
			self.infoDict = info
			self.origDict = {}

			vnum = self.infoDict["vnum"] if self.infoDict.has_key("vnum") else 0
			if not vnum:
				return

			item.SelectItem(vnum)

			text = "x" + str(self.infoDict["count"]) + " " + item.GetItemName()
			self.textDict[HistoryWindow.KEY_ITEMNAME].SetText(text[:HistoryWindow.TEXT_LIMIT] + "..." if len(text) > HistoryWindow.TEXT_LIMIT else text)
			self.origDict[HistoryWindow.KEY_ITEMNAME] = text

			text = self.infoDict["who"]
			if text == "_sys":
				text = localeinfo.OFFLINESHOP_HISTORY_FROM_SYSTEM_UNKNOWN if self.infoDict["expiration"] == 0 else localeinfo.OFFLINESHOP_HISTORY_FROM_SYSTEM_EXIRED

			self.textDict[HistoryWindow.KEY_BUYERNAME].SetText(text[:HistoryWindow.TEXT_LIMIT] + "..." if len(text) > HistoryWindow.TEXT_LIMIT else text)
			self.origDict[HistoryWindow.KEY_BUYERNAME] = text

			text = localeinfo.NumberToStringDotted(self.infoDict["price"])
			self.textDict[HistoryWindow.KEY_PRICE].SetText(text[:HistoryWindow.TEXT_LIMIT] + "..." if len(text) > HistoryWindow.TEXT_LIMIT else text)
			text += " " + localeinfo.MONETARY_UNIT0
			self.origDict[HistoryWindow.KEY_PRICE] = text

			text = self.infoDict["when"] + " UTC"
			self.origDict[HistoryWindow.KEY_TIME] = text
			# >>> SECTION BEGIN USE_OFFLINESHOP history readability (P6): show date only in the
			# narrow time column; the full timestamp stays in the hover tooltip via origDict. <<< END
			self.textDict[HistoryWindow.KEY_TIME].SetText(self.infoDict["when"][:10])

	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)

	def ChangeScrollbar(self):
		if not self.scrollBar:
			return

		if self.scrollBoard.GetHeight() <= self.peekWindow.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.peekWindow.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()

	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)

		self.ChangeScrollbar()

	def __LoadDialog(self):
		if self.isLoaded:
			return

		self.isLoaded = 1

		self.toolTip = uitooltip.ToolTip()
		self.toolTipItem = uitooltip.ItemToolTip()

		self.itemsList = []

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/offlineshop_historywindow.py")

		self.titleBar = self.GetChild("ui_titlebar")
		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))

		tmp = ui.Window()
		# tmp.SetInsideRender(True)
		tmp.SetParent(self)
		tmp.AddFlag("attach")
		tmp.AddFlag("not_pick")
		tmp.SetSize(382, 336)
		tmp.SetPosition(8, 29 + 28)
		tmp.Show()
		self.peekWindow = tmp

		tmp = ui.Window()
		tmp.SetParent(self.peekWindow)
		tmp.AddFlag("attach")
		tmp.AddFlag("not_pick")
		tmp.SetPosition(0, 0)
		tmp.Show()
		self.scrollBoard = tmp

		if app.USE_CLIP_MASK:
			self.scrollBoard.SetClippingMaskWindow(self.peekWindow)

		tmp = self.ScrollBar()
		tmp.SetParent(self)
		tmp.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		tmp.SetSize(7, self.peekWindow.GetHeight())
		tmp.SetScrollEvent(self.OnScrollBar)
		tmp.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar = tmp

	def Destroy(self):
		for i in self.itemsList:
			i.Destroy()
			del i

		if self.scrollBar:
			self.scrollBar.ResetScrollEvent()
			self.scrollBar.Destroy()
			del self.scrollBar
			self.scrollBar = None

		itemsDict = {}

		if self.titleBar:
			self.titleBar.SetCloseEvent(None)
			self.titleBar = None

		if self.scrollBoard:
			del self.scrollBoard
			self.scrollBoard = None

		if self.peekWindow:
			del self.peekWindow
			self.peekWindow = None

		if self.toolTip:
			self.toolTip.ClearToolTip()
			del self.toolTip
			self.toolTip = None

		if self.toolTipItem:
			self.toolTipItem.ClearToolTip()
			del self.toolTipItem
			self.toolTipItem = None

		self.ClearDictionary()

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__LoadDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def BuildItems(self):
		for i in self.itemsList:
			i.Destroy()
			del i

		self.itemsList = []

		self.scrollBoard.SetSize(0, 0)

		for k, v in sorted(self.itemsDict.items()):
			tmp = self.Item(self.toolTip, self.toolTipItem)
			tmp.SetParent(self.scrollBoard)
			tmp.LoadInfo(v)
			tmp.Show()

			if len(self.itemsList) > 0:
				y = (self.itemsList[-1].GetLocalPosition()[1] + self.itemsList[-1].GetHeight())
				tmp.SetPosition(0, y)
			else:
				tmp.SetPosition(0, 0)

			(width, height) = (tmp.GetWidth(), self.scrollBoard.GetHeight() + tmp.GetHeight())
			self.scrollBoard.SetSize(width, height)

			self.itemsList.append(tmp)

		self.ChangeScrollbar()
		return True

	def Rebuild(self, itemDict):
		tmpDict = {}
		tmpDict[0] = itemDict

		if len(self.itemsDict) == offlineshop.OFFLINESHOP_MAX_HISTORY_NUM:
			k = list(self.itemsDict)[-1]
			del self.itemsDict[k]

		i = 1
		for k, v in sorted(self.itemsDict.items()):
			tmpDict[i] = v
			i += 1

		self.itemsDict = tmpDict
		del tmpDict

		self.UpdateScrollbar(0)
		self.BuildItems()

	def Open(self, build = False):
		if build:
			if not self.BuildItems():
				return

		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		if self.toolTip:
			self.toolTip.ClearToolTip()
			self.toolTip.HideToolTip()

		if self.toolTipItem:
			self.toolTipItem.ClearToolTip()
			self.toolTipItem.HideToolTip()

		self.Hide()

	def OnRunMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			if self.scrollBar and self.scrollBar.IsShow():
				self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
				return True

		return False

	def OnPressEscapeKey(self):
		self.Close()
		return True

class OfflineShopWindow(ui.ScriptWindow):
	wndHistory = None

	PAGE_TEXT = ( "I", "II", "III", "IV", "V")

	if app.USE_OFFLINESHOP_STACK_OPTION:
		tmpStackSlots = {}

	if app.USE_OFFLINESHOP_PRICE_AVERAGE:
		priceInputDlg = None

		def Recv_PriceAverage(self, vnum, price):
			if self.priceInputDlg and self.priceInputDlg.itemVnum == vnum:
				self.priceInputDlg.OnRecvAveragePrice(price)
			if self.wndSearchShop:
				self.wndSearchShop.Recv_PriceAverage(vnum, price)

	if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
		unlockSlotDlg = None

		def SlotCanBeAccesed(self, slotNum, pageNum):
			return True if player.GetOffshopSlots() > (pageNum * offlineshop.OFFLINESHOP_SLOTS_PAGE_COUNT) + slotNum else False

		def OnCancelUnlockSlot(self):
			if self.unlockSlotDlg:
				self.unlockSlotDlg.Close()

		def OnAcceptUnlockSlot(self):
			if self.unlockSlotDlg:
				offlineshop.SendUnlockSlot()
				self.unlockSlotDlg.Close()

		def RequestUnlockSlot(self):
			if not self.unlockSlotDlg:
				dlg = uicommon.QuestionDialog()
				dlg.SetText(localeinfo.OFFLINESHOP_UNLOCK_SLOT_DIALOG)
				dlg.SetCancelEvent(ui.__mem_func__(self.OnCancelUnlockSlot))
				dlg.SetAcceptEvent(ui.__mem_func__(self.OnAcceptUnlockSlot))
				self.unlockSlotDlg = dlg

			self.unlockSlotDlg.Open()

	def SaveInputPrice(self, vnum, count, price):
		if not vnum or not price:
			return

		price /= count

		vnum = str(vnum)
		price = str(price)

		if not vnum.isdigit() or not price.isdigit():
			return

		import os
		if not os.path.exists("UserData/offlineshop/"):
			os.makedirs("UserData/offlineshop/")

		n = "UserData/offlineshop/%s.txt" % (vnum)
		f = file(n, "w+")
		f.write(str(price))
		f.close()

	def LoadInputPrice(self, vnum):
		if not vnum:
			return 0

		vnum = str(vnum)
		if not vnum.isdigit():
			return

		import os
		if os.path.exists("UserData/offlineshop/"):
			n = "UserData/offlineshop/%s.txt" % (vnum)
			if os.path.exists(n):
				f = open(n, "r")
				d = f.read()
				f.close()

				l = d.split("\t")
				p = l[0]
				if not p.isdigit():
					os.remove(n)
					return 0

				return long(p)

		return 0

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		# if app.ENABLE_WINDOW_SLIDE_EFFECT:
			# self.AddFlag("animated_board")

		self.bIsLoaded = False
		
		self.wndShop = OfflineShopRenewal(self)
		self.wndShop.Hide()
		
		self.wndSearchShop = uishopsearch.ShopSearch()
		self.wndSearchShop.Hide()

		self.wndDecoration = uiofflineshop_deco.OfflineShopDecoration()
		self.wndDecoration.Hide()

		self.xShopStart = 0
		self.yShopStart = 0

		self.priceInputDlg = None
		# P6 relist-from-safebox session state
		self.hasLiveShop = False
		self._relistActive = False
		self._relistBefore = set()
		self._relistClaimed = set()
		self._relistTtl = 0
		self._relistExpect = {}

		self.__Reinit()
		self.__Reinit2(True)
		self.__LoadWindow()

		self.SetCenterPosition()
	
	def SetItemToolTip(self, tooltip):
		self.tooltipItem = tooltip
		#if self.wndHistory:
		#	self.wndHistory.SetItemToolTip(tooltip)

	def BindInterface(self, interface):
		self.interface = interface
		
		if self.wndSearchShop:
			self.wndSearchShop.SetInterface(interface)
	
	def __Reinit2(self, isDestroy = False):
		self.wBoard = {}
		self.wFrame = {}
		self.wBar = {}
		self.dictName = {}
		self.itemStock = {}
		self.itemRestrict = {}

		self.ClearStockBuilder(isDestroy)

	def __Reinit(self):
		self.MyShopEditNameDlg = None
		self.WithdrawQuestionDialog = None
		self.QuestionDialog = None
		self.ShopName = None
		self.tooltipItem = None
		self.interface = None
		
		self.PageGrid = 0
		
	def OnPressEscapeKey(self):
		if self.NameEdit.IsFocus():
			self.NameEdit.KillFocus()
			return False

		if self.QuestionDialog:
			if self.QuestionDialog.IsShow():
				return False
			
		if self.WithdrawQuestionDialog:
			return False

		self.Close()
		return True
	
	def Destroy(self):
		if self.btnHistoryBuildShop:
			self.btnHistoryBuildShop.SetEvent(None)
			self.btnHistoryBuildShop = None

		if self.btnHistoryMyShop:
			self.btnHistoryMyShop.SetEvent(None)
			self.btnHistoryMyShop = None

		if self.wndHistory:
			self.wndHistory.Destroy()
			del self.wndHistory
			self.wndHistory = None

		for k, v in self.tmpStackSlots.items():
			del v

		self.tmpStackSlots = {}

		self.ClearDictionary()
		self.CloseDialogs(True)

		self.__Reinit()
		self.__Reinit2(True)

		if self.wndShop:
			self.wndShop.Destroy()
			self.wndShop = None

		if self.wndSearchShop:
			self.wndSearchShop.Destroy()
			self.wndSearchShop.Hide()
			self.wndSearchShop = None

		if self.wndDecoration:
			self.wndDecoration.Destroy()
			self.wndDecoration.Hide()
			self.wndDecoration = None

	def CloseDialogs(self, isDestroy=False):
		if app.USE_OFFLINESHOP_EXTENDED_SLOTS and self.unlockSlotDlg:
			self.unlockSlotDlg.Close()

			if isDestroy:
				del self.unlockSlotDlg
				self.unlockSlotDlg = None

		if self.WithdrawQuestionDialog:
			self.WithdrawQuestionDialog.Close()
			self.WithdrawQuestionDialog = None

		if self.QuestionDialog:
			self.OnCloseQuestionDialog()

		if self.priceInputDlg:
			self.priceInputDlg.Close()

			if isDestroy:
				self.priceInputDlg.Destroy()
				del self.priceInputDlg
				self.priceInputDlg = None

	def ClearStockBuilder(self, isDestroy=False):
		self.itemStockBuilder = {}
		self.itemStockBuilder[0] = {}
		self.itemStockBuilder[1] = {}
		self.itemStockBuilder[2] = {}
		self.itemStockBuilder[3] = {}
		self.itemStockBuilder[4] = {}

		self.RefreshItemSlotInv(isDestroy)

	if app.WJ_ENABLE_TRADABLE_ICON:
		def OnTop(self):
			if self.interface == None:
				return
		
			if self.wBoard[PAGE_BUILDER].IsShow() or self.wBoard[PAGE_MYSHOP].IsShow():
				self.interface.SetOnTopWindow(player.ON_TOP_WND_SHOP)
			else:
				self.interface.SetOnTopWindow(player.ON_TOP_WND_NONE)
				
			self.interface.RefreshMarkInventoryBag()
	
	def Close(self, isDestroy=False):
		self._relistActive = False
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "OFFLINE_SHOP")
		if self.wndHistory:
			self.wndHistory.Close()

		self.CancelInputPrice()
		self.ClearStockBuilder(isDestroy)
		self.CloseDialogs(isDestroy)

		if self.MyShopEditNameDlg:
			self.MyShopEditNameDlg.Hide()
			self.MyShopEditNameDlg = None

		offlineshop.SendCloseBoard()
		self.Hide()
		
		if app.WJ_ENABLE_TRADABLE_ICON:
			if self.interface:
				self.interface.SetOnTopWindow(player.ON_TOP_WND_NONE)
				if not isDestroy:
					self.interface.RefreshMarkInventoryBag()

	def Open(self):
		offlineshop.SendCloseBoard()
		offlineshop.SendOpenShopOwner()

	def Show(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "OFFLINE_SHOP")
		self.__LoadWindow()
		ui.ScriptWindow.Show(self)

		self.SetTop()
		(self.xShopStart, self.yShopStart, z) = player.GetMainCharacterPosition()

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("OFFLINE_SHOP", x, y)

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		self.wndShop = None
		
	def __LoadWindow(self):
		if self.bIsLoaded:
			return

		self.bIsLoaded = True

		self.AddFlag("movable")
		self.__InitPage(369, 410+30, PAGE_MYSHOP, localeinfo.OFFLINESHOP_EDIT_TITLE, PATH_ROOT_BUILD + "bg_2.png")
		self.__InitPage(369, 405+30, PAGE_BUILDER, localeinfo.OFFLINESHOP_BUILD_TITLE, PATH_ROOT_BUILD + "bg_2.png")
		self.__InitPage(369, 385+30, PAGE_SAFEBOX, localeinfo.OFFLINESHOP_SAFEBOX_TITLE, PATH_ROOT_BUILD + "bg_2.png")
		self.__InitPage(369, 340+30, PAGE_SHOP, localeinfo.OFFLINESHOP_SHOP_TITLE, PATH_ROOT_BUILD + "bg_2.png")

		self.itemSlot = []
		for xPage in xrange(PAGE_COUNT):
			itemSlot = ui.GridSlotWindow()
			itemSlot.SetParent(self)
			itemSlot.SetPosition(31, 105)
			itemSlot.ArrangeSlot(0, 10, 8, 32, 32, 0, 0)
			itemSlot.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)

			itemSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
			itemSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
			itemSlot.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
			#itemSlot.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
			itemSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
			itemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			itemSlot.SetGridSpecial(10, 8)
			itemSlot.Hide()

			if xPage == 0:
				itemSlot.Show()

			self.itemSlot.append(itemSlot)

	def __ChangePage(self, page):
		if app.USE_OFFLINESHOP_EXTENDED_SLOTS and self.unlockSlotDlg:
			self.unlockSlotDlg.Close()

		self.CancelInputPrice()
	
		for index in xrange(len(self.wBoard)):
			if not self.wBoard.has_key(index):
				continue
		
			if index == page:
				self.wFrame[page].Show()
				self.wBoard[page].Show()
				self.SetSize(self.wFrame[page].GetWidth(), self.wFrame[page].GetHeight())
			else:
				self.wFrame[index].Hide()
				self.wBoard[index].Hide()

		for idxPage in xrange(len(self.dictPages)):
			if page == PAGE_SHOP:
				self.dictPages[idxPage].SetPosition(35 + 40 * idxPage, 360)
			elif page == PAGE_SAFEBOX:
				self.dictPages[idxPage].SetPosition(35 + 40 * idxPage, 360)
			elif page == PAGE_BUILDER:
				self.dictPages[idxPage].SetPosition(35 + 40 * idxPage, 360)
			else:
				self.dictPages[idxPage].SetPosition(35 + 40 * idxPage, 360)

			self.dictPages[idxPage].SetParent(self.wBoard[page])

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.OnTop()

		self.itemSlot[self.PageGrid].Show()

	def __InitPage(self, width, height, page, title, bg = PATH_ROOT + "bg_2.png"):
		OFFSHOP_BOARD_INSET_X = 6
		OFFSHOP_BOARD_INSET_TOP = 28
		OFFSHOP_BOARD_INSET_BOTTOM = 5

		self.wFrame[page] = ui.BoardWithTitleBar()
		self.wFrame[page].SetParent(self)
		self.wFrame[page].SetPosition(0, 0)
		self.wFrame[page].SetTitleName(title)
		self.wFrame[page].SetCloseEvent(ui.__mem_func__(self.Close))
		self.wFrame[page].Show()

		self.wBoard[page] = ui.ExpandedImageBox()
		self.wBoard[page].SetParent(self.wFrame[page])
		self.wBoard[page].AddFlag("not_pick")
		self.wBoard[page].LoadImage(bg)
		self.wBoard[page].SetPosition(OFFSHOP_BOARD_INSET_X, OFFSHOP_BOARD_INSET_TOP)
		self.wBoard[page].Show()

		# inner titlebar kept for back-compat but hidden; the board provides the real chrome now
		self.wBar[page] = ui.TitleBarNEW()
		self.wBar[page].SetParent(self.wBoard[page])
		self.wBar[page].MakeTitleBar(self.wBoard[page].GetWidth() - 12, "red")
		self.wBar[page].SetPosition(6, 6)
		self.wBar[page].SetCloseEvent(ui.__mem_func__(self.Close))
		
		# closeBtn = ui.Button()
		# closeBtn.SetParent(boardImage)
		# closeBtn.SetUpVisual(IMG_DIR+"close_0.tga")
		# closeBtn.SetOverVisual(IMG_DIR+"close_1.tga")
		# closeBtn.SetDownVisual(IMG_DIR+"close_2.tga")
		# closeBtn.SetEvent(self.Close)
		# closeBtn.SetPosition(boardImage.GetWidth()-closeBtn.GetWidth()-5,5)
		# closeBtn.Show()
		
		self.dictName[page] = ui.MakeTextLineNew(self.wBar[page], 0, 4, title)
		self.dictName[page].SetWindowHorizontalAlignCenter()
		self.dictName[page].SetHorizontalAlignCenter()
		self.wBar[page].Hide()

		self.wFrame[page].SetSize(self.wBoard[page].GetWidth() + OFFSHOP_BOARD_INSET_X * 2,
			self.wBoard[page].GetHeight() + OFFSHOP_BOARD_INSET_TOP + OFFSHOP_BOARD_INSET_BOTTOM)

		self.SetSize(self.wFrame[page].GetWidth(), self.wFrame[page].GetHeight())

		if page == PAGE_BUILDER:
			self.NameSlotBar = ui.MakeImageBox(self.wBoard[page], PATH_ROOT_BUILD + "field_name.png", 0, 35)
			self.NameSlotBar.SetWindowHorizontalAlignCenter()
		
			self.NameEdit = ui.EditLine()
			self.NameEdit.SetParent(self.NameSlotBar)
			self.NameEdit.SetMax(40)
			self.NameEdit.SetSize(self.NameSlotBar.GetWidth(), 15)
			if localeinfo.IsARABIC():
				self.NameEdit.SetPosition(-1, 7)
			else:
				self.NameEdit.SetPosition(8, 7)
			self.NameEdit.SetLimitWidth(self.NameEdit.GetWidth())
			self.NameEdit.SetEscapeEvent(ui.__mem_func__(self.OnPressNameEscapeKey))
			self.NameEdit.SetOutline()
			self.NameEdit.Show()

			self.btnGoSafeboxCRT = ui.MakeButton(self.wBoard[page], 316, 34, localeinfo.OFFLINESHOP_SAFEBOX, PATH_ROOT_BUILD, "btn_4_normal.png", "btn_4_hover.png", "btn_4_down.png")
			self.btnCreateOk = ui.MakeButton(self.wBoard[page], 72, 37, False, PATH_ROOT_BUILD, "btn-sm-0.png", "btn-sm-1.png", "btn-sm-2.png")
			self.btnGoDecoCRT = ui.MakeButton(self.wBoard[page], 36, 36, localeinfo.OFFLINESHOP_DECORATION, PATH_ROOT_BUILD, "btn_cosmetic_norm.png", "btn_cosmetic_hover.png", "btn_cosmetic_down.png")
			self.btnCreateOk.SetToolTipText(localeinfo.OFFLINESHOP_CREATE)
			
			self.btnGoSafeboxCRT.SetEvent(ui.__mem_func__(self.ManageWindow))
			self.btnCreateOk.SetEvent(ui.__mem_func__(self.OnCreateShop))
			self.btnGoDecoCRT.SetEvent(ui.__mem_func__(self.OpenDecoration))

			self.btnHistoryBuildShop = ui.MakeButton(self.wBoard[page], 283, 35, localeinfo.OFFLINESHOP_HISTORY, PATH_ROOT, "history_shop_norm.png", "history_shop_hover.png", "history_shop_down.png")
			self.btnHistoryBuildShop.SetEvent(ui.__mem_func__(self.__OpenHistoryWindow))
		elif page == PAGE_MYSHOP:
			self.wndSlotTotalYang = ui.MakeImageBox(self.wBoard[page], PATH_ROOT + "field_total_cost.png", 46, 36)

			if localeinfo.IsARABIC():
				self.wndTotalPrice = ui.MakeTextLineNew(self.wndSlotTotalYang, 150, 7, localeinfo.OFFLINESHOP_TOTAL)
				self.wndTotalPrice.SetWindowHorizontalAlignLeft()
				self.wndTotalPrice.SetHorizontalAlignLeft()
			else:
				self.wndTotalPrice = ui.MakeTextLineNew(self.wndSlotTotalYang, 6, 7, localeinfo.OFFLINESHOP_TOTAL)
				self.wndTotalPrice.SetWindowHorizontalAlignLeft()
				self.wndTotalPrice.SetHorizontalAlignLeft()

			self.wndBoardRefill = ui.MakeImageBox(self.wBoard[page], PATH_ROOT + "field_time.png", 147, 358)

			self.btnRefill = ui.MakeButton(self.wBoard[page], 279, 358, localeinfo.OFFLINESHOP_REFILLTIME, PATH_ROOT, "btn_refill_time_norm.png", "btn_refill_time_hover.png", "btn_refill_time_down.png")
			self.btnRefill.SetEvent(ui.__mem_func__(self.AskIncreaseTimeShop))
			
			self.wndRemainTime = ui.MakeTextLineNew(self.wndBoardRefill, 0, 8, "Left: 0 Day")
			self.wndRemainTime.SetWindowHorizontalAlignCenter()
			self.wndRemainTime.SetHorizontalAlignCenter()

			self.btnCloseShop = ui.MakeButton(self.wBoard[page], 295, 37, localeinfo.OFFLINESHOP_CLOSESHOP, PATH_ROOT, "close_shop_normal.png", "close_shop_hover.png", "close_shop_down.png")
			self.btnCloseShop.SetEvent(ui.__mem_func__(self.AskClosePrivateShop))
			
			self.btnChangeName = ui.MakeButton(self.wBoard[page], 227, 37, localeinfo.OFFLINESHOP_CHANGENAME, PATH_ROOT, "edit_button_normal.png", "edit_button_hover.png", "edit_button_down.png")
			self.btnChangeName.SetEvent(ui.__mem_func__(self.ChangeNameShop))

			self.btnGoToSafebox = ui.MakeButton(self.wBoard[page], 227, 37, localeinfo.OFFLINESHOP_SAFEBOX, PATH_ROOT_BUILD, "btn_4_normal.png", "btn_4_hover.png", "btn_4_down.png")
			self.btnGoToSafebox.SetEvent(ui.__mem_func__(self.ManageWindow))

			self.dictPages = {}

			for i in xrange(PAGE_COUNT):
				self.dictPages[i] = MakeRadioButton(self.wBoard[page], 0, 0, PATH_SHOP + "pages/", "page_button_normal.png", "page_button_hover.png", "page_button_down.png")
				self.dictPages[i].SetText(self.PAGE_TEXT[i] if i < len(self.PAGE_TEXT) else localeinfo.NumberToRoman(i + 1))
				self.dictPages[i].SetToolTipText(localeinfo.NumberToRoman(i + 1))

			for idxPage in xrange(len(self.dictPages)):
				self.dictPages[idxPage].SetEvent(ui.__mem_func__(self.SetPageGrid), idxPage)

			self.dictPages[0].Down()

			self.btnHistoryMyShop = ui.MakeButton(self.wBoard[page], 261, 37, localeinfo.OFFLINESHOP_HISTORY, PATH_ROOT, "history_shop_norm.png", "history_shop_hover.png", "history_shop_down.png")
			self.btnHistoryMyShop.SetEvent(ui.__mem_func__(self.__OpenHistoryWindow))

			# USE_OFFLINESHOP_HYPERLINK: drop a clickable [SHOP] link into chat (see docs/OFFLINESHOP_HYPERLINK.md)
			self.btnShareShop = ui.MakeButton(self.wBoard[page], 210, 389, localeinfo.OFFLINESHOP_SHARE, PATH_ROOT_BUILD, "btn_norm.png", "btn_hover.png", "btn_down.png")
			self.btnShareShop.SetText(localeinfo.OFFLINESHOP_SHARE)
			self.btnShareShop.SetEvent(ui.__mem_func__(self.OnShareShop))
		elif page == PAGE_SAFEBOX:
			self.btnGoBack = ui.MakeButton(self.wBoard[page], 242, 383, localeinfo.OFFLINESHOP_BACK, PATH_ROOT_BUILD, "btn_back_0.png", "btn_back_1.png", "btn_back_2.png")
			self.btnGoBack.SetEvent(ui.__mem_func__(self.ManageWindow))

			self.btnWithdrawYang = ui.MakeButton(self.wBoard[page], 262, 35, False, PATH_ROOT_BUILD, "btn_reward_normal.png", "btn_reward_hover.png", "btn_reward_down.png")
			self.btnWithdrawYang.SetToolTipText(localeinfo.OFFLINESHOP_WITHDRAW)#here2

			self.btnWithdrawYang.SetEvent(ui.__mem_func__(self.WithdrawMoney))

			# >>> SECTION BEGIN USE_OFFLINESHOP withdraw-all items (P6): one-click bulk withdraw via
			# the SUBHEADER_CG_SHOP_SAFEBOX_GET_ALL packet (a single server-side anti-flood charge).
			# Shown only when the client+server were built with the flag. Position is best-guess. <<< END
			if app.USE_OFFLINESHOP_SAFEBOX_GET_ALL:
				self.btnWithdrawAll = ui.MakeButton(self.wBoard[page], 133, 351, localeinfo.OFFLINESHOP_WITHDRAW_ALL, PATH_ROOT, "btn_norm.png", "btn_hover.png", "btn_down.png")
				self.btnWithdrawAll.SetEvent(ui.__mem_func__(self.OnWithdrawAllItems))
				self.btnWithdrawAll.SetText(localeinfo.OFFLINESHOP_WITHDRAW_ALL)
				
				self.btnRelistAll = ui.MakeButton(self.wBoard[page], 21, 351, localeinfo.OFFLINESHOP_RELIST_ALL, PATH_ROOT, "btn_norm.png", "btn_hover.png", "btn_down.png")
				self.btnRelistAll.SetEvent(ui.__mem_func__(self.OnRelistAllItems))
				self.btnRelistAll.SetText(localeinfo.OFFLINESHOP_RELIST_ALL)
				
			self.wndYangField = ui.MakeImageBox(self.wBoard[page], PATH_ROOT + "field_yang.png", 72, 34)
			if localeinfo.IsARABIC():
				self.wndTextYang = ui.MakeTextLineNew(self.wndYangField, 8+100, 6, "|cFFffeaa7 Yang")
			else:
				self.wndTextYang = ui.MakeTextLineNew(self.wndYangField, 8, 6, "|cFFffeaa7 Yang")
			self.wndTextYang.SetWindowHorizontalAlignRight()
			self.wndTextYang.SetHorizontalAlignRight()
		#elif page == PAGE_HISTORY:
		#	if localeinfo.IsARABIC():
		#		self.btnHistoryMyShop2 = ui.MakeButton(self.wBoard[page], 23+10, 35+15, localeinfo.OFFLINESHOP_BACK, PATH_ROOT_BUILD, "btn_cosmetic_norm.png", "btn_cosmetic_hover.png", "btn_cosmetic_down.png")
		#	else:
		#		self.btnHistoryMyShop2 = ui.MakeButton(self.wBoard[page], 23, 35, localeinfo.OFFLINESHOP_BACK, PATH_ROOT_BUILD, "btn_cosmetic_norm.png", "btn_cosmetic_hover.png", "btn_cosmetic_down.png")
		#
		#	self.btnHistoryMyShop2.SetEvent(ui.__mem_func__(self.ManageHistoryWindow))
		#
		#	self.wndHistory = HistoryWindow()#uiofflineshop_history.HistoryWindow()
		#	self.wndHistory.SetParent(self.wBoard[page])
		#	self.wndHistory.SetPosition(8, 10)
		#
		#	self.SetSize(self.wndHistory.GetWidth() + 16, self.wndHistory.GetHeight() + 20)
		#
		#	#self.HistoryScrollBar = ui.ScrollBarNew()
		#	#self.HistoryScrollBar.SetParent(self.wBoard[page])
		#	#self.HistoryScrollBar.SetScrollBarSize(226 + 26 + 100)
		#	#self.HistoryScrollBar.SetPosition(306, 79)
		#	#self.wndHistory.SetScrollBar(self.HistoryScrollBar)
		#	#self.HistoryScrollBar.Show()
		#
		#	#if localeinfo.IsARABIC():
		#	#	self.wndItemNameHistory = ui.MakeTextLineNew(self.wBoard[page], 270, 60, localeinfo.OFFLINESHOP_HISTORY_NAME)
		#	#	self.wndTimeHistory = ui.MakeTextLineNew(self.wBoard[page], 150, 60, localeinfo.OFFLINESHOP_HISTORY_REASON)
		#	#	self.wndPriceHistory = ui.MakeTextLineNew(self.wBoard[page], 150-20, 60, localeinfo.OFFLINESHOP_HISTORY_PRICE)
		#	#else:
		#	#	self.wndItemNameHistory = ui.MakeTextLineNew(self.wBoard[page], 16, 60, localeinfo.OFFLINESHOP_HISTORY_NAME)
		#	#	self.wndTimeHistory = ui.MakeTextLineNew(self.wBoard[page], 150, 60, localeinfo.OFFLINESHOP_HISTORY_REASON)
		#	#	self.wndPriceHistory = ui.MakeTextLineNew(self.wBoard[page], 270, 60, localeinfo.OFFLINESHOP_HISTORY_PRICE)
		#
		#	#self.wndNoSellHistory = ui.MakeTextLineNew(self.wBoard[page], 0, 200, localeinfo.OFFLINESHOP_HISTORY_EMPTY)
		#	#self.wndNoSellHistory.SetWindowHorizontalAlignCenter()
		#	#self.wndNoSellHistory.SetHorizontalAlignCenter()
		#	#self.wndNoSellHistory.Show()

	# >>> SECTION BEGIN duplicated def, second one below is the live one <<<
	# def OpenSearch(self):
	# 	if self.wndSearchShop.IsShow() == FALSE:
	# 		self.wndSearchShop.Show()
	# 	else:
	# 		self.wndSearchShop.Hide()
	# >>> SECTION END <<<

	def OpenSearch(self):
		if self.wndSearchShop.IsShow() == FALSE:
			self.wndSearchShop.Show()
		else:
			self.wndSearchShop.Hide()

	def ManageHistoryWindow(self):
		self.__ChangePage(PAGE_MYSHOP)
		self.RefreshItemSlot()

	def ManageWindow(self):
		if app.USE_OFFLINESHOP_SAFEBOX_TAB:
			# P5d: drop the SendCloseBoard round-trip. The server tolerates board+safebox
			# coexisting and refreshes the requested view in place (AddGuest dedupes; safebox-open
			# is idempotent under the flag). Still re-fetched on every flip, so never stale.
			if self.wBoard[PAGE_SAFEBOX].IsShow():
				offlineshop.SendOpenShopOwner()
			else:
				self._offshopWantSafeboxTab = True
				offlineshop.SendSafeboxOpen()
		else:
			if self.wBoard[PAGE_SAFEBOX].IsShow():
				offlineshop.SendCloseBoard()
				offlineshop.SendOpenShopOwner()
			else:
				offlineshop.SendCloseBoard()
				offlineshop.SendSafeboxOpen()

	def SetPageGrid(self, page):
		if page < 0 or page > PAGE_COUNT:
			return

		self.PageGrid = page

		for idxPage in xrange(len(self.dictPages)):
			if idxPage == page:
				self.dictPages[idxPage].Down()
			else:
				self.dictPages[idxPage].SetUp()

		self.RefreshItemSlot()

	def __ResetGridCacheAndPage(self):
		# >>> FIX bug1/bug2: CACHE_ITEMS_ID is a module-global {page:{item_id:cell}} that is
		# only ever cleared on shop close (OnClosePrivateShop). Stale cross-context entries
		# pinned same-vnum items to hidden grid pages, so:
		#   - bug2: the safebox click handler found no self.itemStock entry for an off-page
		#           cell and silently dropped the click (UseItemSlot, "has_key(slotIndex)==False").
		#   - bug1: the owner-shop render fragmented placement and a single GetGridCachePosItemID
		#           miss aborted the WHOLE board ("shop failed to open / remove one item").
		# On a GENUINE board (re)open we drop the stale cache and snap back to grid page I so
		# freshly-packed items land on the visible page. We only call this when the board was
		# NOT already open, so in-session refreshes (e.g. after a withdraw) keep their positions.
		CACHE_ITEMS_ID.clear()
		self.PageGrid = 0
		for idxPage in xrange(len(self.dictPages)):
			if idxPage == 0:
				self.dictPages[idxPage].Down()
			else:
				self.dictPages[idxPage].SetUp()

	def OnShareShop(self):
		# Build a clickable shop hyperlink for THIS player's live shop and paste it into
		# the chat input (player adds text / picks channel / presses Enter). Static [SHOP]
		# label; PID drives the click. Mirrors the server-side keyword expansion.
		if not self.hasLiveShop:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_SHARE_NO_SHOP)
			return
		pid = self.wndShop.ShopOpenInfo.get("owner_id", 0)
		if not pid:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_SHARE_NO_SHOP)
			return
		# Mirror the item-link token EXACTLY, incl. the Arabic RTL ordering (label before the
		# |H link) -- that ordering is what makes item links clickable in Arabic chat.
		label = localeinfo.OFFLINESHOP_HYPERLINK_LABEL
		if localeinfo.IsARABIC():
			token = " |h|r[%s]|cffffc700|Hoffshop:%x|h" % (label, pid)
		else:
			token = "|cffffc700|Hoffshop:%x|h[%s]|h|r" % (pid, label)
		if self.interface:
			if not self.interface.IsOpenChat():
				self.interface.ToggleChat()
			self.interface.SetChatFocus()
		ime.PasteString(token)

	def ChangeNameShop(self):
	
		if self.MyShopEditNameDlg == None:
			self.MyShopEditNameDlg	= uicommon.InputDialogWithDescription()
			self.MyShopEditNameDlg.SetMaxLength(35)
			self.MyShopEditNameDlg.SetDescription(localeinfo.OFFLINESHOP_EDIT_SHOPNAME_DESCRIPTION)
			self.MyShopEditNameDlg.SetAcceptEvent(self.__OnAcceptChangeShopNameDlg)
			self.MyShopEditNameDlg.SetCancelEvent(self.__OnCancelChangeShopNameDlg)
			self.MyShopEditNameDlg.SetTitle(localeinfo.OFFLINESHOP_EDIT_SHOPNAME_TITLE)

		self.MyShopEditNameDlg.inputValue.SetText("")
		self.MyShopEditNameDlg.Open()

	def __OnAcceptChangeShopNameDlg(self):
		newname = self.MyShopEditNameDlg.GetText()
		self.MyShopEditNameDlg.Hide()
		
		offlineshop.SendChangeName(newname)
	
	def __OnCancelChangeShopNameDlg(self):
		self.MyShopEditNameDlg.Hide()

	def OnPressNameEscapeKey(self):
		if self.OnPressEscapeKey():
			return
	
		if self.NameEdit.IsShowCursor() or self.NameEdit.GetText() != "":
			self.NameEdit.SetText("")
			self.NameEdit.SetEndPosition()

	def RefreshOpenShopPage(self):
		wasOpen = (self.IsShow() and self.wBoard[PAGE_SHOP].IsShow())
	
		name = self.wndShop.ShopOpenInfo["name"]
		ownerName	= name[:name.find('@')] if '@' in name else "NONAME"		
		name		= name[name.find('@')+1:] if '@' in name else name
		if localeinfo.IsARABIC():
			self.dictName[PAGE_SHOP].SetText(localeinfo.OFFLINESHOP_OWNER + " " + ownerName)
			self.wFrame[PAGE_SHOP].SetTitleName(localeinfo.OFFLINESHOP_OWNER + " " + ownerName)
		else:
			self.dictName[PAGE_SHOP].SetText(ownerName + localeinfo.OFFLINESHOP_OWNER)
			self.wFrame[PAGE_SHOP].SetTitleName(ownerName + localeinfo.OFFLINESHOP_OWNER)
		
		self.__ChangePage(PAGE_SHOP)
		if not wasOpen:
			self.__ResetGridCacheAndPage()

		self.RefreshItemSlot()

		if len(self.wndShop.ShopItemForSale) <= 0:
			self.Close()
			return

	def RefreshMyShopPage(self):
		wasOpen = (self.wBoard[PAGE_MYSHOP].IsShow())
		self.__ChangePage(PAGE_MYSHOP)
		if not wasOpen:
			self.__ResetGridCacheAndPage()

		wndRemainTimeLeft = self.wndShop.ShopOpenInfo["duration"]
		self.wndRemainTime.SetText(localeinfo.OFFLINESHOP_TIME_LEFT% (localeinfo.SecondToDHM(wndRemainTimeLeft * 60)))

		name = self.wndShop.ShopOpenInfo["name"]

		if '@' in name:
			name = name[name.find('@')+1:]

		self.ShopName = name
		self.NameEdit.SetText(self.ShopName)

		self.RefreshItemSlot()

		#self.wndHistory.Clear()
		#self.HistoryScrollBar.Hide()

		#if len(self.wndShop.soldItemsDict) == 0:
		#	self.wndNoSellHistory.Show()
		#else:
		#	self.wndNoSellHistory.Hide()

		#for idx, item in enumerate(self.wndShop.ShopItemSold):
		#	self.wndHistory.AppendItem(idx, item)

	def ResetCreateShopPage(self):
		self.ClearStockBuilder()

		self.__ChangePage(PAGE_BUILDER)
		self.RefreshItemSlot()
		
	def RefreshSafeboxPage(self):
		if app.USE_OFFLINESHOP_SAFEBOX_TAB:
			if not getattr(self, "_offshopWantSafeboxTab", False) and not self.wBoard[PAGE_SAFEBOX].IsShow():
				# P5d: a passive safebox refresh (a sale credited the safebox) arrived while the player
				# is on another tab. ShopSafeboxItems is already updated for the next flip; do NOT yank
				# them to the safebox tab.
				return
			self._offshopWantSafeboxTab = False
		wasOpen = (self.wBoard[PAGE_SAFEBOX].IsShow())
		self.__ChangePage(PAGE_SAFEBOX)
		if not wasOpen:
			self.__ResetGridCacheAndPage()

		self.RefreshItemSlot()

	def OverInItem(self, slotIndex):
		if not self.tooltipItem:
			return

		if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
			itemIndex = self.itemSlot[self.PageGrid].GetItemIndex(slotIndex)
			if itemIndex == offlineshop.OFFLINESHOP_LOCKED_SLOT_ITEMVNUM:
				self.tooltipItem.ClearToolTip()
				self.tooltipItem.SetItemToolTip(offlineshop.OFFLINESHOP_LOCKED_SLOT_ITEMVNUM)
				return

		if self.wBoard[PAGE_BUILDER].IsShow():
			if slotIndex in self.itemStockBuilder[self.PageGrid]:
				window, pos, price = self.itemStockBuilder[self.PageGrid][slotIndex]
				self.tooltipItem.SetInventoryItem(pos, window, isOfflineShop = 1)
				self.tooltipItem.AppendSpace(5)
				self.tooltipItem.AppendSellingPrice(price)
		elif slotIndex in self.itemStock:
			if app.USE_ENCHANT_COSTUMES:
				id, vnum, count, skinVnum, setItem , price, sockets ,attrs, itemApplyList, itemEnchantList = self.itemStock[slotIndex]
			else:
				itemApplyList=[]
				itemEnchantList=[]
				id, vnum, count, skinVnum,setItem, price, sockets, attrs = self.itemStock[slotIndex]
			
			self.tooltipItem.ClearToolTip()
			
			restrictInfo = None
			if app.ENABLE_EQUIPMENT_RESTRICTION:
				restrictInfo = self.itemRestrict.get(slotIndex)
			self.tooltipItem.AddItemData(vnum, sockets, attrs, None, 0, 0, player.INVENTORY, -1, None,  apply_random_list=itemApplyList, set_value=0, transmutation=skinVnum, enchantList=itemEnchantList, iSetValue=setItem, restrictInfo=restrictInfo)

			if self.wBoard[PAGE_SAFEBOX].IsShow() == FALSE:
				self.tooltipItem.AppendPrice(price)
			if self.wBoard[PAGE_MYSHOP].IsShow():
				self.tooltipItem.DeclareShortcut(("key_lclick",), localeinfo.OFFLINESHOP_TOOLTIP_EDIT_ITEM)
				self.tooltipItem.DeclareShortcut(("key_rclick",), localeinfo.OFFLINESHOP_TOOLTIP_WITHDRAW_ITEM)
			elif self.wBoard[PAGE_SAFEBOX].IsShow():
				self.tooltipItem.DeclareShortcut(("key_rclick",), localeinfo.OFFLINESHOP_TOOLTIP_WITHDRAW_ITEM)
				self.tooltipItem.DeclareShortcut(("key_ctrl", "key_rclick"), localeinfo.OFFLINESHOP_TOOLTIP_WITHDRAW_ALL_SAME_ITEM)
				self.tooltipItem.DeclareShortcut(("key_alt", "key_rclick"), localeinfo.OFFLINESHOP_TOOLTIP_RELIST_ITEM)
				self.tooltipItem.DeclareShortcut(("key_alt", "key_ctrl", "key_rclick"), localeinfo.OFFLINESHOP_TOOLTIP_RELIST_ALL_SAME_ITEM)

	def OverOutItem(self):
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def GetEmptyPosition(self, size):
		for page in xrange(PAGE_COUNT):
			iPos = self.itemSlot[page].GetEmptyGrid(size)
			if iPos >= 0:
				if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
					itemIndex = self.itemSlot[page].GetItemIndex(iPos)
					if itemIndex == offlineshop.OFFLINESHOP_LOCKED_SLOT_ITEMVNUM:
						return (-1, -1)

				return (page, iPos)

		return (-1, -1)

	def GetGridCachePosItemID(self, size, item_id):
		for page in xrange(len(self.itemSlot)):
			if not CACHE_ITEMS_ID.has_key(page):
				continue

			if CACHE_ITEMS_ID[page].has_key(item_id):
				return (page, CACHE_ITEMS_ID[page][item_id])

		return (self.GetEmptyPosition(size))

	def RefreshItemSlot(self):
		items = []
		if self.wBoard[PAGE_MYSHOP].IsShow() or self.wBoard[PAGE_SHOP].IsShow():
			items = self.wndShop.ShopItemForSale
		elif self.wBoard[PAGE_SAFEBOX].IsShow():
			items = self.wndShop.ShopSafeboxItems

		for itemSlotIdx in xrange(len(self.itemSlot)):
			for index in xrange(OFFLINESHOP_SLOT_COUNT):
				self.itemSlot[itemSlotIdx].ClearSlot(index)
				self.itemSlot[itemSlotIdx].EnableSlotCoverImage(index, False)

			self.itemSlot[itemSlotIdx].ClearGrid()
			self.itemSlot[itemSlotIdx].Hide()

		self.itemSlot[self.PageGrid].Show()

		TotalPrice = 0
		self.itemStock = {}
		self.itemRestrict = {}

		if self.wBoard[PAGE_BUILDER].IsShow():
			for page in xrange(PAGE_COUNT):
				for i in xrange(OFFLINESHOP_SLOT_COUNT):
					if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
						if not self.SlotCanBeAccesed(i, page):
							self.itemSlot[page].SetItemSlot(i, offlineshop.OFFLINESHOP_LOCKED_SLOT_ITEMVNUM, 0)
							self.itemSlot[page].PutItemGrid(i, 1)
							continue

					if not i in self.itemStockBuilder[page]:
						self.itemSlot[page].ClearSlot(i)
						continue

					window, pos, price = self.itemStockBuilder[page][i]
					vnum = player.GetItemIndex(window, pos)
					if vnum <= 0:
						continue
					
					self.itemSlot[page].SetItemSlot(i, vnum, player.GetItemCount(window, pos))
					
					if app.ENABLE_CHANGE_LOOK_SYSTEM:
						if not player.GetChangeLookVnum(window, pos):
							self.itemSlot[page].EnableSlotCoverImage(i, False)
						else:
							self.itemSlot[page].SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")
					
					item.SelectItem(vnum)
					_, size = item.GetItemSize()
					self.itemSlot[page].PutItemGrid(i, size)

			self.itemSlot[self.PageGrid].RefreshSlot()
			return

		if app.USE_OFFLINESHOP_EXTENDED_SLOTS and self.wBoard[PAGE_MYSHOP].IsShow():
			for page in xrange(PAGE_COUNT):
				for i in xrange(OFFLINESHOP_SLOT_COUNT):
					if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
						if not self.SlotCanBeAccesed(i, page):
							self.itemSlot[page].SetItemSlot(i, offlineshop.OFFLINESHOP_LOCKED_SLOT_ITEMVNUM, 0)
							self.itemSlot[page].PutItemGrid(i, 1)
							continue

		shownFullWarn = False
		for index in xrange(len(items)):
			itemVnum = items[index]["vnum"]
			itemCount = items[index]["count"]
			if itemVnum <= 0:
				continue

			item.SelectItem(itemVnum)
			_, size = item.GetItemSize()

			PageItemSlot, iPos = self.GetGridCachePosItemID(size, items[index]["id"])
			if iPos < 0:
				# >>> FIX bug1: was `return`, which aborted the WHOLE board render on a single
				# unplaceable item -> the shop looked like it "failed to open" and the owner had
				# to remove an item. Now skip just the item that doesn't fit, warn once, and keep
				# rendering the rest. The CACHE_ITEMS_ID reset on open (__ResetGridCacheAndPage)
				# keeps this from firing for shops that physically fit the 160-cell grid; the
				# trace records the offender if it ever still does. Revive the old behavior by
				# replacing the `continue` with `return` and dropping the once-guard.
				dbg.TraceError("OFFSHOP render: no grid slot for id=%s vnum=%d size=%d (item %d/%d, page=%d)" % (str(items[index].get("id", 0)), itemVnum, size, index, len(items), self.PageGrid))
				if not shownFullWarn:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_MAX_ITEM)
					shownFullWarn = True
				continue

			self.itemSlot[PageItemSlot].PutItemGrid(iPos, size)

			itemCountGrid = itemCount if itemCount > 1 else 0
			self.itemSlot[PageItemSlot].SetItemSlot(iPos, itemVnum, itemCountGrid)

			sockets = [items[index]["socket"][num] for num in xrange(player.METIN_SOCKET_MAX_NUM)]
			attrs = [(items[index]["attr"][num]['type'], items[index]["attr"][num]['value']) for num in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]	

			if app.ENABLE_APPLY_RANDOM_SHOP:
				itemApplyList=[(items[index]["rand"][num]['type'], items[index]["rand"][num]['value'], items[index]["rand"][num]['path']) for num in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]


			if app.USE_ENCHANT_COSTUMES:
				itemEnchantList=[(items[index]["enchant"][num]['type'], items[index]["enchant"][num]['value'], items[index]["enchant"][num]['time']) for num in xrange(player.ENCHANT_SLOT_MAX_NUM)]

			ItemPrice = 0
			if items[index].has_key("price"):
				ItemPrice = int(items[index]["price"])
				TotalPrice += int(items[index]["price"])

			transmutation = 0
			if items[index].has_key("trans"):
				transmutation = items[index]["trans"]

			if app.ENABLE_SET_ITEM:
				setItem = 0
				if items[index].has_key("setItem"):
					setItem = items[index]["setItem"]

			restrictInfo = (0, "")
			if app.ENABLE_EQUIPMENT_RESTRICTION and items[index].has_key("restrict"):
				restrictInfo = items[index]["restrict"]

			#if app.USE_OFFLINESHOP_STACK_OPTION:
			#	can = True
			#else:
			can = True if PageItemSlot == self.PageGrid else False

			if can:
				if app.USE_ENCHANT_COSTUMES:
					self.itemStock[iPos] = (items[index]["id"], itemVnum, itemCount, transmutation,setItem,ItemPrice, sockets, attrs,itemApplyList, itemEnchantList)
				else:
					self.itemStock[iPos] = (items[index]["id"], itemVnum, itemCount, transmutation, ItemPrice, sockets, attrs)

				if app.ENABLE_EQUIPMENT_RESTRICTION:
					self.itemRestrict[iPos] = restrictInfo

				if app.ENABLE_CHANGE_LOOK_SYSTEM:
					if not transmutation == 0:
						self.itemSlot[PageItemSlot].SetSlotCoverImage(iPos, "icon/item/ingame_convert_Mark.tga")
					else:
						self.itemSlot[PageItemSlot].EnableSlotCoverImage(iPos, False)

			if not CACHE_ITEMS_ID.has_key(PageItemSlot):
				CACHE_ITEMS_ID[PageItemSlot] = {}

			CACHE_ITEMS_ID[PageItemSlot][items[index]["id"]] = iPos

		self.wndTotalPrice.SetText(localeinfo.OFFLINESHOP_TOTAL + str(localeinfo.NumberToMoneyString(TotalPrice)))

		if self.priceInputDlg and self.wBoard[PAGE_MYSHOP].IsShow():
			CurrentPageGrid = self.priceInputDlg.CurrentPageGrid
			targetSlotPos = self.priceInputDlg.targetSlotPos
			isEditMode = self.priceInputDlg.isEditMode

		self.itemSlot[self.PageGrid].RefreshSlot()

	def SelectItemSlot(self, itemSlotIndex):
		if mousemodule.mouseController.isAttached():
			mousemodule.mouseController.DeattachObject()

		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
			itemIndex = self.itemSlot[self.PageGrid].GetItemIndex(itemSlotIndex)
			if itemIndex == offlineshop.OFFLINESHOP_LOCKED_SLOT_ITEMVNUM:
				if self.wBoard[PAGE_BUILDER].IsShow() or self.wBoard[PAGE_MYSHOP].IsShow():
					self.RequestUnlockSlot()
					return

		if self.itemStock.has_key(itemSlotIndex) == False:
			return

		if self.wBoard[PAGE_BUILDER].IsShow():
			return

		if app.USE_ENCHANT_COSTUMES:
			id, vnum, count, trans,setItem, price, sockets_v, attrs_s,rand_s, enchant_s = self.itemStock[itemSlotIndex]
		else:
			id, vnum, count, trans, setItem,price, sockets_v, attrs_s = self.itemStock[itemSlotIndex]


		if app.ENABLE_RENDER_TARGET and app.IsPressed(app.DIK_LSHIFT):
			if uiRenderTarget.IsCanShowItems(itemIndex):
				itemTransmutedVnum = player.GetChangeLookVnum(itemIndex)#to do : fix transmutation we need to specify the slot index
				self.interface.OpenRenderTargetWindow(0, itemTransmutedVnum if itemTransmutedVnum else itemIndex)
		else:
			if self.wBoard[PAGE_MYSHOP].IsShow():
				self.OpenInputPriceDialog(vnum, count, id, itemSlotIndex, True)
				return

		#if self.wBoard[PAGE_MYSHOP].IsShow() or self.wBoard[PAGE_SAFEBOX].IsShow():
		#	if app.IsPressed(app.DIK_LALT):
		#		sockets = {}
		#		for num in xrange(player.METIN_SOCKET_MAX_NUM):
		#			sockets[num] = (int(sockets_v[num]), 1)
		#		
		#		attrs = {}
		#		for num in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
		#			attrs[num] = (int(attrs_s[num][0]), int(attrs_s[num][1]))
		#		
		#		if app.USE_ENCHANT_COSTUMES:
		#			itemEnchantList=(int(enchant_s[num][0]), int(enchant_s[num][1]), int(enchant_s[num][2]))
		#			link = player.GetItemShopOfflineLink(vnum, sockets, attrs,enchant_s)
		#		else:
		#			link = player.GetItemShopOfflineLink(vnum, sockets, attrs)
		#		
		#		ime.PasteString(link)

	def UseItemSlot(self, slotIndex):
		if mousemodule.mouseController.isAttached():
			mousemodule.mouseController.DeattachObject()

		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
			itemIndex = self.itemSlot[self.PageGrid].GetItemIndex(slotIndex)
			if itemIndex == offlineshop.OFFLINESHOP_LOCKED_SLOT_ITEMVNUM:
				if self.wBoard[PAGE_BUILDER].IsShow() or self.wBoard[PAGE_MYSHOP].IsShow():
					self.RequestUnlockSlot()
					return

		# if app.ENABLE_RENDER_TARGET and\
			# app.IsPressed(app.DIK_LSHIFT) and\
			# self.tooltipItem:
			# if self.itemStock.has_key(slotIndex)!=False:
				# if app.USE_ENCHANT_COSTUMES:
					# id, vnum, count, trans, price, sockets, attrs, itemEnchantList = self.itemStock[slotIndex]
				# else:
					# id, vnum, count, trans, price, sockets, attrs = self.itemStock[slotIndex]
				
				# if uiRenderTarget.IsCanShowItems(slotIndex):
					# itemTransmutedVnum = player.GetChangeLookVnum(vnum)#to do : fix transmutation we need to specify the slot index
					# self.interface.OpenRenderTargetWindow(0, itemTransmutedVnum if itemTransmutedVnum else slotIndex)
				# return



		if self.QuestionDialog:
			self.OnCloseQuestionDialog()
		
		if self.wBoard[PAGE_BUILDER].IsShow():
			if slotIndex in self.itemStockBuilder[self.PageGrid]:
				invenType, invenPos, price = self.itemStockBuilder[self.PageGrid][slotIndex]
				del self.itemStockBuilder[self.PageGrid][slotIndex]

				self.RefreshItemSlot()
				self.RefreshItemSlotInv()
			return
		else:
			if self.itemStock.has_key(slotIndex) == False:
				return

			if app.USE_ENCHANT_COSTUMES:
				id, vnum, count, trans,setItem, price, sockets, attrs, itemApplyList,itemEnchantList = self.itemStock[slotIndex]
			else:
				id, vnum, count, trans,setItem, price, sockets, attrs = self.itemStock[slotIndex]

			if self.wBoard[PAGE_SAFEBOX].IsShow():
				if app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT):
					self.RelistFromSafebox(slotIndex, app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL))
					return
				offlineshop.SendSafeboxGetItem(id, True if (app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL)) else False)
				self.ClearCachePos(self.PageGrid, id)
				return
			elif self.wBoard[PAGE_SHOP].IsShow():
				item.SelectItem(vnum)

				if count > 1:
					text = localeinfo.OFFLINESHOP_BUY_COUNT % (item.GetItemName(), count, localeinfo.NumberToMoneyString(price))
				else:
					text = localeinfo.OFFLINESHOP_BUY % (item.GetItemName(), localeinfo.NumberToMoneyString(price))

				if not self.QuestionDialog:
					self.QuestionDialog = uicommon.QuestionDialog()

				if not self.QuestionDialog:
					return

				self.QuestionDialog.SetText(text)
				self.QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.OnCancelShopItem))
				self.QuestionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
				self.QuestionDialog.slotIndex = slotIndex
				self.QuestionDialog.itemStock = self.itemStock[slotIndex]
				self.QuestionDialog.Open()
			elif self.wBoard[PAGE_MYSHOP].IsShow():
				# >>> SECTION BEGIN USE_OFFLINESHOP unlist confirm (P6): a single misclick used to
				# unlist instantly. Route through a confirm dialog; accept -> OnCancelShopItem,
				# which already handles the PAGE_MYSHOP SendRemoveItem path. <<< END
				item.SelectItem(vnum)

				if not self.QuestionDialog:
					self.QuestionDialog = uicommon.QuestionDialog()

				if not self.QuestionDialog:
					return

				self.QuestionDialog.SetText(localeinfo.OFFLINESHOP_UNLIST_CONFIRM % (item.GetItemName()))
				self.QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.OnCancelShopItem))
				self.QuestionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
				self.QuestionDialog.slotIndex = slotIndex
				self.QuestionDialog.itemStock = self.itemStock[slotIndex]
				self.QuestionDialog.Open()
			else:
				return

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def OnCancelShopItem(self):
		if not self.QuestionDialog:
			return True
		
		if app.USE_ENCHANT_COSTUMES:
			id, vnum, count, trans, setItem ,price, sockets, attrs,itemApplyList ,itemEnchantList = self.QuestionDialog.itemStock
		else:
			id, vnum, count, trans,setItem, price, sockets ,attrs = self.QuestionDialog.itemStock
		
		if self.wBoard[PAGE_MYSHOP].IsShow():
			offlineshop.SendRemoveItem(id)
			self.ClearCachePos(self.PageGrid, id)
		elif self.wBoard[PAGE_SHOP].IsShow():
			offlineshop.SendBuyItem(self.wndShop.ShopOpenInfo["owner_id"], id,price)
		else:
			offlineshop.SendSafeboxGetItem(id, False)
			self.ClearCachePos(self.PageGrid, id)

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)
		self.OnCloseQuestionDialog()
		return True

	def OnCloseQuestionDialog(self):
		if self.QuestionDialog == None:
			return
			
		self.QuestionDialog.Close()

		self.QuestionDialog.itemStock = None
		self.QuestionDialog = None
		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	def SelectEmptySlot(self, selectedSlotPos):
		if self.wBoard[PAGE_SAFEBOX].IsShow() or self.wBoard[PAGE_SHOP].IsShow():
			self.OverOutItem()
			if mousemodule.mouseController.isAttached():
				mousemodule.mouseController.DeattachObject()
			return
	
		isAttached = mousemodule.mouseController.isAttached()
		if isAttached:
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			mousemodule.mouseController.DeattachObject()

			attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)
			self.OpenInputPriceDialog(attachedInvenType, attachedSlotPos, self.PageGrid, selectedSlotPos)

	def OpenInputPriceDialog(self, window, slot, page, EmptyGridPos, editMode = False, skipDlg = False):
		if not self.priceInputDlg:
			tmp = MoneyInputDialogNew()
			tmp.SetAcceptEvent(ui.__mem_func__(self.AcceptInputPrice))
			tmp.SetCancelEvent(ui.__mem_func__(self.CancelInputPrice))

			self.priceInputDlg = tmp
		else:
			self.priceInputDlg.Close()

		if not self.priceInputDlg:
			return

		if editMode == False:
			itemVnum = player.GetItemIndex(window, slot)
			itemCount = player.GetItemCount(window, slot)
			item.SelectItem(itemVnum)

			if item.IsAntiFlag(item.ANTIFLAG_GIVE) or item.IsAntiFlag(item.ANTIFLAG_MYSHOP):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PRIVATE_SHOP_CANNOT_SELL_ITEM)
				return
		else:
			itemVnum = window
			itemCount = slot

		if not itemVnum:
			return

		self.priceInputDlg.SetData(itemVnum, itemCount)
		self.priceInputDlg.sourceWindowType = window
		self.priceInputDlg.sourceSlotPos = slot
		self.priceInputDlg.targetSlotPos = EmptyGridPos
		self.priceInputDlg.page = page
		self.priceInputDlg.CurrentPageGrid = self.PageGrid
		self.priceInputDlg.isEditMode = editMode

		if editMode == False:
			self.priceInputDlg.ClearPrice()

			self.priceInputDlg.inputValue.SetFocus()

			price = self.LoadInputPrice(player.GetItemIndex(window, slot))
			if not price:
				self.priceInputDlg.SetValue(DEFAULT_PRICE)
			else:
				count = player.GetItemCount(window, slot)
				if count > 1:
					price *= count
					if price > MAX_PRICE:
						price = MAX_PRICE

				self.priceInputDlg.SetValue(price)

		self.RefreshItemSlotInv()

		if skipDlg:
			self.AcceptInputPrice()
		else:
			self.priceInputDlg.Open()

	if app.USE_OFFLINESHOP_STACK_OPTION:
		def CountPosition(self, vnum, size):
			for k, v in self.tmpStackSlots.items():
				p = v.GetEmptyGrid(size)
				if p >= 0:
					if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
						itemVnum = v.GetItemIndex(p)
						if itemVnum == offlineshop.OFFLINESHOP_LOCKED_SLOT_ITEMVNUM:
							return -1

					v.PutItemGrid(p, size)
					v.SetItemSlot(p, vnum, 1)
					v.RefreshSlot()

					return p

			return -1

		def CountEmptyPosition(self, vnum, size):
			if len(self.tmpStackSlots) == 0:
				for i in xrange(PAGE_COUNT):
					tmp = ui.GridSlotWindow()
					tmp.ArrangeSlot(0, 10, 8, 32, 32, 0, 0)
					tmp.SetGridSpecial(10, 8)
					tmp.Hide()

					self.tmpStackSlots[i] = tmp

			for k, v in self.tmpStackSlots.items():
				v.ClearGrid()

				t = v.GetSlotCount()
				for i in xrange(t):
					itemVnum = self.itemSlot[k].GetItemIndex(i)
					if itemVnum:
						item.SelectItem(itemVnum)
						v.PutItemGrid(i, item.GetItemSize()[1])
						v.SetItemSlot(i, itemVnum, 1)
					else:
						v.ClearSlot(i)

				v.RefreshSlot()

			b = 0
			while (self.CountPosition(vnum, size) != -1):
				b += 1

			return b

	def AcceptInputPrice(self):
		if not self.priceInputDlg:
			return True

		Text = self.priceInputDlg.inputValue.GetText()

		if not Text:
			return True

		if int(Text) <= 0:
			return True

		attachedInvenType = self.priceInputDlg.sourceWindowType
		sourceSlotPos = self.priceInputDlg.sourceSlotPos
		targetSlotPos = self.priceInputDlg.targetSlotPos
		targetPage = self.priceInputDlg.page
		isEditMode = self.priceInputDlg.isEditMode

		self.SaveInputPrice(player.GetItemIndex(attachedInvenType, sourceSlotPos), player.GetItemCount(attachedInvenType, sourceSlotPos), int(Text))

		self.OverOutItem()

		if self.wBoard[PAGE_BUILDER].IsShow():
			for page in xrange(PAGE_COUNT):
				for privatePos, (itemWindowType, itemSlotIndex, priceInfo) in self.itemStockBuilder[page].items():
					if itemWindowType == attachedInvenType and itemSlotIndex == sourceSlotPos:
						del self.itemStockBuilder[page][privatePos]

			self.itemStockBuilder[targetPage][targetSlotPos] = (attachedInvenType, sourceSlotPos, long(Text))

			if self.priceInputDlg.IsEqualOn():
				if not self.priceInputDlg.itemSize:
					return

				self.RefreshItemSlot()

				if attachedInvenType == player.INVENTORY or attachedInvenType == player.DRAGON_SOUL_INVENTORY:
					maxC = player.INVENTORY_SLOT_COUNT if attachedInvenType == player.INVENTORY else player.DS_INVENTORY_COUNT
					for i in xrange(maxC):
						v = player.GetItemIndex(attachedInvenType, i)
						if not v:
							continue

						if v != self.priceInputDlg.itemVnum:
							continue

						if i == sourceSlotPos:
							continue

						c = player.GetItemCount(attachedInvenType, i)
						if c != self.priceInputDlg.itemCount:
							continue

						p, j = self.GetEmptyPosition(self.priceInputDlg.itemSize)
						if p == -1:
							break

						for page in xrange(PAGE_COUNT):
							for privatePos, (itemWindowType, itemSlotIndex, priceInfo) in self.itemStockBuilder[page].items():
								if itemWindowType == attachedInvenType and itemSlotIndex == i:
									del self.itemStockBuilder[page][privatePos]

						self.itemStockBuilder[p][j] = (attachedInvenType, i, long(Text))
						self.RefreshItemSlot()
		else:
			if isEditMode:
				if app.USE_OFFLINESHOP_STACK_OPTION:
					offlineshop.SendEditItem(self.priceInputDlg.page, long(Text), self.priceInputDlg.IsEqualOn())
				else:
					offlineshop.SendEditItem(self.priceInputDlg.page, long(Text))
			else:
				if app.USE_OFFLINESHOP_STACK_OPTION:
					if not self.wBoard[PAGE_MYSHOP].IsShow():
						return

					if not self.priceInputDlg.itemSize:
						return

					availSlots = self.CountEmptyPosition(self.priceInputDlg.itemVnum, self.priceInputDlg.itemSize)
					if availSlots == 0:
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_NO_EMPTY_SLOT)
						return

					offlineshop.SendAddItem(attachedInvenType, sourceSlotPos, long(Text), self.priceInputDlg.IsEqualOn(), availSlots)
				else:
					offlineshop.SendAddItem(attachedInvenType, sourceSlotPos, long(Text))

		self.RefreshItemSlot()
		self.RefreshItemSlotInv()

		self.priceInputDlg.Close()
		return True

	def RefreshItemSlotInv(self, isDestroy=False):
		if isDestroy:
			return
			
		if self.interface == None:
			return
	
		if self.interface.wndInventory:
			self.interface.wndInventory.RefreshItemSlot()
				
		# if self.interface.wndSpecialStorage:
			# self.interface.wndSpecialStorage.RefreshItemSlot()

	def CancelInputPrice(self, isDestroy = False):
		if not self.priceInputDlg:
			return

		self.priceInputDlg.Close()

		if not isDestroy:
			self.RefreshItemSlot()
			self.RefreshItemSlotInv()

		return True

	def AskClosePrivateShop(self):
		if self.QuestionDialog:
			self.OnCloseQuestionDialog()

		if not self.QuestionDialog:
			QuestionDialog = uicommon.QuestionDialog()
			QuestionDialog.SetText(localeinfo.PRIVATE_SHOP_CLOSE_QUESTION)
			QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.OnClosePrivateShop))
			QuestionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
			self.QuestionDialog = QuestionDialog

		self.QuestionDialog.Open()
		return True
	
	def OnClosePrivateShop(self):
		offlineshop.SendForceCloseShop()
		global CACHE_ITEMS_ID
		CACHE_ITEMS_ID = {}
		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)
		self.OnCloseQuestionDialog()
		return True

	def OnWithdrawAllItems(self):
		offlineshop.SendSafeboxGetAll()

	# >>> SECTION BEGIN USE_OFFLINESHOP relist-from-safebox (P6): withdraw safebox item(s) and
	# auto-stage them into the shop builder (or add to a live shop) at their last-used prices.
	# Async via OnUpdate polling: the withdraw lands the item in inventory; ProcessRelistArrivals
	# spots the newly-occupied slot (before/after diff) and stages/adds it. Items never priced
	# before are left in inventory. Triggers: Alt+rclick = one (works with or without a live shop);
	# Alt+Ctrl+rclick = all of that type; "Relist All" button = all (the last two only while
	# building a new shop). <<< END
	def __InvOccupiedSet(self):
		s = set()
		for slot in xrange(player.INVENTORY_SLOT_COUNT):
			if player.GetItemIndex(player.INVENTORY, slot):
				s.add(slot)
		return s

	def __StartRelistSession(self, expectVnums):
		if not self._relistActive:
			self._relistBefore = self.__InvOccupiedSet()
			self._relistClaimed = set()
			self._relistExpect = {}
			self._relistUnpriced = 0
			self._relistActive = True
		for v in expectVnums:
			if v:
				self._relistExpect[v] = self._relistExpect.get(v, 0) + 1
		self._relistTtl = 200
		if not self.hasLiveShop:
			# stage into the builder: show the builder grid so GetEmptyPosition packs against the
			# builder occupancy (not the safebox display), and the player watches items land
			self.__ChangePage(PAGE_BUILDER)
			self.RefreshItemSlot()

	def ProcessRelistArrivals(self):
		if not self._relistActive:
			return
		self._relistTtl -= 1
		if self._relistTtl <= 0 or not any(self._relistExpect.values()):
			self._relistActive = False
			if getattr(self, "_relistUnpriced", 0) > 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_RELIST_UNPRICED % self._relistUnpriced)
			self._relistUnpriced = 0
			return
		# building stages into the builder grid: it must be the rendered board, and we stage at most
		# ONE item per poll so RefreshItemSlot repacks the grid before the next GetEmptyPosition
		# (PutItemGrid is not reflected by GetEmptyGrid within the same frame -> same-poll collision).
		if not self.hasLiveShop and not self.wBoard[PAGE_BUILDER].IsShow():
			return
		for slot in xrange(player.INVENTORY_SLOT_COUNT):
			if slot in self._relistBefore or slot in self._relistClaimed:
				continue
			vnum = player.GetItemIndex(player.INVENTORY, slot)
			if not vnum:
				continue
			# only items this session withdrew; leave unrelated pickups (loot/mail/trade) alone.
			if self._relistExpect.get(vnum, 0) <= 0:
				continue
			self._relistExpect[vnum] -= 1
			self._relistClaimed.add(slot)
			self._relistTtl = 60
			price = self.LoadInputPrice(vnum)
			if not price or price <= 0:
				self._relistUnpriced = getattr(self, "_relistUnpriced", 0) + 1
				continue
			if self.hasLiveShop:
				if app.USE_OFFLINESHOP_STACK_OPTION:
					offlineshop.SendAddItem(player.INVENTORY, slot, long(price), False, 1)
				else:
					offlineshop.SendAddItem(player.INVENTORY, slot, long(price))
				return
			item.SelectItem(vnum)
			_, size = item.GetItemSize()
			page, pos = self.GetEmptyPosition(size)
			if pos < 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_NO_EMPTY_SLOT)
				self._relistActive = False
				return
			self.itemStockBuilder[page][pos] = (player.INVENTORY, slot, long(price))
			self.RefreshItemSlot()
			return

	def RelistFromSafebox(self, slotIndex, allSame):
		if not self.itemStock.has_key(slotIndex):
			return
		if allSame and self.hasLiveShop:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_RELIST_NEEDS_BUILDING)
			return
		itemId = self.itemStock[slotIndex][0]
		vnum = self.itemStock[slotIndex][1]
		if allSame:
			expectVnums = [it["vnum"] for it in self.wndShop.ShopSafeboxItems if it.get("vnum") == vnum]
		else:
			expectVnums = [vnum]
		self.__StartRelistSession(expectVnums)
		offlineshop.SendSafeboxGetItem(itemId, True if allSame else False)
		self.ClearCachePos(self.PageGrid, itemId)

	def OnRelistAllItems(self):
		if self.hasLiveShop:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_RELIST_NEEDS_BUILDING)
			return
		expectVnums = [it["vnum"] for it in self.wndShop.ShopSafeboxItems if it.get("vnum")]
		self.__StartRelistSession(expectVnums)
		offlineshop.SendSafeboxGetAll()

	def WithdrawMoney(self):
		if self.WithdrawQuestionDialog:
			return
		
		shopMoney = self.wndShop.ShopSafeboxValuteAmount
		if shopMoney <= 0:
			return

		# >>> SECTION BEGIN USE_OFFLINESHOP one-click yang collect (P6)
		# Collect the full vault balance in a single click; the server clamps to the
		# real balance. The legacy MoneyInputDialog path below is now unreachable but
		# preserved for a possible partial-withdraw revival. <<< END
		offlineshop.SendSafeboxGetValutes(shopMoney)
		return
		WithdrawQuestionDialog = uicommon.MoneyInputDialog()
		WithdrawQuestionDialog.SetTitle(localeinfo.EXCHANGE_MONEY)
		WithdrawQuestionDialog.SetMoneyHeaderText("Sum: ")
		WithdrawQuestionDialog.SetAcceptEvent(ui.__mem_func__(self.SumWithdraw)) 
		WithdrawQuestionDialog.SetCancelEvent(ui.__mem_func__(self.CloseSumWithdraw))
		WithdrawQuestionDialog.Open()
		WithdrawQuestionDialog.SetMaxLength(len(str(shopMoney)))
		WithdrawQuestionDialog.SetValue(shopMoney)
		WithdrawQuestionDialog.inputValue.SetEndPosition()	

		self.WithdrawQuestionDialog = WithdrawQuestionDialog

	def SumWithdraw(self):
		if not self.WithdrawQuestionDialog:
			return
		
		shopMoney = int(self.WithdrawQuestionDialog.GetText())

		if len(self.WithdrawQuestionDialog.GetText()) <= 0:
			return
		
		if int(self.WithdrawQuestionDialog.GetText()) > self.wndShop.ShopSafeboxValuteAmount:
			shopMoney = self.wndShop.ShopSafeboxValuteAmount

		offlineshop.SendSafeboxGetValutes(shopMoney)
			
		self.WithdrawQuestionDialog.Close()
		self.WithdrawQuestionDialog = None

	def CloseSumWithdraw(self):
		if not self.WithdrawQuestionDialog:
			return False

		self.WithdrawQuestionDialog.Close()
		self.WithdrawQuestionDialog = None
		return True

	def OnCreateShop(self):
		if not self.NameEdit.GetText():
			return

		if 0 == len(self.itemStockBuilder):
			return

		itemLst = []
		
		for page in xrange(PAGE_COUNT):
			for privatePos, (itemWindowType, itemSlotIndex, itemPrice) in self.itemStockBuilder[page].items():
				tupleinfo = (itemWindowType, itemSlotIndex, itemPrice)
				itemLst.append(tupleinfo)

		if (len(itemLst) == 0):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_EMPTY)
			return
		
		totaltime = 600 # 5Days
		
		itemTuple = tuple(itemLst)
		offlineshop.SendShopCreate(self.NameEdit.GetText(), totaltime, self.wndDecoration.GetTypeShop(), self.wndDecoration.GetTypeBanner(), itemTuple)

	def OnUpdate(self):
		if getattr(self, "_relistActive", False):
			self.ProcessRelistArrivals()
		if self.wBoard[PAGE_SHOP].IsShow():
			USE_SHOP_LIMIT_RANGE = 1500

			(x, y, z) = player.GetMainCharacterPosition()
			if abs(x - self.xShopStart) > USE_SHOP_LIMIT_RANGE or abs(y - self.yShopStart) > USE_SHOP_LIMIT_RANGE:
				self.Close()

	def AskIncreaseTimeShop(self):
		if self.QuestionDialog:
			self.OnCloseQuestionDialog()

		if not self.QuestionDialog:
			QuestionDialog = uicommon.QuestionDialog()
			QuestionDialog.SetText(localeinfo.OFFLINESHOP_REFILLTIME_COST)
			QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.OnRefillShopTime))
			QuestionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
			self.QuestionDialog = QuestionDialog

		self.QuestionDialog.Open()
		return True		

	def GetMaxRefill(self, ex_day):
		while True:
			if self.wndShop.ShopOpenInfo["duration"] + ex_day > 7200:
				ex_day -= 1
				continue

			break
			
		return ex_day

	def OnRefillShopTime(self):
		Extend1Day = self.GetMaxRefill(1440)

		if Extend1Day <= 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_MAX_DAYS)
			self.OnCloseQuestionDialog()
			return
			
		offlineshop.SendExtendTime(Extend1Day)

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)
		self.OnCloseQuestionDialog()
		return True


	def ClearCachePos(self, page, id):
		if CACHE_ITEMS_ID.has_key(page):
			if CACHE_ITEMS_ID[page].has_key(id):
				del CACHE_ITEMS_ID[page][id]

	def OpenDecoration(self):
		if self.wndDecoration.IsShow():
			self.wndDecoration.Hide()
		else:
			if app.USE_PREMIUM_FEATURES and constinfo.player_premium_type == player.PREMIUM_TYPE_NONE:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SHOP_DECORATION_JUST_PREMIUM_PLUS)
				return

			self.wndDecoration.Show()

	def __OpenHistoryWindow(self):
		if not self.wndHistory:
			try:
				self.wndHistory = HistoryWindow()
			except Exception as msg:
				dbg.TraceError(str(msg))
				app.Abort()

			offlineshop.SendHistoryRequest()
		else:
			if self.wndHistory.IsShow():
				self.wndHistory.Close()
			else:
				self.wndHistory.Open()
