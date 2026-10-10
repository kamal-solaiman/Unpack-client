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

if app.USE_MULTIPLE_SHOP_BUY:
	import shop

	class MultipleGemBuyDialog(ui.ScriptWindow):
		MIN_WIDTH = 240
		TOOLTIP_FIXED_WIDTH = 220

		def AdjustPosition(self, pos):
			self.SetPosition(pos[0] + 2 + self.gemShopWndInst.GetWidth(), pos[1])

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
				self.toolTipItem = uitooltip.ItemToolTip()
				self.toolTipItem.SetMultipleBuyDialog(True)
				self.toolTipItem.SetParent(self)
				self.toolTipItem.SetPosition(10, 56)

			entry = self.gemShopWndInst.items[self.pos]

			self.toolTipItem.ClearToolTip()
			self.toolTipItem.toolTipWidth = self.TOOLTIP_FIXED_WIDTH
			self.toolTipItem.multipleBuyCount = value

			metinSlot = [0] * player.METIN_SOCKET_MAX_NUM
			attrSlot = [(0, 0)] * player.ATTRIBUTE_SLOT_MAX_NUM
			self.toolTipItem.AddItemData(entry[0], metinSlot, attrSlot)

			totalPrice = entry[1] * value
			self.toolTipItem.AppendSpace(10)
			self.toolTipItem.AppendTextLine(localeinfo.TOOLTIP_BUYPRICE % (localeinfo.NumberToGayaString(totalPrice)), self.toolTipItem.GetPriceColor(totalPrice))

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
			self.pos = pos

			self.SetValue(1)

			self.AdjustPosition(self.gemShopWndInst.GetGlobalPosition())
			self.Show()

		def Close(self):
			self.OnCloseQuestionDlg()

			if self.editLine.IsFocus():
				self.editLine.KillFocus()

			if self.toolTipItem:
				self.toolTipItem.HideToolTip()

			self.Hide()

		def OnPressEscapeKey(self):
			self.gemShopWndInst.Close()
			return True

		def OnAcceptQuestionDlg(self):
			if self.toolTipItem.IsShow():
				net.SendChatPacket("/gem market %d %d" % (self.questionDlg.pos, int(self.editLine.GetText())))

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

			self.gemShopWndInst = parent
			self.questionDlg = None

			self.isLoaded = 0

			self.Initialize()

		def Destroy(self):
			self.gemShopWndInst = None

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

