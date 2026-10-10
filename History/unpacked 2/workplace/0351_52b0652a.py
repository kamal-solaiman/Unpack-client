# coding: latin_1
#
# Pet "Upgrade" sub-window (growth pet rework, U3) -- binder.
# Layout lives in uiscript/petupgradewindow.py (tab rail + Evolve / Upgrade Type
# pages); this module binds the widgets, wires the tabs/buttons and fills the pages:
#
#   Evolve tab: the re-hosted legacy evolve flow --
#     requirements = uipetinfo.EVOLVE_MATERIALS_DICT[currentEvol] (client-side single
#     source, same as the legacy PetEvolveDialog) + required pet level via the legacy
#     window's GetEvolInfo(); gate = its IsActivateEvolButton() (emits the refusal
#     chat lines); send = net.SendPetFeedPacket(player.FEED_EVOL_EVENT, [], []).
#   Upgrade Type tab: fed by the GC pet-rework-info push --
#     player.GetPetTypeInfo() (type/ceiling/pity/chance/caps) +
#     player.GetPetTypeUpgradeCost() (yang + <=5 materials); send =
#     net.SendPetTypeUpgrade(). The server answers both outcomes with a fresh info
#     push -> interface.RefreshCompanionPetPage -> Refresh() here while shown.
import ui
import app
import net
import grp
import skill
import player
import localeinfo
import uitooltip
import uicommon
import uipetinfo

TAB_EVOLVE = 0
TAB_TYPE   = 1

# Count-text colors (grp floats avoid the 0xAARRGGBB channel-flip), matching the
# buffi Upgrade window: green = player owns enough of the material, red = short.
COLOR_HAVE_ENOUGH = grp.GenerateColor(0.5411, 0.7254, 0.5568, 1.0)
COLOR_NOT_ENOUGH  = grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0)

def FillMaterialColumns(slotWnd, countTexts, vnumStore, mats):
	# Shared by the Upgrade window pages and the Skill Upgrade dialog. Clear every column,
	# then fill the used ones: icon in the slot, required count below it colored green
	# (owned enough) / red (short). vnumStore feeds the hover tooltip.
	total = len(vnumStore)
	for i in range(total):
		vnumStore[i] = 0
		if slotWnd:
			slotWnd.ClearSlot(i)
		if i < len(countTexts) and countTexts[i]:
			countTexts[i].SetText("")
	for i in range(min(len(mats), total)):
		vnum, need = mats[i][0], mats[i][1]
		vnumStore[i] = vnum
		if slotWnd:
			slotWnd.SetItemSlot(i, vnum, 0)
		if i < len(countTexts) and countTexts[i]:
			have = player.GetItemCountByVnum(vnum)
			countTexts[i].SetText(str(need))
			countTexts[i].SetPackedFontColor(COLOR_HAVE_ENOUGH if have >= need else COLOR_NOT_ENOUGH)
	if slotWnd:
		slotWnd.RefreshSlot()

