# coding: utf-8

import app
import event
import item
import player
import net
import grp
import grpImage
import wndMgr
import ui
import uiscriptlocale
import localeinfo
import uicommon
import mousemodule
import item

from _weakref import proxy

STATE_NONE = 0
STATE_WAITING = 1
STATE_PLAY = 2

FISH_WAITING_PAGE_BOX_VISIBLE_LINE_COUNT = 8

fish_event_game_state = STATE_NONE

RESERVED_TYPE = 0
SPECIAL_TYPE = 1
NORMAL_TYPE = 2
FISH_EVENT_TYPE_MAX = 3

def LoadScript(self, fileName):
	pyScrLoader = ui.PythonScriptLoader()
	pyScrLoader.LoadScriptFile(self, fileName)

class FishEventGameWaitingPage(ui.ScriptWindow):
	class DescriptionBox(ui.Window):
		def __init__(self):
			ui.Window.__init__(self)
			self.descIndex = -1

		def __del__(self):
			ui.Window.__del__(self)

		def SetIndex(self, index):
			self.descIndex = index

		def OnRender(self):
			event.RenderEventSet(self.descIndex)

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		self.isLoaded = 0
		self.startButton = None
		self.descBoard = None
		self.descriptionBox = None
		self.descIndex = -1
		self.btnPrev = None
		self.btnNext = None
		self.MiniGameFish = None

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def SetMiniGameFish(self, mini_game_fish):
		self.MiniGameFish = mini_game_fish

	def __LoadWindow(self):
	
		if self.isLoaded == 1:
			return
			
		self.isLoaded = 1
		
		try:
			LoadScript(self, "uiscript/minigamefisheventwaitingpage.py")
		except:
			import exception
			exception.Abort("FishEventGameWaitingPage.LoadWindow.LoadObject")

		try:
			self.GetChild("titlebar").SetCloseEvent( ui.__mem_func__(self.Close) )
			self.startButton = self.GetChild("game_start_button")
			self.startButton.SetEvent(ui.__mem_func__(self.__ClickStartButton))

			self.descBoard = self.GetChild("desc_board")
			self.descriptionBox = self.DescriptionBox()
			self.descriptionBox.Hide()

			self.btnPrev = self.GetChild("prev_button")
			self.btnNext = self.GetChild("next_button")
			self.btnPrev.SetEvent(ui.__mem_func__(self.PrevDescriptionPage))
			self.btnNext.SetEvent(ui.__mem_func__(self.NextDescriptionPage))

			if localeinfo.IsARABIC():
				self.btnPrev.LeftRightReverse()
				self.btnNext.LeftRightReverse()
		except:
			import exception
			exception.Abort("FishEventGameWaitingPage.LoadWindow.BindObject")

		self.Hide()

	def Close(self):
		if self.descIndex != -1:
			event.ClearEventSet(self.descIndex)
			self.descIndex = -1

		if self.descriptionBox:
			self.descriptionBox.Hide()

		self.Hide()

	def Destroy(self):
		if self.descriptionBox:
			del self.descriptionBox
			self.descriptionBox = None

		self.descIndex = -1

		self.isLoaded = 0
		self.startButton = None
		self.descBoard = None
		self.btnPrev = None
		self.btnNext = None
		self.MiniGameFish = None

		self.ClearDictionary()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def __ClickStartButton(self):
		global fish_event_game_state
		fish_event_game_state = STATE_PLAY
		self.Close()

		if self.MiniGameFish:
			self.MiniGameFish.Open()

	def Show(self):
		ui.ScriptWindow.Show(self)

		if self.descIndex != -1:
			event.ClearEventSet(self.descIndex)

		self.descIndex = event.RegisterEventSet(uiscriptlocale.FISH_EVENT_DESC)

		event.SetFontColor(self.descIndex, 0.7843, 0.7843, 0.7843)
		event.SetVisibleLineCount( self.descIndex, FISH_WAITING_PAGE_BOX_VISIBLE_LINE_COUNT)

		total_line = event.GetTotalLineCount(self.descIndex)

		if localeinfo.IsARABIC():
			event.SetEventSetWidth(self.descIndex, self.descBoard.GetWidth() - 20)

		event.SetRestrictedCount(self.descIndex, 38)

		if FISH_WAITING_PAGE_BOX_VISIBLE_LINE_COUNT >= total_line:
			self.btnPrev.Hide()
			self.btnNext.Hide()
		else :
			self.btnPrev.Show()
			self.btnNext.Show()

		if self.descriptionBox:
			self.descriptionBox.SetIndex(self.descIndex)
			self.descriptionBox.Show()

	def OnUpdate(self):
		(x, y) = self.descBoard.GetGlobalPosition()
		event.UpdateEventSet(self.descIndex, x + 7, -(y + 7))
		self.descriptionBox.SetIndex(self.descIndex)

	def PrevDescriptionPage(self):
		if True == event.IsWait(self.descIndex):
			if event.GetVisibleStartLine(self.descIndex) - FISH_WAITING_PAGE_BOX_VISIBLE_LINE_COUNT >= 0:
				event.SetVisibleStartLine(self.descIndex, event.GetVisibleStartLine(self.descIndex) - FISH_WAITING_PAGE_BOX_VISIBLE_LINE_COUNT)
				event.Skip(self.descIndex)
		else:
			event.Skip(self.descIndex)

	def NextDescriptionPage(self):
		if True == event.IsWait(self.descIndex):
			event.SetVisibleStartLine(self.descIndex, event.GetVisibleStartLine(self.descIndex) + FISH_WAITING_PAGE_BOX_VISIBLE_LINE_COUNT)
			event.Skip(self.descIndex)
		else:
			event.Skip(self.descIndex)

