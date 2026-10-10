# coding: latin_1

import app
import chrmgr
import net
import player

import dbg
import ui
import snd
import systemSetting
import chat
import localeinfo
import constinfo
import musicinfo

import uiselectmusic
import background
import uiphasecurtain

if app.ENABLE_DOG_MODE:
	import playersettingmodule
if app.ENABLE_FPS:
	from _weakref import proxy
import uicommon

import sys
import uiscriptlocale
import wndMgr

def ReloadModule(name):
	if name in sys.modules:
		del sys.modules[name]

		if name in locals():
			del locals()[name]

		if name in globals():
			del globals()[name]

		module = __import__(name)

		if not module in locals():
			locals()[name] = module

		if not module in globals():
			globals()[name] = module

LOCALE_LANG_DICT = {
	app.LOCALE_EN : { "name" : uiscriptlocale.LANGUAGE_EN, "locale" : "en", "code_page" : 1252 },
	app.LOCALE_AE : { "name" : uiscriptlocale.LANGUAGE_AE, "locale" : "ae", "code_page" : 1256 },
}

MUSIC_FILENAME_MAX_LEN = 25
if app.ENABLE_GRAPHIC_ON_OFF:
	GRAPHIC_LEVEL_MAX_NUM = 5

blockMode = 0

class OptionDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__Initialize()
		self.__Load()

		if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
			self.curtain = uiphasecurtain.PhaseCurtain()
			self.curtain.speed = 0.03
			self.curtain.Hide()

		if app.ENABLE_GRAPHIC_ON_OFF:
			self.RefreshPetStatus()
			self.RefreshNpcNameStatus()

		if app.ENABLE_DOG_MODE:
			self.RefreshDogModeStatus()

		if app.ENABLE_FOV_OPTION:
			self.RefreshFOVOption()
			self.questionDialog = None

		self.__CreateLanguageSelectWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		#print " -------------------------------------- DELETE SYSTEM OPTION DIALOG"

	def __Initialize(self):
		if not app.ENABLE_DISABLE_SOFTWARE_TILING:
			self.tilingMode = 0
		self.titleBar = 0
		self.changeMusicButton = 0
		self.selectMusicFile = 0
		self.ctrlMusicVolume = 0
		self.ctrlSoundVolume = 0
		self.musicListDlg = 0
		if not app.ENABLE_DISABLE_SOFTWARE_TILING:
			self.tilingApplyButton = 0
		self.cameraModeButtonList = []
		self.fogModeButtonList = []
		if not app.ENABLE_DISABLE_SOFTWARE_TILING:
			self.tilingModeButtonList = []
		self.ctrlShadowQuality = 0

		if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
			self.nightModeButtonList = []
			self.snowModeButtonList = []
			self.snowTextureModeButtonList = []

		if app.ENABLE_FOG_FIX:
			self.fogButtonList = []

		if app.ENABLE_SHADOW_RENDER_QUALITY_OPTION:
			self.shadowQualityButtonList = []
			self.shadowTargetButtonList = []

		if app.ENABLE_GRAPHIC_ON_OFF:
			self.effectLevel = 0
			self.effectLevelApplyButton = 0
			self.effectLevelButtonList = []

			self.privateShopLevel = 0
			self.privateShopLevelApplyButton = 0
			self.privateShopLevelButtonList = []

			self.dropItemLevel = 0
			self.dropItemLevelApplyButton = 0
			self.dropItemLevelButtonList = []

			self.petStatusButtonList = []
			self.npcNameStatusButtonList = []

		if app.ENABLE_DOG_MODE:
			self.dogModeStatusButtonList = []

		if app.ENABLE_FOV_OPTION:
			self.fovButtonList = []

		self.language_change_window = None
		self.language_select_button = None
		self.language_change_button = None

		self.cur_language_text = None
		self.cur_language_text_window = None

		self.language_button_dict = {}
		self.language_select_list_open = False
		self.language_select_window_height = 0

		self.language_select_window_bar = None

		self.mouse_over_image = None

		self.selected_language = 0

		self.IsShow = False

	def Destroy(self):
		if app.ENABLE_FPS:
			self.fps = None
			self.fpsInfo = None
			self.currentSelectFPS = 0
		self.ClearDictionary()
		self.__Initialize()
		#print " -------------------------------------- DESTROY SYSTEM OPTION DIALOG"

	def __Load_LoadScript(self, fileName):
		try:
			pyScriptLoader = ui.PythonScriptLoader()
			pyScriptLoader.LoadScriptFile(self, fileName)
		except:
			import exception
			exception.Abort("System.OptionDialog.__Load_LoadScript")

	def __Load_BindObject(self):
		try:
			GetObject = self.GetChild
			self.titleBar = GetObject("titlebar")
			self.selectMusicFile = GetObject("bgm_file")
			self.changeMusicButton = GetObject("bgm_button")
			self.ctrlMusicVolume = GetObject("music_volume_controller")
			self.ctrlSoundVolume = GetObject("sound_volume_controller")
			self.cameraModeButtonList.append(GetObject("camera_short"))
			self.cameraModeButtonList.append(GetObject("camera_long"))

			if app.ENABLE_FOG_FIX:
				self.fogButtonList.append(GetObject("fog_off"))
				self.fogButtonList.append(GetObject("fog_on"))
			else:
				self.fogModeButtonList.append(GetObject("fog_level0"))
				self.fogModeButtonList.append(GetObject("fog_level1"))
				self.fogModeButtonList.append(GetObject("fog_level2"))

			if not app.ENABLE_DISABLE_SOFTWARE_TILING:
				self.tilingModeButtonList.append(GetObject("tiling_cpu"))
				self.tilingModeButtonList.append(GetObject("tiling_gpu"))
				self.tilingApplyButton = GetObject("tiling_apply")

			if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
				self.nightModeButtonList.append(GetObject("night_mode_off"))
				self.nightModeButtonList.append(GetObject("night_mode_on"))
				self.snowModeButtonList.append(GetObject("snow_mode_off"))
				self.snowModeButtonList.append(GetObject("snow_mode_on"))
				self.snowTextureModeButtonList.append(GetObject("snow_texture_mode_off"))
				self.snowTextureModeButtonList.append(GetObject("snow_texture_mode_on"))

			if app.ENABLE_GRAPHIC_ON_OFF:
				for i in xrange(1, GRAPHIC_LEVEL_MAX_NUM + 1):
					self.effectLevelButtonList.append(GetObject("effect_level%d" % i))
					self.privateShopLevelButtonList.append(GetObject("privateShop_level%d" % i))
					self.dropItemLevelButtonList.append(GetObject("dropItem_level%d" % i))

				self.effectLevelApplyButton = GetObject("effect_apply")
				self.privateShopLevelApplyButton = GetObject("privateShop_apply")
				self.dropItemLevelApplyButton = GetObject("dropItem_apply")

				self.petStatusButtonList.append(GetObject("pet_on"))
				self.petStatusButtonList.append(GetObject("pet_off"))

				self.npcNameStatusButtonList.append(GetObject("npcName_on"))
				self.npcNameStatusButtonList.append(GetObject("npcName_off"))

			if app.ENABLE_DOG_MODE:
				self.dogModeStatusButtonList.append(GetObject("dogMode_on"))
				self.dogModeStatusButtonList.append(GetObject("dogMode_off"))

			if app.ENABLE_FOV_OPTION:
				self.fovButtonList.append(GetObject("fov_on"))
				self.fovButtonList.append(GetObject("fov_off"))

			self.language_select_button = self.GetChild("language_select_button")
			self.language_change_window = self.GetChild("language_change_window")
			self.cur_language_text = self.GetChild("cur_language_text")
			self.cur_language_text_window = self.GetChild("cur_language_text_window")
			self.language_change_button = self.GetChild("language_change_button")

			if app.ENABLE_SHADOW_RENDER_QUALITY_OPTION:
				self.shadowQualityButtonList.append(GetObject("shadow_quality_bad"))
				self.shadowQualityButtonList.append(GetObject("shadow_quality_average"))
				self.shadowQualityButtonList.append(GetObject("shadow_quality_good"))

				self.shadowTargetButtonList.append(GetObject("shadow_target_none"))
				self.shadowTargetButtonList.append(GetObject("shadow_target_ground"))
				self.shadowTargetButtonList.append(GetObject("shadow_target_ground_and_solo"))
				self.shadowTargetButtonList.append(GetObject("shadow_target_all"))

			#self.ctrlShadowQuality = GetObject("shadow_bar")
		except:
			import exception
			exception.Abort("OptionDialog.__Load_BindObject")

	def __Load(self):
		self.__Load_LoadScript("uiscript/systemoptiondialog.py")
		self.__Load_BindObject()

		self.SetCenterPosition()

		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))

		self.ctrlMusicVolume.SetSliderPos(float(systemSetting.GetMusicVolume()))
		self.ctrlMusicVolume.SetEvent(ui.__mem_func__(self.OnChangeMusicVolume))

		self.ctrlSoundVolume.SetSliderPos(float(systemSetting.GetSoundVolume()) / 5.0)
		self.ctrlSoundVolume.SetEvent(ui.__mem_func__(self.OnChangeSoundVolume))

		#self.ctrlShadowQuality.SetSliderPos(float(systemSetting.GetShadowLevel()) / 5.0)
		#self.ctrlShadowQuality.SetEvent(ui.__mem_func__(self.OnChangeShadowQuality))

		self.changeMusicButton.SAFE_SetEvent(self.__OnClickChangeMusicButton)

		self.cameraModeButtonList[0].SAFE_SetEvent(self.__OnClickCameraModeShortButton)
		self.cameraModeButtonList[1].SAFE_SetEvent(self.__OnClickCameraModeLongButton)

		if app.ENABLE_FOG_FIX:
			self.fogButtonList[0].SAFE_SetEvent(self.__OnClickFogModeOffButton)
			self.fogButtonList[1].SAFE_SetEvent(self.__OnClickFogModeOnButton)
		else:
			self.fogModeButtonList[0].SAFE_SetEvent(self.__OnClickFogModeLevel0Button)
			self.fogModeButtonList[1].SAFE_SetEvent(self.__OnClickFogModeLevel1Button)
			self.fogModeButtonList[2].SAFE_SetEvent(self.__OnClickFogModeLevel2Button)

		if not app.ENABLE_DISABLE_SOFTWARE_TILING:
			self.tilingModeButtonList[0].SAFE_SetEvent(self.__OnClickTilingModeCPUButton)
			self.tilingModeButtonList[1].SAFE_SetEvent(self.__OnClickTilingModeGPUButton)

			self.tilingApplyButton.SAFE_SetEvent(self.__OnClickTilingApplyButton)

			self.__SetCurTilingMode()

		self.__ClickRadioButton(self.fogModeButtonList, constinfo.GET_FOG_LEVEL_INDEX())
		self.__ClickRadioButton(self.cameraModeButtonList, constinfo.GET_CAMERA_MAX_DISTANCE_INDEX())

		if app.ENABLE_FOG_FIX:
			self.__ClickRadioButton(self.fogButtonList, background.GetFogMode())

		if app.ENABLE_SHADOW_RENDER_QUALITY_OPTION:
			self.shadowQualityButtonList[background.SHADOW_QUALITY_BAD].SAFE_SetEvent(self.__OnClickChangeShadowQuality, background.SHADOW_QUALITY_BAD)
			self.shadowQualityButtonList[background.SHADOW_QUALITY_AVERAGE].SAFE_SetEvent(self.__OnClickChangeShadowQuality, background.SHADOW_QUALITY_AVERAGE)
			self.shadowQualityButtonList[background.SHADOW_QUALITY_GOOD].SAFE_SetEvent(self.__OnClickChangeShadowQuality, background.SHADOW_QUALITY_GOOD)
			self.__ClickRadioButton(self.shadowQualityButtonList, systemSetting.GetShadowQualityLevel())

			self.shadowTargetButtonList[background.SHADOW_TARGET_NONE].SAFE_SetEvent(self.__OnClickChangeShadowTarget, background.SHADOW_TARGET_NONE)
			self.shadowTargetButtonList[background.SHADOW_TARGET_GROUND].SAFE_SetEvent(self.__OnClickChangeShadowTarget, background.SHADOW_TARGET_GROUND)
			self.shadowTargetButtonList[background.SHADOW_TARGET_GROUND_AND_SOLO].SAFE_SetEvent(self.__OnClickChangeShadowTarget, background.SHADOW_TARGET_GROUND_AND_SOLO)
			self.shadowTargetButtonList[background.SHADOW_TARGET_ALL].SAFE_SetEvent(self.__OnClickChangeShadowTarget, background.SHADOW_TARGET_ALL)
			self.__ClickRadioButton(self.shadowTargetButtonList, systemSetting.GetShadowTargetLevel())

		if app.ENABLE_GRAPHIC_ON_OFF:
			self.__ClickRadioButton(self.effectLevelButtonList, systemSetting.GetEffectLevel())
			self.__ClickRadioButton(self.privateShopLevelButtonList, systemSetting.GetPrivateShopLevel())
			self.__ClickRadioButton(self.dropItemLevelButtonList, systemSetting.GetDropItemLevel())

			self.__ClickRadioButton(self.petStatusButtonList, systemSetting.IsPetStatus())
			self.__ClickRadioButton(self.npcNameStatusButtonList, systemSetting.IsNpcNameStatus())

		if app.ENABLE_DOG_MODE:
			self.__ClickRadioButton(self.dogModeStatusButtonList, systemSetting.IsDogModeStatus())

		if app.ENABLE_FOV_OPTION:
			self.__ClickRadioButton(self.fovButtonList, systemSetting.IsExtendedFOV())

		if self.language_select_button:
			self.language_select_button.SetEvent(ui.__mem_func__(self.__OnClickLanguageSelectButton))
			self.cur_language_text_window.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.__OnClickLanguageSelectButton))

		if self.language_change_button:
			self.language_change_button.SetEvent(ui.__mem_func__(self.__OnClickLanguageChangeButton))

		self.mouse_over_image = self.GetChild("mouse_over_image")
		self.mouse_over_image.Hide()

		if musicinfo.fieldMusic == musicinfo.METIN2THEMA:
			self.selectMusicFile.SetText(uiselectmusic.DEFAULT_THEMA)
		else:
			self.selectMusicFile.SetText(musicinfo.fieldMusic[:MUSIC_FILENAME_MAX_LEN])

		if app.ENABLE_FPS:
			self.GetChild("fps_change_btn").SetEvent(ui.__mem_func__(self.ChangeFPS))
			self.currentSelectFPS = systemSetting.GetFPS()
			# labels now match the actual C++ presets (the old list was stale:
			# "30 FPS" really applied 60, "120" applied 144, and 180 was missing)
			self.fpsInfo = {
				0: "60 FPS",
				1: "90 FPS",
				2: "120 FPS",
				3: "144 FPS",
				4: "180 FPS",
			}
			if app.FPS_INDEX_AUTO >= 0:
				# Auto: pace at the monitor's refresh rate (default for new installs)
				self.fpsInfo[app.FPS_INDEX_AUTO] = "AUTO"

			self.fps = ui.ComboBoxImage(self.GetChild("board"),"d:/ymir work/ui/pattern/select_image.tga",55,443)
			self.fps.SetCurrentItem(self.fpsInfo.get(self.currentSelectFPS, "AUTO"))
			self.fps.SetParent(self.GetChild("board"))
			for index in sorted(self.fpsInfo.keys()):
				self.fps.InsertItem(index, self.fpsInfo[index])
			self.fps.SetEvent(lambda x, point=proxy(self): point.__ClickFPS(x))
			self.fps.Show()

		if app.ENABLE_WINDOW_RESIZE:
			board = self.GetChild("board")
			RES_Y = board.GetHeight() + 2
			extraH = 28
			self.SetSize(self.GetWidth(), self.GetHeight() + extraH)
			board.SetSize(board.GetWidth(), board.GetHeight() + extraH)

			self.resolutionLabel = ui.TextLine()
			self.resolutionLabel.SetParent(board)
			self.resolutionLabel.SetPosition(30, RES_Y + 2)
			self.resolutionLabel.SetText(localeinfo.RESOLUTION)
			self.resolutionLabel.Show()

			self.resolutionList = []
			resSeen = {}
			for i in xrange(systemSetting.GetResolutionCount()):
				(rw, rh, rbpp) = systemSetting.GetResolution(i)
				if (rw, rh) in resSeen:
					continue
				resSeen[(rw, rh)] = 1
				self.resolutionList.append((rw, rh))

			self.resolutionCombo = ui.ComboBoxImage(board, "d:/ymir work/ui/pattern/select_image.tga", 130, RES_Y)
			self.resolutionCombo.SetParent(board)
			(cw, ch, cbpp) = systemSetting.GetCurrentResolution()
			self.resolutionCombo.SetCurrentItem("%d x %d" % (cw, ch))
			for idx in xrange(len(self.resolutionList)):
				(rw, rh) = self.resolutionList[idx]
				self.resolutionCombo.InsertItem(idx, "%d x %d" % (rw, rh))
			self.resolutionCombo.SetEvent(lambda x, point=proxy(self): point.__ClickResolution(x))
			self.resolutionCombo.Show()


		if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
			self.nightModeButtonList[0].SAFE_SetEvent(self.__OnClickNightModeOffButton)
			self.nightModeButtonList[1].SAFE_SetEvent(self.__OnClickNightModeOnButton)
			self.__InitNightModeOption()

			self.snowModeButtonList[0].SAFE_SetEvent(self.__OnClickSnowModeOffButton)
			self.snowModeButtonList[1].SAFE_SetEvent(self.__OnClickSnowModeOnButton)
			self.__InitSnowModeOption()

			self.snowTextureModeButtonList[0].SAFE_SetEvent(self.__OnClickSnowTextureModeOffButton)
			self.snowTextureModeButtonList[1].SAFE_SetEvent(self.__OnClickSnowTextureModeOnButton)
			self.__InitSnowTextureModeOption()

		if app.ENABLE_GRAPHIC_ON_OFF:
			for i in xrange(GRAPHIC_LEVEL_MAX_NUM):
				self.effectLevelButtonList[i].SAFE_SetEvent(self.__OnClickEffectLevelButton, i)
				self.privateShopLevelButtonList[i].SAFE_SetEvent(self.__OnClickPrivateShopLevelButton, i)
				self.dropItemLevelButtonList[i].SAFE_SetEvent(self.__OnClickDropItemLevelButton, i)

			self.petStatusButtonList[0].SAFE_SetEvent(self.__OnClickPetStatusButton, 0)
			self.petStatusButtonList[1].SAFE_SetEvent(self.__OnClickPetStatusButton, 1)

			self.npcNameStatusButtonList[0].SAFE_SetEvent(self.__OnClickNpcNameStatusButton, 0)
			self.npcNameStatusButtonList[1].SAFE_SetEvent(self.__OnClickNpcNameStatusButton, 1)

			self.effectLevelApplyButton.SAFE_SetEvent(self.__OnClickEffectApplyButton)
			self.privateShopLevelApplyButton.SAFE_SetEvent(self.__OnClickPrivateShopApplyButton)
			self.dropItemLevelApplyButton.SAFE_SetEvent(self.__OnClickDropItemApplyButton)

		if app.ENABLE_DOG_MODE:
			self.dogModeStatusButtonList[0].SAFE_SetEvent(self.__OnClickDogModeStatusButton, 1) # on
			self.dogModeStatusButtonList[1].SAFE_SetEvent(self.__OnClickDogModeStatusButton, 0) # off

		if app.ENABLE_FOV_OPTION:
			self.fovButtonList[0].SAFE_SetEvent(self.__OnClickFOVButton, 1) # on
			self.fovButtonList[1].SAFE_SetEvent(self.__OnClickFOVButton, 0) # off

	if not app.ENABLE_DISABLE_SOFTWARE_TILING:
		def __OnClickTilingModeCPUButton(self):
			self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_CPU_TILING_1)
			self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_CPU_TILING_2)
			self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_CPU_TILING_3)
			self.__SetTilingMode(0)

		def __OnClickTilingModeGPUButton(self):
			self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_GPU_TILING_1)
			self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_GPU_TILING_2)
			self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_GPU_TILING_3)
			self.__SetTilingMode(1)

		def __OnClickTilingApplyButton(self):
			self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_TILING_EXIT)
			if 0 == self.tilingMode:
				background.EnableSoftwareTiling(1)
			else:
				background.EnableSoftwareTiling(0)

			net.ExitGame()

	def __ClickResolution(self, index):
		if index < 0 or index >= len(self.resolutionList):
			return
		(rw, rh) = self.resolutionList[index]
		self.resolutionCombo.SetCurrentItem("%d x %d" % (rw, rh))
		self.resolutionCombo.CloseListBox()
		app.SetWindowSize(rw, rh)

	def __OnClickChangeMusicButton(self):
		if not self.musicListDlg:
			self.musicListDlg = uiselectmusic.FileListDialog()
			self.musicListDlg.SAFE_SetSelectEvent(self.__OnChangeMusic)

		self.musicListDlg.Open()

	def __ClickRadioButton(self, buttonList, buttonIndex):
		try:
			selButton = buttonList[buttonIndex]
		except IndexError:
			return

		for eachButton in buttonList:
			eachButton.SetUp()

		selButton.Down()

	if not app.ENABLE_DISABLE_SOFTWARE_TILING:
		def __SetTilingMode(self, index):
			self.__ClickRadioButton(self.tilingModeButtonList, index)
			self.tilingMode = index

	def __SetCameraMode(self, index):
		constinfo.SET_CAMERA_MAX_DISTANCE_INDEX(index)
		self.__ClickRadioButton(self.cameraModeButtonList, index)

	def __SetFogLevel(self, index):
		constinfo.SET_FOG_LEVEL_INDEX(index)
		self.__ClickRadioButton(self.fogModeButtonList, index)

	def __OnClickCameraModeShortButton(self):
		self.__SetCameraMode(0)

	def __OnClickCameraModeLongButton(self):
		self.__SetCameraMode(1)

	def __OnClickFogModeLevel0Button(self):
		self.__SetFogLevel(0)

	def __OnClickFogModeLevel1Button(self):
		self.__SetFogLevel(1)

	def __OnClickFogModeLevel2Button(self):
		self.__SetFogLevel(2)

	if app.ENABLE_FOG_FIX:
		def __OnClickFogModeOnButton(self):
			systemSetting.SetFogMode(True)
			background.SetFogMode(True)
			self.__ClickRadioButton(self.fogButtonList, 1)

		def __OnClickFogModeOffButton(self):
			systemSetting.SetFogMode(False)
			background.SetFogMode(False)
			self.__ClickRadioButton(self.fogButtonList, 0)

	def __OnChangeMusic(self, fileName):
		self.selectMusicFile.SetText(fileName[:MUSIC_FILENAME_MAX_LEN])

		if musicinfo.fieldMusic != "":
			snd.FadeOutMusic("BGM/"+ musicinfo.fieldMusic)

		if fileName == uiselectmusic.DEFAULT_THEMA:
			musicinfo.fieldMusic = musicinfo.METIN2THEMA
		else:
			musicinfo.fieldMusic = fileName

		musicinfo.SaveLastPlayFieldMusic()

		if musicinfo.fieldMusic != "":
			snd.FadeInMusic("BGM/" + musicinfo.fieldMusic)

	if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
		def __InitNightModeOption(self):
			self.NightModeOn = systemSetting.GetNightModeOption()
			self.__ClickRadioButton(self.nightModeButtonList, self.NightModeOn)
			# background.SetNightModeOption(self.NightModeOn)

		def __InitSnowModeOption(self):
			self.SnowModeOn = systemSetting.GetSnowModeOption()
			self.__ClickRadioButton(self.snowModeButtonList, self.SnowModeOn)
			# background.SetSnowModeOption(self.SnowModeOn)

		def __InitSnowTextureModeOption(self):
			self.SnowTextureModeOn = systemSetting.GetSnowTextureModeOption()
			self.__ClickRadioButton(self.snowTextureModeButtonList, self.SnowTextureModeOn)
			#background.SetSnowTextureModeOption(self.SnowTextureModeOn)

	if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
		def __OnClickNightModeOffButton(self):
			self.__ClickRadioButton(self.nightModeButtonList, 0)
			self.__SetNightMode(0)

		def __OnClickNightModeOnButton(self):
			self.__ClickRadioButton(self.nightModeButtonList, 1)
			self.__SetNightMode(1)

		def __OnClickSnowModeOffButton(self):
			self.__ClickRadioButton(self.snowModeButtonList, 0)
			self.__SetSnowMode(0)

		def __OnClickSnowModeOnButton(self):
			self.__ClickRadioButton(self.snowModeButtonList, 1)
			self.__SetSnowMode(1)

		def __OnClickSnowTextureModeOffButton(self):
			self.__ClickRadioButton(self.snowTextureModeButtonList, 0)
			self.__SetSnowTextureMode(0)

		def __OnClickSnowTextureModeOnButton(self):
			self.__ClickRadioButton(self.snowTextureModeButtonList, 1)
			self.__SetSnowTextureMode(1)

		def __SetSnowMode(self, index):
			systemSetting.SetSnowModeOption(index)

		def __SetSnowTextureMode(self, index):
			systemSetting.SetSnowTextureModeOption(index)

		def __SetNightMode(self, index):
			systemSetting.SetNightModeOption(index)
			if not background.GetDayMode():
				return
			
			if not background.IsBoomMap():
				return
			
			if 1 == index:
				self.curtain.SAFE_FadeOut(self.__DayMode_OnCompleteChangeToDark)
			else:
				self.curtain.SAFE_FadeOut(self.__DayMode_OnCompleteChangeToLight)

		def __DayMode_OnCompleteChangeToLight(self):
			background.ChangeEnvironmentData(background.DAY_MODE_LIGHT)
			self.curtain.FadeIn()

		def __DayMode_OnCompleteChangeToDark(self):
			background.RegisterEnvironmentData(background.DAY_MODE_DARK, constinfo.ENVIRONMENT_NIGHT)
			background.ChangeEnvironmentData(background.DAY_MODE_DARK)
			self.curtain.FadeIn()

	if app.ENABLE_SHADOW_RENDER_QUALITY_OPTION:
		def __OnClickChangeShadowQuality(self, shadow_quality):
			self.__ClickRadioButton(self.shadowQualityButtonList, shadow_quality)
			self.__SetShadowQualityLevel(shadow_quality)

		def __SetShadowQualityLevel(self, index):
			systemSetting.SetShadowQualityLevel(index)
			background.SetShadowQualityLevel(index)

		def __OnClickChangeShadowTarget(self, shadow_target):
			self.__ClickRadioButton(self.shadowTargetButtonList, shadow_target)
			self.__SetShadowTargetLevel(shadow_target)

		def __SetShadowTargetLevel(self, index):
			systemSetting.SetShadowTargetLevel(index)
			background.SetShadowTargetLevel(index)

	if app.ENABLE_GRAPHIC_ON_OFF:
		# Effect
		def __OnClickEffectLevelButton(self, index):
			self.__ClickRadioButton(self.effectLevelButtonList, index)
			self.effectLevel = index

		def __OnClickEffectApplyButton(self):
			systemSetting.SetEffectLevel(self.effectLevel)

		# PrivateShop
		def __OnClickPrivateShopLevelButton(self, privateShopLevelIdx):
			self.__ClickRadioButton(self.privateShopLevelButtonList, privateShopLevelIdx)
			self.privateShopLevel = privateShopLevelIdx

		def __OnClickPrivateShopApplyButton(self):
			systemSetting.SetPrivateShopLevel(self.privateShopLevel)

		# DropItem
		def __OnClickDropItemLevelButton(self, index):
			self.__ClickRadioButton(self.dropItemLevelButtonList, index)
			self.dropItemLevel = index

		def __OnClickDropItemApplyButton(self):
			systemSetting.SetDropItemLevel(self.dropItemLevel)

		def __OnClickPetStatusButton(self, flag):
			self.__ClickRadioButton(self.petStatusButtonList, flag)
			systemSetting.SetPetStatusFlag(flag)
			self.RefreshPetStatus()

		def RefreshPetStatus(self):
			if systemSetting.IsPetStatus():
				self.petStatusButtonList[0].SetUp()
				self.petStatusButtonList[1].Down()
			else:
				self.petStatusButtonList[0].Down()
				self.petStatusButtonList[1].SetUp()

		def __OnClickNpcNameStatusButton(self, flag):
			self.__ClickRadioButton(self.npcNameStatusButtonList, flag)
			systemSetting.SetNpcNameStatusFlag(flag)
			self.RefreshNpcNameStatus()

		def RefreshNpcNameStatus(self):
			if systemSetting.IsNpcNameStatus():
				self.npcNameStatusButtonList[0].SetUp()
				self.npcNameStatusButtonList[1].Down()
			else:
				self.npcNameStatusButtonList[0].Down()
				self.npcNameStatusButtonList[1].SetUp()

	if app.ENABLE_DOG_MODE:
		def __OnClickDogModeStatusButton(self, flag):
			import debuginfo
			if debuginfo.IsDebugMode():
				self.__NotifyChatLine("[DEBUG] Cannot apply in debug mode.")
				self.RefreshDogModeStatus()
				return

			self.__ClickRadioButton(self.dogModeStatusButtonList, flag)
			systemSetting.SetDogModeStatusFlag(flag)

			chrmgr.ClearRaceNameCache()
			playersettingmodule.ReloadNPC()
			systemSetting.ReloadInstance(flag)

			self.RefreshDogModeStatus()

		def RefreshDogModeStatus(self):
			if systemSetting.IsDogModeStatus():
				self.dogModeStatusButtonList[1].SetUp()
				self.dogModeStatusButtonList[0].Down()
			else:
				self.dogModeStatusButtonList[1].Down()
				self.dogModeStatusButtonList[0].SetUp()

	if app.ENABLE_FOV_OPTION:
		def __OnClickFOVButton(self, flag):
			self.__ClickRadioButton(self.fovButtonList, flag)
			systemSetting.SetExtendedFOV(flag)
			self.RefreshFOVOption()

		def RefreshFOVOption(self):
			if systemSetting.IsExtendedFOV():
				self.fovButtonList[1].SetUp()
				self.fovButtonList[0].Down()
			else:
				self.fovButtonList[1].Down()
				self.fovButtonList[0].SetUp()

	def OnChangeMusicVolume(self):
		pos = self.ctrlMusicVolume.GetSliderPos()
		snd.SetMusicVolume(pos * net.GetFieldMusicVolume())
		systemSetting.SetMusicVolume(pos)

	def OnChangeSoundVolume(self):
		pos = self.ctrlSoundVolume.GetSliderPos()
		snd.SetSoundVolumef(pos)
		systemSetting.SetSoundVolumef(pos)


	if app.ENABLE_FPS:
		def __ClickFPS(self,fps):
			self.currentSelectFPS = fps
			self.fps.SetCurrentItem(self.fpsInfo[fps])
			self.fps.CloseListBox()
		def ChangeFPS(self):
			systemSetting.SetFPS(self.currentSelectFPS)
			if app.IsVisible():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.FPS_WINDOW_ALERT)

	def OnChangeShadowQuality(self):
		pos = self.ctrlShadowQuality.GetSliderPos()
		systemSetting.SetShadowLevel(int(pos / 0.2))

	def OnCloseInputDialog(self):
		self.inputDialog.Close()
		self.inputDialog = None
		return True

	def OnCloseQuestionDialog(self):
		self.questionDialog.Close()
		self.questionDialog = None
		return True

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Show(self):
		ui.ScriptWindow.Show(self)
		self.IsShow = True

	def IsShowWindow(self):
		return self.IsShow

	def Close(self):
		if not app.ENABLE_DISABLE_SOFTWARE_TILING:
			self.__SetCurTilingMode()
		self.Hide()
		self.IsShow = False

		if app.ENABLE_FOV_OPTION:
			if self.questionDialog:
				self.OnCloseQuestionDialog()

		self.__LanguageSelectShowHide(False)

	if not app.ENABLE_DISABLE_SOFTWARE_TILING:
		def __SetCurTilingMode(self):
			if background.IsSoftwareTiling():
				self.__SetTilingMode(0)
			else:
				self.__SetTilingMode(1)

	def __NotifyChatLine(self, text):
		chat.AppendChat(chat.CHAT_TYPE_INFO, text)

	""" Based on dumped meta data"""
	# YMD.2019.12.32.Owsap - Multi Language
	def __AdjustLanguageSelectWindowPosition(self):
		x, y = self.GetGlobalPosition()

		(lx, ly) = self.language_change_window.GetLocalPosition()
		if self.language_select_window_bar:
			self.language_select_window_bar.SetPosition(x + lx + 0, y + ly + 36)

	def __CreateLanguageSelectWindow(self):
		if self.language_button_dict:
			return

		languageList = LOCALE_LANG_DICT
		if not LOCALE_LANG_DICT:
			return

		self.cur_language_text.SetText(LOCALE_LANG_DICT[self.__GetCurLanguageKey()]["name"])

		button_height = 16
		dict_len = len(languageList)
		self.language_select_window_height = dict_len * button_height

		self.language_select_window_bar = ui.Bar("TOP_MOST")
		self.language_select_window_bar.SetSize(210, self.language_select_window_height)
		self.language_select_window_bar.Hide()

		for index, key in enumerate(LOCALE_LANG_DICT):
			button = ui.Button()
			button.SetParent(self.language_select_window_bar)
			button.SetPosition(0, button_height * index)

			if 1 == dict_len:
				button.SetUpVisual("d:/ymir work/ui/quest_re/button_middle.sub")
				button.SetDownVisual("d:/ymir work/ui/quest_re/button_middle.sub")
				button.SetOverVisual("d:/ymir work/ui/quest_re/button_middle.sub")
			elif index == 0:
				button.SetUpVisual("d:/ymir work/ui/quest_re/button_middle.sub")
				button.SetDownVisual("d:/ymir work/ui/quest_re/button_middle.sub")
				button.SetOverVisual("d:/ymir work/ui/quest_re/button_middle.sub")
			elif index == dict_len - 1:
				button.SetUpVisual("d:/ymir work/ui/quest_re/button_bottom.sub")
				button.SetDownVisual("d:/ymir work/ui/quest_re/button_bottom.sub")
				button.SetOverVisual("d:/ymir work/ui/quest_re/button_bottom.sub")
			else:
				button.SetUpVisual("d:/ymir work/ui/quest_re/button_middle.sub")
				button.SetDownVisual("d:/ymir work/ui/quest_re/button_middle.sub")
				button.SetOverVisual("d:/ymir work/ui/quest_re/button_middle.sub")

			button.SetEvent(ui.__mem_func__(self.__OnClickLanguageSelect), key)
			button.SetOverEvent(ui.__mem_func__(self.__OnClickLanguageButtonOver), key)
			button.SetOverOutEvent(ui.__mem_func__(self.__OnClickLanguageButtonOverOut), key)
			button.SetText(LOCALE_LANG_DICT[key]["name"])
			button.Hide()

			self.language_button_dict[key] = button

		self.mouse_over_image.SetParent(self.language_select_window_bar)

		self.__AdjustLanguageSelectWindowPosition()

	def __GetCurLanguageKey(self):
		for key in LOCALE_LANG_DICT.keys():
			localeName = LOCALE_LANG_DICT[key]["locale"]
			if app.GetLocaleName() == localeName:
				return key

	def __GetStringCurLanguage(self):
		for key in LOCALE_LANG_DICT.keys():
			localeName = LOCALE_LANG_DICT[key]["locale"]
			if app.GetLocaleName() == localeName:
				return localeName

	def __LanguageSelectShowHide(self, is_show):
		if True == is_show:
			self.language_select_list_open = True

			if self.language_select_window_bar:
				self.language_select_window_bar.SetSize(210, self.language_select_window_height)
				self.language_select_window_bar.Show()

			for button in self.language_button_dict.values():
				button.Show()
		else:
			self.language_select_list_open = False

			if self.language_select_window_bar:
				self.language_select_window_bar.SetSize(210, 0)

			for button in self.language_button_dict.values():
				button.Hide()

	def __OnClickLanguageButtonOver(self, index):
		if not self.mouse_over_image:
			return

		button = self.language_button_dict.get(index, 0)
		if 0 == button:
			return

		(button_x, button_y) = button.GetLocalPosition()
		self.mouse_over_image.SetPosition(button_x, button_y)
		self.mouse_over_image.Show()

	def __OnClickLanguageButtonOverOut(self, index):
		if not self.mouse_over_image:
			return

		self.mouse_over_image.Hide()

	def __OnClickLanguageChangeButton(self):
		if self.__GetCurLanguageKey() == self.selected_language:
			return

		if self.selected_language != 0:
			self.ConfirmLanguageChange()

	def __OnClickLanguageSelect(self, index):
		for button in self.language_button_dict.values():
			button.Hide()

		self.__LanguageSelectShowHide(False)

		self.selected_language = index

		if self.cur_language_text:
			self.cur_language_text.SetText(LOCALE_LANG_DICT[index]["name"])

	def __OnClickLanguageSelectButton(self):
		self.__CreateLanguageSelectWindow()

		if self.language_select_list_open:
			self.__LanguageSelectShowHide(False)
		else:
			self.__LanguageSelectShowHide(True)

	def __OnLanguageSelectScroll(self):
		pass # To-do for more than 5 languages

	def __SaveLoca(self, code_page, locale):
		if app.SetLoca(code_page, locale):
			return True

		return False

	def OnTop(self):
		if self.language_select_window_bar:
			self.language_select_window_bar.SetTop()

	def OnMoveWindow(self, x, y):
		self.__AdjustLanguageSelectWindowPosition()

	def ConfirmLanguageChange(self):
		questionDialog = uicommon.QuestionDialog2()
		questionDialog.SetText1(localeinfo.RESTART_CLIENT_DO_YOU_ACCEPT_1)
		questionDialog.SetText2(localeinfo.RESTART_CLIENT_DO_YOU_ACCEPT_2)
		questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnAcceptLanguageChange))
		questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
		questionDialog.SetWidth(450)
		questionDialog.Open()
		self.questionDialog = questionDialog

	def OnEndCountDown(self):
		net.Disconnect()
		app.ShellExecute(app.GetName())
		app.Exit()

	def OnPressExitKey(self):
		pass

	def OnAcceptLanguageChange(self):
		self.OnCloseQuestionDialog()

		if self.selected_language != 0:
			locale = LOCALE_LANG_DICT[self.selected_language]["locale"]
			code_page = LOCALE_LANG_DICT[self.selected_language]["code_page"]

			if self.__SaveLoca(code_page, locale):
				#net.SendChangeLanguagePacket(self.selected_language)
				net.SetLanguage(self.selected_language)

				import intrologin
				self.popUpTimer = intrologin.ConnectingDialog()
				self.popUpTimer.Open(3.0)
				self.popUpTimer.SetText(localeinfo.LEFT_TIME)
				self.popUpTimer.SAFE_SetTimeOverEvent(self.OnEndCountDown)
				self.popUpTimer.SAFE_SetExitEvent(self.OnPressExitKey)
		else:
			pass # No language selected
