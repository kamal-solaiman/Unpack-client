# coding: latin_1

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import chr
if app.ENABLE_12ZI or app.ENABLE_POISON_GAUGE_EFFECT:
	import chrmgr

import net
import player
import grp
import ui
import wndMgr
import messenger
if app.ENABLE_COMMUNITY_SYSTEM:
	import community
import guild
import nonplayer
import localeinfo
import constinfo
import osfinfo

if app.ENABLE_MISSION_QUEST:
	import missionhelper
if app.ENABLE_12ZI:
	import background
	import uicommon

if app.ENABLE_MESSENGER_BLOCK:
	import uicommon

if app.USE_PVP_TOURNAMENT:
	import pvp_tournament

if app.ENABLE_RENEWAL_PVP:
	import systemSetting

TARGET_BUTTON_PASS_LEADER = getattr(localeinfo, "TARGET_BUTTON_PASS_LEADER", "Pass Leadership")

if app.ENABLE_DPS_METER:
	import chat
	DPS_TEXT = getattr(localeinfo, "DPSMETER_DPS", "DPS: %s")
	HITS_TEXT = getattr(localeinfo, "DPSMETER_HITS", "Hits: %d")
	DPS_FINAL_TEXT = getattr(localeinfo, "DPSMETER_DPS_FINAL", "Final: %s")
	DPS_SUMMARY_TEXT = getattr(localeinfo, "DPSMETER_SUMMARY", "Boss fight %s | DPS %s | %d hits | %s total damage")
	DPS_SUMMARY_STONE_TEXT = getattr(localeinfo, "DPSMETER_SUMMARY_STONE", "Stone fight %s | DPS %s | %d hits | %s total damage")

	DPS_POLL_INTERVAL = 1.0
	DPS_SMOOTH_FACTOR = 0.35
	DPS_CHANGE_THRESHOLD = 0.04
	DPS_WARMUP_MS = 2000
	DPS_HOLD_SECONDS = 4.0

	def AbbreviateNumber(number):
		if number >= 1000000:
			return "%.1fM" % (number / 1000000.0)
		if number >= 1000:
			return "%.1fK" % (number / 1000.0)
		return str(int(number))

	def AbbreviateDPS(number):
		if number >= 10000000:
			return "%dM" % int(number / 1000000)
		if number >= 1000000:
			return "%.1fM" % (number / 1000000.0)
		if number >= 10000:
			return "%dK" % int(number / 1000)
		if number >= 1000:
			return "%.1fK" % (number / 1000.0)
		return str(int(number))

	def FormatFightTime(elapsedMS):
		totalSeconds = int(elapsedMS / 1000)
		return "%d:%02d" % (totalSeconds / 60, totalSeconds % 60)

	class DPSBadge(ui.ThinBoard):
		def __init__(self):
			ui.ThinBoard.__init__(self, "TOP_MOST", 2)
			self.holdUntil = 0.0

		def IsHolding(self):
			return getattr(self, "holdUntil", 0.0) > 0.0

		def StartHold(self):
			self.holdUntil = app.GetTime() + DPS_HOLD_SECONDS

		def CancelHold(self):
			self.holdUntil = 0.0

		def OnUpdate(self):
			holdUntil = getattr(self, "holdUntil", 0.0)
			if holdUntil > 0.0 and app.GetTime() >= holdUntil:
				self.holdUntil = 0.0
				self.Hide()

