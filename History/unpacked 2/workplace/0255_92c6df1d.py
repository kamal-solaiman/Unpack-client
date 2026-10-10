# coding: latin_1

import app
import chat
import net
import item
import player

import ui
import constinfo
import mousemodule
import uiprivateshopbuilder
import uicommon
import uitooltip
import localeinfo

if app.ENABLE_GEAR_SETS:
	GEARSET_REQUEST = 0
	GEARSET_SAVE = 1
	GEARSET_EQUIP = 2
	GEARSET_RENAME = 3
	GEARSET_ASSIGN_DUNGEON = 4
	GEARSET_CLEAR = 5
	GEARSET_GIVE_TOKEN = 6
	GEARSET_LINK = 7
	GEARSET_UNLINK = 8

	# Curated dungeon list for per-set auto-equip. Each entry = (display name, base map index).
	# The map index is dungeon_info.json "mapIndex" and is what the server matches on dungeon entry.
	# Edit this list to add / remove / rename dungeons (first entry must stay "None" with id 0).
	GEARSET_DUNGEONS = (
		(localeinfo.GEARSET_DUN_NONE,     0),
		(localeinfo.GEARSET_DUN_ORC,      29),
		(localeinfo.GEARSET_DUN_MONKEY,   30),
		(localeinfo.GEARSET_DUN_DT,       66),
		(localeinfo.GEARSET_DUN_SPIDER,   218),
		(localeinfo.GEARSET_DUN_CATACOMB, 216),
		(localeinfo.GEARSET_DUN_DRAGON,   208),
		(localeinfo.GEARSET_DUN_DRAGON_GHOST,  221),
		(localeinfo.GEARSET_DUN_NEMERE,   352),
		(localeinfo.GEARSET_DUN_FLAME,    351),
		# >>> retired with dungeon-list prune 2026-08-04 (docs/MONKEY_DUNGEON.md) (disabled)
		# (localeinfo.GEARSET_DUN_EREBUS,   353),
		# (localeinfo.GEARSET_DUN_MELEY,    212),
		# (localeinfo.GEARSET_DUN_AZRAEL,   372),
		# <<< end retired
	)

PATCH_DESIGN = "d:/ymir work/ui/fast_equip/"
ART = "d:/ymir work/ui/game/new_fast_equip/"   # new_fast_equip skin (gear sets redesign)


# Left-aligned list rows (mirrors uiadvancedgameoptions.ResolutionListBox - the stock ListBox
# right-shifts every row by textWidth under Arabic, which scrambles the alignment).
class GearSetDungeonListBox(ui.ListBox):
	def __init__(self, layer = "UI"):
		ui.ListBox.__init__(self, layer)
		self.SetTextCenterAlign(False)

	def InsertItem(self, number, text, textColor = 0x00000000):
		self.keyDict[len(self.itemList)] = number
		self.textDict[len(self.itemList)] = text
		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetText(text)
		textLine.SetWindowHorizontalAlignLeft()
		textLine.SetHorizontalAlignLeft()
		textLine.SetOutline()
		textLine.Hide()
		self.itemList.append(textLine)
		self._LocateItem()

	def _LocateItem(self):
		yPos = 0
		self.showLineCount = 0
		skipCount = self.basePos
		for textLine in self.itemList:
			textLine.Hide()
			if skipCount > 0:
				skipCount -= 1
				continue
			# RTL: anchor the text at the right edge and keep SetHorizontalAlignLeft so Arabic
			# glyphs flow leftward (alignment unchanged - only the x position moves right).
			textLine.SetPosition(self.GetWidth() - 6, yPos - 2)
			yPos += self.stepSize
			if yPos <= self.GetHeight():
				self.showLineCount += 1
				textLine.Show()