class PetUpgradeWindow(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Initialize()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		self.isLoaded    = 0
		self.board       = None
		self.interface   = None   # set by interfacemodule (evolve gate reuses wndPetInfoWindow)
		self.currentTab  = TAB_EVOLVE
		self.tabButtons  = []     # rail radio-buttons, indexed by TAB_*
		self.evolvePage  = None
		self.typePage    = None
		# Evolve page widgets
		self.evoHeaderText = None
		self.evoMatSlot    = None
		self.evoMatCounts  = []            # 5 count TextLines (index-parallel, may hold None)
		self.evoMatVnums   = [0, 0, 0, 0, 0]  # shown vnums (hover tooltip)
		self.evoReqText    = None
		self.evoBtn        = None
		# Type page widgets
		self.typHeaderText = None
		self.typCapText    = None
		self.typMatSlot    = None
		self.typMatCounts  = []            # 5 count TextLines (index-parallel, may hold None)
		self.typMatVnums   = [0, 0, 0, 0, 0]
		self.typChanceText = None
		self.typPriceText  = None
		self.typPityText   = None
		self.typBtn        = None
		# Shared
		self.matToolTip  = None   # lazily-created item tooltip (material hover)
		self.tabToolTip  = None   # lazily-created boarded tooltip for the rail tabs (the engine
		                          # SetToolTipText draws in the window's own layer -> clips behind it)
		self.questionDlg = None   # confirm dialog (evolve / type attempt)

	def Destroy(self):
		if self.questionDlg:
			self.questionDlg.Close()
			self.questionDlg = None
		self.ClearDictionary()
		self.Initialize()

	# ------------------------------------------------------------------
	# Load + bind
	# ------------------------------------------------------------------
	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/petupgradewindow.py")

		# Best-effort bind: a layout/locale error logs to syserr instead of aborting client boot.
		try:
			self.board = self.GetChild("board")
			self.board.SetTitleName(getattr(localeinfo, "COMPANION_PET_UPGRADE_TITLE", "Pet - Upgrade"))
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
			self.__BindWidgets()
		except:
			import dbg
			dbg.TraceError("PetUpgradeWindow.__LoadWindow - bind failed")

	def __BindWidgets(self):
		self.evolvePage = self.GetChild2("evolvePage")
		self.typePage   = self.GetChild2("typePage")
		self.tabButtons = []
		for name, tab in (("tabEvolve", TAB_EVOLVE), ("tabType", TAB_TYPE)):
			btn = self.GetChild2(name)
			if btn:
				btn.SAFE_SetEvent(self.__OnClickTab, tab)
				# Boarded hover tooltip instead of SetToolTipText (the engine tooltip is a child
				# TextLine of the tab, and the board -- declared after the rail -- draws over it).
				# GOTCHA: CRadioButton::OnMouseOverIn does NOT dispatch Python OnMouseOverIn
				# (SetOverEvent never fires on radio buttons); the C++ calls ShowToolTip /
				# HideToolTip on the handler instead -- so hook THOSE, per tab. __mem_func__
				# keeps the instance attributes cycle-free (weakref proxy).
				if tab == TAB_EVOLVE:
					btn.ShowToolTip = ui.__mem_func__(self.__OnTabOverInEvolve)
				else:
					btn.ShowToolTip = ui.__mem_func__(self.__OnTabOverInType)
				btn.HideToolTip = ui.__mem_func__(self.__OnTabOverOut)
			self.tabButtons.append(btn)
		# Evolve page
		self.evoHeaderText = self.GetChild2("evoHeaderText")
		self.evoMatSlot    = self.GetChild2("evoMaterialSlot")
		if self.evoMatSlot:
			self.evoMatSlot.SetOverInItemEvent(ui.__mem_func__(self.__OnEvoMatOverIn))
			self.evoMatSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OnMatOverOut))
		self.evoMatCounts = []
		for i in range(5):
			self.evoMatCounts.append(self.GetChild2("evoMatCount%d" % i))
		self.evoReqText = self.GetChild2("evoReqText")
		self.evoBtn     = self.GetChild2("evoAcceptButton")
		if self.evoBtn:
			self.evoBtn.SetEvent(ui.__mem_func__(self.__OnClickEvolve))
		# Type page
		self.typHeaderText = self.GetChild2("typHeaderText")
		self.typCapText    = self.GetChild2("typCapText")
		self.typMatSlot    = self.GetChild2("typMaterialSlot")
		if self.typMatSlot:
			self.typMatSlot.SetOverInItemEvent(ui.__mem_func__(self.__OnTypMatOverIn))
			self.typMatSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OnMatOverOut))
		self.typMatCounts = []
		for i in range(5):
			self.typMatCounts.append(self.GetChild2("typMatCount%d" % i))
		self.typChanceText = self.GetChild2("typChanceText")
		self.typPriceText  = self.GetChild2("typPriceText")
		self.typPityText   = self.GetChild2("typPityText")
		self.typBtn        = self.GetChild2("typAcceptButton")
		if self.typBtn:
			self.typBtn.SetEvent(ui.__mem_func__(self.__OnClickTypeUpgrade))
		# "?" -> the Upgrade explainer popup (interface owns the window).
		btnHelp = self.GetChild2("helpButton")
		if btnHelp:
			btnHelp.SetEvent(ui.__mem_func__(self.__OnClickHelp))
			btnHelp.SetToolTipText(getattr(localeinfo, "PET_UP_HELP_TITLE", "Pet Upgrade - Help"), 0, -16)

	# ------------------------------------------------------------------
	# Open / tabs / refresh
	# ------------------------------------------------------------------
	def Open(self):
		petID = player.GetActivePetItemId()
		if 0 == petID:
			return
		# Default tab: Evolve while an evolution is still ahead, else straight to Type
		# (a fully-evolved pet has nothing on the Evolve page but the "final" notice).
		(petLevel, evolLevel, birthday, petNick, s0, s1, s2) = player.GetPetItem(petID)
		tab = TAB_EVOLVE
		if self.__GetEvolRequiredLevel(evolLevel) == 0:
			tab = TAB_TYPE
		self.__SetTab(tab)
		self.SetCenterPosition()
		self.SetTop()
		self.Show()
		self.Refresh()

	def __OnClickTab(self, tab):
		self.__SetTab(tab)
		self.Refresh()
		# Evolution and Type upgrade have SEPARATE help pages -- keep an open help
		# window in sync with the tab the player is looking at.
		if self.interface and hasattr(self.interface, "SyncPetUpgradeHelp"):
			self.interface.SyncPetUpgradeHelp(tab)

	def __OnClickHelp(self):
		# Open the ACTIVE tab's help page (toggle; interface owns the window).
		if self.interface and hasattr(self.interface, "OpenPetUpgradeHelp"):
			self.interface.OpenPetUpgradeHelp(self.currentTab)

	def __SetTab(self, tab):
		self.currentTab = tab
		for i in range(len(self.tabButtons)):
			btn = self.tabButtons[i]
			if not btn:
				continue
			if i == tab:
				btn.Down()
			else:
				btn.SetUp()
		if self.evolvePage:
			if tab == TAB_EVOLVE:
				self.evolvePage.Show()
			else:
				self.evolvePage.Hide()
		if self.typePage:
			if tab == TAB_TYPE:
				self.typePage.Show()
			else:
				self.typePage.Hide()
		if self.matToolTip:
			self.matToolTip.HideToolTip()
		if self.questionDlg:
			self.questionDlg.Close()

	def Refresh(self):
		# Called on open/tab switch, by interface.RefreshCompanionPetPage (the GC info
		# push after every Type attempt) and by RefreshStatus deltas (evolution lands).
		if not self.isLoaded or not self.IsShow():
			return
		petID = player.GetActivePetItemId()
		if 0 == petID:
			self.Close()   # pet dismissed/died while the dialog was up
			return
		(petLevel, evolLevel, birthday, petNick, s0, s1, s2) = player.GetPetItem(petID)
		if self.currentTab == TAB_EVOLVE:
			self.__RefreshEvolve(evolLevel)
		else:
			self.__RefreshType()

	def __GetEvolRequiredLevel(self, evolLevel):
		# Single source = the legacy pet window's GetEvolInfo (lv 40 / 80 / 81; 0 = maxed
		# or invalid). Reached through the interface back-ref; 0 on any missing link.
		iface = getattr(self, "interface", None)
		petWnd = getattr(iface, "wndPetInfoWindow", None) if iface else None
		if petWnd:
			try:
				return petWnd.GetEvolInfo(evolLevel)
			except:
				pass
		return 0

	def __RefreshEvolve(self, evolLevel):
		reqLevel = self.__GetEvolRequiredLevel(evolLevel)
		maxed = (reqLevel == 0)
		if self.evoHeaderText:
			if maxed:
				self.evoHeaderText.SetText(getattr(localeinfo, "COMPANION_PET_EVO_MAX", "Final evolution reached."))
			else:
				fmt = getattr(localeinfo, "COMPANION_PET_EVO_HEADER", "Evolution %s -> %s")
				self.evoHeaderText.SetText(fmt % (evolLevel, evolLevel + 1))
		# Materials: the same client-side dict the legacy PetEvolveDialog renders
		# (keyed by the CURRENT evolution); server-side validation is authoritative.
		mats = []
		if not maxed:
			matsDict = getattr(uipetinfo, "EVOLVE_MATERIALS_DICT", None)
			if matsDict:
				mats = matsDict.get(evolLevel, [])
		self.__FillMaterials(self.evoMatSlot, self.evoMatCounts, self.evoMatVnums, mats)
		if self.evoReqText:
			if maxed:
				self.evoReqText.SetText("")
			else:
				fmt = getattr(localeinfo, "COMPANION_PET_EVO_REQ", "Requires Pet Lv. %s")
				self.evoReqText.SetText(fmt % reqLevel)
		if self.evoBtn:
			if maxed:
				self.evoBtn.Hide()
			else:
				self.evoBtn.Show()

	def __RefreshType(self):
		if not hasattr(player, "GetPetTypeInfo"):
			return
		(petType, typeMax, evoCeiling, failCount, pityMax, chance, capPermille, nextCapPermille) = player.GetPetTypeInfo()
		if petType == 0:
			# No info push received yet (it re-sends on summon; this state is brief).
			# Disarm the Confirm button too -- no data means nothing sensible to send.
			if self.typHeaderText:
				self.typHeaderText.SetText("-")
			if self.typCapText:
				self.typCapText.SetText("")
			self.__FillMaterials(self.typMatSlot, self.typMatCounts, self.typMatVnums, [])
			for w in (self.typChanceText, self.typPriceText, self.typPityText):
				if w:
					w.SetText("")
			if self.typBtn:
				self.typBtn.Hide()
			return
		maxed = (petType >= typeMax)
		if self.typHeaderText:
			if maxed:
				self.typHeaderText.SetText(getattr(localeinfo, "COMPANION_PET_TYPE_MAX", "Maximum Type reached."))
			else:
				fmt = getattr(localeinfo, "COMPANION_PET_TYPE_UP_HEADER", "Type %s -> %s")
				self.typHeaderText.SetText(fmt % (petType, petType + 1))
		# Costs (yang + <=5 materials) from the same info push.
		mats = []
		yang = 0
		if not maxed and hasattr(player, "GetPetTypeUpgradeCost"):
			cost = player.GetPetTypeUpgradeCost()
			yang = cost[0]
			for pair in cost[1:]:
				if pair[0]:
					mats.append(pair)
		self.__FillMaterials(self.typMatSlot, self.typMatCounts, self.typMatVnums, mats)
		if self.typPriceText:
			if maxed:
				self.typPriceText.SetText("")
			else:
				money = localeinfo.NumberToMoneyStringNoUnit(yang) if hasattr(localeinfo, "NumberToMoneyStringNoUnit") else str(yang)
				fmt = getattr(localeinfo, "COMPANION_UPGRADE_COST", "Upgrade Price: %s")
				self.typPriceText.SetText(fmt % money)
		# Strip shows the stat-cap change -- WHAT the upgrade buys (user feedback 2026-07-04:
		# replaced the need-evolve notice; the server's refusal message covers that gate, and
		# the header two-liner was too cramped for the cap text).
		if self.typChanceText:
			if maxed:
				self.typChanceText.SetText("")
			else:
				fmt = getattr(localeinfo, "COMPANION_PET_TYPE_CAP_FMT", "Stat cap %s%% -> %s%%")
				self.typChanceText.SetText(fmt % ("%0.1f" % (capPermille / 10.0), "%0.1f" % (nextCapPermille / 10.0)))
			# >>> SECTION BEGIN: former state-notice branches, kept for revival.
			# elif petType >= evoCeiling:
			# 	self.typChanceText.SetText(getattr(localeinfo, "COMPANION_PET_TYPE_NEED_EVO", "Evolve your pet to unlock the next Type."))
			# else:
			# 	fmt = getattr(localeinfo, "COMPANION_PET_TYPE_CHANCE", "Success Chance: %s%%")
			# 	self.typChanceText.SetText(fmt % chance)
			# <<< SECTION END
		if self.typPityText:
			if maxed:
				self.typPityText.SetText("")
			else:
				fmt = getattr(localeinfo, "COMPANION_UPGRADE_PITY", "Failure before 100%%: %s / %s")
				self.typPityText.SetText(fmt % (failCount, pityMax))
		if self.typBtn:
			if maxed:
				self.typBtn.Hide()
			else:
				self.typBtn.Show()

	def __FillMaterials(self, slotWnd, countTexts, vnumStore, mats):
		FillMaterialColumns(slotWnd, countTexts, vnumStore, mats)   # shared module helper

	# ------------------------------------------------------------------
	# Confirm + send
	# ------------------------------------------------------------------
	def __AskQuestion(self, text, acceptFunc):
		if not self.questionDlg:
			dlg = uicommon.QuestionDialog()
			dlg.SetCancelEvent(ui.__mem_func__(self.__OnCancelQuestion))
			self.questionDlg = dlg
		self.questionDlg.SetText(text)
		self.questionDlg.SetAcceptEvent(acceptFunc)
		self.questionDlg.Open()

	def __OnCancelQuestion(self):
		if self.questionDlg:
			self.questionDlg.Close()
		return True

	def __OnClickEvolve(self):
		petID = player.GetActivePetItemId()
		if 0 == petID:
			return
		# The legacy gate emits its own refusal chat lines (level / EXP-full / age).
		iface = getattr(self, "interface", None)
		petWnd = getattr(iface, "wndPetInfoWindow", None) if iface else None
		if petWnd and not petWnd.IsActivateEvolButton(petID):
			return
		self.__AskQuestion(
			getattr(localeinfo, "GROWTH_PET_EVOLVE_QUESTION", "Evolve your pet?"),
			ui.__mem_func__(self.__OnConfirmEvolve))

	def __OnConfirmEvolve(self):
		self.__OnCancelQuestion()
		# Evolution rides the pet-feed packet with the EVOL index and empty item lists
		# (exactly what the legacy PetEvolveDialog sends); the server consumes the
		# materials and re-validates everything. Mirror the legacy click-time stamp.
		if net.SendPetFeedPacket(player.FEED_EVOL_EVENT, [], []):
			iface = getattr(self, "interface", None)
			petWnd = getattr(iface, "wndPetInfoWindow", None) if iface else None
			if petWnd:
				petWnd.feedButtonClickTime = app.GetGlobalTimeStamp()
		return True

	def __OnClickTypeUpgrade(self):
		if 0 == player.GetActivePetItemId():
			return
		self.__AskQuestion(
			getattr(localeinfo, "COMPANION_PET_TYPE_QUESTION", "Attempt the Type upgrade?"),
			ui.__mem_func__(self.__OnConfirmTypeUpgrade))

	def __OnConfirmTypeUpgrade(self):
		self.__OnCancelQuestion()
		# Server validates evolve-ceiling/materials/yang, rolls with the pity floor and
		# answers BOTH outcomes with a fresh info push -> Refresh() via the interface.
		if hasattr(net, "SendPetTypeUpgrade"):
			net.SendPetTypeUpgrade()
		return True

	# ------------------------------------------------------------------
	# Material hover tooltips
	# ------------------------------------------------------------------
	def __ShowMatToolTip(self, vnumStore, slotIndex):
		if slotIndex < 0 or slotIndex >= len(vnumStore):
			return
		vnum = vnumStore[slotIndex]
		if not vnum:
			return
		if not self.matToolTip:
			self.matToolTip = uitooltip.ItemToolTip()
		self.matToolTip.ClearToolTip()
		self.matToolTip.SetItemToolTip(vnum)

	def __OnEvoMatOverIn(self, slotIndex):
		self.__ShowMatToolTip(self.evoMatVnums, slotIndex)

	def __OnTypMatOverIn(self, slotIndex):
		self.__ShowMatToolTip(self.typMatVnums, slotIndex)

	def __OnMatOverOut(self):
		if self.matToolTip:
			self.matToolTip.HideToolTip()

	def __ShowTabToolTip(self, text):
		if not self.tabToolTip:
			self.tabToolTip = uitooltip.ToolTip()
		tip = self.tabToolTip
		tip.ClearToolTip()
		tip.AutoAppendNewTextLineResize(text)   # resize-to-fit, the proven button-tooltip pattern
		tip.ShowToolTip()

	def __OnTabOverInEvolve(self):
		self.__ShowTabToolTip(getattr(localeinfo, "COMPANION_PET_TAB_EVOLVE", "Evolve"))

	def __OnTabOverInType(self):
		self.__ShowTabToolTip(getattr(localeinfo, "COMPANION_PET_TAB_TYPE", "Upgrade Type"))

	def __OnTabOverOut(self):
		if self.tabToolTip:
			self.tabToolTip.HideToolTip()

	# ------------------------------------------------------------------
	# Lifecycle
	# ------------------------------------------------------------------
	def Close(self):
		if self.matToolTip:
			self.matToolTip.HideToolTip()
		if self.tabToolTip:
			self.tabToolTip.HideToolTip()
		if self.questionDlg:
			self.questionDlg.Close()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True


