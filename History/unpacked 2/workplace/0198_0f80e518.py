# coding: utf-8

import app

if app.ENABLE_CHEQUE_SYSTEM or app.ENABLE_NEW_DROP_DIALOG or app.USE_ITEM_ATTR_BACKUP_MODE:
	import player

if app.USE_ITEM_ATTR_BACKUP_MODE:
	import grp

import ui
import localeinfo
import ime
import uiscriptlocale
import chat
import uitooltip
import chr
import wndMgr

if app.ENABLE_NEW_DROP_DIALOG or app.USE_ITEM_ATTR_BACKUP_MODE:
	import item

if app.USE_OFFLINESHOP:
	import offlineshop

import net

if app.ENABLE_REMEMBER_LAST_SPLIT:
	import systemSetting

class PopupDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_scale")
			self.SetAnimationPreset("popup")

		self.__LoadDialog()
		self.acceptEvent = lambda *arg: None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadDialog(self):
		try:
			PythonScriptLoader = ui.PythonScriptLoader()
			PythonScriptLoader.LoadScriptFile(self, "UIScript/PopupDialog.py")

			self.board = self.GetChild("board")
			self.message = self.GetChild("message")
			self.accceptButton = self.GetChild("accept")
			self.accceptButton.SetEvent(ui.__mem_func__(self.Close))

		except:
			import exception
			exception.Abort("PopupDialog.LoadDialog.BindObject")

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.Hide()
		self.acceptEvent()

	def Destroy(self):
		self.Close()
		self.ClearDictionary()

	def SetWidth(self, width):
		height = self.GetHeight()
		self.SetSize(width, height)

		if self.board.IsRTL():
			self.board.SetPosition(width, 0)

		self.board.SetSize(width, height)
		self.SetCenterPosition()
		self.UpdateRect()

	def SetText(self, text):
		self.message.SetText(text)

	def SetAcceptEvent(self, event):
		self.acceptEvent = event

	def SetButtonName(self, name):
		self.accceptButton.SetText(name)

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnIMEReturn(self):
		self.Close()
		return True

	def GetTextSize(self):
		if self.message:
			return self.message.GetTextSize()

		return (0,0)

class InputDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__CreateDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __CreateDialog(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/inputdialog.py")

		getObject = self.GetChild
		self.board = getObject("Board")
		self.acceptButton = getObject("AcceptButton")
		self.cancelButton = getObject("CancelButton")
		self.inputSlot = getObject("InputSlot")
		self.inputValue = getObject("InputValue")

	def Open(self):
		self.inputValue.SetFocus()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.ClearDictionary()
		self.board = None
		self.acceptButton = None
		self.cancelButton = None
		self.inputSlot = None
		self.inputValue = None
		self.Hide()

	def SetTitle(self, name):
		self.board.SetTitleName(name)

	def SetNumberMode(self):
		self.inputValue.SetNumberMode()

	def SetUseCodePage(self, bUse = True):
		self.inputValue.SetUseCodePage(bUse)

	def SetSecretMode(self):
		self.inputValue.SetSecret()

	def SetFocus(self):
		self.inputValue.SetFocus()

	def SetMaxLength(self, length):
		width = length * 6 + 10
		self.SetBoardWidth(max(width + 50, 160))
		self.SetSlotWidth(width)
		self.inputValue.SetMax(length)

	def SetSlotWidth(self, width):
		self.inputSlot.SetSize(width, self.inputSlot.GetHeight())
		self.inputValue.SetSize(width, self.inputValue.GetHeight())
		if self.IsRTL():
			self.inputValue.SetPosition(self.inputValue.GetWidth(), 0)

	def SetBoardWidth(self, width):
		self.SetSize(max(width + 50, 160), self.GetHeight())
		self.board.SetSize(max(width + 50, 160), self.GetHeight())
		if self.IsRTL():
			self.board.SetPosition(self.board.GetWidth(), 0)
		self.UpdateRect()

	def SetAcceptEvent(self, event):
		self.acceptButton.SetEvent(event)
		self.inputValue.OnIMEReturn = event

	def SetCancelEvent(self, event):
		self.board.SetCloseEvent(event)
		self.cancelButton.SetEvent(event)
		self.inputValue.OnPressEscapeKey = event

	def GetText(self):
		return self.inputValue.GetText()

class InputDialogWithDescription(InputDialog):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__CreateDialog()

	def __del__(self):
		InputDialog.__del__(self)

	def __CreateDialog(self):
		pyScrLoader = ui.PythonScriptLoader()
		if localeinfo.IsARABIC() :
			pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "inputdialogwithdescription.py")
		else:
			pyScrLoader.LoadScriptFile(self, "uiscript/inputdialogwithdescription.py")

		try:
			getObject = self.GetChild
			self.board = getObject("Board")
			self.acceptButton = getObject("AcceptButton")
			self.cancelButton = getObject("CancelButton")
			self.inputSlot = getObject("InputSlot")
			self.inputValue = getObject("InputValue")
			self.description = getObject("Description")

		except:
			import exception
			exception.Abort("InputDialogWithDescription.LoadBoardDialog.BindObject")

	def SetDescription(self, text):
		self.description.SetText(text)

