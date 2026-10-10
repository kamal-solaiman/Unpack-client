# coding: latin_1

import app
import item
import net

import ui
import systemSetting
import localeinfo

IMG_DIR="d:/ymir work/ui/game/whell_of_fortune/"

item_list=[\
			[72148, 1],
			[72149, 1],
			[93100, 1],
			[77777, 1],
			[70772, 1],
			[86371, 1],
			[25041, 1],
			[55408, 1],
			[83012, 1],
			[72089, 1],
			[55033, 1],
			[65143, 1],
			[65147, 1],
			[100700,5],
			[26042,1],
			[70710,5],
			[70706,10],
			[70707,10],
			[55031,5],
			[71153,2],
			[70030,1],
			[70030,2],
			[71035,2],
			[72006,2],
			[100400,1],
			[100400,1],
			[70068,1],
			[80019,10],
			[80019,100],
			[65026,1],
			[65025,1],
]

class MultiTextLine(ui.Window):
	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.children=[]
		self.rangeText=0

	def __init__(self):
		ui.Window.__init__(self)
		self.children=[]
		self.rangeText=15
		self.textType=""

	def SetTextType(self, textType):
		self.textType=textType
		for text in self.children:
			self.AddTextType(self.textType.split("#"),text)

	def SetTextRange(self, range):
		self.rangeText=range
		yPosition=0
		for text in self.children:
			text.SetPosition(0,yPosition)
			yPosition+=self.rangeText

	def AddTextType(self, typeArg, text):
		if len(typeArg) > 1:
			if typeArg[0] == "vertical":
				if typeArg[1] == "top":
					text.SetVerticalAlignTop()
				elif typeArg[1] == "bottom":
					text.SetVerticalAlignBottom()
				elif typeArg[1] == "center":
					text.SetVerticalAlignCenter()
			elif typeArg[0] == "horizontal":
				if typeArg[1] == "left":
					text.SetHorizontalAlignLeft()
				elif typeArg[1] == "right":
					text.SetHorizontalAlignRight()
				elif typeArg[1] == "center":
					text.SetHorizontalAlignCenter()

	def SetText(self, cmd):
		if len(self.children) > 1:
			self.children=[]
		
		multi_arg=cmd.split("\n")
		yPosition=0
		
		for text in multi_arg:
			childText=ui.TextLine()
			childText.SetParent(self)
			childText.SetPosition(0,yPosition)
			if self.textType != "":
				self.AddTextType(self.textType.split("#"),childText)
			
			childText.SetText(str(text))
			childText.Show()
			self.children.append(childText)
			yPosition+=self.rangeText

class MessageWindow(ui.BoardWithTitleBar):
	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.Destroy()

	def Destroy(self):
		self.children={}

	def LoadMessage(self, itemVnum, itemCount):
		self.SetTitleName(localeinfo.WHEEL_REWARD_TITLE)
		self.SetCloseEvent(self.Close)
		self.SetSize(210,180)
		self.AddFlag("attach")
		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetCenterPosition()
		
		item.SelectItem(itemVnum)
		
		multiText=MultiTextLine()
		multiText.SetParent(self)
		multiText.SetTextType("horizontal#center")
		multiText.SetPosition(95,45)
		if itemCount > 1:
			text="%s\nx%d%s\n%s"%(localeinfo.WHEEL_REWARD_TEXT, itemCount,item.GetItemName(), localeinfo.WHEEL_REWARD_TEXT_1)
		else:
			text="%s\n%s\n%s"%(localeinfo.WHEEL_REWARD_TEXT,item.GetItemName(), localeinfo.WHEEL_REWARD_TEXT_1)
		
		multiText.SetText(text)
		multiText.Show()
		self.children["multiText"]=multiText

		itemIcon=ui.ImageBox()
		itemIcon.SetParent(self)
		itemIcon.LoadImage(item.GetIconImageFileName())
		itemIcon.SetPosition(105-16,95)
		itemIcon.Show()
		self.children["itemIcon"]=itemIcon
		
		itemCountNumber=ui.NumberLine()
		itemCountNumber.SetParent(itemIcon)
		itemCountNumber.SetNumber(str(itemCount))
		itemCountNumber.SetPosition(20,20)
		itemCountNumber.Show()
		self.children["itemCount"]=itemCountNumber
		
		okBtn=ui.Button()
		okBtn.SetParent(self)
		okBtn.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		okBtn.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		okBtn.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		okBtn.SetText(localeinfo.UI_OK)
		okBtn.SetEvent(ui.__mem_func__(self.Close))
		okBtn.SetPosition(105-(okBtn.GetWidth()/2),135)
		okBtn.Show()
		self.children["okBtn"]=okBtn
		
		self.Show()

	def Close(self):
		self.Destroy()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

