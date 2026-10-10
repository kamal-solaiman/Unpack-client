# coding: latin_1

import app
import chr
import chrmgr
import net
import player

import os
import dbg
import grp
import item
import background
import snd
import chat
import textTail
import effect
import wndMgr
import uiphasecurtain
if app.ENABLE_DROPINFO_REWORK:
	import uidropInfo
if app.ENABLE_EXTENDED_BATTLE_PASS:
	import uibattlepassextended
if app.WHEEL_INGAME:
	import uispinwheel
if app.ENABLE_CAPTCHA_SYSTEM:
	import uiCaptcha
import hwidManager
import systemSetting
import quest
import guild
import skill
import messenger
import messagescache
import localeinfo
import constinfo
import osfinfo
import exchange
import ime

import ui
import uicommon
import uimapnameshower
import uiaffectshower
import uiplayergauge
import uicharacter
import uitarget

import uiprivateshopbuilder

import mousemodule
import consolemodule
import localeinfo
import random
import playersettingmodule
import interfacemodule

import musicinfo
import debuginfo
import stringcommander
import uiruhtasi
if app.ENABLE_BIOLOG_SYSTEM:
	import uiprofessionalbiolog

from _weakref import proxy
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr

if app.USE_OFFLINESHOP:
	import uiofflineshop_ae
	import offlineshop

import saryongstory

if app.ENABLE_ITEMSHOP:
	import uiitemshop

if app.ENABLE_DAILY_ALCHEMY_ORE or app.__SPIN_WHEEL_DUNGEON__:
	import uispinwheel

if app.ENABLE_KEYCHANGE_SYSTEM:
	import uikeychange

if app.USE_PVP_TOURNAMENT:
	import pvp_tournament

SCREENSHOT_CWDSAVE = False
SCREENSHOT_DIR = None

if localeinfo.IsEUROPE():
	SCREENSHOT_CWDSAVE = True

if localeinfo.IsCIBN10():
	SCREENSHOT_CWDSAVE = False
	SCREENSHOT_DIR = "YT2W"

cameraDistance = 1550.0
cameraPitch = 27.0
cameraRotation = 0.0
cameraHeight = 100.0

testAlignment = 0

if app.ENABLE_INGAME_WIKI and app.ENABLE_FAST_WARP_UI:
	class LazyWikiBinding(object):
		# Truthy stand-in handed to every wiki-consuming window at warp time so
		# their "if self.wndWiki:" guards keep working before the first build.
		# The first real attribute access (always a click handler - no consumer
		# polls the wiki) builds the wiki via GameWindow.__BuildWiki, which
		# rebinds all consumers to the real wiki; the access is then forwarded.
		# Holds only weak __mem_func__ wrappers - no ref cycle with GameWindow.
		def __init__(self, buildFunc, getFunc):
			self.lazyBuildFunc = buildFunc
			self.lazyGetFunc = getFunc

		def __getattr__(self, name):
			if name.startswith("lazy"):
				raise AttributeError(name)
			wiki = self.lazyGetFunc()
			if not wiki:
				self.lazyBuildFunc()
				wiki = self.lazyGetFunc()
			if not wiki:
				raise AttributeError(name)
			return getattr(wiki, name)

		def __nonzero__(self):
			return True

class GameWindow(ui.ScriptWindow):
	def __init__(self, stream):
		if constinfo.ENABLE_MULTI_RANKING:
			self.rankingWindow =None
		ui.ScriptWindow.__init__(self, "GAME")
		self.SetWindowName("game")
		net.SetPhaseWindow(net.PHASE_WINDOW_GAME, self)
		player.SetGameWindow(self)

		self.quickSlotPageIndex = 0
		self.lastPKModeSendedTime = 0
		if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
			self.curtain = uiphasecurtain.PhaseCurtain()
			self.curtain.speed = 0.03
		self.pressNumber = None
		self.ruhtasi = uiruhtasi.RuhTasi()
		self.ruhtasi.Hide()

		self.guildWarQuestionDialog = None
		self.interface = None
		self.targetBoard = None

		self.console = None
		self.mapNameShower = None
		self.affectShower = None
		self.playerGauge = None
		self.removeQuestionDialog = None
		if app.WHEEL_INGAME:
			self.wheelWindow = None
			self.wheelWindow = uispinwheel.WheelWindow()
			self.wheelWindow.Show()
		if app.ENABLE_KEYCHANGE_SYSTEM:
			self.wndKeyChange = None
		if app.ENABLE_EXTENDED_BATTLE_PASS:
			self.isFirstOpeningExtBattlePass = False
		
		self.stream=stream
		self.interface = interfacemodule.Interface()

		self.interface.MakeInterface()
		self.interface.ShowDefaultWindows()

		self.targetBoard = uitarget.TargetBoard()
		self.targetBoard.SetWhisperEvent(ui.__mem_func__(self.interface.OpenWhisperDialog))
		self.targetBoard.Hide()
		self.interface.SettargetBoard(self.targetBoard)

		if app.ENABLE_COMBAT_POINTS:
			import cpinfo
			cpinfo.LoadGearCPTable("gear_cp.txt")

		if app.ENABLE_CAPTCHA_SYSTEM:
			self.wndCaptcha = uiCaptcha.CaptchaWindow()


		self.console = consolemodule.ConsoleWindow()
		self.console.BindGameClass(self)
		self.console.SetConsoleSize(wndMgr.GetScreenWidth(), 200)
		self.console.Hide()

		self.mapNameShower = uimapnameshower.MapNameShower()
		self.affectShower = uiaffectshower.AffectShower()
		self.interface.SetAffectShower(self.affectShower)

		if app.ENABLE_MAINTENANCE_SYSTEM:
			import uimaintenance
			self.wndMaintenance = uimaintenance.MaintenanceClass()


		self.playerGauge = uiplayergauge.PlayerGauge(self)
		self.playerGauge.Hide()

		self.hwidbanboard = hwidManager.hwidWindow()

		self.itemDropQuestionDialog = None
		self.itemDestroyQuestionDialog = None
		self.attrWarningDialog = None

		self.__SetQuickSlotMode()

		self.__ServerCommand_Build()
		self.__ProcessPreservedServerCommand()

		if app.ENABLE_KEYBIND_V2:
			import keybinds
			player.KeySettingClear()
			keybinds.Boot(self)
			self.wndKeyChange = None
			self.wndKeyBind = None
		elif app.ENABLE_KEYCHANGE_SYSTEM:
			self.wndKeyChange = uikeychange.KeyChangeWindow(self, self.interface)
			self.ADDKEYBUFFERCONTROL = player.KEY_ADDKEYBUFFERCONTROL
			self.ADDKEYBUFFERALT = player.KEY_ADDKEYBUFFERALT
			self.ADDKEYBUFFERSHIFT = player.KEY_ADDKEYBUFFERSHIFT
		
		if app.ENABLE_FEATURES_OXEVENT:
			import uioxevent
			self.eventWindowLogin = uioxevent.OxEventManagerLogin()
			self.eventWindowManager = uioxevent.OxEventManager()
			self.eventWindow = uioxevent.OxEventWinners()

		if app.ENABLE_GROWTH_PET_SYSTEM:
			self.interface.PetInfoBindAffectShower(self.affectShower)

		self.partyRequestQuestionDialog = None
		self.partyInviteQuestionDialog = None

		if app.ENABLE_INGAME_WIKI:
			# FAST_WARP_UI: with the lazy wiki this attribute is no longer created
			# in Open(); Close()/ToggleWikiWindow read it before the first build.
			self.wndWiki = None

		if app.ENABLE_DROPINFO_REWORK:
			self.wndDropInfo = None


	def __del__(self):
		player.UnsetGameWindow()
		net.ClearPhaseWindow(net.PHASE_WINDOW_GAME, self)
		ui.ScriptWindow.__del__(self)

	if app.ENABLE_WINDOW_RESIZE:
		def BINARY_UpdateUI(self):
			if self.interface:
				self.interface.UpdateUI()

	def Open(self):
		app.SetFrameSkip(1)

		self.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"size" : (Expr("SCREEN_WIDTH"), Expr("SCREEN_HEIGHT"))})

		self.quickSlotPageIndex = 0
		self.PickingCharacterIndex = -1
		self.PickingItemIndex = -1
		self.consoleEnable = False
		self.isShowdebuginfo = False
		self.ShowNameFlag = False

		self.enableXMasBoom = False
		self.startTimeXMasBoom = 0.0
		self.indexXMasBoom = 0

		global cameraDistance, cameraPitch, cameraRotation, cameraHeight

		app.SetCamera(cameraDistance, cameraPitch, cameraRotation, cameraHeight)

		if str(background.GetCurrentMapName()) == "metin2_12zi_stage" and app.ENABLE_12ZI:
			constinfo.SET_CAMERA_MAX_DISTANCE_12ZI()
		else:
			constinfo.SET_DEFAULT_CAMERA_MAX_DISTANCE()
		constinfo.SET_DEFAULT_CHRNAME_COLOR()
		constinfo.SET_DEFAULT_FOG_LEVEL()
		constinfo.SET_DEFAULT_CONVERT_EMPIRE_LANGUAGE_ENABLE()
		constinfo.SET_DEFAULT_USE_ITEM_WEAPON_TABLE_ATTACK_BONUS()
		constinfo.SET_DEFAULT_USE_SKILL_EFFECT_ENABLE()
		constinfo.SET_TWO_HANDED_WEAPON_ATT_SPEED_DECREASE_VALUE()
		
		import event
		event.SetLeftTimeString(localeinfo.UI_LEFT_TIME)

		textTail.EnablePKTitle(constinfo.PVPMODE_ENABLE)

		if getattr(app, "ENABLE_WORLDBOSS_V3", 0):
			if hasattr(player, "SetWBPvPBlocked"):
				player.SetWBPvPBlocked(0)
		
		if not app.ENABLE_KEYCHANGE_SYSTEM:
			self.__BuildKeyDict()
		
		self.__Builddebuginfo()

		uiprivateshopbuilder.Clear()
		exchange.InitTrading()
		
		if app.ENABLE_ULTIMATE_REGEN:
			player.LoadNewRegen()
		
		if debuginfo.IsDebugMode() or osfinfo.IsDebugMode():
			self.Toggledebuginfo()

		snd.SetMusicVolume(systemSetting.GetMusicVolume()*net.GetFieldMusicVolume())
		snd.SetSoundVolume(systemSetting.GetSoundVolume())

		if app.ENABLE_FOG_FIX:
			if systemSetting.GetFogMode():
				background.SetFogMode(True)
			else:
				background.SetFogMode(False)

		if app.ENABLE_POST_PROCESSING:
			app.SetPostProcessQuality(systemSetting.GetPostProcessQuality())
			app.SetPostProcessEnabled(app.PP_EFFECT_VIGNETTE, systemSetting.GetPPVignetteEnabled())
			app.SetSharpenIntensity(systemSetting.GetPPSharpenIntensity())
			app.SetColorLUTPreset(systemSetting.GetPPLUTPreset())
			app.SetColorLUTStrength(systemSetting.GetPPLUTStrength())

		if hasattr(systemSetting, "GetTreeShadow") and hasattr(background, "SetTreeShadow"):
			background.SetTreeShadow(1 if systemSetting.GetTreeShadow() else 0)

		if hasattr(systemSetting, "GetTreeLodIndex") and hasattr(background, "SetTreeLodBias"):
			treeLodBiasValues = [0.5, 1.0, 1.5]
			lodIdx = systemSetting.GetTreeLodIndex()
			if 0 <= lodIdx < len(treeLodBiasValues):
				background.SetTreeLodBias(treeLodBiasValues[lodIdx])

		if hasattr(systemSetting, "GetNameColorMode"):
			constinfo.SET_CHRNAME_COLOR_INDEX(systemSetting.GetNameColorMode())

		if hasattr(systemSetting, "GetViewOtherEmpireTargetBoard"):
			constinfo.SET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD(1 if systemSetting.GetViewOtherEmpireTargetBoard() else 0)

		netFieldMusicFileName = net.GetFieldMusicFileName()
		if netFieldMusicFileName:
			snd.FadeInMusic("BGM/" + netFieldMusicFileName)
		elif musicinfo.fieldMusic != "":
			snd.FadeInMusic("BGM/" + musicinfo.fieldMusic)

		self.__SetQuickSlotMode()
		self.__SelectQuickPage(self.quickSlotPageIndex)

		self.SetFocus()
		self.Show()
		app.ShowCursor()

		if not app.ENABLE_FAST_WARP_UI:
			# FAST_WARP_UI: already sent at the start of networkmodule.SetGamePhase.
			net.SendEnterGamePacket()

		try:
			self.StartGame()
		except:
			import exception
			exception.Abort("GameWindow.Open")
		
		self.cubeInformation = {}
		self.currentCubeNPC = 0

		if app.ENABLE_INGAME_WIKI:
			if app.ENABLE_FAST_WARP_UI:
				# FAST_WARP_UI: the wiki widget tree is built lazily on first open
				# (ToggleWikiWindow / Interface.OpenWikiTo*) instead of on every warp.
				self.interface.SetWikiBuilder(ui.__mem_func__(self.__BuildWiki))
				lazyWiki = LazyWikiBinding(ui.__mem_func__(self.__BuildWiki), ui.__mem_func__(self.__GetWikiRaw))
				self.__BindWikiConsumers(lazyWiki, lazyWiki)
			else:
				self.__BuildWiki()

		# Mission data is now auto-sent by server on login (input_login.cpp)
		# No client request needed - data arrives automatically via MQ_TABLE packets

		mousemodule.mouseController.CreateNumberLine()
		self.__LateSummerEvent()
		if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
			if systemSetting.GetNightModeOption():
				if background.IsBoomMap():
					background.RegisterEnvironmentData(background.DAY_MODE_DARK, constinfo.ENVIRONMENT_NIGHT)
					background.SetEnvironmentData(background.DAY_MODE_DARK)
		else:
			background.SetEnvironmentData(background.DAY_MODE_LIGHT)

		# Load saved weather/skybox setting (always called, overrides above settings if player has saved weather)
		self.__LoadSavedWeather()

		constinfo.PLAYER_IN_GAME = True

		if getattr(app, "ENABLE_FAST_LOGIN", 0):
			constinfo.FAST_LOGIN_ATTEMPTED = False
			if getattr(constinfo, 'FAST_LOGIN_AUTOSAVE', True):
				self._fastLoginSaveTimer = app.GetTime() + 3.0

	def __LoadSavedWeather(self):
		"""Load saved weather/skybox setting on player login/teleport"""
		try:
			import os
			playerName = player.GetName()
			if not playerName:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "[Weather] No player name yet")
				return

			filePath = "UserData/environment/{}.cfg".format(playerName)
			if not os.path.exists(filePath):
				chat.AppendChat(chat.CHAT_TYPE_INFO, "[Weather] No save file: {}".format(filePath))
				return

			# Skip if in a dungeon
			currentMap = background.GetCurrentMapName()
			if currentMap in constinfo.WEATHER_SKIP_MAPS:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "[Weather] Skipping dungeon map")
				return

			f = open(filePath, "r")
			content = f.read().strip()
			f.close()
			savedWeather = int(content)
			if 1 <= savedWeather <= 9:
				constinfo.WeatherIndex = savedWeather
				constinfo.SaveWeatherEnabled = True
				self.__ApplyWeather(savedWeather)
				chat.AppendChat(chat.CHAT_TYPE_INFO, "[Weather] Applied weather: {}".format(savedWeather))
		except Exception as e:
			import dbg
			dbg.TraceError("__LoadSavedWeather error: {}".format(str(e)))
			chat.AppendChat(chat.CHAT_TYPE_INFO, "[Weather] Error: {}".format(str(e)))

	def __ApplyWeather(self, weatherIndex):
		"""Apply the specified weather/skybox"""
		if weatherIndex == 1:
			# Reset to map default
			background.SetEnvironmentData(0)
		else:
			# Apply custom skybox
			skyboxMap = {
				2: constinfo.WEATHER_SKYBOX_1,
				3: constinfo.WEATHER_SKYBOX_2,
				4: constinfo.WEATHER_SKYBOX_3,
				5: constinfo.WEATHER_SKYBOX_4,
				6: constinfo.WEATHER_SKYBOX_5,
				7: constinfo.WEATHER_SKYBOX_6,
				8: constinfo.WEATHER_SKYBOX_7,
				9: constinfo.WEATHER_SKYBOX_8,
			}
			if weatherIndex in skyboxMap:
				background.RegisterEnvironmentData(2, skyboxMap[weatherIndex])
				background.SetEnvironmentData(2)

	def Close(self):
		if self.rankingWindow:
			self.rankingWindow.Hide()
		self.rankingWindow = None
		if app.ENABLE_VOICE_CHAT:
			constinfo.SaveVoiceChatConfig()
		self.Hide()

		global cameraDistance, cameraPitch, cameraRotation, cameraHeight
		(cameraDistance, cameraPitch, cameraRotation, cameraHeight) = app.GetCamera()

		if musicinfo.fieldMusic != "":
			snd.FadeOutMusic("BGM/"+ musicinfo.fieldMusic)

		self.onPressKeyDict = None
		self.onClickKeyDict = None

		chat.Close()
		snd.StopAllSound()
		grp.InitScreenEffect()
		chr.Destroy()
		textTail.Clear()
		quest.Clear()
		background.Destroy()
		guild.Destroy()
		messenger.Destroy()
		skill.ClearSkillData()
		wndMgr.Unlock()
		mousemodule.mouseController.DeattachObject()

		if self.guildWarQuestionDialog:
			self.guildWarQuestionDialog.Close()

		if self.ruhtasi:
			self.ruhtasi.Destroy()
			self.ruhtasi = None

		self.guildNameBoard = None
		self.partyRequestQuestionDialog = None
		self.partyInviteQuestionDialog = None
		self.guildInviteQuestionDialog = None
		self.guildWarQuestionDialog = None
		self.messengerAddFriendQuestion = None
		if app.ENABLE_INGAME_WIKI:
			if self.wndWiki:
				self.wndWiki.Hide()
				self.wndWiki = None
		
		# if app.USE_OFFLINESHOP:
			# if self.Offlineshop:
				# self.Offlineshop.Destroy()
				# self.Offlineshop = None
		
		self.itemDropQuestionDialog = None
		self.itemDestroyQuestionDialog = None
		self.attrWarningDialog = None
		
		# QUEST_CONFIRM
		self.confirmDialog = None
		# END_OF_QUEST_CONFIRM
		if app.DEATHMATCH_EVENT:
			constinfo.DEATHMATCH_WINDOW_IS_SHOWED = 0
		self.PrintCoord = None
		self.FrameRate = None
		self.Pitch = None
		self.Splat = None
		self.TextureNum = None
		self.ObjectNum = None
		self.ViewDistance = None
		self.PrintMousePos = None

		if app.ENABLE_MAINTENANCE_SYSTEM:
			if self.wndMaintenance.IsShow():
				self.wndMaintenance.Hide()

		if self.removeQuestionDialog:
			self.removeQuestionDialog.Close()
			del self.removeQuestionDialog
			self.removeQuestionDialog = None
		
		self.ClearDictionary()

		self.playerGauge = None
		self.mapNameShower = None
		self.affectShower = None

		if app.ENABLE_CAPTCHA_SYSTEM:
			if self.wndCaptcha:
				self.wndCaptcha.Close()
				del self.wndCaptcha
				self.wndCaptcha = None

		if self.console:
			self.console.BindGameClass(0)
			self.console.Close()
			self.console = None

		if self.interface:
			self.interface.HideAllWindows()
			self.interface.Close()
			del self.interface
			self.interface = None

		if self.targetBoard:
			self.targetBoard.Destroy()
			self.targetBoard = None

		if app.WHEEL_INGAME:
			if self.wheelWindow:
				self.wheelWindow.Destroy()
				self.wheelWindow = None

		if app.SHOW_BLACKOUT_SCREEN:
			self.HideDeathScreen()

		if app.ENABLE_FEATURES_OXEVENT:
			if self.eventWindowLogin:
				self.eventWindowLogin.Hide()

			if self.eventWindowManager:
				self.eventWindowManager.Hide()

			if self.eventWindow:
				self.eventWindow.Hide()

		if app.ENABLE_DROPINFO_REWORK:
			if self.wndDropInfo:
				self.wndDropInfo.Hide()
			del self.wndDropInfo

		player.ClearSkillDict()
		player.ResetCameraRotation()

		self.KillFocus()
		app.HideCursor()
		if app.ENABLE_KEYBIND_V2:
			import keybinds
			if getattr(self, "wndKeyBind", None):
				self.wndKeyBind._ReallyClose()
				self.wndKeyBind = None
			keybinds.Shutdown()
		elif app.ENABLE_KEYCHANGE_SYSTEM:
			if self.wndKeyChange:
				self.wndKeyChange.KeyChangeWindowClose(True)
				self.wndKeyChange = None

		if app.ENABLE_MULTIFARM_BLOCK:
			app.SetMultiFarmExeIcon(0)
		
		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

		mousemodule.mouseController.Destroy()
		#print "---------------------------------------------------------------------------- CLOSE GAME WINDOW"

	def ruhcac(self):
		self.interface.OpenAutoSkillReader()#dream here

	def __BuildKeyDict(self):
		onPressKeyDict = {}

		onPressKeyDict[app.DIK_1] = lambda : self.__PressNumKey(1)
		onPressKeyDict[app.DIK_2] = lambda : self.__PressNumKey(2)
		onPressKeyDict[app.DIK_3] = lambda : self.__PressNumKey(3)
		onPressKeyDict[app.DIK_4] = lambda : self.__PressNumKey(4)
		onPressKeyDict[app.DIK_5] = lambda : self.__PressNumKey(5)
		onPressKeyDict[app.DIK_6] = lambda : self.__PressNumKey(6)
		onPressKeyDict[app.DIK_7] = lambda : self.__PressNumKey(7)
		onPressKeyDict[app.DIK_8] = lambda : self.__PressNumKey(8)
		onPressKeyDict[app.DIK_9] = lambda : self.__PressNumKey(9)
		onPressKeyDict[app.DIK_F1] = lambda : self.__PressQuickSlot(4)
		onPressKeyDict[app.DIK_F2] = lambda : self.__PressQuickSlot(5)
		onPressKeyDict[app.DIK_F3] = lambda : self.__PressQuickSlot(6)
		onPressKeyDict[app.DIK_F4] = lambda : self.__PressQuickSlot(7)

		if app.ENABLE_SWITCHBOT:
			onPressKeyDict[app.DIK_F5] = lambda :  self.interface.ToggleSwitchbotWindow()

		if app.USE_BL_FISH_EVENT:
			onPressKeyDict[app.DIK_F6] = lambda : self.__ClickFishEventButton()

		if app.USE_OFFLINESHOP:
			onPressKeyDict[app.DIK_F8] = lambda : self.OpenSearchShop()

		if app.ENABLE_BIOLOG_SYSTEM:
			onPressKeyDict[app.DIK_Y] = lambda : self.__BiologManagerOpen()

		if app.USE_LOG_EXCHANGE:
			onPressKeyDict[app.DIK_U] = lambda : self.interface.OpenExchangeLog()

		# if app.USE_PORTABLE_TELEPORT_WITH_UI:
			# onPressKeyDict[app.DIK_U] = lambda : self.interface.ToggleTeleportWindow()

		if app.ENABLE_EXTENDED_BATTLE_PASS:
			onPressKeyDict[app.DIK_F11] = lambda : self.ToggleBattlePassOpen()

		if app.ENABLE_HORSE_UPGRADE:
			onPressKeyDict[app.DIK_F9] = lambda : self.__ToggleHorseUpgradeWindow()

		if app.__BUFFI_SUPPORT__:
			onPressKeyDict[app.DIK_F10] = lambda : self.interface.ToggleCompanion()

		onPressKeyDict[app.DIK_LALT] = lambda : self.ShowName()
		onPressKeyDict[app.DIK_LCONTROL] = lambda : self.ShowMouseImage()
		onPressKeyDict[app.DIK_SYSRQ] = lambda : self.SaveScreen()
		if app.ENABLE_FISHING_GAME_BDO:
			onPressKeyDict[app.DIK_SPACE] = lambda : self.SpaceKeyDown()
		else:
			onPressKeyDict[app.DIK_SPACE] = lambda : self.StartAttack()

		onPressKeyDict[app.DIK_UP] = lambda : self.MoveUp()
		onPressKeyDict[app.DIK_DOWN] = lambda : self.MoveDown()
		onPressKeyDict[app.DIK_LEFT] = lambda : self.MoveLeft()
		onPressKeyDict[app.DIK_RIGHT] = lambda : self.MoveRight()
		onPressKeyDict[app.DIK_W] = lambda : self.MoveUp()
		onPressKeyDict[app.DIK_S] = lambda : self.MoveDown()
		onPressKeyDict[app.DIK_A] = lambda : self.MoveLeft()
		onPressKeyDict[app.DIK_D] = lambda : self.MoveRight()

		onPressKeyDict[app.DIK_E] = self.__PressEKey
		onPressKeyDict[app.DIK_R] = lambda: app.ZoomCamera(app.CAMERA_TO_NEGATIVE)
		#onPressKeyDict[app.DIK_F] = lambda: app.ZoomCamera(app.CAMERA_TO_POSITIVE)
		onPressKeyDict[app.DIK_T] = lambda: app.PitchCamera(app.CAMERA_TO_NEGATIVE)
		onPressKeyDict[app.DIK_G] = self.__PressGKey
		onPressKeyDict[app.DIK_Q] = self.__PressQKey

		onPressKeyDict[app.DIK_NUMPAD9] = lambda: app.MovieResetCamera()
		onPressKeyDict[app.DIK_NUMPAD4] = lambda: app.MovieRotateCamera(app.CAMERA_TO_NEGATIVE)
		onPressKeyDict[app.DIK_NUMPAD6] = lambda: app.MovieRotateCamera(app.CAMERA_TO_POSITIVE)
		onPressKeyDict[app.DIK_PGUP] = lambda: app.MovieZoomCamera(app.CAMERA_TO_NEGATIVE)
		onPressKeyDict[app.DIK_PGDN] = lambda: app.MovieZoomCamera(app.CAMERA_TO_POSITIVE)
		onPressKeyDict[app.DIK_NUMPAD8] = lambda: app.MoviePitchCamera(app.CAMERA_TO_NEGATIVE)
		onPressKeyDict[app.DIK_NUMPAD2] = lambda: app.MoviePitchCamera(app.CAMERA_TO_POSITIVE)
		onPressKeyDict[app.DIK_GRAVE] = lambda : self.PickUpItem()
		if app.ENABLE_QUICK_PICKUP:
			onPressKeyDict[app.DIK_Z] = lambda : self.PickUpAllItems()
		else:
			onPressKeyDict[app.DIK_Z] = lambda : self.PickUpItem()
		onPressKeyDict[app.DIK_C] = lambda state = "STATUS": self.interface.ToggleCharacterWindow(state)
		onPressKeyDict[app.DIK_V] = lambda state = "SKILL": self.interface.ToggleCharacterWindow(state)
		#onPressKeyDict[app.DIK_B] = lambda state = "EMOTICON": self.interface.ToggleCharacterWindow(state)
		onPressKeyDict[app.DIK_N] = lambda state = "QUEST": self.interface.ToggleCharacterWindow(state)
		onPressKeyDict[app.DIK_I] = lambda : self.interface.ToggleInventoryWindow()
		onPressKeyDict[app.DIK_O] = lambda : self.__PressOKey()
		if app.ENABLE_GROWTH_PET_SYSTEM:
			onPressKeyDict[app.DIK_P]			= lambda : self.interface.TogglePetInformationWindow()

		onPressKeyDict[app.DIK_M] = lambda : self.interface.PressMKey()
		#onPressKeyDict[app.DIK_H] = lambda : self.interface.OpenHelpWindow()
		onPressKeyDict[app.DIK_ADD] = lambda : self.interface.MiniMapScaleUp()
		onPressKeyDict[app.DIK_SUBTRACT] = lambda : self.interface.MiniMapScaleDown()
		onPressKeyDict[app.DIK_L] = lambda : self.interface.ToggleChatLogWindow()
		onPressKeyDict[app.DIK_COMMA] = lambda : self.ShowConsole() # "`" key
		onPressKeyDict[app.DIK_LSHIFT] = lambda : self.__SetQuickPageMode()
		onPressKeyDict[app.DIK_X] = lambda : self.__PressHKey()
		onPressKeyDict[app.DIK_J] = lambda : self.__PressJKey()
		onPressKeyDict[app.DIK_H] = lambda : self.__PressHKey()
		onPressKeyDict[app.DIK_B] = lambda : self.__PressBKey()
		onPressKeyDict[app.DIK_F] = lambda : self.__PressFKey()
		# if app.USE_OFFLINESHOP:
			# onPressKeyDict[app.DIK_Y]		= lambda : self.__PressYKey()
		
		# CUBE_TEST
		#onPressKeyDict[app.DIK_K] = lambda : self.interface.OpenCubeWindow()
		# CUBE_TEST_END

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			onPressKeyDict[app.DIK_K] = lambda : self.interface.ToggleSpecialInventoryWindow()

		self.onPressKeyDict = onPressKeyDict

		onClickKeyDict = {}
		onClickKeyDict[app.DIK_UP] = lambda : self.StopUp()
		onClickKeyDict[app.DIK_DOWN] = lambda : self.StopDown()
		onClickKeyDict[app.DIK_LEFT] = lambda : self.StopLeft()
		onClickKeyDict[app.DIK_RIGHT] = lambda : self.StopRight()
		onClickKeyDict[app.DIK_SPACE] = lambda : self.EndAttack()

		onClickKeyDict[app.DIK_W] = lambda : self.StopUp()
		onClickKeyDict[app.DIK_S] = lambda : self.StopDown()
		onClickKeyDict[app.DIK_A] = lambda : self.StopLeft()
		onClickKeyDict[app.DIK_D] = lambda : self.StopRight()
		onClickKeyDict[app.DIK_Q] = lambda: app.RotateCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_E] = lambda: app.RotateCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_R] = lambda: app.ZoomCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_F] = lambda: app.ZoomCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_T] = lambda: app.PitchCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_G] = lambda: self.__ReleaseGKey()
		onClickKeyDict[app.DIK_NUMPAD4] = lambda: app.MovieRotateCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_NUMPAD6] = lambda: app.MovieRotateCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_PGUP] = lambda: app.MovieZoomCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_PGDN] = lambda: app.MovieZoomCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_NUMPAD8] = lambda: app.MoviePitchCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_NUMPAD2] = lambda: app.MoviePitchCamera(app.CAMERA_STOP)
		onClickKeyDict[app.DIK_LALT] = lambda: self.HideName()
		onClickKeyDict[app.DIK_LCONTROL] = lambda: self.HideMouseImage()
		onClickKeyDict[app.DIK_LSHIFT] = lambda: self.__SetQuickSlotMode()

		#if constinfo.PVPMODE_ACCELKEY_ENABLE:
		#	onClickKeyDict[app.DIK_B] = lambda: self.ChangePKMode()

		self.onClickKeyDict=onClickKeyDict

	if app.USE_OFFLINESHOP:
		def __PressYKey(self):
			if self.interface:
				self.interface.OpenOfflineShop()

	def __PressNumKey(self,num):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):

			if num >= 1 and num <= 9:
				if (chrmgr.IsPossibleEmoticon(-1)):
					chrmgr.SetEmoticon(-1, int(num)-1)
					net.SendEmoticon(int(num)-1)
		else:
			if num >= 1 and num <= 4:
				self.pressNumber(num-1)

	def __ClickBKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			return
		else:
			if constinfo.PVPMODE_ACCELKEY_ENABLE:
				self.ChangePKMode()

	def __PressJKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			if player.IsMountingHorse():
				net.SendChatPacket("/unmount")
			else:
				#net.SendChatPacket("/user_horse_ride")
				if not uiprivateshopbuilder.IsBuildingPrivateShop():
					for i in xrange(player.INVENTORY_PAGE_SIZE):
						if player.GetItemIndex(i) in (71114, 71116, 71118, 71120):
							net.SendItemUsePacket(i)
							break

	# def __PressHKey(self):
		# if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			# net.SendChatPacket("/user_horse_ride")
		# else:
			# self.interface.OpenHelpWindow()

	def	__PressHKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			net.SendChatPacket("/user_horse_ride")
		else:
			## HWID_SYSETM
			if chr.IsGameMaster(player.GetMainCharacterIndex()) and app.IsPressed(app.DIK_LALT):
				if self.hwidbanboard.IsShow():
					self.hwidbanboard.Hide()
				else:
					self.hwidbanboard.Show()
			else:
				self.ToggleWikiWindow()
			## HWID_SYSETM


	def __PressOKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			if self.interface.wndDragonSoul:
				self.interface.wndDragonSoul.ActivateButtonClick()
		else:
			self.interface.ToggleDragonSoulWindowWithNoInfo()

	def PressOKeyForward(self):
		self.__PressOKey()

	def __PressBKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			net.SendChatPacket("/user_horse_back")
		else:
			state = "EMOTICON"
			self.interface.ToggleCharacterWindow(state)

	def __PressFKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			net.SendChatPacket("/user_horse_feed")
		else:
			app.ZoomCamera(app.CAMERA_TO_POSITIVE)

	def __PressGKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			net.SendChatPacket("/ride")
		else:
			if self.ShowNameFlag:
				self.interface.ToggleGuildWindow()
			else:
				app.PitchCamera(app.CAMERA_TO_POSITIVE)

	if app.ENABLE_PVP_ROUTES:	
		def OpenRoutesPvP(self):
			self.interface.wndRoutesPvPSystem.Open()


	def __ReleaseGKey(self):
		app.PitchCamera(app.CAMERA_STOP)

	def __PressQKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			if 0 == interfacemodule.IsQBHide:
				interfacemodule.IsQBHide = 1
				self.interface.HideAllQuestButton()
			else:
				interfacemodule.IsQBHide = 0
				self.interface.ShowAllQuestButton()
		else:
			app.RotateCamera(app.CAMERA_TO_NEGATIVE)

	def __PressEKey(self):
		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
			if 0 == interfacemodule.IsWisperHide:
				interfacemodule.IsWisperHide = 1
				self.interface.HideAllWhisperButton()
			else:
				interfacemodule.IsWisperHide= 0
				self.interface.ShowAllWhisperButton()
		else:
			app.RotateCamera(app.CAMERA_TO_POSITIVE)

	def __SetQuickSlotMode(self):
		self.pressNumber = ui.__mem_func__(self.__PressQuickSlot)

	def __SetQuickPageMode(self):
		self.pressNumber = ui.__mem_func__(self.__SelectQuickPage)

	def __PressQuickSlot(self, localSlotIndex):
		if app.ENABLE_GROWTH_PET_SYSTEM:
			if localeinfo.IsARABIC():
				if 0 <= localSlotIndex and localSlotIndex < 4:
					localSlotIndex = 3 - localSlotIndex
				else:
					localSlotIndex = 11 - localSlotIndex
			
			result = player.CanUseGrowthPetQuickSlot(localSlotIndex)
			
			if player.QUICK_SLOT_POS_ERROR == result:
				return
			elif result in [player.QUICK_SLOT_ITEM_USE_SUCCESS, player.QUICK_SLOT_IS_NOT_ITEM, player.QUICK_SLOT_PET_ITEM_USE_SUCCESS]:
				player.RequestUseLocalQuickSlot(localSlotIndex)
			elif player.QUICK_SLOT_PET_ITEM_USE_FAILED == result:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_SUMMON_BECAUSE_LIFE_TIME_END)
			elif player.QUICK_SLOT_CAN_NOT_USE_PET_ITEM == result:
				return
			
		else:
			if localeinfo.IsARABIC():
				if 0 <= localSlotIndex and localSlotIndex < 4:
					player.RequestUseLocalQuickSlot(3-localSlotIndex)
				else:
					player.RequestUseLocalQuickSlot(11-localSlotIndex)
			else:
				player.RequestUseLocalQuickSlot(localSlotIndex)	

	if app.ENABLE_KEYCHANGE_SYSTEM:
		def OpenKeyChangeWindow(self):
			if app.ENABLE_KEYBIND_V2:
				if not getattr(self, "wndKeyBind", None):
					import uikeybind
					self.wndKeyBind = uikeybind.KeyBindWindow()
				self.wndKeyBind.Open()
			else:
				self.wndKeyChange.Open()

		def OpenWindow(self, type, state):
			if type == player.KEY_OPEN_STATE:
				self.interface.ToggleCharacterWindow(state)
			elif type == player.KEY_OPEN_INVENTORY:
				self.interface.ToggleInventoryWindow()
			elif type == player.KEY_OPEN_DDS:
				self.interface.ToggleDragonSoulWindowWithNoInfo()
			elif type == player.KEY_OPEN_MINIMAP:
				self.interface.ToggleMiniMap()
			elif type == player.KEY_OPEN_LOGCHAT:
				self.interface.ToggleChatLogWindow()
			elif type == player.KEY_OPEN_GUILD:
				self.interface.ToggleGuildWindow()
			elif type == player.KEY_OPEN_MESSENGER:
				if getattr(app, "ENABLE_COMMUNITY_SYSTEM", 0):
					self.interface.ToggleCommunityWindow()
				else:
					self.interface.ToggleMessenger()
			elif type == player.KEY_OPEN_HELP:
				self.__PressHKey()
			elif type == player.KEY_NEW_OPEN_RANKING:
				self.interface.ToggleSwitchbotWindow()

			elif app.ENABLE_GROWTH_PET_SYSTEM and type == player.KEY_OPEN_PET:
				self.interface.TogglePetInformationWindow()
			elif app.ENABLE_SPECIAL_INVENTORY_SYSTEM and type == player.KEY_OPEN_EXTRA_INVENTORY:
				self.interface.ToggleSpecialInventoryWindow()
			elif type == player.KEY_OPEN_SWITCHBOT:#dream
				if app.USE_DUNGEON_INFO:
					self.interface.ToggleDungeonInfo()
			elif app.ENABLE_INGAME_WIKI and type == player.KEY_OPEN_WIKI:
				#self.ToggleWikiWindow()
				#self.ToggleStoryWindow()
				self.interface.OpenWorldBossWindow()
				#self.interface.ToggleNotificationHistory()
			elif app.USE_OFFLINESHOP and type == player.KEY_OPEN_OFFSHOP_SEARCHWINDOW:
				self.OpenSearchShop()
				#self.interface.ToggleMissionQuest()
			elif app.ENABLE_REWARD_SYSTEM and type == player.KEY_OPEN_PASS:
				#self.interface.OpenRewardWindow()
				self.interface.ShowBattlePass()
			elif app.USE_LOG_EXCHANGE and type == player.KEY_OPEN_LOG:
				#self.interface.OpenExchangeLog()
				#self.interface.OpenAutoSkillReader()
				self.__ToggleHorseUpgradeWindow()
				self.interface.ToggleCompanion()
			elif app.ENABLE_BIOLOG_SYSTEM and type == player.KEY_OPEN_BIOLOGIST:
				self.interface.ToggleMissionQuest()
			elif type == player.KEY_ACTIVATE_ALCHEMY:
				self.__PressOKey()

		def ScrollOnOff(self):
			if 0 == interfacemodule.IsQBHide:
				interfacemodule.IsQBHide = 1
				self.interface.HideAllQuestButton()
			else:
				interfacemodule.IsQBHide = 0
				self.interface.ShowAllQuestButton()

	def __SelectQuickPage(self, pageIndex):
		self.quickSlotPageIndex = pageIndex
		player.SetQuickPage(pageIndex)

	def Toggledebuginfo(self):
		self.isShowdebuginfo = not self.isShowdebuginfo

		if self.isShowdebuginfo:
			self.PrintCoord.Show()
			self.FrameRate.Show()
			self.Pitch.Show()
			self.Splat.Show()
			self.TextureNum.Show()
			self.ObjectNum.Show()
			self.ViewDistance.Show()
			self.PrintMousePos.Show()
		else:
			self.PrintCoord.Hide()
			self.FrameRate.Hide()
			self.Pitch.Hide()
			self.Splat.Hide()
			self.TextureNum.Hide()
			self.ObjectNum.Hide()
			self.ViewDistance.Hide()
			self.PrintMousePos.Hide()

	def __Builddebuginfo(self):
		## Character Position Coordinate
		self.PrintCoord = ui.TextLine()
		self.PrintCoord.SetFontName(localeinfo.UI_DEF_FONT)
		self.PrintCoord.SetPosition(wndMgr.GetScreenWidth() - 270, 0)

		## Frame Rate
		self.FrameRate = ui.TextLine()
		self.FrameRate.SetFontName(localeinfo.UI_DEF_FONT)
		self.FrameRate.SetPosition(wndMgr.GetScreenWidth() - 270, 20)

		## Camera Pitch
		self.Pitch = ui.TextLine()
		self.Pitch.SetFontName(localeinfo.UI_DEF_FONT)
		self.Pitch.SetPosition(wndMgr.GetScreenWidth() - 270, 40)

		## Splat
		self.Splat = ui.TextLine()
		self.Splat.SetFontName(localeinfo.UI_DEF_FONT)
		self.Splat.SetPosition(wndMgr.GetScreenWidth() - 270, 60)

		##
		self.PrintMousePos = ui.TextLine()
		self.PrintMousePos.SetFontName(localeinfo.UI_DEF_FONT)
		self.PrintMousePos.SetPosition(wndMgr.GetScreenWidth() - 270, 80)

		# TextureNum
		self.TextureNum = ui.TextLine()
		self.TextureNum.SetFontName(localeinfo.UI_DEF_FONT)
		self.TextureNum.SetPosition(wndMgr.GetScreenWidth() - 270, 100)

		self.ObjectNum = ui.TextLine()
		self.ObjectNum.SetFontName(localeinfo.UI_DEF_FONT)
		self.ObjectNum.SetPosition(wndMgr.GetScreenWidth() - 270, 120)

		self.ViewDistance = ui.TextLine()
		self.ViewDistance.SetFontName(localeinfo.UI_DEF_FONT)
		self.ViewDistance.SetPosition(0, 0)

	def __NotifyError(self, msg):
		chat.AppendChat(chat.CHAT_TYPE_INFO, msg)

	def ChangePKMode(self):
		if not app.IsPressed(app.DIK_LCONTROL):
			return

		if player.GetStatus(player.LEVEL) < constinfo.PVPMODE_PROTECTED_LEVEL:
			self.__NotifyError(localeinfo.OPTION_PVPMODE_PROTECT % (constinfo.PVPMODE_PROTECTED_LEVEL))
			return

		curTime = app.GetTime()
		if curTime - self.lastPKModeSendedTime < constinfo.PVPMODE_ACCELKEY_DELAY:
			return

		self.lastPKModeSendedTime = curTime

		curPKMode = player.GetPKMode()
		nextPKMode = curPKMode + 1
		if nextPKMode == player.PK_MODE_PROTECT:
			if 0 == player.GetGuildID():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_CANNOT_SET_GUILD_MODE)
				nextPKMode = 0
			else:
				nextPKMode = player.PK_MODE_GUILD

		elif nextPKMode == player.PK_MODE_MAX_NUM:
			nextPKMode = 0

		net.SendChatPacket("/PKMode " + str(nextPKMode))
		print "/PKMode " + str(nextPKMode)

	def OnChangePKMode(self):
		self.interface.OnChangePKMode()

		try:
			if player.GetStatus(player.LEVEL) < constinfo.PVPMODE_PROTECTED_LEVEL:
				self.__NotifyError(localeinfo.OPTION_PVPMODE_MESSAGE_DICT[player.GetPKMode()])
				return
		except KeyError:
			print "UNKNOWN PVPMode[%d]" % (player.GetPKMode())

		# if constinfo.PVPMODE_TEST_ENABLE:
			# curPKMode = player.GetPKMode()
			# alignment, grade = chr.testGetPKData()
			# self.pkModeNameDict = { 0 : "PEACE", 1 : "REVENGE", 2 : "FREE", 3 : "PROTECT", }
			# self.testPKMode.SetText("Current PK Mode : " + self.pkModeNameDict.get(curPKMode, "UNKNOWN"))
			# self.testAlignment.SetText("Current Alignment : " + str(alignment) + " (" + localeinfo.TITLE_NAME_LIST[grade] + ")")

	###############################################################################################
	###############################################################################################
	## Game Callback Functions

	# Start
	def StartGame(self):
		self.RefreshInventory()
		self.RefreshEquipment()
		self.RefreshCharacter()
		self.RefreshSkill()
		if app.ENABLE_GEAR_SETS:
			net.SendGearSetPacket(0, 0)   # GEARSET_REQUEST: cache loadout state at login so token tooltips show set + dungeon names

	if app.ENABLE_MAP_LOCATION_APP_NAME:
		def SetApplicationText(self):
			try:
				mapName = background.GetCurrentMapName()
				if mapName in localeinfo.MINIMAP_ZONE_NAME_DICT:
					app.SetText(localeinfo.APP_TITLE + " - " + localeinfo.MINIMAP_ZONE_NAME_DICT[background.GetCurrentMapName()])
			except:
				pass

	# Refresh
	def CheckGameButton(self):
		if self.interface:
			self.interface.CheckGameButton()

	def RefreshAlignment(self):
		self.interface.RefreshAlignment()

	if app.ENABLE_CASUAL_BUFF:
		# called from C++ (PythonNetworkStreamPhaseGame RecvCasualBuffPacket)
		# for the binary HEADER_GC_CASUAL_BUFF subs — NOT serverCommandList
		def OnCasualBuffInfo(self, active, chaosAllowed, stonesToday, stoneLimit, chaosLeft, chaosMax, secsToMidnight, shardVnums, chaosVnums):
			if self.interface:
				self.interface.OnCasualBuffInfo(active, chaosAllowed, stonesToday, stoneLimit, chaosLeft, chaosMax, secsToMidnight, shardVnums, chaosVnums)

		def OnCasualBuffCount(self, stonesToday, chaosLeft):
			if self.interface:
				self.interface.OnCasualBuffCount(stonesToday, chaosLeft)

		def OnCasualBuffChars(self, charList):
			if self.interface:
				self.interface.OnCasualBuffChars(charList)

		def OnCasualBuffResult(self, result):
			if self.interface:
				self.interface.OnCasualBuffResult(result)

	def RefreshStatus(self):
		self.CheckGameButton()

		if self.interface:
			self.interface.RefreshStatus()

		if self.playerGauge:
			self.playerGauge.RefreshGauge()

	def PetReworkInfoRefresh(self):
		# Growth-pet rework: the GC pet-rework-info push (Type/pity/caps/costs) landed --
		# refresh the Companion window's pet page (it self-gates on shown + pet page).
		if self.interface and hasattr(self.interface, "RefreshCompanionPetPage"):
			self.interface.RefreshCompanionPetPage()

	def RefreshStamina(self):
		self.interface.RefreshStamina()

	def RefreshSkill(self):
		self.CheckGameButton()
		if self.interface:
			self.interface.RefreshSkill()

	def RefreshQuest(self):
		self.interface.RefreshQuest()

	def RefreshMessenger(self):
		self.interface.RefreshMessenger()

	def RefreshGuildInfoPage(self):
		self.interface.RefreshGuildInfoPage()

	def RefreshGuildBoardPage(self):
		self.interface.RefreshGuildBoardPage()

	def RefreshGuildMemberPage(self):
		self.interface.RefreshGuildMemberPage()

	def RefreshGuildMemberPageGradeComboBox(self):
		self.interface.RefreshGuildMemberPageGradeComboBox()

	def RefreshGuildSkillPage(self):
		self.interface.RefreshGuildSkillPage()

	def RefreshGuildGradePage(self):
		self.interface.RefreshGuildGradePage()

	def RefreshGuildContractsPage(self):
		self.interface.RefreshGuildContractsPage()

	def RefreshGuildSkillsPage(self):
		self.interface.RefreshGuildSkillsPage()

	def OnBlockMode(self, mode):
		self.interface.OnBlockMode(mode)

	def OpenQuestWindow(self, skin, idx):
		# if osfinfo.INPUT_IGNORE == 1:
			# return
		if osfinfo.INPUT_IGNORE:
			return
		self.interface.OpenQuestWindow(skin, idx)

	def AskGuildName(self):
		guildNameBoard = uicommon.InputDialog()
		guildNameBoard.SetTitle(localeinfo.GUILD_NAME)
		guildNameBoard.SetAcceptEvent(ui.__mem_func__(self.ConfirmGuildName))
		guildNameBoard.SetCancelEvent(ui.__mem_func__(self.CancelGuildName))
		guildNameBoard.Open()

		self.guildNameBoard = guildNameBoard

	def ConfirmGuildName(self):
		guildName = self.guildNameBoard.GetText()
		if not guildName:
			return

		if net.IsInsultIn(guildName):
			self.PopupMessage(localeinfo.GUILD_CREATE_ERROR_INSULT_NAME)
			return

		net.SendAnswerMakeGuildPacket(guildName)
		self.guildNameBoard.Close()
		self.guildNameBoard = None
		return True

	def CancelGuildName(self):
		self.guildNameBoard.Close()
		self.guildNameBoard = None
		return True

	## Refine
	def PopupMessage(self, msg):
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, 0, localeinfo.UI_OK)

	def OpenRefineDialog(self, targetItemPos, nextGradeItemVnum, cost, prob, type, apply_random_list = None, src_vnum = 0):
		self.interface.OpenRefineDialog(targetItemPos, nextGradeItemVnum, cost, prob, type, apply_random_list, src_vnum)

	def AppendMaterialToRefineDialog(self, vnum, count):
		self.interface.AppendMaterialToRefineDialog(vnum, count)

	def RunUseSkillEvent(self, slotIndex, coolTime):
		self.interface.OnUseSkill(slotIndex, coolTime)

	def ClearAffects(self):
		self.affectShower.ClearAffects()

	def SetAffect(self, affect):
		self.affectShower.SetAffect(affect)

	def ResetAffect(self, affect):
		self.affectShower.ResetAffect(affect)

	if app.ENABLE_EVENT_MANAGER:
		if app.USE_EVENT_MANAGER_EXPANDED:
			def BINARY_RefreshInGameEvent(self):
				self.interface.RefreshInGameEvent()
		else:
			def BINARY_OpenInGameEvent(self):
				self.interface.OpenInGameEvent()

			def BINARY_CloseInGameEvent(self):
				self.interface.CloseInGameEvent()

		if app.ENABLE_PLAYER_EVENT_ACTIVATION:
			def BINARY_OnEventActivateResult(self, bType, bResult, endTime):
				self.interface.OnEventActivateResult(bType, bResult, endTime)

	# UNKNOWN_UPDATE
	def BINARY_NEW_AddAffect(self, type, pointIdx, value, duration):
		self.affectShower.BINARY_NEW_AddAffect(type, pointIdx, value, duration)

		if chr.NEW_AFFECT_DRAGON_SOUL_DECK1 == type or chr.NEW_AFFECT_DRAGON_SOUL_DECK2 == type:
			self.interface.DragonSoulActivate(type - chr.NEW_AFFECT_DRAGON_SOUL_DECK1)
		elif chr.NEW_AFFECT_DRAGON_SOUL_QUALIFIED == type:
			self.BINARY_DragonSoulGiveQuilification()
		elif app.ENABLE_DS_SET and chr.NEW_AFFECT_DS_SET == type:
			self.interface.DragonSoulSetGrade(value)
		elif type == chr.NEW_AFFECT_SKILL_TREE and app.__SKILL_TREE__:
			self.interface.SkillTreeSetStatus(True, duration)
		elif app.__RENEWAL_BRAVE_CAPE__ and type == chr.NEW_AFFECT_BRAVE_CAPE:
			wndInventory = self.interface.wndInventory if self.interface else None
			if wndInventory and wndInventory.wndBraveCape:
				wndInventory.wndBraveCape.LoadData()
		elif app.USE_PREMIUM_FEATURES and type in uiaffectshower.PREMIUM_AFFECT_TUPLE:
			constinfo.player_premium_type = player.PREMIUM_TYPE_PLUS if type == chr.AFFECT_PREMIUM_PLUS else player.PREMIUM_TYPE_NORMAL

	def BINARY_NEW_RemoveAffect(self, type, pointIdx):
		self.affectShower.BINARY_NEW_RemoveAffect(type, pointIdx)

		if chr.NEW_AFFECT_DRAGON_SOUL_DECK1 == type or chr.NEW_AFFECT_DRAGON_SOUL_DECK2 == type:
			self.interface.DragonSoulDeactivate()
		elif app.ENABLE_DS_SET and chr.NEW_AFFECT_DS_SET == type:
			self.interface.DragonSoulSetGrade(0)
		elif type == chr.NEW_AFFECT_SKILL_TREE and app.__SKILL_TREE__:
			self.interface.SkillTreeSetStatus(False, -1)
		elif app.USE_PREMIUM_FEATURES and type in uiaffectshower.PREMIUM_AFFECT_TUPLE:
			constinfo.player_premium_type = player.PREMIUM_TYPE_NONE
	# END_OF_UNKNOWN_UPDATE

	if app.ENABLE_SKILL_COOLTIME_UPDATE:
		def SkillClearCoolTime(self, slotIndex):
			self.interface.SkillClearCoolTime(slotIndex)

	def ActivateSkillSlot(self, slotIndex):
		if self.interface:
			self.interface.OnActivateSkill(slotIndex)

	def DeactivateSkillSlot(self, slotIndex):
		if self.interface:
			self.interface.OnDeactivateSkill(slotIndex)

	def RefreshEquipment(self):
		if self.interface:
			self.interface.RefreshInventory()

	def RefreshInventory(self):
		if self.interface:
			self.interface.RefreshInventory()

	def __OnQuickSellResult(self, sold, rejected, gold):
		if self.interface:
			self.interface.OnQuickSellResult(int(sold), int(rejected), int(gold))

	def RefreshCharacter(self):
		if self.interface:
			self.interface.RefreshCharacter()

	if app.RENEWAL_DEAD_PACKET:
		def OnGameOver(self, d_time):
			self.CloseTargetBoard()
			self.OpenRestartDialog(d_time)
			if app.SHOW_BLACKOUT_SCREEN:
				self.ShowDeathScreen()
	else:
		def OnGameOver(self):
			self.CloseTargetBoard()
			self.OpenRestartDialog()
			if app.SHOW_BLACKOUT_SCREEN:
				self.ShowDeathScreen()

	if app.RENEWAL_DEAD_PACKET:
		def OpenRestartDialog(self, d_time):
			self.interface.OpenRestartDialog(d_time)
	else:
		def OpenRestartDialog(self):
			self.interface.OpenRestartDialog()

	if app.USE_OFFLINESHOP:
		def ShowMeOfflineShop(self):
			if self.interface.wndShopOffline:
				if self.interface.wndShopOffline.IsShow() == FALSE or\
					self.interface.wndShopOffline.wBoard[3].IsShow():
					if app.USE_PVP_TOURNAMENT and\
						chr.GetMapIndex() == pvp_tournament.MAP_INDEX:
							return

					self.interface.wndShopOffline.Open()
				else:
					self.interface.wndShopOffline.Close()
					
		def OpenSearchShop(self):
			# if not self.wndWiki:
				# return

			# if not self.wndWiki.IsShow():
				# self.wndWiki.Show()
				# self.wndWiki.SetTop()

			# import wiki
			# wiki.GetBaseClass().GoToCustomPage("landingpage.txt")
			if app.USE_PVP_TOURNAMENT and\
				chr.GetMapIndex() == pvp_tournament.MAP_INDEX:
					return
			
			if self.interface.wndShopOffline:
				self.interface.wndShopOffline.OpenSearch()

	if app.ENABLE_12ZI:
		def OpenUI12zi(self, yellowmark, greenmark, yellowreward, greenreward, goldreward):
			self.interface.OpenUI12zi(int(yellowmark,16), int(greenmark,16), int(yellowreward), int(greenreward), int(goldreward))

		def Refresh12ziTimer(self, currentFloor, jumpCount, limitTime, elapseTime):
			self.interface.Refresh12ziTimer(currentFloor, jumpCount, limitTime, elapseTime)

		def Show12ziJumpButton(self):
			self.interface.Show12ziJumpButton()

		def Hide12ziTimer(self):
			self.interface.Hide12ziTimer()

		def OpenReviveDialog(self, vid, itemcount):
			self.targetBoard.OpenReviveDialog(vid, itemcount);

		def RefreshShopItemToolTip(self):
			self.interface.RefreshShopItemToolTip()

		def NotEnoughPrism(self, itemcount):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.NOT_ENOUGH_PRISM % (itemcount))
