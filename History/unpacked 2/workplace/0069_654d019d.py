# coding: latin_1

import app
import chrmgr
import net
import player

import ui
import uiscriptlocale
import background
import wndMgr
import constinfo
import playersettingmodule
import colorinfo
import localeinfo
import emotion
import playerLoad
from _weakref import proxy

##################################
## loadingFunctions
##################################
NAME_COLOR_DICT = {
	chrmgr.NAMECOLOR_PC : colorinfo.CHR_NAME_RGB_PC,
	chrmgr.NAMECOLOR_NPC : colorinfo.CHR_NAME_RGB_NPC,
	chrmgr.NAMECOLOR_MOB : colorinfo.CHR_NAME_RGB_MOB,
	chrmgr.NAMECOLOR_PVP : colorinfo.CHR_NAME_RGB_PVP,
	chrmgr.NAMECOLOR_PK : colorinfo.CHR_NAME_RGB_PK,
	chrmgr.NAMECOLOR_PARTY : colorinfo.CHR_NAME_RGB_PARTY,
	chrmgr.NAMECOLOR_WARP : colorinfo.CHR_NAME_RGB_WARP,
	chrmgr.NAMECOLOR_WAYPOINT : colorinfo.CHR_NAME_RGB_WAYPOINT,
	chrmgr.NAMECOLOR_BOSS : colorinfo.CHR_NAME_RGB_BOSS,
	chrmgr.NAMECOLOR_EMPIRE_MOB : colorinfo.CHR_NAME_RGB_EMPIRE_MOB,
	chrmgr.NAMECOLOR_EMPIRE_NPC : colorinfo.CHR_NAME_RGB_EMPIRE_NPC,
	chrmgr.NAMECOLOR_EMPIRE_PC+1 : colorinfo.CHR_NAME_RGB_EMPIRE_PC_A,
	chrmgr.NAMECOLOR_EMPIRE_PC+2 : colorinfo.CHR_NAME_RGB_EMPIRE_PC_B,
	chrmgr.NAMECOLOR_EMPIRE_PC+3 : colorinfo.CHR_NAME_RGB_EMPIRE_PC_C,
}

TITLE_COLOR_LIST = (
	colorinfo.TITLE_RGB_GOOD_4,
	colorinfo.TITLE_RGB_GOOD_3,
	colorinfo.TITLE_RGB_GOOD_2,
	colorinfo.TITLE_RGB_GOOD_1,
	colorinfo.TITLE_RGB_NORMAL,
	colorinfo.TITLE_RGB_EVIL_1,
	colorinfo.TITLE_RGB_EVIL_2,
	colorinfo.TITLE_RGB_EVIL_3,
	colorinfo.TITLE_RGB_EVIL_4,
)

def __main__():
	## RegisterColor
	if app.DOMINIUM_PVP_SYSTEM:
		NAME_COLOR_DICT.update({chrmgr.NAMECOLOR_TEAM_A : (255, 31, 31),})
		NAME_COLOR_DICT.update({chrmgr.NAMECOLOR_TEAM_B : (10, 135, 245),})
	for nameIndex, nameColor in NAME_COLOR_DICT.items():
		chrmgr.RegisterNameColor(nameIndex, *nameColor)

	for titleIndex, titleColor in enumerate(TITLE_COLOR_LIST):
		chrmgr.RegisterTitleColor(titleIndex, *titleColor)
		
	## RegisterTitleName
	if app.ENABLE_GENDER_ALIGNMENT:
		for titleNameIndex, (titleNameFemale, titleNameMale) in enumerate(zip(localeinfo.TITLE_NAME_DICT[localeinfo.GENDER_FEMALE], localeinfo.TITLE_NAME_DICT[localeinfo.GENDER_MALE])):
			chrmgr.RegisterTitleName(titleNameIndex, titleNameFemale, titleNameMale)
	else:
		for titleIndex, titleName in enumerate(localeinfo.TITLE_NAME_LIST):
			chrmgr.RegisterTitleName(titleIndex, titleName)
		
	## RegisterEmotionIcon	
	emotion.RegisterEmotionIcons()
		
	## RegisterDungeonMapName	
	dungeonMapNameList = ("metin2_map_spiderdungeon", "metin2_map_monkeydungeon", "metin2_map_monkeydungeon_02", "metin2_map_monkeydungeon_03", "metin2_map_deviltower1")
	for dungeonMapName in dungeonMapNameList:
		background.RegisterDungeonMapName(dungeonMapName)
		
	## RegisterGuildLeaderGradeName
	for index, name in enumerate(localeinfo.GUILD_LEADER_GRADE_NAME_LIST):
		chrmgr.RegisterGuildLeaderGradeName(index, name)

	if hasattr(chrmgr, "RegisterGuildBandName"):
		for bandIndex in xrange(1, 5):
			chrmgr.RegisterGuildBandName(bandIndex, getattr(localeinfo, "GUILD_BAND%d_NAME" % bandIndex, ("Established", "Renowned", "Exalted", "Legendary")[bandIndex - 1]))
		
	## LoadGuildBuilding
	playersettingmodule.LoadGuildBuildingList(localeinfo.GUILD_BUILDING_LIST_TXT)
	## LoadRaceHeight
	#playersettingmodule.LoadRaceHeight()

