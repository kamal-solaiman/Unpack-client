import ui
import app
import grp
import net
import chat
import item
from _weakref import proxy
import nonplayer
import wndMgr
import localeinfo, uiscriptlocale
import player
import mouseModule
from datetime import datetime, timedelta
import constinfo

PATH_ROOT = "d:/ymir work/ui/game/guild_reworked/"
PATH_ICONS = "d:/ymir work/ui/game/guild_reworked/slice/quest/icons/"

CACHE_TIMESEC_INFO = 5 # auto request after cache is done

# enum SGuildMissionTypes
# {
GUILD_MISSION_KILL_MONSTER	= 1
GUILD_MISSION_KILL_STONE	= 2
GUILD_MISSION_KILL_BOSS		= 3
GUILD_MISSION_USE_ITEM 		= 4
GUILD_MISSION_MINING 		= 5
GUILD_MISSION_FISHING 		= 6
# };

TITLE_TYPES = {\
	GUILD_MISSION_KILL_MONSTER : localeinfo.GUILD_RENEWEL_TITLE_TYPE1,\
	GUILD_MISSION_KILL_STONE : localeinfo.GUILD_RENEWEL_TITLE_TYPE1,\
	GUILD_MISSION_KILL_BOSS : localeinfo.GUILD_RENEWEL_TITLE_TYPE1,\
	GUILD_MISSION_USE_ITEM : localeinfo.GUILD_RENEWEL_TITLE_TYPE1,\
	GUILD_MISSION_MINING : localeinfo.GUILD_RENEWEL_TITLE_TYPE1,\
	GUILD_MISSION_FISHING : localeinfo.GUILD_RENEWEL_TITLE_TYPE1\
}

def GetNameByTypeVnum(type, vnum):
	if vnum == 0:
		return localeinfo.GUILD_RENEWAL_TYPE_ALL

	if type in [GUILD_MISSION_KILL_MONSTER, GUILD_MISSION_KILL_STONE, GUILD_MISSION_KILL_BOSS]:
		return localeinfo.GUILD_RENEWAL_TYPE_MONSTERS if vnum == 0 else nonplayer.GetMonsterName(vnum)
	elif type in [GUILD_MISSION_USE_ITEM, GUILD_MISSION_MINING, GUILD_MISSION_FISHING]:
		if vnum:
			item.SelectItem(vnum)
			return item.GetItemName()
		else:
			return localeinfo.GUILD_RENEWAL_TYPE_ITEMS

	return localeinfo.GUILD_RENEWAL_TYPE_ALL

