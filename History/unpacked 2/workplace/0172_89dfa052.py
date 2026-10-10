# coding: latin_1

import ui
import wndMgr
import net
import biologmgr

import dbg
import item

import localeinfo
import app

import player
from _weakref import proxy
import uiscriptlocale

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

SKILL_SLOT_ENABLE = "d:/ymir work/ui/pet/skill_button/skill_enable_button.sub"

SEON_PYEONG = 20091
BIOLOG_ADDITIONAL_COUNT = 2
BIOLOG_ADDITIONAL_ITEMS_DEFAULT = (59917, 59919)    # Time + Chance for missions 0-15
BIOLOG_ADDITIONAL_ITEMS_NEW     = (59918, 59920)    # Time (Zodiac) + Chance for missions 16+
NEW_MISSION_THRESHOLD = 14

# Mission overview data (sourced from biolog_missions / biolog_rewards DB tables)
# Groups: main mission (collect items, stat bonuses) + optional sub mission (deliver 1 item, get reward item)
BIOLOG_MISSION_GROUPS = [
	{
		"level": 30,
		"main": {"id": 0, "item": 30006, "count": 10, "bonuses": [(item.APPLY_ATTBONUS_MONSTER, 5)]},
		"sub":  {"id": 1, "item": 30220, "count": 1, "reward_item": 50109},
	},
	{
		"level": 40,
		"main": {"id": 2, "item": 30047, "count": 15, "bonuses": [(item.APPLY_ATTBONUS_STONE, 5)]},
		"sub":  {"id": 3, "item": 30221, "count": 1, "reward_item": 50110},
	},
	{
		"level": 50,
		"main": {"id": 4, "item": 30015, "count": 15, "bonuses": [(item.APPLY_MELEE_MAGIC_ATTBONUS_PER, 5)]},
		"sub":  {"id": 5, "item": 30222, "count": 1, "reward_item": 50111},
	},
	{
		"level": 60,
		"main": {"id": 6, "item": 30050, "count": 20, "bonuses": [(item.APPLY_ATTBONUS_BOSS, 5), (item.APPLY_ATT_SPEED, 10)]},
		"sub":  {"id": 7, "item": 30223, "count": 1, "reward_item": 50112},
	},
	{
		"level": 70,
		"main": {"id": 8, "item": 30165, "count": 25, "bonuses": [(item.APPLY_MALL_ATTBONUS, 5), (item.APPLY_DEF_GRADE_BONUS, 50)]},
		"sub":  {"id": 9, "item": 30224, "count": 1, "reward_item": 50113},
	},
	{
		"level": 80,
		"main": {"id": 10, "item": 30166, "count": 30, "bonuses": [(item.APPLY_RESIST_WARRIOR, 10), (item.APPLY_RESIST_ASSASSIN, 10), (item.APPLY_RESIST_SURA, 10), (item.APPLY_RESIST_SHAMAN, 10), (item.APPLY_MAX_HP, 500)]},
		"sub":  {"id": 11, "item": 30225, "count": 1, "reward_item": 50114},
	},
	{
		"level": 85,
		"main": {"id": 12, "item": 30167, "count": 40, "bonuses": [(item.APPLY_ATTBONUS_WARRIOR, 10), (item.APPLY_ATTBONUS_ASSASSIN, 10), (item.APPLY_ATTBONUS_SURA, 10), (item.APPLY_ATTBONUS_SHAMAN, 10), (item.APPLY_MAX_HP, 500)]},
		"sub":  {"id": 13, "item": 30226, "count": 1, "reward_item": 50115},
	},
	{
		"level": 90,
		"main": {"id": 14, "item": 30168, "count": 50, "bonuses": [(item.APPLY_ATT_SPEED, 10), (item.APPLY_NORMAL_HIT_DAMAGE_BONUS, 10), (item.APPLY_ATTBONUS_STONE, 5), (item.APPLY_ATTBONUS_BOSS, 5)]},
		"sub":  {"id": 15, "item": 30227, "count": 1, "reward_item": 50115},
	},
	{
		"level": 92,
		"main": {"id": 16, "item": 30251, "count": 20, "bonuses": [(item.APPLY_ATT_GRADE_BONUS, 50), (item.APPLY_SKILL_DEFEND_BONUS_BOSS_OR_MORE, 5)]},
		"sub": None,
	},
	{
		"level": 94,
		"main": {"id": 17, "item": 30252, "count": 20, "bonuses": [(item.APPLY_ATT_GRADE_BONUS, 60), (item.APPLY_NORMAL_HIT_DAMAGE_BONUS_BOSS_OR_MORE, 5)]},
		"sub": None,
	},
	{
		"level": 100,
		"main": {"id": 18, "item": 31136, "count": 20,  "bonuses": [(item.APPLY_MALL_ATTBONUS, 5),(item.APPLY_ATTBONUS_BOSS, 5), (item.APPLY_ATTBONUS_STONE, 5)]},
		"sub": None,
	},
	{
		"level": 105,
		"main": {"id": 19, "item": 31137, "count": 20, "bonuses": [(item.APPLY_MALL_ATTBONUS, 5),(item.APPLY_ATTBONUS_BOSS, 10), (item.APPLY_ATTBONUS_STONE, 10)]},
		"sub": None,
	},
]

# Build reverse lookup: item_vnum -> mission_id
BIOLOG_ITEM_TO_MISSION = {}
for _group in BIOLOG_MISSION_GROUPS:
	BIOLOG_ITEM_TO_MISSION[_group["main"]["item"]] = _group["main"]["id"]
	if _group["sub"]:
		BIOLOG_ITEM_TO_MISSION[_group["sub"]["item"]] = _group["sub"]["id"]

# Overview card layout
OVERVIEW_CARD_IMAGE = "d:/ymir work/ui/bio_rework/bio_list.png"
OVERVIEW_CARD_LOCKED_IMAGE = "d:/ymir work/ui/bio_rework/bio_locked.png"
OVERVIEW_CARD_DONE_IMAGE = "d:/ymir work/ui/bio_rework/bio_done.png"
OVERVIEW_CARD_WIDTH = 313
OVERVIEW_CARD_HEIGHT = 126

# Slot positions (estimated from image)
OVERVIEW_SLOT_LEFT_X = 271
OVERVIEW_SLOT_LEFT_Y = 30 + 15
OVERVIEW_SLOT_RIGHT_X = 10
OVERVIEW_SLOT_RIGHT_Y = 30 + 15
OVERVIEW_SLOT_SIZE = 32

