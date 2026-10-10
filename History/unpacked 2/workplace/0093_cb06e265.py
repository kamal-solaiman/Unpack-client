# coding: latin_1

import app
import player

import grp
import grpImage
import item
import wndMgr

import skill
import dbg
import grpText

import ui

import systemSetting

import localeinfo

## Mouse Controler

class CursorImage(object):
	if app.USE_V1:
		def __init__(self, imageName):
			self.handle = 0
			self.LoadImage(imageName)
	else:
		def __init__(self):
			self.handle = 0

		def __init__(self, imageName):
			self.handle = 0
			self.LoadImage(imageName)

	if not app.USE_V1:
		def __del__(self):
			if self.handle:
				grpImage.Delete(self.handle)
				self.handle = 0

	def LoadImage(self, imageName):
		try:
			self.handle = grpImage.Generate(imageName)

		except:
			import sys
			dbg.TraceError("%s %s" % (sys.exc_info()[0], sys.exc_info()[1]))
			self.handle = 0

	def DeleteImage(self):
		if self.handle:
			if app.USE_V1:
				del self.handle
			else:
				grpImage.Delete(self.handle)

			self.handle = 0

	def IsImage(self):
		if self.handle:
			return True

		return False

	def SetPosition(self, x, y):
		if self.handle:
			grpImage.SetPosition(self.handle, x, y)

	def Render(self):
		if self.handle:
			grpImage.Render(self.handle)