class ListBox(ui.Window):
	class NewItem(ui.Window):
		def __init__(self, category, mID, curCount, startTime, maxCount, type, vnum, expReward, pointReward, parent):
			ui.Window.__init__(self)
			self.category = category
			self.index = mID
			self.select = False
	
			title = TITLE_TYPES[type]
			self.title = title
			self.type = type
			self.vnum = vnum
			self.count = curCount
			self.maxCount = maxCount
			self.expReward = expReward
			self.pointReward = pointReward
			self.startTime = startTime
	
			self.Reinitialize()

			self.bg = ui.ExpandedImageBox()
			self.bg.SetParent(self)
			self.bg.AddFlag("not_pick")
			self.bg.SetPosition(0, 0)
			self.bg.image = PATH_ROOT + "slice/quest/" + "quest_blue.png"
			self.bg.LoadImage(self.bg.image)
			self.bg.Show()
			
			self.SetSize(self.bg.GetWidth(), self.bg.GetHeight())		

			self.wndIcon = ui.ExpandedImageBox()
			self.wndIcon.SetParent(self)
			self.wndIcon.AddFlag("not_pick")
			self.wndIcon.SetPosition(6, 2)
			self.wndIcon.LoadImage(PATH_ICONS + "%d.png" % (type))
			self.wndIcon.Show()
		
			self.wndTextLine = ui.TextLine()
			self.wndTextLine.SetParent(self.bg)
			self.wndTextLine.SetPosition(55, 5)
			self.wndTextLine.SetText(title + " (%d)" % (self.maxCount - self.count))
			self.wndTextLine.SetPackedFontColor(0xFFC6B38D)
			self.wndTextLine.Show()
	
			self.wndTextLine2 = ui.TextLine()
			self.wndTextLine2.SetParent(self.bg)
			self.wndTextLine2.SetPosition(55, 24)
			self.wndTextLine2.SetText(localeinfo.GUILD_RENEWAL_TEXT7.format(GetNameByTypeVnum(type, vnum)))
			self.wndTextLine2.Show()

			self.wndTextLine3 = ui.TextLine()
			self.wndTextLine3.SetParent(self.bg)
			self.wndTextLine3.SetPosition(250, 5)
			self.wndTextLine3.SetText(localeinfo.GUILD_RENEWAL_TEXT8.format(self.expReward))
			self.wndTextLine3.SetPackedFontColor(0xFF9F8C76)
			self.wndTextLine3.Show()

			self.wndTextLine4 = ui.TextLine()
			self.wndTextLine4.SetParent(self.bg)
			self.wndTextLine4.SetPosition(250, 5 + 17)
			self.wndTextLine4.SetText(localeinfo.GUILD_RENEWAL_TEXT9.format(self.pointReward))
			self.wndTextLine4.SetPackedFontColor(0xFF9F8C76)
			self.wndTextLine4.Show()

			self.bgGauge = ui.Window()
			self.bgGauge.SetParent(self)
			self.bgGauge.SetPosition(1, 41)
			
			self.bgGaugeFull = ui.MakeExpandedImageBox(self.bgGauge, PATH_ROOT+"slice/quest/" + "gauge_blue.png", 0, 2, "not_pick")

			self.bgGauge.SetSize(self.bgGaugeFull.GetWidth(), self.bgGaugeFull.GetHeight())
			self.bgGauge.Show()

			self.wndTextLine5 = ui.TextLine()
			self.wndTextLine5.SetParent(self.bg)
			self.wndTextLine5.SetPosition(380, 14)
			self.wndTextLine5.SetPackedFontColor(0xFF9F8C76)
			self.wndTextLine5.Show()

			self.UpdateGauge(self.count, self.maxCount)

		def GetInfoItem(self):
			return (self.title, self.type, self.vnum, self.count, self.maxCount)
		
		def SetItemToolTip(self, tooltipItem):
			self.tooltipItem = tooltipItem
		
		def OnRender(self):
			xList, yList = self.parent.GetGlobalPosition()
			width, height = self.parent.GetWidth(), self.parent.GetHeight()	
		
			listImage = [self.bg, self.wndIcon]
			for image in listImage:
				if image:
					self.SetClipRect(image, xList, yList, xList + width, yList + height)
			
			self.bgGaugeFull.SetClipRect(0.0, yList, -1.0 + float(self.percentActual) / float(self.percentTotal), yList + self.parent.GetHeight(), True)
			
			listText = [self.wndTextLine, self.wndTextLine2, self.wndTextLine3, self.wndTextLine4, self.wndTextLine5]
			for text in listText:
				if text:
					xText, yText = text.GetGlobalPosition()
					text.Hide() if yText < yList or yText + text.GetTextSize()[1] > yList + height else text.Show()

		def UpdateGauge(self, actual, total):
			if actual != total:
				self.wndTextLine5.SetText(localeinfo.GUILD_RENEWEL_TITLE_TYPE7)
			else:
				self.wndTextLine5.SetText(localeinfo.GUILD_RENEWEL_TITLE_TYPE8)

			self.count = actual
			self.percentActual = actual
			self.percentTotal = total
			
			self.wndTextLine.SetText(self.title + " (%d)" % (self.maxCount - self.count))
		
			if self.percentActual == self.percentTotal:
				self.bgGaugeFull.LoadImage(PATH_ROOT+"slice/quest/" + "gauge_gold.png")
			else:
				self.bgGaugeFull.LoadImage(PATH_ROOT+"slice/quest/" + "gauge_blue.png")
	
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

		def SetSelect(self):
			self.select = True
	
		def OverOutForce(self):
			self.select = False
		
		def __del__(self):
			ui.Window.__del__(self)
			self.Reinitialize()
			
		def Reinitialize(self):
			self.xBase = 0
			self.yBase = 0

			self.bg = None
			self.tooltipItem = None
		
		def SetParent(self, parent):
			ui.Window.SetParent(self, parent)
			self.parent = proxy(parent)

		def SetBasePosition(self, x, y):
			self.xBase = x
			self.yBase = y
			
		def GetBasePosition(self):
			return (self.xBase, self.yBase)

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

	def GetMission(self, index):
		if self.itemList:
			for itemH in self.itemList:
				if itemH.index == index:
					return itemH

		return None
	
	def AppendItem(self, category, mID, curCount, startTime, maxCount, type, vnum, expReward, pointReward):
		mission = self.GetMission(mID)
		if mission:
			mission.UpdateGauge(curCount, maxCount)
			return

		item = self.NewItem(category, mID, curCount, startTime, maxCount, type, vnum, expReward, pointReward, self)
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
	
		for item in self.itemList:
			item.Reinitialize()
			item.Hide()
			del item
		
		if bIsRefresh == False:
			self.tooltipItem = None
		self.itemList = []

