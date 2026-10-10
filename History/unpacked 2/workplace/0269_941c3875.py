# coding: latin_1

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import chr
import net
import player

import ui
import guild
import item
import wndMgr
import grp
import grpText
import localeinfo
import skill
import mousemodule
import uiuploadmark
import uicommon
import uitooltip
import playersettingmodule
import constinfo
import background
import miniMap
import uiscriptlocale

from _weakref import proxy

import systemSetting
if app.ENABLE_GUILD_FINDER:
	import uibadge

GUILD_CONTRACTS_UI = bool(getattr(app, "GUILD_CONTRACTS_REWARDS", 0)
	and hasattr(net, "SendGuildContractsSnapshotPacket") and hasattr(guild, "GetContractData"))
GUILD_DONATION_UI = bool(getattr(app, "GUILD_CONTRACTS_DONATION", 0)
	and hasattr(net, "SendGuildDonateResourcePacket") and hasattr(guild, "GetDonateInfo"))
GUILD_SKILLS_UI = bool(getattr(app, "GUILD_CONTRACTS_SKILLS", 0)
	and hasattr(net, "SendGuildSkillsSnapshotPacket") and hasattr(guild, "GetGuildSkillInfo"))
GUILD_DUNGEON_UI = bool(GUILD_CONTRACTS_UI and getattr(constinfo, "GUILD_DUNGEON_TAB", 0))
GD_ART = "d:/ymir work/ui/new_guild/dungeon/"
GD_PAGE_W = 366
GD_BANNERS = ("dungeon_banner_norm.png", "dungeon_banner_mid.png", "dungeon_banner_hard.png")
GD_RANK_ROWS = ("dungeon_ranking_first.png", "dungeon_ranking_second.png", "dungeon_ranking_third.png", "dungeon_ranking_norm.png")
GD_REP_ICON = "d:/ymir work/ui/new_guild/info_page/reputation.png"
GD_PLATE_COLOR = 0x99201a17
GD_COL_CREAM = 0xfffaf2d7
GD_COL_GOLD = 0xfff2cd98
GD_COL_MUTED = 0xffd2beaa
GD_COL_ACCENT = 0xffffc58d
GD_COL_DIM = 0xff8a8a8a
GD_COST_SLOTS = 5
GD_CHEST_SLOT_ID = 10
GD_CHEST_TEXT_W = 56
GD_MARQUEE_SPEED_PX = 100.0
GD_MARQUEE_DELAY = 0.35

if app.ENABLE_GUILD_FINDER:
	GF_BTN_ART = "d:/ymir work/ui/new_guild/info_page/"
	GF_BTN_UP = GF_BTN_ART + "announce_button.png"
	GF_BTN_OVER = GF_BTN_ART + "announce_button_1.png"
	GF_BTN_DOWN = GF_BTN_ART + "announce_button_2.png"
	GF_BTN_W = 108
	# the info page's action column (upload 84 / war 175 / shop 205 / donate 236 /
	# levelup 265) keeps one free slot at 146; the column never mirrors in Arabic
	GF_BTN_X = 29
	GF_BTN_Y = 146

CONTRACT_ART = "d:/ymir work/ui/new_guild/contracts/"
GUILD_CONTRACT_SLOT_GRIND = 0
GUILD_CONTRACT_SLOT_RALLY = 1
CARD_W = 180
CARD_H = 178
CARD_Y = 24
CARD_LEFT_X = 5
CARD_RIGHT_X = 186
CARD_DESC_X = 8
CARD_DESC_RX = 172
CARD_DESC_Y = 122
CARD_DESC_W = 112
CARD_COUNT_X = 145
CARD_COUNT_RX = 35
CARD_MARQUEE_SPEED_PX = 100.0
CARD_MARQUEE_DELAY = 0.35
GUILD_RALLY_TIER_COUNT = 3
GUILD_DYE_UI = bool(hasattr(net, "SendGuildDyeSetColorPacket") and hasattr(guild, "GetGuildDyeColor"))
if GUILD_DYE_UI:
	import uiguilddye

# specific-monster contract cards render a live model preview + open the wiki, mirroring
# the mission list; only meaningful with the in-game wiki compiled in
CONTRACT_WIKI = bool(getattr(app, "ENABLE_INGAME_WIKI", 0))
if CONTRACT_WIKI:
	try:
		import ingamewikiui
		import nonplayer
	except:
		CONTRACT_WIKI = False

class GuildResourceSlot(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.slotIndex = 0
		self.leftEvent = None
		self.rightEvent = None

	def SetSlotEvent(self, index, leftEvent, rightEvent):
		self.slotIndex = index
		self.leftEvent = leftEvent
		self.rightEvent = rightEvent

	def OnMouseLeftButtonUp(self):
		if self.leftEvent:
			self.leftEvent(self.slotIndex)
		return True

	def OnMouseRightButtonUp(self):
		if self.rightEvent:
			self.rightEvent(self.slotIndex)
		return True

class GuildDonateButton(ui.Button):
	def __init__(self):
		ui.Button.__init__(self)
		self.rIndex = -1
		self.rEvent = None

	def SetRightEvent(self, index, event):
		self.rIndex = index
		self.rEvent = event

	def OnMouseRightButtonUp(self):
		if self.rEvent:
			self.rEvent(self.rIndex)
		return True

class ContractArtSlot(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.slotIndex = 0
		self.overInEvent = None
		self.overOutEvent = None
		self.clickEvent = None

	def SetEvents(self, index, overIn, overOut, click):
		self.slotIndex = index
		self.overInEvent = overIn
		self.overOutEvent = overOut
		self.clickEvent = click

	def OnMouseOverIn(self):
		if self.overInEvent:
			self.overInEvent(self.slotIndex)

	def OnMouseOverOut(self):
		if self.overOutEvent:
			self.overOutEvent(self.slotIndex)

	def OnMouseLeftButtonUp(self):
		if self.clickEvent:
			self.clickEvent(self.slotIndex)
		return True

if app.ENABLE_GUILD_RENEWAL:
	import uiguildmission
if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

DISABLE_GUILD_SKILL = False
DISABLE_DECLARE_WAR = False

def NumberToMoneyString(n):
	return localeinfo.NumberToMoneyString(n)

if (localeinfo.IsEUROPE() and app.GetLocalePath() != "locale/br"):
	def NumberToMoneyString(n):
		if n <= 0 :
			return "0"

		return "%s" % (','.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))

MATERIAL_STONE_INDEX = 0
MATERIAL_LOG_INDEX = 1
MATERIAL_PLYWOOD_INDEX = 2

MATERIAL_STONE_ID = 90010
MATERIAL_LOG_ID = 90011
MATERIAL_PLYWOOD_ID = 90012

BUILDING_DATA_LIST = []

def GetGVGKey(srcGuildID, dstGuildID):
	minID = min(srcGuildID, dstGuildID)
	maxID = max(srcGuildID, dstGuildID)
	return minID*1000 + maxID
def unsigned32(n):
	return n & 0xFFFFFFFFL

class DeclareGuildWarDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.type=0
		self.__CreateDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Open(self):
		self.inputValue.SetFocus()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.ClearDictionary()
		self.board = None
		self.acceptButton = None
		self.cancelButton = None
		self.inputSlot = None
		self.inputValue = None
		self.Hide()

	def __CreateDialog(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()

			if localeinfo.IsVIETNAM() :
				pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "declareguildwardialog.py")
			else:
				pyScrLoader.LoadScriptFile(self, "uiscript/declareguildwardialog.py")

		except:
			import exception
			exception.Abort("DeclareGuildWarWindow.__CreateDialog - LoadScript")

		try:
			getObject = self.GetChild
			self.board = getObject("Board")

			self.typeButtonList = []
			self.typeButtonList.append(getObject("NormalButton"))
			self.typeButtonList.append(getObject("WarpButton"))
			self.typeButtonList.append(getObject("CTFButton"))

			self.acceptButton = getObject("AcceptButton")
			self.cancelButton = getObject("CancelButton")
			self.inputSlot = getObject("InputSlot")
			self.inputValue = getObject("InputValue")

			gameType=getObject("GameType")

		except:
			import exception
			exception.Abort("DeclareGuildWarWindow.__CreateDialog - BindObject")

		if constinfo.GUILD_WAR_TYPE_SELECT_ENABLE == 0:
			gameType.Hide()

		self.typeButtonList[0].SAFE_SetEvent(self.__OnClickTypeButtonNormal)
		self.typeButtonList[1].SAFE_SetEvent(self.__OnClickTypeButtonWarp)
		self.typeButtonList[2].SAFE_SetEvent(self.__OnClickTypeButtonCTF)

		self.typeButtonList[0].SetToolTipWindow(self.__CreateGameTypeToolTip(localeinfo.GUILDWAR_NORMAL_TITLE, localeinfo.GUILDWAR_NORMAL_DESCLIST))
		self.typeButtonList[1].SetToolTipWindow(self.__CreateGameTypeToolTip(localeinfo.GUILDWAR_WARP_TITLE, localeinfo.GUILDWAR_WARP_DESCLIST))
		self.typeButtonList[2].SetToolTipWindow(self.__CreateGameTypeToolTip(localeinfo.GUILDWAR_CTF_TITLE, localeinfo.GUILDWAR_CTF_DESCLIST))

		self.__ClickRadioButton(self.typeButtonList, 0)

		self.SetAcceptEvent(ui.__mem_func__(self.__OnOK))
		self.SetCancelEvent(ui.__mem_func__(self.__OnCancel))

	def __OnOK(self):
		text = self.GetText()
		type = self.GetType()

		if "" == text:
			return

		net.SendChatPacket("/war %s %d" % (text, type))
		self.Close()

		return 1

	def __OnCancel(self):
		self.Close()
		return 1

	def __OnClickTypeButtonNormal(self):
		self.__ClickTypeRadioButton(0)

	def __OnClickTypeButtonWarp(self):
		self.__ClickTypeRadioButton(1)

	def __OnClickTypeButtonCTF(self):
		self.__ClickTypeRadioButton(2)

	def __ClickTypeRadioButton(self, type):
		self.__ClickRadioButton(self.typeButtonList, type)
		self.type=type

	def __ClickRadioButton(self, buttonList, buttonIndex):
		try:
			selButton=buttonList[buttonIndex]
		except IndexError:
			return

		for eachButton in buttonList:
			eachButton.SetUp()

		selButton.Down()

	def SetTitle(self, name):
		self.board.SetTitleName(name)

	def SetNumberMode(self):
		self.inputValue.SetNumberMode()

	def SetSecretMode(self):
		self.inputValue.SetSecret()

	def SetFocus(self):
		self.inputValue.SetFocus()

	def SetMaxLength(self, length):
		width = length * 6 + 10
		self.inputValue.SetMax(length)
		self.SetSlotWidth(width)
		self.SetBoardWidth(max(width + 50, 160))

	def SetSlotWidth(self, width):
		self.inputSlot.SetSize(width, self.inputSlot.GetHeight())
		self.inputValue.SetSize(width, self.inputValue.GetHeight())

	def SetBoardWidth(self, width):
		self.board.SetSize(max(width + 50, 160), self.GetHeight())
		self.SetSize(max(width + 50, 160), self.GetHeight())
		self.UpdateRect()

	def SetAcceptEvent(self, event):
		self.acceptButton.SetEvent(event)
		self.inputValue.OnIMEReturn = event

	def SetCancelEvent(self, event):
		self.board.SetCloseEvent(event)
		self.cancelButton.SetEvent(event)
		self.inputValue.OnPressEscapeKey = event

	def GetType(self):
		return self.type

	def GetText(self):
		return self.inputValue.GetText()

	def __CreateGameTypeToolTip(self, title, descList):
		toolTip = uitooltip.ToolTip()
		toolTip.SetTitle(title)
		toolTip.AppendSpace(5)

		for desc in descList:
			toolTip.AutoAppendTextLine(desc)

		toolTip.AlignHorizonalCenter()
		return toolTip

class AcceptGuildWarDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.type = 0
		self.__CreateDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Open(self, guildName, warType):
		self.guildName=guildName
		self.warType=warType
		self.__ClickSelectedTypeRadioButton()
		self.inputValue.SetText(guildName)
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def GetGuildName(self):
		return self.guildName

	def Close(self):
		self.ClearDictionary()
		self.board = None
		self.acceptButton = None
		self.cancelButton = None
		self.inputSlot = None
		self.inputValue = None
		self.inputSlot = None
		self.inputValue = None
		self.Hide()

	def __ClickSelectedTypeRadioButton(self):
		self.__ClickTypeRadioButton(self.warType)

	def __CreateDialog(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/acceptguildwardialog.py")
		except:
			import exception
			exception.Abort("DeclareGuildWarWindow.__CreateDialog - LoadScript")

		try:
			getObject = self.GetChild
			self.board = getObject("Board")

			self.typeButtonList=[]
			self.typeButtonList.append(getObject("NormalButton"))
			self.typeButtonList.append(getObject("WarpButton"))
			self.typeButtonList.append(getObject("CTFButton"))

			self.acceptButton = getObject("AcceptButton")
			self.cancelButton = getObject("CancelButton")
			self.inputSlot = getObject("InputSlot")
			self.inputValue = getObject("InputValue")

			gameType=getObject("GameType")

		except:
			import exception
			exception.Abort("DeclareGuildWarWindow.__CreateDialog - BindObject")

		if constinfo.GUILD_WAR_TYPE_SELECT_ENABLE == 0:
			gameType.Hide()

		self.typeButtonList[0].SAFE_SetEvent(self.__OnClickTypeButtonNormal)
		self.typeButtonList[1].SAFE_SetEvent(self.__OnClickTypeButtonWarp)
		self.typeButtonList[2].SAFE_SetEvent(self.__OnClickTypeButtonCTF)

		self.typeButtonList[0].SetToolTipWindow(self.__CreateGameTypeToolTip(localeinfo.GUILDWAR_NORMAL_TITLE, localeinfo.GUILDWAR_NORMAL_DESCLIST))
		self.typeButtonList[1].SetToolTipWindow(self.__CreateGameTypeToolTip(localeinfo.GUILDWAR_WARP_TITLE, localeinfo.GUILDWAR_WARP_DESCLIST))
		self.typeButtonList[2].SetToolTipWindow(self.__CreateGameTypeToolTip(localeinfo.GUILDWAR_CTF_TITLE, localeinfo.GUILDWAR_CTF_DESCLIST))

		self.__ClickRadioButton(self.typeButtonList, 0)

	def __OnClickTypeButtonNormal(self):
		self.__ClickSelectedTypeRadioButton()

	def __OnClickTypeButtonWarp(self):
		self.__ClickSelectedTypeRadioButton()

	def __OnClickTypeButtonCTF(self):
		self.__ClickSelectedTypeRadioButton()

	def __ClickTypeRadioButton(self, type):
		self.__ClickRadioButton(self.typeButtonList, type)
		self.type=type

	def __ClickRadioButton(self, buttonList, buttonIndex):
		try:
			selButton=buttonList[buttonIndex]
		except IndexError:
			return

		for eachButton in buttonList:
			eachButton.SetUp()

		selButton.Down()

	def SetTitle(self, name):
		self.board.SetTitleName(name)

	def SetNumberMode(self):
		self.inputValue.SetNumberMode()

	def SetSecretMode(self):
		self.inputValue.SetSecret()

	def SetFocus(self):
		self.inputValue.SetFocus()

	def SetMaxLength(self, length):
		width = length * 6 + 10
		self.inputValue.SetMax(length)
		self.SetSlotWidth(width)
		self.SetBoardWidth(max(width + 50, 160))

	def SetSlotWidth(self, width):
		self.inputSlot.SetSize(width, self.inputSlot.GetHeight())
		self.inputValue.SetSize(width, self.inputValue.GetHeight())

	def SetBoardWidth(self, width):
		self.board.SetSize(max(width + 50, 160), self.GetHeight())
		self.SetSize(max(width + 50, 160), self.GetHeight())
		self.UpdateRect()

	def SAFE_SetAcceptEvent(self, event):
		self.SetAcceptEvent(ui.__mem_func__(event))

	def SAFE_SetCancelEvent(self, event):
		self.SetCancelEvent(ui.__mem_func__(event))

	def SetAcceptEvent(self, event):
		self.acceptButton.SetEvent(event)
		self.inputValue.OnIMEReturn = event

	def SetCancelEvent(self, event):
		self.board.SetCloseEvent(event)
		self.cancelButton.SetEvent(event)
		self.inputValue.OnPressEscapeKey = event

	def GetType(self):
		return self.type

	def GetText(self):
		return self.inputValue.GetText()

	def __CreateGameTypeToolTip(self, title, descList):
		toolTip = uitooltip.ToolTip()
		toolTip.SetTitle(title)
		toolTip.AppendSpace(5)

		for desc in descList:
			toolTip.AutoAppendTextLine(desc)

		toolTip.AlignHorizonalCenter()
		return toolTip

class GuildWarScoreBoard(ui.ThinBoard):
	def __init__(self):
		ui.ThinBoard.__init__(self)
		self.Initialize()

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def Initialize(self):
		self.allyGuildID = 0
		self.enemyGuildID = 0
		self.allyDataDict = {}
		self.enemyDataDict = {}

	def Open(self, allyGuildID, enemyGuildID):
		self.allyGuildID = allyGuildID
		self.enemyGuildID = enemyGuildID

		self.SetPosition(10, wndMgr.GetScreenHeight() - 100)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : (10, Expr("SCREEN_HEIGHT") - 100)})

		mark = ui.MarkBox()
		mark.SetParent(self)
		mark.SetIndex(allyGuildID)
		mark.SetPosition(10, 10 + 18*0)
		mark.Show()
		scoreText = ui.TextLine()
		scoreText.SetParent(self)
		scoreText.SetPosition(30, 10 + 18*0)
		scoreText.SetHorizontalAlignLeft()
		scoreText.Show()
		self.allyDataDict["NAME"] = guild.GetGuildName(allyGuildID)
		self.allyDataDict["SCORE"] = 0
		self.allyDataDict["MEMBER_COUNT"] = -1
		self.allyDataDict["MARK"] = mark
		self.allyDataDict["TEXT"] = scoreText

		mark = ui.MarkBox()
		mark.SetParent(self)
		mark.SetIndex(enemyGuildID)
		mark.SetPosition(10, 10 + 18*1)
		mark.Show()
		scoreText = ui.TextLine()
		scoreText.SetParent(self)
		scoreText.SetPosition(30, 10 + 18*1)
		scoreText.SetHorizontalAlignLeft()
		scoreText.Show()
		self.enemyDataDict["NAME"] = guild.GetGuildName(enemyGuildID)
		self.enemyDataDict["SCORE"] = 0
		self.enemyDataDict["MEMBER_COUNT"] = -1
		self.enemyDataDict["MARK"] = mark
		self.enemyDataDict["TEXT"] = scoreText

		self.__RefreshName()
		self.Show()

	def __GetDataDict(self, ID):
		if self.allyGuildID == ID:
			return self.allyDataDict
		if self.enemyGuildID == ID:
			return self.enemyDataDict

		return None

	def SetScore(self, gainGuildID, opponetGuildID, point):
		dataDict = self.__GetDataDict(gainGuildID)
		if not dataDict:
			return
		dataDict["SCORE"] = point
		self.__RefreshName()

	def UpdateMemberCount(self, guildID1, memberCount1, guildID2, memberCount2):
		dataDict1 = self.__GetDataDict(guildID1)
		dataDict2 = self.__GetDataDict(guildID2)
		if dataDict1:
			dataDict1["MEMBER_COUNT"] = memberCount1
		if dataDict2:
			dataDict2["MEMBER_COUNT"] = memberCount2
		self.__RefreshName()

	def __RefreshName(self):
		nameMaxLen = max(len(self.allyDataDict["NAME"]), len(self.enemyDataDict["NAME"]))

		if -1 == self.allyDataDict["MEMBER_COUNT"] or -1 == self.enemyDataDict["MEMBER_COUNT"]:
			self.SetSize(30+nameMaxLen*6+8*5, 50)
			self.allyDataDict["TEXT"].SetText("%s %d" % (self.allyDataDict["NAME"], self.allyDataDict["SCORE"]))
			self.enemyDataDict["TEXT"].SetText("%s %d" % (self.enemyDataDict["NAME"], self.enemyDataDict["SCORE"]))

		else:
			self.SetSize(30+nameMaxLen*6+8*5+15, 50)
			self.allyDataDict["TEXT"].SetText("%s(%d) %d" % (self.allyDataDict["NAME"], self.allyDataDict["MEMBER_COUNT"], self.allyDataDict["SCORE"]))
			self.enemyDataDict["TEXT"].SetText("%s(%d) %d" % (self.enemyDataDict["NAME"], self.enemyDataDict["MEMBER_COUNT"], self.enemyDataDict["SCORE"]))

class MouseReflector(ui.Window):
	def __init__(self, parent):
		ui.Window.__init__(self)
		self.SetParent(parent)
		self.AddFlag("not_pick")
		self.width = self.height = 0
		self.isDown = False

	def __del__(self):
		ui.Window.__del__(self)

	def Down(self):
		self.isDown = True

	def Up(self):
		self.isDown = False

	def OnRender(self):
		if self.isDown:
			grp.SetColor(ui.WHITE_COLOR)
		else:
			grp.SetColor(ui.HALF_WHITE_COLOR)

		x, y = self.GetGlobalPosition()
		grp.RenderBar(x+2, y+2, self.GetWidth()-4, self.GetHeight()-4)

class EditableTextSlot(ui.ImageBox):
	def __init__(self, parent, x, y):
		ui.ImageBox.__init__(self)
		self.SetParent(parent)
		self.SetPosition(x, y)
		self.LoadImage("d:/ymir work/ui/public/Parameter_Slot_02.sub")

		self.mouseReflector = MouseReflector(self)
		self.mouseReflector.SetSize(self.GetWidth(), self.GetHeight())

		self.Enable = True
		self.textLine = ui.MakeTextLine(self)
		self.event = lambda *arg: None
		self.arg = 0
		self.Show()

		self.mouseReflector.UpdateRect()

	def __del__(self):
		ui.ImageBox.__del__(self)

	def SetText(self, text):
		self.textLine.SetText(text)

	def SetEvent(self, event, arg):
		self.event = event
		self.arg = arg

	def Disable(self):
		self.Enable = False

	def OnMouseOverIn(self):
		if not self.Enable:
			return
		self.mouseReflector.Show()

	def OnMouseOverOut(self):
		if not self.Enable:
			return
		self.mouseReflector.Hide()

	def OnMouseLeftButtonDown(self):
		if not self.Enable:
			return
		self.mouseReflector.Down()

	def OnMouseLeftButtonUp(self):
		if not self.Enable:
			return
		self.mouseReflector.Up()
		self.event(self.arg)

class CheckBox(ui.ImageBox):
	def __init__(self, parent, x, y, event, filename = "d:/ymir work/ui/public/Parameter_Slot_01.sub"):
		ui.ImageBox.__init__(self)
		self.SetParent(parent)
		self.SetPosition(x, y)
		self.LoadImage(filename)

		self.mouseReflector = MouseReflector(self)
		self.mouseReflector.SetSize(self.GetWidth(), self.GetHeight())

		image = ui.MakeImageBox(self, "d:/ymir work/ui/public/check_image.sub", 0, 0)
		image.AddFlag("not_pick")
		image.SetWindowHorizontalAlignCenter()
		image.SetWindowVerticalAlignCenter()
		image.Hide()
		self.Enable = True
		self.image = image
		self.event = event
		self.Show()

		self.mouseReflector.UpdateRect()

	def __del__(self):
		ui.ImageBox.__del__(self)

	def SetCheck(self, flag):
		if flag:
			self.image.Show()
		else:
			self.image.Hide()

	def Disable(self):
		self.Enable = False

	def OnMouseOverIn(self):
		if not self.Enable:
			return
		self.mouseReflector.Show()

	def OnMouseOverOut(self):
		if not self.Enable:
			return
		self.mouseReflector.Hide()

	def OnMouseLeftButtonDown(self):
		if not self.Enable:
			return
		self.mouseReflector.Down()

	def OnMouseLeftButtonUp(self):
		if not self.Enable:
			return
		self.mouseReflector.Up()
		self.event()

class ChangeGradeNameDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Open(self):
		self.gradeNameSlot.SetText("")
		self.gradeNameSlot.SetFocus()
		xMouse, yMouse = wndMgr.GetMousePosition()
		self.SetPosition(xMouse - self.GetWidth()/2, yMouse + 50)
		self.SetTop()
		self.Show()
	def Close(self):
		self.gradeNameSlot.KillFocus()
		self.Hide()
		return True

	def SetGradeNumber(self, gradeNumber):
		self.gradeNumber = gradeNumber
	def GetGradeNumber(self):
		return self.gradeNumber
	def GetGradeName(self):
		return self.gradeNameSlot.GetText()

	def OnPressEscapeKey(self):
		self.Close()
		return True

