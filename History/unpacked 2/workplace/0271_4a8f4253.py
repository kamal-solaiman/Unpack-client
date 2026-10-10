# coding: latin_1

import app
import net
import player

import ui
import localeinfo
import uiscriptlocale
import mousemodule
import snd
import guild
import chat
import uicommon

GUILD_DRAGONLAIR_TYPE_RED = 1
GUILD_DRAGONLAIR_TYPE_BLUE = 2
GUILD_DRAGONLAIR_TYPE_GREEN = 3

class GuildDragonLairRankingDialog(ui.ScriptWindow):
	SLOT_RANKING = 0
	SLOT_GUILDNAME = 1
	SLOT_MEMBERCOUNT =2
	SLOT_CLEARTIME = 3
	if app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
		MAX_LINE_COUNT = 10
		RANK_1 = 0
		RANK_2 = 1
		RANK_3 = 2
	else:
		MAX_LINE_COUNT = 5

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.isLoaded = 0
		self.NowStartLineNumber = 0
		self.DragonLairType = 0
		self.IsShow = False
		self.board = None
		if not app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
			self.ScrollBar = None
		self.ResultButtonList = []
		self.ResultSlotList = {}
		self.MyResultSlotList = []
		if app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
			self.ResultButtonRankList = []

		self.ClearDragonLairRanking()

		self.LoadWindow()
		self.MakeUiBoard()

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		self.isLoaded = 0
		self.NowStartLineNumber = 0
		self.DragonLairType = 0
		self.IsShow = False
		self.board = None
		if not app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
			self.ScrollBar = None
		self.ResultButtonList = []
		self.ResultSlotList = {}
		self.MyResultSlotList = []
		if app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
			self.ResultButtonRankList = []

		self.ClearDragonLairRanking()

	def Destory(self):
		self.Close()
		self.isLoaded = 0
		self.NowStartLineNumber = 0
		self.DragonLairType = 0
		self.IsShow = False
		self.board = None
		if not app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
			self.ScrollBar = None
		self.ResultButtonList = []
		self.ResultSlotList = {}
		self.MyResultSlotList = []
		if app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
			self.ResultButtonRankList = []

		self.ClearDragonLairRanking()

	def Open(self,type):
		if not self.IsShow:
			self.IsShow = True
			self.SetCenterPosition()
			self.SetTop()
			self.NowStartLineNumber = 0
			self.DragonLairType = type
			if not app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
				self.ScrollBar.SetPos(0)
			ui.ScriptWindow.Show(self)

	def Close(self):
		self.IsShow = False
		self.NowStartLineNumber = 0

		self.ClearDragonLairRanking()

		self.Hide()

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/GuildWindow_GuildDragonLairRanking.py")
		except:
			import exception
			exception.Abort("GuildWindow_GuildDragonLairWindow.__LoadWindow.LoadScript")
		try:
			getObject = self.GetChild
			self.board = getObject("TitleBar")
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
			if not app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
				self.ScrollBar = getObject("GuildDragonLairScrollBar")
				self.ScrollBar.SetScrollEvent(ui.__mem_func__(self.OnScrollControl))
			if localeinfo.IsARABIC():
				self.GetChild("leftcenterImg").LeftRightReverse()
				self.GetChild("rightcenterImg").LeftRightReverse()
				self.GetChild("LeftTop").LeftRightReverse()
				self.GetChild("RightTop").LeftRightReverse()
				self.GetChild("LeftBottom").LeftRightReverse()
				self.GetChild("RightBottom").LeftRightReverse()
				self.GetChild("LeftTopSelf").LeftRightReverse()
				self.GetChild("RightTopSelf").LeftRightReverse()
				self.GetChild("LeftBottomSelf").LeftRightReverse()
				self.GetChild("RightBottomSelf").LeftRightReverse()
				self.topcenterimg = self.GetChild("topcenterImg")
				self.topcenterimg.SetPosition(self.GetWidth()-30,38-5)
				self.bottomcenterImg = self.GetChild("bottomcenterImg")
				self.bottomcenterImg.SetPosition(self.GetWidth()-30,173+118-5)
				self.centerImg = self.GetChild("centerImg")
				self.centerImg.SetPosition(self.GetWidth()-30,38+15-5)

				self.topcenterimg = self.GetChild("topcenterImgSelf")
				self.topcenterimg.SetPosition(self.GetWidth()-30,190+120-5)
				self.bottomcenterImg = self.GetChild("bottomcenterImgSelf")
				self.bottomcenterImg.SetPosition(self.GetWidth()-30,190+15+120-5)
		except:
			import exception
			exception.Abort("GuildWindow_GuildDragonLairWindow.__LoadWindow.SetObject")

	def MakeUiBoard(self):
		try:
			yPos = 0
			for i in range(0, self.MAX_LINE_COUNT + 1):
				if app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
					yPos = 60 + i * 24
					if i == 10:
						yPos += 10
				else:
					yPos = 65 + i * 24
					if i == 5:
						yPos += 10

				RankingSlotImage = ui.MakeImageBox(self, "d:/ymir work/ui/public/parameter_slot_00.sub", 23, yPos)
				RankingSlotImage.SetAlpha(0)
				RankingSlot = ui.MakeTextLine(RankingSlotImage)
				self.Children.append(RankingSlotImage)
				self.Children.append(RankingSlot)

				GuildNameImage = ui.MakeImageBox(self, "d:/ymir work/ui/public/parameter_slot_04.sub", 77, yPos)
				GuildNameImage.SetAlpha(0)
				GuildNameSlot = ui.MakeTextLine(GuildNameImage)
				self.Children.append(GuildNameImage)
				self.Children.append(GuildNameSlot)

				MemberCountSlotImage = ui.MakeImageBox(self, "d:/ymir work/ui/public/parameter_slot_00.sub", 205, yPos)
				MemberCountSlotImage.SetAlpha(0)
				MemberCountSlot = ui.MakeTextLine(MemberCountSlotImage)
				self.Children.append(MemberCountSlotImage)
				self.Children.append(MemberCountSlot)

				ClearTimeSlotImage = ui.MakeImageBox(self, "d:/ymir work/ui/public/parameter_slot_00.sub", 270, yPos)
				ClearTimeSlotImage.SetAlpha(0)
				ClearTimeSlot = ui.MakeTextLine(ClearTimeSlotImage)
				self.Children.append(ClearTimeSlotImage)
				self.Children.append(ClearTimeSlot)

				if i < self.MAX_LINE_COUNT:
					tempguildlankingslotlist = []
					tempguildlankingslotlist.append(RankingSlot)
					tempguildlankingslotlist.append(GuildNameSlot)
					tempguildlankingslotlist.append(MemberCountSlot)
					tempguildlankingslotlist.append(ClearTimeSlot)
					self.ResultSlotList[i] = tempguildlankingslotlist
				else:
					self.MyResultSlotList.append(RankingSlot)
					self.MyResultSlotList.append(GuildNameSlot)
					self.MyResultSlotList.append(MemberCountSlot)
					self.MyResultSlotList.append(ClearTimeSlot)

				itemSlotButtonImage = ui.MakeButton(self, 21, yPos, "", "d:/ymir work/ui/game/guild/dragonlairranking/", "ranking_list_button01.sub", "ranking_list_button02.sub", "ranking_list_button02.sub")
				itemSlotButtonImage.Show()
				itemSlotButtonImage.Disable()
				self.Children.append(itemSlotButtonImage)
				if localeinfo.IsARABIC():
					itemSlotButtonImage.LeftRightReverse()
					itemSlotButtonImage.SetPosition(24, yPos)

				if i < self.MAX_LINE_COUNT:
					self.ResultButtonList.append(itemSlotButtonImage)

				if app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
					if i == self.RANK_1:
						RankingRoundImage = ui.MakeImageBox(self, "d:/ymir work/ui/public/ranking_guild_gold.sub", 20, yPos-1)
						RankingRoundImage.Show()
						self.Children.append(RankingRoundImage)
						self.ResultButtonRankList.append(RankingRoundImage)
					elif i == self.RANK_2:
						RankingRoundImage = ui.MakeImageBox(self, "d:/ymir work/ui/public/ranking_guild_silver.sub", 20, yPos-1)
						RankingRoundImage.Show()
						self.Children.append(RankingRoundImage)
						self.ResultButtonRankList.append(RankingRoundImage)
					elif i == self.RANK_3:
						RankingRoundImage = ui.MakeImageBox(self, "d:/ymir work/ui/public/ranking_guild_brown.sub", 20, yPos-1)
						RankingRoundImage.Show()
						self.Children.append(RankingRoundImage)
						self.ResultButtonRankList.append(RankingRoundImage)

				if localeinfo.IsARABIC():
					RankingSlotImage.SetPosition(self.GetWidth() - (37 + 25), yPos)
					GuildNameImage.SetPosition(self.GetWidth() - (160 + 25), yPos)
					MemberCountSlotImage.SetPosition(self.GetWidth() - (223 + 25), yPos)
					ClearTimeSlotImage.SetPosition(self.GetWidth() - (287 + 25), yPos)

		except:
			import exception
			exception.Abort("GuildWindow_GuildDragonLairWindow.MakeUiBoard")

	def GetDragonLairType(self):
		return self.DragonLairType

	def RefreshGuildDragonLairRanking(self, type):
		self.AllClear()
		for line, ResultSlotList in self.ResultSlotList.items():
			nowindex = line + self.NowStartLineNumber
			if nowindex >= self.GetRedDragonLairRankingShowCount():
				break
			if type == GUILD_DRAGONLAIR_TYPE_RED:
				(guildname, membercount, min, sec) = self.GetRedDragonLairRanking(nowindex)
			elif type == GUILD_DRAGONLAIR_TYPE_BLUE:
				pass
			elif type == GUILD_DRAGONLAIR_TYPE_GREEN:
				pass

			ResultSlotList[self.SLOT_RANKING].SetText(str(nowindex+1))
			ResultSlotList[self.SLOT_GUILDNAME].SetText(guildname)
			ResultSlotList[self.SLOT_MEMBERCOUNT].SetText(str(membercount))
			ResultSlotList[self.SLOT_CLEARTIME].SetText(self.GetClearTimeStr(min,sec))
			self.ResultButtonList[line].Show()

			if app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
				if nowindex == self.RANK_1:
					self.ResultButtonRankList[self.RANK_1].Show()
				elif nowindex == self.RANK_2:
					self.ResultButtonRankList[self.RANK_2].Show()
				elif nowindex == self.RANK_3:
					self.ResultButtonRankList[self.RANK_3].Show()

			if guild.IsGuildEnable():
				if guild.GetGuildName() == guildname:
					self.ResultButtonList[line].Down()

		if guild.IsGuildEnable():
			MyResult = True
			if MyResult: # guild.IsDragonLairClearGuild(type):
				(ranking, membercount, min, sec) = self.GetMyRedDragonLairRanking(type)
				if ranking:
					self.MyResultSlotList[self.SLOT_RANKING].SetText(str(ranking))
				else:
					self.MyResultSlotList[self.SLOT_RANKING].SetText("-")
				self.MyResultSlotList[self.SLOT_GUILDNAME].SetText(guild.GetGuildName())
				self.MyResultSlotList[self.SLOT_MEMBERCOUNT].SetText(str(membercount))
				self.MyResultSlotList[self.SLOT_CLEARTIME].SetText(self.GetClearTimeStr(min,sec))
			else:
				self.MyResultSlotList[self.SLOT_RANKING].SetText("-")
				self.MyResultSlotList[self.SLOT_GUILDNAME].SetText("-")
				self.MyResultSlotList[self.SLOT_MEMBERCOUNT].SetText("-")
				self.MyResultSlotList[self.SLOT_CLEARTIME].SetText("-")

		if not app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
			self.ScrollBar.SetMiddleBarSize(float(self.MAX_LINE_COUNT) / float(self.CheckNowItemCount()))

	def GetClearTimeStr(self, min, sec):
		strcleartime = ""
		if min == 0:
			strcleartime = str(sec) + localeinfo.GUILD_DRAGONLAIR_SECOND
		elif sec == 0:
			strcleartime = str(min) + localeinfo.GUILD_DRAGONLAIR_MIN
		else:
			strcleartime = str(min) + localeinfo.GUILD_DRAGONLAIR_MIN + str(sec) + localeinfo.GUILD_DRAGONLAIR_SECOND
		return strcleartime

	def AllClear(self):
		for line, ResultSlotList in self.ResultSlotList.items():
			ResultSlotList[self.SLOT_RANKING].SetText("")
			ResultSlotList[self.SLOT_GUILDNAME].SetText("")
			ResultSlotList[self.SLOT_MEMBERCOUNT].SetText("")
			ResultSlotList[self.SLOT_CLEARTIME].SetText("")
			self.ResultButtonList[line].SetUp()
			self.ResultButtonList[line].Hide()
		self.MyResultSlotList[self.SLOT_RANKING].SetText("-")
		self.MyResultSlotList[self.SLOT_GUILDNAME].SetText("-")
		self.MyResultSlotList[self.SLOT_MEMBERCOUNT].SetText("-")
		self.MyResultSlotList[self.SLOT_CLEARTIME].SetText("-")

		if app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
			self.ResultButtonRankList[self.RANK_1].Hide()
			self.ResultButtonRankList[self.RANK_2].Hide()
			self.ResultButtonRankList[self.RANK_3].Hide()

	def CheckNowItemCount(self):
		if self.GetRedDragonLairRankingShowCount() <= self.MAX_LINE_COUNT:
			return self.MAX_LINE_COUNT
		else:
			return self.GetRedDragonLairRankingShowCount()

	def OnScrollControl(self):
		nowitemcount = 0
		if self.GetRedDragonLairRankingShowCount() <= self.MAX_LINE_COUNT:
			nowitemcount = 0
		else:
			nowitemcount = (self.GetRedDragonLairRankingShowCount() - self.MAX_LINE_COUNT)

		if not app.ENABLE_GUILD_DRAGONLAIR_PARTY_SYSTEM:
			pos = self.ScrollBar.GetPos() * nowitemcount

		if not int(pos) == self.NowStartLineNumber:
			self.NowStartLineNumber = int(pos)
			self.RefreshGuildDragonLairRanking(self.DragonLairType)

	def OnPressEscapeKey(self):
		self.Close()
		return True

	''' 2019.12.19.OSP '''

	def ClearDragonLairRanking(self, type = 0):
		self.RedDragonLairRanking = []
		self.BlueDragonLairRanking = []
		self.GreenDragonLairRanking = []

	def AddDragonLairRanking(self, type, guildname, membercount, min, sec):
		if type == GUILD_DRAGONLAIR_TYPE_RED:
			self.RedDragonLairRanking.append([guildname, membercount, min, sec])
		elif type == GUILD_DRAGONLAIR_TYPE_BLUE:
			pass
		elif type == GUILD_DRAGONLAIR_TYPE_GREEN:
			pass

	def GetRedDragonLairRankingShowCount(self):
		if not self.RedDragonLairRanking:
			return 0

		return len(self.RedDragonLairRanking)

	def GetRedDragonLairRanking(self, nowindex):
		if not self.RedDragonLairRanking:
			return ("", 0, 0, 0)

		guildname = self.RedDragonLairRanking[nowindex][0]
		membercount = self.RedDragonLairRanking[nowindex][1]
		min = self.RedDragonLairRanking[nowindex][2]
		sec = self.RedDragonLairRanking[nowindex][3]

		return guildname, membercount, min, sec

	def GetMyRedDragonLairRanking(self, type):
		if not self.RedDragonLairRanking:
			return (0, 0, 0, 0)

		if guild.IsGuildEnable():
			for i in xrange(len(self.RedDragonLairRanking)):
				if self.RedDragonLairRanking[i][0] == guild.GetGuildName():
					ranking = i + 1
					membercount = self.RedDragonLairRanking[i][1]
					min = self.RedDragonLairRanking[i][2]
					sec = self.RedDragonLairRanking[i][3]
					return (ranking, membercount, min, sec)

			return (0, 0, 0, 0)