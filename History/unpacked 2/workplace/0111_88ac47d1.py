# coding: latin_1

import app
import dbg
import localeinfo
import wndMgr
import systemSetting
import mousemodule
import networkmodule
import uicandidate
import constinfo
import musicinfo
import stringcommander

#bind_me(locals().values())

def RunApp():
	musicinfo.LoadLastPlayFieldMusic()

	app.SetHairColorEnable(constinfo.HAIR_COLOR_ENABLE)
	app.SetArmorSpecularEnable(constinfo.ARMOR_SPECULAR_ENABLE)
	app.SetWeaponSpecularEnable(constinfo.WEAPON_SPECULAR_ENABLE)

	app.SetMouseHandler(mousemodule.mouseController)
	wndMgr.SetMouseHandler(mousemodule.mouseController)
	wndMgr.SetScreenSize(systemSetting.GetWidth(), systemSetting.GetHeight())

	try:
		app.Create(localeinfo.APP_TITLE, systemSetting.GetWidth(), systemSetting.GetHeight(), 1)
	except RuntimeError, msg:
		msg = str(msg)
		if "CREATE_DEVICE" == msg:
			dbg.LogBox("Sorry, Your system does not support 3D graphics,\r\nplease check your hardware and system configeration\r\nthen try again.")
		else:
			dbg.LogBox("Metin2.%s" % msg)
		return

	app.SetCamera(1500.0, 30.0, 0.0, 180.0)

	if hasattr(systemSetting, "SetFPS") and hasattr(systemSetting, "GetFPS"):
		# Apply the saved FRAME_VALUE preset at boot. The config loader only stored it;
		# nothing applied it until the player touched the settings UI - so the game
		# booted with the 60fps defaults (g_fGameFPS / clock budget / ANIFPS) and only
		# became smooth after re-selecting the preset in the options.
		systemSetting.SetFPS(systemSetting.GetFPS())

	# Gets and sets the floating-point control word
	# app.SetControlFP()

	if not mousemodule.mouseController.Create():
		return

	mainStream = networkmodule.MainStream()
	mainStream.Create()

	# mainStream.SetLoadingPhase()
	mainStream.SetLoginPhase()

	# mainStream.SetLoginPhase()
	# mainStream.SetSelectCharacterPhase()
	# mainStream.SetCreateCharacterPhase()
	# mainStream.SetSelectEmpirePhase()
	# mainStream.SetGamePhase()
	import game_data
	game_data.Load()

	if app.ENABLE_RACE_HEIGHT:
		import playersettingmodule
		playersettingmodule.LoadRaceHeight()

	if app.USE_DUNGEON_INFO and app.USE_DUNGEON_COOLDOWN_MANAGER:
		import uidungeoninfo
		uidungeoninfo.LoadDungeons()

	app.Loop()

	mainStream.Destroy()
	if mousemodule.mouseController:
		del mousemodule.mouseController

RunApp()

