# coding: latin_1

import app
import chr
import net
import player

import ui
import item
import constinfo
import localeinfo
import uicommon
import wndMgr
import grp
import chat
import skill
import shop
import math
from _weakref import proxy
from operator import truediv
if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget
import offlineshop
import uitooltip
import ime
import dbg

import systemSetting

PATH = "cream/"
PATH_ROOT = "cream/searchshop/"

MAX_ITEMS_APPEND = 25
PATH_FILTER = "search/"
import uiswitchbot
SELECTED_ITEMS_BUY = {}

def GetTime():
	return app.GetTime()

def _IsSearchPremium():
	# The advanced-search features (sort modes, price-range filter, market-% column) are premium-only.
	# When the premium SYSTEM is off there is no premium tier, so they are available to everyone.
	if not app.USE_PREMIUM_FEATURES:
		return True
	return constinfo.player_premium_type != player.PREMIUM_TYPE_NONE

# Config Categories
def SetCategories(wnd):
	wnd.AppendItem(localeinfo.OFFLINESHOP_SEARCH_C1, "2.png", 89, -1, -1, False, True)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C1_1, 89, item.ITEM_TYPE_WEAPON)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C1_2, 89, item.ITEM_TYPE_ARMOR, item.ARMOR_BODY)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C1_3, 89, item.ITEM_TYPE_ARMOR, item.ARMOR_HEAD)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C1_4, 89, item.ITEM_TYPE_ARMOR, item.ARMOR_SHIELD)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C1_5, 89, item.ITEM_TYPE_ARMOR, item.ARMOR_EAR)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C1_6, 89, item.ITEM_TYPE_ARMOR, item.ARMOR_NECK)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C1_7, 89, item.ITEM_TYPE_ARMOR, item.ARMOR_WRIST)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_COMBOBOX_ARMOR_FOOTS, 89, item.ITEM_TYPE_ARMOR, item.ARMOR_FOOTS)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C1_8, 89, item.ITEM_TYPE_ARMOR, item.ARMOR_PENDANT_FIRE)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C1_9, 89, item.ITEM_TYPE_BELT) 

	wnd.AppendItem(localeinfo.OFFLINESHOP_SEARCH_C2, "4.png", 88, -1, -1, False, True)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C2_1, 88, item.ITEM_TYPE_COSTUME, item.COSTUME_TYPE_HAIR)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C2_2, 88, item.ITEM_TYPE_COSTUME, item.COSTUME_TYPE_BODY)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C2_3, 88, item.ITEM_TYPE_COSTUME, item.COSTUME_TYPE_ACCE)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C2_4, 88, item.ITEM_TYPE_COSTUME, item.COSTUME_TYPE_WEAPON)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C2_5, 88, item.ITEM_TYPE_COSTUME, item.COSTUME_TYPE_MOUNT)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C8, 88, item.ITEM_TYPE_QUEST ,item.QUEST_PET)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C2_22, 88, item.ITEM_TYPE_COSTUME, item.COSTUME_MOUNT_SKIN)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C2_23, 88, item.ITEM_TYPE_COSTUME ,item.COSTUME_PET_SKIN )
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C2_6, 88, item.ITEM_TYPE_SHINING,item.SHINING_WEAPON)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C2_7, 88, item.ITEM_TYPE_SHINING,item.SHINING_ARMOR)

	wnd.AppendItem(localeinfo.OFFLINESHOP_SEARCH_C4, "6.png", 87, -1, -1, False, True)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C4_1, 87, item.ITEM_TYPE_USE,item.ITEM_ENCHANT)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C4_2, 87, item.ITEM_TYPE_USE,item.USE_ENCHANT_BODY_COSTUME)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C4_3, 87, item.ITEM_TYPE_USE,item.USE_ENCHANT_HAIR_COSTUME)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C4_4, 87, item.ITEM_TYPE_USE,item.USE_ENCHANT_WEAPON_COSTUME)

	wnd.AppendItem(localeinfo.OFFLINESHOP_SEARCH_CATEGORY_OTHERS, "9.png", 86, -1, -1, False, True)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C3, 86, item.ITEM_TYPE_GIFTBOX, -1)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C11, 86, item.ITEM_TYPE_EX_SLOT, -1)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C5, 86, item.ITEM_TYPE_METIN, -1)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C6, 86, item.ITEM_TYPE_MATERIAL, -1)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C7, 86, item.ITEM_TYPE_DS, -1)
	wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C10, 86, item.ITEM_TYPE_QUEST, 0) # item.QUEST_NONE client-side is 1 instead 0

	#wnd.AppendItem(localeinfo.OFFLINESHOP_SEARCH_C3, "8.dds", item.ITEM_TYPE_GIFTBOX)
	#wnd.AppendItem(localeinfo.OFFLINESHOP_SEARCH_C11, "11.dds", item.ITEM_TYPE_EX_SLOT)
	#wnd.AppendItem(localeinfo.OFFLINESHOP_SEARCH_C5, "3.dds", item.ITEM_TYPE_METIN)
	#wnd.AppendItem(localeinfo.OFFLINESHOP_SEARCH_C6, "9.dds", item.ITEM_TYPE_MATERIAL)
	#wnd.AppendItem(localeinfo.OFFLINESHOP_SEARCH_C7, "11.dds", item.ITEM_TYPE_DS)
	#wnd.AppendItem(localeinfo.OFFLINESHOP_SEARCH_C10, "11.dds", item.ITEM_TYPE_QUEST ,item.QUEST_NONE)

	#wnd.AppendItem(localeinfo.OFFLINESHOP_SEARCH_C8, "10.dds", 86, -1, -1, False, True)
	#wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C8, 86, item.ITEM_TYPE_QUEST ,item.QUEST_PET)
	#wnd.AppendSubCategory(localeinfo.OFFLINESHOP_SEARCH_C8, 86, item.ITEM_TYPE_QUEST ,item.QUEST_NONE)

