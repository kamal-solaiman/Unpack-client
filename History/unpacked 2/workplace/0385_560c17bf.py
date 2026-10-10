# coding: latin_1

import app
import net
import player

import item
import ui
import uitooltip
import mousemodule
import localeinfo
import uicommon
import constinfo
import osfinfo
import ingamewiki
import grp
import net
import uiofflineshop_ae

import systemSetting

from _weakref import proxy

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

if app.WJ_ENABLE_TRADABLE_ICON:
	INVENTORY_PAGE_SIZE = player.INVENTORY_PAGE_SIZE

# Phase-WIP gate for the reworked "Stone Correction" refine window. Default ON so
# it is live on a pack rebuild with no client recompile; set to 0 to force the
# legacy RefineDialogNew. Promote to a real app.ENABLE_* flag when the rework ships.
ENABLE_REFINE_RENEWAL = getattr(app, "ENABLE_REFINE_RENEWAL", 1)

NEW_REFINE_ASSET = "d:/ymir work/ui/game/new_refine/"

if osfinfo.SHOW_REFINE_ITEM_DESC == True:
	TOOLTIP_DATA = {
		"materials" : [],
		"slot_count" : 0
	}

class RefineDialog(ui.ScriptWindow):
	makeSocketSuccessPercentage = ( 100, 33, 20, 15, 10, 5, 0 )
	upgradeStoneSuccessPercentage = ( 30, 29, 28, 27, 26, 25, 24, 23, 22 )
	upgradeArmorSuccessPercentage = ( 99, 66, 33, 33, 33, 33, 33, 33, 33 )
	upgradeAccessorySuccessPercentage = ( 99, 88, 77, 66, 33, 33, 33, 33, 33 )
	upgradeSuccessPercentage = ( 99, 66, 33, 33, 33, 33, 33, 33, 33 )
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__LoadScript()

		self.scrollItemPos = 0
		self.targetItemPos = 0
		self.IsShow = False

	def __LoadScript(self):
		self.__LoadQuestionDialog()

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/refinedialog.py")

		except:
			import exception
			exception.Abort("RefineDialog.__LoadScript.LoadObject")

		try:
			self.board = self.GetChild("Board")
			self.titleBar = self.GetChild("TitleBar")
			self.successPercentage = self.GetChild("SuccessPercentage")
			self.GetChild("AcceptButton").SetEvent(self.OpenQuestionDialog)
			self.GetChild("CancelButton").SetEvent(self.Close)
		except:
			import exception
			exception.Abort("RefineDialog.__LoadScript.BindObject")

		##if 936 == app.GetDefaultCodePage():
		if osfinfo.SHOW_REFINE_PERCENTAGE == True:
			self.successPercentage.Show()
		else:
			self.successPercentage.Hide()

		toolTip = uitooltip.ItemToolTip()
		toolTip.SetParent(self)
		toolTip.SetPosition(15, 38)
		toolTip.SetFollow(False)
		toolTip.Show()
		self.toolTip = toolTip

		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadQuestionDialog(self):
		self.dlgQuestion = ui.ScriptWindow()

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self.dlgQuestion, "uiscript/questiondialog2.py")
		except:
			import exception
			exception.Abort("RefineDialog.__LoadQuestionDialog.LoadScript")

		try:
			GetObject=self.dlgQuestion.GetChild
			GetObject("message1").SetText(localeinfo.REFINE_DESTROY_WARNING)
			GetObject("message2").SetText(localeinfo.REFINE_WARNING2)
			GetObject("accept").SetEvent(ui.__mem_func__(self.Accept))
			GetObject("cancel").SetEvent(ui.__mem_func__(self.dlgQuestion.Hide))
		except:
			import exception
			exception.Abort("SelectCharacterWindow.__LoadQuestionDialog.BindObject")

	def Destroy(self):
		self.ClearDictionary()
		self.board = 0
		self.successPercentage = 0
		self.titleBar = 0
		self.toolTip = 0
		self.dlgQuestion = 0

	def GetRefineSuccessPercentage(self, scrollSlotIndex, itemSlotIndex):
		if -1 != scrollSlotIndex:
			if player.IsRefineGradeScroll(scrollSlotIndex):
				curGrade = player.GetItemGrade(itemSlotIndex)
				itemIndex = player.GetItemIndex(itemSlotIndex)

				item.SelectItem(itemIndex)
				itemType = item.GetItemType()
				itemSubType = item.GetItemSubType()

				if item.ITEM_TYPE_METIN == itemType:
					if curGrade >= len(self.upgradeStoneSuccessPercentage):
						return 0
					return self.upgradeStoneSuccessPercentage[curGrade]

				elif item.ITEM_TYPE_ARMOR == itemType:
					if item.ARMOR_BODY == itemSubType:
						if curGrade >= len(self.upgradeArmorSuccessPercentage):
							return 0
						return self.upgradeArmorSuccessPercentage[curGrade]
					else:
						if curGrade >= len(self.upgradeAccessorySuccessPercentage):
							return 0
						return self.upgradeAccessorySuccessPercentage[curGrade]
				else:
					if curGrade >= len(self.upgradeSuccessPercentage):
						return 0
					return self.upgradeSuccessPercentage[curGrade]

		for i in xrange(player.METIN_SOCKET_MAX_NUM+1):
			if 0 == player.GetItemMetinSocket(itemSlotIndex, i):
				break

		return self.makeSocketSuccessPercentage[i]

	def Open(self, scrollItemPos, targetItemPos):
		self.scrollItemPos = scrollItemPos
		self.targetItemPos = targetItemPos

		percentage = self.GetRefineSuccessPercentage(scrollItemPos, targetItemPos)
		if 0 == percentage:
			return
		self.successPercentage.SetText(localeinfo.REFINE_SUCCESS_PROBALITY % (percentage))

		itemIndex = player.GetItemIndex(targetItemPos)
		self.toolTip.ClearToolTip()
		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(player.GetItemMetinSocket(targetItemPos, i))
		self.toolTip.AddItemData(itemIndex, 0)

		self.UpdateDialog()
		self.SetTop()
		self.Show()
		self.IsShow = True

	def UpdateDialog(self):
		newWidth = self.toolTip.GetWidth() + 30
		newHeight = self.toolTip.GetHeight() + 98
		self.board.SetSize(newWidth, newHeight)
		self.titleBar.SetWidth(newWidth-15)
		self.SetSize(newWidth, newHeight)

		(x, y) = self.GetLocalPosition()
		self.SetPosition(x, y)

	def OpenQuestionDialog(self):
		percentage = self.GetRefineSuccessPercentage(-1, self.targetItemPos)
		if 100 == percentage:
			self.Accept()
			return

		self.dlgQuestion.SetTop()
		self.dlgQuestion.Show()

	def Accept(self):
		net.SendItemUseToItemPacket(self.scrollItemPos, self.targetItemPos)
		self.Close()

	def Close(self):
		self.dlgQuestion.Hide()
		self.Hide()
		self.IsShow = False

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def IsShow(self):
		return self.IsShow

