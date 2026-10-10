# coding: latin_1

import app
import chr
import net
import player
import item

import ui
import uiscriptlocale
import dbg
import snd
import mousemodule
import wndMgr
import skill
import playersettingmodule
import quest
import localeinfo
import uitooltip
import constinfo
import osfinfo
import emotion
import playerLoad
import uicommon
import uipvmbalanceintro
import chat
from ui import ScrollBar

if app.ENABLE_CASUAL_BUFF:
	import uicasualconfirm

if app.ENABLE_QUEST_RENEWAL:
	import math, uiquest

if app.ENABLE_SKILL_COLOR_SYSTEM:
	import uiskillcolor

if app.__AUTO_SKILL_READER__:
	import systemSetting

if app.USE_BONUS_PAGE:
	import uicharacterdetails
if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

SHOW_ONLY_ACTIVE_SKILL = False
SHOW_LIMIT_SUPPORT_SKILL_LIST = []
HIDE_SUPPORT_SKILL_POINT = False
OPEN_READER_SKILL_LIST = []

SHOW_LIMIT_SUPPORT_SKILL_LIST = [121, 122, 123, 124, 130]

# Leadership skill vnum; left-clicking its skill slot opens the solo role board.
SOLO_LEADERSHIP_SKILL_INDEX = 121

if app.USE_PASSIVE_ABILITY and SHOW_LIMIT_SUPPORT_SKILL_LIST:
	SHOW_LIMIT_SUPPORT_SKILL_LIST += [210, 211, 212, 213, 214, 215, 216]

OPEN_READER_SKILL_LIST = [121, 122, 123, 124, 210, 211, 212]

# Passive-ability skills are auto/granted and never leveled from the character window,
# so they must never show the "+" level-up / open-reader button (display-only).
PASSIVE_ABILITY_SKILL_LIST = [210, 211, 212, 213, 214, 215, 216]

# PvM Mastery bindable set -- mirrors g_aPvmBindSkills in share/passive_ability.hpp.
PVM_BIND_SKILL_LIST = {
	0 : { 1 : (1, 2, 3, 4, 5, 6), 2 : (16, 17, 18, 19, 20, 21) },
	1 : { 1 : (31, 32, 33, 34, 35, 36), 2 : (46, 47, 48, 49, 50, 51) },
	2 : { 1 : (61, 62, 63, 64, 65, 66), 2 : (76, 77, 78, 79, 80, 81) },
	3 : { 1 : (91, 92, 93, 94, 95, 96), 2 : (106, 107, 108, 109, 110, 111) },
	4 : { 1 : (170, 171, 172, 173, 174, 175) },
}

NINTH_SKILLS =  []

SHOW_SKILL_COLOR_IDX = {}

FACE_IMAGE_DICT = {
	playersettingmodule.RACE_WARRIOR_M : "icon/face/warrior_m.tga",
	playersettingmodule.RACE_WARRIOR_W : "icon/face/warrior_w.tga",
	playersettingmodule.RACE_ASSASSIN_M : "icon/face/assassin_m.tga",
	playersettingmodule.RACE_ASSASSIN_W : "icon/face/assassin_w.tga",
	playersettingmodule.RACE_SURA_M : "icon/face/sura_m.tga",
	playersettingmodule.RACE_SURA_W : "icon/face/sura_w.tga",
	playersettingmodule.RACE_SHAMAN_M : "icon/face/shaman_m.tga",
	playersettingmodule.RACE_SHAMAN_W : "icon/face/shaman_w.tga",
	playersettingmodule.RACE_WOLFMAN_M : "icon/face/wolfman_m.tga",
}

def unsigned32(n):
	return n & 0xFFFFFFFFL

if app.ENABLE_QUEST_RENEWAL:
	quest_slot_listbar = {
		"name" : "Quest_Slot",
		"type" : "listbar",

		"x" : 0,
		"y" : 0,

		"width" : 210,
		"height" : 20,

		"text" : "Quest title",
		"align" : "left",

		"horizontal_align" : "left",
		"vertical_align" : "left",
		"text_horizontal_align" : "left",
		"all_align" : "left",

		"text_height": 40
	}

	quest_lable_expend_img_path_dict = {
		0: "d:/ymir work/ui/quest_re/tabcolor_1_main.tga",
		1: "d:/ymir work/ui/quest_re/tabcolor_2_sub.tga",
		# 2: "d:/ymir work/ui/quest_re/tabcolor_3_levelup.tga",
		# 3: "d:/ymir work/ui/quest_re/tabcolor_4_event.tga",
		# 4: "d:/ymir work/ui/quest_re/tabcolor_5_collection.tga",
		# 5: "d:/ymir work/ui/quest_re/tabcolor_6_system.tga",
		# 6: "d:/ymir work/ui/quest_re/tabcolor_7_scroll.tga",
		# 7: "d:/ymir work/ui/quest_re/tabcolor_8_daily.tga"
	}

	quest_label_dict = {
		0 : uiscriptlocale.QUEST_UI_TEXT_MAIN,
		1 : uiscriptlocale.QUEST_UI_TEXT_DAILY,
		# 2 : uiscriptlocale.QUEST_UI_TEXT_LEVELUP,
		# 3 : uiscriptlocale.QUEST_UI_TEXT_EVENT,
		# 4 : uiscriptlocale.QUEST_UI_TEXT_COLLECTION,
		# 5 : uiscriptlocale.QUEST_UI_TEXT_SYSTEM,
		# 6 : uiscriptlocale.QUEST_UI_TEXT_SCROLL,
		# 7 : uiscriptlocale.QUEST_UI_TEXT_DAILY,
	}

class CharacterWindow(ui.ScriptWindow):
	if app.ENABLE_CONQUEROR_LEVEL:
		ACTIVE_PAGE_SLOT_COUNT = 10 #9
		SUPPORT_PAGE_SLOT_COUNT = 18
	else:
		ACTIVE_PAGE_SLOT_COUNT = 8
		SUPPORT_PAGE_SLOT_COUNT = 12

	PAGE_SLOT_COUNT = 12
	PAGE_HORSE = 2
	PAGE_BUFFI = 3
	BUFFI_SKILL_SLOT_START = 130
	BUFFI_SKILL_COUNT = 4
	BUFFI_SKILL_VNUM_START = 163

	SKILL_GROUP_NAME_DICT = {
		playersettingmodule.JOB_WARRIOR : { 1 : localeinfo.SKILL_GROUP_WARRIOR_1, 2 : localeinfo.SKILL_GROUP_WARRIOR_2, },
		playersettingmodule.JOB_ASSASSIN : { 1 : localeinfo.SKILL_GROUP_ASSASSIN_1, 2 : localeinfo.SKILL_GROUP_ASSASSIN_2, },
		playersettingmodule.JOB_SURA : { 1 : localeinfo.SKILL_GROUP_SURA_1, 2 : localeinfo.SKILL_GROUP_SURA_2, },
		playersettingmodule.JOB_SHAMAN : { 1 : localeinfo.SKILL_GROUP_SHAMAN_1, 2 : localeinfo.SKILL_GROUP_SHAMAN_2, },
		playersettingmodule.JOB_WOLFMAN : { 1 : localeinfo.JOB_WOLFMAN1, 2 : localeinfo.JOB_WOLFMAN2, },
	}

	STAT_DESCRIPTION = {
		"HTH" : localeinfo.STAT_TOOLTIP_CON,
		"INT" : localeinfo.STAT_TOOLTIP_INT,
		"STR" : localeinfo.STAT_TOOLTIP_STR,
		"DEX" : localeinfo.STAT_TOOLTIP_DEX,
	}
	if app.ENABLE_CONQUEROR_LEVEL:
		STAT_DESCRIPTION.update({
			"SSTR" : localeinfo.STAT_TOOLTIP_SUNGMA_STR,
			"SHP" : localeinfo.STAT_TOOLTIP_SUNGMA_HP,
			"SMOVE" : localeinfo.STAT_TOOLTIP_SUNGMA_MOVE,
			"SIMMUNE" : localeinfo.STAT_TOOLTIP_SUNGMA_IMMUNE,
		})

	STAT_MINUS_DESCRIPTION = localeinfo.STAT_MINUS_DESCRIPTION

	if app.ENABLE_QUEST_RENEWAL:
		MAX_QUEST_PAGE_HEIGHT = 336.5

	if app.ENABLE_PARTY_BOUNS:
		wndPartyBonusWindow = None

	def __init__(self):
		self.toolTipSkill = None

		if app.USE_BONUS_PAGE:
			self.minimize_btn = None
			self.expand_btn = None
			self.bonus_page_wnd = None

		if app.ENABLE_SKILL_COLOR_SYSTEM:
			self.skillColorWnd = None
			self.skillColorButton = []

		if app.ENABLE_QUEST_RENEWAL:
			self.isQuestCategoryLoad = False
		
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_scale")
			self.SetAnimationPreset("modal")

		self.state = "STATUS"
		self.isLoaded = 0

		self.__Initialize()
		self.__LoadWindow()

		# self.statusPlusCommandDict = {
			# "HTH" : "/stat ht",
			# "INT" : "/stat iq",
			# "STR" : "/stat st",
			# "DEX" : "/stat dx",
		# }