class ListBoxCategory(ui.Window):
	class NewItem(ui.Window):
		def __init__(self, parent, icon, name, type, ForType, Subtype, IsSubCategory, ArrowShow):
			ui.Window.__init__(self)

			self.ImageSubCat = None
			self.background = None
			self.Arrow = None
			self.IconCategory = None			
			self.OnInit()

			self.Type = type
			self.ForType = ForType
			self.Subtype = Subtype
			self.IsSubCategory = IsSubCategory
			self.IsExpanded = False
			self.IsVisible = False

			if IsSubCategory == False:
				self.AppendCategory(parent.hWnd, icon, name, type, ArrowShow)
			else:
				self.AppendSubCategory(parent.hWnd, name, ForType)
				

		def OnRender(self):
			xList, yList = self.parent.GetGlobalPosition()
			widthList, heightList = self.parent.GetWidth(), self.parent.GetHeight()	
		
			images = [self.background, self.IconCategory, self.Arrow]
			for img in images:
				if img:
					img.SetClipRect(xList, yList, xList + widthList, yList + heightList)
		
			textList = [self.NameCategory]
			for text in textList:
				if text:
					xText, yText = text.GetGlobalPosition()
		
					if yText < yList or yText + text.GetTextSize()[1] > yList + heightList:
						text.Hide()
					else:
						text.Show()
		
		def AppendCategory(self, parent, icon, name, type, ArrowShow):
			self.background = ui.ExpandedImageBox()
			self.background.SetParent(self)
			self.background.LoadImage(PATH_ROOT + "category_norm.png")
			self.background.OnMouseOverIn = ui.__mem_func__(self.OnMouseOverIn2)
			self.background.OnMouseOverOut = ui.__mem_func__(self.OnMouseOverOut2)
			self.background.OnMouseLeftButtonDown = ui.__mem_func__(self.OnSelectImageBox)
			self.background.Show()
			
			self.SetSize(self.background.GetWidth(), self.background.GetHeight())

			self.IconCategory = ui.ExpandedImageBox()
			self.IconCategory.SetParent(self)
			self.IconCategory.LoadImage(PATH_ROOT + icon)
			if localeinfo.IsARABIC():
				self.IconCategory.SetPosition(144, 3)
			else:
				self.IconCategory.SetPosition(4, 3)
			self.IconCategory.Show()
		
			if ArrowShow:
				self.Arrow = ui.ExpandedImageBox()
				self.Arrow.SetParent(self.background)
				self.Arrow.LoadImage(PATH_ROOT + "arrow_down.png")
				if localeinfo.IsARABIC():
					self.Arrow.SetPosition(4, 10)
				else:
					self.Arrow.SetPosition(144, 10)
				self.Arrow.Show()

			self.NameCategory = ui.TextLine()
			self.NameCategory.SetParent(self.background)
			self.NameCategory.SetVerticalAlignCenter()
			self.NameCategory.SetWindowVerticalAlignCenter()
			self.NameCategory.SetText(name)
			if localeinfo.IsARABIC():
				self.NameCategory.SetPosition(140, -1)
			else:
				self.NameCategory.SetPosition(40, -1)
			self.NameCategory.Show()
			
			self.SubTypes = {}

		def AppendSubCategory(self, parent, name, ForType):
			self.background = ui.ExpandedImageBox()
			self.background.SetParent(self)
			self.background.LoadImage(PATH_ROOT + "sub_category_norm.png")
			self.background.OnMouseOverIn = ui.__mem_func__(self.OnMouseOverIn2)
			self.background.OnMouseOverOut = ui.__mem_func__(self.OnMouseOverOut2)
			self.background.OnMouseLeftButtonDown = ui.__mem_func__(self.OnMouseLeftButtonDown)
			self.background.SetPosition(0, 0)
			self.background.Show()
			
			self.SetSize(self.background.GetWidth() + 2, self.background.GetHeight())
		
			self.NameCategory = ui.TextLine()
			self.NameCategory.SetParent(self)
			self.NameCategory.SetText(name)
			self.NameCategory.SetPosition(0, 3)
			self.NameCategory.SetHorizontalAlignCenter()
			self.NameCategory.SetWindowHorizontalAlignCenter()
			self.NameCategory.Show()

		def SetVisible(self, flag):
			self.IsVisible = flag

		def GetItemType(self):
			return self.ForType
		
		def CanRender(self):
			if self.NameCategory.IsShow():
				return True
				
			return False
		
		def IsHide(self):
			return self.IsVisible

		def IsExpanded(self):
			return self.IsExpanded
		
		def SetSelectReset(self):
			self.selected = False
		
			if self.IsSubCategory:
				self.background.LoadImage(PATH_ROOT + "sub_category_norm.png")
			else:
				self.background.LoadImage(PATH_ROOT + "category_norm.png")
		
		def OnMouseOverIn2(self):
			if self.selected:
				return
		
			if self.IsSubCategory == False:
				if self.Arrow == None:
					self.background.LoadImage(PATH_ROOT + "category_hover.png")
				return
				
			self.background.LoadImage(PATH_ROOT + "sub_category_hover.png")
			
		def OnMouseOverOut2(self):
			if self.IsSubCategory == False:
				if self.Arrow == None:
					if self.selected:
						self.background.LoadImage(PATH_ROOT + "category_down.png")
						return
				
					self.background.LoadImage(PATH_ROOT + "category_norm.png")
				return
				
			if self.selected:
				self.background.LoadImage(PATH_ROOT + "sub_category_down.png")
			else:
				self.background.LoadImage(PATH_ROOT + "sub_category_norm.png")
		
		def OnMouseLeftButtonDown(self):
			if self.IsSubCategory == False:
				return
			
			dif = constinfo.shopSearchWaitTime - GetTime()
			if dif > 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_RENEWAL_WAIT % (str(dif)[:3]))
				return
			
			if self.clickEvent:
				self.clickEvent(self.ForType, self.Type, self.Subtype, False)
	
			self.selected = True
			self.background.LoadImage(PATH_ROOT + "sub_category_down.png")

		def OnSelectImageBox(self, bNoAct = False):
			if self.IsSubCategory:
				return

			# "ALL" (Type 0) has no subcategories -- just run the browse-all search
			if self.Type == 0:
				dif = constinfo.shopSearchWaitTime - GetTime()
				if dif > 0:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_RENEWAL_WAIT % (str(dif)[:3]))
					return
				if self.clickEvent and bNoAct == False:
					self.clickEvent(99, self.Type, 0, False)
				if self.Arrow == None:
					self.selected = True
					self.background.LoadImage(PATH_ROOT + "category_down.png")
				return

			# main category with subcategories: toggle them open/closed
			self.IsExpanded = not self.IsExpanded
			if self.Arrow:
				if self.IsExpanded:
					self.Arrow.LoadImage(PATH_ROOT + "arrow_up.dds")
				else:
					self.Arrow.LoadImage(PATH_ROOT + "arrow_down.dds")

			if self.clickEvent and bNoAct == False:
				# SelectItem hides subcategories when the flag is True, so pass the collapsed state
				self.clickEvent(99, self.Type, 0, not self.IsExpanded)

		def __del__(self):
			ui.Window.__del__(self)
			self.OnInit()

		def OnInit(self):
			self.selected = False
			self.vnum = 0
			self.xBase = 0
			self.yBase = 0

			self.overInEvent = None
			self.overOutEvent = None
			self.clickEvent = None
			self.NameCategory = None
			if self.background != None:
				self.background.Hide()
			self.background = None
			self.Arrow = None
			self.ImageSubCat = None
			self.IconCategory = None

		def SetParent(self, parent):
			ui.Window.SetParent(self, parent)
			self.parent = proxy(parent)

		def SetBasePosition(self, x, y):
			self.xBase = x
			self.yBase = y
			
		def GetBasePosition(self):
			return (self.xBase, self.yBase)
			
		def SetOverInEvent(self, event):
			self.overInEvent = event
			
		def SetOverOutEvent(self, event):
			self.overOutEvent = event
			
		def SetClickEvent(self, event):
			self.clickEvent = event
			
		def OnMouseOverIn(self):
			self.RefreshSelectState(True)
				
			if self.overInEvent:
				self.overInEvent(self.ItemVnum)
			
		def OnMouseOverOut(self):
			self.RefreshSelectState(False)
			
			if self.overOutEvent:
				self.overOutEvent()
				
		def IsSelected(self):
			return self.selected
				
		def RefreshSelectState(self, isIn):
			if not self.background:
				return
		
		def SetAnimWidth(self, width):
			self.widthAnim = width

	def __init__(self):
		ui.Window.__init__(self)
		self.OnInit()

	def __del__(self):
		ui.Window.__del__(self)
		self.OnInit()
		
	def Destroy(self):
		self.OnInit()

	def OnInit(self):
		self.SetFuncDown = None
		self.itemList = []
		self.scrollBar = None

		self.selectEvent = None
		self.selectedItemVnum = 0

	def SetEventDown(self, event):
		self.SetFuncDown = event

	def SetParent(self, parent):
		ui.Window.SetParent(self, parent)
		
	def SetScrollBar(self, scrollBar):
		scrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		scrollBar.SetScrollStep(0.2)
		self.scrollBar=scrollBar

	def SetSelectEvent(self, event):
		self.selectEvent = event

	def __OnScroll(self):
		self.AdjustItemPositions(True)

	def GetTotalItemHeight(self):
		totalHeight = 0
		
		if self.itemList:
			for itemH in self.itemList:
				totalHeight += itemH.GetHeight() + 6
			
		return totalHeight + 2

	def GetItemCount(self):
		return len(self.itemList)

	def AppendItem(self, Name, IconImage, Type, ForType = -1, Subtype = -1, IsSubCategory = False, ShowArrow = False):
		item = self.NewItem(self, IconImage, Name, Type, ForType, Subtype, IsSubCategory, ShowArrow)
		item.SetParent(self)

		# subcategories start collapsed (hidden); the main category toggles them open
		if IsSubCategory:
			item.SetVisible(True)
		
		if len(self.itemList) == 0:
			item.SetBasePosition(0, 0)
		else:
			x, y = self.itemList[-1].GetLocalPosition()
			y += 2
			item.SetBasePosition(0, y + self.itemList[-1].GetHeight())
		
		item.SetClickEvent(ui.__mem_func__(self.SelectItem))
		item.Show()
		
		self.itemList.append(item)
		
		self.AdjustScrollBar()
		self.AdjustItemPositions()

	def SelectItem(self, ForType, Type, SubType, flag):
		for itemH in self.itemList:
			if ForType == 99:
				if itemH.GetItemType() == Type:
					itemH.SetVisible(flag)

			itemH.SetSelectReset()

		self.AdjustItemPositions(True)

		if Type == 0:
			self.SetFuncDown(-1, -1)
			return
		
		PassTypes = {\
						item.ITEM_TYPE_GIFTBOX,
						item.ITEM_TYPE_USE,
						item.ITEM_TYPE_METIN,
						item.ITEM_TYPE_MATERIAL,
						item.ITEM_TYPE_BLEND,
						item.USE_ENCHANT_BODY_COSTUME,
						item.USE_ENCHANT_HAIR_COSTUME,
						item.USE_ENCHANT_WEAPON_COSTUME,
						item.ITEM_TYPE_DS,
						item.QUEST_PET,
						item.ITEM_ENCHANT,
						item.ITEM_TYPE_EX_SLOT
		}
		
		if ForType == 99 and (Type in PassTypes): 
			self.SetFuncDown(Type, -1)
			return

		if ForType != 99:
			self.SetFuncDown(Type, SubType)
		elif ForType == 99 and Type == -1:
			self.SetFuncDown(-1, -1)

	def AppendSubCategory(self, name, ForType, Type, Subtype = -1):
		self.AppendItem(name, None, Type, ForType, Subtype, 1)
	
	def AdjustScrollBar(self):
		totalHeight = float(self.GetTotalItemHeight())
		if totalHeight:
			scrollBarHeight = min(float(self.GetHeight() - 10) / totalHeight, 1.0)
		else:
			scrollBarHeight = 1.0
			
		self.scrollBar.SetMiddleBarSize(scrollBarHeight)
		
	def ResetScrollbar(self):
		self.scrollBar.SetPos(0)
				
	def AdjustItemPositions(self, scrolling = False, startIndex = -1):		
		scrollPos = self.scrollBar.GetPos()
		totalHeight = self.GetTotalItemHeight() - self.GetHeight()

		idx = 0
		if startIndex >= 0:
			idx = startIndex
		
		CurIdx, yAccumulate, FirstTab = 0, 0, False
		for item in self.itemList[idx:]:
			if startIndex >= 0:
				yAccumulate -= 20 + 2

			if item.IsHide():
				item.Hide()
				continue
			else:
				item.Show()
				
			if item.IsSubCategory == False and CurIdx > 0:
				yAccumulate += 7
				FirstTab = True
			else:
				yAccumulate += 1
				
				if FirstTab:
					yAccumulate += 5
					FirstTab = False
	
			if scrolling:
				setPos = yAccumulate - int(scrollPos * totalHeight)
				item.SetPosition(0, setPos)
			else:
				item.SetPosition(0, yAccumulate)
				
			item.SetBasePosition(0, yAccumulate)
			
			CurIdx += 1
			yAccumulate += 20

	def Clear(self):
		range = len(self.itemList)
		if range:
			for item in self.itemList:
				item.OnInit()
				item.Hide()
				del item
		
		self.itemList = []
		
	def GetList(self):
		return self.itemList


