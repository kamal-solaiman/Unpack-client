# coding: latin_1

import osfinfo

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import net
import player
import chr

import ui
import grp
import chat
import wndMgr
import ime
import localeinfo
import colorinfo
import constinfo
import systemSetting
import uiToolTip

if app.ENABLE_CHATTING_WINDOW_RENEWAL:
	import os
	import uicommon
	import uiscriptlocale
	import cPickle
	import player

from _weakref import proxy

ENABLE_CHAT_COMMAND = True
ENABLE_LAST_SENTENCE_STACK = True
ENABLE_INSULT_CHECK = False

if localeinfo.IsHONGKONG():
	ENABLE_LAST_SENTENCE_STACK = True

if localeinfo.IsEUROPE():
	ENABLE_CHAT_COMMAND = False

if localeinfo.IsCANADA():
	ENABLE_LAST_SENTENCE_STACK = False

chatInputSetList = []
def InsertChatInputSetWindow(wnd):
	global chatInputSetList
	chatInputSetList.append(wnd)
def RefreshChatMode():
	global chatInputSetList
	map(lambda wnd : wnd.OnRefreshChatMode(), chatInputSetList)
def DestroyChatInputSetWindow():
	global chatInputSetList
	chatInputSetList = []

if app.ENABLE_AUTO_SHOUT:
	g_autoShoutLastMessage = "" # Persistent message storage
	wndAutoShout = None # The single instance of our window

	def CreateAutoShoutWindow(send_shout_func):
		global wndAutoShout, g_autoShoutEnabled, g_autoShoutInterval, g_autoShoutLastMessage
		if not wndAutoShout:
			wndAutoShout = AutoShoutBoard(send_shout_func)
		else:
			try:
				wndAutoShout.set_send_func(send_shout_func, rebind=True)
			except AttributeError:
				wndAutoShout.send_shout_func = send_shout_func

		# Apply persistent state to the new/reused window
		try:
			wndAutoShout.SetStatus(g_autoShoutEnabled)
			if g_autoShoutLastMessage:
				wndAutoShout.SetNewShoutMessage(g_autoShoutLastMessage)
			wndAutoShout.autoShoutInterval = g_autoShoutInterval
			try:
				wndAutoShout.intervalComboBox.SelectItem(AUTOSHOUOT_AVAILABLE_INTERVALS.index(g_autoShoutInterval))
				wndAutoShout.intervalComboBox.SetCurrentItem(str(g_autoShoutInterval) + "s")
			except:
				pass
		except:
			pass
		return wndAutoShout
	
	
	# This function is called by the server command
	def UpdateAutoShoutStatus(status):
		global g_autoShoutEnabled
		g_autoShoutEnabled = int(status)
		if wndAutoShout:
			wndAutoShout.SetStatus(g_autoShoutEnabled)

	# This function is called by ChatWindow.OnUpdate
	def UpdateAutoShoutTimer():
		AutoShout_Tick()

	# This is called by the button in ChatWindow
	def ToggleAutoShoutWindow():
		if wndAutoShout:
			if wndAutoShout.IsShow():
				wndAutoShout.Close()
			else:
				wndAutoShout.Open()

if app.ENABLE_CHATTING_WINDOW_RENEWAL:
	CHECK_BOX_X_POS = 145-80
	def SortByName(button):
		return button.key

	def SortByData0(self, data):
		chat.AppendChat(chat.CHAT_TYPE_INFO, str(data))
		return data

	OPTION_CHECKBOX_TALKING = 1
	OPTION_CHECKBOX_PARTY = 2
	OPTION_CHECKBOX_GUILD = 3
	OPTION_CHECKBOX_SHOUT = 4
	OPTION_CHECKBOX_INFO = 5
	OPTION_CHECKBOX_NOTICE = 6
	OPTION_CHECKBOX_DICE = 7
	OPTION_CHECKBOX_EXP_INFO = 8
	OPTION_CHECKBOX_ITEM_INFO = 9
	OPTION_CHECKBOX_MONEY_INFO = 10
	OPTION_LANGUAGE_ONOFF = 11

	OPTION_CHECKBOX_FLAG_DE = 12
	OPTION_CHECKBOX_FLAG_ES = 13
	OPTION_CHECKBOX_FLAG_FR = 14
	OPTION_CHECKBOX_FLAG_EN = 15
	OPTION_CHECKBOX_FLAG_IT = 16
	OPTION_CHECKBOX_FLAG_PT = 17
	OPTION_CHECKBOX_FLAG_RO = 18
	OPTION_SET_NAME_TAB = 19

	OPTION_MAX = 20
	
	OPTION_CHECKBOX_MODE = {
		OPTION_CHECKBOX_TALKING : [[chat.CHAT_TYPE_TALKING], uiscriptlocale.CHATTING_SETTING_TALKING],
		OPTION_CHECKBOX_INFO : [[chat.CHAT_TYPE_INFO], uiscriptlocale.CHATTING_SETTING_SYSTEM],
		OPTION_CHECKBOX_NOTICE : [[chat.CHAT_TYPE_NOTICE,chat.CHAT_TYPE_BIG_NOTICE], uiscriptlocale.CHATTING_SETTING_NOTICE],
		OPTION_CHECKBOX_PARTY : [[chat.CHAT_TYPE_PARTY], uiscriptlocale.CHATTING_SETTING_PARTY],
		OPTION_CHECKBOX_GUILD : [[chat.CHAT_TYPE_GUILD], uiscriptlocale.CHATTING_SETTING_GUILD],
		OPTION_CHECKBOX_SHOUT : [[chat.CHAT_TYPE_SHOUT], uiscriptlocale.CHATTING_SETTING_SHOUT],
		OPTION_CHECKBOX_DICE : [[chat.CHAT_TYPE_DICE_INFO], uiscriptlocale.CHATTING_SETTING_DICE],
		OPTION_CHECKBOX_EXP_INFO : [[chat.CHAT_TYPE_EXP_INFO], uiscriptlocale.CHATTING_SETTING_EXP],
		OPTION_CHECKBOX_ITEM_INFO : [[chat.CHAT_TYPE_ITEM_INFO], uiscriptlocale.CHATTING_SETTING_ITEM],
		OPTION_CHECKBOX_MONEY_INFO : [[chat.CHAT_TYPE_MONEY_INFO], uiscriptlocale.CHATTING_SETTING_GOLD],
	}

	import os
	def CheckDirectory(directory):
		try:
			os.makedirs(directory)
		except:
			pass

	def CheckFile(directory):
		if os.path.exists(directory):
			return True
		return False

	def RemoveFile(directory):
		if os.path.exists(directory):
			os.remove(directory)

	cacheChat = {}

	def CreateEmptyList(index):
		list = [1] * OPTION_MAX
		list[0] = str(index)
		list[OPTION_LANGUAGE_ONOFF] = 0
		for langIndex in range(OPTION_CHECKBOX_FLAG_DE, OPTION_MAX):
			list[langIndex] = 0
		list[8] = 0#EXP off
		list[OPTION_SET_NAME_TAB] = str(index)
		return list

	CHAT_TAB_FILE_VERSION = "tabsv2"
	CHAT_TAB_ALL_NAME = getattr(uiscriptlocale, "CHATTING_TAB_ALL", "All")

	CHAT_TAB_DEFAULTS = (
		(0, "CHATTING_TAB_ALL", "All", None),
		(1, "CHATTING_TAB_GENERAL", "General", (OPTION_CHECKBOX_SHOUT,)),
		(2, "CHATTING_TAB_DROPS", "Drops", (OPTION_CHECKBOX_ITEM_INFO,)),
		(3, "CHATTING_TAB_GOLD", "Gold", (OPTION_CHECKBOX_MONEY_INFO,)),
		(4, "CHATTING_TAB_INFO", "Info", (OPTION_CHECKBOX_INFO,)),
	)

	def SaveChatData():
		global cacheChat
		if len(cacheChat) == 0:
			return

		MAIN_FILE = "UserData/chatting"
		PLAYER_FILE = MAIN_FILE+"/"+player.GetName()+".chat"

		try:
			file = open(PLAYER_FILE, "w+")
			file.write(CHAT_TAB_FILE_VERSION+"\n")
			for key, data in cacheChat.items():
				data = cacheChat[key]
				text = ""
				for x in xrange(OPTION_MAX):
					text+=str(data[x])+"#"
				file.write(text+"\n")
			file.close()
		except:
			pass

	def LoadChatNewEmpty(index):
		global cacheChat
		cacheChat[index] = CreateEmptyList(index)
		SaveChatData()

	def LoadChatEmpty():
		global cacheChat
		cacheChat = {}
		for index, localeKey, fallback, checks in CHAT_TAB_DEFAULTS:
			data = CreateEmptyList(index)
			data[OPTION_SET_NAME_TAB] = getattr(localeinfo, localeKey, fallback)
			if checks != None:
				for key in xrange(OPTION_CHECKBOX_TALKING, OPTION_CHECKBOX_MONEY_INFO+1):
					data[key] = 0
				for key in checks:
					data[key] = 1
			cacheChat[index] = data
		SaveChatData()

	def RemoveChat(index):
		global cacheChat
		if cacheChat.has_key(index):
			del cacheChat[index]
			SaveChatData()

	def LoadChatData():
		global cacheChat
		cacheChat = {}
		MAIN_FILE = "UserData/chatting"
		PLAYER_FILE = MAIN_FILE+"/"+player.GetName()+".chat"
		CheckDirectory(MAIN_FILE)
		if not CheckFile(PLAYER_FILE):
			LoadChatEmpty()
			return

		lines = open(PLAYER_FILE, "r").readlines()
		if len(lines) < 2 or lines[0].strip() != CHAT_TAB_FILE_VERSION:
			LoadChatEmpty()
			return

		for line in lines[1:]:
			lineSplit = line.split("#")

			if len(lineSplit) == 0 or OPTION_MAX != len(lineSplit)-1:
				LoadChatEmpty()
				return

			list = [1] * OPTION_MAX
			for j in xrange(len(lineSplit)-1):
				if j == 0:
					list[j] = str(lineSplit[j])
				elif j == OPTION_SET_NAME_TAB:
					list[j] = str(lineSplit[j])
				else:
					list[j] = int(lineSplit[j])

			cacheChat[int(lineSplit[0])] = list

		if len(cacheChat) == 0:
			LoadChatEmpty()

## ChatModeButton
class ChatModeButton(ui.Window):
	OUTLINE_COLOR = grp.GenerateColor(1.0, 1.0, 1.0, 1.0)
	OVER_COLOR = grp.GenerateColor(1.0, 1.0, 1.0, 0.3)
	BUTTON_STATE_UP = 0
	BUTTON_STATE_OVER = 1
	BUTTON_STATE_DOWN = 2

	def __init__(self):
		ui.Window.__init__(self)
		self.state = None
		self.buttonText = None
		self.event = None
		self.SetWindowName("ChatModeButton")

		net.EnableChatInsultFilter(ENABLE_INSULT_CHECK)

	def __del__(self):
		ui.Window.__del__(self)

	def SAFE_SetEvent(self, event):
		self.event=ui.__mem_func__(event)

	def SetText(self, text):
		if None == self.buttonText:
			textLine = ui.TextLine()
			textLine.SetParent(self)
			textLine.SetWindowHorizontalAlignCenter()
			textLine.SetWindowVerticalAlignCenter()
			textLine.SetVerticalAlignCenter()
			textLine.SetHorizontalAlignCenter()
			textLine.SetPackedFontColor(self.OUTLINE_COLOR)
			textLine.Show()
			self.buttonText = textLine

		self.buttonText.SetText(text)

	def SetSize(self, width, height):
		self.width = width
		self.height = height
		ui.Window.SetSize(self, width, height)

	def OnMouseOverIn(self):
		self.state = self.BUTTON_STATE_OVER

	def OnMouseOverOut(self):
		self.state = self.BUTTON_STATE_UP

	def OnMouseLeftButtonDown(self):
		self.state = self.BUTTON_STATE_DOWN

	def OnMouseLeftButtonUp(self):
		self.state = self.BUTTON_STATE_UP
		if self.IsIn():
			self.state = self.BUTTON_STATE_OVER

		if None != self.event:
			self.event()

	def OnRender(self):
		(x, y) = self.GetGlobalPosition()

		grp.SetColor(self.OUTLINE_COLOR)
		grp.RenderRoundBox(x, y, self.width, self.height)

		if self.state >= self.BUTTON_STATE_OVER:
			grp.RenderRoundBox(x + 1, y, self.width - 2, self.height)
			grp.RenderRoundBox(x, y + 1, self.width, self.height - 2)

			if self.BUTTON_STATE_DOWN == self.state:
				grp.SetColor(self.OVER_COLOR)
				grp.RenderBar(x + 1, y + 1, self.width - 2, self.height - 2)

