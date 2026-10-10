import ui
import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import wndMgr
import localeinfo
import uiscriptlocale
import constinfo
import net
import uitooltip

VOICE_TYPE_TEXT_DICT = {
	app.VOICE_CHAT_TYPE_NONE	: "",
	app.VOICE_CHAT_TYPE_LOCAL	: "[{}] ".format(localeinfo.VOICE_CHAT_LOCAL),
	app.VOICE_CHAT_TYPE_PARTY	: "[{}] ".format(localeinfo.VOICE_CHAT_PARTY),
	app.VOICE_CHAT_TYPE_GUILD	: "[{}] ".format(localeinfo.VOICE_CHAT_GUILD),
	app.VOICE_CHAT_TYPE_MAX_NUM	: "",
}
IMG_DIR = "d:/ymir work/ui/voice_chat/"
VOICE_TYPE_IMAGE_DICT = {
	app.VOICE_CHAT_TYPE_NONE	: "d:/ymir work/ui/voice_chat/voice_normal.png",
	app.VOICE_CHAT_TYPE_LOCAL	: "d:/ymir work/ui/voice_chat/voice_normal.png",
	app.VOICE_CHAT_TYPE_PARTY	: "d:/ymir work/ui/voice_chat/voice_party.png",
	app.VOICE_CHAT_TYPE_GUILD	: "d:/ymir work/ui/voice_chat/voice_guild.png",
	app.VOICE_CHAT_TYPE_MAX_NUM	: "d:/ymir work/ui/voice_chat/voice_muted.png",
}

VOICE_TYPE_COLOR_DICT = {
	app.VOICE_CHAT_TYPE_NONE	: 0xffe3e3e3, # Gray
	app.VOICE_CHAT_TYPE_LOCAL	: 0xffe3e3e3, # Gray
	app.VOICE_CHAT_TYPE_PARTY	: 0xff44accf, # Blue
	app.VOICE_CHAT_TYPE_GUILD	: 0xff43d164, # Green
	app.VOICE_CHAT_TYPE_MAX_NUM	: 0xffb32525, # Red
}

DROP_MESSAGE_TIME = 0.35
DROP_MAX_STACK = 10
SPEAKER_BOARD_WIDTH = 350

