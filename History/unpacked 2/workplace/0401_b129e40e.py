# coding: latin_1

import app
import net
import player

import ui
import mousemodule
import snd
import safebox
import shop
import exchange
import chat
import localeinfo
import uiscriptlocale
import constinfo
import item
if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget
if app.USE_OFFLINESHOP:
	import uiofflineshop_ae

from _weakref import proxy

class PasswordDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__LoadDialog()

		self.sendMessage = "/safebox_password "

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadDialog(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			# if localeinfo.IsEUROPE()and app.GetLocalePath() != "locale/ca"and app.GetLocalePath() != "locale/sg" :
			pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "passworddialog.py")
			# else:
				# pyScrLoader.LoadScriptFile(self, "uiscript/passworddialog.py")
		except:
			import exception
			exception.Abort("PasswordDialog.__LoadDialog.LoadObject")

		try:
			self.passwordValue = self.GetChild("password_value")
			self.acceptButton = self.GetChild("accept_button")
			self.cancelButton = self.GetChild("cancel_button")
			self.titleName = self.GetChild("TitleName")
			self.GetChild("titlebar").SetCloseEvent(ui.__mem_func__(self.CloseDialog))
		except:
			import exception
			exception.Abort("PasswordDialog.__LoadDialog.BindObject")

		self.passwordValue.OnIMEReturn = ui.__mem_func__(self.OnAccept)
		self.passwordValue.OnPressEscapeKey = ui.__mem_func__(self.OnCancel)
		self.acceptButton.SetEvent(ui.__mem_func__(self.OnAccept))
		self.cancelButton.SetEvent(ui.__mem_func__(self.OnCancel))

	def Destroy(self):
		self.ClearDictionary()
		self.passwordValue = None
		self.acceptButton = None
		self.cancelButton = None
		self.titleName = None

	def SetTitle(self, title):
		self.titleName.SetText(title)

	def SetSendMessage(self, msg):
		self.sendMessage = msg

	def ShowDialog(self):
		if app.ENABLE_GROWTH_PET_SYSTEM:
			if player.IsOpenPetHatchingWindow():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_HATCHING_WINDOW_OPEN_CAN_NOT_USE)
				return False

		self.passwordValue.SetText("")
		self.passwordValue.SetFocus()
		self.SetCenterPosition()
		self.Show()

	def CloseDialog(self):
		self.passwordValue.KillFocus()
		self.Hide()

	def OnAccept(self):
		net.SendChatPacket(self.sendMessage + self.passwordValue.GetText())
		self.CloseDialog()
		return True

	def OnCancel(self):
		self.CloseDialog()
		return True

class ChangePasswordDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__LoadDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadDialog(self):
		self.dlgMessage = ui.ScriptWindow()
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self.dlgMessage, "uiscript/popupdialog.py")
			self.dlgMessage.GetChild("message").SetText(localeinfo.SAFEBOX_WRONG_PASSWORD)
			self.dlgMessage.GetChild("accept").SetEvent(ui.__mem_func__(self.OnCloseMessageDialog))
		except:
			import exception
			exception.Abort("SafeboxWindow.__LoadDialog.LoadObject")

	def LoadDialog(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/changepassworddialog.py")

		except:
			import exception
			exception.Abort("ChangePasswordDialog.LoadDialog.LoadObject")

		try:
			self.GetChild("accept_button").SetEvent(ui.__mem_func__(self.OnAccept))
			self.GetChild("cancel_button").SetEvent(ui.__mem_func__(self.OnCancel))
			self.GetChild("titlebar").SetCloseEvent(ui.__mem_func__(self.OnCancel))
			oldPassword = self.GetChild("old_password_value")
			newPassword = self.GetChild("new_password_value")
			newPasswordCheck = self.GetChild("new_password_check_value")
		except:
			import exception
			exception.Abort("ChangePasswordDialog.LoadDialog.BindObject")

		oldPassword.SetTabEvent(lambda arg=1: self.OnNextFocus(arg))
		newPassword.SetTabEvent(lambda arg=2: self.OnNextFocus(arg))
		newPasswordCheck.SetTabEvent(lambda arg=3: self.OnNextFocus(arg))
		oldPassword.SetReturnEvent(lambda arg=1: self.OnNextFocus(arg))
		newPassword.SetReturnEvent(lambda arg=2: self.OnNextFocus(arg))
		newPasswordCheck.SetReturnEvent(ui.__mem_func__(self.OnAccept))
		oldPassword.OnPressEscapeKey = self.OnCancel
		newPassword.OnPressEscapeKey = self.OnCancel
		newPasswordCheck.OnPressEscapeKey = self.OnCancel

		self.oldPassword = oldPassword
		self.newPassword = newPassword
		self.newPasswordCheck = newPasswordCheck

	def OnNextFocus(self, arg):
		if 1 == arg:
			self.oldPassword.KillFocus()
			self.newPassword.SetFocus()
		elif 2 == arg:
			self.newPassword.KillFocus()
			self.newPasswordCheck.SetFocus()
		elif 3 == arg:
			self.newPasswordCheck.KillFocus()
			self.oldPassword.SetFocus()

	def Destroy(self):
		self.ClearDictionary()
		self.dlgMessage.ClearDictionary()
		self.oldPassword = None
		self.newPassword = None
		self.newPasswordCheck = None

	def Open(self):
		self.oldPassword.SetText("")
		self.newPassword.SetText("")
		self.newPasswordCheck.SetText("")
		self.oldPassword.SetFocus()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.oldPassword.SetText("")
		self.newPassword.SetText("")
		self.newPasswordCheck.SetText("")
		self.oldPassword.KillFocus()
		self.newPassword.KillFocus()
		self.newPasswordCheck.KillFocus()
		self.Hide()

	def OnAccept(self):
		oldPasswordText = self.oldPassword.GetText()
		newPasswordText = self.newPassword.GetText()
		newPasswordCheckText = self.newPasswordCheck.GetText()
		if newPasswordText != newPasswordCheckText:
			self.dlgMessage.SetCenterPosition()
			self.dlgMessage.SetTop()
			self.dlgMessage.Show()
			return True
		net.SendChatPacket("/safebox_change_password %s %s" % (oldPasswordText, newPasswordText))
		self.Close()
		return True

	def OnCancel(self):
		self.Close()
		return True

	def OnCloseMessageDialog(self):
		self.newPassword.SetText("")
		self.newPasswordCheck.SetText("")
		self.newPassword.SetFocus()
		self.dlgMessage.Hide()

class SafeboxWindow(ui.ScriptWindow):
	BOX_WIDTH = 176

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.tooltipItem = None
		self.sellingSlotNumber = -1
		self.pageButtonList = []
		self.curPageIndex = 0
		self.isLoaded = 0
		self.xSafeBoxStart = 0
		self.ySafeBoxStart = 0
		self.pageCount = 0
		self.interface = None

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()
		
		ui.ScriptWindow.Show(self)

	def Destroy(self):
		self.ClearDictionary()

		self.dlgChangePassword.Destroy()
		self.dlgChangePassword = None

		self.tooltipItem = None
		self.wndBoard = None
		self.wndItem = None

		self.pageButtonList = []

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "UIScript/SafeboxWindow.py")

		## Item
		wndItem = ui.GridSlotWindow()
		wndItem.SetParent(self)
		wndItem.SetPosition(8, 35)
		wndItem.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndItem.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndItem.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		wndItem.Show()

		## ChangePasswrod
		dlgChangePassword = ChangePasswordDialog()
		dlgChangePassword.LoadDialog()
		dlgChangePassword.Hide()

		## Close Button
		self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
		self.GetChild("ChangePasswordButton").SetEvent(ui.__mem_func__(self.OnChangePassword))
		self.GetChild("ExitButton").SetEvent(ui.__mem_func__(self.Close))

		self.wndItem = wndItem
		self.dlgChangePassword = dlgChangePassword
		self.wndBoard = self.GetChild("board")

		## Initialize
		self.SetTableSize(3)

	def ShowWindow(self, size):
		(self.xSafeBoxStart, self.ySafeBoxStart, z) = player.GetMainCharacterPosition()

		self.SetTableSize(size)
		self.SetTop()
		self.Show()

		if app.ENABLE_GROWTH_PET_SYSTEM or app.ITEM_CHECKINOUT_UPDATE:
			player.SetOpenSafeBox(True)

	def __MakePageButton(self, pageCount):
		self.curPageIndex = 0
		self.pageButtonList = []
		self.pageCount = pageCount

		text = "I"
		pos = -int(float(pageCount-1)/2 * 52)
		for i in xrange(pageCount):
			button = ui.RadioButton()
			button.SetParent(self)
			button.SetUpVisual("d:/ymir work/ui/game/windows/tab_button_middle_01.sub")
			button.SetOverVisual("d:/ymir work/ui/game/windows/tab_button_middle_02.sub")
			button.SetDownVisual("d:/ymir work/ui/game/windows/tab_button_middle_03.sub")
			button.SetWindowHorizontalAlignCenter()
			button.SetWindowVerticalAlignBottom()
			button.SetPosition(pos, 85)
			button.SetText(text)
			button.SetEvent(lambda arg=i: self.SelectPage(arg))
			button.Show()
			self.pageButtonList.append(button)

			pos += 52
			text += "I"

		self.pageButtonList[0].Down()

	def SelectPage(self, index):
		self.curPageIndex = index

		for btn in self.pageButtonList:
			btn.SetUp()

		self.pageButtonList[index].Down()
		self.RefreshSafebox()

	def __LocalPosToGlobalPos(self, local):
		return self.curPageIndex*safebox.SAFEBOX_PAGE_SIZE + local

	def SetTableSize(self, size):
		pageCount = max(1, size / safebox.SAFEBOX_SLOT_Y_COUNT)
		pageCount = min(3, pageCount)
		size = safebox.SAFEBOX_SLOT_Y_COUNT

		self.__MakePageButton(pageCount)

		self.wndItem.ArrangeSlot(0, safebox.SAFEBOX_SLOT_X_COUNT, size, 32, 32, 0, 0)
		self.wndItem.RefreshSlot()
		self.wndItem.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)

		wnd_height = 130 + 32 * size
		self.wndBoard.SetSize(self.BOX_WIDTH, wnd_height)
		self.SetSize(self.BOX_WIDTH, wnd_height)
		self.UpdateRect()

	def RefreshSafebox(self):
		getItemID=safebox.GetItemID
		getItemCount=safebox.GetItemCount
		setItemID=self.wndItem.SetItemSlot

		for i in xrange(safebox.SAFEBOX_PAGE_SIZE):
			slotIndex = self.__LocalPosToGlobalPos(i)
			itemCount = getItemCount(slotIndex)
			if itemCount <= 1:
				itemCount = 0
			setItemID(i, getItemID(slotIndex), itemCount)

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				changelookitemvnum = safebox.GetItemChangeLookVnum(slotIndex)
				if not changelookitemvnum == 0:
					self.wndItem.SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")
				else:
					self.wndItem.EnableSlotCoverImage(i, False)
			if app.ENABLE_GROWTH_PET_SYSTEM:
				self.__SetCoolTimePetItemSlot( slotIndex, getItemID(slotIndex))

			# ENABLE_ACCOUNT_BIND_ITEMS — show lock icon on any bound items in safebox.
			# (Deposit is server-blocked; this covers pre-feature legacy items.)
			fishVnum = getItemID(slotIndex)
			if fishVnum >= 37863 and fishVnum <= 37892:
				self.wndItem.SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")

			if app.ENABLE_ACCOUNT_BIND_ITEMS and player.IsItemAccountBound(player.SAFEBOX, slotIndex):
				self.wndItem.SetSlotCoverImage(i, "icon/item/account_locked.png")

		self.wndItem.RefreshSlot()

	def AddSafeBoxItem(self):
		self.SelectEmptySlot(-1) ## test
		
	def SetItemToolTip(self, tooltip):
		self.tooltipItem = tooltip

	def Close(self):
		net.SendChatPacket("/safebox_close")

	def CommandCloseSafebox(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

		if app.WJ_ENABLE_TRADABLE_ICON:
			if self.interface:
				self.interface.SetOnTopWindow(player.ON_TOP_WND_NONE)
				self.interface.RefreshMarkInventoryBag()
		self.dlgChangePassword.Close()
		self.Hide()

		if app.ENABLE_GROWTH_PET_SYSTEM or app.ITEM_CHECKINOUT_UPDATE:
			player.SetOpenSafeBox(False)

	## Slot Event
	def SelectEmptySlot(self, selectedSlotPos):
		selectedSlotPos = self.__LocalPosToGlobalPos(selectedSlotPos)

		if mousemodule.mouseController.isAttached():
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()

			if player.SLOT_TYPE_SAFEBOX == attachedSlotType:
				net.SendSafeboxItemMovePacket(attachedSlotPos, selectedSlotPos, 0)
				#snd.PlaySound("sound/ui/drop.wav")
			else:
				attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)
				if player.RESERVED_WINDOW == attachedInvenType:
					return

				if app.USE_OFFLINESHOP:
					if uiofflineshop_ae.IsBuildingShop() and\
						uiofflineshop_ae.IsSaleSlot(attachedInvenType, attachedSlotPos):
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
						return

				if mousemodule.mouseController.GetAttachedItemIndex() != player.ITEM_MONEY:
					net.SendSafeboxCheckinPacket(attachedInvenType, attachedSlotPos, selectedSlotPos)
					#snd.PlaySound("sound/ui/drop.wav")

			mousemodule.mouseController.DeattachObject()

	def SelectItemSlot(self, selectedSlotPos):
		selectedSlotPos = self.__LocalPosToGlobalPos(selectedSlotPos)
		if app.ENABLE_RENDER_TARGET and app.IsPressed(app.DIK_LSHIFT):
			if uiRenderTarget.IsCanShowItems(safebox.GetItemID(selectedSlotPos)):
				itemTransmutedVnum = safebox.GetItemChangeLookVnum(selectedSlotPos)
				if itemTransmutedVnum:
					self.interface.OpenRenderTargetWindow(0, itemTransmutedVnum)
				else:
					self.interface.OpenRenderTargetWindow(0, safebox.GetItemID(selectedSlotPos))
				return

		if mousemodule.mouseController.isAttached():
			attachedSlotType = mousemodule.mouseController.GetAttachedType()

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				if player.SLOT_TYPE_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_STONE_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_ENCHANT_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_POTS_INVENTORY == attachedSlotType:

					if mousemodule.mouseController.GetAttachedItemIndex() != player.ITEM_MONEY:
						attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
						#net.SendSafeboxCheckinPacket(attachedSlotPos, selectedSlotPos)
						#snd.PlaySound("sound/ui/drop.wav")
			else:
				if player.SLOT_TYPE_INVENTORY == attachedSlotType:
					if mousemodule.mouseController.GetAttachedItemIndex() != player.ITEM_MONEY:
						attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
						#net.SendSafeboxCheckinPacket(attachedSlotPos, selectedSlotPos)
						#snd.PlaySound("sound/ui/drop.wav")

			mousemodule.mouseController.DeattachObject()
		else:
			curCursorNum = app.GetCursor()
			if app.SELL == curCursorNum:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SAFEBOX_SELL_DISABLE_SAFEITEM)

			elif app.BUY == curCursorNum:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SHOP_BUY_INFO)

			else:
				selectedItemID = safebox.GetItemID(selectedSlotPos)
				mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_SAFEBOX, selectedSlotPos, selectedItemID)
				snd.PlaySound("sound/ui/pick.wav")

	def UseItemSlot(self, slotIndex):
		if app.USE_BL_FISH_EVENT:
			if mousemodule.mouseController.isAttached():
				if player.SLOT_TYPE_FISH_EVENT == mousemodule.mouseController.GetAttachedType():
					return

		mousemodule.mouseController.DeattachObject()
		if app.ITEM_CHECKINOUT_UPDATE:
			slotIndex = self.__LocalPosToGlobalPos(slotIndex)
			net.SendSafeboxCheckoutPacket(slotIndex)

	def __ShowToolTip(self, slotIndex):
		if self.tooltipItem:
			self.tooltipItem.SetSafeBoxItem(slotIndex)

	def OverInItem(self, slotIndex):
		slotIndex = self.__LocalPosToGlobalPos(slotIndex)
		self.wndItem.SetUsableItem(False)
		self.__ShowToolTip(slotIndex)

	def OverOutItem(self):
		self.wndItem.SetUsableItem(False)
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	if app.ENABLE_GROWTH_PET_SYSTEM:
		def __SetCoolTimePetItemSlot(self, slotNumber, itemVnum):
			if 0 == itemVnum:
				return
				
			item.SelectItem(itemVnum)
			itemSubType = item.GetItemSubType()
				
			if itemSubType not in [item.PET_UPBRINGING, item.PET_BAG]:
				return
						
			if itemSubType == item.PET_BAG:
				id = safebox.GetItemMetinSocket(slotNumber, 2)
				if id == 0:
					return
					
			(limitType, limitValue) = item.GetLimit(0)

			if itemSubType == item.PET_UPBRINGING:
				limitValue = safebox.GetItemMetinSocket(slotNumber, 1)
							
			if limitType in [item.LIMIT_REAL_TIME, item.LIMIT_REAL_TIME_START_FIRST_USE]:
										
				sock_time   = safebox.GetItemMetinSocket(slotNumber, 0)
				remain_time = max( 0, sock_time - app.GetGlobalTimeStamp() )

				if slotNumber >= safebox.SAFEBOX_PAGE_SIZE:
					slotNumber -= (self.curPageIndex * safebox.SAFEBOX_PAGE_SIZE)

				self.wndItem.SetSlotCoolTimeInverse(slotNumber, limitValue, limitValue - remain_time)

	def OnChangePassword(self):
		self.dlgChangePassword.Open()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnUpdate(self):
		USE_SAFEBOX_LIMIT_RANGE = 1000

		(x, y, z) = player.GetMainCharacterPosition()
		if abs(x - self.xSafeBoxStart) > USE_SAFEBOX_LIMIT_RANGE or abs(y - self.ySafeBoxStart) > USE_SAFEBOX_LIMIT_RANGE:
			self.Close()

	if app.WJ_ENABLE_TRADABLE_ICON:
		def CantCheckInItem(self, slotIndex):
			itemIndex = player.GetItemIndex(slotIndex)

			if itemIndex:
				return player.IsAntiFlagBySlot(slotIndex, item.ANTIFLAG_SAFEBOX)

			return False

		def BindInterface(self, interface):
			self.interface = proxy(interface)

		def OnTop(self):
			if not self.interface:
				return

			self.interface.SetOnTopWindow(player.ON_TOP_WND_SAFEBOX)
			self.interface.RefreshMarkInventoryBag()