class CMouseController(object):
	def __init__(self):
		if app.ENABLE_CHEQUE_SYSTEM:
			self.chequeValue = 0
			self.chequeNumberLine = None

		self.x = 0
		self.y = 0

		self.IsSoftwareCursor = FALSE
		self.curCursorName = ""
		self.curCursorImage = 0
		self.cursorPosX = 0
		self.cursorPosY = 0

		self.AttachedIconHandle = 0
		self.AttachedOwner = 0
		self.AttachedFlag = FALSE
		self.AttachedType = 0
		self.AttachedSlotNumber = 0
		self.AttachedCount = 1
		self.AttachedIconHalfWidth = 0
		self.AttachedIconHalfHeight = 0
		self.LastAttachedSlotNumber = 0

		self.countNumberLine = None

		if app.USE_BL_FISH_EVENT:
			self.IsAttachedIconRender = True

		self.DeattachObject()

		self.callbackDict = {}
		if app.ENABLE_COMMON_CHANGES:
			self.cursorDict = {}

	def __del__(self):
		self.callbackDict = {}

		if app.ENABLE_COMMON_CHANGES:
			for k, v in self.cursorDict.items():
				if app.USE_V1:
					del v
				else:
					v.DeleteImage()

	def Destroy(self):
		del self.countNumberLine
		self.countNumberLine = None
		if app.ENABLE_CHEQUE_SYSTEM:
			del self.chequeNumberLine
			self.chequeNumberLine = None

	def CreateNumberLine(self):
		self.countNumberLine = ui.NumberLine("GAME")
		self.countNumberLine.SetHorizontalAlignCenter()
		self.countNumberLine.Hide()

		if app.ENABLE_CHEQUE_SYSTEM:
			self.chequeNumberLine = ui.NumberLine("GAME")
			self.chequeNumberLine.SetHorizontalAlignCenter()
			self.chequeNumberLine.Hide()

	def Create(self):
		self.IsSoftwareCursor = systemSetting.IsSoftwareCursor()

		self.cursorDict = {
			app.NORMAL : CursorImage("d:/ymir work/ui/cursor/cursor.sub"),
			app.ATTACK : CursorImage("d:/ymir work/ui/cursor/cursor_attack.sub"),
			app.TARGET : CursorImage("d:/ymir work/ui/cursor/cursor_attack.sub"),
			app.TALK : CursorImage("d:/ymir work/ui/cursor/cursor_talk.sub"),
			app.CANT_GO : CursorImage("d:/ymir work/ui/cursor/cursor_no.sub"),
			app.PICK : CursorImage("d:/ymir work/ui/cursor/cursor_pick.sub"),
			app.DOOR : CursorImage("d:/ymir work/ui/cursor/cursor_door.sub"),
			app.CHAIR : CursorImage("d:/ymir work/ui/cursor/cursor_chair.sub"),
			app.MAGIC : CursorImage("d:/ymir work/ui/cursor/cursor_chair.sub"),
			app.BUY : CursorImage("d:/ymir work/ui/cursor/cursor_buy.sub"),
			app.SELL : CursorImage("d:/ymir work/ui/cursor/cursor_sell.sub"),
			app.CAMERA_ROTATE : CursorImage("d:/ymir work/ui/cursor/cursor_camera_rotate.sub"),
			app.HSIZE : CursorImage("d:/ymir work/ui/cursor/cursor_hsize.sub"),
			app.VSIZE : CursorImage("d:/ymir work/ui/cursor/cursor_vsize.sub"),
			app.HVSIZE : CursorImage("d:/ymir work/ui/cursor/cursor_hvsize.sub"),
		}

		if app.ENABLE_FISHING_GAME:
			self.cursorDict[app.FISH] = CursorImage("d:/ymir work/ui/cursor/fishing_mouse_cursor.sub")

		self.cursorPosDict = {
			app.NORMAL			: (0, 0),
			app.TARGET			: (0, 0),
			app.ATTACK			: (0, 0),
			app.TALK			: (0, 0),
			app.CANT_GO			: (0, 0),
			app.PICK			: (0, 0),
			app.DOOR			: (0, 0),
			app.CHAIR			: (0, 0),
			app.MAGIC			: (0, 0),
			app.BUY				: (0, 0),
			app.SELL			: (0, 0),
			app.CAMERA_ROTATE	: (0, 0),
			app.HSIZE			: (-16, -16),
			app.VSIZE			: (-16, -16),
			app.HVSIZE			: (-16, -16),
		}

		if app.ENABLE_FISHING_GAME:
			self.cursorPosDict[app.FISH] = (0, 0)

		app.SetCursor(app.NORMAL)

		"""
		AttachedCountTextLineHandle = grpText.Generate()
		grpText.SetFontName(AttachedCountTextLineHandle, localeinfo.UI_DEF_FONT_SMALL)
		grpText.SetText(AttachedCountTextLineHandle, "1234")
		grpText.SetPosition(AttachedCountTextLineHandle, 100, 100)
		grpText.SetOutline(AttachedCountTextLineHandle, True)
		grpText.SetFontColor(AttachedCountTextLineHandle, 1.0, 1.0, 1.0)
		grpText.SetHorizontalAlign(AttachedCountTextLineHandle, wndMgr.TEXT_HORIZONTAL_ALIGN_CENTER)
		self.AttachedCountTextLineHandle = AttachedCountTextLineHandle
		"""

		#self.countNumberLine = ui.NumberLine("CURTAIN")
		#self.countNumberLine.SetHorizontalAlignCenter()
		#self.countNumberLine.Hide()

		#if app.ENABLE_CHEQUE_SYSTEM:
		#	self.chequeNumberLine = ui.NumberLine("CURTAIN")
		#	self.chequeNumberLine.SetHorizontalAlignCenter()
		#	self.chequeNumberLine.Hide()

		return True

	# Cursor Control
	def ChangeCursor(self, cursorNum):
		try:
			self.curCursorNum = cursorNum
			self.curCursorImage = self.cursorDict[cursorNum]
			(self.cursorPosX, self.cursorPosY) = self.cursorPosDict[cursorNum]

			if False == self.curCursorImage.IsImage():
				self.curCursorNum = app.NORMAL
				self.curCursorImage = self.cursorDict[app.NORMAL]

		except KeyError:
			dbg.TraceError("mousemodule.MouseController.SetCursor [%d]" % cursorNum)
			self.curCursorName = app.NORMAL
			self.curCursorImage = self.cursorDict[app.NORMAL]

	# Attaching
	def AttachObject(self, Owner, Type, SlotNumber, ItemIndex, count = 0):
		self.LastAttachedSlotNumber = self.AttachedSlotNumber

		self.AttachedFlag = True
		self.AttachedOwner = Owner
		self.AttachedType = Type
		self.AttachedSlotNumber = SlotNumber
		self.AttachedItemIndex = ItemIndex
		self.AttachedCount = count
		self.countNumberLine.SetNumber("")
		self.countNumberLine.Hide()

		if count > 1:
			self.countNumberLine.SetNumber(str(count))
			self.countNumberLine.Show()

		try:
			width = 1
			height = 1

			if Type == player.SLOT_TYPE_INVENTORY or\
				Type == player.SLOT_TYPE_PRIVATE_SHOP or\
				Type == player.SLOT_TYPE_SHOP or\
				Type == player.SLOT_TYPE_SAFEBOX or\
				Type == player.SLOT_TYPE_MALL or\
				Type == player.SLOT_TYPE_DRAGON_SOUL_INVENTORY or\
				Type == player.SLOT_TYPE_SKILL_BOOK_INVENTORY or\
				Type == player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY or\
				Type == player.SLOT_TYPE_STONE_INVENTORY or\
				Type == player.SLOT_TYPE_GIFT_BOX_INVENTORY or\
				Type == player.SLOT_TYPE_ENCHANT_INVENTORY or\
				Type == player.SLOT_TYPE_POTS_INVENTORY or\
				Type == player.SLOT_TYPE_SWITCHBOT or\
				(app.FAST_EQUIP_WORLDARD and self.AttachedType == player.SLOT_TYPE_CHANGE_EQUIP):
				item.SelectItem(self.AttachedItemIndex)
				self.AttachedIconHandle = item.GetIconInstance()

				if not self.AttachedIconHandle:
					self.AttachedIconHandle = 0
					self.DeattachObject()
					return

				(width, height) = item.GetItemSize()

			elif Type == player.SLOT_TYPE_SKILL:
				skillGrade = player.GetSkillGrade(SlotNumber)
				self.AttachedIconHandle = skill.GetIconInstanceNew(self.AttachedItemIndex, skillGrade)

			elif Type == player.SLOT_TYPE_EMOTION:
				image = player.GetEmotionIconImage(ItemIndex)

				if app.USE_V1:
					self.AttachedIconHandle = grpImage.Generate(image)
				else:
					self.AttachedIconHandle = grpImage.GenerateFromHandle(image)
			elif Type == player.SLOT_TYPE_QUICK_SLOT:
				(quickSlotType, position) = player.GetGlobalQuickSlot(SlotNumber)

				if quickSlotType == player.SLOT_TYPE_INVENTORY:

					itemIndex = player.GetItemIndex(position)
					item.SelectItem(itemIndex)
					self.AttachedIconHandle = item.GetIconInstance()
					(width, height) = item.GetItemSize()

				elif quickSlotType == player.SLOT_TYPE_SKILL:
					skillIndex = player.GetSkillIndex(position)
					skillGrade = player.GetSkillGrade(position)
					self.AttachedIconHandle = skill.GetIconInstanceNew(skillIndex, skillGrade)

				elif quickSlotType == player.SLOT_TYPE_EMOTION:
					image = player.GetEmotionIconImage(position)
					if app.USE_V1:
						self.AttachedIconHandle = grpImage.Generate(image)
					else:
						self.AttachedIconHandle = grpImage.GenerateFromHandle(image)

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if Type == player.SLOT_TYPE_CHANGE_LOOK:
					item.SelectItem(self.AttachedItemIndex)
					self.AttachedIconHandle = item.GetIconInstance()

					if not self.AttachedIconHandle:
						self.AttachedIconHandle = 0
						self.DeattachObject()
						return

					(width, height) = item.GetItemSize()

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				if Type == player.SLOT_TYPE_SKILL_BOOK_INVENTORY or\
					Type == player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY or\
					Type == player.SLOT_TYPE_STONE_INVENTORY or\
					Type == player.SLOT_TYPE_GIFT_BOX_INVENTORY or\
					Type == player.SLOT_TYPE_ENCHANT_INVENTORY or\
					Type == player.SLOT_TYPE_POTS_INVENTORY:
					
					item.SelectItem(self.AttachedItemIndex)
					self.AttachedIconHandle = item.GetIconInstance()

					if not self.AttachedIconHandle:
						self.AttachedIconHandle = 0
						self.DeattachObject()
						return

					(width, height) = item.GetItemSize()

			if not self.AttachedIconHandle:
				self.DeattachObject()
				return

			self.AttachedIconHalfWidth = grpImage.GetWidth(self.AttachedIconHandle) / 2
			self.AttachedIconHalfHeight = grpImage.GetHeight(self.AttachedIconHandle) / 2
			self.AttachedIconHalfWidth = grpImage.GetWidth(self.AttachedIconHandle) / 2
			self.AttachedIconHalfHeight = grpImage.GetHeight(self.AttachedIconHandle) / 2
			wndMgr.AttachIcon(self.AttachedType, self.AttachedItemIndex, self.AttachedSlotNumber, width, height)

		except Exception, e:
			dbg.TraceError("mousemodule.py: AttachObject : " + str(e))
			self.AttachedIconHandle = 0

	def IsAttachedMoney(self):
		if True == self.isAttached():
			if player.ITEM_MONEY == self.GetAttachedItemIndex():
				return True
			elif app.ENABLE_CHEQUE_SYSTEM:
				if player.ITEM_CHEQUE == self.GetAttachedItemIndex():
					return True

		return False

	def GetAttachedMoneyAmount(self):
		if True == self.isAttached():
			if player.ITEM_MONEY == self.GetAttachedItemIndex():
				return self.GetAttachedItemCount()
			elif app.ENABLE_CHEQUE_SYSTEM:
				if player.ITEM_CHEQUE == self.GetAttachedItemIndex():
					return True

		return 0

	if app.ENABLE_CHEQUE_SYSTEM:
		def AttachMoney(self, owner, type, count, cheque = 0):
			self.LastAttachedSlotNumber = self.AttachedSlotNumber

			self.AttachedFlag = True
			self.AttachedOwner = owner
			self.AttachedType = type
			self.AttachedSlotNumber = -1
			self.AttachedItemIndex = player.ITEM_MONEY
			self.AttachedCount = count
			self.AttachedIconHandle = grpImage.Generate("icon/item/money.tga")
			self.AttachedIconHalfWidth = grpImage.GetWidth(self.AttachedIconHandle) / 2
			self.AttachedIconHalfHeight = grpImage.GetHeight(self.AttachedIconHandle) / 2
			wndMgr.AttachIcon(self.AttachedType, self.AttachedItemIndex, self.AttachedSlotNumber, 1, 1)

			if count > 1:
				self.countNumberLine.SetNumber(str(count))
				self.countNumberLine.Show()

			if cheque > 0:
				self.chequeNumberLine.SetNumber(str(cheque), 1.0, 1.0, 0.0)
				self.chequeNumberLine.Show()
				self.SetCheque(cheque)
	else:
		def AttachMoney(self, owner, type, count):
			self.LastAttachedSlotNumber = self.AttachedSlotNumber

			self.AttachedFlag = True
			self.AttachedOwner = owner
			self.AttachedType = type
			self.AttachedSlotNumber = -1
			self.AttachedItemIndex = player.ITEM_MONEY
			self.AttachedCount = count
			self.AttachedIconHandle = grpImage.Generate("icon/item/money.tga")
			self.AttachedIconHalfWidth = grpImage.GetWidth(self.AttachedIconHandle) / 2
			self.AttachedIconHalfHeight = grpImage.GetHeight(self.AttachedIconHandle) / 2
			wndMgr.AttachIcon(self.AttachedType, self.AttachedItemIndex, self.AttachedSlotNumber, 1, 1)

			if count > 1:
				self.countNumberLine.SetNumber(str(count))
				self.countNumberLine.Show()
			#grpText.SetText(self.AttachedCountTextLineHandle, str(count))

	if app.ENABLE_CHEQUE_SYSTEM:
		def SetCheque(self, cheque):
			self.chequeValue = cheque

		def GetCheque(self):
			return self.chequeValue

	if app.USE_BL_FISH_EVENT:
		def AttachFishPiece(self, owner, shape, img_handle, adjust_x, adjust_y, width, height):
			self.LastAttachedSlotNumber = self.AttachedSlotNumber
			self.countNumberLine.SetNumber("")
			self.countNumberLine.Hide()

			self.AttachedFlag = True
			self.AttachedOwner = owner
			self.AttachedType = player.SLOT_TYPE_FISH_EVENT
			self.AttachedSlotNumber = -1
			self.AttachedItemIndex = shape
			self.AttachedCount = 0
			self.AttachedIconHandle = img_handle
			self.AttachedIconHalfWidth = grpImage.GetWidth(self.AttachedIconHandle) / 2 + adjust_x
			self.AttachedIconHalfHeight = grpImage.GetHeight(self.AttachedIconHandle) / 2 + adjust_y
			wndMgr.AttachIcon(self.AttachedType, self.AttachedItemIndex, self.AttachedSlotNumber, width, height)

		def DeattachObjectPostProcess(self):
			self.AttachedOwner = 0
			self.AttachedFlag = False
			self.AttachedType = -1
			self.AttachedItemIndex = -1
			self.AttachedSlotNumber = -1
			self.AttachedIconHandle = 0
			wndMgr.SetAttachingFlag(False)

			if self.countNumberLine:
				self.countNumberLine.Hide()

			if app.ENABLE_CHEQUE_SYSTEM:
				self.chequeValue = 0
				if self.chequeNumberLine:
					self.chequeNumberLine.Hide()

			app.ShowCursor()

		def SetAttachedIconRender(self, flag):
			self.IsAttachedIconRender = flag

		def GetAttachedIconRender(self):
			return self.IsAttachedIconRender

	def DeattachObject(self):
		self.ClearCallBack()
		self.LastAttachedSlotNumber = self.AttachedSlotNumber

		if self.AttachedIconHandle != 0:
			if app.USE_V1:
				if app.USE_BL_FISH_EVENT and self.AttachedType == player.SLOT_TYPE_FISH_EVENT:
					self.AttachedOwner.DropQuestionDialog()
					return
				else:
					del self.AttachedIconHandle
					self.AttachedIconHandle = 0
			else:
				if self.AttachedType == player.SLOT_TYPE_INVENTORY or\
					self.AttachedType == player.SLOT_TYPE_PRIVATE_SHOP or\
					self.AttachedType == player.SLOT_TYPE_SHOP or\
					self.AttachedType == player.SLOT_TYPE_SAFEBOX or\
					self.AttachedType == player.SLOT_TYPE_MALL or\
					self.AttachedType == player.SLOT_TYPE_SKILL_BOOK_INVENTORY or\
					self.AttachedType == player.SLOT_TYPE_UPGRADE_ITEMS_INVENTORY or\
					self.AttachedType == player.SLOT_TYPE_STONE_INVENTORY or\
					self.AttachedType == player.SLOT_TYPE_GIFT_BOX_INVENTORY or\
					self.AttachedType == player.SLOT_TYPE_ENCHANT_INVENTORY or\
					self.AttachedType == player.SLOT_TYPE_POTS_INVENTORY or\
					self.AttachedType == player.SLOT_TYPE_SWITCHBOT or\
					(app.FAST_EQUIP_WORLDARD and self.AttachedType == player.SLOT_TYPE_CHANGE_EQUIP):
					item.DeleteIconInstance(self.AttachedIconHandle)

				elif self.AttachedType == player.SLOT_TYPE_SKILL:
					skill.DeleteIconInstance(self.AttachedIconHandle)

				elif not app.USE_V1 and self.AttachedType == player.SLOT_TYPE_EMOTION:
					grpImage.Delete(self.AttachedIconHandle)
				elif app.USE_BL_FISH_EVENT and self.AttachedType == player.SLOT_TYPE_FISH_EVENT:
					self.AttachedOwner.DropQuestionDialog()
					return

		if app.USE_BL_FISH_EVENT:
			self.DeattachObjectPostProcess()
		else:
			self.AttachedFlag = False
			self.AttachedType = -1
			self.AttachedItemIndex = -1
			self.AttachedSlotNumber = -1
			self.AttachedIconHandle = 0
			wndMgr.SetAttachingFlag(False)

			if self.countNumberLine:
				self.countNumberLine.Hide()

			if app.ENABLE_CHEQUE_SYSTEM:
				self.chequeValue = 0
				if self.chequeNumberLine:
					self.chequeNumberLine.Hide()

	def isAttached(self):
		return self.AttachedFlag

	def GetAttachedOwner(self):
		if False == self.isAttached():
			return 0

		return self.AttachedOwner

	def GetAttachedType(self):
		if False == self.isAttached():
			return player.SLOT_TYPE_NONE

		return self.AttachedType

	def GetAttachedSlotNumber(self):
		if False == self.isAttached():
			return 0

		return self.AttachedSlotNumber

	def GetLastAttachedSlotNumber(self):
		return self.LastAttachedSlotNumber

	def GetAttachedItemIndex(self):
		if False == self.isAttached():
			return 0

		return self.AttachedItemIndex

	def GetAttachedItemCount(self):
		if False == self.isAttached():
			return 0

		return self.AttachedCount

	# Update
	def Update(self, x, y):
		self.x = x
		self.y = y

		if True == self.isAttached():
			if 0 != self.AttachedIconHandle:
				if app.USE_BL_FISH_EVENT and self.GetAttachedType() == player.SLOT_TYPE_FISH_EVENT:
					grpImage.SetDiffuseColor(self.AttachedIconHandle, 1.0, 1.0, 1.0, 1.0)
				else:
					grpImage.SetDiffuseColor(self.AttachedIconHandle, 1.0, 1.0, 1.0, 0.5)

				grpImage.SetPosition(self.AttachedIconHandle, self.x - self.AttachedIconHalfWidth, self.y - self.AttachedIconHalfHeight)
				self.countNumberLine.SetPosition(self.x, self.y - self.AttachedIconHalfHeight - 3)

			if app.ENABLE_CHEQUE_SYSTEM:
				if self.chequeNumberLine.IsShow():
					self.chequeNumberLine.SetPosition(self.x, self.y - self.AttachedIconHalfHeight - 13)

		if self.IsSoftwareCursor:
			if 0 != self.curCursorImage:
				self.curCursorImage.SetPosition(self.x + self.cursorPosX, self.y + self.cursorPosY)

	# Render
	def Render(self):
		if True == self.isAttached():
			if 0 != self.AttachedIconHandle:
				if app.USE_BL_FISH_EVENT:
					if self.IsAttachedIconRender == True:
						grpImage.Render(self.AttachedIconHandle)
				else:
					grpImage.Render(self.AttachedIconHandle)

		if self.IsSoftwareCursor:
			if True == app.IsShowCursor():
				if 0 != self.curCursorImage:
					self.curCursorImage.Render()
		else:
			if False == app.IsShowCursor():
				if True == app.IsLiarCursorOn():
					if 0 != self.curCursorImage:
						self.curCursorImage.SetPosition(self.x + self.cursorPosX, self.y + self.cursorPosY)
						self.curCursorImage.Render()

	def SetCallBack(self, type, event=lambda *arg:None):
		self.callbackDict[type] = event

	def RunCallBack(self, type, *arg):
		if not self.callbackDict.has_key(type):
			self.DeattachObject()
			return

		self.callbackDict[type]()

	def ClearCallBack(self):
		self.callbackDict = {}

mouseController = CMouseController()