# Text positions
OVERVIEW_HEADER_X = 100
OVERVIEW_HEADER_Y = 4 + 15
OVERVIEW_MAIN_TEXT_X = 50 + 5
OVERVIEW_MAIN_TEXT_Y = 22 + 15
OVERVIEW_SUB_TEXT_X = 50
OVERVIEW_SUB_TEXT_Y = 36 + 15
OVERVIEW_EFFECTS_START_Y = 55 + 10 + 18
OVERVIEW_EFFECTS_LINE_HEIGHT = 14
OVERVIEW_EFFECTS_X = 15
OVERVIEW_EFFECTS_X2 = 165

# Color constants for overview
OVERVIEW_COLOR_COMPLETED_HEADER = 0xFF4CAF50
OVERVIEW_COLOR_COMPLETED_TEXT = 0xFF7A7A7A
OVERVIEW_COLOR_CURRENT_HEADER = 0xFFFFCC00
OVERVIEW_COLOR_CURRENT_TEXT = 0xFFFFFFFF
OVERVIEW_COLOR_LOCKED_TEXT = 0xFF555555
OVERVIEW_COLOR_EFFECT_TEXT = 0xFFB0B0B0

# Main tab background positioning (328x279 centered in 354x322 content area)
MAIN_BG_X = 13
MAIN_BG_Y = 21

# Delivery gauge (fill image sits 2px inset inside empty at x:137, y:53)
DELIVERY_GAUGE_FILL_IMAGE = "d:/ymir work/ui/bio_rework/fill_count_full.png"
DELIVERY_GAUGE_FILL_X = 23
DELIVERY_GAUGE_FILL_Y = 55

# Cooldown gauge (fill image sits 2px inset inside empty, fills empty->full as cooldown expires)
COOLDOWN_GAUGE_FILL_IMAGE = "d:/ymir work/ui/bio_rework/fill_full_remaining.png"
COOLDOWN_GAUGE_FILL_X = 28
COOLDOWN_GAUGE_FILL_Y = 156

# ===== Overview / History tab: compact scrolling mission table (rework) =====
# One row per mission level (status rail + Lv + full-size item icon + name/progress).
# Missions give affects only (no item reward), so there is no reward column; the
# affects show in a floating ui.Table on hover (BonusTablePanel). Replaces the old
# full-card MissionGroupItem (kept below, deprecated).
ROW_WIDTH = 312          # must match OverviewList "itemsize_x" in the uiscript
ROW_HEIGHT = 34          # must match OverviewList "itemsize_y" (fits a native 32px icon)
ROW_ICON_SIZE = 32       # native item-icon size - NOT scaled
ROW_RAIL_W = 3

# Column X (left-to-right; mirrored for Arabic via MissionRowItem._X)
ROW_LV_X = 8
ROW_MAIN_ICON_X = 50
ROW_TEXT_X = 90
ROW_ICON_Y = (ROW_HEIGHT - ROW_ICON_SIZE) // 2      # 1
ROW_TEXT_Y = 9

# Row backgrounds (0xAARRGGBB)
ROW_BG_ODD = 0x14FFFFFF          # faint zebra stripe
ROW_BG_CURRENT = 0x33FFCC00      # gold highlight on the active mission

# Overview list / header placement inside OverviewBoard
OV_LIST_X = 8
OV_HEADER_Y = 8
OV_HEADER_SEP_Y = 26
OV_HEADER_COLOR = 0xFFB0B0B0
OV_HEADER_SEP_COLOR = 0x40FFFFFF

# Floating affects table (shown on row hover).
BONUS_TABLE_WIDTH = 208
BONUS_VALUE_COL_W = 62
BONUS_ROW_H = 20
BONUS_HEAD_H = 19
BONUS_PANEL_PAD = 9
BONUS_TITLE_H = 18
BONUS_PANEL_WIDTH = BONUS_TABLE_WIDTH + BONUS_PANEL_PAD * 2
# ui.Table color scheme - identical to the syshelp skill's SCHEME.
# [lineColor, headerBgColor, rowBgColor, headerTextColor, cellTextColor]
BONUS_TABLE_COLORS = [0xff756657, 0xff281f1a, 0xff1a1615, 0xffcabdab, 0xffc7c7c7]
BONUS_TITLE_COLOR = 0xffcabdab

class BonusTablePanel(ui.ThinBoard):
	# Floating v2 thinboard holding a 2-column ui.Table [Effect | Value].
	# Rebuilt per hover (few rows, user-paced), positioned beside the biolog window.
	def __init__(self):
		ui.ThinBoard.__init__(self, "UI", 1)
		self.AddFlag("float")
		self.AddFlag("not_pick")
		self.arabic = localeinfo.IsARABIC()
		self.titleLine = ui.MakeTextLineColor(self, BONUS_PANEL_PAD, BONUS_PANEL_PAD, "", BONUS_TITLE_COLOR)
		# RTL: keep align-left but anchor at the panel's right edge, so the Arabic
		# title flows leftward from there instead of hugging the left border.
		self.titleLine.SetHorizontalAlignLeft()
		if self.arabic:
			self.titleLine.SetPosition(BONUS_PANEL_WIDTH - BONUS_PANEL_PAD, BONUS_PANEL_PAD)
		self.titleLine.AddFlag("not_pick")
		self.titleLine.Show()
		self.table = None
		self.Hide()

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def Fill(self, titleText, rows):
		# rows = list of (effectName, valueString)
		self.titleLine.SetText(titleText)
		if self.table:
			self.table.Hide()
			self.table = None

		arabic = self.arabic
		nameW = BONUS_TABLE_WIDTH - BONUS_VALUE_COL_W
		effectHdr = getattr(localeinfo, "BIOLOG_OVERVIEW_COL_EFFECT", "Effect")
		valueHdr = getattr(localeinfo, "BIOLOG_OVERVIEW_COL_VALUE", "Value")

		# RTL: reverse column order (headers, widths, and each row) so the Effect
		# column reads on the right and lines up with its header (syshelp convention).
		headers = [effectHdr, valueHdr]
		widths = [nameW, BONUS_VALUE_COL_W]
		if arabic:
			headers.reverse()
			widths.reverse()

		table = ui.Table(BONUS_TABLE_WIDTH, BONUS_HEAD_H, BONUS_TABLE_COLORS)
		table.SetParent(self)
		table.SetPosition(BONUS_PANEL_PAD, BONUS_PANEL_PAD + BONUS_TITLE_H)
		table.set_columns(headers, widths)
		for effectName, valueStr in rows:
			data = [effectName, valueStr]
			if arabic:
				data.reverse()
			table.add_row(data, BONUS_ROW_H, cell_aligns = ["all:center", "all:center"])
		table.Show()
		self.table = table

		self.SetSize(BONUS_PANEL_WIDTH,
					 BONUS_PANEL_PAD + BONUS_TITLE_H + table.table_height + BONUS_PANEL_PAD)

	def ShowAt(self, x, y):
		self.SetPosition(int(x), int(y))
		self.SetTop()
		self.Show()

