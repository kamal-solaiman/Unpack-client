
import ui
import app
import grp
import net
import chat
import item
from _weakref import proxy
import nonplayer
import wndMgr
import localeinfo
import player
import mousemodule
import time
from datetime import datetime, timedelta
import constinfo
import uitooltip
import uicommon
import math

if app.ENABLE_INGAME_WIKI:
	import wiki
	import ingamewikiui

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

import missionpoolconfig

PATH_ROOT = "d:/ymir work/ui/mission_system/"
INFO_ROOT = "d:/ymir work/ui/game/wheel/"
def MakeTextLineRightAlign(parent):
	textLine = ui.TextLine()
	textLine.SetParent(parent)
	textLine.SetWindowHorizontalAlignRight()
	textLine.SetWindowVerticalAlignCenter()
	textLine.SetHorizontalAlignRight()
	textLine.SetVerticalAlignCenter()
	textLine.SetPosition(3, 0)
	textLine.Show()
	return textLine

## Configuration
TYPE_MONSTERS	= 1
TYPE_STONES 	= 2
TYPE_BOSSES	= 3
TYPE_MINING	= 4
TYPE_FISHING	= 5
TYPE_DUNGEON	= 6
TYPE_USE_ITEM	= 7

DUNGEON_NAME = {
	# VnumTarget : NameDungeon
	0	: localeinfo.MISSIONLIST_DUNGEON_ANY,
	694	: localeinfo.MISSIONLIST_DUNGEON_363, # orc dungeon 35 - 74
	1093	: localeinfo.MISSIONLIST_DUNGEON_66,# devil tower 50 - 99
	2092	: localeinfo.MISSIONLIST_DUNGEON_216, # barone 60 - 99
	2598	: localeinfo.MISSIONLIST_DUNGEON_217, # catacomb 75 - 99
	2493	: localeinfo.MISSIONLIST_DUNGEON_208, # beran 75 - 99
	5623	: localeinfo.MISSIONLIST_DUNGEON_5623, # beran dark 90 - 99
}

INFO_TYPES = {
	# "prefix for types"
	TYPE_MONSTERS : localeinfo.MISSIONLIST_TYPE_MONSTERS,
	TYPE_STONES : localeinfo.MISSIONLIST_TYPE_STONES,
	TYPE_BOSSES : localeinfo.MISSIONLIST_TYPE_BOSSES,
	TYPE_MINING : localeinfo.MISSIONLIST_TYPE_MINING,
	TYPE_FISHING : localeinfo.MISSIONLIST_TYPE_FISHING,
	TYPE_DUNGEON : localeinfo.MISSIONLIST_TYPE_DUNGEON,
	TYPE_USE_ITEM : localeinfo.MISSIONLIST_TYPE_USE_ITEM,
	8 : localeinfo.MISSIONLIST_TYPE_WRITE_SHOUT,
	9 : localeinfo.MISSIONLIST_TYPE_CHANGE_ATTR,
}

def GetNameByTypeVnum(type, vnum, count):
	prefix = INFO_TYPES[type]

	if type == TYPE_MONSTERS: # monsters
		monster_name = nonplayer.GetMonsterName(vnum) if vnum else localeinfo.MISSIONLIST_ANY_MONSTERS
		return "%s x%d %s" % (prefix, count, monster_name)
	if type == TYPE_STONES: # stones
		monster_name = nonplayer.GetMonsterName(vnum) if vnum else localeinfo.MISSIONLIST_ANY_STONES
		return "%s x%d %s" % (prefix, count, monster_name)
	if type == TYPE_BOSSES: # Bosses
		monster_name = nonplayer.GetMonsterName(vnum) if vnum else localeinfo.MISSIONLIST_ANY_BOSSES
		return "%s x%d %s" % (prefix, count, monster_name)
	elif type == TYPE_MINING or type == TYPE_FISHING: # mine/fishing
		return "%s x%d" % (prefix, count)
	elif type == TYPE_DUNGEON:
		return "%s %dx %s" % (prefix, count, DUNGEON_NAME.get(vnum, "NoName"))
	elif type == TYPE_USE_ITEM: # use item
		item.SelectItem(vnum)
		item_name = item.GetItemName()
		return "%s x%d %s" % (prefix, count, item_name)
	elif type == 8: # MQ_WRITE_SHOUT
		return "%s x%d" % (prefix, count)
	elif type == 9: # MQ_USE_ITEM_SWITCH
		return "%s x%d" % (prefix, count)

	return ""

class ListBox(ui.Window):
	class NewItem(ui.Window):
		def __init__(self, category, index, minLevel, maxLevel):
			ui.Window.__init__(self)
			self.category 	= category
			self.index 		= index
			self.minLevel 	= minLevel
			self.maxLevel 	= maxLevel

			self.vnum = 0
			self.count = 0

			self.Reinitialize()

		def SetItemToolTip(self, tooltipItem):
			self.tooltipItem = tooltipItem
			
		def AppendReward(self, vnum, count):
			if vnum == 0:
				return
			
			self.vnum = vnum
			self.count = count
			
			item.SelectItem(vnum)

			newReward = ui.ExpandedImageBox()
			newReward.SetParent(self)
			newReward.LoadImage(item.GetIconImageFileName())
			newReward.SetPosition(185 if localeinfo.IsARABIC() else 0, 0)
			newReward.Show()
			
			newReward.SetStringEvent("MOUSE_OVER_IN",ui.__mem_func__(self.OverInReward), vnum)
			newReward.SetStringEvent("MOUSE_OVER_OUT",ui.__mem_func__(self.OverOutReward))
			
			newName = ui.MakeTextLineNew(self, 185 if localeinfo.IsARABIC() else 35 , -1, "x%d %s" % (count, item.GetItemName()))
			newName.SetWindowVerticalAlignCenter()
			newName.SetVerticalAlignCenter()
			newName.SetOutline()
			newName.SetWindowName("text")
		
			self.newReward = newReward
			self.newName = newName

			self.SetSize(newReward.GetWidth() + 250 if localeinfo.IsARABIC() else newReward.GetWidth(), newReward.GetHeight())

		def OnRender(self):
			xList, yList = self.parent.GetGlobalPosition()
			width, height = self.parent.GetWidth(), self.parent.GetHeight()	
			for image in [self.newReward, self.newName]:
				if image.GetWindowName() == "text":
					xText, yText = image.GetGlobalPosition()
					image.Hide() if yText < yList or yText + image.GetTextSize()[1] > yList + height else image.Show()
					
					# if xText + image.GetTextSize()[0] > xList + width:
						# image.Hide()
				else:
					self.SetClipRect(image, xList, yList, xList + width, yList + height)

		def SetClipRect(self, image, fLeft, fTop, fRight, fBottom):
			if image.GetWidth() == 0 and image.GetHeight() == 0:
				return
		
			(left, top, right, bottom) = image.GetRect()
			right = right + left
			bottom = bottom + top
			
			#calculate
			fDifLeft = -(float(fLeft - left) / float(image.GetWidth())) if (left < fLeft) else 0.0
			fDifTop = -(float(fTop - top) / float(image.GetHeight())) if (top < fTop) else 0.0
			fDifRight = -(float(right - fRight) / float(image.GetWidth())) if (right > fRight) else 0.0
			fDifBottom = -(float(bottom - fBottom) / float(image.GetHeight())) if (bottom > fBottom) else  0.0
			
			image.SetRenderingRect(fDifLeft, fDifTop, fDifRight, fDifBottom)

		def __del__(self):
			ui.Window.__del__(self)
			self.Reinitialize()
			
		def Reinitialize(self):
			self.xBase = 0
			self.yBase = 0

			self.tooltipItem = None

		def SetParent(self, parent):
			ui.Window.SetParent(self, parent)
			self.parent = proxy(parent)

		def SetBasePosition(self, x, y):
			self.xBase = x
			self.yBase = y
			
		def GetBasePosition(self):
			return (self.xBase, self.yBase)
			
		def OverInReward(self, vnum):
			if self.tooltipItem:
				self.tooltipItem.SetItemToolTip(vnum)
		
		def OverOutReward(self):
			if self.tooltipItem:
				self.tooltipItem.HideToolTip()

	def __init__(self):
		ui.Window.__init__(self)
		self.Reinitialize()

	def __del__(self):
		ui.Window.__del__(self)
		self.Reinitialize()
		
	def Destroy(self):
		self.Reinitialize()
		
	def Reinitialize(self):
		self.itemList = []
		self.scrollBar = None
		self.tooltipItem = None
		
		self.selectEvent = None

	def SetParent(self, parent):
		ui.Window.SetParent(self, parent)
		
		self.SetSize(parent.GetWidth() - 10, parent.GetHeight() - 10)
		
	def SetScrollBar(self, scrollBar):
		scrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		scrollBar.SetScrollStep(0.2)
		self.scrollBar = scrollBar

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem
		
	def SetSelectEvent(self, event):
		self.selectEvent = event
		
	def __OnScroll(self):
		self.AdjustItemPositions(True)
		
	def ManageItemByLevelRange(self, itemW):
		myLevel = player.GetStatus(player.LEVEL)
		if myLevel < itemW.minLevel or myLevel > itemW.maxLevel:
			itemW.Hide()
		else:
			itemW.Show()

	def GetTotalItemHeight(self):
		totalHeight = 0
		
		if self.itemList:
			for itemH in self.itemList:
				
				self.ManageItemByLevelRange(itemH)
				if itemH.IsShow() == FALSE:
					continue

				totalHeight += itemH.GetHeight() + 2
			
		return totalHeight

	def GetItemCount(self):
		return len(self.itemList)
	
	def HasItemReward(self, itemVnum, itemCount, minLevel, maxLevel):
		for itemH in self.itemList:
			if minLevel != itemH.minLevel or maxLevel != itemH.maxLevel:
				continue
		
			if itemH.vnum == itemVnum and itemH.count == itemCount:
				return True

		return False
	
	def AppendItemReward(self, category, index, vnum, count, minLevel, maxLevel):
		item = self.NewItem(category, index, minLevel, maxLevel)
		item.SetParent(self)
		item.SetItemToolTip(self.tooltipItem)
		item.AppendReward(vnum, count)
		
		if len(self.itemList) == 0:
			item.SetBasePosition(0, 0)
		else:
			x, y = self.itemList[-1].GetLocalPosition()
			y += 2
			item.SetBasePosition(0, y + self.itemList[-1].GetHeight())
		
		item.Show()
		self.itemList.append(item)
		
		self.AdjustScrollBar()
		self.AdjustItemPositions()
		
		return item

	def AdjustScrollBar(self):
		totalHeight = float(self.GetTotalItemHeight())
		if totalHeight:
			scrollBarHeight = min(float(self.GetHeight() - 10) / totalHeight, 1.0)
		else:
			scrollBarHeight = 1.0
	
		self.scrollBar.SetMiddleBarSize(scrollBarHeight)
		
		if totalHeight < self.GetHeight(): # fixme scroll
			self.scrollBar.Hide()
		else:
			self.scrollBar.Show()
	
	def ResetScrollbar(self):
		self.scrollBar.SetPos(0)

	def AdjustItemPositions(self, scrolling = False, startIndex = -1):		
		scrollPos = self.scrollBar.GetPos()
		totalHeight = self.GetTotalItemHeight() - self.GetHeight()

		idx = 0
		if startIndex >= 0:
			idx = startIndex

		yAccumulate = 0
		for item in self.itemList[idx:]:
			if item.IsShow() == FALSE:
				continue
			
			if startIndex >= 0:
				yAccumulate -= item.GetHeight()
			
			if scrolling:
				setPos = yAccumulate - int(scrollPos * totalHeight)
				item.SetPosition(0, setPos)
			else:
				item.SetPosition(0, yAccumulate)
				
			item.SetBasePosition(0, yAccumulate)

			yAccumulate += item.GetHeight() + 2

	def SelectItem(self):
		if self.selectEvent:
			self.selectEvent()

	def Clear(self, bIsRefresh = False):
		if len(self.itemList) == 0:
			return
	
		for item in self.itemList:
			item.Reinitialize()
			item.Hide()
			del item
		
		if bIsRefresh == False:
			self.tooltipItem = None
		self.itemList = []

