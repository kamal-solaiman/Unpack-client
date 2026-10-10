# coding: latin_1

import ui
import localeinfo

import net
import player

class PartyBonusDistributeWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)

		self.attackerButton = None
		self.berserkerButton = None
		self.tankerButton = None
		self.defenderButton = None
		self.bufferButton = None
		self.skillMasterButton = None

		self.LoadWindow()
		self.LoadObjects()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def LoadWindow(self):
		try:
			PythonScriptLoader = ui.PythonScriptLoader()
			PythonScriptLoader.LoadScriptFile(self, "UIScript/PartyBonusDistributeWindow.py")
		except:
			import exception
			exception.Abort("PartyBonusDistributeWindow.LoadWindow.LoadObject")

		try:
			self.attackerButton = self.GetChild("AttackerButton")
			self.berserkerButton = self.GetChild("BerserkerButton")
			self.tankerButton = self.GetChild("TankerButton")
			self.defenderButton = self.GetChild("DefenderButton")
			self.bufferButton = self.GetChild("BufferButton")
			self.skillMasterButton = self.GetChild("SkillMasterButton")
		except:
			import exception
			exception.Abort("PartyBonusDistributeWindow.LoadWindow.BindObject")

	def LoadObjects(self):
		try:
			self.attackerButton.SetEvent(ui.__mem_func__(self.OnClickAttacker))
			self.berserkerButton.SetEvent(ui.__mem_func__(self.OnClickBerserker))
			self.tankerButton.SetEvent(ui.__mem_func__(self.OnClickTanker))
			self.defenderButton.SetEvent(ui.__mem_func__(self.OnClickDefender))
			self.bufferButton.SetEvent(ui.__mem_func__(self.OnClickBuffer))
			self.skillMasterButton.SetEvent(ui.__mem_func__(self.OnClickSkillMaster))

			slotIndex = player.GetSkillSlotIndex(player.SKILL_INDEX_TONGSOL)
			if slotIndex:
				skillLevel = player.GetSkillLevel(slotIndex)
				if skillLevel <= 0:
					return

				skillCurrentPercentage = player.GetSkillCurrentEfficientPercentage(slotIndex)
				self.attackerButton.SetToolTipText(localeinfo.PARTY_SKILL_ATTACKER % int(10 + 60 * skillCurrentPercentage), 64, 60)
				self.berserkerButton.SetToolTipText(localeinfo.PARTY_SKILL_BERSERKER % int(1 + 5 * skillCurrentPercentage), 64, 60)
				self.tankerButton.SetToolTipText(localeinfo.PARTY_SKILL_TANKER 	% int(50 + 1450 * skillCurrentPercentage), 64, 60)
				self.defenderButton.SetToolTipText(localeinfo.PARTY_SKILL_DEFENDER % int(5 + 30 * skillCurrentPercentage), 64, 60)
				self.bufferButton.SetToolTipText(localeinfo.PARTY_SKILL_BUFFER % int(5 + 45 * skillCurrentPercentage), 64, 60)
				#self.skillMasterButton.SetToolTipText(localeinfo.PARTY_SKILL_NEW)
		except:
			import exception
			exception.Abort("PartyBonusDistributeWindow.__LoadObjects.SetEvent")

	def OnClickAttacker(self):
		net.SendRequestPartyBonus(player.PARTY_STATE_ATTACKER)

	def OnClickBerserker(self):
		net.SendRequestPartyBonus(player.PARTY_STATE_BERSERKER)

	def OnClickTanker(self):
		net.SendRequestPartyBonus(player.PARTY_STATE_TANKER)

	def OnClickDefender(self):
		net.SendRequestPartyBonus(player.PARTY_STATE_DEFENDER)

	def OnClickBuffer(self):
		net.SendRequestPartyBonus(player.PARTY_STATE_BUFFER)

	def OnClickSkillMaster(self):
		net.SendRequestPartyBonus(player.PARTY_STATE_SKILL_MASTER)

	def AdjustPosition(self, x, y):
		self.SetPosition(x, y)

	def Close(self):
		self.Hide()

	def Destroy(self): 
		self.ClearDictionary()

		self.attackerButton = None
		self.berserkerButton = None
		self.tankerButton = None
		self.defenderButton = None
		self.bufferButton = None
		self.skillMasterButton = None

	def Open(self):
		ui.ScriptWindow.Show(self)

	def OnPressEscapeKey(self):
		self.Close()
		return True
