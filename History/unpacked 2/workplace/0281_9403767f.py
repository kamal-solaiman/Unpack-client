# coding: latin_1

import app
import net
import ui
import chat
import player
import item
import chr
import nonplayer
import localeinfo
import uitooltip
import uicommon
import horseupgrade
import uihorseupgradeconfig as cfg
import uihorseupgradepopup
from _weakref import proxy

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

if app.ENABLE_INGAME_WIKI:
	import ingamewikiui


class HorseUpgradeWindow(ui.ScriptWindow):
	WINDOW_ID = "horse_upgrade"

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.isLoaded = False

		# Server-pushed state (filled in by BINARY_HorseUpgradeState).
		self.state = {
			"horse_level"     : 1,
			"state"           : horseupgrade.STATE_IDLE,
			"kills"           : 0,
			"start_time"      : 0,
			"cooldown_until"  : 0,
			"chance_bonus"    : 0,
		}

		# Render preview + tooltips (Phase 10 hooks them up).
		self.targetRender = None
		self.targetOverlay = None
		self.targetToolTip = None
		self.itemOverlay = None
		self.itemToolTip = None
		self.levelToolTip = None
		self.levelOverlay = None
		self.helperResetOverlay = None
		self.helperChanceOverlay = None

		# Wiki bridge (bound from game.py after wndWiki is constructed).
		self.wikiInst = None

		# Internal scratch.
		self._lastTargetVnum = 0
		self._pendingConfirm = None

		# Progress popup — small always-on-top window shown during IN_PROGRESS.
		# Enabled by default; the player can hide it via the toggle on this
		# window or by clicking the popup's close glyph.
		self.progressPopup = None
		self.popupEnabled = True
		self.popupToggleIcon = None
		self.popupToggleLabel = None
		self.popupToggleTooltip = None

	def BindWikiInst(self, wikiInst):
		if wikiInst:
			self.wikiInst = proxy(wikiInst)

	def __LoadWindow(self):
		if self.isLoaded:
			return
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/horseupgradewindow.py")
		except:
			import exception
			exception.Abort("HorseUpgradeWindow.__LoadWindow.LoadScriptFile")
			return

		try:
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
			self.GetChild("start_btn").SAFE_SetEvent(self.__OnClickStart)
			self.GetChild("TitleName").SetText(localeinfo.HORSE_UPGRADE_TITLE)
		except:
			import exception
			exception.Abort("HorseUpgradeWindow.__LoadWindow.BindEvents")
			return

		# Load helper icons BEFORE creating overlays, otherwise parent.GetWidth()
		# returns 0 (image empty) and the overlay ends up unclickable.
		self.__RefreshHelperButtonLabels()

		# Helper items are images — wrap each in a click overlay (mirrors targetOverlay).
		# Left-click uses the item; right-click opens its wiki page.
		# Lambdas resolve the active-tier vnum at call time (swaps with horse level).
		self.helperResetOverlay = self.__MakeOverlay(
			self.GetChild("helper_reset_btn"),
			self.__OnClickReset,
			lambda: self.__OnOverInItem(self.__GetActiveResetVnum(), True),
			ui.__mem_func__(self.__OnOverOutItem),
			lambda: self.__OnClickItemSlot(self.__GetActiveResetVnum()))
		self.helperChanceOverlay = self.__MakeOverlay(
			self.GetChild("helper_chance_btn"),
			self.__OnClickChance,
			lambda: self.__OnOverInItem(self.__GetActiveChanceVnum(), True),
			ui.__mem_func__(self.__OnOverOutItem),
			lambda: self.__OnClickItemSlot(self.__GetActiveChanceVnum()))

		# Progress popup — instantiated once, shown/hidden based on state.
		try:
			self.progressPopup = uihorseupgradepopup.HorseUpgradeProgressPopup(proxy(self))
		except:
			self.progressPopup = None

		# Popup toggle — visible checkbox + label, modelled on
		# fastLoginAutoSaveIcon. Constructed in code so it doesn't depend on
		# locale strings shipping in the .epk.
		self.__BuildPopupToggle()

		# Phase 12 — cumulative-affect tooltip on Current Level text.
		# TextLine doesn't support SetEventOverIn directly, so we layer a
		# transparent ui.Window overlay (same pattern as item-slot/target overlays).
		try:
			levelText = self.GetChild("current_level_text")
			overlay = ui.Window()
			overlay.SetParent(levelText)
			overlay.SetSize(levelText.GetWidth(), levelText.GetHeight())
			overlay.SetPosition(0, 0)
			overlay.SetOverInEvent(ui.__mem_func__(self.__OnOverInLevel))
			overlay.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutLevel))
			overlay.Show()
			self.levelOverlay = overlay
		except:
			pass

		self.isLoaded = True

	def Destroy(self):
		if self.targetRender:
			del self.targetRender
			self.targetRender = None
		self.targetOverlay = None
		self.targetToolTip = None
		self.itemOverlay = None
		self.itemToolTip = None
		self.levelToolTip = None
		self.levelOverlay = None
		self.helperResetOverlay = None
		self.helperChanceOverlay = None
		if self.progressPopup:
			try: self.progressPopup.Destroy()
			except: pass
			self.progressPopup = None
		self.__HidePopupTooltip()
		self.popupToggleIcon = None
		self.popupToggleLabel = None
		self.wikiInst = None
		self._pendingConfirm = None
		self.ClearDictionary()

	def Open(self):
		if not self.isLoaded:
			self.__LoadWindow()

		if app.ENABLE_WINDOW_POSITION_SAVE and \
		   uiwindowpositions.ApplySavedPosition(self, self.WINDOW_ID):
			pass
		else:
			self.SetCenterPosition()

		self.Show()
		self.SetTop()

		# Tell the server to (re)send our current upgrade state.
		horseupgrade.RequestOpen()

		self.__Refresh()

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, self.WINDOW_ID)
		self.Hide()

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove(self.WINDOW_ID, x, y)

	def OnPressEscapeKey(self):
		self.Close()
		return True

	# ------------------------------------------------------------------
	# Server -> client state push (routed from GameWindow.BINARY_*)
	# ------------------------------------------------------------------
	def BINARY_HorseUpgradeState(self, horseLevel, state, kills, startTime, cooldownUntil, chanceBonus):
		self.state.update({
			"horse_level"     : horseLevel,
			"state"           : state,
			"kills"           : kills,
			"start_time"      : startTime,
			"cooldown_until"  : cooldownUntil,
			"chance_bonus"    : chanceBonus,
		})
		if self.IsShow():
			self.__Refresh()
		self.__SyncProgressPopup()

	# ------------------------------------------------------------------
	# Button handlers — bare requests, Phase 10 wraps them in confirms.
	# ------------------------------------------------------------------
	HIGH_COST_YANG_THRESHOLD = 1000000

	def __OnClickStart(self):
		state = self.state["state"]
		horseLevel = self.state["horse_level"]
		if state == horseupgrade.STATE_IN_PROGRESS:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.HORSE_UPGRADE_BTN_IN_PROGRESS)
			return
		if state == horseupgrade.STATE_COOLDOWN_SUCCESS or state == horseupgrade.STATE_COOLDOWN_FAIL:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.HORSE_UPGRADE_ERR_IN_COOLDOWN)
			return
		if horseLevel > horseupgrade.MAX_MISSION:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.HORSE_UPGRADE_MAX_REACHED)
			return
		n = horseLevel if (1 <= horseLevel <= horseupgrade.MAX_MISSION) else 0
		m = cfg.GetMission(n)
		if not m:
			return
		if player.GetStatus(player.LEVEL) < m["MinLevel"]:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.HORSE_UPGRADE_ERR_LEVEL_LOW)
			return
		try: gold = player.GetElk()
		except: gold = 0
		if gold < m["Gold"]:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.HORSE_UPGRADE_ERR_NEED_GOLD)
			return
		if m["ItemVnum"] != 0:
			have = 0
			if hasattr(player, "GetItemCountByVnum"):
				try: have = player.GetItemCountByVnum(m["ItemVnum"])
				except: have = 0
			if have < m["ItemCount"]:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.HORSE_UPGRADE_ERR_NEED_ITEM)
				return
		if m["Gold"] >= self.HIGH_COST_YANG_THRESHOLD or m["ItemCount"] > 0:
			self.__OpenConfirm(m)
		else:
			horseupgrade.RequestStart()

	def __OpenConfirm(self, m):
		try:
			item.SelectItem(m["ItemVnum"])
			itemName = item.GetItemName() if m["ItemVnum"] else ""
		except:
			itemName = ""
		body = localeinfo.HORSE_UPGRADE_CONFIRM_BODY_FMT % (
			localeinfo.NumberToMoneyString(m["Gold"]),
			m["ItemCount"], itemName,
			min(100, m["SuccessChance"] + self.state["chance_bonus"]))

		missionNum = self.state["horse_level"]
		dlg = uicommon.QuestionDialog2()
		try: dlg.SetWidth(360)
		except: pass
		dlg.SetText1(localeinfo.HORSE_UPGRADE_CONFIRM_TITLE_FMT % missionNum)
		dlg.SetText2(body)
		dlg.SetAcceptEvent(ui.__mem_func__(self.__OnConfirmYes))
		dlg.SetCancelEvent(ui.__mem_func__(self.__OnConfirmCancel))
		dlg.Open()
		self._pendingConfirm = dlg

	def __OnConfirmYes(self):
		if self._pendingConfirm:
			try: self._pendingConfirm.Close()
			except: pass
			self._pendingConfirm = None
		horseupgrade.RequestStart()

	def __OnConfirmCancel(self):
		if self._pendingConfirm:
			try: self._pendingConfirm.Close()
			except: pass
			self._pendingConfirm = None

	# ------------------------------------------------------------------
	# Progress popup glue — show during IN_PROGRESS when enabled.
	# ------------------------------------------------------------------
	POPUP_TOGGLE_CHECKED_IMG   = "d:/ymir work/ui/dungeoninfo_rework/checked_box.png"
	POPUP_TOGGLE_UNCHECKED_IMG = "d:/ymir work/ui/dungeoninfo_rework/check_box.png"

	def __BuildPopupToggle(self):
		# ImageBox checkbox (16x16-ish) at the right side of the time row in bg_2.
		try:
			icon = ui.ImageBox()
			icon.SetParent(self)
			icon.SetPosition(250, 180)
			icon.AddFlag("float")
			icon.LoadImage(self.POPUP_TOGGLE_CHECKED_IMG if self.popupEnabled else self.POPUP_TOGGLE_UNCHECKED_IMG)
			icon.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.__OnTogglePopup))
			icon.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__ShowPopupTooltip)
			icon.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__HidePopupTooltip)
			icon.Show()
			self.popupToggleIcon = icon

			# Plain text label next to the checkbox so the player knows what it does.
			label = ui.TextLine()
			label.SetParent(self)
			label.SetPosition(270, 182)
			label.SetText(getattr(localeinfo, "HORSE_UPGRADE_POPUP_LABEL", "Live Popup"))
			label.Show()
			self.popupToggleLabel = label
		except:
			pass

	def __RefreshPopupToggleIcon(self):
		if not self.popupToggleIcon:
			return
		try:
			self.popupToggleIcon.LoadImage(
				self.POPUP_TOGGLE_CHECKED_IMG if self.popupEnabled
				else self.POPUP_TOGGLE_UNCHECKED_IMG)
		except:
			pass

	def __ShowPopupTooltip(self):
		self.__HidePopupTooltip()
		try:
			tipText = getattr(localeinfo, "HORSE_UPGRADE_POPUP_TOGGLE_TIP",
				"Show the live mission progress popup while a mission is in progress.")
			tp = ui.ThinBoard("TOP_MOST", 2)
			tp.AddFlag("float")
			tp.AddFlag("not_pick")
			textLine = ui.TextLine()
			textLine.SetParent(tp)
			textLine.SetPosition(10, 8)
			textLine.SetText(tipText)
			textLine.SetOutline()
			textLine.Show()
			tw, th = textLine.GetTextSize()
			tp.SetSize(tw + 20, th + 16)
			import wndMgr
			mx, my = wndMgr.GetMousePosition()
			tp.SetPosition(mx + 15, my + 15)
			tp.Show()
			self.popupToggleTooltip = tp
		except:
			self.popupToggleTooltip = None

	def __HidePopupTooltip(self):
		if self.popupToggleTooltip:
			try: self.popupToggleTooltip.Hide()
			except: pass
			self.popupToggleTooltip = None

	def SetPopupEnabled(self, enabled):
		self.popupEnabled = bool(enabled)
		self.__RefreshPopupToggleIcon()
		self.__SyncProgressPopup()

	def __OnTogglePopup(self):
		self.SetPopupEnabled(not self.popupEnabled)

	def __SyncProgressPopup(self):
		if not self.progressPopup:
			return
		shouldShow = self.popupEnabled and \
			self.state["state"] == horseupgrade.STATE_IN_PROGRESS
		if shouldShow:
			try:
				# Open() is idempotent (it only restores position on first show).
				# Calling Show() + SetTop() afterwards forces the engine to render
				# the popup even if a map transition just hid it.
				self.progressPopup.Open()
				self.progressPopup.Show()
				self.progressPopup.SetTop()
			except:
				pass
		else:
			try:
				if self.progressPopup.IsShow():
					self.progressPopup.Close()
			except:
				pass

	# Public hook for interfacemodule to call after a warp / map transition,
	# so the popup re-asserts itself even if the engine hid it.
	def EnsurePopupVisible(self):
		self.__SyncProgressPopup()

	# Called by interfacemodule.SetMapName when the player finishes warping.
	# Map transitions can destroy the underlying C++ widget of a top-level
	# ScriptWindow while leaving the Python reference dangling. Re-creating
	# the popup from scratch is the only reliable way to get it back. We
	# also ask the server for fresh state so the gauge/timer are correct.
	def OnMapChanged(self):
		if self.progressPopup:
			try: self.progressPopup.Destroy()
			except: pass
			self.progressPopup = None
		try:
			self.progressPopup = uihorseupgradepopup.HorseUpgradeProgressPopup(proxy(self))
		except:
			self.progressPopup = None
		try: horseupgrade.RequestOpen()
		except: pass
		self.__SyncProgressPopup()

	def __IsHardTier(self):
		return self.state["horse_level"] >= horseupgrade.HARD_TIER_MIN

	def __GetActiveChanceVnum(self):
		return horseupgrade.ITEM_CHANCE_HARD if self.__IsHardTier() else horseupgrade.ITEM_CHANCE

	def __GetActiveResetVnum(self):
		return horseupgrade.ITEM_RESET_HARD if self.__IsHardTier() else horseupgrade.ITEM_RESET

	def __OnClickChance(self):
		if self.__IsHardTier():
			horseupgrade.RequestUseChanceItemHard()
		else:
			horseupgrade.RequestUseChanceItem()

	def __OnClickReset(self):
		if self.__IsHardTier():
			horseupgrade.RequestUseResetItemHard()
		else:
			horseupgrade.RequestUseResetItem()

	# ------------------------------------------------------------------
	# Phase 10 — UI state rendering.
	# ------------------------------------------------------------------
	def __GetTargetName(self, vnum):
		try:
			name = nonplayer.GetMonsterName(vnum)
		except:
			name = ""
		if not name:
			name = str(vnum)
		return name

	def __Refresh(self):
		horseLevel = self.state["horse_level"]
		nextLevel  = horseLevel + 1

		self.GetChild("current_level_text").SetText(
			localeinfo.HORSE_UPGRADE_CURRENT_LEVEL % horseLevel)
		if horseLevel >= horseupgrade.MAX_MISSION + 1:
			self.GetChild("next_level_text").SetText(localeinfo.HORSE_UPGRADE_NEXT_LEVEL_MAX)
		else:
			self.GetChild("next_level_text").SetText(localeinfo.HORSE_UPGRADE_NEXT_LEVEL % nextLevel)

		activeMission = horseLevel if (1 <= horseLevel <= horseupgrade.MAX_MISSION) else 0
		m = cfg.GetMission(activeMission) if activeMission else None
		if m is None:
			self.GetChild("mission_defeat_text").SetText("")
			self.GetChild("mission_level_text").SetText("")
			self.GetChild("mission_yang_text").SetText("")
			self.GetChild("mission_item_text").SetText("")
			self.GetChild("gauge_text").SetText(localeinfo.HORSE_UPGRADE_MAX_REACHED)
			self.GetChild("time_text").SetText("")
			self.GetChild("start_btn").Hide()
			try: self.GetChild("start_btn").DisableHoverPulse()
			except: pass
			return

		targetName = self.__GetTargetName(m["TargetVnum"])
		self.GetChild("mission_defeat_text").SetText(
			localeinfo.HORSE_UPGRADE_DEFEAT_FMT % (m["TargetCount"], targetName))
		self.GetChild("mission_level_text").SetText(
			localeinfo.HORSE_UPGRADE_PLAYER_LEVEL_FMT % m["MinLevel"])
		self.GetChild("mission_yang_text").SetText(
			localeinfo.HORSE_UPGRADE_YANG_FMT % localeinfo.NumberToMoneyString(m["Gold"]))

		# Row 3: required item name + count
		try:
			item.SelectItem(m["ItemVnum"])
			itemName = item.GetItemName() if m["ItemVnum"] else ""
		except:
			itemName = ""
		self.GetChild("mission_item_text").SetText(
			localeinfo.HORSE_UPGRADE_ITEM_FMT % (m["ItemCount"], itemName))

		self.GetChild("start_btn").Show()
		self.__RefreshGauge(m, targetName)
		self.__RefreshChanceLine(m)
		self.__RefreshStartButton(m)
		self.__RefreshHelperButtonLabels()
		self.__BuildTargetRender(m)
		self.__RefreshItemSlot(m)

	def __RefreshHelperButtonLabels(self):
		self.GetChild("helper_reset_text").SetText(localeinfo.HORSE_UPGRADE_TIP_RESET_SCROLL)
		self.GetChild("helper_chance_text").SetText(localeinfo.HORSE_UPGRADE_TIP_CHANCE_ELIXIR)
		try:
			item.SelectItem(self.__GetActiveResetVnum())
			self.GetChild("helper_reset_btn").LoadImage(item.GetIconImageFileName())
		except: pass
		try:
			item.SelectItem(self.__GetActiveChanceVnum())
			self.GetChild("helper_chance_btn").LoadImage(item.GetIconImageFileName())
		except: pass

	def __RefreshGauge(self, m, targetName):
		state = self.state["state"]
		kills = self.state["kills"]
		gaugeFill = self.GetChild("gauge_fill")
		gaugeText = self.GetChild("gauge_text")

		if state == horseupgrade.STATE_IN_PROGRESS:
			gaugeFill.Show()
			ratio = float(kills) / float(m["TargetCount"]) if m["TargetCount"] > 0 else 0.0
			if ratio > 1.0: ratio = 1.0
			try: gaugeFill.SetRenderingRect(0.0, 0.0, -1.0 + ratio, 0.0)
			except: pass
			gaugeText.SetText(localeinfo.HORSE_UPGRADE_PROGRESS_FMT % (kills, m["TargetCount"], targetName))
			try: gaugeText.SetPackedFontColor(0xFFFFFFFF)
			except: pass
			endTime = self.state["start_time"] + m["Duration"]
			leftTime = endTime - app.GetGlobalTimeStamp()
			if leftTime < 0: leftTime = 0
			h  = leftTime / 3600
			mi = (leftTime % 3600) / 60
			sec = leftTime % 60
			self.GetChild("time_text").SetText(localeinfo.HORSE_UPGRADE_TIME_FMT % (h, mi, sec))
		elif state == horseupgrade.STATE_COOLDOWN_SUCCESS:
			gaugeFill.Hide()
			leftTime = self.state["cooldown_until"] - app.GetGlobalTimeStamp()
			if leftTime < 0: leftTime = 0
			h  = leftTime / 3600
			mi = (leftTime % 3600) / 60
			sec = leftTime % 60
			gaugeText.SetText(localeinfo.HORSE_UPGRADE_GAUGE_COOLDOWN_SUCCESS_FMT % (h, mi, sec))
			try: gaugeText.SetPackedFontColor(0xFF2ecc71)
			except: pass
			self.GetChild("time_text").SetText("")
		elif state == horseupgrade.STATE_COOLDOWN_FAIL:
			gaugeFill.Hide()
			leftTime = self.state["cooldown_until"] - app.GetGlobalTimeStamp()
			if leftTime < 0: leftTime = 0
			h  = leftTime / 3600
			mi = (leftTime % 3600) / 60
			sec = leftTime % 60
			gaugeText.SetText(localeinfo.HORSE_UPGRADE_GAUGE_COOLDOWN_FAIL_FMT % (h, mi, sec))
			try: gaugeText.SetPackedFontColor(0xFFe74c3c)
			except: pass
			self.GetChild("time_text").SetText("")
		else:
			gaugeFill.Hide()
			gaugeText.SetText(localeinfo.HORSE_UPGRADE_GAUGE_READY)
			try: gaugeText.SetPackedFontColor(0xFFFFFFFF)
			except: pass
			self.GetChild("time_text").SetText("")

	def __RefreshChanceLine(self, m):
		bonus = self.state["chance_bonus"]
		if bonus > 0:
			total = m["SuccessChance"] + bonus
			if total > 100: total = 100
			self.GetChild("chance_breakdown_text").SetText(
				localeinfo.HORSE_UPGRADE_CHANCE_BREAKDOWN_FMT % (m["SuccessChance"], bonus, total))
		else:
			self.GetChild("chance_breakdown_text").SetText("")

	def __RefreshStartButton(self, m):
		state = self.state["state"]
		btn = self.GetChild("start_btn")
		try: btn.Enable()
		except: pass
		if state == horseupgrade.STATE_IN_PROGRESS:
			btn.SetText(localeinfo.HORSE_UPGRADE_BTN_IN_PROGRESS)
			try: btn.DisableHoverPulse()
			except: pass
			return
		if state == horseupgrade.STATE_COOLDOWN_SUCCESS or state == horseupgrade.STATE_COOLDOWN_FAIL:
			btn.SetText(localeinfo.HORSE_UPGRADE_BTN_COOLDOWN)
			try: btn.DisableHoverPulse()
			except: pass
			return
		btn.SetText(localeinfo.HORSE_UPGRADE_BTN_START)
		if self.__CanStart(m):
			try:
				btn.EnableHoverPulse()
				btn.SetHoverPulseSpeed(1.5)
			except: pass
		else:
			try: btn.DisableHoverPulse()
			except: pass

	def __CanStart(self, m):
		if self.state["horse_level"] > horseupgrade.MAX_MISSION:
			return False
		if player.GetStatus(player.LEVEL) < m["MinLevel"]:
			return False
		try:
			gold = player.GetElk()
		except:
			gold = 0
		if gold < m["Gold"]:
			return False
		if m["ItemVnum"] != 0:
			if hasattr(player, "GetItemCountByVnum"):
				have = player.GetItemCountByVnum(m["ItemVnum"])
			else:
				have = 0
			if have < m["ItemCount"]:
				return False
		return True

	# ------------------------------------------------------------------
	# Phase 11 — Target mob render, required item slot, wiki hooks.
	# ------------------------------------------------------------------
	def __MakeOverlay(self, parent, click_cb, over_in_cb, over_out_cb, right_click_cb=None):
		w = parent.GetWidth()
		h = parent.GetHeight()
		if w <= 0: w = 32
		if h <= 0: h = 32
		overlay = ui.Window()
		overlay.SetParent(parent)
		overlay.SetSize(w, h)
		overlay.SetPosition(0, 0)
		overlay.SetOnMouseLeftButtonUpEvent(click_cb)
		overlay.SetOverInEvent(over_in_cb)
		overlay.SetOverOutEvent(over_out_cb)
		if right_click_cb is not None:
			try: overlay.SetMouseRightButtonUpEvent(right_click_cb)
			except: pass
		overlay.Show()
		return overlay

	def __BuildTargetRender(self, m):
		if not app.ENABLE_INGAME_WIKI:
			return
		board = self.GetChild("target_render_board")

		if self.targetRender and self._lastTargetVnum == m["TargetVnum"]:
			return

		if self.targetRender:
			del self.targetRender
			self.targetRender = None
		if self.targetOverlay:
			self.targetOverlay.Hide()
			del self.targetOverlay
			self.targetOverlay = None

		self._lastTargetVnum = m["TargetVnum"]
		rt = ingamewikiui.WikiRenderTarget(board.GetWidth(), board.GetHeight())
		rt.SetParent(board)
		rt.SetPosition(0, 0)
		rt.SetModel(m["TargetVnum"], False, False)
		rt.Show()
		self.targetRender = rt

		overlay = ui.Window()
		overlay.SetParent(board)
		overlay.SetSize(board.GetWidth(), board.GetHeight())
		overlay.SetPosition(0, 0)
		overlay.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.__OnClickTarget))
		overlay.SetOverInEvent(ui.__mem_func__(self.__OnOverInTarget))
		overlay.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutTarget))
		overlay.Show()
		self.targetOverlay = overlay

	def __OnClickTarget(self):
		if not app.ENABLE_INGAME_WIKI or not self.wikiInst:
			return
		if not self.wikiInst.IsShow():
			net.ToggleWikiWindow()
		try: self.wikiInst.CloseBaseWindows()
		except: pass
		self.wikiInst.OpenSpecialPage(None, self._lastTargetVnum, True)

	def __OnOverInTarget(self):
		horseLevel = self.state["horse_level"]
		activeMission = horseLevel if (1 <= horseLevel <= horseupgrade.MAX_MISSION) else 0
		m = cfg.GetMission(activeMission)
		if not m:
			return
		if not self.targetToolTip:
			self.targetToolTip = uitooltip.ToolTip()
		self.targetToolTip.ClearToolTip()
		self.targetToolTip.AppendTextLine(localeinfo.HORSE_UPGRADE_TIP_MISSION_REWARDS)
		self.targetToolTip.AppendSpace(5)
		anyReward = False
		for r in m["rewards"]:
			if r["apply_type"] == 0:
				continue
			anyReward = True
			try:
				line = uitooltip.GET_AFFECT_STRING(r["apply_type"], r["value"])
			except:
				line = "%s +%s" % (r["apply_name"], r["value"])
			self.targetToolTip.AppendTextLine(line)
		if not anyReward:
			self.targetToolTip.AppendTextLine("-")
		self.targetToolTip.AppendSpace(10)
		self.targetToolTip.AppendShortcutRow(("key_lclick",), localeinfo.HORSE_UPGRADE_CLICK_WIKI)
		self.targetToolTip.ShowToolTip()

	def __OnOverOutTarget(self):
		if self.targetToolTip:
			self.targetToolTip.HideToolTip()

	def __RefreshItemSlot(self, m):
		iconWidget = self.GetChild("item_slot_icon")
		countText  = self.GetChild("item_slot_count")
		if m["ItemVnum"] == 0:
			iconWidget.Hide()
			countText.Hide()
			if self.itemOverlay:
				self.itemOverlay.Hide()
			return
		try:
			item.SelectItem(m["ItemVnum"])
			iconPath = item.GetIconImageFileName()
			iconWidget.LoadImage(iconPath)
		except:
			pass
		iconWidget.Show()

		try:
			have = player.GetItemCountByVnum(m["ItemVnum"])
		except:
			have = 0
		color = 0xFF2ecc71 if have >= m["ItemCount"] else 0xFFe74c3c
		countText.SetText(localeinfo.HORSE_UPGRADE_ITEM_COUNT_FMT % m["ItemCount"])
		try: countText.SetPackedFontColor(color)
		except: pass
		countText.Show()

		if not self.itemOverlay:
			overlay = ui.Window()
			overlay.SetParent(iconWidget)
			overlay.SetSize(iconWidget.GetWidth(), iconWidget.GetHeight())
			overlay.SetPosition(0, 0)
			self.itemOverlay = overlay
		self.itemOverlay.Show()
		vnum = m["ItemVnum"]
		self.itemOverlay.SetOnMouseLeftButtonUpEvent(lambda: self.__OnClickItemSlot(vnum))
		self.itemOverlay.SetOverInEvent(lambda: self.__OnOverInItem(vnum))
		self.itemOverlay.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutItem))

	def __OnClickItemSlot(self, vnum):
		if not app.ENABLE_INGAME_WIKI or not self.wikiInst:
			return
		if not self.wikiInst.IsShow():
			net.ToggleWikiWindow()
		try: self.wikiInst.CloseBaseWindows()
		except: pass
		self.wikiInst.OpenSpecialPage(None, vnum, False)

	def __OnOverInItem(self, vnum, withClickHints=False):
		if not self.itemToolTip:
			self.itemToolTip = uitooltip.ItemToolTip()
		try:
			self.itemToolTip.ClearToolTip()
			self.itemToolTip.SetItemToolTip(vnum)
			if withClickHints:
				self.itemToolTip.DeclareShortcut(("key_lclick",), localeinfo.HORSE_UPGRADE_TIP_HELPER_LCLICK)
				self.itemToolTip.DeclareShortcut(("key_rclick",), localeinfo.HORSE_UPGRADE_TIP_HELPER_RCLICK)
			self.itemToolTip.ShowToolTip()
		except:
			pass

	def __OnOverOutItem(self):
		if self.itemToolTip:
			try: self.itemToolTip.HideToolTip()
			except: pass

	def __OnOverInLevel(self):
		horseLevel = self.state["horse_level"]
		if not self.levelToolTip:
			self.levelToolTip = uitooltip.ToolTip()
		self.levelToolTip.ClearToolTip()
		self.levelToolTip.AppendTextLine(localeinfo.HORSE_UPGRADE_TIP_YOUR_REWARDS)
		self.levelToolTip.AppendSpace(5)
		totals = {}
		for n in xrange(1, horseLevel + 1):
			mm = cfg.GetMission(n)
			if not mm:
				continue
			for r in mm["rewards"]:
				if r["apply_type"] == 0:
					continue
				totals[r["apply_type"]] = totals.get(r["apply_type"], 0) + r["value"]
		if not totals:
			self.levelToolTip.AppendTextLine("-")
		else:
			for apply_type, val in totals.items():
				try:
					line = uitooltip.GET_AFFECT_STRING(apply_type, val)
				except:
					line = "%d +%d" % (apply_type, val)
				self.levelToolTip.AppendTextLine(line)
		self.levelToolTip.ShowToolTip()

	def __OnOverOutLevel(self):
		if self.levelToolTip:
			try: self.levelToolTip.HideToolTip()
			except: pass

	def OnUpdate(self):
		if not self.isLoaded or not self.IsShow():
			return
		horseLevel = self.state["horse_level"]
		activeMission = horseLevel if (1 <= horseLevel <= horseupgrade.MAX_MISSION) else 0
		m = cfg.GetMission(activeMission) if activeMission else None
		if m is None:
			return
		targetName = self.__GetTargetName(m["TargetVnum"])
		self.__RefreshGauge(m, targetName)
		self.__RefreshStartButton(m)
