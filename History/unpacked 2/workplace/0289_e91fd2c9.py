# coding: latin_1

import app
import net
import player

import ui
import mousemodule
import snd
import item
import chat
import grp
import uiscriptlocale
import uirefine
import uiattachmetin
import uicommon
import uiquicksell
import uiprivateshopbuilder
import localeinfo
import constinfo
import osfinfo
import ime
import wndMgr
import systemSetting

if app.ENABLE_LOCATION_SCROLL_REWORK:
	import locationscroll

if app.USE_OFFLINESHOP:
	import offlineshop
	import uiofflineshop_ae

if app.USE_ACCE_SYSTEM:
	import acce

if app.ITEM_CHECKINOUT_UPDATE:
	import exchange
if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget
if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

import shop

from _weakref import proxy

ITEM_MALL_BUTTON_ENABLE = True
ITEM_FLAG_APPLICABLE = 1 << 14
SOCKET_BLESS_ITEM_VNUM = 59951 # Blacksmith's Blessing (placeholder vnum - keep in sync with server SOCKET_BLESS_ITEM_VNUM)

ITEM_VNUM_ANTIDROP_CHARM = 70049

ENABLE_BELT_INVENTORY = 0

if app.ENABLE_EXTEND_INVEN_SYSTEM:
	EX_INVEN_COVER_IMG_OPEN = "d:/ymir work/ui/game/windows/ex_inven_cover_button_open.sub"
	EX_INVEN_COVER_IMG_CLOSE = "d:/ymir work/ui/game/windows/ex_inven_cover_button_close.sub"

def ReprGetItemIndex(window):
	return lambda pos : player.GetItemIndex(window, pos)

if app.__RENEWAL_BRAVE_CAPE__:
	class BraveCapeWindow(ui.ScriptWindow):
		isLoaded = 0
		tooltipItem = None
		__children = {}

		class SliderBarNew(ui.Window):
			def __init__(self):
				ui.Window.__init__(self)
				self.curPos = 1.0
				self.pageSize = 1.0
				self.eventChange = None
				self.__Load()

			def __Load(self):
				IMG_DIR = "d:/ymir work/ui/game/bravery_cape/"

				img = ui.ImageBox()
				img.SetParent(self)
				img.LoadImage(IMG_DIR + "slider_bg.tga")
				img.Show()
				self.backGroundImage = img

				self.SetSize(self.backGroundImage.GetWidth(), self.backGroundImage.GetHeight())

				cursor = ui.DragButton()
				cursor.AddFlag("movable")
				cursor.AddFlag("restrict_y")
				cursor.SetParent(self)
				cursor.SetMoveEvent(ui.__mem_func__(self.__OnMove))
				cursor.SetUpVisual(IMG_DIR + "drag.tga")
				cursor.SetOverVisual(IMG_DIR + "drag.tga")
				cursor.SetDownVisual(IMG_DIR + "drag.tga")
				cursor.Show()
				self.cursor = cursor

				self.cursor.SetRestrictMovementArea(0, 0, self.backGroundImage.GetWidth(), 0)
				self.pageSize = self.backGroundImage.GetWidth() - self.cursor.GetWidth()

			def __OnMove(self):
				(xLocal, yLocal) = self.cursor.GetLocalPosition()
				self.curPos = float(xLocal) / float(self.pageSize)
				if self.eventChange:
					self.eventChange()

			def SetSliderPos(self, pos):
				self.curPos = pos
				self.cursor.SetPosition(int(self.pageSize * pos), 0)

			def GetSliderPos(self):
				return self.curPos

			def SetEvent(self, event):
				self.eventChange = event

			def Enable(self):
				self.cursor.Show()

			def Disable(self):
				self.cursor.Hide()

		def __init__(self, wndInventory):
			if self.isLoaded == 1:
				return

			ui.ScriptWindow.__init__(self)

			self.wndInventory = proxy(wndInventory)

			self.layer = None
			self.bg = None
			self.expand = None
			self.minimize = None
			self.wndItem = None
			self.startBtn = None
			self.stopBtn = None
			self.origWidth = 0

			self.__children = {}

			self.__LoadWindow()

		def __del__(self):
			ui.ScriptWindow.__del__(self)

		def Destroy(self):
			try:
				self.SaveData()
			except:
				import dbg
				dbg.TraceError("bravery_cape: SaveData failed")

			self.wndItem.ClearSlot(0)

			delList = [\
						"timeTextVisual",
						"timeSlider",
						"timeBg",
						"timeText",
						#"rangeTextVisual",
						#"rangeSlider",
						#"rangeBg",
						#"rangeText",
			]

			for k, v in self.__children.items():
				if v in delList:
					del v
					v = None

			self.__children = {}

			self.wndInventory = None

			self.ClearDictionary()
			self.isLoaded = 0

		def CreateWindow(self, classPtr, parent, pos):
			window = classPtr
			window.SetParent(parent)
			window.SetPosition(*pos)
			window.Show()
			return window

		def __LoadWindow(self):
			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "uiscript/bravecapewindow.py")
			except:
				import exception
				exception.Abort("BraveCapeWindow.LoadWindow.LoadObject")

			try:
				self.layer = self.GetChild("layer")
				self.bg = self.GetChild("bg")
				self.expand = self.GetChild("expand")
				self.minimize = self.GetChild("minimize")
				self.wndItem = self.GetChild("item")
				self.startBtn = self.GetChild("start")
				self.stopBtn = self.GetChild("stop")
				self.origWidth = self.GetWidth()

				self.expand.SetEvent(ui.__mem_func__(self.__OpenInventory))
				self.minimize.SetEvent(ui.__mem_func__(self.__CloseInventory))

				self.wndItem.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
				self.wndItem.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
				self.wndItem.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
				self.wndItem.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
				self.wndItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
				self.wndItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
				self.wndItem.SetItemSlot(0, 20574, 0) #20570

				self.startBtn.SAFE_SetEvent(self._ClickStatusBtn, "ACTIVE")
				self.stopBtn.SAFE_SetEvent(self._ClickStatusBtn, "DEACTIVE")
			except:
				import exception
				exception.Abort("BraveCapeWindow.LoadWindow.BindObject")

			self.isLoaded = 1

			IMG_DIR = "d:/ymir work/ui/game/bravery_cape/"

			timeTextVisual = self.CreateWindow(ui.TextLine(), self.bg, (50 + 13 if localeinfo.IsARABIC() else 13, 60))
			timeTextVisual.SetText(localeinfo.BRAVERY_CAPE_SECOND)
			self.__children["timeTextVisual"] = timeTextVisual

			timeSlider = self.CreateWindow(self.SliderBarNew(), self.bg, (13, 73 + 5))
			timeSlider.SetEvent(ui.__mem_func__(self.OnChangeTimeSlider))
			self.__children["timeSlider"] = timeSlider

			timeBg = self.CreateWindow(ui.ImageBox(), self.bg, (77, 64))
			timeBg.LoadImage(IMG_DIR+"input_output.tga")
			self.__children["timeBg"] = timeBg

			timeText = self.CreateWindow(ui.TextLine(), timeBg, (0, 0))
			timeText.SetAllAlign()
			timeText.SetText("0")
			self.__children["timeText"] = timeText

			#rangeTextVisual = self.CreateWindow(ui.TextLine(), self.bg, (50 + 13 if localeinfo.IsARABIC() else 13, 73 + 22 + 17 + 5 - 18))
			#rangeTextVisual.SetText(localeinfo.BRAVERY_CAPE_RANGE)
			#self.__children["rangeTextVisual"] = rangeTextVisual

			#rangeSlider = self.CreateWindow(self.SliderBarNew(), self.bg, (13, 73 + 22 + 17 + 5))
			#rangeSlider.SetEvent(ui.__mem_func__(self.OnChangeRangeSlider))
			#self.__children["rangeSlider"] = rangeSlider

			#rangeBg = self.CreateWindow(ui.ImageBox(), self.bg, (77, 95 + 8))
			#rangeBg.LoadImage(IMG_DIR+"input_output.tga")
			#self.__children["rangeBg"] = rangeBg

			#rangeText = self.CreateWindow(ui.TextLine(), rangeBg, (0, 0))
			#rangeText.SetAllAlign()
			#rangeText.SetText("0")
			#self.__children["rangeText"] = rangeText

			self.__children["firstOpened"] = app.GetGlobalTimeStamp() + 5
			self.__children["second"] = 2
			#self.__children["range"] = 0
			self.__children["status"] = False

			self.stopBtn.Disable()
			self.stopBtn.Down()

			self.Refresh()

		def SaveData(self):
			myPath = "UserData\\bravery_cape"

			import os
			if not os.path.exists(myPath):
				if not os.path.exists("UserData"):
					os.mkdir("UserData")
				os.mkdir(myPath)

			filePath = myPath + "\\" + player.GetName() + ".data"
			old_open(filePath, "w").close()

			#myData = "{}#{}#{}\n".format(1 if (self.__children["status"] if self.__children.has_key("status") else False) == True else 0, self.__children["second"], self.__children["range"])
			myData = "{}#{}\n".format(1 if (self.__children["status"] if self.__children.has_key("status") else False) == True else 0, self.__children["second"])

			myFile = old_open(filePath, "wb")
			myFile.write(myData)
			myFile.close()
		
		def LoadData(self):
			myPath = "UserData\\bravery_cape"

			import os
			if not os.path.exists(myPath):
				return

			filePath = myPath + "\\" + player.GetName() + ".data"
			if os.path.isfile(filePath):
				myFile = old_open(filePath, "rb")
				myContent = myFile.read()
				myLines = myContent.split("#")

				if len(myLines) == 3:
					self.__children["status"] = True if int(myLines[0]) == 1 else False
					self.__children["second"] = int(myLines[1])
					#self.__children["range"] = int(myLines[2])
					self.Refresh()

					if self.__children["status"]:
						self._ClickStatusBtn("ACTIVE")

				myFile.close()

		def IsOpeningInventory(self):
			return self.layer.IsShow()

		def GetBasePosition(self):
			(x, y) = self.wndInventory.GetGlobalPosition() if self.wndInventory else (0, 0)
			return x - 146, y + 135
			#return x - 148, y + 20

		def AdjustPosition(self):
			bx, by = self.GetBasePosition()
			if self.IsOpeningInventory():
				self.SetPosition(bx, by);
				self.layer.SetPosition(self.origWidth - 5, 0)
			else:
				self.SetPosition(bx + 140, by);
				self.layer.SetPosition(self.origWidth - 10, 0)
				self.expand.SetPosition(self.origWidth + 1, 35);

		def __OpenInventory(self):
			self.layer.Show()
			self.expand.Hide()

			self.AdjustPosition()

		def __CloseInventory(self):
			self.layer.Hide()
			self.expand.Show()

			self.AdjustPosition()

		def SelectEmptySlot(self, iPos):
			if mousemodule.mouseController.isAttached():
				mousemodule.mouseController.DeattachObject()

		def SelectItemSlot(self, iPos):
			if mousemodule.mouseController.isAttached():
				mousemodule.mouseController.DeattachObject()

		def UseItemSlot(self, iPos):
			pass

		def OverOutItem(self):
			tooltipItem = self.wndInventory.tooltipItem if self.wndInventory else None
			if tooltipItem:
				tooltipItem.HideToolTip()

		def OverInItem(self, overSlotPos):
			tooltipItem = self.wndInventory.tooltipItem if self.wndInventory else None
			if tooltipItem:
				tooltipItem.SetItemToolTip(20574)#20570

		def Refresh(self):
			#(secondSlider, rangeSlider, posTime, posSlider) = (self.__children["second"], self.__children["range"], 0.0, 0.0)
			(secondSlider, posTime, posSlider) = (self.__children["second"], 0.0, 0.0)
			if secondSlider > 5800:
				secondSlider = 5800

			#if rangeSlider > 14000:
				#rangeSlider = 14000

			self.__children["timeText"].SetText(str((secondSlider/100)+2))
			#self.__children["rangeText"].SetText(str(rangeSlider + 1000))

			self.__children["timeSlider"].SetSliderPos((1.0 / 5800.0) * secondSlider)
			#self.__children["rangeSlider"].SetSliderPos((1.0 / 14000.0) * rangeSlider)

			self.__children["second"] = secondSlider
			#self.__children["range"] = rangeSlider

		def OnChangeRangeSlider(self):
			val = int(((1.0 / 14000.0) * (self.__children["rangeSlider"].GetSliderPos() * 14000)) * 14000)
			self.__children["range"] = val
			self.Refresh()

		def OnChangeTimeSlider(self):
			val = int(((1.0/6000.0)*(self.__children["timeSlider"].GetSliderPos()*6000))*6000)
			self.__children["second"] = 1 if val == 0 else val 
			self.Refresh()

		def SetStatus(self, status):
			self.__children["status"] = True if int(status) == 1 else False

			if self.__children["status"]:
				self.startBtn.Disable()
				self.startBtn.Down()
				self.stopBtn.Enable()
				self.stopBtn.SetUp()
			else:
				self.startBtn.Enable()
				self.startBtn.SetUp()
				self.stopBtn.Disable()
				self.stopBtn.Down()

			self.Refresh()

		def _ClickStatusBtn(self, event):
			if event == "ACTIVE":
				net.SendChatPacket("/brave_cape active {} 6000".format((self.__children["second"] / 100) + 2))
			elif event == "DEACTIVE":
				net.SendChatPacket("/brave_cape deactive")

		def Show(self, openMe = False):
			self.LoadData()

			if openMe:
				self.__OpenInventory()
			else:
				self.__CloseInventory()

			ui.ScriptWindow.Show(self)
			self.SetTop()

		def Close(self):
			self.Hide()

		def OnTop(self):
			if self.wndInventory:
				self.wndInventory.SetClickCapeWindow(True)
				self.wndInventory.SetTop()

class EquipmentTabWindow(ui.ScriptWindow):
	def __init__(self, wndInventory):
		ui.ScriptWindow.__init__(self)
		self.wndInventory = proxy(wndInventory)
		self.tabs = []
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.wndInventory = None
		self.tabs = []
		self.ClearDictionary()

	def __LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/equipmenttabwindow.py")
		except:
			import exception
			exception.Abort("EquipmentTabWindow.LoadWindow.LoadObject")

		try:
			for j in xrange(4):
				tab = self.GetChild("Equipment_Tab_" + str(j))
				tab.SAFE_SetEvent(self.__OnClickTab, j)
				self.tabs.append(tab)
		except:
			import exception
			exception.Abort("EquipmentTabWindow.LoadWindow.BindObject")

	def __OnClickTab(self, pageIdx):
		if self.wndInventory:
			self.wndInventory.SetEquipmentPage(pageIdx)

	def GetBasePosition(self):
		(x, y) = self.wndInventory.GetGlobalPosition() if self.wndInventory else (0, 0)
		return x - 30, y + 33

	def AdjustPosition(self):
		bx, by = self.GetBasePosition()
		self.SetPosition(bx, by)

	def UpdateTabState(self, pageIdx):
		for j, tab in enumerate(self.tabs):
			if j == pageIdx:
				tab.Down()
			else:
				tab.SetUp()

	def Show(self):
		ui.ScriptWindow.Show(self)
		self.AdjustPosition()

	def Close(self):
		self.Hide()

	def OnTop(self):
		if self.wndInventory:
			self.wndInventory.SetTop()

	def OnUpdate(self):
		self.AdjustPosition()

class CostumeWindow(ui.ScriptWindow):
	def __init__(self, wndInventory):
		import exception

		if not wndInventory:
			exception.Abort("wndInventory parameter must be set to InventoryWindow")
			return

		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_scale")
			self.SetAnimationPreset("modal")

		self.wndInventory = proxy(wndInventory);

		self.isLoaded = 0

		if app.ENABLE_HIDE_COSTUME_SYSTEM:
			self.visibleBtnList = []
			self.visibleSlotList = []

		if app.ENABLE_HIDE_SHINING_SYSTEM:
			self.visibleShiningBtnList = []
			self.visibleShiningSlotList = []

		self.__LoadWindow()

	def Destroy(self):
		self.wndInventory = None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()
		self.RefreshCostumeSlot()

		if app.ENABLE_HIDE_SHINING_SYSTEM:
			self.RefreshVisibleShining()

		ui.ScriptWindow.Show(self)

	def Close(self):
		self.Hide()

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			if localeinfo.IsARABIC():
				pyScrLoader.LoadScriptFile(self, "uiscript/ae_CostumeWindow.py")
			else:
				pyScrLoader.LoadScriptFile(self, "uiscript/CostumeWindow.py")
		except:
			import exception
			exception.Abort("CostumeWindow.LoadWindow.LoadObject")

		try:
			wndEquip = self.GetChild("CostumeSlot")
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))

			if app.ENABLE_HIDE_COSTUME_SYSTEM:
				self.visibleBtnList.append(self.GetChild("BodyToolTipButton")) ## 0
				self.visibleBtnList.append(self.GetChild("HairToolTipButton")) ## 1
				self.visibleBtnList.append(self.GetChild("AcceToolTipButton")) ## 2
				self.visibleBtnList.append(self.GetChild("WeaponToolTipButton")) ## 3
				self.visibleBtnList.append(self.GetChild("AuraToolTipButton")) ## 4

				self.visibleSlotList.append(self.GetChild("VisibleBodySlotImg")) ## 0
				self.visibleSlotList.append(self.GetChild("VisibleHairSlotImg")) ## 1
				self.visibleSlotList.append(self.GetChild("VisibleAcceSlotImg")) ## 2
				self.visibleSlotList.append(self.GetChild("VisibleWeaponSlotImg")) ## 3
				self.visibleSlotList.append(self.GetChild("VisibleAuraSlotImg")) ## 4


			if app.ENABLE_HIDE_SHINING_SYSTEM:
				self.visibleShiningBtnList.append(self.GetChild("ShiningWeaponToolTipButton")) ## 0
				self.visibleShiningBtnList.append(self.GetChild("ShiningArmorToolTipButton"))  ## 1
				self.visibleShiningBtnList.append(self.GetChild("ShiningSpecialToolTipButton")) ## 2

				self.visibleShiningSlotList.append(self.GetChild("VisibleShiningWeaponSlotImg")) ## 0
				self.visibleShiningSlotList.append(self.GetChild("VisibleShiningArmorSlotImg"))  ## 1
				self.visibleShiningSlotList.append(self.GetChild("VisibleShiningSpecialSlotImg")) ## 2

			if app.USE_MOUNT_SKIN:
				self.visibleBtnList.append(self.GetChild("MountSkinToolTipButton")) ## 5
				self.visibleSlotList.append(self.GetChild("VisibleMountSkinSlotImg")) ## 5

			if app.USE_PET_SKIN:
				self.visibleBtnList.append(self.GetChild("PetSkinToolTipButton")) ## 6
				self.visibleSlotList.append(self.GetChild("VisiblePetSkinSlotImg")) ## 6
		except:
			import exception
			exception.Abort("CostumeWindow.LoadWindow.BindObject")

		## Equipment
		wndEquip.SetOverInItemEvent(ui.__mem_func__(self.wndInventory.OverInItem))
		wndEquip.SetOverOutItemEvent(ui.__mem_func__(self.wndInventory.OverOutItem))
		wndEquip.SetUnselectItemSlotEvent(ui.__mem_func__(self.wndInventory.UseItemSlot))
		wndEquip.SetUseSlotEvent(ui.__mem_func__(self.wndInventory.UseItemSlot))
		wndEquip.SetSelectEmptySlotEvent(ui.__mem_func__(self.wndInventory.SelectEmptySlot))
		wndEquip.SetSelectItemSlotEvent(ui.__mem_func__(self.wndInventory.SelectItemSlot))

		self.wndEquip = wndEquip

		if app.ENABLE_HIDE_COSTUME_SYSTEM:
			self.visibleBtnList[0].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 1, 0)
			self.visibleBtnList[0].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 1, 1)

			self.visibleBtnList[1].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 2, 0)
			self.visibleBtnList[1].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 2, 1)

			if app.USE_ACCE_SYSTEM:
				self.visibleBtnList[2].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 3, 0)
				self.visibleBtnList[2].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 3, 1)

			if app.USE_WEAPON_COSTUME_SYSTEM:
				self.visibleBtnList[3].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 4, 0)
				self.visibleBtnList[3].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 4, 1)
			self.visibleBtnList[4].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 5, 0)
			self.visibleBtnList[4].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 5, 1)

			if app.USE_MOUNT_SKIN:
				self.visibleBtnList[5].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 6, 0)
				self.visibleBtnList[5].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 6, 1)

			if app.USE_PET_SKIN:
				self.visibleBtnList[6].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 7, 0)
				self.visibleBtnList[6].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 7, 1)

			for slot in xrange(len(self.visibleSlotList)):
				self.visibleSlotList[slot].Hide()

		if app.ENABLE_HIDE_SHINING_SYSTEM:
			self.visibleShiningBtnList[0].SetToggleUpEvent(ui.__mem_func__(self.VisibleShining), 1, 0)
			self.visibleShiningBtnList[0].SetToggleDownEvent(ui.__mem_func__(self.VisibleShining), 1, 1)

			self.visibleShiningBtnList[1].SetToggleUpEvent(ui.__mem_func__(self.VisibleShining), 2, 0)
			self.visibleShiningBtnList[1].SetToggleDownEvent(ui.__mem_func__(self.VisibleShining), 2, 1)

			self.visibleShiningBtnList[2].SetToggleUpEvent(ui.__mem_func__(self.VisibleShining), 3, 0)
			self.visibleShiningBtnList[2].SetToggleDownEvent(ui.__mem_func__(self.VisibleShining), 3, 1)

			for slot in xrange(3):
				self.visibleShiningSlotList[slot].Hide()

	def RefreshCostumeSlot(self):
		getItemVNum = player.GetItemIndex
		
		v_slot = [item.COSTUME_SLOT_WEAPON, item.COSTUME_SLOT_START,\
				item.COSTUME_SLOT_START+1, item.COSTUME_SLOT_START+2,\
				item.COSTUME_SLOT_START+3, item.EQUIPMENT_AURA,\
				item.WEAR_EX_THIEF_SLOT, item.WEAR_EX_RING_SLOT,\
				item.SHINING_SLOT_START+0, item.SHINING_SLOT_START+1 , item.SHINING_SLOT_START+2,item.PENDANT_YOHARA_SLOT,item.COSTUME_MOUNT_SKIN,item.COSTUME_PET_SKIN,\
				#item.SHINING_SLOT_START+3, item.SHINING_SLOT_START+4 , item.SHINING_SLOT_START+5,
				item.EQUIPMENT_UNIQUE1, item.EQUIPMENT_UNIQUE2,item.EQUIPMENT_RING1, item.EQUIPMENT_RING2]
		
		for slotNumber in v_slot:
			self.wndEquip.SetItemSlot(slotNumber, getItemVNum(slotNumber), 0)
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if not player.GetChangeLookVnum(player.EQUIPMENT, slotNumber) == 0:
					self.wndEquip.SetSlotCoverImage(slotNumber, "icon/item/ingame_convert_Mark.tga")
				else:
					self.wndEquip.EnableSlotCoverImage(slotNumber, False)

		self.wndEquip.RefreshSlot()


	# def RefreshCostumeSlot(self):
		# getItemVNum = player.GetItemIndex

		# for i in xrange(item.COSTUME_SLOT_COUNT):
			# slotNumber = item.COSTUME_SLOT_START + i
			# self.wndEquip.SetItemSlot(slotNumber, getItemVNum(slotNumber), 0)

			# if app.ENABLE_CHANGE_LOOK_SYSTEM:
				# if not player.GetChangeLookVnum(player.EQUIPMENT, slotNumber) == 0:
					# self.wndEquip.SetSlotCoverImage(slotNumber, "icon/item/ingame_convert_Mark.tga")
				# else:
					# self.wndEquip.EnableSlotCoverImage(slotNumber, False)

		# if app.USE_WEAPON_COSTUME_SYSTEM:
			# self.wndEquip.SetItemSlot(item.COSTUME_SLOT_WEAPON, getItemVNum(item.COSTUME_SLOT_WEAPON), 0)

			# if app.ENABLE_CHANGE_LOOK_SYSTEM:
				# if not player.GetChangeLookVnum(player.EQUIPMENT, item.COSTUME_SLOT_WEAPON) == 0:
					# self.wndEquip.SetSlotCoverImage(item.COSTUME_SLOT_WEAPON, "icon/item/ingame_convert_Mark.tga")
				# else:
					# self.wndEquip.EnableSlotCoverImage(item.COSTUME_SLOT_WEAPON, False)

		# self.wndEquip.RefreshSlot()

	if app.ENABLE_HIDE_COSTUME_SYSTEM:
		def RefreshVisibleCostume(self):
			body = osfinfo.HIDDEN_BODY_COSTUME
			self.SetHideEvent(0, body)

			hair = osfinfo.HIDDEN_HAIR_COSTUME
			self.SetHideEvent(1, hair)

			if app.USE_ACCE_SYSTEM:
				acce = osfinfo.HIDDEN_ACCE_COSTUME
				self.SetHideEvent(2, acce)

			if app.USE_WEAPON_COSTUME_SYSTEM:
				weapon = osfinfo.HIDDEN_WEAPON_COSTUME
				self.SetHideEvent(3, weapon)

			aura = osfinfo.HIDDEN_AURA_COSTUME
			self.SetHideEvent(4, aura)

			if app.USE_MOUNT_SKIN:
				self.SetHideEvent(5, osfinfo.HIDDEN_MOUNT_SKIN)

			if app.USE_PET_SKIN:
				self.SetHideEvent(6, osfinfo.HIDDEN_PET_SKIN)

		def SetHideEvent(self, slot, hide = False):
			if hide:
				self.visibleBtnList[slot].SetToolTipText(localeinfo.SHOW_COSTUME)
				self.visibleBtnList[slot].SetUpVisual("d:/ymir work/ui/game/costume/eye_closed_01.tga")
				self.visibleBtnList[slot].SetOverVisual("d:/ymir work/ui/game/costume/eye_closed_02.tga")
				self.visibleBtnList[slot].SetDownVisual("d:/ymir work/ui/game/costume/eye_closed_02.tga")
				self.visibleSlotList[slot].Show()
			else:
				self.visibleBtnList[slot].SetToolTipText(localeinfo.HIDE_COSTUME)
				self.visibleBtnList[slot].SetUpVisual("d:/ymir work/ui/game/btn_hide_01.png")
				self.visibleBtnList[slot].SetOverVisual("d:/ymir work/ui/game/btn_hide_02.png")
				self.visibleBtnList[slot].SetDownVisual("d:/ymir work/ui/game/btn_hide_03.png")
				self.visibleSlotList[slot].Hide()

		def VisibleCostume(self, part, hidden):
			net.SendChatPacket("/hide_costume %d %d" % (part, hidden))

	if app.ENABLE_HIDE_SHINING_SYSTEM:
		def RefreshVisibleShining(self):
			weapon = osfinfo.HIDDEN_SHINING_WEAPON
			self.SetShiningHideEvent(0, weapon)

			armor = osfinfo.HIDDEN_SHINING_ARMOR
			self.SetShiningHideEvent(1, armor)

			special = osfinfo.HIDDEN_SHINING_SPECIAL
			self.SetShiningHideEvent(2, special)

		def SetShiningHideEvent(self, slot, hide = False):
			if hide:
				self.visibleShiningBtnList[slot].SetToolTipText(localeinfo.SHOW_COSTUME)
				self.visibleShiningBtnList[slot].SetUpVisual("d:/ymir work/ui/game/costume/eye_closed_01.tga")
				self.visibleShiningBtnList[slot].SetOverVisual("d:/ymir work/ui/game/costume/eye_closed_02.tga")
				self.visibleShiningBtnList[slot].SetDownVisual("d:/ymir work/ui/game/costume/eye_closed_02.tga")
				self.visibleShiningSlotList[slot].Show()
			else:
				self.visibleShiningBtnList[slot].SetToolTipText(localeinfo.HIDE_COSTUME)
				self.visibleShiningBtnList[slot].SetUpVisual("d:/ymir work/ui/game/btn_hide_01.png")
				self.visibleShiningBtnList[slot].SetOverVisual("d:/ymir work/ui/game/btn_hide_02.png")
				self.visibleShiningBtnList[slot].SetDownVisual("d:/ymir work/ui/game/btn_hide_03.png")
				self.visibleShiningSlotList[slot].Hide()

		def VisibleShining(self, part, hidden):
			net.SendChatPacket("/hide_shining %d %d" % (part, hidden))