class MissionPreviewItem(ui.Window):
	"""Item class for displaying a mission preview in the mission pool list"""
	def __init__(self):
		ui.Window.__init__(self)
		self.missionType = 0
		self.targetVnum = 0
		self.count = 0
		self.minLevel = 0
		self.maxLevel = 0

		self.textLine = ui.TextLine()
		self.textLine.SetParent(self)
		self.textLine.SetPosition(5, 0)
		self.textLine.SetOutline()
		self.textLine.Show()

		self.SetSize(230, 18)

	def SetMission(self, missionType, targetVnum, count, minLevel, maxLevel):
		self.missionType = missionType
		self.targetVnum = targetVnum
		self.count = count
		self.minLevel = minLevel
		self.maxLevel = maxLevel

		# Use existing function to get mission description
		missionText = GetNameByTypeVnum(missionType, targetVnum, count)
		self.textLine.SetText(missionText)

	def GetHeight(self):
		return 18

class MissionListBox(ui.Window):
	"""ListBox for displaying mission pool previews"""
	def __init__(self):
		ui.Window.__init__(self)
		self.itemList = []
		self.scrollBar = None
		self.basePos = 0

	def SetScrollBar(self, scrollBar):
		self.scrollBar = scrollBar
		self.scrollBar.SetScrollEvent(ui.__mem_func__(self.OnScroll))

	def OnScroll(self):
		if not self.scrollBar:
			return
		pos = self.scrollBar.GetPos()
		self.basePos = int(pos * max(0, len(self.itemList) - 10))
		self.RefreshItemPositions()

	def AppendMission(self, missionType, targetVnum, count, minLevel, maxLevel):
		item = MissionPreviewItem()
		item.SetParent(self)
		item.SetMission(missionType, targetVnum, count, minLevel, maxLevel)
		item.Show()
		self.itemList.append(item)
		self.RefreshItemPositions()

	def RefreshItemPositions(self):
		yPos = 0
		for i, item in enumerate(self.itemList):
			if i < self.basePos:
				item.Hide()
			elif i < self.basePos + 10:
				item.SetPosition(0, yPos)
				item.Show()
				yPos += item.GetHeight()
			else:
				item.Hide()

	def Clear(self):
		for item in self.itemList:
			item.Hide()
			del item
		self.itemList = []
		self.basePos = 0

	def AdjustScrollBar(self):
		if self.scrollBar:
			if len(self.itemList) <= 10:
				self.scrollBar.Hide()
			else:
				self.scrollBar.Show()