class FishEventGamePage(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)

		self.inven = None
		self.interface = None
		self.tooltipitem = None

		self.isLoaded				= 0
		self.MiniGameFish			= None

		self.fish_box_slot			= [ 0 for col in range(0,FISH_EVENT_TYPE_MAX)]
		self.fish_box_slot_pos		= [-1 for col in range(0,FISH_EVENT_TYPE_MAX)]
		
		self.grid_slot				= None
		self.shape					= 0
		self.question_dialog		= None
		self.popup					= None
		self.use_count_text			= None
		self.use_count				= 0
		
		self.score_text_effect		= None
		self.score_effect1			= None
		self.score_effect2			= None
		self.score_effect3			= None
		self.reward_vnum			= 0

		self.fishPieceDict = {
			app.FISH_EVENT_SHAPE_1 : grpImage.Generate("d:/ymir work/ui/minigame/fish_event/fish_1.sub"),
			app.FISH_EVENT_SHAPE_2 : grpImage.Generate("d:/ymir work/ui/minigame/fish_event/fish_2.sub"),
			app.FISH_EVENT_SHAPE_3 : grpImage.Generate("d:/ymir work/ui/minigame/fish_event/fish_3.sub"),
			app.FISH_EVENT_SHAPE_4 : grpImage.Generate("d:/ymir work/ui/minigame/fish_event/fish_4.sub"),
			app.FISH_EVENT_SHAPE_5 : grpImage.Generate("d:/ymir work/ui/minigame/fish_event/fish_5.sub"),
			app.FISH_EVENT_SHAPE_6 : grpImage.Generate("d:/ymir work/ui/minigame/fish_event/fish_6.sub"),
			app.FISH_EVENT_SHAPE_7 : grpImage.Generate("d:/ymir work/ui/minigame/fish_event/fish_7.sub"),
		}

		if app.USE_V1:
			self.fishPiecePathDict = {
				app.FISH_EVENT_SHAPE_1 : "d:/ymir work/ui/minigame/fish_event/fish_1.sub",
				app.FISH_EVENT_SHAPE_2 : "d:/ymir work/ui/minigame/fish_event/fish_2.sub",
				app.FISH_EVENT_SHAPE_3 : "d:/ymir work/ui/minigame/fish_event/fish_3.sub",
				app.FISH_EVENT_SHAPE_4 : "d:/ymir work/ui/minigame/fish_event/fish_4.sub",
				app.FISH_EVENT_SHAPE_5 : "d:/ymir work/ui/minigame/fish_event/fish_5.sub",
				app.FISH_EVENT_SHAPE_6 : "d:/ymir work/ui/minigame/fish_event/fish_6.sub",
				app.FISH_EVENT_SHAPE_7 : "d:/ymir work/ui/minigame/fish_event/fish_7.sub",
			}

		self.fishPieceAdjustPosDict = {
			app.FISH_EVENT_SHAPE_1	: (0, -32),
			app.FISH_EVENT_SHAPE_2	: (0, 0),
			app.FISH_EVENT_SHAPE_3	: (-16, -16),
			app.FISH_EVENT_SHAPE_4	: (-16, -16),
			app.FISH_EVENT_SHAPE_5	: (-16, -16),
			app.FISH_EVENT_SHAPE_6	: (-32, -16),
			app.FISH_EVENT_SHAPE_7	: (-32, -16),
		}
		self.fishPieceSizeDict = {
			app.FISH_EVENT_SHAPE_1	: (1, 3),
			app.FISH_EVENT_SHAPE_2	: (1, 1),
			app.FISH_EVENT_SHAPE_3	: (2, 2),
			app.FISH_EVENT_SHAPE_4	: (2, 2),
			app.FISH_EVENT_SHAPE_5	: (2, 2),
			app.FISH_EVENT_SHAPE_6	: (3, 2),
			app.FISH_EVENT_SHAPE_7	: (3, 2),
		}
		
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def SetMiniGameFish(self, mini_game_fish):
		self.MiniGameFish = mini_game_fish

	def SetInven(self, inven):
		if inven:
			self.inven = proxy(inven)

	def BindInterface(self, interface):
		if interface:
			self.interface = proxy(interface)

	def SetItemToolTip(self, tooltip):
		if tooltip:
			self.tooltipitem = proxy(tooltip)

	def __LoadWindow(self):
	
		if self.isLoaded == 1:
			return
			
		self.isLoaded = 1
		
		try:
			LoadScript(self, "uiscript/minigamefishgamepage.py")
			
		except:
			import exception
			exception.Abort("FishEventGamePage.LoadWindow.LoadObject")
			
		try:
			self.GetChild("titlebar").SetCloseEvent(ui.__mem_func__(self.Close))
			self.GetChild("help_button").SetEvent(ui.__mem_func__(self.__ClickHelpButton))
				
			# special item slot
			special_item_slot = self.GetChild("SpecialItemSlot")
			special_item_slot.SetSelectEmptySlotEvent(ui.__mem_func__(self.__SelectEmptySlot), SPECIAL_TYPE)
			special_item_slot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem), SPECIAL_TYPE)
			special_item_slot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			special_item_slot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot), SPECIAL_TYPE)
			special_item_slot.SetUnselectItemSlotEvent(ui.__mem_func__(self.__UnselectItemSlot), SPECIAL_TYPE)
			self.fish_box_slot[SPECIAL_TYPE] = special_item_slot
			
			# normal item slot
			normal_item_slot = self.GetChild("NormalItemSlot")
			normal_item_slot.SetSelectEmptySlotEvent(ui.__mem_func__(self.__SelectEmptySlot), NORMAL_TYPE)
			normal_item_slot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem), NORMAL_TYPE)
			normal_item_slot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			normal_item_slot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot), NORMAL_TYPE)
			normal_item_slot.SetUnselectItemSlotEvent(ui.__mem_func__(self.__UnselectItemSlot), NORMAL_TYPE)
			self.fish_box_slot[NORMAL_TYPE] = normal_item_slot
			
			self.grid_slot = self.GetChild("GameSlot")
			self.grid_slot.SetSelectEmptySlotEvent( ui.__mem_func__(self.__SelectEmptyGameSlot) )
			self.grid_slot.SetUnselectEmptySlotEvent( ui.__mem_func__(self.__UnselectEmptyGameSlot) )
			self.grid_slot.SetUnselectItemSlotEvent( ui.__mem_func__(self.__UnselectItemGameSlotEvent) )
			
			self.use_count_text = self.GetChild("use_count_text")
			self.use_count_text.SetText( str(self.use_count) )
			
			## score completion side effect
			self.score_effect1 = self.GetChild("score_completion_effect1")
			self.score_effect2 = self.GetChild("score_completion_effect2")
			self.score_effect3 = self.GetChild("score_completion_effect3")
			self.score_effect1.SetScale(1.2, 1.2)
			self.score_effect2.SetScale(1.2, 1.2)
			self.score_effect3.SetScale(1.2, 1.2)
			self.score_effect1.Hide()
			self.score_effect2.Hide()
			self.score_effect3.Hide()
			self.score_effect1.SetEndFrameEvent( ui.__mem_func__(self.__ScoreEffectEndFrameEvent1) )
			self.score_effect2.SetEndFrameEvent( ui.__mem_func__(self.__ScoreEffectEndFrameEvent2) )
			self.score_effect3.SetEndFrameEvent( ui.__mem_func__(self.__ScoreEffectEndFrameEvent3) )
			
			## score completion text effect
			self.score_text_effect = self.GetChild("score_completion_text_effect")
			self.score_text_effect.SetEndFrameEvent( ui.__mem_func__(self.__ScoreTextEffectEndFrameEvent) )
			self.score_text_effect.Hide()
			
			if localeinfo.IsARABIC():
				(x1, y1) = self.score_effect1.GetLocalPosition()
				self.score_effect1.SetPosition(x1+60, y1)
				self.score_effect1.SetWindowHorizontalAlignLeft()
				
				(x2, y2) = self.score_effect2.GetLocalPosition()
				self.score_effect2.SetPosition(x2+60, y2)
				self.score_effect2.SetWindowHorizontalAlignLeft()
				
				(x3, y3) = self.score_effect3.GetLocalPosition()
				self.score_effect3.SetPosition(x3+60, y3)
				self.score_effect3.SetWindowHorizontalAlignLeft()

				(e_x, e_y) = self.score_text_effect.GetLocalPosition()
				self.score_text_effect.SetPosition(e_x+60, e_y)
				self.score_text_effect.SetWindowHorizontalAlignLeft()
				
				(s_x, s_y) = self.GetChild("SpecialItemSlotBG").GetLocalPosition()
				special_item_slot.SetPosition(s_x-7, s_y+7)
				special_item_slot.SetWindowHorizontalAlignRight()
				(n_x, n_y) = self.GetChild("NormalItemSlotBG").GetLocalPosition()
				normal_item_slot.SetPosition(n_x-7, n_y+7)
				normal_item_slot.SetWindowHorizontalAlignRight()

		except:
			import exception
			exception.Abort("FishEventGamePage.LoadWindow.BindObject")
		
		self.Hide()
		
	def OnPressEscapeKey(self):
		self.Close()
		return True
		
	def Close(self):
		if mousemodule.mouseController.isAttached() and mousemodule.mouseController.GetAttachedType() == player.SLOT_TYPE_FISH_EVENT:
			self.DropQuestionDialog()
			return

		self.SetOnTopWindowNone()
		self.ClearFishBoxSlot()
		app.ShowCursor()

		if self.tooltipitem:
			self.tooltipitem.HideToolTip()

		if self.popup:
			self.popup.Close()

		self.Hide()

	def Destroy(self):
		self.inven = None
		self.interface = None
		self.tooltipitem = None

		self.ClearFishBoxSlot()

		if mousemodule.mouseController.isAttached() and mousemodule.mouseController.GetAttachedType() == player.SLOT_TYPE_FISH_EVENT:
			self.__DropAccept()

		self.isLoaded				= 0
		self.MiniGameFish			= None
			
		if self.fish_box_slot:
			del self.fish_box_slot[:]
		if self.fish_box_slot_pos:
			del self.fish_box_slot_pos[:]

		self.grid_slot				= None
		self.shape					= 0
		self.popup					= None
		self.use_count_text			= None
		self.score_text_effect		= None
		self.score_effect1			= None
		self.score_effect2			= None
		self.score_effect3			= None
		self.reward_vnum			= 0

		for i in self.fishPieceDict.values():
			if app.USE_V1:
				del i
			else:
				grpImage.Delete(i)

		if app.USE_V1:
			self.fishPieceDict = {}
			self.fishPiecePathDict = {}

	def SetOnTopWindowNone(self):
		if not self.interface:
			return
			
		self.interface.SetOnTopWindow(player.ON_TOP_WND_NONE)
		self.interface.RefreshMarkInventoryBag()
		
	def OnTop(self):
		if not self.interface:
			return
			
		self.interface.SetOnTopWindow(player.ON_TOP_WND_FISH_EVENT)
		self.interface.RefreshMarkInventoryBag()

	def RefreshItem(self):
		if not self.IsShow():
			return

		special_item_pos = player.GetFishEventItemPos(item.ITEM_FISH_EVENT_BOX_SPECIAL)
		self.__AddFishEventSlot(SPECIAL_TYPE, special_item_pos)

		normal_item_pos = player.GetFishEventItemPos(item.ITEM_FISH_EVENT_BOX)
		self.__AddFishEventSlot(NORMAL_TYPE, normal_item_pos)

	def Show(self):
		ui.ScriptWindow.Show(self)
		
		# if 0 == self.use_count:
		# 	net.SendRequestFishEventBlock()

		mousemodule.mouseController.DeattachObjectPostProcess()
		self.RefreshItem()

	def __ClickHelpButton(self):
		if player.SLOT_TYPE_FISH_EVENT == mousemodule.mouseController.GetAttachedType():
			return
			
		global fish_event_game_state
		fish_event_game_state = STATE_WAITING
		self.Close()
		
		if self.MiniGameFish:
			self.MiniGameFish.Open()

	def OverInItem(self, slotIndex, type):
		if self.tooltipitem and self.fish_box_slot_pos[type] != -1:
			self.tooltipitem.SetInventoryItem( self.fish_box_slot_pos[type] )
			self.tooltipitem.DeclareShortcut(("key_shift", "key_rclick"), localeinfo.TOOLTIP_VIEW_CHEST_CONTENT)

	def	OverOutItem(self):
		if self.tooltipitem:
			self.tooltipitem.HideToolTip()

	def __UnselectItemSlot(self, slotIndex, type):
		if mousemodule.mouseController.isAttached():
			return

		if self.question_dialog:
			if self.question_dialog.IsShow():
				return

		self.ClearFishBoxSlot(type)

	def __UnselectEmptyGameSlot(self, slotIndex):
		
		if not mousemodule.mouseController.isAttached():
			return
			
		self.DropQuestionDialog()

		
	def	__UnselectItemGameSlotEvent(self, slotIndex):
		
		if not mousemodule.mouseController.isAttached():
			return
			
		self.DropQuestionDialog()

	def __AddFishEventSlot(self, type, pos):
		if -1 != self.fish_box_slot_pos[type]:
			return
			
		item_vnum  = player.GetItemIndex(player.INVENTORY, pos)
		item_count = player.GetItemCount(player.INVENTORY, pos)
		
		self.fish_box_slot_pos[type]	= pos
		self.fish_box_slot[type].SetItemSlot(0, item_vnum, item_count)
		self.fish_box_slot[type].ActivateSlot(0)
		self.fish_box_slot[type].RefreshSlot()
		
	def __SelectEmptySlot(self, slotIndex, type):
		if not mousemodule.mouseController.isAttached():
			return
		
		attachedSlotType = mousemodule.mouseController.GetAttachedType()
		attachedSlotPos = mousemodule.mouseController.GetAttachedSlotNumber()
		attachedItemCount = mousemodule.mouseController.GetAttachedItemCount()
		attachedItemIndex = mousemodule.mouseController.GetAttachedItemIndex()
		
		if player.SLOT_TYPE_INVENTORY != attachedSlotType:
			return
			
		mousemodule.mouseController.DeattachObject()
		if attachedSlotPos >= player.ITEM_SLOT_COUNT:
			return
			
		if NORMAL_TYPE == type:
			if item.ITEM_FISH_EVENT_BOX != attachedItemIndex:
				return
		elif SPECIAL_TYPE == type:
			if item.ITEM_FISH_EVENT_BOX_SPECIAL != attachedItemIndex:
				return
		else:
			return
					
		item_count = player.GetItemCount(player.INVENTORY, attachedSlotPos)
		
		self.fish_box_slot_pos[type]	= attachedSlotPos
		self.fish_box_slot[type].SetItemSlot(0, attachedItemIndex, item_count)
		self.fish_box_slot[type].ActivateSlot(0)
		self.fish_box_slot[type].RefreshSlot()
		
	def __SelectEmptyGameSlot(self,	slotIndex):
		if not mousemodule.mouseController.isAttached():
			return
			
		if 0 == self.shape:
			return
		
		attachedSlotType = mousemodule.mouseController.GetAttachedType()
		if player.SLOT_TYPE_FISH_EVENT != attachedSlotType:
			return
			
		if self.question_dialog:
			self.question_dialog.Close()
			del self.question_dialog

		self.question_dialog = uicommon.QuestionDialog()
		self.question_dialog.SetAcceptEvent(lambda arg = slotIndex : ui.__mem_func__(self.__AddAccept)(arg) )
		self.question_dialog.SetCancelEvent(ui.__mem_func__(self.__QuestionCancel))
		self.question_dialog.SetText( localeinfo.MINIGAME_FISH_EVENT_ADD_ACCEPT,false,true )
		self.question_dialog.Open()

		mousemodule.mouseController.SetAttachedIconRender(False)
		app.ShowCursor()

		if self.grid_slot:
			self.grid_slot.SetPickedAreaRender(False)

	def __AddAccept(self, slotIndex):
		self.__QuestionCancel()
		net.SendAddFishBox( slotIndex, self.shape)
		self.shape = 0
		self.DeattachObject()
		
	def MiniGameFishAdd(self, pos, shape):
		(width, height) = self.fishPieceSizeDict[shape]
		self.grid_slot.SetSlot(pos, shape, width, height, self.fishPiecePathDict[shape] if app.USE_V1 else grpImage.GetGraphicImagePointer(self.fishPieceDict[shape]))
		self.grid_slot.RefreshSlot()

	## ����Ʈ �߰��� ���� clear �� popup �� ����Ʈ ���� �� �߻�
	def MiniGameFishReward(self, vnum):
		
		self.reward_vnum = vnum
		self.__ClearCompletionEffect()
		if self.score_effect1:
			self.score_effect1.Show()
		if self.score_effect2:
			self.score_effect2.Show()
		if self.score_effect3:
			self.score_effect3.Show()
		if self.score_text_effect:
			self.score_text_effect.Show()
			
	
	def MiniGameFishCount(self, count):
		
		self.use_count = count
		if self.use_count_text:
			self.use_count_text.SetText( str(self.use_count) )
		
	def OnUpdate(self):
		if 0 == self.isLoaded:
			return
			
		if not self.inven:
			return
			
		for type in range(1, FISH_EVENT_TYPE_MAX):
			if self.fish_box_slot_pos[type] == -1:
				continue
				
			invenPage = self.inven.GetInventoryPageIndex() ## 0 or 1
			
			min_range = invenPage * player.INVENTORY_PAGE_SIZE			## 0 or 45
			max_range = (invenPage + 1) * player.INVENTORY_PAGE_SIZE	## 45 or 90
				
			inven_slot_pos = self.fish_box_slot_pos[type]
			if min_range <= inven_slot_pos < max_range:
				inven_slot_pos = inven_slot_pos - min_range
				if self.inven.wndItem:
					self.inven.wndItem.SetCantMouseEventSlot(inven_slot_pos)
			
	def ClearFishBoxSlot(self, type = FISH_EVENT_TYPE_MAX):
		if not self.inven:
			return
			
		if FISH_EVENT_TYPE_MAX == type:
			for index in range(1, FISH_EVENT_TYPE_MAX):
				if not self.fish_box_slot[index]:
					continue
				
				if self.fish_box_slot_pos[index] == -1:
					continue
				
				inven_slot_pos = self.fish_box_slot_pos[index]
					
				if inven_slot_pos >= player.INVENTORY_PAGE_SIZE:
					
					try:
						if app.ENABLE_EXTEND_INVEN_SYSTEM:
							inven_page = self.inven.GetInventoryPageIndex()
							inven_slot_pos -= (inven_page * player.INVENTORY_PAGE_SIZE)
						else:
							inven_slot_pos -= player.INVENTORY_PAGE_SIZE
					except:
						inven_slot_pos -= player.INVENTORY_PAGE_SIZE
							
				self.fish_box_slot[index].SetItemSlot(0, 0)
				self.fish_box_slot[index].DeactivateSlot(0)
				self.fish_box_slot[index].RefreshSlot()
				self.fish_box_slot_pos[index]	= -1
				
				if self.inven.wndItem:
					self.inven.wndItem.SetCanMouseEventSlot(inven_slot_pos)
			
		else:	
			if not self.fish_box_slot[type]:
				return
			
			if self.fish_box_slot_pos[type] == -1:
				return		
			
			inven_slot_pos = self.fish_box_slot_pos[type]
				
			if inven_slot_pos >= player.INVENTORY_PAGE_SIZE:
				
				try:
					if app.ENABLE_EXTEND_INVEN_SYSTEM:
						inven_page = self.inven.GetInventoryPageIndex()
						inven_slot_pos -= (inven_page * player.INVENTORY_PAGE_SIZE)
					else:
						inven_slot_pos -= player.INVENTORY_PAGE_SIZE
				except:
					inven_slot_pos -= player.INVENTORY_PAGE_SIZE
						
			self.fish_box_slot[type].SetItemSlot(0, 0)
			self.fish_box_slot[type].DeactivateSlot(0)
			self.fish_box_slot[type].RefreshSlot()
			self.fish_box_slot_pos[type]	= -1
			
			if self.inven.wndItem:
				self.inven.wndItem.SetCanMouseEventSlot(inven_slot_pos)

	def SelectItemSlot(self, slotIndex, type):
		if 0 != self.shape:
			return

		mousemodule.mouseController.DeattachObject()

		if self.question_dialog:
			self.question_dialog.Close()
			del self.question_dialog

		self.question_dialog = uicommon.QuestionDialog()
		self.question_dialog.SetAcceptEvent(lambda arg = type : ui.__mem_func__(self.__UseAccept)(arg))
		self.question_dialog.SetCancelEvent(ui.__mem_func__(self.__UseAcceptCancel))
		self.question_dialog.SetText(localeinfo.MINIGAME_FISH_EVENT_USE_ACCEPT)
		self.question_dialog.Open()

	def __UseAccept(self, type):
		self.__QuestionCancel()
		if self.fish_box_slot_pos[type] != -1:
			net.SendUseFishBox(player.SLOT_TYPE_INVENTORY, self.fish_box_slot_pos[type])

	def __UseAcceptCancel(self):
		if self.question_dialog:
			self.question_dialog.Close()
			self.question_dialog = None

	def __QuestionCancel(self):
		if self.question_dialog:
			self.question_dialog.Close()
			self.question_dialog = None

		if self.grid_slot:
			self.grid_slot.SetPickedAreaRender(True)

		mousemodule.mouseController.SetAttachedIconRender(True)
		app.HideCursor()

	def DropQuestionDialog(self):
		if self.question_dialog:
			self.question_dialog.Close()
			del self.question_dialog

		self.question_dialog = uicommon.QuestionDialog()
		self.question_dialog.SetAcceptEvent(ui.__mem_func__(self.__DropAccept))
		self.question_dialog.SetCancelEvent(ui.__mem_func__(self.__QuestionCancel))
		self.question_dialog.SetText( localeinfo.MINIGAME_FISH_EVENT_DROP_ACCEPT,true )
		self.question_dialog.Open()

		mousemodule.mouseController.SetAttachedIconRender(False)
		app.ShowCursor()
		
		if self.grid_slot:
			self.grid_slot.SetPickedAreaRender(False)

	def __DropAccept(self):
		self.__QuestionCancel()
		self.shape = 0
		app.ShowCursor()
		wndMgr.SetDisableDeattach(False)
		self.DeattachObject()
		
				
	def MiniGameFishUse(self, window, pos, shape):
		self.shape = shape
		
		for index in range(1, FISH_EVENT_TYPE_MAX):
			item_count = player.GetItemCount(window, self.fish_box_slot_pos[index])
			item_vnum  = player.GetItemIndex(window, self.fish_box_slot_pos[index])
			
			if 0 == item_count:
				self.ClearFishBoxSlot(index)
			else:
				self.fish_box_slot[index].SetItemSlot(0, item_vnum, item_count)
				self.fish_box_slot[index].RefreshSlot()
		
		app.HideCursor()
		(adjust_x, adjust_y) = self.fishPieceAdjustPosDict[shape]
		(width, height) = self.fishPieceSizeDict[shape]
		mousemodule.mouseController.AttachFishPiece( self, shape, self.fishPieceDict[shape], adjust_x, adjust_y, width, height)
		
		for type in range(1, FISH_EVENT_TYPE_MAX):
			self.fish_box_slot[type].DeactivateSlot(0)
			
		wndMgr.SetDisableDeattach(True)
		
		self.use_count += 1
		if self.use_count_text:
			self.use_count_text.SetText( str(self.use_count) )
		
	def DeattachObject(self):
		mousemodule.mouseController.DeattachObjectPostProcess()
		
		for type in range(1, FISH_EVENT_TYPE_MAX):
			item_count = player.GetItemCount(player.INVENTORY, self.fish_box_slot_pos[type])
			if item_count:
				self.fish_box_slot[type].ActivateSlot(0)
			else:
				self.fish_box_slot[type].DeactivateSlot(0)
	
	def __ScoreEffectEndFrameEvent1(self):
		if self.score_effect1:
			self.score_effect1.Hide()
		
	def __ScoreEffectEndFrameEvent2(self):
		if self.score_effect2:
			self.score_effect2.Hide()
		
	def __ScoreEffectEndFrameEvent3(self):
		if self.score_effect3:
			self.score_effect3.Hide()
						
	def __ScoreTextEffectEndFrameEvent(self):
		
		if self.score_text_effect: 
			self.score_text_effect.Hide()
			
		self.use_count = 0
		if self.use_count_text:
			self.use_count_text.SetText( str(self.use_count) )
		
		for slotPos in xrange(self.grid_slot.GetSlotCount()):
			self.grid_slot.ClearSlot(slotPos)
		self.grid_slot.RefreshSlot()
		
		if not self.popup:
			self.popup = uicommon.PopupDialog()
			
		item.SelectItem(self.reward_vnum)
		item_name = item.GetItemName()
		self.popup.SetText( localeinfo.MINIGAME_FISH_EVENT_REWARD_MSG % item_name )
		self.popup.Open()
		self.reward_vnum = 0
		
	def __ClearCompletionEffect(self):
		if self.score_text_effect:
			self.score_text_effect.Hide()
			self.score_text_effect.ResetFrame()
			self.score_text_effect.SetDelay(6)
		
		if self.score_effect1:
			self.score_effect1.Hide()
			self.score_effect1.ResetFrame()
			self.score_effect1.SetDelay(6)
		
		if self.score_effect2:
			self.score_effect2.Hide()
			self.score_effect2.ResetFrame()
			self.score_effect2.SetDelay(6)
		
		if self.score_effect3:
			self.score_effect3.Hide()
			self.score_effect3.ResetFrame()
			self.score_effect3.SetDelay(6)
			
		
