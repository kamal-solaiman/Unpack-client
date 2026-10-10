import ui
import app
import grp
import net
import chat
import item
from _weakref import proxy
import nonplayer
import wndMgr
import localeinfo, uiScriptLocale
import player
import mousemodule
from datetime import datetime, timedelta
import ingamewikiui
import constinfo
import systemSetting
import uicommon
import uitooltip

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

PATH_ROOT = "d:/ymir work/ui/game/battle_pass_reworked/"
PATH_ICONS = "d:/ymir work/ui/game/battle_pass_reworked/slice/quest/icons/"
PATH_SLICE = "d:/ymir work/ui/game/battle_pass_reworked/slice/"

OPEN_SHOP_ID = 12

# EXP Boost item (replaces old skip mission token 71083)
ITEM_VNUM_BP_EXP_BOOST = 93113

TITLE_TYPES = {
	1 : localeinfo.BATTLE_PASS_OPEN_ITEM,
	2 : localeinfo.BATTLE_PASS_KILL_MONSTER,
	3 : localeinfo.BATTLE_PASS_KILL_STONE,
	4 : localeinfo.BATTLE_PASS_KILL_BOSS,
	5 : localeinfo.BATTLE_PASS_MINING,
	6 : localeinfo.BATTLE_PASS_FISHING,
	7 : localeinfo.BATTLE_PASS_USE_FISH,
	8 : localeinfo.BATTLE_PASS_DESTROY_ITEM,
	9 : localeinfo.BATTLE_PASS_REFINE_ITEM,
	10 : localeinfo.BATTLE_PASS_SHOUT,
	11 : localeinfo.BATTLE_PASS_COMB_ACCE,
	12 : localeinfo.BATTLE_PASS_REWARD_YANG,
	13 : localeinfo.BATTLE_PASS_BUY_FROM_NPC,
	14 : localeinfo.BATTLE_PASS_SPEND_MONEY,
	15 : localeinfo.BATTLE_PASS_COLLECT,
	16 : localeinfo.BATTLE_PASS_EXP_COLLECT,
	17 : localeinfo.BATTLE_PASS_GAYA_CRAFT_GAYA,
	18 : localeinfo.BATTLE_PASS_COMPLETE_DUNGEON,
	19 : localeinfo.BATTLE_PASS_ENCHANT_USE,
	20 : localeinfo.BATTLE_PASS_DONATE,
}

# Mission description dictionary - detailed tooltips per mission type
def GetMissionDescription(missionType):
	"""Get detailed description for a mission type with safe locale fallback."""
	MISSION_DESC_MAP = {
		1 : "BP_MISSION_DESC_OPEN_ITEM",
		2 : "BP_MISSION_DESC_KILL_MONSTER",
		3 : "BP_MISSION_DESC_KILL_STONE",
		4 : "BP_MISSION_DESC_KILL_BOSS",
		5 : "BP_MISSION_DESC_MINING",
		6 : "BP_MISSION_DESC_FISHING",
		7 : "BP_MISSION_DESC_USE_FISH",
		8 : "BP_MISSION_DESC_DESTROY_ITEM",
		9 : "BP_MISSION_DESC_REFINE_ITEM",
		10 : "BP_MISSION_DESC_SHOUT",
		11 : "BP_MISSION_DESC_COMB_ACCE",
		12 : "BP_MISSION_DESC_REWARD_YANG",
		13 : "BP_MISSION_DESC_BUY_FROM_NPC",
		14 : "BP_MISSION_DESC_SPEND_MONEY",
		15 : "BP_MISSION_DESC_COLLECT",
		16 : "BP_MISSION_DESC_EXP_COLLECT",
		17 : "BP_MISSION_DESC_GAYA_CRAFT",
		18 : "BP_MISSION_DESC_COMPLETE_DUNGEON",
		19 : "BP_MISSION_DESC_ENCHANT_USE",
		20 : "BP_MISSION_DESC_DONATE",
	}

	attrName = MISSION_DESC_MAP.get(missionType, None)
	if attrName:
		try:
			return getattr(localeinfo, attrName, "Complete this mission to earn Battle Pass rewards.")
		except:
			pass
	return "Complete this mission to earn Battle Pass rewards."

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

def GetNameByTypeVnum(type, vnum):
	"""
	Get display name for mission target based on type and vnum.

	Type mapping (from server EBattlePassMissionType):
	1 = OPEN_ITEM (items)
	2 = KILL_MONSTER (monsters)
	3 = KILL_STONE (metin stones - monsters)
	4 = KILL_BOSS (bosses - monsters)
	5-8 = Mining/Fishing related
	9 = REFINE_ITEM (items)
	10 = SHOUT (no target)
	11 = COMB_ACCE (accessory - items)
	etc.
	"""
	# FIX: Safe locale access with fallbacks
	def safe_locale(attr, default):
		try:
			return getattr(localeinfo, attr, default)
		except:
			return default

	if vnum == 0:
		return safe_locale("BP_ALL", "All")

	# Monster types: KILL_MONSTER (2), KILL_STONE (3), KILL_BOSS (4)
	if type in (2, 3, 4):
		monster_name = safe_locale("BP_MONSTERS", "Monsters")
		if vnum:
			try:
				monster_name = nonplayer.GetMonsterName(vnum)
				if not monster_name:
					monster_name = "Monster #%d" % vnum
			except:
				monster_name = "Monster #%d" % vnum
		return monster_name

	# Item types: OPEN_ITEM (1), REFINE_ITEM (9), COMB_ACCE (11), DESTROY_ITEM (8)
	elif type in (1, 8, 9, 11):
		item_name = safe_locale("BP_ITEMS", "Items")
		if vnum:
			try:
				item.SelectItem(vnum)
				item_name = item.GetItemName()
				if not item_name:
					item_name = "Item #%d" % vnum
			except:
				item_name = "Item #%d" % vnum
		return item_name

	return safe_locale("BP_ALL", "All")