class ItemRewardHorizontal(ui.ScriptWindow):
	def __init__(self, parent, vnum, count):
		ui.ScriptWindow.__init__(self)
		self.SetParent(parent)

		self.itemVnum = vnum
		self.itemCount = count
		self.tooltipItem = None
		self.wndWiki = None

		self.Board = ui.MakeExpandedImageBox(self, "d:/ymir work/ui/public/Slot_Base.sub", 0, 0)
		self.SetSize(self.Board.GetWidth(), self.Board.GetHeight())

		item.SelectItem(vnum)

		newReward = ui.ExpandedImageBox()
		newReward.SetParent(self.Board)
		newReward.LoadImage(item.GetIconImageFileName())
		newReward.SetPosition(0, 0)
		newReward.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverInItem), vnum)
		newReward.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOutItem))
		newReward.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.OnClickItem), vnum)
		newReward.Show()
		self.newReward = newReward

		newName = MakeTextLineRightAlign(self.Board)
		newName.SetPosition(1, 7)
		newName.SetText(str(count))
		newName.SetOutline()
		newName.SetWindowName("text")

		self.newName = newName

		self.UpdateRect()

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def SetWikiInstance(self, wndWiki):
		self.wndWiki = wndWiki

	def OnOverInItem(self, vnum):
		if self.tooltipItem:
			self.tooltipItem.SetItemToolTip(vnum)
			if app.ENABLE_INGAME_WIKI and self.wndWiki:
				self.tooltipItem.DeclareShortcut(("key_shift", "key_lclick"), getattr(localeinfo, "TOOLTIP_WIKI_HOVER_NORMAL", "Click to open Wiki"))
				self.tooltipItem.ResizeToolTip()

	def OnOverOutItem(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OnClickItem(self, vnum):
		if not app.ENABLE_INGAME_WIKI:
			return

		if not self.wndWiki:
			return

		# Check if item is a box type
		item.SelectItem(vnum)
		isBoxType = item.GetItemType() in (item.ITEM_TYPE_GIFTBOX, item.ITEM_TYPE_GACHA)

		if not self.wndWiki.IsShow():
			net.ToggleWikiWindow()

		self.wndWiki.CloseBaseWindows()

		if isBoxType:
			self.wndWiki.mainChestWindow.Show([vnum,])
		else:
			self.wndWiki.OpenSpecialPage(None, vnum, False)

	def SetParent(self, parent):
		ui.ScriptWindow.SetParent(self, parent)
		self.parent = proxy(parent)

	def OnRender(self):
		xList, yList = self.parent.GetGlobalPosition()
		xList += 1
		
		width, height = self.parent.GetWidth() - 2, self.parent.GetHeight()	 
		for image in [self.Board, self.newReward, self.newName]:
			if image.GetWindowName() == "text":
				xText, yText = image.GetGlobalPosition()
				image.Hide() if yText < yList or yText + image.GetTextSize()[1] > yList + height else image.Show()

				if xText + image.GetTextSize()[0] > xList + width + 10:
					image.Hide()
				elif xText - image.GetTextSize()[0] < xList:
					image.Hide()
			else:
				self.SetClipRect(image, xList, yList, xList + width, yList + height)

	def SetClipRect(self, image, fLeft, fTop, fRight, fBottom):
		if image.GetWidth() == 0 and image.GetHeight() == 0:
			return
	
		(left, top, right, bottom) = image.GetRect()
		right = right + left
		bottom = bottom + top
		
		#calculate
		fDifLeft = -(float(fLeft - left) / float(image.GetWidth())) if (left < fLeft) else 0.0
		fDifTop = -(float(fTop - top) / float(image.GetHeight())) if (top < fTop) else 0.0
		fDifRight = -(float(right - fRight) / float(image.GetWidth())) if (right > fRight) else 0.0
		fDifBottom = -(float(bottom - fBottom) / float(image.GetHeight())) if (bottom > fBottom) else  0.0
		
		image.SetRenderingRect(fDifLeft, fDifTop, fDifRight, fDifBottom)

	def Destroy(self):
		self.ClearDictionary()

class MissionListWindow(ui.ScriptWindow):
	def __init__(self):
		self.bLoaded = False
		self.tooltipItem = None
		self.ListBoxItem1 = None
		self.ListBoxItem2 = None
		self.isFirstOpened = False
		self.leftTimeUntilTomorrow = 0
		self.leftTimeUntilSunday = 0
		self.lastResetTimeUpdate = 0  # Track last update to avoid updating every frame
		self.wndWiki = None  # Wiki instance for opening monster/item pages

		self.spinTime = 0
		self.spinForceTime = 0
		self.selectedSpinReward = [0, 0, 0, 0]  # [itemVnum, itemCount, category, index]
		self.spinRewardItems = []  # Items created for spin animation
		self.listRewardsImageHorizontal = []  # Horizontal reward images for spinner

		# Reroll/Refresh tracking
		self.rerollCountDaily = 0
		self.rerollLimitDaily = 0
		self.rerollCountWeekly = 0
		self.rerollLimitWeekly = 0
		self.refreshCountDaily = 0
		self.refreshLimitDaily = 0
		self.refreshCountWeekly = 0
		self.refreshLimitWeekly = 0

		# Reroll/Refresh item requirements
		self.rerollItemVnum = 0
		self.rerollItemCount = 0
		self.refreshItemVnum = 0
		self.refreshItemCount = 0

		# HWID claim lock (1 = can claim, 0 = locked by another character)
		self.canClaimDaily = 1
		self.canClaimWeekly = 1

		# Confirmation dialog
		self.confirmDialog = None
		self.pendingRerollCategory = 0
		self.pendingRerollIndex = 0
		self.pendingRefreshCategory = 0
		self.pendingSpinCategory = 0
		self.pendingSpinIndex = 0

		self.tooltipItem = uitooltip.ItemToolTip()
		self.tooltipItem.HideToolTip()

		# Monster preview render target for wiki-enabled missions
		self.monsterPreview = None
		self.monsterPreviewBoard = None
		self.monsterPreviewHint = None
		if app.ENABLE_INGAME_WIKI:
			self.monsterPreviewBoard = ui.ThinBoard()
			self.monsterPreviewBoard.SetSize(180, 240)
			self.monsterPreviewBoard.AddFlag("float")
			self.monsterPreviewBoard.Hide()

			self.monsterPreview = ingamewikiui.WikiRenderTarget(160, 180)
			self.monsterPreview.SetParent(self.monsterPreviewBoard)
			self.monsterPreview.SetPosition(10, 10)
			self.monsterPreview.Hide()

			self.monsterPreviewText = ui.TextLine()
			self.monsterPreviewText.SetParent(self.monsterPreviewBoard)
			self.monsterPreviewText.SetPosition(90, 195)
			self.monsterPreviewText.SetHorizontalAlignCenter()
			self.monsterPreviewText.SetOutline()
			self.monsterPreviewText.Hide()

			# Wiki hint text at bottom of preview
			self.monsterPreviewHint = ui.TextLine()
			self.monsterPreviewHint.SetParent(self.monsterPreviewBoard)
			self.monsterPreviewHint.SetPosition(90, 215)
			self.monsterPreviewHint.SetHorizontalAlignCenter()
			self.monsterPreviewHint.SetPackedFontColor(0xFFffeaa7)
			wikiHintText = getattr(localeinfo, "MISSIONLIST_CLICK_FOR_WIKI", "Click to view in Wiki")
			self.monsterPreviewHint.SetText(wikiHintText)
			self.monsterPreviewHint.Hide()

		ui.ScriptWindow.__init__(self)
		self.LoadWindow()
		self.SetCenterPosition()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.ClearDictionary()
		self.dictMissionInfo = {}

		self.spinTime = 0
		self.spinForceTime = 0
		self.selectedSpinReward = [0, 0, 0, 0]
		self.spinRewardItems = []
		self.listRewardsImageHorizontal = []

		if self.ListBoxItem1:
			self.ListBoxItem1.Clear()
		self.ListBoxItem1 = None

		if self.ListBoxItem2:
			self.ListBoxItem2.Clear()
		self.ListBoxItem2 = None

		self.bLoadedInfo = False
		self.tooltipItem = None
		self.isFirstOpened = False

		if self.helpTooltip:
			self.helpTooltip.Hide()
			self.helpTooltip = None
		self.helpTextLines = []
		self.helpTooltipShown = False
		self.btnHelp = None

	def RequestMissionData(self):
		"""
		Silently request mission data from server without showing the window.
		Uses 'sync' command which sends data but doesn't mark window as open.
		Used on game start/teleport to keep tooltip data available.
		"""
		net.SendChatPacket("/q_mission_quest sync")

	def Show(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "MISSION_LIST")
		self.LoadWindow()
		self.SetTop()
		ui.ScriptWindow.Show(self)

		if self.isFirstOpened == False:
			net.SendChatPacket("/q_mission_quest rewards")

		net.SendChatPacket("/q_mission_quest open")

		self.isFirstOpened = True
		
	def LoadWindow(self):
		if self.bLoaded == True:
			return
			
		self.bLoaded = True

		self.AddFlag("movable")
		self.AddFlag("float")
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetParent(self)
		self.Board.SetSize(522, 341)
		self.Board.SetTitleName(localeinfo.MISSIONLIST_TITLE)
		self.Board.SetCloseEvent(ui.__mem_func__(self.CloseFromPlayer))
		self.Board.Show()

		self.SetSize(self.Board.GetWidth(), self.Board.GetHeight())

		self.__CreateHelpButton()
		self.LoadMiddleBoard()
		self.LoadBoardRewardList1()
		self.LoadBoardRewardList2()
		self.LoadBoardMissionList1()
		self.LoadBoardMissionList2()

		self.ListBoxItem1.SetItemToolTip(self.tooltipItem)
		self.ListBoxItem2.SetItemToolTip(self.tooltipItem)

		# Refresh For Rewards
		self.ListBoxItem1.AdjustScrollBar()
		self.ListBoxItem1.AdjustItemPositions()

		self.ListBoxItem2.AdjustScrollBar()
		self.ListBoxItem2.AdjustItemPositions()

	def __CreateHelpButton(self):
		titleBar = self.Board.titleBar
		btnHelp = ui.Button()
		btnHelp.SetParent(titleBar)
		btnHelp.SetUpVisual("d:/ymir work/ui/game/wheel/question_mark.png")
		btnHelp.SetOverVisual("d:/ymir work/ui/game/wheel/question_mark_glow.png")
		btnHelp.SetDownVisual("d:/ymir work/ui/game/wheel/question_mark_down.png")
		if localeinfo.IsARABIC():
			btnHelp.SetPosition(25, 3)
		else:
			btnHelp.SetPosition(titleBar.GetWidth() - 40, 3)
		btnHelp.SetEvent(ui.__mem_func__(self.__ToggleHelpTooltip))
		btnHelp.Show()
		self.btnHelp = btnHelp

		self.helpTooltip = None
		self.helpTooltipShown = False

	def __ToggleHelpTooltip(self):
		if self.helpTooltipShown and self.helpTooltip:
			self.helpTooltip.Hide()
			self.helpTooltipShown = False
			return

		if not self.helpTooltip:
			self.helpTooltip = self.__BuildHelpTooltip()

		self.__PositionHelpTooltip()
		self.helpTooltip.SetTop()
		self.helpTooltip.Show()
		self.helpTooltipShown = True

	def __PositionHelpTooltip(self):
		if not self.helpTooltip:
			return
		(x, y) = self.GetGlobalPosition()
		newX = x + self.GetWidth() + 5
		if newX + self.helpTooltip.GetWidth() > wndMgr.GetScreenWidth():
			newX = x - self.helpTooltip.GetWidth() - 5
		newY = max(0, y)
		self.helpTooltip.SetPosition(newX, newY)

	def __AddHelpLine(self, parent, yPos, text, color, isArabic):
		textLine = ui.TextLine()
		textLine.SetParent(parent)
		textLine.SetPackedFontColor(color)
		textLine.SetText(text)
		textLine.SetOutline()
		textLine.SetFeather(False)
		if isArabic:
			#textLine.SetHorizontalAlignRight()
			textLine.SetPosition(parent.GetWidth() - 12, yPos)
		else:
			textLine.SetPosition(12, yPos)
		textLine.Show()
		return textLine

	def __BuildHelpTooltip(self):
		BOARD_WIDTH = 280
		TITLE = 0xFFFFE3A9
		HEADER = 0xFF6AD4FF
		TEXT = 0xFFD2D2D2
		HIGHLIGHT = 0xFFFFCC00
		WARNING = 0xFFFF6666
		LINE_H = 16
		SECTION_GAP = 8

		isArabic = localeinfo.IsARABIC()

		lines = []
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_TITLE", "Mission System Guide"), TITLE))
		lines.append(None)
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_OVERVIEW_H", "How It Works"), HEADER))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_OVERVIEW_1", "Complete missions to earn rewards."), TEXT))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_OVERVIEW_2", "3 Daily + 3 Weekly missions available."), TEXT))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_OVERVIEW_3", "Progress is automatic as you play."), TEXT))
		lines.append(None)
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_RESET_H", "Reset Schedule"), HEADER))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_RESET_1", "Daily missions reset every day."), TEXT))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_RESET_2", "Weekly missions reset every week."), TEXT))
		lines.append(None)
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_REROLL_H", "Reroll & Refresh"), HEADER))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_REROLL_1", "Reroll: Replace one mission (costs item)."), TEXT))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_REROLL_2", "Refresh: Replace all missions in a"), TEXT))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_REROLL_3", "category (costs item)."), TEXT))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_REROLL_4", "Both have limited uses per cycle."), TEXT))
		lines.append(None)
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_REWARD_H", "Reward Claiming"), HEADER))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_REWARD_1", "Rewards are shared across all characters."), TEXT))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_REWARD_2", "The first character to claim a reward"), HIGHLIGHT))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_REWARD_3", "locks claiming for that category."), HIGHLIGHT))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_REWARD_4", "Other characters cannot claim until reset."), WARNING))
		lines.append(None)
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_TYPES_H", "Mission Types"), HEADER))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_TYPES_1", "Kill Monsters / Bosses / Metin Stones"), TEXT))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_TYPES_2", "Mining / Fishing / Dungeons"), TEXT))
		lines.append((getattr(localeinfo, "MISSIONLIST_HELP_TYPES_3", "Submit Items / Use Items"), TEXT))

		yPos = 10
		board = ui.ThinBoard("TOP_MOST")
		board.AddFlag("float")
		board.SetSize(BOARD_WIDTH, 100)
		self.helpTextLines = []

		for entry in lines:
			if entry is None:
				yPos += SECTION_GAP
			else:
				text, color = entry
				tl = self.__AddHelpLine(board, yPos, text, color, isArabic)
				self.helpTextLines.append(tl)
				yPos += LINE_H

		yPos += 10
		board.SetSize(BOARD_WIDTH, yPos)
		board.Hide()
		return board

	def LoadMiddleBoard(self):
		self.board_Base = ui.MakeExpandedImageBox(self, PATH_ROOT + "base_daily_ae.png" if localeinfo.IsARABIC() else "base_daily.png", 9, 32)

		self.wndDailyTextHeader = ui.MakeTextLineNew(self.board_Base, self.GetWidth() - 30 if localeinfo.IsARABIC() else 12, 16, localeinfo.MISSIONLIST_DAILY_HEADER)
		self.boardDailyTextReset = ui.MakeExpandedImageBox(self.board_Base, PATH_ROOT + "title_resets.png", 95 + 180 if localeinfo.IsARABIC() else 95, 8)
		self.wndDailyTextReset = ui.MakeTextLine(self.boardDailyTextReset)

		self.wndWeeklyTextHeader = ui.MakeTextLineNew(self.board_Base, 245 if localeinfo.IsARABIC() else 252 + 12, 16, localeinfo.MISSIONLIST_WEEKLY_HEADER)
		self.boardWeeklyTextReset = ui.MakeExpandedImageBox(self.board_Base, PATH_ROOT + "title_resets.png", 10 if localeinfo.IsARABIC() else 252 + 95, 8)
		self.wndWeeklyTextReset = ui.MakeTextLine(self.boardWeeklyTextReset)

		self.dictMissionInfo = {}
		self.dictMissionInfo[0] = {}
		self.dictMissionInfo[1] = {}
		
		for x in xrange(3):
			iconDaily = ui.MakeExpandedImageBox(self.board_Base, PATH_ROOT + "quest_inactive.png", self.GetWidth() - 60 if localeinfo.IsARABIC() else 9, 65 + (x*67))
			iconDaily.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverPreviewReward), 0, x)
			iconDaily.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOutPreviewReward))
			iconDaily.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.OnClickMissionIcon), 0, x)

			TextDaily = ui.MakeTextLineNew(self.board_Base, self.GetWidth() - 70 if localeinfo.IsARABIC() else 55, 65 + (x*67), "right" if localeinfo.IsARABIC() else "")
			claimDaily= ui.MakeButton(self.board_Base, self.GetWidth() - 135 if localeinfo.IsARABIC() else 185, 82 + (x*67), "", PATH_ROOT , "btn_claim_1.png", "btn_claim_2.png", "btn_claim_3.png")
			claimDaily.SetEvent(ui.__mem_func__(self.OnSpinReward), 0, x)

			claimDaily.EnableFlash()
			claimDaily.Hide()

			submitDaily= ui.MakeButton(self.board_Base, self.GetWidth() - 135 if localeinfo.IsARABIC() else 55, 83 + (x*67), "", PATH_ROOT , "btn_skip_1.png", "btn_skip_2.png", "btn_skip_1.png")
			submitDaily.SetEvent(ui.__mem_func__(self.OnSubmitItem), 0, x)
			
			submitDaily.Hide()
			
			submitDaily.SetText(localeinfo.MISSIONLIST_BTN_SUBMIT)
			
			# Reroll button for daily missions
			rerollDaily = ui.MakeButton(self.board_Base, self.GetWidth() - 86 if localeinfo.IsARABIC() else 220, 52 + (x*67) if localeinfo.IsARABIC() else 65 + (x*67), localeinfo.MISSIONLIST_REROLL_DAILY_TITLE, PATH_ROOT, "btn_refresh_sm_1.png", "btn_refresh_sm_2.png", "btn_refresh_sm_3.png")
			rerollDaily.SetEvent(ui.__mem_func__(self.OnRerollMission), 0, x)
			#rerollDaily.SetText("R")
			rerollDaily.Hide()

			# Progress bar for daily missions
			gaugeBaseDaily = ui.MakeExpandedImageBox(self.board_Base, PATH_ROOT + "gauge_0.png",270 if localeinfo.IsARABIC() else 55, 90 + (x*67))
			gaugeBaseDaily.Hide()

			gaugeFillDaily = ui.ExpandedImageBox()
			gaugeFillDaily.SetParent(self.board_Base)
			gaugeFillDaily.LoadImage(PATH_ROOT + "gauge_1.png")
			gaugeFillDaily.SetPosition(270 if localeinfo.IsARABIC() else 55, 90 + (x*67))
			gaugeFillDaily.Hide()

			self.dictMissionInfo[0][x] = {}
			self.dictMissionInfo[0][x]["icon"] = iconDaily
			self.dictMissionInfo[0][x]["text"] = TextDaily
			self.dictMissionInfo[0][x]["claim"] = claimDaily
			self.dictMissionInfo[0][x]["submit"] = submitDaily
			self.dictMissionInfo[0][x]["reroll"] = rerollDaily
			self.dictMissionInfo[0][x]["gaugeBase"] = gaugeBaseDaily
			self.dictMissionInfo[0][x]["gaugeFill"] = gaugeFillDaily

			iconWeekly = ui.MakeExpandedImageBox(self.board_Base, PATH_ROOT + "quest_inactive.png", 210 if localeinfo.IsARABIC() else 252 + 9, 65 + (x*67))
			iconWeekly.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverPreviewReward), 1, x)
			iconWeekly.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOutPreviewReward))
			iconWeekly.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.OnClickMissionIcon), 1, x)

			TextWeekly = ui.MakeTextLineNew(self.board_Base, 210 - 10 if localeinfo.IsARABIC() else 250 + 55, 65 + (x*67), "right" if localeinfo.IsARABIC() else "")
			claimWeekly = ui.MakeButton(self.board_Base, 130 if localeinfo.IsARABIC() else 250 + 185, 82 + (x*67), "", PATH_ROOT , "btn_claim_1.png", "btn_claim_2.png", "btn_claim_3.png")
			claimWeekly.SetEvent(ui.__mem_func__(self.OnSpinReward), 1, x)
			
			claimWeekly.EnableFlash()
			claimWeekly.Hide()
			
			submitWeekly= ui.MakeButton(self.board_Base, 130 if localeinfo.IsARABIC() else 250 + 55, 83 + (x*67), "", PATH_ROOT , "btn_skip_1.png", "btn_skip_2.png", "btn_skip_3.png")
			submitWeekly.SetEvent(ui.__mem_func__(self.OnSubmitItem), 1, x)
			
			submitWeekly.Hide()

			submitWeekly.SetText(localeinfo.MISSIONLIST_BTN_SUBMIT)

			# Reroll button for weekly missions
			rerollWeekly = ui.MakeButton(self.board_Base,161 + 25 if localeinfo.IsARABIC() else  250 + 220, 52 + (x*67) if localeinfo.IsARABIC() else 65 + (x*67), localeinfo.MISSIONLIST_REROLL_TITLE, PATH_ROOT, "btn_refresh_sm_1.png", "btn_refresh_sm_2.png", "btn_refresh_sm_3.png")
			rerollWeekly.SetEvent(ui.__mem_func__(self.OnRerollMission), 1, x)
			#rerollWeekly.SetText("R")
			rerollWeekly.Hide()

			# Progress bar for weekly missions
			gaugeBaseWeekly = ui.MakeExpandedImageBox(self.board_Base, PATH_ROOT + "gauge_0.png", 20 if localeinfo.IsARABIC() else  250 + 55, 90 + (x*67))
			gaugeBaseWeekly.Hide()

			gaugeFillWeekly = ui.ExpandedImageBox()
			gaugeFillWeekly.SetParent(self.board_Base)
			gaugeFillWeekly.LoadImage(PATH_ROOT + "gauge_1.png")
			gaugeFillWeekly.SetPosition(20 if localeinfo.IsARABIC() else  250 + 55, 90 + (x*67))
			gaugeFillWeekly.Hide()

			self.dictMissionInfo[1][x] = {}
			self.dictMissionInfo[1][x]["icon"] = iconWeekly
			self.dictMissionInfo[1][x]["text"] = TextWeekly
			self.dictMissionInfo[1][x]["claim"] = claimWeekly
			self.dictMissionInfo[1][x]["submit"] = submitWeekly
			self.dictMissionInfo[1][x]["reroll"] = rerollWeekly
			self.dictMissionInfo[1][x]["gaugeBase"] = gaugeBaseWeekly
			self.dictMissionInfo[1][x]["gaugeFill"] = gaugeFillWeekly

		################
		self.boardSpinReward = ui.MakeExpandedImageBox(self.board_Base, PATH_ROOT + "spinner_bg.png", 118, 250)
		self.imageSpinPointer = ui.MakeExpandedImageBox(self.boardSpinReward, PATH_ROOT + "spinner_pointer.png", 0, 0)
		self.imageSpinPointer.SetWindowHorizontalAlignCenter()
		
		self.btnRewardListDaily = ui.MakeButton(self.board_Base, 395 if localeinfo.IsARABIC() else 14, 258, "", PATH_ROOT , "btn_view_rewards_1.png", "btn_view_rewards_2.png", "btn_view_rewards_3.png")
		self.btnRewardListDaily.SetText(localeinfo.MISSIONLIST_BTN_REWARD_LIST)
		self.btnRewardListDaily.SetEvent(ui.__mem_func__(self.ClickRewardList), 0)

		self.btnRewardListWeekly = ui.MakeButton(self.board_Base, 14 if localeinfo.IsARABIC() else 395, 258, "", PATH_ROOT , "btn_view_rewards_1.png", "btn_view_rewards_2.png", "btn_view_rewards_3.png")
		self.btnRewardListWeekly.SetText(localeinfo.MISSIONLIST_BTN_REWARD_LIST)
		self.btnRewardListWeekly.SetEvent(ui.__mem_func__(self.ClickRewardList), 1)

		# View Missions buttons (to preview possible missions)
		btnMissionText = getattr(localeinfo, "MISSIONLIST_BTN_MISSION_DAILY", "View Missions")
		self.btnMissionListDaily = ui.MakeButton(self.board_Base, self.GetWidth() - 40 if localeinfo.IsARABIC() else 12, 16 - 10, "", INFO_ROOT , "mob_info_01.png", "mob_info_02.png", "mob_info_03.png")
		self.btnMissionListDaily.SetToolTipText(btnMissionText)
		self.btnMissionListDaily.SetEvent(ui.__mem_func__(self.ClickMissionList), 0)
		
		btnMissionText2 = getattr(localeinfo, "MISSIONLIST_BTN_MISSION_WEEKLY", "View Missions")
		self.btnMissionListWeekly = ui.MakeButton(self.board_Base, 231 if localeinfo.IsARABIC() else 252 + 12, 16 - 10, "", INFO_ROOT , "mob_info_01.png", "mob_info_02.png", "mob_info_03.png")
		self.btnMissionListWeekly.SetToolTipText(btnMissionText2)
		self.btnMissionListWeekly.SetEvent(ui.__mem_func__(self.ClickMissionList), 1)

		# Refresh buttons for daily and weekly
		self.btnRefreshDaily = ui.MakeButton(self.board_Base, 402 if localeinfo.IsARABIC() else 170, 16, localeinfo.MISSIONLIST_REFRESH_DAILY, PATH_ROOT, "btn_refresh_sm_1.png", "btn_refresh_sm_2.png", "btn_refresh_sm_3.png")
		#self.btnRefreshDaily.SetText("Refresh")
		self.btnRefreshDaily.SetEvent(ui.__mem_func__(self.OnRefreshCategory), 0)
		self.btnRefreshDaily.Hide()

		self.btnRefreshWeekly = ui.MakeButton(self.board_Base, 137 if localeinfo.IsARABIC() else 250 + 170, 16, localeinfo.MISSIONLIST_REFRESH_WEEKLY, PATH_ROOT, "btn_refresh_sm_1.png", "btn_refresh_sm_2.png", "btn_refresh_sm_3.png")
		#self.btnRefreshWeekly.SetText("Refresh")
		self.btnRefreshWeekly.SetEvent(ui.__mem_func__(self.OnRefreshCategory), 1)
		self.btnRefreshWeekly.Hide()

		# History button (bottom center)
		historyBtnText = getattr(localeinfo, "MISSIONLIST_BTN_HISTORY", "History")
		self.btnHistory = ui.MakeButton(self.board_Base, 13, 7, historyBtnText, PATH_ROOT, "btn_history_1.png", "btn_history_2.png", "btn_history_1.png")
		#self.btnHistory.SetText(historyBtnText)
		self.btnHistory.SetEvent(ui.__mem_func__(self.ToggleHistoryPage))
		self.btnHistory.Show()

		# Initialize history page reference
		self.historyPage = None
		self.historyList = []


	def OnOverPreviewReward(self, category, index):
		if "info" not in self.dictMissionInfo[category][index]:
			return

		typeTarget, vnumTarget, progress, maxProgress, isCollected, minLevel, maxLevel, rewardVnum, rewardCount = self.dictMissionInfo[category][index]["info"]

		# Show monster/stone/boss preview for wiki-enabled missions
		if app.ENABLE_INGAME_WIKI and typeTarget in [TYPE_MONSTERS, TYPE_STONES, TYPE_BOSSES] and vnumTarget != 0:
			if self.monsterPreviewBoard and self.monsterPreview:
				# Get icon position for preview placement
				icon = self.dictMissionInfo[category][index]["icon"]
				iconX, iconY = icon.GetGlobalPosition()

				# Position preview next to the icon
				self.monsterPreviewBoard.SetPosition(iconX + 40, iconY - 30)

				# Set the monster model
				self.monsterPreview.SetModel(vnumTarget)

				# Set monster name
				monsterName = nonplayer.GetMonsterName(vnumTarget)
				self.monsterPreviewText.SetText(monsterName)

				# Show everything and bring to top
				self.monsterPreviewBoard.Show()
				self.monsterPreviewBoard.SetTop()
				self.monsterPreview.Show()
				self.monsterPreviewText.Show()
				if self.monsterPreviewHint:
					self.monsterPreviewHint.Show()
		elif self.tooltipItem:
			self.tooltipItem.ClearToolTip()
			if isCollected:
				self.tooltipItem.SetTitle(localeinfo.MISSIONLIST_TOOLTIP_REWARD)
				self.tooltipItem.AppendIcon(rewardVnum, rewardCount)
				self.tooltipItem.ShowToolTip()
			elif maxProgress != 0 and progress != maxProgress:
				self.tooltipItem.SetTitle(localeinfo.MISSIONLIST_TOOLTIP_ACTIVE)
				self.tooltipItem.ShowToolTip()

	def OnOverOutPreviewReward(self):
		# Hide monster preview
		if app.ENABLE_INGAME_WIKI and self.monsterPreviewBoard:
			self.monsterPreviewBoard.Hide()
			if self.monsterPreview:
				self.monsterPreview.Hide()
			if self.monsterPreviewText:
				self.monsterPreviewText.Hide()
			if self.monsterPreviewHint:
				self.monsterPreviewHint.Hide()

		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def LoadBoardRewardList1(self):
		self.board_Rewards1 = ui.BoxedBoard()
		self.board_Rewards1.SetParent(self.board_Base)
		self.board_Rewards1.SetPosition(252 if localeinfo.IsARABIC() else 0, 50)
		self.board_Rewards1.SetSize(250, 196)
		
		self.board_Rewards1.SetBaseColor(grp.GenerateColor(0, 0, 0, 1.0))
		self.board_Rewards1.Hide()	

		self.ScrollBarItem1 = ui.ScrollBarNew()
		self.ScrollBarItem1.SetParent(self.board_Rewards1)
		self.ScrollBarItem1.SetScrollBarSize(self.board_Rewards1.GetHeight())
		self.ScrollBarItem1.SetPosition(241, 0)
		self.ScrollBarItem1.Show()

		self.ListBoxItem1 = ListBox()
		self.ListBoxItem1.SetParent(self.board_Rewards1)
		self.ListBoxItem1.SetScrollBar(self.ScrollBarItem1)
		self.ListBoxItem1.SetSize(241 - self.ScrollBarItem1.GetWidth() - 2, self.board_Rewards1.GetHeight() - 4)
		self.ListBoxItem1.SetPosition(2, 2)
		self.ListBoxItem1.Show()

	def LoadBoardRewardList2(self):
		self.board_Rewards2 = ui.BoxedBoard()
		self.board_Rewards2.SetParent(self.board_Base)
		self.board_Rewards2.SetPosition(0 if localeinfo.IsARABIC() else 252, 50)
		self.board_Rewards2.SetSize(250, 196)
		
		self.board_Rewards2.SetBaseColor(grp.GenerateColor(0, 0, 0, 1.0))
		self.board_Rewards2.Hide()	

		self.ScrollBarItem2 = ui.ScrollBarNew()
		self.ScrollBarItem2.SetParent(self.board_Rewards2)
		self.ScrollBarItem2.SetScrollBarSize(self.board_Rewards2.GetHeight())
		self.ScrollBarItem2.SetPosition(241, 0)
		self.ScrollBarItem2.Show()

		self.ListBoxItem2 = ListBox()
		self.ListBoxItem2.SetParent(self.board_Rewards2)
		self.ListBoxItem2.SetScrollBar(self.ScrollBarItem2)
		self.ListBoxItem2.SetSize(241 - self.ScrollBarItem2.GetWidth() - 2, self.board_Rewards2.GetHeight() - 4)
		self.ListBoxItem2.SetPosition(2, 2)
		self.ListBoxItem2.Show()

	def LoadBoardMissionList1(self):
		"""Load mission pool preview board for Daily missions"""
		self.board_Missions1 = ui.BoxedBoard()
		self.board_Missions1.SetParent(self.board_Base)
		self.board_Missions1.SetPosition(252 if localeinfo.IsARABIC() else 0, 50)
		self.board_Missions1.SetSize(250, 196)
		self.board_Missions1.SetBaseColor(grp.GenerateColor(0, 0, 0, 1.0))
		self.board_Missions1.Hide()

		self.ScrollBarMission1 = ui.ScrollBarNew()
		self.ScrollBarMission1.SetParent(self.board_Missions1)
		self.ScrollBarMission1.SetScrollBarSize(self.board_Missions1.GetHeight())
		self.ScrollBarMission1.SetPosition(241, 0)
		self.ScrollBarMission1.Show()

		self.ListBoxMission1 = MissionListBox()
		self.ListBoxMission1.SetParent(self.board_Missions1)
		self.ListBoxMission1.SetScrollBar(self.ScrollBarMission1)
		self.ListBoxMission1.SetSize(241 - self.ScrollBarMission1.GetWidth() - 2, self.board_Missions1.GetHeight() - 4)
		self.ListBoxMission1.SetPosition(230 if localeinfo.IsARABIC() else 2, 2)
		self.ListBoxMission1.Show()

	def LoadBoardMissionList2(self):
		"""Load mission pool preview board for Weekly missions"""
		self.board_Missions2 = ui.BoxedBoard()
		self.board_Missions2.SetParent(self.board_Base)
		self.board_Missions2.SetPosition(0 if localeinfo.IsARABIC() else 252, 50)
		self.board_Missions2.SetSize(250, 196)
		self.board_Missions2.SetBaseColor(grp.GenerateColor(0, 0, 0, 1.0))
		self.board_Missions2.Hide()

		self.ScrollBarMission2 = ui.ScrollBarNew()
		self.ScrollBarMission2.SetParent(self.board_Missions2)
		self.ScrollBarMission2.SetScrollBarSize(self.board_Missions2.GetHeight())
		self.ScrollBarMission2.SetPosition(241, 0)
		self.ScrollBarMission2.Show()

		self.ListBoxMission2 = MissionListBox()
		self.ListBoxMission2.SetParent(self.board_Missions2)
		self.ListBoxMission2.SetScrollBar(self.ScrollBarMission2)
		self.ListBoxMission2.SetSize(241 - self.ScrollBarMission2.GetWidth() - 2, self.board_Missions2.GetHeight() - 4)
		self.ListBoxMission2.SetPosition( 230 if localeinfo.IsARABIC() else 2, 2)
		self.ListBoxMission2.Show()

	def SetMissionQuestUpdate(self, category, index, missionCount, missionState):
		if "info" not in self.dictMissionInfo[category][index]:
			return
			
		typeTarget, vnumTarget, progress, maxProgress, isCollected, minLevel, maxLevel, rewardVnum, rewardCount = self.dictMissionInfo[category][index]["info"]
		self.SetMissionInfo(category, index, typeTarget, vnumTarget, missionCount, maxProgress, missionState, minLevel, maxLevel, rewardVnum, rewardCount)

	def SetMissionQuestGeneral(self, leftTimeUntilTomorrow, leftTimeUntilSunday):
		self.leftTimeUntilTomorrow = leftTimeUntilTomorrow + app.GetGlobalTimeStamp()
		self.leftTimeUntilSunday   = leftTimeUntilSunday + app.GetGlobalTimeStamp()
	
	def SetMissionQuestReward(self, category, index, itemVnum, itemCount, minLevel, maxLevel):
		if category == 0:
			if self.ListBoxItem1.HasItemReward(itemVnum, itemCount, minLevel, maxLevel):
				return
		
			self.ListBoxItem1.AppendItemReward(category, index, itemVnum, itemCount, minLevel, maxLevel)
		elif category == 1:
			if self.ListBoxItem2.HasItemReward(itemVnum, itemCount, minLevel, maxLevel):
				return

			self.ListBoxItem2.AppendItemReward(category, index, itemVnum, itemCount, minLevel, maxLevel)
	
		### Append Reward on Horizontal-board
		countRewards = len(self.listRewardsImageHorizontal)

		newItem = ItemRewardHorizontal(self.boardSpinReward, itemVnum, itemCount)
		newItem.SetItemToolTip(self.tooltipItem)
		newItem.SetWikiInstance(self.wndWiki)
		newItem.SetPosition((countRewards * 32), 6)
		newItem.Show()

		self.listRewardsImageHorizontal.append(newItem)

		self.imageSpinPointer = ui.MakeExpandedImageBox(self.boardSpinReward, PATH_ROOT + "spinner_pointer.png", 0, 0)
		self.imageSpinPointer.SetWindowHorizontalAlignCenter()

	def SetMissionInfo(self, category, index, typeTarget, vnumTarget, progress, maxProgress, isCollected, minLevel, maxLevel, rewardVnum, rewardCount):
		myLevel = player.GetStatus(player.LEVEL)

		# Ensure dictMissionInfo structure exists (for tooltip system when window not loaded)
		if category not in self.dictMissionInfo:
			self.dictMissionInfo[category] = {}
		if index not in self.dictMissionInfo[category]:
			self.dictMissionInfo[category][index] = {}

		# Always store mission info (needed for tooltip system even when window not loaded)
		self.dictMissionInfo[category][index]["info"] = [typeTarget, vnumTarget, progress, maxProgress, isCollected, minLevel, maxLevel, rewardVnum, rewardCount]

		# Skip UI updates if window not loaded yet
		if not self.bLoaded:
			return

		# Manage Submit Button
		self.dictMissionInfo[category][index]["submit"].Hide()
		if typeTarget == 7 and not isCollected and progress < maxProgress:
			self.dictMissionInfo[category][index]["submit"].Show()

		# Manage Claim Button
		self.dictMissionInfo[category][index]["claim"].Hide()
		canClaim = self.canClaimDaily if category == 0 else self.canClaimWeekly
		if progress == maxProgress and not isCollected and canClaim:
			self.dictMissionInfo[category][index]["claim"].Show()

		# Manage Reroll Button - show only if mission is incomplete and not claimed
		self.dictMissionInfo[category][index]["reroll"].Hide()
		if typeTarget != 0 and not isCollected and progress < maxProgress:
			# Check if reroll is allowed (have remaining rerolls)
			if category == 0 and self.rerollCountDaily < self.rerollLimitDaily:
				self.dictMissionInfo[category][index]["reroll"].Show()
			elif category == 1 and self.rerollCountWeekly < self.rerollLimitWeekly:
				self.dictMissionInfo[category][index]["reroll"].Show()
		
		# Icon State
		if typeTarget == 0:
			self.dictMissionInfo[category][index]["icon"].LoadImage(PATH_ROOT + "quest_inactive.png")
		elif myLevel < minLevel or myLevel > maxLevel:
			self.dictMissionInfo[category][index]["icon"].LoadImage(PATH_ROOT + "quest_daily_inactive.png")
		elif isCollected:
			if category == 0:  # Daily
				self.dictMissionInfo[category][index]["icon"].LoadImage("icon/item/scroll_close_2.tga")
			else:  # Weekly
				self.dictMissionInfo[category][index]["icon"].LoadImage("icon/item/scroll_close_blue.tga")
		elif progress == maxProgress:
			if category == 0:  # Daily
				self.dictMissionInfo[category][index]["icon"].LoadImage("icon/item/scroll_open_2.tga")
			else:  # Weekly
				self.dictMissionInfo[category][index]["icon"].LoadImage("icon/item/scroll_open_blue.tga")
		else:
			if category == 0:  # Daily
				self.dictMissionInfo[category][index]["icon"].LoadImage("icon/item/scroll_open_2.tga")
			else:  # Weekly
				self.dictMissionInfo[category][index]["icon"].LoadImage("icon/item/scroll_open_blue.tga")

		# Text State
		text = ""
		if myLevel < minLevel or myLevel > maxLevel:
			text = localeinfo.MISSIONLIST_REQUIRED_LEVEL % (minLevel, maxLevel)
		elif progress == maxProgress and isCollected == 0:
			text = localeinfo.MISSIONLIST_CLICK_CLAIM
		elif progress == maxProgress and isCollected == 1:
			text = localeinfo.MISSIONLIST_ACCOMPLISHED
		elif typeTarget == 0:
			text = localeinfo.MISSIONLIST_UNAVAILABLE
		else:
			text = GetNameByTypeVnum(typeTarget, vnumTarget, maxProgress - progress)

		self.dictMissionInfo[category][index]["text"].SetText(text)

		# Progress Bar State
		gaugeBase = self.dictMissionInfo[category][index]["gaugeBase"]
		gaugeFill = self.dictMissionInfo[category][index]["gaugeFill"]

		# Hide progress bar for inactive, out-of-level-range, or already collected missions
		if typeTarget == 0 or typeTarget == 7 or (myLevel < minLevel or myLevel > maxLevel) or (progress == maxProgress):
			gaugeBase.Hide()
			gaugeFill.Hide()
		else:
			# Show progress bar for active missions
			gaugeBase.Show()
			gaugeFill.Show()

			# Calculate progress percentage and scale the fill gauge
			if maxProgress > 0:
				percentage = float(progress) / float(maxProgress)
			else:
				percentage = 0.0

			# Scale the fill gauge horizontally based on progress
			gaugeFill.SetScale(percentage, 1.0)

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "MISSION_LIST")
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()
		if self.helpTooltip:
			self.helpTooltip.Hide()
			self.helpTooltipShown = False

		self.Hide()

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("MISSION_LIST", x, y)
		if self.helpTooltip and self.helpTooltipShown:
			self.__PositionHelpTooltip()

	def CloseFromPlayer(self):
		if self.IsShow() and self.isFirstOpened:
			net.SendChatPacket("/q_mission_quest close")
		self.Close()

	def SetWikiInstance(self, wndWiki):
		"""Set the wiki window instance for opening monster/item pages"""
		self.wndWiki = proxy(wndWiki)

	def OnClickMissionIcon(self, category, index):
		"""Open wiki page when clicking on a mission icon with a specific target"""
		if "info" not in self.dictMissionInfo[category][index]:
			return

		info = self.dictMissionInfo[category][index]["info"]
		missionType = info[0]  # typeTarget
		vnum = info[1]         # vnumTarget

		# Only open wiki for valid types with specific targets
		if vnum == 0:
			return  # "Any" target, no specific wiki page

		if missionType not in [TYPE_MONSTERS, TYPE_STONES, TYPE_BOSSES, TYPE_USE_ITEM]:
			return

		if not self.wndWiki:
			return

		# Ensure wiki is visible
		if not self.wndWiki.IsShow():
			net.ToggleWikiWindow()

		self.wndWiki.CloseBaseWindows()

		# Determine if monster or item page
		isMonster = missionType in [TYPE_MONSTERS, TYPE_STONES, TYPE_BOSSES]
		self.wndWiki.OpenSpecialPage(None, vnum, isMonster)

	def OnPressEscapeKey(self):
		self.CloseFromPlayer()
		return True

	def OnMouseWheel(self, nLen):
	
		if self.board_Rewards2.IsInPosition():
			if nLen > 0:
				self.ScrollBarItem2.OnUp()
			else:
				self.ScrollBarItem2.OnDown()		
		else:
			if nLen > 0:
				self.ScrollBarItem1.OnUp()
			else:
				self.ScrollBarItem1.OnDown()
	
	def OnRender(self):
		self.UpdateResetTime()
		self.OnRenderSpinReward()
	
	def UpdateResetTime(self):
		current_timestamp = app.GetGlobalTimeStamp()

		# Only update text once per second to save performance
		if current_timestamp == self.lastResetTimeUpdate:
			return

		self.lastResetTimeUpdate = current_timestamp

		if self.leftTimeUntilTomorrow:
			time_left = self.leftTimeUntilTomorrow - current_timestamp
			if time_left > 0:
				self.wndDailyTextReset.SetText(localeinfo.MISSIONLIST_AVAILABLE_AGAIN % (localeinfo.SecondToDHMNew(time_left)))
			else:
				resetText = getattr(localeinfo, "MISSIONLIST_RESET_AVAILABLE", "Missions available!")
				self.wndDailyTextReset.SetText(resetText)

		if self.leftTimeUntilSunday:
			time_left = self.leftTimeUntilSunday - current_timestamp
			if time_left > 0:
				self.wndWeeklyTextReset.SetText(localeinfo.MISSIONLIST_AVAILABLE_AGAIN % (localeinfo.SecondToDHMNew(time_left)))
			else:
				resetText = getattr(localeinfo, "MISSIONLIST_RESET_AVAILABLE", "Missions available!")
				self.wndWeeklyTextReset.SetText(resetText)
	
	def OnSpinReward(self, category, index):
		if "info" not in self.dictMissionInfo[category][index]:
			return

		# Check if there's already a spin in progress
		if self.spinTime != 0:
			return

		typeTarget, vnumTarget, progress, maxProgress, isCollected, minLevel, maxLevel, rewardVnum, rewardCount = self.dictMissionInfo[category][index]["info"]

		# Show warning if this is the first claim (will lock rewards to this character)
		canClaim = self.canClaimDaily if category == 0 else self.canClaimWeekly
		isFirstClaim = canClaim and not self.isClaimLocked(category)
		if isFirstClaim:
			self.pendingSpinCategory = category
			self.pendingSpinIndex = index

			if self.confirmDialog:
				self.confirmDialog.Hide()
				self.confirmDialog.Destroy()

			self.confirmDialog = uicommon.QuestionDialog2()
			self.confirmDialog.SetText1(getattr(localeinfo, "MISSIONLIST_CLAIM_LOCK_WARNING1", "Claiming will lock rewards to this character."))
			self.confirmDialog.SetText2(getattr(localeinfo, "MISSIONLIST_CLAIM_LOCK_WARNING2", "Other characters won't be able to claim until reset."))
			self.confirmDialog.SetAcceptEvent(ui.__mem_func__(self.__OnConfirmClaim))
			self.confirmDialog.SetCancelEvent(ui.__mem_func__(self.__OnCancelClaim))
			self.confirmDialog.Open()
			return

		# Request spin from server - server will respond with MQ_SPIN_REWARD
		net.SendChatPacket("/q_mission_quest spin %d %d" % (category, index))

	def isClaimLocked(self, category):
		if category == 0:
			return self.canClaimDaily == 2
		return self.canClaimWeekly == 2

	def __OnConfirmClaim(self):
		if self.confirmDialog:
			self.confirmDialog.Hide()
			self.confirmDialog.Destroy()
			self.confirmDialog = None
		net.SendChatPacket("/q_mission_quest spin %d %d" % (self.pendingSpinCategory, self.pendingSpinIndex))

	def __OnCancelClaim(self):
		if self.confirmDialog:
			self.confirmDialog.Hide()
			self.confirmDialog.Destroy()
			self.confirmDialog = None

	def SetMissionSpinReward(self, selectedItemIdx, selectedItemCount, cmdData):
		"""Called when server sends MQ_SPIN_REWARD command - starts the spin animation"""
		# Store the selected reward (what the wheel will land on)
		self.selectedSpinReward = [int(selectedItemIdx), int(selectedItemCount), 0, 0]

		# Clear existing spin items
		for item in self.spinRewardItems:
			item.Hide()
		self.spinRewardItems = []

		# Parse cmdData and create reward items for the spinner
		# Format: rareType|itemVnum|itemCount?rareType|itemVnum|itemCount?...
		if cmdData and cmdData != "-":
			rewards = cmdData.split("?")
			xPos = 0

			# Create multiple copies of rewards to fill the spinner
			for repeat in xrange(5):  # Repeat items to make continuous scroll effect
				for rewardStr in rewards:
					parts = rewardStr.split("|")
					if len(parts) == 3:
						rareType = int(parts[0])
						itemVnum = int(parts[1])
						itemCount = int(parts[2])

						newItem = ItemRewardHorizontal(self.boardSpinReward, itemVnum, itemCount)
						newItem.SetItemToolTip(self.tooltipItem)
						newItem.SetWikiInstance(self.wndWiki)
						newItem.SetPosition(xPos, 6)
						newItem.Show()
						self.spinRewardItems.append(newItem)
						xPos += 32

		# Start the spin animation
		self.spinForceTime = app.GetTime() + 10  # Force complete after 10 seconds
		self.spinTime = app.GetTime() + float(app.GetRandom(2, 4))  # Spin for 2-4 seconds

	def OnRenderSpinReward(self):
		if len(self.spinRewardItems) == 0:
			return

		if self.spinTime == 0:
			return

		spinLeftTime = self.spinTime - app.GetTime()
		spinCurrentX = (spinLeftTime * 2) * 2 if spinLeftTime > 0 else 3
		spinItemList = self.spinRewardItems

		# Force complete after timeout
		if app.GetTime() >= self.spinForceTime:
			self.spinTime = 0
			self.OnSpinComplete()
			return

		# Move items left
		for child in spinItemList:
			xPos = child.GetLocalPosition()[0] - math.ceil(spinCurrentX)
			child.SetPosition(xPos, 6)

			# Check if selected item is at center position (animation complete)
			if spinLeftTime < 0:
				if child.itemVnum == self.selectedSpinReward[0] and child.itemCount == self.selectedSpinReward[1]:
					if xPos >= 90 and xPos <= 110:
						self.spinTime = 0
						self.OnSpinComplete()
						return

		# Wrap items around (infinite scroll effect)
		for child in spinItemList:
			if child.GetLocalPosition()[0] < -40:
				xPosHighest = 0
				for childEx in spinItemList:
					if xPosHighest < childEx.GetLocalPosition()[0] + 32:
						xPosHighest = childEx.GetLocalPosition()[0] + 32
				child.SetPosition(xPosHighest, 6)

	def OnSpinComplete(self):
		"""Called when spin animation finishes - tell server to give reward"""
		net.SendChatPacket("/q_mission_quest ani_done")

		# Clean up spin items after a short delay (keep visible briefly)
		# The MQ_UPDATE from server will refresh the UI

	def OnClaimReward(self, category, index):
		net.SendChatPacket("/q_mission_quest collect %d %d" % (category, index))

	def OnSubmitItem(self, category, index):
		net.SendChatPacket("/q_mission_quest submit %d %d" % (category, index))

	def OnRerollMission(self, category, index):
		"""Show confirmation dialog for rerolling a single mission"""
		if self.rerollItemVnum == 0:
			return

		self.pendingRerollCategory = category
		self.pendingRerollIndex = index

		if self.confirmDialog:
			self.confirmDialog.Hide()
			self.confirmDialog.Destroy()

		self.confirmDialog = uicommon.ItemQuestDialog()
		self.confirmDialog.SetTitleName(localeinfo.MISSIONLIST_REROLL_TITLE)
		questionText = getattr(localeinfo, "MISSIONLIST_REROLL_QUESTION", "Do you want to reroll this mission?")
		self.confirmDialog.Open([(self.rerollItemVnum, self.rerollItemCount)], questionText)
		self.confirmDialog.SelectEvent(self.__OnConfirmReroll)

	def __OnConfirmReroll(self, *args):
		"""Callback when reroll is confirmed"""
		if self.confirmDialog:
			self.confirmDialog.Hide()
			self.confirmDialog.Destroy()
			self.confirmDialog = None
		net.SendChatPacket("/q_mission_quest reroll %d %d" % (self.pendingRerollCategory, self.pendingRerollIndex))

	def OnRefreshCategory(self, category):
		"""Show confirmation dialog for refreshing all missions in a category"""
		if self.refreshItemVnum == 0:
			return

		self.pendingRefreshCategory = category

		if self.confirmDialog:
			self.confirmDialog.Hide()
			self.confirmDialog.Destroy()

		self.confirmDialog = uicommon.ItemQuestDialog()
		self.confirmDialog.SetTitleName(localeinfo.MISSIONLIST_REFRESH_TITLE)
		questionText = getattr(localeinfo, "MISSIONLIST_REFRESH_QUESTION", "Do you want to refresh all missions?")
		self.confirmDialog.Open([(self.refreshItemVnum, self.refreshItemCount)], questionText)
		self.confirmDialog.SelectEvent(self.__OnConfirmRefresh)

	def __OnConfirmRefresh(self, *args):
		"""Callback when refresh is confirmed"""
		if self.confirmDialog:
			self.confirmDialog.Hide()
			self.confirmDialog.Destroy()
			self.confirmDialog = None
		net.SendChatPacket("/q_mission_quest refresh %d" % self.pendingRefreshCategory)

	def SetRerollRefreshInfo(self, dailyRerollUsed, dailyRerollMax, weeklyRerollUsed, weeklyRerollMax,
							  dailyRefreshUsed, dailyRefreshMax, weeklyRefreshUsed, weeklyRefreshMax,
							  rerollItemVnum, rerollItemCount, refreshItemVnum, refreshItemCount):
		"""Called by server to update reroll/refresh counts and limits"""
		self.rerollCountDaily = int(dailyRerollUsed)
		self.rerollLimitDaily = int(dailyRerollMax)
		self.rerollCountWeekly = int(weeklyRerollUsed)
		self.rerollLimitWeekly = int(weeklyRerollMax)
		self.refreshCountDaily = int(dailyRefreshUsed)
		self.refreshLimitDaily = int(dailyRefreshMax)
		self.refreshCountWeekly = int(weeklyRefreshUsed)
		self.refreshLimitWeekly = int(weeklyRefreshMax)

		# Store item requirements
		self.rerollItemVnum = int(rerollItemVnum)
		self.rerollItemCount = int(rerollItemCount)
		self.refreshItemVnum = int(refreshItemVnum)
		self.refreshItemCount = int(refreshItemCount)

		# Update refresh button visibility
		if self.refreshCountDaily < self.refreshLimitDaily:
			self.btnRefreshDaily.Show()
		else:
			self.btnRefreshDaily.Hide()

		if self.refreshCountWeekly < self.refreshLimitWeekly:
			self.btnRefreshWeekly.Show()
		else:
			self.btnRefreshWeekly.Hide()

		# Update reroll buttons visibility for all missions
		for category in [0, 1]:
			for index in xrange(3):
				if "info" in self.dictMissionInfo[category][index]:
					info = self.dictMissionInfo[category][index]["info"]
					typeTarget, vnumTarget, progress, maxProgress, isCollected = info[0], info[1], info[2], info[3], info[4]
					# Update reroll button visibility
					self.dictMissionInfo[category][index]["reroll"].Hide()
					if typeTarget != 0 and not isCollected and progress < maxProgress:
						if category == 0 and self.rerollCountDaily < self.rerollLimitDaily:
							self.dictMissionInfo[category][index]["reroll"].Show()
						elif category == 1 and self.rerollCountWeekly < self.rerollLimitWeekly:
							self.dictMissionInfo[category][index]["reroll"].Show()

	def SetClaimLock(self, canClaimDaily, canClaimWeekly):
		self.canClaimDaily = canClaimDaily
		self.canClaimWeekly = canClaimWeekly

		# Re-evaluate claim button visibility for all missions
		for category in [0, 1]:
			canClaim = self.canClaimDaily if category == 0 else self.canClaimWeekly
			for index in xrange(3):
				if "info" in self.dictMissionInfo[category][index]:
					info = self.dictMissionInfo[category][index]["info"]
					progress, maxProgress, isCollected = info[2], info[3], info[4]
					self.dictMissionInfo[category][index]["claim"].Hide()
					if progress == maxProgress and not isCollected and canClaim:
						self.dictMissionInfo[category][index]["claim"].Show()

	def ClickRewardList(self, category):
		info_board = [self.board_Rewards1, self.board_Rewards2]
		board = info_board[category]

		if board.IsShow():
			board.Hide()
		else:
			board.Show()

	def ClickMissionList(self, category):
		"""Toggle mission pool preview board visibility and populate with level-filtered missions"""
		info_board = [self.board_Missions1, self.board_Missions2]
		info_listbox = [self.ListBoxMission1, self.ListBoxMission2]
		board = info_board[category]
		listbox = info_listbox[category]

		if board.IsShow():
			board.Hide()
		else:
			# Populate mission list filtered by player level
			self.PopulateMissionList(category, listbox)
			board.Show()

	def PopulateMissionList(self, category, listbox):
		"""Populate mission list from config file, filtered by player level"""
		listbox.Clear()

		myLevel = player.GetStatus(player.LEVEL)

		# Get all missions for this category from the config
		missionPool = missionpoolconfig.GetMissionPoolByCategory(category)

		for slot, missions in missionPool.items():
			for mission in missions:
				missionType, targetVnum, count, minLevel, maxLevel = mission
				# Filter by player level
				if minLevel <= myLevel <= maxLevel:
					listbox.AppendMission(missionType, targetVnum, count, minLevel, maxLevel)

		listbox.AdjustScrollBar()
		listbox.RefreshItemPositions()

	# ============================================
	# History Page Functions
	# ============================================

	def AddHistoryEntry(self, timestamp, category, missionType, targetVnum, completedCount, rewardVnum, rewardCount):
		"""Called by game.py when receiving MQ_HISTORY packet from server"""
		if not hasattr(self, 'historyList'):
			self.historyList = []

		entry = {
			"timestamp": timestamp,
			"category": category,
			"missionType": missionType,
			"targetVnum": targetVnum,
			"completedCount": completedCount,
			"rewardVnum": rewardVnum,
			"rewardCount": rewardCount
		}
		self.historyList.append(entry)

		# Update history page if it's visible
		if hasattr(self, 'historyPage') and self.historyPage and self.historyPage.IsShow():
			self.historyPage.AddHistoryItem(entry)

	def SetHistoryPageInfo(self, currentPage, hasMore):
		"""Called by game.py when receiving MQ_HISTORY_PAGE packet"""
		if hasattr(self, 'historyPage') and self.historyPage:
			self.historyPage.SetPageInfo(currentPage, hasMore)

	def ToggleHistoryPage(self):
		"""Toggle history page visibility"""
		if not hasattr(self, 'historyPage') or not self.historyPage:
			self._CreateHistoryPage()

		if self.historyPage.IsShow():
			self.historyPage.Hide()
			self.board_Base.Show()
		else:
			# Hide main mission view
			self.board_Base.Hide()
			self.board_Rewards1.Hide()
			self.board_Rewards2.Hide()
			self.board_Missions1.Hide()
			self.board_Missions2.Hide()

			# Clear and request fresh history (page 0)
			self.historyList = []
			self.historyPage.Clear()
			self.historyPage.Show()
			net.SendChatPacket("/q_mission_quest history 0")

	def _CreateHistoryPage(self):
		"""Create the history page UI components"""
		self.historyPage = MissionHistoryPage()
		self.historyPage.SetParent(self.Board)
		self.historyPage.SetPosition(10, 35)
		self.historyPage.SetItemToolTip(self.tooltipItem)
		self.historyPage.SetWikiInstance(self.wndWiki)
		self.historyPage.SetBackEvent(ui.__mem_func__(self.OnHistoryBack))
		self.historyPage.Hide()

	def OnHistoryBack(self):
		"""Called when back button is clicked on history page"""
		if hasattr(self, 'historyPage') and self.historyPage:
			self.historyPage.Hide()
		self.board_Base.Show()