## ChatLine
class ChatLine(ui.EditLine):
	CHAT_MODE_NAME = {
		chat.CHAT_TYPE_TALKING : localeinfo.CHAT_NORMAL,
		chat.CHAT_TYPE_PARTY : localeinfo.CHAT_PARTY,
		chat.CHAT_TYPE_GUILD : localeinfo.CHAT_GUILD,
		chat.CHAT_TYPE_SHOUT : localeinfo.CHAT_SHOUT,
		#@add
		chat.CHAT_TYPE_TEAM : localeinfo.CHAT_TEAM,
	}
	# if osfinfo.WHISPER_ON_CHAT_LINE:
		# CHAT_MODE_NAME.update({
			# chat.CHAT_TYPE_WHISPER : localeinfo.CHAT_WHISPER,
		# })

	def __init__(self):
		ui.EditLine.__init__(self)
		self.SetWindowName("Chat Line")
		self.lastShoutTime = 0
		self.eventEscape = lambda *arg : None
		self.eventReturn = lambda *arg : None
		self.eventTab = None
		self.chatMode = chat.CHAT_TYPE_TALKING
		self.bCodePage = True
		self.overTextLine = ui.TextLine()
		self.overTextLine.SetParent(self)
		self.overTextLine.SetPosition(-1, 0)
		self.overTextLine.SetFontColor(1.0, 1.0, 0.0)
		self.overTextLine.SetOutline()
		self.overTextLine.Hide()

		self.lastSentenceStack = []
		self.lastSentencePos = 0

	def __del__(self):
		ui.EditLine.__del__(self)

	def SetChatMode(self, mode):
		self.chatMode = mode

	def GetChatMode(self):
		return self.chatMode

	def ChangeChatMode(self):
		if chat.CHAT_TYPE_TALKING == self.GetChatMode():
			self.SetChatMode(chat.CHAT_TYPE_PARTY)
			self.SetText("#")
			self.SetEndPosition()

		elif chat.CHAT_TYPE_PARTY == self.GetChatMode():
			self.SetChatMode(chat.CHAT_TYPE_GUILD)
			self.SetText("%")
			self.SetEndPosition()

		elif chat.CHAT_TYPE_GUILD == self.GetChatMode():
			self.SetChatMode(chat.CHAT_TYPE_SHOUT)
			self.SetText("!")
			self.SetEndPosition()

		#elif chat.CHAT_TYPE_SHOUT == self.GetChatMode():
			#if osfinfo.WHISPER_ON_CHAT_LINE:
			#	self.SetChatMode(chat.CHAT_TYPE_WHISPER)
			#	self.SetText("@")
		#	else:
			#	self.SetChatMode(chat.CHAT_TYPE_TALKING)
			#	self.SetText("")

	#	elif chat.CHAT_TYPE_WHISPER == self.GetChatMode() and osfinfo.WHISPER_ON_CHAT_LINE:
		#	self.SetChatMode(chat.CHAT_TYPE_TALKING)
		#	self.SetText("")
		elif chat.CHAT_TYPE_SHOUT == self.GetChatMode():
			self.SetChatMode(chat.CHAT_TYPE_TEAM)
			self.SetText("&")
			
		elif chat.CHAT_TYPE_TEAM == self.GetChatMode():
			self.SetChatMode(chat.CHAT_TYPE_TALKING)
			self.SetText("")
		self.__CheckChatMark()

	def GetCurrentChatModeName(self):
		try:
			return self.CHAT_MODE_NAME[self.chatMode]
		except:
			import exception
			exception.Abort("ChatLine.GetCurrentChatModeName")

	def SAFE_SetEscapeEvent(self, event):
		self.eventReturn = ui.__mem_func__(event)

	def SAFE_SetReturnEvent(self, event):
		self.eventEscape = ui.__mem_func__(event)

	def SAFE_SetTabEvent(self, event):
		self.eventTab = ui.__mem_func__(event)

	def SetTabEvent(self, event):
		self.eventTab = event

	def OpenChat(self):
		self.SetFocus()
		self.__ResetChat()

	def __ClearChat(self):
		self.SetText("")
		constinfo.lastSentencePos = 0

	def __ResetChat(self):
		if chat.CHAT_TYPE_PARTY == self.GetChatMode():
			self.SetText("#")
			self.SetEndPosition()
		elif chat.CHAT_TYPE_GUILD == self.GetChatMode():
			self.SetText("%")
			self.SetEndPosition()
		elif chat.CHAT_TYPE_SHOUT == self.GetChatMode():
			self.SetText("!")
			self.SetEndPosition()
		#elif chat.CHAT_TYPE_WHISPER == self.GetChatMode() and osfinfo.WHISPER_ON_CHAT_LINE:
			#self.SetText("@")
		#	self.SetEndPosition()
		elif chat.CHAT_TYPE_TEAM == self.GetChatMode():
			self.SetText("&")
			self.SetEndPosition()
		else:
			self.__ClearChat()

		self.__CheckChatMark()

	def __SendChatPacket(self, text, type):
		# if text[0] == '/':
			# if ENABLE_CHAT_COMMAND or constinfo.CONSOLE_ENABLE:
				# pass
			# else:
				# return
		if text[0] == '/':
			if chr.IsGameMaster(player.GetMainCharacterIndex()):
				pass
			else:
				return
		if app.ENABLE_AUTO_SHOUT:
			if type == chat.CHAT_TYPE_SHOUT:
				global g_autoShoutLastMessage
				if not g_autoShoutEnabled:
					g_autoShoutLastMessage = text
					if wndAutoShout:
						wndAutoShout.SetNewShoutMessage(text)

		if net.IsChatInsultIn(text):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHAT_INSULT_STRING)
		else:
			if osfinfo.SHOW_EMOJI_IN_CHAT_LINE == True:
				if not osfinfo.IsHyperLinkFilter(text):
					text = osfinfo.EmojiFilter(text)


			net.SendChatPacket(text, type)

	if app.ENABLE_AUTO_SHOUT:
		def SendShout(self, text):
			self.__SendShoutChatPacket(text)

	def __SendPartyChatPacket(self, text):
		if 1 == len(text):
			self.RunCloseEvent()
			return

		self.__SendChatPacket(text[1:], chat.CHAT_TYPE_PARTY)
		self.__ResetChat()

	def __SendGuildChatPacket(self, text):
		if 1 == len(text):
			self.RunCloseEvent()
			return

		self.__SendChatPacket(text[1:], chat.CHAT_TYPE_GUILD)
		self.__ResetChat()

	def __SendShoutChatPacket(self, text):
		if 1 == len(text):
			self.RunCloseEvent()
			return

		# if app.GetTime() < self.lastShoutTime + 15:
			# chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHAT_SHOUT_LIMIT)
			# self.__ResetChat()
			# return

		self.__SendChatPacket(text[1:], chat.CHAT_TYPE_SHOUT)
		#if localeinfo.IsARABIC():
		#	self.__SendChatPacket(localeinfo.SHOUT_PM + "|cFF00ff92|Hvectors:" + str(player.GetName()) + text[1:], chat.CHAT_TYPE_SHOUT)
		#else:
		#	self.__SendChatPacket("|h|r[PM]|h : " + "|cFF00ff92|Hvectors:" +str(player.GetName()) + text[1:], chat.CHAT_TYPE_SHOUT)
		self.__ResetChat()

		self.lastShoutTime = app.GetTime()

	def __SendTeamChatPacket(self, text):
		if 1 == len(text):
			self.RunCloseEvent()
			return

		self.__SendChatPacket(text[1:], chat.CHAT_TYPE_TEAM)
		self.__ResetChat()

	def __SendTalkingChatPacket(self, text):
		self.__SendChatPacket(text, chat.CHAT_TYPE_TALKING)
		self.__ResetChat()

	def OnIMETab(self):
		# if None != self.eventTab:
			# self.eventTab()
		# return True
		return False

	def OnIMEUpdate(self):
		ui.EditLine.OnIMEUpdate(self)
		self.__CheckChatMark()

	def __CheckChatMark(self):
		self.overTextLine.Hide()

		text = self.GetText()
		if len(text) > 0:
			if '#' == text[0]:
				self.overTextLine.SetText("#")
				self.overTextLine.Show()
			elif '%' == text[0]:
				self.overTextLine.SetText("%")
				self.overTextLine.Show()
			elif '!' == text[0]:
				self.overTextLine.SetText("!")
				self.overTextLine.Show()
			#elif '@' == text[0] and osfinfo.WHISPER_ON_CHAT_LINE:
			#self.overTextLine.SetText("@")
			elif '&' == text[0]:
				self.overTextLine.SetText("&")
				self.overTextLine.Show()

	def OnIMEKeyDown(self, key):
		# LAST_SENTENCE_STACK
		if app.VK_UP == key:
			self.__PrevLastSentenceStack()
			return True

		if app.VK_DOWN == key:
			self.__NextLastSentenceStack()
			return True
		# END_OF_LAST_SENTENCE_STACK

		ui.EditLine.OnIMEKeyDown(self, key)

	# LAST_SENTENCE_STACK
	def __PrevLastSentenceStack(self):
		global ENABLE_LAST_SENTENCE_STACK
		if not ENABLE_LAST_SENTENCE_STACK:
			return
		
		if constinfo.lastSentenceStack and constinfo.lastSentencePos < len(constinfo.lastSentenceStack):
			constinfo.lastSentencePos += 1
			lastSentence = constinfo.lastSentenceStack[-constinfo.lastSentencePos]
			self.SetText(lastSentence)
			self.SetEndPosition()

	def __NextLastSentenceStack(self):
		global ENABLE_LAST_SENTENCE_STACK
		if not ENABLE_LAST_SENTENCE_STACK:
			return
		
		if constinfo.lastSentenceStack and constinfo.lastSentencePos > 1:
			constinfo.lastSentencePos -= 1
			lastSentence = constinfo.lastSentenceStack[-constinfo.lastSentencePos]
			self.SetText(lastSentence)
			self.SetEndPosition()

	def __PushLastSentenceStack(self, text):
		global ENABLE_LAST_SENTENCE_STACK
		if not ENABLE_LAST_SENTENCE_STACK:
			return
		
		if len(text) <= 0:
			return
		
		LAST_SENTENCE_STACK_SIZE = 32
		if len(constinfo.lastSentenceStack) > LAST_SENTENCE_STACK_SIZE:
			constinfo.lastSentenceStack.pop(0)
		
		constinfo.lastSentenceStack.append(text)
	# END_OF_LAST_SENTENCE_STACK

####################################################################################
	def IsNumberic(self, text):
		try:
			int(text)
			return True
		except ValueError:
			return False

	def CheckString(self, text, idx):
		textLen = len(text)
		n = text.find("@", idx)
		isResult = True
		for i in xrange(n + 1, n + 5):
			if i == textLen:
				return False

			if self.IsNumberic(text[i]) == False:
				isResult = False
				break
			else:
				continue

		return isResult

	def CheckWrongString(self, text):
		textLen = len(text)
		destList = []
		idx = 0

		while(idx < textLen):
			n = text.find("@", idx)

			if n == -1:
				break
			else:
				destList.append(n)
				idx = n + 1

		if len(destList) == 0:
			return False

		for i in destList:
			if self.CheckString(text, i) == True:
				return True
			else:
				continue

		return False
####################################################################################

	def OnIMEReturn(self):
		text = self.GetText()
		textLen=len(text)

		if self.CheckWrongString(text) == True:
			return False

		# LAST_SENTENCE_STACK
		self.__PushLastSentenceStack(text)
		# END_OF_LAST_SENTENCE_STACK

		textSpaceCount=text.count(' ')

		if (textLen > 0) and (textLen != textSpaceCount):
			if '#' == text[0]:
				self.__SendPartyChatPacket(text)
			elif '%' == text[0]:
				self.__SendGuildChatPacket(text)
			elif '!' == text[0]:
				self.__SendShoutChatPacket(text)
			elif '&' == text[0]:
				self.__SendTeamChatPacket(text)
			else:
				self.__SendTalkingChatPacket(text)
		else:
			self.__ClearChat()
			self.eventReturn()

		return True

	def OnPressEscapeKey(self):
		self.__ClearChat()
		self.eventEscape()
		return True

	def RunCloseEvent(self):
		self.eventEscape()

	def BindInterface(self, interface):
		self.interface = proxy(interface)

	def OnMouseLeftButtonDown(self):
		hyperlink = ui.GetHyperlink()
		if hyperlink:
			if app.IsPressed(app.DIK_LALT):
				link = chat.GetLinkFromHyperlink(hyperlink)
				ime.PasteString(link)
			else:
				self.interface.MakeHyperlinkTooltip(hyperlink)
		else:
			ui.EditLine.OnMouseLeftButtonDown(self)

	def OnMouseRightButtonDown(self):
		# SHIFT+right-click on an item hyperlink opens the wiki on that item.
		# Hint shown inside the hover tooltip (HyperlinkItemToolTip).
		if app.ENABLE_INGAME_WIKI and app.IsPressed(app.DIK_LSHIFT):
			hyperlink = ui.GetHyperlink()
			if hyperlink:
				self.interface.OpenWikiFromHyperlink(hyperlink)

class ChatInputSet(ui.Window):
	CHAT_OUTLINE_COLOR = grp.GenerateColor(1.0, 1.0, 1.0, 1.0)

	def __init__(self):
		ui.Window.__init__(self)
		self.SetWindowName("ChatInputSet")

		InsertChatInputSetWindow(self)
		self.__Create()


	def __del__(self):
		ui.Window.__del__(self)

	def __Create(self):
		chatModeButton = ChatModeButton()
		chatModeButton.SetParent(self)
		chatModeButton.SetSize(40, 17)
		chatModeButton.SetText(localeinfo.CHAT_NORMAL)
		chatModeButton.SetPosition(7, 2)
		chatModeButton.SAFE_SetEvent(self.OnChangeChatMode)
		self.chatModeButton = chatModeButton

		chatLine = ChatLine()
		chatLine.SetParent(self)

		if app.ENABLE_GROWTH_PET_SYSTEM:
			## When buffered in the server, 486 = 512-(CHARACTER_NAME_MAX_LEN + 3) + 1 size.
			## Data is cut off because it is set to 512.
			chatLine.SetMax(486)
		else:
			chatLine.SetMax(512)

		chatLine.SetUserMax(76)
		chatLine.SetText("")
		chatLine.SAFE_SetTabEvent(self.OnChangeChatMode)
		chatLine.x = 0
		chatLine.y = 0
		chatLine.width = 0
		chatLine.height = 0
		self.chatLine = chatLine

		btnSend = ui.Button()
		btnSend.SetParent(self)
		btnSend.SetUpVisual("d:/ymir work/ui/game/taskbar/Send_Chat_Button_01.sub")
		btnSend.SetOverVisual("d:/ymir work/ui/game/taskbar/Send_Chat_Button_02.sub")
		btnSend.SetDownVisual("d:/ymir work/ui/game/taskbar/Send_Chat_Button_03.sub")
		btnSend.SetToolTipText(localeinfo.CHAT_SEND_CHAT)
		btnSend.SAFE_SetEvent(self.chatLine.OnIMEReturn)
		self.btnSend = btnSend

	def Destroy(self):
		self.chatModeButton = None
		self.chatLine = None
		self.btnSend = None

	def Open(self):
		self.chatLine.Show()
		self.chatLine.SetPosition(57, 5)
		self.chatLine.SetFocus()
		self.chatLine.OpenChat()

		self.chatModeButton.SetPosition(7, 2)
		self.chatModeButton.Show()

		self.btnSend.Show()
		self.Show()

		self.RefreshPosition()
		return True

	def Close(self):
		self.chatLine.KillFocus()
		self.chatLine.Hide()
		self.chatModeButton.Hide()
		self.btnSend.Hide()
		self.Hide()
		return True

	def SetEscapeEvent(self, event):
		self.chatLine.SetEscapeEvent(event)

	def SetReturnEvent(self, event):
		self.chatLine.SetReturnEvent(event)

	def OnChangeChatMode(self):
		RefreshChatMode()

	def OnRefreshChatMode(self):
		self.chatLine.ChangeChatMode()
		self.chatModeButton.SetText(self.chatLine.GetCurrentChatModeName())

	def SetChatFocus(self):
		self.chatLine.SetFocus()

	def KillChatFocus(self):
		self.chatLine.KillFocus()

	def SetChatMax(self, max):
		self.chatLine.SetUserMax(max)

	def RefreshPosition(self):
		if localeinfo.IsARABIC():
			self.chatLine.SetSize(self.GetWidth() - 108, 18)
		else:
			self.chatLine.SetSize(self.GetWidth() - 108, 13)

		self.btnSend.SetPosition(self.GetWidth() - 35 - 5, 2)

		(self.chatLine.x, self.chatLine.y, self.chatLine.width, self.chatLine.height) = self.chatLine.GetRect()

	def BindInterface(self, interface):
		self.chatLine.BindInterface(interface)

	def OnRender(self):
		(x, y, width, height) = self.chatLine.GetRect()
		ui.RenderRoundBox(x - 4, y - 3, width + 7, height + 4, self.CHAT_OUTLINE_COLOR)