class SpeakerObject(ui.Bar):
	def __init__(self, topLevel, toolTip):
		ui.Bar.__init__(self)

		self.topLevel = topLevel
		self.toolTip = toolTip

		self.isLocked = False
		self.isMouseOver = False
		self.playerNameLine = None
		self.volumeController = None
		self.playerName = ""

		self.endTime = app.GetTime() + DROP_MESSAGE_TIME

		self.SetColor(0x77000000)

	def __del__(self):
		ui.Bar.__del__(self)

	def SetInfo(self, playerName, voiceType):
		self.playerName = playerName

		self.chatTypeImage = ui.ExpandedImageBox()
		self.chatTypeImage.SetParent(self)
		self.chatTypeImage.LoadImage(VOICE_TYPE_IMAGE_DICT[int(voiceType)])
		self.chatTypeImage.SetPosition(7, 0)
		self.chatTypeImage.AddFlag("not_pick")

		self.playerNameX = self.chatTypeImage.GetLocalPosition()[0] + self.chatTypeImage.GetWidth() + 10
		self.playerNameLine = ui.TextLine()
		self.playerNameLine.SetParent(self)
		self.playerNameLine.SetPosition(self.playerNameX, 4)
		self.playerNameLine.SetHorizontalAlignRight()
		self.playerNameLine.SetText(str(VOICE_TYPE_TEXT_DICT[int(voiceType)] + playerName))
		self.playerNameLine.SetOutline()
		self.playerNameLine.SetFeather(False)
		self.playerNameLine.SetPackedFontColor(VOICE_TYPE_COLOR_DICT[int(voiceType)])
		self.playerNameLine.AddFlag("not_pick")

		self.volumeControllerX = self.playerNameX + self.playerNameLine.GetTextSize()[0] + 10
		self.volumeController = ui.SliderBar()
		self.volumeController.SetParent(self)
		self.volumeController.SetPosition(self.volumeControllerX, 6)
		self.volumeController.SetEvent(ui.__mem_func__(self.OnChangeSpeakerVolume))
		self.volumeController.SetSliderPos(constinfo.GetVoiceChatVolume(playerName))
		self.volumeController.AddFlag("not_pick")
		self.volumeController.backGroundImage.AddFlag("not_pick")
		self.volumeController.cursor.SAFE_SetOverInEvent(self.__OnMouseOverIn, True)
		self.volumeController.cursor.SAFE_SetOverOutEvent(self.OnMouseOverOut)

		app.VoiceChatSetVolumeForSpeaker(self.playerName, constinfo.GetVoiceChatVolume(playerName))

		self.SetSize(self.volumeControllerX, 24)

	def ShowInfos(self):
		self.playerNameLine.Show()
		self.chatTypeImage.Show()

	def __OnMouseOverIn(self, isVolume = False):
		self.toolTip.ClearToolTip()
		self.toolTip.Show()
		if isVolume:
			pos = self.volumeController.GetSliderPos()
			self.toolTip.SetTitle("{}%".format(int(pos * 100.0)))
		else:
			if not self.isLocked:
				self.toolTip.SetTitle(uiscriptlocale.VOICE_CHAT_TOOLTIP_CLICK_TO_LOCK)
			else:
				self.toolTip.SetTitle(uiscriptlocale.VOICE_CHAT_TOOLTIP_CLICK_TO_UNLOCK)

		if not self.isMouseOver:
			self.isMouseOver = True
			self.SetSize(self.volumeControllerX + self.volumeController.GetWidth() + 10, 24)
			self.volumeController.Show()
			self.volumeController.SetTop()

	def OnMouseOverIn(self):
		self.__OnMouseOverIn(False)

	def OnMouseOverOut(self):
		self.isMouseOver = False
		self.toolTip.Hide()
		if not self.isLocked:
			self.SetSize(self.volumeControllerX, 24)
			self.volumeController.Hide()

	def OnMouseLeftButtonDown(self):
		self.toolTip.ClearToolTip()
		if self.isLocked:
			self.isLocked = False
			self.toolTip.SetTitle(uiscriptlocale.VOICE_CHAT_TOOLTIP_CLICK_TO_LOCK)
		else:
			self.isLocked = True
			self.toolTip.SetTitle(uiscriptlocale.VOICE_CHAT_TOOLTIP_CLICK_TO_UNLOCK)

	def isTimeout(self):
		if self.isMouseOver or self.isLocked:
			return False
		return app.GetTime() >= self.endTime

	def AddTime(self):
		self.endTime = app.GetTime() + DROP_MESSAGE_TIME

	def OnChangeSpeakerVolume(self):
		pos = self.volumeController.GetSliderPos()
		if self.isMouseOver:
			self.toolTip.ClearToolTip()
			self.toolTip.Show()
			self.toolTip.SetTitle("{}%".format(int(pos * 100.0)))
		else:
			self.toolTip.Hide()

		constinfo.SetVoiceChatVolume(self.playerName, pos)
		app.VoiceChatSetVolumeForSpeaker(self.playerName, pos)

class SpeakerQueue(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)

		self.notifyStack = {}

		self.lastClock = 0
		self.timeDiff = 0
		self.nextY = 0
		self.tooltip = uitooltip.ToolTip()

		self.__Reset()

	def __del__(self):
		self.tooltip = None
		self.notifyStack = None
		ui.Window.__del__(self)

	def OnMessage(self, voicePlayer, voiceType):
		count = len(self.notifyStack)
		if count == DROP_MAX_STACK:
			self.notifyStack.remove(self.notifyStack[0])
		
		if voicePlayer in self.notifyStack.keys():
			self.notifyStack[voicePlayer].AddTime()
			return

		message = SpeakerObject(self, self.tooltip)
		message.SetParent(self)
		message.SetInfo(voicePlayer, voiceType)
		message.Hide()

		self.notifyStack[voicePlayer] = message
		self.__Render()

	def __Reset(self):
		self.SetPosition(5, wndMgr.GetScreenHeight() - 150)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : (5, Expr("SCREEN_HEIGHT") - 150)})
		self.Show()

	def __Render(self):
		keys_to_delete = [key for key, speaker in self.notifyStack.items() if speaker.isTimeout()]
		for key in keys_to_delete:
			del self.notifyStack[key]

		stack = list(self.notifyStack.values())
		stack.reverse()

		itemSize = 27
		initialSize = len(stack) * itemSize
		self.SetSize(SPEAKER_BOARD_WIDTH, initialSize)
		self.SetPosition(5, wndMgr.GetScreenHeight() - 150 - initialSize)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : (5, Expr("SCREEN_HEIGHT") - 150 - initialSize)})
		self.nextY = initialSize

		for it in stack:
			it.SetPosition(5, self.nextY - itemSize)

			if not it.IsShow():
				it.Show()
				it.ShowInfos()

			self.nextY -= itemSize


	def OnUpdate(self):
		if len(self.notifyStack) > 0:
			if (app.GetTime() - self.lastClock) >= self.timeDiff:
				self.lastClock = app.GetTime()
				self.__Render()

	def Show(self):
		ui.Window.Show(self)


