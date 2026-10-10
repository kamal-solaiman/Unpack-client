#author: dracaryS

#static
import ui
from operator import truediv

#dynamic
import grp, player, app, net, guild, localeinfo, item
import uicommon

import systemSetting

import uitooltip

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

IMG_DIR = "new_rank/"
REWORK_DIR = "new_rank/rework/"

if app.__DONATE_RANKING__:
	try:
		DONATION_RANK = player.RANK_DONATE
	except AttributeError:
		DONATION_RANK = 16

def IsMonthlyRank(rankIdx):
	__rankList = [player.RANK_STONE,player.RANK_STONE_HIGH, player.RANK_MONSTER, player.RANK_BOSS, player.RANK_DUNGEON,player.RANK_STONE_DMG,player.RANK_STONE_DMG_HIGH,player.RANK_SWITCHERS,player.RANK_FISHING, player.RANK_CHEST, player.RANK_BOSS_HIGH, player.RANK_KILL, player.RANK_DONATE, player.RANK_PVP_EVENTS]
	return True if rankIdx in __rankList else False

rank_data = {
	player.RANK_TYPE_PLAYER : {
		"name" : localeinfo.RANKING_CAT_PLAYER,
		"dict" : {
			player.RANK_LEVEL : {
				"index" : 0,
				"image" : "type/0.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_1,localeinfo.RANKING_SUB_1),
				"title_name" : localeinfo.RANKING_CAT_VALUE,
			},
			player.RANK_STONE : {
				"index" : 1,
				"image" : "type/2.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_3,localeinfo.RANKING_SUB_3),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_STONE_HIGH : {
				"index" : 2,
				"image" : "type/22.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_33,localeinfo.RANKING_SUB_33),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_MONSTER : {
				"index" : 3,
				"image" : "type/7.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_8,localeinfo.RANKING_SUB_8),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_BOSS : {
				"index" : 4,
				"image" : "type/3.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_4,localeinfo.RANKING_SUB_4),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_BOSS_HIGH : {
				"index" : 5,
				"image" : "type/3x.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_13,localeinfo.RANKING_SUB_13),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_DUNGEON : {
				"index" : 6,
				"image" : "type/6.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_7,localeinfo.RANKING_SUB_7),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_STONE_DMG : {
				"index" : 7,
				"image" : "type/1.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_2,localeinfo.RANKING_SUB_2),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_STONE_DMG_HIGH : {
				"index" : 8,
				"image" : "type/11.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_22,localeinfo.RANKING_SUB_22),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_CHEST : {
				"index" : 9,
				"image" : "type/5.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_6,localeinfo.RANKING_SUB_6),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_SWITCHERS : {
				"index" : 10,
				"image" : "type/4.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_5,localeinfo.RANKING_SUB_5),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_FISHING : {
				"index" : 11,
				"image" : "type/9.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_10,localeinfo.RANKING_SUB_10),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_PLAYTIME : {
				"index" : 12,
				"image" : "type/9x.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_11,localeinfo.RANKING_SUB_11),
				"title_name" : localeinfo.RANKING_CAT_DURATION,
			},
			player.RANK_KILL : {
				"index" : 13,
				"image" : "type/12.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_9,localeinfo.RANKING_SUB_9),
				"title_name" : localeinfo.RANKING_CAT_RANK,
			},
			player.RANK_PVP_EVENTS : {
				"index" : 14,
				"image" : "type/14.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_15,localeinfo.RANKING_SUB_15),
				"title_name" : localeinfo.PVP_ROUTES_POINTS,
			},
			player.RANK_DONATE : {
				"index" : 15,
				"image" : "type/13.png",
				"name" : "{}".format(localeinfo.RANKING_CAT_14),
				"title_name" : localeinfo.RANKING_CAT_DONATE,
			},
		},
	},
	player.RANK_TYPE_GUILD : {
		"name" : localeinfo.RANKING_CAT_GUILD,
		"dict" : {
			player.RANK_STONE : {
				"index" : 0,
				"image" : "type/2g.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_3,localeinfo.RANKING_SUB_3),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_FISHING : {
				"index" : 1,
				"image" : "type/9.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_10,localeinfo.RANKING_SUB_10),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_BOSS : {
				"index" : 2,
				"image" : "type/3g.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_4,localeinfo.RANKING_SUB_4),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_DUNGEON : {
				"index" : 3,
				"image" : "type/6g.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_7,localeinfo.RANKING_SUB_7),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
			player.RANK_CHEST : {
				"index" : 4,
				"image" : "type/5g.png",
				"name" : "{}#{}".format(localeinfo.RANKING_CAT_6,localeinfo.RANKING_SUB_6),
				"title_name" : localeinfo.RANKING_CAT_COUNT,
			},
		},
	}
}

if app.ENABLE_GUILD_CONTRACTS and hasattr(player, "RANK_GUILD_ACTIVITY"):
	rank_data[player.RANK_TYPE_GUILD]["dict"][player.RANK_GUILD_ACTIVITY] = {
		"index" : 5,
		"image" : "type/6g.png",
		"name" : "{}#{}".format(getattr(localeinfo, "RANKING_CAT_GUILD_ACTIVITY", "Guild Activity"), getattr(localeinfo, "RANKING_SUB_GUILD_ACTIVITY", "")),
		"title_name" : localeinfo.RANKING_CAT_VALUE,
	}
	rank_data[player.RANK_TYPE_GUILD]["dict"][player.RANK_GUILD_CONTRACTS] = {
		"index" : 6,
		"image" : "type/5g.png",
		"name" : "{}#{}".format(getattr(localeinfo, "RANKING_CAT_GUILD_CONTRACTS", "Guild Contracts"), getattr(localeinfo, "RANKING_SUB_GUILD_CONTRACTS", "")),
		"title_name" : localeinfo.RANKING_CAT_COUNT,
	}
	rank_data[player.RANK_TYPE_GUILD]["dict"][player.RANK_GUILD_REPUTATION] = {
		"index" : 7,
		"image" : "type/3g.png",
		"name" : "{}#{}".format(getattr(localeinfo, "RANKING_CAT_GUILD_REPUTATION", "Guild Reputation"), getattr(localeinfo, "RANKING_SUB_GUILD_REPUTATION", "")),
		"title_name" : localeinfo.RANKING_CAT_VALUE,
	}

class RankRewardToolTip(ui.ThinBoard):
	# Reward preview as a ui.Table grid: [Place | Reward | Amount]. Same concept
	# as the world-boss reward tooltip. Item rewards show their icon in the Reward
	# cell; affect/buff rewards show the affect string with duration as the amount.
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
	C_HEAD_BG	= 0xff1c1c1c
	C_ROW_BG	= 0x99000000	# base row (rank 4+)
	C_HEAD_TXT	= 0xffffd300
	C_CELL_TXT	= 0xffe8e8e8
	C_TITLE		= 0xfff2e6c1
	C_AFFECT	= 0xff7ed957

	# Soft podium: a faint rank-tinted wash over each group's rows + a bright
	# gold/silver/bronze place number.
	C_RANK_BG = {
		1: 0xd9241f14,	# faint gold
		2: 0xd9242424,	# faint silver (neutral dark gray)
		3: 0xd9241a12,	# faint bronze
	}
	C_RANK_TXT = {
		1: 0xffffd24a,	# gold
		2: 0xffd6dde6,	# silver
		3: 0xffd98a45,	# bronze
	}
	C_RANK_TXT_DEFAULT	= 0xffffd54f

	def __init__(self):
		ui.ThinBoard.__init__(self, "TOP_MOST")
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

	# Kept for the host window's Destroy(), which calls ClearToolTip().
	def ClearToolTip(self):
		self.Clear()
		self.Hide()

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

	def __AppendSeparator(self, y):
		sep = ui.Line()
		sep.SetParent(self)
		sep.AddFlag("not_pick")
		sep.SetPosition(self.PAD, y)
		sep.SetSize(self.INNER_W, 0)
		sep.SetColor(self.C_LINE)
		sep.Show()
		self.children.append(sep)

	def __CollectRows(self, rewardList):
		rows = []
		lastPos = -1
		for reward in rewardList:
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

	def Build(self, titleText, rewardList):
		self.Clear()
		isAr = localeinfo.IsARABIC()

		y = self.PAD
		self.__AppendText(titleText, y, self.C_TITLE)
		y += self.TITLE_H
		self.__AppendSeparator(y)
		y += self.SEP_H

		rows = self.__CollectRows(rewardList)
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


class Window(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.__children = {}

		self.__LoadWindow()

	def Destroy(self):
		if self.__children.has_key("titleName"):
			del self.__children["titleName"]

		if self.__children.has_key("rewardInfoButton"):
			self.__children["rewardInfoButton"].SetEventOverIn(None)
			self.__children["rewardInfoButton"].SetEventOverOut(None)
			del self.__children["rewardInfoButton"]

		if self.__children.has_key("titleBar"):
			self.__children["titleBar"].SetCloseEvent(None)
			del self.__children["titleBar"]

		if self.__children.has_key("rewardToolTip"):
			self.__children["rewardToolTip"].ClearToolTip()
			del self.__children["rewardToolTip"]

		if self.__children.has_key("trophyButton"):
			self.__children["trophyButton"].SetEventOverIn(None)
			self.__children["trophyButton"].SetEventOverOut(None)

		if self.__children.has_key("trophyToolTip"):
			self.__children["trophyToolTip"].ClearToolTip()
			del self.__children["trophyToolTip"]

		if self.__children.has_key("timerToolTip"):
			self.__children["timerToolTip"].ClearToolTip()
			del self.__children["timerToolTip"]

		if self.__children.has_key("timeBtnToolTip"):
			self.__children["timeBtnToolTip"].ClearToolTip()
			del self.__children["timeBtnToolTip"]

		if app.__DONATE_RANKING__:
			dw = self.__children.get("donationWnd")
			if dw:
				dw.Close()

		self.__children = {}

	def __OnOverInReward(self):
		if not self.__children.has_key("selectedIdx") or not self.__children.has_key("pageIdx") or not self.__children.has_key("timeIdx"):
			return

		timeIdx = self.__children["timeIdx"]
		pageIdx = self.__children["pageIdx"]
		selectedIdx = self.__children["selectedIdx"]

		titleText = ""
		if timeIdx == player.RANK_TIME_WEEKLY:
			if pageIdx == player.RANK_TYPE_PLAYER:
				titleText = localeinfo.RANK_REWARD_WEEKLY.format(localeinfo.RANK_REWARD_PLAYERS)
			elif pageIdx == player.RANK_TYPE_GUILD:
				titleText = localeinfo.RANK_REWARD_WEEKLY.format(localeinfo.RANK_REWARD_GUILDS)
		elif timeIdx == player.RANK_TIME_MONTHLY:
			if pageIdx == player.RANK_TYPE_PLAYER:
				titleText = localeinfo.RANK_REWARD_MONTHLY.format(localeinfo.RANK_REWARD_PLAYERS)
			elif pageIdx == player.RANK_TYPE_GUILD:
				titleText = localeinfo.RANK_REWARD_MONTHLY.format(localeinfo.RANK_REWARD_GUILDS)

		if titleText == "":
			return

		if not self.__children.has_key("rewardToolTip"):
			self.__children["rewardToolTip"] = RankRewardToolTip()

		rewardList = player.GetRankingReward(timeIdx, pageIdx, selectedIdx)
		self.__children["rewardToolTip"].Build(titleText, rewardList)
		self.__children["rewardToolTip"].ShowNear(self.__children["rewardInfoButton"])

	def __OnOverOutReward(self):
		if self.__children.has_key("rewardToolTip"):
			self.__children["rewardToolTip"].Hide()

	def __OnOverInTrophy(self):
		"""Show tooltip for trophy button explaining Hall of Fame toggle"""
		if not self.__children.has_key("trophyToolTip"):
			self.__children["trophyToolTip"] = uitooltip.ItemToolTip()

		self.__children["trophyToolTip"].ClearToolTip()

		hofMode = self.__children.get("hofMode", False)
		timeIdx = self.__children.get("timeIdx", 0)

		# Title based on time period
		if timeIdx == 0:
			titleText = localeinfo.RANKING_HOF_WEEKLY if hasattr(localeinfo, 'RANKING_HOF_WEEKLY') else "Weekly Winners"
		else:
			titleText = localeinfo.RANKING_HOF_MONTHLY if hasattr(localeinfo, 'RANKING_HOF_MONTHLY') else "Monthly Winners"

		self.__children["trophyToolTip"].AppendTextLine(titleText, 0xFFFFD700)

		self.__children["trophyToolTip"].AppendSpace(5)

		# Description based on current mode
		if hofMode:
			descText = localeinfo.RANKING_TROPHY_CLICK_RANKINGS if hasattr(localeinfo, 'RANKING_TROPHY_CLICK_RANKINGS') else "Click to view current rankings"
		else:
			descText = localeinfo.RANKING_TROPHY_CLICK_WINNERS if hasattr(localeinfo, 'RANKING_TROPHY_CLICK_WINNERS') else "Click to view last period's top 3"

		self.__children["trophyToolTip"].AppendTextLine(descText, 0xFFCCCCCC)
		self.__children["trophyToolTip"].ShowToolTip()

	def __OnOverOutTrophy(self):
		if self.__children.has_key("trophyToolTip"):
			self.__children["trophyToolTip"].HideToolTip()

	def __OnOverInTimer(self):
		"""Show tooltip for timer icon explaining reset time"""
		if not self.__children.has_key("timerToolTip"):
			self.__children["timerToolTip"] = uitooltip.ItemToolTip()

		self.__children["timerToolTip"].ClearToolTip()

		timeIdx = self.__children.get("timeIdx", 0)

		# Title based on time period
		if timeIdx == 0:  # Weekly
			titleText = localeinfo.RANKING_RESET_WEEKLY if hasattr(localeinfo, 'RANKING_RESET_WEEKLY') else "Weekly Reset"
		else:  # Monthly
			titleText = localeinfo.RANKING_RESET_MONTHLY if hasattr(localeinfo, 'RANKING_RESET_MONTHLY') else "Monthly Reset"

		self.__children["timerToolTip"].AppendTextLine(titleText, 0xFFFFD700)

		self.__children["timerToolTip"].AppendSpace(5)

		# Show remaining time
		now = app.GetGlobalTimeStamp()
		if timeIdx == 0:
			nextReset = self.__children.get("nextWeeklyReset", 0)
		else:
			nextReset = self.__children.get("nextMonthlyReset", 0)

		if nextReset > 0:
			remaining = nextReset - now
			if remaining > 0:
				timeText = self.__FormatResetCountdown(remaining)
				# Color based on urgency
				if remaining < 86400:  # Less than 24 hours
					self.__children["timerToolTip"].AppendTextLine(timeText, 0xFFFF6B6B)
				else:
					self.__children["timerToolTip"].AppendTextLine(timeText, 0xFFCCCCCC)
			else:
				soonText = localeinfo.RANKING_RESET_SOON if hasattr(localeinfo, 'RANKING_RESET_SOON') else "Soon!"
				self.__children["timerToolTip"].AppendTextLine(soonText, 0xFFFF6B6B)

		self.__children["timerToolTip"].ShowToolTip()

	def __OnOverOutTimer(self):
		if self.__children.has_key("timerToolTip"):
			self.__children["timerToolTip"].HideToolTip()

	def __OnOverInTimeBtn(self, timeIdx):
		"""Show tooltip for time period buttons (Weekly/Monthly)"""
		if not self.__children.has_key("timeBtnToolTip"):
			self.__children["timeBtnToolTip"] = uitooltip.ItemToolTip()

		self.__children["timeBtnToolTip"].ClearToolTip()

		if timeIdx == 0:
			tooltipText = localeinfo.RANKING_WEEKLY_HOVER if hasattr(localeinfo, 'RANKING_WEEKLY_HOVER') else "View Weekly Rankings"
		else:
			tooltipText = localeinfo.RANKING_MONTHLY_HOVER if hasattr(localeinfo, 'RANKING_MONTHLY_HOVER') else "View Monthly Rankings"

		self.__children["timeBtnToolTip"].AppendTextLine(tooltipText, 0xFFFFFFFF)
		self.__children["timeBtnToolTip"].ShowToolTip()

	def __OnOverOutTimeBtn(self):
		if self.__children.has_key("timeBtnToolTip"):
			self.__children["timeBtnToolTip"].HideToolTip()

	def __LoadWindow(self):
		self.Destroy()

		self.AddFlag("movable")
		self.AddFlag("float")
		self.AddFlag("attach")
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
	
		global rank_data

		windowRect = (604, 403 + 40)

		board = CreateWindow(ui.Board(), self, ["attach"], (0, 0), "", "", windowRect)
		self.__children["board"] = board

		titleBar = CreateWindow(ui.TitleBar(), self, ["attach"], (8, 7), "", "")
		titleBar.MakeTitleBar(board.GetWidth() - 16, "red")
		titleBar.SetCloseEvent(ui.__mem_func__(self.Close))
		self.__children["titleBar"] = titleBar

		titleName = CreateWindow(ui.TextLine(), titleBar, [], (0, 2), "", "")
		titleName.SetWindowHorizontalAlignCenter()
		titleName.SetHorizontalAlignCenter()
		titleName.SetText(localeinfo.RANKING_TITLE)
		titleName.Show()
		self.__children["titleName"] = titleName

		rewardInfoButton = ui.MakeButton(titleBar, titleBar.GetWidth() - 30, 1, "", "d:/ymir work/ui/pattern/", "q_mark_01.tga", "q_mark_02.tga", "q_mark_02.tga")
		rewardInfoButton.SetEventOverIn(ui.__mem_func__(self.__OnOverInReward))
		rewardInfoButton.SetEventOverOut(ui.__mem_func__(self.__OnOverOutReward))
		rewardInfoButton.Show()
		self.__children["rewardInfoButton"] = rewardInfoButton

		# Hall of Fame data storage and mode tracking
		self.hallOfFameData = {}  # Storage for winners data
		self.__children["hofMode"] = False  # False = current rankings, True = winners

		thinBoard = CreateWindow(ui.ThinBoard("UI",2), board, ["attach"], (8, 31), "", "", (windowRect[0] - 16, windowRect[1] - (31 + 8)))
		self.__children["thinBoard"] = thinBoard

		# New background image on top of thinBoard
		bgImage = ui.ImageBox()
		bgImage.SetParent(thinBoard)
		bgImage.AddFlag("attach")
		bgImage.LoadImage(REWORK_DIR + "bg.png")
		bgImage.SetPosition(0, 8)
		bgImage.Show()
		self.__children["bgImage"] = bgImage

		# Reset Timer display (in the new 40px top area)
		resetTimerText = CreateWindow(ui.TextLine(), thinBoard, ["not_pick"], (thinBoard.GetWidth() - 50, 18), "", "")
		resetTimerText.SetPackedFontColor(0xFFCCCCCC)
		resetTimerText.Show()
		self.__children["resetTimerText"] = resetTimerText
		self.__children["nextWeeklyReset"] = 0
		self.__children["nextMonthlyReset"] = 0

		# icon for timer (with tooltip)
		resetTimerImage = CreateWindow(ui.ImageBox(), thinBoard, [], (423, 17), IMG_DIR + "timer_icon.png")
		resetTimerImage.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OnOverInTimer)
		resetTimerImage.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OnOverOutTimer)
		resetTimerImage.Show()
		self.__children["resetTimerImage"] = resetTimerImage

		leftBoardImage = CreateWindow(ui.ImageBox(), self, ["attach"], (3, windowRect[1] - 10), IMG_DIR + "left_0.tga")
		self.__children["leftBoardImage"] = leftBoardImage

		rightBoardImage = CreateWindow(ui.ImageBox(), self, ["attach"], (windowRect[0] - 10, 33), IMG_DIR + "right_2.tga")
		rightBoardImage.Hide()
		self.__children["rightBoardImage"] = rightBoardImage

		pageBtnX = [14, 76]
		for j in xrange(2):
			pageBtn = CreateWindow(ui.ImageBox(), leftBoardImage, [], (pageBtnX[j], 5), REWORK_DIR + "left_btn.png")
			pageBtn.SetEvent(ui.__mem_func__(self.__SetPage), "mouse_click", j)
			pageBtn.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OverIn, rank_data[j]["name"])
			pageBtn.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OverOut)
			self.__children["pageBtn" + str(j)] = pageBtn

		# Time period board image (swaps between btn_weekly_1.png and btn_monthly_1.png)
		timeBoardImage = CreateWindow(ui.ImageBox(), thinBoard, ["attach"], (8, 7), REWORK_DIR + "btn_weekly_1.png")
		self.__children["timeBoardImage"] = timeBoardImage

		# Time period click areas (like pageBtn pattern)
		timeBtnX = [5, 109]  # Positions for Weekly and Monthly click areas
		for j in xrange(2):
			timeBtn = CreateWindow(ui.ImageBox(), timeBoardImage, [], (timeBtnX[j], 5), REWORK_DIR + "left_btn.png")
			timeBtn.SetEvent(ui.__mem_func__(self.__SetTime), "mouse_click", j)
			timeBtn.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OnOverInTimeBtn, j)
			timeBtn.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OnOverOutTimeBtn)
			timeBtn.Show()
			self.__children["timeBtn" + str(j)] = timeBtn

		leftBg = CreateWindow(ui.ImageBox(), thinBoard, ["attach"], (5, 58), REWORK_DIR + "left_bg.tga")
		self.__children["leftBg"] = leftBg

		leftBgRender = CreateWindow(ui.Window(), leftBg, ["attach"], (1, 1), "", "", (leftBg.GetWidth() - 2, leftBg.GetHeight() - 2))
		#leftBgRender.OnMouseWheel = ui.__mem_func__(self.__OnMouseWheelSpecial)
		# leftBgRender.SetInsideRender(True)
		self.__children["leftBgRender"] = leftBgRender

		if app.USE_CLIP_MASK:
			self.__children["leftBgRender"].SetClippingMaskWindow(self.__children["leftBg"])

		scrollBarLeft = CreateWindow(ScrollBarSpecial(), thinBoard, [], (195, 58), "", "", (8, leftBgRender.GetHeight()))
		scrollBarLeft.SetScale(leftBgRender.GetHeight(), leftBgRender.GetHeight())
		scrollBarLeft.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		self.__children["scrollBarLeft"] = scrollBarLeft

		rightBg = CreateWindow(ui.ImageBox(), thinBoard, ["attach"], (211, 58), REWORK_DIR + "right_bg.png")
		self.__children["rightBg"] = rightBg

		nameTitle = CreateWindow(ui.TextLine(), rightBg, ["not_pick"], (95, 20-5 - 8), localeinfo.RANKING_CAT_NAME, "horizontal:center")
		nameTitle.SetPackedFontColor(0xFFC29E72)
		self.__children["nameTitle"] = nameTitle

		levelFlagTitle = CreateWindow(ui.TextLine(), rightBg, ["not_pick"], (205, 20-5 - 8), localeinfo.RANKING_CAT_LEVEL, "horizontal:center")
		levelFlagTitle.SetPackedFontColor(0xFFC29E72)
		self.__children["levelFlagTitle"] = levelFlagTitle

		valueTitle = CreateWindow(ui.TextLine(), rightBg, ["not_pick"], (310, 20-5 - 8), localeinfo.RANKING_CAT_VALUE, "horizontal:center")
		valueTitle.SetPackedFontColor(0xFFC29E72)
		self.__children["valueTitle"] = valueTitle

		rankColor = {1 : 0xFFFFD800, 2 : 0xFFC0C0C0, 3 : 0xFFCD7F32}
		# Row background images: 1.png (1st), 2.png (2nd), 3.png (3rd), 4.png (normal), me.png (player)
		# Note: Row backgrounds have built-in medal icons, no separate medal images needed
		rowBgImages = {0: "1.png", 1: "2.png", 2: "3.png", 10: "me.png"}
		for j in xrange(11):
			# Load row background
			rowBgFile = rowBgImages.get(j, "4.png")
			self.__children["rowBg" + str(j)] = CreateWindow(ui.ImageBox(), rightBg, ["not_pick"], (4, 37 - 8 + (j * 26)), REWORK_DIR + rowBgFile)

			index = CreateWindow(ui.TextLine(), rightBg, ["not_pick"], (25+10 - 8, 35 + (j * 26-3)), str(j + 1) if j != 10 else "#")
			if rankColor.has_key(j + 1):
				index.SetPackedFontColor(rankColor[j + 1])
			self.__children["index" + str(j)] = index

			name = CreateWindow(ui.TextLine(), rightBg, ["not_pick"], (95 - 8, 35 + (j * 26-3)), "Player " + str(j + 1) if j != 10 else "?", "horizontal:center")
			if rankColor.has_key(j + 1):
				name.SetPackedFontColor(rankColor[j + 1])
			self.__children["name" + str(j)] = name

			level = CreateWindow(ui.TextLine(), rightBg, ["not_pick"], (180 - 8, 35 + (j * 26-3)), "Lv.?" if j != 10 else "?", "horizontal:center")
			if rankColor.has_key(j + 1):
				level.SetPackedFontColor(rankColor[j + 1])
			self.__children["level" + str(j)] = level

			self.__children["flag" + str(j)] = CreateWindow(ui.ImageBox(), rightBg, ["not_pick"], (215 - 8, 34 + (j * 26)), IMG_DIR + "newempire_1.png")
			self.__children["flag" + str(j)].Hide()

			value = CreateWindow(ui.TextLine(), rightBg, ["not_pick"], (310 - 8, 35 + (j * 26-3)), "0" if j != 10 else "?", "horizontal:center")
			if rankColor.has_key(j + 1):
				value.SetPackedFontColor(rankColor[j + 1])
			self.__children["value" + str(j)] = value

		# ============= HALL OF FAME TOGGLE VIEW =============
		# Trophy button - positioned in top-middle of ranking area
		trophyButton = ui.MakeButton(thinBoard, 222, 7, "", REWORK_DIR, "top_10.png", "top_10_2.png", "top_10.png")
		trophyButton.SAFE_SetEvent(self.__ToggleHallOfFame)
		trophyButton.SetEventOverIn(ui.__mem_func__(self.__OnOverInTrophy))
		trophyButton.SetEventOverOut(ui.__mem_func__(self.__OnOverOutTrophy))
		trophyButton.Show()
		self.__children["trophyButton"] = trophyButton

		# Winner display elements (only shown in HoF mode)
		# Use same row backgrounds and positions as normal ranking rows (rows 0, 1, 2)
		winnerRowBgImages = ["1.png", "2.png", "3.png"]

		for i in xrange(3):
			# Same positions as regular rows
			rowBgY = 37 - 8 + (i * 26)  # = 29 + i*26
			textY = 35 + (i * 26 - 3)   # = 32 + i*26
			flagY = 34 + (i * 26)

			# Row background (same as regular rows)
			winnerRowBg = ui.ImageBox()
			winnerRowBg.SetParent(rightBg)
			winnerRowBg.AddFlag("not_pick")
			winnerRowBg.LoadImage(REWORK_DIR + winnerRowBgImages[i])
			winnerRowBg.SetPosition(4, rowBgY)
			winnerRowBg.Hide()
			self.__children["winnerRowBg" + str(i)] = winnerRowBg

			# Name (same x as normal: 95 - 8 = 87)
			winnerName = ui.TextLine()
			winnerName.SetParent(rightBg)
			winnerName.AddFlag("not_pick")
			winnerName.SetPosition(95 - 8, textY)
			winnerName.SetPackedFontColor(0xFFFFFFFF)  # White, row bg provides distinction
			winnerName.SetText("")
			winnerName.SetHorizontalAlignCenter()
			winnerName.Hide()
			self.__children["winnerName" + str(i)] = winnerName

			# Level (same x as normal: 180 - 8 = 172)
			winnerLevel = ui.TextLine()
			winnerLevel.SetParent(rightBg)
			winnerLevel.AddFlag("not_pick")
			winnerLevel.SetPosition(180 - 8, textY)
			winnerLevel.SetPackedFontColor(0xFFFFFFFF)  # White, row bg provides distinction
			winnerLevel.SetText("")
			winnerLevel.SetHorizontalAlignCenter()
			winnerLevel.Hide()
			self.__children["winnerLevel" + str(i)] = winnerLevel

			# Empire flag (same x as normal: 215 - 8 = 207)
			winnerFlag = ui.ImageBox()
			winnerFlag.SetParent(rightBg)
			winnerFlag.AddFlag("not_pick")
			winnerFlag.LoadImage(IMG_DIR + "newempire_1.png")
			winnerFlag.SetPosition(215 - 8, flagY)
			winnerFlag.Hide()
			self.__children["winnerFlag" + str(i)] = winnerFlag

			# Value (same x as normal: 310 - 8 = 302)
			winnerValue = ui.TextLine()
			winnerValue.SetParent(rightBg)
			winnerValue.AddFlag("not_pick")
			winnerValue.SetPosition(310 - 8, textY)
			winnerValue.SetPackedFontColor(0xFFFFFFFF)  # White, row bg provides distinction
			winnerValue.SetText("")
			winnerValue.SetHorizontalAlignCenter()
			winnerValue.Hide()
			self.__children["winnerValue" + str(i)] = winnerValue

		# "Last Period Winners" title (shown in HoF mode)
		winnerTitle = ui.TextLine()
		winnerTitle.SetParent(rightBg)
		winnerTitle.AddFlag("not_pick")
		winnerTitle.SetPosition(rightBg.GetWidth() / 2, 12)
		winnerTitle.SetHorizontalAlignCenter()
		winnerTitle.SetText(localeinfo.RANKING_HALL_OF_FAME if hasattr(localeinfo, 'RANKING_HALL_OF_FAME') else "LAST PERIOD WINNERS")
		winnerTitle.SetPackedFontColor(0xFFFFD700)  # Gold
		winnerTitle.Hide()
		self.__children["winnerTitle"] = winnerTitle


		loadingImg = CreateWindow(ui.ExpandedImageBox(), rightBg, ["not_pick"], ((rightBg.GetWidth()/2) - 16, (rightBg.GetHeight()/2) - 16), IMG_DIR + "loading.tga")
		loadingImg.SetDiffuseColor(194.0 / 255.0, 158.0 / 255.0, 114.0 / 255.0, 1.0)
		loadingImg.Hide()
		self.__children["loading"] = loadingImg

		if app.__DONATE_RANKING__:
			donateBtn = ui.MakeButton(leftBg, 70, leftBg.GetHeight() - 33, "", "d:/ymir work/ui/", "donate_1.png", "donate_2.png", "donate_3.png")
			donateBtn.SetToolTipText(localeinfo.RANKING_DONATE_TITLE)
			donateBtn.SAFE_SetEvent(self.__OpenDonateUI)
			donateBtn.Hide()
			self.__children["donateBtn"] = donateBtn



		self.SetSize(windowRect[0] + rightBoardImage.GetWidth(), windowRect[1] + leftBoardImage.GetHeight())
		self.SetCenterPosition()

		self.__SetPage("", 0, False)

	def __SetTime(self, emptyArg, timeIdx, needRefresh = True):
		# Reset to normal mode when switching time period
		self.__ResetHofMode()

		selectedIdx = self.__children["selectedIdx"]
		if selectedIdx == -1 or IsMonthlyRank(selectedIdx) == False:
			self.__children["timeIdx"] = 0
			timeIdx = 0
		self.__children["timeIdx"] = timeIdx

		# Update time board image based on selection and category support
		timeBoardImage = self.__children.get("timeBoardImage")
		monthlyBtn = self.__children.get("timeBtn1")
		hasMonthly = selectedIdx != -1 and IsMonthlyRank(selectedIdx)

		if timeBoardImage:
			if not hasMonthly:
				timeBoardImage.LoadImage(REWORK_DIR + "btn_weekly_only.png")
			elif timeIdx == 0:
				timeBoardImage.LoadImage(REWORK_DIR + "btn_weekly_1.png")
			else:
				timeBoardImage.LoadImage(REWORK_DIR + "btn_monthly_1.png")

		if monthlyBtn:
			if hasMonthly:
				monthlyBtn.Show()
			else:
				monthlyBtn.Hide()

		if needRefresh:
			self.Refresh()

	def __SetPage(self, emptyArg, pageIdx, needRefresh = True):
		self.__OnOverOutReward()
		# Reset to normal mode when switching page (Player/Guild)
		self.__ResetHofMode()

		self.__children["leftBoardImage"].LoadImage(IMG_DIR + "left_"+str(pageIdx)+".tga")
		self.__children["pageIdx"] = pageIdx
		selectedIdx = -1
		global rank_data
		for rankIdx, rankData in rank_data[pageIdx]["dict"].items():
			if rankData["index"] == 0:
				selectedIdx = rankIdx
				break
		self.__children["selectedIdx"] = selectedIdx
		self.__SetTime("", 0, False)
		if needRefresh:
			self.Refresh()

	if app.__DONATE_RANKING__:
		def __GetDonationWindow(self):
			if not self.__children.get("donationWnd"):
				self.__children["donationWnd"] = DonationWindow()
			return self.__children["donationWnd"]

		def __OpenDonateUI(self):
			if self.__children.get("selectedIdx") != DONATION_RANK:
				return
			self.__GetDonationWindow().Open()

	def __ClickItem(self, emptyArg, rankIdx):
		self.__OnOverOutReward()
		# Reset to normal mode when switching category
		self.__ResetHofMode()

		self.__children["selectedIdx"] = rankIdx
		self.__SetTime("", self.__children["timeIdx"], False)
		self.Refresh(True, True, False)

	# ============= HALL OF FAME TOGGLE VIEW METHODS =============
	def __ToggleHallOfFame(self):
		"""Toggle between current rankings and Hall of Fame winners"""
		hofMode = self.__children.get("hofMode", False)
		trophyButton = self.__children.get("trophyButton")

		if hofMode:
			# Currently showing winners -> switch to current rankings
			self.__children["hofMode"] = False

			# Change trophy to colorful
			if trophyButton:
				trophyButton.SetUpVisual(REWORK_DIR + "top_10.png")
				trophyButton.SetOverVisual(REWORK_DIR + "top_10.png")
				trophyButton.SetDownVisual(REWORK_DIR + "top_10.png")

			# Hide winner elements
			self.__HideWinnerElements()

			# Show column titles
			self.__children["nameTitle"].Show()
			self.__children["levelFlagTitle"].Show()
			self.__children["valueTitle"].Show()

			# Refresh to show current rankings
			self.Refresh(False, True, False)
		else:
			# Currently showing rankings -> switch to winners
			self.__children["hofMode"] = True

			# Change trophy to colorless
			if trophyButton:
				trophyButton.SetUpVisual(REWORK_DIR + "top_3.png")
				trophyButton.SetOverVisual(REWORK_DIR + "top_3_2.png")
				trophyButton.SetDownVisual(REWORK_DIR + "top_3_3.png")

			# Hide all ranking rows (0-10)
			self.__HideRankingRows()

			# Hide column titles
			self.__children["nameTitle"].Hide()
			self.__children["levelFlagTitle"].Hide()
			self.__children["valueTitle"].Hide()

			# Show winner elements
			self.__ShowWinnerElements()

	def __HideRankingRows(self):
		"""Hide all 11 ranking rows"""
		for j in xrange(11):
			self.__children["rowBg" + str(j)].Hide()
			self.__children["index" + str(j)].Hide()
			self.__children["name" + str(j)].Hide()
			self.__children["level" + str(j)].Hide()
			self.__children["flag" + str(j)].Hide()
			self.__children["value" + str(j)].Hide()

	def __HideWinnerElements(self):
		"""Hide all winner display elements"""
		winnerTitle = self.__children.get("winnerTitle")
		if winnerTitle:
			winnerTitle.Hide()

		for i in xrange(3):
			for elem in ["winnerRowBg", "winnerName", "winnerLevel", "winnerFlag", "winnerValue"]:
				el = self.__children.get(elem + str(i))
				if el:
					el.Hide()

	def __ShowWinnerElements(self):
		"""Show and populate winner display elements"""
		pageIdx = self.__children.get("pageIdx", 0)
		timeIdx = self.__children.get("timeIdx", 0)
		selectedIdx = self.__children.get("selectedIdx", -1)

		key = (pageIdx, timeIdx, selectedIdx)
		winners = self.hallOfFameData.get(key, [])

		# Show title
		winnerTitle = self.__children.get("winnerTitle")
		if winnerTitle:
			winnerTitle.Show()

		for i in xrange(3):
			winnerRowBg = self.__children.get("winnerRowBg" + str(i))
			winnerName = self.__children.get("winnerName" + str(i))
			winnerLevel = self.__children.get("winnerLevel" + str(i))
			winnerFlag = self.__children.get("winnerFlag" + str(i))
			winnerValue = self.__children.get("winnerValue" + str(i))

			if i < len(winners) and winners[i]:
				winner = winners[i]

				if winnerName:
					winnerName.SetText(winner.get("name", ""))
					winnerName.Show()

				if winnerLevel:
					level = winner.get("level", 0)
					empire = winner.get("empire", 0)
					if empire > 10:
						winnerLevel.SetText("Cn.{}".format(level))
					else:
						winnerLevel.SetText("Lv.{}".format(level))
					winnerLevel.Show()

				if winnerFlag:
					empire = winner.get("empire", 0)
					display_empire = empire % 10 if empire > 10 else empire
					if display_empire >= 1 and display_empire <= 3:
						winnerFlag.LoadImage(IMG_DIR + "newempire_{}.png".format(display_empire))
						winnerFlag.Show()
					else:
						winnerFlag.Hide()

				if winnerValue:
					value = winner.get("value", 0)
					winnerValue.SetText(self.__NumberToDecimalString(value))
					winnerValue.Show()

				if winnerRowBg:
					winnerRowBg.Show()
			else:
				# No winner - hide elements
				if winnerRowBg: winnerRowBg.Hide()
				if winnerName: winnerName.Hide()
				if winnerLevel: winnerLevel.Hide()
				if winnerFlag: winnerFlag.Hide()
				if winnerValue: winnerValue.Hide()

	def __ResetHofMode(self):
		"""Reset to normal ranking mode"""
		if self.__children.get("hofMode", False):
			self.__children["hofMode"] = False
			self.__HideWinnerElements()
			# Reset trophy to colorful
			trophyButton = self.__children.get("trophyButton")
			if trophyButton:
				trophyButton.SetUpVisual(IMG_DIR + "top_10.png")
				trophyButton.SetOverVisual(IMG_DIR + "top_10_2.png")
				trophyButton.SetDownVisual(IMG_DIR + "top_10_3.png")
			# Show column titles
			self.__children["nameTitle"].Show()
			self.__children["levelFlagTitle"].Show()
			self.__children["valueTitle"].Show()

	def LoadHallOfFameData(self, pageIdx, timeIdx, rankIdx, winnersCmd):
		"""Load Hall of Fame winners data from server

		winnersCmd format: "pos?name?level?empire?value#pos?name?level?empire?value#..."
		"""
		winners = []
		if winnersCmd and winnersCmd != "empty":
			for entry in winnersCmd.split("#"):
				parts = entry.split("?")
				if len(parts) >= 5:
					winners.append({
						"position": int(parts[0]),
						"name": parts[1],
						"level": int(parts[2]),
						"empire": int(parts[3]),
						"value": long(parts[4])
					})

		key = (pageIdx, timeIdx, rankIdx)
		self.hallOfFameData[key] = winners

		# Refresh if currently in HoF mode and showing this category
		if self.__children.get("hofMode", False):
			currentKey = (self.__children.get("pageIdx", 0),
						  self.__children.get("timeIdx", 0),
						  self.__children.get("selectedIdx", -1))
			if key == currentKey:
				self.__ShowWinnerElements()
	# ============= END HALL OF FAME TOGGLE VIEW METHODS =============

	def UpdateRankData(self, rankType, timeIdx, rankIdx, mainVal):
		global rank_data
		rank_data[rankType]["dict"][rankIdx]["dataDict" + str(timeIdx)]["rankDict"][10]["value"] = mainVal

		selectedIdx = self.__children["selectedIdx"]

		if self.__children["pageIdx"] == rankType and self.__children["timeIdx"] == timeIdx and selectedIdx == rankIdx:
			if selectedIdx == player.RANK_PLAYTIME:
				self.__children["value10"].SetText(self.__FormatTime(mainVal))
			else:
				self.__children["value10"].SetText(self.__NumberToDecimalString(mainVal))

	def LoadRankData(self, rankType, timeIdx, rankIdx, nextUpdateTime, mainVal, cmd, nextWeeklyReset=0, nextMonthlyReset=0):
		global rank_data

		# Store reset times for timer display
		if nextWeeklyReset > 0:
			self.__children["nextWeeklyReset"] = nextWeeklyReset
		if nextMonthlyReset > 0:
			self.__children["nextMonthlyReset"] = nextMonthlyReset

		rankDict = {}
		mainIdx = -1
		if cmd != "empty":
			rankCmd = cmd.split("#")
			for cmdData in rankCmd:
				cmdList = cmdData.split("?")
				rankDict[int(cmdList[0])] = {
					"name" : cmdList[1],
					"level" : int(cmdList[2]),
					"flag" : int(cmdList[3]),
					"value" : long(cmdList[4]),
					"idx" : int(cmdList[0]),
				}
				guildName = guild.GetGuildName(guild.GetGuildID())

				if cmdList[1] == (player.GetName() if rankType == player.RANK_TYPE_PLAYER else guildName):
					mainIdx = int(cmdList[0])

		guildId = guild.GetGuildID()
		rankDict[10] = {
			"name" : player.GetName() if rankType == 0 else guild.GetGuildName(guildId),
			"level" : player.GetLevel() if rankType == 0 else guild.GetGuildLevel(),
			"flag" : player.GetEmpire(),
			"value" : mainVal,
			"idx" : mainIdx,
		}

		rank_data[int(rankType)]["dict"][int(rankIdx)]["dataDict" + str(timeIdx)] ={
			#"leftTimeUpdate" : app.GetGlobalTimeStamp() + int(nextUpdateTime) + 10,
			"leftTimeUpdate" : app.GetGlobalTimeStamp() + 1,
			"rankDict" : rankDict
		}
		self.Refresh(True, True, False)

	def SetLoadingStatus(self, flag):
		if flag:
			self.__children["loading"].Show()
		else:
			self.__children["loading"].Hide()
	def __SortRule(self, child):
		return child[1]
	def __NumberToDecimalString(self, n):
		return str('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))
	# def __FormatTime(self, second):
		# if second <= 0:
			# return "0s"
		# m, s = divmod(second, 60)
		# h, m = divmod(m, 60)
		# d, h = divmod(h, 24)
		# text = ""
		# if d > 0:
			# text+="{}d ".format(d)
		# if h > 0:
			# text+="{}h ".format(h)
		# if m > 0:
			# text+="{}m ".format(m)
		# if s > 0:
			# text+="{}s ".format(s)
		# return text[:len(text)-1] if len(text) > 0 else "0s"

	def __FormatTime(self, minutes):
			if minutes <= 0:
				return "0{}".format(localeinfo.NEW_AFFECT_MIN)

			total_minutes = int(minutes)
			
			hours, rem_minutes = divmod(total_minutes, 60)
			days, rem_hours = divmod(hours, 24)

			text_parts = []
			if days > 0:
				text_parts.append("{}{}".format(days, localeinfo.NEW_AFFECT_DAY))
			if rem_hours > 0:
				text_parts.append("{}{}".format(rem_hours, localeinfo.NEW_AFFECT_HOUR))
			if rem_minutes > 0:
				text_parts.append("{}{}".format(rem_minutes, localeinfo.NEW_AFFECT_MIN))

			result = " ".join(text_parts)

			return result if result else "0{}".format(localeinfo.NEW_AFFECT_MIN)
		
		
	def Refresh(self, leftPart = True, rightPart = True, scrollBarRefresh = True):
		# Don't refresh ranking rows if in HoF mode
		if self.__children.get("hofMode", False) and rightPart:
			return

		global rank_data
		pageIdx = self.__children["pageIdx"]
		selectedIdx = self.__children["selectedIdx"] if self.__children.has_key("selectedIdx") else -1

		pageData = rank_data[pageIdx]
	
		if leftPart:
			leftBgRender = self.__children["leftBgRender"]
			buttonList = []
			for key, data in pageData["dict"].items():
				newItem = CreateWindow(ListItem(data), leftBgRender, [], (0, 0))
				newItem.SetEvent(ui.__mem_func__(self.__ClickItem), "mouse_click", key)
				buttonList.append([newItem, data["index"]])
				if selectedIdx == key:
					newItem.Down()

			yPos = 0
			buttonList.sort(key=ui.__mem_func__(self.__SortRule))
			for data in buttonList:
				if yPos != 0:
					yPos += 8
				data[0].SetPosition(0, yPos, True)
				yPos += data[0].GetHeight()
			self.__children["buttonList"] = buttonList

			if scrollBarRefresh:
				windowHeight = leftBgRender.GetHeight()
				scrollBarLeft = self.__children["scrollBarLeft"]
				scrollBarLeft.SetPos(0)
				if yPos > windowHeight:
					scrollLen = yPos-windowHeight
					scrollBarLeft.SetScale(windowHeight, yPos)
				else:
					scrollLen = 0
					scrollBarLeft.SetScale(windowHeight, windowHeight)
				self.__children["scrollLen"] = scrollLen
			else:
				self.__OnScroll()
	
		if rightPart:
			for j in xrange(11):
				# Show all row backgrounds (new design always shows them)
				self.__children["rowBg" + str(j)].Show()
				self.__children["name" + str(j)].Hide()
				self.__children["level" + str(j)].Hide()
				self.__children["flag" + str(j)].Hide()
				self.__children["value" + str(j)].Hide()


			rankInfo = pageData["dict"][selectedIdx] if selectedIdx != -1 else None

			self.__children["valueTitle"].SetText(rankInfo["title_name"] if rankInfo else "Value")
			if app.__DONATE_RANKING__:
				donateBtn = self.__children.get("donateBtn")
				if donateBtn:
					if pageIdx == player.RANK_TYPE_PLAYER and selectedIdx == DONATION_RANK:
						donateBtn.Show()
					else:
						donateBtn.Hide()

			if rankInfo:
				rankData = rankInfo["dataDict" + str(self.__children["timeIdx"])] if rankInfo.has_key("dataDict" + str(self.__children["timeIdx"])) else {}
				if len(rankData) != 0:
					if rankData["leftTimeUpdate"] > app.GetGlobalTimeStamp():
						self.SetLoadingStatus(False)
						rankDict = rankData["rankDict"]

						mainPlayerName = player.GetName()

						for rankIdx, playerData in rankDict.items():
							original_flag = int(playerData["flag"])
							is_conqueror = original_flag > 10
							display_flag = original_flag % 10 if is_conqueror else original_flag

							# Get all UI elements for this row
							index_obj = self.__children["index" + str(rankIdx)]
							name_obj = self.__children["name" + str(rankIdx)]
							level_obj = self.__children["level" + str(rankIdx)]
							value_obj = self.__children["value" + str(rankIdx)]

							# Colors: top 3 use white (row bg provides distinction), others use light gray
							rankColor = {1 : 0xFFFFFFFF, 2 : 0xFFFFFFFF, 3 : 0xFFFFFFFF}
							base_color = rankColor.get(rankIdx + 1, 0xFFbdc3c7)

							name_obj.SetPackedFontColor(base_color)
							value_obj.SetPackedFontColor(base_color)

							# Set level text and color
							if is_conqueror:
								level_obj.SetText("Cn.{}".format(playerData["level"]))
								level_obj.SetPackedFontColor(0xFFcef1f9)
							else:
								level_obj.SetText("Lv.{}".format(playerData["level"]))
								level_obj.SetPackedFontColor(base_color)

							# Set the rest of the text values
							name_obj.SetText(playerData["name"])
							if selectedIdx == player.RANK_PLAYTIME:
								value_obj.SetText(self.__FormatTime(playerData["value"]))
							else:
								value_obj.SetText(self.__NumberToDecimalString(playerData["value"]))

							# Handle the special '#' row for the local player
							if rankIdx == 10:
								index_obj.SetText(str(playerData["idx"] + 1) if playerData["idx"] != -1 else "#")
								index_obj.SetPackedFontColor(base_color)

							# Show all the elements
							name_obj.Show()
							level_obj.Show()
							value_obj.Show()

							# Hide numbers for top 3 (row bg has built-in medals), show for others
							if rankIdx < 3:
								index_obj.Hide()
							else:
								index_obj.SetPackedFontColor(base_color)
								index_obj.Show()

							# Show the correct empire flag
							self.__children["flag" + str(rankIdx)].LoadImage(IMG_DIR + "newempire_" + str(display_flag) + ".png")
							self.__children["flag" + str(rankIdx)].Show()

							# --- END OF NEW UI LOGIC ---
						return

				if not self.__children["loading"].IsShow():
					net.SendChatPacket("/global_rank _load {} {} {}".format(self.__children["pageIdx"], self.__children["timeIdx"], selectedIdx))
					self.SetLoadingStatus(True)

	def __FormatResetCountdown(self, seconds):
		if seconds <= 0:
			return localeinfo.RANKING_RESET_SOON if hasattr(localeinfo, 'RANKING_RESET_SOON') else "Soon!"
		return localeinfo.SecondToDHMNew(seconds)

		# days = seconds // 86400
		# hours = (seconds % 86400) // 3600
		# mins = (seconds % 3600) // 60

		# if days > 0:
			# return "{}d {}h {}m".format(int(days), int(hours), int(mins))
		# elif hours > 0:
			# return "{}h {}m".format(int(hours), int(mins))
		# else:
			# return "{}m".format(int(mins))

	def __UpdateResetTimer(self):
		resetTimerText = self.__children.get("resetTimerText")
		if not resetTimerText:
			return

		timeIdx = self.__children.get("timeIdx", 0)
		now = app.GetGlobalTimeStamp()

		if timeIdx == 0:  # Weekly
			nextReset = self.__children.get("nextWeeklyReset", 0)
			# prefix = localeinfo.RANKING_RESET_WEEKLY if hasattr(localeinfo, 'RANKING_RESET_WEEKLY') else "Weekly Reset"
		else:  # Monthly
			nextReset = self.__children.get("nextMonthlyReset", 0)
			# prefix = localeinfo.RANKING_RESET_MONTHLY if hasattr(localeinfo, 'RANKING_RESET_MONTHLY') else "Monthly Reset"

		if nextReset > 0:
			remaining = nextReset - now
			if remaining > 0:
				text = "{}".format(self.__FormatResetCountdown(remaining))
				# Turn red when less than 24 hours
				if remaining < 86400:
					resetTimerText.SetPackedFontColor(0xFFFF6B6B)
				else:
					resetTimerText.SetPackedFontColor(0xFFCCCCCC)
			else:
				text = "{}".format(localeinfo.RANKING_RESET_SOON if hasattr(localeinfo, 'RANKING_RESET_SOON') else "Soon!")
				resetTimerText.SetPackedFontColor(0xFFFF6B6B)
			resetTimerText.SetText(text)
			resetTimerText.SetOutline()
		else:
			resetTimerText.SetText("")

	def OnUpdate(self):
		loadingImg = self.__children["loading"] if self.__children.has_key("loading") else None
		if loadingImg:
			if loadingImg.IsShow():
				loadingImgRotation = self.__children["loadingImgRotation"] if self.__children.has_key("loadingImgRotation") else 0.0
				loadingImg.SetRotation(loadingImgRotation)
				self.__children["loadingImgRotation"] = loadingImgRotation + app.GetRandom(15, 40)

		# Update reset timer display
		self.__UpdateResetTimer()

	def __OnScroll(self):
		scrollBar = self.__children["scrollBarLeft"]
		basePos = int(scrollBar.GetPos()*(self.__children["scrollLen"] if self.__children.has_key("scrollLen") else 0))

		buttonList = self.__children["buttonList"] if self.__children.has_key("buttonList") else []
		for child in buttonList:
			(ex, ey) = child[0].exPos
			child[0].SetPosition(ex, ey-(basePos))

	#def __OnMouseWheelSpecial(self, length):
	#	scrollBar = self.__children["scrollBarLeft"]
	#	if scrollBar:
	#		if scrollBar.IsShow():
	#			scrollBar.OnMouseWheel(length)
	#			return True
	#	return False

	def OnRunMouseWheel(self, iLen):
		scrollBar = self.__children["scrollBarLeft"]
		if scrollBar and scrollBar.IsShow():
			leftBgRender = self.__children["leftBgRender"]
			if leftBgRender and leftBgRender.IsInPosition():
				scrollBar.OnMouseWheel(iLen)
				return True

		return False

	def Open(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "RANKING")
		self.Refresh()
		self.Show()
		self.SetTop()

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "RANKING")
		self.__OnOverOutReward()
		if app.__DONATE_RANKING__:
			dw = self.__children.get("donationWnd")
			if dw:
				dw.Close()
				self.__children["donationWnd"] = None
		self.Hide()

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("RANKING", x, y)

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def __OverOut(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.HideToolTip()

	def __OverIn(self, result):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			if isinstance(result, str):
				interfaceHandler.tooltipItem.ClearToolTip()
				interfaceHandler.tooltipItem.AppendTextLine(result)
				interfaceHandler.tooltipItem.ShowToolTip()

class ListItem(ui.RadioButton):
	def __init__(self, data):
		ui.RadioButton.__init__(self)
		self.__LoadData(data)
	def Destroy(self):
		self.__children={}
	def __LoadData(self, data):
		self.Destroy()
		self.SetUpVisual(REWORK_DIR+"btn_1.png")
		self.SetOverVisual(REWORK_DIR+"btn_2.png")
		self.SetDownVisual(REWORK_DIR+"btn_3.png")
		self.__children["avatar"] = CreateWindow(ui.ExpandedImageBox(), self, ["not_pick"], (55+85, 0), IMG_DIR+data["image"])
		textList = []
		textSplit = data["name"].split("#")
		for text in textSplit:
			idx = textSplit.index(text)
			textList.append(CreateWindow(ui.TextLine(), self, ["not_pick"], (55+90 - 20, 7 + (idx * 12) - 3), text))
		self.__children["textList"] = textList

def CreateWindow(window, parent, windowFlags, windowPos, windowArgument = "", windowPositionRule = "", windowSize = (-1, -1), windowFontName = -1):
	window.SetParent(parent)
	for flag in windowFlags:
		window.AddFlag(flag)
	window.SetPosition(*windowPos)
	if windowSize != (-1, -1):
		window.SetSize(*windowSize)
	if windowPositionRule:
		splitList = windowPositionRule.split(":")
		if len(splitList) == 2:
			(type, mode) = (splitList[0], splitList[1])
			if type == "horizontal":
				if isinstance(window, ui.TextLine):
					if mode == "center":
						window.SetHorizontalAlignCenter()
					elif mode == "right":
						window.SetHorizontalAlignRight()
					elif mode == "left":
						window.SetHorizontalAlignLeft()
				else:
					if mode == "center":
						window.SetWindowHorizontalAlignCenter()
					elif mode == "right":
						window.SetWindowHorizontalAlignRight()
					elif mode == "left":
						window.SetWindowHorizontalAlignLeft()
			elif type == "vertical":
				if isinstance(window, ui.TextLine):
					if mode == "center":
						window.SetVerticalAlignCenter()
					elif mode == "top":
						window.SetVerticalAlignTop()
					elif mode == "bottom":
						window.SetVerticalAlignBottom()
				else:
					if mode == "top":
						window.SetWindowVerticalAlignTop()
					elif mode == "center":
						window.SetWindowVerticalAlignCenter()
					elif mode == "bottom":
						window.SetWindowVerticalAlignBottom()
	if windowArgument:
		if isinstance(window, ui.TextLine):
			if windowFontName != -1:
				window.SetFontName(windowFontName)
			window.SetText(windowArgument)
		elif isinstance(window, ui.NumberLine):
			window.SetNumber(windowArgument)
		elif isinstance(window, ui.Button) or isinstance(window, ui.RadioButton) or isinstance(window, ui.ToggleButton):
			if isinstance(windowArgument, list):
				window.SetUpVisual(windowArgument[0])
				window.SetOverVisual(windowArgument[1] if len(windowArgument) >= 2 else windowArgument[0])
				window.SetDownVisual(windowArgument[2] if len(windowArgument) >= 3 else windowArgument[0])
				if len(windowArgument) == 4:
					window.SetDisableVisual(windowArgument[3])
		elif isinstance(window, ui.ExpandedImageBox) or isinstance(window, ui.ImageBox):
			window.LoadImage(windowArgument if windowArgument.find("gr2") == -1 else "icon/item/27995.tga")
	window.Show()
	return window

class ScrollBarSpecial(ui.Window):
	BASE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
	CORNERS_AND_LINES_COLOR = grp.GenerateColor(0.3411, 0.3411, 0.3411, 1.0)
	BAR_NUMB = 9
	SCROLL_WIDTH= 8
	class MiddleBar(ui.DragButton):
		MIDDLE_BAR_COLOR = grp.GenerateColor(0.6470, 0.6470, 0.6470, 1.0)
		def __init__(self, horizontal_scroll):
			ui.DragButton.__init__(self)
			self.AddFlag("movable")
			self.horizontal_scroll = horizontal_scroll
			self.middle = ui.Bar()
			self.middle.SetParent(self)
			self.middle.AddFlag("attach")
			self.middle.AddFlag("not_pick")
			self.middle.SetColor(self.MIDDLE_BAR_COLOR)
			self.middle.SetSize(1, 1)
			self.middle.Show()
		def SetStaticScale(self, size):
			(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
			if not self.horizontal_scroll:
				ui.DragButton.SetSize(self, base_width, size)
				self.middle.SetSize(base_width, size)
			else:
				ui.DragButton.SetSize(self, size, base_height)
				self.middle.SetSize(size, base_height)
		def SetSize(self, selfSize, fullSize):
			(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
			
			if not self.horizontal_scroll:
				ui.DragButton.SetSize(self, base_width, truediv(int(selfSize), int(fullSize)) * selfSize)
				self.middle.SetSize(base_width, truediv(int(selfSize), int(fullSize)) * selfSize)
			else:
				ui.DragButton.SetSize(self, truediv(int(selfSize), int(fullSize)) * selfSize, base_height)
				self.middle.SetSize(truediv(int(selfSize), int(fullSize)) * selfSize, base_height)
		def SetStaticSize(self, size):
			size = max(2, size)
			
			if not self.horizontal_scroll:
				ui.DragButton.SetSize(self, size, self.middle.GetHeight())
				self.middle.SetSize(size, self.middle.GetHeight())
			else:
				ui.DragButton.SetSize(self, self.middle.GetWidth(), size)
				self.middle.SetSize(self.middle.GetWidth(), size)
	def __init__(self, horizontal_scroll = False):
		ui.Window.__init__(self)
		self.horizontal_scroll = horizontal_scroll
		self.scrollEvent = None
		self.scrollSpeed = 50
		self.sizeScale = 1.0
		self.bars = []
		for i in xrange(self.BAR_NUMB):
			br = ui.Bar()
			br.SetParent(self)
			br.AddFlag("attach")
			br.AddFlag("not_pick")
			br.SetColor([self.CORNERS_AND_LINES_COLOR, self.BASE_COLOR][i == (self.BAR_NUMB-1)])
			if not (i % 2 == 0): br.SetSize(1, 1)
			br.Show()
			self.bars.append(br)
		self.middleBar = self.MiddleBar(self.horizontal_scroll)
		self.middleBar.SetParent(self)
		self.middleBar.SetMoveEvent(ui.__mem_func__(self.OnScrollMove))
		self.middleBar.Show()
	def OnScrollMove(self):
		if not self.scrollEvent:
			return
		arg = float(self.middleBar.GetLocalPosition()[1] - 1) / float(self.GetHeight() - 2 - self.middleBar.GetHeight()) if not self.horizontal_scroll else\
				float(self.middleBar.GetLocalPosition()[0] - 1) / float(self.GetWidth() - 2 - self.middleBar.GetWidth())
		self.scrollEvent(arg)
	def SetScrollEvent(self, func):
		self.scrollEvent = func
	def SetScrollSpeed(self, speed):
		self.scrollSpeed = speed
	def OnMouseWheel(self, length):
		if not self.IsShow():
			return False
		length = int((length * 0.01) * self.scrollSpeed)
		if not self.horizontal_scroll:
			val = min(max(1, self.middleBar.GetLocalPosition()[1] - (length * 0.01) * self.scrollSpeed * self.sizeScale), self.GetHeight() - self.middleBar.GetHeight() - 1)
			self.middleBar.SetPosition(1, val)
		else:
			val = min(max(1, self.middleBar.GetLocalPosition()[0] - (length * 0.01) *  self.scrollSpeed * self.sizeScale), self.GetWidth() - self.middleBar.GetWidth() - 1)
			self.middleBar.SetPosition(val, 1)
		self.OnScrollMove()
		return True
	def GetPos(self):
		return float(self.middleBar.GetLocalPosition()[1] - 1) / float(self.GetHeight() - 2 - self.middleBar.GetHeight()) if not self.horizontal_scroll else float(self.middleBar.GetLocalPosition()[0] - 1) / float(self.GetWidth() - 2 - self.middleBar.GetWidth())
	def OnMouseLeftButtonDown(self):
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		if not self.horizontal_scroll:
			if xMouseLocalPosition == 0 or xMouseLocalPosition == self.GetWidth():
				return
			y_pos = (yMouseLocalPosition - self.middleBar.GetHeight() / 2)
			self.middleBar.SetPosition(1, y_pos)
		else:
			if yMouseLocalPosition == 0 or yMouseLocalPosition == self.GetHeight():
				return
			x_pos = (xMouseLocalPosition - self.middleBar.GetWidth() / 2)
			self.middleBar.SetPosition(x_pos, 1)
		self.OnScrollMove()
	def SetSize(self, w, h):
		(width, height) = (max(3, w), max(3, h))
		ui.Window.SetSize(self, width, height)
		self.bars[0].SetSize(1, (height - 2))
		self.bars[0].SetPosition(0, 1)
		self.bars[2].SetSize((width - 2), 1)
		self.bars[2].SetPosition(1, 0)
		self.bars[4].SetSize(1, (height - 2))
		self.bars[4].SetPosition((width - 1), 1)
		self.bars[6].SetSize((width - 2), 1)
		self.bars[6].SetPosition(1, (height - 1))
		self.bars[8].SetSize((width - 2), (height - 2))
		self.bars[8].SetPosition(1, 1)
		self.bars[1].SetPosition(0, 0)
		self.bars[3].SetPosition((width - 1), 0)
		self.bars[5].SetPosition((width - 1), (height - 1))
		self.bars[7].SetPosition(0, (height - 1))
		if not self.horizontal_scroll:
			self.middleBar.SetStaticSize(width - 2)
			self.middleBar.SetSize(12, self.GetHeight())
		else:
			self.middleBar.SetStaticSize(height - 2)
			self.middleBar.SetSize(12, self.GetWidth())
		self.middleBar.SetRestrictMovementArea(1, 1, width - 2, height - 2)
	def SetScale(self, selfSize, fullSize):
		self.sizeScale = float(selfSize)/float(fullSize)
		if self.sizeScale <= 0.0305:
			self.sizeScale = 0.05
		self.middleBar.SetSize(selfSize, fullSize)
	def SetStaticScale(self, r_size):
		self.middleBar.SetStaticScale(r_size)
	def SetPosScale(self, fScale):
		pos = (math.ceil((self.GetHeight() - 2 - self.middleBar.GetHeight()) * fScale) + 1) if not self.horizontal_scroll else (math.ceil((self.GetWidth() - 2 - self.middleBar.GetWidth()) * fScale) + 1)
		self.SetPos(pos)
	def SetPos(self, pos):
		wPos = (1, pos) if not self.horizontal_scroll else (pos, 1)
		self.middleBar.SetPosition(*wPos)

if app.__DONATE_RANKING__:
	class DonationWindow(ui.ScriptWindow):
		GOLD_PER_CHEQUE = 100000000
		MIN_GOLD        = 1000000
		GOLD_STEPS      = (1000000, 10000000, 100000000)  # +1M, +10M, +100M
		CHEQUE_STEPS    = (1, 10, 100)                    # +1, +10, +100

		def __init__(self):
			ui.ScriptWindow.__init__(self)
			self.isOpen   = False
			self.currency = "gold"  # "gold" or "cheque"
			self.AddBtns  = []
			self.questionDialog = None
			self.__Build()
			self.AddFlag("attach")
			if app.ENABLE_WINDOW_SLIDE_EFFECT:
				self.AddFlag("animated_board")

		def __del__(self):
			ui.ScriptWindow.__del__(self)

		# ---------- helpers ----------
		def _clean_int(self, s):
			txt = (s or "").strip()
			digits = "".join(ch for ch in txt if ch.isdigit())
			return int(digits or "0")

		def _fmt_gold(self, n):
			try:
				return localeinfo.NumberToStringDotted(int(n))
			except:
				return "{:,}".format(int(n)).replace(",", ".")

		def _get_amount(self):
			try:
				raw = self.AmountEdit.GetDisplayText()
			except:
				raw = self.AmountEdit.GetText()
			return self._clean_int(raw)

		def _set_amount(self, amt):
			if self.currency == "gold":
				amt = max(self.MIN_GOLD, int(amt))
				self.AmountEdit.SetText(self._fmt_gold(amt))
			else:
				self.AmountEdit.SetText(str(max(0, int(amt))))

		def _step_values(self):
			return self.GOLD_STEPS if self.currency == "gold" else self.CHEQUE_STEPS

		def _update_quick_buttons(self):
			steps = self._step_values()
			for i, b in enumerate(self.AddBtns):
				if self.currency == "gold":
					b.SetText("+%dM" % (steps[i] // 1000000))
				else:
					b.SetText("+%dW" % steps[i])
				b.SetEvent(lambda idx=i: self._add_step(idx))

		def _add_step(self, idx):
			steps = self._step_values()
			cur   = self._get_amount()
			self._set_amount(cur + steps[idx])

		def _refresh_ui_for_currency(self):
			try:
				placeholder = localeinfo.RANKING_DONATE_AMOUNT if self.currency == "gold" else localeinfo.CHEQUE_SYSTEM_UNIT_WON
				self.AmountEdit.SetOverlayCoupon(placeholder, 120)
			except:
				pass

			self._silentClearAmount()

			self._update_quick_buttons()

			if self.currency == "gold":
				self._set_amount(self.MIN_GOLD)

		def _update_conversion_hint(self):
			amt = self._get_amount()
			if self.currency == "gold":
				cheques = amt // self.GOLD_PER_CHEQUE
				rem     = amt %  self.GOLD_PER_CHEQUE
				if cheques > 0 and rem > 0:
					self.ConvLabel.SetText("? %d cheque + %s yang" % (cheques, self._fmt_gold(rem)))
				elif cheques > 0:
					self.ConvLabel.SetText("? %d cheque" % cheques)
				else:
					self.ConvLabel.SetText("? 0 cheque")
			else:
				gold = amt * self.GOLD_PER_CHEQUE
				self.ConvLabel.SetText("? %s yang" % self._fmt_gold(gold))

		# ---------------- internal UI build ----------------
		def __Build(self):
			# Frame
			self.Board = ui.BoardWithTitleBar()
			self.Board.SetSize(260, 150 + 30)
			self.Board.SetCenterPosition()
			self.Board.AddFlag("movable")
			self.Board.AddFlag("float")
			self.Board.AddFlag("attach")
			self.Board.SetTitleName(localeinfo.RANKING_DONATE_TITLE)
			self.Board.SetCloseEvent(self.Close)
			self.Board.Hide()

			# Background
			self.Bg = ui.ThinBoard()
			self.Bg.SetParent(self.Board)
			self.Bg.SetSize(240, 105 + 30)
			self.Bg.SetPosition(10, 35)
			self.Bg.Show()

			# Currency toggle (Gold / Cheque)
			self.GoldBtn = ui.RadioButton(); self.ChequeBtn = ui.RadioButton()
			for i, (btn, text) in enumerate(((self.GoldBtn, localeinfo.CHEQUE_SYSTEM_UNIT_YANG), (self.ChequeBtn, localeinfo.CHEQUE_SYSTEM_UNIT_WON))):
				btn.SetParent(self.Bg)
				btn.SetUpVisual("d:/ymir work/ui/game/gameoption/radio_unselected.tga")
				btn.SetOverVisual("d:/ymir work/ui/game/gameoption/radio_unselected.tga")
				btn.SetDownVisual("d:/ymir work/ui/game/gameoption/radio_selected.tga")
				btn.SetText(text)
				btn.SetTextPosition(-20,0)
				btn.SetPosition(80 + i*80, 8)
				btn.Show()
			self.GoldBtn.SAFE_SetEvent(self.__SetCurrency, "gold")
			self.ChequeBtn.SAFE_SetEvent(self.__SetCurrency, "cheque")

			# Rate hint
			self.Rate = ui.TextLine()
			self.Rate.SetParent(self.Bg)
			self.Rate.SetPosition(170, 12)
			self.Rate.SetText("1 Cheque = %s" % self._fmt_gold(self.GOLD_PER_CHEQUE))
			self.Rate.Hide()

			# Label
			self.Label = ui.TextLine()
			self.Label.SetParent(self.Bg)
			self.Label.SetText("the amount:")
			self.Label.SetPosition(12, 40)
			self.Label.Hide()

			# Amount edit background
			self.AmountBg = ui.ImageBox()
			self.AmountBg.SetParent(self.Bg)
			self.AmountBg.SetPosition(12, 35 + 30)
			self.AmountBg.SetSize(120, 25)
			try:
				self.AmountBg.LoadImage("d:/ymir work/ui/coupon/editline_bg.tga")
			except:
				pass
			self.AmountBg.Show()

			# Amount edit line
			self.AmountEdit = ui.EditLine()
			self.AmountEdit.SetParent(self.AmountBg)
			self.AmountEdit.SetSize(self.AmountBg.GetWidth() - 4, self.AmountBg.GetHeight() - 4)
			self.AmountEdit.SetPosition(-5, 4)
			self.AmountEdit.SetMax(16)
			self.AmountEdit.SetLimitWidth(self.AmountBg.GetWidth() - 4)
			self.AmountEdit.SetEscapeEvent(ui.__mem_func__(self.ClearAmount))  # clear on ESC
			try:
				self.AmountEdit.SetOverlayCoupon(localeinfo.RANKING_DONATE_AMOUNT,200)
				self.AmountEdit.SetNumberMode()
			except:
				pass
			self.AmountEdit.Show()

			# Quick add buttons
			self.AddBtns = []
			for idx in range(3):
				b = ui.Button()
				b.SetParent(self.Bg)
				b.SetPosition(50 + idx * 48, 10 + 30)
				b.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
				b.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
				b.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
				b.Show()
				self.AddBtns.append(b)

			# Conversion label
			self.ConvLabel = ui.TextLine()
			self.ConvLabel.SetParent(self.Bg)
			self.ConvLabel.SetPosition(12, 90)
			self.ConvLabel.SetText("")
			self.ConvLabel.Show()

			# Confirm
			self.Confirm = ui.Button()
			self.Confirm.SetParent(self.Bg)
			self.Confirm.SetPosition(120, 70 + 30)
			try:
				self.Confirm.SetUpVisual("d:/ymir work/ui/coupon/enter_1.png")
				self.Confirm.SetOverVisual("d:/ymir work/ui/coupon/enter_2.png")
				self.Confirm.SetDownVisual("d:/ymir work/ui/coupon/enter_3.png")
			except:
				self.Confirm.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
				self.Confirm.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
				self.Confirm.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
			self.Confirm.SetText(localeinfo.RANKING_DONATE_SUBMIT)
			self.Confirm.SetEvent(self.__DoDonate)
			self.Confirm.Show()

			# Cancel
			self.Cancel = ui.Button()
			self.Cancel.SetParent(self.Bg)
			self.Cancel.SetPosition(50-25, 70 + 30)
			try:
				self.Cancel.SetUpVisual("d:/ymir work/ui/coupon/cancel_1.png")
				self.Cancel.SetOverVisual("d:/ymir work/ui/coupon/cancel_2.png")
				self.Cancel.SetDownVisual("d:/ymir work/ui/coupon/cancel_3.png")
			except:
				self.Cancel.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
				self.Cancel.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
				self.Cancel.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
			self.Cancel.SetText(localeinfo.RANKING_DONATE_CANCEL)
			self.Cancel.SetEvent(self.Close)
			self.Cancel.Show()

			# defaults
			self.__SetCurrency("gold", init=True)

		# ---------------- behavior ----------------
		def __SetCurrency(self, cur, init=False):
			if cur == self.currency and not init:
				return
			self.currency = cur
			if self.currency == "gold":
				self.GoldBtn.Down(); self.ChequeBtn.SetUp()
			else:
				self.ChequeBtn.Down(); self.GoldBtn.SetUp()
			self._refresh_ui_for_currency()

		def Open(self):
			self.Board.SetCenterPosition()
			self.Board.SetTop()
			self.Board.Show()
			self.isOpen = True
			# if self.currency == "gold":
				# self._set_amount(self.MIN_GOLD)
			self.AmountEdit.SetFocus()

		def ClearAmount(self):
			try:
				raw = self.AmountEdit.GetDisplayText()
			except:
				raw = self.AmountEdit.GetText()
			txt = (raw or "").strip()

			if txt and any(ch.isdigit() for ch in txt):
				self.AmountEdit.SetText("")
			else:
				self.Close()

		def _silentClearAmount(self):
			self.AmountEdit.SetText("")


		def Close(self):
			self.Board.Hide()
			self.isOpen = False
			self.OnCloseQuestionDialog() 

		def OpenWindow(self):
			if self.isOpen: self.Close()
			else: self.Open()

		def Destroy(self):
			self.Close()

		def OnPressEscapeKey(self):
			self.Close()
			return True

		# def OnUpdate(self):
			# # live conversion
			# if self.isOpen:
				# self._update_conversion_hint()

		def __DoDonate(self):
			amt = self._get_amount()
			# normalize & validate BEFORE confirming, so the text mirrors the real donation
			if self.currency == "gold":
				if amt < self.MIN_GOLD:
					amt = self.MIN_GOLD
			else:
				if amt < 1:
					return
			self._confirmDonation(self.currency, amt)


		def _confirmDonation(self, currency, amt):
			import uicommon
			self.OnCloseQuestionDialog()

			# Build clear, exact message
			if currency == "gold":
				msg = localeinfo.RANKING_DONATE_QUESTION1 % self._fmt_gold(amt)
			else:
				gold_eq = amt * self.GOLD_PER_CHEQUE
				msg = localeinfo.RANKING_DONATE_QUESTION3 % (amt, self._fmt_gold(gold_eq))

			qd = uicommon.QuestionDialog()
			qd.SetText(msg)
			qd.SetAcceptEvent(lambda c=currency, a=amt: self._sendDonation(c, a))
			qd.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
			qd.Open()
			self.questionDialog = qd

		def OnCloseQuestionDialog(self):
			if self.questionDialog:
				try:
					self.questionDialog.Close()
				except:
					pass
				self.questionDialog = None

		def _sendDonation(self, currency, amt):
			# Fire the command exactly as discussed, then clean up dialog + window
			try:
				if currency == "gold":
					net.SendChatPacket("/donate %d" % amt)
				else:
					net.SendChatPacket("/donate cheque %d" % amt)
			except:
				if currency == "gold":
					net.SendChatPacket(" donate %d" % amt)
				else:
					net.SendChatPacket(" donate cheque %d" % amt)
			self.OnCloseQuestionDialog()
			#self.Close()