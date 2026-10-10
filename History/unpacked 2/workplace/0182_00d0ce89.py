# coding: latin_1
#
# On-screen tracker for the running weekly challenge.
#
# Raised only while a *timed* challenge is active -- untimed ones tick all week and would leave
# the board on screen permanently. The board design comes from uihudboard, the same one the
# dungeon timer draws, anchored underneath it so the two never overlap.
#
# The countdown is display only. The server is the authority on expiry; it re-sends the board.

import app
import ui
import wndMgr
import uichallengetooltip
from uihudboard import HudBoard, BOARD_W, BOARD_H, BOARD_GAP, COLOR_TITLE, COLOR_SUB, TimerColor
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr

# Directly below the dungeon HUD, in the same right-hand column: a dungeon run and a timed
# challenge can be live at once, and stacking them is the only arrangement that never collides.
RIGHT_OFFSET = 240
MARGIN_TOP = 240

MAX_TARGET_BOARDS = 4


class ChallengeHud(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.AddFlag("float")

		self.active = False
		self.deadline = 0
		self.lastShownSecond = -1
		self.headerBoard = None
		self.targetBoards = []
		self.targetZones = []
		self.targetLookup = {}
		self.hudTitle = ""

		self.headerBoard = HudBoard(self)
		self.headerBoard.SetPosition(0, 0)
		self.headerBoard.Show()

		self.SetSize(BOARD_W, BOARD_H)
		self.Hide()

	def __del__(self):
		ui.Window.__del__(self)

	# Grown on demand and kept: a board is cheap, and rebuilding the stack every progress tick
	# would drop widgets the window manager is still drawing.
	def __Board(self, index):
		while len(self.targetBoards) <= index:
			slot = len(self.targetBoards)
			y = (slot + 1) * (BOARD_H + BOARD_GAP)

			board = HudBoard(self)
			board.SetPosition(0, y)
			board.Hide()
			self.targetBoards.append(board)

			# HudBoard is not_pick, and it belongs to the dungeon timer as much as to us, so the
			# hover lives on an overlay of our own. Created after the board, which is what puts it
			# on top of it.
			zone = ui.Window()
			zone.SetParent(self)
			zone.SetPosition(0, y)
			zone.SetSize(BOARD_W, BOARD_H)
			zone.SetOverInEvent(ui.__mem_func__(self.OnTargetOverIn), slot)
			zone.SetOverOutEvent(ui.__mem_func__(self.OnTargetOverOut))
			zone.Hide()
			self.targetZones.append(zone)

		return self.targetBoards[index]

	def OnTargetOverIn(self, slot):
		lookup = self.targetLookup.get(slot)
		if not lookup:
			return

		(kind, vnum) = lookup
		toolTip = uichallengetooltip.GetToolTip()
		toolTip.SetTargets(self.hudTitle, [(kind, [vnum])])
		toolTip.ShowNearMouse()

	def OnTargetOverOut(self):
		uichallengetooltip.HideToolTip()

	def __Anchor(self, boardCount):
		height = (boardCount + 1) * BOARD_H + boardCount * BOARD_GAP
		self.SetSize(BOARD_W, height)

		try:
			screenWidth = wndMgr.GetScreenWidth()
		except:
			screenWidth = 1024

		self.SetPosition(int(max(0, screenWidth - RIGHT_OFFSET - BOARD_W)), MARGIN_TOP)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - RIGHT_OFFSET - BOARD_W, MARGIN_TOP)})

	# targets are (name, have, need, kind, vnum), already localized by the caller. kind/vnum are
	# what the hover looks up and may be (None, 0) for a target with nothing to show.
	def SetChallenge(self, title, deadline, targets):
		self.deadline = int(deadline)
		self.lastShownSecond = -1

		try:
			now = int(app.GetGlobalTimeStamp())
		except:
			now = 0

		if self.deadline <= now:
			self.Deactivate()
			return

		self.hudTitle = title
		self.headerBoard.SetTitle(title)
		self.headerBoard.SetTitleColor(COLOR_TITLE)
		self.SetTargets(targets)

		self.active = True
		self.__RefreshTimer(now)
		self.SetTop()
		self.Show()

	def SetTargets(self, targets):
		shown = min(len(targets), MAX_TARGET_BOARDS)
		self.targetLookup = {}

		for i in range(shown):
			target = targets[i]
			(name, have, need) = target[0], target[1], target[2]
			board = self.__Board(i)
			board.SetTitle(name)
			board.SetValue("%d / %d" % (have, need), COLOR_SUB)
			board.Show()

			# Only a target the tooltip can actually draw gets a hit region; the rest stay inert
			# rather than answering a hover with an empty board.
			kind = target[3] if len(target) > 4 else None
			if kind:
				self.targetLookup[i] = (kind, target[4])
				self.targetZones[i].Show()
			else:
				self.targetZones[i].Hide()

		for i in range(shown, len(self.targetBoards)):
			self.targetBoards[i].Hide()
			self.targetZones[i].Hide()

		self.__Anchor(shown)

	def Deactivate(self):
		self.active = False
		self.deadline = 0
		# A hidden window fires no OverOut, so a tooltip raised from here would stay on screen.
		uichallengetooltip.HideToolTip()
		self.Hide()

	def IsActive(self):
		return self.active

	def __RefreshTimer(self, now):
		remaining = max(0, self.deadline - now)
		self.headerBoard.SetValue("%d:%02d" % (int(remaining / 60), int(remaining % 60)), TimerColor(remaining))

	def OnUpdate(self):
		try:
			if not getattr(self, "active", False):
				return

			now = int(app.GetGlobalTimeStamp())
			if now == self.lastShownSecond:
				return

			self.lastShownSecond = now
			if now >= self.deadline:
				self.Deactivate()
				return

			self.__RefreshTimer(now)
		except:
			pass
