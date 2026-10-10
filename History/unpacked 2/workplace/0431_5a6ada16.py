# coding: latin_1

import app
import chr
import net
import player

import dbg
import constinfo
import ime
import item
import grp
import ui
import uitooltip
import mousemodule
import localeinfo
import wndMgr
import cPickle as pickle
import switchbot
import uiscriptlocale
import chat

if app.USE_ITEM_ATTR_BACKUP_MODE:
	import systemSetting

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

COLOR_INACTIVE = grp.GenerateColor((247.0/255.0), (51.0/255.0), (51.0/255.0), 0.1)
COLOR_ACTIVE   = grp.GenerateColor((255.0/255.0), (204.0/255.0), (153.0/255.0), 0.1)
COLOR_FINISHED = grp.GenerateColor((81.0/255.0), (152.0/255.0), (41.0/255.0), 0.1)
COLOR_SELECTED = grp.GenerateColor(1.0, 1.0, 1.0, 1.0)

SKILL_DAMAGE_BONUS_MAX = 20
NORMAL_HIT_DAMAGE_BONUS_MAX = 50
ADDON_TYPES = {item.APPLY_SKILL_DAMAGE_BONUS : SKILL_DAMAGE_BONUS_MAX, item.APPLY_NORMAL_HIT_DAMAGE_BONUS : NORMAL_HIT_DAMAGE_BONUS_MAX}

BOARD_WIDTH = 490
BOARD_HEIGHT = 373
INPUT_HEIGHT = 27

BORDER_SPACE = 8
BORDER_SPACE_TOP = 30

ITEM_TAB_NAME_BOX_HEIGHT = 20
ITEM_TAB_SPACE = 2
ITEM_TAB_WIDTH = (BOARD_WIDTH - BORDER_SPACE * 2) / switchbot.SLOT_COUNT + 1 - ITEM_TAB_SPACE
	
TOP_PANEL_HEIGHT = (BORDER_SPACE * 2) + (3 * 32) + ITEM_TAB_NAME_BOX_HEIGHT
TOP_PANEL_WIDTH = BOARD_WIDTH - (BORDER_SPACE * 2)

MAIN_PANEL_WIDTH = BOARD_WIDTH - (BORDER_SPACE * 2)
# 1 header row (the alternative selector) + ATTR_SLOT_COUNT attribute rows.
ATTR_SLOT_COUNT = 7
# Rows 0..NORM_ATTR_COUNT-1 are populated from the normal attr pool (g_map_itemAttr).
# Rows NORM_ATTR_COUNT..ATTR_SLOT_COUNT-1 are populated from the rare pool (g_map_itemRare).
NORM_ATTR_COUNT = 5
MAIN_PANEL_HEIGHT = INPUT_HEIGHT * (1 + ATTR_SLOT_COUNT)
MAIN_PANEL_BONUS_SAVER_WIDTH = 149

BOT_PANEL_HEIGHT = 40
BOT_PANEL_WIDTH = BOARD_WIDTH - BORDER_SPACE * 2

BOARD_HEIGHT = BORDER_SPACE_TOP + TOP_PANEL_HEIGHT + MAIN_PANEL_HEIGHT + BOT_PANEL_HEIGHT + BORDER_SPACE

def GetAffectString(affectType, affectValue):
	if not affectType:
		return None

	try:
		return uitooltip.ItemToolTip.AFFECT_DICT[affectType](affectValue)
	except TypeError:
		return "UNKNOWN_VALUE[{}] {}".format(affectType, affectValue)
	except KeyError:
		return "UNKNOWN_TYPE[{}] {}".format(affectType, affectValue)


class SwitchbotItemTab(ui.ScriptWindow):
	def __init__(self, slot_num):
		ui.ScriptWindow.__init__(self)
		
		self.slot_num = slot_num
		
		self.__Initialize()
		self.__LoadItemTab()
		self.__BindEvents()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __Initialize(self):
		self.tooltipItem = None
		self.onSelectEvent = None
		
		self.statusBar = None
		self.itemSlot = None
		self.selectButton = None
		
		self.lastSelectAlpha = 255
		self.lastSelectAlphaDir = 1
		
	def __LoadItemTab(self):
		self.SetSize(ITEM_TAB_WIDTH, TOP_PANEL_HEIGHT)
		
		self.background = ui.ExpandedImageBox()
		self.background.SetParent(self)
		if self.slot_num+1 == switchbot.SLOT_COUNT:
			self.background.LoadImage("d:/ymir work/ui/switchbot/head_bg_finish.tga")
			self.background.SetPosition(0, -1)
		else:
			self.background.LoadImage("d:/ymir work/ui/switchbot/head_bg.tga")
		self.background.Show()
		
		self.statusBar = ui.Bar()
		self.statusBar.SetParent(self)
		self.statusBar.SetPosition(2, 0)
		self.statusBar.SetSize(83, TOP_PANEL_HEIGHT - 2)
		
		self.selectBox = ui.Box()
		self.selectBox.SetParent(self)
		self.selectBox.SetPosition(1, 0)
		self.selectBox.SetSize(85, TOP_PANEL_HEIGHT - 2)
		self.selectBox.SetColor(COLOR_SELECTED)
			
		self.selectButton = ui.RadioButton()
		self.selectButton.SetParent(self)
		self.selectButton.SetUpVisual("d:/ymir work/ui/switchbot/buttons/but_swithcbot_norm.tga")
		self.selectButton.SetOverVisual("d:/ymir work/ui/switchbot/buttons/but_swithcbot_hover.tga")
		self.selectButton.SetDownVisual("d:/ymir work/ui/switchbot/buttons/but_swithcbot_down.tga")
		self.selectButton.SetWindowHorizontalAlignCenter()
		self.selectButton.SetPosition(0, 4)
		self.selectButton.SetText(constinfo.NumberToStrRomanNumerals(self.slot_num+1))
		self.selectButton.SetTextPosition(1, -1)
		self.selectButton.Show()
		
		# self.slotImage = ui.ExpandedImageBox()
		# self.slotImage.SetParent(self)
		# self.slotImage.LoadImage("d:/ymir work/ui/switchbot/switch_slot.tga")
		# self.slotImage.SetPosition(0, 23)
		# self.slotImage.SetWindowHorizontalAlignCenter()
		# self.slotImage.Show()
		
		# self.itemSlot = ui.GridSlotWindow()
		# self.itemSlot.SetParent(self.slotImage)
		# self.itemSlot.ArrangeSlot(0, 1, 3, 32, 32, 0, 0)
		# self.itemSlot.SetWindowHorizontalAlignCenter()
		# self.itemSlot.SetPosition(6, 5)
		# self.itemSlot.Show()
	
		self.itemSlot = ui.GridSlotWindow()
		self.itemSlot.SetParent(self)
		self.itemSlot.ArrangeSlot(0, 1, 3, 32, 32, 0, 0)
		self.itemSlot.SetSlotBaseImage("d:/ymir work/ui/public/slot_base.sub", 1.0, 1.0, 1.0, 1.0)
		self.itemSlot.SetWindowHorizontalAlignCenter()
		self.itemSlot.SetPosition(0, 30)
		self.itemSlot.Show()
	
	def __BindEvents(self):
		self.itemSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		self.itemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		self.itemSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		self.itemSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		self.itemSlot.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
#		self.itemSlot.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))

		self.selectButton.SetEvent(ui.__mem_func__(self.__OnSelectButtonClick))
		
	def Destroy(self):
		self.__Initialize()

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem
		
	def OnPlacedItem(self, slot_num):
		pass

	def OverOutItem(self):
		self.itemSlot.SetUsableItem(False)
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OverInItem(self, overSlotPos):
		self.itemSlot.SetUsableItem(True)

		if self.IsEmpty():
			return

		if self.tooltipItem:
			self.tooltipItem.SetSwitchbotItem(self.slot_num)
			self.tooltipItem.ShowToolTip()

	def SelectEmptySlot(self, selectedSlotPos):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		if mousemodule.mouseController.isAttached():

			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			attachedItemCount = mousemodule.mouseController.GetAttachedItemCount()
			attachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()

			if player.SLOT_TYPE_INVENTORY == attachedSlotType:
				attachedCount = mousemodule.mouseController.GetAttachedItemCount()
				net.SendItemMovePacket(player.INVENTORY, attachedSlotPos, player.SWITCHBOT, self.slot_num, long(attachedItemCount))
			elif player.SLOT_TYPE_SWITCHBOT == attachedSlotType:
				attachedCount = mousemodule.mouseController.GetAttachedItemCount()
				net.SendItemMovePacket(player.SWITCHBOT, attachedSlotPos, player.SWITCHBOT, self.slot_num, long(attachedItemCount))
				
			mousemodule.mouseController.DeattachObject()

			self.OnPlacedItem(self.slot_num)

	def SelectItemSlot(self, itemSlotIndex):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		if switchbot.IsActive(self.slot_num):
			return

		if mousemodule.mouseController.isAttached():
			mousemodule.mouseController.DeattachObject()
		else:
			itemVnum = player.GetItemIndex(player.SWITCHBOT, self.slot_num)
			if not itemVnum:
				return

			if app.IsPressed(app.DIK_LALT):
				link = player.GetItemLink(player.SWITCHBOT, self.slot_num)
				ime.PasteString(link)
			else:
				if app.USE_ITEM_ATTR_BACKUP_MODE:
					if (app.IsPressed(app.DIK_LSHIFT) or app.IsPressed(app.DIK_RSHIFT)):
						item.SelectItem(itemVnum)
						if player.GetItemBackup(player.SWITCHBOT, self.slot_num):
							interfaceHandler = systemSetting.GetInterfaceHandler()
							if interfaceHandler:
								interfaceHandler.OpenItemBackupAttr(player.SWITCHBOT, self.slot_num)
								self.OverOutItem()
							return
						if item.GetItemType() == item.ITEM_TYPE_WEAPON and item.GetItemSubType() in [item.WEAPON_SWORD, item.WEAPON_DAGGER, item.WEAPON_BOW, item.WEAPON_TWO_HANDED, item.WEAPON_BELL, item.WEAPON_FAN, item.WEAPON_CLAW]:
							net.SendItemActivateBackupAttr(player.SWITCHBOT, self.slot_num)

							if self.tooltipItem and self.tooltipItem.IsShow():
								self.OverOutItem()
								self.OverInItem()

							return

				itemCount = player.GetItemCount(player.SWITCHBOT, self.slot_num)
				mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_SWITCHBOT, self.slot_num, itemVnum, itemCount)

	def UseItemSlot(self, slotIndex):
		curCursorNum = app.GetCursor()
		if app.SELL == curCursorNum:
			return

		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		if mousemodule.mouseController.isAttached():
			mousemodule.mouseController.DeattachObject()

		itemVnum = player.GetItemIndex(player.SWITCHBOT, self.slot_num)
		if not itemVnum:
			return

		if switchbot.IsActive(self.slot_num):
			item.SelectItem(itemVnum)
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SWITCHBOT_CANNOT_WITHDRAW_WHILE_IS_SWITCHING % (item.GetItemName()))
			return

		net.SendItemUsePacket(player.SWITCHBOT, self.slot_num)
		self.OverOutItem()

	def RefreshItemSlot(self):
		if self.IsEmpty():
			switchbot.ClearSlot(self.slot_num)
			self.itemSlot.ClearSlot(0)
			self.statusBar.Hide()
		else:			
			itemCount = player.GetItemCount(player.SWITCHBOT, self.slot_num)
			itemVnum = player.GetItemIndex(player.SWITCHBOT, self.slot_num)
			if itemCount == 1:
				itemCount = 0
			
			self.itemSlot.SetItemSlot(0, itemVnum, itemCount)
			item.SelectItem(itemVnum)
			self.statusBar.Show()
			if self.IsActive():
				self.itemSlot.ActivateSlot(0)
				if player.GetItemBackup(player.SWITCHBOT, self.slot_num):
					self.itemSlot.SetSlotDiffuseColor(0, wndMgr.COLOR_TYPE_ORANGE)#dream
				self.statusBar.SetColor(COLOR_ACTIVE)
			else:
				if not player.GetItemBackup(player.SWITCHBOT, self.slot_num):
					self.itemSlot.DeactivateSlot(0)

				if self.IsFinished():
					self.statusBar.SetColor(COLOR_FINISHED)
					if player.GetItemBackup(player.SWITCHBOT, self.slot_num):
						self.itemSlot.ActivateSlot(0)
						self.itemSlot.SetSlotDiffuseColor(0, wndMgr.COLOR_TYPE_GREEN)#dream
				else:
					self.statusBar.SetColor(COLOR_INACTIVE)
		
		self.itemSlot.RefreshSlot()
		
	def IsEmpty(self):
		itemVnum = player.GetItemIndex(player.SWITCHBOT, self.slot_num)	
		return not itemVnum
		
	def IsActive(self):
		return switchbot.IsActive(self.slot_num)

	def IsFinished(self):
		return switchbot.IsFinished(self.slot_num)

	def GetSlotNum(self):
		return self.slot_num
		
	def SetOnSelectEvent(self, event):
		self.onSelectEvent = event
		
	def __OnSelectButtonClick(self):
		if self.onSelectEvent:
			self.onSelectEvent(self.slot_num)
			
	def SetUp(self):
		if self.selectButton:
			self.selectButton.SetUp()
			self.selectBox.Hide()
			
	def Down(self):
		if self.selectButton:
			self.selectButton.Down()
			
			self.lastSelectAlpha = 255
			self.selectBox.Show()
			
	def OnUpdate(self):
		if self.selectBox.IsShow():
			rate = 3
			
			self.lastSelectAlpha -= (rate * self.lastSelectAlphaDir)
		
			if self.lastSelectAlpha <= 0:
				self.lastSelectAlpha = 0
				self.lastSelectAlphaDir = -1
			elif self.lastSelectAlpha >= 255:
				self.lastSelectAlpha = 255
				self.lastSelectAlphaDir = 1
				
			self.selectBox.SetColor(grp.GenerateColor(1.0, 1.0, 1.0, float(self.lastSelectAlpha) / 255.0))
			
