# coding: latin_1

import app
import net
import player
import chat
import item
import ui
import localeinfo
import uitooltip
from _weakref import proxy
if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions
if app.ENABLE_INGAME_WIKI:
	import ingamewikiui

IMG_DIR = "d:/ymir work/ui/game/wb_rework/"

BOSS_VNUMS = {
	0: [4901, 4902, 4903],   # Arena 1
	1: [4911, 4912, 4913],   # Arena 2
}

BOSS_BTN_COUNT = 3
BOSS_LOCKED = [4903, 4913]

BOSS_NAMES = {
	4901: localeinfo.WORLDBOSS_NAME1,
	4902: localeinfo.WORLDBOSS_NAME2,
	4903: localeinfo.WORLDBOSS_NAME3,
	4904: localeinfo.WORLDBOSS_NAME4,
	4911: localeinfo.WORLDBOSS_NAME_1,
	4912: localeinfo.WORLDBOSS_NAME_2,
	4913: localeinfo.WORLDBOSS_NAME_3,
	4914: localeinfo.WORLDBOSS_NAME_4,
}
BOSS_NAMES[6790] = getattr(localeinfo, "GUILD_DUNGEON_BOSS_NAME", "White Dragon")
BOSS_NAMES[6791] = getattr(localeinfo, "GUILD_DUNGEON_BOSS_NAME", "White Dragon")

# Only reachable with ENABLE_WORLDBOSS_V3 off; with it on the row carries coins instead.
# Hardcoded English by construction, and V3 takes the respawn interval from worldboss.json.
BOSS_COOLDOWN = {
	4901: "4h", 4902: "6h", 4903: "24h", 4904: "24h",
	4911: "4h", 4912: "24h", 4913: "24h", 4914: "24h",
}

COIN_VNUMS = {
	4901: {0: 30931, 1: 30932},
	4902: {0: 30933, 1: 30934},
}

COIN_TAG = {0: "|cFF00BFFF", 1: "|cFFFF4444"}
COIN_COLOR = {0: 0xFF00BFFF, 1: 0xFFFF4444}

TIER_NAMES = {0: "-", 1: "I", 2: "II", 3: "III", 4: "IV"}
TIER_COLORS = {0: 0xFFFFFFFF, 1: 0xFFAAAAAA, 2: 0xFF4FC3F7, 3: 0xFFFFD54F, 4: 0xFFFF8A65}

class WorldBossSpawnAlert(ui.BoardWithTitleBar):
	ALERT_OFFSET_Y = 50

	def __init__(self, bossVnum, stackIndex=0, owner=None):
		ui.BoardWithTitleBar.__init__(self)

		self.bossVnum = bossVnum
		self.stackIndex = stackIndex
		self.dismissed = False
		self.owner = owner	# WorldBossWindow; used to flag persistent dismissal

		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetSize(220, 140)
		self.SetTitleName(BOSS_NAMES.get(self.bossVnum, "World Boss"))
		self.SetCloseEvent(self.__OnDismiss)

		self.__Build()

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def __Build(self):
		# Boss portrait image
		bossImg = ui.ImageBox()
		bossImg.SetParent(self)
		bossImg.LoadImage(IMG_DIR + "avail_%d_1.png" % self.bossVnum)
		bossImg.SetPosition(57, 32)
		bossImg.Show()
		self.bossImg = bossImg

		# Text
		infoText = ui.TextLine()
		infoText.SetParent(self)
		infoText.SetPosition(110, 72)
		infoText.SetHorizontalAlignCenter()
		infoText.SetText(localeinfo.WB_POPUPINFO)
		infoText.Show()
		self.infoText = infoText

		# Teleport button
		teleportBtn = ui.Button()
		teleportBtn.SetParent(self)
		teleportBtn.SetPosition(12, 92)
		teleportBtn.SetUpVisual(IMG_DIR + "btn_1.png")
		teleportBtn.SetOverVisual(IMG_DIR + "btn_2.png")
		teleportBtn.SetDownVisual(IMG_DIR + "btn_3.png")
		teleportBtn.SetText(localeinfo.TRACK_TELEPORT)
		teleportBtn.SAFE_SetEvent(self.__OnTeleport)
		teleportBtn.Show()
		self.teleportBtn = teleportBtn

		# Cancel button
		cancelBtn = ui.Button()
		cancelBtn.SetParent(self)
		cancelBtn.SetPosition(12 + 98 + 2, 92)
		cancelBtn.SetUpVisual(IMG_DIR + "btn_1.png")
		cancelBtn.SetOverVisual(IMG_DIR + "btn_2.png")
		cancelBtn.SetDownVisual(IMG_DIR + "btn_3.png")
		cancelBtn.SetText(localeinfo.RANKING_DONATE_CANCEL)
		cancelBtn.SAFE_SetEvent(self.__OnDismiss)
		cancelBtn.Show()
		self.cancelBtn = cancelBtn

	def __OnTeleport(self):
		net.SendChatPacket("/track_window teleport %d" % self.bossVnum)
		net.SendChatPacket("/wb_dismiss_alert %d" % self.bossVnum)
		self.dismissed = True
		if self.owner:
			self.owner.MarkBossDismissed(self.bossVnum)
		self.Hide()

	def __OnDismiss(self):
		net.SendChatPacket("/wb_dismiss_alert %d" % self.bossVnum)
		self.dismissed = True
		if self.owner:
			self.owner.MarkBossDismissed(self.bossVnum)
		self.Hide()

	def IsDismissed(self):
		return self.dismissed

	def Open(self):
		self.SetCenterPosition()
		(x, y) = self.GetLocalPosition()
		self.SetPosition(x, y + self.stackIndex * self.ALERT_OFFSET_Y)
		self.SetTop()
		self.Show()

	def Destroy(self):
		self.bossImg = None
		self.infoText = None
		self.teleportBtn = None
		self.cancelBtn = None

	def OnPressEscapeKey(self):
		self.__OnDismiss()
		return True


