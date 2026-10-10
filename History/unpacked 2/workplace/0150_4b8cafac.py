# coding: latin_1

import app

import ui
import chat
import localeinfo
import anti_multiple_farm

MAX_RESULT_IN_PAGE = 5 #the design was developed for this number of result, do not change if you keep this design
MULTIPLE_FARM_STATE_IMAGES = ["d:/ymir work/ui/pattern/visible_mark_01.tga", "d:/ymir work/ui/pattern/visible_mark_03.tga"]

VIEW_MODE = 0
EDIT_MODE = 1

class player_data(ui.ScriptWindow):
	def __init__(self, wndParent, wndMainClass):
		def __MakePage():
			self.SetParent(wndParent)
			self.SetSize(220, 20)
			self.Show()
		
		if not wndMainClass:
			return
		
		ui.ScriptWindow.__init__(self)
		__MakePage()
		self.wndMainClass = wndMainClass
		
		self.__SetUpData()
		self.__SetUpObjects()
	
	def __del__(self):
		ui.ScriptWindow.__del__(self)
	
	def Destroy(self):
		self.__DestroyObjects()
		self.__SetUpData()
	
	def __SetUpData(self):
		self.player_name = ""
		self.player_pid = -1
		self.player_status = 0
	
	def __SetUpObjects(self):
		self.objPlayerName = None
		self.objPlayerStatus = None
		self.objCheckBox = None
	
	def __DestroyObjects(self):
		if self.objPlayerName:
			self.objPlayerName.Hide()
		if self.objPlayerStatus:
			self.objPlayerStatus.Hide()
		if self.objCheckBox:
			self.objCheckBox.Hide()
		
		self.__SetUpObjects()
	
	def NewDataBuild(self, player_name, player_pid, player_status):
		self.__LoadData(player_name, player_pid, player_status)
		
		self.objPlayerName = ui.MakeTextLineWithouAlign(self, "", 10+10, 7)
		self.objPlayerName.SetHorizontalAlignRight()
		self.objPlayerName.SetText(self.player_name)
		
		try: statusImage = MULTIPLE_FARM_STATE_IMAGES[self.player_status]
		except: statusImage = MULTIPLE_FARM_STATE_IMAGES[0]
		self.objPlayerStatus = ui.MakeImageBox(self, statusImage, 140+20, 7)
		
		self.objCheckBox = ui.MakeOptionsCheckBox(self, "", 142+20, 8)
		self.objCheckBox.SetCheckStatus(bool(not player_status))
		self.objCheckBox.SetEvent(ui.__mem_func__(self.wndMainClass.OnClickEditStatus), "ON_CHECK", True, self.GetPID())
		self.objCheckBox.SetEvent(ui.__mem_func__(self.wndMainClass.OnClickEditStatus), "ON_UNCKECK", False, self.GetPID())
		
		return (self)
	
	def __LoadData(self, player_name, player_pid, player_status):
		self.player_name = player_name
		self.player_pid = player_pid
		self.player_status = player_status
	
	def SetDataState(self, flag):
		if flag == EDIT_MODE:
			self.SetStatus(self.player_status)
			self.objPlayerStatus.Hide()
			self.objCheckBox.Show()
		else:
			self.objPlayerStatus.Show()
			self.objCheckBox.Hide()
	
	def SetStatus(self, player_status):
		self.player_status = player_status
		self.objCheckBox.SetCheckStatus(bool(not self.player_status))
		try: statusImage = MULTIPLE_FARM_STATE_IMAGES[self.player_status]
		except: statusImage = MULTIPLE_FARM_STATE_IMAGES[0]
		self.objPlayerStatus.LoadImage(statusImage)
	
	def GetStatus(self):
		return self.player_status
	
	def SetPreStatus(self, player_status):
		self.objCheckBox.SetCheckStatus(bool(not player_status))
	
	def GetPreStatus(self):
		return self.objCheckBox.GetCheckStatus()
	
	def GetPID(self):
		return self.player_pid
	
	def GetName(self):
		return self.player_name

