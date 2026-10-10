import ui
import localeinfo
import app
import item
import grp
import uiToolTip
import uiCommon
import dbg
import os
import wndMgr
import net
import math

STORY_PATH = "d:/ymir work/ui/game/saryong_story/"
ANIM_PATH  = STORY_PATH + "new_animation/"
OPEN_ANIM_PATH = STORY_PATH + "open_anim/"

START_FRAME_NUM = 0
END_FRAME_NUM   = 44
FRAME_SPEED     = 0.030

OPEN_ANIM_START = 0
OPEN_ANIM_END   = 25
OPEN_ANIM_SPEED = 0.04

MAX_REWARD_SLOTS = 4
DESC_LINE_LIMIT  = 48
DESC_LINE_HEIGHT = 16
DESC_CENTER_X    = 115 + 20

COLOR_R = 0.235
COLOR_G = 0.176
COLOR_B = 0.117

MODE_GLOBAL = 0
MODE_SINGLE = 1

CLIENT_CONFIG_PATHS = [
	"locale/ae/saryong_client.txt",
	"locale/ae/saryong_config.txt",
	"locale/romania/saryong_client.txt",
	"locale/romania/saryong_config.txt",
	"locale/en/saryong_client.txt",
	"locale/en/saryong_config.txt",
	"saryong_client.txt",
	"saryong_config.txt",
	"d:/ymir work/ui/game/saryong_story/saryong_client.txt",
	"d:/ymir work/ui/game/saryong_story/saryong_config.txt",
]


