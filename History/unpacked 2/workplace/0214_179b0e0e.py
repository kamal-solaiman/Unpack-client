# coding: latin_1

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import net

import chat
import grp
import wndMgr
import uicommon
import uiguild
import uitooltip
import ui
import constinfo
import localeinfo

def CalculateTimeLeft(iTime):
	A, B = divmod(iTime, 60)
	C, A = divmod(A, 60)
	return "%02d:%02d" % (A, B)	

class Window(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)

	def __del__(self):
		ui.Window.__del__(self)

	def Initialize(self):
		self.main = {}

		self.main["background"] = ui.ExpandedImageBox()
		self.main["background"].SetParent(self)
		self.main["background"].LoadImage("interfaz/crystalpvp.tga")
		self.main["background"].SetPosition(wndMgr.GetScreenWidth()/2 - 750 / 2, - 5)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["background"].SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 - 750 / 2, - 5)})
		self.main["background"].SetScale(0.9, 0.9)
		self.main["background"].Show()
		
		self.main["text"] = ui.TextLine()
		
		self.main["text"].online_A = ui.TextLine()
		self.main["text"].online_A.SetParent(self)
		self.main["text"].online_A.SetPosition(wndMgr.GetScreenWidth()/2 - 750 / 2 + 240, 27)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["text"].online_A.SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 - 750 / 2 + 240, 27)})
		self.main["text"].online_A.SetFontName("Roman:20")
		self.main["text"].online_A.SetPackedFontColor(0xff948b7d)
		self.main["text"].online_A.SetHorizontalAlignLeft()
		self.main["text"].online_A.Show()
		
		self.main["text"].online_B = ui.TextLine()
		self.main["text"].online_B.SetParent(self)
		self.main["text"].online_B.SetPosition(wndMgr.GetScreenWidth()/2 - 750 / 2 + 500, 27)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["text"].online_B.SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 - 750 / 2 + 500, 27)})
		self.main["text"].online_B.SetFontName("Roman:20")
		self.main["text"].online_B.SetPackedFontColor(0xff948b7d)
		self.main["text"].online_B.SetHorizontalAlignLeft()
		self.main["text"].online_B.Show()
		
		self.main["text"].crystalA = ui.TextLine()
		self.main["text"].crystalA.SetParent(self)
		self.main["text"].crystalA.SetPosition(wndMgr.GetScreenWidth()/2 - 750 / 2 + 175, 22)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["text"].crystalA.SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 - 750 / 2 + 175, 22)})
		self.main["text"].crystalA.SetFontName("Roman:20")
		self.main["text"].crystalA.SetPackedFontColor(0xff948b7d)
		self.main["text"].crystalA.SetHorizontalAlignLeft()
		self.main["text"].crystalA.Show()
		
		self.main["text"].crystalB = ui.TextLine()
		self.main["text"].crystalB.SetParent(self)
		self.main["text"].crystalB.SetPosition(wndMgr.GetScreenWidth()/2 - 750 / 2 + 550, 22)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["text"].crystalB.SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 - 750 / 2 + 550, 22)})
		self.main["text"].crystalB.SetFontName("Roman:20")
		self.main["text"].crystalB.SetPackedFontColor(0xff948b7d)
		self.main["text"].crystalB.SetHorizontalAlignLeft()
		self.main["text"].crystalB.Show()

		self.main["text"].clock = ui.TextLine()
		self.main["text"].clock.SetParent(self)
		self.main["text"].clock.SetPosition(wndMgr.GetScreenWidth()/2 - 750 / 2 + 350, 22)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["text"].clock.SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 - 750 / 2 + 350, 22)})
		self.main["text"].clock.SetFontName("Roman:25")
		self.main["text"].clock.SetPackedFontColor(0xff948b7d)
		self.main["text"].clock.SetHorizontalAlignLeft()
		self.main["text"].clock.Show()
		
	def Append(self, tokens):
		self.leftTime = app.GetGlobalTimeStamp() + int(tokens[0])
		self.Show()
		self.main["text"].online_A.SetText(tokens[1])
		self.main["text"].online_B.SetText(tokens[2])		
		self.main["text"].crystalA.SetText(tokens[3])
		self.main["text"].crystalB.SetText(tokens[4])

	def SetTime(self, iLeft):
		leftTime = iLeft - app.GetGlobalTimeStamp()
		
		if leftTime <= 0:
			leftTime = 0
			self.Hide()

		self.main["text"].clock.SetText(("%s" % (CalculateTimeLeft(leftTime))))

	def OnUpdate(self):
		self.SetTime(int(self.leftTime))

	def Destroy(self):
		self.ClearDictionary()