# coding: latin_1

import app

import ui
import localeinfo
import background

class Cooldown(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.LeftTime = None
		self.CurrentFloor = None
		self.CoolTimeImage = None
		self.Time = 0
		self.NextFloor = 0
		self.Floor = 0
		self.Floor2 = 0
		self.CoolTime = 0.
		self.startTime = 0.
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/map_info.py")
		except:
			import exception
			exception.Abort("Cooldown.__LoadWindow.UIScript/map_info.py")

		self.LeftTime = self.GetChild("LeftTime")
		self.CurrentFloor = self.GetChild("CurrentFloor")
		self.CoolTimeImage = self.GetChild("CoolTime")

	def RefreshDungeonTimer(self, Time, Floor):
		self.CoolTimeImage.Hide()
		#self.Time = float(Time)
		self.CoolTime = float(Time)
		self.Floor = int(Floor)
		self.CoolTimeImage.Show()
		self.startTime = app.GetTime() + 0.5
		self.CoolTimeImage.SetCoolTime(self.CoolTime)
		self.CoolTimeImage.SetStartCoolTime(self.startTime)
		if background.GetCurrentMapName() == "defensawe_hydra":
			self.CurrentFloor.SetText("{} {}".format(localeinfo.WAVE_NUMBER,int(self.Floor)))
		else:
			self.CurrentFloor.SetText("{} {}".format(localeinfo.WAVE_NUMBER,int(self.Floor)))

		self.Show()

	def RefreshDungeonFloor(self, Floor2):
		self.Floor2 = int(Floor2)
		if background.GetCurrentMapName() == "defensawe_hydra":
			self.CurrentFloor.SetText("{} {}".format(localeinfo.WAVE_NUMBER,int(self.Floor2)))
		else:
			self.CurrentFloor.SetText("{} {}".format(localeinfo.WAVE_NUMBER,int(self.Floor2)))
		self.Show()

	def OnUpdate(self):
		leftTime = max(0, self.startTime + self.CoolTime - app.GetTime() + 0.5)
		leftMin = int(leftTime/60)
		leftSecond = int(leftTime%60)
		if leftSecond == 0:
			self.LeftTime.SetText("00:00")
		else:
			self.LeftTime.SetText("%02d:%02d" % (leftMin, leftSecond))

	def Close(self):
		self.Hide()

	def Destroy(self):
		self.ClearDictionary()
		self.LeftTime = 0
		self.CurrentFloor = 0
		self.CoolTimeImage = 0
		self.Time = 0
		self.NextFloor = 0
		self.Floor = 0
		self.Floor2 = 0
		self.CoolTime = 0
		self.startTime = 0
		self.Hide()
