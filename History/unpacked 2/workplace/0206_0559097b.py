# coding: latin_1
#
# Growth Mount "Ride" page sub-dialogs (client Task 7) -- binders.
# Layouts live in uiscript/companionrideupgradewindow.py and uiscript/companionrideskillwindow.py;
# these classes load them, wire the titlebar close, and fill the requirement rows from the live
# rideStatus tuple the Companion window caches (RideUpgradeDialog.Open / OnStatus, RideSkillDialog
# Open / OnStatus). Structure mirrors uicompanionupgrade.py's CompanionUpgradeWindow.
#
# Source contract (Task 6, client-confirmed; active flag added Task 9):
#   inbound : BINARY_OnGrowthMountStatus(active, level, exp, reqExp, gold, upMats, skillLevels,
#             skillFails, skillChances, skillMats) -- reqExp==0 means max level. active==0 means
#             the mount isn't summoned/ridden -- the Companion window Closes both dialogs below.
#             upMats = [(vnum,count),...] for the NEXT level's cost (already non-zero filtered).
#             skillLevels/skillFails/skillChances = 4-tuples; skillMats = 4 lists of (vnum,count).
#   outbound: net.SendGrowthMountPacket(net.GROWTH_MOUNT_CG_LEVELUP, 0)
#             net.SendGrowthMountPacket(net.GROWTH_MOUNT_CG_SKILL_UPGRADE, skillIdx)
#   No result packet either way -- the server pushes a fresh status, which refreshes both
#   the Companion ride page and whichever of these dialogs is open.
import ui
import net
import grp
import player
import localeinfo
import uitooltip
import game_data

RIDE_SKILL_COUNT       = 4
RIDE_SKILL_LEVEL_MAX   = 5
# (active, mountLevel, (skillLv0..3)) -- written by CompanionWindow.OnGrowthMountStatus
# whenever the server pushes mount status; None until the first push this session.
LAST_STATUS = None
RIDE_SKILL_PITY_MAX    = 2    # fails before the 3rd attempt is guaranteed
RIDE_SKILL_UNLOCK_LEVEL = (5, 12, 21, 30)   # mount level that unlocks skill index 0..3
RIDE_SKILL_PCT = (0, 1, 2, 4, 6, 8)   # index = skill level 0..RIDE_SKILL_LEVEL_MAX
RIDE_LEVEL_MAX = 30   # mirrors server GROWTH_MOUNT_MAX_LEVEL
RIDE_SKILL_CHANCE = (0, 100, 75, 60, 45, 30)   # index = target skill level; fallback only, cl_growth_mount.json bake is authoritative
RIDE_EXP_ITEMS = ((50050, 50), (51050, 100), (52050, 150))   # (vnum, exp); mirrors server growth_mount.txt
RIDE_SKILL_ICON_PATH = (
	"icon/item/item_mount/skill_1.png",
	"icon/item/item_mount/skill_2.png",
	"icon/item/item_mount/skill_3.png",
	"icon/item/item_mount/skill_4.png",
)
RIDE_LEVEL_EXP = (0,   # index = current level; mirrors server growth_mount.txt LevelExp
	50, 200, 250, 300, 350, 400, 450, 500, 600, 700,
	800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700,
	1800, 1900, 2000, 2000, 2000, 2000, 2000, 2000, 2000)
RIDE_LEVEL_GOLD_LOW  = 10000   # fallback only (GetGrowthMountData); cl_growth_mount.json bake is authoritative
RIDE_LEVEL_GOLD_HIGH = 25000   # fallback only (GetGrowthMountData); cl_growth_mount.json bake is authoritative
RIDE_LEVEL_MAT_FLOOR = 11      # fallback only (GetGrowthMountData); cl_growth_mount.json bake is authoritative

def RideLevelUpGold(targetLevel):
	# Fallback only -- used by the GetGrowthMountData fallback dict when the
	# cl_growth_mount.json bake is missing; the bake is authoritative.
	if targetLevel < RIDE_LEVEL_MAT_FLOOR:
		return targetLevel * RIDE_LEVEL_GOLD_LOW
	return targetLevel * RIDE_LEVEL_GOLD_HIGH

_FALLBACK_GROWTH_MOUNT_DATA = None