class ListBoxItem(ui.Window):
	class NewItem(ui.Window):
		def __init__(self, parent, index, data):
			ui.Window.__init__(self)
			self.background = None
			self.OnClear()
			self.Index = index
			self.InfoData = data

			Vnum = data["vnum"]
			count = data["count"]
		
			item.SelectItem(Vnum)
			_, self.itemSize = item.GetItemSize()
	
			price = data["price"]
			textYang = str(localeinfo.NumberToMoneyString(price))
			
			pid = 0

			name 	= data["owner_name"]
			seller	= name[:name.find('@')] if '@' in name else "NONAME"		
			name	= name[name.find('@')+1:] if '@' in name else name

			self.background = ui.ExpandedImageBox()
			self.background.SetParent(self)
			self.OnMouseOverOut2()
			
			self.background.OnMouseOverIn = ui.__mem_func__(self.OnMouseOverIn2)
			self.background.OnMouseOverOut = ui.__mem_func__(self.OnMouseOverOut2)
			self.background.OnMouseLeftButtonDown = ui.__mem_func__(self.OnMouseLeftButtonDown)
			self.background.Show()
			
			self.SetSize(self.background.GetWidth(), self.background.GetHeight())

			if count > 1:
				countText = str(count) + "x "
			else:
				countText = ""
				
			ItemName = item.GetItemName()
			
			if len(ItemName) >= 25:
				ItemName = ItemName[:25] + ".."

			self.ItemSlotBase = ui.ExpandedImageBox()
			self.ItemSlotBase.SetParent(self)
			self.ItemSlotBase.SetPosition(26, 0)
			self.ItemSlotBase.LoadImage(PATH + "slot_32x%d.tga" % (self.itemSize * 32))
			self.ItemSlotBase.SetWindowVerticalAlignCenter()
			self.ItemSlotBase.SAFE_SetStringEvent("MOUSE_OVER_IN", self.IconOnMouseOverIn)
			self.ItemSlotBase.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.IconOnMouseOverOut)
			#self.ItemSlotBase.SetMouseRightButtonUpEvent(ui.__mem_func__(self.IconOnRightDown), Vnum)# to do : set this to SetMouseLeftButtonUpEvent
			self.ItemSlotBase.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.IconOnRightDown), Vnum)

			self.ItemSlotBase.Show()

			self.ItemIcon = ui.ExpandedImageBox()
			self.ItemIcon.SetParent(self.ItemSlotBase)
			self.ItemIcon.AddFlag("not_pick")
			self.ItemIcon.LoadImage(item.GetIconImageFileName())
			self.ItemIcon.SetWindowVerticalAlignCenter()
			self.ItemIcon.SetWindowHorizontalAlignCenter()
			self.ItemIcon.Show()

			# item count on the slot, like inventory -- NumberLine draws the engine count digits
			if count > 0:
				self.wndItemCount = ui.NumberLine()
				self.wndItemCount.SetParent(self.ItemSlotBase)
				self.wndItemCount.AddFlag("not_pick")
				self.wndItemCount.SetWindowHorizontalAlignRight()
				self.wndItemCount.SetHorizontalAlignRight()
				self.wndItemCount.SetNumber(str(count))
				self.wndItemCount.SetPosition(3, self.ItemSlotBase.GetHeight() - 8)
				self.wndItemCount.Show()
			else:
				self.wndItemCount = None

			self.ItemIconTransmutu = ui.ExpandedImageBox()
			self.ItemIconTransmutu.SetParent(self.ItemSlotBase)
			self.ItemIconTransmutu.AddFlag("not_pick")
			self.ItemIconTransmutu.LoadImage("icon/item/ingame_convert_Mark.tga")
			self.ItemIconTransmutu.SetPosition(1, 1)
			self.ItemIconTransmutu.Hide()
			
			if data["trans"] > 0:
				self.ItemIconTransmutu.Show()

			self.wndItemName = ui.TextLine()
			self.wndItemName.SetParent(self)
			#self.wndItemName.AddFlag("not_pick")
			if localeinfo.IsARABIC():
				self.wndItemName.SetPosition(205 + 5, 0)
			else:
				self.wndItemName.SetPosition(60, 0)
			self.wndItemName.SetText(ItemName)
			self.wndItemName.SetWindowVerticalAlignCenter()
			self.wndItemName.SetVerticalAlignCenter()
			self.wndItemName.Show()

			self.wndIcon = ui.ExpandedImageBox()
			self.wndIcon.SetParent(self)
			#self.wndIcon.AddFlag("not_pick")
			self.wndIcon.LoadImage("cream/searchshop/yang.png")
			if (self.itemSize == 3):
				self.wndIcon.SetPosition(222 + 10, 15+33)
			if (self.itemSize == 2):
				self.wndIcon.SetPosition(222 + 10, 15+15)
			if (self.itemSize == 1):
				self.wndIcon.SetPosition(222 + 10, 14)
			#self.wndIcon.SetWindowHorizontalAlignRight()
			self.wndIcon.Show()

			self.wndItemPrice = ui.TextLine()
			self.wndItemPrice.SetParent(self)
			#self.wndItemPrice.AddFlag("not_pick")
			self.wndItemPrice.SetPosition(248 + 10, 0)
			self.wndItemPrice.SetText(textYang)
			self.wndItemPrice.SetOutline()
			if (price <= 100000000):
				self.wndItemPrice.SetPackedFontColor(0xfff39c12)
			else:
				self.wndItemPrice.SetPackedFontColor(0xFFd35400)
			#self.wndItemPrice.SetPackedFontColor(0xffe67e22 if textYang <= 10000000 else 0xFFFEE3AE)
			self.wndItemPrice.SetWindowVerticalAlignCenter()
			self.wndItemPrice.SetVerticalAlignCenter()
			self.wndItemPrice.SetHorizontalAlignRight()
			self.wndItemPrice.Show()

			self.Vnum = Vnum
			if app.USE_OFFLINESHOP_PRICE_AVERAGE and _IsSearchPremium():
				self.wndMarketPct = ui.TextLine()
				self.wndMarketPct.SetParent(self)
				self.wndMarketPct.AddFlag("not_pick")
				self.wndMarketPct.SetPosition(30, 12)
				self.wndMarketPct.SetText("")
				self.wndMarketPct.SetWindowHorizontalAlignCenter()
				self.wndMarketPct.SetHorizontalAlignCenter()
				self.wndMarketPct.SetWindowVerticalAlignCenter()
				self.wndMarketPct.SetVerticalAlignCenter()
				self.wndMarketPct.Show()
			else:
				self.wndMarketPct = None

			self.CheckBox = ui.ExpandedImageBox()
			self.CheckBox.SetParent(self)
			self.CheckBox.SetPosition(6, 0)
			self.CheckBox.LoadImage(PATH_ROOT + "box_uncheck.png")
			self.CheckBox.SetWindowVerticalAlignCenter()
			self.CheckBox.OnMouseLeftButtonDown = ui.__mem_func__(self.OnCheckBox)
			self.CheckBox.Show()
	
			self.wndSellerName = ui.TextLine()
			self.wndSellerName.SetParent(self)
			self.wndSellerName.AddFlag("not_pick")
			if localeinfo.IsARABIC():
				self.wndSellerName.SetPosition(150 , 0)
			else:
				self.wndSellerName.SetPosition(13, 0)
			self.wndSellerName.SetText(str(seller))
			self.wndSellerName.SetWindowHorizontalAlignRight()
			self.wndSellerName.SetHorizontalAlignRight()
			self.wndSellerName.SetWindowVerticalAlignCenter()
			self.wndSellerName.SetVerticalAlignCenter()
			self.wndSellerName.Show()

			self.IconWhisperSeller = ui.MakeButton(self, 45 - 10, 2, "", PATH_ROOT, "whisper_btn_norm.png", "whisper_btn_hover.png", "whisper_btn_select.png")
			self.IconWhisperSeller.SetWindowHorizontalAlignRight()
			self.IconWhisperSeller.SetWindowVerticalAlignCenter()
			self.IconWhisperSeller.SetEvent(ui.__mem_func__(self.OnMouseLeftWhisperSeller))

			# open the seller's shop -- a Button (TextLine can't take a click or tooltip; Button can)
			self.btnVisitShop = ui.MakeButton(self, 72 - 10, 1, localeinfo.OFFLINESHOP_SEARCH_VISIT_SHOP, PATH_ROOT, "player_shop_norm.png", "player_shop_hover.png", "player_shop_down.png")
			self.btnVisitShop.SetWindowHorizontalAlignRight()
			self.btnVisitShop.SetWindowVerticalAlignCenter()
			self.btnVisitShop.SetEvent(ui.__mem_func__(self.OnOpenSellerShop))
			
			if self.InfoData["id"] in SELECTED_ITEMS_BUY:
				self.IsSelected = True
				self.CheckBox.LoadImage(PATH_ROOT + "box_checked.png")
				
			self.OnMouseOverOut2()

		def OnRender(self):
			xList, yList = self.parent.GetGlobalPosition()
			widthList, heightList = self.parent.GetWidth(), self.parent.GetHeight()	
		
			images = [self.background, self.CheckBox, self.ItemSlotBase, self.ItemIcon, self.ItemIconTransmutu, self.wndIcon]
			for img in images:
				if img:
					img.SetClipRect(xList, yList, xList + widthList, yList + heightList)
		
			textList = [self.wndItemName, self.wndItemPrice, self.wndSellerName]
			if getattr(self, "wndMarketPct", None):
				textList.append(self.wndMarketPct)
			if getattr(self, "wndItemCount", None):
				cy = self.wndItemCount.GetGlobalPosition()[1]
				if cy < yList or cy + 12 > yList + heightList:
					self.wndItemCount.Hide()
				else:
					self.wndItemCount.Show()
			for text in textList:
				if text:
					xText, yText = text.GetGlobalPosition()
		
					if yText < yList or yText + text.GetTextSize()[1] > yList + heightList:
						text.Hide()
					else:
						text.Show()

			if getattr(self, "btnVisitShop", None):
				bx, by = self.btnVisitShop.GetGlobalPosition()
				if by < yList or by + self.btnVisitShop.GetHeight() > yList + heightList:
					self.btnVisitShop.Hide()
				else:
					self.btnVisitShop.Show()

			if getattr(self, "IconWhisperSeller", None):
				wx, wy = self.IconWhisperSeller.GetGlobalPosition()
				if wy < yList or wy + self.IconWhisperSeller.GetHeight() > yList + heightList:
					self.IconWhisperSeller.Hide()
				else:
					self.IconWhisperSeller.Show()

		def SetMarketAverage(self, avg):
			if not getattr(self, "wndMarketPct", None):
				return
			try:
				avg = long(avg)
			except:
				return
			if avg <= 0:
				self.wndMarketPct.SetText("")
				return
			price = self.InfoData.get("price", 0)
			pct = int(round(100.0 * float(price) / float(avg)))
			self.wndMarketPct.SetText("%d%%" % pct)
			if pct < 95:
				self.wndMarketPct.SetPackedFontColor(0xFF2ecc71)
			elif pct > 105:
				self.wndMarketPct.SetPackedFontColor(0xFFe74c3c)
			else:
				self.wndMarketPct.SetPackedFontColor(0xFFbdc3c7)

		def OnMouseOverIn2(self):
			self.background.LoadImage(PATH_ROOT + "field_%d_selected.png" % (self.itemSize))

		def OnMouseOverOut2(self):
			if self.IsSelected:
				self.background.LoadImage(PATH_ROOT + "field_%d_selected.png" % (self.itemSize))
				return
		
			colorField = "black"
			if self.Index % 2 == 0:
				colorField = "white"
		
			self.background.LoadImage(PATH_ROOT + "field_%d_%s.png" % (self.itemSize, colorField))

		def SetBlock(self):
			self.bIsBlocked = True
		
		def OnCheckBox(self):
			if self.IsSelected:
				self.IsSelected = False
				self.CheckBox.LoadImage(PATH_ROOT + "box_uncheck.png")
				
				if self.InfoData["id"] in SELECTED_ITEMS_BUY:
					del SELECTED_ITEMS_BUY[self.InfoData["id"]]
			else:
				self.IsSelected = True
				self.CheckBox.LoadImage(PATH_ROOT + "box_checked.png")

				SELECTED_ITEMS_BUY[self.InfoData["id"]] = self.InfoData["owner"]
				
			self.OnMouseOverOut2()
		
		def OnMouseLeftWhisperSeller(self):
			if self.WhisperEvent:
				self.WhisperEvent(self.wndSellerName.GetText())

		def OnOpenSellerShop(self):
			# open that seller's full shop (reuses the shop-hyperlink open-by-owner)
			pid = self.InfoData.get("owner", 0)
			if pid:
				offlineshop.SendOpenShop(pid)

		def OnMouseLeftButtonDown(self):
			if self.clickEvent:
				self.clickEvent(self.InfoData["owner"], self.InfoData["id"], self.wndItemName.GetText(), self.InfoData["price"])


		def __del__(self):
			ui.Window.__del__(self)
			self.OnClear()

		def OnClear(self):
			self.IsSelected = False
			self.bIsBlocked = False
			self.vnum = 0
			self.xBase = 0
			self.yBase = 0

			self.overInEventIconImage = None
			self.overOutEventIconImage = None
			self.clickEvent = None
			self.WhisperEvent = None
			if self.background != None:
				self.background.Hide()
			self.background = None
			self.CheckBox = None
			self.ItemSlotBase = None
			self.wndIcon = None

		def SetParent(self, parent):
			ui.Window.SetParent(self, parent)
			self.parent = proxy(parent)

		def SetBasePosition(self, x, y):
			self.xBase = x
			self.yBase = y
			
		def GetBasePosition(self):
			return (self.xBase, self.yBase)
			
		def SetOverInEvent(self, event):
			self.overInEventIconImage = event
			
		def SetOverOutEvent(self, event):
			self.overOutEventIconImage = event
			
		def SetClickEvent(self, event):
			self.clickEvent = event

		def SetWhisperEvent(self, event):
			self.WhisperEvent = event
			
		def IconOnMouseOverIn(self):
			if self.overInEventIconImage:
				self.overInEventIconImage(self.InfoData)
			
		def IconOnMouseOverOut(self):
			if self.overOutEventIconImage:
				self.overOutEventIconImage()

		def IconOnRightDown(self, itemVnum = 0):
			if itemVnum == 0:
				return
			if app.ENABLE_RENDER_TARGET and\
				app.IsPressed(app.DIK_LSHIFT):
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler and interfaceHandler.tooltipItem:
					if uiRenderTarget.IsCanShowItems(itemVnum):
						itemTransmutedVnum = player.GetChangeLookVnum(itemVnum)#to do : fix transmutation we need to specify the slot index
						interfaceHandler.OpenRenderTargetWindow(0, itemTransmutedVnum if itemTransmutedVnum else itemVnum)

	def __init__(self):
		ui.Window.__init__(self)
		
		self.tooltipItem = uitooltip.ItemToolTip()
		self.tooltipItem.Hide()
		
		self.OnClear(0)

	def __del__(self):
		ui.Window.__del__(self)
		self.OnClear()
		#
		#self.tooltipItem = None

	def Destroy(self):
		#self.tooltipItem = None
		self.OnClear()

	def OnClear(self, bFlag = 1):
		if bFlag == 1 and\
			self.tooltipItem:
			self.tooltipItem.HideToolTip()
			del self.tooltipItem
			self.tooltipItem=0
		
		self.SetFuncDown = None
		self.BuyAskEvent = None
		self.WhishperEventFunc = None
		self.itemList = []
		self.scrollBar = None

		self.selectEvent = None
		self.selectedItemVnum = 0

	def SetEventBuy(self, event):
		self.BuyAskEvent = event

	def SetEventWhisper(self, event):
		self.WhishperEventFunc = event

	def SetParent(self, parent):
		ui.Window.SetParent(self, parent)
		
		self.SetPosition(5, 5)
		self.SetSize(parent.GetWidth() - 10, parent.GetHeight() - 10)
		
	def SetScrollBar(self, scrollBar):
		scrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		scrollBar.SetScrollStep(0.2)
		self.scrollBar=scrollBar

	def SetSelectEvent(self, event):
		self.selectEvent = event
		
	def __OnScroll(self):
		self.AdjustItemPositions(True)
			
	def GetTotalItemHeight(self):
		totalHeight = 0
		
		if self.itemList:
			for itemH in self.itemList:
				if itemH.bIsBlocked:
					continue
				totalHeight += itemH.GetHeight() + 2
			
		return totalHeight

	def GetItemCount(self):
		return len(self.itemList)

	def AppendItem(self, index, infoData):
		item = self.NewItem(self, index, infoData)
		item.SetParent(self)

		if len(self.itemList) == 0:
			item.SetBasePosition(0, 0)
		else:
			x, y = self.itemList[-1].GetLocalPosition()
			y += 2
			item.SetBasePosition(0, y + self.itemList[-1].GetHeight())

		item.SetWhisperEvent(ui.__mem_func__(self.OnWhisperName))
		item.SetClickEvent(ui.__mem_func__(self.SelectItem))
		item.SetOverInEvent(ui.__mem_func__(self.OverInItem))
		item.SetOverOutEvent(ui.__mem_func__(self.OverOutItem))		
	
		item.Show()
		self.itemList.append(item)

		self.ResetScrollbar()
		self.AdjustScrollBar()	
		self.AdjustItemPositions()
	
	def OnWhisperName(self, name):
		if self.WhishperEventFunc:
			self.WhishperEventFunc(name)
	
	def OverInItem(self, data):#try
		if self.tooltipItem and data:
			self.tooltipItem.ClearToolTip()
			
			sockets = [data["socket"][num] for num in xrange(player.METIN_SOCKET_MAX_NUM)]
			attrs	= [(data["attr"][num]['type'], data["attr"][num]['value']) for num in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
			if app.ENABLE_APPLY_RANDOM_SHOP:
				itemApplyList=[(data["rand"][num]["type"], data["rand"][num]["value"], data["rand"][num]["path"]) for num in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]

			transmutation = data["trans"]
			if app.ENABLE_SET_ITEM:
				setItem = data["setItem"]

			if app.USE_ENCHANT_COSTUMES:
				itemEnchantList=[(data["enchant"][num]["type"], data["enchant"][num]["value"], data["enchant"][num]["time"]) for num in xrange(player.ENCHANT_SLOT_MAX_NUM)]

			restrictInfo = None
			if app.ENABLE_EQUIPMENT_RESTRICTION and data.has_key("restrict"):
				restrictInfo = data["restrict"]

			self.tooltipItem.AddItemData(data["vnum"], sockets, attrs, None, 0, 0, player.INVENTORY, -1, None, itemApplyList, 0, transmutation,enchantList=itemEnchantList,iSetValue = setItem, restrictInfo = restrictInfo)

	def OverOutItem(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def SelectItem(self, pID, ItemPos, ItemName, itemPrice):
		if self.BuyAskEvent:
			self.BuyAskEvent(pID, ItemPos, ItemName, itemPrice)

	def AdjustScrollBar(self):
		totalHeight = float(self.GetTotalItemHeight())
		if totalHeight:
			scrollBarHeight = min(float(self.GetHeight() - 10) / totalHeight, 1.0)
		else:
			scrollBarHeight = 1.0
			
		self.scrollBar.SetMiddleBarSize(scrollBarHeight)
	
	def ResetScrollbar(self):
		self.scrollBar.SetPos(0)
				
	def AdjustItemPositions(self, scrolling = False):		
		scrollPos = self.scrollBar.GetPos()
		totalHeight = self.GetTotalItemHeight() - self.GetHeight()

		idx = 0

		CurIdx, yAccumulate = 0, 0
		for item in self.itemList[idx:]:
			if item.bIsBlocked:
				continue
			
			if scrolling:
				setPos = yAccumulate - int(scrollPos * totalHeight)
				item.SetPosition(0, setPos)
			else:
				item.SetPosition(0, yAccumulate)
				
			item.SetBasePosition(0, yAccumulate)

			CurIdx += 1
			yAccumulate += item.GetHeight() + 2

	def Clear(self):
		range = len(self.itemList)
		
		if range > 0:
			for item in self.itemList:
				item.OnClear()
				item.Hide()
				del item
		
		self.itemList = []
		
	def RemoveItemBought(self, bOwner, bId):
		range = len(self.itemList)
		
		if range > 0:
			for i in xrange(range):
				owner = self.itemList[i].InfoData["owner"]
				id = self.itemList[i].InfoData["id"]
				if owner == bOwner and id == bId:
					self.itemList[i].IsSelected = False
					self.itemList[i].Hide()
					self.itemList[i].SetBlock()
					break
				
			self.ReloadSymmetryBackground()
			self.ResetScrollbar()
			self.AdjustScrollBar()
			self.AdjustItemPositions(True)
	
	def ReloadSymmetryBackground(self):
		range = len(self.itemList)
		
		if range > 0:
			CntIndex = 0
			for i in xrange(range):
				if self.itemList[i].bIsBlocked:
					continue

				colorField = "black"
				if CntIndex % 2 == 0:
					colorField = "white"
				
				self.itemList[i].background.LoadImage(PATH_ROOT + "field_%d_%s.png" % (self.itemList[i].itemSize, colorField))
				
				self.itemList[i].OnMouseOverOut2()
				
				CntIndex += 1

	def GetItemPrice(self, owner, itemID):
		for itemH in self.itemList:
			ownerItem = itemH.InfoData["owner"]
			idItem = itemH.InfoData["id"]
			if ownerItem == owner and itemID == idItem:
				return itemH.InfoData["price"]
		
		return 0


	def BuySelectedItems(self):
		global SELECTED_ITEMS_BUY
		range = len(SELECTED_ITEMS_BUY)
		
		if range > 0:
			for id_key in SELECTED_ITEMS_BUY:
				owner = SELECTED_ITEMS_BUY[id_key]
				offlineshop.SendBuyItemFromSearch(owner, id_key, self.GetItemPrice(owner, id_key))

class ShopSearch(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.loaded = 0
		self.iCountEnd = 0
		self.currentPage = 1
		self.interface = None
		self.dlgBuyQuestion = None
		self.ListBox = None
		self.CategoryList = None
		self.SearchFilterShopItemResult = []
		self.lastWasByName = 0
		self._liveSearchPending = False
		self._liveSearchAt = 0
		self._lastLiveSearchText = None
		self.LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.ClearDictionary()
		if self.ListBox:
			self.ListBox.Destroy()
			self.ListBox.Clear()
			del self.ListBox
			
		if self.CategoryList:
			self.CategoryList.Clear()
			del self.CategoryList
	
	def Show(self):
		# >>> SECTION BEGIN offlineshop search rework: opening never waits <<<
		# Opening sends nothing to the server, so it must not be gated by the search cooldown a
		# prior search armed -- this was the "open then close fast and you have to wait" bug.
		# dif = constinfo.shopSearchWaitTime-GetTime()
		# if dif > 0:
		#	chat.AppendChat(chat.CHAT_TYPE_INFO,localeinfo.OFFLINESHOP_RENEWAL_WAIT % (str(dif)[:3]))
		#	return
		# >>> SECTION END <<<
		
		self.LoadWindow()
		self.SetCenterPosition()
		self.Clear()
		
		if self.CategoryList:
			# >>> SECTION BEGIN offlineshop search rework: load ALL on open (one search, no burst) <<<
			# Opening used to auto-expand EVERY top-level category, each firing its own filter request
			# -- the first armed the cooldown, the rest spammed "please wait", and reopening was blocked.
			# Now we reset the category strip and fire a SINGLE ALL-items search: OnSearchByValue(-1,-1)
			# is the ALL category (browse-all); byPass=True ignores the debounce so opening always loads.
			# Original per-category auto-expand was:
			#	for item in self.CategoryList.itemList:
			#		if item.Type == 0:
			#			item.OnSelectImageBox()
			#		else:
			#			item.SetSelectReset()
			for item in self.CategoryList.itemList:
				item.SetSelectReset()
			# ease-of-use: remember last search -> re-run it on reopen (else default to ALL)
			last = getattr(self, "SearchFilterLastUsedSetting", None)
			if last:
				self.sCategory = last[0]
				self.sSubCategory = last[1]
				offlineshop.SendFilterRequest(*last)
				self.currentPaginationPage = 1
			else:
				self.OnSearchByValue(-1, -1, True, True)
			# >>> SECTION END <<<
		
		ui.ScriptWindow.Show(self)

	def Clear(self):
		self.sLastItemName = None
		self.sCategory = -1
		self.sSubCategory = -1
		self.iPage = 1
		self.iCountEnd = 0
		self.ItemList.Clear()
		self.bCantChangePage = False
		self.FloodPage = 0

	def LoadWindow(self):
		if self.loaded == 1:
			return

		self.loaded = 1		
		self.AddFlag("movable")
		
		self.Board = ui.MakeBoardWithTitleBar(self, "not_pick", localeinfo.OFFLINESHOP_SEARCH, ui.__mem_func__(self.CloseGame), 730, 537)

		self.BoardListBox = ui.MakeImageBox(self.Board, "cream/shopeditor/category_board.png", 17, 35)
		self.BoardItemList = ui.MakeImageBox(self.Board, "cream/shopeditor/item_board.png", 210, 35)

		self.SetSize(self.Board.GetWidth(), self.Board.GetHeight())
		
		self.btnBuySelectedItems = ui.MakeButton(self, 226, 503, False, PATH_ROOT, "btn_filter_norm.png", "btn_filter_hover.png", "btn_filter_down.png")
		self.btnBuySelectedItems.SetText(localeinfo.OFFLINESHOP_SEARCH_BUY)

		self.LineSearch = ui.MakeImageBox(self.Board, "cream/shopeditor/field_time.png", 27, 45)

		self.sItemName = ui.EditLine()
		self.sItemName.SetParent(self.LineSearch)
		self.sItemName.SetMax(45)
		self.sItemName.SetSize(111 - self.LineSearch.GetWidth() - 2, 15)
		if localeinfo.IsARABIC():
			self.sItemName.SetPosition(2+120, 4)
			self.sItemName.SetOverlayTextAE(localeinfo.OFFLINESHOP_SEARCH_NAME)
		else:
			self.sItemName.SetPosition(2, 4)
			self.sItemName.SetOverlayText(localeinfo.OFFLINESHOP_SEARCH_NAME)
		self.sItemName.SetLimitWidth(self.LineSearch.GetWidth())
		self.sItemName.SetEscapeEvent(ui.__mem_func__(self.OnPressNameEscapeKey))
		self.sItemName.SetUpdateEvent(ui.__mem_func__(self.Search_RefreshTextHint))
		self.sItemName.SetTabEvent(ui.__mem_func__(self.OnSearchTab))
		self.sItemName.SetReturnEvent(ui.__mem_func__(self.OnSearchReturn))
		self.sItemName.SetOutline()
		self.sItemName.Show()

		self.searchEditHint = ui.TextLine()
		self.searchEditHint.SetParent(self.sItemName)
		self.searchEditHint.SetPackedFontColor(grp.GenerateColor(1.0, 1.0, 1.0, 0.5))
		self.searchEditHint.SetPosition(-15, 15)
		self.searchEditHint.Show()

		self.searchDropdown = None

		self.btnSearch = ui.MakeButton(self.Board, 135, 45, False, PATH_ROOT, "btn_search_norm.png", "btn_search_hover.png", "btn_search_down.png")
		self.btnSearch.SetEvent(ui.__mem_func__(self.OnSearch))

		self.btnEmptySearch = ui.MakeButton(self.Board, 165, 45, False, PATH_ROOT, "btn_reset_search_norm.png", "btn_reset_search_hover.png", "btn_reset_search_down.png")
		self.btnEmptySearch.SetEvent(ui.__mem_func__(self.OnResetSearch))
		self.btnEmptySearch.SetToolTipText(localeinfo.SEARCH_SHOP_RESET)
		self.btnBuySelectedItems.SetEvent(ui.__mem_func__(self.AskBuySelectedItems))

		self.ItemList = ListBoxItem()
		self.ItemList.SetParent(self.BoardItemList)
		self.ItemList.SetSize(502, 460)
		self.ItemList.SetPosition(2, 2)
		self.ItemList.SetEventBuy(ui.__mem_func__(self.AskBuySelectedItem))
		self.ItemList.SetEventWhisper(ui.__mem_func__(self.OnWhisper))
		self.ItemList.Show()
	
		self.ScrollBar = ui.ScrollBarNew()
		self.ScrollBar.allow_on_run_mouse_wheel = False
		self.ScrollBar.SetParent(self)
		self.ScrollBar.SetScrollBarSize(464)
		self.ScrollBar.SetPosition(708, 35)
		self.ItemList.SetScrollBar(self.ScrollBar)
		self.ScrollBar.Show()

		self.wndResultCount = ui.TextLine()
		self.wndResultCount.SetParent(self.Board)
		self.wndResultCount.SetPosition(25, 512)
		self.wndResultCount.SetText("")
		self.wndResultCount.Show()

		self.wndEmptyState = ui.TextLine()
		self.wndEmptyState.SetParent(self.BoardItemList)
		self.wndEmptyState.SetWindowHorizontalAlignCenter()
		self.wndEmptyState.SetHorizontalAlignCenter()
		self.wndEmptyState.SetPosition(0, 200)
		self.wndEmptyState.SetText(localeinfo.OFFLINESHOP_SEARCH_EMPTY)
		self.wndEmptyState.Hide()
		
		self.MakeCategory()

		self.nextButton = ui.MakeButton(self, 50 + 453 + 130, 293 + 210, False, PATH_ROOT, "btn_page_norm.png", "btn_page_hover.png", "btn_page_down.png")
		self.nextButton.SetText("<")
		
		self.lastButton = ui.MakeButton(self, 50 + 483 + 130, 293 + 210, False, PATH_ROOT, "btn_page_norm.png", "btn_page_hover.png", "btn_page_down.png")
		self.lastButton.SetText("<<")
		
		self.prevButton = ui.MakeButton(self, 50 + 260-20 + 130, 293 + 210, False, PATH_ROOT, "btn_page_norm.png", "btn_page_hover.png", "btn_page_down.png")
		self.prevButton.SetText(">")
		
		self.firstButton = ui.MakeButton(self, 50 + 230-20 + 130, 293 + 210, False, PATH_ROOT, "btn_page_norm.png", "btn_page_hover.png", "btn_page_down.png")
		self.firstButton.SetText(">>")

		self.pageButtons = []
		self.pageButtons.append(ui.MakeButton(self, 50 + 275-10 + 130 + 5, 293 + 210, False, PATH_ROOT, "btn_page_norm.png", "btn_page_hover.png", "btn_page_down.png"))
		self.pageButtons.append(ui.MakeButton(self, 50 + 310-10 + 130 + 5, 293 + 210, False, PATH_ROOT, "btn_page_norm.png", "btn_page_hover.png", "btn_page_down.png"))
		self.pageButtons.append(ui.MakeButton(self, 50 + 345-10 + 130 + 5, 293 + 210, False, PATH_ROOT, "btn_page_norm.png", "btn_page_hover.png", "btn_page_down.png"))
		self.pageButtons.append(ui.MakeButton(self, 50 + 380-10 + 130 + 5, 293 + 210, False, PATH_ROOT, "btn_page_norm.png", "btn_page_hover.png", "btn_page_down.png"))
		self.pageButtons.append(ui.MakeButton(self, 50 + 415-10 + 130 + 5, 293 + 210, False, PATH_ROOT, "btn_page_norm.png", "btn_page_hover.png", "btn_page_down.png"))

		for index, item in enumerate(self.pageButtons):
			item.SetText(str(index + 1))

		self.pageButtons[0].Show()
		self.pageButtons[1].Hide()
		self.pageButtons[2].Hide()
		self.pageButtons[3].Hide()
		self.pageButtons[4].Hide()
		self.pageButtons[0].Down()
		self.pageButtons[0].Disable()

		self.nextButton.SetEvent(ui.__mem_func__(self.NextPage))
		self.prevButton.SetEvent(ui.__mem_func__(self.PrevPage))
		self.firstButton.SetEvent(ui.__mem_func__(self.FirstPage))
		self.lastButton.SetEvent(ui.__mem_func__(self.LastPage))

		self.textInfoCheckBox = ui.TextLine()
		self.textInfoCheckBox.SetParent(self)
		if localeinfo.IsARABIC():
			self.textInfoCheckBox.SetPosition(38 + 21+90, 77 + 1)
		else:
			self.textInfoCheckBox.SetPosition(38 + 21, 77 + 1)
		self.textInfoCheckBox.SetText(localeinfo.OFFLINESHOP_SEARCH_BYNAME)
		self.textInfoCheckBox.Show()

		self.CheckBox = ui.ExpandedImageBox()
		self.CheckBox.SetParent(self)
		if localeinfo.IsARABIC():
			self.CheckBox.SetPosition(38+120, 77)
		else:
			self.CheckBox.SetPosition(38, 77)
		self.CheckBox.LoadImage(PATH_ROOT + "box_uncheck.png")
		self.CheckBox.IsChecked = False
		self.CheckBox.OnMouseLeftButtonDown = ui.__mem_func__(self.OnCheckBox)
		self.CheckBox.Show()

		self.btnFilter = ui.MakeButton(self, 26, 100, False, PATH_ROOT, "btn_filter_norm.png", "btn_filter_hover.png", "btn_filter_down.png")
		self.btnFilter.SetEvent(ui.__mem_func__(self.OnFilterManage)) # changeme with 
		self.btnFilter.SetText(localeinfo.SEARCH_SHOP_FILTER)

		self.btnResetFilter = ui.MakeButton(self, 170, 100, False, PATH_ROOT, "btn_reset_filter_norm.png", "btn_reset_filter_hover.png", "btn_reset_filter_down.png")
		self.btnResetFilter.SetEvent(ui.__mem_func__(self.OnFilterReset)) # changeme with 
		self.btnResetFilter.SetToolTipText(localeinfo.SEARCH_SHOP_FILTER_RESET)

		## NEW CODE FILTER
		self.boardFilter = ui.Window()
		self.boardFilter.SetParent(self)
		self.boardFilter.SetSize(197, 400)
		self.boardFilter.SetPosition(20, 145)		
		self.boardFilter.isExpand = False
		self.boardFilter.Hide()
		
		self.CreateFilterItems()

		self.attributeSearchWindow = None
		self.attrDict = {}
		for i in xrange(5):
			attr = uiswitchbot.SwitchbotAttribute()
			attr.SetParent(self.BoardItemList)
			attr.Create(250, i)
			attr.SetPosition(3, 320 + (27 * i))
			attr.SetSearchEvent(ui.__mem_func__(self.__OnSearchAttribute))
			attr.attributeUpdateEvent = None
			attr.SetEscapeEvent(ui.__mem_func__(self.Close))
			attr.keyAttr = 0
			attr.Hide()
			
			self.attrDict[i] = attr
			
		# self.wndFilterWarrior = self.CreateFilterRadioButton("", 22 + 33 - 16, 94 + 5, "warrior_no_select.dds", "warrior_select.dds", "warrior_select.dds")
		# self.wndFilterAssassin = self.CreateFilterRadioButton("", 22 + 68 - 16, 94 + 5, "assassin_no_select.dds", "assassin_select.dds", "assassin_select.dds")
		# self.wndFilterSura = self.CreateFilterRadioButton("", 22 + 68 + 35 - 16, 94 + 5, "sura_no_select.dds", "sura_select.dds", "sura_select.dds")
		# self.wndFilterShaman = self.CreateFilterRadioButton("", 22 + 68 + 35 + 35 - 16, 94 + 5, "shaman_no_select.dds", "shaman_select.dds", "shaman_select.dds")

		# Wiki-style live item-name dropdown -- created LAST so it renders above every panel/scrollbar.
		if app.ENABLE_INGAME_WIKI:
			try:
				import ingamewikisearch
				self.searchDropdown = ingamewikisearch.WikiSearchResults(width = max(self.sItemName.GetWidth() + 60, 180), itemsOnly = True)
				self.searchDropdown.SetParent(self)
				self.searchDropdown.SetPosition(0, 0)
				self.searchDropdown.SetPickEvent(ui.__mem_func__(self.OnSearchNamePicked))
				self.searchDropdown.Hide()
			except Exception:
				self.searchDropdown = None

	def OnCheckBox(self):
		if self.CheckBox.IsChecked:
			self.CheckBox.IsChecked = False
			self.CheckBox.LoadImage(PATH_ROOT + "box_uncheck.png")
		else:
			self.CheckBox.IsChecked = True
			self.CheckBox.LoadImage(PATH_ROOT + "box_checked.png")
			
		self.Search_RefreshTextHint()
	
	def CreateFilterRadioButton(self, text, x, y, up, over, down):
		button = ui.ToggleButton()
		button.SetParent(self)
		button.SetPosition(x, y)
		button.SetUpVisual(PATH + "filter/" + up)
		button.SetOverVisual(PATH + "filter/" + over)
		button.SetDownVisual(PATH + "filter/" + down)
		button.SetToolTipText(text)
		button.SetToggleUpEvent(ui.__mem_func__(self.OnFilterButtonDown), button)
		button.SetToggleDownEvent(ui.__mem_func__(self.OnFilterButtonSetUp), button)
		button.Show()
		
		button.Down()
		
		return button
	
	def OnFilterButtonDown(self, wnd):
		wnd.SetUp()
		
	def OnFilterButtonSetUp(self, wnd):
		wnd.Down()

	def OnPressNameEscapeKey(self):
		# if not self.sItemName:
			# return
		
		if not self.sItemName.IsShowCursor() or self.sItemName.GetText() == "":
			self.OnPressEscapeKey()
		else:
			self.sItemName.SetText("")
			self.searchEditHint.SetText("")
		if self.searchDropdown:
			self.searchDropdown.Hide()

	def Search_CompleteTextSearch(self):
		if self.searchEditHint.GetText():
			oldText = self.sItemName.GetText()
			self.sItemName.SetText(oldText + self.searchEditHint.GetText()[len(oldText)+1:])
			self.sItemName.SetEndPosition()
			self.Search_RefreshTextHint()

	def Search_RefreshTextHint(self):
		EDIT_TEXT_BASE_COLOR = grp.GenerateColor(0.8549, 0.8549, 0.8549, 1.0)
		EDIT_TEXT_NOT_FOUND_COLOR = grp.GenerateColor(1.0, 0.2, 0.2, 1.0)
		
		self.searchEditHint.SetText("")
		self.sItemName.SetPackedFontColor(EDIT_TEXT_BASE_COLOR)
		
		search_text = self.sItemName.GetText()
		
		if len(search_text) and self.CheckBox.IsChecked == False:
			(hintName, vnum) = item.GetItemDataByNamePart(search_text)
			
			if vnum == -1:
				self.searchEditHint.SetText("")
				self.sItemName.SetPackedFontColor(EDIT_TEXT_NOT_FOUND_COLOR)
			else:
				self.searchEditHint.SetText(search_text + " " + hintName[len(search_text):])

		if self.searchDropdown:
			if len(search_text) and self.CheckBox.IsChecked == False:
				bx, by = self.sItemName.GetGlobalPosition()
				sx, sy = self.GetGlobalPosition()
				self.searchDropdown.SetPosition(bx - sx, by - sy + self.sItemName.GetHeight() + 2)
				self.searchDropdown.Refresh(search_text)
			else:
				self.searchDropdown.Hide()

		# live results: re-run the shop search shortly after the user stops typing
		self._liveSearchPending = True
		self._liveSearchAt = GetTime() + 0.35

	def OnSearchNamePicked(self, vnum, isMob):
		# wiki-style dropdown pick -> fill the box with the item name and run the search
		if self.searchDropdown:
			self.searchDropdown.Hide()
		item.SelectItem(vnum)
		name = item.GetItemName()
		if name:
			self.sItemName.SetText(name)
			self.sItemName.SetEndPosition()
			self.searchEditHint.SetText("")
		self.OnSearch()

	def OnSearchReturn(self):
		# Enter: pick the highlighted dropdown item (fills name + searches); else normal search.
		if self.searchDropdown and self.searchDropdown.IsShow():
			if self.searchDropdown.PickFirst():
				return
		self.OnSearch()

	def OnSearchTab(self):
		# Tab: fill the box with the highlighted item name WITHOUT searching.
		if self.searchDropdown and self.searchDropdown.IsShow():
			vnum = self.searchDropdown.GetHighlightedVnum()
			if vnum:
				item.SelectItem(vnum)
				name = item.GetItemName()
				if name:
					self.sItemName.SetText(name)
					self.sItemName.SetEndPosition()
					self.searchEditHint.SetText("")
					self.searchDropdown.Hide()
					return
		self.Search_CompleteTextSearch()


	def OnRunMouseWheel(self, nLen):
		if self.ScrollBarCategory and self.ScrollBarCategory.IsShow():
			if self.ScrollBarCategory.IsInPosition() or self.CategoryList.IsInPosition():
				if nLen > 0:
					self.ScrollBarCategory.OnUp()
				else:
					self.ScrollBarCategory.OnDown()

				return True

		if self.ScrollBar and self.ScrollBar.IsShow():
			if self.ScrollBar.IsInPosition() or self.ItemList.IsInPosition():
				if nLen > 0:
					self.ScrollBar.OnUp()
				else:
					self.ScrollBar.OnDown()

				return True

		return False

	def MakeCategory(self):
		self.ScrollBarCategory = ui.ScrollBarNew()
		self.ScrollBarCategory.allow_on_run_mouse_wheel = False
		self.ScrollBarCategory.SetParent(self)
		self.ScrollBarCategory.SetScrollBarSize(380)
		self.ScrollBarCategory.SetPosition(193, 136)
		self.ScrollBarCategory.Show()

		self.CategoryList = ListBoxCategory()
		self.CategoryList.SetParent(self.BoardListBox)
		self.CategoryList.SetSize(self.BoardListBox.GetWidth(), self.BoardListBox.GetHeight() - 110)
		self.CategoryList.SetPosition(6, 100)
		self.CategoryList.SetScrollBar(self.ScrollBarCategory)
		self.CategoryList.SetEventDown(ui.__mem_func__(self.OnSearchByValue))
		self.CategoryList.Show()
		
		self.CategoryList.AppendItem(localeinfo.OFFLINESHOP_SEARCH_ALL, "0.png", 0)
		
		SetCategories(self.CategoryList)

	def OnWhisper(self, name):
		if self.interface:
			self.interface.OpenWhisperDialog(name)

	def SetInterface(self, interface):
		self.interface = interface

	def SearchFilter_BuyFromSearch(self, ownerid, itemid):
		self.ItemList.RemoveItemBought(ownerid, itemid)
		
		for item in self.SearchFilterShopItemResult:
			if item['id'] == itemid and item['owner'] == ownerid:
				self.SearchFilterShopItemResult.remove(item)
				break
		
		global SELECTED_ITEMS_BUY
		SELECTED_ITEMS_BUY = {}

	def AskBuySelectedItems(self):
		global SELECTED_ITEMS_BUY
		count = len(SELECTED_ITEMS_BUY)
	
		self.BuyQuestionCancel()

		dlgBuyQuestion = uicommon.QuestionDialog()
		total = 0
		for id_key in SELECTED_ITEMS_BUY:
			total += self.ItemList.GetItemPrice(SELECTED_ITEMS_BUY[id_key], id_key)
		dlgBuyQuestion.SetText(localeinfo.OFFLINESHOP_SEARCH_BUYALL_TOTAL % (count, localeinfo.NumberToMoneyString(total)))
		dlgBuyQuestion.SetAcceptEvent(ui.__mem_func__(self.BuySelectedItems))
		dlgBuyQuestion.SetCancelEvent(ui.__mem_func__(self.BuyQuestionCancel))
		dlgBuyQuestion.Open()
		self.dlgBuyQuestion = dlgBuyQuestion

	def BuySelectedItems(self):
		self.ItemList.BuySelectedItems()

		if self.dlgBuyQuestion:
			self.dlgBuyQuestion.Close()
			self.dlgBuyQuestion = None

	def AskBuySelectedItem(self, Pid, SlotPos, ItemName, ItemPrice):
		self.BuyQuestionCancel()

		self.sellOwner = Pid
		self.sellitemID = SlotPos
		self.sellItemPrice = ItemPrice
		
		dlgBuyQuestion = uicommon.QuestionDialog()
		dlgBuyQuestion.SetText(localeinfo.OFFLINESHOP_BUY % (ItemName, localeinfo.NumberToMoneyString(ItemPrice)))
		dlgBuyQuestion.SetAcceptEvent(ui.__mem_func__(self.BuySelectedItem))
		dlgBuyQuestion.SetCancelEvent(ui.__mem_func__(self.BuyQuestionCancel))
		dlgBuyQuestion.Open()
		self.dlgBuyQuestion = dlgBuyQuestion
	
	def BuyQuestionCancel(self):
		if self.dlgBuyQuestion:
			self.dlgBuyQuestion.Close()
			self.dlgBuyQuestion = None		
	
	def BuySelectedItem(self):
		offlineshop.SendBuyItemFromSearch(self.sellOwner, self.sellitemID, self.sellItemPrice)
		
		if self.dlgBuyQuestion:
			self.dlgBuyQuestion.Close()
			self.dlgBuyQuestion = None

	# def GetSearchFilterSettings(self, type = 0, subtype = 255):
		# name = self.sItemName.GetText() if self.sItemName.GetText() else ""
		
		# raceFlagDct = {
			# 0	: item.ITEM_ANTIFLAG_WARRIOR,
			# 1	: item.ITEM_ANTIFLAG_ASSASSIN,
			# 2	: item.ITEM_ANTIFLAG_SURA,
			# 3 	: item.ITEM_ANTIFLAG_SHAMAN,
		# }
		
		# raceflagbtn = [
			# self.wndFilterWarrior,
			# self.wndFilterAssassin,
			# self.wndFilterSura,
			# self.wndFilterShaman,
		# ]
		
		# raceflag	= 0
		
		# for k,v in raceFlagDct.items():
			# if not raceflagbtn[k].IsDown():
				# raceflag |= v
	
		# type		= type
		# subtype		= subtype
		# bIsPlayerName = self.CheckBox.IsChecked
		
		# levelmin	= 0
		# levelmax	= 0
		
		# yangmin		= 0
		# yangmax		= 0
		
		# if type == -1:
			# type = 0
			# subtype = 255
		
		# if subtype == -1:	
			# subtype = 255
		
		# attributes	= tuple([(0,0) for x in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)])

		# return (type, subtype, name, (yangmin,yangmax), (levelmin, levelmax, bIsPlayerName), raceflag, attributes)

	def Recv_PriceAverage(self, vnum, price):
		# market-% column: an average for a vnum arrived -> update every visible row of that vnum
		if not self.ItemList:
			return
		for row in self.ItemList.itemList:
			if getattr(row, "Vnum", 0) == vnum:
				row.SetMarketAverage(price)

	def GetSearchFilterSettings(self, type = 0, subtype = 255, page = 1):
		name = self.sItemName.GetText() if self.sItemName.GetText() else ""
		
		raceFlagDct = {
			0	: item.ITEM_ANTIFLAG_WARRIOR,
			1	: item.ITEM_ANTIFLAG_ASSASSIN,
			2	: item.ITEM_ANTIFLAG_SURA,
			3 	: item.ITEM_ANTIFLAG_SHAMAN,
		}
		
		raceflagbtn = [
			self.wndFilterWarrior,
			self.wndFilterAssassin,
			self.wndFilterSura,
			self.wndFilterShaman,
		]
		
		raceflag	= 0
		
		for k,v in raceFlagDct.items():
			if not raceflagbtn[k].IsDown():
				raceflag |= v

		type		= type
		subtype		= subtype
		bIsPlayerName = self.CheckBox.IsChecked

		# Extenstion
		bMale = False
		if self.wndFilterMale.selected:
			bMale = True
	
		bFeMale = False
		if self.wndFilterFeMale.selected:
			bFeMale = True

		levelmin = self.wndRefineMin.listBox.GetSelectedItem()
		levelmax = self.wndRefineMax.listBox.GetSelectedItem()
		
		if levelmin != 0:
			levelmin += 1

		if levelmax != 0:
			levelmax += 1

		wMinStack = int(self.wndTextMinStack.GetText()) if self.wndTextMinStack.GetText() else 0
		wMaxStack = int(self.wndTextMaxStack.GetText()) if self.wndTextMaxStack.GetText() else 0
		
		bGradeDS = self.wndGradeAlchemy.listBox.GetSelectedItem()
		bLevelDS = self.wndLvAlchemy.listBox.GetSelectedItem()

		if bGradeDS == 0:
			bGradeDS = 255
		else:
			bGradeDS -= 1

		if bLevelDS == 0:
			bLevelDS = 255
		else:
			bLevelDS -= 1
	
		bMinAVG = int(self.wndTextMinAVG.GetText()) if self.wndTextMinAVG.GetText() else 0
		bMaxAVG = int(self.wndTextMaxAVG.GetText()) if self.wndTextMaxAVG.GetText() else 0
		
		bMinSD = int(self.wndTextMinSkill.GetText()) if self.wndTextMinSkill.GetText() else 0
		bMaxSD = int(self.wndTextMaxSkill.GetText()) if self.wndTextMaxSkill.GetText() else 0
		
		bMinAbsSash = int(self.wndTextMinABS.GetText()) if self.wndTextMinABS.GetText() else 0
		bMaxAbsSash = int(self.wndTextMaxABS.GetText()) if self.wndTextMaxABS.GetText() else 0
		
		attributes = tuple([(self.GetAttrSelectedType(x), self.GetAttrSelectedValue(self.attrDict[x])) for x in xrange(5)])
		# End

		# offlineshop search rework: price range + sort mode, appended to the wire tuple
		yangMin = int(self.wndTextMinYang.GetText()) if hasattr(self, "wndTextMinYang") and self.wndTextMinYang.GetText() else 0
		yangMax = int(self.wndTextMaxYang.GetText()) if hasattr(self, "wndTextMaxYang") and self.wndTextMaxYang.GetText() else 0
		sortMode = self.wndSortMode.listBox.GetSelectedItem() if hasattr(self, "wndSortMode") and self.wndSortMode else 0
		if not _IsSearchPremium():
			yangMin = 0
			yangMax = 0
			sortMode = 0

		if type == -1:
			type = 0
			subtype = 255
		
		if subtype == -1:	
			subtype = 255
		
		return (type, subtype, name, bIsPlayerName, 
		(wMinStack,wMaxStack),
		(levelmin, levelmax),
		(bMinAVG, bMaxAVG),
		(bMinSD, bMaxSD),
		(bMinAbsSash, bMaxAbsSash),
		(bGradeDS, bLevelDS),
		(bMale, bFeMale),
		raceflag, attributes,
		(yangMin, yangMax), page, MAX_ITEMS_APPEND, sortMode)

	def OnSearchByValue(self, Type, SubType, bySearch = False, byPass = False):
		if byPass == False:
			dif = constinfo.shopSearchWaitTime - GetTime()
			if dif > 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_RENEWAL_WAIT % (str(dif)[:3]))
				return
		
		constinfo.shopSearchWaitTime=GetTime() + constinfo.shopSearchTimeWait
		
		if bySearch == False and\
			self.lastWasByName == 1:
			self.sItemName.SetText("")
			self.searchEditHint.SetText("")

		self.sCategory = Type
		self.sSubCategory = SubType
		self.ItemList.Clear()
		
		if Type == -1 and\
			SubType == -1:
			self.SearchFilterLastUsedSetting = self.GetSearchFilterSettings(0, 0)
		else:
			self.SearchFilterLastUsedSetting = self.GetSearchFilterSettings(Type, SubType)
		
		offlineshop.SendFilterRequest(*self.SearchFilterLastUsedSetting)
		
		self.currentPaginationPage = 1

		global SELECTED_ITEMS_BUY
		SELECTED_ITEMS_BUY = {}

	def OnUpdate(self):
		if getattr(self, "_liveSearchPending", False) and GetTime() >= self._liveSearchAt:
			self._liveSearchPending = False
			self._FireLiveSearch()

	def _FireLiveSearch(self):
		# debounced search fired from typing; the debounce is the throttle (no cooldown message)
		global SELECTED_ITEMS_BUY
		txt = self.sItemName.GetText() or ""
		if txt == self._lastLiveSearchText:
			return
		self._lastLiveSearchText = txt
		self.ItemList.Clear()
		self.SearchFilterLastUsedSetting = self.GetSearchFilterSettings(self.sCategory, self.sSubCategory)
		offlineshop.SendFilterRequest(*self.SearchFilterLastUsedSetting)
		self.currentPaginationPage = 1
		constinfo.shopSearchWaitTime = GetTime() + constinfo.shopSearchTimeWait
		SELECTED_ITEMS_BUY = {}

	def OnSearch(self):
		dif = constinfo.shopSearchWaitTime - GetTime()
		if dif > 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_RENEWAL_WAIT % (str(dif)[:3]))
			return
		
		constinfo.shopSearchWaitTime=GetTime() + constinfo.shopSearchTimeWait
		
#		if self.lastWasByName:
#			self.sItemName.SetText("")
#			self.searchEditHint.SetText("")
		
		self.ItemList.Clear()

		self.SearchFilterLastUsedSetting = self.GetSearchFilterSettings(self.sCategory, self.sSubCategory)
		offlineshop.SendFilterRequest(*self.SearchFilterLastUsedSetting)

		self.currentPaginationPage = 1

		global SELECTED_ITEMS_BUY
		SELECTED_ITEMS_BUY = {}
		
		#self.sItemName.SetText("")
		#self.searchEditHint.SetText("")
		#self.sItemName.KillFocus()

	def OnResetSearch(self):
		self.sItemName.SetText("")
		self.searchEditHint.SetText("")
		if self.searchDropdown:
			self.searchDropdown.Hide()
		#self.sItemName.KillFocus()

	def SearchByOwnerName(self, ownerName):
		if len(ownerName) < 1:
			return

		dif = constinfo.shopSearchWaitTime - GetTime()
		if dif > 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_RENEWAL_WAIT % (str(dif)[:3]))
			return

		constinfo.shopSearchWaitTime = GetTime() + constinfo.shopSearchTimeWait
		self.lastWasByName = 0  # this is fine, it doesn't affect owner search

		if not self.IsShow():
			self.LoadWindow()
			self.SetCenterPosition()
			self.Clear()

			self.CheckBox.IsChecked = True
			self.CheckBox.LoadImage(PATH_ROOT + "box_checked.png")
			self.sItemName.SetText(ownerName)

			self.OnSearchByValue(0, 0, True, True)

			if self.CategoryList:
				for item in self.CategoryList.itemList:
					item.SetSelectReset()

			ui.ScriptWindow.Show(self)
		else:
			self.Clear()

			self.CheckBox.IsChecked = True
			self.CheckBox.LoadImage(PATH_ROOT + "box_checked.png")
			self.sItemName.SetText(ownerName)

			self.OnSearchByValue(0, 0, True, True)

			if self.CategoryList:
				for item in self.CategoryList.itemList:
					item.SetSelectReset()

		self.sItemName.SetText("")
		self.searchEditHint.SetText("")
		self.sItemName.KillFocus()

	def SearchByName(self, itemName):
		if len(itemName) < 1:
			return
		
		dif = constinfo.shopSearchWaitTime - GetTime()
		if dif > 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_RENEWAL_WAIT % (str(dif)[:3]))
			return
		
		constinfo.shopSearchWaitTime=GetTime() + constinfo.shopSearchTimeWait
		
		self.lastWasByName = 1
		
		if not self.IsShow():
			self.LoadWindow()
			self.SetCenterPosition()
			self.Clear()
			
			self.sItemName.SetText(itemName)
			
			self.OnSearchByValue(0, 0, True, True)
			
			if self.CategoryList:
				for item in self.CategoryList.itemList:
					item.SetSelectReset()
			
			ui.ScriptWindow.Show(self)
		else:
			self.Clear()
			
			self.sItemName.SetText(itemName)
			
			self.OnSearchByValue(0, 0, True, True)
			
			if self.CategoryList:
				for item in self.CategoryList.itemList:
					item.SetSelectReset()
		
		self.sItemName.SetText("")
		self.searchEditHint.SetText("")
		self.sItemName.KillFocus()

	def RefreshPaginationButtons(self):
		self.currentPaginationPage = int(math.ceil(float(self.currentPage) / 5.0 ))
		self.shownPages = min(self.pageCount - (5 * (self.currentPaginationPage - 1)), 5)

		for x in xrange(5):
			currentPage = (x + ((self.currentPaginationPage-1) * 5) + 1)
			self.pageButtons[x].SetUp()
			self.pageButtons[x].SetText("%d" % currentPage)
			self.pageButtons[x].SetEvent(ui.__mem_func__(self.GotoPage), currentPage)
		
		map(ui.Button.Hide, self.pageButtons)
		map(ui.Button.Enable, self.pageButtons)
		
		for x in xrange(self.shownPages):
			self.pageButtons[x].Show()

		self.pageButtons[(self.currentPage - ((self.currentPaginationPage - 1) * 5)) - 1].Down()
		self.pageButtons[(self.currentPage - ((self.currentPaginationPage - 1) * 5)) - 1].Disable()

		# tidy grouped pager: '<< < [pages] > >>' even spacing, centered (no gap when <5 pages)
		STEP = 26
		PY = 503
		_startX = 540 - ((self.shownPages + 4) * STEP) // 2
		_x = _startX
		for _b in (self.lastButton, self.nextButton):
			_b.SetPosition(_x, PY)
			_x += STEP
		for _i in xrange(self.shownPages):
			self.pageButtons[_i].SetPosition(_x, PY)
			_x += STEP
		for _b in (self.prevButton, self.firstButton):
			_b.SetPosition(_x, PY)
			_x += STEP

	def __RequestServerPage(self, page):
		pc = getattr(self, "pageCount", 1)
		if pc < 1:
			pc = 1
		if page < 1:
			page = 1
		if page > pc:
			page = pc
		self.SearchFilterLastUsedSetting = self.GetSearchFilterSettings(self.sCategory, self.sSubCategory, page)
		offlineshop.SendFilterRequest(*self.SearchFilterLastUsedSetting)

	def GotoPage(self, page):
		if app.USE_OFFLINESHOP_SEARCH_PAGINATION:
			self.__RequestServerPage(page)
		else:
			self.currentPage = page
			self.RefreshList()

	def FirstPage(self):
		if app.USE_OFFLINESHOP_SEARCH_PAGINATION:
			self.__RequestServerPage(1)
		else:
			self.currentPage = 1
			self.RefreshList()

	def LastPage(self):
		if app.USE_OFFLINESHOP_SEARCH_PAGINATION:
			self.__RequestServerPage(getattr(self, "pageCount", 1))
		else:
			self.currentPage = self.pageCount
			self.RefreshList()

	def NextPage(self):
		if app.USE_OFFLINESHOP_SEARCH_PAGINATION:
			self.__RequestServerPage(self.currentPage + 1)
		else:
			if self.currentPage < self.pageCount:
				self.currentPage += 1
			self.RefreshList()

	def PrevPage(self):
		if app.USE_OFFLINESHOP_SEARCH_PAGINATION:
			self.__RequestServerPage(self.currentPage - 1)
		else:
			if self.currentPage > 1:
				self.currentPage -= 1
			self.RefreshList()

	def ShopFilterResult( self , size, total = None, page = None):
		self.SearchFilterShopItemResult = []
		if app.USE_OFFLINESHOP_SEARCH_PAGINATION and total is not None:
			self.serverTotalMatches = total
			if page is not None and page > 0:
				self.currentPage = page

	def ShopFilterResultItem_Alloc(self):
		self.SearchFilterShopItemResult.append({})

	def ShopFilterResultItem_SetDict(self, index, d):
		# P5: C++ delivers the whole search-result item as one dict.
		self.SearchFilterShopItemResult.append(d)

	def ShopFilterResultItem_SetValue( self,  key, index, *args):
		if key in ("id", "vnum", "count", "price", "owner", "owner_name", "trans","setItem"):
			self.SearchFilterShopItemResult[index][key] = args[0]

		elif app.ENABLE_EQUIPMENT_RESTRICTION and key == "restrict":
			self.SearchFilterShopItemResult[index][key] = (args[0], args[1])
		
		elif key == "attr":
			if not key in self.SearchFilterShopItemResult[index]:
				self.SearchFilterShopItemResult[index][key] = {}
			
			attr_index = args[0]
			attr_type  = args[1]
			attr_value = args[2]
			
			self.SearchFilterShopItemResult[index][key][attr_index] = {}
			self.SearchFilterShopItemResult[index][key][attr_index]["type"]  = attr_type
			self.SearchFilterShopItemResult[index][key][attr_index]["value"] = attr_value

		elif app.ENABLE_APPLY_RANDOM_SHOP and key=="rand":
			if not key in self.SearchFilterShopItemResult[index]:
				self.SearchFilterShopItemResult[index][key] = {}
			
			rand_index=args[0]
			rand_type=args[1]
			rand_value=args[2]
			rand_time=args[3]
			
			self.SearchFilterShopItemResult[index][key][rand_index] = {}
			self.SearchFilterShopItemResult[index][key][rand_index]["type"]=rand_type
			self.SearchFilterShopItemResult[index][key][rand_index]["value"]=rand_value
			self.SearchFilterShopItemResult[index][key][rand_index]["path"]=rand_time

		elif key == "socket":
			if not key in self.SearchFilterShopItemResult[index]:
				self.SearchFilterShopItemResult[index][key] = {}
			
			socket_index = args[0]
			socket_val	 = args[1]
			
			self.SearchFilterShopItemResult[index][key][socket_index] = socket_val
		elif app.USE_ENCHANT_COSTUMES and key=="enchant":
			if not key in self.SearchFilterShopItemResult[index]:
				self.SearchFilterShopItemResult[index][key] = {}
			
			enchant_index=args[0]
			enchant_type=args[1]
			enchant_value=args[2]
			enchant_time=args[3]
			
			self.SearchFilterShopItemResult[index][key][enchant_index] = {}
			self.SearchFilterShopItemResult[index][key][enchant_index]["type"]=enchant_type
			self.SearchFilterShopItemResult[index][key][enchant_index]["value"]=enchant_value
			self.SearchFilterShopItemResult[index][key][enchant_index]["time"]=enchant_time

	def ShopFilterResult_Show(self):
		self.itemCount = len(self.SearchFilterShopItemResult)

		if app.USE_OFFLINESHOP_SEARCH_PAGINATION:
			_total = getattr(self, "serverTotalMatches", self.itemCount)
		else:
			_total = self.itemCount
		if getattr(self, "wndResultCount", None):
			self.wndResultCount.SetText(localeinfo.OFFLINESHOP_SEARCH_RESULT_COUNT % _total)
		if getattr(self, "wndEmptyState", None):
			if self.itemCount == 0:
				self.wndEmptyState.Show()
			else:
				self.wndEmptyState.Hide()

		if app.USE_OFFLINESHOP_SEARCH_PAGINATION:
			total = getattr(self, "serverTotalMatches", self.itemCount)
			self.pageCount = max(1, int(math.ceil(float(total) / float(MAX_ITEMS_APPEND))))
		else:
			self.pageCount = int(math.ceil(float(self.itemCount) / float(MAX_ITEMS_APPEND)))
		self.currentPaginationPage = 1
		self.paginationPageCount = int(math.ceil(float(self.pageCount) / 5.0 ))

		if not app.USE_OFFLINESHOP_SEARCH_PAGINATION:
			self.currentPage = 1

		if self.currentPage > self.pageCount:
			self.currentPage = self.pageCount
		if self.currentPage < 1:
			self.currentPage = 1

		self.RefreshPaginationButtons()
		self.RefreshList()

	def RefreshList(self):
		self.ItemList.Clear()
		self.RefreshPaginationButtons()

		if app.USE_OFFLINESHOP_SEARCH_PAGINATION:
			# server already returned only this page; render every row received
			base = (self.currentPage - 1) * MAX_ITEMS_APPEND
			for x in xrange(len(self.SearchFilterShopItemResult)):
				self.ItemList.AppendItem(base + x, self.SearchFilterShopItemResult[x])
		else:
			size = len(self.SearchFilterShopItemResult)
			start = (self.currentPage - 1) * MAX_ITEMS_APPEND
			end = ((self.currentPage - 1) * MAX_ITEMS_APPEND) + MAX_ITEMS_APPEND
			for x in xrange(size):
				if start + x >= end:
					break
				if start + x < len(self.SearchFilterShopItemResult):
					self.ItemList.AppendItem(start + x, self.SearchFilterShopItemResult[start + x])

		if app.USE_OFFLINESHOP_PRICE_AVERAGE and _IsSearchPremium() and self.ItemList:
			# rows are appended now; request each distinct vnum's market average (cache-hit fans out immediately)
			vnums = []
			seen = {}
			for row in self.ItemList.itemList:
				v = getattr(row, "Vnum", 0)
				if v and v not in seen:
					seen[v] = 1
					vnums.append(v)
			for v in vnums:
				offlineshop.RequestAveragePrice(v)

	def Close(self, IsFromGame = False):
		self.ItemList.Clear()
		
		if self.dlgBuyQuestion:
			self.dlgBuyQuestion.Close()
			self.dlgBuyQuestion = None
		
		self.Hide()
	
	def CloseGame(self):
		self.Close(True)
	
	def OnPressEscapeKey(self):
		self.Close(True)
		return True	