class MissionHistoryPage(ui.Window):
	"""Page displaying completed mission history with pagination"""
	ITEM_HEIGHT = 45
	VISIBLE_ITEMS = 5  # Reduced to make room for pagination controls

	def __init__(self):
		ui.Window.__init__(self)
		self.SetSize(500, 270)

		self.historyItems = []
		self.scrollBar = None
		self.tooltipItem = None
		self.wndWiki = None
		self.basePos = 0
		self.backEvent = None

		# Pagination state
		self.currentPage = 0
		self.hasMorePages = False

		self._CreateUI()

	def _CreateUI(self):
		# Background board
		self.bgBoard = ui.ImageBox()
		self.bgBoard.SetParent(self)
		self.bgBoard.LoadImage(PATH_ROOT + "base_history.png" if localeinfo.IsARABIC() else PATH_ROOT + "base_history.png")
		self.bgBoard.SetPosition(0, 0)
		self.bgBoard.Show()

		# Title
		self.titleText = ui.TextLine()
		self.titleText.SetParent(self)
		self.titleText.SetPosition(250, 8)
		self.titleText.SetHorizontalAlignCenter()
		historyTitle = getattr(localeinfo, "MISSIONLIST_HISTORY_TITLE", "Mission History")
		self.titleText.SetText(historyTitle)
		self.titleText.SetOutline()
		self.titleText.Show()

		# Back button
		backBtnX = 420 if localeinfo.IsARABIC() else 10
		self.btnBack = ui.MakeButton(self, backBtnX, 5, "", PATH_ROOT, "btn_skip_1.png", "btn_skip_2.png", "btn_skip_1.png")
		backText = getattr(localeinfo, "MISSIONLIST_HISTORY_BACK", "Back")
		self.btnBack.SetText(backText)
		self.btnBack.SetEvent(ui.__mem_func__(self.OnClickBack))
		self.btnBack.Show()

		# History list container
		listX = 15 if localeinfo.IsARABIC() else 10
		self.listContainer = ui.Window()
		self.listContainer.SetParent(self)
		self.listContainer.SetPosition(listX, 35)
		self.listContainer.SetSize(470, self.ITEM_HEIGHT * self.VISIBLE_ITEMS)
		self.listContainer.Show()

		# Scrollbar
		scrollX = 5 if localeinfo.IsARABIC() else 485
		self.scrollBar = ui.ScrollBarNew()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(scrollX, 35)
		self.scrollBar.SetScrollBarSize(self.ITEM_HEIGHT * self.VISIBLE_ITEMS)
		self.scrollBar.SetScrollEvent(ui.__mem_func__(self.OnScroll))
		self.scrollBar.Hide()

		# Empty message
		self.emptyText = ui.TextLine()
		self.emptyText.SetParent(self.listContainer)
		self.emptyText.SetPosition(235, 100)
		self.emptyText.SetHorizontalAlignCenter()
		emptyMsg = getattr(localeinfo, "MISSIONLIST_HISTORY_EMPTY", "No completed missions yet.")
		self.emptyText.SetText(emptyMsg)
		self.emptyText.SetPackedFontColor(0xFF888888)
		self.emptyText.Show()

		# Pagination controls at bottom
		paginationY = 35 + self.ITEM_HEIGHT * self.VISIBLE_ITEMS + 5

		# Previous page button (on left for LTR, on right for RTL)
		prevText = getattr(localeinfo, "MISSIONLIST_HISTORY_PREV", "<< Prev")
		prevBtnX = 330 if localeinfo.IsARABIC() else 100
		self.btnPrevPage = ui.MakeButton(self, prevBtnX, paginationY, "", PATH_ROOT, "btn_skip_1.png", "btn_skip_2.png", "btn_skip_1.png")
		self.btnPrevPage.SetText(prevText)
		self.btnPrevPage.SetEvent(ui.__mem_func__(self.OnClickPrevPage))
		self.btnPrevPage.Hide()

		# Page indicator text
		self.textPageInfo = ui.TextLine()
		self.textPageInfo.SetParent(self)
		self.textPageInfo.SetPosition(250, paginationY + 5)
		self.textPageInfo.SetHorizontalAlignCenter()
		self.textPageInfo.SetOutline()
		self.textPageInfo.Hide()

		# Next page button (on right for LTR, on left for RTL)
		nextText = getattr(localeinfo, "MISSIONLIST_HISTORY_NEXT", "Next >>")
		nextBtnX = 100 if localeinfo.IsARABIC() else 330
		self.btnNextPage = ui.MakeButton(self, nextBtnX, paginationY, "", PATH_ROOT, "btn_skip_1.png", "btn_skip_2.png", "btn_skip_1.png")
		self.btnNextPage.SetText(nextText)
		self.btnNextPage.SetEvent(ui.__mem_func__(self.OnClickNextPage))
		self.btnNextPage.Hide()

	def SetItemToolTip(self, tooltip):
		self.tooltipItem = tooltip

	def SetWikiInstance(self, wndWiki):
		self.wndWiki = wndWiki

	def SetBackEvent(self, event):
		self.backEvent = event

	def OnClickBack(self):
		if self.backEvent:
			self.backEvent()

	def Clear(self):
		for histItem in self.historyItems:
			histItem.Hide()
			histItem.Destroy()
		self.historyItems = []
		self.basePos = 0
		if self.emptyText:
			self.emptyText.Show()

	def AddHistoryItem(self, entry):
		if self.emptyText:
			self.emptyText.Hide()

		histItem = MissionHistoryItem()
		histItem.SetParent(self.listContainer)
		histItem.SetData(entry)
		histItem.SetItemToolTip(self.tooltipItem)
		histItem.SetWikiInstance(self.wndWiki)
		self.historyItems.append(histItem)
		self.RefreshPositions()
		self.UpdateScrollBar()

	def RefreshPositions(self):
		yPos = 0
		for i, histItem in enumerate(self.historyItems):
			if i < self.basePos:
				histItem.Hide()
			elif i < self.basePos + self.VISIBLE_ITEMS:
				histItem.SetPosition(0, yPos)
				histItem.Show()
				yPos += self.ITEM_HEIGHT
			else:
				histItem.Hide()

	def UpdateScrollBar(self):
		if len(self.historyItems) <= self.VISIBLE_ITEMS:
			self.scrollBar.Hide()
		else:
			self.scrollBar.Show()

	def OnScroll(self):
		if not self.scrollBar:
			return
		pos = self.scrollBar.GetPos()
		maxScroll = max(0, len(self.historyItems) - self.VISIBLE_ITEMS)
		self.basePos = int(pos * maxScroll)
		self.RefreshPositions()

	def OnMouseWheel(self, nLen):
		if nLen > 0:
			self.scrollBar.OnUp()
		else:
			self.scrollBar.OnDown()

	def SetPageInfo(self, currentPage, hasMore):
		"""Called when server sends page info"""
		self.currentPage = currentPage
		self.hasMorePages = bool(hasMore)
		self._UpdatePaginationControls()

	def _UpdatePaginationControls(self):
		"""Update visibility of pagination buttons based on current state"""
		# Show prev button if not on first page
		if self.currentPage > 0:
			self.btnPrevPage.Show()
		else:
			self.btnPrevPage.Hide()

		# Show next button if there are more pages
		if self.hasMorePages:
			self.btnNextPage.Show()
		else:
			self.btnNextPage.Hide()

		# Update page indicator
		if self.currentPage > 0 or self.hasMorePages:
			pageText = getattr(localeinfo, "MISSIONLIST_HISTORY_PAGE", "Page %d")
			self.textPageInfo.SetText(pageText % (self.currentPage + 1))
			self.textPageInfo.Show()
		else:
			self.textPageInfo.Hide()

	def OnClickPrevPage(self):
		"""Load previous page of history"""
		if self.currentPage > 0:
			self.Clear()
			net.SendChatPacket("/q_mission_quest history %d" % (self.currentPage - 1))

	def OnClickNextPage(self):
		"""Load next page of history"""
		if self.hasMorePages:
			self.Clear()
			net.SendChatPacket("/q_mission_quest history %d" % (self.currentPage + 1))


