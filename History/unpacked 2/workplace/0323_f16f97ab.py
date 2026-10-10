import ui, player, chr, net, wndMgr, player
import app

ACTIVE_SKILL_LIST = {
	0 : { 
		1 : (1, 2, 3, 4, 5, 6,), 
		2 : (16, 17, 18, 19, 20, 21,), 
	},
	1 : { 
		1 : (31, 32, 33, 34, 35, 36,), 
		2 : (46, 47, 48, 49, 50, 51,), 
	},
	2 : { 
		1 : (61, 62, 63, 64, 65, 66,),
		2 : (76, 77, 78, 79, 80, 81,),
	},
	3 : { 
		1 : (91, 92, 93, 94, 95, 96,),
		2 : (106, 107, 108, 109, 110, 111,),
	},
	4 : {
		1 : (170, 171, 172, 173, 174, 175,),  # wolfman
	}
}

class SkillLearnWindow(ui.ScriptWindow):
	def __init__(self):
		super(SkillLearnWindow, self).__init__()
		
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__LoadScript()
		self.selected_index = -1

	def __del__(self):
		super(SkillLearnWindow, self).__del__()
		del self.selected_index

	def Destroy(self):
		self.ClearDictionary()

	def Close(self):
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Open(self):
		self.RefreshStatus()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def __LoadScript(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/learnskill.py")

		except:
			import exception
			exception.Abort("LearnSkill.__LoadScript.LoadObject")

		try:
			self.board = self.GetChild("board")
			self.normal_skill = self.GetChild("normal_skill")
			self.normal_skill_slot = self.GetChild("normal_skill_slot")
			self.learn = self.GetChild("learn")
			self.learn_once = self.GetChild("learn_once")
		except:
			import exception
			exception.Abort("LearnSkill.__LoadScript.BindObject")

		
		self.board.SetCloseEvent(ui.__mem_func__(self.Close))
		
		self.learn_once.SAFE_SetEvent(self.Learn, False)
		self.learn.SAFE_SetEvent(self.Learn, True)

	def Learn(self, isFast):
		net.SendChatPacket("/learn_skill %d %d" % (self.selected_index, int(isFast)))

	def SelectSkill(self, value):
		skillIndexx = player.GetSkillIndex(value+1)
		skillGrade = player.GetSkillGrade(value+1)
		if skillGrade < 4 and skillGrade != 0:
			for i in xrange(0,self.normal_skill_slot.GetSlotCount()):
				if i == value:
					self.normal_skill_slot.ActivateSlot(i)
					self.normal_skill_slot.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_GREEN)
				else:
					self.normal_skill_slot.DeactivateSlot(i)
			
			self.selected_index = skillIndexx
			
			self.normal_item_slot.SetItemSlot(0, int (ACTIVE_SKILL_ITEM_LIST[skillGrade][0]), 0)		
			self.normal_item_slot.SetItemSlot(1, int (ACTIVE_SKILL_ITEM_LIST[skillGrade][1]), 0)		
			self.normal_item_slot.SetItemSlot(2, int (ACTIVE_SKILL_ITEM_LIST[skillGrade][2]), 0)							

		else:
			import chat
			chat.AppendChat(1,"You don't upgrade this skill.")


	def RefreshStatus(self):		
		for i in xrange(0,self.normal_skill_slot.GetSlotCount()):
			self.normal_skill_slot.ClearSlot(i)

		race = net.GetMainActorRace()
		group = net.GetMainActorSkillGroup()
		job = chr.RaceToJob(race)

		if ACTIVE_SKILL_LIST.has_key(job):
			if ACTIVE_SKILL_LIST[job].has_key(group):
				activeSkillList = ACTIVE_SKILL_LIST[job][group]
				for i in xrange(len(activeSkillList)):
					skillIndexx = activeSkillList[i]
					skillLevel = player.GetSkillLevel(i+1)
					skillGrade = player.GetSkillGrade(i+1)
					self.normal_skill_slot.SetSkillSlotNew(i, skillIndexx, skillGrade, skillLevel)
					self.normal_skill_slot.SetSlotCountNew(i, skillGrade, skillLevel)
					self.normal_skill_slot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
					self.normal_skill_slot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectSkill))
						
		self.normal_skill_slot.RefreshSlot()
