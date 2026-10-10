# coding: latin_1

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import chr
import net

import grp
import snd
import wndMgr
import event
import systemSetting
import localeinfo

import ui
import networkmodule
import math
import snd
import musicinfo
import playersettingmodule
import uiscriptlocale
import uitooltip

LOCALE_PATH = "uiscript/"+uiscriptlocale.CODEPAGE+"_"
IMG_PATCH = "d:/ymir work/ui/new_panels/"

MAN			= 0
WOMAN		= 1
SHAPE0		= 0
SHAPE1		= 1
PAGE_COUNT	= 2
SLOT_COUNT	= 4
BASE_CHR_ID	= 3

class CreateCharacterWindow(ui.Window):

	SLOT_ROTATION = [135.0, 225.0, 315.0, 45.0]
	

	CREATE_STAT_POINT = 0

	START_STAT =	(  ## CON INT STR DEX
						[ 4, 3, 6, 3, ], ## Warrior
						[ 3, 3, 4, 6, ], ## Assassin
						[ 3, 5, 5, 3, ], ## Sura
						[ 4, 6, 3, 3, ], ## Shaman
						[ 4, 3, 6, 3, ], ## Warrior
						[ 3, 3, 4, 6, ], ## Assassin
						[ 3, 5, 5, 3, ], ## Sura
						[ 4, 6, 3, 3, ], ## Shaman
					)

	class CharacterRenderer(ui.Window):
		def OnRender(self):
			grp.ClearDepthBuffer()
			grp.SetGameRenderState()
			grp.PushState()
			grp.SetOmniLight()

			screenWidth = wndMgr.GetScreenWidth()
			screenHeight = wndMgr.GetScreenHeight()
			newScreenWidth = float(screenWidth+30)
			newScreenHeight = float(screenHeight+30)

			grp.SetViewport(270.0/screenWidth, 0.0, newScreenWidth/screenWidth, newScreenHeight/screenHeight)
			app.SetCenterPosition(0.0, 0.0, 20.0)
			app.SetCamera(1550.0, 15.0, 180.0, 95.0)
			grp.SetPerspective(11.0, newScreenWidth/newScreenHeight, 1000.0, 3000.0)


			(x, y) = app.GetCursorPosition()
			grp.SetCursorPosition(x, y)

			chr.Deform()
			chr.Render()

			grp.RestoreViewport()
			grp.PopState()
			grp.SetInterfaceRenderState()

	def __init__(self, stream):
		print "NEW CREATE WINDOW ----------------------------------------------------------------------------"
		ui.Window.__init__(self)
		net.SetPhaseWindow(net.PHASE_WINDOW_CREATE, self)

		self.stream=stream

	def __del__(self):
		print "---------------------------------------------------------------------------- DELETE CREATE WINDOW"

		net.SetPhaseWindow(net.PHASE_WINDOW_CREATE, 0)
		ui.Window.__del__(self)

	def Open(self):
		print "OPEN CREATE WINDOW ----------------------------------------------------------------------------"


		self.reservingRaceIndex = -1
		self.reservingShapeIndex = -1
		self.reservingStartTime = 0
		self.stat = [0, 0, 0, 0]
	
		self.gender = 0
		self.slot = -1
		self.shape = 0
		self.shapeList = [
			[0, 0, 0, 0],
			[0, 0, 0, 0]
		]

		self.characterListImageBoard = {}
		self.characterListWindowName = {}
		self.characterListWindowNameText = {}
		self.characterListButtonSelect = {}
		self.characterListButtonGenderMan = {}
		self.characterListButtonGenderWoman = {}
		self.characterListButtonShapeFirst = {}
		self.characterListButtonShapeSecond = {}

		try:
			dlgBoard = ui.ScriptWindow()
			pythonScriptLoader = ui.PythonScriptLoader()
			pythonScriptLoader.LoadScriptFile(dlgBoard, "uiscript/create_character_window.py")

		except:
			import exception
			exception.Abort("CreateCharacterWindow.Open.LoadObject")

		try:
			getChild = dlgBoard.GetChild

			self.btnCreate = getChild("create_button")
			self.btnCancel = getChild("cancel_button")
			self.btnExit = getChild("exit_button")

			self.editCharacterName = getChild("character_name_value")

			self.backGround = getChild("BackGround")

		except:
			import exception
			exception.Abort("CreateCharacterWindow.Open.BindObject")

		self.btnCreate.SetEvent(ui.__mem_func__(self.CreateCharacter))
		self.btnCancel.SetEvent(ui.__mem_func__(self.CancelCreate))
		self.btnExit.SetEvent(ui.__mem_func__(self.ExitCreate))

		self.editCharacterName.SetReturnEvent(ui.__mem_func__(self.CreateCharacter))
		self.editCharacterName.SetEscapeEvent(ui.__mem_func__(self.ExitCreate))

		self.dlgBoard = dlgBoard

		self.characters = {
			0 : [playersettingmodule.RACE_WARRIOR_M, playersettingmodule.RACE_ASSASSIN_M, playersettingmodule.RACE_SURA_M, playersettingmodule.RACE_SHAMAN_M],
			1 : [playersettingmodule.RACE_WARRIOR_W, playersettingmodule.RACE_ASSASSIN_W, playersettingmodule.RACE_SURA_W, playersettingmodule.RACE_SHAMAN_W],
		}

		self.character_names = {
			0: "Sura",
			1: "Ninja",
			2: "Warrior",
			3: "Shaman",
		}

		self.curNameAlpha	= [0.0, 0.0, 0.0, 0.0, 0.0]
		self.destNameAlpha	= [0.0, 0.0, 0.0, 0.0, 0.0]
		self.curGauge		= [0.0, 0.0, 0.0, 0.0]
		self.destGauge		= [0.0, 0.0, 0.0, 0.0]

		self.chrRenderer = self.CharacterRenderer()
		self.chrRenderer.SetParent(self.backGround)
		self.chrRenderer.Show()

		self.toolTip = uitooltip.ToolTip()
		self.toolTip.ClearToolTip()

		self.editCharacterName.SetText("")

		self.EnableWindow()

		app.SetCamera(500.0, 10.0, 180.0, 95.0)

		self.dlgBoard.Show()
		self.Show()

		if musicinfo.createMusic != "":
			snd.SetMusicVolume(systemSetting.GetMusicVolume())
			snd.FadeInMusic("BGM/"+musicinfo.createMusic)

		for i in range(4):
			self.characterListImageBoard[i] = ui.ImageBox()
			self.characterListImageBoard[i].SetParent(self.backGround)
			self.characterListImageBoard[i].SetPosition(0, 0)
			self.characterListImageBoard[i].LoadImage(IMG_PATCH + "create_character/character_slot.tga")
			self.characterListImageBoard[i].Show()

			if i < 2:
				self.characterListImageBoard[i].SetPosition(15, wndMgr.GetScreenHeight() / 2 - 245 + i * 126)
				if app.ENABLE_WINDOW_RESIZE:
					self.characterListImageBoard[i].SetResizeDic({"position" : (15, Expr("SCREEN_HEIGHT") / 2 - 245 + i * 126)})
			else:
				self.characterListImageBoard[i].SetPosition(wndMgr.GetScreenWidth() - 306, wndMgr.GetScreenHeight() / 2 - 245 + (i - 2) * 126)
				if app.ENABLE_WINDOW_RESIZE:
					self.characterListImageBoard[i].SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - 306, Expr("SCREEN_HEIGHT") / 2 - 245 + (i - 2) * 126)})

			self.characterListWindowName[i] = ui.Window()
			self.characterListWindowName[i].SetParent(self.characterListImageBoard[i])
			self.characterListWindowName[i].SetPosition(17, 25)
			self.characterListWindowName[i].SetSize(177, 22)
			self.characterListWindowName[i].Show()

			self.characterListWindowNameText[i] = ui.TextLine()
			self.characterListWindowNameText[i].SetParent(self.characterListWindowName[i])
			self.characterListWindowNameText[i].SetWindowHorizontalAlignCenter()
			self.characterListWindowNameText[i].SetHorizontalAlignCenter()
			self.characterListWindowNameText[i].SetPosition(0, 4)
			self.characterListWindowNameText[i].SetPackedFontColor(0xffc3af9a)
			self.characterListWindowNameText[i].SetText(self.character_names[i])
			self.characterListWindowNameText[i].Show()

			self.characterListButtonSelect[i] = ui.Button()
			self.characterListButtonSelect[i].SetParent(self.characterListImageBoard[i])
			self.characterListButtonSelect[i].SetPosition(209, 8)
			self.characterListButtonSelect[i].SetEvent(ui.__mem_func__(self.__SelectNewSlotIndex), i)

			self.characterListButtonGenderMan[i] = ui.Button()
			self.characterListButtonGenderMan[i].SetParent(self.characterListImageBoard[i])
			self.characterListButtonGenderMan[i].SetPosition(45, 54)
			self.characterListButtonGenderMan[i].SetUpVisual(IMG_PATCH + "create_character/buttons/gender_man_default.tga")
			self.characterListButtonGenderMan[i].SetOverVisual(IMG_PATCH + "create_character/buttons/gender_man_default.tga")
			self.characterListButtonGenderMan[i].SetDownVisual(IMG_PATCH + "create_character/buttons/gender_man_default.tga")
			self.characterListButtonGenderMan[i].SetDisableVisual(IMG_PATCH + "create_character/buttons/gender_man_disable.tga")
			self.characterListButtonGenderMan[i].SetEvent(ui.__mem_func__(self.__SelectGender), MAN)
			self.characterListButtonGenderMan[i].Show()

			self.characterListButtonGenderWoman[i] = ui.Button()
			self.characterListButtonGenderWoman[i].SetParent(self.characterListImageBoard[i])
			self.characterListButtonGenderWoman[i].SetPosition(45 + 28, 54)
			self.characterListButtonGenderWoman[i].SetUpVisual(IMG_PATCH + "create_character/buttons/gender_woman_default.tga")
			self.characterListButtonGenderWoman[i].SetOverVisual(IMG_PATCH + "create_character/buttons/gender_woman_default.tga")
			self.characterListButtonGenderWoman[i].SetDownVisual(IMG_PATCH + "create_character/buttons/gender_woman_default.tga")
			self.characterListButtonGenderWoman[i].SetDisableVisual(IMG_PATCH + "create_character/buttons/gender_woman_disable.tga")
			self.characterListButtonGenderWoman[i].SetEvent(ui.__mem_func__(self.__SelectGender), WOMAN)
			self.characterListButtonGenderWoman[i].Show()

			self.characterListButtonShapeFirst[i] = ui.Button()
			self.characterListButtonShapeFirst[i].SetParent(self.characterListImageBoard[i])
			self.characterListButtonShapeFirst[i].SetPosition(45 + 28 + 44, 54)
			self.characterListButtonShapeFirst[i].SetUpVisual(IMG_PATCH + "create_character/buttons/shape_first_default.tga")
			self.characterListButtonShapeFirst[i].SetOverVisual(IMG_PATCH + "create_character/buttons/shape_first_default.tga")
			self.characterListButtonShapeFirst[i].SetDownVisual(IMG_PATCH + "create_character/buttons/shape_first_default.tga")
			self.characterListButtonShapeFirst[i].SetDisableVisual(IMG_PATCH + "create_character/buttons/shape_first_disable.tga")
			self.characterListButtonShapeFirst[i].SetEvent(ui.__mem_func__(self.__SelectShape), SHAPE0)
			self.characterListButtonShapeFirst[i].Show()

			self.characterListButtonShapeSecond[i] = ui.Button()
			self.characterListButtonShapeSecond[i].SetParent(self.characterListImageBoard[i])
			self.characterListButtonShapeSecond[i].SetPosition(45 + 28 + 44 + 28, 54)
			self.characterListButtonShapeSecond[i].SetUpVisual(IMG_PATCH + "create_character/buttons/shape_second_default.tga")
			self.characterListButtonShapeSecond[i].SetOverVisual(IMG_PATCH + "create_character/buttons/shape_second_default.tga")
			self.characterListButtonShapeSecond[i].SetDownVisual(IMG_PATCH + "create_character/buttons/shape_second_default.tga")
			self.characterListButtonShapeSecond[i].SetDisableVisual(IMG_PATCH + "create_character/buttons/shape_second_disable.tga")
			self.characterListButtonShapeSecond[i].SetEvent(ui.__mem_func__(self.__SelectShape), SHAPE1)
			self.characterListButtonShapeSecond[i].Show()

		self.__SelectSlot(0)
		self.__SelectGender(app.GetRandom(MAN, WOMAN))
		self.__SelectShape(0)
		self.__SelectSlot(app.GetRandom(0, 3))
		self.__RefreshSlots()

		app.ShowCursor()

	def Close(self):
		print "---------------------------------------------------------------------------- CLOSE CREATE WINDOW"

		self.editCharacterName.Enable()
		self.dlgBoard.ClearDictionary()
		self.stream=0
		self.shapeButtonList = []
		self.genderButtonList = []
		self.btnCreate = 0
		self.btnCancel = 0
		self.btnLeft = 0
		self.btnRight = 0
		self.editCharacterName = 0
		self.backGround = None

		if musicinfo.createMusic != "":
			snd.FadeOutMusic("BGM/"+musicinfo.createMusic)

		for id in xrange(BASE_CHR_ID + SLOT_COUNT * PAGE_COUNT):
			chr.DeleteInstance(id)

		self.characterListImageBoard = {}
		self.characterListWindowName = {}
		self.characterListWindowNameText = {}
		self.characterListButtonSelect = {}
		self.characterListButtonGenderMan = {}
		self.characterListButtonGenderWoman = {}
		self.characterListButtonShapeFirst = {}
		self.characterListButtonShapeSecond = {}

		self.dlgBoard.Hide()
		self.Hide()

		app.HideCursor()
		event.Destroy()

	def EnableWindow(self):
		self.reservingRaceIndex = -1
		self.reservingShapeIndex = -1
		self.btnCreate.Enable()
		self.btnCancel.Enable()

		self.editCharacterName.SetFocus()
		self.editCharacterName.Enable()

		for page in xrange(PAGE_COUNT):
			for slot in xrange(SLOT_COUNT):
				chr_id = self.__GetSlotChrID(page, slot)
				chr.SelectInstance(chr_id)
				chr.BlendLoopMotion(chr.MOTION_INTRO_WAIT, 0.1)

	def DisableWindow(self):
		self.btnCreate.Disable()
		self.btnCancel.Disable()
		self.editCharacterName.Disable()

		self.btnCreate.SetUp()

	## Manage Character
	def __GetSlotChrID(self, page, slot):
		return BASE_CHR_ID + page * SLOT_COUNT + slot

	def __MakeCharacter(self, chr_id, race):
		chr.CreateInstance(chr_id)
		chr.SelectInstance(chr_id)
		chr.SetVirtualID(chr_id)
		chr.SetRace(race)
		chr.SetArmor(0)
		chr.SetHair(0)

		chr.Refresh()
		chr.SetMotionMode(chr.MOTION_MODE_GENERAL)
		chr.SetLoopMotion(chr.MOTION_INTRO_WAIT)

		chr.SetRotation(0.0)
		chr.Hide()

	def __SelectGender(self, gender):
		buttons = [self.characterListButtonGenderMan, self.characterListButtonGenderWoman]

		for i in range(len(buttons)):
			for j in range(len(buttons[i])):
				button = buttons[i][j]

				button.SetUp()
				button.Enable()

		for i in range(len(buttons[gender])):
			button = buttons[gender][i]

			button.Down()
			button.Disable()

		self.gender = gender
				
		for id in xrange(BASE_CHR_ID + SLOT_COUNT * PAGE_COUNT):
			chr.DeleteInstance(id)

		chr_id = self.__GetSlotChrID(self.gender, self.slot)

		self.__MakeCharacter(chr_id, self.characters[self.gender][self.slot])
		self.__SelectShape(self.shape)
		self.__RefreshSlots()

	def __SelectShape(self, shape):
		buttons = [self.characterListButtonShapeFirst, self.characterListButtonShapeSecond]

		for i in range(len(buttons)):
			for j in range(len(buttons[i])):
				button = buttons[i][j]

				button.SetUp()
				button.Enable()

		for i in range(len(buttons[shape])):
			button = buttons[shape][i]

			button.Down()
			button.Disable()

		self.shape = shape

		chr_id = self.__GetSlotChrID(self.gender, self.slot)		
		chr.SelectInstance(chr_id)		
		chr.ChangeShape(shape)		
		chr.SetMotionMode(chr.MOTION_MODE_GENERAL)
		chr.SetLoopMotion(chr.MOTION_INTRO_WAIT)

	def GetSlotIndex(self):
		return self.slot
		
	def __SelectSlot(self, slot):

		if (slot < 0):
			return

		if (slot >= SLOT_COUNT):
			return		

		if (self.slot == slot):
			return

		self.slot = slot

		if (self.IsShow()):
			snd.PlaySound("sound/ui/click.wav")
	
		chr_id = self.__GetSlotChrID(self.gender, slot)

		for id in xrange(BASE_CHR_ID + SLOT_COUNT * PAGE_COUNT):
			chr.DeleteInstance(id)
			
		chr.SelectInstance(chr_id)
		self.__MakeCharacter(chr_id, self.characters[self.gender][slot])
		self.__SelectShape(self.shape)
		self.__SelectGender(self.gender)

	def CreateCharacter(self):
		if (not self.reservingRaceIndex == -1):
			return

		textName = self.editCharacterName.GetText()
		if (not self.__CheckCreateCharacter(textName)):
			return

		if len(musicinfo.selectMusic):
			snd.FadeLimitOutMusic("BGM/%s" % musicinfo.selectMusic, systemSetting.GetMusicVolume()*0.05)

		self.DisableWindow()

		chr.SelectInstance(self.__GetSlotChrID(self.gender, self.slot))
		chr.PushOnceMotion(chr.MOTION_INTRO_SELECTED)

		self.reservingRaceIndex = chr.GetRace()
		self.reservingShapeIndex = self.shape
		self.reservingStartTime = app.GetTime()

	def CancelCreate(self):
		self.stream.SetSelectCharacterPhase()

	def ExitCreate(self):
		app.Exit()

	def __DecreaseSlotIndex(self):
		slotIndex = (self.GetSlotIndex() - 1 + SLOT_COUNT) % SLOT_COUNT
		self.__SelectSlot(slotIndex)

	def __IncreaseSlotIndex(self):
		slotIndex = (self.GetSlotIndex() + 1) % SLOT_COUNT
		self.__SelectSlot(slotIndex)

	def __RefreshSlots(self):
		imageMap = {
			0: ["sura_m", "ninja_m", "warrior_m", "shaman_m"],
			1: ["sura_w", "ninja_w", "warrior_w", "shaman_w"],
		}

		for i in range(4):
			self.characterListButtonSelect[i].SetUpVisual(IMG_PATCH + "create_character/races/%s.tga" % imageMap[self.gender][i])
			self.characterListButtonSelect[i].SetOverVisual(IMG_PATCH + "create_character/races/%s.tga" % imageMap[self.gender][i])
			self.characterListButtonSelect[i].SetDownVisual(IMG_PATCH + "create_character/races/%s.tga" % imageMap[self.gender][i])
			self.characterListButtonSelect[i].Show()

	def __SelectNewSlotIndex(self, position):
		newPosition = {
			0: 2,
			2: 0,
		}

		if position in newPosition:
			self.__SelectSlot(newPosition[position])
		else:
			self.__SelectSlot(position)

	def __CheckCreateCharacter(self, name):
		if len(name) == 0:
			self.PopupMessage(localeinfo.CREATE_INPUT_NAME, self.EnableWindow)
			return False

		if name.find(localeinfo.CREATE_GM_NAME)!=-1:
			self.PopupMessage(localeinfo.CREATE_ERROR_GM_NAME, self.EnableWindow)
			return False

		if net.IsInsultIn(name):
			self.PopupMessage(localeinfo.CREATE_ERROR_INSULT_NAME, self.EnableWindow)
			return False

		return True		

	## Event
	def OnCreateSuccess(self):
		self.stream.SetSelectCharacterPhase()

	def OnCreateFailure(self, type):
		if 1 == type:
			self.PopupMessage(localeinfo.CREATE_EXIST_SAME_NAME, self.EnableWindow)
		else:
			self.PopupMessage(localeinfo.CREATE_FAILURE, self.EnableWindow)

	def OnKeyDown(self, key):

		if key == 2:
			self.__SelectSlot(0)
		if key == 3:
			self.__SelectSlot(1)
		if key == 4:
			self.__SelectSlot(2)
		if key == 5:
			self.__SelectSlot(3)

		if 203 == key:
			self.__DecreaseSlotIndex()
		if 205 == key:
			self.__IncreaseSlotIndex()

		if 59 == key:
			self.__SelectGender(MAN_PAGE)
		if 60 == key:
			self.__SelectGender(WOMAN_PAGE)

		return True

	def OnUpdate(self):
		chr.Update()

		for page in xrange(PAGE_COUNT):
			for i in xrange(SLOT_COUNT):
				chr.SelectInstance(self.__GetSlotChrID(page, i))
				chr.Show()

		if (not self.reservingRaceIndex == - 1):
			if (app.GetTime() - self.reservingStartTime >= 1.5):

				chrSlot = self.stream.GetCharacterSlot()
				textName = self.editCharacterName.GetText()
				raceIndex = self.reservingRaceIndex
				shapeIndex = self.reservingShapeIndex

				net.SendCreateCharacterPacket(chrSlot, textName, raceIndex, shapeIndex, 0)

				self.reservingRaceIndex = -1

	def EmptyFunc(self):
		pass

	def PopupMessage(self, msg, func=0):
		if not func:
			func=self.EmptyFunc

		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, func, localeinfo.UI_OK)

	def OnPressExitKey(self):
		self.CancelCreate()
		return True
