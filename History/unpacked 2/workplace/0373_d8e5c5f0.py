# coding: latin_1

import app
import chat
import pvp_tournament

if app.PVP_HAVE_GUI:
	import grp
	import wndMgr

import ui
import localeinfo
import playersettingmodule

FACE_IMAGE_DICT = {\
	playersettingmodule.RACE_WARRIOR_M : "warrior_m.sub",
	playersettingmodule.RACE_ASSASSIN_W : "assassin_w.sub",
	playersettingmodule.RACE_SURA_M : "sura_m.sub",
	playersettingmodule.RACE_SHAMAN_W : "shaman_w.sub",
	playersettingmodule.RACE_WARRIOR_W : "warrior_w.sub",
	playersettingmodule.RACE_ASSASSIN_M : "assassin_m.sub",
	playersettingmodule.RACE_SURA_W : "sura_w.sub",
	playersettingmodule.RACE_SHAMAN_M : "shaman_m.sub",
}

if app.ENABLE_WOLFMAN_CHARACTER:
	FACE_IMAGE_DICT[playersettingmodule.RACE_WOLFMAN_M] = "wolfman_m.sub"

class AdminPanel(ui.ScriptWindow):
	childrenDictUI = {}

	pvpTypesDict = {\
		0: localeinfo.PVP_TOURNAMENT_ALL_CHARACTER,
		1: localeinfo.PVP_TOURNAMENT_ONLY_WARRIOR,
		2: localeinfo.PVP_TOURNAMENT_ONLY_ASSASSIN,
		3: localeinfo.PVP_TOURNAMENT_ONLY_SURA,
		4: localeinfo.PVP_TOURNAMENT_ONLY_SHAMAN
	}

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.titleUI = None
		self.boardUI = None
		self.subBoardUI = None

		self.isLoaded = 0

		self.LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		for k, v in self.childrenDictUI.items():
			if k == "pvpType":
				continue
			elif k == "pvpTypeComboBox":
				v.Destroy()

			del v
			v = None

		self.childrenDictUI = {}

		self.titleUI = None
		self.boardUI = None
		self.subBoardUI = None

		self.isLoaded = 0

		self.ClearDictionary()

	def LoadWindow(self):
		if self.isLoaded != 0:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/pvptournament_admin_window.py")

			self.boardUI = self.GetChild("BoardUI")

			self.titleUI = self.GetChild("TitleBarUI")
			self.titleUI.SetCloseEvent(ui.__mem_func__(self.Hide))

			self.subBoardUI = self.GetChild("ThinBoardUI")

			START_Y_POSITION = 20
			START_X_POSITION = 15

			tmpUI = ui.TextLine()
			tmpUI.SetParent(self.subBoardUI)

			if localeinfo.IsARABIC():
				tmpUI.SetHorizontalAlignRight()
				tmpUI.SetPosition(START_X_POSITION + 250, START_Y_POSITION)
			else:
				tmpUI.SetHorizontalAlignLeft()
				tmpUI.SetPosition(START_X_POSITION, START_Y_POSITION)

			tmpUI.SetText(localeinfo.PVP_TOURNAMENT_PVP_TYPE)
			tmpUI.Show()

			self.childrenDictUI["pvpTypeText"] = tmpUI
			pvpTypeText = self.childrenDictUI["pvpTypeText"]

			self.childrenDictUI["pvpType"] = 0

			START_Y_POSITION += 30

			tmpUI = ui.TextLine()
			tmpUI.SetParent(self.subBoardUI)

			if localeinfo.IsARABIC():
				tmpUI.SetHorizontalAlignRight()
				tmpUI.SetPosition(START_X_POSITION + tmpUI.GetTextSize()[0] + 55,\
											START_Y_POSITION)
			else:
				tmpUI.SetHorizontalAlignLeft()
				tmpUI.SetPosition(START_X_POSITION, START_Y_POSITION)

			tmpUI.SetText(localeinfo.PVP_TOURNAMENT_MIN_LEVEL)
			tmpUI.Show()

			self.childrenDictUI["pvpMinLvLText"] = tmpUI
			pvpMinLvLText = self.childrenDictUI["pvpMinLvLText"]

			tmpUI = ui.SlotBar()
			tmpUI.SetParent(self.subBoardUI)
			tmpUI.SetSize(192 / 4, 13 + 2)

			if localeinfo.IsARABIC():
				tmpUI.SetPosition(START_X_POSITION, START_Y_POSITION)
			else:
				tmpUI.SetPosition(START_X_POSITION + pvpMinLvLText.GetTextSize()[0] + 15,\
													START_Y_POSITION)

			tmpUI.Show()

			self.childrenDictUI["pvpMinLvLEditLineSlot"] = tmpUI
			pvpMinLvLEditLineSlot = self.childrenDictUI["pvpMinLvLEditLineSlot"]

			tmpUI = ui.EditLine()
			tmpUI.SetParent(pvpMinLvLEditLineSlot)
			tmpUI.SetPosition(2, 1)
			tmpUI.SetSize(pvpMinLvLEditLineSlot.GetWidth(),\
										pvpMinLvLEditLineSlot.GetHeight())
			tmpUI.SetEscapeEvent(ui.__mem_func__(self.OnPressEscapeKey))
			tmpUI.SetNumberMode()
			tmpUI.SetMax(3)
			tmpUI.Show()

			self.childrenDictUI["pvpMinLvLEditLine"] = tmpUI
			pvpMinLvLEditLine = self.childrenDictUI["pvpMinLvLEditLine"]

			tmpUI = ui.TextLine()
			tmpUI.SetParent(self.subBoardUI)

			if localeinfo.IsARABIC():
				tmpUI.SetHorizontalAlignRight()
				tmpUI.SetPosition(START_X_POSITION + pvpMinLvLText.GetTextSize()[0] + 30 + pvpMinLvLEditLineSlot.GetWidth() + 30 + tmpUI.GetTextSize()[0] + 30, START_Y_POSITION)
			else:
				tmpUI.SetHorizontalAlignLeft()
				tmpUI.SetPosition(START_X_POSITION + pvpMinLvLText.GetTextSize()[0] + 15 + pvpMinLvLEditLineSlot.GetWidth() + 15, START_Y_POSITION)

			tmpUI.SetText(localeinfo.PVP_TOURNAMENT_MAX_LEVEL)
			tmpUI.Show()

			self.childrenDictUI["pvpMaxLvLText"] = tmpUI
			pvpMaxLvLText = self.childrenDictUI["pvpMaxLvLText"]

			tmpUI = ui.SlotBar()
			tmpUI.SetParent(self.subBoardUI)
			tmpUI.SetSize(192 / 4, 13 + 2)

			if localeinfo.IsARABIC():
				tmpUI.SetPosition(START_X_POSITION + pvpMinLvLText.GetTextSize()[0] + 15 + pvpMinLvLEditLineSlot.GetWidth() + 15, START_Y_POSITION)
			else:
				tmpUI.SetPosition(START_X_POSITION + pvpMinLvLText.GetTextSize()[0] + 15 + pvpMinLvLEditLineSlot.GetWidth() + 15 + pvpMaxLvLText.GetTextSize()[0] + 15, START_Y_POSITION)

			tmpUI.Show()

			self.childrenDictUI["pvpMaxLvLEditLineSlot"] = tmpUI
			pvpMaxLvLEditLineSlot = self.childrenDictUI["pvpMaxLvLEditLineSlot"]

			tmpUI = ui.EditLine()
			tmpUI.SetParent(pvpMaxLvLEditLineSlot)
			tmpUI.SetPosition(2, 1)
			tmpUI.SetSize(pvpMaxLvLEditLineSlot.GetWidth(), pvpMaxLvLEditLineSlot.GetHeight())
			tmpUI.SetEscapeEvent(ui.__mem_func__(self.OnPressEscapeKey))
			tmpUI.SetNumberMode()
			tmpUI.SetMax(3)
			tmpUI.Show()

			self.childrenDictUI["pvpMaxLvLEditLine"] = tmpUI
			pvpMaxLvLEditLine = self.childrenDictUI["pvpMaxLvLEditLine"]

			START_Y_POSITION += 30

			tmpUI = ui.TextLine()
			tmpUI.SetParent(self.subBoardUI)

			if localeinfo.IsARABIC():
				tmpUI.SetHorizontalAlignRight()
				tmpUI.SetPosition(START_X_POSITION + tmpUI.GetTextSize()[0] + 60, START_Y_POSITION)
			else:
				tmpUI.SetHorizontalAlignLeft()
				tmpUI.SetPosition(START_X_POSITION, START_Y_POSITION)

			tmpUI.SetText(localeinfo.PVP_TOURNAMENT_MAX_REGISTER)
			tmpUI.Show()

			self.childrenDictUI["pvpMaxRegisterText"] = tmpUI
			pvpMaxRegisterText = self.childrenDictUI["pvpMaxRegisterText"]

			tmpUI = ui.SlotBar()
			tmpUI.SetParent(self.subBoardUI)
			tmpUI.SetSize(192 / 4, 13 + 2)

			if localeinfo.IsARABIC():
				tmpUI.SetPosition(START_X_POSITION, START_Y_POSITION)
			else:
				tmpUI.SetPosition(START_X_POSITION + pvpMaxRegisterText.GetTextSize()[0] + 15, START_Y_POSITION)

			tmpUI.Show()

			self.childrenDictUI["pvpMaxRegisterEditLineSlot"] = tmpUI
			pvpMaxRegisterEditLineSlot = self.childrenDictUI["pvpMaxRegisterEditLineSlot"]

			tmpUI = ui.EditLine()
			tmpUI.SetParent(pvpMaxRegisterEditLineSlot)
			tmpUI.SetPosition(2, 1)
			tmpUI.SetSize(pvpMaxRegisterEditLineSlot.GetWidth(), pvpMaxRegisterEditLineSlot.GetHeight())
			tmpUI.SetEscapeEvent(ui.__mem_func__(self.OnPressEscapeKey))
			tmpUI.SetNumberMode()
			tmpUI.SetMax(3)
			tmpUI.Show()

			self.childrenDictUI["pvpMaxRegisterEditLine"] = tmpUI
			pvpMaxRegisterEditLine = self.childrenDictUI["pvpMaxRegisterEditLine"]

			tmpUI = ui.TextLine()
			tmpUI.SetParent(self.subBoardUI)

			if localeinfo.IsARABIC():
				tmpUI.SetHorizontalAlignRight()
				tmpUI.SetPosition(START_X_POSITION + pvpMaxRegisterText.GetTextSize()[0] + 35 + pvpMaxRegisterEditLine.GetWidth() + 35 + tmpUI.GetTextSize()[0] + 5, START_Y_POSITION)
			else:
				tmpUI.SetHorizontalAlignLeft()
				tmpUI.SetPosition(START_X_POSITION + pvpMaxRegisterText.GetTextSize()[0] + 15 + pvpMaxRegisterEditLine.GetWidth() + 15, START_Y_POSITION)

			tmpUI.SetText(localeinfo.PVP_TOURNAMENT_REGISTER_TIME)
			tmpUI.Show()

			self.childrenDictUI["pvpRegisterTimeText"] = tmpUI
			pvpRegisterTimeText = self.childrenDictUI["pvpRegisterTimeText"]

			tmpUI = ui.SlotBar()
			tmpUI.SetParent(self.subBoardUI)
			tmpUI.SetSize(192 / 4,13 + 2)

			if localeinfo.IsARABIC():
				tmpUI.SetPosition(START_X_POSITION + pvpMaxRegisterText.GetTextSize()[0] + 15 + pvpMaxRegisterEditLine.GetWidth() + 15, START_Y_POSITION)
			else:
				tmpUI.SetPosition(START_X_POSITION + pvpMaxRegisterText.GetTextSize()[0] + 15 + pvpMaxRegisterEditLine.GetWidth() + 15 + pvpRegisterTimeText.GetTextSize()[0] + 5, START_Y_POSITION)

			tmpUI.Show()

			self.childrenDictUI["pvpRegisterTimeEditLineSlot"] = tmpUI
			pvpRegisterTimeEditLineSlot = self.childrenDictUI["pvpRegisterTimeEditLineSlot"]

			tmpUI = ui.EditLine()
			tmpUI.SetParent(pvpRegisterTimeEditLineSlot)
			tmpUI.SetPosition(2, 1)
			tmpUI.SetSize(pvpRegisterTimeEditLineSlot.GetWidth(), pvpRegisterTimeEditLineSlot.GetHeight())
			tmpUI.SetEscapeEvent(ui.__mem_func__(self.OnPressEscapeKey))
			tmpUI.SetNumberMode()
			tmpUI.SetMax(3)
			tmpUI.Show()

			self.childrenDictUI["pvpRegisterTimeEditLine"] = tmpUI
			pvpRegisterTimeEditLine = self.childrenDictUI["pvpRegisterTimeEditLine"]

			START_Y_POSITION += 30

			tmpUI = ui.TextLine()
			tmpUI.SetParent(self.subBoardUI)

			if localeinfo.IsARABIC():
				tmpUI.SetHorizontalAlignRight()
			else:
				tmpUI.SetHorizontalAlignLeft()

			tmpUI.SetPosition(START_X_POSITION, START_Y_POSITION)
			tmpUI.SetText(localeinfo.PVP_TOURNAMENT_PVP_BET)
			tmpUI.Show()

			self.childrenDictUI["pvpBetText"] = tmpUI
			pvpBetText = self.childrenDictUI["pvpBetText"]

			tmpUI = ui.SlotBar()
			tmpUI.SetParent(self.subBoardUI)
			tmpUI.SetSize(192, 13 + 2)
			tmpUI.SetPosition(START_X_POSITION+pvpBetText.GetTextSize()[0] + 15, START_Y_POSITION)
			tmpUI.Show()

			self.childrenDictUI["pvpBetEditLineSlot"] = tmpUI
			pvpBetEditLineSlot = self.childrenDictUI["pvpBetEditLineSlot"]

			tmpUI = ui.EditLine()
			tmpUI.SetParent(pvpBetEditLineSlot)
			tmpUI.SetPosition(2, 1)
			tmpUI.SetSize(pvpBetEditLineSlot.GetWidth(), pvpBetEditLineSlot.GetHeight())
			tmpUI.SetEscapeEvent(ui.__mem_func__(self.OnPressEscapeKey))
			tmpUI.SetNumberMode()
			tmpUI.SetMax(20)
			tmpUI.Show()

			self.childrenDictUI["pvpBetEditLine"] = tmpUI
			pvpBetEditLine = self.childrenDictUI["pvpBetEditLine"]

			START_Y_POSITION += 30

			tmpUI = ui.Button()
			tmpUI.LeftRightReverse()
			tmpUI.SetParent(self.subBoardUI)
			tmpUI.SetPosition(self.subBoardUI.GetWidth() - 200, START_Y_POSITION)
			tmpUI.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			tmpUI.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
			tmpUI.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
			tmpUI.SAFE_SetEvent(self.__ClickAccepButton)
			tmpUI.Show()

			self.childrenDictUI["acceptButton"] = tmpUI

			tmpUI = ui.Button()
			tmpUI.LeftRightReverse()
			tmpUI.SetParent(self.subBoardUI)
			tmpUI.SetPosition(self.subBoardUI.GetWidth() - 100, START_Y_POSITION)
			tmpUI.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			tmpUI.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
			tmpUI.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
			tmpUI.SetText(localeinfo.GUILD_BANKINFO_CLOSE)
			tmpUI.SAFE_SetEvent(self.Hide)
			tmpUI.Show()

			self.childrenDictUI["closeButton"] = tmpUI

			START_Y_POSITION = 20
			START_X_POSITION = 15

			tmpUI = ui.ComboBoxImage(self.subBoardUI,\
												"d:/ymir work/ui/pattern/select_image.tga",\
												START_X_POSITION + pvpTypeText.GetTextSize()[0]+10,\
												START_Y_POSITION)

			for k, v in self.pvpTypesDict.items():
				tmpUI.InsertItem2(k, v)

			tmpUI.SetEvent(lambda x : self.__SetPvPType(x))
			tmpUI.Show()

			self.childrenDictUI["pvpTypeComboBox"] = tmpUI
		except Exception as e:
			import dbg
			dbg.TraceError(str(e))
			app.Abort()

	def RefreshPhase(self):
		bPhase = pvp_tournament.GetPhase()
		if bPhase >= pvp_tournament.PVP_TOURNAMENT_PHASE_MAX_NUM:
			import dbg
			dbg.TraceError("Unknown pvp tournament phase: %d" % (bPhase))

			app.Abort()
			return

		if bPhase == pvp_tournament.PVP_TOURNAMENT_PHASE_END:
			if self.childrenDictUI.has_key("acceptButton"):
				self.childrenDictUI["acceptButton"].SetText(localeinfo.BATTLE_ROYALE_MAINBUTTON_STARTABLE)
		else:
			if self.childrenDictUI.has_key("acceptButton"):
				self.childrenDictUI["acceptButton"].SetText(localeinfo.PVP_TOURNAMENT_END)

		if self.childrenDictUI.has_key("pvpMinLvLEditLine"):
			self.childrenDictUI["pvpMinLvLEditLine"].SetText(str(pvp_tournament.GetMinimumLevel()))
			
			if bPhase == pvp_tournament.PVP_TOURNAMENT_PHASE_END:
				self.childrenDictUI["pvpMinLvLEditLine"].CanEdit(True)
			else:
				self.childrenDictUI["pvpMinLvLEditLine"].CanEdit(False)
				self.childrenDictUI["pvpMinLvLEditLine"].KillFocus()

		if self.childrenDictUI.has_key("pvpMaxLvLEditLine"):
			self.childrenDictUI["pvpMaxLvLEditLine"].SetText(str(pvp_tournament.GetMaximumLevel()))
			
			if bPhase == pvp_tournament.PVP_TOURNAMENT_PHASE_END:
				self.childrenDictUI["pvpMaxLvLEditLine"].CanEdit(True)
			else:
				self.childrenDictUI["pvpMaxLvLEditLine"].CanEdit(False)
				self.childrenDictUI["pvpMaxLvLEditLine"].KillFocus()

		if self.childrenDictUI.has_key("pvpMaxRegisterEditLine"):
			self.childrenDictUI["pvpMaxRegisterEditLine"].SetText(str(pvp_tournament.GetRegisterCount()))
			
			if bPhase == pvp_tournament.PVP_TOURNAMENT_PHASE_END:
				self.childrenDictUI["pvpMaxRegisterEditLine"].CanEdit(True)
			else:
				self.childrenDictUI["pvpMaxRegisterEditLine"].CanEdit(False)
				self.childrenDictUI["pvpMaxRegisterEditLine"].KillFocus()

		if self.childrenDictUI.has_key("pvpRegisterTimeEditLine"):
			self.childrenDictUI["pvpRegisterTimeEditLine"].SetText(str(pvp_tournament.GetRegisterTime()))
			
			if bPhase == pvp_tournament.PVP_TOURNAMENT_PHASE_END:
				self.childrenDictUI["pvpRegisterTimeEditLine"].CanEdit(True)
			else:
				self.childrenDictUI["pvpRegisterTimeEditLine"].CanEdit(False)
				self.childrenDictUI["pvpRegisterTimeEditLine"].KillFocus()

		if self.childrenDictUI.has_key("pvpBetEditLine"):
			self.childrenDictUI["pvpBetEditLine"].SetText(str(pvp_tournament.GetBetPrice()))
			
			if bPhase == pvp_tournament.PVP_TOURNAMENT_PHASE_END:
				self.childrenDictUI["pvpBetEditLine"].CanEdit(True)
			else:
				self.childrenDictUI["pvpBetEditLine"].CanEdit(False)
				self.childrenDictUI["pvpBetEditLine"].KillFocus()

		if self.childrenDictUI.has_key("pvpTypeComboBox"):
			if bPhase == pvp_tournament.PVP_TOURNAMENT_PHASE_END:
				self.childrenDictUI["pvpTypeComboBox"].Enable()
			else:
				self.childrenDictUI["pvpTypeComboBox"].Disable()

		self.__SetPvPType(pvp_tournament.GetType(), 1)

	def Show(self):
		self.RefreshPhase()

		import background
		if background.GetCurrentMapName() != "metin2_map_pvp_duel":
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CANNOT_OPEN_PVP_TOURNAMENT_IN_HERE)
			return

		ui.ScriptWindow.Show(self)

	def Hide(self):
		if self.childrenDictUI.has_key("pvpTypeComboBox"):
			self.childrenDictUI["pvpTypeComboBox"].CloseListBox()

		ui.ScriptWindow.Hide(self)

	def OnPressEscapeKey(self):
		self.Hide()
		return True

	def __SetPvPType(self, pType, bLoad = 0):
		pvpTypesDict = {
			0: localeinfo.PVP_TOURNAMENT_ALL_CHARACTER,
			1: localeinfo.PVP_TOURNAMENT_ONLY_WARRIOR,
			2: localeinfo.PVP_TOURNAMENT_ONLY_ASSASSIN,
			3: localeinfo.PVP_TOURNAMENT_ONLY_SURA,
			4: localeinfo.PVP_TOURNAMENT_ONLY_SHAMAN,
		}

		if bLoad != 0:
			self.childrenDictUI["pvpTypeComboBox"].SelectItem(pType)
		else:
			self.childrenDictUI["pvpType"] = pType
			self.childrenDictUI["pvpTypeComboBox"].SetCurrentItem(pvpTypesDict[pType])
			self.childrenDictUI["pvpTypeComboBox"].CloseListBox()

	def __ClickAccepButton(self):
		bPhase = pvp_tournament.GetPhase()
		if bPhase >= pvp_tournament.PVP_TOURNAMENT_PHASE_MAX_NUM:
			import dbg
			dbg.TraceError("Unknown pvp tournament phase: %d" % (bPhase))

			app.Abort()
			return

		if bPhase == pvp_tournament.PVP_TOURNAMENT_PHASE_END:
			pvpType = self.childrenDictUI["pvpType"]
			if pvpType < 0 or pvpType > 4:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PVP_TOURNAMENT_PROBLEM_PVP_TYPE)
				return

			minLevel = self.childrenDictUI["pvpMinLvLEditLine"].GetText()
			if not minLevel.isdigit():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PVP_TOURNAMENT_PROBLEM_MIN_LEVEL)
				return

			maxLevel = self.childrenDictUI["pvpMaxLvLEditLine"].GetText()
			if not maxLevel.isdigit():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PVP_TOURNAMENT_PROBLEM_MAX_LEVEL)
				return

			registerCount = self.childrenDictUI["pvpMaxRegisterEditLine"].GetText()
			if not registerCount.isdigit():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PVP_TOURNAMENT_PROBLEM_REGISTER_COUNT)
				return

			registerTime = self.childrenDictUI["pvpRegisterTimeEditLine"].GetText()
			if not registerTime.isdigit():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PVP_TOURNAMENT_PROBLEM_REGISTER_TIME)
				return

			betPrice = self.childrenDictUI["pvpBetEditLine"].GetText()
			if not betPrice.isdigit():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PVP_TOURNAMENT_PROBLEM_BET_PRICE)
				return

			import net
			net.SendChatPacket("/pvp_tournament start %d %s %s %s %s %s" % (pvpType, minLevel, maxLevel, registerCount, registerTime, betPrice))
		else:
			import net
			net.SendChatPacket("/pvp_tournament stop")