class SwitchbotAttribute(ui.Window):
	VALUE_WIDTH = 50
	
	typeInput = None
	typeTextLine = None
	searchTypeButton = None
	deleteAttributeButton = None
	valueInput = None
	valueEditLine = None	
	
	def __init__(self):
		ui.Window.__init__(self)	
		self.__Initialize()
		
	def __del__(self):
		ui.Window.__del__(self)
		
	def __Initialize(self):
		self.selectedSlot = -1
		self.alternative = 0
		self.index = -1
		
		self.attributeType = 0
		self.attributeValue = 0
		
		self.searchEvent = None
		self.attributeMaxValue = 0	
	
		self.typeInput = None
		self.typeTextLine = None
		self.searchTypeButton = None
		self.deleteAttributeButton = None
		self.valueInput = None
		self.valueEditLine = None
		
	def Create(self, width, index):
		self.index = index
		self.SetSize(width, INPUT_HEIGHT)
		
		self.typeInput = ui.ThinBoardCircle()
		self.typeInput.SetParent(self)
		self.typeInput.SetSize(width - self.VALUE_WIDTH, INPUT_HEIGHT)
		self.typeInput.SetPosition(0, 0)
		self.typeInput.Show()
		
		self.typeTextLine = ui.TextLine()
		self.typeTextLine.SetParent(self.typeInput)
		self.typeTextLine.SetText(localeinfo.SWITCHBOT_EMPTY_ATTR)
		self.typeTextLine.SetVerticalAlignCenter()
		self.typeTextLine.SetWindowVerticalAlignCenter()
		self.typeTextLine.SetHorizontalAlignCenter()
		self.typeTextLine.SetWindowHorizontalAlignCenter()
		self.typeTextLine.SetPosition(-20, -1)
		self.typeTextLine.Show()
			
		self.searchTypeButton = ui.Button()
		self.searchTypeButton.SetParent(self.typeInput)
		self.searchTypeButton.SetUpVisual("d:/ymir work/ui/switchbot/search_attr_01.sub")
		self.searchTypeButton.SetOverVisual("d:/ymir work/ui/switchbot/search_attr_02.sub")
		self.searchTypeButton.SetDownVisual("d:/ymir work/ui/switchbot/search_attr_03.sub")
		self.searchTypeButton.SetDisableVisual("d:/ymir work/ui/switchbot/search_attr_03.sub")
		self.searchTypeButton.SetWindowHorizontalAlignRight()
		self.searchTypeButton.SetWindowVerticalAlignCenter()
		self.searchTypeButton.SetPosition(24 * 2 + 2, 1)
		self.searchTypeButton.SetEvent(ui.__mem_func__(self.__OnClickSearchButton))
		self.searchTypeButton.Show()
		
		self.deleteAttributeButton = ui.Button()
		self.deleteAttributeButton.SetParent(self.typeInput)
		self.deleteAttributeButton.SetUpVisual("d:/ymir work/ui/switchbot/delete_attr_01.sub")
		self.deleteAttributeButton.SetOverVisual("d:/ymir work/ui/switchbot/delete_attr_02.sub")
		self.deleteAttributeButton.SetDownVisual("d:/ymir work/ui/switchbot/delete_attr_03.sub")
		self.deleteAttributeButton.SetDisableVisual("d:/ymir work/ui/switchbot/delete_attr_03.sub")
		self.deleteAttributeButton.SetWindowHorizontalAlignRight()
		self.deleteAttributeButton.SetWindowVerticalAlignCenter()
		self.deleteAttributeButton.SetPosition(24 + 2, 1)
		self.deleteAttributeButton.SetToolTipText(localeinfo.SWITCHBOT_CLEAR_ATTR)
		self.deleteAttributeButton.SetEvent(ui.__mem_func__(self.__OnClickClearButton))
		self.deleteAttributeButton.Show()		
		
		self.valueInput = ui.ThinBoardCircle()
		self.valueInput.SetParent(self)
		self.valueInput.SetSize(self.VALUE_WIDTH, INPUT_HEIGHT)
		self.valueInput.SetPosition(width - self.VALUE_WIDTH, 0)
		self.valueInput.Show()
		
		self.valueEditLine = ui.EditLine()
		self.valueEditLine.SetParent(self.valueInput)
		self.valueEditLine.SetSize(self.VALUE_WIDTH, 18)
		self.valueEditLine.SetMax(4)
		self.valueEditLine.SetNumberMode()
		self.valueEditLine.SetText("0")
		self.valueEditLine.SetPosition(-20, 7)
		self.valueEditLine.Show()
		self.valueEditLine.OnIMEUpdate = self.__OnEditLineIMEUpdate
		self.valueEditLine.SetEscapeEvent(ui.__mem_func__(self.__OnEscapeEvent))
		
	def Destroy(self):
		self.__Initialize()
		
	def Hide(self):
		ui.Window.Hide(self)
		
		if self.valueEditLine:
			self.valueEditLine.KillFocus()

	def ClearAttributeRow(self, slot_num, alternative, index):
		self.selectedSlot = slot_num
		self.alternative = alternative
		self.index = index
		self.__OnClickClearButton()
	
	def RefreshAttributeRow(self, slot_num, alternative, index):
		self.selectedSlot = slot_num
		self.alternative = alternative
		self.index = index	
	
		if switchbot.IsActive(slot_num):
			self.searchTypeButton.Disable()
			self.deleteAttributeButton.Disable()
			self.valueEditLine.Hide()
		else:
			self.searchTypeButton.Enable()
			self.deleteAttributeButton.Enable()	
			self.valueEditLine.Show()
			
		(type, value) = switchbot.GetAttribute(slot_num, alternative, index)
		if not type:
			self.SetAttribute(localeinfo.SWITCHBOT_EMPTY_ATTR, 0)
			return
			
		affectString = GetAffectString(type, value)
		if not affectString:
			return
			
		self.SetAttribute(affectString, value)

	def __OnEditLineIMEUpdate(self):
		ui.EditLine.OnIMEUpdate(self.valueEditLine)
		
		text = self.valueEditLine.GetText()
		if len(text) > 0 and text.isdigit():
			(curType, curValue) = switchbot.GetAttribute(self.selectedSlot, self.alternative, self.index)
			
			maxValue = 0
			if self.index >= NORM_ATTR_COUNT:
				# Rare row: clamp by the rare-pool max value for this attr/set.
				maxValue = switchbot.GetRareAttributeMaxValue(self.selectedSlot, curType)
			elif not ADDON_TYPES.has_key(curType):
				maxValue = switchbot.GetAttributeMaxValue(self.selectedSlot, curType)
				
			value = int(text)
			
			if value == curValue:
				return
			
			if maxValue != 0 and value > maxValue:
				value = maxValue
				self.valueEditLine.SetText(str(value))
				
			switchbot.SetAttribute(self.selectedSlot, self.alternative, self.index, curType, value)
			self.typeTextLine.SetText(GetAffectString(curType, value))
			self.__OnAttributeUpdate()
		
	def SetSearchEvent(self, event):
		self.searchEvent= event
		
	def __OnClickSearchButton(self):
		if self.searchEvent:
			self.searchEvent(self.index)
		
	def SetAttributeUpdateEvent(self, event):
		self.attributeUpdateEvent = event		
		
	def __OnAttributeUpdate(self):
		if self.attributeUpdateEvent:
			self.attributeUpdateEvent(self.index)
			
	def SetEscapeEvent(self, event):
		self.escapeEvent = event			
			
	def __OnEscapeEvent(self):
		if self.escapeEvent:
			self.escapeEvent()
			
	def __OnClickClearButton(self):
		self.SetAttribute(localeinfo.SWITCHBOT_EMPTY_ATTR, 0)
		switchbot.SetAttribute(self.selectedSlot, self.alternative, self.index, 0, 0)
		self.__OnAttributeUpdate()		
			
	def SetAttribute(self, applyname, maxValue):
		self.typeTextLine.SetText(applyname)
		self.valueEditLine.SetText(str(maxValue))
		
	def GetIndex(self):
		return self.index

