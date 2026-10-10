# coding: latin_1

import app
import chr
import net
import player

import ui
import uioption

import uisystemoption
import uigameoption
import uiscriptlocale
import networkmodule
import constinfo
import localeinfo
import uiadvancedskyboxoption

if app.ENABLE_GAMEOPTION_RENEWAL:
	import uiadvancedgameoptions

if app.ENABLE_ITEMSHOP:
	import systemSetting

if app.USE_INGAME_CHANGE_CHANNEL:
	import chat
	import wndMgr
	import player
	import os

	CHANNEL_SAVE_PATH = "data/user/data/channel/"

	def GetChannelFilePath():
		char_name = player.GetName()
		filename = "{}_channel.txt".format(char_name)
		return os.path.join(CHANNEL_SAVE_PATH, filename)

	class ChangeChannelDialog(ui.ScriptWindow):
		def __init__(self):
			ui.ScriptWindow.__init__(self)

			if app.ENABLE_WINDOW_SLIDE_EFFECT:
				self.AddFlag("animated_board")

			# Tracking variables
			self.previousChannel = -1
			self.currentChannel = 0
			self.nextChannel = 0
			self.channelID = 1

			self.__Load()
			self.LoadChannels()

		def __Load(self):
			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "uiscript/switchchannel_dialog.py")
			except Exception as e:
				import exception
				exception.Abort("ChangeChannelDialog.Load")
				return

			try:
				self.board = self.GetChild("board_ui")
				self.subboard = self.GetChild("subboard_ui")
				self.titleBar = self.GetChild("title_bar_ui")
				self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))
			except:
				import exception
				exception.Abort("ChangeChannelDialog.Bind")
				return

			self.chBtnList = []
			self.chLabelList = []
			chCount = 4

			self.dlgWidth = 190
			self.subBoardHeight = 23 * chCount + 5 * (chCount - 1) + 13
			self.dlgHeight = self.subBoardHeight + 75

			tmp = ui.MakeButton(self.board, 0, self.dlgHeight - 33, "", "d:/ymir work/ui/", "xbtn_1.png", "xbtn_2.png", "xbtn_3.png")
			center_x = (self.dlgWidth - tmp.GetWidth()) // 2
			tmp.SetPosition(center_x, self.dlgHeight - 36)
			tmp.SetText(localeinfo.SWITCH_CHANNEL_ACCEPT)
			tmp.SetEvent(ui.__mem_func__(self.Accept))
			self.acceptBtn = tmp

			# tmp = ui.MakeButton(self.board, self.dlgWidth - 73, self.dlgHeight - 33, "", "d:/ymir work/ui/public/", "middle_button_01.sub", "middle_button_02.sub", "middle_button_03.sub")
			# tmp.SetText(localeinfo.SWITCH_CHANNEL_CANCEL)
			# tmp.SetEvent(ui.__mem_func__(self.Close))
			# self.closeBtn = tmp

			for i in xrange(chCount):
				# Create channel button
				tmp = ui.MakeButton(self.subboard, 8, 6 + i * 28, "", "d:/ymir work/ui/game/myshop_deco/", "select_btn_01.sub", "select_btn_02.sub", "select_btn_03.sub")
				tmp.SetText(self.GetChannelName(i + 1))
				tmp.SetEvent(ui.__mem_func__(self.__SelectChannel), i + 1)
				self.chBtnList.append(tmp)

				# Create label next to button
				label = ui.TextLine()
				label.SetParent(self.subboard)
				label.SetPosition(150, 10 + i * 28) 
				label.SetText("")
				label.SetHorizontalAlignLeft()
				label.Show()
				self.chLabelList.append(label)

		def __SelectChannel(self, idx):
			if idx == 99:
				idx = 1

			self.newChannelID = idx
			self.nextChannel = idx

			for btn in self.chBtnList:
				btn.SetUp()
				btn.Enable()

			self.chBtnList[idx - 1].Down()
			self.chBtnList[idx - 1].Disable()

			self.__RefreshChannelLabels()

		def __RefreshChannelLabels(self):
			for i in xrange(len(self.chLabelList)):
				label = self.chLabelList[i]

				if (i + 1) == self.currentChannel:
					label.SetText(localeinfo.CHANNEL_SWITCH_ACTUAL)
				elif (i + 1) == self.previousChannel:
					label.SetText(localeinfo.CHANNEL_SWITCH_PREVIOUS)
				else:
					label.SetText("")

		def Accept(self):
			if self.newChannelID == self.channelID:
				return

			self.previousChannel = self.channelID
			self.channelID = self.newChannelID
			self.currentChannel = self.channelID
			self.nextChannel = self.currentChannel

			self.SaveChannels()

			net.SendChatPacket("/channel_switch %d" % self.newChannelID)

			self.__RefreshChannelLabels()
			self.Close()

		def Open(self):
			self.channelID = net.GetConnectedChannelNum()
			self.currentChannel = self.channelID
			self.__SelectChannel(self.channelID)

			self.Show()

		def Close(self):
			self.Hide()

		def OnPressEscapeKey(self):
			self.Close()
			return True

		def GetChannelName(self, idx):
			return "CH %d" % idx

		def SaveChannels(self):
			try:
				data = {
					"previousChannel": self.previousChannel,
					"currentChannel": self.currentChannel,
					"nextChannel": self.nextChannel,
					"channelID": self.channelID
				}
				if not os.path.exists(CHANNEL_SAVE_PATH):
					os.makedirs(CHANNEL_SAVE_PATH)
				file = open(GetChannelFilePath(), "wb")
				file.write(str(data))
				file.close()
			except Exception as e:
				dbg.Trace("Failed to save channels: {}".format(e))

		def LoadChannels(self):
			try:
				file_path = GetChannelFilePath()
				if os.path.exists(file_path):
					file = open(file_path, "rb")
					data = file.read()
					file.close()

					data_dict = eval(data)

					self.previousChannel = data_dict.get("previousChannel", -1)
					self.currentChannel = data_dict.get("currentChannel", 0)
					self.nextChannel = data_dict.get("nextChannel", 0)
					self.channelID = data_dict.get("channelID", 1)
				else:
					self.previousChannel = -1
					self.currentChannel = 0
					self.nextChannel = 0
					self.channelID = 1
			except Exception as e:
				dbg.Trace("Failed to load channels: {}".format(e))
				self.previousChannel = -1
				self.currentChannel = 0
				self.nextChannel = 0
				self.channelID = 1

		def Destroy(self):
			for btn in self.chBtnList:
				btn.SetEvent(None)
				del btn

			for lbl in self.chLabelList:
				lbl.SetText("")
				del lbl
			self.chLabelList = []

			if self.titleBar:
				self.titleBar.SetCloseEvent(None)
				self.titleBar = None

			if self.acceptBtn:
				self.acceptBtn.SetEvent(None)
				del self.acceptBtn
				self.acceptBtn = None

			# if self.closeBtn:
				# self.closeBtn.SetEvent(None)
				# del self.closeBtn
				# self.closeBtn = None

			self.ClearDictionary()

		def __del__(self):
			ui.ScriptWindow.__del__(self)

