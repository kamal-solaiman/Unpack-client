# coding: latin_1

import app
import pack
import net
import player

import dbg
import chat
import wndMgr
import systemSetting
import snd
import background

import ui
import constinfo
import uiselectmusic
import musicinfo
import localeinfo
import uiscriptlocale
if app.USE_OFFLINESHOP:
	import uiofflineshop_ae
	import offlineshop
if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
	import uiphasecurtain

MUSIC_FILENAME_MAX_LEN = 25
blockMode = 0
IMG_DIR = "d:/ymir work/ui/game/gameoption/"
if app.ENABLE_GRAPHIC_ON_OFF:
	GRAPHIC_LEVEL_MAX_NUM = 5

LOCALE_LANG_DICT = {
	0 : { "locale" : "en", "code_page" : 1252 },
	1 : { "locale" : "ae", "code_page" : 1256 },
}

class GameOptionWindow(ui.BoardWithTitleBar):
	def Destroy(self):
		if app.USE_IMPROVEMENTS and self.effectController:
			self.effectController.SetEvent(None)
			self.effectController = None

		if app.USE_OFFLINESHOP_VIEW_RANGE and self.privateshop_range_controller:
			self.privateshop_range_controller.SetEvent(None)
			self.privateshop_range_controller = None

		self.pvpModeButtonDict={}
		self.blockButtonList=[]
		self.viewChatButtonList = []
		self.nameColorModeButtonList = []
		self.viewTargetBoardButtonList=[]
		self.alwaysShowNameButtonList=[]
		self.namesTypeButtonList = []
		
		if app.ENABLE_EXTENDED_PICKUP:
			self.pickupIgnoreButtonList = []
		
		if app.WJ_SHOW_MOB_INFO:
			self.showMobInfoButtonList = []
		
		if app.ENABLE_GRAPHIC_ON_OFF:
			self.petStatusButtonList = []
			self.MountStatusButtonList = []
			self.npcNameStatusButtonList = []
			self.effectLevelButtonList = []
			self.dropLevelButtonList = []
		
		if app.ENABLE_FPS:
			self.fpsButtonList = []
		
		self.showDamageButtonList=[]
		self.showsalesTextButtonList=[]
		self.cameraModeButtonList = []
		if app.ENABLE_FOV_OPTION:
			self.fovButtonList = []
		
		self.ctrlSoundVolume = None
		self.ctrlMusicVolume = None
		self.selectMusicFile = None
		self.musicListDlg = None
		
		if app.USE_METIN_STONE_SCALE:
			self.metinstoneSize = None

		if app.__SCALE_EFFECT_DAMAGE__:
			self.changeScaleEffDamage = None

		self.tilingMode = 0
		self.tilingModeButtonList = []
		self.tilingApplyButton = None
		
		if app.ENABLE_FOG_FIX:
			self.fogButtonList = []
		
		if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
			self.nightModeButtonList = []
			self.snowModeButtonList = []
			self.snowTextureModeButtonList = []

		if app.ENABLE_SHADOW_RENDER_QUALITY_OPTION:
			self.shadowTargetButtonList = []
			self.shadowQualityButtonList = []
		else:
			self.ctrlShadowQuality = 0

		if app.ENABLE_KEYCHANGE_SYSTEM:
			self.keyboardButton = None
		
		self.languageButtons = []
		self.languageApplyButton = None
		self.languageID = 0
		self.questionDialog = None
		
		for j in xrange(10):
			for x in xrange(10):
				if self.children.has_key("optionWindow%d%d"%(j,x)):
					window = self.children["optionWindow%d%d"%(j,x)]
					if window:
						window.Hide()
						window.scrollBar = None
						window.ClearDictionary()
						window.Destroy()
		self.children = {}
		self.Hide()

	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		if app.USE_IMPROVEMENTS:
			self.effectController = None

		if app.USE_OFFLINESHOP_VIEW_RANGE:
			self.privateshop_range_controller = None

		self.children = {}
		self.Destroy()
		self.__LoadWindow()
		self.SetTitleName(uiscriptlocale.GAMEOPTION_TITLE)

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def __LoadWindow(self):
		self.AddFlag("movable")
		self.AddFlag("attach")
		option_data = {
			localeinfo.GAME_OPTIONS_MAIN : {
				"index": 0,
				localeinfo.GAME_OPTIONS_MAIN_0:{"index": 0,},
				localeinfo.GAME_OPTIONS_MAIN_1:{"index": 1,},
				localeinfo.GAME_OPTIONS_MAIN_2:{"index": 2,},
				#localeinfo.GAME_OPTIONS_MAIN_3:{"index": 3,},
			},
			localeinfo.GAME_OPTIONS_MAIN2 : {
			"index": 1,
				localeinfo.GAME_OPTIONS_MAIN_6:{"index": 0,},
				localeinfo.GAME_OPTIONS_MAIN_7:{"index": 1,},
			},
		}

		for key, optionTitles in option_data.items():
			if self.IsCanContinue(key):
				continue

			if not optionTitles.has_key("index"):
				continue
			optionIndex = optionTitles["index"]

			bg = ui.ImageBox()
			bg.SetParent(self)
			bg.AddFlag("attach")
			bg.SetPosition(8,65)
			bg.LoadImage(IMG_DIR+"bg.tga")
			bg.Show()
			self.children["bg%d"%optionIndex] = bg

			titleButton = ui.RadioButton()
			titleButton.SetParent(self)
			if optionIndex == 0:
				titleButton.SetUpVisual(IMG_DIR+"end_title_0.png")
				titleButton.SetOverVisual(IMG_DIR+"end_title_1.png")
				titleButton.SetDownVisual(IMG_DIR+"end_title_3.png")
				titleButton.SetPosition(16+(optionIndex*(titleButton.GetWidth()+5)), 40)
			elif optionIndex == len(option_data)-1:
				titleButton.SetUpVisual(IMG_DIR+"end_title_0.png")
				titleButton.SetOverVisual(IMG_DIR+"end_title_1.png")
				titleButton.SetDownVisual(IMG_DIR+"end_title_3.png")
				titleButton.SetPosition(16+(optionIndex*(titleButton.GetWidth()+5))-5, 40)
			else:
				titleButton.SetUpVisual(IMG_DIR+"middle_title_0.png")
				titleButton.SetOverVisual(IMG_DIR+"middle_title_1.png")
				titleButton.SetDownVisual(IMG_DIR+"middle_title_3.png")
				titleButton.SetPosition(16+(optionIndex*(titleButton.GetWidth()+5)), 40)
			titleButton.SetText(key)
			titleButton.SAFE_SetEvent(self.SetOptionType, optionIndex)
			titleButton.Show()
			self.children["titleBtn%d"%optionIndex] = titleButton

			for keyEx, optionTypes in optionTitles.items():
				if self.IsCanContinue(keyEx):
					continue
				if not optionTypes.has_key("index"):
					continue

				categoryIndex = optionTypes["index"]
				optionCategory = ui.RadioButton()
				optionCategory.SetParent(bg)
				optionCategory.SetUpVisual(IMG_DIR+"btn_cat_1.png")
				optionCategory.SetOverVisual(IMG_DIR+"btn_cat_2.png")
				optionCategory.SetDownVisual(IMG_DIR+"btn_cat_3.png")
				optionCategory.SetPosition(7, 10+(categoryIndex*(optionCategory.GetHeight()+5)))
				optionCategory.SAFE_SetEvent(self.SetCategoryType, categoryIndex)
				optionCategory.SetText(keyEx)
				optionCategory.Show()
				self.children["optionCategory%d%d"%(optionIndex,categoryIndex)] = optionCategory

				optionWindow = self.CreateOptionWindow(bg, optionIndex,categoryIndex)
				self.children["optionWindow%d%d"%(optionIndex,categoryIndex)] = optionWindow

		self.SetOptionType(0)
		self.SetSize(8+bg.GetWidth()+10,65+bg.GetHeight()+10)
		self.SetCenterPosition()
		self.UpdateScrollBar()
	def Open(self):
		self.RefreshBlock()
		self.Show()
	def OnPressEscapeKey(self):
		self.Hide()
		return True
	def __ClickRadioButton(self, buttonList, buttonIndex):
		try:
			btn=buttonList[buttonIndex]
		except IndexError:
			return
		for eachButton in buttonList:
			eachButton.SetUp()
		btn.Down()

	def IsCanContinue(self, dictKey):
		if dictKey == "index":
			return True
		return False

	def SetOptionType(self, optionType):
		self.children["optionType"] = optionType
		for j in xrange(10):
			if self.children.has_key("titleBtn%d"%j):
				titleBtn = self.children["titleBtn%d"%j]
				if j == optionType:
					titleBtn.Down()
				else:
					titleBtn.SetUp()
			if self.children.has_key("bg%d"%j):
				bg = self.children["bg%d"%j]
				if j == optionType:
					bg.Show()
				else:
					bg.Hide()
		self.SetCategoryType(0)

	def SetCategoryType(self, categoryType):
		for j in xrange(3):
			for x in xrange(5):
				if self.children.has_key("optionWindow%d%d" % (j,x)):
					self.children["optionWindow%d%d"%(j,x)].Hide()

		self.children["categoryType"] = categoryType
		currentCategoryType = self.children["optionType"]
		for j in xrange(10):
			if self.children.has_key("optionCategory%d%d"%(currentCategoryType,j)):
				categoryBtn = self.children["optionCategory%d%d"%(currentCategoryType,j)]
				if j == categoryType:
					categoryBtn.Down()
				else:
					categoryBtn.SetUp()
		
		if self.children.has_key("optionWindow%d%d" % (currentCategoryType,categoryType)):
			self.children["optionWindow%d%d"%(currentCategoryType,categoryType)].Show()
		
		self.UpdateScrollBar()

	def CreateOptionWindow(self, windowBG, optionIndex, categoryIndex):
		scriptWindow = ui.ScriptWindow()
		scriptWindow.SetParent(windowBG)
		try:
			if localeinfo.IsARABIC():
				fileName = "uiscript/ae_game_option_%d_%d.py"%(optionIndex, categoryIndex)
			else:
				fileName = "uiscript/game_option_%d_%d.py"%(optionIndex, categoryIndex)
			
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(scriptWindow, fileName)
			self.LoadCatetoryOptions(scriptWindow, optionIndex, categoryIndex)
		except Exception as e:
			dbg.TraceError(str(e))

		if scriptWindow.GetWidth() > 0:
		#Auto add scrollbar
			scrollBar = ScrollBarNew()
			scrollBar.SetParent(scriptWindow)
			scrollBar.SetPosition(scriptWindow.GetWidth()-scrollBar.GetWidth(),0)
			scrollBar.SetScrollBarSize(scriptWindow.GetHeight()-5)
			scrollBar.Hide()
			scrollBar.SetScrollEvent(ui.__mem_func__(self.UpdateScrollBar))
			scriptWindow.scrollBar = scrollBar
			scriptWindow.OnRunMouseWheel = ui.__mem_func__(self.OnRunMouseWheel)

			scriptChildrens = scriptWindow.Children
			for child in scriptChildrens:
				(_x,_y) = child.GetLocalPosition()
				child.SetPosition(_x,_y, True)

			scriptWindow.Show()
		else:
			scriptWindow.scrollBar = None
		
		return scriptWindow

	if app.USE_OFFLINESHOP_VIEW_RANGE:
		def __SetPrivateShopViewRange(self):
			systemSetting.SetPrivateShopViewRange(float(self.privateshop_range_controller.GetSliderPos()))

	def LoadCatetoryOptions(self, scriptWindow, optionIndex, categoryIndex):
		try:
			GetObject = scriptWindow.GetChild
			
			if optionIndex == 0:#Game-Options
				if categoryIndex == 0:#General
					self.pvpModeButtonDict[player.PK_MODE_PEACE] = GetObject("pvp_peace")
					self.pvpModeButtonDict[player.PK_MODE_PEACE].SAFE_SetEvent(self.__OnClickPvPModePeaceButton)
					self.pvpModeButtonDict[player.PK_MODE_REVENGE] = GetObject("pvp_revenge")
					self.pvpModeButtonDict[player.PK_MODE_REVENGE].SAFE_SetEvent(self.__OnClickPvPModeRevengeButton)
					self.pvpModeButtonDict[player.PK_MODE_GUILD] = GetObject("pvp_guild")
					self.pvpModeButtonDict[player.PK_MODE_GUILD].SAFE_SetEvent(self.__OnClickPvPModeGuildButton)
					self.pvpModeButtonDict[player.PK_MODE_FREE] = GetObject("pvp_free")
					self.pvpModeButtonDict[player.PK_MODE_FREE].SAFE_SetEvent(self.__OnClickPvPModeFreeButton)
					self.__SetPeacePKMode()
					
					block_exchange_button = GetObject("block_exchange_button")
					block_exchange_button.SetToggleUpEvent(self.__OnClickBlockExchangeButton)
					block_exchange_button.SetToggleDownEvent(self.__OnClickBlockExchangeButton)
					self.blockButtonList.append(block_exchange_button)
					
					block_party_button = GetObject("block_party_button")
					block_party_button.SetToggleUpEvent(self.__OnClickBlockPartyButton)
					block_party_button.SetToggleDownEvent(self.__OnClickBlockPartyButton)
					self.blockButtonList.append(block_party_button)
					
					block_guild_button = GetObject("block_guild_button")
					block_guild_button.SetToggleUpEvent(self.__OnClickBlockGuildButton)
					block_guild_button.SetToggleDownEvent(self.__OnClickBlockGuildButton)
					self.blockButtonList.append(block_guild_button)
					
					block_whisper_button = GetObject("block_whisper_button")
					block_whisper_button.SetToggleUpEvent(self.__OnClickBlockWhisperButton)
					block_whisper_button.SetToggleDownEvent(self.__OnClickBlockWhisperButton)
					self.blockButtonList.append(block_whisper_button)
					
					block_friend_button = GetObject("block_friend_button")
					block_friend_button.SetToggleUpEvent(self.__OnClickBlockFriendButton)
					block_friend_button.SetToggleDownEvent(self.__OnClickBlockFriendButton)
					self.blockButtonList.append(block_friend_button)
					
					block_party_request_button = GetObject("block_party_request_button")
					block_party_request_button.SetToggleUpEvent(self.__OnClickBlockPartyRequest)
					block_party_request_button.SetToggleDownEvent(self.__OnClickBlockPartyRequest)
					self.blockButtonList.append(block_party_request_button)
					
					self.viewChatButtonList.append(GetObject("view_chat_on_button"))
					self.viewChatButtonList[0].SAFE_SetEvent(self.__OnClickViewChat)
					self.viewChatButtonList.append(GetObject("view_chat_off_button"))
					self.viewChatButtonList[1].SAFE_SetEvent(self.__OnClickViewChat)
					self.RefreshViewChat()
					
					self.nameColorModeButtonList.append(GetObject("name_color_normal"))
					self.nameColorModeButtonList[0].SAFE_SetEvent(self.__OnClickNameColorMode)
					self.nameColorModeButtonList.append(GetObject("name_color_empire"))
					self.nameColorModeButtonList[1].SAFE_SetEvent(self.__OnClickNameColorMode)
					self.RefreshNameColor()
					
					self.viewTargetBoardButtonList.append(GetObject("target_board_view"))
					self.viewTargetBoardButtonList[0].SAFE_SetEvent(self.__SetTargetBoardViewMode)
					self.viewTargetBoardButtonList.append(GetObject("target_board_no_view"))
					self.viewTargetBoardButtonList[1].SAFE_SetEvent(self.__SetTargetBoardViewMode)
					self.RefreshTargetBoard()

					self.tilingModeButtonList.append(GetObject("tiling_cpu"))
					self.tilingModeButtonList.append(GetObject("tiling_gpu"))
					self.tilingModeButtonList[0].SAFE_SetEvent(self.__OnClickTilingModeCPUButton)
					self.tilingModeButtonList[1].SAFE_SetEvent(self.__OnClickTilingModeGPUButton)
					self.tilingApplyButton = GetObject("tiling_apply")
					self.tilingApplyButton.SAFE_SetEvent(self.__OnClickTilingApplyButton)
					self.__SetCurTilingMode()

					self.showDamageButtonList.append(GetObject("show_damage_on_button"))
					self.showDamageButtonList[0].SAFE_SetEvent(self.__OnClickShowDamage)
					self.showDamageButtonList.append(GetObject("show_damage_off_button"))
					self.showDamageButtonList[1].SAFE_SetEvent(self.__OnClickShowDamage)
					self.RefreshShowDamage()

					if app.ENABLE_KEYCHANGE_SYSTEM:
						self.keyboardButton = GetObject("language_info_button")
						self.keyboardButton.SetEvent(ui.__mem_func__(self.OpenKeyChangeWindow))
					else:
						GetObject("keyboard_window").Hide()
				elif categoryIndex == 1:# Camera
					self.cameraModeButtonList.append(GetObject("camera_level0"))
					self.cameraModeButtonList[0].SAFE_SetEvent(self.__OnClickCameraMode, 0)
					self.cameraModeButtonList.append(GetObject("camera_level1"))
					self.cameraModeButtonList[1].SAFE_SetEvent(self.__OnClickCameraMode, 1)
					self.RefreshCameraMode()
					
					if app.ENABLE_FOV_OPTION:
						self.fovButtonList.append(GetObject("fov_on"))
						self.fovButtonList[0].SAFE_SetEvent(self.__OnClickFOVButton, 1)
						self.fovButtonList.append(GetObject("fov_off"))
						self.fovButtonList[1].SAFE_SetEvent(self.__OnClickFOVButton, 0)
						self.RefreshFOVOption()
					else:
						GetObject("fov_mode_window").Hide()

					if app.USE_METIN_STONE_SCALE:
						metinstoneSize = GetObject("stonesize_controller")
						metinstoneSize.SetSliderPos(float(systemSetting.GetMetinStoneSize()))
						metinstoneSize.SetEvent(ui.__mem_func__(self.OnChangeMetinStoneSize))
						self.metinstoneSize = metinstoneSize
					else:
						GetObject("stonesize_window").Hide()

					if app.__SCALE_EFFECT_DAMAGE__:
						changeScaleEffDamage = GetObject("scaleEff_Slider")
						changeScaleEffDamage.SetSliderPos(float(systemSetting.GetScaleEffDamageLevel()) / 5.0)
						changeScaleEffDamage.SetEvent(ui.__mem_func__(self.OnChangeScaleEffDamage))
						self.changeScaleEffDamage = changeScaleEffDamage
					else:
						GetObject("dmgsize_window").Hide()

				elif categoryIndex == 2:# Sound
					ctrlSoundVolume = GetObject("sound_volume_controller")
					ctrlSoundVolume.SetSliderPos(float(systemSetting.GetSoundVolume()) / 5.0)
					ctrlSoundVolume.SetEvent(ui.__mem_func__(self.OnChangeSoundVolume))
					self.ctrlSoundVolume = ctrlSoundVolume
					
					ctrlMusicVolume = GetObject("music_volume_controller")
					ctrlMusicVolume.SetSliderPos(float(systemSetting.GetMusicVolume()))
					ctrlMusicVolume.SetEvent(ui.__mem_func__(self.OnChangeMusicVolume))
					self.ctrlMusicVolume = ctrlMusicVolume
					GetObject("bgm_button").SAFE_SetEvent(self.__OnClickChangeMusicButton)
					self.selectMusicFile = GetObject("bgm_file")

			elif optionIndex == 1:#Graphic-Options
				if categoryIndex == 0: #Performance
					if app.USE_IMPROVEMENTS:
						tmp = GetObject("effect_controller")
						tmp.SetSliderPos(float(systemSetting.GetEffectRenderRange() / float(1)))
						tmp.SetEvent(ui.__mem_func__(self.__OnChangeEffectDistance))
						self.effectController = tmp
					else:
						GetObject("effect_controller").Hide()

					self.alwaysShowNameButtonList.append(GetObject("always_show_name_on_button"))
					self.alwaysShowNameButtonList[0].SAFE_SetEvent(self.__OnClickAlwaysShowName)
					self.alwaysShowNameButtonList.append(GetObject("always_show_name_off_button"))
					self.alwaysShowNameButtonList[1].SAFE_SetEvent(self.__OnClickAlwaysShowName)
					self.RefreshAlwaysShowName()
					
					self.namesTypeButtonList.append(GetObject("name_type1_button"))
					self.namesTypeButtonList.append(GetObject("name_type2_button"))
					self.namesTypeButtonList[0].SAFE_SetEvent(self.__OnClickNamesType1)
					self.namesTypeButtonList[1].SAFE_SetEvent(self.__OnClickNamesType2)
					self.RefreshNamesType()
					
					if app.WJ_SHOW_MOB_INFO:
						self.showMobInfoButtonList.append(GetObject("show_mob_level_button"))
						self.showMobInfoButtonList.append(GetObject("show_mob_AI_flag_button"))
						self.showMobInfoButtonList[0].SetToggleUpEvent(self.__OnClickShowMobLevelButton)
						self.showMobInfoButtonList[0].SetToggleDownEvent(self.__OnClickShowMobLevelButton)
						self.showMobInfoButtonList[1].SetToggleUpEvent(self.__OnClickShowMobAIFlagButton)
						self.showMobInfoButtonList[1].SetToggleDownEvent(self.__OnClickShowMobAIFlagButton)
						self.RefreshShowMobInfo()
					else:
						GetObject("monster_info_window").Hide()

					self.showsalesTextButtonList.append(GetObject("salestext_on_button"))
					self.showsalesTextButtonList.append(GetObject("salestext_off_button"))
					self.showsalesTextButtonList[0].SAFE_SetEvent(self.__OnClickSalesTextOnButton)
					self.showsalesTextButtonList[1].SAFE_SetEvent(self.__OnClickSalesTextOffButton)
					self.RefreshShowSalesText()

					if app.ENABLE_GRAPHIC_ON_OFF:
						self.petStatusButtonList.append(GetObject("pet_off"))
						self.petStatusButtonList.append(GetObject("pet_on"))
						self.petStatusButtonList[0].SAFE_SetEvent(self.__OnClickPetStatusButton, 1)
						self.petStatusButtonList[1].SAFE_SetEvent(self.__OnClickPetStatusButton, 0)
						self.RefreshPetStatus()

						self.MountStatusButtonList.append(GetObject("mount_off"))
						self.MountStatusButtonList.append(GetObject("mount_on"))
						self.MountStatusButtonList[0].SAFE_SetEvent(self.__OnClickMountStatusButton, 1)
						self.MountStatusButtonList[1].SAFE_SetEvent(self.__OnClickMountStatusButton, 0)
						self.RefreshMountStatus()
						
						self.npcNameStatusButtonList.append(GetObject("npcName_off"))
						self.npcNameStatusButtonList.append(GetObject("npcName_on"))
						self.npcNameStatusButtonList[0].SAFE_SetEvent(self.__OnClickNpcNameStatusButton, 1)
						self.npcNameStatusButtonList[1].SAFE_SetEvent(self.__OnClickNpcNameStatusButton, 0)
						self.RefreshNpcNameStatus()
						
						for i in xrange(1, GRAPHIC_LEVEL_MAX_NUM + 1):
							self.effectLevelButtonList.append(GetObject("effect_level%d" % i))
							self.effectLevelButtonList[i - 1].SAFE_SetEvent(self.__OnClickEffectLevelButton, i - 1)
							self.dropLevelButtonList.append(GetObject("drop_level%d" % i))
							self.dropLevelButtonList[i - 1].SAFE_SetEvent(self.__OnClickDropLevelButton, i - 1)
						
						self.RefreshEffectLevel()
						self.RefreshDropLevel()
					else:
						GetObject("pet_mode_window").Hide()
						GetObject("mount_mode_window").Hide()
						GetObject("npc_mode_window").Hide()
						GetObject("effect_window").Hide()
						GetObject("privateshop_window").Hide()
						GetObject("drop_window").Hide()
					
					if app.ENABLE_FPS:
						for i in xrange(5):
							self.fpsButtonList.append(GetObject("fps_mode%d" % i))
							self.fpsButtonList[i].SAFE_SetEvent(self.__OnClickFPSButton, i)
						
						self.RefreshFPS()
					else:
						GetObject("fps_window").Hide()

					if app.USE_OFFLINESHOP_VIEW_RANGE:
						self.privateshop_range_controller = GetObject("privateshop_range_controller_ui")
						self.privateshop_range_controller.SetSliderPos(float(systemSetting.GetPrivateShopViewRange()))
						self.privateshop_range_controller.SetEvent(ui.__mem_func__(self.__SetPrivateShopViewRange))
					else:
						GetObject("privateshop_range_window_ui").Hide()
				elif categoryIndex == 1: #Environment
					if app.ENABLE_SHADOW_RENDER_QUALITY_OPTION:
						#self.shadowTargetButtonList = []
						self.shadowTargetButtonList.append(GetObject("shadow_target_none"))
						self.shadowTargetButtonList[0].SAFE_SetEvent(self.__OnClickChangeShadowTarget, 0)
						self.shadowTargetButtonList.append(GetObject("shadow_target_ground"))
						self.shadowTargetButtonList[1].SAFE_SetEvent(self.__OnClickChangeShadowTarget, 1)
						self.shadowTargetButtonList.append(GetObject("shadow_target_ground_and_solo"))
						self.shadowTargetButtonList[2].SAFE_SetEvent(self.__OnClickChangeShadowTarget, 2)
						self.shadowTargetButtonList.append(GetObject("shadow_target_all"))
						self.shadowTargetButtonList[3].SAFE_SetEvent(self.__OnClickChangeShadowTarget, 3)
						self.__ClickRadioButton(self.shadowTargetButtonList, systemSetting.GetShadowTargetLevel())

						#self.shadowQualityButtonList = []
						self.shadowQualityButtonList.append(GetObject("shadow_quality_bad"))
						self.shadowQualityButtonList[0].SAFE_SetEvent(self.__OnClickChangeShadowQuality, 0)
						self.shadowQualityButtonList.append(GetObject("shadow_quality_average"))
						self.shadowQualityButtonList[1].SAFE_SetEvent(self.__OnClickChangeShadowQuality, 1)
						self.shadowQualityButtonList.append(GetObject("shadow_quality_good"))
						self.shadowQualityButtonList[2].SAFE_SetEvent(self.__OnClickChangeShadowQuality, 2)
						self.__ClickRadioButton(self.shadowQualityButtonList, systemSetting.GetShadowQualityLevel())
					else:
						self.ctrlShadowQuality = GetObject("shadow_bar")
						self.ctrlShadowQuality.SetSliderPos(float(systemSetting.GetShadowLevel()) / 5.0)
						self.ctrlShadowQuality.SetEvent(ui.__mem_func__(self.OnChangeShadowQuality))

					if app.ENABLE_FOG_FIX:
						self.fogButtonList.append(GetObject("fog_off"))
						self.fogButtonList.append(GetObject("fog_on"))
						self.fogButtonList[0].SAFE_SetEvent(self.__OnClickFogModeOffButton)
						self.fogButtonList[1].SAFE_SetEvent(self.__OnClickFogModeOnButton)
						self.RefreshFogMode()
					else:
						GetObject("fog_mode_window").Hide()
					
					if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
						self.curtain = uiphasecurtain.PhaseCurtain()
						self.curtain.speed = 0.03
						self.curtain.Hide()
						
						self.nightModeButtonList.append(GetObject("night_mode_off"))
						self.nightModeButtonList.append(GetObject("night_mode_on"))
						self.nightModeButtonList[0].SAFE_SetEvent(self.__OnClickNightModeOffButton)
						self.nightModeButtonList[1].SAFE_SetEvent(self.__OnClickNightModeOnButton)
						self.RefreshNightMode()
						
						self.snowModeButtonList.append(GetObject("snow_mode_off"))
						self.snowModeButtonList.append(GetObject("snow_mode_on"))
						self.snowModeButtonList[0].SAFE_SetEvent(self.__OnClickSnowModeOffButton)
						self.snowModeButtonList[1].SAFE_SetEvent(self.__OnClickSnowModeOnButton)
						self.RefreshSnowMode()
						
						self.snowTextureModeButtonList.append(GetObject("snowtexture_mode_off"))
						self.snowTextureModeButtonList.append(GetObject("snowtexture_mode_on"))
						self.snowTextureModeButtonList[0].SAFE_SetEvent(self.__OnClickSnowTextureModeOffButton)
						self.snowTextureModeButtonList[1].SAFE_SetEvent(self.__OnClickSnowTextureModeOnButton)
						self.RefreshSnowTextureMode()
					else:
						GetObject("night_mode_window").Hide()
						GetObject("snow_mode_window").Hide()
						GetObject("snowtexture_mode_window").Hide()
		except Exception as e:
			dbg.TraceError(str(e))

	# Dont Touch #
	def GetCurrentWindow(self):
		if self.children.has_key("optionType") and self.children.has_key("categoryType"):
			(optionType,categoryType) = (self.children["optionType"],self.children["categoryType"])
			if self.children.has_key("optionWindow%d%d"%(optionType,categoryType)):
				return self.children["optionWindow%d%d"%(optionType,categoryType)]
		return None
	def GetCurrentScrollBar(self):
		window = self.GetCurrentWindow()
		if window != None:
			return window.scrollBar
		return None

	def OnRunMouseWheel(self, nLen):
		if self.IsInPosition():
			scrollBar = self.GetCurrentScrollBar()
			if scrollBar:
				if scrollBar.IsShow():
					if nLen > 0:
						scrollBar.OnUp()
					else:
						scrollBar.OnDown()
					return True
		
		return False

	def UpdateScrollBar(self):
		window = self.GetCurrentWindow()
		if window == None:
			return
		scrollBar = window.scrollBar
		if scrollBar == None:
			return
		scriptChildrens = window.Children
		if len(scriptChildrens) == 0:
			return

		windowHeight = window.GetHeight()

		# OLD SHIT
		#lastChildren = scriptChildrens[len(scriptChildrens)-1]
		#screenSize = lastChildren.exPos[1]+lastChildren.GetHeight()

		screenSize = 0
		for child in scriptChildrens:
			childHeight = child.exPos[1] + child.GetHeight()
			if childHeight > screenSize:
				screenSize=childHeight

		if screenSize > windowHeight:
			scrollLen = screenSize-windowHeight
			basePos = int(scrollBar.GetPos()*scrollLen)
			for child in scriptChildrens:
				(_x,_y) = child.exPos
				child.SetPosition(_x,_y-basePos)

			scrollBar.SetMiddleBarSize(float(windowHeight-5)/float(screenSize))
			scrollBar.Show()
		else:
			scrollBar.Hide()

		_wy = window.GetGlobalPosition()[1]
		elementDictionary = window.ElementDictionary
		for childName, child in elementDictionary.items():
			(_x,_y) = child.GetGlobalPosition()
			childHeight = child.GetHeight()
			textLines = []
			images = []
			if isinstance(child, ui.ExpandedImageBox):
				images.append(child)
			elif isinstance(child, ui.TextLine):
				textLines.append(child)
			elif isinstance(child, ui.ToggleButton) or isinstance(child, ui.RadioButton):
				if child.ButtonText != None:
					textLines.append(child.ButtonText)
				images.append(child)
			elif isinstance(child, ui.SliderBar):
				if child.backGroundImage != None:
					images.append(child.backGroundImage)
				if child.cursor != None:
					images.append(child.cursor)

				if app.ENABLE_INGAME_WIKI and child.resetButton:
					images.append(child.resetButton)

			for childItem in textLines:
				if _y < _wy:
					if childItem.IsShow():
						childItem.Hide()
				elif _y > (_wy+windowHeight-20):
					if childItem.IsShow():
						childItem.Hide()
				else:
					if not childItem.IsShow():
						childItem.Show()

			for childItem in images:
				if _y < _wy:
					childItem.SetRenderingRect(0,ui.calculateRect(childHeight-abs(_y-_wy),childHeight),0,0)
				elif _y+childHeight > (_wy+windowHeight-4):
					calculate = (_wy+windowHeight-4) - (_y+childHeight)
					if calculate == 0:
						return
					f = ui.calculateRect(childHeight-abs(calculate),childHeight)
					childItem.SetRenderingRect(0,0,0,f)
				else:
					childItem.SetRenderingRect(0,0,0,0)
	# Dont Touch #

	# PvP - Mode
	def __SetPeacePKMode(self):
		self.__SetPKMode(player.PK_MODE_PEACE)
	def __SetPKMode(self, mode):
		for btn in self.pvpModeButtonDict.values():
			btn.SetUp()
		if self.pvpModeButtonDict.has_key(mode):
			self.pvpModeButtonDict[mode].Down()
	def __CheckPvPProtectedLevelPlayer(self):
		if player.GetStatus(player.LEVEL)<constinfo.PVPMODE_PROTECTED_LEVEL:
			self.__SetPeacePKMode()
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_PROTECT % (constinfo.PVPMODE_PROTECTED_LEVEL))
			return True
		return False
	def __RefreshPVPButtonList(self):
		self.__SetPKMode(player.GetPKMode())
	def __OnClickPvPModePeaceButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if constinfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 0", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_NOT_SUPPORT)
	def __OnClickPvPModeRevengeButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if constinfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 1", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_NOT_SUPPORT)
	def __OnClickPvPModeFreeButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if constinfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 2", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_NOT_SUPPORT)
	def __OnClickPvPModeGuildButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if 0 == player.GetGuildID():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_CANNOT_SET_GUILD_MODE)
			return
		if constinfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 4", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_NOT_SUPPORT)
	def OnChangePKMode(self):
		self.__RefreshPVPButtonList()
	# PvP - Mode

	# Block - Mode
	def RefreshBlock(self):
		global blockMode
		for i in xrange(len(self.blockButtonList)):
			if 0 != (blockMode & (1 << i)):
				self.blockButtonList[i].Down()
			else:
				self.blockButtonList[i].SetUp()
	def OnBlockMode(self, mode):
		global blockMode
		blockMode = mode
		self.RefreshBlock()
	def __OnClickBlockExchangeButton(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_EXCHANGE))
	def __OnClickBlockPartyButton(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_PARTY))
	def __OnClickBlockGuildButton(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_GUILD))
	def __OnClickBlockWhisperButton(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_WHISPER))
	def __OnClickBlockFriendButton(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_FRIEND))
	def __OnClickBlockPartyRequest(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_PARTY_REQUEST))
	# Block - Mode

	# Chat - Mode
	def RefreshViewChat(self):
		if systemSetting.IsViewChat():
			self.viewChatButtonList[0].Down()
			self.viewChatButtonList[1].SetUp()
		else:
			self.viewChatButtonList[0].SetUp()
			self.viewChatButtonList[1].Down()
	def __OnClickViewChat(self):
		systemSetting.SetViewChatFlag(not systemSetting.IsViewChat())
		self.RefreshViewChat()
	# Chat - Mode

	# Name Color - Mode
	def __OnClickNameColorMode(self):
		constinfo.SET_CHRNAME_COLOR_INDEX(not constinfo.GET_CHRNAME_COLOR_INDEX())
		self.RefreshNameColor()
	def RefreshNameColor(self):
		index = constinfo.GET_CHRNAME_COLOR_INDEX()
		self.nameColorModeButtonList[index].Down()
		self.nameColorModeButtonList[not index].SetUp()
	# Name Color - Mode

	# Target Board - Mode
	def RefreshTargetBoard(self):
		index = constinfo.GET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD()
		self.viewTargetBoardButtonList[index].Down()
		self.viewTargetBoardButtonList[not index].SetUp()
	def __SetTargetBoardViewMode(self):
		constinfo.SET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD(not constinfo.GET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD())
		self.RefreshTargetBoard()
	# Target Board - Mode

	if app.ENABLE_KEYCHANGE_SYSTEM:
		def OpenKeyChangeWindow(self):
			self.keyboardButton.SetUp()
			player.OpenKeyChangeWindow()

	def RefreshNamesType(self):
		if not systemSetting.IsShowOutline():
			self.namesTypeButtonList[1].Down()
			self.namesTypeButtonList[0].SetUp()
		else:
			self.namesTypeButtonList[1].SetUp()
			self.namesTypeButtonList[0].Down()

	def __OnClickNamesType1(self):
		systemSetting.SetShowOutlineFlag(True)
		self.RefreshNamesType()

	def __OnClickNamesType2(self):
		systemSetting.SetShowOutlineFlag(False)
		self.RefreshNamesType()

	if app.WJ_SHOW_MOB_INFO:
		def RefreshShowMobInfo(self):
			if systemSetting.IsShowMobLevel():
				self.showMobInfoButtonList[0].Down()
			else:
				self.showMobInfoButtonList[0].SetUp()
			if systemSetting.IsShowMobAIFlag():
				self.showMobInfoButtonList[1].Down()
			else:
				self.showMobInfoButtonList[1].SetUp()

		def __OnClickShowMobLevelButton(self):
			systemSetting.SetShowMobLevel(not systemSetting.IsShowMobLevel())
			self.RefreshShowMobInfo()
		def __OnClickShowMobAIFlagButton(self):
			systemSetting.SetShowMobAIFlag(not systemSetting.IsShowMobAIFlag())
			self.RefreshShowMobInfo()

	if app.ENABLE_GRAPHIC_ON_OFF:
		def RefreshPetStatus(self):
			if systemSetting.IsPetStatus():
				self.petStatusButtonList[1].SetUp()
				self.petStatusButtonList[0].Down()
			else:
				self.petStatusButtonList[1].Down()
				self.petStatusButtonList[0].SetUp()

		def __OnClickPetStatusButton(self, flag):
			systemSetting.SetPetStatusFlag(flag)
			self.RefreshPetStatus()

		def RefreshMountStatus(self):
			if systemSetting.IsMountStatus():
				self.MountStatusButtonList[1].SetUp()
				self.MountStatusButtonList[0].Down()
			else:
				self.MountStatusButtonList[1].Down()
				self.MountStatusButtonList[0].SetUp()

		def __OnClickMountStatusButton(self, flag):
			systemSetting.SetMountStatusFlag(flag)
			self.RefreshMountStatus()

		def RefreshNpcNameStatus(self):
			if systemSetting.IsNpcNameStatus():
				self.npcNameStatusButtonList[1].SetUp()
				self.npcNameStatusButtonList[0].Down()
			else:
				self.npcNameStatusButtonList[1].Down()
				self.npcNameStatusButtonList[0].SetUp()

		def __OnClickNpcNameStatusButton(self, flag):
			systemSetting.SetNpcNameStatusFlag(flag)
			self.RefreshNpcNameStatus()

		def RefreshEffectLevel(self):
			for btn in self.effectLevelButtonList:
				btn.SetUp()
			
			self.effectLevelButtonList[systemSetting.GetEffectLevel()].Down()

		def __OnClickEffectLevelButton(self, index):
			systemSetting.SetEffectLevel(index)
			self.RefreshEffectLevel()

		def RefreshDropLevel(self):
			for btn in self.dropLevelButtonList:
				btn.SetUp()
			
			self.dropLevelButtonList[systemSetting.GetDropItemLevel()].Down()

		def __OnClickDropLevelButton(self, index):
			systemSetting.SetDropItemLevel(index)
			self.RefreshDropLevel()

	if app.ENABLE_SHADOW_RENDER_QUALITY_OPTION:
		def __OnClickChangeShadowTarget(self, shadow_target):
			systemSetting.SetShadowTargetLevel(shadow_target)
			background.SetShadowTargetLevel(shadow_target)
			self.__ClickRadioButton(self.shadowTargetButtonList, shadow_target)

		def __OnClickChangeShadowQuality(self, shadow_quality):
			systemSetting.SetShadowQualityLevel(shadow_quality)
			background.SetShadowQualityLevel(shadow_quality)
			self.__ClickRadioButton(self.shadowQualityButtonList, shadow_quality)
	else:
		def OnChangeShadowQuality(self):
			pos = self.ctrlShadowQuality.GetSliderPos()
			systemSetting.SetShadowLevel(int(pos / 0.2))

	if app.ENABLE_FPS:
		def RefreshFPS(self):
			for btn in self.fpsButtonList:
				btn.SetUp()
			
			self.fpsButtonList[systemSetting.GetFPS()].Down()

		def __OnClickFPSButton(self, mode):
			systemSetting.SetFPS(mode)
			if app.IsVisible():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.FPS_WINDOW_ALERT)
			
			self.RefreshFPS()

	if app.ENABLE_FOG_FIX:
		def RefreshFogMode(self):
			if background.GetFogMode():
				self.fogButtonList[1].Down()
				self.fogButtonList[0].SetUp()
			else:
				self.fogButtonList[1].SetUp()
				self.fogButtonList[0].Down()

		def __OnClickFogModeOnButton(self):
			systemSetting.SetFogMode(True)
			background.SetFogMode(True)
			self.RefreshFogMode()

		def __OnClickFogModeOffButton(self):
			systemSetting.SetFogMode(False)
			background.SetFogMode(False)
			self.RefreshFogMode()

	if app.USE_METIN_STONE_SCALE:
		def OnChangeMetinStoneSize(self):
			if not self.metinstoneSize:
				return

			systemSetting.SetMetinStoneScale(float(self.metinstoneSize.GetSliderPos()))

	if app.__SCALE_EFFECT_DAMAGE__:
		def OnChangeScaleEffDamage(self):
			if not self.changeScaleEffDamage:
				return
			pos = float(self.changeScaleEffDamage.GetSliderPos())
			systemSetting.SetScaleEffDamageLevel(pos * 5.0)
			systemSetting.SaveConfig()

	if app.USE_IMPROVEMENTS:
		def __OnChangeEffectDistance(self):
			systemSetting.SetEffectRenderRange(float(self.effectController.GetSliderPos()))

	if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
		def __DayMode_OnCompleteChangeToLight(self):
			background.ChangeEnvironmentData(background.DAY_MODE_LIGHT)
			self.curtain.FadeIn()

		def __DayMode_OnCompleteChangeToDark(self):
			background.RegisterEnvironmentData(background.DAY_MODE_DARK, constinfo.ENVIRONMENT_NIGHT)
			background.ChangeEnvironmentData(background.DAY_MODE_DARK)
			self.curtain.FadeIn()

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
			
			self.RefreshNightMode()

		def RefreshNightMode(self):
			if systemSetting.GetNightModeOption():
				self.nightModeButtonList[1].Down()
				self.nightModeButtonList[0].SetUp()
			else:
				self.nightModeButtonList[1].SetUp()
				self.nightModeButtonList[0].Down()

		def __OnClickNightModeOffButton(self):
			self.__SetNightMode(0)
			self.RefreshNightMode()

		def __OnClickNightModeOnButton(self):
			self.__SetNightMode(1)
			self.RefreshNightMode()

		def __OnClickSnowModeOffButton(self):
			systemSetting.SetSnowModeOption(0)
			self.RefreshSnowMode()

		def __OnClickSnowModeOnButton(self):
			systemSetting.SetSnowModeOption(1)
			self.RefreshSnowMode()

		def RefreshSnowMode(self):
			if systemSetting.GetSnowModeOption():
				self.snowModeButtonList[1].Down()
				self.snowModeButtonList[0].SetUp()
			else:
				self.snowModeButtonList[1].SetUp()
				self.snowModeButtonList[0].Down()

		def __OnClickSnowTextureModeOffButton(self):
			systemSetting.SetSnowTextureModeOption(0)
			self.RefreshSnowTextureMode()

		def __OnClickSnowTextureModeOnButton(self):
			systemSetting.SetSnowTextureModeOption(1)
			self.RefreshSnowTextureMode()

		def RefreshSnowTextureMode(self):
			if systemSetting.GetSnowTextureModeOption():
				self.snowTextureModeButtonList[1].Down()
				self.snowTextureModeButtonList[0].SetUp()
			else:
				self.snowTextureModeButtonList[1].SetUp()
				self.snowTextureModeButtonList[0].Down()

	# Show Always Name - Mode
	def RefreshAlwaysShowName(self):
		index = systemSetting.IsAlwaysShowName()
		self.alwaysShowNameButtonList[index].SetUp()
		self.alwaysShowNameButtonList[not index].Down()
	def __OnClickAlwaysShowName(self):
		systemSetting.SetAlwaysShowNameFlag(not systemSetting.IsAlwaysShowName())
		self.RefreshAlwaysShowName()
	# Show Always Name - Mode

	def __NotifyChatLine(self, text):
		chat.AppendChat(chat.CHAT_TYPE_INFO, text)

	def __SetTilingMode(self, index):
		self.__ClickRadioButton(self.tilingModeButtonList, index)
		self.tilingMode = index

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

	def __SetCurTilingMode(self):
		if background.IsSoftwareTiling():
			self.__SetTilingMode(0)
		else:
			self.__SetTilingMode(1)

	def __OnClickTilingApplyButton(self):
		self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_TILING_EXIT)
		if 0 == self.tilingMode:
			background.EnableSoftwareTiling(1)
		else:
			background.EnableSoftwareTiling(0)
		
		constinfo.restart = 1
		net.LogOutGame()

	# Show Damage - Mode
	def RefreshShowDamage(self):
		index = systemSetting.IsShowDamage()
		self.showDamageButtonList[index].SetUp()
		self.showDamageButtonList[not index].Down()
	def __OnClickShowDamage(self):
		systemSetting.SetShowDamageFlag(not systemSetting.IsShowDamage())
		self.RefreshShowDamage()
	# Show Damage - Mode

	def RefreshLanguage(self):
		if self.languageID == 0:
			self.languageButtons[0].Down()
			self.languageButtons[1].SetUp()
		else:
			self.languageButtons[1].Down()
			self.languageButtons[0].SetUp()

	def __OnClickLanguageButton(self, index):
		self.languageID = index
		self.RefreshLanguage()

	def OnEndCountDown(self):
		net.Disconnect()
		app.ShellExecute(app.GetName())
		app.Exit()

	def OnCloseQuestionDialog(self):
		if self.questionDialog:
			self.questionDialog.Close()
			self.questionDialog = None
		
		return True

	def OnPressExitKey(self):
		pass

	def __SaveLoca(self, code_page, locale):
		if app.SetLoca(code_page, locale):
			return True
		
		return False

	def OnAcceptLanguageChange(self):
		self.OnCloseQuestionDialog()
		
		locale = LOCALE_LANG_DICT[self.languageID]["locale"]
		code_page = LOCALE_LANG_DICT[self.languageID]["code_page"]
		
		if self.__SaveLoca(code_page, locale):
			net.SetLanguage(self.languageID)
			self.OnEndCountDown()

	def __OnClickLanguageApplyButton(self):
		if self.languageID == 0:
			if app.GetLocaleName() == "en":
				return
		else:
			if app.GetLocaleName() == "ae":
				return
		
		import uicommon
		questionDialog = uicommon.QuestionDialog2()
		questionDialog.SetText1(localeinfo.RESTART_CLIENT_DO_YOU_ACCEPT_1)
		questionDialog.SetText2(localeinfo.RESTART_CLIENT_DO_YOU_ACCEPT_2)
		questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnAcceptLanguageChange))
		questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
		questionDialog.SetWidth(450)
		questionDialog.Open()
		self.questionDialog = questionDialog

	def RefreshShowSalesText(self):
		index = systemSetting.IsShowSalesText()
		self.showsalesTextButtonList[not index].Down()
		self.showsalesTextButtonList[index].SetUp()

		import uiprivateshopbuilder
		uiprivateshopbuilder.UpdateADBoard()

	def __OnClickSalesTextOnButton(self):
		systemSetting.SetShowSalesTextFlag(True)
		offlineshop.ShowShopNames()
		self.RefreshShowSalesText()

	def __OnClickSalesTextOffButton(self):
		systemSetting.SetShowSalesTextFlag(False)
		offlineshop.HideShopNames()
		self.RefreshShowSalesText()

	# Sound - Mode
	def OnChangeSoundVolume(self):
		pos = self.ctrlSoundVolume.GetSliderPos()
		snd.SetSoundVolumef(pos)
		systemSetting.SetSoundVolumef(pos)
	# Sound - Mode

	# Music - Mode
	def OnChangeMusicVolume(self):
		pos = self.ctrlMusicVolume.GetSliderPos()
		snd.SetMusicVolume(pos * net.GetFieldMusicVolume())
		systemSetting.SetMusicVolume(pos)
	def __OnChangeMusic(self, fileName):
		self.selectMusicFile.SetText(fileName[:MUSIC_FILENAME_MAX_LEN])
		if musicinfo.fieldMusic != "":
			snd.FadeOutMusic("BGM/"+ musicinfo.fieldMusic)
		if fileName==uiselectmusic.DEFAULT_THEMA:
			musicinfo.fieldMusic=musicinfo.METIN2THEMA
		else:
			musicinfo.fieldMusic=fileName
		musicinfo.SaveLastPlayFieldMusic()
		if musicinfo.fieldMusic != "":
			snd.FadeInMusic("BGM/" + musicinfo.fieldMusic)
	def __OnClickChangeMusicButton(self):
		if not self.musicListDlg:
			self.musicListDlg=uiselectmusic.FileListDialog()
			self.musicListDlg.SAFE_SetSelectEvent(self.__OnChangeMusic)
		self.musicListDlg.Open()
	# Music - Mode

	if app.ENABLE_EXTENDED_PICKUP:
		def __OnClickPickupIgnoreButton(self, type, ignore):
			systemSetting.SetPickupIgnore(type, ignore)
			self.__RefreshPickupIgnoreButtons()
			
		def __RefreshPickupIgnoreButtons(self):
			for i in xrange(len(self.pickupIgnoreButtonList)):
				if systemSetting.GetPickupIgnore(i):
					self.pickupIgnoreButtonList[i].Down()
				else:
					self.pickupIgnoreButtonList[i].SetUp()

	def RefreshCameraMode(self):
		index = constinfo.GET_CAMERA_MAX_DISTANCE_INDEX()
		self.cameraModeButtonList[index].Down()
		self.cameraModeButtonList[not index].SetUp()

	def __OnClickCameraMode(self, index):
		constinfo.SET_CAMERA_MAX_DISTANCE_INDEX(not constinfo.GET_CAMERA_MAX_DISTANCE_INDEX())
		self.RefreshCameraMode()

	if app.ENABLE_FOV_OPTION:
		def __OnClickFOVButton(self, flag):
			systemSetting.SetExtendedFOV(flag)
			self.RefreshFOVOption()

		def RefreshFOVOption(self):
			if systemSetting.IsExtendedFOV():
				self.fovButtonList[1].SetUp()
				self.fovButtonList[0].Down()
			else:
				self.fovButtonList[1].Down()
				self.fovButtonList[0].SetUp()