class SwitchbotWindow(ui.NewBoardWithTitleBar):
	def __init__(self):
		ui.NewBoardWithTitleBar.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		try:
			self.__Initialize()
			self.__LoadWindow()
			self.__BindEvents()
		except:
			import exception
			exception.Abort("SwitchbotWindow.__init__")
	
	def __del__(self):
		ui.NewBoardWithTitleBar.__del__(self)

	def __Initialize(self):
		self.selectedSlot = 0
		self.alternative = 0
		
		self.alternativeButtons = {}
		self.itemTabs = {}
		self.attrDict = {}
		
		self.attributeSearchWindow = None
		self.attrSearchIdx = -1
		
		self.topPanel = None
		self.mainPanel = None
		self.botPanel = None
		self.putHereImage = None
		
		self.toggleButton = None
		self.resetButton = None

		# Standalone side windows: each is now its own titled, movable window.
		# The switcher ("Choose Switch") window auto-shows beside the main window
		# whenever the selected slot is switchable; the save ("Save Configuration")
		# window is opened via saveToggleButton.
		self.switcherInfoWindow = None
		self.bonusSaberWindow = None
		self.saveToggleButton = None

		# Last known main-window position, used to drag the side windows along by
		# the same delta when the main window moves.
		self.lastMovePos = None

	def __LoadWindow(self):
		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetSize(BOARD_WIDTH, BOARD_HEIGHT)
		self.SetTitleName(localeinfo.SWITCHBOT_TITLE)
		
		self.topPanel = ui.ThinBoardCircle()
		self.topPanel.SetParent(self)
		self.topPanel.SetSize(TOP_PANEL_WIDTH, TOP_PANEL_HEIGHT)
		self.topPanel.SetPosition(BORDER_SPACE, BORDER_SPACE_TOP)
		self.topPanel.Show()
		
		for i in xrange(switchbot.SLOT_COUNT):	
			itemTab = SwitchbotItemTab(i)
			itemTab.SetParent(self.topPanel)
			itemTab.SetPosition((ITEM_TAB_WIDTH + ITEM_TAB_SPACE) * i, 0)
			itemTab.SetOnSelectEvent(ui.__mem_func__(self.SelectSlot))
			itemTab.OnPlacedItem = self.__OnPlacedItem
			itemTab.Show()
			
			self.itemTabs[i] = itemTab
		
		self.mainPanel = ui.ThinBoardCircle()
		self.mainPanel.SetParent(self)
		self.mainPanel.SetSize(MAIN_PANEL_WIDTH, MAIN_PANEL_HEIGHT)
		self.mainPanel.SetPosition(BORDER_SPACE, BORDER_SPACE_TOP + TOP_PANEL_HEIGHT)
		self.mainPanel.Show()

		self.mainPanelBg = ui.ExpandedImageBox()
		self.mainPanelBg.SetParent(self.mainPanel)
		self.mainPanelBg.SetPosition(1, 2)
		self.mainPanelBg.LoadImage("d:/ymir work/ui/switchbot/background.tga")
		self.mainPanelBg.Hide()

		self.putHereImage = ui.ExpandedImageBox()
		self.putHereImage.SetParent(self)
		self.putHereImage.SetPosition(BORDER_SPACE + 1, BORDER_SPACE_TOP + TOP_PANEL_HEIGHT + 2)
		self.putHereImage.LoadImage("d:/ymir work/ui/switchbot/put_here_image.tga")
		self.putHereImage.Hide()
		
		self.putHereImageItem = ui.ExpandedImageBox()
		self.putHereImageItem.SetParent(self.putHereImage)
		self.putHereImageItem.SetPosition(30, 84)
		self.putHereImageItem.Hide()
		
		self.alternativePanel = ui.ThinBoardCircle()
		self.alternativePanel.SetParent(self.mainPanel)
		self.alternativePanel.SetSize(MAIN_PANEL_WIDTH, INPUT_HEIGHT)
		self.alternativePanel.SetPosition(0, 0)
		self.alternativePanel.Show()
		
		self.alternativeTextLine = ui.TextLine()
		self.alternativeTextLine.SetParent(self.alternativePanel)
		self.alternativeTextLine.SetPosition(120+140, -1)
		self.alternativeTextLine.SetVerticalAlignCenter()
		self.alternativeTextLine.SetWindowVerticalAlignCenter()
		self.alternativeTextLine.SetHorizontalAlignLeft()
		self.alternativeTextLine.SetText(localeinfo.INTERFACE_TEXT_31)
		self.alternativeTextLine.Show()
		
		for i in xrange(switchbot.ALTERNATIVE_COUNT):
			alternativeButton = ui.RadioButton()
			alternativeButton.SetParent(self.alternativePanel)
			alternativeButton.SetUpVisual("d:/ymir work/ui/switchbot/buttons/but_swithcbot_norm.tga")
			alternativeButton.SetOverVisual("d:/ymir work/ui/switchbot/buttons/but_swithcbot_hover.tga")
			alternativeButton.SetDownVisual("d:/ymir work/ui/switchbot/buttons/but_swithcbot_down.tga")
			alternativeButton.SetWindowVerticalAlignCenter()
			alternativeButton.SetPosition(108 + (alternativeButton.GetWidth() * i) + (i * 5), 0)
			alternativeButton.SetText(constinfo.NumberToStrRomanNumerals(i+1))
			alternativeButton.SetTextPosition(1, -1)
			alternativeButton.SetEvent(lambda arg = i : self.SelectAlternative(arg))
			alternativeButton.Show()
			
			self.alternativeButtons[i] = alternativeButton

		
		for i in xrange(ATTR_SLOT_COUNT):
			attr = SwitchbotAttribute()
			attr.SetParent(self.mainPanel)
			# Attribute rows now use the full main-panel width: the switcher/save
			# lists moved out into their own windows, freeing the old right sidebar.
			attr.Create(MAIN_PANEL_WIDTH, i)
			attr.SetPosition(0, INPUT_HEIGHT + (INPUT_HEIGHT * i))
			attr.SetSearchEvent(ui.__mem_func__(self.__OnSearchAttribute))
			attr.SetAttributeUpdateEvent(ui.__mem_func__(self.__OnAttributeUpdate))
			attr.SetEscapeEvent(ui.__mem_func__(self.Close))
			attr.Show()
			
			self.attrDict[i] = attr
		
		# >>> SWITCHBOT DEDICATED PAGES BEGIN
		# The switcher list and the save list each live in their own titled,
		# movable window now (no cramped right sidebar). They are top-level
		# windows (no parent) that float beside the main window: the switcher
		# window auto-shows via __RefreshBonusSaverWindow, the save window is
		# opened by saveToggleButton.
		self.switcherInfoWindow = SwitcherInfoWindow(self)
		self.switcherInfoWindow.Hide()

		self.bonusSaberWindow = ConfigurationWindow(self)
		self.bonusSaberWindow.Hide()
		# >>> SWITCHBOT DEDICATED PAGES END

		# >>> LEGACY DOCKED SIDEBAR + TAB BUTTONS BEGIN (replaced by dedicated pages)
		# self.switcherInfoWindow.SetParent(self.mainPanel)
		# self.switcherInfoWindow.SetWindowHorizontalAlignCenter()
		# self.switcherInfoWindow.SetWindowHorizontalAlignRight()
		# self.switcherInfoWindow.SetPosition(MAIN_PANEL_BONUS_SAVER_WIDTH, INPUT_HEIGHT)
		#
		# self.bonusSaberWindow.SetParent(self.mainPanel)
		# self.bonusSaberWindow.SetWindowHorizontalAlignCenter()
		# self.bonusSaberWindow.SetWindowHorizontalAlignRight()
		# self.bonusSaberWindow.SetPosition(MAIN_PANEL_BONUS_SAVER_WIDTH, INPUT_HEIGHT)
		#
		# self.sidebarTab = "switchers"
		# self.tabSwitchersBtn = ui.RadioButton()
		# self.tabSwitchersBtn.SetParent(self.mainPanel)
		# self.tabSwitchersBtn.SetUpVisual("d:/ymir work/ui/switchbot/btn_01.png")
		# self.tabSwitchersBtn.SetOverVisual("d:/ymir work/ui/switchbot/btn_02.png")
		# self.tabSwitchersBtn.SetDownVisual("d:/ymir work/ui/switchbot/btn_02.png")
		# self.tabSwitchersBtn.SetWindowHorizontalAlignRight()
		# self.tabSwitchersBtn.SetPosition(MAIN_PANEL_BONUS_SAVER_WIDTH + 35, 3)
		# self.tabSwitchersBtn.SetText(localeinfo.SWITCHBOT_TAB_SWITCHERS)
		# self.tabSwitchersBtn.SetEvent(lambda: self.__SwitchSidebar("switchers"))
		# self.tabSwitchersBtn.Show()
		#
		# self.tabConfigsBtn = ui.RadioButton()
		# self.tabConfigsBtn.SetParent(self.mainPanel)
		# self.tabConfigsBtn.SetUpVisual("d:/ymir work/ui/switchbot/btn_small_01.png")
		# self.tabConfigsBtn.SetOverVisual("d:/ymir work/ui/switchbot/btn_small_02.png")
		# self.tabConfigsBtn.SetDownVisual("d:/ymir work/ui/switchbot/btn_small_02.png")
		# self.tabConfigsBtn.SetWindowHorizontalAlignRight()
		# self.tabConfigsBtn.SetPosition(MAIN_PANEL_BONUS_SAVER_WIDTH / 2 - 4, 3)
		# self.tabConfigsBtn.SetText(localeinfo.SWITCHBOT_TAB_CONFIGS)
		# self.tabConfigsBtn.SetEvent(lambda: self.__SwitchSidebar("configs"))
		# self.tabConfigsBtn.Show()
		#
		# self.tabSwitchersBtn.Down()
		# self.switcherInfoWindow.Open()
		# self.bonusSaberWindow.Hide()
		# <<< LEGACY DOCKED SIDEBAR + TAB BUTTONS END

		self.botPanel = ui.ThinBoardCircle()
		self.botPanel.SetParent(self)
		self.botPanel.SetSize(BOT_PANEL_WIDTH, BOT_PANEL_HEIGHT)
		self.botPanel.SetPosition(BORDER_SPACE, BORDER_SPACE_TOP + TOP_PANEL_HEIGHT + MAIN_PANEL_HEIGHT)
		self.botPanel.Show()

		# Bottom-left floppy button toggles the standalone "Save Configuration" window.
		self.saveToggleButton = ui.Button()
		self.saveToggleButton.SetParent(self.botPanel)
		self.saveToggleButton.SetUpVisual("d:/ymir work/ui/switchbot/buttons/save_bonus_norm.tga")
		self.saveToggleButton.SetOverVisual("d:/ymir work/ui/switchbot/buttons/save_bonus_hover.tga")
		self.saveToggleButton.SetDownVisual("d:/ymir work/ui/switchbot/buttons/save_bonus_down.tga")
		self.saveToggleButton.SetWindowVerticalAlignCenter()
		self.saveToggleButton.SetPosition(BORDER_SPACE, 0)
		self.saveToggleButton.SetToolTipText(localeinfo.SWITCHBOT_SAVE_BUTTON)
		self.saveToggleButton.Show()

		# One button drives both start and stop: its label flips between START and
		# STOP in __RefreshButtons depending on whether the slot is switching.
		self.toggleButton = ui.Button()
		self.toggleButton.SetParent(self.botPanel)
		self.toggleButton.SetUpVisual("d:/ymir work/ui/switchbot/btn_big_01.sub")
		self.toggleButton.SetOverVisual("d:/ymir work/ui/switchbot/btn_big_02.sub")
		self.toggleButton.SetDownVisual("d:/ymir work/ui/switchbot/btn_big_03.sub")
		self.toggleButton.SetDisableVisual("d:/ymir work/ui/switchbot/btn_big_03.sub")
		self.toggleButton.SetWindowVerticalAlignCenter()
		self.toggleButton.SetWindowHorizontalAlignRight()
		self.toggleButton.SetPosition(self.toggleButton.GetWidth() + 8, 0)
		self.toggleButton.SetText(localeinfo.SWITCHBOT_START)
		self.toggleButton.Show()

		self.resetButton = ui.Button()
		self.resetButton.SetParent(self.botPanel)
		self.resetButton.SetUpVisual("d:/ymir work/ui/switchbot/btn_big_01.sub")
		self.resetButton.SetOverVisual("d:/ymir work/ui/switchbot/btn_big_02.sub")
		self.resetButton.SetDownVisual("d:/ymir work/ui/switchbot/btn_big_03.sub")
		self.resetButton.SetDisableVisual("d:/ymir work/ui/switchbot/btn_big_03.sub")
		self.resetButton.SetWindowVerticalAlignCenter()
		self.resetButton.SetWindowHorizontalAlignRight()
		self.resetButton.SetPosition((self.toggleButton.GetWidth() + 8) + (self.resetButton.GetWidth() + 8), 0)
		self.resetButton.SetText(localeinfo.INTERFACE_TEXT_30)
		self.resetButton.Show()
		self.SelectSlot(0)

	def __BindEvents(self):
		self.SetCloseEvent(ui.__mem_func__(self.Close))

		self.toggleButton.SetEvent(ui.__mem_func__(self.__OnToggleActive))
		self.resetButton.SetEvent(ui.__mem_func__(self.__ResetAttributesConfig))
		self.saveToggleButton.SetEvent(ui.__mem_func__(self.__ToggleSaveWindow))

	def Destroy(self):
		if app.USE_SWITCHBOT_FIX_SMALL_STUFF:
			for i in xrange(switchbot.SLOT_COUNT):
				switchbot.ClearSlot(i)

		# The side windows are top-level now (not children of this window), so
		# tear them down explicitly to avoid leaking them.
		if self.switcherInfoWindow:
			self.switcherInfoWindow.Close()
			self.switcherInfoWindow.Destroy()
			self.switcherInfoWindow = None
		if self.bonusSaberWindow:
			self.bonusSaberWindow.Close()
			self.bonusSaberWindow.Destroy()
			self.bonusSaberWindow = None

		self.__Initialize()

	def Open(self):
		if app.ENABLE_WINDOW_POSITION_SAVE and uiwindowpositions.ApplySavedPosition(self,"SWITCHBOT"):
			pass
		else:
			self.SetCenterPosition()

		# The save window is user-toggled; always start it hidden on (re)open.
		if self.bonusSaberWindow:
			self.bonusSaberWindow.Hide()

		self.Show()
		self.SetTop()

		# Baseline for OnMoveWindow's follow-along delta.
		self.lastMovePos = self.GetGlobalPosition()

		# Positions the switcher window relative to the now-shown main window.
		self.RefreshSwitchbotWindow()


	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "SWITCHBOT")
		if self.attributeSearchWindow:
			self.attributeSearchWindow.Close()

		# The dedicated side windows travel with the main window.
		if self.switcherInfoWindow:
			self.switcherInfoWindow.Close()
		if self.bonusSaberWindow:
			self.bonusSaberWindow.Close()

		self.Hide()
		return True

	def Hide(self):
		# The side windows are separate top-level windows, so a plain Hide() of
		# the main window (e.g. HideAllWindows during a cutscene) must take them
		# along or they would keep floating on their own.
		# NOTE: the base __init__ can call Hide() before __Initialize() has run,
		# so the side-window attrs may not exist yet - guard with getattr.
		switcher = getattr(self, "switcherInfoWindow", None)
		if switcher:
			switcher.Hide()
		saver = getattr(self, "bonusSaberWindow", None)
		if saver:
			saver.Hide()
		ui.NewBoardWithTitleBar.Hide(self)

	def Show(self):
		# Symmetric with Hide(): when the main window is shown again (e.g. the
		# ShowAllWindows restore after a cutscene calls Show(), not Open()),
		# restore the switcher window's auto-visibility. The save window stays
		# hidden - it is user-toggled. getattr-guarded for the same reason as Hide.
		ui.NewBoardWithTitleBar.Show(self)
		switcher = getattr(self, "switcherInfoWindow", None)
		if switcher:
			switcher.UpdateAutoVisibility()

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("SWITCHBOT", x, y)

		# Drag the dedicated side windows along with the main window by the same
		# delta, so they keep their relative offset (attached-window behaviour).
		if self.lastMovePos is not None:
			(px, py) = self.lastMovePos
			dx = x - px
			dy = y - py
			if dx or dy:
				for sideWnd in (self.switcherInfoWindow, self.bonusSaberWindow):
					if sideWnd and sideWnd.IsShow():
						(sx, sy) = sideWnd.GetGlobalPosition()
						sideWnd.SetPosition(sx + dx, sy + dy)
		self.lastMovePos = (x, y)

	def __OnPlacedItem(self, slot_num):
		self.SelectSlot(slot_num)

	def __ToggleSaveWindow(self):
		# The save window is a standalone page opened/closed by the bottom button.
		if not self.bonusSaberWindow:
			return
		if self.bonusSaberWindow.IsShow():
			self.bonusSaberWindow.Close()
		else:
			self.bonusSaberWindow.Open()

	def SelectSlot(self, selectedSlot):
		self.itemTabs[self.selectedSlot].SetUp()
		self.selectedSlot = selectedSlot
		self.itemTabs[self.selectedSlot].Down()

		# Drives RefreshSwitchbotWindow, which auto-updates the switcher window.
		self.SelectAlternative(0)

	def GetSelectedSlot(self):
		return self.selectedSlot
		
	def SelectAlternative(self, alternative):
		self.alternativeButtons[self.alternative].SetUp()	
		self.alternative = alternative
		self.alternativeButtons[self.alternative].Down()
		
		self.RefreshSwitchbotWindow()
	def BotHasChanging(self):
		count = 0
		for x in xrange(switchbot.SLOT_COUNT):
			slot = self.itemTabs.get(x, None)
			if not slot:
				continue
			
			count += int(slot.IsActive())
		
		return count
		
	def __OnToggleActive(self):
		# Single start/stop button: stop when the slot is switching, start otherwise.
		self.SetActive(not self.IsActiveSlot())

	def SetActive(self, active):
		if self.selectedSlot >= switchbot.SLOT_COUNT:
			return

		if active and self.IsActiveSlot():
			return

		if not active and not self.IsActiveSlot():
			return

		if active:
			switchbot.Start(self.selectedSlot)
		else:
			switchbot.Stop(self.selectedSlot)

	def SetItemToolTip(self, tooltipItem):
		for i in xrange(switchbot.SLOT_COUNT):
			self.itemTabs[i].SetItemToolTip(tooltipItem)
		# Forward to the switcher info side panel so its rows can show item tooltips
		# on hover. Auto row (vnum=0) opts itself out of tooltip wiring internally.
		if self.switcherInfoWindow:
			self.switcherInfoWindow.SetItemToolTip(tooltipItem)

	def __AnyAttributeConfigured(self):
		for i in xrange(switchbot.ALTERNATIVE_COUNT):
			for j in xrange(ATTR_SLOT_COUNT):
				(type, value) = switchbot.GetAttribute(self.selectedSlot, i, j)
				if type and value:
					return True
				
		return False
		
	def RefreshSwitchbotWindow(self):
		self.__RefreshItemSlots()
		self.__RefreshAlternatives()
		self.__RefreshAttributeRows()
		self.__RefreshButtons()
		self.__RefreshBonusSaverWindow()

	def __RefreshItemSlots(self):
		for i in xrange(switchbot.SLOT_COUNT):
			itemTab = self.itemTabs.get(i, None)
			if not itemTab:
				continue

			itemTab.RefreshItemSlot()

	if app.USE_SWITCHBOT_FIX_MEDIUM_STUFF:
		def RefreshSwitchbotItem(self):
			self.__RefreshItemSlots()
	else:
		def RefreshSwitchbotItem(self, slot):
			itemTab = self.itemTabs.get(slot, None)
			if not itemTab:
				return

			itemTab.RefreshItemSlot()

	def __RefreshAlternatives(self):
		if self.IsEmptySlot():
			self.alternativePanel.Hide()
		else:
			self.alternativePanel.Show()
	
	def __RefreshBonusSaverWindow(self):
		# The switcher window auto-shows/hides based on the selected slot's item
		# (has attributes + a valid switcher). The save window is user-toggled,
		# so it is left untouched here.
		if self.switcherInfoWindow:
			self.switcherInfoWindow.UpdateAutoVisibility()
			
	def __RefreshAttributeRows(self):
		# Show one row per attribute the item ACTUALLY has at that position —
		# normal slots (0..4) and rare slots (5..6) follow the same rule.
		#
		# Why: the bot only re-rolls existing attribute slots. CItem::ChangeAttribute
		# clears + repopulates the existing N normal slots (early-returns if N==0),
		# and CItem::ChangeRareAttribute early-returns when GetRareAttrCount()==0.
		# Showing empty rows for positions the item lacks would let the player
		# configure target attributes the bot can never satisfy, burning switchers
		# forever. The original pre-Task-2 UI got this right by reading the item's
		# actual attrs; this is the same logic, just extended to 7 slots.
		isEmpty = self.IsEmptySlot()
		for i in xrange(ATTR_SLOT_COUNT):
			row = self.attrDict.get(i, None)
			if not row:
				continue

			if isEmpty:
				row.Hide()
			else:
				(applyType, applyValue) = player.GetItemAttribute(player.SWITCHBOT, self.selectedSlot, i)
				if applyType and applyValue:
					row.Show()
				else:
					row.Hide()

			row.RefreshAttributeRow(self.selectedSlot, self.alternative, i)
			
	def __RefreshButtons(self):
		if self.IsEmptySlot() or not self.__AnyAttributeConfigured():
			self.toggleButton.Disable()
			self.resetButton.Disable()
			return

		self.toggleButton.Enable()

		# The single toggle advertises the action it will perform next.
		if self.IsActiveSlot():
			self.toggleButton.SetText(localeinfo.SWITCHBOT_STOP)
			self.resetButton.Disable()
		else:
			self.toggleButton.SetText(localeinfo.SWITCHBOT_START)
			self.resetButton.Enable()
			
	def __ClearAttributes(self):
		for index, row in self.attrDict.iteritems():
			for alternative in xrange(switchbot.ALTERNATIVE_COUNT):
				row.RefreshAttributeRow(self.selectedSlot, alternative, index)
	
	def __ResetAttributesConfig(self):
		for index, row in self.attrDict.iteritems():
			for alternative in xrange(switchbot.ALTERNATIVE_COUNT):
				row.ClearAttributeRow(self.selectedSlot, alternative, index)

	def __OnAttributeUpdate(self, attrIdx):
		self.__RefreshButtons()

	def __OnSearchAttribute(self, attrIdx):
		if self.attributeSearchWindow:
			self.attributeSearchWindow.Close()
			del self.attributeSearchWindow
			
		self.attrSearchIdx = attrIdx
		
		wnd = SearchListWindow()
		width = 260
		height = 260
		wnd.MakeWindow(width, height)
		wnd.SetTitleName(localeinfo.SWITCHBOT_SELECT_ATTR)
		wnd.SetAcceptArgsType("KEY_VALUE")

		(mouseX, mouseY) = wndMgr.GetMousePosition()

		if mouseX + width/2 > wndMgr.GetScreenWidth():
			xPos = wndMgr.GetScreenWidth() - width
		elif mouseX - width/2 < 0:
			xPos = 0
		else:
			xPos = mouseX - width/2
			
		if mouseY + height/2 > wndMgr.GetScreenHeight():
			yPos = wndMgr.GetScreenHeight() - height
		elif mouseY - height/2 < 0:
			yPos = 0
		else:
			yPos = mouseY - height/2

		wnd.SetPosition(xPos, yPos)

		# Rows 0..4 use the normal attr pool; rows 5..6 use the rare pool (6th/7th attrs).
		isRareRow = attrIdx >= NORM_ATTR_COUNT

		if not isRareRow:
			firstAttrType = player.GetItemAttribute(player.SWITCHBOT, self.selectedSlot, 0)[0]
			if firstAttrType in ADDON_TYPES.keys():
				for addonType, maxValue in ADDON_TYPES.iteritems():
					affectString = GetAffectString(addonType, maxValue)
					if not affectString:
						continue

					wnd.AppendItem(addonType, affectString)

			attributes = switchbot.GetAttributesForSet(self.selectedSlot)
		else:
			attributes = switchbot.GetRareAttributesForSet(self.selectedSlot)

		selectedAttributes = [switchbot.GetAttribute(self.selectedSlot, self.alternative, attrIndex)[0] for attrIndex in xrange(ATTR_SLOT_COUNT)]
		
		for (type, value) in attributes:
			if type in selectedAttributes:
				continue

			if isRareRow:
				# Rare pool: show every rare candidate from g_map_itemRare. No costume/normal-attr
				# filtering applies because rare attrs are sourced from a different table and the
				# server's CheckItem matches them against attr slots 5..6 by type, not position.
				affectString = GetAffectString(type, value)
				if not affectString:
					continue
				wnd.AppendItem(type, affectString)
				continue

			save_bonus = True
			ItemVNum = player.GetItemIndex(player.SWITCHBOT, self.selectedSlot)
			item.SelectItem(ItemVNum)
			itemType = item.GetItemType()
			isCustom  = (itemType == item.ITEM_TYPE_COSTUME)
			valid_item_vnums = {21219, 21218, 21217, 21216, 21215, 21214, 21213, 21212, 21211, 21210,
								21239, 21238, 21237, 21236, 21235, 21234, 21233, 21232, 21231, 21230,
								21279, 21278, 21277, 21276, 21275, 21274, 21273, 21272, 21271, 21270,
								21259, 21258, 21257, 21256, 21255, 21254, 21253, 21252, 21251, 21250,
								21220,21221,21222,21223,21224,21225,
								21240,21241,21242,21243,21244,21245,
								21260,21261,21262,21263,21264,21265,
								21280,21281,21282,21283,21284,21285,
								}

			#item.SelectItem(player.GetItemIndex(player.SWITCHBOT, self.selectedSlot))
			for i in xrange(item.ITEM_APPLY_MAX_NUM):
				affect_type, affect_value = item.GetAffect(i)
				if type == affect_type:
					if type == item.APPLY_ATTBONUS_HUMAN:
						save_bonus = True
						break
					elif affect_type in (item.APPLY_ATTBONUS_BOSS,
							 item.APPLY_ATTBONUS_STONE,
							 item.APPLY_ATTBONUS_MONSTER) and isCustom:
						save_bonus = True
						break
					elif type == item.APPLY_MAX_HP and ItemVNum in valid_item_vnums:
						save_bonus = True
						break
					else:
						save_bonus = False
						break

			if save_bonus is False:
				continue

			affectString = GetAffectString(type, value)
			if not affectString:
				continue

			wnd.AppendItem(type, affectString)
		
		wnd.SetAcceptEvent(ui.__mem_func__(self.__OnAcceptSearch))
		wnd.SetCancelEvent(ui.__mem_func__(self.__OnCancelSearch))
		wnd.SetTop()
		wnd.Open()

		self.attributeSearchWindow = wnd
		
	def __OnAcceptSearch(self, key, value):
		if self.attrSearchIdx < 0 or self.attrSearchIdx >= ATTR_SLOT_COUNT:
			return

		attrRow = self.attrDict.get(self.attrSearchIdx, None)
		if not attrRow:
			return

		isRareRow = self.attrSearchIdx >= NORM_ATTR_COUNT

		if isRareRow:
			maxValue = switchbot.GetRareAttributeMaxValue(self.selectedSlot, key)
		else:
			maxValue = ADDON_TYPES.get(key, 0)
			if not maxValue:
				maxValue = switchbot.GetAttributeMaxValue(self.selectedSlot, key)
			
		attrRow.SetAttribute(value, maxValue)
		switchbot.SetAttribute(self.selectedSlot, self.alternative, self.attrSearchIdx, key, maxValue)
		
		self.__RefreshButtons()
		
	def SetSavedAttribute(self, slot, alternative, attrIndex, attrType, attrValue):
		if attrIndex < 0 or attrIndex >= ATTR_SLOT_COUNT:
			return
			
		attrRow = self.attrDict.get(attrIndex, None)
		if not attrRow:
			return
			
		if slot >= switchbot.SLOT_COUNT:
			return
			
		if switchbot.IsActive(slot):
			return
			
		# Validate the loaded attrType against the correct pool for this row index.
		# Rare rows (5..6) check against the rare pool, normal rows (0..4) against the normal pool.
		if attrIndex >= NORM_ATTR_COUNT:
			var = switchbot.GetRareAttributesForSet(slot)
		else:
			var = switchbot.GetAttributesForSet(slot)
		attributes = [var[i][0] for i in xrange(len(var))]

		if attrIndex < NORM_ATTR_COUNT:
			firstAttrType = player.GetItemAttribute(player.SWITCHBOT, slot, 0)[0]
			if firstAttrType in ADDON_TYPES.keys():
				for addon in ADDON_TYPES.keys():
					attributes.append(addon)

		if not attrType in attributes:
			switchbot.SetAttribute(slot, alternative, attrIndex, 0, 0)
		else:
			switchbot.SetAttribute(slot, alternative, attrIndex, attrType, attrValue)
			
		self.RefreshSwitchbotWindow()
		
	def IsEmptySlot(self):
		slot = self.itemTabs.get(self.selectedSlot, None)
		if not slot:
			return True
			
		return slot.IsEmpty()
		
	def IsActiveSlot(self):
		slot = self.itemTabs.get(self.selectedSlot, None)
		if not slot:
			return False

		return slot.IsActive()
		
	def GetSlotAttributeCount(self):
		slot = self.itemTabs.get(self.selectedSlot, None)
		if not slot:
			return 0
			
		return slot.GetAttributeCount()
	
	def __OnCancelSearch(self):
		pass
	def OnUpdate(self):
		if self.putHereImage:
			if self.IsEmptySlot() and mousemodule.mouseController.isAttached():
				attachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()
				attachedSlotType = mousemodule.mouseController.GetAttachedType()
				
				item.SelectItem(attachedItemIndex)
				self.putHereImageItem.LoadImage(item.GetIconImageFileName())
				self.putHereImageItem.SetSwitchBotIconColor()
				y = 84 - self.putHereImageItem.GetHeight() / 2
				self.putHereImageItem.SetPosition(30, y)
				
				if constinfo.CanPutItemInSwitchbot(attachedItemIndex) and player.SLOT_TYPE_INVENTORY == attachedSlotType:
					self.putHereImage.LoadImage("d:/ymir work/ui/switchbot/put_here_image.tga")
					self.putHereImageItem.Show()
				else:
					self.putHereImage.LoadImage("d:/ymir work/ui/switchbot/cant_put_here_image.tga")
					self.putHereImageItem.Hide()
				self.putHereImage.Show()
			else:
				self.putHereImageItem.Hide()
				self.putHereImage.Hide()

		# Keep the switcher panel counts in sync with the player's inventory in real time.
		if self.switcherInfoWindow and self.switcherInfoWindow.IsShow() and not self.IsEmptySlot():
			self.switcherInfoWindow.OnUpdate()

	def OnPressEscapeKey(self):
		self.Close()
		return True