###################################################################################################
## System
class SystemDialog(ui.ScriptWindow):
	if app.USE_INGAME_CHANGE_CHANNEL:
		def __ClickChangeCH(self):
			if not self.switchCHDlg:
				self.switchCHDlg = ChangeChannelDialog()

			if self.switchCHDlg.IsShow():
				self.switchCHDlg.Close()
			else:
				self.switchCHDlg.Open()
				self.switchCHDlg.SetTop()

				wndMgr.Hide(self.hWnd)

		def OnToggleChangeCH(self):
			self.__ClickChangeCH()

		def __RefreshQuickChannels(self):
			cur = net.GetConnectedChannelNum()
			# core99 maps report channel 99 (not 1-4) and disallow CH switching.
			canSwitch = (1 <= cur <= 4)
			for i in xrange(len(self.quickChBtnList)):
				btn = self.quickChBtnList[i]
				if not canSwitch:
					btn.SetUp()
					btn.Disable()
				elif (i + 1) == cur:
					btn.Down()
					btn.Disable()
				else:
					btn.SetUp()
					btn.Enable()

		def __ClickQuickChannel(self, idx):
			cur = net.GetConnectedChannelNum()
			if not (1 <= cur <= 4):
				return
			if idx == cur:
				return
			net.SendChatPacket("/channel_switch %d" % idx)
			self.Close()

	def __init__(self):
		if app.USE_INGAME_CHANGE_CHANNEL:
			self.switchCHDlg = None
			self.quickChBtnList = []

		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.__Initialize()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __Initialize(self):
		self.eventOpenHelpWindow = None
		if app.ENABLE_GAMEOPTION_RENEWAL:
			self.gameOptionDlgNew = None
		else:
			self.systemOptionDlg = None
			self.gameOptionDlg = None

		self.AdvancedskyboxOptionDlg = None

	def LoadDialog(self):
		self.__LoadSystemMenu_Default()

	def __LoadSystemMenu_Default(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/systemdialog.py")
		
		if app.ENABLE_GAMEOPTION_RENEWAL:
			self.GetChild("options_element").SAFE_SetEvent(self.__ClickGameOptionButtonNew)
		else:
			self.GetChild("system_option_button").SAFE_SetEvent(self.__ClickSystemOptionButton)
			self.GetChild("game_option_button").SAFE_SetEvent(self.__ClickGameOptionButton)

		# self.GetChild("advanced_skybox_option_button").SAFE_SetEvent(self.__ClickAdvancedSkyboxOptionButton)

		self.GetChild("change_button").SAFE_SetEvent(self.__ClickChangeCharacterButton)
		self.GetChild("logout_button").SAFE_SetEvent(self.__ClickLogOutButton)
		self.GetChild("exit_button").SAFE_SetEvent(self.__ClickExitButton)
		self.GetChild("help_button").SAFE_SetEvent(self.__ClickHelpButton)
		self.GetChild("cancel_button").SAFE_SetEvent(self.Close)
		self.GetChild("mall_button").SAFE_SetEvent(self.__ClickInGameShopButton)

		if app.USE_INGAME_CHANGE_CHANNEL:
			tmp = self.GetChild("movechannel_button")
			tmp.SetEvent(ui.__mem_func__(self.__ClickChangeCH))
			self.switchCHBtn = tmp

			self.quickChBtnList = []
			for i in xrange(1, 5):
				btn = self.GetChild("quickch_button_%d" % i)
				btn.SetEvent(ui.__mem_func__(self.__ClickQuickChannel), i)
				self.quickChBtnList.append(btn)
		else:
			self.GetChild("movechannel_button").Hide()
			for i in xrange(1, 5):
				self.GetChild("quickch_button_%d" % i).Hide()

	def Destroy(self):
		if app.USE_INGAME_CHANGE_CHANNEL:
			if self.switchCHDlg:
				self.switchCHDlg.Destroy()
				del self.switchCHDlg
				self.switchCHDlg = None

			if self.switchCHBtn:
				self.switchCHBtn.SetEvent(None)
				self.switchCHBtn = None

			for btn in self.quickChBtnList:
				btn.SetEvent(None)
			self.quickChBtnList = []

		self.ClearDictionary()
		if app.ENABLE_GAMEOPTION_RENEWAL:
			if self.gameOptionDlgNew:
				self.gameOptionDlgNew.Destroy()
				self.gameOptionDlgNew = None
		else:
			if self.gameOptionDlg:
				self.gameOptionDlg.Destroy()
			
			if self.systemOptionDlg:
				self.systemOptionDlg.Destroy()

		if self.AdvancedskyboxOptionDlg:
			self.AdvancedskyboxOptionDlg.Destroy()
		
		self.__Initialize()

	def SetOpenHelpWindowEvent(self, event):
		self.eventOpenHelpWindow = event

	def OpenDialog(self):
		if app.USE_INGAME_CHANGE_CHANNEL:
			self.__RefreshQuickChannels()
		self.Show()

	def __ClickChangeCharacterButton(self):
		self.Close()

		net.ExitGame()

	def __OnClosePopupDialog(self):
		self.popup = None

	def __ClickLogOutButton(self):
		self.Close()
		net.LogOutGame()

	def __ClickExitButton(self):
		self.Close()
		net.ExitApplication()

	if app.ENABLE_GAMEOPTION_RENEWAL:
		def __ClickGameOptionButtonNew(self):
			self.Close()
			if not self.gameOptionDlgNew:
				self.gameOptionDlgNew = uiadvancedgameoptions.AdvancedGameOptionsWindow()
			
			self.gameOptionDlgNew.Show()
	else:
		def __ClickSystemOptionButton(self):
			self.Close()
			if not self.systemOptionDlg:
				self.systemOptionDlg = uisystemoption.OptionDialog()
			
			self.systemOptionDlg.Show()

		def __ClickGameOptionButton(self):
			self.Close()
			if not self.gameOptionDlg:
				self.gameOptionDlg = uigameoption.OptionDialog()
			
			self.gameOptionDlg.Show()

	def __ClickAdvancedSkyboxOptionButton(self):
		self.Close()

		if not self.AdvancedskyboxOptionDlg:
			self.AdvancedskyboxOptionDlg = uiadvancedskyboxoption.OptionDialog()

		self.AdvancedskyboxOptionDlg.Show()

	def __ClickHelpButton(self):
		self.Close()

		if None != self.eventOpenHelpWindow:
			self.eventOpenHelpWindow()

	def __ClickInGameShopButton(self):
		self.Close()
		# net.SendChatPacket("/in_game_mall")

		if app.ENABLE_ITEMSHOP:
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.OpenItemShopWindow()

	if app.USE_INGAME_CHANGE_CHANNEL:
		def Hide(self):
			if self.switchCHDlg:
				if self.switchCHDlg.IsShow():
					self.switchCHDlg.Close()

			wndMgr.Hide(self.hWnd)

	def Close(self):
		self.Hide()
		return True

	def OnBlockMode(self, mode):
		if app.ENABLE_GAMEOPTION_RENEWAL:
			uiadvancedgameoptions.blockMode = mode
			if self.gameOptionDlgNew:
				self.gameOptionDlgNew.OnBlockMode(mode)
		else:
			uigameoption.blockMode = mode
			if self.gameOptionDlg:
				self.gameOptionDlg.OnBlockMode(mode)

	def OnChangePKMode(self):
		if app.ENABLE_GAMEOPTION_RENEWAL:
			if self.gameOptionDlgNew:
				self.gameOptionDlgNew.OnChangePKMode()
		else:
			if self.gameOptionDlg:
				self.gameOptionDlg.OnChangePKMode()

	def OnPressExitKey(self):
		self.Close()
		return True

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def GetSystemOption(self):
		if app.ENABLE_GAMEOPTION_RENEWAL:
			return self.gameOptionDlgNew
		else:
			return self.systemOptionDlg

	def HideAllSystemOptioin(self):
		if app.ENABLE_GAMEOPTION_RENEWAL:
			if self.gameOptionDlgNew:
				self.gameOptionDlgNew.Hide()
		else:
			if self.systemOptionDlg:
				self.systemOptionDlg.Hide()
			
			if self.gameOptionDlg:
				self.gameOptionDlg.Hide()

	def ShowAllSystemOptioin(self):
		if app.ENABLE_GAMEOPTION_RENEWAL:
			if self.gameOptionDlgNew and self.gameOptionDlgNew.IsShow():
				self.gameOptionDlgNew.Show()
		else:
			if self.systemOptionDlg and self.systemOptionDlg.IsShowWindow():
				self.systemOptionDlg.Show()
			
			if self.gameOptionDlg and self.gameOptionDlg.IsShowWindow():
				self.gameOptionDlg.Show()