class SaryongStoryWindow(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.isLoaded = False

		## Modul curent (GLOBAL / SINGLE)
		self.currentMode = MODE_GLOBAL

		## GLOBAL — date de la server
		self.globalServerChapter     = 1
		self.globalServerProgress    = 0
		self.globalServerTarget      = 1
		self.globalPlayerLastClaimed = 0
		self.globalEndTime           = 0

		## SINGLE — date de la server
		self.singleServerChapter     = 1
		self.singleServerKills       = 0
		self.singleServerTarget      = 1
		self.singlePlayerLastClaimed = 0
		self.singleTotalChapters     = 0

		## Config client
		self.globalChapterData    = {}
		self.globalTotalChapters  = 0
		self.singleChapterData    = {}
		self.singleTotalFromConfig = 0

		## Pagina vizualizata (per mod)
		self.globalViewChapter = 1
		self.singleViewChapter = 1

		## Animatie
		self.isAnimating    = False
		self.animDirection  = 0
		self.animStartTime  = 0
		self.lastFrameIndex = -1

		## Animatie deschidere carte
		self.isOpenAnimating     = False
		self.openAnimStartTime   = 0
		self.openAnimLastFrame   = -1
		self.openAnimImg         = None

		## Animatie inchidere carte
		self.isCloseAnimating    = False
		self.closeAnimStartTime  = 0
		self.closeAnimLastFrame  = -1

		## UI state
		self.descLines       = []
		self.descHeight      = 0
		self.slotBackgrounds = []
		self.canClaim        = False
		self.toolTip         = None
		self.actionButtonMode = "claim"  ## "claim" | "start"
		self.startConfirmDialog = None
		self.wndWiki = None

		## Help guide
		self.btnHelp         = None
		self.helpTooltip     = None
		self.helpTooltipShown = False
		self.helpTextLines   = []

		## UI widgets
		self.bkImage = None
		self.imgAnimation = None
		self.bgClose = None
		self.btnClose = None
		self.bgTxt = None
		self.bgTxt2 = None
		self.textDecoLine = None
		self.chapterTitle = None
		self.titleDeco = None
		self.titleDeco2 = None
		self.subChapterTitle = None
		self.descViewport = None
		self.descContent = None
		self.descScrollBar = None
		self.bannerImg = None
		self.bgTasks = None
		self.taskTitle = None
		self.gaugeEmpty = None
		self.gaugeFull = None
		self.gaugeText = None
		self.timeText = None
		self.rewardGrid = None
		self.btnPrev = None
		self.btnNext = None
		self.btnAction = None
		self.loreText = None
		self.btnGlobal = None
		self.btnSingle = None

		## Ranking (always visible on right page)
		self.rankCrowns = []
		self.rankNames = []
		self.rankKills = []
		self.rankPrizeIcons = []
		self.rankPrizeCounts = []
		self.rankData = [("---", 0), ("---", 0), ("---", 0)]
		self.rankPrizes = [(0, 0), (0, 0), (0, 0)]
		self.playerContribution = 0
		self.playerContribText = None
		self.activeRankTooltip = -1

		self.AddFlag("movable")
		self.AddFlag("float")

		self.__LoadWindow()
		self.__LoadConfig()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()
		ui.ScriptWindow.Show(self)
		self.SetCenterPosition()
		self.SetTop()

		## Pornim animatia de deschidere
		self.isOpenAnimating   = True
		self.openAnimStartTime = app.GetTime()
		self.openAnimLastFrame = -1

		## Ascundem totul in timpul animatiei
		self.SetContentVisible(False)
		if self.bkImage:
			self.bkImage.Hide()
		if self.bgClose:
			self.bgClose.Hide()
		if self.btnClose:
			self.btnClose.Hide()
		if self.btnGlobal:
			self.btnGlobal.Hide()
		if self.btnSingle:
			self.btnSingle.Hide()
		if self.btnPrev:
			self.btnPrev.Hide()
		if self.btnNext:
			self.btnNext.Hide()
		if self.btnHelp:
			self.btnHelp.Hide()
		if self.helpTooltip:
			self.helpTooltip.Hide()
			self.helpTooltipShown = False

		## Aratam prima frame
		if self.openAnimImg:
			try:
				self.openAnimImg.LoadImage(OPEN_ANIM_PATH + "book_00000.png")
			except:
				pass
			self.openAnimImg.Show()
			self.openAnimImg.SetTop()

	def Open(self):
		self.Show()
		self.SetTop()

	def Close(self):
		if self.isOpenAnimating:
			self.isOpenAnimating = False
			if self.openAnimImg:
				self.openAnimImg.Hide()
			self.Hide()
			return

		if self.isCloseAnimating:
			return

		## Pornim animatia de inchidere
		self.isCloseAnimating   = True
		self.closeAnimStartTime = app.GetTime()
		self.closeAnimLastFrame = -1

		self.SetContentVisible(False)
		if self.bkImage:
			self.bkImage.Hide()
		if self.bgClose:
			self.bgClose.Hide()
		if self.btnClose:
			self.btnClose.Hide()
		if self.btnGlobal:
			self.btnGlobal.Hide()
		if self.btnSingle:
			self.btnSingle.Hide()
		if self.btnPrev:
			self.btnPrev.Hide()
		if self.btnNext:
			self.btnNext.Hide()
		if self.btnHelp:
			self.btnHelp.Hide()
		if self.helpTooltip:
			self.helpTooltip.Hide()
			self.helpTooltipShown = False
		self.activeRankTooltip = -1
		if self.toolTip:
			self.toolTip.HideToolTip()

		if self.openAnimImg:
			try:
				self.openAnimImg.LoadImage(OPEN_ANIM_PATH + "book_00025.png")
			except:
				pass
			self.openAnimImg.Show()
			self.openAnimImg.SetTop()

	def Destroy(self):
		self.ClearDictionary()
		self.toolTip = None
		self.globalChapterData = None
		self.singleChapterData = None
		self.slotBackgrounds = []
		self.descLines = []
		self.descViewport = None
		self.descContent = None
		self.descScrollBar = None
		self.rankCrowns = []
		self.rankNames = []
		self.rankKills = []
		self.rankPrizeIcons = []
		self.rankPrizeCounts = []
		self.playerContribText = None
		self.openAnimImg = None

	############################################################################
	#  Config Loader — parseaza ambele sectiuni din saryong_client.txt
	############################################################################

	def __LoadConfig(self):
		self.globalChapterData    = {}
		self.globalTotalChapters  = 0
		self.singleChapterData    = {}
		self.singleTotalFromConfig = 0

		lines = self.__ReadConfigFile()

		if not lines:
			self.globalChapterData = {
				1: {"Title": localeinfo.SARYONG_CFG_MISSING_TITLE, "SubTitle": localeinfo.SARYONG_CFG_MISSING_SUB,
					"Description": localeinfo.SARYONG_CFG_MISSING_DESC,
					"Image": "", "rewards": []},
			}
			self.globalTotalChapters = 1
			dbg.TraceError("SaryongStory: Config not found!")
			return

		self.globalChapterData, self.globalTotalChapters = \
			self.__ParseSection(lines, "SaryongClient")

		self.singleChapterData, self.singleTotalFromConfig = \
			self.__ParseSection(lines, "SaryongSingleClient")

	def __ReadConfigFile(self):
		for path in CLIENT_CONFIG_PATHS:
			if os.path.exists(path):
				try:
					f = open(path, "r")
					data = f.readlines()
					f.close()
					return data
				except IOError:
					continue

		try:
			import pack
			for path in CLIENT_CONFIG_PATHS:
				if pack.Exist(path):
					return pack.Get(path).split("\n")
		except:
			pass

		return []

	def __ParseSection(self, lines, sectionName):
		"""Parseaza o sectiune Group <sectionName> { ... } si returneaza (dict, totalChapters)."""
		chapterData   = {}
		totalChapters = 0

		inSection    = False
		inChapter    = False
		braceDepth   = 0
		currentGroup = ""
		tempData     = {}

		for rawLine in lines:
			line = rawLine.strip()
			if not line or line.startswith("#"):
				continue

			# Cautam Group <sectionName>
			if not inSection:
				if line.startswith("Group") and sectionName in line:
					inSection = True
				continue

			# { }
			if line == "{":
				braceDepth += 1
				continue

			if line == "}":
				if inChapter:
					try:
						chapNum = int(currentGroup.replace("Chapter", ""))
						chapterData[chapNum] = tempData.copy()
					except:
						pass
					inChapter = False
					currentGroup = ""
				braceDepth -= 1
				if braceDepth <= 0:
					inSection = False
					break
				continue

			# ChapterCount
			if line.startswith("ChapterCount"):
				try:
					totalChapters = int(line.split()[1])
				except:
					totalChapters = 1
				continue

			# Group ChapterN
			if line.startswith("Group") and "Chapter" in line:
				parts = line.split()
				if len(parts) > 1:
					currentGroup = parts[1]
					tempData = {"rewards": []}
					inChapter = True
				continue

			# Chei in interiorul unui capitol
			if not inChapter:
				continue

			if '"' in line:
				quoteStart = line.find('"')
				key = line[:quoteStart].strip()
				quoteEnd = line.rfind('"')
				if key and quoteStart + 1 < quoteEnd:
					tempData[key] = line[quoteStart + 1:quoteEnd]
			else:
				tokens = line.split()
				if len(tokens) < 2:
					continue
				key = tokens[0]
				if key == "Image":
					tempData["Image"] = tokens[1]
				elif key.startswith("Reward"):
					if len(tokens) >= 3:
						try:
							vnum  = int(tokens[1])
							count = int(tokens[2])
							if vnum > 0 and count > 0:
								tempData["rewards"].append((vnum, count))
						except:
							pass

		return chapterData, totalChapters

	############################################################################
	#  Server Data — primite prin BINARY_ handlers
	############################################################################

	def SetGlobalProgress(self, chapter, progress, target, endTime, duration, lastClaimed):
		self.globalServerChapter     = int(chapter)
		self.globalServerProgress    = int(progress)
		self.globalServerTarget      = int(target)
		self.globalPlayerLastClaimed = int(lastClaimed)
		self.globalDuration          = int(duration)

		iEnd = int(endTime)
		if iEnd > 0:
			self.globalEndTime = iEnd  ## server timestamp — fixed, survives relog
		elif int(duration) > 0:
			self.globalEndTime = 0     ## timer not started yet
		else:
			self.globalEndTime = 0     ## no time limit

		if self.IsShow() and self.currentMode == MODE_GLOBAL:
			self.RefreshTime()
			self.__UpdateState()

	def SetSingleProgress(self, chapter, kills, target, lastClaimed, totalChapters):
		self.singleServerChapter     = int(chapter)
		self.singleServerKills       = int(kills)
		self.singleServerTarget      = int(target)
		self.singlePlayerLastClaimed = int(lastClaimed)
		self.singleTotalChapters     = int(totalChapters)

		if self.IsShow() and self.currentMode == MODE_SINGLE:
			self.__UpdateState()

	def RefreshStateOnly(self):
		self.__UpdateState()

	############################################################################
	#  Mode Toggle
	############################################################################

	def SetModeGlobal(self):
		if self.currentMode == MODE_GLOBAL:
			return
		self.currentMode = MODE_GLOBAL
		self.__UpdateModeButtons()
		self.RefreshPageData()

	def SetModeSingle(self):
		if self.currentMode == MODE_SINGLE:
			return
		self.currentMode = MODE_SINGLE
		self.__UpdateModeButtons()
		self.RefreshPageData()

	def __UpdateModeButtons(self):
		if not self.btnGlobal or not self.btnSingle:
			return

		# Resetam ambele la starea clickable
		self.btnGlobal.SetUp()
		self.btnSingle.SetUp()

	############################################################################
	#  Ranking
	############################################################################

	def SetRanking(self, name1, kills1, name2, kills2, name3, kills3):
		self.rankData = [
			(str(name1), int(kills1)),
			(str(name2), int(kills2)),
			(str(name3), int(kills3)),
		]
		self.__RefreshRankingPanel()

	def __RefreshRankingVisibility(self):
		"""Show ranking on current and past global chapters; hide on future/locked and single mode."""
		viewChap = self.__GetViewChapter()
		realChap = self.__GetServerChapter()
		showRank = (self.currentMode == MODE_GLOBAL and viewChap <= realChap)

		for c in self.rankCrowns:
			if showRank: c.Show()
			else: c.Hide()
		for n in self.rankNames:
			if showRank: n.Show()
			else: n.Hide()
		for k in self.rankKills:
			if showRank: k.Show()
			else: k.Hide()
		for ic in self.rankPrizeIcons:
			if showRank: ic.Show()
			else: ic.Hide()
		for pc in self.rankPrizeCounts:
			if showRank: pc.Show()
			else: pc.Hide()
		if self.playerContribText:
			if showRank and self.playerContribution > 0:
				self.playerContribText.Show()
			else:
				self.playerContribText.Hide()

		if showRank:
			self.__RefreshRankingPanel()

	def __RefreshRankingPanel(self):
		if not self.rankNames:
			return

		## Don't show anything during animations or when viewing non-current chapter
		if self.isOpenAnimating or self.isCloseAnimating or self.isAnimating:
			return

		if self.currentMode != MODE_GLOBAL or self.__GetViewChapter() > self.__GetServerChapter():
			return

		RANK_COLORS = [
			(1.0, 0.84, 0.0),   ## 1st — gold
			(0.75, 0.75, 0.75),  ## 2nd — silver
			(0.80, 0.50, 0.20),  ## 3rd — bronze
		]

		for i in range(3):
			name, kills = self.rankData[i]
			vnum, count = self.rankPrizes[i]

			## Prize icon — always show if prize exists (ui.Button for click support)
			if vnum > 0 and i < len(self.rankPrizeIcons):
				try:
					item.SelectItem(vnum)
					iconPath = item.GetIconImageFileName()
					self.rankPrizeIcons[i].SetUpVisual(iconPath)
					self.rankPrizeIcons[i].SetOverVisual(iconPath)
					self.rankPrizeIcons[i].SetDownVisual(iconPath)
					self.rankPrizeIcons[i].Show()
				except:
					self.rankPrizeIcons[i].Hide()

				if i < len(self.rankPrizeCounts):
					self.rankPrizeCounts[i].SetText("x" + str(count))
					self.rankPrizeCounts[i].Show()
			else:
				if i < len(self.rankPrizeIcons):
					self.rankPrizeIcons[i].Hide()
				if i < len(self.rankPrizeCounts):
					self.rankPrizeCounts[i].Hide()

			## Player info
			r, g, b = RANK_COLORS[i]

			if name == "---" or kills <= 0:
				## Show crown only if there's a prize to display
				if vnum > 0:
					self.rankCrowns[i].Show()
				else:
					self.rankCrowns[i].Hide()
				self.rankNames[i].SetText("")
				self.rankNames[i].Hide()
				self.rankKills[i].SetText("")
				self.rankKills[i].Hide()
			else:
				self.rankCrowns[i].Show()
				self.rankNames[i].Show()
				self.rankKills[i].Show()
				displayName = name if len(name) <= 14 else name[:14] + ".."
				self.rankNames[i].SetText(displayName)
				self.rankNames[i].SetFontColor(r, g, b)
				self.rankKills[i].SetText(str(kills))
				self.rankKills[i].SetFontColor(r, g, b)

		## Player contribution
		if self.playerContribText:
			if self.playerContribution > 0:
				self.playerContribText.SetText(localeinfo.SARYONG_YOUR_CONTRIB + str(self.playerContribution))
				self.playerContribText.Show()
			else:
				self.playerContribText.SetText("")
				self.playerContribText.Hide()

	def SetRankPrizes(self, vnum1, count1, vnum2, count2, vnum3, count3):
		self.rankPrizes = [
			(int(vnum1), int(count1)),
			(int(vnum2), int(count2)),
			(int(vnum3), int(count3)),
		]
		self.__RefreshRankingPanel()

	def SetPlayerContribution(self, contrib):
		self.playerContribution = int(contrib)
		self.__RefreshRankingPanel()

	def __UpdateRankTooltip(self):
		if not self.rankPrizeIcons or not self.toolTip:
			return

		(xMouse, yMouse) = wndMgr.GetMousePosition()

		for i in xrange(3):
			if i >= len(self.rankPrizeIcons):
				break
			if not self.rankPrizeIcons[i].IsShow():
				continue

			vnum, count = self.rankPrizes[i]
			if vnum <= 0:
				continue

			try:
				(ix, iy) = self.rankPrizeIcons[i].GetGlobalPosition()
				iw = self.rankPrizeIcons[i].GetWidth()
				ih = self.rankPrizeIcons[i].GetHeight()
			except:
				continue

			if ix <= xMouse <= ix + iw + 30 and iy <= yMouse <= iy + ih:
				if self.activeRankTooltip != i:
					self.toolTip.ClearToolTip()
					self.toolTip.SetItemToolTip(vnum)
					if app.ENABLE_INGAME_WIKI and self.wndWiki:
						self.toolTip.DeclareShortcut(("key_lclick",), localeinfo.BIOLOG_MANAGER_CLICK_WIKI)
					self.toolTip.ShowToolTip()
					self.activeRankTooltip = i
				return

		if self.activeRankTooltip >= 0:
			self.toolTip.HideToolTip()
			self.activeRankTooltip = -1


	############################################################################
	#  Getteri mod-aware
	############################################################################

	def __GetChapterData(self):
		if self.currentMode == MODE_GLOBAL:
			return self.globalChapterData
		return self.singleChapterData

	def __GetTotalChapters(self):
		if self.currentMode == MODE_GLOBAL:
			return self.globalTotalChapters
		# Pentru single, folosim max(config, server)
		return max(self.singleTotalFromConfig, self.singleTotalChapters)

	def __GetViewChapter(self):
		if self.currentMode == MODE_GLOBAL:
			return self.globalViewChapter
		return self.singleViewChapter

	def __SetViewChapter(self, v):
		if self.currentMode == MODE_GLOBAL:
			self.globalViewChapter = v
		else:
			self.singleViewChapter = v

	def __GetServerChapter(self):
		if self.currentMode == MODE_GLOBAL:
			return self.globalServerChapter
		return self.singleServerChapter

	def __GetProgress(self):
		if self.currentMode == MODE_GLOBAL:
			return self.globalServerProgress
		return self.singleServerKills

	def __GetTarget(self):
		if self.currentMode == MODE_GLOBAL:
			return self.globalServerTarget
		return self.singleServerTarget

	def __GetLastClaimed(self):
		if self.currentMode == MODE_GLOBAL:
			return self.globalPlayerLastClaimed
		return self.singlePlayerLastClaimed

	############################################################################
	#  Refresh Pagina
	############################################################################

	def RefreshPageData(self):
		chapterData  = self.__GetChapterData()
		viewChapter  = self.__GetViewChapter()

		## Request ranking data for the viewed chapter (server sends hall of fame for past chapters)
		if self.currentMode == MODE_GLOBAL:
			net.SendChatPacket("/saryong_view_ranking " + str(viewChapter))

		if viewChapter not in chapterData:
			if self.chapterTitle:
				if self.currentMode == MODE_GLOBAL:
					self.chapterTitle.SetText(localeinfo.SARYONG_LABEL_CHAPTER + str(viewChapter))
				else:
					self.chapterTitle.SetText(localeinfo.SARYONG_LABEL_MISSION + str(viewChapter))
			return

		data = chapterData[viewChapter]

		if self.chapterTitle:
			self.chapterTitle.SetText(data.get("Title", ""))
		if self.subChapterTitle:
			self.subChapterTitle.SetText(data.get("SubTitle", ""))

		self.__RefreshDescription(data.get("Description", ""))
		self.__RefreshBannerImage(data.get("Image", ""))
		self.__RefreshRewardGrid(data.get("rewards", []))
		self.__RefreshRankingVisibility()
		self.__UpdateState()

	def __RefreshDescription(self, fullDesc):
		for line in self.descLines:
			line.Hide()
			line.Destroy()
		self.descLines = []

		if self.descContent:
			self.descContent.SetPosition(0, 0)
		if self.descScrollBar:
			self.descScrollBar.SetPos(0.0)

		linesList = self.__SplitText(fullDesc, DESC_LINE_LIMIT)
		textYPos  = 0

		for lineTxt in linesList:
			layer1 = ui.TextLine()
			layer1.SetParent(self.descContent)
			layer1.SetPosition(DESC_CENTER_X, textYPos)
			layer1.SetText(lineTxt)
			#layer1.SetFontName("Tahoma:13b")
			layer1.SetFontColor(COLOR_R, COLOR_G, COLOR_B)
			layer1.SetHorizontalAlignCenter()
			layer1.Show()
			self.descLines.append(layer1)

			layer2 = ui.TextLine()
			layer2.SetParent(self.descContent)
			layer2.SetPosition(DESC_CENTER_X + 1, textYPos)
			layer2.SetText(lineTxt)
			#layer2.SetFontName("Tahoma:13b")
			layer2.SetFontColor(COLOR_R, COLOR_G, COLOR_B)
			layer2.SetHorizontalAlignCenter()
			layer2.Show()
			self.descLines.append(layer2)

			textYPos += DESC_LINE_HEIGHT

		self.descHeight = textYPos

		if self.descViewport and self.descScrollBar:
			viewH = self.descViewport.GetHeight()
			if self.descHeight > viewH:
				self.descScrollBar.Show()
				self.descScrollBar.SetMiddleBarSize(float(viewH) / float(self.descHeight))
			else:
				self.descScrollBar.Hide()

	def __RefreshBannerImage(self, imgName):
		if not self.bannerImg:
			return
		if imgName:
			try:
				self.bannerImg.LoadImage(STORY_PATH + "img/" + imgName)
				self.bannerImg.Show()
			except:
				pass

	def __RefreshRewardGrid(self, rewards):
		if not self.rewardGrid:
			return
		for i in range(MAX_REWARD_SLOTS):
			self.rewardGrid.ClearSlot(i)
		for i in range(min(len(rewards), MAX_REWARD_SLOTS)):
			self.rewardGrid.SetItemSlot(i, rewards[i][0], rewards[i][1])

	############################################################################
	#  State Management
	############################################################################

	def __UpdateState(self):
		self.canClaim = False

		viewChap  = self.__GetViewChapter()
		realChap  = self.__GetServerChapter()
		myClaimed = self.__GetLastClaimed()

		# Slot backgrounds
		if viewChap <= myClaimed:
			slotImg = "slot_claim.png"
		elif viewChap > realChap:
			slotImg = "slot_lock.png"
		else:
			slotImg = "slot1.png"

		for bg in self.slotBackgrounds:
			bg.LoadImage(STORY_PATH + slotImg)

		# Capitol trecut
		if viewChap < realChap:
			self.__SetGauge(1.0, localeinfo.SARYONG_GAUGE_DONE)
			if viewChap > myClaimed:
				self.__SetActionBtn(localeinfo.SARYONG_BTN_CLAIM, True, 0xFFfdcb6e)
				self.canClaim = True
			else:
				self.__SetActionBtn(localeinfo.SARYONG_BTN_COMPLETE, False, 0xFF808080)

		# Capitol viitor (blocat)
		elif viewChap > realChap:
			self.__SetGauge(0.0, localeinfo.SARYONG_GAUGE_LOCKED)
			self.__SetActionBtn(localeinfo.SARYONG_BTN_LOCKED, False, 0xFF808080)

		# Capitol curent
		else:
			if viewChap <= myClaimed:
				self.__SetGauge(1.0, localeinfo.SARYONG_GAUGE_DONE)
				self.__SetActionBtn(localeinfo.SARYONG_BTN_COMPLETE, False, 0xFF808080)
				return

			current = self.__GetProgress()
			target  = max(self.__GetTarget(), 1)
			perc    = min(float(current) / float(target), 1.0)

			chData = self.__GetChapterData()
			missionLabel = chData.get(viewChap, {}).get("MissionLabel", "")
			if missionLabel:
				self.__SetGauge(perc, "%d / %d %s" % (current, target, missionLabel))
			else:
				self.__SetGauge(perc, "%d / %d" % (current, target))

			## Timer not started and no progress yet — show Start button (global only)
			if (self.currentMode == MODE_GLOBAL
				and self.globalEndTime <= 0
				and self.globalDuration > 0
				and current <= 0):
				self.actionButtonMode = "start"
				self.__SetActionBtn(localeinfo.SARYONG_BTN_START_CHAPTER, True, 0xFFfdcb6e)
				return

			self.actionButtonMode = "claim"
			if current >= target:
				self.__SetActionBtn(localeinfo.SARYONG_BTN_CLAIM, True, 0xFFfdcb6e)
				self.canClaim = True
			else:
				self.__SetActionBtn(localeinfo.SARYONG_BTN_IN_PROGRESS, False, 0xFFE6E6E6)

	def __SetGauge(self, pct, text):
		if self.gaugeFull:
			self.gaugeFull.SetRenderingRect(0.0, 0.0, -1.0 + pct, 0.0)
		if self.gaugeText:
			self.gaugeText.SetText(text)

	def __SetActionBtn(self, text, enabled, color):
		if not self.btnAction:
			return
		self.btnAction.SetText(text)
		self.btnAction.SetTextColor(color)
		self.btnAction.SetUpVisual(STORY_PATH + "btn_claim_norm.png")

		if enabled:
			self.btnAction.Enable()
			self.btnAction.EnableHoverPulse()
			self.btnAction.SetHoverPulseSpeed(1.5)  # 1.5 cycles per second
			if self.actionButtonMode == "start":
				self.btnAction.SetEvent(ui.__mem_func__(self.OnClickStart))
			else:
				self.btnAction.SetEvent(ui.__mem_func__(self.OnClickClaim))
		else:
			self.btnAction.Disable()
			self.btnAction.DisableHoverPulse()

	############################################################################
	#  Timer
	############################################################################

	def RefreshTime(self):
		if not self.timeText:
			return

		# In modul single nu avem timer
		if self.currentMode == MODE_SINGLE:
			viewChap = self.singleViewChapter
			realChap = self.singleServerChapter
			if viewChap > realChap:
				self.timeText.SetText(localeinfo.SARYONG_TIME_LOCKED)
				self.timeText.SetFontColor(0.5, 0.5, 0.5)
			elif viewChap < realChap:
				self.timeText.SetText(localeinfo.SARYONG_TIME_MISSION_DONE)
				self.timeText.SetFontColor(0.2, 0.6, 0.2)
			else:
				self.timeText.SetText(localeinfo.SARYONG_TIME_NO_LIMIT)
				self.timeText.SetFontColor(COLOR_R, COLOR_G, COLOR_B)
			return

		# Global — timer normal
		viewChap = self.globalViewChapter
		realChap = self.globalServerChapter

		if viewChap > realChap:
			self.timeText.SetText(localeinfo.SARYONG_TIME_LOCKED)
			self.timeText.SetFontColor(0.5, 0.5, 0.5)
			return

		if viewChap < realChap:
			self.timeText.SetText(localeinfo.SARYONG_TIME_PAGE_DONE)
			self.timeText.SetFontColor(0.2, 0.6, 0.2)
			return

		if self.globalDuration <= 0:
			self.timeText.SetText(localeinfo.SARYONG_TIME_NO_LIMIT)
			self.timeText.SetFontColor(COLOR_R, COLOR_G, COLOR_B)
			return

		if self.globalEndTime <= 0:
			## Timer not started yet — show duration + hint
			formatted = self.__FormatTime(self.globalDuration)
			self.timeText.SetText(formatted + " " + localeinfo.SARYONG_TIME_WAITING)
			self.timeText.SetFontColor(0.6, 0.5, 0.3)
			return

		## Timer running — calculate remaining from server end timestamp
		timeLeft = self.globalEndTime - app.GetGlobalTimeStamp()
		if timeLeft < 0:
			timeLeft = 0

		formatted = self.__FormatTime(timeLeft)
		self.timeText.SetText(localeinfo.SARYONG_TIME_REMAINING + formatted)

		if timeLeft <= 0:
			self.timeText.SetFontColor(1.0, 0.0, 0.0)
		else:
			self.timeText.SetFontColor(COLOR_R, COLOR_G, COLOR_B)

	def __FormatTime(self, seconds):
		if seconds <= 0:
			return localeinfo.SARYONG_TIME_EXPIRED
		m, s = divmod(seconds, 60)
		h, m = divmod(m, 60)
		if h >= 24:
			zile = int(h / 24)
			h = h % 24
			return localeinfo.SARYONG_TIME_DAYS_HOURS % (zile, h)
		return localeinfo.SARYONG_TIME_HOURS_MINS % (h, m)

	############################################################################
	#  User Actions
	############################################################################

	def OnClickClaim(self):
		if self.currentMode == MODE_GLOBAL:
			net.SendChatPacket("/saryong_claim")
		else:
			net.SendChatPacket("/saryong_single_claim")

	def OnClickStart(self):
		## Close any existing dialog first
		if self.startConfirmDialog:
			self.startConfirmDialog.Close()
			self.startConfirmDialog = None

		viewChap = self.__GetViewChapter()

		dialog = uiCommon.QuestionDialog()
		dialog.SetText(localeinfo.SARYONG_START_CONFIRM % viewChap)
		dialog.SetAcceptEvent(ui.__mem_func__(self.__OnConfirmStart))
		dialog.SetCancelEvent(ui.__mem_func__(self.__OnCancelStart))
		dialog.Open()
		self.startConfirmDialog = dialog

	def __OnConfirmStart(self):
		net.SendChatPacket("/saryong_start_chapter")
		if self.startConfirmDialog:
			self.startConfirmDialog.Close()
			self.startConfirmDialog = None
		return True

	def __OnCancelStart(self):
		if self.startConfirmDialog:
			self.startConfirmDialog.Close()
			self.startConfirmDialog = None
		return True

	def ChangeChapter(self, direction):
		if self.isAnimating:
			return

		viewChap = self.__GetViewChapter()
		total    = self.__GetTotalChapters()
		nextChap = viewChap + direction

		if nextChap < 1 or nextChap > total:
			return

		self.__SetViewChapter(nextChap)

		self.isAnimating    = True
		self.animStartTime  = app.GetTime()
		self.animDirection  = direction
		self.lastFrameIndex = -1

		self.SetContentVisible(False)
		self.activeRankTooltip = -1
		if self.toolTip:
			self.toolTip.HideToolTip()
		## Keep bkImage visible — new animation overlays on top
		if self.imgAnimation:
			self.imgAnimation.Show()
			self.imgAnimation.SetTop()

	############################################################################
	#  Animation + Update Loop
	############################################################################

	def OnUpdate(self):
		if self.IsShow():
			self.RefreshTime()

		if self.isOpenAnimating:
			self.__UpdateOpenAnimation()
			return

		if self.isCloseAnimating:
			self.__UpdateCloseAnimation()
			return

		if self.isAnimating:
			self.__UpdateAnimation()

		if self.canClaim:
			self.__UpdateClaimBlink()

		if self.IsShow() and self.currentMode == MODE_GLOBAL and self.__GetViewChapter() <= self.__GetServerChapter():
			self.__UpdateRankTooltip()

	def __UpdateAnimation(self):
		timePassed  = app.GetTime() - self.animStartTime
		frameIdx    = int(timePassed / FRAME_SPEED)
		totalFrames = (END_FRAME_NUM - START_FRAME_NUM) + 1

		if frameIdx >= totalFrames:
			self.__FinishAnimation()
			return

		if frameIdx != self.lastFrameIndex:
			self.lastFrameIndex = frameIdx
			if self.animDirection == 1:
				actualNum = END_FRAME_NUM - frameIdx
			else:
				actualNum = START_FRAME_NUM + frameIdx
			if self.imgAnimation:
				self.imgAnimation.LoadImage(ANIM_PATH + "book_%05d.png" % actualNum)

	def __UpdateClaimBlink(self):
		t = app.GetTime()
		if (int(t * 2) % 2) == 0:
			self.btnAction.SetUpVisual(STORY_PATH + "btn_claim_hover.png")
		else:
			self.btnAction.SetUpVisual(STORY_PATH + "btn_claim_norm.png")

	def __UpdateOpenAnimation(self):
		timePassed = app.GetTime() - self.openAnimStartTime
		frameIdx   = int(timePassed / OPEN_ANIM_SPEED)
		totalFrames = (OPEN_ANIM_END - OPEN_ANIM_START) + 1

		if frameIdx >= totalFrames:
			self.__FinishOpenAnimation()
			return

		if frameIdx != self.openAnimLastFrame:
			self.openAnimLastFrame = frameIdx
			actualNum = OPEN_ANIM_START + frameIdx
			if self.openAnimImg:
				try:
					self.openAnimImg.LoadImage(OPEN_ANIM_PATH + "book_%05d.png" % actualNum)
				except:
					pass

	def __FinishOpenAnimation(self):
		self.isOpenAnimating = False
		if self.openAnimImg:
			self.openAnimImg.Hide()

		## Aratam cartea normala + toate butoanele
		if self.bkImage:
			self.bkImage.Show()
		if self.bgClose:
			self.bgClose.Show()
		if self.btnClose:
			self.btnClose.Show()
		if self.btnGlobal:
			self.btnGlobal.Hide()
		if self.btnSingle:
			self.btnSingle.Hide()
		if self.btnPrev:
			self.btnPrev.Show()
		if self.btnNext:
			self.btnNext.Show()
		if self.btnHelp:
			self.btnHelp.Show()

		## Default to current server chapter
		self.__SetViewChapter(self.__GetServerChapter())
		self.RefreshPageData()
		self.SetContentVisible(True)

	def __UpdateCloseAnimation(self):
		timePassed = app.GetTime() - self.closeAnimStartTime
		frameIdx   = int(timePassed / OPEN_ANIM_SPEED)
		totalFrames = (OPEN_ANIM_END - OPEN_ANIM_START) + 1

		if frameIdx >= totalFrames:
			self.__FinishCloseAnimation()
			return

		if frameIdx != self.closeAnimLastFrame:
			self.closeAnimLastFrame = frameIdx
			actualNum = OPEN_ANIM_END - frameIdx
			if self.openAnimImg:
				try:
					self.openAnimImg.LoadImage(OPEN_ANIM_PATH + "book_%05d.png" % actualNum)
				except:
					pass

	def __FinishCloseAnimation(self):
		self.isCloseAnimating = False
		if self.openAnimImg:
			self.openAnimImg.Hide()
		self.Hide()

	def __FinishAnimation(self):
		self.isAnimating = False
		if self.imgAnimation:
			self.imgAnimation.Hide()
		## bkImage stays visible — no need to re-show
		self.RefreshPageData()
		self.SetContentVisible(True)

	############################################################################
	#  Scroll
	############################################################################

	def OnMouseWheel(self, nLen):
		if not self.descScrollBar or not self.descScrollBar.IsShow():
			return False
		viewH = self.descViewport.GetHeight()
		contentH = self.descHeight
		if contentH <= viewH:
			return False
		stepSize = 48.0 / float(contentH - viewH)
		currentPos = self.descScrollBar.GetPos()
		if nLen > 0:
			currentPos -= stepSize
		else:
			currentPos += stepSize
		currentPos = max(0.0, min(1.0, currentPos))
		self.descScrollBar.SetPos(currentPos)
		self.OnScrollDesc()
		return True

	def OnRunMouseWheel(self, nLen):
		return self.OnMouseWheel(nLen)

	def OnScrollDesc(self):
		if not self.descViewport or not self.descScrollBar:
			return
		viewH = self.descViewport.GetHeight()
		if self.descHeight <= viewH:
			return
		pos = self.descScrollBar.GetPos()
		diff = self.descHeight - viewH
		moveY = int(diff * pos)
		self.descContent.SetPosition(0, -moveY)

	############################################################################
	#  Tooltip
	############################################################################

	def OverInItem(self, slotIndex):
		if not self.toolTip:
			return
		chapterData = self.__GetChapterData()
		viewChap    = self.__GetViewChapter()
		if viewChap not in chapterData:
			return
		rewards = chapterData[viewChap].get("rewards", [])
		if slotIndex < len(rewards):
			vnum = rewards[slotIndex][0]
			self.toolTip.ClearToolTip()
			self.toolTip.SetItemToolTip(vnum)
			if app.ENABLE_INGAME_WIKI and self.wndWiki:
				self.toolTip.DeclareShortcut(("key_lclick",), localeinfo.BIOLOG_MANAGER_CLICK_WIKI)
			self.toolTip.ShowToolTip()

	def OverOutItem(self):
		if self.toolTip:
			self.toolTip.HideToolTip()

	def OnSelectItemSlot(self, slotIndex):
		if not app.ENABLE_INGAME_WIKI or not self.wndWiki:
			return
		chapterData = self.__GetChapterData()
		viewChap    = self.__GetViewChapter()
		if viewChap not in chapterData:
			return
		rewards = chapterData[viewChap].get("rewards", [])
		if slotIndex < len(rewards):
			vnum = rewards[slotIndex][0]
			if vnum > 0:
				self.__OpenWikiPage(vnum)

	def SetWikiWindow(self, wndWiki):
		self.wndWiki = wndWiki

	def __OnClickRankPrize(self, idx):
		if not app.ENABLE_INGAME_WIKI or not self.wndWiki:
			return
		if idx < len(self.rankPrizes):
			vnum, count = self.rankPrizes[idx]
			if vnum > 0:
				self.__OpenWikiPage(vnum)

	def __OpenWikiPage(self, vnum):
		if not self.wndWiki:
			return
		if not self.wndWiki.IsShow():
			net.ToggleWikiWindow()
		self.wndWiki.CloseBaseWindows()
		self.wndWiki.OpenSpecialPage(None, vnum, False)

	############################################################################
	#  Help Guide
	############################################################################

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

	def __AddHelpLine(self, parent, yPos, text, color):
		textLine = ui.TextLine()
		textLine.SetParent(parent)
		textLine.SetPackedFontColor(color)
		textLine.SetText(text)
		textLine.SetOutline()
		textLine.SetFeather(False)
		if localeinfo.IsARABIC():
			textLine.SetPosition(parent.GetWidth() - 12, yPos)
		else:
			textLine.SetPosition(12, yPos)
		textLine.Show()
		return textLine

	def __BuildHelpTooltip(self):
		BOARD_WIDTH = 290
		TITLE   = 0xFFFFE3A9
		HEADER  = 0xFF6AD4FF
		TEXT    = 0xFFD2D2D2
		HIGHLIGHT = 0xFFFFCC00
		WARNING = 0xFFFF6666
		LINE_H  = 16
		GAP     = 8

		lines = []
		lines.append((localeinfo.SARYONG_HELP_TITLE, TITLE))
		lines.append(None)
		lines.append((localeinfo.SARYONG_HELP_OVERVIEW_H, HEADER))
		lines.append((localeinfo.SARYONG_HELP_OVERVIEW_1, TEXT))
		lines.append((localeinfo.SARYONG_HELP_OVERVIEW_2, TEXT))
		lines.append((localeinfo.SARYONG_HELP_OVERVIEW_3, TEXT))
		lines.append(None)
		lines.append((localeinfo.SARYONG_HELP_TIMER_H, HEADER))
		lines.append((localeinfo.SARYONG_HELP_TIMER_1, TEXT))
		lines.append((localeinfo.SARYONG_HELP_TIMER_2, TEXT))
		lines.append((localeinfo.SARYONG_HELP_TIMER_3, WARNING))
		lines.append(None)
		lines.append((localeinfo.SARYONG_HELP_CONTRIB_H, HEADER))
		lines.append((localeinfo.SARYONG_HELP_CONTRIB_1, TEXT))
		lines.append((localeinfo.SARYONG_HELP_CONTRIB_2, TEXT))
		lines.append((localeinfo.SARYONG_HELP_CONTRIB_3, HIGHLIGHT))
		lines.append(None)
		lines.append((localeinfo.SARYONG_HELP_CLAIM_H, HEADER))
		lines.append((localeinfo.SARYONG_HELP_CLAIM_1, TEXT))
		lines.append((localeinfo.SARYONG_HELP_CLAIM_2, TEXT))
		lines.append((localeinfo.SARYONG_HELP_CLAIM_3, WARNING))
		lines.append(None)
		lines.append((localeinfo.SARYONG_HELP_TYPES_H, HEADER))
		lines.append((localeinfo.SARYONG_HELP_TYPES_1, TEXT))
		lines.append((localeinfo.SARYONG_HELP_TYPES_2, TEXT))

		yPos = 10
		board = ui.ThinBoard("TOP_MOST")
		board.AddFlag("float")
		board.SetSize(BOARD_WIDTH, 100)
		self.helpTextLines = []

		for entry in lines:
			if entry is None:
				yPos += GAP
			else:
				text, color = entry
				tl = self.__AddHelpLine(board, yPos, text, color)
				self.helpTextLines.append(tl)
				yPos += LINE_H

		yPos += 10
		board.SetSize(BOARD_WIDTH, yPos)
		board.Hide()
		return board

	############################################################################
	#  Content Visibility
	############################################################################

	def SetContentVisible(self, isVisible):
		widgets = [
			self.bgTxt,self.bgTxt2, self.chapterTitle, self.titleDeco,self.titleDeco2,
			self.subChapterTitle,
			self.bannerImg, self.bgTasks,
			self.taskTitle, self.gaugeEmpty, self.timeText,
			self.rewardGrid, self.btnAction,
		]
		if isVisible:
			for w in widgets:
				if w: w.Show()
			if self.descViewport:
				self.descViewport.Show()
			if self.descScrollBar and self.descHeight > self.descViewport.GetHeight():
				self.descScrollBar.Show()
			for bg in self.slotBackgrounds:
				bg.Show()
			## Ranking visibility is controlled by __RefreshRankingVisibility
			## which is called from RefreshPageData
			self.__RefreshRankingVisibility()
		else:
			for w in widgets:
				if w: w.Hide()
			if self.descViewport:
				self.descViewport.Hide()
			if self.descScrollBar:
				self.descScrollBar.Hide()
			for bg in self.slotBackgrounds:
				bg.Hide()
			## Hide all ranking elements
			for c in self.rankCrowns:
				c.Hide()
			for n in self.rankNames:
				n.Hide()
			for k in self.rankKills:
				k.Hide()
			for ic in self.rankPrizeIcons:
				ic.Hide()
			for pc in self.rankPrizeCounts:
				pc.Hide()
			if self.playerContribText:
				self.playerContribText.Hide()

	############################################################################
	#  Utility
	############################################################################

	def __SplitText(self, text, limit=40):
		lines = []
		currentLine = ""
		words = text.split(" ")
		for word in words:
			if len(currentLine) + len(word) < limit:
				currentLine += word + " "
			else:
				lines.append(currentLine)
				currentLine = word + " "
		if currentLine.strip():
			lines.append(currentLine)
		return lines

	def OnPressEscapeKey(self):
		self.Close()

	############################################################################
	#  Window Builder
	############################################################################

	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = True

		try:
			self.SetSize(700, 450)
			self.SetCenterPosition()

			self.bkImage = ui.ImageBox()
			self.bkImage.SetParent(self)
			self.bkImage.SetPosition(0, 0)
			self.bkImage.LoadImage(STORY_PATH + "book.png")
			self.bkImage.AddFlag("not_pick")
			self.bkImage.Show()

			self.imgAnimation = ui.ImageBox()
			self.imgAnimation.SetParent(self)
			self.imgAnimation.SetPosition(-77, -62)
			self.imgAnimation.AddFlag("not_pick")
			self.imgAnimation.Hide()

			## Animatie deschidere carte
			self.openAnimImg = ui.ImageBox()
			self.openAnimImg.SetParent(self)
			self.openAnimImg.SetPosition(-77, -62)
			self.openAnimImg.AddFlag("not_pick")
			self.openAnimImg.Hide()

			self.bgClose = ui.ImageBox()
			self.bgClose.SetParent(self)
			self.bgClose.SetPosition(47, 4)
			self.bgClose.LoadImage(STORY_PATH + "bg_close.png")
			self.bgClose.Show()

			self.btnClose = ui.Button()
			self.btnClose.SetParent(self)
			self.btnClose.SetPosition(58, 11)
			self.btnClose.SetUpVisual(STORY_PATH + "btn_close_0.png")
			self.btnClose.SetOverVisual(STORY_PATH + "btn_close_1.png")
			self.btnClose.SetDownVisual(STORY_PATH + "btn_close_2.png")
			self.btnClose.SetEvent(ui.__mem_func__(self.Close))
			self.btnClose.Show()

			## ── HELP BUTTON ─────────────────────────────────────────
			self.btnHelp = ui.Button()
			self.btnHelp.SetParent(self)
			self.btnHelp.SetPosition(674, 18)
			self.btnHelp.SetUpVisual("d:/ymir work/ui/game/wheel/question_mark.png")
			self.btnHelp.SetOverVisual("d:/ymir work/ui/game/wheel/question_mark_glow.png")
			self.btnHelp.SetDownVisual("d:/ymir work/ui/game/wheel/question_mark_down.png")
			self.btnHelp.SetEvent(ui.__mem_func__(self.__ToggleHelpTooltip))
			self.btnHelp.Show()

			## ── MODE TOGGLE BUTTONS ──────────────────────────────────
			self.btnGlobal = ui.Button()
			self.btnGlobal.SetParent(self)
			self.btnGlobal.SetPosition(30, 35)
			self.btnGlobal.SetUpVisual(STORY_PATH + "global_icon.png")
			self.btnGlobal.SetOverVisual(STORY_PATH + "global_icon_1.png")
			self.btnGlobal.SetDownVisual(STORY_PATH + "global_icon_2.png")
			self.btnGlobal.SetToolTipText(localeinfo.SARYONG_TOOLTIP_GLOBAL)
			self.btnGlobal.SetEvent(ui.__mem_func__(self.SetModeGlobal))
			self.btnGlobal.Hide()

			self.btnSingle = ui.Button()
			self.btnSingle.SetParent(self)
			self.btnSingle.SetPosition(60, 35)
			self.btnSingle.SetUpVisual(STORY_PATH + "single_icon.png")
			self.btnSingle.SetOverVisual(STORY_PATH + "single_icon_1.png")
			self.btnSingle.SetDownVisual(STORY_PATH + "single_icon_2.png")
			self.btnSingle.SetToolTipText(localeinfo.SARYONG_TOOLTIP_SOLO)
			self.btnSingle.SetEvent(ui.__mem_func__(self.SetModeSingle))
			self.btnSingle.Hide()

			## ── RANKING (always visible on right page) ──────────────
			RANK_BASE_X = 420
			RANK_BASE_Y = 288 - 20
			RANK_ROW_H  = 42

			self.rankCrowns = []
			self.rankNames = []
			self.rankKills = []
			self.rankPrizeIcons = []
			self.rankPrizeCounts = []

			self.titleDeco2 = ui.ImageBox()
			self.titleDeco2.SetParent(self)
			self.titleDeco2.SetPosition(390, 250 - 30)
			self.titleDeco2.LoadImage(STORY_PATH + "title_deco.png")
			self.titleDeco2.Show()

			self.bgTxt2 = ui.ExpandedImageBox()
			self.bgTxt2.SetParent(self)
			self.bgTxt2.SetPosition(382, 245- 20)
			self.bgTxt2.LoadImage(STORY_PATH + "rankingbg.png")
			self.bgTxt2.Show()

			for i in range(3):
				yPos = RANK_BASE_Y + (i * RANK_ROW_H)

				crown = ui.ImageBox()
				crown.SetParent(self)
				crown.SetPosition(RANK_BASE_X, yPos + 3)
				try:
					crown.LoadImage(STORY_PATH + "locul" + str(i + 1) + ".png")
				except:
					pass
				crown.Hide()
				self.rankCrowns.append(crown)

				nameText = ui.TextLine()
				nameText.SetParent(self)
				nameText.SetPosition(RANK_BASE_X + 30, yPos + 5 + 3)
				nameText.SetText("---")
				nameText.SetFontName("Tahoma:12")
				nameText.SetHorizontalAlignRight()
				nameText.SetFontColor(0.5, 0.5, 0.5)
				nameText.Hide()
				self.rankNames.append(nameText)

				killText = ui.TextLine()
				killText.SetParent(self)
				killText.SetPosition(RANK_BASE_X + 140, yPos + 5 + 3)
				killText.SetText("")
				killText.SetFontName("Tahoma:12")
				killText.SetFontColor(0.5, 0.5, 0.5)
				killText.Hide()
				self.rankKills.append(killText)

				prizeIcon = ui.Button()
				prizeIcon.SetParent(self)
				prizeIcon.SetPosition(RANK_BASE_X + 185, yPos - 8)
				prizeIcon.SetEvent(lambda idx=i: self.__OnClickRankPrize(idx))
				prizeIcon.Hide()
				self.rankPrizeIcons.append(prizeIcon)

				prizeCount = ui.TextLine()
				prizeCount.SetParent(self)
				prizeCount.SetPosition(RANK_BASE_X + 218, yPos + 15)
				prizeCount.SetText("")
				prizeCount.SetFontName(localeinfo.UI_DEF_FONT)
				#prizeCount.SetFontColor(COLOR_R, COLOR_G, COLOR_B)
				prizeCount.SetOutline()
				prizeCount.Hide()
				self.rankPrizeCounts.append(prizeCount)




			## ── LEFT PAGE: Progress / Claim area ──────────────────
			self.bannerImg = ui.ImageBox()
			self.bannerImg.SetParent(self)
			self.bannerImg.SetPosition(51, 54)
			self.bannerImg.LoadImage(STORY_PATH + "img/small.png")
			self.bannerImg.Show()

			self.bgTasks = ui.ImageBox()
			self.bgTasks.SetParent(self)
			self.bgTasks.SetPosition(84, 113)
			self.bgTasks.LoadImage(STORY_PATH + "bg_tasks.png")
			self.bgTasks.Show()

			self.taskTitle = ui.TextLine()
			self.taskTitle.SetParent(self)
			self.taskTitle.SetPosition(195, 140 - 20)
			self.taskTitle.SetText(localeinfo.SARYONG_LABEL_OBJECTIVE)
			self.taskTitle.SetFontName("Tahoma:13b")
			self.taskTitle.SetFontColor(COLOR_R, COLOR_G, COLOR_B)
			self.taskTitle.SetHorizontalAlignCenter()
			self.taskTitle.Show()

			self.gaugeEmpty = ui.ImageBox()
			self.gaugeEmpty.SetParent(self)
			self.gaugeEmpty.SetPosition(75, 170 - 20)
			self.gaugeEmpty.LoadImage(STORY_PATH + "jaugebar_empty.png")
			self.gaugeEmpty.Show()

			self.gaugeFull = ui.ExpandedImageBox()
			self.gaugeFull.SetParent(self.gaugeEmpty)
			self.gaugeFull.SetPosition(0, 0)
			self.gaugeFull.LoadImage(STORY_PATH + "jaugebar_full.png")
			self.gaugeFull.Show()

			self.gaugeText = ui.TextLine()
			self.gaugeText.SetParent(self.gaugeEmpty)
			self.gaugeText.SetPosition(self.gaugeEmpty.GetWidth() / 2 + 10, 3)
			self.gaugeText.SetText("0 / 0")
			self.gaugeText.SetHorizontalAlignCenter()
			self.gaugeText.SetOutline()
			self.gaugeText.Show()

			self.timeText = ui.TextLine()
			self.timeText.SetParent(self)
			self.timeText.SetPosition(195, 220 - 20)
			self.timeText.SetText("")
			self.timeText.SetFontName("Tahoma:12b")
			self.timeText.SetFontColor(COLOR_R, COLOR_G, COLOR_B)
			self.timeText.SetHorizontalAlignCenter()
			self.timeText.Show()

			gridX = 240
			gridY = 250 - 20
			itemOffsetX = 10
			itemOffsetY = 5

			self.slotBackgrounds = []
			for i in range(MAX_REWARD_SLOTS):
				img = ui.ImageBox()
				img.SetParent(self)
				img.SetPosition(gridX - (i * 45), gridY)
				img.LoadImage(STORY_PATH + "slot1.png")
				img.Show()
				self.slotBackgrounds.append(img)

			self.rewardGrid = ui.GridSlotWindow()
			self.rewardGrid.SetParent(self)
			self.rewardGrid.SetPosition(105 + itemOffsetX, gridY + itemOffsetY)
			self.rewardGrid.ArrangeSlot(0, MAX_REWARD_SLOTS, 1, 32, 32, 13, 0)
			self.rewardGrid.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
			self.rewardGrid.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
			self.rewardGrid.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			self.rewardGrid.SetSelectItemSlotEvent(ui.__mem_func__(self.OnSelectItemSlot))
			self.rewardGrid.Show()

			self.btnAction = ui.Button()
			self.btnAction.SetParent(self)
			self.btnAction.SetPosition(130, 300 - 20)
			self.btnAction.SetUpVisual(STORY_PATH + "btn_claim_norm.png")
			self.btnAction.SetOverVisual(STORY_PATH + "btn_claim_hover.png")
			self.btnAction.SetDownVisual(STORY_PATH + "btn_claim_select.png")
			self.btnAction.SetText(localeinfo.SARYONG_BTN_CLAIM)
			self.btnAction.SetTextColor(0xFFE6E6E6)
			self.btnAction.Show()

			## Player contribution text
			self.playerContribText = ui.TextLine()
			self.playerContribText.SetParent(self)
			self.playerContribText.SetPosition(195, 340 - 20)
			self.playerContribText.SetText("")
			self.playerContribText.SetFontName("Tahoma:12b")
			self.playerContribText.SetFontColor(0.0, 184.0, 148.0)
			self.playerContribText.SetHorizontalAlignCenter()
			self.playerContribText.Hide()

			## ── SPINE SEPARATOR ─────────────────────────────────────
			self.textDecoLine = ui.Bar()
			self.textDecoLine.SetParent(self)
			self.textDecoLine.SetPosition(350, 155 - 20)
			self.textDecoLine.SetSize(2, 100)
			self.textDecoLine.SetColor(0xFF302010)
			self.textDecoLine.Hide()

			## ── RIGHT PAGE: Description / Lore area ─────────────────
			self.bgTxt = ui.ExpandedImageBox()
			self.bgTxt.SetParent(self)
			self.bgTxt.SetPosition(397, 73)
			self.bgTxt.LoadImage(STORY_PATH + "bg_txt.png")
			self.bgTxt.Show()

			self.chapterTitle = ui.TextLine()
			self.chapterTitle.SetParent(self)
			self.chapterTitle.SetPosition(515 + 25, 65 - 45)
			self.chapterTitle.SetText("")
			self.chapterTitle.SetFontName("Tahoma:14b")
			self.chapterTitle.SetHorizontalAlignCenter()
			self.chapterTitle.SetFontColor(COLOR_R, COLOR_G, COLOR_B)
			self.chapterTitle.Show()

			self.titleDeco = ui.ImageBox()
			self.titleDeco.SetParent(self)
			self.titleDeco.SetPosition(390, 52)
			self.titleDeco.LoadImage(STORY_PATH + "title_deco.png")
			self.titleDeco.Show()

			self.subChapterTitle = ui.TextLine()
			self.subChapterTitle.SetParent(self)
			self.subChapterTitle.SetPosition(515 + 25, 85 - 45)
			self.subChapterTitle.SetText("")
			self.subChapterTitle.SetFontName("Tahoma:13b")
			self.subChapterTitle.SetHorizontalAlignCenter()
			self.subChapterTitle.SetFontColor(COLOR_R, COLOR_G, COLOR_B)
			self.subChapterTitle.Show()

			self.descViewport = ui.Window()
			self.descViewport.SetParent(self)
			self.descViewport.SetPosition(395, 140 - 20)
			self.descViewport.SetSize(230, 120)
			self.descViewport.SetInsideRender(True)
			self.descViewport.Show()

			self.descContent = ui.Window()
			self.descContent.SetParent(self.descViewport)
			self.descContent.SetPosition(0, 0)
			self.descContent.SetSize(230, 120)
			self.descContent.Show()

			self.descScrollBar = ui.ScrollBar()
			self.descScrollBar.SetParent(self)
			self.descScrollBar.SetPosition(10000, 0)
			self.descScrollBar.SetScrollBarSize(120)
			self.descScrollBar.SetScrollEvent(ui.__mem_func__(self.OnScrollDesc))
			self.descScrollBar.Hide()

			self.loreText = ui.TextLine()
			self.loreText.Hide()

			## ── NAV BUTTONS ─────────────────────────────────────────
			self.btnPrev = ui.Button()
			self.btnPrev.SetParent(self)
			self.btnPrev.SetPosition(40, 386)
			self.btnPrev.SetUpVisual(STORY_PATH + "btn_page_l_0.png")
			self.btnPrev.SetOverVisual(STORY_PATH + "btn_page_l_1.png")
			self.btnPrev.SetDownVisual(STORY_PATH + "btn_page_l_2.png")
			self.btnPrev.SetToolTipText(localeinfo.SARYONG_BTN_PREV)
			self.btnPrev.SetEvent(lambda: self.ChangeChapter(-1))
			self.btnPrev.Show()

			self.btnNext = ui.Button()
			self.btnNext.SetParent(self)
			self.btnNext.SetPosition(630, 386)
			self.btnNext.SetUpVisual(STORY_PATH + "btn_page_r_0.png")
			self.btnNext.SetOverVisual(STORY_PATH + "btn_page_r_1.png")
			self.btnNext.SetDownVisual(STORY_PATH + "btn_page_r_2.png")
			self.btnNext.SetToolTipText(localeinfo.SARYONG_BTN_NEXT)
			self.btnNext.SetEvent(lambda: self.ChangeChapter(1))
			self.btnNext.Show()

			self.toolTip = uiToolTip.ItemToolTip()

		except Exception, e:
			import exception
			dbg.TraceError("SaryongStoryWindow Load Error: " + str(e))
			exception.Abort("SaryongStoryWindow.__LoadWindow")