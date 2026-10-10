# coding: latin_1

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import net
import player

import ui
import dbg
import chat
import uitooltip
import wndMgr
import localeinfo
import playersettingmodule
import oxevent
import intrologin, item, ime, grp, uicommon

EMPIRE_NAME = { 
	net.EMPIRE_A : localeinfo.EMPIRE_A, net.EMPIRE_B : localeinfo.EMPIRE_B, net.EMPIRE_C : localeinfo.EMPIRE_C 
}

PATH_IMAGE__UNKNOWN_WINNER = "d:/ymir work/ui/path_oxevent/face/face_unknown.tga"

FACE_IMAGE_DICT = {
	playersettingmodule.RACE_WARRIOR_M : "d:/ymir work/ui/path_oxevent/face/face_warrior_m_01.sub",
	playersettingmodule.RACE_WARRIOR_W : "d:/ymir work/ui/path_oxevent/face/face_warrior_w_01.sub",
	playersettingmodule.RACE_ASSASSIN_M : "d:/ymir work/ui/path_oxevent/face/face_assassin_m_01.sub",
	playersettingmodule.RACE_ASSASSIN_W	: "d:/ymir work/ui/path_oxevent/face/face_assassin_w_01.sub",
	playersettingmodule.RACE_SURA_M : "d:/ymir work/ui/path_oxevent/face/face_sura_m_01.sub",
	playersettingmodule.RACE_SURA_W : "d:/ymir work/ui/path_oxevent/face/face_sura_w_01.sub",
	playersettingmodule.RACE_SHAMAN_M : "d:/ymir work/ui/path_oxevent/face/face_shaman_m_01.sub",
	playersettingmodule.RACE_SHAMAN_W : "d:/ymir work/ui/path_oxevent/face/face_shaman_w_01.sub",
}
#if app.ENABLE_WOLFMAN_CHARACTER:
	#FACE_IMAGE_DICT.update({playersettingmodule.RACE_WOLFMAN_M : "d:/ymir work/ui/path_oxevent/face/face_wolf_m_01.sub",})

