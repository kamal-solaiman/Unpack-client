

import ui, constinfo, localeinfo

import net, player, chat, wndMgr, app, skill

import systemSetting

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

SKILL_MASTER = 0
SKILL_GRAND_MASTER = 1
SKILL_PERFECT_MASTER = 2
SKILL_L_MASTER = 3

USE_YMIR_50300_SKILLBOOK = False
NINETH_SKILL = [176, 177, 178,179,180,181,182,183]

# ---- new design assets (patch5/ymir work/ui/game/skillreader -> d:/ymir work/ui/game/skillreader) ----
SKILLREADER_PATH = "d:/ymir work/ui/game/skillreader/"

# Support items shown in the 3-slot row (exorcism stone, concentrated essence, zen beans).
SUPPORT_ITEMS = (71001, 71094, 70102)
SUPPORT_SLOT_POS = ((24, 61), (85, 61), (146, 61))   # centered on the 3 BG wells (pitch 61)
BOOK_SLOT_POS = (193, 100)   # the book currently being read (gauge band, right well)

# 6 columns x 2 rows skill grid, pushed up so the read buttons sit at the very bottom.
GRID_COLS_X = (10, 48, 86, 124, 162, 200)
GRID_ROWS_Y = (150, 188)

# Ordered skill lists per page (page 2 is intentionally unused for now).
PAGE_SKILLS = {
	0: (1, 2, 3, 4, 5, 6),
	1: (121, 122, 123, 124, 210, 211, 212),
	2: (163, 164, 165, 166),
}

# Skillbook vnum -> passive/special skill index (inverse of server SkillToBook).
# Used so that clicking such a book opens this window on the Passive tab and preselects the skill.
PASSIVE_BOOK_TO_SKILL = {
	50304: 122, 50600: 124,
	50301: 121, 50302: 121, 50303: 121,
	50902: 123, 50903: 123, 50904: 123,
	59900: 210, 59901: 210, 59902: 210,
	59903: 211, 59904: 211, 59905: 211,
	59906: 212, 59907: 212, 59908: 212,
}
# Main-skill books: unified main book + grand-master soul stones -> Basic tab (no single skill).
MAIN_BOOK_VNUMS = (50350, 50513, 50527,)
# Buffi skill books (163-166), mirroring main skills: Master grade reads one book, Grand Master
# a separate book (matches server AUTO_SKILL_BUFFI_BOOK / AUTO_SKILL_BUFFI_BOOK_GM).
BUFFI_BOOK_VNUM = 50351       # Master (M)
BUFFI_BOOK_VNUM_GM = 91125    # Grand Master (G) -> Perfect

def IsSystemBook(vnum):
	if vnum in MAIN_BOOK_VNUMS:
		return True
	if vnum in (BUFFI_BOOK_VNUM, BUFFI_BOOK_VNUM_GM):
		return True
	if vnum in PASSIVE_BOOK_TO_SKILL:
		return True
	if 50569 <= vnum <= 50576: # 9th-skill master books (50393 + skillIndex)
		return True
	return False

# Successful reads to advance one level (mirrors server GetAutoSkillRequired): easy start, ramps up.
REQ_MASTER = [1, 2, 3, 3, 4, 5, 6, 7, 8, 9]  # sum = 48
REQ_GRAND  = [1, 2, 3, 3, 4, 5, 6, 7, 8, 9]  # sum = 48

# vnum -> (skillIndex, tier 'M'/'G'/'P') for passive/special books that get a rich tooltip.
BOOK_TIERS = {
	50301: (121, 'M'), 50302: (121, 'G'), 50303: (121, 'P'),
	50902: (123, 'M'), 50903: (123, 'G'), 50904: (123, 'P'),
	59900: (210, 'M'), 59901: (210, 'G'), 59902: (210, 'P'),
	59903: (211, 'M'), 59904: (211, 'G'), 59905: (211, 'P'),
	59906: (212, 'M'), 59907: (212, 'G'), 59908: (212, 'P'),
	50304: (122, 'M'), 50600: (124, 'M'),
}

