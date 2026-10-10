# coding: latin_1
#
# Growth Mount contextual helps (ride page "?" buttons) -- binder.
# Chrome lives in uiscript/companionridehelpwindow.py. One window, two modes
# (uipethelp.py precedent): MODE_LEVEL = the leveling browser (one level step at
# a time, arrow-paged), MODE_SKILL = the skill browser (one skill, one level at
# a time). Every displayed number flows from the baked server config via
# uicompanionride.GetGrowthMountData() so a retune never leaves the help stale.
# Opened by interface.OpenCompanionRideHelp(mode) from the two ride-page "?"s.
import app
import ui
import item
import localeinfo
import uitooltip
import uicompanionride

MODE_LEVEL = 0
MODE_SKILL = 1

LINE_C   = 0xff756657
ROW_BG_C = 0xff1a1615
LABEL_C  = 0xffcabdab
VALUE_C  = 0xffc7c7c7
ACCENT_C = 0xffd1b183

ARROW_DIR = "d:/ymir work/ui/public/public_intro_btn/"


class CompanionRideHelpWindow(ui.ScriptWindow):

	WINDOW_WIDTH = 360
	M            = 12
	CONTENT_W    = WINDOW_WIDTH - 2 * M   # 336
	ROW_H        = 22
	STRIP_H      = 52
	SELECT_H     = 44
	NAV_H        = 20
	NOTE_H       = 16
	GAP          = 8
	ARROW_W      = 20
	ARROW_H      = 13
	MATS_H       = 30
	MAT_ICON     = 24
	MAT_LABEL_W  = 76
	MAT_MAX      = 5

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Initialize()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		self.isLoaded  = 0
		self.board     = None
		self.tables    = []
		self.icons     = []
		self.itemTip   = None
		self.interface = None
		self.builtMode = None
		self.curStep   = 1
		self.curSkill  = 0
		self.curSkillLevel = 1
		self.btnPrev   = None
		self.btnNext   = None
		self.navText   = None
		self.valExp    = None
		self.valGold   = None
		self.matsLabel = None
		self.matsRowBars = []
		self.matIcons  = []
		self.matCounts = []
		self.matSlotPos = []
		self.curMats   = []
		self.mountData = None
		self.skillSelIcons = []
		self.skillSelBars  = []
		self.skillNameText   = None
		self.skillUnlockText = None
		self.valBonus  = None
		self.valChance = None

	def Destroy(self):
		self.tables = []
		self.icons  = []
		self.ClearDictionary()
		self.Initialize()

	def GetMode(self):
		return self.builtMode

	def __L(self, key, default):
		return getattr(localeinfo, key, default)

	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = 1

		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/companionridehelpwindow.py")

		try:
			self.board = self.GetChild("board")
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
		except:
			import dbg
			dbg.TraceError("CompanionRideHelpWindow.__LoadWindow - bind failed")

	# ------------------------------------------------------------------
	# Draw helpers (bars are not_pick so hovers reach the icons below)
	# ------------------------------------------------------------------
	def __Bar(self, x, y, w, h, color):
		bar = ui.Bar()
		bar.SetParent(self)
		bar.AddFlag("attach")
		bar.AddFlag("not_pick")
		bar.SetPosition(int(x), int(y))
		bar.SetSize(int(w), int(h))
		bar.SetColor(color)
		bar.Show()
		self.tables.append(bar)
		return bar

	def __Box(self, x, y, w, h):
		self.__Bar(x, y, w, h, ROW_BG_C)
		self.__Bar(x, y, w + 1, 1, LINE_C)
		self.__Bar(x, y + h, w + 1, 1, LINE_C)
		self.__Bar(x, y, 1, h + 1, LINE_C)
		self.__Bar(x + w, y, 1, h + 1, LINE_C)

	def __Text(self, x, y, text, color):
		t = ui.TextLine()
		t.SetParent(self)
		t.AddFlag("attach")
		t.AddFlag("not_pick")
		t.SetPackedFontColor(color)
		t.SetHorizontalAlignCenter()
		t.SetPosition(int(x), int(y))
		t.SetText(text)
		t.Show()
		self.tables.append(t)
		return t

	def __Note(self, text, y):
		self.__Text(self.WINDOW_WIDTH / 2, y, text, ACCENT_C)
		return y + self.NOTE_H

	def __ApplyItemIcon(self, ico, vnum, side):
		nm = ""
		try:
			item.SelectItem(vnum)
			nm = item.GetIconImageFileName()
		except:
			pass
		if nm and nm.find("gr2") == -1:
			ico.LoadImage(nm)
		else:
			ico.LoadImage("icon/item/27995.tga")
		iw, ih = ico.GetWidth(), ico.GetHeight()
		if iw > 0 and ih > 0 and (iw > side or ih > side):
			sc = min(float(side) / iw, float(side) / ih)
			ico.SetScale(sc, sc)
			iw, ih = int(iw * sc), int(ih * sc)
		else:
			ico.SetScale(1.0, 1.0)
		return iw, ih

	def __MakeItemIcon(self, vnum, x, y):
		# No "attach" flag: it redirects mouse-down capture to the root window,
		# which swallows the icon's own mouse_click (the skill icons below are
		# already flagless for the same reason).
		ico = ui.ExpandedImageBox()
		ico.SetParent(self)
		iw, ih = self.__ApplyItemIcon(ico, vnum, 32)
		ico.SetPosition(int(x - iw / 2), int(y))
		ico.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OnOverItem, vnum)
		ico.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OnOverOut)
		if app.ENABLE_INGAME_WIKI:
			ico.SAFE_SetEvent(self.__OnClickItem, "mouse_click", vnum)
		ico.Show()
		self.icons.append(ico)
		return ico

	def __OnOverItem(self, vnum):
		if not self.itemTip:
			self.itemTip = uitooltip.ItemToolTip()
		self.itemTip.ClearToolTip()
		self.itemTip.SetItemToolTip(vnum)
		if app.ENABLE_INGAME_WIKI:
			self.itemTip.DeclareShortcut(("key_lclick",), self.__L("GROWTH_MOUNT_HELP_TIP_WIKI", "- Left click to open Wiki |Eemoji/key_lclick|e"))
			self.itemTip.ShowToolTip()

	def __OnOverOut(self):
		if self.itemTip:
			self.itemTip.HideToolTip()

	def __OpenItemWiki(self, vnum):
		# Fail-silent hyperlink jump: the interface API builds the wiki lazily
		# under FAST_WARP_UI and no-ops before it exists.
		iface = getattr(self, "interface", None)
		if not iface or not hasattr(iface, "OpenWikiToItem"):
			return
		if self.itemTip:
			self.itemTip.HideToolTip()
		iface.OpenWikiToItem(vnum)

	def __OnClickItem(self, eventType, vnum):
		self.__OpenItemWiki(vnum)

	def __MakeArrow(self, x, y, prev, event):
		btn = ui.Button()
		btn.SetParent(self)
		stem = "prev_btn" if prev else "next_btn"
		btn.SetUpVisual(ARROW_DIR + stem + "_01.sub")
		btn.SetOverVisual(ARROW_DIR + stem + "_01.sub")
		btn.SetDownVisual(ARROW_DIR + stem + "_02.sub")
		btn.SetPosition(int(x), int(y))
		btn.SetEvent(ui.__mem_func__(event))
		btn.Show()
		self.tables.append(btn)
		return btn

	def __AddNavRow(self, y):
		self.btnPrev = self.__MakeArrow(self.M, y + 3, 1, self.__OnPrev)
		self.btnNext = self.__MakeArrow(self.WINDOW_WIDTH - self.M - self.ARROW_W, y + 3, 0, self.__OnNext)
		self.navText = self.__Text(self.WINDOW_WIDTH / 2, y + 2, "", LABEL_C)
		return y + self.NAV_H

	def __AddCard(self, y, rows):
		# rows = [(labelText or None, splitColumn)] -- the last full-width row has no divider.
		rtl = localeinfo.IsARABIC()
		labelW = 190
		valueW = self.CONTENT_W - labelW
		h = self.ROW_H * len(rows)
		self.__Box(self.M, y, self.CONTENT_W, h)
		for i in range(1, len(rows)):
			self.__Bar(self.M, y + i * self.ROW_H, self.CONTENT_W + 1, 1, LINE_C)
		values = []
		for i, (label, split) in enumerate(rows):
			cy = y + i * self.ROW_H + 4
			if not split:
				values.append(self.__Text(self.WINDOW_WIDTH / 2, cy, label or "", VALUE_C))
				continue
			divX = self.M + (valueW if rtl else labelW)
			self.__Bar(divX, y + i * self.ROW_H, 1, self.ROW_H + 1, LINE_C)
			labelCX = self.M + (valueW + labelW / 2 if rtl else labelW / 2)
			valueCX = self.M + (valueW / 2 if rtl else labelW + valueW / 2)
			self.__Text(labelCX, cy, label, LABEL_C)
			values.append(self.__Text(valueCX, cy, "", VALUE_C))
		return y + h, values

	def __AddMatsBand(self, y):
		# Collapsible band under the 2-row card: the card's bottom border doubles
		# as this band's top edge, so hiding it leaves a clean 2-row card while
		# the board height and footer never move.
		rtl = localeinfo.IsARABIC()
		band = []
		band.append(self.__Bar(self.M, y + 1, self.CONTENT_W, self.MATS_H, ROW_BG_C))
		band.append(self.__Bar(self.M, y + 1, 1, self.MATS_H, LINE_C))
		band.append(self.__Bar(self.M + self.CONTENT_W, y + 1, 1, self.MATS_H, LINE_C))
		band.append(self.__Bar(self.M, y + self.MATS_H, self.CONTENT_W + 1, 1, LINE_C))
		labelCX = self.M + (self.CONTENT_W - self.MAT_LABEL_W / 2 if rtl else self.MAT_LABEL_W / 2)
		self.matsLabel = self.__Text(labelCX, y + 10, self.__L("GROWTH_MOUNT_HELP_MATS_LABEL", "Materials"), LABEL_C)
		self.matsRowBars = band
		self.matIcons  = []
		self.matCounts = []
		self.matSlotPos = []
		pitch = (self.CONTENT_W - self.MAT_LABEL_W) / self.MAT_MAX
		iy = y + 4
		for i in range(self.MAT_MAX):
			if rtl:
				cellX = self.M + self.CONTENT_W - self.MAT_LABEL_W - (i + 1) * pitch
			else:
				cellX = self.M + self.MAT_LABEL_W + i * pitch
			ico = ui.ExpandedImageBox()
			ico.SetParent(self)
			ico.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OnOverMatSlot, i)
			ico.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OnOverOut)
			if app.ENABLE_INGAME_WIKI:
				ico.SAFE_SetEvent(self.__OnClickMatSlot, "mouse_click", i)
			ico.Hide()
			self.icons.append(ico)
			self.matIcons.append(ico)
			txt = self.__Text(cellX + self.MAT_ICON + 14, y + 10, "", VALUE_C)
			txt.Hide()
			self.matCounts.append(txt)
			self.matSlotPos.append((cellX, iy))
		return y + self.MATS_H

	def __OnOverMatSlot(self, slotIdx):
		if slotIdx < len(self.curMats):
			self.__OnOverItem(self.curMats[slotIdx][0])

	def __OnClickMatSlot(self, eventType, slotIdx):
		if slotIdx < len(self.curMats):
			self.__OpenItemWiki(self.curMats[slotIdx][0])

	def __SetMats(self, mats):
		self.curMats = mats
		shown = min(len(mats), len(self.matIcons))
		for i in range(len(self.matIcons)):
			ico = self.matIcons[i]
			txt = self.matCounts[i]
			if i < shown:
				iw, ih = self.__ApplyItemIcon(ico, mats[i][0], self.MAT_ICON)
				cellX, iy = self.matSlotPos[i]
				ico.SetPosition(int(cellX + (self.MAT_ICON - iw) / 2), int(iy + (self.MAT_ICON - ih) / 2))
				txt.SetText("x%d" % mats[i][1])
				ico.Show()
				txt.Show()
			else:
				ico.Hide()
				txt.Hide()
		for w in [self.matsLabel] + self.matsRowBars:
			if not w:
				continue
			if shown > 0:
				w.Show()
			else:
				w.Hide()

	# ------------------------------------------------------------------
	# Live status (through the interface back-ref; None-safe)
	# ------------------------------------------------------------------
	def __RideStatus(self):
		iface = getattr(self, "interface", None)
		wndComp = getattr(iface, "wndCompanion", None) if iface else None
		return getattr(wndComp, "rideStatus", None) if wndComp else None

	# ------------------------------------------------------------------
	# MODE_LEVEL
	# ------------------------------------------------------------------
	def __BuildLevel(self):
		y = 32
		self.__Text(self.WINDOW_WIDTH / 2, y, self.__L("GROWTH_MOUNT_HELP_FEED_LEAD", "Feed these items to fill the EXP bar:"), ACCENT_C)
		y += self.NOTE_H + 6

		items = list(self.mountData["expItems"])
		if localeinfo.IsARABIC():
			items.reverse()
		n = len(items)
		cellW = self.CONTENT_W / n
		self.__Box(self.M, y, self.CONTENT_W, self.STRIP_H)
		for i in range(1, n):
			self.__Bar(self.M + i * cellW, y, 1, self.STRIP_H + 1, LINE_C)
		expFmt = self.__L("GROWTH_MOUNT_HELP_EXP_FMT", "+%d EXP")
		for i, pair in enumerate(items):
			cx = self.M + i * cellW + cellW / 2
			self.__MakeItemIcon(pair[0], cx, y + 2)
			self.__Text(cx, y + 36, expFmt % pair[1], VALUE_C)
		y += self.STRIP_H + self.GAP

		y = self.__AddNavRow(y) + 6
		y, values = self.__AddCard(y, [
			(self.__L("GROWTH_MOUNT_HELP_REQ_EXP", "EXP needed"), 1),
			(self.__L("GROWTH_MOUNT_HELP_REQ_GOLD", "Gold cost"), 1),
		])
		self.valExp  = values[0]
		self.valGold = values[1]
		y = self.__AddMatsBand(y)
		y += self.GAP
		y = self.__Note(self.__L("GROWTH_MOUNT_HELP_OVERFLOW", "Feeding past the bar is refused - items are not wasted."), y)
		return y

	def __StartLevelStep(self):
		st = self.__RideStatus()
		step = st[1] if st else 1
		return max(1, min(int(step), uicompanionride.RIDE_LEVEL_MAX - 1))

	def __SetLevelStep(self, step):
		ride = uicompanionride
		step = max(1, min(int(step), ride.RIDE_LEVEL_MAX - 1))
		self.curStep = step
		if self.navText:
			self.navText.SetText(self.__L("GROWTH_MOUNT_HELP_LEVEL_NAV", "Level %d -> %d") % (step, step + 1))
		if self.valExp:
			self.valExp.SetText(str(self.mountData["levelExp"][step]))
		cost = self.mountData["levelCost"][step + 1]
		if self.valGold:
			gold = cost["gold"]
			money = localeinfo.NumberToMoneyStringNoUnit(gold) if hasattr(localeinfo, "NumberToMoneyStringNoUnit") else str(gold)
			self.valGold.SetText(money)
		self.__SetMats(cost["mats"])
		if self.btnPrev:
			if step <= 1:
				self.btnPrev.Hide()
			else:
				self.btnPrev.Show()
		if self.btnNext:
			if step >= ride.RIDE_LEVEL_MAX - 1:
				self.btnNext.Hide()
			else:
				self.btnNext.Show()

	# ------------------------------------------------------------------
	# MODE_SKILL
	# ------------------------------------------------------------------
	def __BuildSkill(self):
		ride = uicompanionride
		rtl = localeinfo.IsARABIC()
		y = 32

		n = ride.RIDE_SKILL_COUNT
		cellW = self.CONTENT_W / n
		self.__Box(self.M, y, self.CONTENT_W, self.SELECT_H)
		for i in range(1, n):
			self.__Bar(self.M + i * cellW, y, 1, self.SELECT_H + 1, LINE_C)
		self.skillSelIcons = []
		self.skillSelBars  = []
		for i in range(n):
			cell = (n - 1 - i) if rtl else i
			cx = self.M + cell * cellW + cellW / 2
			ico = ui.ExpandedImageBox()
			ico.SetParent(self)
			ico.LoadImage(ride.RIDE_SKILL_ICON_PATH[i])
			ico.SetPosition(int(cx - 16), y + 4)
			ico.SAFE_SetEvent(self.__OnClickSkill, "mouse_click", i)
			ico.Show()
			self.icons.append(ico)
			self.skillSelIcons.append(ico)
			bar = self.__Bar(cx - 16, y + 38, 32, 2, ACCENT_C)
			bar.Hide()
			self.skillSelBars.append(bar)
		y += self.SELECT_H + 6

		self.skillNameText = self.__Text(self.WINDOW_WIDTH / 2, y, "", ACCENT_C)
		y += self.NOTE_H + 2
		self.skillUnlockText = self.__Text(self.WINDOW_WIDTH / 2, y, "", VALUE_C)
		y += self.NOTE_H + 6

		y = self.__AddNavRow(y) + 6
		y, values = self.__AddCard(y, [
			(self.__L("GROWTH_MOUNT_HELP_BONUS_COL", "Bonus"), 1),
			(self.__L("GROWTH_MOUNT_CHANCE", "Success chance"), 1),
		])
		self.valBonus  = values[0]
		self.valChance = values[1]
		y = self.__AddMatsBand(y)
		y += self.GAP
		y = self.__Note(self.__L("GROWTH_MOUNT_SKILL_CHAIN", "Train the previous skill first."), y) + 2
		y = self.__Note(self.__L("GROWTH_MOUNT_HELP_PITY", "After %d fails the next attempt always succeeds.") % ride.RIDE_SKILL_PITY_MAX, y)
		return y

	def __SelectSkill(self, idx):
		ride = uicompanionride
		idx = max(0, min(int(idx), ride.RIDE_SKILL_COUNT - 1))
		self.curSkill = idx
		for i in range(len(self.skillSelIcons)):
			self.skillSelIcons[i].SetAlpha(1.0 if i == idx else 0.35)
			if i < len(self.skillSelBars):
				if i == idx:
					self.skillSelBars[i].Show()
				else:
					self.skillSelBars[i].Hide()
		if self.skillNameText:
			self.skillNameText.SetText(ride.RideSkillLabel(idx))
		if self.skillUnlockText:
			self.skillUnlockText.SetText(self.__L("GROWTH_MOUNT_SKILL_LOCKED", "Unlocks at mount level %d") % ride.RIDE_SKILL_UNLOCK_LEVEL[idx])
		st = self.__RideStatus()
		level = 0
		if st:
			skillLevels = st[6]
			if idx < len(skillLevels):
				level = skillLevels[idx]
		self.__SetSkillLevel(level + 1)

	def __SetSkillLevel(self, level):
		ride = uicompanionride
		level = max(1, min(int(level), ride.RIDE_SKILL_LEVEL_MAX))
		self.curSkillLevel = level
		if self.navText:
			self.navText.SetText(self.__L("GROWTH_MOUNT_HELP_SKILL_NAV", "Level %d / %d") % (level, ride.RIDE_SKILL_LEVEL_MAX))
		if self.valBonus:
			self.valBonus.SetText("+%d%%" % ride.RIDE_SKILL_PCT[level])
		info = self.mountData["skills"][self.curSkill][level]
		if self.valChance:
			self.valChance.SetText("%d%%" % info["chance"])
		self.__SetMats(info["mats"])
		if self.btnPrev:
			if level <= 1:
				self.btnPrev.Hide()
			else:
				self.btnPrev.Show()
		if self.btnNext:
			if level >= ride.RIDE_SKILL_LEVEL_MAX:
				self.btnNext.Hide()
			else:
				self.btnNext.Show()

	def __OnClickSkill(self, eventType, idx):
		self.__SelectSkill(idx)

	# ------------------------------------------------------------------
	# Arrow paging
	# ------------------------------------------------------------------
	def __OnPrev(self):
		if self.builtMode == MODE_SKILL:
			self.__SetSkillLevel(self.curSkillLevel - 1)
		else:
			self.__SetLevelStep(self.curStep - 1)

	def __OnNext(self):
		if self.builtMode == MODE_SKILL:
			self.__SetSkillLevel(self.curSkillLevel + 1)
		else:
			self.__SetLevelStep(self.curStep + 1)

	# ------------------------------------------------------------------
	# Build + lifecycle
	# ------------------------------------------------------------------
	def __Build(self, mode):
		self.mountData = uicompanionride.GetGrowthMountData()
		if not self.board:
			return
		if self.itemTip:
			self.itemTip.HideToolTip()
		self.tables = []
		self.icons  = []
		self.btnPrev = None
		self.btnNext = None
		self.navText = None
		self.valExp = None
		self.valGold = None
		self.matsLabel = None
		self.matsRowBars = []
		self.matIcons  = []
		self.matCounts = []
		self.matSlotPos = []
		self.curMats   = []
		self.skillSelIcons = []
		self.skillSelBars  = []
		self.skillNameText = None
		self.skillUnlockText = None
		self.valBonus = None
		self.valChance = None
		self.builtMode = mode
		if mode == MODE_SKILL:
			self.board.SetTitleName(self.__L("GROWTH_MOUNT_HELP_SKILL_TITLE", "Mount - Skills"))
			y = self.__BuildSkill()
		else:
			self.board.SetTitleName(self.__L("GROWTH_MOUNT_HELP_LEVEL_TITLE", "Mount - Leveling"))
			y = self.__BuildLevel()
		total = int(y + self.GAP)
		self.board.SetSize(self.WINDOW_WIDTH, total)
		self.SetSize(self.WINDOW_WIDTH, total)

	def Open(self, mode = MODE_LEVEL):
		alreadyShown = self.IsShow()
		self.__Build(mode)
		if mode == MODE_SKILL:
			self.__SelectSkill(self.curSkill)
		else:
			self.__SetLevelStep(self.__StartLevelStep())
		if not alreadyShown:
			self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		if self.itemTip:
			self.itemTip.HideToolTip()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