class SearchListWindow(ui.BoardWithTitleBar):
	class SearchListItem(ui.Window):
		LIST_ITEM_HEIGHT = 12
	
		def __init__(self, key, value):
			ui.Window.__init__(self)
			
			self.key = key
			self.value = value
			self.isDown = False
			self.onClickEvent = None	

			self.textLine = ui.TextLine()
			self.textLine.AddFlag("not_pick")
			self.textLine.SetParent(self)
			self.textLine.SetVerticalAlignCenter()
			self.textLine.SetWindowVerticalAlignCenter()
			self.textLine.SetText(str(value))
			self.textLine.Show()
				
		def __del__(self):
			ui.Window.__del__(self)
			
			self.key = None
			self.value = None
			
			self.onClickEvent = None
			
			self.textLine = 0
			
		def SetSize(self, width, height):
			ui.Window.SetSize(self, width, height)
			self.textLine.SetPosition(width + 2, -1)
			
		def OnMouseLeftButtonUp(self):
			if not self.isDown:
				self.__OnClick()
				self.Down()
				
		def OnRender(self):
			if self.IsIn() or self.isDown:
				self.RenderHoverOrSelected()
				
		def RenderHoverOrSelected(self):
			x, y = self.GetGlobalPosition()
			grp.SetColor(grp.GenerateColor((211.0/255.0), (121.0/255.0), (5.0/255.0), 0.7))
			grp.RenderBar(x+5, y, self.GetWidth(), self.GetHeight())
				
		def SetUp(self):
			self.isDown = False
			
		def Down(self):
			self.isDown = True
			
		def IsDown(self):
			return self.isDown
			
		def GetKey(self):
			return self.key
			
		def GetValue(self):
			return self.value
			
		def GetText(self):	
			return self.textLine.GetText()
			
		def MatchText(self, text):
			return text in self.GetText()
			
		def SetOnClickEvent(self, event):
			self.onClickEvent = ui.__mem_func__(event)
			
		def __OnClick(self):
			if self.onClickEvent:
				self.onClickEvent(self.key, self.value)
			
	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		self.AddFlag("attach")
		self.AddFlag("movable")
		
		self.__Initialize()
		
	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)
		self.__Initialize()
		
	def __Initialize(self):
		self.listItems = {}
		self.acceptEvent = None
		self.acceptArgsType = "VALUE"
		self.cancelEvent = None
		
	def MakeWindow(self, width, height, maxInput = 50):
		self.SetSize(width, height+7)
		
		self.searchInput = ui.ThinBoardCircle()
		self.searchInput.SetParent(self)
		self.searchInput.SetSize(width - (BORDER_SPACE*2), INPUT_HEIGHT)
		self.searchInput.SetPosition(BORDER_SPACE, BORDER_SPACE_TOP)
		self.searchInput.Show()
		
		self.searchEditLine = ui.EditLine()
		self.searchEditLine.SetParent(self.searchInput)
		self.searchEditLine.SetPosition(10, 8)
		self.searchEditLine.SetSize(self.searchInput.GetWidth() - 20, self.searchInput.GetHeight() - 16)
		self.searchEditLine.SetMax(maxInput)
		self.searchEditLine.SetReturnEvent(ui.__mem_func__(self.__OnAccept))
		self.searchEditLine.SetEscapeEvent(ui.__mem_func__(self.Close))
		self.searchEditLine.OnIMEUpdate = self.__OnSearchIMEUpdate
		self.searchEditLine.Show()
		
		containerHeight = height - (BORDER_SPACE_TOP + INPUT_HEIGHT + 30)
		
		self.container = ui.ThinBoardCircle()
		self.container.SetParent(self)
		self.container.SetPosition(BORDER_SPACE, BORDER_SPACE_TOP + INPUT_HEIGHT)
		self.container.SetSize(width - (BORDER_SPACE*2), containerHeight)
		self.container.Show()

		self.scrollBar = ui.NewScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetWindowHorizontalAlignRight()
		self.scrollBar.SetPosition(BORDER_SPACE + 6, BORDER_SPACE_TOP + INPUT_HEIGHT + 2 - 11)
		self.scrollBar.SetScrollBarSize(containerHeight+32 - 4)	
		
		listBoxHeight = self.container.GetHeight()
		listBoxWidth = self.container.GetWidth()
		
		self.listBox = ui.ListBoxEx()
		self.listBox.SetParent(self.container)
		self.listBox.SetPosition(2, 2)
		self.listBox.SetSize(listBoxWidth - 4, listBoxHeight- 4)
		self.listBox.SetItemStep(self.SearchListItem.LIST_ITEM_HEIGHT)
		self.listBox.SetViewItemCount(self.__GetViewItemCount())
		self.listBox.SetItemSize(listBoxWidth - 4, self.SearchListItem.LIST_ITEM_HEIGHT)
		self.listBox.SetScrollBar(self.scrollBar)
		self.listBox.Show()
		
		buttonWidth = width / 2 - 20
		
		self.acceptButton = ui.Button()
		self.acceptButton.SetParent(self)
		self.acceptButton.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.acceptButton.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.acceptButton.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.acceptButton.SetDisableVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.acceptButton.SetWindowVerticalAlignBottom()
		self.acceptButton.SetWindowHorizontalAlignCenter()
		self.acceptButton.SetPosition(buttonWidth / 2 - 5, 29)
		self.acceptButton.SetText(localeinfo.UI_ACCEPT)
		self.acceptButton.SetEvent(ui.__mem_func__(self.__OnAccept))
		self.acceptButton.Show()
		
		self.cancelButton = ui.Button()
		self.cancelButton.SetParent(self)
		self.cancelButton.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.cancelButton.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.cancelButton.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.cancelButton.SetDisableVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.cancelButton.SetWindowVerticalAlignBottom()
		self.cancelButton.SetWindowHorizontalAlignCenter()
		self.cancelButton.SetPosition(-buttonWidth / 2 - 5, 29)
		self.cancelButton.SetText(localeinfo.UI_CANCEL)
		self.cancelButton.SetEvent(ui.__mem_func__(self.__OnCancel))
		self.cancelButton.Show()
		
		self.__AdjustScrollbar()
		
	def __OnSearchIMEUpdate(self):
		ui.EditLine.OnIMEUpdate(self.searchEditLine)
		self.__RefreshListBox()
		
	def __GetViewItemCount(self):
		return self.container.GetHeight() / self.SearchListItem.LIST_ITEM_HEIGHT
		
	def __AdjustScrollbar(self):
		if len(self.listItems) > self.__GetViewItemCount():
			listBoxWidth = self.GetWidth() - (BORDER_SPACE*2)
			self.container.SetSize(listBoxWidth, self.container.GetHeight())
			self.listBox.SetSize(listBoxWidth - 4, self.listBox.GetHeight() - 4)
			self.listBox.SetItemSize(listBoxWidth - 4, self.SearchListItem.LIST_ITEM_HEIGHT)
			attachmentCount = len(self.listItems)
			scrollBarHeight = min(float(self.__GetViewItemCount()) / float(attachmentCount), 1.0)
			self.scrollBar.SetMiddleBarSize(scrollBarHeight)
			self.scrollBar.Show()
		else:
			listBoxWidth = self.GetWidth() - (BORDER_SPACE*2)
			self.container.SetSize(listBoxWidth, self.container.GetHeight())
			self.listBox.SetSize(listBoxWidth - 4, self.listBox.GetHeight() - 4)
			self.listBox.SetItemSize(listBoxWidth - 4, self.SearchListItem.LIST_ITEM_HEIGHT)
			self.scrollBar.Hide()
		
	def RemoveAllItems(self):
		self.listItems = {}
		self.listBox.RemoveAllItems()		
		
	def AppendItem(self, key, value = ""):
		if self.listItems.has_key(key):
			return
			
		if not value:
			value = key
			
		self.listItems[key] = { "value" : value, "item" : None, }
		self.__RefreshListBox()
		
	def __RefreshListBox(self):
		self.listBox.RemoveAllItems()
		
		self.__AdjustScrollbar()
		
		for key, dict in self.listItems.items():
			listItem = dict["item"]
			if not self.searchEditLine.GetText() or self.searchEditLine.GetText().lower() in dict["value"].lower():
				listItem = self.SearchListItem(key, dict["value"])
				listItem.SetOnClickEvent(self.__OnClickListItem)
				self.listBox.AppendItem(listItem)
			else:
				del listItem
			
	def GetSelectedItem(self):
		for listItem in self.listBox.GetItems():
			if listItem.IsDown():
				return listItem
				
		return None
		
	def SetCancelEvent(self, event):
		self.cancelEvent = event
		
	def SetAcceptEvent(self, event):
		self.acceptEvent = event
		
	def SetAcceptArgsType(self, type):
		self.acceptArgsType = type
		
	def __OnClickListItem(self, key, value):
		curItem = self.GetSelectedItem()
		if curItem:
			curItem.SetUp()
				
	def __OnCancel(self):
		if self.cancelEvent:
			self.cancelEvent()
			
		self.Close()
			
	def __OnAccept(self):
		selItem = self.GetSelectedItem()
		if not selItem:
			if len(self.listBox.GetItems()) == 1:
				selItem = self.listBox.GetItems()[0]
			else:
				return
	
		if self.acceptEvent:
			if self.acceptArgsType == "VALUES":
				self.acceptEvent(selItem.GetValue())
			elif self.acceptArgsType == "KEY":
				self.acceptEvent(selItem.GetKey())
			elif self.acceptArgsType == "KEY_VALUE":
				self.acceptEvent(selItem.GetKey(), selItem.GetValue())
			
		self.Close()
		
	def OnPressEscapeKey(self):
		self.Close()
		return True
		
	def Open(self):
		self.Show()
		self.searchEditLine.SetFocus()
		
	def Close(self):
		self.searchEditLine.SetText("")
		self.searchEditLine.KillFocus()
		self.Hide()