# Compact dungeon dropdown styled after uiadvancedgameoptions.ResolutionSelector: collapsed box =
# select_image.tga scaled narrower + click-to-toggle popup (ThinBoard + opaque fill + left-aligned
# list) hung on a top board so it renders unclipped. No scrollbar (the curated list is short).
class GearSetDungeonSelector(ui.Window):
	ROW_HEIGHT     = 16
	BOX_WIDTH      = 140        # tune here to resize the box
	IMAGE_NATIVE_W = 195        # select_image.tga native width
	BOX_IMAGE      = "d:/ymir work/ui/pattern/select_image.tga"

	def __init__(self, topBoard, parentWnd, x, y):
		ui.Window.__init__(self)
		self.topBoard = topBoard
		self.items = []
		self.selectEvent = None
		self.isOpen = False
		self.SetParent(parentWnd)
		self.SetPosition(x, y)
		self.__BuildBox()
		self.__BuildPopup(topBoard)
		self.Show()

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.selectEvent = None
		self.items = []
		self.topBoard = None

	def __BuildBox(self):
		img = ui.ExpandedImageBox()
		img.SetParent(self)
		img.AddFlag("not_pick")
		img.LoadImage(self.BOX_IMAGE)
		img.SetScale(float(self.BOX_WIDTH) / float(self.IMAGE_NATIVE_W), 1.0)
		img.SetPosition(0, 0)
		img.Show()
		self.boxImage = img
		self.SetSize(self.BOX_WIDTH, self.ROW_HEIGHT)

		boxText = ui.TextLine()
		boxText.SetParent(self)
		boxText.AddFlag("not_pick")
		# RTL: anchor at the right edge (alignment stays Left so Arabic flows leftward).
		# Y centers the glyphs in the 16px-tall select_image box (was 2 -> text sat at the top).
		boxText.SetPosition(self.BOX_WIDTH - 16, 0)
		boxText.SetHorizontalAlignLeft()
		boxText.SetOutline()
		boxText.Show()
		self.boxText = boxText

	def __BuildPopup(self, topBoard):
		popup = ui.Window()
		popup.SetParent(topBoard)
		popup.Hide()
		self.popup = popup

		board = ui.ThinBoard()
		board.SetParent(popup)
		board.SetPosition(0, 0)
		board.Show()
		self.board = board

		fill = ui.Bar()
		fill.SetParent(popup)
		fill.SetPosition(3, 3)
		fill.SetColor(0xff000000)
		fill.Show()
		self.fill = fill

		listBox = GearSetDungeonListBox()
		listBox.SetParent(popup)
		listBox.SetPosition(6, 5)
		listBox.SetPickAlways()
		listBox.SetEvent(ui.__mem_func__(self.__OnSelectItem))
		listBox.Show()
		self.listBox = listBox

	def OnMouseLeftButtonUp(self):
		self.__ToggleOpen()
		return True

	def SetSelectEvent(self, event):
		self.selectEvent = event

	def SetItems(self, names):
		self.items = names
		self.listBox.ClearItem()
		for i in xrange(len(names)):
			self.listBox.InsertItem(i, names[i])
		rows = len(names) if len(names) > 0 else 1
		listH = rows * self.ROW_HEIGHT
		popupW = self.BOX_WIDTH
		self.listBox.SetSize(popupW - 12, listH)
		self.listBox.SetBasePos(0)
		popupH = listH + 8
		self.popup.SetSize(popupW, popupH)
		self.board.SetSize(popupW, popupH)
		self.fill.SetSize(popupW - 6, popupH - 6)

	def SetCurrentText(self, text):
		self.boxText.SetText(text)

	def __ToggleOpen(self):
		if self.isOpen:
			self.Close()
		else:
			self.Open()

	def Open(self):
		if len(self.items) == 0:
			return
		(bx, by) = self.GetGlobalPosition()
		(tx, ty) = self.topBoard.GetGlobalPosition()
		self.popup.SetPosition(bx - tx, by - ty + self.GetHeight())
		self.popup.Show()
		self.popup.SetTop()
		self.isOpen = True

	def Close(self):
		self.popup.Hide()
		self.isOpen = False

	def __OnSelectItem(self, index, name):
		self.Close()
		if index < 0 or index >= len(self.items):
			return
		self.boxText.SetText(self.items[index])
		if self.selectEvent:
			self.selectEvent(index)