class AntiMultipleFarmWnd(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__SetUpData()
		self.__SetUpObjects()
		
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)
	
	def __SetUpData(self):
		self.player_data = []
		self.data_count = 0
		self.page_manage_mode = VIEW_MODE
	
	def __ClearOldData(self):
		if len(self.player_data) != 0:
			for player_data in self.player_data:
				player_data.Destroy()
		
		self.__SetUpData()
	
	def __SetUpObjects(self):
		self.main_layer_parent = None
		self.scrollbar = None
		
		self.edit_button = None
		self.close_button = None
		self.refresh_button = None

		self.save_edit_button = None
		self.close_edit_button = None
	
	def __LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/antimultiplefarmwindow.py")
			
			GetObject = self.GetChild
			
			self.main_layer_parent = GetObject("anti_farm_bg_layer")
			
			self.scrollbar = GetObject("scrollbar")
			self.scrollbar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
			
			self.edit_button = GetObject("edit_button")
			self.edit_button.SetEvent(ui.__mem_func__(self.OnClickEditButton))
			
			self.close_button = GetObject("close_button")
			self.close_button.SetEvent(ui.__mem_func__(self.OnClickCloseButton))
			
			self.refresh_button = GetObject("refresh_button")
			self.refresh_button.SetEvent(ui.__mem_func__(self.OnRefreshData))
			
			self.save_edit_button = GetObject("save_edit_button")
			self.save_edit_button.SetEvent(ui.__mem_func__(self.OnSaveEditStatus))
			
			self.close_edit_button = GetObject("close_edit_button")
			self.close_edit_button.SetEvent(ui.__mem_func__(self.OnClickEditButton), VIEW_MODE)
		
		except:
			import exception
			exception.Abort("AntiMultipleFarmWnd.__LoadScript.LoadObject")
	
	def __RefreshData(self):
		for idx in xrange(anti_multiple_farm.GetAntiFarmPlayerCount()):
			name, pid, status = anti_multiple_farm.GetAntiFarmPlayerData(idx)
			self.player_data.append(player_data(self.main_layer_parent, self).NewDataBuild(name, pid, status))
			self.player_data[idx].SetPosition(0, 15 + (idx*19))
			self.player_data[idx].SetDataState(self.page_manage_mode)
			self.player_data[idx].Show() if idx < MAX_RESULT_IN_PAGE else self.player_data[idx].Hide()
		
		self.__RefreshDataResult()
		self.__RefreshScrollBar()
	
	def OnSaveEditStatus(self):
		if self.page_manage_mode != EDIT_MODE:
			return
		
		allowed_pids = self.__GetPreAllowedPIDS()
		if self.__GetAllowedPIDS() == allowed_pids:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.ANTI_MULTIPLE_FARM_ADVISE_2)
			return
		
		if len(allowed_pids) < anti_multiple_farm.MULTIPLE_FARM_MAX_ACCOUNT:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.ANTI_MULTIPLE_FARM_ADVISE_3.format(anti_multiple_farm.MULTIPLE_FARM_MAX_ACCOUNT))
			return
		
		chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.ANTI_MULTIPLE_FARM_ATTEND_CHANGE_STATUS)
		self.OnClickEditButton(VIEW_MODE)
		anti_multiple_farm.SendAntiFarmStatus(*tuple(allowed_pids))
	
	def OnClickEditButton(self, mode = None):
		self.page_manage_mode = not self.page_manage_mode if not mode else mode
		self.__RefreshEditMode()
	
	def OnClickCloseButton(self):
		self.Close()
		return True
	
	def __GetPreAllowedPIDS(self):
		pids = []
		for player_data in self.player_data:
			if player_data.GetPreStatus():
				pids.append(player_data.GetPID())
		
		return pids[:anti_multiple_farm.MULTIPLE_FARM_MAX_ACCOUNT]
	
	def __CountPreFreeDropPlayers(self):
		count = 0
		for player_data in self.player_data:
			count += int(player_data.GetPreStatus())
		
		return count

	def __GetAllowedPIDS(self):
		pids = []
		for player_data in self.player_data:
			if bool(not player_data.GetStatus()):
				pids.append(player_data.GetPID())
		
		return pids[:anti_multiple_farm.MULTIPLE_FARM_MAX_ACCOUNT]
	
	def OnClickEditStatus(self, checkArg, status, PID):
		if self.page_manage_mode != EDIT_MODE:
			self.OnClickEditButton(EDIT_MODE)
		
		player_data = self.__GetPlayerDataByPID(PID)
		if not player_data:
			return
		
		if self.__CountPreFreeDropPlayers() > anti_multiple_farm.MULTIPLE_FARM_MAX_ACCOUNT:
			player_data.SetPreStatus(status)
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.ANTI_MULTIPLE_FARM_ADVISE_1.format(anti_multiple_farm.MULTIPLE_FARM_MAX_ACCOUNT))
	
	def __RefreshEditMode(self):
		for player_data in self.player_data:
			player_data.SetDataState(self.page_manage_mode)
		
		wndTable = [self.GetChild("view_window"), self.GetChild("edit_window")]
		wndTable[self.page_manage_mode].Show()
		wndTable[not self.page_manage_mode].Hide()
	
	def __GetPlayerDataByPID(self, PID):
		for player_data in self.player_data:
			if player_data.GetPID() == PID:
				return player_data
		return None
	
	def OnRefreshData(self):
		self.__ClearOldData()
		self.__RefreshEditMode()
		self.__RefreshData()

	def OnRunMouseWheel(self, nLen):
		self.scrollbar.OnUp() if nLen > 0 else self.scrollbar.OnDown()
		return True
	
	def __OnScroll(self):
		if self.data_count <= MAX_RESULT_IN_PAGE:
			return
		
		old_scroll_pos = self.scrollbar.GetPos()
		pos = int(old_scroll_pos * (self.data_count - MAX_RESULT_IN_PAGE))
		
		new_idx = 0
		for idx in xrange(self.data_count):
			player_data = self.player_data[idx]
			if (idx < pos or idx >= (pos + MAX_RESULT_IN_PAGE)):
				player_data.Hide()
			else:
				player_data.SetPosition(0, 15 + (new_idx*19))
				player_data.Show()
				new_idx+=1
	
	def __RefreshScrollBar(self):
		if not self.scrollbar:
			return
		
		if self.data_count:
			new_mid_bar_size = min(0.94, (float(MAX_RESULT_IN_PAGE) / float(self.data_count)))
			self.scrollbar.SetMiddleBarSize(new_mid_bar_size)
		self.scrollbar.SetPos(0.0)
	
	def __RefreshDataResult(self):
		self.data_count = len(self.player_data)
	
	def Open(self):
		self.OnRefreshData()
		
		self.SetCenterPosition()
		self.Show()
		self.SetTop()
	
	def Close(self):
		self.__ClearOldData()
		self.Hide()
	
	def OnPressEscapeKey(self):
		self.Close() if self.page_manage_mode != EDIT_MODE else self.OnClickEditButton(VIEW_MODE)
		return True