# -----------------------------------------------------------------------------
# Switcher info side-panel (Task 4)
# -----------------------------------------------------------------------------

# Custom image used as the visual icon for the "Auto" row. The Auto row has no
# real item behind it (vnum sent to the server is 0); the icon is purely visual
# branding so the entry sits cleanly next to the real switcher item icons. Path
# is the in-game pack path that maps to patch30/ymir work/ui/switchbot/.
SWITCHER_AUTO_ICON_PATH = "d:/ymir work/ui/switchbot/auto_switcher.png"


def _FormatSwitcherCount(count):
	"""Compact rendering: 0..9999 -> raw, 10000+ -> 10K / 99K, 1M+ -> 1.2M."""
	if count <= 0:
		return "0"
	if count >= 1000000:
		return "%.1fM" % (count / 1000000.0)
	if count >= 100000:
		return "%dK" % (count / 1000)
	return "%d" % count


SWITCHER_CHECK_ON_IMG  = "d:/ymir work/ui/game/common/checkbox_selected.png"
SWITCHER_CHECK_OFF_IMG = "d:/ymir work/ui/game/common/checkbox_normal.png"


class SwitcherCheck(ui.ImageBox):
	"""Tiny two-state toggle used as a switcher row's checkbox: shows
	checkbox_normal.png / checkbox_selected.png (16x16). Mirrors CheckBoxNew's
	minimal interface (GetCheck / SetCheck + a click event) so SwitcherRow can
	drive it the same way."""

	def __init__(self, event):
		ui.ImageBox.__init__(self)
		self.event = event
		self.checked = False
		self.LoadImage(SWITCHER_CHECK_OFF_IMG)
		self.Show()

	def __del__(self):
		ui.ImageBox.__del__(self)

	def GetCheck(self):
		return self.checked

	def SetCheck(self, flag):
		self.checked = bool(flag)
		self.LoadImage(SWITCHER_CHECK_ON_IMG if self.checked else SWITCHER_CHECK_OFF_IMG)

	def OnMouseLeftButtonUp(self):
		if self.event:
			self.event()


