# coding: latin_1

import app
import chr
import net
import player

import ui
import uiscriptlocale
import dbg
import snd
import mousemodule
import wndMgr
import skill
import playersettingmodule
import quest
import localeinfo
import uitooltip
import constinfo
import emotion
import item
import uiprivateshopbuilder
import chat
import uicommon
import uiaffectshower
import functools
import event

from _weakref import proxy

SKILL_SLOT_ENABLE	= "d:/ymir work/ui/pet/skill_button/skill_enable_button.sub"
SKILL_SLOT_MAX		= 3
# >>> GROWTH PET SKILL REWORK (U7) BEGIN: the MINI window shows all 6 rework slots.
# SKILL_SLOT_MAX stays 3 -- it also sizes the MAIN window's slot widgets (3 in its
# uiscript; the whole main window is retired in U9).
MINI_SKILL_SLOT_MAX	= 6
# <<< GROWTH PET SKILL REWORK (U7) END

TOTAL_EXP_GAUGE_COUNT = 5
BATTLE_EXP_GAUGE_MAX = 4
ITEM_EXP_GAUGE_POS = 4

FEED_WINDOW_X_SIZE = 3
FEED_WINDOW_Y_SIZE = 3

VISIBLE_LINE_COUNT = 4
DEFAULT_DESC_Y = 7

def unsigned32(n):
	return n & 0xFFFFFFFFL

if app.USE_GROWTH_NEW_EVOLVE_WINDOW:
	import grp

	EVOLVE_MATERIALS_DICT = {\
					1 : [\
							[55003, 10],
							[31047, 10],
							[99408, 5],
							[99403, 20],
							[99404, 20]
					],
					2 : [\
							[55004, 10],
							[31047, 15],
							[99404, 25],
							[99405, 25],
							[99408, 10]
					],
					3 : [\
							[55005, 10],
							[31047, 20],
							[99407, 35],
							[99405, 25],
							[99409, 10]
					]
	}

	EVOLVE_MATERIALS_POSITIVE_COLOR = grp.GenerateColor(0.5411, 0.7254, 0.5568, 1.0)
	EVOLVE_MATERIALS_NEGATIVE_COLOR = grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0)

	class PetEvolveDialog(ui.ScriptWindow):
		def __OnCloseDialog(self):
			if self.evolveQuestionDlg:
				self.evolveQuestionDlg.Close()

		def __OnAcceptDialog(self):
			if net.SendPetFeedPacket(self.petWndInst.feedIndex, [], []):
				self.petWndInst.feedButtonClickTime = app.GetGlobalTimeStamp()

				self.__OnCloseDialog()

		def RefreshCount(self):
			for k, v in self.itemCountSlot.items():
				itemCount = player.GetItemCountByVnum(self.itemCountVnum[k])

				v.SetText(str(itemCount))

				if itemCount >= self.itemCountCount[k]:
					v.SetPackedFontColor(EVOLVE_MATERIALS_POSITIVE_COLOR)
				else:
					v.SetPackedFontColor(EVOLVE_MATERIALS_NEGATIVE_COLOR)

		def Open(self):
			petID = player.GetActivePetItemId()
			if petID == 0:
				return

			if not self.petWndInst.IsActivateEvolButton(petID):
				return

			(petLVL, petEVOL, petBIRTH, petNICK, petHP, petDEF, petSP) = player.GetPetItem(petID)

			if self.lastEvolveBuild != petEVOL:
				self.lastEvolveBuild = petEVOL

				for i in xrange(self.itemSlot.GetSlotCount()):
					self.itemSlot.ClearSlot(i)

					if EVOLVE_MATERIALS_DICT.has_key(self.lastEvolveBuild):
						self.itemCountVnum[i] = EVOLVE_MATERIALS_DICT[self.lastEvolveBuild][i][0]
						self.itemCountCount[i] = EVOLVE_MATERIALS_DICT[self.lastEvolveBuild][i][1]

						self.itemSlot.SetItemSlot(i, self.itemCountVnum[i], self.itemCountCount[i])

			self.RefreshCount()

			(x, y) = self.petWndInst.GetGlobalPosition()
			self.SetPosition(x + self.w - 2, y + 192)

			self.SetTop()
			self.Show()
			#player.SetOpenPetFeedWindow(True)

		def Close(self, exceptToggle = False):
			self.__OnCloseDialog()

			if self.tooltipItem:
				self.tooltipItem.HideToolTip()

			if not self.IsShow():
				return

			if exceptToggle == False:
				self.petWndInst.PetFeedToggleButtonUpAll()
				self.petWndInst.feedIndex = player.FEED_BUTTON_MAX

			self.Hide()
			#player.SetOpenPetFeedWindow(False)

		def OnPressEscapeKey(self):
			self.Close()
			return True

		def __SelectEmptySlot(self, iPos):
			if mousemodule.mouseController.isAttached():
				mousemodule.mouseController.DeattachObject()

		def __SelectItemSlot(self, iPos):
			if mousemodule.mouseController.isAttached():
				mousemodule.mouseController.DeattachObject()

		def __OverInItem(self, iPos):
			if not EVOLVE_MATERIALS_DICT.has_key(self.lastEvolveBuild):
				return

			if not self.tooltipItem:
				self.tooltipItem = uitooltip.ItemToolTip()
				self.tooltipItem.ClearToolTip()

			self.tooltipItem.SetItemToolTip(EVOLVE_MATERIALS_DICT[self.lastEvolveBuild][iPos][0])

		def __OverOutItem(self):
			if self.tooltipItem:
				self.tooltipItem.HideToolTip()

		def __Evolve(self):
			if not self.evolveQuestionDlg:
				self.evolveQuestionDlg = uicommon.QuestionDialog()
				self.evolveQuestionDlg.SetText(localeinfo.GROWTH_PET_EVOLVE_QUESTION)
				self.evolveQuestionDlg.SetAcceptEvent(ui.__mem_func__(self.__OnAcceptDialog))
				self.evolveQuestionDlg.SetCancelEvent(ui.__mem_func__(self.__OnCloseDialog))

			(x, y) = self.GetGlobalPosition()

			self.evolveQuestionDlg.Open()

			self.evolveQuestionDlg.SetPosition(x - self.evolveQuestionDlg.GetWidth() - 4, y + (self.GetHeight() / 2) - (self.evolveQuestionDlg.GetHeight() / 2))

		def __Build(self):
			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "uiscript/growthpet_evolve_dialog.py")

				self.titleBar = self.GetChild("titlebar_ui")
				self.evolveBtn = self.GetChild("evolvebutton_ui")
				self.itemSlot = self.GetChild("itemslot_ui")

				self.itemCountSlot = {}
				self.itemCountVnum = {}
				self.itemCountCount = {}

				for i in xrange(self.itemSlot.GetSlotCount()):
					self.itemCountSlot[i] = self.GetChild("counttext%d_ui" % (i + 1))
					self.itemCountVnum[i] = 0
					self.itemCountCount[i] = 0
			except:
				import exception
				exception.Abort("PetEvolveDialog.__Build.Load")

			try:
				self.lastEvolveBuild = -1

				self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))

				self.evolveBtn.SetEvent(ui.__mem_func__(self.__Evolve))

				self.itemSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.__SelectEmptySlot))
				self.itemSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.__SelectItemSlot))
				self.itemSlot.SetOverInItemEvent(ui.__mem_func__(self.__OverInItem))
				self.itemSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OverOutItem))
			except:
				import exception
				exception.Abort("PetEvolveDialog.__Build.Bind")

		def __init__(self, petWndInst):
			ui.ScriptWindow.__init__(self)

			self.petWndInst = proxy(petWndInst)
			self.w = self.petWndInst.GetWidth()

			self.tooltipItem = None
			self.evolveQuestionDlg = None

			self.__Build()

		def Destroy(self):
			if self.titleBar:
				self.titleBar.SetCloseEvent(None)
				self.titleBar = None

			if self.evolveBtn:
				self.evolveBtn.SetEvent(None)
				self.evolveBtn = None

			if self.evolveQuestionDlg:
				self.evolveQuestionDlg.SetAcceptEvent(None)
				self.evolveQuestionDlg.SetCancelEvent(None)
				del self.evolveQuestionDlg
				self.evolveQuestionDlg = None

			if self.tooltipItem:
				del self.tooltipItem
				self.tooltipItem = None

			self.itemCountSlot = {}
			self.itemCountVnum = {}
			self.itemCountCount = {}

			self.petWndInst = None

			self.ClearDictionary()

		def __del__(self):
			ui.ScriptWindow.__del__(self)

"""
		PetMiniInfomationWindow appears in the bottom left corner.
		It shows experience bars, skill slots and their cooldowns
		and icon flash effect which indicates that pet is ready to
		evolve.
"""
class PetMiniInfomationWindow(ui.ScriptWindow):
	def __init__(self, wndPetInformation):
		import exception

		if not wndPetInformation:
			exception.Abort("wndPetInformation parameter must be set to PetInformationWindow")
			return						
			 	 
		ui.ScriptWindow.__init__(self)
		self.skillSlot = []
		self.isLoaded = 0
		self.wndPetInformation = wndPetInformation
		self.petSlot = 0
		self.petSlotAniImg  = None
		self.expGauge		= None
		self.expGaugeBoard	= None
		
		self.__LoadWindow()
	
	def __del__(self):
		ui.ScriptWindow.__del__(self)
		
	def Show(self):
		self.__LoadWindow()
		ui.ScriptWindow.Show(self)
		
	def Close(self):
		if self.petSlot:
			self.petSlot.SetItemSlot(0, 0)
			
		if self.tooltipEXP:
			self.tooltipEXP.Hide()
				
		self.Hide()
			
		
	def Destroy(self):
		self.isLoaded = 0
		self.wndPetInformation = 0
		self.lifeTimeGauge	= None
		self.petSlot = 0
		self.petSlotAniImg  = None
		self.expGauge		= None
		self.expGaugeBoard	= None
		self.tooltipEXP		= None
		
		if self.skillSlot:
			del self.skillSlot[:]
		
	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			self.__LoadScript("UIScript/petMiniInformationWindow.py")
			
		except:
			import exception
			exception.Abort("PetMiniInfomationWindow.LoadWindow.LoadObject")
			
			
		try:
			# Background
			if localeinfo.IsARABIC():
				self.GetChild("main_bg").LeftRightReverse()
				
			# Pet Icon Slot
			self.petSlot = self.GetChild("pet_icon_slot")
			self.petSlot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)			
			self.petSlot.SAFE_SetButtonEvent("LEFT", "EXIST", self.SelectItemSlot)
			if localeinfo.IsARABIC():
				self.petSlot.SetPosition(0,6)
			
			# Pet Icon Slot Animation Image - Flash
			self.petSlotAniImg = self.GetChild("pet_icon_slot_ani_img")
			self.petSlotAniImg.Hide()
			if localeinfo.IsARABIC():
				self.petSlotAniImg.SetPosition(34, 3)
			
			# EXP Gauges
			expGauge = []
			self.expGaugeBoard = self.GetChild("pet_mini_info_exp_gauge_board")
			expGauge.append(self.GetChild("pet_mini_EXPGauge_01"))
			expGauge.append(self.GetChild("pet_mini_EXPGauge_02"))
			expGauge.append(self.GetChild("pet_mini_EXPGauge_03"))
			expGauge.append(self.GetChild("pet_mini_EXPGauge_04"))
			expGauge.append(self.GetChild("pet_mini_EXPGauge_05"))
			
			for exp in expGauge:
				exp.SetSize(0, 0)
			
			self.expGauge	= expGauge
			self.tooltipEXP = TextToolTip()
			self.tooltipEXP.Hide()
			
			# Mini Info Skill Slot Scale
			# U7: 6 rework slots; GetChild2 + break keeps an old 3-slot uiscript pack loadable.
			for value in range(MINI_SKILL_SLOT_MAX):
				slotWnd = self.GetChild2("mini_skill_slot"+str(value))
				if not slotWnd:
					break
				self.skillSlot.append(slotWnd)
				self.skillSlot[value].SetCoverButton(0, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, False, False)
				self.skillSlot[value].SetAlwaysRenderCoverButton(0)

				if localeinfo.IsARABIC():
					arabic_start_pos_x = -23
					self.skillSlot[value].SetPosition(arabic_start_pos_x, 0)
											
											
			# Life Time Gauge
			self.lifeTimeGauge = self.GetChild("LifeGauge")
			self.lifeTimeGauge.SetWindowHorizontalAlignLeft()
			if localeinfo.IsARABIC():
				self.GetChild("gauge_left").LeftRightReverse()
				self.GetChild("gauge_right").LeftRightReverse()				
				
		except:
			import exception
			exception.Abort("PetMiniInfomationWindow.LoadWindow.BindObject")
			
		
		self.Hide()
			
	def __LoadScript(self, fileName):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, fileName)
		
	def OnUpdate(self):
	
		if self.expGaugeBoard.IsIn():
			self.tooltipEXP.Show()
		else:
			self.tooltipEXP.Hide()
			
		return
		
	def SetItemSlot(self, CurPetItemVNum):
		self.petSlot.SetItemSlot(0, CurPetItemVNum)
		self.petSlot.RefreshSlot()
		
	def SetSkillSlot(self, slotNumber, slotIndex, skillVnum):
		# U7: guard on the BOUND count (an old 3-slot uiscript pack binds fewer than
		# MINI_SKILL_SLOT_MAX; feeding slot 3+ must be a silent no-op, not an IndexError).
		if 0 > slotNumber or slotNumber >= len(self.skillSlot):
			return

		self.skillSlot[slotNumber].SetPetSkillSlotNew(slotIndex, skillVnum)
		self.skillSlot[slotNumber].SetCoverButton(slotIndex)

	def SetSkillCoolTime(self, slotNumber, slotIndex, max_cool_time, cur_cool_time):
		if 0 > slotNumber or slotNumber >= len(self.skillSlot):   # U7 guard (see SetSkillSlot)
			return
		self.skillSlot[slotNumber].SetSlotCoolTime(slotIndex, max_cool_time, cur_cool_time)
		self.skillSlot[slotNumber].SetSlotCoolTimeColor(slotIndex, 0.0, 1.0, 0.0, 0.5)

	def ClearSkillSlot(self):
		for value in range(len(self.skillSlot)):   # U7: iterate what was actually bound
			self.skillSlot[value].ClearSlot(0)
			self.skillSlot[value].SetCoverButton(0, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, False, False)
			self.skillSlot[value].SetAlwaysRenderCoverButton(0)

	def SetAlwaysRenderCoverButton(self, slotNumber):
		if 0 > slotNumber or slotNumber >= len(self.skillSlot):   # U7 guard (see SetSkillSlot)
			return
		self.skillSlot[slotNumber].SetAlwaysRenderCoverButton(0, False)
		
	def SelectItemSlot(self):
		if not self.wndPetInformation:
			return

		# >>> GROWTH PET U9 BEGIN: the legacy main window is retired -- clicking the
		# mini-window pet icon opens the Companion pet page (same toggle the P key
		# uses now). Legacy toggle kept below for non-Companion builds.
		interfaceModule = getattr(self.wndPetInformation, "interface", None)
		if interfaceModule and hasattr(interfaceModule, "ToggleCompanionPetPage"):
			interfaceModule.ToggleCompanionPetPage()
			return
		# <<< GROWTH PET U9 END
		if self.wndPetInformation.IsShow():
			self.wndPetInformation.Close()
		else:
			self.wndPetInformation.Show()
	
	def SetLifeTime(self, curPoint, maxPoint):
		curPoint = min(curPoint, maxPoint)
		if maxPoint > 0:
			self.lifeTimeGauge.SetPercentageWithScale(curPoint, maxPoint)
				
	def SetExperience(self, curPoint, maxPoint, itemExp, itemExpMax):
		
		curPoint = min(curPoint, maxPoint)
		curPoint = max(curPoint, 0)
		maxPoint = max(maxPoint, 0)
		
		itemExp = min(itemExp, itemExpMax)
		itemExp = max(itemExp, 0)
		itemExpMax = max(itemExpMax, 0)
		
		# Battle exp is divided into BATTLE_EXP_GAUGE_MAX parts
		quarterPoint = maxPoint / BATTLE_EXP_GAUGE_MAX
		FullCount = 0

		if 0 != quarterPoint:
			FullCount = min(BATTLE_EXP_GAUGE_MAX, curPoint / quarterPoint)

		for i in xrange(TOTAL_EXP_GAUGE_COUNT):
			self.expGauge[i].Hide()

		for i in xrange(FullCount):
			self.expGauge[i].SetRenderingRect(0.0, 0.0, 0.0, 0.0)
			self.expGauge[i].Show()

		if 0 != quarterPoint:
			if FullCount < BATTLE_EXP_GAUGE_MAX:
				Percentage = float(curPoint % quarterPoint) / quarterPoint - 1.0
				self.expGauge[FullCount].SetRenderingRect(0.0, Percentage, 0.0, 0.0)
				self.expGauge[FullCount].Show()
				

		if 0 != itemExpMax:			
			itemExpGauge = self.expGauge[ITEM_EXP_GAUGE_POS]
			Percentage = float(itemExp) / float(itemExpMax) - float(1.0)
			itemExpGauge.SetRenderingRect(0.0, Percentage, 0.0, 0.0)
			itemExpGauge.Show()
			
		output_cur_exp = curPoint + itemExp
		output_max_exp = maxPoint + itemExpMax

		expPercent = 0
		if output_max_exp:
			expPercent = float(output_cur_exp) / float(output_max_exp) * 100

		if app.USE_CTEXTLINE_AUTO_WRAP:
			if localeinfo.IsARABIC():
				tooltip_text = "{} : {}\n{} : {}\n{} : {}\n{} : {}".format(curPoint, localeinfo.PET_INFO_EXP,\
																			maxPoint - curPoint, localeinfo.PET_INFO_NEXT_EXP,\
																			itemExp, localeinfo.PET_INFO_ITEM_EXP,\
																			itemExpMax - itemExp, localeinfo.PET_INFO_NEXT_ITEM_EXP)
			else:
				tooltip_text = "{} : {}\n{} : {}\n{} : {}\n{} : {}".format(localeinfo.PET_INFO_EXP, curPoint,\
																			localeinfo.PET_INFO_NEXT_EXP, maxPoint - curPoint,\
																			localeinfo.PET_INFO_ITEM_EXP, itemExp,\
																			localeinfo.PET_INFO_NEXT_ITEM_EXP, itemExpMax - itemExp)
			self.tooltipEXP.SetText(tooltip_text)
		else:
			self.tooltipEXP.SetText("%s : %.2f%%" % (localeinfo.TASKBAR_EXP, expPercent))

	def OnFlashEvent(self):
		if self.petSlotAniImg:
			self.petSlotAniImg.Show()
		
	def OffFlashEvent(self):
		if self.petSlotAniImg:
			self.petSlotAniImg.Hide()
		
