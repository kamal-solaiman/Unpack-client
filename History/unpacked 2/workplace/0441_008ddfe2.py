# coding: latin_1

import app
import ui
import uicommon
import net
import player
import nonplayer
import localeinfo
import uitooltip
import game_data

IMG_PATH = "d:/ymir work/ui/game/teleport_window/"
CFG_FILE = "teleport.cfg"

BG_X = 6
BG_Y = 33
BG_W = 516
BG_H = 370
COL_X = BG_X + BG_W
COL_W = 212

# right_border.png draws the column frame at x=1/210, y=1/368 and a double rule
# at y=226/228; the panes below are the interiors those lines enclose.
PANE_X = COL_X + 2
PANE_W = 208
MAP_Y = BG_Y + 2
MAP_H = 224
LIST_Y = BG_Y + 229
LIST_H = 139

ROW_X = PANE_X
ROW_W = 198
ROW_H = 25
ROW_ICON_W = 26
ROW_ICON_X = ROW_W - ROW_ICON_W
HEADER_W = 199
HEADER_H = 28
HEADER_PAD = 10
ARROW_W = 8
ARROW_H = 5
ARROW_Y = (HEADER_H - ARROW_H) / 2

SCROLL_W = 7
SCROLL_X = ROW_X + ROW_W + (PANE_W - ROW_W - SCROLL_W) / 2

MINIMAP_SIZE = 200

# Locked regions are tinted rather than Disable()d: CButton::SetButtonColor
# only reaches the up/over/down visuals, so a disabled button would render its
# untinted disable visual and look identical to an open one.
REGION_LOCKED_TINT = 0.45

# The stock 7-frame waypoint sequence, drawn two frames at a time and
# cross-faded, so the original artwork plays continuously instead of cutting.
# mini_waypoint08..12 are NOT continuation frames -- they are 10x10 subs from
# an unrelated atlas region.
PING_PATH_FMT = "d:/ymir work/ui/minimap/mini_waypoint%02d.sub"
PING_FRAMES = 7
PING_SIZE = 30
PING_HALF = PING_SIZE / 2
PING_RATE = 1.15
# Share of the cycle spent ramping in at the start and out at the end; hides
# the wrap from the last (smallest) frame back to the first (largest).
PING_EDGE = 0.22
TILE_CELLS = 256

class ListWheelCatcher(ui.Window):
	"""The window manager only traverses CHILDREN for wheel events, so a
	top-level window's own OnRunMouseWheel is never called."""

	def __init__(self):
		ui.Window.__init__(self)
		self.scrollEvent = None

	def SetScrollEvent(self, event):
		self.scrollEvent = event

	def OnRunMouseWheel(self, nLen):
		if not self.IsInPosition():
			return False
		if self.scrollEvent:
			self.scrollEvent(nLen)
			return True
		return False


CAT_ORDER = (
	("loc",   "TELEPORT_CAT_LOCATIONS"),
	("stone", "TELEPORT_CAT_METINSTONES"),
	("boss",  "TELEPORT_CAT_BOSSES"),
	("npc",   "TELEPORT_CAT_NPCS"),
)


def _LoadConfirmSetting():
	try:
		return open(CFG_FILE, "rb").read().strip() != "0"
	except:
		return True


def _AllCollapsed():
	return dict((catKey, True) for catKey, locKey in CAT_ORDER)


# >>> #NO_EMPIRE_LOCK BEGIN -- no destination is empire-restricted (owner's
# >>> call, 2026-08-23). This was a client-only lock: CInputMain::TeleportWarp
# >>> never checked the empire, so the filter only hid rows the server would
# >>> have warped anyway. Restoring it means restoring the three call sites
# >>> below as well as this helper.
#def _MyPoints(points, empire):
#	"""The points this character may use -- empire 0 is everyone's."""
#	return [p for p in points if not p["empire"] or p["empire"] == empire]
# <<< #NO_EMPIRE_LOCK END


def _SaveConfirmSetting(flag):
	try:
		open(CFG_FILE, "wb").write(flag and "1" or "0")
	except:
		pass


# localeinfo's wrapper returns "Locale not found: KEY" instead of raising, so
# getattr's default argument is never reached.
def LocaleText(key, default):
	value = getattr(localeinfo, key, default)
	if not value or value.startswith("Locale not found"):
		return default

	return value