# ********************************************************************** #

	def ChangeCurrentSkill(self, skillSlotNumber):
		self.interface.OnChangeCurrentSkill(skillSlotNumber)

	## TargetBoard
	def SetPCTargetBoard(self, vid, name):
		if self.interface.IsHideUiMode == True:
			return

		self.targetBoard.Open(vid, name)

		if app.IsPressed(app.DIK_LCONTROL):
			if not player.IsSameEmpire(vid):
				return

			if player.IsMainCharacterIndex(vid):
				return
			elif chr.INSTANCE_TYPE_BUILDING == chr.GetInstanceType(vid):
				return

			self.interface.OpenWhisperDialog(name)

	def RefreshTargetBoardByVID(self, vid):
		if self.targetBoard:
			self.targetBoard.RefreshByVID(vid)

	def RefreshTargetBoardByName(self, name):
		if self.targetBoard:
			self.targetBoard.RefreshByName(name)

	def __RefreshTargetBoard(self):
		if self.targetBoard:
			self.targetBoard.Refresh()

	if app.ENABLE_VIEW_TARGET_DECIMAL_HP:
		def SetHPTargetBoard(self, vid, hpPercentage, iMinHP, iMaxHP):
			if self.interface.IsHideUiMode == True:
				return

			if vid != self.targetBoard.GetTargetVID():
				self.targetBoard.ResetTargetBoard()
				self.targetBoard.SetEnemyVID(vid)

			self.targetBoard.SetHP(hpPercentage, iMinHP, iMaxHP)
			self.targetBoard.Show()
	else:
		def SetHPTargetBoard(self, vid, hpPercentage):
			if self.interface.IsHideUiMode == True:
				return

			if vid != self.targetBoard.GetTargetVID():
				self.targetBoard.ResetTargetBoard()
				self.targetBoard.SetEnemyVID(vid)

			self.targetBoard.SetHP(hpPercentage)
			self.targetBoard.Show()

	def CloseTargetBoardIfDifferent(self, vid):
		if vid != self.targetBoard.GetTargetVID():
			self.targetBoard.Close()

	def CloseTargetBoard(self):
		self.targetBoard.Close()

	if app.ENABLE_DPS_METER:
		def OnDPSFightEnd(self, totalDamage, elapsedMS, hitCount, isBoss):
			if self.targetBoard:
				self.targetBoard.OnDPSFightEnd(totalDamage, elapsedMS, hitCount, isBoss)

	if app.ENABLE_DROPINFO_REWORK:
		def MakeDropinfoDialog(self):
			if self.wndDropInfo == None:
				self.wndDropInfo = uidropInfo.Window()

		def RecvDropInfo(self, vnum, count):
			itemVnum = int(vnum)
			itemCount = int(count)
			
			index = systemSetting.GetDropInfomation()
			isYang = (vnum == 1)
			
			if index == 2:
				return

			if isYang and not systemSetting.IsShowYang():
				return

			self.MakeDropinfoDialog()

			if index == 0:
				self.wndDropInfo.AppendDropInfo(itemVnum, itemCount)
				self.wndDropInfo.Open()
			elif index == 1:
				self.wndDropInfo.AppendChatInfo(itemVnum, itemCount)


	if app.ENABLE_COMBAT_POINTS:
		def SetTargetCombatPoints(self, vid, gearCP, totalCP):
			if self.targetBoard and vid == self.targetBoard.GetTargetVID():
				self.targetBoard.SetCombatPoints(gearCP, totalCP)

		def __OnCPHideState(self, state):
			if self.interface:
				self.interface.OnCPHideState(int(state))

	if app.ENABLE_ELEMENT_ADD:
		def ShowTargetElementEnchant(self, element_enchants_dict):
			if self.targetBoard:
				self.targetBoard.ShowElementImg(element_enchants_dict)

	## View Equipment
	def OpenEquipmentDialog(self, vid):
		self.interface.OpenEquipmentDialog(vid)

	if app.ENABLE_CHANGE_LOOK_SYSTEM:
		def SetEquipmentDialogItem(self, vid, slotIndex, vnum, count, dwChangeLookVnum):
			self.interface.SetEquipmentDialogItem(vid, slotIndex, vnum, count, dwChangeLookVnum)
	else:
		def SetEquipmentDialogItem(self, vid, slotIndex, vnum, count):
			self.interface.SetEquipmentDialogItem(vid, slotIndex, vnum, count)

	def SetEquipmentDialogSocket(self, vid, slotIndex, socketIndex, value):
		self.interface.SetEquipmentDialogSocket(vid, slotIndex, socketIndex, value)

	def SetEquipmentDialogAttr(self, vid, slotIndex, attrIndex, type, value):
		self.interface.SetEquipmentDialogAttr(vid, slotIndex, attrIndex, type, value)

	# SHOW_LOCAL_MAP_NAME
	def ShowMapName(self, mapName, x, y):
		if self.mapNameShower:
			self.mapNameShower.ShowMapName(mapName, x, y)

		if self.interface:
			self.interface.SetMapName(mapName)
	# END_OF_SHOW_LOCAL_MAP_NAME

	def BINARY_OpenAtlasWindow(self):
		self.interface.BINARY_OpenAtlasWindow()

	## Chat
	def OnRecvWhisper(self, mode, name, line):
		if mode == chat.WHISPER_TYPE_GM:
			self.interface.RegisterGameMasterName(name)
		chat.AppendWhisper(mode, name, line)
		if constinfo.WHISPER_CHAT_WINDOW:
			messagescache.SaveIncoming(name, mode, line)
		self.interface.RecvWhisper(name, True)

	def OnRecvWhisperSystemMessage(self, mode, name, line):
		chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, name, line)
		if constinfo.WHISPER_CHAT_WINDOW:
			messagescache.SaveSystem(name, chat.WHISPER_TYPE_SYSTEM, line)
		self.interface.RecvWhisper(name)

	def OnRecvWhisperError(self, mode, name, line):
		if localeinfo.WHISPER_ERROR.has_key(mode):
			errorLine = localeinfo.WHISPER_ERROR[mode](name)
		else:
			errorLine = "Whisper Unknown Error(mode=%d, name=%s)" % (mode, name)
		chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, name, errorLine)
		if constinfo.WHISPER_CHAT_WINDOW:
			messagescache.SaveSystem(name, chat.WHISPER_TYPE_SYSTEM, errorLine)
		self.interface.RecvWhisper(name)

	def RecvWhisper(self, name):
		self.interface.RecvWhisper(name)

	if app.ENABLE_GEM_SYSTEM:
		def OpenGuiGem(self):
			self.interface.OpenGuiGem()

		def GemCheck(self):
			self.interface.GemCheck()

		def OpenGuiGemMarket(self):
			self.interface.OpenGuiGemMarket()

		def GemMarketItems(self, vnums, gem, count):
			self.interface.GemMarketItems(vnums, gem, count)

		def GemMarketSlotsDesblock(self, slot0, slot1, slot2, slot3, slot4, slot5):
			self.interface.GemMarketSlotsDesblock(slot0, slot1, slot2, slot3, slot4, slot5)

		def GemMarketClear(self):
			self.interface.GemMarketClear()

		def GemTimeMarket(self, time):
			self.interface.GemTime(time)

	if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
		def OpenSpecialInventoryWindow(self, category):
			self.interface.OpenSpecialInventoryWindow(int(category))

	def OpenCostumeWindow(self,pageidx):
		self.interface.OpenCostumeWindow(int(pageidx))

	if app.ENABLE_EXPRESSING_EMOTION:
		def ClearSpecialEmotions(self):
			osfinfo.EXPRESSING_EMOTIONS = {}
			self.interface.ClearSpecialEmotions()

		def RegisterSpecialEmotion(self, emotionIdx, leftTime, notice):
			emotionIdx, leftTime, notice = int(emotionIdx), int(leftTime), int(notice)
			self.interface.RegisterSpecialEmotions(emotionIdx, leftTime)

			if notice != 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPEN_THE_SPECIAL_ACTION_KIT % osfinfo.GET_SPECIAL_EMOTION_NAME(emotionIdx))

	if app.ENABLE_12ZI:
		def SetBeadCount(self, value):
			self.interface.SetBeadCount(value)

		def NextBeadUpdateTime(self, value):
			self.interface.NextBeadUpdateTime(value)

	def OnShopError(self, type):
		if type == "NOT_ENOUGH_GUILDCOIN":
			self.PopupMessage(getattr(localeinfo, "GUILD_SHOP_NOT_ENOUGH_COINS", "Not enough Guild Coins."))
			return
		try:
			self.PopupMessage(localeinfo.SHOP_ERROR_DICT[type])
		except KeyError:
			self.PopupMessage(localeinfo.SHOP_ERROR_UNKNOWN % (type))

	def OnSafeBoxError(self):
		self.PopupMessage(localeinfo.SAFEBOX_ERROR)

	def OnFishingSuccess(self, isFish, fishName):
		chat.AppendChatWithDelay(chat.CHAT_TYPE_INFO, localeinfo.FISHING_SUCCESS(isFish, fishName), 2000)

	# ADD_FISHING_MESSAGE
	def OnFishingNotifyUnknown(self):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.FISHING_UNKNOWN)

	def OnFishingWrongPlace(self):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.FISHING_WRONG_PLACE)
	# END_OF_ADD_FISHING_MESSAGE

	def OnFishingNotify(self, isFish, fishName):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.FISHING_NOTIFY(isFish, fishName))

	def OnFishingFailure(self):
		chat.AppendChatWithDelay(chat.CHAT_TYPE_INFO, localeinfo.FISHING_FAILURE, 2000)

	if app.ENABLE_FISHING_GAME:
		def OnFishingGameStart(self, level):
			if self.interface:
				self.interface.OpenFishingGameWindow(level)

		def OnFishingStopGame(self):
			if self.interface:
				self.interface.CloseFishingGameWindow()

	if app.ENABLE_FISHING_GAME_BDO:
		def OnFishingBdoOpen(self, roundsTotal, hitsRequired):
			if self.interface:
				self.interface.OpenFishingBdoWindow(roundsTotal, hitsRequired)

		def OnFishingBdoRound(self, roundIndex, zoneStartPm, zoneWidthPm, travelMs):
			if self.interface:
				self.interface.RoundFishingBdoWindow(roundIndex, zoneStartPm, zoneWidthPm, travelMs)

		def OnFishingBdoResult(self, roundIndex, hit, hitsSoFar):
			if self.interface:
				self.interface.ResultFishingBdoWindow(roundIndex, hit, hitsSoFar)

		def OnFishingBdoEnd(self, success, doubled):
			if self.interface:
				self.interface.EndFishingBdoWindow(success, doubled)

		def OnFishingBdoQuit(self):
			if self.interface:
				self.interface.CloseFishingBdoWindow()

		def SpaceKeyDown(self):
			if self.interface and self.interface.IsFishingBdoOpen():
				self.interface.PressFishingBdo()
				return
			self.StartAttack()

	def OnCannotPickItem(self):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GAME_CANNOT_PICK_ITEM)

	# MINING
	def OnCannotMining(self):
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GAME_CANNOT_MINING)
	# END_OF_MINING

	def OnCannotUseSkill(self, vid, type):
		if localeinfo.USE_SKILL_ERROR_TAIL_DICT.has_key(type):
			textTail.RegisterInfoTail(vid, localeinfo.USE_SKILL_ERROR_TAIL_DICT[type])

		if localeinfo.USE_SKILL_ERROR_CHAT_DICT.has_key(type):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.USE_SKILL_ERROR_CHAT_DICT[type])

	def	OnCannotShotError(self, vid, type):
		textTail.RegisterInfoTail(vid, localeinfo.SHOT_ERROR_TAIL_DICT.get(type, localeinfo.SHOT_ERROR_UNKNOWN % (type)))

	## PointReset
	def StartPointReset(self):
		self.interface.OpenPointResetDialog()

	## Shop
	def StartShop(self, vid, remote = 0):
		self.interface.OpenShopDialog(vid, remote)

	def EndShop(self):
		self.interface.CloseShopDialog()

	def RefreshShop(self):
		self.interface.RefreshShopDialog()

	def SetShopSellingPrice(self, Price):
		pass

	## Exchange
	def StartExchange(self):
		self.interface.StartExchange()

	def EndExchange(self):
		self.interface.EndExchange()

	def RefreshExchange(self):
		self.interface.RefreshExchange()

	if app.WJ_ENABLE_TRADABLE_ICON:
		def AddExchangeItemSlotIndex(self, idx):
			self.interface.AddExchangeItemSlotIndex(idx)

	## Party
	if app.WJ_NEW_USER_CARE:
		def RecvPartyInviteQuestion(self, leaderVID, leaderName):
			partyInviteQuestionDialog = uicommon.QuestionDialogWithTimeLimit()
			partyInviteQuestionDialog.SetAcceptEvent(lambda arg=True: self.AnswerPartyInvite(arg))
			partyInviteQuestionDialog.SetCancelEvent(lambda arg=False: self.AnswerPartyInvite(arg))
			partyInviteQuestionDialog.Open(leaderName + localeinfo.PARTY_DO_YOU_JOIN, 10)
			partyInviteQuestionDialog.SetTimeOverMsg(localeinfo.PARTY_ANSWER_TIMEOVER)
			partyInviteQuestionDialog.SetCancelOnTimeOver()
			partyInviteQuestionDialog.partyLeaderVID = leaderVID
			self.partyInviteQuestionDialog = partyInviteQuestionDialog
	else:
		def RecvPartyInviteQuestion(self, leaderVID, leaderName):
			partyInviteQuestionDialog = uicommon.QuestionDialog()
			partyInviteQuestionDialog.SetText(leaderName + localeinfo.PARTY_DO_YOU_JOIN)
			partyInviteQuestionDialog.SetAcceptEvent(lambda arg=True: self.AnswerPartyInvite(arg))
			partyInviteQuestionDialog.SetCancelEvent(lambda arg=False: self.AnswerPartyInvite(arg))
			partyInviteQuestionDialog.Open()
			partyInviteQuestionDialog.partyLeaderVID = leaderVID
			self.partyInviteQuestionDialog = partyInviteQuestionDialog

	def AnswerPartyInvite(self, answer):
		if not self.partyInviteQuestionDialog:
			return

		partyLeaderVID = self.partyInviteQuestionDialog.partyLeaderVID

		if not app.WJ_NEW_USER_CARE and not app.ENABLE_CROSSCORE_PARTY_INVITE:
			distance = player.GetCharacterDistance(partyLeaderVID)
			if distance < 0.0 or distance > 5000:
				answer = False

		net.SendPartyInviteAnswerPacket(partyLeaderVID, answer)

		self.partyInviteQuestionDialog.Close()
		self.partyInviteQuestionDialog = None

	if app.WJ_SHOW_PARTY_ON_MINIMAP:
		def AddPartyMember(self, pid, name, mapIdx, channel):
			self.interface.AddPartyMember(pid, name, mapIdx, channel)
	else:
		def AddPartyMember(self, pid, name):
			self.interface.AddPartyMember(pid, name)

	def UpdatePartyMemberInfo(self, pid):
		self.interface.UpdatePartyMemberInfo(pid)

	def RemovePartyMember(self, pid):
		self.interface.RemovePartyMember(pid)
		self.__RefreshTargetBoard()

	if app.WJ_SHOW_PARTY_ON_MINIMAP:
		def LinkPartyMember(self, pid, vid, mapIdx, channel):
			self.interface.LinkPartyMember(pid, vid, mapIdx, channel)
	else:
		def LinkPartyMember(self, pid, vid):
			self.interface.LinkPartyMember(pid, vid)

	def UnlinkPartyMember(self, pid):
		self.interface.UnlinkPartyMember(pid)

	def UnlinkAllPartyMember(self):
		self.interface.UnlinkAllPartyMember()

	def ExitParty(self):
		self.interface.ExitParty()
		self.RefreshTargetBoardByVID(self.targetBoard.GetTargetVID())

	def ChangePartyParameter(self, distributionMode):
		self.interface.ChangePartyParameter(distributionMode)

	## Messenger
	def OnMessengerAddFriendQuestion(self, name):
		# routed through Interface so the friend-request badge/queue owns the flow
		self.interface.OnMessengerAddFriendQuestion(name)

	def OnAcceptAddFriend(self):
		name = self.messengerAddFriendQuestion.name
		net.SendChatPacket("/messenger_auth y " + name)
		self.OnCloseAddFriendQuestionDialog()
		return True

	def OnDenyAddFriend(self):
		name = self.messengerAddFriendQuestion.name
		net.SendChatPacket("/messenger_auth n " + name)
		self.OnCloseAddFriendQuestionDialog()
		return True

	def OnCloseAddFriendQuestionDialog(self):
		self.messengerAddFriendQuestion.Close()
		self.messengerAddFriendQuestion = None
		return True

	## SafeBox
	def OpenSafeboxWindow(self, size):
		self.interface.OpenSafeboxWindow(size)

	def RefreshSafebox(self):
		self.interface.RefreshSafebox()

	def RefreshSafeboxMoney(self):
		self.interface.RefreshSafeboxMoney()

	# ITEM_MALL
	def OpenMallWindow(self, size):
		self.interface.OpenMallWindow(size)

	def RefreshMall(self):
		self.interface.RefreshMall()
	# END_OF_ITEM_MALL

	## Guild
	def RecvGuildInviteQuestion(self, guildID, guildName):
		guildInviteQuestionDialog = uicommon.QuestionDialog()
		guildInviteQuestionDialog.SetText(guildName + localeinfo.GUILD_DO_YOU_JOIN)
		guildInviteQuestionDialog.SetAcceptEvent(lambda arg=True: self.AnswerGuildInvite(arg))
		guildInviteQuestionDialog.SetCancelEvent(lambda arg=False: self.AnswerGuildInvite(arg))
		guildInviteQuestionDialog.Open()
		guildInviteQuestionDialog.guildID = guildID
		self.guildInviteQuestionDialog = guildInviteQuestionDialog

	def AnswerGuildInvite(self, answer):
		if not self.guildInviteQuestionDialog:
			return

		guildLeaderVID = self.guildInviteQuestionDialog.guildID
		net.SendGuildInviteAnswerPacket(guildLeaderVID, answer)

		self.guildInviteQuestionDialog.Close()
		self.guildInviteQuestionDialog = None

	def DeleteGuild(self):
		self.interface.DeleteGuild()

	## Clock
	def ShowClock(self, second):
		self.interface.ShowClock(second)

	def HideClock(self):
		self.interface.HideClock()

	## Emotion
	def BINARY_ActEmotion(self, emotionIndex):
		if self.interface.wndCharacter:
			self.interface.wndCharacter.ActEmotion(emotionIndex)

	###############################################################################################
	###############################################################################################
	## Keyboard Functions

	def CheckFocus(self):
		if False == self.IsFocus():
			if True == self.interface.IsOpenChat():
				self.interface.ToggleChat()

			self.SetFocus()

	def SaveScreen(self):
		print "save screen"

		# SCREENSHOT_CWDSAVE
		if SCREENSHOT_CWDSAVE:
			if not os.path.exists(os.getcwd() + os.sep + "screenshot"):
				os.mkdir(os.getcwd() + os.sep + "screenshot")

			(succeeded, name) = grp.SaveScreenShotToPath(os.getcwd()+os.sep+"screenshot"+os.sep)
		elif SCREENSHOT_DIR:
			(succeeded, name) = grp.SaveScreenShot(SCREENSHOT_DIR)
		else:
			(succeeded, name) = grp.SaveScreenShot()
		# END_OF_SCREENSHOT_CWDSAVE

		if succeeded:
			pass
			"""
			chat.AppendChat(chat.CHAT_TYPE_INFO, name + localeinfo.SCREENSHOT_SAVE1)
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SCREENSHOT_SAVE2)
			"""
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SCREENSHOT_SAVE_FAILURE)

	if app.ENABLE_CAPTCHA_SYSTEM:
		def ProcessCaptcha(self, desc, grid_type, crc_dict, time):
			self.wndCaptcha.Process(desc, grid_type, crc_dict, time)
			self.wndCaptcha.Show()

		if app.ENABLE_CAPTCHA_REWORK:
			def ProcessCaptchaV2(self, nonce, grid_type, timer, round, total_rounds, token_list, desc):
				self.wndCaptcha.ProcessV2(nonce, grid_type, timer, round, total_rounds, token_list, desc)
				self.wndCaptcha.Show()

		if app.USE_CAPTCHA_IMPRISONMENT:
			def ImprisonedPopUp(self):
				self.stream.popupWindow.Close()
				self.stream.popupWindow.Open(localeinfo.CAPTCHA_IMPRISONED_ALERT, 0, localeinfo.UI_OK)

	if app.ENABLE_PARTY_FINDER:
		def BINARY_OnPartyFinderList(self, serverNow, entries):
			self.interface.OnPartyFinderBoard(serverNow, entries)

		def BINARY_OnPartyFinderJoinPrompt(self, pid, name, level, race):
			self.interface.OnPartyFinderJoinPrompt(pid, name, level, race)

		def BINARY_OnPartyFinderJoinResult(self, result, leaderName):
			self.interface.OnPartyFinderJoinResult(result, leaderName)

	if app.ENABLE_GUILD_FINDER:
		def BINARY_OnGuildFinderList(self, entries, myAppGids):
			self.interface.OnGuildFinderList(entries, myAppGids)

		def BINARY_OnGuildFinderDetail(self, guildID, leaderName, members, maxMembers, online, myApplied, desc):
			self.interface.OnGuildFinderDetail(guildID, leaderName, members, maxMembers, online, myApplied, desc)

		def BINARY_OnGuildFinderResult(self, guildID, result):
			self.interface.OnGuildFinderResult(guildID, result)

		def BINARY_OnGuildFinderInbox(self, guildID, mode, minLevel, desc, applicants):
			self.interface.OnGuildFinderInbox(guildID, mode, minLevel, desc, applicants)

		def BINARY_OnGuildFinderBadge(self, count):
			self.interface.OnGuildFinderBadge(count)

		def __OpenGuildFinder(self):
			self.interface.ToggleGuildFinderWindow()

	def ShowConsole(self):
		if debuginfo.IsDebugMode() or True == self.consoleEnable or osfinfo.IsDebugMode():
			player.EndKeyWalkingImmediately()
			self.console.OpenWindow()

	def ShowName(self):
		self.ShowNameFlag = True
		# if app.USE_OFFLINESHOP:
			# offlineshop.ShowShopNames()

		self.playerGauge.EnableShowAlways()
		if not app.ENABLE_KEYCHANGE_SYSTEM:
			player.SetQuickPage(self.quickSlotPageIndex + 1)

	# ADD_ALWAYS_SHOW_NAME
	def __IsShowName(self):
		if systemSetting.IsAlwaysShowName():
			return True

		if self.ShowNameFlag:
			return True

		return False
	# END_OF_ADD_ALWAYS_SHOW_NAME

	def HideName(self):
		self.ShowNameFlag = False
		self.playerGauge.DisableShowAlways()
		if not app.ENABLE_KEYCHANGE_SYSTEM:
			player.SetQuickPage(self.quickSlotPageIndex)
		
		# if app.USE_OFFLINESHOP:
			# offlineshop.HideShopNames()


	def ShowMouseImage(self):
		self.interface.ShowMouseImage()

	def HideMouseImage(self):
		self.interface.HideMouseImage()

	def StartAttack(self):
		player.SetAttackKeyState(True)

	def EndAttack(self):
		player.SetAttackKeyState(False)

	if app.ENABLE_MAINTENANCE_SYSTEM:
		def BINARY_Update_Maintenance(self, iTime, iDuration, iReason):
			sTime = int(iTime)
			sDuration = int(iDuration)
			sReason = str(iReason)

			if sTime != 0 and sDuration != 0:
				self.wndMaintenance.OpenMaintenance(int(iTime), int(iDuration), str(iReason))


	def MoveUp(self):
		player.SetSingleDIKKeyState(app.DIK_UP, True)

	def MoveDown(self):
		player.SetSingleDIKKeyState(app.DIK_DOWN, True)

	def MoveLeft(self):
		player.SetSingleDIKKeyState(app.DIK_LEFT, True)

	def MoveRight(self):
		player.SetSingleDIKKeyState(app.DIK_RIGHT, True)

	def StopUp(self):
		player.SetSingleDIKKeyState(app.DIK_UP, False)

	def StopDown(self):
		player.SetSingleDIKKeyState(app.DIK_DOWN, False)

	def StopLeft(self):
		player.SetSingleDIKKeyState(app.DIK_LEFT, False)

	def StopRight(self):
		player.SetSingleDIKKeyState(app.DIK_RIGHT, False)

	def PickUpItem(self):
		player.PickCloseItem()

	if app.ENABLE_QUICK_PICKUP:
		def PickUpAllItems(self):
			player.PickAllCloseItems()

	###############################################################################################
	###############################################################################################
	## Event Handler

	def OnKeyDown(self, key):
		if key == app.DIK_ESC:
			self.RequestDropItem(False)
			constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

		if app.ENABLE_KEYBIND_V2:
			import keybinds
			keybinds.OnKeyDown(key)
			return True

		try:
			if app.ENABLE_KEYCHANGE_SYSTEM:
				if self.wndKeyChange.IsOpen() == 1:
					if self.wndKeyChange.IsSelectKeySlot():
						if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
							if self.wndKeyChange.IsChangeKey(self.wndKeyChange.GetSelectSlotNumber()):
								self.wndKeyChange.ChangeKey(key + app.DIK_LCONTROL + self.ADDKEYBUFFERCONTROL)
							else:
								chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.KEYCHANGE_IMPOSSIBLE_CHANGE)
						elif app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT):
							if self.wndKeyChange.IsChangeKey(self.wndKeyChange.GetSelectSlotNumber()):
								self.wndKeyChange.ChangeKey(key + app.DIK_LALT + self.ADDKEYBUFFERALT)
							else:
								chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.KEYCHANGE_IMPOSSIBLE_CHANGE)
						elif app.IsPressed(app.DIK_LSHIFT) or app.IsPressed(app.DIK_RSHIFT):
							if self.wndKeyChange.IsChangeKey(self.wndKeyChange.GetSelectSlotNumber()):
								self.wndKeyChange.ChangeKey(key + app.DIK_LSHIFT + self.ADDKEYBUFFERSHIFT)
							else:
								chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.KEYCHANGE_IMPOSSIBLE_CHANGE)
						else:
							self.wndKeyChange.ChangeKey(key)
				else:
					player.OnKeyDown(key)
			else:
				self.onPressKeyDict[key]()
		except KeyError:
			pass
		except:
			raise

		return True

	def OnKeyUp(self, key):
		if app.ENABLE_KEYBIND_V2:
			import keybinds
			keybinds.OnKeyUp(key)
			return True

		if app.ENABLE_KEYCHANGE_SYSTEM:
			player.OnKeyUp(key)
		else:
			try:
				self.onClickKeyDict[key]()
			except KeyError:
				pass
			except:
				raise
		
		return True

	def OnMouseLeftButtonDown(self):
		if self.interface.BUILD_OnMouseLeftButtonDown():
			return

		if mousemodule.mouseController.isAttached():
			self.CheckFocus()
		else:
			hyperlink = ui.GetHyperlink()
			if hyperlink:
				return
			else:
				self.CheckFocus()
				player.SetMouseState(player.MBT_LEFT, player.MBS_PRESS);

		return True

	def OnMouseLeftButtonUp(self):
		if self.interface.BUILD_OnMouseLeftButtonUp():
			return

		if mousemodule.mouseController.isAttached():
			attachedType = mousemodule.mouseController.GetAttachedType()
			attachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()
			attachedItemSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			attachedItemCount = mousemodule.mouseController.GetAttachedItemCount()

			if app.USE_OFFLINESHOP:
				if uiofflineshop_ae.IsBuildingShop() and\
					uiofflineshop_ae.IsSaleSlot(player.SlotTypeToInvenType(attachedType), attachedItemSlotPos): #toupdate
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
					return

			## QuickSlot
			if player.SLOT_TYPE_QUICK_SLOT == attachedType:
				player.RequestDeleteGlobalQuickSlot(attachedItemSlotPos)

			## Inventory
			elif player.SLOT_TYPE_INVENTORY == attachedType or\
				(player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedType or\
				player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedType or\
				player.SLOT_TYPE_STONE_INVENTORY == attachedType or\
				player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedType or\
				player.SLOT_TYPE_ENCHANT_INVENTORY == attachedType or\
				player.SLOT_TYPE_POTS_INVENTORY == attachedType):

				if player.ITEM_MONEY == attachedItemIndex:
					if app.ENABLE_CHEQUE_SYSTEM:
						cheque = mousemodule.mouseController.GetCheque()
						self.__PutMoney(attachedType, attachedItemCount, self.PickingCharacterIndex, cheque)
					else:
						self.__PutMoney(attachedType, attachedItemCount, self.PickingCharacterIndex)
				else:
					self.__PutItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, self.PickingCharacterIndex)

			## DragonSoul
			elif player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedType:
				self.__PutItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, self.PickingCharacterIndex)
			## Aura System
			elif app.USE_AURA_SYSTEM and player.SLOT_TYPE_AURA == attachedType:
				self.__PutItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, self.PickingCharacterIndex)

			mousemodule.mouseController.DeattachObject()

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if player.SLOT_TYPE_CHANGE_LOOK == attachedType:
					self.__PutItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, self.PickingCharacterIndex)

			mousemodule.mouseController.DeattachObject()
		else:
			hyperlink = ui.GetHyperlink()
			if hyperlink:
				# Left-click: ALT rebuilds link for re-paste, otherwise show preview tooltip.
				# (SHIFT+right-click opens the wiki -- see OnMouseRightButtonDown below.)
				if app.IsPressed(app.DIK_LALT):
					link = chat.GetLinkFromHyperlink(hyperlink)
					#ime.PasteString(link)
				else:
					self.interface.MakeHyperlinkTooltip(hyperlink)
				return
			else:
				player.SetMouseState(player.MBT_LEFT, player.MBS_CLICK)

		# player.EndMouseWalking()
		return True

	def __PutItem(self, attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, dstChrID):
		if player.SLOT_TYPE_INVENTORY == attachedType or player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedType or\
			(player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedType or\
			player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedType or\
			player.SLOT_TYPE_STONE_INVENTORY == attachedType or\
			player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedType or\
			player.SLOT_TYPE_ENCHANT_INVENTORY == attachedType or\
			player.SLOT_TYPE_POTS_INVENTORY == attachedType):

			attachedInvenType = player.SlotTypeToInvenType(attachedType)
			if True == chr.HasInstance(self.PickingCharacterIndex) and player.GetMainCharacterIndex() != dstChrID:
				if player.IsEquipmentSlot(attachedItemSlotPos) and player.SLOT_TYPE_DRAGON_SOUL_INVENTORY != attachedType:
					self.stream.popupWindow.Close()
					self.stream.popupWindow.Open(localeinfo.EXCHANGE_FAILURE_EQUIP_ITEM, 0, localeinfo.UI_OK)
				else:
					if chr.IsNPC(dstChrID):
						if app.ENABLE_AUTO_REFINE:
							osfinfo.AUTO_REFINE_TYPE = 2
							osfinfo.AUTO_REFINE_DATA["NPC"][0] = dstChrID
							osfinfo.AUTO_REFINE_DATA["NPC"][1] = attachedInvenType
							osfinfo.AUTO_REFINE_DATA["NPC"][2] = attachedItemSlotPos
							osfinfo.AUTO_REFINE_DATA["NPC"][3] = attachedItemCount

						net.SendGiveItemPacket(dstChrID, attachedInvenType, attachedItemSlotPos, attachedItemCount)
					elif app.ENABLE_MELEY_LAIR_DUNGEON and chr.IsStone(dstChrID):
						net.SendGiveItemPacket(dstChrID, attachedInvenType, attachedItemSlotPos, attachedItemCount)
					else:
						net.SendExchangeStartPacket(dstChrID)
						net.SendExchangeItemAddPacket(attachedInvenType, attachedItemSlotPos, 0)
			else:
				self.__DropItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount)

		if app.USE_AURA_SYSTEM and player.SLOT_TYPE_AURA == attachedType:
			self.__DropItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount)


		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if player.SLOT_TYPE_CHANGE_LOOK == attachedType:
				self.__DropItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount)

	if app.ENABLE_CHEQUE_SYSTEM:
		def __PutMoney(self, attachedType, attachedMoney, dstChrID, cheque):
			if True == chr.HasInstance(dstChrID) and player.GetMainCharacterIndex() != dstChrID:
				net.SendExchangeStartPacket(dstChrID)
				net.SendExchangeElkAddPacket(attachedMoney)
				net.SendExchangeChequeAddPacket(cheque)
			else:
				self.stream.popupWindow.Close()
				self.stream.popupWindow.Open(localeinfo.CHEQUE_SYSTEM_DO_NOT_DROP_MONEY, 0, localeinfo.UI_OK)
	else:
		def __PutMoney(self, attachedType, attachedMoney, dstChrID):
			if True == chr.HasInstance(dstChrID) and player.GetMainCharacterIndex() != dstChrID:
				net.SendExchangeStartPacket(dstChrID)
				net.SendExchangeElkAddPacket(attachedMoney)
			else:
				self.__DropMoney(attachedType, attachedMoney)

	def __DropMoney(self, attachedType, attachedMoney):
		# PRIVATESHOP_DISABLE_ITEM_DROP
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)
			return
		# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP

		if attachedMoney >= 1000:
			self.stream.popupWindow.Close()
			self.stream.popupWindow.Open(localeinfo.DROP_MONEY_FAILURE_1000_OVER, 0, localeinfo.UI_OK)
			return

		itemDropQuestionDialog = uicommon.QuestionDialog()
		itemDropQuestionDialog.SetText(localeinfo.DO_YOU_DROP_MONEY % (attachedMoney))
		itemDropQuestionDialog.SetAcceptEvent(lambda arg=True: self.RequestDropItem(arg))
		itemDropQuestionDialog.SetCancelEvent(lambda arg=False: self.RequestDropItem(arg))
		itemDropQuestionDialog.Open()
		itemDropQuestionDialog.dropType = attachedType
		itemDropQuestionDialog.dropCount = attachedMoney
		itemDropQuestionDialog.dropNumber = player.ITEM_MONEY
		self.itemDropQuestionDialog = itemDropQuestionDialog

	def __HasItemAttributes(self, slotPos):
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			attr = player.GetItemAttribute(slotPos, i)
			if attr[0] > 0:
				return True
		return False

	def __ShowAttrWarning(self, onAccept):
		if self.attrWarningDialog:
			self.attrWarningDialog.Close()
			self.attrWarningDialog = None

		attrWarningDialog = uicommon.QuestionDialog()
		attrWarningDialog.SetText(localeinfo.ITEM_ATTR_WARNING, True)
		attrWarningDialog.SetAcceptText(localeinfo.ITEM_ATTR_WARNING_YES)
		attrWarningDialog.SetCancelText(localeinfo.ITEM_ATTR_WARNING_NO)
		attrWarningDialog.SetAcceptEvent(lambda: self.__OnAttrWarningAccept(onAccept))
		attrWarningDialog.SetCancelEvent(lambda: self.__OnAttrWarningCancel())
		attrWarningDialog.Open()
		self.attrWarningDialog = attrWarningDialog

	def __OnAttrWarningAccept(self, onAccept):
		if self.attrWarningDialog:
			self.attrWarningDialog.Close()
			self.attrWarningDialog = None
		onAccept()

	def __OnAttrWarningCancel(self):
		if self.attrWarningDialog:
			self.attrWarningDialog.Close()
			self.attrWarningDialog = None

	def __DropItem(self, attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount):
		# PRIVATESHOP_DISABLE_ITEM_DROP
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)
			return
		# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP

		if player.SLOT_TYPE_INVENTORY == attachedType and player.IsEquipmentSlot(attachedItemSlotPos):
			self.stream.popupWindow.Close()
			self.stream.popupWindow.Open(localeinfo.DROP_ITEM_FAILURE_EQUIP_ITEM, 0, localeinfo.UI_OK)
		else:
			if player.SLOT_TYPE_INVENTORY == attachedType or\
				(player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedType or\
				player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedType or\
				player.SLOT_TYPE_STONE_INVENTORY == attachedType or\
				player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedType or\
				player.SLOT_TYPE_ENCHANT_INVENTORY == attachedType or\
				player.SLOT_TYPE_POTS_INVENTORY == attachedType):
				dropItemIndex = player.GetItemIndex(attachedItemSlotPos)

				item.SelectItem(dropItemIndex)
				dropItemName = item.GetItemName()

				## Question Text
				questionText = localeinfo.HOW_MANY_ITEM_DO_YOU_DROP(dropItemName, attachedItemCount)

				if not getattr(self, "skipAttrWarning", False) and self.__HasItemAttributes(attachedItemSlotPos):
					self.__ShowAttrWarning(lambda: self.__DropItemConfirmed(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount))
					return

				## Dialog
				if app.ENABLE_NEW_DROP_DIALOG:
					itemDropQuestionDialog = uicommon.QuestionDropDialog()
					itemDropQuestionDialog.SetText(questionText)
					itemDropQuestionDialog.SetAcceptEvent(lambda arg=True: self.RequestDropItem(arg))
					itemDropQuestionDialog.SetDestroyEvent(ui.__mem_func__(self.RequestDestroyItem))
					itemDropQuestionDialog.SetSellEvent(ui.__mem_func__(self.RequestSellItem))
					itemDropQuestionDialog.SetCancelEvent(lambda arg=False: self.RequestDropItem(arg))
					itemDropQuestionDialog.SetItemSlot(attachedItemSlotPos)
					itemDropQuestionDialog.Open()
					itemDropQuestionDialog.dropType = attachedType
					itemDropQuestionDialog.dropNumber = attachedItemSlotPos
					itemDropQuestionDialog.dropCount = attachedItemCount
					self.itemDropQuestionDialog = itemDropQuestionDialog
				else:
					itemDropQuestionDialog = uicommon.QuestionDialog()
					itemDropQuestionDialog.SetText(questionText)
					itemDropQuestionDialog.SetAcceptEvent(lambda arg=True: self.RequestDropItem(arg))
					itemDropQuestionDialog.SetCancelEvent(lambda arg=False: self.RequestDropItem(arg))
					itemDropQuestionDialog.Open()
					itemDropQuestionDialog.dropType = attachedType
					itemDropQuestionDialog.dropNumber = attachedItemSlotPos
					itemDropQuestionDialog.dropCount = attachedItemCount
					self.itemDropQuestionDialog = itemDropQuestionDialog

				constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

			elif player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedType:
				dropItemIndex = player.GetItemIndex(player.DRAGON_SOUL_INVENTORY, attachedItemSlotPos)

				item.SelectItem(dropItemIndex)
				dropItemName = item.GetItemName()

				## Question Text
				questionText = localeinfo.HOW_MANY_ITEM_DO_YOU_DROP(dropItemName, attachedItemCount)

				## Dialog
				itemDropQuestionDialog = uicommon.QuestionDialog()
				itemDropQuestionDialog.SetText(questionText)
				itemDropQuestionDialog.SetAcceptEvent(lambda arg=True: self.RequestDropItem(arg))
				itemDropQuestionDialog.SetCancelEvent(lambda arg=False: self.RequestDropItem(arg))
				itemDropQuestionDialog.Open()
				itemDropQuestionDialog.dropType = attachedType
				itemDropQuestionDialog.dropNumber = attachedItemSlotPos
				itemDropQuestionDialog.dropCount = attachedItemCount
				self.itemDropQuestionDialog = itemDropQuestionDialog

				constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)
		if app.USE_AURA_SYSTEM and player.SLOT_TYPE_AURA == attachedType:
			net.SendAuraRefineCheckOut(attachedItemSlotPos, player.GetAuraRefineWindowType())


			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if player.SLOT_TYPE_CHANGE_LOOK == attachedType:
					net.SendChangeLookCheckOut(attachedItemSlotPos)

	def __DropItemConfirmed(self, attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount):
		self.skipAttrWarning = True
		self.__DropItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount)
		self.skipAttrWarning = False

	def RequestDropItem(self, answer):
		if not self.itemDropQuestionDialog:
			return

		if answer:
			dropType = self.itemDropQuestionDialog.dropType
			dropCount = self.itemDropQuestionDialog.dropCount
			dropNumber = self.itemDropQuestionDialog.dropNumber

			if player.SLOT_TYPE_INVENTORY == dropType or\
				(player.SLOT_TYPE_SKILL_BOOK_INVENTORY == dropType or\
				player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == dropType or\
				player.SLOT_TYPE_STONE_INVENTORY == dropType or\
				player.SLOT_TYPE_GIFT_BOX_INVENTORY == dropType or\
				player.SLOT_TYPE_ENCHANT_INVENTORY == dropType or\
				player.SLOT_TYPE_POTS_INVENTORY == dropType and app.NEW_SPECIAL_INV):

				if dropNumber == player.ITEM_MONEY:
					net.SendGoldDropPacketNew(dropCount)
					snd.PlaySound("sound/ui/money.wav")
				elif dropNumber == player.ITEM_MONEY and app.ENABLE_CHEQUE_SYSTEM:
					net.SendChequeDropPacketNew(dropCount)
					snd.PlaySound("sound/ui/money.wav")
				else:
					# PRIVATESHOP_DISABLE_ITEM_DROP
					self.__SendDropItemPacket(dropNumber, dropCount)
					# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP

			elif player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == dropType:
					# PRIVATESHOP_DISABLE_ITEM_DROP
					self.__SendDropItemPacket(dropNumber, dropCount, player.DRAGON_SOUL_INVENTORY)
					# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP
		elif app.ENABLE_NEW_DROP_DIALOG:
			if self.itemDestroyQuestionDialog:
				self.itemDestroyQuestionDialog.Close()
				self.itemDestroyQuestionDialog = None
		
		self.itemDropQuestionDialog.Close()
		self.itemDropQuestionDialog = None

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	if app.ENABLE_NEW_DROP_DIALOG:
		def __SendDestroyItemPacket(self, itemVNum, itemInvenType = player.INVENTORY):
			if uiprivateshopbuilder.IsBuildingPrivateShop():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)
				return

			net.SendItemDestroyPacket(itemVNum)

		def AnswerDestroyItem(self, answer):
			if not self.itemDropQuestionDialog or not self.itemDestroyQuestionDialog:
				return
			
			if answer:
				dropType = self.itemDestroyQuestionDialog.dropType
				dropCount = self.itemDestroyQuestionDialog.dropCount
				dropNumber = self.itemDestroyQuestionDialog.dropNumber

				if player.SLOT_TYPE_INVENTORY == dropType or\
					(player.SLOT_TYPE_SKILL_BOOK_INVENTORY == dropType or\
					player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == dropType or\
					player.SLOT_TYPE_STONE_INVENTORY == dropType or\
					player.SLOT_TYPE_GIFT_BOX_INVENTORY == dropType or\
					player.SLOT_TYPE_ENCHANT_INVENTORY == dropType or\
					player.SLOT_TYPE_POTS_INVENTORY == dropType and app.NEW_SPECIAL_INV):

					if dropNumber == player.ITEM_MONEY:
						return
					elif dropNumber == player.ITEM_MONEY and app.ENABLE_CHEQUE_SYSTEM:
						return
					else:
						self.__SendDestroyItemPacket(dropNumber)
			
			self.itemDestroyQuestionDialog.Close()
			self.itemDestroyQuestionDialog = None
			
			if answer:
				self.itemDropQuestionDialog.Close()
				self.itemDropQuestionDialog = None
				constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

		def RequestDestroyItem(self):
			if not self.itemDropQuestionDialog:
				return
			
			if self.__HasItemAttributes(self.itemDropQuestionDialog.dropNumber):
				self.__ShowAttrWarning(lambda: self.__RequestDestroyItemConfirmed())
				return
			
			self.__RequestDestroyItemConfirmed()

		def __RequestDestroyItemConfirmed(self):
			if not self.itemDropQuestionDialog:
				return
			
			if self.itemDestroyQuestionDialog:
				self.itemDestroyQuestionDialog.Close()
				self.itemDestroyQuestionDialog = None
			
			dropItemIndex = player.GetItemIndex(self.itemDropQuestionDialog.dropNumber)
			if not dropItemIndex:
				return
			
			item.SelectItem(dropItemIndex)
			if localeinfo.IsARABIC():
				questionText = localeinfo.CONFIRM_ITEM_DESTROY % (self.itemDropQuestionDialog.dropCount, item.GetItemName())
			else:
				questionText = localeinfo.CONFIRM_ITEM_DESTROY % (item.GetItemName(), self.itemDropQuestionDialog.dropCount)
			
			itemDestroyQuestionDialog = uicommon.QuestionDialog()
			itemDestroyQuestionDialog.SetText(questionText)
			itemDestroyQuestionDialog.SetAcceptEvent(lambda arg = True: self.AnswerDestroyItem(arg))
			itemDestroyQuestionDialog.SetCancelEvent(lambda arg = False: self.AnswerDestroyItem(arg))
			itemDestroyQuestionDialog.Open()
			itemDestroyQuestionDialog.dropType = self.itemDropQuestionDialog.dropType
			itemDestroyQuestionDialog.dropNumber = self.itemDropQuestionDialog.dropNumber
			itemDestroyQuestionDialog.dropCount = self.itemDropQuestionDialog.dropCount
			self.itemDestroyQuestionDialog = itemDestroyQuestionDialog

		def AnswerSellItem(self, answer):
			if not self.itemDropQuestionDialog or not self.itemDestroyQuestionDialog:
				return
			
			if answer:
				dropType = self.itemDestroyQuestionDialog.dropType
				dropCount = self.itemDestroyQuestionDialog.dropCount
				dropNumber = self.itemDestroyQuestionDialog.dropNumber
				if player.SLOT_TYPE_INVENTORY == dropType or\
					(player.SLOT_TYPE_SKILL_BOOK_INVENTORY == dropType or\
					player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == dropType or\
					player.SLOT_TYPE_STONE_INVENTORY == dropType or\
					player.SLOT_TYPE_GIFT_BOX_INVENTORY == dropType or\
					player.SLOT_TYPE_ENCHANT_INVENTORY == dropType or\
					player.SLOT_TYPE_POTS_INVENTORY == dropType and app.NEW_SPECIAL_INV):

					if dropNumber == player.ITEM_MONEY:
						return
					elif dropNumber == player.ITEM_MONEY and app.ENABLE_CHEQUE_SYSTEM:
						return
					else:
						self.__SendSellItemPacket(dropNumber, dropCount)
			
			self.itemDestroyQuestionDialog.Close()
			self.itemDestroyQuestionDialog = None
			
			if answer:
				self.itemDropQuestionDialog.Close()
				self.itemDropQuestionDialog = None
				constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

		def RequestSellItem(self):
			if not self.itemDropQuestionDialog:
				return
			
			if self.__HasItemAttributes(self.itemDropQuestionDialog.dropNumber):
				self.__ShowAttrWarning(lambda: self.__RequestSellItemConfirmed())
				return
			
			self.__RequestSellItemConfirmed()

		def __RequestSellItemConfirmed(self):
			if not self.itemDropQuestionDialog:
				return
			
			if self.itemDestroyQuestionDialog:
				self.itemDestroyQuestionDialog.Close()
				self.itemDestroyQuestionDialog = None
			
			dropItemIndex = player.GetItemIndex(self.itemDropQuestionDialog.dropNumber)
			if not dropItemIndex:
				return
			
			item.SelectItem(dropItemIndex)
			itemPrice = item.GetISellItemPrice()
			if item.Is1GoldItem():
				itemPrice = self.itemDropQuestionDialog.dropCount / itemPrice / 5
			else:
				itemPrice = itemPrice * max(1, self.itemDropQuestionDialog.dropCount) / 5
			
			questionText = localeinfo.DO_YOU_SELL_ITEM(item.GetItemName(), self.itemDropQuestionDialog.dropCount, itemPrice)
			itemDestroyQuestionDialog = uicommon.QuestionDialog()
			itemDestroyQuestionDialog.SetText(questionText)
			itemDestroyQuestionDialog.SetAcceptEvent(lambda arg = True: self.AnswerSellItem(arg))
			itemDestroyQuestionDialog.SetCancelEvent(lambda arg = False: self.AnswerSellItem(arg))
			itemDestroyQuestionDialog.Open()
			itemDestroyQuestionDialog.dropType = self.itemDropQuestionDialog.dropType
			itemDestroyQuestionDialog.dropNumber = self.itemDropQuestionDialog.dropNumber
			itemDestroyQuestionDialog.dropCount = self.itemDropQuestionDialog.dropCount
			self.itemDestroyQuestionDialog = itemDestroyQuestionDialog

		def __SendSellItemPacket(self, slotPos, itemCount):
			if uiprivateshopbuilder.IsBuildingPrivateShop():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)
				return
			
			net.SendShopSellPacketNew(slotPos, itemCount, player.INVENTORY)

	# PRIVATESHOP_DISABLE_ITEM_DROP
	def __SendDropItemPacket(self, itemVNum, itemCount, itemInvenType = player.INVENTORY):
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)
			return

		net.SendItemDropPacketNew(itemInvenType, itemVNum, itemCount)
	# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP

	def OnMouseRightButtonDown(self):
		self.CheckFocus()

		# SHIFT+right-click on an item chat hyperlink opens the wiki on that item.
		# Intercept before the normal mouse-right-button handling so it doesn't
		# trigger player movement / camera. Hint shown inside the hover tooltip.
		if app.ENABLE_INGAME_WIKI and app.IsPressed(app.DIK_LSHIFT):
			hyperlink = ui.GetHyperlink()
			if hyperlink:
				self.interface.OpenWikiFromHyperlink(hyperlink)
				return True

		if True == mousemodule.mouseController.isAttached():
			mousemodule.mouseController.DeattachObject()
		else:
			player.SetMouseState(player.MBT_RIGHT, player.MBS_PRESS)

		return True

	def OnMouseRightButtonUp(self):
		if True == mousemodule.mouseController.isAttached():
			return True

		player.SetMouseState(player.MBT_RIGHT, player.MBS_CLICK)
		return True

	def OnMouseMiddleButtonDown(self):
		player.SetMouseMiddleButtonState(player.MBS_PRESS)

	def OnMouseMiddleButtonUp(self):
		player.SetMouseMiddleButtonState(player.MBS_CLICK)

	def OnUpdate(self):
		app.UpdateGame()

		try:                       # mining vein readout: tick the engine text tails
			import uimine
			uimine.Update()
		except:
			pass

		saveTimer = getattr(self, '_fastLoginSaveTimer', 0)
		if saveTimer and app.GetTime() >= saveTimer and player.GetStatus(player.LEVEL) > 0:
			self._fastLoginSaveTimer = 0
			try:
				from introLogin import FastLoginManager
				import serverinfo
				flm = FastLoginManager.GetInstance()
				flm.SaveCharacter(
					getattr(constinfo, 'LastAccount', ''),
					getattr(constinfo, 'FAST_LOGIN_PENDING_PWD', ''),
					self.stream.GetCharacterSlot(),
					player.GetName(),
					player.GetStatus(player.LEVEL),
					net.GetMainActorRace(),
					player.GetGuildName(),
					getattr(constinfo, 'SELECTED_CHANNEL', 0),
					serverinfo.GetServerID(),
					player.GetEmpire(),
				)
				constinfo.FAST_LOGIN_PENDING_PWD = ""
			except:
				import dbg
				dbg.TraceError("FastLogin: Failed to save character data")

		if self.mapNameShower.IsShow():
			self.mapNameShower.Update()

		if self.isShowdebuginfo:
			self.Updatedebuginfo()

		if self.enableXMasBoom:
			self.__XMasBoom_Update()

		self.interface.BUILD_OnUpdate()

		# Horse upgrade: re-assert the progress popup every frame. Map
		# transitions and other engine hooks hide floating windows without
		# notifying Python, so we keep nudging it back open while a mission
		# is in progress. EnsurePopupVisible is idempotent and cheap.
		if app.ENABLE_HORSE_UPGRADE and self.interface:
			wnd = getattr(self.interface, 'wndHorseUpgrade', None)
			if wnd:
				try: wnd.EnsurePopupVisible()
				except: pass

		if constinfo.ENABLE_MAP_WEATHER:
			currentMap = background.GetCurrentMapName()
			if currentMap in constinfo.MAP_WEATHER_CONFIG:
				if currentMap != constinfo.CURRENT_WEATHER_MAP:
					constinfo.CURRENT_WEATHER_MAP = currentMap
					constinfo.CURRENT_WEATHER_INDEX = -1
				weatherConfig = constinfo.MAP_WEATHER_CONFIG[currentMap]
				(x, y, z) = player.GetMainCharacterPosition()
				for index, row in enumerate(weatherConfig["WEATHER_POS_LIST"]):
					from_x = row["From"]["x"]
					from_y = row["From"]["y"]
					to_x = row["To"]["x"]
					to_y = row["To"]["y"]

					if from_x <= x/100 <= to_x and from_y <= y/100 <= to_y:
						if index == constinfo.CURRENT_WEATHER_INDEX:
							return

						constinfo.CURRENT_WEATHER_INDEX = index

						if index != 0:
							background.RegisterEnvironmentData(index, weatherConfig["WEATHER_LIST"][index])

						background.SetEnvironmentData(index)
						self.curtain.FadeIn()

	def Updatedebuginfo(self):
		(x, y, z) = player.GetMainCharacterPosition()
		nUpdateTime = app.GetUpdateTime()
		nUpdateFPS = app.GetUpdateFPS()
		nRenderFPS = app.GetRenderFPS()
		nFaceCount = app.GetFaceCount()
		fFaceSpeed = app.GetFaceSpeed()
		nST=background.GetRenderShadowTime()
		(fAveRT, nCurRT) = app.GetRenderTime()
		(iNum, fFogStart, fFogEnd, fFarCilp) = background.GetDistanceSetInfo()
		(iPatch, iSplat, fSplatRatio, sTextureNum) = background.GetRenderedSplatNum()
		if iPatch == 0:
			iPatch = 1

		#(dwRenderedThing, dwRenderedCRC) = background.GetRenderedGraphicThingInstanceNum()

		self.PrintCoord.SetText("Coordinate: %.2f %.2f %.2f ATM: %d" % (x, y, z, app.GetAvailableTextureMemory()/(1024*1024)))
		xMouse, yMouse = wndMgr.GetMousePosition()
		self.PrintMousePos.SetText("MousePosition: %d %d" % (xMouse, yMouse))

		self.FrameRate.SetText("UFPS: %3d UT: %3d FS %.2f" % (nUpdateFPS, nUpdateTime, fFaceSpeed))

		if fAveRT>1.0:
			self.Pitch.SetText("RFPS: %3d RT:%.2f(%3d) FC: %d(%.2f) " % (nRenderFPS, fAveRT, nCurRT, nFaceCount, nFaceCount/fAveRT))

		self.Splat.SetText("PATCH: %d SPLAT: %d BAD(%.2f)" % (iPatch, iSplat, fSplatRatio))
		# self.Pitch.SetText("Pitch: %.2f" % (app.GetCameraPitch())
		# self.TextureNum.SetText("TN : %s" % (sTextureNum))
		# self.ObjectNum.SetText("GTI : %d, CRC : %d" % (dwRenderedThing, dwRenderedCRC))
		self.ViewDistance.SetText("Num : %d, FS : %f, FE : %f, FC : %f" % (iNum, fFogStart, fFogEnd, fFarCilp))

	def OnRender(self):
		app.RenderGame()

		if self.console.Console.collision:
			background.RenderCollision()
			chr.RenderCollision()

		(x, y) = app.GetCursorPosition()

		########################
		# Picking
		########################
		textTail.UpdateAllTextTail()

		if True == wndMgr.IsPickedWindow(self.hWnd):
			self.PickingCharacterIndex = chr.Pick()

			if -1 != self.PickingCharacterIndex:
				textTail.ShowCharacterTextTail(self.PickingCharacterIndex)
			if 0 != self.targetBoard.GetTargetVID():
				textTail.ShowCharacterTextTail(self.targetBoard.GetTargetVID())

			# ADD_ALWAYS_SHOW_NAME
			if not self.__IsShowName():
				self.PickingItemIndex = item.Pick()
				if -1 != self.PickingItemIndex:
					textTail.ShowItemTextTail(self.PickingItemIndex)
			# END_OF_ADD_ALWAYS_SHOW_NAME

		## Show all name in the range

		# ADD_ALWAYS_SHOW_NAME
		if self.__IsShowName():
			textTail.ShowAllTextTail()
			self.PickingItemIndex = textTail.Pick(x, y)
		# END_OF_ADD_ALWAYS_SHOW_NAME

		if app.ENABLE_GRAPHIC_ON_OFF:
			if systemSetting.IsShowSalesText():
				uiprivateshopbuilder.UpdateADBoard()

		textTail.UpdateShowingTextTail()
		textTail.ArrangeTextTail()
		if -1 != self.PickingItemIndex:
			textTail.SelectItemName(self.PickingItemIndex)

		grp.PopState()
		grp.SetInterfaceRenderState()

		textTail.Render()
		textTail.HideAllTextTail()

	def OnPressEscapeKey(self):
		if app.TARGET == app.GetCursor():
			app.SetCursor(app.NORMAL)

		elif True == mousemodule.mouseController.isAttached():
			mousemodule.mouseController.DeattachObject()
		else:
			self.interface.OpenSystemDialog()

		return True

	def OnIMEReturn(self):
		if app.IsPressed(app.DIK_LSHIFT):
			self.interface.OpenWhisperDialogWithoutTarget()
		else:
			self.interface.ToggleChat()
		return True

	def OnPressExitKey(self):
		self.interface.ToggleSystemDialog()
		return True

	## BINARY CALLBACK
	######################################################################################

	# WEDDING
	def BINARY_LoverInfo(self, name, lovePoint):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.OnAddLover(name, lovePoint)
		if self.affectShower:
			self.affectShower.SetLoverInfo(name, lovePoint)

	def BINARY_UpdateLovePoint(self, lovePoint):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.OnUpdateLovePoint(lovePoint)
		if self.affectShower:
			self.affectShower.OnUpdateLovePoint(lovePoint)
	# END_OF_WEDDING

	if app.USE_AURA_SYSTEM:
		def AuraWindowOpen(self, type):
			self.interface.AuraWindowOpen(type)

		def AuraWindowClose(self):
			self.interface.AuraWindowClose()

	# QUEST_CONFIRM
	def BINARY_OnQuestConfirm(self, msg, timeout, pid):
		confirmDialog = uicommon.QuestionDialogWithTimeLimit()
		confirmDialog.Open(msg, timeout)
		confirmDialog.SetAcceptEvent(lambda answer=True, pid=pid: net.SendQuestConfirmPacket(answer, pid) or self.confirmDialog.Hide())
		confirmDialog.SetCancelEvent(lambda answer=False, pid=pid: net.SendQuestConfirmPacket(answer, pid) or self.confirmDialog.Hide())
		confirmDialog.SetCancelOnTimeOver() # hotfix
		self.confirmDialog = confirmDialog
	# END_OF_QUEST_CONFIRM

	# GIFT command
	def Gift_Show(self):
		self.interface.ShowGift()

	def Gift_Hide(self):
		self.interface.HideGift()

	# CUBE
	def BINARY_Cube_Open(self, npcVNUM, reload = 0):
		self.currentCubeNPC = npcVNUM

		if reload:
			self.cubeInformation.clear()
			self.interface.wndCube.ClearOldSlots()

		self.interface.OpenCubeWindow()

		if npcVNUM not in self.cubeInformation:
			net.SendChatPacket("/cube r_info")
		else:
			cubeInfoList = self.cubeInformation[npcVNUM]

			i = 0
			for cubeInfo in cubeInfoList:
				self.interface.wndCube.AddCubeResultItem(cubeInfo["vnum"], cubeInfo["count"])

				j = 0
				for materialList in cubeInfo["materialList"]:
					for materialInfo in materialList:
						itemVnum, itemCount = materialInfo
						self.interface.wndCube.AddMaterialInfo(i, j, itemVnum, itemCount)
					j = j + 1

				i = i + 1

			self.interface.wndCube.Refresh()

	def BINARY_Cube_Close(self):
		self.interface.CloseCubeWindow()

	def BINARY_Cube_UpdateInfo(self, gold, itemVnum, count):
		self.interface.UpdateCubeInfo(gold, itemVnum, count)

	def BINARY_Cube_Succeed(self, itemVnum, count):
		self.interface.SucceedCubeWork(itemVnum, count)
		pass

	def BINARY_Cube_Failed(self):
		self.interface.FailedCubeWork()
		pass

	def BINARY_Cube_ResultList(self, npcVNUM, listText):
		#print listText

		if npcVNUM == 0:
			npcVNUM = self.currentCubeNPC

		self.cubeInformation[npcVNUM] = []

		try:
			for eachInfoText in listText.split("/"):
				eachInfo = eachInfoText.split(",")
				itemVnum = int(eachInfo[0])
				itemCount = int(eachInfo[1])

				self.cubeInformation[npcVNUM].append({"vnum": itemVnum, "count": itemCount})
				self.interface.wndCube.AddCubeResultItem(itemVnum, itemCount)

			resultCount = len(self.cubeInformation[npcVNUM])
			requestCount = 5
			modCount = resultCount % requestCount
			splitCount = resultCount / requestCount
			for i in xrange(splitCount):
				#print("/cube r_info %d %d" % (i * requestCount, requestCount))
				net.SendChatPacket("/cube r_info %d %d" % (i * requestCount, requestCount))

			if 0 < modCount:
				#print("/cube r_info %d %d" % (splitCount * requestCount, modCount))
				net.SendChatPacket("/cube r_info %d %d" % (splitCount * requestCount, modCount))

		except RuntimeError, msg:
			dbg.TraceError(msg)
			return 0

		pass

	def BINARY_Cube_MaterialInfo(self, startIndex, listCount, listText):
		# Material Text Format : 125,1|126,2|127,2|123,5&555,5&555,4/120000
		try:
			#print listText

			if 3 > len(listText):
				dbg.TraceError("Wrong Cube Material Infomation")
				return 0

			eachResultList = listText.split("@")

			cubeInfo = self.cubeInformation[self.currentCubeNPC]

			itemIndex = 0
			for eachResultText in eachResultList:
				cubeInfo[startIndex + itemIndex]["materialList"] = [[], [], [], [], []]
				materialList = cubeInfo[startIndex + itemIndex]["materialList"]

				gold = 0
				splitResult = eachResultText.split("/")
				if 1 < len(splitResult):
					gold = int(splitResult[1])

				#print "splitResult : ", splitResult
				eachMaterialList = splitResult[0].split("&")

				i = 0
				for eachMaterialText in eachMaterialList:
					complicatedList = eachMaterialText.split("|")

					if 0 < len(complicatedList):
						for complicatedText in complicatedList:
							(itemVnum, itemCount) = complicatedText.split(",")
							itemVnum = int(itemVnum)
							itemCount = int(itemCount)
							self.interface.wndCube.AddMaterialInfo(itemIndex + startIndex, i, itemVnum, itemCount)

							materialList[i].append((itemVnum, itemCount))
					else:
						itemVnum, itemCount = eachMaterialText.split(",")
						itemVnum = int(itemVnum)
						itemCount = int(itemCount)
						self.interface.wndCube.AddMaterialInfo(itemIndex + startIndex, i, itemVnum, itemCount)

						materialList[i].append((itemVnum, itemCount))

					i = i + 1

				itemIndex = itemIndex + 1

			self.interface.wndCube.Refresh()

		except RuntimeError, msg:
			dbg.TraceError(msg)
			return 0

		pass

	# END_OF_CUBE

	def BINARY_Highlight_Item(self, inven_type, inven_pos):
		self.interface.Highligt_Item(inven_type, inven_pos)

	def BINARY_DragonSoulGiveQuilification(self):
		self.interface.DragonSoulGiveQuilification()

	def BINARY_DragonSoulRefineWindow_Open(self):
		self.interface.OpenDragonSoulRefineWindow()

	if app.ENABLE_DS_CHANGE_ATTR:
		def BINARY_DragonSoulRefineAttrWindow_Open(self):
			self.interface.OpenDragonSoulRefineAttrWindow()

	def BINARY_DragonSoulRefineWindow_RefineFail(self, reason, inven_type, inven_pos):
		self.interface.FailDragonSoulRefine(reason, inven_type, inven_pos)

	def BINARY_DragonSoulRefineWindow_RefineSucceed(self, inven_type, inven_pos):
		self.interface.SucceedDragonSoulRefine(inven_type, inven_pos)

	def __OnDragonSoulSetBonus(self, points, tier, nextThreshold, stats):
		if getattr(self, "interface", None):
			self.interface.OnDragonSoulSetBonus(points, tier, nextThreshold, stats)

	if app.ENABLE_HORSE_UPGRADE:
		def __ToggleHorseUpgradeWindow(self):
			if not self.interface:
				return
			wnd = getattr(self.interface, "wndHorseUpgrade", None)
			if not wnd:
				return
			if wnd.IsShow():
				wnd.Close()
			else:
				wnd.Open()

		def BINARY_HorseUpgradeState(self, horseLevel, state, kills, startTime, cooldownUntil, chanceBonus):
			if not self.interface:
				return
			wnd = getattr(self.interface, "wndHorseUpgrade", None)
			if not wnd:
				return
			wnd.BINARY_HorseUpgradeState(horseLevel, state, kills, startTime, cooldownUntil, chanceBonus)

	if app.__BUFFI_SUPPORT__:
		def BINARY_OnBuffiStatus(self, summoned, stage, level, intVal, exp, expToNext, expireAt, ore0, ore1, ore2, oreExp0, oreExp1, oreExp2, bossPct, nameExpire, name, evolveFail=0):
			if not self.interface:
				return
			self.interface.OnBuffiStatus(summoned, stage, level, intVal, exp, expToNext, expireAt, ore0, ore1, ore2, oreExp0, oreExp1, oreExp2, bossPct, nameExpire, name, evolveFail)

	def BINARY_OnGrowthMountStatus(self, active, level, exp, reqExp, gold, upMats, skillLevels, skillFails, skillChances, skillMats):
		if not self.interface:
			return
		wnd = getattr(self.interface, "wndCompanion", None)
		if not wnd or not hasattr(wnd, "OnGrowthMountStatus"):
			return
		wnd.OnGrowthMountStatus(active, level, exp, reqExp, gold, upMats, skillLevels, skillFails, skillChances, skillMats)

	if app.SHOW_BLACKOUT_SCREEN:

		def ShowDeathScreen(self):
			if app.ENABLE_DEATH_EFFECT and app.IsDeathEffectInitialized():
				app.SetDeathEffectActive(1)
				app.SetDeathEffectIntensity(0.0)
				app.SetDeathEffectVignette(0.45)
				app.SetDeathEffectChromatic(0.4)

			# Create widgets if not already present
			if not hasattr(self, "deathScreenOverlay"):
				self.deathScreenOverlay = ui.Bar()
				self.deathScreenOverlay.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())
				if app.ENABLE_WINDOW_RESIZE:
					self.deathScreenOverlay.SetResizeDic({"size" : (Expr("SCREEN_WIDTH"), Expr("SCREEN_HEIGHT"))})
				self.deathScreenOverlay.SetPosition(0, 0)
				self.deathScreenOverlay.AddFlag("not_pick")
				self.deathScreenOverlay.AddFlag("float")

			if not hasattr(self, "deathScreenImage"):
				self.deathScreenImage = ui.ExpandedImageBox()
				self.deathScreenImage.AddFlag("float")
				self.deathScreenImage.LoadImage("d:/ymir work/ui/dead_overlay.png")
				if app.ENABLE_WINDOW_RESIZE:
					self.deathScreenImage.SetResizeDic({"position" : ((Expr("SCREEN_WIDTH") - self.deathScreenImage.GetWidth())/2, 50)})
				self.deathScreenImage.SetPosition(
					(wndMgr.GetScreenWidth() - self.deathScreenImage.GetWidth()) / 2,
					50
				)

			# Reset animation state
			self._deathPhase = "fadein"
			self._deathFadeSpeed = 0.012
			self._deathLUTStrength = 0.0
			self._deathImageAlpha = 0.0
			self._deathImageFadeInDone = False
			self._deathImageHoldEnd = 0.0
			self._deathHiding = False
			self._deathHeartbeatInterval = 2.0
			self._deathNextHeartbeat = app.GetGlobalTime() + self._deathHeartbeatInterval

			# Image starts invisible; fades in later
			self.deathScreenImage.SetDiffuseColor(1.0, 1.0, 1.0, 0.0)
			self.deathScreenImage.Show()

			# First heartbeat and hook per-frame update
			snd.PlaySound("sound/ui/heartbeat.wav")
			if not hasattr(self, "_oldOnUpdate"):
				self._oldOnUpdate = self.OnUpdate
				self.OnUpdate = self.DeathScreenOnUpdateWrapper

		def BINARY_HideDeathScreen(self):
			self.HideDeathScreen()

		def BINARY_ClickEventTrigger(self):
			net.SendRequestEventQuest("click_npc_event")

		def HideDeathScreen(self):
			if hasattr(self, "_deathLUTStrength") and self._deathLUTStrength > 0.0:
				self._deathHiding = True
			else:
				self._DeathScreenCleanup()

		def DeathScreenOnUpdateWrapper(self):
			# Always call original update first
			if hasattr(self, "_oldOnUpdate"):
				self._oldOnUpdate()

			# Pulsing heartbeat (stops when hide begins)
			if not self._deathHiding:
				now = app.GetGlobalTime()
				if now >= self._deathNextHeartbeat:
					snd.PlaySound("sound/ui/heartbeat.wav")
					self._deathHeartbeatInterval = min(self._deathHeartbeatInterval + 0.3, 5.0)
					self._deathNextHeartbeat = now + self._deathHeartbeatInterval

			# Handle hide fade-out
			if self._deathHiding:
				self._deathLUTStrength -= 0.012
				if self._deathLUTStrength <= 0.0:
					self._deathLUTStrength = 0.0
				if app.ENABLE_DEATH_EFFECT and app.IsDeathEffectInitialized():
					app.SetDeathEffectIntensity(self._deathLUTStrength)
				if self._deathLUTStrength <= 0.0:
					self._DeathScreenCleanup()
				return

			# Phase state machine
			if self._deathPhase == "fadein":
				self._deathLUTStrength += self._deathFadeSpeed
				if self._deathLUTStrength >= 1.0:
					self._deathLUTStrength = 1.0
					self._deathPhase = "image_fadein"
				if app.ENABLE_DEATH_EFFECT and app.IsDeathEffectInitialized():
					app.SetDeathEffectIntensity(self._deathLUTStrength)

			elif self._deathPhase == "image_fadein":
				self._deathImageAlpha += 0.005
				if self._deathImageAlpha >= 1.0:
					self._deathImageAlpha = 1.0
					self._deathImageHoldEnd = app.GetGlobalTime() + 3.0
					self._deathPhase = "hold"
				self.deathScreenImage.SetDiffuseColor(1.0, 1.0, 1.0, self._deathImageAlpha)

			elif self._deathPhase == "hold":
				if app.GetGlobalTime() >= self._deathImageHoldEnd:
					self._deathPhase = "image_fadeout"

			elif self._deathPhase == "image_fadeout":
				self._deathImageAlpha -= 0.003
				if self._deathImageAlpha <= 0.0:
					self._deathImageAlpha = 0.0
					self.deathScreenImage.Hide()
					self._deathPhase = "idle"
				self.deathScreenImage.SetDiffuseColor(1.0, 1.0, 1.0, self._deathImageAlpha)

	def _DeathScreenCleanup(self):
		if app.ENABLE_DEATH_EFFECT and app.IsDeathEffectInitialized():
			app.SetDeathEffectIntensity(0.0)
			app.SetDeathEffectActive(0)
		if hasattr(self, "deathScreenOverlay"):
			self.deathScreenOverlay.Hide()
			del self.deathScreenOverlay
		if hasattr(self, "deathScreenImage"):
			self.deathScreenImage.Hide()
			del self.deathScreenImage
		if hasattr(self, "_oldOnUpdate"):
			self.OnUpdate = self._oldOnUpdate
			del self._oldOnUpdate
		for attr in ("_deathPhase", "_deathFadeSpeed", "_deathLUTStrength",
		             "_deathImageAlpha", "_deathImageFadeInDone",
		             "_deathImageHoldEnd", "_deathHiding",
		             "_deathHeartbeatInterval", "_deathNextHeartbeat"):
			if hasattr(self, attr):
				delattr(self, attr)

	def BINARY_SetBigMessage(self, message):
		self.interface.bigBoard.SetTip(message)

	def BINARY_SetTipMessage(self, message):
		self.interface.tipBoard.SetTip(message)

	def BINARY_ShowImportantPopup(self, message):
		if self.interface:
			self.interface.ShowImportantPopup(message)

	if app.ENABLE_NOTIFICATION_SYSTEM:
		def BINARY_NotificationReceived(self, notifType, itemVnum, itemCount, iconPath, title, message):
			"""
			Callback from C++ when a notification packet is received from server.
			Forwards the notification to the interface module for display.
			"""
			if self.interface:
				self.interface.OnNotificationReceived(notifType, itemVnum, itemCount, iconPath, title, message)

	if app.ENABLE_12ZI:
		def BINARY_SetMissionMessage(self, message):
			if self.interface.DungeonHudMission(message):
				return
			self.interface.missionBoard.SetMission(message)

		def BINARY_SetSubMissionMessage(self, message):
			if self.interface.DungeonHudSubMission(message):
				return
			self.interface.missionBoard.SetSubMission(message)

		def BINARY_CleanMissionMessage(self):
			if self.interface.DungeonHudCleanMission():
				return
			self.interface.missionBoard.CleanMission()

	if app.ENABLE_HIDE_COSTUME_SYSTEM:
		def SetBodyCostumeHidden(self, hidden):
			osfinfo.HIDDEN_BODY_COSTUME = int(hidden)
			self.interface.RefreshVisibleCostume()

		def SetHairCostumeHidden(self, hidden):
			osfinfo.HIDDEN_HAIR_COSTUME = int(hidden)
			self.interface.RefreshVisibleCostume()

		def SetAcceCostumeHidden(self, hidden):
			if app.USE_ACCE_SYSTEM:
				osfinfo.HIDDEN_ACCE_COSTUME = int(hidden)
				self.interface.RefreshVisibleCostume()
			else:
				pass

		def SetAuraCostumeHidden(self, hidden):
			osfinfo.HIDDEN_AURA_COSTUME = int(hidden)
			self.interface.RefreshVisibleCostume()

		def SetWeaponCostumeHidden(self, hidden):
			if app.USE_WEAPON_COSTUME_SYSTEM:
				osfinfo.HIDDEN_WEAPON_COSTUME = int(hidden)
				self.interface.RefreshVisibleCostume()
			else:
				pass

		def SetMountSkinHidden(self, hidden):
			if app.USE_MOUNT_SKIN:
				osfinfo.HIDDEN_MOUNT_SKIN = int(hidden)
				self.interface.RefreshVisibleCostume()

		def SetPetSkinHidden(self, hidden):
			if app.USE_PET_SKIN:
				osfinfo.HIDDEN_PET_SKIN = int(hidden)
				self.interface.RefreshVisibleCostume()

		def SetAcceSkinHidden(self, hidden):
			if getattr(app, "USE_ACCE_SKIN", 0):
				osfinfo.HIDDEN_ACCE_SKIN = int(hidden)
				self.interface.RefreshVisibleCostume()

	if app.ENABLE_HIDE_SHINING_SYSTEM:
		def SetShiningWeaponHidden(self, hidden):
			osfinfo.HIDDEN_SHINING_WEAPON = int(hidden)
			self.interface.RefreshVisibleShining()

		def SetShiningArmorHidden(self, hidden):
			osfinfo.HIDDEN_SHINING_ARMOR = int(hidden)
			self.interface.RefreshVisibleShining()

		def SetShiningSpecialHidden(self, hidden):
			osfinfo.HIDDEN_SHINING_SPECIAL = int(hidden)
			self.interface.RefreshVisibleShining()


	## EVENTS
	def __LateSummerEvent(self):
		EnvironmentData = {
			0:	"d:/ymir work/environment/late_summer.msenv",
			1:	"d:/ymir work/environment/late_summer.msenv",
			2:	"d:/ymir work/environment/late_summer.msenv",
			3:	"d:/ymir work/environment/late_summer.msenv",
			4:	"d:/ymir work/environment/late_summer.msenv",
			5:	"d:/ymir work/environment/late_summer.msenv",
			6:	"d:/ymir work/environment/late_summer.msenv",
			7:	"d:/ymir work/environment/late_summer.msenv",
			8:	"d:/ymir work/environment/late_summer.msenv",
			9:	"d:/ymir work/environment/late_summer.msenv",
			10:	"d:/ymir work/environment/late_summer.msenv",
			11:	"d:/ymir work/environment/late_summer.msenv",
			12:	"d:/ymir work/environment/late_summer.msenv",
			13:	"d:/ymir work/environment/late_summer.msenv",
			14:	"d:/ymir work/environment/late_summer.msenv",
			15:	"d:/ymir work/environment/late_summer.msenv",
			16:	"d:/ymir work/environment/late_summer.msenv",
			17:	"d:/ymir work/environment/late_summer.msenv",
			18:	"d:/ymir work/environment/late_summer.msenv",
			19:	"d:/ymir work/environment/late_summer.msenv",
			20:	"d:/ymir work/environment/late_summer.msenv",
			21:	"d:/ymir work/environment/late_summer.msenv",
			22:	"d:/ymir work/environment/late_summer.msenv",
			23:	"d:/ymir work/environment/late_summer.msenv",
		}

		hour = (app.GetGlobalTimeStamp() / 60) / 60 % 24
		for key, c_pszName in EnvironmentData.iteritems():
			if hour is key and app.IsExistFile(c_pszName):
				background.RegisterEnvironmentData(0, c_pszName)
				background.SetEnvironmentData(0)
	## END_OF_EVENTS

	def BINARY_RecieveWhisperDetails(self, name, country):
		if self.interface:
			self.interface.RecieveWhisperDetails(name, country)

	if app.ENABLE_12ZI:
		def BINARY_SetMissionMessage(self, message):
			if app.ENABLE_CHAT_MISSION_ALTERNATIVE:
				message = message.replace("_", " ")
			if self.interface.DungeonHudMission(message):
				return
			self.interface.missionBoard.SetMission(message)

		def BINARY_SetSubMissionMessage(self, message):
			if self.interface.DungeonHudSubMission(message):
				return
			self.interface.missionBoard.SetSubMission(message)

		def BINARY_CleanMissionMessage(self):
			if self.interface.DungeonHudCleanMission():
				return
			self.interface.missionBoard.CleanMission()

	def BINARY_AppendNotifyMessage(self, type, time = 0):
		#if app.USE_OFFLINESHOP_EXTENDED_SLOTS
		if type == "TRY_AGAIN_IN_MILLESECONDS":
			leftTime = float(time) / float(1000)
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.TRY_AGAIN_IN_MILLESECONDS % leftTime)
			return

		if not type in localeinfo.NOTIFY_MESSAGE:
			return

		chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.NOTIFY_MESSAGE[type])

	def BINARY_Guild_EnterGuildArea(self, areaID):
		self.interface.BULID_EnterGuildArea(areaID)

	def BINARY_Guild_ExitGuildArea(self, areaID):
		self.interface.BULID_ExitGuildArea(areaID)

	def BINARY_GuildWar_OnSendDeclare(self, guildID):
		pass

	def BINARY_GuildWar_OnRecvDeclare(self, guildID, warType):
		mainCharacterName = player.GetMainCharacterName()
		masterName = guild.GetGuildMasterName()
		if mainCharacterName == masterName:
			self.__GuildWar_OpenAskDialog(guildID, warType)

	def BINARY_GuildWar_OnRecvPoint(self, gainGuildID, opponentGuildID, point):
		self.interface.OnRecvGuildWarPoint(gainGuildID, opponentGuildID, point)

	def BINARY_GuildWar_OnStart(self, guildSelf, guildOpp):
		self.interface.OnStartGuildWar(guildSelf, guildOpp)

	def BINARY_GuildWar_OnEnd(self, guildSelf, guildOpp):
		self.interface.OnEndGuildWar(guildSelf, guildOpp)

	def BINARY_BettingGuildWar_SetObserverMode(self, isEnable):
		self.interface.BINARY_SetObserverMode(isEnable)

	def BINARY_BettingGuildWar_UpdateObserverCount(self, observerCount):
		self.interface.wndMiniMap.UpdateObserverCount(observerCount)

	if app.ENABLE_BIOLOG_SYSTEM:
		def BINARY_Biolog_Update(self, pLeftTime, pCountActual, pCountNeed, pVnum):
			uiprofessionalbiolog.BIOLOG_BINARY_LOADED["time"][0] = int(pLeftTime) + app.GetGlobalTimeStamp()
			uiprofessionalbiolog.BIOLOG_BINARY_LOADED["countActual"][0] = str(pCountActual)	
			uiprofessionalbiolog.BIOLOG_BINARY_LOADED["countNeed"][0] = str(pCountNeed)
			uiprofessionalbiolog.BIOLOG_BINARY_LOADED["vnum"][0] = int(pVnum)

		def BINARY_Biolog_SendMessage(self, pMessage):
			if str(pMessage) != "":
				self.wndBiologMessage = uicommon.PopupDialog()
				self.wndBiologMessage.SetWidth(350)
				self.wndBiologMessage.SetText((str(pMessage).replace("$"," ")))
				self.wndBiologMessage.Show()
			else:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "Error, i could not initialize message from server!")

		def BINARY_Biolog_PopUp(self, iRewardType, iRewardItem, iBonusName_1, iBonusValue_1, iBonusName_2, iBonusValue_2):
			self.wndBiologSlider = uiprofessionalbiolog.Biolog_FinishSlider()
			self.wndBiologSlider.BINARY_BiologPopUp_Load([str(iRewardType), int(iRewardItem), str(iBonusName_1), int(iBonusValue_1), str(iBonusName_2), int(iBonusValue_2)])
			self.wndBiologSlider.Show()

		def BINARY_Biolog_SelectReward(self, iTypeWindow, iRewardType, iBonusName_1, iBonusValue_1, iBonusName_2, iBonusValue_2, iBonusName_3, iBonusValue_3):
			self.wndBiologSelectReward = uiprofessionalbiolog.Biolog_SelectReward()
			self.wndBiologSelectReward.Open_SelectRewardType([int(iTypeWindow), str(iRewardType), str(iBonusName_1), int(iBonusValue_1), str(iBonusName_2), int(iBonusValue_2), str(iBonusName_3), int(iBonusValue_3)])
			self.wndBiologSelectReward.SetTitle((str(iRewardType).replace("$"," ")))
			self.wndBiologSelectReward.SetCenterPosition()
			self.wndBiologSelectReward.SetTop()
			self.wndBiologSelectReward.Show()



	def __GuildWar_UpdateMemberCount(self, guildID1, memberCount1, guildID2, memberCount2, observerCount):
		guildID1 = int(guildID1)
		guildID2 = int(guildID2)
		memberCount1 = int(memberCount1)
		memberCount2 = int(memberCount2)
		observerCount = int(observerCount)

		self.interface.UpdateMemberCount(guildID1, memberCount1, guildID2, memberCount2)
		self.interface.wndMiniMap.UpdateObserverCount(observerCount)

	def __GuildWar_OpenAskDialog(self, guildID, warType):
		guildName = guild.GetGuildName(guildID)

		# REMOVED_GUILD_BUG_FIX
		if "Noname" == guildName:
			return
		# END_OF_REMOVED_GUILD_BUG_FIX

		import uiguild
		questionDialog = uiguild.AcceptGuildWarDialog()
		questionDialog.SAFE_SetAcceptEvent(self.__GuildWar_OnAccept)
		questionDialog.SAFE_SetCancelEvent(self.__GuildWar_OnDecline)
		questionDialog.Open(guildName, warType)

		self.guildWarQuestionDialog = questionDialog

	def __GuildWar_CloseAskDialog(self):
		self.guildWarQuestionDialog.Close()
		self.guildWarQuestionDialog = None

	def __GuildWar_OnAccept(self):
		guildName = self.guildWarQuestionDialog.GetGuildName()

		net.SendChatPacket("/war " + guildName)
		self.__GuildWar_CloseAskDialog()

		return 1

	def __GuildWar_OnDecline(self):
		guildName = self.guildWarQuestionDialog.GetGuildName()

		net.SendChatPacket("/nowar " + guildName)
		self.__GuildWar_CloseAskDialog()

		return 1

	## BINARY CALLBACK
	######################################################################################
	if app.USE_SHIP_DEFENSE:
		def BINARY_Update_Mast_Window(self, isON):
			if self.interface:
				self.interface.BINARY_Update_Mast_Window(isON)

		def BINARY_Update_Mast_HP(self, hp, maxhp):
			if self.interface:
				self.interface.BINARY_Update_Mast_HP(long(hp), long(maxhp))

	if app.ENABLE_CAPTCHA_SYSTEM or app.USE_CAPTCHA_IMPRISONMENT:
		def CaptchaDone(self):
			if self.wndCaptcha:
				self.wndCaptcha.Close()

		def CaptchaOrder(self):
			if self.wndCaptcha:
				self.wndCaptcha.Order()

	def __OfflineShopDormant(self, count = 0):
		self.interface.OnOfflineShopDormant(count)

	def __MineTimer(self, vid, remaining, curOre, maxOre):
		import uimine
		uimine.OnMineTimer(int(vid), int(remaining), int(curOre), int(maxOre))

	def __MineTally(self, vid, tally, perHit):   # v5 line 2: digger's running ore total + per-hit value
		import uimine
		uimine.OnMineTally(int(vid), int(tally), int(perHit))

	def __BuffiInt(self, summoned, intValue):
		import constinfo
		constinfo.BUFFI_SUMMONED = int(summoned)
		constinfo.BUFFI_TOOLTIP_INT = int(intValue)

	def __FishCombat(self, state):
		shower = getattr(self, "affectShower", None)
		if shower:
			shower.SetFishCombatState(int(state))

	def __CompanionOpen(self):
		if app.__BUFFI_SUPPORT__ and self.interface:
			self.interface.ToggleCompanion()

	def __BuffiNameInput(self, cell):
		if app.__BUFFI_SUPPORT__ and self.interface:
			self.interface.OpenBuffiNameDialog(int(cell))

	def __BundleBoxOpen(self, payload):
		if self.interface:
			self.interface.BundleBoxFeed(payload)

	def __BundleBoxDone(self):
		if self.interface:
			self.interface.BundleBoxDone()

	def __AutoChest(self, payload):
		constinfo.AUTO_CHEST_ACTIVE = 1

		deadlines = {}
		for pair in payload.split("|"):
			parts = pair.split(":")
			if len(parts) != 2:
				continue
			try:
				deadlines[int(parts[0])] = int(parts[1])
			except (TypeError, ValueError):
				continue

		constinfo.AUTO_CHEST_DEADLINES = deadlines

	if app.USE_DUNGEON_INFO:
		def __DgnStatBase(self, first, pairs):
			if self.interface:
				self.interface.RecvDungeonStatBase(first, pairs)

		def __DgnStatRefund(self, left, maxCount):
			if self.interface:
				self.interface.RecvDungeonStatRefund(left, maxCount)

		def __DgnStatReset(self, secs):
			if self.interface:
				self.interface.RecvDungeonStatReset(secs)

		def __DgnBossContrib(self, vid, pct, threshold):
			if self.interface:
				self.interface.RecvDungeonBossContrib(vid, pct, threshold)

		def __DgnRankPos(self, num, pos):
			if self.interface:
				self.interface.RecvDungeonRankPos(num, pos)

	def __ServerCommand_Build(self):
		serverCommandList = {
			"ConsoleEnable" : self.__Console_Enable,
			"DayMode" : self.__DayMode_Update,
			"PRESERVE_DayMode" : self.__PRESERVE_DayMode_Update,
			"CloseRestartWindow" : self.__RestartDialog_Close,
			"OpenPrivateShop" : self.__PrivateShop_Open,
			"OfflineShopDormant" : self.__OfflineShopDormant,
			"MineTimer" : self.__MineTimer,
			"MineTally" : self.__MineTally,
			"BuffiInt" : self.__BuffiInt,
			"CompanionOpen" : self.__CompanionOpen,
			"FishCombat" : self.__FishCombat,
			"BuffiNameInput" : self.__BuffiNameInput,
			"PartyHealReady" : self.PartyHealReady,
			"ShowMeSafeboxPassword" : self.AskSafeboxPassword,
			"CloseSafebox" : self.CommandCloseSafebox,
			"DSSetBonus" : self.__OnDragonSoulSetBonus,
			"QuickSellResult" : self.__OnQuickSellResult,

			# ITEM_MALL
			"CloseMall" : self.CommandCloseMall,
			"ShowMeMallPassword" : self.AskMallPassword,
			"item_mall" : self.__ItemMall_Open,
			# END_OF_ITEM_MALL

			"ruhtasiekranac"		: self.ruhcac,#by dream
			"RefineSuceeded" : self.RefineSuceededMessage,
			"RefineFailed" : self.RefineFailedMessage,
			"xmas_snow" : self.__XMasSnow_Enable,
			"xmas_boom" : self.__XMasBoom_Enable,
			"xmas_song" : self.__XMasSong_Enable,
			"xmas_tree" : self.__XMasTree_Enable,
			"newyear_boom" : self.__XMasBoom_Enable,
			"PartyRequest" : self.__PartyRequestQuestion,
			"PartyRequestDenied" : self.__PartyRequestDenied,
			"horse_state" : self.__Horse_UpdateState,
			"hide_horse_state" : self.__Horse_HideState,
			"WarUC" : self.__GuildWar_UpdateMemberCount,
			"test_server" : self.__EnableTestServerFlag,
			"mall" : self.__InGameShop_Show,

			# PROFESSIONAL_BIOLOG_SYSTEM
			"BINARY_Biolog_Update"	:	self.BINARY_Biolog_Update,
			"BINARY_Biolog_SendMessage"	:	self.BINARY_Biolog_SendMessage,	
			"BINARY_Biolog_PopUp"	:	self.BINARY_Biolog_PopUp,
			"BINARY_Biolog_SelectReward"	:	self.BINARY_Biolog_SelectReward,
			# END_OF_PROFESSIONAL_BIOLOG_SYSTEM	

			# WEDDING
			"lover_login" : self.__LoginLover,
			"lover_logout" : self.__LogoutLover,
			"lover_near" : self.__LoverNear,
			"lover_far" : self.__LoverFar,
			"lover_divorce" : self.__LoverDivorce,
			"PlayMusic" : self.__PlayMusic,
			# END_OF_WEDDING
			# PRIVATE_SHOP_PRICE_LIST
			"MyShopPriceList" : self.__PrivateShop_PriceList,
			# END_OF_PRIVATE_SHOP_PRICE_LIST
			"GET_INPUT_BEGIN" 	: self.GetInputBegin,
			"GET_INPUT_END" 	: self.GetInputEnd,

			"BundleBoxOpen" : self.__BundleBoxOpen,
			"BundleBoxDone" : self.__BundleBoxDone,
			"AutoChest" : self.__AutoChest,
		}

		if app.ENABLE_PRIVATE_INSTANCE_LOBBY:
			serverCommandList["PILChaosEntryConfirm"] = self.__PILChaosEntryConfirm
			serverCommandList["PILChaosReturnAvail"]  = self.__PILChaosReturnAvail

		if app.ENABLE_PIL_DUNGEON:
			# stringcommander enforces exact argcount, so we register one
			# distinct command per verb (Start/Tick/Pause/Resume/Cancel/Done)
			# instead of a single dispatcher with a leading verb.
			serverCommandList["PILFastEnterStart"]  = self.__PILFastEnterStart
			serverCommandList["PILFastEnterTick"]   = self.__PILFastEnterTick
			serverCommandList["PILFastEnterPause"]  = self.__PILFastEnterPause
			serverCommandList["PILFastEnterResume"] = self.__PILFastEnterResume
			serverCommandList["PILFastEnterCancel"] = self.__PILFastEnterCancel
			serverCommandList["PILFastEnterCancelName"] = self.__PILFastEnterCancelName
			serverCommandList["PILFastEnterDone"]   = self.__PILFastEnterDone

		if app.USE_PORTABLE_TELEPORT_WITH_UI:
			serverCommandList["OpenTeleportWindow"] = self.__OpenTeleportWindow

		if app.ENABLE_CAPTCHA_SYSTEM and app.USE_CAPTCHA_IMPRISONMENT:
			serverCommandList["captcha_done"] = self.CaptchaDone
			serverCommandList["captcha_order"] = self.CaptchaOrder

		if app.ENABLE_CAPTCHA_REWORK:
			serverCommandList["captcha_done"] = self.CaptchaDone

		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			serverCommandList["BINARY_AutoDS"] = self.interface.BINARY_AutoDS

		if app.ENABLE_GEM_SYSTEM:
			serverCommandList.update({
				"OpenGuiGem" : self.OpenGuiGem,
				"GemCheck" : self.GemCheck,
				"OpenGuiGemMarket" : self.OpenGuiGemMarket,
				"GemMarketSlotsDesblock" : self.GemMarketSlotsDesblock,
				"GemMarketItems" : self.GemMarketItems,
				"GemMarketClear" : self.GemMarketClear,
				"GemMarketTime" : self.GemTimeMarket,
			})
		if app.ENABLE_12ZI:
			serverCommandList.update({
				"SetMissionMessage" : self.BINARY_SetMissionMessage,
				"SetSubMissionMessage" : self.BINARY_SetSubMissionMessage,
				"CleanMissionMessage" : self.BINARY_CleanMissionMessage,
			})
		
		if app.ENABLE_HIDE_COSTUME_SYSTEM:
			serverCommandList.update({
				"SetBodyCostumeHidden" : self.SetBodyCostumeHidden,
				"SetHairCostumeHidden" : self.SetHairCostumeHidden,
				"SetAcceCostumeHidden" : self.SetAcceCostumeHidden,
				"SetWeaponCostumeHidden" : self.SetWeaponCostumeHidden,
				"SetAuraCostumeHidden" : self.SetAuraCostumeHidden,
				"SetMountSkinHidden" : self.SetMountSkinHidden,
				"SetPetSkinHidden" : self.SetPetSkinHidden,
				"SetAcceSkinHidden" : self.SetAcceSkinHidden,
			})
		if app.ENABLE_HIDE_SHINING_SYSTEM:
			serverCommandList.update({
				"SetShiningWeaponHidden" : self.SetShiningWeaponHidden,
				"SetShiningArmorHidden" : self.SetShiningArmorHidden,
				"SetShiningSpecialHidden" : self.SetShiningSpecialHidden,
			})
		if app.ENABLE_EXPRESSING_EMOTION:
			serverCommandList.update({
				"RegisterSpecialEmotion" : self.RegisterSpecialEmotion,
				"ClearSpecialEmotions" : self.ClearSpecialEmotions,
			})

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			serverCommandList.update({
				"OpenSpecialInventoryWindow" : self.OpenSpecialInventoryWindow,
			})

		serverCommandList.update({
			"OpenCostumeWindow" : self.OpenCostumeWindow,
		})

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			serverCommandList["ShowChangeDialog"] = self.__ChangeWindowOpen

		if app.ENABLE_SOUL_SYSTEM:
			serverCommandList["RefineSoulSuceeded"] = self.__RefineSoulSuceededMessage
			serverCommandList["RefineSoulFailed"] = self.__RefineSoulFailedMessage

		if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
			serverCommandList["OpenSkillbookCombinationDialog"] = self.OpenSkillbookCombinationDialog

		if app.ENABLE_MYSHOP_DECO:
			serverCommandList["OpenMyShopDecoWnd"] = self.__OpenMyShopDecoWnd

		if app.ENABLE_12ZI:
			serverCommandList["NextFloorButton"]			= self.Show12ziJumpButton
			serverCommandList["OpenUI12zi"]					= self.OpenUI12zi

		if app.ENABLE_FEATURES_OXEVENT:
			serverCommandList["BINARY_OxEvent_Window"] = self.BINARY_OxEvent_Window

		if app.ENABLE_RENEWAL_PVP:
			serverCommandList["OpenPvPWindow"] = self.interface.OpenPvPSecond

		if app.ENABLE_MULTIFARM_BLOCK:
			serverCommandList["UpdateMultiFarmAffect"] = self.UpdateMultiFarmAffect
			serverCommandList["UpdateMultiFarmPlayer"] = self.UpdateMultiFarmPlayer

		if app.ENABLE_SOLO_LEADERSHIP_BONUS:
			serverCommandList["LeadershipBonus"] = self.__OnSoloLeadershipBonus

		if app.ENABLE_GUILD_FINDER:
			serverCommandList["OpenGuildRequest"] = self.__OpenGuildFinder

		serverCommandList["PvpOrder"] = self.__OnPvpOrder

		if app.ENABLE_PVP_ROUTES:
			serverCommandList["PVPROUTES"] = self.ManagerRoutesPvPSystem

		if app.ENABLE_ASLAN_TELEPORTPANEL:
			serverCommandList["teleportpanel"] = self.TeleportReciveQuestCommand
		
		if app.ENABLE_ULTIMATE_REGEN:
			serverCommandList["TrackBossInfo"] = self.interface.TrackBossInfo

		if getattr(app, "ENABLE_CURSED_BOSS", 0):
			serverCommandList["CursedAtlas"] = self.interface.OnCursedAtlas
			serverCommandList["CursedHud"] = self.interface.OnCursedHud
			serverCommandList["CursedHudEnd"] = self.interface.OnCursedHudEnd

		if app.ENABLE_ITEMSHOP:
			serverCommandList.update({"SetItemData" : self.interface.SetWheelItemData})
			serverCommandList.update({"OnSetWhell" : self.interface.OnSetWhell})
			serverCommandList.update({"GetGiftData" : self.interface.GetWheelGiftData})
			serverCommandList.update({"update_dragon_coins" : self.OnUpdateDragonCoins})
			serverCommandList.update({"ItemShopAppendLog" : self.ItemShopAppendLogEx})
			serverCommandList.update({"PrizeProgress" : self.interface.RecvPrizeProgress})
			serverCommandList.update({"ItemShopUsage" : self.BINARY_ItemShopUsage})
			serverCommandList.update({"ItemShopGlobalUsage" : self.BINARY_ItemShopGlobalUsage})
			# Wheel of Fortune "Rewards & Chances" odds panel (server: USE_WHEEL_OF_FORTUNE).
			serverCommandList.update({"WheelOddsBegin" : self.interface.RecvWheelOddsBegin})
			serverCommandList.update({"WheelOddsTier" : self.interface.RecvWheelOddsTier})
			serverCommandList.update({"WheelOddsItem" : self.interface.RecvWheelOddsItem})
			serverCommandList.update({"WheelOddsPity" : self.interface.RecvWheelOddsPity})
			serverCommandList.update({"WheelOddsEnd" : self.interface.RecvWheelOddsEnd})

		# Title window push (CTitleManager::SendTitleWindow / SetActiveTitle).
		serverCommandList.update({"TitleWinBegin" : self.interface.RecvTitleWinBegin})
		serverCommandList.update({"TitleWinItem" : self.interface.RecvTitleWinItem})
		serverCommandList.update({"TitleWinEnd" : self.interface.RecvTitleWinEnd})
		serverCommandList.update({"TitleWinActive" : self.interface.RecvTitleWinActive})

		if app.ENABLE_MISSION_QUEST:
			serverCommandList.update({
				"MQ_UPDATE" : self.MissionQuestUpdate,
				"MQ_TABLE" : self.MissionQuestTable,
				"MQ_GENERAL" : self.MissionQuestGeneral,
				"MQ_REWARD" : self.MissionQuestReward,
				"MQ_SPIN_REWARD" : self.MissionQuestSpinReward,
				"MQ_REROLL_INFO" : self.MissionQuestRerollInfo,
				"MQ_CLAIM_LOCK" : self.MissionQuestClaimLock,
				"MQ_HISTORY" : self.MissionQuestHistory,
				"MQ_HISTORY_PAGE" : self.MissionQuestHistoryPage,
				})

		if getattr(app, "ADVANCED_BATTLE_PASS", 0):
			serverCommandList.update({
				"BP_CLEAR" : self.BattlePassClear,
				"BP_ACTIVATED" : self.BattlePassActive,
				"BP_UPDATE" : self.BattlePassUpdate,
				"BP_EXP_UPDATE" : self.BattlePassExpUpdate,
				"BP_INFO" : self.BattlePassInfo,
				"BP_INFOR" : self.BattlePassInfoReward,
				"BP_INFOG" : self.BattlePassInfoGeneral,
				"BP_TIMES" : self.BattlePassSetTimes,
				"BP_SHOP_COIN" : self.ShowShopCoinBattlePass,
				"BP_EXP_TABLE" : self.BattlePassExpTable,
				})

		if app.ENABLE_SKILL_COLOR_SYSTEM:
			serverCommandList["skillcolor"] = self.UpdateSkillColorIcon

		if app.USE_PVP_TOURNAMENT:
			serverCommandList["open_pvptournament_ui"] = self.interface.TogglePvpTournamentAdminTrue

			if app.PVP_HAVE_GUI:
				serverCommandList["add_pvp_tournament_fight"] = self.interface.AddPvpTournamentFight
				serverCommandList["reload_pvp_tournament_fight"] = self.interface.ReloadPvpTournamentFight
				serverCommandList["cache_pvp_tournament_fight"] = self.interface.CachePvpTournamentFight
				serverCommandList["status_pvp_tournament_fight"] = self.interface.StatusPvpTournamentFight
				serverCommandList["hp_pvp_tournament_fight"] = self.interface.UpdateHPPvpTournament
				serverCommandList["score_pvp_tournament_fight"] = self.interface.UpdateScorePvpTournament
				serverCommandList["update_pvp_tournament_fight"] = self.interface.UpdatePvpTournament
				serverCommandList["clear_pvp_tournament_fight"] = self.interface.ClearPvpTournament

		if app.ENABLE_REWARD_SYSTEM:
			serverCommandList["RewardData"] = self.interface.RewardData
			serverCommandList["RewardDefs"] = self.interface.RewardDefs
			serverCommandList["RewardTargets"] = self.interface.RewardTargets
			serverCommandList["RewardWin"] = self.interface.RewardWin
			serverCommandList["ChallengeBoard"] = self.interface.ChallengeBoard
			serverCommandList["ChallengeProg"] = self.interface.ChallengeProg

		if app.__PENDANT__:
			serverCommandList.update({"SetPendantPageIdx" : self.interface.SetPendantPageIdx})

		if app.__AUTO_SKILL_READER__:
			serverCommandList.update({"AutoSkillStatus" : self.interface.AutoSkillStatus})
			serverCommandList.update({"AutoSkillProgress" : self.interface.AutoSkillProgress})
			serverCommandList.update({"AutoSkillHelper" : self.interface.AutoSkillHelper})

		if app.__SKILL_TREE__:
			serverCommandList.update({
				"SkillTreeLoad" : self.interface.SkillTreeLoad,
				"SkillTreeSetTime" : self.interface.SkillTreeSetTime,
				"SkillTreeSetLevel" : self.interface.SkillTreeSetLevel,
				})

		if app.__RENEWAL_BRAVE_CAPE__:
			serverCommandList["SetBraveCapeStatus"] = self.SetBraveCapeStatus

		if app.WHEEL_INGAME:
			serverCommandList.update({"SpinReward" : self.SpinReward})
			serverCommandList.update({"SetPercentage" : self.SetSpinWheel})

		if app.ENABLE_ATTR_6TH_7TH:
			serverCommandList["__OpenAttr67AddDlg"] = self.__OpenAttr67AddDlg

		if app.ENABLE_DAILY_ALCHEMY_ORE:
			# >>> DAILY_ALCHEMY_ORE: replaced legacy spin-wheel registrations
			#serverCommandList["SetSpinReward"] = self.interface.SetSpinReward
			#serverCommandList["SetSpinWheel"] = self.interface.SetSpinWheel
			serverCommandList["SetAlchemyOre"] = self.interface.SetAlchemyOre
			serverCommandList["SetAlchemyRewards"] = self.interface.SetAlchemyRewards
			serverCommandList["SetAlchemyResult"] = self.interface.SetAlchemyResult
			# <<< DAILY_ALCHEMY_ORE

		if app.__SPIN_WHEEL_DUNGEON__:
			serverCommandList["SetDungeonSpinReward"] = self.interface.SetDungeonSpinReward
			serverCommandList["SetDungeonSpinWheel"] = self.interface.SetDungeonSpinWheel

		if app.USE_DUNGEON_INFO:
			serverCommandList["DgnStatBase"] = self.__DgnStatBase
			serverCommandList["DgnStatRefund"] = self.__DgnStatRefund
			serverCommandList["DgnStatReset"] = self.__DgnStatReset
			serverCommandList["DgnBossContrib"] = self.__DgnBossContrib
			serverCommandList["DgnRankPos"] = self.__DgnRankPos

		if app.USE_DUNGEON_INFO and app.USE_DUNGEON_INFO_ADDON_LEVEL_CAP:
			serverCommandList["DungeonInfoCapLevel"] = self.DungeonInfoCapLevel
			serverCommandList["DungeonInfoCapLevelEnd"] = self.DungeonInfoCapLevelEnd

		if app.USE_SHIP_DEFENSE:
			serverCommandList["BINARY_Update_Mast_Window"] = self.BINARY_Update_Mast_Window
			serverCommandList["BINARY_Update_Mast_HP"] = self.BINARY_Update_Mast_HP

		if app.ENABLE_AUTO_SHOUT:
			serverCommandList.update({"UpdateAutoShout" : self.interface.UpdateAutoShout})
			if app.ENABLE_AUTO_SHOUT_V2:
				serverCommandList.update({"AutoShoutInterval" : self.interface.SetAutoShoutInterval})

		if app.ENABLE_MAINTENANCE_SYSTEM:
			serverCommandList.update({"BINARY_Update_Maintenance" : self.BINARY_Update_Maintenance})


		#PITTY_REFINE
		serverCommandList["RefinePitty"] = self.RecvRefinePitty
		serverCommandList["RefineBonus"] = self.RecvRefineBonus
		#Wheel
		#serverCommandList["PrizeProgress"] = self.interface.RecvPrizeProgress
		#Coupon AdminPage
		serverCommandList["BINARY_Coupon_Window"] = self.BINARY_Coupon_Window
		if app.ENABLE_PARTY_WAR:
			# GameMaster Only
			serverCommandList["partywar_board"] = self.__PartyWarBoard
			serverCommandList["BINARY_partywar_Window"] = self.PartyWarBoardOpen
			# Player
			serverCommandList["partywar_time"] = self.__PartyWarTime
			serverCommandList["partywar_button"] = self.PartyWarButton
			
			# Player Board
			serverCommandList["PartyWarRank"] = self.interface.PartyWarRank
			serverCommandList["BINARY_PartyWarRank"] = self.OpenPartyWarRankWindow
			serverCommandList["PartyWarTimeData"] = self.interface.PartyWarTimeData

		serverCommandList["saryong_update"] = self.SaryongStoryUpdate
		serverCommandList["saryong_single_update"] = self.SaryongSingleUpdate
		serverCommandList["saryong_ranking"] = self.SaryongRanking

		if app.ENABLE_WORLDBOSS:
			serverCommandList["WBRankPage"] = self.__WBRankPage
			serverCommandList["WBRankEntry"] = self.__WBRankEntry
			serverCommandList["WBMyRank"] = self.__WBMyRank
			serverCommandList["WBDailyCap"] = self.__WBDailyCap
			serverCommandList["WBWeeklyTimer"] = self.__WBWeeklyTimer
			serverCommandList["WBBossSpawn"] = self.__WBBossSpawn
			serverCommandList["WBBossDied"] = self.__WBBossDied
			serverCommandList["GDRunAlert"] = self.__GDRunAlert
			serverCommandList["GDRunEnd"] = self.__GDRunEnd
			serverCommandList["WBBossConfig"] = self.__WBBossConfig

		if getattr(app, "ENABLE_WORLDBOSS_V3", 0):
			serverCommandList["WBPvPBlock"] = self.__WBPvPBlock
			serverCommandList["WBRewardRow"] = self.__WBRewardRow
			serverCommandList["WBRewardEnd"] = self.__WBRewardEnd
			serverCommandList["WBSpawnMode"] = self.interface.WBSpawnMode

		if app.ENABLE_WORLDBOSS_V2_DAMAGE_METER:
			serverCommandList["WBDmgMeter"] = self.WBDmgMeterHandler
			serverCommandList["WBDmgMeterTest"] = self.WBDmgMeterTestHandler
			if getattr(app, "ENABLE_WORLDBOSS_V3", 0):
				serverCommandList["WBEscrow"] = self.__WBEscrow

		serverCommandList["GDCfg"] = self.__GDDungeonCfg
		serverCommandList["GDTier"] = self.__GDDungeonTier
		serverCommandList["GDChest"] = self.__GDDungeonChest
		serverCommandList["GDTop"] = self.__GDDungeonTop
		serverCommandList["GDLive"] = self.__GDDungeonLive
		serverCommandList["GPFirst"] = self.__GPFirstCmd

		if app.USE_COSTUME_ATTR_TRANSFER:
			serverCommandList["attrtransfer_msg"] = self.BINARY_AttrTransferMessage

		if getattr(app, "USE_QUICK_ATTR_TRANSFER", 0):
			serverCommandList["QuickAttrTransfer"] = self.__QuickAttrTransferCommand

		if app.USE_BL_FISH_EVENT:
			serverCommandList["fish_event"] = self.__FishEvent

		if app.ENABLE_VOICE_CHAT:
			serverCommandList["voice_chat_disabled"] = self.__DisableVoiceChat
			serverCommandList["voice_chat_config"] = self.__ConfigVoiceChat

		if app.USE_NORTHWIND_DEEPS_DUNGEON:
			serverCommandList["nwd_timer"] = self.NorthWindDeeps_Timer
			serverCommandList["nwd_debuff"] = self.NorthWindDeeps_Debuff

		serverCommandList["DgnHudTimer"] = self.DungeonHudTimer
		serverCommandList["DgnHudOff"] = self.DungeonHudOff

		if app.SHOW_BLACKOUT_SCREEN:
			serverCommandList["HideDeathScreen"] = self.BINARY_HideDeathScreen

		serverCommandList["ClickEventTrigger"] = self.BINARY_ClickEventTrigger

		if app.ENABLE_GUILD_RENEWAL:
			serverCommandList["GMission"] = self.RecvGuildMission
			serverCommandList["GLv"] = self.RecvGuildLevelInfo
			serverCommandList["GPassive"] = self.RecvGuildPassiveInfo
			serverCommandList["open_guild_wnd"] = self.interface.OpenGuildWindow

		if app.ENABLE_COMBAT_POINTS:
			serverCommandList["CP_HIDE_STATE"] = self.__OnCPHideState

		if app.ENABLE_DROPINFO_REWORK:
			serverCommandList["DropInfo"] = self.RecvDropInfo


		serverCommandList["PvmBalanceInfo"] = self.RecvPvmBalanceInfo
		serverCommandList["PvmBalanceIntro"] = self.RecvPvmBalanceIntro
		serverCommandList["MessengerLastOnline"] = self.__MessengerLastOnline
		self.serverCommander = stringcommander.Analyzer()
		for serverCommandItem in serverCommandList.items():
			self.serverCommander.SAFE_RegisterCallBack(
				serverCommandItem[0], serverCommandItem[1]
			)

	def RecvPvmBalanceInfo(self, bound, level, grade, bonusA, bonusB):
		try:
			constinfo.PVM_BALANCE = {"bound":int(bound), "level":int(level), "grade":int(grade), "bonusA":int(bonusA), "bonusB":int(bonusB)}
		except:
			constinfo.PVM_BALANCE = {"bound":0, "level":0, "grade":0, "bonusA":0, "bonusB":0}
		constinfo.PVM_BALANCE_ACTIVE = 1
		if constinfo.PVM_BALANCE["bound"] != 0:
			self.interface.ClosePvmBalanceIntro()

	def RecvPvmBalanceIntro(self):
		self.interface.OpenPvmBalanceIntro()

	if app.ENABLE_SKILL_COLOR_SYSTEM:
		def UpdateSkillColorIcon(self, info):
			splittedInfo = info.split("#")
			
			for i in xrange(1, len(splittedInfo)):
				self.interface.wndCharacter.ShowSkillColorBtn(i - 1, int(splittedInfo[i]))

	if app.ENABLE_CHANGE_LOOK_SYSTEM:
		def __ChangeWindowOpen(self, type):
			self.interface.ChangeWindowOpen(type)
	if app.ENABLE_CUBE_RENEWAL_WORLDARD:
		def BINARY_CUBE_RENEWAL_OPEN(self):
			if self.interface:
				self.interface.BINARY_CUBE_RENEWAL_OPEN()

	def BINARY_ServerCommand_Run(self, line):
		#dbg.TraceError(line)
		try:
			#print " BINARY_ServerCommand_Run", line
			return self.serverCommander.Run(line)
		except RuntimeError, msg:
			dbg.TraceError(msg)
			return 0

	def __MessengerLastOnline(self, name, timestamp):
		if getattr(self, "interface", None):
			self.interface.OnMessengerLastOnline(name, timestamp)

	def __ProcessPreservedServerCommand(self):
		try:
			command = net.GetPreservedServerCommand()
			while command:
				print " __ProcessPreservedServerCommand", command
				self.serverCommander.Run(command)
				command = net.GetPreservedServerCommand()
		except RuntimeError, msg:
			dbg.TraceError(msg)
			return 0

	if app.WHEEL_INGAME:
		def BINARY_ClearSpinWheel(self):
			uispinwheel.REWARD_ITEMS = []
			uispinwheel.REWARD_COUNTS = []
			uispinwheel.REWARD_RARITIES = []

		def BINARY_AddSpinWheelResult(self, itemVnum, itemCount, rarity):
			uispinwheel.REWARD_ITEMS.append(itemVnum)
			uispinwheel.REWARD_COUNTS.append(itemCount)
			uispinwheel.REWARD_RARITIES.append(rarity)

		def BINARY_ShuffleList(self):
			combined = list(zip(uispinwheel.REWARD_ITEMS, uispinwheel.REWARD_COUNTS, uispinwheel.REWARD_RARITIES))
			random.shuffle(combined)
			ar1, ar2, ar3 = zip(*combined)
			uispinwheel.REWARD_ITEMS = list(ar1)
			uispinwheel.REWARD_COUNTS = list(ar2)
			uispinwheel.REWARD_RARITIES = list(ar3)

		def BINARY_StartSpinWheel(self, rewardVnum):
			osfinfo.rewardItem = rewardVnum
			if self.interface:
				self.interface.OpenSpin(rewardVnum)
			if self.wheelWindow:
				self.wheelWindow.Reset()

		def BINARY_AddSpinWheelReward(self, index, itemVNum, itemCount, rarity):
			# import dbg
			# dbg.TraceError("AddSpinWheelReward %s %s %s %s" % (index, itemVNum, itemCount, rarity))
			uispinwheel.REWARDS_ITEMS[index].append(itemVNum)
			uispinwheel.REWARDS_COUNTS[index].append(itemCount)
			uispinwheel.REWARDS_RARITIES[index].append(rarity)

		def SpinReward(self):
			if self.interface:
				self.interface.SpinReward()
			if self.wheelWindow:
				self.wheelWindow.PopupReward()
				self.wheelWindow.Reset()

		def SetSpinWheel(self, arg):
			count = int(arg)
			osfinfo.WHEEL_METINSTONE_COUNT = count
			if self.wheelWindow:
				self.wheelWindow.UpdatePercentage(count)

	#PITTY_REFINE
	def RecvRefinePitty(self, itemVnum, pittyValue, pittyMax):
		self.interface.dlgRefineNew.SetPittyInfo(int(itemVnum), int(pittyValue), int(pittyMax))

	def RecvRefineBonus(self, prob):
		fn = getattr(self.interface.dlgRefineNew, "SetRefineBonus", None)
		if fn:
			fn(int(prob))

	def PartyHealReady(self):
		self.interface.PartyHealReady()

	def AskSafeboxPassword(self):
		self.interface.AskSafeboxPassword()

	if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
		def OpenSkillbookCombinationDialog(self):
			self.interface.OpenSkillbookCombinationDialog()

	# ITEM_MALL
	def AskMallPassword(self):
		self.interface.AskMallPassword()

	def __ItemMall_Open(self):
		self.interface.OpenItemMall();

	def CommandCloseMall(self):
		self.interface.CommandCloseMall()
	# END_OF_ITEM_MALL

	if app.ENABLE_ASLAN_TELEPORTPANEL:
		def TeleportReciveQuestCommand(self, command):
			self.interface.ReceiveTeleportQuestCommand(command)

	def RefineSuceededMessage(self):
		snd.PlaySound("sound/ui/make_soket.wav")
		self.PopupMessage(localeinfo.REFINE_SUCCESS)
		if app.ENABLE_AUTO_REFINE:
			self.interface.RefineFail(False)

	def RefineFailedMessage(self):
		snd.PlaySound("sound/ui/jaeryun_fail.wav")
		self.PopupMessage(localeinfo.REFINE_FAILURE)
		if app.ENABLE_AUTO_REFINE:
			self.interface.RefineFail(True)

	if app.ENABLE_SOUL_SYSTEM:
		def __RefineSoulSuceededMessage(self):
			snd.PlaySound("sound/ui/make_soket.wav")
			self.PopupMessage(localeinfo.SOUL_REFINE_SUCCESS)

		def __RefineSoulFailedMessage(self):
			snd.PlaySound("sound/ui/jaeryun_fail.wav")
			self.PopupMessage(localeinfo.SOUL_REFINE_FAILURE)

	if app.ENABLE_REFINE_FAIL_TYPE:
		def BINARY_RefineFailedTypeMessage(self, type):
			REFINE_FAILURE_DICT = {
				player.REFINE_FAIL_GRADE_DOWN : localeinfo.REFINE_FAILURE_GRADE_DOWN,
				player.REFINE_FAIL_DEL_ITEM : localeinfo.REFINE_FAILURE_DEL_ITEM,
				player.REFINE_FAIL_KEEP_GRADE : localeinfo.REFINE_FAILURE_KEEP_GRADE,
				player.REFINE_FAIL_MAX : localeinfo.REFINE_FAILURE
			}

			snd.PlaySound("sound/ui/jaeryun_fail.wav")
			self.PopupMessage(REFINE_FAILURE_DICT.get(type, player.REFINE_FAIL_MAX))
			if app.ENABLE_AUTO_REFINE:
				self.interface.RefineFail(True)

	def CommandCloseSafebox(self):
		self.interface.CommandCloseSafebox()

	# PRIVATE_SHOP_PRICE_LIST
	def __PrivateShop_PriceList(self, itemVNum, itemPrice):
		if app.ENABLE_CHEQUE_SYSTEM:
			return
		else:
			uiprivateshopbuilder.SetPrivateShopItemPrice(itemVNum, itemPrice)
	# END_OF_PRIVATE_SHOP_PRICE_LIST

	def __Horse_HideState(self):
		self.affectShower.SetHorseState(0, 0, 0)

	def __Horse_UpdateState(self, level, health, battery):
		self.affectShower.SetHorseState(int(level), int(health), int(battery))

	if app.ENABLE_CONQUEROR_LEVEL:
		def BINARY_SungMaAttr(self, str, hp, move, immune):
			self.affectShower.SetSungMaAffectImage(str, hp, move, immune)

	def __IsXMasMap(self):
		mapDict = (
			"metin2_map_n_flame_01",
			"metin2_map_n_desert_01",
			"metin2_map_spiderdungeon_01",
			"metin2_map_spiderdungeon_02",
			"metin2_map_spiderdungeon_03",
			"metin2_map_deviltower1",
			"metin2_map_sungzi_flame_hill_01",
			"metin2_map_sungzi_flame_hill_02",
			"metin2_map_sungzi_flame_hill_03",
			"metin2_map_sungzi_desert_01",
			"metin2_map_sungzi_desert_hill_01",
			"metin2_map_sungzi_desert_hill_02",
			"metin2_map_sungzi_desert_hill_03",
			"metin2_map_empirewar03",
			"metin2_map_devilsCatacomb",
			"metin2_map_Mt_Thunder",
			"metin2_map_n_flame_dungeon_01",
			"metin2_map_dawnmist_dungeon_01",
			"metin2_map_Mt_Th_dungeon_01",
			"plechito_pyramide_dungeon",
		)

		if background.GetCurrentMapName() in mapDict:
			return False

		return True

	def __XMasSnow_Enable(self, mode):
		self.__XMasSong_Enable(mode)

		if "1" == mode:
			if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
				background.SetXMasShowEvent(1)

			if not self.__IsXMasMap():
				return

			print "XMAS_SNOW ON"
			background.EnableSnow(1)
		else:
			if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
				background.SetXMasShowEvent(0)

			print "XMAS_SNOW OFF"
			background.EnableSnow(0)

	def __XMasBoom_Enable(self, mode):
		if "1" == mode:
			if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
				if not background.IsBoomMap():
					return
			else:
				if not self.__IsXMasMap():
					return

			print "XMAS_BOOM ON"
			self.__DayMode_Update("dark")
			self.enableXMasBoom = True
			self.startTimeXMasBoom = app.GetTime()
		else:
			print "XMAS_BOOM OFF"
			self.__DayMode_Update("light")
			self.enableXMasBoom = False

	def __XMasTree_Enable(self, grade):
		print "XMAS_TREE ", grade
		background.SetXMasTree(int(grade))

	def __XMasSong_Enable(self, mode):
		if "1" == mode:
			print "XMAS_SONG ON"

			XMAS_BGM = "xmas.mp3"

			if app.IsExistFile("BGM/" + XMAS_BGM) == 1:
				if musicinfo.fieldMusic != "":
					snd.FadeOutMusic("BGM/" + musicinfo.fieldMusic)

				musicinfo.fieldMusic = XMAS_BGM
				snd.FadeInMusic("BGM/" + musicinfo.fieldMusic)
		else:
			print "XMAS_SONG OFF"

			if musicinfo.fieldMusic != "":
				snd.FadeOutMusic("BGM/" + musicinfo.fieldMusic)

			musicinfo.fieldMusic = musicinfo.METIN2THEMA
			snd.FadeInMusic("BGM/" + musicinfo.fieldMusic)

	def __RestartDialog_Close(self):
		self.interface.CloseRestartDialog()

	def __Console_Enable(self):
		self.consoleEnable = True
		app.EnableSpecialCameraMode()
		ui.EnablePaste(True)
		self.ShowConsole()

	## PrivateShop
	def __PrivateShop_Open(self):
		self.interface.OpenPrivateShopInputNameDialog()

	if app.ENABLE_MYSHOP_DECO:
		def MyPrivShopOpen(self, cashItem, tabCnt):
			self.interface.OpenPrivateShopInputNameDialog(cashItem, tabCnt)

		def __OpenMyShopDecoWnd(self):
			self.interface.OpenMyShopDecoWnd()

	def BINARY_PrivateShop_Appear(self, vid, text, type):
		self.interface.AppearPrivateShop(vid, text, type)

	def BINARY_PrivateShop_Disappear(self, vid):
		self.interface.DisappearPrivateShop(vid)

	if app.ENABLE_MINI_GAME_OKEY:
		## MiniGame Rumi
		def BINARY_Cards_UpdateInfo(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, hand_4, hand_4_v, hand_5, hand_5_v, cards_left, points):
			self.interface.UpdateCardsInfo(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, hand_4, hand_4_v, hand_5, hand_5_v, cards_left, points)

		def BINARY_Cards_FieldUpdateInfo(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points):
			self.interface.UpdateCardsFieldInfo(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points)

		def BINARY_Cards_PutReward(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points):
			self.interface.CardsPutReward(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points)

		def BINARY_Cards_ShowIcon(self, active):
			IsRumiGameEvent = int(active)
			if IsRumiGameEvent > 0:
				osfinfo.RUMI_GAME_EVENT = True
			else:
				osfinfo.RUMI_GAME_EVENT = False

			if osfinfo.EVENT_BANNER == True:
				self.interface.IntegrationEventBanner()
			else:
				self.interface.MiniGameOkey()

		def BINARY_Cards_Open(self, safemode):
			self.interface.OpenCardsWindow(safemode)

	if app.ENABLE_MINI_GAME_BNW:
		def MiniGameBNWEvent(self, isEnable):
			if self.interface:
				self.interface.SetBNWEventStatus(isEnable)
				if osfinfo.EVENT_BANNER == True:
					self.interface.IntegrationEventBanner()

		def MiniGameBNWStart(self):
			if self.interface:
				self.interface.MiniGameBNWStart()

		def MiniGameBNWCompare(self, winIndex, playerCard, opponentCard, myScore):
			if self.interface:
				self.interface.MiniGameBNWCompare(winIndex, playerCard, opponentCard, myScore)

		def MiniGameBNWAddRanking(self, position, isMain, name, donations):
			if self.interface:
				self.interface.MiniGameBNWAddRanking(position, isMain,  name, donations)

		def MiniGameBNWClearRanking(self):
			if self.interface:
				self.interface.MiniGameBNWClearRanking()

		def MiniGameBNWOpenRanking(self):
			if self.interface:
				self.interface.MiniGameBNWOpenRanking()

		def MiniGameBNWUpdateRanking(self):
			if self.interface:
				self.interface.MiniGameBNWUpdateRanking()


	if app.ENABLE_MINI_GAME_CATCH_KING:
		def MiniGameCatchKingEvent(self, isEnable):
			if self.interface:
				self.interface.SetCatchKingEventStatus(isEnable)
				if osfinfo.EVENT_BANNER == True:
					self.interface.IntegrationEventBanner()

		def MiniGameCatchKingEventStart(self, bigScore):
			self.interface.MiniGameCatchKingEventStart(bigScore)

		def MiniGameCatchKingSetHandCard(self, cardNumber):
			self.interface.MiniGameCatchKingSetHandCard(cardNumber)

		def MiniGameCatchKingResultField(self, score, rowType, cardPos, cardValue, keepFieldCard, destroyHandCard, getReward, isFiveNear):
			self.interface.MiniGameCatchKingResultField(score, rowType, cardPos, cardValue, keepFieldCard, destroyHandCard, getReward, isFiveNear)

		def MiniGameCatchKingSetEndCard(self, cardPos, cardNumber):
			self.interface.MiniGameCatchKingSetEndCard(cardPos, cardNumber)

		def MiniGameCatchKingReward(self, rewardCode):
			self.interface.MiniGameCatchKingReward(rewardCode)

	## DayMode
	def __PRESERVE_DayMode_Update(self, mode):
		pass

	def __DayMode_Update(self, mode):
		pass

	## XMasBoom
	def __XMasBoom_Update(self):
		self.BOOM_DATA_LIST = ( (2, 5), (5, 2), (7, 3), (10, 3), (20, 5) )
		if self.indexXMasBoom >= len(self.BOOM_DATA_LIST):
			return

		boomTime = self.BOOM_DATA_LIST[self.indexXMasBoom][0]
		boomCount = self.BOOM_DATA_LIST[self.indexXMasBoom][1]

		if app.GetTime() - self.startTimeXMasBoom > boomTime:
			self.indexXMasBoom += 1

			for i in xrange(boomCount):
				self.__XMasBoom_Boom()

	def __XMasBoom_Boom(self):
		x, y, z = player.GetMainCharacterPosition()
		randX = app.GetRandom(-150, 150)
		randY = app.GetRandom(-150, 150)

		snd.PlaySound3D(x+randX, -y+randY, z, "sound/common/etc/salute.mp3")

	if app.WJ_NEW_USER_CARE:
		def __PartyRequestQuestion(self, vid, name):
			vid = int(vid)
			partyRequestQuestionDialog = uicommon.QuestionDialogWithTimeLimit()
			partyRequestQuestionDialog.SetAcceptText(localeinfo.UI_ACCEPT)
			partyRequestQuestionDialog.SetCancelText(localeinfo.UI_DENY)
			partyRequestQuestionDialog.SetAcceptEvent(lambda arg=True: self.__AnswerPartyRequest(arg))
			partyRequestQuestionDialog.SetCancelEvent(lambda arg=False: self.__AnswerPartyRequest(arg))
			partyRequestQuestionDialog.Open(name + localeinfo.PARTY_DO_YOU_ACCEPT, 10)
			partyRequestQuestionDialog.SetTimeOverMsg(localeinfo.PARTY_ANSWER_TIMEOVER)
			partyRequestQuestionDialog.SetCancelOnTimeOver()
			partyRequestQuestionDialog.vid = vid
			self.partyRequestQuestionDialog = partyRequestQuestionDialog
	else:
		def __PartyRequestQuestion(self, vid):
			vid = int(vid)
			partyRequestQuestionDialog = uicommon.QuestionDialog()
			partyRequestQuestionDialog.SetText(chr.GetNameByVID(vid) + localeinfo.PARTY_DO_YOU_ACCEPT)
			partyRequestQuestionDialog.SetAcceptText(localeinfo.UI_ACCEPT)
			partyRequestQuestionDialog.SetCancelText(localeinfo.UI_DENY)
			partyRequestQuestionDialog.SetAcceptEvent(lambda arg=True: self.__AnswerPartyRequest(arg))
			partyRequestQuestionDialog.SetCancelEvent(lambda arg=False: self.__AnswerPartyRequest(arg))
			partyRequestQuestionDialog.Open()
			partyRequestQuestionDialog.vid = vid
			self.partyRequestQuestionDialog = partyRequestQuestionDialog

	if app.ENABLE_PRIVATE_INSTANCE_LOBBY:
		# CHAOS entry confirmation prompt.
		# Server pushes "PILChaosEntryConfirm <vnum>" on item-use outside CHAOS.
		# On Accept we send "/chaos_confirm <vnum>" back; the server handler
		# OnChaosEntryConfirmed then runs the lobby join (entry is free, item
		# is not consumed).
		def __PILChaosEntryConfirm(self, vnumStr):
			try:
				vnum = int(vnumStr)
			except (ValueError, TypeError):
				return
			if hasattr(self, "chaosEntryDialog") and self.chaosEntryDialog:
				self.chaosEntryDialog.Close()
				self.chaosEntryDialog = None
			dlg = uicommon.QuestionDialogWithTimeLimit()
			dlg.SetAcceptText(localeinfo.UI_ACCEPT)
			dlg.SetCancelText(localeinfo.UI_DENY)
			dlg.SetAcceptEvent(lambda v=vnum: self.__PILChaosEntryAccept(v))
			dlg.SetCancelEvent(lambda: self.__PILChaosEntryDecline())
			dlg.Open(localeinfo.PIL_CHAOS_ENTER_QUESTION, 10)
			dlg.SetTimeOverMsg(localeinfo.PIL_CHAOS_TIMEOUT_MSG)
			dlg.SetCancelOnTimeOver()
			self.chaosEntryDialog = dlg

		def __PILChaosEntryAccept(self, vnum):
			net.SendChatPacket("/chaos_confirm %d" % vnum)
			if hasattr(self, "chaosEntryDialog") and self.chaosEntryDialog:
				self.chaosEntryDialog.Close()
				self.chaosEntryDialog = None

		def __PILChaosEntryDecline(self):
			if hasattr(self, "chaosEntryDialog") and self.chaosEntryDialog:
				self.chaosEntryDialog.Close()
				self.chaosEntryDialog = None

		# Server pushes "PILChaosReturnAvail <flag> <grace_until>".
		# IMPORTANT: declare explicit positional args (not *args) — stringcommander
		# reads func_code.co_argcount to slice tokens; *args reports 1 and the
		# dispatcher truncates everything to tokens[:0].
		def __PILChaosReturnAvail(self, flagStr, graceUntilStr):
			try:
				avail      = int(flagStr) != 0
				graceUntil = int(graceUntilStr)
			except (ValueError, TypeError):
				return
			if self.interface:
				self.interface.SetChaosReturnAvail(avail, graceUntil)

	if app.ENABLE_PIL_DUNGEON:
		# Fast-Enter countdown — one handler per verb. Strict positional
		# args (no defaults, no *args) because stringcommander.Analyzer.Run
		# uses func_code.co_argcount to slice tokens and raises RuntimeError
		# on argcount mismatch.
		def __PILFastEnterStart(self, indexStr, totalMsStr):
			if self.interface:
				self.interface.OnFastEnterStart(indexStr, totalMsStr)

		def __PILFastEnterTick(self, remainingMsStr):
			if self.interface:
				self.interface.OnFastEnterTick(remainingMsStr)

		def __PILFastEnterPause(self, reasonIdStr):
			if self.interface:
				self.interface.OnFastEnterPause(reasonIdStr)

		def __PILFastEnterResume(self):
			if self.interface:
				self.interface.OnFastEnterResume()

		def __PILFastEnterCancel(self, reasonIdStr):
			if self.interface:
				self.interface.OnFastEnterCancel(reasonIdStr)

		def __PILFastEnterCancelName(self, reasonIdStr, nameStr):
			if self.interface:
				self.interface.OnFastEnterCancelName(reasonIdStr, nameStr)

		def __PILFastEnterDone(self):
			if self.interface:
				self.interface.OnFastEnterDone()

	if app.USE_PORTABLE_TELEPORT_WITH_UI:
		def __OpenTeleportWindow(self):
			self.interface.OpenTeleportWindow()

	def __AnswerPartyRequest(self, answer):
		if not self.partyRequestQuestionDialog:
			return

		vid = self.partyRequestQuestionDialog.vid

		if answer:
			net.SendChatPacket("/party_request_accept " + str(vid))
		else:
			net.SendChatPacket("/party_request_deny " + str(vid))

		self.partyRequestQuestionDialog.Close()
		self.partyRequestQuestionDialog = None

	def __PartyRequestDenied(self):
		self.PopupMessage(localeinfo.PARTY_REQUEST_DENIED)
	if app.DOMINIUM_PVP_SYSTEM:
		def BINARY_Dominium_OnRecvData(self, leftTime, membersOnline_A, membersOnline_B, score_A, score_B, circle_A, circle_B, circle_C, circle_BR, circle_BB):
			self.interface.AddDominiumResultWindow(leftTime, membersOnline_A, membersOnline_B, score_A, score_B, circle_A, circle_B, circle_C, circle_BR, circle_BB)
	if app.CRYSTAL_PVP_SYSTEM:
		def BINARY_Crystal_OnRecvData(self, leftTime, membersOnline_A, membersOnline_B, crystal_A, crystal_B):
			self.interface.AddCrystalResultWindow(leftTime, membersOnline_A, membersOnline_B, crystal_A, crystal_B)
	if app.DEFENSE_PVP_SYSTEM:
		def BINARY_Defense_OnRecvData(self, leftTime, membersOnline_A, membersOnline_B, metin_A, metin_B):
			self.interface.AddDefenseResultWindow(leftTime, membersOnline_A, membersOnline_B, metin_A, metin_B)

	if app.DOMINIUM_PVP_SYSTEM or app.DEFENSE_PVP_SYSTEM or app.CRYSTAL_PVP_SYSTEM: #app.TOURNAMENT_PVP_SYSTEM or 
		def BINARY_PvP_OnRecvData(self, type, kills, others, points, team, role):
			self.interface.AddPvPEventResultWindow(type, kills, others, points, team, role)

	if app.DEATHMATCH_EVENT:
		def BINARY_Deathmatch_Information(self, kills, death, kill_owner, name_owner):
			self.interface.AddDTInformation(kills, death, kill_owner, name_owner)

	def __EnableTestServerFlag(self):
		app.EnableTestServerFlag()

	if app.BL_KILL_BAR:
		def AddKillInfo(self, killer, victim, killer_race, victim_race, weapon_type,color_type):
			if self.interface:
				self.interface.AddKillInfo(killer, victim, killer_race, victim_race, weapon_type,color_type)

	def __InGameShop_Show(self, url):
		return

	# WEDDING
	def __LoginLover(self):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.OnLoginLover()

	def __LogoutLover(self):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.OnLogoutLover()
		if self.affectShower:
			self.affectShower.HideLoverState()

	def __LoverNear(self):
		if self.affectShower:
			self.affectShower.ShowLoverState()

	def __LoverFar(self):
		if self.affectShower:
			self.affectShower.HideLoverState()

	if app.ENABLE_FEATURES_OXEVENT:
		def BINARY_OxEvent_Window(self):
			if self.eventWindowLogin.IsShow():
				self.eventWindowLogin.Hide()
			else:
				self.eventWindowLogin.Show()

		def BINARY_Coupon_Window(self):
			self.interface.wndCouponAdmin.OpenWindow()

		def BINARY_OxEvent_Append(self, event, participantsCount, observersCount):
			import oxevent
			tokens = int(event)

			if tokens == oxevent.APPEND_WINNERS:
				self.eventWindow.Append()

			elif tokens == oxevent.APPEND_REFRESH:
				self.eventWindowManager.RefreshCounter(participantsCount, observersCount)		

			elif tokens == oxevent.APPEND_WINDOW:
				self.eventWindowManager.Show()

	def __LoverDivorce(self):
		if self.interface.wndMessenger:
			self.interface.wndMessenger.ClearLoverInfo()
		if self.affectShower:
			self.affectShower.ClearLoverState()

	if getattr(app, "ADVANCED_BATTLE_PASS", 0):
		def BattlePassActive(self, isPremium):
			if int(isPremium) == 1:
				self.interface.wndBattlePass.UnlockPremium()

		def BattlePassUpdate(self, index, count, exp, totalExp, level, coolTime):
			self.interface.wndBattlePass.SetExperience(int(exp), int(totalExp))
			self.interface.wndBattlePass.SetLevel(int(level))
			self.interface.wndBattlePass.UpdateMission(int(index), int(count), int(coolTime))

		def BattlePassExpUpdate(self, exp, totalExp, level):
			# Called when using EXP Boost item - updates only exp/level, not missions
			self.interface.wndBattlePass.SetExperience(int(exp), int(totalExp))
			self.interface.wndBattlePass.SetLevel(int(level))

		def BattlePassInfo(self, category, index, title, type, vnum, count, maxCount, expRecv, isPremium, coolTime):
			self.interface.wndBattlePass.AppendMission(int(category), int(index), title, int(type), int(vnum), int(count), int(maxCount), int(expRecv), int(isPremium), int(coolTime))

		def BattlePassInfoReward(self, index, vnum, count, iNecessaryLevel, status, isPremium):
			# Server sends: index, vnum, count, iNecessaryLevel, status, isPremium
			# AppendRewardItem(index, vnum, count, status, isPremium, iNecessaryLevel)
			self.interface.wndBattlePass.AppendRewardItem(int(index), int(vnum), int(count), int(status), int(isPremium), int(iNecessaryLevel))

		def BattlePassInfoGeneral(self, isPremium, monthBattlePass, EXP, totalEXP, level, coins):
			# Set level and exp first (needed for flash calculation)
			self.interface.wndBattlePass.SetExperience(int(EXP), int(totalEXP))
			self.interface.wndBattlePass.SetLevel(int(level))

			# Then refresh flash state (uses currentBattlePassLevel set above)
			if int(isPremium) == 1:
				self.interface.wndBattlePass.UnlockPremium()
			else:
				# Refresh flash state for non-premium users (premium calls it in UnlockPremium)
				self.interface.wndBattlePass.RefreshCollectButtonFlash()

			# constInfo.BATTLE_PASS_COINS = int(coins)

		def BattlePassExpTable(self, *args):
			# Server sends: "BP_EXP_TABLE cap0,cap1,cap2,...,capN"
			# Args is the rest of the chat-command tokens; the cap list is one CSV token (no spaces).
			if not args:
				return
			csv = args[0]
			try:
				caps = [int(x) for x in str(csv).split(",") if x.strip()]
			except (ValueError, TypeError):
				return
			if hasattr(self.interface, "wndBattlePass") and self.interface.wndBattlePass:
				self.interface.wndBattlePass.SetExpTable(caps)

		def ShowShopCoinBattlePass(self):
			self.interface.dlgShop.wndTextBattlePassCoin.Show()
			self.interface.dlgShop.btnBuy.Hide()
			self.interface.dlgShop.btnSell.Hide()

		def BattlePassClear(self):
			self.interface.wndBattlePass.ClearBattlePass()

		def BattlePassSetTimes(self, endTime, dailyReset, weeklyReset):
			"""Set Battle Pass timers - called by server via BP_TIMES command.
			Args:
				endTime: Seconds until battle pass season ends
				dailyReset: Seconds until daily mission reset
				weeklyReset: Seconds until weekly mission reset
			"""
			self.interface.wndBattlePass.SetBattlePassEndTime(int(endTime))
			self.interface.wndBattlePass.SetResetTimes(int(dailyReset), int(weeklyReset))


	def SaryongStoryUpdate(self, iChapter, iProgress, iTarget, iEndTime, iDuration, iLastClaimed):
		self.interface.wndStoryInterface.SetGlobalProgress(
			int(iChapter), int(iProgress), int(iTarget),
			int(iEndTime), int(iDuration), int(iLastClaimed)
		)


	def SaryongSingleUpdate(self, iChapter, iKills, iTarget, iLastClaimed, iTotalChapters):
		self.interface.wndStoryInterface.SetSingleProgress(
			int(iChapter), int(iKills), int(iTarget),
			int(iLastClaimed), int(iTotalChapters)
		)

	def SaryongRanking(self, name1, kills1, name2, kills2, name3, kills3,
							  pv1, pc1, pv2, pc2, pv3, pc3, myContrib):
		if not self.interface:
			return
		if not self.interface.wndStoryInterface:
			return

		self.interface.wndStoryInterface.SetRanking(
			str(name1), int(kills1),
			str(name2), int(kills2),
			str(name3), int(kills3)
		)
		self.interface.wndStoryInterface.SetRankPrizes(
			int(pv1), int(pc1),
			int(pv2), int(pc2),
			int(pv3), int(pc3)
		)
		self.interface.wndStoryInterface.SetPlayerContribution(int(myContrib))

	def ToggleStoryWindow(self):
		self.interface.ToggleStoryWindow()

	if app.ENABLE_WORLDBOSS:
		def __WBBossConfig(self, data):
			if not self.interface or not self.interface.wndWorldBoss:
				return
			args = data.split("|")
			if len(args) >= 5:
				self.interface.wndWorldBoss.OnWBBossConfig(int(args[0]), int(args[1]), int(args[2]), int(args[3]), int(args[4]))

		def __WBRankPage(self, data):
			if not self.interface or not self.interface.wndWorldBoss:
				return
			args = data.split("|")
			if len(args) >= 5:
				self.interface.wndWorldBoss.OnWBRankPage(args[0], args[1], args[2], args[3], args[4])

		def __WBRankEntry(self, data):
			if not self.interface or not self.interface.wndWorldBoss:
				return
			args = data.split("|")
			if len(args) >= 8:
				self.interface.wndWorldBoss.OnWBRankEntry(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7])

		def __WBMyRank(self, data):
			if not self.interface or not self.interface.wndWorldBoss:
				return
			args = data.split("|")
			if len(args) >= 6:
				self.interface.wndWorldBoss.OnWBMyRank(args[0], args[1], args[2], args[3], args[4], args[5])

		def __WBDailyCap(self, data):
			if not self.interface or not self.interface.wndWorldBoss:
				return
			args = data.split("|")
			if len(args) >= 2:
				self.interface.wndWorldBoss.OnWBDailyCap(args[0], args[1])

		def __WBWeeklyTimer(self, data):
			if not self.interface or not self.interface.wndWorldBoss:
				return
			args = data.split("|")
			if len(args) >= 3:
				self.interface.wndWorldBoss.OnWBWeeklyTimer(args[0], args[1], args[2])

		def __WBBossSpawn(self, vnum):
			if not self.interface or not self.interface.wndWorldBoss:
				return
			self.interface.wndWorldBoss.ShowBossSpawnAlert(int(vnum))

		def __WBBossDied(self, vnum):
			if self.interface and self.interface.wndWorldBoss:
				self.interface.wndWorldBoss.HideBossSpawnAlert(int(vnum))

			if app.ENABLE_WORLDBOSS_V2_DAMAGE_METER:
				wnd = getattr(self.interface, "wndWBDamageMeter", None) if self.interface else None
				if wnd and wnd.IsShowingBoss(int(vnum)):
					wnd.Close()

		def __GDRunAlert(self, vnum, runId):
			if not self.interface or not self.interface.wndWorldBoss:
				return
			self.interface.wndWorldBoss.ShowGuildRaidAlert(int(vnum), int(runId))

		def __GDRunEnd(self, vnum):
			if self.interface and self.interface.wndWorldBoss:
				self.interface.wndWorldBoss.HideGuildRaidAlert(int(vnum))

	if getattr(app, "ENABLE_WORLDBOSS_V3", 0):
		def __WBPvPBlock(self, data):
			try:
				player.SetWBPvPBlocked(int(data))
			except (ValueError, AttributeError):
				pass

		def __WBRewardRow(self, data):
			if not self.interface or not self.interface.wndWorldBoss:
				return
			args = data.split("|")
			if len(args) >= 6:
				self.interface.wndWorldBoss.OnWBRewardRow(int(args[0]), int(args[1]), int(args[2]), int(args[3]), int(args[4]), int(args[5]))

		def __WBRewardEnd(self, data):
			if not self.interface or not self.interface.wndWorldBoss:
				return
			self.interface.wndWorldBoss.OnWBRewardEnd(int(data))

	def __GDDungeonWnd(self, method):
		wnd = getattr(self.interface, "wndGuild", None) if self.interface else None
		return getattr(wnd, method, None) if wnd else None

	def __GPFirstCmd(self, payload = "0"):
		fn = self.__GDDungeonWnd("OnGuildPrestigeFirsts")
		if fn:
			fn(payload)

	def __GDDungeonCfg(self, officer, dailyUsed, dailyMax, cooldown, weekUsed, weekCap):
		fn = self.__GDDungeonWnd("OnGuildDungeonCfg")
		if not fn:
			return
		try:
			fn(int(officer), int(dailyUsed), int(dailyMax), int(cooldown), int(weekUsed), int(weekCap))
		except ValueError:
			pass

	def __GDDungeonTier(self, tier, rep, r1, r2, r3, r4, r5, best, exp = 0):
		fn = self.__GDDungeonWnd("OnGuildDungeonTier")
		if not fn:
			return
		try:
			fn(int(tier), int(rep), int(r1), int(r2), int(r3), int(r4), int(r5), int(best), int(exp))
		except ValueError:
			pass

	def __GDDungeonChest(self, tier, vnum):
		fn = self.__GDDungeonWnd("OnGuildDungeonChest")
		if not fn:
			return
		try:
			fn(int(tier), int(vnum))
		except ValueError:
			pass

	def __GDDungeonTop(self, tier, payload):
		fn = self.__GDDungeonWnd("OnGuildDungeonTop")
		if not fn:
			return
		try:
			fn(int(tier), payload)
		except ValueError:
			pass

	def __GDDungeonLive(self, tier, remain):
		fn = self.__GDDungeonWnd("OnGuildDungeonLive")
		if not fn:
			return
		try:
			fn(int(tier), int(remain))
		except ValueError:
			pass

	if app.ENABLE_WORLDBOSS_V2_DAMAGE_METER:
		def WBDmgMeterHandler(self, data):
			wnd = getattr(self.interface, "wndWBDamageMeter", None) if self.interface else None
			if not wnd:
				return

			# Format: "<bossVnum>|<elapsed>|<participants>|<aliveCount>|<myDmg>|<myRank>|name:dmg:isMe,name:dmg:isMe,..."
			parts = data.split("|", 6)
			if len(parts) < 7:
				return

			try:
				bossVnum = int(parts[0])
				elapsed = int(parts[1])
				participants = int(parts[2])
				aliveCount = int(parts[3])
				myDmg = int(parts[4])
				myRank = int(parts[5])
			except ValueError:
				return

			topList = []
			topStr = parts[6]
			if topStr:
				for entry in topStr.split(","):
					fields = entry.split(":")
					if len(fields) != 3:
						continue
					try:
						topList.append((fields[0], int(fields[1]), int(fields[2]) != 0))
					except ValueError:
						continue

			wnd.Update(bossVnum, elapsed, participants, aliveCount, myDmg, myRank, topList)

		def WBDmgMeterTestHandler(self):
			wnd = getattr(self.interface, "wndWBDamageMeter", None) if self.interface else None
			if not wnd:
				return
			topList = [
				("Aria",    125000000, False),
				("Boran",    80000000, False),
				("Corin",    45000000, True),
				("Duke",     35000000, False),
				("Elron",    28000000, False),
			]
			wnd.Update(4901, 155, 7, 1, 45000000, 3, topList)

		if getattr(app, "ENABLE_WORLDBOSS_V3", 0):
			def __WBEscrow(self, data):
				wnd = getattr(self.interface, "wndWBDamageMeter", None) if self.interface else None
				if not wnd:
					return

				parts = data.split("|")
				if len(parts) < 2:
					return

				try:
					coins = int(parts[0])
					bounty = int(parts[1])
				except ValueError:
					return

				wnd.OnWBEscrow(coins, bounty)

	if app.ENABLE_MISSION_QUEST:
		def MissionQuestUpdate(self, category, index, missionCount, missionState):
			self.interface.wndMissionQuest.SetMissionQuestUpdate(int(category), int(index), int(missionCount), int(missionState))
		
		def MissionQuestTable(self, szArgs):
			args = [int(arg) for arg in szArgs.split('|')]
			self.interface.wndMissionQuest.SetMissionInfo(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9], args[10])
		
		def MissionQuestGeneral(self, leftTimeUntilTomorrow, leftTimeUntilSunday):
			self.interface.wndMissionQuest.SetMissionQuestGeneral(int(leftTimeUntilTomorrow), int(leftTimeUntilSunday))
		
		def MissionQuestReward(self, szArgs):
			args = [int(arg) for arg in szArgs.split('|')]
			self.interface.wndMissionQuest.SetMissionQuestReward(args[0], args[1], args[2], args[3], args[4], args[5])

		def MissionQuestSpinReward(self, selectedItemIdx, selectedItemCount, cmdData):
			self.interface.wndMissionQuest.SetMissionSpinReward(int(selectedItemIdx), int(selectedItemCount), cmdData)

		def MissionQuestRerollInfo(self, dailyRerollUsed, dailyRerollMax, weeklyRerollUsed, weeklyRerollMax,
								   dailyRefreshUsed, dailyRefreshMax, weeklyRefreshUsed, weeklyRefreshMax,
								   rerollItemVnum, rerollItemCount, refreshItemVnum, refreshItemCount):
			self.interface.wndMissionQuest.SetRerollRefreshInfo(
				int(dailyRerollUsed), int(dailyRerollMax),
				int(weeklyRerollUsed), int(weeklyRerollMax),
				int(dailyRefreshUsed), int(dailyRefreshMax),
				int(weeklyRefreshUsed), int(weeklyRefreshMax),
				int(rerollItemVnum), int(rerollItemCount),
				int(refreshItemVnum), int(refreshItemCount))

		def MissionQuestClaimLock(self, canClaimDaily, canClaimWeekly):
			self.interface.wndMissionQuest.SetClaimLock(int(canClaimDaily), int(canClaimWeekly))

		def MissionQuestHistory(self, szArgs):
			parts = szArgs.split("|")
			if len(parts) >= 7:
				self.interface.wndMissionQuest.AddHistoryEntry(
					int(parts[0]),  # timestamp
					int(parts[1]),  # category
					int(parts[2]),  # missionType
					int(parts[3]),  # targetVnum
					int(parts[4]),  # completedCount
					int(parts[5]),  # rewardVnum
					int(parts[6])   # rewardCount
				)

		def MissionQuestHistoryPage(self, szArgs):
			parts = szArgs.split("|")
			if len(parts) >= 2:
				self.interface.wndMissionQuest.SetHistoryPageInfo(
					int(parts[0]),  # currentPage
					int(parts[1])   # hasMore (0 or 1)
				)


	if app.ENABLE_PARTY_WAR:
		def PartyWarBoardOpen(self):
			if chr.IsGameMaster(player.GetMainCharacterIndex()):
				if self.interface:
					self.interface.wndPartywarBoard.Open()
			
		def __PartyWarBoard(self, member, reward, groups, value):
			if self.interface:
				self.interface.wndPartywarBoard.SetPartywarBoard(member, reward, groups)
				
		def __PartyWarTime(self, time):
			if self.interface:
				self.interface.wndPartywarTimer.SetPartywarTimer(time)
				self.interface.wndPartywarTimer.Open()
		
		def PartyWarButton(self, time):
			if self.interface:
				self.interface.wndPartywarButton.SetPartywarTimer(time)
				self.interface.wndPartywarButton.Open()
				
		def OpenPartyWarRankWindow(self):
			if self.interface.wndPartywarPlayerBoard.IsShow():
				self.interface.wndPartywarPlayerBoard.Close()
				return
			
			self.interface.wndPartywarPlayerBoard.Open()
			net.SendChatPacket("/open_party_war_wnd")

	def __PlayMusic(self, flag, filename):
		flag = int(flag)
		if flag:
			snd.FadeOutAllMusic()
			musicinfo.SaveLastPlayFieldMusic()
			snd.FadeInMusic("BGM/" + filename)
		else:
			snd.FadeOutAllMusic()
			musicinfo.LoadLastPlayFieldMusic()
			snd.FadeInMusic("BGM/" + musicinfo.fieldMusic)

	# END_OF_WEDDING

	if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
		## HilightSlot Change
		def DeactivateSlot(self, slotindex, type):
			self.interface.DeactivateSlot(slotindex, type)

		## HilightSlot Change
		def ActivateSlot(self, slotindex, type):
			self.interface.ActivateSlot(slotindex, type)

	if app.USE_ACCE_SYSTEM:
		def ActAcce(self, iAct, bWindow):
			if self.interface:
				self.interface.ActAcce(iAct, bWindow)

		def AlertAcce(self, bWindow):
			snd.PlaySound("sound/ui/make_soket.wav")
			if bWindow:
				self.PopupMessage(localeinfo.ACCE_DEL_SERVEITEM)
			else:
				self.PopupMessage(localeinfo.ACCE_DEL_ABSORDITEM)

	def ShowTeleport(self):
		self.interface.ToggleTeleportPanel()

	if app.ENABLE_GROWTH_PET_SYSTEM:
		def PetHatchingWindowCommand(self, command):
			self.interface.PetHatchingWindowCommand(command)

		def PetNameChangeWindowCommand(self, command):
			self.interface.PetNameChangeWindowCommand(command)

		def PetSkillUpgradeDlgOpen(self, slot, index, gold):
			self.interface.PetSkillUpgradeDlgOpen(slot, index, gold)

		def PetFlashEvent(self, index):
			self.interface.PetFlashEvent(index)

		def PetAffectShowerRefresh(self):
			self.interface.PetAffectShowerRefresh()

		def PetFeedReuslt(self, result):
			self.interface.PetFeedReuslt(result)
			
		def PetAttrDetermineResult(self, byType):
			self.interface.PetAttrDetermineResult(byType)
			
		def PetAttrChangeResult(self, slotIndex, byType):
			self.interface.PetAttrChangeResult(slotIndex, byType)
			
		def PetReviveResult(self, result):
			self.interface.PetReviveResult(result)

		def PetWindowTypeResult(self, result): #checked
			self.interface.PetWindowTypeResult(result)

	if app.ENABLE_MULTIFARM_BLOCK:
		def UpdateMultiFarmPlayer(self, multiFarmPlayer):
			self.affectShower.SetMultiFarmPlayer(str(multiFarmPlayer))

		def UpdateMultiFarmAffect(self, multiFarmStatus, isNewStatus):
			self.affectShower.SetMultiFarmInfo(int(multiFarmStatus))
			if int(isNewStatus) == 1:
				if int(multiFarmStatus) == 1:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.MULTI_FARM_ACTIVE_CHAT)
				else:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.MULTI_FARM_DEACTIVE_CHAT)

			app.SetMultiFarmExeIcon(int(multiFarmStatus))

	if app.ENABLE_SOLO_LEADERSHIP_BONUS:
		def __OnSoloLeadershipBonus(self, active, b1, b2, b3, b4, b5, b6):
			constinfo.SOLO_LEADERSHIP_ACTIVE = int(active)
			constinfo.SOLO_LEADERSHIP_BONUS = [int(b1), int(b2), int(b3), int(b4), int(b5), int(b6)]
			if self.interface:
				self.interface.RefreshSoloLeadership()

	def __OnPvpOrder(self, state):
		constinfo.PVP_ORDER = int(state)
		if self.affectShower:
			self.affectShower.SetPvPOrderState(constinfo.PVP_ORDER)

	if app.ENABLE_GEAR_SETS:
		def RefreshGearSetWindow(self):
			self.interface.RefreshGearSetWindow()

		def ShowGearSetToast(self, slot):
			self.interface.ShowGearSetToast(slot)

	if app.ENABLE_SWITCHBOT:
		def RefreshSwitchbotWindow(self):
			self.interface.RefreshSwitchbotWindow()

		if app.USE_SWITCHBOT_FIX_MEDIUM_STUFF:
			def RefreshSwitchbotItem(self):
				self.interface.RefreshSwitchbotItem()
		else:
			def RefreshSwitchbotItem(self, slot):
				self.interface.RefreshSwitchbotItem(slot)

	if app.ENABLE_MAILBOX:
		def MailBoxProcess(self, type, data):
			if self.interface:
				self.interface.MailBoxProcess( type, data )

	if app.ENABLE_ANTI_MULTIPLE_FARM:
		def BINARY_RecvAntiFarmReload(self):
			if not self.interface:
				return
			self.interface.SendAntiFarmReload()

	def BINARY_RecvGiveItemInformation(self, v_GiveItens):
		for i in xrange(len(v_GiveItens)):
			itemVnum, itemCount = v_GiveItens[i]
			self.interface.RegistItemGive(itemVnum, itemCount)

	if app.ENABLE_ITEMSHOP:
		def ItemShopClear(self, updateTime):
			uiitemshop.ItemShopClear(int(updateTime))
		
		def ItemShopAppendItem(self, categoryIndex, categorySubIndex, itemID, itemVnum, itemPrice, itemDiscount, itemOffertime, itemTopSelling, itemAddedTime, itemSellingCount, weekLimit, monthLimit, globalMonthLimit=0):
			uiitemshop.ItemShopAppendItem(int(categoryIndex), int(categorySubIndex), int(itemID), int(itemVnum), long(itemPrice), int(itemDiscount), int(itemOffertime), int(itemTopSelling), int(itemAddedTime), long(itemSellingCount), int(weekLimit), int(monthLimit), int(globalMonthLimit))
		
		def ItemShopHideLoading(self):
			self.interface.ItemShopHideLoading()
		
		def ItemShopOpenMainPage(self):
			self.interface.OpenItemShopMainWindow()
		
		def ItemShopLogClear(self):
			uiitemshop.ItemShopLogClear()
		
		def ItemShopAppendLog(self, dateText, dateTime, playerName, ipAdress, itemVnum, itemCount, itemPrice):
			uiitemshop.ItemShopAppendLog(str(dateText), int(dateTime), str(playerName), str(ipAdress), int(itemVnum), int(itemCount), long(itemPrice))
		
		def ItemShopPurchasesWindow(self):
			self.interface.ItemShopPurchasesWindow()
		
		def ItemShopSetDragonCoin(self, dragonCoin):
			self.interface.ItemShopSetDragonCoin(long(dragonCoin))

		def ItemShopAppendLogEx(self, dateText, dateText2,dateTime, playerName, ipAdress, itemVnum, itemCount, itemPrice):
			uiitemshop.ItemShopAppendLog(str(dateText)+" "+str(dateText2), int(dateTime), str(playerName), str(ipAdress), int(itemVnum), int(itemCount), long(itemPrice))

		def BINARY_ItemShopUsage(self, itemID, weekUsed, monthUsed, weekReset, monthReset):
			uiitemshop.ItemShopSetUsage(int(itemID), int(weekUsed), int(monthUsed), int(weekReset), int(monthReset))

		def BINARY_ItemShopGlobalUsage(self, itemID, remaining, globalLimit):
			uiitemshop.ItemShopSetGlobalUsage(int(itemID), int(remaining), int(globalLimit))

	if app.ENABLE_VOICE_CHAT:
		def BINARY_OnVoice(self, name, vcType = 0):
			if self.interface:
				if self.interface.wndVoiceChatConfig:
					self.interface.wndVoiceChatConfig.OnMessage(name, vcType)
				if self.interface.wndVoiceChatOverlay:
					self.interface.wndVoiceChatOverlay.OnMessage(name, vcType)

		def BINARY_ReloadVoiceChatVolumes(self):
			constinfo.SendVoiceChatVolumes()

		def OnStartTalking(self):
			if constinfo.GetVoiceChatConfig("VOICE_CHAT_MICROPHONE_STATE") != 1:
				if self.interface and self.interface.wndVoiceChatConfig and not self.interface.wndVoiceChatConfig.IsShow():
					self.interface.wndVoiceChatConfig.Show()
					if not self.interface.IsOpenChat():
						self.interface.ToggleChat()
					# self.interface.wndChat.voiceChatButton.Blink(1, True) # Enable if you have Blink or Flash
					return

			app.VoiceChatStartTalking()

		def BINARY_OnStartTalking(self):
			if constinfo.GetVoiceChatConfig("VOICE_CHAT_MICROPHONE_STATE") != 1:
				if self.interface and self.interface.wndVoiceChatConfig and not self.interface.wndVoiceChatConfig.IsShow():
					self.interface.wndVoiceChatConfig.Show()
					if not self.interface.IsOpenChat():
						self.interface.ToggleChat()
					# self.interface.wndChat.voiceChatButton.Blink(1, True) # Enable if you have Blink or Flash
					return

			app.VoiceChatStartTalking()

		def OnStopTalking(self):
			app.VoiceChatStopTalking()
			
		def BINARY_OnStopTalking(self):
			app.VoiceChatStopTalking()

		def __DisableVoiceChat(self, disabled):
			disabled = int(disabled)
			app.VoiceChatSetDisabled(disabled)

		def __ConfigVoiceChat(self, arg):
			arg = int(arg)
			if self.interface and self.interface.wndVoiceChatConfig:
				self.interface.wndVoiceChatConfig.OnReceiveConfig(arg)

	if app.ENABLE_EVENT_MANAGER:
		def BINARY_KingdomWarScore(self, score_shinsoo, score_chunjo, score_jinno):
			self.interface.KingdomWarScore(score_shinsoo, score_chunjo, score_jinno)


	if app.ENABLE_INGAME_WIKI:
		def __BuildWiki(self):
			# Builds the in-game wiki widget tree + all cross-window bindings.
			# Extracted from Open(); under app.ENABLE_FAST_WARP_UI this runs on
			# first open instead of on every warp.
			if self.wndWiki:
				return

			import ingamewiki
			self.wndWiki = ingamewiki.InGameWiki()
			self.__BindWikiConsumers(proxy(self.wndWiki), self.wndWiki)

		def __GetWikiRaw(self):
			return self.wndWiki

		def __BindWikiConsumers(self, wikiProxy, wikiRaw):
			# Binds the wiki (or its lazy stand-in) to every consuming window.
			# Mirrors the legacy Open() wiring: wikiProxy where the legacy code
			# assigned proxy(self.wndWiki), wikiRaw where it passed the instance.
			self.interface.wndWiki = wikiProxy

			self.interface.dlgSystem.wikiWnd = wikiProxy

			if self.targetBoard:
				self.targetBoard.wndWiki = wikiProxy

			if self.interface.wndInventory:
				self.interface.wndInventory.wndWiki = wikiProxy

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM and self.interface.wndSpecialInventory:
				self.interface.wndSpecialInventory.wndWiki = wikiProxy

			if app.USE_DUNGEON_INFO:
				self.interface.wndDungeonInfo.BindWikiInst(wikiRaw)

			if app.ENABLE_CUBE_RENEWAL_WORLDARD and self.interface.wndCubeRenewal:
				self.interface.wndCubeRenewal.wndWiki = wikiProxy

			# if app.ENABLE_REWARD_SYSTEM:
				# self.interface.wndReward.wndWiki = wikiProxy
				# self.interface.wndReward.BindWikiReward(wikiRaw)

			self.interface.wndTrackWindow.BindWikiInst(wikiRaw)

			if app.ENABLE_WORLDBOSS and self.interface.wndWorldBoss:
				self.interface.wndWorldBoss.BindWikiInst(wikiRaw)

			if app.ENABLE_HORSE_UPGRADE and getattr(self.interface, "wndHorseUpgrade", None):
				self.interface.wndHorseUpgrade.BindWikiInst(wikiRaw)

			self.interface.dlgRefineNew.wndWiki = wikiProxy

			if app.ENABLE_BIOLOG_SYSTEM and self.interface.wndBiologManagerPanel:
				self.interface.wndBiologManagerPanel.SetWikiWindow(wikiProxy)

			if app.ENABLE_MISSION_QUEST and self.interface.wndMissionQuest:
				self.interface.wndMissionQuest.SetWikiInstance(wikiRaw)

			if getattr(self.interface, "wndGuild", None) and hasattr(self.interface.wndGuild, "BindWikiInst"):
				self.interface.wndGuild.BindWikiInst(wikiRaw)

			if self.interface.wndStoryInterface:
				self.interface.wndStoryInterface.SetWikiWindow(wikiProxy)

			if app.ADVANCED_BATTLE_PASS and self.interface.wndBattlePass:
				self.interface.wndBattlePass.SetWikiInstance(wikiRaw)

	if app.ENABLE_INGAME_WIKI:
		def ToggleWikiWindow(self):
			if app.ENABLE_FAST_WARP_UI and not self.wndWiki:
				self.__BuildWiki()

			if not self.wndWiki:
				return

			if self.wndWiki.IsShow():
				self.wndWiki.Hide()
			else:
				self.wndWiki.Show()
				self.wndWiki.SetTop()

	if app.ENABLE_PVP_ROUTES:
		def ManagerRoutesPvPSystem(self, cmd):
			cmd = cmd.split("#")
			if cmd[0] == 'CHECK_REWARD':
				constinfo.RoutesPvPSystem['puntos'] = int(cmd[1])
				constinfo.RoutesPvPSystem['recompensa'] = int(cmd[2])
				self.interface.wndRoutesPvPSystem.OnUpdate()
			elif cmd[0] == 'UPDATE':
				self.interface.wndRoutesPvPSystem.OnUpdate()

	def GetInputBegin(self):
		osfinfo.INPUT_IGNORE = 1
		
	def GetInputEnd(self):
		osfinfo.INPUT_IGNORE = 0

	if app.ENABLE_EXTENDED_BATTLE_PASS:
		def ToggleBattlePassOpen(self):
			if False == self.isFirstOpeningExtBattlePass:
				net.SendExtBattlePassAction(1)

			self.interface.ToggleBattlePassExtended()
				
		def BINARY_ExtOpenBattlePass(self):
			if self.interface:
				self.interface.ReciveOpenExtBattlePass()

		def BINARY_ExtBattlePassAddGeneralInfo(self, BattlePassType, BattlePassName, BattlePassID, battlePassStartTime, battlePassEndTime):
			if self.interface:
				self.interface.AddExtendedBattleGeneralInfo(BattlePassType, BattlePassName, BattlePassID, battlePassStartTime, battlePassEndTime)

		def BINARY_ExtBattlePassAddMission(self, battlepassType, battlepassID, missionIndex, missionType, missionInfo1, missionInfo2, missionInfo3):
			if self.interface:
				self.interface.AddExtendedBattlePassMission(battlepassType, battlepassID, missionIndex, missionType, missionInfo1, missionInfo2, missionInfo3)

		def BINARY_ExtBattlePassAddMissionReward(self, battlepassType, battlepassID, missionIndex, missionType, itemVnum, itemCount):
			if self.interface:
				self.interface.AddExtendedBattlePassMissionReward(battlepassType, battlepassID, missionIndex, missionType, itemVnum, itemCount)

		def BINARY_ExtBattlePassUpdate(self, battlepassType, missionIndex, missionType, newProgress):
			if self.interface:
				self.interface.UpdateExtendedBattlePassMission(battlepassType, missionIndex, missionType, newProgress)

		def BINARY_ExtBattlePassAddReward(self, battlepassType, battlepassID, itemVnum, itemCount):
			if self.interface:
				self.interface.AddExtendedBattlePassReward(battlepassType, battlepassID, itemVnum, itemCount)

		def BINARY_ExtBattlePassAddRanklistEntry(self, playername, battlepassType, battlepassID, startTime, endTime):
			if self.interface:
				self.interface.AddExtBattlePassRanklistEntry(playername, battlepassType, battlepassID, startTime, endTime)

	if app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM:
		def AttributesBySet(self, itemCellPos, attrEnchantProb, attrDataList):
			if self.interface:
				self.interface.SetCustomAttributeWindow(itemCellPos, attrEnchantProb, attrDataList)

	def OnCloseRemoveQuestionDialog(self, answer, event):
		if not self.removeQuestionDialog:
			return False
		
		self.removeQuestionDialog.Close()
		if not answer:
			return False
		
		net.SendChatPacket(event)
		return True

	def OnRemoveAffectQuestionDialog(self, event, text):
		if not self.removeQuestionDialog:
			import uicommon
			self.removeQuestionDialog = uicommon.QuestionDialog()
			self.removeQuestionDialog.SetText("")
			self.removeQuestionDialog.SetWidth(350)
			self.removeQuestionDialog.Close()
		
		if self.removeQuestionDialog.IsShow():
			return
		
		self.removeQuestionDialog.SetText(text)
		self.removeQuestionDialog.SetAcceptEvent(lambda arg1 = True, arg2 = event: self.OnCloseRemoveQuestionDialog(arg1, arg2))
		self.removeQuestionDialog.SetCancelEvent(lambda arg1 = False, arg2 = event: self.OnCloseRemoveQuestionDialog(arg1, arg2))
		self.removeQuestionDialog.Open()

	def BINARY_GuildSymbolError(self, errCode):#PRINT ERRCODE
		pass

	if app.ENABLE_BIOLOG_SYSTEM:
		def __BiologManagerOpen(self):
			import biologmgr
			biologmgr.SendPacket(net.BIOLOG_MANAGER_OPEN)

		def BINARY_BiologManagerOpen(self):
			# The wiki biolog page prefetches the info silently; swallow the
			# window toggle for that one reply.
			if getattr(constinfo, "WIKI_BIOLOG_SILENT_INFO", 0):
				constinfo.WIKI_BIOLOG_SILENT_INFO = 0
				return
			self.interface.ToggleBiologManagerWindow()

		def BINARY_BiologManagerUpdate(self):
			self.interface.BiologManagerUpdate()

		def BINARY_BiologManagerAlert(self):
			self.interface.BiologManager_Alert()

		def BINARY_BiologManagerClose(self):
			self.interface.BiologManagerClose()

	if app.ENABLE_ULTIMATE_REGEN:
		def TrackWindowUpdate(self):
			if systemSetting.GetBossTrack():
				try:
					self.interface.MakeTrackWindow()
					self.interface.TrackWindowCheckPacket()
				except Exception as e:
					import dbg
					dbg.TraceError(str(e))

		def BINARY_OnRecvBulkWhisper(self, text):
			chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, localeinfo.WORLDBOSS_NAME, text)
			self.interface.RecvWhisper(localeinfo.WORLDBOSS_NAME)

	if app.ENABLE_GUILD_DONATE:
		def BINARY_GuildDonateInfoUpdate(self, dType, point, exp, arr):
			if self.interface.wndGuild.wndDonate is not None:
				self.interface.wndGuild.wndDonate.UpdateInfos(dType, point, exp, arr)

		def BINARY_GuildDonateCountUpdate(self, count):
			if self.interface.wndGuild.wndDonate is not None:
				self.interface.wndGuild.wndDonate.UpdateCountText(count)

		def BINARY_GuildMedalOfHonorUpdate(self, val):
			if self.interface.wndGuild.wndDonate is not None:
				self.interface.wndGuild.wndDonate.UpdateCurrentMedalText(val)


	if app.USE_WHEEL_OF_FORTUNE:
		def OnUpdateDragonCoins(self, coins):
			constinfo.dragon_coins=int(coins)

			if app.ENABLE_ITEMSHOP:
				self.ItemShopSetDragonCoin(constinfo.dragon_coins)

			#self.interface.WheelSetDragonCoins(constinfo.dragon_coins)

	if app.ENABLE_GUILD_PASSIVE_SKILLS:
		def BINARY_GuildPassiveSkillUpdate(self, skillIdx, isActice, desc):
			player.SetSkill(220+skillIdx, 158+skillIdx)
			self.interface.wndGuild.UpdatePasiveSkill(skillIdx, desc, isActice)

	if app.__RENEWAL_BRAVE_CAPE__:
		def SetBraveCapeStatus(self, status):
			wndInventory = self.interface.wndInventory if self.interface else None
			if wndInventory and wndInventory.wndBraveCape:
				wndInventory.wndBraveCape.SetStatus(status)

	if app.ENABLE_ATTR_6TH_7TH:
		def __OpenAttr67AddDlg(self):
			if self.interface:
				self.interface.OpenAttr67AddDlg()

	if app.USE_DUNGEON_COOLDOWN_MANAGER:
		def BINARY_RecvDungeonCooldown(self, mapIndex):
			if constinfo.GetCooldownAlert(player.GetName(), mapIndex):
				chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, localeinfo.DUNGEON_COOLDOWN_TITLE, localeinfo.DUNGEON_COOLDOWN_DESCRIPTION % (localeinfo.GetMiniMapZoneNameByIdx(mapIndex)))
				self.interface.RecvWhisper(localeinfo.DUNGEON_COOLDOWN_TITLE)

	if app.USE_DUNGEON_INFO:
		def RefreshDungeonInfoWindow(self):
			if self.interface:
				self.interface.RefreshDungeonInfoWindow()

		def RefreshDungeonInfoRankingWindow(self):
			if self.interface:
				self.interface.RefreshDungeonInfoRankingWindow()

		if app.USE_DUNGEON_INFO_ADDON_LEVEL_CAP:
			def DungeonInfoCapLevel(self, level, shown):
				if self.interface:
					self.interface.DungeonInfoCapLevel(int(level), True if int(shown) == 0 else False)

			def DungeonInfoCapLevelEnd(self):
				if self.interface:
					self.interface.DungeonInfoCapLevelEnd()

	if app.__RANKING_SYSTEM__:
		def UpdateRankData(self, rankType, timeIdx, rankIdx, mainVal):
			self.interface.UpdateRankData(rankType, timeIdx, rankIdx, long(mainVal))

		def LoadRankData(self, rankType, timeIdx, rankIdx, nextUpdateTime, mainVal, rankCmd, nextWeeklyReset=0, nextMonthlyReset=0):
			self.interface.LoadRankData(rankType, timeIdx, rankIdx, nextUpdateTime, long(mainVal), rankCmd, nextWeeklyReset, nextMonthlyReset)

		def LoadHallOfFameData(self, rankType, timeIdx, rankIdx, winnersCmd):
			self.interface.LoadHallOfFameData(rankType, timeIdx, rankIdx, winnersCmd)

	if getattr(app, "USE_QUICK_ATTR_TRANSFER", 0):
		def __QuickAttrTransferCommand(self, state):
			if not self.interface:
				return

			if "open" == state:
				self.interface.OpenQuickTransferWindow()
			elif state in ("close", "success"):
				self.interface.CloseQuickTransferWindow(True)

	if app.USE_COSTUME_ATTR_TRANSFER:
		def BINARY_AttrTransfer_Open(self):
			if self.interface:
				self.interface.OpenAttrTransferWindow()

		def BINARY_AttrTransfer_Close(self):
			if self.interface:
				self.interface.CloseAttrTransferWindow()

		def BINARY_AttrTransfer_Success(self):
			if self.interface:
				self.interface.AttrTransferSuccess()

	if app.USE_ACCE_ATTR_TRANSFER:
		def BINARY_AcceAttrTransfer_Open(self):
			if self.interface:
				self.interface.OpenAcceAttrTransferWindow()

		def BINARY_AcceAttrTransfer_Close(self):
			if self.interface:
				self.interface.CloseAcceAttrTransferWindow()

		def BINARY_AcceAttrTransfer_Success(self):
			if self.interface:
				self.interface.AcceAttrTransferSuccess()

		def BINARY_AttrTransferMessage(self):
			snd.PlaySound("sound/ui/make_soket.wav")
			self.PopupMessage(localeinfo.COMB_ALERT)

	if app.USE_BL_FISH_EVENT:
		def __ClickFishEventButton(self):
			self.interface.ClickFishEventButton()

		def __FishEvent(self, enable):
			player.SetFishEventGame(int(enable))
			self.interface.IntegrationEventBanner()

		def MiniGameFishUse(self, window, pos, shape):
			self.interface.MiniGameFishUse(window, pos, shape)

		def MiniGameFishAdd(self, pos, shape):
			self.interface.MiniGameFishAdd(pos, shape)

		def MiniGameFishReward(self, vnum):
			self.interface.MiniGameFishReward(vnum)

		def MiniGameFishCount(self, count):
			self.interface.MiniGameFishCount(count)

	#if app.USE_INGAME_CHANGE_CHANNEL:
	def RefreshChannelText(self):
		self.interface.RefreshChannelText()

	if app.USE_INGAME_CHANGE_CHANNEL:
		def BINARY_ToggleChangeCH(self):
			self.interface.ToggleChangeCH()

	if app.__RENEWAL_BRAVE_CAPE__:
		def BINARY_Activate_Cape(self):
			wndInventory = self.interface.wndInventory if self.interface else None
			if wndInventory and wndInventory.wndBraveCape:
				wndInventory.wndBraveCape._ClickStatusBtn("ACTIVE")

		def BINARY_Deactive_Cape(self):
			wndInventory = self.interface.wndInventory if self.interface else None
			if wndInventory and wndInventory.wndBraveCape:
				wndInventory.wndBraveCape._ClickStatusBtn("DEACTIVE")

	def OnChangeGold(self, amount):
		self.interface.OnChangeGold(amount)
		if amount > 0:
			chat.AppendChat(chat.CHAT_TYPE_MONEY_INFO if app.ENABLE_CHATTING_WINDOW_RENEWAL else chat.CHAT_TYPE_INFO, localeinfo.GAME_CHANGE_GOLD_RECEIVED % (localeinfo.NumberToStringDotted(amount)))
		elif amount < 0:
			chat.AppendChat(chat.CHAT_TYPE_MONEY_INFO if app.ENABLE_CHATTING_WINDOW_RENEWAL else chat.CHAT_TYPE_INFO, localeinfo.GAME_CHANGE_GOLD_DEDUCTED % (localeinfo.NumberToStringDotted(abs(amount))))

	def OnChangeExp(self, amount):
		if amount > 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GAME_CHANGE_EXP_RECEIVED % (localeinfo.NumberToStringDotted(amount)))
		elif amount < 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GAME_CHANGE_EXP_DEDUCTED % (localeinfo.NumberToStringDotted(abs(amount))))

	if app.ENABLE_CHEQUE_SYSTEM:
		def OnChangeCheque(self, amount):
			if amount > 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GAME_CHANGE_CHEQUE_RECEIVED % (localeinfo.NumberToStringDotted(amount)))
			elif amount < 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GAME_CHANGE_CHEQUE_DEDUCTED % (localeinfo.NumberToStringDotted(abs(amount))))

	if app.AUTO_HUNT_RUBINUM:
		def OnRecvQueueMsg(self, errType):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.METIN_STONE_QUEUE_MSG_DICT.get(errType, localeinfo.METIN_STONE_QUEUE_MSG_UNKNOWN % (type)))

		def OnRecvQueueAddMsg(self, onQueue, maxQueue):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.METIN_STONE_QUEUE_MSG_ADDED % (maxQueue,onQueue))


	if app.ENABLE_GEM_SYSTEM:
		def OnChangeGem(self, amount):
			if amount > 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GAME_CHANGE_GEM_RECEIVED % (localeinfo.NumberToStringDotted(amount)))
			elif amount < 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GAME_CHANGE_GEM_DEDUCTED % (localeinfo.NumberToStringDotted(abs(amount))))

	def DungeonHudTimer(self, deadline, mode):
		self.interface.DungeonHudTimer(int(deadline), mode)

	def DungeonHudOff(self):
		self.interface.DungeonHudOff()

	if app.USE_NORTHWIND_DEEPS_DUNGEON:
		def NorthWindDeeps_Timer(self, start_time):
			self.interface.NorthWindDeeps_Timer(int(start_time))

		def NorthWindDeeps_Debuff(self, percent, count, each):
			self.interface.NorthWindDeeps_Debuff(int(percent), int(count), int(each))

	# if app.USE_NORTHWIND_DEEPS_DUNGEON:
	def BINARY_UIDamage(self, damage_type):
		self.interface.UIDamage(damage_type)

	if app.USE_LOG_EXCHANGE:
		def BINARY_LogExchange_Clear(self, actual_page, max_page, refresh):
			if self.interface:
				self.interface.LogExchange_Clear(actual_page, max_page, refresh)

		def BINARY_LogExchange_Load(self, ex_id, unix_time, src_ip, trg_name, trg_level, src_gold, trg_gold, src_cheque, trg_cheque):
			if self.interface:
				self.interface.LogExchange_Load(ex_id, unix_time, src_ip, trg_name, trg_level, src_gold, trg_gold, src_cheque, trg_cheque)

		def BINARY_LogExchange_Open(self, refresh):
			if self.interface:
				self.interface.LogExchange_Open(refresh)

		def BINARY_LogExchangeView_Clear(self, ex_id):
			if self.interface:
				self.interface.LogExchangeView_Clear(ex_id)

		def BINARY_LogExchangeView_Load(self, ex_id,\
											own,\
											pos,\
											vnum,\
											count,\
											soul_bind,\
											transmutation_vnum,\
											socket1,\
											socket2,\
											socket3,\
											socket4,\
											socket5,\
											apply_random_type1,\
											apply_random_value1,\
											apply_random_path1,\
											apply_random_type2,\
											apply_random_value2,\
											apply_random_path2,\
											apply_random_type3,\
											apply_random_value3,\
											apply_random_path3,\
											apply_random_type4,\
											apply_random_value4,\
											apply_random_path4,\
											attr_type1,\
											attr_value1,\
											attr_path1,\
											attr_type2,\
											attr_value2,\
											attr_path2,\
											attr_type3,\
											attr_value3,\
											attr_path3,\
											attr_type4,\
											attr_value4,\
											attr_path4,\
											attr_type5,\
											attr_value5,\
											attr_path5,\
											attr_type6,\
											attr_value6,\
											attr_path6,\
											attr_type7,\
											attr_value7,\
											attr_path7,\
											backup_mode,\
											backup_attr_type1,\
											backup_attr_value1,\
											backup_attr_path1,\
											backup_attr_type2,\
											backup_attr_value2,\
											backup_attr_path2,\
											backup_attr_type3,\
											backup_attr_value3,\
											backup_attr_path3,\
											backup_attr_type4,\
											backup_attr_value4,\
											backup_attr_path4,\
											backup_attr_type5,\
											backup_attr_value5,\
											backup_attr_path5,\
											backup_attr_type6,\
											backup_attr_value6,\
											backup_attr_path6,\
											backup_attr_type7,\
											backup_attr_value7,\
											backup_attr_path7,\
											enchant_type1,\
											enchant_value1,\
											enchant_path1,\
											enchant_type2,\
											enchant_value2,\
											enchant_path2,\
											enchant_type3,\
											enchant_value3,\
											enchant_path3,\
											enchant_type4,\
											enchant_value4,\
											enchant_path4,\
											set_value):
			if self.interface:
				self.interface.LogExchangeView_Load(ex_id,\
													own,\
													pos,\
													vnum,\
													count,\
													soul_bind,\
													transmutation_vnum,\
													socket1,\
													socket2,\
													socket3,\
													socket4,\
													socket5,\
													apply_random_type1,\
													apply_random_value1,\
													apply_random_path1,\
													apply_random_type2,\
													apply_random_value2,\
													apply_random_path2,\
													apply_random_type3,\
													apply_random_value3,\
													apply_random_path3,\
													apply_random_type4,\
													apply_random_value4,\
													apply_random_path4,\
													attr_type1,\
													attr_value1,\
													attr_path1,\
													attr_type2,\
													attr_value2,\
													attr_path2,\
													attr_type3,\
													attr_value3,\
													attr_path3,\
													attr_type4,\
													attr_value4,\
													attr_path4,\
													attr_type5,\
													attr_value5,\
													attr_path5,\
													attr_type6,\
													attr_value6,\
													attr_path6,\
													attr_type7,\
													attr_value7,\
													attr_path7,\
													backup_mode,\
													backup_attr_type1,\
													backup_attr_value1,\
													backup_attr_path1,\
													backup_attr_type2,\
													backup_attr_value2,\
													backup_attr_path2,\
													backup_attr_type3,\
													backup_attr_value3,\
													backup_attr_path3,\
													backup_attr_type4,\
													backup_attr_value4,\
													backup_attr_path4,\
													backup_attr_type5,\
													backup_attr_value5,\
													backup_attr_path5,\
													backup_attr_type6,\
													backup_attr_value6,\
													backup_attr_path6,\
													backup_attr_type7,\
													backup_attr_value7,\
													backup_attr_path7,\
													enchant_type1,\
													enchant_value1,\
													enchant_path1,\
													enchant_type2,\
													enchant_value2,\
													enchant_path2,\
													enchant_type3,\
													enchant_value3,\
													enchant_path3,\
													enchant_type4,\
													enchant_value4,\
													enchant_path4,\
													set_value)

		def BINARY_LogExchangeView_Open(self):
			if self.interface:
				self.interface.LogExchangeView_Open()

	if app.ENABLE_GUILD_RENEWAL:
		def RecvGuildLevelInfo(self, lv, v1, c1, v2, c2, v3, c3):
			self.interface.wndGuild.SetLevelInfo(int(lv), int(v1), int(c1), int(v2), int(c2), int(v3), int(c3))

		def RecvGuildPassiveInfo(self, skIndex, lv, apply, value, reqPoints):
			self.interface.wndGuild.SetPassiveInfo(int(skIndex), int(lv), int(apply), int(value), int(reqPoints))

		def RecvGuildMission(self, data):
			mission_strs = data.split(";")
			for mission_str in mission_strs:
				mission_str = mission_str.strip()
				if not mission_str:
					continue

				fields = mission_str.split(",")
				if len(fields) < 1:
					continue

				ints = map(int, fields)
				self.interface.wndGuild.wndGuildMission.RecvMission(
					ints[0], ints[1], ints[2], ints[3], ints[4],
					ints[5], ints[6], ints[7], ints[8])