class RolesPopup(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Open(self):
		x = (wndMgr.GetScreenWidth() - self.GetWidth()) / 2
		y = (wndMgr.GetScreenHeight() - self.GetHeight()) / 2
		self.SetPosition(int(x), int(y))
		self.SetTop()
		self.Show()

	def Close(self):
		self.Hide()
		return True

	def OnPressEscapeKey(self):
		self.Close()
		return True

class CommentSlot(ui.Window):
	TEXT_LIMIT = 35

	def __init__(self):
		ui.Window.__init__(self)

		self.slotImage = ui.MakeImageBox(self, "d:/ymir work/ui/public/Parameter_Slot_06.sub", 0, 0)
		self.slotImage.AddFlag("not_pick")

		self.slotSimpleText = ui.MakeTextLine(self)
		self.slotSimpleText.SetPosition(2, 0)
		if localeinfo.IsARABIC() :
			self.slotSimpleText.SetWindowHorizontalAlignCenter()
			self.slotSimpleText.SetHorizontalAlignCenter()
		else :
			self.slotSimpleText.SetWindowHorizontalAlignLeft()
			self.slotSimpleText.SetHorizontalAlignLeft()

		self.bar = ui.SlotBar()
		self.bar.SetParent(self)
		self.bar.AddFlag("not_pick")
		self.bar.Hide()

		self.slotFullText = ui.MakeTextLine(self)
		self.slotFullText.SetPosition(2, 0)
		self.slotFullText.SetWindowHorizontalAlignLeft()
		self.slotFullText.SetHorizontalAlignLeft()

		self.SetSize(self.slotImage.GetWidth(), self.slotImage.GetHeight())
		self.len = 0

	def __del__(self):
		ui.Window.__del__(self)

	def SetText(self, text):
		self.len = len(text)

		if len(text) > self.TEXT_LIMIT:
			limitText = grpText.GetSplitingTextLine(text, self.TEXT_LIMIT-3, 0)
			self.slotSimpleText.SetText(limitText + "...")
			self.bar.SetSize(self.len * 6 + 5, 17)
		else:
			self.slotSimpleText.SetText(text)

		self.slotFullText.SetText(text)
		self.slotFullText.SetPosition(2, 0)
		self.slotFullText.Hide()

	def OnMouseOverIn(self):
		if self.len > self.TEXT_LIMIT:
			self.bar.Show()
			self.slotFullText.Show()

	def OnMouseOverOut(self):
		if self.len > self.TEXT_LIMIT:
			self.bar.Hide()
			self.slotFullText.Hide()

RANKING_ART = "d:/ymir work/ui/new_guild/ranking/"

class ContractsRankingPopup(ui.ScriptWindow):
	TYPE_WEEKLY = 0
	TYPE_ALLTIME = 1
	TYPE_COINS = 2
	TYPE_DUNGEON = 3
	TYPE_COUNT = 4

	PANEL_MX = 4
	PANEL_MY = 30

	STAT_BANNER_Y = 6
	PLATE_Y = (30, 70, 110)
	TOP_BANNER_Y = 152
	ROW_Y = (176, 195, 214, 233, 252)

	LABEL_CX = 150
	VALUE_CX = 285
	ROW_RANK_CX = 18
	ROW_NAME_CX = 150
	ROW_POINT_CX = 288
	BANNER_CX = 165

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Initialize()
		self.__Build()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		self.built = 0
		self.board = None
		self.bg = None
		self.prevBtn = None
		self.nextBtn = None
		self.statTitle = None
		self.topTitle = None
		self.statPlates = []
		self.rows = []
		self.rankType = self.TYPE_WEEKLY
		self.nextRefresh = 0.0

	def Destroy(self):
		self.statPlates = []
		self.rows = []
		self.board = None
		self.bg = None
		self.prevBtn = None
		self.nextBtn = None
		self.statTitle = None
		self.topTitle = None
		self.ClearDictionary()
		self.Initialize()

	def __L(self, key, default):
		return getattr(localeinfo, key, default)

	def __Num(self, n):
		s = str(int(n))
		neg = ""
		if s[:1] == "-":
			neg = "-"
			s = s[1:]
		out = ""
		while len(s) > 3:
			out = "," + s[-3:] + out
			s = s[:-3]
		return neg + s + out

	def __Txt(self, cx, y, color):
		t = ui.TextLine()
		t.SetParent(self.bg)
		t.SetPosition(cx, y)
		t.SetHorizontalAlignCenter()
		t.SetVerticalAlignCenter()
		t.SetPackedFontColor(color)
		t.SetText("")
		t.Show()
		return t

	def __Img(self, name, x, y):
		img = ui.ImageBox()
		img.SetParent(self.bg)
		img.LoadImage(RANKING_ART + name)
		img.SetPosition(x, y)
		img.AddFlag("not_pick")
		img.Show()
		return img

	def __Banner(self, y, key, default):
		self.__Img("ranking_titlebar.png", 4, y)
		txt = self.__Txt(self.BANNER_CX, y + 10, 0xffffcc66)
		txt.SetText(self.__L(key, default))
		return txt

	def __Build(self):
		if self.built:
			return
		self.built = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/guildrankingpopup.py")

		self.board = self.GetChild2("board")
		self.board.SetCloseEvent(ui.__mem_func__(self.Close))
		self.prevBtn = self.GetChild2("prevBtn")
		self.nextBtn = self.GetChild2("nextBtn")
		self.prevBtn.SetEvent(ui.__mem_func__(self.__OnPrev))
		self.nextBtn.SetEvent(ui.__mem_func__(self.__OnNext))

		self.bg = ui.ImageBox()
		self.bg.SetParent(self.board)
		self.bg.LoadImage(RANKING_ART + "ranking_bg.png")
		self.bg.SetPosition(self.PANEL_MX, self.PANEL_MY)
		self.bg.AddFlag("not_pick")
		self.bg.Show()

		self.statTitle = self.__Banner(self.STAT_BANNER_Y, "GUILD_RANKING_STAT_TITLE", "Your Statistics")

		plateArt = ("state_contribution_bg.png", "state_rank_bg.png", "state_coins_bg.png")
		statKeys = ("GUILD_RANKING_STAT_CONTRIB", "GUILD_RANKING_STAT_RANK", "GUILD_RANKING_STAT_COINS")
		statDefs = ("Contribution", "Rank in Guild", "Guild Coins")
		self.statPlates = []
		for i in xrange(3):
			py = self.PLATE_Y[i]
			plate = self.__Img(plateArt[i], 2, py)
			lab = self.__Txt(self.LABEL_CX, py + 19, 0xffe8d9b5)
			lab.SetText(self.__L(statKeys[i], statDefs[i]))
			val = self.__Txt(self.VALUE_CX, py + 19, 0xffffffff)
			self.statPlates.append((plate, lab, val))

		self.topTitle = self.__Banner(self.TOP_BANNER_Y, "GUILD_RANKING_TOP_TITLE", "Top Contributors")

		rowArt = ("ranking_num_1.png", "ranking_num_2.png", "ranking_num_3.png", "ranking_num_general.png", "ranking_num_general.png")
		rowRankColor = (0xffffcc44, 0xffe0e0e0, 0xffd0a060, 0xff9a9a9a, 0xff9a9a9a)
		self.rows = []
		for i in xrange(5):
			ry = self.ROW_Y[i]
			img = self.__Img(rowArt[i], 6, ry)
			rk = self.__Txt(self.ROW_RANK_CX, ry + 10, rowRankColor[i])
			nm = self.__Txt(self.ROW_NAME_CX, ry + 10, 0xffdddddd)
			pt = self.__Txt(self.ROW_POINT_CX, ry + 10, 0xffffd700)
			self.rows.append((img, rk, nm, pt))

		self.Refresh()

	def __OnPrev(self):
		self.rankType = (self.rankType - 1) % self.TYPE_COUNT
		self.Refresh()

	def __OnNext(self):
		self.rankType = (self.rankType + 1) % self.TYPE_COUNT
		self.Refresh()

	def __TypeName(self):
		keys = ("GUILD_RANKING_TAB_WEEKLY", "GUILD_RANKING_TAB_ALLTIME", "GUILD_RANKING_TAB_COINS", "GUILD_RANKING_TAB_DUNGEON")
		defs = ("This Week", "All-Time", "Coins Earned", "Dungeon Runs")
		return self.__L(keys[self.rankType], defs[self.rankType])

	def __TopTitle(self):
		keys = ("GUILD_RANKING_TOP_TITLE", "GUILD_RANKING_TOP_ALLTIME", "GUILD_RANKING_TOP_COINS", "GUILD_RANKING_TOP_DUNGEON")
		defs = ("Top Contributors", "All-Time Leaders", "Top Earners", "Most Dungeon Runs")
		return self.__L(keys[self.rankType], defs[self.rankType])

	def __MemberMetric(self, pid):
		t = self.rankType
		if t == self.TYPE_ALLTIME and hasattr(guild, "GetMemberTotalContribution"):
			return guild.GetMemberTotalContribution(pid)
		if t == self.TYPE_COINS and hasattr(guild, "GetMemberCoinsEarned"):
			return guild.GetMemberCoinsEarned(pid)
		if t == self.TYPE_DUNGEON and hasattr(guild, "GetMemberDungeonRuns"):
			return guild.GetMemberDungeonRuns(pid)
		return guild.GetMemberContribution(pid)

	def Refresh(self):
		if not self.built:
			return
		self.board.SetTitleName("%s - %s" % (self.__L("GUILD_RANKING_TITLE", "Guild Ranking"), self.__TypeName()))
		self.topTitle.SetText(self.__TopTitle())

		contrib = 0
		coins = 0
		rank = 0
		if hasattr(guild, "GetMyContribution"):
			contrib = guild.GetMyContribution()
		if hasattr(guild, "GetMyGuildCoins"):
			coins = guild.GetMyGuildCoins()
		if hasattr(guild, "GetContractsMy"):
			my = guild.GetContractsMy()
			if my and len(my) > 3 and my[0]:
				rank = my[3] + 1
		vals = (self.__Num(contrib), ("#%d" % rank if rank > 0 else "-"), self.__Num(coins))
		for i in xrange(3):
			self.statPlates[i][2].SetText(vals[i])

		best = []
		for i in xrange(guild.GetMemberCount()):
			if not guild.IsMember(i):
				continue
			data = guild.GetMemberData(i)
			c = self.__MemberMetric(data[0])
			if c > 0:
				best.append((c, data[1]))
		best.sort(reverse=True)
		for i in xrange(5):
			img, rk, nm, pt = self.rows[i]
			img.Show()
			rk.SetText("" if i < 3 else str(i + 1))
			if i < len(best):
				c, name = best[i]
				nm.SetText(name)
				pt.SetText(self.__Num(c))
			else:
				nm.SetText("-")
				pt.SetText("-")

	def OpenCentered(self):
		self.Refresh()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def OnUpdate(self):
		if not self.IsShow():
			return
		now = app.GetTime()
		if now < self.nextRefresh:
			return
		self.nextRefresh = now + 1.0
		self.Refresh()

	def Close(self):
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True


class GuildWindow(ui.ScriptWindow):
	JOB_NAME = {
		0 : localeinfo.JOB_WARRIOR,
		1 : localeinfo.JOB_ASSASSIN,
		2 : localeinfo.JOB_SURA,
		3 : localeinfo.JOB_SHAMAN,
		4 : localeinfo.JOB_WOLFMAN,
	}

	GUILD_SKILL_PASSIVE_SLOT = 0
	GUILD_SKILL_ACTIVE_SLOT = 1
	GUILD_SKILL_AFFECT_SLOT = 2

	GRADE_SLOT_NAME = 0
	GRADE_ADD_MEMBER_AUTHORITY = 1
	GRADE_REMOVE_MEMBER_AUTHORITY = 2
	GRADE_NOTICE_AUTHORITY = 3
	GRADE_SKILL_AUTHORITY = 4

	ROLES_SLOT_NAME = 0
	ROLES_SLOT_INVITE = 1
	ROLES_SLOT_KICK = 2
	ROLES_SLOT_NOTICE = 3
	ROLES_SLOT_SKILL = 4
	ROLES_SLOT_CONTRACT = 5
	ROLES_SLOT_LEARN = 6

	MEMBER_LINE_COUNT = 13

	class PageWindow(ui.ScriptWindow):
		def __init__(self, parent, filename):
			ui.ScriptWindow.__init__(self)
			self.SetParent(parent)
			self.filename = filename

		def __del__(self):
			ui.ScriptWindow.__del__(self)

		def GetScriptFileName(self):
			return self.filename

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.isLoaded=0

		if app.ENABLE_GUILD_RENEWAL:
			self.wndGuildMission = uiguildmission.GuildMissionWindow()

		self.__Initialize()

		if app.ENABLE_GUILD_FINDER:
			self.guildFinderEvent = lambda *arg: None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __Initialize(self):
		self.board = None
		self.pageName = None
		self.tabDict = None
		self.tabButtonDict = None
		self.questionDialog = None
		self.donate_exp_dlg = None
		self.donate_sp_dlg = None
		self.popupDialog = None
		self.moneyDialog = None
		self.changeGradeNameDialog = None
		self.rolesPopup = None
		self.popup = None
		self.dyeWindow = None
		self.dyeButton = None
		if app.ENABLE_GUILD_FINDER:
			self.finderButton = None

		self.popupMessage = None
		self.commentSlot = None
		self.currentPage = ""

		self.pageWindow = None
		self.tooltipSkill = None

		self.memberLinePos = 0

		self.enemyGuildNameList = []

		if app.ENABLE_GUILD_PASSIVE_SKILLS:
			self.passiveSkillDescList = []


		if app.ENABLE_GUILD_DONATE:
			self.wndDonate = None

		self.buttontooltip = None
		self.ShowButtonToolTip = False

		self.contractCards = []
		self.tierRows = []
		self.contractsFooter = None
		self.contractsTopLine = None
		self.progressionWidgets = None
		self.contractTypeNames = []
		self.contractsQuestion = None
		self.contractsPollTime = 0.0
		self.contractsRecvTime = 0.0
		self.contractsCountdownTime = 0.0
		self.weeklyBoxes = None
		self.boxResetLeft = 0
		self.rankingPopup = None
		self.contractsRankBtn = None
		self.cardMarqueeHot = None
		self.cardMarqueeOffset = 0.0
		self.cardMarqueeDone = False
		self.cardMarqueeSince = 0.0
		self.cardMarqueeTime = 0.0
		self.cardTipZone = None
		self.contractTip = None
		self.contractPreviewBoard = None
		self.contractPreviewRT = None
		self.contractPreviewName = None
		self.contractPreviewHint = None
		self.contractArtTip = None
		self.contractWiki = None
		self.pendingRerollSlot = -1
		self.pendingRallySlot = -1
		self.pendingLevelUpCost = 0
		self.pendingLevelUpLevel = 0
		self.donatePickDlg = None
		self.donatePendingKind = -1
		self.donateStarPendingIndex = -1
		self.donateRefreshTime = 0.0
		self.wndStock = None
		self.gdW = {}
		self.gdRankRows = []
		self.gdHeader = None
		self.gdSelTier = 1
		self.gdCrestTier = 0
		self.gdMode = ""
		self.gpFirstLine = None
		self.gpFirstPoll = 0.0
		self.gdPollTime = 0.0
		self.gdTickTime = 0.0
		self.gdOfficer = 0
		self.gdDaily = (0, 0)
		self.gdWeekly = (0, 0)
		self.gdCooldownUntil = 0.0
		self.gdTiers = {}
		self.gdChests = {}
		self.gdMarqTime = 0.0
		self.gdMarqSince = 0.0
		self.gdMarqOffset = 0.0
		self.gdMarqDone = False
		self.gdMarqHot = False
		self.gdChestText = ""
		self.gdChestFullW = 0
		self.gdChestH = 0
		self.gdChestBaseX = 0
		self.gdTops = {}
		self.gdLive = (0, 0.0)
		self.gdPendingStartTier = 0

		if app.ENABLE_GUILD_RENEWAL:
			self.bLoadedRenewInfo = False
			self.dPassiveInfo = {}
			self.dLevelInfo = {}
			self.dlgQuestionLvUp = None

	def Open(self):
		self.Show()
		self.SetTop()

		guildID = guild.GetGuildID()
		self.largeMarkBox.SetIndex(guildID)
		self.largeMarkBox.SetScale(3)
		if GUILD_CONTRACTS_UI and self.currentPage == "GUILD_INFO":
			self.__ShowStockWindow()

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "guild_window")

		self.__CloseAllGuildMemberPageGradeComboBox()

		if self.donate_exp_dlg:
			self.donate_exp_dlg.Close()

		if self.donate_sp_dlg:
			self.donate_sp_dlg.Close()

		self.popupDialog.Hide()
		self.changeGradeNameDialog.Hide()
		self.tooltipSkill.Hide()
		if app.ENABLE_GUILD_DONATE and self.wndDonate:
			self.wndDonate.Hide()

		self.Hide()

		self.questionDialog = None
		self.popup = None
		if self.buttontooltip:
			self.buttontooltip.Hide()
			self.ShowButtonToolTip = False

	def Hide(self):
		if GUILD_CONTRACTS_UI:
			self.__HideStockWindow()
			self.__CloseLevelUpPopup()
			if getattr(self, "donatePopup", None):
				self.donatePopup.Hide()
			if getattr(self, "contractPreviewBoard", None):
				self.contractPreviewBoard.Hide()
			if getattr(self, "contractArtTip", None):
				self.contractArtTip.Hide()
			if getattr(self, "gdTip", None):
				self.gdTip.Hide()
			if getattr(self, "rankingPopup", None) and self.rankingPopup.IsShow():
				self.rankingPopup.Hide()
		ui.ScriptWindow.Hide(self)

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("guild_window", x, y)
		if GUILD_CONTRACTS_UI:
			self.__PositionStockWindow()

	def Destroy(self):
		if app.ENABLE_GUILD_RENEWAL:
			if self.guildMission:
				self.guildMission.SetEvent(None)
				del self.guildMission
				self.guildMission = None

			if self.wndGuildMission:
				self.wndGuildMission.Destroy()
				del self.wndGuildMission
				self.wndGuildMission = None

			if self.dlgQuestionLvUp:
				self.dlgQuestionLvUp.Destroy()
				del self.dlgQuestionLvUp
				self.dlgQuestionLvUp = None

		if self.donate_exp_dlg:
			self.donate_exp_dlg.Destroy()
			del self.donate_exp_dlg
			self.donate_exp_dlg = None

		if self.donate_sp_dlg:
			self.donate_sp_dlg.Destroy()
			del self.donate_sp_dlg
			self.donate_sp_dlg = None

		self.ClearDictionary()

		if self.popupDialog:
			self.popupDialog.ClearDictionary()

		if self.changeGradeNameDialog:
			self.changeGradeNameDialog.ClearDictionary()

		if self.pageWindow:
			for window in self.pageWindow.values():
				window.ClearDictionary()

		if app.ENABLE_GUILD_DONATE:
			if self.wndDonate:
				self.wndDonate.Close()
				self.wndDonate.Destory()
				del self.wndDonate

		if self.rankingPopup:
			self.rankingPopup.Destroy()
			del self.rankingPopup
			self.rankingPopup = None

		if app.ENABLE_GUILD_FINDER:
			uibadge.Detach("guild_finder")

		self.__Initialize()

	def Show(self):
		if self.isLoaded == 0:
			self.isLoaded = 1

			self.__LoadWindow()

		if app.ENABLE_GUILD_FINDER:
			self.__RefreshGuildFinderButton()

		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "guild_window")

		if app.ENABLE_GUILD_RENEWAL and self.bLoadedRenewInfo == False and not GUILD_SKILLS_UI:
			net.SendChatPacket("/guild_renew info")
			self.bLoadedRenewInfo = True
			return

		self.RefreshGuildInfoPage()
		self.RefreshGuildBoardPage()
		self.RefreshGuildMemberPage()
		self.RefreshGuildSkillPage()
		self.RefreshGuildGradePage()

		ui.ScriptWindow.Show(self)

	def __LoadWindow(self):
		global DISABLE_GUILD_SKILL
		try:
			pyScrLoader = ui.PythonScriptLoader()

			if localeinfo.IsARABIC() :
				pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "guildwindow.py")
			else:
				pyScrLoader.LoadScriptFile(self, "uiscript/guildwindow.py")
				
			self.buttontooltip = uitooltip.ToolTip()
			self.buttontooltip.ClearToolTip()
			
			self.popupDialog = ui.ScriptWindow()
			pyScrLoader.LoadScriptFile(self.popupDialog, "UIScript/PopupDialog.py")

			self.changeGradeNameDialog = ChangeGradeNameDialog()
			pyScrLoader.LoadScriptFile(self.changeGradeNameDialog, "uiscript/changegradenamedialog.py")

			self.rolesPopup = RolesPopup()
			pyScrLoader.LoadScriptFile(self.rolesPopup, "uiscript/guildwindow_rolespopup.py")

			if localeinfo.IsARABIC():
				self.pageWindow = {
					"GUILD_INFO"	: self.PageWindow(self, "uiscript/guildwindow_guildinfopage_eu.py"),
					"BOARD"			: self.PageWindow(self, "uiscript/guildwindow_boardpage.py"),
					"MEMBER"		: self.PageWindow(self, "uiscript/guildwindow_memberpage.py"),
					"BASE_INFO"		: self.PageWindow(self, "uiscript/guildwindow_baseinfopage.py"),
					"SKILL"			: self.PageWindow(self, "uiscript/guildwindow_guildskillpage_renewed.py" if app.ENABLE_GUILD_RENEWAL else "uiscript/guildwindow_guildskillpage.py"),
					"GRADE"			: self.PageWindow(self, "uiscript/guildwindow_gradepage.py"),
				}
			elif localeinfo.IsJAPAN() :
				self.pageWindow = {
					"GUILD_INFO"	: self.PageWindow(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "guildwindow_guildinfopage.py"),
					"BOARD"			: self.PageWindow(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "guildwindow_boardpage.py"),
					"MEMBER"		: self.PageWindow(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "guildwindow_memberpage.py"),
					"BASE_INFO"		: self.PageWindow(self, "uiscript/guildwindow_baseinfopage.py"),
					"SKILL"			: self.PageWindow(self, "uiscript/guildwindow_guildskillpage_renewed.py" if app.ENABLE_GUILD_RENEWAL else "uiscript/guildwindow_guildskillpage.py"),
					"GRADE"			: self.PageWindow(self, "uiscript/guildwindow_gradepage.py"),
				}
			elif localeinfo.IsVIETNAM() :
				self.pageWindow = {
					"GUILD_INFO"	: self.PageWindow(self, "uiscript/guildwindow_guildinfopage_eu.py"),
					"BOARD"			: self.PageWindow(self, "uiscript/guildwindow_boardpage.py"),
					"MEMBER"		: self.PageWindow(self, "uiscript/guildwindow_memberpage.py"),
					"BASE_INFO"		: self.PageWindow(self, "uiscript/guildwindow_baseinfopage.py"),
					"SKILL"			: self.PageWindow(self, "{}/guildwindow_guildskillpage_renewed.py".format(uiscriptlocale.LOCALE_UISCRIPT_PATH) if app.ENABLE_GUILD_RENEWAL else "{}/guildwindow_guildskillpage.py".format(uiscriptlocale.LOCALE_UISCRIPT_PATH)),
					"GRADE"			: self.PageWindow(self, "uiscript/guildwindow_gradepage.py"),
				}
			elif localeinfo.IsEUROPE() and not app.GetLocalePath() == "locale/ca" :
				self.pageWindow = {
					"GUILD_INFO"	: self.PageWindow(self, "uiscript/guildwindow_guildinfopage_eu.py"),
					"BOARD"			: self.PageWindow(self, "uiscript/guildwindow_boardpage.py"),
					"MEMBER"		: self.PageWindow(self, "uiscript/guildwindow_memberpage.py"),
					"BASE_INFO"		: self.PageWindow(self, "uiscript/guildwindow_baseinfopage.py"),
					"SKILL"			: self.PageWindow(self, "uiscript/guildwindow_guildskillpage_renewed.py" if app.ENABLE_GUILD_RENEWAL else "uiscript/guildwindow_guildskillpage.py"),
					"GRADE"			: self.PageWindow(self, "uiscript/guildwindow_gradepage.py"),
				}
			else:
				self.pageWindow = {
					"GUILD_INFO"	: self.PageWindow(self, "uiscript/guildwindow_guildinfopage.py"),
					"BOARD"			: self.PageWindow(self, "uiscript/guildwindow_boardpage.py"),
					"MEMBER"		: self.PageWindow(self, "uiscript/guildwindow_memberpage.py"),
					"BASE_INFO"		: self.PageWindow(self, "uiscript/guildwindow_baseinfopage.py"),
					"SKILL"			: self.PageWindow(self, "uiscript/guildwindow_guildskillpage_renewed.py" if app.ENABLE_GUILD_RENEWAL else "uiscript/guildwindow_guildskillpage.py"),
					"GRADE"			: self.PageWindow(self, "uiscript/guildwindow_gradepage.py"),
				}

			if GUILD_CONTRACTS_UI:
				self.pageWindow["BOARD"] = self.PageWindow(self, "uiscript/guildwindow_contractspage.py")
				self.pageWindow["BASE_INFO"] = self.PageWindow(self, "uiscript/guildwindow_progressionpage.py")
			if GUILD_SKILLS_UI:
				self.pageWindow["SKILL"] = self.PageWindow(self, "uiscript/guildwindow_skillspage.py")

			for window in self.pageWindow.values():
				pyScrLoader.LoadScriptFile(window, window.GetScriptFileName())

		except:
			import exception
			exception.Abort("GuildWindow.__LoadWindow.LoadScript")

		try:
			getObject = self.GetChild

			self.board = getObject("Board")
			self.pageName = {
				"GUILD_INFO"	: localeinfo.GUILD_TILE_INFO,
				"BOARD"			: localeinfo.GUILD_TILE_BOARD,
				"MEMBER"		: localeinfo.GUILD_TILE_MEMBER,
				"BASE_INFO"		: localeinfo.GUILD_TILE_BASEINFO,
				"SKILL"			: localeinfo.GUILD_TILE_SKILL,
				"GRADE"			: localeinfo.GUILD_TILE_GRADE,
			}
			if GUILD_CONTRACTS_UI:
				self.pageName["BOARD"] = getattr(localeinfo, "GUILD_CONTRACTS_PAGE_TITLE", "Contracts")
				self.pageName["BASE_INFO"] = getattr(localeinfo, "GUILD_PROGRESSION_PAGE_TITLE", "Progression")
				if GUILD_DUNGEON_UI:
					self.pageName["BASE_INFO"] = getattr(localeinfo, "GUILD_DUNGEON_PAGE_TITLE", "Dungeon")

			self.tabDict = {
				"GUILD_INFO"	: getObject("Tab_01"),
				"BOARD"			: getObject("Tab_02"),
				"MEMBER"		: getObject("Tab_03"),
				"BASE_INFO"		: getObject("Tab_04"),
				"SKILL"			: getObject("Tab_05"),
				"GRADE"			: getObject("Tab_06"),
			}
			self.tabButtonDict = {
				"GUILD_INFO"	: getObject("Tab_Button_01"),
				"BOARD"			: getObject("Tab_Button_02"),
				"MEMBER"		: getObject("Tab_Button_03"),
				"BASE_INFO"		: getObject("Tab_Button_04"),
				"SKILL"			: getObject("Tab_Button_05"),
				"GRADE"			: getObject("Tab_Button_06"),
			}

			## QuestionDialog
			self.popupMessage = self.popupDialog.GetChild("message")
			self.popupDialog.GetChild("accept").SetEvent(ui.__mem_func__(self.popupDialog.Hide))

			## ChangeGradeName
			self.changeGradeNameDialog.GetChild("AcceptButton").SetEvent(ui.__mem_func__(self.OnChangeGradeName))
			self.changeGradeNameDialog.GetChild("CancelButton").SetEvent(ui.__mem_func__(self.changeGradeNameDialog.Hide))
			self.changeGradeNameDialog.GetChild("Board").SetCloseEvent(ui.__mem_func__(self.changeGradeNameDialog.Hide))
			self.changeGradeNameDialog.gradeNameSlot = self.changeGradeNameDialog.GetChild("GradeNameValue")
			self.changeGradeNameDialog.gradeNameSlot.OnIMEReturn = ui.__mem_func__(self.OnChangeGradeName)
			self.changeGradeNameDialog.gradeNameSlot.OnPressEscapeKey = ui.__mem_func__(self.changeGradeNameDialog.Close)

			## RolesPopup
			self.rolesPopup.GetChild("Board").SetCloseEvent(ui.__mem_func__(self.rolesPopup.Hide))

			## Comment
			if not GUILD_CONTRACTS_UI:
				self.commentSlot = self.pageWindow["BOARD"].GetChild("CommentValue")
				self.commentSlot.OnIMEReturn = ui.__mem_func__(self.OnPostComment)
				self.commentSlot.OnKeyDown = ui.__mem_func__(self.OnKeyDownInBoardPage)

				## RefreshButton
				self.pageWindow["BOARD"].GetChild("RefreshButton").SetEvent(ui.__mem_func__(self.OnRefreshComments))

			## ScrollBar
			scrollBar = self.pageWindow["MEMBER"].GetChild("ScrollBar")
			scrollBar.SetScrollEvent(ui.__mem_func__(self.OnScrollMemberLine))
			self.pageWindow["MEMBER"].scrollBar = scrollBar

		except:
			import exception
			exception.Abort("GuildWindow.__LoadWindow.BindObject")

		self.__MakeInfoPage()
		if GUILD_CONTRACTS_UI:
			self.__MakeContractsPage()
		else:
			self.__MakeBoardPage()
		self.__MakeMemberPage()
		if GUILD_CONTRACTS_UI:
			if GUILD_DUNGEON_UI:
				self.__MakeDungeonPage()
			else:
				self.__MakeProgressionPage()
		else:
			self.__MakeBaseInfoPage()
		if GUILD_SKILLS_UI:
			self.__MakeGuildSkillsPage()
		else:
			self.__MakeSkillPage()
		self.__MakeGradePage()
		self.__MakeRolesPopup()

		for page in self.pageWindow.values():
			page.UpdateRect()

		for key, btn in self.tabButtonDict.items():
			if "GRADE" == key:
				btn.SetEvent(ui.__mem_func__(self.OnOpenRolesPopup))
				btn.ShowToolTip = lambda arg = getattr(localeinfo, "GUILD_ROLES_OPEN", "Manage grade roles") : self.OverInToolTipButton(arg)
				btn.HideToolTip = lambda : self.OverOutToolTipButton()
			else:
				btn.SetEvent(ui.__mem_func__(self.SelectPage), key)

		if not GUILD_CONTRACTS_UI:
			self.tabButtonDict["BASE_INFO"].Disable()
		elif not GUILD_DUNGEON_UI:
			self.tabButtonDict["BASE_INFO"].Hide()
			self.tabDict["BASE_INFO"].Hide()

		if DISABLE_GUILD_SKILL:
			self.tabButtonDict["SKILL"].Disable()

		self.board.SetCloseEvent(ui.__mem_func__(self.Close))
		self.board.SetTitleColor(0xffffffff)
		if app.ENABLE_GUILD_FINDER:
			self.__MakeGuildFinderButton()
		self.SelectPage("GUILD_INFO")

	if app.ENABLE_GUILD_FINDER:
		def SetGuildFinderEvent(self, event):
			self.guildFinderEvent = event

		def __MakeGuildFinderButton(self):
			btn = ui.Button()
			btn.SetParent(self.pageWindow["GUILD_INFO"])
			btn.SetPosition(int(GF_BTN_X), int(GF_BTN_Y))
			btn.SetUpVisual(GF_BTN_UP)
			btn.SetOverVisual(GF_BTN_OVER)
			btn.SetDownVisual(GF_BTN_DOWN)
			label = getattr(localeinfo, "GUILD_FINDER_TITLE", "")
			if not label or label.startswith("Locale not found"):
				label = "Guild Finder"
			btn.SetText(label)
			btn.SetTextPosition(10, -1)
			btn.SetOutline()
			btn.SetEvent(ui.__mem_func__(self.__OnClickGuildFinder))
			btn.Hide()
			self.finderButton = btn
			uibadge.Attach("guild_finder", btn)

		# mirrors GFHasManageAuth (game/guild_finder.cpp): only the master and
		# invite-grade officers can act on the Applications tab
		def __CanManageApplications(self):
			if guild.GetGuildID() == 0:
				return False
			if guild.GetGuildMasterName() == player.GetMainCharacterName():
				return True
			return guild.MainPlayerHasAuthority(guild.AUTH_ADD_MEMBER) != 0

		def __RefreshGuildFinderButton(self):
			btn = getattr(self, "finderButton", None)
			if not btn:
				return
			if self.__CanManageApplications():
				btn.Show()
			else:
				btn.Hide()

		def __OnClickGuildFinder(self):
			event = getattr(self, "guildFinderEvent", None)
			if event:
				event()

	def OverInToolTipButton(self, arg):
		arglen = len(str(arg))
		pos_x, pos_y = wndMgr.GetMousePosition()

		self.buttontooltip.ClearToolTip()
		self.buttontooltip.SetThinBoardSize(11 * arglen)
		self.buttontooltip.SetToolTipPosition(pos_x + 50, pos_y + 50)
		self.buttontooltip.AppendTextLine(arg, 0xffffffff)
		self.buttontooltip.Show()
		self.ShowButtonToolTip = True

	def OverOutToolTipButton(self):
		self.buttontooltip.Hide()
		self.ShowButtonToolTip = False

	def ButtonToolTipProgress(self) :
		if self.ShowButtonToolTip :
			pos_x, pos_y = wndMgr.GetMousePosition()
			self.buttontooltip.SetToolTipPosition(pos_x + 50, pos_y + 50)

	def OnUpdate(self):
		self.ButtonToolTipProgress()
		self.__RefreshDyeButton()
		if GUILD_CONTRACTS_UI and self.isLoaded and self.IsShow() and net.GetMainActorVID() != 0 and self.currentPage in ("GUILD_INFO", "BOARD", "BASE_INFO"):
			now = app.GetTime()
			if now >= self.contractsPollTime:
				self.contractsPollTime = now + 3.0
				net.SendGuildContractsSnapshotPacket()
			if self.contractCards and now >= self.contractsCountdownTime:
				self.contractsCountdownTime = now + 1.0
				self.__UpdateContractStateLine(1)
				self.__UpdateBoxCountdown()
		if GUILD_CONTRACTS_UI and self.contractCards:
			if self.isLoaded and self.IsShow() and self.currentPage == "BOARD":
				self.__ContractHoverTick(app.GetTime())
			elif self.cardMarqueeHot is not None or self.cardTipZone is not None:
				self.__ContractHoverClear()
		if GUILD_DUNGEON_UI and self.isLoaded and self.IsShow() and net.GetMainActorVID() != 0 and self.currentPage == "BASE_INFO":
			gdNow = app.GetTime()
			if gdNow >= self.gdPollTime:
				self.gdPollTime = gdNow + 8.0
				net.SendChatPacket("/gd_info")
			if gdNow >= self.gdTickTime:
				self.gdTickTime = gdNow + 1.0
				self.__RefreshDungeonPage()
			self.__GdTextTick(gdNow)
		if GUILD_DONATION_UI and self.isLoaded and self.IsShow() and self.currentPage == "GUILD_INFO":
			donateNow = app.GetTime()
			if donateNow >= getattr(self, "donateRefreshTime", 0.0):
				self.donateRefreshTime = donateNow + 5.0
				self.__RefreshDonateRows(self.pageWindow["GUILD_INFO"])
				
		if GUILD_SKILLS_UI and self.isLoaded and self.IsShow() and net.GetMainActorVID() != 0 and self.currentPage == "SKILL":
			skillNow = app.GetTime()
			if skillNow >= getattr(self, "skillsPollTime", 0.0):
				self.skillsPollTime = skillNow + 3.0
				net.SendGuildSkillsSnapshotPacket()
			if skillNow >= getattr(self, "skillsTickTime", 0.0):
				self.skillsTickTime = skillNow + 1.0
				self.__RefreshGuildSkillTimers()
				self.__RefreshGuildSkillDetail()

	def __RefreshDyeButton(self):
		# Guild Name Dye: a small entry button that appears only while the guild's
		# dye is active; opens the colour picker. Placement is provisional (one
		# SetPosition line) pending the guild-window redesign.
		if not GUILD_DYE_UI or not self.isLoaded or not self.IsShow():
			return
		try:
			active = guild.GetGuildID() != 0 and guild.GetGuildDyeColor() != 0
		except Exception:
			active = 0
		if active:
			if not self.dyeButton:
				b = ui.Button()
				b.SetParent(self)
				b.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
				b.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
				b.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
				b.SetText(getattr(localeinfo, "GUILD_DYE_CHANGE_BTN", "Colour"))
				b.SetEvent(ui.__mem_func__(self.__OpenDyeWindow))
				try:
					b.SetPosition(self.GetWidth() - b.GetWidth() - 16, self.GetHeight() - 34)
				except Exception:
					b.SetPosition(150, 300)
				b.Show()
				self.dyeButton = b
			else:
				self.dyeButton.Show()
		elif self.dyeButton:
			self.dyeButton.Hide()

	def __OpenDyeWindow(self):
		if not GUILD_DYE_UI:
			return
		if not self.dyeWindow:
			self.dyeWindow = uiguilddye.GuildDyeColorWindow()
		self.dyeWindow.Open()

	def __L(self, key, default):
		v = getattr(localeinfo, key, default)
		try:
			if "not found" in v:
				return default
		except TypeError:
			pass
		return v

	def __InfoLabel(self, page, key, default, y, arX=349, enX=318):
		t = ui.TextLine()
		t.SetParent(page)
		t.SetVerticalAlignCenter()
		if localeinfo.IsARABIC():
			t.SetPosition(arX, y)
			t.SetHorizontalAlignLeft()
		else:
			t.SetPosition(enX, y)
			t.SetHorizontalAlignCenter()
		t.SetText(self.__L(key, default))
		t.SetPackedFontColor(0xffcabdab)
		t.Show()
		page.infoWidgets.append(t)
		return t

	def __InfoValue(self, page, y, cx=232):
		t = ui.TextLine()
		t.SetParent(page)
		t.SetPosition(cx, y)
		t.SetHorizontalAlignCenter()
		t.SetVerticalAlignCenter()
		t.SetPackedFontColor(0xffd1b183)
		t.SetText("")
		t.Show()
		page.infoWidgets.append(t)
		return t

	def __MakeInfoPageNew(self, page):
		for name in ("Guild_Info_Title_Bar", "Guild_Mark_Title_Bar", "OfferButton", "UploadGuildMarkButton", "UploadGuildSymbolButton", "DeclareWarButton"):
			child = page.GetChild2(name)
			if child:
				child.Hide()

		page.infoWidgets = []
		page.infoValues = {}
		rtl = localeinfo.IsARABIC()
		BX, BY = 4, 0

		bg = ui.ImageBox()
		bg.SetParent(page)
		bg.SetPosition(BX, BY)
		bg.LoadImage("d:/ymir work/ui/new_guild/info_page/new_bg_main.png")
		bg.Show()
		page.infoBg = bg
		page.infoWidgets.append(bg)

		VX = BX + 208
		LX = BX + 306
		rows = (
			("name", "GUILD_OV_L_NAME", "GUILD", 1),
			("leader", "GUILD_OV_L_LEADER", "LEADER", 2),
			("rep", "GUILD_OV_L_REP", "REPUTATION", 3),
			("level", "GUILD_OV_L_LEVEL", "LEVEL", 4),
			("grank", "GUILD_OV_L_GRANK", "GUILD RANK", 6),
			("members", "GUILD_OV_L_MEMBERS", "MEMBERS", 7),
			("gold", "GUILD_OV_L_YANG", "GUILD YANG", 8),
			("coins", "GUILD_OV_L_COIN", "YOUR COIN", 9),
			("contrib", "GUILD_OV_L_CONTRIB", "CONTRIBUTION", 10),
			("myrank", "GUILD_OV_L_MYRANK", "YOUR RANK", 11),
		)
		for rid, key, default, rowNo in rows:
			cy = 20 + (rowNo - 1) * 24 + 12
			lab = ui.TextLine()
			lab.SetParent(page)
			lab.SetPosition(LX, cy)
			lab.SetHorizontalAlignCenter()
			lab.SetVerticalAlignCenter()
			lab.SetText(self.__L(key, default))
			lab.SetPackedFontColor(0xffcabdab)
			lab.Show()
			page.infoWidgets.append(lab)
			val = ui.TextLine()
			val.SetParent(page)
			val.SetPosition(VX, cy)
			val.SetHorizontalAlignCenter()
			val.SetVerticalAlignCenter()
			val.SetPackedFontColor(0xffd1b183)
			val.SetText("")
			val.Show()
			page.infoWidgets.append(val)
			page.infoValues[rid] = val

		gy = 20 + 4 * 24 + 2
		gaugeBase = ui.ImageBox()
		gaugeBase.SetParent(page)
		gaugeBase.SetPosition(BX + 160, gy)
		gaugeBase.LoadImage("d:/ymir work/ui/new_guild/info_page/gauge_empty.png")
		gaugeBase.AddFlag("not_pick")
		gaugeBase.Show()
		page.infoWidgets.append(gaugeBase)

		gaugeFill = ui.ExpandedImageBox()
		gaugeFill.SetParent(gaugeBase)
		gaugeFill.SetPosition(0, 0)
		gaugeFill.LoadImage("d:/ymir work/ui/new_guild/info_page/gauge_full.png")
		gaugeFill.SetRenderingRect(0.0, 0.0, -1.0, 0.0)
		gaugeFill.AddFlag("not_pick")
		gaugeFill.Show()
		page.infoGaugeFill = gaugeFill
		page.infoWidgets.append(gaugeFill)

		gaugeTxt = ui.TextLine()
		gaugeTxt.SetParent(gaugeBase)
		gaugeTxt.SetPosition(63, 10)
		gaugeTxt.SetHorizontalAlignCenter()
		gaugeTxt.SetVerticalAlignCenter()
		gaugeTxt.SetOutline()
		gaugeTxt.AddFlag("not_pick")
		gaugeTxt.SetPackedFontColor(0xffffffff)
		gaugeTxt.SetText("")
		gaugeTxt.Show()
		page.infoGaugeTxt = gaugeTxt
		page.infoWidgets.append(gaugeTxt)

		expLabel = ui.TextLine()
		expLabel.SetParent(page)
		expLabel.SetPosition(BX + 320, 128)
		expLabel.SetHorizontalAlignCenter()
		expLabel.SetVerticalAlignCenter()
		expLabel.SetPackedFontColor(0xffcabdab)
		expLabel.SetText(self.__L("GUILD_OV_EXP", "EXP"))
		expLabel.Show()
		page.infoWidgets.append(expLabel)

		def zone(px, py, pw, ph, ev):
			z = ui.Window()
			z.SetParent(page)
			z.SetPosition(px, py)
			z.SetSize(pw, ph)
			z.SetOverInEvent(ui.__mem_func__(ev))
			z.SetOverOutEvent(ui.__mem_func__(self.__HideTermTip))
			z.Show()
			page.infoWidgets.append(z)
		zone(BX + 157, 68, 102, 24, self.__ShowRepTip)
		zone(BX + 160, 116, 127, 24, self.__ShowActivityTip)
		zone(BX + 157, 212, 102, 24, self.__ShowCoinsTip)
		zone(BX + 157, 236, 102, 24, self.__ShowContribTip)

		firstLine = ui.TextLine()
		firstLine.SetParent(page)
		firstLine.SetPosition(280, 296)
		firstLine.SetHorizontalAlignCenter()
		firstLine.SetPackedFontColor(0xffcda05a)
		firstLine.SetText("")
		firstLine.Show()
		page.infoWidgets.append(firstLine)
		self.gpFirstLine = firstLine

		oldSlot = page.GetChild2("LargeGuildMarkSlot")
		if oldSlot:
			oldSlot.Hide()
		emblem = ui.MarkBox()
		emblem.SetParent(page)
		emblem.SetIndex(guild.GetGuildID())
		emblem.SetScale(3)
		emblem.SetPosition(59, 39)
		emblem.SetTop()
		emblem.Show()
		page.emblemMark = emblem
		self.infoEmblem = emblem

		panelCX = BX + 79
		def actBtn(base, y, w, ev):
			b = ui.Button()
			b.SetParent(page)
			b.SetPosition(int(panelCX - w / 2), y)
			b.SetUpVisual("d:/ymir work/ui/new_guild/info_page/" + base + ".png")
			b.SetOverVisual("d:/ymir work/ui/new_guild/info_page/" + base + "_1.png")
			b.SetDownVisual("d:/ymir work/ui/new_guild/info_page/" + base + "_2.png")
			if ev:
				b.SetEvent(ui.__mem_func__(ev))
			b.Show()
			page.infoWidgets.append(b)
			return b

		page.btnUpload = actBtn("upload_button", 84, 120, self.__OnClickSelectGuildMarkButton)
		page.btnUpload.SetText(localeinfo.GUILD_MARK_NAME)
		page.btnUpload.SetOutline()

		page.btnDonate = actBtn("donate_button", 236, 108, self.__ToggleStockWindow)
		page.btnDonate.SetText(localeinfo.GUILD_OV_DONATE)
		page.btnDonate.SetTextPosition(10,-1)
		page.btnDonate.SetOutline()

		#page.btnAnnounce = actBtn("announce_button", 146, 108, None)
		page.btnWar = actBtn("war_button", 175, 108, self.__OnClickDeclareWarButton)
		page.btnWar.SetText(uiscriptlocale.GUILD_INFO_DECALRE_WAR)
		page.btnWar.SetTextPosition(10,-1)
		page.btnWar.SetOutline()

		page.btnLevelUp = actBtn("levelup_button", 265, 140, self.__OpenLevelUpPopup)
		page.btnLevelUp.SetText(uiscriptlocale.PET_INFORMATION_EVOL_BUTTON)
		page.btnLevelUp.SetTextPosition(10,-1)
		page.btnLevelUp.SetOutline()

		#page.btnRecall = actBtn("recall_button", 224, 108, None)
		#page.btnAlliance = actBtn("alliance_button", 250, 108, None)
		if getattr(net, "SendGuildOpenMerchant", None):
			page.btnGuildShop = actBtn("alliance_button", 205, 108, self.__OnClickGuildShopButton)
			page.btnGuildShop.SetText(getattr(localeinfo, "GUILD_SHOP_BUTTON", "Guild Shop"))
			page.btnGuildShop.SetOutline()
			page.btnGuildShop.SetTextPosition(10,-1)

		self.__MakeStockWindow(page)

	def __RefreshInfoPageNew(self):
		page = self.pageWindow["GUILD_INFO"]
		vals = getattr(page, "infoValues", None)
		if not vals:
			return
		emblem = getattr(self, "infoEmblem", None)
		if emblem:
			emblem.SetIndex(guild.GetGuildID())
			emblem.SetScale(3)
		vals["name"].SetText(guild.GetGuildName())
		vals["leader"].SetText(guild.GetGuildMasterName())
		if hasattr(guild, "GetGuildReputation"):
			vals["rep"].SetText(str(guild.GetGuildReputation()))
		if hasattr(guild, "GetGuildProgression"):
			level, maxLevel, exp, milestone, yangCost, vault = guild.GetGuildProgression()
			pct = 0.0
			if milestone > 0:
				pct = min(1.0, max(0.0, float(exp) / float(milestone)))
			fill = getattr(page, "infoGaugeFill", None)
			if fill:
				fill.SetRenderingRect(0.0, 0.0, -1.0 + pct, 0.0)
			txt = getattr(page, "infoGaugeTxt", None)
			if txt:
				txt.SetText("%s / %s" % (self.__CompactCount(exp), self.__CompactCount(milestone)))
		money = guild.GetGuildMoney()
		moneyFmt = getattr(localeinfo, "NumberToMoneyString", None)
		vals["gold"].SetText(moneyFmt(money) if moneyFmt else str(money))
		cur, mx = guild.GetGuildMemberCount()
		if mx == 0xffff:
			vals["members"].SetText("%d / %s" % (cur, localeinfo.GUILD_MEMBER_COUNT_INFINITY))
		else:
			vals["members"].SetText("%d / %d" % (cur, mx))
		vals["level"].SetText(str(guild.GetGuildLevel()))

		if hasattr(guild, "GetContractsMy") and "coins" in vals:
			my = guild.GetContractsMy()
			vals["coins"].SetText(str(guild.GetMyGuildCoins()))
			if my[0]:
				vals["contrib"].SetText(str(my[1]))
				vals["myrank"].SetText("#%d" % (my[3] + 1))
				grank = my[5]
				vals["grank"].SetText(("#%d" % grank) if grank > 0 else "-")

		self.__RefreshStockWindow(page)
		if getattr(self, "donatePopup", None) and self.donatePopup.IsShow():
			self.__RefreshDonatePopup()

	def __ShowRepTip(self):
		self.__ShowTermTip("rep")

	def __ShowActivityTip(self):
		self.__ShowTermTip("activity")

	def __ShowCoinsTip(self):
		self.__ShowTermTip("coins")

	def __ShowContribTip(self):
		self.__ShowTermTip("contrib")

	def __ShowTermTip(self, term):
		if getattr(self, "infoTermTip", None) is None:
			self.infoTermTip = uitooltip.ToolTip(260)
		tip = self.infoTermTip
		tip.ClearToolTip()
		self.__ClearStockTable()
		tip.toolTipWidth = 260
		if term == "activity":
			title = self.__L("GUILD_OV_ACTIVITY", "Activity")
			icon = ("d:/ymir work/ui/new_guild/info_page/activity_small.png", 14, 20)
			lvl = guild.GetGuildLevel() if hasattr(guild, "GetGuildLevel") else 0
			value = self.__L("GUILD_OV_LEVEL_FMT", "Lv. %d") % lvl
			facts = [
				self.__L("GUILD_OV_ACT_L1", "Guild EXP that fills the level bar."),
				self.__L("GUILD_OV_ACT_L2", "Contracts +25 (+15 per tier). Dungeons +10, max 2/day."),
				self.__L("GUILD_OV_ACT_L3", "Milestone EXP = 15 x Lvl^2. Donations give none."),
			]
		elif term == "coins":
			title = self.__L("GUILD_OV_COINS", "Guild Coins")
			icon = ("d:/ymir work/ui/new_guild/info_page/guild_coin_small.png", 16, 16)
			val = guild.GetMyGuildCoins() if hasattr(guild, "GetMyGuildCoins") else 0
			value = self.__Money(val)
			facts = [
				self.__L("GUILD_OV_COINS_L1", "Your wallet, max 3,000. Spend at the Guild Merchant."),
				self.__L("GUILD_OV_COINS_L2", "Weekly chest: 75 / 150 / 275 by tier."),
				self.__L("GUILD_OV_COINS_L3", "Dungeon +1. Farm 100 loot = 1 coin, max 15/day."),
				self.__L("GUILD_OV_COINS_L4", "First donation of each type daily: +5."),
			]
		elif term == "contrib":
			title = self.__L("GUILD_OV_CONTRIB", "Weekly Contribution")
			icon = ("d:/ymir work/ui/new_guild/info_page/star_full_info.png", 16, 15)
			cval = 0
			if hasattr(guild, "GetContractsMy"):
				my = guild.GetContractsMy()
				if my and my[0]:
					cval = my[1]
			value = self.__Money(cval)
			facts = [
				self.__L("GUILD_OV_CONTRIB_L1", "Your share of the guild's weekly effort."),
				self.__L("GUILD_OV_CONTRIB_L2", "Your share of each contract, scaled by its difficulty."),
				self.__L("GUILD_OV_CONTRIB_L3", "Chest tiers at 1,000 / 2,500 / 4,000. Resets Monday."),
			]
		else:
			title = self.__L("GUILD_OV_REPUTATION", "Reputation")
			icon = ("d:/ymir work/ui/new_guild/info_page/reputation_small.png", 18, 16)
			rep = guild.GetGuildReputation() if hasattr(guild, "GetGuildReputation") else 0
			value = self.__Money(rep)
			facts = [
				self.__L("GUILD_OV_REP_L1", "Shared guild honor, held by the whole guild."),
				self.__L("GUILD_OV_REP_L2", "Earned from contract clears and donations."),
				self.__L("GUILD_OV_REP_L3", "Spent on guild skills, level-ups and rerolls."),
			]
		tip.AppendTextLine(title, 0xffcabdab)
		tip.AppendSpace(5)
		self.__TipHeader(tip, icon[0], icon[1], icon[2], value)
		tip.AppendSpace(9)
		last = len(facts) - 1
		for i, f in enumerate(facts):
			for line in self.__WrapText(tip, f, tip.toolTipWidth - 30):
				tip.AppendTextLine(line, 0xffd8c9a8)
			if i != last:
				tip.AppendSpace(7)
		tip.AppendSpace(5)
		tip.ResizeToolTip()
		tip.SetToolTipPosition(-1, -1)
		tip.ShowToolTip()

	def __Money(self, n):
		fmt = getattr(localeinfo, "NumberToMoneyString", None)
		return fmt(n) if fmt else str(n)

	def __TipHeader(self, tip, iconPath, iconW, iconH, valueText):
		# icon + live value on one centred row (RTL: icon flips to the value's right)
		line = tip.AppendTextLine(valueText, 0xffffd98a)
		vw = line.GetTextWidth()
		cx = tip.toolTipWidth / 2
		gap = 3
		y = line.GetLocalPosition()[1]
		if localeinfo.IsARABIC():
			line.SetPosition(int(cx - (iconW + gap) / 2), y)
			ix = int(cx - (iconW + gap) / 2 + vw / 2 + gap)
		else:
			line.SetPosition(int(cx + (iconW + gap) / 2), y)
			ix = int(cx + (iconW + gap) / 2 - vw / 2 - gap - iconW)
		img = ui.ImageBox()
		img.SetParent(tip)
		img.LoadImage(iconPath)
		img.SetPosition(ix, int(y + (17 - iconH) / 2))
		img.Show()
		tip.childrenList.append(img)


	def __WrapText(self, tip, text, maxPixels):
		m = getattr(self, "infoWrapMeasure", None)
		if m is None:
			m = ui.TextLine()
			m.SetParent(self)
			m.SetFontName(tip.defFontName)
			self.infoWrapMeasure = m
		lines = []
		cur = ""
		for w in text.split(" "):
			trial = w if not cur else (cur + " " + w)
			m.SetText(trial)
			if cur and m.GetTextSize()[0] > maxPixels:
				lines.append(cur)
				cur = w
			else:
				cur = trial
		if cur:
			lines.append(cur)
		return lines

	def __HideTermTip(self):
		if getattr(self, "infoTermTip", None):
			self.infoTermTip.Hide()
		if getattr(self, "stockTip", None):
			self.stockTip.Hide()

	def __ResetLine(self):
		now = int(app.GetGlobalTimeStamp())
		secs = max(0, (now / 86400 + 1) * 86400 - now)
		return self.__L("GUILD_OV_RESET_FMT", "Resets in %sh %sm") % (secs / 3600, (secs % 3600) / 60)

	def __StockTitle(self, index):
		if index == 5:
			return self.__L("GUILD_OV_YANG", "Yang")
		meta = guild.GetResourceMeta(index)
		if meta[0]:
			item.SelectItem(meta[0])
			return item.GetItemName()
		return ""

	def __ResetValue(self):
		now = int(app.GetGlobalTimeStamp())
		secs = max(0, (now / 86400 + 1) * 86400 - now)
		return "%sh %sm" % (secs / 3600, (secs % 3600) / 60)

	def __StockTipRows(self, index):
		REP = "d:/ymir work/ui/new_guild/info_page/reputation_small.png"
		COIN = "d:/ymir work/ui/new_guild/info_page/guild_coin_small.png"
		rows = []
		if index == 5:
			haveCount = player.GetMoney()
		else:
			haveCount = player.GetItemCountByVnum(guild.GetResourceMeta(index)[0])
		rows.append((self.__L("GUILD_OV_T_HAVE", "You have"), self.__CompactCount(haveCount), None))
		if index == 5:
			info = guild.GetDonateInfo()
			per, rep, coins = guild.GetYangDonateMeta()
			dmax = info[3]
			rows.append((self.__L("GUILD_OV_T_LEFT", "Donations left"), self.__CompactCount(self.__YangLeft()) if dmax else "-", None))
			rows.append((self.__L("GUILD_OV_T_TODAY", "Donated today"), "%s / %s" % (self.__CompactCount(info[2]), self.__CompactCount(dmax) if dmax else "-"), None))
			if per > 0:
				rows.append((self.__L("GUILD_OV_REPUTATION", "Reputation"), "+%s / %s" % (rep, self.__CompactCount(per)), REP))
				rows.append((self.__L("GUILD_OV_COINS", "Coins"), self.__L("GUILD_OV_T_FIRST_FMT", "+%s first") % coins, COIN))
		else:
			meta = guild.GetResourceMeta(index)
			dmax = meta[3]
			rows.append((self.__L("GUILD_OV_T_LEFT", "Donations left"), str(self.__ResourceLeft(index)) if dmax else "-", None))
			rows.append((self.__L("GUILD_OV_T_TODAY", "Donated today"), "%s / %s" % (meta[4], dmax if dmax else "-"), None))
			rows.append((self.__L("GUILD_OV_REPUTATION", "Reputation"), "+%s / u" % meta[1], REP))
			rows.append((self.__L("GUILD_OV_COINS", "Coins"), self.__L("GUILD_OV_T_FIRST_FMT", "+%s first") % meta[2], COIN))
			info = guild.GetDonateInfo()
			if info[5] and not (info[1] & (1 << index)):
				rows.append((self.__L("GUILD_OV_T_CONTRIB", "Contribution"), self.__L("GUILD_OV_T_FIRST_FMT", "+%s first") % info[5], None))
		rows.append((self.__L("GUILD_OV_T_RESET", "Resets in"), self.__ResetValue(), None))
		return rows

	def __ClearStockTable(self):
		old = getattr(self, "resTipTable", None)
		if old:
			old.Hide()
			old.Destroy()
			self.resTipTable = None

	def __ShowResTip(self, index):
		if index != 5 and not guild.GetResourceMeta(index)[0]:
			return
		if getattr(self, "stockTip", None) is None:
			self.stockTip = uitooltip.ToolTip(240)
		tip = self.stockTip
		tip.ClearToolTip()
		self.__ClearStockTable()
		rtl = localeinfo.IsARABIC()
		rows = self.__StockTipRows(index)
		LW, VW = 132, 86
		W = LW + VW
		tip.toolTipWidth = W + 16
		tip.AppendTextLine(self.__StockTitle(index), 0xffcabdab)
		tip.AppendSpace(2)
		scheme = [0xff756657, 0xff281f1a, 0xff1a1615, 0xffcabdab, 0xffd1b183]
		w = [LW, VW]
		if rtl:
			w = [VW, LW]
		tbl = ui.Table(W, 1, scheme)
		tbl.SetParent(tip)
		tbl.AddFlag("attach")
		tbl.AddFlag("not_pick")
		tbl.set_columns(["", ""], w)
		for i, r in enumerate(rows):
			bg = 0xff262019 if (i % 2) else 0xff17130f
			if rtl:
				data = [r[1], r[0]]
				colors = [0xffd1b183, 0xffcabdab]
				aligns = ["all:center", "horizontal:right"]
				icons = [None, r[2]]
			else:
				data = [r[0], r[1]]
				colors = [0xffcabdab, 0xffd1b183]
				aligns = ["horizontal:left", "all:center"]
				icons = [r[2], None]
			tbl.add_row(data, 17, colors, aligns, icons, 0, bg)
		tbl.SetPosition(8, tip.toolTipHeight)
		tbl.Show()
		self.resTipTable = tbl
		tip.toolTipHeight += tbl.GetHeight() + 8
		tip.ResizeToolTip()
		tip.SetToolTipPosition()
		tip.Show()

	def __MakeStockWindow(self, page):
		wnd = ui.Window()
		OX, OY = 13, 32
		bw = OX * 2 + 152
		bh = OY + 292 + 13
		wnd.SetSize(bw, bh)
		wnd.AddFlag("float")
		wnd.Hide()
		self.wndStock = wnd
		board = ui.BoardWithTitleBar()
		board.SetParent(wnd)
		board.SetPosition(0, 0)
		board.SetSize(bw, bh)
		board.SetTitleName(self.__L("GUILD_OV_STOCKPILE", "STOCKPILE"))
		board.SetCloseEvent(ui.__mem_func__(self.__HideStockWindow))
		board.Show()
		page.stockBoard = board
		bg = ui.ImageBox()
		bg.SetParent(wnd)
		bg.SetPosition(OX, OY)
		bg.LoadImage("d:/ymir work/ui/new_guild/info_page/bg_donation.png")
		bg.AddFlag("not_pick")
		bg.Show()
		page.stockBg = bg
		page.stockWnd = wnd
		page.stockRows = []
		reset = ui.TextLine()
		reset.SetParent(wnd)
		reset.SetPosition(bw / 2, OY + 13)
		reset.SetHorizontalAlignCenter()
		reset.SetVerticalAlignCenter()
		reset.SetOutline()
		reset.AddFlag("not_pick")
		reset.SetPackedFontColor(0xffcabdab)
		reset.SetText("")
		reset.Show()
		page.stockReset = reset
		bands = ((0, 28), (1, 71), (2, 115), (3, 159), (4, 203), (5, 247))
		for index, rowTop in bands:
			slot = GuildResourceSlot()
			slot.SetParent(wnd)
			slot.SetPosition(OX + 6, OY + rowTop)
			slot.SetSize(132, 35)
			slot.SetSlotEvent(index, ui.__mem_func__(self.__OnStockClick), ui.__mem_func__(self.__OnStockRightClick))
			slot.SetOverInEvent(ui.__mem_func__(self.__ShowResTip), index)
			slot.SetOverOutEvent(ui.__mem_func__(self.__HideTermTip))
			slot.Show()
			btn = GuildDonateButton()
			btn.SetParent(slot)
			btn.SetPosition(6, 6)
			btn.SetSize(83, 23)
			btn.SetUpVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_norm.png")
			btn.SetOverVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_hover.png")
			btn.SetDownVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_select.png")
			btn.SetDisableVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_norm.png")
			btn.SetText("0")
			btn.SetOutline()
			btn.SetTextColor(0xffd1b183)
			btn.SetEvent(ui.__mem_func__(self.__OnStockClick), index)
			btn.SetRightEvent(index, ui.__mem_func__(self.__OnStockRightClick))
			btn.Show()
			icon = ui.ImageBox()
			icon.SetParent(slot)
			icon.SetPosition(100, 1)
			icon.AddFlag("not_pick")
			icon.Hide()
			star = ui.ImageBox()
			star.SetParent(slot)
			star.SetPosition(120, 0)
			star.AddFlag("not_pick")
			star.LoadImage("d:/ymir work/ui/new_guild/info_page/star_full_info.png")
			star.Hide()
			page.stockRows.append({"slot": slot, "btn": btn, "icon": icon, "star": star, "index": index, "vnum": -1})

	def __PositionStockWindow(self):
		wnd = getattr(self, "wndStock", None)
		if not wnd:
			return
		gx, gy = self.GetGlobalPosition()
		if localeinfo.IsARABIC():
			x = gx - wnd.GetWidth() - 2
		else:
			x = gx + self.GetWidth() + 2
		wnd.SetPosition(x, gy)

	def __ShowStockWindow(self):
		wnd = getattr(self, "wndStock", None)
		if not wnd:
			return
		self.__PositionStockWindow()
		wnd.Show()

	def __HideStockWindow(self):
		wnd = getattr(self, "wndStock", None)
		if wnd:
			wnd.Hide()

	def __ToggleStockWindow(self):
		wnd = getattr(self, "wndStock", None)
		if wnd and wnd.IsShow():
			self.__HideStockWindow()
		else:
			self.__ShowStockWindow()

	def __SetStockBtn(self, btn, can):
		if can:
			btn.Enable()
			btn.SetTextColor(0xffd1b183)
		else:
			btn.Disable()
			btn.SetTextColor(0xff70685c)

	def __RefreshStockWindow(self, page):
		rows = getattr(page, "stockRows", None)
		if not rows:
			return
		self.__PositionStockWindow()
		if getattr(page, "stockReset", None):
			page.stockReset.SetText(self.__ResetLine())
		rec = guild.GetDonateInfo()[0]
		for sd in rows:
			index = sd["index"]
			btn = sd["btn"]
			if index == 5:
				if sd["vnum"] != -2:
					sd["vnum"] = -2
					sd["icon"].LoadImage("icon/item/guild_yang.png")
					sd["icon"].Show()
				btn.SetText(self.__CompactCount(guild.GetGuildMoney()))
				sd["star"].Hide()
				can = (self.__YangLeft() > 0 and player.GetMoney() > 0)
				self.__SetStockBtn(btn, can)
				continue
			meta = guild.GetResourceMeta(index)
			if meta[0] != sd["vnum"]:
				sd["vnum"] = meta[0]
				shown = False
				if meta[0]:
					try:
						item.SelectItem(meta[0])
						img = item.GetIconImageFileName()
						if img and img.find("gr2") == -1:
							sd["icon"].LoadImage(img)
							sd["icon"].Show()
							shown = True
					except:
						pass
				if not shown:
					sd["icon"].Hide()
			btn.SetText(self.__CompactCount(guild.GetGuildResource(index)))
			if rec == index:
				sd["star"].Show()
			else:
				sd["star"].Hide()
			can = (meta[0] != 0 and self.__ResourceLeft(index) > 0 and player.GetItemCountByVnum(meta[0]) > 0)
			self.__SetStockBtn(btn, can)

	def __MakeStockpile(self, page):
		page.stockSlots = []
		cells = (
			(0, 6, 158, 82, 42), (1, 89, 158, 85, 42),
			(2, 6, 201, 82, 41), (3, 89, 201, 85, 41),
			(4, 6, 242, 82, 42), (5, 89, 242, 85, 42),
		)
		for index, sx, sy, sw, sh in cells:
			slot = GuildResourceSlot()
			slot.SetParent(page)
			slot.SetPosition(sx, sy)
			slot.SetSize(sw, sh)
			slot.SetSlotEvent(index, ui.__mem_func__(self.__OnStockClick), ui.__mem_func__(self.__OnStockRightClick))
			slot.SetOverInEvent(ui.__mem_func__(self.__ShowResTip), index)
			slot.SetOverOutEvent(ui.__mem_func__(self.__HideTermTip))
			slot.Show()
			iconX = sw - 32
			icon = ui.ImageBox()
			icon.SetParent(slot)
			icon.SetPosition(iconX, 5)
			icon.AddFlag("not_pick")
			icon.Hide()
			count = ui.TextLine()
			count.SetParent(slot)
			count.SetPosition((iconX - 4) / 2, 20)
			count.SetHorizontalAlignCenter()
			count.SetVerticalAlignCenter()
			count.SetOutline()
			count.SetPackedFontColor(0xffd1b183)
			count.SetText("")
			count.Show()
			star = ui.ImageBox()
			star.SetParent(slot)
			star.SetPosition(iconX + 16, 1)
			star.AddFlag("not_pick")
			star.LoadImage("d:/ymir work/ui/new_guild/info_page/star_full_info.png")
			star.Hide()
			page.infoWidgets.append(slot)
			page.stockSlots.append({"slot": slot, "icon": icon, "count": count, "star": star, "index": index, "vnum": -1})

	def __RefreshStockpile(self, page):
		slots = getattr(page, "stockSlots", None)
		if not slots:
			return
		rec = guild.GetDonateInfo()[0]
		for sd in slots:
			index = sd["index"]
			if index == 5:
				if sd["vnum"] != -2:
					sd["vnum"] = -2
					sd["icon"].LoadImage("icon/item/guild_yang.png")
					sd["icon"].Show()
				sd["count"].SetText(self.__CompactCount(guild.GetGuildMoney()))
				sd["star"].Hide()
				continue
			meta = guild.GetResourceMeta(index)
			if meta[0] != sd["vnum"]:
				sd["vnum"] = meta[0]
				shown = False
				if meta[0]:
					try:
						item.SelectItem(meta[0])
						img = item.GetIconImageFileName()
						if img and img.find("gr2") == -1:
							sd["icon"].LoadImage(img)
							sd["icon"].Show()
							shown = True
					except:
						pass
				if not shown:
					sd["icon"].Hide()
			sd["count"].SetText(self.__CompactCount(guild.GetGuildResource(index)))
			if rec == index:
				sd["star"].Show()
			else:
				sd["star"].Hide()

	def __OnStockClick(self, index):
		if not GUILD_DONATION_UI:
			return
		self.__OpenDonatePopup(index)

	def __OnStockDonateAll(self):
		kind = getattr(self, "donatePendingKind", -1)
		amount = getattr(self, "donatePendingAmount", 0)
		self.donatePendingKind = -1
		self.donatePendingAmount = 0
		self.__CloseContractsQuestion()
		if kind >= 0 and amount > 0:
			net.SendGuildDonateResourcePacket(kind, amount)

	def __DonateAmounts(self, index):
		if index == 5:
			info = guild.GetDonateInfo()
			per, rep, coins = guild.GetYangDonateMeta()
			leftCount = self.__YangLeft()
			perMax = info[4] if info[4] > 0 else 999999999
			money = player.GetMoney()
			if leftCount <= 0 or per <= 0 or money < per:
				return (5, 0, 0, rep, coins, per if per > 0 else 1)
			maxA = min(money, perMax)
			if maxA < per:
				maxA = 0
			return (5, per, maxA, rep, coins, per)
		meta = guild.GetResourceMeta(index)
		if not meta[0]:
			return None
		left = self.__ResourceLeft(index)
		have = player.GetItemCountByVnum(meta[0])
		maxA = min(have, left)
		one = 1 if maxA >= 1 else 0
		return (index, one, maxA, meta[1], meta[2], 1)

	def __MakeDonatePopup(self):
		rtl = localeinfo.IsARABIC()
		pop = ui.BoardWithTitleBar()
		pop.SetSize(240, 176)
		pop.AddFlag("float")
		pop.AddFlag("movable")
		pop.SetTitleName(self.__L("GUILD_OV_DONATE", "Donate"))
		pop.SetCloseEvent(ui.__mem_func__(self.__CloseDonatePopup))
		bg = ui.ThinBoard("UI", 2)
		bg.SetParent(pop)
		bg.SetPosition(8, 30)
		bg.SetSize(224, 140)
		bg.AddFlag("not_pick")
		bg.Show()
		self.donatePopupBg = bg
		icon = ui.ImageBox()
		icon.SetParent(pop)
		icon.SetPosition(186 if rtl else 22, 38)
		icon.AddFlag("not_pick")
		icon.Show()
		name = ui.TextLine()
		name.SetParent(pop)
		name.SetPosition(176 if rtl else 64, 40)
		name.SetPackedFontColor(0xffcabdab)
		name.Show()
		have = ui.TextLine()
		have.SetParent(pop)
		have.SetPosition(176 if rtl else 64, 58)
		have.SetPackedFontColor(0xffd1b183)
		have.Show()
		rewardRep = ui.TextLine()
		rewardRep.SetParent(pop)
		rewardRep.SetPosition(218 if rtl else 22, 82)
		rewardRep.SetPackedFontColor(0xffd1b183)
		rewardRep.Show()
		rewardCoin = ui.TextLine()
		rewardCoin.SetParent(pop)
		rewardCoin.SetPosition(218 if rtl else 22, 100)
		rewardCoin.SetPackedFontColor(0xffd1b183)
		rewardCoin.Show()
		daily = ui.TextLine()
		daily.SetParent(pop)
		daily.SetPosition(218 if rtl else 22, 122)
		daily.SetPackedFontColor(0xffd1b183)
		daily.Show()
		btnOne = ui.Button()
		btnOne.SetParent(pop)
		btnOne.SetPosition(18, 146)
		btnOne.SetSize(83, 23)
		btnOne.SetUpVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_norm.png")
		btnOne.SetOverVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_hover.png")
		btnOne.SetDownVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_select.png")
		btnOne.SetDisableVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_norm.png")
		btnOne.SetText(self.__L("GUILD_OV_DONATE_ONE", "Donate"))
		btnOne.SetOutline()
		btnOne.SetTextColor(0xffd1b183)
		btnOne.SetEvent(ui.__mem_func__(self.__OnDonateOne))
		btnOne.Show()
		btnMax = ui.Button()
		btnMax.SetParent(pop)
		btnMax.SetPosition(139, 146)
		btnMax.SetSize(83, 23)
		btnMax.SetUpVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_norm.png")
		btnMax.SetOverVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_hover.png")
		btnMax.SetDownVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_select.png")
		btnMax.SetDisableVisual("d:/ymir work/ui/new_guild/info_page/btn_activ_norm.png")
		btnMax.SetText(self.__L("GUILD_OV_DONATE_MAX", "Donate Max"))
		btnMax.SetOutline()
		btnMax.SetTextColor(0xffd1b183)
		btnMax.SetEvent(ui.__mem_func__(self.__OnDonateMax))
		btnMax.Show()
		self.donatePopup = pop
		self.donatePopupIcon = icon
		self.donatePopupName = name
		self.donatePopupHave = have
		self.donatePopupRewardRep = rewardRep
		self.donatePopupRewardCoin = rewardCoin
		self.donatePopupDaily = daily
		self.donatePopupBtnOne = btnOne
		self.donatePopupBtnMax = btnMax

	def __OpenDonatePopup(self, index):
		if index != 5 and not guild.GetResourceMeta(index)[0]:
			return
		self.donatePopupIndex = index
		if getattr(self, "donatePopup", None) is None:
			self.__MakeDonatePopup()
		self.__RefreshDonatePopup()
		pop = self.donatePopup
		pop.SetPosition((wndMgr.GetScreenWidth() - pop.GetWidth()) / 2, (wndMgr.GetScreenHeight() - pop.GetHeight()) / 2)
		pop.Show()
		pop.SetTop()

	def __RefreshDonatePopup(self):
		index = getattr(self, "donatePopupIndex", -1)
		amt = self.__DonateAmounts(index)
		if not amt:
			return
		kind, one, maxA, rep, coins, per = amt
		if index == 5:
			self.donatePopupIcon.LoadImage("icon/item/guild_yang.png")
			nm = self.__L("GUILD_OV_YANG", "Yang")
			haveCount = player.GetMoney()
			guildStock = guild.GetGuildMoney()
			left = self.__YangLeft()
			dmax = guild.GetDonateInfo()[3]
		else:
			meta = guild.GetResourceMeta(index)
			item.SelectItem(meta[0])
			self.donatePopupIcon.LoadImage(item.GetIconImageFileName())
			nm = item.GetItemName()
			haveCount = player.GetItemCountByVnum(meta[0])
			guildStock = guild.GetGuildResource(index)
			left = self.__ResourceLeft(index)
			dmax = meta[3]
		self.donatePopupName.SetText(nm)
		self.donatePopupHave.SetText(self.__L("GUILD_OV_DP_HAVE", "You have %s   Guild %s") % (self.__CompactCount(haveCount), self.__CompactCount(guildStock)))
		self.donatePopupRewardRep.SetText(self.__L("GUILD_OV_DP_REP", "+%s Reputation / unit") % rep)
		self.donatePopupRewardCoin.SetText(self.__L("GUILD_OV_DP_COIN", "First donation: +%s Coins") % coins)
		self.donatePopupDaily.SetText(self.__L("GUILD_OV_DP_DAILY", "Daily left  %s / %s") % (self.__CompactCount(left) if dmax else "-", self.__CompactCount(dmax) if dmax else "-"))
		self.__SetStockBtn(self.donatePopupBtnOne, one > 0)
		self.__SetStockBtn(self.donatePopupBtnMax, maxA > 0)

	def __OnDonateOne(self):
		amt = self.__DonateAmounts(getattr(self, "donatePopupIndex", -1))
		if not amt:
			return
		kind, one, maxA, rep, coins, per = amt
		if one > 0:
			net.SendGuildDonateResourcePacket(kind, one)

	def __OnDonateMax(self):
		amt = self.__DonateAmounts(getattr(self, "donatePopupIndex", -1))
		if not amt:
			return
		kind, one, maxA, rep, coins, per = amt
		if maxA > 0:
			net.SendGuildDonateResourcePacket(kind, maxA)

	def __CloseDonatePopup(self):
		if getattr(self, "donatePopup", None):
			self.donatePopup.Hide()

	def __OnStockRightClick(self, index):
		if index == 5 or not GUILD_DONATION_UI:
			return
		if player.GetMainCharacterName() != guild.GetGuildMasterName():
			return
		meta = guild.GetResourceMeta(index)
		if not meta[0]:
			return
		if guild.GetDonateInfo()[0] == index:
			self.donateStarPendingIndex = 255
			text = getattr(localeinfo, "GUILD_DONATE_CLEAR_STAR", "Remove the needed-resource mark?")
		else:
			self.donateStarPendingIndex = index
			item.SelectItem(meta[0])
			text = getattr(localeinfo, "GUILD_DONATE_SET_STAR_FMT", "Mark %s as the guild needed resource?") % item.GetItemName()
		self.__OpenContractsQuestion(text, self.__OnDonateStarAccept)

	def __MakeInfoPage(self):
		page = self.pageWindow["GUILD_INFO"]

		try:
			page.nameSlot = page.GetChild("GuildNameValue")
			page.masterNameSlot = page.GetChild("GuildMasterNameValue")
			page.guildLevelSlot = page.GetChild("GuildLevelValue")
			page.curExpSlot = page.GetChild("CurrentExperienceValue")
			page.lastExpSlot = page.GetChild("LastExperienceValue")
			page.memberCountSlot = page.GetChild("GuildMemberCountValue")
			page.levelAverageSlot = page.GetChild("GuildMemberLevelAverageValue")
			page.uploadMarkButton = page.GetChild("UploadGuildMarkButton")
			page.uploadSymbolButton = page.GetChild("UploadGuildSymbolButton")
			page.declareWarButton = page.GetChild("DeclareWarButton")

			# try:
				# page.guildMoneySlot = page.GetChild("GuildMoneyValue")
			# except KeyError:
				# page.guildMoneySlot = None
 
			# try:
				# page.GetChild("DepositButton").SetEvent(ui.__mem_func__(self.__OnClickDepositButton))
				# page.GetChild("WithdrawButton").SetEvent(ui.__mem_func__(self.__OnClickWithdrawButton))
			# except KeyError:
				# pass

			page.uploadMarkButton.SetEvent(ui.__mem_func__(self.__OnClickSelectGuildMarkButton))
			page.uploadSymbolButton.SetEvent(ui.__mem_func__(self.__OnClickSelectGuildSymbolButton))
			page.declareWarButton.SetEvent(ui.__mem_func__(self.__OnClickDeclareWarButton))

			if app.ENABLE_GUILD_RENEWAL:
				page.GetChild("OfferButton").Hide()
				# page.GetChild("OfferButton").SetText("Lv Up")
				page.GetChild("OfferButton").SetEvent(ui.__mem_func__(self.OnLevelUp))

				self.guildMission = ui.MakeButton(page, 15, 264, False, "d:/ymir work/ui/public/", "large_button_01.sub", "large_button_02.sub", "large_button_03.sub")
				self.guildMission.SetText("Guild Mission")
				self.guildMission.SetEvent(ui.__mem_func__(self.ToggleGuildMission))
				self.guildMission.Hide() # TODO: re-enable when guild missions are ready
			else:
				page.GetChild("OfferButton").SetEvent(ui.__mem_func__(self.__OnClickOfferButton))

			# >>> ENEMY GUILD UI BEGIN - removed per user request 2026-07-11 (disabled)
			# (uiscript children commented out too; enemyGuildNameList stays [] so the
			#  OnStartGuildWar/OnEndGuildWar name loops are safe no-ops)
