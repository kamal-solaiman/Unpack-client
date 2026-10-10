# coding: utf-8

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import net
import player

if app.ENABLE_POISON_GAUGE_EFFECT:
	import chr
	import chrmgr

import ui
import item
import skill
import localeinfo
import wndMgr
import constinfo
import osfinfo
import mousemodule
import uiscriptlocale
import guild

import uicommon
import uitooltip
import uibadge

if app.ENABLE_ITEMSHOP:
	import systemSetting

if app.ENABLE_ANTI_MULTIPLE_FARM:
	import anti_multiple_farm
	MULTIPLE_FARM_STATE_IMAGES = ["d:/ymir work/ui/pattern/visible_mark_01.tga", "d:/ymir work/ui/pattern/visible_mark_03.tga"]

MOUSE_SETTINGS = [0, 0]
def InitMouseButtonSettings(left, right):
	global MOUSE_SETTINGS
	MOUSE_SETTINGS = [left, right]

def SetMouseButtonSetting(dir, event):
	global MOUSE_SETTINGS
	MOUSE_SETTINGS[dir] = event

def GetMouseButtonSettings():
	global MOUSE_SETTINGS
	return MOUSE_SETTINGS

def SaveMouseButtonSettings():
	global MOUSE_SETTINGS
	open("mouse.cfg", "w").write("%s\t%s" % tuple(MOUSE_SETTINGS))

def LoadMouseButtonSettings():
	global MOUSE_SETTINGS
	tokens = open("mouse.cfg", "r").read().split()

	if len(tokens) != 2:
		raise RuntimeError, "MOUSE_SETTINGS_FILE_ERROR"

	MOUSE_SETTINGS[0] = int(tokens[0])
	MOUSE_SETTINGS[1] = int(tokens[1])

def unsigned32(n):
	return n & 0xFFFFFFFFL

#-------------------Giftbox Begin------------------------------

class GiftBox(ui.ScriptWindow):
	class TextToolTip(ui.Window):
		def __init__(self):
			ui.Window.__init__(self, "TOP_MOST")
			self.SetWindowName("GiftBox")
			textLine = ui.TextLine()
			textLine.SetParent(self)
			textLine.SetHorizontalAlignCenter()
			textLine.SetOutline()
			textLine.Show()
			self.textLine = textLine

		def __del__(self):
			ui.Window.__del__(self)

		def SetText(self, text):
			self.textLine.SetText(text)

		def OnRender(self):
			(mouseX, mouseY) = wndMgr.GetMousePosition()
			self.textLine.SetPosition(mouseX, mouseY - 15)

	def __init__(self):
		# print "NEW TASKBAR -----------------------------------------------------------------------------"
		ui.ScriptWindow.__init__(self)
		self.tooltipGift = self.TextToolTip()
		self.tooltipGift.Show()

	def __del__(self):
		# print "---------------------------------------------------------------------------- DELETE TASKBAR"
		ui.ScriptWindow.__del__(self)

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "giftbox.py")
		except:
			import exception
			exception.Abort("GiftBox.LoadWindow.LoadObject")

		self.giftBoxIcon = self.GetChild("GiftBox_Icon")
		self.giftBoxIcon.SetEvent(ui.__mem_func__(self.OpenMall), "mouse_click")
		self.giftBoxToolTip = self.GetChild("GiftBox_ToolTip")

	def Destroy(self):
		self.giftBoxIcon = None
		self.giftBoxToolTip = None

	def OpenMall(self):
		net.SendChatPacket("/click_mall")
		self.Hide()

#-------------------Giftbox End------------------------------

class EnergyBar(ui.ScriptWindow):
	class TextToolTip(ui.Window):
		def __init__(self):
			ui.Window.__init__(self, "TOP_MOST")
			self.SetWindowName("EnergyBar")
			textLine = ui.TextLine()
			textLine.SetParent(self)
			textLine.SetHorizontalAlignCenter()
			textLine.SetOutline()
			textLine.Show()
			self.textLine = textLine

		def __del__(self):
			ui.Window.__del__(self)

		def SetText(self, text):
			self.textLine.SetText(text)

		def OnRender(self):
			(mouseX, mouseY) = wndMgr.GetMousePosition()
			self.textLine.SetPosition(mouseX, mouseY - 15)

	def __init__(self):
		#print "NEW TASKBAR -----------------------------------------------------------------------------"
		ui.ScriptWindow.__init__(self)
		self.tooltipEnergy = self.TextToolTip()
		self.tooltipEnergy.Show()

	def __del__(self):
		#print "---------------------------------------------------------------------------- DELETE TASKBAR"
		ui.ScriptWindow.__del__(self)

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			if localeinfo.IsARABIC():
				pyScrLoader.LoadScriptFile(self, "uiscript/ae_EnergyBar.py")
			else:
				pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "EnergyBar.py")
		except:
			import exception
			exception.Abort("EnergyBar.LoadWindow.LoadObject")

		self.energyEmpty = self.GetChild("EnergyGauge_Empty")
		self.energyHungry = self.GetChild("EnergyGauge_Hungry")
		self.energyFull = self.GetChild("EnergyGauge_Full")

		self.energyGaugeBoard = self.GetChild("EnergyGauge_Board")
		self.energyGaugeToolTip = self.GetChild("EnergyGauge_ToolTip")

	def Destroy(self):
		self.tooltipEnergy = None
		self.energyEmpty = None
		self.energyHungry = None
		self.energyFull = None

		self.energyGaugeBoard = None
		self.energyGaugeToolTip = None

	## Gauge
	def RefreshStatus(self):
		pointEnergy = player.GetStatus(player.ENERGY)
		if app.ENABLE_EXTENDED_BLEND_AFFECT:
			if pointEnergy != 0:
				leftTimeEnergy = 7200
			else:
				leftTimeEnergy = player.GetStatus(player.ENERGY_END_TIME) - app.GetGlobalTimeStamp()
		else:
			leftTimeEnergy = player.GetStatus(player.ENERGY_END_TIME) - app.GetGlobalTimeStamp()

		self.SetEnergy(pointEnergy, leftTimeEnergy, 7200)

	def SetEnergy(self, point, leftTime, maxTime):
		leftTime = max(leftTime, 0)
		maxTime = max(maxTime, 0)

		self.energyEmpty.Hide()
		self.energyHungry.Hide()
		self.energyFull.Hide()

		if leftTime == 0:
			self.energyEmpty.Show()
		elif ((leftTime * 100) / maxTime) < 15:
			self.energyHungry.Show()
		else:
			self.energyFull.Show()

		self.tooltipEnergy.SetText("%s" % (localeinfo.TOOLTIP_ENERGY(point)))

	def OnUpdate(self):
		if True == self.energyGaugeToolTip.IsIn():
			self.RefreshStatus()
			self.tooltipEnergy.Show()
		else:
			self.tooltipEnergy.Hide()

