# coding: latin_1

import app
import net
import player

import item
import snd
import shop
import guild
import wndMgr
import chat

import ui
import uicommon
import mousemodule
import localeinfo
import constinfo
import osfinfo

import systemSetting

if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

if app.USE_MULTIPLE_SHOP_BUY:
	import ime

	class MultipleBuyDialog(ui.ScriptWindow):
		MIN_WIDTH = 240
		TOOLTIP_FIXED_WIDTH = 220

		def AdjustPosition(self, pos):
			self.SetPosition(pos[0] + 2 + self.shopWindowInst.GetWidth(), pos[1])

		def Refresh(self):
			try:
				value = int(self.editLine.GetText())
			except:
				value = 0

			if value == 0:
				if self.toolTipItem:
					self.toolTipItem.ClearToolTip()
					self.toolTipItem.HideToolTip()

				self.SetSize(self.lastWidth, 90)
				self.board.SetSize(self.GetWidth(), self.GetHeight())
				self.titleBar.SetWidth(self.GetWidth() - 16)
				self.titleName.SetPosition((self.board.GetWidth() - 16) / 2, 4)

				self.btnAccept.Hide()
				self.btnClose.SetPosition(0, self.GetHeight() - 30)
				return

			if not self.toolTipItem:
				import uitooltip
				self.toolTipItem = uitooltip.ItemToolTip()
				self.toolTipItem.SetMultipleBuyDialog(True)
				self.toolTipItem.SetParent(self)
				self.toolTipItem.SetPosition(10, 56)

			self.toolTipItem.ClearToolTip()
			self.toolTipItem.toolTipWidth = self.TOOLTIP_FIXED_WIDTH
			self.toolTipItem.multipleBuyCount = value

			if app.ENABLE_SHOPEX_RENEWAL:
				priceType = shop.GetItemPriceType(self.pos)
				if priceType == 1:
					self.toolTipItem.SetShopItem(self.pos)
				elif priceType == 2:
					self.toolTipItem.SetShopItemBySecondaryCoin(self.pos)
				else:
					self.toolTipItem.SetShopItemByShopEx(self.pos, priceType)
			else:
				if shop.GetTabCoinType(self.shopWindowInst.tabIdx) == shop.SHOP_COIN_TYPE_GOLD:
					self.toolTipItem.SetShopItem(self.pos)
				else:
					self.toolTipItem.SetShopItemBySecondaryCoin(self.pos)

			if self.toolTipItem.toolTipWidth != self.TOOLTIP_FIXED_WIDTH:
				self.toolTipItem.toolTipWidth = self.TOOLTIP_FIXED_WIDTH
				self.toolTipItem.ResizeToolTip()
				self.toolTipItem.AlignTextLineHorizonalCenter()

			self.SetSize(max(self.MIN_WIDTH, self.toolTipItem.GetWidth() + 20), self.toolTipItem.GetHeight() + 56 + 36)
			self.board.SetSize(self.GetWidth(), self.GetHeight())
			self.titleBar.SetWidth(self.GetWidth() - 16)
			self.titleName.SetPosition((self.board.GetWidth() - 16) / 2, 4)

			self.btnClose.SetPosition(40, self.GetHeight() - 30)
			self.btnAccept.SetPosition(-40, self.GetHeight() - 30)

			self.btnClose.Show()
			self.btnAccept.Show()

			self.lastWidth = self.GetWidth()

			self.toolTipItem.ShowToolTip()

		def OnCloseQuestionDlg(self):
			if self.questionDlg:
				self.questionDlg.Close()

		def __OnValueUpdate(self):
			ui.EditLine.OnIMEUpdate(self.editLine)

			self.OnCloseQuestionDlg()

			text = self.editLine.GetText()
			if text.isdigit():
				try:
					maxval = shop.MAX_MULTIPLE_SHOP_BUY_COUNT
					val = min(maxval, int(text))

					if str(val) != text:
						self.editLine.SetText(str(maxval))
						ime.SetCursorPosition(-1)
						self.__OnValueUpdate()
						return
				except:
					self.editLine.SetText("1")
					ime.SetCursorPosition(-1)
					self.__OnValueUpdate()
					return

			self.Refresh()

		def SetValue(self, value):
			self.editLine.SetText(str(value))

			if not self.editLine.IsFocus():
				self.editLine.SetFocus()

			ime.SetCursorPosition(-1)
			self.__OnValueUpdate()

		def Open(self, pos):
			if shop.IsPrivateShop():
				return

			self.pos = pos

			self.SetValue(1)

			self.AdjustPosition(self.shopWindowInst.GetGlobalPosition())
			self.Show()

		def Close(self):
			self.OnCloseQuestionDlg()

			if self.editLine.IsFocus():
				self.editLine.KillFocus()

			if self.toolTipItem:
				self.toolTipItem.HideToolTip()

			self.Hide()

		def OnPressEscapeKey(self):
			self.shopWindowInst.Close()
			return True

		def OnAcceptQuestionDlg(self):
			if self.toolTipItem.IsShow():
				net.SendShopBuyPacket(self.questionDlg.pos, int(self.editLine.GetText()))

			self.Close()

		def Accept(self):
			if not self.questionDlg:
				self.questionDlg = uicommon.QuestionDialog()
				self.questionDlg.SetText(localeinfo.SHOP_MULTIPLE_BUY_PROCEED)
				self.questionDlg.SetAcceptEvent(ui.__mem_func__(self.OnAcceptQuestionDlg))
				self.questionDlg.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDlg))

			self.questionDlg.pos = self.pos
			self.questionDlg.Open()

		def Initialize(self):
			if self.isLoaded:
				return

			self.isLoaded = 1

			try:
				self.lastWidth = self.MIN_WIDTH

				pyScriptLoader = ui.PythonScriptLoader()
				pyScriptLoader.LoadScriptFile(self, "uiscript/multiplebuy_dialog.py")

				self.board = self.GetChild("ui_board")
				self.titleBar = self.GetChild("ui_titlebar")
				self.titleName = self.GetChild("ui_titlename")
				self.slotBar = self.GetChild("ui_slotbar")

				self.editLine = self.GetChild("ui_editline")
				self.editLine.OnIMEUpdate = ui.__mem_func__(self.__OnValueUpdate)
				self.editLine.OnPressEscapeKey = ui.__mem_func__(self.OnPressEscapeKey)

				self.btnAccept = self.GetChild("ui_button_accept")
				self.btnAccept.SetEvent(ui.__mem_func__(self.Accept))

				self.btnClose = self.GetChild("ui_button_close")
				self.btnClose.SetEvent(ui.__mem_func__(self.Close))

				self.toolTipItem = None
			except Exception as msg:
				import dbg
				dbg.TraceError(str(msg))
				app.Abort()

		def __init__(self, parent):
			ui.ScriptWindow.__init__(self)

			self.shopWindowInst = parent
			self.questionDlg = None

			self.isLoaded = 0

			# if app.ENABLE_WINDOW_SLIDE_EFFECT:
				# self.AddFlag("animated_board")

			self.Initialize()

		def Destroy(self):
			self.shopWindowInst = None

			if self.questionDlg:
				self.questionDlg.Close()
				del self.questionDlg
				self.questionDlg = None

			self.board = None
			self.titleBar = None
			self.titleName = None
			self.slotBar = None

			if self.editLine.IsFocus():
				self.editLine.KillFocus()

			self.editLine = None

			self.btnAccept.SetEvent(None)
			self.btnAccept = None

			self.btnClose.SetEvent(None)
			self.btnClose = None

			if self.toolTipItem:
				del self.toolTipItem
				self.toolTipItem = None

			self.ClearDictionary()

		def __del__(self):
			ui.ScriptWindow.__del__(self)

