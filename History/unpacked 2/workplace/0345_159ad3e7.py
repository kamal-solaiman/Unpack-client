import dbg
import ui
import net
import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import localeinfo
import constinfo
import uitooltip
import item
import time
import wndMgr
import uiscriptlocale
import chat
import grp
import background
import os

class PartywarBoardWindow(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__Initialize()
		self.__Load()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)
		self.tooltipitem = None

	def __Initialize(self):
		self.titleBar = 0
		self.curTab = 0
		
		self.tabButtons = []
		self.pages = []
		self.member_button = []
		self.type_button = []
		self.time_button = []
		self.MembersCount = None
		self.GroupsCount = None
		self.SetButton = None
		self.StartButton = None
		self.StopButton = None
		self.ItemImage = None
		self.inputReward = None
		self.inputGroups = None
		
		self.SettingReward = 0
		self.SettingMembers = 2
		self.SettingType = 1
		self.SettingTimer = 5
		
		self.tooltipitem = uitooltip.ItemToolTip()
		
	def Destroy(self):
		self.ClearDictionary()
		self.__Initialize()

	def __Load_LoadScript(self, fileName):
		try:
			pyScriptLoader = ui.PythonScriptLoader()
			pyScriptLoader.LoadScriptFile(self, fileName)
		except:
			import exception
			exception.Abort("PartywarDialog.__Load_LoadScript")

	def __LoadTabPages(self):
		try:
			GetObject = self.GetChild
			self.titleBar = GetObject("titlebar")
			self.pages.append(self.GetChild("Page1"))
			self.pages.append(self.GetChild("Page2"))
			for i in xrange(2):
				self.tabButtons.append(self.GetChild("Tab%d" % (i+1)))
				self.pages[i].Hide()

		except:
			import exception
			exception.Abort("PartywarDialog.__LoadTabPages")

	def __LoadPage1(self):
		try:
			GetObject = self.GetChild
			self.SetButton = GetObject("SetButton")
			for i in xrange(4):
				self.member_button.append(GetObject("member_button%d" % (i)))
			self.inputReward = GetObject("inputReward")
			self.inputGroups = GetObject("inputGroups")
			
		except:
			import exception
			exception.Abort("PartywarDialog.__LoadPage1")

	def __LoadPage2(self):
		try:
			GetObject = self.GetChild
			self.StartButton = GetObject("StartButton")
			self.StopButton = GetObject("StopButton")
			self.MembersCount = self.GetChild("MembersCount")
			self.GroupsCount = self.GetChild("GroupsCount")
			self.ItemImage = GetObject("ItemImage")
			for i in xrange(3):
				self.time_button.append(GetObject("time_button%d" % (i)))
			for s in xrange(2):
				self.type_button.append(GetObject("type_button%d" % (s)))
			

		except:
			import exception
			exception.Abort("PartywarDialog.__LoadPage2")

	def __Load(self):
		self.__Load_LoadScript("uiscript/partywarboard.py")
		self.__LoadTabPages()
		self.__LoadPage1()
		self.__LoadPage2()
		self.SetCenterPosition()
		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))
		self.SetButton.SAFE_SetEvent(self.__OnClickSetButton)
		self.StartButton.SAFE_SetEvent(self.__OnClickStartButton)
		self.StopButton.SAFE_SetEvent(self.__OnClickStopButton)
		self.ItemImage.SetOverInItemEvent(ui.__mem_func__(self.OverInImgItemSlot))
		self.ItemImage.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		for i in xrange(4):
			self.member_button[i].SetEvent(lambda arg=i: self.__OnClickMemberButton(arg))
		for i in xrange(3):
			self.time_button[i].SetEvent(lambda arg=i: self.__OnClickTimerButton(arg))
		for i in xrange(2):
			self.type_button[i].SetEvent(lambda arg=i: self.__OnClickTypeButton(arg))
		self.member_button[0].Down()
		self.type_button[0].Down()
		self.time_button[0].Down()
			
		self.tabButtonGroup = ui.RadioButtonGroup.Create([
			[self.tabButtons[0], self._WrapHandler(self._OnClickTabButton, 0), None],
			[self.tabButtons[1], self._WrapHandler(self._OnClickTabButton, 1), None],
		])

	def _WrapHandler(self, handler, idx):
		return lambda *args: handler(idx)

	def __ClickRadioButton(self, buttonList, buttonIndex):
		try:
			selButton=buttonList[buttonIndex]
		except IndexError:
			return
		for eachButton in buttonList:
			eachButton.SetUp()
		selButton.Down()
		
		
	def __OnClickMemberButton(self, index):
		self.__ClickRadioButton(self.member_button, index)
		self.SettingMembers = index + 2
		
	def __OnClickTypeButton(self, index):
		self.__ClickRadioButton(self.type_button, index)
		self.SettingType = index + 1
		
	def __OnClickTimerButton(self, index):
		self.__ClickRadioButton(self.time_button, index)
		timeTable = [5, 10, 15]
		self.SettingTimer = timeTable[index]
		

	def OverInImgItemSlot(self, slotIndex):
		if self.tooltipitem:
			self.tooltipitem.SetItemToolTip(self.SettingReward)

	def OverOutItem(self):
		if self.tooltipitem:
			self.tooltipitem.HideToolTip()
			self.tooltipitem.ClearToolTip()
	
	def __OnClickStartButton(self):
		net.SendChatPacket("/start_partywar %d %d" % (self.SettingType, self.SettingTimer))
	
	def __OnClickStopButton(self):
		net.SendChatPacket("/start_partywar 0 0")
		
	def __OnClickSetButton(self):
		member  = self.SettingMembers
		reward	= self.inputReward.GetText()
		groups	= self.inputGroups.GetText()
		if reward and not reward.isdigit():
			chat.AppendChat(1, "uncorrect number")
			return
		if groups and not groups.isdigit():
			chat.AppendChat(1, "uncorrect number")
			return
		net.SendChatPacket("/set_partywar %d %s %s" % (member,reward,groups))
		
		self.ItemImage.SetItemSlot(0, member, 0)
		self.ItemImage.RefreshSlot()
		self.MembersCount.SetText(str(member))
		self.GroupsCount.SetText(str(groups))

	def _OnClickTabButton(self, id):
		self.SetCurTab(id)

	def GetCurTab(self):
		return self.curTab

	def SetCurTab(self, tab):
		self.curTab = tab
		self.RefreshTab()
		
	def RefreshTab(self):
		for page in self.pages:
			page.Hide()
		self.pages[self.GetCurTab()].Show()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Open(self):
		if self.IsShow():
			self.Close()
			return
		ui.ScriptWindow.Show(self)
		self.Show()
		
	def SetPartywarBoard(self, member, reward, groups):
		self.MembersCount.SetText(str(member))
		self.GroupsCount.SetText(str(groups))
		self.SettingReward = int(reward)
		
		self.ItemImage.SetItemSlot(0, self.SettingReward, 0)
		self.ItemImage.RefreshSlot()

	def Close(self):
		self.inputReward.KillFocus()
		self.inputGroups.KillFocus()
		self.OverOutItem()
		self.Hide()
		

class PartywarTimerWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__Initialize()
		self.LoadObject()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __Initialize(self):
		self.wndBoard = None
		self.StartTime = 0
		self.LeftTime = None
		self.MainBoardPos = -180
		
	def Destroy(self):
		self.__Initialize()
		self.ClearDictionary()

	def Open(self):
		self.LoadObject()
		ui.ScriptWindow.Show(self)
		
	def LoadObject(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/partywartimer.py")
		except:
			import exception
			exception.Abort("Window.LoadObject.LoadObject")

		try:
			self.wndBoard = self.GetChild("board")
			self.LeftTime = self.GetChild("LeftTime")
		except:
			import exception
			exception.Abort("Window.LoadObject.BindObject")

	def GetMainBoardLimits(self):
		if self.MainBoardPos < 20:
			self.MainBoardPos += 2
			return True
		return False
		
	def SetPartywarTimer(self, time):
		self.StartTime = app.GetTime()+int(time)

	def OnUpdate(self):
		if not self.wndBoard.IsShow():
			return

		leftTime = max(0, self.StartTime - app.GetTime())
		if leftTime <= 0:
			self.wndBoard.Hide()
			return

		leftMin = int((leftTime / 60) % 60)
		leftSecond = int(leftTime % 60)

		if leftTime < 60: # Red Color Under 60 Sec
			self.LeftTime.SetText("|cffe91d1d|H|h %02d:%02d" % (leftMin, leftSecond))
		else:
			self.LeftTime.SetText("%02d:%02d" % (leftMin, leftSecond))

		if self.GetMainBoardLimits():
			self.SetPosition(self.MainBoardPos, wndMgr.GetScreenHeight() - 350)
			if app.ENABLE_WINDOW_RESIZE:
				self.SetResizeDic({"position" : (self.MainBoardPos, Expr("SCREEN_HEIGHT") - 350)})
			
class PartyWarButton(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__Initialize()
		self.LoadObject()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __Initialize(self):
		self.wndBoard = 0
		self.StartTime = 0
		self.LeftTime = None
		
	def Destroy(self):
		self.__Initialize()
		self.ClearDictionary()

	def Open(self):
		self.LoadObject()
		ui.ScriptWindow.Show(self)
		if background.GetCurrentMapName() == "metin2_map_party_war_lobby":
			self.buttonJoin.Hide()
		else:
			self.buttonJoin.Show()
		
	def LoadObject(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/partywarbutton.py")
		except:
			import exception
			exception.Abort("Window.LoadObject.LoadObject")
		
		try:
			self.wndBoard = self.GetChild("board")
			self.LeftTime = self.GetChild("LeftTime")
			self.buttonJoin = self.GetChild("buttonJoin")
		except:
			import exception
			exception.Abort("Window.LoadObject.BindObject")
			
		self.buttonJoin.SAFE_SetEvent(self.__OnClickJoinButton)

	def __OnClickJoinButton(self):
		net.SendChatPacket("/partywar_join join")

	def SetPartywarTimer(self, time):
		self.StartTime = app.GetTime() + int(time)
		
	def OnUpdate(self):
		if not self.wndBoard.IsShow() and not self.buttonJoin.IsShow():
			return
			
		leftTime = max(0, self.StartTime- app.GetTime())
		if leftTime <= 0:
			self.wndBoard.Hide()
			self.buttonJoin.Hide()
			return
			
		leftMin = int((leftTime / 60) % 60)
		leftSecond = int(leftTime % 60)

		if leftTime < 60: # Red Color Under 60 Sec
			self.LeftTime.SetText("|cffe91d1d|H|h %02d:%02d" % (leftMin, leftSecond))
		else:
			self.LeftTime.SetText("%02d:%02d" % (leftMin, leftSecond))




MAX_DESC_LIST = 14
class PartyWarPlayerBoard(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__Initialize()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.ClearDictionary()
		self.__Initialize()

	def __Initialize(self):
		self.rankLine = []
		self.rankData = { "ID" : [], "NAME" : [], "KILLS" : [], "EMPIRE" : [], }
		self.rankDataBackground = { "ID" : [], "NAME" : [], "KILLS" : [], "EMPIRE" : [], }
		
		self.titleBar = None
		self.toolTip = None

		self.TipsBackground = None
		self.TipsTextList = []
		self.RankingBackground = None
		self.LeftTimeCounter = 0
		self.LeftTimeText = None

		self.TipsScrollBar = None
		self.tooltipitem = None
		
		## SmoothScroll
		self.scroll_animation = None
		self.target_pos = 0.0
		self.current_pos = 0.0
		self.animation_speed = 0.1  # Adjust this value to control smoothness
		self.scroll_speed = 4.0 # This'll make the scroll faster with the same smoothness
		## SmoothScroll
		
		self.PrizeTable = [70754, 70754, 70754, 70754, 70754] # prizes
		
	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/partywarplayerboard.py")
		except:
			import exception
			exception.Abort("PlayerRankWindow.LoadDialog.LoadScript")
		
		try:
			self.titleBar = self.GetChild("TitleBar")
			self.RankingBackground = self.GetChild("RankingBackground")
			self.LeftTimeText = self.GetChild("LeftTimeText")
			self.TipsBackground = self.GetChild("TipsBackground")
			
		except:
			import exception
			exception.Abort("PlayerRankWindow.LoadDialog.BindObject")
		

		str_lineDown = "d:/ymir work/ui/pattern/canal_theme/ranked/line_down.png"
		
		for i in xrange(11):
			lineStep = 24
			yPos = i * lineStep + 15
			if i == 10:
				yPos = i * lineStep + 25
			xPos = 5
			
			line = ui.MakeImageBox(self.RankingBackground, str_lineDown, xPos, yPos)
			if i < 5:
				line.OnMouseOverIn = lambda arg=i: self.__OverInBar(arg)
				line.OnMouseOverOut = lambda arg=0: self.__OverOutBar()
			self.rankLine.append(line)
			

			ID_BACKGROUND = ui.Bar("TOP_MOST")
			ID_BACKGROUND.SetParent(self.rankLine[i])
			ID_BACKGROUND.SetPosition(4, 2)
			ID_BACKGROUND.AddFlag("not_pick")
			ID_BACKGROUND.SetSize(31, 16)
			ID_BACKGROUND.SetColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.0))
			ID_BACKGROUND.Show()
			self.rankDataBackground["ID"].append(ID_BACKGROUND)
			
			NAME_BACKGROUND = ui.Bar("TOP_MOST")
			NAME_BACKGROUND.SetParent(self.rankLine[i])
			NAME_BACKGROUND.SetPosition(30 , 2)
			NAME_BACKGROUND.AddFlag("not_pick")
			NAME_BACKGROUND.SetSize(110, 16)
			NAME_BACKGROUND.SetColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.0))
			NAME_BACKGROUND.Show()
			self.rankDataBackground["NAME"].append(NAME_BACKGROUND)
			
			EMPIRE_BACKGROUND = ui.Bar("TOP_MOST")
			EMPIRE_BACKGROUND.SetParent(self.rankLine[i])
			EMPIRE_BACKGROUND.SetPosition(158 - 13, 3)
			EMPIRE_BACKGROUND.AddFlag("not_pick")
			EMPIRE_BACKGROUND.SetSize(48, 16)
			EMPIRE_BACKGROUND.SetColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.0))
			EMPIRE_BACKGROUND.Show()
			self.rankDataBackground["EMPIRE"].append(EMPIRE_BACKGROUND)

			WIN_BACKGROUND = ui.Bar("TOP_MOST")
			WIN_BACKGROUND.SetParent(self.rankLine[i])
			WIN_BACKGROUND.SetPosition(198, 2)
			WIN_BACKGROUND.AddFlag("not_pick")
			WIN_BACKGROUND.SetSize(22, 16)
			WIN_BACKGROUND.SetColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.0))
			WIN_BACKGROUND.Show()
			self.rankDataBackground["KILLS"].append(WIN_BACKGROUND)
			
			ID = ui.MakeTextLine(self.rankDataBackground["ID"][i])
			NAME = ui.MakeTextLine(self.rankDataBackground["NAME"][i])
			EMPIRE = ui.MakeImageBox(self.rankDataBackground["EMPIRE"][i], "d:/ymir work/ui/game/rank/empire_0.sub", 0, 0)
			EMPIRE.AddFlag("not_pick")
			WIN = ui.MakeTextLine(self.rankDataBackground["KILLS"][i])
			
			self.rankData["ID"].append(ID)
			self.rankData["NAME"].append(NAME)
			self.rankData["EMPIRE"].append(EMPIRE)
			self.rankData["KILLS"].append(WIN)
		
		self.toolTip = uitooltip.ToolTip()
		self.SetCenterPosition()
		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))
		
		self.TipsScrollBar = ui.ScrollBarNew()
		self.TipsScrollBar.SetParent(self.TipsBackground)
		self.TipsScrollBar.SetScrollBarSize(298)
		self.TipsScrollBar.SetPosition(192, 2)
		self.TipsScrollBar.SetScrollEvent(ui.__mem_func__(self.OnScroll))
		self.TipsScrollBar.Show()

		self.LoadTipsBoard()
	
	def LoadTipsBoard(self):
		if len(self.TipsTextList) != 0:
			return

		party_war_tips = self.load_party_war_tips()
		for index, (font_name, text) in party_war_tips.items():
			text_line = ui.TextLine()
			text_line.SetParent(self.TipsBackground)
			text_line.SetFontName(font_name)
			text_line.SetPosition(10, 15 + index * 20)
			text_line.SetHorizontalAlignLeft()
			text_line.SetWindowHorizontalAlignRight()
			text_line.Show()
			if font_name == "Tahoma:16":
				text_line.SetText(text)
				text_line.SetPackedFontColor(0xfff1c40f)
			else:
				text_line.SetText(text)
			# if app.__BL_CLIP_MASK__:
				# text_line.SetClippingMaskWindow(self.TipsBackground)
			self.TipsTextList.append(text_line)
			
			
		self.TipsScrollBar.SetMiddleBarSize(float(min(MAX_DESC_LIST, len(self.TipsTextList))) / float(len(self.TipsTextList)))
		
	def OnRender(self):
		## SmoothScroll
		if self.scroll_animation:
			self.current_pos += (self.target_pos - self.current_pos) * self.animation_speed
			if abs(self.target_pos - self.current_pos) < 0.001:
				self.current_pos = self.target_pos
				self.scroll_animation = None
			
			self.TipsScrollBar.SetPos(self.current_pos)
			self.UpdateTipsPositions()
		## SmoothScroll
		
		xList, yList = self.TipsBackground.GetGlobalPosition()
		widthList, heightList = self.TipsBackground.GetWidth(), self.TipsBackground.GetHeight()

		# if app.__BL_CLIP_MASK__:
			# for banner in self.TipsTextList:
				# banner.SetClippingMaskRect(xList, yList + 6, xList + widthList, yList + (heightList - 6))
		# else:
		for text in self.TipsTextList:
			if text:
				xText, yText = text.GetGlobalPosition()
		
				if yText < yList + 6 or yText + text.GetTextSize()[1] > yList + (heightList - 6):
					text.Hide()
				else:
					text.Show()

	## SmoothScroll
	def UpdateTipsPositions(self):
		max_page_buttons = MAX_DESC_LIST
		total_count = len(self.TipsTextList)
		board_count = min(max_page_buttons, total_count)
		
		# Calculate fractional position
		pos = self.TipsScrollBar.GetPos() * (total_count - board_count)
		
		for i, tips in enumerate(self.TipsTextList):
			# Smoothly interpolate the position
			y_position = 15 + (i - pos) * 20
			tips.SetPosition(10, int(y_position))
			
	def OnScroll(self):
		self.UpdateTipsPositions()
		return True

	def OnRunMouseWheel(self, length):
		import constinfo
		lineCount = len(self.TipsTextList)
		if self.IsInPosition() and self.TipsScrollBar.IsShow() and lineCount > 0:
			dir = self.WHEEL_TO_SCROLL(length)
			self.target_pos = self.TipsScrollBar.GetPos() + ((self.scroll_speed / lineCount) * dir)
			self.target_pos = max(0.0, min(1.0, self.target_pos))
			
			if not self.scroll_animation:
				self.scroll_animation = True
				self.current_pos = self.TipsScrollBar.GetPos()
			return True
		return False
	## SmoothScroll

	def WHEEL_TO_SCROLL(self, length):
		if length > 0:
			return -1
		elif length < 0:
			return 1
		return 0

	def load_party_war_tips(self):
		party_war_tips = {}
		try:
			file = open("%s/party_war_tips.txt" % app.GetLocalePath(), "r")
		except:
			file = open("locale/ae/party_war_tips.txt", "r")
			
		for line in file:
			parts = line.strip().split(',')
			if len(parts) >= 3:
				index = int(parts[0])
				font_name = parts[1]
				text = ','.join(parts[2:])
				party_war_tips[index] = (font_name, text)

		return party_war_tips
	
	def PartyWarTimeData(self, Time):
		self.LeftTimeCounter = Time + app.GetTime()
		
	def OnUpdate(self):
		leftTime = max(0, self.LeftTimeCounter - app.GetTime())
		leftMin = int((leftTime / 60) % 60)
		leftSecond = int(leftTime % 60)
		if self.LeftTimeText:
			if leftTime <= 0:
				self.LeftTimeText.SetText(localeinfo.PARTY_WAR_OVER)
			else:
				self.LeftTimeText.SetText(localeinfo.PARTY_WAR_LEFT_TIME % (leftMin, leftSecond))

	
	def SetImageOnToolTip(self, RankNumber):
		item.SelectItem(self.PrizeTable[RankNumber])
		itemImage = ui.ImageBox()
		itemImage.SetParent(self.toolTip)
		itemImage.Show()
		itemImage.LoadImage(item.GetIconImageFileName())
		itemImage.SetPosition(itemImage.GetWidth() * 3.0, self.toolTip.toolTipHeight)
		self.toolTip.toolTipHeight += itemImage.GetHeight()
		self.toolTip.childrenList.append(itemImage)
		self.toolTip.ResizeToolTip()
		self.toolTip.AutoAppendTextLine(item.GetItemName())

	def __OverInBar(self, stat):
		try:
			self.toolTip.ClearToolTip()
			self.toolTip.SetTitle(localeinfo.PARTY_WAR_SPECIAL_PRIZE)
			RANKED_PRIZES_DESC = {
				0 : localeinfo.PARTY_WAR_SPECIAL_PRIZE_1,
				1 : localeinfo.PARTY_WAR_SPECIAL_PRIZE_2,
			}
			NEGATIVE_COLOR = grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0)
			for desc in RANKED_PRIZES_DESC.itervalues():
				self.toolTip.AutoAppendTextLine(desc)
			self.SetImageOnToolTip(stat)
			self.toolTip.AutoAppendTextLine(localeinfo.PARTY_WAR_SPECIAL_PRIZE_3, NEGATIVE_COLOR)
			self.toolTip.AutoAppendTextLine(localeinfo.PARTY_WAR_SPECIAL_PRIZE_4, NEGATIVE_COLOR)
			self.toolTip.AlignHorizonalCenter()
			self.toolTip.SetTop()
			self.toolTip.Show()
		
		except KeyError:
			pass

	def __OverOutBar(self):
		self.toolTip.Hide()

	def AddPlayerRank(self, line, name, empire, kills, MyRank = False):
		if self.rankData != None:
			if MyRank == True:
				self.rankData["ID"][10].SetText(str(line))
				self.rankData["NAME"][10].SetText(str(name))
				self.rankData["NAME"][10].SetFontName("Arial:14")
				self.rankData["EMPIRE"][10].LoadImage("d:/ymir work/ui/game/rank/empire_%s.sub" % empire)
				self.rankData["KILLS"][10].SetText(str(kills))
				return
				
			if self.rankData["ID"][line]:
				self.rankData["ID"][line].SetText(str(line + 1))
				self.rankData["NAME"][line].SetText(str(name))
				self.rankData["NAME"][line].SetFontName("Arial:14")
				self.rankData["EMPIRE"][line].LoadImage("d:/ymir work/ui/game/rank/empire_%s.sub" % empire)
				self.rankData["KILLS"][line].SetText(str(kills))

	def Open(self):
		for i in xrange(11):
			self.AddPlayerRank(i, "-", 0, 0)
		self.Show()

	def Close(self):
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True