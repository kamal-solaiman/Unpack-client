# coding: latin_1

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import net

import ui
import localeinfo
import uiscriptlocale
import datetime
import eventMgr
import uitooltip
import time
import weakref
import item
import wndMgr

def GetEventItemName(eventType, itemVnum):
	if not getattr(app, "ENABLE_STONE_MONSTER_DROP_EVENTS", 0):
		return ""
	if eventType not in (eventMgr.EVENT_TYPE_STONE_DROP, eventMgr.EVENT_TYPE_MONSTER_DROP, eventMgr.EVENT_TYPE_BOSS_DROP):
		return ""
	if itemVnum <= 0:
		return ""
	try:
		item.SelectItem(int(itemVnum))
		return item.GetItemName()
	except:
		return ""

SKILL_SLOT_ENABLE	= "d:/ymir work/ui/pet/skill_button/skill_enable_button.sub"
CALENDAR_LENGHT		= 7

SATURDAY			= 6
SUNDAY				= 7

DEFAULT_DAY			= 1
DEFAULT_WEEK		= 1
WEEK_DAY_COUNT		= 7

class EventRewardList(ui.ScriptWindow):
	def __init__(self, OverviewWindow):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__LoadScript()
		self.tooltipItem = uitooltip.ItemToolTip()
		self.eventType = 0
		self.wndOverviewEvent = OverviewWindow
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)
		self.tooltipItem = None
		self.eventType = 0
		
	def __LoadScript(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/EventRewardListWindow.py")

			self.eventButton = self.GetChild("EventButton")
			self.rewardItemSlot = self.GetChild("reward_item_slot")
			self.eventDurationText = self.GetChild("EventDuration")
			
			self.eventButton.SetEvent(ui.__mem_func__(self.OpenEventDescription))
			self.rewardItemSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
			self.rewardItemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		except:
			import exception
			exception.Abort("EventRewardList.__LoadScript.UIScript/EventRewardListWindow.py")
	
	def SetEventText(self, text):
		self.eventDurationText.SetText(text)
		
	def SetEventButtonText(self, text):
		self.eventButton.SetText(text)
		
	def SetRewardItemSlot(self, event):
		self.eventType = event
		
		for i in range(eventMgr.REWARD_MAX_NUM):
			(itemVnum, itemCount) = eventMgr.GetEventRewardData(event, i)
			
			if itemVnum > 0 and itemCount > 0:
				self.rewardItemSlot.SetItemSlot(i, itemVnum, itemCount)
			else:
				self.rewardItemSlot.ClearSlot(i)
				self.rewardItemSlot.SetCoverButton(i, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, False, False)
				self.rewardItemSlot.SetAlwaysRenderCoverButton(i)
				
	def OpenEventDescription(self):
		type = self.eventType
		
		if type == eventMgr.EVENT_TYPE_BOSS:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("boss_event")
			
		elif type == eventMgr.EVENT_TYPE_FISHING:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("fishing_event")
			
		elif type == eventMgr.EVENT_TYPE_GOLD_FROG:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("golden_frog_event")
			
		elif type == eventMgr.EVENT_TYPE_HEXEGONAL_CHEST:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("hexegonal_drop_event")
			
		elif type == eventMgr.EVENT_TYPE_HIDE_AND_SEEK:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("hide_seek_event")
			
		elif type == eventMgr.EVENT_TYPE_METIN:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("metin_event")
			
		elif type == eventMgr.EVENT_TYPE_MINING:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("mining_event")
			
		elif type == eventMgr.EVENT_TYPE_MOONLIGHT:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("moonlight_drop_event")
			
		elif type == eventMgr.EVENT_TYPE_OX:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("oxevent_manager")
			
		elif type == eventMgr.EVENT_TYPE_TANAKA:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("event_tanaka")
			
		elif type == eventMgr.EVENT_TYPE_OKAY_CARD:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("okay_drop_event")
			
		elif type == eventMgr.EVENT_TYPE_CATCH_KING:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("catch_drop_event")
			
		elif type == eventMgr.EVENT_TYPE_CUSTOMS:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("customs_drop_event")
			
		elif type == eventMgr.EVENT_TYPE_MOUNTS:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("mounts_drop_event")

		elif type == eventMgr.EVENT_TYPE_GOLD:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("gold_event")
			
		elif type == eventMgr.EVENT_TYPE_SIEGE_WAR:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("siege_war_event")
			
		elif type == eventMgr.EVENT_TYPE_KINGDOM_WAR:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("kingdom_war_event")

		elif type == eventMgr.EVENT_TYPE_ATT_MONSTER:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("att_monster_event")

		elif type == eventMgr.EVENT_TYPE_ATT_STONE:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("stone_att_event")

		elif type == eventMgr.EVENT_TYPE_ATT_BOSS:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("boss_att_event")
		elif app.USE_DROP_EVENT and\
			type == eventMgr.EVENT_TYPE_DROP:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("drop_event")
		elif app.USE_FISH_CHEST_EVENT and\
			type == eventMgr.EVENT_TYPE_FISH_CHEST:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("fish_event_chest")

		elif type == eventMgr.EVENT_TYPE_FISHING_CHEST:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("fishing_event_chest")

		elif type == eventMgr.EVENT_TYPE_HORN_CHEST:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("horn_event_chest")

		elif type == eventMgr.EVENT_TYPE_DOUBLE_STONES:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("event_double_stone_loot")
			
		elif type == eventMgr.EVENT_TYPE_DOUBLE_BOSSES:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("event_double_boss_loot")
			
		elif type == eventMgr.EVENT_TYPE_FISHING_MYST:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("fishin_myst_event")
			
		elif type == eventMgr.EVENT_TYPE_PET_EXP:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("petexp_event")

		elif type == eventMgr.EVENT_TYPE_SUPER_METIN:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("event_super_metin")

		elif type == eventMgr.EVENT_TYPE_GOLD_CHEST:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("event_gold_chest")

		elif type == eventMgr.EVENT_TYPE_BEACH_EVENT:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("event_beach")

		elif type == eventMgr.EVENT_TYPE_METIN_BOSS:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("event_metin_boss")

		elif type == eventMgr.EVENT_TYPE_MAGIC_EGG:
			self.wndOverviewEvent.Close()
			net.SendRequestEventQuest("event_magic_egg")



	def OverOutItem(self):
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()
			
	def OverInItem(self, slot):
		if None != self.tooltipItem:
			(itemVnum, itemCount) = eventMgr.GetEventRewardData(self.eventType, slot)
			if itemVnum:
				self.tooltipItem.ClearToolTip()
				self.tooltipItem.AddItemData(itemVnum, 0)

class KingdomWarScoreBoard(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__LoadScript()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)
		
	def __LoadScript(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/KingdomWarScoreBoard.py")

			self.ShinsooScoreText = self.GetChild("ShinsooScoreText")
			self.ChunjoScoreText = self.GetChild("ChunjoScoreText")
			self.JinnoScoreText = self.GetChild("JinnoScoreText")

		except:
			import exception
			exception.Abort("KingdomWarScoreBoard.__LoadScript.UIScript/KingdomWarScoreBoard.py")
			
	def UpdateScore(self, score_shinsoo, score_chunjo, score_jinno):
		self.ShinsooScoreText.SetText(localeinfo.EMPIRE_A + (":\t%d" % score_shinsoo))
		self.ChunjoScoreText.SetText(localeinfo.EMPIRE_B + (":\t%d" % score_chunjo))
		self.JinnoScoreText.SetText(localeinfo.EMPIRE_C + (":\t%d" % score_jinno))

class EventOverview(ui.ScriptWindow):
	DAY_NAME_DICT = {
		0 : localeinfo.TOOLTIP_EVENT_MONDAY,
		1 : localeinfo.TOOLTIP_EVENT_TUESDAY,
		2 : localeinfo.TOOLTIP_EVENT_WEDNESDAY,
		3 : localeinfo.TOOLTIP_EVENT_THURSDAY,
		4 : localeinfo.TOOLTIP_EVENT_FRIDAY,
		5 : localeinfo.TOOLTIP_EVENT_SATURDAY,
		6 : localeinfo.TOOLTIP_EVENT_SUNDAY,
	}
	
	EVENT_NAME_DICT = {
		eventMgr.EVENT_TYPE_EXPERIENCE : localeinfo.TOOLTIP_EVENT_TYPE_EXPERIENCE,
		eventMgr.EVENT_TYPE_ITEM_DROP : localeinfo.TOOLTIP_EVENT_TYPE_ITEM_DROP,
		eventMgr.EVENT_TYPE_BOSS : localeinfo.TOOLTIP_EVENT_TYPE_BOSS,
		eventMgr.EVENT_TYPE_METIN : localeinfo.TOOLTIP_EVENT_TYPE_METIN,
		eventMgr.EVENT_TYPE_MINING : localeinfo.TOOLTIP_EVENT_TYPE_MINING,
		eventMgr.EVENT_TYPE_GOLD_FROG : localeinfo.TOOLTIP_EVENT_TYPE_GOLD_FROG,
		eventMgr.EVENT_TYPE_MOONLIGHT : localeinfo.TOOLTIP_EVENT_TYPE_MOONLIGHT,
		eventMgr.EVENT_TYPE_HEXEGONAL_CHEST : localeinfo.TOOLTIP_EVENT_TYPE_HEXEGONAL_CHEST,
		eventMgr.EVENT_TYPE_FISHING : localeinfo.TOOLTIP_EVENT_TYPE_FISHING,
		eventMgr.EVENT_TYPE_HIDE_AND_SEEK : localeinfo.TOOLTIP_EVENT_TYPE_HIDE_AND_SEEK,
		eventMgr.EVENT_TYPE_OX : localeinfo.TOOLTIP_EVENT_TYPE_OX,
		eventMgr.EVENT_TYPE_TANAKA : localeinfo.TOOLTIP_EVENT_TYPE_TANAKA,
		eventMgr.EVENT_TYPE_OKAY_CARD : localeinfo.TOOLTIP_EVENT_TYPE_OKAY_CARD,
		eventMgr.EVENT_TYPE_CATCH_KING : localeinfo.TOOLTIP_EVENT_TYPE_CATCH_KING,
		eventMgr.EVENT_TYPE_CUSTOMS : localeinfo.TOOLTIP_EVENT_TYPE_CUSTOMS,
		eventMgr.EVENT_TYPE_MOUNTS : localeinfo.TOOLTIP_EVENT_TYPE_MOUNTS,
		eventMgr.EVENT_TYPE_GOLD : localeinfo.TOOLTIP_EVENT_TYPE_GOLD,
		eventMgr.EVENT_TYPE_SIEGE_WAR : localeinfo.TOOLTIP_EVENT_TYPE_SIEGE_WAR,
		eventMgr.EVENT_TYPE_KINGDOM_WAR : localeinfo.TOOLTIP_EVENT_TYPE_KINGDOM_WAR,
		eventMgr.EVENT_TYPE_ATT_MONSTER : localeinfo.TOOLTIP_EVENT_TYPE_ATT_MONSTER,
		eventMgr.EVENT_TYPE_ATT_STONE : localeinfo.TOOLTIP_EVENT_TYPE_ATT_STONE,
		eventMgr.EVENT_TYPE_ATT_BOSS : localeinfo.TOOLTIP_EVENT_TYPE_ATT_BOSS,
	}

	if app.USE_DROP_EVENT:
		EVENT_NAME_DICT[eventMgr.EVENT_TYPE_DROP] = localeinfo.TOOLTIP_EVENT_TYPE_DROP

	if app.USE_FISH_CHEST_EVENT:
		EVENT_NAME_DICT[eventMgr.EVENT_TYPE_FISH_CHEST] = localeinfo.TOOLTIP_EVENT_TYPE_FISH_CHEST

	EVENT_NAME_DICT[eventMgr.EVENT_TYPE_FISHING_CHEST] = localeinfo.TOOLTIP_EVENT_TYPE_FISHING_CHEST
	EVENT_NAME_DICT[eventMgr.EVENT_TYPE_HORN_CHEST] = localeinfo.TOOLTIP_EVENT_TYPE_HORN_CHEST
	EVENT_NAME_DICT[eventMgr.EVENT_TYPE_DOUBLE_STONES] = localeinfo.TOOLTIP_EVENT_TYPE_DOUBLE_STONES
	EVENT_NAME_DICT[eventMgr.EVENT_TYPE_DOUBLE_BOSSES] = localeinfo.TOOLTIP_EVENT_TYPE_DOUBLE_BOSSES
	EVENT_NAME_DICT[eventMgr.EVENT_TYPE_FISHING_MYST] = localeinfo.TOOLTIP_EVENT_TYPE_FISHING_MYST
	EVENT_NAME_DICT[eventMgr.EVENT_TYPE_PET_EXP] = localeinfo.TOOLTIP_EVENT_TYPE_PET_EXP
	EVENT_NAME_DICT[eventMgr.EVENT_TYPE_SUPER_METIN] = localeinfo.TOOLTIP_EVENT_TYPE_SUPER_METIN
	EVENT_NAME_DICT[eventMgr.EVENT_TYPE_GOLD_CHEST] = localeinfo.TOOLTIP_EVENT_TYPE_GOLD_CHEST
	EVENT_NAME_DICT[eventMgr.EVENT_TYPE_MAGIC_EGG] = localeinfo.TOOLTIP_EVENT_TYPE_MAGIC_EGG
	EVENT_NAME_DICT[eventMgr.EVENT_TYPE_BEACH_EVENT] = localeinfo.TOOLTIP_EVENT_TYPE_BEACH_EVENT
	EVENT_NAME_DICT[eventMgr.EVENT_TYPE_METIN_BOSS] = localeinfo.TOOLTIP_EVENT_TYPE_METIN_BOSS

	if getattr(app, "ENABLE_STONE_MONSTER_DROP_EVENTS", 0):
		EVENT_NAME_DICT[eventMgr.EVENT_TYPE_STONE_DROP] = getattr(localeinfo, "TOOLTIP_EVENT_TYPE_STONE_DROP", "Metin Drop Event")
		EVENT_NAME_DICT[eventMgr.EVENT_TYPE_MONSTER_DROP] = getattr(localeinfo, "TOOLTIP_EVENT_TYPE_MONSTER_DROP", "Monster Drop Event")
		EVENT_NAME_DICT[eventMgr.EVENT_TYPE_BOSS_DROP] = getattr(localeinfo, "TOOLTIP_EVENT_TYPE_BOSS_DROP", "Boss Drop Event")

	if getattr(app, "ENABLE_STONE_CAP_EVENT", 0):
		EVENT_NAME_DICT[eventMgr.EVENT_TYPE_STONE_CAP] = getattr(localeinfo, "TOOLTIP_EVENT_TYPE_STONE_CAP", "Metin Cap Raise")

	TILE_SIZE = 75
	TILE_GAP = 9
	TILES_PER_ROW = 4
	TILES_ORIGIN_X = 51
	ROW_1_Y = 42
	DAY_BG_H = 38
	DAY_ROW_Y = 2
	DAY_NUMBER_SCALE = 0.6
	# Day badges sit in the top band, just under the titlebar (container-relative Y). Tune this.
	DAY_NUMBER_TOP_Y = 0
	# Horizontal nudge to match the tile art's visual center (same -9 the event icon uses).
	DAY_NUMBER_X_OFF = -9
	ICON_SCALE = 0.85
	DAYS_PER_PAGE = 4
	ICON_ROTATE_SEC = 5
	EVENT_ICON_PATH = "d:/ymir work/ui/game/event_alert/event_id/"
	TILE_IMG_PATH = "d:/ymir work/ui/event_rework/"

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.toolTip = uitooltip.ToolTip()
		self.dayTip = EventDayToolTip()
		self.weekendDict = {}
		self.weekDict = {}
		self.dayTiles = []
		self.tileIconSets = []
		self.iconRotateTime = 0
		self.updateTime = 0

		import pack
		self.availableEventIcons = {}
		for k in self.EVENT_NAME_DICT.keys():
			filePath = self.EVENT_ICON_PATH + str(k) + "_active.png"
			if pack.Exist(filePath):
				self.availableEventIcons[k] = filePath

		self.__BuildCalendar()
		self.calendarWeek = self.__GetCurrentMonthWeek()

		self.__LoadScript()

		self.wndActivatable = None
		if app.ENABLE_PLAYER_EVENT_ACTIVATION:
			self.wndActivatable = ActivatableEventWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadScript(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/EventOverviewWindow.py")

			self.board = self.GetChild("board")
			self.tileContainer = self.GetChild("tile_container")

			self.GetChild("Event_Title_Bar").SetCloseEvent(ui.__mem_func__(self.Close))
			self.GetChild("prev_button").SetEvent(ui.__mem_func__(self.__PrevCalendarPage))
			self.GetChild("next_button").SetEvent(ui.__mem_func__(self.__NextCalendarPage))
			if localeinfo.IsARABIC():
				self.GetChild("prev_button").LeftRightReverse()
				self.GetChild("next_button").LeftRightReverse()

			self.__SetCalendarWeek(self.calendarWeek)
			self.wndKingdomWarScoreBoard = KingdomWarScoreBoard()
			self.wndKingdomWarScoreBoard.Hide()
		except:
			import exception
			exception.Abort("EventOverview.__LoadScript.UIScript/EventOverviewWindow.py")
			
	def __BuildCalendar(self):
		monthDayCount = self.__GetCurrentMonthDayCount()
		month = self.__GetCurrentMonth()
		year = self.__GetCurrentYear()
		
		weekDays = []
		weekCount = 1
		
		#Weekends Dict
		for day in range(1, monthDayCount + 1):
			weekDay = datetime.date(year, month, day).isoweekday() 
			
			isWeekend = False
			if weekDay == SATURDAY or weekDay == SUNDAY:
				isWeekend = True
			
			self.weekendDict[day] = isWeekend
			
			weekDays.append(day)

			#Add week to the dict if it is the last day of week/month
			if len(weekDays) == self.DAYS_PER_PAGE or (day == monthDayCount):
				self.weekDict[weekCount] = weekDays

				#Prepare week variable/week list for the next week
				weekCount += 1
				weekDays = []

	def __ClearTiles(self):
		for widget in self.dayTiles:
			widget.Hide()
		self.dayTiles = []
		self.tileIconSets = []

	def Destroy(self):
		self.__ClearTiles()
		self.ClearDictionary()
		self.toolTip = None
		if self.dayTip:
			self.dayTip.Clear()
			self.dayTip = None
		if self.wndKingdomWarScoreBoard:
			del self.wndKingdomWarScoreBoard
			self.wndKingdomWarScoreBoard = None
		if self.wndActivatable:
			self.wndActivatable.Destroy()
			del self.wndActivatable
			self.wndActivatable = None

	def KingdomWarScore(self, score_shinsoo, score_chunjo, score_jinno):
		if not self.wndKingdomWarScoreBoard:
			self.wndKingdomWarScoreBoard = KingdomWarScoreBoard()
			
		if not self.wndKingdomWarScoreBoard.IsShow():
			self.wndKingdomWarScoreBoard.Show()
			
		self.wndKingdomWarScoreBoard.UpdateScore(score_shinsoo, score_chunjo, score_jinno)

	def Open(self, x, y):
		if x != -1 and y != -1:
			self.SetPosition(x - self.GetWidth() - 3, y)

		if not app.USE_EVENT_MANAGER_EXPANDED:
			if not eventMgr.GetRequestEventData():
				self.ClearActiveEvents()

				# Events on server have a range of 0-11
				month = self.__GetCurrentMonth() - 1
				net.SendRequestEventData(month)
				return

		self.RefreshActiveEvent()
		#self.SetCenterPosition()
		self.SetTop()
		self.Show()

		# Open the activatable-events side panel only when something can be activated today.
		if self.wndActivatable:
			self.wndActivatable.Open(self.GetLeft(), self.GetTop())

	def ClearActiveEvents(self):
		self.__ClearTiles()

	def Close(self):
		self.Hide()
		if self.wndActivatable:
			self.wndActivatable.Close()
		
	def OnPressEscapeKey(self):
		self.Close()
		return True
		
	TOOLTIP_TIME_COLOR = 0xff16a085
	TOOLTIP_ACTIVE_COLOR = 0xff5ADE5A
	TOOLTIP_FINISHED_COLOR = 0xff888888

	# Percent-style events whose value0 is shown next to the name (e.g. "... +5%").
	__PERCENT_EVENT_TYPES = (eventMgr.EVENT_TYPE_EXPERIENCE, eventMgr.EVENT_TYPE_ITEM_DROP,
						eventMgr.EVENT_TYPE_ATT_MONSTER, eventMgr.EVENT_TYPE_ATT_STONE,
						eventMgr.EVENT_TYPE_ATT_BOSS, eventMgr.EVENT_TYPE_GOLD,
						eventMgr.EVENT_TYPE_PET_EXP)

	def SetEventTooltip(self, day, eventCount):
		import time
		now = int(time.time())
		isAr = localeinfo.IsARABIC()
		isToday = (day == self.__GetCurrentDay())

		blocks = []
		dateStr = "%04d-%02d-%02d" % (self.__GetCurrentYear(), self.__GetCurrentMonth(), day)
		blocks.append(("title", localeinfo.EVENT_TIP_DATE % dateStr, self.dayTip.C_TITLE))

		# Current-day-only: the activatable-events status block (matches screenshot 1).
		statusShown = False
		if app.ENABLE_PLAYER_EVENT_ACTIVATION and isToday:
			actLines = []
			for i in range(eventCount):
				(eid, etype, start, end, value0, value1, completed) = eventMgr.GetEventData(i, day)
				if etype not in self.EVENT_NAME_DICT:
					continue
				(act, pEnd, used, durMin) = eventMgr.GetEventActivation(i, day)
				if not act:
					continue
				name = self.EVENT_NAME_DICT[etype]
				if pEnd > now:
					actLines.append(("%s - %s" % (name, localeinfo.EVENT_TIP_ACT_INPROGRESS % localeinfo.SecondToDHMS(pEnd - now)), self.dayTip.C_ACTIVE))
				elif used:
					actLines.append(("%s - %s" % (name, localeinfo.EVENT_TIP_ACT_USED), self.dayTip.C_USED))
				else:
					actLines.append(("%s - %s" % (name, localeinfo.EVENT_TIP_CAN_ACTIVATE), self.dayTip.C_CANACT))
			if actLines:
				blocks.append(("text", localeinfo.EVENT_TIP_ACTIVATABLE, self.dayTip.C_HEAD_TXT))
				for (txt, col) in actLines:
					blocks.append(("text", txt, col))
				blocks.append(("space", 5))
				statusShown = True

		# Activatable events (Duration) + normal events split by status (Start / End).
		# Each entry is (start, row) so we can sort chronologically (earliest first).
		activatable = []
		inprogress = []
		upcoming = []
		expired = []
		for i in range(eventCount):
			(eid, etype, start, end, value0, value1, completed) = eventMgr.GetEventData(i, day)
			if etype not in self.EVENT_NAME_DICT:
				continue
			name = self.EVENT_NAME_DICT[etype]
			evtItemName = GetEventItemName(etype, value1)
			if evtItemName:
				name = "%s : %s" % (name, evtItemName)
			if etype in self.__PERCENT_EVENT_TYPES:
				name = "%s +%d%%" % (name, value0)

			act = 0
			if app.ENABLE_PLAYER_EVENT_ACTIVATION:
				(act, pEnd, used, durMin) = eventMgr.GetEventActivation(i, day)

			if act:
				# Activatable: how long it runs (the scheduled length).
				activatable.append((start, [name, localeinfo.SecondToDHMS(max(0, end - start))]))
				continue

			# Normal: when it starts and when it ends, bucketed by status.
			row = [name,
					datetime.datetime.fromtimestamp(start).strftime("%H:%M"),
					datetime.datetime.fromtimestamp(end).strftime("%H:%M")]
			if completed or end <= now:
				expired.append((start, row))
			elif start <= now:
				inprogress.append((start, row))
			else:
				upcoming.append((start, row))

		# Earliest first.
		for lst in (activatable, inprogress, upcoming, expired):
			lst.sort(key=lambda t: t[0])

		def addTable(label, labelColor, headers, widths, entries, rowColor):
			if not entries:
				return
			rows = [e[1] for e in entries]
			h, w, r = headers, widths, rows
			if isAr:
				h = headers[::-1]
				w = widths[::-1]
				r = [row[::-1] for row in rows]
			if label:
				blocks.append(("text", label, labelColor))
			blocks.append(("table", h, w, r, [rowColor] * len(r)))
			blocks.append(("space", 3))

		SE_COLS = [localeinfo.EVENT_TIP_COL_EVENT, localeinfo.EVENT_TIP_COL_START, localeinfo.EVENT_TIP_COL_END]
		SE_W = [236, 60, 60]

		# Activatable (Duration). Label suppressed on the current day (status block titles it).
		actLabel = None if statusShown else localeinfo.EVENT_TIP_ACTIVATABLE
		addTable(actLabel, self.dayTip.C_ACTIVE,
				[localeinfo.EVENT_TIP_COL_EVENT, localeinfo.EVENT_TIP_COL_DURATION], [256, 100],
				activatable, self.dayTip.C_CELL_TXT)
		# In progress (green), Upcoming (gold), Expired (red).
		addTable(localeinfo.EVENT_TIP_INPROGRESS, self.dayTip.C_ACTIVE, SE_COLS, SE_W, inprogress, self.dayTip.C_ACTIVE)
		addTable(localeinfo.EVENT_TIP_UPCOMING, self.dayTip.C_UPCOMING, SE_COLS, SE_W, upcoming, self.dayTip.C_CELL_TXT)
		addTable(localeinfo.EVENT_TIP_EXPIRED, self.dayTip.C_EXPIRED, SE_COLS, SE_W, expired, self.dayTip.C_EXPIRED)

		if len(blocks) <= 1:
			self.dayTip.Hide()
			return False

		self.dayTip.SetParent(self)
		self.dayTip.Build(blocks)
		self.dayTip.SetWindowHorizontalAlignCenter()
		self.dayTip.SetPosition(0, self.GetHeight() + 5)
		self.dayTip.SetTop()
		return True

	def ShowEventTooltip(self, dayNum):
		eventCount = eventMgr.GetDayEventCount(dayNum)
		if eventCount:
			if self.SetEventTooltip(dayNum, eventCount):
				self.dayTip.Show()

	def HideEventTooltip(self):
		if self.dayTip:
			self.dayTip.Clear()
			self.dayTip.Hide()

	def __PrevCalendarPage(self):
		self.__SetCalendarWeek(self.calendarWeek - 1)
		
	def __NextCalendarPage(self):
		self.__SetCalendarWeek(self.calendarWeek + 1)
		
	def __SetCalendarWeek(self, week):
		if week > len(self.weekDict):
			return

		if week < DEFAULT_WEEK:
			return

		self.__ClearTiles()
		currentDay = self.__GetCurrentDay()

		tileCount = len(self.weekDict[week])
		for idx, day in enumerate(self.weekDict[week]):
			if localeinfo.IsARABIC():
				tileX = self.TILES_ORIGIN_X + (tileCount - 1 - idx) * (self.TILE_SIZE + self.TILE_GAP)
			else:
				tileX = self.TILES_ORIGIN_X + idx * (self.TILE_SIZE + self.TILE_GAP)
			tileY = self.ROW_1_Y

			eventCount = eventMgr.GetDayEventCount(day)
			if day == currentDay:
				tileImgPath = self.TILE_IMG_PATH + "day_current.png"
			elif eventCount > 0:
				tileImgPath = self.TILE_IMG_PATH + "day.png"
			else:
				tileImgPath = self.TILE_IMG_PATH + "day_inactive.png"

			tile = ui.ExpandedImageBox()
			tile.SetParent(self.tileContainer)
			tile.LoadImage(tileImgPath)
			tile.SetPosition(tileX, tileY)
			tile.OnMouseOverIn = lambda d=day, r=weakref.proxy(self): r.ShowEventTooltip(d)
			tile.OnMouseOverOut = lambda r=weakref.proxy(self): r.HideEventTooltip()
			tile.Show()
			self.dayTiles.append(tile)

			if self.weekendDict[day]:
				dayImgPath = "d:/ymir work/ui/calendar/calendar_weekend_day%d.sub" % day
			else:
				dayImgPath = "d:/ymir work/ui/calendar/calendar_work_day%d.sub" % day

			dayNumImg = ui.ExpandedImageBox()
			dayNumImg.SetParent(self.tileContainer)
			dayNumImg.AddFlag("not_pick")
			dayNumImg.LoadImage(dayImgPath)
			dayNumImg.SetScale(self.DAY_NUMBER_SCALE, self.DAY_NUMBER_SCALE)
			numWidth = int(dayNumImg.GetWidth() * self.DAY_NUMBER_SCALE)
			numHeight = int(dayNumImg.GetHeight() * self.DAY_NUMBER_SCALE)
			dayNumImg.SetPosition(tileX + (self.TILE_SIZE - numWidth) / 2 + self.DAY_NUMBER_X_OFF, self.DAY_NUMBER_TOP_Y)
			dayNumImg.Show()
			self.dayTiles.append(dayNumImg)

			if eventCount > 0:
				iconSet = {"icons": [], "idx": 0}
				seenTypes = {}
				for eventI in range(eventCount):
					(evId, evType, start, end, value0, value1, completed) = eventMgr.GetEventData(eventI, day)

					if evType in seenTypes:
						continue
					seenTypes[evType] = True

					if evType not in self.availableEventIcons:
						continue

					icon = ui.ExpandedImageBox()
					icon.SetParent(tile)
					icon.AddFlag("not_pick")
					icon.LoadImage(self.availableEventIcons[evType])
					icon.SetScale(self.ICON_SCALE, self.ICON_SCALE)

					iconW = int(icon.GetWidth() * self.ICON_SCALE)
					iconH = int(icon.GetHeight() * self.ICON_SCALE)
					icon.SetPosition(((self.TILE_SIZE - iconW) / 2) - 9, (self.TILE_SIZE - iconH) / 2 - 8)
					icon.Hide()
					iconSet["icons"].append(icon)
					self.dayTiles.append(icon)

				if iconSet["icons"]:
					iconSet["icons"][0].Show()
					self.tileIconSets.append(iconSet)

		self.calendarWeek = week

	def RefreshActiveEvent(self):
		self.__SetCalendarWeek(self.calendarWeek)

	def OnUpdate(self):
		currentTime = app.GetTime()

		if currentTime >= self.iconRotateTime:
			self.iconRotateTime = currentTime + self.ICON_ROTATE_SEC
			for iconSet in self.tileIconSets:
				icons = iconSet["icons"]
				if len(icons) <= 1:
					continue
				icons[iconSet["idx"]].Hide()
				iconSet["idx"] = (iconSet["idx"] + 1) % len(icons)
				icons[iconSet["idx"]].Show()

		if self.updateTime < currentTime:
			if self.IsShow():
				self.RefreshActiveEvent()
				self.updateTime = currentTime + 30

		if self.wndActivatable:
			self.wndActivatable.TickRows()
			# Keep the activatable side panel docked to the left of the main panel as it moves.
			if self.wndActivatable.IsShow() and self.IsShow():
				self.wndActivatable.SetPosition(self.GetLeft() - self.wndActivatable.GetWidth() - 5, self.GetTop())

	def __GetCurrentDay(self):
		return datetime.date.today().day
		
	def __GetCurrentMonthWeek(self):
		currentDay = datetime.date.today().day
		for (key, weekList) in self.weekDict.items():
			if currentDay in weekList:
				return key
				
		return DEFAULT_WEEK

	def __GetCurrentMonthDayCount(self):
#		import calendar
#		time = datetime.date.today()
#		return calendar.monthrange(time.year, time.month)[1]
#		
		time = datetime.date.today()
		
		first_of_month = datetime.datetime(time.year, time.month, 1)
		next_month_date = first_of_month + datetime.timedelta(days=32)
		new_dt = datetime.datetime(next_month_date.year, next_month_date.month, 1)
		
		dt = new_dt - datetime.timedelta(days=1)
		
		return dt.day

	def __GetCurrentMonth(self):
		return datetime.date.today().month
		
	def __GetCurrentYear(self):
		return datetime.date.today().year

class EventDayToolTip(ui.ThinBoard):
	WIDTH		= 380
	PAD			= 12
	HEAD_H		= 18
	ROW_H		= 18
	LINE_H		= 17

	C_LINE		= 0xff000000
	C_HEAD_BG	= 0xff1c1c1c
	C_ROW_BG	= 0x99000000
	C_HEAD_TXT	= 0xffffd300
	C_CELL_TXT	= 0xffcfcfcf
	C_TITLE		= 0xfff2e6c1
	C_ACTIVE	= 0xff5ade5a
	C_UPCOMING	= 0xffffc700
	C_ALLDAY	= 0xff8fd3ff
	C_CANACT	= 0xffffffff
	C_USED		= 0xffc86464
	C_EXPIRED	= 0xffd35454

	def __init__(self):
		ui.ThinBoard.__init__(self, "TOP_MOST", 2)
		self.AddFlag("not_pick")
		self.AddFlag("float")
		self.children = []
		self.Hide()

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def Clear(self):
		for child in self.children:
			child.Hide()
		self.children = []

	def __AppendText(self, text, y, color):
		line = ui.TextLine()
		line.SetParent(self)
		line.AddFlag("not_pick")
		line.SetPosition(self.WIDTH / 2, y)
		line.SetHorizontalAlignCenter()
		line.SetPackedFontColor(color)
		line.SetText(text)
		line.SetOutline()
		line.Show()
		self.children.append(line)

	def __AppendTable(self, headers, widths, rows, rowColors, y):
		colors = [self.C_LINE, self.C_HEAD_BG, self.C_ROW_BG, self.C_HEAD_TXT, self.C_CELL_TXT]
		tbl = ui.Table(self.WIDTH - self.PAD * 2, self.HEAD_H, colors)
		tbl.SetParent(self)
		tbl.SetPosition(self.PAD, y)
		tbl.set_columns(headers, widths)
		for idx, rowData in enumerate(rows):
			tbl.add_row(rowData, self.ROW_H, [rowColors[idx]] * len(rowData))
		tbl.Show()
		self.children.append(tbl)
		return tbl.GetHeight()

	def Build(self, blocks):
		self.Clear()
		y = self.PAD
		for block in blocks:
			kind = block[0]
			if kind == "title":
				self.__AppendText(block[1], y, block[2])
				y += self.LINE_H + 3
			elif kind == "text":
				self.__AppendText(block[1], y, block[2])
				y += self.LINE_H
			elif kind == "space":
				y += block[1]
			elif kind == "table":
				h = self.__AppendTable(block[1], block[2], block[3], block[4], y)
				y += h + 4
		self.SetSize(self.WIDTH, y + self.PAD)

if app.ENABLE_PLAYER_EVENT_ACTIVATION:
	class ActivatableEventWindow(ui.Board):
		ART_PATH	= "d:/ymir work/ui/event_rework/"
		ICON_PATH	= "d:/ymir work/ui/game/event_alert/event_id/"
		ROW_IMG		= ART_PATH + "new_event_activatable_row.png"
		BTN_NORM	= ART_PATH + "btn_activ_norm.png"
		BTN_HOVER	= ART_PATH + "btn_activ_hover.png"
		BTN_SELECT	= ART_PATH + "btn_activ_select.png"

		ROW_W		= 223
		ROW_H		= 87
		ROW_GAP		= 6
		COLS		= 2
		COL_GAP		= 6
		PAD_X		= 12
		PAD_TOP		= 30
		PAD_BOTTOM	= 12
		WIN_W		= COLS * ROW_W + (COLS - 1) * COL_GAP + PAD_X * 2

		# row content offsets (relative to the row image)
		NAME_X		= 14 + 100
		NAME_Y		= 12
		TIMER_X		= 14 + 100
		TIMER_Y		= 33
		BTN_X		= 18 + 10
		BTN_Y		= 53
		ICON_X		= ROW_W - 95
		ICON_Y		= 0
		ICON_SCALE	= 0.7

		COLOR_DURATION	= 0xffcfcfcf
		COLOR_RUNNING	= 0xffffda79

		# hover marquee for the one-line name label (uiadvancedgameoptions idiom)
		MARQUEE_LIMIT_PX	= 100
		MARQUEE_SPEED_PX	= 60.0
		MARQUEE_HIT_INTERVAL	= 0.1
		MARQUEE_HOVER_DELAY	= 0.35

		def __init__(self):
			ui.Board.__init__(self)
			# Docked to the main event panel (repositioned in EventOverview.OnUpdate), so not independently movable.
			self.AddFlag("float")
			self.rows = []
			self.nextUpdate = 0
			self.marquee = {}
			self.marqueeHot = None
			self.marqueeHotSince = 0.0
			self.marqueeOffset = 0.0
			self.marqueeDone = False
			self.marqueeHitTime = 0.0
			self.lastMarqueeTime = time.time()
			self.__BuildBase()
			self.SetSize(self.WIN_W, self.PAD_TOP + self.ROW_H + self.PAD_BOTTOM)
			self.Hide()

		def __del__(self):
			ui.Board.__del__(self)

		def __BuildBase(self):
			titleBar = ui.TitleBar()
			titleBar.SetParent(self)
			titleBar.MakeTitleBar(self.WIN_W - 16, "red")
			titleBar.SetPosition(8, 7)
			titleBar.SetCloseEvent(ui.__mem_func__(self.Close))
			titleBar.Show()
			self.titleBar = titleBar

			titleText = ui.TextLine()
			titleText.SetParent(titleBar)
			titleText.SetPosition(0, 0)
			titleText.SetWindowHorizontalAlignCenter()
			titleText.SetHorizontalAlignCenter()
			titleText.SetText(localeinfo.EVENT_ACTIVATABLE_TITLE)
			titleText.Show()
			self.titleText = titleText

		def __ClearRows(self):
			self.__MarqueeRest()
			self.marquee = {}
			for row in self.rows:
				for w in row["widgets"]:
					w.Hide()
				row["bg"].Hide()
			self.rows = []

		def __Collect(self):
			# Returns [(eventType, durationMinutes, personalEnd, itemVnum), ...] for
			# today's activatable events that can still be started or are running.
			result = []
			todayNum = datetime.date.today().day
			eventCount = eventMgr.GetDayEventCount(todayNum)
			now = int(time.time())
			for i in range(eventCount):
				(eventID, eventType, eventStart, eventEnd, value0, value1, completed) = eventMgr.GetEventData(i, todayNum)
				if completed:
					continue

				(act, pEnd, used, durMin) = eventMgr.GetEventActivation(i, todayNum)
				if not act:
					continue

				# Already activated today and the personal timer expired -> nothing left to do.
				if used and pEnd <= now:
					continue

				result.append((eventType, durMin, pEnd, value1))
			return result

		def __BuildRow(self, index, eventType, durMin, personalEnd, itemVnum):
			col = index % self.COLS
			if localeinfo.IsARABIC():
				col = self.COLS - 1 - col
			x = self.PAD_X + col * (self.ROW_W + self.COL_GAP)
			y = self.PAD_TOP + (index // self.COLS) * (self.ROW_H + self.ROW_GAP)
			widgets = []

			bg = ui.ExpandedImageBox()
			bg.SetParent(self)
			bg.AddFlag("not_pick")
			bg.AddFlag("attach")
			bg.LoadImage(self.ROW_IMG)
			bg.SetPosition(x, y)
			bg.Show()

			nameText = ui.TextLine()
			nameText.SetParent(bg)
			nameText.AddFlag("not_pick")
			nameText.SetPosition(self.NAME_X, self.NAME_Y)
			name = EventOverview.EVENT_NAME_DICT.get(eventType, "-")
			evtItemName = GetEventItemName(eventType, itemVnum)
			if evtItemName:
				name = "%s : %s" % (name, evtItemName)
			nameText.SetText(name)
			nameText.SetOutline()
			nameText.Show()
			widgets.append(nameText)

			timerText = ui.TextLine()
			timerText.SetParent(bg)
			timerText.AddFlag("not_pick")
			timerText.SetPosition(self.TIMER_X, self.TIMER_Y)
			timerText.SetOutline()
			timerText.Show()
			widgets.append(timerText)

			btn = ui.Button()
			btn.SetParent(bg)
			btn.SetUpVisual(self.BTN_NORM)
			btn.SetOverVisual(self.BTN_HOVER)
			btn.SetDownVisual(self.BTN_SELECT)
			btn.SetPosition(self.BTN_X, self.BTN_Y)
			btn.SetText(localeinfo.EVENT_ACTIVATE_BTN)
			btn.SetEvent(ui.__mem_func__(self.__OnClickStart), eventType)
			btn.Show()
			widgets.append(btn)

			icon = ui.ExpandedImageBox()
			icon.SetParent(bg)
			icon.AddFlag("not_pick")
			iconPath = self.ICON_PATH + str(eventType) + "_active.png"
			import pack
			if pack.Exist(iconPath):
				icon.LoadImage(iconPath)
			#icon.SetScale(self.ICON_SCALE, self.ICON_SCALE)
			icon.SetPosition(self.ICON_X, self.ICON_Y)
			icon.Show()
			widgets.append(icon)

			row = {"bg": bg, "widgets": widgets, "type": eventType,
				   "durMin": durMin, "personalEnd": personalEnd,
				   "timer": timerText, "btn": btn, "name": nameText}
			self.rows.append(row)
			self.__UpdateRow(row)

		def __UpdateRow(self, row):
			now = int(time.time())
			if row["personalEnd"] > now:
				# Started -> show the remaining personal time, hide the Start button.
				row["timer"].SetText(localeinfo.EVENT_ACTIVE_LEFT % localeinfo.SecondToDHMS(max(0, row["personalEnd"] - now)))
				row["timer"].SetPackedFontColor(self.COLOR_RUNNING)
				row["btn"].Hide()
			else:
				# Not started -> show how long it will run once started.
				sec = max(0, row["durMin"]) * 60
				durStr = "%02d:%02d:%02d" % (sec / 3600, (sec % 3600) / 60, sec % 60)
				row["timer"].SetText(localeinfo.EVENT_ACTIVATE_DURATION % durStr)
				row["timer"].SetPackedFontColor(self.COLOR_DURATION)
				row["btn"].Show()

		def __OnClickStart(self, eventType):
			net.SendEventActivate(eventType)
			# Debounce: hide the clicked row's Start button until the result refreshes the list.
			for row in self.rows:
				if row["type"] == eventType:
					row["btn"].Hide()
					break

		def Refresh(self):
			self.__ClearRows()
			data = self.__Collect()
			if not data:
				self.Hide()
				return 0
			for idx, (eventType, durMin, personalEnd, itemVnum) in enumerate(data):
				self.__BuildRow(idx, eventType, durMin, personalEnd, itemVnum)

			gridRows = (len(data) + self.COLS - 1) // self.COLS
			height = self.PAD_TOP + gridRows * (self.ROW_H + self.ROW_GAP) - self.ROW_GAP + self.PAD_BOTTOM
			self.SetSize(self.WIN_W, height)
			return len(data)

		def HasActivatable(self):
			return len(self.__Collect()) > 0

		def Open(self, refX, refY):
			count = self.Refresh()
			if count <= 0:
				self.Hide()
				return False

			if refX != -1 and refY != -1:
				self.SetPosition(refX - self.GetWidth() - 5, refY)
			self.Show()
			self.SetTop()
			self.nextUpdate = app.GetTime() + 1
			return True

		def Close(self):
			self.Hide()

		def OnPressEscapeKey(self):
			self.Close()
			return True

		def TickRows(self):
			if not self.IsShow():
				return
			now = app.GetTime()
			if now < self.nextUpdate:
				return
			self.nextUpdate = now + 1
			for row in self.rows:
				self.__UpdateRow(row)

		def __MarqueeInfo(self, label):
			info = self.marquee.get(label)
			if info is not None:
				return info
			full = label.GetText()
			if not full:
				return None
			w, h = label.GetTextSize()
			info = {"full": full, "short": full, "fullW": w, "h": h, "over": w > self.MARQUEE_LIMIT_PX}
			if info["over"]:
				cut = full
				while cut and label.GetTextSize()[0] > self.MARQUEE_LIMIT_PX - 10:
					cut = cut[:-1]
					label.SetText(cut)
				info["short"] = cut + ".."
				label.SetText(info["short"])
			self.marquee[label] = info
			return info

		def __MarqueeMask(self, label, info, offset):
			# the label itself is what moves, so the box it must stay inside is derived
			# by undoing the current offset; unlike uiadvancedgameoptions these labels
			# are plain left-anchored windows -- Arabic glyphs flow LEFT from the anchor
			# and the label slides right (+offset), so undoing it is gx - offset
			gx, gy = label.GetGlobalPosition()
			if localeinfo.IsARABIC():
				base = gx - offset
				label.SetClippingMaskRect(int(base - self.MARQUEE_LIMIT_PX), int(gy), int(base + 20), int(gy + info["h"]))
			else:
				base = gx + offset
				label.SetClippingMaskRect(int(base), int(gy), int(base + self.MARQUEE_LIMIT_PX), int(gy + info["h"]))

		def __MarqueeRest(self):
			label = self.marqueeHot
			self.marqueeHot = None
			self.marqueeOffset = 0.0
			self.marqueeDone = False
			if not label:
				return
			info = self.marquee.get(label)
			if not info:
				return
			if "baseX" in info:
				label.SetPosition(info["baseX"], label.GetLocalPosition()[1])
			label.SetText(info["short"])
			# the mask cannot be switched off, so widen it past anything it could clip
			label.SetClippingMaskRect(0, 0, wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())

		def __MarqueeHitTest(self):
			xMouse, yMouse = wndMgr.GetMousePosition()
			rtl = localeinfo.IsARABIC()
			for row in self.rows:
				label = row["name"]
				info = self.__MarqueeInfo(label)
				if not info or not info["over"]:
					continue
				x, y = label.GetGlobalPosition()
				h = info["h"]
				w = self.MARQUEE_LIMIT_PX
				if rtl:
					inside = (xMouse >= x - w and xMouse < x + 20 and yMouse >= y and yMouse < y + h)
				else:
					inside = (xMouse >= x and xMouse < x + w and yMouse >= y and yMouse < y + h)
				if inside:
					return label
			return None

		def __TickMarquee(self):
			current_time = time.time()
			dt = current_time - self.lastMarqueeTime
			if dt <= 0.0:
				return
			self.lastMarqueeTime = current_time

			if current_time - self.marqueeHitTime >= self.MARQUEE_HIT_INTERVAL:
				self.marqueeHitTime = current_time
				hot = self.__MarqueeHitTest()
				if hot is not self.marqueeHot:
					self.__MarqueeRest()
					if hot:
						self.marqueeHot = hot
						self.marqueeHotSince = current_time

			label = self.marqueeHot
			if not label:
				return
			info = self.marquee.get(label)
			if not info or not info["over"]:
				return
			if current_time - self.marqueeHotSince < self.MARQUEE_HOVER_DELAY:
				return

			if label.GetText() != info["full"]:
				info["baseX"] = label.GetLocalPosition()[0]
				label.SetText(info["full"])
				self.marqueeOffset = 0.0
				self.__MarqueeMask(label, info, 0.0)
				return

			travel = info["fullW"] - self.MARQUEE_LIMIT_PX
			if travel <= 0:
				return
			if not self.marqueeDone:
				self.marqueeOffset += self.MARQUEE_SPEED_PX * dt
				if self.marqueeOffset >= travel:
					self.marqueeOffset = float(travel)
					self.marqueeDone = True
				baseX = info.get("baseX", label.GetLocalPosition()[0])
				y = label.GetLocalPosition()[1]
				if localeinfo.IsARABIC():
					label.SetPosition(int(baseX + self.marqueeOffset), y)
				else:
					label.SetPosition(int(baseX - self.marqueeOffset), y)
			self.__MarqueeMask(label, info, self.marqueeOffset)

		def OnUpdate(self):
			self.TickRows()
			if self.IsShow():
				self.__TickMarquee()

		def Destroy(self):
			self.__ClearRows()
			self.Hide()

if app.USE_EVENT_MANAGER_EXPANDED:
	class AlertImg(ui.ImageBox):
		def UpdateTime(self):
			if app.ENABLE_PLAYER_EVENT_ACTIVATION and self.activatable and self.personalEnd > int(time.time()):
				self.descTextLine.SetText("{}".format(localeinfo.EVENT_ACTIVE_LEFT % localeinfo.SecondToDHMS(max(0, self.personalEnd - int(time.time())))))
				self.descTextLine.SetPackedFontColor(0xffffda79)
				self.descTextLine.SetOutline()
				return

			if self.bActive == True:
				leftSec = max(0, self.eventEnd - int(time.time()))
				self.descTextLine.SetText("{}\n{}".format( self.eventName , localeinfo.EVENT_END_IN % localeinfo.SecondToDHMS(leftSec)))
				self.descTextLine.SetOutline()
			else:
				if app.ENABLE_PLAYER_EVENT_ACTIVATION and self.activatable and not self.usedToday:
					# Activatable + not started yet: prompt to activate, not a misleading "starts in" countdown.
					self.descTextLine.SetText("{}\n{}".format(self.eventName, localeinfo.EVENT_ACTIVATE_HINT))
				else:
					leftSec = max(0, self.eventStart - int(time.time()))
					self.descTextLine.SetText("{}\n{}".format(self.eventName,localeinfo.EVENT_START_IN % localeinfo.SecondToDHMS(leftSec)))
				self.descTextLine.SetOutline()
	
		def SetStatus(self, bStatus):
			self.bActive = bStatus

			if app.ENABLE_INGAME_WIKI:
				self.UnloadImage()

			if app.ENABLE_PLAYER_EVENT_ACTIVATION and self.activatable and self.personalEnd > int(time.time()):
				self.LoadImage(self.eventImg + "_active.png")
				self.descTextLine.SetText("{}".format(localeinfo.EVENT_ACTIVE_LEFT % localeinfo.SecondToDHMS(max(0, self.personalEnd - int(time.time())))))
				self.descTextLine.SetPackedFontColor(0xffffda79)
				self.descTextLine.SetOutline()
				return

			if bStatus == True:
				leftSec = max(0, self.eventEnd - int(time.time()))

				self.LoadImage(self.eventImg + "_active.png")

				self.descTextLine.SetText(localeinfo.EVENT_END_IN % localeinfo.SecondToDHMS(leftSec))
				# self.descTextLine.SetPackedFontColor(0xffffda79)
			else:
				self.LoadImage(self.eventImg + "_incoming.png")

				if app.ENABLE_PLAYER_EVENT_ACTIVATION and self.activatable and not self.usedToday:
					# Activatable + not started yet: prompt to activate, not a misleading "starts in" countdown.
					self.descTextLine.SetText("{}\n{}".format(self.eventName, localeinfo.EVENT_ACTIVATE_HINT))
				else:
					leftSec = max(0, self.eventStart - int(time.time()))
					self.descTextLine.SetText(localeinfo.EVENT_START_IN % localeinfo.SecondToDHMS(leftSec))
				# self.descTextLine.SetPackedFontColor(ui.DEFAULT_FONT_COLOR)

		def __init__(self, bgParent, eventImg, eventType, eventStart, eventEnd, activatable=False, personalEnd=0, usedToday=False):
			ui.ImageBox.__init__(self)

			self.bActive = False
			self.activatable = activatable
			self.personalEnd = personalEnd
			self.usedToday = usedToday

			self.SetParent(bgParent)
			self.alertWindow = bgParent
			self.AddFlag("attach")
			self.AddFlag("movable")
			self.LoadImage(eventImg + "_incoming.png")
			self.SetPosition(2, 2)

			self.eventImg = eventImg
			self.eventType = eventType
			self.eventName = EventOverview.EVENT_NAME_DICT.get(eventType, "-")
			self.eventStart = eventStart
			self.eventEnd = eventEnd

			self.descTextLine = ui.TextLine()
			self.descTextLine.SetParent(self)
			self.descTextLine.AddFlag("attach")
			self.descTextLine.AddFlag("movable")

			if localeinfo.IsARABIC():
				self.descTextLine.SetHorizontalAlignRight()

			self.descTextLine.SetPosition(0, self.GetHeight() - 2)
			self.descTextLine.SetText("-")

			if app.USE_CTEXTLINE_AUTO_WRAP:
				self.descTextLine.SetAutoWrap(True)

			self.descTextLine.Show()

		def OnMouseLeftButtonDoubleClick(self):
			if self.alertWindow:
				self.alertWindow.OpenOverview()

		def Destroy(self):
			if app.ENABLE_INGAME_WIKI:
				self.UnloadImage()

			self.alertWindow = None
			del self.descTextLine
			self.descTextLine = None

		def __del__(self):
			ui.ImageBox.__del__(self)

	class EventAlert(ui.Window):
		WITH_PULSE = False
		IMG_PATH = "d:/ymir work/ui/game/event_alert/"

		if app.ENABLE_INGAME_WIKI:
			def __OnClick(self):
				eventType = self.activeEventsList[self.nextEventToBeShown].eventType

				if eventType == eventMgr.EVENT_TYPE_BOSS:
					net.SendRequestEventQuest("boss_event")
				elif eventType == eventMgr.EVENT_TYPE_FISHING:
					net.SendRequestEventQuest("fishing_event")
				elif eventType == eventMgr.EVENT_TYPE_GOLD_FROG:
					net.SendRequestEventQuest("golden_frog_event")
				elif eventType == eventMgr.EVENT_TYPE_HEXEGONAL_CHEST:
					net.SendRequestEventQuest("hexegonal_drop_event")
				elif eventType == eventMgr.EVENT_TYPE_HIDE_AND_SEEK:
					net.SendRequestEventQuest("hide_seek_event")
				elif eventType == eventMgr.EVENT_TYPE_METIN:
					net.SendRequestEventQuest("metin_event")
				elif eventType == eventMgr.EVENT_TYPE_MINING:
					net.SendRequestEventQuest("mining_event")
				elif eventType == eventMgr.EVENT_TYPE_MOONLIGHT:
					net.SendRequestEventQuest("moonlight_drop_event")
				elif eventType == eventMgr.EVENT_TYPE_OX:
					net.SendRequestEventQuest("oxevent_manager")
				elif eventType == eventMgr.EVENT_TYPE_TANAKA:
					net.SendRequestEventQuest("tanaka_event")
				elif eventType == eventMgr.EVENT_TYPE_OKAY_CARD:
					net.SendRequestEventQuest("okay_drop_event")
				elif eventType == eventMgr.EVENT_TYPE_CATCH_KING:
					net.SendRequestEventQuest("catch_drop_event")
				elif eventType == eventMgr.EVENT_TYPE_CUSTOMS:
					net.SendRequestEventQuest("customs_drop_event")
				elif eventType == eventMgr.EVENT_TYPE_MOUNTS:
					net.SendRequestEventQuest("mounts_drop_event")
				elif eventType == eventMgr.EVENT_TYPE_GOLD:
					net.SendRequestEventQuest("gold_event")
				elif eventType == eventMgr.EVENT_TYPE_SIEGE_WAR:
					net.SendRequestEventQuest("siege_war_event")
				elif eventType == eventMgr.EVENT_TYPE_KINGDOM_WAR:
					net.SendRequestEventQuest("kingdom_war_event")
				elif eventType == eventMgr.EVENT_TYPE_ATT_MONSTER:
					net.SendRequestEventQuest("att_monster_event")
				elif eventType == eventMgr.EVENT_TYPE_ATT_STONE:
					net.SendRequestEventQuest("stone_att_event")
				elif eventType == eventMgr.EVENT_TYPE_ATT_BOSS:
					net.SendRequestEventQuest("boss_att_event")
				elif app.USE_DROP_EVENT and eventType == eventMgr.EVENT_TYPE_DROP:
					net.SendRequestEventQuest("drop_event")
				elif app.USE_FISH_CHEST_EVENT and eventType == eventMgr.EVENT_TYPE_FISH_CHEST:
					net.SendRequestEventQuest("fish_event_chest")
				elif eventType == eventMgr.EVENT_TYPE_FISHING_CHEST:
					net.SendRequestEventQuest("fishing_event_chest")
				elif eventType == eventMgr.EVENT_TYPE_HORN_CHEST:
					net.SendRequestEventQuest("horn_event_chest")
				elif eventType == eventMgr.EVENT_TYPE_DOUBLE_STONES:
					net.SendRequestEventQuest("event_double_stone_loot")
				elif eventType == eventMgr.EVENT_TYPE_DOUBLE_BOSSES:
					net.SendRequestEventQuest("event_double_boss_loot")
				elif eventType == eventMgr.EVENT_TYPE_FISHING_MYST:
					net.SendRequestEventQuest("fishin_myst_event")
				elif eventType == eventMgr.EVENT_TYPE_PET_EXP:
					net.SendRequestEventQuest("petexp_event")

		def EmptyActiveEvents(self):
			for e in self.activeEventsList:
				e.Destroy()
				del e

			self.activeEventsList = []

		def OnRefresh(self):
			self.EmptyActiveEvents()

			self.startType = -1
			self.startSentAt = 0
			self.pinStartedAt = 0
			if self.startBtn:
				self.startBtn.Hide()

			self.nextUpdateTime = -1
			self.nextUpdateTodayNum = -1

			if self.WITH_PULSE == True:
				self.nextPulseTime = -1
				self.nextPulseHide = False

			self.nextEventToBeShown = 0
			self.totalEventsShown = 0
			self.wasShowed = False

			if self.todayNum == -1:
				self.todayNum = datetime.date.today().day

			eventCount = eventMgr.GetDayEventCount(self.todayNum)

			timeStampNow = int(time.time())

			if eventCount:
				for i in range(eventCount):
					(eventID, eventType, eventStart, eventEnd, eventValue0, eventValue1, eventCompleted) = eventMgr.GetEventData(i, self.todayNum)
					if eventCompleted:
						continue

					if not self.eventsDict.has_key(eventType):
						continue

					activatable = False
					personalEnd = 0
					usedToday = False
					if app.ENABLE_PLAYER_EVENT_ACTIVATION:
						(act, pEnd, used, durMin) = eventMgr.GetEventActivation(i, self.todayNum)
						activatable = bool(act)
						personalEnd = pEnd
						usedToday = bool(used)

					leftSec = max(0, eventEnd - timeStampNow)
					if activatable:
						if personalEnd <= timeStampNow and (usedToday or leftSec <= 0):
							continue
					else:
						if leftSec <= 0:
							continue

					self.activeEventsList.append(AlertImg(self, self.eventsDict[eventType], eventType, eventStart, eventEnd, activatable, personalEnd, usedToday))

			eventsListLength = len(self.activeEventsList)

			if eventsListLength == 0:
				self.Hide()
			else:
				self.totalEventsShown = len(self.activeEventsList) - 1
				self.nextUpdateTime = app.GetTime()
				self.nextUpdateTodayNum = app.GetTime() + 120

				self.Show()

		def CheckDayRefresh(self):
			if not self.isLoaded:
				return

			if self.todayNum != -1:
				if app.GetTime() > self.nextUpdateTodayNum:
					self.nextUpdateTodayNum = app.GetTime() + 120

					todayNum = datetime.date.today().day

					if self.todayNum != todayNum:
						self.todayNum = todayNum
						self.nextUpdateTime = -1
						self.OnRefresh()
						return

		def OnUpdate(self):
			if self.nextUpdateTime == -1:
				return

			timeNow = app.GetTime()

			if timeNow < self.nextUpdateTime:
				try:
					if self.activeEventsList[self.nextEventToBeShown].IsShow():
						self.activeEventsList[self.nextEventToBeShown].UpdateTime()
				except:
					pass

			if timeNow >= self.nextUpdateTime:
				if app.ENABLE_PLAYER_EVENT_ACTIVATION and self.wasShowed:
					cur = self.activeEventsList[self.nextEventToBeShown]
					ts = int(time.time())
					startable = cur.activatable and cur.personalEnd <= ts and not cur.usedToday and ts <= cur.eventEnd
					if self.mouseOver:
						self.nextUpdateTime = app.GetTime() + 1
						return
					if startable:
						# Hold the rotation on a startable event, but only for a
						# while - other scheduled events must still get screen time.
						if getattr(self, "pinStartedAt", 0) == 0:
							self.pinStartedAt = timeNow
						if timeNow - self.pinStartedAt < 15:
							# Lost-result recovery: re-show Start if no reply came back.
							if self.startType < 0 and getattr(self, "startSentAt", 0) > 0 and timeNow - self.startSentAt > 10:
								self.startSentAt = 0
								self.__UpdateStartButton(cur)
							self.nextUpdateTime = app.GetTime() + 1
							return
					self.pinStartedAt = 0

				if self.wasShowed:
					self.activeEventsList[self.nextEventToBeShown].Hide()

				if self.nextEventToBeShown >= self.totalEventsShown:
					self.nextEventToBeShown = 0
				elif self.wasShowed:
					self.nextEventToBeShown += 1

				if not self.wasShowed:
					self.wasShowed = True

				timeStampNow = int(time.time())

				if timeStampNow > self.activeEventsList[self.nextEventToBeShown].eventEnd:
					self.OnRefresh()
					return

				if timeStampNow >= self.activeEventsList[self.nextEventToBeShown].eventStart:
					self.bgImgIncoming.Hide()
					self.bgImgActivated.Show()
					self.activeEventsList[self.nextEventToBeShown].SetStatus(True)
				else:
					leftSec = max(0, self.activeEventsList[self.nextEventToBeShown].eventStart - timeStampNow)

					if leftSec > 86400:
						return
					else:
						self.bgImgActivated.Hide()
						self.bgImgIncoming.Show()
						self.activeEventsList[self.nextEventToBeShown].SetStatus(False)

				self.activeEventsList[self.nextEventToBeShown].Show()

				if app.ENABLE_PLAYER_EVENT_ACTIVATION:
					self.__UpdateStartButton(self.activeEventsList[self.nextEventToBeShown])

				if self.WITH_PULSE == True:
					self.nextPulseTime = -1
					self.nextPulseHide = False

				self.nextUpdateTime = app.GetTime() + 5
			elif self.WITH_PULSE == True:
				if self.nextPulseTime == -1:
					self.nextPulseTime = float(app.GetTime()) + 0.5
				else:
					if float(app.GetTime()) >= self.nextPulseTime:
						if self.nextPulseHide == False:
							self.activeEventsList[self.nextEventToBeShown].Hide()
							self.nextPulseHide = True
						else:
							self.activeEventsList[self.nextEventToBeShown].Show()
							self.nextPulseHide = False

						self.nextPulseTime = float(app.GetTime()) + 0.5

		def __Build(self):
			if self.isLoaded:
				return

			try:
				self.nextUpdateTime = -1
				self.todayNum = -1
				self.nextUpdateTodayNum = -1

				if self.WITH_PULSE == True:
					self.nextPulseTime = -1
					self.nextPulseHide = False

				self.nextEventToBeShown = 0
				self.totalEventsShown = 0
				self.wasShowed = False

				filePath = self.IMG_PATH + "bg.png"

				import pack
				if not pack.Exist(filePath):
					import dbg
					dbg.TraceError("%s doesn't exists" % (filePath))
					app.Abort()
				else:
					self.bgImgIncoming = ui.ImageBox()
					self.bgImgIncoming.SetParent(self)
					self.bgImgIncoming.AddFlag("attach")
					self.bgImgIncoming.AddFlag("movable")
					self.bgImgIncoming.LoadImage(self.IMG_PATH + "bg.png")
					self.bgImgIncoming.SetPosition(2, 2)
					self.bgImgIncoming.SetAlpha(0.0)
					self.bgImgIncoming.Show()

					self.bgImgActivated = ui.ImageBox()
					self.bgImgActivated.SetParent(self)
					self.bgImgActivated.AddFlag("attach")
					self.bgImgActivated.AddFlag("movable")
					self.bgImgActivated.LoadImage(self.IMG_PATH + "bg.png")
					self.bgImgActivated.SetPosition(2, 2)
					self.bgImgActivated.SetAlpha(0.0)
					self.bgImgActivated.Hide()

					self.SetSize(self.bgImgIncoming.GetWidth() + 4, self.bgImgIncoming.GetHeight() + 4 + 60)

					self.eventsDict = {}

					for k in EventOverview.EVENT_NAME_DICT.keys():
						filePath = self.IMG_PATH + "event_id/" + str(k) + "_incoming.png"
						if not pack.Exist(filePath):
							continue

						filePath = self.IMG_PATH + "event_id/" + str(k) + "_active.png"
						if not pack.Exist(filePath):
							continue

						self.eventsDict[k] = self.IMG_PATH + "event_id/" + str(k)

					self.activeEventsList = []

					if app.ENABLE_PLAYER_EVENT_ACTIVATION:
						self.startBtn = ui.Button()
						self.startBtn.SetParent(self)
						self.startBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
						self.startBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
						self.startBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
						self.startBtn.SetText(localeinfo.EVENT_ACTIVATE_BTN)
						self.startBtn.SetEvent(ui.__mem_func__(self.OnStartClicked))
						self.startBtn.Hide()

					if app.ENABLE_INGAME_WIKI:
						self.SetMouseRightButtonUpEvent(ui.__mem_func__(self.__OnClick))
			except Exception as err:
				import dbg
				dbg.TraceError(str(err))
				app.Abort()

			self.isLoaded = True

			import wndMgr
			self.SetPosition(wndMgr.GetScreenWidth() - self.GetWidth() - 150, 160)
			if app.ENABLE_WINDOW_RESIZE:
				self.SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - self.GetWidth() - 150, 160)})

		def __init__(self):
			ui.Window.__init__(self)

			self.AddFlag("movable")
			self.AddFlag("float")

			self.isLoaded = False
			self.hasAny = False
			self.mouseOver = False
			self.startType = -1
			self.startBtn = None
			self.eventInterface = None
			self.hintToolTip = None

			self.__Build()

		def BindInterface(self, interface):
			self.eventInterface = interface

		def OpenOverview(self):
			if self.eventInterface:
				self.eventInterface.ToggleInGameEvent()

		def OnMouseLeftButtonDoubleClick(self):
			self.OpenOverview()

		def __ShowHint(self):
			if not self.hintToolTip:
				self.hintToolTip = uitooltip.ToolTip(220)
				self.hintToolTip.SetFollow(False)
			self.hintToolTip.ClearToolTip()
			self.hintToolTip.AppendTextLine(localeinfo.EVENT_ALERT_DBLCLICK)
			if app.ENABLE_INGAME_WIKI:
				self.hintToolTip.AppendTextLine(localeinfo.EVENT_ALERT_RCLICK)
			self.hintToolTip.SetTop()
			self.hintToolTip.SetPosition(self.GetLeft(), self.GetTop() + self.GetHeight() + 5)
			self.hintToolTip.Show()

		def __HideHint(self):
			if self.hintToolTip:
				self.hintToolTip.Hide()

		def OnMouseOverIn(self):
			self.mouseOver = True
			self.__ShowHint()

		def OnMouseOverOut(self):
			self.mouseOver = False
			self.__HideHint()

		def OnStartClicked(self):
			if app.ENABLE_PLAYER_EVENT_ACTIVATION and self.startType >= 0:
				net.SendEventActivate(self.startType)
				# Debounce: hide until the result refreshes the alert. startSentAt
				# lets OnUpdate re-show the button if the result never arrives.
				self.startSentAt = app.GetTime()
				if self.startBtn:
					self.startBtn.Hide()
				self.startType = -1

		def __UpdateStartButton(self, cur):
			if not app.ENABLE_PLAYER_EVENT_ACTIVATION or not self.startBtn:
				return
			now = int(time.time())
			startable = cur.activatable and cur.personalEnd <= now and (not cur.usedToday) and now <= cur.eventEnd
			if startable:
				self.startType = cur.eventType
				self.startSentAt = 0
				self.startBtn.SetPosition((self.GetWidth() - self.startBtn.GetWidth()) / 2, cur.GetHeight() + 38)
				self.startBtn.Show()
			else:
				self.startType = -1
				self.startBtn.Hide()

		def Destroy(self):
			if self.isLoaded:
				if app.ENABLE_INGAME_WIKI:
					self.SetMouseRightButtonUpEvent(None)

				self.eventsDict = {}

				self.EmptyActiveEvents()

				if self.startBtn:
					self.startBtn.SetEvent(None)
					del self.startBtn
				self.startBtn = None

				del self.bgImgIncoming
				self.bgImgIncoming = None

				del self.bgImgActivated
				self.bgImgActivated = None

				if self.hintToolTip:
					self.hintToolTip.Hide()
					self.hintToolTip = None

		def __del__(self):
			ui.Window.__del__(self)