if ENABLE_BELT_INVENTORY:
	class BeltInventoryWindow(ui.ScriptWindow):
		def __init__(self, wndInventory):
			import exception

			if not wndInventory:
				exception.Abort("wndInventory parameter must be set to InventoryWindow")
				return

			ui.ScriptWindow.__init__(self)

			if app.ENABLE_WINDOW_SLIDE_EFFECT:
				self.AddFlag("animated_scale")
				self.SetAnimationPreset("modal")

			self.wndInventory = proxy(wndInventory)

			self.isLoaded = 0

			self.wndBeltInventoryLayer = None
			self.wndBeltInventorySlot = None
			self.expandBtn = None
			self.minBtn = None

			self.__LoadWindow()

		def Destroy(self):
			self.wndInventory = None

		def __del__(self):
			ui.ScriptWindow.__del__(self)

		def Show(self, openBeltSlot = False):
			self.__LoadWindow()
			self.RefreshSlot()

			ui.ScriptWindow.Show(self)

			if openBeltSlot:
				self.OpenInventory()
			else:
				self.CloseInventory()

			self.SetTop()

		def Close(self):
			self.Hide()

		def IsOpeningInventory(self):
			return self.wndBeltInventoryLayer.IsShow()

		def OpenInventory(self):
			self.wndBeltInventoryLayer.Show()
			self.expandBtn.Hide()

			if localeinfo.IsARABIC() == 0:
				self.AdjustPositionAndSize()
			else:
				self.AdjustPositionAndSizeAE()

		def CloseInventory(self):
			self.wndBeltInventoryLayer.Hide()
			self.expandBtn.Show()

			if localeinfo.IsARABIC() == 0:
				self.AdjustPositionAndSize()
			else:
				self.AdjustPositionAndSizeAE()

		if app.ENABLE_BIOLOG_SYSTEM:
			def GetBasePosition(self):
				x, y = self.wndInventory.GetGlobalPosition()
				return x - 148, y + 93
		else:
			def GetBasePosition(self):
				x, y = self.wndInventory.GetGlobalPosition()
				return x - 148, y

		if localeinfo.IsARABIC():
			def AdjustPositionAndSizeAE(self):
				bx, by = self.GetBasePosition()

				if self.IsOpeningInventory():
					self.SetPosition(bx, by);
					self.wndBeltInventoryLayer.SetPosition(self.ORIGINAL_WIDTH-5, 0)
				else:
					self.SetPosition(bx + 140, by);
					self.wndBeltInventoryLayer.SetPosition(self.ORIGINAL_WIDTH - 10, 0)
					self.expandBtn.SetPosition(self.ORIGINAL_WIDTH + 1, 15);

		def AdjustPositionAndSize(self):
			if localeinfo.IsARABIC():
				self.AdjustPositionAndSizeAE()
				return
			
			bx, by = self.GetBasePosition()

			if self.IsOpeningInventory():
				self.SetPosition(bx, by)
				self.SetSize(self.ORIGINAL_WIDTH, self.GetHeight())
			else:
				self.SetPosition(bx + 138, by);
				self.SetSize(10, self.GetHeight())

		def __LoadWindow(self):
			if self.isLoaded == 1:
				return

			self.isLoaded = 1

			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "UIScript/BeltInventoryWindow.py")
			except:
				import exception
				exception.Abort("CostumeWindow.LoadWindow.LoadObject")

			try:
				self.ORIGINAL_WIDTH = self.GetWidth()
				wndBeltInventorySlot = self.GetChild("BeltInventorySlot")
				self.wndBeltInventoryLayer = self.GetChild("BeltInventoryLayer")
				self.expandBtn = self.GetChild("ExpandBtn")
				self.minBtn = self.GetChild("MinimizeBtn")

				self.expandBtn.SetEvent(ui.__mem_func__(self.OpenInventory))
				self.minBtn.SetEvent(ui.__mem_func__(self.CloseInventory))

				if localeinfo.IsARABIC():
					self.minBtn.SetPosition(self.minBtn.GetWidth() + 3, 15)

				for i in xrange(item.BELT_INVENTORY_SLOT_COUNT):
					slotNumber = item.BELT_INVENTORY_SLOT_START + i
					wndBeltInventorySlot.SetCoverButton(slotNumber,
						"d:/ymir work/ui/game/quest/slot_button_01.sub",\
						"d:/ymir work/ui/game/quest/slot_button_01.sub",\
						"d:/ymir work/ui/game/quest/slot_button_01.sub",\
						"d:/ymir work/ui/game/belt_inventory/slot_disabled.tga", False, False)

			except:
				import exception
				exception.Abort("CostumeWindow.LoadWindow.BindObject")

			## Equipment
			wndBeltInventorySlot.SetOverInItemEvent(ui.__mem_func__(self.wndInventory.OverInItem))
			wndBeltInventorySlot.SetOverOutItemEvent(ui.__mem_func__(self.wndInventory.OverOutItem))
			wndBeltInventorySlot.SetUnselectItemSlotEvent(ui.__mem_func__(self.wndInventory.UseItemSlot))
			wndBeltInventorySlot.SetUseSlotEvent(ui.__mem_func__(self.wndInventory.UseItemSlot))
			wndBeltInventorySlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.wndInventory.SelectEmptySlot))
			wndBeltInventorySlot.SetSelectItemSlotEvent(ui.__mem_func__(self.wndInventory.SelectItemSlot))

			## MT-436 slot bug fix
			#wndBeltInventorySlot.SetSlotType(player.SLOT_TYPE_BELT_INVENTORY)
			self.wndBeltInventorySlot = wndBeltInventorySlot

		def RefreshSlot(self):
			getItemVNum = player.GetItemIndex

			for i in xrange(item.BELT_INVENTORY_SLOT_COUNT):
				slotNumber = item.BELT_INVENTORY_SLOT_START + i
				self.wndBeltInventorySlot.SetItemSlot(slotNumber, getItemVNum(slotNumber), player.GetItemCount(slotNumber))
				self.wndBeltInventorySlot.SetAlwaysRenderCoverButton(slotNumber, True)

				avail = "0"

				if player.IsAvailableBeltInventoryCell(slotNumber):
					self.wndBeltInventorySlot.EnableCoverButton(slotNumber)
				else:
					self.wndBeltInventorySlot.DisableCoverButton(slotNumber)

			self.wndBeltInventorySlot.RefreshSlot()

		def OnTop(self):
			if self.wndInventory:
				self.wndInventory.SetClickBeltInventory(True)
				self.wndInventory.SetTop()

class BoxMenu(ui.ScriptWindow):
	MAX_BUTTONS = 2

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_scale")
			self.SetAnimationPreset("modal")

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/box_menu.py")
		except:
			import exception
			exception.Abort("BoxMenu.LoadWindow.LoadObject")

		self.buttons = []
		for i in xrange(self.MAX_BUTTONS):
			self.buttons.append(self.GetChild("btn%d" % (i + 1)))
			self.buttons[i].SetEvent(ui.__mem_func__(self.OnClickButton), i)

		self.GetChild("board").SetCloseEvent(ui.__mem_func__(self.Close))

	def Destroy(self):
		self.ClearDictionary()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Open(self):
		ui.ScriptWindow.Show(self)

	def Close(self):
		ui.ScriptWindow.Hide(self)

	def OnClickButton(self, arg):
		if arg == 0:
			net.SendChatPacket("/click_mall")
		elif arg == 1:
			net.SendChatPacket("/click_safebox")
		
		self.Close()

	def OnPressEscapeKey(self):
		self.Close()
		return True