class TargetBoard(ui.ThinBoard):
	if app.ENABLE_MESSENGER_BLOCK:
		BUTTON_NAME_LIST = [
			localeinfo.TARGET_BUTTON_WHISPER,
			localeinfo.TARGET_BUTTON_EXCHANGE,
			localeinfo.TARGET_BUTTON_FIGHT,
			localeinfo.TARGET_BUTTON_ACCEPT_FIGHT,
			localeinfo.TARGET_BUTTON_AVENGE,
			localeinfo.TARGET_BUTTON_FRIEND,
			localeinfo.TARGET_BUTTON_INVITE_PARTY,
			localeinfo.TARGET_BUTTON_LEAVE_PARTY,
			localeinfo.TARGET_BUTTON_EXCLUDE,
			TARGET_BUTTON_PASS_LEADER,
			localeinfo.TARGET_BUTTON_INVITE_GUILD,
			localeinfo.TARGET_BUTTON_DISMOUNT,
			localeinfo.TARGET_BUTTON_EXIT_OBSERVER,
			localeinfo.TARGET_BUTTON_VIEW_EQUIPMENT,
			localeinfo.TARGET_BUTTON_REQUEST_ENTER_PARTY,
			localeinfo.TARGET_BUTTON_BUILDING_DESTROY,
			localeinfo.TARGET_BUTTON_EMOTION_ALLOW,
			localeinfo.TARGET_BUTTON_BLOCK,
			localeinfo.TARGET_BUTTON_BLOCK_REMOVE,
			localeinfo.TARGET_BUTTON_REVIVE,
			"VOTE_BLOCK_CHAT",
		]
	else:
		BUTTON_NAME_LIST = [
			localeinfo.TARGET_BUTTON_WHISPER,
			localeinfo.TARGET_BUTTON_EXCHANGE,
			localeinfo.TARGET_BUTTON_FIGHT,
			localeinfo.TARGET_BUTTON_ACCEPT_FIGHT,
			localeinfo.TARGET_BUTTON_AVENGE,
			localeinfo.TARGET_BUTTON_FRIEND,
			localeinfo.TARGET_BUTTON_INVITE_PARTY,
			localeinfo.TARGET_BUTTON_LEAVE_PARTY,
			localeinfo.TARGET_BUTTON_EXCLUDE,
			TARGET_BUTTON_PASS_LEADER,
			localeinfo.TARGET_BUTTON_INVITE_GUILD,
			localeinfo.TARGET_BUTTON_DISMOUNT,
			localeinfo.TARGET_BUTTON_EXIT_OBSERVER,
			localeinfo.TARGET_BUTTON_VIEW_EQUIPMENT,
			localeinfo.TARGET_BUTTON_REQUEST_ENTER_PARTY,
			localeinfo.TARGET_BUTTON_BUILDING_DESTROY,
			localeinfo.TARGET_BUTTON_EMOTION_ALLOW,
			"VOTE_BLOCK_CHAT",
		]

	GRADE_NAME = {
		nonplayer.PAWN : localeinfo.TARGET_LEVEL_PAWN,
		nonplayer.S_PAWN : localeinfo.TARGET_LEVEL_S_PAWN,
		nonplayer.KNIGHT : localeinfo.TARGET_LEVEL_KNIGHT,
		nonplayer.S_KNIGHT : localeinfo.TARGET_LEVEL_S_KNIGHT,
		nonplayer.BOSS : localeinfo.TARGET_LEVEL_BOSS,
		nonplayer.KING : localeinfo.TARGET_LEVEL_KING,
	}

	EXCHANGE_LIMIT_RANGE = 3000

	if app.ENABLE_ELEMENT_ADD:
		ELEMENT_IMG_PATH = {
			0: 'd:/ymir work/ui/game/12zi/element/elect.sub',
			1: 'd:/ymir work/ui/game/12zi/element/fire.sub',
			2: 'd:/ymir work/ui/game/12zi/element/ice.sub',
			3: 'd:/ymir work/ui/game/12zi/element/wind.sub',
			4: 'd:/ymir work/ui/game/12zi/element/earth.sub',
			5: 'd:/ymir work/ui/game/12zi/element/dark.sub'
		}
		ELEMENT_ENCHANT_ICON_SCALE = 0.8

	if app.ENABLE_INGAME_WIKI:
		wndWiki = None

		def __PressDropInfo(self):
			if self.monsterVnum == 0 or not self.wndWiki:
				return

			if not self.wndWiki.IsShow():
				net.ToggleWikiWindow()

			self.wndWiki.CloseBaseWindows()
			self.wndWiki.OpenSpecialPage(None, self.monsterVnum, True)

	def __init__(self):
		ui.ThinBoard.__init__(self)
		if app.ENABLE_MESSENGER_BLOCK:
			self.AddFlag("float")

		name = ui.TextLine()
		name.SetParent(self)
		name.SetDefaultFontName()
		name.SetOutline()
		if str(background.GetCurrentMapName()) == "metin2_map_deathmatch" and app.DEATHMATCH_MODE:
			name.Hide()
		else:
			name.Show()
		self.name = name

		hpGauge = ui.Gauge()
		hpGauge.SetParent(self)
		hpGauge.MakeGauge(130, "red")
		hpGauge.Hide()
		self.hpGauge = hpGauge

		if app.AUTO_HUNT_RUBINUM:
			self.infoHuntBoard = None
			self.infoText = None

		if app.ENABLE_VIEW_TARGET_DECIMAL_HP:
			hpDecimal = ui.TextLine()
			hpDecimal.SetParent(hpGauge)
			hpDecimal.SetDefaultFontName()
			hpDecimal.SetPosition(5, 5)
			hpDecimal.SetOutline()
			hpDecimal.Hide()
			self.hpDecimal = hpDecimal

		if app.AUTO_HUNT_RUBINUM:
			infoImage = ui.ImageBox()
			infoImage.SetParent(self)
			infoImage.LoadImage("d:/ymir work/ui/game/wheel/question_mark_glow.png")
			infoImage.SAFE_SetStringEvent("MOUSE_OVER_IN", self.ShowAutoHuntInfo)
			infoImage.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.HideAutoHuntInfo)
			infoImage.SetWindowHorizontalAlignRight()
			infoImage.Hide()
			self.infoImage = infoImage

			infoImageText = ui.TextLine()
			infoImageText.SetParent(infoImage)
			infoImageText.SetDefaultFontName()
			infoImageText.SetOutline()
			infoImageText.Hide()
			self.infoImageText = infoImageText

			queueClearWnd = ui.Window("TOP_MOST")
			queueClearWnd.AddFlag("float")
			queueClearWnd.SetSize(59, 55)
			queueClearWnd.Hide()
			self.queueClearWnd = queueClearWnd

			queueClearButton = ui.Button()
			queueClearButton.SetParent(queueClearWnd)
			queueClearButton.SetUpVisual("d:/ymir work/ui/metine_queue_clear_01.png")
			queueClearButton.SetOverVisual("d:/ymir work/ui/metine_queue_clear_02.png")
			queueClearButton.SetDownVisual("d:/ymir work/ui/metine_queue_clear_03.png")
			queueClearButton.SetToolTipText(getattr(localeinfo, "AUTO_QUEUE_CLEAR_TOOLTIP", "Clear queue"))
			queueClearButton.SetEvent(ui.__mem_func__(self.OnPressedQueueClear))
			queueClearButton.SetPosition(0, 0)
			queueClearButton.Show()
			self.queueClearButton = queueClearButton

			queueCountText = ui.TextLine()
			queueCountText.SetParent(queueClearButton)
			queueCountText.SetDefaultFontName()
			queueCountText.SetOutline()
			queueCountText.SetHorizontalAlignCenter()
			queueCountText.SetPosition(11, 33)
			queueCountText.Show()
			self.queueCountText = queueCountText

			self.queueCount = 0

		closeButton = ui.Button()
		closeButton.SetParent(self)
		closeButton.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")
		closeButton.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")
		closeButton.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")
		closeButton.SetPosition(10, 13)

		if localeinfo.IsARABIC():
			hpGauge.SetPosition(55, 17)
			hpGauge.SetWindowHorizontalAlignLeft()
			closeButton.SetWindowHorizontalAlignLeft()
		else:
			hpGauge.SetPosition(175, 17)
			hpGauge.SetWindowHorizontalAlignRight()
			closeButton.SetWindowHorizontalAlignRight()

		closeButton.SetEvent(ui.__mem_func__(self.OnPressedCloseButton))
		closeButton.Show()
		self.closeButton = closeButton

		if app.ENABLE_INGAME_WIKI:
			tmp = ui.Button()
			tmp.SetParent(self)
			tmp.SetUpVisual("d:/ymir work/ui/game/wheel/mob_info_01.png")
			tmp.SetOverVisual("d:/ymir work/ui/game/wheel/mob_info_02.png")
			tmp.SetDownVisual("d:/ymir work/ui/game/wheel/mob_info_03.png")
			tmp.SetToolTipText(localeinfo.WIKI_INFO_BUTTON)
			tmp.SetEvent(ui.__mem_func__(self.__PressDropInfo))
			tmp.Hide()

			self.dropInfoButton = tmp
			self.monsterVnum = 0

		# Mission progress text
		if app.ENABLE_MISSION_QUEST:
			missionProgressText = ui.TextLine()
			missionProgressText.SetParent(self)
			missionProgressText.SetDefaultFontName()
			missionProgressText.SetFontColor(0.4, 1.0, 0.4)  # Bright green
			missionProgressText.SetOutline()
			missionProgressText.Hide()
			self.missionProgressText = missionProgressText

		contribText = ui.TextLine()
		contribText.SetParent(self)
		contribText.SetDefaultFontName()
		contribText.SetOutline()
		contribText.Hide()
		self.contribText = contribText
		self.contribData = {}

		if app.ENABLE_DPS_METER:
			dpsBoard = DPSBadge()
			dpsBoard.AddFlag("float")
			dpsBoard.AddFlag("not_pick")
			dpsBoard.SetSize(90, 60)
			dpsBoard.Hide()
			self.dpsBoard = dpsBoard

			dpsText = ui.TextLine()
			dpsText.SetParent(dpsBoard)
			dpsText.SetFontName(localeinfo.UI_DEF_FONT_LARGE)
			dpsText.SetOutline()
			dpsText.SetPosition(45, 30)
			dpsText.SetHorizontalAlignCenter()
			dpsText.Show()
			self.dpsText = dpsText

			hitsText = ui.TextLine()
			hitsText.SetParent(dpsBoard)
			hitsText.SetDefaultFontName()
			hitsText.SetOutline()
			hitsText.SetPosition(55, 5)
			hitsText.Show()
			self.hitsText = hitsText

			self.dpsNextPollTime = 0.0
			self.dpsSmoothed = None
			self.dpsShownValue = None
			self.dpsLastTargetVID = 0
			self.dpsLastHitCount = -1
			self.dpsLastDPS = 0

		if app.ENABLE_COMBAT_POINTS:
			CP_IMG_PATH = "d:/ymir work/ui/game/combat_point/"

			self.cpGearIcon = ui.ImageBox()
			self.cpGearIcon.SetParent(self)
			self.cpGearIcon.LoadImage(CP_IMG_PATH + "cp_1.png")
			self.cpGearIcon.Hide()

			self.cpGearText = ui.TextLine()
			self.cpGearText.SetParent(self)
			self.cpGearText.SetDefaultFontName()
			self.cpGearText.SetOutline()
			self.cpGearText.SetPackedFontColor(0xFFff9f43)
			self.cpGearText.Hide()

			self.cpTotalIcon = ui.ImageBox()
			self.cpTotalIcon.SetParent(self)
			self.cpTotalIcon.LoadImage(CP_IMG_PATH + "cp_2.png")
			self.cpTotalIcon.Hide()

			self.cpTotalText = ui.TextLine()
			self.cpTotalText.SetParent(self)
			self.cpTotalText.SetDefaultFontName()
			self.cpTotalText.SetOutline()
			self.cpTotalText.SetPackedFontColor(0xFFc8d6e5)
			self.cpTotalText.Hide()

			self.cpGearValue = 0
			self.cpTotalValue = 0

		self.buttonDict = {}
		self.showingButtonList = []
		for buttonName in self.BUTTON_NAME_LIST:
			button = ui.Button()
			button.SetParent(self)

			if localeinfo.IsARABIC():
				button.SetUpVisual("d:/ymir work/ui/public/Small_Button_01.sub")
				button.SetOverVisual("d:/ymir work/ui/public/Small_Button_02.sub")
				button.SetDownVisual("d:/ymir work/ui/public/Small_Button_03.sub")
			else:
				button.SetUpVisual("d:/ymir work/ui/public/small_thin_button_01.sub")
				button.SetOverVisual("d:/ymir work/ui/public/small_thin_button_02.sub")
				button.SetDownVisual("d:/ymir work/ui/public/small_thin_button_03.sub")

			button.SetWindowHorizontalAlignCenter()
			button.SetText(buttonName)
			button.Hide()
			self.buttonDict[buttonName] = button
			self.showingButtonList.append(button)

		self.buttonDict[localeinfo.TARGET_BUTTON_WHISPER].SetEvent(ui.__mem_func__(self.OnWhisper))
		self.buttonDict[localeinfo.TARGET_BUTTON_EXCHANGE].SetEvent(ui.__mem_func__(self.OnExchange))
		self.buttonDict[localeinfo.TARGET_BUTTON_FIGHT].SetEvent(ui.__mem_func__(self.OnPVP))
		self.buttonDict[localeinfo.TARGET_BUTTON_ACCEPT_FIGHT].SetEvent(ui.__mem_func__(self.OnPVP))
		self.buttonDict[localeinfo.TARGET_BUTTON_AVENGE].SetEvent(ui.__mem_func__(self.OnPVP))
		self.buttonDict[localeinfo.TARGET_BUTTON_FRIEND].SetEvent(ui.__mem_func__(self.OnAppendToMessenger))
		self.buttonDict[localeinfo.TARGET_BUTTON_FRIEND].SetEvent(ui.__mem_func__(self.OnAppendToMessenger))
		self.buttonDict[localeinfo.TARGET_BUTTON_INVITE_PARTY].SetEvent(ui.__mem_func__(self.OnPartyInvite))
		self.buttonDict[localeinfo.TARGET_BUTTON_LEAVE_PARTY].SetEvent(ui.__mem_func__(self.OnPartyExit))
		self.buttonDict[localeinfo.TARGET_BUTTON_EXCLUDE].SetEvent(ui.__mem_func__(self.OnPartyRemove))
		self.buttonDict[TARGET_BUTTON_PASS_LEADER].SetEvent(ui.__mem_func__(self.OnPartyPassLeader))

		self.buttonDict[localeinfo.TARGET_BUTTON_INVITE_GUILD].SAFE_SetEvent(self.__OnGuildAddMember)
		self.buttonDict[localeinfo.TARGET_BUTTON_DISMOUNT].SAFE_SetEvent(self.__OnDismount)
		self.buttonDict[localeinfo.TARGET_BUTTON_EXIT_OBSERVER].SAFE_SetEvent(self.__OnExitObserver)
		self.buttonDict[localeinfo.TARGET_BUTTON_VIEW_EQUIPMENT].SAFE_SetEvent(self.__OnViewEquipment)
		self.buttonDict[localeinfo.TARGET_BUTTON_REQUEST_ENTER_PARTY].SAFE_SetEvent(self.__OnRequestParty)
		self.buttonDict[localeinfo.TARGET_BUTTON_BUILDING_DESTROY].SAFE_SetEvent(self.__OnDestroyBuilding)
		self.buttonDict[localeinfo.TARGET_BUTTON_EMOTION_ALLOW].SAFE_SetEvent(self.__OnEmotionAllow)
		if app.ENABLE_MESSENGER_BLOCK:
			self.buttonDict[localeinfo.TARGET_BUTTON_BLOCK].SAFE_SetEvent(self.__OnBlock)
			self.buttonDict[localeinfo.TARGET_BUTTON_BLOCK_REMOVE].SAFE_SetEvent(self.__OnBlockRemove)
		if app.ENABLE_12ZI:
			self.buttonDict[localeinfo.TARGET_BUTTON_REVIVE].SAFE_SetEvent(self.__OnReviveQustionDialog)
		self.buttonDict["VOTE_BLOCK_CHAT"].SetEvent(ui.__mem_func__(self.__OnVoteBlockChat))

		self.__Initialize()
		self.ResetTargetBoard()

	def __del__(self):
		ui.ThinBoard.__del__(self)

		print "===================================================== DESTROYED TARGET BOARD"

	if app.AUTO_HUNT_RUBINUM:
		def ShowAutoHuntInfo(self):
			import item
			thinBoard = ui.ThinBoard()
			thinBoard.SetParent(self)
			thinBoard.SetPosition(self.infoImage.GetLocalPosition()[0], self.infoImage.GetLocalPosition()[1]+30)
			thinBoard.SetSize(330, 160)
			# thinBoard.SetWindowHorizontalAlignCenter()
			# thinBoard.SetWindowVerticalAlignBottom()
			# thinBoard.SetCloseEvent(ui.__mem_func__(self.HideAutoHuntInfo))
			thinBoard.Show()

			infoText = ui.MultiTextLine()
			infoText.SetParent(thinBoard)
			infoText.SetPosition(166, 10)
			#infoText.SetHorizontalAlignCenter()
			infoText.SetTextType("horizontal#center")
			#infoText.SetEnterToken(True)
			#infoText.SetOutline(True)
			item.SelectItem(72731)
			itemIcon = item.GetIconImageFileName()
			multi_text = ""
			#infoText.SetText("|cffF6EF15Target Metin Queue|r\nPressing |cff00ff00Shift + Right Click|r on MetinStones your character will target\na MetinStone and after you destroyed if, it will move to |cff00ff00the next one|r.\n|cffF99A08Max 3 queued Metinstones (without Premium Metinfarm)|r\n|cffF99A08Max. 5 queued Metinstones (with Premium Metinfarm)|r\n|E%s|e\n|cffF99A08Premium Metinfarm|r"%itemIcon)
			multi_text+=localeinfo.AUTO_STONE_HUNT_TEXT1
			multi_text+= "\n\n"
			multi_text+=localeinfo.AUTO_STONE_HUNT_TEXT2
			multi_text+= "\n"
			multi_text+=localeinfo.AUTO_STONE_HUNT_TEXT3
			multi_text+= "\n"
			multi_text+=localeinfo.AUTO_STONE_HUNT_TEXT4
			multi_text+= "\n"
			multi_text+=localeinfo.AUTO_STONE_HUNT_TEXT5
			multi_text+= "\n"
			multi_text+=localeinfo.AUTO_STONE_HUNT_TEXT6
			multi_text+= "\n\n"
			multi_text+=localeinfo.AUTO_STONE_HUNT_ICON
			infoText.SetText(multi_text)

			infoText.Show()
			self.infoText = infoText
			itemImage = ui.ImageBox()
			itemImage.SetParent(self)
			itemImage.Show()
			itemImage.LoadImage(item.GetIconImageFileName())
			itemImage.SetPosition(166, 10)


			self.infoHuntBoard = thinBoard

		def HideAutoHuntInfo(self):
			self.infoHuntBoard.Hide()

		def OnPressedQueueClear(self):
			if app.IsPressed(app.DIK_LSHIFT) or app.IsPressed(app.DIK_RSHIFT):
				player.ClearAutoHuntQueue()
			else:
				player.RemoveCurrentAutoHuntStone()
			self.queueCount = -1

		def __RefreshQueueClearButton(self):
			count = player.GetAutoHuntQueueCount()
			if count <= 0:
				if self.queueCount != 0:
					self.queueCount = 0
					self.queueClearWnd.Hide()
				return
			(bx, by) = self.GetLocalPosition()
			self.queueClearWnd.SetPosition(int(bx + self.GetWidth() + 4), int(by + 6))
			if not self.queueClearWnd.IsShow():
				self.queueClearWnd.Show()
			if count != self.queueCount:
				self.queueCount = count
				self.queueCountText.SetText(str(count))

	def __Initialize(self):
		self.nameString = ""
		self.nameLength = 0
		self.vid = 0

		# self.eventWhisper = None
		self.isShowButton = False
		if app.AUTO_HUNT_RUBINUM:
			self.IsAutoHunt = False
		if app.ENABLE_12ZI:
			self.questionDialog = None
		if app.ENABLE_ELEMENT_ADD:
			self.elementImgList = []

		if osfinfo.PAST_HEALTH_ON_TARGET:
			self.oldPercentage = 100
			self.newPercentage = 100

		if app.ENABLE_INGAME_WIKI:
			self.monsterVnum = 0

	def Destroy(self):
		if app.ENABLE_INGAME_WIKI:
			self.wndWiki = None

			if self.dropInfoButton:
				self.dropInfoButton.SetEvent(None)
				del self.dropInfoButton
				self.dropInfoButton = None

		self.__Initialize()

		self.name = None
		self.hpGauge = None
		if app.AUTO_HUNT_RUBINUM:
			self.infoImage = None
			self.infoImageText = None
			self.infoHuntBoard = None
			self.infoText = None
			self.queueCountText = None
			self.queueClearButton = None
			self.queueClearWnd = None
		if app.ENABLE_VIEW_TARGET_DECIMAL_HP:
			self.hpDecimal = None

		self.closeButton = None
		self.buttonDict = None
		self.showingButtonList = None
		if app.ENABLE_DPS_METER:
			self.dpsBoard = None
			self.dpsText = None
			self.hitsText = None
		if app.ENABLE_ELEMENT_ADD:
			self.elementImgList = None

		self.contribText = None
		self.contribData = {}

	def OnPressedCloseButton(self):
		player.ClearTarget()
		self.Close()

	def Close(self):
		self.__Initialize()

		if app.ENABLE_ELEMENT_ADD:
			self.__HideAllElementImg()

		self.Hide()

	def Hide(self):
		if app.ENABLE_DPS_METER:
			board = getattr(self, "dpsBoard", None)
			if board and not board.IsHolding():
				board.Hide()
		if app.AUTO_HUNT_RUBINUM:
			wnd = getattr(self, "queueClearWnd", None)
			if wnd:
				wnd.Hide()
		ui.ThinBoard.Hide(self)

	def Open(self, vid, name):
		if vid:
			if not constinfo.GET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD():
				if not player.IsSameEmpire(vid):
					self.Hide()
					return

			if vid != self.GetTargetVID():
				self.ResetTargetBoard()
				self.SetTargetVID(vid)
				self.SetTargetName(name)

			if player.IsMainCharacterIndex(vid):
				self.__ShowMainCharacterMenu()
			elif chr.INSTANCE_TYPE_BUILDING == chr.GetInstanceType(self.vid):
				self.Hide()
			else:
				self.RefreshButton()
				self.Show()
		else:
			self.HideAllButton()
			self.__ShowButton(localeinfo.TARGET_BUTTON_WHISPER)
			self.__ShowButton("VOTE_BLOCK_CHAT")
			self.__ArrangeButtonPosition()
			self.SetTargetName(name)
			self.Show()

	def Refresh(self):
		if self.IsShow():
			if self.IsShowButton():
				self.RefreshButton()

	def RefreshByVID(self, vid):
		if vid == self.GetTargetVID():
			self.Refresh()

	def RefreshByName(self, name):
		if name == self.GetTargetName():
			self.Refresh()

	def __ShowMainCharacterMenu(self):
		canShow = 0

		self.HideAllButton()

		if player.IsMountingHorse():
			self.__ShowButton(localeinfo.TARGET_BUTTON_DISMOUNT)
			canShow = 1

		if player.IsObserverMode():
			self.__ShowButton(localeinfo.TARGET_BUTTON_EXIT_OBSERVER)
			canShow = 1

		if canShow:
			self.__ArrangeButtonPosition()
			self.Show()
		else:
			self.Hide()

	def __ShowNameOnlyMenu(self):
		self.HideAllButton()

	def SetWhisperEvent(self, event):
		self.eventWhisper = event

	def UpdatePosition(self):
		self.SetPosition(wndMgr.GetScreenWidth() / 2 - self.GetWidth() / 2, 10)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : (Expr("SCREEN_WIDTH") / 2 - self.GetWidth() / 2, 10)})
		if app.ENABLE_ELEMENT_ADD:
			self.AdjustPositionElementImage()


	def ResetTargetBoard(self):
		for btn in self.buttonDict.values():
			btn.Hide()

		self.__Initialize()

		self.name.SetPosition(0, 13)
		self.name.SetHorizontalAlignCenter()
		self.name.SetWindowHorizontalAlignCenter()

		self.hpGauge.Hide()

		if app.ENABLE_VIEW_TARGET_DECIMAL_HP:
			self.hpDecimal.Hide()

		if app.ENABLE_INGAME_WIKI:
			self.dropInfoButton.Hide()

		if app.AUTO_HUNT_RUBINUM:
			self.infoImage.Hide()
			self.infoImageText.Hide()
			self.infoHuntBoard = None

		if app.ENABLE_COMBAT_POINTS:
			self.__HideCPDisplay()

		contribText = getattr(self, "contribText", None)
		if contribText:
			contribText.Hide()

		self.SetSize(250, 40)

	if app.ENABLE_COMBAT_POINTS:
		def SetCombatPoints(self, gearCP, totalCP):
			self.cpGearValue = gearCP
			self.cpTotalValue = totalCP

			if gearCP <= 0 and totalCP <= 0:
				self.__HideCPDisplay()
				return

			self.cpGearText.SetText(localeinfo.NumberToMoneyStringNEW(gearCP))
			self.cpTotalText.SetText(localeinfo.NumberToMoneyStringNEW(totalCP))
			self.__ShowCPDisplay()

		def __ShowCPDisplay(self):
			isShowButton = self.IsShowButton()
			rowY = 65 if isShowButton else 40

			# Count visible elements to position after them
			elementCount = 0
			if app.ENABLE_ELEMENT_ADD and hasattr(self, 'elementImgList') and self.elementImgList:
				elementCount = len(self.elementImgList)

			startX = (32 * elementCount) + 5

			# Shield icon + gear value
			self.cpGearIcon.SetPosition(startX, rowY + 2)
			self.cpGearText.SetPosition(startX + 22, rowY + 4)
			self.cpGearText.SetHorizontalAlignRight()
			self.cpGearIcon.Show()
			self.cpGearText.Show()

			# Swords icon + total value (after gear text, estimate ~45px for text)
			totalX = startX + 60
			self.cpTotalIcon.SetPosition(totalX, rowY + 2)
			self.cpTotalText.SetPosition(totalX + 22, rowY + 4)
			self.cpTotalText.SetHorizontalAlignRight()
			self.cpTotalIcon.Show()
			self.cpTotalText.Show()

		def __HideCPDisplay(self):
			self.cpGearIcon.Hide()
			self.cpGearText.Hide()
			self.cpTotalIcon.Hide()
			self.cpTotalText.Hide()
			self.cpGearValue = 0
			self.cpTotalValue = 0

	def SetTargetVID(self, vid):
		self.vid = vid

		if app.ENABLE_INGAME_WIKI:
			self.monsterVnum = 0

		self.__RefreshContrib()

	def OnBossContrib(self, vid, pct, threshold):
		try:
			vid = int(vid)
			pct = int(pct)
			threshold = int(threshold)
		except ValueError:
			return

		contribData = getattr(self, "contribData", None)
		if contribData is None:
			return

		if len(contribData) > 8:
			contribData.clear()

		contribData[vid] = (pct, threshold)
		self.__RefreshContrib()

	def __RefreshContrib(self):
		contribText = getattr(self, "contribText", None)
		if not contribText:
			return

		data = getattr(self, "contribData", {}).get(getattr(self, "vid", 0))
		if not data or not self.IsShow():
			contribText.Hide()
			return

		pct, threshold = data
		if pct >= threshold:
			contribText.SetFontColor(0.4, 1.0, 0.4)
			text = getattr(localeinfo, "DGN_BOSS_CONTRIB_OK_FMT", "Loot secured (%d%%)") % pct
		else:
			contribText.SetFontColor(1.0, 0.7, 0.3)
			text = getattr(localeinfo, "DGN_BOSS_CONTRIB_FMT", "Contribution: %d%% / %d%%") % (pct, threshold)

		contribText.SetText(text)

		rowY = 35
		missionText = getattr(self, "missionProgressText", None)
		if missionText and missionText.IsShow():
			rowY = 50

		neededHeight = int(rowY + 18)
		if self.GetHeight() < neededHeight:
			self.SetSize(self.GetWidth(), neededHeight)

		if localeinfo.IsARABIC():
			contribText.SetPosition(150, rowY)
		else:
			contribText.SetPosition(180, rowY)
		contribText.SetHorizontalAlignLeft()
		contribText.Show()

	def SetEnemyVID(self, vid):
		self.SetTargetVID(vid)

		name = chr.GetNameByVID(vid)

		if app.ENABLE_INGAME_WIKI:
			self.monsterVnum = 0

			if chr.GetInstanceType(self.vid) != chr.INSTANCE_TYPE_PLAYER:
				self.monsterVnum = nonplayer.GetRaceNumByVID(vid)

		level = nonplayer.GetLevelByVID(vid)
		grade = nonplayer.GetGradeByVID(vid)
		is_stone = nonplayer.IsMonsterStone(self.monsterVnum)

		nameFront = ""
		if -1 != level:
			nameFront += "Lv." + str(level) + " "
		if self.GRADE_NAME.has_key(grade):
			nameFront += "(" + self.GRADE_NAME[grade] + ") "

		self.SetTargetName(nameFront + name)

		if app.ENABLE_INGAME_WIKI and self.dropInfoButton:
			if self.monsterVnum == 0:
				self.dropInfoButton.Hide()
			else:
				import ingamewikiconfig
				if self.monsterVnum:
					self.dropInfoButton.SetPosition(30, 12)
					self.dropInfoButton.SetWindowHorizontalAlignLeft()
					self.dropInfoButton.Show()
				else:
					self.dropInfoButton.Hide()

		if app.AUTO_HUNT_RUBINUM and self.infoImage:
			if is_stone:
				self.SetSize(250, 65)
				(textWidth, textHeight) = self.name.GetTextSize()
				self.infoImage.SetPosition((self.GetWidth() / 2)+40, 35)
				self.infoImage.SetWindowHorizontalAlignCenter()
				self.infoImage.Show()

				self.infoImageText.SetText(localeinfo.AUTO_STONE_HUNT_TEXT)
				self.infoImageText.SetPosition(2,1)
				self.infoImageText.Show()
			elif self.infoImage.IsShow():
				self.infoImage.Hide()

		# Show mission progress if this monster is a mission target
		if app.ENABLE_MISSION_QUEST and hasattr(self, 'missionProgressText'):
			missionProgress = missionhelper.GetMonsterMissionProgress(self.monsterVnum)
			if missionProgress:
				progress, maxProgress, categoryName = missionProgress
				self.missionProgressText.SetText("[%s] %d/%d" % (categoryName, progress, maxProgress))
				if is_stone:
					self.missionProgressText.SetPosition(150, 35)
				else:
					self.SetSize(200, 65)
					self.missionProgressText.SetPosition(180, 35)
				self.missionProgressText.SetHorizontalAlignLeft()
				self.missionProgressText.Show()
			else:
				self.missionProgressText.Hide()

	def GetTargetVID(self):
		return self.vid

	def GetTargetName(self):
		return self.nameString

	def SetTargetName(self, name):
		self.nameString = name
		self.nameLength = len(name)
		self.name.SetText(name)

	if app.ENABLE_VIEW_TARGET_DECIMAL_HP:
		def SetHP(self, hpPercentage, iMinHP, iMaxHP):
			if not self.hpGauge.IsShow():
				if app.ENABLE_VIEW_TARGET_PLAYER_HP:
					showingButtonCount = len(self.showingButtonList)
					if showingButtonCount < len(self.BUTTON_NAME_LIST):
						if chr.GetInstanceType(self.vid) == chr.INSTANCE_TYPE_PLAYER:
							self.SetSize(max(150 + 75 * 3, showingButtonCount * 75), self.GetHeight())
						else:
							self.SetSize(200 + 7 * self.nameLength, self.GetHeight())
					else:
						self.SetSize(200 + 7 * self.nameLength, self.GetHeight())
				else:
					self.SetSize(200 + 7 * self.nameLength, self.GetHeight())

				if localeinfo.IsARABIC():
					self.name.SetPosition(self.GetWidth() - 23, 13)
				else:
					self.name.SetPosition(23, 13)

				self.name.SetWindowHorizontalAlignLeft()
				self.name.SetHorizontalAlignLeft()
				if str(background.GetCurrentMapName()) == "metin2_map_deathmatch" and app.DEATHMATCH_MODE:
					self.name.Hide()
				else:
					self.name.Show()
				self.hpGauge.Show()
				self.UpdatePosition()

			self.hpGauge.SetPercentage(hpPercentage, 100)

			if osfinfo.PAST_HEALTH_ON_TARGET:
				self.oldPercentage = float(self.newPercentage)
				self.newPercentage = float(hpPercentage)

				self.hpGauge.SetPercentageBack(self.oldPercentage, 100)

			if app.ENABLE_VIEW_TARGET_DECIMAL_HP:
				iMinHPText = '.'.join([i - 3 < 0 and str(iMinHP)[:i] or str(iMinHP)[i-3:i] for i in range(len(str(iMinHP)) % 3, len(str(iMinHP))+1, 3) if i])
				iMaxHPText = '.'.join([i - 3 < 0 and str(iMaxHP)[:i] or str(iMaxHP)[i-3:i] for i in range(len(str(iMaxHP)) % 3, len(str(iMaxHP))+1, 3) if i])
				self.hpDecimal.SetText(str(iMinHPText) + "/" + str(iMaxHPText))
				(textWidth, textHeight) = self.hpDecimal.GetTextSize()
				if localeinfo.IsARABIC():
					self.hpDecimal.SetPosition(120 / 2 + textWidth / 2, -15)
				else:
					self.hpDecimal.SetPosition(130 / 2 - textWidth / 2, -15)

				self.hpDecimal.Show()
	else:
		def SetHP(self, hpPercentage):
			if not self.hpGauge.IsShow():
				if app.ENABLE_VIEW_TARGET_PLAYER_HP:
					showingButtonCount = len(self.showingButtonList)
					if showingButtonCount > 0:
						if chr.GetInstanceType(self.GetTargetVID) != chr.INSTANCE_TYPE_PLAYER:
							if showingButtonCount != 1:
								self.SetSize(max(150, showingButtonCount * 75), self.GetHeight())
							else:
								self.SetSize(max(150, 2 * 75), self.GetHeight())
						else:
							self.SetSize(200 + 7 * self.nameLength, self.GetHeight())
					else:
						self.SetSize(200 + 7 * self.nameLength, self.GetHeight())
				else:
					self.SetSize(200 + 7 * self.nameLength, self.GetHeight())

				if localeinfo.IsARABIC():
					self.name.SetPosition(self.GetWidth() - 23, 13)
				else:
					self.name.SetPosition(23, 13)

				self.name.SetWindowHorizontalAlignLeft()
				self.name.SetHorizontalAlignLeft()
				self.hpGauge.Show()
				self.UpdatePosition()

			if osfinfo.PAST_HEALTH_ON_TARGET:
				if self.oldPercentage > self.newPercentage:
					self.oldPercentage = self.oldPercentage - 0.5
					self.hpGauge.SetPercentageBack(self.oldPercentage, 100)
				else:
					self.hpGauge.SetPercentage(hpPercentage, 100)
			else:
				self.hpGauge.SetPercentage(hpPercentage, 100)

	def ShowDefaultButton(self):
		self.isShowButton = True
		self.showingButtonList.append(self.buttonDict[localeinfo.TARGET_BUTTON_WHISPER])
		self.showingButtonList.append(self.buttonDict[localeinfo.TARGET_BUTTON_EXCHANGE])
		self.showingButtonList.append(self.buttonDict[localeinfo.TARGET_BUTTON_FIGHT])
		self.showingButtonList.append(self.buttonDict[localeinfo.TARGET_BUTTON_EMOTION_ALLOW])
		for button in self.showingButtonList:
			button.Show()

	def HideAllButton(self):
		self.isShowButton = False
		for button in self.showingButtonList:
			button.Hide()
		self.showingButtonList = []

	def __ShowButton(self, name):
		if not self.buttonDict.has_key(name):
			return

		self.buttonDict[name].Show()
		self.showingButtonList.append(self.buttonDict[name])

	def __HideButton(self, name):
		if not self.buttonDict.has_key(name):
			return

		button = self.buttonDict[name]
		button.Hide()

		for btnInList in self.showingButtonList:
			if btnInList == button:
				self.showingButtonList.remove(button)
				break

	def OnWhisper(self):
		if None != self.eventWhisper:
			self.eventWhisper(self.nameString)

	def OnExchange(self):
		net.SendExchangeStartPacket(self.vid)

	def OnPVP(self):
		if app.ENABLE_RENEWAL_PVP:
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.OpenPvPFirst(self.nameString, self.vid)
		else:
			net.SendChatPacket("/pvp %d" % (self.vid))

	def OnAppendToMessenger(self):
		if app.ENABLE_COMMUNITY_SYSTEM:
			net.SendCommunityRequestByVID(self.vid)
		else:
			net.SendMessengerAddByVIDPacket(self.vid)

	def OnPartyInvite(self):
		net.SendPartyInvitePacket(self.vid)

	def OnPartyExit(self):
		net.SendPartyExitPacket()

	def OnPartyRemove(self):
		pid = player.PartyMemberVIDToPID(self.vid)
		if pid:
			net.SendPartyRemovePacket(pid)

	def OnPartyPassLeader(self):
		if self.nameString:
			net.SendChatPacket("/party_leader " + self.nameString)

	def __OnGuildAddMember(self):
		net.SendGuildAddMemberPacket(self.vid)

	def __OnDismount(self):
		net.SendChatPacket("/unmount")

	def __OnExitObserver(self):
		net.SendChatPacket("/observer_exit")

	def __OnViewEquipment(self):
		net.SendChatPacket("/view_equip " + str(self.vid))

	def __OnRequestParty(self):
		net.SendChatPacket("/party_request " + str(self.vid))

	def __OnDestroyBuilding(self):
		net.SendChatPacket("/build d %d" % (self.vid))

	def __OnEmotionAllow(self):
		net.SendChatPacket("/emotion_allow %d" % (self.vid))

	def __OnVoteBlockChat(self):
		cmd = "/vote_block_chat %s" % (self.nameString)
		net.SendChatPacket(cmd)

	def OnPressEscapeKey(self):
		self.OnPressedCloseButton()
		return True

	def IsShowButton(self):
		return self.isShowButton

	if app.AUTO_HUNT_RUBINUM:
		def IsAutoHunt(self):
			return self.IsAutoHunt

	def RefreshButton(self):
		self.HideAllButton()
		if app.ENABLE_12ZI:
			if chrmgr.IsPC(self.vid) and chrmgr.IsDead(self.vid):
				if str(background.GetCurrentMapName()) in "metin2_12zi_stage":
					self.__ShowButton(localeinfo.TARGET_BUTTON_REVIVE)
					self.__ArrangeButtonPosition()
				# return
		if chr.INSTANCE_TYPE_BUILDING == chr.GetInstanceType(self.vid):
			#self.__ShowButton(localeinfo.TARGET_BUTTON_BUILDING_DESTROY)
			#self.__ArrangeButtonPosition()
			return

		if app.USE_PVP_TOURNAMENT and\
			chr.GetMapIndex() == pvp_tournament.MAP_INDEX:
			self.SetSize(200 + 7 * self.nameLength, 40)
			self.UpdatePosition()
			return

		if player.IsPVPInstance(self.vid) or player.IsObserverMode():
			# PVP_INFO_SIZE_BUG_FIX
			self.SetSize(200 + 7 * self.nameLength, 40)
			self.UpdatePosition()
			# END_OF_PVP_INFO_SIZE_BUG_FIX
			return

		self.ShowDefaultButton()

		if guild.MainPlayerHasAuthority(guild.AUTH_ADD_MEMBER):
			if not guild.IsMemberByName(self.nameString):
				if 0 == chr.GetGuildID(self.vid):
					self.__ShowButton(localeinfo.TARGET_BUTTON_INVITE_GUILD)

		if app.ENABLE_COMMUNITY_SYSTEM:
			isFriend = community.IsFriendByName(self.nameString)
			isBlocked = community.IsBlockByName(self.nameString)
		else:
			isFriend = messenger.IsFriendByName(self.nameString)
			isBlocked = app.ENABLE_MESSENGER_BLOCK and messenger.IsBlockFriendByName(self.nameString)

		if not isFriend:
			self.__ShowButton(localeinfo.TARGET_BUTTON_FRIEND)

		if app.ENABLE_MESSENGER_BLOCK:
			if not isBlocked:
				self.__ShowButton(localeinfo.TARGET_BUTTON_BLOCK)
			else:
				self.__ShowButton(localeinfo.TARGET_BUTTON_BLOCK_REMOVE)

		if player.IsPartyMember(self.vid):
			self.__HideButton(localeinfo.TARGET_BUTTON_FIGHT)

			if player.IsPartyLeader(self.vid):
				self.__ShowButton(localeinfo.TARGET_BUTTON_LEAVE_PARTY)
			elif player.IsPartyLeader(player.GetMainCharacterIndex()):
				self.__ShowButton(localeinfo.TARGET_BUTTON_EXCLUDE)
				self.__ShowButton(TARGET_BUTTON_PASS_LEADER)
		else:
			if player.IsPartyMember(player.GetMainCharacterIndex()):
				if player.IsPartyLeader(player.GetMainCharacterIndex()):
					self.__ShowButton(localeinfo.TARGET_BUTTON_INVITE_PARTY)
			else:
				if chr.IsPartyMember(self.vid):
					self.__ShowButton(localeinfo.TARGET_BUTTON_REQUEST_ENTER_PARTY)
				else:
					self.__ShowButton(localeinfo.TARGET_BUTTON_INVITE_PARTY)

			if player.IsRevengeInstance(self.vid):
				self.__HideButton(localeinfo.TARGET_BUTTON_FIGHT)
				self.__ShowButton(localeinfo.TARGET_BUTTON_AVENGE)
			elif player.IsChallengeInstance(self.vid):
				self.__HideButton(localeinfo.TARGET_BUTTON_FIGHT)
				self.__ShowButton(localeinfo.TARGET_BUTTON_ACCEPT_FIGHT)
			elif player.IsCantFightInstance(self.vid):
				self.__HideButton(localeinfo.TARGET_BUTTON_FIGHT)

			if not player.IsSameEmpire(self.vid):
				self.__HideButton(localeinfo.TARGET_BUTTON_INVITE_PARTY)
				self.__HideButton(localeinfo.TARGET_BUTTON_FRIEND)
				if background.GetCurrentMapName() != "metin2_map_desert_lava":
					self.__HideButton(localeinfo.TARGET_BUTTON_FIGHT)

		distance = player.GetCharacterDistance(self.vid)
		if distance > self.EXCHANGE_LIMIT_RANGE:
			self.__HideButton(localeinfo.TARGET_BUTTON_EXCHANGE)
			self.__ArrangeButtonPosition()

		self.__ArrangeButtonPosition()

	def __ArrangeButtonPosition(self):
		showingButtonCount = len(self.showingButtonList)

		pos = -(showingButtonCount / 2) * 68
		if 0 == showingButtonCount % 2:
			pos += 34

		for button in self.showingButtonList:
			button.SetPosition(pos, 33)
			pos += 68

		if app.ENABLE_VIEW_TARGET_PLAYER_HP:
			if showingButtonCount <= 2:
				self.SetSize(max(150 + 125, showingButtonCount * 75), 65)
			else:
				self.SetSize(max(150, showingButtonCount * 75), 65)
		else:
			self.SetSize(max(150, showingButtonCount * 75), 65)

		self.UpdatePosition()

	if app.ENABLE_DPS_METER:
		def __ResetDPSFight(self):
			self.dpsSmoothed = None
			self.dpsShownValue = None
			self.dpsLastHitCount = -1
			self.dpsLastDPS = 0
			self.dpsText.SetText("")
			self.hitsText.SetText("")

		def __PlaceDPSBadge(self):
			(bx, by) = self.GetLocalPosition()
			if localeinfo.IsARABIC():
				self.dpsBoard.SetPosition(int(bx - self.dpsBoard.GetWidth() - 4), int(by))
			else:
				xOff = 4
				if app.AUTO_HUNT_RUBINUM:
					wnd = getattr(self, "queueClearWnd", None)
					if wnd and wnd.IsShow():
						xOff = 67
				self.dpsBoard.SetPosition(int(bx + self.GetWidth() + xOff), int(by))

		def __UpdateDPSText(self, totalDamage, elapsedMS, hitCount):
			if hitCount != self.dpsLastHitCount:
				self.dpsLastHitCount = hitCount
				self.hitsText.SetText(HITS_TEXT % hitCount)
				if elapsedMS >= DPS_WARMUP_MS:
					self.dpsLastDPS = totalDamage * 1000 / elapsedMS

			if elapsedMS < DPS_WARMUP_MS:
				return

			trueDPS = totalDamage * 1000.0 / elapsedMS
			if self.dpsSmoothed is None:
				self.dpsSmoothed = trueDPS
			else:
				self.dpsSmoothed += (trueDPS - self.dpsSmoothed) * DPS_SMOOTH_FACTOR

			shown = self.dpsShownValue
			if shown is not None and abs(self.dpsSmoothed - shown) <= shown * DPS_CHANGE_THRESHOLD:
				return

			self.dpsShownValue = self.dpsSmoothed
			self.dpsText.SetText(DPS_TEXT % AbbreviateDPS(self.dpsSmoothed))

		def __RefreshDPSBadge(self):
			curTime = app.GetTime()
			if curTime < self.dpsNextPollTime:
				return
			self.dpsNextPollTime = curTime + DPS_POLL_INTERVAL

			(active, totalDamage, elapsedMS, hitCount) = player.GetTargetFightStats()
			targetVID = player.GetTargetVID()

			if active and self.IsShow():
				if self.dpsBoard.IsHolding():
					self.dpsBoard.CancelHold()
					self.__ResetDPSFight()
				if targetVID != self.dpsLastTargetVID or hitCount < self.dpsLastHitCount:
					self.__ResetDPSFight()
					self.dpsLastTargetVID = targetVID
				self.__UpdateDPSText(totalDamage, elapsedMS, hitCount)
				self.__PlaceDPSBadge()
				if not self.dpsBoard.IsShow():
					self.dpsBoard.Show()
				return

			if self.dpsBoard.IsHolding():
				return

			if self.dpsLastTargetVID and self.dpsLastTargetVID == targetVID and self.dpsShownValue is not None and self.dpsBoard.IsShow():
				self.dpsText.SetText(DPS_FINAL_TEXT % AbbreviateDPS(self.dpsLastDPS))
				self.dpsLastTargetVID = 0
				self.dpsBoard.StartHold()
				return

			self.dpsLastTargetVID = 0
			if self.dpsBoard.IsShow():
				self.dpsBoard.Hide()

		def OnDPSFightEnd(self, totalDamage, elapsedMS, hitCount, isBoss):
			dps = totalDamage * 1000 / elapsedMS
			summaryText = DPS_SUMMARY_TEXT
			if not isBoss:
				summaryText = DPS_SUMMARY_STONE_TEXT
			chat.AppendChat(chat.CHAT_TYPE_INFO, summaryText % (FormatFightTime(elapsedMS), AbbreviateNumber(dps), hitCount, AbbreviateNumber(totalDamage)))

			board = getattr(self, "dpsBoard", None)
			if not board:
				return

			self.dpsText.SetText(DPS_FINAL_TEXT % AbbreviateDPS(dps))
			self.hitsText.SetText(HITS_TEXT % hitCount)
			self.dpsLastTargetVID = 0
			self.dpsShownValue = None
			self.dpsSmoothed = None
			self.dpsLastHitCount = -1
			board.StartHold()
			if not board.IsShow():
				board.Show()

	def OnUpdate(self):
		if app.ENABLE_POISON_GAUGE_EFFECT:
			if self.hpGauge and self.hpGauge.IsShow():
				if chrmgr.HasAffectByVID(self.GetTargetVID(), chr.AFFECT_POISON):
					self.hpGauge.SetColor("lime")
				else:
					self.hpGauge.SetColor("red")

		if app.ENABLE_DPS_METER:
			self.__RefreshDPSBadge()

		if app.AUTO_HUNT_RUBINUM:
			self.__RefreshQueueClearButton()

		if self.isShowButton:
			exchangeButton = self.buttonDict[localeinfo.TARGET_BUTTON_EXCHANGE]
			distance = player.GetCharacterDistance(self.vid)

			if distance < 0:
				if app.WJ_NEW_USER_CARE:
					player.ClearTarget()
					self.Close()
				return

			if exchangeButton.IsShow():
				if distance > self.EXCHANGE_LIMIT_RANGE:
					self.RefreshButton()
			else:
				if distance < self.EXCHANGE_LIMIT_RANGE:
					self.RefreshButton()

	if app.ENABLE_MESSENGER_BLOCK:
		def __OnBlock(self):
			if app.ENABLE_COMMUNITY_SYSTEM:
				net.SendCommunityBlockAddByVID(self.vid)
			else:
				net.SendMessengerBlockAddByVIDPacket(self.vid)

		def __OnBlockRemove(self):
			self.questionDialog = uicommon.QuestionDialog()
			self.questionDialog.SetText(localeinfo.MESSENGER_DO_YOU_DELETE)
			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnBlockRemove))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnBlockRemoveClose))
			self.questionDialog.Open()

		def OnBlockRemove(self):
			blockName = chr.GetNameByVID(self.vid)
			if app.ENABLE_COMMUNITY_SYSTEM:
				net.SendCommunityBlockDelete(blockName)
			else:
				messenger.RemoveBlock(blockName)
				net.SendMessengerBlockRemoveByVIDPacket(blockName, blockName)
			self.OnBlockRemoveClose()

		def OnBlockRemoveClose(self):
			self.questionDialog.Close()
			self.questionDialog = None
			return True

	if app.ENABLE_ELEMENT_ADD:
		def AdjustPositionElementImage(self):
			if not self.elementImgList:
				return

			isShowButton = False
			if self.IsShowButton():
				isShowButton = True

			for button in self.showingButtonList:
				if button.IsShow():
					isShowButton = True
					break

			for element, elementImg in enumerate(self.elementImgList):
				elementImg.SetPosition((32 * element - 1), 65 if isShowButton else 40)
				elementImg.SetScale(self.ELEMENT_ENCHANT_ICON_SCALE, self.ELEMENT_ENCHANT_ICON_SCALE)
				elementImg.Show()

			if app.ENABLE_COMBAT_POINTS and self.cpGearValue > 0:
				self.__ShowCPDisplay()

		def ShowElementImg(self, element_enchants_dict):
			if all(value == 0 for value in element_enchants_dict.values()) or not element_enchants_dict:
				self.__HideAllElementImg()
				return

			elementDict = sorted(element_enchants_dict.items(), key = lambda item : item[1])
			elementDict.reverse()

			self.elementImgList = []
			for key, value in elementDict:
				if value <= 0:
					continue

				elementImg = ui.ExpandedImageBox()
				elementImg.SetParent(self)
				elementImg.LoadImage(self.ELEMENT_IMG_PATH[key])
				elementImg.Hide()

				self.elementImgList.append(elementImg)

			self.AdjustPositionElementImage()

		def __HideAllElementImg(self):
			if self.elementImgList:
				for elementImg in self.elementImgList:
					elementImg.Hide()
				self.elementImgList = []

	if app.ENABLE_12ZI:
		def __OnReviveQustionDialog(self):
			net.SendChatPacket("/revivedialog %d" % (self.vid))

		def OpenReviveDialog(self, vid, itemcount):
			self.questionDialog = uicommon.QuestionDialog2()
			if player.IsMainCharacterIndex(vid):
				self.questionDialog.SetText1(localeinfo.REVIVE_SELF_QUESTION1)
				self.questionDialog.SetText2(localeinfo.REVIVE_SELF_QUESTION2 % (itemcount))
			else:
				self.questionDialog.SetText1(localeinfo.REVIVE_QUESTION1 % chr.GetNameByVID(vid))
				self.questionDialog.SetText2(localeinfo.REVIVE_QUESTION2 % itemcount)

			self.questionDialog.SetAcceptEvent(lambda arg=vid: self.OnRivive(arg))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnQuestionDialogClose))
			self.questionDialog.Open()

		def OnRivive(self, virId):
			net.SendChatPacket("/revive %d" % (virId))
			self.OnQuestionDialogClose()

		def OnQuestionDialogClose(self):
			self.questionDialog.Close()
			self.questionDialog = None
			return True