class GuildRaidSpawnAlert(WorldBossSpawnAlert):
	def __init__(self, bossVnum, stackIndex=0, owner=None, runId=0):
		self.runId = runId
		WorldBossSpawnAlert.__init__(self, bossVnum, stackIndex, owner)
		self.SetTitleName(getattr(localeinfo, "GUILD_DUNGEON_RAID_TITLE", "Guild Raid"))
		self.SetCloseEvent(self.__OnGuildDismiss)

	# the base __init__ calls this mangled name; replacing it keeps the worldboss-only
	# portrait asset and the /wb_* dismissal wiring out of the guild path
	def _WorldBossSpawnAlert__Build(self):
		bossImg = None
		try:
			img = ui.ImageBox()
			img.SetParent(self)
			img.LoadImage(IMG_DIR + "avail_%d_1.png" % self.bossVnum)
			img.SetPosition(57, 32)
			img.Show()
			bossImg = img
		except:
			bossImg = None
		self.bossImg = bossImg

		infoText = ui.TextLine()
		infoText.SetParent(self)
		infoText.SetPosition(110, 72)
		infoText.SetHorizontalAlignCenter()
		infoText.SetText(getattr(localeinfo, "GUILD_DUNGEON_POPUPINFO", "Your guild's raid has begun!"))
		infoText.Show()
		self.infoText = infoText

		joinBtn = ui.Button()
		joinBtn.SetParent(self)
		joinBtn.SetPosition(12, 92)
		joinBtn.SetUpVisual(IMG_DIR + "btn_1.png")
		joinBtn.SetOverVisual(IMG_DIR + "btn_2.png")
		joinBtn.SetDownVisual(IMG_DIR + "btn_3.png")
		joinBtn.SetText(getattr(localeinfo, "GUILD_DUNGEON_JOIN", "Join"))
		joinBtn.SAFE_SetEvent(self.__OnJoin)
		joinBtn.Show()
		self.teleportBtn = joinBtn

		cancelBtn = ui.Button()
		cancelBtn.SetParent(self)
		cancelBtn.SetPosition(12 + 98 + 2, 92)
		cancelBtn.SetUpVisual(IMG_DIR + "btn_1.png")
		cancelBtn.SetOverVisual(IMG_DIR + "btn_2.png")
		cancelBtn.SetDownVisual(IMG_DIR + "btn_3.png")
		cancelBtn.SetText(localeinfo.RANKING_DONATE_CANCEL)
		cancelBtn.SAFE_SetEvent(self.__OnGuildDismiss)
		cancelBtn.Show()
		self.cancelBtn = cancelBtn

	def __OnJoin(self):
		net.SendChatPacket("/gd_join")
		self.dismissed = True
		self.Hide()

	def __OnGuildDismiss(self):
		net.SendChatPacket("/gd_dismiss_alert %d" % self.runId)
		self.dismissed = True
		self.Hide()

	def OnPressEscapeKey(self):
		self.__OnGuildDismiss()
		return True


