# coding: latin_1

import app
import player

import ui
import chat
import item
import localeinfo
import uitooltip
import grp
import cube_renewal
import mousemodule
import ingamewiki
import net
import uiofflineshop_ae

if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget

import systemSetting

def FReturnInfo(func,index):
	(vnum_reward,count_reward,item_reward_stackable,vnum_material_1,count_material_1,vnum_material_2,count_material_2,vnum_material_3,count_material_3,vnum_material_4,count_material_4,vnum_material_5,count_material_5,vnum_material_6,count_material_6,vnum_material_7,count_material_7,vnum_material_8,count_material_8,vnum_material_9,count_material_9,vnum_material_10,count_material_10,gold, gem,not_remove,set_value,percent,category) = cube_renewal.GetDates(index)
	info = {
			"vnum_reward" : vnum_reward,
			"count_reward" : count_reward,
			"item_reward_stackable" : item_reward_stackable,
			"vnum_material_1" : vnum_material_1,
			"count_material_1" : count_material_1,
			"vnum_material_2" : vnum_material_2,
			"count_material_2" : count_material_2,
			"vnum_material_3" : vnum_material_3,
			"count_material_3" : count_material_3,
			"vnum_material_4" : vnum_material_4,
			"count_material_4" : count_material_4,
			"vnum_material_5" : vnum_material_5,
			"count_material_5" : count_material_5,
			"vnum_material_6" : vnum_material_6,
			"count_material_6" : count_material_6,
			"vnum_material_7" : vnum_material_7,
			"count_material_7" : count_material_7,
			"vnum_material_8" : vnum_material_8,
			"count_material_8" : count_material_8,
			"vnum_material_9" : vnum_material_9,
			"count_material_9" : count_material_9,
			"vnum_material_10" : vnum_material_10,
			"count_material_10" : count_material_10,
			"gold" : gold,
			"gem" : gem,
			"not_remove" : not_remove,
			"set_value" : set_value,
			"percent" : percent,
			"category" : category
	}

	return info[func]

class CubeRenewalItem(ui.Window):
	def __init__(self, getParentEvent):
		ui.Window.__init__(self)
		self.SetParent(getParentEvent().GetBoard())

		self.index = -1
		self.type = -1

		self.count_all = -1

		self.date_cube = None
		if app.ENABLE_INGAME_WIKI:
			wndWiki = None
		self.index = -1

		self.button = ui.Button()
		self.button.SetParent(self)
		self.button.SetEvent(self.Select)
		self.button.Show()

		self.image = ui.ImageBox()
		self.image.SetParent(self)
		self.image.SetPosition(7,3)
		self.image.Show()

		self.text = ui.TextLine()
		self.text.SetParent(self)
		self.text.SetPosition(277,0)
		self.text.Show()

#		self.count_total = ui.TextLine()
#		self.count_total.SetParent(self)
#		self.count_total.SetPosition(277,2)
#		self.count_total.Hide()

		self.getParentEvent = getParentEvent

		self.SetSize(280, 17)

	def SetName(self, name):
		self.name = name
		self.text.SetText(name)

	def SetNameCatagoria(self, name):
		self.name = name
		self.text.SetText(name)
		self.text.SetHorizontalAlignLeft()
		self.text.SetWindowHorizontalAlignLeft()

	def SetNameae(self, name):
		self.name = name
		self.text.SetHorizontalAlignLeft()
		self.text.SetWindowHorizontalAlignCenter()
		self.text.SetText(name)

	def SetCountTotal(self, count):

		self.count_all = count

		if count <= 0:
#			self.count_total.Hide()
			self.text.SetPosition(250,0)
			return

#		self.count_total.SetText(" ?I?? %d ???E "%(count*self.GetCountReward()))
#		self.count_total.SetPackedFontColor(grp.GenerateColor(0.5411, 0.7254, 0.5568, 1.0))
#		self.count_total.SetPosition(120,0)
#		self.count_total.Show()

#		w, h = self.count_total.GetTextSize()
		self.text.SetPosition(250,0)

	def GetCount(self):
		return self.count_all

	def SetType(self,type):
		self.type = type

	def AppendIndex(self,index):
		self.index = index

	def GetIndex(self):
		return self.index

	def GetDates(self,func):
		return FReturnInfo(func,self.GetIndex())

	def GetVnumReward(self):
		return self.GetDates("vnum_reward")

	def GetCountReward(self):
		return self.GetDates("count_reward")

	def GetItemStackable(self):
		return self.GetDates("item_reward_stackable")

	def GetVnumMaterial(self,index):
		return self.GetDates("vnum_material_%d"%index)

	def GetCountMaterial(self,index):
		return self.GetDates("count_material_%d"%index)

	def GetGold(self):
		return self.GetDates("gold")

	def GetGem(self):
		return self.GetDates("gem")

	def GetNotRemove(self):
		return self.GetDates("not_remove")
		
	def GetSetValue(self):
		return self.GetDates("set_value")

	def GetPorcentaje(self):
		return self.GetDates("percent")

	def GetName(self):
		return self.name

	def GetType(self):
		return self.type

	def GetStepWidth(self):
		return 0

	def Select(self):
		self.getParentEvent().OnSelectItem(self)

