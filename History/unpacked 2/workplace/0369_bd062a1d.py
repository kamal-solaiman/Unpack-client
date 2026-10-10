# coding: latin_1

import chr
import net
import player

import ui
import constinfo
import localeinfo
import item
import chat
import app
from _weakref import proxy

import systemSetting

IMG_DIR = "d:/ymir work/ui/game/renewal_pvp/"

pvp_data = {
	player.PVP_CRITICAL_DAMAGE_SKILLS : localeinfo.PVP_CRITICAL_DAMAGE_SKILLS,
	player.PVP_POISONING : localeinfo.PVP_POISONING,
	player.PVP_HALF_HUMAN : localeinfo.PVP_HALF_HUMAN,
	player.PVP_BUFFI_SKILLS : localeinfo.PVP_BUFFI_SKILLS,
	player.PVP_MISS_HITS : localeinfo.PVP_MISS_HITS,
	player.PVP_DISPEL_EFFECTS : localeinfo.PVP_DISPEL_EFFECTS,

	player.PVP_HP_ELIXIR : 72726,
	player.PVP_WHITE_DEW : 50826,
	player.PVP_YELLOW_DEW : 50823,
	player.PVP_ORANGE_DEW : 50822,
	player.PVP_RED_DEW : 50821,
	player.PVP_BLUE_DEW : 50825,
	player.PVP_GREEN_DEW : 50824,
	player.PVP_ZIN_WATER : 50817,
	player.PVP_SAMBO_WATER : 50818,
	player.PVP_ATTACKSPEED_FISH : 27868,
	player.PVP_DRAGON_GOD_ATTACK : 39018,
	player.PVP_DRAGON_GOD_DEFENCE : 39020,
	player.PVP_DRAGON_GOD_LIFE : 39017,
	player.PVP_PIERCING_STRIKE : 39025,
	player.PVP_CRITICAL_STRIKE : 39024,
	player.PVP_PET : 53009,
	player.PVP_NEW_PET : 55704,
	player.PVP_ENERGY : 51002,
}