class InputDialogWithDescription2(InputDialog):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__CreateDialog()

	def __del__(self):
		InputDialog.__del__(self)

	def __CreateDialog(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/inputdialogwithdescription2.py")

		try:
			getObject = self.GetChild
			self.board = getObject("Board")
			self.acceptButton = getObject("AcceptButton")
			self.cancelButton = getObject("CancelButton")
			self.inputSlot = getObject("InputSlot")
			self.inputValue = getObject("InputValue")
			self.description1 = getObject("Description1")
			self.description2 = getObject("Description2")

		except:
			import exception
			exception.Abort("InputDialogWithDescription.LoadBoardDialog.BindObject")

	def SetDescription1(self, text):
		self.description1.SetText(text)

	def SetDescription2(self, text):
		self.description2.SetText(text)

class QuestionDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__CreateDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __CreateDialog(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/questiondialog.py")
		
		self.board = self.GetChild("board")
		self.textLine = self.GetChild("message")
		self.acceptButton = self.GetChild("accept")
		self.cancelButton = self.GetChild("cancel")

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.Hide()

	def SetWidth(self, width):
		height = self.GetHeight()
		self.SetSize(width, height)

		if self.board.IsRTL():
			self.board.SetPosition(width, 0)

		self.board.SetSize(width, height)
		self.SetCenterPosition()
		self.UpdateRect()

	def SAFE_SetAcceptEvent(self, event):
		self.acceptButton.SAFE_SetEvent(event)

	def SAFE_SetCancelEvent(self, event):
		self.cancelButton.SAFE_SetEvent(event)

	def SetAcceptEvent(self, event):
		self.acceptButton.SetEvent(event)

	def SetCancelEvent(self, event):
		self.cancelButton.SetEvent(event)

	def SetText(self, text, isRed = False, isGreen = False):
		self.textLine.SetText(text)
		if text:
			if isRed:
				self.textLine.SetFontColor(211/255.0, 84/255.0, 0/255.0)
			elif isGreen:
				self.textLine.SetFontColor(46/255.0, 204/255.0, 113/255.0)

	def SetAcceptText(self, text):
		self.acceptButton.SetText(text)

	def SetCancelText(self, text):
		self.cancelButton.SetText(text)

	def OnPressEscapeKey(self):
		self.Close()
		self.cancelButton.CallEvent()
		return True

	def GetTextSize(self):
		if self.textLine:
			return self.textLine.GetTextSize()

		return (0,0)

	def OnIMEReturn(self):
		if self.acceptButton:
			self.acceptButton.CallEvent()
			
		return True

	def AutoResize(self, minWidth = 30):
		self.SetWidth(self.textLine.GetTextSize()[0] + minWidth)

class QuestionDialogDestroyConfirm(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__CreateDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __CreateDialog(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/questiondialog_destroy.py")

		self.board = self.GetChild("board")
		self.textLine = self.GetChild("destroy")
		self.acceptButton = self.GetChild("accept")
		self.cancelButton = self.GetChild("cancel")

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.Hide()

	def SetWidth(self, width):
		height = self.GetHeight()
		self.SetSize(width, height)

		if self.board.IsRTL():
			self.board.SetPosition(width, 0)

		self.board.SetSize(width, height)
		self.SetCenterPosition()
		self.UpdateRect()

	def SAFE_SetAcceptEvent(self, event):
		self.acceptButton.SAFE_SetEvent(event)

	def SAFE_SetCancelEvent(self, event):
		self.cancelButton.SAFE_SetEvent(event)

	def SetAcceptEvent(self, event):
		self.acceptButton.SetEvent(event)

	def SetCancelEvent(self, event):
		self.cancelButton.SetEvent(event)

	def SetText(self, text):
		self.textLine.SetText(text)

	def SetAcceptText(self, text):
		self.acceptButton.SetText(text)

	def SetCancelText(self, text):
		self.cancelButton.SetText(text)

	def OnPressEscapeKey(self):
		self.Close()
		self.cancelButton.CallEvent()
		return True

	def GetTextSize(self):
		if self.textLine:
			return self.textLine.GetTextSize()

		return (0,0)

class QuestionDialog2(QuestionDialog):
	def __init__(self):
		QuestionDialog.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__CreateDialog()

	def __del__(self):
		QuestionDialog.__del__(self)

	def __CreateDialog(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/questiondialog2.py")

		self.board = self.GetChild("board")
		self.textLine1 = self.GetChild("message1")
		self.textLine2 = self.GetChild("message2")
		self.acceptButton = self.GetChild("accept")
		self.cancelButton = self.GetChild("cancel")

	def SetText1(self, text):
		self.textLine1.SetText(text)

	def SetText2(self, text):
		self.textLine2.SetText(text)

	if app.ENABLE_GROWTH_PET_SYSTEM:
		def GetTextSize1(self):
			if self.textLine1:
				return self.textLine1.GetTextSize()
				
			return (0,0)
			
		def GetTextSize2(self):
			if self.textLine2:
				return self.textLine2.GetTextSize()
				
			return (0,0)

class QuestionDialogWithTimeLimit(QuestionDialog2):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__CreateDialog()
		self.endTime = 0
		self.timeoverMsg = None
		self.isCancelOnTimeover = False

	def __del__(self):
		QuestionDialog2.__del__(self)

	def __CreateDialog(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/questiondialog2.py")

		self.board = self.GetChild("board")
		self.textLine1 = self.GetChild("message1")
		self.textLine2 = self.GetChild("message2")
		self.acceptButton = self.GetChild("accept")
		self.cancelButton = self.GetChild("cancel")

	def Open(self, msg, timeout):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

		self.SetText1(msg)
		self.endTime = app.GetTime() + timeout

	def OnUpdate(self):
		leftTime = max(0, self.endTime - app.GetTime())
		self.SetText2(localeinfo.UI_LEFT_TIME % (leftTime))
		if leftTime<0.5:
			if self.timeoverMsg:
				chat.AppendChat(chat.CHAT_TYPE_INFO, self.timeoverMsg)
			if self.isCancelOnTimeover:
				self.cancelButton.CallEvent()

	def SetTimeOverMsg(self, msg):
		self.timeoverMsg = msg

	def SetCancelOnTimeOver(self):
		self.isCancelOnTimeover = True

if app.ENABLE_NEW_DROP_DIALOG:
	class QuestionDropDialog(ui.ScriptWindow):
		def __init__(self):
			ui.ScriptWindow.__init__(self)
			if app.ENABLE_WINDOW_SLIDE_EFFECT:
				self.AddFlag("animated_board")
			
			self.__CreateDialog()

		def __del__(self):
			ui.ScriptWindow.__del__(self)

		def __CreateDialog(self):
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/questiondropdialog.py")

			self.board = self.GetChild("board")
			self.textLine = self.GetChild("message")
			self.acceptButton = self.GetChild("accept")
			self.destroyButton = self.GetChild("destroy")
			self.sellButton = self.GetChild("sell_element")
			self.cancelButton = self.GetChild("cancel")
			self.itemSlot = self.GetChild("ItemSlot")
			self.itemSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
			self.itemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		def SetItemSlot(self, slotIndex):
			itemIndex = player.GetItemIndex(slotIndex)
			itemCount = player.GetItemCount(slotIndex)
			self.itemSlot.SetItemSlot(0, itemIndex, itemCount)
			self.itemSlot.SetPosition(120+80,45)			
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if not player.GetChangeLookVnum(player.INVENTORY, slotIndex) == 0:
					self.itemSlot.SetSlotCoverImage(slotIndex, "icon/item/ingame_convert_Mark.tga")
				else:
					self.itemSlot.EnableSlotCoverImage(slotIndex, False)

			item.SelectItem(player.GetItemIndex(slotIndex))

			metinSlot = [player.GetItemMetinSocket(slotIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
			attrSlot = [player.GetItemAttribute(slotIndex, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

			if item.IsAntiFlag(item.ITEM_ANTIFLAG_DROP):
				self.acceptButton.Down()
				self.acceptButton.Disable()

			if item.IsAntiFlag(item.ITEM_ANTIFLAG_DESTROY):
				self.destroyButton.Down()
				self.destroyButton.Disable()
			
			if app.ENABLE_SOUL_BIND_SYSTEM:
				if player.GetItemSealDate(player.INVENTORY, slotIndex) == -1 or player.GetItemSealDate(player.INVENTORY, slotIndex) > 0:
					self.acceptButton.Down()
					self.acceptButton.Disable()
					self.destroyButton.Down()
					self.destroyButton.Disable()
					self.sellButton.Down()
					self.sellButton.Disable()
			
			if item.IsAntiFlag(item.ITEM_ANTIFLAG_SELL):
				self.sellButton.Down()
				self.sellButton.Disable()
			
			self.itemToolTip = uitooltip.ItemToolTip()
			self.itemToolTip.SetInventoryItem(slotIndex) # 2019.02.11.owsap

		def Open(self):
			if 0 != self.itemToolTip:
				self.itemToolTip.HideToolTip()

			self.SetCenterPosition()
			self.SetTop()
			self.Show()

		def Close(self):
			if 0 != self.itemToolTip:
				self.itemToolTip.HideToolTip()

			self.Hide()

		def SetDlgSize(self, width, height):
			self.SetSize(width, height)
			self.board.SetSize(width, height)
			self.SetCenterPosition()
			self.UpdateRect()

		def OverInItem(self, slotNumber):
			if 0 != self.itemToolTip:
				self.itemToolTip.ShowToolTip()

		def OverOutItem(self):
			if 0 != self.itemToolTip:
				self.itemToolTip.HideToolTip()

		def SAFE_SetAcceptEvent(self, event):
			self.acceptButton.SAFE_SetEvent(event)

		def SAFE_SetCancelEvent(self, event):
			self.cancelButton.SAFE_SetEvent(event)

		def SetDestroyEvent(self, event):
			self.destroyButton.SetEvent(event)

		def SetSellEvent(self, event):
			self.sellButton.SetEvent(event)

		def SetAcceptEvent(self, event):
			self.acceptButton.SetEvent(event)

		def SetCancelEvent(self, event):
			self.cancelButton.SetEvent(event)

		def SetText(self, text):
			self.textLine.SetText(text)
			# self.textLine.SetFontColor(0.72, 1.0, 0.0)

		def SetAcceptText(self, text):
			self.acceptButton.SetText(text)

		def SetCancelText(self, text):
			self.cancelButton.SetText(text)

		def OnPressEscapeKey(self):
			self.Close()
			return True

class MoneyInputDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.moneyHeaderText = localeinfo.MONEY_INPUT_DIALOG_SELLPRICE
		self.__CreateDialog()

		self.SetMaxLength(9)

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __CreateDialog(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/moneyinputdialog.py")

		getObject = self.GetChild
		self.board = self.GetChild("board")
		self.acceptButton = getObject("AcceptButton")
		self.cancelButton = getObject("CancelButton")
		self.inputValue = getObject("InputValue")
		self.inputValue.SetNumberMode()
		self.inputValue.OnIMEUpdate = ui.__mem_func__(self.__OnValueUpdate)
		self.moneyText = getObject("MoneyValue")

		if app.ENABLE_CHEQUE_SYSTEM:
			self.chequeText = getObject("ChequeValue")
			self.inputChequeValue = getObject("InputValue_Cheque")
			self.inputChequeValue.OnIMEUpdate = ui.__mem_func__(self.__OnValueUpdate)
			self.inputChequeValue.OnMouseLeftButtonDown = ui.__mem_func__(self.__ClickChequeEditLine)
			self.inputValue.OnMouseLeftButtonDown = ui.__mem_func__(self.__ClickValueEditLine)

	def Open(self):
		self.inputValue.SetText("")
		self.inputValue.SetFocus()
		self.__OnValueUpdate()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		if app.ENABLE_CHEQUE_SYSTEM:
			self.inputChequeValue = None

		self.ClearDictionary()
		self.board = None
		self.acceptButton = None
		self.cancelButton = None
		self.inputValue = None
		self.Hide()

	def SetMax(self, length):
		length = min(12, length)
		self.inputValue.SetMax(length)

	def SetTitle(self, name):
		self.board.SetTitleName(name)

	def SetFocus(self):
		self.inputValue.SetFocus()

	def SetMaxLength(self, length):
		length = min(9, length)

		self.inputValue.SetMax(length)

	def SetMoneyHeaderText(self, text):
		self.moneyHeaderText = text

	def SetAcceptEvent(self, event):
		self.acceptButton.SetEvent(event)
		self.inputValue.OnIMEReturn = event

	def SetCancelEvent(self, event):
		self.board.SetCloseEvent(event)
		self.cancelButton.SetEvent(event)
		self.inputValue.OnPressEscapeKey = event

	def SetValue(self, value):
		value=str(value)
		self.inputValue.SetText(value)
		self.__OnValueUpdate()
		ime.SetCursorPosition(len(value)+1)

	def GetText(self):
		return self.inputValue.GetText()

	if app.ENABLE_CHEQUE_SYSTEM:
		def SetCheque(self, cheque):
			cheque=str(cheque)
			self.inputChequeValue.SetText(cheque)
			self.__OnValueUpdate()
			ime.SetCursorPosition(len(cheque)+1)

		def __ClickChequeEditLine(self):
			self.inputChequeValue.SetFocus()
			if len(self.inputValue.GetText()) <= 0:
				self.inputValue.SetText(str(0))

		def __ClickValueEditLine(self):
			self.inputValue.SetFocus()
			if len(self.inputChequeValue.GetText()) <= 0:
				self.inputChequeValue.SetText(str(0))

		def GetCheque(self):
			return self.inputChequeValue.GetText()

		def __OnValueUpdate(self):
			if self.inputValue.IsFocus():
				ui.EditLine.OnIMEUpdate(self.inputValue)
			elif self.inputChequeValue.IsFocus():
				ui.EditLine.OnIMEUpdate(self.inputChequeValue)
			else:
				pass

			text = self.inputValue.GetText()
			cheque_text = self.inputChequeValue.GetText()

			money = 0
			cheque = 0

			if text and text.isdigit():
				try:
					money = int(text)

					if money >= 10000000000:
						money = 10000000000 - 1
						self.inputValue.SetText(str(money))
				except ValueError:
					money = 0

			if cheque_text and cheque_text.isdigit():
				try:
					cheque = int(cheque_text)

					if cheque >= 1000:
						cheque = 1000 - 1
						self.inputChequeValue.SetText(str(cheque))
				except ValueError:
					cheque = 0

			self.chequeText.SetText(str(cheque) + " " + localeinfo.CHEQUE_SYSTEM_UNIT_WON)
			self.moneyText.SetText(localeinfo.NumberToMoneyString(money) + " " + localeinfo.CHEQUE_SYSTEM_UNIT_YANG)
	else:
		def __OnValueUpdate(self):
			ui.EditLine.OnIMEUpdate(self.inputValue)

			text = self.inputValue.GetText()

			money = 0
			if text and text.isdigit():
				try:
					money = int(text)

				except ValueError:
					money = 199999999

			self.moneyText.SetText(self.moneyHeaderText + localeinfo.NumberToMoneyString(money))

class InputPinCodeDialog(ui.ScriptWindow):
	PIN_CODE_TOOLTIP = [
		localeinfo.PIN_CODE_TOOLTIP_LINE1,
		localeinfo.PIN_CODE_TOOLTIP_LINE2,
		localeinfo.PIN_CODE_TOOLTIP_LINE3,
		localeinfo.PIN_CODE_TOOLTIP_LINE4,
		localeinfo.PIN_CODE_TOOLTIP_LINE5
	]

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__CreateDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __CreateDialog(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "UIScript/InputPinCodeDialog.py")

		getObject = self.GetChild
		self.board = getObject("Board")
		self.pinCodeSlot = getObject("PinCodeSlot")
		self.pinCodeValue = getObject("PinCodeValue")
		self.acceptButton = getObject("AcceptButton")
		self.cancelButton = getObject("CancelButton")
		self.toolTipButton = getObject("ToolTipButton")
		self.toolTip = self.CreateToolTip(localeinfo.INPUT_PIN_CODE_DIALOG_TITLE, self.PIN_CODE_TOOLTIP)
		self.toolTip.SetTop()
		self.toolTipButton.SetToolTipWindow(self.toolTip)

	def CreateToolTip(self, title, descList):
		toolTip = uitooltip.ToolTip()
		toolTip.SetTitle(title)
		toolTip.AppendSpace(7)

		for desc in descList:
			toolTip.AutoAppendTextLine(desc)

		toolTip.AlignHorizonalCenter()
		toolTip.SetTop()
		return toolTip

	def Open(self):
		self.pinCodeValue.SetFocus()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.ClearDictionary()
		self.board = None
		self.toolTipButton = None
		self.toolTip = None
		self.acceptButton = None
		self.cancelButton = None
		self.pinCodeSlot = None
		self.pinCodeValue = None
		self.Hide()

	def SetTitle(self, name):
		self.board.SetTitleName(name)

	def SetNumberMode(self):
		self.pinCodeValue.SetNumberMode()

	def SetUseCodePage(self, bUse = True):
		self.pinCodeValue.SetUseCodePage(bUse)

	def SetSecretMode(self):
		self.pinCodeValue.SetSecret()

	def SetFocus(self):
		self.pinCodeValue.SetFocus()

	def SetAcceptEvent(self, event):
		self.acceptButton.SetEvent(event)
		self.pinCodeValue.OnIMEReturn = event

	def SetCancelEvent(self, event):
		self.board.SetCloseEvent(event)
		self.cancelButton.SetEvent(event)
		self.pinCodeValue.OnPressEscapeKey = event

	def GetText(self):
		return self.pinCodeValue.GetText()

class InputNewPinCodeDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__CreateDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __CreateDialog(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "UIScript/InputNewPinCodeDialog.py")

		getObject = self.GetChild
		self.board = getObject("Board")
		self.acceptButton = getObject("AcceptButton")
		self.cancelButton = getObject("CancelButton")
		self.pinCodeSlot = getObject("PinCodeSlot")
		self.pinCodeSlotCheck = getObject("PinCodeSlotCheck")
		self.pinCodeValue = getObject("PinCodeValue")
		self.pinCodeValueCheck = getObject("PinCodeValueCheck")

		self.pinCodeValue.SetTabEvent(lambda arg = 1: self.OnNextFocus(arg))
		self.pinCodeValueCheck.SetTabEvent(lambda arg = 2: self.OnNextFocus(arg))

	def OnNextFocus(self, arg):
		if 1 == arg:
			self.pinCodeValue.KillFocus()
			self.pinCodeValueCheck.SetFocus()
		elif 2 == arg:
			self.pinCodeValueCheck.KillFocus()
			self.pinCodeValue.SetFocus()

	def Open(self):
		self.pinCodeValue.SetFocus()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Destroy(self):
		self.Close()

	def Close(self):
		self.ClearDictionary()
		self.board = None
		self.acceptButton = None
		self.cancelButton = None
		self.pinCodeSlot = None
		self.pinCodeSlotCheck = None
		self.pinCodeValue = None
		self.pinCodeValueCheck = None
		self.Hide()

	def SetTitle(self, name):
		self.board.SetTitleName(name)

	def SetNumberMode(self):
		self.pinCodeValue.SetNumberMode()
		self.pinCodeValueCheck.SetNumberMode()

	def SetUseCodePage(self, bUse = True):
		self.pinCodeValue.SetUseCodePage(bUse)
		self.pinCodeValueCheck.SetUseCodePage(bUse)

	def SetSecretMode(self):
		self.pinCodeValue.SetSecret()
		self.pinCodeValueCheck.SetSecret()

	def SetFocus(self):
		self.pinCodeValue.SetFocus()

	def SetAcceptEvent(self, event):
		self.acceptButton.SetEvent(event)
		self.pinCodeValueCheck.OnIMEReturn = event

	def SetCancelEvent(self, event):
		self.board.SetCloseEvent(event)
		self.cancelButton.SetEvent(event)
		self.pinCodeValue.OnPressEscapeKey = event
		self.pinCodeValueCheck.OnPressEscapeKey = event

	def GetText(self):
		return self.pinCodeValue.GetText()

	def GetTextCheck(self):
		return self.pinCodeValueCheck.GetText()

class ItemQuestDialog(ui.BoardWithTitleBar):
	POSITIVE_COLOR = 0xFF8AB98E  # Green - player has enough
	NEGATIVE_COLOR = 0xFFE57976  # Red - player doesn't have enough

	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		self.AddFlag("attach")
		self.AddFlag("float")
		self.AddFlag("movable")
		self.__children = {}
		self.tooltipItem = uitooltip.ItemToolTip()
		self.tooltipItem.HideToolTip()

	def Destroy(self):
		self.__children = {}

	def Open(self, itemList, questionText=""):
		self.Destroy()

		window = ui.ThinBoardCircle()
		window.SetParent(self)
		window.SetPosition(10, 35)
		window.Show()
		self.__children["window"] = window

		yPos = 0
		windowWidth = 180

		# Add question/description text if provided
		if questionText:
			questionLine = ui.TextLine()
			questionLine.SetParent(window)
			questionLine.SetPosition(210, 10)
			questionLine.SetText(questionText)
			questionLine.Show()
			self.__children["questionText"] = questionLine

			textWidth = questionLine.GetTextSize()[0] + 20
			if textWidth > windowWidth:
				windowWidth = textWidth

			yPos += 25

		# Add "Required:" label
		requiredLabel = ui.TextLine()
		requiredLabel.SetParent(window)
		requiredLabel.SetPosition(140, yPos + 5)
		requiredLabel.SetText(localeinfo.ITEMQUEST_REQUIRED)
		requiredLabel.SetPackedFontColor(0xFFFFCC00)
		requiredLabel.Show()
		self.__children["requiredLabel"] = requiredLabel
		yPos += 20

		for itemData in itemList:
			itemVnum = itemData[0]
			requiredCount = itemData[1]
			item.SelectItem(itemVnum)
			playerCount = player.GetItemCountByVnum(itemVnum)
			yPos += 8

			itemImage = ui.ExpandedImageBox()
			itemImage.SetParent(window)
			if questionText:
				itemImage.SetPosition(175, yPos)
			else:
				itemImage.SetPosition(10, yPos)
			itemImage.LoadImage(item.GetIconImageFileName())
			itemImage.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverIn), itemVnum)
			itemImage.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOut))

			itemImage.Show()
			self.__children["icon%d"%yPos] = itemImage

			# Format: "ItemName PlayerCount / xRequiredCount"
			displayText = "%s %d / x%d" % (item.GetItemName(), playerCount, requiredCount)
			textColor = self.POSITIVE_COLOR if playerCount >= requiredCount else self.NEGATIVE_COLOR

			itemName = ui.TextLine()
			itemName.SetParent(window)
			itemName.SetPosition(10 + 155 + 5, yPos + 8)
			itemName.SetText(displayText)
			itemName.SetPackedFontColor(textColor)
			itemName.SetHorizontalAlignLeft()
			itemName.Show()
			self.__children["name%d"%yPos] = itemName

			if 10 + 32 + 5 + itemName.GetTextSize()[0] + 10 > windowWidth:
				windowWidth = 10 + 32 + 5 + itemName.GetTextSize()[0] + 10

			yPos += itemImage.GetHeight()

		window.SetSize(windowWidth, yPos + 10)
		self.SetSize(10 + window.GetWidth() + 10, 35 + window.GetHeight() + 15)

		acceptBtn = ui.Button()
		acceptBtn.SetParent(self)
		acceptBtn.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		acceptBtn.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		acceptBtn.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		acceptBtn.SetText(localeinfo.OFFLINESHOP_ACCEPT_OFFER_QUESTION_ACCEPT)
		acceptBtn.Show()
		acceptBtn.SetPosition((self.GetWidth() / 2 ) + 10, window.GetLocalPosition()[1]+ window.GetHeight() + 10)
		self.__children["acceptBtn"] = acceptBtn

		cancelBtn = ui.Button()
		cancelBtn.SetParent(self)
		cancelBtn.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		cancelBtn.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		cancelBtn.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		cancelBtn.SetText(localeinfo.OFFLINESHOP_ACCEPT_OFFER_QUESTION_CANCEL)
		cancelBtn.SetEvent(self.Hide)
		cancelBtn.Show()
		cancelBtn.SetPosition((self.GetWidth() / 2 ) - (acceptBtn.GetWidth() + 10), window.GetLocalPosition()[1]+ window.GetHeight() + 10)
		self.__children["cancelBtn"] = cancelBtn
		self.SetSize(self.GetWidth(), self.GetHeight() + 30)
		self.SetCenterPosition()
		self.Show()
		self.SetTop()

	def SelectEvent(self, func, *arg):
		self.__children["acceptBtn"].SAFE_SetEvent(func, arg)

	def OnOverIn(self, itemVnum):
		self.tooltipItem.SetItemToolTip(itemVnum)

	def OnOverOut(self):
		self.tooltipItem.HideToolTip()

	def OnPressEscapeKey(self):
		self.Hide()
		self.Destroy()
		return True

class OnlinePopup(ui.BorderB):
	def __init__(self):
		ui.BorderB.__init__(self)
		
		self.isActiveSlide = False
		self.isActiveSlideOut = False
		self.endTime = 0
		self.wndWidth = 0

		self.textLine = ui.TextLine()
		self.textLine.SetParent(self)
		self.textLine.SetWindowHorizontalAlignCenter()
		self.textLine.SetWindowVerticalAlignCenter()
		self.textLine.SetHorizontalAlignCenter()
		self.textLine.SetVerticalAlignCenter()
		self.textLine.SetPosition(13, 0)
		self.textLine.Show()
		
		self.onlineImage = ui.ImageBox()
		self.onlineImage.SetParent(self)
		self.onlineImage.SetPosition(8, 8)
		self.onlineImage.LoadImage("d:/ymir work/ui/game/windows/messenger_list_online.sub")
		self.onlineImage.Show()
		
	def __del__(self):
		ui.BorderB.__del__(self)

	def SlideIn(self):
		self.SetTop()
		self.Show()
		
		self.isActiveSlide = True
		self.endTime = app.GetGlobalTimeStamp() + 5

	def Close(self):
		self.Hide()

	def Destroy(self):
		self.Close()

	def SetUserName(self, name):
		self.textLine.SetText(localeinfo.PLAYER_IS_ONLINE % str(name))
		
		self.wndWidth = self.textLine.GetTextSize()[0] + 40
		self.SetSize(self.wndWidth, 25)
		self.SetPosition(-self.wndWidth, wndMgr.GetScreenHeight() - 200)
		
	def OnUpdate(self):
		if self.isActiveSlide and self.isActiveSlide == True:
			x, y = self.GetLocalPosition()
			if x < 0:
				self.SetPosition(x + 4, y)
				
		if self.endTime - app.GetGlobalTimeStamp() <= 0 and self.isActiveSlideOut == False and self.isActiveSlide == True:
			self.isActiveSlide = False
			self.isActiveSlideOut = True
				
		if self.isActiveSlideOut and self.isActiveSlideOut == True:
			x, y = self.GetLocalPosition()
			if x > -(self.wndWidth):
				self.SetPosition(x - 4, y)
				
			if x <= -(self.wndWidth):
				self.isActiveSlideOut = False
				self.Close()

if app.ENABLE_SORT_INVENTORY or app.USE_STACK_INVENTORY:
	class OrganizeItemsDialog(ui.ScriptWindow):
		def SetOnPotion(self, pots):
			if not pots:
				self.activateBtn.Hide()
				self.deactivateBtn.Hide()

				self.SetSize(self.origWidth, self.origHeight)
				self.board.SetSize(self.origWidth, self.origHeight)

				self.image.SetScale(1.0, 1.0)
			else:
				self.activateBtn.Show()
				self.deactivateBtn.Show()

				self.SetSize(self.origWidth, self.origHeight + 23)
				self.board.SetSize(self.origWidth, self.origHeight + 23)

				self.image.SetScale(1.0, 1.3)

			self.potsType = pots

		def __Activate(self, on):
			net.SendChatPacket("/autouse_blend_items %d" % (on))
			self.Close()

		def __CreateDialog(self):
			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "uiscript/organizeitems_dialog.py")

				self.board = self.GetChild("board")
				self.closeButton = self.GetChild("ui_close_button")
				self.closeButton.Hide()

				self.titleBar = self.GetChild("TitleBar")

				if app.ENABLE_SORT_INVENTORY:
					self.sortButton = self.GetChild("ui_sort_button")
				else:
					self.GetChild("ui_sort_button").Hide()

				if app.USE_STACK_INVENTORY:
					self.stackButton = self.GetChild("ui_stack_button")
				else:
					self.GetChild("ui_stack_button").Hide()

				self.potsType = False

				tmp = self.GetChild("ui_activate_button")
				tmp.SetEvent(ui.__mem_func__(self.__Activate), 1)
				self.activateBtn = tmp

				tmp = self.GetChild("ui_deactivate_button")
				tmp.SetEvent(ui.__mem_func__(self.__Activate), 0)
				self.deactivateBtn = tmp

				self.origWidth = self.GetWidth()
				self.origHeight = self.GetHeight()

				self.closeButtonX, self.closeButtonY = self.closeButton.GetLocalPosition()

				self.image = self.GetChild("WindowBG")
			except Exception as e:
				import dbg
				dbg.TraceError(str(e))
				app.Abort()

		def __init__(self):
			ui.ScriptWindow.__init__(self)

			if app.ENABLE_WINDOW_SLIDE_EFFECT:
				self.AddFlag("animated_board")

			self.board = None

			self.titleBar = None

			self.closeButton = None

			self.__CreateDialog()

		def __del__(self):
			ui.ScriptWindow.__del__(self)

		def Destroy(self):
			if self.titleBar:
				self.titleBar.SetCloseEvent(None)
				self.titleBar = None

			if self.closeButton:
				self.closeButton.SetEvent(None)
				self.closeButton = None

			if app.ENABLE_SORT_INVENTORY and self.sortButton:
				self.sortButton.SetEvent(None)
				self.sortButton = None

			if app.USE_STACK_INVENTORY and self.stackButton:
				self.stackButton.SetEvent(None)
				self.stackButton = None

			if self.activateBtn:
				self.activateBtn.SetEvent(None)
				self.activateBtn = None

			if self.deactivateBtn:
				self.deactivateBtn.SetEvent(None)
				self.deactivateBtn = None

			self.board = None

			self.ClearDictionary()

		def Open(self):
			self.SetCenterPosition()
			self.SetTop()
			self.Show()

		def Close(self):
			self.Hide()

		if app.ENABLE_SORT_INVENTORY:
			def SetSortEvent(self, event):
				self.sortButton.SetEvent(event)

		if app.USE_STACK_INVENTORY:
			def SetStackEvent(self, event):
				self.stackButton.SetEvent(event)

		def SetCancelEvent(self, event):
			self.closeButton.SetEvent(event)

		def SetCloserEvent(self, event):
			self.titleBar.SetCloseEvent(event)

		def OnClose(self):
			self.Close()

		def OnPressEscapeKey(self):
			self.Close()
			return True

if app.USE_ITEM_ATTR_BACKUP_MODE:
	class SelectItemBackupAttr(ui.ScriptWindow):
		def Show(self):
			self.SetCenterPosition()
			self.SetTop()

			ui.ScriptWindow.Show(self)

		def Clear(self):
			for v in self.oldBonuses.values():
				v.SetText("")

			for v in self.newBonuses.values():
				v.SetText("")

		def Refresh(self):
			self.Clear()

			attrSlot = [player.GetItemAttribute(self.window, self.cell, i) for i in xrange(item.ITEM_ATTRIBUTE_SLOT_MAX_NUM)]
			for i in xrange(item.ITEM_ATTRIBUTE_SLOT_MAX_NUM):
				attrType = attrSlot[i][0]
				attrValue = attrSlot[i][1]

				if attrType == 0 or attrValue == 0:
					self.newBonuses[i].SetText("")
					continue

				if attrValue > 0:
					self.newBonuses[i].SetPackedFontColor(grp.GenerateColor(0.6911, 0.8754, 0.7068, 1.0))
				else:
					self.newBonuses[i].SetPackedFontColor(grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0))

				self.newBonuses[i].SetText(uitooltip.GET_AFFECT_STRING(attrType, attrValue))

			attrSlot = [player.GetItemAttributeBackup(self.window, self.cell, i) for i in xrange(item.ITEM_ATTRIBUTE_SLOT_MAX_NUM)]
			for i in xrange(item.ITEM_ATTRIBUTE_SLOT_MAX_NUM):
				attrType = attrSlot[i][0]
				attrValue = attrSlot[i][1]

				if attrType == 0 or attrValue == 0:
					self.oldBonuses[i].SetText("")
					continue

				if attrValue > 0:
					self.oldBonuses[i].SetPackedFontColor(grp.GenerateColor(0.6911, 0.8754, 0.7068, 1.0))
				else:
					self.oldBonuses[i].SetPackedFontColor(grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0))

				self.oldBonuses[i].SetText(uitooltip.GET_AFFECT_STRING(attrType, attrValue))

		def Open(self, window, cell):
			itemVnum = player.GetItemIndex(window, cell)
			if not itemVnum:
				return

			self.window = window
			self.cell = cell

			self.slotItem.SetItemSlot(0, itemVnum, 0)
			self.Refresh()
			self.Show()

		def Close(self):
			self.Hide()

		def OnPressEscapeKey(self):
			self.Close()
			return True

		def ChooseOld(self):
			net.SendItemDecisionBackupAttr(self.window, self.cell, False)
			self.Close()

		def ChooseNew(self):
			net.SendItemDecisionBackupAttr(self.window, self.cell, True)
			self.Close()

		def __LoadDialog(self):
			self.AddFlag("movable")

			self.board = ui.BoardWithTitleBar()
			self.board.SetParent(self)
			self.board.SetSize(465, 195)
			self.board.SetTitleName(localeinfo.SWITCH_MODE_ATTR_TITLE)
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
			self.board.Show()

			self.SetSize(self.board.GetWidth(), self.board.GetHeight())

			self.horizontalBarOld = ui.HorizontalBar()
			self.horizontalBarOld.Create(200)
			self.horizontalBarOld.SetParent(self.board)
			self.horizontalBarOld.SetPosition(10, 35)
			self.horizontalBarOld.SetWidth(200)
			self.horizontalBarOld.Show()

			self.horizontalBarOldText = ui.TextLine()
			self.horizontalBarOldText.SetParent(self.horizontalBarOld)
			self.horizontalBarOldText.SetPosition(self.horizontalBarOld.GetWidth() / 2, 3)
			self.horizontalBarOldText.SetText(localeinfo.SWITCH_MODE_ATTR_TITLE_OLD)
			self.horizontalBarOldText.SetHorizontalAlignCenter()
			self.horizontalBarOldText.Show()

			self.thinboardOld = ui.ThinBoardCircle()
			self.thinboardOld.SetParent(self.horizontalBarOld)
			self.thinboardOld.SetSize(200, 95)
			self.thinboardOld.SetPosition(0, 19)

			if self.thinboardOld.Base:
				self.thinboardOld.Base.SetColor(grp.GenerateColor(255.0, 255.0, 255.0, 0.5))

			self.thinboardOld.Show()

			self.horizontalBarNew = ui.HorizontalBar()
			self.horizontalBarNew.Create(200)
			self.horizontalBarNew.SetParent(self.board)
			self.horizontalBarNew.SetPosition(255, 35)
			self.horizontalBarNew.SetWidth(200)
			self.horizontalBarNew.Show()

			self.horizontalBarNewText = ui.TextLine()
			self.horizontalBarNewText.SetParent(self.horizontalBarNew)
			self.horizontalBarNewText.SetPosition(self.horizontalBarNew.GetWidth() / 2, 3)
			self.horizontalBarNewText.SetText(localeinfo.SWITCH_MODE_ATTR_TITLE_NEW)
			self.horizontalBarNewText.SetHorizontalAlignCenter()
			self.horizontalBarNewText.Show()

			self.thinboardNew = ui.ThinBoardCircle()
			self.thinboardNew.SetParent(self.horizontalBarNew)
			self.thinboardNew.SetSize(200, 95)
			self.thinboardNew.SetPosition(0, 19)

			if self.thinboardNew.Base:
				self.thinboardNew.Base.SetColor(grp.GenerateColor(255.0, 255.0, 255.0, 0.5))

			self.thinboardNew.Show()

			self.slotItem = ui.GridSlotWindow()
			self.slotItem.SetParent(self)
			self.slotItem.SetPosition(217, 49)
			self.slotItem.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
			self.slotItem.ArrangeSlot(0, 1, 3, 32, 32, 0, 0)
			self.slotItem.RefreshSlot()
			self.slotItem.SetSlotBaseImage("d:/ymir work/ui/public/slot_base.sub", 1.0, 1.0, 1.0, 1.0)
			self.slotItem.ClearSlot(0)
			#self.slotItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
			#self.slotItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			self.slotItem.Show()

			self.oldBonuses = {}
			self.newBonuses = {}

			self.window = 0
			self.cell = 0

			for x in xrange(item.ITEM_ATTRIBUTE_SLOT_MAX_NUM):
				self.oldBonuses[x] = ui.TextLine()
				self.oldBonuses[x].SetParent(self.thinboardOld)
				self.oldBonuses[x].Show()
				self.oldBonuses[x].SetWindowHorizontalAlignCenter()
				self.oldBonuses[x].SetHorizontalAlignCenter()
				self.oldBonuses[x].SetText("")
				self.oldBonuses[x].SetPosition(0, 5 + (12 * x))

				self.newBonuses[x] = ui.TextLine()
				self.newBonuses[x].SetParent(self.thinboardNew)
				self.newBonuses[x].Show()
				self.newBonuses[x].SetWindowHorizontalAlignCenter()
				self.newBonuses[x].SetHorizontalAlignCenter()
				self.newBonuses[x].SetText("")
				self.newBonuses[x].SetPosition(0, 5 + (12 * x))

			self.oldBonusButton = ui.MakeButton(self, 66, 160, "", "d:/ymir work/ui/public/", "large_button_01.sub", "large_button_02.sub", "large_button_03.sub")
			self.oldBonusButton.SetText(localeinfo.SWITCH_MODE_ATTR_TITLE_CHOOSE)
			self.oldBonusButton.SetEvent(ui.__mem_func__(self.ChooseOld))

			self.newBonusButton = ui.MakeButton(self, 311, 160, "", "d:/ymir work/ui/public/", "large_button_01.sub", "large_button_02.sub", "large_button_03.sub")
			self.newBonusButton.SetText(localeinfo.SWITCH_MODE_ATTR_TITLE_CHOOSE)
			self.newBonusButton.SetEvent(ui.__mem_func__(self.ChooseNew))

		def __init__(self):
			ui.ScriptWindow.__init__(self, "TOP_MOST")

			if app.ENABLE_WINDOW_SLIDE_EFFECT:
				self.AddFlag("animated_board")

			self.__LoadDialog()

		def Destroy(self):
			if self.oldBonusButton:
				self.oldBonusButton.SetEvent(None)
				del self.oldBonusButton
				self.oldBonusButton = None

			if self.newBonusButton:
				self.newBonusButton.SetEvent(None)
				del self.newBonusButton
				self.newBonusButton = None

			for v in self.oldBonuses.values():
				del v

			self.oldBonuses = {}

			for v in self.newBonuses.values():
				del v

			self.newBonuses = {}

			if self.thinboardOld:
				del self.thinboardOld
				self.thinboardOld = None

			if self.horizontalBarOldText:
				del self.horizontalBarOldText
				self.horizontalBarOldText = None

			if self.horizontalBarOld:
				del self.horizontalBarOld
				self.horizontalBarOld = None

			if self.thinboardNew:
				del self.thinboardNew
				self.thinboardNew = None

			if self.horizontalBarNewText:
				del self.horizontalBarNewText
				self.horizontalBarNewText = None

			if self.horizontalBarNew:
				del self.horizontalBarNew
				self.horizontalBarNew = None

			if self.board:
				self.board.SetCloseEvent(None)
				del self.board
				self.board = None

			self.ClearDictionary()

		def __del__(self):
			ui.ScriptWindow.__del__(self)

class PickItemDialog(ui.ScriptWindow):
	def SetTitleName(self, name):
		self.board.SetTitleName(name)

	def SetMax(self, limit):
		self.pick_value.SetMax(limit)

	def GetCount(self):
		text = self.pick_value.GetText()
		if len(text) > 0 and text.isdigit():
			return long(text)

		self.pick_value.SetText("0")
		self.pick_value.SetFocus()
		ime.SetCursorPosition(-1)
		return 0

	def Close(self):
		if self.pick_value.IsFocus():
			self.pick_value.KillFocus()

		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Accept(self):
		count = self.GetCount()
		if count > 0 and self.event_accept:
			self.event_accept(self.slot_index, count, self.split_item if app.USE_AUTO_SPLIT_ITEMS else False)

		self.Close()

	def Open(self, slot_index, max_count):
		(mouseX, mouseY) = wndMgr.GetMousePosition()

		if mouseX + self.width / 2 > wndMgr.GetScreenWidth():
			xPos = wndMgr.GetScreenWidth() - self.width
		elif mouseX - self.width / 2 < 0:
			xPos = 0
		else:
			xPos = mouseX - self.width / 2

		self.SetPosition(xPos, mouseY - self.height - 20)

		if localeinfo.IsARABIC():
			self.max_count_text.SetText("/" + str(max_count))
		else:
			self.max_count_text.SetText(" / " + str(max_count))

		self.slot_index = slot_index
		self.max_count = max_count

		if app.ENABLE_REMEMBER_LAST_SPLIT:
			last_split_count = systemSetting.GetLastSplitData()
			if max_count >= last_split_count:
				self.pick_value.SetText(str(last_split_count))
			else:
				self.pick_value.SetText("")
		else:
			self.pick_value.SetText("")

		self.pick_value.SetFocus()
		ime.SetCursorPosition(-1)

		if app.USE_AUTO_SPLIT_ITEMS:
			self.split_item = False
			self.split_button.SetUp()

		self.Show()
		self.SetTop()

	def SetAcceptEvent(self, event):
		self.event_accept = event

	def __OnValueUpdate(self):
		ui.EditLine.OnIMEUpdate(self.pick_value)

		text = self.pick_value.GetText()
		if len(text) == 0:
			return

		if text[0] == "0":
			self.pick_value.SetText("")
			ime.SetCursorPosition(-1)
			self.__OnValueUpdate()
			return

		if long(text) > 2000:
			self.pick_value.SetText("2000")
			ime.SetCursorPosition(-1)
			self.__OnValueUpdate()
		elif long(text) > self.max_count:
			self.pick_value.SetText(str(self.max_count))
			ime.SetCursorPosition(-1)
			self.__OnValueUpdate()

	if app.USE_AUTO_SPLIT_ITEMS:
		def OnSetSplit(self, status):
			self.split_item = status

	def __Load(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/pickitemdialog.py")
		except:
			import exception
			exception.Abort("PickItemDialog.__Load.Load")

		try:
			self.board = self.GetChild("board_ui")
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))

			self.accept_button = self.GetChild("accept_button_ui")
			self.accept_button.SetEvent(ui.__mem_func__(self.Accept))

			self.close_button = self.GetChild("close_button_ui")
			self.close_button.SetEvent(ui.__mem_func__(self.Close))

			self.max_count_text = self.GetChild("max_count_ui")

			self.pick_value = self.GetChild("pick_value_ui")
			self.pick_value.SetReturnEvent(ui.__mem_func__(self.Accept))
			self.pick_value.SetEscapeEvent(ui.__mem_func__(self.Close))
			self.pick_value.OnIMEUpdate = ui.__mem_func__(self.__OnValueUpdate)

			if app.USE_AUTO_SPLIT_ITEMS:
				self.split_button = self.GetChild("split_button_ui")
				self.split_button.SetToggleDownEvent(ui.__mem_func__(self.OnSetSplit), True)
				self.split_button.SetToggleUpEvent(ui.__mem_func__(self.OnSetSplit), False)
		except:
			import exception
			exception.Abort("PickItemDialog.__Load.Bind")

		self.width = self.GetWidth()
		self.height = self.GetHeight()

		self.max_count = 0

		if app.USE_AUTO_SPLIT_ITEMS:
			self.split_item = False

		self.event_accept = None

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.__Load()

	def Destroy(self):
		self.event_accept = None

		self.board.SetCloseEvent(None)
		self.board = None

		if self.pick_value.IsFocus():
			self.pick_value.KillFocus()

		self.pick_value.SetReturnEvent(None)
		self.pick_value.SetEscapeEvent(None)
		self.pick_value.OnIMEUpdate = None
		self.pick_value = None

		if app.USE_AUTO_SPLIT_ITEMS:
			self.split_button.SetToggleDownEvent(None)
			self.split_button.SetToggleUpEvent(None)
			self.split_button = None

		self.ClearDictionary()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

class PickMoneyDialog(ui.ScriptWindow):
	def LoadDialog(self):
		pass

	def SetTitleName(self, name):
		self.board.SetTitleName(name)

	def SetMax(self, limit, cheque_limit = 0):
		self.value.SetMax(limit)

		if app.ENABLE_CHEQUE_SYSTEM:
			self.cheque_value.SetMax(cheque_limit)

	def GetCount(self):
		text = self.value.GetText()
		if len(text) > 0 and text.isdigit():
			return long(text)

		self.value.SetText("0")
		self.value.SetFocus()
		ime.SetCursorPosition(-1)
		return 0

	if app.ENABLE_CHEQUE_SYSTEM:
		def GetChequeCount(self):
			text = self.cheque_value.GetText()
			if len(text) > 0 and text.isdigit():
				return long(text)

			self.cheque_value.SetText("0")
			self.cheque_value.SetFocus()
			ime.SetCursorPosition(-1)
			return 0

	def Close(self):
		if self.value.IsFocus():
			self.value.KillFocus()

		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Accept(self):
		if self.event_accept:
			if app.ENABLE_CHEQUE_SYSTEM:
				cheque = self.GetChequeCount()
				money = self.GetCount()

				if (cheque > 0 or money > 0):
					self.event_accept(money, cheque)
			else:
				money = self.GetCount()
				if money > 0:
					self.event_accept(money)

		self.Close()

	def Open(self, max_count, max_pick_count, max_cheque_count = 0, max_pick_cheque_count = 0):
		(mouseX, mouseY) = wndMgr.GetMousePosition()

		if mouseX + self.width / 2 > wndMgr.GetScreenWidth():
			xPos = wndMgr.GetScreenWidth() - self.width
		elif mouseX - self.width / 2 < 0:
			xPos = 0
		else:
			xPos = mouseX - self.width / 2

		self.SetPosition(xPos, mouseY - self.height - 20)

		if localeinfo.IsARABIC():
			self.max_count_text.SetText("/" + localeinfo.NumberToStringDotted(max_count))
		else:
			self.max_count_text.SetText(" / " + localeinfo.NumberToStringDotted(max_count))

		self.value.SetText("")

		self.max_count = max_count
		self.max_pick_count = max_pick_count

		if app.ENABLE_CHEQUE_SYSTEM:
			if localeinfo.IsARABIC():
				self.max_cheque_count_text.SetText("/" + str(max_cheque_count))
			else:
				self.max_cheque_count_text.SetText(" / " + str(max_cheque_count))

			self.cheque_value.SetText("")

			self.max_cheque_count = max_cheque_count
			self.max_pick_cheque_count = max_pick_cheque_count

		self.SetFocus(0)

		self.Show()
		self.SetTop()

	def SetFocus(self, num):
		if num == 0:
			if app.ENABLE_CHEQUE_SYSTEM and self.cheque_value.IsFocus():
				self.cheque_value.KillFocus()

			self.value.SetFocus()
			ime.SetCursorPosition(-1)
		elif app.ENABLE_CHEQUE_SYSTEM and num == 1:
			if self.value.IsFocus():
				self.value.KillFocus()

			self.cheque_value.SetFocus()
			ime.SetCursorPosition(-1)

	def SetAcceptEvent(self, event):
		self.event_accept = event

	def OnValueUpdate(self):
		ui.EditLine.OnIMEUpdate(self.value)

		text = self.value.GetText()
		if len(text) == 0:
			return

		if text.isdigit():
			if text[0] == "0":
				self.value.SetText("")
				ime.SetCursorPosition(-1)
				self.OnValueUpdate()
				return

			if long(text) > self.max_count:
				self.value.SetText(str(self.max_count))
				ime.SetCursorPosition(-1)
				self.OnValueUpdate()
			elif long(text) > self.max_pick_count:
				self.value.SetText(str(self.max_pick_count))
				ime.SetCursorPosition(-1)
				self.OnValueUpdate()
		else:
			newtext = ""
			refresh = False
			replace = False

			for char in text:
				if char in "0123456789k":
					if char == "k":
						replace = True

					newtext += char
				else:
					refresh = True

			if refresh:
				self.value.SetText(newtext)
				ime.SetCursorPosition(-1)
				self.OnValueUpdate()
			else:
				text = text.replace("k", "000")

				if replace or long(text) > self.max_count or long(text) > self.max_pick_count:
					if replace:
						self.value.SetText(text)
					elif long(text) > self.max_count:
						self.value.SetText(str(self.max_count))
					else:
						self.value.SetText(str(self.max_pick_count))

					ime.SetCursorPosition(-1)
					self.OnValueUpdate()

	if app.ENABLE_CHEQUE_SYSTEM:
		def OnChequeValueUpdate(self):
			ui.EditLine.OnIMEUpdate(self.cheque_value)

			text = self.cheque_value.GetText()
			if len(text) == 0:
				return

			if text.isdigit():
				if text[0] == "0":
					self.cheque_value.SetText("")
					ime.SetCursorPosition(-1)
					self.OnChequeValueUpdate()
					return

				if long(text) > self.max_cheque_count:
					self.cheque_value.SetText(str(self.max_cheque_count))
					ime.SetCursorPosition(-1)
					self.OnChequeValueUpdate()
				elif long(text) > self.max_pick_cheque_count:
					self.cheque_value.SetText(str(self.max_pick_cheque_count))
					ime.SetCursorPosition(-1)
					self.OnChequeValueUpdate()

		def OnTab(self):
			if self.value.IsFocus():
				self.value.KillFocus()
				self.cheque_value.SetFocus()
			else:
				if self.cheque_value.IsFocus():
					self.cheque_value.KillFocus()

				self.value.SetFocus()

			ime.SetCursorPosition(-1)

	def __Load(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/pickmoneydialog.py")
		except:
			import exception
			exception.Abort("PickMoneyDialog.__Load.Load")

		try:
			self.board = self.GetChild("board_ui")
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))

			self.accept_button = self.GetChild("accept_button_ui")
			self.accept_button.SetEvent(ui.__mem_func__(self.Accept))

			self.close_button = self.GetChild("close_button_ui")
			self.close_button.SetEvent(ui.__mem_func__(self.Close))

			self.max_count_text = self.GetChild("max_count_ui")

			self.value = self.GetChild("value_ui")
			self.value.SetReturnEvent(ui.__mem_func__(self.Accept))
			self.value.SetEscapeEvent(ui.__mem_func__(self.Close))
			self.value.OnIMEUpdate = ui.__mem_func__(self.OnValueUpdate)

			if app.ENABLE_CHEQUE_SYSTEM:
				self.value.SetTabEvent(ui.__mem_func__(self.OnTab))

				self.max_cheque_count_text = self.GetChild("max_cheque_count_ui")

				self.cheque_value = self.GetChild("cheque_value_ui")
				self.cheque_value.SetReturnEvent(ui.__mem_func__(self.Accept))
				self.cheque_value.SetEscapeEvent(ui.__mem_func__(self.Close))
				self.cheque_value.OnIMEUpdate = ui.__mem_func__(self.OnChequeValueUpdate)
				self.cheque_value.SetTabEvent(ui.__mem_func__(self.OnTab))
		except:
			import exception
			exception.Abort("PickMoneyDialog.__Load.Bind")

		self.width = self.GetWidth()
		self.height = self.GetHeight()

		self.max_count = 0

		self.event_accept = None

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.__Load()

	def Destroy(self):
		self.event_accept = None

		if self.value.IsFocus():
			self.value.KillFocus()

		self.value.SetReturnEvent(None)
		self.value.SetEscapeEvent(None)
		self.value.OnIMEUpdate = None
		self.value = None

		self.max_count_text = None

		if app.ENABLE_CHEQUE_SYSTEM:
			if self.cheque_value.IsFocus():
				self.cheque_value.KillFocus()

			self.cheque_value.SetReturnEvent(None)
			self.cheque_value.SetEscapeEvent(None)
			self.cheque_value.OnIMEUpdate = None
			self.cheque_value = None

			self.max_cheque_count_text = None

		self.accept_button.SetEvent(None)
		self.accept_button = None

		self.close_button.SetEvent(None)
		self.close_button = None

		self.board.SetCloseEvent(None)
		self.board = None

		self.ClearDictionary()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

class PickETCDialog(ui.ScriptWindow):
	def SetTitleName(self, name):
		self.board.SetTitleName(name)

	def SetMax(self, limit):
		self.pick_value.SetMax(limit)

	def GetCount(self):
		text = self.pick_value.GetText()
		if len(text) > 0 and text.isdigit():
			return long(text)

		self.pick_value.SetText("0")
		self.pick_value.SetFocus()
		ime.SetCursorPosition(-1)
		return 0

	def Close(self):
		if self.pick_value.IsFocus():
			self.pick_value.KillFocus()

		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Accept(self):
		count = self.GetCount()
		if count > 0 and self.event_accept:
			self.event_accept(count)

		self.Close()

	def Open(self, max_count, max_insert_count, unit_name, dotted):
		(mouseX, mouseY) = wndMgr.GetMousePosition()

		if mouseX + self.width / 2 > wndMgr.GetScreenWidth():
			xPos = wndMgr.GetScreenWidth() - self.width
		elif mouseX - self.width / 2 < 0:
			xPos = 0
		else:
			xPos = mouseX - self.width / 2

		self.SetPosition(xPos, mouseY - self.height - 20)

		if localeinfo.IsARABIC():
			self.max_count_text.SetText("/{} {}".format(localeinfo.NumberToStringDotted(max_count) if dotted else max_count, unit_name))
		else:
			self.max_count_text.SetText(" / {} {}".format(localeinfo.NumberToStringDotted(max_count) if dotted else max_count, unit_name))

		self.max_count = max_count
		self.max_insert_count = max_insert_count

		self.pick_value.SetText("")

		self.pick_value.SetFocus()
		ime.SetCursorPosition(-1)

		self.Show()
		self.SetTop()

	def SetAcceptEvent(self, event):
		self.event_accept = event

	def __OnValueUpdate(self):
		ui.EditLine.OnIMEUpdate(self.pick_value)

		text = self.pick_value.GetText()
		if len(text) == 0:
			return

		if text[0] == "0":
			self.pick_value.SetText("")
			ime.SetCursorPosition(-1)
			self.__OnValueUpdate()
			return

		if long(text) > self.max_count:
			self.pick_value.SetText(str(self.max_count))
			ime.SetCursorPosition(-1)
			self.__OnValueUpdate()
		elif long(text) > self.max_insert_count:
			self.pick_value.SetText(str(self.max_insert_count))
			ime.SetCursorPosition(-1)
			self.__OnValueUpdate()

	def __Load(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/picketcdialog.py")
		except:
			import exception
			exception.Abort("PickETCDialog.__Load.Load")

		try:
			self.board = self.GetChild("board_ui")
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))

			self.accept_button = self.GetChild("accept_button_ui")
			self.accept_button.SetEvent(ui.__mem_func__(self.Accept))

			self.close_button = self.GetChild("close_button_ui")
			self.close_button.SetEvent(ui.__mem_func__(self.Close))

			self.max_count_text = self.GetChild("max_count_ui")

			self.pick_value = self.GetChild("pick_value_ui")
			self.pick_value.SetReturnEvent(ui.__mem_func__(self.Accept))
			self.pick_value.SetEscapeEvent(ui.__mem_func__(self.Close))
			self.pick_value.OnIMEUpdate = ui.__mem_func__(self.__OnValueUpdate)
		except:
			import exception
			exception.Abort("PickETCDialog.__Load.Bind")

		self.width = self.GetWidth()
		self.height = self.GetHeight()

		self.max_count = 0

		self.event_accept = None

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.__Load()

	def Destroy(self):
		self.event_accept = None

		if self.pick_value.IsFocus():
			self.pick_value.KillFocus()

		self.pick_value.SetReturnEvent(None)
		self.pick_value.SetEscapeEvent(None)
		self.pick_value.OnIMEUpdate = None
		self.pick_value = None

		self.accept_button.SetEvent(None)
		self.accept_button = None

		self.close_button.SetEvent(None)
		self.close_button = None

		self.board.SetCloseEvent(None)
		self.board = None

		self.ClearDictionary()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

if app.USE_EXCHANGE_CURRENCY:
	class ExchangeCurrencyDialog(ui.ScriptWindow):
		def Open(self, num, max_count):
			if num == 0:
				self.board.SetTitleName(uiscriptlocale.CURRENCY_WON_BUY)
			elif num == 1:
				self.board.SetTitleName(uiscriptlocale.CURRENCY_WON_SELL)
			else:
				return False

			if max_count == 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.TOOLTIP_EXCHANGE_MULTIPLE_NOT_ENOUGH_YANG if num == 0 else localeinfo.TOOLTIP_EXCHANGE_MULTIPLE_NOT_ENOUGH_WON)
				return False

			(mouseX, mouseY) = wndMgr.GetMousePosition()

			if mouseX + self.width / 2 > wndMgr.GetScreenWidth():
				xPos = wndMgr.GetScreenWidth() - self.width
			elif mouseX - self.width / 2 < 0:
				xPos = 0
			else:
				xPos = mouseX - self.width / 2

			self.SetPosition(xPos, mouseY - self.height - 20)

			if localeinfo.IsARABIC():
				self.max_count_text.SetText("/{}".format(max_count))
			else:
				self.max_count_text.SetText(" / {}".format(max_count))

			self.max_count = max_count
			self.exchangeType = num

			self.pick_value.SetText("")

			self.pick_value.SetFocus()
			ime.SetCursorPosition(-1)

			self.SetTop()
			self.Show()
			return True

		def Close(self):
			if self.pick_value.IsFocus():
				self.pick_value.KillFocus()

			self.exchangeType = -1

			self.Hide()

		def Accept(self):
			count = self.GetCount()
			if count > 0 and self.event_accept:
				self.event_accept(self.exchangeType, count)

			self.Close()

		def SetAcceptEvent(self, event):
			self.event_accept = event

		def __OnValueUpdate(self):
			ui.EditLine.OnIMEUpdate(self.pick_value)

			text = self.pick_value.GetText()
			if len(text) == 0:
				return

			if text[0] == "0":
				self.pick_value.SetText("")
				ime.SetCursorPosition(-1)
				self.__OnValueUpdate()
				return

			if long(text) > self.max_count:
				self.pick_value.SetText(str(self.max_count))
				ime.SetCursorPosition(-1)
				self.__OnValueUpdate()

		def GetCount(self):
			text = self.pick_value.GetText()
			if len(text) > 0 and text.isdigit():
				return long(text)

			self.pick_value.SetText("0")
			self.pick_value.SetFocus()
			ime.SetCursorPosition(-1)
			return 0

		def __Load(self):
			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "uiscript/exchangecurrencydialog.py")
			except:
				import exception
				exception.Abort("ExchangeCurrencyDialog.__Load.Load")

			try:
				self.board = self.GetChild("board_ui")
				self.board.SetCloseEvent(ui.__mem_func__(self.Close))

				self.accept_button = self.GetChild("accept_button_ui")
				self.accept_button.SetEvent(ui.__mem_func__(self.Accept))

				self.close_button = self.GetChild("close_button_ui")
				self.close_button.SetEvent(ui.__mem_func__(self.Close))

				self.max_count_text = self.GetChild("max_count_ui")

				self.pick_value = self.GetChild("input_value_ui")
				self.pick_value.SetReturnEvent(ui.__mem_func__(self.Accept))
				self.pick_value.SetEscapeEvent(ui.__mem_func__(self.Close))
				self.pick_value.OnIMEUpdate = ui.__mem_func__(self.__OnValueUpdate)
			except:
				import exception
				exception.Abort("ExchangeCurrencyDialog.__Load.Bind")

			self.width = self.GetWidth()
			self.height = self.GetHeight()

			self.max_count = 0
			self.exchangeType = -1

			self.event_accept = None

		def __init__(self):
			ui.ScriptWindow.__init__(self)
			self.__Load()

		def Destroy(self):
			self.event_accept = None

			if self.pick_value.IsFocus():
				self.pick_value.KillFocus()

			self.pick_value.SetReturnEvent(None)
			self.pick_value.SetEscapeEvent(None)
			self.pick_value.OnIMEUpdate = None
			self.pick_value = None

			self.accept_button.SetEvent(None)
			self.accept_button = None

			self.close_button.SetEvent(None)
			self.close_button = None

			self.board.SetCloseEvent(None)
			self.board = None

			self.ClearDictionary()

		def __del__(self):
			ui.ScriptWindow.__del__(self)

