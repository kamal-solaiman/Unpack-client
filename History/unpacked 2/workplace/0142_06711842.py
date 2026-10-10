# coding: latin_1

import dbg
import ui
import snd
import systemSetting
import net
import chat
import app
import chrmgr
import background
import player
import musicInfo
import uiScriptLocale
import wndMgr
import localeinfo
import event
import colorinfo
import constinfo
import uiSelectMusic

MUSIC_FILENAME_MAX_LEN = 25

blockMode = 0

class OptionDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__Initialize()
		self.__Load()

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		print " -------------------------------------- DELETE SYSTEM OPTION DIALOG"

	def __Initialize(self):
		self.tilingMode = 0
		self.titleBar = 0

################################### SKYBOX SYSTEM #######################################
		self.skyboxbutton1 = 0
		self.skyboxbutton2 = 0
		self.skyboxbutton3 = 0
		self.skyboxbutton4 = 0
		self.skyboxbutton5 = 0
		self.skyboxbutton6 = 0
		self.skyboxbutton7 = 0
		self.skyboxbutton8 = 0
		self.skyboxbutton9 = 0
		self.skyboxbutton10 = 0
		self.skyboxbutton11 = 0
		self.skyboxbutton12 = 0
		self.skyboxbutton13 = 0
		self.skyboxbutton14 = 0
		self.skyboxbutton15 = 0
		self.skyboxbutton16 = 0
		self.skyboxbutton17 = 0
		self.skyboxbutton18 = 0
		self.skyboxbutton19 = 0
		self.skyboxbutton20 = 0
		self.maviruh = 0
		self.maviruh2 = 0
		self.maviruh3 = 0
		self.maviruh4 = 0
		self.maviruh5 = 0
		self.maviruh6 = 0
		self.mr_skybox_button1 = []
		self.page_button = []
################################### SKYBOX SYSTEM #######################################

	def Destroy(self):
		self.ClearDictionary()

		self.__Initialize()
		print " -------------------------------------- DESTROY SYSTEM OPTION DIALOG"

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

################################### SKYBOX SYSTEM #######################################
			self.mr_skybox_button1.append(GetObject("skyboxbutton1"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton2"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton3"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton4"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton5"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton6"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton7"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton8"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton9"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton10"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton11"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton12"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton13"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton14"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton15"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton16"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton17"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton18"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton19"))
			self.mr_skybox_button1.append(GetObject("skyboxbutton20"))
			self.page_button.append(GetObject("page_button1"))
			self.page_button.append(GetObject("page_button2"))
			self.page_button.append(GetObject("page_button3"))
			self.page_button.append(GetObject("page_button4"))
			self.page_button.append(GetObject("page_button5"))
			self.page_button.append(GetObject("page_button6"))
			self.page_button.append(GetObject("page_button7"))
			self.page_button.append(GetObject("page_button8"))
			self.maviruh = self.GetChild("maviruh")
			self.maviruh2 = self.GetChild("maviruh2")
			self.maviruh3 = self.GetChild("maviruh3")
			self.maviruh4 = self.GetChild("maviruh4")
			self.maviruh5 = self.GetChild("maviruh5")
			self.maviruh6 = self.GetChild("maviruh6")
################################### SKYBOX SYSTEM #######################################

		except:
			import exception
			exception.Abort("OptionDialog.__Load_BindObject")

	def __Load(self):
		self.__Load_LoadScript("uiscript/advanced_skybox_option.py")
		self.__Load_BindObject()

		self.SetCenterPosition()
		
		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))