class SwitcherRow(ui.Window):
	"""One row in the switcher info list. RTL layout (Arabic client):

	    [checkbox] ....... [count] [icon]

	The slot uses GridSlotWindow so it gets the standard slot_base frame and
	icon rendering free. Real switcher rows render the item proto's icon via
	SetItemSlot. The Auto row (vnum=0) leaves the slot empty and overlays a
	custom image (SWITCHER_AUTO_ICON_PATH) inside the frame instead.
	The checkbox is single-select inside SwitcherInfoWindow (clicking one
	unchecks the others), behaving as a radio group visually styled as
	checkboxes."""

	HEIGHT      = 34
	SLOT_SIZE   = 32
	SLOT_MARGIN_RIGHT = 4     # gap from the row's right edge to the icon
	CHECK_SIZE  = 16
	CHECK_MARGIN_LEFT = 26     # gap from the row's left edge to the checkbox
	COUNT_GAP   = 6           # gap between the count text and the icon

	def __init__(self, width, vnum, isInfoOnly=False):
		ui.Window.__init__(self)
		self.SetSize(width, self.HEIGHT)
		self.SetPosition(0, 0)
		self.vnum = vnum
		self.onSelect = None
		self.isInfoOnly = isInfoOnly
		self.tooltipItem = None  # set later via SetItemToolTip()

		# RTL: the icon sits at the RIGHT edge of the row.
		slotX = width - self.SLOT_SIZE - self.SLOT_MARGIN_RIGHT
		slotY = (self.HEIGHT - self.SLOT_SIZE) / 2

		# Item slot frame - same look for every row, including Auto. count=0 hides
		# the stack-count overlay on the icon (player's inventory count is shown
		# as a separate text label).
		self.slot = ui.GridSlotWindow()
		self.slot.SetParent(self)
		self.slot.ArrangeSlot(0, 1, 1, self.SLOT_SIZE, self.SLOT_SIZE, 0, 0)
		self.slot.SetSlotBaseImage("d:/ymir work/ui/public/slot_base.sub", 1.0, 1.0, 1.0, 1.0)
		self.slot.SetPosition(slotX, slotY)
		# Tooltip hooks fire whenever the cursor enters/leaves the slot. The Auto
		# row (vnum=0) opts out of tooltip wiring inside SetItemToolTip.
		self.slot.SetOverInItemEvent(ui.__mem_func__(self.__OnOverInSlot))
		self.slot.SetOverOutItemEvent(ui.__mem_func__(self.__OnOverOutSlot))
		self.slot.Show()

		# Auto rows get a custom image overlay inside the slot frame. Real rows
		# get the item proto's icon via SetItemSlot.
		self.autoIcon = None
		if vnum == 0:
			self.autoIcon = ui.ImageBox()
			self.autoIcon.SetParent(self)
			self.autoIcon.LoadImage(SWITCHER_AUTO_ICON_PATH)
			# Center the image inside the slot frame (slot_base.sub has a 1px inset).
			self.autoIcon.SetPosition(slotX + 1, slotY + 1)
			self.autoIcon.Show()
		else:
			self.slot.SetItemSlot(0, vnum, 0)

		# Player's total count, right-aligned so its right edge sits just left of
		# the icon (RTL: the count reads immediately to the left of the item).
		self.countLabel = ui.TextLine()
		self.countLabel.SetParent(self)
		self.countLabel.SetHorizontalAlignLeft()
		self.countLabel.SetVerticalAlignCenter()
		self.countLabel.SetWindowVerticalAlignCenter()
		self.countLabel.SetPosition(slotX - self.COUNT_GAP, 0)
		self.countLabel.SetText("")
		self.countLabel.Show()

		# Clock checkbox at the LEFT edge (RTL: the toggle is on the far side from
		# the item). Info-only rows (the rare reroll info entry) have no checkbox.
		self.checkbox = None
		if not self.isInfoOnly:
			self.checkbox = SwitcherCheck(ui.__mem_func__(self.__OnCheckClick))
			self.checkbox.SetParent(self)
			self.checkbox.SetPosition(self.CHECK_MARGIN_LEFT, (self.HEIGHT - self.CHECK_SIZE) / 2)
			self.checkbox.Show()

	def __del__(self):
		ui.Window.__del__(self)

	def SetOnSelectEvent(self, event):
		self.onSelect = event

	def __OnCheckClick(self):
		if self.onSelect:
			self.onSelect(self.vnum)

	def SetItemToolTip(self, tooltipItem):
		# Only real-item rows get a tooltip — the Auto row (vnum=0) uses 71085 as
		# a placeholder icon that doesn't represent the actual behaviour, so its
		# tooltip would be misleading.
		if self.vnum == 0:
			self.tooltipItem = None
			return
		self.tooltipItem = tooltipItem

	def __OnOverInSlot(self, overSlotPos):
		if not self.tooltipItem:
			return
		self.tooltipItem.SetItemToolTip(self.vnum)
		self.tooltipItem.ShowToolTip()

	def __OnOverOutSlot(self):
		if not self.tooltipItem:
			return
		self.tooltipItem.HideToolTip()

	def SetCount(self, count):
		# Auto row carries no inventory count.
		if self.vnum == 0:
			self.countLabel.SetText("")
		else:
			self.countLabel.SetText(_FormatSwitcherCount(count))

	def SetSelected(self, selected):
		if self.checkbox:
			self.checkbox.SetCheck(selected)


