# coding: utf-8

import app
import chat
import dungeonInfo
import item
import player
import net
import grp
import wndMgr

import constinfo
import localeinfo
import uiscriptlocale

import ui
import uicommon
import uitooltip

if app.ENABLE_INGAME_WIKI:
	import net
	import ingamewikiui

import math
from operator import truediv
from _weakref import proxy

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

dungeonsLoaded = False
dungeonsDict = {}

statusBaseLimits = {}
statusRefund = [-1, 0]
statusResetStamp = [0]

rankPosDict = {}

def OnRankPos(num, pos):
	rankPosDict[num] = pos

def _FormatRunTime(value):
	value = int(value)
	if value >= 2147483647:
		return "-"
	mins = value / 60
	secs = value % 60
	if mins >= 60:
		return "%d:%02d:%02d" % (mins / 60, mins % 60, secs)
	return "%d:%02d" % (mins, secs)

def OnStatBase(first, pairs):
	if int(first):
		statusBaseLimits.clear()
	for pair in pairs.split("|"):
		if ":" in pair:
			mapIdx, baseLimit = pair.split(":", 1)
			statusBaseLimits[int(mapIdx)] = int(baseLimit)

def OnStatRefund(left, maxCount):
	statusRefund[0] = int(left)
	statusRefund[1] = int(maxCount)

def OnStatReset(secs):
	statusResetStamp[0] = app.GetGlobalTimeStamp() + int(secs)

def FormatEffectiveLimit(mapIndex, limit):
	base = statusBaseLimits.get(mapIndex, 0)
	if base > 0 and limit > base:
		return "{} (+{})".format(base, limit - base)
	return str(limit)

class DungeonLimitToolTip(ui.ThinBoard):
	WIDTH = 380
	PAD = 12
	HEAD_H = 18
	ROW_H = 18
	LINE_H = 17

	C_LINE = 0xff756657
	C_HEAD_BG = 0xff281f1a
	C_ROW_BG = 0xff1a1615
	C_HEAD_TXT = 0xffcabdab
	C_CELL_TXT = 0xffc7c7c7
	C_TITLE = 0xfff2e6c1
	C_ACTIVE = 0xff5ade5a
	C_UPCOMING = 0xffefa37f
	C_CANACT = 0xfff2e6c1
	C_USED = 0xffc86464

	def __init__(self):
		ui.ThinBoard.__init__(self, "TOP_MOST", 2)
		self.AddFlag("not_pick")
		self.AddFlag("float")
		self.children = []
		self.resetLine = None
		self.Hide()

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def Clear(self):
		for child in self.children:
			child.Hide()
		self.children = []
		self.resetLine = None

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
		return line

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
			elif kind == "reset":
				self.resetLine = self.__AppendText(block[1], y, block[2])
				y += self.LINE_H
			elif kind == "space":
				y += block[1]
			elif kind == "table":
				h = self.__AppendTable(block[1], block[2], block[3], block[4], y)
				y += h + 4
		self.SetSize(self.WIDTH, y + self.PAD)

def LoadDungeons():
	global dungeonsLoaded
	global dungeonsDict

	dungeonsLoaded = True

	try:
		file = open("dungeon_info.json", "rb")
		data = file.read()
		file.close()

		tmpList = eval(data)
		for dungeon in tmpList:
			index = dungeon["index"]

			del dungeon["index"]
			del dungeon["entryMapIndex"]
			del dungeon["entryBaseX"]
			del dungeon["entryBaseY"]
			del dungeon["questName"]
			del dungeon["isFormat"]

			dungeonsDict[index] = dungeon
	except:
		pass

#app.ENABLE_CONQUEROR_LEVEL
def RetJoin(dungeonKey, currTime, charLevel, charConquerorLevel, charCooldown, hwidCooldown1, hwidCooldown2, numCount, numLimit):
	global dungeonsDict
	if not dungeonsDict.has_key(dungeonKey):
		return -1

	if app.ENABLE_CONQUEROR_LEVEL:
		if dungeonsDict[dungeonKey]["levelConquerorMin"] > charConquerorLevel:
			return 2
		elif dungeonsDict[dungeonKey]["levelConquerorMax"] < charConquerorLevel:
			return 3

	if dungeonsDict[dungeonKey]["levelMin"] > charLevel:
		return 2
	elif dungeonsDict[dungeonKey]["levelMax"] < charLevel:
		return 3
	elif currTime < charCooldown:
		return 4
	elif currTime < hwidCooldown1 and currTime < hwidCooldown2:
		return 5
	elif app.USE_DUNGEON_COUNT_LIMIT_DAILY and numLimit <= numCount:
		return 6

	return 1