class SelectGems(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.tooltipItem = uitooltip.ItemToolTip()
		self.tooltipItem.Hide()

		self.inventorySlot = []
		self.slot_gui = []
		self.slotIndex = 0
		self.slot_select = 0

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def LoadWindow(self):
		try:
			PythonScriptLoader = ui.PythonScriptLoader()
			PythonScriptLoader.LoadScriptFile(self, "UIScript/selectitemwindow.py")
		except:
			import exception
			exception.Abort("ItemSelectWindow.LoadDialog.LoadObject")

		try:
			GetObject = self.GetChild
			self.board = GetObject("board")
			self.titleBar = GetObject("TitleBar")
			self.itemSlot = GetObject("ItemSlot")
			self.btnExit = GetObject("ExitButton")
		except:
			import exception
			exception.Abort("ItemSelectWindow.LoadDialog.BindObject")

		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))
		self.btnExit.SetEvent(ui.__mem_func__(self.Close))
		self.itemSlot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
		self.itemSlot.SAFE_SetButtonEvent("LEFT", "EXIST", self.SelectItemSlot)
		self.itemSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		self.itemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

	def Close(self):
		wndMgr.OnceIgnoreMouseLeftButtonUpEvent()
		self.Hide()

	def Open(self):
		self.Clear()
		self.Show()
		self.RefreshSlot(False)

	def Clear(self):
		self.inventorySlot = []
		self.slot_gui = []
		self.slotIndex = 0
		self.slot_select = 0

	def SelectItemSlot(self, slotIndex):
		wndMgr.OnceIgnoreMouseLeftButtonUpEvent()
		inventorySlot = self.inventorySlot[slotIndex]
		self.slot_select = slotIndex
		net.SendChatPacket("/gem craft %d" % inventorySlot)

	def SetTableSize(self, size):
		SLOT_X_COUNT = 5
		self.itemSlot.ArrangeSlot(0, SLOT_X_COUNT, size, 32, 32, 0, 0)
		self.itemSlot.RefreshSlot()
		self.itemSlot.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
		self.board.SetSize(self.board.GetWidth(), 76 + 32 * size)
		self.SetSize(self.board.GetWidth(), 76 + 32 * size)
		self.UpdateRect()

	def RefreshSlot(self,refresh = False):
		getItemVNum = player.GetItemIndex
		getItemCount = player.GetItemCount
		setItemVNum = self.itemSlot.SetItemSlot

		if not refresh:
			for i in xrange(player.INVENTORY_SLOT_COUNT):
				slotNumber = i
				itemVNum = getItemVNum(slotNumber)

				if 0 == itemVNum or not item.IsMetin(itemVNum):
					continue

				itemGrade = self.CheckGradeStone(item.GetItemName())
				if itemGrade > "3":
					continue

				#if itemVNum != 50926:
				#	continue

				self.inventorySlot.append(i)
				self.slot_gui.append(self.slotIndex)

				self.slotIndex += 1
				if self.slotIndex > 54:
					break

		itemCount = len(self.inventorySlot)
		if itemCount < 15:
			self.SetTableSize(3)

		else:
			lineCount = 3
			lineCount += (itemCount - 15) / 5
			if itemCount % 5:
				lineCount += 1
			self.SetTableSize(lineCount)

		count = 0
		for inventoryPos in self.inventorySlot:
			itemVNum = getItemVNum(inventoryPos)
			itemCount = getItemCount(inventoryPos)

			if itemCount <= 1:
				itemCount = 0

			setItemVNum(count, itemVNum, itemCount)
			count += 1

		self.itemSlot.RefreshSlot()
		if refresh:
			self.tooltipItem.Hide()

	def OverOutItem(self):
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OverInItem(self, slotIndex):
		if None != self.tooltipItem:
			inventorySlotPos = self.inventorySlot[slotIndex]
			self.tooltipItem.SetInventoryItem(inventorySlotPos)

	def CheckGradeStone(self,name):
		Search = name.rfind('+')
		Text = name[Search+1]
		return Text

	def SucceedGem(self):
		itemIndex = player.GetItemIndex(self.slot_select)
		if not itemIndex:
			del self.inventorySlot[self.slot_select]
			del self.slot_gui[self.slot_select]

		self.RefreshSlot(True)

	def OnPressEscapeKey(self):
		self.Close()
		return True

