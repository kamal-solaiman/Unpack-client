# coding: latin_1
# ENABLE_DUNGEON_HUD - quest-data-driven dungeon HUD.
# Activated by server command "DgnHudTimer <deadlineEpoch> <run|grace>" (broadcast through
# the northwinddeeps_timer transport), deactivated by "DgnHudOff", deadline expiry, or any
# warp (interface rebuild). While active it also captures the CHAT_TYPE_MISSION texts that
# would otherwise render on the legacy screen-wide uitip.MissionBoard bar.

import app
import ui
import net
import snd
import wndMgr
import localeinfo
import uitooltip
import uicommon
# The board itself is shared with the weekly-challenge tracker; only the dungeon-specific
# geometry below stays here.
from uihudboard import HudBoard, IMG_PATH, BOARD_W, BOARD_H, BOARD_GAP, \
	COLOR_TITLE, COLOR_TIMER_OK, COLOR_TIMER_WARN, COLOR_TIMER_DANGER, COLOR_SUB, COLOR_FLASH, \
	WARN_SECONDS, DANGER_SECONDS, FLASH_TIME
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr

BTN_SIZE = 63
BTN_GAP = 6
RIGHT_OFFSET = 240
MARGIN_TOP = 108



class DungeonHud(ui.Window):
	MODE_RUN = "run"
	MODE_GRACE = "grace"

	def __init__(self):
		ui.Window.__init__(self)
		self.AddFlag("float")

		self.active = False
		self.deadline = 0
		self.mode = self.MODE_RUN
		self.lastShownSecond = -1
		self.dangerPlayed = False
		self.flashBoard = None
		self.flashUntil = 0.0
		self.questionDialog = None
		self.tooltip = None

		self.__Build()
		self.Hide()

	def __del__(self):
		ui.Window.__del__(self)

	def __Build(self):
		totalH = BOARD_H * 2 + BOARD_GAP
		self.SetSize(BTN_SIZE + BTN_GAP + BOARD_W, totalH)

		btn = ui.Button()
		btn.SetParent(self)
		btn.SetPosition(0, int((totalH - BTN_SIZE) / 2))
		btn.SetUpVisual(IMG_PATH + "rejoin_norm.png")
		btn.SetOverVisual(IMG_PATH + "rejoin_hover.png")
		btn.SetDownVisual(IMG_PATH + "rejoin_down.png")
		btn.SetEvent(ui.__mem_func__(self.__OnLeaveClick))
		btn.SetOverEvent(ui.__mem_func__(self.__OnOverIn))
		btn.SetOverOutEvent(ui.__mem_func__(self.__OnOverOut))
		btn.Show()
		self.leaveButton = btn

		self.timerBoard = HudBoard(self)
		self.timerBoard.SetPosition(BTN_SIZE + BTN_GAP, 0)
		self.timerBoard.SetTitle(getattr(localeinfo, "DUNGEON_HUD_COMPLETE", "Complete the dungeon"))
		self.timerBoard.Show()

		self.objectiveBoard = HudBoard(self)
		self.objectiveBoard.SetPosition(BTN_SIZE + BTN_GAP, BOARD_H + BOARD_GAP)
		self.objectiveBoard.Hide()

		try:
			tt = uitooltip.ToolTip(200)
			tt.SetFollow(False)
			tt.ClearToolTip()
			tt.AppendTextLine(getattr(localeinfo, "DUNGEON_HUD_LEAVE", "Leave dungeon"))
			tt.HideToolTip()
			self.tooltip = tt
		except:
			self.tooltip = None

		self.__AnchorToScreen()

	def __AnchorToScreen(self):
		try:
			sw = wndMgr.GetScreenWidth()
		except:
			sw = 1024
		self.SetPosition(int(max(0, sw - RIGHT_OFFSET - self.GetWidth())), MARGIN_TOP)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - RIGHT_OFFSET - self.GetWidth(), MARGIN_TOP)})

	def SetTimer(self, deadline, mode):
		self.deadline = int(deadline)
		self.mode = mode
		self.lastShownSecond = -1
		self.dangerPlayed = False

		try:
			now = int(app.GetGlobalTimeStamp())
		except:
			now = 0
		if self.deadline <= now:
			self.Deactivate()
			return

		if self.mode == self.MODE_GRACE:
			self.timerBoard.SetTitle(getattr(localeinfo, "DUNGEON_HUD_LEAVE_IN", "Returning to town in"))
			self.CleanMission()
			self.__StartFlash(self.timerBoard)
			snd.PlaySound("sound/ui/click.wav")
		else:
			self.timerBoard.SetTitle(getattr(localeinfo, "DUNGEON_HUD_COMPLETE", "Complete the dungeon"))

		self.active = True
		self.__AnchorToScreen()
		self.__RefreshTimer(now)
		self.SetTop()
		self.Show()

	def Deactivate(self):
		self.active = False
		self.deadline = 0
		self.flashBoard = None
		self.__CloseDialog()
		self.CleanMission()
		if self.tooltip:
			try:
				self.tooltip.HideToolTip()
			except:
				pass
		self.Hide()

	def IsActive(self):
		return self.active

	def SetMission(self, text):
		self.objectiveBoard.SetTitle(text)
		self.objectiveBoard.Show()
		self.__StartFlash(self.objectiveBoard)
		snd.PlaySound("sound/ui/click.wav")

	def SetSubMission(self, text):
		self.objectiveBoard.SetValue(text)
		self.objectiveBoard.Show()

	def CleanMission(self):
		if not getattr(self, "objectiveBoard", None):
			return
		self.objectiveBoard.SetTitle("")
		self.objectiveBoard.SetValue("")
		self.objectiveBoard.Hide()

	def __StartFlash(self, board):
		self.flashBoard = board
		try:
			self.flashUntil = app.GetTime() + FLASH_TIME
		except:
			self.flashUntil = 0.0

	def __RefreshTimer(self, now):
		remaining = max(0, self.deadline - now)
		mm = int(remaining / 60)
		ss = int(remaining % 60)
		if self.mode == self.MODE_GRACE:
			color = COLOR_TIMER_WARN
		elif remaining <= DANGER_SECONDS:
			color = COLOR_TIMER_DANGER
			if not self.dangerPlayed:
				self.dangerPlayed = True
				snd.PlaySound("sound/ui/heartbeat.wav")
		elif remaining <= WARN_SECONDS:
			color = COLOR_TIMER_WARN
		else:
			color = COLOR_TIMER_OK
		self.timerBoard.SetValue("%d:%02d" % (mm, ss), color)

	def OnUpdate(self):
		try:
			if not getattr(self, "active", False):
				return

			if self.flashBoard:
				try:
					t = app.GetTime()
				except:
					t = self.flashUntil
				if t >= self.flashUntil:
					self.flashBoard.SetTitleColor(COLOR_TITLE)
					self.flashBoard = None
				elif int(t * 6) % 2:
					self.flashBoard.SetTitleColor(COLOR_FLASH)
				else:
					self.flashBoard.SetTitleColor(COLOR_TITLE)

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

	def __OnLeaveClick(self):
		if self.questionDialog:
			return
		dlg = uicommon.QuestionDialog()
		dlg.SetText(getattr(localeinfo, "DUNGEON_HUD_LEAVE_CONFIRM", "Leave the dungeon?"))
		dlg.SetAcceptEvent(ui.__mem_func__(self.__OnLeaveAccept))
		dlg.SetCancelEvent(ui.__mem_func__(self.__OnLeaveCancel))
		dlg.Open()
		self.questionDialog = dlg

	def __OnLeaveAccept(self):
		net.SendChatPacket("/dungeon_leave")
		self.__CloseDialog()

	def __OnLeaveCancel(self):
		self.__CloseDialog()

	def __CloseDialog(self):
		if getattr(self, "questionDialog", None):
			self.questionDialog.Close()
			self.questionDialog = None

	def __OnOverIn(self):
		if self.tooltip:
			try:
				self.tooltip.SetPosition(self.GetLeft(), self.GetTop() + self.GetHeight() + 4)
				self.tooltip.SetTop()
				self.tooltip.ShowToolTip()
			except:
				pass

	def __OnOverOut(self):
		if self.tooltip:
			try:
				self.tooltip.HideToolTip()
			except:
				pass
