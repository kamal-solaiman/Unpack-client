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
		self.percentage = [0,0,0,0,0]

	def __del__(self):
		ui.Window.__del__(self)

	def Initialize(self):
		self.main = {}

		self.main["background"] = ui.ExpandedImageBox()
		self.main["background"].SetParent(self)
		self.main["background"].LoadImage("interfaz/dominiumpvp.png")
		self.main["background"].SetPosition(wndMgr.GetScreenWidth()/2 - 700 / 2, 0)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["background"].SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 - 700 / 2, 0)})
		self.main["background"].Show()
		
		self.main["text"] = ui.TextLine()
		
		self.main["text"].online_A = ui.TextLine()
		self.main["text"].online_A.SetParent(self.main["background"])
		self.main["text"].online_A.SetPosition(200, 22)
		self.main["text"].online_A.SetFontName("Roman:20")
		self.main["text"].online_A.SetPackedFontColor(0xff948b7d)
		self.main["text"].online_A.SetHorizontalAlignLeft()
		self.main["text"].online_A.Show()
		
		self.main["text"].online_B = ui.TextLine()
		self.main["text"].online_B.SetParent(self.main["background"])
		self.main["text"].online_B.SetPosition(480, 22)
		self.main["text"].online_B.SetFontName("Roman:20")
		self.main["text"].online_B.SetPackedFontColor(0xff948b7d)
		self.main["text"].online_B.SetHorizontalAlignLeft()
		self.main["text"].online_B.Show()
		
		self.main["text"].pointA = ui.TextLine()
		self.main["text"].pointA.SetParent(self.main["background"])
		self.main["text"].pointA.SetPosition(125, 20)
		self.main["text"].pointA.SetFontName("Roman:20")
		self.main["text"].pointA.SetPackedFontColor(0xff948b7d)
		self.main["text"].pointA.SetHorizontalAlignLeft()
		self.main["text"].pointA.Show()
		
		self.main["text"].pointB = ui.TextLine()
		self.main["text"].pointB.SetParent(self.main["background"])
		self.main["text"].pointB.SetPosition(545, 20)
		self.main["text"].pointB.SetFontName("Roman:20")
		self.main["text"].pointB.SetPackedFontColor(0xff948b7d)
		self.main["text"].pointB.SetHorizontalAlignLeft()
		self.main["text"].pointB.Show()

		self.main["text"].clock = ui.TextLine()
		self.main["text"].clock.SetParent(self.main["background"])
		self.main["text"].clock.SetPosition(320+60, 20)
		self.main["text"].clock.SetFontName("Roman:25")
		self.main["text"].clock.SetPackedFontColor(0xff948b7d)
		self.main["text"].clock.SetHorizontalAlignLeft()
		self.main["text"].clock.Show()

		self.CircleBRBase = ui.ExpandedImageBox()
		self.CircleBRBase.SetParent(self.main["background"])
		self.CircleBRBase.SetPosition(265, 67)
		self.CircleBRBase.AddFlag("not_pick")
		self.CircleBRBase.LoadImage("interfaz/circle_empty.png")
		self.CircleBRBase.Show()
		
		self.CircleABase = ui.ExpandedImageBox()
		self.CircleABase.SetParent(self.main["background"])
		self.CircleABase.SetPosition(265+35, 67)
		self.CircleABase.AddFlag("not_pick")
		self.CircleABase.LoadImage("interfaz/circle_empty.png")
		self.CircleABase.Show()
		
		self.CircleBBase = ui.ExpandedImageBox()
		self.CircleBBase.SetParent(self.main["background"])
		self.CircleBBase.SetPosition(265+35+35, 67)
		self.CircleBBase.AddFlag("not_pick")
		self.CircleBBase.LoadImage("interfaz/circle_empty.png")
		self.CircleBBase.Show()
		
		self.CircleCBase = ui.ExpandedImageBox()
		self.CircleCBase.SetParent(self.main["background"])
		self.CircleCBase.SetPosition(265+35+35+35, 67)
		self.CircleCBase.AddFlag("not_pick")
		self.CircleCBase.LoadImage("interfaz/circle_empty.png")
		self.CircleCBase.Show()
		
		self.CircleBBBase = ui.ExpandedImageBox()
		self.CircleBBBase.SetParent(self.main["background"])
		self.CircleBBBase.SetPosition(265+35+35+35+35, 67)
		self.CircleBBBase.AddFlag("not_pick")
		self.CircleBBBase.LoadImage("interfaz/circle_empty.png")
		self.CircleBBBase.Show()
		
		self.CircleA = CreateCircle()
		self.CircleA.SetParent(self.CircleABase)
		self.CircleA.SetPosition(0, 0)
		self.CircleA.Show()
		
		self.CircleAText = ui.TextLine()
		self.CircleAText.SetParent(self.CircleABase)
		self.CircleAText.SetPosition(8+8, 4)
		self.CircleAText.SetFontName("Tahoma:14")
		self.CircleAText.SetText("A")
		self.CircleAText.SetPackedFontColor(0xffffffff)
		self.CircleAText.Show()
		
		self.CircleB = CreateCircle()
		self.CircleB.SetParent(self.CircleBBase)
		self.CircleB.SetPosition(0, 0)
		self.CircleB.Show()
		
		self.CircleBText = ui.TextLine()
		self.CircleBText.SetParent(self.CircleBBase)
		self.CircleBText.SetPosition(8+8, 4)
		self.CircleBText.SetFontName("Tahoma:14")
		self.CircleBText.SetText("B")
		self.CircleBText.SetPackedFontColor(0xffffffff)
		self.CircleBText.Show()
		
		self.CircleC = CreateCircle()
		self.CircleC.SetParent(self.CircleCBase)
		self.CircleC.SetPosition(0, 0)
		self.CircleC.Show()
		
		self.CircleCText = ui.TextLine()
		self.CircleCText.SetParent(self.CircleCBase)
		self.CircleCText.SetPosition(8+8, 4)
		self.CircleCText.SetFontName("Tahoma:14")
		self.CircleCText.SetText("C")
		self.CircleCText.SetPackedFontColor(0xffffffff)
		self.CircleCText.Show()
		
		self.CircleBR = CreateCircle()
		self.CircleBR.SetParent(self.CircleBRBase)
		self.CircleBR.SetPosition(0, 0)
		self.CircleBR.Show()
		
		self.CircleBRText = ui.TextLine()
		self.CircleBRText.SetParent(self.CircleBRBase)
		self.CircleBRText.SetPosition(6+12, 4)
		self.CircleBRText.SetFontName("Tahoma:14")
		self.CircleBRText.SetText("BR")
		self.CircleBRText.SetPackedFontColor(0xffffffff)
		self.CircleBRText.Show()
		
		self.CircleBB = CreateCircle()
		self.CircleBB.SetParent(self.CircleBBBase)
		self.CircleBB.SetPosition(0, 0)
		self.CircleBB.Show()
		
		self.CircleBBText = ui.TextLine()
		self.CircleBBText.SetParent(self.CircleBBBase)
		self.CircleBBText.SetPosition(6+12, 4)
		self.CircleBBText.SetFontName("Tahoma:14")
		self.CircleBBText.SetText("BB")
		self.CircleBBText.SetPackedFontColor(0xffffffff)
		self.CircleBBText.Show()
		
	def Append(self, tokens):
		self.leftTime = app.GetGlobalTimeStamp() + int(tokens[0])
		self.Show()
		self.main["text"].online_A.SetText(tokens[1])
		self.main["text"].online_B.SetText(tokens[2])		
		self.main["text"].pointA.SetText(tokens[3])
		self.main["text"].pointB.SetText(tokens[4])
		self.percentage[0] = int(tokens[5])
		self.percentage[1] = int(tokens[6])
		self.percentage[2] = int(tokens[7])
		self.percentage[3] = int(tokens[8])
		self.percentage[4] = int(tokens[9])

	def SetTime(self, iLeft):
		leftTime = iLeft - app.GetGlobalTimeStamp()
		
		if leftTime <= 0:
			leftTime = 0
			self.Hide()

		self.main["text"].clock.SetText(("%s" % (CalculateTimeLeft(leftTime))))

	def OnUpdate(self):
		self.SetTime(int(self.leftTime))
		self.CircleA.SetPercentage(self.percentage[0])
		self.CircleB.SetPercentage(self.percentage[1])
		self.CircleC.SetPercentage(self.percentage[2])
		self.CircleBR.SetPercentage(self.percentage[3])
		self.CircleBB.SetPercentage(self.percentage[4])

	def Destroy(self):
		self.ClearDictionary()
#
class CreateCircle(ui.ExpandedImageBox):

	def __init__(self, layer = "UI"):
		ui.ExpandedImageBox.__init__(self, layer)
	
		self.percentage = 0
		
	def __del__(self):
		ui.ExpandedImageBox.__del__(self)
		
	def SetPercentage(self, value):
		self.percentage = value
		self.Refresh()
		
	def Refresh(self):
		image = "interfaz/circle_red.png"
		percentage = self.percentage
		if self.percentage < 0:
			image = "interfaz/circle_blue.png"
			percentage = percentage*-1
			
		self.LoadImage(image)
		self.SetPercentageDown(percentage, 100)
#