"""
		PetHatchingWindow will appear when hatching an egg.
		It can be closed manually or after successful egg hatch.
"""
class PetHatchingWindow(ui.ScriptWindow):
	def __init__(self, wndPetInformation):
		import exception

		if not wndPetInformation:
			exception.Abort("wndPetInformation parameter must be set to PetInformationWindow")
			return						
		
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.isLoaded = 0
		self.hatchingSlot = 0
		self.eggItemSlotIndex  = -1
		self.eggItemSlotWindow = player.INVENTORY
		self.wndPetInformation = wndPetInformation
		self.hatchingButton = 0
		self.petNameEdit = 0
		self.petName = 0
		self.questionDialog = 0
		self.popupDialog = 0
		self.hatchingMoneyText = None
			
		self.__LoadWindow()
	
	def __del__(self):
		ui.ScriptWindow.__del__(self)
		
	def Show(self):
		self.__LoadWindow()
		ui.ScriptWindow.Show(self)		
		self.SetTop()
		
	def Close(self):
		self.ClearMouseEventEggItem()
		self.hatchingSlot.SetItemSlot(0, 0)
		self.hatchingSlot.RefreshSlot()
		self.petName = 0
			
		self.Hide()
		player.SetOpenPetHatchingWindow(False)
		net.SendPetHatchingWindowPacket(False)
		
		if self.questionDialog:
			self.questionDialog.Close()
			
		if self.popupDialog:
			self.popupDialog.Close()
			
		if self.petNameEdit:
			self.petNameEdit.KillFocus()
		
	def Destroy(self):
		self.isLoaded = 0
		self.hatchingSlot = 0
		self.wndPetInformation = 0
		self.hatchingButton = 0
		self.petName = 0
		self.hatchingMoneyText = None
		
		if self.popupDialog:
			self.popupDialog.Destroy()
		
	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			self.__LoadScript("UIScript/petHatchingWindow.py")
				
		except:
			import exception
			exception.Abort("petHatchingWindow.LoadWindow.LoadObject")
			
			
		try:
			self.GetChild("PetHatching_TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
			self.hatchingSlot = self.GetChild("HatchingItemSlot")
			self.hatchingSlot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
			self.hatchingSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))			
			self.hatchingSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			
			# Hatch button
			self.hatchingButton = self.GetChild("HatchingButton")
			self.hatchingButton.SetEvent(ui.__mem_func__(self.ClickHatchingButton))
				
			# Hatch price text
			self.hatchingMoneyText = self.GetChild("HatchingMoney");
			self.hatchingMoneyText.SetText(localeinfo.PET_HATCHING_MONEY % localeinfo.NumberToMoneyString(0))
			
			# Pet name editline
			self.petNameEdit = self.GetChild("pet_name")
			self.petNameEdit.SetText("")
			self.petNameEdit.SetReturnEvent(ui.__mem_func__(self.ClickHatchingButton))
			self.petNameEdit.SetEscapeEvent(ui.__mem_func__(self.Close))
			self.petNameEdit.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.OnMouseLeftButtonUpEvent))
			self.petNameEdit.SetFocus()
			self.petNameEdit.Show()
			
			# Initialize question and popup dialogs
			self.__MakeQuestionDialog()
			self.__MakePopupDialog()
			
			
		except:
			import exception
			exception.Abort("petHatchingWindow.LoadWindow.BindObject")
			
	def __LoadScript(self, fileName):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, fileName)
		
	def __MakeQuestionDialog(self):
		if not self.questionDialog:
			self.questionDialog = uicommon.QuestionDialog()
			self.questionDialog.SetText("")
			
			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__HatchingQuestionDialogAccept))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__HatchingQuestionDialogCancel))
		
		
	def __MakePopupDialog(self):
		self.popupDialog = uicommon.PopupDialog()
		self.popupDialog.SetText("")
		
	def ClickHatchingButton(self):
		if self.popupDialog:
			if self.popupDialog.IsShow():
				return
				
		self.__OpenHatchingQuestionDialog()
		
	def OnMouseLeftButtonUpEvent(self):
		if self.petName == self.petNameEdit.GetText():
			self.petNameEdit.SetText("")
			self.petNameEdit.SetEndPosition()
			
		
	def OverInItem(self, slotIndex):
		return
		
	def OverOutItem(self):
		return
		
	def ClearMouseEventEggItem(self):
		if self.eggItemSlotIndex == -1:
			return
			
		# Unlock egg item
		inven_slot_pos = self.eggItemSlotIndex
			
		if inven_slot_pos >= player.INVENTORY_PAGE_SIZE:
			inven_page = self.wndPetInformation.inven.GetInventoryPageIndex()
			inven_slot_pos -= (inven_page * player.INVENTORY_PAGE_SIZE)
					
		self.wndPetInformation.inven.wndItem.SetCanMouseEventSlot(inven_slot_pos)
	
		# Reset egg item position
		self.eggItemSlotIndex  = -1
		self.eggItemSlotWindow = player.INVENTORY
		
	def OnUpdate(self):

		if not self.wndPetInformation.inven:
			return
			
		if self.eggItemSlotIndex == -1:
			return
			
		if not self.hatchingSlot:
			return		
		
		try:
			inven = self.wndPetInformation.inven
			invenPage = inven.GetInventoryPageIndex()
		
			min_range = invenPage * player.INVENTORY_PAGE_SIZE
			max_range = (invenPage + 1) * player.INVENTORY_PAGE_SIZE
			
			# Lock egg item
			inven_slot_pos = self.eggItemSlotIndex
			
			if min_range <= inven_slot_pos < max_range:
				inven_slot_pos = inven_slot_pos - min_range
				inven.wndItem.SetCantMouseEventSlot(inven_slot_pos)
			
		except:
			pass
				
		return
		
	def HatchingWindowOpen(self, slotWindow, slotIndex):
		# Check if player has no other trading windows opened
		checkMsg = net.CheckUsePetItem()
		
		if checkMsg == item.PET_EGG_USE_FAILED_BECAUSE_TRADING:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_EGG_ITEM_USE)
			
		elif checkMsg == item.PET_EGG_USE_FAILED_BECAUSE_SHOP_OPEN:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_EGG_ITEM_USE)
			
		elif checkMsg == item.PET_EGG_USE_FAILED_BECAUSE_MALL_OPEN:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_EGG_ITEM_USE)
			
		elif checkMsg == item.PET_EGG_USE_FAILED_BECAUSE_SAFEBOX_OPEN:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_EGG_ITEM_USE)
			
		if checkMsg != item.PET_EGG_USE_TRUE:
			return
			
		if not self.hatchingSlot:
			return
			
		ItemVNum = player.GetItemIndex(slotWindow, slotIndex)
		
		if ItemVNum == 0:
			return
			
		item.SelectItem(ItemVNum)
		
		growthPetVnum = item.GetValue(0)
			
		if growthPetVnum == 0:
			return

		hatching_money_value = 1000
		if self.hatchingMoneyText:
			self.hatchingMoneyText.SetText(localeinfo.PET_HATCHING_MONEY % localeinfo.NumberToMoneyString(hatching_money_value))
		
		self.Close()
		self.eggItemSlotIndex  = slotIndex
		self.eggItemSlotWindow = slotWindow
		self.hatchingSlot.SetItemSlot(0, growthPetVnum)
		self.hatchingSlot.RefreshSlot()
		item_string = item.GetItemName()
		#self.petName = item_string[:item.PET_NAME_MAX_SIZE]
		#self.petNameEdit.SetText(self.petName)
		self.petNameEdit.SetEndPosition()
		self.petNameEdit.SetFocus()
		self.petNameEdit.Show()
		self.Show()
		net.SendPetHatchingWindowPacket(True)
		player.SetOpenPetHatchingWindow(True)
		
	def __OpenHatchingQuestionDialog(self):
		interface = self.wndPetInformation.interface
		
		if interface.IsShowDlgQuestionWindow():
			interface.CloseDlgQuestionWindow()
			
		if not self.questionDialog:
			self.__MakeQuestionDialog()
			
		# Reset position if name has no characters inside editline
		if "" == self.petNameEdit.GetText():
			self.petNameEdit.SetText(self.petName)
			self.petNameEdit.SetEndPosition()
			
		self.questionDialog.SetText(localeinfo.PET_HATCHING_ACCEPT % (self.petNameEdit.GetText()))
		self.questionDialog.SetTop()
		self.questionDialog.Open()
		
		
	def __HatchingQuestionDialogAccept(self):
		self.questionDialog.Close()
		
		# Check if pet's name is smaller than defined minimal size (item.PET_NAME_MIN_SIZE)
		if len(self.petNameEdit.GetText()) < item.PET_NAME_MIN_SIZE:
			self.petNameEdit.SetText("")
			self.__OpenPopupDialog(localeinfo.PET_NAME_MIN)
			return

		itemVnum = player.GetItemIndex(self.eggItemSlotWindow, self.eggItemSlotIndex)
		if itemVnum == 0:
			return
			
		item.SelectItem(itemVnum)
		hatching_money = item.GetValue(3)
		
		# Check if player has enough money to hatch an egg
		if player.GetMoney() < hatching_money:
			self.__OpenPopupDialog(localeinfo.PET_MSG_NOT_ENOUGH_MONEY)
			return		
			
		net.SendPetHatchingPacket(self.petNameEdit.GetText(), self.eggItemSlotWindow, self.eggItemSlotIndex)
		
	def __HatchingQuestionDialogCancel(self):
		self.questionDialog.Close()
		
	def __OpenPopupDialog(self, str):
		interface = self.wndPetInformation.interface
		
		if interface.IsShowDlgQuestionWindow():
			interface.CloseDlgQuestionWindow()
		
		if not self.popupDialog:
			self.__MakePopupDialog()
			
		self.popupDialog.SetText(str)
		self.popupDialog.SetTop()
		self.popupDialog.Open()
	
	def PetHatchingWindowCommand(self, command):
		# Egg hatch succeeded, close the window
		if command == item.EGG_USE_SUCCESS:
			self.Close()
			
		# Egg hatch failed, clear the name
		elif command == item.EGG_USE_FAILED_BECAUSE_NAME:
			self.petNameEdit.SetText("")
			self.petNameEdit.SetEndPosition()
			
		# Egg hatch hit an error, close the window
		elif command == item.EGG_USE_FAILED_TIMEOVER:
				self.Close()
		