def _ScriptRegions(body):
	"""Atlas regions are the layout children that declare a "map".

	Read out of the script dict rather than off the widgets: the loader keeps
	only the keys it knows, and "map"/"tooltip"/"page" are ours.
	"""
	found = []
	stack = [body]
	while stack:
		node = stack.pop()
		if not node:
			continue
		for child in node.get("children", ()):
			stack.append(child)
			if "map" in child:
				found.append({"key": child["name"], "map": child["map"],
					"tooltip": child.get("tooltip", child["name"]),
					"page": int(child.get("page", 1))})
	return found


class TeleportWindow(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		self.selectedMap = None
		self.curPage = 1
		self.showConfirm = _LoadConfirmSetting()
		self.pendingPointID = 0
		self.pendingPointName = ""
		self.scrollIndex = 0
		self.displayList = []
		self.pinnedIndex = -2
		self.collapsed = _AllCollapsed()
		self.dlgQuestion = None
		self.scrollBar = None
		self.arrowBack = None
		self.arrowForward = None
		self.pageCount = 1
		self.regionToolTip = None
		self.lockedMaps = set()
		self.miniMapImage = None
		self.miniMapScale = 0.0
		self.miniMapW = 0
		self.miniMapH = 0
		self.miniMapX = 0
		self.miniMapY = 0

		self.__BuildRegionToolTip()
		self.__BuildAtlas()
		self.__BuildRightColumn()
		self.__BuildConfirmCheckbox()
		self.Hide()

	def __BuildAtlas(self):
		loader = ui.PythonScriptLoader()
		loader.LoadScriptFile(self, "uiscript/teleportwindow.py")

		board = self.GetChild("Board")
		board.SetTitleName(LocaleText("TELEPORT_WINDOW_TITLE", "Teleport"))
		board.SetCloseEvent(ui.__mem_func__(self.Close))
		self.bgImage = self.GetChild("Atlas")

		self.arrowBack = self.GetChild("ArrowBack")
		self.arrowBack.SetEvent(ui.__mem_func__(self.__OnPageBack))
		self.arrowForward = self.GetChild("ArrowForward")
		self.arrowForward.SetEvent(ui.__mem_func__(self.__OnPageForward))

		self.regionButtons = []
		for info in _ScriptRegions(loader.ScriptDictionary.get("window")):
			btn = self.GetChild(info["key"])
			if not btn:
				continue
			btn.SetEventOverIn(ui.__mem_func__(self.__OnRegionOverIn), info)
			btn.SetEventOverOut(ui.__mem_func__(self.__OnRegionOverOut))
			btn.SetEvent(ui.__mem_func__(self.__OnRegionClick), info["map"])
			btn.regionInfo = info
			self.regionButtons.append(btn)
			if info["page"] > self.pageCount:
				self.pageCount = info["page"]

		self.__RefreshPage()

	def __BuildRegionToolTip(self):
		tip = uitooltip.ToolTip()
		tip.HideToolTip()
		self.regionToolTip = tip

	def __RegionMinLevel(self, mapName):
		"""Lowest level that unlocks anything on this map."""
		data = game_data.teleportData
		if not data:
			return 1
		pts = data["points"].get(mapName, [])
		if not pts:
			return 1
		return min(int(p["min_lv"]) for p in pts)

	def __OnRegionOverIn(self, info):
		tip = self.regionToolTip
		if not tip:
			return
		minLv = self.__RegionMinLevel(info["map"])
		# Same red/grey the item tooltips use for an unmet level requirement.
		color = tip.GetLimitTextLineColor(player.GetStatus(player.LEVEL), minLv)
		tip.ClearToolTip()
		tip.SetTitle(LocaleText(info["tooltip"], info["key"]))
		tip.AppendTextLine(
			LocaleText("TELEPORT_TOOLTIP_LEVEL", "Required level: %d") % minLv, color)
		tip.ResizeToolTip()
		tip.ShowToolTip()

	def __OnRegionOverOut(self):
		if self.regionToolTip:
			self.regionToolTip.HideToolTip()

	def __BuildRightColumn(self):
		self.colBorder = self.GetChild("ColumnBorder")

		self.miniMapImage = None
		self.framePool = []
		self.pinCount = 0
		self.pinFrame = -1

		wheel = ListWheelCatcher()
		wheel.SetParent(self)
		wheel.SetPosition(PANE_X, LIST_Y)
		wheel.SetSize(PANE_W, LIST_H)
		wheel.SetScrollEvent(ui.__mem_func__(self.__OnListScroll))
		wheel.Show()
		self.wheelCatcher = wheel

		self.headerPool = []
		self.rowPool = []
		for i in xrange(len(CAT_ORDER)):
			hdr = ui.Button()
			hdr.SetParent(self)
			hdr.SetUpVisual(IMG_PATH + "btn_categ_norm.png")
			hdr.SetOverVisual(IMG_PATH + "btn_categ_norm.png")
			hdr.SetDownVisual(IMG_PATH + "btn_categ_norm.png")
			hdr.SetEvent(ui.__mem_func__(self.__OnHeaderClick), i)
			text = ui.TextLine()
			text.SetParent(hdr)
			if localeinfo.IsARABIC():
				text.SetPosition(HEADER_W - HEADER_PAD, HEADER_H / 2)
				text.SetHorizontalAlignLeft()
				arrowX = HEADER_PAD
			else:
				text.SetPosition(HEADER_PAD, HEADER_H / 2)
				arrowX = HEADER_W - HEADER_PAD - ARROW_W
			text.SetVerticalAlignCenter()
			text.SetOutline()
			text.Show()
			hdr.textLine = text
			arrow = ui.ImageBox()
			arrow.SetParent(hdr)
			arrow.LoadImage(IMG_PATH + "arrow_down.png")
			arrow.SetPosition(arrowX, ARROW_Y)
			arrow.AddFlag("not_pick")
			arrow.Show()
			hdr.arrowImage = arrow
			hdr.Hide()
			self.headerPool.append(hdr)

		maxRows = LIST_H / ROW_H + 1
		for i in xrange(maxRows):
			row = ui.Button()
			row.SetParent(self)
			row.SetUpVisual(IMG_PATH + "searchfield.png")
			row.SetOverVisual(IMG_PATH + "searchfield.png")
			row.SetDownVisual(IMG_PATH + "searchfield.png")
			row.SetEvent(ui.__mem_func__(self.__OnRowClick), i)
			text = ui.TextLine()
			text.SetParent(row)
			if localeinfo.IsARABIC():
				text.SetPosition(ROW_ICON_X - 6, ROW_H / 2)
				text.SetHorizontalAlignLeft()
			else:
				text.SetPosition(8, ROW_H / 2)
			text.SetVerticalAlignCenter()
			text.SetOutline()
			text.Show()
			row.textLine = text
			icon = ui.MakeButton(row, ROW_ICON_X, 0, "",
				IMG_PATH, "search_01.png", "search_02.png", "search_03.png")
			icon.SetEvent(ui.__mem_func__(self.__OnRowClick), i)
			row.iconButton = icon
			row.Hide()
			self.rowPool.append(row)

		# Same bar the wiki and party-finder windows build; art ships in patch1.
		import ingamewikiui_new
		bar = ingamewikiui_new.AdvScrollBar()
		bar.SetParent(self)
		bar.SetPosition(SCROLL_X, LIST_Y)
		bar.SetScrollBarSize(LIST_H)
		bar.SetScrollEvent(ui.__mem_func__(self.__OnScrollBarMove))
		bar.Hide()
		self.scrollBar = bar

	def __BuildConfirmCheckbox(self):
		cb = ui.CheckBox_Biolog()
		cb.SetParent(self)
		cb.SetPosition(BG_X + 10, BG_Y + 8)
		cb.SetText(LocaleText("TELEPORT_SHOW_CONFIRM", "Show Confirmation"))
		cb.SetChecked(self.showConfirm and 1 or 0)
		cb.SetEvent(ui.__mem_func__(self.__OnToggleConfirm))
		cb.Show()
		self.confirmCheck = cb

	# ------------------------------------------------------------------
	# page / region state

	def __RefreshPage(self):
		pages = max(1, self.pageCount)
		myLevel = player.GetStatus(player.LEVEL)
		self.lockedMaps = set()

		for btn in self.regionButtons:
			r = btn.regionInfo
			if r["page"] != self.curPage:
				btn.Hide()
				continue

			minLv = self.__RegionMinLevel(r["map"])

			btn.Show()
			if myLevel >= minLv:
				btn.SetButtonColor(1.0, 1.0, 1.0, 1.0)
			else:
				self.lockedMaps.add(r["map"])
				btn.SetButtonColor(REGION_LOCKED_TINT, REGION_LOCKED_TINT,
					REGION_LOCKED_TINT, 1.0)

		if self.arrowForward and self.arrowBack:
			if pages > 1 and self.curPage < pages:
				self.arrowForward.Show()
			else:
				self.arrowForward.Hide()
			if pages > 1 and self.curPage > 1:
				self.arrowBack.Show()
			else:
				self.arrowBack.Hide()

	def __OnPageForward(self):
		self.curPage += 1
		self.__RefreshPage()

	def __OnPageBack(self):
		self.curPage = max(1, self.curPage - 1)
		self.__RefreshPage()

	def __OnRegionClick(self, mapName):
		# The button stays enabled so its tint renders; the lock is enforced here.
		if mapName in self.lockedMaps:
			return
		self.selectedMap = mapName
		self.scrollIndex = 0
		self.collapsed = _AllCollapsed()
		self.__RefreshMiniMap()
		self.__RefreshList()

	def __OnToggleConfirm(self):
		self.showConfirm = self.confirmCheck.IsChecked()
		_SaveConfirmSetting(self.showConfirm)

	# ------------------------------------------------------------------
	# right column

	def __RefreshList(self):
		data = game_data.teleportData
		self.displayList = []
		self.pinnedIndex = -2
		if data and self.selectedMap:
			myLevel = player.GetStatus(player.LEVEL)
			pts = data["points"].get(self.selectedMap, [])
			spawns = data["spawns"].get(self.selectedMap, {})
			for catIdx, (catKey, locKey) in enumerate(CAT_ORDER):
				self.displayList.append(("header", catIdx, LocaleText(locKey, catKey)))
				if self.collapsed.get(catKey):
					continue
				if catKey == "loc":
					for p in pts:
						name = LocaleText(p["name"], p["name"])
						locked = myLevel < int(p["min_lv"])
						self.displayList.append(("loc", p, name, locked))
				else:
					for vnum, coords in spawns.get(catKey, []):
						name = nonplayer.GetMonsterName(int(vnum))
						if not name:
							name = str(vnum)
						self.displayList.append(("ping", coords, name, False))
		self.__RenderList()

	def __RenderList(self):
		for hdr in self.headerPool:
			hdr.Hide()
		for row in self.rowPool:
			row.Hide()

		maxIndex = self.__MaxScrollIndex()
		if self.scrollIndex > maxIndex:
			self.scrollIndex = maxIndex

		y = LIST_Y
		usedHeaders = 0
		usedRows = 0
		i = self.scrollIndex
		while i < len(self.displayList):
			entry = self.displayList[i]
			if entry[0] == "header":
				if y + HEADER_H > LIST_Y + LIST_H or usedHeaders >= len(self.headerPool):
					break
				hdr = self.headerPool[usedHeaders]
				hdr.SetPosition(ROW_X, int(y))
				hdr.textLine.SetText(entry[2])
				if self.collapsed.get(CAT_ORDER[entry[1]][0]):
					hdr.arrowImage.LoadImage(IMG_PATH + "arrow_down.png")
				else:
					hdr.arrowImage.LoadImage(IMG_PATH + "arrow_up.png")
				hdr.displayIndex = i
				hdr.Show()
				usedHeaders += 1
				y += HEADER_H
			else:
				if y + ROW_H > LIST_Y + LIST_H or usedRows >= len(self.rowPool):
					break
				row = self.rowPool[usedRows]
				row.SetPosition(ROW_X, int(y))
				name = entry[2]
				if entry[0] == "loc" and entry[3]:
					name = name + " " + (LocaleText("TELEPORT_ROW_LOCKED", "(Lv %d)") % int(entry[1]["min_lv"]))
				row.textLine.SetText(name)
				row.displayIndex = i
				row.Show()
				usedRows += 1
				y += ROW_H
			i += 1

		self.__UpdateScrollBar(maxIndex)

	def __MaxScrollIndex(self):
		total = 0
		i = len(self.displayList) - 1
		while i >= 0:
			if self.displayList[i][0] == "header":
				total += HEADER_H
			else:
				total += ROW_H
			if total > LIST_H:
				return i + 1
			i -= 1
		return 0

	def __UpdateScrollBar(self, maxIndex):
		if not self.scrollBar:
			return
		if maxIndex <= 0:
			self.scrollBar.Hide()
			return
		total = len(self.displayList)
		self.scrollBar.SetMiddleBarSize(float(total - maxIndex) / float(total))
		self.scrollBar.LockScroll()
		self.scrollBar.SetPos(float(self.scrollIndex) / float(maxIndex), False)
		self.scrollBar.UnlockScroll()
		self.scrollBar.Show()

	def __OnScrollBarMove(self):
		maxIndex = self.__MaxScrollIndex()
		if maxIndex <= 0:
			return
		# The thumb's drag area is the whole track, so GetPos overshoots 1.0 by
		# its own height near the bottom.
		index = min(maxIndex, max(0, int(round(self.scrollBar.GetPos() * maxIndex))))
		if index == self.scrollIndex:
			return
		self.scrollIndex = index
		self.__RenderList()

	def __RefreshMiniMap(self):
		self.__HidePins()
		self.pinnedIndex = -2
		if self.miniMapImage:
			self.miniMapImage.Hide()
			self.miniMapImage = None
		self.miniMapScale = 0.0
		self.miniMapW = 0
		self.miniMapH = 0
		self.miniMapX = 0
		self.miniMapY = 0

		data = game_data.teleportData
		if not data or not self.selectedMap:
			return

		img = ui.ExpandedImageBox()
		img.SetParent(self)
		try:
			img.LoadImage("d:/ymir work/ui/atlas/%s/atlas.sub" % self.selectedMap)
		except:
			img.Hide()
			return
		w = img.GetWidth()
		h = img.GetHeight()
		if w <= 0 or h <= 0:
			img.Hide()
			return
		scale = float(MINIMAP_SIZE) / float(max(w, h))
		img.SetScale(scale, scale)
		mapX = int(PANE_X + (PANE_W - w * scale) / 2)
		mapY = int(MAP_Y + (MAP_H - h * scale) / 2)
		img.SetPosition(mapX, mapY)
		img.Show()
		self.miniMapImage = img
		self.miniMapScale = scale
		self.miniMapW = w
		self.miniMapH = h
		self.miniMapX = mapX
		self.miniMapY = mapY

	def __OnHeaderClick(self, headerSlot):
		if headerSlot >= len(self.headerPool):
			return
		hdr = self.headerPool[headerSlot]
		idx = getattr(hdr, "displayIndex", -1)
		if idx < 0 or idx >= len(self.displayList):
			return
		catIdx = self.displayList[idx][1]
		catKey = CAT_ORDER[catIdx][0]
		self.collapsed[catKey] = not self.collapsed.get(catKey)
		self.__RefreshList()

	def __OnRowClick(self, rowSlot):
		if rowSlot >= len(self.rowPool):
			return
		row = self.rowPool[rowSlot]
		idx = getattr(row, "displayIndex", -1)
		if idx < 0 or idx >= len(self.displayList):
			return
		entry = self.displayList[idx]
		if entry[0] == "loc":
			if entry[3]:
				return
			self.__RequestWarp(int(entry[1]["id"]), entry[2])

	def __RequestWarp(self, pointID, pointName):
		if not self.showConfirm:
			net.SendTeleportWarpPacket(pointID)
			return
		if self.dlgQuestion:
			self.dlgQuestion.Close()
			self.dlgQuestion = None
		self.pendingPointID = pointID
		self.pendingPointName = pointName
		dlg = uicommon.QuestionDialog()
		dlg.SetText(LocaleText("TELEPORT_CONFIRM_WARP", "Teleport to %s?") % pointName)
		dlg.SetAcceptEvent(ui.__mem_func__(self.__OnConfirmWarp))
		dlg.SetCancelEvent(ui.__mem_func__(self.__OnCancelWarp))
		dlg.Open()
		self.dlgQuestion = dlg

	def __OnConfirmWarp(self):
		if self.dlgQuestion:
			self.dlgQuestion.Close()
			self.dlgQuestion = None
		if self.pendingPointID:
			net.SendTeleportWarpPacket(self.pendingPointID)
			self.pendingPointID = 0

	def __OnCancelWarp(self):
		if self.dlgQuestion:
			self.dlgQuestion.Close()
			self.dlgQuestion = None
		self.pendingPointID = 0

	def __HidePins(self):
		for frames in self.framePool:
			for box in frames:
				box.Hide()
		self.pinCount = 0
		self.pinFrame = -1

	def __ShowPins(self, coordList):
		self.__HidePins()
		if not self.miniMapImage or not self.selectedMap:
			return
		data = game_data.teleportData
		tiles = data["tiles"].get(self.selectedMap)
		if not tiles:
			return
		tilesX, tilesY = int(tiles[0]), int(tiles[1])
		if tilesX <= 0 or tilesY <= 0:
			return

		# One box per frame, each loaded once: CImageBox::LoadImage reallocates the
		# image instance and resets its diffuse colour, so it cannot be called from
		# the animation loop.
		while len(self.framePool) < len(coordList):
			frames = []
			for f in xrange(1, PING_FRAMES + 1):
				box = ui.ExpandedImageBox()
				box.LoadImage(PING_PATH_FMT % f)
				box.AddFlag("not_pick")
				frames.append(box)
			self.framePool.append(frames)

		# Pins are children of the atlas image, which is recreated on every map
		# switch, so re-parenting here always moves them above it in the child
		# list. Coordinates are relative to the image origin: SetScale does not
		# transform child positions, so the scale is applied here by hand.
		for i, c in enumerate(coordList):
			px = float(c[0]) / float(tilesX * TILE_CELLS) * self.miniMapW * self.miniMapScale
			py = float(c[1]) / float(tilesY * TILE_CELLS) * self.miniMapH * self.miniMapScale
			for box in self.framePool[i]:
				box.SetParent(self.miniMapImage)
				box.SetPosition(int(px) - PING_HALF, int(py) - PING_HALF)
		self.pinCount = len(coordList)
		self.pinFrame = -1
		self.__AnimatePins()

	def __AnimatePins(self):
		if not self.pinCount:
			return
		t = (app.GetTime() * PING_RATE) % 1.0
		f = t * PING_FRAMES
		idx = int(f)
		if idx >= PING_FRAMES:
			idx = PING_FRAMES - 1
		nxt = (idx + 1) % PING_FRAMES
		edge = min(t, 1.0 - t) / PING_EDGE
		if edge > 1.0:
			edge = 1.0
		frac = f - idx
		alphaCur = (1.0 - frac) * edge
		alphaNxt = frac * edge

		if idx != self.pinFrame:
			prev = self.pinFrame
			for i in xrange(self.pinCount):
				frames = self.framePool[i]
				if prev >= 0:
					frames[prev].Hide()
					frames[(prev + 1) % PING_FRAMES].Hide()
				frames[idx].Show()
				frames[nxt].Show()
			self.pinFrame = idx

		for i in xrange(self.pinCount):
			frames = self.framePool[i]
			frames[idx].SetDiffuseColor(1.0, 1.0, 1.0, alphaCur)
			frames[nxt].SetDiffuseColor(1.0, 1.0, 1.0, alphaNxt)

	def __HoveredIndex(self):
		for row in self.rowPool:
			if row.IsShow() and row.IsInPosition():
				return getattr(row, "displayIndex", -1)
		return -1

	def __ApplyPins(self, index):
		if 0 <= index < len(self.displayList):
			entry = self.displayList[index]
			if entry[0] == "loc":
				self.__ShowPins([[int(entry[1]["x"]), int(entry[1]["y"])]])
				return
			if entry[0] == "ping":
				self.__ShowPins(entry[1])
				return
		data = game_data.teleportData
		if not data or not self.selectedMap:
			self.__HidePins()
			return
		pts = data["points"].get(self.selectedMap, [])
		self.__ShowPins([[int(p["x"]), int(p["y"])] for p in pts])

	def OnUpdate(self):
		if not self.miniMapImage:
			return
		hoverIndex = self.__HoveredIndex()
		if hoverIndex != self.pinnedIndex:
			self.pinnedIndex = hoverIndex
			self.__ApplyPins(hoverIndex)
		self.__AnimatePins()

	def __OnListScroll(self, nLen):
		if not self.displayList:
			return
		if nLen > 0:
			self.scrollIndex = max(0, self.scrollIndex - 1)
		else:
			self.scrollIndex = min(self.__MaxScrollIndex(), self.scrollIndex + 1)
		self.__RenderList()

	# ------------------------------------------------------------------
	# lifecycle

	def Open(self):
		self.__RefreshPage()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		if self.regionToolTip:
			self.regionToolTip.HideToolTip()
		if self.dlgQuestion:
			self.dlgQuestion.Close()
			self.dlgQuestion = None
		self.Hide()

	def Toggle(self):
		if self.IsShow():
			self.Close()
		else:
			self.Open()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Destroy(self):
		self.Close()
		self.regionButtons = []
		self.regionToolTip = None
		self.headerPool = []
		self.rowPool = []
		self.framePool = []
		self.pinCount = 0
		self.pinFrame = -1
		self.miniMapImage = None
		self.confirmCheck = None
		self.dlgQuestion = None
		self.wheelCatcher = None
		self.scrollBar = None
