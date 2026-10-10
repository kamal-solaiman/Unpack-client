# coding: latin_1

import app
import net
import player

import dbg
import item
import snd
import ui
import uitooltip
import localeinfo

class AttachMetinDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__LoadScript()

		self.metinItemPos = 0
		self.targetItemPos = 0

	def __LoadScript(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/attachstonedialog.py")

		except:
			import exception
			exception.Abort("AttachStoneDialog.__LoadScript.LoadObject")

		try:
			self.board = self.GetChild("Board")
			self.titleBar = self.GetChild("TitleBar")
			self.metinImage = self.GetChild("MetinImage")
			self.GetChild("AcceptButton").SetEvent(ui.__mem_func__(self.Accept))
			self.GetChild("CancelButton").SetEvent(ui.__mem_func__(self.Close))

		except:
			import exception
			exception.Abort("AttachStoneDialog.__LoadScript.BindObject")

		oldToolTip = uitooltip.ItemToolTip()
		oldToolTip.SetParent(self)
		oldToolTip.SetPosition(15, 38)
		oldToolTip.SetFollow(False)
		oldToolTip.Show()
		self.oldToolTip = oldToolTip

		newToolTip = uitooltip.ItemToolTip()
		newToolTip.SetParent(self)
		newToolTip.SetPosition(230 + 20, 38)
		newToolTip.SetFollow(False)
		newToolTip.Show()
		self.newToolTip = newToolTip

		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.ClearDictionary()
		self.board = 0
		self.titleBar = 0
		self.metinImage = 0
		self.toolTip = 0

	def CanAttachMetin(self, slot, metin):
		if item.METIN_NORMAL == metin:
			if player.METIN_SOCKET_TYPE_SILVER == slot or player.METIN_SOCKET_TYPE_GOLD == slot:
				return True
		elif item.METIN_GOLD == metin:
			if player.METIN_SOCKET_TYPE_GOLD == slot:
				return True
		elif app.USE_GLOVE_SYSTEM and metin == item.METIN_SUNGMA:
			if player.METIN_SOCKET_TYPE_SILVER == slot or player.METIN_SOCKET_TYPE_GOLD == slot:
				return True

	def Open(self, metinItemPos, targetItemPos):
		self.metinItemPos = metinItemPos
		self.targetItemPos = targetItemPos

		metinIndex = player.GetItemIndex(metinItemPos)
		itemIndex = player.GetItemIndex(targetItemPos)
		self.oldToolTip.ClearToolTip()
		self.newToolTip.ClearToolTip()

		item.SelectItem(metinIndex)
		metinSubType = item.GetItemSubType()

		## Metin Image
		try:
			self.metinImage.LoadImage(item.GetIconImageFileName())
		except:
			dbg.TraceError("AttachMetinDialog.Open.LoadImage - Failed to find item data")

		## New Item ToolTip
		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(player.GetItemMetinSocket(targetItemPos, i))
		apply_random_list = []
		if app.ENABLE_APPLY_RANDOM:
			for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
				apply_random_list.append(player.GetItemApplyRandom(targetItemPos, i))
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			slotData = metinSlot[i]
			if self.CanAttachMetin(slotData, metinSubType):
				metinSlot[i] = metinIndex
				break
		if app.ENABLE_SET_ITEM:
			set_value = player.GetItemSetValue(metinIndex, targetItemPos)
		self.newToolTip.AddItemData(itemIndex, metinSlot, 0, None, 0, 0, player.INVENTORY, -1, None, apply_random_list, 0,0,0,set_value)

		## Old Item ToolTip
		item.SelectItem(metinIndex)
		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(player.GetItemMetinSocket(targetItemPos, i))
		apply_random_list = []
		if app.ENABLE_APPLY_RANDOM:
			for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
				apply_random_list.append(player.GetItemApplyRandom(targetItemPos, i))
		if app.ENABLE_SET_ITEM:
			set_value = player.GetItemSetValue(metinIndex, targetItemPos)
		self.oldToolTip.ResizeToolTipWidth(self.newToolTip.GetWidth())
		self.oldToolTip.AddItemData(itemIndex, metinSlot, 0, None, 0, 0, player.INVENTORY, -1, None, apply_random_list, 0,0,0,set_value)

		self.UpdateDialog()
		self.SetTop()
		self.Show()

	def UpdateDialog(self):
		newWidth = 15 + self.oldToolTip.GetWidth() + 45 + self.newToolTip.GetWidth() + 15
		newHeight = self.newToolTip.GetHeight() + 98

		self.newToolTip.SetPosition(15 + self.oldToolTip.GetWidth() + 45, 38)
		if localeinfo.IsARABIC():
			self.board.SetPosition( newWidth, 0 )

			(x,y) = self.titleBar.GetLocalPosition()
			self.titleBar.SetPosition( newWidth - 15, y )

		self.board.SetSize(newWidth, newHeight)
		self.titleBar.SetWidth(newWidth-15)
		self.SetSize(newWidth, newHeight)

		(x, y) = self.GetLocalPosition()
		self.SetPosition(x, y)

	def Accept(self):
		net.SendItemUseToItemPacket(self.metinItemPos, self.targetItemPos)

		snd.PlaySound("sound/ui/metinstone_insert.wav")
		self.Close()

	def Close(self):
		self.Hide()