class MiniGameFish(ui.Window):
	def RefreshItem(self):
		if self.game_page:
			self.game_page.RefreshItem()

	def __init__(self):
		ui.Window.__init__(self)

		self.inven = None
		self.interface = None
		self.tooltipitem = None

		self.isLoaded		= 0
		
		self.cur_page		= None
		self.waiting_page	= None
		self.game_page		= None
		
		self.__LoadWindow()
		
	def __del__(self):
		ui.Window.__del__(self)
		
	def Show(self):
		self.__LoadWindow()
		ui.Window.Show(self)

	def Close(self):
		self.Hide()
		
		if self.cur_page:
			self.cur_page.Close()

	def Destroy(self):
		self.inven = None
		self.interface = None
		self.tooltipitem = None

		global fish_event_game_state
		fish_event_game_state	= STATE_NONE
		self.isLoaded			= 0
		self.cur_page			= None
		if self.waiting_page:
			self.waiting_page.Destroy()

		if self.game_page:
			self.game_page.Destroy()

	def __LoadWindow(self):
		
		if self.isLoaded == 1:
			return
			
		self.isLoaded	= 1
		global fish_event_game_state
		fish_event_game_state		= STATE_WAITING
		
		try:
			## ���� ����â
			self.waiting_page	= FishEventGameWaitingPage()
			self.waiting_page.SetMiniGameFish(self)
			
			## ���� ����â
			self.game_page		= FishEventGamePage()
			self.game_page.SetMiniGameFish(self)
		except:
			import exception
			exception.Abort("MiniGameFish.LoadWindow")
		
		self.Hide()

	def SetInven(self, inven):
		if inven:
			self.inven = proxy(inven)

			if self.game_page:
				self.game_page.SetInven(inven)

	def BindInterface(self, interface):
		if interface:
			self.interface = proxy(interface)

			if self.game_page:
				self.game_page.BindInterface(interface)

	def SetItemToolTip(self, tooltip):
		if tooltip:
			self.tooltipitem = proxy(tooltip)

			if self.game_page:
				self.game_page.SetItemToolTip(tooltip)

	def Open(self):
		global fish_event_game_state
		
		if STATE_WAITING == fish_event_game_state:
			self.cur_page = self.waiting_page
			
		elif STATE_PLAY == fish_event_game_state:
			self.cur_page = self.game_page
			
		else:
			return
			
		if self.cur_page.IsShow():
			self.cur_page.Close()
		else:
			self.cur_page.Show()
			self.cur_page.SetTop()
	
	def MiniGameFishUse(self, window, pos, shape):
		
		if STATE_PLAY != fish_event_game_state:
			return
			
		self.cur_page.MiniGameFishUse(window, pos, shape)
		
		
	def MiniGameFishAdd(self, pos, shape):
			
		if STATE_PLAY != fish_event_game_state:
			return
			
		self.cur_page.MiniGameFishAdd( pos, shape )
		
	def MiniGameFishReward(self, vnum):
	
		if STATE_PLAY != fish_event_game_state:
			return
			
		self.cur_page.MiniGameFishReward( vnum )
		
	def MiniGameFishCount(self, count):
	
		if STATE_PLAY != fish_event_game_state:
			return
			
		self.cur_page.MiniGameFishCount( count )
		
	def CantFishEventSlot(self, InvenSlot):
		ItemVnum = player.GetItemIndex(InvenSlot)
		if ItemVnum in [item.ITEM_FISH_EVENT_BOX, item.ITEM_FISH_EVENT_BOX_SPECIAL]:
			return False
				
		return True