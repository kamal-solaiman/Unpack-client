# coding: latin_1

import app
import chr
import chrmgr
import net
import player

import dbg
import snd
import background
import playersettingmodule

import ui
import uiphasecurtain

import localeinfo

class PopupDialog(ui.ScriptWindow):
	def __init__(self):
		#print "NEW POPUP DIALOG ----------------------------------------------------------------------------"
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

	def __del__(self):
		self.CloseEvent = 0

	def __del__(self):
		#print "---------------------------------------------------------------------------- DELETE POPUP DIALOG "
		ui.ScriptWindow.__del__(self)

	def LoadDialog(self):
		PythonScriptLoader = ui.PythonScriptLoader()
		PythonScriptLoader.LoadScriptFile(self, "UIScript/PopupDialog.py")

	def Open(self, Message, event = 0, ButtonName = localeinfo.UI_CANCEL):
		if True == self.IsShow():
			self.Close()

		self.Lock()
		self.SetTop()
		self.CloseEvent = event

		AcceptButton = self.GetChild("accept")
		AcceptButton.SetText(ButtonName)
		AcceptButton.SetEvent(ui.__mem_func__(self.Close))

		self.GetChild("message").SetText(Message)

		self.Show()

	def Close(self):
		if False == self.IsShow():
			self.CloseEvent = 0
			return

		self.Unlock()
		self.Hide()

		try:
			if 0 != self.CloseEvent:
				self.CloseEvent()
				self.CloseEvent = 0
		except:
			pass

	def Destroy(self):
		self.Close()
		self.ClearDictionary()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnIMEReturn(self):
		self.Close()
		return True