class ImageBoxSpecial(ui.Window):
	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.imageList=[]
		self.waitingTime=0.0
		self.sleepTime=0.0
		self.alphaValue=0.0
		self.increaseValue=0.0
		self.minAlpha=0.0
		self.maxAlpha=0.0
		self.alphaStatus=False
		self.imageIndex=0
		self.img=0
		self.numberText=0

	def __init__(self):
		ui.Window.__init__(self)
		self.Destroy()
		self.waitingTime=2.0
		self.alphaValue=0.3
		self.increaseValue=0.05
		self.minAlpha=0.3
		self.maxAlpha=1.0

	def SetImage(self, folder, itemVnum, itemCount):
		(x, y)=(0,0)
		if self.img!=0:
			(x, y)=self.img.GetLocalPosition()
		
		if self.img==0:
			img=ui.ImageBox()
			img.SetParent(self)
			img.SAFE_SetStringEvent("MOUSE_OVER_OUT",self.OverOutItem)
			img.SAFE_SetStringEvent("MOUSE_OVER_IN",self.OverInItem)
			self.img=img
		
		if self.numberText==0:
			numberText=ui.NumberLine()
			numberText.SetParent(self.img)
			numberText.SetPosition(20,20)
			self.numberText=numberText
		
		self.numberText.SetNumber(str(itemCount))
		self.numberText.Show()
		
		self.img.LoadImage(folder)
		self.img.SetPosition(x, y)
		self.img.Show()

	def OverOutItem(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.HideToolTip()

	def OverInItem(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.SetItemToolTip(self.imageList[self.imageIndex][1])

	def Clear(self):
		self.img=0
		self.numberText=0
		self.imageList=[]

	def LoadImage(self, imageFolder, itemVnum, itemCount):
		item_list=[imageFolder, itemVnum, itemCount]
		if item_list in self.imageList:
			return
		
		self.imageList.append(item_list)
		if self.img==0:
			self.SetImage(imageFolder, itemVnum, itemCount)

	def GetNextImage(self, listIndex):
		if listIndex >= len(self.imageList):
			if len(self.imageList) > 0:
				return (0,self.imageList[0][0],self.imageList[0][1],self.imageList[0][2])
			
			return (0,"",0,0)
		
		return (listIndex, self.imageList[listIndex][0],self.imageList[listIndex][0], self.imageList[listIndex][2])

	def OnUpdate(self):
		if len(self.imageList) <= 1:
			self.imageIndex=0
			return
		elif self.sleepTime > app.GetTime():
			return
		
		if self.alphaStatus == True:
			self.alphaValue -= self.increaseValue
			if self.alphaValue < self.minAlpha:
				self.alphaValue=self.minAlpha
				self.alphaStatus=False
				(imageIndex, imageFolder, itemVnum, itemCount)=self.GetNextImage(self.imageIndex+1)
				if imageFolder != "":
					self.SetImage(imageFolder, itemVnum, itemCount)
				
				self.imageIndex=imageIndex
		else:
			self.alphaValue += self.increaseValue
			if self.alphaValue > self.maxAlpha:
				self.alphaStatus=True
				self.sleepTime=app.GetTime()+self.waitingTime
		
		if self.img!=0:
			self.img.SetAlpha(self.alphaValue)

class WheelofFortune(ui.BoardWithTitleBar):
	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.Destroy()
		self.CreateGame()

	def Destroy(self):
		self.children={}
		self.circleRotation=0
		self.wheelStep=0
		self.giftIndex=0
		self.showAnimation=True

	def Open(self):
		self.Show()

	def Close(self):
		self.CloseMessageWindow()
		if self.wheelStep > 0:
			self.wheelStep=0
			self.circleRotation=self.wheelRotation
			self.children["wheelCircle"].SetRotation(self.circleRotation)
			self.UpdateSingleFortune()
			self.SendServerDone()
		
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def CreateGame(self):
		self.SetSize(437+12,33+421)
		self.SetCenterPosition()
		self.SetTitleName(localeinfo.WHEEL_GAME_TITLE)
		self.SetCloseEvent(self.Close)
		self.AddFlag("movable")
		self.AddFlag("attach")
		self.AddFlag("float")
		
		board=ui.ImageBox()
		board.SetParent(self)
		board.LoadImage(IMG_DIR+"wallpaper.tga")
		board.SetPosition(5,28)
		board.Show()
		self.children["board"]=board
		
		fortuneImg=ui.ImageBox()
		fortuneImg.SetParent(board)
		fortuneImg.AddFlag("not_pick")
		fortuneImg.LoadImage(IMG_DIR+"fortune.tga")
		fortuneImg.SetPosition(28,23)
		fortuneImg.Show()
		self.children["fortuneImg"]=fortuneImg
		
		fortuneSingle=ui.ExpandedImageBox()
		fortuneSingle.SetParent(board)
		fortuneSingle.AddFlag("not_pick")
		fortuneSingle.LoadImage(IMG_DIR+"single.tga")
		fortuneSingle.SetPosition(164,38)
		fortuneSingle.Show()
		self.children["fortuneSingle"]=fortuneSingle
		
		wheelCircle=ui.ExpandedImageBox()
		wheelCircle.SetParent(board)
		wheelCircle.LoadImage(IMG_DIR+"circle.tga")
		wheelCircle.AddFlag("not_pick")
		wheelCircle.SetPosition(155,136)
		wheelCircle.Show()
		self.children["wheelCircle"]=wheelCircle
		
		wheelBtn=ui.Button()
		wheelBtn.SetParent(board)
		wheelBtn.SetUpVisual(IMG_DIR+"wheel_0.tga")
		wheelBtn.SetOverVisual(IMG_DIR+"wheel_1.tga")
		wheelBtn.SetDownVisual(IMG_DIR+"wheel_2.tga")
		wheelBtn.SetPosition(160,155)
		wheelBtn.SetEvent(ui.__mem_func__(self.StartWheel))
		wheelBtn.Show()
		self.children["wheelBtn"]=wheelBtn
		
		dcBar=ui.Bar()
		dcBar.SetParent(board)
		dcBar.SetSize(128,24)
		dcBar.SetPosition(9,10)
		import grp
		dcBar.SetColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.8))
		dcBar.Show()
		self.children["dcBar"]=dcBar
		
		dcIcon=ui.ExpandedImageBox()
		dcIcon.SetParent(board)
		dcIcon.LoadImage(IMG_DIR+"coin.tga")
		dcIcon.AddFlag("not_pick")
		dcIcon.SetPosition(12,12)
		dcIcon.Show()
		self.children["dcIcon"]=dcIcon
		
		dcText=ui.TextLine()
		dcText.SetParent(board)
		dcText.SetText("0")
		dcText.SetOutline()
		dcText.SetPosition(12+self.children["dcIcon"].GetWidth()+40,14)
		dcText.Show()
		self.children["dcText"]=dcText
		
		infoBar=ui.Bar()
		infoBar.SetParent(board)
		infoBar.SetSize(128,24)
		infoBar.SetPosition(9,390)
		import grp
		infoBar.SetColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.8))
		infoBar.Show()
		self.children["infoBar"]=infoBar
		
		event=lambda index=0 : ui.__mem_func__(self.SetAnimationStatus)(index)
		self.children["animationCheckBox"]=ui.CheckBoxNew(board, 12, 393, event)
		
		animationText=ui.TextLine()
		animationText.SetParent(board)
		animationText.SetText(localeinfo.WHEEL_GAME_SKIP_ANIMATION)
		animationText.SetOutline()
		animationText.SetPosition(12+self.children["animationCheckBox"].GetWidth()+100,395)
		animationText.Show()
		self.children["animationText"]=animationText
		
		itemPosition=[[205,65], [275,90], [320,160], [320,235], [275,290], [205,320], [130,295], [90,235], [85,160], [130,90]]
		for j in xrange(len(itemPosition)):
			wheelItem=ImageBoxSpecial()
			wheelItem.SetParent(board)
			wheelItem.SetPosition(itemPosition[j][0],itemPosition[j][1])
			wheelItem.SetSize(32,32)
			wheelItem.Show()
			self.children["wheelItem%d"%j]=wheelItem
		
		self.SetTrailerMode()

	def SetAnimationStatus(self, key):
		value=0
		if not self.children["animationCheckBox"].GetCheck():
			value=1
		
		self.children["animationCheckBox"].SetCheck(value)
		if value == 1:
			self.showAnimation=False
		else:
			self.showAnimation=True

	def GetGiftRotation(self, giftIndex):
		if giftIndex == 0:
			if app.GetRandom(0,1) == 0:
				return 341+app.GetRandom(4,18)
			else:
				return app.GetRandom(4,19)
		else:
			listofIndex=[0,20,58,94,126,160,196,232,268,304,341]
			return listofIndex[giftIndex]+app.GetRandom(4,28)

	def CloseMessageWindow(self):
		if self.children.has_key("message_window"):
			msgWindow=self.children["message_window"]
			if msgWindow!=0:
				msgWindow.Hide()
				msgWindow=0

	def GetGiftData(self, itemVnum, itemCount):
		self.CloseMessageWindow()
		self.children["message_window"]=MessageWindow()
		self.children["message_window"].LoadMessage(itemVnum, itemCount)

	def GetRotationToIndex(self, rotation):
		if rotation >= 341 and rotation <= 360 or rotation <= 20:
			return 0
		elif rotation >= 305 and rotation <= 305+38:
			return 9
		elif rotation >= 269 and rotation <= 269+38:
			return 8
		elif rotation >= 233 and rotation <= 233+38:
			return 7
		elif rotation >= 197 and rotation <= 197+38:
			return 6
		elif rotation >= 161 and rotation <= 161+38:
			return 5
		elif rotation >= 127 and rotation <= 127+38:
			return 4
		elif rotation >= 95 and rotation <= 95+38:
			return 3
		elif rotation >= 59 and rotation <= 59+38:
			return 2
		elif rotation >= 21 and rotation <= 21+38:
			return 1
		
		return 0

	def SetTrailerMode(self):
		for j in xrange(10):
			self.children["wheelItem%d"%j].Clear()
			for x in xrange(10):
				itemData=item_list[app.GetRandom(0,len(item_list)-1)]
				item.SelectItem(itemData[0])
				self.children["wheelItem%d"%j].LoadImage(item.GetIconImageFileName(), itemData[0], itemData[1])

	def SendServerDone(self):
		net.SendChatPacket("/wheel_of_fortune done")

	def StartWheel(self):
		net.SendChatPacket("/wheel_of_fortune start")

	def SetItemData(self, data):
		for j in xrange(10):
			self.children["wheelItem%d"%j].Clear()
		
		index=0
		splitData=data.split("#")
		for splitText in splitData:
			splitItem=splitText.split("|")
			if len(splitItem) == 2:
				item.SelectItem(int(splitItem[0]))
				self.children["wheelItem%d"%index].LoadImage(item.GetIconImageFileName(), int(splitItem[0]), int(splitItem[1]))
				index += 1

	def UpdateSingleFortune(self):
		single_pos=[[164,38,0], [230,63,35], [270,120,70], [266,188,110], [226,241,142], [160,262,180], [98,243,215], [56,189,250], [53,119,285], [96,61,324]]
		index=self.GetRotationToIndex(self.circleRotation)
		self.children["fortuneSingle"].SetRotation(single_pos[index][2])
		self.children["fortuneSingle"].SetPosition(single_pos[index][0],single_pos[index][1])

	def OnSetWhell(self, giftIndex):
		self.giftIndex=giftIndex
		self.wheelRotation=self.GetGiftRotation(giftIndex)
		if self.showAnimation:
			self.wheelStep=app.GetRandom(10, 15)
		else:
			self.wheelStep=0
			self.circleRotation=self.wheelRotation
			self.children["wheelCircle"].SetRotation(self.circleRotation)
			self.UpdateSingleFortune()
			self.SendServerDone()

	def OnUpdate(self):
		if self.wheelStep > 0:
			increaseValue=0.5 * float((self.wheelStep*2))
			self.circleRotation += increaseValue
			self.children["wheelCircle"].SetRotation(self.circleRotation)
			self.UpdateSingleFortune()
			
			if self.circleRotation >= 360:
				if self.wheelStep > 1:
					self.wheelStep-= 1
				
				self.circleRotation= 0
			
			if self.wheelStep == 1 and self.wheelRotation == self.circleRotation:
				self.wheelStep -= 1
				self.SendServerDone()
				return

	def SetDragonCoins(self, coins):
		self.children["dcText"].SetText(str(coins))

	def OnPressEscapeKey(self):
		self.Close()
		return True