class PetSkillUpgradeDialog(ui.ScriptWindow):
	# Pet "Skill Upgrade" dialog (U4): opened by a skill slot's "+" on the Companion pet
	# page. Shows the NO-FAIL ladder cost for THIS slot's next skill level (<=4 materials
	# + Yang, from the GC pet-rework-info push via player.GetPetSkillUpgradeCost) and
	# sends net.SendPetSkillUpgradeRequest(slot) on Confirm -- the visible costs are the
	# confirmation, no extra question dialog. The server's after-upgrade info push lands
	# in interface.RefreshCompanionPetPage, which re-feeds this dialog while it is shown.

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Initialize()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		self.isLoaded   = 0
		self.board      = None
		self.interface  = None
		self.skillSlot  = -1          # pet skill slot (0..5) this dialog is upgrading
		self.headerText = None
		self.matSlot    = None
		self.matCounts  = []          # 4 count TextLines (index-parallel, may hold None)
		self.matVnums   = [0, 0, 0, 0]
		self.priceText  = None
		self.btnAccept  = None
		self.matToolTip = None

	def Destroy(self):
		self.ClearDictionary()
		self.Initialize()

	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/petskillupgradewindow.py")

		# Best-effort bind: a layout/locale error logs to syserr instead of aborting client boot.
		try:
			self.board = self.GetChild("board")
			self.board.SetTitleName(getattr(localeinfo, "COMPANION_PET_SKILL_UP_TITLE", "Pet - Skill Upgrade"))
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
			self.headerText = self.GetChild2("headerText")
			self.matSlot = self.GetChild2("materialSlot")
			if self.matSlot:
				self.matSlot.SetOverInItemEvent(ui.__mem_func__(self.__OnMatOverIn))
				self.matSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OnMatOverOut))
			self.matCounts = []
			for i in range(4):
				self.matCounts.append(self.GetChild2("matCount%d" % i))
			self.priceText = self.GetChild2("priceText")
			self.btnAccept = self.GetChild2("acceptButton")
			if self.btnAccept:
				self.btnAccept.SetEvent(ui.__mem_func__(self.__OnClickUpgrade))
		except:
			import dbg
			dbg.TraceError("PetSkillUpgradeDialog.__LoadWindow - bind failed")

	def Open(self, slot):
		self.skillSlot = slot
		self.SetCenterPosition()
		self.SetTop()
		self.Show()
		self.Refresh()

	def Refresh(self):
		# Called on open and by interface.RefreshCompanionPetPage after every upgrade
		# (the GC info push carries the NEXT rung's costs).
		if not self.isLoaded or not self.IsShow():
			return
		petID = player.GetActivePetItemId()
		if 0 == petID or self.skillSlot < 0 or not hasattr(player, "GetPetSkillByIndex"):
			self.Close()
			return
		skillData = player.GetPetSkillByIndex(petID, self.skillSlot)
		skillVnum = skillData[0]
		skillLv   = skillData[1]
		if 0 == skillVnum:
			self.Close()   # no skill in this slot anymore
			return
		skillName = ""
		try:
			(skillName, _skillDesc, _skillUseType, _skillCool) = skill.GetPetSkillInfo(skillVnum)
		except:
			pass
		maxLv = getattr(player, "PET_GROWTH_SKILL_LEVEL_MAX", 20)
		maxed = (skillLv >= maxLv)
		if self.headerText:
			if maxed:
				self.headerText.SetText(getattr(localeinfo, "COMPANION_PET_SKILL_UP_MAX", "This skill is at its maximum level."))
			else:
				fmt = getattr(localeinfo, "COMPANION_PET_SKILL_UP_HEADER", "%s  Lv %s -> %s")
				self.headerText.SetText(fmt % (skillName, skillLv, skillLv + 1))
		mats = []
		yang = 0
		if not maxed and hasattr(player, "GetPetSkillUpgradeCost"):
			cost = player.GetPetSkillUpgradeCost(self.skillSlot)
			yang = cost[0]
			for pair in cost[1:5]:
				if pair[0]:
					mats.append(pair)
		FillMaterialColumns(self.matSlot, self.matCounts, self.matVnums, mats)
		if self.priceText:
			if maxed:
				self.priceText.SetText("")
			else:
				money = localeinfo.NumberToMoneyStringNoUnit(yang) if hasattr(localeinfo, "NumberToMoneyStringNoUnit") else str(yang)
				fmt = getattr(localeinfo, "COMPANION_UPGRADE_COST", "Upgrade Price: %s")
				self.priceText.SetText(fmt % money)
		if self.btnAccept:
			if maxed:
				self.btnAccept.Hide()
			else:
				self.btnAccept.Show()

	def __OnClickUpgrade(self):
		if 0 == player.GetActivePetItemId() or self.skillSlot < 0:
			return
		if hasattr(net, "SendPetSkillUpgradeRequest"):
			net.SendPetSkillUpgradeRequest(self.skillSlot)

	def __OnMatOverIn(self, slotIndex):
		if slotIndex < 0 or slotIndex >= len(self.matVnums):
			return
		vnum = self.matVnums[slotIndex]
		if not vnum:
			return
		if not self.matToolTip:
			self.matToolTip = uitooltip.ItemToolTip()
		self.matToolTip.ClearToolTip()
		self.matToolTip.SetItemToolTip(vnum)

	def __OnMatOverOut(self):
		if self.matToolTip:
			self.matToolTip.HideToolTip()

	def Close(self):
		if self.matToolTip:
			self.matToolTip.HideToolTip()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