class ShopDialog(ui.ScriptWindow):
	if app.USE_MULTIPLE_SHOP_BUY:
		def OnMoveWindow(self, x, y):
			if app.ENABLE_WINDOW_POSITION_SAVE:
				uiwindowpositions.OnWindowMove("SHOP", x, y)
			if self.multipleBuyDlg:
				self.multipleBuyDlg.AdjustPosition(self.GetGlobalPosition())
	elif app.ENABLE_WINDOW_POSITION_SAVE:
		def OnMoveWindow(self, x, y):
			uiwindowpositions.OnWindowMove("SHOP", x, y)

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		# if app.ENABLE_WINDOW_SLIDE_EFFECT:
			# self.AddFlag("animated_board")

		self.tooltipItem = 0
		self.xShopStart = 0
		self.yShopStart = 0
		self.isRemoteShop = 0
		self.questionDialog = None
		self.popup = None
		self.attrWarningDialog = None
		self.itemBuyQuestionDialog = None
		self.interface = None

		if app.ENABLE_DYNAMIC_SHOP_SLOTSIZE:
			self.empty_slots = 0

		if app.USE_MULTIPLE_SHOP_BUY:
			self.multipleBuyDlg = None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __GetRealIndex(self, i):
		return self.tabIdx * shop.SHOP_SLOT_COUNT + i

	if app.ENABLE_DYNAMIC_SHOP_SLOTSIZE:
		def GetEmptySlots(self):
			emptyLines = 8
			for i in xrange(5):
				empty = 8
				for j in xrange(8):
					idx = self.__GetRealIndex(5 * j + i)
					itemIndex = shop.GetItemID(idx)
					if itemIndex:
						item.SelectItem(itemIndex)
						(w, h) = item.GetItemSize()
						empty -= h
				
				emptyLines = min(emptyLines, empty)
			
			return emptyLines

	def Refresh(self):
		getItemID = shop.GetItemID
		getItemCount = shop.GetItemCount
		setItemID = self.itemSlotWindow.SetItemSlot

		for i in xrange(shop.SHOP_SLOT_COUNT):
			idx = self.__GetRealIndex(i)
			itemCount = getItemCount(idx)
			if itemCount <= 1:
				itemCount = 0
			setItemID(i, getItemID(idx), itemCount)

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				changelookvnum = shop.GetItemChangeLookVnum(idx)
				if not changelookvnum == 0:
					self.itemSlotWindow.SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")
				else:
					self.itemSlotWindow.EnableSlotCoverImage(i, False)

			if app.ENABLE_EXTENDED_BLEND_AFFECT:
				if osfinfo.IS_EXTENDED_BLEND_POTION(getItemID(idx)):
					self.itemSlotWindow.SetSlotCoverImage(i, "d:/ymir work/ui/acce/ingame_convert_mark_02.tga")
				elif osfinfo.IS_BLEND_POTION(getItemID(idx)):
					self.itemSlotWindow.SetSlotCoverImage(i, "icon/item/trade.tga")
				else:
					self.itemSlotWindow.EnableSlotCoverImage(i, False)

			# ShopEx: show the account-bound lock overlay on the slot itself (mirrors
			# uiinventory). Runs last so it wins over change-look / blend covers above.
			fishVnum = getItemID(idx)
			if fishVnum >= 37863 and fishVnum <= 37892:
				self.itemSlotWindow.SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")

			if app.ENABLE_SHOPEX_ACCOUNT_BIND_SELL:
				if shop.IsItemAccountBound(idx):
					self.itemSlotWindow.SetSlotCoverImage(i, "icon/item/account_locked.png")
				elif not (app.ENABLE_CHANGE_LOOK_SYSTEM or app.ENABLE_EXTENDED_BLEND_AFFECT):
					self.itemSlotWindow.EnableSlotCoverImage(i, False)

			# ShopEx: slots whose per-character stock is used up get the lock overlay,
			# so an exhausted item reads as unavailable without hovering it.
			if app.ENABLE_SHOPEX_DAILY_LIMIT:
				stockLimit = shop.GetItemCharDailyLimit(idx)
				if stockLimit > 0 and shop.GetItemCharDailyBought(idx) >= stockLimit:
					itemVnum = getItemID(idx)
					lockImage = "d:/ymir work/ui/new_guild/shop/32x32_background_lock.png"
					if itemVnum:
						item.SelectItem(itemVnum)
						(w, h) = item.GetItemSize()
						if h >= 3:
							lockImage = "d:/ymir work/ui/new_guild/shop/3slot_background_lock.png"
						elif h == 2:
							lockImage = "d:/ymir work/ui/new_guild/shop/2slot_background_lock.png"
					self.itemSlotWindow.SetSlotCoverImage(i, lockImage)

			# Guild shop: overlay the lock on slots whose required guild level
			# is above the guild's. Runs last so it wins over the covers above.
			isGuildShop = getattr(shop, "IsGuildShop", None)
			if isGuildShop and shop.IsGuildShop():
				getReqLvl = getattr(shop, "GetItemRequiredLevel", None)
				reqLvl = getReqLvl(idx) if getReqLvl else 0
				getLvl = getattr(guild, "GetGuildLevel", None)
				if reqLvl > (getLvl() if getLvl else 0):
					itemVnum = getItemID(idx)
					lockImage = "d:/ymir work/ui/new_guild/shop/32x32_background_lock.png"
					if itemVnum:
						item.SelectItem(itemVnum)
						(w, h) = item.GetItemSize()
						if h >= 3:
							lockImage = "d:/ymir work/ui/new_guild/shop/3slot_background_lock.png"
						elif h == 2:
							lockImage = "d:/ymir work/ui/new_guild/shop/2slot_background_lock.png"
					self.itemSlotWindow.SetSlotCoverImage(i, lockImage)
				elif not (app.ENABLE_CHANGE_LOOK_SYSTEM or app.ENABLE_EXTENDED_BLEND_AFFECT or app.ENABLE_SHOPEX_ACCOUNT_BIND_SELL):
					self.itemSlotWindow.EnableSlotCoverImage(i, False)

		wndMgr.RefreshSlot(self.itemSlotWindow.GetWindowHandle())

	def SetItemData(self, pos, itemID, itemCount, itemPrice):
		shop.SetItemData(pos, itemID, itemCount, itemPrice)

	def LoadDialog(self):
		try:
			PythonScriptLoader = ui.PythonScriptLoader()
			PythonScriptLoader.LoadScriptFile(self, "UIScript/shopdialog.py")
		except:
			import exception
			exception.Abort("ShopDialog.LoadDialog.LoadObject")

		smallTab1 = None
		smallTab2 = None
		smallTab3 = None
		if app.ENABLE_SHOPEX_TAB4:
			xSmallTab1 = None
			xSmallTab2 = None
			xSmallTab3 = None
			xSmallTab4 = None
		middleTab1 = None
		middleTab2 = None

		try:
			GetObject = self.GetChild
			if app.ENABLE_DYNAMIC_SHOP_SLOTSIZE:
				self.board = GetObject("board")
			
			self.itemSlotWindow = GetObject("ItemSlot")
			self.btnBuy = GetObject("BuyButton")
			self.btnSell = GetObject("SellButton")
			self.btnClose = GetObject("CloseButton")
			self.titleBar = GetObject("TitleBar")
			middleTab1 = GetObject("MiddleTab1")
			middleTab2 = GetObject("MiddleTab2")
			smallTab1 = GetObject("SmallTab1")
			smallTab2 = GetObject("SmallTab2")
			smallTab3 = GetObject("SmallTab3")
			if app.ENABLE_SHOPEX_TAB4:
				xSmallTab1 = GetObject("xSmallTab1")
				xSmallTab2 = GetObject("xSmallTab2")
				xSmallTab3 = GetObject("xSmallTab3")
				xSmallTab4 = GetObject("xSmallTab4")

		except:
			import exception
			exception.Abort("ShopDialog.LoadDialog.BindObject")

		self.itemSlotWindow.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
		self.itemSlotWindow.SAFE_SetButtonEvent("LEFT", "EMPTY", self.SelectEmptySlot)
		self.itemSlotWindow.SAFE_SetButtonEvent("LEFT", "EXIST", self.SelectItemSlot)
		self.itemSlotWindow.SAFE_SetButtonEvent("RIGHT", "EXIST", self.UnselectItemSlot)

		self.itemSlotWindow.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		self.itemSlotWindow.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		self.btnBuy.SetToggleUpEvent(ui.__mem_func__(self.CancelShopping))
		self.btnBuy.SetToggleDownEvent(ui.__mem_func__(self.OnBuy))

		self.btnSell.SetToggleUpEvent(ui.__mem_func__(self.CancelShopping))
		self.btnSell.SetToggleDownEvent(ui.__mem_func__(self.OnSell))

		self.btnClose.SetEvent(ui.__mem_func__(self.AskClosePrivateShop))

		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))

		if app.ENABLE_SHOPEX_TAB4:
			self.xSmallRadioButtonGroup = ui.RadioButtonGroup.Create([
				[xSmallTab1, ui.__mem_func__(self.OnClickTabButton), None],
				[xSmallTab2, ui.__mem_func__(self.OnClickTabButton), None],
				[xSmallTab3, ui.__mem_func__(self.OnClickTabButton), None],
				[xSmallTab4, ui.__mem_func__(self.OnClickTabButton), None],
			])
		self.smallRadioButtonGroup = ui.RadioButtonGroup.Create([
			[smallTab1, ui.__mem_func__(self.OnClickTabButton), None],
			[smallTab2, ui.__mem_func__(self.OnClickTabButton), None],
			[smallTab3, ui.__mem_func__(self.OnClickTabButton), None]
		])
		self.middleRadioButtonGroup = ui.RadioButtonGroup.Create([
			[middleTab1, ui.__mem_func__(self.OnClickTabButton), None],
			[middleTab2, ui.__mem_func__(self.OnClickTabButton), None]
		])

		self.__HideMiddleTabs()
		self.__HideSmallTabs()
		if app.ENABLE_SHOPEX_TAB4:
			self.__HideXSmallTabs()

		self.tabIdx = 0
		self.coinType = shop.SHOP_COIN_TYPE_GOLD


		self.Refresh()

	def __ShowBuySellButton(self):
		self.btnBuy.Show()
		self.btnSell.Show()

	def __ShowMiddleTabs(self):
		self.middleRadioButtonGroup.Show()

	def __ShowSmallTabs(self):
		self.smallRadioButtonGroup.Show()

	if app.ENABLE_SHOPEX_TAB4:
		def __ShowXSmallTabs(self):
			self.xSmallRadioButtonGroup.Show()

	def __HideBuySellButton(self):
		self.btnBuy.Hide()
		self.btnSell.Hide()

	def __HideMiddleTabs(self):
		self.middleRadioButtonGroup.Hide()

	def __HideSmallTabs(self):
		self.smallRadioButtonGroup.Hide()

	if app.ENABLE_SHOPEX_TAB4:
		def __HideXSmallTabs(self):
			self.xSmallRadioButtonGroup.Hide()

	def __SetTabNames(self, pos = False):
		if shop.GetTabCount() == 2:
			if not pos:
				self.middleRadioButtonGroup.SetText(0, shop.GetTabName(0))
				self.middleRadioButtonGroup.SetText(1, shop.GetTabName(1))
			
			if app.ENABLE_DYNAMIC_SHOP_SLOTSIZE:
				btn = self.GetChild("MiddleTab1")
				(x, y) = btn.GetLocalPosition()
				btn.SetPosition(x, 295 - self.empty_slots)
				btn = self.GetChild("MiddleTab2")
				(x, y) = btn.GetLocalPosition()
				btn.SetPosition(x, 295 - self.empty_slots)
		elif shop.GetTabCount() == 3:
			if not pos:
				self.smallRadioButtonGroup.SetText(0, shop.GetTabName(0))
				self.smallRadioButtonGroup.SetText(1, shop.GetTabName(1))
				self.smallRadioButtonGroup.SetText(2, shop.GetTabName(2))
			
			if app.ENABLE_DYNAMIC_SHOP_SLOTSIZE:
				btn = self.GetChild("SmallTab1")
				(x, y) = btn.GetLocalPosition()
				btn.SetPosition(x, 295 - self.empty_slots)
				btn = self.GetChild("SmallTab2")
				(x, y) = btn.GetLocalPosition()
				btn.SetPosition(x, 295 - self.empty_slots)
				btn = self.GetChild("SmallTab3")
				(x, y) = btn.GetLocalPosition()
				btn.SetPosition(x, 295 - self.empty_slots)
		elif shop.GetTabCount() == 4 and app.ENABLE_SHOPEX_TAB4:
			if not pos:
				self.xSmallRadioButtonGroup.SetText(0, shop.GetTabName(0))
				self.xSmallRadioButtonGroup.SetText(1, shop.GetTabName(1))
				self.xSmallRadioButtonGroup.SetText(2, shop.GetTabName(2))
				self.xSmallRadioButtonGroup.SetText(3, shop.GetTabName(3))
			
			if app.ENABLE_DYNAMIC_SHOP_SLOTSIZE:
				btn = self.GetChild("xSmallTab1")
				(x, y) = btn.GetLocalPosition()
				btn.SetPosition(x, 295 - self.empty_slots)
				btn = self.GetChild("xSmallTab2")
				(x, y) = btn.GetLocalPosition()
				btn.SetPosition(x, 295 - self.empty_slots)
				btn = self.GetChild("xSmallTab3")
				(x, y) = btn.GetLocalPosition()
				btn.SetPosition(x, 295 - self.empty_slots)
				btn = self.GetChild("xSmallTab4")
				(x, y) = btn.GetLocalPosition()
				btn.SetPosition(x, 295 - self.empty_slots)

	def Destroy(self):
		self.Close()

		if app.USE_MULTIPLE_SHOP_BUY and self.multipleBuyDlg:
			self.multipleBuyDlg.Destroy()
			del self.multipleBuyDlg
			self.multipleBuyDlg = None

		self.ClearDictionary()

		self.tooltipItem = 0
		if app.ENABLE_DYNAMIC_SHOP_SLOTSIZE:
			self.board = None
		
		self.itemSlotWindow = 0
		self.btnBuy = 0
		self.btnSell = 0
		self.btnClose = 0
		self.titleBar = 0
		self.questionDialog = None
		self.popup = None
		self.attrWarningDialog = None

	def Open(self, vid, remote = 0):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "SHOP")
		isPrivateShop = False
		isMainPlayerPrivateShop = False

		import chr
		if remote or chr.IsNPC(vid):
			isPrivateShop = False
		else:
			isPrivateShop = True

		if app.ENABLE_DYNAMIC_SHOP_SLOTSIZE:
			self.board.SetSize(184, 328)
			self.itemSlotWindow.ArrangeSlot(0, 5, 8, 32, 32, 0, 0)
			self.itemSlotWindow.RefreshSlot()
			self.itemSlotWindow.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
			(x, y) = self.btnBuy.GetLocalPosition()
			self.btnBuy.SetPosition(x, 295)
			(x, y) = self.btnSell.GetLocalPosition()
			self.btnSell.SetPosition(x, 295)
		
		if player.IsMainCharacterIndex(vid):
			isMainPlayerPrivateShop = True

			self.btnBuy.Hide()
			self.btnSell.Hide()
			self.btnClose.Show()
		else:
			if app.ENABLE_DYNAMIC_SHOP_SLOTSIZE:
				self.empty_slots = 32 * self.GetEmptySlots()
				self.SetSize(184, 328 - self.empty_slots)
				self.board.SetSize(184, 328 - self.empty_slots)
				self.itemSlotWindow.ArrangeSlot(0, 5, 8 - self.empty_slots / 32, 32, 32, 0, 0)
				self.itemSlotWindow.RefreshSlot()
				self.itemSlotWindow.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
				(x, y) = self.btnBuy.GetLocalPosition()
				self.btnBuy.SetPosition(x, 295 - self.empty_slots)
				(x, y) = self.btnSell.GetLocalPosition()
				self.btnSell.SetPosition(x, 295 - self.empty_slots)
			
			isMainPlayerPrivateShop = False

			self.btnBuy.Show()
			self.btnSell.Show()
			self.btnClose.Hide()

		shop.Open(isPrivateShop, isMainPlayerPrivateShop)

		self.tabIdx = 0

		if isPrivateShop:
			self.__HideMiddleTabs()
			self.__HideSmallTabs()
		else:
			if shop.GetTabCount() == 1:
				self.__ShowBuySellButton()
				self.__HideMiddleTabs()
				self.__HideSmallTabs()
				if app.ENABLE_SHOPEX_TAB4:
					self.__HideXSmallTabs()
			elif shop.GetTabCount() == 2:
				self.__HideBuySellButton()
				self.__ShowMiddleTabs()
				self.__HideSmallTabs()
				if app.ENABLE_SHOPEX_TAB4:
					self.__HideXSmallTabs()
				self.__SetTabNames()
				if app.ENABLE_SHOPEX_RENEWAL:
					self.middleRadioButtonGroup.OnClick(0)
				else:
					self.middleRadioButtonGroup.OnClick(1)
			elif shop.GetTabCount() == 3:
				self.__HideBuySellButton()
				self.__HideMiddleTabs()
				self.__ShowSmallTabs()
				if app.ENABLE_SHOPEX_TAB4:
					self.__HideXSmallTabs()
				self.__SetTabNames()
				if app.ENABLE_SHOPEX_RENEWAL:
					self.smallRadioButtonGroup.OnClick(0)
				else:
					self.middleRadioButtonGroup.OnClick(1)
			elif shop.GetTabCount() == 4 and app.ENABLE_SHOPEX_TAB4:
				self.__HideBuySellButton()
				self.__HideMiddleTabs()
				self.__HideSmallTabs()
				self.__ShowXSmallTabs()
				self.__SetTabNames()
				self.xSmallRadioButtonGroup.OnClick(0)

		self.Refresh()
		self.SetTop()

		self.Show()

		(self.xShopStart, self.yShopStart, z) = player.GetMainCharacterPosition()
		self.isRemoteShop = (vid == 0)	# owner_vid 0 = from-anywhere shop (item-shop / remote), no NPC anchor

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "SHOP")
		if app.USE_MULTIPLE_SHOP_BUY and self.multipleBuyDlg:
			self.multipleBuyDlg.Close()

		print("uishop.py Close")
		if app.WJ_ENABLE_TRADABLE_ICON:
			if self.interface:
				self.interface.SetOnTopWindow(player.ON_TOP_WND_NONE)
				self.interface.RefreshMarkInventoryBag()

		if self.itemBuyQuestionDialog:
			self.itemBuyQuestionDialog.Close()
			self.itemBuyQuestionDialog = None
			constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

		if self.questionDialog:
			self.OnCloseQuestionDialog()

		shop.Close()
		net.SendShopEndPacket()
		self.CancelShopping()
		self.tooltipItem.HideToolTip()
		self.Hide()

	def GetIndexFromSlotPos(self, slotPos):
		return self.tabIdx * shop.SHOP_SLOT_COUNT + slotPos

	def OnClickTabButton(self, idx):
		self.tabIdx = idx
		if app.ENABLE_DYNAMIC_SHOP_SLOTSIZE:
			self.empty_slots = 32 * self.GetEmptySlots()
			self.SetSize(184, 328 - self.empty_slots)
			self.board.SetSize(184, 328 - self.empty_slots)
			self.itemSlotWindow.ArrangeSlot(0, 5, 8 - self.empty_slots / 32, 32, 32, 0, 0)
			self.itemSlotWindow.RefreshSlot()
			self.itemSlotWindow.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
			(x, y) = self.btnBuy.GetLocalPosition()
			self.btnBuy.SetPosition(x, 295 - self.empty_slots)
			(x, y) = self.btnSell.GetLocalPosition()
			self.btnSell.SetPosition(x, 295 - self.empty_slots)
			
			self.__SetTabNames(True)
			self.Refresh()
			return
		else:
			self.Refresh()

	def AskClosePrivateShop(self):
		questionDialog = uicommon.QuestionDialog()
		questionDialog.SetText(localeinfo.PRIVATE_SHOP_CLOSE_QUESTION)
		questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnClosePrivateShop))
		questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
		questionDialog.Open()
		self.questionDialog = questionDialog

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

		return True

	def OnClosePrivateShop(self):
		net.SendChatPacket("/close_shop")
		self.OnCloseQuestionDialog()
		return True

	def OnPressEscapeKey(self):
		self.Close()
		return True