class ItemTooltipButton(ui.Window):
	"""
	A reusable button that shows an item tooltip on hover.
	Can wrap ExpandedImageBoxButton for image-based buttons.
	Usage:
		btn = ItemTooltipButton()
		btn.Create(parent, x, y, upImg, overImg, downImg, itemVnum, description)
		btn.SetEvent(clickHandler)
	"""

	def __init__(self):
		ui.Window.__init__(self)
		self.tooltipItem = None
		self.itemVnum = 0
		self.button = None
		self.description = ""

	def __del__(self):
		ui.Window.__del__(self)

	def Create(self, parent, x, y, upImg, overImg, downImg, itemVnum, description=""):
		"""
		Create the button with item tooltip support.

		Args:
			parent: Parent window
			x, y: Position
			upImg, overImg, downImg: Button visual states (image paths)
			itemVnum: Item VNUM to show in tooltip
			description: Optional description text to show above item info
		"""
		self.SetParent(parent)
		self.SetPosition(x, y)

		# Create the button
		self.button = ui.ExpandedImageBoxButton()
		self.button.SetParent(self)
		self.button.SetPosition(0, 0)
		self.button.SetUpVisual(upImg)
		self.button.SetOverVisual(overImg)
		self.button.SetDownVisual(downImg)
		self.button.Show()

		# Set size based on button
		self.SetSize(self.button.GetWidth(), self.button.GetHeight())

		# Store item info
		self.itemVnum = itemVnum
		self.description = description

		# Create item tooltip
		self.tooltipItem = uitooltip.ItemToolTip()
		self.tooltipItem.HideToolTip()

		# Set hover events on button by directly setting eventDict (ImageBox-based classes)
		# This works because ExpandedImageBoxButton inherits from ImageBox which has eventDict/argDict
		self.button.eventDict["MOUSE_OVER_IN"] = ui.__mem_func__(self.__OnMouseOverIn)
		self.button.argDict["MOUSE_OVER_IN"] = ()
		self.button.eventDict["MOUSE_OVER_OUT"] = ui.__mem_func__(self.__OnMouseOverOut)
		self.button.argDict["MOUSE_OVER_OUT"] = ()

		self.Show()

	def SetEvent(self, func):
		"""Set click event for the button."""
		if self.button:
			# Use SetEvent for click handling (ExpandedImageBoxButton stores in clickEventFunc)
			self.button.SetEvent(func)

	def __OnMouseOverIn(self):
		if self.tooltipItem and self.itemVnum > 0:
			self.tooltipItem.ClearToolTip()
			if self.description:
				self.tooltipItem.AppendTextLine(self.description, self.tooltipItem.NORMAL_COLOR)
				self.tooltipItem.AppendSpace(5)
			self.tooltipItem.SetItemToolTip(self.itemVnum)

	def __OnMouseOverOut(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def SetItemVnum(self, vnum):
		"""Update the item VNUM for the tooltip."""
		self.itemVnum = vnum

	def SetDescription(self, desc):
		"""Update the description text shown above item info."""
		self.description = desc

	def GetButton(self):
		"""Get the underlying button widget."""
		return self.button

	def Destroy(self):
		"""Clean up resources."""
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()
			self.tooltipItem = None
		if self.button:
			self.button = None

class QuestionDialogGuildLvUp(ui.ScriptWindow):
	def __init__(self):
		self.tooltipItem = None

		ui.ScriptWindow.__init__(self)
		self.__CreateDialog()
		self.vnums = {}

	def Destroy(self):
		if self.tooltipItem:
			self.tooltipItem = None

		self.slotItem.SetOverInItemEvent(None)
		self.slotItem.SetOverOutItemEvent(None)
		self.slotItem = None

		self.vnums = {}

		self.acceptButton.SetEvent(None)
		self.acceptButton = None

		self.cancelButton.SetEvent(None)
		self.cancelButton = None

		self.board = None
		self.textLine = None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __CreateDialog(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/questiondialog.py")

		self.board = self.GetChild("board")
		self.textLine = self.GetChild("message")
		self.acceptButton = self.GetChild("accept")
		self.cancelButton = self.GetChild("cancel")
		
		#
		self.cancelButton.SAFE_SetEvent(self.Close)
		#

		self.slotItem = ui.GridSlotWindow()
		self.slotItem.SetParent(self)
		self.slotItem.SetPosition(125, 45)
		self.slotItem.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
		self.slotItem.ArrangeSlot(0, 3, 1, 32, 32, 0, 0)
		self.slotItem.RefreshSlot()
		self.slotItem.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
		
		self.slotItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		self.slotItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		self.slotItem.Show()
		
		width = self.GetWidth()
		height = self.GetHeight() + 22
		self.SetSize(width, height)
		self.board.SetSize(width, height)
		self.UpdateRect()
		
		self.textLine.SetPosition(0, 23)
		self.acceptButton.SetPosition(-65, 90)
		self.cancelButton.SetPosition(65, 90)

		self.RefreshItemSlot()

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def OverInItem(self, slotPos):
		if None != self.tooltipItem and self.vnums.has_key(slotPos):
			self.tooltipItem.SetItemToolTip(self.vnums[slotPos])

	def OverOutItem(self):
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def AddItemSlot(self, index, vnum, count):
		self.slotItem.SetItemSlot(index, vnum, count)
		
		self.vnums[index] = vnum

	def Show(self):
		self.SetCenterPosition()
		self.SetTop()
		ui.ScriptWindow.Show(self)

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.OverOutItem()
		self.Hide()

	def SetWidth(self, width):
		height = self.GetHeight()
		self.SetSize(width, height)
		self.board.SetSize(width, height)
		self.SetCenterPosition()
		self.UpdateRect()

	def SAFE_SetAcceptEvent(self, event):
		self.acceptButton.SAFE_SetEvent(event)

	def SAFE_SetCancelEvent(self, event):
		self.cancelButton.SAFE_SetEvent(event)

	def SetAcceptEvent(self, event):
		self.acceptButton.SetEvent(event)

	def SetCancelEvent(self, event):
		self.cancelButton.SetEvent(event)

	def SetText(self, text):
		self.textLine.SetText(text)

	def SetAcceptText(self, text):
		self.acceptButton.SetText(text)

	def SetCancelText(self, text):
		self.cancelButton.SetText(text)

	def OnPressEscapeKey(self):
		self.Close()
		return True