class ExpandedTaskBar(ui.ScriptWindow):
	BTN_NUM = 0

	if app.ENABLE_EVENT_MANAGER:
		BUTTON_EVENT_INFO = BTN_NUM
		BTN_NUM += 1

	if app.ENABLE_GROWTH_PET_SYSTEM:
		BUTTON_PET_INFO = BTN_NUM
		BTN_NUM += 1

	if app.ENABLE_SWITCHBOT:
		BUTTON_SWITCH_BOT = BTN_NUM
		BTN_NUM += 1

	if app.ENABLE_INGAME_WIKI:
		BUTTON_WIKI = BTN_NUM
		BTN_NUM += 1

	if app.ADVANCED_BATTLE_PASS:
		BUTTON_BP = BTN_NUM
		BTN_NUM += 1

	if app.FAST_EQUIP_WORLDARD:
		BUTTON_CHANGE_EQUIP = BTN_NUM
		BTN_NUM += 1

	if app.ENABLE_REWARD_SYSTEM:
		BUTTON_REWARD = BTN_NUM
		BTN_NUM += 1

	if app.USE_LOG_EXCHANGE:
		BUTTON_LOG = BTN_NUM
		BTN_NUM += 1
		
	if app.ENABLE_MISSION_QUEST:
		BUTTON_MISSION = BTN_NUM
		BTN_NUM += 1

	if app.ENABLE_NOTIFICATION_SYSTEM:
		BUTTON_NOTIFICATION = BTN_NUM
		BTN_NUM += 1

	BUTTON_SARYONG = BTN_NUM
	BTN_NUM += 1

	DEFAULT_Y_OFFSET = 74

	def __init__(self):
		ui.Window.__init__(self)
		self.SetWindowName("ExpandedTaskBar")
		self.chatOpen = False

	def __del__(self):
		ui.Window.__del__(self)

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "expandedtaskbar.py")
		except:
			import exception
			exception.Abort("ExpandedTaskBar.LoadWindow.LoadObject")

		self.expandedTaskBarBoard = self.GetChild("ExpanedTaskBar_Board")

		self.toggleButtonDict = {}

		if app.ENABLE_GROWTH_PET_SYSTEM:
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_PET_INFO] = self.GetChild("PetInfoButton")
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_PET_INFO].SetParent(self)

		if app.ENABLE_SWITCHBOT:
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_SWITCH_BOT] = self.GetChild("Switch_Bot")
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_SWITCH_BOT].SetParent(self)

		if app.ENABLE_INGAME_WIKI:
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_WIKI] = self.GetChild("WikiInfoButton")
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_WIKI].SetParent(self)

		if app.ADVANCED_BATTLE_PASS:
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_BP] = self.GetChild("bp_btn")
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_BP].SetParent(self)

		if app.ENABLE_EVENT_MANAGER:
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_EVENT_INFO] = self.GetChild("EventInfoButton")
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_EVENT_INFO].SetParent(self)


		if app.FAST_EQUIP_WORLDARD:
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_CHANGE_EQUIP] = self.GetChild("fast_equip_btn")
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_CHANGE_EQUIP].SetParent(self)

		if app.ENABLE_REWARD_SYSTEM:
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_REWARD] = self.GetChild("reward_btn")
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_REWARD].SetParent(self)

		if app.USE_LOG_EXCHANGE:
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_LOG] = self.GetChild("log_btn")
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_LOG].SetParent(self)

		if app.ENABLE_MISSION_QUEST:
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_MISSION] = self.GetChild("mission_btn")
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_MISSION].SetParent(self)

		if app.ENABLE_NOTIFICATION_SYSTEM:
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_NOTIFICATION] = self.GetChild("noti_btn")
			self.toggleButtonDict[ExpandedTaskBar.BUTTON_NOTIFICATION].SetParent(self)

		self.toggleButtonDict[ExpandedTaskBar.BUTTON_SARYONG] = self.GetChild("saryong_btn")
		self.toggleButtonDict[ExpandedTaskBar.BUTTON_SARYONG].SetParent(self)

	def RePositionButton(self):
		total_count = len(self.toggleButtonDict)
		quotient = total_count /2
		remainder = total_count % 2

		window_x = (wndMgr.GetScreenWidth()/2 + 33) + (-36 * quotient)
		if 0 == remainder:
			window_x = window_x + 18

		window_y = wndMgr.GetScreenHeight() - self.DEFAULT_Y_OFFSET
		self.SetPosition( window_x, window_y )

		pos_x = 0
		pos_y = 0
		for k, v in self.toggleButtonDict.items():
			v.SetPosition( pos_x, pos_y)
			pos_x = pos_x + 36

	if app.ENABLE_WINDOW_RESIZE:
		def OnResize(self):
			self.RePositionButton()

	def OnChatOpen(self, chatTopY):
		self.chatOpen = True
		self.__UpdateYPosition(chatTopY)

	def OnChatClose(self):
		self.chatOpen = False
		self.__UpdateYPosition()

	def __UpdateYPosition(self, chatTopY=0):
		if self.chatOpen and chatTopY > 0:
			window_y = chatTopY - 37
		else:
			window_y = wndMgr.GetScreenHeight() - self.DEFAULT_Y_OFFSET

		(cur_x, cur_y) = self.GetLocalPosition()
		self.SetPosition(cur_x, window_y)
		self.SetTop()

	def SetTop(self):
		super(ExpandedTaskBar, self).SetTop()
		for button in self.toggleButtonDict.values():
			button.SetTop()

	def Show(self):
		ui.ScriptWindow.Show(self)

	def Close(self):
		self.chatOpen = False
		self.Hide()

	def SetToolTipText(self, eButton, text):
		self.toggleButtonDict[eButton].SetToolTipText(text)

	def SetToggleButtonEvent(self, eButton, kEventFunc):
		self.toggleButtonDict[eButton].SetEvent(kEventFunc)

	def OnPressEscapeKey(self):
		self.Close()
		return True