class SelectGemsShop(ui.ScriptWindow):
	GEM_SHOP_SLOT_MAX = 9
	GEM_SHOP_REFRESH_ITEM_VNUM = 39063
	GEM_SHOP_WINDOW_LIMIT_RANGE = 500
	GEM_SHOP_ADD_ITEM_VNUM = 39064

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.tooltipitem = None
		self.wndSellItemSlot = None
		self.questionDialog = None
		self.RefreshTimeValue = 0
		self.items = []
		self.slots_block = []
		self.xGemWindowStart = 0
		self.yGemWindowStart = 0
		self.gemshoprefreshtime = 0
		self.IsOpen = False
		if app.USE_MULTIPLE_SHOP_BUY:
			self.multipleBuyDlg = None

	if app.USE_MULTIPLE_SHOP_BUY:
		def OnMoveWindow(self, x, y):
			if getattr(self, "multipleBuyDlg", None):
				self.multipleBuyDlg.AdjustPosition(self.GetGlobalPosition())

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		self.tooltipitem = None
		self.wndSellItemSlot = None
		self.questionDialog = None
		self.RefreshTimeValue = 0
		self.items = []
		self.slots_block = []
		self.xGemWindowStart = 0
		self.yGemWindowStart = 0
		self.gemshoprefreshtime = 0
		self.IsOpen = False

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/GemShopWindow.py")
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))

			## RefreshButton
			self.GetChild("RefreshButton").SetEvent(ui.__mem_func__(self.RefreshItemSlot))

			## RefreshTimeValue
			self.RefreshTimeValue = self.GetChild("BuyRefreshTime")

			## Slot Background
			self.bg = self.GetChild("gemshopbackimg")

		except:
			import exception
			exception.Abort("SelectGems.LoadWindow.UIScript/GemShopWindow.py")

		## SlostSetting
		self.wndSellItemSlot = ui.GridSlotWindow()
		self.wndSellItemSlot.SetParent(self.bg)
		self.wndSellItemSlot.SetPosition(8, 28)
		self.wndSellItemSlot.ArrangeSlot(0, 3, 3, 32, 32, 13, 26)
		self.wndSellItemSlot.SAFE_SetButtonEvent("LEFT", "EXIST", self.UseItemSlot)
		self.wndSellItemSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		self.wndSellItemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		self.wndSellItemSlot.Show()

		positions = [
			[8,28],[8+45,28],[8+(45*2),28],
			[8,28+58],[8+45,28+58],[8+(45*2),28+58],
			[8,28+(58*2)],[8+45,28+(58*2)],[8+(45*2),28+(58*2)]
		]

		self.name,self.icongem = {},{}
		count = 0

		for i in positions:
			self.icongem[count] = ui.ImageBox()
			self.icongem[count].SetParent(self.bg)
			self.icongem[count].SetPosition(positions[count][0]-2,positions[count][1]+40)
			self.icongem[count].LoadImage("d:/ymir work/ui/gemshop/gemshop_gemicon.sub")
			self.icongem[count].Show()

			self.name[count] = ui.TextLine()
			self.name[count].SetParent(self.bg)
			if localeinfo.IsARABIC():
				self.name[count].SetPosition(positions[count][0]+14+20,positions[count][1]+39)
			else :
				self.name[count].SetPosition(positions[count][0]+14,positions[count][1]+39)
			self.name[count].Show()
			count +=1

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		ui.ScriptWindow.Show(self)
		(self.xGemWindowStart, self.yGemWindowStart, z) = player.GetMainCharacterPosition()
		self.IsOpen = True

	def Close(self):
		if app.USE_MULTIPLE_SHOP_BUY and getattr(self, "multipleBuyDlg", None):
			self.multipleBuyDlg.Close()
		self.Hide()
		if self.IsOpen:
			net.SendChatPacket("/gem close")
		self.IsOpen = False
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS():
			self.OnCloseQuestionDialog()

	def Clear(self):
		self.items = []
		self.slots_block = []

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Destroy(self):
		if app.USE_MULTIPLE_SHOP_BUY and getattr(self, "multipleBuyDlg", None):
			self.multipleBuyDlg.Destroy()
			self.multipleBuyDlg = None
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS():
			self.OnCloseQuestionDialog()

	def Time(self, time):
		self.gemshoprefreshtime = int(time)

	def __FormatTime(self, time):
		m, s = divmod(time, 60)
		h, m = divmod(m, 60)
		return "%1d:%02d:%02d" % (h, m, s)

	def Information(self, vnums, precios, count):
		self.items.append([int(vnums), int(precios), int(count)])

	def SlotsDesblock(self, slot0, slot1, slot2, slot3, slot4, slot5):
		self.slots_block.append([slot0, slot1, slot2, slot3, slot4, slot5])
		count = 0
		for i in xrange(0,6):
			if(self.slots_block[0][i] == "0"):
				self.wndSellItemSlot.DisableSlot(count+3)
			count +=1

	def LoadInformation(self):
		for i in xrange(0,len(self.items)):
			self.name[i].SetText(str(self.items[i][1]))
			self.wndSellItemSlot.SetItemSlot(i, self.items[i][0], self.items[i][2])

	def SetItemToolTip(self, tooltip):
		self.tooltipitem = tooltip

	def __ShowToolTip(self, slotIndex):
		if self.tooltipitem:
			self.tooltipitem.ClearToolTip()
			metinSlot = []
			for i in xrange(player.METIN_SOCKET_MAX_NUM):
				metinSlot.append(0)
			attrSlot = []
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				attrSlot.append((0, 0))

			self.tooltipitem.AddItemData(self.items[slotIndex][0], metinSlot, attrSlot)

	def OverInItem(self, slotIndex):
		self.__ShowToolTip(slotIndex)

	def OverOutItem(self):
		if self.tooltipitem:
			self.tooltipitem.HideToolTip()

	def SlotAddQuestion(self, slotIndex):
		item.SelectItem(self.GEM_SHOP_ADD_ITEM_VNUM)
		gemshopadditemvnum = item.GetItemName()
		openslotitemcount = 1

		self.questionDialog = uicommon.QuestionDialog2()
		self.questionDialog.SetText1(localeinfo.GEM_SYSTEM_ADD_SLOT % (gemshopadditemvnum))
		self.questionDialog.SetText2(localeinfo.GEM_SYSTEM_ADD_SLOT2 % (openslotitemcount))
		self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.SlotAddQuestionAccept))
		self.questionDialog.SetCancelEvent(ui.__mem_func__(self.SlotAddQuestionCancle))
		self.questionDialog.SetWidth(350)
		self.questionDialog.Open()

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def SlotAddQuestionAccept(self):
		if None == self.questionDialog:
			return

		self.OnCloseQuestionDialog()

	def SlotAddQuestionCancle(self):
		if None == self.questionDialog:
			return

		self.OnCloseQuestionDialog()

	def UseItemSlot(self, slotIndex):
		if self.questionDialog:
			return

		if app.USE_MULTIPLE_SHOP_BUY and app.IsPressed(app.DIK_LCONTROL):
			if slotIndex < 3 or self.slots_block[0][slotIndex - 3] != "0":
				if not self.multipleBuyDlg:
					self.multipleBuyDlg = MultipleGemBuyDialog(self)
				self.multipleBuyDlg.Open(slotIndex)
				return

		if player.GetGem() < self.items[slotIndex][1] and self.slots_block[0][slotIndex - 3] != "0":
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GEM_SYSTEM_NOT_ENOUGH_HP_GEM)
			return

		self.questionDialog = uicommon.QuestionDialog()

		if (slotIndex >= 3):
			if (self.slots_block[0][slotIndex - 3] == "0"):
				item.SelectItem(self.GEM_SHOP_ADD_ITEM_VNUM)
				unlockSlotItemName = item.GetItemName()
				openSlotItemCount = 1

				self.questionDialog = uicommon.QuestionDialog()
				self.questionDialog.SetText(localeinfo.GEM_SYSTEM_ADD_SLOT % (unlockSlotItemName, openSlotItemCount))
			else:
				self.questionDialog.SetText(localeinfo.GEM_SYSTEM_BUY_ITEM)
		else:
			self.questionDialog.SetText(localeinfo.GEM_SYSTEM_BUY_ITEM)

		self.questionDialog.SetAcceptEvent(lambda arg=slotIndex: self.SendBuyAccept(arg))
		self.questionDialog.SetCancelEvent(self.OnCloseQuestionDialog)
		self.questionDialog.SetWidth(350)
		self.questionDialog.Open()

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def SendBuyAccept(self, slotindex):
		if None == self.questionDialog:
			return

		net.SendChatPacket("/gem market %d" % slotindex)

		self.OnCloseQuestionDialog()

	def OnCloseQuestionDialog(self):
		if not self.questionDialog:
			return

		self.questionDialog.Close()
		self.questionDialog = None
		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	def RefreshItemSlot(self):
		ItemRefreshItemCount = player.GetItemCountByVnum(self.GEM_SHOP_REFRESH_ITEM_VNUM)

		if ItemRefreshItemCount == 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GEM_SYSTEM_NOT_ENOUGHT_REFRESHITEM)
			return;

		self.questionDialog = uicommon.QuestionDialog()
		self.questionDialog.SetText(localeinfo.GEM_SYSTEM_REFRESH_SHOP_ITEMS)
		self.questionDialog.SetAcceptEvent(self.SendRequestRefreshAccept)
		self.questionDialog.SetCancelEvent(self.OnCloseQuestionDialog)
		self.questionDialog.Open()

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def SendRequestRefreshAccept(self):
		if not self.questionDialog:
			return

		net.SendChatPacket("/gem refresh")

		self.OnCloseQuestionDialog()

	def OnUpdate(self):
		if self.IsOpen:
			(x, y, z) = player.GetMainCharacterPosition()
			if abs(x - self.xGemWindowStart) > self.GEM_SHOP_WINDOW_LIMIT_RANGE or abs(y - self.yGemWindowStart) > self.GEM_SHOP_WINDOW_LIMIT_RANGE:
				self.Close()

			leftSec = max(0, self.gemshoprefreshtime - app.GetGlobalTimeStamp())
			if leftSec > 0:
				self.RefreshTimeValue.SetText(str(self.__FormatTime(leftSec)))
			else:
				# self.RefreshTimeValue.SetText(str(localeinfo.SecondToHMGolbal(leftSec)))
				self.RefreshTimeValue.SetText(str("00:00"))