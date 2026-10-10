# coding: latin_1

import app
import chr
import net
import player

import ui
import chat
import localeinfo
import time
import grpText
import ime
import messenger
if app.ENABLE_COMMUNITY_SYSTEM:
	import community
import uisystemoption
import osfinfo
import item
import grp
if app.USE_OFFLINESHOP:
	import offlineshop
	import uiofflineshop_ae
if app.ENABLE_WHISPER_RENEWAL:
	import whisper
	b_name = localeinfo.WHISPER_TYPING

import systemSetting

class WhisperButton(ui.Button):
	def __init__(self):
		ui.Button.__init__(self, "TOP_MOST")
		self.dismissEvent = None
		self.dismissHint = None
		self.rightPressed = False

	def __del__(self):
		ui.Button.__del__(self)

	def SetToolTipText(self, text, x = 0, y = 32):
		ui.Button.SetToolTipText(self, text, x, y)
		self.ToolTipText.Show()

	def SetToolTipTextWithColor(self, text, color, x = 0, y = 32):
		ui.Button.SetToolTipText(self, text, x, y)
		self.ToolTipText.SetPackedFontColor(color)
		self.ToolTipText.Show()

	def ShowToolTip(self):
		if 0 != self.ToolTipText:
			self.ToolTipText.Show()
		if self.dismissHint:
			self.dismissHint.Show()

	def HideToolTip(self):
		if 0 != self.ToolTipText:
			self.ToolTipText.Show()
		if self.dismissHint:
			self.dismissHint.Hide()

	def SetDismissEvent(self, event):
		# no stored args: an args tuple holding the button itself would form a
		# cycle with __del__ that py2 gc can never collect, keeping a destroyed
		# button alive and rendered
		self.dismissEvent = event
		if event and not self.dismissHint:
			hint = ui.TextLine()
			hint.SetParent(self)
			hint.SetPosition(self.GetWidth() / 2, 45)
			hint.SetHorizontalAlignCenter()
			hint.SetOutline()
			hint.SetPackedFontColor(0xffaaaaaa)
			hint.SetText(getattr(localeinfo, "WHISPERCHAT_DISMISS_HINT", "Right-click: close"))
			hint.Hide()
			self.dismissHint = hint

	def OnMouseRightButtonDown(self):
		if self.dismissEvent:
			self.rightPressed = True

	def OnMouseRightButtonUp(self):
		# fires only for a full press+release on the button, like CallEvent for
		# left clicks; True consumes the release while this button holds the
		# engine's right capture, preventing the point-window re-dispatch
		if not self.dismissEvent:
			return False
		pressed = self.rightPressed
		self.rightPressed = False
		if pressed and self.IsIn():
			self.dismissEvent(self)
		return True

