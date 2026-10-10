# coding: latin_1

import app

import ui
import systemSetting
import interfacemodule

class OptionDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__Initialize()
		self.__Load()
		
		# self.__RefreshPickUpModeButtons()
		self.__RefreshPickupIgnoreButtons()

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		print " -------------------------------------- DELETE DROP OPTION DIALOG"

	def __Initialize(self):
		self.board = 0
		
		# self.pickupModeButtonList = []
		self.pickupIgnoreButtonList = []

	def Destroy(self):
		self.ClearDictionary()
		self.__Initialize()
		print " -------------------------------------- DESTROY DROP OPTION DIALOG"
	
	def __Load_LoadScript(self, fileName):
		try:
			pyScriptLoader = ui.PythonScriptLoader()
			pyScriptLoader.LoadScriptFile(self, fileName)
		except:
			import exception
			exception.Abort("OptionDialog.__Load_LoadScript")

	def __Load_BindObject(self):
		try:
			# for mode in ["single", "all"]:
				# self.pickupModeButtonList.append(self.GetChild("pickup_mode_" + mode))
			
			for type in ["weapon", "armor", "head", "shield", "wrist", "foots", "neck", "ear"]:
				self.pickupIgnoreButtonList.append(self.GetChild("drops_ignore_" + type))
			
		except:
			import exception
			exception.Abort("OptionDialog.__Load_BindObject")

	def __Load(self):
		self.__Load_LoadScript("uiscript/pickupoptiondialog.py")
		self.__Load_BindObject()
		self.SetCenterPosition()

		self.GetChild("board").SetCloseEvent(ui.__mem_func__(self.Close))
		
		# for i in xrange(len(self.pickupModeButtonList)):
			# self.pickupModeButtonList[i].SetEvent(lambda mode = i : self.__OnClickPickupModeButton(mode))
			
		for i in xrange(len(self.pickupIgnoreButtonList)):
			self.pickupIgnoreButtonList[i].SetToggleUpEvent(lambda type = i, ignore = 0 : self.__OnClickPickupIgnoreButton(type, ignore))
			self.pickupIgnoreButtonList[i].SetToggleDownEvent(lambda type = i, ignore = 1 : self.__OnClickPickupIgnoreButton(type, ignore))

	# def __OnClickPickupModeButton(self, mode):
		# systemSetting.SetPickupMode(mode)
		# self.__RefreshPickUpModeButtons()
		
	# def __RefreshPickUpModeButtons(self):
		# if systemSetting.GetPickupMode() == systemSetting.PICKUP_MODE_SINGLE:
			# self.pickupModeButtonList[0].Down()
			# self.pickupModeButtonList[1].SetUp()
		# elif systemSetting.GetPickupMode() == systemSetting.PICKUP_MODE_ALL:
			# self.pickupModeButtonList[0].SetUp()
			# self.pickupModeButtonList[1].Down()
		
	def __OnClickPickupIgnoreButton(self, type, ignore):
		systemSetting.SetPickupIgnore(type, ignore)
		self.__RefreshPickupIgnoreButtons()
		
	def __RefreshPickupIgnoreButtons(self):
		for i in xrange(len(self.pickupIgnoreButtonList)):
			if systemSetting.GetPickupIgnore(i):
				self.pickupIgnoreButtonList[i].Down()
			else:
				self.pickupIgnoreButtonList[i].SetUp()
				
	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Show(self):
		ui.ScriptWindow.Show(self)

	def Close(self):
		self.Hide()