# add at the end of file 
	def OnCheckBox(self):
		if self.CheckBox.IsChecked:
			self.CheckBox.IsChecked = False
			self.CheckBox.LoadImage(PATH_ROOT + "box_uncheck.png")
		else:
			self.CheckBox.IsChecked = True
			self.CheckBox.LoadImage(PATH_ROOT + "box_checked.png")
			
		self.Search_RefreshTextHint()

# add at end of file 

	def OnFilterReset(self):
		self.CreateFilterItems()

	def AskFilterName(self):

		FilterNameBoard = uiCommon.InputDialog()
		FilterNameBoard.SetTitle(localeinfo.SHOP_SEARCH_FILTER_NAME)
		FilterNameBoard.SetAcceptEvent(ui.__mem_func__(self.ConfirmFilterName))
		FilterNameBoard.SetCancelEvent(ui.__mem_func__(self.CancelFilterName))
		FilterNameBoard.Open()

		self.FilterNameBoard = FilterNameBoard

	def ConfirmFilterName(self):
		wndName = self.FilterNameBoard.GetText()
		if not wndName:
			return
		
		self.szFilterName = wndName
		self.SaveFilter()
		
		self.FilterNameBoard.Close()
		self.FilterNameBoard = None
		return True

	def CancelFilterName(self):
		if self.FilterNameBoard:
			self.FilterNameBoard.Close()
		self.FilterNameBoard = None
		return True

	def SaveFilter(self):
		pass
	def ManageBonusFilter(self):
		for i in xrange(len(self.attrDict)):
			if not self.btnFilterAttrManage.isExpanded:
				self.attrDict[i].Show()
			else:
				self.attrDict[i].Hide()
		
		self.btnFilterAttrManage.isExpanded = not self.btnFilterAttrManage.isExpanded
	
	def __OnSearchAttribute(self, attrIdx):
		if self.attributeSearchWindow:
			self.attributeSearchWindow.Close()
			del self.attributeSearchWindow
			
		self.attrSearchIdx = attrIdx
			
		wnd = uiswitchbot.SearchListWindow()
		width = 260
		height = 260
		wnd.MakeWindow(width, height)
		wnd.SetTitleName(localeinfo.SWITCHBOT_SELECT_ATTR)
		wnd.SetAcceptArgsType("KEY_VALUE")

		(mouseX, mouseY) = wndMgr.GetMousePosition()

		if mouseX + width/2 > wndMgr.GetScreenWidth():
			xPos = wndMgr.GetScreenWidth() - width
		elif mouseX - width/2 < 0:
			xPos = 0
		else:
			xPos = mouseX - width/2
			
		if mouseY + height/2 > wndMgr.GetScreenHeight():
			yPos = wndMgr.GetScreenHeight() - height
		elif mouseY - height/2 < 0:
			yPos = 0
		else:
			yPos = mouseY - height/2

		wnd.SetPosition(xPos, yPos)	
				
		for addonType, maxValue in uiswitchbot.ADDON_TYPES.iteritems():
			affectString = uiswitchbot.GetAffectString(addonType, maxValue)
			if not affectString:
				continue
				
			wnd.AppendItem(addonType, affectString)

		for type in xrange(200):
			affectString = uiswitchbot.GetAffectString(type, 0)
			if not affectString:
				continue
				
			if affectString.find("UNKNOWN_TYPE") != -1:
				continue
				
			wnd.AppendItem(type, affectString)
		
		wnd.SetAcceptEvent(ui.__mem_func__(self.__OnAcceptSearch))
		wnd.SetCancelEvent(ui.__mem_func__(self.__OnCancelSearch))
		wnd.SetTop()
		wnd.Open()

		self.attributeSearchWindow = wnd

	def __OnCancelSearch(self):
		pass

	def __OnAcceptSearch(self, key, value):
		if self.attrSearchIdx < 0 or self.attrSearchIdx >= len(self.attrDict):
			return
			
		attrRow = self.attrDict.get(self.attrSearchIdx, None)
		if not attrRow:
			return
			
		maxValue = uiswitchbot.ADDON_TYPES.get(key, 0)
		attrRow.keyAttr = key
		attrRow.SetAttribute(value, maxValue)

	def OnFilterManage(self):
		if self.boardFilter.isExpand:
			self.boardFilter.Hide()
			self.CategoryList.Show()
			self.ScrollBarCategory.Show()
		else:
			self.CategoryList.Hide()
			self.ScrollBarCategory.Hide()
			self.boardFilter.Show()
			self.__UpdatePremiumSearchWidgets()

		self.boardFilter.isExpand = not self.boardFilter.isExpand

	def __UpdatePremiumSearchWidgets(self):
		# sort dropdown + price-range inputs are premium-only; hide them otherwise (the rest of the panel stays)
		show = _IsSearchPremium()
		for w in (getattr(self, "wndBoardMinYang", None), getattr(self, "wndBoardMaxYang", None), getattr(self, "boardlistSort", None)):
			if w:
				if show:
					w.Show()
				else:
					w.Hide()
	
	def RadioButtonFilter(self, parent, text, x, y, up, over, down):
		button = ui.ToggleButton()
		button.SetParent(parent)
		button.SetPosition(x, y)
		button.SetUpVisual(PATH_FILTER + up)
		button.SetOverVisual(PATH_FILTER + over)
		button.SetDownVisual(PATH_FILTER + down)
		button.SetToolTipText(text)
		button.SetToggleUpEvent(ui.__mem_func__(self.OnFilterButtonDown), button)
		button.SetToggleDownEvent(ui.__mem_func__(self.OnFilterButtonSetUp), button)
		button.Show()
		button.Down()		
	
		button.selected = 0
	
		return button
	
	def OnFilterButtonDown(self, wnd):
		wnd.SetUp()
		wnd.selected = 1
		
	def OnFilterButtonSetUp(self, wnd):
		wnd.Down()
		wnd.selected = 0
	
	def MakeFilterLine(self, textOverlay, x, y, xOverlay = 1, yOverlay = 0):
		image = ui.ThinBoardCircle()
		image.SetParent(self.boardFilter)
		image.SetSize(85, 21)
		image.SetPosition(x, y)
		image.Show()
		
		wndTextName = ui.EditLine()
		wndTextName.SetParent(image)
		wndTextName.SetMax(45)
		wndTextName.SetSize(image.GetWidth() - 2, 15)
		wndTextName.SetPosition(0, 4)
		wndTextName.SetOverlayTextNew(textOverlay)
		wndTextName.SetLimitWidth(image.GetWidth())
		wndTextName.SetOutline()
		#wndTextName.overLay.SetPosition(80, yOverlay)
		wndTextName.Show()
		
		return (image, wndTextName)
	
	def MakeFilterList(self, width, x,y, textes):
		bg = ui.ThinBoardCircle()
		bg.SetParent(self.boardFilter)
		bg.SetSize(width, 21)
		bg.SetPosition(x, y)
		bg.Show()
		
		ListBox = ui.ComboBox()
		ListBox.SetParent(bg)
		ListBox.SetPosition(0, 1)
		ListBox.SetSize(bg.GetWidth(), bg.GetHeight() - 3)
		ListBox.SetEventNew(ui.__mem_func__(self.OnSelectListBoxFilter))
		ListBox.Show()
		
		for x in xrange(len(textes)):
			ListBox.InsertItem2(x, textes[x])
	
		ListBox.SetCurrentItem(textes[0])
		return (bg, ListBox)
	
	def OnSelectListBoxFilter(self, wnd, index, name):
		wnd.SetCurrentItem(name)

	def CreateFilterItems(self):
		self.wndFilterMale = self.RadioButtonFilter(self.boardFilter, "", 5, 0, "male_no_select.dds", "male_select.dds", "male_select.dds")
		self.wndFilterFeMale = self.RadioButtonFilter(self.boardFilter, "", 5, 25, "female_no_select.dds", "female_select.dds", "female_select.dds")
		
		self.wndFilterWarrior = self.RadioButtonFilter(self.boardFilter, "", 32, 7, "warrior_no_select.dds", "warrior_select.dds", "warrior_select.dds")
		self.wndFilterAssassin = self.RadioButtonFilter(self.boardFilter,"", (33 * 2) - 1, 7, "assassin_no_select.dds", "assassin_select.dds", "assassin_select.dds")
		self.wndFilterSura = self.RadioButtonFilter(self.boardFilter,"", (33 * 3) - 1, 7, "sura_no_select.dds", "sura_select.dds", "sura_select.dds")
		self.wndFilterShaman = self.RadioButtonFilter(self.boardFilter,"", (33 * 4) - 1, 7, "shaman_no_select.dds", "shaman_select.dds", "shaman_select.dds")
		
		self.wndBoardMinStack, self.wndTextMinStack = self.MakeFilterLine(localeinfo.SEARCH_FILTER_STACK_MIN, 7, 70)
		self.wndBoardMaxStack, self.wndTextMaxStack = self.MakeFilterLine(localeinfo.SEARCH_FILTER_STACK_MAX, 95, 70, 5)
		
		self.wndBoardMinAVG, self.wndTextMinAVG = self.MakeFilterLine(localeinfo.SEARCH_FILTER_AVG_MIN, 7, 128)
		self.wndBoardMaxAVG, self.wndTextMaxAVG = self.MakeFilterLine(localeinfo.SEARCH_FILTER_AVG_MAX, 95, 128, 5)

		self.wndBoardMinSkill, self.wndTextMinSkill = self.MakeFilterLine(localeinfo.SEARCH_FILTER_SK_MIN, 7, 156)
		self.wndBoardMaxSkill, self.wndTextMaxSkill = self.MakeFilterLine(localeinfo.SEARCH_FILTER_SK_MAX, 95, 156, 5)

		self.wndBoardMinABS, self.wndTextMinABS = self.MakeFilterLine(localeinfo.SEARCH_FILTER_ABS_MIN, 7, 183)
		self.wndBoardMaxABS, self.wndTextMaxABS = self.MakeFilterLine(localeinfo.SEARCH_FILTER_ABS_MAX, 95, 183, 5)

		self.btnFilterAttrManage = ui.MakeButton(self.boardFilter, 18, 260, False, PATH_ROOT, "btn_filter_norm.png", "btn_filter_hover.png", "btn_filter_down.png")
		self.btnFilterAttrManage.SetEvent(ui.__mem_func__(self.ManageBonusFilter))
		self.btnFilterAttrManage.SetText(localeinfo.SEARCH_SHOP_ATTRS)
		self.btnFilterAttrManage.isExpanded = False

		self.boardlist4, self.wndLvAlchemy = self.MakeFilterList(160, 8, 232, [localeinfo.SEARCH_FILTER_ALCHEMY_LV, "+0", "+1", "+2", "+3", "+4", "+5", "+6"])
		self.boardlist3, self.wndGradeAlchemy = self.MakeFilterList(160, 8, 208, [localeinfo.SEARCH_FILTER_ALCHEMY_GRADE, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE1, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE2, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE3, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE4, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE5, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE6])
		self.boardlist2, self.wndRefineMax = self.MakeFilterList(79, 88, 100, [localeinfo.SEARCH_FILTER_REFINE_MAX, "+2", "+3", "+4", "+5", "+6", "+7", "+8", "+9"])
		self.boardlist1, self.wndRefineMin = self.MakeFilterList(79, 8, 100, [localeinfo.SEARCH_FILTER_REFINE_MIN, "+2", "+3", "+4", "+5", "+6", "+7", "+8", "+9"])

		# offlineshop search rework: price range + sort mode controls
		self.wndBoardMinYang, self.wndTextMinYang = self.MakeFilterLine(localeinfo.SEARCH_FILTER_YANG_MIN, 7, 290)
		self.wndBoardMaxYang, self.wndTextMaxYang = self.MakeFilterLine(localeinfo.SEARCH_FILTER_YANG_MAX, 95, 290, 5)
		self.boardlistSort, self.wndSortMode = self.MakeFilterList(180, 8, 316, [localeinfo.SEARCH_FILTER_SORT_UNIT_ASC, localeinfo.SEARCH_FILTER_SORT_UNIT_DESC, localeinfo.SEARCH_FILTER_SORT_TOTAL_ASC, localeinfo.SEARCH_FILTER_SORT_TOTAL_DESC, localeinfo.SEARCH_FILTER_SORT_LEVEL, localeinfo.SEARCH_FILTER_SORT_RECENT])

	def GetAttrSelectedValue(self, attr):
		text = attr.valueEditLine.GetText()
		if not text:
			return 0
			
		return int(text)

	def GetAttrSelectedType(self, x):#try
		text = self.attrDict[x].valueEditLine.GetText()
		if not text:
			return 0
			
		if int(text) == 0:
			return 0
	
		return self.attrDict[x].keyAttr
