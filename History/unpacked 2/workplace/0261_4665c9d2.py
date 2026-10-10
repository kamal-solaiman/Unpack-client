# coding: latin_1

import app
import net
import player

import ui
import uibadge
import localeinfo

import systemSetting

class GameButtonWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__LoadWindow("UIScript/gamewindow.py")

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadWindow(self, filename):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, filename)

		except Exception, msg:
			import dbg
			dbg.TraceError("GameButtonWindow.LoadScript - %s" % (msg))
			app.Abort()
			return False

		try:
			self.gameButtonDict = {
				"STATUS" : self.GetChild("StatusPlusButton"),
				"SKILL" : self.GetChild("SkillPlusButton"),
				"QUEST" : self.GetChild("QuestButton"),
				"HELP" : self.GetChild("HelpButton"),
				"BUILD" : self.GetChild("BuildGuildBuilding"),
				"EXIT_OBSERVER" : self.GetChild("ExitObserver"),
			}

			if app.USE_DUNGEON_INFO and app.USE_DUNGEON_INFO_ADDON_LEVEL_CAP:
				self.gameButtonDict["LEVEL_CAP"] = self.GetChild("levelcap_button")
			else:
				self.GetChild("levelcap_button").Hide()

			if app.ENABLE_REWARD_SYSTEM:
				self.gameButtonDict["CHALLENGE"] = self.GetChild("ChallengeMapButton")
				uibadge.Attach("challenge_map", self.gameButtonDict["CHALLENGE"])

			self.gameButtonDict["EXIT_OBSERVER"].SetEvent(ui.__mem_func__(self.__OnClickExitObserver))

			if app.ENABLE_GEM_SYSTEM:
				posx, posy = self.gameButtonDict["SKILL"].GetGlobalPosition()
				#self.gameButtonDict["SKILL"].SetPosition(posx, posy - 25 )

				posx, posy = self.gameButtonDict["BUILD"].GetGlobalPosition()
				self.gameButtonDict["BUILD"].SetPosition(posx, posy - 25 )

				posx, posy = self.gameButtonDict["EXIT_OBSERVER"].GetGlobalPosition()
				self.gameButtonDict["EXIT_OBSERVER"].SetPosition(posx, posy - 25)
		except Exception, msg:
			import dbg
			dbg.TraceError("GameButtonWindow.LoadScript - %s" % (msg))
			app.Abort()
			return False

		self.__HideAllGameButton()
		self.SetObserverMode(player.IsObserverMode())
		return True

	def Destroy(self):
		if app.ENABLE_REWARD_SYSTEM:
			uibadge.Detach("challenge_map")

		for key in self.gameButtonDict:
			self.gameButtonDict[key].SetEvent(0)

		self.gameButtonDict={}

	def SetButtonEvent(self, name, event):
		try:
			self.gameButtonDict[name].SetEvent(event)

		except Exception, msg:
			print "GameButtonWindow.LoadScript - %s" % (msg)
			app.Abort()
			return

	def ShowBuildButton(self):
		self.gameButtonDict["BUILD"].Show()

	def HideBuildButton(self):
		self.gameButtonDict["BUILD"].Hide()

	def CheckGameButton(self):
		if not self.IsShow():
			return

		statusPlusButton=self.gameButtonDict["STATUS"]
		skillPlusButton=self.gameButtonDict["SKILL"]
		helpButton=self.gameButtonDict["HELP"]

		if player.GetStatus(player.STAT) > 0:
			statusPlusButton.Show()
		else:
			statusPlusButton.Hide()

		if self.__IsSkillStat():
			skillPlusButton.Show()
		else:
			skillPlusButton.Hide()

		if 0 == player.GetPlayTime():
			helpButton.Show()
		else:
			helpButton.Hide()

	if app.USE_DUNGEON_INFO and app.USE_DUNGEON_INFO_ADDON_LEVEL_CAP:
		def RefreshCapLevelButton(self, isON):
			if isON:
				self.gameButtonDict["LEVEL_CAP"].Show()
			else:
				self.gameButtonDict["LEVEL_CAP"].Hide()

	if app.ENABLE_REWARD_SYSTEM:
		# localeinfo answers a missing key with "Locale not found: KEY" instead of raising,
		# so a plain getattr default never applies -- and would then blow up the % format.
		def __ChallengeLocaleText(self, key, default):
			value = getattr(localeinfo, key, default)
			if not value or value.startswith("Locale not found"):
				return default

			return value

		def RefreshChallengeMapButton(self, total, here):
			button = getattr(self, "gameButtonDict", {}).get("CHALLENGE")
			if not button:
				return

			uibadge.SetCount("challenge_map", here)
			if total <= 0:
				button.Hide()
				return

			if here > 0:
				text = self.__ChallengeLocaleText("CHALLENGE_MAP_BTN_HERE",
					"%d challenges are waiting for you on this map.") % here
			else:
				text = self.__ChallengeLocaleText("CHALLENGE_MAP_BTN_NONE",
					"Opens your challenges - you still have challenges left to do.")
			button.SetToolTipText(text)
			button.Show()

	def __IsSkillStat(self):
		if player.GetStatus(player.SKILL_ACTIVE) > 0:
			return True

		return False

	def __OnClickExitObserver(self):
		net.SendChatPacket("/observer_exit")

	def __HideAllGameButton(self):
		for btn in self.gameButtonDict.values():
			btn.Hide()

	def SetObserverMode(self, isEnable):
		if isEnable:
			self.gameButtonDict["EXIT_OBSERVER"].Show()
		else:
			self.gameButtonDict["EXIT_OBSERVER"].Hide()
