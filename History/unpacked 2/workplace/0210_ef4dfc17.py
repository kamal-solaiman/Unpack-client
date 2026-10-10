# coding: latin_1
#
# Companion "Upgrade Type" (Evolve) sub-window — binder.
# Layout lives in uiscript/companionupgradewindow.py; this module loads it, wires the
# titlebar close, and (when those widgets are placed) fills the requirement rows from
# app.GetBuffiEvolveInfo(targetStage) and sends the evolve packet on Confirm.
#
# Source contract (server side, already shipped):
#   app.GetBuffiEvolveInfo(stage) -> (intValue, reqLevel, yang, chance, pity, [(vnum,count),...])
#       where `stage` is the TARGET stage (1..3); chance = base success %, pity = fails -> guaranteed.
#   net.SendBuffiPacket(net.BUFFI_CG_EVOLVE, 0)  -> CBuffi::Evolve() (gamble + pity, server-validated).
#   The buffi's CURRENT stage + live pity counter come from the status push (passed in by the
#   Companion window when it opens this dialog, refreshed via OnBuffiStatus while shown).
import ui
import app
import net
import grp
import player
import localeinfo
import uitooltip

# Count-text colors (grp.GenerateColor floats avoid the 0xAARRGGBB channel-flip), matching the
# growth-pet evolve dialog: green when the player owns enough of the material, red when short.
COLOR_HAVE_ENOUGH = grp.GenerateColor(0.5411, 0.7254, 0.5568, 1.0)
COLOR_NOT_ENOUGH  = grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0)

# Mirrors BUFFI_EVOL_MAX_STAGE (srcs/share/buffi.hpp). Past this there is nothing left to buy:
# every getter in the shared header clamps stage+1 back to the max, so without this check the
# dialog re-advertised the final stage's cost as if another evolution existed.
BUFFI_EVOL_MAX_STAGE = 3

