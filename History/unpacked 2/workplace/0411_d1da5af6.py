# coding: latin_1

#
# Title: Custom Select Attributes
# Description: Allows your character to add all any bonus they want.
# Author: Owsap
# Last Date: 2021.11.24 (YMD)
#
# Skype: owsap.
# Discord: Owsap#7928
#
# Web: https://owsap.dev/
# GitHub: https://github.com/Owsap
#
# 0x0
#

__author__ = "Owsap"
__copyright__ = "Copyright 2021, Owsap"

import app
import mousemodule
import ui
import uicommon
import uitooltip
import item
import player
import net
import localeinfo
import constinfo

from _weakref import proxy

ROOT = "d:/ymir work/ui/game/setcustomattribute/"

def GetAffectString(affectType, affectValue):
	if not affectType:
		return None

	try:
		return uitooltip.ItemToolTip().AFFECT_DICT[affectType](affectValue)
	except TypeError:
		return "UNKNOWN_VALUE[%s] %s" % (affectType, affectValue)
	except KeyError:
		return "UNKNOWN_TYPE[%s] %s" % (affectType, affectValue)

class SetCustomAttributeWindow(ui.ScriptWindow):

	ATTR_MAX_SLOT_NUM = 5
	ATTR_TOOLTIP_LIST = [
		localeinfo.ATTR_TOOLTIP_LIST_1
	]

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.isLoaded = False

		## Target Item Related
		self.itemSlot = None
		self.itemCellPos = -1
		self.itemToolTip = None
		self.isAttached = False

		## Attribute Related
		self.attrDataList = []
		self.attrIndex = [ -1 for i in range(self.ATTR_MAX_SLOT_NUM) ]
		self.attrProb = 0

		## Board Related
		self.attrSlotText = []
		self.attrSlotTextPreviousBtn = []
		self.attrSlotTextNextBtn = []

		self.questionDialog = None
		self.toolTip = None
		self.interface = None
		self.inven = None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.interface = None
		self.inven = None
		self.toolTip = None

		self.ClearDictionary()

		self.isLoaded = False

		## Target Item Related
		self.itemSlot = None
		self.itemCellPos = -1
		self.itemToolTip = None
		self.isAttached = False

		## Attribute Related
		self.attrDataList = []
		self.attrIndex = [ -1 for i in range(self.ATTR_MAX_SLOT_NUM) ]
		self.attrProb = 0

		## Board Related
		self.attrSlotText = []
		self.attrSlotTextPreviousBtn = []
		self.attrSlotTextNextBtn = []

		self.questionDialog = None

	def SetItemToolTip(self, tooltip):
		if tooltip:
			self.itemToolTip = proxy(tooltip)

	def BindInterface(self, interface):
		if interface:
			self.interface = proxy(interface)

	def SetInven(self, inven):
		if inven:
			self.inven = proxy(inven)

	def __LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/SetCustomAttributeWindow.py")
		except:
			import exception
			exception.Abort("CustomSelectAttrWindow.LoadWindow.LoadScriptFile")

		try:
			self.__BindObject()
		except:
			import exception
			exception.Abort("CustomSelectAttrWindow.LoadWindow.BindObject")

		try:
			self.__BindEvent()
		except:
			import exception
			exception.Abort("CustomSelectAttrWindow.LoadWindow.BindEvent")

	## Bind Objects
	def __BindObject(self):
		## Board Image
		self.boardImage = self.GetChild("BoardImage")

		## Item Slot
		self.itemSlot = self.GetChild("ItemSlot")

		## Enchantment Probability
		self.enchantProbText = self.GetChild("EnchantProbabilityText")

		## Attribute Slots
		for slotIndex in range(self.ATTR_MAX_SLOT_NUM):
			self.attrSlotText.append(self.GetChild("AttrSlotText%d" % (slotIndex + 1)))
			self.attrSlotTextPreviousBtn.append(self.GetChild("AttrSlotText%dPrevious" % (slotIndex + 1)))
			self.attrSlotTextNextBtn.append(self.GetChild("AttrSlotText%dNext" % (slotIndex + 1)))

		## Enchant Button
		self.enchantButton = self.GetChild("EnchantButton")
		self.enchantButton.Disable()
		self.enchantButton.Down()

	## Bind Events
	def __BindEvent(self):
		## Board
		self.GetChild("Board").SetCloseEvent(ui.__mem_func__(self.Close))

		## Item Slot
		if self.itemSlot:
			self.itemSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInItemSlot))
			self.itemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItemSlot))

		## Attribute Slots
		for slotIndex in range(self.ATTR_MAX_SLOT_NUM):
			self.attrSlotText[slotIndex].SetText("---")
			self.attrSlotTextPreviousBtn[slotIndex].SetEvent(ui.__mem_func__(self.__OnClickPreviousAttr), slotIndex)
			self.attrSlotTextNextBtn[slotIndex].SetEvent(ui.__mem_func__(self.__OnClickNextAttr), slotIndex)

		## Enchant Button
		if self.enchantButton:
			self.enchantButton.SetEvent(ui.__mem_func__(self.__OnClickEnchantButton))

		## ToolTip
		self.toolTipButton = self.GetChild("ToolTipButton")
		self.toolTip = self.__CreateGameTypeToolTip(localeinfo.ATTR_TOOLTIP_LIST_TITLE, self.ATTR_TOOLTIP_LIST)
		self.toolTip.SetTop()
		self.toolTipButton.SetToolTipWindow(self.toolTip)

	## Game Type ToolTip
	def __CreateGameTypeToolTip(self, title, descList):
		toolTip = uitooltip.ToolTip()
		toolTip.SetTitle(title)
		toolTip.AppendSpace(7)

		for desc in descList:
			toolTip.AutoAppendTextLine(desc)

		toolTip.AlignHorizonalCenter()
		toolTip.SetTop()
		return toolTip

	## Check enchant requirements
	def CanEnchantItem(self):
		# Check attached item.
		if not self.itemIsAttached:
			return False

		# Check attached item cell.
		if self.itemCellPos < 0 or self.itemCellPos >= player.ITEM_SLOT_COUNT:
			return False

		# Check item attribute list.
		if not self.attrDataList:
			return False

		return True

	## Check selected attribute
	def HasSelectedAttrPreviously(self, slotIndex):
		count = 0
		for index in self.attrIndex:
			if index == self.attrIndex[slotIndex]:
				count += 1

		if count > 1:
			return True

		return False

	## Previous Attribute (Button)
	def __OnClickPreviousAttr(self, slotIndex):
		if not self.CanEnchantItem():
			return

		self.attrIndex[slotIndex] -= 1
		if self.attrIndex[slotIndex] < 0:
			self.attrIndex[slotIndex] = len(self.attrDataList) - 1

		## (Previous) Pagination Control
		# We don't want to select attributes previously selected.
		# This control function will skip an attribute that has
		# already been selected before in other fields.
		if self.HasSelectedAttrPreviously(slotIndex):
			self.__OnClickPreviousAttr(slotIndex)
			return

		if self.attrSlotText:
			self.attrSlotText[slotIndex].SetText(GetAffectString(self.attrDataList[self.attrIndex[slotIndex]][0], self.attrDataList[self.attrIndex[slotIndex]][1]))

	## Next Attribute (Button)
	def __OnClickNextAttr(self, slotIndex):
		if not self.CanEnchantItem():
			return

		self.attrIndex[slotIndex] += 1
		if self.attrIndex[slotIndex] >= len(self.attrDataList):
			self.attrIndex[slotIndex] = 0

		## (Next) Pagination Control
		# We don't want to select attributes previously selected.
		# This control function will skip an attribute that has
		# already been selected before in other fields.
		if self.HasSelectedAttrPreviously(slotIndex):
			self.__OnClickNextAttr(slotIndex)
			return

		if self.attrSlotText:
			self.attrSlotText[slotIndex].SetText(GetAffectString(self.attrDataList[self.attrIndex[slotIndex]][0], self.attrDataList[self.attrIndex[slotIndex]][1]))

	## OnClick Enchantment Button
	def __OnClickEnchantButton(self):
		if not self.CanEnchantItem():
			return

		questionDialog = uicommon.QuestionDialog()
		questionDialog.SetText(localeinfo.ATTR_ENCHANT_DIALOG_QUESTION)
		questionDialog.SetAcceptEvent(ui.__mem_func__(self.__OnQuestionPopupAccept))
		questionDialog.SetCancelEvent(ui.__mem_func__(self.__OnQuestionPopupCancel))
		questionDialog.Open()
		self.questionDialog = questionDialog

	## OnQuestion PopupAccept
	def __OnQuestionPopupAccept(self):
		if not self.questionDialog:
			return

		if not self.CanEnchantItem():
			return

		applyNumList = []
		for slotIndex in range(self.ATTR_MAX_SLOT_NUM):
			applyNumList.append(self.attrDataList[self.attrIndex[slotIndex]][0])

		if applyNumList:
			net.SendSetCustomAttribute(player.INVENTORY, self.itemCellPos, applyNumList)

		self.__OnQuestionPopupCancel()
		self.Close()

	## OnQuestion PopupCancel
	def __OnQuestionPopupCancel(self):
		if self.questionDialog:
			self.questionDialog.Close()
			self.questionDialog = None

	## Refresh AttributeSet Data
	def RefreshAttrSet(self, itemCellPos, attrEnchantProb, attrDataList):
		self.itemCellPos = itemCellPos
		self.attrEnchantProb = attrEnchantProb
		self.attrDataList = attrDataList

		itemVNum = player.GetItemIndex(itemCellPos)
		item.SelectItem(itemVNum)

		if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
			return

		# Set custom board image.
		if self.boardImage:
			if attrEnchantProb >= 100:
				self.boardImage.LoadImage(ROOT + "background2pct.png")
			else:
				self.boardImage.LoadImage(ROOT + "backgroundpct.png")

		# Set enchantment probability.
		if self.enchantProbText:
			self.enchantProbText.SetText("%d%%" % attrEnchantProb)

		# Set attached item slot.
		if self.itemSlot:
			self.itemSlot.SetItemSlot(0, itemVNum)
			self.itemSlot.RefreshSlot()
			self.itemIsAttached = True

		# Enable enchant button.
		if self.enchantButton:
			self.enchantButton.Enable()

		# Set first pagination.
		for slotIndex in range(self.ATTR_MAX_SLOT_NUM):
			self.__OnClickNextAttr(slotIndex)

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def OverInItemSlot(self, slotIndex):
		if self.itemToolTip and self.itemCellPos >= 0:
			self.itemToolTip.SetInventoryItem(self.itemCellPos)

	def OverOutItemSlot(self):
		if self.itemToolTip:
			self.itemToolTip.HideToolTip()

	def __ClearData(self):
		# Clear item slot.
		self.__ClearItemSlot()

		# Clear attribute related.
		self.attrDataList = []
		self.attrIndex = [ -1 for i in range(self.ATTR_MAX_SLOT_NUM) ]
		self.attrEnchantProb = 0

		if self.attrSlotText:
			for slotIndex in range(self.ATTR_MAX_SLOT_NUM):
				self.attrSlotText[slotIndex].SetText("---")

	## Clear Item Slot
	def __ClearItemSlot(self):
		self.itemCellPos = -1
		self.itemIsAttached = False

		if self.itemSlot:
			for slotIndex in xrange(self.itemSlot.GetSlotCount()):
				self.itemSlot.ClearSlot(slotIndex)
			self.itemSlot.RefreshSlot()

	def Open(self, itemCellPos = 0, attrEnchantProb = 0, attrDataList = []):
		if self.isLoaded != True:
			self.isLoaded = True
			self.__LoadWindow()
			self.SetCenterPosition()

		self.__ClearData()
		self.RefreshAttrSet(itemCellPos, attrEnchantProb, attrDataList)

		self.SetTop()
		ui.ScriptWindow.Show(self)

	def Close(self):
		if self.itemToolTip:
			self.itemToolTip.HideToolTip()

		if self.questionDialog:
			self.questionDialog.Close()

		constinfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

		self.Hide()