##
## Main Stream
##
class MainStream(object):
	isChrData = 0

	def __init__(self):
		#print "NEWMAIN STREAM ----------------------------------------------------------------------------"
		net.SetHandler(self)
		net.SetTCPRecvBufferSize(153600)
		if app.ENABLE_VOICE_CHAT:
			net.SetTCPSendBufferSize(1024 * 12) # 12kb
		else:
			net.SetTCPSendBufferSize(4096)
		net.SetUDPRecvBufferSize(4096)

		self.id = ""
		self.pwd = ""
		self.addr = ""
		self.port = 0
		self.account_addr = 0
		self.account_port = 0
		self.slot = 0
		self.isAutoSelect = 0
		self.isAutoLogin = 0

		self.curtain = 0
		self.curPhaseWindow = 0
		self.newPhaseWindow = 0

	def __del__(self):
		import uiquest
		if uiquest.QuestDialog:
			if uiquest.QuestDialog.__dict__.has_key("QuestCurtain"):
				del uiquest.QuestDialog.QuestCurtain

	def Destroy(self):
		if self.curPhaseWindow:
			self.curPhaseWindow.Close()
			self.curPhaseWindow = 0

		if self.newPhaseWindow:
			self.newPhaseWindow.Close()
			self.newPhaseWindow = 0

		self.popupWindow.Destroy()
		self.popupWindow = 0

		self.curtain = 0

	def Create(self):
		self.CreatePopupDialog()

		self.curtain = uiphasecurtain.PhaseCurtain()

	# def SetPhaseWindow(self, newPhaseWindow):
		# if self.newPhaseWindow:
			# self.__ChangePhaseWindow()

		# self.newPhaseWindow = newPhaseWindow
		# if self.curPhaseWindow:
			# self.curtain.FadeOut(self.__ChangePhaseWindow)
		# else:
			# self.__ChangePhaseWindow()
			
	# def SetPhaseWindow(self, newPhaseWindow):
		# import dbg
		# dbg.TraceError(str([self.curPhaseWindow.__class__.__name__, newPhaseWindow.__class__.__name__ ]))
		# self.newPhaseWindow = newPhaseWindow
		# self.__ChangePhaseWindow()
		
	def SetPhaseWindow(self, newPhaseWindow):
		if self.newPhaseWindow:
			self.__ChangePhaseWindow()

		self.newPhaseWindow = newPhaseWindow
		if self.curPhaseWindow:
			curName = self.curPhaseWindow.__class__.__name__
			newName = newPhaseWindow.__class__.__name__
			skipFade = newName in ("LoginWindow", "SelectEmpireWindow") \
				or (curName == 'GameWindow' and newName == 'LoadingWindow') \
				or (curName == 'LoadingWindow' and newName == 'GameWindow')
			if not skipFade and curName == 'SelectCharacterWindow' and newName == 'LoadingWindow':
				import constinfo
				skipFade = getattr(constinfo, 'FAST_LOGIN_ATTEMPTED', False)
			if skipFade:
				self.__ChangePhaseWindow()
			else:
				self.curtain.FadeOut(self.__ChangePhaseWindow)
		else:
			self.__ChangePhaseWindow()

	def __ChangePhaseWindow(self):
		oldPhaseWindow = self.curPhaseWindow
		newPhaseWindow = self.newPhaseWindow
		self.curPhaseWindow = 0
		self.newPhaseWindow = 0

		if oldPhaseWindow:
			oldPhaseWindow.Close()

		if newPhaseWindow:
			newPhaseWindow.Open()

		self.curPhaseWindow = newPhaseWindow

		if self.curPhaseWindow:
			self.curtain.FadeIn()
		else:
			app.Exit()

	def CreatePopupDialog(self):
		self.popupWindow = PopupDialog()
		self.popupWindow.LoadDialog()
		self.popupWindow.SetCenterPosition()
		self.popupWindow.Hide()

	## SelectPhase
	##########################################################################################
	def SetLogoPhase(self):
		net.Disconnect()

		import intrologo
		self.SetPhaseWindow(intrologo.LogoWindow(self))

	def SetLoginPhase(self):
		net.Disconnect()

		import intrologin
		self.SetPhaseWindow(intrologin.LoginWindow(self))

	def SameLogin_SetLoginPhase(self):
		net.Disconnect()

		import intrologin
		introInst = intrologin.LoginWindow(self)
		self.SetPhaseWindow(introInst)
		introInst.SameLogin_OpenUI()

	def SetSelectEmpirePhase(self):
		try:
			import introempire
			self.SetPhaseWindow(introempire.SelectEmpireWindow(self))
		except:
			import exception
			exception.Abort("networkmodule.SetSelectEmpirePhase")

	def SetReselectEmpirePhase(self):
		try:
			import introempire
			self.SetPhaseWindow(introempire.ReselectEmpireWindow(self))
		except:
			import exception
			exception.Abort("networkmodule.SetReselectEmpirePhase")

	def SetSelectCharacterPhase(self):
		try:
			localeinfo.LoadLocaleData()
			self.popupWindow.Close()

			if app.ENABLE_SELECT_RENEWAL:
				import new_introselect
				self.SetPhaseWindow(new_introselect.SelectCharacterWindow(self))
			else:
				import introselect
				self.SetPhaseWindow(introselect.SelectCharacterWindow(self))
		except:
			import exception
			exception.Abort("networkmodule.SetSelectCharacterPhase")

	def SetCreateCharacterPhase(self):
		try:
			if app.ENABLE_CREATE_RENEWAL:
				import new_introcreate
				self.SetPhaseWindow(new_introcreate.CreateCharacterWindow(self))
			else:
				import introcreate
				self.SetPhaseWindow(introcreate.CreateCharacterWindow(self))
		except:
			import exception
			exception.Abort("networkmodule.SetCreateCharacterPhase")

	def SetTestGamePhase(self, x, y):
		try:
			import introloading
			loadingPhaseWindow = introloading.LoadingWindow(self)
			loadingPhaseWindow.LoadData(x, y)
			self.SetPhaseWindow(loadingPhaseWindow)
		except:
			import exception
			exception.Abort("networkmodule.SetLoadingPhase")

	def SetLoadingPhase(self):
		try:
			import introloading
			self.SetPhaseWindow(introloading.LoadingWindow(self))
		except:
			import exception
			exception.Abort("networkmodule.SetLoadingPhase")

	def SetGamePhase(self):
		try:
			import game
			if app.ENABLE_FAST_WARP_UI:
				# Send the in-game "ready" packet BEFORE the heavy GameWindow/Interface
				# construction: the server spawns us and streams the surrounding world
				# while the UI is built (packets are processed after this call returns,
				# when all phase windows are registered).
				net.SendEnterGamePacket()
			self.popupWindow.Close()
			self.SetPhaseWindow(game.GameWindow(self))
		except:
			raise
			import exception
			exception.Abort("networkmodule.SetGamePhase")

	################################
	# Functions used in python

	## Login
	def Connect(self):
		import constinfo
		if app.LOGIN_COUNT_DOWN_UI_MODIFY:
			result = False
			if constinfo.KEEP_ACCOUNT_CONNETION_ENABLE:
				result = net.ConnectToAccountServer(self.addr, self.port, self.account_addr, self.account_port)
			else:
				result = net.ConnectTCP(self.addr, self.port)

			return result
		else:
			if constinfo.KEEP_ACCOUNT_CONNETION_ENABLE:
				net.ConnectToAccountServer(self.addr, self.port, self.account_addr, self.account_port)
			else:
				net.ConnectTCP(self.addr, self.port)

		#net.ConnectUDP(IP, Port)

	def SetConnectInfo(self, addr, port, account_addr = 0, account_port = 0):
		self.addr = addr
		self.port = port
		self.account_addr = account_addr
		self.account_port = account_port

	def GetConnectAddr(self):
		return self.addr

	def SetLoginInfo(self, id, pwd):
		self.id = id
		self.pwd = pwd
		net.SetLoginInfo(id, pwd)

	def CancelEnterGame(self):
		pass

	## Select
	def SetCharacterSlot(self, slot):
		self.slot = slot

	def GetCharacterSlot(self):
		return self.slot

	## Empty
	def EmptyFunction(self):
		pass