class RefineDialogNew(ui.ScriptWindow):
	NEGATIVE_COLOR = grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0)
	POSITIVE_COLOR = grp.GenerateColor(0.5411, 0.7254, 0.5568, 1.0)

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.interface = None
			self.inven = None

		self.__Initialize()
		self.isLoaded = False

		self.wndWiki = None

	def __Initialize(self):
		self.dlgQuestion = None
		self.children = []
		self.vnum = 0
		self.targetItemPos = 0
		self.dialogHeight = 0
		self.cost = 0
		self.percentage = 0
		self.type = 0
		self.apply_random_list = None
		self.src_vnum = 0
		self.IsShow = False

	def __LoadScript(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/refinedialog.py")

		except:
			import exception
			exception.Abort("RefineDialog.__LoadScript.LoadObject")

		try:
			self.board = self.GetChild("Board")
			self.titleBar = self.GetChild("TitleBar")
			self.probText = self.GetChild("SuccessPercentage")
			self.costText = self.GetChild("Cost")
			self.successPercentage = self.GetChild("SuccessPercentage")
			self.GetChild("AcceptButton").SetEvent(self.OpenQuestionDialog)
			self.GetChild("CancelButton").SetEvent(self.CancelRefine)
		except:
			import exception
			exception.Abort("RefineDialog.__LoadScript.BindObject")

		##if 936 == app.GetDefaultCodePage():
		if osfinfo.SHOW_REFINE_PERCENTAGE == True:
			self.successPercentage.Show()
		else:
			self.successPercentage.Hide()

		toolTip = uitooltip.ItemToolTip()
		toolTip.SetParent(self)
		toolTip.SetFollow(False)
		toolTip.SetPosition(15, 38)
		toolTip.Show()
		self.toolTip = toolTip
		self.overInSlot = None

		if osfinfo.SHOW_REFINE_ITEM_DESC == True:
			self.toolTipItem = uitooltip.ItemToolTip()
			self.toolTipItem.Hide()

		self.slotList = []
		for i in xrange(3):
			slot = self.__MakeSlot()
			slot.SetParent(toolTip)
			slot.SetWindowVerticalAlignCenter()
			self.slotList.append(slot)

		itemImage = self.__MakeItemImage()
		itemImage.SetParent(toolTip)
		itemImage.SetWindowVerticalAlignCenter()
		#itemImage.SetPosition(190, 0)
		itemImage.SetPosition(-35, 0)
		self.itemImage = itemImage

		self.titleBar.SetCloseEvent(ui.__mem_func__(self.CancelRefine))
		self.isLoaded = True

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __MakeSlot(self):
		slot = ui.ImageBox()
		slot.LoadImage("d:/ymir work/ui/public/slot_base.sub")
		slot.Show()
		self.children.append(slot)
		return slot

	if osfinfo.SHOW_REFINE_ITEM_DESC == True:
		def __MakeItemSlot(self, slotIndex):
			slot = ui.SlotWindow()
			slot.SetParent(self)
			slot.SetSize(32, 32)
			slot.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
			slot.AppendSlot(slotIndex, 0, 0, 32, 32)
			slot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
			slot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			slot.SetUnselectItemSlotEvent(ui.__mem_func__(self.SearchInWiki))
			slot.RefreshSlot()
			slot.Show()
			self.children.append(slot)
			return slot

		def OverInItem(self, slotIndex):
			if slotIndex > len(TOOLTIP_DATA["materials"]):
				return

			itemVnum = TOOLTIP_DATA["materials"][slotIndex]
			metinSlot = []
			attrSlot = []
			rare_attr_slot = None
			flags = 0
			unbindTime = 0
			window_type = player.INVENTORY

			for i in xrange(player.METIN_SOCKET_MAX_NUM):
				metinSlot.append(0)

			if self.toolTipItem:
				self.toolTipItem.ClearToolTip()
				self.toolTipItem.AddItemData(itemVnum, 0)
				self.toolTipItem.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_WIKI_HOVER)
				self.toolTipItem.DeclareShortcut(("key_alt", "key_rclick"), localeinfo.TOOLTIP_QUICKSEARCH_OFFLINESHOP)
				self.toolTipItem.AlignHorizonalCenter()
				self.toolTipItem.ShowToolTip()
			self.overInSlot = slotIndex

		def OverOutItem(self):
			if self.toolTipItem:
				self.toolTipItem.HideToolTip()
			self.overInSlot = 0

	def SearchInWiki(self):
		slotIndex = self.overInSlot
		if slotIndex > len(TOOLTIP_DATA["materials"]):
			return

		vnum = TOOLTIP_DATA["materials"][slotIndex]

		if app.IsPressed(app.DIK_LSHIFT):
			if not self.wndWiki.IsShow():
				net.ToggleWikiWindow()

			self.wndWiki.CloseBaseWindows()
			self.wndWiki.OpenSpecialPage(None, vnum, False)

		if app.USE_OFFLINESHOP and\
			not uiofflineshop_ae.IsBuildingShop() and\
			(app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT)):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				wndShopOffline = interfaceHandler.wndShopOffline
				if wndShopOffline:
					wndSearchShop = wndShopOffline.wndSearchShop
					if wndSearchShop:
						wndSearchShop.SearchByName(item.GetItemNameByVnum(vnum))

	def __MakeItemImage(self):
		itemImage = ui.ImageBox()
		itemImage.Show()
		self.children.append(itemImage)
		return itemImage

	def __MakeThinBoard(self):
		thinBoard = ui.ThinBoard("UI",2)
		thinBoard.SetParent(self)
		thinBoard.Show()
		self.children.append(thinBoard)
		return thinBoard

	def Destroy(self):
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.interface = None
			self.inven = None

		self.ClearDictionary()
		self.dlgQuestion = None
		self.board = 0
		self.probText = 0
		self.costText = 0
		self.titleBar = 0
		self.toolTip = 0
		self.successPercentage = None
		self.slotList = []
		self.children = []
		self.wndWiki = None

	def Open(self, targetItemPos, nextGradeItemVnum, cost, prob, type, apply_random_list, src_vnum):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "REFINE")
		if False == self.isLoaded:
			self.__LoadScript()
			self.MakePittyInfoWindow() #PITTY_REFINE

		self.__Initialize()
		self.boardPitty.Hide() #PITTY_REFINE

		self.targetItemPos = targetItemPos
		self.vnum = nextGradeItemVnum
		self.cost = cost
		self.percentage = prob
		self.type = type
		self.apply_random_list = apply_random_list
		self.src_vnum = src_vnum

		self.probText.SetText(localeinfo.REFINE_SUCCESS_PROBALITY % (self.percentage))
		self.costText.SetText(localeinfo.REFINE_COST % (self.cost))
		if app.ENABLE_AUTO_REFINE:
			self.checkBox = ui.CheckBox()
			self.checkBox.SetParent(self)
			self.checkBox.SetPosition(0, 90)
			self.checkBox.SetWindowHorizontalAlignCenter()
			self.checkBox.SetWindowVerticalAlignBottom()
			self.checkBox.SetEvent(ui.__mem_func__(self.AutoRefine), "ON_CHECK", True)
			self.checkBox.SetEvent(ui.__mem_func__(self.AutoRefine), "ON_UNCKECK", False)
			self.checkBox.SetCheckStatus(osfinfo.IS_AUTO_REFINE)
			self.checkBox.SetTextInfo(localeinfo.REFINE_AUTO)
			self.checkBox.Show()

		self.toolTip.ClearToolTip()
		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(player.GetItemMetinSocket(targetItemPos, i))

		attrSlot = []
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			attrSlot.append(player.GetItemAttribute(targetItemPos, i))

		#def AddRefineItemData(self, item_vnum, sockets, attributes, rare_attr_slot = None, flags = 0, refine_element = None, apply_random_list = None, set_value = 0):
		if app.ENABLE_APPLY_RANDOM:
			self.toolTip.AddRefineItemData(nextGradeItemVnum, metinSlot, attrSlot, None, type, None, apply_random_list, 0)
		else:
			self.toolTip.AddRefineItemData(nextGradeItemVnum, metinSlot, attrSlot, type)

		item.SelectItem(nextGradeItemVnum)
		self.itemImage.LoadImage(item.GetIconImageFileName())
		xSlotCount, ySlotCount = item.GetItemSize()
		for slot in self.slotList:
			slot.Hide()
		for i in xrange(min(3, ySlotCount)):
			self.slotList[i].SetPosition(-35, i*32 - (ySlotCount-1)*16)
			self.slotList[i].Show()

		self.dialogHeight = self.toolTip.GetHeight() + 46
		self.UpdateDialog()

		if osfinfo.IS_AUTO_REFINE == True and osfinfo.AUTO_REFINE == True:
			pass
		else:
			self.SetTop()

		self.Show()
		self.IsShow = True

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "REFINE")
		self.dlgQuestion = None
		self.Hide()
		self.IsShow = False
		if app.ENABLE_AUTO_REFINE:
			osfinfo.AUTO_REFINE = False

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("REFINE", x, y)

	def IsShow(self):
		return self.IsShow

	#PITTY_REFINE
	def MakePittyInfoWindow(self):
		self.boardPitty = ui.ThinBoardCircle()
		self.boardPitty.SetParent(self)
		self.boardPitty.SetPosition(14, 370)
		self.boardPitty.SetSize(221, 31+2)
		self.boardPitty.Show()

		self.btnMark = ui.MakeButton(self.boardPitty, self.boardPitty.GetWidth() - 20, 3, False, "d:/ymir work/ui/pattern/", "q_mark_01.tga", "q_mark_02.tga", "q_mark_01.tga")
		self.btnMark.SetEventOverIn(ui.__mem_func__(self.OverInMarkPitty))
		self.btnMark.SetEventOverOut(ui.__mem_func__(self.OverOutItemPitty))
		
		self.wndTextPitty = ui.MakeTextLine(self.boardPitty)
		self.wndTextPitty.SetText(localeinfo.PITTY_REFINE_ENERGY_STILL)
		self.wndTextPitty.SetPosition(0, -8)
		
		self.wndGaugePitty = ui.Gauge()
		self.wndGaugePitty.SetParent(self.boardPitty)
		self.wndGaugePitty.SetPosition(5, 22)
		self.wndGaugePitty.MakeGauge(self.boardPitty.GetWidth() - 10, "red_spc")
		self.wndGaugePitty.Show()
	
	def OverInMarkPitty(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.ClearToolTip()
			interfaceHandler.tooltipItem.SetCannotUseItemForceSetDisableColor(False)

			interfaceHandler.tooltipItem.SetTitle(localeinfo.PITTY_REFINE_TITLE)
			interfaceHandler.tooltipItem.AppendSpace(7)
			interfaceHandler.tooltipItem.AppendDescription(
			"{}".format(localeinfo.PITTY_REFINE_DEC1) +
			"{}".format(localeinfo.PITTY_REFINE_DEC2), 26,grp.GenerateColor(248/255.0, 239/255.0, 186/255.0, 1.0))
			interfaceHandler.tooltipItem.AppendHorizontalLine()
			interfaceHandler.tooltipItem.AppendDescription(
			"{}".format(localeinfo.PITTY_REFINE_DEC3) +
			"{}".format(localeinfo.PITTY_REFINE_DEC4) , 26,grp.GenerateColor(248/255.0, 239/255.0, 186/255.0, 1.0))

			interfaceHandler.tooltipItem.ShowToolTip()

	def OverOutItemPitty(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interface.tooltipItem.HideToolTip()

	def SetPittyInfo(self, forVnum, pittyCurrent, pittyMax):
		if player.GetItemIndex(self.targetItemPos) != forVnum or pittyMax == 0:
			self.boardPitty.Hide()
			self.UpdateDialog()
			return
		if pittyCurrent == pittyMax:
			self.wndTextPitty.SetText(localeinfo.PITTY_REFINE_ENERGY_FILLED % (pittyMax,pittyCurrent))
			self.wndTextPitty.SetPackedFontColor(0xfffad390)
			self.wndTextPitty.SetOutline()
			self.percentage = 100
		else:
			self.wndTextPitty.SetText(localeinfo.PITTY_REFINE_ENERGY_STILL % (pittyMax,pittyCurrent))
			self.wndTextPitty.SetPackedFontColor(0xffDEE3E9)
		
		self.wndGaugePitty.SetPercentage(pittyCurrent, pittyMax)
		#self.wndGaugePitty.SetToolTipText("%d \ %d" % (pittyCurrent,pittyMax))
		self.boardPitty.Show()
		self.UpdateDialog()

	def AppendMaterial(self, vnum, count):
		item_count = player.GetItemCountByVnum(vnum)
		curMoney = player.GetMoney()
		if osfinfo.SHOW_REFINE_ITEM_DESC == True:
			slotIndex = len(TOOLTIP_DATA["materials"])

			slot = self.__MakeItemSlot(slotIndex)
			slot.SetPosition(15, self.dialogHeight)
			slot.SetItemSlot(slotIndex, vnum, count)

			TOOLTIP_DATA["materials"].append(vnum)
		else:
			slot = self.__MakeSlot()
			slot.SetParent(self)
			slot.SetPosition(15, self.dialogHeight)

			itemImage = self.__MakeItemImage()
			itemImage.SetParent(slot)
			item.SelectItem(vnum)
			itemImage.LoadImage(item.GetIconImageFileName())

		thinBoard = self.__MakeThinBoard()
		thinBoard.SetPosition(50, self.dialogHeight)
		thinBoard.SetSize(self.toolTip.GetWidth(), 20)

		name = "%s %d / x%d" % (item.GetItemName(),item_count,count)

		textColor = self.POSITIVE_COLOR if item_count >= count else self.NEGATIVE_COLOR

		textLine = ui.TextLine()
		textLine.SetParent(thinBoard)
		textLine.SetFontName(localeinfo.UI_DEF_FONT)
		textLine.SetPackedFontColor(textColor)
		textLine.SetText(name)
		textLine.SetOutline()
		textLine.SetFeather(False)
		if not localeinfo.IsARABIC():
			textLine.SetWindowVerticalAlignCenter()
			textLine.SetVerticalAlignCenter()

		if localeinfo.IsARABIC():
			(x,y) = textLine.GetTextSize()
			textLine.SetPosition(180, 0)
		else:
			textLine.SetPosition(15, 0)

		textLine.Show()
		self.children.append(textLine)

		self.dialogHeight += 34
		self.UpdateDialog()

	def UpdateDialog(self):
		newWidth = self.toolTip.GetWidth() + 60
		if app.ENABLE_AUTO_REFINE:
			newHeight = self.dialogHeight + 69 + 40
		else:
			newHeight = self.dialogHeight + 69

		##if 936 == app.GetDefaultCodePage():
		newHeight -= 8

		#PITTY_REFINE
		if self.boardPitty.IsShow():
			self.boardPitty.SetPosition(14, newHeight - 95)
			newHeight += self.boardPitty.GetHeight() + 2

		if localeinfo.IsARABIC():
			self.board.SetPosition(newWidth, 0)

			(x, y) = self.titleBar.GetLocalPosition()
			self.titleBar.SetPosition(newWidth - 15, y)

		self.board.SetSize(newWidth, newHeight)
		self.toolTip.SetPosition(15 + 35, 38)
		self.titleBar.SetWidth(newWidth-15)
		self.SetSize(newWidth, newHeight)

		(x, y) = self.GetLocalPosition()
		self.SetPosition(x, y)

	def OpenQuestionDialog(self):
		if 100 == self.percentage:
			self.Accept()
			return

		if 5 == self.type:
			self.Accept()
			return

		if app.ENABLE_STONE_OF_BLESS:
			if 7 == self.type:
				self.Accept()
				return

		if app.ENABLE_SOUL_SYSTEM:
			if 8 == self.type or 9 == self.type:
				self.Accept()
				return

		if app.NEW_WELLY_UPGRADE_STONES:
			if 11 == self.type or 12 == self.type or 10 == self.type:#no need for warning
				self.Accept()
				return

		dlgQuestion = uicommon.QuestionDialog2()
		dlgQuestion.SetText2(localeinfo.REFINE_WARNING2)
		dlgQuestion.SetAcceptEvent(ui.__mem_func__(self.Accept))
		dlgQuestion.SetCancelEvent(ui.__mem_func__(dlgQuestion.Close))

		if 3 == self.type:
			if localeinfo.IsEUROPE():
				if dlgQuestion:
					del dlgQuestion

				dlgQuestion = uicommon.QuestionDialog()
				dlgQuestion.SetAcceptEvent(ui.__mem_func__(self.Accept))
				dlgQuestion.SetCancelEvent(ui.__mem_func__(dlgQuestion.Close))
				dlgQuestion.SetText(localeinfo.REFINE_DESTROY_WARNING_WITH_BONUS_PERCENT_1)
			else:
				dlgQuestion.SetText1(localeinfo.REFINE_DESTROY_WARNING_WITH_BONUS_PERCENT_1)
				dlgQuestion.SetText2(localeinfo.REFINE_DESTROY_WARNING_WITH_BONUS_PERCENT_2)
		elif 2 == self.type:
			dlgQuestion.SetText1(localeinfo.REFINE_DOWN_GRADE_WARNING)
		else:
			dlgQuestion.SetText1(localeinfo.REFINE_DESTROY_WARNING)

		dlgQuestion.Open()
		self.dlgQuestion = dlgQuestion

	def Accept(self):
		if app.ENABLE_AUTO_REFINE:
			net.SendRefinePacket(self.targetItemPos, self.type)
		else:
			net.SendRefinePacket(self.targetItemPos, self.type)
			self.Close()

	def CancelRefine(self):
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.SetCanMouseEventSlot(self.targetItemPos)
		
		self.targetItemPos = 0
		
		net.SendRefinePacket(255, 255)
		self.Close()
		
		if app.ENABLE_AUTO_REFINE:
			osfinfo.AUTO_REFINE = False
			osfinfo.AUTO_REFINE_TYPE = 0
			osfinfo.AUTO_REFINE_DATA = {
				"ITEM" : [-1, -1],
				"NPC" : [0, -1, -1, 0]
			}

		if osfinfo.SHOW_REFINE_ITEM_DESC:
			TOOLTIP_DATA["materials"] = []

	if app.ENABLE_AUTO_REFINE:
		def AutoRefine(self, checkType, autoFlag):
			osfinfo.IS_AUTO_REFINE = autoFlag

		def CheckRefine(self, isFail):
			if osfinfo.IS_AUTO_REFINE == True:
				if osfinfo.AUTO_REFINE_TYPE == 1:
					if osfinfo.AUTO_REFINE_DATA["ITEM"][0] != -1 and osfinfo.AUTO_REFINE_DATA["ITEM"][1] != -1:
						scrollIndex = player.GetItemIndex(osfinfo.AUTO_REFINE_DATA["ITEM"][0])
						itemIndex = player.GetItemIndex(osfinfo.AUTO_REFINE_DATA["ITEM"][1])

						if int(itemIndex % 10) == 9:
							self.Close()

						if scrollIndex <= 0 or (itemIndex % 10 == 8 and not isFail):
							self.Close()
						else:
							osfinfo.AUTO_REFINE = True
							net.SendItemUseToItemPacket(osfinfo.AUTO_REFINE_DATA["ITEM"][0], osfinfo.AUTO_REFINE_DATA["ITEM"][1])

				elif osfinfo.AUTO_REFINE_TYPE == 2:
					npcData = osfinfo.AUTO_REFINE_DATA["NPC"]
					if npcData[0] != 0 and npcData[1] != -1 and npcData[2] != -1 and npcData[3] != 0:
						itemIndex = player.GetItemIndex(npcData[1], npcData[2])

						if int(itemIndex %10) == 9:
							self.Close()

						if (itemIndex % 10 == 8 and not isFail) or isFail:
							self.Close()
						else:
							osfinfo.AUTO_REFINE = True
							net.SendGiveItemPacket(npcData[0], npcData[1], npcData[2], npcData[3])
				else:
					self.Close()
			else:
				self.Close()

	def OnPressEscapeKey(self):
		self.CancelRefine()
		return True

	if app.WJ_ENABLE_TRADABLE_ICON:
		def BindInterface(self, interface):
			if interface:
				self.interface = proxy(interface)

		def SetInven(self, inven):
			if inven:
				self.inven = proxy(inven)

		def SetCanMouseEventSlot(self, idx):
			if idx >= INVENTORY_PAGE_SIZE:
				page = self.inven.GetInventoryPageIndex()
				idx -= (page * INVENTORY_PAGE_SIZE)
			
			self.inven.wndItem.SetCanMouseEventSlot(idx)

		def OnUpdate(self):
			if not self.inven:
				return
			
			targetItemPos = self.targetItemPos
			if targetItemPos <= 0:
				return
			
			page = self.inven.GetInventoryPageIndex()
			
			if (page * INVENTORY_PAGE_SIZE) <= targetItemPos < ((page + 1) * INVENTORY_PAGE_SIZE):
				lock_idx = targetItemPos - (page * INVENTORY_PAGE_SIZE)
				self.inven.wndItem.SetCantMouseEventSlot(lock_idx)


class _RefineRecIcon(ui.ImageBox):
	def __init__(self):
		ui.ImageBox.__init__(self)
		self.owner = None

	def __del__(self):
		ui.ImageBox.__del__(self)

	def OnMouseOverIn(self):
		if self.owner:
			self.owner.OnRecIconOver()

	def OnMouseOverOut(self):
		if self.owner:
			self.owner.OnRecIconOut()

	def OnMouseLeftButtonUp(self):
		if self.owner:
			self.owner.OnRecIconClick()


class RefineRecommendConfirm(ui.ScriptWindow):
	# Refine OK-confirm popup enriched with a recommended guarantee-item hint: the
	# same destroy/downgrade warning as the stock confirm, plus a framed, hoverable,
	# wiki-linked icon of the item that guarantees this upgrade. Built in Python so
	# the shared uicommon.QuestionDialog2 layout stays untouched.
	FE_BTN  = "d:/ymir work/ui/game/new_fast_equip/"
	WIDTH   = 320
	HEIGHT  = 232
	MSG1_Y  = 38
	MSG2_Y  = 58
	PANEL_X = 14
	PANEL_Y = 80
	PANEL_W = 292
	PANEL_H = 110
	HINT_Y  = 88
	SLOT    = 40
	SLOT_Y  = 110
	NAME_Y  = 158
	BTN_Y   = 192
	BTN_W   = 126
	COL_WARN = (0.90, 0.72, 0.42)
	COL_TEXT = (0.80, 0.82, 0.86)
	COL_HINT = (0.62, 0.66, 0.72)
	COL_NAME = (0.96, 0.86, 0.55)

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.AddFlag("movable")
		self.AddFlag("float")
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		self.acceptEvent = None
		self.recVnum = 0
		self.slotX = 0
		self.keepRefs = []
		self.icon = None
		self.nameText = None
		self.msg1 = None
		self.msg2 = None
		self.itemToolTip = None
		try:
			self.rtl = localeinfo.IsARABIC()
		except:
			self.rtl = False
		self.__Build()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __Label(self, y, color):
		t = ui.TextLine()
		t.SetParent(self)
		t.SetPosition(self.WIDTH / 2, y)
		t.SetHorizontalAlignCenter()
		t.SetFontColor(*color)
		t.Show()
		self.keepRefs.append(t)
		return t

	def __Button(self, x, text, event):
		b = ui.Button()
		b.SetParent(self)
		b.SetUpVisual(self.FE_BTN + "btn_norm.png")
		b.SetOverVisual(self.FE_BTN + "btn_hover.png")
		b.SetDownVisual(self.FE_BTN + "btn_select.png")
		b.SetText(text)
		b.SetPosition(x, self.BTN_Y)
		b.SetEvent(ui.__mem_func__(event))
		b.Show()
		self.keepRefs.append(b)
		return b

	def __Build(self):
		board = ui.BoardWithTitleBar()
		board.SetParent(self)
		board.SetSize(self.WIDTH, self.HEIGHT)
		board.SetTitleName(localeinfo.REFINE_RECOMMEND_TITLE)
		board.SetCloseEvent(ui.__mem_func__(self.Close))
		board.Show()
		self.board = board
		self.SetSize(self.WIDTH, self.HEIGHT)

		self.msg1 = self.__Label(self.MSG1_Y, self.COL_WARN)
		self.msg2 = self.__Label(self.MSG2_Y, self.COL_TEXT)

		panel = ui.ThinBoard("UI", 2)
		panel.SetParent(self)
		panel.SetSize(self.PANEL_W, self.PANEL_H)
		panel.SetPosition(self.PANEL_X, self.PANEL_Y)
		panel.Show()
		self.keepRefs.append(panel)

		hint = self.__Label(self.HINT_Y, self.COL_HINT)
		hint.SetText(localeinfo.REFINE_RECOMMEND_HINT)

		self.slotX = (self.WIDTH - self.SLOT) / 2
		slotBg = ui.ImageBox()
		slotBg.SetParent(self)
		slotBg.AddFlag("not_pick")
		slotBg.LoadImage(NEW_REFINE_ASSET + "slot_material.png")
		slotBg.SetPosition(self.slotX, self.SLOT_Y)
		slotBg.Show()
		self.keepRefs.append(slotBg)

		icon = _RefineRecIcon()
		icon.SetParent(self)
		icon.owner = self
		icon.Show()
		self.icon = icon

		self.nameText = self.__Label(self.NAME_Y, self.COL_NAME)

		if self.rtl:
			okX, cancelX = (self.WIDTH - 20 - self.BTN_W, 20)
		else:
			okX, cancelX = (20, self.WIDTH - 20 - self.BTN_W)
		self.__Button(okX, localeinfo.UI_OK, self.__OnAccept)
		self.__Button(cancelX, localeinfo.UI_CANCEL, self.Close)

		self.itemToolTip = uitooltip.ItemToolTip()
		self.itemToolTip.Hide()

	def Setup(self, line1, line2, recVnum, acceptEvent):
		self.acceptEvent = acceptEvent
		self.msg1.SetText(line1)
		self.msg2.SetText(line2)
		self.__SetRecItem(recVnum)

	def __SetRecItem(self, vnum):
		self.recVnum = vnum
		item.SelectItem(vnum)
		path = item.GetIconImageFileName()
		if path:
			self.icon.LoadImage(path)
		iw = self.icon.GetWidth() or 32
		ih = self.icon.GetHeight() or 32
		self.icon.SetPosition(self.slotX + (self.SLOT - iw) / 2, self.SLOT_Y + (self.SLOT - ih) / 2)
		self.icon.Show()
		self.nameText.SetText(item.GetItemName())

	def OnRecIconOver(self):
		if self.recVnum and self.itemToolTip:
			self.itemToolTip.SetItemToolTip(self.recVnum)

	def OnRecIconOut(self):
		if self.itemToolTip:
			self.itemToolTip.HideToolTip()

	def OnRecIconClick(self):
		if not self.recVnum:
			return
		import wiki
		isBox = 1 if item.GetItemTypeByVnum(self.recVnum) == item.ITEM_TYPE_GIFTBOX else 0
		wiki.GetBaseClass().OpenSpecialWikiPage(self.recVnum, isBox)

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.OnRecIconOut()
		self.Hide()

	def __OnAccept(self):
		if self.acceptEvent:
			self.acceptEvent()
		self.Close()

	def OnPressEscapeKey(self):
		self.Close()
		return True


if ENABLE_REFINE_RENEWAL:
	class RefineDialogRenewal(ui.ScriptWindow):
		# Reworked "Stone Correction" window. Phase 1 = top area only: title, an
		# "Upgrade Result" panel (item slot + a wheel-scrolled attribute preview
		# inside bg_desc), and a "Requirements" slot row. Chrome/positions live in
		# uiscript/refinedialogrenewal.py; this class only wires behaviour + dynamic
		# widgets. Accept/cost/pity land in later phases; close via title X / ESC
		# sends the cancel packet so the server refine state clears cleanly.
		NEGATIVE_COLOR = grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0)
		POSITIVE_COLOR = grp.GenerateColor(0.5411, 0.7254, 0.5568, 1.0)
		TITLE_COLOR    = grp.GenerateColor(0.9490, 0.9058, 0.7568, 1.0)

		ATTR_STEP = 17

		MAT_MAX  = 5
		MAT_SLOT = 32          # actual (native) slot size, so SetItemSlot's count renders correctly
		MAT_CELL = 40          # cell/refine_count_bg width; the 32 slot is centred in it
		MAT_GAP  = 5
		MAT_TOP  = 9           # slot y within the material panel (row auto-centres on X)
		SLOT_BASE_IMAGE = "d:/ymir work/ui/public/Slot_Base.sub"

		# Pity = a ROW OF DISCRETE PIPS: one pitty_empty.png per pity point, each overlaid
		# with pitty_full.png once earned (current/max from the server). Natural image size,
		# laid contiguous + centred in the bar - NOT a stretched gauge. Tune via the uiscript
		# pity bar position + these consts.
		PITY_TRACK_L = 8       # left inset of the pip row within the pity bar
		PITY_TRACK_R = 30      # right inset (leaves room for the hover icon)
		PITY_PIP_TOP = 11      # pip row y within the pity bar
		PITY_PIP_GAP = 3       # px between adjacent pips
		PITY_PIP_W   = 24      # pitty_empty.png natural size
		PITY_PIP_H   = 11
		PITY_FULL_W  = 20      # pitty_full.png natural size (overlaid, centred on a pip)
		PITY_FULL_H  = 7
		PITY_FILLED_COLOR = grp.GenerateColor(0.9803, 0.8235, 0.5647, 1.0)
		# Refine 'type' values that force 100% success server-side even though the info
		# packet still carries the base recipe prob (<100). Only REFINE_TYPE_MUSIN (5) is
		# a true 100% scroll; bless(7)/bdragon(6) are NOT guaranteed, so stay off this.
		GUARANTEED_REFINE_TYPES = (5,)
		# Recommended guarantee-item hint for the OK confirm popup. Each entry is
		# (minGrade, maxGrade, itemVnum): when the target item's refine grade is in
		# [min,max] and the shown success chance is < 100, the confirm suggests
		# itemVnum (a guaranteed-success item) and links its wiki page.
		REFINE_RECOMMEND_MAP = ((0, 3, 71021),)
		# Price row: yang icon + number centred as one cluster (positioned in Python each
		# Open since the number width varies; a centred cluster is also RTL-mirror-safe).
		PRICE_ROW_W    = 247
		PRICE_YANG_W   = 22
		PRICE_YANG_GAP = 4
		PRICE_YANG_Y   = 5
		PRICE_TEXT_Y   = 6

		def __init__(self):
			ui.ScriptWindow.__init__(self)
			if app.ENABLE_WINDOW_SLIDE_EFFECT:
				self.AddFlag("animated_board")
			if app.WJ_ENABLE_TRADABLE_ICON:
				self.interface = None
				self.inven = None
			self.__Initialize()
			self.__LoadScript()
			self.wndWiki = None

		def __Initialize(self):
			self.materialSlots = []
			self.materialVnums = []
			self.materialFilled = 0
			self.vnum = 0
			self.targetItemPos = 0
			self.cost = 0
			self.percentage = 0
			self.type = 0
			self.apply_random_list = None
			self.src_vnum = 0
			self.metinSlot = []
			self.attrSlot = []
			self.attrContentH = 0
			self.attrOverflow = 0
			self.attrScrollPos = 0
			self.pityBar = None
			self.pityIcon = None
			self.pityIconHover = None
			self.pityEmptyPips = []
			self.pityFullPips = []
			self.pityCurrent = 0
			self.pityMax = 0
			self.chanceBgSuccess = None
			self.chanceBgFail = None
			self.chanceText = None
			self.okButton = None
			self.cancelButton = None
			self.dlgQuestion = None
			self.keepOpen = False
			self.refreshPending = False
			self.keepChk = None
			self.priceText = None
			self.yangIcon = None
			self.bonusRow = None
			self.bonusText = None
			self.refineBonus = 0
			self.IsShow = False

		def __del__(self):
			ui.ScriptWindow.__del__(self)

		def __LoadScript(self):
			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "uiscript/refinedialogrenewal.py")
			except:
				import exception
				exception.Abort("RefineDialogRenewal.__LoadScript.LoadObject")

			try:
				self.board = self.GetChild("board")
				self.itemPanel = self.GetChild("ItemPanel")
				self.itemSlotBg = self.GetChild("ItemSlotBg")
				self.descBg = self.GetChild("DescBg")
				self.matPanel = self.GetChild("MatPanel")
				self.pityBar = self.GetChild("PityBar")
				self.pityIcon = self.GetChild("PityIcon")
				self.header1Text = self.GetChild("Header1Text")
				self.header2Text = self.GetChild("Header2Text")
				self.chanceBgSuccess = self.GetChild("ChanceBgSuccess")
				self.chanceBgFail = self.GetChild("ChanceBgFail")
				self.chanceText = self.GetChild("ChanceText")
				self.okButton = self.GetChild("OKButton")
				self.cancelButton = self.GetChild("CancelButton")
				self.keepChk = self.GetChild("ChkKeepOpen")
				self.priceText = self.GetChild("PriceText")
				self.yangIcon = self.GetChild("YangIcon")
				self.bonusRow = self.GetChild("BonusRow")
				self.bonusText = self.GetChild("BonusText")
			except:
				import exception
				exception.Abort("RefineDialogRenewal.__LoadScript.BindObject")

			self.board.SetCloseEvent(ui.__mem_func__(self.CancelRefine))
			self.board.SetTitleName(getattr(localeinfo, "REFINE_RENEWAL_TITLE", "Stone Correction"))

			self.okButton.SetText(getattr(localeinfo, "UI_OK", "OK"))
			self.okButton.SetEvent(ui.__mem_func__(self.OpenQuestionDialog))
			self.cancelButton.SetText(getattr(localeinfo, "UI_CANCEL", "Cancel"))
			self.cancelButton.SetEvent(ui.__mem_func__(self.CancelRefine))
			self.keepChk.SetEvent(ui.__mem_func__(self.__OnToggleKeepOpen))
			self.bonusRow.Hide()

			self.header1Text.SetText(getattr(localeinfo, "REFINE_UPGRADE_RESULT", "Upgrade Result"))
			self.header1Text.SetPackedFontColor(self.TITLE_COLOR)
			self.header1Text.SetOutline()
			self.header2Text.SetText(getattr(localeinfo, "REFINE_REQUIREMENTS", "Requirements"))
			self.header2Text.SetPackedFontColor(self.TITLE_COLOR)
			self.header2Text.SetOutline()

			# Result-item icon on the left slot + a pickable hover catcher that shows
			# the normal floating item tooltip.
			itemIcon = ui.ImageBox()
			itemIcon.SetParent(self.itemSlotBg)
			itemIcon.SetWindowHorizontalAlignCenter()
			itemIcon.SetWindowVerticalAlignCenter()
			itemIcon.Show()
			self.itemIcon = itemIcon

			itemHover = ui.Window()
			itemHover.SetParent(self.itemSlotBg)
			itemHover.SetPosition(0, 0)
			itemHover.SetSize(self.itemSlotBg.GetWidth(), self.itemSlotBg.GetHeight())
			itemHover.SetOverInEvent(ui.__mem_func__(self.__OnItemOverIn))
			itemHover.SetOverOutEvent(ui.__mem_func__(self.__OnItemOverOut))
			itemHover.Show()
			self.itemHover = itemHover

			# Attribute preview: a clip-masked viewport inside DescBg holding a
			# chrome-less ItemToolTip. No scrollbar - overflow scrolls by mouse wheel.
			vw = self.descBg.GetWidth() - 10
			vh = self.descBg.GetHeight() - 10
			self.attrViewW = vw
			self.attrViewH = vh

			viewport = ui.Window()
			viewport.SetParent(self.descBg)
			viewport.AddFlag("attach")
			viewport.SetPosition(5, 5)
			viewport.SetSize(vw, vh)
			viewport.Show()
			self.attrViewport = viewport

			scrollBoard = ui.Window()
			scrollBoard.SetParent(viewport)
			scrollBoard.AddFlag("attach")
			if app.USE_CLIP_MASK:
				scrollBoard.SetClippingMaskWindow(viewport)
			scrollBoard.SetPosition(0, 0)
			scrollBoard.SetSize(vw, vh)
			scrollBoard.Show()
			self.attrScrollBoard = scrollBoard

			attrTip = uitooltip.ItemToolTip(vw)
			attrTip.RemoveFlag("float")
			attrTip.SetFollow(False)
			if attrTip.Base:
				attrTip.Base.Hide()
			for piece in attrTip.Corners:
				piece.Hide()
			for piece in attrTip.Lines:
				piece.Hide()
			attrTip.SetParent(scrollBoard)
			attrTip.SetPosition(0, 0)
			if app.USE_CLIP_MASK:
				attrTip.SetClippingMaskWindow(viewport)
			attrTip.Show()
			self.attrTip = attrTip

			self.__BuildMaterialSlots()
			self.__BuildPityGauge()
			self.__UpdateChance()

		def __BuildPityGauge(self):
			# The pity bar shows a row of discrete pips built on demand from the server's max
			# (see __LayoutPity); here we only wire the hover icon's tooltip. Pip widgets are
			# pooled and created lazily the first time SetPittyInfo gives us a max.
			#
			# A plain uiscript image (CImageBox) does not fire mouse-over, so a ui.Window
			# hover catcher over the icon drives the tooltip (same pattern as the result-item
			# hover). Child of the icon => tracks the icon's uiscript position; padded a few
			# px so the tiny 15x14 icon is easy to hit.
			pad = 3
			hover = ui.Window()
			hover.SetParent(self.pityIcon)
			hover.SetPosition(-pad, -pad)
			hover.SetSize(self.pityIcon.GetWidth() + pad * 2, self.pityIcon.GetHeight() + pad * 2)
			hover.SetOverInEvent(ui.__mem_func__(self.__OnPityOverIn))
			hover.SetOverOutEvent(ui.__mem_func__(self.__OnPityOverOut))
			hover.Show()
			self.pityIconHover = hover

		def __EnsurePityPips(self, count):
			while len(self.pityEmptyPips) < count:
				empty = ui.ImageBox()
				empty.SetParent(self.pityBar)
				empty.LoadImage(NEW_REFINE_ASSET + "pitty_empty.png")
				empty.Hide()
				self.pityEmptyPips.append(empty)

				full = ui.ImageBox()
				full.SetParent(self.pityBar)
				full.LoadImage(NEW_REFINE_ASSET + "pitty_full.png")
				full.Hide()
				self.pityFullPips.append(full)

		def __LayoutPity(self, pittyMax, pittyCurrent):
			# Lay `pittyMax` pips contiguous + centred in the bar's track and light the first
			# `pittyCurrent` with the full overlay; pooled extras stay hidden.
			self.__EnsurePityPips(pittyMax)

			trackW = self.pityBar.GetWidth() - self.PITY_TRACK_L - self.PITY_TRACK_R
			rowW = pittyMax * self.PITY_PIP_W + max(0, pittyMax - 1) * self.PITY_PIP_GAP
			startX = self.PITY_TRACK_L + max(0, (trackW - rowW) // 2)
			fullDX = (self.PITY_PIP_W - self.PITY_FULL_W) // 2
			fullDY = (self.PITY_PIP_H - self.PITY_FULL_H) // 2

			for i in xrange(len(self.pityEmptyPips)):
				empty = self.pityEmptyPips[i]
				full = self.pityFullPips[i]
				if i < pittyMax:
					x = startX + i * (self.PITY_PIP_W + self.PITY_PIP_GAP)
					empty.SetPosition(x, self.PITY_PIP_TOP)
					empty.Show()
					full.SetPosition(x + fullDX, self.PITY_PIP_TOP + fullDY)
					if i < pittyCurrent:
						full.Show()
					else:
						full.Hide()
				else:
					empty.Hide()
					full.Hide()

		def __UpdateChance(self):
			# Label-only success indicator (no percentage): 'Guaranteed Success' when the
			# item is 100% or the pity is full, else 'May Fail'. Swap the two backgrounds.
			if not self.chanceText:
				return
			guaranteed = (self.percentage >= 100) or (self.pityMax > 0 and self.pityCurrent >= self.pityMax) or (self.type in self.GUARANTEED_REFINE_TYPES and self.refineBonus <= 0)
			if guaranteed:
				self.chanceBgFail.Hide()
				self.chanceBgSuccess.Show()
				self.chanceText.SetText(getattr(localeinfo, "REFINE_CHANCE_GUARANTEED", "Guaranteed Success"))
			else:
				self.chanceBgSuccess.Hide()
				self.chanceBgFail.Show()
				self.chanceText.SetText(getattr(localeinfo, "REFINE_CHANCE_MAY_FAIL", "May Fail"))

		def __BuildMaterialSlots(self):
			# A fixed row of MAT_MAX single-slot 32x32 SlotWindows. Empty = slot_locked.png;
			# a filled slot swaps to the native Slot_Base + SetItemSlot (real inventory
			# icon + count). Owned count sits on refine_count_bg below each slot.
			self.materialSlots = []
			self.materialVnums = [0] * self.MAT_MAX
			rowW = self.MAT_MAX * self.MAT_CELL + (self.MAT_MAX - 1) * self.MAT_GAP
			pad = max(0, (self.matPanel.GetWidth() - rowW) // 2)
			for i in xrange(self.MAT_MAX):
				cellX = pad + i * (self.MAT_CELL + self.MAT_GAP)
				slotX = cellX + (self.MAT_CELL - self.MAT_SLOT) // 2

				slot = ui.SlotWindow()
				slot.SetParent(self.matPanel)
				slot.SetPosition(slotX, self.MAT_TOP)
				slot.SetSize(self.MAT_SLOT, self.MAT_SLOT)
				slot.SetSlotBaseImage(NEW_REFINE_ASSET + "slot_locked.png", 1.0, 1.0, 1.0, 1.0)
				# Local slot index = material index i (each window holds one slot): the
				# over-in / unselect events report this index, so the handlers know which
				# material was hovered. Using 0 for every window made them all report slot 0.
				slot.AppendSlot(i, 0, 0, self.MAT_SLOT, self.MAT_SLOT)
				slot.SetOverInItemEvent(ui.__mem_func__(self.__OnMatOverIn))
				slot.SetOverOutItemEvent(ui.__mem_func__(self.__OnMatOverOut))
				slot.SetUnselectItemSlotEvent(ui.__mem_func__(self.__OnMatSearch))
				slot.RefreshSlot()
				slot.Show()

				countBg = ui.ExpandedImageBox()
				countBg.SetParent(self.matPanel)
				countBg.LoadImage(NEW_REFINE_ASSET + "refine_count_bg.png")
				countBg.SetPosition(cellX, self.MAT_TOP + self.MAT_SLOT + 4)
				countBg.Hide()

				haveText = ui.TextLine()
				haveText.SetParent(countBg)
				haveText.SetFontName(localeinfo.UI_DEF_FONT)
				haveText.SetOutline()
				haveText.SetWindowHorizontalAlignCenter()
				haveText.SetHorizontalAlignCenter()
				haveText.SetPosition(0, 4)
				haveText.Hide()

				self.materialSlots.append((slot, countBg, haveText))

		def Open(self, targetItemPos, nextGradeItemVnum, cost, prob, type, apply_random_list, src_vnum):
			if app.ENABLE_WINDOW_POSITION_SAVE:
				uiwindowpositions.ApplySavedPosition(self, "REFINE")

			self.__ResetMaterials()

			self.targetItemPos = targetItemPos
			self.vnum = nextGradeItemVnum
			self.cost = cost
			self.percentage = prob
			self.type = type
			self.apply_random_list = apply_random_list
			self.src_vnum = src_vnum

			self.metinSlot = []
			for i in xrange(player.METIN_SOCKET_MAX_NUM):
				self.metinSlot.append(player.GetItemMetinSocket(targetItemPos, i))
			self.attrSlot = []
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				self.attrSlot.append(player.GetItemAttribute(targetItemPos, i))

			item.SelectItem(nextGradeItemVnum)
			self.itemIcon.LoadImage(item.GetIconImageFileName())

			self.__BuildAttr()

			self.priceText.SetText(localeinfo.NumberToMoneyStringNoUnit(self.cost))
			self.__CenterPrice()
			self.bonusRow.Hide()

			self.pityCurrent = 0
			self.pityMax = 0
			self.refineBonus = 0
			self.__UpdateChance()

			# A keep-open refresh must NOT raise the window: the result popup (and the next
			# confirm) are opened around it and have to stay reachable on top.
			if self.refreshPending:
				self.refreshPending = False
			else:
				self.SetTop()

			self.Show()
			self.IsShow = True

		def __BuildAttr(self):
			self.attrTip.ClearToolTip()
			if app.ENABLE_APPLY_RANDOM:
				self.attrTip.AddRefineItemData(self.vnum, self.metinSlot, self.attrSlot, None, self.type, None, self.apply_random_list, 0)
			else:
				self.attrTip.AddRefineItemData(self.vnum, self.metinSlot, self.attrSlot, self.type)

			# AddRefineItemData may widen the tooltip past the viewport, which shifts
			# its centered text off to the right - recentre it on the viewport.
			xoff = (self.attrViewW - self.attrTip.GetWidth()) / 2
			self.attrTip.SetPosition(xoff, 0)

			contentH = self.attrTip.GetHeight()
			self.attrContentH = contentH
			self.attrScrollBoard.SetSize(self.attrViewW, max(contentH, self.attrViewH))
			self.attrScrollPos = 0
			self.attrScrollBoard.SetPosition(0, 0)
			self.attrOverflow = max(0, contentH - self.attrViewH)

		def OnRunMouseWheel(self, nLen):
			if self.attrOverflow <= 0 or not self.IsInPosition():
				return False
			if nLen > 0:
				self.attrScrollPos = max(0, self.attrScrollPos - self.ATTR_STEP)
			else:
				self.attrScrollPos = min(self.attrOverflow, self.attrScrollPos + self.ATTR_STEP)
			self.attrScrollBoard.SetPosition(0, -self.attrScrollPos)
			return True

		def __OnItemOverIn(self):
			if not self.vnum:
				return
			interface = systemSetting.GetInterfaceHandler()
			if not interface:
				return
			tip = getattr(interface, "tooltipItem", None)
			if not tip:
				return
			tip.ClearToolTip()
			# Normal item tooltip WITH metin stones (AddRefineItemData strips sockets).
			if app.ENABLE_APPLY_RANDOM:
				tip.AddItemData(self.vnum, self.metinSlot, self.attrSlot, apply_random_list = self.apply_random_list)
			else:
				tip.AddItemData(self.vnum, self.metinSlot, self.attrSlot)
			tip.ShowToolTip()

		def __OnItemOverOut(self):
			interface = systemSetting.GetInterfaceHandler()
			if not interface:
				return
			tip = getattr(interface, "tooltipItem", None)
			if tip:
				tip.HideToolTip()

		def AppendMaterial(self, vnum, count):
			if self.materialFilled >= self.MAT_MAX:
				return
			index = self.materialFilled
			slot, countBg, haveText = self.materialSlots[index]
			self.materialFilled += 1
			self.materialVnums[index] = vnum

			slot.SetSlotBaseImage(self.SLOT_BASE_IMAGE, 1.0, 1.0, 1.0, 1.0)
			slot.SetItemSlot(index, vnum, count)
			slot.RefreshSlot()

			have = player.GetItemCountByVnum(vnum)
			haveText.SetText(str(have))
			haveText.SetPackedFontColor(self.POSITIVE_COLOR if have >= count else self.NEGATIVE_COLOR)
			haveText.Show()
			countBg.Show()

		def __ResetMaterials(self):
			self.materialFilled = 0
			for i in xrange(self.MAT_MAX):
				self.materialVnums[i] = 0
				slot, countBg, haveText = self.materialSlots[i]
				slot.ClearSlot(i)
				slot.SetSlotBaseImage(NEW_REFINE_ASSET + "slot_locked.png", 1.0, 1.0, 1.0, 1.0)
				slot.RefreshSlot()
				haveText.Hide()
				countBg.Hide()

		def __OnMatOverIn(self, slotIndex):
			if slotIndex >= self.MAT_MAX:
				return
			vnum = self.materialVnums[slotIndex]
			if not vnum:
				return
			interface = systemSetting.GetInterfaceHandler()
			tip = getattr(interface, "tooltipItem", None) if interface else None
			if not tip:
				return
			tip.ClearToolTip()
			tip.AddItemData(vnum, 0)
			tip.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_WIKI_HOVER)
			tip.DeclareShortcut(("key_alt", "key_rclick"), localeinfo.TOOLTIP_QUICKSEARCH_OFFLINESHOP)
			tip.AlignHorizonalCenter()
			tip.ShowToolTip()

		def __OnMatOverOut(self):
			interface = systemSetting.GetInterfaceHandler()
			tip = getattr(interface, "tooltipItem", None) if interface else None
			if tip:
				tip.HideToolTip()

		def __OnMatSearch(self, slotIndex):
			if slotIndex >= self.MAT_MAX:
				return
			vnum = self.materialVnums[slotIndex]
			if not vnum:
				return

			if app.IsPressed(app.DIK_LSHIFT):
				if self.wndWiki:
					if not self.wndWiki.IsShow():
						net.ToggleWikiWindow()
					self.wndWiki.CloseBaseWindows()
					self.wndWiki.OpenSpecialPage(None, vnum, False)

			if app.USE_OFFLINESHOP and\
				not uiofflineshop_ae.IsBuildingShop() and\
				(app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT)):
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler:
					wndShopOffline = interfaceHandler.wndShopOffline
					if wndShopOffline:
						wndSearchShop = wndShopOffline.wndSearchShop
						if wndSearchShop:
							wndSearchShop.SearchByName(item.GetItemNameByVnum(vnum))

		def __OnPityOverIn(self):
			interface = systemSetting.GetInterfaceHandler()
			tip = getattr(interface, "tooltipItem", None) if interface else None
			if not tip:
				return
			tip.ClearToolTip()
			tip.SetCannotUseItemForceSetDisableColor(False)
			tip.SetTitle(localeinfo.PITTY_REFINE_TITLE)
			tip.AppendSpace(7)
			tip.AppendDescription(localeinfo.PITTY_REFINE_DEC1 + localeinfo.PITTY_REFINE_DEC2, 26, self.PITY_FILLED_COLOR)
			tip.AppendHorizontalLine()
			tip.AppendDescription(localeinfo.PITTY_REFINE_DEC3 + localeinfo.PITTY_REFINE_DEC4, 26, self.PITY_FILLED_COLOR)
			tip.ShowToolTip()

		def __OnPityOverOut(self):
			interface = systemSetting.GetInterfaceHandler()
			tip = getattr(interface, "tooltipItem", None) if interface else None
			if tip:
				tip.HideToolTip()

		def SetPittyInfo(self, forVnum, pittyCurrent, pittyMax):
			# Server pushes pity state for the item in the slot. Show `pittyMax` pips and
			# light `pittyCurrent`; clear them when it does not match or the item has no pity.
			if not self.pityBar:
				return
			if pittyMax <= 0 or player.GetItemIndex(self.targetItemPos) != forVnum:
				self.pityCurrent = 0
				self.pityMax = 0
				self.__LayoutPity(0, 0)
				self.__UpdateChance()
				return
			self.pityCurrent = pittyCurrent
			self.pityMax = pittyMax
			self.__LayoutPity(pittyMax, pittyCurrent)
			self.__UpdateChance()

		def SetRefineBonus(self, prob):
			# Server pushes the scroll's success-chance bonus (welly extraProb). Show the
			# row only when there is a bonus; the base packet folds it into the total prob.
			if not self.bonusRow:
				return
			self.refineBonus = prob if prob > 0 else 0
			if prob <= 0:
				self.bonusRow.Hide()
			else:
				self.bonusText.SetText(getattr(localeinfo, "REFINE_PROB_BONUS", "+%d%% Success Chance") % prob)
				self.bonusRow.Show()
			self.__UpdateChance()

		if app.ENABLE_AUTO_REFINE:
			def CheckRefine(self, isFail):
				# Refine result push. Without keep-open the window just closes, as before.
				if not self.keepOpen:
					self.Close()
					return

				self.__RefreshAfterRefine()

			def __RefreshAfterRefine(self):
				# The window renders the payload the server pushed when it OPENED, so with
				# keep-open ticked it keeps showing the grade it was opened with. There is no
				# refresh packet in this protocol: re-issue the action that opened the window
				# and the server answers with fresh refine info (exactly how the auto-refine
				# loop refreshes). Neither packet refines by itself - only SendRefinePacket does.
				# osfinfo.AUTO_REFINE_DATA is filled on every open by uiinventory (scroll on item)
				# and game.py __PutItem (item given to the smith), auto-refine on or off.
				if 1 == osfinfo.AUTO_REFINE_TYPE:
					scrollPos = osfinfo.AUTO_REFINE_DATA["ITEM"][0]
					targetPos = osfinfo.AUTO_REFINE_DATA["ITEM"][1]
					if -1 == scrollPos or -1 == targetPos:
						return

					targetIndex = player.GetItemIndex(targetPos)
					# item destroyed / scroll used up / already at max grade -> nothing to show
					if targetIndex <= 0 or player.GetItemIndex(scrollPos) <= 0 or 9 == targetIndex % 10:
						self.Close()
						return

					self.refreshPending = True
					net.SendItemUseToItemPacket(scrollPos, targetPos)

				elif 2 == osfinfo.AUTO_REFINE_TYPE:
					npcData = osfinfo.AUTO_REFINE_DATA["NPC"]
					if 0 == npcData[0] or -1 == npcData[1] or -1 == npcData[2] or 0 == npcData[3]:
						return

					targetIndex = player.GetItemIndex(npcData[1], npcData[2])
					if targetIndex <= 0 or 9 == targetIndex % 10:
						self.Close()
						return

					self.refreshPending = True
					net.SendGiveItemPacket(npcData[0], npcData[1], npcData[2], npcData[3])

		def __CenterPrice(self):
			# Centre the yang icon + price number as one cluster in the price row.
			if not self.priceText or not self.yangIcon:
				return
			textW = self.priceText.GetTextWidth()
			clusterW = self.PRICE_YANG_W + self.PRICE_YANG_GAP + textW
			startX = max(0, (self.PRICE_ROW_W - clusterW) // 2)
			self.yangIcon.SetPosition(startX, self.PRICE_YANG_Y)
			self.priceText.SetPosition(startX + self.PRICE_YANG_W + self.PRICE_YANG_GAP, self.PRICE_TEXT_Y)

		def __OnToggleKeepOpen(self):
			# Keep-open is a manual image-swap toggle (ui.CheckBox is broken here); the
			# custom art is check_unselect / checkbox_select. When set, Accept leaves the
			# window open after a refine.
			self.keepOpen = not self.keepOpen
			img = NEW_REFINE_ASSET + ("checkbox_select.png" if self.keepOpen else "check_unselect.png")
			self.keepChk.SetUpVisual(img)
			self.keepChk.SetOverVisual(img)
			self.keepChk.SetDownVisual(img)

		def __GetRecommendItem(self):
			# Guarantee-item suggestion for the OK confirm: only when the shown chance
			# is < 100 and the item's refine grade falls in a REFINE_RECOMMEND_MAP band.
			if self.percentage >= 100:
				return 0
			grade = player.GetItemGrade(self.targetItemPos)
			for lo, hi, vnum in self.REFINE_RECOMMEND_MAP:
				if lo <= grade <= hi:
					return vnum
			return 0

		def __WarningTexts(self):
			# The two confirm lines the stock QuestionDialog2 path would show, so the
			# recommend popup carries the identical destroy/downgrade wording.
			if 3 == self.type:
				return (localeinfo.REFINE_DESTROY_WARNING_WITH_BONUS_PERCENT_1,
					localeinfo.REFINE_DESTROY_WARNING_WITH_BONUS_PERCENT_2)
			if 2 == self.type:
				return (localeinfo.REFINE_DOWN_GRADE_WARNING, localeinfo.REFINE_WARNING2)
			return (localeinfo.REFINE_DESTROY_WARNING, localeinfo.REFINE_WARNING2)

		def OpenQuestionDialog(self):
			# OK button. No confirm when the refine cannot lose the item (100% / guaranteed
			# scroll / bless / soul / welly); otherwise warn per type before sending.
			if 100 == self.percentage:
				self.Accept()
				return
			if self.type in self.GUARANTEED_REFINE_TYPES:
				self.Accept()
				return
			if app.ENABLE_STONE_OF_BLESS and 7 == self.type:
				self.Accept()
				return
			if app.ENABLE_SOUL_SYSTEM and (8 == self.type or 9 == self.type):
				self.Accept()
				return
			if app.NEW_WELLY_UPGRADE_STONES and (10 == self.type or 11 == self.type or 12 == self.type):
				self.Accept()
				return

			recVnum = self.__GetRecommendItem()
			if recVnum and not (3 == self.type and localeinfo.IsEUROPE()):
				line1, line2 = self.__WarningTexts()
				dlg = RefineRecommendConfirm()
				dlg.Setup(line1, line2, recVnum, ui.__mem_func__(self.Accept))
				dlg.Open()
				self.dlgQuestion = dlg
				return

			dlgQuestion = uicommon.QuestionDialog2()
			dlgQuestion.SetText2(localeinfo.REFINE_WARNING2)
			dlgQuestion.SetAcceptEvent(ui.__mem_func__(self.Accept))
			dlgQuestion.SetCancelEvent(ui.__mem_func__(dlgQuestion.Close))
			if 3 == self.type:
				if localeinfo.IsEUROPE():
					dlgQuestion = uicommon.QuestionDialog()
					dlgQuestion.SetAcceptEvent(ui.__mem_func__(self.Accept))
					dlgQuestion.SetCancelEvent(ui.__mem_func__(dlgQuestion.Close))
					dlgQuestion.SetText(localeinfo.REFINE_DESTROY_WARNING_WITH_BONUS_PERCENT_1)
				else:
					dlgQuestion.SetText1(localeinfo.REFINE_DESTROY_WARNING_WITH_BONUS_PERCENT_1)
					dlgQuestion.SetText2(localeinfo.REFINE_DESTROY_WARNING_WITH_BONUS_PERCENT_2)
			elif 2 == self.type:
				dlgQuestion.SetText1(localeinfo.REFINE_DOWN_GRADE_WARNING)
			else:
				dlgQuestion.SetText1(localeinfo.REFINE_DESTROY_WARNING)
			dlgQuestion.Open()
			self.dlgQuestion = dlgQuestion

		def Accept(self):
			net.SendRefinePacket(self.targetItemPos, self.type)
			if self.dlgQuestion:
				self.dlgQuestion.Close()
			if not self.keepOpen:
				self.Close()

		def CancelRefine(self):
			net.SendRefinePacket(255, 255)
			self.Close()

		def Close(self):
			if app.ENABLE_WINDOW_POSITION_SAVE:
				uiwindowpositions.SaveOnClose(self, "REFINE")
			# Unlock the greyed source slot on EVERY close path (cancel, ESC, and the
			# auto-refine CheckRefine->Close), else OnUpdate leaves it locked while hidden.
			if app.WJ_ENABLE_TRADABLE_ICON and self.targetItemPos:
				self.SetCanMouseEventSlot(self.targetItemPos)
			self.targetItemPos = 0
			self.__OnItemOverOut()
			self.dlgQuestion = None
			self.refreshPending = False
			self.Hide()
			self.IsShow = False

		def OnMoveWindow(self, x, y):
			if app.ENABLE_WINDOW_POSITION_SAVE:
				uiwindowpositions.OnWindowMove("REFINE", x, y)

		def OnPressEscapeKey(self):
			self.CancelRefine()
			return True

		def IsShow(self):
			return self.IsShow

		def Destroy(self):
			self.ClearDictionary()
			if app.WJ_ENABLE_TRADABLE_ICON:
				self.interface = None
				self.inven = None
			self.board = None
			self.header1Text = None
			self.header2Text = None
			self.itemPanel = None
			self.itemSlotBg = None
			self.descBg = None
			self.itemIcon = None
			self.itemHover = None
			self.attrViewport = None
			self.attrScrollBoard = None
			self.attrTip = None
			self.matPanel = None
			self.pityBar = None
			self.pityIcon = None
			self.pityIconHover = None
			self.pityEmptyPips = []
			self.pityFullPips = []
			self.chanceBgSuccess = None
			self.chanceBgFail = None
			self.chanceText = None
			self.okButton = None
			self.cancelButton = None
			self.dlgQuestion = None
			self.keepChk = None
			self.priceText = None
			self.yangIcon = None
			self.bonusRow = None
			self.bonusText = None
			self.materialSlots = []
			self.materialVnums = []
			self.wndWiki = None
			self.IsShow = False

		if app.WJ_ENABLE_TRADABLE_ICON:
			def BindInterface(self, interface):
				if interface:
					self.interface = proxy(interface)

			def SetInven(self, inven):
				if inven:
					self.inven = proxy(inven)

			def SetCanMouseEventSlot(self, idx):
				if not self.inven:
					return
				if idx >= INVENTORY_PAGE_SIZE:
					page = self.inven.GetInventoryPageIndex()
					idx -= (page * INVENTORY_PAGE_SIZE)
				self.inven.wndItem.SetCanMouseEventSlot(idx)

			def OnUpdate(self):
				if not self.inven:
					return
				targetItemPos = self.targetItemPos
				if targetItemPos <= 0:
					return
				page = self.inven.GetInventoryPageIndex()
				if (page * INVENTORY_PAGE_SIZE) <= targetItemPos < ((page + 1) * INVENTORY_PAGE_SIZE):
					lock_idx = targetItemPos - (page * INVENTORY_PAGE_SIZE)
					self.inven.wndItem.SetCantMouseEventSlot(lock_idx)