class UiFastEquip(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)

		self.toolTip = uitooltip.ItemToolTip()

		self.index_presets = 0
		self.equipament = None
		self.thinboard_presets = None
		self.title_bar_s = None
		self.Change_Equipament = None
		self.getTokenButton = None
		self.dungeonCombo = None
		self.dungeonLabel = None
		self.name_presets = None

		self.elements = {}
		self.elements["max_presets_view"] = 8
		self.elements["max_presets_count"] = player.CHANGE_EQUIP_PAGE_EXTRA
		self.elements["scrollbar_pos"] = 1
		self.elements["select_presets"] = -1

		for i in xrange(0, self.elements["max_presets_count"]):
			self.elements["presets_name%d" % i] = localeinfo.FAST_EQUIPMENT_PAGE % (localeinfo.NumberToRoman(i + 1))

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		if self.name_presets:
			self.name_presets.Close()
			del self.name_presets
			self.name_presets = None

		if self.equipament:
			self.equipament = None

		if self.thinboard_presets:
			self.thinboard_presets = None

		if self.title_bar_s:
			self.title_bar_s = None

		if self.Change_Equipament:
			self.Change_Equipament = None

		if self.getTokenButton:
			self.getTokenButton = None

		if self.dungeonCombo:
			self.dungeonCombo = None

		if self.dungeonLabel:
			self.dungeonLabel = None

		for i in xrange(0, self.elements["max_presets_view"]):
			for prefix in ("slot_presets%d", "slot_presets_name%d", "button_rename_%d"):
				key = prefix % i
				if self.elements.has_key(key):
					del self.elements[key]
					self.elements[key] = None

		key = "scrollbar"
		if self.elements.has_key(key):
			del self.elements[key]
			self.elements[key] = None

		self.elements = {}
		self.ClearDictionary()

	def LoadPresets(self):
		myPath = "UserData\\fast_equip"

		import os
		if not os.path.exists(os.getcwd() + os.sep + myPath):
			return

		filePath = myPath + "\\" + player.GetName() + ".data"
		if os.path.isfile(filePath):
			with old_open(filePath, "rb") as myFile:
				try:
					myContent = app.DecryptLocal(myFile.read())
				except WindowsError:
					return

				myLines = myContent.split("\n")
				for l in myLines:
					myKeyValue = l.split("\t")
					if len(myKeyValue) == 2:
						try:
							k = "presets_name%d" % int(myKeyValue[0])
							self.elements[k] = myKeyValue[1]
						except:
							pass

			myFile.close()

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/fastequip_windows.py")
		except:
			import exception
			exception.Abort("UiFastEquip.LoadWindow.LoadObject")

		try:
			self.equipament 		= self.GetChild2("Equipament")
			self.thinboard_presets 	= self.GetChild2("thinboard_presets")
			self.Change_Equipament  = self.GetChild2("Change_Equipament")
			self.getTokenButton     = self.GetChild2("GetTokenButton")
			self.titleBar = self.GetChild2("TitleBar")
		except:
			import exception
			exception.Abort("UiFastEquip.LoadWindow.LoadElements")

		self.LoadPresets()
		self.PresetsElements()
		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))
		self.Change_Equipament.SetEvent(ui.__mem_func__(self.ClickChangeEquip))
		self.getTokenButton.SetEvent(ui.__mem_func__(self.ClickGetToken))
		if app.ENABLE_GEAR_SETS:
			self.MakeDungeonCombo()
		self.equipament.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		self.equipament.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		self.equipament.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		self.equipament.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		self.equipament.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

	def PresetsElements(self):
		# >>> SECTION BEGIN: legacy draggable scrollbar (replaced by mousewheel paging, OnMouseWheel) <<<
		# self.elements["scrollbar"] = ScrollBarNew()
		# self.elements["scrollbar"].SetParent(self.thinboard_presets)
		# self.elements["scrollbar"].SetPosition(173,24)
		# self.elements["scrollbar"].SetScrollBarSize(187)
		# self.elements["scrollbar"].SetScrollEvent(ui.__mem_func__(self.OnScroll))
		# self.elements["scrollbar"].Show()
		# >>> SECTION END <<<
		self.elements["scrollbar"] = None

		# 8 visible page rows on the right panel (new_fast_equip skin). 10 sets total -> mousewheel
		# scrolls scrollbar_pos in [1, 3] to reach pages 9-10.
		ROW_X = 6
		ROW_Y0 = 10
		ROW_PITCH = 28
		for i in xrange(0, self.elements["max_presets_view"]):
			k = "slot_presets%d" % i
			tmp = ui.RadioButton()
			tmp.SetParent(self.thinboard_presets)
			tmp.SetUpVisual(ART + "btn_norm.png")
			tmp.SetOverVisual(ART + "btn_hover.png")
			tmp.SetDownVisual(ART + "btn_select.png")
			tmp.SetPosition(ROW_X, ROW_Y0 + i * ROW_PITCH)
			tmp.Show()
			self.elements[k] = tmp

			k = "button_rename_%d" % i
			tmp = ui.Button()
			tmp.SetParent(self.thinboard_presets)
			tmp.SetUpVisual(ART + "edit_norm.png")
			tmp.SetOverVisual(ART + "edit_hover.png")
			tmp.SetDownVisual(ART + "edit_select.png")
			tmp.SetPosition(ROW_X + 126 - 20, ROW_Y0 + i * ROW_PITCH + 7)
			tmp.SetToolTipText(localeinfo.FAST_EQUIPMENT_CHANGE_NAME)
			tmp.Show()
			self.elements[k] = tmp

			k = "slot_presets_name%d"%i
			tmp = ui.TextLine()
			tmp.SetParent(self.elements["slot_presets%d"%i])
			tmp.SetPosition(57, 8)
			tmp.SetHorizontalAlignCenter()

			k2 = "presets_name%d" % i
			if self.elements.has_key(k2):
				tmp.SetText(self.elements[k2])
			else:
				tmp.SetText(localeinfo.FAST_EQUIPMENT_PAGE % (localeinfo.NumberToRoman(i + 1)))

			tmp.Show()
			self.elements[k] = tmp

		self.SetViewPresets()
		self.FuncSelectPresets(0, 1)

	def OnCancelAddPresets(self):
		if self.name_presets:
			self.name_presets.Close()
			del self.name_presets
			self.name_presets = None

	def RefreshTextLine(self):
		for i in xrange(0, self.elements["max_presets_view"]):
			idx = i + self.elements["scrollbar_pos"]
			if app.ENABLE_GEAR_SETS:
				name = net.GetGearSetName(idx - 1)
				if not name:
					name = localeinfo.FAST_EQUIPMENT_PAGE % (localeinfo.NumberToRoman(idx))
				self.elements["slot_presets_name%d" % i].SetText(name)
			else:
				self.elements["slot_presets_name%d" % i].SetText(self.elements["presets_name%d" % (idx - 1)])
	def RefreshTitle(self):
		if not self.title_bar_s:   # page-name header removed from the new skin
			return
		if app.ENABLE_GEAR_SETS:
			sel = self.elements["select_presets"]
			name = net.GetGearSetName(sel - 1)
			if not name:
				name = localeinfo.FAST_EQUIPMENT_PAGE % (localeinfo.NumberToRoman(sel))
			self.title_bar_s.SetText(name)
			return
		k = "presets_name%d" % (self.elements["select_presets"] - 1)
		if self.elements.has_key(k):
			self.title_bar_s.SetText(self.elements[k])
		else:
			self.title_bar_s.SetText(localeinfo.FAST_EQUIPMENT_PAGE % (localeinfo.NumberToRoman(self.elements["select_presets"] + 1)))
	def UpdateTitle(self, i):
		if not self.title_bar_s:   # page-name header removed from the new skin
			return
		if self.elements["select_presets"] != i:
			return
		if app.ENABLE_GEAR_SETS:
			name = net.GetGearSetName(i - 1)
			if not name:
				name = localeinfo.FAST_EQUIPMENT_PAGE % (localeinfo.NumberToRoman(i))
			self.title_bar_s.SetText(name)
			return
		k = "presets_name%d" % (i - 1)
		if self.elements.has_key(k):
			self.title_bar_s.SetText(self.elements[k])
		else:
			self.title_bar_s.SetText(localeinfo.FAST_EQUIPMENT_PAGE % (localeinfo.NumberToRoman(i + 1)))

	def OnAddPresets(self):
		text = self.name_presets.GetText()
		if len(text) > 0:
			if app.ENABLE_GEAR_SETS:
				net.SendGearSetPacket(GEARSET_RENAME, self.index_presets, 0, 0, text)
				self.elements["presets_name%d" % self.index_presets] = text
				self.RefreshTitle()
				self.RefreshTextLine()
			else:
				self.elements["presets_name%d" % self.index_presets] = text

				myPath = "UserData\\fast_equip"

				import os
				if not os.path.exists(os.getcwd() + os.sep + myPath):
					os.mkdir(os.getcwd() + os.sep + myPath)

				filePath = myPath + "\\" + player.GetName() + ".data"
				old_open(filePath, "w").close()

				myData = ""
				myFile = old_open(filePath, "wb")

				for i in xrange(0, self.elements["max_presets_count"]):
					myData += "%d\t%s\n" % (i, self.elements["presets_name%d" % i])

				myData = app.EncryptLocal(myData)
				myFile.write(myData)
				myFile.close()

				self.RefreshTitle()
				self.RefreshTextLine()

		self.OnCancelAddPresets()
	def SavePresets(self, i):
		tmp = uicommon.InputDialog()
		tmp.SetTitle(localeinfo.FAST_EQUIPMENT_CHANGE_NAME)
		tmp.SetAcceptEvent(ui.__mem_func__(self.OnAddPresets))
		tmp.SetCancelEvent(ui.__mem_func__(self.OnCancelAddPresets))
		tmp.SetMaxLength(20)
		tmp.Open()
		self.name_presets = tmp
		self.index_presets = i

	def SetViewPresets(self):
		for i in xrange(0, self.elements["max_presets_view"]):
			idx = i + self.elements["scrollbar_pos"]
			self.elements["slot_presets%d" % i].SetEvent(self.FuncSelectPresets, i, idx)
			self.elements["button_rename_%d" % i].SetEvent(self.SavePresets, idx - 1)
			self.ClickRadioButton(i, idx)

		self.RefreshTextLine()

	def FuncSelectPresets(self, index_a, index_b):
		for i in xrange(self.elements["max_presets_view"]):
			self.elements["slot_presets%d" % i].SetUp()

		self.elements["select_presets"] = index_b

		self.ClickRadioButton(index_a, index_b)

		self.UpdateTitle(index_b)

		self.RefreshEquipSlotWindow()
		self.RefreshDungeonCombo()

	def ClickRadioButton(self,index,index1):
		if self.elements["select_presets"] == index1:
			self.elements["slot_presets%d"%index].Down()
		else:
			self.elements["slot_presets%d"%index].SetUp()

	def GetChangeEquipIndex(self):
		return self.elements["select_presets"]

	def SelectEmptySlot(self, selectedSlotPos):
		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.MOVE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		isAttached = mousemodule.mouseController.isAttached()
		index_change_equip = self.GetChangeEquipIndex()

		if app.ENABLE_GEAR_SETS:
			wear_cell = selectedSlotPos - player.CHANGE_EQUIP_SLOT_START
			if isAttached:
				attachedSlotType = mousemodule.mouseController.GetAttachedType()
				attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
				mousemodule.mouseController.DeattachObject()
				if player.SLOT_TYPE_INVENTORY == attachedSlotType:
					net.SendGearSetPacket(GEARSET_LINK, index_change_equip - 1, wear_cell, attachedSlotPos)
			return

		selectedSlotPos = player.CHANGE_EQUIP_SLOT_COUNT/player.CHANGE_EQUIP_PAGE_EXTRA*(index_change_equip-1) + (selectedSlotPos-player.CHANGE_EQUIP_SLOT_START)

		if isAttached:
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			mousemodule.mouseController.DeattachObject()

			if player.SLOT_TYPE_INVENTORY == attachedSlotType:
				attachedCount = mousemodule.mouseController.GetAttachedItemCount()
				net.SendItemMovePacket(player.INVENTORY, attachedSlotPos, player.CHANGE_EQUIP, selectedSlotPos, attachedCount)
	def SelectItemSlot(self, selectedSlotPos):

		if uiprivateshopbuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.MOVE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		isAttached = mousemodule.mouseController.isAttached()
		index_change_equip = self.GetChangeEquipIndex()

		if app.ENABLE_GEAR_SETS:
			wear_cell = selectedSlotPos - player.CHANGE_EQUIP_SLOT_START
			if isAttached:
				attachedSlotType = mousemodule.mouseController.GetAttachedType()
				attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
				mousemodule.mouseController.DeattachObject()
				if player.SLOT_TYPE_INVENTORY == attachedSlotType:
					net.SendGearSetPacket(GEARSET_LINK, index_change_equip - 1, wear_cell, attachedSlotPos)
			return

		selectedSlotPos = player.CHANGE_EQUIP_SLOT_COUNT/player.CHANGE_EQUIP_PAGE_EXTRA*(index_change_equip-1) + (selectedSlotPos-player.CHANGE_EQUIP_SLOT_START)
		if isAttached:
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			mousemodule.mouseController.DeattachObject()
			if player.SLOT_TYPE_INVENTORY == attachedSlotType:
				itemIndex = player.GetItemIndex(attachedSlotPos)
				itemCount = player.GetItemCount(attachedSlotPos)

				item.SelectItem(itemIndex)
				itemType = item.GetItemType()

				attachedCount = mousemodule.mouseController.GetAttachedItemCount()
				net.SendItemMovePacket(player.INVENTORY, attachedSlotPos, player.CHANGE_EQUIP, selectedSlotPos, attachedCount)
		else:
			itemVnum = player.GetItemIndex(player.CHANGE_EQUIP, selectedSlotPos)
			itemCount = player.GetItemCount(player.CHANGE_EQUIP, selectedSlotPos)
			mousemodule.mouseController.AttachObject(self, player.SLOT_TYPE_CHANGE_EQUIP, selectedSlotPos, itemVnum, itemCount)
	def UseItemSlot(self, slotIndex):
		curCursorNum = app.GetCursor()
		if app.SELL == curCursorNum:
			return

		if constinfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		index_change_equip = self.GetChangeEquipIndex()

		if app.ENABLE_GEAR_SETS:
			wear_cell = slotIndex - player.CHANGE_EQUIP_SLOT_START
			net.SendGearSetPacket(GEARSET_UNLINK, index_change_equip - 1, wear_cell)
			mousemodule.mouseController.DeattachObject()
			self.OverOutItem()
			return

		slotIndex = player.CHANGE_EQUIP_SLOT_COUNT/player.CHANGE_EQUIP_PAGE_EXTRA*(index_change_equip-1) + (slotIndex-player.CHANGE_EQUIP_SLOT_START)

		net.SendItemUsePacket(player.CHANGE_EQUIP, slotIndex)
		mousemodule.mouseController.DeattachObject()
		self.OverOutItem()
	def RefreshEquipSlotWindow(self):
		index_change_equip = self.GetChangeEquipIndex()
		count = 0

		if app.ENABLE_GEAR_SETS:
			if index_change_equip != 0:
				set_idx = index_change_equip - 1
				slots_per_page = player.CHANGE_EQUIP_SLOT_COUNT/player.CHANGE_EQUIP_PAGE_EXTRA
				for i in xrange(0, slots_per_page):
					slotNumber = player.CHANGE_EQUIP_SLOT_START + i
					self.equipament.SetItemSlot(slotNumber, net.GetGearSetItemVnum(set_idx, i), 0)
			self.equipament.RefreshSlot()
			return

		if index_change_equip != 0:
			if index_change_equip > 1:
				index_old = player.CHANGE_EQUIP_SLOT_COUNT/player.CHANGE_EQUIP_PAGE_EXTRA*(index_change_equip-1)
			else:
				index_old = player.CHANGE_EQUIP_SLOT_COUNT-(player.CHANGE_EQUIP_SLOT_COUNT/index_change_equip)

			for i in xrange(index_old ,player.CHANGE_EQUIP_SLOT_COUNT/player.CHANGE_EQUIP_PAGE_EXTRA*index_change_equip):
				slotNumber = player.CHANGE_EQUIP_SLOT_START + count

				itemCount = player.GetItemCount(player.CHANGE_EQUIP,i)
				if itemCount <= 1:
					itemCount = 0

				self.equipament.SetItemSlot(slotNumber, player.GetItemIndex(player.CHANGE_EQUIP,i), itemCount)
				count += 1

		self.equipament.RefreshSlot()
	def OverInItem(self,index):
		index_change_equip = self.GetChangeEquipIndex()

		if app.ENABLE_GEAR_SETS:
			set_idx = index_change_equip - 1
			wear_cell = index - player.CHANGE_EQUIP_SLOT_START
			vnum = net.GetGearSetItemVnum(set_idx, wear_cell)
			if None != self.toolTip and vnum:
				# The server sends this slot's REAL item (resolved by item id): metin sockets + the
				# (type, value) attribute pairs. Render the specific item so its bonuses show.
				metinSlot = [net.GetGearSetItemSocket(set_idx, wear_cell, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
				attrSlot = [net.GetGearSetItemAttr(set_idx, wear_cell, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
				self.toolTip.ClearToolTip()
				self.toolTip.AddItemData(vnum, metinSlot, attrSlot)
				self.toolTip.ShowToolTip()
			return

		index = player.CHANGE_EQUIP_SLOT_COUNT/player.CHANGE_EQUIP_PAGE_EXTRA*(index_change_equip-1) + (index-player.CHANGE_EQUIP_SLOT_START)

		if None != self.toolTip:
			self.toolTip.ClearToolTip()
			self.toolTip.SetInventoryItem(index, player.CHANGE_EQUIP)
	def OverOutItem(self):
		self.toolTip.HideToolTip()

	def ClickChangeEquip(self):
		index_change_equip = self.GetChangeEquipIndex()
		if index_change_equip != 0:
			if app.ENABLE_GEAR_SETS:
				net.SendGearSetPacket(GEARSET_EQUIP, index_change_equip - 1)
			else:
				net.SendChatPacket("/change_equip_wa %d"%(index_change_equip))

	def ClickGetToken(self):
		# Dispense the Loadout Token for the selected page. The server refuses if you already hold it
		# (throw it away to get another) or your bag is full; messages come back via ChatPacketNew.
		index_change_equip = self.GetChangeEquipIndex()
		if index_change_equip != 0:
			net.SendGearSetPacket(GEARSET_GIVE_TOKEN, index_change_equip - 1)

	def LinkItemFromInventory(self, invPos):
		# Right-click auto-link (inventory item, this window open): the server resolves the wear cell
		# from the item (0xFFFF = auto), so no drop target is needed. Mirrors safebox right-click-to-stow.
		index_change_equip = self.GetChangeEquipIndex()
		if index_change_equip != 0:
			net.SendGearSetPacket(GEARSET_LINK, index_change_equip - 1, 0xFFFF, invPos)

	def RequestGearSetData(self):
		# Pull the full gear-set state from the server (server never pushes it unsolicited at
		# login, so an unflagged client never receives HEADER_GC_GEARSET and cannot desync).
		if app.ENABLE_GEAR_SETS:
			net.SendGearSetPacket(GEARSET_REQUEST, 0)

	def MakeDungeonCombo(self):
		# "Auto-equip in: [ dungeon v ]" row above the buttons. Selecting a dungeon links the
		# currently-selected set to that dungeon's base map index (server matches it on entry).
		self.dungeonLabel = ui.TextLine()
		self.dungeonLabel.SetParent(self)
		self.dungeonLabel.SetPosition(270, 229)
		self.dungeonLabel.SetText(localeinfo.GEARSET_AUTO_EQUIP_LABEL)
		self.dungeonLabel.SetOutline()
		self.dungeonLabel.Hide()

		names = []
		for i in xrange(len(GEARSET_DUNGEONS)):
			names.append(GEARSET_DUNGEONS[i][0])
		sel = GearSetDungeonSelector(self, self, 248, 228)
		sel.SetItems(names)
		sel.SetCurrentText(GEARSET_DUNGEONS[0][0])
		sel.SetSelectEvent(ui.__mem_func__(self.OnSelectDungeon))
		self.dungeonCombo = sel

	def OnSelectDungeon(self, index):
		if index < 0 or index >= len(GEARSET_DUNGEONS):
			return
		name, mapIndex = GEARSET_DUNGEONS[index]
		page = self.GetChangeEquipIndex()
		if page != 0:
			net.SendGearSetPacket(GEARSET_ASSIGN_DUNGEON, page - 1, mapIndex)

	def RefreshDungeonCombo(self):
		if not self.dungeonCombo:
			return
		page = self.GetChangeEquipIndex()
		dunId = net.GetGearSetDungeon(page - 1) if page != 0 else 0
		name = GEARSET_DUNGEONS[0][0]   # default = None
		for i in xrange(len(GEARSET_DUNGEONS)):
			if GEARSET_DUNGEONS[i][1] == dunId:
				name = GEARSET_DUNGEONS[i][0]
				break
		self.dungeonCombo.SetCurrentText(name)

	def RefreshGearSetWindow(self):
		self.RefreshTextLine()
		self.RefreshTitle()
		self.RefreshEquipSlotWindow()
		self.RefreshDungeonCombo()
	def ScrollPresets(self, nLen):
		# wheel up (nLen > 0) -> earlier pages, wheel down -> later pages.
		maxStart = self.elements["max_presets_count"] - self.elements["max_presets_view"] + 1
		if maxStart < 1:
			maxStart = 1
		pos = self.elements["scrollbar_pos"]
		pos = pos - 1 if nLen > 0 else pos + 1
		if pos < 1:
			pos = 1
		if pos > maxStart:
			pos = maxStart
		if pos != self.elements["scrollbar_pos"]:
			self.elements["scrollbar_pos"] = pos
			self.SetViewPresets()

	def OnMouseWheel(self, nLen):
		self.ScrollPresets(nLen)
		return True

	def OnRunMouseWheel(self, nLen):
		self.ScrollPresets(nLen)
		return True

	def OnScroll(self):
		# legacy draggable-scrollbar callback - no longer wired (mousewheel paging now). Safe no-op.
		return

	def Close(self):
		if self.name_presets:
			self.name_presets.Close()
			del self.name_presets
			self.name_presets = None

		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

class ScrollBarNew(ui.Window):
	MIDDLE_BAR_POS = 4
	SCROLLBAR_BUTTON_HEIGHT = 0
	SCROLLBAR_WIDTH = 4
	SCROLLBAR_MIDDLE_HEIGHT = 33

	class MiddleBar(ui.DragButton):
		def __init__(self):
			ui.DragButton.__init__(self)
			self.AddFlag("movable")

		def MakeImage(self):
			bar = ui.ImageBox()
			bar.SetParent(self)
			bar.LoadImage(PATCH_DESIGN+"middle_bar.tga")
			bar.SetPosition(0, 0)
			bar.AddFlag("not_pick")
			bar.Show()
			self.bar = bar

		def SetSize(self, height):
			height = max(12, height)
			ui.DragButton.SetSize(self, 10, height)
			height -= 4*3

	def __init__(self):
		ui.Window.__init__(self)

		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = lambda *arg: None
		self.lockFlag = False
		self.scrollStep = 0.20


		self.CreateScrollBar()

	def __del__(self):
		ui.Window.__del__(self)

	def CreateScrollBar(self):
		barSlot = ui.ImageBox()
		barSlot.SetParent(self)
		barSlot.AddFlag("not_pick")
		barSlot.LoadImage(PATCH_DESIGN+"bar_slot_new.tga")
		barSlot.Show()

		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(ui.__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(33)

		self.middleBar = middleBar
		self.barSlot = barSlot

		self.SCROLLBAR_MIDDLE_HEIGHT = self.middleBar.GetHeight()


	def Destroy(self):
		self.middleBar = None
		self.eventScroll = lambda *arg: None

	def SetScrollEvent(self, event):
		self.eventScroll = event

	def GetPos(self):
		return self.curPos

	def SetPos(self, pos):
		pos = max(0.0, pos)
		pos = min(1.0, pos)

		newPos = float(self.pageSize) * pos
		self.middleBar.SetPosition(self.MIDDLE_BAR_POS, int(newPos))
		self.OnMove()


	def SetScrollBarSize(self, height):
		self.pageSize = height- self.SCROLLBAR_MIDDLE_HEIGHT
		self.SetSize(self.SCROLLBAR_WIDTH, height)
		self.middleBar.SetRestrictMovementArea(self.MIDDLE_BAR_POS, 0, 8, 187)
		self.middleBar.SetPosition(self.MIDDLE_BAR_POS, 0)

		self.UpdateBarSlot()

	def UpdateBarSlot(self):
		self.barSlot.SetPosition(0, self.SCROLLBAR_BUTTON_HEIGHT)

	def SetScrollStep(self, step):
		self.scrollStep = step

	def GetScrollStep(self):
		return self.scrollStep

	def OnUp(self):
		self.SetPos(self.curPos-self.scrollStep)

	def OnDown(self):
		self.SetPos(self.curPos+self.scrollStep)

	def OnMove(self):

		if self.lockFlag:
			return

		if 0 == self.pageSize:
			return

		(xLocal, yLocal) = self.middleBar.GetLocalPosition()
		self.curPos = float(yLocal) / float(self.pageSize)

		self.eventScroll()

	def OnMouseLeftButtonDown(self):
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		pickedPos = yMouseLocalPosition  - self.SCROLLBAR_MIDDLE_HEIGHT/2
		newPos = float(pickedPos) / float(self.pageSize)
		self.SetPos(newPos)

	def LockScroll(self):
		self.lockFlag = True

	def UnlockScroll(self):
		self.lockFlag = False