class PvPWindow(ui.BoardWithTitleBar):
	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)
	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.children = {}
		self.Destroy()
		self.LoadWindow()
	def Destroy(self):
		if self.children.has_key("saveWindow"):
			self.children["saveWindow"].children = {}
			self.children["saveWindow"].Hide()
			self.children["saveWindow"] = None

		self.children = {}
		self.savedData = {}

	def LoadWindow(self):
		self.AddFlag("movable")
		self.AddFlag("attach")
		self.AddFlag("float")

		bg = ui.ImageBox()
		bg.SetParent(self)
		bg.AddFlag("attach")
		bg.LoadImage(IMG_DIR+"bg.tga")
		bg.SetPosition(14,30+6)
		bg.Show()
		self.children["bg"] = bg

		self.SetSize(28+bg.GetWidth(),31+18+bg.GetHeight())

		pvpIndex = 0
		yPos = 13
		for j in range(player.PVP_CRITICAL_DAMAGE_SKILLS, player.PVP_DISPEL_EFFECTS+1):
			pvpIndex += 1
			text = ui.TextLine()
			text.SetParent(bg)
			text.SetText(pvp_data[j])
			text.SetHorizontalAlignCenter()
			if ((pvpIndex%2) == 0):
				text.SetPosition(215, yPos)
			else:
				text.SetPosition(60, yPos)
			text.Show()
			self.children["text%d"%j] = text

			btn = ui.Button()
			btn.SetParent(bg)
			btn.SAFE_SetEvent(self.__ClickButton,j)
			if ((pvpIndex%2) == 0):
				btn.SetPosition(280,yPos)
				yPos+=30
			else:
				btn.SetPosition(130,yPos)
			btn.Show()
			self.children["btn%d"%j] = btn

		pvpIndex = 0
		xPos = 2
		yPos = 94
		for j in range(player.PVP_HP_ELIXIR, player.PVP_ENERGY+1):
			if player.PVP_ATTACKSPEED_FISH == j:
				yPos+=33
				pvpIndex = 0
				xPos = 2

			backBar = ui.ImageBox()
			backBar.SetParent(bg)
			backBar.LoadImage(IMG_DIR+"empty_bg_0.tga")
			backBar.SetPosition(xPos+(pvpIndex*33),yPos)
			backBar.SetStringEvent("mouse_over_in",self.__OnOverInPvP,j)
			backBar.SetStringEvent("mouse_over_out",self.__OnOverOutPvP,j)
			backBar.SetEvent(ui.__mem_func__(self.__ClickPvpItem), "mouse_click", j)
			backBar.Show()
			self.children["backBar%d"%j] = backBar

			item.SelectItem(pvp_data[j])

			pvpItem = ui.ImageBox()
			pvpItem.SetParent(bg)
			pvpItem.LoadImage(item.GetIconImageFileName())
			pvpItem.SetPosition(xPos+(pvpIndex*33),yPos)
			pvpItem.SetStringEvent("mouse_over_in",self.__OnOverInItemPvP,j, pvp_data[j])
			pvpItem.SetStringEvent("mouse_over_out",self.__OnOverOutItemPvP,j)
			pvpItem.SetEvent(ui.__mem_func__(self.__ClickPvpItem), "mouse_click", j)
			pvpItem.Show()
			self.children["pvpItem%d"%j] = pvpItem

			pvpItemCheck = ui.ImageBox()
			pvpItemCheck.SetParent(bg)
			pvpItemCheck.AddFlag("not_pick")
			pvpItemCheck.SetPosition(xPos+(pvpIndex*33)+19,yPos+18)
			pvpItemCheck.Show()
			self.children["pvpItemCheck%d"%j] = pvpItemCheck

			pvpIndex+=1

		pvpBetText = ui.TextLine()
		pvpBetText.SetParent(bg)
		pvpBetText.SetHorizontalAlignCenter()
		pvpBetText.SetPosition(37,176)
		pvpBetText.SetText(localeinfo.PVP_BET_TEXT)
		pvpBetText.Show()
		self.children["pvpBetText"] = pvpBetText

		pvpBet2 = ui.TextLine()
		pvpBet2.SetParent(bg)
		pvpBet2.SetPosition(92,175)
		if localeinfo.IsARABIC():
			pvpBet2.SetHorizontalAlignRight()
		else:
			pvpBet2.SetHorizontalAlignLeft()
		#pvpBet2.Show()
		self.children["pvpBet2"] = pvpBet2

		pvpBet = ui.EditLine()
		pvpBet.SetParent(bg)
		pvpBet.SetPosition(92,175)
		if localeinfo.IsARABIC():
			pvpBet.SetHorizontalAlignRight()
		pvpBet.SetSize(12,199)
		pvpBet.SetNumberMode()
		pvpBet.OnIMEUpdate = ui.__mem_func__(self.__UpdateBetValue)
		pvpBet.OnPressEscapeKey = ui.__mem_func__(self.Close)
		pvpBet.SetMax(15)
		pvpBet.Show()
		self.children["pvpBet"] = pvpBet

		saveBtn = ui.Button()
		saveBtn.SetParent(bg)
		saveBtn.SAFE_SetEvent(self.__ClickSaveBtn)
		saveBtn.SetUpVisual(IMG_DIR+"save_btn_0.tga")
		saveBtn.SetOverVisual(IMG_DIR+"save_btn_1.tga")
		saveBtn.SetDownVisual(IMG_DIR+"save_btn_2.tga")
		saveBtn.SetPosition(17,213)
		saveBtn.SetText(localeinfo.PVP_SAVE)
		saveBtn.Show()
		self.children["saveBtn"] = saveBtn

		cancelBtn = ui.Button()
		cancelBtn.SetParent(bg)
		cancelBtn.SAFE_SetEvent(self.__ClickCancelBtn)
		cancelBtn.SetUpVisual(IMG_DIR+"save_btn_0.tga")
		cancelBtn.SetOverVisual(IMG_DIR+"save_btn_1.tga")
		cancelBtn.SetDownVisual(IMG_DIR+"save_btn_2.tga")
		cancelBtn.SetPosition(199,247)
		cancelBtn.SetText(localeinfo.PVP_CANCEL)
		cancelBtn.Show()
		self.children["cancelBtn"] = cancelBtn

		okBtn = ui.Button()
		okBtn.SetParent(bg)
		okBtn.SAFE_SetEvent(self.__ClickOkBtn)
		okBtn.SetUpVisual(IMG_DIR+"ok_btn_0.tga")
		okBtn.SetOverVisual(IMG_DIR+"ok_btn_1.tga")
		okBtn.SetDownVisual(IMG_DIR+"ok_btn_2.tga")
		okBtn.SetPosition(17,244)
		okBtn.SetText(localeinfo.PVP_OK)
		okBtn.Show()
		self.children["okBtn"] = okBtn

		saveWindow = ui.BoardWithTitleBar()
		saveWindow.AddFlag("attach")
		saveWindow.AddFlag("float")
		saveWindow.AddFlag("movable")
		saveWindow.SetSize(200,88)
		saveWindow.SetTitleName(localeinfo.PVP_SAVE)
		saveWindow.SetCenterPosition()
		saveWindow.children = {}
		self.children["saveWindow"] = saveWindow

		saveNameSlot = ui.SlotBar()
		saveNameSlot.SetParent(saveWindow)
		saveNameSlot.SetSize(181,19)
		saveNameSlot.SetPosition(10,34)
		saveNameSlot.Show()
		saveWindow.children["saveNameSlot"] = saveNameSlot

		saveName = ui.EditLine()
		saveName.SetParent(saveNameSlot)
		saveName.SetPosition(3,3)
		if localeinfo.IsARABIC():
			saveName.SetHorizontalAlignRight()
		saveName.SetSize(177,15)
		saveName.OnPressEscapeKey = ui.__mem_func__(saveWindow.Hide)
		saveName.SetMax(15)
		saveName.Show()
		saveWindow.children["saveName"] = saveName

		saveBtnReal = ui.Button()
		saveBtnReal.SetParent(saveWindow)
		saveBtnReal.SAFE_SetEvent(self.__ClickSaveRealBtn)
		saveBtnReal.SetUpVisual(IMG_DIR+"saved_btn_0.tga")
		saveBtnReal.SetOverVisual(IMG_DIR+"saved_btn_1.tga")
		saveBtnReal.SetDownVisual(IMG_DIR+"saved_btn_2.tga")
		saveBtnReal.SetPosition(34,59)
		saveBtnReal.SetText(localeinfo.PVP_OK)
		saveBtnReal.Show()
		saveWindow.children["saveBtnReal"] = saveBtnReal

		cancelBtnReal = ui.Button()
		cancelBtnReal.SetParent(saveWindow)
		cancelBtnReal.SAFE_SetEvent(self.__ClickCancelRealBtn)
		cancelBtnReal.SetUpVisual(IMG_DIR+"saved_btn_0.tga")
		cancelBtnReal.SetOverVisual(IMG_DIR+"saved_btn_1.tga")
		cancelBtnReal.SetDownVisual(IMG_DIR+"saved_btn_2.tga")
		cancelBtnReal.SetPosition(105,59)
		cancelBtnReal.SetText(localeinfo.PVP_CANCEL)
		cancelBtnReal.Show()
		saveWindow.children["cancelBtnReal"] = cancelBtnReal

		self.SetCloseEvent(self.Close)

		savedData = ui.ComboBoxImage(bg,IMG_DIR+"select_image.tga",160,209)
		savedData.Show()
		self.children["savedData"] = savedData

		self.children["designMode"] = True

	def __SetPvPData(self, pvpIndex, pvpValue):
		self.savedData[self.children["currentData"]][pvpIndex] = pvpValue

	def __GetPvPData(self, pvpIndex):
		return self.savedData[self.children["currentData"]][pvpIndex]

	def OpenSecond(self, playerName, playerVID, data):
		self.__LoadSavedData()
		self.children["designMode"] = False
		self.children["playerName"] = playerName
		self.children["playerVID"] = int(chr.GetVIDByName(playerName))
		self.savedData[localeinfo.PVP_SAVED_OPTIONS] = data

		self.children["pvpBet2"].Show()
		self.children["saveBtn"].Hide()
		self.children["savedData"].Hide()
		self.children["savedData"].imagebox.Hide()
		self.children["pvpBet"].Hide()

		self.Open()

	def OpenFirst(self, playerName, playerVID):
		self.__LoadSavedData()
		self.children["playerName"] = playerName
		self.children["playerVID"] = int(playerVID)
		self.children["designMode"] = True

		if player.IsChallengeInstance(self.children["playerVID"]) or player.IsChallengeInstance(self.children["playerVID"]):
			packetText = "/pvp revenge %d"%self.children["playerVID"]
			net.SendChatPacket(packetText)
			return

		self.children["pvpBet2"].Hide()
		self.children["saveBtn"].Show()
		self.children["savedData"].Show()
		self.children["savedData"].imagebox.Show()
		self.children["pvpBet"].Show()

		self.Open()

	def Open(self):
		self.SetTitleName(localeinfo.PVP_TITLE % self.children["playerName"])
		self.__UpdatePvP()

		self.SetCenterPosition()
		self.Show()
		self.SetTop()

	def Close(self):
		packetText = "/pvp close %d"%self.children["playerVID"]
		net.SendChatPacket(packetText)
		self.Hide()

	def __ClickOkBtn(self):
		packetText = "/pvp pvp %d"%self.children["playerVID"]
		for j in xrange(player.PVP_MAX):
			packetText+= " "+str(int(self.__GetPvPData(j)))
		net.SendChatPacket(packetText)

		self.SaveData()
		self.Hide()

	def __ClickCancelBtn(self):
		self.SaveData()
		self.Close()

	def OnPressEscapeKey(self):
		self.SaveData()
		self.Close()
		return True

	def __ClickSaveBtn(self):
		self.children["saveWindow"].children["saveName"].SetText("")
		self.children["saveWindow"].children["saveName"].SetFocus()
		self.children["saveWindow"].Show()
		self.children["saveWindow"].SetTop()

	def __ClickCancelRealBtn(self):
		self.children["saveWindow"].Hide()

	def __ClickSaveRealBtn(self):
		if self.children.has_key("saveWindow"):
			text = self.children["saveWindow"].children["saveName"].GetText()
			if len(text) > 0:
				if text == " ":
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PVP_TEXT_EMPTY)
					return
				if self.savedData.has_key(text):
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PVP_SAME_NAME)
					return
				self.savedData[text] = self.savedData[self.children["currentData"]]
				#self.__SaveSavedData()
				self.__UpdateComboBox()
				self.__ClickSaveData(text)
			else:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PVP_TEXT_EMPTY)
			self.children["saveWindow"].Hide()

	def __ClickSaveData(self, key):
		if self.children["designMode"] == False:
			return

		self.children["currentData"] = key
		self.children["savedData"].SetCurrentItem(key)
		self.__UpdatePvP()

	def __ClickPvpItem(self, emptyArg, pvpIndex):
		if self.children["designMode"] == False:
			return

		newValue = not self.__GetPvPData(pvpIndex)
		self.__SetPvPData(pvpIndex, newValue)
		pvpBtn = self.children["pvpItemCheck%d"%pvpIndex]
		if newValue == True:
			pvpBtn.LoadImage(IMG_DIR+"check_1.tga")
		else:
			pvpBtn.LoadImage(IMG_DIR+"check_0.tga")

	def __ClickButton(self, pvpIndex):
		if self.children["designMode"] == False:
			return

		newValue = not self.__GetPvPData(pvpIndex)
		pvpBtn = self.children["btn%d"%pvpIndex]

		self.__SetPvPData(pvpIndex, newValue)
		if newValue == True:
			pvpBtn.SetUpVisual(IMG_DIR+"select_1.tga")
			pvpBtn.SetOverVisual(IMG_DIR+"select_1.tga")
			pvpBtn.SetDownVisual(IMG_DIR+"select_1.tga")
		else:
			pvpBtn.SetUpVisual(IMG_DIR+"select_0.tga")
			pvpBtn.SetOverVisual(IMG_DIR+"select_0.tga")
			pvpBtn.SetDownVisual(IMG_DIR+"select_0.tga")

	def __UpdatePvP(self):
		if self.children["designMode"]:
			self.children["pvpBet"].SetText(str(self.__GetPvPData(player.PVP_BET)))
		else:
			self.children["pvpBet2"].SetText(str(self.__GetPvPData(player.PVP_BET)))

		for j in range(player.PVP_HP_ELIXIR, player.PVP_ENERGY+1):
			if self.children.has_key("pvpItemCheck%d"%j):
				btn = self.children["pvpItemCheck%d"%j]
				if self.__GetPvPData(j) == True:
					btn.LoadImage(IMG_DIR+"check_1.tga")
				else:
					btn.LoadImage(IMG_DIR+"check_0.tga")

		for j in range(player.PVP_CRITICAL_DAMAGE_SKILLS, player.PVP_DISPEL_EFFECTS+1):
			if self.children.has_key("btn%d"%j):
				btn = self.children["btn%d"%j]
				if self.__GetPvPData(j) == True:
					btn.SetUpVisual(IMG_DIR+"select_1.tga")
					btn.SetOverVisual(IMG_DIR+"select_1.tga")
					btn.SetDownVisual(IMG_DIR+"select_1.tga")
				else:
					btn.SetUpVisual(IMG_DIR+"select_0.tga")
					btn.SetOverVisual(IMG_DIR+"select_0.tga")
					btn.SetDownVisual(IMG_DIR+"select_0.tga")
	
	def __UpdateComboBox(self):
		savedData = self.children["savedData"]
		savedData.ClearItem()
		savedData.InsertItem2(localeinfo.PVP_SAVED_OPTIONS, localeinfo.PVP_SAVED_OPTIONS)# always top!
		for key, data in self.savedData.items():
			if key == localeinfo.PVP_SAVED_OPTIONS:
				continue
			savedData.InsertItem2(key, key)
			savedData.SetEvent(lambda x, point=proxy(self): point.__ClickSaveData(x))
		savedData.SetCurrentItem(localeinfo.PVP_SAVED_OPTIONS)
		self.children["currentData"] = localeinfo.PVP_SAVED_OPTIONS

	def __UpdateBetValue(self):
		pvpBet = self.children["pvpBet"]
		ui.EditLine.OnIMEUpdate(pvpBet)
		if len(pvpBet.GetText()) > 0:
			self.__SetPvPData(player.PVP_BET, int(pvpBet.GetText()))
		else:
			self.__SetPvPData(player.PVP_BET, 0)

	def __OnOverOutPvP(self, pvpIndex):
		self.children["backBar%d"%pvpIndex].LoadImage(IMG_DIR+"empty_bg_0.tga")

	def __OnOverOutItemPvP(self, pvpIndex):
		self.__OnOverOutPvP(pvpIndex)

		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interface.tooltipItem.HideToolTip()

	def __OnOverInItemPvP(self, pvpIndex, itemVnum):
		self.__OnOverInPvP(pvpIndex)

		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.ClearToolTip()

			if pvpIndex == player.PVP_PET:
				interfaceHandler.tooltipItem.SetTitle(localeinfo.PVP_PET_TEXT)
				interfaceHandler.tooltipItem.ShowToolTip()
			elif pvpIndex == player.PVP_NEW_PET:
				interfaceHandler.tooltipItem.SetTitle(localeinfo.PVP_NEW_PET_TEXT)
				interfaceHandler.tooltipItem.ShowToolTip()
			else:
				item.SelectItem(itemVnum)
				interfaceHandler.tooltipItem.SetTitle(item.GetItemName())
				interfaceHandler.tooltipItem.ShowToolTip()

	def __OnOverInPvP(self, pvpIndex):
		self.children["backBar%d"%pvpIndex].LoadImage(IMG_DIR+"empty_bg_1.tga")

	def __SetDefaultData(self):
		data = {}
		for j in xrange(player.PVP_MAX):
			data[j] = True
		data[player.PVP_BET] = 0
		data[player.PVP_HALF_HUMAN] = False
		data[player.PVP_BUFFI_SKILLS] = False
		data[player.PVP_HP_ELIXIR] = False
		self.savedData[localeinfo.PVP_SAVED_OPTIONS] = data
		self.children["currentData"] = localeinfo.PVP_SAVED_OPTIONS
	
	def SaveData(self):
		try:
			file = open("UserData/%s.pvp"%player.GetName(),"w+")
			for key, items in self.savedData.items():
				if key == localeinfo.PVP_SAVED_OPTIONS:
					continue
				text = ""
				for i in xrange(player.PVP_MAX):
					text+="%d"%int(items[i])
					text+="#"
				text+=key
				file.write(text+"\n")
			file.close()
		except:
			pass

	def __LoadSavedData(self):
		self.savedData = {}
		self.__SetDefaultData()
		try:
			lines = open("UserData/%s.pvp"%player.GetName()).readlines()
			for line in lines:
				splitText = line.split("#")
				if len(splitText) == player.PVP_MAX+1:
					data = {}
					for j in xrange(player.PVP_MAX):
						if j == player.PVP_BET:
							data[j] = int(splitText[j])
						else:
							if splitText[j] == "1":
								data[j] = True
							else:
								data[j] = False
					self.savedData[str(splitText[len(splitText)-1])] = data
		except:
			pass
		self.__UpdateComboBox()