################################### SKYBOX SYSTEM #######################################
		self.maviruh.SetEvent(ui.__mem_func__(self.MaviRuh))
		self.maviruh2.SetEvent(ui.__mem_func__(self.MaviRuh))
		self.maviruh3.SetEvent(ui.__mem_func__(self.MaviRuh))
		self.maviruh4.SetEvent(ui.__mem_func__(self.MaviRuh))
		self.maviruh5.SetEvent(ui.__mem_func__(self.MaviRuh))
		self.maviruh6.SetEvent(ui.__mem_func__(self.MaviRuh))
		self.page_button[0].SAFE_SetEvent(self.Page_Button1)
		self.page_button[1].SAFE_SetEvent(self.Page_Button2)
		self.page_button[2].SAFE_SetEvent(self.Page_Button3)
		self.page_button[3].SAFE_SetEvent(self.Page_Button4)
		self.page_button[4].SAFE_SetEvent(self.Page_Button5)
		self.page_button[5].SAFE_SetEvent(self.Page_Button6)
		self.page_button[6].SAFE_SetEvent(self.Page_Button7)
		self.page_button[7].SAFE_SetEvent(self.Page_Button8)
################################### SKYBOX SYSTEM #######################################

################################### SKYBOX SYSTEM #######################################
		self.mr_skybox_button1[0].SAFE_SetEvent(self.__OnClickOneSkyboxSelectButton)
		self.mr_skybox_button1[1].SAFE_SetEvent(self.__OnClickTwoSkyboxSelectButton)
		self.mr_skybox_button1[2].SAFE_SetEvent(self.__OnClickTreeSkyboxSelectButton)
		self.mr_skybox_button1[3].SAFE_SetEvent(self.__OnClickFourSkyboxSelectButton)
		self.mr_skybox_button1[4].SAFE_SetEvent(self.__OnClickFiveSkyboxSelectButton)
		self.mr_skybox_button1[5].SAFE_SetEvent(self.__OnClickSixSkyboxSelectButton)
		self.mr_skybox_button1[6].SAFE_SetEvent(self.__OnClick7SkyboxSelectButton)
		self.mr_skybox_button1[7].SAFE_SetEvent(self.__OnClick8SkyboxSelectButton)
		self.mr_skybox_button1[8].SAFE_SetEvent(self.__OnClick9SkyboxSelectButton)
		self.mr_skybox_button1[9].SAFE_SetEvent(self.__OnClick10SkyboxSelectButton)
		self.mr_skybox_button1[10].SAFE_SetEvent(self.__OnClick11SkyboxSelectButton)
		self.mr_skybox_button1[11].SAFE_SetEvent(self.__OnClick12SkyboxSelectButton)
		self.mr_skybox_button1[12].SAFE_SetEvent(self.__OnClick13SkyboxSelectButton)
		self.mr_skybox_button1[13].SAFE_SetEvent(self.__OnClick14SkyboxSelectButton)
		self.mr_skybox_button1[14].SAFE_SetEvent(self.__OnClick15SkyboxSelectButton)
		self.mr_skybox_button1[15].SAFE_SetEvent(self.__OnClick16SkyboxSelectButton)
		self.mr_skybox_button1[16].SAFE_SetEvent(self.__OnClick17SkyboxSelectButton)
		self.mr_skybox_button1[17].SAFE_SetEvent(self.__OnClick18SkyboxSelectButton)
		self.mr_skybox_button1[18].SAFE_SetEvent(self.__OnClick19SkyboxSelectButton)
		self.mr_skybox_button1[19].SAFE_SetEvent(self.__OnClick20SkyboxSelectButton)
################################### SKYBOX SYSTEM #######################################