def TextLine(parent, text, x, y):
	textLine = ui.TextLine()
	textLine.SetText(text)
	textLine.SetPackedFontColor(0xfffff2cc)
	textLine.SetOutline()
	textLine.SetParent(parent)
	textLine.SetPosition(x, y)
	textLine.Show()
	return textLine


def Button(parent, text, x, y):
	btn = ui.RadioButton()
	# btn.SetUpVisual(IMG_DIR + "btn_cat_1.png")
	# btn.SetOverVisual(IMG_DIR + "btn_cat_2.png")
	# btn.SetDownVisual(IMG_DIR + "btn_cat_3.png")
	btn.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
	btn.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
	btn.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
	btn.SetText(text)
	btn.SetParent(parent)
	btn.SetPosition(x, y)
	btn.Show()
	return btn

def ToggleButton(parent, text, x, y):
	btn = ui.ToggleButton()
	btn.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
	btn.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
	btn.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
	btn.SetText(text)
	btn.SetParent(parent)
	btn.SetPosition(x, y)
	btn.Show()
	return btn

class VoiceChatConfig(ui.Window):
	BOARD_WIDTH = 370 + 65
	BOARD_HEIGHT = 145 + 80

	VOICE_TYPE_TEXT_DICT = {
		0: "{} ".format(localeinfo.VOICE_CHAT_LOCAL),
		1: "{} ".format(localeinfo.VOICE_CHAT_PARTY),
		2: "{} ".format(localeinfo.VOICE_CHAT_GUILD),
	}

	INDEX_TO_CHAT_TYPE = {
		0: "LOCAL",
		1: "PARTY",
		2: "GUILD",
	}

	BUTTON_START_X = 10
	BUTTON_WIDTH = 85 + 30

	def __init__(self):
		ui.Window.__init__(self)

		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetSize(self.BOARD_WIDTH, self.BOARD_HEIGHT)

		x, y = 10, (wndMgr.GetScreenHeight() - self.GetHeight()) / 2
		self.SetPosition(x, y)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : (10, (Expr("SCREEN_HEIGHT") - self.GetHeight()) / 2)})

		self.__Reset()
		self.__Load()

		constinfo.LoadVoiceChatConfig()
		constinfo.SendVoiceChatVolumes()

		self.Hide()
		self.SetTop()

	def __del__(self):
		self.__Reset()
		ui.Window.__del__(self)

	def __Load(self):
		self.__CreateElements()

	def __Reset(self):
		self.currentConfig = 0
		self.board = None

		self.texts = []
		self.recorderButtons = []
		self.voiceHearButtons = []
		self.voiceTypeButtons = []

	def __CreateElements(self):
		# Board
		self.board = ui.BoardWithTitleBar()
		self.board.SetCloseEvent(ui.__mem_func__(self.Hide))
		self.board.SetTitleName(localeinfo.VOICE_CHAT_CONFIG_TITLE)
		self.board.SetSize(self.BOARD_WIDTH, self.BOARD_HEIGHT)
		self.board.SetParent(self)
		self.board.SetPosition(0, 0)
		self.board.AddFlag("attach")
		self.board.Show()


		infoImage = ui.ImageBox()
		infoImage.SetParent(self.board)
		infoImage.LoadImage("d:/ymir work/ui/game/wheel/question_mark_glow.png")
		infoImage.SAFE_SetStringEvent("MOUSE_OVER_IN", self.ShowVoiceChatInfo)
		infoImage.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.HideVoiceChatInfo)
		infoImage.SetWindowHorizontalAlignRight()
		#infoImage.SetSize(250, 65)
		infoImage.SetPosition(180, 10)
		infoImage.SetWindowHorizontalAlignCenter()
		infoImage.Show()
		self.infoImage = infoImage

		# Microphone config
		depth = 0
		self.texts.append(TextLine(self.board, localeinfo.VOICE_CHAT_CONFIG_MICROPHONE, self.BOARD_WIDTH - 20, 35 + 25 * depth))
		for i in xrange(3):
			btn = Button(self.board, "", self.BUTTON_START_X + self.BUTTON_WIDTH * i, 35 + 25 * depth)
			btn.SAFE_SetEvent(self.__OnClickRecorderButton, i)
			self.recorderButtons.append(btn)

		self.recorderButtons[0].SetText(localeinfo.VOICE_CHAT_MIC_OFF)
		self.recorderButtons[1].SetText(localeinfo.VOICE_CHAT_MIC_PUSH_TO_TALK)
		self.recorderButtons[1].SetToolTipText(localeinfo.VOICE_CHAT_MIC_PUSH_TO_TALK_INFO)
		self.recorderButtons[2].SetText(localeinfo.VOICE_CHAT_MIC_ALWAYS_ON)


		# Hearing config
		depth += 2
		self.texts.append(TextLine(self.board, localeinfo.VOICE_CHAT_HEAR, self.BOARD_WIDTH - 15, 35 + 25 * depth))
		for i in xrange(3):
			btn = ToggleButton(self.board, self.VOICE_TYPE_TEXT_DICT[i], self.BUTTON_START_X + self.BUTTON_WIDTH * i, 35 + 25 * depth)
			btn.SetToggleUpEvent(lambda arg=i, isUp=True: self.__OnTogglePlaybackHear(arg, isUp))
			btn.SetToggleDownEvent(lambda arg=i, isUp=False: self.__OnTogglePlaybackHear(arg, isUp))
			self.voiceHearButtons.append(btn)


		# Hearing volume
		depth += 2
		self.texts.append(TextLine(self.board, localeinfo.VOICE_CHAT_VOLUME, self.BOARD_WIDTH - 15, 35 + 25 * depth))
		self.volumeController = ui.SliderBar()
		self.volumeController.SetParent(self.board)
		self.volumeController.SetPosition(75, 35 + 25 * depth + 3)
		self.volumeController.SetEvent(ui.__mem_func__(self.__OnChangeVoicePlaybackVolume))
		self.volumeController.Show()


		# Speaking config
		depth += 2
		self.texts.append(TextLine(self.board, localeinfo.VOICE_CHAT_TALK_ON, self.BOARD_WIDTH - 15, 35 + 25 * depth))
		for i in xrange(3):
			btn = Button(self.board, self.VOICE_TYPE_TEXT_DICT[i], self.BUTTON_START_X + self.BUTTON_WIDTH * i, 35 + 25 * depth)
			btn.SAFE_SetEvent(self.__OnClickVoiceTypeButton, i)
			self.voiceTypeButtons.append(btn)


	def __OnClickRecorderButton(self, idx):
		for btn in self.recorderButtons:
			btn.SetUp()

		self.recorderButtons[idx].Down()
		app.VoiceChatSetRecorderState(idx)
		constinfo.SetVoiceChatConfig("VOICE_CHAT_MICROPHONE_STATE", idx)


	def __OnTogglePlaybackHear(self, idx, isUp):
		if isUp:
			self.voiceHearButtons[idx].SetUp()
		else:
			self.voiceHearButtons[idx].Down()
		net.SendChatPacket("/voice_chat_config {}".format(idx + 1))
		constinfo.SetVoiceChatConfig("VOICE_CHAT_HEAR_{}".format(self.INDEX_TO_CHAT_TYPE[idx]), int(not isUp))


	def __OnChangeVoicePlaybackVolume(self):
		pos = self.volumeController.GetSliderPos()
		app.VoiceChatSetVolume(pos)
		constinfo.SetVoiceChatVolume("VOICE_PLAYBACK_VOLUME", pos)


	def __OnClickVoiceTypeButton(self, idx, checkHearButtons = True):
		for btn in self.voiceTypeButtons:
			btn.SetUp()

		self.voiceTypeButtons[idx].Down()
		app.VoiceChatSetChatType(idx + 1)
		constinfo.SetVoiceChatConfig("VOICE_CHAT_TYPE", idx)

		# You can't talk if you can't hear it
		if checkHearButtons and not self.voiceHearButtons[idx].IsDown():
			self.voiceHearButtons[idx].Down()
			net.SendChatPacket("/voice_chat_config {}".format(idx + 1))


	def UpdateSizes(self):
		if self.volumes.IsShow():
			self.SetSize(self.BOARD_WIDTH, self.BOARD_HEIGHT + self.volumes.GetHeight())


	def OnReceiveConfig(self, config):
		self.currentConfig = config

		self.__OnClickRecorderButton(constinfo.GetVoiceChatConfig("VOICE_CHAT_MICROPHONE_STATE"))
		self.__OnClickVoiceTypeButton(constinfo.GetVoiceChatConfig("VOICE_CHAT_TYPE"), False)
		self.volumeController.SetSliderPos(constinfo.GetVoiceChatVolume("VOICE_PLAYBACK_VOLUME"))

		for btn in self.voiceHearButtons:
			btn.Down()

		isBlockLocal = (config & (1 << app.VOICE_CHAT_TYPE_LOCAL)) != 0
		isBlockParty = (config & (1 << app.VOICE_CHAT_TYPE_PARTY)) != 0
		isBlockGuild = (config & (1 << app.VOICE_CHAT_TYPE_GUILD)) != 0

		if isBlockLocal:
			self.voiceHearButtons[0].SetUp()
		if isBlockParty:
			self.voiceHearButtons[1].SetUp()
		if isBlockGuild:
			self.voiceHearButtons[2].SetUp()

		if not (isBlockLocal and isBlockGuild and isBlockParty):
			constinfo.SendVoiceChatVolumes()

	def OnMessage(self, name, vcType):
		# constinfo.SetVoiceChatVolume(name, constinfo.GetVoiceChatVolume(name))
		pass

	def OnPressEscapeKey(self):
		self.Hide()
		return True


	def ShowVoiceChatInfo(self):
		thinBoard = ui.ThinBoard()
		thinBoard.SetParent(self)
		thinBoard.SetPosition(self.infoImage.GetLocalPosition()[0]+220, self.infoImage.GetLocalPosition()[1]-40)
		thinBoard.SetSize(330, 160)
		thinBoard.Show()

		infoText = ui.MultiTextLine()
		infoText.SetParent(thinBoard)
		infoText.SetPosition(166, 10)
		infoText.SetTextType("horizontal#center")

		multi_text = ""
		multi_text+=localeinfo.VOICE_CHAT_TEXT1
		multi_text+= "\n\n"
		multi_text+=localeinfo.VOICE_CHAT_TEXT2
		multi_text+= "\n"
		multi_text+=localeinfo.VOICE_CHAT_TEXT3
		multi_text+= "\n"
		multi_text+=localeinfo.VOICE_CHAT_TEXT4
		multi_text+= "\n"
		multi_text+=localeinfo.VOICE_CHAT_TEXT5
		multi_text+= "\n"
		multi_text+=localeinfo.VOICE_CHAT_TEXT6
		multi_text+= "\n"
		multi_text+= "\n"
		multi_text+=localeinfo.VOICE_CHAT_TEXT7
		infoText.SetText(multi_text)


		infoText.Show()
		self.infoText = infoText


		infoText.Show()
		self.infoText = infoText


		self.infoHuntBoard = thinBoard

	def HideVoiceChatInfo(self):
		if getattr(self, "infoHuntBoard", None):
			self.infoHuntBoard.Hide()