class ScrollBarNew(ui.Window):
	SCROLLBAR_WIDTH = 7
	SCROLL_BTN_XDIST = 0
	SCROLL_BTN_YDIST = 0
	class MiddleBar(ui.DragButton):
		def __init__(self):
			ui.DragButton.__init__(self)
			self.AddFlag("movable")
			self.SetWindowName("scrollbar_middlebar")
		def MakeImage(self):
			top = ui.ExpandedImageBox()
			top.SetParent(self)
			top.LoadImage(IMG_DIR+"scrollbar/scrollbar_top.tga")
			top.AddFlag("not_pick")
			top.Show()
			topScale = ui.ExpandedImageBox()
			topScale.SetParent(self)
			topScale.SetPosition(0, top.GetHeight())
			topScale.LoadImage(IMG_DIR+"scrollbar/scrollbar_scale.tga")
			topScale.AddFlag("not_pick")
			topScale.Show()
			bottom = ui.ExpandedImageBox()
			bottom.SetParent(self)
			bottom.LoadImage(IMG_DIR+"scrollbar/scrollbar_bottom.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()
			bottomScale = ui.ExpandedImageBox()
			bottomScale.SetParent(self)
			bottomScale.LoadImage(IMG_DIR+"scrollbar/scrollbar_scale.tga")
			bottomScale.AddFlag("not_pick")
			bottomScale.Show()
			middle = ui.ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage(IMG_DIR+"scrollbar/scrollbar_mid.tga")
			middle.AddFlag("not_pick")
			middle.Show()
			self.top = top
			self.topScale = topScale
			self.bottom = bottom
			self.bottomScale = bottomScale
			self.middle = middle
		def SetSize(self, height):
			minHeight = self.top.GetHeight() + self.bottom.GetHeight() + self.middle.GetHeight()
			height = max(minHeight, height)
			ui.DragButton.SetSize(self, 10, height)
			scale = (height - minHeight) / 2 
			extraScale = 0
			if (height - minHeight) % 2 == 1:
				extraScale = 1
			self.topScale.SetRenderingRect(0, 0, 0, scale - 1)
			self.middle.SetPosition(0, self.top.GetHeight() + scale)
			self.bottomScale.SetPosition(0, self.middle.GetBottom())
			self.bottomScale.SetRenderingRect(0, 0, 0, scale - 1 + extraScale)
			self.bottom.SetPosition(0, height - self.bottom.GetHeight())
	def __init__(self):
		ui.Window.__init__(self)
		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = None
		self.eventArgs = None
		self.lockFlag = False
		self.CreateScrollBar()
		self.SetScrollBarSize(0)
		self.scrollStep = 0.4
		self.SetWindowName("NONAME_ScrollBar")
	def __del__(self):
		ui.Window.__del__(self)
	def CreateScrollBar(self):
		topImage = ui.ExpandedImageBox()
		topImage.SetParent(self)
		topImage.AddFlag("not_pick")
		topImage.LoadImage(IMG_DIR+"scrollbar/scroll_top.tga")
		topImage.Show()
		bottomImage = ui.ExpandedImageBox()
		bottomImage.SetParent(self)
		bottomImage.AddFlag("not_pick")
		bottomImage.LoadImage(IMG_DIR+"scrollbar/scroll_bottom.tga")
		bottomImage.Show()
		middleImage = ui.ExpandedImageBox()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, topImage.GetHeight())
		middleImage.LoadImage(IMG_DIR+"scrollbar/scroll_mid.tga")
		middleImage.Show()
		self.topImage = topImage
		self.bottomImage = bottomImage
		self.middleImage = middleImage
		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(ui.__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(12)
		self.middleBar = middleBar
	def Destroy(self):
		self.eventScroll = None
		self.eventArgs = None
	def SetScrollEvent(self, event, *args):
		self.eventScroll = event
		self.eventArgs = args
	def SetMiddleBarSize(self, pageScale):
		self.middleBar.SetSize(int(pageScale * float(self.GetHeight() - (self.SCROLL_BTN_YDIST*2))))
		realHeight = self.GetHeight() - (self.SCROLL_BTN_YDIST*2) - self.middleBar.GetHeight()
		self.pageSize = realHeight

	def SetScrollBarSize(self, height):
		self.SetSize(self.SCROLLBAR_WIDTH, height)
		self.pageSize = height - self.SCROLL_BTN_YDIST*2 - self.middleBar.GetHeight()
		middleImageScale = float((height - self.SCROLL_BTN_YDIST*2) - self.middleImage.GetHeight()) / float(self.middleImage.GetHeight())
		self.middleImage.SetRenderingRect(0, 0, 0, middleImageScale)
		self.bottomImage.SetPosition(0, height - self.bottomImage.GetHeight())
		self.middleBar.SetRestrictMovementArea(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST, \
			self.middleBar.GetWidth(), height - self.SCROLL_BTN_YDIST * 2)
		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST)
	def SetScrollStep(self, step):
		self.scrollStep = step
	def OnUp(self):
		self.SetPos(self.curPos-self.scrollStep)
	def OnDown(self):
		self.SetPos(self.curPos+self.scrollStep)
	def GetScrollStep(self):
		return self.scrollStep
	def GetPos(self):
		return self.curPos
	def OnUp(self):
		self.SetPos(self.curPos-self.scrollStep)
	def OnDown(self):
		self.SetPos(self.curPos+self.scrollStep)
	def SetPos(self, pos, moveEvent = True):
		pos = max(0.0, pos)
		pos = min(1.0, pos)
		newPos = float(self.pageSize) * pos
		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, int(newPos) + self.SCROLL_BTN_YDIST)
		if moveEvent == True:
			self.OnMove()
	def OnMove(self):
		if self.lockFlag:
			return
		if 0 == self.pageSize:
			return
		(xLocal, yLocal) = self.middleBar.GetLocalPosition()
		self.curPos = float(yLocal - self.SCROLL_BTN_YDIST) / float(self.pageSize)
		if self.eventScroll:
			apply(self.eventScroll, self.eventArgs)
	def OnMouseLeftButtonDown(self):
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		newPos = float(yMouseLocalPosition) / float(self.GetHeight())
		self.SetPos(newPos)
	def LockScroll(self):
		self.lockFlag = True
	def UnlockScroll(self):
		self.lockFlag = False