#			page.GetChild("EnemyGuildCancel1").Hide()
#			page.GetChild("EnemyGuildCancel2").Hide()
#			page.GetChild("EnemyGuildCancel3").Hide()
#			page.GetChild("EnemyGuildCancel4").Hide()
#			page.GetChild("EnemyGuildCancel5").Hide()
#			page.GetChild("EnemyGuildCancel6").Hide()
#			self.enemyGuildNameList.append(page.GetChild("EnemyGuildName1"))
#			self.enemyGuildNameList.append(page.GetChild("EnemyGuildName2"))
#			self.enemyGuildNameList.append(page.GetChild("EnemyGuildName3"))
#			self.enemyGuildNameList.append(page.GetChild("EnemyGuildName4"))
#			self.enemyGuildNameList.append(page.GetChild("EnemyGuildName5"))
#			self.enemyGuildNameList.append(page.GetChild("EnemyGuildName6"))
			# <<< ENEMY GUILD UI END

			self.largeMarkBox = page.GetChild("LargeGuildMark")

			if app.ENABLE_GUILD_PASSIVE_SKILLS and not GUILD_SKILLS_UI:
				net.SendGuildPassiveSkillInfoPacket()

			if app.ENABLE_GUILD_DONATE and not GUILD_DONATION_UI:
				self.wndDonate = DonateWindow()
				self.wndDonate.Hide()
				net.SendGuildDonateLoadInfoPacket()

			page.uploadSymbolButton.ShowToolTip = lambda arg = localeinfo.GUILDWINDOW_BUTTON_SYMBOL : self.OverInToolTipButton(arg)
			page.uploadSymbolButton.HideToolTip = lambda : self.OverOutToolTipButton()
			
			
			page.uploadMarkButton.ShowToolTip = lambda arg = localeinfo.GUILDWINDOW_BUTTON_MARK : self.OverInToolTipButton(arg)
			page.uploadMarkButton.HideToolTip = lambda : self.OverOutToolTipButton()

			
			page.declareWarButton.ShowToolTip = lambda arg = localeinfo.GUILDWINDOW_BUTTON_DECLARE : self.OverInToolTipButton(arg)
			page.declareWarButton.HideToolTip = lambda : self.OverOutToolTipButton()
				
			page.GetChild("OfferButton").ShowToolTip = lambda arg = localeinfo.GUILDWINDOW_BUTTON_OFFER : self.OverInToolTipButton(arg)
			page.GetChild("OfferButton").HideToolTip = lambda : self.OverOutToolTipButton()
		except:
			import exception
			exception.Abort("GuildWindow.__MakeInfoPage")

		#self.largeMarkBox.AddFlag("not_pick")

		self.markSelectDialog=uiuploadmark.MarkSelectDialog()
		self.markSelectDialog.SAFE_SetSelectEvent(self.__OnSelectMark)

		self.symbolSelectDialog=uiuploadmark.SymbolSelectDialog()
		self.symbolSelectDialog.SAFE_SetSelectEvent(self.__OnSelectSymbol)

		if app.ENABLE_GUILD_CONTRACTS and hasattr(guild, "GetGuildReputation") and not GUILD_CONTRACTS_UI:
			repLabel = ui.TextLine()
			repLabel.SetParent(page)
			repLabel.SetPosition(3, 223)
			repLabel.SetText(getattr(localeinfo, "GUILD_INFO_REPUTATION", "Reputation"))
			repLabel.Show()
			repValue = ui.TextLine()
			repValue.SetParent(page)
			repValue.SetPosition(73, 223)
			repValue.SetPackedFontColor(0xffffd700)
			repValue.SetText("0")
			repValue.Show()
			page.repLabel = repLabel
			page.repValueSlot = repValue

		if GUILD_DONATION_UI and not GUILD_CONTRACTS_UI:
			self.__MakeDonateRows(page)

		if GUILD_CONTRACTS_UI:
			self.__MakeInfoPageNew(page)


	def __ResourceLeft(self, index):
		meta = guild.GetResourceMeta(index)
		if not meta[3]:
			return 999
		return max(0, meta[3] - meta[4])

	def __YangLeft(self):
		info = guild.GetDonateInfo()
		if not info[3]:
			return 999
		return max(0, info[3] - info[2])

	def __CompactCount(self, value):
		if value >= 1000000:
			return "%.1fM" % (value / 1000000.0)
		if value >= 10000:
			return "%dk" % (value // 1000)
		return str(value)

	def __MakeDonateRows(self, page):
		vaultLabel = ui.TextLine()
		vaultLabel.SetParent(page)
		vaultLabel.SetPosition(3, 239)
		vaultLabel.SetText(getattr(localeinfo, "GUILD_INFO_VAULT", "Vault"))
		vaultLabel.Show()
		vaultValue = ui.TextLine()
		vaultValue.SetParent(page)
		vaultValue.SetPosition(73, 239)
		vaultValue.SetPackedFontColor(0xffffd700)
		vaultValue.SetText("0")
		vaultValue.Show()
		vaultPlus = ui.Button()
		vaultPlus.SetParent(page)
		vaultPlus.SetPosition(152, 238)
		vaultPlus.SetUpVisual("d:/ymir work/ui/game/windows/btn_plus_up.sub")
		vaultPlus.SetOverVisual("d:/ymir work/ui/game/windows/btn_plus_over.sub")
		vaultPlus.SetDownVisual("d:/ymir work/ui/game/windows/btn_plus_down.sub")
		vaultPlus.SetEvent(ui.__mem_func__(self.__OnDonateYangClick))
		vaultPlus.ShowToolTip = lambda f=ui.__mem_func__(self.__ShowDonateToolTip): f(5)
		vaultPlus.HideToolTip = lambda f=ui.__mem_func__(self.OverOutToolTipButton): f()
		vaultPlus.Show()
		page.vaultLabel = vaultLabel
		page.vaultValueSlot = vaultValue
		page.vaultPlusButton = vaultPlus

		slots = []
		for i in xrange(5):
			slot = GuildResourceSlot()
			slot.SetParent(page)
			slot.SetPosition(3 + i * 33, 257)
			slot.SetSize(32, 32)
			slot.SetSlotEvent(i, ui.__mem_func__(self.__OnDonateSlotClick), ui.__mem_func__(self.__OnDonateSlotRightClick))
			slot.Show()
			icon = ui.ImageBox()
			icon.SetParent(slot)
			icon.SetPosition(0, 0)
			icon.AddFlag("not_pick")
			icon.Hide()
			count = ui.TextLine()
			count.SetParent(slot)
			count.SetPosition(2, 19)
			count.SetOutline()
			count.SetText("0")
			count.Show()
			star = ui.Bar()
			star.SetParent(slot)
			star.SetPosition(0, 30)
			star.SetSize(32, 2)
			star.SetColor(0xffffd700)
			star.AddFlag("not_pick")
			star.Hide()
			plus = ui.Button()
			plus.SetParent(slot)
			plus.SetPosition(20, 0)
			plus.SetUpVisual("d:/ymir work/ui/game/windows/btn_plus_up.sub")
			plus.SetOverVisual("d:/ymir work/ui/game/windows/btn_plus_over.sub")
			plus.SetDownVisual("d:/ymir work/ui/game/windows/btn_plus_down.sub")
			plus.SetEvent(ui.__mem_func__(self.__OnDonateSlotClick), i)
			plus.ShowToolTip = lambda arg=i, f=ui.__mem_func__(self.__ShowDonateToolTip): f(arg)
			plus.HideToolTip = lambda f=ui.__mem_func__(self.OverOutToolTipButton): f()
			plus.Show()
			slots.append({"window": slot, "icon": icon, "count": count, "star": star, "plus": plus, "vnum": 0})
		page.donateSlots = slots

	def __RefreshDonateRows(self, page):
		if getattr(page, "vaultValueSlot", None):
			page.vaultValueSlot.SetText(localeinfo.NumberToMoneyString(guild.GetGuildMoney()))
		slots = getattr(page, "donateSlots", None)
		if not slots:
			return
		info = guild.GetDonateInfo()
		for i in xrange(5):
			data = slots[i]
			meta = guild.GetResourceMeta(i)
			if meta[0] != data["vnum"]:
				data["vnum"] = meta[0]
				shown = False
				if meta[0]:
					try:
						item.SelectItem(meta[0])
						imageName = item.GetIconImageFileName()
						if imageName and imageName.find("gr2") == -1:
							data["icon"].LoadImage(imageName)
							data["icon"].Show()
							shown = True
					except:
						pass
				if not shown:
					data["icon"].Hide()
			data["count"].SetText(self.__CompactCount(guild.GetGuildResource(i)))
			if info[0] == i:
				data["star"].Show()
			else:
				data["star"].Hide()
			if meta[0] and (not meta[3] or meta[4] < meta[3]):
				data["plus"].Enable()
			else:
				data["plus"].Disable()
		if getattr(page, "vaultPlusButton", None):
			if self.__YangLeft() > 0:
				page.vaultPlusButton.Enable()
			else:
				page.vaultPlusButton.Disable()

	def __ShowDonateToolTip(self, kind):
		info = guild.GetDonateInfo()
		if kind == 5:
			parts = [getattr(localeinfo, "GUILD_DONATE_YANG_DAILY_FMT", "Yang today: %d/%d") % (info[2], info[3])]
			parts.append(getattr(localeinfo, "GUILD_DONATE_YANG_MAX_FMT", "Max %s per donation") % localeinfo.NumberToMoneyString(info[4]))
		else:
			meta = guild.GetResourceMeta(kind)
			parts = [getattr(localeinfo, "GUILD_DONATE_DAILY_FMT", "Today: %d/%d") % (meta[4], meta[3])]
			parts.append(getattr(localeinfo, "GUILD_DONATE_GRANTS_FMT", "+%d Rep / unit, +%d Coins first") % (meta[1], meta[2]))
		if info[5] and not (info[1] & (1 << kind)):
			parts.append(getattr(localeinfo, "GUILD_DONATE_CONTRIB_TIP", "First of the day: +%d Contribution") % info[5])
		self.OverInToolTipButton(" | ".join(parts))

	def __OnDonateSlotClick(self, index):
		if not GUILD_DONATION_UI:
			return
		meta = guild.GetResourceMeta(index)
		if not meta[0]:
			return
		left = self.__ResourceLeft(index)
		if left <= 0:
			self.__PopupMessage(getattr(localeinfo, "GUILD_DONATE_CAP_REACHED", "Daily donation limit reached."))
			return
		have = player.GetItemCountByVnum(meta[0])
		if have <= 0:
			self.__PopupMessage(getattr(localeinfo, "GUILD_DONATE_NO_ITEMS", "You do not have any of this resource."))
			return
		maxDonate = min(have, left, 200)
		item.SelectItem(meta[0])
		itemName = item.GetItemName()
		self.__CloseDonateDialog()
		dlg = self.__GetDonatePickDialog()
		dlg.SetMax(3)
		dlg.SetTitleName(getattr(localeinfo, "GUILD_DONATE_TITLE_FMT", "Donate %s") % itemName)
		self.donatePendingKind = index
		dlg.Open(maxDonate, maxDonate, itemName, True)

	def __OnDonateAccept(self, count):
		kind = getattr(self, "donatePendingKind", -1)
		self.donatePendingKind = -1
		try:
			count = int(count)
		except:
			count = 0
		if kind < 0 or count <= 0:
			return
		if kind == 5:
			info = guild.GetDonateInfo()
			perMax = info[4] if info[4] > 0 else 999999999
			count = min(count, player.GetMoney(), perMax)
		else:
			meta = guild.GetResourceMeta(kind)
			if not meta[0]:
				return
			count = min(count, player.GetItemCountByVnum(meta[0]), self.__ResourceLeft(kind), 200)
		if count > 0:
			net.SendGuildDonateResourcePacket(kind, count)

	def __OnDonateYangClick(self):
		if not GUILD_DONATION_UI:
			return
		if self.__YangLeft() <= 0:
			self.__PopupMessage(getattr(localeinfo, "GUILD_DONATE_CAP_REACHED", "Daily donation limit reached."))
			return
		money = player.GetMoney()
		if money <= 0:
			return
		info = guild.GetDonateInfo()
		perDonateMax = info[4]
		if perDonateMax <= 0:
			perDonateMax = 999999999
		maxDonate = min(money, perDonateMax)
		self.__CloseDonateDialog()
		dlg = self.__GetDonatePickDialog()
		dlg.SetMax(len(str(perDonateMax)))
		dlg.SetTitleName(getattr(localeinfo, "GUILD_DONATE_YANG_TITLE", "Donate Yang to the Guild Vault"))
		self.donatePendingKind = 5
		dlg.Open(maxDonate, maxDonate, getattr(localeinfo, "MONETARY_UNIT0", "Yang"), True)

	def __OnDonateSlotRightClick(self, index):
		if not GUILD_DONATION_UI:
			return
		if player.GetMainCharacterName() != guild.GetGuildMasterName():
			return
		meta = guild.GetResourceMeta(index)
		if not meta[0]:
			return
		info = guild.GetDonateInfo()
		if info[0] == index:
			self.donateStarPendingIndex = 255
			text = getattr(localeinfo, "GUILD_DONATE_CLEAR_STAR", "Remove the needed-resource mark?")
		else:
			self.donateStarPendingIndex = index
			item.SelectItem(meta[0])
			text = getattr(localeinfo, "GUILD_DONATE_SET_STAR_FMT", "Mark %s as the guild's needed resource?") % item.GetItemName()
		self.__OpenContractsQuestion(text, self.__OnDonateStarAccept)

	def __OnDonateStarAccept(self):
		index = getattr(self, "donateStarPendingIndex", -1)
		if index >= 0:
			net.SendGuildSetRecommendedPacket(index)
		self.donateStarPendingIndex = -1
		self.__CloseContractsQuestion()

	def __GetDonatePickDialog(self):
		if not getattr(self, "donatePickDlg", None):
			dlg = uicommon.PickETCDialog()
			dlg.SetAcceptEvent(ui.__mem_func__(self.__OnDonateAccept))
			self.donatePickDlg = dlg
		return self.donatePickDlg

	def __CloseDonateDialog(self):
		dlg = getattr(self, "donatePickDlg", None)
		if dlg and dlg.IsShow():
			dlg.Close()
		self.donatePendingKind = -1

	def __MakeBoardPage(self):
		i = 0
		lineStep = 20
		page = self.pageWindow["BOARD"]

		page.boardDict = {}

		for i in xrange(12):
			yPos = 25 + i * lineStep

			## NoticeMark
			if localeinfo.IsJAPAN():
				noticeMarkImage = ui.MakeImageBox(page, "d:/ymir work/ui/game/guild/notice_mark.sub", 15, yPos+3)
			else:
				noticeMarkImage = ui.MakeImageBox(page, "d:/ymir work/ui/game/guild/notice_mark.sub", 5, yPos+3)
			noticeMarkImage.Hide()
			page.Children.append(noticeMarkImage)

			## Name
			if localeinfo.IsJAPAN():
				nameSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_100x18.sub", 9, yPos)
			elif localeinfo.IsARABIC():
				nameSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_03.sub", 255, yPos)
			else:
				nameSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_03.sub", 15, yPos)
			nameSlot = ui.MakeTextLine(nameSlotImage)
			page.Children.append(nameSlotImage)
			page.Children.append(nameSlot)

			## Delete Button
			if localeinfo.IsARABIC():
				deleteButton = ui.MakeButton(page, 3, yPos + 3, localeinfo.GUILD_DELETE, "d:/ymir work/ui/public/", "close_button_01.sub", "close_button_02.sub", "close_button_03.sub")
			else:
				deleteButton = ui.MakeButton(page, 340, yPos + 3, localeinfo.GUILD_DELETE, "d:/ymir work/ui/public/", "close_button_01.sub", "close_button_02.sub", "close_button_03.sub")

			deleteButton.SetEvent(ui.__mem_func__(self.OnDeleteComment), i)
			page.Children.append(deleteButton)

			## Comment
			commentSlot = CommentSlot()
			commentSlot.SetParent(page)
			if localeinfo.IsARABIC():
				commentSlot.SetPosition(25, yPos)
			else:
				commentSlot.SetPosition(114, yPos)
			commentSlot.Show()
			page.Children.append(commentSlot)

			boardSlotList = []
			boardSlotList.append(noticeMarkImage)
			boardSlotList.append(nameSlot)
			boardSlotList.append(commentSlot)
			page.boardDict[i] = boardSlotList

		## PostComment - Have to make this here for that fit tooltip's position.
		if localeinfo.IsARABIC():
			postCommentButton = ui.MakeButton(page, 3, 273, localeinfo.GUILD_COMMENT, "d:/ymir work/ui/game/taskbar/", "Send_Chat_Button_01.sub", "Send_Chat_Button_02.sub", "Send_Chat_Button_03.sub")
		else:
			postCommentButton = ui.MakeButton(page, 337, 273, localeinfo.GUILD_COMMENT, "d:/ymir work/ui/game/taskbar/", "Send_Chat_Button_01.sub", "Send_Chat_Button_02.sub", "Send_Chat_Button_03.sub")
		postCommentButton.SetEvent(ui.__mem_func__(self.OnPostComment))
		page.Children.append(postCommentButton)

	def __MakeMemberPage(self):
		page = self.pageWindow["MEMBER"]

		lineStep = 20
		page.memberDict = {}

		page.GetChild("IndexName").OnMouseOverIn = lambda arg = localeinfo.GUILD_MEMBER_NAME : self.OverInToolTipButton(arg)
		page.GetChild("IndexName").OnMouseOverOut = lambda : self.OverOutToolTipButton()

		page.GetChild("IndexGrade").OnMouseOverIn = lambda arg = localeinfo.GUILD_MEMBER_RANK : self.OverInToolTipButton(arg)
		page.GetChild("IndexGrade").OnMouseOverOut = lambda : self.OverOutToolTipButton()

		page.GetChild("IndexJob").OnMouseOverIn = lambda arg = localeinfo.GUILD_MEMBER_JOB : self.OverInToolTipButton(arg)
		page.GetChild("IndexJob").OnMouseOverOut = lambda : self.OverOutToolTipButton()

		page.GetChild("IndexLevel").OnMouseOverIn = lambda arg = localeinfo.GUILD_MEMBER_LEVEL : self.OverInToolTipButton(arg)
		page.GetChild("IndexLevel").OnMouseOverOut = lambda : self.OverOutToolTipButton()

		if app.ENABLE_GUILD_CONTRACTS:
			page.GetChild("IndexOffer").OnMouseOverIn = lambda arg = localeinfo.GUILD_MEMBER_CONTRIBUTION : self.OverInToolTipButton(arg)
		else:
			page.GetChild("IndexOffer").OnMouseOverIn = lambda arg = localeinfo.GUILD_MEMBER_SPECIFIC_GRAVITY : self.OverInToolTipButton(arg)
		page.GetChild("IndexOffer").OnMouseOverOut = lambda : self.OverOutToolTipButton()

		page.GetChild("IndexGeneral").OnMouseOverIn = lambda arg = localeinfo.GUILD_MEMBER_KNIGHT : self.OverInToolTipButton(arg)
		page.GetChild("IndexGeneral").OnMouseOverOut = lambda : self.OverOutToolTipButton()
			
		for i in xrange(self.MEMBER_LINE_COUNT):
			inverseLineIndex = self.MEMBER_LINE_COUNT - i - 1
			yPos = 28 + inverseLineIndex*lineStep

			## Name
			if localeinfo.IsJAPAN():
				nameSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_100x18.sub", 15, yPos)
			elif localeinfo.IsARABIC():
				nameSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_100x18.sub", 255, yPos)
			else:
				nameSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_03.sub", 10, yPos)
			nameSlot = ui.MakeTextLine(nameSlotImage)
			page.Children.append(nameSlotImage)
			page.Children.append(nameSlot)

			## Grade
			gradeSlot = ui.ComboBox()
			gradeSlot.SetParent(page)
			if localeinfo.IsJAPAN():
				gradeSlot.SetPosition(117, yPos-1)
			elif localeinfo.IsARABIC():
				gradeSlot.SetPosition(192, yPos-1)
			else:
				gradeSlot.SetPosition(101, yPos-1)
			gradeSlot.SetSize(61, 18)
			gradeSlot.SetEvent(lambda gradeNumber, lineIndex=inverseLineIndex, argSelf=proxy(self): argSelf.OnChangeMemberGrade(lineIndex, gradeNumber))
			gradeSlot.Show()
			page.Children.append(gradeSlot)

			## Job
			if localeinfo.IsJAPAN():
				jobSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_00.sub", 181, yPos)
			elif localeinfo.IsARABIC():
				jobSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_00.sub", 145, yPos)
			else:
				jobSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_00.sub", 170, yPos)
			jobSlot = ui.MakeTextLine(jobSlotImage)
			page.Children.append(jobSlotImage)
			page.Children.append(jobSlot)

			## Level
			if localeinfo.IsJAPAN():
				levelSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_00.sub", 221, yPos)
			elif localeinfo.IsARABIC():
				levelSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_00.sub", 106, yPos)
			else:
				levelSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_00.sub", 210, yPos)
			levelSlot = ui.MakeTextLine(levelSlotImage)
			page.Children.append(levelSlotImage)
			page.Children.append(levelSlot)

			## Offer
			if localeinfo.IsJAPAN():
				offerSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_00.sub", 261, yPos)
			elif localeinfo.IsARABIC():
				offerSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_00.sub", 66, yPos)
			else:
				offerSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_00.sub", 250, yPos)
			offerSlot = ui.MakeTextLine(offerSlotImage)
			page.Children.append(offerSlotImage)
			page.Children.append(offerSlot) 

			## General Enable
			event = lambda argSelf=proxy(self), argIndex=inverseLineIndex: apply(argSelf.OnEnableGeneral, (argIndex,))
			if localeinfo.IsJAPAN():
				generalEnableCheckBox = CheckBox(page, 307, yPos, event, "d:/ymir work/ui/public/Parameter_Slot_00.sub")
			elif localeinfo.IsARABIC():
				generalEnableCheckBox = CheckBox(page, 22, yPos, event, "d:/ymir work/ui/public/Parameter_Slot_00.sub")
			else:
				generalEnableCheckBox = CheckBox(page, 297, yPos, event, "d:/ymir work/ui/public/Parameter_Slot_00.sub")
			page.Children.append(generalEnableCheckBox)

			memberSlotList = []
			memberSlotList.append(nameSlot)
			memberSlotList.append(gradeSlot)
			memberSlotList.append(jobSlot)
			memberSlotList.append(levelSlot)
			memberSlotList.append(offerSlot)
			memberSlotList.append(generalEnableCheckBox)
			page.memberDict[inverseLineIndex] = memberSlotList

	def __MakeBaseInfoPage(self):
		page = self.pageWindow["BASE_INFO"]

		page.buildingDataDict = {}

		lineStep = 20
		GUILD_BUILDING_MAX_NUM = 7

		yPos = 95 + 35

		for i in xrange(GUILD_BUILDING_MAX_NUM):
			nameSlotImage = ui.MakeSlotBar(page, 15, yPos, 78, 17)
			nameSlot = ui.MakeTextLine(nameSlotImage)
			page.Children.append(nameSlotImage)
			page.Children.append(nameSlot)
			nameSlot.SetText(localeinfo.GUILD_BUILDING_NAME)

			gradeSlotImage = ui.MakeSlotBar(page, 99, yPos, 26, 17)
			gradeSlot = ui.MakeTextLine(gradeSlotImage)
			page.Children.append(gradeSlotImage)
			page.Children.append(gradeSlot)
			gradeSlot.SetText(localeinfo.GUILD_BUILDING_GRADE)

			RESOURCE_MAX_NUM = 6
			for j in xrange(RESOURCE_MAX_NUM):
				resourceSlotImage = ui.MakeSlotBar(page, 131 + 29*j, yPos, 26, 17)
				resourceSlot = ui.MakeTextLine(resourceSlotImage)
				page.Children.append(resourceSlotImage)
				page.Children.append(resourceSlot)
				resourceSlot.SetText(localeinfo.GUILD_GEM)

			event = lambda *arg: None
			powerSlot = CheckBox(page, 308, yPos, event, "d:/ymir work/ui/public/Parameter_Slot_00.sub")
			page.Children.append(powerSlot)

			yPos += lineStep

	def __MakeSkillPage(self):
		if app.ENABLE_GUILD_RENEWAL:
			self.__MakeSkillPageNew()
			return

		page = self.pageWindow["SKILL"]

		page.skillPoint = page.GetChild("Skill_Plus_Value")
		page.passiveSlot = page.GetChild("Passive_Skill_Slot_Table")
		page.activeSlot = page.GetChild("Active_Skill_Slot_Table")
		page.affectSlot = page.GetChild("Affect_Slot_Table")
		page.gpGauge = page.GetChild("Dragon_God_Power_Gauge")
		page.gpValue = page.GetChild("Dragon_God_Power_Value")
		page.btnHealGSP = page.GetChild("Heal_GSP_Button")

		page.activeSlot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
		page.activeSlot.SetOverInItemEvent(lambda slotNumber, type=self.GUILD_SKILL_ACTIVE_SLOT: self.OverInItem(slotNumber, type))
		page.activeSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		page.activeSlot.SetSelectItemSlotEvent(lambda slotNumber, type=self.GUILD_SKILL_ACTIVE_SLOT: self.OnPickUpGuildSkill(slotNumber, type))
		page.activeSlot.SetUnselectItemSlotEvent(lambda slotNumber, type=self.GUILD_SKILL_ACTIVE_SLOT: self.OnUseGuildSkill(slotNumber, type))
		page.activeSlot.SetPressedSlotButtonEvent(lambda slotNumber, type=self.GUILD_SKILL_ACTIVE_SLOT: self.OnUpGuildSkill(slotNumber, type))
		page.activeSlot.AppendSlotButton("d:/ymir work/ui/game/windows/btn_plus_up.sub",\
										"d:/ymir work/ui/game/windows/btn_plus_over.sub",\
										"d:/ymir work/ui/game/windows/btn_plus_down.sub")
		page.passiveSlot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
		page.passiveSlot.SetOverInItemEvent(lambda slotNumber, type=self.GUILD_SKILL_PASSIVE_SLOT: self.OverInItem(slotNumber, type))
		page.passiveSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		page.passiveSlot.SetPressedSlotButtonEvent(lambda slotNumber, type=self.GUILD_SKILL_PASSIVE_SLOT: self.OnUpGuildSkill(slotNumber, type))
		page.passiveSlot.AppendSlotButton("d:/ymir work/ui/game/windows/btn_plus_up.sub",\
										"d:/ymir work/ui/game/windows/btn_plus_over.sub",\
										"d:/ymir work/ui/game/windows/btn_plus_down.sub")
		page.affectSlot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
		page.affectSlot.SetOverInItemEvent(lambda slotNumber, type=self.GUILD_SKILL_AFFECT_SLOT: self.OverInItem(slotNumber, type))
		page.affectSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		page.btnHealGSP.SetEvent(ui.__mem_func__(self.__OnOpenHealGSPBoard))

		page.btnHealGSP.ShowToolTip = lambda arg = localeinfo.GUILDWINDOW_BUTTON_HEALGSP : self.OverInToolTipButton(arg)
		page.btnHealGSP.HideToolTip = lambda : self.OverOutToolTipButton()

		## Passive
		"""
		for i in xrange(len(playersettingmodule.PASSIVE_GUILD_SKILL_INDEX_LIST)):
			slotIndex = page.passiveSlot.GetStartIndex()+i
			skillIndex = playersettingmodule.PASSIVE_GUILD_SKILL_INDEX_LIST[i]

			page.passiveSlot.SetSkillSlot(slotIndex, skillIndex, 0)
			page.passiveSlot.RefreshSlot()
			guild.SetSkillIndex(slotIndex, i)
		"""

		## Active
		for i in xrange(len(playersettingmodule.ACTIVE_GUILD_SKILL_INDEX_LIST)):
			slotIndex = page.activeSlot.GetStartIndex()+i
			skillIndex = playersettingmodule.ACTIVE_GUILD_SKILL_INDEX_LIST[i]

			page.activeSlot.SetSkillSlot(slotIndex, skillIndex, 0)
			page.activeSlot.SetCoverButton(slotIndex)
			page.activeSlot.RefreshSlot()
			guild.SetSkillIndex(slotIndex, len(playersettingmodule.PASSIVE_GUILD_SKILL_INDEX_LIST)+i)

	def UpdatePasiveSkill(self, i, desc, isActive):
		if GUILD_SKILLS_UI:
			return

		if app.ENABLE_GUILD_RENEWAL:
			return

		if app.ENABLE_GUILD_PASSIVE_SKILLS:
		## New Passive
			# for i in xrange(len(playersettingmodule.ACTIVE_GUILD_SKILL_INDEX_LIST)):

			page = self.pageWindow["SKILL"]
			slotIndex = page.passiveSlot.GetStartIndex()+i
			skillIndex = 158+i
			page.passiveSlot.SetSkillSlot(slotIndex, skillIndex, isActive)
			page.passiveSlot.SetCoverButton(slotIndex)
			page.passiveSlot.RefreshSlot()
			guild.SetSkillIndex(slotIndex, i)
			self.passiveSkillDescList.append(desc.title())

	def __MakeGradePage(self):
		lineStep = 18
		page = self.pageWindow["GRADE"]

		page.gradeDict = {}
		
		page.GradeNumber = page.GetChild("GradeNumber")
		page.GradeNumber.OnMouseOverIn = lambda arg = localeinfo.GUILDWINDOW_GRADE_GRADENUMBER : self.OverInToolTipButton(arg)
		page.GradeNumber.OnMouseOverOut = lambda : self.OverOutToolTipButton()

		page.GradeName = page.GetChild("GradeName")
		page.GradeName.OnMouseOverIn = lambda arg = localeinfo.GUILDWINDOW_GRADE_GRADENAME : self.OverInToolTipButton(arg)
		page.GradeName.OnMouseOverOut = lambda : self.OverOutToolTipButton()

		page.InviteAuthority = page.GetChild("InviteAuthority")
		page.InviteAuthority.OnMouseOverIn = lambda arg = localeinfo.GUILDWINDOW_GRADE_INVITEAUTHORITY : self.OverInToolTipButton(arg)
		page.InviteAuthority.OnMouseOverOut = lambda : self.OverOutToolTipButton()

		page.DriveOutAuthority = page.GetChild("DriveOutAuthority")
		page.DriveOutAuthority.OnMouseOverIn = lambda arg = localeinfo.GUILDWINDOW_GRADE_DRIVEOUTAUTHORITY : self.OverInToolTipButton(arg)
		page.DriveOutAuthority.OnMouseOverOut = lambda : self.OverOutToolTipButton()

		page.NoticeAuthority = page.GetChild("NoticeAuthority")
		page.NoticeAuthority.OnMouseOverIn = lambda arg = localeinfo.GUILDWINDOW_GRADE_NOTICEAUTHORITY : self.OverInToolTipButton(arg)
		page.NoticeAuthority.OnMouseOverOut = lambda : self.OverOutToolTipButton()

		page.SkillAuthority = page.GetChild("SkillAuthority")
		page.SkillAuthority.OnMouseOverIn = lambda arg = localeinfo.GUILDWINDOW_GRADE_SKILLAUTHORITY : self.OverInToolTipButton(arg)
		page.SkillAuthority.OnMouseOverOut = lambda : self.OverOutToolTipButton()

		for i in xrange(15):
			yPos = 22 + i * lineStep
			index = i + 1
			## GradeNumber
			if localeinfo.IsARABIC():
				gradeNumberSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_00.sub", 310, yPos)
			else:
				gradeNumberSlotImage = ui.MakeImageBox(page, "d:/ymir work/ui/public/Parameter_Slot_00.sub", 14, yPos)
			gradeNumberSlot = ui.MakeTextLine(gradeNumberSlotImage)
			gradeNumberSlot.SetText(str(i + 1))
			page.Children.append(gradeNumberSlotImage)
			page.Children.append(gradeNumberSlot)

			## GradeName
			if localeinfo.IsARABIC():
				gradeNameSlot = EditableTextSlot(page, 242, yPos)
			else:
				gradeNameSlot = EditableTextSlot(page, 58, yPos)
			gradeNameSlot.SetEvent(ui.__mem_func__(self.OnOpenChangeGradeName), index)
			page.Children.append(gradeNameSlot)

			## Invite Authority
			event = lambda argSelf=proxy(self), argIndex=index, argAuthority=1<<0: apply(argSelf.OnCheckAuthority, (argIndex,argAuthority))
			if localeinfo.IsARABIC():
				inviteAuthorityCheckBox = CheckBox(page, 185, yPos, event)
			else:
				inviteAuthorityCheckBox = CheckBox(page, 124, yPos, event)
			page.Children.append(inviteAuthorityCheckBox)

			## DriveOut Authority
			event = lambda argSelf=proxy(self), argIndex=index, argAuthority=1<<1: apply(argSelf.OnCheckAuthority, (argIndex,argAuthority))
			if localeinfo.IsARABIC():
				driveoutAuthorityCheckBox = CheckBox(page, 128, yPos, event)
			else:
				driveoutAuthorityCheckBox = CheckBox(page, 181, yPos, event)
			page.Children.append(driveoutAuthorityCheckBox)

			## Notice Authority
			event = lambda argSelf=proxy(self), argIndex=index, argAuthority=1<<2: apply(argSelf.OnCheckAuthority, (argIndex,argAuthority))
			if localeinfo.IsARABIC():
				noticeAuthorityCheckBox = CheckBox(page, 71, yPos, event)
			else:
				noticeAuthorityCheckBox = CheckBox(page, 238, yPos, event)
			page.Children.append(noticeAuthorityCheckBox)

			## Skill Authority
			event = lambda argSelf=proxy(self), argIndex=index, argAuthority=1<<3: apply(argSelf.OnCheckAuthority, (argIndex,argAuthority))
			if localeinfo.IsARABIC():
				skillAuthorityCheckBox = CheckBox(page, 14, yPos, event)
			else:
				skillAuthorityCheckBox = CheckBox(page, 295, yPos, event)
			page.Children.append(skillAuthorityCheckBox)

			gradeSlotList = []
			gradeSlotList.append(gradeNameSlot)
			gradeSlotList.append(inviteAuthorityCheckBox)
			gradeSlotList.append(driveoutAuthorityCheckBox)
			gradeSlotList.append(noticeAuthorityCheckBox)
			gradeSlotList.append(skillAuthorityCheckBox)
			page.gradeDict[index] = gradeSlotList

		masterSlotList = page.gradeDict[1]
		for slot in masterSlotList:
			slot.Disable()

	def __MakeRolesPopup(self):
		popup = self.rolesPopup
		popup.rowDict = {}
		popup.headerWidgets = []

		rowAreaWidth = 452
		numX, numW = 12, 24
		nameX, nameW = 44, 90
		checkW = 20
		checkColumns = (
			("INVITE", 150, 1<<0, "GUILD_ROLES_COL_INVITE", "Invite"),
			("KICK", 202, 1<<1, "GUILD_ROLES_COL_KICK", "Kick"),
			("NOTICE", 254, 1<<2, "GUILD_ROLES_COL_NOTICE", "Notice"),
			("SKILL", 306, 1<<3, "GUILD_ROLES_COL_SKILL", "Skill"),
			("CONTRACT", 358, 1<<4, "GUILD_ROLES_COL_CONTRACT", "Contracts"),
			("LEARN", 410, 1<<5, "GUILD_ROLES_COL_LEARN", "Learn"),
		)

		def ColX(enX, w):
			if localeinfo.IsARABIC():
				return rowAreaWidth - enX - w
			return enX

		headerY = 40
		headers = [(ColX(numX, numW), getattr(localeinfo, "GUILDWINDOW_GRADE_GRADENUMBER", "#"))]
		headers.append((ColX(nameX, nameW), getattr(localeinfo, "GUILDWINDOW_GRADE_GRADENAME", "Name")))
		for key, x, bit, localeKey, default in checkColumns:
			headers.append((ColX(x, checkW), getattr(localeinfo, localeKey, default)))

		for x, text in headers:
			headerText = ui.TextLine()
			headerText.SetParent(popup)
			headerText.SetPosition(int(x), headerY)
			headerText.SetVerticalAlignCenter()
			headerText.SetPackedFontColor(0xffcabdab)
			headerText.SetText(text)
			headerText.Show()
			popup.headerWidgets.append(headerText)

		lineStep = 18
		rowStartY = headerY + 24
		for i in xrange(15):
			yPos = rowStartY + i * lineStep
			index = i + 1

			numberImage = ui.MakeImageBox(popup, "d:/ymir work/ui/public/Parameter_Slot_00.sub", int(ColX(numX, numW)), yPos)
			numberText = ui.MakeTextLine(numberImage)
			numberText.SetText(str(index))
			popup.Children.append(numberImage)
			popup.Children.append(numberText)

			nameSlot = EditableTextSlot(popup, int(ColX(nameX, nameW)), yPos)
			nameSlot.SetEvent(ui.__mem_func__(self.OnOpenChangeGradeName), index)
			popup.Children.append(nameSlot)

			rowList = [nameSlot]
			for key, x, bit, localeKey, default in checkColumns:
				event = lambda argSelf=proxy(self), argIndex=index, argAuthority=bit: apply(argSelf.OnCheckAuthority, (argIndex, argAuthority))
				checkBox = CheckBox(popup, int(ColX(x, checkW)), yPos, event)
				popup.Children.append(checkBox)
				rowList.append(checkBox)

			popup.rowDict[index] = rowList

		masterRowList = popup.rowDict[1]
		for slot in masterRowList:
			slot.Disable()

	def RefreshRolesPopup(self):
		if self.isLoaded == 0:
			return
		if not self.rolesPopup:
			return

		popup = self.rolesPopup
		if not getattr(popup, "rowDict", None):
			return

		for key, rowList in popup.rowDict.items():
			name, authority = guild.GetGradeData(int(key))

			if key > 1:
				if name == "...":
					rowList[self.ROLES_SLOT_NAME].SetText(uiscriptlocale.GUILD_BANKINFO_NAME)
				else:
					rowList[self.ROLES_SLOT_NAME].SetText(name)
			else:
				rowList[self.ROLES_SLOT_NAME].SetText(uiscriptlocale.GUILD_INFO_MASTER_VALUE)

			rowList[self.ROLES_SLOT_INVITE].SetCheck(authority & (1<<0))
			rowList[self.ROLES_SLOT_KICK].SetCheck(authority & (1<<1))
			rowList[self.ROLES_SLOT_NOTICE].SetCheck(authority & (1<<2))
			rowList[self.ROLES_SLOT_SKILL].SetCheck(authority & (1<<3))
			rowList[self.ROLES_SLOT_CONTRACT].SetCheck(authority & (1<<4))
			rowList[self.ROLES_SLOT_LEARN].SetCheck(authority & (1<<5))

	def OnOpenRolesPopup(self):
		if not self.rolesPopup:
			return
		self.tabButtonDict["GRADE"].SetUp()
		self.RefreshRolesPopup()
		self.rolesPopup.Open()

	def CanOpen(self):
		return guild.IsGuildEnable()

	def Open(self):
		self.Show()
		self.SetTop()

		guildID = guild.GetGuildID()
		self.largeMarkBox.SetIndex(guildID)
		self.largeMarkBox.SetScale(3)
		if GUILD_CONTRACTS_UI and self.currentPage == "GUILD_INFO":
			self.__ShowStockWindow()
		if localeinfo.IsARABIC() and not GUILD_CONTRACTS_UI:
			self.largeMarkBox.SetPosition(self.largeMarkBox.GetWidth()+32,0)

		if "BOARD" == self.currentPage:
			if self.commentSlot:
				self.commentSlot.SetFocus()
				self.commentSlot.Show()

	def Close(self):
		self.__CloseAllGuildMemberPageGradeComboBox()

		if self.donate_exp_dlg:
			self.donate_exp_dlg.Close()

		if self.donate_sp_dlg:
			self.donate_sp_dlg.Close()

		self.popupDialog.Hide()
		self.changeGradeNameDialog.Hide()
		if self.rolesPopup:
			self.rolesPopup.Hide()
		self.Hide()

		if self.tooltipSkill:
			self.tooltipSkill.Hide()

		self.questionDialog = None
		self.moneyDialog = None

		if GUILD_CONTRACTS_UI:
			self.__CloseContractsQuestion()
		if GUILD_DONATION_UI:
			self.__CloseDonateDialog()

		if self.commentSlot:
			self.commentSlot.KillFocus()
			self.commentSlot.Hide()

	def Destroy(self):
		if GUILD_CONTRACTS_UI:
			self.__CloseContractsQuestion()
		if GUILD_DONATION_UI:
			self.__CloseDonateDialog()
		self.ClearDictionary()
		self.board = None
		self.pageName = None
		self.tabDict = None
		self.tabButtonDict = None
		self.questionDialog = None
		self.markSelectDialog = None
		self.symbolSelectDialog = None

		if self.donate_exp_dlg:
			self.donate_exp_dlg.Destroy()
			del self.donate_exp_dlg
			self.donate_exp_dlg = None

		if self.donate_sp_dlg:
			self.donate_sp_dlg.Destroy()
			del self.donate_sp_dlg
			self.donate_sp_dlg = None

		if self.popupDialog:
			self.popupDialog.ClearDictionary()
			self.popupDialog = None

		if self.changeGradeNameDialog:
			self.changeGradeNameDialog.ClearDictionary()
			self.changeGradeNameDialog = None

		if self.rolesPopup:
			self.rolesPopup.ClearDictionary()
			self.rolesPopup = None

		self.popupMessage = None
		self.commentSlot = None
		self.currentPage = ""

		if self.pageWindow:
			for window in self.pageWindow.values():
				window.ClearDictionary()

		self.pageWindow = None
		self.tooltipSkill = None
		self.moneyDialog = None

		self.enemyGuildNameList = []

		if app.ENABLE_GUILD_PASSIVE_SKILLS:
			self.passiveSkillDescList = []

		if app.ENABLE_GUILD_DONATE and self.wndDonate:
			self.wndDonate.Destroy()
			self.wndDonate = None

	def DeleteGuild(self):
		self.RefreshGuildInfoPage()
		self.RefreshGuildBoardPage()
		self.RefreshGuildMemberPage()
		self.RefreshGuildSkillPage()
		self.RefreshGuildGradePage()
		self.Hide()

	def SetSkillToolTip(self, tooltipSkill):
		self.tooltipSkill = tooltipSkill

	def __ContractArtPath(self, ctype, group):
		g = (group or "").lower()
		if "stone" in g:
			n = "stones"
		elif "monster" in g:
			n = "monsters"
		elif ctype == 1:
			n = "bosses"
		elif ctype == 2:
			n = "dungeon"
		elif ctype == 3:
			n = "fishing"
		elif ctype == 4:
			n = "mining"
		else:
			n = "monsters"
		return CONTRACT_ART + "contracts_missions_" + n + ".png"

	def __MakeContractCard(self, page, slot, x, y):
		rtl = localeinfo.IsARABIC()
		isGrind = (slot == GUILD_CONTRACT_SLOT_GRIND)
		hold = page.contractChildren

		card = ui.Window()
		card.SetParent(page)
		card.SetPosition(x, y)
		card.SetSize(CARD_W, CARD_H)
		card.Show()
		hold.append(card)

		bg = ui.ImageBox()
		bg.SetParent(card)
		bg.LoadImage(CONTRACT_ART + "per_contract_bg.png")
		bg.SetPosition(0, 0)
		bg.Show()
		hold.append(bg)

		titleBar = ui.ImageBox()
		titleBar.SetParent(card)
		titleBar.LoadImage(CONTRACT_ART + "per_contract_title.png")
		titleBar.SetPosition(1, 0)
		titleBar.Show()
		hold.append(titleBar)

		iconW = 21 if isGrind else 16
		icon = ui.ImageBox()
		icon.SetParent(card)
		icon.LoadImage(CONTRACT_ART + ("per_contract_grind_icon.png" if isGrind else "per_contract_rally_icon.png"))
		icon.Show()
		hold.append(icon)

		slotName = ui.TextLine()
		slotName.SetParent(card)
		slotName.SetHorizontalAlignLeft()
		slotName.SetVerticalAlignCenter()
		slotName.SetPackedFontColor(0xffe8d9b5)
		slotName.SetText(self.__L("GUILD_CONTRACT_SLOT_GRIND", "GRIND") if isGrind else self.__L("GUILD_CONTRACT_SLOT_RALLY", "RALLY"))
		slotName.Show()
		hold.append(slotName)

		tierBg = ui.ImageBox()
		tierBg.SetParent(card)
		tierBg.LoadImage(CONTRACT_ART + "per_contract_tier_bg.png")
		tierBg.SetPosition(6 if rtl else 132, 4)
		tierBg.Show()
		hold.append(tierBg)

		tierText = ui.TextLine()
		tierText.SetParent(card)
		tierText.SetPosition(27 if rtl else 153, 11)
		tierText.SetHorizontalAlignCenter()
		tierText.SetVerticalAlignCenter()
		tierText.SetPackedFontColor(0xffffd98a)
		tierText.SetText("")
		tierText.Show()
		hold.append(tierText)

		# icon and label ride together in the 122px the tier box leaves free, so a long
		# Arabic label cannot run under the number
		nameW = slotName.GetTextSize()[0]
		spanL = 52 if rtl else 6
		groupL = spanL + (122 - (nameW + 4 + iconW)) / 2
		if groupL < spanL:
			groupL = spanL
		iconY = 3 if isGrind else 4
		if rtl:
			slotName.SetPosition(int(groupL + nameW), 11)
			icon.SetPosition(int(groupL + nameW + 4), iconY)
		else:
			icon.SetPosition(int(groupL), iconY)
			slotName.SetPosition(int(groupL + iconW + 4), 11)

		art = ui.ImageBox()
		art.SetParent(card)
		art.LoadImage(CONTRACT_ART + "contracts_missions_monsters.png")
		art.SetPosition(2, 25)
		art.Show()
		hold.append(art)

		# clickable overlay on the art (kept above the gauge at y79) -- hover shows the target
		# monster preview / objective, click opens its wiki page
		artHit = ContractArtSlot()
		artHit.SetParent(card)
		artHit.SetPosition(2, 25)
		artHit.SetSize(176, 53)
		artHit.SetEvents(slot, ui.__mem_func__(self.__OnContractArtOverIn), ui.__mem_func__(self.__OnContractArtOverOut), ui.__mem_func__(self.__OnContractArtClick))
		artHit.Show()
		hold.append(artHit)

		# header hover -> explains the GRIND vs RALLY track (kept clear of the tier box)
		headHit = ContractArtSlot()
		headHit.SetParent(card)
		headHit.SetPosition(50 if rtl else 2, 0)
		headHit.SetSize(128, 22)
		headHit.SetEvents(slot, ui.__mem_func__(self.__OnContractHeaderOverIn), ui.__mem_func__(self.__OnContractHeaderOverOut), None)
		headHit.Show()
		hold.append(headHit)

		# the trough rides the art's lower edge -- 178px of card cannot hold six stacked rows
		gaugeBase = ui.ImageBox()
		gaugeBase.SetParent(card)
		gaugeBase.LoadImage(CONTRACT_ART + "per_contract_gauge_empty.png")
		gaugeBase.SetPosition(-1, 79)
		gaugeBase.Show()
		hold.append(gaugeBase)

		gaugeFill = ui.ExpandedImageBox()
		gaugeFill.SetParent(card)
		gaugeFill.LoadImage(CONTRACT_ART + "per_contract_gauge_fill.png")
		gaugeFill.SetPosition(3, 83)
		gaugeFill.SetRenderingRect(0.0, 0.0, -1.0, 0.0)
		gaugeFill.Show()
		hold.append(gaugeFill)

		rewardBg = ui.ImageBox()
		rewardBg.SetParent(card)
		rewardBg.LoadImage(CONTRACT_ART + "per_contract_reward_value.png")
		rewardBg.SetPosition(1, 98)
		rewardBg.Show()
		hold.append(rewardBg)

		rewardTexts = []
		pillIcons = (("guild_reputation_icon.png", 17), ("guild_activity_icon.png", 15), ("contribution_icon.png", 18))
		for p in xrange(3):
			px = 1 + p * 59
			pillArt, pillW = pillIcons[p]
			ic = ui.ImageBox()
			ic.SetParent(card)
			ic.LoadImage(CONTRACT_ART + pillArt)
			ic.SetPosition(px + 53 - pillW if rtl else px + 6, 100)
			ic.Show()
			hold.append(ic)

			val = ui.TextLine()
			val.SetParent(card)
			val.SetPosition(px + 21 if rtl else px + 38, 102)
			val.SetHorizontalAlignCenter()
			val.SetPackedFontColor(0xffe8d9b5)
			val.SetText("-")
			val.Show()
			hold.append(val)
			rewardTexts.append(val)

		textBg = ui.ImageBox()
		textBg.SetParent(card)
		textBg.LoadImage(CONTRACT_ART + "per_contract_text_bg.png")
		textBg.SetPosition(3, 121)
		textBg.Show()
		hold.append(textBg)

		# AlignLeft for both: in this engine it anchors the text's left edge for Latin and
		# its right edge for Arabic, which is exactly the side each script starts from
		objText = ui.TextLine()
		objText.SetParent(card)
		objText.SetHorizontalAlignLeft()
		objText.SetPackedFontColor(0xffe0d2b0)
		objBaseX = CARD_DESC_RX if rtl else CARD_DESC_X
		objText.SetPosition(objBaseX, CARD_DESC_Y)
		objText.SetText("")
		objText.Show()
		hold.append(objText)

		countText = ui.TextLine()
		countText.SetParent(card)
		countText.SetPosition(CARD_COUNT_RX if rtl else CARD_COUNT_X, CARD_DESC_Y)
		countText.SetHorizontalAlignCenter()
		countText.SetPackedFontColor(0xffbfa870)
		countText.SetText("")
		countText.Show()
		hold.append(countText)

		timerIcon = ui.ImageBox()
		timerIcon.SetParent(card)
		timerIcon.LoadImage(CONTRACT_ART + "per_contract_timer_icon.png")
		timerIcon.SetPosition(22, 141)
		timerIcon.Hide()
		hold.append(timerIcon)

		stateLine = ui.TextLine()
		stateLine.SetParent(card)
		stateLine.SetPosition(90, 139)
		stateLine.SetHorizontalAlignCenter()
		stateLine.SetPackedFontColor(0xffcdbb96)
		stateLine.SetText("")
		stateLine.Show()
		hold.append(stateLine)

		# rally frees its button row once started (mission is locked); the player's share fills it
		shareLine = ui.TextLine()
		shareLine.SetParent(card)
		shareLine.SetPosition(90, 159)
		shareLine.SetHorizontalAlignCenter()
		shareLine.SetPackedFontColor(0xffe0d2b0)
		shareLine.SetText("")
		shareLine.Hide()
		hold.append(shareLine)

		def mkBtn(bx, textKey, textDef, handler):
			b = ui.Button()
			b.SetParent(card)
			b.SetUpVisual(CONTRACT_ART + "btn_general_normal.png")
			b.SetOverVisual(CONTRACT_ART + "btn_general_hover.png")
			b.SetDownVisual(CONTRACT_ART + "btn_general_down.png")
			b.SetDisableVisual(CONTRACT_ART + "btn_general_normal.png")
			b.SetPosition(bx, 156)
			b.SetText(self.__L(textKey, textDef))
			b.SetEvent(ui.__mem_func__(handler), slot)
			b.Hide()
			hold.append(b)
			return b

		if isGrind:
			startBtn = None
			rerollBtn = mkBtn(53, "GUILD_CONTRACT_REROLL", "Reroll", self.__OnRerollClick)
		else:
			sx, rx = (95, 10) if rtl else (10, 95)
			startBtn = mkBtn(sx, "GUILD_CONTRACT_START", "Start", self.__OnRallyStartClick)
			rerollBtn = mkBtn(rx, "GUILD_CONTRACT_REROLL", "Reroll", self.__OnRerollClick)

		return {
			"card" : card, "art" : art, "title" : slotName, "tier" : tierText,
			"obj" : objText, "count" : countText, "textBg" : textBg,
			"rewards" : rewardTexts,
			"gaugeBase" : gaugeBase, "gaugeFill" : gaugeFill,
			"timerIcon" : timerIcon, "state" : stateLine,
			"startBtn" : startBtn, "rerollBtn" : rerollBtn,
			"artPath" : "",
			"objFull" : "", "objFullW" : 0, "objH" : 0,
			"objOver" : False, "objBaseX" : objBaseX,
			"secondsLeft" : 0, "rerollCost" : 0, "contractState" : 0, "completed" : 0,
			"myShare" : 0, "tierNum" : 0,
			"progressPair" : (0, 0),
			"rewardBg" : rewardBg, "shareLine" : shareLine,
			"rewardVals" : (0, 0, 0), "rerollCount" : 0, "rerollCap" : 0,
			"targetVnum" : 0, "ctype" : 0, "group" : "", "slot" : slot,
		}

	def __CardObjMeasure(self, card):
		# no character chopping: an ellipsis cut mid-word breaks Arabic glyph joining, so
		# the full string always stands and the clip mask decides what is visible
		t = card["obj"]
		t.SetText(card["objFull"])
		w, h = t.GetTextSize()
		card["objFullW"] = w
		card["objH"] = h
		card["objOver"] = (w > CARD_DESC_W)
		t.SetPosition(card["objBaseX"], CARD_DESC_Y)

	def __CardObjMask(self, card, offset):
		# the label is what moves, so undo the offset to recover the fixed box it stays inside
		h = card["objH"]
		if not h:
			return
		t = card["obj"]
		gx, gy = t.GetGlobalPosition()
		if localeinfo.IsARABIC():
			base = gx - offset
			t.SetClippingMaskRect(int(base - CARD_DESC_W), int(gy), int(base), int(gy + h))
		else:
			base = gx + offset
			t.SetClippingMaskRect(int(base), int(gy), int(base + CARD_DESC_W), int(gy + h))

	def __CardObjRest(self):
		card = self.cardMarqueeHot
		self.cardMarqueeHot = None
		self.cardMarqueeOffset = 0.0
		self.cardMarqueeDone = False
		if card is None:
			return
		card["obj"].SetPosition(card["objBaseX"], CARD_DESC_Y)

	def __ContractHoverClear(self):
		self.__CardObjRest()
		self.cardTipZone = None
		if self.contractTip:
			self.contractTip.Hide()
		self.__HideContractPreview()
		if self.contractArtTip:
			self.contractArtTip.Hide()

	def __ContractHoverTick(self, now):
		dt = now - self.cardMarqueeTime
		self.cardMarqueeTime = now
		if dt <= 0.0 or dt > 0.5:
			dt = 0.0
		mx, my = wndMgr.GetMousePosition()
		hotObj = None
		tipZone = None
		for i, card in enumerate(self.contractCards):
			x, y = card["textBg"].GetGlobalPosition()
			if mx >= x and mx < x + 174 and my >= y and my < y + 17:
				hotObj = card
			if tipZone is not None:
				continue
			rb = card["rerollBtn"]
			if rb.IsShow():
				bx, by = rb.GetGlobalPosition()
				if mx >= bx and mx < bx + rb.GetWidth() and my >= by and my < by + rb.GetHeight():
					tipZone = ("reroll", i)
					continue
			rx, ry = card["rewardBg"].GetGlobalPosition()
			if mx >= rx and mx < rx + 177 and my >= ry and my < ry + 21:
				p = int((mx - rx) / 59)
				if p > 2:
					p = 2
				tipZone = ("pill", i, p)
				continue
			gx, gy = card["gaugeBase"].GetGlobalPosition()
			if mx >= gx and mx < gx + 183 and my >= gy and my < gy + 17:
				tipZone = ("gauge", i)

		if hotObj is not self.cardMarqueeHot:
			self.__CardObjRest()
			if hotObj is not None and hotObj["objOver"]:
				self.cardMarqueeHot = hotObj
				self.cardMarqueeSince = now

		card = self.cardMarqueeHot
		if card is not None and not self.cardMarqueeDone and now - self.cardMarqueeSince >= CARD_MARQUEE_DELAY:
			travel = card["objFullW"] - CARD_DESC_W
			self.cardMarqueeOffset += CARD_MARQUEE_SPEED_PX * dt
			if self.cardMarqueeOffset >= travel:
				self.cardMarqueeOffset = float(travel)
				self.cardMarqueeDone = True
			# Arabic text grows leftward from its anchor, so revealing the hidden head
			# means sliding the anchor the other way
			if localeinfo.IsARABIC():
				card["obj"].SetPosition(int(card["objBaseX"] + self.cardMarqueeOffset), CARD_DESC_Y)
			else:
				card["obj"].SetPosition(int(card["objBaseX"] - self.cardMarqueeOffset), CARD_DESC_Y)

		# the mask is screen-space, so every card re-clips each tick -- the window can be dragged
		for c in self.contractCards:
			self.__CardObjMask(c, self.cardMarqueeOffset if c is self.cardMarqueeHot else 0.0)

		if tipZone != self.cardTipZone:
			self.cardTipZone = tipZone
			self.__ShowCardTip(tipZone)

	def __ShowContractProgressTip(self, card):
		if self.contractTip is None:
			self.contractTip = uitooltip.ToolTip(200)
		tip = self.contractTip
		tip.ClearToolTip()
		tip.toolTipWidth = 200
		progress, target = card["progressPair"]
		tgt = target if target > 0 else 1
		pct = progress * 100 / tgt
		if pct > 100:
			pct = 100
		if card["objFull"]:
			for line in self.__WrapText(tip, card["objFull"], tip.toolTipWidth - 30):
				tip.AppendTextLine(line, 0xffcabdab)
			tip.AppendSpace(6)
		count = self.__L("GUILD_CONTRACT_PROGRESS_TIP", "%s / %s") % (self.__Money(progress), self.__Money(target))
		tip.AppendTextLine("%s  (%d%s)" % (count, pct, "%"), 0xffffd98a)
		tip.AppendSpace(4)
		tip.ResizeToolTip()
		tip.SetToolTipPosition(-1, -1)
		tip.ShowToolTip()

	def __ShowCardTip(self, zone):
		if zone is None:
			if self.contractTip:
				self.contractTip.Hide()
			return
		kind = zone[0]
		card = self.contractCards[zone[1]]
		if kind == "gauge":
			self.__ShowContractProgressTip(card)
		elif kind == "pill":
			self.__ShowContractPillTip(card, zone[2])
		elif kind == "reroll":
			self.__ShowContractRerollTip(card)

	def __ShowContractPillTip(self, card, idx):
		if self.contractTip is None:
			self.contractTip = uitooltip.ToolTip(200)
		tip = self.contractTip
		tip.ClearToolTip()
		tip.toolTipWidth = 200
		titleKey = ("GUILD_CONTRACT_PILL_REP_TITLE", "GUILD_CONTRACT_PILL_ACT_TITLE", "GUILD_CONTRACT_PILL_CONTRIB_TITLE")
		titleDef = ("Guild Reputation", "Guild Activity", "Your Contribution")
		descKey = ("GUILD_CONTRACT_PILL_REP_DESC", "GUILD_CONTRACT_PILL_ACT_DESC", "GUILD_CONTRACT_PILL_CONTRIB_DESC")
		descDef = ("The guild's currency for rerolls and guild skills.",
			"Fills the bar toward your next guild level.",
			"Your personal score for the weekly reward boxes and guild rank.")
		tip.AppendTextLine(self.__L(titleKey[idx], titleDef[idx]), 0xffffd98a)
		for line in self.__WrapText(tip, self.__L(descKey[idx], descDef[idx]), tip.toolTipWidth - 30):
			tip.AppendTextLine(line, 0xffcabdab)
		tip.AppendSpace(4)
		tip.AppendTextLine(self.__L("GUILD_CONTRACT_PILL_PER_CLEAR", "+%s on each clear") % self.__Money(card["rewardVals"][idx]), 0xff8ed18e)
		tip.AppendSpace(4)
		# the rep number only compares across tracks once you know each track's clear rate
		if idx == 0:
			if card.get("slot", 0) == GUILD_CONTRACT_SLOT_GRIND:
				cad = self.__L("GUILD_CONTRACT_PILL_REP_CADENCE_GRIND", "Same reward per clear as a rally - grind just clears a few times a week.")
			else:
				cad = self.__L("GUILD_CONTRACT_PILL_REP_CADENCE_RALLY", "Same reward per clear as grind - rally just clears up to 3 times a day.")
			for line in self.__WrapText(tip, cad, tip.toolTipWidth - 30):
				tip.AppendTextLine(line, 0xffbfa870)
			tip.AppendSpace(4)
		tip.ResizeToolTip()
		tip.SetToolTipPosition(-1, -1)
		tip.ShowToolTip()

	def __ShowContractRerollTip(self, card):
		if self.contractTip is None:
			self.contractTip = uitooltip.ToolTip(200)
		tip = self.contractTip
		tip.ClearToolTip()
		tip.toolTipWidth = 200
		tip.AppendTextLine(self.__L("GUILD_CONTRACT_REROLL_TIP_TITLE", "Reroll Contract"), 0xffffd98a)
		for line in self.__WrapText(tip, self.__L("GUILD_CONTRACT_REROLL_TIP_DESC", "Swap this contract for a random new one at the same tier."), tip.toolTipWidth - 30):
			tip.AppendTextLine(line, 0xffcabdab)
		tip.AppendSpace(4)
		tip.AppendTextLine(self.__L("GUILD_CONTRACT_REROLL_TIP_COST", "Cost: %s Reputation") % self.__Money(card["rerollCost"]), 0xffe0d2b0)
		left = card["rerollCap"] - card["rerollCount"]
		if left < 0:
			left = 0
		if left <= 0:
			tip.AppendTextLine(self.__L("GUILD_CONTRACT_REROLL_TIP_NONE", "No rerolls left this week."), 0xffff6a6a)
		else:
			tip.AppendTextLine(self.__L("GUILD_CONTRACT_REROLL_TIP_LEFT", "Rerolls left this week: %d of %d") % (left, card["rerollCap"]), 0xff8ed18e)
		tip.AppendSpace(4)
		tip.ResizeToolTip()
		tip.SetToolTipPosition(-1, -1)
		tip.ShowToolTip()

	def __EnsureContractPreview(self):
		if self.contractPreviewBoard is not None or not CONTRACT_WIKI:
			return
		# the board overlaps the wide art hover zone, so it must NOT catch the mouse -- a
		# pickable board pops up under the cursor, steals the hover from the art overlay and
		# oscillates OverIn/OverOut (flicker). not_pick lets the cursor fall through to the art.
		board = ui.ThinBoard()
		board.SetSize(180, 240)
		board.AddFlag("float")
		board.AddFlag("not_pick")
		board.Hide()
		self.contractPreviewBoard = board
		rt = ingamewikiui.WikiRenderTarget(160, 180)
		rt.SetParent(board)
		rt.SetPosition(10, 10)
		rt.AddFlag("not_pick")
		rt.Hide()
		self.contractPreviewRT = rt
		name = ui.TextLine()
		name.SetParent(board)
		name.SetPosition(90, 195)
		name.SetHorizontalAlignCenter()
		name.SetOutline()
		name.AddFlag("not_pick")
		name.Hide()
		self.contractPreviewName = name
		hint = ui.TextLine()
		hint.SetParent(board)
		hint.SetPosition(90, 215)
		hint.SetHorizontalAlignCenter()
		hint.SetPackedFontColor(0xffffeaa7)
		hint.SetText(self.__L("MISSIONLIST_CLICK_FOR_WIKI", "Click to view in Wiki"))
		hint.AddFlag("not_pick")
		hint.Hide()
		self.contractPreviewHint = hint

	def __HideContractPreview(self):
		if self.contractPreviewBoard:
			self.contractPreviewBoard.Hide()
		if self.contractPreviewRT:
			self.contractPreviewRT.Hide()
		if self.contractPreviewName:
			self.contractPreviewName.Hide()
		if self.contractPreviewHint:
			self.contractPreviewHint.Hide()

	def __OnContractArtOverIn(self, slot):
		if slot < 0 or slot >= len(self.contractCards):
			return
		card = self.contractCards[slot]
		if not card.get("group"):
			return
		vnum = card.get("targetVnum", 0)
		if CONTRACT_WIKI and vnum > 0 and card.get("ctype", 0) not in (3, 4):
			self.__ShowContractArtPreview(card, vnum)
		else:
			self.__ShowContractArtTip(card)

	def __OnContractArtOverOut(self, slot):
		self.__HideContractPreview()
		if self.contractArtTip:
			self.contractArtTip.Hide()

	def __OnContractArtClick(self, slot):
		if slot < 0 or slot >= len(self.contractCards):
			return
		card = self.contractCards[slot]
		vnum = card.get("targetVnum", 0)
		if not (CONTRACT_WIKI and vnum > 0 and card.get("ctype", 0) not in (3, 4)):
			return
		if self.contractWiki is None:
			return
		if not self.contractWiki.IsShow():
			net.ToggleWikiWindow()
		self.contractWiki.CloseBaseWindows()
		self.contractWiki.OpenSpecialPage(None, vnum, True)

	def __ShowContractArtPreview(self, card, vnum):
		self.__EnsureContractPreview()
		if not self.contractPreviewBoard:
			self.__ShowContractArtTip(card)
			return
		if self.contractArtTip:
			self.contractArtTip.Hide()
		x, y = card["art"].GetGlobalPosition()
		self.contractPreviewBoard.SetPosition(x + 60, y - 40)
		self.contractPreviewRT.SetModel(vnum)
		self.contractPreviewName.SetText(nonplayer.GetMonsterName(vnum))
		self.contractPreviewBoard.Show()
		self.contractPreviewBoard.SetTop()
		self.contractPreviewRT.Show()
		self.contractPreviewName.Show()
		self.contractPreviewHint.Show()

	def __ShowContractArtTip(self, card):
		self.__HideContractPreview()
		if self.contractArtTip is None:
			self.contractArtTip = uitooltip.ToolTip(220)
		tip = self.contractArtTip
		tip.ClearToolTip()
		tip.toolTipWidth = 220
		title = card.get("objFull") or "-"
		tip.AppendTextLine(title, 0xffffd98a)
		key, dflt = self.__ContractObjExplain(card.get("ctype", 0), card.get("group", ""))
		for line in self.__WrapText(tip, self.__L(key, dflt), tip.toolTipWidth - 30):
			tip.AppendTextLine(line, 0xffcabdab)
		tip.AppendSpace(4)
		tip.ResizeToolTip()
		tip.SetToolTipPosition(-1, -1)
		tip.ShowToolTip()

	def __ContractObjExplain(self, ctype, group):
		g = (group or "").lower()
		if g.startswith("stone"):
			return ("GUILD_CONTRACT_OBJ_TIP_STONE", "Break any Metin stone, anywhere in the world.")
		if ctype == 1:
			return ("GUILD_CONTRACT_OBJ_TIP_BOSS", "Defeat any boss monster.")
		if ctype == 2:
			return ("GUILD_CONTRACT_OBJ_TIP_DUNGEON", "Kill boss monsters inside a dungeon.")
		if ctype == 3:
			return ("GUILD_CONTRACT_OBJ_TIP_FISHING", "Catch any fish while fishing.")
		if ctype == 4:
			return ("GUILD_CONTRACT_OBJ_TIP_MINING", "Mine any ore from ore veins.")
		return ("GUILD_CONTRACT_OBJ_TIP_MONSTER", "Hunt any monster, anywhere in the world.")

	def BindWikiInst(self, wikiInst):
		self.contractWiki = wikiInst

	def __OnContractHeaderOverIn(self, slot):
		if slot < 0 or slot >= len(self.contractCards):
			return
		self.__ShowContractTrackTip(slot == GUILD_CONTRACT_SLOT_GRIND)

	def __OnContractHeaderOverOut(self, slot):
		if self.contractArtTip:
			self.contractArtTip.Hide()

	def __ShowContractTrackTip(self, isGrind):
		self.__HideContractPreview()
		if self.contractArtTip is None:
			self.contractArtTip = uitooltip.ToolTip(240)
		tip = self.contractArtTip
		tip.ClearToolTip()
		tip.toolTipWidth = 240
		if isGrind:
			title = self.__L("GUILD_CONTRACT_SLOT_GRIND", "GRIND")
			body = self.__L("GUILD_CONTRACT_TRACK_TIP_GRIND", "Solo track. Always active - no officer, no timer. The target triples each tier and climbs all week, resetting Monday. Farm at your own pace.")
		else:
			title = self.__L("GUILD_CONTRACT_SLOT_RALLY", "RALLY")
			body = self.__L("GUILD_CONTRACT_TRACK_TIP_RALLY", "Team track. An officer starts a 1-hour push. Three tiers a day, each bigger - clear all three and it is done until tomorrow. Unlimited attempts; failing only costs the hour.")
		tip.AppendTextLine(title, 0xffffd98a)
		for line in self.__WrapText(tip, body, tip.toolTipWidth - 30):
			tip.AppendTextLine(line, 0xffcabdab)
		tip.AppendSpace(4)
		tip.ResizeToolTip()
		tip.SetToolTipPosition(-1, -1)
		tip.ShowToolTip()

	def __MakeContractsPage(self):
		page = self.pageWindow["BOARD"]
		# the old cards die with contractChildren, so hover state pointing at them must go too
		self.cardMarqueeHot = None
		self.cardTipZone = None
		self.cardMarqueeOffset = 0.0
		self.cardMarqueeDone = False
		if self.contractTip:
			self.contractTip.Hide()
		self.__HideContractPreview()
		if self.contractArtTip:
			self.contractArtTip.Hide()
		page.contractChildren = []
		self.contractCards = []
		self.tierRows = []
		self.weeklyBoxes = None
		self.contractTypeNames = []
		for key in ("GUILD_CONTRACT_TYPE_HUNT", "GUILD_CONTRACT_TYPE_BOSS", "GUILD_CONTRACT_TYPE_DUNGEON", "GUILD_CONTRACT_TYPE_FISHING", "GUILD_CONTRACT_TYPE_MINING"):
			self.contractTypeNames.append(getattr(localeinfo, key, key))

		rtl = localeinfo.IsARABIC()

		panel = ui.ImageBox()
		panel.SetParent(page)
		panel.LoadImage(CONTRACT_ART + "main_bg.png")
		panel.SetPosition(0, 0)
		panel.Show()
		page.contractChildren.append(panel)

		titleBar = ui.ImageBox()
		titleBar.SetParent(page)
		titleBar.LoadImage(CONTRACT_ART + "contracts_titlebar.png")
		titleBar.SetPosition(128 if rtl else 6, 5)
		titleBar.Show()
		page.contractChildren.append(titleBar)

		titleText = ui.TextLine()
		titleText.SetParent(page)
		titleText.SetPosition((128 if rtl else 6) + 116, 8)
		titleText.SetHorizontalAlignCenter()
		titleText.SetPackedFontColor(0xffe8d9b5)
		titleText.SetText(self.__L("GUILD_CONTRACTS_PAGE_TITLE", "Contracts"))
		titleText.Show()
		page.contractChildren.append(titleText)

		rankBtn = ui.Button()
		rankBtn.SetParent(page)
		rankBtn.SetUpVisual(CONTRACT_ART + "btn_ranking_normal.png")
		rankBtn.SetOverVisual(CONTRACT_ART + "btn_ranking_hover.png")
		rankBtn.SetDownVisual(CONTRACT_ART + "btn_ranking_down.png")
		rankBtn.SetPosition(4 if rtl else 287, 4)
		rankBtn.Show()
		page.contractChildren.append(rankBtn)
		self.contractsRankBtn = rankBtn
		rankBtn.SetEvent(ui.__mem_func__(self.__OnOpenRanking))

		rallyX = CARD_RIGHT_X if rtl else CARD_LEFT_X
		grindX = CARD_LEFT_X if rtl else CARD_RIGHT_X
		cards = {}
		cards[GUILD_CONTRACT_SLOT_RALLY] = self.__MakeContractCard(page, GUILD_CONTRACT_SLOT_RALLY, rallyX, CARD_Y)
		cards[GUILD_CONTRACT_SLOT_GRIND] = self.__MakeContractCard(page, GUILD_CONTRACT_SLOT_GRIND, grindX, CARD_Y)
		self.contractCards = [cards[0], cards[1]]

		self.contractsTopLine = None
		self.contractsFooter = None
		self.__MakeWeeklyBoxes(page, rtl)

	def __OnOpenRanking(self):
		if not self.rankingPopup:
			self.rankingPopup = ContractsRankingPopup()
		self.rankingPopup.OpenCentered()

	def __BoxCenters(self, n):
		if n <= 1:
			return [190]
		if n == 3:
			return [64, 185, 316]
		L, R = 64, 316
		return [int(L + (R - L) * i / float(n - 1)) for i in xrange(n)]

	def __MakeWeeklyBoxes(self, page, rtl):
		BOXART = CONTRACT_ART + "boxes/"
		PAGE_W = 366
		def mx(x, w):
			return (PAGE_W - x - w) if rtl else x
		wb = {"boxes" : []}

		bg = ui.ImageBox()
		bg.SetParent(page)
		bg.LoadImage(BOXART + "bg.png")
		bg.SetPosition(mx(4, 359), 219)
		bg.AddFlag("not_pick")
		bg.Show()
		page.contractChildren.append(bg)

		titleBar = ui.ImageBox()
		titleBar.SetParent(page)
		titleBar.LoadImage(BOXART + "titlebar.png")
		titleBar.SetPosition(mx(6, 352), 200)
		titleBar.AddFlag("not_pick")
		titleBar.Show()
		page.contractChildren.append(titleBar)

		tbX = mx(6, 352)
		timerText = ui.TextLine()
		timerText.SetParent(page)
		timerText.SetPackedFontColor(0xffe8d9b5)
		timerText.SetHorizontalAlignCenter()
		timerText.SetVerticalAlignCenter()
		timerText.SetPosition(tbX + (252 if rtl else 100), 210)
		timerText.AddFlag("not_pick")
		timerText.Show()
		page.contractChildren.append(timerText)
		wb["timer"] = timerText

		pointsText = ui.TextLine()
		pointsText.SetParent(page)
		pointsText.SetPackedFontColor(0xffffd773)
		pointsText.SetHorizontalAlignCenter()
		pointsText.SetVerticalAlignCenter()
		pointsText.SetPosition(tbX + (100 if rtl else 252), 210)
		pointsText.AddFlag("not_pick")
		pointsText.Show()
		page.contractChildren.append(pointsText)
		wb["points"] = pointsText

		trackEmpty = ui.ImageBox()
		trackEmpty.SetParent(page)
		trackEmpty.LoadImage(BOXART + "chest_milestone.png")
		trackEmpty.SetPosition(11, 285)
		trackEmpty.AddFlag("not_pick")
		trackEmpty.Show()
		page.contractChildren.append(trackEmpty)

		trackFill = ui.ExpandedImageBox()
		trackFill.SetParent(page)
		trackFill.LoadImage(BOXART + "chest_milestone_fill.png")
		trackFill.SetPosition(11, 285)
		trackFill.SetRenderingRect(0.0, 0.0, -1.0, 0.0)
		trackFill.AddFlag("not_pick")
		trackFill.Show()
		page.contractChildren.append(trackFill)
		wb["trackFill"] = trackFill

		centers = self.__BoxCenters(3)
		for i in xrange(3):
			cx = (PAGE_W - centers[i]) if rtl else centers[i]
			box = {"cx" : cx, "tier" : 0, "need" : 0, "state" : ""}

			chest = ui.Button()
			chest.SetParent(page)
			chest.SetUpVisual(BOXART + "chest_locked.png")
			chest.SetOverVisual(BOXART + "chest_locked.png")
			chest.SetDownVisual(BOXART + "chest_locked.png")
			chest.SetEvent(ui.__mem_func__(self.__OnClaimBox), i)
			chest.SetPosition(cx - 22, 230)
			chest.Show()
			page.contractChildren.append(chest)
			box["chest"] = chest

			marker = ui.ImageBox()
			marker.SetParent(page)
			marker.LoadImage(BOXART + "chest_milestone_indicator.png")
			marker.SetPosition(cx - 7, 280)
			marker.AddFlag("not_pick")
			marker.Show()
			page.contractChildren.append(marker)
			box["marker"] = marker

			coin = ui.ImageBox()
			coin.SetParent(page)
			coin.LoadImage(BOXART + "coin_ready.png")
			coin.SetPosition(cx + 8, 229)
			coin.AddFlag("not_pick")
			coin.Show()
			page.contractChildren.append(coin)
			box["coin"] = coin

			coinText = ui.TextLine()
			coinText.SetParent(page)
			coinText.SetPackedFontColor(0xffffd773)
			coinText.SetHorizontalAlignCenter()
			coinText.SetVerticalAlignCenter()
			coinText.SetPosition(cx + 30, 235)
			coinText.SetText("")
			coinText.AddFlag("not_pick")
			coinText.Show()
			page.contractChildren.append(coinText)
			box["coinText"] = coinText

			plate = ui.ImageBox()
			plate.SetParent(page)
			plate.LoadImage(BOXART + "label.png")
			plate.SetPosition(cx - 16, 260)
			plate.AddFlag("not_pick")
			plate.Show()
			page.contractChildren.append(plate)
			box["plate"] = plate

			plateText = ui.TextLine()
			plateText.SetParent(page)
			plateText.SetHorizontalAlignCenter()
			plateText.SetVerticalAlignCenter()
			plateText.SetPackedFontColor(0xffe8d9b5)
			plateText.SetPosition(cx, 267)
			plateText.SetText("")
			plateText.AddFlag("not_pick")
			plateText.Show()
			page.contractChildren.append(plateText)
			box["plateText"] = plateText

			wb["boxes"].append(box)

		you = ui.ImageBox()
		you.SetParent(page)
		you.LoadImage(BOXART + "you_indicator.png")
		you.AddFlag("not_pick")
		you.Hide()
		page.contractChildren.append(you)
		wb["you"] = you

		self.weeklyBoxes = wb
		self.boxResetLeft = 0

	def __OnClaimBox(self, i):
		wb = self.weeklyBoxes
		if not wb or i < 0 or i >= len(wb["boxes"]):
			return
		box = wb["boxes"][i]
		if box.get("state") != "ready":
			return
		tier = box.get("tier", 0)
		if tier > 0:
			net.SendGuildTierClaimPacket(tier)
			self.contractsPollTime = 0.0

	def __WeeklyResetText(self, left):
		if left < 0:
			left = 0
		d = left // 86400
		h = (left % 86400) // 3600
		m = (left % 3600) // 60
		if d > 0:
			dur = self.__L("GUILD_WEEKLY_DUR_DH", "%dd %dh") % (d, h)
		elif h > 0:
			dur = self.__L("GUILD_WEEKLY_DUR_HM", "%dh %dm") % (h, m)
		else:
			dur = self.__L("GUILD_WEEKLY_DUR_M", "%dm") % m
		return self.__L("GUILD_WEEKLY_RESET_FMT", "Resets in %s") % dur

	def __UpdateBoxCountdown(self):
		wb = self.weeklyBoxes
		if not wb or not wb.get("timer"):
			return
		left = self.boxResetLeft - int(app.GetTime() - self.contractsRecvTime)
		wb["timer"].SetText(self.__WeeklyResetText(left))

	def __RefreshWeeklyBoxes(self, my):
		wb = self.weeklyBoxes
		if not wb:
			return
		BOXART = CONTRACT_ART + "boxes/"
		rtl = localeinfo.IsARABIC()
		myContrib = my[1]
		claimed = my[2]
		count = guild.GetRewardTierCount()
		boxes = wb["boxes"]
		firstUnreached = -1
		for i in xrange(len(boxes)):
			box = boxes[i]
			if i >= count:
				box["state"] = ""
				box["chest"].Hide()
				box["marker"].Hide()
				box["coin"].Hide()
				box["coinText"].Hide()
				box["plate"].Hide()
				box["plateText"].Hide()
				continue
			tier, need, chestCount = guild.GetRewardTier(i)
			coins = guild.GetRewardTierCoins(i) if hasattr(guild, "GetRewardTierCoins") else 0
			box["tier"] = tier
			box["need"] = need
			if claimed >= tier:
				st = "claimed"
			elif myContrib >= need:
				st = "ready"
			else:
				if firstUnreached < 0:
					firstUnreached = i
				st = "to_reach" if i == firstUnreached else "locked"
			cx = box["cx"]
			if st != box["state"]:
				box["state"] = st
				if st == "ready":
					box["chest"].SetUpVisual(BOXART + "chest_ready_normal.png")
					box["chest"].SetOverVisual(BOXART + "chest_ready_hover.png")
					box["chest"].SetDownVisual(BOXART + "chest_ready_down.png")
					cw = 45
				elif st == "claimed":
					img = BOXART + "chest_claimed.png"
					box["chest"].SetUpVisual(img)
					box["chest"].SetOverVisual(img)
					box["chest"].SetDownVisual(img)
					cw = 43
				elif st == "to_reach":
					img = BOXART + "chest_to_reach.png"
					box["chest"].SetUpVisual(img)
					box["chest"].SetOverVisual(img)
					box["chest"].SetDownVisual(img)
					cw = 44
				else:
					img = BOXART + "chest_locked.png"
					box["chest"].SetUpVisual(img)
					box["chest"].SetOverVisual(img)
					box["chest"].SetDownVisual(img)
					cw = 45
				box["chest"].SetPosition(int(cx - cw // 2), 230)
				if st == "claimed":
					box["marker"].LoadImage(BOXART + "chest_milestone_indicator_claimed.png")
					box["marker"].SetPosition(cx - 9, 277)
					box["coin"].LoadImage(BOXART + "coin_claimed.png")
					box["coinText"].SetPackedFontColor(0xff9a9a9a)
				else:
					box["marker"].LoadImage(BOXART + "chest_milestone_indicator.png")
					box["marker"].SetPosition(cx - 7, 280)
					box["coin"].LoadImage(BOXART + "coin_ready.png")
					box["coinText"].SetPackedFontColor(0xffffd773)
			box["chest"].Show()
			box["marker"].Show()
			box["coin"].Show()
			box["coinText"].Show()
			box["plate"].Show()
			box["plateText"].Show()
			box["coinText"].SetText("+%d" % coins)
			box["plateText"].SetText(str(need))
		originX = 355 if rtl else 11
		pos = float(originX)
		prevX = float(originX)
		prevNeed = 0
		placed = False
		for i in xrange(len(boxes)):
			if i >= count:
				break
			box = boxes[i]
			need = box["need"]
			if myContrib <= need:
				denom = (need - prevNeed) or 1
				frac = float(myContrib - prevNeed) / denom
				if frac < 0.0:
					frac = 0.0
				if frac > 1.0:
					frac = 1.0
				pos = prevX + (box["cx"] - prevX) * frac
				placed = True
				break
			prevX = float(box["cx"])
			prevNeed = need
		if not placed and count > 0:
			pos = float(boxes[min(count, len(boxes)) - 1]["cx"])
		if rtl:
			fillFrac = (originX - pos) / 344.0
		else:
			fillFrac = (pos - originX) / 344.0
		if fillFrac < 0.0:
			fillFrac = 0.0
		if fillFrac > 1.0:
			fillFrac = 1.0
		if rtl:
			wb["trackFill"].SetRenderingRect(-1.0 + fillFrac, 0.0, 0.0, 0.0)
		else:
			wb["trackFill"].SetRenderingRect(0.0, 0.0, -1.0 + fillFrac, 0.0)
		if count > 0:
			wb["you"].SetPosition(int(pos - 5), 283)
			wb["you"].Show()
		else:
			wb["you"].Hide()
		wb["points"].SetText(self.__L("GUILD_WEEKLY_MY_POINTS_FMT", "Points: %s") % str(myContrib))
		self.boxResetLeft = guild.GetContractsResetLeft() if hasattr(guild, "GetContractsResetLeft") else 0
		self.__UpdateBoxCountdown()

	def __MakeGuildSkillsPage(self):
		page = self.pageWindow["SKILL"]
		page.skillChildren = []
		self.skillSlots = []
		self.skillSelected = 0
		self.skillsPollTime = 0.0
		self.skillsTickTime = 0.0
		self.skillsRecvTime = 0.0
		self.pendingSkillIdx = -1
		self.pendingSkillAction = ""

		for i in xrange(8):
			slot = GuildResourceSlot()
			slot.SetParent(page)
			slot.SetPosition(10 + (i % 4) * 86, 6 + (i / 4) * 52)
			slot.SetSize(80, 48)
			slot.SetSlotEvent(i, ui.__mem_func__(self.__OnGuildSkillSlotClick), ui.__mem_func__(self.__OnGuildSkillSlotClick))
			slot.Show()

			board = ui.ThinBoard("UI", 2)
			board.SetParent(slot)
			board.SetPosition(0, 0)
			board.SetSize(80, 48)
			board.AddFlag("not_pick")
			board.Show()

			icon = ui.ImageBox()
			icon.SetParent(slot)
			icon.SetPosition(4, 8)
			icon.AddFlag("not_pick")
			icon.Hide()

			levelText = ui.TextLine()
			levelText.SetParent(slot)
			levelText.SetPosition(44, 6)
			levelText.SetPackedFontColor(0xffffd700)
			levelText.SetOutline()
			levelText.SetText("")
			levelText.Show()

			stateText = ui.TextLine()
			stateText.SetParent(slot)
			stateText.SetPosition(44, 26)
			stateText.SetPackedFontColor(0xffaaaaaa)
			stateText.SetOutline()
			stateText.SetText("")
			stateText.Show()

			self.skillSlots.append({
				"slot" : slot, "board" : board, "icon" : icon, "level" : levelText,
				"state" : stateText, "iconLoaded" : "", "data" : None,
			})
			page.skillChildren.append(slot)

		detail = ui.ThinBoard("UI", 2)
		detail.SetParent(page)
		detail.SetPosition(5, 112)
		detail.SetSize(350, 156)
		detail.Show()
		page.skillChildren.append(detail)
		self.skillDetail = {"board" : detail}

		yPos = 8
		for key in ("name", "effect", "levelline", "timers", "castcost", "upcost"):
			line = ui.TextLine()
			line.SetParent(detail)
			if localeinfo.IsARABIC():
				line.SetPosition(340, yPos)
				line.SetHorizontalAlignLeft()
			else:
				line.SetPosition(10, yPos)
			line.SetPackedFontColor(0xffffffff)
			line.SetText("")
			line.Show()
			self.skillDetail[key] = line
			yPos += 17

		btnY = 126
		activateBtn = ui.Button()
		activateBtn.SetParent(detail)
		activateBtn.SetPosition(14, btnY)
		activateBtn.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		activateBtn.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		activateBtn.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		activateBtn.SetText(getattr(localeinfo, "GUILD_SKILL_ACTIVATE", "Activate"))
		activateBtn.SetEvent(ui.__mem_func__(self.__OnGuildSkillActivateClick))
		activateBtn.Show()
		self.skillDetail["activateBtn"] = activateBtn

		levelUpBtn = ui.Button()
		levelUpBtn.SetParent(detail)
		levelUpBtn.SetPosition(130, btnY)
		levelUpBtn.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		levelUpBtn.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		levelUpBtn.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		levelUpBtn.SetText(getattr(localeinfo, "GUILD_SKILL_LEVELUP", "Level Up"))
		levelUpBtn.SetEvent(ui.__mem_func__(self.__OnGuildSkillLevelUpClick))
		levelUpBtn.Show()
		self.skillDetail["levelUpBtn"] = levelUpBtn

		teleportBtn = ui.Button()
		teleportBtn.SetParent(detail)
		teleportBtn.SetPosition(246, btnY)
		teleportBtn.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		teleportBtn.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		teleportBtn.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		teleportBtn.SetText(getattr(localeinfo, "GUILD_SKILL_TELEPORT", "Teleport"))
		teleportBtn.SetEvent(ui.__mem_func__(self.__OnGuildSummonTeleportClick))
		teleportBtn.Hide()
		self.skillDetail["teleportBtn"] = teleportBtn

	def __GuildSkillEffectText(self, idx, value):
		fmt = getattr(localeinfo, "GUILD_SKILL_EFFECT_%d" % idx, "+%d%%")
		try:
			return fmt % value
		except TypeError:
			return fmt

	def __GuildSkillSecondsText(self, seconds):
		seconds = int(seconds)
		if seconds >= 3600:
			return "%d:%02d:%02d" % (seconds / 3600, (seconds % 3600) / 60, seconds % 60)
		return "%d:%02d" % (seconds / 60, seconds % 60)

	def RefreshGuildSkillsPage(self):
		if not GUILD_SKILLS_UI or not self.isLoaded:
			return
		self.skillsRecvTime = app.GetTime()
		meta = guild.GetGuildSkillsMeta()
		for i in xrange(8):
			data = guild.GetGuildSkillInfo(i)
			cell = self.skillSlots[i]
			if data[2] < 0 or not data[0]:
				cell["data"] = None
				cell["slot"].Hide()
				continue
			cell["data"] = data
			cell["slot"].Show()
			cell["level"].SetText(getattr(localeinfo, "GUILD_SKILL_LEVEL_FMT", "Lv %d / %d") % (data[3], data[4]))
			icon = cell["icon"]
			iconPath = "d:/ymir work/ui/new_guild/skills/%s.png" % data[1]
			if cell["iconLoaded"] != iconPath:
				try:
					icon.LoadImage(iconPath)
					icon.Show()
					cell["iconLoaded"] = iconPath
				except:
					icon.Hide()
					cell["iconLoaded"] = ""
		self.__RefreshGuildSkillTimers()
		self.__RefreshGuildSkillDetail()

	def __RefreshGuildSkillTimers(self):
		if not GUILD_SKILLS_UI or not getattr(self, "skillSlots", None):
			return
		elapsed = int(app.GetTime() - getattr(self, "skillsRecvTime", 0.0))
		for i in xrange(8):
			cell = self.skillSlots[i]
			data = cell["data"]
			if not data:
				continue
			activeLeft = max(0, data[11] - elapsed)
			cooldownLeft = max(0, data[12] - elapsed)
			if data[3] == 0:
				cell["state"].SetPackedFontColor(0xff888888)
				cell["state"].SetText(getattr(localeinfo, "GUILD_SKILL_NOT_LEARNED", "Not learned"))
			elif activeLeft > 0 and data[2] != 2:
				cell["state"].SetPackedFontColor(0xff77ff77)
				cell["state"].SetText(self.__GuildSkillSecondsText(activeLeft))
			elif cooldownLeft > 0:
				cell["state"].SetPackedFontColor(0xffff7777)
				cell["state"].SetText(self.__GuildSkillSecondsText(cooldownLeft))
			else:
				cell["state"].SetPackedFontColor(0xffaaaaaa)
				cell["state"].SetText(getattr(localeinfo, "GUILD_SKILL_READY", "Ready"))

	def __RefreshGuildSkillDetail(self):
		if not GUILD_SKILLS_UI or not getattr(self, "skillDetail", None):
			return
		idx = self.skillSelected
		data = self.skillSlots[idx]["data"] if idx < len(self.skillSlots) else None
		meta = guild.GetGuildSkillsMeta()
		detail = self.skillDetail
		if not data or not meta[0]:
			for key in ("name", "effect", "levelline", "timers", "castcost", "upcost"):
				detail[key].SetText("")
			detail["activateBtn"].Hide()
			detail["levelUpBtn"].Hide()
			detail["teleportBtn"].Hide()
			return
		elapsed = int(app.GetTime() - getattr(self, "skillsRecvTime", 0.0))
		name = getattr(localeinfo, data[0], data[0])
		detail["name"].SetPackedFontColor(0xffffd700)
		detail["name"].SetText(name)
		detail["effect"].SetText(self.__GuildSkillEffectText(idx, data[7]))
		if data[3] == 0:
			detail["levelline"].SetText("%s - %s" % (
				getattr(localeinfo, "GUILD_SKILL_NOT_LEARNED", "Not learned"),
				getattr(localeinfo, "GUILD_SKILL_LOCKED_FMT", "Guild level %d required") % data[5]))
		else:
			detail["levelline"].SetText(getattr(localeinfo, "GUILD_SKILL_LEVEL_FMT", "Lv %d / %d") % (data[3], data[4]))
		durTxt = getattr(localeinfo, "GUILD_SKILL_DURATION_FMT", "Duration: %s") % self.__GuildSkillSecondsText(data[9])
		cdTxt = getattr(localeinfo, "GUILD_SKILL_COOLDOWN_FMT", "Cooldown: %s") % self.__GuildSkillSecondsText(data[10])
		detail["timers"].SetText("%s | %s" % (durTxt, cdTxt))
		cast = guild.GetGuildSkillCast(idx)
		castParts = []
		if cast[0]:
			castParts.append(getattr(localeinfo, "GUILD_SKILL_COST_REP_FMT", "%d Reputation") % cast[0])
		if cast[1]:
			castParts.append(getattr(localeinfo, "GUILD_SKILL_COST_YANG_FMT", "%s Yang") % localeinfo.NumberToMoneyString(cast[1]))
		for r in xrange(5):
			if cast[2 + r]:
				castParts.append("%dx R%d" % (cast[2 + r], r + 1))
		castAfford = (meta[2] >= cast[0] and meta[8] >= cast[1])
		for r in xrange(5):
			if meta[3 + r] < cast[2 + r]:
				castAfford = False
		detail["castcost"].SetPackedFontColor(castAfford and 0xffffffff or 0xffff5555)
		detail["castcost"].SetText("%s %s" % (getattr(localeinfo, "GUILD_SKILL_CAST_COST", "Activation cost:"), " + ".join(castParts)))
		up = guild.GetGuildSkillUp(idx)
		upParts = []
		if up[0]:
			upParts.append(getattr(localeinfo, "GUILD_SKILL_COST_REP_FMT", "%d Reputation") % up[0])
		if up[1]:
			upParts.append(getattr(localeinfo, "GUILD_SKILL_COST_YANG_FMT", "%s Yang") % localeinfo.NumberToMoneyString(up[1]))
		for r in xrange(5):
			if up[2 + r]:
				upParts.append("%dx R%d" % (up[2 + r], r + 1))
		if up[7] and up[8]:
			upParts.append(getattr(localeinfo, "GUILD_SKILL_COST_TOME_FMT", "%d x Tome %s") % (up[8], up[7]))
		if data[3] >= data[4]:
			detail["upcost"].SetText("")
		else:
			upAfford = (meta[2] >= up[0] and meta[8] >= up[1])
			for r in xrange(5):
				if meta[3 + r] < up[2 + r]:
					upAfford = False
			detail["upcost"].SetPackedFontColor(upAfford and 0xffffffff or 0xffff5555)
			detail["upcost"].SetText("%s %s" % (getattr(localeinfo, "GUILD_SKILL_UP_COST", "Next level cost:"), " + ".join(upParts)))
		isOfficer = meta[1]
		activeLeft = max(0, data[11] - elapsed)
		cooldownLeft = max(0, data[12] - elapsed)
		if isOfficer and data[3] > 0 and cooldownLeft <= 0:
			detail["activateBtn"].Show()
		else:
			detail["activateBtn"].Hide()
		if isOfficer and data[3] < data[4]:
			if data[3] == 0:
				detail["levelUpBtn"].SetText(getattr(localeinfo, "GUILD_SKILL_LEARN", "Learn"))
			else:
				detail["levelUpBtn"].SetText(getattr(localeinfo, "GUILD_SKILL_LEVELUP", "Level Up"))
			detail["levelUpBtn"].Show()
		else:
			detail["levelUpBtn"].Hide()
		gateLeft = max(0, meta[10] - elapsed)
		if meta[9] and gateLeft > 0:
			detail["teleportBtn"].Show()
		else:
			detail["teleportBtn"].Hide()

	def __OnGuildSkillSlotClick(self, index):
		if index < 0 or index >= 8:
			return
		self.skillSelected = index
		self.__RefreshGuildSkillDetail()

	def __OnGuildSkillActivateClick(self):
		idx = self.skillSelected
		data = self.skillSlots[idx]["data"] if idx < len(self.skillSlots) else None
		if not data:
			return
		name = getattr(localeinfo, data[0], data[0])
		self.pendingSkillIdx = idx
		self.pendingSkillAction = "activate"
		self.__OpenContractsQuestion(getattr(localeinfo, "GUILD_SKILL_ACTIVATE_CONFIRM", "Activate %s?") % name,
			self.__OnGuildSkillConfirmAccept)

	def __OnGuildSkillLevelUpClick(self):
		idx = self.skillSelected
		data = self.skillSlots[idx]["data"] if idx < len(self.skillSlots) else None
		if not data:
			return
		name = getattr(localeinfo, data[0], data[0])
		self.pendingSkillIdx = idx
		self.pendingSkillAction = "levelup"
		self.__OpenContractsQuestion(getattr(localeinfo, "GUILD_SKILL_LEVELUP_CONFIRM", "Level up %s?") % name,
			self.__OnGuildSkillConfirmAccept)

	def __OnGuildSkillConfirmAccept(self):
		idx = getattr(self, "pendingSkillIdx", -1)
		action = getattr(self, "pendingSkillAction", "")
		self.pendingSkillIdx = -1
		self.pendingSkillAction = ""
		self.__CloseContractsQuestion()
		if idx < 0:
			return
		if action == "activate":
			net.SendGuildSkillActivatePacket(idx)
		elif action == "levelup":
			net.SendGuildSkillLevelUpPacket(idx)
		self.skillsPollTime = 0.0

	def __OnGuildSummonTeleportClick(self):
		net.SendGuildSummonAcceptPacket()

	def __MakeProgressionPage(self):
		page = self.pageWindow["BASE_INFO"]
		page.progChildren = []
		w = {}
		for key, y, color in (("level", 20, 0xffffd700), ("activity", 50, 0xffffffff), ("vault", 100, 0xffffffff), ("cost", 118, 0xffffffff), ("reason", 205, 0xff9a9a9a)):
			line = ui.TextLine()
			line.SetParent(page)
			line.SetWindowHorizontalAlignCenter()
			line.SetHorizontalAlignCenter()
			line.SetPosition(0, y)
			line.SetPackedFontColor(color)
			line.SetText("")
			line.Show()
			w[key] = line
			page.progChildren.append(line)

		activityGauge = ui.Gauge()
		activityGauge.SetParent(page)
		activityGauge.MakeGauge(310, "blue")
		activityGauge.SetPosition(20, 68)
		activityGauge.Show()
		w["activityGauge"] = activityGauge
		page.progChildren.append(activityGauge)

		vaultGauge = ui.Gauge()
		vaultGauge.SetParent(page)
		vaultGauge.MakeGauge(310, "yellow")
		vaultGauge.SetPosition(20, 136)
		vaultGauge.Show()
		w["vaultGauge"] = vaultGauge
		page.progChildren.append(vaultGauge)

		levelUpBtn = ui.Button()
		levelUpBtn.SetParent(page)
		levelUpBtn.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		levelUpBtn.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		levelUpBtn.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		levelUpBtn.SetText(getattr(localeinfo, "GUILD_PROGRESSION_LEVELUP", "Level Up"))
		levelUpBtn.SetPosition(136, 170)
		levelUpBtn.SetEvent(ui.__mem_func__(self.__OnLevelUpClick))
		levelUpBtn.Disable()
		levelUpBtn.Show()
		w["levelUpBtn"] = levelUpBtn
		page.progChildren.append(levelUpBtn)

		self.progressionWidgets = w

	def __GdX(self, x, w):
		if localeinfo.IsARABIC():
			return GD_PAGE_W - x - w
		return x

	def __GdAx(self, x):
		if localeinfo.IsARABIC():
			return GD_PAGE_W - x
		return x

	def __GdPlate(self, page, name, x, y, w):
		img = ui.ImageBox()
		img.SetParent(page)
		img.LoadImage(GD_ART + name)
		img.SetPosition(self.__GdX(x, w), y)
		img.Show()
		self.gdChildren.append(img)
		return img

	def __GdLine(self, page, x, y, color, centered = True, mirror = True):
		line = ui.TextLine()
		line.SetParent(page)
		if centered:
			line.SetHorizontalAlignCenter()
		line.SetPosition(self.__GdAx(x) if mirror else x, y)
		line.SetVerticalAlignCenter()
		line.SetPackedFontColor(color)
		line.SetText("")
		line.Show()
		self.gdChildren.append(line)
		return line

	def __GdMakeSlot(self, page, x, y, index):
		bg = self.__GdPlate(page, "dungeon_item_bg.png", x, y, 44)
		icon = ui.ImageBox()
		icon.SetParent(page)
		icon.SetPosition(self.__GdX(x + 6, 32), y + 6)
		icon.Hide()
		self.gdChildren.append(icon)
		count = self.__GdLine(page, x + 22, y + 35, GD_COL_CREAM)
		hot = ContractArtSlot()
		hot.SetParent(page)
		hot.SetPosition(self.__GdX(x, 44), y)
		hot.SetSize(44, 44)
		hot.SetEvents(index, self.__OnGdSlotOverIn, self.__OnGdSlotOverOut, None)
		hot.Show()
		self.gdChildren.append(hot)
		slot = {"bg" : bg, "icon" : icon, "count" : count, "hot" : hot, "vnum" : -1, "path" : "", "name" : "", "qty" : "", "hasIcon" : False}
		bg.Hide()
		count.Hide()
		hot.Hide()
		return slot

	def __MakeDungeonPage(self):
		page = self.pageWindow["BASE_INFO"]
		self.gdW = {}
		self.gdChildren = []
		self.gdRankRows = []
		self.gdCostSlots = []
		self.gdChestSlot = None
		self.gdBannerTier = 0
		w = self.gdW

		self.__GdPlate(page, "dungeon_bg.png", 0, 0, 366)
		self.__GdPlate(page, "title_dungeon_bg.png", 2, 0, 362)
		w["daily"] = self.__GdLine(page, 76, 17, GD_COL_CREAM)
		w["cdIcon"] = self.__GdPlate(page, "dungeon_cooldown.png", 152, 11, 12)
		w["cooldown"] = self.__GdLine(page, 202, 17, GD_COL_GOLD)
		w["weekly"] = self.__GdLine(page, 292, 17, GD_COL_CREAM)

		banner = ui.ImageBox()
		banner.SetParent(page)
		banner.LoadImage(GD_ART + GD_BANNERS[0])
		banner.SetPosition(self.__GdX(5, 356), 34)
		banner.Show()
		self.gdChildren.append(banner)
		w["banner"] = banner
		self.gdBannerTier = 1

		leftDelta = 1 if localeinfo.IsARABIC() else -1
		for key, art, bx, delta in (("leftBtn", "left_arrow", 5, leftDelta), ("rightBtn", "right_arrow", 292, -leftDelta)):
			btn = ui.Button()
			btn.SetParent(page)
			btn.SetUpVisual(GD_ART + art + "_norm.png")
			btn.SetOverVisual(GD_ART + art + "_hover.png")
			btn.SetDownVisual(GD_ART + art + "_down.png")
			btn.SetPosition(bx, 50)
			btn.SetEvent(ui.__mem_func__(self.__OnGdArrow), delta)
			btn.Show()
			self.gdChildren.append(btn)
			w[key] = btn

		for key, y, color in (("tierName", 64, GD_COL_GOLD), ("bossLine", 81, GD_COL_MUTED)):
			bar = ui.Bar()
			bar.SetParent(page)
			bar.SetColor(GD_PLATE_COLOR)
			bar.SetSize(12, 14)
			bar.SetPosition(self.__GdX(11, 12), y)
			bar.Hide()
			self.gdChildren.append(bar)
			w[key + "Bar"] = bar
			w[key] = self.__GdLine(page, 17, y + 7, color, False)
		w["pageInd"] = self.__GdLine(page, 336, 43, GD_COL_MUTED)

		self.__GdPlate(page, "requirements_chest_bg.png", 4, 101, 358)
		for i in xrange(GD_COST_SLOTS):
			self.gdCostSlots.append(self.__GdMakeSlot(page, 10 + i * 46, 107, i))
		w["sep"] = self.__GdPlate(page, "dungeon_item_seperate.png", 246, 109, 1)
		self.gdChestSlot = self.__GdMakeSlot(page, 254, 107, GD_CHEST_SLOT_ID)
		w["chestName"] = self.__GdLine(page, 304, 118, GD_COL_CREAM, False)
		self.gdChestBaseX = self.__GdAx(304)
		w["chestExp"] = self.__GdLine(page, 304, 136, GD_COL_GOLD, False)

		self.__GdPlate(page, "dungeon_start_bg.png", 4, 157, 358)
		chip = ui.ImageBox()
		chip.SetParent(page)
		chip.LoadImage(GD_ART + "dungeon_available.png")
		chip.SetPosition(self.__GdX(12, 63), 163)
		chip.Show()
		self.gdChildren.append(chip)
		w["chip"] = chip
		w["chipArt"] = ""
		w["chipText"] = self.__GdLine(page, 43, 172, GD_COL_CREAM)
		w["detail"] = self.__GdLine(page, 183, 172, GD_COL_MUTED)

		actBtn = ui.Button()
		actBtn.SetParent(page)
		actBtn.SetUpVisual(GD_ART + "btn_general_normal.png")
		actBtn.SetOverVisual(GD_ART + "btn_general_hover.png")
		actBtn.SetDownVisual(GD_ART + "btn_general_down.png")
		actBtn.SetText("")
		actBtn.SetPosition(self.__GdX(280, 74), 162)
		actBtn.SetEvent(ui.__mem_func__(self.__OnGdActionClick))
		actBtn.Hide()
		self.gdChildren.append(actBtn)
		w["actBtn"] = actBtn

		self.__GdPlate(page, "dungeon_ranking_bg.png", 4, 187, 358)
		for i in xrange(5):
			ry = 195 + i * 20
			row = {}
			row["img"] = self.__GdPlate(page, GD_RANK_ROWS[i if i < 3 else 3], 7, ry, 352)
			row["rank"] = self.__GdLine(page, 25, ry + 10, GD_COL_MUTED, True, False)
			row["name"] = self.__GdLine(page, 177 if localeinfo.IsARABIC() else 51, ry + 10, GD_COL_CREAM, False, False)
			row["time"] = self.__GdLine(page, 270, ry + 10, GD_COL_GOLD, True, False)
			row["crown"] = (i < 3)
			row["art"] = GD_RANK_ROWS[i if i < 3 else 3]
			self.gdRankRows.append(row)

	def __GdMarqueeRest(self):
		self.gdMarqOffset = 0.0
		self.gdMarqDone = False
		self.gdMarqSince = 0.0
		t = self.gdW.get("chestName") if getattr(self, "gdW", None) else None
		if t is not None:
			t.SetPosition(self.gdChestBaseX, 118)

	def __GdChestMask(self, offset):
		# the label is what moves, so undo the offset to recover the fixed box
		t = self.gdW.get("chestName")
		if t is None or not self.gdChestH:
			return
		gx, gy = t.GetGlobalPosition()
		if localeinfo.IsARABIC():
			base = gx - offset
			t.SetClippingMaskRect(int(base - GD_CHEST_TEXT_W), int(gy), int(base), int(gy + self.gdChestH))
		else:
			base = gx + offset
			t.SetClippingMaskRect(int(base), int(gy), int(base + GD_CHEST_TEXT_W), int(gy + self.gdChestH))

	def __GdTextTick(self, now):
		if not getattr(self, "gdW", None) or not self.gdChestSlot:
			return
		dt = now - self.gdMarqTime
		self.gdMarqTime = now
		if dt <= 0.0 or dt > 0.5:
			dt = 0.0
		arab = localeinfo.IsARABIC()
		bx, by = self.gdChestSlot["bg"].GetGlobalPosition()
		zx = (bx - 6 - GD_CHEST_TEXT_W) if arab else (bx + 50)
		mx, my = wndMgr.GetMousePosition()
		hot = (mx >= zx and mx < zx + GD_CHEST_TEXT_W and my >= by and my < by + 44)
		over = (self.gdChestFullW > GD_CHEST_TEXT_W)
		if hot != self.gdMarqHot:
			self.gdMarqHot = hot
			if not hot:
				self.__GdMarqueeRest()
			else:
				self.gdMarqSince = now
		if hot and over and not self.gdMarqDone and now - self.gdMarqSince >= GD_MARQUEE_DELAY:
			travel = self.gdChestFullW - GD_CHEST_TEXT_W
			self.gdMarqOffset += GD_MARQUEE_SPEED_PX * dt
			if self.gdMarqOffset >= travel:
				self.gdMarqOffset = float(travel)
				self.gdMarqDone = True
			# Arabic grows leftward from its anchor, so revealing the head slides the other way
			t = self.gdW["chestName"]
			if arab:
				t.SetPosition(int(self.gdChestBaseX + self.gdMarqOffset), 118)
			else:
				t.SetPosition(int(self.gdChestBaseX - self.gdMarqOffset), 118)
		# re-applied every frame: the mask is screen-space and must track window drags
		self.__GdChestMask(self.gdMarqOffset)

	def __GdTierName(self, tier):
		return self.__L("GUILD_DUNGEON_TIER%d_NAME" % tier, ("War Party", "Battalion", "Crusade")[tier - 1])

	def __GdBossText(self, tier):
		return self.__L("GUILD_DUNGEON_TIER%d_BOSS" % tier, ("Ice White Dragon - up to 5 players", "Elec White Dragon - up to 10 players", "Elec White Dragon - up to 25 players")[tier - 1])

	def __GdFmtTime(self, sec):
		sec = int(sec)
		if sec < 0:
			sec = 0
		return "%d:%02d" % (sec / 60, sec % 60)

	def __GdSanitizeName(self, name):
		for ch in ("|", ":", " "):
			name = name.replace(ch, "_")
		return name

	def __GdCostEntries(self, tier):
		data = self.gdTiers.get(tier)
		if not data:
			return []
		out = []
		if data["rep"] > 0:
			out.append((GD_REP_ICON, 0, data["rep"], self.__L("GUILD_DUNGEON_COST_REP", "Reputation")))
		res = data["res"]
		for i in xrange(5):
			if res[i] <= 0:
				continue
			vnum = 0
			name = ""
			if hasattr(guild, "GetResourceMeta"):
				vnum = guild.GetResourceMeta(i)[0]
				name = self.__StockTitle(i)
			if not name:
				name = "#%d" % (i + 1)
			out.append(("", vnum, res[i], name))
		return out

	def __GdCostText(self, tier):
		parts = []
		for path, vnum, qty, name in self.__GdCostEntries(tier):
			parts.append("%s %s" % (str(qty), name))
		return ", ".join(parts)

	def __GdApplySlot(self, slot, path, vnum, qty, name):
		# visibility must be applied OUTSIDE the memo guard: a slot hidden on one tier
		# and reused on another matches its old memo and would never re-Show the icon
		if slot["path"] != path or slot["vnum"] != vnum:
			slot["path"] = path
			slot["vnum"] = vnum
			hasIcon = False
			if path:
				slot["icon"].LoadImage(path)
				hasIcon = True
			elif vnum:
				try:
					item.SelectItem(vnum)
					img = item.GetIconImageFileName()
					if img and img.find("gr2") == -1:
						slot["icon"].LoadImage(img)
						hasIcon = True
				except:
					hasIcon = False
			slot["hasIcon"] = hasIcon
		if slot["hasIcon"]:
			slot["icon"].Show()
		else:
			slot["icon"].Hide()
		slot["name"] = name
		slot["qty"] = str(qty) if qty > 0 else ""
		slot["bg"].Show()
		slot["hot"].Show()
		if qty > 0:
			slot["count"].SetText(str(qty))
			slot["count"].Show()
		else:
			slot["count"].Hide()

	def __GdHideSlot(self, slot):
		slot["bg"].Hide()
		slot["icon"].Hide()
		slot["count"].Hide()
		slot["hot"].Hide()
		slot["name"] = ""

	def __OnGdSlotOverIn(self, index):
		if index == GD_CHEST_SLOT_ID:
			slot = self.gdChestSlot
		elif index < len(self.gdCostSlots):
			slot = self.gdCostSlots[index]
		else:
			return
		if not slot or not slot["name"]:
			return
		if getattr(self, "gdTip", None) is None:
			self.gdTip = uitooltip.ToolTip(200)
		tip = self.gdTip
		tip.ClearToolTip()
		tip.AppendTextLine(slot["name"], GD_COL_CREAM)
		if slot["qty"]:
			tip.AppendTextLine(self.__L("GUILD_DUNGEON_COST_QTY_FMT", "Required : %s") % slot["qty"], GD_COL_GOLD)
		tip.Show()

	def __OnGdSlotOverOut(self, index):
		if getattr(self, "gdTip", None):
			self.gdTip.Hide()

	def __RefreshDungeonPage(self):
		if not GUILD_DUNGEON_UI or not getattr(self, "gdW", None):
			return
		now = app.GetTime()
		du, dm = self.gdDaily
		wu, wm = self.gdWeekly
		w = self.gdW
		tier = self.gdSelTier

		w["daily"].SetText(self.__L("GUILD_DUNGEON_HDR_DAILY_FMT", "Starts today %s/%s") % (str(du), str(dm) if dm else "-"))
		w["weekly"].SetText(self.__L("GUILD_DUNGEON_HDR_WEEKLY_FMT", "Weekly clears %s/%s") % (str(wu), str(wm) if wm else "-"))
		cd = self.gdCooldownUntil - now
		if cd > 0:
			w["cdIcon"].Show()
			w["cooldown"].SetText(self.__L("GUILD_DUNGEON_CD_FMT", "Cooldown %s") % self.__GdFmtTime(cd))
		else:
			w["cdIcon"].Hide()
			w["cooldown"].SetText("")

		locked = 0
		if tier > 1:
			prevData = self.gdTiers.get(tier - 1)
			if not prevData or prevData["best"] <= 0:
				locked = 1

		if tier != self.gdBannerTier:
			w["banner"].LoadImage(GD_ART + GD_BANNERS[tier - 1])
			self.gdBannerTier = tier
		if locked:
			w["banner"].SetDiffuseColor(0.32, 0.32, 0.36, 1.0)
		else:
			w["banner"].SetDiffuseColor(1.0, 1.0, 1.0, 1.0)

		for key, text, color in (("tierName", self.__GdTierName(tier), GD_COL_DIM if locked else GD_COL_GOLD), ("bossLine", self.__GdBossText(tier), GD_COL_MUTED)):
			line = w[key]
			line.SetPackedFontColor(color)
			line.SetText(text)
			tw = line.GetTextSize()[0]
			bar = w[key + "Bar"]
			if tw > 0:
				bar.SetSize(tw + 12, 14)
				bar.SetPosition(self.__GdX(11, tw + 12), 64 if key == "tierName" else 81)
				bar.Show()
			else:
				bar.Hide()
		w["pageInd"].SetText(self.__L("GUILD_DUNGEON_PAGE_IND_FMT", "%s / 3") % str(tier))

		entries = self.__GdCostEntries(tier)
		for i in xrange(GD_COST_SLOTS):
			slot = self.gdCostSlots[i]
			if i < len(entries):
				path, vnum, qty, name = entries[i]
				self.__GdApplySlot(slot, path, vnum, qty, name)
			else:
				self.__GdHideSlot(slot)

		data = self.gdTiers.get(tier)
		chestVnum = self.gdChests.get(tier, 0)
		chestName = self.__L("GUILD_DUNGEON_CHEST_DEFAULT", "Dragon Chest")
		if chestVnum:
			try:
				item.SelectItem(chestVnum)
				nm = item.GetItemName()
				if nm:
					chestName = nm
			except:
				pass
		self.__GdApplySlot(self.gdChestSlot, "", chestVnum, 0, chestName)
		if chestName != self.gdChestText:
			self.gdChestText = chestName
			w["chestName"].SetText(chestName)
			self.gdChestFullW = w["chestName"].GetTextSize()[0]
			self.gdChestH = w["chestName"].GetTextSize()[1]
			self.__GdMarqueeRest()
		exp = data["exp"] if data else 0
		if exp > 0 and wm and wu >= wm:
			w["chestExp"].SetText(self.__L("GUILD_DUNGEON_EXP_CAPPED", "Weekly EXP cap reached"))
		elif exp > 0:
			w["chestExp"].SetText(self.__L("GUILD_DUNGEON_EXP_FMT", "+%s Guild EXP") % str(exp))
		else:
			w["chestExp"].SetText("")

		liveTier, liveEnd = self.gdLive
		liveLeft = liveEnd - now
		if liveTier and liveLeft <= 0:
			liveTier = 0

		mode = ""
		if locked:
			chipArt, chipKey, chipDef = "dungeon_unavailable.png", "GUILD_DUNGEON_CHIP_LOCKED", "Locked"
			detail = self.__L("GUILD_DUNGEON_DETAIL_LOCKED_FMT", "Clear %s to unlock") % self.__GdTierName(tier - 1)
		elif liveTier == tier:
			chipArt, chipKey, chipDef = "dungeon_available.png", "GUILD_DUNGEON_CHIP_LIVE", "Live"
			detail = self.__L("GUILD_DUNGEON_DETAIL_LIVE_FMT", "%s left") % self.__GdFmtTime(liveLeft)
			mode = "join"
		elif liveTier:
			chipArt, chipKey, chipDef = "dungeon_unavailable.png", "GUILD_DUNGEON_CHIP_BUSY", "Busy"
			detail = self.__L("GUILD_DUNGEON_STATE_OTHER_RUN", "Run in progress")
		elif cd > 0:
			chipArt, chipKey, chipDef = "dungeon_unavailable.png", "GUILD_DUNGEON_CHIP_COOLDOWN", "Cooldown"
			detail = self.__GdFmtTime(cd)
		elif dm and du >= dm:
			chipArt, chipKey, chipDef = "dungeon_unavailable.png", "GUILD_DUNGEON_CHIP_NOSTART", "No starts"
			detail = self.__L("GUILD_DUNGEON_STATE_DAILY", "Daily starts used")
		else:
			chipArt, chipKey, chipDef = "dungeon_available.png", "GUILD_DUNGEON_CHIP_AVAILABLE", "Available"
			detail = ""
			if self.gdOfficer:
				mode = "start"

		if w["chipArt"] != chipArt:
			w["chip"].LoadImage(GD_ART + chipArt)
			w["chipArt"] = chipArt
		w["chipText"].SetText(self.__L(chipKey, chipDef))

		own = data["best"] if data else 0
		tops = self.gdTops.get(tier, [])
		if not detail:
			if own > 0 and tops:
				detail = self.__L("GUILD_DUNGEON_DELTA_FMT", "Your best %s - #1 %s") % (self.__GdFmtTime(own), self.__GdFmtTime(tops[0][1]))
			elif own > 0:
				detail = self.__L("GUILD_DUNGEON_BEST_FMT", "Best %s") % self.__GdFmtTime(own)
			else:
				detail = self.__L("GUILD_DUNGEON_BEST_NONE", "Best --:--")
		w["detail"].SetText(detail)

		self.gdMode = mode
		if mode == "join":
			w["actBtn"].SetText(self.__L("GUILD_DUNGEON_JOIN", "Join"))
			w["actBtn"].Show()
		elif mode == "start":
			w["actBtn"].SetText(self.__L("GUILD_DUNGEON_START", "Start"))
			w["actBtn"].Show()
		else:
			w["actBtn"].Hide()

		myName = self.__GdSanitizeName(str(guild.GetGuildName()))
		for i in xrange(5):
			row = self.gdRankRows[i]
			wantArt = GD_RANK_ROWS[i if i < len(tops) and i < 3 else 3]
			if row["art"] != wantArt:
				row["img"].LoadImage(GD_ART + wantArt)
				row["art"] = wantArt
			if i < len(tops):
				mine = (tops[i][0] == myName)
				color = GD_COL_ACCENT if mine else GD_COL_CREAM
				row["name"].SetPackedFontColor(color)
				row["time"].SetPackedFontColor(GD_COL_ACCENT if mine else GD_COL_GOLD)
				row["name"].SetText(tops[i][0])
				row["time"].SetText(self.__GdFmtTime(tops[i][1]))
				row["rank"].SetText("" if (row["crown"] and i < 3) else str(i + 1))
			elif i == 0:
				row["name"].SetPackedFontColor(GD_COL_DIM)
				row["name"].SetText(self.__L("GUILD_DUNGEON_TOP_EMPTY", "No clears recorded yet"))
				row["time"].SetText("")
				row["rank"].SetText("")
			else:
				row["name"].SetText("")
				row["time"].SetText("")
				row["rank"].SetText("")

	def OnGuildDungeonCfg(self, officer, dailyUsed, dailyMax, cooldown, weekUsed, weekCap):
		if not GUILD_DUNGEON_UI:
			return
		self.gdOfficer = officer
		self.gdDaily = (dailyUsed, dailyMax)
		self.gdWeekly = (weekUsed, weekCap)
		if cooldown > 0:
			self.gdCooldownUntil = app.GetTime() + cooldown
		else:
			self.gdCooldownUntil = 0.0
		self.__RefreshDungeonPage()

	def OnGuildDungeonTier(self, tier, rep, r1, r2, r3, r4, r5, best, exp = 0):
		if not GUILD_DUNGEON_UI or tier < 1 or tier > 3:
			return
		self.gdTiers[tier] = {"rep" : rep, "res" : (r1, r2, r3, r4, r5), "best" : best, "exp" : exp}
		self.__RefreshDungeonPage()

	def OnGuildDungeonChest(self, tier, vnum):
		if not GUILD_DUNGEON_UI or tier < 1 or tier > 3:
			return
		self.gdChests[tier] = vnum
		if tier == self.gdSelTier:
			self.__RefreshDungeonPage()

	def OnGuildDungeonTop(self, tier, payload):
		if not GUILD_DUNGEON_UI or tier < 1 or tier > 3:
			return
		entries = []
		for tok in payload.split("|"):
			parts = tok.split(":")
			if len(parts) != 2:
				continue
			try:
				entries.append((parts[0], int(parts[1])))
			except ValueError:
				continue
		self.gdTops[tier] = entries
		if tier == self.gdSelTier:
			self.__RefreshDungeonPage()

	def OnGuildDungeonLive(self, tier, remain):
		if not GUILD_DUNGEON_UI:
			return
		if tier > 0 and remain > 0:
			self.gdLive = (tier, app.GetTime() + remain)
		else:
			self.gdLive = (0, 0.0)
		self.__RefreshDungeonPage()

	def OnGuildPrestigeFirsts(self, payload = "0"):
		if not getattr(self, "gpFirstLine", None):
			return
		best = 0
		ts = 0
		if payload and payload != "0":
			for tok in payload.split("|"):
				parts = tok.split(":")
				if len(parts) != 2:
					continue
				try:
					b = int(parts[0])
					t = int(parts[1])
				except ValueError:
					continue
				if b > best:
					best = b
					ts = t
		if best < 1 or best > 4:
			self.gpFirstLine.SetText("")
			return
		import time
		name = self.__L("GUILD_BAND%d_NAME" % best, ("Established", "Renowned", "Exalted", "Legendary")[best - 1])
		when = time.strftime("%Y-%m-%d", time.localtime(ts)) if ts else "?"
		self.gpFirstLine.SetText(self.__L("GUILD_PRESTIGE_FIRST_FMT", "First %s guild of the server - %s") % (name, when))

	def __OnGdArrow(self, delta):
		self.gdSelTier = (self.gdSelTier - 1 + delta) % 3 + 1
		self.__RefreshDungeonPage()

	def __OnGdActionClick(self):
		tier = self.gdSelTier
		mode = getattr(self, "gdMode", "")
		if mode == "join":
			net.SendChatPacket("/gd_join")
		elif mode == "start":
			self.gdPendingStartTier = tier
			text = self.__L("GUILD_DUNGEON_START_CONFIRM_FMT", "Start %s? %s - the guild pays now.") % (self.__GdTierName(tier), self.__GdCostText(tier))
			self.__OpenContractsQuestion(text, self.__OnGdStartAccept)

	def __OnGdStartAccept(self):
		if getattr(self, "gdPendingStartTier", 0):
			net.SendChatPacket("/gd_start %d" % self.gdPendingStartTier)
			self.gdPendingStartTier = 0
			self.gdPollTime = app.GetTime() + 1.0
		self.__CloseContractsQuestion()

	def RefreshGuildContractsPage(self):
		if self.isLoaded == 0 or not GUILD_CONTRACTS_UI:
			return
		if not self.contractCards:
			return
		my = guild.GetContractsMy()
		if not my[0]:
			return
		self.contractsRecvTime = app.GetTime()
		for slot in xrange(2):
			self.__RefreshContractCard(slot, guild.GetContractData(slot), my)
		self.__RefreshWeeklyBoxes(my)
		self.__RefreshProgressionPage(my)
		if getattr(self, "levelPopup", None) and self.levelPopup.IsShow():
			self.__RefreshLevelUpPopup()
		self.__RefreshInfoPageNew()

	def __RefreshContractCard(self, slot, data, my):
		card = self.contractCards[slot]
		nameKey, group, ctype, state, tier, completed, rerollCount, rerollCap, progress, target, secondsLeft, rerollCost, rewardRep, rewardActivity, rewardContrib, myShare, targetVnum = data
		isOfficer = my[6]
		name = getattr(localeinfo, nameKey, None) if nameKey else None
		if not name:
			name = group if group else "-"
		if name != card["objFull"]:
			if self.cardMarqueeHot is card:
				self.__CardObjRest()
			card["objFull"] = name
			self.__CardObjMeasure(card)
		card["tierNum"] = tier
		shownTier = tier
		if slot != GUILD_CONTRACT_SLOT_GRIND and shownTier > GUILD_RALLY_TIER_COUNT:
			shownTier = GUILD_RALLY_TIER_COUNT
		card["tier"].SetText(str(shownTier) if shownTier else "")

		artPath = self.__ContractArtPath(ctype, group)
		if artPath != card["artPath"]:
			card["art"].LoadImage(artPath)
			card["artPath"] = artPath

		tgt = max(1, target)
		pct = float(progress) / float(tgt)
		if pct < 0.0:
			pct = 0.0
		elif pct > 1.0:
			pct = 1.0
		card["gaugeFill"].SetRenderingRect(0.0, 0.0, -1.0 + pct, 0.0)
		card["count"].SetText("%s / %s" % (self.__CompactCount(progress), self.__CompactCount(target)))

		card["secondsLeft"] = secondsLeft
		card["contractState"] = state
		card["completed"] = completed
		card["rerollCost"] = rerollCost
		card["rerollCount"] = rerollCount
		card["rerollCap"] = rerollCap
		card["progressPair"] = (progress, target)
		card["myShare"] = myShare
		card["rewardVals"] = (rewardRep, rewardActivity, rewardContrib)
		card["targetVnum"] = targetVnum
		card["ctype"] = ctype
		card["group"] = group
		for i, v in enumerate((rewardRep, rewardActivity, rewardContrib)):
			card["rewards"][i].SetText(self.__Money(v) if v else "-")
		self.__UpdateContractStateLine(slot)

		if card["startBtn"]:
			if state == 0 and not completed and isOfficer and group and tier <= GUILD_RALLY_TIER_COUNT:
				card["startBtn"].Show()
			else:
				card["startBtn"].Hide()
		rallyLive = (slot == GUILD_CONTRACT_SLOT_RALLY and state == 1 and not completed)
		if isOfficer and not completed and not rallyLive and rerollCap > 0 and group:
			if rerollCount >= rerollCap:
				card["rerollBtn"].Disable()
			else:
				card["rerollBtn"].Enable()
			card["rerollBtn"].Show()
		else:
			card["rerollBtn"].Hide()
		if slot == GUILD_CONTRACT_SLOT_RALLY and rallyLive:
			card["shareLine"].SetText(self.__L("GUILD_CONTRACT_YOUR_SHARE_FMT", "Your share : %s Points") % self.__Money(myShare))
			card["shareLine"].Show()
		else:
			card["shareLine"].Hide()
		if self.cardTipZone and self.cardTipZone[1] == slot:
			self.__ShowCardTip(self.cardTipZone)

	def __UpdateContractStateLine(self, slot):
		if slot >= len(self.contractCards):
			return
		card = self.contractCards[slot]
		showTimer = False
		if card["completed"]:
			text = self.__L("GUILD_CONTRACT_STATE_DONE", "Completed - re-arming soon")
		elif slot == GUILD_CONTRACT_SLOT_GRIND:
			text = self.__L("GUILD_CONTRACT_YOUR_SHARE_FMT", "Your share : %s Points") % self.__Money(card["myShare"])
		elif card.get("tierNum", 0) > GUILD_RALLY_TIER_COUNT:
			text = self.__L("GUILD_CONTRACT_RALLY_DONE", "All rallies done for today")
		elif card["contractState"] == 1:
			left = card["secondsLeft"] - int(app.GetTime() - self.contractsRecvTime)
			if left < 0:
				left = 0
			text = self.__L("GUILD_CONTRACT_STATE_ENDS_IN", "Ends in %s") % ("%d:%02d" % (left / 60, left % 60))
			showTimer = True
		else:
			text = self.__L("GUILD_CONTRACT_STATE_READY", "Ready to start")
			showTimer = True
		card["state"].SetText(text)
		if showTimer:
			stateW = card["state"].GetTextSize()[0]
			if localeinfo.IsARABIC():
				card["timerIcon"].SetPosition(int(90 + stateW / 2 + 3), 141)
			else:
				card["timerIcon"].SetPosition(int(90 - stateW / 2 - 15), 141)
			card["timerIcon"].Show()
		else:
			card["timerIcon"].Hide()

	def __RefreshTierRows(self, my):
		myContrib = my[1]
		claimed = my[2]
		count = guild.GetRewardTierCount()
		for i in xrange(len(self.tierRows)):
			row = self.tierRows[i]
			if i >= count:
				row["label"].SetText("")
				row["status"].SetText("")
				row["claimBtn"].Hide()
				row["tier"] = 0
				continue
			tier, need, chestCount = guild.GetRewardTier(i)
			row["tier"] = tier
			row["label"].SetText(getattr(localeinfo, "GUILD_TIER_ROW_FMT", "Tier %s - %s contribution") % (str(tier), str(need)))
			if claimed >= tier:
				row["status"].SetPackedFontColor(0xff6ec06e)
				row["status"].SetText(getattr(localeinfo, "GUILD_TIER_CLAIMED", "Claimed"))
				row["claimBtn"].Hide()
			elif myContrib >= need:
				row["status"].SetText("")
				row["claimBtn"].Show()
			else:
				row["status"].SetPackedFontColor(0xff9a9a9a)
				row["status"].SetText("%d / %d" % (myContrib, need))
				row["claimBtn"].Hide()

	def __RefreshContractsFooter(self, my):
		if not self.contractsFooter:
			return
		if self.contractsTopLine:
			best = []
			for i in xrange(guild.GetMemberCount()):
				if not guild.IsMember(i):
					continue
				data = guild.GetMemberData(i)
				c = guild.GetMemberContribution(data[0])
				if c > 0:
					best.append((c, data[1]))
			best.sort(reverse=True)
			if best:
				parts = []
				for c, name in best[:3]:
					parts.append("%s (%d)" % (name, c))
				self.contractsTopLine.SetText(getattr(localeinfo, "GUILD_TOP_CONTRIBUTORS_FMT", "Top this week: %s") % ", ".join(parts))
			else:
				self.contractsTopLine.SetText("")
		self.contractsFooter[0].SetText(getattr(localeinfo, "GUILD_MY_CONTRIBUTION_FMT", "Your contribution: %s (rank %s of %s)") % (str(my[1]), str(my[3]), str(my[4])))
		if my[5] > 0:
			self.contractsFooter[1].SetText(getattr(localeinfo, "GUILD_SERVER_RANK_FMT", "Guild activity rank: #%s") % str(my[5]))
		else:
			self.contractsFooter[1].SetText(getattr(localeinfo, "GUILD_SERVER_RANK_UNRANKED", "Guild activity rank: outside the top 10"))

	def __RefreshProgressionPage(self, my):
		w = self.progressionWidgets
		if not w:
			return
		level, maxLevel, exp, milestone, yangCost, vault = guild.GetGuildProgression()
		if maxLevel == 0:
			return
		moneyFmt = getattr(localeinfo, "NumberToMoneyString", None)
		if moneyFmt:
			vaultText = moneyFmt(vault)
			costText = moneyFmt(yangCost)
		else:
			vaultText = str(vault)
			costText = str(yangCost)
		w["level"].SetText(getattr(localeinfo, "GUILD_PROGRESSION_LEVEL_FMT", "Guild Level %s / %s") % (str(level), str(maxLevel)))
		w["activity"].SetText(getattr(localeinfo, "GUILD_PROGRESSION_ACTIVITY_FMT", "Activity %s / %s") % (str(exp), str(milestone)))
		w["activityGauge"].SetPercentage(exp, max(1, milestone))
		w["vault"].SetText(getattr(localeinfo, "GUILD_PROGRESSION_VAULT_FMT", "Vault: %s Yang") % vaultText)
		w["cost"].SetText(getattr(localeinfo, "GUILD_PROGRESSION_COST_FMT", "Next level costs %s Yang") % costText)
		w["vaultGauge"].SetPercentage(vault, max(1, yangCost))
		isOfficer = my[6]
		reason = ""
		canLevel = False
		if level >= maxLevel:
			reason = getattr(localeinfo, "GUILD_PROGRESSION_MAXED", "Maximum level reached")
		elif not isOfficer:
			reason = getattr(localeinfo, "GUILD_PROGRESSION_OFFICER_ONLY", "Only officers can level the guild up")
		elif exp < milestone:
			reason = getattr(localeinfo, "GUILD_PROGRESSION_NEED_ACTIVITY", "Not enough guild activity yet")
		elif vault < yangCost:
			if moneyFmt:
				missing = moneyFmt(yangCost - vault)
			else:
				missing = str(yangCost - vault)
			reason = getattr(localeinfo, "GUILD_PROGRESSION_NEED_YANG_FMT", "The vault needs %s more Yang") % missing
		else:
			canLevel = True
		if canLevel:
			w["levelUpBtn"].Enable()
		else:
			w["levelUpBtn"].Disable()
		w["reason"].SetText(reason)
		self.pendingLevelUpCost = yangCost
		self.pendingLevelUpLevel = level + 1

	def __OnClaimTier(self, rowIndex):
		if rowIndex < 0 or rowIndex >= len(self.tierRows):
			return
		tier = self.tierRows[rowIndex]["tier"]
		if tier > 0:
			net.SendGuildTierClaimPacket(tier)
			self.contractsPollTime = 0.0

	def __OnRerollClick(self, slot):
		if slot < 0 or slot >= len(self.contractCards):
			return
		self.pendingRerollSlot = slot
		text = getattr(localeinfo, "GUILD_CONTRACT_REROLL_CONFIRM", "Reroll this contract for %s reputation? The new contract is random.") % str(self.contractCards[slot]["rerollCost"])
		self.__OpenContractsQuestion(text, self.__OnRerollAccept)

	def __OnRerollAccept(self):
		slot = getattr(self, "pendingRerollSlot", -1)
		if slot >= 0:
			net.SendGuildContractRerollPacket(slot)
		self.pendingRerollSlot = -1
		self.__CloseContractsQuestion()
		self.contractsPollTime = 0.0

	def __OnRallyStartClick(self, slot):
		self.pendingRallySlot = slot
		text = getattr(localeinfo, "GUILD_CONTRACT_RALLY_CONFIRM", "Start this rally now? Your guild gets 60 minutes to finish it.")
		self.__OpenContractsQuestion(text, self.__OnRallyStartAccept)

	def __OnRallyStartAccept(self):
		slot = getattr(self, "pendingRallySlot", -1)
		if slot >= 0:
			net.SendGuildRallyStartPacket(slot)
		self.pendingRallySlot = -1
		self.__CloseContractsQuestion()
		self.contractsPollTime = 0.0

	def __MakeLevelUpPopup(self):
		LV = "d:/ymir work/ui/new_guild/levelup/"
		IC = "d:/ymir work/ui/new_guild/info_page/"
		OX, OY = 8, 32
		pop = ui.BoardWithTitleBar()
		pop.SetSize(281, 212)
		pop.AddFlag("float")
		pop.AddFlag("movable")
		pop.SetTitleName(self.__L("GUILD_PROGRESSION_PAGE_TITLE", "Progression"))
		pop.SetCloseEvent(ui.__mem_func__(self.__CloseLevelUpPopup))
		bg = ui.ImageBox()
		bg.SetParent(pop)
		bg.SetPosition(OX, OY)
		bg.LoadImage(LV + "levelbg.png")
		bg.AddFlag("not_pick")
		bg.Show()
		self.levelPopupBg = bg
		title = ui.TextLine()
		title.SetParent(pop)
		title.SetPosition(OX + 132, OY + 14)
		title.SetHorizontalAlignCenter()
		title.SetVerticalAlignCenter()
		title.SetPackedFontColor(0xffffd200)
		title.AddFlag("not_pick")
		title.Show()
		self.levelPopupTitle = title
		self.levelPopupRows = {}
		for key, labY, cy, iconName, fillName in (("activity", 35, 52, "activity.png", "activity_full_red.png"), ("gold", 81, 98, "guild_yang.png", "yang_full_green.png")):
			label = ui.TextLine()
			label.SetParent(pop)
			label.SetPosition(OX + 147, OY + labY)
			label.SetHorizontalAlignCenter()
			label.SetVerticalAlignCenter()
			label.SetPackedFontColor(0xffd1b183)
			label.AddFlag("not_pick")
			label.Show()
			req = ui.TextLine()
			req.SetParent(pop)
			req.SetPosition(OX + 41, OY + cy)
			req.SetHorizontalAlignCenter()
			req.SetVerticalAlignCenter()
			req.SetPackedFontColor(0xffcabdab)
			req.AddFlag("not_pick")
			req.Show()
			gaugeBg = ui.ImageBox()
			gaugeBg.SetParent(pop)
			gaugeBg.SetPosition(OX + 74, OY + cy - 5)
			gaugeBg.LoadImage(LV + "gauge_bg.png")
			gaugeBg.AddFlag("not_pick")
			gaugeBg.Show()
			fill = ui.ExpandedImageBox()
			fill.SetParent(gaugeBg)
			fill.SetPosition(3, 3)
			fill.LoadImage(LV + fillName)
			fill.SetRenderingRect(0.0, 0.0, -1.0, 0.0)
			fill.AddFlag("not_pick")
			fill.Show()
			icon = ui.ImageBox()
			icon.SetParent(pop)
			icon.SetPosition(OX + 220, OY + labY - 1)
			icon.LoadImage(IC + iconName)
			icon.AddFlag("not_pick")
			icon.Show()
			self.levelPopupRows[key] = {"label": label, "req": req, "gaugeBg": gaugeBg, "fill": fill, "icon": icon}
		reason = ui.TextLine()
		reason.SetParent(pop)
		reason.SetPosition(OX + 132, OY + 124)
		reason.SetHorizontalAlignCenter()
		reason.SetVerticalAlignCenter()
		reason.SetPackedFontColor(0xff9a9a9a)
		reason.AddFlag("not_pick")
		reason.Show()
		self.levelPopupReason = reason
		accept = ui.Button()
		accept.SetParent(pop)
		accept.SetPosition(OX + 25, OY + 140)
		accept.SetUpVisual(LV + "accept_btn_0.png")
		accept.SetOverVisual(LV + "accept_btn_1.png")
		accept.SetDownVisual(LV + "accept_btn_2.png")
		accept.SetDisableVisual(LV + "accept_btn_0.png")
		accept.SetEvent(ui.__mem_func__(self.__OnLevelUpClick))
		accept.Show()
		self.levelPopupAccept = accept
		cancel = ui.Button()
		cancel.SetParent(pop)
		cancel.SetPosition(OX + 144, OY + 140)
		cancel.SetUpVisual(LV + "cancel_btn_0.png")
		cancel.SetOverVisual(LV + "cancel_btn_1.png")
		cancel.SetDownVisual(LV + "cancel_btn_2.png")
		cancel.SetEvent(ui.__mem_func__(self.__CloseLevelUpPopup))
		cancel.Show()
		self.levelPopupCancel = cancel
		self.levelPopup = pop

	def __RefreshLevelUpPopup(self):
		if getattr(self, "levelPopup", None) is None:
			return
		level, maxLevel, exp, milestone, yangCost, vault = guild.GetGuildProgression()
		if maxLevel == 0:
			return
		self.levelPopupTitle.SetText(self.__L("GUILD_PROGRESSION_LEVEL_FMT", "Guild Level %s / %s") % (str(level), str(maxLevel)))
		act = self.levelPopupRows["activity"]
		act["label"].SetText(self.__L("GUILD_LV_ACTIVITY_HAVE", "Activity: you have %s") % self.__CompactCount(exp))
		act["req"].SetText(self.__CompactCount(milestone))
		pa = min(1.0, max(0.0, float(exp) / float(milestone))) if milestone > 0 else 0.0
		act["fill"].SetRenderingRect(0.0, 0.0, -1.0 + pa, 0.0)
		gold = self.levelPopupRows["gold"]
		gold["label"].SetText(self.__L("GUILD_LV_GOLD_HAVE", "Gold: you have %s") % self.__CompactCount(vault))
		gold["req"].SetText(self.__CompactCount(yangCost))
		pg = min(1.0, max(0.0, float(vault) / float(yangCost))) if yangCost > 0 else 0.0
		gold["fill"].SetRenderingRect(0.0, 0.0, -1.0 + pg, 0.0)
		my = guild.GetContractsMy()
		isOfficer = my[6] if (my and my[0]) else False
		reason = ""
		canLevel = False
		if level >= maxLevel:
			reason = self.__L("GUILD_PROGRESSION_MAXED", "Maximum level reached")
		elif not isOfficer:
			reason = self.__L("GUILD_PROGRESSION_OFFICER_ONLY", "Only officers can level the guild up")
		elif exp < milestone:
			reason = self.__L("GUILD_PROGRESSION_NEED_ACTIVITY", "Not enough guild activity yet")
		elif vault < yangCost:
			reason = self.__L("GUILD_PROGRESSION_NEED_YANG_FMT", "The vault needs %s more Yang") % self.__CompactCount(yangCost - vault)
		else:
			canLevel = True
		self.levelPopupReason.SetText(reason)
		if canLevel:
			self.levelPopupAccept.Enable()
		else:
			self.levelPopupAccept.Disable()
		self.pendingLevelUpCost = yangCost
		self.pendingLevelUpLevel = level + 1

	def __OpenLevelUpPopup(self):
		if not GUILD_CONTRACTS_UI:
			return
		if getattr(self, "levelPopup", None) is None:
			self.__MakeLevelUpPopup()
		self.__RefreshLevelUpPopup()
		pop = self.levelPopup
		pop.SetPosition((wndMgr.GetScreenWidth() - pop.GetWidth()) / 2, (wndMgr.GetScreenHeight() - pop.GetHeight()) / 2)
		pop.Show()
		pop.SetTop()

	def __CloseLevelUpPopup(self):
		if getattr(self, "levelPopup", None):
			self.levelPopup.Hide()

	def __OnLevelUpClick(self):
		text = getattr(localeinfo, "GUILD_PROGRESSION_LEVELUP_CONFIRM", "Spend %s Yang to raise the guild to level %s?") % (str(getattr(self, "pendingLevelUpCost", 0)), str(getattr(self, "pendingLevelUpLevel", 0)))
		self.__OpenContractsQuestion(text, self.__OnLevelUpAccept)

	def __OnLevelUpAccept(self):
		net.SendGuildLevelUpPacket()
		self.__CloseContractsQuestion()
		self.contractsPollTime = 0.0

	def __OpenContractsQuestion(self, text, acceptFunc):
		self.__CloseContractsQuestion()
		q = uicommon.QuestionDialog()
		q.SetWidth(min(500, max(340, 6 * len(text) + 60)))
		q.SetText(text)
		q.SetAcceptEvent(ui.__mem_func__(acceptFunc))
		q.SetCancelEvent(ui.__mem_func__(self.__CloseContractsQuestion))
		q.Open()
		self.contractsQuestion = q

	def __CloseContractsQuestion(self):
		if getattr(self, "contractsQuestion", None):
			self.contractsQuestion.Close()
		self.contractsQuestion = None

	def SelectPage(self, arg):
		if GUILD_CONTRACTS_UI and not GUILD_DUNGEON_UI and arg == "BASE_INFO":
			arg = "GUILD_INFO"
		if "BOARD" == arg and not GUILD_CONTRACTS_UI:
			self.OnRefreshComments()
			if self.commentSlot:
				self.commentSlot.SetFocus()
				self.commentSlot.Show()
		else:
			if self.commentSlot:
				self.commentSlot.KillFocus()
				self.commentSlot.Hide()

		self.currentPage = arg

		if GUILD_CONTRACTS_UI and arg in ("BOARD", "BASE_INFO"):
			self.contractsPollTime = 0.0

		if GUILD_SKILLS_UI and arg == "SKILL":
			self.skillsPollTime = 0.0

		if GUILD_DUNGEON_UI and arg == "BASE_INFO":
			self.gdSelTier = 1
			self.gdPollTime = 0.0

		if GUILD_CONTRACTS_UI and arg == "GUILD_INFO" and getattr(self, "gpFirstLine", None):
			gpNow = app.GetTime()
			if gpNow >= getattr(self, "gpFirstPoll", 0.0):
				self.gpFirstPoll = gpNow + 60.0
				net.SendChatPacket("/gp_info")

		for key, btn in self.tabButtonDict.items():
			if arg != key:
				btn.SetUp()
		for key, img in self.tabDict.items():
			if arg == key:
				img.Show()
			else:
				img.Hide()
		for key, page in self.pageWindow.items():
			if arg == key:
				page.Show()
			else:
				page.Hide()
		if GUILD_CONTRACTS_UI:
			if arg == "GUILD_INFO":
				self.__ShowStockWindow()
			else:
				self.__HideStockWindow()
		self.board.SetTitleName(self.pageName[arg])
		self.__CloseAllGuildMemberPageGradeComboBox()

	def __CloseAllGuildMemberPageGradeComboBox(self):
		page = self.pageWindow["MEMBER"]

		for key, slotList in page.memberDict.items():
			slotList[1].CloseListBox()

	def RefreshGuildInfoPage(self):
		if self.isLoaded == 0:
			return

		if GUILD_CONTRACTS_UI:
			self.__RefreshInfoPageNew()
			return

		global DISABLE_DECLARE_WAR
		page = self.pageWindow["GUILD_INFO"]
		page.nameSlot.SetText(guild.GetGuildName())
		page.masterNameSlot.SetText(guild.GetGuildMasterName())
		page.guildLevelSlot.SetText(str(guild.GetGuildLevel()))
		# if page.guildMoneySlot:
			# page.guildMoneySlot.SetText(str(guild.GetGuildMoney()))

		curExp, lastExp = guild.GetGuildExperience()
		curExp *= 100
		lastExp *= 100
		page.curExpSlot.SetText(str(curExp))
		page.lastExpSlot.SetText(str(lastExp))

		if app.ENABLE_GUILD_RENEWAL:
			if lastExp == 0:
				page.GetChild("OfferButton").Hide()
			# elif curExp == lastExp - 1:
			elif player.GetMainCharacterName() == guild.GetGuildMasterName():
				page.GetChild("OfferButton").Show()

		if getattr(page, "repValueSlot", None):
			page.repValueSlot.SetText(str(guild.GetGuildReputation()))

		if GUILD_DONATION_UI:
			self.__RefreshDonateRows(page)

		curMemberCount, maxMemberCount = guild.GetGuildMemberCount()
		if maxMemberCount== 0xffff:
			page.memberCountSlot.SetText("%d / %s " % (curMemberCount, localeinfo.GUILD_MEMBER_COUNT_INFINITY))
		else:
			page.memberCountSlot.SetText("%d / %d" % (curMemberCount, maxMemberCount))

		page.levelAverageSlot.SetText(str(guild.GetGuildMemberLevelAverage()))

		mainCharacterName = player.GetMainCharacterName()
		masterName = guild.GetGuildMasterName()

		if mainCharacterName == masterName:
			page.uploadMarkButton.Show()

			if DISABLE_DECLARE_WAR:
				page.declareWarButton.Hide()
			else:
				page.declareWarButton.Show()

			if guild.HasGuildLand():
				page.uploadSymbolButton.Show()
			else:
				page.uploadSymbolButton.Hide()
		else:
			page.uploadMarkButton.Hide()
			page.declareWarButton.Hide()
			page.uploadSymbolButton.Hide()

		# >>> ENEMY GUILD UI BEGIN - removed per user request 2026-07-11 (disabled)
#		for i in xrange(guild.ENEMY_GUILD_SLOT_MAX_COUNT):
#			name = guild.GetEnemyGuildName(i)
#			nameTextLine = self.enemyGuildNameList[i]
#			if name:
#				nameTextLine.SetText(name)
#			else:
#				nameTextLine.SetText(localeinfo.GUILD_INFO_ENEMY_GUILD_EMPTY)
		# <<< ENEMY GUILD UI END

	def __GetGuildBoardCommentData(self, index):
		commentID, chrName, comment = guild.GetGuildBoardCommentData(index)
		if 0==commentID:
			if ""==chrName:
				chrName=localeinfo.UI_NONAME
			if ""==comment:
				comment=localeinfo.UI_NOCONTENTS

		return commentID, chrName, comment

	def RefreshGuildBoardPage(self):
		if self.isLoaded == 0:
			return
		if GUILD_CONTRACTS_UI:
			return

		page = self.pageWindow["BOARD"]

		self.BOARD_LINE_MAX_NUM = 12
		lineIndex = 0

		commentCount = guild.GetGuildBoardCommentCount()
		for i in xrange(commentCount):
			commentID, chrName, comment = self.__GetGuildBoardCommentData(i)

			if not comment:
				continue

			slotList = page.boardDict[lineIndex]

			if "!" == comment[0]:
				slotList[0].Show()
				slotList[1].SetText(chrName)
				slotList[2].SetText(comment[1:])

			else:
				slotList[0].Hide()
				slotList[1].SetText(chrName)
				slotList[2].SetText(comment)

			lineIndex += 1

		for i in xrange(self.BOARD_LINE_MAX_NUM - lineIndex):
			slotList = page.boardDict[lineIndex+i]
			slotList[0].Hide()
			slotList[1].SetText("")
			slotList[2].SetText("")

	def RefreshGuildMemberPage(self):
		if self.isLoaded == 0:
			return

		page = self.pageWindow["MEMBER"]

		## ScrollBar
		count = guild.GetMemberCount()
		if count > self.MEMBER_LINE_COUNT:
			page.scrollBar.SetMiddleBarSize(float(self.MEMBER_LINE_COUNT) / float(count))
			page.scrollBar.Show()
		else:
			page.scrollBar.Hide()
		self.__BuildMemberSortOrder()
		self.RefreshGuildMemberPageGradeComboBox()
		self.RefreshGuildMemberPageMemberList()

	def RefreshGuildMemberPageMemberList(self):
		if self.isLoaded == 0:
			return

		page = self.pageWindow["MEMBER"]

		for line, slotList in page.memberDict.items():
			gradeComboBox = slotList[1]
			gradeComboBox.Disable()

			if not guild.IsMember(line):
				slotList[0].SetText("")
				slotList[2].SetText("")
				slotList[3].SetText("")
				slotList[4].SetText("")
				slotList[5].SetCheck(False)
				continue

			pid, name, grade, race, level, offer, general = self.GetMemberData(line)
			if pid < 0:
				continue

			job = chr.RaceToJob(race)

			guildExperienceSummary = guild.GetGuildExperienceSummary()

			offerPercentage = 0
			if guildExperienceSummary > 0:
				offerPercentage = int(float(offer) / float(guildExperienceSummary) * 100.0)

			slotList[0].SetText(name)
			if getattr(guild, "IsMemberOnline", None):
				slotList[0].SetPackedFontColor(0xff44dd66 if guild.IsMemberOnline(pid) else 0xff909090)
			slotList[2].SetText(self.JOB_NAME.get(job, "?"))
			slotList[3].SetText(str(level))
			if app.ENABLE_GUILD_CONTRACTS:
				slotList[4].SetText(str(guild.GetMemberContribution(pid)))
			else:
				slotList[4].SetText(str(offerPercentage) + "%")
			slotList[5].SetCheck(general)
			if line > 0:
				gradeComboBox.SetCurrentItem(guild.GetGradeName(grade))
			else:
				gradeComboBox.SetCurrentItem(uiscriptlocale.GUILD_INFO_MASTER_VALUE)

			if guild.GetGradeName(grade) == "...":
				gradeComboBox.SetCurrentItem(uiscriptlocale.GUILD_BANKINFO_NAME)

			if 1 != grade:
				gradeComboBox.Enable()

	def RefreshGuildMemberPageGradeComboBox(self):
		if self.isLoaded == 0:
			return

		page = self.pageWindow["MEMBER"]

		self.CAN_CHANGE_GRADE_COUNT = 15 - 1
		for key, slotList in page.memberDict.items():
			gradeComboBox = slotList[1]
			gradeComboBox.Disable()

			if not guild.IsMember(key):
				continue

			pid, name, grade, job, level, offer, general = self.GetMemberData(key)
			if pid < 0:
				continue

			gradeComboBox.ClearItem()
			for i in xrange(self.CAN_CHANGE_GRADE_COUNT):
				if guild.GetGradeName(i + 2) == "...":
					gradeComboBox.InsertItem(i + 2, uiscriptlocale.GUILD_BANKINFO_NAME)
				else:
					gradeComboBox.InsertItem(i + 2, guild.GetGradeName(i + 2))

			if guild.GetGradeName(grade) == "...":
				gradeComboBox.SetCurrentItem(uiscriptlocale.GUILD_BANKINFO_NAME)
			else:
				gradeComboBox.SetCurrentItem(guild.GetGradeName(grade))

			if 1 != grade:
				gradeComboBox.Enable()

	def RefreshGuildSkillPage(self):
		if GUILD_SKILLS_UI:
			return

		if self.isLoaded == 0:
			return

		page = self.pageWindow["SKILL"]

		curPoint, maxPoint = guild.GetDragonPowerPoint()
		maxPoint = max(maxPoint, 1)

		if not app.ENABLE_GUILD_RENEWAL:
			page.gpValue.SetText(str(curPoint) + " / " + str(maxPoint))

			percentage = (float(curPoint) / float(maxPoint) * 100) * (float(173) / float(95))
			page.gpGauge.SetPercentage(int(percentage), 100)

		skillPoint = guild.GetGuildSkillPoint()
		page.skillPoint.SetText(str(skillPoint))

		if not app.ENABLE_GUILD_RENEWAL:
			page.passiveSlot.HideAllSlotButton()

		page.activeSlot.HideAllSlotButton()

		## Passive
		"""
		for i in xrange(len(playersettingmodule.PASSIVE_GUILD_SKILL_INDEX_LIST)):
			slotIndex = page.passiveSlot.GetStartIndex()+i
			skillIndex = playersettingmodule.PASSIVE_GUILD_SKILL_INDEX_LIST[i]
			skillLevel = guild.GetSkillLevel(slotIndex)
			skillMaxLevel = skill.GetSkillMaxLevel(skillIndex)

			page.passiveSlot.SetSlotCount(slotIndex, skillLevel)
			if skillPoint > 0:
				if skillLevel < skillMaxLevel:
					page.passiveSlot.ShowSlotButton(slotIndex)
		"""

		## Active
		for i in xrange(len(playersettingmodule.ACTIVE_GUILD_SKILL_INDEX_LIST)):
			slotIndex = page.activeSlot.GetStartIndex()+i
			skillIndex = playersettingmodule.ACTIVE_GUILD_SKILL_INDEX_LIST[i]
			skillLevel = guild.GetSkillLevel(slotIndex)

			if app.ENABLE_GUILD_RENEWAL:
				dwRealVnum = skillIndex - playersettingmodule.START_SKILL_INDEX_GUILD
				skillMaxLevel = self.GetSkillMaxLevel(dwRealVnum)
			else:
				skillMaxLevel = skill.GetSkillMaxLevel(skillIndex)

			page.activeSlot.SetSlotCount(slotIndex, skillLevel)

			if skillLevel <= 0:
				page.activeSlot.DisableCoverButton(slotIndex)
			else:
				page.activeSlot.EnableCoverButton(slotIndex)

			if app.ENABLE_GUILD_RENEWAL:
				expireTime = guild.GetActiveSkillTime(i)
				page.activeSlot.SetSkillSlot(slotIndex, skillIndex, skillLevel)
				if expireTime > app.GetGlobalTimeStamp():
					page.activeSlot.ActivateSlot(slotIndex)
				else:
					page.activeSlot.DeactivateSlot(slotIndex)

			if skillPoint > 0:
				if skillLevel < skillMaxLevel:
					page.activeSlot.ShowSlotButton(slotIndex)

	def RefreshGuildGradePage(self):
		if self.isLoaded == 0:
			return

		page = self.pageWindow["GRADE"]

		for key, slotList in page.gradeDict.items():
			name, authority = guild.GetGradeData(int(key))

			if key > 1:
				if name == "...":
					slotList[self.GRADE_SLOT_NAME].SetText(uiscriptlocale.GUILD_BANKINFO_NAME)
				else:
					slotList[self.GRADE_SLOT_NAME].SetText(name)
			else:
				slotList[self.GRADE_SLOT_NAME].SetText(uiscriptlocale.GUILD_INFO_MASTER_VALUE)
			slotList[self.GRADE_ADD_MEMBER_AUTHORITY].SetCheck(authority & guild.AUTH_ADD_MEMBER)
			slotList[self.GRADE_REMOVE_MEMBER_AUTHORITY].SetCheck(authority & guild.AUTH_REMOVE_MEMBER)
			slotList[self.GRADE_NOTICE_AUTHORITY].SetCheck(authority & guild.AUTH_NOTICE)
			slotList[self.GRADE_SKILL_AUTHORITY].SetCheck(authority & guild.AUTH_SKILL)

		self.RefreshRolesPopup()

	## GuildInfo
	def __PopupMessage(self, msg):
		self.popupMessage.SetText(msg)
		self.popupDialog.SetTop()
		self.popupDialog.Show()

	def __OnClickSelectGuildMarkButton(self):
		if guild.GetGuildLevel() < int(localeinfo.GUILD_MARK_MIN_LEVEL):
			self.__PopupMessage(localeinfo.GUILD_MARK_NOT_ENOUGH_LEVEL)
		elif not guild.MainPlayerHasAuthority(guild.AUTH_NOTICE):
			self.__PopupMessage(localeinfo.GUILD_NO_NOTICE_PERMISSION)
		else:
			self.markSelectDialog.Open()

	def __OnClickSelectGuildSymbolButton(self):
		if guild.MainPlayerHasAuthority(guild.AUTH_NOTICE):
			self.symbolSelectDialog.Open()
		else:
			self.__PopupMessage(localeinfo.GUILD_NO_NOTICE_PERMISSION)


	def __OnClickDeclareWarButton(self):
		inputDialog = DeclareGuildWarDialog()
		inputDialog.Open()
		self.inputDialog = inputDialog

	def __OnClickGuildShopButton(self):
		if getattr(net, "SendGuildOpenMerchant", None):
			net.SendGuildOpenMerchant()

	def __OnSelectMark(self, markFileName):
		ret = net.UploadMark("upload/"+markFileName)

		# MARK_BUG_FIX
		if net.ERROR_MARK_UPLOAD_NEED_RECONNECT == ret:
			self.__PopupMessage(localeinfo.UPLOAD_MARK_UPLOAD_NEED_RECONNECT);

		return ret
		# END_OF_MARK_BUG_FIX

	def __OnSelectSymbol(self, symbolFileName):
		net.UploadSymbol("upload/"+symbolFileName)

	if not app.ENABLE_GUILD_RENEWAL:
		def __OnClickOfferButton(self):
			if app.ENABLE_GUILD_DONATE and not GUILD_DONATION_UI:
				if player.GetStatus(player.LEVEL) < 75:
					self.__PopupMessage("You must be level 75")
					return
				lvl = guild.GetGuildLevel()
				if lvl >= 40: return
				if lvl >= 20:
					self.wndDonate.Open()
					return

			curEXP = unsigned32(player.GetStatus(player.EXP))
			if curEXP <= 100:
				self.__PopupMessage(localeinfo.GUILD_SHORT_EXP);
				return

			if not self.donate_exp_dlg:
				self.donate_exp_dlg = uicommon.PickETCDialog()
				self.donate_exp_dlg.SetMax(9)
				self.donate_exp_dlg.SetTitleName(localeinfo.GUILD_OFFER_EXP)
				self.donate_exp_dlg.SetAcceptEvent(ui.__mem_func__(self.OnOffer))

			self.donate_exp_dlg.Open(curEXP, 999999999, localeinfo.EXP_NAME, True)

	# def __OnClickDepositButton(self):
		# if app.ENABLE_CHEQUE_SYSTEM:
			# moneyDialog = uipicketc.PickETCDialog()

		# moneyDialog.LoadDialog()
		# moneyDialog.SetMax(6)
		# moneyDialog.SetTitleName(localeinfo.GUILD_DEPOSIT)
		# moneyDialog.SetAcceptEvent(ui.__mem_func__(self.OnDeposit))
		# moneyDialog.Open(player.GetMoney())
		# self.moneyDialog = moneyDialog

	# def __OnClickWithdrawButton(self):
		# if app.ENABLE_CHEQUE_SYSTEM:
			# moneyDialog = uipicketc.PickETCDialog()

		# moneyDialog.LoadDialog()
		# moneyDialog.SetMax(6)
		# moneyDialog.SetTitleName(localeinfo.GUILD_WITHDRAW)
		# moneyDialog.SetAcceptEvent(ui.__mem_func__(self.OnWithdraw))
		# moneyDialog.Open(guild.GetGuildMoney())
		# self.moneyDialog = moneyDialog

	def __OnBlock(self):
		popup = uicommon.PopupDialog()
		popup.SetText(localeinfo.NOT_YET_SUPPORT)
		popup.SetAcceptEvent(self.__OnClosePopupDialog)
		popup.Open()
		self.popup = popup

	def __OnClosePopupDialog(self):
		self.popup = None

	def OnDeposit(self, money):
		net.SendGuildDepositMoneyPacket(money)

	def OnWithdraw(self, money):
		net.SendGuildWithdrawMoneyPacket(money)

	def OnOffer(self, exp):
		net.SendGuildOfferPacket(exp)

	## Board
	def OnPostComment(self):
		text = self.commentSlot.GetText()
		if not text:
			return False

		net.SendGuildPostCommentPacket(text[:50])
		self.commentSlot.SetText("")
		return True

	def OnDeleteComment(self, index):
		commentID, chrName, comment = self.__GetGuildBoardCommentData(index)
		net.SendGuildDeleteCommentPacket(commentID)

	def OnRefreshComments(self):
		net.SendGuildRefreshCommentsPacket(0)

	def OnKeyDownInBoardPage(self, key):
		if key == 63:
			self.OnRefreshComments()
		return True

	## Member
	## OnEnableGeneral
	def OnChangeMemberGrade(self, lineIndex, gradeNumber):
		PID = guild.MemberIndexToPID(self.__ResolveMemberIndex(lineIndex))
		net.SendGuildChangeMemberGradePacket(PID, gradeNumber)

	def OnEnableGeneral(self, lineIndex):
		if not guild.IsMember(lineIndex):
			return

		pid, name, grade, job, level, offer, general = self.GetMemberData(lineIndex)
		if pid < 0:
			return

		net.SendGuildChangeMemberGeneralPacket(pid, 1 - general)

	## Grade
	def OnOpenChangeGradeName(self, arg):
		self.changeGradeNameDialog.SetGradeNumber(arg)
		self.changeGradeNameDialog.Open()

	def OnChangeGradeName(self):
		self.changeGradeNameDialog.Hide()
		gradeNumber = self.changeGradeNameDialog.GetGradeNumber()
		gradeName = self.changeGradeNameDialog.GetGradeName()

		if len(gradeName) == 0:
			gradeName = localeinfo.GUILD_DEFAULT_GRADE

		net.SendGuildChangeGradeNamePacket(gradeNumber, gradeName)
		return True

	def OnCheckAuthority(self, argIndex, argAuthority):
		name, authority = guild.GetGradeData(argIndex)
		net.SendGuildChangeGradeAuthorityPacket(argIndex, authority ^ argAuthority)

	def OnScrollMemberLine(self):
		scrollBar = self.pageWindow["MEMBER"].scrollBar
		pos = scrollBar.GetPos()

		count = guild.GetMemberCount()
		newLinePos = int(float(count - self.MEMBER_LINE_COUNT) * pos)

		if newLinePos != self.memberLinePos:
			self.memberLinePos = newLinePos
			self.RefreshGuildMemberPageMemberList()
			self.__CloseAllGuildMemberPageGradeComboBox()

	def GetMemberData(self, localPos):
		return guild.GetMemberData(self.__ResolveMemberIndex(localPos))

	def __ResolveMemberIndex(self, localPos):
		absPos = localPos + self.memberLinePos
		order = getattr(self, "memberSortOrder", None)
		if order is not None and 0 <= absPos < len(order):
			return order[absPos]
		return absPos

	def __BuildMemberSortOrder(self):
		count = guild.GetMemberCount()
		order = list(range(count))
		if app.ENABLE_GUILD_CONTRACTS and getattr(guild, "GetMemberContribution", None):
			def contribKey(idx):
				pid = guild.MemberIndexToPID(idx)
				return (0 if idx == 0 else 1, -guild.GetMemberContribution(pid))
			order.sort(key=contribKey)
		self.memberSortOrder = order

	## Guild Skill
	def __OnOpenHealGSPBoard(self):
		curPoint, maxPoint = guild.GetDragonPowerPoint()
		if maxPoint - curPoint <= 0:
			self.__PopupMessage(localeinfo.GUILD_CANNOT_HEAL_GSP_ANYMORE)
			return

		if not self.donate_sp_dlg:
			self.donate_sp_dlg = uicommon.PickETCDialog()
			self.donate_sp_dlg.SetMax(5)
			self.donate_sp_dlg.SetTitleName(localeinfo.GUILD_OFFER_EXP)
			self.donate_sp_dlg.SetAcceptEvent(ui.__mem_func__(self.__OnOpenHealGSPQuestionDialog))

		self.donate_sp_dlg.Open(player.GetStatus(player.SP), maxPoint - curPoint, localeinfo.MP_NAME, False)

	def __OnOpenHealGSPQuestionDialog(self, healGSP):
		money = healGSP * constinfo.GUILD_MONEY_PER_GSP

		questionDialog = uicommon.QuestionDialog()
		questionDialog.SetText(localeinfo.GUILD_DO_YOU_HEAL_GSP % (money, healGSP))
		questionDialog.SetAcceptEvent(ui.__mem_func__(self.__OnHealGSP))
		questionDialog.SetCancelEvent(ui.__mem_func__(self.__OnCloseQuestionDialog))
		questionDialog.SetWidth(400)
		questionDialog.Open()
		questionDialog.healGSP = healGSP
		self.questionDialog = questionDialog

	def __OnHealGSP(self):
		net.SendGuildChargeGSPPacket(self.questionDialog.healGSP)
		self.__OnCloseQuestionDialog()

	def __OnCloseQuestionDialog(self):
		if self.questionDialog:
			self.questionDialog.Close()
		self.questionDialog = None

	def OnPickUpGuildSkill(self, skillSlotIndex, type):
		if GUILD_SKILLS_UI:
			return

		mouseController = mousemodule.mouseController

		if False == mouseController.isAttached():
			skillIndex = player.GetSkillIndex(skillSlotIndex)
			skillLevel = guild.GetSkillLevel(skillSlotIndex)

			if skill.CanUseSkill(skillIndex) and skillLevel > 0:
				if app.IsPressed(app.DIK_LCONTROL):
					player.RequestAddToEmptyLocalQuickSlot(player.SLOT_TYPE_SKILL, skillSlotIndex)
					return

				mouseController.AttachObject(self, player.SLOT_TYPE_SKILL, skillSlotIndex, skillIndex)
		else:
			mouseController.DeattachObject()

	def OnUseGuildSkill(self, slotNumber, type):
		if GUILD_SKILLS_UI:
			return

		skillIndex = player.GetSkillIndex(slotNumber)
		skillLevel = guild.GetSkillLevel(slotNumber)

		if skillLevel <= 0:
			return

		if app.ENABLE_GUILD_RENEWAL:
			dwRealVnum = skillIndex - playersettingmodule.START_SKILL_INDEX_GUILD
			net.SendChatPacket("/guild_renew active %d" % (dwRealVnum))
		else:
			player.UseGuildSkill(slotNumber)

	def OnUpGuildSkill(self, slotNumber, type):
		if GUILD_SKILLS_UI:
			return

		skillIndex = player.GetSkillIndex(slotNumber)
		net.SendChatPacket("/gskillup " + str(skillIndex))

	def OnUseSkill(self, slotNumber, coolTime):
		if GUILD_SKILLS_UI:
			return

		if self.isLoaded == 0:
			return

		page = self.pageWindow["SKILL"]

		if page.activeSlot.HasSlot(slotNumber):
			page.activeSlot.SetSlotCoolTime(slotNumber, coolTime)

	def OnStartGuildWar(self, guildSelf, guildOpp):
		if self.isLoaded == 0:
			return

		if guild.GetGuildID() != guildSelf:
			return

		guildName = guild.GetGuildName(guildOpp)

		for guildNameTextLine in self.enemyGuildNameList:
			if localeinfo.GUILD_INFO_ENEMY_GUILD_EMPTY == guildNameTextLine.GetText():
				guildNameTextLine.SetText(guildName)
				return

	def OnEndGuildWar(self, guildSelf, guildOpp):
		if self.isLoaded == 0:
			return

		if guild.GetGuildID() != guildSelf:
			return

		guildName = guild.GetGuildName(guildOpp)

		for guildNameTextLine in self.enemyGuildNameList:
			if guildName == guildNameTextLine.GetText():
				guildNameTextLine.SetText(localeinfo.GUILD_INFO_ENEMY_GUILD_EMPTY)
				return

	## ToolTip
	def OverInItem(self, slotNumber, type):
		if mousemodule.mouseController.isAttached():
			return

		if app.ENABLE_GUILD_PASSIVE_SKILLS:
			if type == self.GUILD_SKILL_PASSIVE_SLOT:
				desc = self.passiveSkillDescList[slotNumber - 200]
				self.tooltipSkill.ClearToolTip()
				self.tooltipSkill.AppendTextLine(desc)
				self.tooltipSkill.ShowToolTip()
				return

		if None != self.tooltipSkill:
			skillIndex = player.GetSkillIndex(slotNumber)
			skillLevel = guild.GetSkillLevel(slotNumber)

			if app.ENABLE_GUILD_RENEWAL and skillIndex in playersettingmodule.ACTIVE_GUILD_SKILL_INDEX_LIST:
				self.tooltipSkill.ClearToolTip()

				dwRealVnum = skillIndex - playersettingmodule.START_SKILL_INDEX_GUILD
				expireTime = guild.GetActiveSkillTime(dwRealVnum)

				self.tooltipSkill.SetTitle(skill.GetSkillName(skillIndex, 0))

				apply, value, reqPoints = self.GetInfoApplyPassive(dwRealVnum, skillLevel)

				affStr = uitooltip.GET_AFFECT_STRING(apply, value)

				if affStr:
					self.tooltipSkill.AppendSpace(5)
					self.tooltipSkill.AppendTextLine(localeinfo.GUILD_RENEWAL_TEXT1)
					self.tooltipSkill.AppendTextLine(affStr, grp.GenerateColor(0.6911, 0.8754, 0.7068, 1.0))
					self.tooltipSkill.AppendTextLine(localeinfo.GUILD_RENEWAL_TEXT1.format(reqPoints))

					applyNext, valueNext, reqPointsNext = self.GetInfoApplyPassive(dwRealVnum, skillLevel+1)
					affStr = uitooltip.GET_AFFECT_STRING(applyNext, valueNext)

					if affStr:
						self.tooltipSkill.AppendTextLine(localeinfo.GUILD_RENEWAL_TEXT3)
						self.tooltipSkill.AppendTextLine(affStr, grp.GenerateColor(0.6911, 0.8754, 0.7068, 1.0))
						# self.tooltipSkill.AppendTextLine(localeinfo.GUILD_RENEWAL_TEXT4.format(reqPointsNext))

				if expireTime > app.GetGlobalTimeStamp():
					self.tooltipSkill.AppendSpace(5)
					self.tooltipSkill.AppendTextLine(localeinfo.GUILD_RENEWAL_TEXT5.format(localeinfo.SecondToDHM(expireTime - app.GetGlobalTimeStamp())))

				self.tooltipSkill.ShowToolTip()
				return

			self.tooltipSkill.SetSkill(skillIndex, skillLevel)

	def OverOutItem(self):
		if None != self.tooltipSkill:
			self.tooltipSkill.HideToolTip()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	if app.ENABLE_GUILD_RENEWAL:
		def ToggleGuildMission(self):
			if self.wndGuildMission.IsShow():
				self.wndGuildMission.Hide()
			else:
				self.wndGuildMission.Show()

		def OnLevelUp(self):
			self.__PopupMessage(localeinfo.GUILD_NO_LEVEL_NOW)
			return
			# curlevel = guild.GetGuildLevel()
			# if self.dLevelInfo.has_key(curlevel):
			# 	if self.dLevelInfo[0] != 0:
			# 		if not self.dlgQuestionLvUp:
			# 			self.dlgQuestionLvUp = uicommon.QuestionDialogGuildLvUp()
			# 			self.dlgQuestionLvUp.SetText(localeinfo.GUILD_RENEWAL_TEXT6)
			# 			self.dlgQuestionLvUp.SetAcceptEvent(ui.__mem_func__(self.__OnAcceptLvUP))
			# 			self.dlgQuestionLvUp.SetCancelEvent(ui.__mem_func__(self.__OnCloseQuestionDialogLvUP))
			# 			self.dlgQuestionLvUp.SetItemToolTip(self.tooltipSkill)
			#
			# 		self.dlgQuestionLvUp.AddItemSlot(0, self.dLevelInfo[0], self.dLevelInfo[1])
			# 		self.dlgQuestionLvUp.AddItemSlot(1, self.dLevelInfo[2], self.dLevelInfo[3])
			# 		self.dlgQuestionLvUp.AddItemSlot(2, self.dLevelInfo[4], self.dLevelInfo[5])
			#
			# 		self.dlgQuestionLvUp.Open()
			# 		return
			#
			# net.SendChatPacket("/guild_renew level")

		def __OnAcceptLvUP(self):
			net.SendChatPacket("/guild_renew level")
			self.__OnCloseQuestionDialog()

		def __OnCloseQuestionDialogLvUP(self):
			if self.dlgQuestionLvUp:
				self.dlgQuestionLvUp.Close()

		def SetLevelInfo(self, lv, v1, c1, v2, c2, v3, c3):
			self.dLevelInfo[lv] = (v1, c1, v2, c2, v3, c3)

		def SetPassiveInfo(self, skIndex, lv, apply, value, reqPoints):
			if not self.dPassiveInfo.has_key(skIndex):
				self.dPassiveInfo[skIndex] = {}

			self.dPassiveInfo[skIndex][lv] = (apply, value, reqPoints)

		def GetInfoApplyPassive(self, skIndex, lv):
			if skIndex not in self.dPassiveInfo:
				return (0, 0, 0)

			if lv not in self.dPassiveInfo[skIndex]:
				return (0, 0, 0)

			return self.dPassiveInfo[skIndex][lv]

		def GetSkillMaxLevel(self, skIndex):
			if skIndex not in self.dPassiveInfo:
				return 0

			return len(self.dPassiveInfo[skIndex])

		def __MakeSkillPageNew(self):
			page = self.pageWindow["SKILL"]

			page.skillPoint = page.GetChild("Skill_Plus_Value")
			page.activeSlot = page.GetChild("Active_Skill_Slot_Table")

			page.activeSlot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
			page.activeSlot.SetOverInItemEvent(lambda slotNumber, type=self.GUILD_SKILL_ACTIVE_SLOT: self.OverInItem(slotNumber, type))
			page.activeSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			page.activeSlot.SetUnselectItemSlotEvent(lambda slotNumber, type=self.GUILD_SKILL_ACTIVE_SLOT: self.OnUseGuildSkill(slotNumber, type))
			page.activeSlot.SetPressedSlotButtonEvent(lambda slotNumber, type=self.GUILD_SKILL_ACTIVE_SLOT: self.OnUpGuildSkill(slotNumber, type))
			page.activeSlot.AppendSlotButton("d:/ymir work/ui/game/windows/btn_plus_up.sub",\
											"d:/ymir work/ui/game/windows/btn_plus_over.sub",\
											"d:/ymir work/ui/game/windows/btn_plus_down.sub")

			for i in xrange(len(playersettingmodule.ACTIVE_GUILD_SKILL_INDEX_LIST)):
				slotIndex = page.activeSlot.GetStartIndex()+i
				skillIndex = playersettingmodule.ACTIVE_GUILD_SKILL_INDEX_LIST[i]

				skillLevel = guild.GetSkillLevel(slotIndex)
				expireTime = guild.GetActiveSkillTime(i)

				page.activeSlot.SetSkillSlot(slotIndex, skillIndex, skillLevel)
				page.activeSlot.SetCoverButton(slotIndex)

				if expireTime > app.GetGlobalTimeStamp():
					page.activeSlot.ActivateSlot(slotIndex)
				else:
					page.activeSlot.DeactivateSlot(slotIndex)

				page.activeSlot.RefreshSlot()
				guild.SetSkillIndex(slotIndex, i)

class BuildGuildBuildingWindow(ui.ScriptWindow):
	try:
		GUILD_CATEGORY_LIST = (
			("HEADQUARTER", localeinfo.GUILD_HEADQUARTER),
			("FACILITY", localeinfo.GUILD_FACILITY),
			("OBJECT", localeinfo.GUILD_OBJECT),
		)
	except:
		GUILD_CATEGORY_LIST = (
			("HEADQUARTER", "Main Building"),
			("FACILITY", "Facility"),
			("OBJECT", "Object"),
		)

	MODE_VIEW = 0
	MODE_POSITIONING = 1
	MODE_PREVIEW = 2

	BUILDING_ALPHA = 0.55

	ENABLE_COLOR = grp.GenerateColor(0.7607, 0.7607, 0.7607, 1.0)
	DISABLE_COLOR = grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0)

	START_INSTANCE_INDEX = 123450
	# WALL_SET_INSTANCE = 14105

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__LoadWindow()

		self.closeEvent = None
		self.popup = None
		self.mode = self.MODE_VIEW
		self.race = 0
		self.type = None
		self.x = 0
		self.y = 0
		self.z = 0
		self.rot_x = 0
		self.rot_y = 0
		self.rot_z = 0
		self.rot_x_limit = 0
		self.rot_y_limit = 0
		self.rot_z_limit = 0
		self.needMoney = 0
		self.needStoneCount = 0
		self.needLogCount = 0
		self.needPlywoodCount = 0

		# self.index = 0
		self.indexList = []
		self.raceList = []
		self.posList = []
		self.rotList = []

		index = 0
		for category in self.GUILD_CATEGORY_LIST:
			self.categoryList.InsertItem(index, category[1])
			index += 1

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			if localeinfo.IsARABIC() or localeinfo.IsVIETNAM():
				pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "buildguildbuildingwindow.py")
			else:
				pyScrLoader.LoadScriptFile(self, "uiscript/buildguildbuildingwindow.py")
		except:
			import exception
			exception.Abort("DeclareGuildWarWindow.__CreateDialog - LoadScript")

		try:
			getObject = self.GetChild
			self.board = getObject("Board")
			self.categoryList = getObject("CategoryList")
			self.buildingList = getObject("BuildingList")
			self.listScrollBar = getObject("ListScrollBar")
			self.positionButton = getObject("PositionButton")
			self.previewButton = getObject("PreviewButton")
			self.posValueX = getObject("BuildingPositionXValue")
			self.posValueY = getObject("BuildingPositionYValue")
			self.ctrlRotationX = getObject("BuildingRotationX")
			self.ctrlRotationY = getObject("BuildingRotationY")
			self.ctrlRotationZ = getObject("BuildingRotationZ")
			self.buildingPriceValue = getObject("BuildingPriceValue")
			self.buildingMaterialStoneValue = getObject("BuildingMaterialStoneValue")
			self.buildingMaterialLogValue = getObject("BuildingMaterialLogValue")
			self.buildingMaterialPlywoodValue = getObject("BuildingMaterialPlywoodValue")

			self.positionButton.SetEvent(ui.__mem_func__(self.__OnSelectPositioningMode))
			self.previewButton.SetToggleDownEvent(ui.__mem_func__(self.__OnEnterPreviewMode))
			self.previewButton.SetToggleUpEvent(ui.__mem_func__(self.__OnLeavePreviewMode))
			self.ctrlRotationX.SetEvent(ui.__mem_func__(self.__OnChangeRotation))
			self.ctrlRotationY.SetEvent(ui.__mem_func__(self.__OnChangeRotation))
			self.ctrlRotationZ.SetEvent(ui.__mem_func__(self.__OnChangeRotation))
			self.listScrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScrollBuildingList))

			getObject("CategoryList").SetEvent(ui.__mem_func__(self.__OnSelectCategory))
			getObject("BuildingList").SetEvent(ui.__mem_func__(self.__OnSelectBuilding))
			getObject("AcceptButton").SetEvent(ui.__mem_func__(self.Build))
			getObject("CancelButton").SetEvent(ui.__mem_func__(self.Close))
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))

		except:
			import exception
			exception.Abort("BuildGuildBuildingWindow.__LoadWindow - BindObject")

	def __CreateWallBlock(self, race, x, y, rot = 0.0):
		idx = self.START_INSTANCE_INDEX + len(self.indexList)
		self.indexList.append(idx)
		self.raceList.append(race)
		self.posList.append((x, y))
		self.rotList.append(rot)
		chr.CreateInstance(idx)
		chr.SelectInstance(idx)
		chr.SetVirtualID(idx)
		chr.SetInstanceType(chr.INSTANCE_TYPE_OBJECT)

		chr.SetRace(race)
		chr.SetArmor(0)
		chr.Refresh()
		chr.SetLoopMotion(chr.MOTION_WAIT)
		chr.SetBlendRenderMode(idx, self.BUILDING_ALPHA)
		chr.SetRotationAll(0.0, 0.0, rot)

		self.ctrlRotationX.SetSliderPos(0.5)
		self.ctrlRotationY.SetSliderPos(0.5)
		self.ctrlRotationZ.SetSliderPos(0.5)

	def __GetObjectSize(self, race):
		idx = self.START_INSTANCE_INDEX + 1000
		chr.CreateInstance(idx)
		chr.SelectInstance(idx)
		chr.SetVirtualID(idx)
		chr.SetInstanceType(chr.INSTANCE_TYPE_OBJECT)

		chr.SetRace(race)
		chr.SetArmor(0)
		chr.Refresh()
		chr.SetLoopMotion(chr.MOTION_WAIT)
		sx, sy, ex, ey = chr.GetBoundBoxOnlyXY(idx)
		chr.DeleteInstance(idx)
		return sx, sy, ex, ey

	def __GetBuildInPosition(self):
		zList = []
		zList.append(background.GetHeight(self.x + self.sxPos, self.y + self.syPos))
		zList.append(background.GetHeight(self.x + self.sxPos, self.y + self.eyPos))
		zList.append(background.GetHeight(self.x + self.exPos, self.y + self.syPos))
		zList.append(background.GetHeight(self.x + self.exPos, self.y + self.eyPos))
		zList.append(background.GetHeight(self.x + (self.exPos + self.sxPos) / 2, self.y + (self.eyPos + self.syPos) / 2))
		zList.sort()
		return zList[3]

	def __CreateBuildInInstance(self,race):
		self.__DeleteInstance()

		object_base = race - race % 10

		door_minX, door_minY, door_maxX, door_maxY = self.__GetObjectSize(object_base + 4)
		corner_minX, corner_minY, corner_maxX, corner_maxY = self.__GetObjectSize(object_base + 1)
		line_minX, line_minY, line_maxX, line_maxY = self.__GetObjectSize(object_base + 2)
		line_width = line_maxX - line_minX
		line_width_half = line_width / 2

		X_SIZE_STEP = 2 * 2
		Y_SIZE_STEP = 8
		sxPos = door_maxX - corner_minX + (line_width_half * X_SIZE_STEP)
		exPos = -sxPos
		syPos = 0
		eyPos = -(corner_maxY * 2 + line_width * Y_SIZE_STEP)

		self.sxPos = sxPos
		self.syPos = syPos
		self.exPos = exPos
		self.eyPos = eyPos

		z = self.__GetBuildInPosition()

		## Door
		self.__CreateWallBlock(object_base + 4, 0.0, syPos)

		## Corner
		self.__CreateWallBlock(object_base + 1, sxPos, syPos)
		self.__CreateWallBlock(object_base + 1, exPos, syPos, 270.0)
		self.__CreateWallBlock(object_base + 1, sxPos, eyPos, 90.0)
		self.__CreateWallBlock(object_base + 1, exPos, eyPos, 180.0)

		## Line
		lineBlock = object_base + 2
		line_startX = -door_maxX - line_minX - (line_width_half * X_SIZE_STEP)
		self.__CreateWallBlock(lineBlock, line_startX, eyPos)
		self.__CreateWallBlock(lineBlock, line_startX + line_width * 1, eyPos)
		self.__CreateWallBlock(lineBlock, line_startX + line_width * 2, eyPos)
		self.__CreateWallBlock(lineBlock, line_startX + line_width * 3, eyPos)
		for i in xrange(X_SIZE_STEP):
			self.__CreateWallBlock(lineBlock, line_startX + line_width * (3 + i + 1), eyPos)
		for i in xrange(X_SIZE_STEP/2):
			self.__CreateWallBlock(lineBlock, door_minX - line_maxX - line_width * i, syPos)
			self.__CreateWallBlock(lineBlock, door_maxX - line_minX + line_width * i, syPos)
		for i in xrange(Y_SIZE_STEP):
			self.__CreateWallBlock(lineBlock, sxPos, line_minX + corner_minX - line_width * i, 90.0)
			self.__CreateWallBlock(lineBlock, exPos, line_minX + corner_minX - line_width * i, 90.0)

		self.SetBuildingPosition(int(self.x), int(self.y), self.__GetBuildInPosition())

	def __DeleteInstance(self):
		if not self.indexList:
			return

		for index in self.indexList:
			chr.DeleteInstance(index)

		self.indexList = []
		self.raceList = []
		self.posList = []
		self.rotList = []

	def __CreateInstance(self, race):
		self.__DeleteInstance()

		self.race = race

		idx = self.START_INSTANCE_INDEX
		self.indexList.append(idx)
		self.posList.append((0, 0))
		self.rotList.append(0)

		chr.CreateInstance(idx)
		chr.SelectInstance(idx)
		chr.SetVirtualID(idx)
		chr.SetInstanceType(chr.INSTANCE_TYPE_OBJECT)

		chr.SetRace(race)
		chr.SetArmor(0)
		chr.Refresh()
		chr.SetLoopMotion(chr.MOTION_WAIT)
		chr.SetBlendRenderMode(idx, self.BUILDING_ALPHA)

		self.SetBuildingPosition(int(self.x), int(self.y), 0)
		self.ctrlRotationX.SetSliderPos(0.5)
		self.ctrlRotationY.SetSliderPos(0.5)
		self.ctrlRotationZ.SetSliderPos(0.5)

	"""
	if app.ENABLE_10TH_EVENT:
		def __IsTenthEventObject(self):
			if 20139 <= self.race <= 20141:
				return True
			else:
				return False

		def __TenthEventDialog(self):
			cnt = 0

			if self.race == 20139:
				cnt = 1
			elif self.race == 20140:
				cnt = 3
			elif self.race == 20141:
				cnt = 5
			else:
				return

			questionDialog = uicommon.QuestionDialog()
			questionDialog.SetText(localeinfo.TENTH_EVENT_ASK_EXCHANGE % (cnt))
			questionDialog.SetAcceptEvent(ui.__mem_func__(self.__AskExchangeTenth))
			questionDialog.SetCancelEvent(ui.__mem_func__(self.Close))
			questionDialog.Open()
			self.dlgTenth = questionDialog

		def __AskExchangeTenth(self):
			if not self.__IsEnoughMoney():
				self.__PopupDialog(localeinfo.GUILD_NOT_ENOUGH_MONEY)
				return
			if not self.__IsEnoughMaterialStone():
				self.__PopupDialog(localeinfo.GUILD_NOT_ENOUGH_MATERIAL)
				return
			if not self.__IsEnoughMaterialLog():
				self.__PopupDialog(localeinfo.GUILD_NOT_ENOUGH_MATERIAL)
				return
			if not self.__IsEnoughMaterialPlywood():
				self.__PopupDialog(localeinfo.GUILD_NOT_ENOUGH_MATERIAL)
				return

			net.SendChatPacket("/build c %d %d %d %d %d %d" % (self.race, int(self.x), int(self.y), self.rot_x, self.rot_y, self.rot_z))
			self.Close()
	"""

	def Build(self):
		"""
		if app.ENABLE_10TH_EVENT:
			if self.__IsTenthEventObject():
				self.__TenthEventDialog()
				return
		"""

		if not self.__IsEnoughMoney():
			self.__PopupDialog(localeinfo.GUILD_NOT_ENOUGH_MONEY)
			return
		if not self.__IsEnoughMaterialStone():
			self.__PopupDialog(localeinfo.GUILD_NOT_ENOUGH_MATERIAL)
			return
		if not self.__IsEnoughMaterialLog():
			self.__PopupDialog(localeinfo.GUILD_NOT_ENOUGH_MATERIAL)
			return
		if not self.__IsEnoughMaterialPlywood():
			self.__PopupDialog(localeinfo.GUILD_NOT_ENOUGH_MATERIAL)
			return

		## /build c vnum x y x_rot y_rot z_rot
		## /build d vnum
		if "BUILDIN" == self.type:
			for i in xrange(len(self.raceList)):
				race = self.raceList[i]
				xPos, yPos = self.posList[i]
				rot = self.rotList[i]
				net.SendChatPacket("/build c %d %d %d %d %d %d" % (race, int(self.x+xPos), int(self.y+yPos), self.rot_x, self.rot_y, rot))
		else:
			net.SendChatPacket("/build c %d %d %d %d %d %d" % (self.race, int(self.x), int(self.y), self.rot_x, self.rot_y, self.rot_z))

		self.Close()

	def Open(self):
		x, y, z = player.GetMainCharacterPosition()
		app.SetCameraSetting(int(x), int(-y), int(z), 3000, 0, 30)

		background.VisibleGuildArea()

		self.x = x
		self.y = y
		self.z = z
		self.categoryList.SelectItem(0)
		self.buildingList.SelectItem(0)
		self.SetTop()
		self.Show()
		self.__DisablePCBlocker()

		import debuginfo
		if debuginfo.IsDebugMode():
			self.categoryList.SelectItem(2)
			self.buildingList.SelectItem(0)

		player.SetParalysis(True)

	def Close(self):
		self.__DeleteInstance()

		background.DisableGuildArea()

		self.Hide()
		self.__OnClosePopupDialog()
		self.__EnablePCBlocker()
		self.__UnlockCameraMoving()
		if self.closeEvent:
			self.closeEvent()

		player.SetParalysis(False)

		"""
		if app.ENABLE_10TH_EVENT:
			self.dlgTenth = None
		"""

	def Destory(self):
		self.Close()

		self.ClearDictionary()
		self.board = None
		self.categoryList = None
		self.buildingList = None
		self.listScrollBar = None
		self.positionButton = None
		self.previewButton = None
		self.posValueX = None
		self.posValueY = None
		self.ctrlRotationX = None
		self.ctrlRotationY = None
		self.ctrlRotationZ = None
		self.buildingPriceValue = None
		self.buildingMaterialStoneValue = None
		self.buildingMaterialLogValue = None
		self.buildingMaterialPlywoodValue = None
		self.closeEvent = None

	def SetCloseEvent(self, event):
		self.closeEvent = event

	def __PopupDialog(self, text):
		popup = uicommon.PopupDialog()
		popup.SetText(text)
		popup.SetAcceptEvent(self.__OnClosePopupDialog)
		popup.Open()
		self.popup = popup

	def __OnClosePopupDialog(self):
		self.popup = None

	def __EnablePCBlocker(self):
		chr.SetInstanceType(chr.INSTANCE_TYPE_BUILDING)

		for idx in self.indexList:
			chr.SetBlendRenderMode(idx, 1.0)

	def __DisablePCBlocker(self):
		chr.SetInstanceType(chr.INSTANCE_TYPE_OBJECT)

		for idx in self.indexList:
			chr.SetBlendRenderMode(idx, self.BUILDING_ALPHA)

	def __OnSelectPositioningMode(self):
		if self.MODE_PREVIEW == self.mode:
			self.positionButton.SetUp()
			return

		self.mode = self.MODE_POSITIONING
		self.Hide()

	def __OnEnterPreviewMode(self):
		if self.MODE_POSITIONING == self.mode:
			self.previewButton.SetUp()
			return

		self.mode = self.MODE_PREVIEW
		self.positionButton.SetUp()
		self.__UnlockCameraMoving()
		self.__EnablePCBlocker()

	def __OnLeavePreviewMode(self):
		self.__RestoreViewMode()

	def __RestoreViewMode(self):
		self.__DisablePCBlocker()
		self.__LockCameraMoving()
		self.mode = self.MODE_VIEW
		self.positionButton.SetUp()
		self.previewButton.SetUp()

	def __IsEnoughMoney(self):
		if app.IsEnableTestServerFlag():
			return True

		curMoney = player.GetMoney()
		if curMoney < self.needMoney:
			return False

		return True

	def __IsEnoughMaterialStone(self):
		if app.IsEnableTestServerFlag():
			return True

		curStoneCount = player.GetItemCountByVnum(MATERIAL_STONE_ID)
		if curStoneCount < self.needStoneCount:
			return False
		return True

	def __IsEnoughMaterialLog(self):
		if app.IsEnableTestServerFlag():
			return True

		curLogCount = player.GetItemCountByVnum(MATERIAL_LOG_ID)
		if curLogCount < self.needLogCount:
			return False
		return True

	def __IsEnoughMaterialPlywood(self):
		if app.IsEnableTestServerFlag():
			return True

		curPlywoodCount = player.GetItemCountByVnum(MATERIAL_PLYWOOD_ID)
		if curPlywoodCount < self.needPlywoodCount:
			return False
		return True

	def __OnSelectCategory(self):
		self.listScrollBar.SetPos(0.0)
		self.__RefreshItem()

	def __SetBuildingData(self, data):
		self.buildingPriceValue.SetText(NumberToMoneyString(data["PRICE"]))

		self.needMoney = int(data["PRICE"])

		materialList = data["MATERIAL"]
		self.needStoneCount = int(materialList[MATERIAL_STONE_INDEX])
		self.needLogCount = int(materialList[MATERIAL_LOG_INDEX])
		self.needPlywoodCount = int(materialList[MATERIAL_PLYWOOD_INDEX])

		if (localeinfo.IsEUROPE() and app.GetLocalePath() != "locale/ca") and (localeinfo.IsEUROPE() and app.GetLocalePath() != "locale/br"):
			self.buildingMaterialStoneValue.SetText(materialList[MATERIAL_STONE_INDEX])
			self.buildingMaterialLogValue.SetText(materialList[MATERIAL_LOG_INDEX] )
			self.buildingMaterialPlywoodValue.SetText(materialList[MATERIAL_PLYWOOD_INDEX])
		else:
			self.buildingMaterialStoneValue.SetText(materialList[MATERIAL_STONE_INDEX] + localeinfo.THING_COUNT)
			self.buildingMaterialLogValue.SetText(materialList[MATERIAL_LOG_INDEX] + localeinfo.THING_COUNT)
			self.buildingMaterialPlywoodValue.SetText(materialList[MATERIAL_PLYWOOD_INDEX] + localeinfo.THING_COUNT)
		if self.__IsEnoughMoney():
			self.buildingPriceValue.SetPackedFontColor(self.ENABLE_COLOR)
		else:
			self.buildingPriceValue.SetPackedFontColor(self.DISABLE_COLOR)

		if self.__IsEnoughMaterialStone():
			self.buildingMaterialStoneValue.SetPackedFontColor(self.ENABLE_COLOR)
		else:
			self.buildingMaterialStoneValue.SetPackedFontColor(self.DISABLE_COLOR)

		if self.__IsEnoughMaterialLog():
			self.buildingMaterialLogValue.SetPackedFontColor(self.ENABLE_COLOR)
		else:
			self.buildingMaterialLogValue.SetPackedFontColor(self.DISABLE_COLOR)

		if self.__IsEnoughMaterialPlywood():
			self.buildingMaterialPlywoodValue.SetPackedFontColor(self.ENABLE_COLOR)
		else:
			self.buildingMaterialPlywoodValue.SetPackedFontColor(self.DISABLE_COLOR)

		self.rot_x_limit = data["X_ROT_LIMIT"]
		self.rot_y_limit = data["Y_ROT_LIMIT"]
		self.rot_z_limit = data["Z_ROT_LIMIT"]
		self.ctrlRotationX.Enable()
		self.ctrlRotationY.Enable()
		self.ctrlRotationZ.Enable()
		if 0 == self.rot_x_limit:
			self.ctrlRotationX.Disable()
		if 0 == self.rot_y_limit:
			self.ctrlRotationY.Disable()
		if 0 == self.rot_z_limit:
			self.ctrlRotationZ.Disable()

	def __OnSelectBuilding(self):
		buildingIndex = self.buildingList.GetSelectedItem()
		if buildingIndex >= len(BUILDING_DATA_LIST):
			return

		categoryIndex = self.categoryList.GetSelectedItem()
		if categoryIndex >= len(self.GUILD_CATEGORY_LIST):
			return
		selectedType = self.GUILD_CATEGORY_LIST[categoryIndex][0]

		index = 0
		for data in BUILDING_DATA_LIST:
			type = data["TYPE"]
			vnum = data["VNUM"]
			if selectedType != type:
				continue

			if index == buildingIndex:
				self.type = type
				if "BUILDIN" == self.type:
					self.__CreateBuildInInstance(vnum)
				else:
					self.__CreateInstance(vnum)

				self.__SetBuildingData(data)

			index += 1

	def __OnScrollBuildingList(self):
		viewItemCount = self.buildingList.GetViewItemCount()
		itemCount = self.buildingList.GetItemCount()
		pos = self.listScrollBar.GetPos() * (itemCount-viewItemCount)
		self.buildingList.SetBasePos(int(pos))

	def __OnChangeRotation(self):
		self.rot_x = self.ctrlRotationX.GetSliderPos() * self.rot_x_limit - self.rot_x_limit / 2
		self.rot_y = self.ctrlRotationY.GetSliderPos() * self.rot_y_limit - self.rot_y_limit / 2
		self.rot_z = (self.ctrlRotationZ.GetSliderPos() * 360 + 180) % 360
		if "BUILDIN" == self.type:
			chr.SetRotationAll(self.rot_x, self.rot_y, self.rot_z)
		else:
			chr.SetRotationAll(self.rot_x, self.rot_y, self.rot_z)

	def __LockCameraMoving(self):
		app.SetCameraSetting(int(self.x), int(-self.y), int(self.z), 3000, 0, 30)

	def __UnlockCameraMoving(self):
		app.SetDefaultCamera()

	def __RefreshItem(self):
		self.buildingList.ClearItem()

		categoryIndex = self.categoryList.GetSelectedItem()
		if categoryIndex >= len(self.GUILD_CATEGORY_LIST):
			return
		selectedType = self.GUILD_CATEGORY_LIST[categoryIndex][0]

		index = 0
		for data in BUILDING_DATA_LIST:
			if selectedType != data["TYPE"]:
				continue

			if data["SHOW"]:
				self.buildingList.InsertItem(index, data["LOCAL_NAME"])

			index += 1

		self.buildingList.SelectItem(0)

		if self.buildingList.GetItemCount() < self.buildingList.GetViewItemCount():
			self.buildingList.SetSize(120, self.buildingList.GetHeight())
			self.buildingList.LocateItem()
			self.listScrollBar.Hide()
		else:
			self.buildingList.SetSize(105, self.buildingList.GetHeight())
			self.buildingList.LocateItem()
			self.listScrollBar.Show()

	def SettleCurrentPosition(self):
		guildID = miniMap.GetGuildAreaID(self.x, self.y)

		import debuginfo
		if debuginfo.IsDebugMode():
			guildID = player.GetGuildID()

		if guildID != player.GetGuildID():
			return

		self.__RestoreViewMode()
		self.__LockCameraMoving()
		self.Show()

	def SetBuildingPosition(self, x, y, z):
		self.x = x
		self.y = y
		self.posValueX.SetText(str(int(x)))
		self.posValueY.SetText(str(int(y)))

		for i in xrange(len(self.indexList)):
			idx = self.indexList[i]
			xPos, yPos = self.posList[i]

			chr.SelectInstance(idx)
			if 0 != z:
				self.z = z
				chr.SetPixelPosition(int(x+xPos), int(y+yPos), int(z))
			else:
				chr.SetPixelPosition(int(x+xPos), int(y+yPos))

	def IsPositioningMode(self):
		if self.MODE_POSITIONING == self.mode:
			return True
		return False

	def IsPreviewMode(self):
		if self.MODE_PREVIEW == self.mode:
			return True
		return False

	def OnPressEscapeKey(self):
		self.Close()
		return True