class SwitcherInfoWindow(ui.NewBoardWithTitleBar):
	"""Standalone 'Choose Switch' window listing eligible switchers for the
	currently-selected slot of the main Switchbot window.

	It is no longer docked in the main window's right sidebar: it is its own
	titled, movable window that floats beside the main window. It auto-shows
	whenever the selected slot holds an item that has attributes and at least
	one valid switcher, and auto-hides otherwise (see UpdateAutoVisibility).

	Layout:
	  - Title bar (window title) at top
	  - Scrollable list of SwitcherRow entries (Auto + each eligible vnum),
	    capped at MAX_VISIBLE_ROWS visible; scrollbar appears when there's more
	  - Rare reroll info row at the bottom, info-only, when applicable

	The eligible-vnum list is server-authoritative: it's pushed by the server
	via SUBHEADER_GC_SWITCHBOT_ELIGIBLE_SWITCHERS and queried here via
	switchbot.GetEligibleSwitchers. Clicking a checkbox calls
	switchbot.SetPreferredSwitcher; the server validates and persists."""

	AUTO_VNUM = 0
	MAX_VISIBLE_ROWS = 5
	ROW_GAP          = 8
	CONTENT_X        = 10
	CONTENT_TOP      = 32
	SIDE_GAP         = 4

	def __init__(self, wndSwitchbot=None):
		ui.NewBoardWithTitleBar.__init__(self)

		if not wndSwitchbot:
			import exception
			exception.Abort("SwitcherInfoWindow.__init__ requires a parent SwitchbotWindow.")

		self.wndSwitchbot = wndSwitchbot
		self.rows = []
		self.rareRow = None
		self.tooltipItem = None
		self.__LoadWindow()

	def SetItemToolTip(self, tooltipItem):
		# Stored centrally; propagated to each row when (re)built in Refresh.
		self.tooltipItem = tooltipItem
		for row in self.rows:
			row.SetItemToolTip(tooltipItem)
		if self.rareRow:
			self.rareRow.SetItemToolTip(tooltipItem)

	def __del__(self):
		ui.NewBoardWithTitleBar.__del__(self)

	def Destroy(self):
		self.rows = []
		self.rareRow = None
		self.wndSwitchbot = None

	def __LoadWindow(self):
		listHeight = (SwitcherRow.HEIGHT + self.ROW_GAP) * self.MAX_VISIBLE_ROWS
		listWidth  = 132
		boardWidth  = self.CONTENT_X + listWidth + self.CONTENT_X
		boardHeight = self.CONTENT_TOP + listHeight + 10

		self.SetSize(boardWidth, boardHeight)
		self.AddFlag("movable")
		self.AddFlag("float")

		try:
			titleText = localeinfo.SWITCHBOT_ELIGIBLE_SWITCHERS
		except AttributeError:
			titleText = "Eligible switchers"
		self.SetTitleName(titleText)
		self.SetCloseEvent(ui.__mem_func__(self.Close))

		# ThinBoard v2 backdrop behind the list (see feedback: prefer v2 thinboard).
		self.listBg = ui.ThinBoard("UI", 2)
		self.listBg.SetParent(self)
		self.listBg.SetPosition(self.CONTENT_X - 2, self.CONTENT_TOP - 2)
		self.listBg.SetSize(listWidth + 4, listHeight + 4)
		self.listBg.Show()

		# Inner row width: leave 12px on the right for the scrollbar (whether or not
		# it's visible - keeps row layout stable across slot transitions).
		self.rowInnerWidth = listWidth - 12

		self.listContainer = ui.Window()
		self.listContainer.SetParent(self)
		self.listContainer.SetPosition(self.CONTENT_X, self.CONTENT_TOP)
		self.listContainer.SetSize(listWidth, listHeight)
		self.listContainer.Show()

		self.scrollBar = ui.NewScrollBar()
		self.scrollBar.SetParent(self.listContainer)
		self.scrollBar.SetWindowHorizontalAlignRight()
		self.scrollBar.SetPosition(2, 0)
		self.scrollBar.SetScrollBarSize(listHeight)

		self.listBox = ui.ListBoxEx()
		self.listBox.SetParent(self.listContainer)
		self.listBox.SetPosition(0, 0)
		self.listBox.SetSize(self.rowInnerWidth, listHeight)
		self.listBox.SetItemStep(SwitcherRow.HEIGHT + self.ROW_GAP)
		self.listBox.SetViewItemCount(self.MAX_VISIBLE_ROWS)
		self.listBox.SetItemSize(self.rowInnerWidth, SwitcherRow.HEIGHT)
		self.listBox.SetScrollBar(self.scrollBar)
		self.listBox.Show()

	def __AdjustScrollbar(self):
		# Show the scrollbar only when there's more content than the view can fit,
		# and size the thumb proportionally to the visible/total ratio.
		totalRows = len(self.rows)
		if totalRows > self.MAX_VISIBLE_ROWS:
			thumbRatio = min(float(self.MAX_VISIBLE_ROWS) / float(totalRows), 1.0)
			self.scrollBar.SetMiddleBarSize(thumbRatio)
			self.scrollBar.Show()
		else:
			self.scrollBar.Hide()

	def Refresh(self):
		# Tear down previous rows. listBox.RemoveAllItems takes care of any
		# rare row from a previous slot (it lives inside the listbox now).
		self.listBox.RemoveAllItems()
		self.rows = []
		self.rareRow = None

		if not self.wndSwitchbot:
			return
		if self.wndSwitchbot.IsEmptySlot():
			self.__AdjustScrollbar()
			return

		slot = self.wndSwitchbot.GetSelectedSlot()
		eligibles = switchbot.GetEligibleSwitchers(slot)
		preferred = switchbot.GetPreferredSwitcher(slot)

		# Auto row first — explicit toggle so player can revert to default.
		autoRow = SwitcherRow(self.rowInnerWidth, self.AUTO_VNUM)
		autoRow.SetOnSelectEvent(ui.__mem_func__(self.__OnSelect))
		autoRow.SetItemToolTip(self.tooltipItem)  # SwitcherRow internally skips Auto
		autoRow.SetSelected(preferred == 0)
		self.listBox.AppendItem(autoRow)
		self.rows.append(autoRow)

		# Eligible switcher rows in server-priority order.
		for vnum in eligibles:
			row = SwitcherRow(self.rowInnerWidth, vnum)
			row.SetOnSelectEvent(ui.__mem_func__(self.__OnSelect))
			row.SetItemToolTip(self.tooltipItem)
			row.SetCount(player.GetItemCountByVnum(vnum))
			row.SetSelected(preferred == vnum)
			self.listBox.AppendItem(row)
			self.rows.append(row)

		# Rare reroll info row, appended INSIDE the listbox (so it scrolls with
		# the other rows and never overflows the sidebar bounds). Gated by two
		# conditions: (a) the server told us about a rare switcher vnum, AND
		# (b) the item in this slot actually has at least one 6th/7th attribute.
		# Without (b) the bot can't reroll rare attrs (see switchbot.cpp Start
		# guard), so surfacing the row would be misleading.
		rareVnum = switchbot.GetRareSwitcherVnum()
		if rareVnum and self.__ItemHasRareAttrs(slot):
			rr = SwitcherRow(self.rowInnerWidth, rareVnum, isInfoOnly=True)
			rr.SetItemToolTip(self.tooltipItem)
			rr.SetCount(player.GetItemCountByVnum(rareVnum))
			self.listBox.AppendItem(rr)
			self.rows.append(rr)
			self.rareRow = rr

		self.__AdjustScrollbar()

	def __ItemHasRareAttrs(self, slot):
		# Rare attrs live at indices NORM_ATTR_COUNT..ITEM_ATTRIBUTE_SLOT_MAX_NUM-1
		# (i.e. positions 5 and 6 on the item). Mirrors the visibility rule used
		# for the attribute target rows in __RefreshAttributeRows.
		for i in xrange(NORM_ATTR_COUNT, player.ATTRIBUTE_SLOT_MAX_NUM):
			(attrType, _) = player.GetItemAttribute(player.SWITCHBOT, slot, i)
			if attrType:
				return True
		return False

	def __OnSelect(self, vnum):
		if not self.wndSwitchbot:
			return
		slot = self.wndSwitchbot.GetSelectedSlot()
		switchbot.SetPreferredSwitcher(slot, vnum)
		# Enforce single-select inside the list (only the clicked row stays checked).
		for row in self.rows:
			row.SetSelected(row.vnum == vnum)

	def OnUpdate(self):
		# Live count refresh - cheap inventory lookup per visible row. The rare
		# row is now part of self.rows when present, so this single loop covers
		# everything.
		for row in self.rows:
			if row.vnum != self.AUTO_VNUM:
				row.SetCount(player.GetItemCountByVnum(row.vnum))

	def __HasValidSwitcher(self):
		# A slot has a "valid switcher" when the server pushed at least one
		# eligible switcher vnum for it, or a rare switcher applies to a 6th/7th
		# attribute the item actually carries.
		if not self.wndSwitchbot:
			return False
		slot = self.wndSwitchbot.GetSelectedSlot()
		if switchbot.GetEligibleSwitchers(slot):
			return True
		rareVnum = switchbot.GetRareSwitcherVnum()
		return bool(rareVnum and self.__ItemHasRareAttrs(slot))

	def __PositionBesideMain(self):
		# Float to the LEFT of the main window; fall back to the right edge if
		# there isn't room on the left.
		if not self.wndSwitchbot:
			return
		(mx, my) = self.wndSwitchbot.GetGlobalPosition()
		x = mx - self.GetWidth() - self.SIDE_GAP
		if x < 0:
			x = mx + self.wndSwitchbot.GetWidth() + self.SIDE_GAP
		self.SetPosition(x, my)

	def UpdateAutoVisibility(self):
		# Auto-show only when the selected slot holds a switchable item (has
		# attributes AND a valid switcher). Position beside the main window the
		# first time it becomes visible; leave it wherever the player dragged it
		# afterwards.
		if not self.wndSwitchbot:
			return
		if self.wndSwitchbot.IsEmptySlot() or not self.__HasValidSwitcher():
			self.Hide()
			return
		wasShown = self.IsShow()
		if not wasShown:
			self.__PositionBesideMain()
		self.Show()
		if not wasShown:
			self.SetTop()
		self.Refresh()

	def Open(self):
		self.__PositionBesideMain()
		self.Show()
		self.SetTop()
		self.Refresh()

	def Close(self):
		self.Hide()