class GuildMissionWindow(ui.ScriptWindow):
	def __init__(self):
		self.bLoaded = False
		self.tooltipItem = None
		self.ListBoxItem = None
		self.startTimeDict = {}
		self.lastRequestTimeSec = 0
		
		self.selectedCategoryMission = 0
		
		ui.ScriptWindow.__init__(self)
		self.LoadWindow()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.ClearDictionary()
		
		self.categories = []
		
		if self.ListBoxItem:
			self.ListBoxItem.Clear()
		self.ListBoxItem = None
		
		self.tooltipItem = None

	def SetItemToolTip(self, itemTooltip):
		self.tooltipItem = itemTooltip

	def Show(self):
		self.SetTop()
		ui.ScriptWindow.Show(self)

		self.ListBoxItem.Clear()
		
		self.lastRequestTimeSec = CACHE_TIMESEC_INFO + app.GetGlobalTimeStamp()
		net.SendChatPacket("/guild_renew mission")
		
		# for x in xrange(10):
			# self.RecvMission(x + 111, x+3, 0, 155, 1, 101 + x, 1, 1, 1)

	def LoadWindow(self):
		if self.bLoaded == True:
			return
			
		self.bLoaded = True

		self.AddFlag("movable")
		self.AddFlag("float")

		self.Board = ui.BoardWithTitleBar()
		self.Board.SetParent(self)
		self.Board.SetSize(492, 285 + 35 + 23)
		self.Board.SetTitleName(localeinfo.GUILD_RENEWEL_TITLE_TYPE9)
		self.Board.SetCloseEvent(ui.__mem_func__(self.Close))
		self.Board.Show()
		
		self.SetSize(self.Board.GetWidth(), self.Board.GetHeight())
		
		self.LoadMiddleBoard()
			
		self.ListBoxItem.SetItemToolTip(self.tooltipItem)
		self.SetCenterPosition()

	def LoadMiddleBoard(self):
		self.board_Base = ui.BoxedBoard()
		self.board_Base.SetParent(self.Board)
		self.board_Base.SetPosition(8, 90 + 25 - 55)
		self.board_Base.SetSize(475, 218 + 55)
		self.board_Base.Show()	
		
		self.categories = []
		
		self.wndInfResetTime = ui.MakeTextLineNew(self.board_Base, 315, -20, "")
		
		btnCategory1 = ui.MakeRadioButton(self, 8, 91 - 55, localeinfo.GUILD_RENEWEL_TITLE_TYPE10, PATH_ROOT+"slice/quest/" , "btn_l_0.png", "btn_l_1.png", "btn_l_1.png")
		btnCategory1.category = 0
		btnCategory1.Down()
		
		self.categories.append(btnCategory1)
		
		btnCategory2 = ui.MakeRadioButton(self, 8 + 84, 91 - 55, localeinfo.GUILD_RENEWEL_TITLE_TYPE11, PATH_ROOT+"slice/quest/" , "btn_m_0.png", "btn_m_1.png", "btn_m_1.png")
		btnCategory2.category = 1
		self.categories.append(btnCategory2)

		for i, btnCat in enumerate(self.categories):
			btnCat.SetEvent(ui.__mem_func__(self.ClickCategoryMission), i)
	
		# Mission List Code
		self.ScrollBarItem = ui.NewScrollBar()
		self.ScrollBarItem.SetParent(self.board_Base)
		self.ScrollBarItem.SetScrollBarSize(self.board_Base.GetHeight() - 6)
		self.ScrollBarItem.SetPosition(self.board_Base.GetWidth() - 9, 3)
		self.ScrollBarItem.Show()

		self.ListBoxItem = ListBox()
		self.ListBoxItem.SetParent(self.board_Base)
		self.ListBoxItem.SetScrollBar(self.ScrollBarItem)
		self.ListBoxItem.SetSize(self.board_Base.GetWidth() - self.ScrollBarItem.GetWidth() - 2, self.board_Base.GetHeight() - 4)
		self.ListBoxItem.SetPosition(2, 2)
		self.ListBoxItem.Show()

	def OnUpdate(self):
		if self.lastRequestTimeSec < app.GetGlobalTimeStamp():
			self.lastRequestTimeSec = CACHE_TIMESEC_INFO + app.GetGlobalTimeStamp()
			net.SendChatPacket("/guild_mission")

		if self.startTimeDict.has_key(self.selectedCategoryMission):
			startTime = self.startTimeDict[self.selectedCategoryMission][0]
			bDayResetAt = self.startTimeDict[self.selectedCategoryMission][1]
			now = app.GetGlobalTimeStamp()

			leftSec = max(0, bDayResetAt * 86400 - (now - startTime))
			
			self.wndInfResetTime.SetText(localeinfo.GUILD_RENEWEL_TITLE_TYPE12.format(localeinfo.SecondToDHM(leftSec)))
			self.wndInfResetTime.Show()
		else:
			self.wndInfResetTime.Hide()

	def Close(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
	
	# Recv Packets
	def RecvMission(self, mID, curCount, startTime, maxCount, type, vnum, expReward, pointReward, bDayResetAt):
		category = 0
		if bDayResetAt != 1:
			category = 1
		
		self.startTimeDict[category] = (startTime, bDayResetAt)
		self.ListBoxItem.AppendItem(category, mID, curCount, startTime, maxCount, type, vnum, expReward, pointReward)
		
	def OnMouseWheel(self, nLen):
		if nLen > 0:
			self.ScrollBarItem.OnUp()
		else:
			self.ScrollBarItem.OnDown()
			
		return True
	
	def ClickCategoryMission(self, index):
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