def _BuildFallbackGrowthMountData():
	levelExp = {}
	for level in range(1, RIDE_LEVEL_MAX):
		levelExp[level] = RIDE_LEVEL_EXP[level]
	levelCost = {}
	for target in range(2, RIDE_LEVEL_MAX + 1):
		levelCost[target] = {"gold": RideLevelUpGold(target), "mats": []}
	skills = []
	for idx in range(RIDE_SKILL_COUNT):
		perLevel = {}
		for level in range(1, RIDE_SKILL_LEVEL_MAX + 1):
			perLevel[level] = {"chance": RIDE_SKILL_CHANCE[level], "mats": []}
		skills.append(perLevel)
	return {
		"expItems": [list(pair) for pair in RIDE_EXP_ITEMS],
		"levelExp": levelExp,
		"levelCost": levelCost,
		"skills": skills,
	}

def GetGrowthMountData():
	data = getattr(game_data, "growthMountData", None)
	if data:
		return data
	global _FALLBACK_GROWTH_MOUNT_DATA
	if _FALLBACK_GROWTH_MOUNT_DATA is None:
		_FALLBACK_GROWTH_MOUNT_DATA = _BuildFallbackGrowthMountData()
	return _FALLBACK_GROWTH_MOUNT_DATA

def RideSkillLabel(skillIdx):
	# STONE/MONSTER/BOSS/MEDI, in server slot order (assumption -- the server only carries the
	# 4 skills by index, no semantic names; matches the order the design brief listed them in).
	labels = (
		getattr(localeinfo, "GROWTH_MOUNT_SKILL_STONE", "Strong against Stones"),
		getattr(localeinfo, "GROWTH_MOUNT_SKILL_MONSTER", "Strong against Monsters"),
		getattr(localeinfo, "GROWTH_MOUNT_SKILL_BOSS", "Strong against Bosses"),
		getattr(localeinfo, "GROWTH_MOUNT_SKILL_MEDI", "Meditation PvM"),
	)
	if skillIdx < 0 or skillIdx >= len(labels):
		return ""
	return labels[skillIdx]

# Count-text colors (grp.GenerateColor floats avoid the 0xAARRGGBB channel-flip), matching the
# buffi/growth-pet evolve dialogs: green when the player owns enough of the material, red when short.
COLOR_HAVE_ENOUGH = grp.GenerateColor(0.5411, 0.7254, 0.5568, 1.0)
COLOR_NOT_ENOUGH  = grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0)


class RideUpgradeDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Initialize()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		self.isLoaded     = 0
		self.board        = None
		self.curLevel     = 0
		self.curGold      = 0
		self.curMats      = []       # [(vnum,count), ...]
		self.txtTargetLevel = None   # "targetLevelValue"
		self.matSlot      = None     # "materialSlot"
		self.matCountText = []       # "matCount0".."matCount4"
		self.matVnum      = [0, 0, 0, 0, 0]
		self.matToolTip   = None
		self.txtPrice     = None     # "priceValue"
		self.btnConfirm   = None     # "rideUpgradeAcceptButton"

	def Destroy(self):
		self.ClearDictionary()
		self.Initialize()

	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/companionrideupgradewindow.py")

		try:
			self.board = self.GetChild("board")
			self.board.SetTitleName(getattr(localeinfo, "GROWTH_MOUNT_UPGRADE_TITLE", "Mount Level Up"))
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
			self.__BindWidgets()
		except:
			import dbg
			dbg.TraceError("RideUpgradeDialog.__LoadWindow - bind failed")

	def __BindWidgets(self):
		self.txtTargetLevel = self.GetChild2("targetLevelValue")
		self.matSlot = self.GetChild2("materialSlot")
		if self.matSlot:
			self.matSlot.SetOverInItemEvent(ui.__mem_func__(self.__OnMatOverIn))
			self.matSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OnMatOverOut))
		self.matCountText = []
		for i in range(5):
			self.matCountText.append(self.GetChild2("matCount%d" % i))
		self.txtPrice = self.GetChild2("priceValue")
		self.btnConfirm = self.GetChild2("rideUpgradeAcceptButton")
		if self.btnConfirm:
			self.btnConfirm.SetEvent(ui.__mem_func__(self.__OnClickConfirm))

	# ------------------------------------------------------------------
	# Open / refresh / close
	# ------------------------------------------------------------------
	def Open(self, level, gold, upMats):
		self.__ApplyStatus(level, gold, upMats)
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def OnStatus(self, level, gold, upMats):
		# The Companion window forwards every fresh status push here while this dialog is open,
		# so the requirement rows stay live across a failed/succeeded confirm.
		self.__ApplyStatus(level, gold, upMats)

	def __ApplyStatus(self, level, gold, upMats):
		self.curLevel = level
		self.curGold  = gold
		self.curMats  = upMats
		if self.txtTargetLevel:
			fmt = getattr(localeinfo, "GROWTH_MOUNT_LEVEL", "Level") + " %d -> %d"
			self.txtTargetLevel.SetText(fmt % (level, level + 1))
		if self.txtPrice:
			money = localeinfo.NumberToMoneyStringNoUnit(gold) if hasattr(localeinfo, "NumberToMoneyStringNoUnit") else str(gold)
			fmt = getattr(localeinfo, "COMPANION_UPGRADE_COST", "Upgrade Price: %s")
			self.txtPrice.SetText(fmt % money)
		self.__RefreshMaterials(upMats)

	def __RefreshMaterials(self, mats):
		for i in range(5):
			self.matVnum[i] = 0
			if self.matSlot:
				self.matSlot.ClearSlot(i)
			if i < len(self.matCountText) and self.matCountText[i]:
				self.matCountText[i].SetText("")
		for i, pair in enumerate(mats):
			if i >= 5:
				break
			vnum, need = pair[0], pair[1]
			self.matVnum[i] = vnum
			if self.matSlot:
				self.matSlot.SetItemSlot(i, vnum, 0)
			if i < len(self.matCountText) and self.matCountText[i]:
				have = player.GetItemCountByVnum(vnum)
				self.matCountText[i].SetText(str(need))
				self.matCountText[i].SetPackedFontColor(COLOR_HAVE_ENOUGH if have >= need else COLOR_NOT_ENOUGH)
		if self.matSlot:
			self.matSlot.RefreshSlot()

	def __OnMatOverIn(self, slotIndex):
		if slotIndex < 0 or slotIndex >= len(self.matVnum):
			return
		vnum = self.matVnum[slotIndex]
		if not vnum:
			return
		if not self.matToolTip:
			self.matToolTip = uitooltip.ItemToolTip()
		self.matToolTip.ClearToolTip()
		self.matToolTip.SetItemToolTip(vnum)

	def __OnMatOverOut(self):
		if self.matToolTip:
			self.matToolTip.HideToolTip()

	def __OnClickConfirm(self):
		# Server re-validates level/exp/materials/gold. No result packet -- it pushes a fresh
		# status, which refreshes both this dialog (OnStatus) and the Companion ride page.
		if hasattr(net, "SendGrowthMountPacket"):
			net.SendGrowthMountPacket(net.GROWTH_MOUNT_CG_LEVELUP, 0)

	def Close(self):
		if self.matToolTip:
			self.matToolTip.HideToolTip()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True


class RideSkillDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Initialize()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		self.isLoaded    = 0
		self.board       = None
		self.curSkillIdx = 0
		self.curLevel    = 0
		self.curFail     = 0
		self.curChance   = 0
		self.curMats     = []
		self.skillIconSlot  = None   # "skillIconSlot" (image widget, LoadImage per skillIdx)
		self.txtSkillLevel  = None   # "skillLevelValue"
		self.matSlot      = None     # "materialSlot"
		self.matCountText = []       # "matCount0".."matCount4"
		self.matVnum      = [0, 0, 0, 0, 0]
		self.matToolTip   = None
		self.txtChance    = None     # "chanceValue"
		self.txtFail      = None     # "failValue"
		self.btnConfirm   = None     # "rideSkillAcceptButton"

	def Destroy(self):
		self.ClearDictionary()
		self.Initialize()

	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/companionrideskillwindow.py")

		try:
			self.board = self.GetChild("board")
			self.board.SetTitleName(getattr(localeinfo, "GROWTH_MOUNT_SKILL_TITLE", "Mount Skill Upgrade"))
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
			self.__BindWidgets()
		except:
			import dbg
			dbg.TraceError("RideSkillDialog.__LoadWindow - bind failed")

	def __BindWidgets(self):
		self.skillIconSlot = self.GetChild2("skillIconSlot")
		self.txtSkillLevel = self.GetChild2("skillLevelValue")
		self.matSlot = self.GetChild2("materialSlot")
		if self.matSlot:
			self.matSlot.SetOverInItemEvent(ui.__mem_func__(self.__OnMatOverIn))
			self.matSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OnMatOverOut))
		self.matCountText = []
		for i in range(5):
			self.matCountText.append(self.GetChild2("matCount%d" % i))
		self.txtChance  = self.GetChild2("chanceValue")
		self.txtFail    = self.GetChild2("failValue")
		self.btnConfirm = self.GetChild2("rideSkillAcceptButton")
		if self.btnConfirm:
			self.btnConfirm.SetEvent(ui.__mem_func__(self.__OnClickConfirm))

	# ------------------------------------------------------------------
	# Open / refresh / close
	# ------------------------------------------------------------------
	def Open(self, skillIdx, level, fail, chance, mats):
		self.curSkillIdx = skillIdx
		self.__ApplyStatus(level, fail, chance, mats)
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def OnStatus(self, skillLevels, skillFails, skillChances, skillMats):
		# The Companion window forwards every fresh status push here while this dialog is open
		# (indexed by the skill it was opened for), so the pity/chance/materials stay live.
		idx = self.curSkillIdx
		if idx < 0 or idx >= len(skillLevels):
			return
		mats = skillMats[idx] if idx < len(skillMats) else []
		self.__ApplyStatus(skillLevels[idx], skillFails[idx], skillChances[idx], mats)

	def __ApplyStatus(self, level, fail, chance, mats):
		self.curLevel  = level
		self.curFail   = fail
		self.curChance = chance
		self.curMats   = mats
		idx = self.curSkillIdx
		if self.skillIconSlot and 0 <= idx < len(RIDE_SKILL_ICON_PATH):
			self.skillIconSlot.LoadImage(RIDE_SKILL_ICON_PATH[idx])
		if self.txtSkillLevel:
			nextLevel = level + 1 if level < RIDE_SKILL_LEVEL_MAX else level
			fmt = getattr(localeinfo, "GROWTH_MOUNT_SKILL_LEVEL_FMT", "%s: Lv %d -> Lv %d")
			self.txtSkillLevel.SetText(fmt % (RideSkillLabel(idx), level, nextLevel))
		if self.txtChance:
			fmt = getattr(localeinfo, "GROWTH_MOUNT_CHANCE", "Success chance") + ": %d%%"
			self.txtChance.SetText(fmt % chance)
		if self.txtFail:
			fmt = getattr(localeinfo, "GROWTH_MOUNT_PITY", "Fail counter") + ": %d / %d"
			self.txtFail.SetText(fmt % (fail, RIDE_SKILL_PITY_MAX))
		self.__RefreshMaterials(mats)

	def __RefreshMaterials(self, mats):
		for i in range(5):
			self.matVnum[i] = 0
			if self.matSlot:
				self.matSlot.ClearSlot(i)
			if i < len(self.matCountText) and self.matCountText[i]:
				self.matCountText[i].SetText("")
		for i, pair in enumerate(mats):
			if i >= 5:
				break
			vnum, need = pair[0], pair[1]
			self.matVnum[i] = vnum
			if self.matSlot:
				self.matSlot.SetItemSlot(i, vnum, 0)
			if i < len(self.matCountText) and self.matCountText[i]:
				have = player.GetItemCountByVnum(vnum)
				self.matCountText[i].SetText(str(need))
				self.matCountText[i].SetPackedFontColor(COLOR_HAVE_ENOUGH if have >= need else COLOR_NOT_ENOUGH)
		if self.matSlot:
			self.matSlot.RefreshSlot()

	def __OnMatOverIn(self, slotIndex):
		if slotIndex < 0 or slotIndex >= len(self.matVnum):
			return
		vnum = self.matVnum[slotIndex]
		if not vnum:
			return
		if not self.matToolTip:
			self.matToolTip = uitooltip.ItemToolTip()
		self.matToolTip.ClearToolTip()
		self.matToolTip.SetItemToolTip(vnum)

	def __OnMatOverOut(self):
		if self.matToolTip:
			self.matToolTip.HideToolTip()

	def __OnClickConfirm(self):
		# Server re-validates level/materials and rolls the gamble (pity floor at
		# RIDE_SKILL_PITY_MAX+1 attempts). No result packet -- it pushes a fresh status.
		if hasattr(net, "SendGrowthMountPacket"):
			net.SendGrowthMountPacket(net.GROWTH_MOUNT_CG_SKILL_UPGRADE, self.curSkillIdx)

	def Close(self):
		if self.matToolTip:
			self.matToolTip.HideToolTip()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