class DungeonInfoWindow(ui.ScriptWindow):
	IMG_PATH = "d:/ymir work/ui/game/dungeoninfo/"
	IMG_REWORK = "d:/ymir work/ui/dungeoninfo_rework/"

	DIFFUSE_COLOR_SELECTED = (253.0 / 255.0, 203.0 / 255.0, 110.0 / 255.0, 1.0)#rgba(253, 203, 110,1.0)
	#DIFFUSE_COLOR_UNSELECTED = (200.0 / 255.0, 138.0 / 255.0, 109.0 / 255.0, 1.0)
	DIFFUSE_COLOR_UNSELECTED = (130.0 / 255.0, 88.0 / 255.0, 159.0 / 255.0, 1.0)
	DIFFUSE_COLOR_OVER = (214.0 / 255.0, 162.0 / 255.0, 232.0 / 255.0, 1.0)#rgba(214, 162, 232,1.0)
	DIFFUSE_COLOR_BAR = (200.0 / 255.0, 138.0 / 255.0, 109.0 / 255.0, 0.8)
	DIFFUSE_COLOR_COOLDOWN = (1.0, 0.0, 0.0, 1.0)
	SCROLL_SPEED = 28

	if app.ENABLE_INGAME_WIKI:
		class TopWindow(ui.ScriptWindow):
			topNamesPath = "d:/ymir work/ui/game/guild/dragonlairranking/"
			topNamesDict = {\
								dungeonInfo.TOP_DMG : uiscriptlocale.DUNGEON_INFO_RANK0_TITLE,
								dungeonInfo.TOP_TIME : uiscriptlocale.DUNGEON_INFO_RANK1_TITLE,
								dungeonInfo.TOP_COUNT : uiscriptlocale.DUNGEON_INFO_RANK2_TITLE
			}

			SCROLL_SPEED = 8

			def Open(self):
				topNum = dungeonInfo.GetRankNum()
				if topNum >= dungeonInfo.TOP_MAX:
					return

				self.titleName.SetText(self.topNamesDict[topNum] if self.topNamesDict.has_key(topNum) else "")

				if len(self.topSlotsDict) == 0:
					for i in xrange(dungeonInfo.MAX_LIST_TOP):
						tmp = ui.ExpandedImageBox()
						tmp.SetParent(self.scrollWnd)
						tmp.LoadImage(self.topNamesPath + "ranking_list_button01.sub")

						self.h = tmp.GetHeight() + 2

						tmp.SetPosition(0, i * self.h)
						tmp.Show()
						self.topSlotsDict[i] = tmp

						self.topBGElementsDict[i] = []
						self.topTXTElementsDict[i] = []
						yE = 5

						for j in xrange(4):
							tmpBG = ui.ExpandedImageBox()
							tmpBG.SetParent(self.topSlotsDict[i])

							if j == 0:
								tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/32x16.png")
							elif j == 1:
								tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/112x16.png")
							elif j == 2:
								tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/24x16.png")
							elif j == 3:
								tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/64x16.png")

							tmpBG.SetPosition(yE, 2)
							tmpBG.Show()

							if j == 0:
								yE += tmpBG.GetWidth() + 20
							elif j == 1:
								yE += tmpBG.GetWidth() + 22
							elif j == 2:
								yE += tmpBG.GetWidth() + 22

							tmpTXT = ui.TextLine()
							tmpTXT.SetParent(tmpBG)
							tmpTXT.SetText("-")
							tmpTXT.Show()
							tmpTXT.SetHorizontalAlignCenter()
							tmpTXT.SetWindowHorizontalAlignCenter()
							tmpTXT.SetPosition(0, 1)

							self.topBGElementsDict[i].append(tmpBG)
							self.topTXTElementsDict[i].append(tmpTXT)

					tmp = ui.ExpandedImageBox()
					tmp.SetParent(self.content2)
					tmp.LoadImage(self.topNamesPath + "ranking_list_button02.sub")
					tmp.SetPosition(8, 6)
					tmp.Show()
					self.topSlotsDict[dungeonInfo.MAX_LIST_TOP] = tmp

					self.topBGElementsDict[dungeonInfo.MAX_LIST_TOP] = []
					self.topTXTElementsDict[dungeonInfo.MAX_LIST_TOP] = []
					yE = 5

					for j in xrange(4):
						tmpBG = ui.ExpandedImageBox()
						tmpBG.SetParent(self.topSlotsDict[dungeonInfo.MAX_LIST_TOP])

						if j == 0:
							tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/32x16.png")
						elif j == 1:
							tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/112x16.png")
						elif j == 2:
							tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/24x16.png")
						elif j == 3:
							tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/64x16.png")

						tmpBG.SetPosition(yE, 2)
						tmpBG.Show()

						if j == 0:
							yE += tmpBG.GetWidth() + 20
						elif j == 1:
							yE += tmpBG.GetWidth() + 22
						elif j == 2:
							yE += tmpBG.GetWidth() + 22

						tmpTXT = ui.TextLine()
						tmpTXT.SetParent(tmpBG)
						tmpTXT.SetText("-")
						tmpTXT.Show()
						tmpTXT.SetHorizontalAlignCenter()
						tmpTXT.SetWindowHorizontalAlignCenter()
						tmpTXT.SetPosition(0, 1)

						self.topBGElementsDict[dungeonInfo.MAX_LIST_TOP].append(tmpBG)
						self.topTXTElementsDict[dungeonInfo.MAX_LIST_TOP].append(tmpTXT)

					self.topBGElementsDict[dungeonInfo.MAX_LIST_TOP + 1] = []
					self.topTXTElementsDict[dungeonInfo.MAX_LIST_TOP + 1] = []
					yE = 7
					for j in xrange(4):
						tmpBG = ui.ExpandedImageBox()
						tmpBG.SetParent(self.subtitle)

						if j == 0:
							tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/32x16.png")
						elif j == 1:
							tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/112x16.png")
						elif j == 2:
							tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/24x16.png")
						elif j == 3:
							tmpBG.LoadImage(DungeonInfoWindow.IMG_PATH + "rank/64x16.png")

						tmpBG.SetPosition(yE, 2)
						tmpBG.Show()

						if j == 0:
							yE += tmpBG.GetWidth() + 20
						elif j == 1:
							yE += tmpBG.GetWidth() + 22
						elif j == 2:
							yE += tmpBG.GetWidth() + 22

						tmpTXT = ui.TextLine()
						tmpTXT.SetParent(tmpBG)
						tmpTXT.SetText("-")
						tmpTXT.Show()
						tmpTXT.SetHorizontalAlignCenter()
						tmpTXT.SetWindowHorizontalAlignCenter()
						tmpTXT.SetPackedFontColor(0xFFFEE3AE)
						tmpTXT.SetPosition(0, 1)

						self.topBGElementsDict[dungeonInfo.MAX_LIST_TOP + 1].append(tmpBG)
						self.topTXTElementsDict[dungeonInfo.MAX_LIST_TOP + 1].append(tmpTXT)

				c = 0
				self.scrollWnd.SetSize(self.scrollWnd.GetWidth(), 0)

				for i in xrange(dungeonInfo.MAX_LIST_TOP + 2):
					if i == (dungeonInfo.MAX_LIST_TOP + 1):
						self.topTXTElementsDict[i][0].SetText(localeinfo.DUNGEON_INFO_SUBTITLE_1)
						self.topTXTElementsDict[i][1].SetText(localeinfo.DUNGEON_INFO_SUBTITLE_2)
						self.topTXTElementsDict[i][2].SetText(localeinfo.DUNGEON_INFO_SUBTITLE_3)

						if topNum == dungeonInfo.TOP_DMG:
							self.topTXTElementsDict[i][3].SetText(localeinfo.DUNGEON_INFO_SUBTITLE_4A)
						elif topNum == dungeonInfo.TOP_TIME:
							self.topTXTElementsDict[i][3].SetText(localeinfo.DUNGEON_INFO_SUBTITLE_4B)
						elif topNum == dungeonInfo.TOP_COUNT:
							self.topTXTElementsDict[i][3].SetText(localeinfo.DUNGEON_INFO_SUBTITLE_4C)
						else:
							self.topTXTElementsDict[i][3].SetText("-")
					else:
						(num, name, level, value) = dungeonInfo.GetRankData(topNum, i)
						if name == "":
							self.topSlotsDict[i].Hide()
						else:
							if i == dungeonInfo.MAX_LIST_TOP:
								ownPos = rankPosDict.get(topNum, 0)
								self.topTXTElementsDict[i][0].SetText("#%d" % ownPos if ownPos > 0 else "-")
							else:
								self.topTXTElementsDict[i][0].SetText(str(num))
							self.topTXTElementsDict[i][1].SetText(name)
							self.topTXTElementsDict[i][2].SetText(str(level))
							self.topTXTElementsDict[i][3].SetText(_FormatRunTime(value) if topNum == dungeonInfo.TOP_TIME else str(value))

							self.topSlotsDict[i].Show()

							if i != dungeonInfo.MAX_LIST_TOP:
								c += 1

				self.scrollWnd.SetSize(self.scrollWnd.GetWidth(), c * self.h)
				self.UpdateScrollBar()

				self.SetCenterPosition()
				self.SetTop()
				self.Show()

			def Close(self):
				self.Hide()

			def OnPressEscapeKey(self):
				self.Close()
				return True

			def OnScrollBar(self, fScale):
				curr = min(0, max(math.ceil((self.scrollWnd.GetHeight() - self.peekWnd.GetHeight()) * fScale * -1.0), -self.scrollWnd.GetHeight() + self.peekWnd.GetHeight()))
				self.scrollWnd.SetPosition(0, curr)

			def ChangeScrollBar(self):
				if self.scrollWnd.GetHeight() <= self.peekWnd.GetHeight():
					self.scrollBar.Hide()
				else:
					self.scrollBar.SetScale(self.peekWnd.GetHeight(), self.scrollWnd.GetHeight())
					self.scrollBar.SetPosScale(truediv(abs(self.scrollWnd.GetLocalPosition()[1]), (self.scrollWnd.GetHeight() - self.peekWnd.GetHeight())))
					self.scrollBar.Show()

			def UpdateScrollBar(self, val = 0):
				curr = min(0, max(self.scrollWnd.GetLocalPosition()[1] + val, -self.scrollWnd.GetHeight() + self.peekWnd.GetHeight()))
				self.scrollWnd.SetPosition(0, curr)

				self.ChangeScrollBar()

			def OnRunMouseWheel(self, iLen):
				if self.peekWnd.IsInPosition():
					self.UpdateScrollBar(int((iLen * 0.01) * self.SCROLL_SPEED))
					return True

				return False

			def Initialize(self):
				try:
					self.h = 0

					PythonScriptLoader = ui.PythonScriptLoader()
					PythonScriptLoader.LoadScriptFile(self, "uiscript/dungeoninfo_ranking.py")

					self.board = self.GetChild("board_ui")
					self.content1 = self.GetChild("content1_ui")
					self.content2 = self.GetChild("content2_ui")
					self.subtitle = self.GetChild("subtitle_ui")

					self.peekWnd = self.GetChild("subcontent_ui")
					# self.peekWnd.SetInsideRender(True)

					tmp = ui.Window()
					tmp.SetParent(self.peekWnd)
					tmp.AddFlag("attach")
					tmp.AddFlag("not_pick")
					tmp.SetSize(self.GetWidth(), 0)
					tmp.SetPosition(0, 0)
					tmp.Show()
					self.scrollWnd = tmp

					if app.USE_CLIP_MASK:
						self.scrollWnd.SetClippingMaskWindow(self.peekWnd)

					tmp = DungeonInfoWindow.ScrollBar()
					tmp.SetParent(self.board)

					(x1, y1) = self.content1.GetLocalPosition()
					(x2, y2) = self.peekWnd.GetLocalPosition()

					tmp.SetPosition(x1 + x2 + self.peekWnd.GetWidth() + 6, y1 + y2)
					tmp.SetSize(6, self.peekWnd.GetHeight())
					tmp.SetScrollEvent(self.OnScrollBar)
					tmp.SetScrollSpeed(self.SCROLL_SPEED)
					self.scrollBar = tmp

					self.topSlotsDict = {}
					self.topBGElementsDict = {}
					self.topTXTElementsDict = {}

					self.titleName = self.GetChild("titlename_ui")
					self.titleBar = self.GetChild("titlebar_ui")
					self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))
				except Exception as msg:
					import dbg
					dbg.TraceError(str(msg))
					app.Abort()

			def __init__(self):
				ui.ScriptWindow.__init__(self)
				self.Initialize()

			def Destroy(self):
				self.h = 0

				for v in self.topTXTElementsDict.values():
					for e in v:
						del e

				for v in self.topBGElementsDict.values():
					for e in v:
						del e

				for v in self.topSlotsDict.values():
					del v

				self.topSlotsDict = {}

				if self.scrollBar:
					self.scrollBar.ResetScrollEvent()
					del self.scrollBar
					self.scrollBar = None

				if self.scrollWnd:
					del self.scrollWnd
					self.scrollWnd = None

				self.titleName = None

				if self.titleBar:
					self.titleBar.SetCloseEvent(None)
					self.titleBar = None

				self.peekWnd = None
				self.content1 = None
				self.content2 = None
				self.subtitle = None
				self.board = None

				self.ClearDictionary()

			def __del__(self):
				ui.ScriptWindow.__del__(self)

	if app.USE_DUNGEON_INFO_ADDON_LEVEL_CAP:
		class CapLevelDialog(ui.ScriptWindow):
			if app.ENABLE_INGAME_WIKI:
				SCROLL_SPEED = 7.5

			if app.ENABLE_INGAME_WIKI:
				def OnScrollBar(self, fScale):
					curr = min(0, max(math.ceil((self.scrollWnd.GetHeight() - self.peekWnd.GetHeight()) * fScale * -1.0), -self.scrollWnd.GetHeight() + self.peekWnd.GetHeight()))
					self.scrollWnd.SetPosition(0, curr)

				def ChangeScrollBar(self):
					if self.scrollWnd.GetHeight() <= self.peekWnd.GetHeight():
						self.scrollBar.Hide()
					else:
						self.scrollBar.SetScale(self.peekWnd.GetHeight(), self.scrollWnd.GetHeight())
						self.scrollBar.SetPosScale(truediv(abs(self.scrollWnd.GetLocalPosition()[1]), (self.scrollWnd.GetHeight() - self.peekWnd.GetHeight())))
						self.scrollBar.Show()

				def UpdateScrollBar(self, val = 0):
					curr = min(0, max(self.scrollWnd.GetLocalPosition()[1] + val, -self.scrollWnd.GetHeight() + self.peekWnd.GetHeight()))
					self.scrollWnd.SetPosition(0, curr)

					self.ChangeScrollBar()

				def OnRunMouseWheel(self, iLen):
					if self.peekWnd.IsInPosition():
						self.UpdateScrollBar(int((iLen * 0.01) * self.SCROLL_SPEED))
						return True

					return False

			def Open(self, level, shown):
				if self.level != level:
					self.level = level
					self.levelMsg.SetText(localeinfo.DUNGEON_INFO_ADDON_LEVEL_CAP_MSG3 % (self.level + 1))

					for i in self.itemsList:
						del i

					self.itemsList = []

					self.scrollWnd.SetSize(self.peekWnd.GetWidth(), 0)

					y = 16
					j = 0

					global dungeonsDict
					for k, v in dungeonsDict.items():
						if (dungeonsDict[k]["levelMax"] - self.level) == 0:
							tmp = ui.TextLine()
							tmp.SetParent(self.scrollWnd)
							tmp.SetText(localeinfo.GetMiniMapZoneNameByIdx(dungeonsDict[k]["mapIndex"]))
							tmp.Show()
							tmp.SetHorizontalAlignCenter()
							tmp.SetWindowHorizontalAlignCenter()
							tmp.SetPosition(0, j * 16)
							self.itemsList.append(tmp)
							j += 1

					self.scrollWnd.SetSize(self.peekWnd.GetWidth(), j * 15)

				self.UpdateScrollBar()

				if shown:
					self.SetCenterPosition()
					self.SetTop()
					self.Show()

				return True

			def Close(self):
				self.Hide()

			def OnPressEscapeKey(self):
				self.Close()
				return True

			def OnToggle(self):
				if self.IsShow():
					self.Close()
				else:
					self.Open(self.level, True)

			def Accept(self):
				net.SendChatPacket("/accept_levelup")
				self.Close()

			def Initialize(self):
				try:
					PythonScriptLoader = ui.PythonScriptLoader()
					PythonScriptLoader.LoadScriptFile(self, "uiscript/dungeoninfo_caplevel_dialog.py")

					self.board = self.GetChild("ui_board")
					self.subBoard = self.GetChild("ui_subboard")
					self.levelMsg = self.GetChild("ui_text3")

					self.titleBar = self.GetChild("ui_titlebar")
					self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))

					self.buttonAccept = self.GetChild("ui_accept_button")
					self.buttonAccept.SetEvent(ui.__mem_func__(self.Accept))

					self.buttonClose = self.GetChild("ui_close_button")
					self.buttonClose.SetEvent(ui.__mem_func__(self.Close))
				except Exception as msg:
					import dbg
					dbg.TraceError(str(msg))
					app.Abort()

				self.level = 0

				self.peekWnd = None
				self.scrollWnd = None
				self.scrollBar = None

				self.itemsList = []

				if app.ENABLE_INGAME_WIKI:
					tmp = ui.Window()
					# tmp.SetInsideRender(True)
					tmp.SetParent(self.subBoard)
					tmp.AddFlag("attach")
					tmp.AddFlag("not_pick")
					tmp.SetSize(self.subBoard.GetWidth(), self.subBoard.GetHeight() - 6)
					tmp.SetPosition(0, 2)
					tmp.Show()
					self.peekWnd = tmp

					tmp = ui.Window()
					tmp.SetParent(self.peekWnd)
					tmp.AddFlag("attach")
					tmp.AddFlag("not_pick")
					tmp.SetSize(0, 0)
					tmp.SetPosition(0, 0)
					tmp.Show()
					self.scrollWnd = tmp

					if app.USE_CLIP_MASK:
						self.scrollWnd.SetClippingMaskWindow(self.peekWnd)

					tmp = DungeonInfoWindow.ScrollBar()
					tmp.SetParent(self.subBoard)
					tmp.SetPosition(self.peekWnd.GetWidth() - 10, self.peekWnd.GetLocalPosition()[1] + 2)
					tmp.SetSize(6, self.peekWnd.GetHeight())
					tmp.SetScrollEvent(self.OnScrollBar)
					tmp.SetScrollSpeed(self.SCROLL_SPEED)
					self.scrollBar = tmp

			def __init__(self):
				ui.ScriptWindow.__init__(self)
				self.Initialize()

			def Destroy(self):
				for i in self.itemsList:
					del i

				self.itemsList = []

				if self.peekWnd:
					del self.peekWnd
					self.peekWnd = None

				if self.scrollWnd:
					del self.scrollWnd
					self.scrollWnd = None

				if self.scrollBar:
					self.scrollBar.ResetScrollEvent()
					del self.scrollBar
					self.scrollBar = None

				self.board = None
				self.subBoard = None
				self.levelMsg = None

				self.titleBar.SetCloseEvent(None)
				self.titleBar = None

				self.buttonAccept.SetEvent(None)
				self.buttonAccept = None

				self.buttonClose.SetEvent(None)
				self.buttonClose = None

				self.ClearDictionary()

			def __del__(self):
				ui.ScriptWindow.__del__(self)

		def CapLevel(self, level, shown):
			if not self.capLevelDlg:
				self.capLevelDlg = DungeonInfoWindow.CapLevelDialog()

			return self.capLevelDlg.Open(level, shown)

		def CapLevelEnd(self):
			if self.capLevelDlg:
				self.capLevelDlg.Destroy()
				del self.capLevelDlg
				self.capLevelDlg = None

			return True

		def OnToggleCapLevel(self):
			if self.capLevelDlg:
				self.capLevelDlg.OnToggle()

		def IsCapLevel(self):
			if self.capLevelDlg:
				return True

			return False

	class ScrollBar(ui.Window):
		BASE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
		CORNERS_AND_LINES_COLOR = grp.GenerateColor(0.3411, 0.3411, 0.3411, 1.0)
		BAR_NUMB = 9

		class MiddleBar(ui.DragButton):
			MIDDLE_BAR_COLOR = grp.GenerateColor(0.6470, 0.6470, 0.6470, 1.0)

			def __init__(self):
				ui.DragButton.__init__(self)
				self.AddFlag("movable")

				self.middle = ui.Bar()
				self.middle.SetParent(self)
				self.middle.AddFlag("attach")
				self.middle.AddFlag("not_pick")
				self.middle.SetColor(self.MIDDLE_BAR_COLOR)
				self.middle.SetSize(1, 1)
				self.middle.Show()

			def __del__(self):
				ui.DragButton.__del__(self)

			def SetStaticScale(self, size):
				(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
				ui.DragButton.SetSize(self, base_width, size)
				self.middle.SetSize(base_width, size)

			def SetSize(self, selfSize, fullSize):
				(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
				ui.DragButton.SetSize(self, base_width, truediv(int(selfSize), int(fullSize)) * selfSize)
				self.middle.SetSize(base_width, truediv(int(selfSize), int(fullSize)) * selfSize)

			def SetStaticSize(self, size):
				size = max(2, size)
				ui.DragButton.SetSize(self, size, self.middle.GetHeight())
				self.middle.SetSize(size, self.middle.GetHeight())

		def __init__(self):
			ui.Window.__init__(self)

			self.scrollEvent = None
			self.scrollSpeed = 1
			self.sizeScale = 1.0

			self.bars = []
			for i in xrange(self.BAR_NUMB):
				br = ui.Bar()
				br.SetParent(self)
				br.AddFlag("attach")
				br.AddFlag("not_pick")
				br.SetColor([self.CORNERS_AND_LINES_COLOR, self.BASE_COLOR][i == (self.BAR_NUMB - 1)])
				if not (i % 2 == 0): br.SetSize(1, 1)
				br.Show()

				self.bars.append(br)

			self.middleBar = self.MiddleBar()
			self.middleBar.SetParent(self)
			self.middleBar.SetMoveEvent(ui.__mem_func__(self.OnScrollMove))
			self.middleBar.Show()

		def __del__(self):
			ui.Window.__del__(self)

		def Destroy(self):
			for e in self.bars:
				del e

			self.bars = []

			if self.middleBar:
				del self.middleBar
				self.middleBar = None

		def OnScrollMove(self):
			if not self.scrollEvent:
				return

			arg = float(self.middleBar.GetLocalPosition()[1] - 1) / float(self.GetHeight() - 2 - self.middleBar.GetHeight())
			self.scrollEvent(arg)

		def ResetScrollEvent(self):
			self.scrollEvent = None

		def SetScrollEvent(self, func):
			self.scrollEvent = ui.__mem_func__(func)

		def SetScrollSpeed(self, speed):
			self.scrollSpeed = speed

		def OnRunMouseWheel(self, length):
			if self.IsInPosition():
				val = min(max(1, self.middleBar.GetLocalPosition()[1] - (length * 0.01) * self.scrollSpeed * self.sizeScale), self.GetHeight() - self.middleBar.GetHeight() - 1)
				self.middleBar.SetPosition(1, val)

				self.OnScrollMove()
				return True

			return False

		def OnMouseLeftButtonDown(self):
			(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
			if xMouseLocalPosition == 0 or xMouseLocalPosition == self.GetWidth():
				return

			y_pos = (yMouseLocalPosition - self.middleBar.GetHeight() / 2)
			self.middleBar.SetPosition(1, y_pos)

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

			self.middleBar.SetStaticSize(width - 2)
			self.middleBar.SetSize(12, self.GetHeight())

			self.middleBar.SetRestrictMovementArea(1, 1, width - 2, height - 2)

		def SetScale(self, selfSize, fullSize):
			self.sizeScale = float(selfSize/fullSize)
			self.middleBar.SetSize(selfSize, fullSize)

		def SetStaticScale(self, r_size):
			self.middleBar.SetStaticScale(r_size)

		def SetPosScale(self, fScale):
			pos = (math.ceil((self.GetHeight() - 2 - self.middleBar.GetHeight()) * fScale) + 1)
			self.SetPos(pos)

		def SetPos(self, pos):
			wPos = (1, pos)
			self.middleBar.SetPosition(*wPos)

	def OnCloseTeleportDlg(self):
		if self.teleportDlg:
			self.teleportDlg.Close()

	def __RefreshSelected(self):
		for k, v in self.dungeonsMyDict.items():
			v.isSelected = (k == self.selectedIndex)
			v.RefreshSlotImage()

		if app.ENABLE_INGAME_WIKI:
			for v in self.dungeonsMyInfoDict.values():
				v.Hide()

			if self.dungeonsMyInfoDict.has_key(self.selectedIndex):
				self.dungeonsMyInfoDict[self.selectedIndex].Open()

	def ChangeSelected(self, index):
		self.OnCloseTeleportDlg()

		if self.selectedIndex == index:
			return

		self.selectedIndex = index
		self.__RefreshSelected()

	def OnDrop(self, index):
		global dungeonsDict
		if dungeonsDict.has_key(index):
			dropMonsterVnum = dungeonsDict[index]["dropMonsterVnum"] if dungeonsDict[index].has_key("dropMonsterVnum") else 0
			if dropMonsterVnum:
				if app.ENABLE_INGAME_WIKI:
					if not self.wikiInst.IsShow():
						net.ToggleWikiWindow()

					self.wikiInst.CloseBaseWindows()
					self.wikiInst.OpenSpecialPage(None, dropMonsterVnum, True)
			else:
				dropItemVnum = dungeonsDict[index]["dropItemVnum"] if dungeonsDict[index].has_key("dropItemVnum") else 0
				if dropItemVnum:
					if app.ENABLE_INGAME_WIKI:
						if not self.wikiInst.IsShow():
							net.ToggleWikiWindow()

						self.wikiInst.CloseBaseWindows()
						self.wikiInst.OpenSpecialPage(None, dropItemVnum, False)
				else:
					dropChestItemVnum = dungeonsDict[index]["dropChestItemVnum"] if dungeonsDict[index].has_key("dropChestItemVnum") else 0
					if not dropChestItemVnum:
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_TIP_NO_DROP)
						return

					if app.ENABLE_INGAME_WIKI:
						if not self.wikiInst.IsShow():
							net.ToggleWikiWindow()

						self.wikiInst.CloseBaseWindows()
						self.wikiInst.mainChestWindow.Show([dropChestItemVnum,])

	def OnOverInItem(self, itemVnum):
		if not itemVnum:
			return

		if not self.toolTipItem:
			self.toolTipItem = uitooltip.ItemToolTip()

		self.toolTipItem.ClearToolTip()
		self.toolTipItem.SetItemToolTip(itemVnum)

		hint = getattr(localeinfo, "DUNGEON_INFO_TICKET_SHOP_HINT", "")
		if not hint or hint.startswith("Locale not found"):
			hint = "Click to open the ticket shop."
		self.toolTipItem.AppendSpace(5)
		self.toolTipItem.AppendTextLineDontCheckColor(hint, 0xff8EC292)

	def OnOverOutItem(self):
		if self.toolTipItem:
			self.toolTipItem.HideToolTip()

	class ElementItemInfo(ui.Window):
		SCROLL_SPEED = 8

		KEY_INFORMATION = 1
		KEY_ELEMENT = 2
		KEY_TICKET = 3

		def OnScrollBarInformation(self, fScale):
			curr = min(0, max(math.ceil((self.scrollDict[self.KEY_INFORMATION].GetHeight() - self.peekDict[self.KEY_INFORMATION].GetHeight()) * fScale * -1.0), -self.scrollDict[self.KEY_INFORMATION].GetHeight() + self.peekDict[self.KEY_INFORMATION].GetHeight()))
			self.scrollDict[self.KEY_INFORMATION].SetPosition(0, curr)

		def ChangeScrollBarInformation(self):
			if self.scrollDict[self.KEY_INFORMATION].GetHeight() <= self.peekDict[self.KEY_INFORMATION].GetHeight():
				self.scrollBarDict[self.KEY_INFORMATION].Hide()
			else:
				self.scrollBarDict[self.KEY_INFORMATION].SetScale(self.peekDict[self.KEY_INFORMATION].GetHeight(), self.scrollDict[self.KEY_INFORMATION].GetHeight())
				self.scrollBarDict[self.KEY_INFORMATION].SetPosScale(truediv(abs(self.scrollDict[self.KEY_INFORMATION].GetLocalPosition()[1]), (self.scrollDict[self.KEY_INFORMATION].GetHeight() - self.peekDict[self.KEY_INFORMATION].GetHeight())))
				self.scrollBarDict[self.KEY_INFORMATION].Show()

		def UpdateScrollBarInformation(self, val = 0):
			curr = min(0, max(self.scrollDict[self.KEY_INFORMATION].GetLocalPosition()[1] + val, -self.scrollDict[self.KEY_INFORMATION].GetHeight() + self.peekDict[self.KEY_INFORMATION].GetHeight()))
			self.scrollDict[self.KEY_INFORMATION].SetPosition(0, curr)

			self.ChangeScrollBarInformation()

		def OnScrollBarElement(self, fScale):
			curr = min(0, max(math.ceil((self.scrollDict[self.KEY_ELEMENT].GetHeight() - self.peekDict[self.KEY_ELEMENT].GetHeight()) * fScale * -1.0), -self.scrollDict[self.KEY_ELEMENT].GetHeight() + self.peekDict[self.KEY_ELEMENT].GetHeight()))
			self.scrollDict[self.KEY_ELEMENT].SetPosition(0, curr)

		def ChangeScrollBarElement(self):
			if self.scrollDict[self.KEY_ELEMENT].GetHeight() <= self.peekDict[self.KEY_ELEMENT].GetHeight():
				self.scrollBarDict[self.KEY_ELEMENT].Hide()
			else:
				self.scrollBarDict[self.KEY_ELEMENT].SetScale(self.peekDict[self.KEY_ELEMENT].GetHeight(), self.scrollDict[self.KEY_ELEMENT].GetHeight())
				self.scrollBarDict[self.KEY_ELEMENT].SetPosScale(truediv(abs(self.scrollDict[self.KEY_ELEMENT].GetLocalPosition()[1]), (self.scrollDict[self.KEY_ELEMENT].GetHeight() - self.peekDict[self.KEY_ELEMENT].GetHeight())))
				self.scrollBarDict[self.KEY_ELEMENT].Show()

		def UpdateScrollBarElement(self, val = 0):
			curr = min(0, max(self.scrollDict[self.KEY_ELEMENT].GetLocalPosition()[1] + val, -self.scrollDict[self.KEY_ELEMENT].GetHeight() + self.peekDict[self.KEY_ELEMENT].GetHeight()))
			self.scrollDict[self.KEY_ELEMENT].SetPosition(0, curr)

			self.ChangeScrollBarElement()

		def OnScrollBarTicket(self, fScale):
			curr = min(0, max(math.ceil((self.scrollDict[self.KEY_TICKET].GetHeight() - self.peekDict[self.KEY_TICKET].GetHeight()) * fScale * -1.0), -self.scrollDict[self.KEY_TICKET].GetHeight() + self.peekDict[self.KEY_TICKET].GetHeight()))
			self.scrollDict[self.KEY_TICKET].SetPosition(0, curr)

		def ChangeScrollBarTicket(self):
			if self.scrollDict[self.KEY_TICKET].GetHeight() <= self.peekDict[self.KEY_TICKET].GetHeight():
				self.scrollBarDict[self.KEY_TICKET].Hide()
			else:
				self.scrollBarDict[self.KEY_TICKET].SetScale(self.peekDict[self.KEY_TICKET].GetHeight(), self.scrollDict[self.KEY_TICKET].GetHeight())
				self.scrollBarDict[self.KEY_TICKET].SetPosScale(truediv(abs(self.scrollDict[self.KEY_TICKET].GetLocalPosition()[1]), (self.scrollDict[self.KEY_TICKET].GetHeight() - self.peekDict[self.KEY_TICKET].GetHeight())))
				self.scrollBarDict[self.KEY_TICKET].Show()

		def UpdateScrollBarTicket(self, val = 0):
			curr = min(0, max(self.scrollDict[self.KEY_TICKET].GetLocalPosition()[1] + val, -self.scrollDict[self.KEY_TICKET].GetHeight() + self.peekDict[self.KEY_TICKET].GetHeight()))
			self.scrollDict[self.KEY_TICKET].SetPosition(0, curr)

			self.ChangeScrollBarTicket()

		def OnRunMouseWheel(self, iLen):
			for k, v in self.peekDict.items():
				if v.IsInPosition():
					if self.scrollBarDict[k] and self.scrollBarDict[k].IsShow():
						if k == self.KEY_INFORMATION:
							self.UpdateScrollBarInformation(int((iLen * 0.01) * self.SCROLL_SPEED))
						elif k == self.KEY_ELEMENT:
							self.UpdateScrollBarElement(int((iLen * 0.01) * self.SCROLL_SPEED))
						elif k == self.KEY_TICKET:
							self.UpdateScrollBarTicket(int((iLen * 0.01) * self.SCROLL_SPEED))

						return True

			return False

		def __OverIn(self):
			self.mainInst.OnOverInItem(self.itemVnum)

		def __OverOut(self):
			self.mainInst.OnOverOutItem()

		def __ClickTicket(self):
			net.SendRemoteShopPacket(2)

		def __OverInLimitHelp(self):
			self.mainInst.ShowLimitTip(self.index)

		def __OverOutLimitHelp(self):
			self.mainInst.HideLimitTip()

		def Open(self):
			if not self.isBuilded:
				self.isBuilded = True

				global dungeonsDict
				if dungeonsDict.has_key(self.index):
					LINE_HEIGHT = 20
					y = 18
					h = 8 + (LINE_HEIGHT * 4)
					j = 0

					if app.USE_DUNGEON_COUNT_LIMIT_DAILY:
						numCooldownPlayer, numCooldownHwid1, numCooldownHwid2, numCount, numLimit, numRequiredCP = dungeonInfo.GetCooldown(self.index)
						if numLimit > 0:
							h += LINE_HEIGHT

							infoMapIndex = dungeonsDict[self.index].get("mapIndex", 0)

							tmp = ui.TextLine()
							tmp.SetParent(self.scrollDict[self.KEY_INFORMATION])
							tmp.SetText(localeinfo.DUNGEON_INFO_LEFT_COUNT_FOR_TODAY.format(numCount, FormatEffectiveLimit(infoMapIndex, numLimit)))
							tmp.Show()
							tmp.SetHorizontalAlignCenter()
							tmp.SetWindowHorizontalAlignCenter()
							tmp.SetOutline()
							tmp.SetPosition(0, j * LINE_HEIGHT)
							self.dailyLimitText = tmp
							self.informationsDict[j] = tmp

							j += 1

							helpBtn = ui.Button()
							helpBtn.SetParent(self.scrollDict[self.KEY_INFORMATION])
							helpBtn.SetUpVisual("d:/ymir work/ui/game/wheel/question_mark.png")
							helpBtn.SetOverVisual("d:/ymir work/ui/game/wheel/question_mark_glow.png")
							helpBtn.SetDownVisual("d:/ymir work/ui/game/wheel/question_mark_down.png")
							if localeinfo.IsARABIC():
								helpBtn.SetPosition(4, (j - 1) * LINE_HEIGHT + 2)
							else:
								helpBtn.SetPosition(self.scrollDict[self.KEY_INFORMATION].GetWidth() - 18, (j - 1) * LINE_HEIGHT + 2)
							helpBtn.SetOverEvent(ui.__mem_func__(self.__OverInLimitHelp))
							helpBtn.SetOverOutEvent(ui.__mem_func__(self.__OverOutLimitHelp))
							helpBtn.Show()
							self.limitHelpBtn = helpBtn

					if app.ENABLE_COMBAT_POINTS:
						reqCP = dungeonsDict[self.index].get("combatPointsMin", 0)
						if reqCP > 0:
							h += LINE_HEIGHT

							tmp = ui.TextLine()
							tmp.SetParent(self.scrollDict[self.KEY_INFORMATION])
							tmp.SetText(localeinfo.DUNGEON_INFO_REQUIRED_CP.format(reqCP))
							tmp.Show()
							tmp.SetHorizontalAlignCenter()
							tmp.SetWindowHorizontalAlignCenter()
							tmp.SetOutline()
							tmp.SetPosition(0, j * LINE_HEIGHT)
							if player.GetStatus(player.GEAR_CP) >= reqCP:
								tmp.SetPackedFontColor(0xFF00FF00)
							else:
								tmp.SetPackedFontColor(0xFFFF0000)
							self.combatPointsText = tmp
							self.combatPointsReq = reqCP
							self.informationsDict[j] = tmp

							j += 1

					self.barDict[self.KEY_INFORMATION].SetPosition(0, y)
					self.barDict[self.KEY_INFORMATION].Show()

					self.bgDict[self.KEY_INFORMATION].SetPosition(0, y + 22)
					self.bgDict[self.KEY_INFORMATION].Show()

					self.scrollDict[self.KEY_INFORMATION].SetSize(self.scrollDict[self.KEY_INFORMATION].GetWidth(), h)

					tmp = ui.TextLine()
					tmp.SetParent(self.scrollDict[self.KEY_INFORMATION])

					if app.ENABLE_CONQUEROR_LEVEL:
						if dungeonsDict[self.index]["levelConquerorMin"] > 0:
							tmp.SetText(localeinfo.DUNGEON_INFO_TIP_MIN_LEVEL_CONQUEROR % (dungeonsDict[self.index]["levelConquerorMin"]))
						else:
							tmp.SetText(localeinfo.DUNGEON_INFO_TIP_MIN_LEVEL2 % (dungeonsDict[self.index]["levelMin"]))
					else:
						tmp.SetText(localeinfo.DUNGEON_INFO_TIP_MIN_LEVEL % (dungeonsDict[self.index]["levelMin"]))

					tmp.Show()
					tmp.SetHorizontalAlignCenter()
					tmp.SetWindowHorizontalAlignCenter()
					tmp.SetPosition(0, j * LINE_HEIGHT)
					self.informationsDict[j] = tmp

					j += 1

					tmp = ui.TextLine()
					tmp.SetParent(self.scrollDict[self.KEY_INFORMATION])

					if app.ENABLE_CONQUEROR_LEVEL:
						if dungeonsDict[self.index]["levelConquerorMin"] > 0:
							tmp.SetText(localeinfo.DUNGEON_INFO_TIP_MAX_LEVEL_CONQUEROR % (dungeonsDict[self.index]["levelConquerorMax"]))
						else:
							tmp.SetText(localeinfo.DUNGEON_INFO_TIP_MAX_LEVEL2 % (dungeonsDict[self.index]["levelMax"]))
					else:
						tmp.SetText(localeinfo.DUNGEON_INFO_TIP_MAX_LEVEL % (dungeonsDict[self.index]["levelMax"]))

					tmp.Show()
					tmp.SetHorizontalAlignCenter()
					tmp.SetWindowHorizontalAlignCenter()
					tmp.SetPosition(0, j * LINE_HEIGHT)
					self.informationsDict[j] = tmp

					j += 1

					tmp = ui.TextLine()
					tmp.SetParent(self.scrollDict[self.KEY_INFORMATION])
					tmp.SetText(localeinfo.DUNGEON_INFO_TIP_LIMIT_TIME % (localeinfo.SecondToDHMS(dungeonsDict[self.index]["timeLimit"])))
					tmp.Show()
					tmp.SetHorizontalAlignCenter()
					tmp.SetWindowHorizontalAlignCenter()
					tmp.SetPosition(0, 8 + (j * LINE_HEIGHT))
					self.informationsDict[j] = tmp

					j += 1

					tmp = ui.TextLine()
					tmp.SetParent(self.scrollDict[self.KEY_INFORMATION])
					tmp.SetText(localeinfo.DUNGEON_INFO_TIP_COOLDOWN_TIME % (localeinfo.SecondToDHMS(dungeonsDict[self.index]["timeCooldown"])))
					tmp.Show()
					tmp.SetHorizontalAlignCenter()
					tmp.SetWindowHorizontalAlignCenter()
					tmp.SetPosition(0, 8 + (j * LINE_HEIGHT))
					self.informationsDict[j] = tmp

					j += 1

					n = 0
					c = len(dungeonsDict[self.index]["applyAttack"])
					yyy = h

					if c > 0:
						n = 1
						yyy += 8

						self.scrollDict[self.KEY_INFORMATION].SetSize(self.scrollDict[self.KEY_INFORMATION].GetWidth(), (self.scrollDict[self.KEY_INFORMATION].GetHeight() + (16 * (c + 1))) + 8)

						tmp = ui.TextLine()
						tmp.SetParent(self.scrollDict[self.KEY_INFORMATION])
						tmp.SetText(localeinfo.DUNGEON_INFO_ATTACK)
						tmp.Show()
						tmp.SetHorizontalAlignCenter()
						tmp.SetWindowHorizontalAlignCenter()
						tmp.SetPosition(0, yyy)

						self.informationsDict[j] = tmp

						j += 1

						for e in dungeonsDict[self.index]["applyAttack"]:
							yyy += 16

							tmp = ui.TextLine()
							tmp.SetParent(self.scrollDict[self.KEY_INFORMATION])
							tmp.SetText(uitooltip.GET_AFFECT_STRING(e, 1))
							tmp.Show()
							tmp.SetHorizontalAlignCenter()
							tmp.SetWindowHorizontalAlignCenter()
							tmp.SetPosition(0, yyy)
							self.informationsDict[j] = tmp

							j += 1

					c = len(dungeonsDict[self.index]["applyDefense"])
					if c > 0:
						yyy += (16 + 8) if n == 1 else 8

						self.scrollDict[self.KEY_INFORMATION].SetSize(self.scrollDict[self.KEY_INFORMATION].GetWidth(), (self.scrollDict[self.KEY_INFORMATION].GetHeight() + (16 * (c + 1))) + 8)

						tmp = ui.TextLine()
						tmp.SetParent(self.scrollDict[self.KEY_INFORMATION])
						tmp.SetText(localeinfo.DUNGEON_INFO_DEFENSE)
						tmp.Show()
						tmp.SetHorizontalAlignCenter()
						tmp.SetWindowHorizontalAlignCenter()
						tmp.SetPosition(0, yyy)

						self.informationsDict[j] = tmp

						j += 1

						for e in dungeonsDict[self.index]["applyDefense"]:
							yyy += 16

							tmp = ui.TextLine()
							tmp.SetParent(self.scrollDict[self.KEY_INFORMATION])
							tmp.SetText(uitooltip.GET_AFFECT_STRING(e, 1))
							tmp.Show()
							tmp.SetHorizontalAlignCenter()
							tmp.SetWindowHorizontalAlignCenter()
							tmp.SetPosition(0, yyy)
							self.informationsDict[j] = tmp

							j += 1

					y += self.bgDict[self.KEY_INFORMATION].GetHeight() + 30

					c = len(dungeonsDict[self.index]["applyElement"])
					if c == 0:
						self.barDict[self.KEY_ELEMENT].Hide()
						self.bgDict[self.KEY_ELEMENT].Hide()
					else:
						self.barDict[self.KEY_ELEMENT].SetPosition(0, y)
						self.barDict[self.KEY_ELEMENT].Show()

						self.bgDict[self.KEY_ELEMENT].SetPosition(0, y + 22)
						self.bgDict[self.KEY_ELEMENT].Show()

						j = 0
						yy = 0
						for e in dungeonsDict[self.index]["applyElement"]:
							tmp = ui.ExpandedImageBox()
							tmp.SetParent(self.scrollDict[self.KEY_ELEMENT])
							tmp.LoadImage(DungeonInfoWindow.IMG_PATH + "elements/" + str(e) + ".png")
							tmp.Show()
							tmp.SetPosition(0, yy)
							tmp.SetWindowHorizontalAlignCenter()
							self.elementsDict[j] = tmp

							yy += self.elementsDict[j].GetHeight()
							self.scrollDict[self.KEY_ELEMENT].SetSize(self.scrollDict[self.KEY_ELEMENT].GetWidth(), self.scrollDict[self.KEY_ELEMENT].GetHeight() + (self.elementsDict[j].GetHeight()))

							j += 1

						y += self.bgDict[self.KEY_ELEMENT].GetHeight() + 30

					ticketVnum = dungeonsDict[self.index]["ticketVnum"]
					ticketCount = dungeonsDict[self.index]["ticketCount"]
					if ticketVnum > 0 and ticketCount > 0:
						self.itemVnum = ticketVnum

						item.SelectItem(ticketVnum)
						ticketName = item.GetItemName()
						ticketIcon = item.GetIconImageFileName()

						self.barDict[self.KEY_TICKET].SetPosition(0, y)
						self.barDict[self.KEY_TICKET].Show()

						self.bgDict[self.KEY_TICKET].SetPosition(0, y + 22)
						self.bgDict[self.KEY_TICKET].Show()

						self.scrollDict[self.KEY_TICKET].SetSize(self.scrollDict[self.KEY_TICKET].GetWidth(), self.peekDict[self.KEY_TICKET].GetHeight())

						tmp = ui.TextLine()
						tmp.SetParent(self.scrollDict[self.KEY_TICKET])
						tmp.SetText("{} (x{})".format(ticketName, ticketCount))
						tmp.Show()
						tmp.SetHorizontalAlignCenter()
						tmp.SetWindowHorizontalAlignCenter()
						tmp.SetPosition(0, 0)
						self.ticketDict[0] = tmp

						tmp = ui.ExpandedImageBox()
						tmp.SetParent(self.scrollDict[self.KEY_TICKET])
						tmp.LoadImage(DungeonInfoWindow.IMG_PATH + "bg_ticket.png")
						tmp.Show()
						tmp.SetPosition(0, 18)
						tmp.SetWindowHorizontalAlignCenter()
						self.ticketDict[1] = tmp

						tmp = ui.ExpandedImageBox()
						tmp.SetParent(self.ticketDict[1])
						tmp.LoadImage(ticketIcon)
						tmp.Show()
						tmp.SetPosition(0, 0)
						tmp.SetWindowHorizontalAlignCenter()
						tmp.SetWindowVerticalAlignCenter()
						tmp.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.__OverIn))
						tmp.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.__OverOut))
						tmp.SAFE_SetEvent(self.__ClickTicket, "mouse_click")
						self.ticketDict[2] = tmp
					else:
						self.barDict[self.KEY_TICKET].Hide()
						self.bgDict[self.KEY_TICKET].Hide()

			self.UpdateScrollBarInformation(0)
			self.UpdateScrollBarElement(0)
			self.UpdateScrollBarTicket(0)

			self.Show()

		def RefreshDailyLimit(self):
			if app.USE_DUNGEON_COUNT_LIMIT_DAILY and self.dailyLimitText:
				numCooldownPlayer, numCooldownHwid1, numCooldownHwid2, numCount, numLimit, numRequiredCP = dungeonInfo.GetCooldown(self.index)
				if numLimit > 0:
					infoMapIndex = dungeonsDict[self.index].get("mapIndex", 0) if dungeonsDict.has_key(self.index) else 0
					self.dailyLimitText.SetText(localeinfo.DUNGEON_INFO_LEFT_COUNT_FOR_TODAY.format(numCount, FormatEffectiveLimit(infoMapIndex, numLimit)))

			if app.ENABLE_COMBAT_POINTS and self.combatPointsText and self.combatPointsReq > 0:
				if player.GetStatus(player.GEAR_CP) >= self.combatPointsReq:
					self.combatPointsText.SetPackedFontColor(0xFF00FF00)
				else:
					self.combatPointsText.SetPackedFontColor(0xFFFF0000)

		def __Drop(self):
			self.mainInst.OnDrop(self.index)

		def __init__(self, mainInst, k):
			self.isBuilded = False

			ui.Window.__init__(self)
			self.SetSize(188, 330)
			if localeinfo.IsARABIC():
				self.SetPosition(mainInst.GetWidth() - 630, 37)
			else:
				self.SetPosition(mainInst.GetWidth() - 210, 37)
			self.SetParent(mainInst)

			self.mainInst = proxy(mainInst)
			self.index = k
			self.dailyLimitText = None
			self.limitHelpBtn = None
			self.combatPointsText = None
			self.combatPointsReq = 0

			self.barDict = {}
			self.titleDict = {}
			self.bgDict = {}

			self.informationsDict = {}
			self.elementsDict = {}
			self.ticketDict = {}

			self.peekDict = {}
			self.scrollDict = {}
			self.scrollBarDict = {}
			self.sectionBgImgDict = {}

			self.itemVnum = 0

			for i in range(1, self.KEY_TICKET + 1):
				tmp = ui.ThinBoardCircle()
				tmp.SetParent(self)

				if i == self.KEY_INFORMATION:
					h = 102
				elif i == self.KEY_ELEMENT:
					h = 50
				elif i == self.KEY_TICKET:
					h = 61 + 8

				tmp.SetSize(self.GetWidth(), h)
				tmp.Hide()
				self.bgDict[i] = tmp

				tmpBg = ui.ExpandedImageBox()
				tmpBg.SetParent(self.bgDict[i])
				tmpBg.SetPosition(0, 0)
				tmpBg.AddFlag("not_pick")

				if i == self.KEY_INFORMATION:
					tmpBg.LoadImage(DungeonInfoWindow.IMG_REWORK + "info_bg.png")
				elif i == self.KEY_ELEMENT:
					tmpBg.LoadImage(DungeonInfoWindow.IMG_REWORK + "info_element.png")
				elif i == self.KEY_TICKET:
					tmpBg.LoadImage(DungeonInfoWindow.IMG_REWORK + "info_ticket.png")

				tmpBg.Show()
				self.sectionBgImgDict[i] = tmpBg

				tmp = ui.Window()
				# tmp.SetInsideRender(True)
				tmp.SetParent(self.bgDict[i])
				tmp.AddFlag("attach")
				tmp.AddFlag("not_pick")
				tmp.SetSize(self.bgDict[i].GetWidth(), self.bgDict[i].GetHeight() - 10)
				tmp.SetPosition(0, 5)
				tmp.Show()
				self.peekDict[i] = tmp

				tmp = ui.Window()
				tmp.SetParent(self.peekDict[i])
				tmp.AddFlag("attach")
				tmp.AddFlag("not_pick")
				tmp.SetSize(self.peekDict[i].GetWidth(), 0)
				tmp.SetPosition(0, 0)
				tmp.Show()
				self.scrollDict[i] = tmp

				if app.USE_CLIP_MASK:
					self.scrollDict[i].SetClippingMaskWindow(self.peekDict[i])

				tmp = DungeonInfoWindow.ScrollBar()
				tmp.SetParent(self.bgDict[i])
				tmp.SetPosition(self.peekDict[i].GetWidth() - 10, self.peekDict[i].GetLocalPosition()[1] + 2)
				tmp.SetSize(6, self.peekDict[i].GetHeight())

				if i == self.KEY_INFORMATION:
					tmp.SetScrollEvent(self.OnScrollBarInformation)
				elif i == self.KEY_ELEMENT:
					tmp.SetScrollEvent(self.OnScrollBarElement)

				tmp.SetScrollSpeed(self.SCROLL_SPEED)
				self.scrollBarDict[i] = tmp

				tmp = ui.ExpandedImageBox()
				tmp.SetParent(self)
				tmp.LoadImage(DungeonInfoWindow.IMG_REWORK + "title_bar.png")
				#tmp.SetDiffuseColor(DungeonInfoWindow.DIFFUSE_COLOR_BAR[0], DungeonInfoWindow.DIFFUSE_COLOR_BAR[1], DungeonInfoWindow.DIFFUSE_COLOR_BAR[2], DungeonInfoWindow.DIFFUSE_COLOR_BAR[3])
				tmp.SetPosition(0, 1)
				tmp.SetWindowHorizontalAlignCenter()
				tmp.Hide()
				self.barDict[i] = tmp

				tmp = ui.TextLine()
				tmp.SetParent(self.barDict[i])

				if i == self.KEY_INFORMATION:
					tmp.SetText(localeinfo.DUNGEON_INFO_INFORMATIONS)
				elif i == self.KEY_ELEMENT:
					tmp.SetText(localeinfo.DUNGEON_INFO_ELEMENTS)
				elif i == self.KEY_TICKET:
					tmp.SetText(localeinfo.DUNGEON_INFO_TICKET)

				tmp.SetPosition(0, 3)
				tmp.SetWindowHorizontalAlignCenter()
				tmp.SetHorizontalAlignCenter()
				tmp.Show()
				self.titleDict[i] = tmp

				self.dropButton = None

		def __del__(self):
			self.itemVnum = 0

			if self.dropButton:
				self.dropButton.SetEvent(None)
				del self.dropButton
				self.dropButton = None

			for v in self.informationsDict.values():
				del v

			self.informationsDict = {}

			for v in self.elementsDict.values():
				del v

			self.elementsDict = {}

			for k, v in self.ticketDict.items():
				if k == 1 or k == 2:
					v.SetStringEvent("MOUSE_OVER_IN", None)
					v.SetStringEvent("MOUSE_OVER_OUT", None)

				del v

			self.ticketDict = {}

			for v in self.peekDict.values():
				del v

			self.peekDict = {}

			for v in self.scrollDict.values():
				del v

			self.scrollDict = {}

			for v in self.scrollBarDict.values():
				v.ResetScrollEvent()
				del v

			self.scrollBarDict = {}

			for v in self.titleDict.values():
				del v

			self.titleDict = {}

			for v in self.barDict.values():
				del v

			self.barDict = {}

			for v in self.bgDict.values():
				del v

			self.bgDict = {}

			for v in self.sectionBgImgDict.values():
				del v

			self.sectionBgImgDict = {}

			ui.Window.__del__(self)

	class ElementItem(ui.ExpandedImageBox):
		SLOT_IMG_GREEN = "d:/ymir work/ui/dungeoninfo_rework/green.png"
		SLOT_IMG_GREEN_HOVER = "d:/ymir work/ui/dungeoninfo_rework/green_hover.png"
		SLOT_IMG_GREEN_SELECTED = "d:/ymir work/ui/dungeoninfo_rework/green_selected.png"
		SLOT_IMG_RED = "d:/ymir work/ui/dungeoninfo_rework/red.png"
		SLOT_IMG_RED_HOVER = "d:/ymir work/ui/dungeoninfo_rework/red_hover.png"
		SLOT_IMG_RED_SELECTED = "d:/ymir work/ui/dungeoninfo_rework/red_selected.png"

		def __ChangeSelected(self):
			if app.IsPressed(app.DIK_LSHIFT) or app.IsPressed(app.DIK_RSHIFT):
				self.mainInst.ChangeSelected(self.index)
				self.mainInst.QuickTeleport(self.index)
				return

			self.mainInst.ChangeSelected(self.index)

		def __OnShiftRightClick(self):
			if app.IsPressed(app.DIK_LSHIFT) or app.IsPressed(app.DIK_RSHIFT):
				self.mainInst.OnDrop(self.index)

		def RefreshSlotImage(self):
			if self.hasCooldown:
				if self.isSelected:
					newImg = self.SLOT_IMG_RED_SELECTED
				elif self.isHovered:
					newImg = self.SLOT_IMG_RED_HOVER
				else:
					newImg = self.SLOT_IMG_RED
			else:
				if self.isSelected:
					newImg = self.SLOT_IMG_GREEN_SELECTED
				elif self.isHovered:
					newImg = self.SLOT_IMG_GREEN_HOVER
				else:
					newImg = self.SLOT_IMG_GREEN

			if self.currentSlotImg != newImg:
				self.currentSlotImg = newImg
				self.UnloadImage()
				self.LoadImage(newImg)

		def __OverIn(self):
			self.isHovered = True
			self.RefreshSlotImage()

			if not self.wikiHoverTip:
				self.wikiHoverTip = uitooltip.ToolTip()

			self.wikiHoverTip.ClearToolTip()
			self.wikiHoverTip.AppendSpace(5)
			self.wikiHoverTip.AppendShortcutRow(("key_shift", "key_lclick"), localeinfo.TOOLTIP_TELEPORT_WIKI_HOVER)
			self.wikiHoverTip.AppendShortcutRow(("key_shift", "key_rclick"), localeinfo.TOOLTIP_DUNGEON_WIKI_HOVER)
			self.wikiHoverTip.ShowToolTip()

		def __OverOut(self):
			self.isHovered = False
			self.RefreshSlotImage()

			if self.wikiHoverTip:
				self.wikiHoverTip.HideToolTip()

		if app.USE_DUNGEON_COOLDOWN_MANAGER:
			def __OverInCooldownAlert(self):
				if not self.toolTip:
					self.toolTip = uitooltip.ToolTip()

				self.toolTip.ClearToolTip()
				self.toolTip.AutoAppendNewTextLineResize(localeinfo.DUNGEON_COOLDOWN_ALERT_TRUE if self.newStatus else localeinfo.DUNGEON_COOLDOWN_ALERT_FALSE)
				self.toolTip.ShowToolTip()

			def __OverOutCooldownAlert(self):
				if self.toolTip:
					self.toolTip.HideToolTip()

			def __ChangeCooldownAlert(self):
				oldStatus = constinfo.GetCooldownAlert(player.GetName(), self.mapIndex)

				if oldStatus:
					imgPath = DungeonInfoWindow.IMG_REWORK + "check_box.png"
					constinfo.SetCooldownAlert(player.GetName(), self.mapIndex, False)
					self.newStatus = False
				else:
					imgPath = DungeonInfoWindow.IMG_REWORK + "checked_box.png"
					constinfo.SetCooldownAlert(player.GetName(), self.mapIndex, True)
					self.newStatus = True

				self.cooldownAlertImg.UnloadImage()
				self.cooldownAlertImg.LoadImage(imgPath)

				self.__OverInCooldownAlert()

		def UpdateTime(self, currTime):
			lastConquerorLevel = 0
			if app.ENABLE_CONQUEROR_LEVEL:
				lastConquerorLevel = self.mainInst.lastConquerorLevel

			joinRet = RetJoin(self.index, currTime, self.mainInst.lastLevel, lastConquerorLevel, self.numCooldownPlayer, self.numCooldownHwid1, self.numCooldownHwid2, self.numCount, self.numLimit)

			oldCooldown = self.hasCooldown
			self.hasCooldown = (joinRet != 1)

			newUnable = (joinRet == 2)
			if self.isUnable != newUnable:
				self.isUnable = newUnable
				if self.isUnable:
					self.unableOverlay.Show()
				else:
					self.unableOverlay.Hide()

			if joinRet == 1:
				self.cannotText.SetText(localeinfo.DUNGEON_STATUS_1)
				self.cannotText.SetPackedFontColor(0xff16a085)
			else:
				if joinRet == 6:
					self.cannotText.SetText(localeinfo.DUNGEON_STATUS_7)
				elif joinRet == 2:
					self.cannotText.SetText(localeinfo.DUNGEON_STATUS_2)
				elif joinRet == 3:
					self.cannotText.SetText(localeinfo.DUNGEON_STATUS_3)
				elif joinRet == 4:
					self.cannotText.SetText(localeinfo.DUNGEON_STATUS_4)
				elif joinRet == 5:
					self.cannotText.SetText(localeinfo.DUNGEON_STATUS_5)
				else:
					self.cannotText.SetText(localeinfo.DUNGEON_STATUS_6)

				if joinRet == 5:
					self.cannotText.SetPackedFontColor(0xffd35400)
				else:
					self.cannotText.SetPackedFontColor(0xffc0392b)

			if oldCooldown != self.hasCooldown:
				self.RefreshSlotImage()

			if app.USE_DUNGEON_COUNT_LIMIT_DAILY and self.dungeonTitle:
				if self.numLimit > 0:
					self.dungeonTitle.SetText("{} {}/{}".format(self.baseDungeonName, self.numCount, FormatEffectiveLimit(self.mapIndex, self.numLimit)))
				else:
					self.dungeonTitle.SetText(self.baseDungeonName)

			leftPlayerSec = max(0, self.numCooldownPlayer - currTime)
			if self.lastPlayerSec != leftPlayerSec:
				self.lastPlayerSec = leftPlayerSec

				if leftPlayerSec > 0:
					if self.cooldownPlayer:
						self.cooldownPlayer.SetText(localeinfo.SecondToDHMS(leftPlayerSec))
						self.cooldownPlayer.SetPackedFontColor(0xffc0392b)
				else:
					if self.cooldownPlayer:
						self.cooldownPlayer.SetText("")

			leftHwid1Sec = max(0, self.numCooldownHwid1 - currTime)
			if self.lastHwid1Sec != leftHwid1Sec:
				self.lastHwid1Sec = leftHwid1Sec

				if leftHwid1Sec > 0:
					if self.cooldownHwid1:
						self.cooldownHwid1.SetText(localeinfo.DUNGEON_INFO_LEFT_DUNGEON_SLOT_COOLDOWN % (1, localeinfo.SecondToDHMS(leftHwid1Sec)))
						self.cooldownHwid1.SetPackedFontColor(0xffe67e22)
				else:
					if self.cooldownHwid1:
						self.cooldownHwid1.SetText("")

			leftHwid2Sec = max(0, self.numCooldownHwid2 - currTime)
			if self.lastHwid2Sec != leftHwid2Sec:
				self.lastHwid2Sec = leftHwid2Sec

				if leftHwid2Sec > 0:
					if self.cooldownHwid2:
						self.cooldownHwid2.SetText(localeinfo.DUNGEON_INFO_LEFT_DUNGEON_SLOT_COOLDOWN % (2, localeinfo.SecondToDHMS(leftHwid2Sec)))
						self.cooldownHwid2.SetPackedFontColor(0xffe67e22)
				else:
					if self.cooldownHwid2:
						self.cooldownHwid2.SetText("")

		def Refresh(self):
			self.lastPlayerSec = -1

			if app.USE_DUNGEON_COOLDOWN_MANAGER:
				self.lastHwid1Sec = -1
				self.lastHwid2Sec = -1

			(self.numCooldownPlayer, self.numCooldownHwid1, self.numCooldownHwid2, self.numCount, self.numLimit, self.numRequiredCP) = dungeonInfo.GetCooldown(self.index)

			timeNow = app.GetGlobalTimeStamp()

			self.UpdateTime(timeNow)

		if app.AUTO_HIDE_LOW_LEVELS_DUNGEONS:
			def __Hide(self):
				if app.USE_DUNGEON_COOLDOWN_MANAGER:
					oldStatus = constinfo.GetCooldownAlert(player.GetName(), self.mapIndex)

					if oldStatus:
						imgPath = DungeonInfoWindow.IMG_REWORK + "check_box.png"
						constinfo.SetCooldownAlert(player.GetName(), self.mapIndex, False)
						self.newStatus = False

						self.cooldownAlertImg.UnloadImage()
						self.cooldownAlertImg.LoadImage(imgPath)

				constinfo.HideDungeon(player.GetName(), self.index, 1)
				self.isShowing = 0
				self.mainInst.ReloadDungeons()

			def __OverInHideButton(self):
				if not self.hideButtonTip:
					self.hideButtonTip = uitooltip.ToolTip()

				self.hideButtonTip.ClearToolTip()
				self.hideButtonTip.AutoAppendNewTextLineResize(localeinfo.TOOLTIP_DUNGEON_HIDE)
				self.hideButtonTip.ShowToolTip()

			def __OverOutHideButton(self):
				if self.hideButtonTip:
					self.hideButtonTip.HideToolTip()

		def __init__(self, mainInst, c, k, v):
			ui.ExpandedImageBox.__init__(self)

			self.hasCooldown = False
			self.isSelected = False
			self.isHovered = False
			self.currentSlotImg = self.SLOT_IMG_GREEN
			self.LoadImage(self.SLOT_IMG_GREEN)

			self.mainInst = proxy(mainInst)
			self.SetParent(self.mainInst.wndScroll)

			self.mainInst.wndScroll.SetSize(self.mainInst.peekWidth, self.mainInst.wndScroll.GetHeight() + self.GetHeight())
			self.SetPosition(0, self.GetHeight() * c)

			self.index = k
			self.infoDict = v

			tmp = ui.Window()
			tmp.SetParent(self)
			tmp.SetSize(120, self.GetHeight() - 8)
			tmp.SetPosition(3, 6)
			tmp.Show()
			self.renderWindow = tmp

			self.renderTarget = None

			if v.has_key("renderMonsterVnum"):
				monsterVnum = v["renderMonsterVnum"]
				if monsterVnum > 0:
					if app.ENABLE_INGAME_WIKI:
						tmp = ingamewikiui.WikiRenderTarget(self.renderWindow.GetWidth(), self.renderWindow.GetHeight())
						tmp.SetParent(self.renderWindow)
						tmp.SetPosition(0, 0)
						tmp.Show()
						tmp.SetModel(monsterVnum, True,True)
						self.renderTarget = tmp

			tmp = ui.Window()
			tmp.SetParent(self)
			tmp.SetSize(self.GetWidth() - 123, self.GetHeight() - 8)
			tmp.SetPosition(123, 6)
			tmp.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.__ChangeSelected))
			tmp.SetMouseRightButtonUpEvent(ui.__mem_func__(self.__OnShiftRightClick))
			tmp.SetOverInEvent(ui.__mem_func__(self.__OverIn))
			tmp.SetOverOutEvent(ui.__mem_func__(self.__OverOut))
			tmp.Show()
			self.contentWindow = tmp

			self.dungeonTitle = None
			self.baseDungeonName = ""

			self.mapIndex = v["mapIndex"]
			if self.mapIndex > 0:
				self.baseDungeonName = localeinfo.GetMiniMapZoneNameByIdx(self.mapIndex)

				tmp = ui.TextLine()
				tmp.SetParent(self.contentWindow)
				tmp.SetPosition(0, 6)
				tmp.SetWindowHorizontalAlignCenter()
				tmp.SetHorizontalAlignCenter()
				tmp.SetText(self.baseDungeonName)
				tmp.Show()
				self.dungeonTitle = tmp

			if app.AUTO_HIDE_LOW_LEVELS_DUNGEONS:
				tmp = ui.MakeButton(self.contentWindow, 257, 0, "", DungeonInfoWindow.IMG_REWORK, "hide.png", "hide_hover.png", "hide_down.png")
				tmp.SetEvent(ui.__mem_func__(self.__Hide))
				tmp.SetOverEvent(ui.__mem_func__(self.__OverInHideButton))
				tmp.SetOverOutEvent(ui.__mem_func__(self.__OverOutHideButton))
				self.hideButton = tmp
				self.hideButtonTip = None

			self.wikiHoverTip = None

			if app.USE_DUNGEON_COOLDOWN_MANAGER:
				self.toolTip = None
				# self.dungeonClockImg = None

				tmp = ui.ExpandedImageBox()
				tmp.SetParent(self.contentWindow)

				if constinfo.GetCooldownAlert(player.GetName(), self.mapIndex):
					tmp.LoadImage(DungeonInfoWindow.IMG_REWORK + "checked_box.png")
					self.newStatus = True
				else:
					tmp.LoadImage(DungeonInfoWindow.IMG_REWORK + "check_box.png")
					self.newStatus = False

				tmp.SetPosition(258, 85)
				tmp.SetEvent(ui.__mem_func__(self.__ChangeCooldownAlert), "mouse_click")
				tmp.SetEvent(ui.__mem_func__(self.__OverInCooldownAlert), "mouse_over_in")
				tmp.SetEvent(ui.__mem_func__(self.__OverOutCooldownAlert), "mouse_over_out")
				tmp.Show()
				self.cooldownAlertImg = tmp

				# tmp = ui.ExpandedImageBox()
				# tmp.SetParent(self.contentWindow)
				# tmp.LoadImage("biolog_manager/clock2.png")
				# tmp.SetPosition(250 + 4, 75)
				# tmp.Show()
				# self.dungeonClockImg = tmp

			y = 22

			tmp = ui.TextLine()
			tmp.SetParent(self.contentWindow)
			tmp.SetPosition(0, y)
			tmp.SetWindowHorizontalAlignCenter()
			tmp.SetHorizontalAlignCenter()
			tmp.SetText("")
			tmp.Show()
			self.cooldownPlayer = tmp
			self.numCooldownPlayer = 0

			y += 16

			if app.USE_DUNGEON_COOLDOWN_MANAGER:
				tmp = ui.TextLine()
				tmp.SetParent(self.contentWindow)
				tmp.SetPosition(0, y)
				tmp.SetWindowHorizontalAlignCenter()
				tmp.SetHorizontalAlignCenter()
				tmp.SetText("")
				tmp.Show()
				self.cooldownHwid1 = tmp

				y += 16

				tmp = ui.TextLine()
				tmp.SetParent(self.contentWindow)
				tmp.SetPosition(0, y)
				tmp.SetWindowHorizontalAlignCenter()
				tmp.SetHorizontalAlignCenter()
				tmp.SetText("")
				tmp.Show()
				self.cooldownHwid2 = tmp

				y += 16

			# app.USE_DUNGEON_COOLDOWN_MANAGER
			self.numCooldownHwid1 = 0
			self.numCooldownHwid2 = 0

			# app.USE_DUNGEON_COUNT_LIMIT_DAILY
			self.numCount = 0
			self.numLimit = 0

			tmp = ui.TextLine()
			tmp.SetParent(self.contentWindow)
			tmp.SetPosition(0, y)
			tmp.SetWindowHorizontalAlignCenter()
			tmp.SetHorizontalAlignCenter()
			tmp.SetText("")
			tmp.Show()
			self.cannotText = tmp

			self.isShowing = 0 if constinfo.IsDungeonHided(player.GetName(), self.index) else 1

			tmp = ui.ExpandedImageBox()
			tmp.SetParent(self)
			tmp.LoadImage(DungeonInfoWindow.IMG_REWORK + "unable.png")
			tmp.SetPosition(0, 0)
			tmp.AddFlag("not_pick")
			tmp.Hide()
			self.unableOverlay = tmp
			self.isUnable = False

			self.Refresh()

		def __del__(self):
			if self.renderTarget:
				del self.renderTarget
				self.renderTarget = None

			if self.renderWindow:
				del self.renderWindow
				self.renderWindow = None

			if self.dungeonTitle:
				del self.dungeonTitle
				self.dungeonTitle = None

			# if self.dungeonClockImg:
				# del self.dungeonClockImg
				# self.dungeonClockImg = None

			if app.AUTO_HIDE_LOW_LEVELS_DUNGEONS and self.hideButton:
				self.hideButton.SetEvent(None)
				self.hideButton.SetOverEvent(None)
				self.hideButton.SetOverOutEvent(None)

				if self.hideButtonTip:
					del self.hideButtonTip
					self.hideButtonTip = None

			if self.cooldownAlertImg:
				self.cooldownAlertImg.SetEvent(None, "mouse_click")
				self.cooldownAlertImg.SetEvent(None, "mouse_over_in")
				self.cooldownAlertImg.SetEvent(None, "mouse_over_out")

				del self.cooldownAlertImg
				self.cooldownAlertImg = None

			if self.toolTip:
				del self.toolTip
				self.toolTip = None

			if self.wikiHoverTip:
				del self.wikiHoverTip
				self.wikiHoverTip = None

			if self.cooldownPlayer:
				del self.cooldownPlayer
				self.cooldownPlayer = None

			if app.USE_DUNGEON_COOLDOWN_MANAGER:
				if self.cooldownHwid1:
					del self.cooldownHwid1
					self.cooldownHwid1 = None

				if self.cooldownHwid2:
					del self.cooldownHwid2
					self.cooldownHwid2 = None

			if self.cannotText:
				del self.cannotText
				self.cannotText = None

			if self.unableOverlay:
				del self.unableOverlay
				self.unableOverlay = None

			if self.contentWindow:
				self.contentWindow.SetOnMouseLeftButtonUpEvent(None)
				self.contentWindow.SetMouseRightButtonUpEvent(None)
				self.contentWindow.SetOverInEvent(None)
				self.contentWindow.SetOverOutEvent(None)

				del self.contentWindow
				self.contentWindow = None

			self.mainInst = None

			ui.ExpandedImageBox.__del__(self)

	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.wndScroll.GetHeight() - self.wndPeek.GetHeight()) * fScale * -1.0), -self.wndScroll.GetHeight() + self.wndPeek.GetHeight()))
		self.wndScroll.SetPosition(0, curr)

	def ChangeScrollBar(self):
		if not self.scrollBar:
			return

		if self.wndScroll.GetHeight() <= self.wndPeek.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.wndPeek.GetHeight(), self.wndScroll.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.wndScroll.GetLocalPosition()[1]), (self.wndScroll.GetHeight() - self.wndPeek.GetHeight())))
			self.scrollBar.Show()

	def UpdateScrollBar(self, val = 0):
		curr = min(0, max(self.wndScroll.GetLocalPosition()[1] + val, -self.wndScroll.GetHeight() + self.wndPeek.GetHeight()))
		self.wndScroll.SetPosition(0, curr)

		self.ChangeScrollBar()

	def OnRunMouseWheel(self, iLen):
		if self.wndPeek.IsInPosition():
			if self.scrollBar and self.scrollBar.IsShow():
				self.UpdateScrollBar(int((iLen * 0.01) * self.SCROLL_SPEED))
				return True

		return False

	def __Build(self):
		self.wndScroll.SetSize(0, 0)

		c = 0
		global dungeonsDict
		for k, v in dungeonsDict.items():
			if self.dungeonsMyDict.has_key(k):
				for dungeon in self.dungeonsMyDict.values():
					del dungeon

				self.dungeonsMyDict = {}

				import dbg
				dbg.TraceError("DungeonInfoWindow.__Build: dungeon index {} already exists".format(k))
				return

			tmp = DungeonInfoWindow.ElementItem(self, c, k, v)
			tmp.Show()
			self.dungeonsMyDict[k] = tmp

			if app.ENABLE_INGAME_WIKI:
				if self.dungeonsMyInfoDict.has_key(k):
					for info in self.dungeonsMyInfoDict.values():
						del info

					self.dungeonsMyInfoDict = {}

					import dbg
					dbg.TraceError("DungeonInfoWindow.__Build: info index {} already exists".format(k))
					return

				tmp = DungeonInfoWindow.ElementItemInfo(self, k)
				tmp.Show()
				self.dungeonsMyInfoDict[k] = tmp

			c += 1

			if self.selectedIndex == -1:
				self.selectedIndex = k

		if len(self.dungeonsMyDict) == 0:
			return False

		self.ReloadDungeons()
		return True

	def Refresh(self):
		for v in self.dungeonsMyDict.values():
			v.Refresh()

		if app.ENABLE_INGAME_WIKI and app.USE_DUNGEON_COUNT_LIMIT_DAILY:
			if self.dungeonsMyInfoDict.has_key(self.selectedIndex):
				self.dungeonsMyInfoDict[self.selectedIndex].RefreshDailyLimit()

	if app.AUTO_HIDE_LOW_LEVELS_DUNGEONS:
		def ReloadDungeons(self):
			j = 0
			for k, v in self.dungeonsMyDict.items():
				if v.isShowing:
					v.Show()
					j += 1
					break

			if j == 0:
				for v in self.topButtonsDict.values():
					v.Hide()

				self.teleportBtn.Hide()
			else:
				for v in self.topButtonsDict.values():
					v.Show()

				self.teleportBtn.Show()

			self.wndScroll.SetSize(self.peekWidth, 0)

			s = 0
			self.selectedIndex = -1

			for k, v in self.dungeonsMyDict.items():
				if v.isShowing:
					v.Show()

					if j != 0 and self.selectedIndex == -1:
						self.selectedIndex = k

					self.wndScroll.SetSize(self.peekWidth, self.wndScroll.GetHeight() + v.GetHeight())
					v.SetPosition(0, v.GetHeight() * s)

					s += 1
				else:
					v.Hide()

			self.scrollBar.SetPos(0)
			self.scrollBar.OnScrollMove()

			self.UpdateScrollBar(0)

			self.__RefreshSelected()

		def Unhide(self):
			for v in self.dungeonsMyDict.values():
				constinfo.HideDungeon(player.GetName(), v.index, 0)
				v.isShowing = 1

			self.ReloadDungeons()

		def __OverInUnhide(self):
			if not self.unhideButtonTip:
				self.unhideButtonTip = uitooltip.ToolTip()

			self.unhideButtonTip.ClearToolTip()
			self.unhideButtonTip.AutoAppendNewTextLineResize(localeinfo.TOOLTIP_DUNGEON_SHOWALL)
			self.unhideButtonTip.ShowToolTip()

		def __OverOutUnhide(self):
			if self.unhideButtonTip:
				self.unhideButtonTip.HideToolTip()

	def RefreshLevel(self):
		if app.ENABLE_CONQUEROR_LEVEL:
			toRefresh = False

			if player.GetLevel() != self.lastLevel:
				self.lastLevel = player.GetLevel()
				toRefresh = True

			if player.GetStatus(player.POINT_CONQUEROR_LEVEL) != self.lastConquerorLevel:
				self.lastConquerorLevel = player.GetStatus(player.POINT_CONQUEROR_LEVEL)
				toRefresh = True

			if toRefresh:
				self.Refresh()
		else:
			if player.GetLevel() != self.lastLevel:
				self.lastLevel = player.GetLevel()
				self.Refresh()

	def RefreshEntryStatus(self):
		if not hasattr(self, "dungeonsMyInfoDict") or not hasattr(self, "selectedIndex"):
			return

		if self.selectedIndex >= 0 and self.dungeonsMyInfoDict.has_key(self.selectedIndex):
			self.dungeonsMyInfoDict[self.selectedIndex].RefreshDailyLimit()

	def ShowLimitTip(self, index):
		numCooldownPlayer, numCooldownHwid1, numCooldownHwid2, numCount, numLimit, numRequiredCP = dungeonInfo.GetCooldown(index)
		if numLimit <= 0:
			return

		if not self.limitTip:
			self.limitTip = DungeonLimitToolTip()

		global dungeonsDict
		mapIndex = dungeonsDict[index].get("mapIndex", 0) if dungeonsDict.has_key(index) else 0
		base = statusBaseLimits.get(mapIndex, 0)
		bank = (numLimit - base) if (base > 0 and numLimit > base) else 0

		tip = self.limitTip
		blocks = []
		blocks.append(("title", getattr(localeinfo, "DUNGEON_LIMIT_TIP_TITLE", "Daily Entry Limit"), tip.C_TITLE))
		blocks.append(("text", getattr(localeinfo, "DUNGEON_LIMIT_TIP_INTRO1", "Maximum number of dungeon entries per day."), tip.C_CELL_TXT))
		blocks.append(("text", getattr(localeinfo, "DUNGEON_LIMIT_TIP_INTRO2", "The PC limit has priority: when it is reached,"), tip.C_CELL_TXT))
		blocks.append(("text", getattr(localeinfo, "DUNGEON_LIMIT_TIP_INTRO3", "every character on this PC is blocked."), tip.C_CELL_TXT))
		blocks.append(("space", 6))
		if base > 0:
			blocks.append(("text", getattr(localeinfo, "DUNGEON_LIMIT_TIP_TODAY", "Entries today: {}/{} (+{} banked)").format(numCount, base, bank), tip.C_CANACT))
		else:
			blocks.append(("text", getattr(localeinfo, "DUNGEON_LIMIT_TIP_TODAY_PLAIN", "Entries today: {}/{}").format(numCount, numLimit), tip.C_CANACT))
		if statusRefund[1] > 0:
			refundColor = tip.C_ACTIVE
			if statusRefund[0] <= 0:
				refundColor = tip.C_USED
			blocks.append(("text", getattr(localeinfo, "DUNGEON_INFO_REFUNDS_LEFT", "Auto-refunds left today: {}/{}").format(statusRefund[0], statusRefund[1]), refundColor))
		if statusResetStamp[0] > 0:
			blocks.append(("reset", getattr(localeinfo, "DUNGEON_INFO_RESET_IN", "Daily reset in: {}").format(localeinfo.SecondToDHMS(max(0, statusResetStamp[0] - app.GetGlobalTimeStamp()))), tip.C_UPCOMING))
		blocks.append(("space", 8))
		blocks.append(("text", getattr(localeinfo, "DUNGEON_LIMIT_TIP_BANK_TITLE", "Entry Bank"), tip.C_HEAD_TXT))
		blocks.append(("text", getattr(localeinfo, "DUNGEON_LIMIT_TIP_BANK1", "Didn't use all your runs today? No worries!"), tip.C_CELL_TXT))
		blocks.append(("text", getattr(localeinfo, "DUNGEON_LIMIT_TIP_BANK2", "Unused entries carry over to tomorrow's limit."), tip.C_CELL_TXT))
		blocks.append(("space", 8))
		infoRows = [
			[getattr(localeinfo, "DUNGEON_LIMIT_TIP_INFO1", "The bank stores up to half of the daily limit.")],
			[getattr(localeinfo, "DUNGEON_LIMIT_TIP_INFO2", "No completion needed - banking is automatic.")],
			[getattr(localeinfo, "DUNGEON_LIMIT_TIP_INFO3", "Failed runs are refunded (2 per day, all dungeons).")],
			[getattr(localeinfo, "DUNGEON_LIMIT_TIP_INFO4", "Everything resets daily at midnight.")],
		]
		blocks.append(("table", [getattr(localeinfo, "DUNGEON_LIMIT_TIP_INFO_HEAD", "About this system")], [tip.WIDTH - tip.PAD * 2], infoRows, [tip.C_CELL_TXT] * len(infoRows)))

		tip.SetParent(self)
		tip.Build(blocks)
		tip.SetWindowHorizontalAlignCenter()
		tip.SetPosition(0, 40)
		tip.SetTop()
		tip.Show()

	def HideLimitTip(self):
		if self.limitTip:
			self.limitTip.Clear()
			self.limitTip.Hide()

	def OnUpdate(self):
		currTime = app.GetTime()
		if currTime > self.lastUpdate:
			self.lastUpdate = currTime + 1

			currTime = app.GetGlobalTimeStamp()
			for dungeon in self.dungeonsMyDict.values():
				dungeon.UpdateTime(currTime)

			if app.ENABLE_COMBAT_POINTS and self.selectedIndex >= 0:
				if self.dungeonsMyInfoDict.has_key(self.selectedIndex):
					info = self.dungeonsMyInfoDict[self.selectedIndex]
					if info.combatPointsText and info.combatPointsReq > 0:
						if player.GetStatus(player.GEAR_CP) >= info.combatPointsReq:
							info.combatPointsText.SetPackedFontColor(0xFF00FF00)
						else:
							info.combatPointsText.SetPackedFontColor(0xFFFF0000)

			if self.limitTip and self.limitTip.IsShow() and self.limitTip.resetLine and statusResetStamp[0] > 0:
				self.limitTip.resetLine.SetText(getattr(localeinfo, "DUNGEON_INFO_RESET_IN", "Daily reset in: {}").format(localeinfo.SecondToDHMS(max(0, statusResetStamp[0] - app.GetGlobalTimeStamp()))))

	def Show(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "DUNGEON_INFO")
		self.lastLevel = player.GetLevel()

		if app.ENABLE_CONQUEROR_LEVEL:
			self.lastConquerorLevel = player.GetStatus(player.POINT_CONQUEROR_LEVEL)

		global dungeonsLoaded
		global dungeonsDict

		if dungeonsLoaded and len(dungeonsDict) == 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_NOTHING_AVAILABLE)
			return

		if not dungeonsLoaded:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_NOTHING_AVAILABLE)
			return

		if len(self.dungeonsMyDict) == 0:
			if not self.__Build():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_NOTHING_AVAILABLE)
				return

			self.UpdateScrollBar(0)

		currTime = app.GetGlobalTimeStamp()
		for dungeon in self.dungeonsMyDict.values():
			dungeon.UpdateTime(currTime)

		self.lastUpdate = app.GetTime() + 1

		self.__RefreshSelected()
		self.Refresh()

		self.SetCenterPosition()
		self.SetTop()

		wndMgr.Show(self.hWnd)

	def Hide(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "DUNGEON_INFO")
		if self.topWin:
			self.topWin.Close()

		self.OnOverOutItem()
		self.OnCloseTeleportDlg()
		wndMgr.Hide(self.hWnd)

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("DUNGEON_INFO", x, y)

	def OnPressEscapeKey(self):
		self.Hide()
		return True

	def OnConfirmTeleportDlg(self):
		self.OnCloseTeleportDlg()
		self.waitWarp = app.GetTime() + 3
		dungeonInfo.Teleport(self.selectedIndex)

	def QuickTeleport(self, index):
		if app.USE_PREMIUM_FEATURES and constinfo.player_premium_type == player.PREMIUM_TYPE_NONE:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.QUICKTELEPORT_JUST_PREMIUM_PLUS)
			return
		diffTime = self.waitWarp - app.GetTime()
		if diffTime > 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_WAIT % (3))
			return

		global dungeonsDict
		if dungeonsDict.has_key(index):
			if app.ENABLE_CONQUEROR_LEVEL:
				charConquerorLevel = player.GetStatus(player.POINT_CONQUEROR_LEVEL)
				if charConquerorLevel < dungeonsDict[index]["levelConquerorMin"]:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_TELEPORT_MIN_LEVEL)
					return
				elif charConquerorLevel > dungeonsDict[index]["levelConquerorMax"]:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_TELEPORT_MAX_LEVEL)
					return

			charLevel = player.GetLevel()
			if charLevel < dungeonsDict[index]["levelMin"]:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_TELEPORT_MIN_LEVEL)
				return

		self.waitWarp = app.GetTime() + 3
		dungeonInfo.Teleport(index)

	if app.ENABLE_PIL_DUNGEON:
		# New cross-core direct entry. Bypasses the NPC entrance Teleport
		# step — server runs the lobby's RequestJoinDungeon flow after a
		# 3-sec countdown rendered by uifastenter.FastEnterCountdown.
		def __FastEnter(self):
			if self.selectedIndex < 0:
				return
			dungeonInfo.FastEnter(self.selectedIndex)

	def __Teleport(self):
		diffTime = self.waitWarp - app.GetTime()
		if diffTime > 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_WAIT % (3))
			return

		global dungeonsDict
		if dungeonsDict.has_key(self.selectedIndex):
			if app.ENABLE_CONQUEROR_LEVEL:
				charConquerorLevel = player.GetStatus(player.POINT_CONQUEROR_LEVEL)
				if charConquerorLevel < dungeonsDict[self.selectedIndex]["levelConquerorMin"]:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_TELEPORT_MIN_LEVEL)
					return
				elif charConquerorLevel > dungeonsDict[self.selectedIndex]["levelConquerorMax"]:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_TELEPORT_MAX_LEVEL)
					return

			charLevel = player.GetLevel()
			if charLevel < dungeonsDict[self.selectedIndex]["levelMin"]:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_TELEPORT_MIN_LEVEL)
				return
			# elif charLevel > dungeonsDict[self.selectedIndex]["levelMax"]:
				# chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DUNGEON_INFO_TELEPORT_MAX_LEVEL)
				# return

		if not self.teleportDlg:
			tmp = uicommon.QuestionDialog()
			tmp.SetText(localeinfo.DUNGEON_INFO_TELEPORT_DLG)
			tmp.SetAcceptEvent(ui.__mem_func__(self.OnConfirmTeleportDlg))
			tmp.SetCancelEvent(ui.__mem_func__(self.OnCloseTeleportDlg))
			self.teleportDlg = tmp

		if self.teleportDlg:
			self.teleportDlg.Open()

	if app.ENABLE_INGAME_WIKI:
		def BindWikiInst(self, wikiInst):
			if wikiInst:
				self.wikiInst = proxy(wikiInst)

	def __Top(self, topNum):
		if self.topWin and self.topWin.IsShow():
			self.topWin.Close()

		dungeonInfo.SendOpenTop(topNum, self.selectedIndex)

	def RefreshRanking(self):
		topNum = dungeonInfo.GetRankNum()

		if topNum >= dungeonInfo.TOP_MAX:
			return

		if not self.topWin:
			if app.ENABLE_INGAME_WIKI:
				self.topWin = self.TopWindow()
			else:
				#you may build it under another render method
				return

		if self.topWin:
			self.topWin.Open()

	def __Load(self):
		try:
			self.waitWarp = 0

			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/dungeoninfo_window.py")

			self.selectedIndex = -1

			self.board = self.GetChild("board_ui")

			self.titleBar = self.GetChild("titlebar_ui")
			self.titleBar.SetCloseEvent(ui.__mem_func__(self.Hide))

			if app.AUTO_HIDE_LOW_LEVELS_DUNGEONS:
				self.unhideButton = self.GetChild("reset_hided_button_ui")
				self.unhideButton.SetEvent(ui.__mem_func__(self.Unhide))
				self.unhideButton.SetOverEvent(ui.__mem_func__(self.__OverInUnhide))
				self.unhideButton.SetOverOutEvent(ui.__mem_func__(self.__OverOutUnhide))
				self.unhideButtonTip = None

			self.listUI = self.GetChild("list_ui")
			self.listUI.HideCorners(0)
			self.listUI.HideCorners(1)
			self.listUI.HideCorners(2)
			self.listUI.HideCorners(3)

			self.listUI.HideLine(0)
			self.listUI.HideLine(1)
			self.listUI.HideLine(2)
			self.listUI.HideLine(3)

			self.extraListUI = self.GetChild("extra_list_ui")
			self.extraListUI.HideCorners(0)
			self.extraListUI.HideCorners(1)
			self.extraListUI.HideCorners(2)
			self.extraListUI.HideCorners(3)

			self.extraListUI.HideLine(0)
			self.extraListUI.HideLine(1)
			self.extraListUI.HideLine(2)
			self.extraListUI.HideLine(3)

			tmp = ui.Window()
			# tmp.SetInsideRender(True)
			tmp.SetParent(self.listUI)
			tmp.AddFlag("attach")
			tmp.AddFlag("not_pick")
			tmp.SetSize(self.listUI.GetWidth() - 6, self.listUI.GetHeight() - 4)
			tmp.SetPosition(3, 2)
			tmp.Show()
			self.wndPeek = tmp

			tmp = ui.Window()
			tmp.SetParent(self.wndPeek)
			tmp.AddFlag("attach")
			tmp.AddFlag("not_pick")
			tmp.SetPosition(0, 0)
			tmp.Show()
			self.wndScroll = tmp

			if app.USE_CLIP_MASK:
				self.wndScroll.SetClippingMaskWindow(self.wndPeek)

			self.peekWidth = self.wndPeek.GetWidth()

			tmp = DungeonInfoWindow.ScrollBar()
			tmp.SetParent(self)
			if localeinfo.IsARABIC():
				tmp.SetPosition(self.listUI.GetLocalPosition()[0] - self.wndPeek.GetWidth() + 205, self.listUI.GetLocalPosition()[1] + 3)
			else:
				tmp.SetPosition(self.listUI.GetLocalPosition()[0] + self.wndPeek.GetWidth() + 8, self.listUI.GetLocalPosition()[1] + 3)
			tmp.SetSize(6, self.wndPeek.GetHeight())
			tmp.SetScrollEvent(self.OnScrollBar)
			tmp.SetScrollSpeed(DungeonInfoWindow.SCROLL_SPEED)
			self.scrollBar = tmp

			self.topButtonsDict = {}
			for i in xrange(dungeonInfo.TOP_MAX):
				tmp = self.GetChild("top%d_button_ui" % (i))
				tmp.SetEvent(ui.__mem_func__(self.__Top), i)
				self.topButtonsDict[i] = tmp

			tmp = self.GetChild("teleport_button_ui")
			tmp.SetEvent(ui.__mem_func__(self.__Teleport))
			self.teleportBtn = tmp

			# Fast-Enter button is declared in uiscript/dungeoninfo_window.py
			# (always present in the layout — edit x/y there to reposition
			# without touching this code). Bind click only when the feature
			# flag is on; hide it otherwise so the layout slot stays empty.
			fastBtn = self.GetChild("fast_enter_button_ui")
			if fastBtn:
				if app.ENABLE_PIL_DUNGEON:
					fastBtn.SetEvent(ui.__mem_func__(self.__FastEnter))
					self.fastEnterBtn = fastBtn
				else:
					fastBtn.Hide()
					self.fastEnterBtn = None
		except Exception as e:
			import dbg
			dbg.TraceError("DungeonInfoWindow.__Load: {}".format(e))
			app.Abort()

	def __init__(self):
		if app.USE_DUNGEON_INFO_ADDON_LEVEL_CAP:
			self.capLevelDlg = None

		self.topWin = None
		self.toolTipItem = None
		self.limitTip = None

		if app.ENABLE_INGAME_WIKI:
			self.wikiInst = None

		self.teleportDlg = None

		self.lastLevel = -1

		if app.ENABLE_CONQUEROR_LEVEL:
			self.lastConquerorLevel = -1

		self.peekWidth = 0

		if app.ENABLE_INGAME_WIKI:
			self.dungeonsMyInfoDict = {}

		self.dungeonsMyDict = {}

		ui.ScriptWindow.__init__(self)
		self.__Load()

	def Destroy(self):
		if app.USE_DUNGEON_INFO_ADDON_LEVEL_CAP:
			if self.capLevelDlg:
				self.capLevelDlg.Destroy()
				del self.capLevelDlg
				self.capLevelDlg = None

		for v in self.topButtonsDict.values():
			v.SetEvent(None)
			v = None

		self.topButtonsDict = {}

		if self.titleBar:
			self.titleBar.SetCloseEvent(None)
			self.titleBar = None

		if app.AUTO_HIDE_LOW_LEVELS_DUNGEONS and self.unhideButton:
			self.unhideButton.SetEvent(None)
			self.unhideButton.SetOverEvent(None)
			self.unhideButton.SetOverOutEvent(None)

			if self.unhideButtonTip:
				del self.unhideButtonTip
				self.unhideButtonTip = None

		if self.topWin:
			del self.topWin
			self.topWin = None

		if self.toolTipItem:
			self.toolTipItem.ClearToolTip()
			del self.toolTipItem
			self.toolTipItem = None

		if self.limitTip:
			self.limitTip.Clear()
			self.limitTip.Hide()
			self.limitTip = None

		if app.ENABLE_INGAME_WIKI:
			self.wikiInst = None

		if app.ENABLE_INGAME_WIKI:
			for info in self.dungeonsMyInfoDict.values():
				del info

			self.dungeonsMyInfoDict = {}

		for dungeon in self.dungeonsMyDict.values():
			del dungeon

		self.dungeonsMyDict = {}

		if self.scrollBar:
			self.scrollBar.ResetScrollEvent()
			del self.scrollBar
			self.scrollBar = None

		if self.wndScroll:
			del self.wndScroll
			self.wndScroll = None

		if self.wndPeek:
			del self.wndPeek
			self.wndPeek = None

		if self.teleportBtn:
			self.teleportBtn.SetEvent(None)
			self.teleportBtn = None

		if app.ENABLE_PIL_DUNGEON and hasattr(self, "fastEnterBtn") and self.fastEnterBtn:
			self.fastEnterBtn.SetEvent(None)
			self.fastEnterBtn = None

		if self.teleportDlg:
			self.teleportDlg.SetAcceptEvent(None)
			self.teleportDlg.SetCancelEvent(None)
			del self.teleportDlg
			self.teleportDlg = None

		self.ClearDictionary()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

