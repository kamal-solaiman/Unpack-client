import ui
import app
import net
import wndMgr
import localeinfo
import uicommon
import chat

HWID_MAX_LEN_TEXT = 512

class hwidWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)

		self.checkBoxTable = {}
		self.__Initialize()
		self.__Load()
		self.RefreshMode()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __Initialize(self):
		self.hwidmode = 0
		self.hwidModeList = []

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/hwidManagerDialog.py")
		except:
			import exception
			exception.Abort("hwidManager.Initialize.LoadObject")
		try:
			GetObject = self.GetChild

			self.hwidModeButtonDict = {}
			self.board = GetObject("board")
			GetObject("accept_button").SetEvent(self.AskQuestion)
			GetObject("cancel_button").SetEvent(self.Close)
			GetObject("titlebar").SetCloseEvent(self.Close)
			GetObject("clear_button").SetEvent(self.Clear)

			self.hwidModeList.append(GetObject("hwid_unban"))
			self.hwidModeList.append(GetObject("hwid_ban"))
			self.hwidModeList.append(GetObject("hwid_hwidban"))
			self.hwidModeList.append(GetObject("hwid_deletehwidban"))
			self.hwidModeList.append(GetObject("hwid_totalhwidban"))
			self.hwidModeList.append(GetObject("hwid_chatban"))

			self.textLength = GetObject("textLine1")
			self.textLang = GetObject("textLine2")
			self.outtext = GetObject("ReasonText")
			self.playerName = GetObject("playerName_Value")
			self.textLine = GetObject("currentLine_Value")
			self.textLine.SetFocus()
		except:
			import exception
			exception.Abort("hwidManager.Initialize.BindObject")

		self.SetCenterPosition()
		self.UpdateRect()

	def __Load(self):
		self.LoadWindow()

		self.hwidModeList[0].SAFE_SetEvent(self.__OnClickModeButton0)
		self.hwidModeList[1].SAFE_SetEvent(self.__OnClickModeButton1)
		self.hwidModeList[2].SAFE_SetEvent(self.__OnClickModeButton2)
		self.hwidModeList[3].SAFE_SetEvent(self.__OnClickModeButton3)
		self.hwidModeList[4].SAFE_SetEvent(self.__OnClickModeButton4)
		self.hwidModeList[5].SAFE_SetEvent(self.__OnClickModeButton5)

	def __OnClickModeButton0(self):
		self.hwidmode = 1
		self.RefreshMode()

	def __OnClickModeButton1(self):
		self.hwidmode = 2
		self.RefreshMode()

	def __OnClickModeButton2(self):
		self.hwidmode = 3
		self.RefreshMode()

	def __OnClickModeButton3(self):
		self.hwidmode = 4
		self.RefreshMode()

	def __OnClickModeButton4(self):
		self.hwidmode = 5
		self.RefreshMode()

	def __OnClickModeButton5(self):
		self.hwidmode = 6
		self.RefreshMode()

	def RefreshMode(self):
		if self.hwidmode == 5:
			self.hwidModeList[0].SetUp()
			self.hwidModeList[1].SetUp()
			self.hwidModeList[2].SetUp()
			self.hwidModeList[3].SetUp()
			self.hwidModeList[4].Down()
			self.hwidModeList[5].SetUp()
		elif self.hwidmode == 4:
			self.hwidModeList[0].SetUp()
			self.hwidModeList[1].SetUp()
			self.hwidModeList[2].SetUp()
			self.hwidModeList[3].Down()
			self.hwidModeList[4].SetUp()
			self.hwidModeList[5].SetUp()
		elif self.hwidmode == 3:
			self.hwidModeList[0].SetUp()
			self.hwidModeList[1].SetUp()
			self.hwidModeList[2].Down()
			self.hwidModeList[3].SetUp()
			self.hwidModeList[4].SetUp()
			self.hwidModeList[5].SetUp()
		elif self.hwidmode == 2:
			self.hwidModeList[0].SetUp()
			self.hwidModeList[1].Down()
			self.hwidModeList[2].SetUp()
			self.hwidModeList[3].SetUp()
			self.hwidModeList[4].SetUp()
			self.hwidModeList[5].SetUp()
		elif self.hwidmode == 1:
			self.hwidModeList[0].Down()
			self.hwidModeList[1].SetUp()
			self.hwidModeList[2].SetUp()
			self.hwidModeList[3].SetUp()
			self.hwidModeList[4].SetUp()
			self.hwidModeList[5].SetUp()
		elif self.hwidmode == 6:
			self.hwidModeList[0].SetUp()
			self.hwidModeList[1].SetUp()
			self.hwidModeList[2].SetUp()
			self.hwidModeList[3].SetUp()
			self.hwidModeList[4].SetUp()
			self.hwidModeList[5].Down()

	def SetFlag(self, x, y, image):
		self.image = ui.ImageBox()
		self.image.SetParent(self)
		self.image.SetPosition(x, y)
		self.image.LoadImage(image)
		self.image.Show()
		return self.image

	def __HWIDModeBtn(self, mode):
		for btn in self.hwidModeButtonDict.values():
			btn.SetUp()
		if self.hwidModeButtonDict.has_key(mode):
			self.hwidModeButtonDict[mode].Down()

	def OnUpdate(self):
		(x, y) = wndMgr.GetMousePosition()

		def IsExistToolTip(key):
			return (self.checkBoxTable[key][0].IsIn())

		self.textLength.SetText(localeinfo.HWID_MAX_TEXT_LEN % (len(self.textLine.GetText()), HWID_MAX_LEN_TEXT))
		#self.textLang.SetText(localeinfo.HWID_COPYRIGHT_SIB)
		if self.hwidmode == 6:
			self.outtext.SetText(localeinfo.HWID_TIME_IN_MIN)
		else:
			self.outtext.SetText(localeinfo.HWID_REASON_TEXT)

	def Destroy(self):
		self.ClearDictionary()

	def Close(self):
		self.Hide()

	def Clear(self):
		self.textLine.SetText("")
		self.playerName.SetText("")
		self.textLine.SetFocus()

	def SendPacket(self):

		def GetReason():
			return str(self.textLine.GetText())

		def GetMode():
			return self.hwidmode

		def GetPlayer():
			return str(self.playerName.GetText())

		if self.hwidmode == 6:
			cb_time = str(self.textLine.GetText())
			cb_timelower = cb_time.lower()
			if cb_timelower.islower():
				chat.AppendChat(chat.CHAT_TYPE_INFO, "wrong format")
				return
			else:
				net.SendChatPacket("/block_chat " + str(self.playerName.GetText())+ " "+str(int(self.textLine.GetText())*60))
				chat.AppendChat(chat.CHAT_TYPE_COMMAND, str(self.playerName.GetText())+ " has now chatblock for "+str(int(self.textLine.GetText()))+ " minutes")
		else:
			net.SendHwidBanPacket(GetMode(), GetPlayer(), GetReason())

		self.Clear()

	def AnswerQuestion(self, answer):
		if not self.wndOpenQuestion:
			return

		self.wndOpenQuestion.Close()
		self.wndOpenQuestion = None

		if not answer:
			return

		self.SendPacket()

	def AskQuestion(self):
		self.wndOpenQuestion = uicommon.QuestionDialog()
		self.wndOpenQuestion.SetText(localeinfo.HWID_ASK_QUESTION)
		self.wndOpenQuestion.SetWidth(300)
		self.wndOpenQuestion.SetAcceptEvent(lambda arg = TRUE: self.AnswerQuestion(arg))
		self.wndOpenQuestion.SetCancelEvent(lambda arg = FALSE: self.AnswerQuestion(arg))
		self.wndOpenQuestion.Open()