class ListBox(ui.Window):
	class NewItem(ui.Window):
		def __init__(self, category, index, title, type, vnum, count, maxCount, expRecieve, func, IsPremium, coolTime, parent):
			ui.Window.__init__(self)
			self.category = category
			self.isPremium = IsPremium
			self.index = index
			self.select = False
			self.expRecieve = expRecieve
			self.QuestionDialog = None
			self.coolTime = coolTime
			self.isSkipInProgress = False  # FIX: Prevent double-click on skip
			self.tooltipMission = None  # Mission description tooltip

			# FIX: Safe lookup with fallback for missing locale strings
			title = TITLE_TYPES.get(type, "Unknown Mission")
			self.title = title
			self.type = type
			self.vnum = vnum
			self.count = count
			self.maxCount = maxCount
	
			self.Reinitialize()

			if func:
				self.OnSelectitemIndex = ui.__mem_func__(func)

			self.bg = ui.ExpandedImageBox()
			self.bg.SetParent(self)
			self.bg.AddFlag("not_pick")
			self.bg.SetPosition(0, 0)
			self.bg.image = PATH_ROOT + "slice/quest/" + "quest.png"
			self.bg.LoadImage(self.bg.image)
			self.bg.Show()
			
			self.SetSize(self.bg.GetWidth(), self.bg.GetHeight())		

			self.wndIcon = ui.ExpandedImageBox()
			self.wndIcon.SetParent(self)
			self.wndIcon.SetPosition(393, 4)
			self.wndIcon.LoadImage(PATH_ICONS + "%d.png" % (type))
			self.wndIcon.Show()

			# Create and bind mission tooltip to icon
			self.__CreateMissionTooltip()
			self.wndIcon.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnMissionIconOverIn))
			self.wndIcon.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnMissionIconOverOut))

			self.wndTextLine = ui.TextLine()
			self.wndTextLine.SetParent(self.bg)
			self.wndTextLine.SetPosition(self.GetWidth() - 80, 4)
			# FIX: Use format string properly to avoid string concatenation issues with % operator
			self.wndTextLine.SetText("%s (%d)" % (title, self.maxCount - self.count))
			self.wndTextLine.SetPackedFontColor(0xFFC6B38D)
			self.wndTextLine.SetOutline()
			self.wndTextLine.Show()

			self.wndTextLine2 = ui.TextLine()
			self.wndTextLine2.SetParent(self.bg)
			self.wndTextLine2.SetPosition(self.GetWidth() - 215, 4)
			# FIX: Safe string formatting with fallback for missing locale
			try:
				targetName = GetNameByTypeVnum(type, vnum)
				targetText = localeinfo.BP_TARGET % (targetName,)
			except (AttributeError, TypeError):
				targetText = "Target: %s" % (GetNameByTypeVnum(type, vnum),)
			self.wndTextLine2.SetText(targetText)
			self.wndTextLine2.SetOutline()
			self.wndTextLine2.Show()

			self.wndTextLine3 = ui.TextLine()
			self.wndTextLine3.SetParent(self.bg)
			self.wndTextLine3.SetPosition(90, 5)
			#self.wndTextLine3.SetText("%s %d" % (expRecieve))
			self.wndTextLine3.SetText("{} {} ".format(expRecieve,localeinfo.EXP_NAME))
			self.wndTextLine3.SetPackedFontColor(0xFF9F8C76)
			self.wndTextLine3.Show()

			self.wndTextLine4 = ui.TextLine()
			self.wndTextLine4.SetParent(self.bg)
			self.wndTextLine4.SetPosition(90, 5 + 17)
			if self.isPremium:
				self.wndTextLine4.SetText(localeinfo.BP_MISSIONTYPE_PREMIUM)
				self.wndTextLine4.SetPackedFontColor(0xFFf39c12)
			else:
				self.wndTextLine4.SetText(localeinfo.BP_MISSIONTYPE_NORMAL)
				self.wndTextLine4.SetPackedFontColor(0xFF95a5a6)
			
			self.wndTextLine4.Show()

			self.bgGauge = ui.Window()
			self.bgGauge.SetParent(self)
			self.bgGauge.SetPosition(216, 27)
			
			if self.isPremium:
				self.bgGaugeFull = ui.MakeExpandedImageBox(self.bgGauge, PATH_ROOT+"slice/quest/" + "quest_innerbar_premium.png", 0, 2, "not_pick")
			else:
				self.bgGaugeFull = ui.MakeExpandedImageBox(self.bgGauge, PATH_ROOT+"slice/quest/" + "quest_innerbar.png", 0, 2, "not_pick")

			self.bgGauge.SetSize(self.bgGaugeFull.GetWidth(), self.bgGaugeFull.GetHeight())
			self.bgGauge.Show()
			


			self.wndTextLine5 = ui.TextLine()
			self.wndTextLine5.SetParent(self.bg)
			self.wndTextLine5.SetPosition(380, 14)
			self.wndTextLine5.SetText("")
			self.wndTextLine5.SetPackedFontColor(0xFF9F8C76)
			self.wndTextLine5.Show()

			self.UpdateGauge(count, maxCount, self.coolTime)


		def GetInfoItem(self):
			return (self.title, self.type, self.vnum, self.count, self.maxCount)
		
		def SetItemToolTip(self, tooltipItem):
			self.tooltipItem = tooltipItem

		def __CreateMissionTooltip(self):
			"""Create a rich tooltip with detailed mission description."""
			self.tooltipMission = uitooltip.RichItemToolTip(350)  # Wide tooltip for clear explanations

			# Get mission title and description
			missionTitle = TITLE_TYPES.get(self.type, "Unknown Mission")
			missionDesc = GetMissionDescription(self.type)

			# Get target name if applicable
			targetName = GetNameByTypeVnum(self.type, self.vnum)

			# Build descriptions list
			descriptions = []

			# Add main description - split by multiple delimiters for language support
			# English uses ". " (period + space), Arabic uses "، " (Arabic comma + space) or "٫ "
			import re
			# Split by: period+space, Arabic comma+space, or Chinese period
			descParts = re.split(r'\. |، |。', missionDesc)
			for part in descParts:
				part = part.strip()
				if part:
					descriptions.append((part, self.tooltipMission.DESC_COLOR))

			# Add empty line for spacing
			descriptions.append("")

			# Add progress info with locale fallback
			progressText = "%d / %d" % (self.count, self.maxCount)
			try:
				progressLabel = localeinfo.BP_MISSION_PROGRESS
			except:
				progressLabel = "Progress:"
			descriptions.append((progressLabel + " " + progressText, self.tooltipMission.HIGHLIGHT_COLOR))

			# Add target info if applicable (vnum > 0 means specific target)
			if self.vnum > 0:
				# try:
					# targetLabel = localeinfo.BP_MISSION_TARGET
				# except:
					# targetLabel = "Target:"
				descriptions.append((targetName, self.tooltipMission.TITLE_COLOR))

			# Add reward info
			try:
				rewardLabel = localeinfo.BP_MISSION_REWARD
			except:
				rewardLabel = "Reward:"
			descriptions.append((rewardLabel + " %d %s" % (self.expRecieve, localeinfo.EXP_NAME), self.tooltipMission.HIGHLIGHT_COLOR))

			# Footer based on premium status
			try:
				if self.isPremium:
					footer = localeinfo.BP_MISSION_PREMIUM
				else:
					footer = localeinfo.BP_MISSION_STANDARD
			except:
				footer = "Premium Mission" if self.isPremium else "Standard Mission"

			# Set up tooltip using mission icon image path
			iconPath = PATH_ICONS + "%d.png" % self.type
			self.tooltipMission.AddIconWithDescription(
				iconPath,
				missionTitle,
				descriptions,
				footer
			)
			self.tooltipMission.HideToolTip()

		def OnMissionIconOverIn(self):
			"""Show tooltip when hovering over mission icon."""
			if self.tooltipMission:
				self.tooltipMission.ShowToolTip()

		def OnMissionIconOverOut(self):
			"""Hide tooltip when mouse leaves mission icon."""
			if self.tooltipMission:
				self.tooltipMission.HideToolTip()

		def AppendReward(self, vnum, count):
			if vnum == 0:
				return

			item.SelectItem(vnum)

			length = len(self.dictRewards)

			newReward = ui.ExpandedImageBoxWiki()
			newReward.SetParent(self)
			newReward.LoadImage(item.GetIconImageFileName())
			# FIX: Use integer division operator for Python 2/3 compatibility
			newReward.SetPosition(360 + (32 * (length // 2)), 6)
			newReward.Show()
			
			newReward.SetStringEvent("MOUSE_OVER_IN",ui.__mem_func__(self.OverInReward), vnum)
			newReward.SetStringEvent("MOUSE_OVER_OUT",ui.__mem_func__(self.OverOutReward))
			
			newCount = MakeTextLineRightAlign(newReward)
			newCount.SetPosition(1, 7)
			newCount.SetText(str(count))
			newCount.SetOutline()
			newCount.SetWindowName("text")
			
			self.dictRewards.append(newReward)
			self.dictRewards.append(newCount)
		
		def OnRender(self):
			xList, yList = self.parent.GetGlobalPosition()
			width, height = self.parent.GetWidth(), self.parent.GetHeight()

			listImage = [self.bg, self.wndIcon]
			for image in listImage:
				if image:
					self.SetClipRect(image, xList, yList, xList + width, yList + height)

			# FIX: Prevent division by zero in gauge clip calculation
			if self.percentTotal > 0:
				gaugeProgress = float(self.percentActual) / float(self.percentTotal)
			else:
				gaugeProgress = 0.0
			self.bgGaugeFull.SetClipRect(0.0, yList, -1.0 + gaugeProgress, yList + self.parent.GetHeight(), True)
			
			listText = [self.wndTextLine, self.wndTextLine2, self.wndTextLine3, self.wndTextLine4, self.wndTextLine5]
			for text in listText:
				if text:
					xText, yText = text.GetGlobalPosition()
					text.Hide() if yText < yList or yText + text.GetTextSize()[1] > yList + height else text.Show()
			
			if len(self.dictRewards):
				for image in self.dictRewards:
					if image.GetWindowName() == "text":
						xText, yText = image.GetGlobalPosition()
						image.Hide() if yText < yList or yText + image.GetTextSize()[1] > yList + height else image.Show()
					else:
						self.SetClipRect(image, xList, yList, xList + width, yList + height)

			# if self.coolTime > 0 and self.coolTime > app.GetGlobalTimeStamp():
				# if self.category > 0: # hide time for monthly
					# self.wndTextLine5.SetText("")
					# self.coolTime = 0
				# else:
					# leftSec = self.coolTime - app.GetGlobalTimeStamp()
					# self.wndTextLine5.SetText(localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(leftSec))
			# elif self.coolTime > 0:
				# self.wndTextLine5.SetText("")
				# self.coolTime = 0
		
		def UpdateCoolTimeText(self):
			if self.count == self.maxCount:
				self.wndTextLine5.SetText("Complete")
				return
		
			current_time = datetime.utcnow()
			if self.coolTime != current_time.day:
				self.wndTextLine5.SetText("")
		
		def UpdateGauge(self, actual, total, coolTime):
			# FIX: Robust handling of edge cases
			if total <= 0:
				total = self.maxCount if self.maxCount > 0 else 1
			if actual < 0:
				actual = 0
			if actual > total:
				actual = total

			self.coolTime = coolTime


			self.count = actual
			self.percentActual = actual
			self.percentTotal = total

			# FIX: Calculate remaining count correctly (can't be negative)
			# FIX: Use proper format string to avoid issues with title containing % characters
			remaining = max(0, self.maxCount - self.count)
			self.wndTextLine.SetText("%s (%d)" % (self.title, remaining))

			if self.percentActual >= self.percentTotal:
				self.bgGaugeFull.LoadImage(PATH_ROOT+"slice/quest/" + "quest_innerbar_premium.png")
			else:
				if self.isPremium:
					self.bgGaugeFull.LoadImage(PATH_ROOT+"slice/quest/" + "quest_innerbar_premium.png")
				else:
					self.bgGaugeFull.LoadImage(PATH_ROOT+"slice/quest/" + "quest_innerbar.png")

			self.UpdateCoolTimeText()
	
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

		def SelectImage(self):
			# self.bg.LoadImage(PATH_ROOT + "slice/quest/"+ "quest_gold.png")
			# self.OnSelectitemIndex([self.index])
			self.select = True

		def OverInImage(self):
			if self.select:
				return
		
			# self.bg.LoadImage(PATH_ROOT + "slice/quest/"+ "quest_gold.png")

		def OverOutImage(self):
			pass
			# if self.select == False:
				# self.bg.LoadImage(PATH_ROOT + "slice/quest/"+ "quest_gold.png")
	
		def SetSelect(self):
			self.select = True
			# self.bg.LoadImage(PATH_ROOT + "slice/quest/"+ "quest_gold.png")
	
		def OverOutForce(self):
			self.select = False
			# self.bg.LoadImage(PATH_ROOT + "slice/quest/"+ "quest_gold.png")
		
		def __del__(self):
			ui.Window.__del__(self)
			self.Reinitialize()
			
		def Reinitialize(self):
			self.xBase = 0
			self.yBase = 0

			self.bg = None
			self.dictRewards = []
			self.tooltipItem = None
			self.tooltipMission = None
			self.QuestionDialog = None
			self.isSkipInProgress = False

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
				
		def OnMouseLeftButtonDown(self):	
			self.SelectImage()

	def __init__(self):
		ui.Window.__init__(self)
		self.currentCategory = 0
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
		
		self.SetPosition(5, 5)
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
			
	def GetTotalItemHeight(self):
		totalHeight = 0
		
		if self.itemList:
			for itemH in self.itemList:
				if itemH.IsShow() == FALSE:
					continue
				totalHeight += itemH.GetHeight() + 2
			
		return totalHeight

	def GetItemCount(self):
		return len(self.itemList)
			
	def SelectItemIndex(self, index):
		for x in xrange(len(self.itemList)):
			itemCurrent = self.itemList[x]
			itemCurrent.OverOutForce()
			
			if itemCurrent.index == index:	
				itemCurrent.SetSelect()
	
	def GetInfoItem(self, index):
		mission = self.GetMission(index)
		return mission.GetInfoItem()
	
	def GetFinishedMissions(self):
		count_finished = 0
		count_need_done = 0

		if self.itemList:
			for itemH in self.itemList:
				if itemH.percentActual >= itemH.percentTotal:
					count_finished += 1
				
				count_need_done += 1

		return (count_finished, count_need_done)
	
	def UpdateMissionCount(self, index, count, coolTime):
		mission = self.GetMission(index)

		if mission:
			# FIX: Pass mission's maxCount instead of 0 to prevent division by zero
			mission.UpdateGauge(count, mission.maxCount, coolTime)
	
	def GetMission(self, index):
		if self.itemList:
			for itemH in self.itemList:
				if itemH.index == index:
					return itemH

		return None
	
	def AppendItemReward(self, index, vnum, count):
		mission = self.GetMission(index)
		
		if mission:
			mission.AppendReward(vnum, count)
	
	def AppendItem(self, category, index, title, type, vnum, count, maxCount, expRecieve, func, isPremium, coolTime):
		item = self.NewItem(category, index, title, type, vnum, count, maxCount, expRecieve, func, isPremium, coolTime, self)
		item.SetParent(self)
		item.SetItemToolTip(self.tooltipItem)
		
		if len(self.itemList) == 0:
			item.SetBasePosition(0, 0)
		else:
			x, y = self.itemList[-1].GetLocalPosition()
			y += 2
			item.SetBasePosition(0, y + self.itemList[-1].GetHeight())
			
		if item.category == self.currentCategory:
			item.Show()

		self.itemList.append(item)
		
		self.AdjustScrollBar()
		self.AdjustItemPositions()

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
	
	def RefreshList(self, category):
		self.currentCategory = category
	
		for item in self.itemList:
			if item.category != self.currentCategory:
				item.Hide()
			else:
				item.Show()
	
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

		# FIX: Proper cleanup - don't use del on loop variable
		for item in self.itemList:
			item.Reinitialize()
			item.Hide()

		# Clear the list - Python GC handles object cleanup
		self.itemList = []

		if bIsRefresh == False:
			self.tooltipItem = None

class ListBoxHorizontal(ui.Window):
	class NewItem(ui.Window):
		def __init__(self, index, vnum, count, iNecessaryLevel, status):
			ui.Window.__init__(self)
			self.index = index
			self.vnum = vnum
			self.status = status
			self.iNecessaryLevel = iNecessaryLevel

			self.Reinitialize()

			self.bg = ui.ExpandedImageBox()
			self.bg.SetParent(self)
			self.bg.AddFlag("not_pick")
			self.bg.SetPosition(0, 0)
			self.bg.LoadImage(PATH_ROOT + "slice/board_base.png")
			self.bg.Show()

			item.SelectItem(vnum)

			self.wndIcon = ui.ExpandedImageBox()
			self.wndIcon.SetParent(self)
			self.wndIcon.AddFlag("not_pick")
			self.wndIcon.LoadImage(item.GetIconImageFileName())
			self.wndIcon.SetWindowHorizontalAlignCenter()
			self.wndIcon.SetWindowVerticalAlignCenter()
			self.wndIcon.Show()

			self.wndCount = MakeTextLineRightAlign(self.wndIcon)
			self.wndCount.SetPosition(1, 7)
			self.wndCount.SetText(str(count))
			self.wndCount.SetOutline()
			self.wndCount.Show()
			
			self.wndStatus = ui.ExpandedImageBox()
			self.wndStatus.SetParent(self)
			self.wndStatus.AddFlag("not_pick")
			if status == 0: # is currently locked
				self.wndStatus.LoadImage(PATH_ROOT + "slice/items/item_lock.png")
			elif status == 1: # is currently ongoing
				pass
			elif status == 2: # is currently done
				self.wndStatus.LoadImage(PATH_ROOT + "slice/items/item_done.png")
			self.wndStatus.SetWindowHorizontalAlignCenter()
			self.wndStatus.SetWindowVerticalAlignCenter()
			self.wndStatus.Show()

			# Create animated effect for collectible rewards
			self.wndCollectEffect = ui.AniImageBox()
			self.wndCollectEffect.SetParent(self)
			# self.wndCollectEffect.AddFlag("not_pick")
			# self.wndCollectEffect.AddFlag("float")
			self.wndCollectEffect.SetDelay(5)  # Animation speed
			# Load animation frames (reward_effect_00 to reward_effect_43)
			for i in xrange(44):
				self.wndCollectEffect.AppendImage(PATH_ROOT + "reward_effect/reward_effect_%02d.png" % i)
			self.wndCollectEffect.SetPosition(0, 0)
			self.wndCollectEffect.Hide()  # Hidden by default, shown in OnRender when collectible

			self.wndDesignLevel = None
			self.wndDesignLevelCount = None

			self.SetSize(self.bg.GetWidth() - 1, self.bg.GetHeight())		
	
		def SetItemToolTip(self, tooltipItem):
			self.tooltipItem = tooltipItem
		
		def SetDesignLevel(self):
			self.wndDesignLevel = ui.ExpandedImageBox()
			self.wndDesignLevel.SetParent(self.parent.parentBoard)
			self.wndDesignLevel.AddFlag("not_pick")
			self.wndDesignLevel.AddFlag("float")
			self.wndDesignLevel.LoadImage(PATH_ROOT + "slice/items/level_bar/bg_level_0.png")
			self.wndDesignLevel.Show()

			self.wndDesignLevelCount = ui.ExpandedImageBox()
			self.wndDesignLevelCount.SetParent(self.wndDesignLevel)
			self.wndDesignLevelCount.AddFlag("not_pick")
			self.wndDesignLevelCount.LoadImage(PATH_ROOT + "slice/items/level_bar/%d.png" % (self.iNecessaryLevel))
			self.wndDesignLevelCount.SetWindowHorizontalAlignCenter()
			self.wndDesignLevelCount.SetWindowVerticalAlignCenter()
			self.wndDesignLevelCount.Show()
	
		def OnRender(self):
			# FIX: Get current level from parent window instead of global
			currentLevel = self.GetCurrentBattlePassLevel()
			isCollectible = self.status != 2 and currentLevel >= self.iNecessaryLevel

			if self.status != 2:
				if currentLevel >= self.iNecessaryLevel:
					self.wndStatus.Hide()
			else:
				self.wndStatus.Show()

			# Show/hide collect effect based on collectibility
			if self.wndCollectEffect:
				if isCollectible:
					self.wndCollectEffect.Show()
				else:
					self.wndCollectEffect.Hide()

			try:
				xList, yList = self.parent.GetGlobalPosition()
				width, height = self.parent.GetWidth(), self.parent.GetHeight()

				# Clip images to parent bounds
				listImage = [self.bg, self.wndIcon, self.wndStatus]
				for image in listImage:
					if image:
						self.SetClipRect(image, xList, yList, xList + width, yList + height)

				if self.wndCollectEffect and isCollectible:
					xEffect, yEffect = self.wndCollectEffect.GetGlobalPosition()
					effectWidth = self.wndCollectEffect.GetWidth()
					effectHeight = self.wndCollectEffect.GetHeight()
					# Hide if outside parent bounds
					if xEffect + effectWidth < xList or xEffect > xList + width or yEffect + effectHeight < yList or yEffect > yList + height:
						self.wndCollectEffect.Hide()
					else:
						self.wndCollectEffect.Show()

				# Hide text if outside bounds
				listText = [self.wndCount]
				for text in listText:
					if text:
						xText, yText = text.GetGlobalPosition()
						# Hide if vertically outside bounds
						if yText < yList or yText + text.GetTextSize()[1] > yList + height:
							text.Hide()
						# Hide if horizontally outside bounds
						elif xText < xList + 10 or xText + text.GetTextSize()[0] - 10 > xList + width:
							text.Hide()
						else:
							text.Show()

				# Clip level design elements if present
				if self.wndDesignLevel:
					# Update position relative to board_BaseItems (parent of ListBox)
					listBoxX, listBoxY = self.parent.GetLocalPosition()
					itemX, itemY = self.GetLocalPosition()
					self.wndDesignLevel.SetPosition(listBoxX + itemX + 30, listBoxY + itemY + 84)
					self.wndDesignLevel.SetTop()
					# Use board bounds for clipping (extends below ListBox into Premium row)
					boardX, boardY = self.parent.parentBoard.GetGlobalPosition()
					boardW, boardH = self.parent.parentBoard.GetWidth(), self.parent.parentBoard.GetHeight()
					self.SetClipRect(self.wndDesignLevel, xList, boardY, xList + width, boardY + boardH)
					self.SetClipRect(self.wndDesignLevelCount, xList, boardY, xList + width, boardY + boardH)
			except (ReferenceError, AttributeError):
				# Handle weakref death gracefully
				pass


		def GetCurrentBattlePassLevel(self):
			"""Get level from parent ListBoxHorizontal - defaults to 0 if not found."""
			try:
				if hasattr(self, 'parent') and self.parent:
					if hasattr(self.parent, 'currentLevel'):
						return self.parent.currentLevel
			except (ReferenceError, AttributeError):
				# FIX: Handle weakref death or missing attribute gracefully
				pass
			return 0

		def OnRenderClip(self):
			pass
			xList, yList = self.parent.GetGlobalPosition()
			width, height = self.parent.GetWidth(), self.parent.GetHeight()

			listImage = [self.bg, self.wndIcon, self.wndStatus]
			for image in listImage:
				if image:
					self.SetClipRect(image, xList, yList, xList + width, yList + height)

			# Clip collect effect animation
			if self.wndCollectEffect:
				self.SetClipRect(self.wndCollectEffect, xList, yList, xList + width, yList + height)

			listText = [self.wndCount]
			for text in listText:
				if text:
					xText, yText = text.GetGlobalPosition()
					text.Hide() if yText < yList or yText + text.GetTextSize()[1] > yList + height else text.Show()

					if xText < xList+10 or xText + text.GetTextSize()[0]-10 > xList + width:
						text.Hide()

			if self.wndDesignLevel:
				self.SetClipRect(self.wndDesignLevel, xList, yList - 55, xList + width, yList - 55 + height)
				self.SetClipRect(self.wndDesignLevelCount, xList, yList - 55, xList + width, yList - 55 + height)

		def SetClipRect(self, image, fLeft, fTop, fRight, fBottom):
			# FIX: Check for zero dimensions to prevent division by zero
			imgWidth = image.GetWidth()
			imgHeight = image.GetHeight()
			if imgWidth <= 0 or imgHeight <= 0:
				return

			(left, top, right, bottom) = image.GetRect()
			right = right + left
			bottom = bottom + top

			# Calculate clipping ratios
			fDifLeft = -(float(fLeft - left) / float(imgWidth)) if (left < fLeft) else 0.0
			fDifTop = -(float(fTop - top) / float(imgHeight)) if (top < fTop) else 0.0
			fDifRight = -(float(right - fRight) / float(imgWidth)) if (right > fRight) else 0.0
			fDifBottom = -(float(bottom - fBottom) / float(imgHeight)) if (bottom > fBottom) else 0.0

			image.SetRenderingRect(fDifLeft, fDifTop, fDifRight, fDifBottom)

		def __del__(self):
			ui.Window.__del__(self)
			self.Reinitialize()

		def Reinitialize(self):
			self.xBase = 0
			self.yBase = 0

			self.bg = None
			self.tooltipItem = None
			self.wndWiki = None
			self.wndCollectEffect = None

		def SetParent(self, parent):
			ui.Window.SetParent(self, parent)
			self.parent = proxy(parent)

		def SetBasePosition(self, x, y):
			self.xBase = x
			self.yBase = y

		def GetBasePosition(self):
			return (self.xBase, self.yBase)

		def OnMouseOverIn(self):
			wnd = systemSetting.GetInterfaceHandler()
			if wnd == None:
				return

			isPremium = not self.wndDesignLevel

			IsPromo = False
			if not isPremium and self.vnum in [39008, 39030, 71084, 50513, 59050, 71035, 64748, 25041, 71136]:
				IsPromo = True

			if wnd.tooltipItem:
				wnd.tooltipItem.SetItemToolTip(self.vnum)#, IsPromo)
				if app.ENABLE_INGAME_WIKI and self.wndWiki:
					wnd.tooltipItem.AppendSpace(5)
					wnd.tooltipItem.AppendTextLine(localeinfo.ATLAS_BOSS_HINT_WIKI)
					wnd.tooltipItem.ResizeToolTip()
		
		def OnMouseOverOut(self):
			wnd = systemSetting.GetInterfaceHandler()
			if wnd == None:
				return

			if wnd.tooltipItem:
				wnd.tooltipItem.HideToolTip()

		def SetWikiInstance(self, wndWiki):
			"""Set wiki instance for opening item page on click."""
			self.wndWiki = wndWiki

		def OnMouseLeftButtonDown(self):
			"""Open wiki page for this item when clicked."""
			if not app.ENABLE_INGAME_WIKI:
				return

			if not self.wndWiki:
				return

			# Check if item is a box type (giftbox/gacha)
			item.SelectItem(self.vnum)
			isBoxType = item.GetItemType() in (item.ITEM_TYPE_GIFTBOX, item.ITEM_TYPE_GACHA)

			if not self.wndWiki.IsShow():
				net.ToggleWikiWindow()

			self.wndWiki.CloseBaseWindows()

			if isBoxType:
				self.wndWiki.mainChestWindow.Show([self.vnum,])
			else:
				self.wndWiki.OpenSpecialPage(None, self.vnum, False)

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
		self.wndWiki = None  # Wiki instance for opening item pages
		self.currentLevel = 0  # FIX: Instance variable for current battle pass level
		self.parentBoard = None  # Reference to parent board for level bar z-ordering

		self.selectEvent = None

	def SetParent(self, parent):
		ui.Window.SetParent(self, parent)
		self.parentBoard = parent  # Store reference to parent board

		self.SetPosition(5, 5)
		self.SetSize(parent.GetWidth() - 10, parent.GetHeight() - 10)

	def SetScrollBar(self, scrollBar):
		scrollBar.SetScrollSpeed(50)
		self.scrollBar = scrollBar

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def SetWikiInstance(self, wndWiki):
		"""Set wiki instance for opening item pages on click."""
		self.wndWiki = wndWiki
		# Update existing items
		for itemW in self.itemList:
			itemW.SetWikiInstance(self.wndWiki)

	def SetSelectEvent(self, event):
		self.selectEvent = event

	def GetTotalItemWidth(self):
		totalHeight = 0
		
		if self.itemList:
			for itemH in self.itemList:
				totalHeight += float(itemH.GetWidth())
				totalHeight -= 2.5
			
		return totalHeight

	def AppendItem(self, index, vnum, count, iNecessaryLevel, state, setDesignlevel = False):
		item = self.NewItem(index, vnum, count, iNecessaryLevel, state)
		item.SetParent(self)
		item.SetItemToolTip(self.tooltipItem)
		item.SetWikiInstance(self.wndWiki)

		if setDesignlevel:
			item.SetDesignLevel()
		
		if len(self.itemList) == 0:
			item.SetBasePosition(0, 0)
		else:
			x, y = self.itemList[-1].GetLocalPosition()

			item.SetBasePosition(x + self.itemList[-1].GetWidth(), 0)
			
		item.Show()
		self.itemList.append(item)
		
		# self.AdjustScrollBar()
		self.AdjustItemPositions()
	
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
		scrollPos = self.scrollBar.middleBar.GetLocalPosition()[0] * 0.0032
		totalHeight = self.GetTotalItemWidth() - self.GetWidth()

		idx = 0
		if startIndex >= 0:
			idx = startIndex

		for item in self.itemList[idx:]:
			xB, yB = item.GetBasePosition()
			
			if startIndex >= 0:
				yB -= 2
			
			if scrolling:
				setPos = xB - int(scrollPos * totalHeight)
				item.SetPosition(setPos, yB)
			else:
				item.SetPosition(xB, yB)
				
			item.SetBasePosition(xB, yB)

	def Clear(self, bIsRefresh = False):
		if len(self.itemList) == 0:
			return

		# FIX: Proper cleanup - don't use del on loop variable
		for item in self.itemList:
			item.Reinitialize()
			item.Hide()

		# Clear the list - Python GC handles object cleanup
		self.itemList = []

		if bIsRefresh == False:
			self.tooltipItem = None

class BattlePassWindow(ui.ScriptWindow):
	def __init__(self):
		self.bLoaded = False
		self.tooltipItem = None
		self.tooltipExpBoost = None
		self.tooltipBanner = None
		self.tooltipCategory = None
		self.tooltipCollect = None
		self.collectableRewardsCount = 0  # Track number of collectible rewards for flash effect
		self.ListBoxItem = None
		self.ListBoxItems = None
		self.ListBoxItemsPremium = None
		self.currentBattlePassLevel = 0  # FIX: Instance variable instead of global
		self.currentExp = 0  # Store EXP for restoring when switching pages
		self.currentMaxExp = 1  # Store max EXP for restoring when switching pages
		self.QuestionDialog = None
		self.isSkipInProgress = False
		self.isPremiumActive = False  # Track premium status for banner display
		self.wndWiki = None  # Wiki instance for opening item pages
		self.expTable = []  # List[int] of required_exp per level (sent by server via BP_EXP_TABLE)
		self.wndExpBoostDialog = None  # Bulk-use EXP boost dialog (lazy-created)
		# Parallel reward cache for the EXP boost preview (the existing reward NewItem
		# class doesn't store count as an attribute, so we mirror data here as it arrives).
		# Each entry: dict(vnum, count, status, isPremium, iNecessaryLevel)
		self.rewardCache = []

		# Timer tracking variables
		self.battlePassEndTime = 0  # Timestamp when battle pass ends
		self.dailyResetTime = 0     # Timestamp for daily mission reset
		self.weeklyResetTime = 0    # Timestamp for weekly mission reset
		self.lastTimerUpdate = 0    # Track last update to avoid updating every frame

		ui.ScriptWindow.__init__(self)
		self.LoadWindow()
		self.SetCenterPosition()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.ClearDictionary()

		self.categories = []

		if self.ListBoxItem:
			self.ListBoxItem.Clear()
		self.ListBoxItem = None

		if self.ListBoxItems:
			self.ListBoxItems.Clear()
		self.ListBoxItems = None

		if self.wndExpBoostDialog:
			self.wndExpBoostDialog.Hide()
		self.wndExpBoostDialog = None

		self.rewardCache = []
		self.expTable = []

		self.bLoadedInfo = False
		self.tooltipItem = None
		self.tooltipExpBoost = None
		self.tooltipBanner = None
		self.tooltipCategory = None
		self.tooltipCollect = None

	def SetItemToolTip(self, itemTooltip):
		self.tooltipItem = itemTooltip
		self.ListBoxItem.SetItemToolTip(self.tooltipItem)

	def SetWikiInstance(self, wndWiki):
		"""Set wiki window instance for opening item pages on click."""
		self.wndWiki = proxy(wndWiki) if wndWiki else None
		if self.ListBoxItems:
			self.ListBoxItems.SetWikiInstance(self.wndWiki)
		if self.ListBoxItemsPremium:
			self.ListBoxItemsPremium.SetWikiInstance(self.wndWiki)

	def Show(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "BATTLE_PASS")
		self.LoadWindow()
		self.SetTop()
		ui.ScriptWindow.Show(self)

		self.ListBoxItem.Clear()
		self.ListBoxItems.Clear()
		self.ListBoxItemsPremium.Clear()

		net.SendChatPacket("/battle_pass request")

	def OnUpdate(self):
		"""Called every frame to update timers."""
		if not self.IsShow():
			return

		current_timestamp = app.GetGlobalTimeStamp()

		# Only update text once per second to save performance
		if current_timestamp == self.lastTimerUpdate:
			return

		self.lastTimerUpdate = current_timestamp

		# Update Battle Pass end time
		if self.battlePassEndTime > 0:
			time_left = self.battlePassEndTime - current_timestamp
			if time_left > 0:
				self.wndBattlePassEndTime.SetText(localeinfo.BP_ENDS_IN % localeinfo.SecondToDHMNew(time_left))
			else:
				self.wndBattlePassEndTime.SetText(localeinfo.BP_ENDED)

		# Update Daily reset timer
		if self.dailyResetTime > 0 and hasattr(self, 'wndInfoDailyTime'):
			time_left = self.dailyResetTime - current_timestamp
			if time_left > 0:
				self.wndInfoDailyTime.SetText(localeinfo.BP_DAILY_RESET % localeinfo.SecondToDHMNew(time_left))
			else:
				self.wndInfoDailyTime.SetText(localeinfo.BP_MISSIONS_AVAILABLE)

		# Update Weekly reset timer
		if self.weeklyResetTime > 0 and hasattr(self, 'wndInfoWeeklyTime'):
			time_left = self.weeklyResetTime - current_timestamp
			if time_left > 0:
				self.wndInfoWeeklyTime.SetText(localeinfo.BP_WEEKLY_RESET % localeinfo.SecondToDHMNew(time_left))
			else:
				self.wndInfoWeeklyTime.SetText(localeinfo.BP_MISSIONS_AVAILABLE)

	def SetBattlePassEndTime(self, endTime):
		"""Set the battle pass end time (timestamp from server)."""
		self.battlePassEndTime = int(endTime) + app.GetGlobalTimeStamp()

	def SetDailyResetTime(self, resetTime):
		"""Set the daily mission reset time (seconds until reset from server)."""
		self.dailyResetTime = int(resetTime) + app.GetGlobalTimeStamp()

	def SetWeeklyResetTime(self, resetTime):
		"""Set the weekly mission reset time (seconds until reset from server)."""
		self.weeklyResetTime = int(resetTime) + app.GetGlobalTimeStamp()

	def SetResetTimes(self, dailyResetTime, weeklyResetTime):
		"""Set both daily and weekly reset times at once."""
		self.SetDailyResetTime(dailyResetTime)
		self.SetWeeklyResetTime(weeklyResetTime)

	def LoadWindow(self):
		if self.bLoaded == True:
			return
			
		self.bLoaded = True

		self.AddFlag("movable")
		self.AddFlag("float")
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		# self.BoardEx = ui.Board()
		# self.BoardEx.SetParent(self)
		# self.BoardEx.SetSize(180, 45)
		# self.BoardEx.SetPosition(320, 290)
		# self.BoardEx.Show()
	
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetParent(self)
		self.Board.SetSize(499, 285 + 35 + 25)
		self.Board.SetTitleName(localeinfo.MINIMAP_SHOW_PASS_INFO)
		self.Board.SetCloseEvent(ui.__mem_func__(self.Close))
		self.Board.Show()
		
		self.SetSize(self.Board.GetWidth(), self.Board.GetHeight() + 32)
			
		self.LoadTopBoard()
		self.LoadBottomBoard()
		
		self.LoadItemsByExpBoard()
		self.LoadMiddleBoard()
		
		self.ClickCategory()
		self.RefreshCategory()
		
	def OnOpenShop(self):
		net.SendRemoteShopPacket(5)

	def OnUseExpBoost(self):
		# Bulk-use EXP boost dialog (replaces the per-click confirmation flow).
		#
		# IMPORTANT: recreate the dialog every open instead of caching. Caching
		# breaks after a warp/channel transfer because the cached dialog's
		# `proxy(parentBP)` keeps pointing at the previous BP window state —
		# snapshots/previews silently no-op against stale data and the user sees
		# "Use clicked but nothing happens." Fresh dialog every open = fresh proxy
		# bound to the current BP window state.
		if self.wndExpBoostDialog is not None:
			try:
				self.wndExpBoostDialog.Hide()
			except (ReferenceError, AttributeError):
				pass
			self.wndExpBoostDialog = None

		import uibattlepass_expboost
		self.wndExpBoostDialog = uibattlepass_expboost.ExpBoostDialog()
		self.wndExpBoostDialog.Bind(self, self.tooltipItem)
		self.wndExpBoostDialog.Open()

	def AnswerQuestionExpBoost(self, answer):
		if not self.QuestionDialog:
			self.isSkipInProgress = False
			return

		if answer:
			net.SendChatPacket("/battle_pass expboost")

		self.QuestionDialog.Close()
		self.QuestionDialog = None
		self.isSkipInProgress = False

	def OnExpBoostMouseOverIn(self):
		if self.tooltipExpBoost:
			self.tooltipExpBoost.ShowToolTip()

	def OnExpBoostMouseOverOut(self):
		if self.tooltipExpBoost:
			self.tooltipExpBoost.HideToolTip()

	def OnBannerMouseOverIn(self):
		"""Called when mouse enters the banner area."""
		if self.tooltipBanner:
			self.tooltipBanner.ShowToolTip()

	def OnBannerMouseOverOut(self):
		"""Called when mouse leaves the banner area."""
		if self.tooltipBanner:
			self.tooltipBanner.HideToolTip()

	def __CreateBannerTooltip(self):
		"""Create a simple tooltip for the banner."""
		self.tooltipBanner = uitooltip.ToolTip()
		self.tooltipBanner.ClearToolTip()
		self.tooltipBanner.AppendTextLine(localeinfo.BP_BANNER_TOOLTIP)
		self.tooltipBanner.ResizeToolTip()
		self.tooltipBanner.HideToolTip()

	def __CreateCategoryTooltip(self):
		"""Create a simple tooltip for the category button."""
		self.tooltipCategory = uitooltip.ToolTip()
		self.tooltipCategory.ClearToolTip()
		self.tooltipCategory.AppendTextLine(localeinfo.BP_CATEGORY_TOOLTIP)
		self.tooltipCategory.ResizeToolTip()
		self.tooltipCategory.HideToolTip()

	def __CreateCollectTooltip(self):
		"""Create a simple tooltip for the collect button."""
		self.tooltipCollect = uitooltip.ToolTip()
		self.tooltipCollect.ClearToolTip()
		self.tooltipCollect.AppendTextLine(localeinfo.BP_COLLECT_TOOLTIP)
		self.tooltipCollect.ResizeToolTip()
		self.tooltipCollect.HideToolTip()

	def OnCategoryOverIn(self):
		if self.tooltipCategory:
			self.tooltipCategory.ShowToolTip()

	def OnCategoryOverOut(self):
		if self.tooltipCategory:
			self.tooltipCategory.HideToolTip()

	def OnCollectOverIn(self):
		if self.tooltipCollect:
			self.tooltipCollect.ShowToolTip()

	def OnCollectOverOut(self):
		if self.tooltipCollect:
			self.tooltipCollect.HideToolTip()

	def __UpdateCollectButtonFlash(self):
		"""Enable or disable flash effect on collect button based on collectible rewards."""
		if not self.btnCollect:
			return

		if self.collectableRewardsCount > 0:
			self.btnCollect.EnableFlash()
		else:
			self.btnCollect.DisableFlash()

	def OnRewardsCollected(self, count=0):
		"""Called when rewards are collected to update the flash effect.

		Args:
			count: Number of rewards collected. If 0, disables flash entirely.
		"""
		if count > 0:
			self.collectableRewardsCount = max(0, self.collectableRewardsCount - count)
		else:
			self.collectableRewardsCount = 0
		self.__UpdateCollectButtonFlash()

	def RefreshCollectButtonFlash(self):
		"""Recount collectible rewards and update flash state.
		Called after all reward data is loaded and premium status is known."""
		self.collectableRewardsCount = 0

		# Count free rewards that can be collected
		# A reward is collectible if: status != 2 (not already collected) AND level >= required level
		if self.ListBoxItems and self.ListBoxItems.itemList:
			for rewardItem in self.ListBoxItems.itemList:
				# status 0 = locked by server, status 1 = can collect, status 2 = already collected
				# But server may send status=0 even when level is reached, so check level too
				if rewardItem.status != 2 and self.currentBattlePassLevel >= rewardItem.iNecessaryLevel:
					self.collectableRewardsCount += 1

		# Count premium rewards if premium is active
		if self.isPremiumActive and self.ListBoxItemsPremium and self.ListBoxItemsPremium.itemList:
			for rewardItem in self.ListBoxItemsPremium.itemList:
				if rewardItem.status != 2 and self.currentBattlePassLevel >= rewardItem.iNecessaryLevel:
					self.collectableRewardsCount += 1

		self.__UpdateCollectButtonFlash()

	def __CreateExpBoostTooltip(self):
		"""Create a rich tooltip for the EXP Boost button with item icon and description lines."""
		self.tooltipExpBoost = uitooltip.RichItemToolTip(220)

		# Get item name for the title
		item.SelectItem(ITEM_VNUM_BP_EXP_BOOST)
		itemName = item.GetItemName()

		# Build description lines using locale strings
		descriptions = [
			(localeinfo.BP_EXP_BOOST_TOOLTIP_TITLE, self.tooltipExpBoost.TITLE_COLOR),
			"",
			(localeinfo.BP_EXP_BOOST_TOOLTIP_DESC1, self.tooltipExpBoost.DESC_COLOR),
			(localeinfo.BP_EXP_BOOST_TOOLTIP_DESC2, self.tooltipExpBoost.HIGHLIGHT_COLOR),
		]

		# Footer text
		footer = localeinfo.BP_EXP_BOOST_TOOLTIP_FOOTER

		# Set up the tooltip
		self.tooltipExpBoost.AddItemWithDescription(
			ITEM_VNUM_BP_EXP_BOOST,
			itemName,
			descriptions,
			footer
		)
		self.tooltipExpBoost.HideToolTip()

	def LoadTopBoard(self):
		self.boardExpInfo = ui.MakeExpandedImageBox(self, PATH_ROOT+"slice/" + "top_bg.png", 8, 30, "not_pick")


		# Banner starts with non-active image, will be updated when premium status is received
		self.bannerMonth = ui.MakeImageBoxAE(self, PATH_ROOT+"slice/banners/" + "banner_nonactive.png", 239 + 51, 32)
		self.bannerMonth.SetEvent(ui.__mem_func__(self.OnOpenShop), "mouse_click")
		# Add hover events to parent banner as well
		self.bannerMonth.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OnBannerMouseOverIn)
		self.bannerMonth.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OnBannerMouseOverOut)

		# Banner animated effect (now interactive - click opens shop, hover shows tooltip)
		self.wndAnibanner = ui.AniImageBoxButton()
		self.wndAnibanner.SetParent(self.bannerMonth)
		self.wndAnibanner.SetPosition(0, 0)
		self.wndAnibanner.SetDelay(5)
		self.wndAnibanner.Show()

		# Banner click event - opens shop just like the parent banner
		self.wndAnibanner.SetEvent(ui.__mem_func__(self.OnOpenShop), "MOUSE_CLICK")
		# Banner hover events for tooltip
		self.wndAnibanner.SetEvent(ui.__mem_func__(self.OnBannerMouseOverIn), "MOUSE_OVER_IN")
		self.wndAnibanner.SetEvent(ui.__mem_func__(self.OnBannerMouseOverOut), "MOUSE_OVER_OUT")

		self.dictImagesBannerEffect = []
		for x in xrange(61):
			self.wndAnibanner.AppendImage(PATH_ROOT+"effect/new_%02d.png" % (x))

		# Create banner tooltip
		self.__CreateBannerTooltip()

		self.wndBattlePassEndTime = ui.TextLine()
		self.wndBattlePassEndTime.SetParent(self.bannerMonth)
		self.wndBattlePassEndTime.SetPosition(196/2, 36)
		self.wndBattlePassEndTime.SetHorizontalAlignCenter()
		self.wndBattlePassEndTime.SetOutline()
		self.wndBattlePassEndTime.SetText("")
		self.wndBattlePassEndTime.Show()

		self.wndLevel = ui.MakeTextLineNew(self.boardExpInfo, 50, 10, "Lv. 0")
		self.wndEXP = ui.MakeTextLineNew(self.boardExpInfo, 150, 10, "0/100 EXP")

		# Quest progress text element (hidden by default, shown on quest page)
		self.wndQuestProgress = ui.MakeTextLineNew(self.boardExpInfo, 150 + 30, 9, "")
		self.wndQuestProgress.SetHorizontalAlignLeft()
		self.wndQuestProgress.SetOutline()
		self.wndQuestProgress.Hide()

		self.boardGaugeEXP = ui.MakeExpandedImageBox(self, PATH_ROOT+"slice/" + "gauge.png", 34 - 21, 60, "not_pick")
		self.GaugeEXP = ui.MakeExpandedImageBox(self.boardGaugeEXP, PATH_ROOT+"slice/" + "gauge_inner.png", 3, 3, "not_pick")

		# Gauge Lines
		self.LinegaugeEXP1 = ui.MakeExpandedImageBox(self.boardGaugeEXP, PATH_SLICE + "gauge_line.png", 37, 1, "not_pick")
		self.LinegaugeEXP2 = ui.MakeExpandedImageBox(self.boardGaugeEXP, PATH_SLICE + "gauge_line.png", 33*2, 1, "not_pick")
		self.LinegaugeEXP3 = ui.MakeExpandedImageBox(self.boardGaugeEXP, PATH_SLICE + "gauge_line.png", 33*3, 1, "not_pick")
		self.LinegaugeEXP4 = ui.MakeExpandedImageBox(self.boardGaugeEXP, PATH_SLICE + "gauge_line.png", 33*4, 1, "not_pick")
		self.LinegaugeEXP5 = ui.MakeExpandedImageBox(self.boardGaugeEXP, PATH_SLICE + "gauge_line.png", 33*5, 1, "not_pick")
		self.LinegaugeEXP6 = ui.MakeExpandedImageBox(self.boardGaugeEXP, PATH_SLICE + "gauge_line.png", 33*6, 1, "not_pick")
		self.LinegaugeEXP7 = ui.MakeExpandedImageBox(self.boardGaugeEXP, PATH_SLICE + "gauge_line.png", 33*7, 1, "not_pick")

		# EXP Boost Button (using Button for hover pulse support)
		self.wndExpBoost = ui.MakeButton(self, 189, 35, "", PATH_SLICE, "btnx_level_up_0.png", "btnx_level_up_1.png", "btnx_level_up_2.png")
		self.wndExpBoost.SetEvent(ui.__mem_func__(self.OnUseExpBoost))
		self.wndExpBoost.Show()

		# Enable hover pulse effect (smooth glow animation)
		self.wndExpBoost.EnableHoverPulse()
		self.wndExpBoost.SetHoverPulseSpeed(1.5)  # 1.5 cycles per second

		# Rich tooltip for EXP Boost button with item icon and description
		self.__CreateExpBoostTooltip()

		# Set hover events for tooltip (Button uses SetEventOverIn/Out)
		self.wndExpBoost.SetEventOverIn(ui.__mem_func__(self.OnExpBoostMouseOverIn))
		self.wndExpBoost.SetEventOverOut(ui.__mem_func__(self.OnExpBoostMouseOverOut))

		# # GaugeEXP Effect
		# self.wndAnimEXP = ui.AniImageBox()
		# self.wndAnimEXP.SetParent(self.boardGaugeEXP)
		# self.wndAnimEXP.SetPosition(0, 0)
		# self.wndAnimEXP.SetDelay(3)
		# self.wndAnimEXP.Show()
		
		# self.dictImagesEXPEffect = []
		# for x in xrange(53):
			# self.wndAnimEXP.AppendImage(PATH_ROOT+"gauge effect gif/gauge_effect_%02d.png" % (x))
		
	def GetSecondsLeftUntilNextDay(self):
		current_time = datetime.utcnow()
		next_day = current_time + timedelta(days=1)
		next_day_midnight = datetime(year=next_day.year, month=next_day.month, day=next_day.day)
		time_left = next_day_midnight - current_time

		return int(time_left.total_seconds())
		
	def LoadMiddleBoard(self):
		self.board_Base = ui.BoxedBoard()
		self.board_Base.SetParent(self.Board)
		self.board_Base.SetPosition(8, 90 + 25)
		self.board_Base.SetSize(482, 218)
		self.board_Base.Show()

		self.categories = []

		# Daily reset timer text
		self.wndInfoDailyTime = ui.MakeTextLineNew(self.board_Base, self.GetWidth() - 35, -20, "right")
		# Weekly reset timer text (same position, shown when weekly tab is selected)
		self.wndInfoWeeklyTime = ui.MakeTextLineNew(self.board_Base, self.GetWidth() - 35, -20, "right")
		self.wndInfoWeeklyTime.Hide()

		btnCategory1 = ui.MakeRadioButton(self, 8, 91, "",PATH_ROOT+"slice/quest/" , "btn_l_0.png", "btn_l_1.png", "btn_l_1.png")
		btnCategory1.category = 0
		btnCategory1.SetText(localeinfo.BP_DAILY_MISSIONS)
		btnCategory1.Down()

		self.categories.append(btnCategory1)

		btnCategory2 = ui.MakeRadioButton(self, 8 + 84, 91, "",PATH_ROOT+"slice/quest/" , "btn_m_0.png", "btn_m_1.png", "btn_m_1.png")
		btnCategory2.category = 1
		btnCategory2.SetText(localeinfo.BP_WEEKLY_MISSIONS)
		self.categories.append(btnCategory2)

		btnCategory3 = ui.MakeRadioButton(self, 8 + 84 + 82, 91, "",PATH_ROOT+"slice/quest/" , "btn_r_0.png", "btn_r_1.png", "btn_r_1.png")
		btnCategory3.category = 2
		btnCategory3.SetText(localeinfo.BP_MONTHLY_MISSIONS)
		self.categories.append(btnCategory3)
	
		for i, btnCat in enumerate(self.categories):
			btnCat.SetEvent(ui.__mem_func__(self.ClickCategoryMission), btnCat.category)
		
		# Mission List Code
		self.ScrollBarItem = ui.NewBpScrollBar()
		self.ScrollBarItem.SetParent(self.board_Base)
		self.ScrollBarItem.SetScrollBarSize(self.board_Base.GetHeight() - 6)
		self.ScrollBarItem.SetPosition(self.board_Base.GetWidth() - 12, 3)
		self.ScrollBarItem.Show()

		self.ListBoxItem = ListBox()
		self.ListBoxItem.SetParent(self.board_Base)
		self.ListBoxItem.SetScrollBar(self.ScrollBarItem)
		self.ListBoxItem.SetSize(self.board_Base.GetWidth() - self.ScrollBarItem.GetWidth() - 2, self.board_Base.GetHeight() - 4)
		self.ListBoxItem.SetPosition(2, 2)
		self.ListBoxItem.Show()

	def LoadBottomBoard(self):
		self.currentCategory = 1

		self.btnCategory = ui.MakeButton(self, 2, 275+ 35 + 25, "", PATH_ROOT+"slice/" , "btns_quests.tga", "btns_quests.tga", "btns_quests.tga")
		self.btnCategory.SetEvent(ui.__mem_func__(self.ClickCategory))
		self.btnCategory.SetEventOverIn(ui.__mem_func__(self.OnCategoryOverIn))
		self.btnCategory.SetEventOverOut(ui.__mem_func__(self.OnCategoryOverOut))
		# Collect Button
		self.btnCollect = ui.MakeButton(self, 423, 275+ 35 + 25, "", PATH_ROOT+"slice/" , "btn_collect_0.png", "btn_collect_1.png", "btn_collect_2.png")
		self.btnCollect.SetEvent(ui.__mem_func__(self.ClickCollect))
		self.btnCollect.SetEventOverIn(ui.__mem_func__(self.OnCollectOverIn))
		self.btnCollect.SetEventOverOut(ui.__mem_func__(self.OnCollectOverOut))

		# Create tooltips
		self.__CreateCategoryTooltip()
		self.__CreateCollectTooltip()

		# Shop Button
		# self.btnShop = ui.MakeButton(self, 330, 275+ 42, "", PATH_ROOT+"slice/quest/" , "btn_0.png", "btn_1.png", "btn_2.png")
		# self.btnShop.SetText("Shop")
		# self.btnShop.SetEvent(ui.__mem_func__(self.ClickShop))	
	
	def LoadItemsByExpBoard(self):
		self.board_Base_items = ui.MakeExpandedImageBox(self, PATH_ROOT+"slice/items/" + "bg_fram_norm.png", 8, 90, "not_pick")

		self.board_BaseItems = ui.BorderA()
		self.board_BaseItems.SetParent(self.board_Base_items)
		self.board_BaseItems.SetPosition(72, 1)
		self.board_BaseItems.SetSize(409, 193)
		self.board_BaseItems.Show()

		self.ScrollBarItems = ingamewikiui.WikiScrollBar(True)
		self.ScrollBarItems.SetParent(self)
		self.ScrollBarItems.SetSize(481, 12)
		self.ScrollBarItems.SetPosition(8, 287)
		self.ScrollBarItems.SetStaticScale(90)
		self.ScrollBarItems.Show()
		
		self.ListBoxItems = ListBoxHorizontal()
		self.ListBoxItems.SetParent(self.board_BaseItems)
		self.ListBoxItems.SetScrollBar(self.ScrollBarItems)
		self.ListBoxItems.SetSize(self.board_BaseItems.GetWidth() - 5, 100)
		self.ListBoxItems.SetPosition(3, 3)
		self.ListBoxItems.Show()

		self.ListBoxItemsPremium = ListBoxHorizontal()
		self.ListBoxItemsPremium.SetParent(self.board_BaseItems)
		self.ListBoxItemsPremium.SetScrollBar(self.ScrollBarItems)
		self.ListBoxItemsPremium.SetSize(self.board_BaseItems.GetWidth() - 5, 100)
		self.ListBoxItemsPremium.SetPosition(3, 98)
		self.ListBoxItemsPremium.Show()

		self.ScrollBarItems.SetScrollEvent(self.OnScrollPageItems)
		
		# Premium Lock
		self.premium_board = ui.MakeExpandedImageBox(self.board_BaseItems, PATH_ROOT+"slice/items/" + "big_lock.png", 1, 100, "not_pick")

		self.btnPreviewPremium = ui.MakeButton(self.premium_board , 245, 33, "", PATH_ROOT+"slice/quest/" , "btn_0.png", "btn_1.png", "btn_2.png")
		self.btnPreviewPremium.SetEvent(ui.__mem_func__(self.ClickPreviewPremium))
		self.btnPreviewPremium.SetText(localeinfo.BP_PREVIEW_REWARD)

		# test
		# for x in xrange(20):
			# self.ListBoxItems.AppendItem(x, 71084, 15 + x, 2, True)
			# self.ListBoxItemsPremium.AppendItem(x, 71085, 15 + x, False)
			
		# self.SetExperience(150, 300)
	
	def OnScrollPageItems(self):
		self.ListBoxItems.AdjustItemPositions(True)
		self.ListBoxItemsPremium.AdjustItemPositions(True)
	
	def ClickPreviewPremium(self):
		self.premium_board.Hide()
	
	def ClickCollect(self):
		net.SendChatPacket("/battle_pass collect")
	
	def ClickShop(self):
		net.SendChatPacket("/open_shop %d" % (OPEN_SHOP_ID))
	
	def ClickCategory(self):
		self.currentCategory = not self.currentCategory

		if self.currentCategory == 0:
			self.btnCategory.SetUpVisual(PATH_ROOT+"slice/" + "btns_items.tga")
			self.btnCategory.SetOverVisual(PATH_ROOT+"slice/" + "btns_items.tga")
			self.btnCategory.SetDownVisual(PATH_ROOT+"slice/" + "btns_items.tga")
			
			self.Board.SetSize(499, 285 + 35)
			self.btnCategory.SetPosition(2, 275+ 35)
			self.btnCollect.SetPosition(423, 275+ 35)
			
			for btnCat in self.categories:
				btnCat.Hide()
		else:
			self.btnCategory.SetUpVisual(PATH_ROOT+"slice/" + "btns_quests.tga")
			self.btnCategory.SetOverVisual(PATH_ROOT+"slice/" + "btns_quests.tga")
			self.btnCategory.SetDownVisual(PATH_ROOT+"slice/" + "btns_quests.tga")
			
			self.Board.SetSize(499, 285 + 35 + 25)
			self.btnCategory.SetPosition(2, 275+ 35 + 25)
			self.btnCollect.SetPosition(423, 275+ 35 + 25)
			
			for btnCat in self.categories:
				btnCat.Show()
			
		self.RefreshCategory()
	
	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "BATTLE_PASS")
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

		self.Hide()

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("BATTLE_PASS", x, y)

	def OnPressEscapeKey(self):
		self.Close()
		return True
	
	def RefreshCategory(self):
		if self.currentCategory == 1:
			# Quest page
			self.board_Base.Show()
			self.board_Base_items.Hide()
			self.ScrollBarItems.Hide()
			self.btnCollect.Hide()
			# Show quest progress elements, hide level/EXP elements
			self.wndLevel.Hide()
			self.wndEXP.Hide()
			self.wndQuestProgress.Show()
			# Hide EXP boost button on quest page
			self.wndExpBoost.Hide()
			# Update quest progress display
			self.__UpdateMissionProgress()
		else:
			# Rewards page
			self.board_Base_items.Show()
			self.board_Base.Hide()
			self.ScrollBarItems.Show()
			self.btnCollect.Show()
			# Show level/EXP elements, hide quest progress elements
			self.wndLevel.Show()
			self.wndEXP.Show()
			self.wndQuestProgress.Hide()
			# Show EXP boost button on rewards page
			self.wndExpBoost.Show()
			# Restore level/EXP display and gauge
			self.SetLevel(self.currentBattlePassLevel)
			exp = getattr(self, 'currentExp', 0)
			maxExp = getattr(self, 'currentMaxExp', 1)
			self.GaugeEXP.SetPercentage(exp, maxExp)

		# Update banner for current page
		self.__UpdateBannerImage()
	
	# Recv Packets
	def AppendMission(self, category, index, title, type, vnum, count, maxCount, expRecv, isPremium, coolTime):
		self.ListBoxItem.AppendItem(category, index, title, type, vnum, count, maxCount, expRecv, None, isPremium, coolTime)

	def AppendMissionReward(self, category, index, vnum, count):
		self.ListBoxItem.AppendItemReward(category, index, vnum, count)
		
	def UpdateMission(self, index, count, coolTime):
		self.ListBoxItem.UpdateMissionCount(index, count, coolTime)
		# Update quest progress display if on quest page
		if self.currentCategory == 1:
			self.__UpdateMissionProgress()
		
	def AppendRewardItem(self, index, vnum, count, status, isPremium, iNecessaryLevel):
		if isPremium:
			self.ListBoxItemsPremium.AppendItem(index, vnum, count, iNecessaryLevel, status)
		else:
			self.ListBoxItems.AppendItem(index, vnum, count, iNecessaryLevel, status, True)
		# Mirror into reward cache used by the EXP boost preview dialog
		self.rewardCache.append({
			"index" : index,
			"vnum" : vnum,
			"count" : count,
			"status" : status,
			"isPremium" : isPremium,
			"iNecessaryLevel" : iNecessaryLevel,
		})
		# Note: Flash state is updated in RefreshCollectButtonFlash() called from BattlePassInfoGeneral

	def SetExperience(self, exp, maxExp):
		# FIX: Robust handling of edge cases
		if maxExp <= 0:
			maxExp = 1
		if exp < 0:
			exp = 0
		# FIX: Cap exp at maxExp to prevent gauge overflow
		if exp > maxExp:
			exp = maxExp

		# Store values for restoring when switching pages
		self.currentExp = exp
		self.currentMaxExp = maxExp

		self.wndEXP.SetText("%d/%d EXP" % (exp, maxExp))
		# Only update gauge if on rewards page (not quest page)
		if self.currentCategory != 1:
			self.GaugeEXP.SetPercentage(exp, maxExp)

	def SetExpTable(self, caps):
		"""Cache the per-level required-EXP curve (sent by server via BP_EXP_TABLE).
		Used by the EXP boost preview dialog to predict target level for arbitrary EXP gain."""
		self.expTable = list(caps) if caps else []

	def GetExpTable(self):
		return self.expTable
	
	def SetLevel(self, currentLevel):
		self.wndLevel.SetText("Lv. %d" % (currentLevel + 1))

		# FIX: Store level in instance instead of global
		self.currentBattlePassLevel = currentLevel

		# Update level on list boxes so items can access it
		if self.ListBoxItems:
			self.ListBoxItems.currentLevel = currentLevel
		if self.ListBoxItemsPremium:
			self.ListBoxItemsPremium.currentLevel = currentLevel
	
	def UnlockPremium(self):
		self.premium_board.Hide()
		self.isPremiumActive = True
		self.__UpdateBannerImage()
		# Refresh flash state now that premium status is known
		self.RefreshCollectButtonFlash()

	def __UpdateBannerImage(self):
		"""Update the banner image based on current page and premium status."""
		if not self.bannerMonth:
			return

		# Quest page shows quest banner
		if self.currentCategory == 1:
			self.bannerMonth.LoadImage(PATH_ROOT + "slice/banners/banner_quest.png")
		elif self.isPremiumActive:
			self.bannerMonth.LoadImage(PATH_ROOT + "slice/banners/banner_premium.png")
		else:
			self.bannerMonth.LoadImage(PATH_ROOT + "slice/banners/banner_nonactive.png")
	
	def ClearBattlePass(self):
		self.ListBoxItem.Clear()
		self.ListBoxItems.Clear()
		self.ListBoxItemsPremium.Clear()
		# Clear EXP boost preview cache too
		self.rewardCache = []
		# Reset premium status - will be set again when server sends data
		self.isPremiumActive = False
		self.__UpdateBannerImage()
		# Reset collectible rewards count and disable flash
		self.collectableRewardsCount = 0
		self.__UpdateCollectButtonFlash()
		# Reset timer values - will be set again when server sends data
		self.battlePassEndTime = 0
		self.dailyResetTime = 0
		self.weeklyResetTime = 0
		if hasattr(self, 'wndBattlePassEndTime'):
			self.wndBattlePassEndTime.SetText("")

	def OnRunMouseWheel(self, nLen):
		if self.board_Base.IsShow():	
			if nLen > 0:
				self.ScrollBarItem.OnUp()
			else:
				self.ScrollBarItem.OnDown()
		else:
			self.ScrollBarItems.OnRunMouseWheel(nLen)

	def ClickCategoryMission(self, index):
		# Show/hide appropriate timer based on selected category
		if index == 0:  # Daily
			self.wndInfoDailyTime.Show()
			self.wndInfoWeeklyTime.Hide()
		elif index == 1:  # Weekly
			self.wndInfoDailyTime.Hide()
			self.wndInfoWeeklyTime.Show()
		else:  # Monthly - no timer
			self.wndInfoDailyTime.Hide()
			self.wndInfoWeeklyTime.Hide()

		self.selectedCategoryMission = index
		
		for i, btnCat in enumerate(self.categories):
			if index == btnCat.category:
				btnCat.Down()
			else:
				btnCat.SetUp()		
		
		self.ListBoxItem.RefreshList(self.selectedCategoryMission)

		self.ListBoxItem.ResetScrollbar()
		self.ListBoxItem.AdjustScrollBar()
		self.ListBoxItem.AdjustItemPositions()

		# Update quest progress display for new subcategory
		if self.currentCategory == 1:
			self.__UpdateMissionProgress()

	def __GetMissionProgress(self):
		"""Calculate mission completion progress for each category.
		Returns dict: {category: [completed, total]}
		"""
		progress = {0: [0, 0], 1: [0, 0], 2: [0, 0]}  # Daily, Weekly, Monthly

		if not self.ListBoxItem:
			return progress

		for item in self.ListBoxItem.itemList:
			category = item.category
			progress[category][1] += 1  # total
			if item.count >= item.maxCount:
				progress[category][0] += 1  # completed

		return progress

	def __UpdateMissionProgress(self):
		"""Update quest progress display elements (not level/EXP elements)."""
		progress = self.__GetMissionProgress()

		# Get progress for currently selected mission subcategory
		category = getattr(self, 'selectedCategoryMission', 0)
		completed, total = progress.get(category, [0, 0])

		if total <= 0:
			total = 1

		# Update quest progress text
		self.wndQuestProgress.SetText("{} : {}/{}".format(localeinfo.BATTLE_PASS_COMPLETED_QUESTS,total, completed))

		# Update gauge with quest completion percentage
		self.GaugeEXP.SetPercentage(completed, total)