class TaskBar(ui.ScriptWindow):
	BUTTON_CHARACTER = 0
	BUTTON_INVENTORY = 1
	BUTTON_MESSENGER = 2
	BUTTON_SYSTEM = 3
	BUTTON_CHAT = 4
	BUTTON_EXPAND = 4
	# BUTTON_EXPAND_MONEY = 5

	if app.BL_REMOTE_SHOP:
		BUTTON_REMOTE_SHOP = 6

	if app.USE_OFFLINESHOP:
		BUTTON_OFFLINE_SHOP = 7

	if app.ENABLE_ANTI_MULTIPLE_FARM:
		BUTTON_ANTI_MULTIPLE_FARM = 8

	if app.ENABLE_PARTY_FINDER:
		BUTTON_PARTY_FINDER = 9

	IS_EXPANDED = False

	MOUSE_BUTTON_LEFT = 0
	MOUSE_BUTTON_RIGHT = 1
	NONE = 255

	LAST_EVENT = 0

	EVENT_MOVE = LAST_EVENT
	LAST_EVENT += 1

	EVENT_ATTACK = LAST_EVENT
	LAST_EVENT += 1

	EVENT_MOVE_AND_ATTACK = LAST_EVENT
	LAST_EVENT += 1

	EVENT_CAMERA = LAST_EVENT
	LAST_EVENT += 1

	EVENT_SKILL = LAST_EVENT
	LAST_EVENT += 1

	EVENT_AUTO = LAST_EVENT
	LAST_EVENT += 1

	if app.AUTO_HUNT_RUBINUM:
		EVENT_AUTO_QUEUE = LAST_EVENT
		LAST_EVENT += 1
		EVENT_AUTO_QUEUE_AREA = LAST_EVENT
		LAST_EVENT += 1

	GAUGE_WIDTH = 95
	GAUGE_HEIGHT = 13

	QUICKPAGE_NUMBER_FILENAME = [
		"d:/ymir work/ui/game/taskbar/1.sub",
		"d:/ymir work/ui/game/taskbar/2.sub",
		"d:/ymir work/ui/game/taskbar/3.sub",
		"d:/ymir work/ui/game/taskbar/4.sub",
	]

	# Gift icon show and hide
	def ShowGift(self):
		if not localeinfo.IsBRAZIL():
			self.wndGiftBox.Show()

	def HideGift(self):
		self.wndGiftBox.Hide()

	class TextToolTip(ui.Window):
		def __init__(self):
			ui.Window.__init__(self, "TOP_MOST")

			textLine = ui.TextLine()
			textLine.SetParent(self)
			textLine.SetHorizontalAlignCenter()
			textLine.SetOutline()
			textLine.Show()
			self.textLine = textLine

		def __del__(self):
			ui.Window.__del__(self)
			self.textLine = None

		def SetText(self, text):
			self.textLine.SetText(text)

		def OnRender(self):
			(mouseX, mouseY) = wndMgr.GetMousePosition()
			self.textLine.SetPosition(mouseX, mouseY - 15)

	class SkillButton(ui.SlotWindow):
		def __init__(self):
			ui.SlotWindow.__init__(self)

			self.event = None
			self.arg = None

			self.slotIndex = 0
			self.skillIndex = 0

			slotIndex = 0
			wndMgr.SetSlotBaseImage(self.hWnd, "d:/ymir work/ui/public/slot_base.sub", 1.0, 1.0, 1.0, 1.0)
			wndMgr.AppendSlot(self.hWnd, slotIndex, 0, 0, 32, 32)
			self.SetCoverButton(slotIndex, "d:/ymir work/ui/public/slot_cover_button_01.sub",\
				"d:/ymir work/ui/public/slot_cover_button_02.sub",\
				"d:/ymir work/ui/public/slot_cover_button_03.sub",\
				"d:/ymir work/ui/public/slot_cover_button_04.sub", True, False)
			self.SetSize(32, 32)

		def __del__(self):
			ui.SlotWindow.__del__(self)

		def Destroy(self):
			if 0 != self.tooltipSkill:
				self.tooltipSkill.HideToolTip()

		def RefreshSkill(self):
			if 0 != self.slotIndex:
				self.SetSkill(self.slotIndex)

		def SetSkillToolTip(self, tooltip):
			self.tooltipSkill = tooltip

		def SetSkill(self, skillSlotNumber):
			slotNumber = 0
			skillIndex = player.GetSkillIndex(skillSlotNumber)
			skillGrade = player.GetSkillGrade(skillSlotNumber)
			skillLevel = player.GetSkillLevel(skillSlotNumber)
			skillType = skill.GetSkillType(skillIndex)

			self.skillIndex = skillIndex
			if 0 == self.skillIndex:
				self.ClearSlot(slotNumber)
				return

			self.slotIndex = skillSlotNumber

			self.SetSkillSlotNew(slotNumber, skillIndex, skillGrade, skillLevel)
			self.SetSlotCountNew(slotNumber, skillGrade, skillLevel)

			if player.IsSkillCoolTime(skillSlotNumber):
				(coolTime, elapsedTime) = player.GetSkillCoolTime(skillSlotNumber)
				self.SetSlotCoolTime(slotNumber, coolTime, elapsedTime)

			if player.IsSkillActive(skillSlotNumber):
				self.ActivateSlot(slotNumber)

		def SetSkillEvent(self, event, arg=0):
			self.event = event
			self.arg = arg

		def GetSkillIndex(self):
			return self.skillIndex

		def GetSlotIndex(self):
			return self.slotIndex

		def Activate(self, coolTime):
			self.SetSlotCoolTime(0, coolTime)

			if skill.IsToggleSkill(self.skillIndex):
				self.ActivateSlot(0)

		def Deactivate(self):
			if skill.IsToggleSkill(self.skillIndex):
				self.DeactivateSlot(0)

		def OnOverInItem(self, dummy):
			self.tooltipSkill.SetSkill(self.skillIndex)

		def OnOverOutItem(self):
			self.tooltipSkill.HideToolTip()

		def OnSelectItemSlot(self, dummy):
			if 0 != self.event:
				if 0 != self.arg:
					self.event(self.arg)
				else:
					self.event()

	def __init__(self):
		#print "NEW TASKBAR -----------------------------------------------------------------------------"

		ui.ScriptWindow.__init__(self, "TOP_MOST")

		self.quickPageNumImageBox = None
		self.tooltipItem = None
		self.tooltipSkill = None
		self.mouseModeButtonList = [ ui.ScriptWindow("TOP_MOST"), ui.ScriptWindow("TOP_MOST") ]

		if app.ENABLE_HEART_BEAT_MALL:
			self.heartBeat = False

		self.tooltipHP = self.TextToolTip()
		self.tooltipHP.Show()
		self.tooltipSP = self.TextToolTip()
		self.tooltipSP.Show()
		self.tooltipST = self.TextToolTip()
		self.tooltipST.Show()
		self.tooltipEXP = self.TextToolTip()
		self.tooltipEXP.Show()

		if app.ENABLE_ANTI_MULTIPLE_FARM:
			self.anti_farm_info = None

		self.skillCategoryNameList = [ "ACTIVE_1", "ACTIVE_2", "ACTIVE_3" ]
		self.skillPageStartSlotIndexDict = {
			"ACTIVE_1" : 1,
			"ACTIVE_2" : 21,
			"ACTIVE_3" : 41,
		}

		self.selectSkillButtonList = []

		self.lastUpdateQuickSlot = 0
		self.SetWindowName("TaskBar")

	def __del__(self):
		#print "---------------------------------------------------------------------------- DELETE TASKBAR"
		ui.ScriptWindow.__del__(self)

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()

			if constinfo.IN_GAME_SHOP_ENABLE:
				if app.ENABLE_GEM_SYSTEM:
					pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "newtaskbar.py")
				else:
					pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "TaskBar.py")
			else:
				if app.ENABLE_GEM_SYSTEM:
					pyScrLoader.LoadScriptFile(self, uiscriptlocale.LOCALE_UISCRIPT_PATH + "newtaskbar.py")
				else:
					pyScrLoader.LoadScriptFile(self, "UIScript/TaskBar.py")

			pyScrLoader.LoadScriptFile(self.mouseModeButtonList[self.MOUSE_BUTTON_LEFT], "UIScript/MouseButtonWindow.py")
			pyScrLoader.LoadScriptFile(self.mouseModeButtonList[self.MOUSE_BUTTON_RIGHT], "UIScript/RightMouseButtonWindow.py")
		except:
			import exception
			exception.Abort("TaskBar.LoadWindow.LoadObject")

		self.quickslot = []
		self.quickslot.append(self.GetChild("quick_slot_1"))
		self.quickslot.append(self.GetChild("quick_slot_2"))
		for slot in self.quickslot:
			slot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
			slot.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptyQuickSlot))
			slot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemQuickSlot))
			slot.SetUnselectItemSlotEvent(ui.__mem_func__(self.UnselectItemQuickSlot))
			slot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
			slot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		toggleButtonDict = {}
		toggleButtonDict[TaskBar.BUTTON_CHARACTER] = self.GetChild("CharacterButton")
		toggleButtonDict[TaskBar.BUTTON_INVENTORY] = self.GetChild("InventoryButton")
		toggleButtonDict[TaskBar.BUTTON_MESSENGER] = self.GetChild("MessengerButton")
		uibadge.Attach("messenger", toggleButtonDict[TaskBar.BUTTON_MESSENGER])
		toggleButtonDict[TaskBar.BUTTON_SYSTEM] = self.GetChild("SystemButton")

		try:
			toggleButtonDict[TaskBar.BUTTON_CHAT]=self.GetChild("ChatButton")
		except:
			toggleButtonDict[TaskBar.BUTTON_EXPAND]=self.GetChild("ExpandButton")
			TaskBar.IS_EXPANDED = True

		# toggleButtonDict[TaskBar.BUTTON_EXPAND_MONEY] = self.GetChild("ExpandMoneyButton")
		self.GetChild("ExpandMoneyButton").Hide()

		if app.BL_REMOTE_SHOP:
			toggleButtonDict[TaskBar.BUTTON_REMOTE_SHOP]=self.GetChild("RemoteShop")
			if osfinfo.BETA_PVP == True:
				self.GetChild("RemoteShop").Hide()

		if app.USE_OFFLINESHOP:
			toggleButtonDict[TaskBar.BUTTON_OFFLINE_SHOP]=self.GetChild("OfflineShop")
			if osfinfo.BETA_PVP == True:
				self.GetChild("OfflineShop").Hide()

		if app.ENABLE_ANTI_MULTIPLE_FARM:
			if osfinfo.BETA_PVP == True:
				pos_x, pos_y = (tuple(x-y for x,y in zip(toggleButtonDict[TaskBar.BUTTON_CHARACTER].GetLocalPosition(), [toggleButtonDict[TaskBar.BUTTON_CHARACTER].GetWidth() + 2, 0])))
			else:
				pos_x, pos_y = (tuple(x-y for x,y in zip(toggleButtonDict[TaskBar.BUTTON_OFFLINE_SHOP].GetLocalPosition(), [toggleButtonDict[TaskBar.BUTTON_OFFLINE_SHOP].GetWidth() + 2, 0])))

			tmpButton = ui.MakeButton(self, pos_x, pos_y, "", "d:/ymir work/ui/anti_multiple_farm/", "anti_multiple_farm_bt_norm.png", "anti_multiple_farm_bt_hover.png", "anti_multiple_farm_bt_down.png")
			toggleButtonDict[TaskBar.BUTTON_ANTI_MULTIPLE_FARM] = tmpButton
			self.anti_farm_info = ui.MakeImageBox(toggleButtonDict[TaskBar.BUTTON_ANTI_MULTIPLE_FARM],\
					"d:/ymir work/ui/pattern/visible_mark_01.tga", 0, 0)

		if app.ENABLE_PARTY_FINDER:
			toggleButtonDict[TaskBar.BUTTON_PARTY_FINDER] = self.GetChild("PartyFinderButton")
			uibadge.Attach("party_finder", toggleButtonDict[TaskBar.BUTTON_PARTY_FINDER])

		if localeinfo.IsARABIC():
			systemButton = toggleButtonDict[TaskBar.BUTTON_SYSTEM]
			if systemButton.ToolTipText:
				tx, ty = systemButton.ToolTipText.GetLocalPosition()
				tw = systemButton.ToolTipText.GetWidth() 
				systemButton.ToolTipText.SetPosition(-tw/2, ty)

		expGauge = []
		expGauge.append(self.GetChild("EXPGauge_01"))
		expGauge.append(self.GetChild("EXPGauge_02"))
		expGauge.append(self.GetChild("EXPGauge_03"))
		expGauge.append(self.GetChild("EXPGauge_04"))

		for exp in expGauge:
			exp.SetSize(0, 0)

		if app.ENABLE_CONQUEROR_LEVEL:
			newExpGauge = []
			newExpGauge.append(self.GetChild("NewExpGauge_01"))
			newExpGauge.append(self.GetChild("NewExpGauge_02"))
			newExpGauge.append(self.GetChild("NewExpGauge_03"))
			newExpGauge.append(self.GetChild("NewExpGauge_04"))

			for newExp in newExpGauge:
				newExp.SetSize(0, 0)
				newExp.Hide()

		self.quickPageNumImageBox=self.GetChild("QuickPageNumber")

		self.GetChild("QuickPageUpButton").SetEvent(ui.__mem_func__(self.__OnClickQuickPageUpButton))
		self.GetChild("QuickPageDownButton").SetEvent(ui.__mem_func__(self.__OnClickQuickPageDownButton))

		mouseLeftButtonModeButton = self.GetChild("LeftMouseButton")
		mouseRightButtonModeButton = self.GetChild("RightMouseButton")
		mouseLeftButtonModeButton.SetEvent(ui.__mem_func__(self.ToggleLeftMouseButtonModeWindow))
		mouseRightButtonModeButton.SetEvent(ui.__mem_func__(self.ToggleRightMouseButtonModeWindow))
		self.curMouseModeButton = [ mouseLeftButtonModeButton, mouseRightButtonModeButton ]

		(xLocalRight, yLocalRight) = mouseRightButtonModeButton.GetLocalPosition()
		self.curSkillButton = self.SkillButton()
		self.curSkillButton.SetParent(self)
		self.curSkillButton.SetPosition(xLocalRight, 3)
		self.curSkillButton.SetSkillEvent(ui.__mem_func__(self.ToggleRightMouseButtonModeWindow))
		self.curSkillButton.Hide()

		(xLeft, yLeft) = mouseLeftButtonModeButton.GetGlobalPosition()
		(xRight, yRight) = mouseRightButtonModeButton.GetGlobalPosition()
		leftModeButtonList = self.mouseModeButtonList[self.MOUSE_BUTTON_LEFT]
		leftModeButtonList.SetPosition(xLeft, yLeft - leftModeButtonList.GetHeight()-5)
		if app.ENABLE_WINDOW_RESIZE:
			leftModeButtonList.SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 + (xLeft - wndMgr.GetScreenWidth()/2), Expr("SCREEN_HEIGHT") + ((yLeft - leftModeButtonList.GetHeight()-5) - wndMgr.GetScreenHeight()))})
		rightModeButtonList = self.mouseModeButtonList[self.MOUSE_BUTTON_RIGHT]
		rightModeButtonList.SetPosition(xRight - rightModeButtonList.GetWidth() + 32, yRight - rightModeButtonList.GetHeight()-5)
		if app.ENABLE_WINDOW_RESIZE:
			rightModeButtonList.SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 + ((xRight - rightModeButtonList.GetWidth() + 32) - wndMgr.GetScreenWidth()/2), Expr("SCREEN_HEIGHT") + ((yRight - rightModeButtonList.GetHeight()-5) - wndMgr.GetScreenHeight()))})
		rightModeButtonList.GetChild("button_skill").SetEvent(lambda adir=self.MOUSE_BUTTON_RIGHT, aevent=self.EVENT_SKILL: self.SelectMouseButtonEvent(adir, aevent))
		rightModeButtonList.GetChild("button_skill").Hide()

		mouseImage = ui.ImageBox("TOP_MOST")
		mouseImage.AddFlag("float")
		mouseImage.LoadImage("d:/ymir work/ui/game/taskbar/mouse_button_camera_01.sub")
		mouseImage.SetPosition(xRight, wndMgr.GetScreenHeight() - 34)
		if app.ENABLE_WINDOW_RESIZE:
			mouseImage.SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 + (xRight - wndMgr.GetScreenWidth()/2), Expr("SCREEN_HEIGHT") - 34)})
		mouseImage.Hide()
		self.mouseImage = mouseImage

		dir = self.MOUSE_BUTTON_LEFT
		wnd = self.mouseModeButtonList[dir]
		wnd.GetChild("button_move_and_attack").SetEvent(lambda adir=dir, aevent=self.EVENT_MOVE_AND_ATTACK: self.SelectMouseButtonEvent(adir, aevent))
		wnd.GetChild("button_auto_attack").SetEvent(lambda adir=dir, aevent=self.EVENT_AUTO: self.SelectMouseButtonEvent(adir, aevent))
		wnd.GetChild("button_camera").SetEvent(lambda adir=dir, aevent=self.EVENT_CAMERA: self.SelectMouseButtonEvent(adir, aevent))

		if app.AUTO_HUNT_RUBINUM:
			wnd.GetChild("button_auto_attack_queue").SetEvent(lambda adir = dir, aevent = self.EVENT_AUTO_QUEUE: self.SelectMouseButtonEvent(adir, aevent))
			wnd.GetChild("button_auto_attack_queue_area").SetEvent(lambda adir = dir, aevent = self.EVENT_AUTO_QUEUE_AREA: self.SelectMouseButtonEvent(adir, aevent))
		else:
			wnd.GetChild("button_auto_attack_queue").Hide()
			wnd.GetChild("button_auto_attack_queue_area").Hide()

		dir = self.MOUSE_BUTTON_RIGHT
		wnd = self.mouseModeButtonList[dir]
		wnd.GetChild("button_move_and_attack").SetEvent(lambda adir=dir, aevent=self.EVENT_MOVE_AND_ATTACK: self.SelectMouseButtonEvent(adir, aevent))
		wnd.GetChild("button_camera").SetEvent(lambda adir=dir, aevent=self.EVENT_CAMERA: self.SelectMouseButtonEvent(adir, aevent))

		if app.AUTO_HUNT_RUBINUM:
			wnd.GetChild("button_auto_attack_queue").SetEvent(lambda adir = dir, aevent = self.EVENT_AUTO_QUEUE: self.SelectMouseButtonEvent(adir, aevent))
			wnd.GetChild("button_auto_attack_queue_area").SetEvent(lambda adir = dir, aevent = self.EVENT_AUTO_QUEUE_AREA: self.SelectMouseButtonEvent(adir, aevent))
		else:
			wnd.GetChild("button_auto_attack_queue").Hide()
			wnd.GetChild("button_auto_attack_queue_area").Hide()

		self.toggleButtonDict = toggleButtonDict
		self.expGauge = expGauge
		if app.ENABLE_CONQUEROR_LEVEL:
			self.newExpGauge = newExpGauge

		if constinfo.IN_GAME_SHOP_ENABLE:
			self.rampageGauge1 = self.GetChild("RampageGauge")
			self.rampageGauge1.OnMouseOverIn = ui.__mem_func__(self.__RampageGauge_OverIn)
			self.rampageGauge2 = self.GetChild("RampageGauge2")
			self.rampageGauge2.OnMouseOverOut = ui.__mem_func__(self.__RampageGauge_OverOut)
			self.rampageGauge2.OnMouseLeftButtonUp = ui.__mem_func__(self.__RampageGauge_Click)
			if app.ENABLE_HEART_BEAT_MALL:
				self.rampageGauge1.SetDelay(10)
				self.rampageGauge2.SetDelay(10)

				self.rampageGauge3 = self.GetChild("RampageGauge3")
				self.rampageGauge3.OnMouseOverIn = ui.__mem_func__(self.__RampageGauge_OverIn)
				self.rampageGauge3.SetDelay(10)

				self.rampageGauge4 = self.GetChild("RampageGauge4")
				self.rampageGauge4.OnMouseOverOut = ui.__mem_func__(self.__RampageGauge_OverOut)
				self.rampageGauge4.OnMouseLeftButtonUp = ui.__mem_func__(self.__RampageGauge_Click)
				self.rampageGauge4.SetDelay(10)

			print "[DEBUG]: constinfo.IN_GAME_SHOP_ENABLE / self.rampageGauge1",constinfo.IN_GAME_SHOP_ENABLE, self.rampageGauge1
			self.__RampageGauge_OverOut()

		self.hpGauge = self.GetChild("HPGauge")
		self.mpGauge = self.GetChild("SPGauge")
		self.stGauge = self.GetChild("STGauge")
		self.hpRecoveryGaugeBar = self.GetChild("HPRecoveryGaugeBar")
		self.spRecoveryGaugeBar = self.GetChild("SPRecoveryGaugeBar")

		if app.ENABLE_POISON_GAUGE_EFFECT:
			self.hpPoisonGauge = self.GetChild("HPPoisonGauge")
			self.hpPoisonRecoveryGaugeBar = self.GetChild("HPPoisonRecoveryGaugeBar")
			self.hpPoisonGauge.Hide()
			self.hpPoisonRecoveryGaugeBar.Hide()

		self.hpGaugeBoard = self.GetChild("HPGauge_Board")
		self.mpGaugeBoard = self.GetChild("SPGauge_Board")
		self.stGaugeBoard = self.GetChild("STGauge_Board")
		self.expGaugeBoard = self.GetChild("EXP_Gauge_Board")

		# Giftbox object
		wndGiftBox = GiftBox()
		wndGiftBox.LoadWindow()
		self.wndGiftBox = wndGiftBox

		self.__LoadMouseSettings()
		self.RefreshStatus()
		self.RefreshQuickSlot()

	def __RampageGauge_OverIn(self):
		print "rampage_over_in"
		if app.ENABLE_HEART_BEAT_MALL:
			if self.heartBeat:
				self.rampageGauge4.Show()
				self.rampageGauge3.Hide()

				self.rampageGauge1.Hide()
				self.rampageGauge2.Hide()
			else:
				self.rampageGauge2.Show()
				self.rampageGauge1.Hide()

				self.rampageGauge3.Hide()
				self.rampageGauge4.Hide()
		else:
			self.rampageGauge2.Show()
			self.rampageGauge1.Hide()

	def __RampageGauge_OverOut(self):
		print "rampage_over_out"
		if app.ENABLE_HEART_BEAT_MALL:
			if self.heartBeat:
				self.rampageGauge4.Hide()
				self.rampageGauge3.Show()

				self.rampageGauge1.Hide()
				self.rampageGauge2.Hide()
			else:
				self.rampageGauge2.Hide()
				self.rampageGauge1.Show()

				self.rampageGauge3.Hide()
				self.rampageGauge4.Hide()
		else:
			self.rampageGauge2.Hide()
			self.rampageGauge1.Show()

	def __RampageGauge_Click(self):
		print "rampage_up"
		if app.ENABLE_ITEMSHOP:
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.OpenItemShopWindow()
		# gift icon hide when click mall icon
		# self.wndGiftBox.Hide()

	def __LoadMouseSettings(self):
		try:
			LoadMouseButtonSettings()
			(mouseLeftButtonEvent, mouseRightButtonEvent) = GetMouseButtonSettings()
			if not self.__IsInSafeMouseButtonSettingRange(mouseLeftButtonEvent) or not self.__IsInSafeMouseButtonSettingRange(mouseRightButtonEvent):
				raise RuntimeError, "INVALID_MOUSE_BUTTON_SETTINGS"
		except:
			InitMouseButtonSettings(self.EVENT_AUTO, self.EVENT_CAMERA)
			(mouseLeftButtonEvent, mouseRightButtonEvent) = GetMouseButtonSettings()

		try:
			self.SelectMouseButtonEvent(self.MOUSE_BUTTON_LEFT, mouseLeftButtonEvent)
			self.SelectMouseButtonEvent(self.MOUSE_BUTTON_RIGHT, mouseRightButtonEvent)
		except:
			InitMouseButtonSettings(self.EVENT_AUTO, self.EVENT_CAMERA)
			(mouseLeftButtonEvent, mouseRightButtonEvent) = GetMouseButtonSettings()

			self.SelectMouseButtonEvent(self.MOUSE_BUTTON_LEFT, mouseLeftButtonEvent)
			self.SelectMouseButtonEvent(self.MOUSE_BUTTON_RIGHT, mouseRightButtonEvent)

	def __IsInSafeMouseButtonSettingRange(self, arg):
		return arg >= self.EVENT_MOVE and arg < self.LAST_EVENT#self.EVENT_AUTO_QUEUE

	def Destroy(self):
		SaveMouseButtonSettings()

		uibadge.ClearAll()
		self.ClearDictionary()
		self.mouseModeButtonList[0].ClearDictionary()
		self.mouseModeButtonList[1].ClearDictionary()
		self.mouseModeButtonList = []
		self.curMouseModeButton = []
		self.curSkillButton = None
		self.selectSkillButtonList = []

		self.expGauge = None
		if app.ENABLE_CONQUEROR_LEVEL:
			self.newExpGauge = None
		self.hpGauge = None
		self.mpGauge = None
		self.stGauge = None
		self.hpRecoveryGaugeBar = None
		self.spRecoveryGaugeBar = None

		if app.ENABLE_POISON_GAUGE_EFFECT:
			self.hpPoisonGauge = None
			self.hpPoisonRecoveryGaugeBar = None

		self.rampageGauge1 = None
		self.rampageGauge2 = None
		if app.ENABLE_HEART_BEAT_MALL:
			self.heartBeat = False

			self.rampageGauge3 = None
			self.rampageGauge4 = None

		self.tooltipItem = None
		self.tooltipSkill = None
		self.quickslot = []
		self.toggleButtonDict = {}

		self.hpGaugeBoard = None
		self.mpGaugeBoard = None
		self.stGaugeBoard = None
		self.expGaugeBoard = None

		self.tooltipHP = None
		self.tooltipSP = None
		self.tooltipST = None
		self.tooltipEXP = None

		self.mouseImage = None

	def __OnClickQuickPageUpButton(self):
		player.SetQuickPage(player.GetQuickPage()-1)

	def __OnClickQuickPageDownButton(self):
		player.SetQuickPage(player.GetQuickPage()+1)

	def SetToggleButtonEvent(self, eButton, kEventFunc):
		self.toggleButtonDict[eButton].SetEvent(kEventFunc)

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def SetSkillToolTip(self, tooltipSkill):
		self.tooltipSkill = tooltipSkill
		self.curSkillButton.SetSkillToolTip(self.tooltipSkill)

	## Mouse Image
	def ShowMouseImage(self):
		self.mouseImage.SetTop()
		self.mouseImage.Show()

	def HideMouseImage(self):
		player.SetQuickCameraMode(False)
		self.mouseImage.Hide()

	## Gauge
	def RefreshStatus(self):
		curHP = player.GetStatus(player.HP)
		maxHP = player.GetStatus(player.MAX_HP)
		curSP = player.GetStatus(player.SP)
		maxSP = player.GetStatus(player.MAX_SP)
		if app.ENABLE_CONQUEROR_LEVEL:
			if player.GetStatus(player.POINT_CONQUEROR_LEVEL) > 0:
				curEXP = unsigned32(player.GetStatus(player.POINT_CONQUEROR_EXP))
				nextEXP = unsigned32(player.GetStatus(player.POINT_CONQUEROR_NEXT_EXP))
			else:
				curEXP = unsigned32(player.GetStatus(player.EXP))
				nextEXP = unsigned32(player.GetStatus(player.NEXT_EXP))
		else:
			curEXP = unsigned32(player.GetStatus(player.EXP))
			nextEXP = unsigned32(player.GetStatus(player.NEXT_EXP))
		recoveryHP = player.GetStatus(player.HP_RECOVERY)
		recoverySP = player.GetStatus(player.SP_RECOVERY)

		self.RefreshStamina()

		self.SetHP(curHP, recoveryHP, maxHP)
		self.SetSP(curSP, recoverySP, maxSP)
		self.SetExperience(curEXP, nextEXP)

	def RefreshStamina(self):
		curST = player.GetStatus(player.STAMINA)
		maxST = player.GetStatus(player.MAX_STAMINA)
		self.SetST(curST, maxST)

	def RefreshSkill(self):
		self.curSkillButton.RefreshSkill()
		for button in self.selectSkillButtonList:
			button.RefreshSkill()

	if app.ENABLE_SKILL_COOLTIME_UPDATE:
		def SkillClearCoolTime(self, usedSlotIndex):
			QUICK_SLOT_SLOT_COUNT = 4
			slotIndex = 0
			for slotWindow in self.quickslot:
				for i in xrange(QUICK_SLOT_SLOT_COUNT):
					(Type, Position) = player.GetLocalQuickSlot(slotIndex)
					if Type == player.SLOT_TYPE_SKILL:
						if usedSlotIndex == Position:
							slotWindow.SetSlotCoolTime(slotIndex, 0)
							return
					slotIndex += 1

	def SetHP(self, curPoint, recoveryPoint, maxPoint):
		curPoint = min(curPoint, maxPoint)

		if app.ENABLE_POISON_GAUGE_EFFECT:
			isPoisoned = chrmgr.HasAffectByVID(player.GetMainCharacterIndex(), chr.AFFECT_POISON)
			if isPoisoned:
				self.hpGauge.Hide()
				self.hpPoisonGauge.Show()
			else:
				self.hpPoisonGauge.Hide()
				self.hpGauge.Show()

		if maxPoint > 0:
			self.hpGauge.SetPercentage(curPoint, maxPoint)
			if app.ENABLE_POISON_GAUGE_EFFECT:
				self.hpPoisonGauge.SetPercentage(curPoint, maxPoint)
			self.tooltipHP.SetText("%s : %d / %d" % (localeinfo.TASKBAR_HP, curPoint, maxPoint))

			if 0 == recoveryPoint:
				self.hpRecoveryGaugeBar.Hide()
				if app.ENABLE_POISON_GAUGE_EFFECT:
					self.hpPoisonRecoveryGaugeBar.Hide()
			else:
				destPoint = min(maxPoint, curPoint + recoveryPoint)
				newWidth = int(self.GAUGE_WIDTH * (float(destPoint) / float(maxPoint)))
				if app.ENABLE_POISON_GAUGE_EFFECT and isPoisoned:
					self.hpRecoveryGaugeBar.Hide()
					self.hpPoisonRecoveryGaugeBar.SetSize(newWidth, self.GAUGE_HEIGHT)
					self.hpPoisonRecoveryGaugeBar.Show()
				else:
					if app.ENABLE_POISON_GAUGE_EFFECT:
						self.hpPoisonRecoveryGaugeBar.Hide()
					self.hpRecoveryGaugeBar.SetSize(newWidth, self.GAUGE_HEIGHT)
					self.hpRecoveryGaugeBar.Show()

		if app.ENABLE_HEART_BEAT_MALL:
			self.heartBeat = True
			curPointPct = int(100 * float(curPoint) / float(maxPoint))
			heartBeats = [
				[ [0, 30], 1 ],
				[ [30, 40], 2 ],
				[ [40, 50], 3 ],
			]

			if curPointPct >= heartBeats[0][0][0] and curPointPct <= heartBeats[0][0][1]:
				self.rampageGauge1.SetDelay(heartBeats[0][1])
				self.rampageGauge2.SetDelay(heartBeats[0][1])
				self.rampageGauge3.SetDelay(heartBeats[0][1])
				self.rampageGauge4.SetDelay(heartBeats[0][1])
			elif curPointPct >= heartBeats[1][0][0] and curPointPct <= heartBeats[1][0][1]:
				self.rampageGauge1.SetDelay(heartBeats[1][1])
				self.rampageGauge2.SetDelay(heartBeats[1][1])
				self.rampageGauge3.SetDelay(heartBeats[1][1])
				self.rampageGauge4.SetDelay(heartBeats[1][1])
			elif curPointPct >= heartBeats[2][0][0] and curPointPct <= heartBeats[2][0][1]:
				self.rampageGauge1.SetDelay(heartBeats[2][1])
				self.rampageGauge2.SetDelay(heartBeats[2][1])
				self.rampageGauge3.SetDelay(heartBeats[2][1])
				self.rampageGauge4.SetDelay(heartBeats[2][1])
			else:
				if curPointPct <= 0:
					self.rampageGauge1.SetDelay(99)
					self.rampageGauge2.SetDelay(99)
					self.rampageGauge3.SetDelay(99)
					self.rampageGauge4.SetDelay(99)
				else:
					self.heartBeat = False

					self.rampageGauge1.SetDelay(10)
					self.rampageGauge2.SetDelay(10)
					self.rampageGauge3.SetDelay(10)
					self.rampageGauge4.SetDelay(10)

			if self.heartBeat:
				self.rampageGauge1.Hide()
				self.rampageGauge2.Hide()
				self.rampageGauge3.Show()
				self.rampageGauge4.Show()
			else:
				self.rampageGauge1.Show()
				self.rampageGauge2.Show()
				self.rampageGauge3.Hide()
				self.rampageGauge4.Hide()

	def SetSP(self, curPoint, recoveryPoint, maxPoint):
		curPoint = min(curPoint, maxPoint)
		if maxPoint > 0:
			self.mpGauge.SetPercentage(curPoint, maxPoint)
			self.tooltipSP.SetText("%s : %d / %d" % (localeinfo.TASKBAR_SP, curPoint, maxPoint))

			if 0 == recoveryPoint:
				self.spRecoveryGaugeBar.Hide()
			else:
				destPoint = min(maxPoint, curPoint + recoveryPoint)
				newWidth = int(self.GAUGE_WIDTH * (float(destPoint) / float(maxPoint)))
				self.spRecoveryGaugeBar.SetSize(newWidth, self.GAUGE_HEIGHT)
				self.spRecoveryGaugeBar.Show()

	def SetST(self, curPoint, maxPoint):
		curPoint = min(curPoint, maxPoint)
		if maxPoint > 0:
			self.stGauge.SetPercentage(curPoint, maxPoint)
			self.tooltipST.SetText("%s : %d / %d" % (localeinfo.TASKBAR_ST, curPoint, maxPoint))

	def SetExperience(self, curPoint, maxPoint):
		if app.USE_ANTI_EXP:
			for i in self.expGauge:
				if player.CanReceiveExp():
					i.SetDiffuseColor(1.0, 1.0, 1.0, 1.0)
				else:
					i.SetDiffuseColor(113.0 / 255.0, 128.0 / 255.0, 147.0 / 255.0, 1.0)

			if app.ENABLE_CONQUEROR_LEVEL:
				for i in self.newExpGauge:
					if player.CanReceiveExp():
						i.SetDiffuseColor(1.0, 1.0, 1.0, 1.0)
					else:
						i.SetDiffuseColor(223.0 / 255.0, 230.0 / 255.0, 233.0 / 255.0, 1.0)

		curPoint = min(curPoint, maxPoint)
		curPoint = max(curPoint, 0)
		maxPoint = max(maxPoint, 0)

		quarterPoint = maxPoint / 4
		FullCount = 0

		if 0 != quarterPoint:
			FullCount = min(4, curPoint / quarterPoint)

		if app.ENABLE_CONQUEROR_LEVEL:
			if player.GetStatus(player.POINT_CONQUEROR_LEVEL) > 0:
				for i in xrange(4):
					self.expGauge[i].Hide()
					self.newExpGauge[i].Hide()

				for i in xrange(FullCount):
					self.newExpGauge[i].SetRenderingRect(0.0, 0.0, 0.0, 0.0)
					self.newExpGauge[i].Show()

				if 0 != quarterPoint:
					if FullCount < 4:
						Percentage = float(curPoint % quarterPoint) / quarterPoint - 1.0
						self.newExpGauge[FullCount].SetRenderingRect(0.0, Percentage, 0.0, 0.0)
						self.newExpGauge[FullCount].Show()

				self.tooltipEXP.SetText("%s : %.2f%%" % (localeinfo.TASKBAR_EXP, float(curPoint) / max(1, float(maxPoint)) * 100))
				return
			else:
				for i in xrange(4):
					self.newExpGauge[i].Hide()

		for i in xrange(4):
			self.expGauge[i].Hide()

		for i in xrange(FullCount):
			self.expGauge[i].SetRenderingRect(0.0, 0.0, 0.0, 0.0)
			self.expGauge[i].Show()

		if 0 != quarterPoint:
			if FullCount < 4:
				Percentage = float(curPoint % quarterPoint) / quarterPoint - 1.0
				self.expGauge[FullCount].SetRenderingRect(0.0, Percentage, 0.0, 0.0)
				self.expGauge[FullCount].Show()

		#####
		self.tooltipEXP.SetText("%s : %.2f%%" % (localeinfo.TASKBAR_EXP, float(curPoint) / max(1, float(maxPoint)) * 100))

	## QuickSlot
	def RefreshQuickSlot(self):
		pageNum = player.GetQuickPage()

		try:
			self.quickPageNumImageBox.LoadImage(TaskBar.QUICKPAGE_NUMBER_FILENAME[pageNum])
		except:
			pass

		startNumber = 0
		for slot in self.quickslot:

			for i in xrange(4):
				slotNumber = i+startNumber

				(Type, Position) = player.GetLocalQuickSlot(slotNumber)

				if player.SLOT_TYPE_NONE == Type:
					slot.ClearSlot(slotNumber)
					continue

				if player.SLOT_TYPE_INVENTORY == Type:
					itemIndex = player.GetItemIndex(Position)
					itemCount = player.GetItemCount(Position)
					if itemCount <= 1:
						itemCount = 0

					if constinfo.IS_AUTO_POTION(itemIndex):
						metinSocket = [player.GetItemMetinSocket(Position, j) for j in xrange(player.METIN_SOCKET_MAX_NUM)]

						if 0 != int(metinSocket[0]):
							slot.ActivateSlot(slotNumber)
						else:
							slot.DeactivateSlot(slotNumber)

					if osfinfo.IS_PET_SEAL(itemIndex):
						metinSocket = [player.GetItemMetinSocket(Position, j) for j in xrange(player.METIN_SOCKET_MAX_NUM)]

						if 0 != int(metinSocket[1]):
							slot.ActivateSlot(slotNumber)
						else:
							slot.DeactivateSlot(slotNumber)

					if app.ENABLE_SOUL_SYSTEM:
						if item.IsSoulItem(itemIndex):
							metinSocket = [player.GetItemMetinSocket(window, Position, j) for j in xrange(player.METIN_SOCKET_MAX_NUM)]

							if 0 != int(metinSocket[1]):
								slot.ActivateSlot(slotNumber)
							else:
								slot.DeactivateSlot(slotNumber)

					if app.ENABLE_GROWTH_PET_SYSTEM:
						if constinfo.IS_PET_ITEM(itemIndex):
							self.__SetCoolTimePetItemSlot(slot, Position, slotNumber, itemIndex)
							
							slot.DeactivateSlot(slotNumber)
							
							active_id = player.GetActivePetItemId()
							if active_id and active_id == player.GetItemMetinSocket(Position, 2):
								slot.ActivateSlot(slotNumber)

					slot.SetItemSlot(slotNumber, itemIndex, itemCount)

				elif player.SLOT_TYPE_SKILL == Type:
					skillIndex = player.GetSkillIndex(Position)
					if 0 == skillIndex:
						slot.ClearSlot(slotNumber)
						continue

					skillType = skill.GetSkillType(skillIndex)
					if skill.SKILL_TYPE_GUILD == skillType:
						skillGrade = 0
						skillLevel = guild.GetSkillLevel(Position)
					else:
						skillGrade = player.GetSkillGrade(Position)
						skillLevel = player.GetSkillLevel(Position)

					slot.SetSkillSlotNew(slotNumber, skillIndex, skillGrade, skillLevel)
					slot.SetSlotCountNew(slotNumber, skillGrade, skillLevel)
					slot.SetCoverButton(slotNumber)

					if player.IsSkillCoolTime(Position):
						(coolTime, elapsedTime) = player.GetSkillCoolTime(Position)
						slot.SetSlotCoolTime(slotNumber, coolTime, elapsedTime)

					if player.IsSkillActive(Position):
						slot.ActivateSlot(slotNumber)

				elif player.SLOT_TYPE_EMOTION == Type:

					emotionIndex = Position
					slot.SetEmotionSlot(slotNumber, emotionIndex)
					slot.SetCoverButton(slotNumber)
					slot.SetSlotCount(slotNumber, 0)

			slot.RefreshSlot()
			startNumber += 4

	if app.ENABLE_GROWTH_PET_SYSTEM:		
		def __SetCoolTimePetItemSlot(self, slot, Position, slotNumber, itemVnum):
		
			item.SelectItem(itemVnum)
			itemSubType = item.GetItemSubType()
		
			if itemSubType not in [item.PET_UPBRINGING, item.PET_BAG]:
				return
				
			if itemSubType == item.PET_BAG:
				id = player.GetItemMetinSocket(Position, 2)
				if id == 0:
					return
			
			(limitType, limitValue) = item.GetLimit(0)

			if itemSubType == item.PET_UPBRINGING:
				limitValue = player.GetItemMetinSocket(Position, 1)
					
			if limitType in [item.LIMIT_REAL_TIME, item.LIMIT_REAL_TIME_START_FIRST_USE]:
				sock_time   = player.GetItemMetinSocket(Position, 0)
				remain_time = max( 0, sock_time - app.GetGlobalTimeStamp() )
				
				slot.SetSlotCoolTimeInverse(slotNumber, limitValue, limitValue - remain_time)

	def canAddQuickSlot(self, Type, slotNumber):
		if player.SLOT_TYPE_INVENTORY == Type:
			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM and slotNumber >= item.SKILL_BOOK_INVENTORY_SLOT_START:
				return True
			else:
				itemIndex = player.GetItemIndex(slotNumber)
				return item.CanAddToQuickSlotItem(itemIndex)

		return True

	def AddQuickSlot(self, localSlotIndex):
		AttachedSlotType = mousemodule.mouseController.GetAttachedType()
		AttachedSlotNumber = mousemodule.mouseController.GetAttachedSlotNumber()
		AttachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()

		if player.SLOT_TYPE_QUICK_SLOT == AttachedSlotType:
			player.RequestMoveGlobalQuickSlotToLocalQuickSlot(AttachedSlotNumber, localSlotIndex)

		elif player.SLOT_TYPE_EMOTION == AttachedSlotType:
			player.RequestAddLocalQuickSlot(localSlotIndex, AttachedSlotType, AttachedItemIndex)

		elif True == self.canAddQuickSlot(AttachedSlotType, AttachedSlotNumber):
			## Online Code
			player.RequestAddLocalQuickSlot(localSlotIndex, AttachedSlotType, AttachedSlotNumber)

		mousemodule.mouseController.DeattachObject()
		self.RefreshQuickSlot()

	def SelectEmptyQuickSlot(self, slotIndex):
		if True == mousemodule.mouseController.isAttached():
			self.AddQuickSlot(slotIndex)

	def SelectItemQuickSlot(self, localQuickSlotIndex):
		if True == mousemodule.mouseController.isAttached():
			self.AddQuickSlot(localQuickSlotIndex)
		else:
			globalQuickSlotIndex=player.LocalQuickSlotIndexToGlobalQuickSlotIndex(localQuickSlotIndex)
			mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_QUICK_SLOT, globalQuickSlotIndex, globalQuickSlotIndex)

	def UnselectItemQuickSlot(self, localSlotIndex):
		if False == mousemodule.mouseController.isAttached():
			player.RequestUseLocalQuickSlot(localSlotIndex)
			return
		elif mousemodule.mouseController.isAttached():
			mousemodule.mouseController.DeattachObject()
			return

	def OnUseSkill(self, usedSlotIndex, coolTime):
		QUICK_SLOT_SLOT_COUNT = 4
		slotIndex = 0

		## Current Skill Button
		if usedSlotIndex == self.curSkillButton.GetSlotIndex():
			self.curSkillButton.Activate(coolTime)

		## Quick Slot
		for slotWindow in self.quickslot:
			for i in xrange(QUICK_SLOT_SLOT_COUNT):
				(Type, Position) = player.GetLocalQuickSlot(slotIndex)

				if Type == player.SLOT_TYPE_SKILL:
					if usedSlotIndex == Position:
						slotWindow.SetSlotCoolTime(slotIndex, coolTime)
						return

				slotIndex += 1

	def OnActivateSkill(self, usedSlotIndex):
		slotIndex = 0

		## Current Skill Button
		if usedSlotIndex == self.curSkillButton.GetSlotIndex():
			self.curSkillButton.Deactivate()

		## Quick Slot
		for slotWindow in self.quickslot:
			for i in xrange(4):
				(Type, Position) = player.GetLocalQuickSlot(slotIndex)

				if Type == player.SLOT_TYPE_SKILL:
					if usedSlotIndex == Position:
						slotWindow.ActivateSlot(slotIndex)
						return

				slotIndex += 1

	def OnDeactivateSkill(self, usedSlotIndex):
		slotIndex = 0

		## Current Skill Button
		if usedSlotIndex == self.curSkillButton.GetSlotIndex():
			self.curSkillButton.Deactivate()

		## Quick Slot
		for slotWindow in self.quickslot:
			for i in xrange(4):
				(Type, Position) = player.GetLocalQuickSlot(slotIndex)

				if Type == player.SLOT_TYPE_SKILL:
					if usedSlotIndex == Position:
						slotWindow.DeactivateSlot(slotIndex)
						return

				slotIndex += 1

	## ToolTip
	def OverInItem(self, slotNumber):
		if mousemodule.mouseController.isAttached():
			return

		(Type, Position) = player.GetLocalQuickSlot(slotNumber)

		if player.SLOT_TYPE_INVENTORY == Type:
			self.tooltipItem.SetInventoryItem(Position)
			self.tooltipSkill.HideToolTip()

		elif player.SLOT_TYPE_SKILL == Type:
			skillIndex = player.GetSkillIndex(Position)
			skillType = skill.GetSkillType(skillIndex)

			if skill.SKILL_TYPE_GUILD == skillType:
				skillGrade = 0
				skillLevel = guild.GetSkillLevel(Position)

			else:
				skillGrade = player.GetSkillGrade(Position)
				skillLevel = player.GetSkillLevel(Position)

			self.tooltipSkill.SetSkillNew(Position, skillIndex, skillGrade, skillLevel)
			self.tooltipItem.HideToolTip()

	def OverOutItem(self):
		if 0 != self.tooltipItem:
			self.tooltipItem.HideToolTip()
		if 0 != self.tooltipSkill:
			self.tooltipSkill.HideToolTip()

	def OnUpdate(self):
		if app.GetGlobalTime() - self.lastUpdateQuickSlot > 500:
			self.lastUpdateQuickSlot = app.GetGlobalTime()
			self.RefreshQuickSlot()

		if True == self.hpGaugeBoard.IsIn():
			self.tooltipHP.Show()
		else:
			self.tooltipHP.Hide()

		if True == self.mpGaugeBoard.IsIn():
			self.tooltipSP.Show()
		else:
			self.tooltipSP.Hide()

		if True == self.stGaugeBoard.IsIn():
			self.tooltipST.Show()
		else:
			self.tooltipST.Hide()

		if True == self.expGaugeBoard.IsIn():
			self.tooltipEXP.Show()
		else:
			self.tooltipEXP.Hide()

	## Skill
	def ToggleLeftMouseButtonModeWindow(self):
		wndMouseButtonMode = self.mouseModeButtonList[self.MOUSE_BUTTON_LEFT]

		if True == wndMouseButtonMode.IsShow():
			wndMouseButtonMode.Hide()
		else:
			wndMouseButtonMode.Show()

	def ToggleRightMouseButtonModeWindow(self):
		wndMouseButtonMode = self.mouseModeButtonList[self.MOUSE_BUTTON_RIGHT]

		if True == wndMouseButtonMode.IsShow():
			wndMouseButtonMode.Hide()
			self.CloseSelectSkill()
		else:
			wndMouseButtonMode.Show()
			self.OpenSelectSkill()

	def OpenSelectSkill(self):
		PAGE_SLOT_COUNT = 6

		(xSkillButton, y) = self.curSkillButton.GetGlobalPosition()
		y -= (37 + 32 + 1)

		for key in self.skillCategoryNameList:
			appendCount = 0
			startNumber = self.skillPageStartSlotIndexDict[key]
			x = xSkillButton

			getSkillIndex=player.GetSkillIndex
			getSkillLevel=player.GetSkillLevel

			for i in xrange(PAGE_SLOT_COUNT):
				skillIndex = getSkillIndex(startNumber+i)
				skillLevel = getSkillLevel(startNumber+i)

				if 0 == skillIndex:
					continue
				if 0 == skillLevel:
					continue
				if skill.IsStandingSkill(skillIndex):
					continue

				skillButton = self.SkillButton()
				skillButton.SetSkill(startNumber+i)
				skillButton.SetPosition(x, y)
				skillButton.SetSkillEvent(ui.__mem_func__(self.CloseSelectSkill), startNumber+i+1)
				skillButton.SetSkillToolTip(self.tooltipSkill)
				skillButton.SetTop()
				skillButton.Show()
				self.selectSkillButtonList.append(skillButton)

				appendCount += 1
				x -= 32

			if appendCount > 0:
				y -= 32

	def CloseSelectSkill(self, slotIndex=-1):
		self.mouseModeButtonList[self.MOUSE_BUTTON_RIGHT].Hide()
		for button in self.selectSkillButtonList:
			button.Destroy()

		self.selectSkillButtonList = []

		if -1 != slotIndex:
			self.curSkillButton.Show()
			self.curMouseModeButton[self.MOUSE_BUTTON_RIGHT].Hide()
			player.SetMouseFunc(player.MBT_RIGHT, player.MBF_SKILL)
			player.ChangeCurrentSkillNumberOnly(slotIndex-1)
		else:
			self.curSkillButton.Hide()
			self.curMouseModeButton[self.MOUSE_BUTTON_RIGHT].Show()

	def SelectMouseButtonEvent(self, dir, event):
		SetMouseButtonSetting(dir, event)

		self.CloseSelectSkill()
		self.mouseModeButtonList[dir].Hide()

		btn = 0
		type = self.NONE
		func = self.NONE
		tooltip_text = ""

		if self.MOUSE_BUTTON_LEFT == dir:
			type = player.MBT_LEFT

		elif self.MOUSE_BUTTON_RIGHT == dir:
			type = player.MBT_RIGHT

		if self.EVENT_MOVE == event:
			btn = self.mouseModeButtonList[dir].GetChild("button_move")
			func = player.MBF_MOVE
			tooltip_text = localeinfo.TASKBAR_MOVE
		elif self.EVENT_ATTACK == event:
			btn = self.mouseModeButtonList[dir].GetChild("button_attack")
			func = player.MBF_ATTACK
			tooltip_text = localeinfo.TASKBAR_ATTACK
		elif self.EVENT_AUTO == event:
			btn = self.mouseModeButtonList[dir].GetChild("button_auto_attack")
			func = player.MBF_AUTO
			tooltip_text = localeinfo.TASKBAR_AUTO
		elif self.EVENT_MOVE_AND_ATTACK == event:
			btn = self.mouseModeButtonList[dir].GetChild("button_move_and_attack")
			func = player.MBF_SMART
			tooltip_text = localeinfo.TASKBAR_ATTACK
		elif self.EVENT_CAMERA == event:
			btn = self.mouseModeButtonList[dir].GetChild("button_camera")
			func = player.MBF_CAMERA
			tooltip_text = localeinfo.TASKBAR_CAMERA
		elif self.EVENT_SKILL == event:
			btn = self.mouseModeButtonList[dir].GetChild("button_skill")
			func = player.MBF_SKILL
			tooltip_text = localeinfo.TASKBAR_SKILL
		elif app.AUTO_HUNT_RUBINUM and event == self.EVENT_AUTO_QUEUE:
			btn = self.mouseModeButtonList[dir].GetChild("button_auto_attack_queue")
			func = player.MBF_AUTO_QUEUE
			tooltip_text = getattr(localeinfo, "TASKBAR_AUTO_QUEUE_LEFT", localeinfo.TASKBAR_AUTO_QUEUE) if dir == self.MOUSE_BUTTON_LEFT else localeinfo.TASKBAR_AUTO_QUEUE
		elif app.AUTO_HUNT_RUBINUM and event == self.EVENT_AUTO_QUEUE_AREA:
			btn = self.mouseModeButtonList[dir].GetChild("button_auto_attack_queue_area")
			func = player.MBF_AUTO_QUEUE_AREA
			tooltip_text = getattr(localeinfo, "TASKBAR_AUTO_QUEUE_AREA", localeinfo.TASKBAR_AUTO_QUEUE)

		if 0 != btn:
			self.curMouseModeButton[dir].SetToolTipText(tooltip_text, 0, -18)
			self.curMouseModeButton[dir].SetUpVisual(btn.GetUpVisualFileName())
			self.curMouseModeButton[dir].SetOverVisual(btn.GetOverVisualFileName())
			self.curMouseModeButton[dir].SetDownVisual(btn.GetDownVisualFileName())
			self.curMouseModeButton[dir].Show()

		player.SetMouseFunc(type, func)

	def OnChangeCurrentSkill(self, skillSlotNumber):
		self.curSkillButton.SetSkill(skillSlotNumber)
		self.curSkillButton.Show()
		self.curMouseModeButton[self.MOUSE_BUTTON_RIGHT].Hide()

	if app.ENABLE_ANTI_MULTIPLE_FARM:
		def ReloadAntiMultipleFarmState(self):
			if not self.anti_farm_info:
				return
			
			playerState = anti_multiple_farm.GetAntiFarmMainPlayerStatus()
			self.anti_farm_info.LoadImage(MULTIPLE_FARM_STATE_IMAGES[playerState])