class CompanionUpgradeWindow(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Initialize()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		self.isLoaded     = 0
		self.board        = None
		self.curStage     = 0   # buffi's CURRENT evolution stage (target = curStage + 1)
		self.evolveFail   = 0   # live pity counter (consecutive fails)
		# Optional requirement widgets (declared in the uiscript later; bound defensively so the
		# window already opens with just the bg/header). Add widgets with these names and they fill
		# automatically — or tell me your names and I'll rebind.
		self.matSlot      = None   # "materialSlot": a SlotWindow holding the (<=5) required item icons
		self.matCountText = []     # "matCount0".."matCount4": per-slot count text (green=have / red=short)
		self.matVnum      = [0, 0, 0, 0, 0]   # vnum shown in each slot (for the hover tooltip)
		self.matToolTip   = None   # lazily-created item tooltip
		self.txtNewInt    = None   # "newIntValue": header strip -> the INT gained by evolving (cur -> new)
		self.txtPrice     = None   # "priceValue":  Yang cost text
		self.txtChance    = None   # "chanceValue": base success-% text
		self.txtFail      = None   # "failValue":   "N / pity" pity-counter text
		self.btnConfirm   = None   # "evolveAcceptButton"

	def Destroy(self):
		self.ClearDictionary()
		self.Initialize()

	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/companionupgradewindow.py")

		# Best-effort bind: a layout/locale error logs to syserr instead of aborting client boot.
		try:
			self.board = self.GetChild("board")
			self.board.SetTitleName(getattr(localeinfo, "COMPANION_UPGRADE_TITLE", "Upgrade"))
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
			self.__BindWidgets()
		except:
			import dbg
			dbg.TraceError("CompanionUpgradeWindow.__LoadWindow - bind failed")

	def __BindWidgets(self):
		# Everything here is optional (GetChild2 -> None if absent) so the skeleton window
		# (board + header + bg only) still opens cleanly. Each fills in __Refresh once placed.
		self.txtNewInt  = self.GetChild2("newIntValue")
		self.matSlot    = self.GetChild2("materialSlot")
		if self.matSlot:
			self.matSlot.SetOverInItemEvent(ui.__mem_func__(self.__OnMatOverIn))
			self.matSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OnMatOverOut))
		self.matCountText = []
		for i in range(5):
			self.matCountText.append(self.GetChild2("matCount%d" % i))
		self.txtPrice   = self.GetChild2("priceValue")
		self.txtChance  = self.GetChild2("chanceValue")
		self.txtFail    = self.GetChild2("failValue")
		self.btnConfirm = self.GetChild2("evolveAcceptButton")
		if self.btnConfirm:
			self.btnConfirm.SetEvent(ui.__mem_func__(self.__OnClickConfirm))

	# ------------------------------------------------------------------
	# Open / refresh / close
	# ------------------------------------------------------------------
	def Open(self, curStage, evolveFail):
		self.curStage   = curStage
		self.evolveFail = evolveFail
		self.__Refresh()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def OnBuffiStatus(self, curStage, evolveFail):
		# The server pushes a fresh status after every evolve attempt (stage and/or pity changed).
		# The Companion window forwards it here while this dialog is up so the rows stay live.
		self.curStage   = curStage
		self.evolveFail = evolveFail
		self.__Refresh()

	def __Refresh(self):
		# Fetch the TARGET stage's requirements from the single-source shared header (server C++).
		if not hasattr(app, "GetBuffiEvolveInfo"):
			return
		target = self.curStage + 1
		if target > BUFFI_EVOL_MAX_STAGE:
			self.__ApplyMaxStage()
			return
		if self.btnConfirm:
			self.btnConfirm.Enable()
			self.btnConfirm.Show()
		try:
			info = app.GetBuffiEvolveInfo(target)   # (int, reqLevel, yang, chance, pity, [(vnum,count)...])
		except:
			return
		if not info or len(info) < 6:
			return
		intValue, reqLevel, yang, chance, pity, mats = info[0], info[1], info[2], info[3], info[4], info[5]

		# Header strip: the INT the buffi gains by evolving (current stage's INT -> target stage's INT).
		if self.txtNewInt:
			curInt = intValue
			try:
				curInfo = app.GetBuffiEvolveInfo(self.curStage)
				if curInfo:
					curInt = curInfo[0]
			except:
				pass
			fmt = getattr(localeinfo, "COMPANION_UPGRADE_NEWINT", "Intelligence: %s -> %s")
			self.txtNewInt.SetText(fmt % (curInt, intValue))

		# Yang price, dot-grouped (e.g. 10.000.000) via the standard no-unit money formatter.
		if self.txtPrice:
			money = localeinfo.NumberToMoneyStringNoUnit(yang) if hasattr(localeinfo, "NumberToMoneyStringNoUnit") else str(yang)
			fmt = getattr(localeinfo, "COMPANION_UPGRADE_COST", "Upgrade Price: %s")
			self.txtPrice.SetText(fmt % money)
		# Optional base success chance (no widget in the current layout -> no-op).
		if self.txtChance:
			self.txtChance.SetText("%d%%" % chance)
		# Pity line: consecutive fails so far / the count that guarantees success (e.g. "0 / 3").
		if self.txtFail:
			fmt = getattr(localeinfo, "COMPANION_UPGRADE_PITY", "Failure before 100%%: %s / %s")
			self.txtFail.SetText(fmt % (self.evolveFail, pity))
		# Material icons + required counts (<=5), like the reference: icon in the slot, count below it,
		# colored green if the player owns enough / red if short.
		self.__RefreshMaterials(mats)

	def __ApplyMaxStage(self):
		# Fully evolved: clear the requirement rows and take Confirm away so the player cannot send an
		# evolve the server will only refuse.
		self.__RefreshMaterials([])
		if self.txtNewInt:
			self.txtNewInt.SetText(getattr(localeinfo, "COMPANION_UPGRADE_MAXSTAGE", "Fully evolved"))
		if self.txtPrice:
			self.txtPrice.SetText("")
		if self.txtChance:
			self.txtChance.SetText("")
		if self.txtFail:
			self.txtFail.SetText("")
		if self.btnConfirm:
			self.btnConfirm.Disable()
			self.btnConfirm.Hide()

	def __RefreshMaterials(self, mats):
		# Empty every column first (icon + count text), then fill the ones this stage uses.
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
			# Icon only (count=0 -> no corner overlay; the count is shown below in its own colored text).
			if self.matSlot:
				self.matSlot.SetItemSlot(i, vnum, 0)
			# Count text below the slot, green if owned >= required else red.
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
		# Server re-validates level + materials + Yang and rolls the gamble (pity floor). It then
		# pushes a fresh status, which refreshes both this dialog and the Companion window.
		if self.curStage >= BUFFI_EVOL_MAX_STAGE:
			return
		if hasattr(net, "SendBuffiPacket"):
			net.SendBuffiPacket(net.BUFFI_CG_EVOLVE, 0)

	def Close(self):
		if self.matToolTip:
			self.matToolTip.HideToolTip()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