class MallWindow(ui.ScriptWindow):
	BOX_WIDTH = 176

	if app.ENABLE_SAFEBOX_EX_SYSTEM:
		PAGE_TEXT = ( "I", "II", "III", "IV", "V")

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.tooltipItem = None
		self.sellingSlotNumber = -1
		self.pageButtonList = []
		self.curPageIndex = 0
		self.isLoaded = 0
		self.xSafeBoxStart = 0
		self.ySafeBoxStart = 0

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()
		
		ui.ScriptWindow.Show(self)

	def Destroy(self):
		self.ClearDictionary()

		self.tooltipItem = None
		self.wndBoard = None
		self.wndItem = None

		self.pageButtonList = []

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "UIScript/MallWindow.py")

		## Item
		wndItem = ui.GridSlotWindow()
		wndItem.SetParent(self)
		wndItem.SetPosition(8, 35)
		wndItem.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndItem.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndItem.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		wndItem.Show()

		## Close Button
		self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
		self.GetChild("ExitButton").SetEvent(ui.__mem_func__(self.Close))

		self.wndItem = wndItem
		self.wndBoard = self.GetChild("board")

		## Initialize
		self.SetTableSize(3)

	def ShowWindow(self, size):
		(self.xSafeBoxStart, self.ySafeBoxStart, z) = player.GetMainCharacterPosition()

		self.SetTableSize(size)
		self.Show()

		if app.ENABLE_GROWTH_PET_SYSTEM:
			player.SetOpenMall(True)

	def SetTableSize(self, size):
		pageCount = max(1, size / safebox.SAFEBOX_SLOT_Y_COUNT)
		if app.ENABLE_SAFEBOX_EX_SYSTEM:
			pageCount = min(5, pageCount)
		else:
			pageCount = min(3, pageCount)
		size = safebox.SAFEBOX_SLOT_Y_COUNT
		
		if app.ENABLE_SAFEBOX_EX_SYSTEM:
			self.__MakePageButton(pageCount)

		self.wndItem.ArrangeSlot(0, safebox.SAFEBOX_SLOT_X_COUNT, size, 32, 32, 0, 0)
		self.wndItem.RefreshSlot()
		self.wndItem.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
		if app.ENABLE_SAFEBOX_EX_SYSTEM:
			self.wndBoard.SetSize(self.BOX_WIDTH, 102 + 32*size)
			self.SetSize(self.BOX_WIDTH, 105 + 32*size)
		else:
			self.wndBoard.SetSize(self.BOX_WIDTH, 82 + 32*size)
			self.SetSize(self.BOX_WIDTH, 85 + 32*size)
		self.UpdateRect()
		
	if app.ENABLE_SAFEBOX_EX_SYSTEM:
		def __MakePageButton(self, pageCount):
			
			self.curPageIndex = 0
			self.pageButtonList = []
			
			pos = -int(float(pageCount-1)/2 * 32)
			for i in xrange(pageCount):
				text = self.PAGE_TEXT[i]
				button = ui.RadioButton()
				button.SetParent(self)
				button.SetUpVisual("d:/ymir work/ui/game/windows/tab_button_small_01.sub")
				button.SetOverVisual("d:/ymir work/ui/game/windows/tab_button_small_02.sub")
				button.SetDownVisual("d:/ymir work/ui/game/windows/tab_button_small_03.sub")
				button.SetWindowHorizontalAlignCenter()
				button.SetWindowVerticalAlignBottom()
				button.SetPosition(pos, 65)
				button.SetText(text)
				button.SetEvent(lambda arg=i: self.SelectPage(arg))
				button.Show()
				self.pageButtonList.append(button)
				
				pos += 32
			
			self.pageButtonList[0].Down()

		def SelectPage(self, index):
		
			self.curPageIndex = index
		
			for btn in self.pageButtonList:
				btn.SetUp()
		
			self.pageButtonList[index].Down()
			self.RefreshMall()
			
			
		def __LocalPosToGlobalPos(self, local):
			return self.curPageIndex*safebox.SAFEBOX_PAGE_SIZE + local

	def RefreshMall(self):
		getItemID=safebox.GetMallItemID
		getItemCount=safebox.GetMallItemCount
		setItemID=self.wndItem.SetItemSlot

		if app.ENABLE_SAFEBOX_EX_SYSTEM:
			for i in xrange(safebox.SAFEBOX_PAGE_SIZE):
				slotIndex = self.__LocalPosToGlobalPos(i)
				itemCount = getItemCount(slotIndex)
				if itemCount <= 1:
					itemCount = 0
				setItemID(i, getItemID(slotIndex), itemCount)

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				changelookitemvnum = safebox.GetMallItemChangeLookVnum(slotIndex)
				if not changelookitemvnum == 0:
					self.wndItem.SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")
				else:
					self.wndItem.EnableSlotCoverImage(i, False)


		self.wndItem.RefreshSlot()

	def SetItemToolTip(self, tooltip):
		self.tooltipItem = tooltip

	def Close(self):
		net.SendChatPacket("/mall_close")

	def CommandCloseMall(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

		self.Hide()

		if app.ENABLE_GROWTH_PET_SYSTEM:
			player.SetOpenMall(False)

	## Slot Event
	def SelectEmptySlot(self, selectedSlotPos):
		if mousemodule.mouseController.isAttached():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.MALL_CANNOT_INSERT)
			mousemodule.mouseController.DeattachObject()

	def SelectItemSlot(self, selectedSlotPos):
		if app.ENABLE_SAFEBOX_EX_SYSTEM:
			selectedSlotPos = self.__LocalPosToGlobalPos(selectedSlotPos)

		if app.ENABLE_RENDER_TARGET:
			if uiRenderTarget.IsCanShowItems(safebox.GetMallItemID(selectedSlotPos)):
				itemTransmutedVnum = safebox.GetItemChangeLookVnum(selectedSlotPos)
				if itemTransmutedVnum:
					self.interface.OpenRenderTargetWindow(0, itemTransmutedVnum)
				else:
					self.interface.OpenRenderTargetWindow(0, safebox.GetMallItemID(selectedSlotPos))
				return

		if mousemodule.mouseController.isAttached():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.MALL_CANNOT_INSERT)
			mousemodule.mouseController.DeattachObject()
		else:
			curCursorNum = app.GetCursor()
			selectedItemID = safebox.GetMallItemID(selectedSlotPos)
			mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_MALL, selectedSlotPos, selectedItemID)
			snd.PlaySound("sound/ui/pick.wav")

	def UseItemSlot(self, slotIndex):
		if app.USE_BL_FISH_EVENT:
			if mousemodule.mouseController.isAttached():
				if player.SLOT_TYPE_FISH_EVENT == mousemodule.mouseController.GetAttachedType():
					return

		mousemodule.mouseController.DeattachObject()
		if app.ITEM_CHECKINOUT_UPDATE:
			net.SendMallCheckoutPacket(slotIndex)

	def __ShowToolTip(self, slotIndex):
		if self.tooltipItem:
			self.tooltipItem.SetMallItem(slotIndex)

	def OverInItem(self, slotIndex):
		self.__ShowToolTip(slotIndex)

	def OverOutItem(self):
		self.wndItem.SetUsableItem(False)
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnUpdate(self):
		USE_SAFEBOX_LIMIT_RANGE = 1000

		(x, y, z) = player.GetMainCharacterPosition()
		if abs(x - self.xSafeBoxStart) > USE_SAFEBOX_LIMIT_RANGE or abs(y - self.ySafeBoxStart) > USE_SAFEBOX_LIMIT_RANGE:
			self.Close()