class InventoryWindow(ui.ScriptWindow):
	USE_TYPE_TUPLE = (
		"USE_CLEAN_SOCKET",
		"USE_CHANGE_ATTRIBUTE",
		"USE_ADD_ATTRIBUTE",
		"USE_ADD_ATTRIBUTE2",
		"USE_ADD_ACCESSORY_SOCKET",
		"USE_PUT_INTO_ACCESSORY_SOCKET",
		"USE_PUT_INTO_BELT_SOCKET",
		"USE_PUT_INTO_RING_SOCKET",
		"USE_CHANGE_COSTUME_ATTR",
		"USE_RESET_COSTUME_ATTR",
		"USE_REMOVE_ENCHANT"
	)
	
	if app.ENABLE_COSTUME_EXTENDED_RECHARGE:
		USE_TYPE_LIST = list(USE_TYPE_TUPLE)
		USE_TYPE_LIST.append("USE_TIME_CHARGE_PER")
		USE_TYPE_LIST.append("USE_TIME_CHARGE_FIX")
		USE_TYPE_TUPLE = tuple(USE_TYPE_LIST)
	
	if app.USE_AURA_SYSTEM and not app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
		USE_TYPE_TUPLE += ("USE_PUT_INTO_AURA_SOCKET",
							"USE_REMOVE_AURA_ATTR",)
	
	if app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM:
		USE_TYPE_TUPLE += ("USE_SET_CUSTOM_ATTRIBUTE",)
	
	if app.USE_ENCHANT_COSTUMES:
		USE_TYPE_TUPLE += (\
							"USE_ENCHANT_BODY_COSTUME",
							"USE_ENCHANT_HAIR_COSTUME",
							"USE_ENCHANT_WEAPON_COSTUME",
							"USE_ENCHANT_MOUNT_SKIN",
							"USE_ENCHANT_PET_SKIN",
							"USE_REMOVE_COSTUME_ENCHANT",)

	if app.ENABLE_ATTR_6TH_7TH:
		USE_TYPE_TUPLE += ("USE_CHANGE_ATTRIBUTE2",)


	questionDialog = None
	tooltipItem = None
	lastGold = None

	if app.ENABLE_BIOLOG_SYSTEM:
		wndCollect = None

	sellingSlotNumber = -1
	quickTransferGreenSlot = -1
	quickTransferRedSlot = -1
	isLoaded = 0
	isOpenedCostumeWindowWhenClosingInventory = 0
	isOpenedBeltWindowWhenClosingInventory = 0
	isOpenedCollectWindowWhenClosingInventory = 0
	if app.ENABLE_GROWTH_PET_SYSTEM:
		petHatchingWindow	= None
		petFeedWindow		= None
		petNameChangeWindow = None

	interface = None

	# if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
		# SPECIAL_BUTTONS_COUNT = 4

	if app.__RENEWAL_BRAVE_CAPE__:
		isOpenedBraveCapeWindowWhenClosingInventory = 0
		IsClickBraveCapeWindow = False

	wndEquipmentTab = None

	if app.ENABLE_INGAME_WIKI:
		wndWiki = None

	if app.ENABLE_SORT_INVENTORY or app.USE_STACK_INVENTORY:
		organizeDlg = None

		def __CloseOrganizeDlg(self):
			if self.organizeDlg:
				self.organizeDlg.Close()

		def __SortOrganizeDlg(self):
			net.SendChatPacket("/sort_inventory")
			snd.PlaySound("sound/ui/pickup_item_in_inventory.wav")

			self.__CloseOrganizeDlg()

		def __StackOrganizeDlg(self):
			net.SendChatPacket("/stack_items")
			snd.PlaySound("sound/ui/pickup_item_in_inventory.wav")

			self.__CloseOrganizeDlg()

		def __OrganizeInventory(self):
			if not self.organizeDlg:
				tmp = uicommon.OrganizeItemsDialog()
				tmp.SetCancelEvent(ui.__mem_func__(self.__CloseOrganizeDlg))
				tmp.SetCloserEvent(ui.__mem_func__(self.__CloseOrganizeDlg))
				
				if app.ENABLE_SORT_INVENTORY:
					tmp.SetSortEvent(ui.__mem_func__(self.__SortOrganizeDlg))

				if app.USE_STACK_INVENTORY:
					tmp.SetStackEvent(ui.__mem_func__(self.__StackOrganizeDlg))

				self.organizeDlg = tmp

			if not self.organizeDlg:
				return

			self.organizeDlg.SetOnPotion(False)
			self.organizeDlg.Open()

	def __init__(self):
		if app.__RENEWAL_BRAVE_CAPE__:
			self.wndBraveCape = None

		self.wndCostume = None
		self.wndBelt = None
		self.boxMenuWindow = None

		self.pick_item_dialog = None
		self.tooltipItem = None
		self.wndItem = None

		if app.ENABLE_LOCATION_SCROLL_REWORK:
			self.locScrollCountDialog = None
			self.locScrollRenameDialog = None
			self.locScrollClearDialog = None
			self.locScrollRenamePos = (0, 0)
			self.locScrollClearPos = (0, 0)
			self.locScrollClearSlot = 0

		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_scale")
			self.SetAnimationPreset("modal")

		# if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			# osfinfo.isExtraWindowWhenClosingInventory = 0

		self.isOpenedBeltWindowWhenClosingInventory = 0

		if app.ENABLE_HIDE_COSTUME_SYSTEM:
			self.visibleBtnList = []
			self.visibleSlotList = []

		if app.ENABLE_HIDE_SHINING_SYSTEM:
			self.visibleShiningBtnList = []
			self.visibleShiningSlotList = []

		self.__LoadWindow()
		self.IsClickBeltInventory = False

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def SetClickBeltInventory(self, isclick):
		self.IsClickBeltInventory = isclick

	def Show(self):
		self.__LoadWindow()
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "inventory_window")
		ui.ScriptWindow.Show(self)

		# if app.ENABLE_SPECIAL_INVENTORY_SYSTEM and osfinfo.isExtraWindowWhenClosingInventory:
			# interfaceHandler = systemSetting.GetInterfaceHandler()
			# if interfaceHandler and interfaceHandler.wndSpecialInventory:
				# interfaceHandler.wndSpecialInventory.JustOpen()

		self.RefreshItemSlot()

		if self.isOpenedCostumeWindowWhenClosingInventory and self.wndCostume:
			self.wndCostume.Show()

		if self.wndBelt:
			self.wndBelt.Show(self.isOpenedBeltWindowWhenClosingInventory)

		if app.__RENEWAL_BRAVE_CAPE__ and self.wndBraveCape:
			self.wndBraveCape.Show(self.isOpenedBraveCapeWindowWhenClosingInventory)

		if self.wndEquipmentTab:
			self.wndEquipmentTab.Show()
			self.wndEquipmentTab.AdjustPosition()

		if app.ENABLE_BIOLOG_SYSTEM:
			if self.wndCollect:
				self.wndCollect.Show(self.isOpenedCollectWindowWhenClosingInventory)

	def BindInterfaceClass(self, interface):
		self.interface = proxy(interface)

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()

			if localeinfo.IsARABIC():
				pyScrLoader.LoadScriptFile(self, "uiscript/ae_inventorywindow.py")
			else:
				pyScrLoader.LoadScriptFile(self, "uiscript/inventorywindow.py")
		except:
			import exception
			exception.Abort("InventoryWindow.LoadWindow.LoadObject")

		try:
			wndItem = self.GetChild("ItemSlot")
			#wndEquip = self.GetChild("EquipmentSlot")
			if app.ENABLE_HIDE_COSTUME_SYSTEM:
				self.visibleBtnList.append(self.GetChild("BodyToolTipButton")) ## 0
				self.visibleBtnList.append(self.GetChild("HairToolTipButton")) ## 1
				self.visibleBtnList.append(self.GetChild("AcceToolTipButton")) ## 2
				self.visibleBtnList.append(self.GetChild("WeaponToolTipButton")) ## 3
				self.visibleBtnList.append(self.GetChild("AuraToolTipButton")) ## 4
				# self.GetChild("BodyToolTipButton").Hide()
				# self.GetChild("HairToolTipButton").Hide()
				# self.GetChild("WeaponToolTipButton").Hide()
				# self.GetChild("AuraToolTipButton").Hide()
				
				self.visibleSlotList.append(self.GetChild("VisibleBodySlotImg")) ## 0
				self.visibleSlotList.append(self.GetChild("VisibleHairSlotImg")) ## 1
				self.visibleSlotList.append(self.GetChild("VisibleAcceSlotImg")) ## 2
				self.visibleSlotList.append(self.GetChild("VisibleWeaponSlotImg")) ## 3
				self.visibleSlotList.append(self.GetChild("VisibleAuraSlotImg")) ## 4
				# self.GetChild("VisibleBodySlotImg").Hide()
				# self.GetChild("VisibleHairSlotImg").Hide()
				# self.GetChild("VisibleWeaponSlotImg").Hide()
				# self.GetChild("VisibleAuraSlotImg").Hide()

				if app.USE_MOUNT_SKIN:
					self.visibleBtnList.append(self.GetChild("MountSkinToolTipButton")) ## 5
					self.visibleSlotList.append(self.GetChild("VisibleMountSkinSlotImg")) ## 5

				if app.USE_PET_SKIN:
					self.visibleBtnList.append(self.GetChild("PetSkinToolTipButton")) ## 6
					self.visibleSlotList.append(self.GetChild("VisiblePetSkinSlotImg")) ## 6
	

			if app.ENABLE_HIDE_SHINING_SYSTEM:
				self.visibleShiningBtnList.append(self.GetChild("ShiningWeaponToolTipButton"))  ## 0
				self.visibleShiningBtnList.append(self.GetChild("ShiningArmorToolTipButton"))   ## 1
				self.visibleShiningBtnList.append(self.GetChild("ShiningSpecialToolTipButton")) ## 2

				self.visibleShiningSlotList.append(self.GetChild("VisibleShiningWeaponSlotImg"))  ## 0
				self.visibleShiningSlotList.append(self.GetChild("VisibleShiningArmorSlotImg"))   ## 1
				self.visibleShiningSlotList.append(self.GetChild("VisibleShiningSpecialSlotImg")) ## 2				
										
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))

			self.boxMenuWindow = BoxMenu()
			self.mallButton = self.GetChild2("MallButton")
			# self.costumeButton = self.GetChild2("CostumeButton")
			
			if app.USE_OFFLINESHOP:
				self.offlineshopButton = self.GetChild2("OfflineshopButton")
			else:
				self.GetChild2("OfflineshopButton").Hide()

			if app.USE_LOG_EXCHANGE:
				self.ExchangelogButton = self.GetChild2("ExchangelogButton")
				self.GetChild2("ExchangelogButton").Hide()
			else:
				self.GetChild2("ExchangelogButton").Hide()

			# if app.ENABLE_BIOLOG_SYSTEM:
				# self.GetChild2("BioButton").Hide()
			# else:
				# self.GetChild2("BioButton").Hide()
			
			# if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				# self.extraButtons = []
				# for i in xrange(self.SPECIAL_BUTTONS_COUNT):
					# self.extraButtons.append(self.GetChild("extra_btn_%d_element" % i))
					# self.extraButtons[i].HideToolTipText()
					# self.extraButtons[i].SetEvent(lambda arg = i : self.OnPressExtraButton(arg))

			if app.ENABLE_SORT_INVENTORY or app.USE_STACK_INVENTORY:
				tmp = self.GetChild2("SortInventoryButton")
				tmp.SetEvent(ui.__mem_func__(self.__OrganizeInventory))
				self.itemsBtn = tmp
			else:
				self.GetChild2("SortInventoryButton").Hide()

			self.inventoryTab = []
			self.inventoryTab.append(self.GetChild("Inventory_Tab_01"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_02"))
			if app.ENABLE_EXTEND_INVEN_SYSTEM:
				self.inventoryTab.append(self.GetChild("Inventory_Tab_03"))
				self.inventoryTab.append(self.GetChild("Inventory_Tab_04"))

			slotIdxList = []
			for j in xrange(4):
				wndEquip = self.GetChild("EquipmentSlot_"+str(j))
				slotIdxList.append(wndEquip.GetSlotIndexList())
				wndEquip.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
				wndEquip.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
				wndEquip.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
				wndEquip.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
				wndEquip.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
				wndEquip.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

			self.slotIdxList = slotIdxList

			self.equipmentTab = []
			self.equipmentTab.append(self.GetChild("Equipment_Tab_01"))
			self.equipmentTab.append(self.GetChild("Equipment_Tab_02"))

			if app.ENABLE_BIOLOG_SYSTEM:
				self.wndCollect = None
			self.dlgQuestion = uicommon.QuestionDialog2()
			self.dlgQuestion.Close()

			if app.ENABLE_NEW_EQUIPMENT_SYSTEM and ENABLE_BELT_INVENTORY:
				self.wndBelt = BeltInventoryWindow(self)

			if app.USE_ACCE_SYSTEM:
				self.listHighlightedAcceSlot = []

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				self.listHighlightedChangeLookSlot = []

			if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
				self.listHighlightedSlot = []

			if app.ENABLE_GROWTH_PET_SYSTEM:
				self.PetItemQuestionDlg = uicommon.QuestionDialog()
				self.PetItemQuestionDlg.Close()

				self.PetSkillDelDlg = uicommon.QuestionDialog2()
				self.PetSkillDelDlg.Close()
				self.PetSkillAllDelBookIndex = -1

			self.board = self.GetChild("board")
		except:
			import exception
			exception.Abort("InventoryWindow.LoadWindow.BindObject")

		## Item
		wndItem.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndItem.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndItem.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		## Equipment
		wndEquip.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndEquip.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndEquip.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndEquip.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndEquip.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndEquip.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		if app.ENABLE_HIDE_COSTUME_SYSTEM:
			self.visibleBtnList[0].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 1, 0)
			self.visibleBtnList[0].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 1, 1)

			self.visibleBtnList[1].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 2, 0)
			self.visibleBtnList[1].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 2, 1)

			if app.USE_ACCE_SYSTEM:
				self.visibleBtnList[2].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 3, 0)
				self.visibleBtnList[2].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 3, 1)

			if app.USE_WEAPON_COSTUME_SYSTEM:
				self.visibleBtnList[3].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 4, 0)
				self.visibleBtnList[3].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 4, 1)
			if getattr(app, "USE_ACCE_SKIN", 0):
				self.visibleBtnList[4].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 8, 0)
				self.visibleBtnList[4].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 8, 1)
			else:
				self.visibleBtnList[4].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 5, 0)
				self.visibleBtnList[4].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 5, 1)

			if app.USE_MOUNT_SKIN:
				self.visibleBtnList[5].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 6, 0)
				self.visibleBtnList[5].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 6, 1)

			if app.USE_PET_SKIN:
				self.visibleBtnList[6].SetToggleUpEvent(ui.__mem_func__(self.VisibleCostume), 7, 0)
				self.visibleBtnList[6].SetToggleDownEvent(ui.__mem_func__(self.VisibleCostume), 7, 1)

			for slot in xrange(len(self.visibleSlotList)):
				self.visibleSlotList[slot].Hide()

		if app.ENABLE_HIDE_SHINING_SYSTEM:
			self.visibleShiningBtnList[0].SetToggleUpEvent(ui.__mem_func__(self.VisibleShining), 1, 0)
			self.visibleShiningBtnList[0].SetToggleDownEvent(ui.__mem_func__(self.VisibleShining), 1, 1)

			self.visibleShiningBtnList[1].SetToggleUpEvent(ui.__mem_func__(self.VisibleShining), 2, 0)
			self.visibleShiningBtnList[1].SetToggleDownEvent(ui.__mem_func__(self.VisibleShining), 2, 1)

			self.visibleShiningBtnList[2].SetToggleUpEvent(ui.__mem_func__(self.VisibleShining), 3, 0)
			self.visibleShiningBtnList[2].SetToggleDownEvent(ui.__mem_func__(self.VisibleShining), 3, 1)

			for slot in xrange(3):
				self.visibleShiningSlotList[slot].Hide()

		## RefineDialog
		self.refineDialog = uirefine.RefineDialog()
		self.refineDialog.Hide()

		## AttachMetinDialog
		self.attachMetinDialog = uiattachmetin.AttachMetinDialog()
		self.attachMetinDialog.Hide()

		if app.ENABLE_EXTEND_INVEN_SYSTEM:
			for inven_index in range(player.INVENTORY_PAGE_COUNT): ## 0, 1, 2, 3
				self.inventoryTab[inven_index].SetEvent(lambda arg=inven_index: self.SetInventoryPage(arg))
		else:
			self.inventoryTab[0].SetEvent(lambda arg = 0: self.SetInventoryPage(arg))
			self.inventoryTab[1].SetEvent(lambda arg = 1: self.SetInventoryPage(arg))
		self.inventoryTab[0].Down()

		self.equipmentTab[0].SetEvent(lambda arg = 0: self.SetEquipmentPageOld(arg))
		self.equipmentTab[1].SetEvent(lambda arg = 1: self.SetEquipmentPageOld(arg))
		self.equipmentTab[0].Down()
		self.equipmentTab[0].Hide()
		self.equipmentTab[1].Hide()

		self.equipmentTypeIndex = 0
		self.wndItem = wndItem
		self.wndEquip = wndEquip

		if self.mallButton:
			self.mallButton.SetEvent(ui.__mem_func__(self.OnClickMallButton))
		
		self.wndCostume = None

		# if self.costumeButton:
			# self.costumeButton.SetEvent(ui.__mem_func__(self.ClickCostumeButton))
	
		if app.USE_OFFLINESHOP and self.offlineshopButton:
			self.offlineshopButton.SetEvent(ui.__mem_func__(self.OnClickOfflineshop))

		if app.USE_LOG_EXCHANGE and self.ExchangelogButton:
			self.ExchangelogButton.SetEvent(ui.__mem_func__(self.__PressTrackOpen))#__PressTrackOpen

		# if app.ENABLE_BIOLOG_SYSTEM and self.BioButton:
			# self.BioButton.SetEvent(ui.__mem_func__(self.OnClickBioWindow))

		if app.__PENDANT__:
			self.pendantPageIdx = 0
			self.pendantPageOpened = 0
			self.pendantQuestionDialog = None
			self.GetChild("pendant_page_0").SAFE_SetEvent(self.__ClickPendantPage, 0)
			self.GetChild("pendant_page_1").SAFE_SetEvent(self.__ClickPendantPage, 1)

		if app.__RENEWAL_BRAVE_CAPE__:
			self.wndBraveCape = BraveCapeWindow(self)

		self.wndEquipmentTab = EquipmentTabWindow(self)

		self.original_height = self.board.GetHeight()
		self.MakeNewTitleBarOptions()
		
		self.SetEquipmentPageOld(0)
		self.SetInventoryPage(0)
		self.SetEquipmentPageOld(0)
		self.RefreshItemSlot()

	def MakeNewTitleBarOptions(self):
		for invTab in self.inventoryTab:
			invTab.posOriginal = invTab.GetLocalPosition()

		for j in xrange(4):
			tab = self.GetChild("Equipment_Base_Tab_" + str(j))
			tab.posOriginal = tab.GetLocalPosition()

		self.wndItem.posOriginal = self.wndItem.GetLocalPosition()
		
		self.wndExpandOptionTitleBar = self.itemsBtn
		self.wndExpandOptionTitleBar.isExpanded = False
		self.wndExpandOptionTitleBar.SetEvent(ui.__mem_func__(self.OnExpandTitleBar))
		
		self.boardExpandOption = ui.BorderA()
		self.boardExpandOption.SetParent(self)
		self.boardExpandOption.SetPosition(10, 30)
		self.boardExpandOption.SetSize(self.GetWidth() - 18, 30)
		self.boardExpandOption.Hide()
		
		ROOT_PATH = "d:/ymir work/ui/game/inv_manage/"
		self.separateButton = ui.MakeButton(self.boardExpandOption, 4, 6, uiscriptlocale.ITEM_SORT_OPTION, ROOT_PATH, "btn-sort-1.png", "btn-sort-2.png", "btn-sort-3.png")
		self.separateButton.SetEvent(ui.__mem_func__(self.__SortOrganizeDlg))
		
		self.StackButton = ui.MakeButton(self.boardExpandOption, 28, 6, uiscriptlocale.ITEM_STACK_OPTION, ROOT_PATH, "btn-stack-1.png", "btn-stack-2.png", "btn-stack-3.png")
		self.StackButton.SetEvent(ui.__mem_func__(self.__StackOrganizeDlg))
		
		self.slotBarExpandOption = ui.MakeImageBox(self.boardExpandOption, "neue/input.png", 52, 6)
		self.wndEditLineName = ui.EditLine()
		self.wndEditLineName.SetParent(self.slotBarExpandOption)
		self.wndEditLineName.SetPosition(4, 4)
		self.wndEditLineName.SetSize(self.slotBarExpandOption.GetWidth() - 4, self.slotBarExpandOption.GetHeight() - 4)
		self.wndEditLineName.SetMax(20)
		self.wndEditLineName.SetOverlayTextNew(localeinfo.OFFLINESHOP_SEARCH_NAME)
		self.wndEditLineName.OnIMEUpdate = ui.__mem_func__(self.OnValueUpdateSearch)
		self.wndEditLineName.SetEscapeEvent(ui.__mem_func__(self.OnEditLineName))
		self.wndEditLineName.Show()

	def OnEditLineName(self):
		if len(self.wndEditLineName.GetText()) == 0:
			self.Close()
			return True
			
		self.wndEditLineName.SetText("")
		self.OnValueUpdateSearch(True)
		return True

	def OnValueUpdateSearch(self, skipIme = False):
		if self.IsShow() == False:
			return

		if self.boardExpandOption.IsShow() == False:
			return

		if skipIme == False:
			if self.wndEditLineName.IsFocus() == False:
				return
		
			ui.EditLine.OnIMEUpdate(self.wndEditLineName)
		
		self.RefreshBagSlotWindow()

	def OnExpandTitleBar(self):
		self.wndExpandOptionTitleBar.isExpanded = not self.wndExpandOptionTitleBar.isExpanded
		
		SET_SIZE_HEIGHT = 30

		self.boardExpandOption.SetSize(self.boardExpandOption.GetWidth(), SET_SIZE_HEIGHT)
		
		if not self.wndExpandOptionTitleBar.isExpanded:
			self.boardExpandOption.Hide()
			self.board.SetSize(self.GetWidth(), self.original_height)

			for invTab in self.inventoryTab:
				invTab.SetPosition(*invTab.posOriginal)
				
			for j in xrange(4):
				tab = self.GetChild("Equipment_Base_Tab_" + str(j))
				tab.SetPosition(*tab.posOriginal)

			self.wndItem.SetPosition(*self.wndItem.posOriginal)
		else:
			self.boardExpandOption.Show()
			self.board.SetSize(self.GetWidth(), self.original_height + SET_SIZE_HEIGHT)
			
			for invTab in self.inventoryTab:
				invTab.SetPosition(invTab.posOriginal[0], invTab.posOriginal[1] + SET_SIZE_HEIGHT)

			for j in xrange(4):
				tab = self.GetChild("Equipment_Base_Tab_" + str(j))
				tab.SetPosition(tab.posOriginal[0], tab.posOriginal[1] + SET_SIZE_HEIGHT)

			self.wndItem.SetPosition(self.wndItem.posOriginal[0], self.wndItem.posOriginal[1] + SET_SIZE_HEIGHT)
			
		self.wndEditLineName.SetText("")
	
		self.SetSize(self.board.GetWidth(), self.board.GetHeight())
		self.UpdateRect()

	if app.USE_OFFLINESHOP:
		def OnClickOfflineshop(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.OpenOfflineShop()

	if app.USE_LOG_EXCHANGE:
		def OnClickExchangeLog(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.OpenExchangeLog()

	if app.ENABLE_BIOLOG_SYSTEM:
		def OnClickBioWindow(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.BiologManagerOpen()

	if app.ENABLE_EVENT_MANAGER:
		def ToggleInGameEvent(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.ToggleInGameEvent()

	if app.ENABLE_ULTIMATE_REGEN:
		def __PressTrackOpen(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.OpenTrackWindow()

	# if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
		# def OnPressExtraButton(self, arg, force = False):
			# interfaceHandler = systemSetting.GetInterfaceHandler()
			# if interfaceHandler:
				# interfaceHandler.ToggleExtraInventoryWindow(arg, self.extraButtons[arg].GetToolTipText(), force)

	def Destroy(self):
		if self.pick_item_dialog:
			self.pick_item_dialog.Destroy()
			del self.pick_item_dialog
			self.pick_item_dialog = None

		if app.ENABLE_SORT_INVENTORY or app.USE_STACK_INVENTORY:
			if self.itemsBtn:
				self.itemsBtn.SetEvent(None)
				self.itemsBtn = None

			if self.organizeDlg:
				self.organizeDlg.Destroy()
				del self.organizeDlg
				self.organizeDlg = None

		if app.__RENEWAL_BRAVE_CAPE__ and self.wndBraveCape:
			self.wndBraveCape.Destroy()
			del self.wndBraveCape
			self.wndBraveCape = None

		if self.wndCostume:
			self.wndCostume.Destroy()
			del self.wndCostume
			self.wndCostume = None

		if self.wndBelt:
			self.wndBelt.Destroy()
			del self.wndBelt
			self.wndBelt = None

		if self.boxMenuWindow:
			self.boxMenuWindow.Destroy()
			del self.boxMenuWindow
			self.boxMenuWindow = None

		if app.ENABLE_INGAME_WIKI:
			self.wndWiki = None

		self.board = None

		self.ClearDictionary()

		# if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			# self.extraButtons = []

		self.refineDialog.Destroy()
		self.refineDialog = 0

		self.attachMetinDialog.Destroy()
		self.attachMetinDialog = 0

		self.tooltipItem = None
		self.lastGold = None
		self.wndItem = 0
		self.wndEquip = 0

		self.questionDialog = None
		self.mallButton = None

		self.costumeButton = None
		self.interface = None

		if app.ENABLE_GROWTH_PET_SYSTEM:
			if self.petHatchingWindow:
				self.petHatchingWindow = None
				
			if self.petFeedWindow:
				self.petFeedWindow = None
				
			if self.petNameChangeWindow:
				self.petNameChangeWindow = None 

		if app.ENABLE_BIOLOG_SYSTEM:
			if self.wndCollect:
				self.wndCollect.Destroy()
				self.wndCollect = None

		self.inventoryTab = []
		self.equipmentTab = []

	def Hide(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.wndExpandedMoneyTaskBar:
			interfaceHandler.wndExpandedMoneyTaskBar.Hide()

		self.OverOutItem()

		# if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS():
		self.OnCloseQuestionDialog()
			# return

		if self.pick_item_dialog:
			self.pick_item_dialog.Close()

		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

		if self.wndCostume:
			self.isOpenedCostumeWindowWhenClosingInventory = self.wndCostume.IsShow()
			self.wndCostume.Close()

		if app.ENABLE_BIOLOG_SYSTEM:
			if self.wndCollect:
				self.isOpenedCollectWindowWhenClosingInventory = self.wndCollect.IsOpeningInventory()
				print "Is opening Biolog Inventory", self.isOpenedCollectWindowWhenClosingInventory
				self.wndCollect.Close()

		if self.wndBelt:
			self.isOpenedBeltWindowWhenClosingInventory = self.wndBelt.IsOpeningInventory()
			self.wndBelt.Close()

		# if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			# interfaceHandler = systemSetting.GetInterfaceHandler()
			# if interfaceHandler and interfaceHandler.wndSpecialInventory:
				# if interfaceHandler.wndSpecialInventory.IsShow():
					# interfaceHandler.wndSpecialInventory.Close()
					# osfinfo.isExtraWindowWhenClosingInventory = 1
				# else:
					# osfinfo.isExtraWindowWhenClosingInventory = 0

		if app.__RENEWAL_BRAVE_CAPE__ and self.wndBraveCape:
			self.isOpenedBraveCapeWindowWhenClosingInventory = self.wndBraveCape.IsOpeningInventory()
			self.wndBraveCape.Close()

		if self.wndEquipmentTab:
			self.wndEquipmentTab.Close()

		if app.ENABLE_SORT_INVENTORY or app.USE_STACK_INVENTORY:
			self.__CloseOrganizeDlg()

		wndMgr.Hide(self.hWnd)

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "inventory_window")
		self.Hide()

	if app.ENABLE_EXTEND_INVEN_SYSTEM:
		def SetInventoryPage(self, page):
			self.inventoryPageIndex = page

			for index in range(len(self.inventoryTab)):
				if index == page:
					continue
				self.inventoryTab[index].SetUp()

			self.RefreshBagSlotWindow()
	else:
		def SetInventoryPage(self, page):
			self.inventoryPageIndex = page
			self.inventoryTab[1-page].SetUp()
			self.RefreshBagSlotWindow()

	def SetEquipmentPageOld(self, page):
		self.equipmentPageIndex = page
		self.equipmentTab[1-page].SetUp()
		self.RefreshEquipSlotWindow()

	if app.__PENDANT__:
		def __CheckAllPendant(self):
			for slotIdx in range(item.PENDANT_FIRE_SLOT, item.PENDANT_FIRST_SOUL_SLOT):
				itemIdx = player.GetItemIndex(slotIdx)
				if not itemIdx:
					return False
				item.SelectItem(itemIdx)
				# if item.GetItemName().find("+5") == -1:
					# return False
			return True
		def __AcceptPendantPage(self, pageIdx):
			net.SendChatPacket("/pendant set %d" % pageIdx)
			self.pendantQuestionDialog.Hide()
			self.pendantQuestionDialog.Destroy()
			self.pendantQuestionDialog = None
		def __ClickPendantPage(self, pageIdx):
			self.SetEquipmentPage(self.equipmentTypeIndex)
			if not self.pendantPageOpened:
				if not self.pendantQuestionDialog:
					self.pendantQuestionDialog = uicommon.ItemQuestDialog()
				self.pendantQuestionDialog.SetTitleName(localeinfo.PENDANT_OPEN)
				self.pendantQuestionDialog.Open([[99900, 1]])
				self.pendantQuestionDialog.SelectEvent(self.__AcceptPendantPage, pageIdx)
				return
			net.SendChatPacket("/pendant set %d" % pageIdx)

		def SetPendantPageIdx(self, pageIdx, secondOpened):
			self.pendantPageIdx = pageIdx
			self.pendantPageOpened = secondOpened
			self.SetEquipmentPage(self.equipmentTypeIndex)

	def SetEquipmentPage(self, pageIdx):
		self.equipmentTypeIndex = pageIdx

		if self.wndEquipmentTab:
			self.wndEquipmentTab.UpdateTabState(pageIdx)

		for j in xrange(4):
			if j == pageIdx:
				self.GetChild("Equipment_Base_Tab_"+str(j)).Show()
			else:
				self.GetChild("Equipment_Base_Tab_"+str(j)).Hide()

		if app.__PENDANT__:
			if pageIdx == 3:
				self.GetChild("pendant_page_"+str(self.pendantPageIdx)).Down()
				self.GetChild("pendant_page_"+str(0 if self.pendantPageIdx else 1)).SetUp()

				wndEquip = self.GetChild("EquipmentSlot_"+str(pageIdx))
				wndEquip.ClearAllSlot()
				wndEquip.AppendSlot(item.PENDANT_FIRE_SLOT, 61, 12, 32, 32)
				wndEquip.AppendSlot(item.PENDANT_ICE_SLOT, 112, 49, 32, 32)
				wndEquip.AppendSlot(item.PENDANT_THUNDER_SLOT, 112, 109, 32, 32)
				wndEquip.AppendSlot(item.PENDANT_WIND_SLOT, 61, 146, 32, 32)
				wndEquip.AppendSlot(item.PENDANT_DARK_SLOT, 11, 109, 32, 32)
				wndEquip.AppendSlot(item.PENDANT_EARTH_SLOT, 11, 49, 32, 32)
				wndEquip.AppendSlot(item.PENDANT_FIRST_SOUL_SLOT if self.pendantPageIdx == 0 else item.PENDANT_SECOND_SOUL_SLOT, 61, 70, 32, 32)

				self.slotIdxList[3] = wndEquip.GetSlotIndexList()

		self.RefreshEquipSlotWindow()

	def OnClickMallButton(self):
		if self.boxMenuWindow:
			if self.boxMenuWindow.IsShow():
				self.boxMenuWindow.Close()
			else:
				self.boxMenuWindow.SetCenterPosition()
				self.boxMenuWindow.SetTop()
				self.boxMenuWindow.Open()

	def ClickCostumeButton(self):
		if self.wndCostume:
			if self.wndCostume.IsShow():
				self.wndCostume.Hide()
			else:
				self.wndCostume.Show()
		else:
			self.wndCostume = CostumeWindow(self)
			self.wndCostume.Show()

	def ShowCostumeInventory(self,pageidx):
		self.SetEquipmentPage(pageidx)
		# if self.wndCostume:
			# if not self.wndCostume.IsShow():
				# self.wndCostume.Show()
		# else:
			# self.wndCostume = CostumeWindow(self)
			# self.wndCostume.Show()

	def OnPickItem(self, itemSlot, splitCount, splitAuto):
		if app.USE_AUTO_SPLIT_ITEMS and splitAuto:
			net.SendChatPacket("/split_item {} {}".format(itemSlot, splitCount))
			return

		if app.USE_OFFLINESHOP and uiofflineshop_ae.IsBuildingShop() and uiofflineshop_ae.IsSaleSlot(player.INVENTORY, itemSlot):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
			return

		itemVnum = player.GetItemIndex(itemSlot)
		if itemVnum:
			mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_INVENTORY, itemSlot, itemVnum, splitCount)

		if app.ENABLE_REMEMBER_LAST_SPLIT:
			systemSetting.SetLastSplitData(splitCount)

	def __InventoryLocalSlotPosToGlobalSlotPos(self, local):
		if player.IsEquipmentSlot(local) or player.IsCostumeSlot(local) or (player.IsBeltInventorySlot(local)):
			return local

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			if player.IsSkillBookInventorySlot(local) or player.IsUpgradeItemsInventorySlot(local) or player.IsStoneInventorySlot(local) or player.IsGiftBoxInventorySlot(local):
				return local

		return self.inventoryPageIndex * player.INVENTORY_PAGE_SIZE + local

	def SetQuickTransferHighlight(self, greenSlot, redSlot):
		self.quickTransferGreenSlot = greenSlot
		self.quickTransferRedSlot = redSlot
		self.RefreshBagSlotWindow()

	def ClearQuickTransferHighlightSlots(self):
		if self.quickTransferGreenSlot >= 0 or self.quickTransferRedSlot >= 0:
			self.quickTransferGreenSlot = -1
			self.quickTransferRedSlot = -1
			self.RefreshBagSlotWindow()

	def RefreshBagSlotWindow(self):
		if not self.wndItem:
			return

		onTopWindow = None

		if app.WJ_ENABLE_TRADABLE_ICON and self.interface:
			onTopWindow = self.interface.GetOnTopWindow()

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			for i in self.listHighlightedChangeLookSlot:
				self.wndItem.SetCanMouseEventSlot(i)

			self.listHighlightedChangeLookSlot = []

		for i in xrange(self.wndItem.GetSlotCount()):
			self.wndItem.DeactivateSlot(i)

			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)

			if self.quickTransferGreenSlot >= 0 and slotNumber == self.quickTransferGreenSlot:
				self.wndItem.ActivateSlot(i)
				if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
					self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_GREEN)
			elif self.quickTransferRedSlot >= 0 and slotNumber == self.quickTransferRedSlot:
				self.wndItem.ActivateSlot(i)
				if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
					self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_RED)
			itemVnum = player.GetItemIndex(slotNumber)

			if itemVnum and self.wndEditLineName.GetText() and self.wndExpandOptionTitleBar.isExpanded:
				item.SelectItem(itemVnum)
				stName = item.GetItemName()
				
				if itemVnum == 50300: # IS_SKILLBOOK
					import skill
					stName = skill.GetSkillName(player.GetItemMetinSocket(slotNumber, 0))
					
				text = self.wndEditLineName.GetText()
				if len(stName) >= len(text) and stName[:len(text)].lower() == text.lower():
					pass
				else:
					self.wndItem.ClearSlot(i)
					continue

			if onTopWindow != None or (app.USE_OFFLINESHOP and uiofflineshop_ae.IsBuildingShop()):
				if itemVnum:
					if self.interface.MarkUnusableInvenSlotOnTopWnd(onTopWindow, slotNumber):
						self.wndItem.SetUnusableSlotOnTopWnd(i)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(i)
				else:
					self.wndItem.SetUsableSlotOnTopWnd(i)

			itemCount = player.GetItemCount(slotNumber)
			if not itemVnum or not itemCount:
				self.wndItem.ClearSlot(i)
				continue
			elif 1 == itemCount:
				itemCount = 0

			self.wndItem.SetItemSlot(i, itemVnum, itemCount)

			changeLookVnum = 0
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				changeLookVnum = player.GetChangeLookVnum(player.INVENTORY, slotNumber)
				if not changeLookVnum:
					self.wndItem.EnableSlotCoverImage(i, False)
				else:
					self.wndItem.SetSlotCoverImage(i, "icon/item/ingame_convert_mark.tga")

			wasActivated = 0

			if app.USE_ITEM_ATTR_BACKUP_MODE and player.GetItemBackup(player.INVENTORY, slotNumber):
				self.wndItem.ActivateSlot(i)
				self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_ORANGE)
				wasActivated = 1

			if app.ENABLE_GROWTH_PET_SYSTEM and constinfo.IS_PET_ITEM(itemVnum):
				wasActivated = self.__ActivePetHighlightSlot(slotNumber)
				self.__SetCoolTimePetItemSlot(slotNumber, itemVnum)

			# Buffi summon scroll: highlighted while its buffi is out (server sets socket0=1 active /
			# 0 dismissed, same active-flag pattern as pets/auto-potion).
			if wasActivated == 0 and constinfo.IS_BUFFI_SUMMON_ITEM(itemVnum):
				if player.GetItemMetinSocket(player.INVENTORY, slotNumber, 0):
					self.wndItem.ActivateSlot(i)
					wasActivated = 1

			if wasActivated == 0 and (constinfo.IS_AUTO_POTION(itemVnum) or osfinfo.IS_PET_SEAL(itemVnum)):
				if player.GetItemMetinSocket(slotNumber, 0 if constinfo.IS_AUTO_POTION(itemVnum) else 1):
					self.wndItem.ActivateSlot(i)
					wasActivated = 1

			if wasActivated == 0 and app.ENABLE_SOUL_SYSTEM and item.IsSoulItem(itemVnum):
				if player.GetItemMetinSocket(slotNumber, 1):
					self.wndItem.ActivateSlot(i)
					wasActivated = 1

			if wasActivated == 0 and itemVnum >= 98001 and itemVnum <= 98005:
				if player.GetItemMetinSocket(slotNumber, 2):
					self.wndItem.ActivateSlot(i)
					wasActivated = 1

																			#(osfinfo.IS_BLEND_POTION(itemVnum) or osfinfo.IS_EXTENDED_BLEND_POTION(itemVnum)):
			if wasActivated == 0 and app.ENABLE_EXTENDED_BLEND_AFFECT and item.GetItemTypeByVnum(itemVnum) == item.ITEM_TYPE_BLEND:
				if player.GetItemMetinSocket(slotNumber, 3):
					self.wndItem.ActivateSlot(i)
					wasActivated = 1

					if osfinfo.IS_EXTENDED_BLEND_POTION(itemVnum):
						self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_RED)
					elif osfinfo.NORMAL_BLEND_COLOR(itemVnum):
						self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_PURPLE)
					elif osfinfo.DRAGON_GOD_COLOR(itemVnum):
						self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_ORANGE)
					elif osfinfo.OTHER_ITEMS_COLOR(itemVnum):
						self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_DARK_BLUE)
					else:
						self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_DARK_BLUE)

				if not changeLookVnum:
					if osfinfo.IS_EXTENDED_BLEND_POTION(itemVnum):
						self.wndItem.SetSlotCoverImage(i, "d:/ymir work/ui/acce/ingame_convert_mark_02.tga")
					elif osfinfo.IS_BLEND_POTION(itemVnum) and itemVnum not in (39217, 39218, 39219, 39220, 39224, 39225):
						self.wndItem.SetSlotCoverImage(i, "icon/item/trade.tga")
					else:
						self.wndItem.EnableSlotCoverImage(i, False)

			if wasActivated == 0 and app.ENABLE_TITLE_SYSTEM_YUMA:
				item.SelectItem(itemVnum)
				if item.GetItemType() == item.ITEM_TYPE_TITLE:
					if player.GetItemMetinSocket(slotNumber, 2) == 1:
						self.wndItem.ActivateSlot(i)
						wasActivated = 1

			if wasActivated == 0 and app.USE_ACCE_SYSTEM:
				for j in xrange(acce.WINDOW_MAX_MATERIALS):
					(isHere, iCell) = acce.GetAttachedItem(j)
					if isHere and iCell == slotNumber:
						self.wndItem.ActivateSlot(slotNumber)
						self.wndItem.SetSlotDiffuseColor(slotNumber, wndMgr.COLOR_TYPE_GREEN)

			if wasActivated == 0 and itemVnum == ITEM_VNUM_ANTIDROP_CHARM:
				if player.GetItemMetinSocket(slotNumber, 2):
					self.wndItem.ActivateSlot(i)
					self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_RED)
					wasActivated = 1

			# ENABLE_ACCOUNT_BIND_ITEMS — bound items get a lock icon overlay.
			# Runs last so it wins over change-look / blend cover images above.
			if itemVnum >= 37863 and itemVnum <= 37892:
				self.wndItem.SetSlotCoverImage(i, "icon/item/ingame_convert_Mark.tga")

			if app.ENABLE_ACCOUNT_BIND_ITEMS and player.IsItemAccountBound(player.INVENTORY, slotNumber):
				self.wndItem.SetSlotCoverImage(i, "icon/item/account_locked.png")

		self.__HighlightSlot_Refresh()

		self.wndItem.RefreshSlot()

		if app.QUICK_SELL_SYSTEM:
			self.RefreshQuickSellMarks()

		if self.wndBelt:
			self.wndBelt.RefreshSlot()

	def RefreshEquipSlotWindow(self):
		wndEquip = self.GetChild("EquipmentSlot_"+str(self.equipmentTypeIndex))
		slotIdxList = self.slotIdxList[self.equipmentTypeIndex]
		for slotNumber in slotIdxList:
			wndEquip.SetItemSlot(slotNumber, player.GetItemIndex(slotNumber), 0)

			if app.__PENDANT__ and self.equipmentTypeIndex == 3:
				if slotNumber == item.PENDANT_FIRST_SOUL_SLOT or slotNumber == item.PENDANT_SECOND_SOUL_SLOT:
					if self.__CheckAllPendant():
						wndEquip.ActivateSlot(slotNumber)
					else:
						wndEquip.DeactivateSlot(slotNumber)

			if app.ENABLE_ACCOUNT_BIND_ITEMS and player.GetItemIndex(slotNumber) and player.IsItemAccountBound(player.INVENTORY, slotNumber):
				wndEquip.SetSlotCoverImage(slotNumber, "icon/item/account_locked.png")
			elif app.ENABLE_ACCOUNT_BIND_ITEMS:
				wndEquip.EnableSlotCoverImage(slotNumber, False)

		wndEquip.RefreshSlot()

		if self.wndCostume:
			self.wndCostume.RefreshCostumeSlot()

	# def RefreshEquipSlotWindow(self):
		# getItemVNum=player.GetItemIndex
		# getItemCount=player.GetItemCount
		# setItemVNum=self.wndEquip.SetItemSlot

		# for i in xrange(player.EQUIPMENT_PAGE_COUNT):
			# slotNumber = player.EQUIPMENT_SLOT_START + i
			# itemCount = getItemCount(slotNumber)
			# if itemCount <= 1:
				# itemCount = 0
			# setItemVNum(slotNumber, getItemVNum(slotNumber), itemCount)

			# if app.ENABLE_CHANGE_LOOK_SYSTEM:
				# if not player.GetChangeLookVnum(player.EQUIPMENT, slotNumber) == 0:
					# self.wndEquip.SetSlotCoverImage(slotNumber, "icon/item/ingame_convert_Mark.tga")
				# else:
					# self.wndEquip.EnableSlotCoverImage(slotNumber, False)

			# # if app.__PENDANT__:
				# # if slotNumber==item.PENDANT_FIRST_SOUL_SLOT or slotNumber==item.PENDANT_SECOND_SOUL_SLOT:
					# # if self.__CheckAllPendant():
						# # wndEquip.ActivateSlot(slotNumber)
					# # else:
						# # wndEquip.DeactivateSlot(slotNumber)

		# if app.ENABLE_NEW_EQUIPMENT_SYSTEM:
			# for i in xrange(player.NEW_EQUIPMENT_SLOT_COUNT):
				# slotNumber = player.NEW_EQUIPMENT_SLOT_START + i
				# itemCount = getItemCount(slotNumber)
				# if itemCount <= 1:
					# itemCount = 0
				# setItemVNum(slotNumber, getItemVNum(slotNumber), itemCount)

		# self.wndEquip.RefreshSlot()

		# if self.wndCostume:
			# self.wndCostume.RefreshCostumeSlot()

	def RefreshItemSlot(self):
		self.RefreshBagSlotWindow()
		self.RefreshEquipSlotWindow()

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def SellItem(self):
		if app.USE_OFFLINESHOP:
			if uiofflineshop_ae.IsBuildingShop() and\
				uiofflineshop_ae.IsSaleSlot(player.INVENTORY, self.sellingSlotNumber):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				return

		if self.sellingSlotitemIndex == player.GetItemIndex(self.sellingSlotNumber):
			if self.sellingSlotitemCount == player.GetItemCount(self.sellingSlotNumber):
				net.SendShopSellPacketNew(self.sellingSlotNumber, self.questionDialog.count, player.INVENTORY)
				snd.PlaySound("sound/ui/money.wav")

		self.OnCloseQuestionDialog()

	def OnDetachMetinFromItem(self):
		if None == self.questionDialog:
			return

		#net.SendItemUseToItemPacket(self.questionDialog.sourcePos, self.questionDialog.targetPos)
		self.__SendUseItemToItemPacket(self.questionDialog.sourcePos, self.questionDialog.targetPos)
		self.OnCloseQuestionDialog()

	def OnCloseQuestionDialog(self):
		if not self.questionDialog:
			return
		
		self.questionDialog.Close()
		del self.questionDialog
		self.questionDialog = None
		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	def __HasItemAttributes(self, slotIndex):
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			if player.GetItemAttribute(slotIndex, i)[0] != 0:
				return True
		return False

	def __AskQuickSellEnchanted(self, slotIndex, itemCount):
		if self.questionDialog:
			self.OnCloseQuestionDialog()

		itemVnum = player.GetItemIndex(slotIndex)

		self.questionDialog = uicommon.QuestionDialog()
		self.questionDialog.SetText(getattr(localeinfo, "QUICK_SELL_ENCHANTED_WARN", "This item is enchanted. Are you sure?"), isRed=True)
		self.questionDialog.SetAcceptEvent(lambda arg=TRUE: self.__OnAnswerQuickSellEnchanted(arg, slotIndex, itemCount, itemVnum))
		self.questionDialog.SetCancelEvent(lambda arg=FALSE: self.__OnAnswerQuickSellEnchanted(arg, slotIndex, itemCount, itemVnum))
		self.questionDialog.Open()
		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def __OnAnswerQuickSellEnchanted(self, answer, slotIndex, itemCount, itemVnum):
		self.OnCloseQuestionDialog()
		if not answer:
			return

		# the bag can move under an open dialog - sell only what the player actually confirmed
		if player.GetItemIndex(slotIndex) != itemVnum:
			return

		if player.GetItemCount(slotIndex) != itemCount:
			return

		net.SendShopSellPacketNew(slotIndex, itemCount, player.INVENTORY)
		snd.PlaySound("sound/ui/money.wav")

	## Slot Event
	def SelectEmptySlot(self, selectedSlotPos):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		#if app.USE_ACCE_SYSTEM:
		#	if player.GetAcceRefineWindowOpen() == 1:
		#		return

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if player.GetChangeLookWindowOpen() == 1:
				return

		if app.ENABLE_ATTR_6TH_7TH:
			if self.interface.wndAttr67Add.IsShow():
				return

		selectedSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(selectedSlotPos)

		if mousemodule.mouseController.isAttached():
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			attachedItemCount = mousemodule.mouseController.GetAttachedItemCount()
			attachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()

			if app.USE_OFFLINESHOP:
				if uiofflineshop_ae.IsBuildingShop() and\
					uiofflineshop_ae.IsSaleSlot(player.SlotTypeToInvenType(attachedSlotType),attachedSlotPos):
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
					return

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				if player.SLOT_TYPE_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_STONE_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_ENCHANT_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_POTS_INVENTORY == attachedSlotType:

					itemCount = player.GetItemCount(attachedSlotPos)
					attachedCount = mousemodule.mouseController.GetAttachedItemCount()

					self.__SendMoveItemPacket(attachedSlotPos, selectedSlotPos, attachedCount)

					if item.IsRefineScroll(attachedItemIndex):
						self.interface.SetUseItemMode(False)

				elif app.ENABLE_SWITCHBOT and player.SLOT_TYPE_SWITCHBOT == attachedSlotType:
					attachedCount = mousemodule.mouseController.GetAttachedItemCount()
					net.SendItemMovePacket(player.SWITCHBOT, attachedSlotPos, player.INVENTORY, selectedSlotPos, attachedCount)
				elif app.USE_AURA_SYSTEM and player.SLOT_TYPE_AURA == attachedSlotType:
					net.SendAuraRefineCheckOut(attachedSlotPos, player.GetAuraRefineWindowType())

				elif player.SLOT_TYPE_PRIVATE_SHOP == attachedSlotType:
					mousemodule.mouseController.RunCallBack("INVENTORY")
				elif player.SLOT_TYPE_SHOP == attachedSlotType:
					net.SendShopBuyPacket(attachedSlotPos)

				elif player.SLOT_TYPE_SAFEBOX == attachedSlotType:
					if player.ITEM_MONEY == attachedItemIndex:
						net.SendSafeboxWithdrawMoneyPacket(mousemodule.mouseController.GetAttachedItemCount())
						snd.PlaySound("sound/ui/money.wav")
					else:
						net.SendSafeboxCheckoutPacket(attachedSlotPos, selectedSlotPos)
				elif player.SLOT_TYPE_MALL == attachedSlotType:
					net.SendMallCheckoutPacket(attachedSlotPos, selectedSlotPos)
				elif app.FAST_EQUIP_WORLDARD and attachedSlotType == player.SLOT_TYPE_CHANGE_EQUIP:
					net.SendItemMovePacket(player.CHANGE_EQUIP, attachedSlotPos, player.INVENTORY, selectedSlotPos, mousemodule.mouseController.GetAttachedItemCount())
				elif app.ENABLE_CHANGE_LOOK_SYSTEM and attachedSlotType == player.SLOT_TYPE_CHANGE_LOOK:
					pass
			else:
				if player.SLOT_TYPE_INVENTORY == attachedSlotType:
					itemCount = player.GetItemCount(attachedSlotPos)
					attachedCount = mousemodule.mouseController.GetAttachedItemCount()

					self.__SendMoveItemPacket(attachedSlotPos, selectedSlotPos, attachedCount)

					if item.IsRefineScroll(attachedItemIndex):
						self.interface.SetUseItemMode(False)

				elif app.ENABLE_SWITCHBOT and player.SLOT_TYPE_SWITCHBOT == attachedSlotType:
					attachedCount = mousemodule.mouseController.GetAttachedItemCount()
					net.SendItemMovePacket(player.SWITCHBOT, attachedSlotPos, player.INVENTORY, selectedSlotPos, attachedCount)
				elif app.USE_AURA_SYSTEM and player.SLOT_TYPE_AURA == attachedSlotType:
					net.SendAuraRefineCheckOut(attachedSlotPos, player.GetAuraRefineWindowType())

				elif player.SLOT_TYPE_PRIVATE_SHOP == attachedSlotType:
					mousemodule.mouseController.RunCallBack("INVENTORY")
				elif player.SLOT_TYPE_SHOP == attachedSlotType:
					net.SendShopBuyPacket(attachedSlotPos)

				elif player.SLOT_TYPE_SAFEBOX == attachedSlotType:
					if player.ITEM_MONEY == attachedItemIndex:
						net.SendSafeboxWithdrawMoneyPacket(mousemodule.mouseController.GetAttachedItemCount())
						snd.PlaySound("sound/ui/money.wav")
					else:
						net.SendSafeboxCheckoutPacket(attachedSlotPos, selectedSlotPos)

				elif player.SLOT_TYPE_MALL == attachedSlotType:
					net.SendMallCheckoutPacket(attachedSlotPos, selectedSlotPos)
				elif app.FAST_EQUIP_WORLDARD and attachedSlotType == player.SLOT_TYPE_CHANGE_EQUIP:
					net.SendItemMovePacket(player.CHANGE_EQUIP, attachedSlotPos, player.INVENTORY, selectedSlotPos, mousemodule.mouseController.GetAttachedItemCount())
				elif app.ENABLE_CHANGE_LOOK_SYSTEM and attachedSlotType == player.SLOT_TYPE_CHANGE_LOOK:
					pass

			mousemodule.mouseController.DeattachObject()

	def SelectItemSlot(self, itemSlotIndex):
		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		## 2021.02.01.Owsap - Prevent unequipping an item while acting emotion.
		if player.IsActingEmotion():
			return

		itemSlotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(itemSlotIndex)

		if mousemodule.mouseController.isAttached():
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			attachedItemVID = mousemodule.mouseController.GetAttachedItemIndex()

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				if player.SLOT_TYPE_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_SKILL_BOOK_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_STONE_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_GIFT_BOX_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_ENCHANT_INVENTORY == attachedSlotType or\
					player.SLOT_TYPE_POTS_INVENTORY == attachedSlotType:

					self.__DropSrcItemToDestItemInInventory(attachedItemVID, attachedSlotPos, itemSlotIndex)
			else:
				if player.SLOT_TYPE_INVENTORY == attachedSlotType:
					self.__DropSrcItemToDestItemInInventory(attachedItemVID, attachedSlotPos, itemSlotIndex)

			mousemodule.mouseController.DeattachObject()
		else:
			curCursorNum = app.GetCursor()

			if app.SELL == curCursorNum:
				self.__SellItem(itemSlotIndex)

			elif app.BUY == curCursorNum:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.SHOP_BUY_INFO)

			elif app.IsPressed(app.DIK_LALT):
				link = player.GetItemLink(itemSlotIndex)
				ime.PasteString(link)

			elif getattr(app, "USE_QUICK_ATTR_TRANSFER", 0) and app.IsPressed(app.DIK_LCONTROL) and app.IsPressed(app.DIK_LSHIFT):
				if self.interface:
					self.interface.RequestOpenQuickTransferWindow(itemSlotIndex)

			elif app.IsPressed(app.DIK_LSHIFT):
				if app.USE_ITEM_ATTR_BACKUP_MODE and player.GetItemBackup(player.INVENTORY, itemSlotIndex):
					if self.interface:
						self.interface.OpenItemBackupAttr(player.INVENTORY, itemSlotIndex)
					return
				itemCount = player.GetItemCount(itemSlotIndex)
				if itemCount > 1:
					if not self.pick_item_dialog:
						self.pick_item_dialog = uicommon.PickItemDialog()
						self.pick_item_dialog.SetAcceptEvent(ui.__mem_func__(self.OnPickItem))

					self.pick_item_dialog.Open(itemSlotIndex, itemCount)
				else:
					if app.ENABLE_RENDER_TARGET:
						if uiRenderTarget.IsCanShowItems(player.GetItemIndex(itemSlotIndex)):
							itemTransmutedVnum = player.GetChangeLookVnum(player.INVENTORY,itemSlotIndex)
							self.interface.OpenRenderTargetWindow(0, itemTransmutedVnum if itemTransmutedVnum else player.GetItemIndex(itemSlotIndex))

			elif app.IsPressed(app.DIK_LCONTROL):
				itemIndex = player.GetItemIndex(itemSlotIndex)

				if True == item.CanAddToQuickSlotItem(itemIndex):
					player.RequestAddToEmptyLocalQuickSlot(player.SLOT_TYPE_INVENTORY, itemSlotIndex)
				else:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.QUICKSLOT_REGISTER_DISABLE_ITEM)
			else:
				if app.IsPressed(app.DIK_TAB):
					if app.QUICK_SELL_SYSTEM:
						self.interface.ToggleQuickSellSlot(player.INVENTORY, itemSlotIndex)
						self.RefreshBagSlotWindow()
						return

					if app.USE_OFFLINESHOP:
						if uiofflineshop_ae.IsBuildingShop() and uiofflineshop_ae.IsSaleSlot(player.INVENTORY, itemSlotIndex):
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
							return

					itemCount = player.GetItemCount(itemSlotIndex)

					if shop.IsOpen():
						#if not shop.IsPrivateShop():
						if self.__HasItemAttributes(itemSlotIndex):
							self.__AskQuickSellEnchanted(itemSlotIndex, itemCount)
							return
						net.SendShopSellPacketNew(itemSlotIndex, itemCount, player.INVENTORY)
						snd.PlaySound("sound/ui/money.wav")
						return

				selectedItemVNum = player.GetItemIndex(itemSlotIndex)
				itemCount = player.GetItemCount(itemSlotIndex)
				if app.ENABLE_GROWTH_PET_SYSTEM:
					if self.__CanAttachGrowthPetItem(selectedItemVNum, itemSlotIndex):
						mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_INVENTORY, itemSlotIndex, selectedItemVNum, itemCount)
				else:
					mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_INVENTORY, itemSlotIndex, selectedItemVNum, itemCount)

				if self.__IsUsableItemToItem(selectedItemVNum, itemSlotIndex):
					self.interface.SetUseItemMode(True)
				else:
					self.interface.SetUseItemMode(False)

				snd.PlaySound("sound/ui/pick.wav")

	def __DropSrcItemToDestItemInInventory(self, srcItemVID, srcItemSlotPos, dstItemSlotPos):
		if app.USE_AURA_SYSTEM and player.IsAuraRefineWindowOpen():
			return

		if srcItemSlotPos == dstItemSlotPos:
			return

		if app.USE_ACCE_SYSTEM:
			if player.GetAcceRefineWindowOpen() == 1:
				return

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if player.GetChangeLookWindowOpen() == 1:
				return

		if app.USE_OFFLINESHOP:
			if uiofflineshop_ae.IsBuildingShop() and\
				(uiofflineshop_ae.IsSaleSlot(player.INVENTORY, srcItemSlotPos) or\
				uiofflineshop_ae.IsSaleSlot(player.INVENTORY , dstItemSlotPos)):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				return
		
		sourceItemVnum = player.GetItemIndex(srcItemSlotPos)
		if not sourceItemVnum:
			return
		
		useType = item.GetUseType(sourceItemVnum)
		
		if app.USE_AURA_SYSTEM and not app.USE_AURA_ACCESSORY_SOCKET_RENEWED and useType == "USE_REMOVE_AURA_ATTR":
			self.AttachItemToDesc(useType, srcItemSlotPos, dstItemSlotPos)
			return
		elif app.USE_ENCHANT_COSTUMES and\
			useType == "USE_REMOVE_COSTUME_ENCHANT":
			self.AttachItemToDesc(useType, srcItemSlotPos, dstItemSlotPos)
			return

		if player.GetItemIndex(srcItemSlotPos) == player.GetItemIndex(dstItemSlotPos) \
			and (player.GetItemFlags(srcItemSlotPos) & item.ITEM_FLAG_STACKABLE) \
			and player.IsEquipmentSlot(dstItemSlotPos) == False:
			self.__SendMoveItemPacket(srcItemSlotPos, dstItemSlotPos, 0)
			return
		
		if app.ENABLE_SOUL_BIND_SYSTEM:
			# cyh itemseal 2013 11 08
			if item.IsSealScroll(srcItemVID):
				if player.CanSealItem(srcItemVID, player.INVENTORY, dstItemSlotPos):
					self.__OpenQuestionDialog(srcItemSlotPos, dstItemSlotPos)
					return

		if item.IsRefineScroll(srcItemVID):
			self.RefineItem(srcItemSlotPos, dstItemSlotPos)
			self.interface.SetUseItemMode(False)

		elif item.IsMetin(srcItemVID):
			self.AttachMetinToItem(srcItemSlotPos, dstItemSlotPos)

		elif item.IsDetachScroll(srcItemVID):
			self.DetachMetinFromItem(srcItemSlotPos, dstItemSlotPos)

		elif item.IsKey(srcItemVID):
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		elif srcItemVID == SOCKET_BLESS_ITEM_VNUM:
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		elif (player.GetItemFlags(srcItemSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		elif item.GetUseType(srcItemVID) in self.USE_TYPE_TUPLE:
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		elif app.ENABLE_67TH_BONUS and (srcItemVID == item.ADD_RARE_ATTRIBUTE_VNUM or srcItemVID == item.CHANGE_RARE_ATTRIBUTE_VNUM):
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		else:
			if app.ENABLE_GROWTH_PET_SYSTEM:
				if self.__IsPetItem(srcItemVID):
					if self.__SendUsePetItemToItemPacket(srcItemVID, srcItemSlotPos, dstItemSlotPos):
						return
			
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if item.IsChangeLookClearScroll(srcItemVID):
					if dstItemSlotPos > player.EQUIPMENT_SLOT_START - 1:
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHANGE_LOOK_DO_NOT_EQUIP_ITEM)
						return
					
					if player.CanChangeLookClearItem(srcItemVID, player.INVENTORY, dstItemSlotPos):
						self.__OpenQuestionDialog(srcItemSlotPos, dstItemSlotPos)
						return

			if app.ENABLE_SET_ITEM:
				if item.IsSetItemScroll(srcItemVID):
					if player.CanSetItemClearItem(srcItemVID, player.INVENTORY, dstItemSlotPos):
						self.__OpenQuestionDialog(srcItemSlotPos, dstItemSlotPos)
						return

			if player.IsEquipmentSlot(dstItemSlotPos):

				if item.IsEquipmentVID(srcItemVID):
					self.__UseItem(srcItemSlotPos)
			else:
				self.__SendMoveItemPacket(srcItemSlotPos, dstItemSlotPos, 0)
				# net.SendItemMovePacket(srcItemSlotPos, dstItemSlotPos, 0)

	def __OpenQuestionDialog(self, srcItemPos, dstItemPos):
		if self.interface.IsShowDlgQuestionWindow():
			self.interface.CloseDlgQuestionWindow()

		getItemVNum = player.GetItemIndex(dstItemPos)

		self.srcItemPos = srcItemPos
		self.dstItemPos = dstItemPos

		self.dlgQuestion.SetAcceptEvent(ui.__mem_func__(self.__Accept))
		self.dlgQuestion.SetCancelEvent(ui.__mem_func__(self.__Cancel))

		self.dlgQuestion.SetText1("%s" % item.GetItemNameByVnum(getItemVNum))
		self.dlgQuestion.SetText2(localeinfo.INVENTORY_REALLY_USE_ITEM)

		self.dlgQuestion.Open()

	def __Accept(self):
		self.dlgQuestion.Close()
		self.__SendUseItemToItemPacket(self.srcItemPos, self.dstItemPos)
		self.srcItemPos = (0, 0)
		self.dstItemPos = (0, 0)

	def __Cancel(self):
		self.srcItemPos = (0, 0)
		self.dstItemPos = (0, 0)
		self.dlgQuestion.Close()

	def __SellItem(self, itemSlotPos):
		if app.USE_OFFLINESHOP:
			if uiofflineshop_ae.IsBuildingShop():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				return

		if not player.IsEquipmentSlot(itemSlotPos):
			self.sellingSlotNumber = itemSlotPos
			itemIndex = player.GetItemIndex(itemSlotPos)
			itemCount = player.GetItemCount(itemSlotPos)

			self.sellingSlotitemIndex = itemIndex
			self.sellingSlotitemCount = itemCount

			item.SelectItem(itemIndex)
			
			if item.IsAntiFlag(item.ANTIFLAG_SELL):
				popup = uicommon.PopupDialog()
				popup.SetText(localeinfo.SHOP_CANNOT_SELL_ITEM)
				popup.SetAcceptEvent(self.__OnClosePopupDialog)
				popup.Open()
				self.popup = popup
				return

			itemPrice = item.GetISellItemPrice()

			if item.Is1GoldItem():
				itemPrice = itemCount / itemPrice / 5
			else:
				itemPrice = itemPrice * itemCount / 5

			item.GetItemName(itemIndex)
			itemName = item.GetItemName()

			self.questionDialog = uicommon.QuestionDialog()
			self.questionDialog.SetText(localeinfo.DO_YOU_SELL_ITEM(itemName, itemCount, itemPrice))
			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.SellItem))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
			self.questionDialog.Open()
			self.questionDialog.count = itemCount

			constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def __OnClosePopupDialog(self):
		self.pop = None

	def RefineItem(self, scrollSlotPos, targetSlotPos):
		if app.USE_OFFLINESHOP:
			if uiofflineshop_ae.IsBuildingShop():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				return

		scrollIndex = player.GetItemIndex(scrollSlotPos)
		targetIndex = player.GetItemIndex(targetSlotPos)

		if player.REFINE_OK != player.CanRefine(scrollIndex, targetSlotPos):
			return

		if app.ENABLE_AUTO_REFINE:
			osfinfo.AUTO_REFINE_TYPE = 1
			osfinfo.AUTO_REFINE_DATA["ITEM"][0] = scrollSlotPos
			osfinfo.AUTO_REFINE_DATA["ITEM"][1] = targetSlotPos

		###########################################################
		self.__SendUseItemToItemPacket(scrollSlotPos, targetSlotPos)
		#net.SendItemUseToItemPacket(scrollSlotPos, targetSlotPos)
		return
		###########################################################

		###########################################################
		#net.SendRequestRefineInfoPacket(targetSlotPos)
		#return
		###########################################################

		result = player.CanRefine(scrollIndex, targetSlotPos)

		if player.REFINE_ALREADY_MAX_SOCKET_COUNT == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_NO_MORE_SOCKET)

		elif player.REFINE_NEED_MORE_GOOD_SCROLL == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_NEED_BETTER_SCROLL)

		elif player.REFINE_CANT_MAKE_SOCKET_ITEM == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_SOCKET_DISABLE_ITEM)

		elif player.REFINE_NOT_NEXT_GRADE_ITEM == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_UPGRADE_DISABLE_ITEM)

		elif player.REFINE_CANT_REFINE_METIN_TO_EQUIPMENT == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_EQUIP_ITEM)

		if player.REFINE_OK != result:
			return

		self.refineDialog.Open(scrollSlotPos, targetSlotPos)

	def DetachMetinFromItem(self, scrollSlotPos, targetSlotPos):
		scrollIndex = player.GetItemIndex(scrollSlotPos)
		targetIndex = player.GetItemIndex(targetSlotPos)

		if scrollIndex == 71109:
			if player.CanDetach(scrollIndex, targetSlotPos):
				self.__OpenQuestionDialog(scrollSlotPos, targetSlotPos)
			return

		if app.USE_ACCE_SYSTEM:
			if not player.CanDetach(scrollIndex, targetSlotPos):
				item.SelectItem(scrollIndex)
				if acce.IsCleanScroll(scrollIndex):
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.ACCE_FAILURE_CLEAN)
				else:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_METIN_INSEPARABLE_ITEM)

				return
		else:
			if not player.CanDetach(scrollIndex, targetSlotPos):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_METIN_INSEPARABLE_ITEM)
				return


		self.questionDialog = uicommon.QuestionDialog()
		self.questionDialog.SetText(localeinfo.REFINE_DO_YOU_SEPARATE_METIN)
		if app.USE_ACCE_SYSTEM:
			item.SelectItem(targetIndex)
			if item.GetItemType() == item.ITEM_TYPE_COSTUME and item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
				item.SelectItem(scrollIndex)
				if acce.IsCleanScroll(scrollIndex):
					self.questionDialog.SetText(localeinfo.ACCE_DO_YOU_CLEAN)



		self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnDetachMetinFromItem))
		self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
		self.questionDialog.Open()
		self.questionDialog.sourcePos = scrollSlotPos
		self.questionDialog.targetPos = targetSlotPos

	def AttachMetinToItem(self, metinSlotPos, targetSlotPos):
		metinIndex = player.GetItemIndex(metinSlotPos)
		targetIndex = player.GetItemIndex(targetSlotPos)

		item.SelectItem(metinIndex)
		itemName = item.GetItemName()

		result = player.CanAttachMetin(metinIndex, targetSlotPos)

		if player.ATTACH_METIN_NOT_MATCHABLE_ITEM == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_CAN_NOT_ATTACH(itemName))

		if player.ATTACH_METIN_NO_MATCHABLE_SOCKET == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_NO_SOCKET(itemName))

		elif player.ATTACH_METIN_NOT_EXIST_GOLD_SOCKET == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_NO_GOLD_SOCKET(itemName))

		elif player.ATTACH_METIN_CANT_ATTACH_TO_EQUIPMENT == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.REFINE_FAILURE_EQUIP_ITEM)

		if player.ATTACH_METIN_OK != result:
			return

		self.attachMetinDialog.Open(metinSlotPos, targetSlotPos)

	def OverOutItem(self):
		if self.wndItem:
			self.wndItem.SetUsableItem(False)

		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OverInItem(self, overSlotPos):
		overInvenSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(overSlotPos)
		self.wndItem.SetUsableItem(False)
		
		getItemVNum = player.GetItemIndex
		itemVnum = getItemVNum(overInvenSlotPos)
		if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
			self.DelHighlightSlot(overInvenSlotPos)
		
		if mousemodule.mouseController.isAttached():
			attachedItemType = mousemodule.mouseController.GetAttachedType()
			if player.SLOT_TYPE_INVENTORY == attachedItemType:
				attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
				attachedItemVNum = mousemodule.mouseController.GetAttachedItemIndex()
				
				if self.__CanUseSrcItemToDstItem(attachedItemVNum, attachedSlotPos, overInvenSlotPos):
					self.wndItem.SetUsableItem(True)
					self.ShowToolTip(overInvenSlotPos)
					return

		self.ShowToolTip(overInvenSlotPos)

	def __IsUsableItemToItem(self, srcItemVNum, srcSlotPos):
		if srcItemVNum == SOCKET_BLESS_ITEM_VNUM:
			return True
		if item.IsRefineScroll(srcItemVNum):
			return True
		elif app.ENABLE_SOUL_BIND_SYSTEM and item.IsSealScroll(srcItemVNum):
			return True
		elif app.ENABLE_67TH_BONUS and (srcItemVNum == item.ADD_RARE_ATTRIBUTE_VNUM or srcItemVNum == item.CHANGE_RARE_ATTRIBUTE_VNUM):
			return True
		elif item.IsMetin(srcItemVNum):
			return True
		elif item.IsDetachScroll(srcItemVNum):
			return True
		elif item.IsKey(srcItemVNum):
			return True
		elif item.IsItemUsedForDragonSoul(srcItemVNum):
			return True
		elif (player.GetItemFlags(srcSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
			if self.__CanRefundMetinStone(dstSlotPos):
				return True

			return False
		else:
			if app.ENABLE_GROWTH_PET_SYSTEM:
				if self.__IsUsablePetItem(srcItemVNum):
					return True
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if item.IsChangeLookClearScroll(srcItemVNum):
					return True
			if app.ENABLE_SET_ITEM:
				if item.IsSetItemScroll(srcItemVNum):
					return True

			if item.GetUseType(srcItemVNum) in self.USE_TYPE_TUPLE:
				return True

		return False

	def __CanUseSrcItemToDstItem(self, srcItemVNum, srcSlotPos, dstSlotPos):
		if srcSlotPos == dstSlotPos:
			return False

		if srcItemVNum == SOCKET_BLESS_ITEM_VNUM:
			return self.__CanBlessSocketItem(dstSlotPos)

		if item.IsRefineScroll(srcItemVNum):
			if player.REFINE_OK == player.CanRefine(srcItemVNum, dstSlotPos) or\
				player.GetItemIndex(dstSlotPos) == srcItemVNum:
				return True
		elif app.ENABLE_SOUL_BIND_SYSTEM and item.IsSealScroll(srcItemVNum):
			if player.CanSealItem(srcItemVNum, player.INVENTORY, dstSlotPos):
				return True
		elif item.IsMetin(srcItemVNum):
			if player.ATTACH_METIN_OK == player.CanAttachMetin(srcItemVNum, dstSlotPos):
				return True
		elif item.IsDetachScroll(srcItemVNum):
			if player.DETACH_METIN_OK == player.CanDetach(srcItemVNum, dstSlotPos):
				return True
		elif item.IsKey(srcItemVNum):
			if player.CanUnlock(srcItemVNum, dstSlotPos):
				return True
		elif app.ENABLE_67TH_BONUS and srcItemVNum == item.ADD_RARE_ATTRIBUTE_VNUM:
			if self.__CanAddRareItemAttr(dstSlotPos):
				return True
		elif app.ENABLE_67TH_BONUS and srcItemVNum == item.CHANGE_RARE_ATTRIBUTE_VNUM:
			if self.__CanChangeRareItemAttrList(dstSlotPos):
				return True
		else:

			useType = item.GetUseType(srcItemVNum)
			if "USE_CLEAN_SOCKET" == useType:
				if self.__CanCleanBrokenMetinStone(dstSlotPos):
					return True

				return False
			elif "USE_CHANGE_ATTRIBUTE" == useType:
				if srcItemVNum == 39929:
					return False

				if srcItemVNum == 39930:
					dstItemVNum = player.GetItemIndex(dstSlotPos)
					item.SelectItem(dstItemVNum)
					if item.GetItemType() != item.ITEM_TYPE_WEAPON:
						return False

				if self.__CanChangeItemAttrList(dstSlotPos):
					return True

				return False
			elif "USE_ADD_ATTRIBUTE" == useType:
				if self.__CanAddItemAttr(dstSlotPos):
					return True

				return False
			elif "USE_CHANGE_ATTRIBUTE2" == useType:
				if self.__CanChangeItemAttr67List(player.INVENTORY, dstSlotPos):
					return True

				return False#maybe remove ?
#			elif "USE_ADD_ATTRIBUTE2" == useType:
#				if self.__CanAddItemAttr2(dstSlotPos):
#					return True
#
#				return False
			elif "USE_ADD_ACCESSORY_SOCKET" == useType:
				if self.__CanAddAccessorySocket(dstSlotPos):
					return True

				return False
			elif "USE_PUT_INTO_ACCESSORY_SOCKET" == useType:
				if self.__CanPutAccessorySocket(dstSlotPos, srcItemVNum):
					return True

				return False
			elif "USE_PUT_INTO_BELT_SOCKET" == useType:
				dstItemVNum = player.GetItemIndex(dstSlotPos)
				item.SelectItem(dstItemVNum)

				if item.ITEM_TYPE_BELT == item.GetItemType():
					return True

				return False
			elif "USE_CHANGE_COSTUME_ATTR" == useType:
				if self.__CanChangeCostumeAttrList(dstSlotPos):
					return True

				return False
			elif "USE_RESET_COSTUME_ATTR" == useType:
				if self.__CanResetCostumeAttr(dstSlotPos):
					return True

				return False
			elif "USE_TIME_CHARGE_PER" == useType:
				if self.__CanExtendTime(dstSlotPos):
					return True

				return False
			elif "USE_TIME_CHARGE_FIX" == useType:
				if self.__CanExtendTime(dstSlotPos):
					return True

				return False
			elif app.USE_ENCHANT_COSTUMES and useType in ("USE_ENCHANT_BODY_COSTUME", "USE_ENCHANT_HAIR_COSTUME", "USE_ENCHANT_WEAPON_COSTUME", "USE_ENCHANT_MOUNT_SKIN", "USE_ENCHANT_PET_SKIN"):
				if self.CanEnchantCostume(useType,dstSlotPos):
					return True

				return False
			elif app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM and useType == "USE_SET_CUSTOM_ATTRIBUTE":
				if self.__CanSetCustomAttr(player.INVENTORY, dstSlotPos):
					return True

				return False
			elif app.USE_AURA_SYSTEM and not app.USE_AURA_ACCESSORY_SOCKET_RENEWED and useType == "USE_REMOVE_AURA_ATTR":
				if self.__CanRemoveAuraAttr(player.INVENTORY, dstSlotPos):
					return True

				return False
			elif app.USE_ENCHANT_COSTUMES and useType == "USE_REMOVE_COSTUME_ENCHANT":
				if self.__CanRemoveEnchants(player.INVENTORY, dstSlotPos):
					return True

				return False
			elif app.ENABLE_ATTR_6TH_7TH and useType == "USE_CHANGE_ATTRIBUTE2":
				if self.__CanChangeItemAttr67List(player.INVENTORY, dstSlotPos):
					return True

				return False
			elif "USE_REMOVE_ENCHANT" == useType:
				if self.__CanAddItemAttrNew(dstSlotPos):
					return True

				return False
			elif app.USE_AURA_SYSTEM and not app.USE_AURA_ACCESSORY_SOCKET_RENEWED and useType == "USE_PUT_INTO_AURA_SOCKET":
					if app.ENABLE_EXTEND_INVEN_SYSTEM:
						if item.ITEM_TYPE_COSTUME == player.GetItemTypeBySlot(dstSlotPos) and item.COSTUME_TYPE_AURA == player.GetItemSubTypeBySlot(dstSlotPos):
							if player.GetItemMetinSocket(dstSlotPos, player.ITEM_SOCKET_AURA_BOOST) == 0:
								return True
					else:
						dstItemVnum = player.GetItemIndex(dstSlotPos)
						item.SelectItem(dstItemVnum)
						if item.ITEM_TYPE_COSTUME == item.GetItemType() and item.COSTUME_TYPE_AURA == item.GetItemSubType():
							if player.GetItemMetinSocket(dstSlotPos, player.ITEM_SOCKET_AURA_BOOST) == 0:
								return True

					return False

			if app.ENABLE_GROWTH_PET_SYSTEM:
				if self.__CanUseSrcPetItemToDstPetItem(srcItemVNum, srcSlotPos, dstSlotPos):
					return True
				else:
					return False

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if player.CanChangeLookClearItem(srcItemVNum, player.INVENTORY, dstSlotPos):
					return True
				else:
					return False

			if app.ENABLE_SET_ITEM:
				if item.IsSetItemScroll(srcItemVNum):
					if player.CanSetItemClearItem(srcItemVNum, player.INVENTORY, dstSlotPos):
						return True
					else:
						return True

			if (player.GetItemFlags(srcSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
				return True
		
		return False

	if app.USE_ENCHANT_COSTUMES:
		def CanEnchantCostume(self,useType,dstSlotPos):
			dstItemVnum = player.GetItemIndex(dstSlotPos)
			if not dstItemVnum:
				return False
			
			if (player.GetItemFlags(dstSlotPos) & item.ITEM_CAN_BE_ENCHANTED) != item.ITEM_CAN_BE_ENCHANTED:
				return False
			
			item.SelectItem(dstItemVnum)
			
			if item.GetItemType() != item.ITEM_TYPE_COSTUME:
				return False
			
			allowDict={\
						item.COSTUME_TYPE_BODY:"USE_ENCHANT_BODY_COSTUME",
						item.COSTUME_TYPE_HAIR:"USE_ENCHANT_HAIR_COSTUME"
			}
			
			if app.USE_WEAPON_COSTUME_SYSTEM:
				allowDict[item.COSTUME_TYPE_WEAPON]="USE_ENCHANT_WEAPON_COSTUME"
			
			if app.USE_MOUNT_SKIN:
				allowDict[getattr(item, "COSTUME_TYPE_MOUNT_SKIN", -1)]="USE_ENCHANT_MOUNT_SKIN"
			
			if app.USE_PET_SKIN:
				allowDict[getattr(item, "COSTUME_TYPE_PET_SKIN", -2)]="USE_ENCHANT_PET_SKIN"
			
			itemSubType=item.GetItemSubType()
			
			if not allowDict.has_key(itemSubType):
				return False
			
			return allowDict[itemSubType]==useType

	if app.ENABLE_67TH_BONUS:
		def __CanAddRareItemAttr(self, dstSlotPos):
			dstItemVNum = player.GetItemIndex(dstSlotPos)
			if dstItemVNum == 0:
				return False

			item.SelectItem(dstItemVNum)

			if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
				return False

			attrCount = 0
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
					attrCount += 1

			if attrCount < player.ATTRIBUTE_SLOT_MAX_NUM and attrCount >= (player.ATTRIBUTE_SLOT_MAX_NUM - 2):
				return True

			return False

		def __CanChangeRareItemAttrList(self, dstSlotPos):
			dstItemVNum = player.GetItemIndex(dstSlotPos)
			if dstItemVNum == 0:
				return False

			item.SelectItem(dstItemVNum)

			if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
				return False

			attrCount = 0
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
					attrCount += 1

			if attrCount < player.ATTRIBUTE_SLOT_MAX_NUM and attrCount >= (player.ATTRIBUTE_SLOT_MAX_NUM - 2):
				return True

			return False

	if app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM:
		def __CanSetCustomAttr(self, dstSlotWindow, dstSlotPos):
			dstItemVnum = player.GetItemIndex(dstSlotWindow, dstSlotPos)
			if dstItemVnum == 0:
				return False

			item.SelectItem(dstItemVnum)
			if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
				return False

			if (item.GetItemType() == item.ITEM_TYPE_WEAPON and item.GetItemSubType() == item.WEAPON_ARROW) or \
				(app.ENABLE_QUIVER_SYSTEM and item.GetItemType() == item.ITEM_TYPE_WEAPON and item.GetItemSubType() == item.WEAPON_QUIVER) or \
				(app.USE_ACCE_SYSTEM and item.GetItemSubType() == item.ITEM_TYPE_COSTUME and item.GetItemSubType() == item.COSTUME_TYPE_ACCE):
				return False

			if player.IsAntiFlagBySlot(dstSlotWindow, dstSlotPos, item.ITEM_ANTIFLAG_ENCHANT):
				return False

			if app.ENABLE_SOUL_BIND_SYSTEM:
				if player.GetItemSealDate(dstSlotWindow, dstSlotPos) == -1 or player.GetItemSealDate(dstSlotWindow, dstSlotPos) > 0:
					return False

			attrCount = 0
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
					attrCount += 1

			if attrCount == 0:
				return True

			return False

	def AttachItemToDesc(self, useType, scrollSlotPos, targetSlotPos):
		bContinue = 0
		
		dlgText = ""

		if app.USE_AURA_SYSTEM and not app.USE_AURA_ACCESSORY_SOCKET_RENEWED and useType == "USE_REMOVE_AURA_ATTR":
			if self.__CanRemoveAuraAttr(player.INVENTORY, targetSlotPos):
				bContinue = 1
				dlgText = localeinfo.REMOVE_AURA_ATTR_DLG
		elif app.USE_ENCHANT_COSTUMES and\
			useType == "USE_REMOVE_COSTUME_ENCHANT":
			if self.__CanRemoveEnchants(player.INVENTORY, targetSlotPos):
				bContinue = 1
				dlgText = localeinfo.REMOVE_COSTUME_ENCHANT_DLG
		
		if bContinue == 0:
			return
		
		if mousemodule.mouseController.isAttached():
			mousemodule.mouseController.DeattachObject()
		
		if self.questionDialog:
			self.OnCloseQuestionDialog()
		
		questionDialog = uicommon.QuestionDialog()
		questionDialog.SetText(dlgText)
		questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnDetachMetinFromItem))
		questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
		questionDialog.Open()
		questionDialog.sourcePos = scrollSlotPos
		questionDialog.targetPos = targetSlotPos
		
		self.questionDialog = questionDialog

	if app.USE_AURA_SYSTEM and not app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
		def __CanRemoveAuraAttr(self, windowType, dstSlotPos):
			itemVnum = player.GetItemIndex(windowType, dstSlotPos)
			if not itemVnum:
				return False
			
			if app.ENABLE_SOUL_BIND_SYSTEM:
				if player.GetItemSealDate(windowType, dstSlotPos) == -1 or\
					player.GetItemSealDate(windowType, dstSlotPos) > 0:
					return False
			
			item.SelectItem(itemVnum)
			if item.GetItemType() != item.ITEM_TYPE_COSTUME:
				return False
			
			if item.GetItemSubType() != item.COSTUME_TYPE_AURA:
				return False
			
			socketInDrainItemVnum = player.GetItemMetinSocket(windowType, dstSlotPos, player.ITEM_SOCKET_AURA_DRAIN_ITEM_VNUM)
			if not socketInDrainItemVnum:
				return False
			
			return True

	if app.USE_ENCHANT_COSTUMES:
		def __CanRemoveEnchants(self, windowType, dstSlotPos):
			itemVnum = player.GetItemIndex(windowType, dstSlotPos)
			if not itemVnum:
				return False
			
			if app.ENABLE_SOUL_BIND_SYSTEM:
				if player.GetItemSealDate(windowType, dstSlotPos) == -1 or\
					player.GetItemSealDate(windowType, dstSlotPos) > 0:
					return False
			
			itemEnchantList=[player.GetItemEnchant(windowType, dstSlotPos, i) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]
			
			bReturn = False
			
			for i in xrange(player.ENCHANT_SLOT_MAX_NUM):
				a1, a2, a3 = player.GetItemEnchant(windowType, dstSlotPos, i)
				if a1 != 0:
					bReturn = True
					break
			
			return bReturn

	def __CanRefundMetinStone(self, dstSlotPos):
		dstItemVnum = player.GetItemIndex(dstSlotPos)
		if dstItemVnum == 0:
			return False

		item.SelectItem(dstItemVnum)

		itemType = item.GetItemType()
		itemSubType = item.GetItemSubType()

		if itemType == item.ITEM_TYPE_WEAPON:
			allowedSubTypes = (item.WEAPON_SWORD,\
								item.WEAPON_DAGGER,\
								item.WEAPON_BOW,\
								item.WEAPON_TWO_HANDED,\
								item.WEAPON_BELL,\
								item.WEAPON_FAN,\
								item.WEAPON_CLAW,)

			if itemSubType not in allowedSubTypes:
				return False
		elif itemType == item.ITEM_TYPE_ARMOR:
			allowedSubTypes = (item.ARMOR_BODY,)

			if app.USE_GLOVE_SYSTEM:
				allowedSubTypes += (item.ARMOR_GLOVE,)

			if itemSubType not in allowedSubTypes:
				return False

		if app.USE_GLOVE_SYSTEM and itemType == item.ITEM_TYPE_ARMOR and itemSubType == item.ARMOR_GLOVE:
			for i in xrange(player.METIN_SOCKET_MAX_NUM):
				if player.GetItemMetinSocket(dstSlotPos, i) >= 1000000:
					return True
		else:
			for i in xrange(player.METIN_SOCKET_MAX_NUM):
				value = player.GetItemMetinSocket(dstSlotPos, i)
				if value > 2 and value != constInfo.ERROR_METIN_STONE:
					return True

		return False

	def __CanBlessSocketItem(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)
		itemType = item.GetItemType()
		if itemType == item.ITEM_TYPE_WEAPON:
			return True
		elif itemType == item.ITEM_TYPE_ARMOR:
			allowedSubTypes = (item.ARMOR_BODY,)
			if app.USE_GLOVE_SYSTEM:
				allowedSubTypes += (item.ARMOR_GLOVE,)
			return item.GetItemSubType() in allowedSubTypes

		return False

	def __CanCleanBrokenMetinStone(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		itemType = item.GetItemType()
		if itemType == item.ITEM_TYPE_WEAPON:
			allowedSubTypes = (item.WEAPON_SWORD,\
								item.WEAPON_DAGGER,\
								item.WEAPON_BOW,\
								item.WEAPON_TWO_HANDED,\
								item.WEAPON_BELL,\
								item.WEAPON_FAN,\
								item.WEAPON_CLAW,)

			if item.GetItemSubType() not in allowedSubTypes:
				return False
		elif itemType == item.ITEM_TYPE_ARMOR:
			allowedSubTypes = (item.ARMOR_BODY,)

			if app.USE_GLOVE_SYSTEM:
				allowedSubTypes += (item.ARMOR_GLOVE,)

			if item.GetItemSubType() not in allowedSubTypes:
				return False

		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			if player.GetItemMetinSocket(dstSlotPos, i) == constInfo.ERROR_METIN_STONE:
				return True

		return False

	def __CanChangeItemAttrList(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
			return False

		attrCount = 0
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
				attrCount += 1

		if attrCount > 0:
			return True

		return False

	def __CanPutAccessorySocket(self, dstSlotPos, mtrlVnum):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		itemType = item.GetItemType()

		if itemType != item.ITEM_TYPE_ARMOR:
			if app.USE_AURA_SYSTEM and itemType == item.ITEM_TYPE_COSTUME and item.GetItemSubType() == item.COSTUME_TYPE_AURA and app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
				if mtrlVnum == item.ITEM_VNUM_AURA_ACCESORY_ADD:
					if player.GetItemMetinSocket(dstSlotPos, 0) < player.GetItemMetinSocket(dstSlotPos, 1):
						return True

			return False

		if not item.GetItemSubType() in (item.ARMOR_WRIST, item.ARMOR_NECK, item.ARMOR_EAR):
			return False

		curCount = player.GetItemMetinSocket(dstSlotPos, 0)
		maxCount = player.GetItemMetinSocket(dstSlotPos, 1)

		if mtrlVnum != constinfo.GET_ACCESSORY_MATERIAL_VNUM(dstItemVNum, item.GetItemSubType()):
			return False

		if curCount >= maxCount:
			return False

		return True

	def __CanAddAccessorySocket(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		itemType = item.GetItemType()
		if not itemType in (item.ITEM_TYPE_ARMOR, item.ITEM_TYPE_BELT):
			if app.USE_AURA_SYSTEM and itemType == item.ITEM_TYPE_COSTUME and item.GetItemSubType() == item.COSTUME_TYPE_AURA and app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
				if player.GetItemMetinSocket(dstSlotPos, 1) < 3:
					return True

			return False

		#if not item.GetItemSubType() in (item.ARMOR_WRIST, item.ARMOR_NECK, item.ARMOR_EAR):
		if not item.GetItemType() == item.ITEM_TYPE_BELT:
			if not item.GetItemSubType() in (item.ARMOR_WRIST, item.ARMOR_NECK, item.ARMOR_EAR):
				return False

		curCount = player.GetItemMetinSocket(dstSlotPos, 0)
		maxCount = player.GetItemMetinSocket(dstSlotPos, 1)

		ACCESSORY_SOCKET_MAX_SIZE = 3
		if maxCount >= ACCESSORY_SOCKET_MAX_SIZE:
			return False

		return True

	def __CanAddItemAttrNew(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
			return False

		attrCount = 0
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			# 2020.02.13.Owsap - Fix Attribute Count
			if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
				attrCount += 1

		if attrCount > 0:
			return True

		return False

	if app.ENABLE_ATTR_6TH_7TH:
		def __CanChangeItemAttr67List(self, dstSlotWindow, dstSlotPos):
			dstItemVNum = player.GetItemIndex(dstSlotWindow, dstSlotPos)
			if dstItemVNum == 0:
				return False

			item.SelectItem(dstItemVNum)

			if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
				return False

			attrCount = 0
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
					attrCount += 1

			if attrCount > player.ATTRIBUTE_SLOT_MAX_NUM - 2 and attrCount <= player.ATTRIBUTE_SLOT_MAX_NUM:
				return True

			return False

	def __CanAddItemAttr(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
			return False

		attrCount = 0
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			# 2020.02.13.Owsap - Fix Attribute Count
			if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
				attrCount += 1

		if attrCount < 4:
			return True

		return False

	# 2020.02.13.Owsap - Fix Attribute Count
	def __CanAddItemAttr2(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
			return False

		attrCount = 0
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
				attrCount += 1

		if attrCount == 4:
			return True

		return False

	def __CanChangeCostumeAttrList(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if item.GetItemType() != item.ITEM_TYPE_COSTUME:
			return False

		if app.USE_ACCE_SYSTEM:
			if item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
				return False

		if app.USE_MOUNT_COSTUME_SYSTEM:
			if item.GetItemSubType() == item.COSTUME_TYPE_MOUNT:
				return False

		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			type, value = player.GetItemAttribute(dstSlotPos, i)
			if type != 0:
				return True

		return False

	def __CanResetCostumeAttr(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if item.GetItemType() != item.ITEM_TYPE_COSTUME:
			return False

		if app.USE_ACCE_SYSTEM:
			if item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
				return False

		if app.USE_MOUNT_COSTUME_SYSTEM:
			if item.GetItemSubType() == item.COSTUME_TYPE_MOUNT:
				return False

		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			type, value = player.GetItemAttribute(dstSlotPos, i)
			if type != 0:
				return True

		return False

	def __CanExtendTime(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if app.ENABLE_COSTUME_EXTENDED_RECHARGE:
			if item.GetItemType() != item.ITEM_TYPE_COSTUME and item.GetItemType() != item.ITEM_TYPE_DS:
				return False

			if app.USE_ACCE_SYSTEM:
				if item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
					return False

			metinSlot = [player.GetItemMetinSocket(dstSlotPos, j) for j in xrange(player.METIN_SOCKET_MAX_NUM)]
			leftSec = max(0, metinSlot[0] - app.GetGlobalTimeStamp())

			if leftSec >= item.MIN_INFINITE_DURATION:
				return False
		else:
			if item.GetItemType() != item.ITEM_TYPE_DS:
				return False

		return True

	def ShowToolTip(self, slotIndex):
		if self.tooltipItem:
			vnum = player.GetItemIndex(slotIndex)
			if not vnum:
				return

			self.tooltipItem.SetInventoryItem(slotIndex)

			i = 0
			show = 0
			if app.ENABLE_INGAME_WIKI:
				if app.USE_MULTIPLE_OPENING:
					if vnum != 27987:
						view = item.CanBeMultipleOpened(vnum)
					else:
						view = 0
				else:
					item.SelectItem(vnum)
					view = 1 if vnum != 27987 and item.GetItemType() in (item.ITEM_TYPE_GIFTBOX, item.ITEM_TYPE_GACHA) else 0

				if view:
					self.tooltipItem.DeclareShortcut(("key_shift", "key_rclick"), localeinfo.TOOLTIP_VIEW_CHEST_CONTENT)
					i = 1

					if app.USE_MULTIPLE_OPENING:
						if player.GetItemCount(slotIndex) > 1:
							self.tooltipItem.DeclareShortcut(("key_ctrl", "key_rclick"), localeinfo.TOOLTIP_OPEN_ALL_CHETS)
				else:
					self.tooltipItem.DeclareShortcut(("key_shift", "key_rclick"), localeinfo.TOOLTIP_WIKI_HOVER)
					i = 1

			
			elif player.GetItemCount(slotIndex) > 1:
				if app.USE_MULTIPLE_OPENING and vnum != 27987:
					view = item.CanBeMultipleOpened(vnum)
					if view:
						self.tooltipItem.DeclareShortcut(("key_ctrl", "key_rclick"), localeinfo.TOOLTIP_OPEN_ALL_CHETS)
						i = 1

			if app.USE_OFFLINESHOP:
				if uiofflineshop_ae.IsBuildingShop():
					self.__AddTooltipSaleMode(slotIndex)
				else:
					self.tooltipItem.DeclareShortcut(("key_alt", "key_rclick"), localeinfo.TOOLTIP_QUICKSEARCH_OFFLINESHOP)

	if app.USE_OFFLINESHOP:
		def __AddTooltipSaleMode(self, slot):
			if player.IsEquipmentSlot(slot):
				return
			
			itemIndex = player.GetItemIndex(slot)
			if itemIndex !=0:
				item.SelectItem(itemIndex)
				if item.IsAntiFlag(item.ANTIFLAG_MYSHOP) or item.IsAntiFlag(item.ANTIFLAG_GIVE):
					return
				
				self.tooltipItem.AddRightClickForSale()

	def OnTop(self):
		if None != self.tooltipItem:
			self.tooltipItem.SetTop()

		if self.wndBelt:
			if self.IsClickBeltInventory == False:
				self.wndBelt.SetTop()
			else:
				self.IsClickBeltInventory = False

		if self.wndCostume:
			self.wndCostume.SetTop()

		if app.__RENEWAL_BRAVE_CAPE__ and self.wndBraveCape:
			if self.IsClickBraveCapeWindow == False:
				self.wndBraveCape.SetTop()
			else:
				self.IsClickBraveCapeWindow = False

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def UseItemSlot(self, slotIndex):
		curCursorNum = app.GetCursor()
		if app.SELL == curCursorNum:
			return
		elif constinfo.GET_ITEM_QUESTION_DIALOG_STATUS():
			return
		elif player.IsActingEmotion():
			return

		if app.USE_BL_FISH_EVENT:
			if mousemodule.mouseController.isAttached():
				if player.SLOT_TYPE_FISH_EVENT == mousemodule.mouseController.GetAttachedType():
					return

		slotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(slotIndex)

		if app.USE_ITEM_ATTR_BACKUP_MODE and player.GetItemBackup(player.INVENTORY, slotIndex):
			if self.interface:
				self.interface.OpenItemBackupAttr(player.INVENTORY, slotIndex)
			return

		# if app.QUICK_SELL_SYSTEM:
			# if app.IsPressed(app.DIK_TAB):
				# if slotIndex in constinfo.QUICK_SELL_ITEMS:
					# self.interface.RemoveSellSlot(slotIndex)
					# self.RefreshBagSlotWindow()
					# return
				# else:
					# self.interface.AppendSellSlot(slotIndex)
					# self.RefreshBagSlotWindow()
					# return


		if app.USE_OFFLINESHOP and uiofflineshop_ae.IsBuildingShop():
			itemIndex = player.GetItemIndex(slotIndex)
			if itemIndex:
				item.SelectItem(itemIndex)

				if not item.IsAntiFlag(item.ANTIFLAG_GIVE) and\
					not item.IsAntiFlag(item.ANTIFLAG_MYSHOP):
					offlineshop.ShopBuilding_AddItem(player.INVENTORY, slotIndex)
				else:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)

				return

		if self.wndDragonSoulRefine.IsShow():
			self.wndDragonSoulRefine.AutoSetItem((player.INVENTORY, slotIndex), 1)
			return

		if app.ITEM_CHECKINOUT_UPDATE:
			if player.IsOpenSafeBox() and slotIndex < player.EQUIPMENT_SLOT_START:
				net.SendSafeboxCheckinPacket(slotIndex)
				return

			if exchange.isTrading() and slotIndex < player.EQUIPMENT_SLOT_START:
				net.SendExchangeItemAddPacket(player.INVENTORY, slotIndex, -1)
				return

		if app.ENABLE_GEAR_SETS and slotIndex < player.EQUIPMENT_SLOT_START:
			# loadout window open -> right-click auto-links this item into the selected page (like safebox)
			if self.interface and self.interface.LinkFastEquipItemFromInventory(slotIndex):
				return

		if app.USE_ACCE_SYSTEM:
			if self.isShowAcceWindow():
				if app.ENABLE_SOUL_BIND_SYSTEM:
					if player.GetItemSealDate(player.INVENTORY, slotIndex) == -1 or player.GetItemSealDate(player.INVENTORY, slotIndex) > 0:
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.ACCE_NOT_SEALITEM)
						return
				
				acce.Add(player.INVENTORY, slotIndex, 255)
				return

		itemVnum = player.GetItemIndex(slotIndex)
		if not itemVnum:
			return

		# Clicking a skillbook handled by the auto skill reader opens that window
		# (Basic/Passive tab + preselect) instead of consuming the book.
		if app.__AUTO_SKILL_READER__:
			if self.interface and self.interface.TryOpenAutoSkillReaderForBook(itemVnum):
				mousemodule.mouseController.DeattachObject()
				self.OverOutItem()
				return

		# Shift+click on a horse-summon pony item opens the Horse Upgrade window.
		# Plain click still summons; the shortcut is opt-in via modifier.
		if app.ENABLE_HORSE_UPGRADE and (app.IsPressed(app.DIK_LSHIFT) or app.IsPressed(app.DIK_RSHIFT)):
			if itemVnum in (50051, 50052):
				if self.interface and hasattr(self.interface, "ToggleHorseUpgrade"):
					self.interface.ToggleHorseUpgrade()
				return

		# Location scroll modifiers must be tested BEFORE the offlineshop Alt handler and the
		# USE_MULTIPLE_OPENING Ctrl handler below, both of which would otherwise swallow the
		# keypress. Only location scrolls are diverted; every other item falls straight through.
		if app.ENABLE_LOCATION_SCROLL_REWORK and locationscroll.IsLocationScroll(itemVnum):
			if self.__LocationScrollModifier(slotIndex, itemVnum):
				mousemodule.mouseController.DeattachObject()
				self.OverOutItem()
				return

		if app.USE_OFFLINESHOP and\
			not uiofflineshop_ae.IsBuildingShop() and\
			(app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT)):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				wndShopOffline = interfaceHandler.wndShopOffline
				if wndShopOffline:
					wndSearchShop = wndShopOffline.wndSearchShop
					if wndSearchShop:
						item.SelectItem(itemVnum)
						wndSearchShop.SearchByName(item.GetItemName())
						return

		if app.USE_MULTIPLE_OPENING and (app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL)):
			if itemVnum > 0:
				itemCount = player.GetItemCount(slotIndex)
				if item.CanBeMultipleOpened(itemVnum) and itemCount > 1:
					net.SendMultipleOpening(player.INVENTORY, slotIndex, itemCount)
				else:
					self.__UseItem(slotIndex)
		else:
			self.__UseItem(slotIndex)

		mousemodule.mouseController.DeattachObject()
		self.OverOutItem()

	if app.ENABLE_LOCATION_SCROLL_REWORK:
		def __LocationScrollModifier(self, slotIndex, itemVnum):
			"""Returns True when a modifier consumed the click."""
			alt = app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT)
			ctrl = app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL)
			shift = app.IsPressed(app.DIK_LSHIFT) or app.IsPressed(app.DIK_RSHIFT)

			if not alt and not ctrl and not shift:
				return False

			metinSlot = [player.GetItemMetinSocket(slotIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
			(savedX, savedY) = locationscroll.GetSavedPosition(metinSlot)
			isSaved = bool(savedX or savedY)

			if alt and not isSaved:
				itemCount = player.GetItemCount(slotIndex)

				if itemCount <= 1:
					return False

				if not self.locScrollCountDialog:
					self.locScrollCountDialog = uicommon.PickItemDialog()
					self.locScrollCountDialog.SetAcceptEvent(ui.__mem_func__(self.__OnLocationScrollBulk))

				self.locScrollCountDialog.SetMax(min(itemCount, app.LOCATION_SCROLL_BULK_MAX))
				self.locScrollCountDialog.Open(slotIndex, min(itemCount, app.LOCATION_SCROLL_BULK_MAX))
				return True

			if not isSaved:
				return False

			if alt:
				# Re-save in one action: drop the old spot, then use the now-blank scroll.
				net.SendChatPacket("/memo_clear %d" % slotIndex)
				self.__UseItem(slotIndex)
				return True

			if ctrl:
				self.locScrollRenamePos = (savedX, savedY)

				if not self.locScrollRenameDialog:
					self.locScrollRenameDialog = uicommon.InputDialog()
					self.locScrollRenameDialog.SetAcceptEvent(ui.__mem_func__(self.__OnLocationScrollRename))
					self.locScrollRenameDialog.SetCancelEvent(ui.__mem_func__(self.__OnLocationScrollRenameClose))

				self.locScrollRenameDialog.SetTitle(getattr(localeinfo, "LOCSCROLL_RENAME_TITLE", "Name this location"))
				self.locScrollRenameDialog.SetMaxLength(app.LOCATION_SCROLL_NAME_MAX)
				self.locScrollRenameDialog.Open()
				return True

			if shift:
				self.locScrollClearSlot = slotIndex
				self.locScrollClearPos = (savedX, savedY)

				if not self.locScrollClearDialog:
					self.locScrollClearDialog = uicommon.QuestionDialog()
					self.locScrollClearDialog.SetAcceptEvent(ui.__mem_func__(self.__OnLocationScrollClearAccept))
					self.locScrollClearDialog.SetCancelEvent(ui.__mem_func__(self.__OnLocationScrollClearCancel))

				self.locScrollClearDialog.SetText(getattr(localeinfo, "LOCSCROLL_CLEAR_CONFIRM",
					"Clear the location saved on this scroll?"))
				self.locScrollClearDialog.Open()
				return True

			return False

		def __OnLocationScrollBulk(self, slotIndex, count, split = False):
			net.SendChatPacket("/memo_bulk %d %d" % (slotIndex, count))
			return True

		def __OnLocationScrollRename(self):
			if not self.locScrollRenameDialog:
				return True

			name = self.locScrollRenameDialog.GetText()
			(x, y) = self.locScrollRenamePos
			locationscroll.SetName(x, y, name)
			self.__OnLocationScrollRenameClose()
			return True

		def __OnLocationScrollRenameClose(self):
			if self.locScrollRenameDialog:
				self.locScrollRenameDialog.Close()
			return True

		def __OnLocationScrollClearAccept(self):
			net.SendChatPacket("/memo_clear %d" % self.locScrollClearSlot)
			(x, y) = self.locScrollClearPos
			locationscroll.ClearName(x, y)
			return self.__OnLocationScrollClearCancel()

		def __OnLocationScrollClearCancel(self):
			if self.locScrollClearDialog:
				self.locScrollClearDialog.Close()
			return True

	def __UseItem(self, slotIndex):
		if app.USE_AURA_SYSTEM:
			if player.IsAuraRefineWindowOpen():
				self.__UseItemAura(slotIndex)
				return


		ItemVNum = player.GetItemIndex(slotIndex)
		item.SelectItem(ItemVNum)

		_item_type = item.GetItemType()
		_item_sub_type = item.GetItemSubType()

		if ItemVNum == 70043 or ItemVNum == 72001 or ItemVNum == 72002 or ItemVNum == 72003 or \
		ItemVNum == 72004 or ItemVNum == 72005 or ItemVNum == 72006 or ItemVNum == 72049 or ItemVNum == 72050 or ItemVNum == 70005 :
			self.__UseItemExp(slotIndex)
			return

		if app.ENABLE_SKILL_LEARN_SYSTEM and ItemVNum == 88050:
			self.interface.OpenLearnSkillWindow()
			return

		if app.ENABLE_GROWTH_PET_SYSTEM:
			itemType = item.GetItemType()
			
			if self.interface.wndPetInfoWindow.AttachItemToPetWindow(player.INVENTORY, slotIndex):
				return
				
			if self.PetSkillDelDlg and self.PetSkillDelDlg.IsShow():
				self.__PetSkillDeleteQuestionDialogCancel()

			if item.ITEM_TYPE_PET == itemType:
				self.__UseItemPet(slotIndex)
				return

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if player.GetChangeLookWindowOpen() == 1:
				return

		if app.WJ_ENABLE_TRADABLE_ICON:
			if self.interface.AttachInvenItemToOtherWindowSlot(slotIndex):
				return

		if app.USE_OFFLINESHOP:
			if uiofflineshop_ae.IsBuildingShop() and\
				uiofflineshop_ae.IsSaleSlot(player.INVENTORY, slotIndex):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_CANT_SELECT_ITEM_DURING_BUILING)
				return

		if item.IsFlag(item.ITEM_FLAG_CONFIRM_WHEN_USE):
			self.questionDialog = uicommon.QuestionDialog()

			if app.USE_WEAR_STATS_SYSTEM and app.USE_GLOVE_SYSTEM and ItemVNum == item.ITEM_GLOVES_LICENSE_VNUM:
				self.questionDialog.SetText(localeinfo.INVENTORY_REALLY_USE_UNLOCK_GLOVES_SLOT)
			elif app.USE_DUNGEON_COUNT_LIMIT_DAILY and ItemVNum == item.ITEM_VNUM_DUNGEONS_COUNT_RESET:
				self.questionDialog.SetText(localeinfo.INVENTORY_REALLY_USE_RESET_ALL_DUNGEONS_COUNT)
			elif app.USE_PREMIUM_FEATURES and _item_type == item.ITEM_TYPE_USE and _item_sub_type == item.USE_PREMIUM_AFFECT:
				self.questionDialog.SetText(localeinfo.INVENTORY_REALLY_USE_PREMIUM_AFFECT)
			else:
				self.questionDialog.SetText(localeinfo.INVENTORY_REALLY_USE_ITEM2)

			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnAccept))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnCancel))
			self.questionDialog.Open()
			self.questionDialog.slotIndex = slotIndex

			constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)
			return

		if app.ENABLE_INGAME_WIKI and app.IsPressed(app.DIK_LSHIFT):
			if self.wndWiki:
				if app.USE_MULTIPLE_OPENING:
					if ItemVNum != 27987:
						view = item.CanBeMultipleOpened(ItemVNum)
				else:
					item.SelectItem(ItemVNum)
					view = 1 if ItemVNum != 27987 and item.GetItemType() in (item.ITEM_TYPE_GIFTBOX, item.ITEM_TYPE_GACHA) else 0


				if not self.wndWiki.IsShow():
					net.ToggleWikiWindow()

				self.wndWiki.CloseBaseWindows()
				if view:
					self.wndWiki.mainChestWindow.Show([ItemVNum,])
				else:
					self.wndWiki.OpenSpecialPage(None, ItemVNum, False)
					#self.wndWiki.GetBaseClass().GoToCustomPage("guides/95-105.txt")
				return


		if ItemVNum == 72327 or ItemVNum == 72329 or ItemVNum == 72328 and app.ENABLE_12ZI:
			self.questionDialog = uicommon.QuestionDialog()
			self.questionDialog.SetText(self.GetConfirmQuestion(ItemVNum))
			(width, height) = self.questionDialog.GetTextSize()
			self.questionDialog.SetWidth(width+16)
			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnAccept))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnCancel))
			self.questionDialog.Open()
			self.questionDialog.slotIndex = slotIndex

			constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)
		else:
			self.__SendUseItemPacket(slotIndex)
			#net.SendItemUsePacket(slotIndex)

	if app.ENABLE_12ZI:
		def GetConfirmQuestion(self, vnum):
			item.SelectItem(vnum)
			if vnum == 72327 or vnum == 72329:
				return localeinfo.CHARGE_BEAD_QUESTION % (item.GetValue(0))
			elif vnum == 72328:
				return localeinfo.UNLIMIT_ENTER_CZ_QUESTION % (item.GetValue(0))
			else:
				return localeinfo.INVENTORY_REALLY_USE_ITEM2

	def __UseItemQuestionDialog_OnCancel(self):
		self.OnCloseQuestionDialog()

	def __UseItemQuestionDialog_OnAccept(self):
		self.__SendUseItemPacket(self.questionDialog.slotIndex)
		self.OnCloseQuestionDialog()

	def __SendUseItemToItemPacket(self, srcSlotPos, dstSlotPos):
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.USE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		if self.interface.IsShowDlgQuestionWindow():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
			return

		net.SendItemUseToItemPacket(srcSlotPos, dstSlotPos)

	def __SendUseItemPacket(self, slotPos):
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.USE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		if self.interface.IsShowDlgQuestionWindow():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
			return

		net.SendItemUsePacket(slotPos)

	def __SendMoveItemPacket(self, srcSlotPos, dstSlotPos, srcItemCount):
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.MOVE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		if self.interface.IsShowDlgQuestionWindow():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
			return

		net.SendItemMovePacket(srcSlotPos, dstSlotPos, srcItemCount)

	def SetDragonSoulRefineWindow(self, DragonSoulRefine):
		self.wndDragonSoulRefine = proxy(DragonSoulRefine)

	def AdjustPosition(self, x, y, bCape):
		# if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			# self.SetPosition(x + 172, y - 229)
		# else:
		self.SetPosition(x, y)

		if self.wndBelt:
			self.wndBelt.AdjustPositionAndSize()

		if app.__RENEWAL_BRAVE_CAPE__ and self.wndBraveCape:
			self.wndBraveCape.AdjustPosition()

		if self.wndEquipmentTab:
			self.wndEquipmentTab.AdjustPosition()

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("inventory_window", x, y)

		if self.wndBelt:
			self.wndBelt.AdjustPositionAndSize()

		# if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			# interfaceHandler = systemSetting.GetInterfaceHandler()
			# if interfaceHandler and interfaceHandler.wndSpecialInventory and interfaceHandler.wndSpecialInventory.IsShow():
				# (x, y) = self.GetGlobalPosition()
				# interfaceHandler.wndSpecialInventory.AdjustPosition(x, y)

		if app.__RENEWAL_BRAVE_CAPE__ and self.wndBraveCape:
			self.wndBraveCape.AdjustPosition()

		if self.wndEquipmentTab:
			self.wndEquipmentTab.AdjustPosition()

	## HilightSlot Change
	def DeactivateSlot(self, slotindex, type):
		if type == wndMgr.HILIGHTSLOT_MAX:
			return
		
		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if type == wndMgr.HILIGHTSLOT_CHANGE_LOOK:
				self.__DelHighlightSlotChangeLook(slotindex)

	## HilightSlot Change
	def ActivateSlot(self, slotindex, type):
		if type == wndMgr.HILIGHTSLOT_MAX:
			return
		
		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if type == wndMgr.HILIGHTSLOT_CHANGE_LOOK:
				self.__AddHighlightSlotChangeLook(slotindex)

	if app.ENABLE_CHANGE_LOOK_SYSTEM:
		def __AddHighlightSlotChangeLook(self, slotIndex):
			if not slotIndex in self.listHighlightedChangeLookSlot:
				self.listHighlightedChangeLookSlot.append(slotIndex)

		def __DelHighlightSlotChangeLook(self, slotIndex):
			if slotIndex in self.listHighlightedChangeLookSlot:
				if slotIndex >= player.INVENTORY_PAGE_SIZE:
					self.wndItem.DeactivateSlot(slotIndex - (self.inventoryPageIndex * player.INVENTORY_PAGE_SIZE))
					self.wndItem.SetCanMouseEventSlot(slotIndex - (self.inventoryPageIndex * player.INVENTORY_PAGE_SIZE))
				else:
					self.wndItem.DeactivateSlot(slotIndex)
					self.wndItem.SetCanMouseEventSlot(slotIndex)
				self.listHighlightedChangeLookSlot.remove(slotIndex)

	def __HighlightSlot_Refresh(self):
		for i in xrange(self.wndItem.GetSlotCount()):
			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
			
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if slotNumber in self.listHighlightedChangeLookSlot:
					self.wndItem.ActivateSlot(i)
					self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_RED)
					self.wndItem.SetCantMouseEventSlot(i)

			## HilightSlot Change
			if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
				if slotNumber in self.listHighlightedSlot:
					self.wndItem.ActivateSlot(i)

	def __HighlightSlot_Clear(self):
		for i in xrange(self.wndItem.GetSlotCount()):
			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
			
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if slotNumber in self.listHighlightedChangeLookSlot:
					self.wndItem.DeactivateSlot(i)
					self.wndItem.SetCanMouseEventSlot(i)
					self.listHighlightedChangeLookSlot.remove(slotNumber)
			
			if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
				if slotNumber in self.listHighlightedSlot:
					self.wndItem.DeactivateSlot(i)
					self.listHighlightedSlot.remove(slotNumber)

	if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
		def HighlightSlot(self, slot):
			if slot > player.INVENTORY_PAGE_SIZE * player.INVENTORY_PAGE_COUNT:
				return

			if not slot in self.listHighlightedSlot:
				self.listHighlightedSlot.append(slot)

		def DelHighlightSlot(self, inventorylocalslot):
			if inventorylocalslot in self.listHighlightedSlot:
				if inventorylocalslot >= player.INVENTORY_PAGE_SIZE:
					self.wndItem.DeactivateSlot(inventorylocalslot - (self.inventoryPageIndex * player.INVENTORY_PAGE_SIZE))
				else:
					self.wndItem.DeactivateSlot(inventorylocalslot)

				self.listHighlightedSlot.remove(inventorylocalslot)

	def IsDlgQuestionShow(self):
		if self.dlgQuestion.IsShow():
			return True
		else:
			return False

	def CancelDlgQuestion(self):
		self.__Cancel()

	def SetUseItemMode(self, bUse):
		self.wndItem.SetUseMode(bUse)

	def GetInventoryPageIndex(self):
		return self.inventoryPageIndex

	if app.USE_ACCE_SYSTEM:
		def SetAcceWindow(self, wndAcceCombine, wndAcceAbsorption):
			self.wndAcceCombine = wndAcceCombine
			self.wndAcceAbsorption = wndAcceAbsorption

		def isShowAcceWindow(self):
			if self.wndAcceCombine:
				if self.wndAcceCombine.IsShow():
					return 1

			if self.wndAcceAbsorption:
				if self.wndAcceAbsorption.IsShow():
					return 1

			return 0

	def __UseItemExp(self, slotIndex):
		if player.IsEquipmentSlot(slotIndex):
			self.questionDialog = uicommon.QuestionDialog()
			self.questionDialog.SetText(localeinfo.EXP_REMOVE_ALERT)

			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnAccept))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnCancel))
			self.questionDialog.Open()
			self.questionDialog.slotIndex = slotIndex
			constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)
		else:
			self.questionDialog = uicommon.QuestionDialog()
			self.questionDialog.SetText(localeinfo.EXP_WEAR_ALERT)

			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnAccept))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnCancel))
			self.questionDialog.Open()
			self.questionDialog.slotIndex = slotIndex
			constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	if app.ENABLE_GROWTH_PET_SYSTEM:
		def __UseItemPet(self, slotIndex):
			itemSubType = item.GetItemSubType()
			if item.PET_EGG == itemSubType:
				self.petHatchingWindow.HatchingWindowOpen(player.INVENTORY, slotIndex)
				
			elif item.PET_UPBRINGING == itemSubType:
				if self.__CanUseGrowthPet(slotIndex):
					self.__SendUseItemPacket(slotIndex)
						
			elif item.PET_BAG == itemSubType:
				if self.__CanUsePetBagItem(slotIndex):
					if self.questionDialog:
						self.questionDialog.Close()
						
					self.questionDialog = uicommon.QuestionDialog()
					self.questionDialog.SetText(localeinfo.INVENTORY_REALLY_USE_PET_BAG_TAKE_OUT)
					self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnAccept))
					self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnCancel))
					self.questionDialog.slotIndex = slotIndex
					self.questionDialog.Open()

			elif item.PET_STAT_POTION == itemSubType:
				# Growth-pet stat potion: forward to server; it validates (pet summoned/alive, caps) and replies.
				self.__SendUseItemPacket(slotIndex)

			elif item.PET_FEEDSTUFF == itemSubType:
				# Growth-pet charge item: CONFIRM first, telling the player how much lifetime
				# the item gives (proto value0 days, 3 when unset; the server caps remaining
				# time at 30 days). Accept -> use packet; the server charges the SUMMONED pet
				# or revives an expired one. Dragging onto a pet item still covers the rest.
				chargeDays = item.GetValue(0)
				if chargeDays <= 0:
					chargeDays = 3
				if self.questionDialog:
					self.questionDialog.Close()
				self.questionDialog = uicommon.QuestionDialog()
				self.questionDialog.SetText(getattr(localeinfo, "COMPANION_PET_CHARGE_QUESTION", "Give your pet %s day(s) of lifetime?") % chargeDays)
				self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnAccept))
				self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnCancel))
				self.questionDialog.slotIndex = slotIndex
				self.questionDialog.Open()

			if item.PET_SKILL_ALL_DEL_BOOK == itemSubType:
				pet_id = player.GetActivePetItemId()
				if 0 == pet_id:
					return
				(skill_count, pet_skill1, pet_skill_level1, pet_skill_cool1, pet_skill2, pet_skill_level2, pet_skill_cool2, pet_skill3, pet_skill_level3, pet_skill_cool3) = player.GetPetSkill(pet_id)
				if 0 == pet_skill1 and 0 == pet_skill2 and 0 == pet_skill3:
					popup = uicommon.PopupDialog()
					popup.SetText(localeinfo.PET_EMPTY_SKILL_SLOT_USE_ITEM)
					popup.SetAcceptEvent(self.__OnClosePopupDialog)
					popup.Open()
					self.pop = popup
					return
			
				self.PetSkillAllDelBookIndex = slotIndex
				self.SetCantMouseEventSlot( self.PetSkillAllDelBookIndex )
				
				self.PetSkillDelDlg.SetAcceptEvent(ui.__mem_func__(self.__PetSkillDeleteQuestionDialogAccept))
				self.PetSkillDelDlg.SetCancelEvent(ui.__mem_func__(self.__PetSkillDeleteQuestionDialogCancel))
				
				self.PetSkillDelDlg.SetText1( localeinfo.PET_SKILL_DELETE_QUESTION_DLG_MSG1 )
				self.PetSkillDelDlg.SetText2( localeinfo.PET_SKILL_DELETE_QUESTION_DLG_MSG2 )
				(w,h) = self.PetSkillDelDlg.GetTextSize1()
				self.PetSkillDelDlg.SetWidth(w+100)
				self.PetSkillDelDlg.Open()
				
		def __OnClosePopupDialog(self):
			self.pop = None

		def __ActivePetHighlightSlot(self, slotNumber):
			active_id = player.GetActivePetItemId()
			if active_id == player.GetItemMetinSocket(player.INVENTORY, slotNumber, 2):
				if slotNumber >= player.INVENTORY_PAGE_SIZE:
					slotNumber -= (self.inventoryPageIndex * player.INVENTORY_PAGE_SIZE)

				self.wndItem.ActivateSlot(slotNumber)
				return 1
			else:
				if slotNumber >= player.INVENTORY_PAGE_SIZE:
					slotNumber -= (self.inventoryPageIndex * player.INVENTORY_PAGE_SIZE)

				self.wndItem.DeactivateSlot(slotNumber)
				return 0

		def __SetCoolTimePetItemSlot(self, slotNumber, itemVnum):
		
			item.SelectItem(itemVnum)
			itemSubType = item.GetItemSubType()
		
			if itemSubType not in [item.PET_UPBRINGING, item.PET_BAG]:
				return
				
			if itemSubType == item.PET_BAG:
				id = player.GetItemMetinSocket(player.INVENTORY, slotNumber, 2)
				if id == 0:
					return
			
			(limitType, limitValue) = item.GetLimit(0)

			if itemSubType == item.PET_UPBRINGING:
				limitValue = player.GetItemMetinSocket(player.INVENTORY, slotNumber, 1)
					
			if limitType in [item.LIMIT_REAL_TIME, item.LIMIT_REAL_TIME_START_FIRST_USE]:
								
				sock_time   = player.GetItemMetinSocket(player.INVENTORY, slotNumber, 0)
				
				remain_time = max(0, sock_time - app.GetGlobalTimeStamp())
			
				if slotNumber >= player.INVENTORY_PAGE_SIZE:
					slotNumber -= (self.inventoryPageIndex * player.INVENTORY_PAGE_SIZE)

				self.wndItem.SetSlotCoolTimeInverse(slotNumber, limitValue, limitValue - remain_time)

		def __IsPetItem(self, srcItemVID):
			item.SelectItem(srcItemVID)
			
			if item.GetItemType() == item.ITEM_TYPE_PET:
				return True
			
			return False

		def __SendUsePetItemToItemPacket(self, srcItemVID, srcItemSlotPos, dstItemSlotPos):
			if self.__CanUseSrcPetItemToDstPetItem(srcItemVID, srcItemSlotPos, dstItemSlotPos):
				srcItemVnum		= player.GetItemIndex(srcItemSlotPos)
				item.SelectItem( srcItemVnum )
				srcItemType		= item.GetItemType()
				srcItemSubType	= item.GetItemSubType()
				
				if item.ITEM_TYPE_PET == srcItemType:					
					if srcItemSubType in [item.PET_FEEDSTUFF, item.PET_BAG]:
						self.__OpenPetItemQuestionDialog(srcItemSlotPos, dstItemSlotPos)
					elif item.PET_NAME_CHANGE == srcItemSubType:
						self.__UseItemPetNameChange(srcItemSlotPos, dstItemSlotPos)
				return True
				
			return False
			
		def __UseItemPetNameChange(self, srcSlotPos, dstSlotPos):
			if self.petNameChangeWindow:
				self.petNameChangeWindow.NameChangeWindowOpen(srcSlotPos, dstSlotPos)

		def __IsUsablePetItem(self, srcItemVNum):
			item.SelectItem(srcItemVNum)
			srcItemType		= item.GetItemType()
			srcItemSubType	= item.GetItemSubType()

			if srcItemType != item.ITEM_TYPE_PET:
				return False
			
			if srcItemSubType not in [item.PET_UPBRINGING, item.PET_FEEDSTUFF, item.PET_BAG, item.PET_NAME_CHANGE]:
				return False
			
			return True

		def __CanUseSrcPetItemToDstPetItem(self, srcItemVNum, srcSlotPos, dstSlotPos):
			item.SelectItem(srcItemVNum)
			srcItemType		= item.GetItemType()
			srcItemSubType	= item.GetItemSubType()
			
			if srcItemType != item.ITEM_TYPE_PET:
				return False
			
			if srcItemSubType == item.PET_FEEDSTUFF:		
				detIndex = player.GetItemIndex(dstSlotPos)
				item.SelectItem(detIndex)
				
				dstItemType		= item.GetItemType()
				dstItemSubType	= item.GetItemSubType()
				
				if dstItemType != item.ITEM_TYPE_PET:
					return False
					
				if dstItemSubType not in [item.PET_UPBRINGING]:
					return False
					
				if dstItemSubType == item.PET_BAG:
					incaseTime = player.GetItemMetinSocket(dstSlotPos, 1)
					if incaseTime == 0:
						return False
			
			elif srcItemSubType == item.PET_BAG:
				detIndex = player.GetItemIndex(dstSlotPos)
				item.SelectItem(detIndex)
				
				dstItemType		= item.GetItemType()
				dstItemSubType	= item.GetItemSubType()
				
				if dstItemType != item.ITEM_TYPE_PET:
					return False
					
				if dstItemSubType not in [item.PET_UPBRINGING, item.PET_BAG]:
					return False
			
				lifeTime = player.GetItemMetinSocket(dstSlotPos, 0)
					
				if dstItemSubType == item.PET_UPBRINGING:
					if lifeTime < app.GetGlobalTimeStamp():
						return False

					srcIncase = player.GetItemMetinSocket(srcSlotPos, 1)
					if srcIncase != 0:
						return False
					
				elif dstItemSubType == item.PET_BAG:
					if lifeTime > app.GetGlobalTimeStamp():
						return False
						
					srcIncase = player.GetItemMetinSocket(srcSlotPos, 1)
					if srcIncase != 0:
						return False
					
					destIncase = player.GetItemMetinSocket(dstSlotPos, 1)
					if destIncase == 0:
						return False
						
			elif srcItemSubType == item.PET_NAME_CHANGE:
				detIndex = player.GetItemIndex(dstSlotPos)
				item.SelectItem(detIndex)
				
				dstItemType		= item.GetItemType()
				dstItemSubType	= item.GetItemSubType()
				
				if dstItemType != item.ITEM_TYPE_PET:
					return False
					
				if dstItemSubType not in [item.PET_UPBRINGING]:
					return False
					
			else:
				return False
			
			return True

		def __CanUseGrowthPet(self, slotIndex):
			if not player.GetItemMetinSocket(player.INVENTORY, slotIndex, 2):
				return False
				
			(limitType, limitValue) = item.GetLimit(0)
			remain_time = 999
			if item.LIMIT_REAL_TIME == limitType:
				sock_time   = player.GetItemMetinSocket(player.INVENTORY, slotIndex, 0)
				if app.GetGlobalTimeStamp() > sock_time:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_SUMMON_BECAUSE_LIFE_TIME_END)
					return False
					
			return True

		def __CanUsePetBagItem(self, slotIndex):
			if not player.GetItemMetinSocket(player.INVENTORY, slotIndex, 2):
				return False
				
			(limitType, limitValue) = item.GetLimit(0)
			remain_time = 999
			if item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
				sock_time   = player.GetItemMetinSocket(player.INVENTORY, slotIndex, 0)
				use_cnt	    = player.GetItemMetinSocket(player.INVENTORY, slotIndex, 1)
				
				if use_cnt:
					if app.GetGlobalTimeStamp() > sock_time:
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_USE_BAG)
						return False;
						
			return True

		def __CanAttachGrowthPetItem(self, itemVNum, itemSlotIndex):
			activePetId = player.GetActivePetItemId()
			if activePetId == 0:
				return True
			
			item.SelectItem(itemVNum)
			itemType	= item.GetItemType()
			itemSubType = item.GetItemSubType()
			
			if item.ITEM_TYPE_PET == itemType and itemSubType == item.PET_UPBRINGING:
				petId = player.GetItemMetinSocket(itemSlotIndex, 2)
				if petId == activePetId:
					return False
					
					
			return True

		def SetPetHatchingWindow(self, window):
			self.petHatchingWindow = window

		def SetPetNameChangeWindow(self, window):
			self.petNameChangeWindow = window

		def SetPetFeedWindow(self, window):
			self.petFeedWindow = window

		def ItemMoveFeedWindow(self, slotWindow, slotIndex):
			if not self.petFeedWindow:
				return
				
			self.petFeedWindow.ItemMoveFeedWindow(slotWindow, slotIndex)

		def __OpenPetBagQuestionDialog(self, srcItemSlotPos, dstItemSlotPos):
			if self.interface.IsShowDlgQuestionWindow():
				self.interface.CloseDlgQuestionWindow()

		def __OpenPetItemQuestionDialog(self, srcItemPos, dstItemPos):
			if self.interface.IsShowDlgQuestionWindow():
				self.interface.CloseDlgQuestionWindow()
			
			getItemVNum=player.GetItemIndex
			self.srcItemPos = srcItemPos
			self.dstItemPos = dstItemPos

			srcItemVnum = getItemVNum(srcItemPos)
			dstItemVnum = getItemVNum(dstItemPos)
			
			item.SelectItem( srcItemVnum )
			src_item_name = item.GetItemName( srcItemVnum )
			srcItemType		= item.GetItemType()
			srcItemSubType	= item.GetItemSubType()
			
			item.SelectItem( dstItemVnum )
			dst_item_name = item.GetItemName( getItemVNum(dstItemPos) )
			
			self.PetItemQuestionDlg.SetAcceptEvent(ui.__mem_func__(self.__PetItemAccept))
			self.PetItemQuestionDlg.SetCancelEvent(ui.__mem_func__(self.__PetItemCancel))
			
			if item.ITEM_TYPE_PET == srcItemType:
				if item.PET_FEEDSTUFF == srcItemSubType:
					self.PetItemQuestionDlg.SetText( localeinfo.INVENTORY_REALLY_USE_PET_FEEDSTUFF_ITEM % ( src_item_name, dst_item_name ) )
					self.PetItemQuestionDlg.Open()
				
				elif item.PET_BAG == srcItemSubType:
					self.PetItemQuestionDlg.SetText( localeinfo.INVENTORY_REALLY_USE_PET_BAG_ITEM )
					self.PetItemQuestionDlg.Open()			
				
		def __PetItemAccept(self):
			self.PetItemQuestionDlg.Close()
			self.__SendUseItemToItemPacket(self.srcItemPos, self.dstItemPos)
			self.srcItemPos = (0, 0)
			self.dstItemPos = (0, 0)
			self.srcItemWindow = None
			self.dstItemWindow = None

		def __PetItemCancel(self):
			self.srcItemPos = (0, 0)
			self.dstItemPos = (0, 0)
			self.PetItemQuestionDlg.Close()

		def __PetSkillDeleteQuestionDialogAccept(self):
			net.SendPetDeleteAllSkill( self.PetSkillAllDelBookIndex )	
			self.__PetSkillDeleteQuestionDialogCancel()
			
		def __PetSkillDeleteQuestionDialogCancel(self):
			self.PetSkillDelDlg.Close()
			self.SetCanMouseEventSlot( self.PetSkillAllDelBookIndex )
			self.PetSkillAllDelBookIndex = -1
			
		def SetCanMouseEventSlot(self, inven_slot_index):
			if inven_slot_index >= player.INVENTORY_PAGE_SIZE:
				page = self.GetInventoryPageIndex()
				inven_slot_index -= (page * player.INVENTORY_PAGE_SIZE)
			
			self.wndItem.SetCanMouseEventSlot(inven_slot_index)

		def SetCantMouseEventSlot(self, inven_slot_index):
			if inven_slot_index >= player.INVENTORY_PAGE_SIZE:
				page = self.GetInventoryPageIndex() # range 0,1,2,3
				inven_slot_index -= (page * player.INVENTORY_PAGE_SIZE)
			self.wndItem.SetCantMouseEventSlot(inven_slot_index)

	if app.USE_AURA_SYSTEM:
		def __UseItemAuraQuestionDialog_OnAccept(self):
			self.questionDialog.Close()
			net.SendAuraRefineCheckIn(*(self.questionDialog.srcItem + self.questionDialog.dstItem + (player.GetAuraRefineWindowType(),)))
			self.questionDialog.srcItem = (0, 0)
			self.questionDialog.dstItem = (0, 0)

		def __UseItemAuraQuestionDialog_Close(self):
			self.questionDialog.Close()

			self.questionDialog.srcItem = (0, 0)
			self.questionDialog.dstItem = (0, 0)

		def __UseItemAura(self, slotIndex):
			AuraSlot = player.FineMoveAuraItemSlot()
			UsingAuraSlot = player.FindActivatedAuraSlot(player.INVENTORY, slotIndex)
			AuraVnum = player.GetItemIndex(slotIndex)
			item.SelectItem(AuraVnum)
			if player.GetAuraCurrentItemSlotCount() >= player.AURA_SLOT_MAX <= UsingAuraSlot:
				return

			if player.IsEquipmentSlot(slotIndex):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_IMPOSSIBLE_EQUIPITEM)
				return

			if app.ENABLE_SOUL_BIND_SYSTEM:
				if player.GetItemSealDate(player.INVENTORY, slotIndex) == -1 or player.GetItemSealDate(player.INVENTORY, slotIndex) > 0:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_IMPOSSIBLE_SEALITEM)
					return

			if player.GetAuraRefineWindowType() == player.AURA_WINDOW_TYPE_ABSORB:
				isAbsorbItem = False
				if item.GetItemType() == item.ITEM_TYPE_COSTUME:
					if item.GetItemSubType() == item.COSTUME_TYPE_AURA:
						if player.GetItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_DRAIN_ITEM_VNUM) == 0:
							if UsingAuraSlot == player.AURA_SLOT_MAX:
								if AuraSlot != player.AURA_SLOT_MAIN:
									return

								net.SendAuraRefineCheckIn(player.INVENTORY, slotIndex, player.AURA_REFINE, AuraSlot, player.GetAuraRefineWindowType())

						else:
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_IMPOSSIBLE_ABSORBITEM)
							return

					else:
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_IMPOSSIBLE_ABSORBITEM)
						return

				elif item.GetItemType() == item.ITEM_TYPE_ARMOR:
					if item.GetItemSubType() in [item.ARMOR_SHIELD, item.ARMOR_WRIST, item.ARMOR_NECK, item.ARMOR_EAR]:
						if player.FindUsingAuraSlot(player.AURA_SLOT_MAIN) == player.NPOS():
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_POSSIBLE_REGISTER_AURAITEM)
							return

						isAbsorbItem = True
					else:
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_IMPOSSIBLE_ABSORBITEM)
						return

				else:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_IMPOSSIBLE_ABSORBITEM)
					return

				if isAbsorbItem:
					if UsingAuraSlot == player.AURA_SLOT_MAX:
						if AuraSlot != player.AURA_SLOT_SUB:
							if player.FindUsingAuraSlot(player.AURA_SLOT_SUB) == player.NPOS():
								AuraSlot = player.AURA_SLOT_SUB
							else:
								return

						self.questionDialog = uicommon.QuestionDialog()
						self.questionDialog.SetText(localeinfo.AURA_NOTICE_DEL_ABSORDITEM)
						self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemAuraQuestionDialog_OnAccept))
						self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemAuraQuestionDialog_Close))
						self.questionDialog.srcItem = (player.INVENTORY, slotIndex)
						self.questionDialog.dstItem = (player.AURA_REFINE, AuraSlot)
						self.questionDialog.Open()

			elif player.GetAuraRefineWindowType() == player.AURA_WINDOW_TYPE_GROWTH:
				if UsingAuraSlot == player.AURA_SLOT_MAX:
					if AuraSlot == player.AURA_SLOT_MAIN:
						if item.GetItemType() == item.ITEM_TYPE_COSTUME:
							if item.GetItemSubType() == item.COSTUME_TYPE_AURA:
								socketLevelValue = player.GetItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_CURRENT_LEVEL)
								curLevel = (socketLevelValue / 100000) - 1000
								curExp = socketLevelValue % 100000;
								if curLevel >= player.AURA_MAX_LEVEL:
									chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_MAX_LEVEL)
									return

								if curExp >= player.GetAuraRefineInfo(curLevel, player.AURA_REFINE_INFO_NEED_EXP):
									chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_IMPOSSIBLE_GROWTHITEM)
									return

								net.SendAuraRefineCheckIn(player.INVENTORY, slotIndex, player.AURA_REFINE, AuraSlot, player.GetAuraRefineWindowType())

							else:
								chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_POSSIBLE_AURAITEM)
								return

						else:
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_POSSIBLE_AURAITEM)
							return

					elif AuraSlot == player.AURA_SLOT_SUB:
						if player.FindUsingAuraSlot(player.AURA_SLOT_MAIN) != player.NPOS():
							if item.GetItemType() == item.ITEM_TYPE_RESOURCE:
								if item.GetItemSubType() == item.RESOURCE_AURA:
									if UsingAuraSlot == player.AURA_SLOT_MAX:
										if AuraSlot != player.AURA_SLOT_SUB:
											return

										net.SendAuraRefineCheckIn(player.INVENTORY, slotIndex, player.AURA_REFINE, AuraSlot, player.GetAuraRefineWindowType())
								else:
									chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_POSSIBLE_AURARESOURCE)
									return

							else:
								chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_POSSIBLE_AURARESOURCE)
								return

						else:
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_POSSIBLE_REGISTER_AURAITEM)
							return

			elif player.GetAuraRefineWindowType() == player.AURA_WINDOW_TYPE_EVOLVE:
				if UsingAuraSlot == player.AURA_SLOT_MAX:
					if AuraSlot == player.AURA_SLOT_MAIN:
						if item.GetItemType() == item.ITEM_TYPE_COSTUME:
							if item.GetItemSubType() == item.COSTUME_TYPE_AURA:
								socketLevelValue = player.GetItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_CURRENT_LEVEL)
								curLevel = (socketLevelValue / 100000) - 1000
								curExp = socketLevelValue % 100000;
								if curLevel >= player.AURA_MAX_LEVEL:
									chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_MAX_LEVEL)
									return

								if curLevel != player.GetAuraRefineInfo(curLevel, player.AURA_REFINE_INFO_LEVEL_MAX) or curExp < player.GetAuraRefineInfo(curLevel, player.AURA_REFINE_INFO_NEED_EXP):
									chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_IMPOSSIBLE_EVOLUTION_ITEM)
									return

								if player.FindUsingAuraSlot(AuraSlot) != player.NPOS():
									return

								net.SendAuraRefineCheckIn(player.INVENTORY, slotIndex, player.AURA_REFINE, AuraSlot, player.GetAuraRefineWindowType())

							else:
								chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_POSSIBLE_AURAITEM)
								return

						else:
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_POSSIBLE_AURAITEM)
							return

					elif AuraSlot == player.AURA_SLOT_SUB:
						Cell = player.FindUsingAuraSlot(player.AURA_SLOT_MAIN)
						if Cell == player.NPOS():
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_POSSIBLE_REGISTER_AURAITEM)
							return

						socketLevelValue = player.GetItemMetinSocket(*(Cell + (player.ITEM_SOCKET_AURA_CURRENT_LEVEL,)))
						curLevel = (socketLevelValue / 100000) - 1000
						curExp = socketLevelValue % 100000;
						if curLevel >= player.AURA_MAX_LEVEL:
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_MAX_LEVEL)
							return

						if curExp < player.GetAuraRefineInfo(curLevel, player.AURA_REFINE_INFO_NEED_EXP):
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_IMPOSSIBLE_EVOLUTION_ITEM)
							return

						if AuraVnum != player.GetAuraRefineInfo(curLevel, player.AURA_REFINE_INFO_MATERIAL_VNUM):
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_IMPOSSIBLE_EVOLUTION_ITEM)
							return

						if player.GetItemCount(slotIndex) < player.GetAuraRefineInfo(curLevel, player.AURA_REFINE_INFO_MATERIAL_COUNT):
							chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_IMPOSSIBLE_EVOLUTION_ITEMCOUNT)
							return

						if UsingAuraSlot == player.AURA_SLOT_MAX:
							if AuraSlot != player.AURA_SLOT_MAX:
								if player.FindUsingAuraSlot(AuraSlot) != player.NPOS():
									return

							net.SendAuraRefineCheckIn(player.INVENTORY, slotIndex, player.AURA_REFINE, AuraSlot, player.GetAuraRefineWindowType())

	if app.ENABLE_HIDE_COSTUME_SYSTEM:
		def RefreshVisibleCostume(self):
			body = osfinfo.HIDDEN_BODY_COSTUME
			self.SetHideEvent(0, body)

			hair = osfinfo.HIDDEN_HAIR_COSTUME
			self.SetHideEvent(1, hair)

			if app.USE_ACCE_SYSTEM:
				acce = osfinfo.HIDDEN_ACCE_COSTUME
				self.SetHideEvent(2, acce)

			if app.USE_WEAPON_COSTUME_SYSTEM:
				weapon = osfinfo.HIDDEN_WEAPON_COSTUME
				self.SetHideEvent(3, weapon)

			if getattr(app, "USE_ACCE_SKIN", 0):
				self.SetHideEvent(4, getattr(osfinfo, "HIDDEN_ACCE_SKIN", 0))
			else:
				aura = osfinfo.HIDDEN_AURA_COSTUME
				self.SetHideEvent(4, aura)

			if app.USE_MOUNT_SKIN:
				self.SetHideEvent(5, osfinfo.HIDDEN_MOUNT_SKIN)

			if app.USE_PET_SKIN:
				self.SetHideEvent(6, osfinfo.HIDDEN_PET_SKIN)

		def SetHideEvent(self, slot, hide = False):
			if hide:
				self.visibleBtnList[slot].SetToolTipText(localeinfo.SHOW_COSTUME)
				self.visibleBtnList[slot].SetUpVisual("d:/ymir work/ui/game/icon_red_1.png")
				self.visibleBtnList[slot].SetOverVisual("d:/ymir work/ui/game/icon_red_2.png")
				self.visibleBtnList[slot].SetDownVisual("d:/ymir work/ui/game/icon_red_3.png")
				self.visibleSlotList[slot].Show()
			else:
				self.visibleBtnList[slot].SetToolTipText(localeinfo.HIDE_COSTUME)
				self.visibleBtnList[slot].SetUpVisual("d:/ymir work/ui/game/icon_green_1.png")
				self.visibleBtnList[slot].SetOverVisual("d:/ymir work/ui/game/icon_green_2.png")
				self.visibleBtnList[slot].SetDownVisual("d:/ymir work/ui/game/icon_green_3.png")
				self.visibleSlotList[slot].Hide()

		def VisibleCostume(self, part, hidden):
			net.SendChatPacket("/hide_costume %d %d" % (part, hidden))

	if app.ENABLE_HIDE_SHINING_SYSTEM:
		def RefreshVisibleShining(self):
			weapon = osfinfo.HIDDEN_SHINING_WEAPON
			self.SetShiningHideEvent(0, weapon)

			armor = osfinfo.HIDDEN_SHINING_ARMOR
			self.SetShiningHideEvent(1, armor)

			special = osfinfo.HIDDEN_SHINING_SPECIAL
			self.SetShiningHideEvent(2, special)

			if self.wndCostume and self.wndCostume.isLoaded:
				self.wndCostume.RefreshVisibleShining()

		def SetShiningHideEvent(self, slot, hide = False):
			if hide:
				self.visibleShiningBtnList[slot].SetToolTipText(localeinfo.SHOW_COSTUME)
				self.visibleShiningBtnList[slot].SetUpVisual("d:/ymir work/ui/game/costume/eye_closed_01.tga")
				self.visibleShiningBtnList[slot].SetOverVisual("d:/ymir work/ui/game/costume/eye_closed_02.tga")
				self.visibleShiningBtnList[slot].SetDownVisual("d:/ymir work/ui/game/costume/eye_closed_02.tga")
				self.visibleShiningSlotList[slot].Show()
			else:
				self.visibleShiningBtnList[slot].SetToolTipText(localeinfo.HIDE_COSTUME)
				self.visibleShiningBtnList[slot].SetUpVisual("d:/ymir work/ui/game/btn_hide_01.png")
				self.visibleShiningBtnList[slot].SetOverVisual("d:/ymir work/ui/game/btn_hide_02.png")
				self.visibleShiningBtnList[slot].SetDownVisual("d:/ymir work/ui/game/btn_hide_03.png")
				self.visibleShiningSlotList[slot].Hide()

		def VisibleShining(self, part, hidden):
			net.SendChatPacket("/hide_shining %d %d" % (part, hidden))

	# if app.ENABLE_HIDE_COSTUME_SYSTEM:
		# def RefreshVisibleCostume(self):
			# if self.wndCostume:
				# self.wndCostume.RefreshVisibleCostume()
			# else:
				# self.wndCostume = CostumeWindow(self)
				# self.wndCostume.RefreshVisibleCostume()

	if app.__RENEWAL_BRAVE_CAPE__:
		def SetClickCapeWindow(self, isclick):
			self.IsClickBraveCapeWindow = isclick

	if app.QUICK_SELL_SYSTEM:
		# Runs last in RefreshBagSlotWindow so the cart mark wins over the other cover images.
		# Deliberately set-only: the account-bound and convert covers are applied earlier in the
		# same refresh, so clearing here would wipe them. Deselected marks are cleared by the
		# ENABLE_CHANGE_LOOK_SYSTEM reset pass above - SetItemSlot itself keeps the cover when the
		# slot's vnum is unchanged. Turning that flag off would strand marks here.
		def RefreshQuickSellMarks(self):
			if not self.wndItem:
				return

			for k in xrange(self.wndItem.GetSlotCount()):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(k)
				if uiquicksell.IsSelected(player.INVENTORY, slotNumber):
					self.wndItem.SetSlotCoverImage(k, uiquicksell.SELECTED_COVER_IMAGE)