################################### SKYBOX SYSTEM #######################################
	def __OnClickOneSkyboxSelectButton(self):
		background.RegisterEnvironmentData(0, "d:/ymir work/environment/skybox1.msenv")
		background.SetEnvironmentData(0)
		constinfo.Hava = 0
		self.RefreshShowSkybox1()

	def __OnClickTwoSkyboxSelectButton(self):
		background.RegisterEnvironmentData(1, "d:/ymir work/environment/skybox2.msenv")
		background.SetEnvironmentData(1)
		constinfo.Hava = 1
		self.RefreshShowSkybox1()

	def __OnClickTreeSkyboxSelectButton(self):
		background.RegisterEnvironmentData(2, "d:/ymir work/environment/skybox3.msenv")
		background.SetEnvironmentData(2)
		constinfo.Hava = 2
		self.RefreshShowSkybox1()

	def __OnClickFourSkyboxSelectButton(self):
		background.RegisterEnvironmentData(3, "d:/ymir work/environment/skybox4.msenv")
		background.SetEnvironmentData(3)
		constinfo.Hava = 3
		self.RefreshShowSkybox1()

	def __OnClickFiveSkyboxSelectButton(self):
		background.RegisterEnvironmentData(4, "d:/ymir work/environment/skybox5.msenv")
		background.SetEnvironmentData(4)
		constinfo.Hava = 4
		self.RefreshShowSkybox1()

	def __OnClickSixSkyboxSelectButton(self):
		background.RegisterEnvironmentData(5, "d:/ymir work/environment/skybox6.msenv")
		background.SetEnvironmentData(5)
		constinfo.Hava = 5
		self.RefreshShowSkybox1()

	def __OnClick7SkyboxSelectButton(self):
		background.RegisterEnvironmentData(6, "d:/ymir work/environment/skybox7.msenv")
		background.SetEnvironmentData(6)
		constinfo.Hava = 6
		self.RefreshShowSkybox1()

	def __OnClick8SkyboxSelectButton(self):
		background.RegisterEnvironmentData(7, "d:/ymir work/environment/skybox8.msenv")
		background.SetEnvironmentData(7)
		constinfo.Hava = 7
		self.RefreshShowSkybox1()

	def __OnClick9SkyboxSelectButton(self):
		background.RegisterEnvironmentData(8, "d:/ymir work/environment/skybox9.msenv")
		background.SetEnvironmentData(8)
		constinfo.Hava = 8
		self.RefreshShowSkybox1()

	def __OnClick10SkyboxSelectButton(self):
		background.RegisterEnvironmentData(9, "d:/ymir work/environment/skybox1.msenv")
		background.SetEnvironmentData(9)
		constinfo.Hava = 9
		self.RefreshShowSkybox1()

	def __OnClick11SkyboxSelectButton(self):
		background.RegisterEnvironmentData(10, "d:/ymir work/environment/ridack_day2.msenv")
		background.SetEnvironmentData(10)
		constinfo.Hava = 10
		self.RefreshShowSkybox1()

	def __OnClick12SkyboxSelectButton(self):
		background.RegisterEnvironmentData(11, "d:/ymir work/environment/turiks_nebel_sky_by_reco.msenv")
		background.SetEnvironmentData(11)
		constinfo.Hava = 11
		self.RefreshShowSkybox1()

	def __OnClick13SkyboxSelectButton(self):
		background.RegisterEnvironmentData(12, "d:/ymir work/environment/niebo_radeon.msenv")
		background.SetEnvironmentData(12)
		constinfo.Hava = 12
		self.RefreshShowSkybox1()

	def __OnClick14SkyboxSelectButton(self):
		background.RegisterEnvironmentData(13, "d:/ymir work/environment/skybox_reco_lightblue.msenv")
		background.SetEnvironmentData(13)
		constinfo.Hava = 13
		self.RefreshShowSkybox1()

	def __OnClick15SkyboxSelectButton(self):
		background.RegisterEnvironmentData(14, "d:/ymir work/environment/skybox_reco_red_v1.msenv")
		background.SetEnvironmentData(14)
		constinfo.Hava = 14
		self.RefreshShowSkybox1()

	def __OnClick16SkyboxSelectButton(self):
		background.RegisterEnvironmentData(15, "d:/ymir work/environment/ridack_valentine.msenv")
		background.SetEnvironmentData(15)
		constinfo.Hava = 15
		self.RefreshShowSkybox1()

	def __OnClick17SkyboxSelectButton(self):
		background.RegisterEnvironmentData(16, "d:/ymir work/environment/moonlight04.msenv")
		background.SetEnvironmentData(16)
		constinfo.Hava = 16
		self.RefreshShowSkybox1()

	def __OnClick18SkyboxSelectButton(self):
		background.RegisterEnvironmentData(17, "d:/ymir work/environment/skyboxridack39_g.msenv")
		background.SetEnvironmentData(17)
		constinfo.Hava = 17
		self.RefreshShowSkybox1()

	def __OnClick19SkyboxSelectButton(self):
		background.RegisterEnvironmentData(18, "d:/ymir work/environment/ridacksky21.msenv")
		background.SetEnvironmentData(18)
		constinfo.Hava = 18
		self.RefreshShowSkybox1()

	def __OnClick20SkyboxSelectButton(self):
		background.RegisterEnvironmentData(19, "d:/ymir work/environment/ridacksky15.msenv")
		background.SetEnvironmentData(19)
		constinfo.Hava = 19
		self.RefreshShowSkybox1()

	def RefreshShowSkybox1(self):
		if constinfo.Hava == 1:
			self.mr_skybox_button1[0].Down()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 2:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].Down()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 3:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].Down()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 4:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].Down()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 5:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].Down()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 6:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].Down()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 7:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].Down()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 8:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].Down()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 9:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].Down()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 10:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].Down()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 11:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].Down()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 12:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].Down()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 13:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].Down()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 14:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].Down()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 15:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].Down()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 16:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].Down()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 17:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].Down()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 18:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].Down()
			self.mr_skybox_button1[19].SetUp()
		elif constinfo.Hava == 19:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].SetUp()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].Down()
		else:
			self.mr_skybox_button1[0].SetUp()
			self.mr_skybox_button1[1].Down()
			self.mr_skybox_button1[2].SetUp()
			self.mr_skybox_button1[3].SetUp()
			self.mr_skybox_button1[4].SetUp()
			self.mr_skybox_button1[5].SetUp()
			self.mr_skybox_button1[6].SetUp()
			self.mr_skybox_button1[7].SetUp()
			self.mr_skybox_button1[8].SetUp()
			self.mr_skybox_button1[9].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[10].SetUp()
			self.mr_skybox_button1[11].SetUp()
			self.mr_skybox_button1[12].SetUp()
			self.mr_skybox_button1[13].SetUp()
			self.mr_skybox_button1[14].SetUp()
			self.mr_skybox_button1[15].SetUp()
			self.mr_skybox_button1[16].SetUp()
			self.mr_skybox_button1[17].SetUp()
			self.mr_skybox_button1[18].SetUp()
			self.mr_skybox_button1[19].SetUp()

	def RefreshShowPage(self):
		if constinfo.Page == 1:
			self.page_button[0].Down()
			self.page_button[1].SetUp()
			self.page_button[2].SetUp()
			self.page_button[3].SetUp()
			self.page_button[4].SetUp()
			self.page_button[5].SetUp()
			self.page_button[6].SetUp()
			self.page_button[7].SetUp()
		elif constinfo.Page == 2:
			self.page_button[0].SetUp()
			self.page_button[1].SetUp()
			self.page_button[2].Down()
			self.page_button[3].SetUp()
			self.page_button[4].SetUp()
			self.page_button[5].SetUp()
			self.page_button[6].SetUp()
			self.page_button[7].SetUp()
		elif constinfo.Page == 3:
			self.page_button[0].SetUp()
			self.page_button[1].SetUp()
			self.page_button[2].SetUp()
			self.page_button[3].Down()
			self.page_button[4].SetUp()
			self.page_button[5].SetUp()
			self.page_button[6].SetUp()
			self.page_button[7].SetUp()
		elif constinfo.Page == 4:
			self.page_button[0].SetUp()
			self.page_button[1].SetUp()
			self.page_button[2].SetUp()
			self.page_button[3].SetUp()
			self.page_button[4].Down()
			self.page_button[5].SetUp()
			self.page_button[6].SetUp()
			self.page_button[7].SetUp()
		elif constinfo.Page == 5:
			self.page_button[0].SetUp()
			self.page_button[1].SetUp()
			self.page_button[2].SetUp()
			self.page_button[3].SetUp()
			self.page_button[4].SetUp()
			self.page_button[5].Down()
			self.page_button[6].SetUp()
			self.page_button[7].SetUp()
		elif constinfo.Page == 6:
			self.page_button[0].SetUp()
			self.page_button[1].SetUp()
			self.page_button[2].SetUp()
			self.page_button[3].SetUp()
			self.page_button[4].SetUp()
			self.page_button[5].SetUp()
			self.page_button[6].Down()
			self.page_button[7].SetUp()
		elif constinfo.Page == 7:
			self.page_button[0].SetUp()
			self.page_button[1].SetUp()
			self.page_button[2].SetUp()
			self.page_button[3].SetUp()
			self.page_button[4].SetUp()
			self.page_button[5].SetUp()
			self.page_button[6].SetUp()
			self.page_button[7].Down()
		else:
			self.page_button[0].SetUp()
			self.page_button[1].Down()
			self.page_button[2].SetUp()
			self.page_button[3].SetUp()
			self.page_button[4].SetUp()
			self.page_button[5].SetUp()
			self.page_button[6].SetUp()
			self.page_button[7].SetUp()

	def Page_Button1(self):
		self.maviruh.Show()
		self.maviruh2.Hide()
		self.maviruh3.Hide()
		self.maviruh4.Hide()
		self.maviruh5.Hide()
		self.maviruh6.Hide()
		constinfo.Page = 0
		self.RefreshShowPage()

	def Page_Button2(self):
		self.maviruh.Hide()
		self.maviruh2.Show()
		self.maviruh3.Hide()
		self.maviruh4.Hide()
		self.maviruh5.Hide()
		self.maviruh6.Hide()
		constinfo.Page = 1
		self.RefreshShowPage()

	def Page_Button3(self):
		self.maviruh.Hide()
		self.maviruh2.Hide()
		self.maviruh3.Show()
		self.maviruh4.Hide()
		self.maviruh5.Hide()
		self.maviruh6.Hide()
		constinfo.Page = 2
		self.RefreshShowPage()

	def Page_Button4(self):
		self.maviruh.Hide()
		self.maviruh2.Hide()
		self.maviruh3.Hide()
		self.maviruh4.Show()
		self.maviruh5.Hide()
		self.maviruh6.Hide()
		constinfo.Page = 3
		self.RefreshShowPage()

	def Page_Button5(self):
		self.maviruh.Hide()
		self.maviruh2.Hide()
		self.maviruh3.Hide()
		self.maviruh4.Hide()
		self.maviruh5.Show()
		self.maviruh6.Hide()
		constinfo.Page = 4
		self.RefreshShowPage()

	def Page_Button6(self):
		self.maviruh.Hide()
		self.maviruh2.Hide()
		self.maviruh3.Hide()
		self.maviruh4.Hide()
		self.maviruh5.Hide()
		self.maviruh6.Show()
		constinfo.Page = 5
		self.RefreshShowPage()

	def Page_Button7(self):
		self.maviruh.Show()
		self.maviruh2.Hide()
		self.maviruh3.Hide()
		self.maviruh4.Hide()
		self.maviruh5.Hide()
		self.maviruh6.Hide()
		constinfo.Page = 6
		self.RefreshShowPage()

	def Page_Button8(self):
		self.maviruh.Hide()
		self.maviruh2.Show()
		self.maviruh3.Hide()
		self.maviruh4.Hide()
		self.maviruh5.Hide()
		self.maviruh6.Hide()
		constinfo.Page = 7
		self.RefreshShowPage()
################################### SKYBOX SYSTEM #######################################

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
		self.maviruh.Show()
		self.maviruh2.Hide()
		self.maviruh3.Hide()
		self.maviruh4.Hide()
		self.maviruh5.Hide()
		self.maviruh6.Hide()
		ui.ScriptWindow.Show(self)

	def Close(self):
		self.Hide()

	def MaviRuh(self):
		self.Hide()

	def __NotifyChatLine(self, text):
		chat.AppendChat(chat.CHAT_TYPE_INFO, text)
		