class OxEventManagerLogin(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.Initialize()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/oxeventmanagerlogin.py")
		except:
			import exception
			exception.Abort("OxEventManagerLogin.Initialize.LoadObject")
		try:
			self.GetChild("accept_button").SetEvent(self.Login)
			self.GetChild("cancel_button").SetEvent(self.Close)
			self.GetChild("titlebar").SetCloseEvent(self.Close)

			self.LinePassword = self.GetChild("currentLine_Value")
			self.LinePassword.SetFocus()
		except:
			import exception
			exception.Abort("OxEventManagerLogin.Initialize.BindObject")
		self.SetCenterPosition()

	def Destroy(self):
		self.ClearDictionary()

	def Close(self):
		self.Hide()

	def Login(self):
		oxevent.Manager(oxevent.LOGIN, str(self.LinePassword.GetText()), oxevent.EMPTY_VALUE, oxevent.EMPTY_VALUE)
		self.Hide()

	def Open(self):
		import intrologin
		self.connectDialog = intrologin.ConnectingDialog()
		self.connectDialog.Open(3.0)
		self.connectDialog.SetText(localeinfo.OXEVENT_MANAGER_BTN_LOGIN)
		self.connectDialog.SAFE_SetTimeOverEvent(self.Login)
		self.connectDialog.SAFE_SetExitEvent(self.Close)

class OxEventManager(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.row = 0		
		self.key = 0
		self.itemName = ""
		self.vnumIndex = []
		self.listKeys = []
		self.wndOpenQuestion = {}
		self.pageKey = ["open_event", "close_gates", "close_event", "reward_players", "ask_question", "close_force", "clear_reward"]
		self.ITEM_LIST = player.GetItemList()
		self.Initialize()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/oxeventmanager.py")
		except:
			import exception
			exception.Abort("OxEventManager.Initialize.LoadObject")
		try:
			GetObject = self.GetChild	
			self.main = {
				"rewards" : {
					"password" : oxevent.EMPTY_PASSWORD,
					"vnum" : oxevent.EMPTY_VNUM,
					"count" : oxevent.EMPTY_COUNT
				},
				"elements" :
				{
					"board" : GetObject("Board"),
					"participants" : GetObject("current_participants"),
					"slot_vnum" : GetObject("slot_vnum_value"),
					"slot_count" : GetObject("slot_count_value"),
					"slot_image" : GetObject("slot_image_value"),
					"listbox_bar" : GetObject("listbox_bar"),					
					"listbox" : GetObject("ListBox")
				},			
				"btn" :
				{
					"open_event" : GetObject("open_button_btn"),
					"close_gates" : GetObject("close_gates_btn"),
					"close_event" : GetObject("close_event_btn"),
					"close_force" : GetObject("force_close_event_btn"),
					"reward_players" : GetObject("reward_players_btn"),
					"ask_question" : GetObject("ask_question_btn"),
					"clear_reward" : GetObject("clear_reward_btn"),
				}
			}
			
			for key in xrange(oxevent.APPEND_WINDOW):
				self.main["btn"][self.pageKey[key]].SAFE_SetEvent(self.AskQuestionPacket, key + 1)

			self.main["elements"]["slot_vnum"].SetEscapeEvent(self.Close)
			self.main["elements"]["slot_vnum"].OnIMEUpdate = ui.__mem_func__(self.OnUpdateKeyVnum)

			self.main["elements"]["slot_count"].SetEscapeEvent(self.Close)
			self.main["elements"]["slot_count"].OnIMEUpdate = ui.__mem_func__(self.OnUpdateKeyCount)
			self.main["elements"]["slot_count"].SetNumberMode()

			self.main["elements"]["listbox"].SetEvent(self.OnClick)
			self.main["elements"]["board"].SetCloseEvent(self.Close)
		except:
			import exception
			exception.Abort("OxEventManager.Initialize.BindObject")

		self.main["elements"]["slot_image"].Hide()
		
		self.itemTooltip = uitooltip.ItemToolTip()
		self.itemTooltip.HideToolTip()

		self.SetStatusListBox(0)
		self.SetCenterPosition()
		self.UpdateRect()
		
	def SetStatusListBox(self, key):
		for it in [self.main["elements"]["listbox"], self.main["elements"]["listbox_bar"]]:
			if key == 0:
				it.Hide()
			else:
				it.Show()
				
	def GetIsSearchedVnum(self):
		return ((self.main["rewards"]["vnum"] != oxevent.EMPTY_VNUM) and (self.main["rewards"]["count"] != oxevent.EMPTY_COUNT))
		
	def OnUpdateKeyCount(self):
		ui.EditLine.OnIMEUpdate(self.main["elements"]["slot_count"])

		def GetText():
			return self.main["elements"]["slot_count"].GetText()
			
		def GetIsTextDigit(val):
			return (val.isdigit())
			
		def IsStackable():
			item.SelectItem(int(self.main["rewards"]["vnum"]))
			return (item.IsAntiFlag(item.ITEM_ANTIFLAG_STACK))
			
		def IsDenied(val):
			return (int(val) > oxevent.ITEM_MAX_COUNT)

		val = GetText()
		if GetIsTextDigit(val):
			it = int(val)

			if IsDenied(it):
				self.main["elements"]["slot_count"].SetText(str(oxevent.ITEM_MAX_COUNT))

			self.main["rewards"]["count"] = it

	def OnUpdateKeyVnum(self):
		ui.EditLine.OnIMEUpdate(self.main["elements"]["slot_vnum"])

		def GetText():
			return str(self.main["elements"]["slot_vnum"].GetText())

		def GetTextSize():
			return len(GetText())

		def SetKey(key):
			if key in [oxevent.CLEAR_DATA, oxevent.REFRESH_DATA]:
				self.vnumIndex = []
				self.listKeys = []
				self.row = 0
				
			if key != oxevent.REFRESH_DATA:
				self.SetStatusListBox(0)

			self.main["elements"]["listbox"].ClearItem()

		def GetItemCountListBox():
			return self.main["elements"]["listbox"].GetItemCount()

		def SetSizeListBox():
			for it in [self.main["elements"]["listbox"], self.main["elements"]["listbox_bar"]]:
				it.SetSize(200, 17.5 * GetItemCountListBox())
		
		if GetTextSize() <= oxevent.NEED_SIZE:
			SetKey(oxevent.CLEAR_DATA)
			return

		SetKey(oxevent.REFRESH_DATA)
		c_szText = GetText()

		for key in self.ITEM_LIST:
			c_szItem, c_szName = key["index"], key["name"]

			if len(c_szName) >= len(c_szText) and c_szName[:len(c_szText)].lower() == c_szText.lower():
				self.listKeys.append(c_szItem)

		for key in xrange(len(self.listKeys)):
			if self.row >= oxevent.MAX_ROWS:
				break

			item.SelectItem(self.listKeys[key])
			c_szName = item.GetItemName()

			self.main["elements"]["listbox"].InsertItem(key, c_szName)
			self.vnumIndex.append(self.listKeys[key])
			self.row += 1

		self.SetStatusListBox(1)
		SetSizeListBox()

		if len(self.vnumIndex) == (oxevent.NEED_SIZE - 1):
			SetKey(oxevent.CLEAR_DATA)
			return
			
	def AppendTextLine(self, c_szName):
		self.itemName = c_szName
		self.main["elements"]["slot_vnum"].SetText(c_szName)
		self.main["elements"]["slot_vnum"].SetFocus()

	def OnClick(self, key, c_szName):

		def Clear():
			self.SetStatusListBox(0)
			self.main["elements"]["listbox"].ClearItem()
			self.row = 0
			
		def ShowImage():
			if self.GetIsSearchedVnum():
				item.SelectItem(self.main["rewards"]["vnum"])
				try:
					self.main["elements"]["slot_image"].LoadImage(item.GetIconImageFileName())
					self.main["elements"]["slot_image"].Show()
				except:
					dbg.TraceError("OxEventManager.LoadImage - Failed to find item data")
		
		def MoveCursor(text):
			ime.SetCursorPosition(len(text) + 1)

		def SetItemVnum(key):
			self.key = key
			self.main["rewards"]["vnum"] = self.vnumIndex[self.key]
			self.main["elements"]["slot_count"].SetText(str(oxevent.NEED_SIZE))
			self.main["rewards"]["count"] = 1

		self.AppendTextLine(c_szName)
		SetItemVnum(key)
		MoveCursor(c_szName)
		ShowImage()
		Clear()
		
	def OnUpdate(self):
		def PermisionOnToolTip():
			return ((self.main["elements"]["slot_image"].IsShow() and self.main["elements"]["slot_image"].IsIn()) and self.GetIsSearchedVnum())

		if PermisionOnToolTip():
			self.itemTooltip.SetItemToolTip(self.main["rewards"]["vnum"])
		else:
			self.itemTooltip.HideToolTip()

	def ClearList(self):
		self.main["rewards"]["vnum"] = 0
		self.AppendTextLine(oxevent.EMPTY_PASSWORD)
		self.main["elements"]["slot_count"].SetText(str(oxevent.NEED_SIZE))
		self.main["elements"]["slot_image"].Hide()
		
	def RefreshCounter(self, participantsCount, observersCount):
		self.main["elements"]["participants"].SetText(localeinfo.OXEVENT_MANAGER_USER_COUNT % (participantsCount, observersCount))
		
	def AnswerWithKey(self, answer, key):

		if not self.wndOpenQuestion[key]:
			return

		self.wndOpenQuestion[key].Close()
		self.wndOpenQuestion[key] = None
		
		if not answer:		
			return
			
		if key in (oxevent.OPEN_EVENT, oxevent.CLOSE_GATES, oxevent.CLOSE_EVENT, oxevent.ASK_QUESTION, oxevent.FORCE_CLOSE_EVENT):
			oxevent.Manager(key, oxevent.EMPTY_PASSWORD, oxevent.EMPTY_VALUE, oxevent.EMPTY_VALUE)
		else:
			if self.GetIsSearchedVnum():
				oxevent.Manager(key, oxevent.EMPTY_PASSWORD, self.main["rewards"]["vnum"], self.main["rewards"]["count"])
				self.ClearList()
		
	def AskQuestionPacket(self, key):
		def resize(key):
			return ("|cFFb6ff7d%s|r" % str(key))

		self.QUESTION_DESCRIPTION = {
			oxevent.OPEN_EVENT : localeinfo.OXEVENT_MANAGER_QUEST_OPEN_GATES,			
			oxevent.CLOSE_GATES : localeinfo.OXEVENT_MANAGER_QUEST_CLOSE_GATES,
			oxevent.CLOSE_EVENT : localeinfo.OXEVENT_MANAGER_QUEST_FINISH_EVENT,
			oxevent.REWARD_PLAYERS : (localeinfo.OXEVENT_MANAGER_QUEST_GIVE_REWARD % (resize(self.main["rewards"]["vnum"]), resize(self.itemName), resize(self.main["rewards"]["count"]))),
			oxevent.ASK_QUESTION : localeinfo.OXEVENT_MANAGER_QUEST_RUN_QUIZ,
			oxevent.FORCE_CLOSE_EVENT : localeinfo.OXEVENT_MANAGER_QUEST_FORCE_CLOSE,
			oxevent.CLEAR_REWARD : localeinfo.OXEVENT_MANAGER_QUEST_CLEAR_REWARD			
		}
		
		if key == oxevent.REWARD_PLAYERS and not self.GetIsSearchedVnum():
			return

		self.wndOpenQuestion[key] = uicommon.QuestionDialog()
		self.wndOpenQuestion[key].SetText(self.QUESTION_DESCRIPTION[key])
		self.wndOpenQuestion[key].SetWidth(450)
		self.wndOpenQuestion[key].SetAcceptEvent(lambda arg = TRUE, key = key: self.AnswerWithKey(arg, key))
		self.wndOpenQuestion[key].SetCancelEvent(lambda arg = FALSE, key = key: self.AnswerWithKey(arg, key))
		self.wndOpenQuestion[key].Open()
		
	def OpenWindow(self):
		self.Show()

	def Close(self):
		self.itemTooltip.HideToolTip()
		self.Hide()

class OxEventWinners(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.textToolTip = None
		self.Initialize()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/oxeventwinners.py")
		except:
			import exception
			exception.Abort("OxEventWinners.Initialize.LoadObject")
		try:
			GetObject = self.GetChild
			self.main = {
				"data" : {
					"real_name" : {}, "name" : {}, "level" : {}, "guild" : {}, "empire" : {}, "real_job" : {}, "job" : {}, "date" : {}, "real_correct_answers" : {}, "correct_answers" : {}
				},
				"elements" :
				{
					"board" : GetObject("board"),
					"slot" : [GetObject("character_slot_%d" % (i + 1)) for i in xrange(oxevent.MAX_RANGE)],						
					"name" : [GetObject("character_name_%d" % (i + 1)) for i in xrange(oxevent.MAX_RANGE)],						
					"face" : [GetObject("character_face_%d" % (i + 1)) for i in xrange(oxevent.MAX_RANGE)],	
					"answers" : [GetObject("character_answers_%d" % (i + 1)) for i in xrange(oxevent.MAX_RANGE)],				
				}
			}

		except:
			import exception
			exception.Abort("OxEventWinners.Initialize.BindObject")

		self.main["elements"]["board"].SetSize(175, 235)
		self.SetPosition(-120, wndMgr.GetScreenHeight() - 450)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : (-120, Expr("SCREEN_HEIGHT") - 450)})
		self.UpdateRect()
		
	def GetCurrentKeys(self):
		return ([self.main["data"]["real_name"], self.main["data"]["name"], self.main["data"]["level"], self.main["data"]["guild"], self.main["data"]["empire"], self.main["data"]["real_job"], self.main["data"]["job"], self.main["data"]["date"], self.main["data"]["real_correct_answers"], self.main["data"]["correct_answers"]])
		
	def GetExistKey(self, key):
		self.sumKeys = self.GetCurrentKeys()

		return (self.sumKeys[key].get(key) != localeinfo.OXEVENT_TOOLTIP_EMPTY)
		
	def GetRealFace(self, index):
		return FACE_IMAGE_DICT[index]
		
	def AppendTextLine(self):
		for key in xrange(oxevent.MAX_RANGE):
			if self.GetExistKey(key):
				self.main["elements"]["name"][key].SetText(self.main["data"]["real_name"].get(key))
				self.main["elements"]["answers"][key].SetText(str(self.main["data"]["real_correct_answers"].get(key)))
				self.main["elements"]["face"][key].LoadImage(self.GetRealFace(self.main["data"]["real_job"].get(key)))
			else:
				self.main["elements"]["face"][key].LoadImage(PATH_IMAGE__UNKNOWN_WINNER)				

	def Append(self):

		def resize(key):
			return ("|cFFfffbaa%s|r" % str(key))

		def GetEmpire(index):
			return resize(EMPIRE_NAME[index])

		for key in xrange(oxevent.MAX_RANGE):
			row = oxevent.GetWinners(key)
			name, level, guild, empire, job, date, correct_answers = row[0], row[1], row[2], row[3], row[4], row[5], row[6]

			if level == oxevent.EMPTY_DATA: 

				for keyEmpty in self.GetCurrentKeys():
					keyEmpty.update({key : localeinfo.OXEVENT_TOOLTIP_EMPTY})

			else:
				self.main["data"]["real_name"].update({key : name})
				self.main["data"]["name"].update({key : (localeinfo.OXEVENT_TOOLTIP_NAME % resize(name))})

				self.main["data"]["level"].update({key : (localeinfo.OXEVENT_TOOLTIP_LEVEL % resize(level))})
				self.main["data"]["guild"].update({key : (localeinfo.OXEVENT_TOOLTIP_GUILD % resize(guild))})
				self.main["data"]["empire"].update({key : (localeinfo.OXEVENT_TOOLTIP_EMPIRE % GetEmpire(empire))})
				
				self.main["data"]["real_job"].update({key : job})
				self.main["data"]["job"].update({key : self.GetRealFace(job)})

				self.main["data"]["date"].update({key : (localeinfo.OXEVENT_TOOLTIP_DATE % resize(date))})

				self.main["data"]["real_correct_answers"].update({key : correct_answers})
				self.main["data"]["correct_answers"].update({key : (localeinfo.OXEVENT_TOOLTIP_ANSWERS % resize(correct_answers))})
	
		self.AppendTextLine()
		self.Show()
		
	def OnUpdate(self):
		(x, y) = wndMgr.GetMousePosition()

		for key in xrange(oxevent.MAX_RANGE):
			if self.main["elements"]["slot"][key].IsIn() ^ self.main["elements"]["face"][key].IsIn():
				if self.GetExistKey(key):
					self.textToolTip = uitooltip.ToolTip()
					self.textToolTip.SetPosition(x + 15, y)
					self.textToolTip.AppendPlayersDesc(self.main["data"]["name"].get(key),self.main["data"]["level"].get(key),self.main["data"]["guild"].get(key), self.main["data"]["empire"].get(key),self.main["data"]["job"].get(key), self.main["data"]["date"].get(key),self.main["data"]["correct_answers"].get(key))

	def Openwindow(self):
		if self.IsShow():
			self.Hide()
		else:
			self.Show()