# coding: latin_1
#
# The on-screen HUD board, shared by every tracker that wants one.
#
# Extracted verbatim from uidungeonhud.py so the dungeon timer and the weekly-challenge tracker
# render the same board instead of two copies drifting apart. Anything that is board *design* --
# size, colours, the countdown thresholds -- lives here; where the board is anchored and what it
# says stay with the tracker that owns it.

import ui

IMG_PATH = "d:/ymir work/ui/"

BOARD_W = 209
BOARD_H = 53
BOARD_GAP = 4

COLOR_TITLE = 0xFFF2E7C1
COLOR_TIMER_OK = 0xFF6EE26E
COLOR_TIMER_WARN = 0xFFFFD24D
COLOR_TIMER_DANGER = 0xFFFF5A5A
COLOR_SUB = 0xFF8CE28C
COLOR_FLASH = 0xFFFFFFFF

WARN_SECONDS = 180
DANGER_SECONDS = 60
FLASH_TIME = 1.2


def TimerColor(remaining):
	if remaining <= DANGER_SECONDS:
		return COLOR_TIMER_DANGER
	if remaining <= WARN_SECONDS:
		return COLOR_TIMER_WARN

	return COLOR_TIMER_OK


class HudBoard(ui.Window):
	def __init__(self, parent):
		ui.Window.__init__(self)
		self.SetParent(parent)
		self.AddFlag("not_pick")
		self.SetSize(BOARD_W, BOARD_H)

		bg = ui.ImageBox()
		bg.SetParent(self)
		bg.AddFlag("not_pick")
		bg.LoadImage(IMG_PATH + "bg_mission.png")
		bg.SetPosition(0, 0)
		bg.Show()
		self.bg = bg

		title = ui.TextLine()
		title.SetParent(self)
		title.SetPosition(int(BOARD_W / 2), 10)
		title.SetHorizontalAlignCenter()
		title.SetOutline()
		title.SetPackedFontColor(COLOR_TITLE)
		title.SetText("")
		title.Show()
		self.title = title

		value = ui.TextLine()
		value.SetParent(self)
		value.SetPosition(int(BOARD_W / 2), 29)
		value.SetHorizontalAlignCenter()
		value.SetOutline()
		value.SetPackedFontColor(COLOR_SUB)
		value.SetText("")
		value.Show()
		self.value = value

	def __del__(self):
		ui.Window.__del__(self)

	def SetTitle(self, text):
		self.title.SetText(text)

	def SetValue(self, text, color=None):
		self.value.SetText(text)
		if color is not None:
			self.value.SetPackedFontColor(color)

	def SetTitleColor(self, color):
		self.title.SetPackedFontColor(color)