#add multiple values
		self.statusPlusCommandDict={
			"HTH" : "/stat_val ht ",
			"INT" : "/stat_val iq ",
			"STR" : "/stat_val st ",
			"DEX" : "/stat_val dx ",
		}

		self.statusMinusCommandDict = {
			"HTH-" : "/stat_val- ht",
			"INT-" : "/stat_val- iq",
			"STR-" : "/stat_val- st",
			"DEX-" : "/stat_val- dx",
		}

		if app.ENABLE_CONQUEROR_LEVEL:
			self.statusConquerorPlusCommandDict = {
				"SSTR" : "/conqueror_point sstr",
				"SHP" : "/conqueror_point shp",
				"SMOVE" : "/conqueror_point smove",
				"SIMMUNE" : "/conqueror_point simmune",
			}

	def __del__(self):
		ui.ScriptWindow.__del__(self)


	def __Initialize(self):
		if app.USE_BONUS_PAGE:
			self.bonus_page_wnd = None

		if app.ENABLE_SKILL_COLOR_SYSTEM:
			self.skillColorWnd = None
			self.skillColorButton = []

		if app.ENABLE_COMBAT_POINTS:
			self.cpBaseBoard = None
			self.cpBoard = None
			self.cpBgImage = None
			self.cpGearIcon = None
			self.cpTotalIcon = None
			self.cpGearValue = None
			self.cpTotalValue = None
			self.cpExpandBtn = None
			self.cpCollapseBtn = None
			self.cpPanelVisible = True

		self.refreshToolTip = 0
		self.curSelectedSkillGroup = 0
		self.canUseHorseSkill = -1

		if app.ENABLE_SOLO_LEADERSHIP_BONUS:
			self.leadershipBoard = None         # separate float board (uiscript/leadershipboard.py)
			self.leadershipRoleButtons = []     # 6 role buttons, index 0..5 -> role idx 1..6
			self.leadershipOpenButton = None    # open button on the character window top region

		if app.ENABLE_CASUAL_BUFF:
			self.casualAvailable = False
			# last known server state
			# (active, chaosAllowed, stonesToday, stoneLimit, chaosLeft, chaosMax, secsToMidnight)
			self.casualInfo = None
			self.casualChars = []
			# boosted vnum sets from the INFO trailer (confirm-dialog icons)
			self.casualShardVnums = []
			self.casualChaosVnums = []
			self.casualConfirmDialog = None
			# cycling item icon (slot bg + icon + name) embedded in the chaos tooltip
			self.casualTipIcon = None
			self.casualTipSlot = None
			self.casualTipName = None
			self.casualTipSlotRect = None
			self.casualTipVnums = []
			self.casualTipIdx = 0
			self.casualTipNext = 0.0
			self.casualTipShown = False
			self.casualActivateButton = None
			self.casualStatusText = None
			self.casualHelpButton = None
			self.casualChaosStatusText = None
			self.casualChaosHelpButton = None
			self.casualChaosImage = None
			self.casualTimeText = None
			self.casualChaosProgressText = None
			# visual-state guards so per-kill refreshes don't reload textures
			self.casualShownActive = -1
			self.casualShownChaosActive = -1
			# client-side midnight countdown (anchored on each INFO push)
			self.casualMidnightAt = 0
			self.casualShownSecond = -1

		self.toolTip = None
		self.toolTipJob = None
		self.toolTipAlignment = None
		self.toolTipSkill = None
		self.alignmentWnd = None
		self.titleButton = None
		self.faceImage = None
		self.statusPlusLabel = None
		self.statusPlusValue = None
		self.activeSlot = None
		self.tabDict = None
		self.tabButtonDict = None
		self.pageDict = None
		self.titleBarDict = None
		self.statusPlusButtonDict = None
		self.statusMinusButtonDict = None

		self.skillPageDict = None
		if app.ENABLE_QUEST_RENEWAL:
			self.questScrollBar = None
			self.questLastScrollPosition = 0
			self.questPage = None
			self.questTitleBar = None
			self.quest_page_board_window = None
			self.quest_object_board_window = None
			self.questSlotList = []
			self.questCategory = {}
			self.questCategoryList = []

			self.questColorList = {
				"green" : 0xFF83C055,
				"blue": 0xFF45678D,
				"golden": 0xFFCAB62F,
				"default_title": 0xFFCEC6B5
			}

			self.questOpenedCategories = []
			self.questMaxOpenedCategories = 1

			self.questClicked = []
			self.questIndexMap = {}
			self.questCounterList = []
			self.questClockList = []
			self.questSeparatorList = []

			self.displayY = 0
			self.baseCutY = 0
			self.questCategoryRenderPos = []
		else:
			self.questShowingStartIndex = 0
			self.questScrollBar = None
			self.questSlot = None
			self.questNameList = None
			self.questLastTimeList = None
			self.questLastCountList = None
		self.skillGroupButton = ()
		self.buffiGroupButtonIndex = -1

		self.activeSlot = None
		self.activeSkillPointValue = None
		self.supportSkillPointValue = None
		self.skillGroupButton1 = None
		self.skillGroupButton2 = None
		self.activeSkillGroupName = None

		self.guildNameSlot = None
		self.guildNameValue = None
		self.characterNameSlot = None
		self.characterNameValue = None

		self.emotionToolTip = None
		self.soloEmotionSlot = None
		self.dualEmotionSlot = None
		if app.ENABLE_EXPRESSING_EMOTION:
			self.specialEmotionSlot = None
		
		if app.ENABLE_CONQUEROR_LEVEL:
			self.levelType = 0
			
			self.tabLevelInfoButtonDict = None
			self.tabLevelInfoPageDict = None
			self.statusConquerorPlusButtonDict = None
			
			self.passive_expanded_btn = None

	if app.USE_BONUS_PAGE or app.ENABLE_SKILL_COLOR_SYSTEM or app.ENABLE_COMBAT_POINTS:
		def OnTop(self):
			if app.USE_BONUS_PAGE and self.bonus_page_wnd:
				self.bonus_page_wnd.SetTop()

			if app.ENABLE_SKILL_COLOR_SYSTEM and self.skillColorWnd:
				self.skillColorWnd.SetTop()

			if app.ENABLE_COMBAT_POINTS and self.cpBaseBoard:
				self.cpBaseBoard.SetTop()

	def AdjustPosition(self, x, y, width):
		self.SetPosition(x - width, y)

	if app.USE_BONUS_PAGE or app.ENABLE_PARTY_BOUNS or app.ENABLE_WINDOW_POSITION_SAVE or app.ENABLE_COMBAT_POINTS or app.ENABLE_SOLO_LEADERSHIP_BONUS:
		def OnMoveWindow(self, x, y):
			if app.ENABLE_SOLO_LEADERSHIP_BONUS and getattr(self, "leadershipBoard", None) and self.leadershipBoard.IsShow():
				self.leadershipBoard.SetPosition(x, y + self.GetHeight() + 3)

			if app.ENABLE_WINDOW_POSITION_SAVE:
				uiwindowpositions.OnWindowMove("character_window", x, y)

			if app.USE_BONUS_PAGE and self.bonus_page_wnd:
				self.bonus_page_wnd.AdjustPosition(x + self.GetWidth() + 1, y)

			if app.ENABLE_PARTY_BOUNS and self.wndPartyBonusWindow:
				self.wndPartyBonusWindow.AdjustPosition(x, y + 410)

			if self.alignmentWnd and self.alignmentWnd.IsShow():
				self.alignmentWnd.AdjustPosition(x + self.GetWidth() + 3, y)

			if app.ENABLE_COMBAT_POINTS and self.cpBaseBoard:
				self.__UpdateCPPanelPosition()

	def __LoadScript(self, fileName):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, fileName)

	if app.USE_BONUS_PAGE:
		def ClickExpandButton(self):
			if not self.bonus_page_wnd:
				self.bonus_page_wnd = uicharacterdetails.CharacterDetailsUI()
				self.bonus_page_wnd.SetMainParent(self)

			self.expand_btn.Hide()
			self.minimize_btn.Show()

			(x, y) = self.GetGlobalPosition()
			uicharacterdetails.bonus_page_show_status = True
			self.bonus_page_wnd.AdjustPosition(x + self.GetWidth() + 1, y)
			self.bonus_page_wnd.Open()

			if app.ENABLE_SKILL_COLOR_SYSTEM:
				if self.skillColorWnd and self.skillColorWnd.IsShow():
					self.skillColorWnd.Hide()

		def ClickMinimizeButton(self):
			if self.bonus_page_wnd:
				uicharacterdetails.bonus_page_show_status = False
				self.bonus_page_wnd.Hide()

			self.minimize_btn.Hide()
			self.expand_btn.Show()

	def __BindObject(self):
		self.toolTip = uitooltip.ToolTip()
		self.toolTipJob = uitooltip.ToolTip()
		self.toolTipAlignment = uitooltip.ToolTip(130)

		self.faceImage = self.GetChild("Face_Image")

		faceSlot=self.GetChild("Face_Slot")
		if app.ENABLE_COMBAT_POINTS:
			faceSlot.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__ShowJobToolTip)
			faceSlot.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__HideJobToolTip)
		elif 949 == app.GetDefaultCodePage():
			faceSlot.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__ShowJobToolTip)
			faceSlot.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__HideJobToolTip)

		self.statusPlusLabel = self.GetChild("Status_Plus_Label")
		self.statusPlusValue = self.GetChild("Status_Plus_Value")

		self.characterNameSlot = self.GetChild("Character_Name_Slot")
		self.characterNameValue = self.GetChild("Character_Name")
		self.guildNameSlot = self.GetChild("Guild_Name_Slot")
		self.guildNameValue = self.GetChild("Guild_Name")
		self.characterNameSlot.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__ShowAlignmentToolTip)
		self.characterNameSlot.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__HideAlignmentToolTip)
		self.characterNameSlot.OnMouseLeftButtonDown = self.__OnClickAlignment

		self.titleButton = self.GetChild2("title_button")
		if self.titleButton:
			titleText = getattr(localeinfo, "TITLE_WINDOW_TITLE", "Titles")
			if not titleText or titleText.startswith("Locale not found"):
				titleText = "Titles"
			self.titleButton.SetText(titleText)
			self.titleButton.SetTextColor(0xffe2d6ba)
			self.titleButton.SetOutline()
			# the medal is baked into the left of the plate (right, in the ae art)
			if self.titleButton.ButtonText:
				if localeinfo.IsARABIC():
					self.titleButton.ButtonText.SetPosition(29, 10)
				else:
					self.titleButton.ButtonText.SetPosition(49, 10)
			self.titleButton.SetEvent(ui.__mem_func__(self.__OnClickTitleButton))

		# Conqueror level display is unused on this server; the titles button
		# occupies its slot.
		conquerorLevelButton = self.GetChild2("change_conqueror_button")
		if conquerorLevelButton:
			conquerorLevelButton.Hide()

		self.activeSlot = self.GetChild("Skill_Active_Slot")
		self.activeSkillPointValue = self.GetChild("Active_Skill_Point_Value")
		self.supportSkillPointValue = self.GetChild("Support_Skill_Point_Value")
		self.skillGroupButton1 = self.GetChild("Skill_Group_Button_1")
		self.skillGroupButton2 = self.GetChild("Skill_Group_Button_2")
		self.activeSkillGroupName = self.GetChild("Active_Skill_Group_Name")

		if app.ENABLE_QUEST_RENEWAL:
			self.questScrollBar = self.GetChild("Quest_ScrollBar")
			self.questPage = self.GetChild("Quest_Page")
			self.questTitleBar = self.GetChild("Quest_TitleBar")
			self.quest_page_board_window = self.GetChild("quest_page_board_window")
			self.quest_object_board_window = self.GetChild("quest_object_board_window")

		# ENABLE_CASUAL_BUFF: the AE uiscript carries a 5th page — CASUAL sits
		# THIRD in the strip (STATUS, SKILL, CASUAL, EMOTICON, QUEST), shifting
		# EMOTICON/QUEST to Tab_04/Tab_05. Other locale scripts still have the
		# 4-tab layout, so bind by what the loaded script actually contains.
		self.casualAvailable = False
		if app.ENABLE_CASUAL_BUFF:
			if self.GetChild2("Tab_05") and self.GetChild2("Casual_Page"):
				self.casualAvailable = True

		if self.casualAvailable:
			self.tabDict = {
				"STATUS" : self.GetChild("Tab_01"),
				"SKILL" : self.GetChild("Tab_02"),
				"CASUAL" : self.GetChild("Tab_03"),
				"EMOTICON" : self.GetChild("Tab_04"),
				"QUEST" : self.GetChild("Tab_05"),
			}

			self.tabButtonDict = {
				"STATUS" : self.GetChild("Tab_Button_01"),
				"SKILL" : self.GetChild("Tab_Button_02"),
				"CASUAL" : self.GetChild("Tab_Button_03"),
				"EMOTICON" : self.GetChild("Tab_Button_04"),
				"QUEST" : self.GetChild("Tab_Button_05")
			}

			self.pageDict = {
				"STATUS" : self.GetChild("Character_Page"),
				"SKILL" : self.GetChild("Skill_Page"),
				"CASUAL" : self.GetChild("Casual_Page"),
				"EMOTICON" : self.GetChild("Emoticon_Page"),
				"QUEST" : self.GetChild("Quest_Page")
			}

			self.titleBarDict = {
				"STATUS" : self.GetChild("Character_TitleBar"),
				"SKILL" : self.GetChild("Skill_TitleBar"),
				"CASUAL" : self.GetChild("Casual_TitleBar"),
				"EMOTICON" : self.GetChild("Emoticon_TitleBar"),
				"QUEST" : self.GetChild("Quest_TitleBar")
			}

			## casual page, upper section: activation icon + status line + help
			self.casualActivateButton = self.GetChild2("Casual_Activate_Button")
			self.casualStatusText = self.GetChild2("Casual_Status_Text")
			self.casualHelpButton = self.GetChild2("Casual_Help_Button")

			## lower section: Blessing of Chaos
			self.casualChaosStatusText = self.GetChild2("Casual_Chaos_Status_Text")
			self.casualChaosHelpButton = self.GetChild2("Casual_Chaos_Help_Button")
			self.casualChaosImage = self.GetChild2("Casual_Chaos_Image")
			self.casualTimeText = self.GetChild2("Casual_Time_Text")
			self.casualChaosProgressText = self.GetChild2("Casual_Chaos_Progress_Text")
			self.casualShownActive = -1
			self.casualShownChaosActive = -1
			self.casualShownSecond = -1

			## upper status + clock lines render centered around their anchor
			## (uiscript anchors them at the board midpoint)
			if self.casualStatusText:
				self.casualStatusText.SetHorizontalAlignCenter()
			if self.casualTimeText:
				self.casualTimeText.SetHorizontalAlignCenter()

			if self.casualActivateButton:
				self.casualActivateButton.SetEvent(ui.__mem_func__(self.__OnClickCasualActivate))

			# rich, state-aware tooltips (own ungated handlers — the generic
			# __ShowToolTipButton/__HideToolTip are conqueror-gated). SetShow/
			# HideToolTipEvent only exist on Button, so the status text/timer/
			# icon info is folded into the activate-button + ? tooltips.
			if self.casualHelpButton:
				self.casualHelpButton.SetShowToolTipEvent(ui.__mem_func__(self.__ShowCasualBuffTip))
				self.casualHelpButton.SetHideToolTipEvent(ui.__mem_func__(self.__HideCasualTip))

			if self.casualChaosHelpButton:
				self.casualChaosHelpButton.SetShowToolTipEvent(ui.__mem_func__(self.__ShowCasualChaosTip))
				self.casualChaosHelpButton.SetHideToolTipEvent(ui.__mem_func__(self.__HideCasualTip))

			if self.casualActivateButton:
				self.casualActivateButton.SetShowToolTipEvent(ui.__mem_func__(self.__ShowCasualActivateTip))
				self.casualActivateButton.SetHideToolTipEvent(ui.__mem_func__(self.__HideCasualTip))

			self.__RefreshCasualPage()
		else:
			self.tabDict = {
				"STATUS" : self.GetChild("Tab_01"),
				"SKILL" : self.GetChild("Tab_02"),
				"EMOTICON" : self.GetChild("Tab_03"),
				"QUEST" : self.GetChild("Tab_04"),
			}

			self.tabButtonDict = {
				"STATUS" : self.GetChild("Tab_Button_01"),
				"SKILL" : self.GetChild("Tab_Button_02"),
				"EMOTICON" : self.GetChild("Tab_Button_03"),
				"QUEST" : self.GetChild("Tab_Button_04")
			}

			self.pageDict = {
				"STATUS" : self.GetChild("Character_Page"),
				"SKILL" : self.GetChild("Skill_Page"),
				"EMOTICON" : self.GetChild("Emoticon_Page"),
				"QUEST" : self.GetChild("Quest_Page")
			}

			self.titleBarDict = {
				"STATUS" : self.GetChild("Character_TitleBar"),
				"SKILL" : self.GetChild("Skill_TitleBar"),
				"EMOTICON" : self.GetChild("Emoticon_TitleBar"),
				"QUEST" : self.GetChild("Quest_TitleBar")
			}

		self.statusPlusButtonDict = {
			"HTH" : self.GetChild("HTH_Plus"),
			"INT" : self.GetChild("INT_Plus"),
			"STR" : self.GetChild("STR_Plus"),
			"DEX" : self.GetChild("DEX_Plus"),
		}

		self.statusMinusButtonDict = {
			"HTH-" : self.GetChild("HTH_Minus"),
			"INT-" : self.GetChild("INT_Minus"),
			"STR-" : self.GetChild("STR_Minus"),
			"DEX-" : self.GetChild("DEX_Minus"),
		}

		self.skillPageDict = {
			"ACTIVE" : self.GetChild("Skill_Active_Slot"),
			"SUPPORT" : self.GetChild("Skill_ETC_Slot"),
			"HORSE" : self.GetChild("Skill_Active_Slot"),
			"BUFFI" : self.GetChild("Skill_Active_Slot"),
		}

		self.skillPageStatDict = {
			"SUPPORT" : player.SKILL_SUPPORT,
			"ACTIVE" : player.SKILL_ACTIVE,
			"HORSE" : player.SKILL_HORSE,
			"BUFFI" : 0,
		}

		self.skillGroupButton = (
			self.GetChild("Skill_Group_Button_1"),
			self.GetChild("Skill_Group_Button_2"),
		)
		if app.__BUFFI_SUPPORT__:
			buffiGroupBtn = self.GetChild2("Skill_Group_Button_3")
			if buffiGroupBtn:
				self.buffiGroupButtonIndex = len(self.skillGroupButton)
				self.skillGroupButton = self.skillGroupButton + (buffiGroupBtn,)

		if app.ENABLE_CONQUEROR_LEVEL:
			self.tabLevelInfoButtonDict = {
				player.LEVEL_TYPE_BASE : self.GetChild("change_base_button"),
				player.LEVEL_TYPE_CONQUEROR : self.GetChild("change_conqueror_button")
			}

			self.tabLevelInfoPageDict = {
				player.LEVEL_TYPE_BASE : self.GetChild("base_info"),
				player.LEVEL_TYPE_CONQUEROR : self.GetChild("sungma_info"),
			}

			self.statusConquerorPlusButtonDict = {
				"SSTR" : self.GetChild("sungma_str_plus"),
				"SHP" : self.GetChild("sungma_hp_plus"),
				"SMOVE" : self.GetChild("sungma_move_plus"),
				"SIMMUNE" : self.GetChild("sungma_immune_plus"),
			}

			## TabButton tooltips — the 5-tab casual layout puts CASUAL third and
			## shifts EMOTICON/QUEST to buttons 4/5, so bind per loaded layout
			if app.ENABLE_CASUAL_BUFF and self.casualAvailable:
				tabToolTipList = (
					("Tab_Button_01", localeinfo.STAT_TOOLTIP_TAB_CHARACTER),
					("Tab_Button_02", localeinfo.STAT_TOOLTIP_TAB_SKILL),
					("Tab_Button_03", localeinfo.STAT_TOOLTIP_TAB_CASUAL),
					("Tab_Button_04", localeinfo.STAT_TOOLTIP_TAB_EMOTICON),
					("Tab_Button_05", localeinfo.STAT_TOOLTIP_TAB_QUEST),
				)
			else:
				tabToolTipList = (
					("Tab_Button_01", localeinfo.STAT_TOOLTIP_TAB_CHARACTER),
					("Tab_Button_02", localeinfo.STAT_TOOLTIP_TAB_SKILL),
					("Tab_Button_03", localeinfo.STAT_TOOLTIP_TAB_EMOTICON),
					("Tab_Button_04", localeinfo.STAT_TOOLTIP_TAB_QUEST),
				)

			for (tabButtonName, tabToolTipText) in tabToolTipList:
				self.GetChild(tabButtonName).SetShowToolTipEvent(ui.__mem_func__(self.__ShowToolTipButton), tabToolTipText)
				self.GetChild(tabButtonName).SetHideToolTipEvent(ui.__mem_func__(self.__HideToolTip))

			## Level
			self.GetChild("Lv_ToolTip").SetShowToolTipEvent(ui.__mem_func__(self.__ShowToolTipButton), localeinfo.STAT_TOOLTIP_LEVEL)
			self.GetChild("Lv_ToolTip").SetHideToolTipEvent(ui.__mem_func__(self.__HideToolTip))
			## EXP
			self.GetChild("Exp_ToolTip").SetShowToolTipEvent(ui.__mem_func__(self.__ShowToolTipButton), localeinfo.STAT_TOOLTIP_EXP)
			self.GetChild("Exp_ToolTip").SetHideToolTipEvent(ui.__mem_func__(self.__HideToolTip))

			## Base Level
			self.GetChild("change_base_button").SetShowToolTipEvent(ui.__mem_func__(self.__ShowToolTipButton), localeinfo.STAT_TOOLTIP_BASE_LEVEL)
			self.GetChild("change_base_button").SetHideToolTipEvent(ui.__mem_func__(self.__HideToolTip))
			## Conqueror Level
			self.GetChild("change_conqueror_button").SetShowToolTipEvent(ui.__mem_func__(self.__ShowToolTipButton), localeinfo.STAT_TOOLTIP_CONQUEROR_LEVEL)
			self.GetChild("change_conqueror_button").SetHideToolTipEvent(ui.__mem_func__(self.__HideToolTip))
			## Passive Relic
			self.passive_expanded_btn = self.GetChild("passive_expanded_btn")
			self.passive_expanded_btn.SetShowToolTipEvent(ui.__mem_func__(self.__ShowToolTipButton), localeinfo.STAT_TOOLTIP_PASSIVE)
			self.passive_expanded_btn.SetHideToolTipEvent(ui.__mem_func__(self.__HideToolTip))
			self.passive_expanded_btn.Hide()

			## Char Status Info
			self.GetChild("Char_Info_Status_img").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_STAT : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("Char_Info_Status_img").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## Status Plus Points
			self.GetChild("Status_Plus_Label").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_POINT : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("Status_Plus_Label").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()

			## CON (Constitution)
			self.GetChild("HTH_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_IMG_CON : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("HTH_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## INT (Intelligence)
			self.GetChild("INT_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_IMG_INT : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("INT_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## STR (Strength)
			self.GetChild("STR_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_IMG_STR : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("STR_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## DEX (Dexterity)
			self.GetChild("DEX_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_IMG_DEX : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("DEX_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()

			## HP (Health)
			self.GetChild("HEL_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_HP : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("HEL_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## SP (Stamina)
			self.GetChild("SP_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_SP : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("SP_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## ATT (Attack)
			self.GetChild("ATT_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_ATT : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("ATT_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## DEF (Defense)
			self.GetChild("DEF_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_DEF : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("DEF_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()

			## MSPD (Move Speed)
			self.GetChild("MSPD_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_MOVE_SPEED : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("MSPD_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## ASPD (Attack Speed)
			self.GetChild("ASPD_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_ATT_SPEED : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("ASPD_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## CSPD (Cast Speed)
			self.GetChild("CSPD_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_CAST_SPEED : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("CSPD_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## MATT (Magic Attack)
			self.GetChild("MATT_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_MAG_ATT : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("MATT_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## MDEF (Magic Defense)
			self.GetChild("MDEF_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_MAG_DEF : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("MDEF_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## EF (Evasion Resistance)
			self.GetChild("ER_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_DODGE_PER : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("ER_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()

			## SUNGMA_STR
			self.GetChild("SUNGMA_STR_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_SUNGMA_STR : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("SUNGMA_STR_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## SUNGMA_HP
			self.GetChild("SUNGMA_HP_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_SUNGMA_HP : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("SUNGMA_HP_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## SUNGMA_MOVE
			self.GetChild("SUNGMA_MOVE_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_SUNGMA_MOVE : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("SUNGMA_MOVE_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## SUNGMA_IMMUNE
			self.GetChild("SUNGMA_IMMUNE_IMG").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_SUNGMA_IMMUNE : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("SUNGMA_IMMUNE_IMG").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## Active Skill Point Label
			self.GetChild("Active_Skill_Point_Label").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_POINT : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("Active_Skill_Point_Label").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			## Support Skill Point Label
			self.GetChild("Support_Skill_ToolTip").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_SUPPORT_SKILL : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("Support_Skill_ToolTip").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()

			self.GetChild("Action_Bar_Img").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_ACTION : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("Action_Bar_Img").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			self.GetChild("Reaction_Bar_Img").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_REACTION : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("Reaction_Bar_Img").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()
			self.GetChild("Special_Action_Bar_Img").OnMouseOverIn = lambda arg = localeinfo.STAT_TOOLTIP_SPECIAL_ACTION : ui.__mem_func__(self.__ShowToolTip)(arg)
			self.GetChild("Special_Action_Bar_Img").OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()

		global SHOW_ONLY_ACTIVE_SKILL
		global HIDE_SUPPORT_SKILL_POINT
		if SHOW_ONLY_ACTIVE_SKILL or HIDE_SUPPORT_SKILL_POINT:
			self.GetChild("Support_Skill_Point_Label").Hide()

		self.soloEmotionSlot = self.GetChild("SoloEmotionSlot")
		self.dualEmotionSlot = self.GetChild("DualEmotionSlot")
		if app.ENABLE_EXPRESSING_EMOTION:
			self.specialEmotionSlot = self.GetChild("SpecialEmotionSlot")
		self.__SetEmotionSlot()

		if app.ENABLE_QUEST_RENEWAL:
			self.questScrollBar.SetParent(self.quest_page_board_window)
			for i in xrange(quest.QUEST_CATEGORY_MAX_NUM):
				self.questCategory = ui.SubTitleBar()
				self.questCategory.SetParent(self.questPage)
				self.questCategory.MakeSubTitleBar(210)
				self.questCategory.SetText(quest_label_dict[i])
				self.questCategory.SetSize(210, 16)
				self.questCategory.SetTextColor(0xffCEC6B5)
				self.questCategory.SetPosition(0, 0)#150 100

				self.questCategoryList.append(self.questCategory)

				# self.questCategoryList.append(self.questCategory[i])
				# self.questCategoryList.append(self.GetChild("Quest_Category_0" + str(i)))
				self.questCategoryRenderPos.append(0)

			self.questScrollBar.SetParent(self.questPage)
			self.RearrangeQuestCategories(xrange(quest.QUEST_CATEGORY_MAX_NUM))
		else:
			self.questShowingStartIndex = 0
			self.questScrollBar = self.GetChild("Quest_ScrollBar")
			self.questScrollBar.SetScrollEvent(ui.__mem_func__(self.OnQuestScroll))
			self.questSlot = self.GetChild("Quest_Slot")
			for i in xrange(quest.QUEST_MAX_NUM):
				self.questSlot.HideSlotBaseImage(i)
				self.questSlot.SetCoverButton(i,\
					"d:/ymir work/ui/game/quest/slot_button_01.sub",\
					"d:/ymir work/ui/game/quest/slot_button_02.sub",\
					"d:/ymir work/ui/game/quest/slot_button_03.sub",\
					"d:/ymir work/ui/game/quest/slot_button_03.sub", True)

			self.questNameList = []
			self.questLastTimeList = []
			self.questLastCountList = []
			for i in xrange(quest.QUEST_MAX_NUM):
				self.questNameList.append(self.GetChild("Quest_Name_0" + str(i)))
				self.questLastTimeList.append(self.GetChild("Quest_LastTime_0" + str(i)))
				self.questLastCountList.append(self.GetChild("Quest_LastCount_0" + str(i)))

		if app.USE_BONUS_PAGE:
			self.MainBoard = self.GetChild("board")

			self.expand_btn = ui.MakeButton(self.MainBoard, 240, 120, "", "d:/ymir work/ui/game/belt_inventory/", "btn_minimize_normal.tga", "btn_minimize_over.tga", "btn_minimize_down.tga")
			self.expand_btn.SetEvent(ui.__mem_func__(self.ClickExpandButton))

			self.minimize_btn = ui.MakeButton(self.MainBoard, 240, 120, "", "d:/ymir work/ui/game/belt_inventory/", "btn_expand_normal.tga", "btn_expand_over.tga", "btn_expand_down.tga")
			self.minimize_btn.SetEvent(ui.__mem_func__(self.ClickMinimizeButton))

			if app.ENABLE_CONQUEROR_LEVEL:
				self.expand_btn.OnMouseOverIn = lambda arg = localeinfo.DETAILS_TITLE : ui.__mem_func__(self.__ShowToolTip)(arg)
				self.expand_btn.OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()

				self.minimize_btn.OnMouseOverIn = lambda arg = localeinfo.DETAILS_TITLE : ui.__mem_func__(self.__ShowToolTip)(arg)
				self.minimize_btn.OnMouseOverOut = lambda : ui.__mem_func__(self.__HideToolTip)()

		if app.ENABLE_COMBAT_POINTS:
			self.__BuildCPPanel()

	def __SetSkillSlotEvent(self):# dream
		for skillPageValue in self.skillPageDict.itervalues():
			skillPageValue.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
			skillPageValue.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectSkill))
			skillPageValue.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
			skillPageValue.SetUnselectItemSlotEvent(ui.__mem_func__(self.ClickSkillSlot))
			skillPageValue.SetUseSlotEvent(ui.__mem_func__(self.ClickSkillSlot))
			skillPageValue.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
			skillPageValue.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			skillPageValue.SetPressedSlotButtonEvent(ui.__mem_func__(self.OnPressedSlotButton))
			skillPageValue.AppendSlotButton("d:/ymir work/ui/game/windows/btn_plus_up.sub",\
				"d:/ymir work/ui/game/windows/btn_plus_over.sub",\
				"d:/ymir work/ui/game/windows/btn_plus_down.sub")

	def __SetEmotionSlot(self):
		self.emotionToolTip = uitooltip.ToolTip()

		if app.ENABLE_EXPRESSING_EMOTION:
			for slot in (self.soloEmotionSlot, self.dualEmotionSlot, self.specialEmotionSlot):
				slot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
				slot.SetSelectItemSlotEvent(ui.__mem_func__(self.__SelectEmotion))
				slot.SetUnselectItemSlotEvent(ui.__mem_func__(self.__ClickEmotionSlot))
				slot.SetUseSlotEvent(ui.__mem_func__(self.__ClickEmotionSlot))
				slot.SetOverInItemEvent(ui.__mem_func__(self.__OverInEmotion))
				slot.SetOverOutItemEvent(ui.__mem_func__(self.__OverOutEmotion))
				slot.AppendSlotButton("d:/ymir work/ui/game/windows/btn_plus_up.sub",\
					"d:/ymir work/ui/game/windows/btn_plus_over.sub",\
					"d:/ymir work/ui/game/windows/btn_plus_down.sub")
		else:
			for slot in (self.soloEmotionSlot, self.dualEmotionSlot):
				slot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
				slot.SetSelectItemSlotEvent(ui.__mem_func__(self.__SelectEmotion))
				slot.SetUnselectItemSlotEvent(ui.__mem_func__(self.__ClickEmotionSlot))
				slot.SetUseSlotEvent(ui.__mem_func__(self.__ClickEmotionSlot))
				slot.SetOverInItemEvent(ui.__mem_func__(self.__OverInEmotion))
				slot.SetOverOutItemEvent(ui.__mem_func__(self.__OverOutEmotion))
				slot.AppendSlotButton("d:/ymir work/ui/game/windows/btn_plus_up.sub",\
					"d:/ymir work/ui/game/windows/btn_plus_over.sub",\
					"d:/ymir work/ui/game/windows/btn_plus_down.sub")

		for slotIdx, datadict in emotion.EMOTION_DICT.items():
			emotionIdx = slotIdx

			slot = self.soloEmotionSlot
			if app.ENABLE_EXPRESSING_EMOTION:
				if slotIdx > 50 and slotIdx < app.SPECIAL_ACTION_START_INDEX:
					slot = self.dualEmotionSlot

				if slotIdx >= app.SPECIAL_ACTION_START_INDEX:
					slot = self.specialEmotionSlot
			else:
				if slotIdx > 50:
					slot = self.dualEmotionSlot

			slot.SetEmotionSlot(slotIdx, emotionIdx)
			slot.SetCoverButton(slotIdx)

	def __SelectEmotion(self, slotIndex):
		if not slotIndex in emotion.EMOTION_DICT:
			return

		if app.IsPressed(app.DIK_LCONTROL):
			player.RequestAddToEmptyLocalQuickSlot(player.SLOT_TYPE_EMOTION, slotIndex)
			return

		mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_EMOTION, slotIndex, slotIndex)

	def __ClickEmotionSlot(self, slotIndex):
		print "click emotion"
		if not slotIndex in emotion.EMOTION_DICT:
			return

		print "check target acting"
		if player.IsActingTargetEmotion():
			return

		command = emotion.EMOTION_DICT[slotIndex]["command"]
		print "command", command

		if app.ENABLE_EXPRESSING_EMOTION:
			if slotIndex > 50 and slotIndex < app.SPECIAL_ACTION_START_INDEX:
				vid = player.GetTargetVID()

				if 0 == vid or vid == player.GetMainCharacterIndex() or chr.IsNPC(vid) or chr.IsEnemy(vid):
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.EMOTION_CHOOSE_ONE)
					return

				command += " " + chr.GetNameByVID(vid)
		else:
			if slotIndex > 50:
				vid = player.GetTargetVID()

				if 0 == vid or vid == player.GetMainCharacterIndex() or chr.IsNPC(vid) or chr.IsEnemy(vid):
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.EMOTION_CHOOSE_ONE)
					return

				command += " " + chr.GetNameByVID(vid)

		print "send_command", command
		net.SendChatPacket(command)

	def ActEmotion(self, emotionIndex):
		self.__ClickEmotionSlot(emotionIndex)

	def __OverInEmotion(self, slotIndex):
		if self.emotionToolTip:

			if not slotIndex in emotion.EMOTION_DICT:
				return

			self.emotionToolTip.ClearToolTip()
			self.emotionToolTip.SetTitle(emotion.EMOTION_DICT[slotIndex]["name"])
			if app.ENABLE_EXPRESSING_EMOTION:
				if slotIndex >= app.SPECIAL_ACTION_START_INDEX:
					self.emotionToolTip.AppendLastTime(emotion.EMOTION_DICT[slotIndex]["time"])
			self.emotionToolTip.AlignHorizonalCenter()
			self.emotionToolTip.ShowToolTip()

	def __OverOutEmotion(self):
		if self.emotionToolTip:
			self.emotionToolTip.HideToolTip()

	def __BindEvent(self):
		if app.ENABLE_SOLO_LEADERSHIP_BONUS:
			try:
				self.leadershipOpenButton = self.GetChild("leadership_button")
				self.leadershipOpenButton.SetEvent(ui.__mem_func__(self.ToggleLeadershipBoard))
				self.leadershipOpenButton.SetToolTipText(localeinfo.SOLO_LEADERSHIP_TITLE, 0, -16)
			except:
				self.leadershipOpenButton = None

		for i in xrange(len(self.skillGroupButton)):
			self.skillGroupButton[i].SetEvent(ui.__mem_func__(self.__SelectSkillGroup),i)

		self.RefreshQuest()
		self.__HideJobToolTip()

		for (tabKey, tabButton) in self.tabButtonDict.items():
			tabButton.SetEvent(ui.__mem_func__(self.__OnClickTabButton), tabKey)

		if app.ENABLE_CONQUEROR_LEVEL:
			for (tabKey, tabButton) in self.tabLevelInfoButtonDict.items():
				tabButton.SetEvent(ui.__mem_func__(self.__ChangeLevelInfoButton), tabKey)

			for (statusPlusKey, statusPlusButton) in self.statusConquerorPlusButtonDict.items():
				statusPlusButton.SAFE_SetEvent(self.__OnClickConquerorStatusPlusButton, statusPlusKey)
				statusPlusButton.ShowToolTip = lambda arg = statusPlusKey: self.__OverInStatButton(arg)
				statusPlusButton.HideToolTip = lambda arg = statusPlusKey: self.__OverOutStatButton()

		for (statusPlusKey, statusPlusButton) in self.statusPlusButtonDict.items():
			statusPlusButton.SAFE_SetEvent(self.__OnClickStatusPlusButton, statusPlusKey)
			statusPlusButton.SetShowToolTipEvent(ui.__mem_func__(self.__OverInStatButton), statusPlusKey)
			statusPlusButton.SetHideToolTipEvent(ui.__mem_func__(self.__OverOutStatButton), statusPlusKey)

		for (statusMinusKey, statusMinusButton) in self.statusMinusButtonDict.items():
			statusMinusButton.SAFE_SetEvent(self.__OnClickStatusMinusButton, statusMinusKey)
			statusMinusButton.SetShowToolTipEvent(ui.__mem_func__(self.__OverInStatMinusButton), statusMinusKey)
			statusMinusButton.SetHideToolTipEvent(ui.__mem_func__(self.__OverOutStatMinusButton), statusMinusKey)

		for titleBarValue in self.titleBarDict.itervalues():
			titleBarValue.SetCloseEvent(ui.__mem_func__(self.Hide))

		if app.ENABLE_QUEST_RENEWAL:
			self.questTitleBar.SetCloseEvent(ui.__mem_func__(self.Close))
			self.questScrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScrollQuest))

			for i in xrange(quest.QUEST_CATEGORY_MAX_NUM):
				self.questCategoryList[i].SetEvent(ui.__mem_func__(self.__OnClickQuestCategoryButton), i)
		else:
			self.questSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.__SelectQuest))

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			if localeinfo.IsARABIC():
				self.__LoadScript("uiscript/ae_CharacterWindow.py")
			else:
				self.__LoadScript("uiscript/CharacterWindow.py")

			self.__BindObject()
			self.__BindEvent()
		except:
			import exception
			exception.Abort("CharacterWindow.__LoadWindow")

		# self.tabButtonDict["EMOTICON"].Disable()
		self.SetState("STATUS")
		if app.ENABLE_CONQUEROR_LEVEL:
			self.__ChangeLevelInfoButton(player.LEVEL_TYPE_BASE)

		if app.ENABLE_SOLO_LEADERSHIP_BONUS:
			self.__LoadLeadershipBoard()

	# ------------------------------------------------------------------
	# Solo Leadership role board (ENABLE_SOLO_LEADERSHIP_BONUS)
	# ------------------------------------------------------------------
	def __LoadLeadershipBoard(self):
		self.leadershipBoard = None
		self.leadershipRoleButtons = []
		try:
			pyScrLoader = ui.PythonScriptLoader()
			board = ui.ScriptWindow()
			pyScrLoader.LoadScriptFile(board, "uiscript/leadershipboard.py")
		except:
			import exception
			exception.Abort("CharacterWindow.__LoadLeadershipBoard")
			return

		for i in xrange(6):
			btn = board.GetChild("role_button_%d" % (i + 1))
			btn.SetEvent(ui.__mem_func__(self.__OnSelectLeadershipRole), i + 1)
			btn.SetEventOverIn(ui.__mem_func__(self.__OnOverInLeadershipRole), i + 1)
			btn.SetEventOverOut(ui.__mem_func__(self.__OnOverOutLeadershipRole))
			self.leadershipRoleButtons.append(btn)

		board.Hide()
		self.leadershipBoard = board
		self.RefreshSoloLeadership()

	def __CloseLeadershipBoard(self):
		if self.leadershipBoard:
			self.leadershipBoard.Hide()

	def ToggleLeadershipBoard(self):
		if not self.leadershipBoard:
			return
		if self.leadershipBoard.IsShow():
			self.leadershipBoard.Hide()
		else:
			(x, y) = self.GetGlobalPosition()
			self.leadershipBoard.SetPosition(x, y + self.GetHeight() + 3)
			self.leadershipBoard.Show()
			self.leadershipBoard.SetTop()

	def __OnSelectLeadershipRole(self, idx):
		net.SendChatPacket("/leadership_bonus %d" % idx)
		self.__CloseLeadershipBoard()

	def RefreshSoloLeadership(self):
		if not app.ENABLE_SOLO_LEADERSHIP_BONUS:
			return
		if not getattr(self, "leadershipBoard", None):
			return

		for i in xrange(6):
			btn = self.leadershipRoleButtons[i]
			if (i + 1) == constinfo.SOLO_LEADERSHIP_ACTIVE:
				btn.Down()
			else:
				btn.SetUp()

	def __LeadershipTipLines(self, idx):
		ROLE_NAME = {
			1 : localeinfo.SOLO_LEADERSHIP_ROLE_1,
			2 : localeinfo.SOLO_LEADERSHIP_ROLE_2,
			3 : localeinfo.SOLO_LEADERSHIP_ROLE_3,
			4 : localeinfo.SOLO_LEADERSHIP_ROLE_4,
			5 : localeinfo.SOLO_LEADERSHIP_ROLE_5,
			6 : localeinfo.SOLO_LEADERSHIP_ROLE_6,
		}
		GRANT_FORMAT = {
			1 : localeinfo.SOLO_LEADERSHIP_GRANT_1,
			2 : localeinfo.SOLO_LEADERSHIP_GRANT_2,
			3 : localeinfo.SOLO_LEADERSHIP_GRANT_3,
			4 : localeinfo.SOLO_LEADERSHIP_GRANT_4,
			5 : localeinfo.SOLO_LEADERSHIP_GRANT_5,
			6 : localeinfo.SOLO_LEADERSHIP_GRANT_6,
		}
		name = ROLE_NAME[idx]
		if idx == constinfo.SOLO_LEADERSHIP_ACTIVE:
			name = "%s (%s)" % (name, localeinfo.SOLO_LEADERSHIP_ACTIVE)
		grant = GRANT_FORMAT[idx] % constinfo.SOLO_LEADERSHIP_BONUS[idx - 1]
		return (name, grant)

	def __OnOverInLeadershipRole(self, idx):
		if not self.toolTip:
			return
		(name, grant) = self.__LeadershipTipLines(idx)
		t = self.toolTip
		t.ClearToolTip()
		t.toolTipWidth = 160
		t.AutoAppendTextLine(name)
		t.AutoAppendTextLine(grant)
		t.AlignHorizonalCenter()
		t.Show()

	def __OnOverOutLeadershipRole(self):
		if self.toolTip:
			self.toolTip.HideToolTip()

	def Destroy(self):
		if app.ENABLE_CASUAL_BUFF and self.casualConfirmDialog:
			self.casualConfirmDialog.Close()
			self.casualConfirmDialog = None

		if self.alignmentWnd:
			self.alignmentWnd.Hide()
			self.alignmentWnd = None

		if app.USE_BONUS_PAGE and self.bonus_page_wnd:
			self.bonus_page_wnd.Destroy()
			del self.bonus_page_wnd
			self.bonus_page_wnd = None

		if app.ENABLE_PARTY_BOUNS:
			self.wndPartyBonusWindow = None

		if app.ENABLE_SOLO_LEADERSHIP_BONUS:
			self.leadershipRoleButtons = []
			self.leadershipBoard = None

		self.ClearDictionary()
		self.__Initialize()

	def Show(self):
		self.__LoadWindow()
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "character_window")

		if app.USE_BONUS_PAGE:
			if uicharacterdetails.bonus_page_show_status:
				if self.expand_btn:
					self.expand_btn.Hide()

				if self.minimize_btn:
					self.minimize_btn.Show()
			else:
				if self.minimize_btn:
					self.minimize_btn.Hide()

				if self.expand_btn:
					self.expand_btn.Show()

			if uicharacterdetails.bonus_page_show_status:
				if not self.bonus_page_wnd:
					self.bonus_page_wnd = uicharacterdetails.CharacterDetailsUI()
					self.bonus_page_wnd.SetMainParent(self)

				(x, y) = self.GetGlobalPosition()
				self.bonus_page_wnd.AdjustPosition(x + self.GetWidth() + 1, y)
				self.bonus_page_wnd.Open()

		if app.ENABLE_COMBAT_POINTS and self.cpBaseBoard:
			self.__UpdateCPPanelPosition()
			if self.cpPanelVisible:
				self.cpBaseBoard.Show()
				self.cpCollapseBtn.Show()
				self.cpExpandBtn.Hide()
			else:
				self.cpBaseBoard.Hide()
				self.cpCollapseBtn.Hide()
				self.cpExpandBtn.Show()
			self.__RefreshCPValues()

		ui.ScriptWindow.Show(self)

		if app.__BL_MOUSE_WHEEL_TOP_WINDOW__:
			wndMgr.SetWheelTopWindow(self.hWnd)

	def Hide(self, _from_interface = False):
		if self.toolTipSkill:
			self.toolTipSkill.Hide()

		if app.ENABLE_COMBAT_POINTS and hasattr(self, 'cpBaseBoard') and self.cpBaseBoard:
			self.cpBaseBoard.Hide()
			if self.cpCollapseBtn:
				self.cpCollapseBtn.Hide()
			if self.cpExpandBtn:
				self.cpExpandBtn.Hide()

		if app.USE_BONUS_PAGE and self.bonus_page_wnd:
			if not _from_interface:
				uicharacterdetails.bonus_page_show_status = self.bonus_page_wnd.IsShow()

			self.bonus_page_wnd.Hide()

		if app.ENABLE_SKILL_COLOR_SYSTEM:
			if self.skillColorWnd and self.skillColorWnd.IsShow():
				self.skillColorWnd.Close()

		if getattr(self, "alignmentWnd", None):
			self.alignmentWnd.Hide()

		if app.ENABLE_SOLO_LEADERSHIP_BONUS and getattr(self, "leadershipBoard", None):
			self.leadershipBoard.Hide()   # standalone float -> not auto-hidden with the parent window

		ui.ScriptWindow.Hide(self)

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "character_window")

		if self.toolTipSkill:
			self.toolTipSkill.Hide()

		if app.ENABLE_PARTY_BOUNS and self.wndPartyBonusWindow:
			self.wndPartyBonusWindow.Close()

		if app.ENABLE_COMBAT_POINTS and hasattr(self, 'cpBaseBoard') and self.cpBaseBoard:
			self.cpBaseBoard.Hide()
			if self.cpCollapseBtn:
				self.cpCollapseBtn.Hide()
			if self.cpExpandBtn:
				self.cpExpandBtn.Hide()

		if app.USE_BONUS_PAGE and self.bonus_page_wnd:
			self.bonus_page_wnd.Hide()

		if app.ENABLE_SKILL_COLOR_SYSTEM:
			if self.skillColorWnd and\
				self.skillColorWnd.IsShow():
				self.skillColorWnd.Hide()

		if getattr(self, "alignmentWnd", None):
			self.alignmentWnd.Hide()

		if app.ENABLE_SOLO_LEADERSHIP_BONUS and getattr(self, "leadershipBoard", None):
			self.leadershipBoard.Hide()

		ui.ScriptWindow.Hide(self)

		if app.__BL_MOUSE_WHEEL_TOP_WINDOW__:
			wndMgr.ClearWheelTopWindow()


	def SetSkillToolTip(self, toolTipSkill):
		self.toolTipSkill = toolTipSkill

	# def __OnClickStatusPlusButton(self, statusKey):
		# try:
			# statusPlusCommand=self.statusPlusCommandDict[statusKey]
			# net.SendChatPacket(statusPlusCommand)
		# except KeyError, msg:
			# dbg.TraceError("CharacterWindow.__OnClickStatusPlusButton KeyError: %s", msg)

	def __OnClickStatusPlusButton(self, statusKey):
		cmd = self.statusPlusCommandDict[statusKey]

		if app.IsPressed(app.DIK_LCONTROL):
			cmd = cmd + "10"
		else:
			cmd = cmd + "1"
			
		net.SendChatPacket(cmd)

	def __OnClickStatusMinusButton(self, statusKey):
		try:
			statusMinusCommand=self.statusMinusCommandDict[statusKey]
			if app.IsPressed(app.DIK_LCONTROL):
				statusMinusCommand += " 10"
			else:
				statusMinusCommand += " 1"
			net.SendChatPacket(statusMinusCommand)
		except KeyError, msg:
			dbg.TraceError("CharacterWindow.__OnClickStatusMinusButton KeyError: %s", msg)


	if app.ENABLE_CONQUEROR_LEVEL:
		def __OnClickConquerorStatusPlusButton(self, statusKey):
			try:
				statusConquerorPlusCommand = self.statusConquerorPlusCommandDict[statusKey]
				net.SendChatPacket(statusConquerorPlusCommand)
			except KeyError, msg:
				dbg.TraceError("CharacterWindow.__OnClickConquerorStatusPlusButton KeyError: %s", msg)

	def __OnClickTabButton(self, stateKey):
		self.SetState(stateKey)

	if app.ENABLE_CONQUEROR_LEVEL:
		def __ChangeLevelInfoButton(self, key):
			self.levelType = key

			for (tabKey, tabButton) in self.tabLevelInfoButtonDict.items():
				if key != tabKey:
					tabButton.SetUp()

			self.tabLevelInfoButtonDict[key].Down()

			for tabPage in self.tabLevelInfoPageDict.itervalues():
				tabPage.Hide()

			self.tabLevelInfoPageDict[key].Show()

			self.RefreshStatus()

	def SetState(self, stateKey):
		self.state = stateKey

		if app.ENABLE_QUEST_RENEWAL:
			if stateKey != "QUEST":
				self.questPage.Hide()
			else:
				self.__LoadQuestCategory()

		for (tabKey, tabButton) in self.tabButtonDict.items():
			if stateKey!=tabKey:
				tabButton.SetUp()

		for tabValue in self.tabDict.itervalues():
			tabValue.Hide()

		for pageValue in self.pageDict.itervalues():
			pageValue.Hide()

		for titleBarValue in self.titleBarDict.itervalues():
			titleBarValue.Hide()

		self.titleBarDict[stateKey].Show()
		self.tabDict[stateKey].Show()
		self.pageDict[stateKey].Show()

		if app.ENABLE_CASUAL_BUFF and stateKey == "CASUAL":
			# pull side of the server's notification policy: fresh state is
			# requested every time the page is opened (cross-core counters)
			net.SendCasualBuffPacket(net.CASUAL_REQ_INFO)

		if app.ENABLE_PARTY_BOUNS and self.wndPartyBonusWindow:
			if stateKey == "SKILL":
				x, y = self.GetGlobalPosition()
				self.wndPartyBonusWindow.AdjustPosition(x, y + 410)
				self.wndPartyBonusWindow.Open()
			else:
				self.wndPartyBonusWindow.Close()

	def GetState(self):
		return self.state

	if app.ENABLE_CASUAL_BUFF:
		# Server pushes arrive via the binary GC packet:
		# game.py OnCasualBuff* -> interfacemodule -> here.
		def OnCasualBuffInfo(self, active, chaosAllowed, stonesToday, stoneLimit, chaosLeft, chaosMax, secsToMidnight, shardVnums, chaosVnums):
			self.casualInfo = (active, chaosAllowed, stonesToday, stoneLimit, chaosLeft, chaosMax, secsToMidnight)
			self.casualShardVnums = shardVnums
			self.casualChaosVnums = chaosVnums
			# anchor the ticking countdown on the client clock
			self.casualMidnightAt = app.GetTime() + secsToMidnight
			self.casualShownSecond = -1
			self.__RefreshCasualPage()

		def OnCasualBuffCount(self, stonesToday, chaosLeft):
			if self.casualInfo:
				(active, chaosAllowed, _, stoneLimit, _, chaosMax, secsToMidnight) = self.casualInfo
				self.casualInfo = (active, chaosAllowed, stonesToday, stoneLimit, chaosLeft, chaosMax, secsToMidnight)
				self.__RefreshCasualPage()

		def OnCasualBuffChars(self, charList):
			self.casualChars = charList
			# if the confirm dialog is open it requested this list — feed it live
			if self.casualConfirmDialog and self.casualConfirmDialog.IsShow():
				self.casualConfirmDialog.SetCharList(charList)

		def OnCasualBuffResult(self, result):
			# OK arrives together with a fresh INFO push (page refreshes itself);
			# the failure codes get a localized chat line so the click isn't silent
			if result == net.CASUAL_RESULT_ALREADY:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CASUAL_RESULT_ALREADY_MSG)
			elif result == net.CASUAL_RESULT_LIMIT:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CASUAL_RESULT_LIMIT_MSG)
			elif result == net.CASUAL_RESULT_ERROR:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CASUAL_RESULT_ERROR_MSG)

		def __OnClickCasualActivate(self):
			# server-authoritative: the buff can only be turned ON; it expires
			# at midnight by itself.
			if not self.casualInfo:
				return

			(active, chaosAllowed, stonesToday, stoneLimit, chaosLeft, chaosMax, secsToMidnight) = self.casualInfo

			if active:
				return

			# already burned the daily allowance: activating buys nothing — say so
			# instead of opening the dialog (the server rejects this too)
			if stoneLimit > 0 and stonesToday >= stoneLimit:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CASUAL_RESULT_LIMIT_MSG)
				return

			if self.casualConfirmDialog is None:
				self.casualConfirmDialog = uicasualconfirm.CasualConfirmDialog()

			# pull the cross-account affected-characters list for the dialog
			net.SendCasualBuffPacket(net.CASUAL_REQ_CHAR_LIST)

			self.casualConfirmDialog.Open(
				self.casualInfo, self.casualChars,
				self.casualShardVnums, self.casualChaosVnums,
				ui.__mem_func__(self.__DoCasualActivate))

		def __DoCasualActivate(self):
			net.SendCasualBuffPacket(net.CASUAL_REQ_ACTIVATE)

		# --- rich, state-aware tooltips (palette: gold title / green gain /
		#     red warning / grey detail). Content is a snapshot at hover time. ---
		# minimal cohesive palette: gold title, off-white body, one mint accent,
		# amber only for the cap, muted grey detail, soft red only for inactive
		CASUAL_TIP_GOLD  = 0xFFE8B84B   # title
		CASUAL_TIP_GREEN = 0xFF8FD9B0   # the single accent (benefits, pool, active)
		CASUAL_TIP_RED   = 0xFFD98C86   # inactive only (soft)
		CASUAL_TIP_GREY  = 0xFF9AA0A8   # detail / counts / notes (muted)
		CASUAL_TIP_WHITE = 0xFFE6E8EA   # description (off-white)
		CASUAL_TIP_AMBER = 0xFFE6A94D   # the daily stone cap (important, neutral)

		def __CasualRemainStr(self):
			rem = max(0, int(self.casualMidnightAt - app.GetTime()))
			return (rem / 3600, (rem % 3600) / 60, rem % 60)

		def __CasualTipBegin(self):
			# self.toolTip is SHARED with tab/stat hovers. ClearToolTip resets the
			# height but NOT the width, and AutoAppendTextLine only ever grows it —
			# so without this reset each tooltip inherits the widest width any
			# previous hover left behind (the random big/small width bug).
			if not self.toolTip:
				return None
			# ClearToolTip empties the python child list but does NOT hide the
			# embedded icon C++ child — hide it ourselves so it can't linger on the
			# next (possibly non-casual) tooltip
			self.__CasualTipDropIcon()
			t = self.toolTip
			t.ClearToolTip()
			t.toolTipWidth = 160   # base; AutoAppendTextLine grows it to fit content
			return t

		def __CasualTipEnd(self, t):
			# re-center every line in the FINAL width (lines were positioned at the
			# width-at-append-time, which desyncs once a later line widens it) and
			# resize the board to match
			t.AlignHorizonalCenter()
			t.Show()

		def __CasualTipDropIcon(self):
			self.casualTipShown = False
			for w in (self.casualTipIcon, self.casualTipName, self.casualTipSlot):
				if w:
					w.Hide()
			self.casualTipIcon = None
			self.casualTipName = None
			self.casualTipSlot = None
			self.casualTipSlotRect = None

		def __CasualTipAddCyclingIcon(self, vnums):
			# framed slot + item icon + item name under the text, rotating through
			# `vnums` (advanced from OnUpdate -> __CasualTipCycle while shown).
			t = self.toolTip
			if not t or not vnums:
				return
			self.casualTipVnums = list(vnums)
			self.casualTipIdx = 0
			SLOT = 40

			# name line — measure the WIDEST name up front so the box is pre-sized
			# and the cycle never has to re-widen it
			name = ui.TextLine()
			name.SetParent(t)
			name.SetHorizontalAlignCenter()
			name.SetPackedFontColor(self.CASUAL_TIP_GOLD)
			maxNameW = 0
			for v in self.casualTipVnums:
				item.SelectItem(v)
				name.SetText(item.GetItemName())
				(w, h) = name.GetTextSize()
				if w > maxNameW:
					maxNameW = w

			need = max(SLOT, maxNameW) + 24
			if t.toolTipWidth < need:
				t.toolTipWidth = need

			t.AppendSpace(6)
			slotY = t.toolTipHeight
			slotX = (t.toolTipWidth - SLOT) / 2

			slot = ui.OutlineWindow()
			slot.SetParent(t)
			slot.MakeOutlineWindow(SLOT, SLOT)
			slot.SetPosition(slotX, slotY)
			slot.AddFlag("not_pick")
			slot.Show()
			t.childrenList.append(slot)

			item.SelectItem(self.casualTipVnums[0])
			icon = ui.ImageBox()
			icon.SetParent(t)
			icon.AddFlag("not_pick")
			path = item.GetIconImageFileName()
			if path:
				icon.LoadImage(path)
			iw = icon.GetWidth() or 32
			ih = icon.GetHeight() or 32
			icon.SetPosition(slotX + (SLOT - iw) / 2, slotY + (SLOT - ih) / 2)
			icon.Show()
			t.childrenList.append(icon)

			nameY = slotY + SLOT + 4
			name.SetText(item.GetItemName())
			name.SetPosition(t.toolTipWidth / 2, nameY)
			name.Show()
			t.childrenList.append(name)

			t.toolTipHeight = nameY + 18
			t.ResizeToolTip()

			self.casualTipSlot = slot
			self.casualTipIcon = icon
			self.casualTipName = name
			self.casualTipSlotRect = (slotX, slotY, SLOT, SLOT)
			self.casualTipShown = True
			self.casualTipNext = app.GetTime() + 1.0

		def __CasualTipCycle(self):
			if not (self.casualTipShown and self.casualTipIcon and len(self.casualTipVnums) > 1):
				return
			now = app.GetTime()
			if now < self.casualTipNext:
				return
			self.casualTipNext = now + 1.0
			self.casualTipIdx = (self.casualTipIdx + 1) % len(self.casualTipVnums)
			item.SelectItem(self.casualTipVnums[self.casualTipIdx])
			path = item.GetIconImageFileName()
			if path:
				self.casualTipIcon.LoadImage(path)
			if self.casualTipSlotRect:
				(sx, sy, sw, sh) = self.casualTipSlotRect
				iw = self.casualTipIcon.GetWidth() or 32
				ih = self.casualTipIcon.GetHeight() or 32
				self.casualTipIcon.SetPosition(sx + (sw - iw) / 2, sy + (sh - ih) / 2)
			if self.casualTipName:
				self.casualTipName.SetText(item.GetItemName())   # center-aligned, re-centers itself

		def __ShowCasualBuffTip(self):
			t = self.__CasualTipBegin()
			if not t:
				return
			t.AutoAppendTextLine(localeinfo.CASUAL_TIP_BUFF_TITLE, self.CASUAL_TIP_GOLD)
			t.AutoAppendTextLine(localeinfo.CASUAL_TIP_BUFF_DESC, self.CASUAL_TIP_WHITE)
			t.AppendSpace(4)
			t.AutoAppendTextLine(localeinfo.CASUAL_TIP_BUFF_CD, self.CASUAL_TIP_GREEN)
			t.AutoAppendTextLine(localeinfo.CASUAL_TIP_BUFF_DAILY, self.CASUAL_TIP_GREEN)
			t.AutoAppendTextLine(localeinfo.CASUAL_TIP_BUFF_SHARD, self.CASUAL_TIP_GREEN)
			if self.casualInfo:
				(active, ca, st, sl, cl, cm, secs) = self.casualInfo
				if sl > 0:
					# the daily stone cap is the load-bearing rule: it applies to
					# EVERY player all day, buff or not — stones broken before you
					# enable still count, and past the cap stones drop nothing
					t.AppendSpace(4)
					t.AutoAppendTextLine(localeinfo.CASUAL_TIP_LIMIT % sl, self.CASUAL_TIP_AMBER)
					t.AutoAppendTextLine(localeinfo.CASUAL_TIP_LIMIT_BOTH, self.CASUAL_TIP_GREY)
					t.AutoAppendTextLine(localeinfo.CASUAL_TIP_BUFF_STONES % (st, sl), self.CASUAL_TIP_GREY)
				else:
					t.AutoAppendTextLine(localeinfo.CASUAL_TIP_BUFF_STONES_NOLIMIT % st, self.CASUAL_TIP_GREY)
				t.AppendSpace(4)
				if active:
					t.AutoAppendTextLine(localeinfo.CASUAL_TIP_STATUS_ACTIVE % self.__CasualRemainStr(), self.CASUAL_TIP_GREEN)
				else:
					t.AutoAppendTextLine(localeinfo.CASUAL_TIP_STATUS_INACTIVE, self.CASUAL_TIP_RED)
			self.__CasualTipEnd(t)

		def __ShowCasualChaosTip(self):
			t = self.__CasualTipBegin()
			if not t:
				return
			t.AutoAppendTextLine(localeinfo.CASUAL_TIP_CHAOS_TITLE, self.CASUAL_TIP_GOLD)
			t.AutoAppendTextLine(localeinfo.CASUAL_TIP_CHAOS_DESC, self.CASUAL_TIP_WHITE)
			t.AppendSpace(4)
			if self.casualInfo:
				(active, ca, st, sl, cl, cm, secs) = self.casualInfo
				t.AutoAppendTextLine(localeinfo.CASUAL_TIP_CHAOS_POOL % (cl, cm), self.CASUAL_TIP_GREEN)
			t.AutoAppendTextLine(localeinfo.CASUAL_TIP_CHAOS_SLOTS, self.CASUAL_TIP_GREY)
			t.AutoAppendTextLine(localeinfo.CASUAL_TIP_CHAOS_FIRST, self.CASUAL_TIP_GREY)
			if self.casualInfo:
				(active, ca, st, sl, cl, cm, secs) = self.casualInfo
				t.AppendSpace(4)
				# infer the eligibility reason from the state we have
				if not active:
					t.AutoAppendTextLine(localeinfo.CASUAL_TIP_CHAOS_NEEDBUFF, self.CASUAL_TIP_RED)
				elif cl <= 0:
					t.AutoAppendTextLine(localeinfo.CASUAL_TIP_CHAOS_EMPTY, self.CASUAL_TIP_RED)
				elif ca:
					t.AutoAppendTextLine(localeinfo.CASUAL_TIP_CHAOS_OK, self.CASUAL_TIP_GREEN)
				else:
					t.AutoAppendTextLine(localeinfo.CASUAL_TIP_CHAOS_NOTELIG, self.CASUAL_TIP_RED)
			# add the slot/icon/name first (it finalizes the width), then re-center
			# only the TEXT lines — AlignTextLineHorizonalCenter leaves the slot and
			# icon ImageBoxes at their manually-centered positions
			self.__CasualTipAddCyclingIcon(self.casualChaosVnums)
			t.AlignTextLineHorizonalCenter()
			t.Show()

		def __ShowCasualActivateTip(self):
			t = self.__CasualTipBegin()
			if not t:
				return
			# concise: the full cap explanation lives on the (?) button so this
			# big-icon tooltip stays small
			info = self.casualInfo
			if info and info[0]:
				(active, ca, st, sl, cl, cm, secs) = info
				t.AutoAppendTextLine(localeinfo.CASUAL_TIP_ACT_ACTIVE % self.__CasualRemainStr(), self.CASUAL_TIP_GREEN)
				if sl > 0:
					t.AutoAppendTextLine(localeinfo.CASUAL_TIP_ACT_STONES_LEFT % max(0, sl - st), self.CASUAL_TIP_GREY)
			else:
				t.AutoAppendTextLine(localeinfo.CASUAL_TIP_ACT_ENABLE, self.CASUAL_TIP_WHITE)
				t.AutoAppendTextLine(localeinfo.CASUAL_TIP_ACT_SHARE, self.CASUAL_TIP_GREY)
			self.__CasualTipEnd(t)

		def __HideCasualTip(self):
			self.__CasualTipDropIcon()
			if self.toolTip:
				self.toolTip.HideToolTip()

		def __RefreshCasualPage(self):
			if not self.casualAvailable or not self.casualStatusText:
				return

			bActive = self.casualInfo and self.casualInfo[0]

			## activation icon swaps to the "on" art while the buff runs
			if self.casualActivateButton:
				iWantActive = 1 if bActive else 0
				if iWantActive != self.casualShownActive:
					self.casualShownActive = iWantActive
					if iWantActive:
						self.casualActivateButton.SetUpVisual("d:/ymir work/ui/casual_buff/casual_on_normal.png")
						self.casualActivateButton.SetOverVisual("d:/ymir work/ui/casual_buff/casual_on_hover.png")
						self.casualActivateButton.SetDownVisual("d:/ymir work/ui/casual_buff/casual_on_hover.png")
					else:
						self.casualActivateButton.SetUpVisual("d:/ymir work/ui/casual_buff/casual_off_normal.png")
						self.casualActivateButton.SetOverVisual("d:/ymir work/ui/casual_buff/casual_off_hover.png")
						self.casualActivateButton.SetDownVisual("d:/ymir work/ui/casual_buff/casual_off_hover.png")

			## upper section: activation status / daily stones left
			if bActive:
				(active, chaosAllowed, stonesToday, stoneLimit, chaosLeft, chaosMax, secsToMidnight) = self.casualInfo
				iStonesLeft = max(0, stoneLimit - stonesToday)
				self.casualStatusText.SetText(localeinfo.CASUAL_STONES_LEFT % iStonesLeft)
				self.casualStatusText.SetFontColor(0.78, 0.78, 0.78)
			else:
				self.casualStatusText.SetText(localeinfo.CASUAL_STATUS_DISABLED)
				self.casualStatusText.SetFontColor(1.0, 0.2, 0.2)

			if self.casualTimeText:
				if bActive:
					self.__UpdateCasualClock(True)
				else:
					self.casualTimeText.SetText("")

			## lower section: Blessing of Chaos — three states:
			##  buff off            -> "Requires Active Casual Buff" (red)
			##  on + eligible       -> "Guaranteed Frags: left / max" (green)
			##  on but not eligible -> "Blessing of Chaos Inactive" (red)
			##  (eligible = slot + multi-farm drops on + not blocked + pool > 0,
			##   all folded into chaosAllowed by the server)
			if not self.casualChaosStatusText:
				return

			bChaosRunning = bActive and self.casualInfo[1] and self.casualInfo[4] > 0

			## line 1: state, line 2: frags progress (only while running)
			if not bActive:
				self.casualChaosStatusText.SetText(localeinfo.CASUAL_CHAOS_REQUIRES)
				self.casualChaosStatusText.SetFontColor(1.0, 0.2, 0.2)
			elif bChaosRunning:
				self.casualChaosStatusText.SetText(localeinfo.CASUAL_CHAOS_ENABLED)
				self.casualChaosStatusText.SetFontColor(0.3, 1.0, 0.3)
			else:
				self.casualChaosStatusText.SetText(localeinfo.CASUAL_CHAOS_INACTIVE)
				self.casualChaosStatusText.SetFontColor(1.0, 0.2, 0.2)

			if self.casualChaosProgressText:
				if bChaosRunning:
					self.casualChaosProgressText.SetText(localeinfo.CASUAL_CHAOS_LEFT % (self.casualInfo[4], self.casualInfo[5]))
					self.casualChaosProgressText.SetFontColor(0.78, 0.78, 0.78)
				else:
					self.casualChaosProgressText.SetText("")

			## chaos icon glows while fragments remain
			if self.casualChaosImage:
				iWantChaos = 1 if bChaosRunning else 0
				if iWantChaos != self.casualShownChaosActive:
					self.casualShownChaosActive = iWantChaos
					if iWantChaos:
						self.casualChaosImage.LoadImage("d:/ymir work/ui/casual_buff/chaos_image_active.png")
					else:
						self.casualChaosImage.LoadImage("d:/ymir work/ui/casual_buff/chaos_image.png")

		def __UpdateCasualClock(self, bForce = False):
			# per-frame from OnUpdate while the page shows; renders at most
			# once per second (casualShownSecond guard)
			if not self.casualAvailable or not self.casualTimeText:
				return

			if not (self.casualInfo and self.casualInfo[0]):
				return

			if not bForce and self.GetState() != "CASUAL":
				return

			iRemain = int(self.casualMidnightAt - app.GetTime())
			if iRemain < 0:
				iRemain = 0

			if iRemain == self.casualShownSecond:
				return

			self.casualShownSecond = iRemain
			self.casualTimeText.SetText(localeinfo.CASUAL_TIME_LEFT % (iRemain / 3600, (iRemain % 3600) / 60, iRemain % 60))
			self.casualTimeText.SetFontColor(0.78, 0.78, 0.78)

	def OnRunMouseWheel(self, nLen):
		if app.ENABLE_INGAME_WIKI:
			if not self.IsInPosition():
				return False
		else:
			if not self.IsIn():
				return False

		# CASUAL sits between SKILL and EMOTICON when the 5-tab script is loaded
		casualInChain = app.ENABLE_CASUAL_BUFF and self.casualAvailable

		if nLen > 0:
			if self.GetState() == "QUEST" and self.questScrollBar and self.questScrollBar.IsShow():
				self.questScrollBar.OnUp()
			else:
				if self.GetState() == "STATUS":
					self.SetState("SKILL")
				elif self.GetState() == "SKILL":
					if casualInChain:
						self.SetState("CASUAL")
					else:
						self.SetState("EMOTICON")
				elif self.GetState() == "CASUAL":
					self.SetState("EMOTICON")
				elif self.GetState() == "EMOTICON":
					self.SetState("QUEST")

			return True
		else:
			if self.GetState() == "QUEST" and self.questScrollBar and self.questScrollBar.IsShow():
				self.questScrollBar.OnDown()
			else:
				if self.GetState() == "SKILL":
					self.SetState("STATUS")
				elif self.GetState() == "CASUAL":
					self.SetState("SKILL")
				elif self.GetState() == "EMOTICON":
					if casualInChain:
						self.SetState("CASUAL")
					else:
						self.SetState("SKILL")
				elif self.GetState() == "QUEST":
					self.SetState("EMOTICON")

			return True

		return False

	# if app.__BL_MOUSE_WHEEL_TOP_WINDOW__:
		# def OnMouseWheelButtonUp(self):
			# if self.GetState() == "STATUS":
				# self.SetState("SKILL")
			# elif self.GetState() == "SKILL":
				# self.SetState("EMOTICON")
			# elif self.GetState() == "EMOTICON":
				# self.SetState("QUEST")
			# if self.ScrollBar:
				# self.ScrollBar.OnUp()
				# return True

			# return False

		# def OnMouseWheelButtonDown(self):
			# if self.GetState() == "SKILL":
				# self.SetState("STATUS")
			# elif self.GetState() == "EMOTICON":
				# self.SetState("SKILL")
			# elif self.GetState() == "QUEST":
				# self.SetState("EMOTICON")
			# if self.ScrollBar:
				# self.ScrollBar.OnDown()
				# return True

			# return False

	def __GetTotalAtkText(self):
		minAtk=player.GetStatus(player.ATT_MIN)
		maxAtk=player.GetStatus(player.ATT_MAX)
		atkBonus=player.GetStatus(player.ATT_BONUS)
		attackerBonus=player.GetStatus(player.ATTACKER_BONUS)

		#if player.IsPoly():
		#	atkBonus = 0

		if minAtk==maxAtk:
			return "%d" % (minAtk+atkBonus+attackerBonus)
		else:
			return "%d-%d" % (minAtk+atkBonus+attackerBonus, maxAtk+atkBonus+attackerBonus)

	def __GetTotalMagAtkText(self):
		minMagAtk=player.GetStatus(player.MAG_ATT)+player.GetStatus(player.MIN_MAGIC_WEP)
		maxMagAtk=player.GetStatus(player.MAG_ATT)+player.GetStatus(player.MAX_MAGIC_WEP)

		if minMagAtk==maxMagAtk:
			return "%d" % (minMagAtk)
		else:
			return "%d-%d" % (minMagAtk, maxMagAtk)

	def __GetTotalDefText(self):
		defValue=player.GetStatus(player.DEF_GRADE)
		if constinfo.ADD_DEF_BONUS_ENABLE:
			defValue+=player.GetStatus(player.DEF_BONUS)
		return "%d" % (defValue)

	if app.ENABLE_CONQUEROR_LEVEL:
		def __GetSungMaPointValuePer(self, point_type, percent_point_type):
			pass

	def RefreshStatus(self):
		if self.isLoaded == 0:
			return

		try:
			if app.ENABLE_CONQUEROR_LEVEL:
				if self.levelType == player.LEVEL_TYPE_CONQUEROR:
					self.GetChild("Level_Value").SetText(str(player.GetStatus(player.POINT_CONQUEROR_LEVEL)))
					self.GetChild("Exp_Value").SetText(str(unsigned32(player.GetStatus(player.POINT_CONQUEROR_EXP))))
					self.GetChild("RestExp_Value").SetText(str(unsigned32(player.GetStatus(player.POINT_CONQUEROR_NEXT_EXP)) - unsigned32(player.GetStatus(player.POINT_CONQUEROR_EXP))))
				else:
					self.GetChild("Level_Value").SetText(str(player.GetStatus(player.LEVEL)))
					self.GetChild("Exp_Value").SetText(str(unsigned32(player.GetEXP())))
					self.GetChild("RestExp_Value").SetText(str(unsigned32(player.GetStatus(player.NEXT_EXP)) - unsigned32(player.GetStatus(player.EXP))))
			else:
				self.GetChild("Level_Value").SetText(str(player.GetStatus(player.LEVEL)))
				self.GetChild("Exp_Value").SetText(str(unsigned32(player.GetEXP())))
				self.GetChild("RestExp_Value").SetText(str(unsigned32(player.GetStatus(player.NEXT_EXP)) - unsigned32(player.GetStatus(player.EXP))))
			self.GetChild("HP_Value").SetText(str(player.GetStatus(player.HP)) + "/" + str(player.GetStatus(player.MAX_HP)))
			self.GetChild("SP_Value").SetText(str(player.GetStatus(player.SP)) + "/" + str(player.GetStatus(player.MAX_SP)))

			self.GetChild("STR_Value").SetText(str(player.GetStatus(player.ST)))
			self.GetChild("DEX_Value").SetText(str(player.GetStatus(player.DX)))
			self.GetChild("HTH_Value").SetText(str(player.GetStatus(player.HT)))
			self.GetChild("INT_Value").SetText(str(player.GetStatus(player.IQ)))

			self.GetChild("ATT_Value").SetText(self.__GetTotalAtkText())
			self.GetChild("DEF_Value").SetText(self.__GetTotalDefText())

			self.GetChild("MATT_Value").SetText(self.__GetTotalMagAtkText())
			# self.GetChild("MATT_Value").SetText(str(player.GetStatus(player.MAG_ATT)))

			self.GetChild("MDEF_Value").SetText(str(player.GetStatus(player.MAG_DEF)))
			self.GetChild("ASPD_Value").SetText(str(player.GetStatus(player.ATT_SPEED)))
			self.GetChild("MSPD_Value").SetText(str(player.GetStatus(player.MOVING_SPEED)))
			self.GetChild("CSPD_Value").SetText(str(player.GetStatus(player.CASTING_SPEED)))
			self.GetChild("ER_Value").SetText(str(player.GetStatus(player.EVADE_RATE)))

			if app.ENABLE_CONQUEROR_LEVEL:
				self.GetChild("sungma_str_value").SetText(str(player.GetStatus(player.POINT_SUNGMA_STR)))
				self.GetChild("sungma_hp_value").SetText(str(player.GetStatus(player.POINT_SUNGMA_HP)))
				self.GetChild("sungma_move_value").SetText(str(player.GetStatus(player.POINT_SUNGMA_MOVE)))
				self.GetChild("sungma_immune_value").SetText(str(player.GetStatus(player.POINT_SUNGMA_IMMUNE)))
				self.GetChild("sungma_str_value").SetText(str(player.GetStatus(player.POINT_SUNGMA_STR)))
				self.GetChild("sungma_hp_value").SetText(str(player.GetStatus(player.POINT_SUNGMA_HP)))
				self.GetChild("sungma_move_value").SetText(str(player.GetStatus(player.POINT_SUNGMA_MOVE)))
				self.GetChild("sungma_immune_value").SetText(str(player.GetStatus(player.POINT_SUNGMA_IMMUNE)))
		except:
			# import exception
			# exception.Abort("CharacterWindow.RefreshStatus.BindObject")
			pass

		self.__RefreshStatusPlusButtonList()
		self.__RefreshStatusMinusButtonList()
		self.RefreshAlignment()

		if app.ENABLE_COMBAT_POINTS:
			self.__RefreshCPValues()

		if self.refreshToolTip:
			self.refreshToolTip()

		if app.USE_BONUS_PAGE and self.bonus_page_wnd:
			self.bonus_page_wnd.RefreshStatus()

	def __RefreshStatusPlusButtonList(self):
		if self.isLoaded == 0:
			return

		if app.ENABLE_CONQUEROR_LEVEL:
			if self.levelType == player.LEVEL_TYPE_CONQUEROR:
				statusPlusPoint = player.GetStatus(player.POINT_CONQUEROR_POINT)
			else:
				statusPlusPoint = player.GetStatus(player.STAT)
		else:
			statusPlusPoint = player.GetStatus(player.STAT)

		if statusPlusPoint > 0:
			self.statusPlusValue.SetText(str(statusPlusPoint))
			if not app.ENABLE_CONQUEROR_LEVEL:
				self.statusPlusLabel.Show()
			self.ShowStatusPlusButtonList()
			if app.ENABLE_CONQUEROR_LEVEL:
				self.ShowConquerorStatusPlusButtonList()
		else:
			self.statusPlusValue.SetText(str(0))
			if not app.ENABLE_CONQUEROR_LEVEL:
				self.statusPlusLabel.Hide()
			self.HideStatusPlusButtonList()
			if app.ENABLE_CONQUEROR_LEVEL:
				self.HideConquerorStatusPlusButtonList()

		if app.ENABLE_CONQUEROR_LEVEL:
			self.statusPlusLabel.Show()

	def __RefreshStatusMinusButtonList(self):
		if self.isLoaded==0:
			return
		self.__ShowStatusMinusButtonList()

		# statusMinusPoint=self.__GetStatMinusPoint()

		# if statusMinusPoint>0:
			# self.__ShowStatusMinusButtonList()
		# else:
			# self.__HideStatusMinusButtonList()

	def RefreshAlignment(self):
		point, grade = player.GetAlignmentData()

		import colorinfo
		COLOR_DICT = {
			0 : colorinfo.TITLE_RGB_GOOD_4,
			1 : colorinfo.TITLE_RGB_GOOD_3,
			2 : colorinfo.TITLE_RGB_GOOD_2,
			3 : colorinfo.TITLE_RGB_GOOD_1,
			4 : colorinfo.TITLE_RGB_NORMAL,
			5 : colorinfo.TITLE_RGB_EVIL_1,
			6 : colorinfo.TITLE_RGB_EVIL_2,
			7 : colorinfo.TITLE_RGB_EVIL_3,
			8 : colorinfo.TITLE_RGB_EVIL_4,
		}
		colorList = COLOR_DICT.get(grade, colorinfo.TITLE_RGB_NORMAL)
		gradeColor = ui.GenerateColor(colorList[0], colorList[1], colorList[2])

		if app.ENABLE_GENDER_ALIGNMENT:
			titleName = localeinfo.GetAlignmentTitleName(point)
		else:
			titleName = localeinfo.TITLE_NAME_LIST[grade]

		thresholds = localeinfo.ALIGNMENT_GRADE_THRESHOLDS
		upperBound = thresholds[grade]
		if grade == 0:
			progressStr = localeinfo.ALIGNMENT_TOOLTIP_MAX
			nextStr = localeinfo.ALIGNMENT_TOOLTIP_MAX_RANK
		else:
			progressStr = localeinfo.ALIGNMENT_TOOLTIP_PROGRESS % (point, upperBound)
			needed = upperBound - point
			if app.ENABLE_GENDER_ALIGNMENT:
				import chr, net
				_gender = chr.RaceToSex(net.GetMainActorRace())
				_nameList = localeinfo.TITLE_NAME_DICT.get(_gender, localeinfo.TITLE_NAME_DICT[localeinfo.GENDER_MALE])
			else:
				_nameList = localeinfo.TITLE_NAME_LIST
			nextStr = localeinfo.ALIGNMENT_TOOLTIP_NEXT_GRADE % (needed, _nameList[grade - 1])

		if grade == 0 and point < 20000:
			bonusStr = localeinfo.ALIGNMENT_GRADE_BONUSES[1]
		else:
			bonusStr = localeinfo.ALIGNMENT_GRADE_BONUSES[grade]

		self.toolTipAlignment.ClearToolTip()
		self.toolTipAlignment.AutoAppendTextLine(titleName, gradeColor)
		self.toolTipAlignment.AppendHorizontalLine()
		self.toolTipAlignment.AutoAppendTextLine(bonusStr, gradeColor)
		self.toolTipAlignment.AppendHorizontalLine()
		self.toolTipAlignment.AutoAppendTextLine(localeinfo.ALIGNMENT_NAME + str(point))
		self.toolTipAlignment.AutoAppendTextLine(progressStr)
		self.toolTipAlignment.AutoAppendTextLine(nextStr)
		if grade >= 5:
			_DUNGEON_PENALTY = {5: 10, 6: 15, 7: 20, 8: 30}
			_LOOT_BUFF = {6: 15, 7: 10}
			penalty = _DUNGEON_PENALTY.get(grade, 0)
			self.toolTipAlignment.AppendHorizontalLine()
			self.toolTipAlignment.AutoAppendTextLine(localeinfo.ALIGNMENT_DUNGEON_PENALTY % penalty, ui.GenerateColor(255, 80, 80))
			if grade == 8:
				self.toolTipAlignment.AutoAppendTextLine(localeinfo.ALIGNMENT_LOOT_BUFF_DISABLED, ui.GenerateColor(255, 80, 80))
				self.toolTipAlignment.AutoAppendTextLine(localeinfo.ALIGNMENT_LOOT_DROP_ALERT , ui.GenerateColor(255, 80, 80))
			elif grade in _LOOT_BUFF:
				self.toolTipAlignment.AutoAppendTextLine(localeinfo.ALIGNMENT_LOOT_BUFF_REDUCED % _LOOT_BUFF[grade], ui.GenerateColor(255, 130, 50))
				self.toolTipAlignment.AutoAppendTextLine(localeinfo.ALIGNMENT_LOOT_DROP_ALERT , ui.GenerateColor(255, 80, 80))
		self.toolTipAlignment.AppendHorizontalLine()
		self.toolTipAlignment.AutoAppendTextLine(localeinfo.ALIGNMENT_TOOLTIP_CLICK)
		self.toolTipAlignment.AlignHorizonalCenter()

		if self.alignmentWnd and self.alignmentWnd.IsShow():
			self.alignmentWnd.Refresh()

	def __ShowStatusMinusButtonList(self):
		for (stateMinusKey, statusMinusButton) in self.statusMinusButtonDict.items():
			statusMinusButton.Show()

	def __HideStatusMinusButtonList(self):
		for (stateMinusKey, statusMinusButton) in self.statusMinusButtonDict.items():
			statusMinusButton.Hide()

	def ShowStatusPlusButtonList(self):
		for (statePlusKey, statusPlusButton) in self.statusPlusButtonDict.items():
			statusPlusButton.Show()

	def HideStatusPlusButtonList(self):
		for (statePlusKey, statusPlusButton) in self.statusPlusButtonDict.items():
			statusPlusButton.Hide()

	if app.ENABLE_CONQUEROR_LEVEL:
		def ShowConquerorStatusPlusButtonList(self):
			for (statePlusKey, statusPlusButton) in self.statusConquerorPlusButtonDict.items():
				statusPlusButton.Show()

		def HideConquerorStatusPlusButtonList(self):
			for (statePlusKey, statusPlusButton) in self.statusConquerorPlusButtonDict.items():
				statusPlusButton.Hide()
	# def SelectSkill(self, skillSlotIndex):
		# mouseController = mousemodule.mouseController

		# if False == mouseController.isAttached():
			# srcSlotIndex = self.__RealSkillSlotToSourceSlot(skillSlotIndex)
			# selectedSkillIndex = player.GetSkillIndex(srcSlotIndex)

			# if skill.CanUseSkill(selectedSkillIndex):
				# if app.IsPressed(app.DIK_LCONTROL):
					# player.RequestAddToEmptyLocalQuickSlot(player.SLOT_TYPE_SKILL, srcSlotIndex)
					# return

				# mouseController.AttachObject(self, player.SLOT_TYPE_SKILL, srcSlotIndex, selectedSkillIndex)
		# else:
			# mouseController.DeattachObject()

	def SelectSkill(self, skillSlotIndex):
		mouseController = mousemodule.mouseController
		if False == mouseController.isAttached():
			srcSlotIndex = self.__RealSkillSlotToSourceSlot(skillSlotIndex)
			selectedSkillIndex = player.GetSkillIndex(srcSlotIndex)
		
			if app.ENABLE_SOLO_LEADERSHIP_BONUS and selectedSkillIndex == SOLO_LEADERSHIP_SKILL_INDEX:
				self.ToggleLeadershipBoard()
				return
		
			if skill.CanUseSkill(selectedSkillIndex):
				if app.IsPressed(app.DIK_LCONTROL):
					player.RequestAddToEmptyLocalQuickSlot(player.SLOT_TYPE_SKILL, srcSlotIndex)
					return

				mouseController.AttachObject(self, player.SLOT_TYPE_SKILL, srcSlotIndex, selectedSkillIndex)
		else:
			mouseController.DeattachObject()


	def SelectEmptySlot(self, SlotIndex):
		mousemodule.mouseController.DeattachObject()

	if app.ENABLE_CONQUEROR_LEVEL:
		def __ShowToolTip(self, desc):
			if not self.toolTip:
				return

			descLen = len(desc)
			self.toolTip.ClearToolTip()
			self.toolTip.SetThinBoardSize(11 * descLen)
			self.toolTip.AutoAppendTextLine(desc)
			self.toolTip.AlignHorizonalCenter()
			self.toolTip.Show()

		def __HideToolTip(self):
			self.__HideStatToolTip()

		def __ShowToolTipButton(self, desc):
			self.__ShowToolTip(desc)

		def __ShowToolTipImg(self, event_type, text):
			if "mouse_over_in" == event_type :
				textLen = len(text)

				self.toolTip.ClearToolTip()
				self.toolTip.SetThinBoardSize(11 * arglen)
				# self.toolTip.SetToolTipPosition(pos_x + 50, pos_y + 50)
				self.toolTip.AppendTextLine(text, 0xffffffff)
				self.toolTip.Show()
			elif "mouse_over_out" == event_type:
				self.__HideToolTip()

		def __TogglePassiveAttrWindow(self, event_type):
			pass

		def __ToolTipProgress(self):
			pass

	## ToolTip
	def OverInItem(self, slotNumber):
		if mousemodule.mouseController.isAttached():
			return

		if 0 == self.toolTipSkill:
			return

		srcSlotIndex = self.__RealSkillSlotToSourceSlot(slotNumber)
		skillIndex = player.GetSkillIndex(srcSlotIndex)
		skillLevel = player.GetSkillLevel(srcSlotIndex)
		skillGrade = player.GetSkillGrade(srcSlotIndex)
		skillType = skill.GetSkillType(skillIndex)

		## ACTIVE
		if skill.SKILL_TYPE_ACTIVE == skillType:
			overInSkillGrade = self.__GetSkillGradeFromSlot(slotNumber)

			if overInSkillGrade == skill.SKILL_GRADE_COUNT-1 and skillGrade == skill.SKILL_GRADE_COUNT:
				self.toolTipSkill.SetSkillNew(srcSlotIndex, skillIndex, skillGrade, skillLevel)
			elif overInSkillGrade == skillGrade:
				self.toolTipSkill.SetSkillNew(srcSlotIndex, skillIndex, overInSkillGrade, skillLevel)
			else:
				self.toolTipSkill.SetSkillOnlyName(srcSlotIndex, skillIndex, overInSkillGrade)
		else:
			self.toolTipSkill.SetSkillNew(srcSlotIndex, skillIndex, skillGrade, skillLevel)
		if app.__AUTO_SKILL_READER__:
			self.toolTipSkill.AppendSpace(5)
			self.toolTipSkill.AppendShortcutRow(("key_x",), localeinfo.AUTO_SKILL_READER_OPEN)

	def OverOutItem(self):
		if self.toolTipSkill:
			self.toolTipSkill.HideToolTip()

	## Quest
	def __SelectQuest(self, slotIndex):
		if app.ENABLE_QUEST_RENEWAL:
			questIndex = self.questIndexMap[slotIndex]

			if not questIndex in self.questClicked:
				self.questClicked.append(questIndex)
		else:
			questIndex = quest.GetQuestIndex(self.questShowingStartIndex + slotIndex)

		import event
		event.QuestButtonClick(-2147483648 + questIndex)

	if app.ENABLE_EXPRESSING_EMOTION:
		def ClearSpecialEmotions(self):
			emotion.ClearSpecialEmotionIcons()
			self.__SetEmotionSlot()

		def RegisterSpecialEmotions(self, emotionIdx, leftTime):
			emotion.RegisterSpecialEmotionIcons(emotionIdx, leftTime)
			self.__SetEmotionSlot()

	def RefreshQuest(self):
		if app.ENABLE_QUEST_RENEWAL:
			if self.isLoaded == 0 or self.state != "QUEST":
				return

			for cat in self.questOpenedCategories:
				self.RefreshQuestCategory(cat)

			self.RefreshQuestCategoriesCount()
		else:
			if self.isLoaded == 0:
				return

			self.OnQuestScroll()

			questCount = quest.GetQuestCount()
			questRange = range(quest.QUEST_MAX_NUM)

			if questCount > quest.QUEST_MAX_NUM:
				self.questScrollBar.Show()
			else:
				self.questScrollBar.Hide()

			for i in questRange[:questCount]:
				(questName, questIcon, questCounterName, questCounterValue) = quest.GetQuestData(self.questShowingStartIndex + i)

				# if questName[0] == "*":
					# questName = questName[1:]

				self.questNameList[i].SetText(questName)
				self.questNameList[i].Show()
				self.questLastCountList[i].Show()
				self.questLastTimeList[i].Show()

				if len(questCounterName) > 0:
					self.questLastCountList[i].SetText("%s : %d" % (questCounterName, questCounterValue))
				else:
					self.questLastCountList[i].SetText("")

				## Icon
				self.questSlot.SetSlot(i, i, 1, 1, questIcon)

			for i in questRange[questCount:]:
				self.questNameList[i].Hide()
				self.questLastTimeList[i].Hide()
				self.questLastCountList[i].Hide()
				self.questSlot.ClearSlot(i)
				self.questSlot.HideSlotBaseImage(i)

			self.__UpdateQuestClock()

	# def OnRunMouseWheel(self, nLen):
		# if nLen > 0:
			# self.questScrollBar.OnUp()
		# else:
			# self.questScrollBar.OnDown()

	def __UpdateQuestClock(self):
		if "QUEST" == self.state:
			if app.ENABLE_QUEST_RENEWAL:
				for clock in self.questClockList:
					clockText = localeinfo.QUEST_UNLIMITED_TIME

					if clock.GetProperty("idx"):
						(lastName, lastTime) = quest.GetQuestLastTime(clock.GetProperty("idx"))

						if len(lastName) > 0:
							if lastTime <= 0:
								clockText = localeinfo.QUEST_TIMEOVER
							else:
								questLastMinute = lastTime / 60
								questLastSecond = lastTime % 60

								clockText = lastName + " : "

								if questLastMinute > 0:
									clockText += str(questLastMinute) + localeinfo.QUEST_MIN
									if questLastSecond > 0:
										clockText += " "

								if questLastSecond > 0:
									clockText += str(questLastSecond) + localeinfo.QUEST_SEC

					clock.SetText(clockText)
			else:
				# QUEST_LIMIT_COUNT_BUG_FIX
				for i in xrange(min(quest.GetQuestCount(), quest.QUEST_MAX_NUM)):
				# END_OF_QUEST_LIMIT_COUNT_BUG_FIX
					(lastName, lastTime) = quest.GetQuestLastTime(i + self.questShowingStartIndex)

					clockText = localeinfo.QUEST_UNLIMITED_TIME
					if len(lastName) > 0:

						if lastTime <= 0:
							clockText = localeinfo.QUEST_TIMEOVER
						else:
							questLastMinute = lastTime / 60
							questLastSecond = lastTime % 60

							clockText = lastName + " : "

							if questLastMinute > 0:
								clockText += str(questLastMinute) + localeinfo.QUEST_MIN
								if questLastSecond > 0:
									clockText += " "

							if questLastSecond > 0:
								clockText += str(questLastSecond) + localeinfo.QUEST_SEC

					self.questLastTimeList[i].SetText(clockText)

	def __GetStatMinusPoint(self):
		POINT_STAT_RESET_COUNT = 112
		return player.GetStatus(POINT_STAT_RESET_COUNT)

	def __OverInStatMinusButton(self, stat):
		try:
			self.__ShowStatToolTip(self.STAT_MINUS_DESCRIPTION[stat], localeinfo.EMOJI_CHARACTER_STATS_DELETE, True)
		except KeyError:
			pass

		self.refreshToolTip = lambda arg = stat : ui.__mem_func__(self.__OverInStatMinusButton)(arg)

	def __OverOutStatMinusButton(self):
		self.__HideStatToolTip()
		self.refreshToolTip = 0

	# def __OverInStatButton(self, stat):
		# try:
			# self.__ShowStatToolTip(self.STAT_DESCRIPTION[stat])
		# except KeyError:
			# pass

	def __OverInStatButton(self, stat):	
		try:
			self.__ShowStatToolTip(self.STAT_DESCRIPTION[stat], localeinfo.EMOJI_CHARACTER_STATS_ADD, True)
		except KeyError:
			pass

	def __OverOutStatButton(self):
		self.__HideStatToolTip()

	# def __ShowStatToolTip(self, statDesc):
		# if not self.toolTip:
			# return

		# if app.ENABLE_CONQUEROR_LEVEL:
			# statDescLen = len(statDesc)
			# self.toolTip.SetThinBoardSize(11 * statDescLen)
			# self.toolTip.AlignHorizonalCenter()

		# self.toolTip.ClearToolTip()
		# self.toolTip.AppendTextLine(statDesc)
		# self.toolTip.Show()

	def __ShowStatToolTip(self, statDesc, statDesc2 = False, arg2 = False):
		if not self.toolTip:
			return

		if app.ENABLE_CONQUEROR_LEVEL:
			statDescLen = len(statDesc)
			self.toolTip.SetThinBoardSize(11 * statDescLen)
			self.toolTip.AlignHorizonalCenter()

		self.toolTip.ClearToolTip()
		self.toolTip.AppendTextLine(statDesc)

		if arg2 == True:
			self.toolTip.AppendShortcutRow(("key_ctrl", "key_lclick"), statDesc2)

		self.toolTip.Show()


	def __HideStatToolTip(self):
		if self.toolTip:
			self.toolTip.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnUpdate(self):
		self.__UpdateQuestClock()

		if app.ENABLE_CASUAL_BUFF:
			self.__UpdateCasualClock()
			self.__CasualTipCycle()

		if app.ENABLE_SKILL_COLOR_SYSTEM:
			if self.skillColorWnd:
				self.__UpdateSkillColorPosition()

	## Skill Process
	def __RefreshSkillPage(self, name, slotCount):# dream
		global SHOW_LIMIT_SUPPORT_SKILL_LIST

		skillPage = self.skillPageDict[name]

		startSlotIndex = skillPage.GetStartIndex()
		if "SUPPORT" == name and startSlotIndex == 0:
			startSlotIndex = 101   # explicit-slot passive grid reports startIndex 0; support skills live at player slots 101+
		if "ACTIVE" == name:
			if self.PAGE_HORSE == self.curSelectedSkillGroup:
				startSlotIndex += slotCount

		getSkillType = skill.GetSkillType
		getSkillIndex = player.GetSkillIndex
		getSkillGrade = player.GetSkillGrade
		getSkillLevel = player.GetSkillLevel
		getSkillLevelUpPoint = skill.GetSkillLevelUpPoint
		getSkillMaxLevel = skill.GetSkillMaxLevel

		for i in xrange(slotCount + 1):
			slotIndex = i + startSlotIndex
			skillIndex = getSkillIndex(slotIndex)

			for j in xrange(skill.SKILL_GRADE_COUNT):
				skillPage.ClearSlot(self.__GetRealSkillSlot(j, i))

			if 0 == skillIndex:
				continue

			skillGrade = getSkillGrade(slotIndex)
			skillLevel = getSkillLevel(slotIndex)
			skillType = getSkillType(skillIndex)

			if player.SKILL_INDEX_RIDING == skillIndex:
				if skillGrade == 1:
					skillLevel += 19
				elif skillGrade == 2:
					skillLevel += 29
				elif skillGrade == 3:
					skillLevel = 40

				skillPage.SetSkillSlotNew(slotIndex, skillIndex, max(skillLevel - 1, 0), skillLevel)
				skillPage.SetSlotCount(slotIndex, skillLevel)

			## ACTIVE
			elif skill.SKILL_TYPE_ACTIVE == skillType:
				for j in xrange(skill.SKILL_GRADE_COUNT):
					realSlotIndex = self.__GetRealSkillSlot(j, slotIndex)
					skillPage.SetSkillSlotNew(realSlotIndex, skillIndex, j, skillLevel)
					skillPage.SetCoverButton(realSlotIndex)

					if (skillGrade == skill.SKILL_GRADE_COUNT) and j == (skill.SKILL_GRADE_COUNT-1):
						skillPage.SetSlotCountNew(realSlotIndex, skillGrade, skillLevel)
					elif (not self.__CanUseSkillNow()) or (skillGrade != j):
						skillPage.SetSlotCount(realSlotIndex, 0)
						skillPage.DisableCoverButton(realSlotIndex)
						skillPage.DeactivateSlot(realSlotIndex) # hotfix
					else:
						skillPage.SetSlotCountNew(realSlotIndex, skillGrade, skillLevel)

					if player.IsSkillActive(slotIndex) and (skillGrade == j): # hotfix
						skillPage.ActivateSlot(realSlotIndex)
			else:
				if not SHOW_LIMIT_SUPPORT_SKILL_LIST or skillIndex in SHOW_LIMIT_SUPPORT_SKILL_LIST:
					realSlotIndex = self.__GetETCSkillRealSlotIndex(slotIndex)
					skillPage.SetSkillSlot(realSlotIndex, skillIndex, skillLevel)
					skillPage.SetSlotCountNew(realSlotIndex, skillGrade, skillLevel)

					if skill.CanUseSkill(skillIndex):
						skillPage.SetCoverButton(realSlotIndex)

					if player.IsSkillActive(slotIndex): # hotfix
						skillPage.ActivateSlot(realSlotIndex)
					else:
						skillPage.DeactivateSlot(realSlotIndex)

			skillPage.RefreshSlot()

		self.__RestoreSlotCoolTime(skillPage)

		if app.ENABLE_SKILL_COLOR_SYSTEM:
			if "ACTIVE" == name:
				if self.PAGE_HORSE != self.curSelectedSkillGroup:
					self.__CreateSkillColorButton(skillPage)
				else:
					self.skillColorButton = []

	def __RestoreSlotCoolTime(self, skillPage):
		restoreType = skill.SKILL_TYPE_NONE
		if self.PAGE_HORSE == self.curSelectedSkillGroup:
			restoreType = skill.SKILL_TYPE_HORSE
		else:
			restoreType = skill.SKILL_TYPE_ACTIVE

		skillPage.RestoreSlotCoolTime(restoreType)

	def RefreshSkill(self):
		if self.isLoaded==0:
			return

		if self.__IsChangedHorseRidingSkillLevel():
			self.RefreshCharacter()
			return

		global SHOW_ONLY_ACTIVE_SKILL
		if app.__BUFFI_SUPPORT__ and self.PAGE_BUFFI == self.curSelectedSkillGroup:
			self.__RefreshBuffiPage()
			if not SHOW_ONLY_ACTIVE_SKILL:
				self.__RefreshSkillPage("SUPPORT", self.SUPPORT_PAGE_SLOT_COUNT)
		elif SHOW_ONLY_ACTIVE_SKILL:
			self.__RefreshSkillPage("ACTIVE", self.ACTIVE_PAGE_SLOT_COUNT)
		else:
			self.__RefreshSkillPage("ACTIVE", self.ACTIVE_PAGE_SLOT_COUNT)
			self.__RefreshSkillPage("SUPPORT", self.SUPPORT_PAGE_SLOT_COUNT)

		self.RefreshSkillPlusButtonList()

	def CanShowPlusButton(self, skillIndex, skillLevel, curStatPoint, skillGrade = 0):
		if 0 == skillIndex:
			return False

		# Passive-ability skills are auto/granted (display-only): never show a level-up button.
		if skillIndex in PASSIVE_ABILITY_SKILL_LIST:
			return False

		# Master+ combat/passive skills level through the skill reader (not skill points), so keep
		# their open-reader button visible. Main combat skills are vnum <= 111.
		if skillGrade > 0 and (skillIndex <= 111 or skillIndex in OPEN_READER_SKILL_LIST):
			return True

		if not skillIndex in NINTH_SKILLS and not skillIndex in OPEN_READER_SKILL_LIST and not skill.CanLevelUpSkill(skillIndex, skillLevel):
			return False

		return True

	def __RefreshSkillPlusButton(self, name):# dream
		global HIDE_SUPPORT_SKILL_POINT

		slotWindow = self.skillPageDict[name]
		slotWindow.HideAllSlotButton()

		slotStatType = self.skillPageStatDict[name]
		if 0 == slotStatType:
			return

		statPoint = player.GetStatus(slotStatType)
		startSlotIndex = slotWindow.GetStartIndex()
		if "SUPPORT" == name and startSlotIndex == 0:
			startSlotIndex = 101
		if "HORSE" == name:
			startSlotIndex += self.ACTIVE_PAGE_SLOT_COUNT

		if statPoint > 0:
			for i in xrange(self.PAGE_SLOT_COUNT):
				slotIndex = i + startSlotIndex
				skillIndex = player.GetSkillIndex(slotIndex)
				skillGrade = player.GetSkillGrade(slotIndex)
				skillLevel = player.GetSkillLevel(slotIndex)

				if skillIndex == 0:
					continue
				if skillGrade > 2:
					continue

				if name == "HORSE":
					if player.GetStatus(player.LEVEL) >= skill.GetSkillLevelLimit(skillIndex):
						if skillLevel < 20:
							slotWindow.ShowSlotButton(self.__GetETCSkillRealSlotIndex(slotIndex))
				else:
					if "SUPPORT" == name:
						if not SHOW_LIMIT_SUPPORT_SKILL_LIST or skillIndex in SHOW_LIMIT_SUPPORT_SKILL_LIST:
							if self.CanShowPlusButton(skillIndex, skillLevel, statPoint, skillGrade):
								slotWindow.ShowSlotButton(slotIndex)
					else:
						srcSlotIndex = self.__RealSkillSlotToSourceSlot(slotIndex)
						selectedSkillIndex = self.__GetRealSkillSlot(skillGrade, slotIndex)#player.GetSkillIndex(srcSlotIndex)
						if self.CanShowPlusButton(skillIndex, skillLevel, statPoint, skillGrade):
							slotWindow.ShowSlotButton(selectedSkillIndex)#dream here this shows the plus but it appears only in the first skill slot 

	if app.ENABLE_SKILL_COLOR_SYSTEM:
		def __IsColorableSkill(self, skillIndex):
			if not osfinfo.SKILL_COLOR_BUFF_ONLY:
				return True

			WARRIOR_SG = [
				[3, 4], # WARRIOR SG1
				[19] # WARRIOR SG2
			]
			NINJA_SG = [
				[34], # NINJA SG1
				[49] # NINJA SG2
			]
			SURA_SG = [
				[63, 64, 65], # SURA SG1
				[78, 79] # SURA SG2
			]
			SHAMAN_SG = [
				[94, 95, 96], # SHAMAN SG1
				[109, 110, 111] # SHAMAN SG1
			]

			if skillIndex in WARRIOR_SG[0] or skillIndex in WARRIOR_SG[1] or\
				skillIndex in NINJA_SG[0] or skillIndex in NINJA_SG[1] or\
				skillIndex in SURA_SG[0] or skillIndex in SURA_SG[1] or\
				skillIndex in SHAMAN_SG[0] or skillIndex in SHAMAN_SG[1]:
				return True
			return False

		def ShowSkillColorBtn(self, i, info):
			try:
				global SHOW_SKILL_COLOR_IDX
				
				if info == 0:
					self.skillColorButton[i].Hide()
				else:
					self.skillColorButton[i].Show()
				
				SHOW_SKILL_COLOR_IDX[i] = info
			except:
				pass

		def __CreateSkillColorButton(self, parent):
			self.skillColorButton = []

			xPos, yPos = 0, 0
			tmpSlot = 0
			for skillSlot in xrange(self.ACTIVE_PAGE_SLOT_COUNT):
				xPos = 75 if (skillSlot % 2) == 0  else 187
				yPos = 4 + (skillSlot / 2 * 36)

				skillIndex = player.GetSkillIndex(skillSlot + 1)
				skillMaxGrade = 3

				if len(self.skillColorButton) == tmpSlot:
					self.skillColorButton.append([])
					self.skillColorButton[tmpSlot] = ui.Button()
					self.skillColorButton[tmpSlot].SetParent(parent)
					self.skillColorButton[tmpSlot].SetUpVisual("d:/ymir work/ui/skillcolor/skill_color_button_default.tga")
					self.skillColorButton[tmpSlot].SetOverVisual("d:/ymir work/ui/skillcolor/skill_color_button_over.tga")
					self.skillColorButton[tmpSlot].SetDownVisual("d:/ymir work/ui/skillcolor/skill_color_button_down.tga")
					self.skillColorButton[tmpSlot].SetPosition(xPos, yPos)
					self.skillColorButton[tmpSlot].SetEvent(lambda arg = skillSlot, arg2 = skillIndex : ui.__mem_func__(self.__OnPressSkillColorButton)(arg, arg2))
					if player.GetSkillGrade(tmpSlot + 1) >= skillMaxGrade and self.__IsColorableSkill(skillIndex):
						self.skillColorButton[tmpSlot].Hide()
					else:
						self.skillColorButton[tmpSlot].Hide()
				else:
					self.skillColorButton[tmpSlot].SetPosition(xPos, yPos)
				tmpSlot += 1
			
			global SHOW_SKILL_COLOR_IDX
			for k, v in SHOW_SKILL_COLOR_IDX.items():
				if k >= len(self.skillColorButton):
					break
				
				if v == 0:
					self.skillColorButton[k].Hide()
				else:
					self.skillColorButton[k].Show()

		def __UpdateSkillColorPosition(self):
			x, y = self.GetGlobalPosition()
			wndWidth = self.skillColorWnd.GetWidth()
			xPos = x + self.GetWidth() + 10
			if xPos + wndWidth > wndMgr.GetScreenWidth():
				xPos = max(0, x - wndWidth - 10)
			self.skillColorWnd.SetPosition(xPos, y)

		def __OnPressSkillColorButton(self, skillSlot, skillIndex):
			# if osfinfo.BETA_PVP == True:
				# try:
					# self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					# self.wndPopupDialog.Open()
				# except:
					# self.wndPopupDialog = uicommon.PopupDialog()
					# self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					# self.wndPopupDialog.Open()
				# return
			self.skillColorWnd = uiskillcolor.SkillColorWindow(skillSlot, skillIndex)
			if self.skillColorWnd and not self.skillColorWnd.IsShow():
				self.skillColorWnd.Show()
			self.__UpdateSkillColorPosition()

	def RefreshSkillPlusButtonList(self):
		if self.isLoaded==0:
			return

		self.RefreshSkillPlusPointLabel()

		if not self.__CanUseSkillNow():
			return

		try:
			if app.__BUFFI_SUPPORT__ and self.PAGE_BUFFI == self.curSelectedSkillGroup:
				self.skillPageDict["BUFFI"].HideAllSlotButton()
			elif self.PAGE_HORSE == self.curSelectedSkillGroup:
				self.__RefreshSkillPlusButton("HORSE")
			else:
				self.__RefreshSkillPlusButton("ACTIVE")

			self.__RefreshSkillPlusButton("SUPPORT")

		except:
			import exception
			exception.Abort("CharacterWindow.RefreshSkillPlusButtonList.BindObject")

	def RefreshSkillPlusPointLabel(self):
		if self.isLoaded==0:
			return

		if self.PAGE_HORSE == self.curSelectedSkillGroup:
			activeStatPoint = player.GetStatus(player.SKILL_HORSE)
			self.activeSkillPointValue.SetText(str(activeStatPoint))

		else:
			activeStatPoint = player.GetStatus(player.SKILL_ACTIVE)
			self.activeSkillPointValue.SetText(str(activeStatPoint))

		supportStatPoint = max(0, player.GetStatus(player.SKILL_SUPPORT))
		self.supportSkillPointValue.SetText(str(supportStatPoint))

	## Skill Level Up Button
	def OnPressedSlotButton(self, slotNumber):# dream
		srcSlotIndex = self.__RealSkillSlotToSourceSlot(slotNumber)

		skillIndex = player.GetSkillIndex(srcSlotIndex)
		curLevel = player.GetSkillLevel(srcSlotIndex)
		maxLevel = skill.GetSkillMaxLevel(skillIndex)
		skillGrade = player.GetSkillGrade(srcSlotIndex)
		if skillIndex in OPEN_READER_SKILL_LIST :
			self.OnClickOpenAutoSkill(skillIndex)                                   # passive: point by vnum
			return
		if skillGrade > 0:
			self.OnClickOpenAutoSkill(srcSlotIndex if srcSlotIndex <= 9 else skillIndex)  # main skill: point by slot
			return
		if self.__ShouldConfirmPvmBind(skillIndex, curLevel):
			self.__ConfirmPvmBalanceBind(skillIndex)
			return
		net.SendChatPacket("/skillup " + str(skillIndex))

	def __ShouldConfirmPvmBind(self, skillIndex, curLevel):
		# Confirm only when the server says the PvM passive is live for this (non-warrior)
		# player, it is not bound yet, and this is the first point into the skill.
		if not getattr(constinfo, "PVM_BALANCE_ACTIVE", 0):
			return 0
		if constinfo.PVM_BALANCE.get("bound", 0) != 0:
			return 0
		if curLevel != 0:
			return 0
		job = chr.RaceToJob(net.GetMainActorRace())
		group = net.GetMainActorSkillGroup()
		if skillIndex not in PVM_BIND_SKILL_LIST.get(job, {}).get(group, ()):
			return 0
		return 1

	def __ConfirmPvmBalanceBind(self, skillIndex):
		self.pvmBindPendingSkill = skillIndex
		if not getattr(self, "pvmBindDialog", None):
			self.pvmBindDialog = uipvmbalanceintro.PvmBalanceConfirmDialog()
		self.pvmBindDialog.SetSkillToolTip(getattr(self, "toolTipSkill", None))
		self.pvmBindDialog.Open(skill.GetSkillName(skillIndex), ui.__mem_func__(self.__OnPvmBindAccept))

	def __OnPvmBindAccept(self):
		net.SendChatPacket("/skillup " + str(self.pvmBindPendingSkill))

	if app.__AUTO_SKILL_READER__:
		def OnClickOpenAutoSkill(self, target = 0):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				if target:
					interfaceHandler.OpenAutoSkillReaderForSkill(target)
				else:
					interfaceHandler.OpenAutoSkillReader()

	## Use Skill
	def ClickSkillSlot(self, slotIndex):
		srcSlotIndex = self.__RealSkillSlotToSourceSlot(slotIndex)
		skillIndex = player.GetSkillIndex(srcSlotIndex)
		skillType = skill.GetSkillType(skillIndex)

		if not self.__CanUseSkillNow():
			if skill.SKILL_TYPE_ACTIVE == skillType:
				return

		for slotWindow in self.skillPageDict.values():
			if slotWindow.HasSlot(slotIndex):
				if skill.CanUseSkill(skillIndex):
					player.ClickSkillSlot(srcSlotIndex)
					return

		mousemodule.mouseController.DeattachObject()

	def OnUseSkill(self, slotIndex, coolTime):
		skillIndex = player.GetSkillIndex(slotIndex)
		skillType = skill.GetSkillType(skillIndex)

		## ACTIVE
		if skill.SKILL_TYPE_ACTIVE == skillType:
			skillGrade = player.GetSkillGrade(slotIndex)
			slotIndex = self.__GetRealSkillSlot(skillGrade, slotIndex)
		## ETC
		else:
			slotIndex = self.__GetETCSkillRealSlotIndex(slotIndex)

		for slotWindow in self.skillPageDict.values():
			if slotWindow.HasSlot(slotIndex):
				slotWindow.StoreSlotCoolTime(skillType, slotIndex, coolTime)
				self.__RestoreSlotCoolTime(slotWindow)
				#slotWindow.SetSlotCoolTime(slotIndex, coolTime)
				return

	def OnActivateSkill(self, slotIndex):
		skillGrade = player.GetSkillGrade(slotIndex)
		slotIndex = self.__GetRealSkillSlot(skillGrade, slotIndex)

		for slotWindow in self.skillPageDict.values():
			if slotWindow.HasSlot(slotIndex):
				slotWindow.ActivateSlot(slotIndex)
				return

		self.RefreshSkill()

	def OnDeactivateSkill(self, slotIndex):
		skillGrade = player.GetSkillGrade(slotIndex)
		slotIndex = self.__GetRealSkillSlot(skillGrade, slotIndex)

		for slotWindow in self.skillPageDict.values():
			if slotWindow.HasSlot(slotIndex):
				slotWindow.DeactivateSlot(slotIndex)
				return

		self.RefreshSkill()

	if app.ENABLE_COMBAT_POINTS:
		CP_IMG_PATH = "d:/ymir work/ui/game/combat_point/"
		CP_PANEL_WIDTH = 120
		CP_PANEL_HEIGHT = 79

		def __BuildCPPanel(self):
			# Base Board (dark outer frame)
			self.cpBaseBoard = ui.Board()
			self.cpBaseBoard.SetSize(self.CP_PANEL_WIDTH + 20, self.CP_PANEL_HEIGHT + 20)
			self.cpBaseBoard.AddFlag("not_pick")
			self.cpBaseBoard.Hide()

			# ThinBoard v3 on top of Board
			self.cpBoard = ui.ThinBoard("UI", 2)
			self.cpBoard.SetParent(self.cpBaseBoard)
			self.cpBoard.SetSize(self.CP_PANEL_WIDTH + 5, self.CP_PANEL_HEIGHT + 3)
			self.cpBoard.SetPosition(6, 8)
			self.cpBoard.AddFlag("not_pick")
			self.cpBoard.Show()

			# Background image (custom asset)
			self.cpBgImage = ui.ExpandedImageBox()
			self.cpBgImage.SetParent(self.cpBoard)
			self.cpBgImage.LoadImage(self.CP_IMG_PATH + "bg.png")
			self.cpBgImage.SetPosition(4, 4)
			self.cpBgImage.AddFlag("not_pick")
			self.cpBgImage.Show()

			# Shield icon (top right, hoverable)
			self.cpGearIcon = ui.ImageBox()
			self.cpGearIcon.SetParent(self.cpBgImage)
			self.cpGearIcon.LoadImage(self.CP_IMG_PATH + "cp_1.png")
			self.cpGearIcon.SetPosition(87, 12)
			self.cpGearIcon.OnMouseOverIn = lambda: self.__ShowCPIconToolTip("gear")
			self.cpGearIcon.OnMouseOverOut = lambda: self.toolTip.HideToolTip()
			self.cpGearIcon.Show()

			# Swords icon (bottom right, hoverable)
			self.cpTotalIcon = ui.ImageBox()
			self.cpTotalIcon.SetParent(self.cpBgImage)
			self.cpTotalIcon.LoadImage(self.CP_IMG_PATH + "cp_2.png")
			self.cpTotalIcon.SetPosition(87, 47)
			self.cpTotalIcon.OnMouseOverIn = lambda: self.__ShowCPIconToolTip("total")
			self.cpTotalIcon.OnMouseOverOut = lambda: self.toolTip.HideToolTip()
			self.cpTotalIcon.Show()

			# Gear Score value
			self.cpGearValue = ui.TextLine()
			self.cpGearValue.SetParent(self.cpBgImage)
			self.cpGearValue.SetPosition(40, 12)
			self.cpGearValue.SetPackedFontColor(0xFFff9f43)
			self.cpGearValue.SetHorizontalAlignCenter()
			self.cpGearValue.SetText("0")
			self.cpGearValue.Show()

			# Total CP value
			self.cpTotalValue = ui.TextLine()
			self.cpTotalValue.SetParent(self.cpBgImage)
			self.cpTotalValue.SetPosition(40, 52)
			self.cpTotalValue.SetPackedFontColor(0xFFc8d6e5)
			self.cpTotalValue.SetHorizontalAlignCenter()
			self.cpTotalValue.SetText("0")
			self.cpTotalValue.Show()

			# Toggle buttons (independent windows, between panel and char window)
			self.cpExpandBtn = ui.Button()
			self.cpExpandBtn.SetUpVisual("d:/ymir work/ui/game/belt_inventory/btn_expand_normal.tga")
			self.cpExpandBtn.SetOverVisual("d:/ymir work/ui/game/belt_inventory/btn_expand_over.tga")
			self.cpExpandBtn.SetDownVisual("d:/ymir work/ui/game/belt_inventory/btn_expand_down.tga")
			self.cpExpandBtn.SetEvent(ui.__mem_func__(self.__ToggleCPPanel))
			self.cpExpandBtn.Hide()

			self.cpCollapseBtn = ui.Button()
			self.cpCollapseBtn.SetUpVisual("d:/ymir work/ui/game/belt_inventory/btn_minimize_normal.tga")
			self.cpCollapseBtn.SetOverVisual("d:/ymir work/ui/game/belt_inventory/btn_minimize_over.tga")
			self.cpCollapseBtn.SetDownVisual("d:/ymir work/ui/game/belt_inventory/btn_minimize_down.tga")
			self.cpCollapseBtn.SetEvent(ui.__mem_func__(self.__ToggleCPPanel))
			self.cpCollapseBtn.Hide()

			# Hide/Show toggle button (on the CP panel)
			CP_BTN_PATH = "d:/ymir work/ui/game/"
			self.cpHideBtn = ui.Button()
			self.cpHideBtn.SetParent(self.cpBgImage)
			self.cpHideBtn.SetUpVisual(CP_BTN_PATH + "btn_hide_01.png")
			self.cpHideBtn.SetOverVisual(CP_BTN_PATH + "btn_hide_02.png")
			self.cpHideBtn.SetDownVisual(CP_BTN_PATH + "btn_hide_03.png")
			self.cpHideBtn.SetToolTipText(localeinfo.CP_TOGGLE_VISIBILITY if hasattr(localeinfo, 'CP_TOGGLE_VISIBILITY') else "Toggle CP Visibility")
			self.cpHideBtn.SetPosition(6, 8)
			self.cpHideBtn.SetEvent(ui.__mem_func__(self.__OnClickCPHide))
			self.cpHideBtn.Show()

			self.cpIsHidden = False

		def __OnClickCPHide(self):
			net.SendChatPacket("/cp_hide")

		def OnCPHideState(self, state):
			self.cpIsHidden = (state == 1)
			CP_BTN_PATH = "d:/ymir work/ui/game/"

			if self.cpIsHidden:
				self.cpHideBtn.SetUpVisual(CP_BTN_PATH + "icon_red_1.png")
				self.cpHideBtn.SetOverVisual(CP_BTN_PATH + "icon_red_2.png")
				self.cpHideBtn.SetDownVisual(CP_BTN_PATH + "icon_red_3.png")
			else:
				self.cpHideBtn.SetUpVisual(CP_BTN_PATH + "btn_hide_01.png")
				self.cpHideBtn.SetOverVisual(CP_BTN_PATH + "btn_hide_02.png")
				self.cpHideBtn.SetDownVisual(CP_BTN_PATH + "btn_hide_03.png")

		def __ShowCPIconToolTip(self, cpType):
			self.toolTip.ClearToolTip()

			if cpType == "gear":
				gearCP = player.GetStatus(player.GEAR_CP)
				self.toolTip.AutoAppendTextLine(localeinfo.CP_GEAR_SCORE_TITLE, 0xFFFFCC00)
				self.toolTip.AppendHorizontalLine()
				self.toolTip.AutoAppendTextLine(localeinfo.NumberToMoneyStringNEW(gearCP), 0xFF8BBDFF)
				self.toolTip.AppendSpace(3)
				self.toolTip.AutoAppendTextLine(localeinfo.CP_GEAR_SCORE_DESC_1, 0xFFAAAAAA)
				self.toolTip.AutoAppendTextLine(localeinfo.CP_GEAR_SCORE_DESC_2, 0xFFAAAAAA)
				self.toolTip.AutoAppendTextLine(localeinfo.CP_GEAR_SCORE_DESC_3, 0xFFAAAAAA)
				self.toolTip.AppendHorizontalLine()
				self.toolTip.AutoAppendTextLine(localeinfo.CP_GEAR_SCORE_FOOTER, 0xFF98FB98)
			elif cpType == "total":
				totalCP = player.GetStatus(player.TOTAL_CP)
				self.toolTip.AutoAppendTextLine(localeinfo.CP_TOTAL_TITLE, 0xFFFFCC00)
				self.toolTip.AppendHorizontalLine()
				self.toolTip.AutoAppendTextLine(localeinfo.NumberToMoneyStringNEW(totalCP), 0xFFADFF2F)
				self.toolTip.AppendSpace(3)
				self.toolTip.AutoAppendTextLine(localeinfo.CP_TOTAL_DESC_1, 0xFFAAAAAA)
				self.toolTip.AutoAppendTextLine(localeinfo.CP_TOTAL_DESC_2, 0xFFAAAAAA)
				self.toolTip.AppendHorizontalLine()
				self.toolTip.AutoAppendTextLine(localeinfo.CP_TOTAL_FOOTER, 0xFF98FB98)

			self.toolTip.AlignHorizonalCenter()
			self.toolTip.ShowToolTip()

		def __ToggleCPPanel(self):
			if self.cpPanelVisible:
				self.cpBaseBoard.Hide()
				self.cpCollapseBtn.Hide()
				self.cpExpandBtn.Show()
				self.cpPanelVisible = False
			else:
				self.__UpdateCPPanelPosition()
				self.cpBaseBoard.Show()
				self.cpCollapseBtn.Show()
				self.cpExpandBtn.Hide()
				self.cpPanelVisible = True

		def __UpdateCPPanelPosition(self):
			if self.cpBaseBoard:
				(x, y) = self.GetGlobalPosition()
				panelW = self.cpBaseBoard.GetWidth()
				panelH = self.cpBaseBoard.GetHeight()
				panelX = x - panelW - 2
				panelY = y + 30
				btnX = x - 8
				btnY = panelY + (panelH / 2) - 16 - 37
				self.cpBaseBoard.SetPosition(panelX, panelY)
				self.cpCollapseBtn.SetPosition(btnX, btnY)
				self.cpExpandBtn.SetPosition(btnX, btnY)

		def __RefreshCPValues(self):
			if not self.cpGearValue or not self.cpTotalValue:
				return
			gearCP = player.GetStatus(player.GEAR_CP)
			totalCP = player.GetStatus(player.TOTAL_CP)
			self.cpGearValue.SetText(localeinfo.NumberToMoneyStringNEW(gearCP))
			self.cpTotalValue.SetText(localeinfo.NumberToMoneyStringNEW(totalCP))

	def __ShowJobToolTip(self):
		if app.ENABLE_COMBAT_POINTS:
			self.toolTipJob.ClearToolTip()
			gearCP = player.GetStatus(player.GEAR_CP)
			totalCP = player.GetStatus(player.TOTAL_CP)
			self.toolTipJob.AutoAppendTextLine(localeinfo.CP_COMBAT_POWER, 0xFFFFCC00)
			self.toolTipJob.AppendSpace(3)
			self.toolTipJob.AutoAppendTextLine("%s: %s" % (localeinfo.CP_GEAR_SCORE_TITLE, localeinfo.NumberToMoneyStringNEW(gearCP)), 0xFF8BBDFF)
			self.toolTipJob.AutoAppendTextLine("%s: %s" % (localeinfo.CP_TOTAL_TITLE, localeinfo.NumberToMoneyStringNEW(totalCP)), 0xFFADFF2F)
			self.toolTipJob.AlignHorizonalCenter()
		self.toolTipJob.ShowToolTip()

	if app.ENABLE_SKILL_COOLTIME_UPDATE:
		def SkillClearCoolTime(self, slotIndex):
			slotIndex = self.__GetRealSkillSlot(player.GetSkillGrade(slotIndex), slotIndex)
			for slotWindow in self.skillPageDict.values():
				if slotWindow.HasSlot(slotIndex):
					slotWindow.SetSlotCoolTime(slotIndex, 0)

	def __HideJobToolTip(self):
		self.toolTipJob.HideToolTip()

	def __SetJobText(self, mainJob, subJob):
		if player.GetStatus(player.LEVEL)<5:
			subJob=0

		if 949 == app.GetDefaultCodePage():
			self.toolTipJob.ClearToolTip()

			try:
				jobInfoTitle=localeinfo.JOBINFO_TITLE[mainJob][subJob]
				jobInfoData=localeinfo.JOBINFO_DATA_LIST[mainJob][subJob]
			except IndexError:
				print "uicharacter.CharacterWindow.__SetJobText(mainJob=%d, subJob=%d)" % (mainJob, subJob)
				return

			self.toolTipJob.AutoAppendTextLine(jobInfoTitle)
			self.toolTipJob.AppendSpace(5)

			for jobInfoDataLine in jobInfoData:
				self.toolTipJob.AutoAppendTextLine(jobInfoDataLine)

			self.toolTipJob.AlignHorizonalCenter()

	def __ShowAlignmentToolTip(self):
		self.toolTipAlignment.ShowToolTip()
		self.toolTipAlignment.SetTop()

	def __HideAlignmentToolTip(self):
		self.toolTipAlignment.HideToolTip()

	def __OnClickAlignment(self):
		import uialignment
		if self.alignmentWnd is None:
			self.alignmentWnd = uialignment.AlignmentWindow()
		if self.alignmentWnd.IsShow():
			self.alignmentWnd.Hide()
		else:
			x, y = self.GetGlobalPosition()
			self.alignmentWnd.Open(x, y)

	def __OnClickTitleButton(self):
		import systemSetting
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler:
			interfaceHandler.ToggleTitleWindow()

	def RefreshCharacter(self):
		if self.isLoaded == 0:
			return

		## Name
		try:
			characterName = player.GetName()
			guildName = player.GetGuildName()
			self.characterNameValue.SetText(characterName)
			self.guildNameValue.SetText(guildName)
			if not guildName:
				if localeinfo.IsARABIC():
					self.characterNameSlot.SetPosition(190, 34)
				else:
					self.characterNameSlot.SetPosition(109, 34)

				self.guildNameSlot.Hide()
			else:
				if localeinfo.IsJAPAN():
					self.characterNameSlot.SetPosition(143, 34)
				else:
					self.characterNameSlot.SetPosition(153, 34)
				self.guildNameSlot.Show()

		except:
			import exception
			exception.Abort("CharacterWindow.RefreshCharacter.BindObject")

		race = net.GetMainActorRace()
		group = net.GetMainActorSkillGroup()
		empire = net.GetMainActorEmpire()

		## Job Text
		job = chr.RaceToJob(race)
		self.__SetJobText(job, group)

		## FaceImage
		try:
			faceImageName = FACE_IMAGE_DICT[race]

			try:
				self.faceImage.LoadImage(faceImageName)
			except:
				print "CharacterWindow.RefreshCharacter(race=%d, faceImageName=%s)" % (race, faceImageName)
				self.faceImage.Hide()

		except KeyError:
			self.faceImage.Hide()

		## GroupName
		self.__SetSkillGroupName(race, group)

		## Skill
		if 0 == group:
			self.__SelectSkillGroup(0)

		else:
			self.__SetSkillSlotData(race, group, empire)

			if self.__CanUseHorseSkill():
				self.__SelectSkillGroup(0)

	def __SetSkillGroupName(self, race, group):
		job = chr.RaceToJob(race)

		if app.__BUFFI_SUPPORT__ and self.buffiGroupButtonIndex >= 0:
			buffiBtn = self.skillGroupButton[self.buffiGroupButtonIndex]
			buffiBtn.SetText(getattr(localeinfo, "SKILL_GROUP_BUFFI", "Buffi"))
			buffiBtn.Show()

		if not self.SKILL_GROUP_NAME_DICT.has_key(job):
			return

		nameList = self.SKILL_GROUP_NAME_DICT[job]

		if 0 == group:
			self.skillGroupButton1.SetText(nameList[1])
			self.skillGroupButton2.SetText(nameList[2])
			self.skillGroupButton1.Show()

			if playersettingmodule.RACE_WOLFMAN_M != race:
				self.skillGroupButton2.Show()

			self.activeSkillGroupName.Hide()
		else:
			if self.__CanUseHorseSkill():
				self.activeSkillGroupName.Hide()
				self.skillGroupButton1.SetText(nameList.get(group, "Noname"))
				self.skillGroupButton2.SetText(localeinfo.SKILL_GROUP_HORSE)
				self.skillGroupButton1.Show()
				self.skillGroupButton2.Show()
			elif app.__BUFFI_SUPPORT__ and self.buffiGroupButtonIndex >= 0:
				# No horse, but the buffi tab needs a clickable sibling to return to:
				# show the active-skills group as a real button instead of a static label.
				self.skillGroupButton1.SetText(nameList.get(group, "Noname"))
				self.skillGroupButton1.Show()
				self.skillGroupButton2.Hide()
				self.activeSkillGroupName.Hide()
			else:
				self.activeSkillGroupName.SetText(nameList.get(group, "Noname"))
				self.activeSkillGroupName.Show()
				self.skillGroupButton1.Hide()
				self.skillGroupButton2.Hide()

	def __SetSkillSlotData(self, race, group, empire=0):
		## SkillIndex
		playerLoad.RegisterSkill(race, group, empire)

		self.__RegisterSupportSkillSlots()

		if app.__BUFFI_SUPPORT__:
			self.__RegisterBuffiSkillSlots()

		## Event
		self.__SetSkillSlotEvent()

		## Refresh
		self.RefreshSkill()

	def __RegisterBuffiSkillSlots(self):
		for i in xrange(self.BUFFI_SKILL_COUNT):
			player.SetSkill(self.BUFFI_SKILL_SLOT_START + i, self.BUFFI_SKILL_VNUM_START + i)

	def __RegisterSupportSkillSlots(self):
		# The precompiled playerLoad.RegisterSkill() writes vecSupportSkills onto
		# slots 101+, but then re-assigns the empire language skills (126/127/128)
		# onto the first support slots (101/102), shadowing the leadership/combo
		# entries that were meant to live there. Those language vnums are not in
		# SHOW_LIMIT_SUPPORT_SKILL_LIST, so the render filter skips them and the
		# first two slots come up blank. Re-assert the intended support layout after
		# the loader (same approach as __RegisterBuffiSkillSlots) so slot 101+i
		# always holds the whitelisted skill the page expects to draw.
		for i, skillIndex in enumerate(SHOW_LIMIT_SUPPORT_SKILL_LIST):
			player.SetSkill(101 + i, skillIndex)

	def __RefreshBuffiPage(self):
		skillPage = self.skillPageDict["BUFFI"]

		getSkillIndex = player.GetSkillIndex
		getSkillGrade = player.GetSkillGrade
		getSkillLevel = player.GetSkillLevel

		for i in xrange(self.ACTIVE_PAGE_SLOT_COUNT + 1):
			for j in xrange(skill.SKILL_GRADE_COUNT):
				skillPage.ClearSlot(self.__GetRealSkillSlot(j, i))

		for i in xrange(self.BUFFI_SKILL_COUNT):
			srcSlotIndex = self.BUFFI_SKILL_SLOT_START + i
			skillIndex = getSkillIndex(srcSlotIndex)
			if 0 == skillIndex:
				continue

			skillGrade = getSkillGrade(srcSlotIndex)
			skillLevel = getSkillLevel(srcSlotIndex)
			renderBaseSlot = i + 1

			for j in xrange(skill.SKILL_GRADE_COUNT):
				realSlotIndex = renderBaseSlot + j * skill.SKILL_GRADE_STEP_COUNT
				skillPage.SetSkillSlotNew(realSlotIndex, skillIndex, j, skillLevel)
				skillPage.SetCoverButton(realSlotIndex)

				if (skillGrade == skill.SKILL_GRADE_COUNT) and j == (skill.SKILL_GRADE_COUNT - 1):
					skillPage.SetSlotCountNew(realSlotIndex, skillGrade, skillLevel)
				elif skillGrade != j:
					skillPage.SetSlotCount(realSlotIndex, 0)
					skillPage.DisableCoverButton(realSlotIndex)
					skillPage.DeactivateSlot(realSlotIndex)
				else:
					skillPage.SetSlotCountNew(realSlotIndex, skillGrade, skillLevel)

			skillPage.RefreshSlot()

		self.__RestoreSlotCoolTime(skillPage)

	def __SelectSkillGroup(self, index):
		for btn in self.skillGroupButton:
			btn.SetUp()
		self.skillGroupButton[index].Down()

		if app.__BUFFI_SUPPORT__ and self.buffiGroupButtonIndex == index:
			self.curSelectedSkillGroup = self.PAGE_BUFFI
			self.RefreshSkill()
			return

		if self.__CanUseHorseSkill():
			if 0 == index:
				index = net.GetMainActorSkillGroup() - 1
			elif 1 == index:
				index = self.PAGE_HORSE
		elif app.__BUFFI_SUPPORT__ and 0 == index and net.GetMainActorSkillGroup() != 0:
			index = net.GetMainActorSkillGroup() - 1

		self.curSelectedSkillGroup = index
		self.__SetSkillSlotData(net.GetMainActorRace(), index+1, net.GetMainActorEmpire())

	def __CanUseSkillNow(self):
		if 0 == net.GetMainActorSkillGroup():
			return False

		return True

	def __CanUseHorseSkill(self):
		slotIndex = player.GetSkillSlotIndex(player.SKILL_INDEX_RIDING)

		if not slotIndex:
			return False

		grade = player.GetSkillGrade(slotIndex) # hotfix
		level = player.GetSkillLevel(slotIndex)

		if level < 0:
			level *= -1

		if level >= 20:
			return True

		if grade >= 1 and level >= 1: # hotfix
			return True

		return False

	def __IsChangedHorseRidingSkillLevel(self):
		ret = False

		if -1 == self.canUseHorseSkill:
			self.canUseHorseSkill = self.__CanUseHorseSkill()

		if self.canUseHorseSkill != self.__CanUseHorseSkill():
			ret = True

		self.canUseHorseSkill = self.__CanUseHorseSkill()
		return ret

	def __GetRealSkillSlot(self, skillGrade, skillSlot):
		return skillSlot + min(skill.SKILL_GRADE_COUNT-1, skillGrade) * skill.SKILL_GRADE_STEP_COUNT

	def __GetETCSkillRealSlotIndex(self, skillSlot):
		if skillSlot > 100:
			return skillSlot
		return skillSlot % self.ACTIVE_PAGE_SLOT_COUNT

	def __RealSkillSlotToSourceSlot(self, realSkillSlot):
		if realSkillSlot > 100:
			return realSkillSlot
		if app.__BUFFI_SUPPORT__ and self.PAGE_BUFFI == self.curSelectedSkillGroup:
			return self.BUFFI_SKILL_SLOT_START + (realSkillSlot % skill.SKILL_GRADE_STEP_COUNT) - 1
		if self.PAGE_HORSE == self.curSelectedSkillGroup:
			return realSkillSlot + self.ACTIVE_PAGE_SLOT_COUNT
		return realSkillSlot % skill.SKILL_GRADE_STEP_COUNT

	def __GetSkillGradeFromSlot(self, skillSlot):
		return int(skillSlot / skill.SKILL_GRADE_STEP_COUNT)

	def SelectSkillGroup(self, index):
		self.__SelectSkillGroup(index)

	def OnQuestScroll(self):
		questCount = quest.GetQuestCount()
		scrollLineCount = max(0, questCount - quest.QUEST_MAX_NUM)
		startIndex = int(scrollLineCount * self.questScrollBar.GetPos())

		if startIndex != self.questShowingStartIndex:
			self.questShowingStartIndex = startIndex
			self.RefreshQuest()

	if app.ENABLE_QUEST_RENEWAL:
		def __OnScrollQuest(self):
			if self.state != "QUEST":
				return

			curPos = self.questScrollBar.GetPos()
			if math.fabs(curPos - self.questLastScrollPosition) >= 0.001:
				self.RerenderQuestPage()
				self.questLastScrollPosition = curPos

		def ResetQuestScroll(self):
			self.questScrollBar.Hide()

			if self.questScrollBar.GetPos() != 0:
				self.questScrollBar.SetPos(0)

		def RerenderQuestPage(self):
			overflowingY = self.displayY - self.MAX_QUEST_PAGE_HEIGHT
			if overflowingY < 0:
				overflowingY = 0

			self.baseCutY = math.ceil(overflowingY * self.questScrollBar.GetPos())
			self.displayY = 0
			self.RearrangeQuestCategories(xrange(quest.QUEST_CATEGORY_MAX_NUM))
			self.RefreshQuestCategory()

			if overflowingY > 0:
				if (len(self.questOpenedCategories)) == 0:
					self.ResetQuestScroll()
				else:
					self.questScrollBar.Show()
			else:
				self.ResetQuestScroll()

		def __LoadQuestCategory(self):
			self.questPage.Show()

			if self.isLoaded == 0:
				return

			for i in xrange(quest.QUEST_CATEGORY_MAX_NUM):
				category = self.questCategoryList[i]

				categoryName = category.GetProperty("name")
				if not categoryName:
					category.SetProperty("name", category.GetText())
					categoryName = category.GetText()

				questCount = self.GetQuestCountInCategory(i)
				self.questCategoryList[i].SetTextAlignLeft(categoryName + " (" + str(questCount) + ")")
				self.questCategoryList[i].SetTextColor(self.GetQuestCategoryColor(i))
				self.questCategoryList[i].SetQuestLabel(quest_lable_expend_img_path_dict[i], self.GetQuestCountInCategory(i))
				self.questCategoryList[i].Show()

			self.RefreshQuestCategory()
			if self.isQuestCategoryLoad == False:
				self.questScrollBar.Hide()
			else:
				self.RerenderQuestPage()

			self.isQuestCategoryLoad = True

		def GetQuestCategoryColor(self, category):
			return self.questColorList["default_title"]

		def GetQuestProperties(self, questName):
			if len(questName) > 0:
				findString = {
					"*" : "blue",
					"&" : "green",
					"~" : "golden"
				}

				if questName[0] in findString:
					return (questName[1:], findString[questName[0]])

			return (questName, None)

		def IsQuestCategoryOpen(self, category):
			return (category in self.questOpenedCategories)

		def ToggleCategory(self, category):
			if self.IsQuestCategoryOpen(category):
				self.CloseQuestCategory(category)
			else:
				self.OpenQuestCategory(category)

		def RearrangeQuestCategories(self, categoryRange):
			i = 0
			for i in categoryRange:
				if (self.displayY - self.baseCutY) >= 0 and (self.displayY - self.baseCutY) < self.MAX_QUEST_PAGE_HEIGHT - 20:
					self.questCategoryList[i].SetPosition(13, (self.displayY - self.baseCutY) + 10)#13 10
					self.questCategoryList[i].Show()
				else:
					self.questCategoryList[i].Hide()

				self.displayY += 20
				self.questCategoryRenderPos[i] = self.displayY

		def CloseQuestCategory(self, category):
			self.questCategoryList[category].CloseCategory(self.GetQuestCountInCategory(category))

			if category in self.questOpenedCategories:
				self.questOpenedCategories.remove(category)

			for currentSlot in self.questSlotList:
				if currentSlot.GetProperty("category") == category:
					currentSlot.Hide()
					self.displayY -= currentSlot.GetHeight()

			self.RerenderQuestPage()

		def OpenQuestCategory(self, category):
			if self.GetQuestCountInCategory(category) == 0:
				return

			while len(self.questOpenedCategories) >= self.questMaxOpenedCategories:
				openedCategories = self.questOpenedCategories.pop()
				self.CloseQuestCategory(openedCategories)

			self.questCategoryList[category].OpenCategory(self.GetQuestCountInCategory(category))
			self.questOpenedCategories.append(category)
			self.RefreshQuestCategory(category)
			self.RerenderQuestPage()

		def RefreshQuestCategory(self, category = -1):
			if self.isLoaded == 0 or self.state != "QUEST":
				return

			categories = []
			if category == -1:
				categories = self.questOpenedCategories
			elif not category in self.questOpenedCategories:
				self.OpenQuestCategory(category)
				return
			else:
				categories.append(category)

			for currentCategory in categories:
				self.displayY = self.questCategoryRenderPos[currentCategory]

				self.LoadCategory(currentCategory)
				self.RearrangeQuestCategories(xrange(currentCategory + 1, quest.QUEST_CATEGORY_MAX_NUM))

		def RefreshQuestCategoriesCount(self):
			for category in xrange(quest.QUEST_CATEGORY_MAX_NUM):
				categoryName = self.questCategoryList[category].GetProperty("name")
				questCount = self.GetQuestCountInCategory(category)
				self.questCategoryList[category].SetTextAlignLeft(categoryName + " (" + str(questCount) + ")")

		def RefreshQuest(self):
			if self.isLoaded == 0 or self.state != "QUEST":
				return

			for category in self.questOpenedCategories:
				self.RefreshQuestCategory(category)

			self.RefreshQuestCategoriesCount()

		def CreateQuestSlot(self, name):
			for questSlot in self.questSlotList:
				if questSlot.GetWindowName() == name:
					return questSlot

			pyScrLoader = ui.PythonScriptLoader()
			slot = ui.ListBar()
			pyScrLoader.LoadElementListBar(slot, quest_slot_listbar, self.questPage)

			slot.SetParent(self.quest_page_board_window)
			slot.SetWindowName(name)
			slot.Hide()
			self.questSlotList.append(slot)
			return slot

		def SetQuest(self, slot, questID, questName, questCounterName, questCounterValue):
			(name, color) = self.GetQuestProperties(questName)
			slot.SetTextAlignLeftCat(name, 20)
			if color:
				slot.SetTextColor(self.questColorList[color])
			slot.SetEvent(ui.__mem_func__(self.__SelectQuest), questID)
			slot.SetWindowHorizontalAlignLeft()
			slot.Show()

		def LoadCategory(self, category):
			self.questIndexMap = {}
			self.questCounterList = []
			self.questClockList = []
			self.questSeparatorList = []

			for questSlot in self.questSlotList:
				questSlot.Hide()

			questCount = 0
			for questIdx in self.GetQuestsInCategory(category):
				questCount += 1
				(questID, questIndex, questName, questCategory, _, questCounterName, questCounterValue) = questIdx
				(lastName, lastTime) = quest.GetQuestLastTime(questID)

				slot = self.CreateQuestSlot("QuestSlotList_" + str(questCategory) + "_" + str(questID))

				slot.SetPosition(0, -153 + (self.displayY - self.baseCutY))
				slot.SetParent(self.quest_page_board_window)
				baseDisplayY = self.displayY

				## -- Quest Counter
				hasCounter = False
				if questCounterName != "":
					self.displayY += 20

					counter = ui.TextLine()
					counter.SetParent(slot)
					counter.SetPosition(198, 22)
					counter.SetText(questCounterName + ": " + str(questCounterValue))
					counter.Show()

					self.questCounterList.append(counter)
					hasCounter = True
				## -- Quest Counter

				## -- Quest Clock
				self.displayY += 20

				clockText = localeinfo.QUEST_UNLIMITED_TIME
				if len(lastName) > 0:
					if lastTime <= 0:
						clockText = localeinfo.QUEST_TIMEOVER
					else:
						questLastMinute = lastTime / 60
						questLastSecond = lastTime % 60

						clockText = lastName + " : "

						if questLastMinute > 0:
							clockText += str(questLastMinute) + localeinfo.QUEST_MIN
							if questLastSecond > 0:
								clockText += " "

						if questLastSecond > 0:
							clockText += str(questLastSecond) + localeinfo.QUEST_SEC

				clock = ui.TextLine()
				clock.SetParent(slot)
				clock.SetPosition(198, (int(hasCounter) * 14) +22)
				clock.SetText(clockText)
				clock.SetProperty("idx", questID)
				self.questClockList.append(clock)
				clock.Show()
				## -- Quest Clock

				## -- Quest Separator
				self.displayY += 10
				if questCount < self.GetQuestCountInCategory(category):
					seperator = ui.ImageBox()
					seperator.SetParent(slot)
					seperator.SetPosition(8, (int(hasCounter) * 14 +46))
					seperator.LoadImage("d:/ymir work/ui/quest_re/quest_list_line_01.tga")
					seperator.Show()
					self.questSeparatorList.append(seperator)
				## -- Quest Separator

				slot.SetProperty("category", questCategory)

				if questIndex in self.questClicked:
					slot.OnClickEvent()

				if (baseDisplayY - self.baseCutY) + 2 >= 0 and (baseDisplayY - self.baseCutY) + 2 < self.MAX_QUEST_PAGE_HEIGHT - 30:
					self.questIndexMap[questID] = questIndex
					self.SetQuest(slot, questID, questName, questCounterName, questCounterValue)

				self.displayY += 20

			newList = []
			for questSlot in self.questSlotList:
				if questSlot.IsShow():
					newList.append(questSlot)

			self.questSlotList = newList

		def __OnClickQuestCategoryButton(self, category):
			self.ToggleCategory(category)

		def GetQuestsInCategory(self, category, retCount = False):
			questList = []
			count = 0
			for i in xrange(quest.GetQuestCount()):
				(questIndex, questName, questCategory, questIcon, questCounterName, questCounterValue) = quest.GetQuestData(i)
				if questCategory == category:
					count += 1
					questList.append((i, questIndex, questName, questCategory, questIcon, questCounterName, questCounterValue))

			if retCount:
				return count

			return questList

		def GetQuestCountInCategory(self, category):
			return self.GetQuestsInCategory(category, True)