if app.PVP_HAVE_GUI:
	class FightsPanel(ui.ScriptWindow):
		class FightWindow(ui.Box):
			BAR1_COLOR = grp.GenerateColor(73.0 / 255.0, 73.0 / 255.0, 73.0 / 255.0, 0.3)

			WIN_BG_COLOR = grp.GenerateColor(0.0 / 255.0, 255.0 / 255.0, 0.0 / 255.0, 0.2)
			LOSE_BG_COLOR = grp.GenerateColor(255.0 / 255.0, 0.0 / 255.0, 0.0 / 255.0, 0.2)
			#DRAW_BG_COLOR = grp.GenerateColor(255.0 / 255.0, 240.0 / 255.0, 0.0 / 255.0, 0.2)
			DRAW_BG_COLOR = LOSE_BG_COLOR

			PLAYER1_KEY = 1
			PLAYER2_KEY = 2

			def __init__(self, width, height, parent, arena, pid1, name1, race1, hp1, maxhp1, pid2, name2, race2, hp2, maxhp2):
				ui.Box.__init__(self)

				self.SetParent(parent)
				self.SetSize(width, height)

				self.end = False

				self.pid1 = int(pid1)
				self.pid2 = int(pid2)

				self.hp1 = int(hp1)
				self.maxhp1 = int(maxhp1)

				self.hp2 = int(hp2)
				self.maxhp2 = int(maxhp2)

				self.scoreText1 = None
				self.scoreText2 = None

				self.gaugeHPDict = {}

				self.width = width

				self.name1 = name1
				self.name2 = name2

				self.vsUI = None
				self.vs_width = 0
				self.vs_x = 0

				from _weakref import proxy
				self.parent = proxy(parent)

				self.SetColor(0xFF000000)

				self.childrenDict = {}

				self.SetPlayer(self.PLAYER1_KEY, name1, race1)
				self.SetPlayer(self.PLAYER2_KEY, name2, race2)

			def __del__(self):
				self.end = True

				self.width = 0
				self.vs_width = 0
				self.vs_x = 0

				if self.vsUI:
					del self.vsUI
					self.vsUI = None

				if self.scoreText1:
					del self.scoreText1
					self.scoreText1 = None

				if self.scoreText2:
					del self.scoreText2
					self.scoreText2 = None

				for k, v in self.gaugeHPDict.items():
					del v

				self.gaugeHPDict = {}

				for k, v in self.childrenDict.items():
					for e in v:
						del e

				self.childrenDict = {}

				self.hp1 = 0
				self.maxhp1 = 0

				self.hp2 = 0
				self.maxhp2 = 0

				self.parent = None

				ui.Box.__del__(self)

			def SetPlayer(self, key, name, race):
				race = int(race)
				dictLen = len(self.childrenDict)

				if self.childrenDict.has_key(key):
					if len(self.childrenDict[key]) != 0:
						for e in self.childrenDict[key]:
							del e

				self.childrenDict[key] = []

				tmpBG = ui.ExpandedImageBox()
				tmpBG.SetParent(self)
				tmpBG.AddFlag("not_pick")
				tmpBG.SetAlpha(0.2)

				if key == self.PLAYER2_KEY:
					tmpBG.SetPosition(self.vs_x + self.vs_width + 5, 7)
				else:
					tmpBG.SetPosition(8, 7)

				pathImg = "d:/ymir work/ui/game/pvp_tournament/bg_char%d.sub" % key

				try:
					tmpBG.LoadImage(pathImg)
					tmpBG.Show()
				except:
					import dbg
					dbg.TraceError("%s cannot be loaded." % (pathImg))
					app.Abort()

				tmpUI = ui.ExpandedImageBox()
				tmpUI.SetParent(tmpBG)
				tmpUI.AddFlag("not_pick")
				if key == self.PLAYER2_KEY:
					tmpUI.SetPosition(96, -3)
				else:
					tmpUI.SetPosition(3, -3)

				if FACE_IMAGE_DICT.has_key(race):
					pathImg = "d:/ymir work/ui/game/pvp_tournament/face/" + FACE_IMAGE_DICT[race]
				else:
					pathImg = "d:/ymir work/ui/game/pvp_tournament/face/empty.sub"

				try:
					tmpUI.LoadImage(pathImg)
					tmpUI.Show()
				except:
					import dbg
					dbg.TraceError("%s cannot be loaded." % (pathImg))
					app.Abort()

				if dictLen == 0:
					tmpVS = ui.ExpandedImageBox()
					tmpVS.SetParent(self)
					tmpVS.AddFlag("not_pick")

					x = 4 + tmpBG.GetWidth() + 5
					tmpVS.SetPosition(x + 3, 9)

					pathImg = "d:/ymir work/ui/game/pvp_tournament/vs.sub"

					try:
						tmpVS.LoadImage(pathImg)
						tmpVS.Show()
					except:
						import dbg
						dbg.TraceError("%s cannot be loaded." % (pathImg))
						app.Abort()

					self.vs_width = tmpVS.GetWidth()
					self.vs_x = x
					self.vsUI = tmpVS

				tmpText1BG = ui.Bar()
				tmpText1BG.SetParent(tmpBG)
				tmpText1BG.AddFlag("not_pick")
				tmpText1BG.SetSize(89, 14)
				tmpText1BG.SetColor(self.BAR1_COLOR)

				if key == self.PLAYER2_KEY:
					tmpText1BG.SetPosition(4, 5)
				else:
					tmpText1BG.SetPosition(50, 5)

				tmpText1BG.Show()

				tmpText = ui.TextLine()
				tmpText.SetParent(tmpText1BG)
				tmpText.AddFlag("not_pick")
				tmpText.SetPosition(0, -2)
				tmpText.SetFontName("Tahoma:12")
				tmpText.SetHorizontalAlignCenter()
				tmpText.SetVerticalAlignCenter()
				tmpText.SetWindowHorizontalAlignCenter()
				tmpText.SetWindowVerticalAlignCenter()
				tmpText.SetText(name)
				tmpText.Show()

				tmpGaugeBG = ui.Bar()
				tmpGaugeBG.SetParent(tmpBG)
				tmpGaugeBG.AddFlag("not_pick")
				tmpGaugeBG.SetSize(64, 12)
				tmpGaugeBG.SetColor(0x00000000)

				if key == self.PLAYER2_KEY:
					tmpGaugeBG.SetPosition(29, 20)
				else:
					tmpGaugeBG.SetPosition(50, 20)

				tmpGaugeBG.Show()

				tmpGaugeHP = ui.Gauge()
				tmpGaugeHP.SetParent(tmpGaugeBG)
				tmpGaugeHP.MakeGauge(64, "red")

				if key == self.PLAYER2_KEY:
					tmpGaugeHP.SetPosition(0, 3)
				else:
					tmpGaugeHP.SetPosition(0, 3)

				if key == self.PLAYER2_KEY:
					if self.hp2 == -1:
						tmpGaugeHP.Hide()
					else:
						tmpGaugeHP.Show()

					self.gaugeHPDict[self.PLAYER2_KEY] = tmpGaugeHP
				else:
					if self.hp1 == -1:
						tmpGaugeHP.Hide()
					else:
						tmpGaugeHP.Show()

					self.gaugeHPDict[self.PLAYER1_KEY] = tmpGaugeHP

				tmpScoreBG = ui.Bar()
				tmpScoreBG.SetParent(tmpBG)
				tmpScoreBG.AddFlag("not_pick")
				tmpScoreBG.SetSize(22, 12)
				tmpScoreBG.SetColor(0x00000000)

				if key == self.PLAYER2_KEY:
					tmpScoreBG.SetPosition(4, 20)
				else:
					tmpScoreBG.SetPosition(50 + tmpGaugeBG.GetWidth() + 3, 20)

				tmpScoreBG.Show()

				tmpScoreText = ui.TextLine()
				tmpScoreText.SetParent(tmpScoreBG)
				tmpScoreText.AddFlag("not_pick")
				tmpScoreText.SetPosition(0, -1)
				tmpScoreText.SetFontName("Tahoma:12")
				tmpScoreText.SetHorizontalAlignCenter()
				tmpScoreText.SetVerticalAlignCenter()
				tmpScoreText.SetWindowHorizontalAlignCenter()
				tmpScoreText.SetWindowVerticalAlignCenter()
				tmpScoreText.SetText("0")
				tmpScoreText.Show()

				if key == self.PLAYER2_KEY:
					self.scoreText2 = tmpScoreText
				else:
					self.scoreText1 = tmpScoreText

				self.childrenDict[key].append(tmpBG)
				self.childrenDict[key].append(tmpUI)
				self.childrenDict[key].append(tmpText1BG)
				self.childrenDict[key].append(tmpText)
				self.childrenDict[key].append(tmpGaugeBG)
				self.childrenDict[key].append(tmpScoreBG)

				self.OnRefreshHP()

			def OnRefreshHP(self):
				if self.end == True:
					return

				try:
					if self.gaugeHPDict.has_key(self.PLAYER1_KEY):
						hpPercentage = float(self.hp1) / float(self.maxhp1)
						self.gaugeHPDict[self.PLAYER1_KEY].SetPercentage(float(hpPercentage) * 100.0, 100)

					if self.gaugeHPDict.has_key(self.PLAYER2_KEY):
						hpPercentage = float(self.hp2) / float(self.maxhp2)
						self.gaugeHPDict[self.PLAYER2_KEY].SetPercentage(float(hpPercentage) * 100.0, 100)
				except:
					pass

			def Disconnect(self, pid):
				if self.end == True:
					return

				pid = int(pid)
				if pid == self.pid1:
					self.gaugeHPDict[self.PLAYER1_KEY].Hide()
				elif pid == self.pid2:
					self.gaugeHPDict[self.PLAYER2_KEY].Hide()

			def Enter(self, pid):
				if self.end == True:
					return

				pid = int(pid)
				if pid == self.pid1:
					self.gaugeHPDict[self.PLAYER1_KEY].Show()
				elif pid == self.pid2:
					self.gaugeHPDict[self.PLAYER2_KEY].Show()

			def UpdateHP(self, pid, hp, maxhp):
				if self.end == True:
					return

				pid = int(pid)
				hp = int(hp)
				maxhp = int(maxhp)

				if pid == self.pid1:
					if hp == self.hp1 and\
						maxhp == self.maxhp1:
						return

					self.hp1 = hp
					self.maxhp1 = maxhp

					if self.hp1 == -1:
						self.gaugeHPDict[self.PLAYER1_KEY].Hide()
					else:
						self.gaugeHPDict[self.PLAYER1_KEY].Show()
				elif pid == self.pid2:
					if hp == self.hp2 and\
						maxhp == self.maxhp2:
						return

					self.hp2 = hp
					self.maxhp2 = maxhp

					if self.hp2 == -1:
						self.gaugeHPDict[self.PLAYER2_KEY].Hide()
					else:
						self.gaugeHPDict[self.PLAYER2_KEY].Show()

				self.OnRefreshHP()

			def UpdateScore(self, pid, score):
				if self.end == True:
					return

				pid = int(pid)

				if pid == self.pid1:
					if not self.scoreText1:
						return

					myscore = self.scoreText1.GetText()
					if myscore == score:
						return

					self.scoreText1.SetText(score)
				elif pid == self.pid2:
					if not self.scoreText2:
						return

					myscore = self.scoreText1.GetText()
					if myscore == score:
						return

					self.scoreText2.SetText(score)

			def Update(self, pid, draw):
				self.end = True

				pathImg = "d:/ymir work/ui/game/pvp_tournament/lose.sub"

				self.gaugeHPDict[self.PLAYER1_KEY].Hide()
				self.gaugeHPDict[self.PLAYER2_KEY].Hide()

				for key in range(self.PLAYER1_KEY, self.PLAYER2_KEY + 1):
					if self.childrenDict.has_key(key):
						if len(self.childrenDict[key]) < 2:
							continue

						tmpLose = ui.Bar()
						tmpLose.SetParent(self.childrenDict[key][0])
						tmpLose.AddFlag("not_pick")
						tmpLose.SetSize(self.childrenDict[key][0].GetWidth(), self.childrenDict[key][0].GetHeight())

						if draw == 1:
							tmpLose.SetColor(self.DRAW_BG_COLOR)
						else:
							if key == self.PLAYER1_KEY:
								if int(pid) == self.pid1:
									tmpLose.SetColor(self.WIN_BG_COLOR)
								else:
									tmpLose.SetColor(self.LOSE_BG_COLOR)
							else:
								if int(pid) == self.pid2:
									tmpLose.SetColor(self.WIN_BG_COLOR)
								else:
									tmpLose.SetColor(self.LOSE_BG_COLOR)

						tmpLose.SetPosition(0, 0)
						tmpLose.Show()

						self.childrenDict[key].append(tmpLose)

		def __init__(self):
			ui.ScriptWindow.__init__(self)

			self.isLoaded = 0
			self.boardUI = None
			self.maxWidth = 0
			self.screenHeight = wndMgr.GetScreenHeight()

			self.arenaDict = {}

			self.pidToArenaDict = {}
			self.fightWindowHeight = 50

			self.LoadWindow()

		def __del__(self):
			ui.ScriptWindow.__del__(self)

		def Destroy(self):
			import constinfo
			constinfo.arena = 1

			for k, v in self.arenaDict.items():
				del v

			self.arenaDict = {}

			self.pidToArenaDict = {}

			self.boardUI = None
			self.maxWidth = 0
			self.screenHeight = 0

			self.ClearDictionary()

		def LoadWindow(self):
			if self.isLoaded != 0:
				return

			self.isLoaded = 1

			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "uiscript/pvptournament_fights_window.py")

				self.boardUI = self.GetChild("BoardUI")
				self.maxWidth = self.boardUI.GetWidth()

				self.SetSize(0, 0)
			except Exception as e:
				import dbg
				dbg.TraceError(str(e))
				app.Abort()

		def Show(self):
			import background
			if background.GetCurrentMapName() != "metin2_map_pvp_duel":
				if self.IsShow():
					self.Hide()

				return

			ui.ScriptWindow.Show(self)

		def Hide(self):
			ui.ScriptWindow.Hide(self)

		def CreateFight(self, arena, pid1, name1, race1, hp1, maxhp1, pid2, name2, race2, hp2, maxhp2):
			self.arenaDict[arena] = self.FightWindow(self.maxWidth\
													, self.fightWindowHeight\
													, self\
													, arena\
													, pid1\
													, name1\
													, race1\
													, hp1\
													, maxhp1
													, pid2\
													, name2\
													, race2\
													, hp2\
													, maxhp2)
			
			return True

		def AddFight(self, arena, pid1, name1, race1, hp1, maxhp1, pid2, name2, race2, hp2, maxhp2, score1 = -1, score2 = -2):
			if arena < 0:
				return

			if not self.IsShow():
				self.Show()

			if self.arenaDict.has_key(arena):
				del self.arenaDict[arena]

			if self.CreateFight(arena, pid1, name1, race1, hp1, maxhp1, pid2, name2, race2, hp2, maxhp2) == True:
				self.RefreshPosition()

			self.pidToArenaDict[pid1] = arena
			self.pidToArenaDict[pid2] = arena

			if score1 != -1:
				if self.arenaDict.has_key(arena):
					self.arenaDict[arena].UpdateScore(pid1, score1)
					self.arenaDict[arena].UpdateScore(pid2, score2)

		def CacheFight(self, arena, pid1, name1, race1, pid2, name2, race2, score1, score2, winner_pid):
			if arena < 0:
				return

			if not self.IsShow():
				self.Show()

			if self.arenaDict.has_key(arena):
				del self.arenaDict[arena]

			if self.CreateFight(arena, pid1, name1, race1, 100, 100, pid2, name2, race2, 100, 100) == True:
				self.RefreshPosition()

			self.pidToArenaDict[pid1] = arena
			self.pidToArenaDict[pid2] = arena

			if winner_pid != 0:
				self.Update(winner_pid, 0)
			else:
				self.Update(pid1, 1)

		def RefreshPosition(self):
			h = 16
			for k, v in sorted(self.arenaDict.items()):
				v.SetPosition(0, 8 + ((int(k) - 1) * self.fightWindowHeight) + (int(k) * 4))
				h += self.fightWindowHeight + 4

			for k, v in sorted(self.arenaDict.items()):
				if not v.IsShow():
					v.Show()

			self.SetPosition(6, (self.screenHeight - h) / 2)

		def FoundArenaByPID(self, pid):
			if self.pidToArenaDict.has_key(pid):
				return self.pidToArenaDict[pid]

			return -1

		def Disconnect(self, pid):
			arena = self.FoundArenaByPID(pid)
			if self.arenaDict.has_key(arena):
				self.arenaDict[arena].Disconnect(pid)

		def Enter(self, pid):
			arena = self.FoundArenaByPID(pid)
			if self.arenaDict.has_key(arena):
				self.arenaDict[arena].Enter(pid)

		def UpdateHP(self, pid, hp, maxhp):
			arena = self.FoundArenaByPID(pid)
			if self.arenaDict.has_key(arena):
				self.arenaDict[arena].UpdateHP(pid, hp, maxhp)

		def UpdateScore(self, pid, score):
			arena = self.FoundArenaByPID(pid)
			if self.arenaDict.has_key(arena):
				self.arenaDict[arena].UpdateScore(pid, score)

		def Update(self, pid, draw):
			arena = self.FoundArenaByPID(pid)

			if self.arenaDict.has_key(arena):
				pid1 = str(self.arenaDict[arena].pid1)
				pid2 = str(self.arenaDict[arena].pid2)

				self.arenaDict[arena].Update(pid, draw)

			if len(self.arenaDict) != 0:
				self.RefreshPosition()