## ChatWindow

class ChatWindow(ui.Window):

	BOARD_START_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 0.0)
	BOARD_END_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 0.8)
	BOARD_MIDDLE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 0.5)
	CHAT_OUTLINE_COLOR = grp.GenerateColor(1.0, 1.0, 1.0, 1.0)

	EDIT_LINE_HEIGHT = 25
	if app.ENABLE_CHAT_SETTINGS:
		CHAT_WINDOW_WIDTH = 600
		EDIT_LINE_HIDE_HEIGHT = 20
		chatLoby = []
		ChatLog = {}
		chatIndex = 0
	else:
		CHAT_WINDOW_WIDTH = 600

	class ChatBackBoard(ui.Window):
		def __init__(self):
			ui.Window.__init__(self)

		def __del__(self):
			ui.Window.__del__(self)

	class ChatButton(ui.DragButton):
		def __init__(self):
			ui.DragButton.__init__(self)
			self.AddFlag("float")
			self.AddFlag("movable")
			self.AddFlag("restrict_x")
			self.topFlag = False
			self.SetWindowName("ChatWindow:ChatButton")

		def __del__(self):
			ui.DragButton.__del__(self)

		def SetOwner(self, owner):
			self.owner = proxy(owner)

		def OnMouseOverIn(self):
			app.SetCursor(app.VSIZE)

		def OnMouseOverOut(self):
			app.SetCursor(app.NORMAL)

		def OnTop(self):
			if True == self.topFlag:
				return

			self.topFlag = True
			self.owner.SetTop()
			self.topFlag = False

	def __init__(self):
		ui.Window.__init__(self)
		self.AddFlag("float")

		self.SetWindowName("ChatWindow")
		self.__RegisterChatColorDict()

		self.boardState = chat.BOARD_STATE_VIEW
		self.chatID = chat.CreateChatSet(chat.CHAT_SET_CHAT_WINDOW)
		chat.SetBoardState(self.chatID, chat.BOARD_STATE_VIEW)
		self.onChatStateChange = None

		if app.ENABLE_CHAT_SETTINGS:
			self.current_log = None
			self.chatLoby = []
			self.ChatLog = {}
			self.chatIndex = 0
		self.xBar = 0
		if app.ENABLE_VOICE_CHAT:
			self.interface = None
		if app.ENABLE_AUTO_SHOUT:
			self.wndAutoShout = None # Initialize to None first


		self.yBar = 0
		self.widthBar = 0
		self.heightBar = 0
		self.curHeightBar = 0
		self.visibleLineCount = 0
		self.scrollBarPos = 1.0
		self.scrollLock = False

		chatInputSet = ChatInputSet()
		chatInputSet.SetParent(self)
		chatInputSet.SetEscapeEvent(ui.__mem_func__(self.CloseChat))
		chatInputSet.SetReturnEvent(ui.__mem_func__(self.CloseChat))
		chatInputSet.SetSize(550, 25)
		self.chatInputSet = chatInputSet

		btnSendWhisper = ui.Button()
		btnSendWhisper.SetParent(self)
		btnSendWhisper.SetUpVisual("d:/ymir work/ui/game/taskbar/Send_Whisper_Button_01.sub")
		btnSendWhisper.SetOverVisual("d:/ymir work/ui/game/taskbar/Send_Whisper_Button_02.sub")
		btnSendWhisper.SetDownVisual("d:/ymir work/ui/game/taskbar/Send_Whisper_Button_03.sub")
		btnSendWhisper.SetToolTipText(localeinfo.CHAT_SEND_MEMO)
		btnSendWhisper.Hide()
		self.btnSendWhisper = btnSendWhisper

		if app.ENABLE_AUTO_SHOUT:
			autoChatButton = ui.Button()
			autoChatButton.SetParent(self)
			autoChatButton.SetUpVisual("d:/ymir work/ui/bot_0.tga")
			autoChatButton.SetOverVisual("d:/ymir work/ui/bot_1.tga")
			autoChatButton.SetDownVisual("d:/ymir work/ui/bot_2.tga")
			autoChatButton.SetToolTipText(localeinfo.AUTOSHOUT_TITLE_TOOLTIP, 0, -23)
			autoChatButton.SetEvent(ui.__mem_func__(self.ToggleAutoShoutWindow))
			autoChatButton.Hide()
			self.autoChatButton = autoChatButton

		btnChatLog = ui.Button()
		btnChatLog.SetParent(self)
		btnChatLog.SetUpVisual("d:/ymir work/ui/game/taskbar/Open_Chat_Log_Button_01.sub")
		btnChatLog.SetOverVisual("d:/ymir work/ui/game/taskbar/Open_Chat_Log_Button_02.sub")
		btnChatLog.SetDownVisual("d:/ymir work/ui/game/taskbar/Open_Chat_Log_Button_03.sub")
		btnChatLog.SetToolTipText(localeinfo.CHAT_LOG)
		btnChatLog.Hide()
		self.btnChatLog = btnChatLog

		btnChatSizing = self.ChatButton()
		btnChatSizing.SetOwner(self)
		btnChatSizing.SetMoveEvent(ui.__mem_func__(self.Refresh))
		btnChatSizing.Hide()
		self.btnChatSizing = btnChatSizing

		if app.ENABLE_VOICE_CHAT:
			voiceChatButton = ui.Button()
			voiceChatButton.SetParent(self.btnChatSizing)
			voiceChatButton.SetUpVisual("d:/ymir work/ui/voice_chat/btn_addtab01_default.tga")
			voiceChatButton.SetOverVisual("d:/ymir work/ui/voice_chat/btn_addtab01_over.tga")
			voiceChatButton.SetDownVisual("d:/ymir work/ui/voice_chat/btn_addtab01_down.tga")
			voiceChatButton.SAFE_SetEvent(self.__ToggleVoiceChat)
			voiceChatButton.SetToolTipText(localeinfo.CHAT_VOICE_CHAT)
			voiceChatButton.Hide()
			self.voiceChatButton = voiceChatButton

		if app.ENABLE_CHAT_SETTINGS:
			imgChatBarLeft = ui.ImageBox()
			imgChatBarLeft.SetParent(self.btnChatSizing)
			imgChatBarLeft.AddFlag("not_pick")
			imgChatBarLeft.LoadImage("d:/ymir work/ui/chat/chat_linebar_left.tga")
			imgChatBarLeft.Show()
			self.imgChatBarLeft = imgChatBarLeft

			imgChatBarRight = ui.ImageBox()
			imgChatBarRight.SetParent(self.btnChatSizing)
			imgChatBarRight.AddFlag("not_pick")
			imgChatBarRight.LoadImage("d:/ymir work/ui/chat/chat_linebar_right.tga")
			imgChatBarRight.Show()
			self.imgChatBarRight = imgChatBarRight

			imgChatBarMiddle = ui.ExpandedImageBox()
			imgChatBarMiddle.SetParent(self.btnChatSizing)
			imgChatBarMiddle.AddFlag("not_pick")
			imgChatBarMiddle.LoadImage("d:/ymir work/ui/chat/chatmenutab_line.tga")
			imgChatBarMiddle.Show()
			self.imgChatBarMiddle = imgChatBarMiddle

			# Settings
			btnChatLobyCreate = ui.Button()
			btnChatLobyCreate.SetParent(self.btnChatSizing)
			btnChatLobyCreate.SetUpVisual("d:/ymir work/ui/chat/btn_addtab01_default.tga")
			btnChatLobyCreate.SetOverVisual("d:/ymir work/ui/chat/btn_addtab01_over.tga")
			btnChatLobyCreate.SetDownVisual("d:/ymir work/ui/chat/btn_addtab01_down.tga")
			btnChatLobyCreate.SetToolTipText(localeinfo.CHATTING_SETTING_SETTING_NEW, 0, -23)
			btnChatLobyCreate.SetEvent(ui.__mem_func__(self.CreateLobyButton))
			btnChatLobyCreate.Show()
			self.btnChatLobyCreate = btnChatLobyCreate

			btnChatSettingOption = ui.Button()
			btnChatSettingOption.SetParent(self.btnChatSizing)
			btnChatSettingOption.SetUpVisual("d:/ymir work/ui/chat/btn_option01_default.tga")
			btnChatSettingOption.SetOverVisual("d:/ymir work/ui/chat/btn_option01_over.tga")
			btnChatSettingOption.SetDownVisual("d:/ymir work/ui/chat/btn_option01_down.tga")
			btnChatSettingOption.SetToolTipText(localeinfo.CHATTING_SETTING_SETTING, 0, -23)
			btnChatSettingOption.SetEvent(ui.__mem_func__(self.__SettingOptionWndOpen))
			btnChatSettingOption.Show()
			self.btnChatSettingOption = btnChatSettingOption

			btnChatFreeze = ui.ToggleButton()
			btnChatFreeze.SetParent(self.btnChatSizing)
			btnChatFreeze.SetUpVisual("d:/ymir work/ui/public/xsmall_button_01.sub")
			btnChatFreeze.SetOverVisual("d:/ymir work/ui/public/xsmall_button_02.sub")
			btnChatFreeze.SetDownVisual("d:/ymir work/ui/public/xsmall_button_03.sub")
			btnChatFreeze.SetText(getattr(localeinfo, "CHAT_LOG_STOP", "Stop"))
			btnChatFreeze.SetToolTipText(getattr(localeinfo, "CHAT_LOG_STOP", "Stop"), 0, -23)
			btnChatFreeze.SetToggleDownEvent(ui.__mem_func__(self.__ChatFreezeOn))
			btnChatFreeze.SetToggleUpEvent(ui.__mem_func__(self.__ChatFreezeOff))
			btnChatFreeze.Show()
			self.btnChatFreeze = btnChatFreeze

			self.wndChatSettingOption = ChatSettingWindow()

			self.LoadChatLoby(True)
		else:
			imgChatBarLeft = ui.ImageBox()
			imgChatBarLeft.SetParent(self.btnChatSizing)
			imgChatBarLeft.AddFlag("not_pick")
			imgChatBarLeft.LoadImage("d:/ymir work/ui/pattern/chat_bar_left.tga")
			imgChatBarLeft.Show()
			self.imgChatBarLeft = imgChatBarLeft

			imgChatBarRight = ui.ImageBox()
			imgChatBarRight.SetParent(self.btnChatSizing)
			imgChatBarRight.AddFlag("not_pick")
			imgChatBarRight.LoadImage("d:/ymir work/ui/pattern/chat_bar_right.tga")
			imgChatBarRight.Show()
			self.imgChatBarRight = imgChatBarRight

			imgChatBarMiddle = ui.ExpandedImageBox()
			imgChatBarMiddle.SetParent(self.btnChatSizing)
			imgChatBarMiddle.AddFlag("not_pick")
			imgChatBarMiddle.LoadImage("d:/ymir work/ui/pattern/chat_bar_middle.tga")
			imgChatBarMiddle.Show()
			self.imgChatBarMiddle = imgChatBarMiddle

		scrollBar = ui.ScrollBar()
		scrollBar.AddFlag("float")
		scrollBar.SetScrollEvent(ui.__mem_func__(self.OnScroll))
		self.scrollBar = scrollBar
		# if app.ENABLE_AUTO_SHOUT:
			# self.wndAutoShout = CreateAutoShoutWindow(self.chatInputSet.chatLine.SendShout)
		if app.ENABLE_AUTO_SHOUT:
			BindAutoShoutChatLine(self.chatInputSet.chatLine)


		self.Refresh()
		self.chatInputSet.RefreshPosition() # Position update is required to properly position at RTL

	def __del__(self):
		ui.Window.__del__(self)

	if app.ENABLE_AUTO_SHOUT:
		def SetInterface(self, interface):
			self.interface = proxy(interface)

	if app.ENABLE_AUTO_SHOUT:
		def UpdateLastShout(self, text):
			if self.wndAutoShout and not g_autoShoutEnabled:
				self.wndAutoShout.SetNewShoutMessage(text)

	def __RegisterChatColorDict(self):
		CHAT_COLOR_DICT = {
			chat.CHAT_TYPE_TALKING : colorinfo.CHAT_RGB_TALK,
			chat.CHAT_TYPE_INFO : colorinfo.CHAT_RGB_INFO,
			chat.CHAT_TYPE_NOTICE : colorinfo.CHAT_RGB_NOTICE,
			chat.CHAT_TYPE_PARTY : colorinfo.CHAT_RGB_PARTY,
			chat.CHAT_TYPE_GUILD : colorinfo.CHAT_RGB_GUILD,
			chat.CHAT_TYPE_COMMAND : colorinfo.CHAT_RGB_COMMAND,
			chat.CHAT_TYPE_SHOUT : colorinfo.CHAT_RGB_SHOUT,
			chat.CHAT_TYPE_TEAM : colorinfo.CHAT_RGB_TEAM,
			chat.CHAT_TYPE_WHISPER : colorinfo.CHAT_RGB_WHISPER,
		}
		if app.ENABLE_CHATTING_WINDOW_RENEWAL:
			CHAT_COLOR_DICT.update({
				chat.CHAT_TYPE_EXP_INFO : colorinfo.CHAT_RGB_INFO,
				chat.CHAT_TYPE_ITEM_INFO : colorinfo.CHAT_RGB_INFO,
				chat.CHAT_TYPE_MONEY_INFO : colorinfo.CHAT_RGB_INFO,
				chat.CHAT_TYPE_DICE_INFO : colorinfo.CHAT_RGB_DICE_INFO,
			})
		if app.NEW_DUNGEON_NOTICE:
			CHAT_COLOR_DICT.update({
				chat.CHAT_TYPE_DUNGEON : colorinfo.CHAT_RGB_DUNGEON,
			})


		for colorItem in CHAT_COLOR_DICT.items():
			type=colorItem[0]
			rgb=colorItem[1]
			chat.SetChatColor(type, rgb[0], rgb[1], rgb[2])

	def Destroy(self):
		self.chatInputSet.Destroy()
		self.chatInputSet = None

		if app.ENABLE_VOICE_CHAT:
			self.interface = None

		if app.ENABLE_VOICE_CHAT:
			self.voiceChatButton = None
		if app.ENABLE_AUTO_SHOUT:
			global wndAutoShout
			if self.wndAutoShout:
				self.wndAutoShout.Hide()
				self.wndAutoShout.Destroy()
				self.wndAutoShout = None
				wndAutoShout = None

		if app.ENABLE_CHAT_SETTINGS:
			self.EDIT_LINE_HIDE_HEIGHT = 0
			self.chatLoby = []
			self.btnChatLobyCreate = None
			self.btnChatSettingOption = None
			self.btnChatFreeze = None
			
			for key, data in self.ChatLog.items():
				data.Close(True)
				data.Destroy()

			if self.current_log:
				self.current_log.Close(True)
				self.current_log.Destroy()

			self.current_log = None

			self.ChatLog ={}
			if self.wndChatSettingOption:
				self.wndChatSettingOption.Hide()
				self.wndChatSettingOption.Destroy()
				self.wndChatSettingOption=None
			SaveChatData()

		self.btnSendWhisper = 0
		self.btnChatLog = 0
		self.btnChatSizing = 0

	################
	## Open & Close
	def OpenChat(self):
		self.SetSize(self.CHAT_WINDOW_WIDTH, 25)
		chat.SetBoardState(self.chatID, chat.BOARD_STATE_EDIT)
		self.boardState = chat.BOARD_STATE_EDIT

		(x, y, width, height) = self.GetRect()
		(btnX, btnY) = self.btnChatSizing.GetGlobalPosition()

		if localeinfo.IsARABIC():
			chat.SetPosition(self.chatID, x + width - 10, y)
		else:
			chat.SetPosition(self.chatID, x + 10, y)

		chat.SetHeight(self.chatID, y - btnY - self.EDIT_LINE_HEIGHT + 100)

		if self.IsShow():
			self.btnChatSizing.Show()

		self.Refresh()
		self.btnSendWhisper.SetPosition(self.GetWidth() - 50 - 12 - 5, 2)
		self.btnSendWhisper.Show()

		self.btnChatLog.SetPosition(self.GetWidth() - 25 - 15 - 5, 2)
		self.btnChatLog.Show()
		
		if app.ENABLE_AUTO_SHOUT:
			self.autoChatButton.SetPosition(self.GetWidth() - 23, 2)
			self.autoChatButton.Show()

		if app.ENABLE_VOICE_CHAT:
			self.voiceChatButton.Show()

		self.chatInputSet.Open()
		self.chatInputSet.SetTop()
		self.SetTop()

		if self.onChatStateChange:
			(btnX, btnY) = self.btnChatSizing.GetGlobalPosition()
			self.onChatStateChange(True, btnY)

	def CloseChat(self):
		if app.ENABLE_CHAT_SETTINGS and getattr(self, "btnChatFreeze", None):
			self.btnChatFreeze.SetUp()
			chat.SetFreeze(self.chatID, 0)
		chat.SetBoardState(self.chatID, chat.BOARD_STATE_VIEW)
		self.boardState = chat.BOARD_STATE_VIEW

		if self.onChatStateChange:
			self.onChatStateChange(False, 0)

		(x, y, width, height) = self.GetRect()

		if localeinfo.IsARABIC():
			chat.SetPosition(self.chatID, x + width - 10, y + self.EDIT_LINE_HEIGHT)
		else:
			chat.SetPosition(self.chatID, x + 10, y + self.EDIT_LINE_HEIGHT)

		self.SetSize(self.CHAT_WINDOW_WIDTH, 0)

		self.chatInputSet.Close()
		self.btnSendWhisper.Hide()
		self.btnChatLog.Hide()
		self.btnChatSizing.Hide()
		if app.ENABLE_VOICE_CHAT:
			self.voiceChatButton.Hide()
		if app.ENABLE_AUTO_SHOUT:
			self.autoChatButton.Hide()

		self.Refresh()


	def SetSendWhisperEvent(self, event):
		self.btnSendWhisper.SetEvent(event)

	if app.ENABLE_CHAT_SETTINGS:
		def __ClickRadioButton(self, buttonList, buttonIndex):
			try:
				selButton = buttonList[buttonIndex]
			except IndexError:
				return
			for eachButton in buttonList:
				eachButton.SetUp()
			selButton.Down()

		def SelectLobyButtonWithKey(self, index = 0):
			for eachButton in self.chatLoby:
				if eachButton.key == index:
					self.SelectLobyButton(self.chatLoby.index(eachButton), index, True)
					return

		def SelectLobyButton(self, buttonIndex = 0, index = 0, isNotFast = False):
			self.wndChatSettingOption.CheckCacheDict(index)

			if app.IsPressed(app.DIK_LCONTROL) and isNotFast == False:
				pass
			else:
				self.__ClickRadioButton(self.chatLoby,buttonIndex)
				if index == self.chatIndex:
					return
				self.chatIndex = index
				self.UpdateChat()
				if getattr(self, "btnChatFreeze", None):
					self.btnChatFreeze.SetUp()
					chat.SetFreeze(self.chatID, 0)

		def CreateLobyButton(self, idx = -1, name = ""):
			if idx != -1 and self.GetKeyList(idx):
				return

			if len(self.chatLoby) == 10:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHATTING_SETTING_ADD_MAX)
				return

			kCheck = {}
			for key, data in cacheChat.items():
				number = int(data[0])

				kCheck[number] = True

			emptyLine = -1
			for key in xrange(1, 10):
				if kCheck.has_key(key) or (self.ChatLog.has_key(key) and self.ChatLog[key].IsShow()):
					continue

				emptyLine = key
				break

			if idx != -1:
				emptyLine = idx

			if emptyLine != -1:
				LoadChatNewEmpty(emptyLine)

			if name:
				cacheChat[emptyLine][OPTION_SET_NAME_TAB] = name

			self.LoadChatLoby()

		def GetKeyList(self, key):
			for btn in self.chatLoby:
				if btn.key == key:
					return True

			return False

		def __ChatFreezeOn(self):
			chat.SetFreeze(self.chatID, 1)

		def __ChatFreezeOff(self):
			chat.SetFreeze(self.chatID, 0)

		def __SettingOptionWndOpen(self):
			if self.wndChatSettingOption:
				self.wndChatSettingOption.Open(self.chatIndex)

		def UpdateChat(self):
			if self.wndChatSettingOption == None:
				return

			#import dbg
			#dbg.TraceError("{}".format(1))

			CHAT_MODE_INDEX = [ chat.CHAT_TYPE_TALKING,chat.CHAT_TYPE_PARTY,chat.CHAT_TYPE_GUILD,chat.CHAT_TYPE_SHOUT,chat.CHAT_TYPE_INFO,chat.CHAT_TYPE_NOTICE, chat.CHAT_TYPE_BIG_NOTICE, chat.CHAT_TYPE_DICE_INFO]
			if app.ENABLE_CHAT_SETTINGS_EXTEND:
				CHAT_MODE_INDEX.append(chat.CHAT_TYPE_EXP_INFO)
				CHAT_MODE_INDEX.append(chat.CHAT_TYPE_ITEM_INFO)
				CHAT_MODE_INDEX.append(chat.CHAT_TYPE_MONEY_INFO)

			for i in CHAT_MODE_INDEX:
				chat.DisableChatMode(self.chatID, i)

			if self.wndChatSettingOption.cacheDict.has_key(self.chatIndex):
				dataChat = self.wndChatSettingOption.cacheDict[self.chatIndex]

				for key, data in OPTION_CHECKBOX_MODE.items():
					if dataChat[key] > 0:
						for chatIndex in data[0]:
							chat.EnableChatMode(self.chatID, chatIndex)

				# if app.ENABLE_MULTI_LANGUAGE_SYSTEM_NOTUSED:
					# for j in range(1,10):
						# chat.DisableCountryMode(self.chatID, j)

				# if app.ENABLE_MULTI_LANGUAGE_SYSTEM_NOTUSED:
					# if dataChat[OPTION_LANGUAGE_ONOFF] == 1:
						# for country in range(OPTION_CHECKBOX_FLAG_DE, OPTION_MAX):
							# if dataChat[country] > 0:
								# chat.EnableCountryMode(self.chatID, dataChat[country])
					# else:
						# for j in range(1,10):
							# chat.EnableCountryMode(self.chatID, j)

		def RemoveAllLoby(self):
			self.chatLoby = []

		def RemoveChat(self, chatIndex):
			if self.wndChatSettingOption.cacheDict.has_key(chatIndex):
				del self.wndChatSettingOption.cacheDict[chatIndex]
			RemoveChat(chatIndex)
			self.LoadChatLoby()

			#chat.AppendChat(chat.CHAT_TYPE_INFO, str(chatIndex))

		def GetKeyByID(self, id):
			for key, data in cacheChat.items():
				if data[0] == id:
					return key

			return 0

		def LoadChatLoby(self, isFirst = False):
			if isFirst:
				LoadChatData()
			self.RemoveAllLoby()

			indexForX = 0

			# sort
			newList = []
			for key, data in cacheChat.items():
				newList.append(int(data[0]))

			newList.sort(reverse = False)

			for key, dataf in enumerate(newList):
				data = str(dataf)

				btnChatTab = ui.ToggleButton()
				btnChatTab.SetParent(self.btnChatSizing)
				btnChatTab.SetUpVisual("d:/ymir work/ui/chat/chatmenutab_default.tga")
				btnChatTab.SetOverVisual("d:/ymir work/ui/chat/chatmenutab_default.tga")
				btnChatTab.SetDownVisual("d:/ymir work/ui/chat/chatmenutab_down.tga")
				if data == "0":
					btnChatTab.SetToolTipText(CHAT_TAB_ALL_NAME, 0, -23)
					btnChatTab.SetTextAddPos(CHAT_TAB_ALL_NAME, -2)
				else:
					tabList = cacheChat[int(data)]
					btnChatTab.SetToolTipText(str(tabList[OPTION_SET_NAME_TAB]), 0, -23)
					btnChatTab.SetTextAddPos(str(tabList[OPTION_SET_NAME_TAB]), -2)
				btnChatTab.SetPosition(4+(indexForX*54), 0)
				btnChatTab.SetToggleUpEvent(self.SelectLobyButton, indexForX, self.GetKeyByID(data))
				btnChatTab.SetToggleDownEvent(self.SelectLobyButton, indexForX, self.GetKeyByID(data))
				btnChatTab.OnMouseRightButtonDown = lambda arg=self.GetKeyByID(data): self.OnLogChat(arg)
				btnChatTab.Show()
				btnChatTab.key = self.GetKeyByID(data)
				self.chatLoby.append(btnChatTab)

				indexForX+=1

			self.SortButtons()
			if isFirst:
				self.SelectLobyButton(0,0)
			else:
				self.SelectLobyButtonWithKey(self.chatIndex)
				if self.wndChatSettingOption.IsShow():
					self.wndChatSettingOption.Open(self.chatIndex)

			self.__RefreshSizingBar()
			if self.wndChatSettingOption:
				if isFirst:
					self.wndChatSettingOption.CheckCacheDict(0)

				self.UpdateChat()

		def SortButtons(self):
			cacheList = self.chatLoby
			cacheList.sort(reverse = False, key = SortByName)

			for indexForX, button in enumerate(cacheList):
				button.SetPosition(4+(indexForX*54), 0)
				button.SetToggleUpEvent(self.SelectLobyButton, indexForX, button.key)
				button.SetToggleDownEvent(self.SelectLobyButton, indexForX, button.key)

		def OnLogChat(self, index):
			if not self.ChatLog.has_key(index):
				newLog = ChatLogWindowNew()
				newLog.Open(index)
				self.ChatLog[index] = newLog
			else:
				self.ChatLog[index].Open(index)

			if index != 0:
				RemoveChat(index)

				if index == self.chatIndex:
					self.RemoveChat(index)
					self.chatIndex = 0
					self.__ClickRadioButton(self.chatLoby,0)
				else:
					RemoveChat(index)

				self.LoadChatLoby()
			else:
				self.chatLoby[0].Down()

			self.UpdateChat()

	def SetOpenChatLogEvent(self, event):
		self.btnChatLog.SetEvent(event)

	def SetChatStateChangeEvent(self, event):
		self.onChatStateChange = event

	def IsEditMode(self):
		if chat.BOARD_STATE_EDIT == self.boardState:
			return True

		return False

	def __RefreshSizingBar(self):
		(x, y, width, height) = self.GetRect()
		gxChat, gyChat = self.btnChatSizing.GetGlobalPosition()
		self.btnChatSizing.SetPosition(x, gyChat)
		self.btnChatSizing.SetSize(width, 22)
		if app.ENABLE_VOICE_CHAT:
			self.voiceChatButton.SetPosition(width - 57 - 12, 3)

			
		if app.ENABLE_CHAT_SETTINGS:
			self.imgChatBarLeft.SetPosition(0, 17)
			self.imgChatBarRight.SetPosition(width - 57, 0)

			# Settings
			self.btnChatSettingOption.SetPosition(width - 30 - -2, 3)
			self.btnChatLobyCreate.SetPosition(width - 30 - 20, 3)
			if getattr(self, "btnChatFreeze", None):
				self.btnChatFreeze.SetPosition(width - 30 - 20 - 48, 3)

			xEx = len(self.chatLoby)*54.4
			self.imgChatBarMiddle.SetPosition(57.0, 0)
			self.imgChatBarMiddle.SetRenderingRect(0.0, 0.0, float(width - 57.0 * 2) / 57.0 - 1.0, 0.0)
		else:
			self.imgChatBarLeft.SetPosition(0, 0)
			self.imgChatBarRight.SetPosition(width - 64, 0)
			self.imgChatBarMiddle.SetPosition(64, 0)
			self.imgChatBarMiddle.SetRenderingRect(0.0, 0.0, float(width - 128) / 64.0 - 1.0, 0.0)

	def SetPosition(self, x, y):
		ui.Window.SetPosition(self, x, y)
		self.__RefreshSizingBar()

	def SetSize(self, width, height):
		ui.Window.SetSize(self, width, height)
		self.__RefreshSizingBar()

	def SetHeight(self, height):
		gxChat, gyChat = self.btnChatSizing.GetGlobalPosition()
		self.btnChatSizing.SetPosition(gxChat, wndMgr.GetScreenHeight() - height)
		if app.ENABLE_WINDOW_RESIZE:
			self.btnChatSizing.SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 - self.CHAT_WINDOW_WIDTH/2, Expr("SCREEN_HEIGHT") - height)})

	###########
	## Refresh
	def Refresh(self):
		if self.boardState == chat.BOARD_STATE_EDIT:
			self.RefreshBoardEditState()
		elif self.boardState == chat.BOARD_STATE_VIEW:
			self.RefreshBoardViewState()

	def RefreshBoardEditState(self):
		(x, y, width, height) = self.GetRect()
		(btnX, btnY) = self.btnChatSizing.GetGlobalPosition()

		self.xBar = x
		self.yBar = btnY
		self.widthBar = width
		self.heightBar = y - btnY + self.EDIT_LINE_HEIGHT
		self.curHeightBar = self.heightBar

		if localeinfo.IsARABIC():
			chat.SetPosition(self.chatID, x + width - 10, y)
		else:
			chat.SetPosition(self.chatID, x + 10, y)

		chat.SetHeight(self.chatID, y - btnY - self.EDIT_LINE_HEIGHT)
		chat.ArrangeShowingChat(self.chatID)

		if btnY > y:
			self.btnChatSizing.SetPosition(btnX, y)
			self.heightBar = self.EDIT_LINE_HEIGHT

	def RefreshBoardViewState(self):
		(x, y, width, height) = self.GetRect()
		(btnX, btnY) = self.btnChatSizing.GetGlobalPosition()
		textAreaHeight = self.visibleLineCount * chat.GetLineStep(self.chatID)

		if localeinfo.IsARABIC():
			chat.SetPosition(self.chatID, x + width - 10, y + self.EDIT_LINE_HEIGHT)
		else:
			chat.SetPosition(self.chatID, x + 10, y + self.EDIT_LINE_HEIGHT)

		chat.SetHeight(self.chatID, y - btnY - self.EDIT_LINE_HEIGHT + 100)

		if self.boardState == chat.BOARD_STATE_EDIT:
			textAreaHeight += 45
		elif self.visibleLineCount != 0:
			textAreaHeight += 10 + 10

		self.xBar = x
		self.yBar = y + self.EDIT_LINE_HEIGHT - textAreaHeight
		self.widthBar = width
		self.heightBar = textAreaHeight

		self.scrollBar.Hide()

	##########
	## Render
	def OnUpdate(self):
		# per-frame UpdateChat rebuilt the showing list 10-20x/frame; every settings handler already invokes it on change (docs/CHAT_WINDOW_RENEWAL_AUDIT_2026-08-03.md)
		#if app.ENABLE_CHAT_SETTINGS:
		#	if self.wndChatSettingOption:
		#		self.UpdateChat()
		if self.boardState == chat.BOARD_STATE_EDIT:
			chat.Update(self.chatID)
		elif self.boardState == chat.BOARD_STATE_VIEW:
			if systemSetting.IsViewChat():
				chat.Update(self.chatID)

		if app.ENABLE_AUTO_SHOUT:
			UpdateAutoShoutTimer()

	def OnRender(self):
		if chat.GetVisibleLineCount(self.chatID) != self.visibleLineCount:
			self.visibleLineCount = chat.GetVisibleLineCount(self.chatID)
			self.Refresh()

		if self.curHeightBar != self.heightBar:
			self.curHeightBar += (self.heightBar - self.curHeightBar) / 10

		if self.boardState == chat.BOARD_STATE_EDIT:
			grp.SetColor(self.BOARD_MIDDLE_COLOR)
			if app.ENABLE_CHAT_SETTINGS:
				grp.RenderBar(self.xBar, self.yBar + (self.heightBar - self.curHeightBar) + self.EDIT_LINE_HIDE_HEIGHT, self.widthBar, self.curHeightBar)
			else:
				grp.RenderBar(self.xBar, self.yBar + (self.heightBar - self.curHeightBar) + 10, self.widthBar, self.curHeightBar)
			chat.Render(self.chatID)
		elif self.boardState == chat.BOARD_STATE_VIEW:
			if systemSetting.IsViewChat():
				grp.RenderGradationBar(self.xBar, self.yBar + (self.heightBar - self.curHeightBar), self.widthBar, self.curHeightBar, self.BOARD_START_COLOR, self.BOARD_END_COLOR)
				chat.Render(self.chatID)

	##########
	## Event
	def OnTop(self):
		self.btnChatSizing.SetTop()
		self.scrollBar.SetTop()

	def OnScroll(self):
		if not self.scrollLock:
			self.scrollBarPos = self.scrollBar.GetPos()

		lineCount = chat.GetLineCount(self.chatID)
		visibleLineCount = chat.GetVisibleLineCount(self.chatID)
		endLine = visibleLineCount + int(float(lineCount - visibleLineCount) * self.scrollBarPos)

		chat.SetEndPos(self.chatID, self.scrollBarPos)

	def OnChangeChatMode(self):
		self.chatInputSet.OnChangeChatMode()

	def SetChatFocus(self):
		self.chatInputSet.SetChatFocus()

	if app.ENABLE_AUTO_SHOUT:
		def SendChat(self, text, type):
			self.__SendChatPacket(text, type)

		def ToggleAutoShoutWindow(self):
			global wndAutoShout
			# ensure instance exists (after teleport it might have been destroyed)
			if not getattr(self, "wndAutoShout", None) or wndAutoShout is None:
				self.wndAutoShout = CreateAutoShoutWindow(self.chatInputSet.chatLine.SendShout)
			# open/close
			if self.wndAutoShout.IsShow():
				self.wndAutoShout.Close()
			else:
				self.wndAutoShout.Open()

	if app.ENABLE_VOICE_CHAT:
		def __ToggleVoiceChat(self):
			if self.interface:
				self.interface.ToggleVoiceChatConfigWindow()

	def BindInterface(self, interface):
		if interface:

			if app.ENABLE_VOICE_CHAT:
				self.interface = proxy(interface)

			self.chatInputSet.BindInterface(interface)

	def hide_btnChatSizing(self):
		if self.btnChatSizing:
			if self.IsShow():
				self.btnChatSizing.Hide()

	def show_btnChatSizing(self):
		if self.btnChatSizing:
			if self.btnChatLog.IsShow():
				self.btnChatSizing.Show()

