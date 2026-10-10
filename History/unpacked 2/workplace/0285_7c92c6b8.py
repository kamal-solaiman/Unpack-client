# coding: latin_1
#
# Small always-on-top progress popup shown while a horse upgrade mission is
# in progress. Lives alongside HorseUpgradeWindow but stays visible after the
# main window is closed so the player gets passive feedback while farming.

import app
import ui
import item
import nonplayer
import localeinfo
import horseupgrade
import uihorseupgradeconfig as cfg

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions


# Pony summon item — used for the popup's "open main window" icon so the
# button visually reads as horse-related without needing a custom asset.
HORSE_ICON_VNUM = 50052

# Gauge assets, reused from the alignment / battle-pass UI.
PATH_BP_QUEST = "d:/ymir work/ui/game/battle_pass_reworked/slice/quest/"

# Layout constants — kept in sync with uiscript/horseupgradepopupwindow.py.
WINDOW_WIDTH = 340
WINDOW_HEIGHT = 100
CENTER_X = WINDOW_WIDTH / 2

# Horse-window asset path (for the time icon).
HORSE_IMG = "d:/ymir work/ui/game/horse/"


class HorseUpgradeProgressPopup(ui.ScriptWindow):
	WINDOW_ID = "horse_upgrade_popup"

	def __init__(self, parentWnd):
		ui.ScriptWindow.__init__(self)
		self.parentWnd = parentWnd
		self.isLoaded = False
		self.iconBtn = None
		self.closeBtn = None
		self.killsGaugeBack = None
		self.killsGaugeFull = None
		self.killsText = None
		self.timeIcon = None
		self.timeText = None

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/horseupgradepopupwindow.py")
		except:
			return

		# --- Horse icon (left edge): clickable, opens main horse window. ---
		try:
			icon = ui.ImageBox()
			icon.SetParent(self)
			icon.SetPosition(10, 10)
			icon.AddFlag("float")
			item.SelectItem(HORSE_ICON_VNUM)
			icon.LoadImage(item.GetIconImageFileName())
			icon.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.__OnClickIcon))
			icon.Show()
			self.iconBtn = icon
		except:
			pass

		# --- Close X (right edge): hides + disables for session. ---
		try:
			closeText = ui.TextLine()
			closeText.SetParent(self)
			closeText.SetPosition(WINDOW_WIDTH - 18, 10)
			closeText.SetText("X")
			closeText.AddFlag("float")
			closeText.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.__OnClickClose))
			closeText.Show()
			self.closeBtn = closeText
		except:
			pass

		# --- Kills gauge (uialignment-style: quest_bar + quest_innerbar) ---
		try:
			gaugeBack = ui.MakeExpandedImageBox(self,
				PATH_BP_QUEST + "quest_bar.png", 15, 50, "not_pick")
			gaugeFull = ui.MakeExpandedImageBox(gaugeBack,
				PATH_BP_QUEST + "quest_innerbar.png", 0, 2, "not_pick")
			gaugeFull.SetRenderingRect(0.0, 0.0, -1.0, 0.0)
			self.killsGaugeBack = gaugeBack
			self.killsGaugeFull = gaugeFull
		except:
			pass

		# Kills text overlay (centred on the gauge).
		try:
			text = ui.TextLine()
			text.SetParent(self)
			text.SetPosition(CENTER_X, 52)
			text.SetHorizontalAlignCenter()
			text.SetOutline()
			text.AddFlag("float")
			text.Show()
			self.killsText = text
		except:
			pass

		# --- Time row: clock icon + compact countdown, centered. ---
		try:
			tIcon = ui.ImageBox()
			tIcon.SetParent(self)
			tIcon.SetPosition(CENTER_X - 50, 73)
			tIcon.AddFlag("float")
			tIcon.LoadImage(HORSE_IMG + "icon_time.png")
			tIcon.Show()
			self.timeIcon = tIcon

			tText = ui.TextLine()
			tText.SetParent(self)
			tText.SetPosition(CENTER_X - 22, 75)
			tText.AddFlag("float")
			tText.Show()
			self.timeText = tText
		except:
			pass

		self.isLoaded = True

	def Destroy(self):
		self.parentWnd = None
		self.iconBtn = None
		self.closeBtn = None
		self.killsGaugeBack = None
		self.killsGaugeFull = None
		self.killsText = None
		self.timeIcon = None
		self.timeText = None
		self.ClearDictionary()

	def Open(self):
		if not self.isLoaded:
			return
		# Only restore saved position the first time we show — otherwise the
		# popup would snap back every frame when game.py keeps Open()-ing it
		# to keep it visible across warps.
		if not self.IsShow():
			if app.ENABLE_WINDOW_POSITION_SAVE and \
			   uiwindowpositions.ApplySavedPosition(self, self.WINDOW_ID):
				pass
			else:
				self.SetPosition(20, 100)
		self.Show()
		self.__Refresh()

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, self.WINDOW_ID)
		self.Hide()

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove(self.WINDOW_ID, x, y)

	def OnUpdate(self):
		if self.IsShow():
			self.__Refresh()

	def __OnClickClose(self):
		# Clicking the X disables the popup for this session — the player
		# can re-enable it from the main window's toggle.
		if self.parentWnd:
			try: self.parentWnd.SetPopupEnabled(False)
			except: pass
		self.Close()

	def __OnClickIcon(self):
		# The horse icon doubles as the "open horse page" button.
		if not self.parentWnd:
			return
		try:
			if not self.parentWnd.IsShow():
				self.parentWnd.Open()
			else:
				self.parentWnd.SetTop()
		except:
			pass

	def __Refresh(self):
		if not self.parentWnd:
			return
		state = self.parentWnd.state
		n = state["horse_level"]
		if n < 1 or n > horseupgrade.MAX_MISSION:
			return
		m = cfg.GetMission(n)
		if not m:
			return
		try:    targetName = nonplayer.GetMonsterName(m["TargetVnum"])
		except: targetName = ""
		if not targetName:
			targetName = str(m["TargetVnum"])

		self.GetChild("popup_title_text").SetText(
			localeinfo.HORSE_UPGRADE_POPUP_TITLE_FMT % n)

		# Kills gauge fill — ratio of kills / target, clamped 0..1.
		kills = state["kills"]
		target = m["TargetCount"]
		ratio = (float(kills) / float(target)) if target > 0 else 0.0
		if ratio < 0.0: ratio = 0.0
		if ratio > 1.0: ratio = 1.0
		if self.killsGaugeFull:
			try: self.killsGaugeFull.SetRenderingRect(0.0, 0.0, -(1.0 - ratio), 0.0)
			except: pass
		if self.killsText:
			try: self.killsText.SetText(
				localeinfo.HORSE_UPGRADE_PROGRESS_FMT % (kills, target, targetName))
			except: pass

		endTime = state["start_time"] + m["Duration"]
		leftTime = endTime - app.GetGlobalTimeStamp()
		if leftTime < 0: leftTime = 0
		h  = leftTime / 3600
		mi = (leftTime % 3600) / 60
		sec = leftTime % 60
		# Short, prefix-less format ("H:MM:SS") — the clock icon next to the
		# text is enough context; full-sentence "Time remaining: ..." would
		# clash with the icon and is redundant.
		fmt = getattr(localeinfo, "HORSE_UPGRADE_POPUP_TIME_FMT", "%d:%02d:%02d")
		if self.timeText:
			try: self.timeText.SetText(fmt % (h, mi, sec))
			except: pass