class CubeRenewalCategoriaItem(CubeRenewalItem):

	def __init__(self, getParentEvent):
		self.OpenFunc = FALSE
		self.SubCategorias = []
		self.index = -1

		CubeRenewalItem.__init__(self, getParentEvent)

		self.button.SetUpVisual("d:/ymir work/ui/game/cube/cube_menu_tab1.sub")
		self.button.SetOverVisual("d:/ymir work/ui/game/cube/cube_menu_tab1.sub")
		self.button.SetDownVisual("d:/ymir work/ui/game/cube/cube_menu_tab1.sub")

		self.SetType(1)

	def SetCategoria(self,index,name):
		self.SetName(name)
		self.IndexCategoria(index)

	def AppendSubCategorias(self, date_cube):
		subcategorias = CubeRenewalSubCategoriaItem(self.getParentEvent)
		subcategorias.AppendIndex(date_cube)
		subcategorias.LoadInfo()
		subcategorias.Select()
		self.SubCategorias.append(subcategorias)

	def GetListSubCategorias(self):
		return self.SubCategorias

	def IndexCategoria(self,index):
		self.index = index

	def GetIndexCategoria(self):
		return self.index

	def FindVnumSubCategoria(self, key):
		list = filter(lambda argMember, argKey=key: argMember.IsSameVnum(argKey), self.SubCategorias)
		if list:
			return list[0]

		return None

	def Open(self):
		self.image.LoadImage("d:/ymir work/ui/game/cube/cube_menu_tab1_minus.sub")
		self.OpenFunc = TRUE

	def Close(self):
		self.image.LoadImage("d:/ymir work/ui/game/cube/cube_menu_tab1_plus.sub")
		self.OpenFunc = FALSE
		map(ui.Window.Hide, self.SubCategorias)

	def OnPressEscapeKey(self):
		self.Close()
		return TRUE

	def IsOpen(self):
		return self.OpenFunc

	def Select(self):
		if self.OpenFunc:
			self.Close()
		else:
			self.Open()

		for x in self.GetListSubCategorias():
			x.Select()

		self.getParentEvent().OnRefresh()
		
class CubeRenewalSubCategoriaItem(CubeRenewalItem):

	def __init__(self, getParentEvent):

		self.OpenFunc = FALSE
		self.SubCategoriaObjects = []

		CubeRenewalItem.__init__(self, getParentEvent)

		self.button.SetUpVisual("d:/ymir work/ui/game/cube/cube_menu_tab2.sub")
		self.button.SetOverVisual("d:/ymir work/ui/game/cube/cube_menu_tab2.sub")
		self.button.SetDownVisual("d:/ymir work/ui/game/cube/cube_menu_tab2.sub")

		self.image.SetPosition(7,4)
		self.text.SetPosition(270,0)
		self.text.SetPackedFontColor(0xffa28b5f)

		self.SetType(2)

	def LoadInfo(self):
		item.SelectItem(self.GetVnumReward())
		self.SetName(item.GetItemName())

	def AppendSubCategoriaObjects(self, date_cube):
		subcategoriaobj = CubeRenewalSubCategoriaObjects(self.getParentEvent)
		subcategoriaobj.AppendIndex(date_cube)
		subcategoriaobj.LoadInfo()
		self.SubCategoriaObjects.append(subcategoriaobj)

	def IsSameVnum(self, vnum):
		return self.GetVnumReward() == vnum

	def Open(self):
		self.image.LoadImage("d:/ymir work/ui/game/cube/cube_menu_tab2_minus.sub")
		self.OpenFunc = TRUE

	def Close(self):
		self.image.LoadImage("d:/ymir work/ui/game/cube/cube_menu_tab2_plus.sub")
		self.OpenFunc = FALSE
		map(ui.Window.Hide, self.SubCategoriaObjects)

	def OnPressEscapeKey(self):
		self.Close()
		return TRUE	

	def IsOpen(self):
		return self.OpenFunc

	def GetListSubCategoriasObjects(self):
		return self.SubCategoriaObjects

	def Select(self):
		if self.OpenFunc:
			self.Close()
		else:
			self.Open()

		self.getParentEvent().OnRefresh()

class CubeRenewalSubCategoriaObjects(CubeRenewalItem):
	def __init__(self, getParentEvent):
		CubeRenewalItem.__init__(self, getParentEvent)

		self.button.SetUpVisual("d:/ymir work/ui/game/cube/cube_menu_tab3_default.sub")
		self.button.SetOverVisual("d:/ymir work/ui/game/cube/cube_menu_tab3_select.sub")
		self.button.SetDownVisual("d:/ymir work/ui/game/cube/cube_menu_tab3_select.sub")
		self.SetType(3)
		self.text.SetPosition(17,2)

	def LoadInfo(self):
		item.SelectItem(self.GetVnumReward())
		self.SetName(item.GetItemName()+' (%d%%)'%(self.GetPorcentaje()))
		self.CountTotal()

	def CountTotal(self):
		count_items = []
		count_all_items = 0

		for i in xrange(1,11):
			if self.GetVnumMaterial(i) != 0:
				if player.GetItemCountByVnum(self.GetVnumMaterial(i)) >= self.GetCountMaterial(i):
					number = player.GetItemCountByVnum(self.GetVnumMaterial(i)) / (self.GetCountMaterial(i))
					count_items.append(number)

				if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
					if player.GetItemCountByVnum(self.GetVnumMaterial(i)) >= self.GetCountMaterial(i):
						number = player.GetItemCountByVnum(self.GetVnumMaterial(i)) / (self.GetCountMaterial(i))
						count_items.append(number)
						
				count_all_items += 1

		if len(count_items) >= count_all_items:
			self.SetCountTotal(min(count_items))
		else:
			self.SetCountTotal(0)

	def UpdatePorcentaje(self):
		item.SelectItem(self.GetVnumReward())
		porcentaje_actual = 0

		if self.GetPorcentUpdate() != 0:
			if self.GetPorcentaje()+self.GetPorcentUpdate() > 100:
				porcentaje_actual = 100
			else:
				porcentaje_actual = self.GetPorcentaje()+self.GetPorcentUpdate()
		else:
			porcentaje_actual = self.GetPorcentaje()

		self.SetName(item.GetItemName()+ localeinfo.INTERFACE_TEXT_12 +'%d%%'%(porcentaje_actual))

	def GetPorcentUpdate(self):
		return self.getParentEvent().GetPorcentNew()

	def UnSelect(self):
		self.button.SetUp()
		self.button.Enable()

	def SetSelect(self):
		self.button.Down()
		self.button.Disable()

	def Select(self):
		self.getParentEvent().SelectObject(self)

