# coding: latin_1

import app
import player

import item
import nonplayer
import ui
import wndMgr
import grp
import math
import wiki
import ingamewikiconfig
import ingamewikidungeon
import ingamewikibiolog
import ingamewikidragonsoul
import ingamewikigrowthpet
import ingamewikigrowthmount
import ingamewikigemshop
import ingamewikibuffi
import uitooltip
import types
import constinfo
import localeinfo
import uiscriptlocale
import dbg
import sys
import chat
import osfinfo
if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget
from _weakref import proxy
from operator import truediv

import systemSetting

import game_data
import net

# ShopEx stock rule, baked by 'wiki server to client/convert.py' as a 5th element
# on each shop item: [char_limit, restock_days]. Older baked files have no such
# element, so the length check is the version gate.
def AppendShopStockLine(toolTip, itemEntry):
	if not toolTip or len(itemEntry) < 5:
		return

	stock = itemEntry[4]
	if not stock or int(stock[0]) <= 0:
		return

	limit = int(stock[0])
	days = int(stock[1])
	if days < 0:
		toolTip.AppendTextLine(getattr(localeinfo, "SHOPEX_ONE_TIME", "One-time purchase"), 0xFF8EC6FF)
	elif days <= 1:
		toolTip.AppendTextLine(getattr(localeinfo, "SHOPEX_WIKI_STOCK_DAILY", "Stock: %d per day") % limit, 0xFF8EC6FF)
	else:
		toolTip.AppendTextLine(getattr(localeinfo, "SHOPEX_WIKI_STOCK_PERIOD", "Stock: %d per %d days") % (limit, days), 0xFF8EC6FF)

"""Static pages size values!
	Please dont touch on them."""
categoryPeakWindowSize = [109, 340]
mainBoardPos = [148, 106]
mainBoardSize = [555, 361]
monsterBonusInfoPageSize = [539, 157]
itemOriginPageSize = [351, 142]
chestItemOriginPageSize = [85, 58]


# ---------------------------------------------------------------------------
# GM Drop Editor — ack callback invoked by C++ (DropEditor_DispatchAckToPython
# in PythonWikiModule.cpp). Forwards to ingamewikieditor.RouteAck.
# Kept at module scope so PyObject_GetAttrString("OnDropEditorAckPyCb") works
# whether the wiki window is open or not.
# ---------------------------------------------------------------------------
def OnDropEditorAckPyCb(sub, file_kind, group_vnum, group_name, err_text, rows, _):
	try:
		import ingamewikieditor
		ingamewikieditor.RouteAck(sub, file_kind, group_vnum, group_name,
								  err_text, rows)
	except Exception:
		import traceback
		dbg.TraceError("OnDropEditorAckPyCb: " + traceback.format_exc())


# Trust-file gate for the GM Drop Editor. The "Edit drops" button only appears
# when this file exists in the client's game folder (the client's working
# directory). Ship the test client WITHOUT it and hand the file to trusted
# people separately -- its mere existence is the gate, the file can be empty.
# This is a button-visibility gate only; the server still enforces
# GM_IMPLEMENTOR on every drop-edit packet regardless.
DROP_EDITOR_KEY_FILE = "dropeditor.key"


def _DropEditor_IsAllowed():
	"""Gate for the GM Drop Editor: feature flag + the trust file + live GM
	status.

	The trust file (DROP_EDITOR_KEY_FILE) is how access is shared with only
	trusted people -- on a test server every character is a GM, so the GM check
	alone gates nothing; the file is the real visibility gate.

	This is safe to call from SpecialPageWindow.__init__ because the special
	page is only ever constructed on demand (clicking a monster's renderTarget
	or a chest icon) -- the player is in-game and their character instance
	exists by then. It must NOT be called at main-wiki build time: that runs
	inside GameWindow.Open() before the character spawns."""
	if not bool(getattr(app, "ENABLE_DROP_EDITOR", 0)):
		return False
	try:
		import os
		if not os.path.exists(DROP_EDITOR_KEY_FILE):
			return False
	except Exception:
		return False
	try:
		import chr
		return bool(chr.IsGameMaster(player.GetMainCharacterIndex()))
	except Exception:
		return False

def HAS_FLAG(value, flag):
	return (value & flag) == flag

def MakeMoneyText(money):
	money = str(money)
	(original, sLen, kLen) = (money, len(money), 3)

	while sLen > kLen and original[sLen-kLen:] == "000":
		money = money[::-1].replace("000"[::-1], "k"[::-1], 1)[::-1]
		original = original[:sLen - kLen]
		sLen -= kLen

	return money


# Drop-chance tiers for the monster-drop hover tooltip. chance is in PPM
# (parts per million): 1,000,000 == 100%. Four tiers (locale words reused):
#   GUARANTEED (green)  >= 100%                 -> WIKI_DROP_TIER_GUARANTEED
#   MEDIUM     (cyan)   >= per-class Hard top   -> WIKI_DROP_TIER_RARE
#   HARD       (orange) >= per-class Hard floor -> WIKI_DROP_TIER_LEGENDARY
#   LOW        (purple) <  per-class Hard floor -> WIKI_DROP_TIER_EPIC
WIKI_DROP_TIER_COLOR_GUARANTEED = 0xFF66FF66
WIKI_DROP_TIER_COLOR_RARE       = 0xFF66CCFF
WIKI_DROP_TIER_COLOR_LEGENDARY  = 0xFFFFAA33
WIKI_DROP_TIER_COLOR_EPIC       = 0xFFCC66FF

# Source-class ids -- MUST match SRC_CLASS_* in tools/wiki_drop_baker/bake.py
# (shipped per mob in cl_mob_class.json -> game_data.mobClassDict).
SRC_CLASS_REGULAR   = 0
SRC_CLASS_STONE     = 1
SRC_CLASS_MINIBOSS  = 2
SRC_CLASS_BOSS      = 3
SRC_CLASS_WORLDBOSS = 4

# Per-class thresholds in PPM (1,000,000 == 100%): (HARD_floor, HARD_top).
# The SAME drop % reads rarer on a low-kill-volume source -- you break
# thousands of stones a day but kill very few bosses, so a 2.5% boss drop is
# much harder to obtain than 2.5% on a stone. Bands:
#     ppm >= 1,000,000  -> Guaranteed
#     ppm >= HARD_top   -> Medium
#     ppm >= HARD_floor -> Hard
#     else              -> Low
# Tunable live here (no rebake needed -- only mob classes are baked).
#   regular  : Hard  1-3%   (you kill the most -> most lenient)
#   stone    : Hard  5-10%
#   miniboss : Hard 10-20%
#   boss     : Hard 15-30%
#   worldboss: Hard 25-50%  (you kill the fewest -> strictest)
WIKI_DROP_TIER_GUARANTEED_PPM = 1000000
WIKI_DROP_TIER_THRESHOLDS = {
	SRC_CLASS_REGULAR:   ( 10000,  30000),
	SRC_CLASS_STONE:     ( 50000, 100000),
	SRC_CLASS_MINIBOSS:  (100000, 200000),
	SRC_CLASS_BOSS:      (150000, 300000),
	SRC_CLASS_WORLDBOSS: (250000, 500000),
}


def GetDropChanceTier(chance_ppm, src_class = SRC_CLASS_REGULAR):
	# Map a PPM drop chance + source class to (locale tier text, packed color).
	# Returns (None, 0) when chance is zero / negative so the caller can
	# decide whether to suppress the tag entirely.
	try:
		ppm = int(chance_ppm)
	except (TypeError, ValueError):
		return (None, 0)
	if ppm <= 0:
		return (None, 0)
	hard_floor, hard_top = WIKI_DROP_TIER_THRESHOLDS.get(
		src_class, WIKI_DROP_TIER_THRESHOLDS[SRC_CLASS_REGULAR])
	if ppm >= WIKI_DROP_TIER_GUARANTEED_PPM:
		return (localeinfo.WIKI_DROP_TIER_GUARANTEED, WIKI_DROP_TIER_COLOR_GUARANTEED)
	if ppm >= hard_top:
		return (localeinfo.WIKI_DROP_TIER_RARE, WIKI_DROP_TIER_COLOR_RARE)        # Medium
	if ppm >= hard_floor:
		return (localeinfo.WIKI_DROP_TIER_LEGENDARY, WIKI_DROP_TIER_COLOR_LEGENDARY)  # Hard
	return (localeinfo.WIKI_DROP_TIER_EPIC, WIKI_DROP_TIER_COLOR_EPIC)             # Low


def FormatDropPercent(chance_ppm):
	# ppm -> compact percent string (1,000,000 ppm == 100%). ~3 significant
	# figures, trailing zeros stripped:  1000000->"100%", 75000->"7.5%",
	# 50000->"5%", 250->"0.025%", 25->"0.0025%". Empty string when <= 0.
	try:
		ppm = int(chance_ppm)
	except (TypeError, ValueError):
		return ""
	if ppm <= 0:
		return ""
	pct = ppm / 10000.0
	if pct >= 100.0:
		return "100%"
	if pct >= 10.0:
		txt = "%.1f" % pct
	elif pct >= 1.0:
		txt = "%.2f" % pct
	elif pct >= 0.1:
		txt = "%.3f" % pct
	elif pct >= 0.01:
		txt = "%.4f" % pct
	else:
		txt = "%.5f" % pct
	txt = txt.rstrip("0").rstrip(".")
	return txt + "%"


def WikiViewerIsGM():
	# True when the local player is a game master. Gates the exact drop-rate
	# figure: GMs see "<tier> - <pct>", normal players see only "<tier>" so the
	# precise rates stay internal. (NOTE: the baked cl_mob_drop.json ships in the
	# client pack, so this is a UI gate, not hard secrecy -- see the baker.)
	try:
		import chr, player
		return bool(chr.IsGameMaster(player.GetMainCharacterIndex()))
	except Exception:
		return False


def FormatMoneyKK(n):
	# Compact money formatter:
	#   1500       -> "1.5k"
	#   100000     -> "100k"
	#   20000000   -> "20M"
	#   5500000    -> "5.5M"
	# Used wherever a money value has to fit a narrow column (mini cube
	# recipes, weapon refine table). MakeMoneyText above tops out at "k"
	# and renders 20M as "20000k", which is too wide.
	try:
		n = int(n)
	except (TypeError, ValueError):
		return "0"
	if n < 1000:
		return str(n)
	if n < 1000000:
		v = n / 1000.0
		return ("%dk" % int(v)) if v == int(v) else ("%.1fk" % v)
	if n < 1000000000:
		v = n / 1000000.0
		return ("%dM" % int(v)) if v == int(v) else ("%.1fM" % v)
	v = n / 1000000000.0
	return ("%dB" % int(v)) if v == int(v) else ("%.1fB" % v)

class WikiRenderTarget(ui.WikiRenderTarget):
	def __init__(self, width, height):
		self.moduleID = wiki.WIKI_RENDER_MODULE_DELETE
		
		ui.WikiRenderTarget.__init__(self)
		self.SetSize(width, height)
		
		self.ManageModelViewWindow(False)
	
	def __del__(self):
		self.ManageModelViewWindow(True)
		
		ui.WikiRenderTarget.__del__(self)

	def ManageModelViewWindow(self, deleteModule = False):
		if deleteModule:
			wiki.UnregisterModelViewWindow(self.moduleID, self.hWnd)
		else:
			self.moduleID = wiki.GetFreeModelViewID()
			wiki.RegisterModelViewWindow(self.moduleID, self.hWnd)

	def IsValidModuleID(self):
		if self.moduleID == wiki.WIKI_RENDER_MODULE_DELETE or\
			self.moduleID < wiki.WIKI_RENDER_MODULE_START:
			return False
		
		return True
	
	def SetModel(self, model_vnum, dungeoninfo = False, noBg = False):
		if self.IsValidModuleID():
			if not noBg:
				wiki.RenderTargetSetBackground(self.moduleID, "d:/ymir work/ui/game/myshop_deco/model_view_bg.sub")
			else :
				wiki.RenderTargetSetBackground(self.moduleID, "d:/ymir work/ui/dungeoninfo_rework/targetinfo.png")
			wiki.SetModelViewModel(self.moduleID, model_vnum, dungeoninfo)
	
	def SetWeaponModel(self, weapon_vnum):
		if self.IsValidModuleID():
			wiki.SetWeaponModel(self.moduleID, weapon_vnum)

	def SetModelShining(self, shining, vnum):
		if self.IsValidModuleID():
			wiki.SetShining(self.moduleID, shining, vnum)

	def SetModelForm(self, main_vnum):
		if self.IsValidModuleID():
			wiki.SetModelForm(self.moduleID, main_vnum)
	
	def SetModelHair(self, hair_vnum):
		if self.IsValidModuleID():
			wiki.SetModelHair(self.moduleID, hair_vnum)
			
	def SetModelSash(self, sash_vnum):
		if self.IsValidModuleID():
			wiki.SetModelSash(self.moduleID, sash_vnum)
	
	def SetModelV3Eye(self, x, y, z):
		if self.IsValidModuleID():
			wiki.SetModelV3Eye(self.moduleID, x, y, z)
	
	def SetModelV3Target(self, x, y, z):
		if self.IsValidModuleID():
			wiki.SetModelV3Target(self.moduleID, x, y, z)
	
	def Show(self):
		wndMgr.Show(self.hWnd)
		
		if self.IsValidModuleID():
			wiki.ManageModelViewVisibility(self.moduleID, True)
	
	def Hide(self):
		wndMgr.Hide(self.hWnd)
		
		if self.IsValidModuleID():
			wiki.ManageModelViewVisibility(self.moduleID, False)

class WikiScrollBar(ui.Window):
	BASE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
	CORNERS_AND_LINES_COLOR = grp.GenerateColor(0.3411, 0.3411, 0.3411, 1.0)
	
	BAR_NUMB = 9 #This is static value! Please dont touch in him.
	
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
		self.scrollSpeed = 1
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
		self.scrollEvent = ui.__mem_func__(func)
	
	def SetScrollSpeed(self, speed):
		self.scrollSpeed = speed
	
	def OnRunMouseWheel(self, length):
		if self.IsInPosition():
			if not self.horizontal_scroll:
				val = min(max(1, self.middleBar.GetLocalPosition()[1] - (length * 0.01) * self.scrollSpeed * self.sizeScale), self.GetHeight() - self.middleBar.GetHeight() - 1)
				self.middleBar.SetPosition(1, val)
			else:
				val = min(max(1, self.middleBar.GetLocalPosition()[0] - (length * 0.01) *  self.scrollSpeed * self.sizeScale), self.GetWidth() - self.middleBar.GetWidth() - 1)
				self.middleBar.SetPosition(val, 1)
			
			self.OnScrollMove()
			return True
		
		return False

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
		self.sizeScale = float(selfSize/fullSize)
		self.middleBar.SetSize(selfSize, fullSize)
	
	def SetStaticScale(self, r_size):
		self.middleBar.SetStaticScale(r_size)
	
	def SetPosScale(self, fScale):
		pos = (math.ceil((self.GetHeight() - 2 - self.middleBar.GetHeight()) * fScale) + 1) if not self.horizontal_scroll else\
				(math.ceil((self.GetWidth() - 2 - self.middleBar.GetWidth()) * fScale) + 1)
		
		self.SetPos(pos)
	
	def SetPos(self, pos):
		wPos = (1, pos) if not self.horizontal_scroll else (pos, 1)
		self.middleBar.SetPosition(*wPos)

class WikiBuildGrid(ui.ScriptWindow):
	"""Static values!
		Please dont touch on them."""
	GRID_WIDTH = 541
	AUTO_BUILD_GRID_COUNT = 3
	
	IMAGES_PATH = "d:/ymir work/ui/wiki/"
	AUTO_BUILD_GRID_IMAGES = [IMAGES_PATH + "detail_item_2.png", IMAGES_PATH + "detail_item.png"]
	
	def __init__(self, parent, size, flags):
		ui.ScriptWindow.__init__(self)
		self.SetWindowName("WikiGridWindow")
		
		self.SetParent(parent)
		for flag in flags:
			self.AddFlag(flag)
		
		self.grid_elements = []
		self.LoadBackgroundParent()
		self.LoadGrid(size)
	
	def __del__(self):
		ui.ScriptWindow.__del__(self)
	
	def LoadBackgroundParent(self):
		self.backgroundParent = ui.Window()
		self.backgroundParent.SetParent(self)
		self.backgroundParent.AddFlag("attach")
		self.backgroundParent.AddFlag("not_pick")
		self.backgroundParent.SetPosition(0, 0)
		self.backgroundParent.Show()
	
	def SetBackgroundGridSize(self, size):
		self.SetSize(*size)
		self.backgroundParent.SetSize(*size)
	
	def SetGridSize(self, new_size):
		self.LoadGrid(new_size)
	
	def CleanOldGrid(self):
		for grid in self.grid_elements:
			grid.Hide()
		
		del self.grid_elements[:]
	
	# def LoadGrid(self, size):
		# self.CleanOldGrid()
		
		# if size <= self.AUTO_BUILD_GRID_COUNT:
			# self.grid_elements.append(ui.ExpandedImageBox())
			# self.grid_elements[0].SetParent(self.backgroundParent)
			# self.grid_elements[0].AddFlag("attach")
			# self.grid_elements[0].AddFlag("not_pick")
			# self.grid_elements[0].LoadImage(self.AUTO_BUILD_GRID_IMAGES[abs(self.AUTO_BUILD_GRID_COUNT - size)])
			# self.grid_elements[0].SetPosition(0,0)
			# self.grid_elements[0].Show()
			
			# self_size = (self.GRID_WIDTH, self.grid_elements[0].GetHeight())
			# self.SetBackgroundGridSize(self_size)
		# else:
			# REFACT_COUNT = (size - self.AUTO_BUILD_GRID_COUNT)
			
			# self.grid_elements.append(ui.ExpandedImageBox())
			# self.grid_elements[0].SetParent(self.backgroundParent)
			# self.grid_elements[0].AddFlag("attach")
			# self.grid_elements[0].AddFlag("not_pick")
			# self.grid_elements[0].LoadImage(self.IMAGES_PATH + "grid/initial_grid.tga")
			# self.grid_elements[0].SetPosition(0,0)
			# self.grid_elements[0].Hide()
			
			# (main_grid_pos_x, main_grid_pos_y) = self.grid_elements[0].GetLocalPosition()
			# main_grid_height = self.grid_elements[0].GetHeight()
			# main_grid_final_pos = main_grid_height + main_grid_pos_y
			
			# for i in xrange(REFACT_COUNT):
				# tmpGrid = ui.ExpandedImageBox()
				# tmpGrid.SetParent(self.backgroundParent)
				# tmpGrid.AddFlag("attach")
				# tmpGrid.AddFlag("not_pick")
				# tmpGrid.LoadImage(self.IMAGES_PATH + "grid/grid_line.tga")
				# tmpGrid.SetPosition(main_grid_pos_x, main_grid_final_pos + (tmpGrid.GetHeight() * i))
				# tmpGrid.Hide()
				
				# self.grid_elements.append(tmpGrid)
			
			# (last_grid_pos_x, last_grid_pos_y) = self.grid_elements[-1].GetLocalPosition()
			# last_grid_height = self.grid_elements[-1].GetHeight()
			
			# self.grid_elements.append(ui.ExpandedImageBox())
			# self.grid_elements[-1].SetParent(self.backgroundParent)
			# self.grid_elements[-1].AddFlag("attach")
			# self.grid_elements[-1].AddFlag("not_pick")
			# self.grid_elements[-1].LoadImage(self.IMAGES_PATH + "grid/last_grid.tga")
			# self.grid_elements[-1].SetPosition(last_grid_pos_x, last_grid_pos_y + last_grid_height)
			# self.grid_elements[-1].Hide()
			
			# for grid in self.grid_elements:
				# grid.Show()

			# (last_grid_pos_x, last_grid_pos_y) = self.grid_elements[-1].GetLocalPosition()
			# last_grid_height = self.grid_elements[-1].GetHeight()
			
			# self_size = (self.GRID_WIDTH, last_grid_pos_y + last_grid_height)
			# self.SetBackgroundGridSize(self_size)

	def LoadGrid(self, size):
		self.CleanOldGrid()

		# Define grid image based on the size
		if size <= 2:
			grid_image = self.IMAGES_PATH + "detail_item.png"
		elif size == 3:
			grid_image = self.IMAGES_PATH + "detail_item_2.png"
		elif size >= 4 and size <= 8:
			grid_image = self.IMAGES_PATH + "detail_item%d.png" % size


		# Load the appropriate grid image
		grid_element = ui.ExpandedImageBox()
		grid_element.SetParent(self.backgroundParent)
		grid_element.AddFlag("attach")
		grid_element.AddFlag("not_pick")
		grid_element.LoadImage(grid_image)
		grid_element.SetPosition(0, 0)
		grid_element.Show()

		self.grid_elements.append(grid_element)

		# Update the background size to fit the grid
		self_size = (self.GRID_WIDTH, grid_element.GetHeight())
		self.SetBackgroundGridSize(self_size)


class SubCategObject(ui.Window):
	def __init__(self, text):#, mask_window = None):
		ui.Window.__init__(self)
		self.SetWindowName("SubCategObject_ListBoxEx_Item")
		
		self.mArgs = ()
		self.parent = None
		
		new_text = ""
		self.bannerFileName = None
		
		if type(text) == types.ListType:
			new_text = text[0]
			self.mArgs = text[1]
			if len(text) > 2:
				self.bannerFileName = text[2]
		
		self.textWindow = ui.Window()
		self.textWindow.SetParent(self)
		self.textWindow.AddFlag("attach")
		self.textWindow.AddFlag("not_pick")
		self.textWindow.SetPosition(2, 3)

		# if app.USE_CLIP_MASK:
			# self.textWindow.SetClippingMaskWindow(self)

		# if app.USE_CLIP_MASK:
			# self.mask_window = proxy(mask_window)

		self.textWindow.Show()

		self.textLine = ui.TextLine()
		self.textLine.AddFlag("attach")
		self.textLine.AddFlag("not_pick")
		self.textLine.SetParent(self.textWindow)
		if localeinfo.IsARABIC():
			#self.textLine.SetWindowHorizontalAlignCenter()
			self.textLine.SetWindowHorizontalAlignRight()
		self.textLine.SetText(new_text)
		self.textLine.Show()
		
		self.cutTextLine = ui.TextLine()
		self.cutTextLine.SetParent(self.textWindow)
		if localeinfo.IsARABIC():
			#self.cutTextLine.SetWindowHorizontalAlignCenter()
			self.cutTextLine.SetWindowHorizontalAlignRight()
		self.cutTextLine.SetText(new_text)
		self.cutTextLine.Hide()
		
		self.originText = new_text
		self.cutedText = new_text

	def SetSize(self, w, h):
		ui.Window.SetSize(self, w, h)
		self.textWindow.SetSize(w - 2, h - 3)
		
		self.cutedText = self.GetCutText()
	
	def SetParent(self, parent):
		self.parent = proxy(parent)
		
		ui.Window.SetParent(self, parent)
	
	def OnMouseLeftButtonDown(self):
		if self.parent:
			self.parent.SelectItem(self)
	
	def GetCutText(self):
		return self.originText
		# opop
		# (wL, wT, wR, wB) = self.cutTextLine.GetClippingMaskRect() if app.USE_CLIP_MASK else self.cutTextLine.GetRenderBox()
		# if wR > 0:
			# i = (len(self.originText) - 1)
			
			# while wR > 0:
				# self.cutTextLine.SetText(self.originText[:i])
				# (wL, wT, wR, wB) = self.cutTextLine.GetClippingMaskRect() if app.USE_CLIP_MASK else self.cutTextLine.GetRenderBox()
				# i -= 1
			
			# self.cutTextLine.SetText(self.originText[:i].strip() + "..")
			
			# (wL, wT, wR, wB) = self.cutTextLine.GetClippingMaskRect() if app.USE_CLIP_MASK else self.cutTextLine.GetRenderBox()
			# if wR > 0:
				# i -= 1
			
			# cut_text = (self.originText[:i] + "..")
			# self.cutTextLine.SetText(self.originText)
			# self.textLine.SetText(cut_text)
			
			# return cut_text
		
		# self.cutTextLine.SetText(self.originText)
		# self.textLine.SetText(self.originText)
		
		# return self.originText

	# opop
	# def OnUpdate(self):
		# (wL, wT, wR, wB) = self.cutTextLine.GetClippingMaskRect() if app.USE_CLIP_MASK else self.cutTextLine.GetRenderBox()
		# currX = self.textLine.GetLocalPosition()[0]

		# if self.IsInPosition():
			# if wR > 0:
				# if self.originText != self.textLine.GetText():
					# self.textLine.SetText(self.originText)

				# (wL, wT, wR, wB) = self.textLine.GetClippingMaskRect() if app.USE_CLIP_MASK else self.textLine.GetRenderBox()
				# if wR > 0:
					# self.textLine.SetPosition(currX - 1, 0)
		# elif currX < 0:
			# self.textLine.SetPosition(currX + 1, 0)
		# elif self.textLine.GetText() != self.cutedText:
			# self.textLine.SetText(self.cutedText)

	def OnRender(self):
		if self.parent.GetSelectedItem()==self:
			grp.SetColor(0xff40407a)#40407a
			self.OnSelectedRender()
		elif self.IsIn():#rgb(162, 155, 254) dream
			grp.SetColor(0xff706fd3)
			self.OnSelectedRender()

	def OnSelectedRender(self):
		x, y = self.GetGlobalPosition()
		wndMgr.RenderBarWithinMaskWindow(x, y, self.GetWidth(), self.GetHeight() - 2, self.hWnd)

class WikiCategory(ui.Window):
	"""Static values!
		Please dont touch on them."""
	TICK_COUNT = 6
	MIN_HEIGHT = 20
	ARROW_IMG = ["d:/ymir work/ui/wiki/arrow.tga", "d:/ymir work/ui/wiki/arrow_up.tga"]
	
	LINES_COLOR = grp.GenerateColor(0.2941, 0.2941, 0.2941, 1.0)
	CORNER_COLOR = grp.GenerateColor(0.2117, 0.2117, 0.2117, 1.0)
	BASE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
	
	def __init__(self, owner = None):
		ui.Window.__init__(self)
		
		self.owner = (None if not owner else proxy(owner))
		
		self.expectedSize = 0
		self.currHeight = self.MIN_HEIGHT
		
		self.isAnimating = False
		self.isOpening = False
		
		self.clickEvent = None
		
		self.titleImg = ui.ExpandedImageBox()
		self.titleImg.SetParent(self)
		self.titleImg.LoadImage("d:/ymir work/ui/wiki/category_new.png")
		self.titleImg.SetStringEvent("MOUSE_LEFT_DOWN",ui.__mem_func__( self.ClickExpand))
		self.titleImg.Show()
		
		self.titleText = ui.TextLine()
		self.titleText.SetParent(self)
		self.titleText.AddFlag("attach")
		self.titleText.AddFlag("not_pick")
		self.titleText.SetPosition(1, self.titleImg.GetHeight() / 2)
		#self.titleText.SetHorizontalAlignLeft()
		self.titleText.Show()
		
		self.arrow = ui.ExpandedImageBox()
		self.arrow.SetParent(self.titleImg)
		self.arrow.AddFlag("attach")
		self.arrow.AddFlag("not_pick")
		self.arrow.LoadImage(self.ARROW_IMG[0])
		self.arrow.SetPosition(95, self.titleImg.GetHeight() / 2 - self.arrow.GetHeight() / 2)
		self.arrow.Show()
		
		self.expandWnd = ui.Window()
		self.expandWnd.SetParent(self)
		self.expandWnd.AddFlag("attach")
		self.expandWnd.AddFlag("not_pick")
		self.expandWnd.SetPosition(0, self.titleImg.GetHeight())
		self.expandWnd.SetSize(self.titleImg.GetWidth(), 0)

		if not app.USE_CLIP_MASK:
			self.expandWnd.Show()

		self.bars = []
		for i in xrange(self.TICK_COUNT):
			br = ui.Bar()
			br.SetParent(self.expandWnd)
			br.AddFlag("attach")
			br.AddFlag("not_pick")
			br.SetColor([self.LINES_COLOR, self.CORNER_COLOR, self.BASE_COLOR][2 if i == (self.TICK_COUNT - 1) else int(i % 2 == 0)])
			br.Show()
			
			self.bars.append(br)
		
		self.categList = ui.ListBoxEx()
		self.categList.SetParent(self.expandWnd)
		self.categList.SetItemSize(self.titleImg.GetWidth() - 6 , 17+3)#here
		self.categList.SetItemStep(17)
		self.categList.SetSize(self.titleImg.GetWidth() - 6, self.MIN_HEIGHT - 1)
		self.categList.SetPosition(3+12, 1)
		self.categList.SetSelectEvent(ui.__mem_func__(self.OnSelectSubCategory))
		self.categList.Show()

		# if app.USE_CLIP_MASK:
			# self.categList.SetClippingMaskWindow(self.expandWnd)

		ui.Window.SetSize(self, self.titleImg.GetWidth(), self.titleImg.GetHeight())
		self.ArrangeBars(self.MIN_HEIGHT)

	def OnSelectSubCategory(self, elem):
		if self.owner:
			self.owner.NotifyCategorySelect(self)
		
		wikiClass = wiki.GetBaseClass()
		if wikiClass:
			if elem.bannerFileName:
				wikiClass.header.LoadImage(elem.bannerFileName)
				wikiClass.header.Show()
			else:
				wikiClass.header.Hide()
		
		if self.clickEvent:
			apply(self.clickEvent, elem.mArgs)
	
	def UnselectSubCategory(self):
		self.categList.SelectIndex(-1)
	
	def AddSubCategory(self, key, text):
		self.currHeight = (17 * (self.categList.GetItemCount() + 1) + 3)
		
		if self.expandWnd.GetHeight() > 0:
			self.ArrangeBars(self.currHeight)
			self.isAnimating = True
		
		self.categList.SetViewItemCount(self.categList.GetItemCount() + 1)

		# if app.USE_CLIP_MASK:
			# item = SubCategObject(text, self.expandWnd)
		# else:
		item = SubCategObject(text)
		self.categList.AppendItem(item)

		# if app.USE_CLIP_MASK:
			# item.SetClippingMaskWindow(self.categList)

		self.categList.SetSize(self.categList.GetWidth(), self.currHeight - 1)

	def ClickExpand(self):
		self.arrow.LoadImage(self.ARROW_IMG[(0 if self.isOpening else 1)])
		
		self.isOpening = not self.isOpening
		self.isAnimating = True
		
		self.expandWnd.Show()
		
		self.ArrangeBars(self.currHeight if self.isOpening else 0)
	
	def OnUpdate(self):
		if not self.isAnimating:
			return
		
		h = self.expandWnd.GetHeight()
		
		if h == self.expectedSize:
			self.isAnimating = False
			
			if h == 0:
				self.expandWnd.Hide()
			
			return
		
		step = (self.currHeight / self.TICK_COUNT)
		newSize = 0
		isOpening = (False if h > self.expectedSize else True)
		
		if isOpening:
			newSize = min(self.currHeight, self.expandWnd.GetHeight() + step)
		else:
			newSize = max(0, self.expandWnd.GetHeight() - step)
		
		change = newSize - self.expandWnd.GetHeight()
		
		self.expandWnd.SetSize(self.titleImg.GetWidth(), newSize)
		ui.Window.SetSize(self, self.titleImg.GetWidth(), self.titleImg.GetHeight() + newSize)
		self.owner.NotifySizeChange(self, change, (newSize > h))

	def SetSize(self, width, height):
		dbg.LogBox("WikiCategory -> SetSize - unsupported function")

	def ArrangeBars(self, currHeight):
		self.expectedSize = currHeight
		if currHeight < self.MIN_HEIGHT:
			return
		
		currWidth = self.expandWnd.GetWidth()
		
		self.bars[0].SetSize(1, (currHeight - 1))
		self.bars[1].SetSize(1, 1)
		self.bars[1].SetPosition(0, (currHeight - 1))
		self.bars[2].SetSize((currWidth - 2), 1)
		self.bars[2].SetPosition(1, (currHeight - 1))
		self.bars[3].SetSize(1, 1)
		self.bars[3].SetPosition((currWidth - 1), (currHeight - 1))
		self.bars[4].SetSize(1, (currHeight - 1))
		self.bars[4].SetPosition((currWidth - 1), 0)
		self.bars[5].SetSize((currWidth - 2), (currHeight - 1))
		self.bars[5].SetPosition(1, 0)
	
	def SetTitleName(self, text):
		self.titleText.SetText(text)
		
		pos_y = (self.titleImg.GetHeight() / 2 - self.titleText.GetTextSize()[1] / 2 - 1)
		self.titleText.SetPosition(5, pos_y)

	def SetTitleNameAe(self, text):
		self.titleText.SetText(text)
		self.titleText.SetHorizontalAlignLeft()
		pos_y = (self.titleImg.GetHeight() / 2 - self.titleText.GetTextSize()[1] / 2 - 1)
		self.titleText.SetPosition(80, pos_y-2)

class WikiCategories(ui.Window):
	"""Static values!
		Please dont touch on them."""
	CATEGORY_PADDING = 5
	SCROLL_SPEED = 17
	
	def __init__(self):
		ui.Window.__init__(self)
		
		self.SetSize(*categoryPeakWindowSize)

		if not app.USE_CLIP_MASK:
			self.SetInsideRender(True)

		self.scrollBar = None
		self.hideWindowsEvent = None
		self.elements = []

		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")

		if app.USE_CLIP_MASK:
			self.scrollBoard.SetClippingMaskWindow(self)

		self.scrollBoard.Show()

	def AddCategory(self, text):
		tmp = WikiCategory(self)
		tmp.SetParent(self.scrollBoard)
		if localeinfo.IsARABIC():
			tmp.SetTitleNameAe(text)
		else:
			tmp.SetTitleName(text)
		tmp.Show()
		
		addPadding = 0
		if len(self.elements) > 0:
			pos_y = (self.elements[-1].GetLocalPosition()[1] + self.elements[-1].GetHeight() + self.CATEGORY_PADDING)
			tmp.SetPosition(0, pos_y)
			
			addPadding = self.CATEGORY_PADDING
		
		(width, height) = (tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.scrollBoard.SetSize(width, height)
		
		self.elements.append(tmp)
		return tmp
	
	def NotifySizeChange(self, obj, amount, expanded):
		ind = len(self.elements)
		if obj in self.elements:
			ind = (self.elements.index(obj) + 1)
		
		if ind < len(self.elements):
			for i in xrange(ind, len(self.elements)):
				pos_y = (self.elements[(i - 1)].GetLocalPosition()[1] + self.elements[(i - 1)].GetHeight() + self.CATEGORY_PADDING)
				self.elements[i].SetPosition(0, pos_y)
		
		(width, height) = (self.scrollBoard.GetWidth(), (self.scrollBoard.GetHeight() + amount))
		self.scrollBoard.SetSize(width, height)
		self.UpdateScrollbar()

	def NotifyCategorySelect(self, obj):
		if self.hideWindowsEvent:
			self.hideWindowsEvent()

		for i in self.elements:
			if obj != proxy(i) and obj != i:
				i.UnselectSubCategory()

	def OnRunMouseWheel(self, length):
		if self.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True

		return False

	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - categoryPeakWindowSize[1]) * fScale * -1.0), -self.scrollBoard.GetHeight() + categoryPeakWindowSize[1]))
		self.scrollBoard.SetPosition(0, curr)

	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		scrollBoardHeight = self.scrollBoard.GetHeight()
		selfHeight = self.GetHeight()
		
		if scrollBoardHeight <= selfHeight:
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(selfHeight, scrollBoardHeight)
			
			new_pos = self.GetNewScrollBarPosition()
			if new_pos != 0:
				self.scrollBar.SetPos(new_pos)
			else:
				pos_scale = truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (scrollBoardHeight - selfHeight))
				self.scrollBar.SetPosScale(pos_scale)
			
			self.scrollBar.Show()

	def GetNewScrollBarPosition(self):
		if self.scrollBoard.GetLocalPosition()[1] >= 0:
			return 0
		
		out_perc = truediv(self.scrollBoard.GetLocalPosition()[1], self.scrollBoard.GetHeight())
		scroll_max_size = abs(self.GetHeight() * out_perc)
		return scroll_max_size

	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + categoryPeakWindowSize[1]))
		self.scrollBoard.SetPosition(0, curr)
		self.ChangeScrollbar()

	def RegisterScrollBar(self, scroll):
		self.scrollBar = proxy(scroll)
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.ChangeScrollbar()

class WikiMainWeaponWindow(ui.Window):
	class WikiItem(ui.Window):
		"""Static values!
			Please dont touch on them."""
		SCROLL_SPEED = 50
		
		TABLE_COLS = [
			[131,21,40,134],
			[172,21,40,134],
			[213,21,41,134],
			[255,21,40,134],
			[296,21,40,134],
			[337,21,41,134],
			[379,21,40,134],
			[420,21,40,134],
			[461,21,41,134],
			[503,21,36,134]
		]
		
		STARTING_MAT_COUNT = 2
		
		ROW_HEIGHTS = [21, 44, 51, 17]
		ROW_START_Y = [0, 22, 67, 119]
		
		ROW_HEIGHTS_EXPANDED = {}
		for idx in range(STARTING_MAT_COUNT + 1, wiki.REFINE_MATERIAL_MAX_NUM + 1):
			ROW_HEIGHTS_EXPANDED.update({idx : ([21, 44, 42, 22], [])})
			
			for insert_values in xrange(idx - STARTING_MAT_COUNT):
				ROW_HEIGHTS_EXPANDED[idx][0].insert((2 + insert_values), 47)
			
			for build_pos in xrange(len(ROW_HEIGHTS_EXPANDED[idx][0])):
				new_pos = 0
				for idx_pos in xrange(build_pos):
					new_pos += (ROW_HEIGHTS_EXPANDED[idx][0][idx_pos] + 1)
				
				ROW_HEIGHTS_EXPANDED[idx][1].append(new_pos)

		#if app.USE_EXTENDED_WIKI:
		def __init__(self, vnum, parent, allow_special_page = True, isUpgradable = True):
			ui.Window.__init__(self)
			
			self.parent = proxy(parent)
			
			wikiBase = wiki.GetBaseClass()
			if id(self) not in wikiBase.objList:
				wikiBase.objList[long(id(self))] = proxy(self)

			if app.USE_EXTENDED_WIKI:
				self.isUpgradable = isUpgradable

			self.scrollBoard = None
			self.scrollBar = None
			
			self.additionalLoaded = False
			self.vnum = vnum
			self.levelLimit = 0
			
			self.base = WikiBuildGrid(self, 2, ["attach", "not_pick"])
			self.base.Show()

			if app.USE_EXTENDED_WIKI and not self.isUpgradable:
				self.base.Hide()

			item.SelectItem(self.vnum)
			allow_increase_vnum = wiki.CanIncrRefineLevel()
			
			self.cols = []
			for (pos_x, pos_y, width, height) in self.TABLE_COLS:
				
				tmp = ui.Window()
				tmp.SetParent(self.base)
				tmp.AddFlag("attach")
				tmp.AddFlag("not_pick")
				tmp.SetPosition(pos_x, pos_y)
				tmp.SetSize(width, height)
				tmp.Show()
				
				tmp.titleWnd = ui.Window()
				tmp.titleWnd.SetParent(tmp)
				tmp.titleWnd.SetPosition(0, self.ROW_START_Y[0])
				tmp.titleWnd.SetSize(tmp.GetWidth(), self.ROW_HEIGHTS[0])
				tmp.titleWnd.SAFE_SetOverInEvent(self.parent.OnOverIn, self.vnum + (len(self.cols) if allow_increase_vnum else 0), 1)
				tmp.titleWnd.SAFE_SetOverOutEvent(self.parent.OnOverOut)
				tmp.titleWnd.SetMouseRightButtonUpEvent(ui.__mem_func__(self.parent.OnRightDown), self.vnum + (len(self.cols) if allow_increase_vnum else 0))# to do : make this SetMouseLeftButtonUpEvent
				if wiki.GetBaseClass() and allow_special_page:
					tmp.titleWnd.SetMouseLeftButtonDownEvent(ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), self.parent, self.vnum, False)
				# if wiki.GetBaseClass() and allow_special_page:
					# self.itemImage.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), self.parent, self.vnum, False)
			
				tmp.titleWnd.Show()
				
				tmp.refineText = ui.TextLine()
				tmp.refineText.SetParent(tmp.titleWnd)
				tmp.refineText.SetText("+" + str(len(self.cols)))
				if localeinfo.IsARABIC():
					tmp.refineText.SetHorizontalAlignRight()
					tmp.refineText.SetPosition(10, tmp.titleWnd.GetHeight() / 2 - tmp.refineText.GetTextSize()[1] / 2 - 1)
				else:
					tmp.refineText.SetPosition(tmp.titleWnd.GetWidth() / 2 - tmp.refineText.GetTextSize()[0] / 2, tmp.titleWnd.GetHeight() / 2 - tmp.refineText.GetTextSize()[1] / 2 - 1)
				tmp.refineText.Show()
				
				tmp.refineMat = []
				tmp.refineMatText = []
				tmp.refineMatNum = []

				for j in xrange(self.STARTING_MAT_COUNT):
					tmp.refineMat.append(ui.ExpandedImageBox())
					tmp.refineMat[j].SetParent(tmp)
					tmp.refineMat[j].Show()

					# Engine-rendered count (same digit sprites the inventory
					# uses). Hidden until a material vnum is bound to this
					# cell in ProcessRetInfo.
					tmp.refineMatNum.append(ui.NumberLine())
					tmp.refineMatNum[j].SetParent(tmp)
					tmp.refineMatNum[j].SetHorizontalAlignRight()
					tmp.refineMatNum[j].Hide()

					# "-" fallback shown only when this cell has no material.
					tmp.refineMatText.append(ui.TextLine())
					tmp.refineMatText[j].SetParent(tmp)
					tmp.refineMatText[j].SetText("-")
					tmp.refineMatText[j].SetPosition(tmp.GetWidth() / 2 - tmp.refineMatText[j].GetTextSize()[0] / 2, self.ROW_START_Y[(1 + j)] + self.ROW_HEIGHTS[(1 + j)] / 2 - tmp.refineMatText[j].GetTextSize()[1] / 2 - 1)
					tmp.refineMatText[j].Show()
				
				tmp.moneyText = ui.TextLine()
				tmp.moneyText.SetParent(tmp)
				tmp.moneyText.SetText("-")
				tmp.moneyText.SetPosition(tmp.GetWidth() / 2 - tmp.moneyText.GetTextSize()[0] / 2, self.ROW_START_Y[(self.STARTING_MAT_COUNT+1)] + self.ROW_HEIGHTS[(self.STARTING_MAT_COUNT+1)] / 2 - tmp.moneyText.GetTextSize()[1] / 2 - 1)
				tmp.moneyText.Show()
				
				self.cols.append(tmp)
			
			self.goldText = ui.TextLine()
			self.goldText.SetParent(self.base)
			self.goldText.SetText(localeinfo.WIKI_REFINEINFO_YANG_COSTS)
			if localeinfo.IsARABIC():
				self.goldText.SetHorizontalAlignRight()
				self.goldText.SetPosition(49 + 81 / 2 - self.goldText.GetTextSize()[0] / 2, 21 + self.ROW_START_Y[(self.STARTING_MAT_COUNT+1)] + self.ROW_HEIGHTS[(self.STARTING_MAT_COUNT+1)] / 2 - self.goldText.GetTextSize()[1] / 2 - 1 - 2)
			else:
				self.goldText.SetPosition(49 + 81 / 2 - self.goldText.GetTextSize()[0] / 2, 21 + self.ROW_START_Y[(self.STARTING_MAT_COUNT+1)] + self.ROW_HEIGHTS[(self.STARTING_MAT_COUNT+1)] / 2 - self.goldText.GetTextSize()[1] / 2 - 1)

			self.goldText.Show()
			
			self.upgradeText = ui.TextLine()
			self.upgradeText.SetParent(self.base)
			self.upgradeText.SetText(localeinfo.WIKI_REFINEINFO_UPGRADE_COSTS)
			if localeinfo.IsARABIC():
				self.upgradeText.SetPosition(49 + 81+35 / 2 - self.upgradeText.GetTextSize()[0] / 2, 21 + self.ROW_START_Y[0] + self.ROW_HEIGHTS[0] / 2 - self.upgradeText.GetTextSize()[1] / 2 - 1)
			else:
				self.upgradeText.SetPosition(49 + 81 / 2 - self.upgradeText.GetTextSize()[0] / 2, 21 + self.ROW_START_Y[0] + self.ROW_HEIGHTS[0] / 2 - self.upgradeText.GetTextSize()[1] / 2 - 1)
			self.upgradeText.Show()
			
			for i in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(i)
				if item.LIMIT_LEVEL == limitType:
					self.levelLimit = limitValue
					break
			
			self.levelText = ui.TextLine()
			self.levelText.SetParent(self.base)
			self.levelText.SetText(localeinfo.WIKI_REFINEINFO_ITEM_LEVEL % self.levelLimit)
			self.levelText.SetPackedFontColor(0xfffad390)
			self.levelText.SetPosition(self.base.GetWidth() - self.levelText.GetTextSize()[0] - 8, 1 + 19 / 2 - self.levelText.GetTextSize()[1] / 2)
			self.levelText.Show()
			
			itemName = item.GetItemName()
			fnd = itemName.find("+")
			if fnd >= 0:
				itemName = itemName[:fnd].strip()
			
			self.itemNameText = ui.TextLine()
			self.itemNameText.SetParent(self.base)
			self.itemNameText.SetText(itemName)
			if localeinfo.IsARABIC():
				self.itemNameText.SetPosition(130, 1 + 19 / 2 - self.itemNameText.GetTextSize()[1] / 2)
				self.itemNameText.SetHorizontalAlignLeft()
				self.itemNameText.SetPackedFontColor(0xfffad390)
			else:
				self.itemNameText.SetPosition(5, 1 + 19 / 2 - self.itemNameText.GetTextSize()[1] / 2)
			self.itemNameText.Show()
			
			self.itemImage = ui.ExpandedImageBox()
			self.itemImage.SetParent(self.base)
			self.itemImage.LoadImage(item.GetIconImageFileName())
			self.itemImage.SetPosition(1 + 47 / 2 - self.itemImage.GetWidth() / 2, 21 + 134 / 2 - self.itemImage.GetHeight() / 2)
			self.itemImage.Show()
			self.itemImage.SetStringEvent("MOUSE_OVER_IN",ui.__mem_func__(self.parent.OnOverIn), self.vnum + (9 if wiki.CanIncrRefineLevel() else 0), 0)
			self.itemImage.SetStringEvent("MOUSE_OVER_OUT",ui.__mem_func__(self.parent.OnOverOut))
			self.itemImage.SetMouseRightButtonUpEvent(ui.__mem_func__(self.parent.OnRightDown), self.vnum + (9 if wiki.CanIncrRefineLevel() else 0))# to do : make this SetMouseLeftButtonUpEvent
			# if wiki.GetBaseClass() and allow_special_page:
				# self.itemImage.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), self.parent, self.vnum, False)
			if wiki.GetBaseClass() and allow_special_page:
				self.itemImage.SetStringEvent("MOUSE_LEFT_DOWN",ui.__mem_func__(self._PageOpen),self.vnum,self.parent)

			self.SetSize(self.base.GetWidth(), self.base.GetHeight())
			
			self.scrollBoard = ui.Window()
			self.scrollBoard.SetParent(self)
			self.scrollBoard.AddFlag("attach")
			self.scrollBoard.AddFlag("not_pick")
			self.scrollBoard.Hide()
			
			self.RegisterHorizontalScrollBar()

		def _PageOpen(self,vnum,parent):#imhere
			if app.ENABLE_RENDER_TARGET and\
				app.IsPressed(app.DIK_LSHIFT):
					if uiRenderTarget.IsCanShowItems(vnum):
						# GetRefineInfo returns an empty tuple for anything non-refinable, so it can
						# only narrow the preview vnum here, never gate whether a preview happens
						previewVnum = vnum
						if wiki.CanIncrRefineLevel():
							(max_refine_count, retInfo) = wiki.GetRefineInfo(vnum)
							if retInfo:
								previewVnum = vnum + max_refine_count
						interfaceHandler = systemSetting.GetInterfaceHandler()
						if interfaceHandler:
							interfaceHandler.OpenRenderTargetWindow(0, previewVnum)
			else:
				wiki.GetBaseClass().OpenSpecialPage(parent, vnum, False)

		def __del__(self):
			if wiki.GetBaseClass():
				wiki.GetBaseClass().objList.pop(long(id(self)))
			
			ui.Window.__del__(self)
		
		def GetMaterialCount(self, refine_count, retInfo):
			maxMat = self.STARTING_MAT_COUNT
			
			for i in xrange(refine_count):
				curr = 0
				
				for j in retInfo[i][1]:
					if j[0] == 0:
						continue
					
					if curr >= wiki.REFINE_MATERIAL_MAX_NUM:
						break
					
					curr += 1
				
				maxMat = max(maxMat, curr)
			
			return maxMat
		
		def ProcessRetInfo(self, retInfo, maxMat, moneyRow, useHeight, useStart, starting_col = 0):
			for i in xrange(wiki.MAX_REFINE_COUNT):
				# Compact formatter so refine costs like 20,000,000 fit the
				# column as "20M" instead of MakeMoneyText's "20000k".
				money = FormatMoneyKK(retInfo[(i+starting_col)][0])
				
				currWindow = self.cols[i+1]
				
				if self.parent:
					item.SelectItem(self.vnum)
					
					currWindow.titleWnd.SAFE_SetOverInEvent(self.parent.OnOverIn, self.vnum + ((1+i+starting_col) if wiki.CanIncrRefineLevel() else 0), 1)
					currWindow.titleWnd.SAFE_SetOverOutEvent(self.parent.OnOverOut)
					currWindow.titleWnd.SetMouseRightButtonUpEvent(ui.__mem_func__(self.parent.OnRightDown), self.vnum + ((1+i+starting_col) if wiki.CanIncrRefineLevel() else 0))# to do : make this SetMouseLeftButtonUpEvent
				
				currWindow.refineText.SetText("+" + str((i+1)+starting_col))
				if localeinfo.IsARABIC():
					currWindow.refineText.SetHorizontalAlignRight()
					currWindow.refineText.SetPosition(10,\
											currWindow.titleWnd.GetHeight() / 2 - currWindow.refineText.GetTextSize()[1] / 2 - 1)
				else:
					currWindow.refineText.SetPosition(currWindow.titleWnd.GetWidth() / 2 - currWindow.refineText.GetTextSize()[0] / 2,\
											currWindow.titleWnd.GetHeight() / 2 - currWindow.refineText.GetTextSize()[1] / 2 - 1)
				
				currWindow.moneyText.SetText(money)
				
				if localeinfo.IsARABIC():
					currWindow.SetSize(750,750)
					currWindow.moneyText.SetHorizontalAlignRight()
					currWindow.moneyText.SetPosition(2,\
											useStart[moneyRow] + useHeight[moneyRow] / 2 - currWindow.moneyText.GetTextSize()[1] / 2 - 1)
				else:
					currWindow.moneyText.SetPosition(currWindow.GetWidth() / 2 - currWindow.moneyText.GetTextSize()[0] / 2,\
											useStart[moneyRow] + useHeight[moneyRow] / 2 - currWindow.moneyText.GetTextSize()[1] / 2 - 1)
				
				curr = 0
				
				for j in retInfo[(i+starting_col)][1]:
					if curr >= maxMat:
						break
					
					if j[0] != 0:
						item.SelectItem(j[0])

						currWindow.refineMat[curr].LoadImage(item.GetIconImageFileName())
						currWindow.refineMat[curr].SetPosition(5, useStart[curr + 1] + useHeight[curr + 1] / 2 - currWindow.refineMat[curr].GetHeight() / 2)
						currWindow.refineMat[curr].SetStringEvent("MOUSE_OVER_IN",ui.__mem_func__( self.parent.OnOverIn), j[0], 0)
						currWindow.refineMat[curr].SetStringEvent("MOUSE_OVER_OUT",ui.__mem_func__( self.parent.OnOverOut))
						currWindow.refineMat[curr].SetMouseRightButtonUpEvent(ui.__mem_func__(self.parent.OnRightDown), j[0])
						if wiki.GetBaseClass():
							currWindow.refineMat[curr].SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), self.parent, j[0], False) # needs fixing

						# Count rendered through the engine's NumberLine
						# (inventory-style digits) anchored at the icon's
						# bottom-right. The "-" TextLine is hidden while a
						# material is bound to this cell.
						currWindow.refineMatNum[curr].SetNumber(str(j[1]))
						currWindow.refineMatNum[curr].SetPosition(
							currWindow.refineMat[curr].GetLocalPosition()[0] + currWindow.refineMat[curr].GetWidth() - 2,
							currWindow.refineMat[curr].GetLocalPosition()[1] + currWindow.refineMat[curr].GetHeight() - 12)
						currWindow.refineMatNum[curr].Show()
						currWindow.refineMatText[curr].Hide()

					else:
						currWindow.refineMat[curr].UnloadImage()
						currWindow.refineMatNum[curr].Hide()

						currWindow.refineMatText[curr].SetText("-")
						currWindow.refineMatText[curr].SetFontColor(0.78, 0.78, 0.78)
						currWindow.refineMatText[curr].SetPosition(currWindow.GetWidth() / 2 - currWindow.refineMatText[curr].GetTextSize()[0] / 2,\
													useStart[curr + 1] + useHeight[curr + 1] / 2 - currWindow.refineMatText[curr].GetTextSize()[1] / 2 - 1)
						currWindow.refineMatText[curr].Show()
					curr += 1
		
		def NoticeMe(self, noticeType = [False, 0]):
			(scrollingNoticeType, starting_col) = noticeType
			(max_refine_count, retInfo) = wiki.GetRefineInfo(self.vnum)
			if not retInfo:
				return
			
			if self.itemImage and self.parent:
				item.SelectItem(self.vnum)
				
				self.itemImage.SetStringEvent("MOUSE_OVER_IN",ui.__mem_func__( self.parent.OnOverIn), self.vnum + (max_refine_count if wiki.CanIncrRefineLevel() else 0), 0)
				self.itemImage.SetStringEvent("MOUSE_OVER_OUT",ui.__mem_func__( self.parent.OnOverOut))
				self.itemImage.SetMouseRightButtonUpEvent(ui.__mem_func__(self.parent.OnRightDown), self.vnum + (max_refine_count if wiki.CanIncrRefineLevel() else 0)) # to do : make this SetMouseLeftButtonUpEvent
			
			maxMat = self.GetMaterialCount(max_refine_count, retInfo)
			moneyRow = (maxMat + 1)
			
			if maxMat > self.STARTING_MAT_COUNT:
				if not scrollingNoticeType:
					self.SetExpandedRow(maxMat)
				
				useHeight = self.ROW_HEIGHTS_EXPANDED[maxMat][0]
				useStart = self.ROW_HEIGHTS_EXPANDED[maxMat][1]
			else:
				useHeight = self.ROW_HEIGHTS
				useStart = self.ROW_START_Y
			
			if not scrollingNoticeType:
				self.LoadHorizontalScrollBoard(max_refine_count)
			
			self.ProcessRetInfo(retInfo, maxMat, moneyRow, useHeight, useStart, starting_col)
		
		def SetExpandedRow(self, materialCount):
			(useHeight, useStart) = self.ROW_HEIGHTS_EXPANDED[materialCount]
			oldSize = self.base.GetHeight()
			
			self.base.SetGridSize(materialCount)
			self.SetSize(self.base.GetWidth(), self.base.GetHeight())
			
			for tmp in self.cols:
				tmp.SetSize(tmp.GetWidth(), ((useStart[-1] - 2) + useHeight[-1]))

				tmp.refineMat = []
				tmp.refineMatText = []
				tmp.refineMatNum = []

				for j in xrange(materialCount):
					tmp.refineMat.append(ui.ExpandedImageBox())
					tmp.refineMat[j].SetParent(tmp)
					tmp.refineMat[j].Show()

					tmp.refineMatNum.append(ui.NumberLine())
					tmp.refineMatNum[j].SetParent(tmp)
					tmp.refineMatNum[j].SetHorizontalAlignRight()
					tmp.refineMatNum[j].Hide()

					tmp.refineMatText.append(ui.TextLine())
					tmp.refineMatText[j].SetParent(tmp)
					tmp.refineMatText[j].SetText("-")
					tmp.refineMatText[j].SetPosition(tmp.GetWidth() / 2 - tmp.refineMatText[j].GetTextSize()[0] / 2,\
													useStart[j + 1] + useHeight[j + 1] / 2 - tmp.refineMatText[j].GetTextSize()[1] / 2 - 1)
					tmp.refineMatText[j].Show()
				
				tmp.moneyText = ui.TextLine()
				tmp.moneyText.SetParent(tmp)
				tmp.moneyText.SetText("-")
				tmp.moneyText.SetPosition(tmp.GetWidth() / 2 - tmp.moneyText.GetTextSize()[0] / 2,\
										useStart[(materialCount + 1)] + useHeight[(materialCount + 1)] / 2 - tmp.moneyText.GetTextSize()[1] / 2 - 1)
				tmp.moneyText.Show()
			
			self.goldText.SetPosition(49 + 81 / 2 - self.goldText.GetTextSize()[0] / 2, 21 + useStart[(materialCount + 1)] + useHeight[(materialCount + 1)] / 2 - self.goldText.GetTextSize()[1] / 2 - 1)
			self.itemImage.SetPosition(1 + 47 / 2 - self.itemImage.GetWidth() / 2, 10 + (self.base.GetHeight() / 2) - (self.itemImage.GetHeight() / 2))
			
			if self.parent:
				self.parent.ChangeElementSize(self, self.base.GetHeight() - oldSize)
		
		def LoadHorizontalScrollBoard(self, max_refine_count):
			(baseWidth, baseHeight) = (self.base.GetWidth(), self.base.GetHeight())
			scrollBoardHeight = 7
			
			if max_refine_count > wiki.MAX_REFINE_COUNT and\
				self.scrollBoard and self.scrollBar:
				
				self.SetSize(baseWidth, baseHeight + (scrollBoardHeight - 1))
				
				self.scrollBoard.SetSize(baseWidth, scrollBoardHeight)
				self.scrollBoard.SetPosition(0, (baseHeight - 1))
				self.scrollBoard.Show()
				
				size_perc = truediv(wiki.MAX_REFINE_COUNT, max_refine_count)
				new_size = int(size_perc * self.scrollBoard.GetWidth())
				
				self.scrollBar.SetSize(self.scrollBoard.GetWidth(), self.scrollBoard.GetHeight())
				self.scrollBar.SetStaticScale(new_size)
				self.scrollBar.SetPosScale(0.0)
				self.scrollBar.Show()
				
				if self.parent:
					self.parent.ChangeElementSize(self, (scrollBoardHeight - 1))
			else:
				self.SetSize(baseWidth, baseHeight)
				self.scrollBoard.Hide()
				
				if self.parent:
					self.parent.ChangeElementSize(self, self.GetHeight() - baseHeight)
		
		def RegisterHorizontalScrollBar(self):
			if not self.scrollBoard:
				return
			
			self.scrollBar = WikiScrollBar(True)
			self.scrollBar.SetParent(self.scrollBoard)
			self.scrollBar.SetPosition(0, 0)
			self.scrollBar.SetScrollEvent(self.OnScrollBar)
			self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
			self.scrollBar.Show()
		
		def OnScrollBar(self, fScale):
			(max_refine_count, _) = wiki.GetRefineInfo(self.vnum)
			
			if max_refine_count <= wiki.MAX_REFINE_COUNT:
				return
			
			starting_col = int(fScale * (max_refine_count - wiki.MAX_REFINE_COUNT))
			self.NoticeMe([True, starting_col])
		
		def OnRender(self):
			if self.additionalLoaded:
				return
			
			if wiki.IsSet(self.vnum) or not hasattr(self.parent, "loadFrom") or\
				self.parent.loadFrom == self.parent.loadTo:
				self.additionalLoaded = True
				wiki.LoadInfo(long(id(self)), self.vnum)

	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 5
	SCROLL_SPEED = 50
	ITEM_LOAD_PER_UPDATE = 1
	
	classButtonsPath = "d:/ymir work/ui/wiki/"
	if app.INGAME_WIKI_WOLFMAN:
		classButtonsPath += "ingame_wiki_wolfman/"
	
	CLASS_BUTTONS = [
		[
			item.ITEM_ANTIFLAG_WARRIOR,
			classButtonsPath + "class_w_normal.png",
			classButtonsPath + "class_w_hover.png",
			classButtonsPath + "class_w_selected.png"
		],
		[
			item.ITEM_ANTIFLAG_ASSASSIN,
			classButtonsPath + "class_n_normal.png",
			classButtonsPath + "class_n_hover.png",
			classButtonsPath + "class_n_selected.png"
		],
		[
			item.ITEM_ANTIFLAG_SHAMAN,
			classButtonsPath + "class_s_normal.png",
			classButtonsPath + "class_s_hover.png",
			classButtonsPath + "class_s_selected.png"
		],
		[
			item.ITEM_ANTIFLAG_SURA,
			classButtonsPath + "class_su_normal.png",
			classButtonsPath + "class_su_hover.png",
			classButtonsPath + "class_su_selected.png"
		]
	]
	
	if app.INGAME_WIKI_WOLFMAN:
		lWolfmanClassButtons = [
			[
				item.ITEM_ANTIFLAG_WOLFMAN,
				classButtonsPath + "class_l_normal.tga",
				classButtonsPath + "class_l_hover.tga",
				classButtonsPath + "class_l_selected.tga"
			]
		]
		
		CLASS_BUTTONS.extend(lWolfmanClassButtons)
	
	def __init__(self):
		ui.Window.__init__(self)
		
		self.toolTip = uitooltip.ItemToolTip()
		
		self.SetSize(*mainBoardSize)
		
		self.elements = []
		self.scrollBar = None
		
		self.isOpened = False
		self.loadFrom = 0
		self.loadTo = 0
		
		self.currFlag = 0
		self.currCateg = 0
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(541, self.GetHeight() - 50 - 10)
		self.peekWindow.SetPosition(5, 50)

		if not app.USE_CLIP_MASK:
			self.peekWindow.SetInsideRender(True)

		self.peekWindow.Show()

		self.categWindow = ui.Window()
		self.categWindow.SetParent(self)
		self.categWindow.AddFlag("attach")
		self.categWindow.AddFlag("not_pick")
		self.categWindow.Show()
		
		self.classBtns = []
		for info in self.CLASS_BUTTONS:
			idx = len(self.classBtns)
			
			self.classBtns.append(ui.RadioButton())
			self.classBtns[idx].SetParent(self.categWindow)
			self.classBtns[idx].SetUpVisual(info[1])
			self.classBtns[idx].SetOverVisual(info[2])
			self.classBtns[idx].SetDownVisual(info[3])
			self.classBtns[idx].SetEvent(ui.__mem_func__(self.OnSelectCateg), proxy(self.classBtns[idx]), info[0])
			self.classBtns[idx].SetPosition(self.categWindow.GetWidth() + 5 * self.CLASS_BUTTONS.index(info), 0)
			self.classBtns[idx].Show()
			
			self.categWindow.SetSize(self.categWindow.GetWidth() + self.classBtns[idx].GetWidth(), self.classBtns[idx].GetHeight())
		
		self.categWindow.SetSize(self.categWindow.GetWidth() + 5 * (len(self.CLASS_BUTTONS) - 1), self.categWindow.GetHeight())
		self.categWindow.SetPosition(self.GetWidth() / 2 - self.categWindow.GetWidth() / 2, 10)
		
		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")

		if app.USE_CLIP_MASK:
			self.scrollBoard.SetClippingMaskWindow(self.peekWindow)

		self.scrollBoard.Show()

		self.RegisterScrollBar()
	
	def OpenWindow(self):
		wndMgr.Show(self.hWnd)
	
	def Show(self, categID):
		wndMgr.Show(self.hWnd)
		
		isChanged = (not categID == self.currCateg)
		self.currCateg = categID
		
		if not self.isOpened:
			self.isOpened = True
			
			if len(self.classBtns):
				self.OnSelectCateg(proxy(self.classBtns[0]), self.CLASS_BUTTONS[0][0])
		else:
			self.loadTo = wiki.LoadClassItems(self.currCateg, self.currFlag)
			
			if self.loadFrom > self.loadTo or isChanged:
				del self.elements[:]
				
				self.scrollBoard.SetSize(0, 0)
				self.UpdateScrollbar()
				self.loadFrom = 0
	
	def OnOverIn(self, vnum, render):
		if not self.toolTip:
			return
		
		self.toolTip.ClearToolTip()
		self.toolTip.AddItemData(vnum, [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)], 0, noRender = render)
		self.toolTip.AppendWikiAccessoryMaterials(vnum)

	def OnOverOut(self):
		if not self.toolTip:
			return
		
		self.toolTip.Hide()

	def OnRightDown(self, itemVnum = 0):
		if itemVnum == 0:
			return
		if app.ENABLE_RENDER_TARGET and\
			app.IsPressed(app.DIK_LSHIFT):
				if uiRenderTarget.IsCanShowItems(itemVnum):
					interfaceHandler = systemSetting.GetInterfaceHandler()
					if interfaceHandler:
						interfaceHandler.OpenRenderTargetWindow(0, itemVnum)

	def OnSelectCateg(self, btn, flag):
		self.currFlag = flag
		
		for tmpBtn in self.classBtns:
			tmpBtn.SetUp() if proxy(tmpBtn) != btn else tmpBtn.Down()
		
		del self.elements[:]
		
		self.scrollBoard.SetSize(0, 0)
		self.UpdateScrollbar()
		
		self.loadTo = wiki.LoadClassItems(self.currCateg, self.currFlag)
		self.loadFrom = 0
	
	def OnUpdate(self):
		if self.loadFrom < self.loadTo:
			for i in wiki.ChangePage(self.loadFrom, min(self.loadTo, self.loadFrom + self.ITEM_LOAD_PER_UPDATE)):
				self.AddItem(i)
				self.loadFrom += 1
	
	def ChangeElementSize(self, elem, sizeDiff):
		foundItem = False
		
		for i in self.elements:
			if elem != i and not foundItem:
				continue
			elif elem == i:
				foundItem = True
				continue
			
			i.SetPosition(i.GetLocalPosition()[0],\
							i.GetLocalPosition()[1] + sizeDiff)
		
		if foundItem:
			self.scrollBoard.SetSize(elem.GetWidth(), self.scrollBoard.GetHeight() + sizeDiff)
			self.UpdateScrollbar()
	
	def AddItem(self, vnum):
		startRefineVnum = wiki.GetWikiItemStartRefineVnum(vnum)
		vnum = startRefineVnum if startRefineVnum != 0 else (int(vnum / 10) * 10)
		
		for i in self.elements:
			if vnum == i.vnum:
				return None
		
		item.SelectItem(vnum)
		
		tmp = self.WikiItem(vnum, self)
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")
		
		addPadding = 0
		totalElem = len(self.elements)
		if totalElem > 0:
			lastIndex = 0
			
			for i in xrange(totalElem):
				if self.elements[i].levelLimit < tmp.levelLimit or self.elements[i].levelLimit == tmp.levelLimit and self.elements[i].vnum < tmp.vnum:
					break
				
				lastIndex += 1
			
			self.elements.insert(lastIndex, tmp)
			totalElem += 1
			
			for i in xrange(lastIndex, totalElem):
				self.elements[i].SetPosition(0,\
							(0 if i == 0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))
			
			addPadding = self.ELEM_PADDING
		else:
			self.elements.append(tmp)
		
		tmp.Show()
		
		self.scrollBoard.SetSize(tmp.GetWidth(),\
								self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.UpdateScrollbar()
		
		return tmp
	
	def OnRunMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			val = int((length * 0.01) * self.SCROLL_SPEED)
			self.UpdateScrollbar(val)
			
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.peekWindow.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.peekWindow.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

class ChestPeekWindow(ui.Window):
	"""Static values!
		Please dont touch on them."""
	ELEM_X_PADDING = 0
	ELEM_PADDING = 0

	if app.USE_EXTENDED_WIKI_SHOP:
		ELEM_START_X = 0

	SCROLL_SPEED = 25
	ELEM_PER_LINE = 11

	def __init__(self, parent, width, height, sendParent = True):
		ui.Window.__init__(self)

		self.SetSize(width, height)

		self.parent = proxy(parent)
		self.sendParent = sendParent

		self.elements = []
		self.posMap = {}
		self.scrollBar = None

		self.mOverInEvent = None
		self.mOverOutEvent = None
		self.mOnRightEvent = None

		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(width - 6, self.GetHeight())
		self.peekWindow.SetPosition(0, 0)
		self.peekWindow.Show()

		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")
		# Give scrollBoard an explicit size + position so UpdateRect has
		# something to compute against when slotWnd is later parented to it.
		self.scrollBoard.SetSize(width - 6, height)
		self.scrollBoard.SetPosition(0, 0)
		self.scrollBoard.Show()

		# SlotWindow renders the chest/drop/shop items via the engine's
		# wndMgr.SetSlot + wndMgr.SetSlotCount path -- same icon + count
		# rendering inventory uses. Clip masks: the wiki's outer scroll
		# viewport propagates a PRIMARY clip mask down through AddChild
		# when chestPeek gets parented; we set our local peekWindow as the
		# SUB mask so the effective clip is sub-intersect-with-primary,
		# letting off-screen rows clip away (engine intersection logic in
		# CWindow::OnUpdate).
		self.slotWnd = ui.SlotWindow()
		self.slotWnd.SetParent(self.scrollBoard)
		self.slotWnd.SetPosition(0, 0)
		self.slotWnd.SetSize(width - 6, height)
		if app.USE_CLIP_MASK:
			# Sub mask: row-local bounds. Primary mask is supplied later by
			# the wiki's outer SetClippingMaskWindow propagation, after
			# chestPeek is parented to the wiki row. NOT calling
			# SetClippingMaskWindow here -- that would set m_bEnableMask
			# and block the outer propagation.
			self.slotWnd.SetSubClippingMaskWindow(self.peekWindow)
		self.slotWnd.Show()

		# slotIndex -> per-slot metadata (vnum, metin sockets, shop/item
		# indices, navigation target vnum). Engine slot callbacks only know
		# the slot index; this dict lets us recover everything for routing
		# back through mOverInEvent / mOverOutEvent / mOnRightEvent.
		self.slotMeta = {}

		self.slotWnd.SetOverInItemEvent(ui.__mem_func__(self._OnSlotOverIn))
		self.slotWnd.SetOverOutItemEvent(ui.__mem_func__(self._OnSlotOverOut))
		self.slotWnd.SetSelectItemSlotEvent(ui.__mem_func__(self._OnSlotLeftClick))
		self.slotWnd.SetUseSlotEvent(ui.__mem_func__(self._OnSlotRightClick))

	def AddItem(self, vnumFrom, vnumTo, _shop_index = None, _item_index = None):
		if not self.scrollBar:
			self.RegisterScrollBar()

		metinSlot = [0 for _i in xrange(player.METIN_SOCKET_MAX_NUM)]
		if vnumFrom == 8:
			vnumFrom = 70104
			metinSlot[0] = vnumTo

		item.SelectItem(vnumFrom)
		(itemW, itemH) = item.GetItemSize()  # 1x1 for jewelry/etc, 1x2 for armor/weapons

		# ---- Slot position: same posMap algorithm as the original code -----
		# Scan posMap to find the leftmost free cell. Multi-row items
		# (itemH == 2) claim both the current AND next-row cells so subsequent
		# slots flow around them.
		totalElem = len(self.slotMeta)
		if totalElem > 0:
			currAdd = 0
			while currAdd in self.posMap:
				currAdd += 1

			totalLine = (currAdd % self.ELEM_PER_LINE)
			currH = (math.floor(currAdd / self.ELEM_PER_LINE) * (32 + self.ELEM_PADDING))

			for i in xrange(itemH):
				self.posMap[currAdd + i * self.ELEM_PER_LINE] = True

			cellX = (self.ELEM_START_X if app.USE_EXTENDED_WIKI_SHOP else 0) + 1 \
				+ totalLine * (36 + self.ELEM_X_PADDING)
			cellY = 0 + currH
		else:
			for i in xrange(itemH):
				self.posMap[i * self.ELEM_PER_LINE] = True
			cellX = (self.ELEM_START_X if app.USE_EXTENDED_WIKI_SHOP else 0) + 1
			cellY = 0

		# ---- Compute the wiki-page navigation vnum -------------------------
		# Weapons / armor jump to the start of their refine chain so the
		# wiki opens at the +0 detail page (same logic as the legacy
		# MOUSE_LEFT_DOWN string-event wiring).
		navVnum = vnumFrom
		if wiki.GetBaseClass():
			if (item.GetItemType() == item.ITEM_TYPE_WEAPON
					or item.GetItemType() == item.ITEM_TYPE_ARMOR):
				startRefineVnum = wiki.GetWikiItemStartRefineVnum(vnumFrom)
				navVnum = startRefineVnum if startRefineVnum != 0 else (int(vnumFrom / 10) * 10)

		# ---- Slot rendering via engine (icon + count) ----------------------
		slotIndex = len(self.slotMeta)
		self.slotWnd.AppendSlot(slotIndex, cellX, cellY, itemW * 32, itemH * 32)

		# Yang (vnum 1) needs MakeMoneyText formatting that wndMgr.SetSlotCount
		# can't produce -- fall back to a TextLine overlay for that case.
		# Every other item count goes through the engine.
		moneyOverlay = None
		if vnumFrom == 1:
			self.slotWnd.SetItemSlot(slotIndex, vnumFrom, 0)  # icon, no count
			moneyOverlay = ui.TextLine()
			moneyOverlay.SetParent(self.slotWnd)
			moneyOverlay.AddFlag("attach")
			moneyOverlay.AddFlag("not_pick")
			moneyOverlay.SetFontName(localeinfo.UI_DEF_FONT)
			moneyOverlay.SetOutline()
			moneyOverlay.SetFeather(False)
			moneyOverlay.SetHorizontalAlignRight()
			moneyOverlay.SetText(MakeMoneyText(vnumTo))
			moneyOverlay.SetPosition(
				cellX + (itemW * 32) - 1,
				cellY + (itemH * 32) - moneyOverlay.GetTextSize()[1])
			if app.USE_CLIP_MASK:
				moneyOverlay.SetSubClippingMaskWindow(self.peekWindow)
			moneyOverlay.Show()
		else:
			# Engine convention: count of 1 is hidden (single item). Wiki
			# chests sometimes legitimately drop "1 of X" -- keep the
			# original behavior of showing any non-zero count.
			engineCount = vnumTo if vnumTo and vnumTo > 1 else 0
			self.slotWnd.SetItemSlot(slotIndex, vnumFrom, engineCount)

		# ---- Metadata so the slot-index callbacks can route correctly -----
		self.slotMeta[slotIndex] = {
			"vnum":       vnumFrom,
			"metinSlot":  metinSlot,
			"shopIndex":  _shop_index,
			"itemIndex":  _item_index,
			"navVnum":    navVnum,
			"itemSize":   itemH,
			"moneyTxt":   moneyOverlay,   # keep ref so it isn't GC'd
		}

		# elements list kept for back-compat (some callers iterate it).
		# Tuple shape preserved so unpacking sites don't break.
		self.elements.append((slotIndex, moneyOverlay))

		# ---- Grow scroll surfaces to fit -----------------------------------
		rowBottom = cellY + itemH * 32
		boardH = max(self.scrollBoard.GetHeight(), rowBottom)
		self.scrollBoard.SetSize(self.peekWindow.GetWidth(), boardH)
		self.slotWnd.SetSize(self.peekWindow.GetWidth(), boardH)
		self.UpdateScrollbar()

		# No callers use the return value -- previously returned the
		# ExpandedImageBox; now returning None is fine (verified via grep
		# of every dropList/itemContainer.AddItem(...) call site).
		return None

	# ----------------------------------------------------------------------
	# Slot event handlers (route engine slot-index callbacks to the
	# parent's existing string-event hooks).
	# ----------------------------------------------------------------------

	def _OnSlotOverIn(self, slotIndex):
		meta = self.slotMeta.get(slotIndex)
		if not meta or not self.mOverInEvent:
			return
		if meta["shopIndex"] is not None and meta["itemIndex"] is not None:
			self.mOverInEvent(meta["vnum"], meta["metinSlot"],
				meta["shopIndex"], meta["itemIndex"])
		else:
			self.mOverInEvent(meta["vnum"], meta["metinSlot"])

	def _OnSlotOverOut(self):
		if self.mOverOutEvent:
			self.mOverOutEvent()

	def _OnSlotLeftClick(self, slotIndex):
		meta = self.slotMeta.get(slotIndex)
		if not meta:
			return
		wikiBase = wiki.GetBaseClass()
		if not wikiBase:
			return
		# Match the legacy MOUSE_LEFT_DOWN routing: sendParent decides which
		# window the new wiki page is bound to.
		if not self.sendParent:
			wikiBase.OpenSpecialPage(None, meta["navVnum"], False)
		elif hasattr(self.parent, "parent"):
			wikiBase.OpenSpecialPage(self.parent.parent, meta["navVnum"], False)
		else:
			wikiBase.OpenSpecialPage(self.parent, meta["navVnum"], False)

	def _OnSlotRightClick(self, slotIndex):
		# Engine convention: right-click on a slot fires "use" -- we map
		# that to the existing mOnRightEvent hook. Shop variant passes vnum
		# (so OnRightDown can open render target); drop-list variant
		# passes nothing (OnRightDown(0) is a no-op, preserves prior
		# behavior).
		meta = self.slotMeta.get(slotIndex)
		if not meta or not self.mOnRightEvent:
			return
		if meta["shopIndex"] is not None and meta["itemIndex"] is not None:
			self.mOnRightEvent(meta["vnum"])
		else:
			self.mOnRightEvent()

	def OnRunMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			if self.scrollBar and self.scrollBar.IsShow():
				self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
				return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1,\
									self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(5, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

class WikiMainChestWindow(ui.Window):
	class WikiItem(ui.Window):
		#if app.USE_EXTENDED_WIKI:
		def __init__(self, vnum, parent, fromSpecialPage = False):
			ui.Window.__init__(self)

			self.parent = proxy(parent)

			if app.USE_EXTENDED_WIKI:
				self.fromSpecialPage = fromSpecialPage

			self.vnum = vnum
			self.additionalLoaded = False

			wikiBase = wiki.GetBaseClass()
			if id(self) not in wikiBase.objList:
				wikiBase.objList[long(id(self))] = proxy(self)

			self.base = ui.ExpandedImageBox()
			self.base.SetParent(self)
			self.base.AddFlag("attach")
			self.base.AddFlag("not_pick")

			if app.USE_EXTENDED_WIKI and self.fromSpecialPage:
				self.base.LoadImage("d:/ymir work/ui/wiki/detail_chest2.png")
			else:
				self.base.LoadImage("d:/ymir work/ui/wiki/detail_chest.png")

			self.base.Show()

			self.chestImage = ui.ExpandedImageBox()
			self.chestImage.SetParent(self.base)
			self.chestImage.LoadImage(item.GetIconImageFileName())
			self.chestImage.SetPosition(1 + 47 / 2 - self.chestImage.GetWidth() / 2,\
									1 + 87 / 2 - self.chestImage.GetHeight() / 2)
			self.chestImage.SetStringEvent("MOUSE_OVER_IN",ui.__mem_func__( self.parent.OnOverIn), self.vnum, 0)
			self.chestImage.SetStringEvent("MOUSE_OVER_OUT",ui.__mem_func__( self.parent.OnOverOut))
			self.chestImage.SetMouseRightButtonUpEvent(ui.__mem_func__(self.parent.OnRightDown), self.vnum)
			# Left-click opens the chest's detail (special) page. This wiring was
			# missing -- unlike the weapon/boss WikiItems -- so chest icons in
			# the listing were unclickable and their special page never opened.
			# isMonster=False because a chest is an item.
			self.chestImage.SetMouseLeftButtonDownEvent(
				ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage),
				self.parent, self.vnum, False)

			if app.USE_EXTENDED_WIKI and self.fromSpecialPage:
				self.chestImage.Hide()
			else:
				self.chestImage.Show()

			if app.USE_EXTENDED_WIKI and self.fromSpecialPage:
				self.dropList = ChestPeekWindow(self, 400, 96, False)
			else:
				self.dropList = ChestPeekWindow(self, 401, 66)

			self.dropList.AddFlag("attach")
			self.dropList.SetParent(self.base)

			if app.USE_EXTENDED_WIKI and self.fromSpecialPage:
				self.dropList.SetPosition(70, 30)
			else:
				self.dropList.SetPosition(49, 22)

			self.dropList.mOverInEvent = ui.__mem_func__(self.parent.OnOverIn)
			self.dropList.mOverOutEvent = ui.__mem_func__(self.parent.OnOverOut)
			self.dropList.mOnRightEvent = ui.__mem_func__(self.parent.OnRightDown)
			self.dropList.Show()

			self.originTextHead = ui.TextLine()
			self.originTextHead.SetParent(self.base)
			self.originTextHead.AddFlag("attach")
			self.originTextHead.AddFlag("not_pick")
			self.originTextHead.SetText(localeinfo.WIKI_CHESTINFO_ORIGIN)
			self.originTextHead.SetPackedFontColor(0xfffad390)
			if localeinfo.IsARABIC():
				#self.originTextHead.SetHorizontalAlignLeft()
				self.originTextHead.SetPosition(451 + 170 / 2 - self.originTextHead.GetTextSize()[0] / 2,\
						1 + 20 / 2 - self.originTextHead.GetTextSize()[1] / 2 - 1)
			else:
				self.originTextHead.SetPosition(451 + 89 / 2 - self.originTextHead.GetTextSize()[0] / 2,\
						1 + 20 / 2 - self.originTextHead.GetTextSize()[1] / 2 - 1)

			if app.USE_EXTENDED_WIKI and self.fromSpecialPage:
				self.originTextHead.Hide()
			else:
				self.originTextHead.Show()

			self.contentText = ui.TextLine()
			self.contentText.SetParent(self.base)
			self.contentText.AddFlag("attach")
			self.contentText.AddFlag("not_pick")
			self.contentText.SetText(localeinfo.WIKI_CHESTINFO_CONTENTOF % item.GetItemName())
			if localeinfo.IsARABIC():

				self.contentText.SetPosition(250,\
										1 + 20 / 2 - self.contentText.GetTextSize()[1] / 2 - 1)
				self.contentText.SetHorizontalAlignCenter()
				self.contentText.SetPackedFontColor(0xfffad390)
			else:
				self.contentText.SetPosition(49 + 401 / 2 - self.contentText.GetTextSize()[0] / 2,\
										1 + 20 / 2 - self.contentText.GetTextSize()[1] / 2 - 1)

			if app.USE_EXTENDED_WIKI and self.fromSpecialPage:
				self.contentText.Hide()
			else:
				self.contentText.Show()

			self.originText = ui.TextLine()
			self.originText.SetParent(self.base)
			self.originText.AddFlag("attach")
			self.originText.AddFlag("not_pick")
			self.originText.SetText("")
			self.originText.SetPosition(451 + 89 / 2 - self.originText.GetTextSize()[0] / 2,\
									22 + 66 / 2 - self.originText.GetTextSize()[1] / 2 - 1)

			if app.USE_EXTENDED_WIKI and self.fromSpecialPage:
				self.originText.Hide()
			else:
				self.originText.Show()

			self.originInfoLoad = False

			self.originInfo = WikiItemOriginInfo(self.vnum, True, _parent = parent)
			# self.originInfo = WikiItemOriginInfo(self.vnum, True)
			self.originInfo.SetParent(self.base)
			self.originInfo.AddFlag("attach")

			# if localeinfo.IsARABIC():
				# self.originInfo.SetPosition(451 + 2, 22 + 4)
			# else:
			self.originInfo.SetPosition(451 + 2, 22 + 4)

			if app.USE_EXTENDED_WIKI and self.fromSpecialPage:
				self.originInfo.Hide()
			else:
				self.originInfo.Show()

			self.SetSize(self.base.GetWidth(), self.base.GetHeight())

		def __del__(self):
			if wiki.GetBaseClass():
				wiki.GetBaseClass().objList.pop(long(id(self)))
			
			ui.Window.__del__(self)
		
		def __GenerateMultiLine(self, text, maxWidth):
			currText = self.__GenerateSingleLine()
			textHolder = []
			
			tempText = ui.TextLine()
			tempText.Hide()
			
			splt = text.split(" ")
			currText.SetText(splt[0])
			splt = splt[1:]
			for i in splt:
				tempText.SetText(" " + i)
				if tempText.GetTextSize()[0] + currText.GetTextSize()[0] > maxWidth:
					currText.AdjustSize()
					textHolder.append(currText)
					currText = self.__GenerateSingleLine()
					#currText.SetHorizontalAlignLeft()
					currText.SetText(i)
				else:
					#currText.SetHorizontalAlignLeft()
					currText.SetText(currText.GetText() + " " + i)
			
			textHolder.append(currText)
			return textHolder
		
		def __GenerateSingleLine(self):
			text = ui.TextLine()
			text.SetParent(self.base)
			#text.SetHorizontalAlignLeft()
			text.Show()
			return text
		
		def NoticeMe(self):
			ret = wiki.GetChestInfo(self.vnum)
			allow_lst = (len(ret) > 2)

			if not allow_lst:
				(dwOrigin, isCommon) = ret
			else:
				(dwOrigin, isCommon, lst) = ret
			
			self.originInfoLoad = False
			self.originText.Hide()
			self.multiHolder = []
			
			if isCommon:
				self.multiHolder = self.__GenerateMultiLine(localeinfo.WIKI_CHESTINFO_COMMON_DROP, 66)
			elif dwOrigin:
				if app.USE_EXTENDED_WIKI and self.fromSpecialPage:
					self.originInfo.Hide()
				else:
					self.originInfo.Show()
			else:
				if app.USE_EXTENDED_WIKI and self.fromSpecialPage:
					pass
				else:
					self.originText.SetPosition(451 + 89 / 2 - self.originText.GetTextSize()[0] / 2, 22 + 66 / 2 - self.originText.GetTextSize()[1] / 2 - 1)
					self.originText.Show()

			for i in self.multiHolder:
				totalH = self.multiHolder[0].GetTextSize()[1] * len(self.multiHolder) + 3 * (len(self.multiHolder) - 1)
				i.SetPosition(451 + 89 / 2 - i.GetTextSize()[0] / 2, 22 + 66 / 2 - totalH / 2 + 3 * self.multiHolder.index(i) + i.GetTextSize()[1] * self.multiHolder.index(i))

			if not allow_lst:
				return
			
			sizeLst = []
			orderedLst = []
			otherStuff = []
			
			for i in lst:
				if i[0] < wiki.CONTROL_ITEM_VNUM:
					otherStuff.append(i[:])
					continue
				
				item.SelectItem(i[0])
				size = item.GetItemSize()[1]
				
				lastPos = 0
				for k in xrange(len(sizeLst)):
					if sizeLst[k] < size:
						break
					
					lastPos += 1
				
				sizeLst.insert(lastPos, size)
				orderedLst.insert(lastPos, i[:])
			
			for i in orderedLst:
				count = (i[1] if i[1] > 1 else 0)
				self.dropList.AddItem(i[0], count)
			
			for i in otherStuff:
				self.dropList.AddItem(i[0], i[1])
		
		def OnRender(self):
			if not self.originInfoLoad and self.originInfo.IsShow():
				self.originInfo.ParseTextlines()
				self.originInfoLoad = True

			if self.additionalLoaded:
				return

			if wiki.IsSet(self.vnum) or self.parent.loadFrom == self.parent.loadTo:
				self.additionalLoaded = True
				wiki.LoadInfo(long(id(self)), self.vnum)
	
	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 5
	SCROLL_SPEED = 50
	ITEM_LOAD_PER_UPDATE = 1
	
	def __init__(self):
		ui.Window.__init__(self)

		self.toolTip = uitooltip.ItemToolTip()
		
		self.SetSize(*mainBoardSize)
		
		self.elements = []
		self.scrollBar = None
		
		self.chestVnums = []
		
		self.isOpened = False
		self.loadFrom = 0
		self.loadTo = 0
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(541, self.GetHeight() - 15)
		self.peekWindow.SetPosition(5, 5)

		if not app.USE_CLIP_MASK:
			self.peekWindow.SetInsideRender(True)

		self.peekWindow.Show()

		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")

		if app.USE_CLIP_MASK:
			self.scrollBoard.SetClippingMaskWindow(self.peekWindow)

		self.scrollBoard.Show()

		self.RegisterScrollBar()
	
	def OpenWindow(self):
		wndMgr.Show(self.hWnd)
	
	def Show(self, vnums):
		wndMgr.Show(self.hWnd)
		
		isChanged = (not len(vnums) == len(self.chestVnums))
		
		if not isChanged:
			for i in vnums:
				if i not in self.chestVnums:
					isChanged = True
					break
		
		if not isChanged:
			for i in self.chestVnums:
				if i not in vnums:
					isChanged = True
					break
		
		self.chestVnums = vnums[:]
		self.loadTo = len(self.chestVnums)
		
		if not self.isOpened:
			self.isOpened = True
			self.loadFrom = 0
		
		if self.loadFrom > self.loadTo or isChanged:
			del self.elements[:]
			self.loadFrom = 0
			
			self.scrollBoard.SetSize(0, 0)
			self.UpdateScrollbar()
	
	def OnOverIn(self, vnum, render):
		if not self.toolTip:
			return
		
		self.toolTip.ClearToolTip()
		self.toolTip.AddItemData(vnum, [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)], 0, noRender = render)
		self.toolTip.AppendWikiAccessoryMaterials(vnum)

	def OnOverOut(self):
		if not self.toolTip:
			return
		
		self.toolTip.Hide()

	def OnRightDown(self, itemVnum = 0):
		if itemVnum == 0:
			return

		if app.ENABLE_RENDER_TARGET and\
			app.IsPressed(app.DIK_LSHIFT):
				if uiRenderTarget.IsCanShowItems(itemVnum):
					interfaceHandler = systemSetting.GetInterfaceHandler()
					if interfaceHandler:
						interfaceHandler.OpenRenderTargetWindow(0,itemVnum)

	def OnUpdate(self):
		if self.loadFrom < self.loadTo:
			for i in xrange(self.loadFrom, min(self.loadTo, self.loadFrom + self.ITEM_LOAD_PER_UPDATE)):
				if type(self.chestVnums[i]) == types.ListType:
					for idx in self.chestVnums[i]:
						self.AddItem(idx)
				else:
					self.AddItem(self.chestVnums[i])
				self.loadFrom += 1
	
	def AddItem(self, vnum):
		for i in self.elements:
			if vnum == i.vnum:
				return None
		
		item.SelectItem(vnum)
		
		tmp = self.WikiItem(vnum, self)
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")
		
		addPadding = 0
		totalElem = len(self.elements)
		
		if totalElem > 0:
			lastIndex = totalElem
			
			self.elements.insert(lastIndex, tmp)
			totalElem += 1
			
			for i in xrange(lastIndex, totalElem):
				self.elements[i].SetPosition(0,\
					(0 if i == 0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))
			
			addPadding = self.ELEM_PADDING
		else:
			self.elements.append(tmp)
		
		tmp.Show()
		
		self.scrollBoard.SetSize(tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.UpdateScrollbar()
		
		return tmp
	
	def OnRunMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

class WikiMainBossWindow(ui.Window):
	class WikiItem(ui.Window):
		def __init__(self, vnum, parent):
			ui.Window.__init__(self)
			
			self.parent = proxy(parent)
			self.vnum = vnum
			
			wikiBase = wiki.GetBaseClass()
			if id(self) not in wikiBase.objList:
				wikiBase.objList[long(id(self))] = proxy(self)
			
			self.additionalLoaded = False
			
			self.base = ui.ExpandedImageBox()
			self.base.SetParent(self)
			self.base.AddFlag("attach")
			self.base.AddFlag("not_pick")
			self.base.LoadImage("d:/ymir work/ui/wiki/detail_chest.png")
			self.base.Show()
			
			self.modelView = WikiRenderTarget(47, 87)
			self.modelView.SetParent(self.base)
			self.modelView.SetPosition(1 + 47 / 2 - self.modelView.GetWidth() / 2,\
								1 + 87 / 2 - self.modelView.GetHeight() / 2)
			if wiki.GetBaseClass():
				self.modelView.SetMouseLeftButtonDownEvent(ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), self.parent, self.vnum, True)

			self.modelView.Hide()
			
			self.dropList = ChestPeekWindow(self, 401, 66)
			self.dropList.AddFlag("attach")
			self.dropList.SetParent(self.base)
			self.dropList.SetPosition(49, 22)
			self.dropList.mOverInEvent = ui.__mem_func__(self.parent.OnOverIn)
			self.dropList.mOverOutEvent = ui.__mem_func__(self.parent.OnOverOut)
			self.dropList.mOnRightEvent = ui.__mem_func__(self.parent.OnRightDown)
			self.dropList.Show()
			
			self.originTextHead = ui.TextLine()
			self.originTextHead.SetParent(self.base)
			self.originTextHead.AddFlag("attach")
			self.originTextHead.AddFlag("not_pick")
			# Header above the new location panel (was empty before -- see the
			# WikiItemOriginInfo block at the bottom of __init__).
			self.originTextHead.SetText(localeinfo.WIKI_NPC_LOCATION)
			self.originTextHead.SetPackedFontColor(0xfffad390)
			if localeinfo.IsARABIC():
				self.originTextHead.SetHorizontalAlignRight()
				self.originTextHead.SetPosition(451 + 89 / 2 - self.originTextHead.GetTextSize()[0] / 2,\
						1 + 20 / 2 - self.originTextHead.GetTextSize()[1] / 2 - 1)
			else:
				self.originTextHead.SetPosition(451 + 89 / 2 - self.originTextHead.GetTextSize()[0] / 2,\
						1 + 20 / 2 - self.originTextHead.GetTextSize()[1] / 2 - 1)
			self.originTextHead.Show()

			self.contentText = ui.TextLine()
			self.contentText.SetParent(self.base)
			self.contentText.AddFlag("attach")
			self.contentText.AddFlag("not_pick")
			self.contentText.SetText(localeinfo.WIKI_MONSTERINFO_DROPLISTOF % nonplayer.GetMonsterName(self.vnum))
			if localeinfo.IsARABIC():
				self.contentText.SetHorizontalAlignCenter()
				self.contentText.SetPosition(250,\
										1 + 20 / 2 - self.contentText.GetTextSize()[1] / 2 - 1)
				
				self.contentText.SetPackedFontColor(0xfffad390)
				#self.contentText.SetHorizontalAlignRight()
			else:
				self.contentText.SetPosition(49 + 401 / 2 - self.contentText.GetTextSize()[0] / 2,\
										1 + 20 / 2 - self.contentText.GetTextSize()[1] / 2 - 1)
			self.contentText.Show()
			
			self.originText = ui.TextLine()
			self.originText.SetParent(self.base)
			self.originText.AddFlag("attach")
			self.originText.AddFlag("not_pick")
			self.originText.SetText("")
			if localeinfo.IsARABIC():
				self.originText.SetPosition(451 + 210 / 2 - self.originText.GetTextSize()[0] / 2,\
											22 + 66 / 2 - self.originText.GetTextSize()[1] / 2 - 1)
			else:
				self.originText.SetPosition(451 + 89 / 2 - self.originText.GetTextSize()[0] / 2,\
											22 + 66 / 2 - self.originText.GetTextSize()[1] / 2 - 1)
			self.originText.Show()

			# Location panel in the right column (mirrors the chest list view's
			# origin panel). Lists the maps this mob/boss/stone spawns on; hovering
			# a row shows the minimap atlas + dots in the tooltip. Data is local
			# (game_data.mobSpawnDict) so we can ParseTextlines eagerly here.
			self.originInfo = WikiItemOriginInfo(self.vnum, False, 85, 58, parent, True)
			self.originInfo.SetParent(self.base)
			self.originInfo.AddFlag("attach")
			self.originInfo.SetPosition(451 + 2, 22 + 4)
			self.originInfo.Show()
			self.originInfo.ParseTextlines()

			self.SetSize(self.base.GetWidth(), self.base.GetHeight())
		
		def __del__(self):
			if wiki.GetBaseClass():
				wiki.GetBaseClass().objList.pop(long(id(self)))
			
			ui.Window.__del__(self)


		def __GenerateMultiLine(self, text, maxWidth):
			currText = self.__GenerateSingleLine()
			textHolder = []
			
			tempText = ui.TextLine()
			tempText.Hide()
			
			splt = text.split(" ")
			currText.SetHorizontalAlignCenter()
			currText.SetText(splt[0])
			splt = splt[1:]
			for i in splt:
				tempText.SetHorizontalAlignCenter()
				tempText.SetText(" " + i)
				if tempText.GetTextSize()[0] + currText.GetTextSize()[0] > maxWidth:
					currText.AdjustSize()
					textHolder.append(currText)
					currText = self.__GenerateSingleLine()
					currText.SetHorizontalAlignCenter()
					currText.SetText(i)
				else:
					currText.SetHorizontalAlignCenter()
					currText.SetText(currText.GetText() + " " + i)
			
			textHolder.append(currText)
			return textHolder
		
		def __GenerateSingleLine(self):
			text = ui.TextLine()
			text.SetParent(self.base)
			text.SetHorizontalAlignCenter()
			text.Show()
			return text
		
		def NoticeMe(self):
			lst = wiki.GetMobInfo(self.vnum)
			if not lst:
				return

			self.originText.SetPosition(451 + 89 / 2 - self.originText.GetTextSize()[0] / 2, 22 + 66 / 2 - self.originText.GetTextSize()[1] / 2 - 1)
			self.originText.Show()

			sizeLst = []
			orderedLst = []

			for i in lst:
				if i[0] < wiki.CONTROL_ITEM_VNUM:
					continue

				for j in orderedLst:
					if j[0] == i[0]:
						continue

				item.SelectItem(i[0])
				size = item.GetItemSize()[1]

				lastPos = 0
				for k in xrange(len(sizeLst)):
					if sizeLst[k] < size:
						break

					lastPos += 1

				sizeLst.insert(lastPos, size)
				orderedLst.insert(lastPos, i[:])

			for i in orderedLst:
				count = (i[1] if i[1] > 1 else 0)
				self.dropList.AddItem(i[0], count)

		def OnRender(self):
			if self.additionalLoaded:
				return

			if wiki.IsSet(self.vnum, True) or self.parent.loadFrom == self.parent.loadTo:
				self.additionalLoaded = True
				
				self.modelView.SetModel(self.vnum)
				self.modelView.Show()
				
				wiki.LoadInfo(long(id(self)), self.vnum, True)
	
	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 5
	SCROLL_SPEED = 50
	ITEM_LOAD_PER_UPDATE = 2
	
	def __init__(self):
		ui.Window.__init__(self)
		
		self.toolTip = uitooltip.ItemToolTip()
		
		self.SetSize(*mainBoardSize)
		
		self.elements = []
		self.scrollBar = None
		
		self.isOpened = False
		self.loadFrom = 0
		self.loadTo = 0
		
		self.mobtypes = 0
		self.fromlvl = 0
		self.tolvl = 0
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(541, self.GetHeight() - 15)
		self.peekWindow.SetPosition(5, 5)

		if not app.USE_CLIP_MASK:
			self.peekWindow.SetInsideRender(True)

		self.peekWindow.Show()

		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")

		if app.USE_CLIP_MASK:
			self.scrollBoard.SetClippingMaskWindow(self.peekWindow)

		self.scrollBoard.Show()

		self.RegisterScrollBar()
	
	def OpenWindow(self):
		wndMgr.Show(self.hWnd)
	
	def Show(self, mobtypes, fromlvl, tolvl):
		wndMgr.Show(self.hWnd)
		
		isChanged = True if not (mobtypes == self.mobtypes and\
								fromlvl == self.fromlvl and tolvl == self.tolvl) else False
		
		self.mobtypes = mobtypes
		self.fromlvl = fromlvl
		self.tolvl = tolvl
		self.loadTo = wiki.LoadClassMobs(mobtypes, fromlvl, tolvl)
		
		if not self.isOpened:
			self.isOpened = True
			self.loadFrom = 0
		
		if self.loadFrom > self.loadTo or isChanged:
			del self.elements[:]
			self.loadFrom = 0
			
			self.scrollBoard.SetSize(0, 0)
			self.UpdateScrollbar()
	
	def Hide(self):
		wndMgr.Hide(self.hWnd)
	
	def OnOverIn(self, vnum, render):
		if not self.toolTip:
			return
		
		self.toolTip.ClearToolTip()
		self.toolTip.AddItemData(vnum, [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)], 0, noRender = render)
		self.toolTip.AppendWikiAccessoryMaterials(vnum)

	def OnOverOut(self):
		if not self.toolTip:
			return
		
		self.toolTip.Hide()

	def OnRightDown(self, itemVnum = 0):
		if itemVnum == 0:
			return
		
		if app.ENABLE_RENDER_TARGET and\
			app.IsPressed(app.DIK_LSHIFT):
				if uiRenderTarget.IsCanShowItems(itemVnum):
					interfaceHandler = systemSetting.GetInterfaceHandler()
					if interfaceHandler:
						interfaceHandler.OpenRenderTargetWindow(0,itemVnum)

	def OnUpdate(self):
		if self.loadFrom < self.loadTo:
			for i in wiki.ChangePage(self.loadFrom, min(self.loadTo, self.loadFrom + self.ITEM_LOAD_PER_UPDATE), True):
				self.AddItem(i)
				self.loadFrom += 1
	
	def AddItem(self, vnum):
		for i in self.elements:
			if vnum == i.vnum:
				return None
		
		tmp = self.WikiItem(vnum, self)
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")
		
		addPadding = 0
		totalElem = len(self.elements)
		
		if totalElem > 0:
			lastIndex = 0
			
			for i in xrange(totalElem):
				if self.elements[i].vnum < tmp.vnum:
					break
				
				lastIndex += 1
			
			self.elements.insert(lastIndex, tmp)
			totalElem += 1
			
			for i in xrange(lastIndex, totalElem):
				self.elements[i].SetPosition(0,\
						(0 if i ==0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))
			
			addPadding = self.ELEM_PADDING
		else:
			self.elements.append(tmp)
		
		tmp.Show()
		
		self.scrollBoard.SetSize(tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.UpdateScrollbar()
		
		return tmp
	
	def OnRunMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1,\
								self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

if app.USE_EXTENDED_WIKI_CRAFT:
	class CraftPeekWindow(ui.Window):
		ELEM_X_PADDING = 0
		ELEM_PADDING = 0
		SCROLL_SPEED = 25
		ELEM_PER_LINE = 11

		def __init__(self, main_parent, parent, width, height, sendParent = True):
			ui.Window.__init__(self)

			self.SetSize(width, height)

			self.main_parent = proxy(main_parent)
			self.parent = proxy(parent)
			self.sendParent = sendParent

			self.elements = []
			self.posMap = {}
			self.scrollBar = None

			self.mOverInEvent = None
			self.mOverOutEvent = None
			self.mOnRightEvent = None
			self.mOnLeftEvent = None

			# self.peekWindow = ui.Bar()
			self.peekWindow = ui.Window()
			self.peekWindow.SetParent(self)
			# self.peekWindow.SetColor(0xFFFFFFFF)
			self.peekWindow.AddFlag("attach")
			self.peekWindow.AddFlag("not_pick")
			# self.peekWindow.SetSize(width - (12 if localeinfo.IsARABIC() else 6), self.GetHeight())
			self.peekWindow.SetSize(width, self.GetHeight())

			# if localeinfo.IsARABIC():
				# self.peekWindow.SetInsideRender(True, True)

			# self.peekWindow.SetPosition(6 if localeinfo.IsARABIC() else 3, 0)
			self.peekWindow.SetPosition(0, 0)
			self.peekWindow.Show()

			self.scrollBoard = ui.Window()
			self.scrollBoard.SetParent(self.peekWindow)
			self.scrollBoard.AddFlag("ltr")
			self.scrollBoard.AddFlag("attach")
			self.scrollBoard.AddFlag("not_pick")
			self.scrollBoard.SetSize(0, 0)
			self.scrollBoard.Show()

			if app.USE_CLIP_MASK:
				self.scrollBoard.SetSubClippingMaskWindow(self.peekWindow)

		def AddItem(self, num, materials_len, vnum, count):
			if not self.scrollBar:
				self.RegisterScrollBar()

			tmp = ui.ExpandedImageBox()
			tmp.SetParent(self.scrollBoard)
			tmp.LoadImage("d:/ymir work/ui/wiki/craft_material_slot.png")
			tmp.SetPosition(13 + (num * (14 if materials_len else 12)) + (num * tmp.GetWidth()), 3)

			if app.USE_CLIP_MASK:
				tmp.SetSubClippingMaskWindow(self.peekWindow)

			tmp.Show()

			tmp2 = ui.ExpandedImageBox()
			tmp2.SetParent(self.scrollBoard)
			tmp2.LoadImage("d:/ymir work/ui/wiki/reward_count.png")
			tmp2.SetScale(0.8, 0.7)
			(x, y) = tmp.GetLocalPosition()
			tmp2.SetPosition(x + 6, y + tmp.GetHeight() + 2)

			if app.USE_CLIP_MASK:
				tmp2.SetSubClippingMaskWindow(self.peekWindow)

			tmp2.Show()

			tmp3 = ui.TextLine()
			tmp3.SetParent(tmp2)
			tmp3.SetPosition(tmp2.GetWidth() / 2, 0)
			tmp3.SetHorizontalAlignCenter()
			# tmp3.SetHorizontalAlignArabic()
			tmp3.SetFontName("Tahoma:12")
			tmp3.SetText(str(count))

			if app.USE_CLIP_MASK:
				tmp3.SetSubClippingMaskWindow(self.peekWindow)

			tmp3.Show()

			if vnum:
				tmp4 = ui.ExpandedImageBox()
				tmp4.SetParent(tmp)
				tmp4.SetPosition(4, 4)
				item.SelectItem(vnum)
				tmp4.LoadImage(item.GetIconImageFileName())
				tmp4.SetStringEvent("MOUSE_OVER_IN", self.mOverInEvent, vnum)
				tmp4.SetStringEvent("MOUSE_OVER_OUT", self.mOverOutEvent)
				tmp4.SetStringEvent("MOUSE_RIGHT_DOWN", self.mOnRightEvent, vnum)
				tmp4.SetStringEvent("MOUSE_LEFT_DOWN", self.mOnLeftEvent, self.main_parent, vnum)

				if app.USE_CLIP_MASK:
					tmp4.SetSubClippingMaskWindow(self.peekWindow)

				tmp4.Show()

				self.elements.append((tmp, tmp2, tmp3, tmp4))
			else:
				self.elements.append((tmp, tmp2, tmp3))

			self.scrollBoard.SetSize(max(self.peekWindow.GetWidth(), 26 + (num * (14 if materials_len else 12)) + ((num + 1) * tmp.GetWidth())), self.peekWindow.GetHeight())

			self.UpdateScrollbar()
			return tmp

		def OnRunMouseWheel(self, length):
			if self.peekWindow.IsInPosition():
				if self.scrollBar and self.scrollBar.IsShow():
					self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
					return True

			return False

		def OnScrollBar(self, fScale):
			if localeinfo.IsARABIC():
				curr = min(0, max(math.ceil((self.scrollBoard.GetWidth() - self.peekWindow.GetWidth()) * fScale * -1.0), -self.scrollBoard.GetWidth() + self.peekWindow.GetWidth()))
			else:
				curr = min(0, max(math.ceil((self.scrollBoard.GetWidth() - self.peekWindow.GetWidth()) * fScale * -1.0), -self.scrollBoard.GetWidth() + self.peekWindow.GetWidth()))

			self.scrollBoard.SetPosition(curr, 0)

		def ChangeScrollbar(self):
			if not self.scrollBar:
				return

			if self.scrollBoard.GetWidth() <= self.GetWidth():
				self.scrollBar.Hide()
			else:
				self.scrollBar.SetScale(self.GetWidth(), self.scrollBoard.GetWidth())
				self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[0]), (self.scrollBoard.GetWidth() - self.peekWindow.GetWidth())))
				self.scrollBar.Show()

		def UpdateScrollbar(self, val = 0):
			curr = min(0, max(self.scrollBoard.GetLocalPosition()[0] + val, -self.scrollBoard.GetWidth() + self.peekWindow.GetWidth()))
			self.scrollBoard.SetPosition(curr, 0)

			self.ChangeScrollbar()

		def RegisterScrollBar(self):
			self.scrollBar = WikiScrollBar(True)
			self.scrollBar.SetParent(self)
			# self.scrollBar.SetPosition(0, self.peekWindow.GetHeight() - 8)
			# self.scrollBar.SetSize(self.peekWindow.GetWidth() + 6, 8)
			self.scrollBar.SetPosition(0, self.peekWindow.GetHeight() - 8)
			self.scrollBar.SetSize(self.peekWindow.GetWidth(), 8)
			self.scrollBar.SetScrollEvent(self.OnScrollBar)
			self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
			self.scrollBar.Hide()

			self.ChangeScrollbar()

	class WikiItemCraftWindow(ui.Window):
		class WikiItem(ui.Window):
			def __init__(self, npc_vnum, index, parent):
				ui.Window.__init__(self)

				self.craftDict = game_data.craftingDict[npc_vnum][index]

				self.parent = proxy(parent)
				self.index = index
				self.vnum = index

				wikiBase = wiki.GetBaseClass()

				if id(self) not in wikiBase.objList:
					wikiBase.objList[long(id(self))] = proxy(self)

				self.additionalLoaded = False

				self.base = ui.ExpandedImageBox()
				self.base.SetParent(self)
				self.base.AddFlag("attach")
				self.base.AddFlag("not_pick")
				self.base.LoadImage("d:/ymir work/ui/wiki/craft_detail.png")
				self.base.Show()

				self.resultTitleWnd = ui.Window()
				self.resultTitleWnd.SetParent(self.base)
				self.resultTitleWnd.SetPosition(1, 1)
				self.resultTitleWnd.SetSize(99, 22)
				self.resultTitleWnd.Show()

				self.resultTitleWndText = ui.TextLine()
				self.resultTitleWndText.SetParent(self.resultTitleWnd)
				self.resultTitleWndText.SetPosition(99 / 2, 4)
				self.resultTitleWndText.SetHorizontalAlignCenter()
				self.resultTitleWndText.SetText(localeinfo.UI_WIKI_CRAFT_RESULT)
				self.resultTitleWndText.Show()

				self.rewardItemImg = ui.ExpandedImageBox()
				self.rewardItemImg.SetParent(self.base)
				self.rewardItemImg.SetPosition(21, 26)
				self.rewardItemImg.LoadImage("d:/ymir work/ui/wiki/craft_reward_slot.png")
				self.rewardItemImg.Show()

				item.SelectItem(self.craftDict['reward_item'][0])
				rewardIcon = item.GetIconImageFileName()

				self.rewardItemIcon = ui.ExpandedImageBox()
				self.rewardItemIcon.SetParent(self.rewardItemImg)
				self.rewardItemIcon.SetPosition(8, 8)
				self.rewardItemIcon.LoadImage(rewardIcon)
				self.rewardItemIcon.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.parent.OnOverIn), self.craftDict['reward_item'][0])
				self.rewardItemIcon.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.parent.OnOverOut))
				self.rewardItemIcon.SetStringEvent("MOUSE_RIGHT_DOWN", ui.__mem_func__(self.parent.OnRightDown), self.craftDict['reward_item'][0])
				self.rewardItemIcon.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.parent.OnLeftDown), self.parent, self.craftDict['reward_item'][0])
				self.rewardItemIcon.Show()

				self.rewardCountImg = ui.ExpandedImageBox()
				self.rewardCountImg.SetParent(self.base)
				self.rewardCountImg.SetPosition(27, 26 + self.rewardItemImg.GetHeight() + 4)
				self.rewardCountImg.LoadImage("d:/ymir work/ui/wiki/reward_count.png")
				self.rewardCountImg.Show()

				self.rewardCountText = ui.TextLine()
				self.rewardCountText.SetParent(self.rewardCountImg)
				self.rewardCountText.SetPosition(self.rewardCountImg.GetWidth() / 2, 2)
				self.rewardCountText.SetHorizontalAlignCenter()
				self.rewardCountText.SetText(str(self.craftDict['reward_item'][1]))
				self.rewardCountText.Show()

				self.materialsTitleWnd = ui.Window()
				self.materialsTitleWnd.SetParent(self.base)
				self.materialsTitleWnd.SetPosition(102, 1)
				self.materialsTitleWnd.SetSize(337, 22)
				self.materialsTitleWnd.Show()

				self.materialsTitleWndText = ui.TextLine()
				self.materialsTitleWndText.SetParent(self.materialsTitleWnd)
				self.materialsTitleWndText.SetPosition(337 / 2, 4)
				self.materialsTitleWndText.SetHorizontalAlignCenter()
				self.materialsTitleWndText.SetText(localeinfo.UI_WIKI_CRAFT_REQUIRMENT)
				self.materialsTitleWndText.Show()

				self.materialsList = CraftPeekWindow(parent, self, 337, 132)
				self.materialsList.AddFlag("attach")
				self.materialsList.SetParent(self.base)
				self.materialsList.SetPosition(102, 24)
				self.materialsList.mOverInEvent = ui.__mem_func__(self.parent.OnOverIn)
				self.materialsList.mOverOutEvent = ui.__mem_func__(self.parent.OnOverOut)
				self.materialsList.mOnRightEvent = ui.__mem_func__(self.parent.OnRightDown)
				self.materialsList.mOnLeftEvent = ui.__mem_func__(self.parent.OnLeftDown)
				self.materialsList.Show()

				self.gemIcon = ui.ExpandedImageBox()
				self.gemIcon.SetParent(self.base)
				self.gemIcon.SetPosition(107, 132 + 4 + 27)
				self.gemIcon.LoadImage("d:/ymir work/ui/game/cube/cube_gem_icon.sub")
				self.gemIcon.Show()

				self.gemTextBG = ui.ExpandedImageBox()
				self.gemTextBG.SetParent(self.base)
				self.gemTextBG.SetPosition(107 + 16, 132 + 4 + 24)
				self.gemTextBG.LoadImage("d:/ymir work/ui/game/cube/cube_yang_textbg.sub")
				self.gemTextBG.Show()

				self.gemText = ui.TextLine()
				self.gemText.SetParent(self.gemTextBG)
				self.gemText.SetPosition(self.gemTextBG.GetWidth() / 2, 2)
				self.gemText.SetHorizontalAlignCenter()
				self.gemText.Show()

				self.yangIcon = ui.ExpandedImageBox()
				self.yangIcon.SetParent(self.base)
				self.yangIcon.SetPosition(107 + 110, 132 + 4 + 26)
				self.yangIcon.LoadImage("d:/ymir work/ui/game/cube/cube_yang_icon.sub")
				self.yangIcon.Show()

				self.yangTextBG = ui.ExpandedImageBox()
				self.yangTextBG.SetParent(self.base)
				self.yangTextBG.SetPosition(107 + 110 + 16, 132 + 4 + 24)
				self.yangTextBG.LoadImage("d:/ymir work/ui/game/cube/cube_yang_textbg.sub")
				self.yangTextBG.Show()

				self.yangText = ui.TextLine()
				self.yangText.SetParent(self.yangTextBG)
				self.yangText.SetPosition(self.yangTextBG.GetWidth() / 2, 2)
				self.yangText.SetHorizontalAlignCenter()
				self.yangText.Show()

				self.percentageIcon = ui.ExpandedImageBox()
				self.percentageIcon.SetParent(self.base)
				self.percentageIcon.SetPosition(107 + 110 + 110, 132 + 4 + 25)
				self.percentageIcon.LoadImage("d:/ymir work/ui/wiki/success_percentage_craft.png")
				self.percentageIcon.Show()

				self.percentageTextBG = ui.ExpandedImageBox()
				self.percentageTextBG.SetParent(self.base)
				self.percentageTextBG.SetPosition(107 + 110 + 110 + 17, 132 + 4 + 24)
				self.percentageTextBG.LoadImage("d:/ymir work/ui/game/cube/cube_yang_textbg.sub")
				self.percentageTextBG.Show()

				self.percentageText = ui.TextLine()
				self.percentageText.SetParent(self.percentageTextBG)
				self.percentageText.SetPosition(self.percentageTextBG.GetWidth() / 2, 2)
				self.percentageText.SetHorizontalAlignCenter()
				self.percentageText.Show()

				self.originTitleWnd = ui.Window()
				self.originTitleWnd.SetParent(self.base)
				self.originTitleWnd.SetPosition(440, 1)
				self.originTitleWnd.SetSize(100, 22)
				self.originTitleWnd.Show()

				self.originTitleWndText = ui.TextLine()
				self.originTitleWndText.SetParent(self.originTitleWnd)
				self.originTitleWndText.SetPosition(100 / 2, 4)
				self.originTitleWndText.SetHorizontalAlignCenter()
				self.originTitleWndText.SetText(localeinfo.UI_WIKI_CRAFT_ORIGIN)
				self.originTitleWndText.Show()

				self.originInfoParsed = False

				self.originInfo = WikiItemOriginInfo(self.craftDict['reward_item'][0], False, 100, 157, parent)
				self.originInfo.SetParent(self.base)
				self.originInfo.AddFlag("attach")
				self.originInfo.SetPosition(440, 24)
				self.originInfo.Show()

				self.SetSize(self.base.GetWidth(), self.base.GetHeight())

			def __del__(self):
				if wiki.GetBaseClass():
					wiki.GetBaseClass().objList.pop(long(id(self)))

				ui.Window.__del__(self)

			def NoticeMe(self):
				if not self.originInfoParsed:
					self.originInfoParsed = True
					self.originInfo.ParseTextlines()

				materials_len = len(self.craftDict['material_list']) / 2
				self.craftDict['material_list']

				j = 0

				for i in xrange(materials_len if materials_len > 6 else 6):
					if i < materials_len:
						self.materialsList.AddItem(i, materials_len, self.craftDict['material_list'][j], self.craftDict['material_list'][j + 1])
						j += 2
					else:
						self.materialsList.AddItem(i, materials_len, 0, 0)

				self.gemText.SetText("{}".format(self.craftDict['price_gem']))
				self.yangText.SetText(localeinfo.NumToStr(self.craftDict['price_yang']))
				self.percentageText.SetText("{}%".format(self.craftDict['success_percentage']))

			def OnRender(self):
				if self.additionalLoaded:
					return

				if wiki.IsSet(self.craftDict['reward_item'][0], False) or self.parent.loadFrom == self.parent.loadTo:
					self.additionalLoaded = True
					wiki.LoadInfo(long(id(self)), self.craftDict['reward_item'][0], False)

		"""Static values!
			Please dont touch on them."""
		ELEM_PADDING = 5
		SCROLL_SPEED = 50
		CRAFT_LOAD_PER_UPDATE = 2

		def __init__(self):
			ui.Window.__init__(self)

			self.toolTip = uitooltip.ItemToolTip()

			self.SetSize(*mainBoardSize)

			self.elements = []
			self.scrollBar = None

			self.isOpened = False

			self.npc_vnum = 0

			self.loadIndexList = []

			self.loadFrom = 0
			self.loadTo = 0

			self.peekWindow = ui.Window()
			self.peekWindow.SetParent(self)
			self.peekWindow.AddFlag("attach")
			self.peekWindow.AddFlag("not_pick")
			self.peekWindow.SetSize(541, self.GetHeight() - 15)
			self.peekWindow.SetPosition(5, 5)

			if not app.USE_CLIP_MASK:
				self.peekWindow.SetInsideRender(True)

			self.peekWindow.Show()

			self.scrollBoard = ui.Window()
			self.scrollBoard.SetParent(self.peekWindow)
			self.scrollBoard.AddFlag("attach")
			self.scrollBoard.AddFlag("not_pick")

			if app.USE_CLIP_MASK:
				# Top-level dedicated page -- no outer wiki scroll viewport
				# propagates a primary mask, so set it here. Without primary,
				# CTextLine::OnUpdate's `m_bEnableMask` guard fails for every
				# descendant (drop slots, WikiItemOriginInfo's text rows, ...)
				# and m_rMaskRect never updates -- content bleeds between
				# sections. Matches WikiMainWeaponWindow / WikiMainChestWindow.
				self.scrollBoard.SetClippingMaskWindow(self.peekWindow)

			self.scrollBoard.Show()

			self.RegisterScrollBar()

		def OpenWindow(self):
			wndMgr.Show(self.hWnd)

		def Show(self, npc_vnum, load_to, load_index_list):
			wndMgr.Show(self.hWnd)

			isChanged = True if self.npc_vnum != npc_vnum else False

			if isChanged:
				self.loadIndexList = load_index_list

			self.npc_vnum = npc_vnum
			self.loadTo = load_to

			if not self.isOpened:
				self.isOpened = True

				self.loadFrom = 0

			if self.loadFrom > self.loadTo or isChanged:
				del self.elements[:]

				self.loadFrom = 0

				self.scrollBoard.SetSize(0, 0)
				self.UpdateScrollbar()

		def Hide(self):
			wndMgr.Hide(self.hWnd)

		def OnOverIn(self, vnum):
			if not self.toolTip or not vnum:
				return

			self.toolTip.ClearToolTip()
			self.toolTip.AddItemData(vnum, [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)])
			self.toolTip.AppendWikiAccessoryMaterials(vnum)

		def OnOverOut(self):
			if not self.toolTip:
				return

			self.toolTip.Hide()

		def OnRightDown(self, itemVnum):
			if app.ENABLE_RENDER_TARGET and app.IsPressed(app.DIK_LSHIFT):
				if uiRenderTarget.IsCanShowItems(itemVnum):
					interfaceHandler = systemSetting.GetInterfaceHandler()
					if interfaceHandler:
						interfaceHandler.OpenRenderTargetWindow(0, itemVnum)

		def OnLeftDown(self, parent, itemVnum):
			if itemVnum:
				baseClass = wiki.GetBaseClass()
				if baseClass:
					baseClass.OpenSpecialPage(parent, itemVnum, False)

		def AddItem(self, index):
			for element in self.elements:
				if element.index == index:
					return None

			tmp = self.WikiItem(self.npc_vnum, index, self)
			tmp.SetParent(self.scrollBoard)
			tmp.AddFlag("attach")

			addPadding = 0
			totalElem = len(self.elements)

			if totalElem > 0:
				lastIndex = 0

				for i in xrange(totalElem):
					if self.elements[i].index < tmp.index:
						break

					lastIndex += 1

				self.elements.insert(lastIndex, tmp)
				totalElem += 1

				for i in xrange(lastIndex, totalElem):
					self.elements[i].SetPosition(0,\
							(0 if i ==0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))

				addPadding = self.ELEM_PADDING
			else:
				self.elements.append(tmp)

			tmp.Show()

			self.scrollBoard.SetSize(tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
			self.UpdateScrollbar()

			return tmp

		def OnUpdate(self):
			if self.loadFrom < self.loadTo:
				loadMax = min(self.loadTo, self.loadFrom + self.CRAFT_LOAD_PER_UPDATE)

				if loadMax:
					for i in range(self.loadFrom, loadMax):
						self.AddItem(self.loadIndexList[i])
						self.loadFrom += 1

		def OnRunMouseWheel(self, length):
			if self.peekWindow.IsInPosition():
				self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
				return True

			return False

		def OnScrollBar(self, fScale):
			curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
			self.scrollBoard.SetPosition(0, curr)

		def ChangeScrollbar(self):
			if not self.scrollBar:
				return

			if self.scrollBoard.GetHeight() <= self.GetHeight():
				self.scrollBar.Hide()
			else:
				self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
				self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
				self.scrollBar.Show()

		def UpdateScrollbar(self, val = 0):
			curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
			self.scrollBoard.SetPosition(0, curr)

			self.ChangeScrollbar()

		def RegisterScrollBar(self):
			self.scrollBar = WikiScrollBar()
			self.scrollBar.SetParent(self)
			self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
			self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
			self.scrollBar.SetScrollEvent(self.OnScrollBar)
			self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
			self.scrollBar.Show()

			self.ChangeScrollbar()

if app.USE_EXTENDED_WIKI_SHOP:
	class WikiShopWindow(ui.Window):
		class WikiItem(ui.Window):
			def __init__(self, npc_vnum, index, parent):
				ui.Window.__init__(self)

				self.npc_vnum = npc_vnum
				self.index = index

				self.parent = proxy(parent)
				self.index = index
				self.vnum = index

				wikiBase = wiki.GetBaseClass()

				if id(self) not in wikiBase.objList:
					wikiBase.objList[long(id(self))] = proxy(self)

				self.additionalLoaded = False

				self.base = ui.ExpandedImageBox()
				self.base.SetParent(self)
				self.base.AddFlag("attach")
				self.base.AddFlag("not_pick")
				self.base.LoadImage("d:/ymir work/ui/wiki/shop_detail.png")
				self.base.Show()

				self.modelTitleWnd = ui.Window()
				self.modelTitleWnd.SetParent(self.base)
				self.modelTitleWnd.SetPosition(1, 1)
				self.modelTitleWnd.SetSize(99, 22)
				self.modelTitleWnd.Show()

				self.modelTitleText = ui.TextLine()
				self.modelTitleText.SetParent(self.modelTitleWnd)
				self.modelTitleText.SetPosition(99 / 2, 4)
				self.modelTitleText.SetHorizontalAlignCenter()
				self.modelTitleText.SetText(localeinfo.UI_WIKI_SHOP_VIEW)
				self.modelTitleText.Show()

				self.modelView = WikiRenderTarget(100, 145)
				self.modelView.SetParent(self.base)
				self.modelView.SetPosition(1, 24)

				if wiki.GetBaseClass():
					self.modelView.SetMouseLeftButtonDownEvent(ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), self.parent, npc_vnum, True)

				self.modelView.Hide()

				self.shopTitleWnd = ui.Window()
				self.shopTitleWnd.SetParent(self.base)
				self.shopTitleWnd.SetPosition(102, 1)
				self.shopTitleWnd.SetSize(337, 22)
				self.shopTitleWnd.Show()

				self.shopTitleText = ui.TextLine()
				self.shopTitleText.SetParent(self.shopTitleWnd)
				self.shopTitleText.SetPosition(337 / 2, 4)
				self.shopTitleText.SetHorizontalAlignCenter()
				self.shopTitleText.SetText(game_data.shopDict[npc_vnum][index]["name"])
				self.shopTitleText.Show()

				self.dropList = ChestPeekWindow(self, 337, 145)#(self, 337, 157)
				self.dropList.ELEM_PER_LINE = 9
				self.dropList.ELEM_START_X = 5
				self.dropList.AddFlag("attach")
				self.dropList.SetParent(self.base)
				self.dropList.SetPosition(102, 24)#(107, 24)
				self.dropList.mOverInEvent = ui.__mem_func__(self.parent.OnOverIn)
				self.dropList.mOverOutEvent = ui.__mem_func__(self.parent.OnOverOut)
				self.dropList.mOnRightEvent = ui.__mem_func__(self.parent.OnRightDown)
				self.dropList.Show()

				self.originTitleWnd = ui.Window()
				self.originTitleWnd.SetParent(self.base)
				self.originTitleWnd.SetPosition(440, 1)
				self.originTitleWnd.SetSize(100, 22)
				self.originTitleWnd.Show()

				self.originTitleText = ui.TextLine()
				self.originTitleText.SetParent(self.originTitleWnd)
				self.originTitleText.SetPosition(100 / 2, 4)
				self.originTitleText.SetHorizontalAlignCenter()
				self.originTitleText.SetText(localeinfo.UI_WIKI_CRAFT_ORIGIN)
				self.originTitleText.Show()

				self.originInfoParsed = False

				self.originInfo = WikiItemOriginInfo(self.npc_vnum, False, 100, 145, parent, True)
				self.originInfo.SetParent(self.base)
				self.originInfo.AddFlag("attach")
				self.originInfo.SetPosition(440, 24)
				self.originInfo.Show()

				self.SetSize(self.base.GetWidth(), self.base.GetHeight())

			def __del__(self):
				if wiki.GetBaseClass():
					wiki.GetBaseClass().objList.pop(long(id(self)))

				ui.Window.__del__(self)

			def NoticeMe(self):
				if self.originInfoParsed:
					return

				self.originInfoParsed = True
				self.originInfo.ParseTextlines()

				_item_index = 0

				for item in game_data.shopDict[self.npc_vnum][self.index]["items"]:
					self.dropList.AddItem(item[0], item[1], self.index, _item_index)
					_item_index += 1

			def OnRender(self):
				if self.additionalLoaded:
					return

				if wiki.IsSet(self.npc_vnum, True) or self.parent.loadFrom == self.parent.loadTo:
					self.modelView.SetModel(self.npc_vnum)
					self.modelView.Show()

					self.additionalLoaded = True
					wiki.LoadInfo(long(id(self)), self.npc_vnum, True)

		"""Static values!
			Please dont touch on them."""
		ELEM_PADDING = 5
		SCROLL_SPEED = 50
		SHOP_LOAD_PER_UPDATE = 2

		def __init__(self):
			ui.Window.__init__(self)

			self.toolTip = uitooltip.ItemToolTip()

			self.SetSize(*mainBoardSize)

			self.elements = []
			self.scrollBar = None

			self.isOpened = False

			self.npc_vnum = 0

			self.loadIndexList = []

			self.loadFrom = 0
			self.loadTo = 0

			self.peekWindow = ui.Window()
			self.peekWindow.SetParent(self)
			self.peekWindow.AddFlag("attach")
			self.peekWindow.AddFlag("not_pick")
			self.peekWindow.SetSize(541, self.GetHeight() - 15)
			self.peekWindow.SetPosition(5, 5)

			if not app.USE_CLIP_MASK:
				self.peekWindow.SetInsideRender(True)

			self.peekWindow.Show()

			self.scrollBoard = ui.Window()
			self.scrollBoard.SetParent(self.peekWindow)
			self.scrollBoard.AddFlag("attach")
			self.scrollBoard.AddFlag("not_pick")

			if app.USE_CLIP_MASK:
				# Top-level dedicated page -- no outer wiki scroll viewport
				# propagates a primary mask, so set it here. Without primary,
				# CTextLine::OnUpdate's `m_bEnableMask` guard fails for every
				# descendant (drop slots, WikiItemOriginInfo's text rows, ...)
				# and m_rMaskRect never updates -- content bleeds between
				# sections. Matches WikiMainWeaponWindow / WikiMainChestWindow.
				self.scrollBoard.SetClippingMaskWindow(self.peekWindow)

			self.scrollBoard.Show()

			self.RegisterScrollBar()

		def OpenWindow(self):
			wndMgr.Show(self.hWnd)

		def Show(self, npc_vnum, load_to, load_index_list):
			wndMgr.Show(self.hWnd)

			isChanged = True if self.npc_vnum != npc_vnum else False

			if isChanged:
				self.loadIndexList = load_index_list

			self.npc_vnum = npc_vnum
			self.loadTo = load_to

			if not self.isOpened:
				self.isOpened = True

				self.loadFrom = 0

			if self.loadFrom > self.loadTo or isChanged:
				del self.elements[:]

				self.loadFrom = 0

				self.scrollBoard.SetSize(0, 0)
				self.UpdateScrollbar()

		def Hide(self):
			wndMgr.Hide(self.hWnd)

		def OnOverIn(self, vnum, metinSlot, _shop_index = None, _item_index = None):
			if not self.toolTip or not vnum:
				return

			self.toolTip.ClearToolTip()
			self.toolTip.AddItemData(vnum, metinSlot)

			if _shop_index != None and _item_index != None:
				self.toolTip.isShopItemNpc = True

				_price_type = game_data.shopDict[self.npc_vnum][_shop_index]["items"][_item_index][2]
				if _price_type == 1:
					if app.ENABLE_CHEQUE_SYSTEM:
						self.toolTip.AppendPrice(game_data.shopDict[self.npc_vnum][_shop_index]["items"][_item_index][3][0][1], 0)
					else:
						self.toolTip.AppendPrice(game_data.shopDict[self.npc_vnum][_shop_index]["items"][_item_index][3][0][1])
				elif _price_type == 2:
					self.toolTip.AppendPriceBySecondaryCoin(game_data.shopDict[self.npc_vnum][_shop_index]["items"][_item_index][3][0][1], 0)
				elif app.ENABLE_SHOPEX_RENEWAL:
					if _price_type == 5:
						_price = game_data.shopDict[self.npc_vnum][_shop_index]["items"][_item_index][3][0][1]
						self.toolTip.AppendTextLine(localeinfo.TOOLTIP_BUYPRICE % (localeinfo.NumberToGayaString(_price)), self.toolTip.GetPriceColor(_price))
					else:
						if app.SHOPEX_RENEWAL_EXTEND_ITEM_VNUM_PRICES:
							_have_title = False

							for price in game_data.shopDict[self.npc_vnum][_shop_index]["items"][_item_index][3]:
								if not _have_title:
									_have_title = True
									self.toolTip.AddShopEXItem(price[0], price[1])
									continue

								self.toolTip.AddShopEXItem(price[0], price[1], True)
						else:
							self.toolTip.AddShopEXItem(game_data.shopDict[self.npc_vnum][_shop_index]["items"][_item_index][3][0][0], game_data.shopDict[self.npc_vnum][_shop_index]["items"][_item_index][3][0][1])

				AppendShopStockLine(self.toolTip, game_data.shopDict[self.npc_vnum][_shop_index]["items"][_item_index])

		def OnOverOut(self):
			if not self.toolTip:
				return

			self.toolTip.Hide()

		def OnRightDown(self, itemVnum):
			if app.ENABLE_RENDER_TARGET and app.IsPressed(app.DIK_LSHIFT):
				if uiRenderTarget.IsCanShowItems(itemVnum):
					interfaceHandler = systemSetting.GetInterfaceHandler()
					if interfaceHandler:
						interfaceHandler.OpenRenderTargetWindow(0, itemVnum)

		def OnLeftDown(self, parent, itemVnum):
			if itemVnum:
				baseClass = wiki.GetBaseClass()
				if baseClass:
					baseClass.OpenSpecialPage(parent, itemVnum, False)

		def AddItem(self, index):
			for element in self.elements:
				if element.index == index:
					return None

			tmp = self.WikiItem(self.npc_vnum, index, self)
			tmp.SetParent(self.scrollBoard)
			tmp.AddFlag("attach")

			addPadding = 0
			totalElem = len(self.elements)

			if totalElem > 0:
				lastIndex = 0

				for i in xrange(totalElem):
					if self.elements[i].index < tmp.index:
						break

					lastIndex += 1

				self.elements.insert(lastIndex, tmp)
				totalElem += 1

				for i in xrange(lastIndex, totalElem):
					self.elements[i].SetPosition(0,\
							(0 if i ==0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))

				addPadding = self.ELEM_PADDING
			else:
				self.elements.append(tmp)

			tmp.Show()

			self.scrollBoard.SetSize(tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
			self.UpdateScrollbar()

			return tmp

		def OnUpdate(self):
			if self.loadFrom < self.loadTo:
				loadMax = min(self.loadTo, self.loadFrom + self.SHOP_LOAD_PER_UPDATE)

				if loadMax:
					for i in range(self.loadFrom, loadMax):
						self.AddItem(self.loadIndexList[i])
						self.loadFrom += 1

		def OnRunMouseWheel(self, length):
			if self.peekWindow.IsInPosition():
				self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
				return True

			return False

		def OnScrollBar(self, fScale):
			curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
			self.scrollBoard.SetPosition(0, curr)

		def ChangeScrollbar(self):
			if not self.scrollBar:
				return

			if self.scrollBoard.GetHeight() <= self.GetHeight():
				self.scrollBar.Hide()
			else:
				self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
				self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
				self.scrollBar.Show()

		def UpdateScrollbar(self, val = 0):
			curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
			self.scrollBoard.SetPosition(0, curr)

			self.ChangeScrollbar()

		def RegisterScrollBar(self):
			self.scrollBar = WikiScrollBar()
			self.scrollBar.SetParent(self)
			self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
			self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
			self.scrollBar.SetScrollEvent(self.OnScrollBar)
			self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
			self.scrollBar.Show()

			self.ChangeScrollbar()

class WikiMonsterBonusInfoWindow(ui.Window):
	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 5
	SCROLL_SPEED = 50
	ITEM_LOAD_PER_UPDATE = 2

	RACE_FLAG_TO_NAME = {
		nonplayer.RACE_FLAG_ANIMAL : localeinfo.WIKI_MONSTERINFO_RACE_ANIMAL,
		nonplayer.RACE_FLAG_UNDEAD : localeinfo.WIKI_MONSTERINFO_RACE_UNDEAD,
		nonplayer.RACE_FLAG_DEVIL : localeinfo.WIKI_MONSTERINFO_RACE_DEVIL,
		nonplayer.RACE_FLAG_HUMAN : localeinfo.WIKI_MONSTERINFO_RACE_HUMAN,
		nonplayer.RACE_FLAG_ORC : localeinfo.WIKI_MONSTERINFO_RACE_ORC,
		nonplayer.RACE_FLAG_MILGYO : localeinfo.WIKI_MONSTERINFO_RACE_MILGYO,
		nonplayer.RACE_FLAG_TREE : localeinfo.WIKI_MONSTERINFO_RACE_TREE,
	}
	SUB_RACE_FLAG_TO_NAME = {
		nonplayer.RACE_FLAG_ATT_ELEC : localeinfo.WIKI_MONSTERINFO_RACE_ELEC,
		nonplayer.RACE_FLAG_ATT_FIRE : localeinfo.WIKI_MONSTERINFO_RACE_FIRE,
		nonplayer.RACE_FLAG_ATT_ICE : localeinfo.WIKI_MONSTERINFO_RACE_ICE,
		nonplayer.RACE_FLAG_ATT_WIND : localeinfo.WIKI_MONSTERINFO_RACE_WIND,
		nonplayer.RACE_FLAG_ATT_EARTH : localeinfo.WIKI_MONSTERINFO_RACE_EARTH,
		nonplayer.RACE_FLAG_ATT_DARK : localeinfo.WIKI_MONSTERINFO_RACE_DARK,
	}
	IMMUNE_FLAG_TO_NAME = {
		nonplayer.IMMUNE_STUN : localeinfo.WIKI_MONSTERINFO_IMMUNE_STUN,
		nonplayer.IMMUNE_SLOW : localeinfo.WIKI_MONSTERINFO_IMMUNE_SLOW,
		nonplayer.IMMUNE_CURSE : localeinfo.WIKI_MONSTERINFO_IMMUNE_CURSE,
		nonplayer.IMMUNE_POISON : localeinfo.WIKI_MONSTERINFO_IMMUNE_POISON,
		nonplayer.IMMUNE_TERROR : localeinfo.WIKI_MONSTERINFO_IMMUNE_TERROR,
	}
	
	def __init__(self, vnum):
		ui.Window.__init__(self)
		
		self.SetSize(*monsterBonusInfoPageSize)
		
		self.vnum = vnum
		
		self.elements = []
		self.scrollBar = None
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(self.GetWidth() - 8 - 6, self.GetHeight() - 6)
		self.peekWindow.SetPosition(3, 3)

		if not app.USE_CLIP_MASK:
			self.peekWindow.SetInsideRender(True)

		self.peekWindow.Show()

		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")

		if app.USE_CLIP_MASK:
			self.scrollBoard.SetSubClippingMaskWindow(self.peekWindow)

		self.scrollBoard.Show()

		#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
		
		(main_race, sub_race) = self.GetRaceStrings()
		(_dmin, _dmax) = nonplayer.GetMonsterDamage(self.vnum)
		(_gMin, _gMax) = nonplayer.GetMonsterGold(self.vnum)
		
		monster_level = nonplayer.GetMonsterLevel(self.vnum)
		immune_string = self.GetImmuneString()
		damageMin = localeinfo.NumberToMoneyString(_dmin)
		damageMax = localeinfo.NumberToMoneyString(_dmax)
		goldMin = localeinfo.NumberToMoneyString(_gMin)
		goldMax = localeinfo.NumberToMoneyString(_gMax)
		
		d_page_content = [
			((localeinfo.WIKI_MONSTERINFO_LEVEL % monster_level), 0),
			((localeinfo.WIKI_MONSTERINFO_MAINRACE % main_race) + " " + (localeinfo.WIKI_MONSTERINFO_SUBRACE % sub_race), 0),
			((localeinfo.WIKI_MONSTERINFO_IMMUNE_TO % immune_string), 0),
			((localeinfo.WIKI_MONSTERINFO_DMG_HP % (damageMin, damageMax, localeinfo.NumberToMoneyString(nonplayer.GetMonsterMaxHP(self.vnum)))), 0),
			((localeinfo.WIKI_MONSTERINFO_GOLD_EXP % (goldMin, goldMax, localeinfo.NumberToMoneyString(nonplayer.GetMonsterExp(self.vnum)))), 0),
			(localeinfo.WIKI_MONSTERINFO_RESISTANCES, 0),
			((uitooltip.GET_AFFECT_STRING(item.APPLY_RESIST_SWORD, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_SWORD))), 10),
			((uitooltip.GET_AFFECT_STRING(item.APPLY_RESIST_TWOHAND, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_TWOHAND))), 10),
			((uitooltip.GET_AFFECT_STRING(item.APPLY_RESIST_DAGGER, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_DAGGER))), 10),
			((uitooltip.GET_AFFECT_STRING(item.APPLY_RESIST_BELL, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_BELL))), 10),
			((uitooltip.GET_AFFECT_STRING(item.APPLY_RESIST_FAN, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_FAN))), 10),
			((uitooltip.GET_AFFECT_STRING(item.APPLY_RESIST_BOW, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_BOW))), 10),
		]
		
		if nonplayer.IsMonsterStone(self.vnum):
			stoneCaps = game_data.GetStoneCaps(self.vnum)
			if stoneCaps:
				d_page_content.append((getattr(localeinfo, "WIKI_STONECAP_HEADER", "Max damage per hit:"), 0))
				d_page_content.append((getattr(localeinfo, "WIKI_STONECAP_WARRIOR", "Warrior: %s") % localeinfo.NumberToMoneyString(stoneCaps[0]), 10))
				d_page_content.append((getattr(localeinfo, "WIKI_STONECAP_ASSASSIN", "Assassin: %s") % localeinfo.NumberToMoneyString(stoneCaps[1]), 10))
				d_page_content.append((getattr(localeinfo, "WIKI_STONECAP_SURA", "Sura: %s") % localeinfo.NumberToMoneyString(stoneCaps[2]), 10))
				d_page_content.append((getattr(localeinfo, "WIKI_STONECAP_SHAMAN", "Shaman: %s") % localeinfo.NumberToMoneyString(stoneCaps[3]), 10))
				d_page_content.append((getattr(localeinfo, "WIKI_STONECAP_NOTE", "The 5th bonus and stone events raise your cap."), 0))
		for (text, padding) in d_page_content:
			self.AddItem(text, padding)
		
		#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
		
		self.RegisterScrollBar()
	
	def GetImmuneString(self):
		dwImmuneFlag = nonplayer.GetMonsterImmuneFlag(self.vnum)
		
		immuneflags = ""
		for i in xrange(nonplayer.IMMUNE_FLAG_MAX_NUM):
			curFlag = 1 << i
			
			if HAS_FLAG(dwImmuneFlag, curFlag):
				if self.IMMUNE_FLAG_TO_NAME.has_key(curFlag):
					immuneflags += self.IMMUNE_FLAG_TO_NAME[curFlag] + ", "
		
		immuneflags = (immuneflags[:-2] if len(immuneflags) else localeinfo.WIKI_MONSTERINFO_IMMUNE_NOTHING)
		return immuneflags
	
	def GetRaceStrings(self):
		dwRaceFlag = nonplayer.GetMonsterRaceFlag(self.vnum)
		(mainrace, subrace) = ("", "")
		
		for i in xrange(nonplayer.RACE_FLAG_MAX_NUM):
			curFlag = 1 << i
			
			if HAS_FLAG(dwRaceFlag, curFlag):
				if self.RACE_FLAG_TO_NAME.has_key(curFlag):
					mainrace += self.RACE_FLAG_TO_NAME[curFlag] + ", "
				elif self.SUB_RACE_FLAG_TO_NAME.has_key(curFlag):
					subrace += self.SUB_RACE_FLAG_TO_NAME[curFlag] + ", "
		
		if nonplayer.IsMonsterStone(self.vnum):
			mainrace += localeinfo.WIKI_MONSTERINFO_RACE_METIN + ", "
		
		mainrace = (mainrace[:-2] if len(mainrace) else localeinfo.WIKI_MONSTERINFO_NO_RACE)
		subrace = (subrace[:-2] if len(subrace) else localeinfo.WIKI_MONSTERINFO_NO_RACE)
		
		return (mainrace, subrace)
	
	def AddItem(self, text, padding = 0):
		tmp = ui.Window()
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")
		tmp.SetSize(self.GetWidth(), 15)
		
		tmp.img = ui.ExpandedImageBox()
		tmp.img.SetParent(tmp)
		tmp.img.AddFlag("attach")
		tmp.img.AddFlag("not_pick")
		tmp.img.LoadImage("d:/ymir work/ui/wiki/arrow_2.tga")
		if localeinfo.IsARABIC:
			tmp.img.SetPosition(padding +250, tmp.GetHeight() / 2 - tmp.img.GetHeight() / 2)
		else:
			tmp.img.SetPosition(padding, tmp.GetHeight() / 2 - tmp.img.GetHeight() / 2)
		if not localeinfo.IsARABIC:
			tmp.img.Show()

		tmp.txt = ui.TextLine()
		tmp.txt.SetParent(tmp)
		tmp.txt.AddFlag("attach")
		tmp.txt.AddFlag("not_pick")
		tmp.txt.SetText(text)
		if localeinfo.IsARABIC:
			tmp.txt.SetHorizontalAlignCenter()#here
			#tmp.txt.SetHorizontalAlignLeft()
			tmp.txt.SetPosition(260,\
								tmp.GetHeight() / 2 - tmp.txt.GetTextSize()[1] / 2 - 1)
		else:
			tmp.txt.SetPosition(tmp.img.GetLocalPosition()[0] + tmp.img.GetWidth() + 20,\
								tmp.GetHeight() / 2 - tmp.txt.GetTextSize()[1] / 2 - 1)
		tmp.txt.Show()
		
		addPadding = 0
		totalElem = len(self.elements)
		
		if totalElem > 0:
			lastIndex = totalElem
			
			self.elements.insert(lastIndex, tmp)
			totalElem += 1
			
			for i in xrange(lastIndex, totalElem):
				self.elements[i].SetPosition(0,\
					(0 if i == 0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))
			
			addPadding = self.ELEM_PADDING
		else:
			self.elements.append(tmp)
		
		tmp.Show()
		
		self.scrollBoard.SetSize(tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.UpdateScrollbar()
		
		return tmp
	
	def OnRunMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

# Gold (0xAARRGGBB) used by the "drops from" row hover. Module-level int --
# no module dereference at parse time, so this can't break the EPK packer.
WIKI_ORIGIN_HOVER_COLOR = 0xFFFFD700
WIKI_ORIGIN_DIM_COLOR = 0xFFB0B0B0


class WikiItemOriginInfo(ui.Window):
	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 5
	SCROLL_SPEED = 50
	ITEM_LOAD_PER_UPDATE = 2
	# Hover preview dimensions. Tooltip width = MONSTER_PREVIEW_W + 2*PAD.
	# Bumped up so the model has breathing room AND the shop "[Buy Price]"
	# rows (icon + count + item name) don't get crammed against the edge.
	MONSTER_PREVIEW_W   = 150
	MONSTER_PREVIEW_H   = 195
	MONSTER_PREVIEW_PAD = 28

	#app.USE_EXTENDED_WIKI_CRAFT: w & h
	def __init__(self, vnum, origin = False, w = -1, h = -1, _parent = None, _location = False):
		ui.Window.__init__(self)
		# self.SetColor(0xFFFFFFFF)

		self.parent = proxy(_parent) if _parent else None

		self._location = _location

		self.toolTip = uitooltip.ToolTip()

		if _location:
			self._coords = {}

		# Lazy hover-preview slots (no widget construction here -- the
		# previous attempt subclassed uitooltip.ToolTip at module level and
		# broke EPK packing. These get instantiated on first hover via
		# _ShowItemHoverTip / _ShowMonsterHoverTip below).
		self.itemHoverTip      = None  # uitooltip.ItemToolTip() (cursor-follow)
		self.monsterHoverTip   = None  # uitooltip.ToolTip() (composed, not subclassed)
		self.monsterHoverModel = None  # WikiRenderTarget child of monsterHoverTip

		if w != -1 and h != -1:
			self.SetSize(w, h)
		elif origin:
			self.SetSize(*chestItemOriginPageSize)
		else:
			self.SetSize(*itemOriginPageSize)

		self.vnum = vnum

		self.elements = {}

		# npc_vnum -> (price_type, price_data) for items sold by NPC shops.
		# Populated in ParseTextlines for the "obtained from" (non-_location)
		# panel; the hover preview looks here to render a "[Buy Price]" block
		# under the NPC render.
		self._shopSellers = {}

		# npc_vnum -> recipe dict for cube/craft NPCs that produce this vnum.
		# Same flow as _shopSellers but the hover renders the recipe's
		# material rows + yang cost instead of a buy price.
		self._cubeProducers = {}

		# row index -> zero-arg callable, for rows whose click does something
		# other than open another wiki page. Held here rather than passed to
		# the event system because __mem_func__ cannot carry a callable.
		self._clickActions = {}

		# row index -> "itemshop" / "wheel". These rows name a source, not an
		# entity, so OnOver has no vnum to preview and renders a text block.
		self._premiumRows = {}

		self.scrollBar = None

		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		# self.peekWindow.SetSize(self.GetWidth() - 8 - 6, self.GetHeight() - 6)
		self.peekWindow.SetSize(self.GetWidth() - 2, self.GetHeight() - 2)
		self.peekWindow.SetPosition(1, 1)

		if not app.USE_CLIP_MASK:
			self.peekWindow.SetInsideRender(True)

		self.peekWindow.Show()

		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")

		self.scrollBoard.Show()

		# SUB mask only -- primary mask comes from the wiki's outer
		# SetClippingMaskWindow propagation when this widget gets parented
		# into the wiki. Using primary here would block that propagation,
		# leaving rows clipped only to the local (possibly off-screen)
		# peekWindow when this widget belongs to a row scrolled out of view.
		if app.USE_CLIP_MASK:
			self.scrollBoard.SetSubClippingMaskWindow(self.peekWindow)

		self.RegisterScrollBar()

	def ParseTextlines(self):
		for element in self.elements.values():
			element.SetMouseOverInEvent(None)
			element.SetMouseOverOutEvent(None)
			element.SetOnMouseLeftButtonUpEvent(None)

			del element.txt
			del element

		self.elements = {}
		self._shopSellers = {}
		self._cubeProducers = {}
		self._clickActions = {}
		self._premiumRows = {}

		self.scrollBoard.SetSize(0, 0)

		if self.scrollBar:
			self.scrollBar.Hide()

		if self._location:
			# Prefer the comprehensive mobSpawnDict baked by tools/wiki_spawn_baker
			# (1k+ vnums across mobs/bosses/stones/npcs). Fall back to the legacy
			# npcOriginDict if our entity isn't in the baked set (covers a handful
			# of NPC vnums the baker may have missed and the existing UI relied on).
			spawnRecords = game_data.mobSpawnDict.get(self.vnum, [])

			if spawnRecords:
				# Group by map name. Each unique map becomes one clickable row.
				# We also record the map name on the element so OnOver can load
				# the right atlas for the tooltip minimap.
				byMap = {}
				for s in spawnRecords:
					m = s.get("map")
					if not m:
						continue
					byMap.setdefault(m, []).append((s.get("x", 0), s.get("y", 0)))

				# Sort by spawn count desc, then by display name for stable ordering.
				orderedMaps = sorted(
					byMap.keys(),
					key=lambda m: (-len(byMap[m]), m))

				if not hasattr(self, "_mapNames"):
					self._mapNames = []
				else:
					self._mapNames = []

				for mapName in orderedMaps:
					self._coords[len(self._mapNames)] = byMap[mapName]
					self._mapNames.append(mapName)
					self.AddItem(mapName, _by_name=True)

			elif game_data.npcOriginDict.has_key(self.vnum):
				for _index, _locations in sorted(game_data.npcOriginDict[self.vnum].items()):
					self._coords[self.vnum + _index] = _locations
					self.AddItem(_index)
		else:
			lst = wiki.GetOriginInfo(self.vnum) or []

			alreadyParsed = []

			for (vnum, isMonster) in lst:
				bAlready = False

				for i in alreadyParsed:
					if i[0] == vnum and i[1] == isMonster:
						bAlready = True
						break

				if bAlready or not vnum:
					continue

				# isMonster=True  -> mob that drops this item        -> [MONSTER]
				# isMonster=False -> chest/gacha that contains it    -> [CHEST]
				# (shop / cube rows are tagged separately below.)
				if isMonster:
					currName = nonplayer.GetMonsterName(vnum)
					rowText = "%s %s" % (localeinfo.WIKI_ORIGIN_MONSTER_TAG, currName)
				else:
					item.SelectItem(vnum)
					currName = item.GetItemName()
					rowText = "%s %s" % (localeinfo.WIKI_ORIGIN_CHEST_TAG, currName)

				alreadyParsed.append([vnum, isMonster])
				self.AddItem(rowText, is_monster = isMonster, event_vnum = vnum)

			# Shop sellers: walk every NPC shop, record the first tab+entry
			# that lists self.vnum, render as "[SHOP] NPC name". Stored price
			# is used by _ShowMonsterHoverTip to render the buy-price block.
			# Skip NPCs already in alreadyParsed (the drop origin loop above
			# can list the same NPC as a "monster" source -- e.g. a
			# blacksmith that also drops something) so each NPC appears once.
			parsedMonsters = set(
				p[0] for p in alreadyParsed if len(p) >= 2 and p[1])
			if app.USE_EXTENDED_WIKI_SHOP:
				try:
					npcOrder = sorted(game_data.shopDict.keys())
				except Exception:
					npcOrder = list(game_data.shopDict.keys())
				for npcVnum in npcOrder:
					if npcVnum in game_data.shopHiddenNpcSet:
						continue
					if npcVnum in self._shopSellers:
						continue
					if npcVnum in parsedMonsters:
						# Already rendered as a regular drop/origin row.
						# We still want the price tooltip on hover, so
						# record the price -- just don't add a duplicate row.
						pass
					tabs = game_data.shopDict[npcVnum]
					if not isinstance(tabs, dict):
						continue
					found = False
					for _tabKey, tab in tabs.items():
						for itemEntry in tab.get("items", []):
							if not itemEntry:
								continue
							try:
								if itemEntry[0] != self.vnum:
									continue
							except (IndexError, TypeError):
								continue
							priceType = itemEntry[2] if len(itemEntry) >= 3 else 1
							priceData = itemEntry[3] if len(itemEntry) >= 4 else []
							self._shopSellers[npcVnum] = (priceType, priceData)
							found = True
							break
						if found:
							break
					if not found:
						continue
					if npcVnum in parsedMonsters:
						# Price recorded for hover; row was already added.
						continue
					name = nonplayer.GetMonsterName(npcVnum) or ("#%d" % npcVnum)
					self.AddItem(
						"%s %s" % (localeinfo.WIKI_ORIGIN_SHOP_TAG, name),
						is_monster = True,
						event_vnum = npcVnum)

			# Item-opened shops (ENABLE_ITEM_SHOPS): the shop has no NPC to name,
			# so the row points at the use-item that opens it -- icon hover and a
			# click through to that item's page, like the [Combine] rows below.
			if app.ENABLE_ITEM_SHOPS:
				try:
					openerOrder = sorted(game_data.itemShopDict.keys())
				except Exception:
					openerOrder = list(game_data.itemShopDict.keys())
				for openerVnum in openerOrder:
					if [openerVnum, False] in alreadyParsed:
						continue
					shopInfo = game_data.itemShopDict[openerVnum]
					if not isinstance(shopInfo, dict):
						continue
					found = False
					for itemEntry in shopInfo.get("items", []):
						if not itemEntry:
							continue
						try:
							if itemEntry[0] != self.vnum:
								continue
						except (IndexError, TypeError):
							continue
						found = True
						break
					if not found:
						continue
					alreadyParsed.append([openerVnum, False])
					item.SelectItem(openerVnum)
					openerName = item.GetItemName() or ("#%d" % openerVnum)
					self.AddItem(
						"%s %s" % (localeinfo.WIKI_ORIGIN_SHOP_TAG, openerName),
						is_monster = False,
						event_vnum = openerVnum)

			# Cube producers: scan every NPC cube and record the recipe whose
			# reward_item matches self.vnum. Same dedup as shops -- a row is
			# only added if the NPC isn't already listed as a drop source or
			# a shop seller, but the recipe is still recorded so the hover
			# popup can render it on the existing row.
			if app.USE_EXTENDED_WIKI_CRAFT:
				shopSet = set(self._shopSellers.keys())
				try:
					cubeNpcOrder = sorted(game_data.craftingDict.keys())
				except Exception:
					cubeNpcOrder = list(game_data.craftingDict.keys())
				for npcVnum in cubeNpcOrder:
					if npcVnum in self._cubeProducers:
						continue
					recipes = game_data.craftingDict[npcVnum]
					if not isinstance(recipes, dict):
						continue
					matchingRecipe = None
					for _idx, recipe in recipes.items():
						if not isinstance(recipe, dict):
							continue
						reward = recipe.get("reward_item")
						if not reward:
							continue
						try:
							rewardVnum = int(reward[0])
						except (TypeError, ValueError, IndexError):
							continue
						if rewardVnum == self.vnum:
							matchingRecipe = recipe
							break
					if matchingRecipe is None:
						continue
					self._cubeProducers[npcVnum] = matchingRecipe
					if npcVnum in parsedMonsters or npcVnum in shopSet:
						# Recipe recorded for hover; row already exists.
						continue
					name = nonplayer.GetMonsterName(npcVnum) or ("#%d" % npcVnum)
					self.AddItem(
						"%s %s" % (localeinfo.WIKI_ORIGIN_CUBE_TAG, name),
						is_monster = True,
						event_vnum = npcVnum)

			# Item-transformation origins (ENABLE_ITEM_TRANSFORM): list every
			# material whose collected set transforms INTO this item. Each
			# material is itself an item, so the row hover shows the item
			# preview (same flow as a drop-origin item row).
			addedItems = set(p[0] for p in alreadyParsed if len(p) >= 2 and not p[1])
			try:
				transformOrder = sorted(game_data.itemTransformDict.keys())
			except Exception:
				transformOrder = list(game_data.itemTransformDict.keys())
			for matVnum in transformOrder:
				info = game_data.itemTransformDict[matVnum]
				try:
					if int(info.get("result", 0)) != self.vnum:
						continue
				except (TypeError, ValueError, AttributeError):
					continue
				if matVnum in addedItems:
					continue
				addedItems.add(matVnum)
				needCount = info.get("count", 0)
				item.SelectItem(matVnum)
				matName = item.GetItemName()
				self.AddItem(
					"%s %dx %s" % (localeinfo.WIKI_ORIGIN_TRANSFORM_TAG, needCount, matName),
					is_monster = False,
					event_vnum = matVnum)

			# Bundle-box origins: boxes whose category/guaranteed rolls can
			# hand out this item (game_data.bundleBoxDict, wiki Task 6 bake).
			# Reuses the SAME [CHEST] tag the drop-origin loop above uses for
			# is_monster=False container rows -- a bundle box IS a chest/gacha
			# style container, just picked client-side instead of server-
			# rolled, so no new locale key. addedItems already dedupes against
			# a box vnum the server itself listed as a chest origin.
			if app.USE_EXTENDED_WIKI:
				import ingamewikireverse
				for boxVnum in ingamewikireverse.GetBundleSources(self.vnum):
					if boxVnum in addedItems:
						continue
					addedItems.add(boxVnum)
					item.SelectItem(boxVnum)
					boxName = item.GetItemName() or ("#%d" % boxVnum)
					self.AddItem(
						"%s %s" % (localeinfo.WIKI_ORIGIN_CHEST_TAG, boxName),
						is_monster = False,
						event_vnum = boxVnum)

			# Premium sources. Both catalogs are server-pushed rather than baked,
			# so an empty index just means the prefetch hasn't landed yet -- the
			# row appears the next time this page is built. Neither row navigates
			# to another wiki page, hence click_action instead of event_vnum.
			if app.USE_EXTENDED_WIKI_USAGE:
				import ingamewikipremium

				if app.ENABLE_ITEMSHOP and ingamewikipremium.GetItemShopEntries(self.vnum):
					self._premiumRows[len(self.elements)] = "itemshop"
					self.AddItem(
						ingamewikipremium.GetItemShopRowText(),
						is_monster = False,
						event_vnum = 0,
						click_action = lambda v = self.vnum: ingamewikipremium.OpenItemShopSearch(v))

				if app.USE_WHEEL_OF_FORTUNE and ingamewikipremium.GetWheelEntries(self.vnum):
					self._premiumRows[len(self.elements)] = "wheel"
					self.AddItem(
						ingamewikipremium.GetWheelRowText(),
						is_monster = False,
						event_vnum = 0,
						click_action = ingamewikipremium.OpenWheelView)

			try:
				import ingamewikigemshop
				gemMarketOffers = ingamewikigemshop.GetMarketEntries(self.vnum)
			except Exception:
				gemMarketOffers = []
			if gemMarketOffers:
				self._premiumRows[len(self.elements)] = "gemshop"
				self.AddItem(
					ingamewikigemshop.GetMarketRowText(),
					is_monster = False,
					event_vnum = 0,
					click_action = ingamewikigemshop.OpenWikiPage)

	def ShowPremiumTip(self, source, _in):
		if not _in:
			self.toolTip.HideToolTip()
			return

		if source == "gemshop":
			import ingamewikigemshop
			title = ingamewikigemshop.GetMarketRowText()
			lines = ingamewikigemshop.GetMarketTooltipLines(self.vnum)
		elif source == "itemshop":
			import ingamewikipremium
			title = ingamewikipremium.GetItemShopRowText()
			lines = ingamewikipremium.GetItemShopTooltipLines(self.vnum)
		else:
			import ingamewikipremium
			title = ingamewikipremium.GetWheelRowText()
			lines = ingamewikipremium.GetWheelTooltipLines(self.vnum)

		self.toolTip.ClearToolTip()
		self.toolTip.AutoAppendTextLineAll(title, WIKI_ORIGIN_HOVER_COLOR)
		for (text, dim) in lines:
			self.toolTip.AutoAppendTextLineAll(text, WIKI_ORIGIN_DIM_COLOR if dim else ui.DEFAULT_FONT_COLOR)
		self.toolTip.ShowToolTip()

	def OnOver(self, _id, _in, _name = None, _index = None, _vnum = 0, _is_monster = False):
		if self.elements.has_key(_id):
			self.elements[_id].txt.SetPackedFontColor(WIKI_ORIGIN_HOVER_COLOR if _in else ui.DEFAULT_FONT_COLOR)

			if _id in self._premiumRows:
				self.ShowPremiumTip(self._premiumRows[_id], _in)
				return

			if self._location:
				if _in:
					self.toolTip.ClearToolTip()
					self.toolTip.AutoAppendTextLineAll(_name, WIKI_ORIGIN_HOVER_COLOR)

					# Two key formats for self._coords:
					#  - new mobSpawnDict path: key = element index (_id),
					#    map name carried in _index (string)
					#  - legacy npcOriginDict path: key = self.vnum + _index,
					#    map name resolved via GetMiniMapZoneNameByIdx
					coordList = None
					mapName = None
					if isinstance(_index, str) or isinstance(_index, unicode):
						coordList = self._coords.get(_id)
						mapName = _index
					else:
						key = self.vnum + (_index or 0)
						coordList = self._coords.get(key)

					# Embed the atlas minimap with dots if we have everything;
					# otherwise fall through to text-only coordinates.
					embedded = False
					if coordList and mapName:
						try:
							import ingamewikispawn
							embedded = ingamewikispawn.RenderMiniMapIntoTooltip(
								self.toolTip, mapName, coordList)
						except Exception:
							embedded = False

					if not embedded and coordList:
						self.toolTip.AppendSpace(5)
						for _cords in coordList:
							try:
								x = _cords["x"] if isinstance(_cords, dict) else _cords[0]
								y = _cords["y"] if isinstance(_cords, dict) else _cords[1]
							except (KeyError, TypeError, IndexError):
								continue
							self.toolTip.AppendTextLine("({}, {})".format(x, y))

					self.toolTip.ShowToolTip()
				else:
					self.toolTip.HideToolTip()
			else:
				# Non-location "drops from" row hover: show a preview.
				# Items get the canonical HyperlinkItemToolTip (icon + stats),
				# monsters get a small 3D model render. Both go through lazy
				# helpers so widget construction happens at hover-time (not
				# at import-time, which is what broke the previous attempt).
				if _in and _vnum:
					if _is_monster:
						self._ShowMonsterHoverTip(_vnum)
					else:
						self._ShowItemHoverTip(_vnum)
				else:
					self._HideHoverTips()

	def _ShowItemHoverTip(self, vnum):
		"""Show a compact icon + name + "Open Wikipedia" hint popup -- same
		layout the reverse-lookup panels use, but built by COMPOSITION here
		(plain uitooltip.ToolTip instance + manually appended children) so
		no module-level subclass is involved. Cursor-follow works because
		the base ToolTip.OnUpdate is intact."""
		try:
			if self.itemHoverTip is None:
				self.itemHoverTip = uitooltip.ToolTip(150)
			if self.monsterHoverTip is not None:
				self.monsterHoverTip.HideToolTip()

			item.SelectItem(int(vnum))
			iconPath = item.GetIconImageFileName()
			name = item.GetItemName() or ("#%d" % int(vnum))

			self.itemHoverTip.ClearToolTip()

			# Icon, centered. The image's intrinsic dimensions (32x32 for
			# jewelry, 32x64 for armor/weapons) drive layout.
			if iconPath:
				self.itemHoverTip.AppendSpace(6)
				icon = ui.ImageBox()
				icon.SetParent(self.itemHoverTip)
				icon.LoadImage(iconPath)
				iconW = icon.GetWidth() or 32
				iconH = icon.GetHeight() or 32
				icon.SetPosition(
					(self.itemHoverTip.toolTipWidth - iconW) / 2,
					self.itemHoverTip.toolTipHeight)
				icon.Show()
				self.itemHoverTip.childrenList.append(icon)
				self.itemHoverTip.toolTipHeight += iconH
				self.itemHoverTip.ResizeToolTip()

			# Item name (center-aligned via base AppendTextLine default).
			self.itemHoverTip.AppendSpace(4)
			self.itemHoverTip.AppendTextLine(name)

			# Footer: "Open Wikipedia" hint in dim grey.
			self.itemHoverTip.AppendSpace(2)
			self.itemHoverTip.AppendTextLine(localeinfo.WIKI_OPEN_HINT, 0xFFB0B0B0)

			self.itemHoverTip.ShowToolTip()
		except Exception:
			self._HideHoverTips()

	def _ShowMonsterHoverTip(self, vnum):
		"""Show a small popup with the monster's 3D model + name. Built by
		COMPOSITION (uitooltip.ToolTip instance + WikiRenderTarget child),
		not subclassing -- subclassing broke EPK packing previously."""
		try:
			# Lazy first-call construction. uitooltip.ToolTip / WikiRenderTarget
			# are both dereferenced here, not at module level.
			if self.monsterHoverTip is None:
				w = self.MONSTER_PREVIEW_W + 2 * self.MONSTER_PREVIEW_PAD
				self.monsterHoverTip = uitooltip.ToolTip(w)
				self.monsterHoverModel = WikiRenderTarget(
					self.MONSTER_PREVIEW_W, self.MONSTER_PREVIEW_H)
				self.monsterHoverModel.SetParent(self.monsterHoverTip)
				self.monsterHoverModel.Hide()

			if self.itemHoverTip is not None:
				self.itemHoverTip.HideToolTip()

			try:
				name = nonplayer.GetMonsterName(int(vnum)) or ("#%d" % int(vnum))
			except Exception:
				name = "#%d" % int(vnum)

			self.monsterHoverTip.ClearToolTip()
			self.monsterHoverModel.SetModel(int(vnum))
			# Center the render target horizontally, place at current cursor Y.
			modelX = (self.monsterHoverTip.toolTipWidth - self.MONSTER_PREVIEW_W) / 2
			self.monsterHoverTip.AppendSpace(self.MONSTER_PREVIEW_PAD / 2)
			self.monsterHoverModel.SetPosition(modelX, self.monsterHoverTip.toolTipHeight)
			self.monsterHoverModel.Show()
			# childrenList is what ClearToolTip wipes -- re-append every show.
			self.monsterHoverTip.childrenList.append(self.monsterHoverModel)
			self.monsterHoverTip.toolTipHeight += self.MONSTER_PREVIEW_H
			self.monsterHoverTip.ResizeToolTip()

			self.monsterHoverTip.AppendSpace(4)
			self.monsterHoverTip.AppendTextLine(name)

			# Shop NPC: buy-price block. Cube NPC: recipe materials + yang.
			# Both go under the model+name. If the same NPC happens to be in
			# both (a shop seller AND a cube producer for this vnum), shop
			# wins -- "buying with money" is the simpler path to surface.
			vnumKey = int(vnum)
			sellerInfo = self._shopSellers.get(vnumKey) if hasattr(self, "_shopSellers") else None
			cubeRecipe = self._cubeProducers.get(vnumKey) if hasattr(self, "_cubeProducers") else None
			if sellerInfo:
				self._AppendShopPriceLines(*sellerInfo)
			elif cubeRecipe:
				self._AppendCubeRecipeLines(cubeRecipe)

			self.monsterHoverTip.ShowToolTip()
		except Exception:
			self._HideHoverTips()

	def _AppendShopPriceLines(self, priceType, priceData):
		# Renders the "[Buy Price]" header followed by one icon+count+name
		# row per cost component. Layout for each row: small item icon on
		# the left, "<count> <name>" text right of it. Matches the dedicated
		# shop popup's appearance.
		if not priceData or self.monsterHoverTip is None:
			return
		try:
			self.monsterHoverTip.AppendSpace(6)
			# Header. localeinfo.TOOLTIP_BUYPRICE is "Price: %s" -- pass
			# empty so we just emit "Price:" / equivalent translation.
			self.monsterHoverTip.AppendTextLine(localeinfo.TOOLTIP_BUYPRICE % "")

			# Dispatch matches WikiShopWindow.OnOverIn. Each legacy type has
			# a single (something, amount) entry; ShopEX renewal carries a
			# list of (vnum, count) items.
			if priceType == 1:
				self._AppendShopPriceRow(1, priceData[0][1])
			elif priceType == 2:
				# Cheque: priceData[0] = (some_id, amount). Use cheque vnum
				# for the icon if entry[0] looks like one; otherwise fall
				# back to text-only.
				self._AppendShopPriceRow(priceData[0][0] or 0, priceData[0][1])
			elif app.ENABLE_SHOPEX_RENEWAL and priceType == 5:
				self._AppendShopPriceRow(priceData[0][0] or 0, priceData[0][1])
			else:
				# ShopEX vnum-item prices: one row per entry.
				for entry in priceData:
					if not entry or len(entry) < 2:
						continue
					self._AppendShopPriceRow(entry[0], entry[1])

			self.monsterHoverTip.ResizeToolTip()
		except Exception:
			pass

	def _AppendShopPriceRow(self, pVnum, pCount):
		# Append a single "<icon> <count> <name>" row inside the hover
		# tooltip. The icon is the item's normal inventory icon, scaled
		# down so the row stays compact.
		ICON_SIZE  = 28
		ICON_PAD_X = 18
		ROW_HEIGHT = ICON_SIZE + 6

		rowY = self.monsterHoverTip.toolTipHeight + 2

		# Resolve icon + display name. vnum 1 = yang -- format the count
		# with the money separator so big numbers stay readable.
		iconPath = ""
		name = ""
		try:
			item.SelectItem(int(pVnum))
			iconPath = item.GetIconImageFileName() or ""
			name = item.GetItemName() or ""
		except Exception:
			pass
		if not name:
			name = "#%d" % pVnum

		if pVnum == 1:
			text = "%s %s" % (localeinfo.NumberToMoneyString(pCount), name)
		else:
			text = "%d %s" % (pCount, name)

		# RTL locales read right-to-left -- mirror the row so the icon
		# anchors the right edge and the text right-aligns toward it.
		isRTL = localeinfo.IsARABIC()
		if isRTL:
			iconX = self.monsterHoverTip.toolTipWidth - ICON_PAD_X - ICON_SIZE
		else:
			iconX = ICON_PAD_X

		if iconPath:
			iconBox = ui.ExpandedImageBox()
			iconBox.SetParent(self.monsterHoverTip)
			iconBox.LoadImage(iconPath)
			# Native inventory icons are 32x32 (jewelry) up to 32x64
			# (armor/weapons). Scale down to ICON_SIZE so the row is
			# compact regardless of source dimensions.
			try:
				iconBox.SetScale(ICON_SIZE / 32.0, ICON_SIZE / 32.0)
			except Exception:
				pass
			iconBox.SetPosition(iconX, rowY)
			iconBox.Show()
			self.monsterHoverTip.childrenList.append(iconBox)

		txt = ui.TextLine()
		txt.SetParent(self.monsterHoverTip)
		# Vertically center the text against the icon (icon center at
		# rowY + ICON_SIZE/2; default font is ~12 px tall, so offset 8).
		if isRTL:
			# Arabic glyphs flow leftward from the anchor when using
			# SetHorizontalAlignLeft, so we anchor at the right (just
			# left of the icon) and the text grows toward the left edge.
			txt.SetHorizontalAlignLeft()
			txt.SetPosition(iconX - 8, rowY + 8)
		else:
			txt.SetPosition(iconX + ICON_SIZE + 8, rowY + 8)
		txt.SetText(text)
		txt.Show()
		self.monsterHoverTip.childrenList.append(txt)

		self.monsterHoverTip.toolTipHeight += ROW_HEIGHT

	def _AppendCubeRecipeLines(self, recipe):
		# Renders the cube recipe under the NPC model+name: a header,
		# one icon+count+name row per material, then a yang-cost row.
		# Reuses _AppendShopPriceRow so the icons mirror to the right side
		# under Arabic locale exactly like the shop price block does.
		if not recipe or self.monsterHoverTip is None:
			return
		try:
			self.monsterHoverTip.AppendSpace(6)
			# Reuse the cube page's "Required materials" header so the
			# wording stays consistent across the wiki.
			self.monsterHoverTip.AppendTextLine(localeinfo.UI_WIKI_CRAFT_REQUIRMENT)

			# material_list is a flat [v, c, v, c, ...] list -- walk in pairs.
			matList = recipe.get("material_list") or []
			for i in range(0, len(matList) - 1, 2):
				try:
					mVnum  = int(matList[i])
					mCount = int(matList[i + 1])
				except (TypeError, ValueError):
					continue
				if not mVnum:
					continue
				self._AppendShopPriceRow(mVnum, mCount)

			# Yang fee. vnum 1 = yang, so the row picks up the yang icon
			# and money-string formatting from _AppendShopPriceRow.
			yangCost = recipe.get("price_yang") or 0
			if yangCost:
				self._AppendShopPriceRow(1, yangCost)

			self.monsterHoverTip.ResizeToolTip()
		except Exception:
			pass

	def _HideHoverTips(self):
		if self.itemHoverTip is not None:
			try: self.itemHoverTip.HideToolTip()
			except Exception: pass
		if self.monsterHoverTip is not None:
			try: self.monsterHoverTip.HideToolTip()
			except Exception: pass
			if self.monsterHoverModel is not None:
				try: self.monsterHoverModel.Hide()
				except Exception: pass

	def OnClick(self, is_monster, event_vnum):
		if event_vnum:
			wikiBase = wiki.GetBaseClass()
			if wikiBase:
				wikiBase.OpenSpecialPage(self.parent, event_vnum, is_monster)
				# wikiBase.OpenSpecialPage(None, event_vnum, is_monster)

	def OnClickAction(self, index):
		action = self._clickActions.get(index)
		if action:
			action()

	def AddItem(self, text, padding = 0, is_monster = False, event_vnum = 0, _by_name = False, click_action = None):
		tmp = ui.Window()

		tmp.SetParent(self.scrollBoard)
		# tmp.AddFlag("attach")
		# tmp.SetSize(self.GetWidth() + 120, 15)
		tmp.SetSize((self.peekWindow.GetWidth() - 9) if self.scrollBar.IsShow() else (self.peekWindow.GetWidth()), 16)
		# tmp.SetPosition(0, 4 + (16 * len(self.elements)))
		tmp.SetPosition(0, 19 * len(self.elements))

		if self._location:
			if _by_name:
				# mobSpawnDict path -- `text` is a map name string. Convert via
				# the name->display dict (falls back to the raw map name).
				mapName = text
				text = localeinfo.MINIMAP_ZONE_NAME_DICT.get(mapName, mapName)
				# _coords is keyed by element index (matches len(self.elements)
				# below). event_vnum carries the map name so OnOver can load
				# the right atlas for the minimap embed.
				event_vnum = mapName
			else:
				# Legacy npcOriginDict path -- `text` is a map index integer.
				event_vnum = text
				text = localeinfo.GetMiniMapZoneNameByIdx(text)
			tmp.SetOverInEvent(ui.__mem_func__(self.OnOver), len(self.elements), True, text, event_vnum)
			tmp.SetOverOutEvent(ui.__mem_func__(self.OnOver), len(self.elements), False)
		else:
			# Pass (vnum, is_monster) through so OnOver can route to the right
			# preview. None/None fill the _name/_index slots used by the
			# location path; positional order stays compatible with OnOver.
			tmp.SetOverInEvent(ui.__mem_func__(self.OnOver),
				len(self.elements), True, None, None, event_vnum, is_monster)
			tmp.SetOverOutEvent(ui.__mem_func__(self.OnOver),
				len(self.elements), False, None, None, event_vnum, is_monster)

		if not self._location:
			if click_action is not None:
				self._clickActions[len(self.elements)] = click_action
				tmp.SetMouseLeftButtonDownEvent(ui.__mem_func__(self.OnClickAction), len(self.elements))
			else:
				tmp.SetMouseLeftButtonDownEvent(ui.__mem_func__(self.OnClick), is_monster, event_vnum)

		# import dbg
		# dbg.TraceError("asd: %d - %d"%(self.peekWindow.GetWidth(), self.peekWindow.GetHeight()))

		# tmp.img = ui.ExpandedImageBox()
		# tmp.img.SetParent(tmp)
		# tmp.img.AddFlag("attach")
		# tmp.img.AddFlag("not_pick")
		# tmp.img.LoadImage("d:/ymir work/ui/wiki/arrow_2.tga")
		# tmp.img.SetPosition(padding, tmp.GetHeight() / 2 - tmp.img.GetHeight() / 2)

		# if not localeinfo.IsARABIC():
			# tmp.img.Show()

		tmp.txt = ui.TextLine()
		tmp.txt.SetParent(tmp)
		# tmp.txt.AddFlag("attach")
		tmp.txt.AddFlag("not_pick")
		tmp.txt.SetText(text)

		# if localeinfo.IsARABIC():
			# tmp.txt.SetHorizontalAlignCenter()
			# tmp.txt.SetPosition(30,
									# tmp.GetHeight() / 2 - tmp.txt.GetTextSize()[1] / 2 - 1)
		# else:
			# tmp.txt.SetPosition(tmp.img.GetLocalPosition()[0] + tmp.img.GetWidth() + 5,
									# tmp.GetHeight() / 2 - tmp.txt.GetTextSize()[1] / 2 - 1)
		tmp.txt.SetHorizontalAlignCenter()
		# tmp.txt.SetPosition(tmp.GetWidth() / 2, -5 if localeinfo.IsARABIC() else -3)
		tmp.txt.SetPosition(tmp.GetWidth() / 2, 0)
		tmp.txt.Show()

		# addPadding = 0
		# totalElem = len(self.elements)
		
		# if totalElem > 0:
			# lastIndex = totalElem
			
			# self.elements.insert(lastIndex, tmp)
			# totalElem += 1
			
			# for i in xrange(lastIndex, totalElem):
				# self.elements[i].SetPosition(0,
						# (0 if i == 0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))
			
			# addPadding = self.ELEM_PADDING
		# else:
		self.elements[len(self.elements)] = tmp

		# tmp.SAFE_SetOverInEvent(self.OnOver, True)
		# tmp.SAFE_SetOverInEvent(self.OnOver, True)

		if app.USE_CLIP_MASK:
			# tmp.img.SetSubClippingMaskWindow(self.peekWindow)
			# tmp.SetSubClippingMaskWindow(self.peekWindow)
			tmp.txt.SetSubClippingMaskWindow(self.peekWindow)

		tmp.Show()

		# self.scrollBoard.SetSize(tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		# self.scrollBoard.SetSize(self.peekWindow.GetWidth(), 8 + (16 * len(self.elements)))
		self.scrollBoard.SetSize(self.peekWindow.GetWidth(), 19 * len(self.elements))
		self.UpdateScrollbar()
		return tmp

	def OnRunMouseWheel(self, length):
		# app.USE_EXTENDED_WIKI_CRAFT
		if not self.scrollBar or not self.scrollBar.IsShow():
			return False

		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True

		return False

	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			if not self.scrollBar.IsShow():
				for element in self.elements.values():
					element.SetSize(self.peekWindow.GetWidth() - 9, 16)
					element.txt.SetPosition(element.GetWidth() / 2, element.txt.GetLocalPosition()[1])

			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()

	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		# self.scrollBar.SetParent(self)
		# self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetParent(self.peekWindow)
		self.scrollBar.SetPosition(self.peekWindow.GetWidth() - 8, 0)
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()

		self.ChangeScrollbar()

if app.USE_EXTENDED_WIKI_CRAFT:
	class WikiCubeMiniRecipe(ui.Window):
		# One cube recipe rendered as a single 486x144 strip for use inside
		# SpecialPageWindow when the page is a cube NPC. Layout:
		#
		#   [reward slot]  [m1][m2][m3][m4][m5][m6]      [yang]
		#                                                [gaya]
		#
		# Slot icons + counts go through ui.SlotWindow so they use the same
		# engine renderer the inventory does (no manual TextLine overlays).
		# The decorative slot frames (craft_reward_slot_small.png /
		# craft_material_slot.png) are ExpandedImageBox children of self.bg.

		ROW_W           = 486
		ROW_H           = 144
		REWARD_BG_PATH  = "d:/ymir work/ui/wiki/craft_reward_slot_small.png"
		MAT_BG_PATH     = "d:/ymir work/ui/wiki/craft_material_slot.png"
		BG_PATH         = "d:/ymir work/ui/wiki/craft_detail_small.png"

		# Geometry. Slot bgs are 40 wide x 103 tall; item icons are 32 wide
		# centered horizontally (4 px inset) and anchored near the top. Height
		# follows the item's real GetItemSize() height (32 for jewelry/etc,
		# 64 for weapons/armor) so the engine's count overlay anchors against
		# the icon's actual bottom-right and stays within the slot frame.
		SLOT_BG_W       = 40
		SLOT_BG_H       = 103
		SLOT_ICON_W     = 32
		SLOT_ICON_INSET = 4
		SLOT_Y          = ((ROW_H - SLOT_BG_H) / 2 ) + 10

		REWARD_X        = 15 + 10

		# Materials show 5 slots at a time. Recipes with more materials get
		# left/right arrow buttons that page through batches of 5. Arrows
		# are HIDDEN when they wouldn't do anything: prev is hidden on
		# page 0, next is hidden on the last page. So the player only ever
		# sees an arrow that actually moves the page.
		MAT_VISIBLE     = 5
		MAT_PAD_X       = 4
		MAT_PEEK_X      = 75 + 30 + 38
		MAT_PEEK_W      = MAT_VISIBLE * SLOT_BG_W + (MAT_VISIBLE - 1) * MAT_PAD_X  # = 216

		# Page nav arrow geometry. Buttons sit on the left/right of the
		# slot strip, vertically centered against the row.
		PAGE_BTN_W      = 16
		PAGE_BTN_H      = 16
		PAGE_BTN_PAD    = 4
		PAGE_BTN_LEFT_PATH  = "d:/ymir work/ui/wiki/dungeons/left_arrow.png"
		PAGE_BTN_LEFT_OVER  = "d:/ymir work/ui/wiki/dungeons/left_arrow_hover.png"
		PAGE_BTN_LEFT_DOWN  = "d:/ymir work/ui/wiki/dungeons/left_arrow_down.png"
		PAGE_BTN_RIGHT_PATH = "d:/ymir work/ui/wiki/dungeons/right_arrow.png"
		PAGE_BTN_RIGHT_OVER = "d:/ymir work/ui/wiki/dungeons/right_arrow_hover.png"
		PAGE_BTN_RIGHT_DOWN = "d:/ymir work/ui/wiki/dungeons/right_arrow_down.png"

		SCROLL_SPEED    = 50

		# Cost text positions. The bg already has yang + gaya icons painted
		# in -- we ONLY place the value text next to them. Tuned to land at
		# the embedded icons' right edge; nudge if the painted icons move.
		COST_YANG_TEXT_X = 425
		COST_YANG_TEXT_Y = 38
		COST_GEM_TEXT_X  = 425
		COST_GEM_TEXT_Y  = 80

		@staticmethod
		def _FormatKK(n):
			# Delegates to the module-level formatter so the cube mini rows
			# and the weapons refine table share one money formatter.
			return FormatMoneyKK(n)

		def __init__(self, recipe,
				mOverInEvent=None, mOverOutEvent=None,
				mOnRightEvent=None, mOnLeftEvent=None):
			ui.Window.__init__(self)
			self.SetSize(self.ROW_W, self.ROW_H)

			self.recipe = recipe or {}
			self.mOverInEvent  = mOverInEvent
			self.mOverOutEvent = mOverOutEvent
			self.mOnRightEvent = mOnRightEvent
			self.mOnLeftEvent  = mOnLeftEvent
			# slotIndex -> {"vnum": ...} so engine slot callbacks can route
			# back to the parent's tooltip / click handlers.
			self.slotMeta = {}
			self.materialBgs = []

			# Background plate.
			self.bg = ui.ExpandedImageBox()
			self.bg.SetParent(self)
			self.bg.AddFlag("attach")
			self.bg.AddFlag("not_pick")
			self.bg.LoadImage(self.BG_PATH)
			self.bg.SetPosition(0, 0)
			self.bg.Show()

			# Reward slot frame on the left.
			self.rewardBg = ui.ExpandedImageBox()
			self.rewardBg.SetParent(self.bg)
			self.rewardBg.AddFlag("attach")
			self.rewardBg.AddFlag("not_pick")
			self.rewardBg.LoadImage(self.REWARD_BG_PATH)
			self.rewardBg.SetPosition(self.REWARD_X, self.SLOT_Y)
			self.rewardBg.Show()

			# Single SlotWindow covers the whole strip; all slots
			# (reward + materials) live inside it so the engine handles
			# icon + count drawing uniformly.
			self.slotWnd = ui.SlotWindow()
			self.slotWnd.SetParent(self)
			self.slotWnd.SetPosition(0, 0)
			self.slotWnd.SetSize(self.ROW_W, self.ROW_H)
			self.slotWnd.SetOverInItemEvent(ui.__mem_func__(self._OnSlotOverIn))
			self.slotWnd.SetOverOutItemEvent(ui.__mem_func__(self._OnSlotOverOut))
			self.slotWnd.SetSelectItemSlotEvent(ui.__mem_func__(self._OnSlotLeftClick))
			self.slotWnd.SetUseSlotEvent(ui.__mem_func__(self._OnSlotRightClick))
			self.slotWnd.Show()

			# Pre-parse materials and stash everything we need for the slot
			# build. We DO NOT call AppendSlot / SetItemSlot here -- doing so
			# would create CNumberLine count badges before the row's clip
			# mask is propagated (the mask only arrives after row.SetParent
			# in WikiCubeMiniList._BuildRows), and SetSlotCount copies the
			# slotWnd's mask pointers into the badge ONCE at creation time.
			# Result: badges born maskless render at unclipped screen
			# positions = floating "10"s far above/below the wiki.
			#
			# _BuildSlots() below is invoked AFTER row.SetParent, when the
			# mask is in place. That's when slots actually get populated.
			reward = self.recipe.get("reward_item") or [0, 0]
			try:
				self._rewardVnum  = int(reward[0])
				self._rewardCount = int(reward[1]) if len(reward) > 1 else 0
			except (TypeError, ValueError):
				self._rewardVnum, self._rewardCount = 0, 0

			matList = self.recipe.get("material_list") or []
			self.allMaterials = []
			for i in range(0, len(matList) - 1, 2):
				try:
					mVnum  = int(matList[i])
					mCount = int(matList[i + 1])
				except (TypeError, ValueError):
					continue
				if mVnum:
					self.allMaterials.append((mVnum, mCount))

			self.matPageOffset = 0
			# Slot index layout: 0 = reward. 1..MAT_VISIBLE = material slots.
			self._matSlotIndexStart = 1

			# Decorative slot frames -- safe to draw now; no count badges
			# attached to ExpandedImageBox.
			for i in range(self.MAT_VISIBLE):
				matX = self.MAT_PEEK_X + i * (self.SLOT_BG_W + self.MAT_PAD_X)
				matBg = ui.ExpandedImageBox()
				matBg.SetParent(self.bg)
				matBg.AddFlag("attach")
				matBg.AddFlag("not_pick")
				matBg.LoadImage(self.MAT_BG_PATH)
				matBg.SetPosition(matX, self.SLOT_Y)
				matBg.Show()
				self.materialBgs.append(matBg)

			# Page nav arrows (only when more than 6 materials).
			self.prevPageBtn = None
			self.nextPageBtn = None
			if len(self.allMaterials) > self.MAT_VISIBLE:
				self._BuildPageButtons()

			# Tracks whether _BuildSlots() has run -- guards against double
			# AppendSlot calls if the list ever calls it twice by mistake.
			self._slotsBuilt = False

			# Cost block: yang + gaya. The yang coin and gaya gem icons are
			# already painted into craft_detail_small.png, so we only render
			# the value text next to them. Yang amount uses the compact "kk"
			# formatter (20000000 -> "20kk") so the value fits inside the
			# cost column without being truncated. No success rate.
			yangCost = self.recipe.get("price_yang") or 0
			gemCost  = self.recipe.get("price_gem")  or 0

			self.yangText = ui.TextLine()
			self.yangText.SetParent(self.bg)
			self.yangText.AddFlag("attach")
			self.yangText.AddFlag("not_pick")
			self.yangText.SetText(self._FormatKK(yangCost))
			self.yangText.SetPosition(self.COST_YANG_TEXT_X, self.COST_YANG_TEXT_Y)
			self.yangText.Show()

			self.gemText = ui.TextLine()
			self.gemText.SetParent(self.bg)
			self.gemText.AddFlag("attach")
			self.gemText.AddFlag("not_pick")
			self.gemText.SetText(str(gemCost))
			self.gemText.SetPosition(self.COST_GEM_TEXT_X, self.COST_GEM_TEXT_Y)
			self.gemText.Show()

		def _OnSlotOverIn(self, slotIndex):
			meta = self.slotMeta.get(slotIndex)
			if not meta or not self.mOverInEvent:
				return
			# Match the (vnum, render/metinSlot) signature SpecialPageWindow's
			# OnOverIn expects (truthy "render" flag suppresses model render
			# inside the item tooltip).
			self.mOverInEvent(meta["vnum"],
				[0 for _ in xrange(player.METIN_SOCKET_MAX_NUM)])

		def _OnSlotOverOut(self):
			if self.mOverOutEvent:
				self.mOverOutEvent()

		def _OnSlotLeftClick(self, slotIndex):
			meta = self.slotMeta.get(slotIndex)
			if not meta:
				return
			wikiBase = wiki.GetBaseClass()
			if not wikiBase:
				return
			navVnum = meta["vnum"]
			try:
				item.SelectItem(navVnum)
				iType = item.GetItemType()
				if iType == item.ITEM_TYPE_WEAPON or iType == item.ITEM_TYPE_ARMOR:
					startRefineVnum = wiki.GetWikiItemStartRefineVnum(navVnum)
					navVnum = startRefineVnum if startRefineVnum != 0 else (int(navVnum / 10) * 10)
			except Exception:
				pass
			wikiBase.OpenSpecialPage(None, navVnum, False)

		def _OnSlotRightClick(self, slotIndex):
			meta = self.slotMeta.get(slotIndex)
			if not meta or not self.mOnRightEvent:
				return
			self.mOnRightEvent(meta["vnum"])

		def _BuildPageButtons(self):
			# Vertical anchor: center against the slot strip.
			btnY = self.SLOT_Y + (self.SLOT_BG_H - self.PAGE_BTN_H) / 2

			# Buttons parent to self (the recipe row Window) -- NOT self.bg.
			# self.slotWnd is also a child of self, added BEFORE the buttons,
			# so the buttons end up later in self's child list and render
			# (and pick-test) on top of slotWnd. If they sat under bg they'd
			# be below slotWnd in Z order and clicks would never reach them.
			self.prevPageBtn = ui.Button()
			self.prevPageBtn.SetParent(self)
			self.prevPageBtn.SetUpVisual(self.PAGE_BTN_LEFT_PATH)
			self.prevPageBtn.SetOverVisual(self.PAGE_BTN_LEFT_OVER)
			self.prevPageBtn.SetDownVisual(self.PAGE_BTN_LEFT_DOWN)
			self.prevPageBtn.SetPosition(
				self.MAT_PEEK_X - self.PAGE_BTN_W - self.PAGE_BTN_PAD - 38 - 9,
				btnY)
			self.prevPageBtn.SAFE_SetEvent(self._OnPrevPage)
			# Hidden initially -- shown only when page > 0 (see _RefreshMaterials).
			self.prevPageBtn.Hide()

			self.nextPageBtn = ui.Button()
			self.nextPageBtn.SetParent(self)
			self.nextPageBtn.SetUpVisual(self.PAGE_BTN_RIGHT_PATH)
			self.nextPageBtn.SetOverVisual(self.PAGE_BTN_RIGHT_OVER)
			self.nextPageBtn.SetDownVisual(self.PAGE_BTN_RIGHT_DOWN)
			self.nextPageBtn.SetPosition(
				self.MAT_PEEK_X + self.MAT_PEEK_W + self.PAGE_BTN_PAD,
				btnY)
			self.nextPageBtn.SAFE_SetEvent(self._OnNextPage)
			# Hidden initially -- shown only when there is a next page.
			self.nextPageBtn.Hide()

		def _OnPrevPage(self):
			if self.matPageOffset <= 0:
				return
			self.matPageOffset = max(0, self.matPageOffset - self.MAT_VISIBLE)
			self._RefreshMaterials()

		def _OnNextPage(self):
			if self.matPageOffset + self.MAT_VISIBLE >= len(self.allMaterials):
				return
			self.matPageOffset += self.MAT_VISIBLE
			self._RefreshMaterials()

		def _RefreshMaterials(self):
			# Push the current page's materials into the fixed slot indices.
			# Slots without a material on this page get cleared (vnum 0).
			# Skip entirely if slots haven't been built yet -- _BuildSlots()
			# will call this once at the end of its work.
			if not self._slotsBuilt:
				return
			for i in range(self.MAT_VISIBLE):
				slotIdx = self._matSlotIndexStart + i
				matIdx  = self.matPageOffset + i
				if matIdx < len(self.allMaterials):
					mVnum, mCount = self.allMaterials[matIdx]
					self.slotWnd.SetItemSlot(slotIdx, mVnum,
						mCount if mCount > 1 else 0)
					self.slotMeta[slotIdx] = {"vnum": mVnum}
				else:
					self.slotWnd.SetItemSlot(slotIdx, 0, 0)
					self.slotMeta[slotIdx] = {"vnum": 0}

			# Hide arrow buttons that wouldn't do anything: prev disappears
			# on page 0, next disappears once we're showing the tail.
			if self.prevPageBtn:
				if self.matPageOffset <= 0:
					self.prevPageBtn.Hide()
				else:
					self.prevPageBtn.Show()
			if self.nextPageBtn:
				if self.matPageOffset + self.MAT_VISIBLE >= len(self.allMaterials):
					self.nextPageBtn.Hide()
				else:
					self.nextPageBtn.Show()

		def BuildSlots(self):
			# Append all slots + populate them. MUST be called AFTER the row
			# is parented into the list's scrollBoard, because SetSlotCount
			# (called via SetItemSlot) creates each count badge's clip mask
			# from the slotWnd's CURRENT mask pointers -- which only exist
			# after parent propagation. Calling this in __init__ would bake
			# in maskless badges that float far outside the row.
			if self._slotsBuilt:
				return
			self._slotsBuilt = True

			# Reward slot at index 0.
			rewardIconX = self.REWARD_X + self.SLOT_ICON_INSET
			rewardIconY = self.SLOT_Y + self.SLOT_ICON_INSET
			self.slotWnd.AppendSlot(0, rewardIconX, rewardIconY,
				self.SLOT_ICON_W, 32)
			self.slotWnd.SetItemSlot(0, self._rewardVnum,
				self._rewardCount if self._rewardCount > 1 else 0)
			self.slotMeta[0] = {"vnum": self._rewardVnum}

			# 6 material slot positions at fixed indices 1..MAT_VISIBLE.
			for i in range(self.MAT_VISIBLE):
				slotIdx = self._matSlotIndexStart + i
				matX    = self.MAT_PEEK_X + i * (self.SLOT_BG_W + self.MAT_PAD_X)
				iconX   = matX + self.SLOT_ICON_INSET
				iconY   = self.SLOT_Y + self.SLOT_ICON_INSET
				self.slotWnd.AppendSlot(slotIdx, iconX, iconY, 32, 32)
				self.slotMeta[slotIdx] = {"vnum": 0}

			# Now fill the slots with the first page of materials.
			self._RefreshMaterials()


	class WikiCubeMiniList(ui.Window):
		# Vertical scrollable column of WikiCubeMiniRecipe strips, one per
		# recipe the NPC produces. Drops into the bottom half of
		# SpecialPageWindow for cube NPCs (the old stats panel area).

		SCROLL_SPEED = 50
		ELEM_PADDING = 6

		def __init__(self, npc_vnum, w=540, h=158,
				mOverInEvent=None, mOverOutEvent=None,
				mOnRightEvent=None, mOnLeftEvent=None):
			ui.Window.__init__(self)
			self.npc_vnum = npc_vnum
			self.elements = []
			self.scrollBar = None
			self.mOverInEvent  = mOverInEvent
			self.mOverOutEvent = mOverOutEvent
			self.mOnRightEvent = mOnRightEvent
			self.mOnLeftEvent  = mOnLeftEvent

			self.SetSize(w, h)

			self.peekWindow = ui.Window()
			self.peekWindow.SetParent(self)
			self.peekWindow.AddFlag("attach")
			self.peekWindow.AddFlag("not_pick")
			self.peekWindow.SetSize(w - 12, h)
			self.peekWindow.SetPosition(0, 0)

			if not app.USE_CLIP_MASK:
				self.peekWindow.SetInsideRender(True)

			self.peekWindow.Show()

			self.scrollBoard = ui.Window()
			self.scrollBoard.SetParent(self.peekWindow)
			self.scrollBoard.AddFlag("attach")
			self.scrollBoard.AddFlag("not_pick")

			if app.USE_CLIP_MASK:
				# Primary clip so recipe rows are bounded by peekWindow when
				# scrolled past the top/bottom (same pattern as the other
				# bottom-area scrollable widgets).
				self.scrollBoard.SetClippingMaskWindow(self.peekWindow)

			self.scrollBoard.Show()

			self._BuildRows()

		def _BuildRows(self):
			recipes = getattr(game_data, "craftingDict", {}).get(self.npc_vnum, {}) or {}
			if not isinstance(recipes, dict):
				return

			try:
				keyOrder = sorted(recipes.keys())
			except Exception:
				keyOrder = list(recipes.keys())

			# Center rows horizontally inside the scrollBoard.
			rowW = WikiCubeMiniRecipe.ROW_W
			rowX = max(0, (self.peekWindow.GetWidth() - rowW) / 2)

			currY = 0
			for k in keyOrder:
				recipe = recipes[k]
				if not isinstance(recipe, dict):
					continue
				row = WikiCubeMiniRecipe(recipe,
					self.mOverInEvent, self.mOverOutEvent,
					self.mOnRightEvent, self.mOnLeftEvent)
				row.SetParent(self.scrollBoard)
				row.AddFlag("attach")
				row.SetPosition(rowX, currY)
				row.Show()
				# Build slots AFTER parenting so the scrollBoard's primary
				# clip mask has propagated down to the row's slotWnd before
				# SetSlotCount snapshots it into each count badge.
				row.BuildSlots()
				self.elements.append(row)
				currY += row.GetHeight() + self.ELEM_PADDING

			self.scrollBoard.SetSize(self.peekWindow.GetWidth(), max(currY, 1))
			self._RegisterScrollBar()

		def _RegisterScrollBar(self):
			if self.scrollBar or not self.elements:
				return
			self.scrollBar = WikiScrollBar()
			self.scrollBar.SetParent(self)
			self.scrollBar.SetPosition(self.peekWindow.GetWidth() + 1, 0)
			self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
			# SetScrollEvent wraps internally with __mem_func__; pass the raw
			# bound method or the wrapper double-wraps and crashes with
			# "__mem_func__ instance has no attribute 'im_func'".
			self.scrollBar.SetScrollEvent(self.OnScrollBar)
			self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
			self.scrollBar.Show()
			self._UpdateScrollbarVisibility()

		def _UpdateScrollbarVisibility(self):
			if not self.scrollBar:
				return
			if self.scrollBoard.GetHeight() <= self.peekWindow.GetHeight():
				self.scrollBar.Hide()
			else:
				self.scrollBar.SetScale(
					self.peekWindow.GetHeight(),
					self.scrollBoard.GetHeight())
				denom = float(self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) or 1.0
				self.scrollBar.SetPosScale(
					abs(self.scrollBoard.GetLocalPosition()[1]) / denom)
				self.scrollBar.Show()

		def OnScrollBar(self, fScale):
			delta = (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0
			curr  = min(0, max(int(math.ceil(delta)),
				-self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
			self.scrollBoard.SetPosition(0, curr)

		def OnRunMouseWheel(self, length):
			if not self.peekWindow.IsInPosition():
				return False
			if not self.scrollBar or not self.scrollBar.IsShow():
				return False
			delta = int((length * 0.01) * self.SCROLL_SPEED)
			curr  = min(0, max(self.scrollBoard.GetLocalPosition()[1] + delta,
				-self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
			self.scrollBoard.SetPosition(0, curr)
			self._UpdateScrollbarVisibility()
			return True

if app.USE_EXTENDED_WIKI:
	class BundleContentRow(ui.Window):
		"""One flat strip of item slots for a single bundle-box category (or
		the guaranteed section), rendered directly inside
		SpecialPageWindow's bonus-info scroll band (self.bonusScrollBoard /
		self.bonusPeekWindow).

		Deliberately does NOT own an inner peekWindow/scrollBoard/scrollBar
		the way ChestPeekWindow does. ChestPeekWindow's own constructor
		claims the engine's SUB clip-mask slot for its children the moment
		it is built (PythonWindow.cpp SetSubClippingMaskWindow is
		first-set-wins, no re-set API) -- nesting one of those inside the
		band's own scroll meant its rows could never pick up the band's
		real viewport mask, so they rendered outside it once the band was
		wheel-scrolled (the reported "leaks above y=187" bug). This class
		is the flattened replacement: a single ui.SlotWindow sized to the
		category's actual content (no clipping of its own), explicitly
		given the same sub mask window every other widget in the band
		uses, so the band's own scroll is the only scroller. """

		ELEM_PER_LINE = ChestPeekWindow.ELEM_PER_LINE
		ELEM_X_PADDING = ChestPeekWindow.ELEM_X_PADDING
		ELEM_PADDING = ChestPeekWindow.ELEM_PADDING
		ELEM_PITCH_X = 36
		ELEM_ROW_H = 32

		def __init__(self, width, subMaskWindow, mOverInEvent = None, mOverOutEvent = None, mOnRightEvent = None):
			ui.Window.__init__(self)

			self.mOverInEvent = mOverInEvent
			self.mOverOutEvent = mOverOutEvent
			self.mOnRightEvent = mOnRightEvent
			self._subMaskWindow = subMaskWindow

			self.posMap = {}
			self.slotMeta = {}
			self.markers = []

			self.SetSize(width, self.ELEM_ROW_H)

			self.slotWnd = ui.SlotWindow()
			self.slotWnd.SetParent(self)
			self.slotWnd.SetPosition(0, 0)
			self.slotWnd.SetSize(width, self.ELEM_ROW_H)
			if app.USE_CLIP_MASK and subMaskWindow:
				self.slotWnd.SetSubClippingMaskWindow(subMaskWindow)
			self.slotWnd.SetOverInItemEvent(ui.__mem_func__(self._OnSlotOverIn))
			self.slotWnd.SetOverOutItemEvent(ui.__mem_func__(self._OnSlotOverOut))
			self.slotWnd.SetSelectItemSlotEvent(ui.__mem_func__(self._OnSlotLeftClick))
			self.slotWnd.SetUseSlotEvent(ui.__mem_func__(self._OnSlotRightClick))
			self.slotWnd.Show()

		def AddItem(self, vnum, count, sex = 0):
			item.SelectItem(vnum)
			(itemW, itemH) = item.GetItemSize()

			totalElem = len(self.posMap)
			if totalElem > 0:
				currAdd = 0
				while currAdd in self.posMap:
					currAdd += 1
				totalLine = currAdd % self.ELEM_PER_LINE
				currH = int(math.floor(currAdd / self.ELEM_PER_LINE) * (32 + self.ELEM_PADDING))
				for i in xrange(itemH):
					self.posMap[currAdd + i * self.ELEM_PER_LINE] = True
				cellX = (ChestPeekWindow.ELEM_START_X if app.USE_EXTENDED_WIKI_SHOP else 0) + 1 \
					+ totalLine * (self.ELEM_PITCH_X + self.ELEM_X_PADDING)
				cellY = currH
			else:
				for i in xrange(itemH):
					self.posMap[i * self.ELEM_PER_LINE] = True
				cellX = (ChestPeekWindow.ELEM_START_X if app.USE_EXTENDED_WIKI_SHOP else 0) + 1
				cellY = 0

			navVnum = vnum
			if wiki.GetBaseClass():
				if (item.GetItemType() == item.ITEM_TYPE_WEAPON
					or item.GetItemType() == item.ITEM_TYPE_ARMOR):
					startRefineVnum = wiki.GetWikiItemStartRefineVnum(vnum)
					navVnum = startRefineVnum if startRefineVnum != 0 else (int(vnum / 10) * 10)

			slotIndex = len(self.slotMeta)
			self.slotWnd.AppendSlot(slotIndex, cellX, cellY, itemW * 32, itemH * 32)

			# Yang (vnum 1) needs MakeMoneyText formatting the engine's slot
			# count can't produce -- same special case ChestPeekWindow.AddItem
			# handles. Not observed in current cl_bundle_box.json data, kept
			# for parity since it's a straight mirror, not new behavior.
			moneyOverlay = None
			if vnum == 1:
				self.slotWnd.SetItemSlot(slotIndex, vnum, 0)
				moneyOverlay = ui.TextLine()
				moneyOverlay.SetParent(self.slotWnd)
				moneyOverlay.AddFlag("attach")
				moneyOverlay.AddFlag("not_pick")
				moneyOverlay.SetFontName(localeinfo.UI_DEF_FONT)
				moneyOverlay.SetOutline()
				moneyOverlay.SetFeather(False)
				moneyOverlay.SetHorizontalAlignRight()
				moneyOverlay.SetText(MakeMoneyText(count))
				moneyOverlay.SetPosition(
					cellX + (itemW * 32) - 1,
					cellY + (itemH * 32) - moneyOverlay.GetTextSize()[1])
				if app.USE_CLIP_MASK and self._subMaskWindow:
					moneyOverlay.SetSubClippingMaskWindow(self._subMaskWindow)
				moneyOverlay.Show()
			else:
				engineCount = count if count and count > 1 else 0
				self.slotWnd.SetItemSlot(slotIndex, vnum, engineCount)

			self.slotMeta[slotIndex] = {
				"vnum":      vnum,
				"metinSlot": [0 for _i in xrange(player.METIN_SOCKET_MAX_NUM)],
				"navVnum":   navVnum,
				"moneyTxt":  moneyOverlay,
			}

			rowBottom = cellY + itemH * 32

			if sex == 1 or sex == 2:
				marker = ui.TextLine()
				marker.SetParent(self)
				marker.AddFlag("attach")
				marker.AddFlag("not_pick")
				marker.SetHorizontalAlignCenter()
				marker.SetOutline()
				marker.SetPackedFontColor(0xFF99CCFF if sex == 1 else 0xFFFFAACC)
				marker.SetText(getattr(localeinfo, "BUNDLEBOX_WIKI_MALE", "(M)") if sex == 1
					else getattr(localeinfo, "BUNDLEBOX_WIKI_FEMALE", "(F)"))
				marker.SetPosition(int(cellX + (itemW * 32) / 2), int(cellY + itemH * 32))
				if app.USE_CLIP_MASK and self._subMaskWindow:
					marker.SetSubClippingMaskWindow(self._subMaskWindow)
				marker.Show()
				self.markers.append(marker)
				rowBottom = cellY + itemH * 32 + marker.GetTextSize()[1]

			newH = max(self.GetHeight(), int(rowBottom))
			self.SetSize(self.GetWidth(), newH)
			self.slotWnd.SetSize(self.GetWidth(), newH)

		def _OnSlotOverIn(self, slotIndex):
			meta = self.slotMeta.get(slotIndex)
			if not meta or not self.mOverInEvent:
				return
			self.mOverInEvent(meta["vnum"], meta["metinSlot"])

		def _OnSlotOverOut(self):
			if self.mOverOutEvent:
				self.mOverOutEvent()

		def _OnSlotLeftClick(self, slotIndex):
			meta = self.slotMeta.get(slotIndex)
			if not meta:
				return
			wikiBase = wiki.GetBaseClass()
			if not wikiBase:
				return
			wikiBase.OpenSpecialPage(None, meta["navVnum"], False)

		def _OnSlotRightClick(self, slotIndex):
			meta = self.slotMeta.get(slotIndex)
			if not meta or not self.mOnRightEvent:
				return
			self.mOnRightEvent(meta["vnum"])

class SpecialPageWindow(ui.Window):
	"""Static values!
		Please dont touch on them."""
	SCROLL_SPEED = 50
	
	def __init__(self, vnum, isMonster):
		ui.Window.__init__(self)
		
		self.toolTip = uitooltip.ItemToolTip()
		
		wikiBase = wiki.GetBaseClass()
		if id(self) not in wikiBase.objList:
			wikiBase.objList[long(id(self))] = proxy(self)

		if app.USE_EXTENDED_WIKI:
			import ingamewikireverse
			self.isUpgradable = False
			self.isChest = False
			# Set to True when the item is neither a weapon/armor (refinable)
			# nor a chest (gacha box). Triggers the new layout that exposes
			# three reverse-lookup panels (refine usages, cube usages, shops).
			self.isNoContent = False
			# Set to True when this vnum is a bundle-box key in
			# game_data.bundleBoxDict (wiki Task 6 bake). Bundle boxes render
			# a JSON-driven Contents section instead of isChest/isNoContent.
			self.isBundle = False
			self.bundleSections = []
			self.bundleReverseHeader = None
			self.bundleRender = None

		self.vnum = vnum
		self.isMonster = isMonster
		self.bonusScrollBoard = None

		# NPCs that own a shop (e.g. weapons merchant, armor merchant) come
		# through the wiki as "monsters" because they share the entity model
		# pipeline, but they don't drop loot and don't have combat stats.
		# Detect those so the detail page shows their shop inventory (with
		# prices, matching the dedicated shops page) instead of the drop
		# grid + HP/dmg/gold/EXP panel.
		if app.USE_EXTENDED_WIKI_SHOP:
			self.isShopNpc = isMonster and (self.vnum in game_data.shopDict)
		else:
			self.isShopNpc = False

		# Same idea for cube/craft NPCs. The bottom half of the page
		# (where combat stats used to live) becomes a mini cube recipe list
		# instead. NPCs that are BOTH shop and cube get shop items on top
		# and the cube recipes below.
		if app.USE_EXTENDED_WIKI_CRAFT:
			self.isCubeNpc = isMonster and (self.vnum in game_data.craftingDict)
		else:
			self.isCubeNpc = False

		self.bg = ui.ExpandedImageBox()
		self.bg.SetParent(self)
		self.bg.AddFlag("attach")
		self.bg.AddFlag("not_pick")
		self.bg.LoadImage("d:/ymir work/ui/wiki/{}.png".format("detail_monster_new" if isMonster else "detail_monster"))
		self.bg.Show()

		self.SetSize(self.bg.GetWidth(), self.bg.GetHeight())

		if app.USE_CLIP_MASK:
			self.SetClippingMaskWindow(self.bg)
		else:
			self.SetInsideRender(True, True)

		self.subTitleBg1 = ui.Window()
		self.subTitleBg1.SetParent(self.bg)
		self.subTitleBg1.AddFlag("attach")
		self.subTitleBg1.AddFlag("not_pick")
		self.subTitleBg1.SetSize(287 if isMonster else 351, 20)
		self.subTitleBg1.SetPosition(127 if isMonster else 189, 1)
		self.subTitleBg1.Show()

		self.subTitleBg2 = ui.Window()
		self.subTitleBg2.SetParent(self.bg)
		self.subTitleBg2.AddFlag("attach")
		self.subTitleBg2.AddFlag("not_pick")
		self.subTitleBg2.SetSize(539, 22)
		self.subTitleBg2.SetPosition(1, 165)
		self.subTitleBg2.Show()

		self.subTitleText1 = ui.TextLine()
		self.subTitleText1.SetParent(self.subTitleBg1)
		self.subTitleText1.AddFlag("attach")
		self.subTitleText1.AddFlag("not_pick")
		self.subTitleText1.SetHorizontalAlignCenter()
		self.subTitleText1.SetPosition(self.subTitleBg1.GetWidth() / 2, 0 if localeinfo.IsARABIC() else 0)
		self.subTitleText1.Show()

		self.subTitleText2 = ui.TextLine()
		self.subTitleText2.SetParent(self.subTitleBg2)
		self.subTitleText2.AddFlag("attach")
		self.subTitleText2.AddFlag("not_pick")
		self.subTitleText2.SetHorizontalAlignCenter()
		self.subTitleText2.SetPosition(self.subTitleBg2.GetWidth() / 2, 0 if localeinfo.IsARABIC() else 0)
		self.subTitleText2.Show()

		self.additionalLoaded = False

		if isMonster:
			self.subTitleBg3 = ui.Window()
			self.subTitleBg3.SetParent(self.bg)
			self.subTitleBg3.AddFlag("attach")
			self.subTitleBg3.AddFlag("not_pick")
			self.subTitleBg3.SetSize(125, 20)
			self.subTitleBg3.SetPosition(415, 0)
			self.subTitleBg3.Show()

			self.subTitleText3 = ui.TextLine()
			self.subTitleText3.SetParent(self.subTitleBg3)
			self.subTitleText3.AddFlag("attach")
			self.subTitleText3.AddFlag("not_pick")
			self.subTitleText3.SetHorizontalAlignCenter()
			self.subTitleText3.SetPosition(self.subTitleBg3.GetWidth() / 2, 0 if localeinfo.IsARABIC() else 0)
			self.subTitleText3.Show()

			# Shop NPCs and cube NPCs both replace the stats panel -- shop
			# NPCs with nothing (only items + locations), cube NPCs with the
			# mini recipe list. Either way, hide the "Statistics of ..."
			# header band so we don't render an empty title strip.
			hideStats = self.isShopNpc or self.isCubeNpc

			if self.isShopNpc:
				# Shop NPCs don't drop loot -- use the NPC's name alone as
				# the panel title (matches the dedicated shops page styling,
				# where the section header is just the merchant name).
				self.subTitleText1.SetText(nonplayer.GetMonsterName(self.vnum))
			elif self.isCubeNpc:
				# Pure cube NPC (no shop): top items area is empty, so the
				# title just shows the NPC name as a header.
				self.subTitleText1.SetText(nonplayer.GetMonsterName(self.vnum))
			else:
				self.subTitleText1.SetText(localeinfo.WIKI_MONSTERINFO_DROPLISTOF % nonplayer.GetMonsterName(self.vnum))
				self.subTitleText2.SetText(localeinfo.WIKI_MONSTERINFO_STATISTICSOF % nonplayer.GetMonsterName(self.vnum))

			if hideStats:
				self.subTitleBg2.Hide()
				self.subTitleText2.Hide()
			self.subTitleText3.SetText(localeinfo.WIKI_NPC_LOCATION)

			self.modelView = WikiRenderTarget(130, 145)
			self.modelView.SetParent(self.bg)
			self.modelView.AddFlag("attach")
			self.modelView.SetPosition(1, 1)
			self.modelView.SetModel(vnum)
			self.modelView.Show()

			self.itemContainer = ChestPeekWindow(self, 289, 136, False)
			self.itemContainer.ELEM_PER_LINE = 8
			self.itemContainer.ELEM_X_PADDING = -2
			self.itemContainer.AddFlag("attach")
			self.itemContainer.SetParent(self.bg)
			self.itemContainer.SetPosition(137, 22)
			self.itemContainer.mOverInEvent = ui.__mem_func__(self.OnOverIn)
			self.itemContainer.mOverOutEvent = ui.__mem_func__(self.OnOverOut)
			self.itemContainer.mOnRightEvent = ui.__mem_func__(self.OnRightDown)
			self.itemContainer.Show()

			if self.isShopNpc:
				# Shop inventory lives in game_data.shopDict (loaded locally
				# from the client's shop_proto/equivalent) -- no server
				# round-trip needed, populate immediately.
				self.LoadShopData()
			elif self.isCubeNpc:
				# Pure cube NPC: top items area stays empty. Cube recipes
				# render below via WikiCubeMiniList -- no drop fetch, no
				# stats panel.
				pass
			else:
				self.LoadDropData()

				self.bonusInfo = WikiMonsterBonusInfoWindow(self.vnum)#here
				self.bonusInfo.SetParent(self.bg)
				self.bonusInfo.AddFlag("attach")
				self.bonusInfo.SetPosition(6, 190)
				self.bonusInfo.Show()

			# Mini cube recipe list occupies the old stats panel area for
			# every cube NPC (shop+cube hybrids included). Sized to match
			# detail_monster_new.png's bottom band: 540 wide x 158 tall
			# starting at y=188 (right under subTitleBg2). One 486-tall...
			# wait -- the row is 486 wide x 144 tall; rows stack vertically
			# and overflow scrolls inside the list.
			if self.isCubeNpc:
				self.cubeMiniList = WikiCubeMiniList(self.vnum, 540, 158,
					mOverInEvent  = ui.__mem_func__(self.OnOverIn),
					mOverOutEvent = ui.__mem_func__(self.OnOverOut),
					mOnRightEvent = ui.__mem_func__(self.OnRightDown))
				self.cubeMiniList.SetParent(self.bg)
				self.cubeMiniList.AddFlag("attach")
				self.cubeMiniList.SetPosition(1, 188)
				self.cubeMiniList.Show()

			self.originInfoParsed = False

			self.originInfo = WikiItemOriginInfo(self.vnum, False, 125, 142, None, True)
			self.originInfo.SetParent(self.bg)
			self.originInfo.AddFlag("attach")
			self.originInfo.SetPosition(428, 24)
			self.originInfo.Show()
		else:
			item.SelectItem(self.vnum)

			if app.USE_EXTENDED_WIKI:
				bundleBoxData = getattr(game_data, "bundleBoxDict", {})
				self.isBundle = bundleBoxData.has_key(self.vnum)
				itemType = item.GetItemType()
				if self.isBundle:
					pass
				elif itemType in [item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR]:
					self.isUpgradable = True

					startRefineVnum = wiki.GetWikiItemStartRefineVnum(self.vnum)
					self.vnum = startRefineVnum if startRefineVnum != 0 else (int(self.vnum / 10) * 10)
				elif itemType in [item.ITEM_TYPE_ROD, item.ITEM_TYPE_PICK]:
					self.isUpgradable = True
				elif itemType in [item.ITEM_TYPE_GIFTBOX, item.ITEM_TYPE_GACHA]:
					self.isChest = True
				else:
					self.isNoContent = True
					self.bg.UnloadImage()
					self.bg.LoadImage("d:/ymir work/ui/wiki/detail_itemnocontent2.png")
			else:
				if wiki.CanIncrRefineLevel():
					startRefineVnum = wiki.GetWikiItemStartRefineVnum(self.vnum)
					self.vnum = startRefineVnum if startRefineVnum != 0 else (int(self.vnum / 10) * 10)

			self.subTitleText1.SetText(localeinfo.WIKI_ITEMINFO_OPTAINEDFROM)

			if app.USE_EXTENDED_WIKI:
				if self.isChest or self.isBundle:
					self.subTitleText2.SetText(localeinfo.WIKI_CHESTINFO_CONTENTOF % item.GetItemName())
				elif self.isUpgradable:
					self.subTitleText2.SetText(localeinfo.WIKI_ITEMINFO_REFINEINFO % item.GetItemName())
			else:
				self.subTitleText2.SetText(localeinfo.WIKI_ITEMINFO_REFINEINFO % item.GetItemName())

			self.modelView = ui.ExpandedImageBox()
			self.modelView.SetParent(self.bg)
			# self.modelView.AddFlag("attach")
			self.modelView.LoadImage(item.GetIconImageFileName())
			self.modelView.SetPosition(1 + 187 / 2 - self.modelView.GetWidth() / 2, 1 + 163 / 2 - self.modelView.GetHeight() / 2)
			self.modelView.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnOverIn), self.vnum + (wiki.MAX_REFINE_COUNT if wiki.CanIncrRefineLevel() else 0), 0)
			self.modelView.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnOverOut))
			self.modelView.SetMouseRightButtonDownEvent(ui.__mem_func__(self.OnRightDown), self.vnum + (wiki.MAX_REFINE_COUNT if wiki.CanIncrRefineLevel() else 0))
			self.modelView.Show()

			# For no-content items we skip the bonus refine/chest panel entirely
			# (nothing to show, and its position would overlap the new
			# reverse-lookup panels we add below).
			if not (app.USE_EXTENDED_WIKI and self.isNoContent):
				self.bonusPeekWindow = ui.Window()
				self.bonusPeekWindow.SetParent(self.bg)
				self.bonusPeekWindow.AddFlag("attach")
				self.bonusPeekWindow.AddFlag("not_pick")
				self.bonusPeekWindow.SetPosition(0, 187)

				if not app.USE_CLIP_MASK:
					self.bonusPeekWindow.SetInsideRender(True)

				self.bonusPeekWindow.Show()

				self.bonusScrollBoard = ui.Window()
				self.bonusScrollBoard.SetParent(self.bonusPeekWindow)
				self.bonusScrollBoard.AddFlag("attach")
				self.bonusScrollBoard.AddFlag("not_pick")

				if app.USE_CLIP_MASK:
					self.bonusScrollBoard.SetClippingMaskWindow(self.bonusPeekWindow)

				self.bonusScrollBoard.Show()

				if app.USE_EXTENDED_WIKI and self.isBundle:
					if app.USE_CLIP_MASK:
						self.bonusScrollBoard.SetSubClippingMaskWindow(self.bonusPeekWindow)
					self.loadFrom = self.vnum
					self.loadTo = self.vnum
					self.bundleSections = []
					contentHeight = self._BuildBundleContents(bundleBoxData[self.vnum])
					contentHeight = max(contentHeight, 1)
					visibleHeight = max(min(contentHeight, self.bg.GetHeight() - 187), 1)
					self.bonusPeekWindow.SetSize(540, visibleHeight)
					self.bonusScrollBoard.SetSize(540, contentHeight)

					if app.ENABLE_RENDER_TARGET:
						self._BuildBundleSetPreview(visibleHeight)
				else:
					if app.USE_EXTENDED_WIKI:
						if self.isChest:
							self.loadFrom = self.vnum
							self.loadTo = self.vnum
							self.bonusInfo = WikiMainChestWindow.WikiItem(self.vnum, self, True)
						else:
							self.bonusInfo = WikiMainWeaponWindow.WikiItem(self.vnum, self, False, self.isUpgradable)
					else:
						self.bonusInfo = WikiMainWeaponWindow.WikiItem(self.vnum, self, False)

					self.bonusInfo.SetParent(self.bonusScrollBoard)
					self.bonusInfo.Show()

					self.bonusPeekWindow.SetSize(self.bonusInfo.GetWidth(), self.bonusInfo.GetHeight())
					self.bonusScrollBoard.SetSize(self.bonusInfo.GetWidth(), self.bonusInfo.GetHeight())

			# self.originInfo = WikiItemOriginInfo(self, self.vnum)
			self.originInfo = WikiItemOriginInfo(self.vnum)
			self.originInfo.SetParent(self.bg)
			self.originInfo.AddFlag("attach")
			self.originInfo.SetPosition(200, 23)

			self.originInfo.Show()

			# No-content items get the three reverse-lookup panels at the
			# bottom of the page (the new detail_itemnocontent2.png cells).
			# Refine column is wired empty for v1 -- refine_proto is still
			# DB-only; the column will get data once refine_proto.txt ships.
			if app.USE_EXTENDED_WIKI and self.isNoContent:
				# Trigger the server-side wiki packet for this vnum. The
				# weapon/chest paths normally fire this from inside their
				# bonusInfo (WikiMainWeaponWindow.WikiItem.OnRender), but we
				# skipped that for no-content -- without this call,
				# wiki.IsSet stays False and OnRender never refreshes the
				# "Drops from" (originInfo) panel.
				if not wiki.IsSet(self.vnum):
					wiki.LoadInfo(long(id(self)), self.vnum, False)

				import ingamewikireverse

				# Bottom row layout: y=173 lines up the panel's reserved top
				# band (PANEL_TOP_PAD=22) with the column-title strip painted
				# into detail_itemnocontent2.png. Three equal-width columns
				# (185 px each) span the 555 px page; panel is 173 px tall.
				panel_y = 173
				panel_h = 173
				panel_w = 185
				# Column titles are embedded in detail_itemnocontent2.png by
				# the bg artist -- the widget doesn't render headers.
				# Items buyable with this item are listed by vnum, not the
				# selling NPC, so isMonster is always False.
				# Refine column placeholder: "(coming soon)" while the system
				# isn't wired (USE_REFINE_PROTO_TXT off), else the same "No
				# results" the other columns use when the item legitimately
				# has no refine usages.
				refineEmpty = (localeinfo.WIKI_REVERSE_EMPTY
					if app.USE_REFINE_PROTO_TXT
					else localeinfo.WIKI_REVERSE_REFINE_PENDING)
				cols = [
					(0,           ingamewikireverse.GetRefineUsages(self.vnum),
						refineEmpty),
					(panel_w,     ingamewikireverse.GetCubeUsages(self.vnum),
						localeinfo.WIKI_REVERSE_EMPTY),
					(panel_w * 2, ingamewikireverse.GetPurchasableWith(self.vnum),
						localeinfo.WIKI_REVERSE_EMPTY),
				]
				self.reverseLookupPanels = []
				for (colIndex, (px, vnumList, emptyText)) in enumerate(cols):
					p = ingamewikireverse.WikiReverseLookupPanel(panel_w, panel_h)
					p.SetParent(self.bg)
					p.AddFlag("attach")
					p.SetPosition(px, panel_y)
					p.SetEmptyPlaceholder(emptyText)
					if colIndex == 2:
						p.SetRows(self._BuildBuyColumnRows(vnumList))
					else:
						p.SetItems(vnumList, isMonster = False)
					p.Show()
					self.reverseLookupPanels.append(p)

		# GM Drop Editor: attach the per-page Edit button (no-op for non-GMs
		# or when the feature flag is off). Safe to call here -- the special
		# page is only ever opened on demand while the player is in-game.
		# Wrapped so a failure here can never abort SpecialPageWindow.__init__
		# (OpenSpecialPage swallows ReferenceError, which would hide the cause).
		try:
			self._DropEditor_Setup()
		except Exception:
			import traceback
			dbg.TraceError("DropEditor SpecialPage _DropEditor_Setup call: " +
						   traceback.format_exc())

	def _BuildBuyColumnRows(self, purchasableVnums):
		"""Rows for the buy column: what this item BUYS (tagged [Buy]) plus every
		growth-pet / buffi / growth-mount upgrade step that CONSUMES it.
		Returns [(label, vnum, click_action, tip_lines), ...]."""
		rows = []

		buyTag = localeinfo.WIKI_USE_TAG_BUY
		for vnum in (purchasableVnums or []):
			try:
				vnum = int(vnum)
			except (TypeError, ValueError):
				continue
			item.SelectItem(vnum)
			name = item.GetItemName() or ("#%d" % vnum)
			rows.append(("%s %s" % (buyTag, name), vnum, None, None))

		if app.USE_EXTENDED_WIKI_USAGE:
			import ingamewikisystemuse
			for usage in ingamewikisystemuse.GetSystemUsages(self.vnum):
				rows.append((
					ingamewikisystemuse.GetRowLabel(usage),
					0,
					ingamewikisystemuse.MakeHelpAction(usage["sys"]),
					ingamewikisystemuse.GetRowTooltipLines(usage)))

		return rows

	# The contents list never reaches past x~322 (7 slots at ELEM_PITCH_X 36 from SECTION_X 70)
	# and its headers are centred on 270, so the right end of the 540-wide band is free for the
	# outfit the box contains. Parented to self.bg rather than the scroll board so it holds its
	# place while the list scrolls under it.
	def _BuildBundleSetPreview(self, bandHeight):
		PREVIEW_X = 372
		PREVIEW_W = 160
		PREVIEW_MAX_H = 150
		BAND_TOP = 187

		slots = uiRenderTarget.GetBundleBoxSlots(self.vnum)
		if not slots:
			return

		height = min(PREVIEW_MAX_H, bandHeight - 12)
		if height < 60:
			return

		if not self.bundleRender:
			# no wheel zoom: the band scrolls on the wheel and the traversal reaches this window
			# wherever the cursor sits, so capturing it here would break scrolling the page
			self.bundleRender = uiRenderTarget.SetPreviewRender(
				self.bg, PREVIEW_X, BAND_TOP + 6, PREVIEW_W, height)
			self.bundleRender.SetEvent(ui.__mem_func__(self._OnBundleSetPreviewClick), "mouse_click")
		else:
			self.bundleRender.SetPosition(PREVIEW_X, BAND_TOP + 6)
			self.bundleRender.Show()

		self.bundleRender.SetSlots(slots, net.GetMainActorRace())

	def _OnBundleSetPreviewClick(self, *args):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler:
			interfaceHandler.OpenRenderTargetWindow(0, self.vnum)

	def _BuildBundleContents(self, bundleData):
		"""Populate self.bonusScrollBoard with the bundle box's JSON-driven
		Contents section (categories the player picks from + guaranteed
		items). Returns the total content height in px.

		Flattened to ONE scroll level: BundleContentRow renders its slots
		directly into this band, with no inner scrollBoard/peekWindow/
		scrollBar of its own (see BundleContentRow's docstring for why
		nesting ChestPeekWindow here used to leak outside the band once it
		was wheel-scrolled). self.bonusPeekWindow -- this page's own scroll
		viewport -- is the single SUB clip mask handed to every row/header/
		marker built here, matching the sub-mask idiom every other
		scrolling row in this file already uses."""
		SECTION_X = 70
		SECTION_W = 400
		HEADER_H = 16
		SECTION_GAP = 8

		y = 4

		for cat in (bundleData.get("categories") or []):
			label = cat.get("label", "")
			localizedLabel = getattr(localeinfo, "BUNDLEBOX_CAT_" + label,
				label.replace("_", " ").title())
			chooseFmt = getattr(localeinfo, "BUNDLEBOX_WIKI_CHOOSE", "Choose %s:")

			header = ui.TextLine()
			header.SetParent(self.bonusScrollBoard)
			header.AddFlag("attach")
			header.AddFlag("not_pick")
			if app.USE_CLIP_MASK:
				header.SetSubClippingMaskWindow(self.bonusPeekWindow)
			header.SetHorizontalAlignCenter()
			header.SetPackedFontColor(0xfffad390)
			header.SetText("%s %s" % (chooseFmt % cat.get("pick", 1), localizedLabel))
			header.SetPosition(int(SECTION_X + SECTION_W / 2), y)
			header.Show()
			self.bundleSections.append(header)
			y += HEADER_H

			row = BundleContentRow(SECTION_W, self.bonusPeekWindow,
				ui.__mem_func__(self.OnOverIn), ui.__mem_func__(self.OnOverOut),
				ui.__mem_func__(self.OnRightDown))
			row.SetParent(self.bonusScrollBoard)
			row.AddFlag("attach")
			if app.USE_CLIP_MASK:
				row.SetSubClippingMaskWindow(self.bonusPeekWindow)
			row.SetPosition(SECTION_X, y)
			row.Show()
			self.bundleSections.append(row)

			for itemRow in (cat.get("items") or []):
				if not itemRow:
					continue
				vnum = int(itemRow[0])
				count = int(itemRow[1]) if len(itemRow) > 1 else 1
				sex = int(itemRow[2]) if len(itemRow) > 2 else 0
				row.AddItem(vnum, count, sex)

			y += row.GetHeight() + SECTION_GAP

		guaranteed = bundleData.get("guaranteed") or []
		if guaranteed:
			header = ui.TextLine()
			header.SetParent(self.bonusScrollBoard)
			header.AddFlag("attach")
			header.AddFlag("not_pick")
			if app.USE_CLIP_MASK:
				header.SetSubClippingMaskWindow(self.bonusPeekWindow)
			header.SetHorizontalAlignCenter()
			header.SetPackedFontColor(0xfffad390)
			header.SetText(getattr(localeinfo, "BUNDLEBOX_GUARANTEED", "Always included"))
			header.SetPosition(int(SECTION_X + SECTION_W / 2), y)
			header.Show()
			self.bundleSections.append(header)
			y += HEADER_H

			row = BundleContentRow(SECTION_W, self.bonusPeekWindow,
				ui.__mem_func__(self.OnOverIn), ui.__mem_func__(self.OnOverOut),
				ui.__mem_func__(self.OnRightDown))
			row.SetParent(self.bonusScrollBoard)
			row.AddFlag("attach")
			if app.USE_CLIP_MASK:
				row.SetSubClippingMaskWindow(self.bonusPeekWindow)
			row.SetPosition(SECTION_X, y)
			row.Show()
			self.bundleSections.append(row)

			for itemRow in guaranteed:
				if not itemRow:
					continue
				vnum = int(itemRow[0])
				count = int(itemRow[1]) if len(itemRow) > 1 else 1
				row.AddItem(vnum, count)

			y += row.GetHeight() + SECTION_GAP

		return y

	def __del__(self):
		try:
			self._DropEditor_Unmount()
		except Exception:
			pass
		if wiki.GetBaseClass():
			wiki.GetBaseClass().objList.pop(long(id(self)))

		ui.Window.__del__(self)
	
	def OnRunMouseWheel(self, length):
		if not self.bonusScrollBoard:
			return
		
		if self.bonusScrollBoard.GetHeight() == self.bonusPeekWindow.GetHeight():
			return
		
		if self.bonusPeekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def ChangeElementSize(self, elem, sizeDiff):
		if self.bonusScrollBoard:
			self.bonusScrollBoard.SetSize(self.bonusScrollBoard.GetWidth(), self.bonusScrollBoard.GetHeight() + sizeDiff)
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.bonusScrollBoard.GetLocalPosition()[1] + val, -self.bonusScrollBoard.GetHeight() + self.bonusPeekWindow.GetHeight()))
		if self.bonusScrollBoard:
			self.bonusScrollBoard.SetPosition(0, curr)
	
	def OnOverIn(self, vnum, render, _shop_index = None, _item_index = None):
		# Tail params are populated by ChestPeekWindow when the slot was
		# added with shop indices (LoadShopData path) -- they let us echo
		# the same price tooltip the dedicated shops page renders.
		if not self.toolTip:
			return

		self.toolTip.ClearToolTip()
		self.toolTip.AddItemData(vnum, [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)], 0, noRender = render)
		self.toolTip.AppendWikiAccessoryMaterials(vnum)

		# Drop-chance tier tag: only on real monster drop pages (not shop
		# NPCs, not cube NPCs, not item pages). Looks up
		# game_data.mobDropDict[self.vnum][vnum]; appends a colored tier
		# line when a PPM value is found.
		if (self.isMonster
				and not getattr(self, "isShopNpc", False)
				and not getattr(self, "isCubeNpc", False)):
			try:
				chance_ppm = game_data.mobDropDict.get(int(self.vnum), {}).get(int(vnum), 0)
			except (TypeError, ValueError):
				chance_ppm = 0
			if chance_ppm > 0:
				# Tier the drop relative to this mob's source class (stone /
				# boss / ...) so the same % reads rarer on rarely-killed bosses.
				try:
					src_class = game_data.mobClassDict.get(int(self.vnum), SRC_CLASS_REGULAR)
				except (TypeError, ValueError):
					src_class = SRC_CLASS_REGULAR
				tier_text, tier_color = GetDropChanceTier(chance_ppm, src_class)
				if tier_text:
					# GMs additionally see the exact baked rate; normal players
					# see only the rarity tier word.
					if WikiViewerIsGM():
						pct_text = FormatDropPercent(chance_ppm)
						if pct_text:
							tier_text = "%s - %s" % (tier_text, pct_text)
					self.toolTip.AppendTextLine(tier_text, tier_color)

		if _shop_index is None or _item_index is None:
			return
		if not getattr(self, "isShopNpc", False):
			return
		if self.vnum not in game_data.shopDict:
			return
		if _shop_index not in game_data.shopDict[self.vnum]:
			return

		items = game_data.shopDict[self.vnum][_shop_index].get("items", [])
		if _item_index >= len(items):
			return
		itemEntry = items[_item_index]
		if len(itemEntry) < 4:
			return

		# Mirrors WikiShopWindow.OnOverIn -- same price_type dispatch.
		self.toolTip.isShopItemNpc = True
		_price_type = itemEntry[2]
		_price_data = itemEntry[3]

		if _price_type == 1:
			if app.ENABLE_CHEQUE_SYSTEM:
				self.toolTip.AppendPrice(_price_data[0][1], 0)
			else:
				self.toolTip.AppendPrice(_price_data[0][1])
		elif _price_type == 2:
			self.toolTip.AppendPriceBySecondaryCoin(_price_data[0][1], 0)
		elif app.ENABLE_SHOPEX_RENEWAL:
			if _price_type == 5:
				_price = _price_data[0][1]
				self.toolTip.AppendTextLine(
					localeinfo.TOOLTIP_BUYPRICE % localeinfo.NumberToGayaString(_price),
					self.toolTip.GetPriceColor(_price))
			else:
				if app.SHOPEX_RENEWAL_EXTEND_ITEM_VNUM_PRICES:
					_have_title = False
					for price in _price_data:
						if not _have_title:
							_have_title = True
							self.toolTip.AddShopEXItem(price[0], price[1])
							continue
						self.toolTip.AddShopEXItem(price[0], price[1], True)
				else:
					self.toolTip.AddShopEXItem(_price_data[0][0], _price_data[0][1])

		AppendShopStockLine(self.toolTip, itemEntry)

	def OnOverOut(self):
		if not self.toolTip:
			return

		self.toolTip.Hide()

	def OnRightDown(self, itemVnum = 0):
		if itemVnum == 0:
			return

		if app.ENABLE_RENDER_TARGET and\
			app.IsPressed(app.DIK_LSHIFT):
				if uiRenderTarget.IsCanShowItems(itemVnum):
					interfaceHandler = systemSetting.GetInterfaceHandler()
					if interfaceHandler:
						interfaceHandler.OpenRenderTargetWindow(0,itemVnum)

	def OnRender(self):
		if self.additionalLoaded:
			return

		if self.isMonster or wiki.IsSet(self.vnum):
			self.additionalLoaded = True
			# Wrap the parse so a single malformed shop/cube entry can't
			# bubble up through OnRender and leave the page un-renderable.
			# The page stays visible; just the originInfo column may be
			# empty until the issue is fixed.
			try:
				self.originInfo.ParseTextlines()
			except Exception:
				import traceback
				dbg.TraceError(
					"SpecialPageWindow.OnRender: originInfo.ParseTextlines "
					"raised for vnum=%s:\n%s" % (self.vnum, traceback.format_exc()))

	def OpenWindow(self):
		wndMgr.Show(self.hWnd)

	def NoticeMe(self):
		# While the GM Drop Editor overlay is mounted, don't repopulate the
		# read-only drop grid underneath it -- ChestPeekWindow.AddItem has no
		# dedup and the grid is hidden anyway.
		# Shop NPCs are populated once in __init__ from local shopDict, so
		# NoticeMe (which fires on server wiki-info callback) is a no-op for
		# them. Cube NPCs likewise have no drop table; their recipes are
		# loaded straight from craftingDict in __init__.
		if (not getattr(self, "editMode", False)
				and not getattr(self, "isShopNpc", False)
				and not getattr(self, "isCubeNpc", False)):
			self.LoadDropData()

		if self.isMonster and not self.originInfoParsed:
			self.originInfoParsed = True
			self.originInfo.ParseTextlines()

	def LoadShopData(self):
		# Walk every shop tab the NPC owns and pour the items into the
		# detail page's ChestPeekWindow with (shop_index, item_index) so
		# OnOverIn can pull the matching price entry.
		if not getattr(self, "isShopNpc", False):
			return
		if self.vnum not in game_data.shopDict:
			return
		shopData = game_data.shopDict[self.vnum]
		try:
			tabKeys = sorted(shopData.keys())
		except Exception:
			tabKeys = list(shopData.keys())
		for shop_index in tabKeys:
			items = shopData[shop_index].get("items", [])
			for _item_index, itemEntry in enumerate(items):
				if not itemEntry:
					continue
				vnumFrom = itemEntry[0]
				count = itemEntry[1] if len(itemEntry) > 1 else 0
				self.itemContainer.AddItem(vnumFrom, count, shop_index, _item_index)

	def LoadDropData(self):
		if not self.isMonster:
			return

		# Shop NPCs don't have a drop table; LoadShopData handles their
		# itemContainer. Cube NPCs likewise have no drop list -- their
		# itemContainer just stays empty (the recipe list renders below).
		if getattr(self, "isShopNpc", False):
			return
		if getattr(self, "isCubeNpc", False):
			return

		if not wiki.IsSet(self.vnum, True):
			wiki.LoadInfo(long(id(self)), self.vnum, True)
			return

		lst = wiki.GetMobInfo(self.vnum)
		if not lst:
			return

		sizeLst = []
		orderedLst = []

		for i in lst:
			if i[0] < wiki.CONTROL_ITEM_VNUM:
				continue

			item.SelectItem(i[0])
			size = item.GetItemSize()[1]

			lastPos = 0
			for k in xrange(len(sizeLst)):
				if sizeLst[k] < size:
					break

				lastPos += 1

			sizeLst.insert(lastPos, size)
			orderedLst.insert(lastPos, i[:])

		for i in orderedLst:
			count = (i[1] if i[1] > 1 else 0)
			self.itemContainer.AddItem(i[0], count)

	# -----------------------------------------------------------------------
	# GM Drop Editor integration (lives on the detail page, not the listing).
	# Monster/stone pages edit mob_drop_item.txt; chest pages edit
	# special_item_group.txt. group_name is sent empty -- the server matches
	# the group by vnum alone (see ITEM_MANAGER::GetMobGroupByName).
	# -----------------------------------------------------------------------
	def _DropEditor_Setup(self):
		# Whole body guarded: this runs at the tail of __init__, and a stray
		# exception here would otherwise be swallowed by OpenSpecialPage's
		# `except ReferenceError` and silently prevent the page from opening.
		self.editMode = False
		self._dropEditorPanel = None
		self.editButton = None
		self._dropEditorFileKind = -1
		try:
			if not _DropEditor_IsAllowed():
				return

			# Shop NPCs share the monster page layout but have no entry in
			# mob_drop_item.txt -- skip the editor button so a GM doesn't
			# get an empty drop-edit overlay for them. Cube NPCs same.
			if getattr(self, "isShopNpc", False):
				return
			if getattr(self, "isCubeNpc", False):
				return

			if self.isMonster:
				self._dropEditorFileKind = 0      # ingamewikieditor.FK_MOB_DROP
			elif getattr(self, "isChest", False):
				self._dropEditorFileKind = 1      # ingamewikieditor.FK_SPECIAL
			else:
				return                            # plain item / refine page

			# Parent the button to the SpecialPageWindow itself, NOT self.bg:
			# self.bg carries the "not_pick" flag, which stops its children
			# from receiving mouse clicks.
			#
			# Position: the previous top-right placement (self.GetWidth() - 90,
			# 2) sat directly on top of the monster page's location subtitle
			# (subTitleBg3 at x=415, y=1, 125x20) and the corner of the
			# location panel (originInfo at x=415, y=22, 125x142), which made
			# the location/spawn-map area unusable for GMs. Anchor the button
			# at the LEFT edge of the drop-list subtitle bar instead -- the
			# subtitle text is centered, so a small button at the left edge
			# doesn't cover it, and the location panel is fully clear.
			#   * monster pages: subTitleBg1 at x=127, button at x=131
			#   * item/chest pages: subTitleBg1 at x=189, button at x=193
			self.editButton = ui.Button()
			self.editButton.SetParent(self)
			self.editButton.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
			self.editButton.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
			self.editButton.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
			self.editButton.SetText("Edit drops")
			self.editButton.SetPosition(131 if self.isMonster else 193, 2)
			self.editButton.SAFE_SetEvent(self._DropEditor_Mount)
			self.editButton.Show()
		except Exception:
			import traceback
			dbg.TraceError("DropEditor SpecialPage setup: " +
						   traceback.format_exc())
			self.editButton = None

	def _DropEditor_Mount(self):
		# Open the drop editor. It is a standalone top-level ("float") window,
		# NOT a child of the wiki: it sits to the right of the special page,
		# outside the wiki's rect, and a child positioned outside its parent
		# would not be click-pickable. It opens next to the special page but is
		# independently movable from there.
		if self._dropEditorPanel is not None:
			return
		try:
			import ingamewikieditor
			GAP = 6
			# close_cb is wrapped weak: a raw bound method would form a strong
			# SpecialPageWindow <-> DropEditorWindow cycle, and both classes
			# define __del__, so Python 2.7 would never collect either (it
			# would leak on the CloseBaseWindows path, which drops the page
			# without calling Hide()).
			panel = ingamewikieditor.DropEditorWindow(
				self._dropEditorFileKind, int(self.vnum), "",
				close_cb=ui.__mem_func__(self._DropEditor_Unmount))
			gx, gy = self.GetGlobalPosition()
			panel.SetPosition(gx + self.GetWidth() + GAP, gy)
			panel.Show()
			panel.SetTop()
			self._dropEditorPanel = panel
			self.editMode = True
			if self.editButton:
				try: self.editButton.Hide()
				except Exception: pass
			# Hide the read-only drop widget underneath -- it shows stale,
			# client-cached drops that would contradict the live editor.
			if self.isMonster:
				try: self.itemContainer.Hide()
				except Exception: pass
			else:
				try: self.bonusInfo.Hide()
				except Exception: pass
		except Exception:
			import traceback
			dbg.TraceError("DropEditor SpecialPage mount: " +
						   traceback.format_exc())

	def _DropEditor_Unmount(self):
		panel = getattr(self, "_dropEditorPanel", None)
		if panel is not None:
			try:
				panel.Close()
			except Exception:
				pass
			self._dropEditorPanel = None
		self.editMode = False
		if getattr(self, "editButton", None):
			try: self.editButton.Show()
			except Exception: pass
		if getattr(self, "isMonster", False):
			try: self.itemContainer.Show()
			except Exception: pass
		else:
			bonus = getattr(self, "bonusInfo", None)
			if bonus is not None:
				try: bonus.Show()
				except Exception: pass

	def Show(self):
		wndMgr.Show(self.hWnd)

	def Hide(self):
		# Tearing down the special page (wiki history nav, closing the wiki)
		# must also tear down the docked editor -- it is parented to the wiki
		# root, not to us, so it would otherwise be left orphaned on screen.
		try:
			self._DropEditor_Unmount()
		except Exception:
			pass
		wndMgr.Hide(self.hWnd)

class SimpleTextLoader(ui.Window):
	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 0
	SCROLL_SPEED = 50
	
	def __init__(self):
		ui.Window.__init__(self)
		self.SetSize(*mainBoardSize)

		self.elements = []
		self._docModels = []
		self.images = []
		self.scrollBar = None
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(self.GetWidth() - 8 - 5, self.GetHeight() - 5)

		self.peekWindow.SetPosition(5, 5)

		if not app.USE_CLIP_MASK:
			self.peekWindow.SetInsideRender(True)

		self.peekWindow.Show()

		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		#self.scrollBoard.SetSize(self.GetWidth() + 125, self.GetHeight() - 5)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")

		if app.USE_CLIP_MASK:
			self.scrollBoard.SetClippingMaskWindow(self.peekWindow)

		self.scrollBoard.Show()

		self.RegisterScrollBar()

		# >>> WIKI REHAUL PHASE 1: live-reload support. currentFile remembers the
		# last page so a dev can re-read it in place; reloadBtn is revealed only on
		# the test server (see LoadFile). <<<
		self.currentFile = None
		self.reloadBtn = ui.Button()
		self.reloadBtn.SetParent(self)
		self.reloadBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.reloadBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.reloadBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.reloadBtn.SetText("Reload v59-GEAR")
		self.reloadBtn.SetPosition(8, 4)
		self.reloadBtn.SAFE_SetEvent(self.ReloadCurrent)
		self.reloadBtn.Hide()
		self.itemBuilderBtn = ui.Button()
		self.itemBuilderBtn.SetParent(self)
		self.itemBuilderBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.itemBuilderBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.itemBuilderBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.itemBuilderBtn.SetText(localeinfo.WIKI_BUILDER_BUTTON)
		self.itemBuilderBtn.SetPosition(78, 4)
		self.itemBuilderBtn.SAFE_SetEvent(self.OpenItemBuilder)
		self.itemBuilderBtn.Hide()
		# >>> WIKI REHAUL PHASE 4: in-place block editor (doc pages, dev only). <<<
		self.docNodes = []
		self.editMode = False
		self.editSel = -1
		self.editBtn = ui.Button()
		self.editBtn.SetParent(self)
		self.editBtn.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.editBtn.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.editBtn.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.editBtn.SetText("Edit")
		self.editBtn.SetPosition(148, 4)
		self.editBtn.SAFE_SetEvent(self.ToggleEditMode)
		self.editBtn.Hide()
	
	def ParseToken(self, data):
		data = data.replace(chr(10), "").replace(chr(13), "")
		if not (len(data) and data[0] == "["):
			return (False, {}, data)
		
		fnd = data.find("]")
		if fnd <= 0:
			return (False, {}, data)
		
		content = data[1:fnd]
		data = data[fnd+1:]
		
		content = content.split(";")
		container = {}
		
		for i in content:
			i = i.strip()
			splt = i.split("=")
			
			if len(splt) == 1:
				container[splt[0].lower().strip()] = True
			else:
				# >>> WIKI REHAUL PHASE 0: lower-case the KEY only; keep the value's
				# original case so paths, button text and linkindex filenames are not
				# silently mangled, and re-join on '=' so a value may itself contain '='.
				# Old: container[splt[0].lower().strip()] = splt[1].lower().strip()
				container[splt[0].lower().strip()] = "=".join(splt[1:]).strip()
		
		return (True, container, data)
	
	def GetColorFromString(self, strCol):
		retData = []
		dNum = 4
		hCol = long(strCol, 16)
		
		if hCol <= 0xFFFFFF:
			retData.append(1.0)
			dNum = 3
		
		for i in xrange(dNum):
			retData.append(float((hCol >> (8 * i)) & 0xFF) / 255.0)
		
		retData.reverse()
		return retData

	def LoadFile(self, filename):
		del self._docModels[:]
		del self.elements[:]
		del self.images[:]
		self.editMode = False
		self.editSel = -1
		
		self.scrollBoard.SetSize(0, 0)
		self.UpdateScrollbar()
		
		#open_filename = "{}/wiki/{}".format(app.GetLocalePath(), filename)
		# >>> WIKI REHAUL PHASE 0/1 <<<
		# Phase 1: a loose UserData/wiki/<file> overrides the packed page on the
		# test server so authors iterate without repacking. Phase 0: always close
		# the handle, drop the throwaway first line (BOM-dodge convention), trim
		# trailing blank lines, and never let one bad line blank the whole page
		# (each line renders under try/except).
		open_filename = "wiki/{}".format(filename)
		self.currentFile = filename
		_wikiLines = []
		try:
			(open_filename, loadF) = self._ResolveWikiSource(filename)
			try:
				_wikiLines = loadF.readlines()
			finally:
				try:
					loadF.close()
				except:
					pass
		except Exception:
			self._RenderWikiError(0, None, missing=filename)
		_headerLine = _wikiLines[0] if _wikiLines else ""
		if _wikiLines:
			_wikiLines = _wikiLines[1:]
			while _wikiLines and not _wikiLines[-1].replace(chr(10), "").replace(chr(13), "").strip():
				_wikiLines.pop()
		if self._WikiDevMode():
			self.reloadBtn.Show()
			self.itemBuilderBtn.Show()
			if open_filename[:8] == "UserData":
				try:
					chat.AppendChat(chat.CHAT_TYPE_INFO, "[wiki] loose: %s" % open_filename)
				except:
					pass
		else:
			self.reloadBtn.Hide()
			self.itemBuilderBtn.Hide()
		self.editBtn.Hide()
		if self._IsDocMode(_headerLine):
			if self._WikiDevMode():
				self.editBtn.SetText("Edit")
				self.editBtn.Show()
			self._RenderDoc(_wikiLines)
			self.UpdateScrollbar()
			wndMgr.Show(self.hWnd)
			return
		for _lineNo in xrange(len(_wikiLines)):
			_rawLine = _wikiLines[_lineNo]
			i = _rawLine
			try:
				(ret, tokenMap, i) = self.ParseToken(i)
			
				if ret:
					if tokenMap.has_key("banner_img"):
						if wiki.GetBaseClass():
							wiki.GetBaseClass().header.LoadImage(tokenMap["banner_img"])
							wiki.GetBaseClass().header.Show()
					
						tokenMap.pop("banner_img")
				
					if tokenMap.has_key("img"):
						cimg = ui.ExpandedImageBox()
						cimg.SetParent(self.scrollBoard)
						cimg.AddFlag("attach")
						cimg.AddFlag("not_pick")
						cimg.LoadImage(tokenMap["img"])
						cimg.Show()
					
						tokenMap.pop("img")
					
						x = 0
						if tokenMap.has_key("x"):
							x = int(tokenMap["x"])
							tokenMap.pop("x")
					
						y = 0
						if tokenMap.has_key("y"):
							y = int(tokenMap["y"])
							tokenMap.pop("y")


						if tokenMap.has_key("center_align"):
							cimg.SetPosition(self.peekWindow.GetWidth() / 2 - cimg.GetWidth() / 2, y)
							#cimg.SetWindowHorizontalAlignCenter()
							tokenMap.pop("center_align")
						elif tokenMap.has_key("right_align"):
							cimg.SetPosition(self.peekWindow.GetWidth() - cimg.GetWidth(), y)
							tokenMap.pop("right_align")
						else:
							cimg.SetPosition(x, y)
					
						self.images.append(cimg)

					if tokenMap.has_key("item"):
						itemVnum = int(tokenMap["item"])
						tokenMap.pop("item")

						metinSlot = [0 for j in xrange(player.METIN_SOCKET_MAX_NUM)]
						attrSlot = [[0,0] for j in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

						if tokenMap.has_key("item_socket"):
							metinSlotData = tokenMap["item_socket"].split("|")
							tokenMap.pop("item_socket")
							for index, metin in enumerate(metinSlotData):
								if index < player.METIN_SOCKET_MAX_NUM:
									metinSlot[index] = int(metin)

						if tokenMap.has_key("item_apply"):
							attrSlotData = tokenMap["item_apply"].split("|")
							tokenMap.pop("item_apply")
							for index, item_apply in enumerate(attrSlotData):
								attrSplit = item_apply.split(":")
								if len(attrSplit) == 2 and index < player.ATTRIBUTE_SLOT_MAX_NUM:
									attrSlot[index] = [int(attrSplit[0]), int(attrSplit[1])]

						item.SelectItem(itemVnum)
						cimg = ui.ExpandedImageBox()
						cimg.SetParent(self.scrollBoard)
						if item.GetIconImageFileName().find("gr2") == -1:
							cimg.LoadImage(item.GetIconImageFileName())
						else:
							cimg.LoadImage("icon/item/27995.tga")
						cimg.SAFE_SetStringEvent("MOUSE_OVER_IN",self.OverInItem, itemVnum, metinSlot, attrSlot)
						cimg.SAFE_SetStringEvent("MOUSE_OVER_OUT",self.OverOutItem)
						cimg.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.OnClickItem), 0, itemVnum)
						cimg.Show()
						x = 0
						if tokenMap.has_key("x"):
							x = int(tokenMap["x"])
							tokenMap.pop("x")
						y = 0
						if tokenMap.has_key("y"):
							y = int(tokenMap["y"])
							tokenMap.pop("y")
						if tokenMap.has_key("center_align"):
							cimg.SetPosition(self.scrollBoard.GetWidth() / 2 - cimg.GetWidth() / 2, y, True)
							tokenMap.pop("center_align")
						elif tokenMap.has_key("right_align"):
							cimg.SetPosition(self.scrollBoard.GetWidth() - cimg.GetWidth(), y, True)
							tokenMap.pop("right_align")
						else:
							cimg.SetPosition(x, y, True)

						self.images.append(cimg)

					if tokenMap.has_key("rendertarget"):
						import uiRenderTarget
						mobVnum = int(tokenMap["rendertarget"])
						tokenMap.pop("rendertarget")

						(width, height) = (47, 87)

						if tokenMap.has_key("width"):
							width = int(tokenMap["width"])
							tokenMap.pop("width")

						if tokenMap.has_key("height"):
							height = int(tokenMap["height"])
							tokenMap.pop("height")


						tmp = WikiRenderTarget(width, height)
						tmp.SetParent(self.scrollBoard)
						tmp.SetModel(mobVnum, False, False)

						tmp.SetMouseLeftButtonDownEvent(ui.__mem_func__(self.OnClickMonster), mobVnum)
						tmp.Show()

						if tokenMap.has_key("movable"):
							if int(tokenMap["movable"]):
								tmp.AddFlag("movable")
							tokenMap.pop("movable")


						if tokenMap.has_key("y"):
							y = int(tokenMap["y"])
							tokenMap.pop("y")
						if tokenMap.has_key("x"):
							x = int(tokenMap["x"])
							tokenMap.pop("x")						
						if tokenMap.has_key("center_align"):
							tmp.SetPosition(self.scrollBoard.GetWidth() / 2 - tmp.GetWidth() / 2, y, True)
							tokenMap.pop("center_align")
						elif tokenMap.has_key("right_align"):
							tmp.SetPosition(self.scrollBoard.GetWidth() - tmp.GetWidth(), y, True)
							tokenMap.pop("right_align")
						else:
							tmp.SetPosition(x, y, True)
						self.elements.append(tmp)

					if tokenMap.has_key("button"):
						button = tokenMap["button"].split("#")
						tokenMap.pop("button")
						if len(button) != 1:
							continue

						#tmp = ui.Button()
						tmp = ui.ExpandedImageBox()
						tmp.SetParent(self.scrollBoard)
						tmp.LoadImage(button[0])
						tmp.SetSize(tmp.GetWidth(), tmp.GetHeight())
						#tmp.SetUpVisual(button[0])
						#tmp.SetOverVisual(button[1])
						#tmp.SetDownVisual(button[2])
						tmp.Show()
						if tokenMap.has_key("linkindex"):
							linkindex = tokenMap["linkindex"]
							#tmp.SetEvent(ui.__mem_func__(wiki.GetBaseClass().GoToCustomPage), linkindex)
							tmp.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(wiki.GetBaseClass().GoToCustomPage), linkindex)
							tokenMap.pop("linkindex")

						if tokenMap.has_key("text"):
							tmp.SetText(tokenMap["text"])
							tokenMap.pop("text")
						if tokenMap.has_key("y"):
							y = int(tokenMap["y"])
							tokenMap.pop("y")
						if tokenMap.has_key("x"):
							x = int(tokenMap["x"])
							tokenMap.pop("x")
						if tokenMap.has_key("center_align"):
							tmp.SetPosition(self.scrollBoard.GetWidth() / 2 - tmp.GetWidth() / 2, y, True)
							tokenMap.pop("center_align")
						elif tokenMap.has_key("right_align"):
							tmp.SetPosition(self.scrollBoard.GetWidth() - tmp.GetWidth(), y, True)
							tokenMap.pop("right_align")
						else:
							tmp.SetPosition(x, y, True)
						self.elements.append(tmp)



				if ret and not len(i):
					continue
			
				tmp = ui.Window()
				tmp.SetParent(self.scrollBoard)
				tmp.SetWindowHorizontalAlignRight()
				tmp.AddFlag("attach")
				tmp.AddFlag("not_pick")
			
				tmp.txt = ui.TextLine()
				tmp.txt.SetParent(tmp)
				if tokenMap.has_key("font_size"):
					splt = localeinfo.UI_DEF_FONT.split(":")
					tmp.txt.SetFontName(splt[0]+":"+tokenMap["font_size"])
					tokenMap.pop("font_size")
				else:
					tmp.txt.SetFontName(localeinfo.UI_DEF_FONT)
				tmp.txt.SetText(i)
				#if localeinfo.IsARABIC():
					#self.textLine.SetWindowHorizontalAlignCenter()
					#tmp.txt.SetWindowHorizontalAlignRight()
				tmp.txt.Show()
				tmp.SetSize(*tmp.txt.GetTextSize())
			
				if len(i) > 0 and i[0] == "*":
					tmp.txt.SetText(i[1:])
				
					tmp.img = ui.ExpandedImageBox()
					tmp.img.SetParent(tmp)
					tmp.img.AddFlag("attach")
					tmp.img.AddFlag("not_pick")
					tmp.img.LoadImage("d:/ymir work/ui/wiki/arrow_2.tga")
					tmp.img.Show()
				
					tmp.SetSize(tmp.img.GetWidth() + 5 + tmp.txt.GetTextSize()[0], max(tmp.img.GetHeight(), tmp.txt.GetTextSize()[1]))
					tmp.img.SetPosition(0, abs(tmp.GetHeight() / 2 - tmp.img.GetHeight() / 2))
				
					tmp.txt.SetPosition(tmp.img.GetWidth() + 5, abs(tmp.GetHeight() / 2 - tmp.txt.GetTextSize()[1] / 2) - 1)

				if tokenMap.has_key("color"):
					fontColor = self.GetColorFromString(tokenMap["color"])
					tmp.txt.SetPackedFontColor(grp.GenerateColor(fontColor[0], fontColor[1], fontColor[2], fontColor[3]))
				
					tokenMap.pop("color")
			
				addPadding = 0
				totalElem = len(self.elements)
			
				if tokenMap.has_key("y_padding"):
					addPadding = int(tokenMap["y_padding"])
					tokenMap.pop("y_padding")
			
				if totalElem > 0:
					lastIndex = totalElem
				
					self.elements.insert(lastIndex, tmp)
					totalElem += 1
				
					for i in xrange(lastIndex, totalElem):
						self.elements[i].SetPosition(0,\
							(0 if i ==0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + addPadding))
				else:
					self.elements.append(tmp)
					tmp.SetPosition(0, addPadding)
			
				if tokenMap.has_key("center_align"):
					tmp.SetPosition(self.peekWindow.GetWidth() / 2 - tmp.GetWidth() / 2, tmp.GetLocalPosition()[1])
					tokenMap.pop("center_align")
				elif tokenMap.has_key("right_align"):
					tmp.SetPosition(self.peekWindow.GetWidth() - tmp.GetWidth(), tmp.GetLocalPosition()[1])
					tokenMap.pop("right_align")
				elif tokenMap.has_key("x_padding"):
					tmp.SetPosition(int(tokenMap["x_padding"]), tmp.GetLocalPosition()[1])
					tokenMap.pop("x_padding")
			
				tmp.Show()
			
				self.scrollBoard.SetSize(self.peekWindow.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		
			except Exception:
				self._RenderWikiError(_lineNo + 2, _rawLine)
		for i in self.images:
			mxSize = i.GetLocalPosition()[1] + i.GetHeight()
			if mxSize > self.scrollBoard.GetHeight():
				self.scrollBoard.SetSize(self.peekWindow.GetWidth(), mxSize)
		
		self.UpdateScrollbar()
		wndMgr.Show(self.hWnd)

	def _WikiDevMode(self):
		# Author/dev mode for live tutorial editing. ON when the server marks
		# this a test server OR a local UserData/wiki/wiki_dev.key file exists
		# -- the .key is a server-independent escape hatch (same idea as the
		# drop editor's key gate) so editing works on any dev client even when
		# the server never sends the test-server flag.
		if app.IsEnableTestServerFlag():
			return True
		try:
			kf = open("UserData/wiki/wiki_dev.key", "r")
			kf.close()
			return True
		except:
			return False

	def _ResolveWikiSource(self, filename):
		# Test/dev authors can drop a loose UserData/wiki/<file> to iterate without
		# repacking; production always reads the packed wiki/<file>. UserData is
		# never packed, so the hooked open() (system.py) falls through to the real
		# on-disk file there.
		if self._WikiDevMode():
			userPath = "UserData/wiki/{}".format(filename)
			try:
				loose = open(userPath, 'r')
				return (userPath, loose)
			except:
				pass
		packPath = "wiki/{}".format(filename)
		return (packPath, open(packPath, 'r'))

	def _RenderWikiError(self, lineNo, rawLine, missing=None):
		# Phase 0: never blank the whole page on a single bad line or a missing
		# file. Drop a red marker into the text flow so the author sees exactly
		# what broke and where, and the rest of the page still renders.
		if missing is not None:
			msg = "[wiki] page not found: %s" % missing
		else:
			shown = (rawLine or "").replace(chr(10), "").replace(chr(13), "")
			if len(shown) > 80:
				shown = shown[:80] + "..."
			msg = "[wiki] line %d failed: %s" % (lineNo, shown)
		try:
			dbg.TraceError(msg)
		except:
			pass
		tmp = ui.Window()
		tmp.SetParent(self.scrollBoard)
		tmp.SetWindowHorizontalAlignRight()
		tmp.AddFlag("attach")
		tmp.AddFlag("not_pick")
		tmp.txt = ui.TextLine()
		tmp.txt.SetParent(tmp)
		tmp.txt.SetFontName(localeinfo.UI_DEF_FONT)
		tmp.txt.SetText(msg)
		tmp.txt.SetPackedFontColor(grp.GenerateColor(1.0, 0.25, 0.25, 1.0))
		tmp.txt.Show()
		tmp.SetSize(*tmp.txt.GetTextSize())
		totalElem = len(self.elements)
		if totalElem > 0:
			prev = self.elements[totalElem - 1]
			tmp.SetPosition(0, prev.GetLocalPosition()[1] + prev.GetHeight())
		else:
			tmp.SetPosition(0, 0)
		self.elements.append(tmp)
		tmp.Show()
		self.scrollBoard.SetSize(self.peekWindow.GetWidth(), self.scrollBoard.GetHeight() + tmp.GetHeight())

	def ReloadCurrent(self):
		# Test/dev live-reload: re-read the current page from disk in place so an
		# author can edit UserData/wiki/<file> and see it without closing the wiki
		# or repacking. Wired to the test-only Reload button.
		if self.currentFile:
			self.LoadFile(self.currentFile)

	def OpenItemBuilder(self):
		# Dev/test authoring: open the item-with-attributes builder bound to
		# this page so a generated [item=...; apply=...] token can be appended
		# straight into the loose UserData/wiki page and live-reloaded.
		try:
			import ingamewikiitembuilder
			ingamewikiitembuilder.Open(self)
		except Exception:
			import traceback, dbg
			dbg.TraceError("SimpleTextLoader.OpenItemBuilder:\n" + traceback.format_exc())

	def ToggleEditMode(self):
		# 4a: flip the in-place block editor. Edit mode re-renders the same live
		# model (self.docNodes) with a per-block edit gutter; off = clean page.
		if not self._WikiDevMode():
			return
		self.editMode = not getattr(self, "editMode", False)
		self.editSel = -1
		self.editBtn.SetText("Editing" if self.editMode else "Edit")
		self.RerenderDoc()

	def RerenderDoc(self):
		# Live editor update: re-render straight from the in-memory node model
		# WITHOUT re-reading the file (LoadFile reparses; this does not). Called
		# after the editor mutates self.docNodes.
		if getattr(self, "docNodes", None) is None:
			return
		del self._docModels[:]
		del self.elements[:]
		del self.images[:]
		self.scrollBoard.SetSize(0, 0)
		self._RenderDocNodes()
		self.UpdateScrollbar()

	def _EditBlockHandle(self, idx, yStart, yEnd, contentW, rtl):
		# Select-then-act gutter: a full-height clickable SELECT strip (bar +
		# index) per block. Click selects it (bar -> yellow) and ONLY the selected
		# block shows a clear action toolbar (Up / Dn / Del) -- one at a time keeps
		# it uncluttered. Actions mutate the live model + RerenderDoc.
		n = len(self.docNodes)
		sel = (idx == getattr(self, "editSel", -1))
		h = yEnd - yStart
		if h < 18:
			h = 18
		strip = ui.Window()
		strip.SetParent(self.scrollBoard)
		strip.SetSize(20, h)
		strip.SetMouseLeftButtonDownEvent(ui.__mem_func__(self._EditSelect), idx)
		strip.SetPosition(0, yStart)
		strip.Show()
		self.elements.append(strip)
		bar = ui.Bar()
		bar.SetParent(strip)
		bar.AddFlag("not_pick")
		bar.SetPosition(0, 0)
		bar.SetSize(3, h)
		bar.SetColor(0xffffcc33 if sel else 0xff4a90d9)
		bar.Show()
		strip.elBar = bar
		lbl = ui.TextLine()
		lbl.SetParent(strip)
		lbl.AddFlag("not_pick")
		lbl.SetFontName(self._DocFont(None))
		lbl.SetText("%d" % (idx + 1))
		lbl.SetPackedFontColor(grp.GenerateColor(*self.GetColorFromString("FFCC33" if sel else "9CD2FF")))
		lbl.SetHorizontalAlignLeft()
		lbl.SetPosition(6, 1)
		lbl.Show()
		strip.elLbl = lbl
		if not sel:
			return
		btns = []
		if idx > 0:
			btns.append(("Up", "9CD2FF", self._EditMoveUp))
		if idx < n - 1:
			btns.append(("Dn", "9CD2FF", self._EditMoveDown))
		btns.append(("Del", "FF6060", self._EditDelete))
		BW = 30
		plate = ui.Bar()
		plate.SetParent(self.scrollBoard)
		plate.AddFlag("not_pick")
		plate.SetPosition(24, yStart)
		plate.SetSize(8 + BW * len(btns), 18)
		plate.SetColor(0xdd0d141c)
		plate.Show()
		self.elements.append(plate)
		bx = 28
		for (lab, c, hnd) in btns:
			self._EditBtn(lab, bx, yStart + 1, BW - 4, c, hnd, idx)
			bx = bx + BW

	def _EditBtn(self, label, x, yStart, w, colorHex, handler, idx):
		# A clickable gutter/toolbar button. NO "attach" (else the click would
		# redirect to the root window, v40) and NO "not_pick" (must be pickable).
		win = ui.Window()
		win.SetParent(self.scrollBoard)
		win.SetSize(w, 16)
		win.SetMouseLeftButtonDownEvent(ui.__mem_func__(handler), idx)
		t = ui.TextLine()
		t.SetParent(win)
		t.AddFlag("not_pick")
		t.SetFontName(self._DocFont(None))
		t.SetText(label)
		t.SetPackedFontColor(grp.GenerateColor(*self.GetColorFromString(colorHex)))
		t.SetHorizontalAlignLeft()
		t.SetPosition(4, 1)
		t.Show()
		win.elTxt = t
		win.SetPosition(x, yStart)
		win.Show()
		self.elements.append(win)

	def _EditSelect(self, idx):
		# Click a block's gutter strip to select it (toggle off if already
		# selected); only the selected block shows the action toolbar.
		if idx == getattr(self, "editSel", -1):
			self.editSel = -1
		else:
			self.editSel = idx
		self.RerenderDoc()

	def _EditMoveUp(self, idx):
		if idx > 0 and idx < len(self.docNodes):
			self.docNodes.insert(idx - 1, self.docNodes.pop(idx))
			self.RerenderDoc()

	def _EditMoveDown(self, idx):
		if idx >= 0 and idx < len(self.docNodes) - 1:
			self.docNodes.insert(idx + 1, self.docNodes.pop(idx))
			self.RerenderDoc()

	def _EditDelete(self, idx):
		if idx >= 0 and idx < len(self.docNodes):
			del self.docNodes[idx]
			self.RerenderDoc()

	def _IsDocMode(self, headerLine):
		# Opt-in per page via a [DOC] first line, AND only when the doc-flow flag
		# is compiled in OR we are in author/dev mode -- legacy pages + production
		# are completely unaffected (no production page carries the marker).
		if not (getattr(app, "ENABLE_WIKI_DOC_FLOW", False) or self._WikiDevMode()):
			return False
		h = (headerLine or "").replace(chr(10), "").replace(chr(13), "").strip().lower()
		return h[:5] == "[doc]" or h[:5] == "[doc;" or h[:5] == "[doc "

	def _DocFont(self, size):
		if size:
			return localeinfo.UI_DEF_FONT.split(":")[0] + ":" + str(size)
		return localeinfo.UI_DEF_FONT

	def _DocAlign(self, tk):
		if tk.has_key("center_align"): return "center"
		if tk.has_key("right_align"): return "right"
		if tk.has_key("left_align"): return "left"
		return None

	def _DocInt(self, v, d):
		try: return int(v)
		except: return d

	def _ParseDoc(self, lines):
		# A [DOC] page -> a flat ordered list of typed nodes (the document model).
		# One renderer then stacks them with a single Y-cursor (no x/y in the file).
		nodes = []
		self._ParseDocInto(lines, nodes, [])
		return nodes

	def _ParseDocInto(self, lines, nodes, stack):
		# Parse lines into nodes, expanding [include=...] inline and collecting
		# [table cols=N] ... [row] ... [cell] ... [/table] into one table node
		# (each cell is itself a parsed node). `stack` guards include cycles.
		if len(stack) > 6:
			return
		i = 0
		total = len(lines)
		while i < total:
			raw = lines[i]
			(matched, tk, text) = self.ParseToken(raw)
			if matched and tk.has_key("include"):
				inc = tk.get("include")
				if inc and inc not in stack:
					ilines = None
					try:
						(path, f) = self._ResolveWikiSource(inc)
						try:
							ilines = f.readlines()
						finally:
							try:
								f.close()
							except:
								pass
					except Exception:
						nodes.append({"type": "para", "text": "[include missing: %s]" % inc, "color": "FF6060", "size": None, "align": None})
						ilines = None
					if ilines is not None:
						if ilines:
							ilines = ilines[1:]
						self._ParseDocInto(ilines, nodes, stack + [inc])
				i = i + 1
				continue
			if matched and tk.has_key("table"):
				cols = self._DocInt(tk.get("cols"), 2)
				talign = self._DocAlign(tk)
				rows = []
				i = i + 1
				while i < total:
					(m2, tk2, txt2) = self.ParseToken(lines[i])
					if m2 and tk2.has_key("/table"):
						i = i + 1
						break
					if m2 and tk2.has_key("row"):
						rows.append([])
					elif m2 and tk2.has_key("cell"):
						if not rows:
							rows.append([])
						parsed = self._ParseDocLine(txt2.strip())
						if parsed:
							rows[-1].append(parsed[0])
						else:
							rows[-1].append({"type": "para", "text": "", "color": None, "size": None, "align": None})
					i = i + 1
				nodes.append({"type": "table", "cols": cols, "rows": rows, "align": talign})
				continue
			for nn in self._ParseDocLine(raw):
				nodes.append(nn)
			i = i + 1

	def _ParseDocLine(self, raw):
		(matched, tk, text) = self.ParseToken(raw)
		out = []
		if matched:
			if tk.has_key("float"):
				out.append({"type": "float", "x": tk.get("x"), "y": tk.get("y"), "w": tk.get("w"), "h": tk.get("h"), "item": tk.get("item"), "img": tk.get("img"), "socket": tk.get("socket"), "apply": tk.get("apply"), "text": text, "color": tk.get("color"), "size": tk.get("font_size")})
				return out
			if tk.has_key("spacer"):
				out.append({"type": "spacer", "h": self._DocInt(tk.get("h"), 12)})
			if tk.has_key("divider"):
				out.append({"type": "divider", "style": tk.get("style", "long")})
			if tk.has_key("img"):
				out.append({"type": "img", "path": tk["img"], "align": self._DocAlign(tk)})
			if tk.has_key("item"):
				out.append({"type": "item", "vnum": tk["item"], "socket": tk.get("socket") or tk.get("item_socket"), "apply": tk.get("apply") or tk.get("item_apply"), "align": self._DocAlign(tk), "style": (tk.get("style") or "").lower(), "label": tk.get("label"), "size": tk.get("font_size")})
			if tk.has_key("mob"):
				out.append({"type": "mob", "vnum": tk["mob"], "align": self._DocAlign(tk), "label": tk.get("label")})
			if tk.has_key("require"):
				out.append({"type": "require", "point": tk.get("point"), "apply": tk.get("apply"), "have": tk.get("have"), "skill": tk.get("skill"), "level": tk.get("level"), "value": tk.get("value"), "text": text, "align": self._DocAlign(tk)})
				return out
			if tk.has_key("heading"):
				out.append({"type": "heading", "text": text}); return out
			if tk.has_key("section"):
				out.append({"type": "section", "text": text}); return out
			if text.strip():
				t = text
				bullet = (t[:1] == "*")
				if bullet: t = t[1:]
				out.append({"type": ("bullet" if bullet else "para"), "text": t, "color": tk.get("color"), "size": tk.get("font_size"), "align": self._DocAlign(tk)})
			return out
		st = text.strip()
		if not st: return [{"type": "spacer", "h": 10}]
		if st == "---": return [{"type": "divider", "style": "long"}]
		if st[:3] == "## ": return [{"type": "section", "text": st[3:].strip()}]
		if st[:2] == "# ": return [{"type": "heading", "text": st[2:].strip()}]
		if st[:2] == "- " or st[:2] == "* ": return [{"type": "bullet", "text": st[2:].strip(), "color": None, "size": None, "align": None}]
		return [{"type": "para", "text": text, "color": None, "size": None, "align": None}]

	def _DocMakeText(self, text, size, colorHex):
		host = ui.Window()
		host.SetParent(self.scrollBoard)
		host.AddFlag("attach")
		host.AddFlag("not_pick")
		host.txt = ui.TextLine()
		host.txt.SetParent(host)
		host.txt.SetFontName(self._DocFont(size))
		host.txt.SetText(text)
		if colorHex:
			col = self.GetColorFromString(colorHex)
			host.txt.SetPackedFontColor(grp.GenerateColor(col[0], col[1], col[2], col[3]))
		host.txt.Show()
		host.SetSize(*host.txt.GetTextSize())
		host.Show()
		self.elements.append(host)
		return host

	def _DocPlace(self, widget, y, align, contentW):
		# The engine's horizontal-align flag controls BOTH placement and,
		# for Arabic, text DIRECTION (AlignLeft renders Arabic L-to-R, which
		# is wrong). So pick the flag by alignment and pin with SetPosition(0,y).
		if align == "center":
			widget.SetWindowHorizontalAlignCenter()
			widget.SetPosition(0, y)
		elif align == "right":
			widget.SetWindowHorizontalAlignRight()
			widget.SetPosition(18, y)
		else:
			widget.SetWindowHorizontalAlignLeft()
			widget.SetPosition(18, y)

	def _DocOrnament(self, path, y, contentW):
		# Centered ornamental line from the wiki_new art set -- shared by
		# headings/sections (underline) and standalone dividers so every
		# structural separator looks identical across all doc pages.
		img = ui.ExpandedImageBox()
		img.SetParent(self.scrollBoard)
		img.AddFlag("attach")
		img.AddFlag("not_pick")
		img.LoadImage(path)
		img.Show()
		self.elements.append(img)
		self._DocPlace(img, y, "center", contentW)
		return y + img.GetHeight()

	def _DocBarText(self, bgPath, text, size, colorHex, y, contentW, rtl, rtlInset, plateAlign):
		# Title/section: a background plate from the wiki_new set with the
		# text centered on top (host window: image child + text child over
		# it). One path so every title (and every section) matches across
		# pages. Plate is centered in the content column.
		host = ui.Window()
		host.SetParent(self.scrollBoard)
		host.AddFlag("attach")
		host.AddFlag("not_pick")
		host.bg = ui.ExpandedImageBox()
		host.bg.SetParent(host)
		host.bg.AddFlag("attach")
		host.bg.AddFlag("not_pick")
		host.bg.LoadImage(bgPath)
		host.bg.SetPosition(0, 0)
		host.bg.Show()
		bw = host.bg.GetWidth()
		bh = host.bg.GetHeight()
		host.SetSize(bw, bh)
		host.txt = ui.TextLine()
		host.txt.SetParent(host)
		host.txt.SetFontName(self._DocFont(size))
		host.txt.SetText(text)
		if colorHex:
			col = self.GetColorFromString(colorHex)
			host.txt.SetPackedFontColor(grp.GenerateColor(col[0], col[1], col[2], col[3]))
		tw = host.txt.GetTextSize()
		vy = bh / 2 - tw[1] / 2
		# Text child: its OWN align flag sets direction + placement on the
		# plate (center title, right/RTL section, inset to clear the ornament).
		if plateAlign == "center":
			host.txt.SetWindowHorizontalAlignRight()
			cx = (bw - tw[0]) / 2
			if cx < 4:
				cx = 4
			host.txt.SetPosition(cx, vy)
		elif plateAlign == "right":
			host.txt.SetWindowHorizontalAlignRight()
			host.txt.SetPosition(rtlInset, vy)
		else:
			host.txt.SetWindowHorizontalAlignLeft()
			host.txt.SetPosition(15, vy)
		host.txt.Show()
		host.Show()
		self.elements.append(host)
		# Plate placed with AlignLeft + explicit x so the image always shows
		# (AlignRight on an image+text host did not render reliably).
		host.SetWindowHorizontalAlignLeft()
		if plateAlign == "center":
			host.SetPosition(contentW / 2 - bw / 2, y)
		elif plateAlign == "right":
			host.SetPosition(contentW - bw - 10, y)
		else:
			host.SetPosition(10, y)
		return y + bh

	def _DocWrapText(self, text, size, maxW):
		# Greedy word-wrap to the column width. ui.TextLine is single-line,
		# so long paragraphs are split here into multiple rows; each row is
		# then placed by the caller (right-aligned in Arabic). A reused,
		# off-screen TextLine measures candidate widths.
		if getattr(self, "_measText", None) is None:
			self._measText = ui.TextLine()
			self._measText.SetParent(self.scrollBoard)
			self._measText.SetWindowHorizontalAlignLeft()
		m = self._measText
		m.SetFontName(self._DocFont(size))
		m.SetPosition(0, 0)
		out = []
		cur = ""
		for w in text.split(" "):
			test = w if not cur else cur + " " + w
			m.SetText(test)
			m.Show()
			if cur and m.GetTextSize()[0] > maxW:
				out.append(cur)
				cur = w
			else:
				cur = test
		if cur:
			out.append(cur)
		m.Hide()
		if not out:
			out = [text]
		return out

	def _RenderDoc(self, lines):
		# Parse the [DOC] page into the node model (kept LIVE for the editor),
		# then render it. RerenderDoc re-runs only the render half from the same
		# model -- no reparse.
		self.docNodes = self._ParseDoc(lines)
		self._RenderDocNodes()

	def _RenderDocNodes(self):
		nodes = getattr(self, "docNodes", None) or []
		contentW = self.peekWindow.GetWidth()
		try: rtl = localeinfo.IsARABIC()
		except: rtl = False
		y = 10
		for idx in xrange(len(nodes)):
			yStart = y
			try:
				y = self._RenderDocNode(nodes[idx], y, contentW, rtl)
			except Exception:
				try: dbg.TraceError("[wiki] doc block %d failed: %s" % (idx + 1, str(nodes[idx])))
				except: pass
				host = self._DocMakeText("[wiki] block %d failed" % (idx + 1), None, "FF4040")
				self._DocPlace(host, y, "left", contentW)
				y = y + host.GetHeight() + 4
			if getattr(self, "editMode", False):
				try: self._EditBlockHandle(idx, yStart, y, contentW, rtl)
				except: pass
		self.scrollBoard.SetSize(contentW, y + 10)

	def _RenderDocNode(self, node, y, contentW, rtl):
		t = node["type"]
		defAlign = "right" if rtl else "left"
		GAP = 8
		if t == "spacer":
			return y + node.get("h", 12)
		if t == "divider":
			img = ui.ExpandedImageBox()
			img.SetParent(self.scrollBoard)
			img.AddFlag("attach")
			img.AddFlag("not_pick")
			if (node.get("style") or "").lower() == "small":
				img.LoadImage("d:/ymir work/ui/wiki/wiki_new/dungeons/header.png")
			else:
				img.LoadImage("d:/ymir work/ui/wiki/wiki_new/dungeons/footer.png")
			img.Show()
			self.elements.append(img)
			self._DocPlace(img, y + GAP, "center", contentW)
			return y + GAP + img.GetHeight() + GAP
		if t == "heading":
			y = self._DocBarText("d:/ymir work/ui/wiki/wiki_new/dungeons/subtitle.png", self._ExpandInline(node["text"], True), 18, "FFD200", y + GAP, contentW, rtl, 70, "center")
			return y + GAP
		if t == "section":
			y = self._DocBarText("d:/ymir work/ui/wiki/wiki_new/dungeons/element.png", self._ExpandInline(node["text"], True), 16, "FFE2A0", y + GAP, contentW, rtl, 76, defAlign)
			return y + 4
		if t == "img":
			img = ui.ExpandedImageBox()
			img.SetParent(self.scrollBoard)
			img.AddFlag("attach")
			img.AddFlag("not_pick")
			img.LoadImage(node["path"])
			img.Show()
			self.elements.append(img)
			self._DocPlace(img, y, node.get("align") or "center", contentW)
			return y + img.GetHeight() + GAP
		if t == "item":
			return self._RenderDocItem(node, y, contentW, defAlign)
		if t == "float":
			return self._RenderDocFloat(node, y, contentW, rtl)
		if t == "mob":
			return self._RenderDocMob(node, y, contentW, defAlign)
		if t == "require":
			return self._RenderDocRequire(node, y, contentW, defAlign)
		if t == "table":
			return self._RenderDocTable(node, y, contentW, rtl)
		if t == "bullet":
			return self._RenderDocBullet(node, y, contentW, rtl, defAlign)
		al = node.get("align") or defAlign
		ptext = self._ExpandInline(node["text"], False)
		if ptext.find("{link:") != -1:
			return self._RenderDocParaInline(ptext, y, contentW, rtl, node.get("size"), node.get("color"), al)
		lines = self._DocWrapText(ptext, node.get("size"), contentW - 10)
		for ln in lines:
			h = self._DocMakeText(ln, node.get("size"), node.get("color"))
			self._DocPlace(h, y, al, contentW)
			y = y + h.GetHeight() + 2
		return y + 4

	def _InlineTokenText(self, tok, stripLinks):
		# Replacement text for a {..} token, or None to leave it literal.
		try:
			if tok[:2] == "i:":
				v = int(tok[2:]); item.SelectItem(v); return item.GetItemName() or ("#%d" % v)
			if tok[:2] == "m:":
				v = int(tok[2:]); return nonplayer.GetMonsterName(v) or ("#%d" % v)
			if tok[:2] == "s:":
				import skill
				return skill.GetSkillName(int(tok[2:])) or tok
			if tok[:2] == "y:":
				return localeinfo.NumberToMoneyString(int(tok[2:]))
		except:
			return None
		if stripLinks and (tok[:5] == "link:" or tok == "/link"):
			return ""
		return None

	def _ExpandInline(self, text, stripLinks = False):
		# Expand {i:}/{m:}/{s:}/{y:} text tokens in place; {link:} markup is left
		# for the paragraph run-renderer unless stripLinks (then -> bare label).
		if not text or text.find("{") == -1:
			return text
		out = []
		i = 0
		n = len(text)
		while i < n:
			if text[i] == "{":
				end = text.find("}", i)
				if end != -1:
					rep = self._InlineTokenText(text[i + 1:end], stripLinks)
					if rep is not None:
						out.append(rep)
						i = end + 1
						continue
			out.append(text[i])
			i = i + 1
		return "".join(out)

	def _InlineSeg(self, text):
		# Split into ("text", s) / ("link", file, label) segments.
		segs = []
		buf = []
		i = 0
		n = len(text)
		while i < n:
			if text[i] == "{" and text[i:i + 6] == "{link:":
				end = text.find("}", i)
				if end != -1:
					close = text.find("{/link}", end)
					if close != -1:
						if buf:
							segs.append(("text", "".join(buf)))
							buf = []
						segs.append(("link", text[i + 6:end], text[end + 1:close]))
						i = close + 7
						continue
			buf.append(text[i])
			i = i + 1
		if buf:
			segs.append(("text", "".join(buf)))
		return segs

	def _MeasInline(self, text, size):
		if getattr(self, "_measText", None) is None:
			self._measText = ui.TextLine()
			self._measText.SetParent(self.scrollBoard)
			self._measText.SetWindowHorizontalAlignLeft()
		m = self._measText
		m.SetFontName(self._DocFont(size))
		m.SetPosition(-10000, -10000)
		m.SetText(text)
		m.Show()
		return m.GetTextSize()

	def _OnInlineLink(self, fileName):
		try:
			base = wiki.GetBaseClass()
			if base:
				base.GoToCustomPage(fileName)
		except:
			pass

	def _RenderDocParaInline(self, text, y, contentW, rtl, size, colorHex, al):
		# Paragraph with {link:} -> text words + clickable link atoms laid out on
		# wrapped lines (host + child TextLines; RTL via AlignRight children whose
		# x is measured from the right edge -- the bullet/card pattern).
		atoms = []
		for seg in self._InlineSeg(text):
			if seg[0] == "text":
				for w in seg[1].split(" "):
					if w != "":
						atoms.append((0, None, w))
			else:
				atoms.append((1, seg[1], seg[2]))
		if not atoms:
			return y + 4
		spaceW = self._MeasInline(" ", size)[0]
		lineH = self._MeasInline("M", size)[1]
		maxW = contentW - 36
		lines = []
		cur = []
		curW = 0
		for a in atoms:
			aw = self._MeasInline(a[2], size)[0]
			step = aw if not cur else spaceW + aw
			if cur and curW + step > maxW:
				lines.append((cur, curW))
				cur = []
				curW = 0
				step = aw
			cur.append((a, aw))
			curW = curW + step
		if cur:
			lines.append((cur, curW))
		col = self.GetColorFromString(colorHex) if colorHex else None
		lcol = self.GetColorFromString("6AB8FF")
		for (lineAtoms, lw) in lines:
			host = ui.Window()
			host.SetParent(self.scrollBoard)
			host.AddFlag("attach")
			host.SetSize(lw, lineH)
			host.kids = []
			accum = 0
			for (a, aw) in lineAtoms:
				if a[0] == 1:
					# clickable link: a pickable Window (TextLine is not hit-tested) with
					# the label as a not_pick child.
					btn = ui.Window()
					btn.SetParent(host)
					btn.SetSize(aw, lineH)
					btn.SetMouseLeftButtonDownEvent(ui.__mem_func__(self._OnInlineLink), a[1])
					lab = ui.TextLine()
					lab.SetParent(btn)
					lab.AddFlag("not_pick")
					lab.SetFontName(self._DocFont(size))
					lab.SetText(a[2])
					lab.SetPackedFontColor(grp.GenerateColor(lcol[0], lcol[1], lcol[2], lcol[3]))
					if rtl:
						lab.SetWindowHorizontalAlignRight()
					else:
						lab.SetWindowHorizontalAlignLeft()
					lab.SetPosition(0, 0)
					lab.Show()
					btn.kid = lab
					if rtl:
						btn.SetWindowHorizontalAlignRight()
					else:
						btn.SetWindowHorizontalAlignLeft()
					btn.SetPosition(accum, 0)
					btn.Show()
					host.kids.append(btn)
				else:
					t = ui.TextLine()
					t.SetParent(host)
					t.AddFlag("not_pick")
					t.SetFontName(self._DocFont(size))
					t.SetText(a[2])
					if col:
						t.SetPackedFontColor(grp.GenerateColor(col[0], col[1], col[2], col[3]))
					if rtl:
						t.SetWindowHorizontalAlignRight()
					else:
						t.SetWindowHorizontalAlignLeft()
					t.SetPosition(accum, 0)
					t.Show()
					host.kids.append(t)
				accum = accum + aw + spaceW
			host.Show()
			self.elements.append(host)
			host.SetWindowHorizontalAlignLeft()
			if al == "center":
				host.SetPosition(contentW / 2 - lw / 2, y)
			elif al == "right" or rtl:
				host.SetPosition(contentW - lw - 18, y)
			else:
				host.SetPosition(18, y)
			y = y + lineH + 2
		return y + 4

	def _RenderDocItem(self, node, y, contentW, defAlign):
		# A framed item card: an item3 (square) or itemcircle (round) tile
		# holds the real item icon -- NO name label, just the icon + hover
		# tooltip + click-to-open. The whole frame is the click/hover target.
		try:
			vnum = int(node["vnum"])
		except:
			return y
		metinSlot = [0 for j in xrange(player.METIN_SOCKET_MAX_NUM)]
		attrSlot = [[0, 0] for j in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
		if node.get("socket"):
			idx = 0
			for m in node["socket"].split("|"):
				if idx < player.METIN_SOCKET_MAX_NUM:
					metinSlot[idx] = self._DocInt(m, 0)
				idx = idx + 1
		if node.get("apply"):
			idx = 0
			for ap in node["apply"].split("|"):
				parts = ap.split(":")
				if len(parts) == 2 and idx < player.ATTRIBUTE_SLOT_MAX_NUM:
					attrSlot[idx] = [self._DocInt(parts[0], 0), self._DocInt(parts[1], 0)]
				idx = idx + 1
		item.SelectItem(vnum)
		name = node.get("label") or item.GetItemName() or ("#%d" % vnum)
		rtl = (defAlign == "right")
		if (node.get("style") or "") == "circle":
			framePath = "d:/ymir work/ui/wiki/wiki_new/dungeons/itemcircle1.png"
			FW = 70
			FH = 77
		else:
			framePath = "d:/ymir work/ui/wiki/wiki_new/dungeons/item3.png"
			FW = 72
			FH = 72
		GAP = 10
		NAMEPAD = 8
		host = ui.Window()
		host.SetParent(self.scrollBoard)
		host.AddFlag("attach")
		host.frame = ui.ExpandedImageBox()
		host.frame.SetParent(host)
		# The frame (the circle/square background) carries the click + hover so
		# the WHOLE card is interactive -- the small icon alone was an awkward
		# target (the bg was not_pick, so clicking it did nothing).
		host.frame.LoadImage(framePath)
		host.frame.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OverInItem, vnum, metinSlot, attrSlot)
		host.frame.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OverOutItem)
		host.frame.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.OnClickItem), 0, vnum)
		host.frame.Show()
		host.icon = ui.ExpandedImageBox()
		host.icon.SetParent(host)
		iconName = item.GetIconImageFileName()
		if iconName.find("gr2") == -1:
			host.icon.LoadImage(iconName)
		else:
			host.icon.LoadImage("icon/item/27995.tga")
		iw = host.icon.GetWidth()
		ih = host.icon.GetHeight()
		host.icon.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OverInItem, vnum, metinSlot, attrSlot)
		host.icon.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OverOutItem)
		host.icon.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.OnClickItem), 0, vnum)
		host.icon.Show()
		hostW = FW
		hostH = FH
		host.SetSize(hostW, hostH)
		iconX = (FW - iw) / 2
		iconY = (FH - ih) / 2
		# Images render reliably only with AlignLeft + explicit x (AlignRight on
		# an ExpandedImageBox does NOT mirror like a TextLine). Frame at origin,
		# icon centered -- same both LTR + RTL since there is no name beside it.
		host.frame.SetWindowHorizontalAlignLeft()
		host.icon.SetWindowHorizontalAlignLeft()
		host.frame.SetPosition(0, 0)
		host.icon.SetPosition(iconX, iconY)
		host.Show()
		self.elements.append(host)
		host.SetWindowHorizontalAlignLeft()
		al = node.get("align") or defAlign
		if al == "center":
			host.SetPosition(contentW / 2 - hostW / 2, y)
		elif al == "right":
			host.SetPosition(contentW - hostW - 18, y)
		else:
			host.SetPosition(18, y)
		return y + hostH + 8

	def _RenderDocFloat(self, node, y, contentW, rtl):
		# Absolute-positioned overlay -- the rare specific-placement escape hatch.
		# A no-bg PICKABLE ui.Window so UI_DEBUGGER can grab + drag it (a bare
		# TextLine isn't hit-testable); placed by window-AlignLeft + SetPosition
		# so the token x/y maps 1:1 to what UI_DEBUGGER reports. Text direction
		# comes from the TEXT-instance align (independent of window placement);
		# can instead wrap an item icon or an image. Flow is NOT disturbed.
		fx = self._DocInt(node.get("x"), 18)
		fy = self._DocInt(node.get("y"), y)
		host = ui.Window()
		host.SetParent(self.scrollBoard)
		host.AddFlag("attach")
		host.SetWindowHorizontalAlignLeft()
		host.SetPosition(fx, fy)
		host.SetSize(8, 8)
		host.Show()
		self.elements.append(host)
		# Dev-only faint grab box: a definite, visible pickable rect at the host
		# bounds so UI_DEBUGGER has something to grab (and so the author sees the
		# float's real bounds vs where the text renders). None in production.
		dev = self._WikiDevMode()
		if dev:
			bg = ui.Bar()
			bg.SetParent(host)
			bg.AddFlag("not_pick")
			bg.SetPosition(0, 0)
			bg.SetSize(8, 8)
			bg.SetColor(0x40339cff)
			bg.Show()
			host.elBg = bg
		fw = 8
		fh = 8
		if node.get("item"):
			try:
				vnum = int(node["item"])
				item.SelectItem(vnum)
				ico = ui.ExpandedImageBox()
				ico.SetParent(host)
				ico.AddFlag("not_pick")
				nm = item.GetIconImageFileName()
				if nm.find("gr2") == -1:
					ico.LoadImage(nm)
				else:
					ico.LoadImage("icon/item/27995.tga")
				ico.SetPosition(0, 0)
				ico.Show()
				host.elIco = ico
				fw = ico.GetWidth()
				fh = ico.GetHeight()
			except:
				pass
		elif node.get("img"):
			try:
				im = ui.ExpandedImageBox()
				im.SetParent(host)
				im.AddFlag("not_pick")
				im.LoadImage(node["img"])
				im.SetPosition(0, 0)
				im.Show()
				host.elImg = im
				fw = im.GetWidth()
				fh = im.GetHeight()
			except:
				pass
		else:
			txt = ui.TextLine()
			txt.SetParent(host)
			txt.AddFlag("not_pick")
			txt.SetFontName(self._DocFont(node.get("size")))
			txt.SetText(self._ExpandInline(node.get("text") or "", True))
			if node.get("color"):
				c = self.GetColorFromString(node["color"])
				txt.SetPackedFontColor(grp.GenerateColor(c[0], c[1], c[2], c[3]))
			if rtl:
				txt.SetHorizontalAlignArabic()
			else:
				txt.SetHorizontalAlignLeft()
			txt.SetPosition(0, 0)
			txt.Show()
			host.elTxt = txt
			(tw, th) = txt.GetTextSize()
			if tw > 0:
				fw = tw
			if th > 0:
				fh = th
		# Pad to a clear minimum so the float is an easy UI_DEBUGGER grab target
		# (a tiny text-sized rect is almost impossible to hover/drag).
		fw = self._DocInt(node.get("w"), fw)
		fh = self._DocInt(node.get("h"), fh)
		if fw < 40:
			fw = 40
		if fh < 18:
			fh = 18
		host.SetSize(fw, fh)
		if dev:
			host.elBg.SetSize(fw, fh)
		return y

	def _RenderDocMob(self, node, y, contentW, defAlign):
		# A monster_preview portrait card with a LIVE 3D model of the mob
		# (WikiRenderTarget), sized to fill the frame. No name/level text -- just
		# the rendered model. Clicking opens the full page. The render target is
		# tracked in self._docModels so it hides when the page hides and is
		# freed/unregistered on reload.
		try:
			vnum = int(node["vnum"])
		except:
			return y
		FW = 135
		FH = 183
		host = ui.Window()
		host.SetParent(self.scrollBoard)
		host.AddFlag("attach")
		host.SetSize(FW, FH)
		host.frame = ui.ExpandedImageBox()
		host.frame.SetParent(host)
		host.frame.LoadImage("d:/ymir work/ui/wiki/wiki_new/dungeons/monster_preview.png")
		host.frame.SetPosition(0, 0)
		host.frame.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.OnClickMonster), vnum)
		host.frame.Show()
		try:
			MW = 115
			MH = 160
			rt = WikiRenderTarget(MW, MH)
			rt.SetParent(host)
			rt.SetPosition((FW - MW) / 2, (FH - MH) / 2)
			rt.SetModel(vnum)
			rt.SetModelV3Eye(0.0, -2050.0, 300.0)
			rt.SetModelV3Target(0.0, 600.0, 100.0)
			rt.SetMouseLeftButtonDownEvent(ui.__mem_func__(self.OnClickMonster), vnum)
			rt.Show()
			self._docModels.append(rt)
		except:
			try:
				dbg.TraceError("[wiki] mob model failed vnum %d" % vnum)
			except:
				pass
		host.Show()
		self.elements.append(host)
		host.SetWindowHorizontalAlignLeft()
		al = node.get("align") or defAlign
		if al == "center":
			host.SetPosition(contentW / 2 - FW / 2, y)
		elif al == "right":
			host.SetPosition(contentW - FW - 18, y)
		else:
			host.SetPosition(18, y)
		return y + FH + 8

	def _RequireEval(self, node):
		# Returns (display, colorHex) for a [require]: reads the reader's current
		# stat / item count / skill rank vs the threshold. Shared by the [require]
		# block and by require-cells in a [table].
		reqVal = self._DocInt(node.get("value"), 1)
		label = node.get("text") or ""
		cur = 0
		met = False
		if node.get("have"):
			vnum = self._DocInt(node.get("have"), 0)
			try:
				cur = player.GetItemCountByVnum(vnum)
			except:
				cur = 0
			if not label and vnum:
				try:
					item.SelectItem(vnum)
					label = item.GetItemName() or ""
				except:
					pass
			met = (cur >= reqVal)
		elif node.get("skill"):
			sid = self._DocInt(node.get("skill"), 0)
			reqVal = self._DocInt(node.get("level"), 1)
			try:
				cur = player.GetSkillLevel(sid)
			except:
				cur = 0
			met = (cur >= reqVal)
		else:
			name = node.get("point") or node.get("apply") or ""
			pc = getattr(player, "POINT_" + name, None) if name else None
			if pc is not None:
				try:
					cur = player.GetPoint(pc)
				except:
					cur = 0
			met = (cur >= reqVal)
		mark = "+ " if met else "! "
		color = "60D060" if met else "E05858"
		return ("%s%s  (%d / %d)" % (mark, label, cur, reqVal), color)

	def _RenderDocRequire(self, node, y, contentW, defAlign):
		# Stacking several [require] lines yields a gear/dungeon-prep checklist.
		(line, color) = self._RequireEval(node)
		h = self._DocMakeText(line, None, color)
		self._DocPlace(h, y, node.get("align") or defAlign, contentW)
		return y + h.GetHeight() + 4

	def _CellLine(self, text, x, y, w, rtl, size, colorHex):
		# One text line inside a table cell: host(AlignLeft) at (x,y) width w, with
		# a child TextLine AlignRight (RTL, correct direction) / AlignLeft (LTR).
		host = ui.Window()
		host.SetParent(self.scrollBoard)
		host.AddFlag("attach")
		host.AddFlag("not_pick")
		host.txt = ui.TextLine()
		host.txt.SetParent(host)
		host.txt.AddFlag("not_pick")
		host.txt.SetFontName(self._DocFont(size))
		host.txt.SetText(text)
		if colorHex:
			c = self.GetColorFromString(colorHex)
			host.txt.SetPackedFontColor(grp.GenerateColor(c[0], c[1], c[2], c[3]))
		th = host.txt.GetTextSize()[1]
		if th <= 0:
			th = 14
		host.SetSize(w, th)
		if rtl:
			host.txt.SetWindowHorizontalAlignRight()
		else:
			host.txt.SetWindowHorizontalAlignLeft()
		host.txt.SetPosition(0, 0)
		host.txt.Show()
		host.Show()
		self.elements.append(host)
		host.SetWindowHorizontalAlignLeft()
		host.SetPosition(x, y)
		return th

	def _RenderCellText(self, text, x, y, w, rtl, size, colorHex):
		cy = y
		for ln in self._DocWrapText(text, size, w):
			cy = cy + self._CellLine(ln, x, cy, w, rtl, size, colorHex) + 1
		return cy - y

	def _RenderCellItem(self, node, x, y, w, rtl):
		# Compact item: icon (reading edge) + name, hover tooltip + click-to-open.
		try:
			vnum = int(node["vnum"])
		except:
			return 16
		metinSlot = [0 for j in xrange(player.METIN_SOCKET_MAX_NUM)]
		attrSlot = [[0, 0] for j in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
		item.SelectItem(vnum)
		nm = node.get("label") or item.GetItemName() or ("#%d" % vnum)
		ICON = 32
		icon = ui.ExpandedImageBox()
		icon.SetParent(self.scrollBoard)
		icon.AddFlag("attach")
		iconName = item.GetIconImageFileName()
		if iconName.find("gr2") == -1:
			icon.LoadImage(iconName)
		else:
			icon.LoadImage("icon/item/27995.tga")
		icon.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OverInItem, vnum, metinSlot, attrSlot)
		icon.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OverOutItem)
		icon.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.OnClickItem), 0, vnum)
		icon.Show()
		self.elements.append(icon)
		icon.SetWindowHorizontalAlignLeft()
		ny = y + (ICON - 14) / 2
		if rtl:
			icon.SetPosition(x + w - ICON, y)
			self._CellLine(nm, x, ny, w - ICON - 4, rtl, None, "FFE2A0")
		else:
			icon.SetPosition(x, y)
			self._CellLine(nm, x + ICON + 4, ny, w - ICON - 4, rtl, None, "FFE2A0")
		return ICON

	def _RenderCell(self, node, x, y, w, rtl):
		pad = 5
		cx = x + pad
		cw = w - 2 * pad
		if cw < 20:
			cw = 20
		t = node.get("type")
		if t == "item":
			return self._RenderCellItem(node, cx, y + pad, cw, rtl) + 2 * pad
		if t == "require":
			(line, color) = self._RequireEval(node)
			return self._RenderCellText(line, cx, y + pad, cw, rtl, None, color) + 2 * pad
		txt = self._ExpandInline(node.get("text", ""), True)
		return self._RenderCellText(txt, cx, y + pad, cw, rtl, node.get("size"), node.get("color")) + 2 * pad

	def _CellPlain(self, node):
		# Plain display text of a cell node (used for header cells).
		if node is None:
			return ""
		t = node.get("type")
		if t == "item":
			try:
				v = int(node["vnum"]); item.SelectItem(v); return node.get("label") or item.GetItemName() or ("#%d" % v)
			except:
				return ""
		if t == "mob":
			try:
				return node.get("label") or nonplayer.GetMonsterName(int(node["vnum"])) or ""
			except:
				return ""
		if t == "require":
			return self._RequireEval(node)[0]
		return self._ExpandInline(node.get("text", ""), True)

	def _CellTableData(self, node):
		# (text, icon, packedColor) for a data cell. icon = item vnum or None;
		# color 0 = use the table default.
		if node is None:
			return ("", None, 0)
		t = node.get("type")
		if t == "item":
			try:
				v = int(node["vnum"]); item.SelectItem(v)
				nm = node.get("label") or item.GetItemName() or ("#%d" % v)
				c = self.GetColorFromString("FFE2A0")
				return (nm, v, grp.GenerateColor(c[0], c[1], c[2], c[3]))
			except:
				return ("", None, 0)
		if t == "require":
			(txt, colHex) = self._RequireEval(node)
			c = self.GetColorFromString(colHex)
			return (txt, None, grp.GenerateColor(c[0], c[1], c[2], c[3]))
		if t == "mob":
			try:
				return (node.get("label") or nonplayer.GetMonsterName(int(node["vnum"])) or "", None, 0)
			except:
				return ("", None, 0)
		txt = self._ExpandInline(node.get("text", ""), True)
		ch = node.get("color")
		if ch:
			c = self.GetColorFromString(ch)
			return (txt, None, grp.GenerateColor(c[0], c[1], c[2], c[3]))
		return (txt, None, 0)

	def _TableItemCell(self, cellWnd, vnum, em, ea):
		# Item cell: the icon at its NATIVE size (NO scaling) centered in the
		# cell, clickable (open page) + hover tooltip. No name label.
		cw = cellWnd.GetWidth()
		ch = cellWnd.GetHeight()
		item.SelectItem(vnum)
		ico = ui.ExpandedImageBox()
		ico.SetParent(cellWnd)
		iconName = item.GetIconImageFileName()
		if iconName.find("gr2") == -1:
			ico.LoadImage(iconName)
		else:
			ico.LoadImage("icon/item/27995.tga")
		iw = ico.GetWidth()
		ih = ico.GetHeight()
		ico.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OverInItem, vnum, em, ea)
		ico.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OverOutItem)
		ico.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.OnClickItem), 0, vnum)
		ico.SetPosition((cw - iw) / 2, (ch - ih) / 2)
		ico.Show()
		cellWnd.ov_ico = ico

	def _RenderDocTable(self, node, y, contentW, rtl):
		# Bordered ui.Table grid. Item cells render a stacked icon+name overlay
		# (taller rows); inner horizontal lines are redrawn on top because the
		# opaque row backgrounds cover ui.Table's own dividers.
		M = 12
		cols = node.get("cols") or 1
		if cols < 1:
			cols = 1
		rows = node.get("rows") or []
		if not rows:
			return y
		tableW = contentW - 2 * M
		colW = tableW / cols
		widths = []
		c = 0
		while c < cols:
			widths.append(colW if c < cols - 1 else (tableW - colW * (cols - 1)))
			c = c + 1
		headRow = rows[0]
		headers = []
		c = 0
		while c < cols:
			headers.append(self._CellPlain(headRow[c]) if c < len(headRow) else "")
			c = c + 1
		dataRows = []
		hasItem = False
		r = 1
		while r < len(rows):
			row = rows[r]
			texts = []
			icons = []
			colors = []
			c = 0
			while c < cols:
				cell = row[c] if c < len(row) else None
				(txt, icon, colr) = self._CellTableData(cell)
				if icon:
					hasItem = True
				texts.append(txt)
				icons.append(icon)
				colors.append(colr)
				c = c + 1
			dataRows.append((texts, icons, colors))
			r = r + 1
		if rtl:
			headers.reverse()
			widths.reverse()
			k = 0
			while k < len(dataRows):
				(tt, ic, co) = dataRows[k]
				dataRows[k] = (tt[::-1], ic[::-1], co[::-1])
				k = k + 1
		HEAD_H = 22
		ROW_H = 34
		if hasItem:
			# Native-size icons (no scaling) => size item-table rows to the
			# tallest icon so nothing clips.
			probe = ui.ExpandedImageBox()
			maxIH = 0
			for (ptt, pic, pco) in dataRows:
				for pvn in pic:
					if pvn:
						item.SelectItem(int(pvn))
						pnm = item.GetIconImageFileName()
						if pnm.find("gr2") == -1:
							probe.LoadImage(pnm)
						else:
							probe.LoadImage("icon/item/27995.tga")
						ph = probe.GetHeight()
						if ph > maxIH:
							maxIH = ph
			probe = None
			ROW_H = max(40, maxIH + 10)
		# line color alpha-0: ui.Table draws lines via CLine, which ignores the
		# scroll clip mask (bleeds outside the viewport) -- hide them and redraw
		# the grid below as clipping ui.Bar.
		scheme = [0xff756657, 0xff281f1a, 0xff1a1615, 0xffcabdab, 0xffc7c7c7]
		tbl = ui.Table(tableW, HEAD_H, scheme)
		tbl.SetParent(self.scrollBoard)
		tbl.AddFlag("attach")
		tbl.set_columns(headers, widths)
		dataAlign = "horizontal:right" if rtl else "horizontal:left"
		cellAligns = [dataAlign] * cols
		em = [0 for jj in xrange(player.METIN_SOCKET_MAX_NUM)]
		ea = [[0, 0] for jj in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
		ri = 0
		for (texts, icons, colors) in dataRows:
			dispTexts = []
			c = 0
			while c < len(texts):
				dispTexts.append("" if icons[c] else texts[c])
				c = c + 1
			tbl.add_row(dispTexts, ROW_H, colors, cellAligns, None)
			ci = 0
			for vn in icons:
				if vn:
					cellWnd = tbl._tchildren.get("row_%d_c%d" % (ri, ci))
					if cellWnd:
						try:
							self._TableItemCell(cellWnd, int(vn), em, ea)
						except:
							pass
				ci = ci + 1
			ri = ri + 1
		tbl.Show()
		self.elements.append(tbl)
		tbl.SetWindowHorizontalAlignLeft()
		tableY = y + 6
		tbl.SetPosition(M, tableY)
		nRows = len(dataRows)
		totalH = HEAD_H + nRows * ROW_H
		# Draw the WHOLE grid (outer border + inner dividers) as ui.Bar, NOT
		# ui.Line: CLine ignores the scroll clip mask so lines bleed outside the
		# viewport when scrolled; CBar clips (inherits the mask from scrollBoard
		# via AddChild). ui.Table's own line color is alpha-0 (invisible) so only
		# these clipping bars show.
		LINE_C = 0xff756657
		hy = [tableY]
		k = 0
		while k <= nRows:
			hy.append(tableY + HEAD_H + k * ROW_H)
			k = k + 1
		for yy in hy:
			hb = ui.Bar()
			hb.SetParent(self.scrollBoard)
			hb.AddFlag("attach")
			hb.AddFlag("not_pick")
			hb.SetPosition(M, yy)
			hb.SetSize(tableW + 1, 1)
			hb.SetColor(LINE_C)
			hb.Show()
			self.elements.append(hb)
		vx = [M]
		cum = 0
		ci = 0
		while ci < cols:
			cum = cum + widths[ci]
			vx.append(M + cum)
			ci = ci + 1
		for xx in vx:
			vb = ui.Bar()
			vb.SetParent(self.scrollBoard)
			vb.AddFlag("attach")
			vb.AddFlag("not_pick")
			vb.SetPosition(xx, tableY)
			vb.SetSize(1, totalH + 1)
			vb.SetColor(LINE_C)
			vb.Show()
			self.elements.append(vb)
		return tableY + tbl.GetHeight() + 10

	def _RenderDocBullet(self, node, y, contentW, rtl, defAlign):
		# A bullet: a red "-" on the reading edge + the text beside it, now
		# WRAPPED. Long bullets flow onto continuation lines that hang-indent
		# under the text (aligned with the first text line, NOT under the dash).
		# Same proven child pattern as the single-line version: AlignLeft host
		# at the reading-edge x; AlignRight TextLine children in Arabic (their x
		# measured from the host right edge), AlignLeft otherwise.
		host = ui.Window()
		host.SetParent(self.scrollBoard)
		host.AddFlag("attach")
		host.AddFlag("not_pick")
		host.mark = ui.TextLine()
		host.mark.SetParent(host)
		host.mark.SetFontName(self._DocFont(node.get("size")))
		host.mark.SetText("-")
		mcol = self.GetColorFromString("FF3333")
		host.mark.SetPackedFontColor(grp.GenerateColor(mcol[0], mcol[1], mcol[2], mcol[3]))
		host.mark.Show()
		dw = host.mark.GetTextSize()
		indent = dw[0] + 6
		maxW = contentW - 36 - indent
		if maxW < 60:
			maxW = 60
		wrapped = self._DocWrapText(self._ExpandInline(node["text"], True), node.get("size"), maxW)
		col = None
		if node.get("color"):
			col = self.GetColorFromString(node["color"])
		host.lines = []
		lineH = dw[1]
		maxLineW = 0
		for ln in wrapped:
			t = ui.TextLine()
			t.SetParent(host)
			t.SetFontName(self._DocFont(node.get("size")))
			t.SetText(ln)
			if col:
				t.SetPackedFontColor(grp.GenerateColor(col[0], col[1], col[2], col[3]))
			t.Show()
			sz = t.GetTextSize()
			if sz[0] > maxLineW:
				maxLineW = sz[0]
			if sz[1] > lineH:
				lineH = sz[1]
			host.lines.append(t)
		hostW = indent + maxLineW
		hostH = lineH * max(1, len(host.lines))
		host.SetSize(hostW, hostH)
		markY = (lineH - dw[1]) / 2
		if rtl:
			host.mark.SetWindowHorizontalAlignRight()
			host.mark.SetPosition(0, markY)
		else:
			host.mark.SetWindowHorizontalAlignLeft()
			host.mark.SetPosition(0, markY)
		i = 0
		for t in host.lines:
			ty = i * lineH
			if rtl:
				t.SetWindowHorizontalAlignRight()
				t.SetPosition(indent, ty)
			else:
				t.SetWindowHorizontalAlignLeft()
				t.SetPosition(indent, ty)
			i = i + 1
		host.SetWindowHorizontalAlignLeft()
		if rtl:
			host.SetPosition(contentW - hostW - 18, y)
		else:
			host.SetPosition(18, y)
		host.Show()
		self.elements.append(host)
		return y + hostH + 4
	def OverOutItem(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.HideToolTip()

	def OverInItem(self, itemVnum, metinSlot=[], attrSlot=[]):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			if not len(metinSlot):
				metinSlot = [0 for j in xrange(player.METIN_SOCKET_MAX_NUM)]

			if not len(attrSlot):
				attrSlot = [(0,0) for j in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

			interfaceHandler.tooltipItem.ClearToolTip()
			interfaceHandler.tooltipItem.AddItemData(itemVnum, metinSlot, attrSlot)

	def OnClickItem(self, arg, itemVnum = 0):
		self.OverOutItem()

		if itemVnum > 0:
			wikiBase = wiki.GetBaseClass()
			if wikiBase:
				wikiBase.OpenSpecialPage(self, itemVnum, False)

	def OnClickMonster(self, mobVnum):
		self.OverOutItem()

		if mobVnum > 0:
			wikiBase = wiki.GetBaseClass()
			if wikiBase:
				wikiBase.OpenSpecialPage(self, mobVnum, True)

	def OpenWindow(self):
		self.UpdateScrollbar()
		wndMgr.Show(self.hWnd)
		for m in getattr(self, "_docModels", ()):
			try:
				m.Show()
			except:
				pass

	def Hide(self):
		# Stop the mob-card 3D model views rendering when this page hides
		# (e.g. navigating to another wiki page); they resume on OpenWindow
		# / reload.
		for m in getattr(self, "_docModels", ()):
			try:
				m.Hide()
			except:
				pass
		ui.Window.Hide(self)

	def OnRunMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

class WikiMainCostumeWindow(ui.Window):
	class WikiItem(ui.Window):
		def __init__(self, vnum, parent):
			ui.Window.__init__(self)
			
			self.vnum = vnum
			self.parent = proxy(parent)
			
			self.base = ui.ExpandedImageBox()
			self.base.SetParent(self)
			self.base.AddFlag("attach")
			self.base.AddFlag("not_pick")
			self.base.LoadImage("d:/ymir work/ui/wiki/detail_item_small.png")
			self.base.Show()
			
			self.costumeImage = ui.ExpandedImageBox()
			self.costumeImage.SetParent(self.base)
			self.costumeImage.LoadImage(item.GetIconImageFileName())
			self.costumeImage.SetPosition(1 + 125 / 2 - self.costumeImage.GetWidth() / 2,\
										1 + 120 / 2 - self.costumeImage.GetHeight() / 2)
			self.costumeImage.SetStringEvent("MOUSE_OVER_IN",ui.__mem_func__( self.parent.OnOverIn), self.vnum, 0)
			self.costumeImage.SetStringEvent("MOUSE_OVER_OUT",ui.__mem_func__( self.parent.OnOverOut))
			#self.costumeImage.SetMouseRightButtonDownEvent(ui.__mem_func__(self.parent.OnRightDown), self.vnum)
			self.costumeImage.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.parent.OnRightDown), self.vnum)

			self.costumeImage.Show()
			
			self.contentText = ui.TextLine()
			self.contentText.SetParent(self.base)
			self.contentText.AddFlag("attach")
			self.contentText.AddFlag("not_pick")
			self.contentText.SetText(item.GetItemName())#dream??
			self.contentText.SetPosition(1 + 125 / 2 - self.contentText.GetTextSize()[0] / 2, 122 + 18 / 2 - self.contentText.GetTextSize()[1] / 2 - 1)
			if localeinfo.IsARABIC():
				#self.cutTextLine.SetWindowHorizontalAlignCenter()
				self.contentText.SetWindowHorizontalAlignRight()
			self.contentText.Show()
			
			self.SetSize(self.base.GetWidth(), self.base.GetHeight())
	
	"""Static values!
		Please dont touch on them."""
	ELEM_X_PADDING = 10
	ELEM_PADDING = 10
	SCROLL_SPEED = 25
	ELEM_PER_LINE = 4
	ITEM_LOAD_PER_UPDATE = 1
	
	def __init__(self):
		ui.Window.__init__(self)
		
		self.toolTip = uitooltip.ItemToolTip()
		self.toolTip.AddFlag("not_pick")
		
		self.SetSize(*mainBoardSize)
		
		self.elements = []
		self.costumeVnums = []
		self.posMap = {}
		self.scrollBar = None
		
		self.isOpened = False
		self.loadFrom = 0
		self.loadTo = 0
		
		self.wikiRenderTarget = WikiRenderTarget(150, 200)
		self.wikiRenderTarget.SetParent(self.toolTip)
		self.wikiRenderTarget.AddFlag("not_pick")
		self.wikiRenderTarget.SetPosition(5, self.toolTip.toolTipHeight)
		self.wikiRenderTarget.Hide()
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(541, self.GetHeight() - 15)
		self.peekWindow.SetPosition(5, 5)

		if not app.USE_CLIP_MASK:
			self.peekWindow.SetInsideRender(True)

		self.peekWindow.Show()

		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")

		if app.USE_CLIP_MASK:
			self.scrollBoard.SetClippingMaskWindow(self.peekWindow)

		self.scrollBoard.Show()

		self.RegisterScrollBar()
	
	def OpenWindow(self):
		wndMgr.Show(self.hWnd)
	
	def Hide(self):
		wndMgr.Hide(self.hWnd)
	
	def Show(self, vnums):
		wndMgr.Show(self.hWnd)
		
		extractedLists = []
		for i in vnums:
			if type(i) == types.ListType:
				extractedLists.append(i)
		
		for i in extractedLists:
			pos = vnums.index(i)
			
			vnums.remove(i)
			for j in xrange(len(i)):
				vnums.insert(pos + j, i[j])
		
		isChanged = (not len(vnums) == len(self.costumeVnums))
		
		if not isChanged:
			for i in vnums:
				if i not in self.costumeVnums:
					isChanged = True
					break
		
		if not isChanged:
			for i in self.costumeVnums:
				if i not in vnums:
					isChanged = True
					break
		
		self.costumeVnums = vnums[:]
		self.loadTo = len(self.costumeVnums)
		
		if not self.isOpened:
			self.isOpened = True
			self.loadFrom = 0
		
		if self.loadFrom > self.loadTo or isChanged:
			del self.elements[:]
			self.posMap = {}
			
			self.loadFrom = 0
			
			self.scrollBoard.SetSize(0, 0)
			self.UpdateScrollbar()
	
	def GetRandomChar(self):
		ASSASSINS 		= [ player.MAIN_RACE_ASSASSIN_W, player.MAIN_RACE_ASSASSIN_M ]
		WARRIORS 		= [ player.MAIN_RACE_WARRIOR_W, player.MAIN_RACE_WARRIOR_M ]
		SURAS 			= [ player.MAIN_RACE_SURA_W, player.MAIN_RACE_SURA_M ]
		SHAMANS 		= [ player.MAIN_RACE_SHAMAN_W, player.MAIN_RACE_SHAMAN_M ]
		ITEM_CHARACTERS = [ ASSASSINS, WARRIORS, SURAS, SHAMANS ]
		
		if app.INGAME_WIKI_WOLFMAN:
			WOLFMANS		= [player.MAIN_RACE_WOLFMAN_M]
			ITEM_CHARACTERS.extend([WOLFMANS])
		
		SEX_FEMALE		= 0
		SEX_MALE		= 1
		ITEM_SEX		= [ SEX_FEMALE, SEX_MALE ]
		
		#-#
		
		# if item.IsAntiFlag( item.ITEM_ANTIFLAG_MALE ):
			# ITEM_SEX.remove( SEX_MALE )
		#not needed for now
		# if item.IsAntiFlag( item.ITEM_ANTIFLAG_FEMALE ):
			# ITEM_SEX.remove( SEX_FEMALE )
		
		#-#
		
		if item.IsAntiFlag( item.ITEM_ANTIFLAG_WARRIOR ):
			ITEM_CHARACTERS.remove( WARRIORS )
		
		if item.IsAntiFlag( item.ITEM_ANTIFLAG_SURA ):
			ITEM_CHARACTERS.remove( SURAS )
		
		if item.IsAntiFlag( item.ITEM_ANTIFLAG_ASSASSIN ):
			ITEM_CHARACTERS.remove( ASSASSINS )
		
		if item.IsAntiFlag( item.ITEM_ANTIFLAG_SHAMAN ):
			ITEM_CHARACTERS.remove( SHAMANS )
		
		if app.INGAME_WIKI_WOLFMAN:
			if item.IsAntiFlag( item.ITEM_ANTIFLAG_WOLFMAN ):
				ITEM_CHARACTERS.remove( WOLFMANS )
			
			CHAR_TYPE = ITEM_CHARACTERS[app.GetRandom(0, len(ITEM_CHARACTERS) - 1)]
			if len(CHAR_TYPE) == 1 and CHAR_TYPE[0] == player.MAIN_RACE_WOLFMAN_M:
				return player.MAIN_RACE_WOLFMAN_M
			else:
				CHAR_SEX = ITEM_SEX[app.GetRandom(0, len(ITEM_SEX) - 1)]
				if (CHAR_SEX > (len(CHAR_TYPE) - 1)):
					return CHAR_TYPE[0]
				else:
					return CHAR_TYPE[CHAR_SEX]
		else:
			return ITEM_CHARACTERS[app.GetRandom(0, len(ITEM_CHARACTERS) - 1)][ITEM_SEX[app.GetRandom(0, len(ITEM_SEX) - 1)]]

	def GetCharTypeHairCamera(self, char_type):
		if not ingamewikiconfig.HAIRSTYLE_CAMERA_CFG.has_key(char_type):
			return tuple([], [])
		
		return ingamewikiconfig.HAIRSTYLE_CAMERA_CFG[char_type]
	
	def OnOverIn(self, vnum, render):
		if not self.toolTip:
			return
		
		self.toolTip.ClearToolTip()
		self.toolTip.SetThinBoardSize(self.wikiRenderTarget.GetWidth() + 10, self.wikiRenderTarget.GetHeight() + self.toolTip.toolTipHeight)
		self.toolTip.childrenList.append(self.wikiRenderTarget)
		self.toolTip.ResizeToolTip()
		
		item.SelectItem(vnum)
		
		itemType = item.GetItemType()
		subType = item.GetItemSubType()
		char_type = self.GetRandomChar()
		
		donot=0
		self.wikiRenderTarget.SetModel(char_type)
		if itemType == item.ITEM_TYPE_WEAPON or itemType == item.ITEM_TYPE_COSTUME and subType == item.COSTUME_TYPE_WEAPON:
			self.wikiRenderTarget.SetWeaponModel(vnum)
		elif itemType == item.ITEM_TYPE_COSTUME and subType == item.COSTUME_TYPE_BODY:
			self.wikiRenderTarget.SetModelForm(vnum)
		elif itemType == item.ITEM_TYPE_COSTUME and subType == item.COSTUME_TYPE_ACCE:
			self.wikiRenderTarget.SetModelSash(vnum)
		elif itemType == item.ITEM_TYPE_COSTUME and subType == item.COSTUME_TYPE_HAIR:
			self.wikiRenderTarget.SetModelHair(item.GetValue(3))
			(V3Eye, V3Target) = self.GetCharTypeHairCamera(char_type)
			if len(V3Eye) and len(V3Target):
				self.wikiRenderTarget.SetModelV3Eye(*V3Eye)
				self.wikiRenderTarget.SetModelV3Target(*V3Target)
		elif itemType == item.ITEM_TYPE_SHINING:
			if subType == item.SHINING_ARMOR:
				armor = 11209
				if char_type == 1 or char_type == 5:
					armor == 11409
				elif char_type == 2 or char_type == 6:
					armor == 11609
				elif char_type == 3 or char_type == 7:
					armor == 11809
					
				self.wikiRenderTarget.SetModelForm(armor)
				self.wikiRenderTarget.SetModelShining(1, vnum)
			elif subType == item.SHINING_WEAPON:
				weapon = 19
				effectID = item.GetValue(0)
				if char_type == 1 or char_type == 5:
					weapon = 1009
				elif char_type == 3 or char_type == 7:
					weapon = 7009
				
				self.wikiRenderTarget.SetWeaponModel(weapon)
				self.wikiRenderTarget.SetModelShining(0, vnum)
		elif itemType == item.ITEM_TYPE_COSTUME and subType == item.COSTUME_TYPE_MOUNT:
			mobVnum = item.GetValue(1)
			if mobVnum != 0:
				self.wikiRenderTarget.SetModel(mobVnum)
				self.wikiRenderTarget.SetModelV3Eye(0.0000, -2050.0000, 300.0000)
				self.wikiRenderTarget.SetModelV3Target(0.0000, 600.0000, 100.0000)
			else:
				donot=1
		else:
			if osfinfo.IS_PET_SEAL(vnum):
				mobVnum = item.GetValue(0)
				if mobVnum != 0:
					self.wikiRenderTarget.SetModel(mobVnum)
					self.wikiRenderTarget.SetModelV3Eye(0.0000, -2050.0000, 300.0000)
					self.wikiRenderTarget.SetModelV3Target(0.0000, 600.0000, 100.0000)
				else:
					donot=1
		
		self.toolTip.AddItemData(vnum, [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)], 0, noRender = render)
		self.toolTip.AppendWikiAccessoryMaterials(vnum)
		if donot==0:
			self.wikiRenderTarget.SetPosition(self.toolTip.GetWidth() / 2 - self.wikiRenderTarget.GetWidth() / 2, self.wikiRenderTarget.GetLocalPosition()[1])
			self.wikiRenderTarget.Show()

	def OnOverOut(self):
		if not self.toolTip:
			return
		
		self.toolTip.Hide()

	def OnRightDown(self, itemVnum = 0):
		if itemVnum == 0:
			return
		
		if app.ENABLE_RENDER_TARGET and\
			app.IsPressed(app.DIK_LSHIFT):
				if uiRenderTarget.IsCanShowItems(itemVnum):
					interfaceHandler = systemSetting.GetInterfaceHandler()
					if interfaceHandler:
						interfaceHandler.OpenRenderTargetWindow(0, itemVnum)

	def OnUpdate(self):
		if self.loadFrom < self.loadTo:
			for i in xrange(self.loadFrom, min(self.loadTo, self.loadFrom + self.ITEM_LOAD_PER_UPDATE)):
				self.AddItem(self.costumeVnums[i])
				self.loadFrom += 1
	
	def AddItem(self, vnum):
		for i in self.elements:
			if vnum == i.vnum:
				return None
		
		item.SelectItem(vnum)
		
		tmp = self.WikiItem(vnum, self)
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")

		totalElem = len(self.elements)
		if totalElem > 0:
			currAdd = 0
			while currAdd in self.posMap:
				currAdd += 1
			
			totalLine = currAdd % self.ELEM_PER_LINE
			currH = math.floor(currAdd / self.ELEM_PER_LINE) * (tmp.GetHeight() + self.ELEM_PADDING)
			
			self.posMap[currAdd] = True
			tmp.SetPosition(1 + totalLine * (tmp.GetWidth() + self.ELEM_X_PADDING), 0 + currH)
		else:
			self.posMap[0] = True
			tmp.SetPosition(1, 0)
		
		tmp.Show()
		self.elements.append(tmp)
		
		self.scrollBoard.SetSize(self.peekWindow.GetWidth(), max(self.scrollBoard.GetHeight(), tmp.GetLocalPosition()[1] + tmp.GetHeight()))
		self.UpdateScrollbar()
	
	def OnRunMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

if app.ENABLE_ITEM_SHOPS:
	class WikiMainShopItemWindow(WikiMainCostumeWindow):
		# Same grid + detail_item_small.png cards as the costume/shining/mount page.
		# Left-clicking a card opens that item's shop (open-for-anyone: the server
		# validates the vnum is a real USE_OPEN_SHOP item before opening).
		def OnOverIn(self, vnum, render):
			# Plain item tooltip only. The costume base class' OnOverIn renders a 3D
			# character model into the tooltip (it leaked a random model on these
			# use-items), so show just the item data -- no SetModel / wikiRenderTarget.
			if not self.toolTip:
				return
			self.toolTip.ClearToolTip()
			item.SelectItem(vnum)
			self.toolTip.AddItemData(vnum, [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)], 0, noRender = render)
			self.toolTip.AppendWikiAccessoryMaterials(vnum)

		def OnRightDown(self, itemVnum = 0):
			if itemVnum == 0:
				return
			net.SendOpenItemShop(itemVnum)

def InitMainWindow(self):
	self.AddFlag('movable')
	self.AddFlag('float')
	
	for i in ingamewikiconfig.ITEM_BLACKLIST:
		if type(i) == types.ListType:
			for k in i:
				wiki.RegisterItemBlacklist(k)
		else:
			wiki.RegisterItemBlacklist(i)
	
	for i in ingamewikiconfig.MOB_WHITELIST:
		if type(i) == types.ListType:
			for k in i:
				wiki.RegisterMonsterBlacklist(k)
		else:
			wiki.RegisterMonsterBlacklist(i)
	
	nonplayer.BuildWikiSearchList()

def InitMainWeaponWindow(self):
	self.mainWeaponWindow = WikiMainWeaponWindow()
	self.mainWeaponWindow.SetParent(self.baseBoard)
	self.mainWeaponWindow.AddFlag("attach")
	self.mainWeaponWindow.SetPosition(*mainBoardPos)

def InitMainChestWindow(self):
	self.mainChestWindow = WikiMainChestWindow()
	self.mainChestWindow.SetParent(self.baseBoard)
	self.mainChestWindow.AddFlag("attach")
	self.mainChestWindow.SetPosition(*mainBoardPos)

def InitMainBossWindow(self):
	self.mainBossWindow = WikiMainBossWindow()
	self.mainBossWindow.SetParent(self.baseBoard)
	self.mainBossWindow.AddFlag("attach")
	self.mainBossWindow.SetPosition(*mainBoardPos)

def InitCustomPageWindow(self):
	self.customPageWindow = SimpleTextLoader()
	self.customPageWindow.SetParent(self.baseBoard)
	self.customPageWindow.AddFlag("attach")
	self.customPageWindow.SetPosition(*mainBoardPos)
	self.customPageWindow.Show()

def InitCostumePageWindow(self):
	self.costumePageWindow = WikiMainCostumeWindow()
	self.costumePageWindow.SetParent(self.baseBoard)
	self.costumePageWindow.AddFlag("attach")
	self.costumePageWindow.SetPosition(*mainBoardPos)

def InitDungeonPageWindow(self):
	self.dungeonPageWindow = ingamewikidungeon.WikiDungeonWindow()
	self.dungeonPageWindow.SetParent(self.baseBoard)
	self.dungeonPageWindow.AddFlag("attach")
	self.dungeonPageWindow.SetPosition(*mainBoardPos)

def InitBiologPageWindow(self):
	self.biologPageWindow = ingamewikibiolog.WikiBiologWindow()
	self.biologPageWindow.SetParent(self.baseBoard)
	self.biologPageWindow.AddFlag("attach")
	self.biologPageWindow.SetPosition(*mainBoardPos)

def InitDragonSoulPageWindow(self):
	self.dragonSoulPageWindow = ingamewikidragonsoul.WikiDragonSoulWindow()
	self.dragonSoulPageWindow.SetParent(self.baseBoard)
	self.dragonSoulPageWindow.AddFlag("attach")
	self.dragonSoulPageWindow.SetPosition(*mainBoardPos)

def InitGrowthPetPageWindow(self):
	self.growthPetPageWindow = ingamewikigrowthpet.WikiGrowthPetWindow()
	self.growthPetPageWindow.SetParent(self.baseBoard)
	self.growthPetPageWindow.AddFlag("attach")
	self.growthPetPageWindow.SetPosition(*mainBoardPos)

def InitGrowthMountPageWindow(self):
	self.growthMountPageWindow = ingamewikigrowthmount.WikiGrowthMountWindow()
	self.growthMountPageWindow.SetParent(self.baseBoard)
	self.growthMountPageWindow.AddFlag("attach")
	self.growthMountPageWindow.SetPosition(*mainBoardPos)

def InitGemShopPageWindow(self):
	self.gemShopPageWindow = ingamewikigemshop.WikiGemShopWindow()
	self.gemShopPageWindow.SetParent(self.baseBoard)
	self.gemShopPageWindow.AddFlag("attach")
	self.gemShopPageWindow.SetPosition(*mainBoardPos)

def InitBuffiPageWindow(self):
	self.buffiPageWindow = ingamewikibuffi.WikiBuffiWindow()
	self.buffiPageWindow.SetParent(self.baseBoard)
	self.buffiPageWindow.AddFlag("attach")
	self.buffiPageWindow.SetPosition(*mainBoardPos)

if app.USE_EXTENDED_WIKI_CRAFT:
	def InitCraftItemPageWindow(self):
		self.craftItemPageWindow = WikiItemCraftWindow()
		self.craftItemPageWindow.SetParent(self.baseBoard)
		self.craftItemPageWindow.AddFlag("attach")
		self.craftItemPageWindow.SetPosition(*mainBoardPos)

if app.USE_EXTENDED_WIKI_SHOP:
	def InitShopPageWindow(self):
		self.shopPageWindow = WikiShopWindow()
		self.shopPageWindow.SetParent(self.baseBoard)
		self.shopPageWindow.AddFlag("attach")
		self.shopPageWindow.SetPosition(*mainBoardPos)

if app.ENABLE_ITEM_SHOPS:
	def InitShopItemPageWindow(self):
		self.shopItemPageWindow = WikiMainShopItemWindow()
		self.shopItemPageWindow.SetParent(self.baseBoard)
		self.shopItemPageWindow.AddFlag("attach")
		self.shopItemPageWindow.SetPosition(*mainBoardPos)

def InitTitleBar(self):
	self.titleBar = ui.TitleBar()
	self.titleBar.SetParent(self.baseBoard)
	self.titleBar.MakeTitleBar(0, "red")
	self.titleBar.SetWidth(self.GetWidth() - 15)
	self.titleBar.SetPosition(8, 7)
	self.titleBar.SetCloseEvent(self.Close)
	self.titleBar.Show()
	
	self.titleName = ui.TextLine()
	self.titleName.SetParent(self.titleBar)
	self.titleName.SetPosition(0, 4)
	self.titleName.SetPosition(0, 4)
	self.titleName.SetWindowHorizontalAlignCenter()
	self.titleName.SetHorizontalAlignCenter()
	self.titleName.SetText(localeinfo.WIKI_TITLENAME)
	self.titleName.Show()

def BuildSearchWindow(self):
	self.searchBG = ui.ExpandedImageBox()
	self.searchBG.SetParent(self.baseBoard)
	self.searchBG.LoadImage("d:/ymir work/ui/wiki/searchfield_new.tga")
	self.searchBG.SetPosition(13, 33+4)
	self.searchBG.Show()
	
	self.searchButton = ui.Button()
	self.searchButton.SetParent(self.searchBG)
	self.searchButton.SetUpVisual("d:/ymir work/ui/wiki/search_btn_s_0.png")
	self.searchButton.SetOverVisual("d:/ymir work/ui/wiki/search_btn_s_1.png")
	self.searchButton.SetDownVisual("d:/ymir work/ui/wiki/search_btn_s_2.png")
	self.searchButton.SetPosition(self.searchBG.GetWidth() - self.searchButton.GetWidth() - 2, self.searchBG.GetHeight() / 2 - self.searchButton.GetHeight() / 2)
	self.searchButton.SAFE_SetEvent(self.StartSearch)
	self.searchButton.Show()
	
	self.searchEdit = ui.EditLine()
	self.searchEdit.SetParent(self.searchBG)
	self.searchEdit.SetMax(50)
	self.searchEdit.SetSize(111 - self.searchButton.GetWidth() - 2, 15)
	self.searchEdit.SetPosition(5, self.searchBG.GetHeight() / 2 - 15 / 2)
	# self.searchEdit.SetOverlayText(localeinfo.WIKI_SEARCH_OVERLAY_TEXT)
	# self.searchEdit.SetLimitWidth(self.searchEdit.GetWidth())

	if app.USE_GRAPHIC_TEXT_SEARCH_BOX_WIDTH_LIMIT:
		self.searchEdit.SetSearchBoxLimitWidth(self.searchEdit.GetWidth())

	self.searchEdit.SetEscapeEvent(ui.__mem_func__(self.OnPressNameEscapeKey))
	self.searchEdit.SetReturnEvent(ui.__mem_func__(self.StartSearch))
	self.searchEdit.SetUpdateEvent(ui.__mem_func__(self.Search_RefreshResults))
	self.searchEdit.SetTabEvent(ui.__mem_func__(self.OnPressSearchTab))
	self.searchEdit.SetOutline()
	self.searchEdit.Show()

	# Inline ghost-text prediction. Sits as a sibling of the edit, drawn in
	# gray right after the typed text. Long item names trail off the visible
	# edit area but the dropdown still shows the full name, so this is just
	# a "hit Tab to fill this in" affordance, not a full preview.
	self.searchHint = ui.TextLine()
	self.searchHint.SetParent(self.searchBG)
	self.searchHint.SetPackedFontColor(0xFF808080)
	self.searchHint.Hide()

	import ingamewikisearch
	# Parent the dropdown to the wiki Window itself (sibling of baseBoard) so
	# SetTop() puts it above the entire wiki content frame, not just above
	# baseBoard's other children. baseBoard sits at (0, 0) inside the wiki
	# window, so coordinates inside baseBoard map 1:1 here.
	# Width is wider than searchBG so multi-word item names fit on one row;
	# the dropdown is intentionally a bit chunkier than the edit field.
	self.searchResults = ingamewikisearch.WikiSearchResults(width = max(self.searchBG.GetWidth() + 50, 175))
	self.searchResults.SetParent(self)
	self.searchResults.SetPosition(
		self.searchBG.GetLocalPosition()[0],
		self.searchBG.GetLocalPosition()[1] + self.searchBG.GetHeight() + 2)
	self.searchResults.SetPickEvent(ui.__mem_func__(self.OnSearchResultPicked))

def BuildBaseMain(self):
	if app.USE_EXTENDED_WIKI_CRAFT or app.USE_EXTENDED_WIKI_SHOP or app.ENABLE_ITEM_SHOPS:
		ingamewikiconfig.Load()

	self.baseBoard = ui.ExpandedImageBox()
	self.baseBoard.AddFlag("attach")
	self.baseBoard.SetParent(self)
	self.baseBoard.LoadImage("D:/Ymir Work/ui/wiki/bg.png")
	self.baseBoard.SetWindowName("InGameWikiBoard")
	self.baseBoard.Show()
	
	self.SetSize(self.baseBoard.GetWidth(), self.baseBoard.GetHeight())
	
	self.header = ui.ExpandedImageBox()
	self.header.SetParent(self.baseBoard)
	self.header.SetPosition(149, 37)
	
	BuildSearchWindow(self)
	
	self.categText = ui.TextLine()
	self.categText.SetParent(self.baseBoard)
	if localeinfo.IsARABIC():
		self.categText.SetPosition(100, self.searchBG.GetLocalPosition()[1] + self.searchBG.GetHeight()+25)# arabic
	else :
		self.categText.SetPosition(13, self.searchBG.GetLocalPosition()[1] + self.searchBG.GetHeight() + 25)# english 


	self.categ = WikiCategories()
	self.categ.hideWindowsEvent = ui.__mem_func__(self.CloseBaseWindows)
	self.categ.SetParent(self.baseBoard)
	self.categ.AddFlag("attach")
	self.categ.SetPosition(13, 107)
	self.categ.Show()
	
	self.prevButt = ui.Button()
	self.prevButt.SetParent(self.baseBoard)
	self.prevButt.SetUpVisual("d:/ymir work/ui/wiki/btn_arrow_left_normal.png")
	self.prevButt.SetOverVisual("d:/ymir work/ui/wiki/btn_arrow_left_hover.png")
	self.prevButt.SetDownVisual("d:/ymir work/ui/wiki/btn_arrow_left_down.png")
	self.prevButt.SetDisableVisual("d:/ymir work/ui/wiki/btn_arrow_left_down.png")
	self.prevButt.SetPosition(self.categ.GetLocalPosition()[0]-3, self.categ.GetLocalPosition()[1] + self.categ.GetHeight() + 3)
	self.prevButt.SAFE_SetEvent(self.OnPressPrevButton)
	self.prevButt.Show()
	self.prevButt.Disable()
	
	self.nextButt = ui.Button()
	self.nextButt.SetParent(self.baseBoard)
	self.nextButt.SetUpVisual("d:/ymir work/ui/wiki/btn_arrow_right_normal.png")
	self.nextButt.SetOverVisual("d:/ymir work/ui/wiki/btn_arrow_right_hover.png")
	self.nextButt.SetDownVisual("d:/ymir work/ui/wiki/btn_arrow_right_down.png")
	self.nextButt.SetDisableVisual("d:/ymir work/ui/wiki/btn_arrow_right_down.png")
	self.nextButt.SetPosition(19+self.categ.GetLocalPosition()[0] + self.categ.GetWidth() - self.nextButt.GetWidth(), self.categ.GetLocalPosition()[1] + self.categ.GetHeight() + 3)
	self.nextButt.SAFE_SetEvent(self.OnPressNextButton)
	self.nextButt.Show()
	self.nextButt.Disable()
	
	self.scrollBar = WikiScrollBar()
	self.scrollBar.SetParent(self.baseBoard)
	self.scrollBar.SetPosition(self.categ.GetLocalPosition()[0] + self.categ.GetWidth() + 5, self.categ.GetLocalPosition()[1])
	self.scrollBar.SetSize(7, categoryPeakWindowSize[1])
	self.scrollBar.Show()

	self.categ.RegisterScrollBar(self.scrollBar)

	InitTitleBar(self)
	InitMainWeaponWindow(self)
	InitMainChestWindow(self)
	InitMainBossWindow(self)
	InitCustomPageWindow(self)
	InitCostumePageWindow(self)
	InitDungeonPageWindow(self)
	InitBiologPageWindow(self)
	InitDragonSoulPageWindow(self)
	InitGrowthPetPageWindow(self)
	InitGrowthMountPageWindow(self)
	InitGemShopPageWindow(self)
	InitBuffiPageWindow(self)

	if app.USE_EXTENDED_WIKI_CRAFT:
		InitCraftItemPageWindow(self)

	if app.USE_EXTENDED_WIKI_SHOP:
		InitShopPageWindow(self)

	if app.ENABLE_ITEM_SHOPS:
		InitShopItemPageWindow(self)

	funclist = [
		ui.__mem_func__(self.mainWeaponWindow.Show),
		ui.__mem_func__(self.mainChestWindow.Show),
		ui.__mem_func__(self.mainBossWindow.Show),
		ui.__mem_func__(self.mainBossWindow.Show),
		ui.__mem_func__(self.mainBossWindow.Show),
		ui.__mem_func__(self.costumePageWindow.Show),
		ui.__mem_func__(self.costumePageWindow.Show),
		ui.__mem_func__(self.customPageWindow.LoadFile),
		ui.__mem_func__(self.customPageWindow.LoadFile),
		ui.__mem_func__(self.OpenDungeonRoute),
	]

	if app.USE_EXTENDED_WIKI_CRAFT:
		funclist.append(ui.__mem_func__(self.craftItemPageWindow.Show))

	if app.USE_EXTENDED_WIKI_SHOP:
		funclist.append(ui.__mem_func__(self.shopPageWindow.Show))

	if app.ENABLE_ITEM_SHOPS:
		funclist.append(ui.__mem_func__(self.shopItemPageWindow.Show))

	hiddenCategories = getattr(ingamewikiconfig, "WIKI_HIDDEN_CATEGORIES", [])

	for i in ingamewikiconfig.WIKI_CATEGORIES:
		if i[0] in hiddenCategories:
			continue

		ret = self.categ.AddCategory(i[0])

		for j in xrange(len(i[1])):
			ret.AddSubCategory(j, i[1][j])

		curr = ingamewikiconfig.WIKI_CATEGORIES.index(i)
		if curr < len(funclist):
			ret.clickEvent = funclist[curr]

		# Index-independent binding: the positional funclist mapping above
		# mis-assigns when the category count shifts. Force the Dungeons
		# category onto the data-driven dungeon-page dispatcher.
		if i[0] == localeinfo.WIKI_CATEGORY_DUNGEONS:
			ret.clickEvent = ui.__mem_func__(self.OpenDungeonRoute)

		if i[0] == localeinfo.WIKI_CATEGORY_SYSTEMS:
			ret.clickEvent = ui.__mem_func__(self.OpenSystemRoute)

	self.customPageWindow.LoadFile("landingpage.txt")
	self.header.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.GoToLanding))

	# NOTE: the GM Drop Editor used to attach a global "Edit Mode" toggle here.
	# It now lives on SpecialPageWindow (the per-entity detail page) instead --
	# the main listing pages have ~150 rows and overlaying every one was a mess.
	# See SpecialPageWindow._DropEditor_Setup.