class BiologManager(ui.ScriptWindow):
	TEXT_OBJECTS = {}
	CHECKBOX_OBJECTS = {}
	BUTTON_OBJECTS = {}

	class ListBoxItem(ui.ListBoxEx.Item):
		def __init__(self, parent, text, colour, center = False):
			ui.ListBoxEx.Item.__init__(self)

			ui.ListBoxEx.Item.SetParent(self, parent)
			self.parent = proxy(parent)

			self.textBox = ui.TextLine()
			self.textBox.SetParent(self)
			self.textBox.SetText(text)
			if center:
				self.textBox.SetHorizontalAlignCenter()
				self.textBox.SetWindowHorizontalAlignCenter()
			self.textBox.SetPackedFontColor(colour)
			self.textBox.Show()

			self.Show()

		def __del__(self):
			ui.ListBoxEx.Item.__del__(self)

		def OnMouseLeftButtonDown(self):
			pass

		def OnRender(self):
			pass

	# >>> DEPRECATED (kept for reference, no longer instantiated) SECTION BEGIN >>>
	# Old full-card overview row. Superseded by MissionRowItem below, which renders
	# a compact scrolling table instead of a 126px card wall. Safe to remove later.
	class MissionGroupItem(ui.ListBoxEx.Item):
		def __init__(self, parent, group, completed, activeMain, activeSub, locked, givenItems, requiredItems, toolTip):
			ui.ListBoxEx.Item.__init__(self)
			ui.ListBoxEx.Item.SetParent(self, parent)
			self.parent = proxy(parent)
			self.textLines = []
			self.slots = []

			if completed:
				headerColor = OVERVIEW_COLOR_COMPLETED_HEADER
				detailColor = OVERVIEW_COLOR_COMPLETED_TEXT
			elif activeMain or activeSub:
				headerColor = OVERVIEW_COLOR_CURRENT_HEADER
				detailColor = OVERVIEW_COLOR_CURRENT_TEXT
			else:
				headerColor = OVERVIEW_COLOR_LOCKED_TEXT
				detailColor = OVERVIEW_COLOR_LOCKED_TEXT

			# Background card image
			self.bgImage = ui.ImageBox()
			self.bgImage.SetParent(self)
			self.bgImage.LoadImage(OVERVIEW_CARD_IMAGE)
			self.bgImage.SetPosition(0, 15)
			self.bgImage.Show()

			# Status prefix
			if completed:
				prefix = "[V] "
			elif activeMain or activeSub:
				prefix = "[>] "
			else:
				prefix = "[X] "

			# Level header
			headerText = "%sLv. %d" % (prefix, group["level"])
			self.__AddTextLine(headerText, headerColor, OVERVIEW_HEADER_X, OVERVIEW_HEADER_Y)

			# Main mission item slot (left)
			mainData = group["main"]
			mainSlot = self.__CreateSlot(OVERVIEW_SLOT_LEFT_X, OVERVIEW_SLOT_LEFT_Y)
			mainSlot.SetItemSlot(0, mainData["item"], 0)
			if toolTip:
				mainSlot.SetOverInItemEvent(lambda slotNum, vnum=mainData["item"], tt=toolTip: self.__OnOverInItem(vnum, tt))
				mainSlot.SetOverOutItemEvent(lambda: self.__OnOverOutItem(toolTip))
			self.slots.append(mainSlot)

			# Main mission text
			item.SelectItem(mainData["item"])
			mainItemName = item.GetItemName()
			if activeMain:
				mainText = "%s x%d (%d/%d)" % (mainItemName, mainData["count"], givenItems, requiredItems)
			elif completed:
				mainText = "%s x%d (%d/%d)" % (mainItemName, mainData["count"], mainData["count"], mainData["count"])
			else:
				mainText = "%s x%d" % (mainItemName, mainData["count"])
			self.__AddTextLine(mainText, detailColor, OVERVIEW_MAIN_TEXT_X, OVERVIEW_MAIN_TEXT_Y)

			# Sub mission text
			subData = group.get("sub")
			if subData:
				item.SelectItem(subData["item"])
				subItemName = item.GetItemName()
				if activeSub:
					subText = "%s x%d (%d/%d)" % (subItemName, subData["count"], givenItems, requiredItems)
				elif completed:
					subText = "%s x%d (%d/%d)" % (subItemName, subData["count"], subData["count"], subData["count"])
				else:
					subText = "%s x%d" % (subItemName, subData["count"])
				self.__AddTextLine(subText, detailColor, OVERVIEW_SUB_TEXT_X, OVERVIEW_SUB_TEXT_Y)

			# Reward item slot (right)
			rewardVnum = 0
			if subData and subData.get("reward_item"):
				rewardVnum = subData["reward_item"]
			if rewardVnum:
				rewardSlot = self.__CreateSlot(OVERVIEW_SLOT_RIGHT_X, OVERVIEW_SLOT_RIGHT_Y)
				rewardSlot.SetItemSlot(0, rewardVnum, 0)
				if toolTip:
					rewardSlot.SetOverInItemEvent(lambda slotNum, vnum=rewardVnum, tt=toolTip: self.__OnOverInItem(vnum, tt))
					rewardSlot.SetOverOutItemEvent(lambda: self.__OnOverOutItem(toolTip))
				self.slots.append(rewardSlot)

			# Effects (first 3 vertical, 4th/5th horizontal next to 1st/2nd)
			if mainData.get("bonuses") and toolTip:
				effectLines = []
				for bType, bValue in mainData["bonuses"]:
					bStr = toolTip.GetAffectBiologString(bType, bValue)
					if bStr and bStr != "-":
						effectLines.append(bStr)

				for i, bStr in enumerate(effectLines):
					if i < 3:
						y = OVERVIEW_EFFECTS_START_Y + i * OVERVIEW_EFFECTS_LINE_HEIGHT
						self.__AddTextLine(bStr, OVERVIEW_COLOR_EFFECT_TEXT, OVERVIEW_EFFECTS_X, y)
					else:
						row = i - 3
						y = OVERVIEW_EFFECTS_START_Y + row * OVERVIEW_EFFECTS_LINE_HEIGHT
						self.__AddTextLine(bStr, OVERVIEW_COLOR_EFFECT_TEXT, OVERVIEW_EFFECTS_X2, y)

			# Status overlays (render on top, non-interactive so tooltips still work)
			if locked:
				self.statusOverlay = ui.ImageBox()
				self.statusOverlay.SetParent(self)
				self.statusOverlay.LoadImage(OVERVIEW_CARD_LOCKED_IMAGE)
				self.statusOverlay.SetPosition(0, 15)
				self.statusOverlay.AddFlag("not_pick")
				self.statusOverlay.Show()
			elif completed:
				self.statusOverlay = ui.ImageBox()
				self.statusOverlay.SetParent(self)
				self.statusOverlay.LoadImage(OVERVIEW_CARD_DONE_IMAGE)
				self.statusOverlay.SetPosition(0, 15)
				self.statusOverlay.AddFlag("not_pick")
				self.statusOverlay.Show()

			self.Show()

		def __CreateSlot(self, x, y):
			slot = ui.SlotWindow()
			slot.SetParent(self)
			slot.SetPosition(x, y)
			slot.SetSize(OVERVIEW_SLOT_SIZE, OVERVIEW_SLOT_SIZE)
			slot.AppendSlot(0, 0, 0, OVERVIEW_SLOT_SIZE, OVERVIEW_SLOT_SIZE)
			slot.Show()
			return slot

		def __OnOverInItem(self, vnum, toolTip):
			if toolTip:
				toolTip.ClearToolTip()
				toolTip.AddItemData(vnum, metinSlot=(0, 0, 0, 0, 0, 0))

		def __OnOverOutItem(self, toolTip):
			if toolTip:
				toolTip.HideToolTip()

		def __AddTextLine(self, text, color, x, y):
			textLine = ui.TextLine()
			textLine.SetParent(self)
			if localeinfo.IsARABIC():
				textLine.SetWindowHorizontalAlignRight()
			textLine.SetPosition(x, y)
			textLine.SetText(text)
			textLine.SetPackedFontColor(color)
			textLine.Show()
			self.textLines.append(textLine)

		def __del__(self):
			ui.ListBoxEx.Item.__del__(self)

		def OnMouseLeftButtonDown(self):
			pass

		def OnRender(self):
			pass
	# <<< DEPRECATED SECTION END <<<

	class MissionRowItem(ui.ListBoxEx.Item):
		# Compact single-line table row for the overview / history tab.
		# The row itself is the pick target (all children are "not_pick"), so hovering
		# anywhere on it shows the mission tooltip. No self-capturing lambdas -> no leak.
		def __init__(self, parent, group, state, activeVnum, given, required, owner, rowIndex):
			ui.ListBoxEx.Item.__init__(self)
			ui.ListBoxEx.Item.SetParent(self, parent)
			self.parent = proxy(parent)

			self.group = group
			self.state = state                 # "done" | "current" | "locked"
			self.owner = owner                 # proxy(BiologManager) - drives the hover panel
			self.arabic = localeinfo.IsARABIC()
			self.widgets = []                  # keep child refs alive
			self.progressText = None           # updated in place while farming
			self.activeName = ""

			self.__Build(activeVnum, given, required, rowIndex)
			self.Show()

		def __del__(self):
			ui.ListBoxEx.Item.__del__(self)

		# Mirror a left-to-right x into RTL space when the client is Arabic.
		def _X(self, x, w):
			if self.arabic:
				return ROW_WIDTH - x - w
			return x

		def __MakeBar(self, x, y, w, h, color):
			bar = ui.Bar()
			bar.SetParent(self)
			bar.SetPosition(self._X(x, w), y)
			bar.SetSize(w, h)
			bar.SetColor(color)
			bar.AddFlag("not_pick")
			bar.Show()
			self.widgets.append(bar)
			return bar

		def __MakeIcon(self, vnum, x):
			icon = ui.ExpandedImageBox()
			icon.SetParent(self)
			item.SelectItem(vnum)
			icon.LoadImage(item.GetIconImageFileName())
			# Full-size (native) icon - do not scale.
			icon.SetPosition(self._X(x, ROW_ICON_SIZE), ROW_ICON_Y)
			icon.AddFlag("not_pick")
			icon.Show()
			self.widgets.append(icon)
			return icon

		def __MakeText(self, text, color, x):
			# Arabic convention (same as ui.Table): keep align-LEFT and anchor at the
			# column's right edge - Arabic glyphs then flow leftward from that anchor.
			t = ui.MakeTextLineColor(self, 0, ROW_TEXT_Y, text, color)
			t.SetHorizontalAlignLeft()
			if self.arabic:
				t.SetPosition(ROW_WIDTH - x, ROW_TEXT_Y)
			else:
				t.SetPosition(x, ROW_TEXT_Y)
			t.AddFlag("not_pick")
			self.widgets.append(t)
			return t

		def __Build(self, activeVnum, given, required, rowIndex):
			if self.state == "done":
				railColor = OVERVIEW_COLOR_COMPLETED_HEADER
				textColor = OVERVIEW_COLOR_COMPLETED_TEXT
			elif self.state == "current":
				railColor = OVERVIEW_COLOR_CURRENT_HEADER
				textColor = OVERVIEW_COLOR_CURRENT_TEXT
			else:
				railColor = OVERVIEW_COLOR_LOCKED_TEXT
				textColor = OVERVIEW_COLOR_LOCKED_TEXT

			# Row background: highlight the active mission, zebra-stripe the rest.
			if self.state == "current":
				self.__MakeBar(ROW_RAIL_W, 0, ROW_WIDTH - ROW_RAIL_W, ROW_HEIGHT, ROW_BG_CURRENT)
			elif rowIndex % 2 == 1:
				self.__MakeBar(ROW_RAIL_W, 0, ROW_WIDTH - ROW_RAIL_W, ROW_HEIGHT, ROW_BG_ODD)

			# Status rail on the leading edge.
			self.__MakeBar(0, 0, ROW_RAIL_W, ROW_HEIGHT, railColor)

			group = self.group
			mainData = group["main"]

			# Level.
			self.__MakeText("Lv. %d" % group["level"], textColor, ROW_LV_X)

			# Mission icon: the active step's item while current, otherwise the main item.
			iconVnum = activeVnum if (self.state == "current" and activeVnum) else mainData["item"]
			self.__MakeIcon(iconVnum, ROW_MAIN_ICON_X)

			# Name + progress / status.
			if self.state == "current" and activeVnum:
				item.SelectItem(activeVnum)
				self.activeName = item.GetItemName()
				label = "%s  %d/%d" % (self.activeName, given, required)
			elif self.state == "done":
				item.SelectItem(mainData["item"])
				label = "%s  %s" % (item.GetItemName(), getattr(localeinfo, "BIOLOG_OVERVIEW_DONE", "Done"))
			else:
				item.SelectItem(mainData["item"])
				label = "%s  x%d" % (item.GetItemName(), mainData["count"])
			self.progressText = self.__MakeText(label, textColor, ROW_TEXT_X)

		def UpdateProgress(self, given, required):
			# In-place text update for the active row (avoids a full rebuild while farming).
			if self.state == "current" and self.progressText:
				self.progressText.SetText("%s  %d/%d" % (self.activeName, given, required))

		def OnMouseOverIn(self):
			if self.owner:
				self.owner.ShowBonusTable(self.group, self)

		def OnMouseOverOut(self):
			if self.owner:
				self.owner.HideBonusTable()

		def OnMouseLeftButtonDown(self):
			pass

		def OnRender(self):
			pass

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__Initialize()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.ClearDictionary()
		self.__Initialize()

	def __Initialize(self):
		# Instance vars must be set BEFORE __LoadWindow: __BindEvents creates the tab
		# RadioButtonGroup, whose Create() immediately fires OnClick(0) -> __OnTabCurrent,
		# which touches self.bonusPanel / overview state before load finishes.
		self.ToolTip = None
		self.wndWiki = None
		self.overviewSignature = None
		self.overviewRows = []
		self.overviewCurrentRow = None
		self.overviewHeaderBuilt = False
		self.overviewHeaderWidgets = []
		self.bonusPanel = None
		self.__LoadWindow()
		TEXT_OBJECTS = {}
		CHECKBOX_OBJECTS = {}
		BUTTON_OBJECTS = {}

	def __LoadWindow(self):
		try:
			ui.PythonScriptLoader().LoadScriptFile(self, "uiscript/BiologManagerWindow.py")

		except KeyError, msg:
			dbg.TraceError("BiologManager #1")

		try:
			self.__BindObjects()

		except KeyError, msg:
			dbg.TraceError("BiologManager #2 - %s" % str(msg))

		try:
			self.__BindEvents()
		
		except KeyError, msg:
			dbg.TraceError("BiologManager #3 - %s" % str(msg))
	
	def __BindObjects(self):
		GetObject = self.GetChild

		self.TEXT_OBJECTS["BiologLevelinfo"] = [GetObject("BiologRequiredLevel"), 0]
		self.TEXT_OBJECTS["BiologItemInfo"] = [GetObject("BiologItemInfo"), 0]
		self.TEXT_OBJECTS["BiologCooldownInfo"] = [GetObject("BiologCooldownInfo"), 0]
		self.TEXT_OBJECTS["BiologTitle"] = [GetObject("TitleName"), 0]

		self.CHECKBOX_OBJECTS["CheckBoxReminder"] = GetObject("CheckBoxReminder")
		self.CHECKBOX_OBJECTS["AdditionalCheckboxes"] = [GetObject("AdditionalCheckbox_%d" % (i)) for i in xrange(BIOLOG_ADDITIONAL_COUNT)]

		self.main = {
			"seon_image" : GetObject("SeonImage"),

			"board" : GetObject("TitleBar"),
			"item_required" : GetObject("BiologRequiredItem"),

			"additional_items" : [GetObject("AdditionalItem_%d" % (i)) for i in xrange(BIOLOG_ADDITIONAL_COUNT)],

			"biolog_reward_item" : GetObject("BiologRewardItem"),

			"reward_storage" : GetObject("RewardsStorage"),

			"biolog_submit_mission" : GetObject("SubmitMissionButton"),
			"biolog_submit_sub_mission" : GetObject("SubmitSubMissionButton"),
			"biolog_shop_button" : GetObject("BiologShop"),

			"thinboard_main" : GetObject("ThinBoardMain"),
			"overview_board" : GetObject("OverviewBoard"),
			"overview_list" : GetObject("OverviewList"),
			"overview_scrollbar" : GetObject("OverviewScrollBar"),
			"tab_current" : GetObject("TabCurrent"),
			"tab_overview" : GetObject("TabOverview"),
		}

		# Connect scrollbar to overview list
		self.main["overview_list"].SetScrollBar(self.main["overview_scrollbar"])

		# Hide overview by default
		self.main["overview_board"].Hide()

		# Create delivery gauge fill (dynamic, clips based on progress)
		self.deliveryGaugeFill = ui.ExpandedImageBox()
		self.deliveryGaugeFill.SetParent(self.main["thinboard_main"])
		self.deliveryGaugeFill.LoadImage(DELIVERY_GAUGE_FILL_IMAGE)
		self.deliveryGaugeFill.SetPosition(DELIVERY_GAUGE_FILL_X, DELIVERY_GAUGE_FILL_Y)
		self.deliveryGaugeFill.SetRenderingRect(-1.0, 0, 0, 0)
		self.deliveryGaugeFill.Show()

		# Create cooldown gauge fill (dynamic, fills empty->full as cooldown expires)
		self.cooldownGaugeFill = ui.ExpandedImageBox()
		self.cooldownGaugeFill.SetParent(self.main["thinboard_main"])
		self.cooldownGaugeFill.LoadImage(COOLDOWN_GAUGE_FILL_IMAGE)
		self.cooldownGaugeFill.SetPosition(COOLDOWN_GAUGE_FILL_X, COOLDOWN_GAUGE_FILL_Y)
		self.cooldownGaugeFill.SetRenderingRect(-1.0, 0, 0, 0)
		self.cooldownGaugeFill.Show()
		self.cooldownEndTime = 0
		self.cooldownTotalTime = 0
		self.hoverPulseActive = False

	def __BindEvents(self):
		GetObject = self.GetChild
		wnd = self.main

		wnd["board"].SetCloseEvent(ui.__mem_func__(self.Close))

		self.CHECKBOX_OBJECTS["CheckBoxReminder"].SetEvent(self.__selectCooldownCheckBox)

		wnd["biolog_submit_mission"].SetEvent(self.__submitPacket)
		wnd["biolog_submit_sub_mission"].SetEvent(self.__submitPacket)
		wnd["biolog_shop_button"].SetEvent(self.OpenShop)

		# Tab group
		self.tabGroup = ui.RadioButtonGroup.Create([
			(wnd["tab_current"], ui.__mem_func__(self.__OnTabCurrent), None),
			(wnd["tab_overview"], ui.__mem_func__(self.__OnTabOverview), None),
		])

	def __OnTabCurrent(self, idx):
		self.HideBonusTable()
		self.main["overview_board"].Hide()
		self.main["thinboard_main"].Show()

	def __OnTabOverview(self, idx):
		self.main["thinboard_main"].Hide()
		self.main["overview_board"].Show()
		self.__RenderOverview()

	def __BuildOverviewHeader(self):
		if self.overviewHeaderBuilt:
			return
		board = self.main["overview_board"]
		arabic = localeinfo.IsARABIC()

		# ListBoxEx shifts Arabic rows by (listWidth - itemWidth - 10) = -10 (both 312);
		# match that so the header + separator sit exactly over the row columns.
		rowOriginX = OV_LIST_X + (-10 if arabic else 0)

		def mkLabel(colX, text):
			# Same RTL rule as the rows: align-left, anchor at the column's right edge.
			t = ui.MakeTextLineColor(board, 0, OV_HEADER_Y, text, OV_HEADER_COLOR)
			t.SetHorizontalAlignLeft()
			if arabic:
				t.SetPosition(rowOriginX + (ROW_WIDTH - colX), OV_HEADER_Y)
			else:
				t.SetPosition(rowOriginX + colX, OV_HEADER_Y)
			t.AddFlag("not_pick")
			t.Show()
			self.overviewHeaderWidgets.append(t)

		mkLabel(ROW_LV_X, getattr(localeinfo, "BIOLOG_OVERVIEW_COL_LEVEL", "Lv."))
		mkLabel(ROW_TEXT_X, getattr(localeinfo, "BIOLOG_OVERVIEW_COL_MISSION", "Mission"))

		sep = ui.Bar()
		sep.SetParent(board)
		sep.SetPosition(rowOriginX, OV_HEADER_SEP_Y)
		sep.SetSize(ROW_WIDTH, 1)
		sep.SetColor(OV_HEADER_SEP_COLOR)
		sep.AddFlag("not_pick")
		sep.Show()
		self.overviewHeaderWidgets.append(sep)

		self.overviewHeaderBuilt = True

	def __RenderOverview(self):
		currentItem = biologmgr.GetInfoItem()[0]
		currentMissionId = BIOLOG_ITEM_TO_MISSION.get(currentItem, 99)
		givenItems, requiredItems = biologmgr.GetInfoCount()
		signature = (currentMissionId, givenItems, requiredItems)

		# Fast path: same mission, only progress moved -> update the active row in place.
		if self.overviewSignature is not None and self.overviewRows:
			if self.overviewSignature[0] == currentMissionId:
				if self.overviewSignature != signature and self.overviewCurrentRow:
					self.overviewCurrentRow.UpdateProgress(givenItems, requiredItems)
				self.overviewSignature = signature
				return

		# Full rebuild: first open or the active mission changed.
		self.overviewSignature = signature
		self.__BuildOverviewHeader()

		listbox = self.main["overview_list"]
		listbox.RemoveAllItems()
		self.overviewRows = []
		self.overviewCurrentRow = None

		rowIndex = 0
		for group in BIOLOG_MISSION_GROUPS:
			mainId = group["main"]["id"]
			subData = group.get("sub")
			subId = subData["id"] if subData else None

			if subId is not None:
				completed = currentMissionId > subId
				activeMain = currentMissionId == mainId
				activeSub = currentMissionId == subId
			else:
				completed = currentMissionId > mainId
				activeMain = currentMissionId == mainId
				activeSub = False

			if completed:
				state = "done"
			elif activeMain or activeSub:
				state = "current"
			else:
				state = "locked"

			if activeMain:
				activeVnum = group["main"]["item"]
			elif activeSub:
				activeVnum = subData["item"]
			else:
				activeVnum = 0

			row = self.MissionRowItem(
				listbox, group, state, activeVnum,
				givenItems, requiredItems, proxy(self), rowIndex
			)
			listbox.AppendItem(row)
			self.overviewRows.append(row)
			if state == "current":
				self.overviewCurrentRow = row
			rowIndex += 1

		listbox.UpdateScrollBarSize()

	def __SplitAffect(self, full, bValue):
		# Locale formats are not consistent: "Name +%d%%" (monster), "+%d%% name"
		# (metin stone), "Name: %d%%" (resists). Cut the value token out wherever it
		# sits; whatever remains is the effect name. Never yields an empty name.
		valueStr = ""
		name = full
		for token in ("+%d%%" % bValue, "%d%%" % bValue, "+%d" % bValue, "%d" % bValue):
			pos = full.find(token)
			if pos >= 0:
				name = full[:pos] + full[pos + len(token):]
				valueStr = ("+%d%%" % bValue) if token.endswith("%") else ("+%d" % bValue)
				break
		name = name.strip(" \t+:")
		if not name:
			name = full
		if not valueStr:
			valueStr = str(bValue)
		return (name, valueStr)

	def __BuildBonusRows(self, group):
		rows = []
		bonuses = group["main"].get("bonuses")
		if not (self.ToolTip and bonuses):
			return rows
		for bType, bValue in bonuses:
			full = self.ToolTip.GetAffectBiologString(bType, bValue)
			if not full or full == "-":
				continue
			rows.append(self.__SplitAffect(full, bValue))
		return rows

	def ShowBonusTable(self, group, row):
		rows = self.__BuildBonusRows(group)
		if not rows:
			self.HideBonusTable()
			return
		if self.bonusPanel is None:
			self.bonusPanel = BonusTablePanel()

		item.SelectItem(group["main"]["item"])
		self.bonusPanel.Fill(item.GetItemName(), rows)

		winX, winY = self.GetGlobalPosition()
		rowX, rowY = row.GetGlobalPosition()
		panelW = self.bonusPanel.GetWidth()
		if localeinfo.IsARABIC():
			panelX = winX - panelW - 2
			if panelX < 0:
				panelX = winX + self.GetWidth() + 2
		else:
			panelX = winX + self.GetWidth() + 2
		self.bonusPanel.ShowAt(panelX, rowY)

	def HideBonusTable(self):
		if self.bonusPanel:
			self.bonusPanel.Hide()

	def __OpenBiologQuest(self):
		self.Close()
		net.SendRequestEventQuest("biolog_manager")

	def __CreateGameTypeToolTip(self, title, descList):
		import uiToolTip
		toolTip = uiToolTip.ToolTip()
		toolTip.SetTitle(title)
		toolTip.AppendSpace(7)

		for desc in descList:
			toolTip.AutoAppendTextLine(desc)

		toolTip.AlignHorizonalCenter()
		toolTip.SetTop()
		return toolTip

	def Open(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "BIOLOG")
		self.tabGroup.OnClick(0)
		self.RecvUpdate()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def _GetAdditionalItems(self):
		currentItem = biologmgr.GetInfoItem()[0]
		missionId = BIOLOG_ITEM_TO_MISSION.get(currentItem, 0)
		if missionId >= NEW_MISSION_THRESHOLD:
			return BIOLOG_ADDITIONAL_ITEMS_NEW
		return BIOLOG_ADDITIONAL_ITEMS_DEFAULT

	def RecvUpdate(self):
		wnd = self.main

		biologLevel = biologmgr.GetInfoLevel()
		biologItem,biologItemCount = biologmgr.GetInfoItem()
		if biologItem in (31065,31066):
			data = localeinfo.BIOLOG_ZODIAC_MANAGER_REQUIRED_LEVEL + " |cFF{}Lv.{} ".format("F1C40F" if player.GetStatus(player.LEVEL) >= biologLevel else "E30505", biologLevel)
			wnd["seon_image"].Show()
		else:
			data = localeinfo.BIOLOG_MANAGER_REQUIRED_LEVEL + " |cFF{}Lv.{} ".format("05E310" if player.GetStatus(player.LEVEL) >= biologLevel else "E30505", biologLevel)
			wnd["seon_image"].Hide()


		self.UpdateElement("BiologLevelinfo", data)

		additionalItems = self._GetAdditionalItems()
		for i in xrange(BIOLOG_ADDITIONAL_COUNT):
			additionalItemCount = player.GetItemCountByVnum(additionalItems[i])
			item.SelectItem(additionalItems[i])
			wnd["additional_items"][i].SetItemSlot(0, additionalItems[i], additionalItemCount)
			if additionalItemCount:
				wnd["additional_items"][i].EnableSlot(0)
			else:
				wnd["additional_items"][i].DisableSlot(0)
			wnd["additional_items"][i].SetOverInItemEvent(self.__MakeAdditionalOverIn(i))
			wnd["additional_items"][i].SetOverOutItemEvent(ui.__mem_func__(self.OnOverOutItem))
			wnd["additional_items"][i].SetSelectItemSlotEvent(self.__MakeAdditionalClick(i))
			wnd["additional_items"][i].RefreshSlot()

		biologGiven, biologRequired = biologmgr.GetInfoCount()

		biologItemGiven = biologGiven
		biologItemRequired = biologRequired
		item_count = player.GetItemCountByVnum(biologItem)
		item.SelectItem(biologItem)

		wnd["item_required"].SetItemSlot(0, biologItem, item_count)
		if item_count:
			wnd["item_required"].EnableSlot(0)
		else:
			wnd["item_required"].DisableSlot(0)
		wnd["item_required"].SetOverInItemEvent(ui.__mem_func__(self.OnOverInItem))
		wnd["item_required"].SetOverOutItemEvent(ui.__mem_func__(self.OnOverOutItem))
		wnd["item_required"].SetSelectItemSlotEvent(ui.__mem_func__(self.OnSelectItemSlot))
		wnd["item_required"].RefreshSlot()

		# Count text (simplified for gauge UI) - update BEFORE gauge code
		data = "%d/%d" % (biologItemRequired, biologItemGiven) #(biologItemGiven, biologItemRequired)
		self.UpdateElement("BiologItemInfo", data)

		# Update delivery gauge fill
		if biologItemRequired > 0:
			gaugePercent = float(biologItemGiven) / float(biologItemRequired)
		else:
			gaugePercent = 0.0
		self.deliveryGaugeFill.SetRenderingRect(-(1.0 - gaugePercent), 0, 0, 0)

		GCooldown, Cooldown = biologmgr.GetInfoCooldown()
		self.cooldownEndTime = app.GetTime() + Cooldown
		self.cooldownTotalTime = GCooldown
		self.UpdateElement("BiologCooldownInfo", self.cooldownEndTime)

		biologReminder = biologmgr.GetInfoReminder()
		self.CHECKBOX_OBJECTS["CheckBoxReminder"].SetChecked(True if biologReminder else False)

		if biologmgr.GetNpcVnum() == SEON_PYEONG:
			self.TEXT_OBJECTS["BiologTitle"][0].SetText(localeinfo.BIOLOG_MANAGER_TITLE2)
		else:
			self.TEXT_OBJECTS["BiologTitle"][0].SetText(localeinfo.BIOLOG_MANAGER_TITLE)
		wnd["biolog_reward_item"].Show()
		iItem, iItemCount = biologmgr.GetInfoRewardItem()
		if ((iItem and iItemCount) != 0):
			wnd["biolog_reward_item"].SetItemSlot(0, iItem, iItemCount)
			wnd["biolog_reward_item"].SetOverInItemEvent(lambda slotNumber, iVnum = iItem: self.OnOverInItem(slotNumber, iVnum))
			wnd["biolog_reward_item"].SetOverOutItemEvent(ui.__mem_func__(self.OnOverOutItem))
		else:
			wnd["biolog_reward_item"].ClearSlot(0)
			wnd["biolog_reward_item"].SetCoverButton(0, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, False, False)
			wnd["biolog_reward_item"].SetAlwaysRenderCoverButton(0)

		cooldownActive = Cooldown > 0
		canDeliver = item_count > 0 and not cooldownActive

		if biologGiven == biologRequired:
			wnd["biolog_submit_mission"].Hide()
			#wnd["biolog_submit_mission"].Disable()
			wnd["biolog_submit_mission"].DisableHoverPulse()
			wnd["biolog_submit_sub_mission"].Show()
			# if cooldownActive:
				# wnd["biolog_submit_sub_mission"].Disable()
			# else:
				# wnd["biolog_submit_sub_mission"].Enable()
		else:
			wnd["biolog_submit_mission"].Show()
			# if cooldownActive:
				# wnd["biolog_submit_mission"].Disable()
			# else:
				# wnd["biolog_submit_mission"].Enable()
			wnd["biolog_submit_sub_mission"].Hide()
			#wnd["biolog_submit_sub_mission"].Disable()
			wnd["biolog_submit_sub_mission"].DisableHoverPulse()

		if canDeliver:
			activeBtn = wnd["biolog_submit_sub_mission"] if biologGiven == biologRequired else wnd["biolog_submit_mission"]
			if not self.hoverPulseActive:
				activeBtn.EnableHoverPulse()
				activeBtn.SetHoverPulseSpeed(1.5)
				self.hoverPulseActive = True
		else:
			if self.hoverPulseActive:
				wnd["biolog_submit_mission"].DisableHoverPulse()
				wnd["biolog_submit_sub_mission"].DisableHoverPulse()
				self.hoverPulseActive = False

		wnd["reward_storage"].RemoveAllItems()
		for i in range(biologmgr.BIOLOG_BONUS_LENGTH):
			rType, rValue = biologmgr.GetInfoRewardBonus(i)
			wnd["reward_storage"].AppendItem(self.ListBoxItem(wnd["reward_storage"], self.ToolTip.GetAffectBiologString(rType, rValue), 0xFFffeaa7, True))

		if self.main["overview_board"].IsShow():
			self.__RenderOverview()

	def UpdateElement(self, key, value):
		templ_tab = {"BiologLevelinfo" : "%s", "BiologItemInfo" : "%s", "BiologCooldownInfo" : "%s"}
		if key == "BiologCooldownInfo":
			if value > app.GetTime():
				self.TEXT_OBJECTS["BiologCooldownInfo"][1] = value
				self.TEXT_OBJECTS["BiologCooldownInfo"][0].SetText(templ_tab[key] % localeinfo.SecondToHMS(self.TEXT_OBJECTS["BiologCooldownInfo"][1] - app.GetTime()))
			else:
				self.TEXT_OBJECTS["BiologCooldownInfo"][0].SetText(localeinfo.BIOLOG_MANAGER_TIME_TEXT)
		else:
			if key in self.TEXT_OBJECTS:
				self.TEXT_OBJECTS[key][0].SetText(templ_tab[key] % value)
				self.TEXT_OBJECTS[key][1] = value

	def __selectCooldownCheckBox(self):
		wnd = self.CHECKBOX_OBJECTS["CheckBoxReminder"]
		biologmgr.SendPacketReminder(wnd.IsChecked())

	def __submitPacket(self):
		wnd = self.CHECKBOX_OBJECTS["AdditionalCheckboxes"]
		biologmgr.SendPacketItem(wnd[0].IsChecked(), wnd[1].IsChecked())


	def OpenShop(self):
		net.SendRemoteShopPacket(3)

	def SetItemToolTip(self, tooltip):
		self.ToolTip = tooltip

	def SetWikiWindow(self, wndWiki):
		self.wndWiki = wndWiki

	def __MakeAdditionalOverIn(self, pos):
		def handler(*args):
			additionalItems = self._GetAdditionalItems()
			itemVnum = additionalItems[pos]
			if self.ToolTip and itemVnum:
				self.ToolTip.ClearToolTip()
				self.ToolTip.AddItemData(itemVnum, metinSlot = (0, 0, 0, 0, 0, 0))
				if app.ENABLE_INGAME_WIKI and self.wndWiki:
					self.ToolTip.DeclareShortcut(("key_lclick",), getattr(localeinfo, "BIOLOG_MANAGER_CLICK_WIKI", "Click to open Wiki page"))
				self.ToolTip.AlignHorizonalCenter()
				self.ToolTip.ShowToolTip()
		return handler

	def __MakeAdditionalClick(self, pos):
		def handler(*args):
			if app.ENABLE_INGAME_WIKI and self.wndWiki:
				additionalItems = self._GetAdditionalItems()
				itemVnum = additionalItems[pos]
				if itemVnum:
					if not self.wndWiki.IsShow():
						net.ToggleWikiWindow()
					self.wndWiki.CloseBaseWindows()
					self.wndWiki.OpenSpecialPage(None, itemVnum, False)
		return handler

	def OnOverInItem(self, *args):
		iVnum = biologmgr.GetInfoItem()[0]
		if self.ToolTip and iVnum:
			self.ToolTip.ClearToolTip()
			self.ToolTip.AddItemData(iVnum, metinSlot = (0, 0, 0, 0, 0, 0))
			if app.ENABLE_INGAME_WIKI and self.wndWiki:
				self.ToolTip.DeclareShortcut(("key_lclick",), getattr(localeinfo, "BIOLOG_MANAGER_CLICK_WIKI", "Click to open Wiki page"))
			self.ToolTip.AlignHorizonalCenter()
			self.ToolTip.ShowToolTip()

	def OnSelectItemSlot(self, *args):
		if app.ENABLE_INGAME_WIKI and self.wndWiki:
			iVnum = biologmgr.GetInfoItem()[0]
			if iVnum:
				if not self.wndWiki.IsShow():
					net.ToggleWikiWindow()
				self.wndWiki.CloseBaseWindows()
				self.wndWiki.OpenSpecialPage(None, iVnum, False)

	def OnOverOutItem(self):
		if self.ToolTip:
			self.ToolTip.HideToolTip()

	def OnOverInRequiredItem(self, slotNumber, iVnum):
		if self.ToolTip:
			self.ToolTip.ClearToolTip()
			self.ToolTip.AddItemData(iVnum, 0)

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "BIOLOG")
		if self.ToolTip:
			self.ToolTip.HideToolTip()
		self.HideBonusTable()
		self.Hide()

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("BIOLOG", x, y)

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnUpdate(self):
		biologGiven, biologItemRequired = biologmgr.GetInfoCount()
		if (biologmgr.GetNpcVnum() == SEON_PYEONG) and (biologGiven == biologItemRequired):
			self.TEXT_OBJECTS["BiologCooldownInfo"][0].SetText(localeinfo.BIOLOG_MANAGER_TIME_SELECT)
		else:
			if self.TEXT_OBJECTS["BiologCooldownInfo"][1] >= app.GetTime():
				self.TEXT_OBJECTS["BiologCooldownInfo"][0].SetText(localeinfo.BIOLOG_MANAGER_TIME_WAIT + " " + localeinfo.SecondToHMS(self.TEXT_OBJECTS["BiologCooldownInfo"][1] - app.GetTime()))
			else:
				self.TEXT_OBJECTS["BiologCooldownInfo"][0].SetText(localeinfo.BIOLOG_MANAGER_TIME_TEXT)

		# Update cooldown gauge (fills empty->full as cooldown expires)
		if self.cooldownTotalTime > 0 and self.cooldownEndTime > app.GetTime():
			remaining = self.cooldownEndTime - app.GetTime()
			gaugePercent = 1.0 - (remaining / float(self.cooldownTotalTime))
			gaugePercent = max(0.0, min(1.0, gaugePercent))
		else:
			gaugePercent = 1.0
		self.cooldownGaugeFill.SetRenderingRect(-(1.0 - gaugePercent), 0, 0, 0)

		# Re-enable deliver button + pulse when cooldown expires (only on transition)
		biologItem = biologmgr.GetInfoItem()[0]
		hasItem = player.GetItemCountByVnum(biologItem) > 0
		canDeliver = gaugePercent >= 1.0 and hasItem

		if canDeliver:
			if biologGiven == biologItemRequired:
				self.main["biolog_submit_sub_mission"].Enable()
			else:
				self.main["biolog_submit_mission"].Enable()
			if not self.hoverPulseActive:
				activeBtn = self.main["biolog_submit_sub_mission"] if biologGiven == biologItemRequired else self.main["biolog_submit_mission"]
				activeBtn.EnableHoverPulse()
				activeBtn.SetHoverPulseSpeed(1.5)
				self.hoverPulseActive = True
		elif self.hoverPulseActive:
			self.main["biolog_submit_mission"].DisableHoverPulse()
			self.main["biolog_submit_sub_mission"].DisableHoverPulse()
			self.hoverPulseActive = False

		# Keep delivery gauge in sync (poll each frame)
		if biologItemRequired > 0:
			deliveryPercent = float(biologGiven) / float(biologItemRequired)
		else:
			deliveryPercent = 0.0
		self.deliveryGaugeFill.SetRenderingRect(-(1.0 - deliveryPercent), 0, 0, 0)