class MissionHistoryItem(ui.Window):
	"""Individual history entry display"""
	def __init__(self):
		ui.Window.__init__(self)
		self.SetSize(460, 43)
		self.tooltipItem = None
		self.wndWiki = None
		self.rewardVnum = 0

		isArabic = localeinfo.IsARABIC()

		# Background bar
		self.bgImage = ui.ExpandedImageBox()
		self.bgImage.SetParent(self)
		self.bgImage.LoadImage(PATH_ROOT + "quest_inactive.png")
		self.bgImage.SetPosition(429 if isArabic else 0, 6)
		self.bgImage.Show()

		if isArabic:
			# Arabic RTL layout (reading right to left on screen)
			# Visual layout: [Reward Icon][Count] ... [Mission Text] ... [Date]
			#                                                           [Category]
			# Positions: icon at X=5, count at X=40, mission at X=200, date/category at X=380-455

			# Reward icon - far left (start of row in RTL reading)
			self.rewardIcon = ui.ExpandedImageBox()
			self.rewardIcon.SetParent(self)
			self.rewardIcon.SetPosition(5, 10)
			self.rewardIcon.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverInReward))
			self.rewardIcon.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOutReward))
			self.rewardIcon.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.OnClickReward))
			self.rewardIcon.Show()

			# Reward count - next to icon
			self.textRewardCount = ui.TextLine()
			self.textRewardCount.SetParent(self)
			self.textRewardCount.SetPosition(40, 8)
			self.textRewardCount.SetOutline()
			self.textRewardCount.Show()

			# Mission description text - center area, right-aligned text
			self.textMission = ui.TextLine()
			self.textMission.SetParent(self)
			self.textMission.SetPosition(280, 14)
			self.textMission.SetHorizontalAlignLeft()
			self.textMission.SetOutline()
			self.textMission.Show()

			# Date text - far right, top row
			self.textDate = ui.TextLine()
			self.textDate.SetParent(self)
			self.textDate.SetPosition(420, 6)
			self.textDate.SetHorizontalAlignLeft()
			self.textDate.SetPackedFontColor(0xFFAAAAAA)
			self.textDate.SetOutline()
			self.textDate.Show()

			# Category badge - far right, bottom row (below date)
			self.textCategory = ui.TextLine()
			self.textCategory.SetParent(self)
			self.textCategory.SetPosition(420, 25)
			self.textCategory.SetHorizontalAlignLeft()
			self.textCategory.SetOutline()
			self.textCategory.Show()
		else:
			# Standard LTR layout (left to right reading)
			# Layout: [Date + Category] | [Mission Text] | [Reward Icon + Count]

			# Date text - far left
			self.textDate = ui.TextLine()
			self.textDate.SetParent(self)
			self.textDate.SetPosition(5, 5)
			self.textDate.SetPackedFontColor(0xFFAAAAAA)
			self.textDate.SetOutline()
			self.textDate.Show()

			# Category badge - far left, below date
			self.textCategory = ui.TextLine()
			self.textCategory.SetParent(self)
			self.textCategory.SetPosition(5, 22)
			self.textCategory.SetOutline()
			self.textCategory.Show()

			# Mission description text - center area
			self.textMission = ui.TextLine()
			self.textMission.SetParent(self)
			self.textMission.SetPosition(100, 14)
			self.textMission.SetOutline()
			self.textMission.Show()

			# Reward icon - far right
			self.rewardIcon = ui.ExpandedImageBox()
			self.rewardIcon.SetParent(self)
			self.rewardIcon.SetPosition(400, 8)
			self.rewardIcon.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverInReward))
			self.rewardIcon.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOutReward))
			self.rewardIcon.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.OnClickReward))
			self.rewardIcon.Show()

			# Reward count - next to icon on right
			self.textRewardCount = ui.TextLine()
			self.textRewardCount.SetParent(self)
			self.textRewardCount.SetPosition(435, 14)
			self.textRewardCount.SetOutline()
			self.textRewardCount.Show()

	def SetItemToolTip(self, tooltip):
		self.tooltipItem = tooltip

	def SetWikiInstance(self, wndWiki):
		self.wndWiki = wndWiki

	def SetData(self, entry):
		# Format date
		try:
			dateStr = time.strftime("%m/%d %H:%M", time.localtime(entry["timestamp"]))
		except:
			dateStr = "Unknown"
		self.textDate.SetText(dateStr)

		# Category with color
		if entry["category"] == 0:
			dailyText = getattr(localeinfo, "MISSIONLIST_DAILY_SHORT", "Daily")
			self.textCategory.SetText(dailyText)
			self.textCategory.SetPackedFontColor(0xFF66CC66)  # Green
		else:
			weeklyText = getattr(localeinfo, "MISSIONLIST_WEEKLY_SHORT", "Weekly")
			self.textCategory.SetText(weeklyText)
			self.textCategory.SetPackedFontColor(0xFF6699FF)  # Blue

		# Mission description
		missionText = GetNameByTypeVnum(
			entry["missionType"],
			entry["targetVnum"],
			entry["completedCount"]
		)
		# Truncate if too long
		if len(missionText) > 40:
			missionText = missionText[:37] + "..."
		self.textMission.SetText(missionText)

		# Reward icon
		self.rewardVnum = entry["rewardVnum"]
		item.SelectItem(entry["rewardVnum"])
		self.rewardIcon.LoadImage(item.GetIconImageFileName())

		# Reward count
		self.textRewardCount.SetText("x%d" % entry["rewardCount"])

	def OnOverInReward(self):
		if self.tooltipItem and self.rewardVnum:
			self.tooltipItem.SetItemToolTip(self.rewardVnum)

	def OnOverOutReward(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OnClickReward(self):
		"""Open wiki page for reward item"""
		if not app.ENABLE_INGAME_WIKI:
			return

		if not self.wndWiki or not self.rewardVnum:
			return

		# Check if item is a box type
		item.SelectItem(self.rewardVnum)
		isBoxType = item.GetItemType() in (item.ITEM_TYPE_GIFTBOX, item.ITEM_TYPE_GACHA)

		if not self.wndWiki.IsShow():
			net.ToggleWikiWindow()

		self.wndWiki.CloseBaseWindows()

		if isBoxType:
			self.wndWiki.mainChestWindow.Show([self.rewardVnum,])
		else:
			self.wndWiki.OpenSpecialPage(None, self.rewardVnum, False)

	def Destroy(self):
		self.tooltipItem = None
		self.wndWiki = None