class ConfigurationWindow(ui.NewBoardWithTitleBar):
	"""Standalone 'Save Configuration' window. No longer docked in the main
	window's right sidebar - it is its own titled, movable window that floats
	beside the main window and is opened via a button on the main window."""

	CONTENT_X        = 10
	CONTENT_TOP      = 32
	SIDE_GAP         = 4
	ROW_GAP          = 4
	MAX_VISIBLE_ROWS = 6

	class ConfigurationLine(ui.Window):
		LIST_ITEM_HEIGHT = 30

		id = 0
		name = ""

		loadEvent = None
		deleteEvent = None

		def __init__(self, width):
			ui.Window.__init__(self)

			self.SetSize(width, self.LIST_ITEM_HEIGHT)

			# RTL: config name on the RIGHT, apply/delete buttons on the LEFT.
			self.nameTextLine = ui.TextLine()
			self.nameTextLine.SetParent(self)
			self.nameTextLine.SetVerticalAlignCenter()
			self.nameTextLine.SetWindowVerticalAlignCenter()
			# SetHorizontalAlignLeft anchors the text's RIGHT edge at X and flows
			# it leftward - the correct RTL alignment (see Arabic-align note).
			self.nameTextLine.SetHorizontalAlignLeft()
			self.nameTextLine.SetPosition(width - 8, -1)
			self.nameTextLine.Show()

			self.loadButton = ui.Button()
			self.loadButton.SetParent(self)
			self.loadButton.SetUpVisual("d:/ymir work/ui/switchbot/load_attr_01.sub")
			self.loadButton.SetOverVisual("d:/ymir work/ui/switchbot/load_attr_02.sub")
			self.loadButton.SetDownVisual("d:/ymir work/ui/switchbot/load_attr_03.sub")
			self.loadButton.SetDisableVisual("d:/ymir work/ui/switchbot/load_attr_03.sub")
			self.loadButton.SetWindowVerticalAlignCenter()
			self.loadButton.SetPosition(6, 1)
			self.loadButton.SetToolTipText(localeinfo.SWITCHBOT_LOAD_CONFIGURATION)
			self.loadButton.SetEvent(ui.__mem_func__(self.__OnClickLoadButton))
			self.loadButton.Show()

			self.deleteButton = ui.Button()
			self.deleteButton.SetParent(self)
			self.deleteButton.SetUpVisual("d:/ymir work/ui/switchbot/delete_attr_01.sub")
			self.deleteButton.SetOverVisual("d:/ymir work/ui/switchbot/delete_attr_02.sub")
			self.deleteButton.SetDownVisual("d:/ymir work/ui/switchbot/delete_attr_03.sub")
			self.deleteButton.SetDisableVisual("d:/ymir work/ui/switchbot/delete_attr_03.sub")
			self.deleteButton.SetWindowVerticalAlignCenter()
			self.deleteButton.SetPosition(30, 1)
			self.deleteButton.SetToolTipText(localeinfo.SWITCHBOT_CLEAR_CONFIGURATION)
			self.deleteButton.SetEvent(ui.__mem_func__(self.__OnClickDeleteButton))
			self.deleteButton.Show()
			
		def __del__(self):
			ui.Window.__del__(self)
			
		def Load(self, id, name):
			self.id = id
			self.name = name
			self.nameTextLine.SetText(name)
			
		def SetLoadEvent(self, event):
			self.loadEvent = event
			
		def SetDeleteEvent(self, event):
			self.deleteEvent = event
			
		def __OnClickLoadButton(self):
			if self.loadEvent:
				self.loadEvent(self.id)
			
		def __OnClickDeleteButton(self):
			if self.deleteEvent:
				self.deleteEvent(self.id)
	
	wndSwitchbot = None
	valueEditLine = None
	
	dict = {}
	
	listItems = {}
	
	def __init__(self, wndSwitchbot=None):
		ui.NewBoardWithTitleBar.__init__(self)

		if not wndSwitchbot:
			import exception
			exception.Abort("ConfigurationWindow.__init__ Cannot initialize without binding to Switchbot window.")

		self.wndSwitchbot = wndSwitchbot

		self.__LoadWindow()

	def __del__(self):
		ui.NewBoardWithTitleBar.__del__(self)

	def Destroy(self):
		self.nameEditLine = None
		self.nameInput = None
		self.saveButton = None
		self.scrollBar = None
		self.container = None
		self.listBox = None

		self.listItems = {}
		self.wndSwitchbot = None

	def __LoadWindow(self):
		self.listWidth = 200
		rowStep        = self.ConfigurationLine.LIST_ITEM_HEIGHT + self.ROW_GAP
		listHeight     = rowStep * self.MAX_VISIBLE_ROWS
		inputHeight    = 24
		topRowHeight   = inputHeight + 6
		boardWidth     = self.CONTENT_X + self.listWidth + self.CONTENT_X
		boardHeight    = self.CONTENT_TOP + topRowHeight + listHeight + 12

		self.SetSize(boardWidth, boardHeight)
		self.AddFlag("movable")
		self.AddFlag("float")

		try:
			titleText = localeinfo.SWITCHBOT_CONFIGURATION_TITLE
		except AttributeError:
			titleText = "Save Configuration"
		self.SetTitleName(titleText)
		self.SetCloseEvent(ui.__mem_func__(self.Close))

		# RTL top row: save (commit) button on the LEFT, framed name field on the right.
		self.saveButton = ui.Button()
		self.saveButton.SetParent(self)
		self.saveButton.SetUpVisual("d:/ymir work/ui/switchbot/buttons/save_bonus_norm.tga")
		self.saveButton.SetOverVisual("d:/ymir work/ui/switchbot/buttons/save_bonus_hover.tga")
		self.saveButton.SetDownVisual("d:/ymir work/ui/switchbot/buttons/save_bonus_down.tga")
		self.saveButton.SetPosition(self.CONTENT_X, self.CONTENT_TOP + 1)
		self.saveButton.SetToolTipText(localeinfo.SWITCHBOT_SAVE)
		self.saveButton.SetEvent(ui.__mem_func__(self.__OnSave))
		self.saveButton.Show()

		# The name field gets the same rounded input frame the attribute rows use,
		# otherwise the raw EditLine renders as a bare line on the board.
		nameX = self.CONTENT_X + 30
		nameW = self.CONTENT_X + self.listWidth - nameX

		self.nameInput = ui.ThinBoardCircle()
		self.nameInput.SetParent(self)
		self.nameInput.SetSize(nameW, inputHeight)
		self.nameInput.SetPosition(nameX, self.CONTENT_TOP)
		self.nameInput.Show()

		self.nameEditLine = ui.EditLine()
		self.nameEditLine.SetParent(self.nameInput)
		self.nameEditLine.SetSize(nameW - 12, 18)
		self.nameEditLine.SetMax(19)
		self.nameEditLine.SetMaxSizeMode(70)
		self.nameEditLine.SetPosition(6, 4)
		self.nameEditLine.SetPlaceHolder(localeinfo.INTERFACE_TEXT_32)
		self.nameEditLine.Show()
		self.nameEditLine.SetEscapeEvent(ui.__mem_func__(self.__OnEscapeEvent))

		# ThinBoard v2 backdrop behind the list (see feedback: prefer v2 thinboard).
		listTop = self.CONTENT_TOP + topRowHeight
		self.listBg = ui.ThinBoard("UI", 2)
		self.listBg.SetParent(self)
		self.listBg.SetPosition(self.CONTENT_X - 2, listTop - 2)
		self.listBg.SetSize(self.listWidth + 4, listHeight + 4)
		self.listBg.Show()

		self.container = ui.Window()
		self.container.SetParent(self)
		self.container.SetPosition(self.CONTENT_X, listTop)
		self.container.SetSize(self.listWidth, listHeight)
		self.container.Show()

		self.scrollBar = ui.NewScrollBar()
		self.scrollBar.SetParent(self.container)
		self.scrollBar.SetWindowHorizontalAlignRight()
		self.scrollBar.SetPosition(2, 0)
		self.scrollBar.SetScrollBarSize(listHeight)

		self.listBox = ui.ListBoxEx()
		self.listBox.SetParent(self.container)
		self.listBox.SetPosition(0, 2)
		self.listBox.SetSize(self.listWidth, listHeight)
		self.listBox.SetItemStep(rowStep)
		self.listBox.SetViewItemCount(self.__GetViewItemCount())
		self.listBox.SetItemSize(self.listWidth, self.ConfigurationLine.LIST_ITEM_HEIGHT)
		self.listBox.SetScrollBar(self.scrollBar)
		self.listBox.Show()

		self.__AdjustScrollbar()
		
	def LoadConfigurations(self):
		try:
			f = open('switchbot.pkl', 'rb')
			self.dict = pickle.load(f)

		except IOError:
			self.dict = {}	
		
		self.listBox.RemoveAllItems()
			
		lineWidth = self.listBox.GetWidth()
		if len(self.dict) > self.__GetViewItemCount():	
			lineWidth -= 20
			
		self.__AdjustScrollbar()
			
		for key in self.dict.iterkeys():
			config = self.dict.get(key, None)
			if not config:
				continue
				
			line = self.ConfigurationLine(lineWidth)
			line.Load(key, config["name"])
			line.SetLoadEvent(ui.__mem_func__(self.__OnApplyConfiguration))
			line.SetDeleteEvent(ui.__mem_func__(self.__OnDeleteConfiguration))
			self.listBox.AppendItem(line)
			
			self.listItems[key] = line
			
	def SaveConfigurations(self):
		with open('switchbot.pkl', 'wb') as f:
			pickle.dump(self.dict, f)
			
	def __OnApplyConfiguration(self, key):
		config = self.dict.get(key, None)
		if not config:
			return
			
		if not self.wndSwitchbot:
			return
			
		selectedSlot = self.wndSwitchbot.GetSelectedSlot()			
		for alternativeIdx in xrange(len(config["alternatives"])):
			alternative = config["alternatives"][alternativeIdx]
			for attrIdx in xrange(len(alternative)):
				(attrType, attrValue) = alternative[attrIdx]
				self.wndSwitchbot.SetSavedAttribute(selectedSlot, alternativeIdx, attrIdx, attrType, attrValue)
		
	def __OnDeleteConfiguration(self, key):
		config = self.dict.get(key, None)
		if not config:
			return
			
		del self.listItems[key]
		del self.dict[key]
		self.SaveConfigurations()
		self.LoadConfigurations()
			
	def __PositionBesideMain(self):
		# Float to the LEFT of the main window; fall back to the right edge if
		# there isn't room on the left.
		if not self.wndSwitchbot:
			return
		(mx, my) = self.wndSwitchbot.GetGlobalPosition()
		x = mx - self.GetWidth() - self.SIDE_GAP
		if x < 0:
			x = mx + self.wndSwitchbot.GetWidth() + self.SIDE_GAP
		self.SetPosition(x, my)

	def Open(self):
		self.__PositionBesideMain()
		self.Show()
		self.SetTop()
		self.LoadConfigurations()

	def Close(self):
		if self.nameEditLine:
			self.nameEditLine.KillFocus()
		self.Hide()

	def __GetViewItemCount(self):
		return self.container.GetHeight() / (self.ConfigurationLine.LIST_ITEM_HEIGHT + self.ROW_GAP)

	def __AdjustScrollbar(self):
		# Fixed-width list now; just toggle the scrollbar and size its thumb.
		itemCount = len(self.dict)
		viewCount = self.__GetViewItemCount()
		if itemCount > viewCount:
			ratio = min(float(viewCount) / float(itemCount), 1.0)
			self.scrollBar.SetMiddleBarSize(ratio)
			self.scrollBar.Show()
		else:
			self.scrollBar.Hide()

	def __OnEscapeEvent(self):
		self.Close()
		
	def __GetNewKey(self):
		key = 0
		while self.dict.has_key(key):
			key += 1
			
		return key
		
	def __BuildDict(self, slot, name):	
		key = self.__GetNewKey()
		alternatives = []
		for alternative in xrange(switchbot.ALTERNATIVE_COUNT):
			attributes = [switchbot.GetAttribute(slot, alternative, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
			alternatives.append(attributes)
		
		new_dict = {
			"name" : name,
			"alternatives" : alternatives,
		}
		
		return (key, new_dict)
		
	def __OnSave(self):
		if not self.wndSwitchbot:
			return
			
		selectedSlot = self.wndSwitchbot.GetSelectedSlot()
		name = self.nameEditLine.GetText()
		
		if not name:
			return
		
		(key, new_dict) = self.__BuildDict(selectedSlot, name)
		self.dict[key] = new_dict
		
		self.nameEditLine.SetText("")
		
		self.SaveConfigurations()
		self.LoadConfigurations()
		