## ChatLogWindow
class ChatLogWindow(ui.Window):
	BLOCK_WIDTH = 32

	CHAT_MODE_NAME = (
		localeinfo.CHAT_NORMAL,
		localeinfo.CHAT_PARTY,
		localeinfo.CHAT_GUILD,
		localeinfo.CHAT_SHOUT,
		localeinfo.CHAT_INFORMATION,
		localeinfo.CHAT_NOTICE,
		localeinfo.CHAT_DICE_INFO
	)

	CHAT_MODE_INDEX = (
		chat.CHAT_TYPE_TALKING,
		chat.CHAT_TYPE_PARTY,
		chat.CHAT_TYPE_GUILD,
		chat.CHAT_TYPE_SHOUT,
		chat.CHAT_TYPE_INFO,
		chat.CHAT_TYPE_NOTICE,
		chat.CHAT_TYPE_DICE_INFO
	)

	CHAT_LOG_WINDOW_MINIMUM_WIDTH = 450
	CHAT_LOG_WINDOW_MINIMUM_HEIGHT = 120

	class ResizeButton(ui.DragButton):
		def __init__(self):
			ui.DragButton.__init__(self)

		def __del__(self):
			ui.DragButton.__del__(self)

		def OnMouseOverIn(self):
			app.SetCursor(app.HVSIZE)

		def OnMouseOverOut(self):
			app.SetCursor(app.NORMAL)

	def __init__(self):
		self.allChatMode = True
		self.chatInputSet = None

		ui.Window.__init__(self)
		self.AddFlag("float")
		self.AddFlag("movable")
		self.SetWindowName("ChatLogWindow")
		self.__CreateChatInputSet()
		self.__CreateWindow()
		self.__CreateButton()
		self.__CreateScrollBar()

		self.chatID = chat.CreateChatSet(chat.CHAT_SET_LOG_WINDOW)
		chat.SetBoardState(self.chatID, chat.BOARD_STATE_LOG)
		for i in self.CHAT_MODE_INDEX:
			chat.EnableChatMode(self.chatID, i)

		self.SetPosition(20, 20)
		self.SetSize(self.CHAT_LOG_WINDOW_MINIMUM_WIDTH, self.CHAT_LOG_WINDOW_MINIMUM_HEIGHT)
		self.btnSizing.SetPosition(self.CHAT_LOG_WINDOW_MINIMUM_WIDTH - self.btnSizing.GetWidth(), self.CHAT_LOG_WINDOW_MINIMUM_HEIGHT - self.btnSizing.GetHeight() + 2)

		self.OnResize()

	def __CreateChatInputSet(self):
		chatInputSet = ChatInputSet()
		chatInputSet.SetParent(self)
		chatInputSet.SetEscapeEvent(ui.__mem_func__(self.Close))
		chatInputSet.SetWindowVerticalAlignBottom()
		chatInputSet.Open()
		self.chatInputSet = chatInputSet

	def __CreateWindow(self):
		imgLeft = ui.ImageBox()
		imgLeft.AddFlag("not_pick")
		imgLeft.SetParent(self)

		imgCenter = ui.ExpandedImageBox()
		imgCenter.AddFlag("not_pick")
		imgCenter.SetParent(self)

		imgRight = ui.ImageBox()
		imgRight.AddFlag("not_pick")
		imgRight.SetParent(self)

		if localeinfo.IsARABIC():
			imgLeft.LoadImage("locale/ae/ui/pattern/titlebar_left.tga")
			imgCenter.LoadImage("locale/ae/ui/pattern/titlebar_center.tga")
			imgRight.LoadImage("locale/ae/ui/pattern/titlebar_right.tga")
		else:
			imgLeft.LoadImage("d:/ymir work/ui/pattern/chatlogwindow_titlebar_left.tga")
			imgCenter.LoadImage("d:/ymir work/ui/pattern/chatlogwindow_titlebar_middle.tga")
			imgRight.LoadImage("d:/ymir work/ui/pattern/chatlogwindow_titlebar_right.tga")

		imgLeft.Show()
		imgCenter.Show()
		imgRight.Show()

		btnClose = ui.Button()
		btnClose.SetParent(self)
		btnClose.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")
		btnClose.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")
		btnClose.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")
		btnClose.SetToolTipText(localeinfo.UI_CLOSE, 0, -23)
		btnClose.SetEvent(ui.__mem_func__(self.Close))
		btnClose.Show()

		btnSizing = self.ResizeButton()
		btnSizing.SetParent(self)
		btnSizing.SetMoveEvent(ui.__mem_func__(self.OnResize))
		btnSizing.SetSize(16, 16)
		btnSizing.Show()

		titleName = ui.TextLine()
		titleName.SetParent(self)

		if localeinfo.IsARABIC():
			titleName.SetPosition(self.GetWidth() - 20, 6)
		else:
			titleName.SetPosition(20, 6)

		titleName.SetText(localeinfo.CHAT_LOG_TITLE)
		titleName.Show()

		self.imgLeft = imgLeft
		self.imgCenter = imgCenter
		self.imgRight = imgRight
		self.btnClose = btnClose
		self.btnSizing = btnSizing
		self.titleName = titleName

	def __CreateButton(self):
		if localeinfo.IsARABIC():
			bx = 20
		else:
			bx = 13

		btnAll = ui.RadioButton()
		btnAll.SetParent(self)
		btnAll.SetPosition(bx, 24)
		btnAll.SetUpVisual("d:/ymir work/ui/public/xsmall_button_01.sub")
		btnAll.SetOverVisual("d:/ymir work/ui/public/xsmall_button_02.sub")
		btnAll.SetDownVisual("d:/ymir work/ui/public/xsmall_button_03.sub")
		btnAll.SetText(localeinfo.CHAT_ALL)
		btnAll.SetEvent(ui.__mem_func__(self.ToggleAllChatMode))
		btnAll.Down()
		btnAll.Show()
		self.btnAll = btnAll

		x = bx + 48
		i = 0
		self.modeButtonList = []
		for name in self.CHAT_MODE_NAME:
			btn = ui.ToggleButton()
			btn.SetParent(self)
			btn.SetPosition(x, 24)
			btn.SetUpVisual("d:/ymir work/ui/public/xsmall_button_01.sub")
			btn.SetOverVisual("d:/ymir work/ui/public/xsmall_button_02.sub")
			btn.SetDownVisual("d:/ymir work/ui/public/xsmall_button_03.sub")
			btn.SetText(name)
			btn.Show()

			mode = self.CHAT_MODE_INDEX[i]
			btn.SetToggleUpEvent(lambda arg = mode: self.ToggleChatMode(arg))
			btn.SetToggleDownEvent(lambda arg = mode: self.ToggleChatMode(arg))
			self.modeButtonList.append(btn)

			x += 48
			i += 1

		btnFreeze = ui.ToggleButton()
		btnFreeze.SetParent(self)
		btnFreeze.SetPosition(x, 24)
		btnFreeze.SetUpVisual("d:/ymir work/ui/public/xsmall_button_01.sub")
		btnFreeze.SetOverVisual("d:/ymir work/ui/public/xsmall_button_02.sub")
		btnFreeze.SetDownVisual("d:/ymir work/ui/public/xsmall_button_03.sub")
		btnFreeze.SetText(getattr(localeinfo, "CHAT_LOG_STOP", "Stop"))
		btnFreeze.SetToggleDownEvent(ui.__mem_func__(self.__FreezeOn))
		btnFreeze.SetToggleUpEvent(ui.__mem_func__(self.__FreezeOff))
		btnFreeze.Show()
		self.btnFreeze = btnFreeze

	def __CreateScrollBar(self):
		scrollBar = ui.SmallThinScrollBar()
		scrollBar.SetParent(self)
		scrollBar.Show()
		scrollBar.SetScrollEvent(ui.__mem_func__(self.OnScroll))
		self.scrollBar = scrollBar
		self.scrollBarPos = 1.0

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.imgLeft = None
		self.imgCenter = None
		self.imgRight = None
		self.btnClose = None
		self.btnSizing = None
		self.modeButtonList = []
		self.btnFreeze = None
		self.scrollBar = None
		self.chatInputSet = None

	def ToggleAllChatMode(self):
		if self.allChatMode:
			return

		self.allChatMode = True

		for i in self.__AllFilterModes():
			chat.EnableChatMode(self.chatID, i)

		for btn in self.modeButtonList:
			btn.SetUp()

	def __AllFilterModes(self):
		modes = list(self.CHAT_MODE_INDEX)
		modes.append(chat.CHAT_TYPE_BIG_NOTICE)
		if app.ENABLE_CHAT_SETTINGS_EXTEND:
			modes.append(chat.CHAT_TYPE_EXP_INFO)
			modes.append(chat.CHAT_TYPE_ITEM_INFO)
			modes.append(chat.CHAT_TYPE_MONEY_INFO)
		return modes

	def __LinkedModes(self, mode):
		modes = [mode]
		if mode == chat.CHAT_TYPE_NOTICE:
			modes.append(chat.CHAT_TYPE_BIG_NOTICE)
		if app.ENABLE_CHAT_SETTINGS_EXTEND and mode == chat.CHAT_TYPE_INFO:
			modes.append(chat.CHAT_TYPE_EXP_INFO)
			modes.append(chat.CHAT_TYPE_ITEM_INFO)
			modes.append(chat.CHAT_TYPE_MONEY_INFO)
		return modes

	def ToggleChatMode(self, mode):
		if self.allChatMode:
			self.allChatMode = False
			for i in self.__AllFilterModes():
				chat.DisableChatMode(self.chatID, i)
			for i in self.__LinkedModes(mode):
				chat.EnableChatMode(self.chatID, i)
			self.btnAll.SetUp()

		else:
			for i in self.__LinkedModes(mode):
				chat.ToggleChatMode(self.chatID, i)

	def SetSize(self, width, height):
		self.imgCenter.SetRenderingRect(0.0, 0.0, float((width - self.BLOCK_WIDTH * 2) - self.BLOCK_WIDTH) / self.BLOCK_WIDTH, 0.0)
		self.imgCenter.SetPosition(self.BLOCK_WIDTH, 0)
		self.imgRight.SetPosition(width - self.BLOCK_WIDTH, 0)

		if localeinfo.IsARABIC():
			self.titleName.SetPosition(self.GetWidth() - 20, 3)
			self.btnClose.SetPosition(3, 3)
			self.scrollBar.SetPosition(1, 45)
		else:
			self.btnClose.SetPosition(width - self.btnClose.GetWidth() - 5, 5)
			self.scrollBar.SetPosition(width - 15, 45)

		self.scrollBar.SetScrollBarSize(height - 45 - 12)
		self.scrollBar.SetPos(self.scrollBarPos)
		ui.Window.SetSize(self, width, height)

	def Open(self):
		self.OnResize()
		self.chatInputSet.SetChatFocus()
		self.Show()

	def Hide(self):
		if getattr(self, "btnFreeze", None) and getattr(self, "chatID", None) != None:
			self.btnFreeze.SetUp()
			if app.ENABLE_CHAT_SETTINGS:
				chat.SetFreeze(self.chatID, 0)
		ui.Window.Hide(self)

	def __FreezeOn(self):
		if app.ENABLE_CHAT_SETTINGS:
			chat.SetFreeze(self.chatID, 1)

	def __FreezeOff(self):
		if app.ENABLE_CHAT_SETTINGS:
			chat.SetFreeze(self.chatID, 0)

	def Close(self):
		if self.chatInputSet:
			self.chatInputSet.KillChatFocus()
		self.Hide()

	def OnResize(self):
		x, y = self.btnSizing.GetLocalPosition()
		width = self.btnSizing.GetWidth()
		height = self.btnSizing.GetHeight()

		if x < self.CHAT_LOG_WINDOW_MINIMUM_WIDTH - width:
			self.btnSizing.SetPosition(self.CHAT_LOG_WINDOW_MINIMUM_WIDTH - width, y)
			return
		if y < self.CHAT_LOG_WINDOW_MINIMUM_HEIGHT - height:
			self.btnSizing.SetPosition(x, self.CHAT_LOG_WINDOW_MINIMUM_HEIGHT - height)
			return

		self.scrollBar.LockScroll()
		self.SetSize(x + width, y + height)
		self.scrollBar.UnlockScroll()

		if localeinfo.IsARABIC():
			self.chatInputSet.SetPosition(20, 25)
		else:
			self.chatInputSet.SetPosition(0, 25)

		self.chatInputSet.SetSize(self.GetWidth() - 20, 20)
		self.chatInputSet.RefreshPosition()
		self.chatInputSet.SetChatMax(self.GetWidth() / 8)
		chat.ArrangeShowingChat(self.chatID)

	def OnScroll(self):
		self.scrollBarPos = self.scrollBar.GetPos()

		lineCount = chat.GetLineCount(self.chatID)
		visibleLineCount = chat.GetVisibleLineCount(self.chatID)
		endLine = visibleLineCount + int(float(lineCount - visibleLineCount) * self.scrollBarPos)

		chat.SetEndPos(self.chatID, self.scrollBarPos)

	def OnRunMouseWheel(self, nLen):
		if nLen > 0:
			self.scrollBar.OnUp()
		else:
			self.scrollBar.OnDown()

	def OnRender(self):
		(x, y, width, height) = self.GetRect()

		if localeinfo.IsARABIC():
			grp.SetColor(0x77000000)
			grp.RenderBar(x + 2, y + 45, 13, height - 45)

			grp.SetColor(0x77000000)
			grp.RenderBar(x, y, width, height)
			grp.SetColor(0x77000000)
			grp.RenderBox(x, y, width - 2, height)
			grp.SetColor(0x77000000)
			grp.RenderBox(x + 1, y + 1, width - 2, height)

			grp.SetColor(0xff989898)
			grp.RenderLine(x + width - 13, y + height - 1, 11, -11)
			grp.RenderLine(x + width - 9, y + height - 1, 7, -7)
			grp.RenderLine(x + width - 5, y + height - 1, 3, -3)
		else:
			grp.SetColor(0x77000000)
			grp.RenderBar(x + width - 15, y + 45, 13, height - 45)

			grp.SetColor(0x77000000)
			grp.RenderBar(x, y, width, height)
			grp.SetColor(0x77000000)
			grp.RenderBox(x, y, width - 2, height)
			grp.SetColor(0x77000000)
			grp.RenderBox(x + 1, y + 1, width - 2, height)

			grp.SetColor(0xff989898)
			grp.RenderLine(x + width - 13, y + height - 1, 11, -11)
			grp.RenderLine(x + width - 9, y + height - 1, 7, -7)
			grp.RenderLine(x + width - 5, y + height - 1, 3, -3)

		#####

		if not app.ENABLE_CHAT_SETTINGS:
			chat.ArrangeShowingChat(self.chatID)

		if localeinfo.IsARABIC():
			chat.SetPosition(self.chatID, x + width - 10, y + height - 25)
		else:
			chat.SetPosition(self.chatID, x + 10, y + height - 25)

		chat.SetHeight(self.chatID, height - 45 - 25)
		chat.Update(self.chatID)
		chat.Render(self.chatID)

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def BindInterface(self, interface):
		self.interface = proxy(interface)

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