if app.ENABLE_GUILD_DONATE:
	class DonateWindow(ui.ScriptWindow):
		DONATE_ITMES = (90010, 90011, 90012)
		def __init__(self):
			super(DonateWindow, self).__init__()
			self.questionDialog = None
			self.ToolTip = uitooltip.ItemToolTip()
			self.dntType = -1
			self.LoadWindow()

		def __del__(self):
			super(DonateWindow, self).__del__()
			del self.questionDialog

		def Destroy(self):
			self.ClearDictionary()
			self.Close()
			self.questionDialog = None
			self.ToolTip = None
			self.dntType = -1

		def Open(self):
			self.SetTop()
			self.SetCenterPosition()
			self.Show()

		def Close(self):
			self.__HideToolTip()
			self.Hide()

		def OnPressEscapeKey(self):
			self.Close()
			return True

		def LoadWindow(self):
			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "uiscript/guilddonatedialog.py")
			except:
				import exception
				exception.Abort("DonateWindow.LoadWindow - LoadScript")

			try:
				getObject = self.GetChild
				self.board = getObject("board")
				self.lowDonateBtn = getObject("NoramlDonateButton")
				self.midDonateBtn = getObject("MiddleDonateButton")
				self.largeDonateBtn = getObject("HighDonateButton")

				self.lowDonateSlot = getObject("normal_donate_get_item_slot")
				self.midDonateSlot = getObject("middle_donate_get_item_slot")
				self.largeDonateSlot = getObject("high_donate_get_item_slot")

				self.lowDonateBtn.SetEvent(ui.__mem_func__(self.__OpenQuestionDialog), localeinfo.GUILD_DONATE_QUESTION_NORMAL, 0)
				self.midDonateBtn.SetEvent(ui.__mem_func__(self.__OpenQuestionDialog), localeinfo.GUILD_DONATE_QUESTION_MIDDLE, 1)
				self.largeDonateBtn.SetEvent(ui.__mem_func__(self.__OpenQuestionDialog), localeinfo.GUILD_DONATE_QUESTION_HIGH, 2)

				self.curMedal = getObject("cur_medal_of_honor_text")
				self.donateCount = getObject("donate_count_text")

				self.lowMedalText = getObject("normal_donate_medal_of_honor")
				self.lowExpText = getObject("normal_donate_guild_exp")
				getObject("normal_donate_medal_of_honor_over_window").SAFE_SetOverInEvent(self.__ShowMedalToolTip)
				getObject("normal_donate_medal_of_honor_over_window").SAFE_SetOverOutEvent(self.__HideToolTip)
				getObject("normal_donate_guild_exp_over_window").SAFE_SetOverInEvent(self.__ShowExpToolTip)
				getObject("normal_donate_guild_exp_over_window").SAFE_SetOverOutEvent(self.__HideToolTip)


				self.midMedalText = getObject("middle_donate_medal_of_honor")
				self.midExpText = getObject("middle_donate_guild_exp")
				getObject("middle_donate_medal_of_honor_over_window").SAFE_SetOverInEvent(self.__ShowMedalToolTip)
				getObject("middle_donate_medal_of_honor_over_window").SAFE_SetOverOutEvent(self.__HideToolTip)
				getObject("middle_donate_guild_exp_over_window").SAFE_SetOverInEvent(self.__ShowExpToolTip)
				getObject("middle_donate_guild_exp_over_window").SAFE_SetOverOutEvent(self.__HideToolTip)

				self.largeMedalText = getObject("high_donate_medal_of_honor")
				self.largeExpText = getObject("high_donate_guild_exp")
				getObject("high_donate_medal_of_honor_over_window").SAFE_SetOverInEvent(self.__ShowMedalToolTip)
				getObject("high_donate_medal_of_honor_over_window").SAFE_SetOverOutEvent(self.__HideToolTip)
				getObject("high_donate_guild_exp_over_window").SAFE_SetOverInEvent(self.__ShowExpToolTip)
				getObject("high_donate_guild_exp_over_window").SAFE_SetOverOutEvent(self.__HideToolTip)

				getObject("cur_medal_of_honor_over_window").SAFE_SetOverInEvent(self.__ShowMedalToolTip)
				getObject("cur_medal_of_honor_over_window").SAFE_SetOverOutEvent(self.__HideToolTip)

				self.board.SetCloseEvent(ui.__mem_func__(self.Close))

				self.lowDonateSlot.SetOverInItemEvent(ui.__mem_func__(self.__OverInDonateItems))
				self.lowDonateSlot.SetOverOutItemEvent(ui.__mem_func__(self.__HideToolTip))

				self.midDonateSlot.SetOverInItemEvent(ui.__mem_func__(self.__OverInDonateItems))
				self.midDonateSlot.SetOverOutItemEvent(ui.__mem_func__(self.__HideToolTip))

				self.largeDonateSlot.SetOverInItemEvent(ui.__mem_func__(self.__OverInDonateItems))
				self.largeDonateSlot.SetOverOutItemEvent(ui.__mem_func__(self.__HideToolTip))


				questionDialog = uicommon.QuestionDialog()
				# questionDialog.SetText(localeinfo.GUILD_DO_YOU_HEAL_GSP % (money, healGSP))
				questionDialog.SetAcceptEvent(ui.__mem_func__(self.__SendDonate))
				questionDialog.SetCancelEvent(ui.__mem_func__(self.__OnCloseQuestionDialog))
				questionDialog.Hide()
				self.questionDialog = questionDialog
			except:
				import exception
				exception.Abort("DonateWindow.__LoadWindow - BindObject")

		def __OpenQuestionDialog(self, text, dntType):
			self.questionDialog.SetText(text)
			self.questionDialog.SetTop()
			self.questionDialog.Show()
			self.dntType = dntType

		def __OnCloseQuestionDialog(self):
			self.questionDialog.Hide()

		def __SendDonate(self):
			if self.dntType > -1:
				net.SendGuildDonatePacket(self.dntType)
			self.__OnCloseQuestionDialog()

		def __ShowMedalToolTip(self):
			self.__HideToolTip()
			self.ToolTip.AppendTextLine("Medal Of Honor")
			self.ToolTip.Show()

		def __ShowExpToolTip(self):
			self.__HideToolTip()
			self.ToolTip.AppendTextLine("EXP")
			self.ToolTip.Show()

		def __HideToolTip(self):
			self.ToolTip.ClearToolTip()
			self.ToolTip.Hide()

		def __OverInDonateItems(self, slotIndex):
			if self.ToolTip:
				self.ToolTip.SetItemToolTip(self.DONATE_ITMES[slotIndex])

		def UpdateInfos(self, dType, point, exp, arr):
			slot = self.lowDonateSlot
			pointText = self.lowMedalText
			expText = self.lowExpText
			if dType == 1:
				slot = self.midDonateSlot
				pointText = self.midMedalText
				expText = self.midExpText
			elif dType == 2:
				slot = self.largeDonateSlot
				pointText = self.largeMedalText
				expText = self.largeExpText

			pointText.SetText(localeinfo.NumberWithPoint(point))
			expText.SetText(localeinfo.NumberWithPoint(exp))

			for idx, (vnum, count) in enumerate(arr):
				slot.SetItemSlot(int(idx), vnum, count)
			slot.RefreshSlot()

		def UpdateCurrentMedalText(self, val):
			self.curMedal.SetText("{}".format(val))

		def UpdateCountText(self, val):
			self.donateCount.SetText(uiscriptlocale.GUILD_DONATE_COUNT % (val,25))