"""
		PetNameChangeWindow will appear when change name item is
		dragged to upbringing item. It can be closed manually or 
		after successful name change.
"""
class PetNameChangeWindow(ui.ScriptWindow):
	def __init__(self, wndPetInformation):
		import exception

		if not wndPetInformation:
			exception.Abort("wndPetInformation parameter must be set to PetInformationWindow")
			return						
			 	 
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.isLoaded					= 0
		self.wndPetInformation			= wndPetInformation
		
		self.nameChangeItemSlotIndex	= -1
		self.petItemSlotIndex			= -1
		
		self.petItemSlot		= None
		self.nameChangeButton	= None
		self.petNameEdit		= None
		self.petName			= None
		self.questionDialog		= None
		self.popupDialog		= None
		
		self.__LoadWindow()
	
	def __del__(self):
		ui.ScriptWindow.__del__(self)
		
	def Show(self):
		self.__LoadWindow()
		ui.ScriptWindow.Show(self)		
		self.SetTop()
		
	def Close(self):
		self.ClearMouseEventItem()
		
		if self.petItemSlot:
			self.petItemSlot.SetItemSlot(0, 0)
			self.petItemSlot.RefreshSlot()
			
		self.petName = None
		self.Hide()
		
		player.SetOpenPetNameChangeWindow(False)
		net.SendPetNameChangeWindowPacket(False)
		
		if self.questionDialog:
			self.questionDialog.Close()
			
		if self.popupDialog:
			self.popupDialog.Close()
			
		if self.petNameEdit:
			self.petNameEdit.KillFocus()
			
		
	def Destroy(self):
		self.isLoaded			= 0
		self.wndPetInformation	= None
		self.petItemSlot		= None
		self.nameChangeButton	= None
		self.petName			= None
		
		if self.popupDialog:
			self.popupDialog.Destroy()
		
	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			self.__LoadScript("UIScript/petNameChangeWindow.py")
				
		except:
			import exception
			exception.Abort("petNameChangeWindow.LoadWindow.LoadObject")
			
			
		try:
			self.GetChild("PetNameChangeTitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
			self.petItemSlot = self.GetChild("PetItemSlot")
			self.petItemSlot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
			
			# Name change button
			self.nameChangeButton = self.GetChild("NameChangeButton")
			self.nameChangeButton.SetEvent(ui.__mem_func__(self.ClickNameChangeButton))
				
			# Pet change name price
			MoneyText = self.GetChild("NameChangeMoney");
			MoneyText.SetText(localeinfo.PET_HATCHING_MONEY % (localeinfo.NumberToMoneyString(item.PET_HATCHING_MONEY)))
			
			# Pet name editline
			self.petNameEdit = self.GetChild("pet_name")
			self.petNameEdit.SetText("")
			self.petNameEdit.SetReturnEvent(ui.__mem_func__(self.ClickNameChangeButton))
			self.petNameEdit.SetEscapeEvent(ui.__mem_func__(self.Close))
			self.petNameEdit.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.OnMouseLeftButtonUpEvent))
			self.petNameEdit.SetFocus()
			self.petNameEdit.Show()
			
			# Initialize question and popup dialogs
			self.__MakeQuestionDialog()
			self.__MakePopupDialog()
			
			
		except:
			import exception
			exception.Abort("petNameChangeWindow.LoadWindow.BindObject")
			
	def __LoadScript(self, fileName):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, fileName)
		
	def __MakeQuestionDialog(self):
		if not self.questionDialog:
			self.questionDialog = uicommon.QuestionDialog()
			self.questionDialog.SetText("")
			
			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__NameChangeQuestionDialogAccept))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__NameChangeQuestionDialogCancel))
		
		
	def __MakePopupDialog(self):
		self.popupDialog = uicommon.PopupDialog()
		self.popupDialog.SetText("")
		
	def ClickNameChangeButton(self):
		if self.popupDialog:
			if self.popupDialog.IsShow():
				return
				
		self.__OpenNameChangeQuestionDialog()
		
	def OnMouseLeftButtonUpEvent(self):
		if self.petName == self.petNameEdit.GetText():
			self.petNameEdit.SetText("")
			self.petNameEdit.SetEndPosition()

	def ClearMouseEventItem(self):
		if self.nameChangeItemSlotIndex == -1:
			return
			
		if self.petItemSlotIndex == -1:
			return
		
		# Unlock name change item
		if self.nameChangeItemSlotIndex >= player.INVENTORY_PAGE_SIZE:
			inven_page = self.wndPetInformation.inven.GetInventoryPageIndex()
			self.nameChangeItemSlotIndex -= (inven_page * player.INVENTORY_PAGE_SIZE)
					
		self.wndPetInformation.inven.wndItem.SetCanMouseEventSlot(self.nameChangeItemSlotIndex)
		
		# Unlock pet upbringing item
		if self.petItemSlotIndex >= player.INVENTORY_PAGE_SIZE:
			inven_page = self.wndPetInformation.inven.GetInventoryPageIndex()
			self.petItemSlotIndex -= (inven_page * player.INVENTORY_PAGE_SIZE)
					
		self.wndPetInformation.inven.wndItem.SetCanMouseEventSlot(self.petItemSlotIndex)
	
		# Reset item positions
		self.nameChangeItemSlotIndex	= -1
		self.petItemSlotIndex			= -1
		
	def OnUpdate(self):
		if not self.wndPetInformation.inven:
			return
			
		if self.nameChangeItemSlotIndex == -1:
			return
			
		if self.petItemSlotIndex == -1:
			return
			
		if not self.petItemSlot:
			return
		
		try:
			inven		= self.wndPetInformation.inven
			invenPage	= inven.GetInventoryPageIndex()
		
			min_range = invenPage * player.INVENTORY_PAGE_SIZE
			max_range = (invenPage + 1) * player.INVENTORY_PAGE_SIZE
			
			# Lock name change item
			inven_slot_pos = self.nameChangeItemSlotIndex
			if min_range <= inven_slot_pos < max_range:
				inven_slot_pos = inven_slot_pos - min_range
				inven.wndItem.SetCantMouseEventSlot(inven_slot_pos)
				
			# Lock pet upbringing item
			inven_slot_pos = self.petItemSlotIndex
			if min_range <= inven_slot_pos < max_range:
				inven_slot_pos = inven_slot_pos - min_range
				inven.wndItem.SetCantMouseEventSlot(inven_slot_pos)
		except:
			pass
				
		return
		
	def NameChangeWindowOpen(self, srcSlotIndex, dstSlotIndex):
		# Check if player has no other trading windows opened
		checkMsg = net.CheckUsePetItem()
		
		if checkMsg == item.PET_EGG_USE_FAILED_BECAUSE_TRADING:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_EGG_ITEM_USE)
			
		elif checkMsg == item.PET_EGG_USE_FAILED_BECAUSE_SHOP_OPEN:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_EGG_ITEM_USE)
			
		elif checkMsg == item.PET_EGG_USE_FAILED_BECAUSE_MALL_OPEN:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_EGG_ITEM_USE)
			
		elif checkMsg == item.PET_EGG_USE_FAILED_BECAUSE_SAFEBOX_OPEN:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_EGG_ITEM_USE)
			
		if checkMsg != item.PET_EGG_USE_TRUE:
			return
			
		if not self.petItemSlot:
			return
		
		petItemVnum = player.GetItemIndex(dstSlotIndex)
		if 0 == petItemVnum:
			return
		
		metinSlot = [player.GetItemMetinSocket(dstSlotIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
		pet_id = metinSlot[2]
		if 0 == pet_id:
			return
			
		(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
					
		self.Close()
		self.nameChangeItemSlotIndex	= srcSlotIndex
		self.petItemSlotIndex			= dstSlotIndex

		self.petItemSlot.SetItemSlot(0, petItemVnum)
		self.petItemSlot.RefreshSlot()
		self.petName = pet_nick
		self.petNameEdit.SetText(self.petName)
		self.petNameEdit.SetEndPosition()
		self.petNameEdit.SetFocus()
		self.petNameEdit.Show()
		self.Show()
		
		net.SendPetNameChangeWindowPacket(True)
		player.SetOpenPetNameChangeWindow(True)
		
	def __OpenNameChangeQuestionDialog(self):
		interface = self.wndPetInformation.interface
		
		if interface.IsShowDlgQuestionWindow():
			interface.CloseDlgQuestionWindow()
			
		if not self.questionDialog:
			self.__MakeQuestionDialog()
			
		# Reset position if name has no characters inside editline
		if "" == self.petNameEdit.GetText():
			self.petNameEdit.SetText(self.petName)
			self.petNameEdit.SetEndPosition()
			
		self.questionDialog.SetText(localeinfo.PET_NAME_CHANGE_ACCEPT % (self.petNameEdit.GetText()))
		self.questionDialog.SetTop()
		self.questionDialog.Open()
		
		
	def __NameChangeQuestionDialogAccept(self):
		self.questionDialog.Close()
		
		# Check if pet's name is smaller than defined minimal size (item.PET_NAME_MIN_SIZE)
		if len(self.petNameEdit.GetText()) < item.PET_NAME_MIN_SIZE:
			self.petNameEdit.SetText("")
			self.__OpenPopupDialog(localeinfo.PET_NAME_MIN)
			return
		
		# Check if player has enough money to change the name
		if player.GetMoney() < item.PET_HATCHING_MONEY:
			self.__OpenPopupDialog(localeinfo.PET_MSG_NOT_ENOUGH_MONEY)
			return			
			
		net.SendPetNameChangePacket(self.petNameEdit.GetText(), self.nameChangeItemSlotIndex, self.petItemSlotIndex)
		
	def __NameChangeQuestionDialogCancel(self):
		self.questionDialog.Close()
		
	def __OpenPopupDialog(self, str):
		interface = self.wndPetInformation.interface
		
		if interface.IsShowDlgQuestionWindow():
			interface.CloseDlgQuestionWindow()
		
		if not self.popupDialog:
			self.__MakePopupDialog()
			
		self.popupDialog.SetText(str)
		self.popupDialog.SetTop()
		self.popupDialog.Open()
			
	def PetNameChangeWindowCommand(self, command):
		# Name change succeeded, close the window
		if command == item.NAME_CHANGE_USE_SUCCESS:
			self.Close()
			
		# Name change has failed, clear the name
		elif command == item.NAME_CHANGE_USE_FAILED_BECAUSE_NAME:
			self.petNameEdit.SetText("")
			self.petNameEdit.SetEndPosition()
						
"""
		PetFeedWindow is opened through main pet interface.
		It consists of item slot grid on which player can
		drag items. Used for pet lifetime, evolve & item exp.
"""
class PetFeedWindow(ui.ScriptWindow):
	def __init__(self, wndPetInformation):
		import exception

		if not wndPetInformation:
			exception.Abort("wndPetInformation parameter must be set to PetInformationWindow")
			return						
			 	 
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.isLoaded = 0
		self.feedButtonClickTime = 0
		self.backupFeedItems = []
		self.wndPetInformation = wndPetInformation
		
		self.questionDialogEmptyPos = -1
		self.questionDialogItemPos = -1
		
		self.__LoadWindow()
	
	def __del__(self):
		ui.ScriptWindow.__del__(self)
		
	def Show(self):
		self.__LoadWindow()
		ui.ScriptWindow.Show(self)
		player.SetOpenPetFeedWindow(True)
		
		if self.wndPetInformation and self.wndPetInformation.inven:
			self.wndPetInformation.inven.Show()
				
	def ClearFeedItems(self):
		self.ClearMouseEventFeedItems()
		
		if self.FeedItemSlot:
			for slotPos in xrange(self.FeedItemSlot.GetSlotCount()):
				self.FeedItemSlot.ClearSlot(slotPos)
				
			self.FeedItemSlot.RefreshSlot()
		
	def SetOnTopWindowNone(self):

		if not self.wndPetInformation:
			return
			
		if not self.wndPetInformation.interface:
			return
			
		interface = self.wndPetInformation.interface
		interface.SetOnTopWindow(player.ON_TOP_WND_NONE)
		interface.RefreshMarkInventoryBag()

	#if app.USE_GROWTH_NEW_EVOLVE_WINDOW:
	def Close(self, exceptToggle = False):
		if app.USE_GROWTH_NEW_EVOLVE_WINDOW:
			if not self.IsShow():
				return

		self.SetOnTopWindowNone()

		if exceptToggle == False:
			self.wndPetInformation.PetFeedToggleButtonUpAll()
			self.wndPetInformation.feedIndex = player.FEED_BUTTON_MAX

		self.ClearFeedItems()

		if self.questionDialog:
			self.questionDialog.Close()

		self.Hide()

		player.SetOpenPetFeedWindow(False)

	def Destroy(self):
		del self.FeedItems[:]
		del	self.FeedItemsCount[:]
		del self.FeedItemDummy[:]
		self.FeedItems		= None
		self.FeedItemsCount	= None
		self.FeedItemSlot	= None
		self.FeedItemDummy  = None
		self.questionDialog = None
		
		self.questionDialogEmptyPos = -1
		self.questionDialogItemPos = -1
	
	
	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			self.__LoadScript("UIScript/petFeedWindow.py")
				
		except:
			import exception
			exception.Abort("petFeedWindow.LoadWindow.LoadObject")
			
		try:				
			self.GetChild("PetFeed_TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
			
			# Item slot grid
			FeedItemSlot = self.GetChild("FeedItemSlot")
			FeedItemSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))			
			FeedItemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			FeedItemSlot.SetUnselectItemSlotEvent(ui.__mem_func__(self.UnselectItemSlot))
			FeedItemSlot.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
			FeedItemSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
			FeedItemSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
			self.FeedItemSlot = FeedItemSlot
			
			self.FeedItems		= []
			self.FeedItemsCount = []
			
			# Used as a sub-container for items to check their positions
			self.FeedItemDummy	= []
						
			self.ClearMouseEventFeedItems()

			self.feedButton = self.GetChild("FeedButton")
			if self.feedButton:
				self.feedButton.SetEvent(ui.__mem_func__(self.ClickPetFeedButton))

			self.questionDialog = uicommon.QuestionDialog2()
			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__ItemMoveQuestionDialogAccept))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__ItemMoveQuestionDialogCancel))
			self.questionDialog.Close()
			
		except:
			import exception
			exception.Abort("petFeedWindow.LoadWindow.BindObject")
			
	def __LoadScript(self, fileName):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, fileName)
		
	def OverInItem(self, slotIndex):
		if None != self.wndPetInformation.tooltipItem:
			invenPos = self.FeedItems[slotIndex]
			if invenPos != -1:
				self.wndPetInformation.tooltipItem.SetInventoryItem(invenPos, player.INVENTORY)
				
		return
		
	def OverOutItem(self):
		if None != self.wndPetInformation.tooltipItem:
			self.wndPetInformation.tooltipItem.HideToolTip()
		return
		
	def UseItemSlot(self, slotIndex):
		self.RemoveItemSlot(slotIndex)
		return
	
	def UnselectItemSlot(self, slotIndex):
		self.RemoveItemSlot(slotIndex)
		return
		
	def SelectItemSlot(self, slotIndex):
	
		self.RemoveItemSlot(slotIndex)
		return
		
	def RemoveItemSlot(self, slotIndex):
		if mousemodule.mouseController.isAttached():
			return
		
		# Unlock item that was inside feed window
		inven_slot_pos = self.FeedItems[slotIndex]
		if inven_slot_pos != -1:
			if inven_slot_pos >= player.INVENTORY_PAGE_SIZE:
				inven_page = self.wndPetInformation.inven.GetInventoryPageIndex()
				inven_slot_pos -= (inven_page * player.INVENTORY_PAGE_SIZE)
				
			self.wndPetInformation.inven.wndItem.SetCanMouseEventSlot(inven_slot_pos)
		
		self.DeleteDataDummySlot(slotIndex, self.FeedItems[slotIndex])
		self.FeedItems[slotIndex] = -1
		self.FeedItemsCount[slotIndex] = 0
		self.FeedItemSlot.ClearSlot(slotIndex)		
		self.FeedItemSlot.RefreshSlot()

	# Search for empty slot space for item
	# If not found, return -1
	def SearchEmptySlot(self, size):
		
		for value in range(player.PET_FEED_SLOT_MAX):
			
			if 0 == self.FeedItemDummy[value]:	# Check if value inside this slot is empty
			
				if 1 == size:
					return value
					
				emptySlotIndex	= value
				searchSucceed	= True
				
				for i in range(size - 1):
					emptySlotIndex = emptySlotIndex + FEED_WINDOW_X_SIZE
				
					if emptySlotIndex >= player.PET_FEED_SLOT_MAX:
						searchSucceed = False
						continue
					
					if 1 == self.FeedItemDummy[emptySlotIndex]:
						searchSucceed = False
			
				if True == searchSucceed:
					return value
				
		return -1
	
	# Move items inside the feed window (item slot grid)
	def ItemMoveFeedWindow(self, slotWindow, slotIndex):
		if player.INVENTORY == slotWindow:
			attachSlotType = player.SLOT_TYPE_INVENTORY
		else:
			return False
	
		checkTime = app.GetGlobalTimeStamp() - self.feedButtonClickTime
		if checkTime < 2:
			if slotIndex in self.backupFeedItems:
				return False
		else:
			self.backupFeedItems = []
	
		mousemodule.mouseController.DeattachObject()
		
		selectedItemVNum = player.GetItemIndex(slotWindow, slotIndex)
		count			 = player.GetItemCount(slotWindow, slotIndex)
		
		mousemodule.mouseController.AttachObject(self, attachSlotType, slotIndex, selectedItemVNum, count)
		
		item.SelectItem(selectedItemVNum)
		itemSize = item.GetItemSize()
		
		emptySlotPos = self.SearchEmptySlot(itemSize[1])

		if -1 != emptySlotPos:
			self.ProcessItemMove(slotIndex, emptySlotPos)
			return True
			
		return False
		
	def ProcessItemMove(self, slotIndex, emptySlotIndex):
		itemVnum = player.GetItemIndex(player.INVENTORY, slotIndex)
		item.SelectItem(itemVnum)
		
		# If item has one or more attributes, display a question dialog to continue
		if item.GetItemType() in [item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR]:
			metinSlot = [player.GetItemMetinSocket(player.INVENTORY, slotIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
			attrSlot = [player.GetItemAttribute(player.INVENTORY, slotIndex, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
			
			attributeCount = 0
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				type = attrSlot[i][0]
				value = attrSlot[i][1]
				
				if value:
					attributeCount += 1
					
			if attributeCount >= 3:
				self.questionDialogEmptyPos = emptySlotIndex
				self.questionDialogItemPos = slotIndex
				
				self.questionDialog.SetText1(localeinfo.SECOND_CONFIRM_PET_FEED_QUESTION_1 % attributeCount)
				self.questionDialog.SetText2(localeinfo.SECOND_CONFIRM_PET_FEED_QUESTION_2)
				self.questionDialog.SetTop()
				self.questionDialog.Open()
				
				if mousemodule.mouseController.isAttached():
					mousemodule.mouseController.DeattachObject()
				return

		# Item did not have any attributes, move it to the feed window
		self.InsertItemToSlot(emptySlotIndex)

				
	def __ItemMoveQuestionDialogAccept(self):
		attachSlotType = player.SLOT_TYPE_INVENTORY
		selectedItemVNum = player.GetItemIndex(player.INVENTORY, self.questionDialogItemPos)
		count			 = player.GetItemCount(player.INVENTORY, self.questionDialogItemPos)
		
		mousemodule.mouseController.AttachObject(self, attachSlotType, self.questionDialogItemPos, selectedItemVNum, count)
		
		self.InsertItemToSlot(self.questionDialogEmptyPos)
		
		# Clear question dialog data for further use
		self.__ClearItemMoveQuestionDialog()
		
	def __ItemMoveQuestionDialogCancel(self):
		self.__ClearItemMoveQuestionDialog()
		
	def __ClearItemMoveQuestionDialog(self):
		if self.questionDialog:
			self.questionDialog.Close()
			
		# Clear the locked item (it will stay locked if it was put into the feed window)
		inven_slot_pos = self.questionDialogItemPos
		if inven_slot_pos != -1:
			if inven_slot_pos >= player.INVENTORY_PAGE_SIZE:
				inven_page = self.wndPetInformation.inven.GetInventoryPageIndex()
				inven_slot_pos -= (inven_page * player.INVENTORY_PAGE_SIZE)
				
			self.wndPetInformation.inven.wndItem.SetCanMouseEventSlot(inven_slot_pos)
			
		self.questionDialogEmptyPos = -1
		self.questionDialogItemPos = -1
		
	def SelectEmptySlot(self, slotIndex):
		attachedSlotType	= mousemodule.mouseController.GetAttachedType()			
		attachedSlotPos		= mousemodule.mouseController.GetAttachedSlotNumber()
		
		if player.SLOT_TYPE_INVENTORY != attachedSlotType:
			return False
		
		self.ItemMoveFeedWindow(player.INVENTORY, attachedSlotPos)
		
	def InsertItemToSlot(self, slotIndex):
		checkTime = app.GetGlobalTimeStamp() - self.feedButtonClickTime
		if checkTime < 2:
			if slotIndex in self.backupFeedItems:
				return False
		else:
			self.backupFeedItems = []
				
		if not mousemodule.mouseController.isAttached():
			return False
		
		attachedSlotType	= mousemodule.mouseController.GetAttachedType()			
		attachedSlotPos		= mousemodule.mouseController.GetAttachedSlotNumber()
		attachedItemCount	= mousemodule.mouseController.GetAttachedItemCount()
		attachedItemVNum	= player.GetItemIndex(attachedSlotPos)
		item.SelectItem(attachedItemVNum)		
		
		itemType	= item.GetItemType()
		itemSubType = item.GetItemSubType()			
		
		# Return if item is beging attached from not inventory window
		if player.SLOT_TYPE_INVENTORY != attachedSlotType:
			return False
			
		# Return if item position is bigger than player.ITEM_SLOT_COUNT
		if attachedSlotPos >= player.ITEM_SLOT_COUNT: 
			return False
		
		# Return if there is no pet summoned
		petVNum = player.GetActivePetItemVNum()
		if 0 == petVNum:
			return False
			
		# Return if active pet is being dragged to the window
		if item.ITEM_TYPE_PET == itemType and itemSubType == item.PET_UPBRINGING:
			activePetId = player.GetActivePetItemId()
			petId = player.GetItemMetinSocket(attachedSlotPos, 2)
			if petId == activePetId:
				return False
				
		# Display a msg if item type does not correspond to condtions
		if self.wndPetInformation.CantFeedItem(attachedSlotPos):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_FEED_TYPE)
			return False
			
		if -1 != self.FeedItems[slotIndex]:
			return False
		
		if attachedSlotPos not in self.FeedItems:
			mousemodule.mouseController.DeattachObject()
			
			invenItemCount = player.GetItemCount(attachedSlotPos)
			if attachedItemCount != invenItemCount:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_FEED_SPLIT_ITEM)
				return False
			
			self.FeedItems[slotIndex] = attachedSlotPos			
			self.FeedItemsCount[slotIndex] = attachedItemCount
			self.InsertDataDummySlot(slotIndex, attachedItemVNum)
			self.FeedItemSlot.SetItemSlot(slotIndex, attachedItemVNum, attachedItemCount)
			self.FeedItemSlot.RefreshSlot()
			
		return True
		
		
	def InsertDataDummySlot(self, slotIndex, vnum):
	
		self.FeedItemDummy[slotIndex] = 1
	
		item.SelectItem(vnum)
		itemSize = item.GetItemSize(vnum)
		
		if 1 == itemSize[1]:
			return
		
		addSlotIndex = slotIndex
		
		for value in range(itemSize[1] - 1):
			addSlotIndex = addSlotIndex + FEED_WINDOW_X_SIZE
		
			if addSlotIndex >= player.PET_FEED_SLOT_MAX:
				return
				
			self.FeedItemDummy[addSlotIndex] = 1
			
		
	def DeleteDataDummySlot(self, slotIndex, InvenPos):
	
		vnum = player.GetItemIndex(InvenPos)
		item.SelectItem(vnum)
		itemSize = item.GetItemSize(vnum)
		
		self.FeedItemDummy[slotIndex] = 0
		
		if 1 == itemSize[1]:
			return
			
		delSlotIndex = slotIndex
		
		for value in range(itemSize[1] - 1):
			delSlotIndex = delSlotIndex + FEED_WINDOW_X_SIZE
		
			if delSlotIndex >= player.PET_FEED_SLOT_MAX:
				return
				
			self.FeedItemDummy[delSlotIndex] = 0
		
		
	# Send feed packet if there are items inside the window
	def ClickPetFeedButton(self):
		resultFeedItems = [value for value in self.FeedItems if value != -1]
		resultFeedItemCounts = [value for value in self.FeedItemsCount if value != 0]

		if resultFeedItems:
			if net.SendPetFeedPacket(self.wndPetInformation.feedIndex, resultFeedItems, resultFeedItemCounts):
				self.feedButtonClickTime = app.GetGlobalTimeStamp()

	def ClearMouseEventFeedItems(self):
		# Unlock items that are inside the feed window
		for inven_slot_pos in self.FeedItems:
			if inven_slot_pos != -1:
				if inven_slot_pos >= player.INVENTORY_PAGE_SIZE:
					inven_page = self.wndPetInformation.inven.GetInventoryPageIndex()
					inven_slot_pos -= (inven_page * player.INVENTORY_PAGE_SIZE)
					
				self.wndPetInformation.inven.wndItem.SetCanMouseEventSlot(inven_slot_pos)
	
		del self.FeedItems[:]
		del self.FeedItemsCount[:]
		del self.FeedItemDummy[:]
		
		for value in range(0, player.PET_FEED_SLOT_MAX):			
			self.FeedItems.append(-1)
			self.FeedItemsCount.append(0)
			self.FeedItemDummy.append(0)
	
	def BackUpSucceedFeedItems(self):
		self.backupFeedItems = self.FeedItems[:]
		
	def OnUpdate(self):
		if self.wndPetInformation.inven == 0:
			return
		
		inven = self.wndPetInformation.inven
		invenPage = inven.GetInventoryPageIndex()
		
		min_range = invenPage * player.INVENTORY_PAGE_SIZE
		max_range = (invenPage + 1) * player.INVENTORY_PAGE_SIZE
		
		# Lock items that are inside the feed window
		for inven_slot_pos in self.FeedItems:
			if inven_slot_pos == -1:
				continue
				
			if min_range <= inven_slot_pos < max_range:
				inven_slot_pos = inven_slot_pos - min_range
				inven.wndItem.SetCantMouseEventSlot(inven_slot_pos)
				
		if self.questionDialogItemPos != -1:
			inven_slot_pos = self.questionDialogItemPos
			if min_range <= inven_slot_pos < max_range:
				inven_slot_pos = inven_slot_pos - min_range
				inven.wndItem.SetCantMouseEventSlot(inven_slot_pos)
				
		return
	
	def OnTop(self):
		if not self.wndPetInformation:
			return
			
		if not self.wndPetInformation.interface:
			return
			
		interface = self.wndPetInformation.interface
		interface.SetOnTopWindow(player.ON_TOP_WND_PET_FEED)
		interface.RefreshMarkInventoryBag()
	
"""
		PetInformationWindow is opened through taskbar or 'P' key.
		Shows pet statistics and windows for attr change/pet revive.
"""
class PetInformationWindow(ui.ScriptWindow):
	wndPetFeed		= None
	tooltipItem		= None
	inven			= None
	wndPetHatching	= None
	wndPetNameChange= None
	wndPetMiniInfo	= None
	feedIndex		= player.FEED_BUTTON_MAX
	skillSlot		= []
	feedButton		= []
	
	SkillBookSlotIndex	= -1
	SkillBookInvenIndex = -1
	
	SkillBookDelSlotIndex	= -1
	SkillBookDelInvenIndex	= -1
	
	typeInfo = {
		1	:	localeinfo.PET_ATTR_DETERMINE_TYPE1,
		2	:	localeinfo.PET_ATTR_DETERMINE_TYPE2,
		3	:	localeinfo.PET_ATTR_DETERMINE_TYPE3,
		4	:	localeinfo.PET_ATTR_DETERMINE_TYPE4,
		5	:	localeinfo.PET_ATTR_DETERMINE_TYPE5,
		6	:	localeinfo.PET_ATTR_DETERMINE_TYPE6,
		7	:	localeinfo.PET_ATTR_DETERMINE_TYPE7,
		8	:	localeinfo.PET_ATTR_DETERMINE_TYPE8,
	}
	
	class DescriptionBox(ui.Window):
		def __init__(self):
			ui.Window.__init__(self)
			self.descIndex = 0
		def __del__(self):
			ui.Window.__del__(self)
		def SetIndex(self, index):
			self.descIndex = index
		def OnRender(self):
			event.RenderEventSet(self.descIndex)

	def __init__(self):
		if app.USE_GROWTH_NEW_EVOLVE_WINDOW:
			self.evolveWnd = None

		ui.ScriptWindow.__init__(self)

		self.interface = None
		self.inven = None
		self.tooltipItem = None

		self.isLoaded = 0
		self.state = player.PET_WINDOW_INFO
		self.tabDict		= None
		self.tabButtonDict	= None
		self.pageDict		= None
		self.AffectShower	= None
		self.popupDialog	= None
		self.questionDialog	= None
		self.skillUpgradeGold	= 0
		self.skillUpgradeSlot	= -1
		self.skillUpgradeIndex	= -1
		self.tooptipPetSkill	= None
		self.attrChangeIndex	= [-1, -1, -1]
		self.petReviveIndex		= -1
		self.petReviveItems	= [-1 for i in xrange(player.PET_REVIVE_MATERIAL_SLOT_MAX)]
		self.petReviveItemsCount	= [0 for i in xrange(player.PET_REVIVE_MATERIAL_SLOT_MAX)]
		self.isPetReviveResultTooltip = False
		self.descIndex = 0
		self.desc_Y = DEFAULT_DESC_Y
		self.SetWindowName("PetInformationWindow")
		self.__LoadWindow()
		self.wndPetHatching		= PetHatchingWindow(self)
		self.wndPetNameChange	= PetNameChangeWindow(self)
		self.wndPetMiniInfo 	= PetMiniInfomationWindow(self)
		self.wndPetFeed			= PetFeedWindow(self)

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()
		ui.ScriptWindow.Show(self)
		self.SetTop()

	def Hide(self):
		if app.USE_GROWTH_NEW_EVOLVE_WINDOW and self.evolveWnd:
			self.evolveWnd.Close()

		if self.wndPetFeed:
			self.wndPetFeed.Close()

		wndMgr.Hide(self.hWnd)

	def BindInterfaceClass(self, interface):
		self.interface = proxy(interface)

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return
		self.isLoaded = 1
		
		try:
			self.__LoadScript("UIScript/petInformationWindow.py")
				
		except:
			import exception
			exception.Abort("petInformationWindow.LoadWindow.__LoadScript")
		
		
		
		
		try:
			# Background
			# if localeinfo.IsARABIC():
				# self.GetChild("PetUIBG").LeftRightReverse()
				
			# Close Button Event
			self.GetChild("CloseButton").SetEvent(ui.__mem_func__(self.Close))
			
			# Page Tabs
			self.tabDict = {
				player.PET_WINDOW_INFO					: self.GetChild("Tab_01"),
				player.PET_WINDOW_ATTR_CHANGE			: self.GetChild("Tab_02"),
				player.PET_WINDOW_PRIMIUM_FEEDSTUFF		: self.GetChild("Tab_03"),
			}

			self.tabButtonDict = {
				player.PET_WINDOW_INFO					: self.GetChild("Tab_Button_01"),
				player.PET_WINDOW_ATTR_CHANGE			: self.GetChild("Tab_Button_02"),
				player.PET_WINDOW_PRIMIUM_FEEDSTUFF		: self.GetChild("Tab_Button_03"),
			}
			
			self.pageDict = {
				player.PET_WINDOW_INFO					: self.GetChild("PetInfo_Page"),
				player.PET_WINDOW_ATTR_CHANGE			: self.GetChild("PetAttrChange_Page"),
				player.PET_WINDOW_PRIMIUM_FEEDSTUFF		: self.GetChild("PetPremiumFeefstuff_Page"),
			}
			
			for (tabKey, tabButton) in self.tabButtonDict.items():
				tabButton.SetEvent(ui.__mem_func__(self.__OnClickTabButton), tabKey)
			
			# UpBringing Pet Slot
			wndUpBringingPetSlot = self.GetChild("UpBringing_Pet_Slot")
			wndUpBringingPetSlot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
			
			if localeinfo.IsARABIC():
				wndUpBringingPetSlot.SetPosition(25,50)
				
			self.wndUpBringingPetSlot	= wndUpBringingPetSlot
			
			# Feed Life Time Button
			feedLifeTimeButton = self.GetChild("FeedLifeTimeButton")
			if feedLifeTimeButton:
				feedLifeTimeButton.SetToggleDownEvent(ui.__mem_func__(self.ClickFeedLifeTimeButtonDown))
				feedLifeTimeButton.SetToggleUpEvent(ui.__mem_func__(self.ClickFeedLifeTimeButtonUp))
			self.feedButton.append(feedLifeTimeButton)
				
			# Feed Evolution Button
			feedEvolButton = self.GetChild("FeedEvolButton")
			if feedEvolButton:
				feedEvolButton.SetToggleDownEvent(ui.__mem_func__(self.ClickFeedEvolButtonDown))
				feedEvolButton.SetToggleUpEvent(ui.__mem_func__(self.ClickFeedEvolButtonUp))
			self.feedButton.append(feedEvolButton)
			
			# Feed EXP Button
			feedExpButton = self.GetChild("FeedExpButton")
			if feedExpButton:
				feedExpButton.SetToggleDownEvent(ui.__mem_func__(self.ClickFeedExpButtonDown))
				feedExpButton.SetToggleUpEvent(ui.__mem_func__(self.ClickFeedExpButtonUp))
			self.feedButton.append(feedExpButton)
			
			for value in range(player.FEED_BUTTON_MAX):
				self.feedButton[value].DisableFlash()
				
			# Life Time Gauge
			self.lifeTimeGauge = self.GetChild("LifeGauge")
			self.lifeTimeGauge.SetScale(1.61, 1.0)
			self.lifeTimeGauge.SetWindowHorizontalAlignLeft()
			
			if localeinfo.IsARABIC():
				self.lifeTimeGauge.SetPosition(0,0)
						
			# EXP Gauges
			expGauge = []
			self.expGaugeBoard = self.GetChild("UpBringing_Pet_EXP_Gauge_Board")
			expGauge.append(self.GetChild("UpBringing_Pet_EXPGauge_01"))
			expGauge.append(self.GetChild("UpBringing_Pet_EXPGauge_02"))
			expGauge.append(self.GetChild("UpBringing_Pet_EXPGauge_03"))
			expGauge.append(self.GetChild("UpBringing_Pet_EXPGauge_04"))
			expGauge.append(self.GetChild("UpBringing_Pet_EXPGauge_05"))
			
			for exp in expGauge:
				exp.SetSize(0, 0)
			
			self.expGauge	= expGauge
			self.tooltipEXP = TextToolTip()
			self.tooltipEXP.Hide()
			
			# Skill slot
			arabic_start_pos_x = 36
			
			for value in range(SKILL_SLOT_MAX):
				self.skillSlot.append(self.GetChild("PetSkillSlot"+str(value)))
				self.skillSlot[value].SetCoverButton(0, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, False, False)
				self.skillSlot[value].SetAlwaysRenderCoverButton(0)
				self.skillSlot[value].AppendSlotButton("d:/ymir work/ui/game/windows/btn_plus_up.sub",\
											"d:/ymir work/ui/game/windows/btn_plus_over.sub",\
											"d:/ymir work/ui/game/windows/btn_plus_down.sub")
				if localeinfo.IsARABIC():
					# 36, 100, 164
					self.skillSlot[value].SetPosition(arabic_start_pos_x, 365)
					arabic_start_pos_x = arabic_start_pos_x + 64
				
			# Skill slot empty event
			self.skillSlot[0].SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySkillSlot1))
			self.skillSlot[1].SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySkillSlot2))
			self.skillSlot[2].SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySkillSlot3))
			
			# Skill slotselect Item event
			self.skillSlot[0].SetSelectItemSlotEvent(ui.__mem_func__(self.SetSelectItemSlotEvent1))
			self.skillSlot[1].SetSelectItemSlotEvent(ui.__mem_func__(self.SetSelectItemSlotEvent2))
			self.skillSlot[2].SetSelectItemSlotEvent(ui.__mem_func__(self.SetSelectItemSlotEvent3))
			
			# Skill slot over in event 
			self.skillSlot[0].SetOverInItemEvent(ui.__mem_func__(self.OverInSkillSlot1))
			self.skillSlot[1].SetOverInItemEvent(ui.__mem_func__(self.OverInSkillSlot2))
			self.skillSlot[2].SetOverInItemEvent(ui.__mem_func__(self.OverInSkillSlot3))
			
			# Skill slot over out event 
			self.skillSlot[0].SetOverOutItemEvent(ui.__mem_func__(self.OverOutSkillSlot1))
			self.skillSlot[1].SetOverOutItemEvent(ui.__mem_func__(self.OverOutSkillSlot2))
			self.skillSlot[2].SetOverOutItemEvent(ui.__mem_func__(self.OverOutSkillSlot3))
			
			self.skillSlot[0].SetPressedSlotButtonEvent(ui.__mem_func__(self.OnPressedSkill1SlotButton))
			self.skillSlot[1].SetPressedSlotButtonEvent(ui.__mem_func__(self.OnPressedSkill2SlotButton))
			self.skillSlot[2].SetPressedSlotButtonEvent(ui.__mem_func__(self.OnPressedSkill3SlotButton))
			
			# Initialize skill delete question dialog
			self.questionSkillDelDlg = uicommon.QuestionDialog2()
			self.questionSkillDelDlg.SetAcceptEvent(ui.__mem_func__(self.__SkillDeleteQuestionDialogAccept))
			self.questionSkillDelDlg.SetCancelEvent(ui.__mem_func__(self.__SkillDeleteQuestionDialogCancel))
			self.questionSkillDelDlg.Close()
			
			# Initialize skill learn question dialog
			self.questionDialog1 = uicommon.QuestionDialog()
			self.questionDialog1.SetAcceptEvent(ui.__mem_func__(self.__SkillLearnQuestionDialogAccept))
			self.questionDialog1.SetCancelEvent(ui.__mem_func__(self.__SkillLearnQuestionDialogCancel))
			self.questionDialog1.Close()
			
			# Initialize skill upgrade question dialog
			self.questionDialog2 = uicommon.QuestionDialog2()
			self.questionDialog2.SetText1(localeinfo.PET_SKILL_UPGRADE_QUESTION_DLG_MSG1)
			self.questionDialog2.SetText2("")
			self.questionDialog2.SetAcceptEvent(ui.__mem_func__(self.__SkillUpgradeQuestionDialogAccept))
			self.questionDialog2.SetCancelEvent(ui.__mem_func__(self.__SkillUpgradeQuestionDialogCancel))
			self.questionDialog2.Close()
				
			# Determine Button
			self.GetChild("DetermineButton").SetEvent(ui.__mem_func__(self.ClickDetermineButton))
				
			# Attr Change Slot
			attrChangeSlot = self.GetChild("Change_Pet_Slot")
			attrChangeSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptyAttrChangeSlot))
			attrChangeSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectAttrChangeItemSlot))
			attrChangeSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInAttrChangeItem))
			attrChangeSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutAttrChangeItem))
			self.attrChangeSlot = attrChangeSlot
		
			# Attr Change Button
			self.attrChangeButton = self.GetChild("Pet_Change_Button")
			self.attrChangeButton.SetEvent(ui.__mem_func__(self.ClickAttrChangeButton))
			self.attrChangeButton.Hide()
			
			# Attr Change Close Button
			self.attrCloseButton = self.GetChild("Pet_OK_Button")		
			self.attrCloseButton.SetEvent(ui.__mem_func__(self.ClickAttrClearButton))
			
			# Attr Change Type Text
			self.attrChangeText = self.GetChild("PetDetermineInfoText")

			# Revive description window
			self.reviveDescWindow = self.GetChild("desc_window")
			
			# Revive description box
			self.descriptionBox = self.DescriptionBox()
			self.descriptionBox.Show()
			self.descriptionBox.SetParent(self.reviveDescWindow)

			# Revive description prev/next buttons
			self.petReviveDescPrevButton = self.GetChild("PetReviveDescPrevButton")
			self.petReviveDescNextButton = self.GetChild("PetReviveDescNextButton")
			self.petReviveDescPrevButton.SetEvent(ui.__mem_func__(self.PetPremiumFeedStuffPrevDescriptionPage))
			self.petReviveDescNextButton.SetEvent(ui.__mem_func__(self.PetPremiumFeedStuffNextDescriptionPage))
			
			# Revive UpBringing Pet Slot
			petReviveSlot = self.GetChild("PetReviveSlot")
			petReviveSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectPetReviveEmptySlot))
			petReviveSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectPetReviveItemSlot))
			petReviveSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInPetReviveSlot))
			petReviveSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutPetReviveSlot))
			self.petReviveSlot = petReviveSlot
			
			# Revived UpBringing Pet Slot
			petReviveResultSlot = self.GetChild("PetReviveResultSlot")
			petReviveResultSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInPetReviveResultSlot))
			petReviveResultSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutPetReviveResultSlot))
			self.petReviveResultSlot = petReviveResultSlot
			
			# Revive Material Slot Grid
			petReviveMaterialSlot = self.GetChild("PetReviveMaterialSlot")
			petReviveMaterialSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectPetReviveMaterialEmptySlot))
			petReviveMaterialSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectPetReviveMaterialItemSlot))
			self.petReviveMaterialSlot = petReviveMaterialSlot
			
			# Revive Age/Material Count Texts 
			self.petReviveAgeText = self.GetChild("PetReviveAgeNumberText")
			self.petReviveResultAgeText = self.GetChild("PetReviveResultAgeNumerText")
			self.petReviveItemsCountText = self.GetChild("PetReviveMaterialCountText")
			
			# Revive Button
			self.petReviveButton = self.GetChild("PetReviveButton")
			self.petReviveButton.SetEvent(ui.__mem_func__(self.ClickPetReviveButton))
			
			# Revive Cancel Button
			self.petReviveCancelButton = self.GetChild("PetReviveCancelButton")
			self.petReviveCancelButton.SetEvent(ui.__mem_func__(self.ClickPetReviveCancelButton))
			
			# Initialize question dialog
			self.questionDialog = uicommon.QuestionDialog()
			self.questionDialog.Close()
			
			# Initialize info page and revive description
			self.SetState(player.PET_WINDOW_INFO)
			self.__DescPetPremiumFeedstuff()
		except:
			import exception
			exception.Abort("petInformationWindow.LoadWindow.BindObject")
			
	def OnPressEscapeKey(self):
		self.Close()
		return True
		
	def __LoadScript(self, fileName):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, fileName)
		
	def Destroy(self):
		self.isLoaded = 0

		if app.USE_GROWTH_NEW_EVOLVE_WINDOW and self.evolveWnd:
			self.evolveWnd.Destroy()
			del self.evolveWnd
			self.evolveWnd = None

		if self.wndPetFeed:
			self.wndPetFeed.Destroy()
			self.wndPetFeed = None

		self.interface = None
		self.inven = None
		self.tooltipItem = None

		self.ClearDictionary()
		self.wndUpBringingPetSlot = None	
		
		self.lifeTimeGauge	= None
		self.expGauge		= None
		self.expGaugeBoard	= None
		self.tooltipEXP		= None
			
		if self.wndPetHatching:
			self.wndPetHatching.Destroy()
			self.wndPetHatching = None
			
		if self.wndPetNameChange:
			self.wndPetNameChange.Destroy()
			self.wndPetNameChange = None
			
		if self.wndPetMiniInfo:
			self.wndPetMiniInfo.Destroy()
			self.wndPetMiniInfo = None
			
		if self.skillSlot:
			del self.skillSlot[:]
			
		if self.feedButton:
			del self.feedButton[:]
			
		self.feedIndex				= player.FEED_BUTTON_MAX		
		self.SkillBookSlotIndex  = -1
		self.SkillBookInvenIndex = -1
		
		SkillBookDelSlotIndex	= -1
		SkillBookDelInvenIndex	= -1

		self.skillUpgradeGold	 = 0
		self.skillUpgradeSlot	 = -1
		self.skillUpgradeIndex	 = -1
		self.attrChangeIndex	 = None
		self.petReviveIndex		 = -1
		self.petReviveItems	= None
		self.petReviveItemsCount = None
		self.isPetReviveResultTooltip	= False
		
		self.AffectShower		= None
		self.tooptipPetSkill	= None
		
		if self.questionDialog1:
			self.questionDialog1.Destroy()
		
		if self.questionDialog2:
			self.questionDialog2.Destroy()
			
		if self.questionSkillDelDlg:
			self.questionSkillDelDlg.Destroy()
			
		if self.popupDialog:
			self.popupDialog.Destroy()
			
		if self.questionDialog:
			self.questionDialog.Destroy()
			
		self.questionDialog1		= None
		self.questionDialog2		= None
		self.questionSkillDelDlg	= None
		self.popupDialog			= None
		self.questionDialog		= None
		
		self.tabDict		= None
		self.tabButtonDict	= None
		self.pageDict		= None
		
		self.descIndex = 0
		self.desc_Y = DEFAULT_DESC_Y
		
	def Close(self):
		if self.tooltipEXP:
			self.tooltipEXP.Hide()

		if app.USE_GROWTH_NEW_EVOLVE_WINDOW and self.evolveWnd:
			self.evolveWnd.Close()

		if self.wndPetFeed:
			self.wndPetFeed.Close()

		self.PetFeedToggleButtonUpAll()

		self.__ClearPetSkillSlot()
		
		self.__ClearSkillBookLearnEvent()
		self.__ClearSkillUpgradeEvent()
		self.__ClearSkillDeleteBookEvent()
		
		self.__ClearAttrChangeWindow()
		self.__ClearPetReviveWindow()
		
		if self.popupDialog:
			self.popupDialog.Close()
		
		if self.questionDialog:
			self.questionDialog.Close()
		self.Hide()
		
		net.SendPetWindowType(player.PET_WINDOW_INFO)
		
	def __OnClickTabButton(self, stateKey):
		if stateKey == self.state:
			return
			
		# Update server with current opened window
		if stateKey == player.PET_WINDOW_INFO:
			net.SendPetWindowType(player.PET_WINDOW_INFO)
			
		elif stateKey == player.PET_WINDOW_ATTR_CHANGE:
			net.SendPetWindowType(player.PET_WINDOW_ATTR_CHANGE)
			
		elif stateKey == player.PET_WINDOW_PRIMIUM_FEEDSTUFF:
			net.SendPetWindowType(player.PET_WINDOW_PRIMIUM_FEEDSTUFF)

	def PetWindowTypeResult(self, result):
		if result == player.PET_WINDOW_INFO:
			self.SetState(player.PET_WINDOW_INFO)
			
		elif result == player.PET_WINDOW_ATTR_CHANGE:
			self.SetState(player.PET_WINDOW_ATTR_CHANGE)
			
		elif result == player.PET_WINDOW_PRIMIUM_FEEDSTUFF:
			self.SetState(player.PET_WINDOW_PRIMIUM_FEEDSTUFF)
		
	def SetState(self, stateKey):
		self.state = stateKey

		for (tabKey, tabButton) in self.tabButtonDict.items():
			if stateKey!=tabKey:
				tabButton.SetUp()

		for tabValue in self.tabDict.itervalues():
			tabValue.Hide()

		for pageValue in self.pageDict.itervalues():
			pageValue.Hide()

		self.tabDict[stateKey].Show()
		self.pageDict[stateKey].Show()
		
		if self.interface:
			if stateKey == player.PET_WINDOW_INFO:
				self.interface.SetOnTopWindow(player.ON_TOP_WND_NONE)
				self.interface.RefreshMarkInventoryBag()
				
			elif stateKey == player.PET_WINDOW_ATTR_CHANGE:
				if app.USE_GROWTH_NEW_EVOLVE_WINDOW and self.evolveWnd:
					self.evolveWnd.Close()

				if self.wndPetFeed.IsShow():
					self.wndPetFeed.Close()

				self.interface.SetOnTopWindow(player.ON_TOP_WND_PET_ATTR_CHANGE)
				self.interface.RefreshMarkInventoryBag()

			elif stateKey == player.PET_WINDOW_PRIMIUM_FEEDSTUFF:
				if app.USE_GROWTH_NEW_EVOLVE_WINDOW and self.evolveWnd:
					self.evolveWnd.Close()

				if self.wndPetFeed.IsShow():
					self.wndPetFeed.Close()

				self.interface.SetOnTopWindow(player.ON_TOP_WND_PET_PRIMIUM_FEEDSTUFF)
				self.interface.RefreshMarkInventoryBag()

		# Clear attr change/revive windows
		self.__ClearAttrChangeWindow()
		self.__ClearPetReviveWindow()
		
	
	def GetState(self):
		return self.state
		
	def __ClearPetSkillSlot(self):
		for value in range(SKILL_SLOT_MAX):
			self.skillSlot[value].ClearSlot(0)
			self.skillSlot[value].SetCoverButton(0, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, SKILL_SLOT_ENABLE, False, False)
			self.skillSlot[value].SetAlwaysRenderCoverButton(0)
	
	
	# Skill upgrade button events
	def OnPressedSkill1SlotButton(self, slotIndex):
		self.OnPressedSkillSlotButton(0, slotIndex)
		
	def OnPressedSkill2SlotButton(self, slotIndex):
		self.OnPressedSkillSlotButton(1, slotIndex)
		
	def OnPressedSkill3SlotButton(self, slotIndex):
		self.OnPressedSkillSlotButton(2, slotIndex)
	
	# Open skill upgrade question dialog, triggered from OnPressedSkillXSlotButton
	def OnPressedSkillSlotButton(self, slotPos, slotIndex):
		self.OpenPetSkillUpGradeQuestionDialog(slotPos, slotIndex)
		
	def __MakePopupDialog(self):
		self.popupDialog = uicommon.PopupDialog()
		self.popupDialog.SetText("")
		
	def __OpenPopupDialog(self, str):
		if self.interface.IsShowDlgQuestionWindow():
			self.interface.CloseDlgQuestionWindow()
		
		if not self.popupDialog:
			self.__MakePopupDialog()
			
		self.popupDialog.SetText(str)
		self.popupDialog.SetTop()
		self.popupDialog.Open()
		
		
	def OpenPetSkillUpGradeQuestionDialog(self, slot, index):
		if not self.questionDialog2:
			self.questionDialog2 = uicommon.QuestionDialog2()
			self.questionDialog2.SetText1(localeinfo.PET_SKILL_UPGRADE_QUESTION_DLG_MSG1)
			self.questionDialog2.SetAcceptEvent(ui.__mem_func__(self.__SkillUpgradeQuestionDialogAccept))
			self.questionDialog2.SetCancelEvent(ui.__mem_func__(self.__SkillUpgradeQuestionDialogCancel))
			
		self.skillUpgradeGold	= 10000000
		self.skillUpgradeSlot	= slot
		self.skillUpgradeIndex	= index
		
		self.questionDialog2.SetText2(localeinfo.PET_SKILL_UPGRADE_QUESTION_DLG_MSG2 % (localeinfo.NumberToMoneyString(self.skillUpgradeGold)))
		self.questionDialog2.SetTop()
		self.questionDialog2.Open()
		
	def __SkillUpgradeQuestionDialogAccept(self):
	
		slot  = self.skillUpgradeSlot
		gold  = self.skillUpgradeGold
		index = self.skillUpgradeIndex
		
		self.__ClearSkillUpgradeEvent()
		
		# Check if player has enough money to upgrade skill
		if player.GetMoney() < gold:
			self.__OpenPopupDialog(localeinfo.PET_MSG_NOT_ENOUGH_MONEY)		
			return
			
		# Send skill upgrade request packet
		net.SendPetSkillUpgradeRequest(slot, index)
	
	def __SkillUpgradeQuestionDialogCancel(self):
		self.__ClearSkillUpgradeEvent()
	
	def __ClearSkillUpgradeEvent(self):
		if self.questionDialog2:
			self.questionDialog2.Close()
			
		self.skillUpgradeGold	= 0
		self.skillUpgradeSlot	= -1
		self.skillUpgradeIndex	= -1
		
	# Skill slot select events
	def SetSelectItemSlotEvent1(self, slotIndex):
		self.SetSelectItemSlotEvent(0)
		
	def SetSelectItemSlotEvent2(self, slotIndex):
		self.SetSelectItemSlotEvent(1)
		
	def SetSelectItemSlotEvent3(self, slotIndex):
		self.SetSelectItemSlotEvent(2)

	# Delete skill dialog, triggered from SetSelectItemSlotEventX
	def SetSelectItemSlotEvent(self, skillSlotIndex):
		# Return if there is no pet summoned	
		pet_id = player.GetActivePetItemId()
		if 0 == pet_id:
			return
			
		if not mousemodule.mouseController.isAttached():
			return
			
		# Return if skill slot index is not between 0~2
		if skillSlotIndex < 0 or skillSlotIndex >= SKILL_SLOT_MAX:
			return
		
		# Skill data
		(skill_count, pet_skill1, pet_skill_level1, pet_skill_cool1, pet_skill2, pet_skill_level2, pet_skill_cool2, pet_skill3, pet_skill_level3, pet_skill_cool3) = player.GetPetSkill(pet_id)
			
		if 0 == skill_count:
			return
			
		if skillSlotIndex >= skill_count:
			return
			
		if 0 == skillSlotIndex:
			if not pet_skill1:
				return
		elif 1 == skillSlotIndex:
			if not pet_skill2:
				return
		elif 2 == skillSlotIndex:
			if not pet_skill3:
				return
				
		attachedSlotType	= mousemodule.mouseController.GetAttachedType()			
		attachedSlotPos		= mousemodule.mouseController.GetAttachedSlotNumber()
		attachedItemCount	= mousemodule.mouseController.GetAttachedItemCount()
		attachedItemVNum	= player.GetItemIndex(attachedSlotPos)
		item.SelectItem(attachedItemVNum)		
		
		itemType	= item.GetItemType()
		itemSubType = item.GetItemSubType()			
		
		# Return if item is not from inventory
		if player.SLOT_TYPE_INVENTORY != attachedSlotType and\
			(player.SLOT_TYPE_SKILL_BOOK_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_STONE_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_GIFT_BOX_INVENTORY != attachedSlotType and app.ENABLE_SPECIAL_INVENTORY_SYSTEM and\
			player.SLOT_TYPE_ENCHANT_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_POTS_INVENTORY != attachedSlotType):

			return False
			
		# Return if item position is bigger than player.ITEM_SLOT_COUNT
		if attachedSlotPos >= player.ITEM_SLOT_COUNT: 
			return
		
		# Return if it is not a skill delete item
		if item.ITEM_TYPE_PET != itemType or item.PET_SKILL_DEL_BOOK != itemSubType:
			return
			
		# Initialize skill delete question dialog if it hasn't been yet
		if not self.questionSkillDelDlg:
			self.questionSkillDelDlg = uicommon.QuestionDialog2()
			self.questionSkillDelDlg.SetAcceptEvent(ui.__mem_func__(self.__SkillDeleteQuestionDialogAccept))
			self.questionSkillDelDlg.SetCancelEvent(ui.__mem_func__(self.__SkillDeleteQuestionDialogCancel))
			
			
		self.questionSkillDelDlg.SetText1(localeinfo.PET_SKILL_DELETE_QUESTION_DLG_MSG1)
		self.questionSkillDelDlg.SetText2(localeinfo.PET_SKILL_DELETE_QUESTION_DLG_MSG2)
		(w,h) = self.questionSkillDelDlg.GetTextSize1()
		self.questionSkillDelDlg.SetWidth(w+100)
		
		mousemodule.mouseController.DeattachObject()
		self.SkillBookDelSlotIndex  = skillSlotIndex
		self.SkillBookDelInvenIndex = attachedSlotPos
		self.questionSkillDelDlg.SetTop()
		self.questionSkillDelDlg.Open()
			
	def __SkillDeleteQuestionDialogAccept(self):
		pet_id = player.GetActivePetItemId()
		if pet_id:
			net.SendPetDeleteSkill(self.SkillBookDelSlotIndex, self.SkillBookDelInvenIndex)	
		
		self.__ClearSkillDeleteBookEvent()
		return
		
	def __SkillDeleteQuestionDialogCancel(self):
		self.__ClearSkillDeleteBookEvent()
		return
		
	def __ClearSkillDeleteBookEvent(self):
		# Lock skill delete item
		self.CanInvenSlot(self.SkillBookDelInvenIndex)
		
		self.SkillBookDelSlotIndex  = -1
		self.SkillBookDelInvenIndex = -1
		
		if self.questionSkillDelDlg:
			self.questionSkillDelDlg.Close()
		
	# Skill slot OverIn events
	def OverInSkillSlot1(self, slotIndex):
		self.OverInPetSkillSlot(0, slotIndex)
		
	def OverInSkillSlot2(self, slotIndex):
		self.OverInPetSkillSlot(1, slotIndex)
		
	def OverInSkillSlot3(self, slotIndex):
		self.OverInPetSkillSlot(2, slotIndex)
		
	# Show pet tooltip
	def OverInPetSkillSlot(self, slot, index):
		pet_id = player.GetActivePetItemId()
		if 0 == pet_id:
			return
		
		if self.tooptipPetSkill:
			self.tooptipPetSkill.SetPetSkill(pet_id, slot, index)
	
	# Skill slot OverOut events
	def OverOutSkillSlot1(self):
		self.tooptipPetSkill.HideToolTip()
		
	def OverOutSkillSlot2(self):
		self.tooptipPetSkill.HideToolTip()
		
	def OverOutSkillSlot3(self):
		self.tooptipPetSkill.HideToolTip()
	
	# Skill empty slot events
	def SelectEmptySkillSlot1(self, slotIndex):
		self.SelectEmptySkillSlot(0)
		
	def SelectEmptySkillSlot2(self, slotIndex):
		self.SelectEmptySkillSlot(1)
		
	def SelectEmptySkillSlot3(self, slotIndex):
		self.SelectEmptySkillSlot(2)

	# Triggered from SelectEmptySkillSlotX, opens learn skill dialog
	def SelectEmptySkillSlot(self, skillSlotIndex):
		# Return if there is no summoned pet		
		pet_id = player.GetActivePetItemId()
		if 0 == pet_id:
			return
			
		if not mousemodule.mouseController.isAttached():
			return
			
		if skillSlotIndex < 0 or skillSlotIndex >= SKILL_SLOT_MAX:
			return
		
		# Pet data
		(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
		
		# Skill data
		(skill_count, pet_skill1, pet_skill_level1, pet_skill_cool1, pet_skill2, pet_skill_level2, pet_skill_cool2, pet_skill3, pet_skill_level3, pet_skill_cool3) = player.GetPetSkill(pet_id)
			
		attachedSlotType	= mousemodule.mouseController.GetAttachedType()			
		attachedSlotPos		= mousemodule.mouseController.GetAttachedSlotNumber()
		attachedItemCount	= mousemodule.mouseController.GetAttachedItemCount()
		attachedItemVNum	= player.GetItemIndex(attachedSlotPos)
		item.SelectItem(attachedItemVNum)		
		
		itemType	= item.GetItemType()
		itemSubType = item.GetItemSubType()			
		
		# Return if item is not from inventory
		if player.SLOT_TYPE_INVENTORY != attachedSlotType and\
			(player.SLOT_TYPE_SKILL_BOOK_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_STONE_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_GIFT_BOX_INVENTORY != attachedSlotType and app.ENABLE_SPECIAL_INVENTORY_SYSTEM and\
			player.SLOT_TYPE_ENCHANT_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_POTS_INVENTORY != attachedSlotType):
			
			return False
			
		# Return if item position is bigger than player.ITEM_SLOT_COUNT
		if attachedSlotPos >= player.ITEM_SLOT_COUNT:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "1")
			return
		
		# Check if item is item.ITEM_TYPE_PET
		if item.ITEM_TYPE_PET != itemType:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "2")
			return
		
		# Return if skill delete item is dragged to an empty slot
		if item.PET_SKILL_DEL_BOOK == itemSubType:
			self.__OpenPopupDialog(localeinfo.PET_EMPTY_SKILL_SLOT_USE_ITEM)
			return
				
		# Return if it is not item.PET_SKILL subtype
		if item.PET_SKILL != itemSubType:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "3")
			return
			
		# Pet has no unlocked skills, return
		if 0 == skill_count:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "4")
			return
			
		if skillSlotIndex >= skill_count:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "5")
			return
			
		if 0 == skillSlotIndex:
			if pet_skill1:
				return
		elif 1 == skillSlotIndex:
			if pet_skill2:
				return
		elif 2 == skillSlotIndex:
			if pet_skill3:
				return
			
		# Return if pet's evolution is not player.PET_GROWTH_SKILL_OPEN_EVOL_LEVEL
		if evol_level < player.PET_GROWTH_SKILL_OPEN_EVOL_LEVEL:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "6")
			return
		
		if not self.questionDialog1:
			self.questionDialog1 = uicommon.QuestionDialog()
			self.questionDialog1.SetAcceptEvent(ui.__mem_func__(self.__SkillLearnQuestionDialogAccept))
			self.questionDialog1.SetCancelEvent(ui.__mem_func__(self.__SkillLearnQuestionDialogCancel))
			
			
		self.questionDialog1.SetText(localeinfo.PET_SKILL_LEARN_QUESTION_DLG_MSG % (item.GetItemName()))
		mousemodule.mouseController.DeattachObject()
		self.SkillBookSlotIndex  = skillSlotIndex
		self.SkillBookInvenIndex = attachedSlotPos
		self.questionDialog1.SetTop()
		self.questionDialog1.Open()
		
	def __SkillLearnQuestionDialogAccept(self):
		pet_id = player.GetActivePetItemId()
		if pet_id:
			net.SendPetLearnSkill(self.SkillBookSlotIndex, self.SkillBookInvenIndex)	
		
		self.__ClearSkillBookLearnEvent()
		return
		
	def __SkillLearnQuestionDialogCancel(self):
		self.__ClearSkillBookLearnEvent()
		return
		
	def __ClearSkillBookLearnEvent(self):
	
		self.CanInvenSlot(self.SkillBookInvenIndex)
		
		self.SkillBookSlotIndex  = -1
		self.SkillBookInvenIndex = -1
		
		if self.questionDialog1:
			self.questionDialog1.Close()

	def PetFeedToggleButtonUpAll(self, exclusion_index = player.FEED_BUTTON_MAX):
		for value in range(player.FEED_BUTTON_MAX):
			if exclusion_index == value:
				continue

			self.feedButton[value].SetUp()

	def ClickFeedLifeTimeButtonDown(self):
		self.ClickPetFeedButton(player.FEED_LIFE_TIME_EVENT)

	def ClickFeedLifeTimeButtonUp(self):
		if self.feedIndex == player.FEED_LIFE_TIME_EVENT:
			self.feedIndex = player.FEED_BUTTON_MAX

			if app.USE_GROWTH_NEW_EVOLVE_WINDOW and self.evolveWnd:
				self.evolveWnd.Close()

			self.wndPetFeed.Close()

	def ClickFeedEvolButtonDown(self):
		self.ClickPetFeedButton(player.FEED_EVOL_EVENT)

	def ClickFeedEvolButtonUp(self):
		if self.feedIndex == player.FEED_EVOL_EVENT:
			self.feedIndex = player.FEED_BUTTON_MAX

			if app.USE_GROWTH_NEW_EVOLVE_WINDOW and self.evolveWnd:
				self.evolveWnd.Close()

			self.wndPetFeed.Close()

	def ClickFeedExpButtonDown(self):
		self.ClickPetFeedButton(player.FEED_EXP_EVENT)

	def ClickFeedExpButtonUp(self):
		if self.feedIndex == player.FEED_EXP_EVENT:
			self.feedIndex = player.FEED_BUTTON_MAX

			if app.USE_GROWTH_NEW_EVOLVE_WINDOW and self.evolveWnd:
				self.evolveWnd.Close()

			self.wndPetFeed.Close()

	def IsActivateEvolButton(self, pet_id):
		# Return if there is no summoned pet
		if 0 == pet_id:
			return False
			
		(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
		
		if evol_level == player.PET_GROWTH_SKILL_OPEN_EVOL_LEVEL:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_OPEN_EVOL_BUTTON_LEVEL_MAX)
			return False
			
		evol_require = self.GetEvolInfo(evol_level)
		if 0 == evol_require:
			return False
		
		# Check level and experience limit for the first two evolutions
		if evol_level < player.PET_GROWTH_SKILL_OPEN_EVOL_LEVEL-1:
			# Level Check
			if pet_level < evol_require:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_OPEN_EVOL_BUTTON % evol_require)
				return False
			else:
				# EXP Check
				(curEXP, nextEXP, itemEXP, itemMaxEXP) = player.GetPetExpPoints(pet_id)
				
				if curEXP != nextEXP or (pet_level >= 55 and itemEXP != itemMaxEXP):
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_OPEN_EVOL_BUTTON_EXP_LACK)
					return False
					
		# Check level and age limit for the last evolution
		elif evol_level == player.PET_GROWTH_SKILL_OPEN_EVOL_LEVEL - 1:
			# Level Check
			if pet_level < evol_require:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_OPEN_EVOL_BUTTON % evol_require)
				return False
			else:
				# Age Check
				curTime = app.GetGlobalTimeStamp()
				birthSec = max(0, curTime - birthday)
				
				if birthSec < player.SPECIAL_EVOL_MIN_AGE:
					day = localeinfo.SecondToDayNumber(player.SPECIAL_EVOL_MIN_AGE)
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_OPEN_SPECIAL_EVOL_BUTTON % day)
					return False
			
		return True

	def ClickPetFeedButton(self, index):
		pet_id = player.GetActivePetItemId()
		if pet_id == 0:
			self.PetFeedToggleButtonUpAll()
			return

		if player.FEED_EVOL_EVENT == index:
			if self.IsActivateEvolButton(pet_id) == False:
				self.PetFeedToggleButtonUpAll(self.feedIndex)
				return

			if app.USE_GROWTH_NEW_EVOLVE_WINDOW:
				if self.wndPetFeed:
					self.wndPetFeed.Close(True)

				if not self.evolveWnd:
					self.evolveWnd = PetEvolveDialog(self)

				self.feedIndex = index
				self.PetFeedToggleButtonUpAll(self.feedIndex)

				self.evolveWnd.Open()
				return

		if app.USE_GROWTH_NEW_EVOLVE_WINDOW and self.evolveWnd:
			self.evolveWnd.Close(True)

		if not self.wndPetFeed:
			self.wndPetFeed = PetFeedWindow(self)

		self.feedIndex = index
		self.wndPetFeed.ClearFeedItems()
		self.wndPetFeed.Show()
		self.wndPetFeed.SetTop()

		self.PetFeedToggleButtonUpAll(self.feedIndex)
		# U5: programmatic openers (companion Feed button / feed-window rail tabs) must
		# press the matching legacy toggle DOWN like a physical click would have -- else
		# that toggle's next click re-opens (wiping the staged items) instead of closing.
		if index < len(self.feedButton) and self.feedButton[index]:
			self.feedButton[index].Down()

	def OnUpdate(self):
		self.RefreshStatus()
		
		# Lock used items 
		self.CantInvenSlot(self.SkillBookInvenIndex)
		self.CantInvenSlot(self.SkillBookDelInvenIndex	)	
		self.CantInvenSlot(self.petReviveIndex	)	
		
		for i in xrange(player.PET_WND_SLOT_ATTR_CHANGE_MAX):
			self.CantInvenSlot(self.attrChangeIndex[i])
			
		for i in xrange(player.PET_REVIVE_MATERIAL_SLOT_MAX):
			self.CantInvenSlot(self.petReviveItems[i])
		
		if self.expGaugeBoard.IsIn():
			self.tooltipEXP.Show()
		else:
			self.tooltipEXP.Hide()
					
		(xposEventSet, yposEventSet) = self.reviveDescWindow.GetGlobalPosition()
		event.UpdateEventSet(self.descIndex, xposEventSet+7, -(yposEventSet+self.desc_Y))
		self.descriptionBox.SetIndex(self.descIndex)
		self.descriptionBox.SetTop()
			
				
	def RefreshStatus(self):
		if self.isLoaded==0:
			return

		# If there is no summoned pet, close pet mini window and clear the main window
		pet_id = player.GetActivePetItemId()
		if 0 == pet_id:
			self.ClearStatus()
			if self.wndPetMiniInfo:
				self.wndPetMiniInfo.Close()
			return
			
		if not self.wndPetMiniInfo:
			return
			
		(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
		curTime = app.GetGlobalTimeStamp()
		
		# UpBringing Pet Slot Image
		CurPetItemVNum = player.GetActivePetItemVNum()
		self.wndUpBringingPetSlot.SetItemSlot(0, CurPetItemVNum)
		self.wndPetMiniInfo.SetItemSlot(CurPetItemVNum)
		
		# Pet Name
		self.GetChild("PetName").SetText(pet_nick);
		
		# Evolution Name
		self.GetChild("EvolName").SetText(self.__GetEvolName(evol_level))
		
		# Level
		self.GetChild("LevelValue").SetText(str(pet_level))
		
		# Age
		birthSec = max(0, curTime - birthday)
		self.GetChild("AgeValue").SetText(localeinfo.SecondToDay(birthSec))
		
		# Life Time Text
		(endTime, maxTime) = player.GetPetLifeTime(pet_id)			
		lifeTime = max(0, endTime - curTime)			
		self.GetChild("LifeTextValue").SetText(localeinfo.SecondToH(lifeTime) + " / " + localeinfo.SecondToH(maxTime) + " " +uiscriptlocale.PET_INFORMATION_LIFE_TIME)
		
		# Life Time Gauge
		self.SetLifeTime(lifeTime, maxTime)
		self.wndPetMiniInfo.SetLifeTime(lifeTime, maxTime)
		
		# HP, Def, SP Bonus Text
		self.GetChild("HpValue").SetText("+" + str("%0.1f" % pet_hp) + "%")
		self.GetChild("DefValue").SetText("+" + str("%0.1f" % pet_def) + "%")
		self.GetChild("SpValue").SetText("+" + str("%0.1f" % pet_sp) + "%")
		
		# EXP
		(curEXP, nextEXP, itemEXP, itemMaxEXP) = player.GetPetExpPoints(pet_id)

		curEXP		= unsigned32(curEXP)
		nextEXP		= unsigned32(nextEXP)
		itemEXP		= unsigned32(itemEXP)
		itemMaxEXP	= unsigned32(itemMaxEXP)
		self.SetExperience(curEXP, nextEXP, itemEXP, itemMaxEXP)
		self.wndPetMiniInfo.SetExperience(curEXP, nextEXP, itemEXP, itemMaxEXP)
		
		# Clear skill slots
		self.__ClearPetSkillSlot()
		
		# Clear skill slots on mini window
		self.wndPetMiniInfo.ClearSkillSlot()
			
		# Check for evolution conditions and enable flash effect
		# Enable feed button flash effect if pet is hungry
		# Enable item exp button flash effect if battle exp is full
		
		bMiniWindowFlash = False
		
		if self.PetEvolFlashEventCheck(pet_level, evol_level, birthday, curEXP, nextEXP, itemEXP, itemMaxEXP):
			bMiniWindowFlash = True
			
		if self.PetLifeTimeFlashEventCheck(lifeTime):
			bMiniWindowFlash = True
			
		if self.PetItemExpFlashEventCheck(curEXP, nextEXP, itemEXP, itemMaxEXP):
			bMiniWindowFlash = True
			
		if not bMiniWindowFlash:
			self.wndPetMiniInfo.OffFlashEvent()
		else:
			self.wndPetMiniInfo.OnFlashEvent()
		
		# >>> GROWTH PET SKILL REWORK (U7) BEGIN: feed all 6 mini slots via the per-index
		# getters. The legacy 3-skill block below stays for non-rework clients; under the
		# rework GetPetSkill is deliberately 3-clamped and would drop slots 4-6.
		# GATE on GetPetSkillCoolTimeByIndex: it is #ifdef GROWTH_PET_SKILL_REWORK in the
		# client binary, so it truly marks a rework build. GetPetSkillByIndex exists on
		# EVERY build -- keying on it would run the 6-slot loop on an OFF client, where
		# the getter's bounds checks are compiled out (per-frame OOB reads past slot 2).
		if hasattr(player, "GetPetSkillCoolTimeByIndex"):
			self.__RefreshPetSkillsByIndex(pet_id, pet_level, curTime)
			self.wndPetMiniInfo.Show()
			return
		# <<< GROWTH PET SKILL REWORK (U7) END
		
		# Skill data
		(skill_count, pet_skill1, pet_skill_level1, pet_skill_cool1, pet_skill2, pet_skill_level2, pet_skill_cool2, pet_skill3, pet_skill_level3, pet_skill_cool3) = player.GetPetSkill(pet_id)
		
		if skill_count:
			for value in range(skill_count):
				self.skillSlot[value].SetAlwaysRenderCoverButton(0, False)
				self.wndPetMiniInfo.SetAlwaysRenderCoverButton(value)
				
		if pet_skill1:
			self.skillSlot[0].SetPetSkillSlotNew(0, pet_skill1)
			self.skillSlot[0].SetSlotCount(0, pet_skill_level1)
			self.skillSlot[0].SetCoverButton(0)
			self.wndPetMiniInfo.SetSkillSlot(0, 0, pet_skill1)
			
			if player.PET_GROWTH_SKILL_LEVEL_MAX > pet_skill_level1:
				self.skillSlot[0].ShowSlotButton(0)
				
			(pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time) = skill.GetPetSkillInfo(pet_skill1)
			if skill.PET_SKILL_USE_TYPE_AUTO == pet_skill_use_type:
				if curTime <= pet_skill_cool1:
					curCoolTime = pet_skill_cool1 - curTime
					curCoolTime = pet_skill_cool_time - curCoolTime
					self.skillSlot[0].SetSlotCoolTime(0, pet_skill_cool_time, curCoolTime)
					self.wndPetMiniInfo.SetSkillCoolTime(0, 0, pet_skill_cool_time, curCoolTime)
				else:
					if self.AffectShower:
						self.AffectShower.SetPetSkillAffect(1, pet_skill1)
			
			elif skill.PET_SKILL_USE_TYPE_PASSIVE == pet_skill_use_type:	
				if self.AffectShower:
					self.AffectShower.SetPetSkillAffect(1, pet_skill1)
				
		if pet_skill2:
			self.skillSlot[1].SetPetSkillSlotNew(0, pet_skill2)
			self.skillSlot[1].SetSlotCount(0, pet_skill_level2)
			self.skillSlot[1].SetCoverButton(0)
			self.wndPetMiniInfo.SetSkillSlot(1, 0, pet_skill2)
			
			if player.PET_GROWTH_SKILL_LEVEL_MAX > pet_skill_level2:
				self.skillSlot[1].ShowSlotButton(0)
				
			(pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time) = skill.GetPetSkillInfo(pet_skill2)
			if skill.PET_SKILL_USE_TYPE_AUTO == pet_skill_use_type:
				if curTime <= pet_skill_cool2:
					curCoolTime = pet_skill_cool2 - curTime
					curCoolTime = pet_skill_cool_time - curCoolTime
					self.skillSlot[1].SetSlotCoolTime(0, pet_skill_cool_time, curCoolTime)
					self.wndPetMiniInfo.SetSkillCoolTime(1, 0, pet_skill_cool_time, curCoolTime)
				else:
					if self.AffectShower:
						self.AffectShower.SetPetSkillAffect(2, pet_skill2)
			
			elif skill.PET_SKILL_USE_TYPE_PASSIVE == pet_skill_use_type:	
				if self.AffectShower:
					self.AffectShower.SetPetSkillAffect(2, pet_skill2)
			
		if pet_skill3:
			self.skillSlot[2].SetPetSkillSlotNew(0, pet_skill3)
			self.skillSlot[2].SetSlotCount(0, pet_skill_level3)
			self.skillSlot[2].SetCoverButton(0)
			self.wndPetMiniInfo.SetSkillSlot(2, 0, pet_skill3)
			
			if player.PET_GROWTH_SKILL_LEVEL_MAX > pet_skill_level3:
				self.skillSlot[2].ShowSlotButton(0)
			
			(pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time) = skill.GetPetSkillInfo(pet_skill3)
			if skill.PET_SKILL_USE_TYPE_AUTO == pet_skill_use_type:
				if curTime <= pet_skill_cool3:
					curCoolTime = pet_skill_cool3 - curTime
					curCoolTime = pet_skill_cool_time - curCoolTime
					self.skillSlot[2].SetSlotCoolTime(0, pet_skill_cool_time, curCoolTime)
					self.wndPetMiniInfo.SetSkillCoolTime(2, 0, pet_skill_cool_time, curCoolTime)
				else:
					if self.AffectShower:
						self.AffectShower.SetPetSkillAffect(3, pet_skill3)
			
			elif skill.PET_SKILL_USE_TYPE_PASSIVE == pet_skill_use_type:	
				if self.AffectShower:
					self.AffectShower.SetPetSkillAffect(3, pet_skill3)		

		self.wndPetMiniInfo.Show()	
		
	# >>> GROWTH PET SKILL REWORK (U7) BEGIN
	def __RefreshPetSkillsByIndex(self, pet_id, pet_level, curTime):
		# 6-slot skill feed: mini window gets every slot; THIS window's own 3 legacy
		# slot widgets mirror what they can (the whole main window retires in U9).
		# Per-slot data = GetPetSkillByIndex (vnum/level) + GetPetSkillCoolTimeByIndex
		# (cooldown END timestamp; separate getter -- the 9-int tuple is unchanged so
		# positional unpackers elsewhere keep working).
		open1 = getattr(player, "PET_GROWTH_SKILL_OPEN_LEVEL_1", 90)
		open2 = getattr(player, "PET_GROWTH_SKILL_OPEN_LEVEL_2", 105)
		tier1 = getattr(player, "PET_GROWTH_SKILL_SLOT_TIER1_COUNT", 3)
		if pet_level >= open2:
			unlockedCount = MINI_SKILL_SLOT_MAX
		elif pet_level >= open1:
			unlockedCount = tier1
		else:
			unlockedCount = 0
		# Unlocked slots render as enabled cells (the legacy skill_count loop, but the
		# count is derived from the level gates -- the rework getter has no count).
		for i in xrange(unlockedCount):
			if i < len(self.skillSlot):
				self.skillSlot[i].SetAlwaysRenderCoverButton(0, False)
			self.wndPetMiniInfo.SetAlwaysRenderCoverButton(i)
		canReadCool = hasattr(player, "GetPetSkillCoolTimeByIndex")
		for i in xrange(MINI_SKILL_SLOT_MAX):
			skillData = player.GetPetSkillByIndex(pet_id, i)
			skillVnum = skillData[0]
			skillLevel = skillData[1]
			# level 0 = unlearned (the getter returns vnum + zero level by contract);
			# deliberate delta vs the legacy block, which keyed on the vnum alone.
			if not skillVnum or not skillLevel:
				continue
			if i < len(self.skillSlot):
				self.skillSlot[i].SetPetSkillSlotNew(0, skillVnum)
				self.skillSlot[i].SetSlotCount(0, skillLevel)
				self.skillSlot[i].SetCoverButton(0)
				if player.PET_GROWTH_SKILL_LEVEL_MAX > skillLevel:
					self.skillSlot[i].ShowSlotButton(0)
			self.wndPetMiniInfo.SetSkillSlot(i, 0, skillVnum)
			(pet_skill_name, pet_skill_desc, pet_skill_use_type, pet_skill_cool_time) = skill.GetPetSkillInfo(skillVnum)
			coolEnd = 0
			if canReadCool:
				coolEnd = player.GetPetSkillCoolTimeByIndex(pet_id, i)
			if skill.PET_SKILL_USE_TYPE_AUTO == pet_skill_use_type:
				if coolEnd and curTime <= coolEnd:
					curCoolTime = pet_skill_cool_time - (coolEnd - curTime)
					if i < len(self.skillSlot):
						self.skillSlot[i].SetSlotCoolTime(0, pet_skill_cool_time, curCoolTime)
					self.wndPetMiniInfo.SetSkillCoolTime(i, 0, pet_skill_cool_time, curCoolTime)
				else:
					if self.AffectShower:
						self.AffectShower.SetPetSkillAffect(i + 1, skillVnum)
			elif skill.PET_SKILL_USE_TYPE_PASSIVE == pet_skill_use_type:
				if self.AffectShower:
					self.AffectShower.SetPetSkillAffect(i + 1, skillVnum)
	# <<< GROWTH PET SKILL REWORK (U7) END

	def ClearStatus(self):
		self.wndUpBringingPetSlot.SetItemSlot(0, 0)
		self.GetChild("PetName").SetText("")
		self.GetChild("EvolName").SetText("")
		self.GetChild("LevelValue").SetText("")
		self.GetChild("AgeValue").SetText("")
		self.GetChild("LifeTextValue").SetText("")
		self.GetChild("DefValue").SetText("")
		self.GetChild("SpValue").SetText("")
		self.GetChild("HpValue").SetText("")
		self.SetExperience(0, 0, 0, 0)
		self.SetLifeTime(100, 100)
		self.__ClearPetSkillSlot()

		if app.USE_GROWTH_NEW_EVOLVE_WINDOW and self.evolveWnd:
			self.evolveWnd.Close()

		if self.wndPetFeed:
			if self.wndPetFeed.IsShow():
				self.wndPetFeed.Close()

		self.__ClearSkillBookLearnEvent()
		self.__ClearSkillDeleteBookEvent()
		self.__ClearSkillUpgradeEvent()
			
		if self.AffectShower:
			self.AffectShower.ClearPetSkillAffect()
			
		self.AllOffPetInfoFlashEvent()	

	# Lock item at position invenIndex
	def CantInvenSlot(self, invenIndex):
		if invenIndex == -1:
			return
		
		inven = self.inven
		invenPage = inven.GetInventoryPageIndex()
		
		min_range = invenPage * player.INVENTORY_PAGE_SIZE
		max_range = (invenPage + 1) * player.INVENTORY_PAGE_SIZE
			
		inven_slot_pos = invenIndex
			
		if min_range <= inven_slot_pos < max_range:
			inven_slot_pos = inven_slot_pos - min_range
			inven.wndItem.SetCantMouseEventSlot(inven_slot_pos)
			
	# Unlock item at position invenIndex
	def CanInvenSlot(self, invenIndex):
		if invenIndex == -1:
			return
			
		inven = self.inven
		invenPage = inven.GetInventoryPageIndex()
		
		min_range = invenPage * player.INVENTORY_PAGE_SIZE
		max_range = (invenPage + 1) * player.INVENTORY_PAGE_SIZE
			
		inven_slot_pos = invenIndex
			
		if min_range <= inven_slot_pos < max_range:
			inven_slot_pos = inven_slot_pos - min_range
			inven.wndItem.SetCanMouseEventSlot(inven_slot_pos)		
	
	def __GetEvolName(self, evol_level):
		if 1 == evol_level:
			return localeinfo.PET_INFORMATION_STAGE1
		elif 2 == evol_level:
			return localeinfo.PET_INFORMATION_STAGE2
		elif 3 == evol_level:
			return localeinfo.PET_INFORMATION_STAGE3
		elif 4 == evol_level:
			return localeinfo.PET_INFORMATION_STAGE4
			
		return localeinfo.PET_INFORMATION_STAGE1
		
	def PetAffectShowerRefresh(self):
		
		# Return if affectShower class was not bound
		if not self.AffectShower:
			return
			
		# Clear pet affects
		self.AffectShower.ClearPetSkillAffect()	
			
		# Return if there is no summoned pet
		pet_id = player.GetActivePetItemId()
		if 0 == pet_id:
			return
			
		curTime = app.GetGlobalTimeStamp()		
		
		# >>> GROWTH PET SKILL REWORK (U7) BEGIN: re-show ALL 6 slots' affects after a
		# skill update; the legacy 3-skill block below stays for non-rework clients.
		# Gate = the #ifdef-gated getter (see the RefreshStatus branch for why NOT
		# GetPetSkillByIndex, which exists on every build).
		if hasattr(player, "GetPetSkillCoolTimeByIndex"):
			canReadCool = 1   # implied by the gate; kept for the shared loop shape
			for i in xrange(MINI_SKILL_SLOT_MAX):
				skillData = player.GetPetSkillByIndex(pet_id, i)
				if not skillData[0] or not skillData[1]:
					continue
				(pet_skill_name, pet_skill_desc, pet_skill_use_type, pet_skill_cool_time) = skill.GetPetSkillInfo(skillData[0])
				coolEnd = 0
				if canReadCool:
					coolEnd = player.GetPetSkillCoolTimeByIndex(pet_id, i)
				if skill.PET_SKILL_USE_TYPE_AUTO == pet_skill_use_type:
					if coolEnd and curTime <= coolEnd:
						pass   # still cooling: no affect icon (legacy behavior)
					else:
						self.AffectShower.SetPetSkillAffect(i + 1, skillData[0])
				elif skill.PET_SKILL_USE_TYPE_PASSIVE == pet_skill_use_type:
					self.AffectShower.SetPetSkillAffect(i + 1, skillData[0])
			return
		# <<< GROWTH PET SKILL REWORK (U7) END
		
		# Skill data
		(skill_count, pet_skill1, pet_skill_level1, pet_skill_cool1, pet_skill2, pet_skill_level2, pet_skill_cool2, pet_skill3, pet_skill_level3, pet_skill_cool3) = player.GetPetSkill(pet_id)
		
		if pet_skill1:
		
			(pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time) = skill.GetPetSkillInfo(pet_skill1)
			
			if skill.PET_SKILL_USE_TYPE_AUTO == pet_skill_use_type:
				if curTime <= pet_skill_cool1:
					pass
				else:
					self.AffectShower.SetPetSkillAffect(1, pet_skill1)
				
			elif skill.PET_SKILL_USE_TYPE_PASSIVE == pet_skill_use_type:
				self.AffectShower.SetPetSkillAffect(1, pet_skill1)
					
		if pet_skill2:
			(pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time) = skill.GetPetSkillInfo(pet_skill2)
			
			if skill.PET_SKILL_USE_TYPE_AUTO == pet_skill_use_type:
				if curTime <= pet_skill_cool2:
					pass
				else:
					self.AffectShower.SetPetSkillAffect(2, pet_skill2)
				
			elif skill.PET_SKILL_USE_TYPE_PASSIVE == pet_skill_use_type:	
				self.AffectShower.SetPetSkillAffect(2, pet_skill2)
				
		if pet_skill3:
		
			(pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time) = skill.GetPetSkillInfo(pet_skill3)
			
			if skill.PET_SKILL_USE_TYPE_AUTO == pet_skill_use_type:
				if curTime <= pet_skill_cool3:
					pass
				else:
					self.AffectShower.SetPetSkillAffect(3, pet_skill3)
				
			elif skill.PET_SKILL_USE_TYPE_PASSIVE == pet_skill_use_type:
				self.AffectShower.SetPetSkillAffect(3, pet_skill3)
				
				
	
	def PetEvolFlashEventCheck(self, pet_level, evol_level, birthday, curEXP, nextEXP, itemEXP, itemMaxEXP):
		# Return if pet has reached peak evolution
		if evol_level == player.PET_GROWTH_SKILL_OPEN_EVOL_LEVEL:
			self.DisableFlashButtonEvent(player.FEED_EVOL_EVENT)
			return False
			
		# Return if there is no level conditions for evolution
		evol_require = self.GetEvolInfo(evol_level)
		if 0 == evol_require:
			self.DisableFlashButtonEvent(player.FEED_EVOL_EVENT)
			return False
		
		# Check level and experience limit for the first two evolutions
		if evol_level < player.PET_GROWTH_SKILL_OPEN_EVOL_LEVEL-1:
			# Level Check
			if pet_level == evol_require:
				if curEXP == nextEXP and itemEXP == itemMaxEXP:
					self.EnableFlashButtonEvent(player.FEED_EVOL_EVENT)
					
					return True
					
		# Check level and age limit for the last evolution
		elif evol_level == player.PET_GROWTH_SKILL_OPEN_EVOL_LEVEL - 1:
			# Level Check
			if pet_level >= evol_require:

				curTime = app.GetGlobalTimeStamp()
				birthSec = max(0, curTime - birthday)
				
				if birthSec > player.SPECIAL_EVOL_MIN_AGE:
					self.EnableFlashButtonEvent(player.FEED_EVOL_EVENT)
					
					return True
				
		self.DisableFlashButtonEvent(player.FEED_EVOL_EVENT)
		return False
				
	def PetLifeTimeFlashEventCheck(self, lifeTime):
		if lifeTime < player.LIFE_TIME_FLASH_MIN_TIME:
			self.EnableFlashButtonEvent(player.FEED_LIFE_TIME_EVENT)
			
			return True
			
		self.DisableFlashButtonEvent(player.FEED_LIFE_TIME_EVENT)
		return False

	def PetItemExpFlashEventCheck(self, curEXP, nextEXP, itemEXP, itemMaxEXP):
		if (curEXP >= nextEXP) and (itemEXP < itemMaxEXP):
			self.EnableFlashButtonEvent(player.FEED_EXP_EVENT)
			return True

		self.DisableFlashButtonEvent(player.FEED_EXP_EVENT)
		return False
		
	def AllOffPetInfoFlashEvent(self):
		if self.wndPetMiniInfo:
			self.wndPetMiniInfo.OffFlashEvent()
	
		for i in xrange(player.FEED_BUTTON_MAX):
			self.DisableFlashButtonEvent(i)
			
	def EnableFlashButtonEvent(self, index):
		if index < 0 or index >= player.FEED_BUTTON_MAX:
			return
		
		if self.feedButton[index]:
			self.feedButton[index].EnableFlash()
			
	def DisableFlashButtonEvent(self, index):
		if index < 0 or index >= player.FEED_BUTTON_MAX:
			return
		
		if self.feedButton[index]:
			self.feedButton[index].DisableFlash()
	
	def SetExperience(self, curPoint, maxPoint, itemExp, itemExpMax):
		
		curPoint = min(curPoint, maxPoint)
		curPoint = max(curPoint, 0)
		maxPoint = max(maxPoint, 0)
		
		itemExp = min(itemExp, itemExpMax)
		itemExp = max(itemExp, 0)
		itemExpMax = max(itemExpMax, 0)
		
		# Battle exp is divided into BATTLE_EXP_GAUGE_MAX parts
		quarterPoint = maxPoint / BATTLE_EXP_GAUGE_MAX
		FullCount = 0

		if 0 != quarterPoint:
			FullCount = min(BATTLE_EXP_GAUGE_MAX, curPoint / quarterPoint)

		for i in xrange(TOTAL_EXP_GAUGE_COUNT):
			self.expGauge[i].Hide()

		for i in xrange(FullCount):
			self.expGauge[i].SetRenderingRect(0.0, 0.0, 0.0, 0.0)
			self.expGauge[i].Show()

		if 0 != quarterPoint:
			if FullCount < BATTLE_EXP_GAUGE_MAX:
				Percentage = float(curPoint % quarterPoint) / quarterPoint - 1.0
				self.expGauge[FullCount].SetRenderingRect(0.0, Percentage, 0.0, 0.0)
				self.expGauge[FullCount].Show()

		if 0 != itemExpMax:			
			itemExpGauge = self.expGauge[ITEM_EXP_GAUGE_POS]
			Percentage = float(itemExp) / float(itemExpMax) - float(1.0)
			itemExpGauge.SetRenderingRect(0.0, Percentage, 0.0, 0.0)
			itemExpGauge.Show()
		
		output_cur_exp = curPoint + itemExp
		output_max_exp = maxPoint + itemExpMax
		
		expPercent = 0
		if output_max_exp:
			expPercent = float(output_cur_exp) / float(output_max_exp) * 100

		if app.USE_CTEXTLINE_AUTO_WRAP:
			if localeinfo.IsARABIC():
				tooltip_text = "{} : {}\n{} : {}\n{} : {}\n{} : {}".format(curPoint, localeinfo.PET_INFO_EXP,\
																			maxPoint - curPoint, localeinfo.PET_INFO_NEXT_EXP,\
																			itemExp, localeinfo.PET_INFO_ITEM_EXP,\
																			itemExpMax - itemExp, localeinfo.PET_INFO_NEXT_ITEM_EXP)
			else:
				tooltip_text = "{} : {}\n{} : {}\n{} : {}\n{} : {}".format(localeinfo.PET_INFO_EXP, curPoint,\
																			localeinfo.PET_INFO_NEXT_EXP, maxPoint - curPoint,\
																			localeinfo.PET_INFO_ITEM_EXP, itemExp,\
																			localeinfo.PET_INFO_NEXT_ITEM_EXP, itemExpMax - itemExp)
			self.tooltipEXP.SetText(tooltip_text)
		else:
			self.tooltipEXP.SetText("%s : %.2f%%" % (localeinfo.TASKBAR_EXP, expPercent))


	def SetLifeTime(self, curPoint, maxPoint):
		curPoint = min(curPoint, maxPoint)
		if maxPoint > 0:
			self.lifeTimeGauge.SetPercentageWithScale(curPoint, maxPoint)

	def SetItemToolTip(self, tooltipItem):
		if tooltipItem:
			self.tooltipItem = proxy(tooltipItem)

	def SetInven(self, inven):
		if inven:
			self.inven = proxy(inven)

	def IsFeedWindowOpen(self):
		if self.wndPetFeed:
			if self.wndPetFeed.IsShow():
				return True

		return False

	def GetPetHatchingWindow(self):
		return self.wndPetHatching

	def GetPetNameChangeWindow(self):
		return self.wndPetNameChange

	def GetPetFeedWindow(self):
		return self.wndPetFeed

	def CantFeedItem(self, InvenSlot):
		if self.feedIndex == player.FEED_LIFE_TIME_EVENT:
			return self.__CantLifeTimeFeedItem(InvenSlot)
			
		elif self.feedIndex == player.FEED_EVOL_EVENT:
			return self.__CantEvolFeedItem(InvenSlot)
			
		elif self.feedIndex == player.FEED_EXP_EVENT:
			return self.__CantExpFeedItem(InvenSlot)
		
		return False
		
		
	def __CantLifeTimeFeedItem(self, InvenSlot):
		ItemVNum = player.GetItemIndex(InvenSlot)
		
		if ItemVNum == 0:
			return True

		if item.IsAntiFlag(item.ITEM_ANTIFLAG_PETFEED):
			return True
			
		item.SelectItem(ItemVNum)
		if item.GetItemType() == item.ITEM_TYPE_PET:
			if item.GetItemSubType() in [item.PET_UPBRINGING, item.PET_EGG]:
				return False
		
		return True
		
	def __CantEvolFeedItem(self, InvenSlot):
		ItemVNum = player.GetItemIndex(InvenSlot)
	
		if ItemVNum == 0:
			return True
			
		item.SelectItem(ItemVNum)
		
		if item.IsAntiFlag(item.ITEM_ANTIFLAG_PETFEED):
			return True
		
	def __CantExpFeedItem(self, InvenSlot):
		ItemVNum = player.GetItemIndex(InvenSlot)
		
		if ItemVNum == 0:
			return True
			
		item.SelectItem(ItemVNum)

		if item.IsAntiFlag(item.ITEM_ANTIFLAG_PETFEED):
			return True
		
		if item.GetItemType() in [item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR, item.ITEM_TYPE_BELT, item.ITEM_TYPE_PET]:
			if item.ITEM_TYPE_PET == item.GetItemType():
				if item.GetItemSubType() in [item.PET_EXPFOOD, item.PET_EXPFOOD_PER]:
					return False
				else:
					return True
			else:
				return False
		
		return True
		
	def CantAttrChangeItem(self, InvenSlot):
		ItemVNum = player.GetItemIndex(InvenSlot)
		
		if ItemVNum == 0:
			return True
			
		item.SelectItem(ItemVNum)
		
		if item.GetItemType() == item.ITEM_TYPE_PET:
			if item.GetItemSubType() in [item.PET_UPBRINGING, item.PET_ATTR_CHANGE]:
				return False
			
		return True
		
	def CantPremiumFeedItem(self, InvenSlot):
		ItemVNum = player.GetItemIndex(InvenSlot)
		
		if ItemVNum == 0:
			return True
			
		item.SelectItem(ItemVNum)
		
		if item.GetItemType() == item.ITEM_TYPE_PET:
			if item.GetItemSubType() in [item.PET_UPBRINGING, item.PET_PRIMIUM_FEEDSTUFF]:
				return False
			
		return True
		
	def PetInfoBindAffectShower(self, affect_shower):
		self.AffectShower = affect_shower
		
	def SetPetSkillToolTip(self, tooltipPetSkill):
		self.tooptipPetSkill = tooltipPetSkill
		
	def GetEvolInfo(self, evol_level):
		# Return if evolution level in invalid
		if evol_level < 1 or evol_level >= player.PET_GROWTH_EVOL_MAX:
			return 0

		if 1 == evol_level:
			return 40
		elif 2 == evol_level:
			return 80
		elif 3 == evol_level:
			return 81
			
		return 0

	def PetFeedReuslt(self, result):
		if not self.wndPetFeed:
			if app.USE_GROWTH_NEW_EVOLVE_WINDOW:
				if not self.evolveWnd:
					return
			else:
				return

		if True == result:
			self.wndPetFeed.BackUpSucceedFeedItems()

			if self.feedIndex == player.FEED_EVOL_EVENT:
				if app.USE_GROWTH_NEW_EVOLVE_WINDOW:
					if self.evolveWnd:
						self.evolveWnd.Close()
				else:
					self.wndPetFeed.Close()

		if app.USE_GROWTH_NEW_EVOLVE_WINDOW:
			if self.feedIndex != player.FEED_EVOL_EVENT:
				if self.wndPetFeed:
					self.wndPetFeed.ClearFeedItems()
		else:
			if self.wndPetFeed:
				self.wndPetFeed.ClearFeedItems()

	def OverInAttrChangeItem(self, slotIndex):
		if None != self.tooltipItem:
			invenPos = self.attrChangeIndex[slotIndex]
			if invenPos != -1:
				self.tooltipItem.SetInventoryItem(invenPos, player.INVENTORY)

		return

	def OverOutAttrChangeItem(self):
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()
		return
		
	def SelectAttrChangeItemSlot(self, slotIndex):
		self.__ClearAttrChangeWindow()
		
	def __ClearAttrChangeSlot(self, slotIndex):
		if mousemodule.mouseController.isAttached():
			return

		#Unlock item in slotIndex slot
		self.CanInvenSlot(self.attrChangeIndex[slotIndex])
		self.attrChangeIndex[slotIndex] = -1
		self.attrChangeSlot.ClearSlot(slotIndex)
		self.attrChangeSlot.RefreshSlot()
		
		if self.attrChangeButton.IsShow():
			self.attrChangeButton.Hide()
		
	def SelectEmptyAttrChangeSlot(self, slotIndex):
		if not mousemodule.mouseController.isAttached():
			return False
		
		attachedSlotType	= mousemodule.mouseController.GetAttachedType()			
		attachedSlotPos		= mousemodule.mouseController.GetAttachedSlotNumber()
		attachedItemVNum	= player.GetItemIndex(attachedSlotPos)
		item.SelectItem(attachedItemVNum)		
		
		itemType	= item.GetItemType()
		itemSubType = item.GetItemSubType()			

		# Return if item is beging attached from not inventory window
		if player.SLOT_TYPE_INVENTORY != attachedSlotType:
			return False
			
		# Return if item position is bigger than player.ITEM_SLOT_COUNT
		if attachedSlotPos >= player.ITEM_SLOT_COUNT: 
			return False

		if slotIndex == player.PET_WND_SLOT_ATTR_CHANGE:
		
			# Return if upbringing item is already in place
			if -1 != self.attrChangeIndex[player.PET_WND_SLOT_ATTR_CHANGE]:
				return False
			

			if item.ITEM_TYPE_PET != itemType or itemSubType != item.PET_UPBRINGING:
				return False
				
			# Return if there is an active pet
			activePetId = player.GetActivePetItemId()
			if activePetId != 0:
				return False
					
			# Select attr change item if it wasn't selected yet
			if -1 == self.attrChangeIndex[player.PET_WND_SLOT_ATTR_CHANGE_ITEM]:

				attrChangePos = player.GetItemSlotIndex(player.PET_ATTR_CHANGE_ITEM)
				if attrChangePos != -1:
					self.attrChangeIndex[player.PET_WND_SLOT_ATTR_CHANGE_ITEM] = attrChangePos
					self.attrChangeSlot.SetItemSlot(player.PET_WND_SLOT_ATTR_CHANGE_ITEM, player.PET_ATTR_CHANGE_ITEM)
					#self.attrChangeButton.Show()
				
		elif slotIndex == player.PET_WND_SLOT_ATTR_CHANGE_ITEM:
		
			# Return if attr change item is already in place
			if -1 != self.attrChangeIndex[player.PET_WND_SLOT_ATTR_CHANGE_ITEM]:
				return False
				
			if item.ITEM_TYPE_PET != itemType or itemSubType != item.PET_ATTR_CHANGE:
				return False
				
		elif slotIndex == player.PET_WND_SLOT_ATTR_CHANGE_RESULT:
			return False
			
		self.attrChangeIndex[slotIndex] = attachedSlotPos
		self.attrChangeSlot.SetItemSlot(slotIndex, attachedItemVNum)
		self.attrChangeSlot.RefreshSlot()
		
		if self.attrChangeIndex[player.PET_WND_SLOT_ATTR_CHANGE_ITEM] != -1 and self.attrChangeIndex[player.PET_WND_SLOT_ATTR_CHANGE] != -1:
			self.attrChangeButton.Show()
		
		mousemodule.mouseController.DeattachObject()
		return True
		
	def ClickAttrChangeButton(self):
		if self.questionDialog.IsShow():
			return
			
		self.questionDialog.SetText(localeinfo.PET_ATTR_CHANGE_DIALOG_TEXT)
		self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__PetAttrChangeAccept))
		self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__PetAttrChangeCancel))
		self.questionDialog.Open()
		
	def ClickAttrClearButton(self):
		self.__ClearAttrChangeWindow()
			
	def __ClearAttrChangeWindow(self):
		if self.questionDialog.IsShow():
			self.questionDialog.Close()
		
		self.attrChangeText.SetText("")
		for i in xrange(player.PET_WND_SLOT_ATTR_CHANGE_MAX):
			self.__ClearAttrChangeSlot(i)
	
	def __PetAttrChangeAccept(self):
		upBringingPos = self.attrChangeIndex[player.PET_WND_SLOT_ATTR_CHANGE]
		attrChangePos = self.attrChangeIndex[player.PET_WND_SLOT_ATTR_CHANGE_ITEM]
		
		# Send packet if positions are valid and close the question dialog
		if upBringingPos != -1 and attrChangePos != -1:
			net.SendPetAttrChange(upBringingPos, attrChangePos)
			
		self.questionDialog.Close()
		
	def __PetAttrChangeCancel(self):
		self.questionDialog.Close()
		
		
	def PetAttrChangeResult(self, slotIndex, byType):
		self.attrChangeButton.Hide()

		text = self.typeInfo[byType]
		self.attrChangeText.SetText(text)

		# Clear slots 
		for i in xrange(player.PET_WND_SLOT_ATTR_CHANGE_MAX):
			self.__ClearAttrChangeSlot(i)
			
		# Append new upbringing pet item in result slot
		itemVnum = player.GetItemIndex(slotIndex)
		self.attrChangeIndex[player.PET_WND_SLOT_ATTR_CHANGE_RESULT] = slotIndex
		self.attrChangeSlot.SetItemSlot(player.PET_WND_SLOT_ATTR_CHANGE_RESULT, itemVnum)
		self.attrChangeSlot.RefreshSlot()
		
	def ItemMoveAttrChangeWindow(self, slotWindow, slotIndex):
		if player.INVENTORY == slotWindow:
			attachSlotType = player.SLOT_TYPE_INVENTORY
		else:
			return False
	
		mousemodule.mouseController.DeattachObject()
		
		selectedItemVNum = player.GetItemIndex(slotWindow, slotIndex)
		count			 = player.GetItemCount(slotWindow, slotIndex)
		
		mousemodule.mouseController.AttachObject(self, attachSlotType, slotIndex, selectedItemVNum, count)
		
		item.SelectItem(selectedItemVNum)
		
		if item.GetItemType() == item.ITEM_TYPE_PET:
			if item.GetItemSubType() == item.PET_UPBRINGING:
				slotPos = player.PET_WND_SLOT_ATTR_CHANGE
				
			elif item.GetItemSubType() == item.PET_ATTR_CHANGE:
				slotPos = player.PET_WND_SLOT_ATTR_CHANGE_ITEM
				
			else:
				return False
		
			self.SelectEmptyAttrChangeSlot(slotPos)
		
			mousemodule.mouseController.DeattachObject()
			return True
		
		return False
		
	def ClickDetermineButton(self):
		# If there is an active pet and player has player.PET_ATTR_DETERMINE_ITEM 
		# item, send the packet
		activePetId = player.GetActivePetItemId()
		if activePetId != 0:
					
			sourcePos = player.GetItemSlotIndex(player.PET_ATTR_DETERMINE_ITEM)
			if sourcePos != -1:
				net.SendPetAttrDetermine(sourcePos)
		
	def PetAttrDetermineResult(self, byType):
		# Display determine result in a popup dialog
		text = self.typeInfo[byType]
		self.__OpenPopupDialog(text)
		
	def __DescPetPremiumFeedstuff(self):
		# Initialize pet premium feedstuff description
		event.ClearEventSet(self.descIndex)

		self.descIndex = event.RegisterEventSet(uiscriptlocale.PET_PRIMIUM_FEEDSTUFF_DESC)
		event.SetVisibleLineCount(self.descIndex, VISIBLE_LINE_COUNT)

		if localeinfo.IsARABIC():
			event.SetEventSetWidth(self.descIndex, 300)
			
		event.SetVisibleLineCount(self.descIndex, VISIBLE_LINE_COUNT)
		event.SetRestrictedCount(self.descIndex, 70)

	def PetPremiumFeedStuffPrevDescriptionPage(self):
		line_height	= event.GetLineHeight(self.descIndex) + 4
		if localeinfo.IsARABIC():
			line_height -= 4
			
		cur_start_line	= event.GetVisibleStartLine(self.descIndex)
		
		decrease_count = VISIBLE_LINE_COUNT
		
		if cur_start_line - decrease_count < 0:
			return;

		event.SetVisibleStartLine(self.descIndex, cur_start_line - decrease_count)
		self.desc_Y += (line_height * decrease_count)

	def PetPremiumFeedStuffNextDescriptionPage(self):
		line_height	= event.GetLineHeight(self.descIndex) + 4
		if localeinfo.IsARABIC():
			line_height -= 4
			
		total_line_count = event.GetProcessedLineCount(self.descIndex)
		cur_start_line = event.GetVisibleStartLine(self.descIndex)
		
		increase_count = VISIBLE_LINE_COUNT
		
		if cur_start_line + increase_count >= total_line_count:
			increase_count = total_line_count - cur_start_line

		if increase_count < 0 or cur_start_line + increase_count >= total_line_count:
			return
		
		event.SetVisibleStartLine(self.descIndex, cur_start_line + increase_count)
		self.desc_Y -= (line_height * increase_count)
		
		
	def OverInPetReviveResultSlot(self):
		if None != self.tooltipItem:
			invenPos = self.petReviveIndex
			if invenPos != -1:
				if self.isPetReviveResultTooltip:	# Real pet tooltip after being revived
					self.tooltipItem.SetInventoryItem(invenPos, player.INVENTORY)
				else:	# To be revived pet dummy tooltip
					metinSlot = [player.GetItemMetinSocket(invenPos, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
					pet_id = metinSlot[2]

					if pet_id:
						self.tooltipItem.ClearToolTip()
						
						itemVnum = player.GetItemIndex(invenPos)
						item.SelectItem(itemVnum)
						
						(skill_count, pet_skill1, pet_skill_level1, pet_skill_cool1, pet_skill2, pet_skill_level2, pet_skill_cool2, pet_skill3, pet_skill_level3, pet_skill_cool3) = player.GetPetSkill(pet_id)

						(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
						
						# Item Title
						self.tooltipItem.AppendTextLine(pet_nick, self.tooltipItem.TITLE_COLOR)
						
						# Item Description
						itemDesc = item.GetItemDescription()
						self.tooltipItem.AppendDescription(itemDesc, 26)
						
						# Pet Level/Age
						self.tooltipItem.AppendSpace(5)
						birthSec = max(0, metinSlot[0] - birthday)
						self.tooltipItem.AppendTextLine(localeinfo.PET_TOOLTIP_LEVEL + " " + str(pet_level) + " (" + localeinfo.SecondToDay(birthSec * 0.8) + ")")

						# Pet Evolution / Skill Count
						self.tooltipItem.AppendSpace(5)
						if skill_count:
							self.tooltipItem.AppendTextLine(self.tooltipItem.GetEvolName(evol_level) + "(" + str(skill_count) + ")")
						else:
							self.tooltipItem.AppendTextLine(self.tooltipItem.GetEvolName(evol_level))

						# Pet HP/SP/DEF
						self.tooltipItem.AppendSpace(5)
						self.tooltipItem.AppendTextLine(localeinfo.PET_TOOLTIP_HP + " +" + str("%0.1f" % pet_hp) + "%", self.tooltipItem.SPECIAL_POSITIVE_COLOR)
						self.tooltipItem.AppendTextLine(localeinfo.PET_TOOLTIP_DEF + " +" + str("%0.1f" % pet_def) + "%", self.tooltipItem.SPECIAL_POSITIVE_COLOR)
						self.tooltipItem.AppendTextLine(localeinfo.PET_TOOLTIP_SP + " +" + str("%0.1f" % pet_sp) + "%", self.tooltipItem.SPECIAL_POSITIVE_COLOR)				

						# Pet Skills
						if pet_skill1:
							self.tooltipItem.AppendSpace(5)
							(pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time) = skill.GetPetSkillInfo(pet_skill1)
							self.tooltipItem.AppendTextLine(localeinfo.PET_TOOLTUP_SKILL % (pet_skill_name, pet_skill_level1) , self.tooltipItem.SPECIAL_POSITIVE_COLOR)
						if pet_skill2:
							self.tooltipItem.AppendSpace(5)
							(pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time) = skill.GetPetSkillInfo(pet_skill2)
							self.tooltipItem.AppendTextLine(localeinfo.PET_TOOLTUP_SKILL % (pet_skill_name, pet_skill_level2) , self.tooltipItem.SPECIAL_POSITIVE_COLOR)
						if pet_skill3:
							self.tooltipItem.AppendSpace(5)
							(pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time) = skill.GetPetSkillInfo(pet_skill3)
							self.tooltipItem.AppendTextLine(localeinfo.PET_TOOLTUP_SKILL % (pet_skill_name, pet_skill_level3) , self.tooltipItem.SPECIAL_POSITIVE_COLOR)

						# Pet Lifetime
						for i in xrange(item.LIMIT_MAX_NUM):
							(limitType, limitValue) = item.GetLimit(i)
							if item.LIMIT_REAL_TIME == limitType:
								(endTime, maxTime) = player.GetPetLifeTime(pet_id)
								self.tooltipItem.AppendPetItemLastTime(app.GetGlobalTimeStamp() + maxTime)
								
						self.tooltipItem.Show()
				
		return
		
	def OverOutPetReviveResultSlot(self):
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()
		return
		
	def OverInPetReviveSlot(self):
		if None != self.tooltipItem:
			invenPos = self.petReviveIndex
			if invenPos != -1:
				self.tooltipItem.SetInventoryItem(invenPos, player.INVENTORY)
				
		return
		
	def OverOutPetReviveSlot(self):
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()
		return
		
	def __ClearPetReviveWindow(self):
		self.CanInvenSlot(self.petReviveIndex)
			
		self.isPetReviveResultTooltip = False
		self.petReviveIndex = -1
		
		self.petReviveSlot.SetItemSlot(0, 0)
		self.petReviveSlot.RefreshSlot()
		
		self.petReviveResultSlot.SetItemSlot(0, 0)
		self.petReviveResultSlot.RefreshSlot()

		for i in xrange(player.PET_REVIVE_MATERIAL_SLOT_MAX):
			self.petReviveMaterialSlot.SetItemSlot(i, 0)
			self.petReviveMaterialSlot.RefreshSlot()
			
			if self.petReviveItems[i]:
				self.CanInvenSlot(self.petReviveItems[i])
			self.petReviveItems[i] = -1
			self.petReviveItemsCount[i] = 0
			
		self.petReviveAgeText.SetText("")
		self.petReviveResultAgeText.SetText("")
		self.petReviveItemsCountText.SetText(localeinfo.PET_REVIVE_UI_MATERIAL_COUNT % (0, 0))
		
	def SelectPetReviveEmptySlot(self, slotIndex):
		if not mousemodule.mouseController.isAttached():
			return False
		
		attachedSlotType	= mousemodule.mouseController.GetAttachedType()			
		attachedSlotPos		= mousemodule.mouseController.GetAttachedSlotNumber()
		attachedItemVNum	= player.GetItemIndex(attachedSlotPos)
		item.SelectItem(attachedItemVNum)		
		
		itemType	= item.GetItemType()
		itemSubType = item.GetItemSubType()			

		# Return if item is beging attached from not inventory window
		if player.SLOT_TYPE_INVENTORY != attachedSlotType and\
			(player.SLOT_TYPE_SKILL_BOOK_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_STONE_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_GIFT_BOX_INVENTORY != attachedSlotType and app.ENABLE_SPECIAL_INVENTORY_SYSTEM and\
			player.SLOT_TYPE_ENCHANT_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_POTS_INVENTORY != attachedSlotType):

			return False
			
		# Return if item position is bigger than player.ITEM_SLOT_COUNT
		if attachedSlotPos >= player.ITEM_SLOT_COUNT: 
			return False
			
		curTime = app.GetGlobalTimeStamp()
		metinSlot = [player.GetItemMetinSocket(attachedSlotPos, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
		
		# Return if there is an active pet or target pet is still alive
		if item.ITEM_TYPE_PET == itemType and itemSubType == item.PET_UPBRINGING:
			activePetId = player.GetActivePetItemId()
			if activePetId != 0:
				return False
				
			if metinSlot[0] > curTime:
				return False
		else:
			return False

		# Return if there is already pet in place
		if self.petReviveIndex != -1:
			return False

		# Return if no pet_id in the socket
		pet_id = metinSlot[2]
		if 0 == pet_id:
			return False
			
		(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
		birthSec = max(0, metinSlot[0] - birthday)
		
		# Upbringing Slot
		self.petReviveIndex = attachedSlotPos
		self.petReviveSlot.SetItemSlot(slotIndex, attachedItemVNum)
		self.petReviveSlot.RefreshSlot()
		
		# Revived Upbringing Slot
		self.petReviveResultSlot.SetItemSlot(slotIndex, attachedItemVNum)
		self.petReviveResultSlot.RefreshSlot()
		
		# Age Texts
		self.petReviveAgeText.SetText("%s" % localeinfo.SecondToDay(birthSec))
		self.petReviveResultAgeText.SetText("%s" % localeinfo.SecondToDay(birthSec * 0.8))
		self.__RefreshPetReviveMaterialCount()		
		
		mousemodule.mouseController.DeattachObject()
		return True
		
	def SelectPetReviveItemSlot(self):
		self.__ClearPetReviveWindow()
		
	def SelectPetReviveMaterialEmptySlot(self, slotIndex):
		if not mousemodule.mouseController.isAttached():
			return False
		
		attachedSlotType	= mousemodule.mouseController.GetAttachedType()			
		attachedSlotPos		= mousemodule.mouseController.GetAttachedSlotNumber()
		attachedItemCount	= mousemodule.mouseController.GetAttachedItemCount()
		attachedItemVNum	= player.GetItemIndex(attachedSlotPos)
		item.SelectItem(attachedItemVNum)		
		
		itemType	= item.GetItemType()
		itemSubType = item.GetItemSubType()	
		
		# Return if item is beging attached from not inventory window
		if player.SLOT_TYPE_INVENTORY != attachedSlotType and\
			(player.SLOT_TYPE_SKILL_BOOK_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_STONE_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_GIFT_BOX_INVENTORY != attachedSlotType and app.ENABLE_SPECIAL_INVENTORY_SYSTEM and\
			player.SLOT_TYPE_ENCHANT_INVENTORY != attachedSlotType and\
			player.SLOT_TYPE_POTS_INVENTORY != attachedSlotType):
			return False
			
		# Return if item position is bigger than player.ITEM_SLOT_COUNT
		if attachedSlotPos >= player.ITEM_SLOT_COUNT: 
			return False
		
		# Return if there is no to-be-revived pet in slot
		if self.petReviveIndex == -1:
			return False
			
		# Return if material is not item.PET_PRIMIUM_FEEDSTUFF
		if itemType != item.ITEM_TYPE_PET and itemSubType != item.PET_PRIMIUM_FEEDSTUFF:
			return False
			
		# Return if the slot is already occupied or item is in another slot
		if self.petReviveItems[slotIndex] != -1:
			return False
			
		if attachedSlotPos in self.petReviveItems:
			return False
			
		# Return if enough material has been appended
		if self.HasEnoughPetReviveMaterial():
			return False
	
		self.petReviveItems[slotIndex] = attachedSlotPos
		self.petReviveItemsCount[slotIndex] = attachedItemCount
		self.petReviveMaterialSlot.SetItemSlot(slotIndex, attachedItemVNum, attachedItemCount)
		self.petReviveMaterialSlot.RefreshSlot()
		
		# Refresh required material text
		self.__RefreshPetReviveMaterialCount()
		
		mousemodule.mouseController.DeattachObject()
		return True
		
	def SelectPetReviveMaterialItemSlot(self, slotIndex):
		if mousemodule.mouseController.isAttached():
			return

		self.CanInvenSlot(self.petReviveItems[slotIndex])
		self.petReviveItems[slotIndex] = -1
		self.petReviveItemsCount[slotIndex] = 0
		self.petReviveMaterialSlot.ClearSlot(slotIndex)
		self.petReviveMaterialSlot.RefreshSlot()
		
		self.__RefreshPetReviveMaterialCount()
		
	def __RefreshPetReviveMaterialCount(self):
		if -1 == self.petReviveIndex:
			self.petReviveItemsCountText.SetText(localeinfo.PET_REVIVE_UI_MATERIAL_COUNT % (0, 0))
			return
			
		metinSlot = [player.GetItemMetinSocket(self.petReviveIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
		pet_id = metinSlot[2]

		# Pet data
		(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
		birthSec = max(0, metinSlot[0] - birthday)
		
		# Material Count
		petMaxReviveMaterialCount = localeinfo.SecondToDayNumber(birthSec) / 10
		if petMaxReviveMaterialCount < 1:
			petMaxReviveMaterialCount = 1
			
		petReviveMaterialCount = 0
		for i in xrange(player.PET_REVIVE_MATERIAL_SLOT_MAX):
			if self.petReviveItems[i] != -1:
				petReviveMaterialCount += self.petReviveItemsCount[i]
			
		# Set added mateiral count to required material count if higher
		if petReviveMaterialCount > petMaxReviveMaterialCount:
			petReviveMaterialCount = petMaxReviveMaterialCount
			
		self.petReviveItemsCountText.SetText(localeinfo.PET_REVIVE_UI_MATERIAL_COUNT % (petReviveMaterialCount, petMaxReviveMaterialCount))
		
	def HasEnoughPetReviveMaterial(self):
		if -1 == self.petReviveIndex:
			return False
			
		metinSlot = [player.GetItemMetinSocket(self.petReviveIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
		pet_id = metinSlot[2]

		(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
		birthSec = max(0, metinSlot[0] - birthday)
		
		# Material Count
		petMaxReviveMaterialCount = localeinfo.SecondToDayNumber(birthSec) / 10
		if petMaxReviveMaterialCount < 1:
			petMaxReviveMaterialCount = 1
			
		itemCount = 0
		for i in xrange(player.PET_REVIVE_MATERIAL_SLOT_MAX):
			if self.petReviveItems[i] != -1:
				itemCount += self.petReviveItemsCount[i]
			
			if itemCount >= petMaxReviveMaterialCount:
				return True
				
		return False
		
	def ClickPetReviveButton(self):
		# Return if there is no pet upbringing item in slot
		if self.petReviveIndex == -1:
			self.__OpenPopupDialog(localeinfo.PET_REVIVE_FAIL_EMPTY_PET_SLOT)
			return
			
		# Return if question dialog is already opened
		if self.questionDialog.IsShow():
			return
			
		# Return if there is not enough material
		if not self.HasEnoughPetReviveMaterial():
			self.__OpenPopupDialog(localeinfo.PET_REVIVE_FAIL_NOT_ENOUGHT_MATERIAL)
			return
			
		metinSlot = [player.GetItemMetinSocket(self.petReviveIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
		pet_id = metinSlot[2]

		(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
		birthSec = max(0, metinSlot[0] - birthday)
		
		petMaxReviveMaterialCount = localeinfo.SecondToDayNumber(birthSec) / 10
		if petMaxReviveMaterialCount < 1:
			petMaxReviveMaterialCount = 1
			
		self.questionDialog.SetText(localeinfo.REVIVE_QUESTION % (pet_nick, petMaxReviveMaterialCount)) 
		self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__PetReviveAccept))
		self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__PetReviveCancel))
		self.questionDialog.Open()
			
	def __PetReviveAccept(self):
		resultReviveItems = [value for value in self.petReviveItems if value != -1]
		resultReviveItemsCount = [value for value in self.petReviveItemsCount if value != 0]
		
		# Send revive packet if there are items in list and close the question dialog
		if resultReviveItems:
			net.SendPetRevive(self.petReviveIndex, resultReviveItems, resultReviveItemsCount)
			
		self.questionDialog.Close()
		
	def __PetReviveCancel(self):
		self.questionDialog.Close()
		
	def ClickPetReviveCancelButton(self):
		self.__ClearPetReviveWindow()
		
	def PetReviveResult(self, result):
		# If succeeded set revived pet to result item slot,
		# else clear the revive window.
		if result:
			self.isPetReviveResultTooltip = True
			self.petReviveSlot.SetItemSlot(0, 0)
			self.petReviveSlot.RefreshSlot()

			for i in xrange(player.PET_REVIVE_MATERIAL_SLOT_MAX):
				self.petReviveMaterialSlot.SetItemSlot(i, 0)
				self.petReviveMaterialSlot.RefreshSlot()
				
				if self.petReviveItems[i]:
					self.CanInvenSlot(self.petReviveItems[i])
				self.petReviveItems[i] = -1
				self.petReviveItemsCount[i] = 0

			self.petReviveAgeText.SetText("")
			self.petReviveItemsCountText.SetText(localeinfo.PET_REVIVE_UI_MATERIAL_COUNT % (0, 0))
		else:
			self.__ClearPetReviveWindow()
			
			
	def ItemMovePremiumFeedWindow(self, slotWindow, slotIndex):
		if player.INVENTORY == slotWindow:
			attachSlotType = player.SLOT_TYPE_INVENTORY
		else:
			return False
	
		mousemodule.mouseController.DeattachObject()
		
		selectedItemVNum = player.GetItemIndex(slotWindow, slotIndex)
		count			 = player.GetItemCount(slotWindow, slotIndex)
		
		mousemodule.mouseController.AttachObject(self, attachSlotType, slotIndex, selectedItemVNum, count)
		
		item.SelectItem(selectedItemVNum)
		
		if item.GetItemType() == item.ITEM_TYPE_PET:
			if item.GetItemSubType() == item.PET_UPBRINGING:
				return self.SelectPetReviveEmptySlot(0)
				
			elif item.GetItemSubType() == item.PET_PRIMIUM_FEEDSTUFF:
				# Return the first available slot
				for i in xrange(player.PET_REVIVE_MATERIAL_SLOT_MAX):
					if self.petReviveItems[i] == -1:
						return self.SelectPetReviveMaterialEmptySlot(i)
		
		return False

	def AttachItemToPetWindow(self, windowType, slotIndex):
		# >>> GROWTH PET U9: the feed window opens STANDALONE now (Companion Feed
		# button; the main window is retired and never shown), so right-click item
		# staging must also pass when only the feed window is up. The state machine
		# rests at PET_WINDOW_INFO and feedIndex is set by ClickPetFeedButton, so
		# the inner branch logic is unchanged.
		if self.IsShow() or (self.wndPetFeed and self.wndPetFeed.IsShow()):
			if self.GetState() == player.PET_WINDOW_INFO and self.feedIndex != player.FEED_BUTTON_MAX:
				if app.USE_GROWTH_NEW_EVOLVE_WINDOW and self.feedIndex == player.FEED_EVOL_EVENT:
					return False

				if not self.CantFeedItem(slotIndex):
					if self.wndPetFeed.ItemMoveFeedWindow(windowType, slotIndex):
						return True
			elif self.GetState() == player.PET_WINDOW_ATTR_CHANGE:
				if self.ItemMoveAttrChangeWindow(windowType, slotIndex):
					return True
			elif  self.GetState() == player.PET_WINDOW_PRIMIUM_FEEDSTUFF:
				if self.ItemMovePremiumFeedWindow(windowType, slotIndex):
					return True

		return False
		
class TextToolTip(ui.Window):
	def __init__(self):
		ui.Window.__init__(self, "TOP_MOST")
		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetHorizontalAlignCenter()
		textLine.SetOutline()

		if app.USE_CTEXTLINE_AUTO_WRAP:
			textLine.SetAutoWrap(True)

		textLine.Show()
		self.textLine = textLine

	def __del__(self):
		ui.Window.__del__(self)

	def SetText(self, text):
		self.textLine.SetHorizontalAlignLeft()
		self.textLine.SetText(text)		

	def OnRender(self):
		(mouseX, mouseY) = wndMgr.GetMousePosition()

		if localeinfo.IsARABIC():
			mouseX = mouseX + 100
			mouseY = mouseY - 70
		else:
			mouseY = mouseY - 50

		mouseY = mouseY - (self.textLine.GetAutoWrapLinesCount() - 1) * 6
		self.textLine.SetPosition(mouseX, mouseY)