#	def OnPressExitKey(self):
#		self.Close()
#		return True

	def OnBuy(self):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SHOP_BUY_INFO)
		app.SetCursor(app.BUY)
		self.btnSell.SetUp()

	def OnSell(self):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SHOP_SELL_INFO)
		app.SetCursor(app.SELL)
		self.btnBuy.SetUp()

	def CancelShopping(self):
		self.btnBuy.SetUp()
		self.btnSell.SetUp()
		app.SetCursor(app.NORMAL)

	def __OnClosePopupDialog(self):
		self.pop = None
		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	def SellAttachedItem(self):
		if shop.IsPrivateShop():
			mousemodule.mouseController.DeattachObject()
			return

		attachedSlotType = mousemodule.mouseController.GetAttachedType()
		attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
		attachedCount = mousemodule.mouseController.GetAttachedItemCount()
		if localeinfo.IsBRAZIL() == 0:
			attachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()

		if player.IsEquipmentSlot(attachedSlotPos):
			return

		if app.ENABLE_SOUL_BIND_SYSTEM:
			if player.GetItemSealDate(attachedSlotType, attachedSlotPos) == -1 or player.GetItemSealDate(attachedSlotType, attachedSlotPos) > 0:
				mousemodule.mouseController.DeattachObject()
				return

		if player.SLOT_TYPE_INVENTORY == attachedSlotType or player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedSlotType or\
			(player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedSlotType or\
			player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedSlotType or\
			player.SLOT_TYPE_STONE_INVENTORY == attachedSlotType or\
			player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedSlotType or\
			player.SLOT_TYPE_ENCHANT_INVENTORY == attachedSlotType or\
			player.SLOT_TYPE_POTS_INVENTORY == attachedSlotType):

			if localeinfo.IsBRAZIL():
				itemIndex = player.GetItemIndex(attachedSlotPos)
				item.SelectItem(itemIndex)
			else:
				item.SelectItem(attachedItemIndex)

			if item.IsAntiFlag(item.ANTIFLAG_SELL):
				popup = uicommon.PopupDialog()
				popup.SetText(localeinfo.SHOP_CANNOT_SELL_ITEM)
				popup.SetAcceptEvent(self.__OnClosePopupDialog)
				popup.Open()
				self.popup = popup
				return

			hasAttr = False
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				if player.GetItemAttribute(attachedSlotPos, i)[0] > 0:
					hasAttr = True
					break

			if hasAttr:
				self.__ShowAttrWarningSell(attachedSlotPos, attachedCount, attachedSlotType)
				return

			itemtype = player.INVENTORY

			if localeinfo.IsBRAZIL() == 0:
				if player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedSlotType:
					itemtype = player.DRAGON_SOUL_INVENTORY

			if player.IsValuableItem(itemtype, attachedSlotPos):
				itemPrice = item.GetISellItemPrice()

				if item.Is1GoldItem():
					itemPrice = attachedCount / itemPrice / 5
				else:
					itemPrice = itemPrice * max(1, attachedCount) / 5

				itemName = item.GetItemName()

				questionDialog = uicommon.QuestionDialog()
				questionDialog.SetText(localeinfo.DO_YOU_SELL_ITEM(itemName, attachedCount, itemPrice))

				questionDialog.SetAcceptEvent(lambda arg1=attachedSlotPos, arg2=attachedCount, arg3 = itemtype: self.OnSellItem(arg1, arg2, arg3))
				questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
				questionDialog.Open()
				self.questionDialog = questionDialog

				constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)
			else:
				self.OnSellItem(attachedSlotPos, attachedCount, itemtype)
		else:
			snd.PlaySound("sound/ui/loginfail.wav")

		mousemodule.mouseController.DeattachObject()

	def __ShowAttrWarningSell(self, slotPos, count, slotType):
		if self.attrWarningDialog:
			self.attrWarningDialog.Close()
			self.attrWarningDialog = None

		attrWarningDialog = uicommon.QuestionDialog()
		attrWarningDialog.SetText(localeinfo.ITEM_ATTR_WARNING, True)
		attrWarningDialog.SetAcceptText(localeinfo.ITEM_ATTR_WARNING_YES)
		attrWarningDialog.SetCancelText(localeinfo.ITEM_ATTR_WARNING_NO)
		attrWarningDialog.SetAcceptEvent(lambda: self.__OnAttrWarningSellAccept(slotPos, count, slotType))
		attrWarningDialog.SetCancelEvent(lambda: self.__OnAttrWarningSellCancel())
		attrWarningDialog.Open()
		self.attrWarningDialog = attrWarningDialog

	def __OnAttrWarningSellAccept(self, slotPos, count, slotType):
		if self.attrWarningDialog:
			self.attrWarningDialog.Close()
			self.attrWarningDialog = None

		itemtype = player.INVENTORY
		if localeinfo.IsBRAZIL() == 0:
			if slotType == player.SLOT_TYPE_DRAGON_SOUL_INVENTORY:
				itemtype = player.DRAGON_SOUL_INVENTORY

		if player.IsValuableItem(itemtype, slotPos):
			itemIndex = player.GetItemIndex(slotPos)
			item.SelectItem(itemIndex)
			itemPrice = item.GetISellItemPrice()
			if item.Is1GoldItem():
				itemPrice = count / itemPrice / 5
			else:
				itemPrice = itemPrice * max(1, count) / 5
			itemName = item.GetItemName()
			questionDialog = uicommon.QuestionDialog()
			questionDialog.SetText(localeinfo.DO_YOU_SELL_ITEM(itemName, count, itemPrice))
			questionDialog.SetAcceptEvent(lambda arg1=slotPos, arg2=count, arg3=itemtype: self.OnSellItem(arg1, arg2, arg3))
			questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
			questionDialog.Open()
			self.questionDialog = questionDialog
			constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)
		else:
			self.OnSellItem(slotPos, count, itemtype)

		mousemodule.mouseController.DeattachObject()

	def __OnAttrWarningSellCancel(self):
		if self.attrWarningDialog:
			self.attrWarningDialog.Close()
			self.attrWarningDialog = None
		mousemodule.mouseController.DeattachObject()

	def OnSellItem(self, slotPos, count, itemtype):
		net.SendShopSellPacketNew(slotPos, count, itemtype)
		snd.PlaySound("sound/ui/money.wav")
		self.OnCloseQuestionDialog()

	def OnCloseQuestionDialog(self):
		if not self.questionDialog:
			return

		self.questionDialog.Close()
		self.questionDialog = None
		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	def SelectEmptySlot(self, selectedSlotPos):
		isAttached = mousemodule.mouseController.isAttached()
		if isAttached:
			self.SellAttachedItem()

	def UnselectItemSlot(self, selectedSlotPos):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		pos = self.__GetRealIndex(selectedSlotPos)

		if shop.IsPrivateShop():
			net.SendShopBuyPacket(pos)
		else:
			if app.IsPressed(app.DIK_LSHIFT):
				itemVnum = shop.GetItemID(pos)
				isBox = 1 if item.GetItemTypeByVnum(itemVnum) == item.ITEM_TYPE_GIFTBOX else 0
				import wiki
				wiki.GetBaseClass().OpenSpecialWikiPage(itemVnum,isBox)
				return

			if app.USE_MULTIPLE_SHOP_BUY and app.IsPressed(app.DIK_LCONTROL):
				if not self.multipleBuyDlg:
					self.multipleBuyDlg = MultipleBuyDialog(self)

				self.multipleBuyDlg.Open(pos)
				return

			net.SendShopBuyPacket(pos)

	def SelectItemSlot(self, selectedSlotPos):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		isAttached = mousemodule.mouseController.isAttached()
		selectedSlotPos = self.__GetRealIndex(selectedSlotPos)

		if app.IsPressed(app.DIK_LSHIFT) and app.ENABLE_RENDER_TARGET:
			if uiRenderTarget.IsCanShowItems(shop.GetItemID(selectedSlotPos)):
				itemVnum = shop.GetItemID(selectedSlotPos)
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler:
					interfaceHandler.OpenRenderTargetWindow(0, itemVnum)
					return

		if isAttached:
			self.SellAttachedItem()
		else:
			if True == shop.IsMainPlayerPrivateShop():
				return

			curCursorNum = app.GetCursor()
			if app.BUY == curCursorNum:
				self.AskBuyItem(selectedSlotPos)
			elif app.SELL == curCursorNum:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SHOP_SELL_INFO)
			else:
				selectedItemID = shop.GetItemID(selectedSlotPos)
				itemCount = shop.GetItemCount(selectedSlotPos)

				type = player.SLOT_TYPE_SHOP
				if shop.IsPrivateShop():
					type = player.SLOT_TYPE_PRIVATE_SHOP

				mousemodule.mouseController.AttachObject(self, type, selectedSlotPos, selectedItemID, itemCount)
				mousemodule.mouseController.SetCallBack("INVENTORY", ui.__mem_func__(self.DropToInventory))
				snd.PlaySound("sound/ui/pick.wav")

	def DropToInventory(self):
		attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
		self.AskBuyItem(attachedSlotPos)

	def AskBuyItem(self, slotPos, count=1):
		slotPos = self.__GetRealIndex(slotPos)

		isGuildShop = getattr(shop, "IsGuildShop", None)
		if isGuildShop and shop.IsGuildShop():
			getReqLvl = getattr(shop, "GetItemRequiredLevel", None)
			reqLvl = int(getReqLvl(slotPos)) if getReqLvl else 0
			getLvl = getattr(guild, "GetGuildLevel", None)
			if reqLvl > (getLvl() if getLvl else 0):
				chat.AppendChat(chat.CHAT_TYPE_INFO, getattr(localeinfo, "GUILD_SHOP_REQUIRES_LEVEL", "Requires Guild Lv.%d") % reqLvl)
				return

		if app.ENABLE_SHOPEX_DAILY_LIMIT:
			stockLimit = shop.GetItemCharDailyLimit(slotPos)
			if stockLimit > 0 and shop.GetItemCharDailyBought(slotPos) >= stockLimit:
				chat.AppendChat(chat.CHAT_TYPE_INFO, getattr(localeinfo, "SHOPEX_DAILY_OVER", "Out of stock - come back after the restock."))
				return

		itemIndex = shop.GetItemID(slotPos)
		itemPrice = shop.GetItemPrice(slotPos)
		itemCount = shop.GetItemCount(slotPos)

		item.SelectItem(itemIndex)
		itemName = item.GetItemName()

		itemBuyQuestionDialog = uicommon.QuestionDialog()
		if app.ENABLE_CHEQUE_SYSTEM:
			itemBuyQuestionDialog.SetText(localeinfo.DO_YOU_BUY_ITEM(itemName, itemCount, localeinfo.NumberToMoneyString(itemPrice), shop.GetItemPriceCheque(slotPos)))
		else:
			itemBuyQuestionDialog.SetText(localeinfo.DO_YOU_BUY_ITEM(itemName, itemCount, localeinfo.NumberToMoneyString(itemPrice)))

		itemBuyQuestionDialog.SetAcceptEvent(lambda arg=True: self.AnswerBuyItem(arg))
		itemBuyQuestionDialog.SetCancelEvent(lambda arg=False: self.AnswerBuyItem(arg))
		itemBuyQuestionDialog.Open()
		itemBuyQuestionDialog.pos = slotPos
		itemBuyQuestionDialog.count = count

		self.itemBuyQuestionDialog = itemBuyQuestionDialog

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def AnswerBuyItem(self, flag):
		if flag:
			pos = self.itemBuyQuestionDialog.pos
			for i in xrange(self.itemBuyQuestionDialog.count):
				net.SendShopBuyPacket(pos)

		self.itemBuyQuestionDialog.Close()
		self.itemBuyQuestionDialog = None

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def OverInItem(self, slotIndex):
		slotIndex = self.__GetRealIndex(slotIndex)
		if mousemodule.mouseController.isAttached():
			return

		if 0 != self.tooltipItem:
			if app.ENABLE_SHOPEX_RENEWAL:
				PriceType = shop.GetItemPriceType(slotIndex)
				if PriceType == 1:
					self.tooltipItem.SetShopItem(slotIndex)
				elif PriceType == 2:
					self.tooltipItem.SetShopItemBySecondaryCoin(slotIndex)
				else:
					self.tooltipItem.SetShopItemByShopEx(slotIndex, PriceType)
			else:
				if shop.SHOP_COIN_TYPE_GOLD == shop.GetTabCoinType(self.tabIdx):
					self.tooltipItem.SetShopItem(slotIndex)
				else:
					self.tooltipItem.SetShopItemBySecondaryCoin(slotIndex)

			isGuildShop = getattr(shop, "IsGuildShop", None)
			if isGuildShop and shop.IsGuildShop():
				getReqLvl = getattr(shop, "GetItemRequiredLevel", None)
				reqLvl = int(getReqLvl(slotIndex)) if getReqLvl else 0
				getLvl = getattr(guild, "GetGuildLevel", None)
				self.tooltipItem.AppendSpace(5)
				if reqLvl > (getLvl() if getLvl else 0):
					self.tooltipItem.AppendTextLine(getattr(localeinfo, "GUILD_SHOP_REQUIRES_LEVEL", "Requires Guild Lv.%d") % reqLvl, 0xffff4444)
				self.tooltipItem.ShowToolTip()

	def OverOutItem(self):
		if 0 != self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OnUpdate(self):
		if self.isRemoteShop:
			# From-anywhere shops (item-shop / remote button, owner_vid 0) have no NPC anchor, so the
			# 'walked too far from where it opened' auto-close does not apply.
			return

		USE_SHOP_LIMIT_RANGE = 1000

		(x, y, z) = player.GetMainCharacterPosition()
		if abs(x - self.xShopStart) > USE_SHOP_LIMIT_RANGE or abs(y - self.yShopStart) > USE_SHOP_LIMIT_RANGE:
			self.Close()

	if app.WJ_ENABLE_TRADABLE_ICON:
		def CantSellInvenItem(self, slotIndex):
			itemIndex = player.GetItemIndex(slotIndex)

			if itemIndex:
				if app.ENABLE_SOUL_BIND_SYSTEM:
					if player.GetItemSealDate(player.INVENTORY, slotIndex) == -1 or player.GetItemSealDate(player.INVENTORY, slotIndex) > 0:
						return True

				return player.IsAntiFlagBySlot(slotIndex, item.ANTIFLAG_SELL)
			return False

		def BindInterface(self, interface):
			from _weakref import proxy
			self.interface = proxy(interface)

		def OnTop(self):
			if not self.interface:
				return

			if shop.IsPrivateShop():
				self.interface.SetOnTopWindow(player.ON_TOP_WND_NONE)
				self.interface.RefreshMarkInventoryBag()
			else:
				self.interface.SetOnTopWindow(player.ON_TOP_WND_SHOP)
				self.interface.RefreshMarkInventoryBag()

class MallPageDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.ClearDictionary()

	def Open(self):
		scriptLoader = ui.PythonScriptLoader()
		scriptLoader.LoadScriptFile(self, "uiscript/mallpagedialog.py")

		self.GetChild("titlebar").SetCloseEvent(ui.__mem_func__(self.Close))

		(x, y) = self.GetGlobalPosition()
		x += 10
		y += 30

		MALL_PAGE_WIDTH = 600
		MALL_PAGE_HEIGHT = 480
		
		self.Lock()
		self.Show()

	def Close(self):
		self.Unlock()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
