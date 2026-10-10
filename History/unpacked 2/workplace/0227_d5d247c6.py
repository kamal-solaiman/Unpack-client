import chat
import grp
import net
import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import wndMgr
import uicommon
import uiGuild
import uitooltip
import ui
import constinfo
import localeinfo

class Window(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

	def __del__(self):
		ui.Window.__del__(self)

	def Initialize(self):
		self.main = {}
		
		self.main["background"] = ui.ExpandedImageBox()
		self.main["background"].SetParent(self)
		self.main["background"].LoadImage("d:/ymir work/ui/game/dt_interface.tga")
		self.main["background"].SetPosition(0, wndMgr.GetScreenHeight() - 87)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["background"].SetResizeDic({"position" : (0, Expr("SCREEN_HEIGHT") - 87)})
		self.main["background"].SetScale(0.9, 0.9)
		self.main["background"].Show()
		
		self.main["death_01"] = ui.ImageBox()
		self.main["death_01"].SetParent(self)		
		self.main["death_01"].Show()
		
		self.main["death_02"] = ui.ImageBox()
		self.main["death_02"].SetParent(self)		
		self.main["death_02"].Show()		

		self.main["death_03"] = ui.ImageBox()
		self.main["death_03"].SetParent(self)		
		self.main["death_03"].Show()	
		
		self.main["text"] = ui.TextLine()
		
		self.main["text"].kills = ui.TextLine()
		self.main["text"].kills.SetParent(self)
		self.main["text"].kills.SetPosition(148, wndMgr.GetScreenHeight() - 84)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["text"].kills.SetResizeDic({"position" : (148, Expr("SCREEN_HEIGHT") - 84)})
		self.main["text"].kills.SetPackedFontColor(0xff948b7d)
		self.main["text"].kills.SetHorizontalAlignLeft()
		self.main["text"].kills.Show()
		
		self.main["text"].top_kills = ui.TextLine()
		self.main["text"].top_kills.SetParent(self)					
		self.main["text"].top_kills.SetPosition(117, wndMgr.GetScreenHeight() - 87 + 32)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["text"].top_kills.SetResizeDic({"position" : (117, Expr("SCREEN_HEIGHT") - 87 + 32)})
		self.main["text"].top_kills.SetPackedFontColor(0xff948b7d)
		self.main["text"].top_kills.SetHorizontalAlignLeft()	
		self.main["text"].top_kills.Show()
		
		self.main["text"].kill_owner = ui.TextLine()
		self.main["text"].kill_owner.SetParent(self)
		self.main["text"].kill_owner.SetPosition(175, wndMgr.GetScreenHeight() - 87 + 32)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["text"].kill_owner.SetResizeDic({"position" : (175, Expr("SCREEN_HEIGHT") - 87 + 32)})
		self.main["text"].kill_owner.SetPackedFontColor(0xff948b7d)
		self.main["text"].kill_owner.SetHorizontalAlignLeft()
		self.main["text"].kill_owner.Show()

		
	def Append(self, tokens):
		self.Show()
		
		self.main["text"].kills.SetText(tokens[0])
			
		self.main["text"].top_kills.SetText(tokens[2])
		self.main["text"].kill_owner.SetText(tokens[3])
		if int(tokens[1]) == 1:
			self.main["death_01"].LoadImage("d:/ymir work/ui/game/dt_death_icon.tga")
			self.main["death_01"].SetPosition(9, wndMgr.GetScreenHeight() - 83)		
			if app.ENABLE_WINDOW_RESIZE:
				self.main["death_01"].SetResizeDic({"position" : (9, Expr("SCREEN_HEIGHT") - 83)})
		elif int(tokens[1]) == 2:
			self.main["death_01"].LoadImage("d:/ymir work/ui/game/dt_death_icon.tga")
			self.main["death_01"].SetPosition(9, wndMgr.GetScreenHeight() - 83)		
			if app.ENABLE_WINDOW_RESIZE:
				self.main["death_01"].SetResizeDic({"position" : (9, Expr("SCREEN_HEIGHT") - 83)})
			self.main["death_02"].LoadImage("d:/ymir work/ui/game/dt_death_icon.tga")
			self.main["death_02"].SetPosition(35, wndMgr.GetScreenHeight() - 75)
			if app.ENABLE_WINDOW_RESIZE:
				self.main["death_02"].SetResizeDic({"position" : (35, Expr("SCREEN_HEIGHT") - 75)})
		elif int(tokens[1]) == 3:
			self.main["death_01"].LoadImage("d:/ymir work/ui/game/dt_death_icon.tga")
			self.main["death_01"].SetPosition(9, wndMgr.GetScreenHeight() - 83)		
			if app.ENABLE_WINDOW_RESIZE:
				self.main["death_01"].SetResizeDic({"position" : (9, Expr("SCREEN_HEIGHT") - 83)})
			self.main["death_02"].LoadImage("d:/ymir work/ui/game/dt_death_icon.tga")
			self.main["death_02"].SetPosition(35, wndMgr.GetScreenHeight() - 75)		
			if app.ENABLE_WINDOW_RESIZE:
				self.main["death_02"].SetResizeDic({"position" : (35, Expr("SCREEN_HEIGHT") - 75)})
			self.main["death_03"].LoadImage("d:/ymir work/ui/game/dt_death_icon.tga")
			self.main["death_03"].SetPosition(56, wndMgr.GetScreenHeight() - 58)
			if app.ENABLE_WINDOW_RESIZE:
				self.main["death_03"].SetResizeDic({"position" : (56, Expr("SCREEN_HEIGHT") - 58)})

	def Destroy(self):
		self.ClearDictionary()