if app.ENABLE_CHAT_SETTINGS:
	CHECK_BOX_X_POS = 145

	class ChatSettingWindow(ui.ScriptWindow):
		def __del__(self):
			ui.ScriptWindow.__del__(self)
		def __init__(self):
			ui.ScriptWindow.__init__(self)
			self.Destroy()
			self.LoadWindow()

		def Destroy(self):
			self.questionDialog = None
			self.children = {}
			self.checkBoxSlotDict = {}
			self.cacheDict = {}
			self.chatIndex = 0

		def LoadWindow(self):
			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "UIScript/ChatSettingWindow.py")

				self.GetChild("language_setting_text").SetText(uiscriptlocale.CHATTING_SETTING_LANGUAGE_CUR % app.GetLocaleName())#app.GetLocalePath().split("/")[-1])

				self.GetChild("tabname_accept_button").SAFE_SetEvent(self.SetNameQuestion)
				self.GetChild("reset_button").SAFE_SetEvent(self.ResetButton)
				self.GetChild("save_button").SAFE_SetEvent(self.Save)
				self.GetChild("cancle_button").SAFE_SetEvent(self.Close)

				self.GetChild("onoff_button").SetToggleUpEvent(self.__FilterUp)
				self.GetChild("onoff_button").SetToggleDownEvent(self.__FilterDown)

				self.GetChild("board").SetCloseEvent(self.Close)

				yPos = 64+18
				for key in range(OPTION_CHECKBOX_TALKING, OPTION_CHECKBOX_MONEY_INFO+1):
					event = lambda index = key : ui.__mem_func__(self.SetCurrentChatOption)(index)
					if localeinfo.IsARABIC():
						x = 83
					else:
						x = 145

					y = yPos+((key-1)*18)
					if key >= OPTION_CHECKBOX_DICE:
						y+=28+21+18+18+18+28+3
					if key > OPTION_CHECKBOX_DICE:
						y+=28+3
					self.checkBoxSlotDict[key] = ui.CheckBoxNew(self.GetChild("board"), x, y, event)

				(xPos,yPos) = self.GetChild("onoff_button").GetLocalPosition()
				CHATTING_PATH = "d:/ymir work/ui/chat/"
				for j in xrange(3):
					realIndex = 2 - j

					if localeinfo.IsARABIC():
						langCombo = ui.ComboBoxImage(self.GetChild("board"),CHATTING_PATH + "chattingoption_dropdown_large_bg.sub",xPos -120,yPos+22+(18*realIndex))
					else:
						langCombo = ui.ComboBoxImage(self.GetChild("board"),CHATTING_PATH + "chattingoption_dropdown_large_bg.sub",xPos,yPos+18+(18*realIndex))
					langCombo.Show()
					langCombo.SetEvent(lambda x, real = realIndex, point=proxy(self): point.__ClickLanguageBox(x, real))
					self.children["langCombo%d"%realIndex] = langCombo

					langComboButton = ui.Button()
					langComboButton.SetParent(langCombo)
					langComboButton.SetUpVisual(CHATTING_PATH + "chattingoption_dropdown_arrow_01.sub")
					langComboButton.SetOverVisual(CHATTING_PATH + "chattingoption_dropdown_arrow_02.sub")
					langComboButton.SetDownVisual(CHATTING_PATH + "chattingoption_dropdown_arrow_03.sub")
					if localeinfo.IsARABIC():
						langComboButton.SetPosition(langCombo.GetWidth()-langComboButton.GetWidth()-120,1)
					else:
						langComboButton.SetPosition(langCombo.GetWidth()-langComboButton.GetWidth(),1)
					langComboButton.SAFE_SetEvent(langCombo.OnMouseLeftButtonUp)
					langComboButton.Show()
					self.children["langComboButton%d"%realIndex] = langComboButton

				if localeinfo.IsARABIC():
					listCombo = ui.ComboBoxImage(self.GetChild("board"),CHATTING_PATH + "chattingoption_dropdown_small_bg.sub",20,64)
				else:
					listCombo = ui.ComboBoxImage(self.GetChild("board"),CHATTING_PATH + "chattingoption_dropdown_small_bg.sub",145,64)
				listCombo.Show()
				listCombo.SetEvent(lambda x, point=proxy(self): point.__ClickChat(x))
				self.children["listCombo"] = listCombo

				listComboButton = ui.Button()
				listComboButton.SetParent(listCombo)
				listComboButton.SetUpVisual(CHATTING_PATH + "chattingoption_dropdown_arrow_01.sub")
				listComboButton.SetOverVisual(CHATTING_PATH + "chattingoption_dropdown_arrow_02.sub")
				listComboButton.SetDownVisual(CHATTING_PATH + "chattingoption_dropdown_arrow_03.sub")
				if localeinfo.IsARABIC():
					listComboButton.SetPosition(listCombo.GetWidth()-listComboButton.GetWidth()-70,1)
				else:
					listComboButton.SetPosition(listCombo.GetWidth()-listComboButton.GetWidth(),1)
				listComboButton.SAFE_SetEvent(listCombo.OnMouseLeftButtonUp)
				listComboButton.Show()
				self.children["listComboButton"] = listComboButton

			except:
				import exception
				exception.Abort("ChatSettingWindow.LoadWindow.LoadScript")

		def __FilterUp(self):
			if self.CheckCacheDict(self.chatIndex) == False:
				return
			self.cacheDict[self.chatIndex][OPTION_LANGUAGE_ONOFF] = 0
			self.SetLangFilter()

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.wndChat:
				interfaceHandler.wndChat.UpdateChat()

		def __FilterDown(self):
			if self.CheckCacheDict(self.chatIndex) == False:
				return
			self.cacheDict[self.chatIndex][OPTION_LANGUAGE_ONOFF] = 1
			self.SetLangFilter()

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.wndChat:
				interfaceHandler.wndChat.UpdateChat()

		def __ClickChat(self, chatIndex):
			if self.chatIndex == chatIndex:
				return
			self.Open(chatIndex)

		def __ClickLanguageBox(self, langIndex, realIndex):
			if self.CheckCacheDict(self.chatIndex) == False:
				return
			self.cacheDict[self.chatIndex][OPTION_CHECKBOX_FLAG_DE+realIndex] = langIndex
			self.SetLangFilter()

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.wndChat:
				interfaceHandler.wndChat.UpdateChat()

		def SetCurrentChatOption(self, index):
			if self.CheckCacheDict(self.chatIndex) == False:
				return
			value = 0
			if not self.checkBoxSlotDict[index].GetCheck():
				value = 1
			self.checkBoxSlotDict[index].SetCheck(value)
			self.cacheDict[self.chatIndex][index] = value

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.wndChat:
				interfaceHandler.wndChat.UpdateChat()

		def CheckCacheDict(self, chatIndex):
			if not self.cacheDict.has_key(chatIndex):
				if cacheChat.has_key(chatIndex):
					self.cacheDict[chatIndex] = cacheChat[chatIndex]
				else:
					return False
			return True

		def Open(self, chatIndex = 0):
			if self.CheckCacheDict(chatIndex) == False:
				self.Open(0)
				return

			if chatIndex == -1:
				self.Open(self.chatIndex)
				return

			self.chatIndex = chatIndex
			self.SetList()
			self.SetCheckBox()
			self.SetLangFilter()
			self.Show()

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.wndChat:
				interfaceHandler.wndChat.UpdateChat()

		def SetList(self):
			if self.CheckCacheDict(self.chatIndex) == False:
				return
			dataChat = cacheChat[self.chatIndex]
			#dataChat = self.cacheDict[self.chatIndex]

			self.children["listCombo"].ClearItem()
			if dataChat[0] == "0" and self.chatIndex == 0:
				self.children["listCombo"].SetCurrentItem(CHAT_TAB_ALL_NAME)
				self.GetChild("tab_name_value").SetText("")
				self.GetChild("tab_name_value").SetInfoMessage(CHAT_TAB_ALL_NAME)
			else:
				self.children["listCombo"].SetCurrentItem(dataChat[OPTION_SET_NAME_TAB])
				self.GetChild("tab_name_value").SetText("")
				self.GetChild("tab_name_value").SetInfoMessage(dataChat[OPTION_SET_NAME_TAB])

			for index, data in cacheChat.iteritems():
				if index == 0 and data[0] == "0":
					self.children["listCombo"].InsertItem(index, CHAT_TAB_ALL_NAME)
				else:
					self.children["listCombo"].InsertItem(index, data[OPTION_SET_NAME_TAB])

		def SetCheckBox(self):
			if self.CheckCacheDict(self.chatIndex) == False:
				return
			dataChat = self.cacheDict[self.chatIndex]
			for j in range(OPTION_CHECKBOX_TALKING, OPTION_CHECKBOX_MONEY_INFO+1):
				self.checkBoxSlotDict[j].SetCheck(dataChat[j])

		def SetLangFilter(self):
			if self.CheckCacheDict(self.chatIndex) == False:
				return
			dataChat = self.cacheDict[self.chatIndex]

			if dataChat[OPTION_LANGUAGE_ONOFF]:
				self.GetChild("onoff_button").SetText(localeinfo.CHATTING_SETTING_LANGUAGE_ON)
				self.GetChild("onoff_button").Down()
			else:
				self.GetChild("onoff_button").SetText(localeinfo.CHATTING_SETTING_LANGUAGE_OFF)
				self.GetChild("onoff_button").SetUp()

			alreadyHaveLang = []
			langData = {
				0:localeinfo.CHATTING_SETTING_NON,
			}

			for j in xrange(3):
				alreadyHaveLang.append(dataChat[j+OPTION_CHECKBOX_FLAG_DE])

			for j in xrange(3):
				langIndex = dataChat[j+OPTION_CHECKBOX_FLAG_DE]
				self.children["langCombo%d"%j].ClearItem()
				self.children["langCombo%d"%j].SetCurrentItem(langData[langIndex])
				for index, data in langData.iteritems():
					if index != 0:
						if index in alreadyHaveLang:
							continue
					self.children["langCombo%d"%j].InsertItem(index, data)

		def SetNameQuestion(self):
			if self.CheckCacheDict(self.chatIndex) == False:
				return

			if self.questionDialog != None:
				self.__QuestionPopupCancel()
			questionDialog = uicommon.QuestionDialog()
			questionDialog.SetText(localeinfo.CHATTING_SETTING_CHANGE_TITLE_NAME)
			questionDialog.SetAcceptEvent(ui.__mem_func__(self.__QuestionSetNameAccept))
			questionDialog.SetCancelEvent(ui.__mem_func__(self.__QuestionPopupCancel))
			questionDialog.Open()
			self.questionDialog = questionDialog

		def __QuestionSetNameAccept(self):
			if self.chatIndex == 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHATTING_SETTING_CHANGE_TITLE_NOT)
				self.__QuestionPopupCancel()
				return

			text = self.GetChild("tab_name_value").GetText()

			self.GetChild("tab_name_value").SetText("General")
			(x_,y_) = self.GetChild("tab_name_value").GetTextSize()
			self.GetChild("tab_name_value").SetText(text)

			if self.GetChild("tab_name_value").GetTextSize()[0] > x_ or len(text) == 0 or text.isspace():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHATTING_SETTING_CANT_CHANGE_TITLE)
				self.__QuestionPopupCancel()
				return

			self.cacheDict[self.chatIndex][OPTION_SET_NAME_TAB] = text
			cacheChat[self.chatIndex][OPTION_SET_NAME_TAB] = text

			SaveChatData()

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.wndChat:
				interfaceHandler.wndChat.LoadChatLoby()

			self.__QuestionPopupCancel()

		def ResetButton(self):
			if self.CheckCacheDict(self.chatIndex) == False:
				return

			if self.questionDialog != None:
				self.__QuestionPopupCancel()
			questionDialog = uicommon.QuestionDialog()
			questionDialog.SetText(localeinfo.CHATTING_SETTING_CLEAR_QUESTION)
			questionDialog.SetAcceptEvent(ui.__mem_func__(self.__QuestionClearAccept))
			questionDialog.SetCancelEvent(ui.__mem_func__(self.__QuestionPopupCancel))
			questionDialog.Open()
			self.questionDialog = questionDialog

		def __QuestionClearAccept(self):
			LoadChatNewEmpty(self.chatIndex)
			self.cacheDict[self.chatIndex] = cacheChat[self.chatIndex]
			self.Open(self.chatIndex)

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.wndChat:
				interfaceHandler.wndChat.LoadChatLoby()

			self.__QuestionPopupCancel()

		def __QuestionPopupCancel(self):
			if self.questionDialog != None:
				self.questionDialog.Close()
				self.questionDialog=None

		def Save(self):
			#if self.questionDialog != None:
			#	self.__QuestionPopupCancel()
			#questionDialog = uicommon.QuestionDialog()
			name = cacheChat[self.chatIndex][0]
			if self.chatIndex == 0 and name == "0":
				name = uiscriptlocale.CHATTING_SETTING_TALKING
			#questionDialog.SetText(localeinfo.CHATTING_SETTING_SAVE_QUESTION % name)
			#questionDialog.SetAcceptEvent(ui.__mem_func__(self.__QuestionSaveAccept))
			#questionDialog.SetCancelEvent(ui.__mem_func__(self.__QuestionPopupCancel))
			#questionDialog.Open()
			#self.questionDialog = questionDialog
			self.__QuestionSaveAccept()

		def __QuestionSaveAccept(self):
			cacheChat[self.chatIndex] = self.cacheDict[self.chatIndex]
			SaveChatData()
			self.__QuestionPopupCancel()

		def Close(self):
			self.Hide()

		def OnPressEscapeKey(self):
			self.Close()
			return True

	LOG_CHAT_SET_BASE = 10

	class ChatLogWindowNew(ui.Window):
		CHAT_LOG_WINDOW_MINIMUM_WIDTH = 450
		CHAT_LOG_WINDOW_MINIMUM_HEIGHT = 120
		CHAT_POSITION = 25
		BLOCK_WIDTH = 32

		class ResizeButton(ui.DragButton):
			def __init__(self):
				ui.DragButton.__init__(self)
			def __del__(self):
				ui.DragButton.__del__(self)
			def OnMouseOverIn(self):
				app.SetCursor(app.HVSIZE)
			def OnMouseOverOut(self):
				app.SetCursor(app.NORMAL)

		def __init__(self):
			ui.Window.__init__(self)
			self.AddFlag("float")
			self.AddFlag("movable")
			if app.ENABLE_WINDOW_SLIDE_EFFECT:
				self.AddFlag("animated_board")
			self.SetWindowName("ChatLogWindowNew")
			self.chatID = 0

			self.__CreateWindow()
			self.__CreateScrollBar()

			self.SetPosition(20, 20)
			self.SetSize(self.CHAT_LOG_WINDOW_MINIMUM_WIDTH, self.CHAT_LOG_WINDOW_MINIMUM_HEIGHT)
			self.btnSizing.SetPosition(self.CHAT_LOG_WINDOW_MINIMUM_WIDTH-self.btnSizing.GetWidth(), self.CHAT_LOG_WINDOW_MINIMUM_HEIGHT-self.btnSizing.GetHeight()+2)
			self.OnResize()

		def __del__(self):
			ui.Window.__del__(self)

		def Destroy(self):
			self.BLOCK_WIDTH = 0
			self.CHAT_MODE_INDEX =0
			self.CHAT_LOG_WINDOW_MINIMUM_WIDTH = 0
			self.CHAT_LOG_WINDOW_MINIMUM_HEIGHT = 0
			self.allChatMode = 0
			self.chatID = 0
			self.imgLeft = 0
			self.imgCenter = 0
			self.imgRight = 0
			self.btnClose = 0
			self.btnSizing = 0
			self.titleName = 0
			self.btnAll = 0
			self.modeButtonList = 0
			self.scrollBar = 0
			self.scrollBarPos = 0
			self.btnFreeze = 0
			self.Hide()

		def __CreateWindow(self):
			imgLeft = ui.ImageBox()
			imgLeft.AddFlag("not_pick")
			imgLeft.SetParent(self)

			imgCenter = ui.ExpandedImageBox()
			imgCenter.AddFlag("not_pick")
			imgCenter.SetParent(self)

			imgRight = ui.ImageBox()
			imgRight.AddFlag("not_pick")
			imgRight.SetParent(self)
			imgLeft.LoadImage("d:/ymir work/ui/chat/titlebar_chat_left.tga")
			imgCenter.LoadImage("d:/ymir work/ui/chat/titlebar_chat_middle.tga")
			imgRight.LoadImage("d:/ymir work/ui/chat/titlebar_chat_right.tga")

			imgLeft.Show()
			imgCenter.Show()
			imgRight.Show()

			btnClose = ui.Button()
			btnClose.SetParent(self)
			btnClose.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")
			btnClose.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")
			btnClose.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")
			btnClose.SetToolTipText(localeinfo.UI_CLOSE, 0, -20)
			btnClose.SetEvent(ui.__mem_func__(self.Close))
			btnClose.Show()

			btnAdd = ui.Button()
			btnAdd.SetParent(self)
			btnAdd.SetUpVisual("d:/ymir work/ui/chat/btn_hide01_default.tga")
			btnAdd.SetOverVisual("d:/ymir work/ui/chat/btn_hide01_over.tga")
			btnAdd.SetDownVisual("d:/ymir work/ui/chat/btn_hide01_down.tga")
			btnAdd.SetToolTipText(localeinfo.CHATTING_SETTING_DEL, 0, -24)
			btnAdd.SetEvent(ui.__mem_func__(self.Add))
			btnAdd.Show()

			btnSizing = self.ResizeButton()
			btnSizing.SetParent(self)
			btnSizing.SetMoveEvent(ui.__mem_func__(self.OnResize))
			btnSizing.SetSize(16, 16)
			btnSizing.Show()

			titleName = ui.TextLine()
			titleName.SetParent(self)

			if localeinfo.IsARABIC():
				titleName.SetPosition(self.GetWidth() + 320, 7)
			else:
				titleName.SetPosition(20, 6)

			titleName.Show()

			self.imgLeft = imgLeft
			self.imgCenter = imgCenter
			self.imgRight = imgRight
			self.btnClose = btnClose
			self.btnSizing = btnSizing
			self.titleName = titleName
			self.btnAdd = btnAdd

			btnFreeze = ui.ToggleButton()
			btnFreeze.SetParent(self)
			btnFreeze.SetUpVisual("d:/ymir work/ui/public/xsmall_button_01.sub")
			btnFreeze.SetOverVisual("d:/ymir work/ui/public/xsmall_button_02.sub")
			btnFreeze.SetDownVisual("d:/ymir work/ui/public/xsmall_button_03.sub")
			btnFreeze.SetText(getattr(localeinfo, "CHAT_LOG_STOP", "Stop"))
			btnFreeze.SetToggleDownEvent(ui.__mem_func__(self.__FreezeOn))
			btnFreeze.SetToggleUpEvent(ui.__mem_func__(self.__FreezeOff))
			btnFreeze.Show()
			self.btnFreeze = btnFreeze

			self.backupData = {}
			self.chatIndex = -1

		def __CreateScrollBar(self):
			scrollBar = ui.SmallThinScrollBar()
			scrollBar.SetParent(self)
			scrollBar.Show()
			scrollBar.SetScrollEvent(ui.__mem_func__(self.OnScroll))
			self.scrollBar = scrollBar
			self.scrollBarPos = 1.0

		def SetSize(self, width, height):
			self.imgCenter.SetRenderingRect(0.0, 0.0, float((width - self.BLOCK_WIDTH*2) - self.BLOCK_WIDTH) / self.BLOCK_WIDTH, 0.0)
			self.imgCenter.SetPosition(self.BLOCK_WIDTH, 0)
			self.imgRight.SetPosition(width - self.BLOCK_WIDTH, 0)
			self.btnClose.SetPosition(width - self.btnClose.GetWidth()-5, 5)
			self.btnAdd.SetPosition(width - 44, 2)
			self.btnFreeze.SetPosition(width - 94, 2)
			self.scrollBar.SetPosition(width - 15, 26)
			self.scrollBar.SetScrollBarSize(height - 26 - 12)
			self.scrollBar.SetPos(self.scrollBarPos)
			ui.Window.SetSize(self, width, height)

		def UpdateChat(self):
			CHAT_MODE_INDEX = [ chat.CHAT_TYPE_TALKING,chat.CHAT_TYPE_PARTY,chat.CHAT_TYPE_GUILD,chat.CHAT_TYPE_SHOUT,chat.CHAT_TYPE_INFO,chat.CHAT_TYPE_NOTICE, chat.CHAT_TYPE_BIG_NOTICE, chat.CHAT_TYPE_DICE_INFO]
			CHAT_MODE_INDEX.append(chat.CHAT_TYPE_EXP_INFO)
			CHAT_MODE_INDEX.append(chat.CHAT_TYPE_ITEM_INFO)
			CHAT_MODE_INDEX.append(chat.CHAT_TYPE_MONEY_INFO)

			for i in CHAT_MODE_INDEX:
				chat.DisableChatMode(self.chatID, i)
			dataChat = self.backupData
			for key, data in OPTION_CHECKBOX_MODE.items():
				if dataChat[key] > 0:
					for chatIndex in data[0]:
						chat.EnableChatMode(self.chatID, chatIndex)

			# if app.ENABLE_MULTI_LANGUAGE_SYSTEM_NOTUSED:
				# for j in range(1,10):
					# chat.DisableCountryMode(self.chatID, j)

			# if app.ENABLE_MULTI_LANGUAGE_SYSTEM_NOTUSED:
				# if dataChat[OPTION_LANGUAGE_ONOFF] == 1:
					# for country in range(OPTION_CHECKBOX_FLAG_DE, OPTION_MAX):
						# if dataChat[country] > 0:
							# chat.EnableCountryMode(self.chatID, dataChat[country])
				# else:
					# for j in range(1,10):
						# chat.EnableCountryMode(self.chatID, j)

		def __FreezeOn(self):
			if self.chatID >= LOG_CHAT_SET_BASE:
				chat.SetFreeze(self.chatID, 1)
			else:
				self.btnFreeze.SetUp()

		def __FreezeOff(self):
			if self.chatID >= LOG_CHAT_SET_BASE:
				chat.SetFreeze(self.chatID, 0)

		def Open(self, chatIndex = -1):
			if not cacheChat.has_key(chatIndex):
				return

			self.chatIndex = int(chatIndex)
			self.chatID = chat.CreateChatSet(LOG_CHAT_SET_BASE + self.chatIndex)
			chat.SetBoardState(self.chatID, chat.BOARD_STATE_LOG)

			chatData = cacheChat[chatIndex]
			self.backupData = chatData

			if chatData[0] == "0" and chatIndex == 0:
				self.titleName.SetText(CHAT_TAB_ALL_NAME)
			else:
				self.titleName.SetText(chatData[OPTION_SET_NAME_TAB])
			self.UpdateChat()
			self.btnFreeze.SetUp()
			self.OnResize()
			self.Show()

		def Add(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()

			if self.chatIndex != 0:
				if interfaceHandler and interfaceHandler.wndChat:
					interfaceHandler.wndChat.CreateLobyButton(self.chatIndex, self.backupData[OPTION_SET_NAME_TAB])
					interfaceHandler.wndChat.LoadChatLoby()

			self.Hide()
			if self.chatID >= LOG_CHAT_SET_BASE:
				chat.DeleteChatSet(self.chatID)
				self.chatID = 0

		def Close(self, isAuto = False):
			self.Hide()
			if getattr(self, "btnFreeze", None):
				self.btnFreeze.SetUp()
			if self.chatID >= LOG_CHAT_SET_BASE:
				chat.DeleteChatSet(self.chatID)
				self.chatID = 0

			if isAuto == False:
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler and interfaceHandler.wndChat:
					interfaceHandler.wndChat.LoadChatLoby()

		def OnResize(self):
			x, y = self.btnSizing.GetLocalPosition()
			width = self.btnSizing.GetWidth()
			height = self.btnSizing.GetHeight()

			if x < self.CHAT_LOG_WINDOW_MINIMUM_WIDTH - width:
				self.btnSizing.SetPosition(self.CHAT_LOG_WINDOW_MINIMUM_WIDTH - width, y)
				width = self.CHAT_LOG_WINDOW_MINIMUM_WIDTH
			if y < self.CHAT_LOG_WINDOW_MINIMUM_HEIGHT - height:
				self.btnSizing.SetPosition(x, self.CHAT_LOG_WINDOW_MINIMUM_HEIGHT - height)
				height = self.CHAT_LOG_WINDOW_MINIMUM_HEIGHT

			self.scrollBar.LockScroll()
			self.SetSize(x + width, y + height)
			self.scrollBar.UnlockScroll()
			if self.chatID >= LOG_CHAT_SET_BASE:
				chat.ArrangeShowingChat(self.chatID)

		def OnMouseWheel(self, nLen):
			if self.scrollBar:
				if nLen > 0:
					self.scrollBar.OnUp()
				else:
					self.scrollBar.OnDown()
				return True
			return False

		def OnScroll(self):
			self.scrollBarPos = self.scrollBar.GetPos()

			lineCount = chat.GetLineCount(self.chatID)
			visibleLineCount = chat.GetVisibleLineCount(self.chatID)
			endLine = visibleLineCount + int(float(lineCount - visibleLineCount) * self.scrollBarPos)

			chat.SetEndPos(self.chatID, self.scrollBarPos)

		def OnRender(self):
			(x, y, width, height) = self.GetRect()

			if localeinfo.IsARABIC():
				grp.SetColor(0x77000000)
				grp.RenderBar(x + 2, y + 45, 13, height - 45)

				grp.SetColor(0x77000000)
				grp.RenderBar(x, y, width, height)
				grp.SetColor(0x77000000)
				grp.RenderBox(x, y, width - 2, height)
				grp.SetColor(0x77000000)
				grp.RenderBox(x + 1, y + 1, width - 2, height)

				grp.SetColor(0xff525552)
				grp.RenderLine(x + width - 13, y + height - 1, 11, -11)
				grp.RenderLine(x + width - 9, y + height - 1, 7, -7)
				grp.RenderLine(x + width - 5, y + height - 1, 3, -3)
			else:
				grp.SetColor(0x77000000)
				grp.RenderBar(x + width - 15, y + 45, 13, height - 45)

				grp.SetColor(0x77000000)
				grp.RenderBar(x, y, width, height)
				grp.SetColor(0x77000000)
				grp.RenderBox(x, y, width - 2, height)
				grp.SetColor(0xff000000)
				grp.RenderBox(x + 1, y + 1, width - 2, height)

				grp.SetColor(0xff989898)
				grp.RenderLine(x + width - 13, y + height - 1, 11, -11)
				grp.RenderLine(x + width - 9, y + height - 1, 7, -7)
				grp.RenderLine(x + width - 5, y + height - 1, 3, -3)

			#####

			if localeinfo.IsARABIC():
				chat.SetPosition(self.chatID, x + width - 10, y + height - 25)
			else:
				chat.SetPosition(self.chatID, x + 10, y + height - 25)

			chat.SetHeight(self.chatID, height - 45 - 25)
			chat.Update(self.chatID)
			chat.Render(self.chatID)

		def OnPressEscapeKey(self):
			self.Close()
			return True

		def OnMouseLeftButtonDown(self):
			hyperlink = ui.GetHyperlink()
			if hyperlink:
				if app.IsPressed(app.DIK_LALT):
					link = chat.GetLinkFromHyperlink(hyperlink)
					ime.PasteString(link)
				else:
					interfaceHandler = systemSetting.GetInterfaceHandler()
					if interfaceHandler:
						interfaceHandler.MakeHyperlinkTooltip(hyperlink)

		def OnMouseRightButtonDown(self):
			# SHIFT+right-click on an item hyperlink opens the wiki on that item.
			if app.ENABLE_INGAME_WIKI and app.IsPressed(app.DIK_LSHIFT):
				hyperlink = ui.GetHyperlink()
				if hyperlink:
					interfaceHandler = systemSetting.GetInterfaceHandler()
					if interfaceHandler:
						interfaceHandler.OpenWikiFromHyperlink(hyperlink)

if app.ENABLE_AUTO_SHOUT:
	if app.ENABLE_AUTO_SHOUT_V2:
		g_autoShoutMinInterval = 45
		AUTOSHOUOT_AVAILABLE_INTERVALS = [45, 90, 120]
	else:
		AUTOSHOUOT_AVAILABLE_INTERVALS = [5, 10, 15, 20, 25]
	CLIENT_SIDE_SHOUT_COOLDOWN = 5
	g_autoShoutEnabled = 0
	g_autoShoutInterval = AUTOSHOUOT_AVAILABLE_INTERVALS[0]
	g_autoShoutLastSend = 0.0
	g_autoShoutClientCooldownNext = 0.0

	if app.ENABLE_AUTO_SHOUT_V2:
		# the server re-pushes the entitled floor whenever premium state settles,
		# so this must stay a no-op when the value has not actually changed
		def SetAutoShoutMinInterval(seconds):
			global g_autoShoutMinInterval, AUTOSHOUOT_AVAILABLE_INTERVALS, g_autoShoutInterval
			try:
				seconds = int(seconds)
			except:
				return
			if seconds < 1 or seconds == g_autoShoutMinInterval:
				return
			g_autoShoutMinInterval = seconds
			AUTOSHOUOT_AVAILABLE_INTERVALS = [g_autoShoutMinInterval, 90, 120]
			if g_autoShoutInterval < g_autoShoutMinInterval or g_autoShoutInterval not in AUTOSHOUOT_AVAILABLE_INTERVALS:
				g_autoShoutInterval = g_autoShoutMinInterval
			if wndAutoShout:
				wndAutoShout.RefreshIntervalCombo()
	else:
		AUTO_SHOUT_PERIOD = 30 if app.USE_PREMIUM_FEATURES and constinfo.player_premium_type == player.PREMIUM_TYPE_NONE else 60  # seconds

	g_autoShoutChatLine = None

	def BindAutoShoutChatLine(chatLine):
		global g_autoShoutChatLine
		g_autoShoutChatLine = proxy(chatLine)
		if not hasattr(g_autoShoutChatLine, "lastShoutTime"):
			g_autoShoutChatLine.lastShoutTime = 0

	def AutoShout_Tick():
		# Runs every frame from ChatWindow.OnUpdate
		if not g_autoShoutEnabled:
			return
		if not g_autoShoutLastMessage:
			return
		if not g_autoShoutChatLine:
			return

		now = app.GetTime()
		cl = g_autoShoutChatLine

		if app.ENABLE_AUTO_SHOUT_V2:
			# the pushed floor wins over a stale combo pick, a slower pick wins over the floor
			if now < cl.lastShoutTime + max(g_autoShoutInterval, g_autoShoutMinInterval):
				return
			cl.lastShoutTime = now
			net.SendChatPacket(g_autoShoutLastMessage, chat.CHAT_TYPE_SHOUT_AUTO)
		else:
			# identical to the tutorial: wait 10s from last shout
			if now < cl.lastShoutTime + AUTO_SHOUT_PERIOD:
				return
			if chr.IsGameMaster(player.GetMainCharacterIndex()):
				return
			cl.lastShoutTime = now
			net.SendChatPacket(g_autoShoutLastMessage, chat.CHAT_TYPE_SHOUT)


	class AutoShoutBoard(ui.ScriptWindow):
		def __init__(self, send_shout_func):
			ui.ScriptWindow.__init__(self)
			self.send_shout_func = send_shout_func
			self.isAutoShoutEnabled = 0
			self.autoShoutMessage = ""
			self.autoShoutInterval = AUTOSHOUOT_AVAILABLE_INTERVALS[0]
			self.nextAutoShoutTime = 0
			self.lastSendTime = 0.0
			self.clientSideNextShoutTime = 0.0
			self.question_button_tooltip = None
			self.question_button_tooltip_list = [
				localeinfo.AUTOSHOUT_DESC1,
				localeinfo.AUTOSHOUT_DESC2,
				localeinfo.AUTOSHOUT_DESC3,
				localeinfo.AUTOSHOUT_DESC4
			]
			if app.ENABLE_WINDOW_SLIDE_EFFECT:
				self.AddFlag("animated_board")
			self.__Load()

		def __del__(self):
			ui.ScriptWindow.__del__(self)

		def __Load(self):
			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "uiscript/autoshoutwindow.py")
			except:
				import exception
				exception.Abort("AutoShoutBoard.LoadWindow.LoadObject")

			try:
				GetObject=self.GetChild
				self.board = GetObject("board")
				self.board_window = GetObject("board_window")
				self.lastShoutText = GetObject("last_shout_text")
				self.enableButton = GetObject("enable_button")
				self.ToolTipButton = GetObject("ToolTipButton")
			except:
				import exception
				exception.Abort("AutoShoutBoard.LoadWindow.BindObject")

			self.intervalComboBox = ui.ComboBox()
			self.intervalComboBox.SetParent(self.board_window)
			self.intervalComboBox.SetPosition(80, 50)
			self.intervalComboBox.SetSize(70, 15)
			self.intervalComboBox.Hide()
			self.board.SetCloseEvent(self.Close)
			for interval in AUTOSHOUOT_AVAILABLE_INTERVALS:
				self.intervalComboBox.InsertItem2(AUTOSHOUOT_AVAILABLE_INTERVALS.index(interval), str(interval) + "s")
			self.intervalComboBox.SetEvent(lambda index: self.__OnAutoShoutSelectInterval(index))
			self.enableButton.SetToggleUpEvent(ui.__mem_func__(self.__RequestStatusChange))
			self.enableButton.SetToggleDownEvent(ui.__mem_func__(self.__RequestStatusChange))
			self.intervalComboBox.SetCurrentItem(str(self.autoShoutInterval) + "s")
			self.intervalComboBox.SelectItem(AUTOSHOUOT_AVAILABLE_INTERVALS.index(self.autoShoutInterval))
			self.enableButton.SetUp()

			self.question_button_tooltip = self.__CreateGameTypeToolTip("", self.question_button_tooltip_list)
			self.question_button_tooltip.SetTop()
			self.ToolTipButton.SetToolTipWindow(self.question_button_tooltip)
		
		def SetNewShoutMessage(self, message):
			if g_autoShoutEnabled:
				return
			self.lastShoutText.SetText(message)
			self.autoShoutMessage = message

		def __CreateGameTypeToolTip(self, title, descList):
			toolTip = uiToolTip.ToolTip()
			toolTip.AppendSpace(7)

			for desc in descList:
				toolTip.AutoAppendTextLineAE(desc)

			toolTip.AlignHorizonalCenter()
			toolTip.SetTop()
			return toolTip

		def SetStatus(self, status):
			self.isAutoShoutEnabled = status
			global g_autoShoutEnabled
			g_autoShoutEnabled = self.isAutoShoutEnabled
			if self.isAutoShoutEnabled:
				global g_autoShoutLastMessage
				last_message = g_autoShoutLastMessage
				if not last_message:
					self.isAutoShoutEnabled = 0
					net.SendChatPacket("/auto_shout disable")
					self.enableButton.SetUp()
				else:
					self.autoShoutMessage = last_message
					self.lastShoutText.SetText(self.autoShoutMessage)
					self.enableButton.Down()
			else:
				self.autoShoutMessage = ""
				self.enableButton.SetUp()

		def __RequestStatusChange(self):
			if self.isAutoShoutEnabled:
				net.SendChatPacket("/auto_shout disable")
			else:
				global g_autoShoutLastMessage
				if not g_autoShoutLastMessage:
					chat.AppendChat(chat.CHAT_TYPE_INFO, "You need to send a shout first.")
					self.enableButton.SetUp()
					return
				net.SendChatPacket("/auto_shout enable")

		def __OnAutoShoutSelectInterval(self, index):
			self.autoShoutInterval = AUTOSHOUOT_AVAILABLE_INTERVALS[index]
			selected_text = str(self.autoShoutInterval) + "s"
			self.intervalComboBox.SetCurrentItem(selected_text)

			global g_autoShoutInterval, g_autoShoutLastSend
			g_autoShoutInterval = self.autoShoutInterval
			g_autoShoutLastSend = app.GetTime() - (g_autoShoutInterval - 2)

		if app.ENABLE_AUTO_SHOUT_V2:
			def RefreshIntervalCombo(self):
				comboBox = getattr(self, "intervalComboBox", None)
				if not comboBox:
					return
				comboBox.ClearItem()
				for itemKey, interval in enumerate(AUTOSHOUOT_AVAILABLE_INTERVALS):
					comboBox.InsertItem2(itemKey, str(interval) + "s")
				self.autoShoutInterval = g_autoShoutInterval
				comboBox.SetCurrentItem(str(self.autoShoutInterval) + "s")
				comboBox.SelectItem(AUTOSHOUOT_AVAILABLE_INTERVALS.index(self.autoShoutInterval))

		def OnUpdate(self):
			return
			# >>> AUTO_SHOUT_V2 BEGIN - second auto-send path, unreachable behind the return above; AutoShout_Tick is the only sender (disabled)
			# if not self.isAutoShoutEnabled or not self.autoShoutMessage:
				# return

			# now = app.GetTime()

			# # If time jumped backwards (warp/phase), force a quick resync
			# if not hasattr(self, "_lastTick"):
				# self._lastTick = now
			# elif now < self._lastTick:
				# # make it fire soon after warp, but still respect 5s client cooldown
				# self.lastSendTime = now - self.autoShoutInterval
				# self.clientSideNextShoutTime = max(self.clientSideNextShoutTime, now + 2)
			# self._lastTick = now

			# # Respect client-side shout cooldown first
			# if now < self.clientSideNextShoutTime:
				# return

			# # Relative schedule: send when enough seconds passed since last send
			# if now - self.lastSendTime >= self.autoShoutInterval:
				# net.SendChatPacket(self.autoShoutMessage, chat.CHAT_TYPE_SHOUT)
				# self.lastSendTime = now
				# self.clientSideNextShoutTime = now + CLIENT_SIDE_SHOUT_COOLDOWN
			# <<< AUTO_SHOUT_V2 END
		
		
		def set_send_func(self, f, rebind=False):
			self.send_shout_func = f
			if rebind and self.isAutoShoutEnabled and self.autoShoutMessage:
				now = app.GetTime()
				# Resume within ~2�5s, still respecting client cooldown
				self.nextAutoShoutTime = max(now + 2, self.clientSideNextShoutTime)

		def Close(self):
			self.Hide()

		def Open(self):
			global g_autoShoutLastMessage
			if g_autoShoutLastMessage:
				self.lastShoutText.SetText(g_autoShoutLastMessage)
			else:
				self.lastShoutText.SetText(localeinfo.AUTOSHOUT_NO_MESSAGE)
			self.SetCenterPosition()
			self.SetTop()
			self.Show()

		def OnPressEscapeKey(self):
			self.Close()
			return True
