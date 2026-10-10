# coding: latin_1

import app
import net
import player

import ui
import chat
import math
import wndMgr
import background
import constinfo
import grp
import item
import event
import localeinfo

class RoutesPvPWindow(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.isLoaded = False
		self.interface = None
		self.__LoadWindow()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadWindow(self):
		try:
			PythonScriptLoader = ui.PythonScriptLoader()
			PythonScriptLoader.LoadScriptFile(self, "uiscript/routespvp.py")
		except:
			import exception
			exception.Abort("RoutesPvPWindow.LoadWindow.LoadObject")
		
		self.board = self.GetChild("board")
		self.board.SetCloseEvent(ui.__mem_func__(self.Close))
		
		self.RewardButton = self.GetChild("type0button")
		self.RewardButton.SetEvent(ui.__mem_func__(self.__ObtainReward))
		
		self.TextPuntos = self.GetChild("textpuntos")

		self.globalProgress = RoutesPvPProgressBar()
		self.globalProgress.SetParent(self.board)
		self.globalProgress.SetSize(460, 25)
		self.globalProgress.SetPosition(-10, 80)
		self.globalProgress.SetWindowHorizontalAlignCenter()
		self.globalProgress.SetProgress(0, 3500, 0)
		self.globalProgress.Show()
		
		self.isLoaded = True

	def Destroy(self):
		self.Close()
		self.ClearDictionary()
		
	def Close(self):
		self.Hide()
		return TRUE
		
	def OnPressEscapeKey(self):
		self.Close()
		return TRUE
		
	def OnPressExitKey(self):
		self.Close()
		return TRUE

	def Open(self):
		if self.IsShow():
			self.Close()
		else:
			self.SetCenterPosition()
			self.SetTop()
			self.Show()
			net.SendChatPacket('/routes_pvp_get_points')
			
	def BindInterface(self, interface):
		self.interface = interface

	def __ObtainReward(self):
		if self.puntos >= 500:
			net.SendChatPacket('/routes_pvp_obtain_reward')
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.ROUTES_PVP_LESS)


	def OnUpdate(self):
		self.puntos = constinfo.RoutesPvPSystem['puntos']
		self.recompensa = constinfo.RoutesPvPSystem['recompensa']
		self.progress = self.recompensa*500
		self.globalProgress.SetProgress(self.progress, 3500, self.puntos)
		self.TextPuntos.SetText("{} : {}".format(localeinfo.PVP_ROUTES_POINTS,self.puntos))

class RoutesPvPProgressBar(ui.Window):

	BACKGROUND_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
	DARK_COLOR = grp.GenerateColor(0.4, 0.4, 0.4, 1.0)
	
	#PROGRESS_COLOR = grp.GenerateColor(0.25, 1.0, 0.75, 1.0)
	PROGRESS_COLOR = grp.GenerateColor(0, 0.9, 1.0, 1.0)
	PROGRESS_COLOR_2 = grp.GenerateColor(0.5, 1.0, 1.0, 0.95)
	FINISHED_COLOR = grp.GenerateColor(0.0, 1.0, 0.0, 0.5)

	def __init__(self, layer = "UI"):
		ui.Window.__init__(self, layer)

		self.width = 0
		self.height = 0		
		self.progress = 0
		self.isFinished = False
		
		self.textLine = None
		self.textLineExtra = None
		
	def __del__(self):
		ui.Window.__del__(self)

	def SetSize(self, width, height):
		ui.Window.SetSize(self, width, height)
		self.width = width
		self.height = height

	def SetProgress(self, current, max, extra):
		try:
			self.progress = min(math.ceil((float(current)/float(max))*100.00), 100)
			if (extra+current) > 3500:
				extra = 3500-current
			self.progressextra = min(math.ceil((float(current+extra)/float(max))*100.00), 100)
		except:
			self.progress = 0
			self.progressextra = 0
		if self.progress == 100:
			self.isFinished = True
		else:
			self.isFinished = False
		
		if not self.textLine:		
			textLine = ui.TextLine()
			textLine.SetParent(self)
			textLine.SetOutline()
			textLine.Show()
			self.textLine = textLine
		
		if current > max:
			self.textLine.SetText('%d/%d' % (max, max))
		else:
			self.textLine.SetText('%d/%d' % (current, max))
		self.textLine.SetPosition(170, self.GetHeight()/2)
		self.textLine.SetHorizontalAlignCenter()
		self.textLine.SetWindowHorizontalAlignCenter()
		self.textLine.SetVerticalAlignCenter()
		
	def SetText(self, text):
		if not self.textLineExtra:		
			textLineExtra = ui.TextLine()
			textLineExtra.SetParent(self)
			textLineExtra.SetPosition(12, self.GetHeight()/2)
			textLineExtra.SetVerticalAlignCenter()
			textLineExtra.SetOutline()
			textLineExtra.Show()
			self.textLineExtra = textLineExtra
		
		self.textLineExtra.SetText('%s' % text)
		
	def SetProgressPosition(self, x):
		self.textLine.SetPosition(x, self.GetHeight()/2)

	def OnRender(self):
		xRender, yRender = self.GetGlobalPosition()
		
		widthRender = self.width
		heightRender = self.height
		grp.SetColor(self.BACKGROUND_COLOR)
		grp.RenderBar(xRender, yRender, widthRender, heightRender)
		grp.SetColor(self.DARK_COLOR)
		grp.RenderLine(xRender, yRender, widthRender, 0)
		grp.RenderLine(xRender, yRender, 0, heightRender)
		grp.RenderLine(xRender, yRender+heightRender, widthRender+1, 0)
		grp.RenderLine(xRender+widthRender, yRender, 0, heightRender)

		grp.SetColor(self.PROGRESS_COLOR_2)
		grp.RenderBar(xRender + 2, yRender + 2, (self.width - 3) * self.progressextra / 100, heightRender - 3)
		
		if self.isFinished:
			grp.SetColor(self.FINISHED_COLOR)
		else:
			grp.SetColor(self.PROGRESS_COLOR)
		grp.RenderBar(xRender + 2, yRender + 2, (self.width - 3) * self.progress / 100, heightRender - 3)
#