def GetBookTooltipInfo(vnum):
	# Returns (skillIndex, tierLetter, totalBooksForGrade) or None.
	if vnum not in BOOK_TIERS:
		return None
	skillIndex, tier = BOOK_TIERS[vnum]
	total = sum(REQ_MASTER) if tier == 'M' else sum(REQ_GRAND)
	return (skillIndex, tier, total)

class Window(ui.BoardWithTitleBar):
	# offset of the SkillReaderBG art inside the system board (below the engine titlebar)
	BG_X = 8
	BG_Y = 30
	BG_W = 241
	BG_H = 264   # SkillReaderBG.png size (height was 251; +13px at the bottom for the read buttons)

	# Buffi skills (163-166) occupy dedicated player skill-slots 130-133 (the same mapping
	# uicharacter uses). Reserved in Open() so the normal skill packet can fill their level.
	BUFFI_SKILL_SLOT_START = 130
	BUFFI_SKILL_COUNT = 4
	BUFFI_SKILL_VNUM_START = 163

	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		self.__LoadWindow()

	def Destroy(self):
		self.__children = {}

	def __LoadWindow(self):
		self.Destroy()

		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetSize(self.BG_W + self.BG_X * 2, self.BG_Y + self.BG_H + self.BG_X)
		self.SetTitleName(localeinfo.AUTO_SKLLL_READER_TITLE)
		self.SetCloseEvent(self.Close)
		self.SetCenterPosition()

		# the design art sits on the system board, just under the titlebar; everything
		# below is a child of `bg` so coordinates stay relative to the art (0..241 / 0..251).
		bg = CreateWindow(ui.ExpandedImageBox(), self, (self.BG_X, self.BG_Y), SKILLREADER_PATH + "SkillReaderBG.png")
		self.__children["bg"] = bg

		# build per-page skill->grid-position maps
		__data = {}
		for page, order in PAGE_SKILLS.items():
			slots = {}
			for n, sk in enumerate(order):
				slots[sk] = [GRID_COLS_X[n % 6], GRID_ROWS_Y[n // 6]]
			__data[page] = { "slots": slots }
		self.__children["data"] = __data

		# skill wells + one slot-window per page (lower area)
		for page, data in __data.items():
			slots = data["slots"]
			for sk, pos in slots.items():
				self.__children["slotImg"+str(page)+str(sk)] = self.__CreateSlot(bg, pos[0], pos[1])

			sw = CreateWindow(ui.SlotWindow(), bg, (0, 0), "", "", (self.BG_W, self.BG_H))
			sw.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
			sw.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnSelectItemSlot))
			sw.SetUnselectItemSlotEvent(ui.__mem_func__(self.__OnSelectItemSlot))
			sw.SetOverInItemEvent(ui.__mem_func__(self.OverInSkill))
			sw.SetOverOutItemEvent(ui.__mem_func__(self.OverOutSkill))
			for sk, pos in slots.items():
				sw.AppendSlot(sk, pos[0], pos[1], 32, 32)
			self.__children["slotWindow"+str(page)] = sw

		# support-item slots (3) + book-being-read slot (1), topmost over the skill windows
		itemSlotWindow = CreateWindow(ui.SlotWindow(), bg, (0, 0), "", "", (241, 150))
		itemSlotWindow.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
		for j, (sx, sy) in enumerate(SUPPORT_SLOT_POS):
			itemSlotWindow.AppendSlot(j, sx, sy, 32, 32)
		itemSlotWindow.AppendSlot(3, BOOK_SLOT_POS[0], BOOK_SLOT_POS[1], 32, 32)
		itemSlotWindow.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		itemSlotWindow.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		itemSlotWindow.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnClickItemSlot))   # left click -> open wiki
		self.__children["itemSlotWindow"] = itemSlotWindow

		# page tabs at the TOP band (Basic / Passive used; a 3rd page reserved, not built)
		tabNames = { 0: localeinfo.AUTO_SKLLL_READER_NORMAL, 1: localeinfo.AUTO_SKLLL_READER_PASSIVE, 2: localeinfo.AUTO_SKLLL_READER_PASSIVE }
		tabX = { 0: 160, 1: 81, 2: 4 }
		for page in (0, 1, 2):
			tab = CreateWindow(ui.RadioButton(), bg, (tabX[page], 6))
			tab.SetUpVisual(SKILLREADER_PATH + "skillpage_01.png")
			tab.SetOverVisual(SKILLREADER_PATH + "skillpage_02.png")
			tab.SetDownVisual(SKILLREADER_PATH + "skillpage_03.png")
			tab.SetText(tabNames[page])
			tab.SAFE_SetEvent(self.__SetPage, page)
			self.__children["categoryBtn"+str(page)] = tab

		# selected skill name
		nameText = CreateWindow(ui.TextLine(), bg, (120, 40), "", "horizontal:center")
		self.__children["nameText"] = nameText

		# progress text + custom gauge (progressbar.png clipped to %)
		progressText = CreateWindow(ui.TextLine(), bg, (100, 104), "%s 0 / 0" % localeinfo.AUTO_SKLLL_READER_PROGRESS, "horizontal:center")
		self.__children["progressText"] = progressText

		gaugeFill = CreateWindow(ui.ExpandedImageBox(), bg, (14, 122), SKILLREADER_PATH + "progressbar.png")
		gaugeFill.SetPercentage(0, 1)
		self.__children["progressGauge"] = gaugeFill

		# READ ALL (toggle start/stop loop) + READ ONCE (single read) at the very bottom
		readAllBtn = CreateWindow(ui.Button(), bg, (12, 230))
		readAllBtn.SetUpVisual(SKILLREADER_PATH + "read_norm.png")
		readAllBtn.SetOverVisual(SKILLREADER_PATH + "read_hover.png")
		readAllBtn.SetDownVisual(SKILLREADER_PATH + "read_down.png")
		readAllBtn.SetText(localeinfo.AUTO_SKLLL_READER_START)
		readAllBtn.SAFE_SetEvent(self.__ToggleRun)
		self.__children["readAllBtn"] = readAllBtn

		readOnceBtn = CreateWindow(ui.Button(), bg, (130, 230))
		readOnceBtn.SetUpVisual(SKILLREADER_PATH + "read_norm.png")
		readOnceBtn.SetOverVisual(SKILLREADER_PATH + "read_hover.png")
		readOnceBtn.SetDownVisual(SKILLREADER_PATH + "read_down.png")
		readOnceBtn.SetText(localeinfo.AUTO_SKLLL_READER_READ_ONCE)
		readOnceBtn.SAFE_SetEvent(self.__ReadOnce)
		self.__children["readOnceBtn"] = readOnceBtn

		# one usage toggle per support item, placed just to the right of each item slot
		self.__children["helperState"] = {}
		for j, vnum in enumerate(SUPPORT_ITEMS):
			sx, sy = SUPPORT_SLOT_POS[j]
			chk = CreateWindow(ui.Button(), bg, (sx + 33, sy + 2))
			chk.SAFE_SetEvent(self.__ToggleHelper, vnum)
			self.__children["helperCheck"+str(vnum)] = chk
			self.__children["helperState"][vnum] = True

		self.__children["botStatus"] = 0
		self.__children["selectedSkill"] = 0
		self.__children["progressCur"] = 0
		self.__children["progressReq"] = 0
		self.__UpdateHelperChecks()

		self.__SetPage(0)

	def ServerSetStatus(self, status):
		self.__children["botStatus"] = True if int(status) else False
		self.Refresh()

	def __UpdateHelperChecks(self):
		state = self.__children["helperState"] if self.__children.has_key("helperState") else {}
		for vnum in SUPPORT_ITEMS:
			key = "helperCheck"+str(vnum)
			if not self.__children.has_key(key):
				continue
			enabled = state[vnum] if state.has_key(vnum) else True
			img = SKILLREADER_PATH + ("checked.png" if enabled else "unchecked.png")
			btn = self.__children[key]
			btn.SetUpVisual(img)
			btn.SetOverVisual(img)
			btn.SetDownVisual(img)
			btn.SetUp()

	def __ToggleHelper(self, vnum):
		state = self.__children["helperState"] if self.__children.has_key("helperState") else {}
		enabled = not (state[vnum] if state.has_key(vnum) else True)
		state[vnum] = enabled
		self.__children["helperState"] = state
		self.__UpdateHelperChecks()
		net.SendChatPacket("/auto_skill_reader helper {} {}".format(vnum, 1 if enabled else 0))

	def ServerSetHelper(self, vnum, enabled):
		vnum = int(vnum)
		state = self.__children["helperState"] if self.__children.has_key("helperState") else {}
		state[vnum] = True if int(enabled) else False
		self.__children["helperState"] = state
		self.__UpdateHelperChecks()

	def __SelectedServerSkillIdx(self):
		selectedSkill = self.__children["selectedSkill"] if self.__children.has_key("selectedSkill") else 0
		if selectedSkill == 0:
			return 0
		if selectedSkill >= 1 and selectedSkill <= 9:
			return player.GetSkillIndex(selectedSkill)
		return selectedSkill

	def __RequestProgress(self):
		selected = self.__SelectedServerSkillIdx()
		if selected:
			net.SendChatPacket("/auto_skill_reader progress {}".format(selected))

	def __ResetProgress(self):
		self.__children["progressCur"] = 0
		self.__children["progressReq"] = 0
		self.__UpdateProgressDisplay()

	def __UpdateProgressDisplay(self):
		cur = self.__children["progressCur"] if self.__children.has_key("progressCur") else 0
		req = self.__children["progressReq"] if self.__children.has_key("progressReq") else 0
		if self.__children.has_key("progressText"):
			self.__children["progressText"].SetText("%s %d / %d" % (localeinfo.AUTO_SKLLL_READER_PROGRESS, cur, req))
		if self.__children.has_key("progressGauge"):
			self.__children["progressGauge"].SetPercentage(cur, req if req > 0 else 1)

	def ServerSetProgress(self, skillIdx, cur, req):
		selected = self.__SelectedServerSkillIdx()
		if selected == 0 or int(skillIdx) != selected:
			return
		self.__children["progressCur"] = int(cur)
		self.__children["progressReq"] = int(req)
		self.Refresh()
		self.__UpdateProgressDisplay()

	def __UpdateSelectedName(self):
		selectedSkill = self.__children["selectedSkill"] if self.__children.has_key("selectedSkill") else 0
		name = ""
		if selectedSkill:
			currentPage = self.__children["currentPage"] if self.__children.has_key("currentPage") else 0
			skillIndex = player.GetSkillIndex(selectedSkill) if currentPage == 0 else selectedSkill
			name = skill.GetSkillName(skillIndex)
		if self.__children.has_key("nameText"):
			self.__children["nameText"].SetText(name)

	def __ToggleRun(self):
		botStatus = self.__children["botStatus"] if self.__children.has_key("botStatus") else 0
		self.__SetStatus(0 if botStatus else 1)

	def __ReadOnce(self):
		selectedSkill = self.__children["selectedSkill"] if self.__children.has_key("selectedSkill") else 0
		if selectedSkill == 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, getattr(localeinfo, "AUTO_SKLLL_READER_SELECT_FIRST", "First you need select a skill."))
			return
		if self.__SkillToBook(selectedSkill) == 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, getattr(localeinfo, "AUTO_SKLLL_READER_NO_BOOK", "You can't upgrade this skill!"))
			return
		net.SendChatPacket("/auto_skill_reader read {}".format(self.__SelectedServerSkillIdx()))

	def OpenForSkill(self, skillIdx):
		# Open the reader on the tab that owns this skill and preselect it (used by the
		# uicharacter reader button, mirroring OpenForBook for passive skill books).
		skillIdx = int(skillIdx)
		if not self.IsShow():
			self.Open()
		botStatus = self.__children["botStatus"] if self.__children.has_key("botStatus") else 0
		if botStatus:
			return
		if skillIdx in PAGE_SKILLS[0]:      # main skill slots 1-6 -> Basic tab
			page = 0
		elif skillIdx in PAGE_SKILLS[2]:    # buffi 163-166 -> Buffi tab
			page = 2
		elif skillIdx in PAGE_SKILLS[1]:    # passives -> Passive tab
			page = 1
		else:
			page = 0
		self.__children["currentPage"] = page
		self.__children["selectedSkill"] = skillIdx
		self.Refresh()
		self.__ResetProgress()
		self.__RequestProgress()

	def OpenForBook(self, vnum):
		if not self.IsShow():
			self.Open()
		botStatus = self.__children["botStatus"] if self.__children.has_key("botStatus") else 0
		if vnum in (BUFFI_BOOK_VNUM, BUFFI_BOOK_VNUM_GM):
			# buffi books open straight to the buffi tab (page 2), like 50350 opens the main tab
			self.__children["currentPage"] = 2
			self.Refresh()
		elif vnum in PASSIVE_BOOK_TO_SKILL and not botStatus:
			self.__children["currentPage"] = 1
			self.__children["selectedSkill"] = PASSIVE_BOOK_TO_SKILL[vnum]
			self.Refresh()
			self.__ResetProgress()
			self.__RequestProgress()
		else:
			self.__children["currentPage"] = 0
			self.Refresh()

	def __SetStatus(self, status):
		botStatus = self.__children["botStatus"] if self.__children.has_key("botStatus") else 0
		if botStatus == status:
			self.Refresh()
			return
		selectedSkill = self.__children["selectedSkill"] if self.__children.has_key("selectedSkill") else 0
		if status:
			if selectedSkill == 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, getattr(localeinfo, "AUTO_SKLLL_READER_SELECT_FIRST", "First you need select a skill."))
				return
			elif self.__SkillToBook(selectedSkill) == 0:
				chat.AppendChat(chat.CHAT_TYPE_INFO, getattr(localeinfo, "AUTO_SKLLL_READER_NO_BOOK", "You can't upgrade this skill!"))
				return
		net.SendChatPacket("/auto_skill_reader status {} {}".format(self.__SelectedServerSkillIdx(), int(status)))

	def __SkillToMaxGrade(self, skillIdx):
		if skillIdx >= 1 and skillIdx <= 6:
			return SKILL_L_MASTER
		else:
			__skillToMaxGrade = {
				122 : SKILL_PERFECT_MASTER,
				123 : SKILL_PERFECT_MASTER,
				124 : SKILL_PERFECT_MASTER,
				121 : SKILL_PERFECT_MASTER,
				246 : SKILL_PERFECT_MASTER,
				210 : SKILL_PERFECT_MASTER,
				211 : SKILL_PERFECT_MASTER,
				212 : SKILL_PERFECT_MASTER,
				133 : SKILL_PERFECT_MASTER,
				134 : SKILL_PERFECT_MASTER,
			}
			if __skillToMaxGrade.has_key(skillIdx):
				return __skillToMaxGrade[skillIdx]
		return 0

	def __SkillToBook(self, skillIdx):
		if skillIdx >= 1 and skillIdx <= 6:
			grade = player.GetSkillGrade(skillIdx)
			if grade == 1:
				return 50350 # one unified book for all active main skills (Master grade)
			elif grade == 2:
				return 50513
		elif skillIdx == 9:
			grade = player.GetSkillGrade(skillIdx)
			if grade == 1:
				return [50300, player.GetSkillIndex(skillIdx)] if USE_YMIR_50300_SKILLBOOK else 50393 + player.GetSkillIndex(skillIdx)
			elif grade == 2:
				return 50527
		else:
			# Buffi level-storage skills (163-166) mirror main skills: Master reads one book,
			# Grand Master a separate book. GetSkillGradeNew returns the server masterType
			# (1 = Master, 2 = Grand Master, 3 = Perfect); matches the server SkillToBook.
			if 163 <= skillIdx <= 166:
				grade = player.GetSkillGradeNew(skillIdx)
				if grade == 1:
					return BUFFI_BOOK_VNUM
				elif grade == 2:
					return BUFFI_BOOK_VNUM_GM
				return 0
			if 122 == skillIdx and player.GetSkillLevelNew(skillIdx) >= 2:#combo_checking_level
				return 0

			# if skill has 1 book put here
			__skillBookItemList = {
				122 : 50304,
				124 : 50600,
				246 : 50325,
			}
			if __skillBookItemList.has_key(skillIdx):
				return __skillBookItemList[skillIdx]

			#if skill different book for every stage(M | G | P)
			__skillBookItemList = {
				210 : { SKILL_MASTER : 59900, SKILL_GRAND_MASTER : 59901, SKILL_PERFECT_MASTER : 59902, },
				211 : { SKILL_MASTER : 59903, SKILL_GRAND_MASTER : 59904, SKILL_PERFECT_MASTER : 59905, },
				212 : { SKILL_MASTER : 59906, SKILL_GRAND_MASTER : 59907, SKILL_PERFECT_MASTER : 59908, },
				121 : {
					SKILL_MASTER : 50301,
					SKILL_GRAND_MASTER : 50302,
					SKILL_PERFECT_MASTER : 50303,
				},
				123 : {
					SKILL_MASTER : 50902,
					SKILL_GRAND_MASTER : 50903,
					SKILL_PERFECT_MASTER : 50904,
				},
				133 : {
					SKILL_MASTER : 50338,
					SKILL_GRAND_MASTER : 50339,
					SKILL_PERFECT_MASTER : 50340,
				},
				134 : {
					SKILL_MASTER : 50341,
					SKILL_GRAND_MASTER : 50342,
					SKILL_PERFECT_MASTER : 50343,
				},
			}
			if __skillBookItemList.has_key(skillIdx):
				grade = player.GetSkillGradeNew(skillIdx)
				if __skillBookItemList[skillIdx].has_key(grade):
					return __skillBookItemList[skillIdx][grade]
		return 0

	def __OnSelectItemSlot(self, selectedSlotPos):
		botStatus = self.__children["botStatus"] if self.__children.has_key("botStatus") else 0
		if botStatus:
			return
		selectedSkill = self.__children["selectedSkill"] if self.__children.has_key("selectedSkill") else 0
		self.__children["selectedSkill"] = 0 if selectedSkill == selectedSlotPos else selectedSlotPos
		self.Refresh()
		self.__ResetProgress()
		self.__RequestProgress()
		return True

	def Refresh(self):
		__data = self.__children["data"] if self.__children.has_key("data") else {}
		currentPage = self.__children["currentPage"] if self.__children.has_key("currentPage") else 0
		selectedSkill = self.__children["selectedSkill"] if self.__children.has_key("selectedSkill") else 0

		for page, data in __data.items():
			slots = data["slots"]
			sw = self.__children["slotWindow"+str(page)]
			tab = self.__children["categoryBtn"+str(page)]
			if page == currentPage:
				tab.Down()
				for sk, pos in slots.items():
					self.__children["slotImg"+str(page)+str(sk)].Show()
					if page == 0:
						grade = player.GetSkillGrade(sk)
						level = player.GetSkillLevel(sk)
						sw.SetSkillSlotNew(sk, player.GetSkillIndex(sk), grade, level)
					else:
						grade = player.GetSkillGradeNew(sk)
						level = player.GetSkillLevelNew(sk)
						# Buffi (163-166) are ACTIVE skills: only their per-grade GradeData[].pImage
						# is loaded -- the top-level pImage is NULL, so SetSkillSlot()/skill.GetIconImage()
						# would dereference NULL and crash the client. Render them via the grade-aware
						# path (skill.GetIconImageNew), exactly like uicharacter's buffi page does.
						if page == 2:
							sw.SetSkillSlotNew(sk, sk, grade, level)
						else:
							sw.SetSkillSlot(sk, sk, level)
					sw.SetSlotCountNew(sk, grade, level)
					if selectedSkill == sk:
						sw.ActivateSlot(sk)
					else:
						sw.DeactivateSlot(sk)
				sw.RefreshSlot()
				sw.Show()
			else:
				tab.SetUp()
				for sk in slots.keys():
					self.__children["slotImg"+str(page)+str(sk)].Hide()
				sw.Hide()

		# support items + the book being read
		itemSW = self.__children["itemSlotWindow"]
		for j, vnum in enumerate(SUPPORT_ITEMS):
			cnt = player.GetItemCountByVnum(vnum)
			itemSW.SetItemSlot(j, vnum, cnt)
			if cnt:
				itemSW.EnableSlot(j)
			else:
				itemSW.DisableSlot(j)

		book = self.__SkillToBook(selectedSkill) if selectedSkill else 0
		if isinstance(book, list):
			book_count = player.GetItemCountByVnumNew(book[0], book[1])
			book_vnum = book[0]
		elif book:
			book_count = player.GetItemCountByVnum(book)
			book_vnum = book
		else:
			book_count = 0
			book_vnum = 0
		itemSW.SetItemSlot(3, book_vnum, book_count)
		if book_count:
			itemSW.EnableSlot(3)
		else:
			itemSW.DisableSlot(3)
		itemSW.RefreshSlot()

		self.__UpdateSelectedName()

		botStatus = self.__children["botStatus"] if self.__children.has_key("botStatus") else 0
		if self.__children.has_key("readAllBtn"):
			self.__children["readAllBtn"].SetText(localeinfo.AUTO_SKLLL_READER_STOP if botStatus else localeinfo.AUTO_SKLLL_READER_START)

	def __ItemSlotVnum(self, slotNumber):
		# vnum behind an item slot: 0..2 = support items, 3 = the book being read.
		if slotNumber < len(SUPPORT_ITEMS):
			return SUPPORT_ITEMS[slotNumber]
		selectedSkill = self.__children["selectedSkill"] if self.__children.has_key("selectedSkill") else 0
		if not selectedSkill:
			return 0
		book = self.__SkillToBook(selectedSkill)
		if isinstance(book, list):
			return book[0]
		return book or 0

	def __AppendWikiHint(self, tooltipItem):
		if not app.ENABLE_INGAME_WIKI:
			return
		tooltipItem.DeclareShortcut(("key_lclick",), getattr(localeinfo, "BIOLOG_MANAGER_CLICK_WIKI", "Click to open Wiki page"))
		tooltipItem.ShowToolTip()

	def __OnClickItemSlot(self, slotNumber):
		# left click on a support item / book slot -> open its wiki page
		if not app.ENABLE_INGAME_WIKI:
			return
		vnum = self.__ItemSlotVnum(slotNumber)
		if not vnum:
			return
		interface = systemSetting.GetInterfaceHandler()
		if interface:
			interface.OpenWikiToItem(vnum)
		return True

	def OverInItem(self, slotNumber):
		interface = systemSetting.GetInterfaceHandler()
		if not interface or not interface.tooltipItem:
			return
		tooltipItem = interface.tooltipItem

		if slotNumber < len(SUPPORT_ITEMS):
			tooltipItem.SetItemToolTip(SUPPORT_ITEMS[slotNumber])
			self.__AppendWikiHint(tooltipItem)
			return

		# book-being-read slot
		selectedSkill = self.__children["selectedSkill"] if self.__children.has_key("selectedSkill") else 0
		if not selectedSkill:
			return
		book = self.__SkillToBook(selectedSkill)
		if not book:
			return
		if isinstance(book, list):
			tooltipItem.ClearToolTip()
			metinSlot = [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)]
			attrSlot = [(0, 0) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
			metinSlot[0] = book[1]
			tooltipItem.AddItemData(book[0], metinSlot, attrSlot)
			tooltipItem.ShowToolTip()
		else:
			tooltipItem.SetItemToolTip(book)
		self.__AppendWikiHint(tooltipItem)

	def OverOutItem(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.HideToolTip()

	def OverOutSkill(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipSkill:
			interfaceHandler.tooltipSkill.HideToolTip()

	def OverInSkill(self, slotNumber):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipSkill:
			currentPage = self.__children["currentPage"] if self.__children.has_key("currentPage") else 0
			skillIndex = player.GetSkillIndex(slotNumber) if currentPage == 0 else slotNumber
			skillLevel = player.GetSkillLevel(slotNumber) if currentPage == 0 else player.GetSkillLevelNew(slotNumber)
			skillGrade = player.GetSkillGrade(slotNumber) if currentPage == 0 else player.GetSkillGradeNew(slotNumber)
			interfaceHandler.tooltipSkill.SetSkillNew(slotNumber, skillIndex, skillGrade, skillLevel)

	def __SetPage(self, pageIdx):
		self.__children["currentPage"] = pageIdx
		botStatus = self.__children["botStatus"] if self.__children.has_key("botStatus") else 0
		if botStatus:
			# keep the running skill selected so Stop still targets it and progress keeps updating
			self.Refresh()
			self.__RequestProgress()
			return
		self.__children["selectedSkill"] = 0
		self.Refresh()
		self.__ResetProgress()

	def __CreateSlot(self, parent, x, y):
		return CreateWindow(ui.ImageBox(), parent, (x, y), "d:/ymir work/ui/public/slot_base.sub")

	def __RegisterBuffiSkillSlots(self):
		# Buffi skills (163-166) have no native player skill-slot; the client drops their
		# level for any vnum with no registered slot (SetSkillLevel_ early-returns). Reserve
		# slots 130-133 -- the same mapping uicharacter uses -- so the normal skill packet
		# fills the grade/level the buffi page reads. Idempotent and never clears existing
		# levels (player.SetSkill only sets the slot's skill index).
		if not app.__BUFFI_SUPPORT__:
			return
		for i in xrange(self.BUFFI_SKILL_COUNT):
			player.SetSkill(self.BUFFI_SKILL_SLOT_START + i, self.BUFFI_SKILL_VNUM_START + i)

	def Open(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "AUTO_SKILL_READER")
		self.__RegisterBuffiSkillSlots()
		self.Refresh()
		self.Show()
		net.SendChatPacket("/auto_skill_reader helper_query")   # sync helper checkbox with server state

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "AUTO_SKILL_READER")
		self.Hide()
		return True

	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("AUTO_SKILL_READER", x, y)

	def OnPressEscapeKey(self):
		self.Close()
		return True

def CreateWindow(window, parent, windowPos, windowArgument = "", windowPositionRule = "", windowSize = (-1, -1), windowFontName = -1):
	window.SetParent(parent)
	window.SetPosition(*windowPos)
	if windowSize != (-1, -1):
		window.SetSize(*windowSize)
	if windowPositionRule:
		splitList = windowPositionRule.split(":")
		if len(splitList) == 2:
			(type, mode) = (splitList[0], splitList[1])
			if type == "horizontal":
				if isinstance(window, ui.TextLine):
					if mode == "center":
						window.SetHorizontalAlignCenter()
					elif mode == "right":
						window.SetHorizontalAlignRight()
					elif mode == "left":
						window.SetHorizontalAlignLeft()
				else:
					if mode == "center":
						window.SetWindowHorizontalAlignCenter()
					elif mode == "right":
						window.SetWindowHorizontalAlignRight()
					elif mode == "left":
						window.SetWindowHorizontalAlignLeft()
			elif type == "vertical":
				if isinstance(window, ui.TextLine):
					if mode == "center":
						window.SetVerticalAlignCenter()
					elif mode == "top":
						window.SetVerticalAlignTop()
					elif mode == "bottom":
						window.SetVerticalAlignBottom()
				else:
					if mode == "top":
						window.SetWindowVerticalAlignTop()
					elif mode == "center":
						window.SetWindowVerticalAlignCenter()
					elif mode == "bottom":
						window.SetWindowVerticalAlignBottom()
	if windowArgument:
		if isinstance(window, ui.TextLine):
			if windowFontName != -1:
				window.SetFontName(windowFontName)
			window.SetText(windowArgument)
		elif isinstance(window, ui.NumberLine):
			window.SetNumber(windowArgument)
		elif isinstance(window, ui.ExpandedImageBox) or isinstance(window, ui.ImageBox):
			window.LoadImage(windowArgument if windowArgument.find("gr2") == -1 else "icon/item/27995.tga")
	window.Show()
	return window
