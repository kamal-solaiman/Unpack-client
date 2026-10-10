# coding: latin_1

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import chr
import net
import player

import grp
import wndMgr
import snd
import systemSetting
import localeinfo
import ui
import musicinfo
import playersettingmodule
import uicommon
import constinfo
import chat
import uicommon
import math

defaultCharacterSelect = False
IMG_PATCH = "d:/ymir work/ui/new_panels/"

class SelectCharacterWindow(ui.Window):

	SLOT_COUNT = 4
	SLOT_ROTATION = [135.0, 225.0, 315.0, 45.0]
	
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
		ui.Window.__init__(self)
		net.SetPhaseWindow(net.PHASE_WINDOW_SELECT, self)

		self.stream = stream
		self.slot = self.stream.GetCharacterSlot()

		self.openLoadingFlag = False
		self.startIndex = -1
		self.startReservingTime = 0

		self.dlgBoard = None
		self.changeNameFlag = False
		self.nameInputBoard = None
		self.sendedChangeNamePacket = False

		self.startIndex = -1
		self.isLoad = False
		
		self.curGauge = [0.0, 0.0, 0.0, 0.0]
		self.destGauge = [0.0, 0.0, 0.0, 0.0]

		self.characterListImageBoard = {}

		self.characterListTextName = {}
		self.characterListTextLevel = {}

		self.characterListButtonCreate = {}
		self.characterListButtonSelect = {}
		self.characterListButtonDelete = {}
		
		if defaultCharacterSelect == True:
			self.curRotation = []
			self.destRotation = []
			for rot in self.SLOT_ROTATION:
				self.curRotation.append(rot)
				self.destRotation.append(rot)

	def __del__(self):
		ui.Window.__del__(self)
		net.SetPhaseWindow(net.PHASE_WINDOW_SELECT, 0)

	def Open(self):
		if app.USE_PREMIUM_FEATURES:
			constinfo.player_premium_type = player.PREMIUM_TYPE_NONE

		constinfo.PLAYER_IN_GAME = False

		self.__LoadBoardDialog("uiscript/select_character_window.py")
		self.__LoadQuestionDialog("uiscript/questiondialog.py")

		playersettingmodule.LoadGameData("INIT")

		self.InitCharacterBoard()

		self.btnEnter.Enable()
		self.btnCreate.Enable()
		self.btnDelete.Enable()

		self.dlgBoard.Show()
		
		self.SetWindowName("SelectCharacterWindow")
		self.Show()

		if (len(musicinfo.selectMusic)):
			snd.SetMusicVolume(systemSetting.GetMusicVolume())
			snd.FadeInMusic("BGM/%s" % musicinfo.selectMusic)

		app.SetCenterPosition(0.0, 0.0, 0.0)
		app.SetCamera(1550.0, 15.0, 180.0, 95.0)

		self.isLoad = True

		self.Refresh()
		self.RefreshSlots()

		app.ShowCursor()

	def Close(self):
		if (len(musicinfo.selectMusic)):
			snd.FadeOutMusic("BGM/%s" % musicinfo.selectMusic)

		self.stream.popupWindow.Close()

		if (self.dlgBoard):
			self.dlgBoard.ClearDictionary()

		self.flagDict = {}
		self.dlgBoard = None
		self.btnEnter = None
		self.btnCreate = None
		self.btnDelete = None
		self.backGround = None

		self.dlgQuestion.ClearDictionary()
		self.dlgQuestion = None
		self.dlgQuestionText = None
		self.dlgQuestionAcceptButton = None
		self.dlgQuestionCancelButton = None
		self.privateInputBoard = None
		self.nameInputBoard = None
		
		for i in xrange(self.SLOT_COUNT):
			chr.DeleteInstance(i)

		self.characterListImageBoard = {}

		self.characterListTextName = {}
		self.characterListTextLevel = {}

		self.characterListButtonCreate = {}
		self.characterListButtonSelect = {}
		self.characterListButtonDelete = {}

		self.Hide()
		self.KillFocus()

		app.HideCursor()

	def Refresh(self):
		if (not self.isLoad):
			return

		indexArray = (3, 2, 1, 0)
		for index in indexArray:
			id = net.GetAccountCharacterSlotDataInteger(index, net.ACCOUNT_CHARACTER_SLOT_ID)
			race = net.GetAccountCharacterSlotDataInteger(index, net.ACCOUNT_CHARACTER_SLOT_RACE)
			form = net.GetAccountCharacterSlotDataInteger(index, net.ACCOUNT_CHARACTER_SLOT_FORM)
			name = net.GetAccountCharacterSlotDataString(index, net.ACCOUNT_CHARACTER_SLOT_NAME)
			hair = net.GetAccountCharacterSlotDataInteger(index, net.ACCOUNT_CHARACTER_SLOT_HAIR)

			if (id):
				self.MakeCharacter(index, id, name, race, form, hair)
				self.SelectSlot(index)

		self.SelectSlot(self.slot)

	def RefreshSlots(self):
		racesMap = {
			0: "warrior_m",
			1: "ninja_w",
			2: "sura_m",
			3: "shaman_w",
			4: "warrior_w",
			5: "ninja_m",
			6: "sura_w",
			7: "shaman_m",
		}

		for i in range(self.SLOT_COUNT):
			exist = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_ID)

			if self.characterListButtonCreate[i].IsShow():
				self.characterListButtonCreate[i].Hide()

			if self.characterListButtonSelect[i].IsShow():
				self.characterListButtonSelect[i].Hide()

			if self.characterListButtonDelete[i].IsShow():
				self.characterListButtonDelete[i].Hide()

			if exist:
				name = net.GetAccountCharacterSlotDataString(i, net.ACCOUNT_CHARACTER_SLOT_NAME)
				level = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_LEVEL)
				race = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_RACE)

				if race in racesMap:
					self.characterListButtonSelect[i].SetUpVisual(IMG_PATCH + "select_character/races/%s.tga" % racesMap[race])
					self.characterListButtonSelect[i].SetOverVisual(IMG_PATCH + "select_character/races/%s.tga" % racesMap[race])
					self.characterListButtonSelect[i].SetDownVisual(IMG_PATCH + "select_character/races/%s.tga" % racesMap[race])
					self.characterListButtonSelect[i].Show()

				self.characterListTextName[i].SetText("|cFF85705c|hName:|r |cFFc5be97|h%s|r" % name)
				self.characterListTextLevel[i].SetText("|cFF85705c|hLevel:|r |cFFc5be97|h%s|r" % level)

				self.characterListButtonDelete[i].Show()

			else:
				self.characterListButtonCreate[i].Show()

	def GetCharacterSlotID(self, slotIndex):
		return net.GetAccountCharacterSlotDataInteger(slotIndex, net.ACCOUNT_CHARACTER_SLOT_ID)

	def __LoadQuestionDialog(self, fileName):
		self.dlgQuestion = ui.ScriptWindow()

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self.dlgQuestion, fileName)
		except:
			import exception
			exception.Abort("SelectCharacterWindow.LoadQuestionDialog.LoadScript")

		try:
			GetObject = self.dlgQuestion.GetChild
			self.dlgQuestionText = GetObject("message")
			self.dlgQuestionAcceptButton = GetObject("accept")
			self.dlgQuestionCancelButton = GetObject("cancel")
		except:
			import exception
			exception.Abort("SelectCharacterWindow.LoadQuestionDialog.BindObject")

		self.dlgQuestionText.SetText(localeinfo.SELECT_DO_YOU_DELETE_REALLY)
		self.dlgQuestionAcceptButton.SetEvent(ui.__mem_func__(self.RequestDeleteCharacter))
		self.dlgQuestionCancelButton.SetEvent(ui.__mem_func__(self.dlgQuestion.Hide))
		return True

	def __LoadBoardDialog(self, fileName):
		self.dlgBoard = ui.ScriptWindow()

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self.dlgBoard, fileName)
		except:
			import exception
			exception.Abort("SelectCharacterWindow.LoadBoardDialog.LoadScript")

		try:
			GetObject = self.dlgBoard.GetChild
			
			self.btnEnter = GetObject("enter_button")
			self.btnCreate = GetObject("create_button")
			self.btnDelete = GetObject("delete_button")
			self.btnExit = GetObject("exit_button")
			self.btnBack = GetObject("back_button")
			
			self.btnLeft = GetObject("left_button")
			self.btnRight = GetObject("right_button")

			self.backGround = GetObject("BackGround")
			
			self.charName = GetObject("name")
			self.guildName = GetObject("guild")
			self.level = GetObject("level")
			self.time = GetObject("time")

			self.gaugeList = { 0 : [] }
			self.gaugeList[0].append(GetObject("hth_gauge_full"))
			self.gaugeList[0].append(GetObject("int_gauge_full"))
			self.gaugeList[0].append(GetObject("str_gauge_full"))
			self.gaugeList[0].append(GetObject("dex_gauge_full"))

			self.hth_slotbar_text = GetObject("hth_slotbar_text")
			self.int_slotbar_text = GetObject("int_slotbar_text")
			self.dex_slotbar_text = GetObject("dex_slotbar_text")
			self.str_slotbar_text = GetObject("str_slotbar_text")

			for i in range(self.SLOT_COUNT):
				self.characterListImageBoard[i] = ui.ImageBox()
				self.characterListImageBoard[i].SetParent(self.backGround)
				self.characterListImageBoard[i].SetPosition(wndMgr.GetScreenWidth() - 306, wndMgr.GetScreenHeight() / 2 - 245 + i * 126)
				if app.ENABLE_WINDOW_RESIZE:
					self.characterListImageBoard[i].SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - 306, Expr("SCREEN_HEIGHT") / 2 - 245 + i * 126)})
				self.characterListImageBoard[i].LoadImage(IMG_PATCH + "select_character/character_slot.tga")
				self.characterListImageBoard[i].Show()

				self.characterListTextName[i] = ui.TextLine()
				self.characterListTextName[i].SetParent(self.characterListImageBoard[i])
				self.characterListTextName[i].SetPosition(112, 29)
				self.characterListTextName[i].Show()

				self.characterListTextLevel[i] = ui.TextLine()
				self.characterListTextLevel[i].SetParent(self.characterListImageBoard[i])
				self.characterListTextLevel[i].SetPosition(112, 55)
				self.characterListTextLevel[i].Show()

				self.characterListButtonSelect[i] = ui.Button()
				self.characterListButtonSelect[i].SetParent(self.characterListImageBoard[i])
				self.characterListButtonSelect[i].SetPosition(5, 8)
				self.characterListButtonSelect[i].SetEvent(ui.__mem_func__(self.SelectSlot), i)

				self.characterListButtonCreate[i] = ui.Button()
				self.characterListButtonCreate[i].SetParent(self.characterListImageBoard[i])
				self.characterListButtonCreate[i].SetPosition(5, 8)
				self.characterListButtonCreate[i].SetUpVisual(IMG_PATCH + "select_character/buttons/create_default.tga")
				self.characterListButtonCreate[i].SetOverVisual(IMG_PATCH + "select_character/buttons/create_default.tga")
				self.characterListButtonCreate[i].SetDownVisual(IMG_PATCH + "select_character/buttons/create_default.tga")
				self.characterListButtonCreate[i].SetEvent(ui.__mem_func__(self.CreateCharacterNew), i)

				self.characterListButtonDelete[i] = ui.Button()
				self.characterListButtonDelete[i].SetParent(self.characterListImageBoard[i])
				self.characterListButtonDelete[i].SetPosition(254, 37)
				self.characterListButtonDelete[i].SetUpVisual(IMG_PATCH + "select_character/buttons/delete_default.tga")
				self.characterListButtonDelete[i].SetOverVisual(IMG_PATCH + "select_character/buttons/delete_default.tga")
				self.characterListButtonDelete[i].SetDownVisual(IMG_PATCH + "select_character/buttons/delete_default.tga")
				self.characterListButtonDelete[i].SetEvent(ui.__mem_func__(self.InputPrivateCode))

		except:
			import exception
			exception.Abort("SelectCharacterWindow.LoadBoardDialog.BindObject")

		self.btnEnter.SetEvent(ui.__mem_func__(self.StartGame))
		self.btnCreate.SetEvent(ui.__mem_func__(self.CreateCharacter))
		self.btnDelete.SetEvent(ui.__mem_func__(self.InputPrivateCode))
		self.btnExit.SetEvent(ui.__mem_func__(self.ExitSelect))
		self.btnBack.SetEvent(ui.__mem_func__(self.ExitSelect))
		
		self.btnLeft.SetEvent(ui.__mem_func__(self.DecreaseSlotIndex))
		self.btnRight.SetEvent(ui.__mem_func__(self.IncreaseSlotIndex))
		
		self.chrRenderer = self.CharacterRenderer()
		self.chrRenderer.SetParent(self.backGround)
		self.chrRenderer.Show()
		
		return True
    
	def SameLoginDisconnect(self):
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(localeinfo.LOGIN_FAILURE_SAMELOGIN, self.ExitSelect, localeinfo.UI_OK)
        
	def MakeCharacter(self, index, id, name, race, form, hair):
		if (not id):
			return

		chr.CreateInstance(index)
		chr.SelectInstance(index)
		chr.SetVirtualID(index)
		chr.SetNameString(name)

		chr.SetRace(race)
		chr.SetArmor(form)
		chr.SetHair(hair)

		chr.Refresh()
		chr.SetMotionMode(chr.MOTION_MODE_GENERAL)
		chr.SetLoopMotion(chr.MOTION_INTRO_WAIT)

		chr.SetRotation(0.0)
		chr.Show()

	def StartGame(self):

		if (self.sendedChangeNamePacket):
			return

		if (self.changeNameFlag):
			self.OpenChangeNameDialog()
			return

		if (not self.startIndex == -1):
			return

		if (len(musicinfo.selectMusic)):
			snd.FadeLimitOutMusic("BGM/%s" % musicinfo.selectMusic, systemSetting.GetMusicVolume()*0.05)

		self.btnEnter.Disable()
		self.btnCreate.Disable()
		self.btnDelete.Disable()
		
		self.dlgQuestion.Hide()

		self.stream.SetCharacterSlot(self.slot)
		
		self.startIndex = self.slot
		self.startReservingTime = app.GetTime()

		for i in xrange(self.SLOT_COUNT):

			if (not chr.HasInstance(i)):
				continue

			chr.SelectInstance(i)

			if (i == self.slot):
				self.slot = self.slot
				chr.PushOnceMotion(chr.MOTION_INTRO_SELECTED, 0.1)
				continue

			chr.PushOnceMotion(chr.MOTION_INTRO_NOT_SELECTED, 0.1)

	def OpenChangeNameDialog(self):
		nameInputBoard = uicommon.InputDialogWithDescription()
		nameInputBoard.SetTitle(localeinfo.SELECT_CHANGE_NAME_TITLE)
		nameInputBoard.SetAcceptEvent(ui.__mem_func__(self.AcceptInputName))
		nameInputBoard.SetCancelEvent(ui.__mem_func__(self.CancelInputName))
		nameInputBoard.SetMaxLength(chr.PLAYER_NAME_MAX_LEN)
		nameInputBoard.SetBoardWidth(200)
		nameInputBoard.SetDescription(localeinfo.SELECT_INPUT_CHANGING_NAME)
		nameInputBoard.Open()
		nameInputBoard.slot = self.slot
		self.nameInputBoard = nameInputBoard

	def OnChangeName(self, id, name):
		self.SelectSlot(id)
		self.sendedChangeNamePacket = False
		self.PopupMessage(localeinfo.SELECT_CHANGED_NAME)

	def AcceptInputName(self):
		changeName = self.nameInputBoard.GetText()
		if (not changeName):
			return

		self.sendedChangeNamePacket = True
		net.SendChangeNamePacket(self.nameInputBoard.slot, changeName)
		return self.CancelInputName()

	def CancelInputName(self):
		self.nameInputBoard.Close()
		self.nameInputBoard = None
		return True

	def OnCreateFailure(self, type):
		self.sendedChangeNamePacket = False
		if (0 == type):
			self.PopupMessage(localeinfo.SELECT_CHANGE_FAILURE_STRANGE_NAME)
		elif (1 == type):
			self.PopupMessage(localeinfo.SELECT_CHANGE_FAILURE_ALREADY_EXIST_NAME)
		elif (100 == type):
			self.PopupMessage(localeinfo.SELECT_CHANGE_FAILURE_STRANGE_INDEX)

	def CreateCharacter(self):
		if (not self.GetCharacterSlotID(self.slot)):
			self.stream.SetCharacterSlot(self.slot)

			EMPIRE_MODE = True

			if (EMPIRE_MODE):
				if self.__AreAllSlotEmpty():
					self.stream.SetReselectEmpirePhase()
				else:
					self.stream.SetCreateCharacterPhase()
			else:
				self.stream.SetCreateCharacterPhase()

	def CreateCharacterNew(self, slot):
		self.slot = slot
		self.CreateCharacter()

	def __AreAllSlotEmpty(self):
		for iSlot in xrange(self.SLOT_COUNT):
			if (not net.GetAccountCharacterSlotDataInteger(iSlot, net.ACCOUNT_CHARACTER_SLOT_ID) == 0):
				return False
		return True

	def PopupDeleteQuestion(self):
		id = self.GetCharacterSlotID(self.slot)
		if (not id):
			return

		self.dlgQuestion.Show()
		self.dlgQuestion.SetTop()

	def RequestDeleteCharacter(self):
		self.dlgQuestion.Hide()

		id = self.GetCharacterSlotID(self.slot)
		if (not id):
			self.PopupMessage(localeinfo.SELECT_EMPTY_SLOT)
			return

		net.SendDestroyCharacterPacket(self.slot, "1234567")
		self.PopupMessage(localeinfo.SELECT_DELEING)

	def InputPrivateCode(self):
		privateInputBoard = uicommon.InputDialogWithDescription()
		privateInputBoard.SetTitle(localeinfo.INPUT_PRIVATE_CODE_DIALOG_TITLE)
		privateInputBoard.SetAcceptEvent(ui.__mem_func__(self.AcceptInputPrivateCode))
		privateInputBoard.SetCancelEvent(ui.__mem_func__(self.CancelInputPrivateCode))
		privateInputBoard.SetNumberMode()

		privateInputBoard.SetSecretMode()
		privateInputBoard.SetMaxLength(7)
			
		privateInputBoard.SetBoardWidth(250)
		privateInputBoard.SetDescription(localeinfo.INPUT_PRIVATE_CODE_DIALOG_DESCRIPTION)
		privateInputBoard.Open()
		self.privateInputBoard = privateInputBoard

	def AcceptInputPrivateCode(self):
		privateCode = self.privateInputBoard.GetText()
		if (not privateCode):
			return

		id = self.GetCharacterSlotID(self.slot)
		if (not id):
			self.PopupMessage(localeinfo.SELECT_EMPTY_SLOT)
			return

		net.SendDestroyCharacterPacket(self.slot, privateCode)
		self.PopupMessage(localeinfo.SELECT_DELEING)

		self.CancelInputPrivateCode()
		return True

	def CancelInputPrivateCode(self):
		self.privateInputBoard = None
		return True

	def OnDeleteSuccess(self, slot):
		self.PopupMessage(localeinfo.SELECT_DELETED)
		self.DeleteCharacter(slot)

	def OnDeleteFailure(self):
		self.PopupMessage(localeinfo.SELECT_CAN_NOT_DELETE)

	def DeleteCharacter(self, index):
		chr.DeleteInstance(index)
		self.SelectSlot(self.slot)

	def ExitSelect(self):
		self.dlgQuestion.Hide()
		self.Hide()
		self.stream.SetLoginPhase()

	def GetSlotIndex(self):
		return self.slot

	def SelectSlot(self, index):
		if (index < 0):
			return

		if (index >= self.SLOT_COUNT):
			return

		self.slot = index
		
		if defaultCharacterSelect == True:
			for i in xrange(self.SLOT_COUNT):
				self.destRotation[(i + self.slot) % self.SLOT_COUNT] = self.SLOT_ROTATION[i]
		else:
			for i in xrange(self.SLOT_COUNT):
				chr.DeleteInstance(i)
	
		chr.SelectInstance(self.slot)
		self.destGauge = [0.0, 0.0, 0.0, 0.0]
		
		id = net.GetAccountCharacterSlotDataInteger(self.slot, net.ACCOUNT_CHARACTER_SLOT_ID)
		if (id):
			self.btnEnter.Enable()
			self.btnDelete.Enable()
			self.btnCreate.Disable()

			name = net.GetAccountCharacterSlotDataString(self.slot, net.ACCOUNT_CHARACTER_SLOT_NAME)
			level = net.GetAccountCharacterSlotDataInteger(self.slot, net.ACCOUNT_CHARACTER_SLOT_LEVEL)
			hth = net.GetAccountCharacterSlotDataInteger(self.slot, net.ACCOUNT_CHARACTER_SLOT_HTH)
			int = net.GetAccountCharacterSlotDataInteger(self.slot, net.ACCOUNT_CHARACTER_SLOT_INT)
			str = net.GetAccountCharacterSlotDataInteger(self.slot, net.ACCOUNT_CHARACTER_SLOT_STR)
			dex = net.GetAccountCharacterSlotDataInteger(self.slot, net.ACCOUNT_CHARACTER_SLOT_DEX)
			race = net.GetAccountCharacterSlotDataInteger(self.slot, net.ACCOUNT_CHARACTER_SLOT_RACE)
			playtime = net.GetAccountCharacterSlotDataInteger(self.slot, net.ACCOUNT_CHARACTER_SLOT_PLAYTIME)
			form = net.GetAccountCharacterSlotDataInteger(index, net.ACCOUNT_CHARACTER_SLOT_FORM)
			hair = net.GetAccountCharacterSlotDataInteger(index, net.ACCOUNT_CHARACTER_SLOT_HAIR)
			
			self.changeNameFlag = net.GetAccountCharacterSlotDataInteger(self.slot, net.ACCOUNT_CHARACTER_SLOT_CHANGE_NAME_FLAG)
			
			self.MakeCharacter(self.slot, id, name, race, form, hair)
				
			self.charName.SetText("%s" % name)
			if (net.GetAccountCharacterSlotDataString(self.slot, net.ACCOUNT_CHARACTER_SLOT_GUILD_NAME)):
				self.guildName.SetText(net.GetAccountCharacterSlotDataString(self.slot, net.ACCOUNT_CHARACTER_SLOT_GUILD_NAME))
			else:
				self.guildName.SetText("---")

			self.level.SetText("%d" % level)
			self.time.SetText("%d min." % playtime)
			self.hth_slotbar_text.SetText("%d" % hth)
			self.int_slotbar_text.SetText("%d" % int)
			self.str_slotbar_text.SetText("%d" % str)
			self.dex_slotbar_text.SetText("%d" % dex)

			statesSummary = float(120)

			if (statesSummary > 0.0):
				self.destGauge = [float(hth) / statesSummary, float(int) / statesSummary, float(str) / statesSummary, float(dex) / statesSummary]
		else:
			self.InitCharacterBoard()

	def InitCharacterBoard(self):
		self.btnEnter.Disable()
		self.btnDelete.Disable()
		self.btnCreate.Enable()
		
		self.charName.SetText("")
		self.guildName.SetText("")
		self.level.SetText("")
		self.time.SetText("")
		self.hth_slotbar_text.SetText("")
		self.int_slotbar_text.SetText("")
		self.str_slotbar_text.SetText("")
		self.dex_slotbar_text.SetText("")
		
	def DecreaseSlotIndex(self):
		if (self.startIndex == -1):
			slotIndex = (self.GetSlotIndex() - 1 + self.SLOT_COUNT) % self.SLOT_COUNT
			self.SelectSlot(slotIndex)

	def IncreaseSlotIndex(self):
		if (self.startIndex == -1):
			slotIndex = (self.GetSlotIndex() + 1) % self.SLOT_COUNT
			self.SelectSlot(slotIndex)

	def OnKeyDown(self, key):
		if (1 == key):
			self.ExitSelect()
		if (2 == key):
			self.SelectSlot(0)
		if (3 == key):
			self.SelectSlot(1)
		if (4 == key):
			self.SelectSlot(2)
		if (5 == key):
			self.SelectSlot(3)

		if (28 == key):
			id = net.GetAccountCharacterSlotDataInteger(self.slot, net.ACCOUNT_CHARACTER_SLOT_ID)
			if (0 == id):
				self.CreateCharacter()
			else:
				self.StartGame()

		if (203 == key):
			self.DecreaseSlotIndex()
		if (205 == key):
			self.IncreaseSlotIndex()

		return True

	def OnUpdate(self):
		chr.Update()
		
		for i in xrange(4):
			self.curGauge[i] += (self.destGauge[i] - self.curGauge[i]) / 10.0
			if (abs(self.curGauge[i] - self.destGauge[i]) < 0.005):
				self.curGauge[i] = self.destGauge[i]
			self.gaugeList[0][i].SetPercentage(self.curGauge[i], 1.0)

		for i in xrange(self.SLOT_COUNT):
			if defaultCharacterSelect == True:
				if (not chr.HasInstance(i)):
					continue

				chr.SelectInstance(i)
				
				distance = 50.0
				rotRadian = self.curRotation[i] * (math.pi*2) / 360.0
				x = distance*math.sin(rotRadian) + distance*math.cos(rotRadian)
				y = distance*math.cos(rotRadian) - distance*math.sin(rotRadian)
				chr.SetPixelPosition(int(x), int(y), 30)

				dir = app.GetRotatingDirection(self.destRotation[i], self.curRotation[i])
				rot = app.GetDegreeDifference(self.destRotation[i], self.curRotation[i])

				if (app.DEGREE_DIRECTION_RIGHT == dir):
					self.curRotation[i] += rot / 10.0
				elif (app.DEGREE_DIRECTION_LEFT == dir):
					self.curRotation[i] -= rot / 10.0

				self.curRotation[i] = (self.curRotation[i] + 360.0) % 360.0
			else:
				chr.SelectInstance(i)

		if (not self.startIndex == -1):
			if (app.GetTime() - self.startReservingTime > 0.0):
				if (not self.openLoadingFlag):
					chrSlot = self.stream.GetCharacterSlot()
					net.DirectEnter(chrSlot)

					self.openLoadingFlag = True
					player.SetPlayTime(net.GetAccountCharacterSlotDataInteger(self.slot, net.ACCOUNT_CHARACTER_SLOT_PLAYTIME))

					chat.Clear()

	def EmptyFunc(self):
		pass

	def PopupMessage(self, msg, func = 0):
		if (not func):
			func = self.EmptyFunc

		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, func, localeinfo.UI_OK)

	def OnPressExitKey(self):
		self.ExitSelect()
		return True