if app.USE_DUNGEON_COOLDOWN_MANAGER:
	class CooldownAlert(object):
		def __init__(self, interfaceInst):
			self.lastUpdate = 0
			self.playerName = ""
			self.cachedDict = {}
			self.alertedK = []
			self.isLoaded = False

			self.interfaceInst = proxy(interfaceInst)

		def __del__(self):
			self.lastUpdate = 0
			self.playerName = ""
			self.cachedDict = {}
			self.alertedK = []
			self.isLoaded = False

			self.interfaceInst = None

		def Update(self):
			if not self.interfaceInst:
				return

			currTime = app.GetGlobalTimeStamp()
			if self.lastUpdate < currTime:
				self.lastUpdate = currTime + 10

				if self.playerName == "":
					self.playerName = player.GetName()

				global dungeonsDict

				if not self.isLoaded:
					self.isLoaded = True
					self.cachedDict = constinfo.GetCooldownsAlert(self.playerName)
					constinfo.cooldownMapIndexAlert = 0
				else:
					cooldownMapIndexAlert = constinfo.cooldownMapIndexAlert
					if cooldownMapIndexAlert:
						constinfo.cooldownMapIndexAlert = 0

						self.cachedDict = constinfo.GetCooldownsAlert(self.playerName)

						for k, v in dungeonsDict.items():
							if v["mapIndex"] == cooldownMapIndexAlert:
								if k in self.alertedK:
									self.alertedK.remove(k)

				if len(self.cachedDict) == 0:
					return

				for k, v in dungeonsDict.items():
					if k in self.alertedK:
						continue

					mapIndex = v["mapIndex"]

					if self.cachedDict.has_key(mapIndex):
						if self.cachedDict[mapIndex]:
							numCooldownPlayer, numCooldownHwid1, numCooldownHwid2, numCount, numLimit, numRequiredCP = dungeonInfo.GetCooldown(k)

							conquerorLevel = 0
							if app.ENABLE_CONQUEROR_LEVEL:
								conquerorLevel = player.GetStatus(player.POINT_CONQUEROR_LEVEL)

							joinRet = RetJoin(k, currTime, player.GetLevel(), conquerorLevel, numCooldownPlayer, numCooldownHwid1, numCooldownHwid2, numCount, numLimit)

							if joinRet == 1:
								chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, localeinfo.DUNGEON_COOLDOWN_TITLE, localeinfo.DUNGEON_COOLDOWN_DESCRIPTION % (localeinfo.GetMiniMapZoneNameByIdx(mapIndex)))
								self.interfaceInst.RecvWhisper(localeinfo.DUNGEON_COOLDOWN_TITLE)

								self.alertedK.append(k)