class WBRewardToolTip(ui.ThinBoard):
	# Reward preview rendered as a real ui.Table grid: [Place | Reward | Amount].
	# Item rewards show their icon in the Reward cell (ui.Table icon support);
	# affect/buff rewards show the affect string with the duration as the amount.
	PAD			= 12
	HEAD_H		= 22
	ROW_H		= 34
	TITLE_H		= 22
	SEP_H		= 6
	ICON_SIDE	= 28

	COL_PLACE_W	= 46
	COL_NAME_W	= 250
	COL_AMT_W	= 70
	INNER_W		= COL_PLACE_W + COL_NAME_W + COL_AMT_W
	WIDTH		= INNER_W + PAD * 2

	C_LINE		= 0xff4a5160	# visible grid lines (black is invisible on the dark board)
	C_HEAD_BG	= 0xff1c1c1c	# black column-header row
	C_ROW_BG	= 0x99000000	# base clean dark row (rank 4+)
	C_HEAD_TXT	= 0xffffd300
	C_CELL_TXT	= 0xffe8e8e8
	C_TITLE		= 0xfff2e6c1
	C_AFFECT	= 0xff7ed957

	# Soft podium: a faint rank-tinted wash over each group's rows (kept very
	# close to the base dark so it never looks muddy) + a bright gold/silver/
	# bronze place number.
	C_RANK_BG = {
		1: 0xd9241f14,	# faint gold
		2: 0xd9242424,	# faint silver (neutral dark gray, no blue cast)
		3: 0xd9241a12,	# faint bronze
	}
	C_RANK_TXT = {
		1: 0xffffd24a,	# gold
		2: 0xffd6dde6,	# silver
		3: 0xffd98a45,	# bronze
	}
	C_RANK_TXT_DEFAULT	= 0xffffd54f

	def __init__(self, owner=None):
		ui.ThinBoard.__init__(self, "TOP_MOST")
		self.AddFlag("not_pick")
		self.AddFlag("float")
		self.children = []
		self.owner = owner
		self.Hide()

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def Clear(self):
		for child in self.children:
			child.Hide()
		self.children = []

	def Destroy(self):
		self.Clear()

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

	def __CollectRows(self, bossVnum):
		rows = []
		lastPos = -1

		if getattr(app, "ENABLE_WORLDBOSS_V3", 0):
			rawRows = self.owner.rewardRows.get(bossVnum, []) if self.owner else []
			for rank, rtype, idx, val, dur in rawRows:
				placeText = "" if rank == lastPos else str(rank)
				lastPos = rank

				if rtype == player.RANK_REWARD_TYPE_ITEM:
					item.SelectItem(idx)
					rows.append({
						"pos": rank,
						"place": placeText,
						"name": item.GetItemName(),
						"amount": "x%d" % val,
						"icon": idx,
						"color": self.C_CELL_TXT,
					})
				elif rtype == player.RANK_REWARD_TYPE_AFFECT:
					rows.append({
						"pos": rank,
						"place": placeText,
						"name": uitooltip.GET_AFFECT_STRING(idx, val),
						"amount": localeinfo.SecondToDHMS(dur) if dur else "-",
						"icon": None,
						"color": self.C_AFFECT,
					})
			return rows

		for reward in player.GetWBReward(bossVnum):
			if not (reward.has_key("position") and reward.has_key("type") and reward.has_key("idx") and reward.has_key("val")):
				continue

			pos = reward["position"]
			placeText = "" if pos == lastPos else str(pos)
			lastPos = pos

			if reward["type"] == player.RANK_REWARD_TYPE_ITEM:
				item.SelectItem(reward["idx"])
				rows.append({
					"pos": pos,
					"place": placeText,
					"name": item.GetItemName(),
					"amount": "x%d" % reward["val"],
					"icon": reward["idx"],
					"color": self.C_CELL_TXT,
				})
			elif reward["type"] == player.RANK_REWARD_TYPE_AFFECT:
				duration = reward["duration"] if reward.has_key("duration") else 0
				rows.append({
					"pos": pos,
					"place": placeText,
					"name": uitooltip.GET_AFFECT_STRING(reward["idx"], reward["val"]),
					"amount": localeinfo.SecondToDHMS(duration) if duration else "-",
					"icon": None,
					"color": self.C_AFFECT,
				})
		return rows

	def __AppendSeparator(self, y):
		sep = ui.Line()
		sep.SetParent(self)
		sep.AddFlag("not_pick")
		sep.SetPosition(self.PAD, y)
		sep.SetSize(self.INNER_W, 0)
		sep.SetColor(self.C_LINE)
		sep.Show()
		self.children.append(sep)

	def Build(self, bossVnum):
		self.Clear()
		isAr = localeinfo.IsARABIC()

		y = self.PAD
		self.__AppendText(localeinfo.WB_REWARD_TITLE, y, self.C_TITLE)
		y += self.TITLE_H
		self.__AppendSeparator(y)
		y += self.SEP_H

		rows = self.__CollectRows(bossVnum)
		if not rows:
			self.__AppendText(localeinfo.RANK_NO_REWARD, y, self.C_CELL_TXT)
			self.SetSize(self.WIDTH, y + self.HEAD_H + self.PAD)
			return

		colors = [self.C_LINE, self.C_HEAD_BG, self.C_ROW_BG, self.C_HEAD_TXT, self.C_CELL_TXT]
		tbl = ui.Table(self.INNER_W, self.HEAD_H, colors)
		tbl.SetParent(self)
		tbl.SetPosition(self.PAD, y)

		headers = [localeinfo.WB_REWARD_COL_PLACE, localeinfo.WB_REWARD_COL_NAME, localeinfo.WB_REWARD_COL_AMOUNT]
		widths = [self.COL_PLACE_W, self.COL_NAME_W, self.COL_AMT_W]
		if isAr:
			headers = headers[::-1]
			widths = widths[::-1]
		tbl.set_columns(headers, widths)

		nameAlign = "horizontal:right" if isAr else "horizontal:left"
		for row in rows:
			pos = row["pos"]
			placeColor = self.C_RANK_TXT.get(pos, self.C_RANK_TXT_DEFAULT)
			rowBg = self.C_RANK_BG.get(pos, self.C_ROW_BG)
			data = [row["place"], row["name"], row["amount"]]
			icons = [None, row["icon"], None]
			cellColors = [placeColor, row["color"], row["color"]]
			aligns = ["all:center", nameAlign, "all:center"]
			if isAr:
				data = data[::-1]
				icons = icons[::-1]
				cellColors = cellColors[::-1]
				aligns = aligns[::-1]
			tbl.add_row(data, self.ROW_H, cellColors, aligns, icons, self.ICON_SIDE, rowBg)

		tbl.Show()
		self.children.append(tbl)

		self.SetSize(self.WIDTH, y + tbl.GetHeight() + self.PAD)

	def ShowNear(self, anchor):
		bx, by = anchor.GetGlobalPosition()
		self.SetPosition(bx, by + anchor.GetHeight() + 3)
		self.SetTop()
		self.Show()


class WorldBossWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.isLoaded = False
		self.trackWindow = None

		# Boss selection
		self.selectedBossVnum = 4901
		self.selectedArena = 0
		self.selectedBossIndex = 0

		# UI references
		self.bossButtons = []
		self.renderTarget = None
		self.rankRows = []
		self.rewardToolTip = None
		self.renderToolTip = None
		self.wikiInst = None
		self.meRow = None
		self.guildRaidAlert = None
		self.spawnAlerts = {}  # {bossVnum: WorldBossSpawnAlert} — destroyed on warp
		self.dismissedBosses = set()  # {bossVnum, ...} — persists across warps; cleared on boss death

		# Data storage
		self.myRankData = {}
		self.rankingPage = {}
		self.rankingPageInfo = {}
		self.dailyCap = {"used": 0, "max": 100}
		self.weeklyTimer = {"days": 0, "hours": 0, "minutes": 0}
		self.weeklyResetTimestamp = 0
		self.bossConfig = {}  # {vnum: {minDamageRank, damageDivisor, minPresenceSec, maxPointsPerFight}}
		self.rewardRows = {}  # {bossVnum: [(rank, type, idx, val, dur), ...]}
		self.rewardRowsComplete = {}  # {bossVnum: True}
		self.coinToolTip = None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def SetTrackWindow(self, trackWindow):
		if trackWindow:
			self.trackWindow = proxy(trackWindow)

	def BindWikiInst(self, wikiInst):
		if wikiInst:
			self.wikiInst = proxy(wikiInst)

	def Destroy(self):
		self.trackWindow = None
		self.bossButtons = []
		self.rankRows = []
		self.meRow = None
		if self.renderTarget:
			del self.renderTarget
			self.renderTarget = None
		for alert in self.spawnAlerts.values():
			alert.Destroy()
		self.spawnAlerts = {}
		if self.guildRaidAlert:
			self.guildRaidAlert.Destroy()
			self.guildRaidAlert = None
		if self.rewardToolTip:
			self.rewardToolTip.Destroy()
			self.rewardToolTip = None
		self.myRankData = {}
		self.rankingPage = {}
		self.rankingPageInfo = {}
		self.rewardRows = {}
		self.rewardRowsComplete = {}
		self.coinToolTip = None
		self.isLoaded = False
		self.ClearDictionary()

	# ============================================================
	# Window loading — Step 3: bg + titlebar + boss buttons + render
	# ============================================================
	def __LoadWindow(self):
		if self.isLoaded:
			return

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/worldbosswindow_v2.py")
		except:
			import exception
			exception.Abort("WorldBossWindow.__LoadWindow")
			return

		self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))

		# Boss selector buttons (3 visible + 1 hidden)
		for i in xrange(4):
			btn = self.GetChild("boss_btn_%d" % i)
			if i < BOSS_BTN_COUNT:
				btn.SAFE_SetEvent(self.__OnClickBoss, i)
			else:
				btn.Hide()
			self.bossButtons.append(btn)

		# Teleport and Shop buttons
		self.GetChild("teleport_btn").SetEvent(ui.__mem_func__(self.__OnClickTeleport))
		self.GetChild("shop_btn").SetEvent(ui.__mem_func__(self.__OnClickShop))

		# Reward info button (hover tooltip)
		rewardBtn = self.GetChild("reward_info_btn")
		rewardBtn.SetEventOverIn(ui.__mem_func__(self.__OnOverInReward))
		rewardBtn.SetEventOverOut(ui.__mem_func__(self.__OnOverOutReward))

		# Ranking rows — create text children on each row background
		self.rankRows = []
		for i in xrange(10):
			rowBg = self.GetChild("rank_row_%d" % i)

			rankNum = ui.TextLine()
			rankNum.SetParent(rowBg)
			rankNum.SetPosition(25, 3)
			rankNum.SetText("")
			rankNum.Show()

			nameText = ui.TextLine()
			nameText.SetParent(rowBg)
			nameText.SetPosition(40, 3)
			nameText.SetHorizontalAlignRight()
			nameText.SetText("")
			nameText.Show()

			dmgText = ui.TextLine()
			dmgText.SetParent(rowBg)
			dmgText.SetPosition(185, 3)
			dmgText.SetHorizontalAlignLeft()
			dmgText.SetText("")
			dmgText.Show()

			# Hide rank number for top 3 (row bg has built-in crown icons)
			self.rankRows.append({
				"bg": rowBg,
				"rank": rankNum,
				"name": nameText,
				"damage": dmgText,
			})

		# "Me" row
		meRowBg = self.GetChild("rank_row_me")

		meRankNum = ui.TextLine()
		meRankNum.SetParent(meRowBg)
		meRankNum.SetPosition(25, 3)
		meRankNum.SetText("#")
		meRankNum.Show()

		meNameText = ui.TextLine()
		meNameText.SetParent(meRowBg)
		meNameText.SetPosition(40, 3)
		meNameText.SetHorizontalAlignRight()
		meNameText.SetText("")
		meNameText.Show()

		meDmgText = ui.TextLine()
		meDmgText.SetParent(meRowBg)
		meDmgText.SetPosition(185, 3)
		meDmgText.SetHorizontalAlignLeft()
		meDmgText.SetText("")
		meDmgText.Show()

		self.meRow = {"bg": meRowBg, "rank": meRankNum, "name": meNameText, "damage": meDmgText}

		if getattr(app, "ENABLE_WORLDBOSS_V3", 0):
			coinHover = self.GetChild("coin_hover")
			coinHover.SetOverInEvent(ui.__mem_func__(self.__OnOverInCoins))
			coinHover.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutCoins))
		else:
			self.GetChild("coin_label").SetText(localeinfo.WB_COOLDOWN)
			coinValue = self.GetChild("coin_value")
			coinValue.SetHorizontalAlignCenter()
			coinValue.SetPackedFontColor(0xFFb1aa8c)

		self.__RefreshBossButtons(True)
		self.__SetBossRender(self.selectedBossVnum)

		self.isLoaded = True

	# ============================================================
	# Boss selection
	# ============================================================
	def __OnClickBoss(self, index):
		bossList = BOSS_VNUMS.get(self.selectedArena, [])
		if index >= len(bossList):
			return

		if bossList[index] in BOSS_LOCKED:
			return

		self.selectedBossIndex = index
		self.selectedBossVnum = bossList[index]

		self.__RefreshBossButtons(True)
		self.__SetBossRender(self.selectedBossVnum)
		self.__RefreshBossInfo()
		self.__RefreshContribution()

		# Clear old ranking data so stale entries don't show
		self.rankingPage[self.selectedBossVnum] = []
		self.__RefreshRanking()

		# Request fresh data from server
		self.RequestMyRank(self.selectedBossVnum)
		self.RequestRankingPage(self.selectedBossVnum, 0, 0)
		self.RequestRewardInfo(self.selectedBossVnum)

	def __RefreshBossButtons(self, force=False):
		bossList = BOSS_VNUMS.get(self.selectedArena, [])
		for i, btn in enumerate(self.bossButtons):
			if i >= len(bossList):
				btn.Hide()
				continue

			vnum = bossList[i]
			isLocked = vnum in BOSS_LOCKED

			if isLocked:
				stateKey = "locked_%d" % vnum
				if not force and hasattr(btn, "_lastState") and btn._lastState == stateKey:
					continue

				btn._lastState = stateKey
				btn.SetUpVisual(IMG_DIR + "btn_boss_locked.png")
				btn.SetOverVisual(IMG_DIR + "btn_boss_locked.png")
				btn.SetDownVisual(IMG_DIR + "btn_boss_locked.png")
				btn.Show()
				continue

			isAlive = self.__IsBossAlive(vnum)
			isSelected = (i == self.selectedBossIndex)
			prefix = "avail" if isAlive else "dead"

			stateKey = "%s_%d_%d" % (prefix, vnum, isSelected)
			if not force and hasattr(btn, "_lastState") and btn._lastState == stateKey:
				continue

			btn._lastState = stateKey

			if isSelected:
				btn.SetUpVisual(IMG_DIR + "%s_%d_3.png" % (prefix, vnum))
				btn.SetOverVisual(IMG_DIR + "%s_%d_3.png" % (prefix, vnum))
				btn.SetDownVisual(IMG_DIR + "%s_%d_3.png" % (prefix, vnum))
			else:
				btn.SetUpVisual(IMG_DIR + "%s_%d_1.png" % (prefix, vnum))
				btn.SetOverVisual(IMG_DIR + "%s_%d_2.png" % (prefix, vnum))
				btn.SetDownVisual(IMG_DIR + "%s_%d_3.png" % (prefix, vnum))

			btn.Show()

	def __IsBossAlive(self, bossVnum):
		if not self.trackWindow:
			return False

		for data in self.trackWindow._TrackWindow__dataDict:
			if data["bossVnum"] == bossVnum:
				return data["status"]

		return False

	def __SetBossRender(self, bossVnum):
		if not app.ENABLE_INGAME_WIKI:
			return

		renderWindow = self.GetChild("boss_render_window")

		if self.renderTarget:
			del self.renderTarget
			self.renderTarget = None

		rt = ingamewikiui.WikiRenderTarget(renderWindow.GetWidth(), renderWindow.GetHeight())
		rt.SetParent(renderWindow)
		rt.SetPosition(0, 0)
		rt.Show()
		rt.SetModel(bossVnum, True, False)
		self.renderTarget = rt

		# Recreate click overlay on top of render target every time
		# (render target eats mouse events, overlay must be on top)
		if hasattr(self, "renderClickOverlay") and self.renderClickOverlay:
			self.renderClickOverlay.Hide()
			del self.renderClickOverlay
			self.renderClickOverlay = None

		overlay = ui.Window()
		overlay.SetParent(renderWindow)
		overlay.SetSize(renderWindow.GetWidth(), renderWindow.GetHeight())
		overlay.SetPosition(0, 0)
		overlay.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.__OnClickBossRender))
		overlay.SetOverInEvent(ui.__mem_func__(self.__OnOverInRender))
		overlay.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutRender))
		overlay.Show()
		self.renderClickOverlay = overlay

	def __GetModeBadgeText(self, data):
		if not getattr(app, "ENABLE_WORLDBOSS_V3", 0):
			return ""
		mode = data.get("nextMode", -1)
		if mode == 0:
			return "  |cFF00BFFF[%s]" % getattr(localeinfo, "WB_MODE_PVM", "PvM")
		if mode == 1:
			return "  |cFFFF4444[%s]" % getattr(localeinfo, "WB_MODE_PVP", "PvP")
		return ""

	def __RefreshBossInfo(self):
		vnum = self.selectedBossVnum

		# Boss name
		self.GetChild("boss_name_text").SetText(BOSS_NAMES.get(vnum, ""))

		# Status + Timer from track window
		if self.trackWindow:
			for data in self.trackWindow._TrackWindow__dataDict:
				if data["bossVnum"] == vnum:
					if data["status"]:
						self.GetChild("status_img").LoadImage(IMG_DIR + "alive.png")
						self.GetChild("timer_value").SetText("-" + self.__GetModeBadgeText(data))
					else:
						leftTime = data["server_cooldown"] - app.GetGlobalTimeStamp()
						if leftTime > 0:
							self.GetChild("status_img").LoadImage(IMG_DIR + "dead.png")
							self.GetChild("timer_value").SetText(localeinfo.SecondToDHMS(leftTime) + self.__GetModeBadgeText(data))
						else:
							self.GetChild("status_img").LoadImage(IMG_DIR + "alive.png")
							self.GetChild("timer_value").SetText("-" + self.__GetModeBadgeText(data))
					return

		self.GetChild("status_img").LoadImage(IMG_DIR + "dead.png")
		self.GetChild("timer_value").SetText("-")

	def __RefreshWeeklyTimer(self):
		if self.weeklyResetTimestamp <= 0:
			self.GetChild("weekly_reset_text").SetText("")
			return

		leftTime = self.weeklyResetTimestamp - app.GetGlobalTimeStamp()
		if leftTime <= 0:
			self.GetChild("weekly_reset_text").SetText(localeinfo.WB_RESET_NOW)
			return

		days = leftTime / 86400
		hours = (leftTime % 86400) / 3600
		minutes = (leftTime % 3600) / 60
		seconds = leftTime % 60

		self.GetChild("weekly_reset_text").SetText(localeinfo.WB_RESET_TIMER % (days, hours, minutes, seconds))

	def __RefreshContribution(self):
		# WB Points
		self.GetChild("wb_points_value").SetText(str(player.GetWbPoints()))

		# Daily cap
		self.GetChild("daily_cap_value").SetText("%d/%d" % (self.dailyCap["used"], self.dailyCap["max"]))

		# Your damage + tier for selected boss
		data = self.myRankData.get(self.selectedBossVnum, None)
		if data and data["rank"] > 0:
			self.GetChild("your_damage_value").SetText(str(data["damage"]))
			self.GetChild("your_tier_value").SetText(TIER_NAMES.get(data["tier"], "-"))
			self.GetChild("your_tier_value").SetPackedFontColor(TIER_COLORS.get(data["tier"], 0xFFFFFFFF))
		else:
			self.GetChild("your_damage_value").SetText("0")
			self.GetChild("your_tier_value").SetText("-")
			self.GetChild("your_tier_value").SetPackedFontColor(0xFFFFFFFF)

		self.__RefreshCoinRow()

	def __RefreshCoinRow(self):
		if not getattr(app, "ENABLE_WORLDBOSS_V3", 0):
			self.GetChild("coin_value").SetText(BOSS_COOLDOWN.get(self.selectedBossVnum, ""))
			return

		coins = COIN_VNUMS.get(self.selectedBossVnum)
		if not coins:
			self.GetChild("coin_value").SetText("-")
			return

		self.GetChild("coin_value").SetText("%s%d|r / %s%d" % (
			COIN_TAG[0], player.GetItemCountByVnum(coins[0]),
			COIN_TAG[1], player.GetItemCountByVnum(coins[1])))

	def __OnOverInCoins(self):
		coins = COIN_VNUMS.get(self.selectedBossVnum)
		if not coins:
			return

		if not self.coinToolTip:
			self.coinToolTip = uitooltip.ToolTip()

		self.coinToolTip.ClearToolTip()
		self.coinToolTip.AppendSpace(5)
		for mode in (0, 1):
			item.SelectItem(coins[mode])
			self.coinToolTip.AutoAppendNewTextLineResize(
				"%s  x%d" % (item.GetItemName(), player.GetItemCountByVnum(coins[mode])),
				COIN_COLOR[mode])
		self.coinToolTip.AppendSpace(5)
		self.coinToolTip.ShowToolTip()

	def __OnOverOutCoins(self):
		if self.coinToolTip:
			self.coinToolTip.HideToolTip()

	def __RefreshRanking(self):
		entries = self.rankingPage.get(self.selectedBossVnum, [])

		for i in xrange(10):
			row = self.rankRows[i]
			if i < len(entries):
				e = entries[i]

				# Rank number: hide for top 3 (row bg has crown), show for 4+
				if e["rank"] <= 3:
					row["rank"].SetText("")
				else:
					row["rank"].SetText(str(e["rank"]))

				row["name"].SetText(e["name"][:14])
				row["damage"].SetText(self.__FormatNumber(e["damage"]))

				# Color: top 3 white, rest light gray
				color = 0xFFFFFFFF if e["rank"] <= 3 else 0xFFbdc3c7
				row["rank"].SetPackedFontColor(color)
				row["name"].SetPackedFontColor(color)
				row["damage"].SetPackedFontColor(color)

				# Swap row bg image for top 3
				if e["rank"] == 1:
					row["bg"].LoadImage(IMG_DIR + "1.png")
				elif e["rank"] == 2:
					row["bg"].LoadImage(IMG_DIR + "2.png")
				elif e["rank"] == 3:
					row["bg"].LoadImage(IMG_DIR + "3.png")
				else:
					row["bg"].LoadImage(IMG_DIR + "4.png")
			else:
				row["rank"].SetText("")
				row["name"].SetText("")
				row["damage"].SetText("")
				row["bg"].LoadImage(IMG_DIR + "4.png")

		# "Me" row
		if self.meRow:
			data = self.myRankData.get(self.selectedBossVnum, None)
			if data and data["rank"] > 0:
				self.meRow["rank"].SetText("#%d" % data["rank"])
				self.meRow["name"].SetText(player.GetName())
				self.meRow["damage"].SetText(self.__FormatNumber(data["damage"]))
			else:
				self.meRow["rank"].SetText("#")
				self.meRow["name"].SetText(player.GetName())
				self.meRow["damage"].SetText("0")

	def __FormatNumber(self, n):
		"""Format number with dot separators: 1234567 -> 1.234.567"""
		s = str(n)
		result = []
		for i, c in enumerate(reversed(s)):
			if i > 0 and i % 3 == 0:
				result.append(".")
			result.append(c)
		return "".join(reversed(result))

	# ============================================================
	# Server command handlers
	# ============================================================
	def OnWBRankPage(self, bossVnum, page, weeksAgo, totalPages, totalEntries):
		bossVnum = int(bossVnum)
		self.rankingPageInfo[bossVnum] = {
			"page": int(page),
			"weeksAgo": int(weeksAgo),
			"totalPages": int(totalPages),
			"totalEntries": int(totalEntries),
		}
		self.rankingPage[bossVnum] = []

	def OnWBRankEntry(self, bossVnum, rank, name, guild, empire, damage, tier, fights):
		bossVnum = int(bossVnum)
		if bossVnum not in self.rankingPage:
			self.rankingPage[bossVnum] = []

		self.rankingPage[bossVnum].append({
			"rank": int(rank),
			"name": str(name),
			"guild": str(guild) if str(guild) != "-" else "",
			"empire": int(empire),
			"damage": int(damage),
			"tier": int(tier),
			"fights": int(fights),
		})

		if bossVnum == self.selectedBossVnum and self.isLoaded:
			self.__RefreshRanking()

	def OnWBBossConfig(self, bossVnum, minDamageRank, damageDivisor, minPresenceSec, maxPointsPerFight):
		self.bossConfig[int(bossVnum)] = {
			"minDamageRank": int(minDamageRank),
			"damageDivisor": int(damageDivisor),
			"minPresenceSec": int(minPresenceSec),
			"maxPointsPerFight": int(maxPointsPerFight),
		}

	def OnWBRewardRow(self, bossVnum, rank, rtype, idx, val, dur):
		self.rewardRows.setdefault(bossVnum, []).append((rank, rtype, idx, val, dur))

	def OnWBRewardEnd(self, bossVnum):
		self.rewardRowsComplete[bossVnum] = True

	def OnWBMyRank(self, bossVnum, rank, damage, tier, fights, gap):
		bossVnum = int(bossVnum)
		self.myRankData[bossVnum] = {
			"rank": int(rank),
			"damage": int(damage),
			"tier": int(tier),
			"fights": int(fights),
			"gap": int(gap),
		}
		if self.isLoaded:
			self.__RefreshContribution()

	def OnWBDailyCap(self, used, capMax):
		self.dailyCap["used"] = int(used)
		self.dailyCap["max"] = int(capMax)
		if self.isLoaded:
			self.__RefreshContribution()

	def OnWBWeeklyTimer(self, days, hours, minutes):
		self.weeklyTimer["days"] = int(days)
		self.weeklyTimer["hours"] = int(hours)
		self.weeklyTimer["minutes"] = int(minutes)
		# Store absolute reset timestamp for live countdown
		totalSeconds = int(days) * 86400 + int(hours) * 3600 + int(minutes) * 60
		self.weeklyResetTimestamp = app.GetGlobalTimeStamp() + totalSeconds
		if self.isLoaded:
			self.__RefreshWeeklyTimer()

	# ============================================================
	# Button handlers
	# ============================================================
	def __OnClickTeleport(self):
		net.SendChatPacket("/track_window teleport %d" % self.selectedBossVnum)

	def __OnClickShop(self):
		net.SendRemoteShopPacket(4)

	def __OnOverInReward(self):
		if not self.rewardToolTip:
			self.rewardToolTip = WBRewardToolTip(self)

		self.rewardToolTip.Build(self.selectedBossVnum)
		self.rewardToolTip.ShowNear(self.GetChild("reward_info_btn"))

	def __OnOverOutReward(self):
		if self.rewardToolTip:
			self.rewardToolTip.Hide()

	def __OnClickBossRender(self):
		if not app.ENABLE_INGAME_WIKI or not self.wikiInst:
			return

		if not self.wikiInst.IsShow():
			net.ToggleWikiWindow()

		self.wikiInst.CloseBaseWindows()
		self.wikiInst.OpenSpecialPage(None, self.selectedBossVnum, True)

	def __OnOverInRender(self):
		if not self.renderToolTip:
			self.renderToolTip = uitooltip.ToolTip()

		self.renderToolTip.ClearToolTip()
		self.renderToolTip.AppendSpace(5)

		cfg = self.bossConfig.get(self.selectedBossVnum)
		if cfg:
			self.renderToolTip.AutoAppendNewTextLineResize(localeinfo.WB_TOOLTIP_1 % self.__FormatDmgShort(cfg["minDamageRank"]))
			self.renderToolTip.AppendSpace(5)
			self.renderToolTip.AutoAppendNewTextLineResize(localeinfo.WB_TOOLTIP_2 % self.__FormatDmgShort(cfg["damageDivisor"]))
			self.renderToolTip.AppendSpace(5)
			self.renderToolTip.AutoAppendNewTextLineResize(localeinfo.WB_TOOLTIP_3 % cfg["minPresenceSec"])
			self.renderToolTip.AppendSpace(5)
			self.renderToolTip.AutoAppendNewTextLineResize(localeinfo.WB_TOOLTIP_4 % cfg["maxPointsPerFight"])
			self.renderToolTip.AppendSpace(10)

		self.renderToolTip.AppendShortcutRow(("key_lclick",), localeinfo.WB_CLICK_WIKI)
		self.renderToolTip.ShowToolTip()

	def __FormatDmgShort(self, dmg):
		if dmg >= 1000000000:
			return "%.1fB" % (dmg / 1000000000.0)
		if dmg >= 1000000:
			return "%.1fM" % (dmg / 1000000.0)
		if dmg >= 1000:
			return "%.1fK" % (dmg / 1000.0)
		return str(int(dmg))

	def __OnOverOutRender(self):
		if self.renderToolTip:
			self.renderToolTip.HideToolTip()

	# ============================================================
	# Boss spawn/death alerts
	# ============================================================
	def ShowBossSpawnAlert(self, bossVnum):
		# Persistent dismissal (survives warp across cores): if the player
		# clicked Cancel/Teleport on this boss, don't reshow regardless of
		# which core sent the WBBossSpawn.
		if bossVnum in self.dismissedBosses:
			return

		if bossVnum in self.spawnAlerts:
			alert = self.spawnAlerts[bossVnum]
			if alert.IsDismissed():
				self.dismissedBosses.add(bossVnum)
				return
			if alert.IsShow():
				return

		stackIndex = len([v for v in self.spawnAlerts.values() if v.IsShow()])
		if self.guildRaidAlert and self.guildRaidAlert.IsShow():
			stackIndex += 1
		alert = WorldBossSpawnAlert(bossVnum, stackIndex, owner=self)
		alert.Open()
		self.spawnAlerts[bossVnum] = alert

	def ShowGuildRaidAlert(self, bossVnum, runId):
		if self.guildRaidAlert:
			if self.guildRaidAlert.runId == runId and self.guildRaidAlert.IsDismissed():
				return
			if self.guildRaidAlert.runId == runId and self.guildRaidAlert.IsShow():
				return
			self.guildRaidAlert.Hide()
			self.guildRaidAlert = None
		stackIndex = len([v for v in self.spawnAlerts.values() if v.IsShow()])
		alert = GuildRaidSpawnAlert(bossVnum, stackIndex, owner=self, runId=runId)
		alert.Open()
		self.guildRaidAlert = alert

	def HideGuildRaidAlert(self, bossVnum):
		if self.guildRaidAlert:
			self.guildRaidAlert.Hide()
			self.guildRaidAlert = None

	def MarkBossDismissed(self, bossVnum):
		"""Called by the alert widget when Cancel/Teleport is pressed."""
		self.dismissedBosses.add(bossVnum)

	def HideBossSpawnAlert(self, bossVnum):
		if bossVnum in self.spawnAlerts:
			self.spawnAlerts[bossVnum].Hide()
			self.spawnAlerts[bossVnum].Destroy()
			del self.spawnAlerts[bossVnum]
		# Boss died (or cross-core death relay): forget any dismissal so a
		# future respawn shows the popup again.
		self.dismissedBosses.discard(bossVnum)

	def DestroyAllAlerts(self):
		"""Called on warp/phase change to clean up all popups.
		Does NOT clear dismissedBosses — dismissal persists across warps so
		the popup doesn't reappear when the player enters a new core."""
		for alert in self.spawnAlerts.values():
			alert.Hide()
			alert.Destroy()
		self.spawnAlerts = {}
		if self.guildRaidAlert:
			self.guildRaidAlert.Hide()
			self.guildRaidAlert.Destroy()
			self.guildRaidAlert = None

	# ============================================================
	# Request helpers
	# ============================================================
	def RequestMyRank(self, bossVnum):
		net.SendChatPacket("/wb_myrank %d" % bossVnum)

	def RequestRankingPage(self, bossVnum, page=0, weeksAgo=0):
		net.SendChatPacket("/wb_rank %d %d %d" % (bossVnum, page, weeksAgo))

	def RequestInfo(self):
		net.SendChatPacket("/wb_info")

	def RequestRewardInfo(self, bossVnum):
		if not getattr(app, "ENABLE_WORLDBOSS_V3", 0):
			return
		if self.rewardRowsComplete.get(bossVnum):
			return
		self.rewardRows[bossVnum] = []
		net.SendChatPacket("/wb_rewardinfo %d" % bossVnum)

	# ============================================================
	# Window management
	# ============================================================
	def Open(self):
		if app.ENABLE_WINDOW_POSITION_SAVE and uiwindowpositions.ApplySavedPosition(self,"worldboss"):
			pass
		else:
			self.SetCenterPosition()

		if not self.isLoaded:
			self.__LoadWindow()

		# Request data from server
		self.__RequestBossStatus()
		self.RequestInfo()
		self.RequestRankingPage(self.selectedBossVnum, 0, 0)
		self.RequestRewardInfo(self.selectedBossVnum)

		self.__RefreshBossInfo()
		self.__RefreshContribution()
		self.__RefreshRanking()

		self.Show()
		self.SetTop()

	def __RequestBossStatus(self):
		if not self.trackWindow:
			return

		command = "/track_window load"
		for data in self.trackWindow._TrackWindow__dataDict:
			command += " %d" % data["regen_id"]
		net.SendChatPacket(command)

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "worldboss")
		self.Hide()

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("worldboss", x, y)

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnUpdate(self):
		if not self.isLoaded or not self.IsShow():
			return

		# Refresh boss button images (status may change while window is open)
		self.__RefreshBossButtons()

		# Live weekly reset countdown
		self.__RefreshWeeklyTimer()

		self.__RefreshCoinRow()

		# Live update respawn timer for selected boss
		if self.trackWindow:
			for data in self.trackWindow._TrackWindow__dataDict:
				if data["bossVnum"] == self.selectedBossVnum:
					if data["status"]:
						self.GetChild("status_img").LoadImage(IMG_DIR + "alive.png")
						self.GetChild("timer_value").SetText("-" + self.__GetModeBadgeText(data))
					else:
						leftTime = data["server_cooldown"] - app.GetGlobalTimeStamp()
						if leftTime > 0:
							self.GetChild("status_img").LoadImage(IMG_DIR + "dead.png")
							self.GetChild("timer_value").SetText(localeinfo.SecondToDHMS(leftTime) + self.__GetModeBadgeText(data))
						else:
							self.GetChild("status_img").LoadImage(IMG_DIR + "alive.png")
							self.GetChild("timer_value").SetText("-" + self.__GetModeBadgeText(data))
					break