class WhisperDialog(ui.ScriptWindow):
	class TextRenderer(ui.Window):
		def SetTargetName(self, targetName):
			self.targetName = targetName

		def OnRender(self):
			(x, y) = self.GetGlobalPosition()
			chat.RenderWhisper(self.targetName, x, y)

	class ResizeButton(ui.DragButton):
		def __init__(self):
			ui.DragButton.__init__(self)

		def __del__(self):
			ui.DragButton.__del__(self)

		def OnMouseOverIn(self):
			app.SetCursor(app.HVSIZE)

		def OnMouseOverOut(self):
			app.SetCursor(app.NORMAL)

	def __init__(self, eventMinimize, eventClose):
		# print "NEW WHISPER DIALOG ----------------------------------------------------------------------------"
		ui.ScriptWindow.__init__(self)
		
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.targetName = ""
		self.eventMinimize = eventMinimize
		self.eventClose = eventClose
		self.eventAcceptTarget = None
		self.countryID = 0

	def __del__(self):
		# print "---------------------------------------------------------------------------- DELETE WHISPER DIALOG"
		ui.ScriptWindow.__del__(self)

	def LoadDialog(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/WhisperDialog.py")
		except:
			import exception
			exception.Abort("WhisperDialog.LoadDialog.LoadScript")

		try:
			GetObject = self.GetChild
			self.titleName = GetObject("titlename")
			self.titleNameEdit = GetObject("titlename_edit")
			self.closeButton = GetObject("closebutton")
			self.scrollBar = GetObject("scrollbar")
			self.chatLine = GetObject("chatline")
			self.minimizeButton = GetObject("minimizebutton")
			self.ignoreButton = GetObject("ignorebutton")
			self.reportViolentWhisperButton = GetObject("reportviolentwhisperbutton")
			self.acceptButton = GetObject("acceptbutton")
			self.sendButton = GetObject("sendbutton")
			self.board = GetObject("board")
			self.editBar = GetObject("editbar")
			self.gamemasterMark = GetObject("gamemastermark")
			if app.ENABLE_WHISPER_RENEWAL:
				self.typing = GetObject("typing")
			if app.ENABLE_CHATTING_WINDOW_RENEWAL:
				self.addFriendButton = GetObject("AddFriendButton")
				self.blockFrindButton = GetObject("BlockFrindButton")
				self.searchShopButton = GetObject("SearchShopButton")
		except:
			import exception
			exception.Abort("DialogWindow.LoadDialog.BindObject")
		
		self.gamemasterMark.Hide()

		self.titleName.SetText("")
		self.titleNameEdit.SetText("")

		self.minimizeButton.SetEvent(ui.__mem_func__(self.Minimize))
		self.closeButton.SetEvent(ui.__mem_func__(self.Close))

		self.scrollBar.SetPos(1.0)
		self.scrollBar.SetScrollEvent(ui.__mem_func__(self.OnScroll))

		self.chatLine.SetReturnEvent(ui.__mem_func__(self.SendWhisper))
		self.chatLine.SetEscapeEvent(ui.__mem_func__(self.Minimize))
		self.chatLine.SetMultiLine()

		self.sendButton.SetEvent(ui.__mem_func__(self.SendWhisper))

		self.titleNameEdit.SetReturnEvent(ui.__mem_func__(self.AcceptTarget))
		self.titleNameEdit.SetEscapeEvent(ui.__mem_func__(self.Close))

		self.ignoreButton.SetToggleDownEvent(ui.__mem_func__(self.IgnoreTarget))
		self.ignoreButton.SetToggleUpEvent(ui.__mem_func__(self.IgnoreTarget))

		self.reportViolentWhisperButton.SetEvent(ui.__mem_func__(self.ReportViolentWhisper))

		self.acceptButton.SetEvent(ui.__mem_func__(self.AcceptTarget))

		if app.ENABLE_CHATTING_WINDOW_RENEWAL:
			self.addFriendButton.SetEvent(ui.__mem_func__(self.OnMessengerAddFriendButton))
			self.blockFrindButton.SetEvent(ui.__mem_func__(self.OnMessengerBlockButton))
			self.searchShopButton.SetEvent(ui.__mem_func__(self.OnSearchShopButton))

		self.textRenderer = self.TextRenderer()
		self.textRenderer.SetParent(self)
		self.textRenderer.SetPosition(20, 28)
		self.textRenderer.SetTargetName("")
		self.textRenderer.Show()
		
		self.resizeButton = self.ResizeButton()
		self.resizeButton.SetParent(self)
		self.resizeButton.SetSize(20, 20)
		self.resizeButton.SetPosition(280, 180)
		self.resizeButton.SetMoveEvent(ui.__mem_func__(self.ResizeWhisperDialog))
		self.resizeButton.Show()

		# self.countryFlag = ui.ExpandedImageBox()
		# self.countryFlag.SetParent(self.board)
		# self.countryFlag.SetPosition(130, 28)
		# self.countryFlag.Show()



		self.ResizeWhisperDialog()

	def Destroy(self):
		self.eventMinimize = None
		self.eventClose = None
		self.eventAcceptTarget = None

		self.ClearDictionary()

		self.titleName = None
		self.titleNameEdit = None
		self.closeButton = None
		self.scrollBar.Destroy()
		self.scrollBar = None
		self.chatLine = None
		self.minimizeButton = None
		self.ignoreButton = None
		self.reportViolentWhisperButton = None
		self.acceptButton = None
		self.sendButton = None
		self.board = None
		self.editBar = None
		self.gamemasterMark = None

		self.textRenderer = None
		self.resizeButton = None
		self.countryFlag = None
		self.countryID = 0

		if app.ENABLE_CHATTING_WINDOW_RENEWAL:
			self.addFriendButton = None
			self.blockFrindButton = None
			self.searchShopButton = None

	def ResizeWhisperDialog(self):
		(xPos, yPos) = self.resizeButton.GetLocalPosition()

		if xPos < 280:
			self.resizeButton.SetPosition(280, yPos)
			return

		if yPos < 150:
			self.resizeButton.SetPosition(xPos, 150)
			return

		self.SetWhisperDialogSize(xPos + 20, yPos + 20)

	def SetWhisperDialogSize(self, width, height):
		try:
			max = int((width - 90) / 6) * 3 - 6

			self.board.SetSize(width, height)
			self.scrollBar.SetPosition(width - 25, 35)
			self.scrollBar.SetScrollBarSize(height - 100)
			self.scrollBar.SetPos(1.0)
			self.editBar.SetSize(width - 18, 50)
			self.chatLine.SetSize(width - 90, 40)
			self.chatLine.SetLimitWidth(width - 90)
			self.SetSize(width, height)

			if 0 != self.targetName:
				chat.SetWhisperBoxSize(self.targetName, width - 50, height - 90)

			if localeinfo.IsARABIC():
				self.textRenderer.SetPosition(width - 20, 28)
				self.scrollBar.SetPosition(width - 25 + self.scrollBar.GetWidth(), 35)
				self.editBar.SetPosition(10 + self.editBar.GetWidth(), height - 60)
				self.sendButton.SetPosition(width - 80 + self.sendButton.GetWidth(), 10)
				self.minimizeButton.SetPosition(width-42 + self.minimizeButton.GetWidth(), 12)
				self.closeButton.SetPosition(width - 24 + self.closeButton.GetWidth(), 12)
				self.chatLine.SetPosition(5 + self.chatLine.GetWidth(), 5)
				self.board.SetPosition(self.board.GetWidth(), 0)
			else:
				self.textRenderer.SetPosition(20, 28)
				self.scrollBar.SetPosition(width - 25, 35)
				self.editBar.SetPosition(10, height - 60)
				self.sendButton.SetPosition(width - 80, 10)
				self.minimizeButton.SetPosition(width - 42, 12)
				self.closeButton.SetPosition(width - 24, 12)

			self.SetChatLineMax(max)

		except:
			import exception
			exception.Abort("WhisperDialog.SetWhisperDialogSize.BindObject")

	# def RequestCountryFlag(self, targetName):
		# if targetName:
			# net.SendWhisperDetails(targetName)

		# if self.countryFlag:
			# self.countryFlag.SetPosition(121, 13.5)

	# def SetCountryFlag(self, countryID):
		# self.countryID = countryID

		# if countryID != 0:
			# self.countryFlag.LoadImage("d:/ymir work/ui/game/flag/%s.tga" % uisystemoption.LOCALE_LANG_DICT[countryID]["locale"])
			# self.countryFlag.Show()
		# else:
			# self.countryFlag.Hide()

	def SetChatLineMax(self, max):
		if max > 230:
			max = 230
		
		self.chatLine.SetMax(max)
		
		from grpText import GetSplitingTextLine
		text = self.chatLine.GetText()
		if text:
			self.chatLine.SetText(GetSplitingTextLine(text, max, 0))

	def OpenWithTarget(self, targetName):
		chat.CreateWhisper(targetName)
		chat.SetWhisperBoxSize(targetName, self.GetWidth() - 60, self.GetHeight() - 90)

		self.chatLine.SetFocus()
		self.titleName.SetText(targetName)
		self.targetName = targetName
		self.textRenderer.SetTargetName(targetName)
		self.titleNameEdit.Hide()
		if app.ENABLE_WHISPER_RENEWAL:
			self.SetTimer()
			self.typing.SetText(b_name)
		self.ignoreButton.Hide()

		# self.RequestCountryFlag(targetName)
		# self.countryFlag.Hide()

		if app.IsDevStage():
			self.reportViolentWhisperButton.Show()
		else:
			self.reportViolentWhisperButton.Hide()

		self.acceptButton.Hide()
		self.gamemasterMark.Hide()
		self.minimizeButton.Show()
		#self.SearchShopButton.Show()
		if app.ENABLE_CHATTING_WINDOW_RENEWAL:
			self.RefreshMessengerButtons()
			self.searchShopButton.Show()

	def OpenWithoutTarget(self, event):
		self.eventAcceptTarget = event

		self.titleName.SetText("")

		self.titleNameEdit.SetText("")
		self.titleNameEdit.SetFocus()
		self.titleNameEdit.Show()

		self.targetName = 0

		self.ignoreButton.Hide()
		self.reportViolentWhisperButton.Hide()
		self.acceptButton.Show()
		self.minimizeButton.Hide()
		self.gamemasterMark.Hide()
		if app.ENABLE_WHISPER_RENEWAL:
			self.typing.Hide()
		# self.countryFlag.Hide()

		if app.ENABLE_CHATTING_WINDOW_RENEWAL:
			self.addFriendButton.Hide()
			self.blockFrindButton.Hide()
			self.searchShopButton.Hide()

	def SetGameMasterLook(self):
		self.gamemasterMark.Show()
		self.reportViolentWhisperButton.Hide()

	def Minimize(self):
		self.titleNameEdit.KillFocus()
		self.chatLine.KillFocus()
		self.Hide()

		if app.ENABLE_WHISPER_RENEWAL:
			if whisper.IsSended(self.targetName) and 0 != self.targetName:
				whisper.Remove(self.targetName)

		if None != self.eventMinimize:
			self.eventMinimize(self.targetName)

	def Close(self):
		chat.ClearWhisper(self.targetName)
		if app.ENABLE_WHISPER_RENEWAL:
			if self.targetName != 0:
				if whisper.IsSended(self.targetName) and self.targetName:
					whisper.Remove(self.targetName)
		self.titleNameEdit.KillFocus()
		self.chatLine.KillFocus()
		self.Hide()

		if None != self.eventClose:
			self.eventClose(self.targetName)

	def ReportViolentWhisper(self):
		net.SendChatPacket("/reportviolentwhisper " + self.targetName)

	def IgnoreTarget(self):
		net.SendChatPacket("/ignore " + self.targetName)

	def AcceptTarget(self):
		name = self.titleNameEdit.GetText()
		if len(name) <= 0:
			self.Close()
			return

		if None != self.eventAcceptTarget:
			self.titleNameEdit.KillFocus()
			self.eventAcceptTarget(name)

			# self.RequestCountryFlag(name)

			if app.ENABLE_CHATTING_WINDOW_RENEWAL:
				if name != player.GetName():
					self.addFriendButton.Show()
					self.blockFrindButton.Show()
					self.searchShopButton.Show()

	def OnScroll(self):
		chat.SetWhisperPosition(self.targetName, self.scrollBar.GetPos())

	if app.ENABLE_WHISPER_RENEWAL:
		def SetTimer(self):
			self.endTime = time.clock() + 0.4
		def OnUpdate(self):
			if 0 != self.targetName:
				if len(self.chatLine.GetText()) > 0 and not whisper.IsSended(self.targetName):
					whisper.Add(self.targetName)
				elif not len(self.chatLine.GetText()) > 0 and whisper.IsSended(self.targetName):
					whisper.Remove(self.targetName)
				if whisper.CheckName(self.targetName):
					self.typing.Show()
					lastTime = max(0, self.endTime - time.clock())
					if 0 == lastTime:
						if len(self.typing.GetText()) - len(b_name) < 3:
							self.typing.SetText(self.typing.GetText() + ".")
						else:
							self.typing.SetText(b_name)	
						self.SetTimer()
				else:
					self.typing.Hide()


	def OnRunMouseWheel(self, nLen):
		if nLen > 0:
			self.scrollBar.OnUp()
		else:
			self.scrollBar.OnDown()

	def SendWhisper(self):
		text = self.chatLine.GetText()
		textLength = len(text)
		conquerorLevel = player.GetStatus(player.POINT_CONQUEROR_LEVEL)
		if textLength > 0:
			if net.IsInsultIn(text):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHAT_INSULT_STRING)
				return

			if osfinfo.SHOW_EMOJI_IN_WHISPER_LINE == True:
				text = osfinfo.EmojiFilter(text)

			#net.SendWhisperPacket(self.targetName, text)
			if conquerorLevel > 0:
				net.SendWhisperPacket(self.targetName, "cLv." + str(conquerorLevel) + ": " + text)
			else:
				net.SendWhisperPacket(self.targetName, "Lv." + str(player.GetStatus(player.LEVEL)) + ": " + text)
			self.chatLine.SetText("")

			if localeinfo.IsARABIC():
				chat.AppendWhisper(chat.WHISPER_TYPE_CHAT, self.targetName, player.GetName() + " : " )
				chat.AppendWhisper(chat.WHISPER_TYPE_CHAT, self.targetName, text)
			else:
				chat.AppendWhisper(chat.WHISPER_TYPE_CHAT, self.targetName, player.GetName() + " : " + text)

	def OnTop(self):
		self.chatLine.SetFocus()

	def BindInterface(self, interface):
		self.interface = interface

	def OnMouseLeftButtonDown(self):
		hyperlink = ui.GetHyperlink()
		if hyperlink:
			if app.IsPressed(app.DIK_LALT):
				link = chat.GetLinkFromHyperlink(hyperlink)
				ime.PasteString(link)
			else:
				self.interface.MakeHyperlinkTooltip(hyperlink)

	def OnMouseRightButtonDown(self):
		# SHIFT+right-click on an item hyperlink opens the wiki on that item.
		# Hint shown inside the hover tooltip (HyperlinkItemToolTip).
		if app.ENABLE_INGAME_WIKI and app.IsPressed(app.DIK_LSHIFT):
			hyperlink = ui.GetHyperlink()
			if hyperlink:
				self.interface.OpenWikiFromHyperlink(hyperlink)

	if app.ENABLE_CHATTING_WINDOW_RENEWAL:
		def OnMessengerAddFriendButton(self):
			if self.targetName:
				if app.ENABLE_COMMUNITY_SYSTEM:
					net.SendCommunityRequestByName(self.targetName)
				else:
					net.SendMessengerAddByNamePacket(self.targetName)

		def OnMessengerBlockButton(self):
			if self.targetName:
				if app.ENABLE_COMMUNITY_SYSTEM:
					net.SendCommunityBlockAddByName(self.targetName)
				else:
					net.SendMessengerBlockAddByNamePacket(self.targetName)

		def RefreshMessengerButtons(self):
			if self.targetName:
				if app.ENABLE_COMMUNITY_SYSTEM:
					isFriend = community.IsFriendByName(self.targetName)
					isBlocked = community.IsBlockByName(self.targetName)
				else:
					isFriend = messenger.IsFriendByName(self.targetName)
					isBlocked = messenger.IsBlockFriendByName(self.targetName)

				if isFriend:
					self.addFriendButton.Disable()
				else:
					self.addFriendButton.Enable()

				if isBlocked:
					self.blockFrindButton.Disable()
				else:
					self.blockFrindButton.Enable()

		def OnSearchShopButton(self):
			if not self.targetName:
				return

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				wndShopOffline = interfaceHandler.wndShopOffline
				if wndShopOffline:
					wndSearchShop = wndShopOffline.wndSearchShop
					if wndSearchShop:
						wndSearchShop.SearchByOwnerName(self.targetName)