class CubeRenewalWindows(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		cube_renewal.SetCubeRenewalHandler(self)

		self.categoria = [
			[1,"WEAPON", localeinfo.INTERFACE_TEXT_13],
			[2,"ARMOR", localeinfo.INTERFACE_TEXT_14],
			[3,"HELMET", localeinfo.INTERFACE_TEXT_15],
			[4,"ACCESSORY", localeinfo.INTERFACE_TEXT_16],
			[5,"BELT", localeinfo.INTERFACE_TEXT_17],
			[6,"ETC", localeinfo.INTERFACE_TEXT_18],
			[7,"EVENT", localeinfo.INTERFACE_TEXT_19],
			[8,"WING", localeinfo.INTERFACE_TEXT_20],
			[9,"COSTUME", localeinfo.INTERFACE_TEXT_D1],
			[10,"HAIR", localeinfo.INTERFACE_TEXT_D2],
			[12,"COSTUME2", localeinfo.INTERFACE_TEXT_D3],
			[13,"BOX", localeinfo.INTERFACE_TEXT_D4],
			[14,"PET", localeinfo.INTERFACE_TEXT_D5],
			[15,"DUNGEON", localeinfo.INTERFACE_TEXT_D6],
			[16,"WEAPON_2", localeinfo.INTERFACE_TEXT_D7],
			[17,"WEAPON_3", localeinfo.INTERFACE_TEXT_D8],
			[18,"ARMOR_2", localeinfo.INTERFACE_TEXT_D9],
			[19,"ARMOR_3", localeinfo.INTERFACE_TEXT_D10],
			[20,"HELMET_2", localeinfo.INTERFACE_TEXT_D13],
			[21,"HELMET_3", localeinfo.INTERFACE_TEXT_D14],
			[22,"ACCESSORY_2", localeinfo.INTERFACE_TEXT_D11],
			[23,"ACCESSORY_3", localeinfo.INTERFACE_TEXT_D12],
			[24,"SHIELD_2", localeinfo.INTERFACE_TEXT_D15],
			[25,"SHIELD_3", localeinfo.INTERFACE_TEXT_D16],
			[26,"SHOES_2", localeinfo.INTERFACE_TEXT_D17],
			[27,"SHOES_3", localeinfo.INTERFACE_TEXT_D18],
			[28,"FARMING", localeinfo.INTERFACE_TEXT_D19],
			[29,"LV_55", localeinfo.INTERFACE_TEXT_D20],
			[30,"FARMING_2", localeinfo.INTERFACE_TEXT_D22],
			[31,"RINGS", localeinfo.INTERFACE_TEXT_D23],
			[32,"CHARM", localeinfo.INTERFACE_TEXT_D24],
			[33,"UPGRADE", localeinfo.INTERFACE_TEXT_D25],
			[34,"PET_PVP", localeinfo.INTERFACE_TEXT_D26],
			[35,"PET_PVM", localeinfo.INTERFACE_TEXT_D27],
			[36,"FISH_PVP", localeinfo.INTERFACE_TEXT_D28],
			[37,"FISH_PVM", localeinfo.INTERFACE_TEXT_D29],
			[38,"MOUNT", localeinfo.INTERFACE_TEXT_D30],
			[39,"MOUNT_PET", localeinfo.INTERFACE_TEXT_D31],
			[40,"MOUNT_PET_1", localeinfo.INTERFACE_TEXT_D32],
			[41,"ZODIAC_BOX", localeinfo.INTERFACE_TEXT_D34],
			[42,"SETADD_WEAPON", localeinfo.CUBE_CATEGORY_SETADD_WEAPON],
			[43,"SETADD_ARMOR",localeinfo.CUBE_CATEGORY_SETADD_ARMOR],
			[44,"SETADD_HELMET", localeinfo.CUBE_CATEGORY_SETADD_HELMET],
			[45,"GLOVES", localeinfo.CUBE_CATEGORY_ARMOR_GLOVE],
			[46,"GLOVES_2", localeinfo.CUBE_CATEGORY_ARMOR_GLOVE2],
			[47,"STONES", localeinfo.CUBE_CATEGORY_STONES],
			[48,"ELEMENT", localeinfo.CUBE_CATEGORY_ELEMENT],
			[49,"SNAKE_WEP", localeinfo.CUBE_CATEGORY_WEAPON2],
			[50,"SNAKE_ARM", localeinfo.CUBE_CATEGORY_ARMOR2],
			[51,"SNAKE_ACC", localeinfo.CUBE_CATEGORY_ACCESSORY2],
			[52,"SEAL_BEGINNER", localeinfo.CUBE_CATEGORY_SEAL_BEGINNER],
			[53,"SEAL_MEDIUM", localeinfo.CUBE_CATEGORY_SEAL_MEDIUM],
			[54,"SEAL_ADVANCED", localeinfo.CUBE_CATEGORY_SEAL_ADVANCED],
			[999,"WORLDARD", localeinfo.INTERFACE_TEXT_21]
		]

		self.showingItemList = []
		self.categoria_list = []
		self.startLine = 0
		self.MaxElements = 12
		self.cube_elements = {}
		self.selectedItem = None
		self.count_item_reward = 0

		self.vnum_item_improve = 79605
		self.max_count_item_improve = 40
		self.slot_item_improve = -1
		self.NextPageBtn = None
		self.PreviousPageBtn = None
		self.MainBoard = None
		self.materialWindowIndex = 0
		self.tooltipIndex = 0

		self.toolTip = uitooltip.ItemToolTip()

		self.LoadWindow()

	def __del__(self):
		cube_renewal.SetCubeRenewalHandler(None)
		ui.ScriptWindow.__init__(self)

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/cuberenewalwindow.py")
		except:
			import exception
			exception.Abort("CubeRenewalWindows.LoadWindow.LoadObject")

		try:
			self.board = self.GetChild("item_list_board")
			self.item_slot = self.GetChild("item_slot")
			self.cube_list_scroll_bar = self.GetChild("cube_list_scroll_bar")
			self.yang_text = self.GetChild("yang_text")
			self.gem_text = self.GetChild("gem_text")
			self.result_qty = self.GetChild("result_qty")
			self.button_ok = self.GetChild("button_ok")
			self.button_cancel = self.GetChild("button_cancel")
			self.MainBoard = self.GetChild("board")
			self.NextPageBtn = ui.MakeButton(self.MainBoard, 320, 289, "", "d:/ymir work/ui/game/belt_inventory/", "btn_minimize_normal.tga", "btn_minimize_over.tga", "btn_minimize_down.tga")
			self.NextPageBtn.SetEvent(ui.__mem_func__(self.__ClickNextPageButton))
			self.NextPageBtn.Hide()

			self.PreviousPageBtn = ui.MakeButton(self.MainBoard, 320, 289, "", "d:/ymir work/ui/game/belt_inventory/", "btn_expand_normal.tga", "btn_expand_over.tga", "btn_expand_down.tga")
			self.PreviousPageBtn.SetEvent(ui.__mem_func__(self.__ClickPreviousPageButton))
			self.PreviousPageBtn.Hide()

			self.qty_sub_button = self.GetChild("qty_sub_button")
			self.qty_add_button = self.GetChild("qty_add_button")

			self.imporve_slot = self.GetChild("imporve_slot")
			
			self.GetChild("board").SetCloseEvent(ui.__mem_func__(self.Close))

			for i in xrange(1,6):
				self.cube_elements["count_elements_%d"%i] = self.GetChild("material_qty_text_%d"%i)

		except:
			import exception
			exception.Abort("CubeRenewalWindows.LoadWindow.LoadElements")

		self.slot_improve = ui.SlotWindow()
		self.slot_improve.SetParent(self.imporve_slot)
		self.slot_improve.SetSize(32,32)
		self.slot_improve.SetPosition(6,5)
		self.slot_improve.SetSelectEmptySlotEvent(ui.__mem_func__(self.__OnSelectEmptySlot))
		self.slot_improve.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnSelectItemSlot))
		self.slot_improve.AppendSlot(0,0,0,32,32)
		self.slot_improve.Show()

		self.button_cancel.SetEvent(self.Close)

		self.button_ok.SetEvent(self.AceptCube)
		self.result_qty.SetReturnEvent(self.AceptInputItem)
		self.result_qty.SetEscapeEvent(ui.__mem_func__(self.Close))
		self.result_qty.CanEdit(FALSE)

		self.qty_sub_button.SetEvent(self.QtySubButton)
		self.qty_add_button.SetEvent(self.QtyAddButton)

		self.cube_list_scroll_bar.SetScrollEvent(ui.__mem_func__(self.OnScroll))

		self.icons_items = ui.SlotWindow()
		self.icons_items.SetParent(self.item_slot)
		self.icons_items.SetPosition(25,13)
		self.icons_items.SetSize((32*9),32*3)
		self.icons_items.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		self.icons_items.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		self.icons_items.SetUnselectItemSlotEvent(ui.__mem_func__(self.SearchInWiki))
		if app.ENABLE_RENDER_TARGET:
			self.icons_items.SetSelectItemSlotEvent(ui.__mem_func__(self.RenderItem))

		self.icons_items.AppendSlot(0,0,0,32,32*3)

		for i in xrange(0,6):
			self.icons_items.AppendSlot(i+1,46*i+62,0,32,32*3)

		self.icons_items.Show()

	def BINARY_CUBE_RENEWAL_LOADING(self):
		self.ClearElements()
		self.LoadCategoria()
		self.LoadSubCategoria()
		self.LoadSubObjects()
		self.OnRefresh()

	def BINARY_CUBE_RENEWAL_UPDATE(self):
		if self.selectedItem:
			self.UpdateCountSubCategoria()
			self.UpdateMaterialCount()

	def ClearElements(self):
		if len(self.showingItemList) > 0:
			map(ui.Window.Hide, self.showingItemList)

		for group in self.categoria_list:
			group.Close()

			for categorias in group.GetListSubCategorias():
				categorias.Close()

		for i in xrange(0,6):
			self.icons_items.ClearSlot(i)
			if i > 0:
				self.cube_elements["count_elements_%d"%i].Hide()

		self.yang_text.Hide()
		self.result_qty.Hide()

		self.categoria_list = []
		self.startLine = 0

		self.cube_list_scroll_bar.SetPos(0)

	def CheckListCategoriasTotal(self):
		list1 = []
		list2 = []

		for i2 in xrange(cube_renewal.CountDates()):
			list1.append(self.CheckCategoryIndex(FReturnInfo("category",i2)))

		for ia in list1:
			if ia not in list2:
				list2.append(ia)

		return list2

	def LoadCategoria(self):
		world = self.CheckListCategoriasTotal()
		for i in world:
			for i1 in xrange(len(self.categoria)):
				if self.categoria[i1][0] == i:
					member = CubeRenewalCategoriaItem(ui.__mem_func__(self.GetSelf))
					member.SetCategoria(self.categoria[i1][0],self.categoria[i1][2])
					member.Close()
					member.Show()
					self.categoria_list.append(member)

	def CheckCategoryIndex(self,name):
		vnum_default = 0
		for i in xrange(len(self.categoria)):
			if name == self.categoria[i][1]:
				return self.categoria[i][0]
		for i in xrange(len(self.categoria)):
			if "WORLDARD" == self.categoria[i][1]:
				return self.categoria[i][0]

	def LoadSubCategoria(self):
		for group in self.categoria_list:
			for i in xrange(cube_renewal.CountDates()):
				if self.CheckCategoryIndex(FReturnInfo("category",i)) == group.GetIndexCategoria():
					if not group.FindVnumSubCategoria(FReturnInfo("vnum_reward",i)):
						group.AppendSubCategorias(i)

	def LoadSubObjects(self):
		for group in self.categoria_list:
			for i in xrange(cube_renewal.CountDates()):
				if self.CheckCategoryIndex(FReturnInfo("category",i)) == group.GetIndexCategoria():
					for categorias in group.GetListSubCategorias():
						if FReturnInfo("vnum_reward",i) == categorias.GetVnumReward():
							categorias.AppendSubCategoriaObjects(i)

	def OnScroll(self):
		scrollLineCount = len(self.showingItemList) - (self.MaxElements)
		startLine = int(scrollLineCount * self.cube_list_scroll_bar.GetPos())


		if startLine != self.startLine:
			self.startLine = startLine
			self.SetExtraInfo()

	def OnRunMouseWheel(self, nLen):
		if self.cube_list_scroll_bar:
			if self.cube_list_scroll_bar.IsShow():
				self.cube_list_scroll_bar.OnMouseWheel2(nLen)
				return True
		return False

	def __OnSelectEmptySlot(self,selectedSlotPos):
		isAttached = mousemodule.mouseController.isAttached()

		if not self.selectedItem:
			return

		if self.selectedItem.GetPorcentaje() >= 100:
			return

		if isAttached:
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			mousemodule.mouseController.DeattachObject()


			itemVNum = player.GetItemIndex(attachedSlotPos)
			itemCount = player.GetItemCount(attachedSlotPos)

			if itemVNum == self.vnum_item_improve and itemCount <= self.max_count_item_improve:
				self.slot_improve.SetItemSlot(selectedSlotPos,itemVNum,itemCount)
				self.slot_item_improve = attachedSlotPos

	def __OnSelectItemSlot(self,selectedSlotPos):
		if app.ENABLE_RENDER_TARGET:
			if app.IsPressed(app.DIK_LSHIFT) and uiRenderTarget.IsCanShowItems(player.GetItemIndex(selectedSlotPos)):
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler:
					self.interfaceHandler.OpenRenderTargetWindow(0, player.GetItemIndex(selectedSlotPos))
					return

		isAttached = mousemodule.mouseController.isAttached()

		if not self.selectedItem:
			return

		if self.selectedItem.GetPorcentaje() >= 100:
			return

		if isAttached:
			attachedSlotType = mousemodule.mouseController.GetAttachedType()
			attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
			mousemodule.mouseController.DeattachObject()

			itemVNum = player.GetItemIndex(attachedSlotPos)
			itemCount = player.GetItemCount(attachedSlotPos)

			if itemVNum == self.vnum_item_improve and itemCount <= self.max_count_item_improve:
				self.slot_improve.SetItemSlot(selectedSlotPos,itemVNum,itemCount)
				self.slot_item_improve = attachedSlotPos
		else:
			self.slot_improve.SetItemSlot(0,0,0)
			self.slot_item_improve = -1

	def OnRefresh(self):
		self.showingItemList = []

		for group in self.categoria_list:
			self.showingItemList.append(group)

			if group.IsOpen():
				for categorias in group.GetListSubCategorias():
					self.showingItemList.append(categorias)

					if categorias.IsOpen():
						for a in categorias.GetListSubCategoriasObjects():
							self.showingItemList.append(a)

		self.SetExtraInfo()

	def SetExtraInfo(self):
		if self.MaxElements >= len(self.showingItemList):
			self.cube_list_scroll_bar.Hide()
			self.startLine = 0
		else:
			if self.showingItemList:
				self.cube_list_scroll_bar.SetMiddleBarSize(float(self.MaxElements) / float(len(self.showingItemList)))
			self.cube_list_scroll_bar.Show()

		map(ui.Window.Hide, self.showingItemList)

		yPos = 11
		heightLimit = 240

		for item in self.showingItemList[self.startLine:]:
			XPos = 0
			if item.GetType() == 2:
				XPos += 15
			if item.GetType() == 3:
				XPos += 35
			item.SetPosition(6 + XPos, yPos)
			item.SetTop()
			item.Show()

			yPos += 20

			if yPos > heightLimit:
				break

	def SelectObject(self,item):
		self.selectedItem = item
		self.materialWindowIndex = 0
		if self.selectedItem.GetVnumMaterial(6) == 0:
			self.PreviousPageBtn.Hide()
			self.NextPageBtn.Hide()
		else:
			self.PreviousPageBtn.Hide()
			self.NextPageBtn.Show()
			self.NextPageBtn.Flash()
		if self.selectedItem:	
			self.UpdateInfoSelect()
			self.UpdateSelectSubCategoria()

	def UpdateInfoSelect(self):

		self.icons_items.ClearSlot(0)
		self.icons_items.SetItemSlot(0,self.selectedItem.GetVnumReward(),self.selectedItem.GetCountReward())

		begin = 1 + (self.materialWindowIndex * 5)
		end = 6 + (self.materialWindowIndex * 5)

		for i in xrange(begin,end):
			realSlotIndex = i - (self.materialWindowIndex * 5)
			self.icons_items.ClearSlot(realSlotIndex)
			self.icons_items.SetItemSlot(realSlotIndex, self.selectedItem.GetVnumMaterial(i), self.selectedItem.GetCountMaterial(i))


		self.result_qty.KillFocus()
		self.result_qty.CanEdit(self.selectedItem.GetItemStackable())
		self.result_qty.SetText("%s"%(self.selectedItem.GetCountReward()))
		self.result_qty.Show()

		self.count_item_reward = self.selectedItem.GetCountReward()
	
		self.UpdateMaterialCount()
		self.UpdateSlotItemImprove()

	def UpdateSlotItemImprove(self):
		if self.selectedItem.GetPorcentaje() >= 100 and self.slot_item_improve != -1:
			self.slot_improve.SetItemSlot(0,0,0)
			self.slot_item_improve = -1

	def UpdateMaterialCount(self):
		count = (self.count_item_reward/(self.selectedItem.GetCountReward()))

		begin = 1 + (self.materialWindowIndex * 5)
		end = 6 + (self.materialWindowIndex * 5)

		for i in xrange(begin,end):
			realSlotIndex = i - (self.materialWindowIndex * 5)
			
			if self.selectedItem.GetVnumMaterial(i) != 0:
				if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
					if player.GetItemCountByVnum(self.selectedItem.GetVnumMaterial(i)) >= (self.selectedItem.GetCountMaterial(i)*count):
						self.cube_elements["count_elements_%d"%realSlotIndex].SetPackedFontColor(grp.GenerateColor(0.5411, 0.7254, 0.5568, 1.0))
					elif  player.GetItemCountByVnum(self.selectedItem.GetVnumMaterial(i)) >= (self.selectedItem.GetCountMaterial(i)*count):
						self.cube_elements["count_elements_%d"%realSlotIndex].SetPackedFontColor(grp.GenerateColor(0.5411, 0.7254, 0.5568, 1.0))
					else:
						self.cube_elements["count_elements_%d"%realSlotIndex].SetPackedFontColor(grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0))
				else:
					if player.GetItemCountByVnum(self.selectedItem.GetVnumMaterial(i)) >= (self.selectedItem.GetCountMaterial(i)*count):
						self.cube_elements["count_elements_%d"%realSlotIndex].SetPackedFontColor(grp.GenerateColor(0.5411, 0.7254, 0.5568, 1.0))
					else:
						self.cube_elements["count_elements_%d"%realSlotIndex].SetPackedFontColor(grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0))

				if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
					if player.GetItemCountByVnum(self.selectedItem.GetVnumMaterial(i)) > 0 and player.GetItemCountByVnum(self.selectedItem.GetVnumMaterial(i)) <= 0:
						self.cube_elements["count_elements_%d"%realSlotIndex].SetText("%d/%d"%(player.GetItemCountByVnum(self.selectedItem.GetVnumMaterial(i)),self.selectedItem.GetCountMaterial(i)*count))
					else:
						self.cube_elements["count_elements_%d"%realSlotIndex].SetText("%d/%d"%(player.GetItemCountByVnum(self.selectedItem.GetVnumMaterial(i)),self.selectedItem.GetCountMaterial(i)*count))
				else:
					self.cube_elements["count_elements_%d"%realSlotIndex].SetText("%d/%d"%(player.GetItemCountByVnum(self.selectedItem.GetVnumMaterial(i)),self.selectedItem.GetCountMaterial(i)*count))
				self.cube_elements["count_elements_%d"%realSlotIndex].Show()
			else:
				self.cube_elements["count_elements_%d"%realSlotIndex].Hide() 
		#self.yang_text.SetHorizontalAlignLeft()
		# self.yang_text.SetWindowHorizontalAlignCenter()
		self.yang_text.SetText(localeinfo.NumberToMoneyString(self.selectedItem.GetGold()*count))
		self.yang_text.Show()
		self.gem_text.SetText(localeinfo.NumberToGemString(self.selectedItem.GetGem()*count))
		self.gem_text.Show()

		if long(self.selectedItem.GetGold()*count) < player.GetElk():
			self.yang_text.SetPackedFontColor(grp.GenerateColor(0.7607, 0.7607, 0.7607, 1.0))
		else:
			self.yang_text.SetPackedFontColor(grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0))

		if long(self.selectedItem.GetGem()*count) < player.GetGem():
			self.gem_text.SetPackedFontColor(grp.GenerateColor(0.7607, 0.7607, 0.7607, 1.0))
		else:
			self.gem_text.SetPackedFontColor(grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0))

	def ConvertInputResult(self):
		edit = int(self.result_qty.GetText())
		total = self.selectedItem.GetCountReward()
		convert = edit % total
		return convert

	def AceptInputItem(self):
		self.result_qty.KillFocus()

		result_total = int(self.result_qty.GetText())

		if int(self.result_qty.GetText()) < self.selectedItem.GetCountReward():
			result_total = self.selectedItem.GetCountReward()
		elif result_total > 2000:
			result_total = 2000
		else:
			result = self.ConvertInputResult()
			if result != 0:
				result_total = result_total-result

		self.count_item_reward = result_total
		self.result_qty.SetText("%d"%(result_total))

		count = (self.count_item_reward/(self.selectedItem.GetCountReward()))

		for i in xrange(0,6):
			self.icons_items.ClearSlot(i)
			if i == 0:
				self.icons_items.SetItemSlot(i,self.selectedItem.GetVnumReward(),self.count_item_reward)
			else:
				self.icons_items.SetItemSlot(i, self.selectedItem.GetVnumMaterial(i), self.selectedItem.GetCountMaterial(i)*count)
		
	def AceptCube(self):
		if self.selectedItem:
			index = self.selectedItem.GetIndex()
			self.CheckInputFocus()
			count = (self.count_item_reward/(self.selectedItem.GetCountReward()))
			index_improve = self.slot_item_improve

			cube_renewal.CubeRenewalMakeItem(index,count,index_improve)

	def QtyAddButton(self):
		if self.selectedItem and self.selectedItem.GetItemStackable():
			self.result_qty.SetText("%d"%(self.selectedItem.GetCountReward()*self.selectedItem.GetCount()))
			self.AceptInputItem()
			self.__ClickPreviousPageButton()

	def QtySubButton(self):
		if self.selectedItem and self.selectedItem.GetItemStackable():
			self.result_qty.SetText("%d"%(self.selectedItem.GetCountReward()))
			self.AceptInputItem()
			self.__ClickPreviousPageButton()

	def CheckInputFocus(self):
		if self.result_qty.IsFocus():
			self.result_qty.SetText("%d"%(self.selectedItem.GetCountReward()))
			self.AceptInputItem()

	def OnSelectItem(self, item):
		self.selectedItem = item

		if self.selectedItem:
			self.selectedItem.Select()

	def OnUpdate(self):
		if self.showingItemList:
			self.UpdateCountSubCategoria()
		if self.selectedItem:
			self.UpdateMaterialCount()

		index_improve = self.slot_item_improve
		if index_improve != -1:
			itemVNum = player.GetItemIndex(index_improve)
			itemCount = player.GetItemCount(index_improve)
			if itemVNum == self.vnum_item_improve and itemCount <= self.max_count_item_improve:
				self.slot_improve.SetItemSlot(0,itemVNum,itemCount)
			else:
				self.slot_improve.SetItemSlot(0,0,0)
				self.slot_item_improve = -1
		else:

			self.slot_improve.SetItemSlot(0,0,0)
			self.slot_item_improve = -1
		self.imporve_slot.Hide()
		self.GetChild("impove_text_window").Hide()

	def GetPorcentNew(self):
		index_improve = self.slot_item_improve
		if index_improve != -1:
			itemVNum = player.GetItemIndex(index_improve)
			itemCount = player.GetItemCount(index_improve)
			if itemVNum == self.vnum_item_improve and itemCount <= self.max_count_item_improve:
				return itemCount
		return 0

	def UpdateCountSubCategoria(self):
		for group in self.categoria_list:
			if group.IsOpen():
				for categorias in group.GetListSubCategorias():
					if categorias.IsOpen():
						for a in categorias.GetListSubCategoriasObjects():
							a.CountTotal()
							a.UpdatePorcentaje()

	def UpdateSelectSubCategoria(self):
		for group in self.categoria_list:
			for categorias in group.GetListSubCategorias():
				for a in categorias.GetListSubCategoriasObjects():
					a.UnSelect()
		self.selectedItem.SetSelect()

	def GetBoard(self):
		return self.board

	def GetSelf(self):
		return self		

	def SearchInWiki(self):
		vnum = self.tooltipIndex
		isBox = 1 if item.GetItemTypeByVnum(vnum) == item.ITEM_TYPE_GIFTBOX else 0
		if app.IsPressed(app.DIK_LSHIFT):
			if not self.wndWiki.IsShow():
				net.ToggleWikiWindow()
			self.wndWiki.CloseBaseWindows()

			if isBox:
				self.wndWiki.mainChestWindow.Show([vnum,])
			else:
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

	if app.ENABLE_RENDER_TARGET:
		def RenderItem(self, index):
			if app.IsPressed(app.DIK_LSHIFT):
				if self.selectedItem:
					if index == 0:
						vnum = self.selectedItem.GetVnumReward()
					else:
						index = index + (self.materialWindowIndex * 5)
						vnum = self.selectedItem.GetVnumMaterial(index)

					if uiRenderTarget.IsCanShowItems(vnum):
						interfaceHandler = systemSetting.GetInterfaceHandler()
						if interfaceHandler:
							interfaceHandler.OpenRenderTargetWindow(0, vnum)

	def OverInItem(self, index):
		self.toolTip.ClearToolTip()
		
		if self.selectedItem:
			if index == 0:
				vnum = self.selectedItem.GetVnumReward()
			else:
				index = index + (self.materialWindowIndex * 5)
				vnum = self.selectedItem.GetVnumMaterial(index)

			metinSlot = []
			AttrList = []

			check_item = index

			if check_item != 1 and index == 0:
				check_item_material = -1
				check_item_armour = 0
				
				if self.selectedItem.GetVnumMaterial(1) != 0:
					for i in xrange(player.INVENTORY_PAGE_SIZE):
						item_vnum = player.GetItemIndex(i)

						if item_vnum == self.selectedItem.GetVnumMaterial(1) and check_item_material == -1:
							check_item_material = i

					item.SelectItem(self.selectedItem.GetVnumMaterial(1))

					if item.GetItemType() == item.ITEM_TYPE_ARMOR and item.GetItemSubType() == item.ARMOR_BODY:
						check_item_armour = 1

					if check_item_material != -1:
						if check_item_armour == 1:
							for c in xrange(player.METIN_SOCKET_MAX_NUM):
								metinSlot.append(player.GetItemMetinSocket(check_item_material,c))
						else:
							for c in xrange(player.METIN_SOCKET_MAX_NUM):
								metinSlot.append(0)

						for b in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
							AttrList.append(player.GetItemAttribute(check_item_material,b))
					else:
						if check_item_armour == 1:
							for c in xrange(player.METIN_SOCKET_MAX_NUM):
								metinSlot.append(player.GetItemMetinSocket(check_item_material,c))
						else:
							for c in xrange(player.METIN_SOCKET_MAX_NUM):
								metinSlot.append(0)

						for b in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
							AttrList.append((0,0))
			else:
				check_item_material = -1

				if self.selectedItem.GetVnumMaterial(index) != 0:
					for i in xrange(player.INVENTORY_PAGE_SIZE):
						item_vnum = player.GetItemIndex(i)

						if item_vnum == self.selectedItem.GetVnumMaterial(index) and check_item_material == -1:
							check_item_material = i

					if check_item_material != -1:
						for c in xrange(player.METIN_SOCKET_MAX_NUM):
							metinSlot.append(player.GetItemMetinSocket(check_item_material,c))

						for b in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
							AttrList.append(player.GetItemAttribute(check_item_material,b))
					else:

						for c in xrange(player.METIN_SOCKET_MAX_NUM):
							metinSlot.append(0)

						for b in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
							AttrList.append((0,0))

		else:
			metinSlot = []
			for i in xrange(player.METIN_SOCKET_MAX_NUM):
				metinSlot.append(0)

			AttrList = []
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				AttrList.append((0,0))

		self.toolTip.AddItemData(vnum,metinSlot,AttrList,None,0)
		self.tooltipIndex = vnum
		self.toolTip.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_WIKI_HOVER)
		self.toolTip.DeclareShortcut(("key_alt", "key_rclick"), localeinfo.TOOLTIP_QUICKSEARCH_OFFLINESHOP)

	def OverOutItem(self):
		self.toolTip.Hide()
		self.tooltipIndex = 0
		
	def Close(self):
		cube_renewal.CubeRenewalClose()
		self.slot_item_improve = -1
		self.selectedItem = None
		self.gem_text.SetText(" ")
		if self.PreviousPageBtn.IsShow():
			self.PreviousPageBtn.Hide()
		if self.NextPageBtn.IsShow():
			self.NextPageBtn.Hide()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return TRUE
	def __ClickNextPageButton(self):
		self.materialWindowIndex = 1
		self.UpdateInfoSelect()
		self.UpdateMaterialCount()

		self.PreviousPageBtn.Show()
		self.NextPageBtn.Hide()

	def __ClickPreviousPageButton(self):
		self.materialWindowIndex = 0
		self.UpdateInfoSelect()
		self.UpdateMaterialCount()

		self.PreviousPageBtn.Hide()
		self.NextPageBtn.Show()
		self.NextPageBtn.Flash()