class ExpandedMoneyTaskBar(ui.ScriptWindow):
	if app.USE_EXCHANGE_CURRENCY:
		def OnCloseExchangeCurrencyDialog(self):
			if self.exchange_currency_dlg:
				self.exchange_currency_dlg.Close()

		def OnAcceptExchangeCurrencyDialog(self):
			if self.exchange_currency_dlg:
				exchangeAmount = self.exchange_currency_dlg.GetCount()
				if exchangeAmount > 0:
					net.SendExchangeCurrency(exchangeAmount, self.exchange_currency_dlg.exchangeType)

				self.exchange_currency_dlg.Close()

		def OnAcceptExchange(self, num, count):
			net.SendExchangeCurrency(num, count)

		def ClickExchange(self, arg, num):
			if app.IsPressed(app.DIK_RSHIFT) or app.IsPressed(app.DIK_LSHIFT):
				if not self.exchange_currency_dlg:
					self.exchange_currency_dlg = uicommon.ExchangeCurrencyDialog()
					self.exchange_currency_dlg.SetAcceptEvent(ui.__mem_func__(self.OnAcceptExchange))

				if not self.exchange_currency_dlg.Open(num, player.GetElk() / 103000000 if num == 0 else player.GetCheque()):
					self.exchange_currency_dlg.Close()
			else:
				net.SendExchangeCurrency(num, 1)

	def OnOverIn(self, arg, num):
		if not self.toolTipDesc:
			self.toolTipDesc = uitooltip.ToolTip()

		self.toolTipDesc.ClearToolTip()

		if num == 0:
			if app.USE_EXCHANGE_CURRENCY:
				self.toolTipDesc.AppendShortcutRow(("key_lclick",), localeinfo.TOOLTIP_EXCHANGE_YANG_TO_WON)
				self.toolTipDesc.AppendShortcutRow(("key_shift", "key_lclick"), localeinfo.TOOLTIP_EXCHANGE_MULTIPLE_YANG_TO_WON)
				self.toolTipDesc.AppendSpace(2)
			else:
				self.toolTipDesc.AppendTextLine(localeinfo.TOOLTIP_CURRENCY_YANG, 0xFFFFEB3B)
		elif app.ENABLE_CHEQUE_SYSTEM and num == 1:
			if app.USE_EXCHANGE_CURRENCY:
				self.toolTipDesc.AppendShortcutRow(("key_lclick",), localeinfo.TOOLTIP_EXCHANGE_WON_TO_YANG)
				self.toolTipDesc.AppendShortcutRow(("key_shift", "key_lclick"), localeinfo.TOOLTIP_EXCHANGE_MULTIPLE_WON_TO_YANG)
				self.toolTipDesc.AppendSpace(2)
			else:
				self.toolTipDesc.AppendTextLine(localeinfo.TOOLTIP_CURRENCY_CHEQUE, self.toolTipDesc.CHEQUE_COLOR)
		elif app.ENABLE_GEM_SYSTEM and num == 2:
			self.toolTipDesc.AppendTextLine(localeinfo.TOOLTIP_CURRENCY_GEM, self.toolTipDesc.GEM_COLOR)

		self.toolTipDesc.ShowToolTip()

	def OnOverOut(self):
		if self.toolTipDesc:
			self.toolTipDesc.HideToolTip()

	def OnClosePickMoneyDialog(self):
		if self.pickMoneyDialog:
			self.pickMoneyDialog.Close()

	def OnPickMoney(self, yang, cheque = 0):
		if mousemodule.mouseController.isAttached():
			mousemodule.mouseController.DeattachObject()

		if app.ENABLE_CHEQUE_SYSTEM:
			mousemodule.mouseController.AttachMoney(self, player.SLOT_TYPE_INVENTORY, yang, cheque)
		else:
			mousemodule.mouseController.AttachMoney(self, player.SLOT_TYPE_INVENTORY, yang)

	def OnClick(self, arg, num):
		if not self.pickMoneyDialog:
			self.pickMoneyDialog = uicommon.PickMoneyDialog()
			self.pickMoneyDialog.SetAcceptEvent(ui.__mem_func__(self.OnPickMoney))

		if app.ENABLE_CHEQUE_SYSTEM:
			self.pickMoneyDialog.Open(player.GetElk(), 2000000000, player.GetCheque(), 999)
		else:
			self.pickMoneyDialog.Open(player.GetElk(), 2000000000)

		self.pickMoneyDialog.SetFocus(num)

	def Hide(self):
		if app.USE_EXCHANGE_CURRENCY:
			self.OnCloseExchangeCurrencyDialog()

		self.OnOverOut()
		self.OnClosePickMoneyDialog()
		ui.ScriptWindow.Hide(self)

	def Show(self):
		self.RefreshStatus()

		ui.ScriptWindow.Show(self)
		self.SetTop()

	def __Load(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/expandedmoneytaskbar.py")
		except:
			import exception
			exception.Abort("ExpandedMoneyTaskBar.__Load.Load")

		try:
			self.money_icon = self.GetChild("money_icon_ui")
			self.money_icon.SetEvent(ui.__mem_func__(self.OnOverIn), "mouse_over_in", 0)
			self.money_icon.SetEvent(ui.__mem_func__(self.OnOverOut), "mouse_over_out")

			if app.USE_EXCHANGE_CURRENCY:
				self.money_icon.SetEvent(ui.__mem_func__(self.ClickExchange), "mouse_click", 0)

			self.money_slot = self.GetChild("money_slot_ui")
			self.money_slot.SetEvent(ui.__mem_func__(self.OnClick), "mouse_click", 0)

			self.money_text = self.GetChild("money_text_ui")

			if app.ENABLE_CHEQUE_SYSTEM:
				self.cheque_icon = self.GetChild("cheque_icon_ui")
				self.cheque_icon.SetEvent(ui.__mem_func__(self.OnOverIn), "mouse_over_in", 1)
				self.cheque_icon.SetEvent(ui.__mem_func__(self.OnOverOut), "mouse_over_out")

				if app.USE_EXCHANGE_CURRENCY:
					self.cheque_icon.SetEvent(ui.__mem_func__(self.ClickExchange), "mouse_click", 1)

				self.cheque_slot = self.GetChild("cheque_slot_ui")
				self.cheque_slot.SetEvent(ui.__mem_func__(self.OnClick), "mouse_click", 1)

				self.cheque_text = self.GetChild("cheque_text_ui")

			if app.ENABLE_GEM_SYSTEM:
				self.gem_icon = self.GetChild("gem_icon_ui")
				self.gem_icon.SetEvent(ui.__mem_func__(self.OnOverIn), "mouse_over_in", 2)
				self.gem_icon.SetEvent(ui.__mem_func__(self.OnOverOut), "mouse_over_out")

				self.gem_text = self.GetChild("gem_text_ui")
		except:
			import exception
			exception.Abort("ExpandedMoneyTaskBar.__Load.Bind")

		self.Show()

	def __init__(self):
		if app.USE_EXCHANGE_CURRENCY:
			self.exchange_currency_dlg = None

		self.toolTipDesc = None
		self.pickMoneyDialog = None

		ui.ScriptWindow.__init__(self)
		self.__Load()

	def Destroy(self):
		if app.USE_EXCHANGE_CURRENCY and self.exchange_currency_dlg:
			self.exchange_currency_dlg.Destroy()
			del self.exchange_currency_dlg
			self.exchange_currency_dlg = None

		if self.toolTipDesc:
			del self.toolTipDesc
			self.toolTipDesc = None

		if self.pickMoneyDialog:
			self.pickMoneyDialog.Destroy()
			del self.pickMoneyDialog
			self.pickMoneyDialog = None

		self.money_icon.SetEvent(None, "mouse_over_in")
		self.money_icon.SetEvent(None, "mouse_over_out")

		if app.USE_EXCHANGE_CURRENCY:
			self.money_icon.SetEvent(None, "mouse_click")

		self.money_icon = None

		self.money_slot.SetEvent(None, "mouse_click")
		self.money_slot = None

		self.money_text = None

		if app.ENABLE_CHEQUE_SYSTEM:
			self.cheque_icon.SetEvent(None, "mouse_over_in")
			self.cheque_icon.SetEvent(None, "mouse_over_out")

			if app.USE_EXCHANGE_CURRENCY:
				self.cheque_icon.SetEvent(None, "mouse_click")

			self.cheque_icon = None

			self.cheque_slot.SetEvent(None, "mouse_click")
			self.cheque_slot = None

			self.cheque_text = None

		if app.ENABLE_GEM_SYSTEM:
			self.gem_icon.SetEvent(None, "mouse_over_in")
			self.gem_icon.SetEvent(None, "mouse_over_out")
			self.gem_icon = None

			self.gem_text = None

		self.ClearDictionary()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def RefreshStatus(self):
		self.money_text.SetText(localeinfo.NumberToStringDotted(player.GetElk()))

		if app.ENABLE_CHEQUE_SYSTEM:
			self.cheque_text.SetText(str(player.GetCheque()))

		if app.ENABLE_GEM_SYSTEM:
			self.gem_text.SetText(str(player.GetGem()))
