# coding: latin_1

import app
import net
import os
import ui
import snd
import wndMgr
import musicinfo
import systemSetting
import localeinfo
import constinfo
import ime
import ServerStateChecker
import _winreg
import binascii

from _weakref import proxy

REGISTER_URL = "https://lava2.ae/ab"

serverList = {
	1: {
		"name" : localeinfo.TITLE_SERVER_1,
		"ip" : "92.246.89.164",
		"login" : 30091,
		"mark" : 30125,
		"channels" : [30093, 30101, 30109, 30117],
	},

	2: {
		"name" : localeinfo.TITLE_SERVER_2,
		"ip" : "92.246.89.164",
		"login" : 30091,
		"mark" : 30125,
		"channels" : [30093, 30101, 30109, 30117],
	},
}

REG_PATCH = r"SOFTWARE\Classic2"

class LoginWindow(ui.ScriptWindow):
	def __init__(self, stream):
		ui.ScriptWindow.__init__(self)
		
		net.SetPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(self)

		self.stream = stream

		try:
			self.server_id = int(LoadWinAccountReg("server"))
		except:
			self.server_id = 1

		self.channel_id = 0

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		
		net.ClearPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(0)

	def Close(self):
		if (self.stream.popupWindow):
			self.stream.popupWindow.Close()

		ServerStateChecker.Initialize(self)

		self.Hide()
		app.HideCursor()
		ime.ClearExceptKey()
		
	def OnPressExitKey(self):
		if (self.stream.popupWindow):
			self.stream.popupWindow.Close()
			
		self.stream.SetPhaseWindow(0)
		
		return True

	def Open(self):
		ServerStateChecker.Create(self)

		self.loginFailureMsgDict = {
			"ALREADY"	: localeinfo.LOGIN_FAILURE_ALREAY,
			"NOID"		: localeinfo.LOGIN_FAILURE_NOT_EXIST_ID,
			"WRONGPWD"	: localeinfo.LOGIN_FAILURE_WRONG_PASSWORD,
			"FULL"		: localeinfo.LOGIN_FAILURE_TOO_MANY_USER,
			"SHUTDOWN"	: localeinfo.LOGIN_FAILURE_SHUTDOWN,
			"REPAIR"	: localeinfo.LOGIN_FAILURE_REPAIR_ID,
			"BLOCK"		: localeinfo.LOGIN_FAILURE_BLOCK_ID,
			"WRONGMAT"	: localeinfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER,
			"QUIT"		: localeinfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER_TRIPLE,
			"BESAMEKEY"	: localeinfo.LOGIN_FAILURE_BE_SAME_KEY,
			"NOTAVAIL"	: localeinfo.LOGIN_FAILURE_NOT_AVAIL,
			"NOBILL"	: localeinfo.LOGIN_FAILURE_NOBILL,
			"BLKLOGIN"	: localeinfo.LOGIN_FAILURE_BLOCK_LOGIN,
			"WEBBLK"	: localeinfo.LOGIN_FAILURE_WEB_BLOCK,
			"DEVLIMIT"	: localeinfo.LOGIN_FAILURE_DEVICE_LIMIT,
		}

		self.loginFailureFuncDict = {
			"WRONGPWD"	: localeinfo.LOGIN_FAILURE_WRONG_PASSWORD,
			"WRONGMAT"	: localeinfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER,
			"QUIT"		: app.Exit,
		}

		self.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())
		self.SetWindowName("LoginWindow")
		
		self.__LoadScript("uiscript/login_window.py")
		
		ime.AddExceptKey(91)
		ime.AddExceptKey(93)

		self.OnClickChannelButton(0)
		self.__RefreshSavedAccount()
		self.OnClickServerButton(self.server_id - 1)
		self.OnClickArrowButton(0)

		self.Show()

		app.ShowCursor()

	def __LoadScript(self, fileName):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, fileName)
			
		except:
			import exception
			exception.Abort("LoginWindow.__LoadScript.LoadObject")

		try:
			self.serverList = []
			for i in xrange(2):
				self.serverList.append(self.GetChild2("server_button_%02d" % (i + 1)))
			
			self.channelList = []
			self.channelStatusList = []
			for i in xrange(4):
				self.channelList.append(self.GetChild2("channel_button_%02d" % (i + 1)))
				self.channelStatusList.append({
					"off": self.GetChild2("channel_status_off_%02d" % (i + 1)),
					"on": self.GetChild2("channel_status_on_%02d" % (i + 1)),
				})

			map(lambda x: x["on"].Hide(), self.channelStatusList)

			self.accountWindowList = []
			for i in xrange(2):
				self.accountWindowList.append(self.GetChild2("account_window_%02d" % (i + 1)))

			self.id_editline					= self.GetChild2("id")
			self.pw_editline					= self.GetChild2("pwd")
			
			if localeinfo.IsARABIC():
				self.GetChild2("login_input").SetScale(-1.0, 1.0)
				self.GetChild2("login_input").SetRenderingRect(-1.0, 0.0, 1.0, 0.0)
				
				self.GetChild2("password_input").SetScale(-1.0, 1.0)
				self.GetChild2("password_input").SetRenderingRect(-1.0, 0.0, 1.0, 0.0)

			self.arrowLeft						= self.GetChild2("arrow_left_button")
			self.arrowRight						= self.GetChild2("arrow_right_button")

			self.login_button					= self.GetChild2("login_button")
			self.register_button				= self.GetChild2("register_button")
			self.exit_button					= self.GetChild2("exit_button")

		except:
			import exception
			exception.Abort("LoginWindow.__LoadScript.LoadElements")

		for i, server in enumerate(self.serverList):
			server.SetEvent(ui.__mem_func__(self.OnClickServerButton), i)

		for i, channel in enumerate(self.channelList):
			channel.SetEvent(ui.__mem_func__(self.OnClickChannelButton), i)
		
		self.accountList = []
		for i in xrange(8):
			loadButton = self.GetChild2("account_load_button_%02d" % (i + 1))
			deleteButton = self.GetChild2("account_delete_button_%02d" % (i + 1))
			slot = self.GetChild2("account_text_%02d" % (i + 1))

			loadButton.SetEvent(ui.__mem_func__(self.__OnClickAccountConnectButton), i)
			deleteButton.SetEvent(ui.__mem_func__(self.__OnClickAccountDeleteButton), i)
			self.accountList.append({
				"slot": slot,
				"load_button": loadButton,
				"delete_button": deleteButton,
			})

		self.id_editline.SetTabEvent(ui.__mem_func__(self.pw_editline.SetFocus))
		self.id_editline.SetReturnEvent(ui.__mem_func__(self.pw_editline.SetFocus))
		self.pw_editline.SetTabEvent(ui.__mem_func__(self.id_editline.SetFocus))
		self.pw_editline.SetReturnEvent(ui.__mem_func__(self.OnClickLoginButton))

		self.arrowLeft.SetEvent(ui.__mem_func__(self.OnClickArrowButton), 0)
		self.arrowRight.SetEvent(ui.__mem_func__(self.OnClickArrowButton), 1)

		self.login_button.SetEvent(ui.__mem_func__(self.OnClickLoginButton))
		self.register_button.SetEvent(ui.__mem_func__(self.OnClickRegisterButton))
		self.exit_button.SetEvent(ui.__mem_func__(self.OnPressExitKey))

		self.id_editline.SetFocus()

	def GetChannel(self):
		channelID = 1
		
		try:
			file = open("channel.inf")
			lines = file.readlines()
			if len(lines) > 0:
				tokens = lines[0].split()
				channelID = int(tokens[1])
			
			file.close()
		except:
			pass
		
		return channelID

	def OnRefreshChannelInfo(self, channelID = -1):
		if channelID == -1:
			channelID = self.GetChannel()
		
		try:
			file = open("channel.inf", "w")
			file.write("%d %d 0" % (self.server_id, channelID))
		except Exception as e:
			import dbg
			dbg.TraceError(str(e))

	def OnClickServerButton(self, index):
		map(ui.RadioButton.SetUp, self.serverList)
		self.serverList[index].Down()

		self.server_id = index + 1

		ServerStateChecker.Initialize();

		# import dbg
		# for port in range(len(serverList[self.server_id]["channels"])):
			# dbg.TraceError("i %d, ip %s, port %d" % (port, serverList[self.server_id]["ip"], serverList[self.server_id]["channels"][port]))
			# ServerStateChecker.AddChannel(port, serverList[self.server_id]["ip"], serverList[self.server_id]["channels"][port])

		ServerStateChecker.Request()

		self.OnClickChannelButton(self.channel_id)
		CreateWinAccountReg("server", "%s" % self.server_id)
		self.OnRefreshChannelInfo()

	def OnClickChannelButton(self, channel):
		server_ip = serverList[self.server_id]["ip"]
		server_ch = serverList[self.server_id]["channels"][channel]
		server_login = serverList[self.server_id]["login"]
		server_mark = serverList[self.server_id]["mark"]
		server_name = serverList[self.server_id]["name"]
		
		for channel_button in self.channelList:
			channel_button.SetUp()
		
		self.channelList[channel].Down()
		self.channel_id = channel
		
		self.stream.SetConnectInfo(server_ip, server_ch, server_ip, server_login)

		net.SetMarkServer(server_ip, server_mark)
		app.SetGuildMarkPath("mark.tga")
		app.SetGuildSymbolPath("")

		net.SetServerInfo("%s - CH%s" % (server_name, channel + 1))
		self.OnRefreshChannelInfo(channel + 1)

	def OnClickArrowButton(self, index):
		map(ui.Window.Hide, self.accountWindowList)
		self.accountWindowList[index].Show()

	def OnClickLoginButton(self, id="", pwd=""):
		text_id = id if len(id) else self.id_editline.GetText()
		text_pw = pwd if len(pwd) else self.pw_editline.GetText()

		if not self.CheckTextSize(text_id):
			self.PopupNotifyMessage(localeinfo.LOGIN_INPUT_ID, self.EmptyFunc)
			return False

		if not self.CheckTextSize(text_pw):
			self.PopupNotifyMessage(localeinfo.LOGIN_INPUT_PASSWORD, self.EmptyFunc)
			return False

		self.Connect(text_id, text_pw)

	def OnClickRegisterButton(self):
		os.system("start %s" % REGISTER_URL)

	def OnClickSaveButton(self, slot):
		text_id = self.id_editline.GetText()
		text_pw = self.pw_editline.GetText()

		if not self.CheckTextSize(text_id):
			self.PopupNotifyMessage(localeinfo.INTERFACE_TEXT_3, self.EmptyFunc)
			return False

		if not self.CheckTextSize(text_pw):
			self.PopupNotifyMessage(localeinfo.INTERFACE_TEXT_4, self.EmptyFunc)
			return False

		if LoadWinAccountReg("account_%s" % slot):
			self.PopupNotifyMessage(localeinfo.INTERFACE_TEXT_5, self.EmptyFunc)
			return False

		CreateWinAccountReg("account_%s" % slot, "%s|%s" % (text_id, text_pw))

		if LoadWinAccountReg("account_%s" % slot):
			self.PopupNotifyMessage(localeinfo.INTERFACE_TEXT_6, self.EmptyFunc)
			self.LoadSavedAccounts()
		else:
			self.PopupNotifyMessage(localeinfo.INTERFACE_TEXT_7, self.EmptyFunc)
			return False

	def OnClickLoadButton(self, slot):
		login = LoadWinAccountReg("account_%s" % slot).split("|")[0]
		password = LoadWinAccountReg("account_%s" % slot).split("|")[1]

		self.id_editline.SetText(login)
		self.pw_editline.SetText(password)

		self.Connect(login, password)

	def OnClickRemoveButton(self, slot):
		RemoveWinAccountReg("account_%s" % slot)

		if not LoadWinAccountReg("account_%s" % slot):
			self.PopupNotifyMessage(localeinfo.INTERFACE_TEXT_8, self.EmptyFunc)
			self.LoadSavedAccounts()
		else:
			self.PopupNotifyMessage(localeinfo.INTERFACE_TEXT_9, self.EmptyFunc)
			return False

	def OnConnectFailure(self):
		self.PopupNotifyMessage(localeinfo.LOGIN_CONNECT_FAILURE, self.EmptyFunc)

	def OnLoginStart(self):
		self.PopupDisplayMessage(localeinfo.LOGIN_PROCESSING)

	def OnLoginFailure(self, error):
		try:
			loginFailureMsg = self.loginFailureMsgDict[error]
			
		except KeyError:
			loginFailureMsg = localeinfo.LOGIN_FAILURE_UNKNOWN + error
			
		loginFailureFunc = self.loginFailureFuncDict.get(error, self.EmptyFunc)

		self.PopupNotifyMessage(loginFailureMsg, loginFailureFunc)

	def Connect(self, login, password):
		if app.USE_SEQUENCE:
			net.SetPacketSequenceMode()

		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(localeinfo.LOGIN_CONNETING, self.EmptyFunc, localeinfo.UI_CANCEL)

		self.stream.SetLoginInfo(login, password)
		self.stream.Connect()

	def PopupDisplayMessage(self, msg):
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg)

	def PopupNotifyMessage(self, msg, func = 0):
		if (not func):
			func = self.EmptyFunc

		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, func, localeinfo.UI_OK)

	def EmptyFunc(self):
		pass

	def NotifyChannelState(self, addrKey, state, count=0):
		import dbg
		dbg.TraceError("witam addr key %d, state %d, count %d" % (addrKey, state, count))
	
		channelStatus = self.channelStatusList[addrKey]
		if status > 0:
			channelStatus["off"].Hide()
			channelStatus["on"].Show()
		else:
			channelStatus["off"].Show()
			channelStatus["on"].Hide()

	def CheckTextSize(self, text):
		if len(text) == 0:
			return False
		else:
			return True

	def ReturnSecondServer(self):
		if self.server_id == 1:
			return 2
		else:
			return 1

	def OnUpdate(self):
		ServerStateChecker.Update()

	def __OnClickAccountSaveButton(self, index):
		id = self.id_editline.GetText()
		pwd = self.pw_editline.GetText()

		login = LoadWinAccountReg("login%d" % index)
		if login:
			self.PopupNotifyMessage(localeinfo.LOGIN_SAVE_FULL)
			return

		if len(id) == 0:
			self.PopupNotifyMessage(localeinfo.LOGIN_INPUT_ID, self.SetIDEditLineFocus)
			return

		if len(pwd) == 0:
			self.PopupNotifyMessage(localeinfo.LOGIN_INPUT_PASSWORD, self.SetPasswordEditLineFocus)
			return

		CreateWinAccountReg("login%d" % index, id)
		CreateWinAccountReg("password%d" % index, pwd)
		self.PopupNotifyMessage(localeinfo.LOGIN_DATA_SAVE)

		self.__RefreshSavedAccount()

	def __OnClickAccountConnectButton(self, index, keyboard=False):
		id = LoadWinAccountReg("login%d" % index)
		pwd = LoadWinAccountReg("password%d" % index)

		if keyboard:
			if id and pwd:
				self.Connect(id, pwd)
			return

		if not id and not pwd:
			self.__OnClickAccountSaveButton(index)
		else:
			self.OnClickLoginButton(id, pwd)

	def __OnClickAccountDeleteButton(self, index):
		CreateWinAccountReg("login%d" % index, "")
		CreateWinAccountReg("password%d" % index, "")

		self.__RefreshSavedAccount()

		self.PopupNotifyMessage(localeinfo.LOGIN_DATA_DELETED)

	def __RefreshSavedAccount(self):
		for i in xrange(len(self.accountList)):
			id = LoadWinAccountReg("login%d" % i)

			if not id:
				id = localeinfo.LOGIN_EMPTY_SLOT
				self.accountList[i]["delete_button"].Hide()
			else:
				self.accountList[i]["delete_button"].Show()

			self.accountList[i]["slot"].SetText("F%d. %s" % ((i + 1), id))

	def OnKeyDown(self, key):
		#import dbg
		#dbg.TraceError("{} was taken".format(key))
		if key in {app.DIK_F1, app.DIK_F2, app.DIK_F3, app.DIK_F4, app.DIK_F5, app.DIK_F6 }:
			self.__OnClickAccountConnectButton(key - app.DIK_F1, True)
			#dbg.TraceError("{} was sent".format(key - app.DIK_F1))
		
		return True

def LoadWinAccountReg(name):
	try:
		registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATCH, 0, _winreg.KEY_READ)
		value, regtype = _winreg.QueryValueEx(registry_key, name)
		_winreg.CloseKey(registry_key)

		return str(binascii.a2b_base64(value))

	except WindowsError:
		return None

def CreateWinAccountReg(name, value):
	try:
		_winreg.CreateKey(_winreg.HKEY_CURRENT_USER, REG_PATCH)
		registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATCH, 0, _winreg.KEY_WRITE)

		value = binascii.b2a_base64(value)
		_winreg.SetValueEx(registry_key, name, 0, _winreg.REG_SZ, value)
		_winreg.CloseKey(registry_key)

		return True

	except WindowsError:
		return False

def RemoveWinAccountReg(name):
	try:
		registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATCH, 0, _winreg.KEY_ALL_ACCESS)
		_winreg.DeleteValue(registry_key, name)
		_winreg.CloseKey(registry_key)
		
		return True
	
	except WindowsError:
		return False