##################################
## LoadingWindow
##################################
class LoadingWindow(ui.ScriptWindow):
	def __init__(self, stream):
		print "NEW LOADING WINDOW -------------------------------------------------------------------------------"
		ui.Window.__init__(self)
		net.SetPhaseWindow(net.PHASE_WINDOW_LOAD, self)
		self.stream=stream
		self.loadingImage=0
		self.loadingGage=0
		self.errMsg=0
		self.update=0
		self.playerX=0
		self.playerY=0
		self.loadStepList=[]

	def __del__(self):
		print "---------------------------------------------------------------------------- DELETE LOADING WINDOW"
		net.SetPhaseWindow(net.PHASE_WINDOW_LOAD, 0)
		ui.Window.__del__(self)

	def Open(self):
		print "OPEN LOADING WINDOW -------------------------------------------------------------------------------"
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/LoadingWindow1.py")
		except:
			import exception
			exception.Abort("LodingWindow.Open - LoadScriptFile Error")

		try:
			self.errMsg=self.GetChild("ErrorMessage")
			self.gageBoard=self.GetChild("GageBoard")
			self.background=self.GetChild("BackGround")
		except:
			import exception
			exception.Abort("LodingWindow.Open - LoadScriptFile Error")

		self.errMsg.Hide()

		## Character login: show background, hide GIF
		## Teleport (in-game): show GIF, hide background
		if constinfo.PLAYER_IN_GAME:
			self.background.Hide()
			self.gageBoard.Show()
		else:
			self.background.Show()
			self.gageBoard.Hide()

		if app.USE_OFFLINESHOP:
			constinfo.shopSearchWaitTime=0

		self.Show()
		chrSlot=self.stream.GetCharacterSlot()
		net.SendSelectCharacterPacket(chrSlot)
		app.SetFrameSkip(0)

	def Close(self):
		print "---------------------------------------------------------------------------- CLOSE LOADING WINDOW\n"

		app.SetFrameSkip(1)

		self.loadStepList=[]
		self.loadingImage=0
		# self.loadingGage=0
		# self.errMsg=0
		self.ClearDictionary()
		self.Hide()

	def OnPressEscapeKey(self):
		## no skip loading because its forced to have only one per client start
		#app.SetFrameSkip(1)
		#self.stream.SetLoginPhase()
		return True

	def __SetNext(self, next):
		if next:
			self.update=ui.__mem_func__(next)
		else:
			self.update=0

	def LoadData(self, playerX, playerY):
		self.playerX=playerX
		self.playerY=playerY

		if app.ENABLE_FAST_WARP_UI:
			# FAST_WARP_UI: run the single load step inline instead of waiting for
			# the next OnUpdate tick - saves one frame of dead loading time.
			try:
				self.__StartGame()
			except:
				dbg.TraceError(" !!! Failed to load game data (inline start)")
				app.Exit()
			return

		self.loadStepList=[
			(100, ui.__mem_func__(self.__StartGame)),
		]

	def OnUpdate(self):
		if len(self.loadStepList)>0:
			(progress, runFunc)=self.loadStepList[0]
			startTime = app.GetGlobalTime()

			try:
				runFunc()
			except:
				# self.errMsg.Show()
				self.loadStepList=[]
				dbg.TraceError(" !!! Failed to load game data : STEP [%d]" % (progress))
				app.Exit()
				return

			self.loadStepList.pop(0)

	def __StartGame(self):
		background.SetViewDistanceSet(background.DISTANCE0, 25600)
		background.SelectViewDistanceNum(background.DISTANCE0)
		app.SetGlobalCenterPosition(self.playerX, self.playerY)
		background.RegisterEnvironmentData(background.DAY_MODE_DARK, constinfo.ENVIRONMENT_NIGHT)

		net.StartGame()