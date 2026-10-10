import ui
import app
import player
import localeinfo
import colorinfo

PATH_BP_QUEST = "d:/ymir work/ui/game/battle_pass_reworked/slice/quest/"


class AlignmentWindow(ui.Board):
	GRADE_COLORS = {
		0: colorinfo.TITLE_RGB_GOOD_4,
		1: colorinfo.TITLE_RGB_GOOD_3,
		2: colorinfo.TITLE_RGB_GOOD_2,
		3: colorinfo.TITLE_RGB_GOOD_1,
		4: colorinfo.TITLE_RGB_NORMAL,
		5: colorinfo.TITLE_RGB_EVIL_1,
		6: colorinfo.TITLE_RGB_EVIL_2,
		7: colorinfo.TITLE_RGB_EVIL_3,
		8: colorinfo.TITLE_RGB_EVIL_4,
	}


	def __init__(self):
		ui.Board.__init__(self)
		self.sessionBase = None
		self.gradeRows = []
		self._BuildUI()
		self.SetSize(255, 330 + 20)
		self.Hide()

	def __del__(self):
		ui.Board.__del__(self)

	def _MakeSeparator(self, y):
		bar = ui.Bar()
		bar.SetParent(self)
		bar.AddFlag("not_pick")
		bar.SetColor(ui.GenerateColor(75, 60, 40))
		bar.SetSize(232, 1)
		bar.SetPosition(11, y)
		bar.Show()
		return bar

	def _MakeSectionLabel(self, text, y):
		lbl = ui.TextLine()
		lbl.SetParent(self)
		lbl.SetPosition(127, y)
		lbl.SetText(text)
		lbl.SetHorizontalAlignCenter()
		lbl.SetPackedFontColor(ui.GenerateColor(195, 170, 110))
		lbl.Show()
		return lbl

	def _BuildUI(self):
		# Simple ThinBoard background for each item
		bgBoard = ui.OutlineWindow()
		bgBoard.SetParent(self)
		bgBoard.MakeOutlineWindow(255 - 16, 330 + 20 - 20)
		bgBoard.SetPosition(7, 10)
		bgBoard.Show()
		self.bgBoard = bgBoard

		# --- Title bar ---
		titleBar = ui.TitleBar()
		titleBar.SetParent(self)
		titleBar.MakeTitleBar(238, "red")
		titleBar.SetPosition(8, 7)
		titleBar.SetCloseEvent(ui.__mem_func__(self.Hide))
		titleBar.Show()
		self.titleBar = titleBar


		titleText = ui.TextLine()
		titleText.SetParent(titleBar)
		titleText.SetPosition(0, 0)
		titleText.SetWindowHorizontalAlignCenter()
		titleText.SetHorizontalAlignCenter()
		titleText.SetText(localeinfo.ALIGNMENT_WINDOW_TITLE)
		titleText.Show()
		self.titleText = titleText

		# --- Current rank section ---
		gradeText = ui.TextLine()
		gradeText.SetParent(self)
		gradeText.SetPosition(127, 37)
		gradeText.SetHorizontalAlignCenter()
		gradeText.Show()
		self.gradeText = gradeText

		bonusText = ui.TextLine()
		bonusText.SetParent(self)
		bonusText.SetPosition(127, 54)
		bonusText.SetHorizontalAlignCenter()
		bonusText.Show()
		self.bonusText = bonusText

		bgGaugeBack = ui.MakeExpandedImageBox(self, PATH_BP_QUEST + "quest_bar.png", 41, 80, "not_pick")
		bgGaugeFull = ui.MakeExpandedImageBox(bgGaugeBack, PATH_BP_QUEST + "quest_innerbar.png", 0, 2, "not_pick")
		self.bgGaugeBack = bgGaugeBack
		self.bgGaugeFull = bgGaugeFull

		sessionText = ui.TextLine()
		sessionText.SetParent(self)
		sessionText.SetPosition(127, 100)
		sessionText.SetHorizontalAlignCenter()
		sessionText.Show()
		self.sessionText = sessionText

		autoRecovText = ui.TextLine()
		autoRecovText.SetParent(self)
		autoRecovText.SetPosition(127, 115)
		autoRecovText.SetHorizontalAlignCenter()
		#autoRecovText.SetPackedFontColor(ui.GenerateColor(155, 155, 155))
		autoRecovText.Show()
		self.autoRecovText = autoRecovText

		# --- Separator + Rankings header ---
		self._MakeSeparator(122)
		self._MakeSectionLabel(localeinfo.ALIGNMENT_GRADE_RANKINGS, 127)
		self._MakeSeparator(142)

		# --- Grade rows ---
		# Left column: grade name (x=15), Right column: bonus (x=130)
		ROW_Y_START = 135
		ROW_HEIGHT = 17

		for i in xrange(9):
			nameText = ui.TextLine()
			nameText.SetParent(self)
			nameText.SetPosition(230, ROW_Y_START + i * ROW_HEIGHT)
			nameText.SetHorizontalAlignLeft()
			nameText.Show()

			bonusRowText = ui.TextLine()
			bonusRowText.SetParent(self)
			bonusRowText.SetPosition(100, ROW_Y_START + i * ROW_HEIGHT)
			bonusRowText.SetHorizontalAlignCenter()
			bonusRowText.Show()

			self.gradeRows.append((nameText, bonusRowText))

		# --- Dungeon penalty notice (only visible for negative alignment grades) ---
		self._MakeSeparator(285)

		penaltyDropText = ui.TextLine()
		penaltyDropText.SetParent(self)
		penaltyDropText.SetPosition(127, 292)
		penaltyDropText.SetHorizontalAlignCenter()
		penaltyDropText.Show()
		self.penaltyDropText = penaltyDropText

		penaltyLootText = ui.TextLine()
		penaltyLootText.SetParent(self)
		penaltyLootText.SetPosition(127, 307)
		penaltyLootText.SetHorizontalAlignCenter()
		penaltyLootText.Show()
		self.penaltyLootText = penaltyLootText

	def AdjustPosition(self, x, y):
		self.SetPosition(x, y)

	def Open(self, charWndX, charWndY):
		self.SetPosition(charWndX + 258, charWndY)
		if self.sessionBase is None:
			point, _ = player.GetAlignmentData()
			self.sessionBase = point
		self.Refresh()
		self.Show()
		self.SetTop()

	def Refresh(self):
		point, grade = player.GetAlignmentData()

		colorList = self.GRADE_COLORS.get(grade, colorinfo.TITLE_RGB_NORMAL)
		gradeColor = ui.GenerateColor(colorList[0], colorList[1], colorList[2])

		# Current grade name
		if app.ENABLE_GENDER_ALIGNMENT:
			name = localeinfo.GetAlignmentTitleName(point)
		else:
			name = localeinfo.TITLE_NAME_LIST[grade]
		self.gradeText.SetText(name)
		self.gradeText.SetPackedFontColor(gradeColor)

		# Active bonus -- grade 0 has two sub-tiers (3% below max, 5% at 20000)
		if grade == 0 and point < 20000:
			bonusStr = localeinfo.ALIGNMENT_GRADE_BONUSES[1]
		else:
			bonusStr = localeinfo.ALIGNMENT_GRADE_BONUSES[grade]
		self.bonusText.SetText(bonusStr)
		self.bonusText.SetPackedFontColor(gradeColor)

		# Progress bar within tier
		thresholds = localeinfo.ALIGNMENT_GRADE_THRESHOLDS
		upperBound = thresholds[grade]
		lowerBound = thresholds[grade + 1] if grade + 1 < len(thresholds) else -20000
		tierSize = upperBound - lowerBound
		pct = float(point - lowerBound) / tierSize if tierSize > 0 else 1.0
		pct = max(0.0, min(1.0, pct))
		self.bgGaugeFull.SetRenderingRect(0.0, 0.0, -(1.0 - pct), 0.0)

		# Session gain
		if self.sessionBase is not None:
			gain = point - self.sessionBase
			if gain > 0:
				self.sessionText.SetText(localeinfo.ALIGNMENT_SESSION_GAIN % gain)
				self.sessionText.SetPackedFontColor(ui.GenerateColor(0, 215, 95))
			elif gain < 0:
				self.sessionText.SetText(localeinfo.ALIGNMENT_SESSION_LOSS % gain)
				self.sessionText.SetPackedFontColor(ui.GenerateColor(255, 80, 80))
			else:
				self.sessionText.SetText(localeinfo.ALIGNMENT_SESSION_NONE)
				self.sessionText.SetPackedFontColor(ui.GenerateColor(155, 155, 155))

		# Auto-recovery note
		if point < 0:
			self.autoRecovText.SetText(localeinfo.ALIGNMENT_AUTO_RECOVERY)
		else:
			self.autoRecovText.SetText("")

		# --- Grade ladder ---
		if app.ENABLE_GENDER_ALIGNMENT:
			import chr, net
			gender = chr.RaceToSex(net.GetMainActorRace())
			gradeNameList = localeinfo.TITLE_NAME_DICT.get(gender, localeinfo.TITLE_NAME_DICT[localeinfo.GENDER_MALE])
		else:
			gradeNameList = localeinfo.TITLE_NAME_LIST

		for i, (nameText, bonusRowText) in enumerate(self.gradeRows):
			gradeName = gradeNameList[i]
			# Grade 0: show earned bonus (3% partial, 5% at max) for active row; max for dim rows
			if i == 0 and i == grade and point < 20000:
				gradeBonus = localeinfo.ALIGNMENT_GRADE_BONUSES[1]
			else:
				gradeBonus = localeinfo.ALIGNMENT_GRADE_BONUSES[i]

			if i == grade:
				iColorList = self.GRADE_COLORS.get(i, colorinfo.TITLE_RGB_NORMAL)
				iColor = ui.GenerateColor(iColorList[0], iColorList[1], iColorList[2])
				nameText.SetText("> " + gradeName)
				nameText.SetPackedFontColor(iColor)
				bonusRowText.SetText(gradeBonus)
				bonusRowText.SetPackedFontColor(iColor)
			else:
				fullList = self.GRADE_COLORS.get(i, colorinfo.TITLE_RGB_NORMAL)
				dimColor = ui.GenerateColor(int(fullList[0] * 0.4), int(fullList[1] * 0.4), int(fullList[2] * 0.4))
				nameText.SetText("   " + gradeName)
				nameText.SetPackedFontColor(dimColor)
				bonusRowText.SetText(gradeBonus)
				bonusRowText.SetPackedFontColor(ui.GenerateColor(105, 105, 105))

		# --- Dungeon penalty notice ---
		_DUNGEON_PENALTY = {5: 10, 6: 15, 7: 20, 8: 30}
		_LOOT_BUFF = {6: 15, 7: 10}
		if grade >= 5:
			penalty = _DUNGEON_PENALTY.get(grade, 0)
			self.penaltyDropText.SetText(localeinfo.ALIGNMENT_DUNGEON_PENALTY % penalty)
			self.penaltyDropText.SetPackedFontColor(ui.GenerateColor(255, 80, 80))
			if grade == 8:
				self.penaltyLootText.SetText(localeinfo.ALIGNMENT_LOOT_BUFF_DISABLED)
				self.penaltyLootText.SetPackedFontColor(ui.GenerateColor(255, 80, 80))
			elif grade in _LOOT_BUFF:
				self.penaltyLootText.SetText(localeinfo.ALIGNMENT_LOOT_BUFF_REDUCED % _LOOT_BUFF[grade])
				self.penaltyLootText.SetPackedFontColor(ui.GenerateColor(255, 130, 50))
			else:
				self.penaltyLootText.SetText("")
		else:
			self.penaltyDropText.SetText("")
			self.penaltyLootText.SetText("")
