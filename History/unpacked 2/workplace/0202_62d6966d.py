# coding: latin_1
#
# Companion window (buffi system client UI).
#
# Built top-down, one region at a time. The whole layout (board chrome,
# background panel, Name/Level/Intelligence detail rows, "Experience" subheader,
# 4 buffi-skill icon placeholders, Evolve/Duration buttons) is declared in
# uiscript/companionwindow.py; this module only binds the widgets (GetChild),
# wires the button events, and attaches the 3D buffi render target.
# Lower regions (Ore slots, Duration gauge, Skills list, bottom stat table)
# are added in later increments.
#
# Source contract (see docs/BUFFI_EVOLUTION.md "P5 source contract"):
#   inbound : BINARY_OnBuffiStatus -> interface -> RefreshFromStatus(...)
#   outbound: net.SendBuffiPacket(net.BUFFI_CG_*, pos)
#   static  : app.GetBuffiEvolveInfo(stage)
# Gated on app.__BUFFI_SUPPORT__; evolution probed via hasattr(app,"GetBuffiEvolveInfo").

import ui
import app
import net
import chat
import item
import skill
import player
import wndMgr
import osfinfo
import mousemodule
import localeinfo
import uitooltip
import uicommon
import uicompanionride

# Window geometry, background, detail rows, subheader, skill icons and buttons
# all live in uiscript/companionwindow.py now; this module just binds + wires them.
# Client mob_proto row rendered as the shaman-PC buffi (data vnum, see buffi.hpp).
BUFFI_MOB_VNUM = 60666
# Asset path (must match PATH in uiscript/companionwindow.py) for runtime EXP-ball image swaps.
BUFFI_UI_PATH  = "d:/ymir work/ui/game/companion/"
# Duration gauge reference (matches server BUFFI_DURATION_MAX = 30 days) + the permanent sentinel.
BUFFI_MAX_DURATION_SEC   = 30 * 24 * 60 * 60
BUFFI_DURATION_PERMANENT = 0xFFFFFFFF
# Per-slot INT cap an ore can grant (mirrors server BUFFI_ORE_INT_EACH) -- used for the ore tooltip.
BUFFI_ORE_INT_EACH       = 3
# Third section (skills + bonuses). The 4 buffi skills (vnums 163-166 = Hosin/Gicheon/Kwaesok/Jeungryeok)
# are registered into this client slot range so grade/level/efficiency resolve (mirrors uicharacter's
# buffi page). Kwaesok+Jeungryeok (index 2,3) are premium: only cast while the buffi is named.
BUFFI_SKILL_SLOT_START = 130
BUFFI_SKILL_VNUM_START = 163
BUFFI_SKILL_COUNT      = 4
BUFFI_BOOK_VNUM        = 50351        # auto-skill-reader buffi book -> opens the buffi skill page (page 2)
BUFFI_PREMIUM_SKILLS   = (2, 3)       # name-gated skills (greyed/locked while unnamed)
BUFFI_SKILL_SUFFIX     = ("%", "%", "%", "")   # melee-resist% / crit% / move-speed% / attack(flat)
# Bottom bonus list is a SCROLLABLE region (clip viewport + thin scrollbar) so it can grow -- the 4
# skill bonuses + a boss-damage row (and future rows) -- without resizing the fixed window. Rows are
# built in code as children of a clipped scrollBoard; bg = skill_value.png (257x25) scaled to row width.
BONUS_ROW_W = 240   # scrolled content width (= bonusViewport width)
BONUS_ROW_H = 26    # row pitch
BONUS_IMG_H = 25    # skill_value.png native height
# Page tab rail (left column in the uiscript): the window hosts multiple companion pages.
# PAGE_PET is an empty placeholder for the growth-pet rework -- its widgets will live inside
# the "petPage" uiscript container with names starting with "pet" (the page toggle keys on that).
PAGE_BUFFI = 0
PAGE_PET   = 1
PAGE_RIDE  = 2
# ---- Pet page (growth pet rework, U2 data binding) -------------------------
# Stat-potion vnums shown in the 3 stat-row icon slots: [statIndex][sizeClass].
# The size class derives from the pet's CURRENT Type stat-cap (<= 5% -> S,
# <= 10% -> M, else L), so each row always advertises the potion that can still
# raise that stat. Since U6 these are LIVE: clicking a row finds this vnum in
# the inventory and sends the stat-potion batch packet -- so the table MUST
# point at the real potion items before ship (ITEM_PET / PET_STAT_POTION,
# Value0 = stat 0/1/2, Value1 = size %, Value2 = step permille). The server
# validates type/subtype, so a wrong vnum here is dead UI, not an exploit.
# A 0 entry leaves the slot empty (and the row unclickable).
PET_STAT_POTION_VNUMS = (
	(55101, 55104, 55107),   # stat 0: Max HP          (S, M, L)
	(55102, 55105, 55108),   # stat 1: Attack PvM/PvP  (S, M, L)
	(55103, 55106, 55109),   # stat 2: Elemental       (S, M, L)
)
PET_SKILL_SLOT_COUNT = 6     # display slots on the page (matches PET_SKILL_COUNT_MAX)

def unsigned32(n):
	# GetPetExpPoints crosses the C boundary as signed ints; wrap like uipetinfo does.
	return n & 0xFFFFFFFF

class CompanionWindow(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Initialize()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Initialize(self):
		self.isLoaded       = 0
		self.board          = None
		self.portrait       = None   # portraitFrame widget (from uiscript)
		self.portraitRender = None   # 3D buffi render target (created in code)
		self.btnEvolve      = None
		self.btnDuration    = None
		self.emptyText      = None   # centered "no buffi summoned" notice (shown only while unsummoned)
		self.btnHelp        = None   # "?" help button (buffi + ride pages; hidden on the pet page)
		self.btnPetHelp     = None   # pet-page "?" (general pet help; pet page only, same titlebar spot)
		self.btnPetExpHelp  = None   # "?" beside the pet EXP header (leveling-journey help; inside petPage)
		self.detailValues   = {}     # "name" / "level" / "int" -> value TextLine
		self.expBalls       = []     # 4 EXP orb fill layers (progress.png), each clipped for smooth % fill
		self.expOverlay     = None   # transparent hover target over the EXP balls
		self.oreSlotWindow  = None   # SlotWindow over the 3 ore-slot backgrounds (icons + drag-insert + hover tooltip)
		self.oreVnums       = (0, 0, 0)  # socketed ore item vnums per slot (for the hover tooltip)
		self.oreExpire      = (0, 0, 0)  # per-slot wall-clock expiry unix ts (for the hover tooltip)
		self.oreToolTip     = None   # lazily-created ore tooltip (+INT + remaining duration)
		self.durationGaugeFill = None  # expanded_image gauge fill, clipped by remaining duration
		self.durationText   = None   # remaining-duration text under the gauge
		self.durationConfirmDlg = None  # confirm popup before consuming a duration item (anti ghost-click)
		self.durationExpireAt = 0    # cached buffi expiry (for the per-second live countdown tick)
		self.durationTickLast = 0    # last server-second the countdown text was re-rendered
		self.summonedNow    = 0      # last-known summon state (gates the live tick)
		self.expToolTip     = None   # lazily-created EXP tooltip
		self.expCur         = 0
		self.expNext        = 0
		self.expIsMax       = 0
		self.hasBuffi       = 0
		self.nameOverlay    = None   # transparent hover target over the name row (nickname tooltip)
		self.nameToolTip    = None   # lazily-created nickname tooltip (remaining time + grants)
		self.nameExpire     = 0      # nickname window expiry unix ts (0 = unnamed, 0xFFFFFFFF = permanent)
		self.bossPct        = 0      # boss-damage % granted by the nickname
		self.isNamed        = 0      # whether the nickname is currently active
		self.buffiStage     = 0      # current evolution stage 0..3 (set from status; drives the Upgrade window)
		self.evolveFail     = 0      # evolve pity counter (consecutive fails; guaranteed at BUFFI_EVOL_PITY)
		self.buffiSkillSlot = None   # SlotWindow holding the 4 buffi-skill icons (third section)
		self.skillPlusBtns  = []     # 4 "+" buttons -> open the auto-skill-reader buffi page
		self.skillLocks     = {}     # premium-skill lock overlays (skill index -> ImageBox)
		self.skillBonusText = []     # 4 skill bonus value TextLines (= first 4 of the scroll list)
		self.bonusViewport  = None   # clip window for the scrollable bonus list
		self.bonusScrollBoard = None # content window (moved by the scrollbar), clipped to the viewport
		self.bonusScroll    = None   # thin scrollbar
		self.bonusWidgets   = []     # all code-built bonus row widgets (held so they aren't GC'd)
		self.bonusValueText = []     # per-row value TextLines (last one = boss damage)
		self.bossValueText  = None   # the boss-damage row's value cell
		self.bonusContentH  = 0
		self.bonusViewH     = 0
		self.interface      = None   # set by interfacemodule after construction (to open the skill reader)
		self.currentPage    = PAGE_BUFFI  # active page (PAGE_BUFFI / PAGE_PET)
		self.tabButtons     = []     # page tab rail radio-buttons, indexed by PAGE_*
		self.petPage        = None   # pet page container (U1 skeleton; controller lands in U2+)
		# Pet page widgets. The per-index lists are INDEX-PARALLEL (may hold None) because the
		# index IS the identity -- orb i = EXP quarter i, list i = stat i, slot i = skill slot i --
		# so a missing widget must not shift its neighbours (unlike the buffi expBalls, where the
		# compacted list only ever gets zero-clipped in bulk). Every use guards on truthiness.
		self.petExpBalls         = []    # 4 EXP orb fill layers
		self.petStatFills        = []    # 3 stat-bar fill layers (fill-to-Type-cap)
		self.petDurationGaugeFill = None # duration gauge fill layer
		# Pet page controller state (U2 data binding)
		self.petDetailValues = {}    # "name" / "type" / "level" -> value TextLine
		self.petIconSlot     = None  # summon-item icon slot (portrait corner)
		self.petStatValues   = []    # 3 stat value TextLines
		self.petStatIconSlots = []   # 3 potion-icon SlotWindows (vnum by stat + Type size class)
		self.petSkillSlotWnd = None  # the 6-slot skill SlotWindow
		self.petSkillLocks   = []    # 6 lock overlays (level-gated: 0-2 @ lv90, 3-5 @ lv105)
		self.petSkillPluses  = []    # 6 "+" buttons (hidden until U4 wires the upgrade dialog)
		self.petEmptyNotice  = None  # centered "no pet summoned" notice (duration strip)
		self.petDurationText = None
		self.petDurationEnd  = 0     # pet expiry unix ts (drives the per-second countdown tick)
		self.petDurationMax  = 0     # pet max lifetime seconds (gauge reference)
		self.petDurationTickLast = 0
		self.petExpToolTip   = None  # lazily-created EXP tooltip (battle + item exp numbers)
		self.petExpData      = (0, 0, 0, 0)  # (curEXP, nextEXP, itemEXP, itemMaxEXP) for the tooltip
		self.petHasPet       = 0     # last-known summon state (gates the live duration tick)
		# Drag-to-learn / drag-to-delete on the skill slots (book -> empty slot, del book ->
		# filled slot; mirrors the legacy pet window's drag flows). Pending send state:
		self.petSkillBookSlot = -1   # learn: target skill slot
		self.petSkillBookCell = -1   # learn: book inventory cell
		self.petSkillDelSlot  = -1   # delete: target skill slot
		self.petSkillDelCell  = -1   # delete: del-book inventory cell
		self.petSkillQuestionDlg = None   # shared confirm dialog for both drops
		# Stat-row potion slots (U6): click -> "apply how many?" -> CG stat-potion batch.
		self.petStatPotionVnums = [0, 0, 0]   # advertised vnum per stat row (click + hover target)
		self.petPotionToolTip   = None        # lazily-created potion hover tooltip
		self.petPotionPickDlg   = None        # lazily-created quantity dialog (uicommon.PickItemDialog)
		self.petPotionPickVnum  = 0           # vnum the open dialog was armed with (stale-cell guard)
		# Locked-skill-slot hover -> "unlocks at pet level N" tooltip. Geometry-driven from
		# OnUpdate: a locked slot is an EMPTY SlotWindow cell (the engine only fires item
		# hover events for filled cells) and the lock overlays are not_pick ON PURPOSE
		# (book drops must reach the slot beneath) -- so no widget event can carry this.
		self.petLockToolTip  = None
		self.petLockHoverIdx = -1             # lock index currently hovered (-1 = none)
		# Ride page controller state (growth mount rework, client Task 7).
		self.ridePage        = None   # ride page container (names starting with "ride")
		self.ridePortraitIcon = None  # static mount_voucher glyph (fallback, no costume/skin worn)
		self.ridePortraitSlot = None  # live equipped costume/skin icon (SlotWindow)
		self.ridePortraitVnum = 0     # vnum currently shown in ridePortraitSlot (0 = glyph shown)
		self.ridePortraitToolTip = None  # lazily-created ItemToolTip for the portrait slot
		self.rideStatus      = None   # last BINARY_OnGrowthMountStatus tuple (None until requested)
		self.rideDetailValues = {}    # "name" / "level" / "skills" -> value TextLine
		self.rideExpGaugeFill = None  # exp gauge fill layer (same progress as the orbs)
		self.rideExpBalls    = []     # 4 EXP orb fill layers (index-parallel, like the pet orbs)
		self.rideExpText     = None
		self.rideUpgradeButton = None
		self.rideSkillLocks  = []     # 4 lock overlays (level-gated: 5/12/21/30)
		self.rideSkillPluses = []     # 4 "+" buttons -> RideSkillDialog
		self.rideBonusArea   = None   # container for the code-built bonus rows
		self.rideBonusWidgets = []    # code-built bonus row widgets (held so they aren't GC'd)
		self.rideBonusValues = []     # per-skill bonus value TextLines ("+N%" once unlocked)
		self.rideEmptyText   = None   # centered "summon your mount" notice (mount-called gate, Task 9)
		self.rideUpgradeDlg  = None    # RideUpgradeDialog (owned directly -- no interfacemodule wiring)
		self.rideSkillDlg    = None    # RideSkillDialog
		self.rideExpHelpBtn   = None  # "?" beside the EXP header -> OpenCompanionRideHelp(0)
		self.rideSkillHelpBtn = None  # "?" beside the Skills header -> OpenCompanionRideHelp(1)
		self.rideExpToolTip   = None  # lazily-created EXP tooltip (gauge + ball cluster hover)
		self.rideSkillToolTip = None  # lazily-created skill tooltip (locked hint / unlocked name+level)
		self.rideTabAvailable = True  # False on a flag-off client (no net.SendGrowthMountPacket) -- tab stays hidden/unreachable

	def Destroy(self):
		if self.durationConfirmDlg:
			self.durationConfirmDlg.Close()
			self.durationConfirmDlg = None
		if self.petSkillQuestionDlg:
			self.petSkillQuestionDlg.Close()
			self.petSkillQuestionDlg = None
		if self.petPotionPickDlg:
			self.petPotionPickDlg.Close()
			self.petPotionPickDlg.Destroy()   # PickItemDialog unwires its own edit/button events
			self.petPotionPickDlg = None
		if self.rideUpgradeDlg:
			self.rideUpgradeDlg.Close()
			self.rideUpgradeDlg.Destroy()
			self.rideUpgradeDlg = None
		if self.rideSkillDlg:
			self.rideSkillDlg.Close()
			self.rideSkillDlg.Destroy()
			self.rideSkillDlg = None
		self.ClearDictionary()
		self.Initialize()

	# ------------------------------------------------------------------
	# Load + bind (everything is declared in uiscript/companionwindow.py)
	# ------------------------------------------------------------------
	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = 1
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/companionwindow.py")

		# Built at interface startup; guard so a layout/locale error logs to
		# syserr instead of aborting the whole client boot.
		try:
			self.board = self.GetChild("board")
			self.board.SetTitleName(localeinfo.COMPANION_TITLE)
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
			self.__BindWidgets()
		except:
			import dbg
			dbg.TraceError("CompanionWindow.__LoadWindow - bind failed")

	def __BindWidgets(self):
		# Detail value cells (declared in the uiscript) -> filled by RefreshFromStatus.
		self.detailValues["name"]  = self.GetChild("detailsName_text_value")
		self.detailValues["level"] = self.GetChild("detailslevel_text_value")
		self.detailValues["int"]   = self.GetChild("detailsInt_text_value")

		# Buttons (declared in the uiscript) -> wire the click events.
		self.btnEvolve = self.GetChild("evolveButton")
		self.btnEvolve.SetEvent(ui.__mem_func__(self.__OnClickEvolve))
		self.btnDuration = self.GetChild("durationButton")
		self.btnDuration.SetEvent(ui.__mem_func__(self.__OnClickDuration))

		# Help "?" button -> opens the buffi-system explainer popup. Always available (it is in the
		# __ApplyEmptyState keep-set), so a new player with no buffi can still read how it works.
		self.btnHelp = self.GetChild2("helpButton")
		if self.btnHelp:
			self.btnHelp.SetEvent(ui.__mem_func__(self.__OnClickHelp))
			self.btnHelp.SetToolTipText(getattr(localeinfo, "COMPANION_HELP_TITLE", "Buffi - Help"), 0, -16)
		# Pet-page help "?" buttons (H2a general / H2b EXP journey). The general one
		# shares the buffi "?"'s titlebar spot and starts hidden (buffi page is the
		# default); the EXP one lives inside petPage so it toggles with the page.
		self.btnPetHelp = self.GetChild2("petHelpButton")
		if self.btnPetHelp:
			self.btnPetHelp.SetEvent(ui.__mem_func__(self.__OnClickPetHelp))
			self.btnPetHelp.SetToolTipText(getattr(localeinfo, "PET_HELP_TITLE_GEN", "Companion Pet - Help"), 0, -16)
			self.btnPetHelp.Hide()
		self.btnPetExpHelp = self.GetChild2("petExpHelpButton")
		if self.btnPetExpHelp:
			self.btnPetExpHelp.SetEvent(ui.__mem_func__(self.__OnClickPetExpHelp))
			self.btnPetExpHelp.SetToolTipText(getattr(localeinfo, "PET_HELP_TITLE_EXP", "Pet EXP - Help"), 0, -16)

		# Attach the live 3D buffi model to the portrait frame (best-effort; needs
		# the mob present in the client mob_proto).
		self.portrait = self.GetChild("portraitFrame")
		try:
			if app.ENABLE_INGAME_WIKI:
				import ingamewikiui
				rt = ingamewikiui.WikiRenderTarget(64, 64)
				rt.SetParent(self.portrait)
				rt.SetPosition(0, -3)
				rt.SetModel(BUFFI_MOB_VNUM, False, False)
				rt.Show()
				self.portraitRender = rt
		except:
			pass

		# The 4 EXP orbs (fill layers) -> each clipped per-orb for SMOOTH progress in RefreshFromStatus.
		# Start fully clipped (empty) so the static progress_empty.png orbs behind show until status arrives.
		self.expBalls = []
		for i in range(4):
			ball = self.GetChild("expBall%d" % i)
			if ball:
				ball.SetRenderingRect(0.0, -1.0, 0.0, 0.0)
				self.expBalls.append(ball)

		# Hover target over the balls -- declared in the uiscript as "expHover" (so RTL mirroring keeps it
		# aligned with the balls, unlike a code-created window). Bind the tooltip events only; create nothing.
		self.expOverlay = self.GetChild("expHover")
		if self.expOverlay:
			self.expOverlay.SetOverInEvent(ui.__mem_func__(self.__OnOverInExp))
			self.expOverlay.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutExp))

		# Hover target over the name row -> tooltip with the nickname's remaining time + what it grants
		# (boss damage + the 2 unlocked buffs). Declared in the uiscript so it RTL-mirrors with the name.
		self.nameOverlay = self.GetChild2("nameHover")
		if self.nameOverlay:
			self.nameOverlay.SetOverInEvent(ui.__mem_func__(self.__OnOverInName))
			self.nameOverlay.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutName))

		# Second section (declared in the uiscript): ore SlotWindow (render-LEFT) + duration gauge/text
		# (render-RIGHT). Ore drop = insert. Ores are CONSUMED on socket and auto-expire after a real-time
		# lifetime -- they are NOT removable -- so the only filled-slot interaction is the hover tooltip
		# (+INT + remaining duration). Icons filled by RefreshFromStatus.
		self.oreSlotWindow = self.GetChild("oreSlotWindow")
		if self.oreSlotWindow:
			self.oreSlotWindow.SetSelectEmptySlotEvent(ui.__mem_func__(self.__OnOreDropInsert))
			self.oreSlotWindow.SetOverInItemEvent(ui.__mem_func__(self.__OnOreOverIn))
			self.oreSlotWindow.SetOverOutItemEvent(ui.__mem_func__(self.__OnOreOverOut))
			# >>> SECTION BEGIN: ore removal disabled (ores auto-expire, non-removable). Kept for revival.
			# self.oreSlotWindow.SetUnselectItemSlotEvent(ui.__mem_func__(self.__OnOreSlotUse))
			# self.oreSlotWindow.SetUseSlotEvent(ui.__mem_func__(self.__OnOreSlotUse))
			# <<< SECTION END
		self.durationGaugeFill = self.GetChild("durationGaugeFill")
		self.durationText = self.GetChild("durationText")
		if self.durationGaugeFill:
			self.durationGaugeFill.SetRenderingRect(0.0, 0.0, -1.0, 0.0)   # start empty until status arrives

		# Third section (skills + bonuses): 4 buffi-skill icons (SlotWindow) + per-skill "+" (opens the
		# auto-skill-reader buffi page) + premium lock overlays + the 4 bonus value texts. Register the 4
		# skills into their client slot range so grade/level/efficiency resolve (mirrors uicharacter).
		self.buffiSkillSlot = self.GetChild2("buffiSkillSlot")
		if self.buffiSkillSlot:
			for i in range(BUFFI_SKILL_COUNT):
				player.SetSkill(BUFFI_SKILL_SLOT_START + i, BUFFI_SKILL_VNUM_START + i)
			self.buffiSkillSlot.SetOverInItemEvent(ui.__mem_func__(self.__OnSkillOverIn))
			self.buffiSkillSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OnSkillOverOut))
		self.skillPlusBtns = []
		for i in range(BUFFI_SKILL_COUNT):
			btn = self.GetChild2("buffiSkillPlus%d" % i)
			if btn:
				btn.SetEvent(ui.__mem_func__(self.__OnClickSkillPlus))   # any "+" opens the buffi reader page
			self.skillPlusBtns.append(btn)
		self.skillLocks = {}
		for i in BUFFI_PREMIUM_SKILLS:
			self.skillLocks[i] = self.GetChild2("buffiSkillLock%d" % i)
		# Empty-state notice -- bind FIRST so __ApplyEmptyState can always hide/show it even if the
		# bonus-list build below fails (otherwise self.emptyText stays None and the "no buffi" notice
		# is stuck visible while summoned).
		self.emptyText = self.GetChild2("emptyText")

		# Bonus rows are now a scrollable list (4 skill bonuses + a boss-damage row) built in code.
		# Non-fatal: a build error must not abort the rest of __BindWidgets.
		try:
			self.__BuildBonusList()
		except:
			import dbg
			dbg.TraceError("CompanionWindow.__BuildBonusList failed")

		# Page tab rail (buffi / pet) + the pet placeholder container. SAFE_SetEvent wraps the
		# handler in __mem_func__ and forwards the page index. The buffi tab starts pressed.
		self.petPage = self.GetChild2("petPage")

		# Pet page bindings (U2). Zero-clip every fill layer so the page shows EMPTY orbs/gauges
		# until data arrives. All pet widgets live inside the petPage container and their names
		# start with "pet", so the page toggle / buffi empty-state logic never touches them --
		# RefreshPetPage owns their content and visibility.
		self.petExpBalls = []
		for i in range(4):
			ball = self.GetChild2("petExpBall%d" % i)
			if ball:
				ball.SetRenderingRect(0.0, -1.0, 0.0, 0.0)   # vertical fill, start empty
			self.petExpBalls.append(ball)                   # index-parallel (orb i = quarter i)
		self.petDurationGaugeFill = self.GetChild2("petDurationGaugeFill")
		if self.petDurationGaugeFill:
			self.petDurationGaugeFill.SetRenderingRect(0.0, 0.0, -1.0, 0.0)   # horizontal fill, start empty
		self.petStatFills = []
		self.petStatValues = []
		self.petStatIconSlots = []
		for i in range(3):
			fill = self.GetChild2("petStatGaugeFill%d" % i)
			if fill:
				fill.SetRenderingRect(0.0, 0.0, -1.0, 0.0)   # horizontal fill, start empty
			self.petStatFills.append(fill)                  # index-parallel (list i = stat i)
			self.petStatValues.append(self.GetChild2("petStatValue%d" % i))
			statSlot = self.GetChild2("petStatIconSlot%d" % i)
			if statSlot:
				# Each row's single slot is declared with index = row in the uiscript,
				# so the three windows share one handler set keyed on the slot index.
				# Click = quantity dialog (U6); hover = plain item tooltip for the
				# advertised potion (tells the player what to go get).
				statSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnClickPetStatPotion))
				statSlot.SetOverInItemEvent(ui.__mem_func__(self.__OnPetStatPotionOverIn))
				statSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OnPetStatPotionOverOut))
			self.petStatIconSlots.append(statSlot)
		self.petDetailValues["name"]  = self.GetChild2("petName_text_value")
		self.petDetailValues["type"]  = self.GetChild2("petType_text_value")
		self.petDetailValues["level"] = self.GetChild2("petLevel_text_value")
		self.petIconSlot     = self.GetChild2("petIconSlot")
		self.petDurationText = self.GetChild2("petDurationText")
		if self.petDurationText:
			self.petDurationText.SetText("")   # uiscript placeholder text until data arrives
		self.petSkillSlotWnd = self.GetChild2("petSkillSlot")
		if self.petSkillSlotWnd:
			# Hover tooltip = the shared PetSkillToolTip the interface owns (legacy pet window
			# uses the same one; SetPetSkill reads GetPetSkillByIndex and shows itself, and it
			# silently no-ops on an empty slot).
			self.petSkillSlotWnd.SetOverInItemEvent(ui.__mem_func__(self.__OnPetSkillOverIn))
			self.petSkillSlotWnd.SetOverOutItemEvent(ui.__mem_func__(self.__OnPetSkillOverOut))
			# Drag-to-learn / drag-to-delete (the legacy window's book drops, re-hosted):
			# skill book -> EMPTY unlocked slot = learn; deletion book -> FILLED slot = forget.
			self.petSkillSlotWnd.SetSelectEmptySlotEvent(ui.__mem_func__(self.__OnPetSkillEmptySlotDrop))
			self.petSkillSlotWnd.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnPetSkillFilledSlotDrop))
		self.petSkillLocks  = []
		self.petSkillPluses = []
		for i in range(PET_SKILL_SLOT_COUNT):
			self.petSkillLocks.append(self.GetChild2("petSkillLock%d" % i))
			plus = self.GetChild2("petSkillPlus%d" % i)
			if plus:
				plus.SAFE_SetEvent(self.__OnClickPetSkillPlus, i)   # opens the skill-upgrade dialog
				plus.Hide()   # shown per-slot by __RefreshPetSkills (learned + below max only)
			self.petSkillPluses.append(plus)
		# Hover target over the pet EXP orbs -> tooltip with battle + item EXP numbers.
		petExpHover = self.GetChild2("petExpHover")
		if petExpHover:
			petExpHover.SetOverInEvent(ui.__mem_func__(self.__OnOverInPetExp))
			petExpHover.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutPetExp))
		# Page buttons: Upgrade -> the 2-tab Evolve/Type sub-window (U3);
		# Feed -> the tabbed legacy feed window, Experience mode first (U5).
		btnPetUpgrade = self.GetChild2("petUpgradeButton")
		if btnPetUpgrade:
			btnPetUpgrade.SetEvent(ui.__mem_func__(self.__OnClickPetUpgrade))
		btnPetFeed = self.GetChild2("petFeedButton")
		if btnPetFeed:
			btnPetFeed.SetEvent(ui.__mem_func__(self.__OnClickPetFeed))
		# "No pet" notice: RefreshPetPage owns it; hidden until a no-pet state is resolved.
		self.petEmptyNotice = self.GetChild2("petEmptyText")
		if self.petEmptyNotice:
			self.petEmptyNotice.Hide()
		# Ride page bindings (growth mount rework, client Task 7). All widgets live inside the
		# ridePage container and their names start with "ride", so the page toggle / buffi
		# empty-state logic never touches them -- RefreshRidePage owns their content/visibility.
		self.ridePage = self.GetChild2("ridePage")
		self.ridePortraitIcon = self.GetChild2("ridePortraitIcon")   # static glyph fallback
		self.ridePortraitSlot = self.GetChild2("ridePortraitSlot")   # live equipped-mount icon
		if self.ridePortraitSlot:
			self.ridePortraitSlot.SetOverInItemEvent(ui.__mem_func__(self.__OnRidePortraitOverIn))
			self.ridePortraitSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OnRidePortraitOverOut))
			self.ridePortraitSlot.Hide()   # RefreshRidePage picks glyph vs live icon
		self.rideDetailValues["name"]   = self.GetChild2("rideName_text_value")
		self.rideDetailValues["level"]  = self.GetChild2("rideLevel_text_value")
		self.rideDetailValues["skills"] = self.GetChild2("rideSkills_text_value")
		self.rideExpBalls = []
		for i in range(4):
			ball = self.GetChild2("rideExpBall%d" % i)
			if ball:
				ball.SetRenderingRect(0.0, -1.0, 0.0, 0.0)   # vertical fill, start empty
			self.rideExpBalls.append(ball)                  # index-parallel (orb i = quarter i)
		self.rideExpGaugeFill = self.GetChild2("rideExpGaugeFill")
		if self.rideExpGaugeFill:
			self.rideExpGaugeFill.SetRenderingRect(0.0, 0.0, -1.0, 0.0)   # horizontal fill, start empty
		self.rideExpText = self.GetChild2("rideExpText")
		self.rideEmptyText = self.GetChild2("rideEmptyText")
		self.rideExpHelpBtn = self.GetChild2("rideExpHelpButton")
		if self.rideExpHelpBtn:
			self.rideExpHelpBtn.SetEvent(ui.__mem_func__(self.__OnClickRideExpHelp))
			self.rideExpHelpBtn.SetToolTipText(getattr(localeinfo, "GROWTH_MOUNT_HELP_LEVEL_TITLE", "Mount - Leveling"), 0, -16)
		self.rideSkillHelpBtn = self.GetChild2("rideSkillHelpButton")
		if self.rideSkillHelpBtn:
			self.rideSkillHelpBtn.SetEvent(ui.__mem_func__(self.__OnClickRideSkillHelp))
			self.rideSkillHelpBtn.SetToolTipText(getattr(localeinfo, "GROWTH_MOUNT_HELP_SKILL_TITLE", "Mount - Skills"), 0, -16)
		self.rideUpgradeButton = self.GetChild2("rideUpgradeButton")
		if self.rideUpgradeButton:
			self.rideUpgradeButton.SetEvent(ui.__mem_func__(self.__OnClickRideUpgrade))
			self.rideUpgradeButton.Disable()   # enabled only once RefreshRidePage sees exp full
		# EXP hover pick-targets (gauge + ball cluster) -> the same tooltip, same idiom as petExpHover.
		rideExpGaugeHover = self.GetChild2("rideExpGaugeHover")
		if rideExpGaugeHover:
			rideExpGaugeHover.SetOverInEvent(ui.__mem_func__(self.__OnOverInRideExp))
			rideExpGaugeHover.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutRideExp))
		rideExpBallHover = self.GetChild2("rideExpBallHover")
		if rideExpBallHover:
			rideExpBallHover.SetOverInEvent(ui.__mem_func__(self.__OnOverInRideExp))
			rideExpBallHover.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutRideExp))
		self.rideSkillLocks = []
		self.rideSkillPluses = []
		for i in range(uicompanionride.RIDE_SKILL_COUNT):
			self.rideSkillLocks.append(self.GetChild2("rideSkillLock%d" % i))
			plus = self.GetChild2("rideSkillPlus%d" % i)
			if plus:
				plus.SAFE_SetEvent(self.__OnClickRideSkillPlus, i)   # opens the skill-upgrade dialog
				plus.Hide()   # shown per-slot by __RefreshRideSkills (unlocked + below max only)
			self.rideSkillPluses.append(plus)
			skillHover = self.GetChild2("rideSkillHover%d" % i)
			if skillHover:
				skillHover.SAFE_SetOverInEvent(self.__OnOverInRideSkillHover, i)
				skillHover.SAFE_SetOverOutEvent(self.__OnOverOutRideSkillHover)
		# Bonus rows (one per skill, buffi bonus-list row anatomy). Non-fatal, like the buffi build.
		try:
			self.__BuildRideBonusList()
		except:
			import dbg
			dbg.TraceError("CompanionWindow.__BuildRideBonusList failed")
		# Owned directly (no interfacemodule wiring for the ride sub-dialogs): independent
		# top-level windows, started hidden like the buffi/pet dialogs interfacemodule owns.
		self.rideUpgradeDlg = uicompanionride.RideUpgradeDialog()
		self.rideUpgradeDlg.Hide()
		self.rideSkillDlg = uicompanionride.RideSkillDialog()
		self.rideSkillDlg.Hide()

		self.tabButtons = []
		for name in ("tabBuffi", "tabPet", "tabRide"):   # index order MUST match PAGE_BUFFI / PAGE_PET / PAGE_RIDE
			self.tabButtons.append(self.GetChild2(name))
		if self.tabButtons[PAGE_BUFFI]:
			self.tabButtons[PAGE_BUFFI].SAFE_SetEvent(self.__OnClickPageTab, PAGE_BUFFI)
			self.tabButtons[PAGE_BUFFI].Down()
		if self.tabButtons[PAGE_PET]:
			self.tabButtons[PAGE_PET].SAFE_SetEvent(self.__OnClickPageTab, PAGE_PET)
		self.rideTabAvailable = hasattr(net, "SendGrowthMountPacket")
		if self.tabButtons[PAGE_RIDE]:
			if self.rideTabAvailable:
				self.tabButtons[PAGE_RIDE].SAFE_SetEvent(self.__OnClickPageTab, PAGE_RIDE)
			else:
				self.tabButtons[PAGE_RIDE].Hide()   # flag-off client: no packet layer, keep the tab unreachable

		# Start hidden: until a status arrives we show only the background + notice.
		self.__ApplyEmptyState(0)

	# ------------------------------------------------------------------
	# Events (stubs filled in by later increments)
	# ------------------------------------------------------------------
	def __OnClickEvolve(self):
		# Open the "Upgrade Type" sub-window, handing it the buffi's live stage + pity counter
		# (set from the last status push). It reads the target-stage requirements itself.
		if self.interface:
			self.interface.OpenCompanionUpgrade(self.buffiStage, self.evolveFail)

	def __OnClickHelp(self):
		# Open the buffi-system explainer popup (interface owns the window, like the Upgrade dialog).
		if self.interface and hasattr(self.interface, "OpenCompanionHelp"):
			self.interface.OpenCompanionHelp()

	def __OnClickPetUpgrade(self):
		# Open the pet Upgrade sub-window (Evolve | Upgrade Type tabs; interface owns it).
		if self.interface and hasattr(self.interface, "OpenPetUpgrade"):
			self.interface.OpenPetUpgrade()

	def __OnClickPetSkillPlus(self, slot):
		# Open the no-fail skill-upgrade dialog for this slot (interface owns the window).
		if self.interface and hasattr(self.interface, "OpenPetSkillUpgrade"):
			self.interface.OpenPetSkillUpgrade(slot)

	def __OnClickPetFeed(self):
		# Open the feed window (Experience | Duration rail tabs). It re-hosts the legacy
		# 9-slot staging machine -- inventory locking, item validation, attr warnings all
		# reused -- and shows the inventory alongside.
		if self.interface and hasattr(self.interface, "OpenPetFeed"):
			self.interface.OpenPetFeed()

	def __OnClickPetHelp(self):
		# General pet help (lifetime / feedstuff / potions). Mode ints match
		# uipethelp.MODE_GENERAL / MODE_EXP -- passed raw because uipethelp
		# imports this module (the potion table), so importing it back here
		# would be a circular import.
		if self.interface and hasattr(self.interface, "OpenPetHelp"):
			self.interface.OpenPetHelp(0)

	def __OnClickPetExpHelp(self):
		# The leveling-journey help (the "?" beside the EXP header).
		if self.interface and hasattr(self.interface, "OpenPetHelp"):
			self.interface.OpenPetHelp(1)

	def __OnClickRideExpHelp(self):
		# Ride-page leveling help. Mode ints match uicompanionridehelp.MODE_LEVEL/MODE_SKILL
		# (raw, the pet-help idiom).
		if self.interface and hasattr(self.interface, "OpenCompanionRideHelp"):
			self.interface.OpenCompanionRideHelp(0)

	def __OnClickRideSkillHelp(self):
		if self.interface and hasattr(self.interface, "OpenCompanionRideHelp"):
			self.interface.OpenCompanionRideHelp(1)

	def __OnClickRideUpgrade(self):
		# Opens the level-up dialog directly (no interfacemodule wiring for the ride sub-dialogs).
		if not self.rideStatus:
			return
		(active, level, exp, reqExp, gold, upMats, skillLevels, skillFails, skillChances, skillMats) = self.rideStatus
		if not active:
			return   # stale render guard; the button is hidden while the mount isn't called
		if self.rideUpgradeDlg:
			self.rideUpgradeDlg.Open(level, gold, upMats)

	def __OnClickRideSkillPlus(self, idx):
		if not self.rideStatus:
			return
		(active, level, exp, reqExp, gold, upMats, skillLevels, skillFails, skillChances, skillMats) = self.rideStatus
		if not active:
			return   # stale render guard; the "+" is hidden while the mount isn't called
		if idx < 0 or idx >= len(skillLevels):
			return
		if level < uicompanionride.RIDE_SKILL_UNLOCK_LEVEL[idx]:
			return   # stale render guard; the "+" is hidden while locked
		if idx > 0 and skillLevels[idx - 1] < 1:
			return   # stale render guard; chain-locked, the "+" is hidden
		mats = skillMats[idx] if idx < len(skillMats) else []
		if self.rideSkillDlg:
			self.rideSkillDlg.Open(idx, skillLevels[idx], skillFails[idx], skillChances[idx], mats)

	# ------------------------------------------------------------------
	# Stat-row potion slots (U6). Click (or drop a potion stack on the row)
	# -> "apply how many?" quantity dialog -> net.SendPetStatPotion(cell, n).
	# The server is the authority: it re-clamps the count to the stack AND to
	# the cap, applies in ONE point change, consumes only what was applied,
	# and chats every rejection (revive first / at Type max / larger potion)
	# -- so the client only needs an honest maximum and a valid cell.
	# ------------------------------------------------------------------
	def __FindPetPotionStack(self, vnum):
		# Largest stack wins: the CG packet applies from ONE stack, so the
		# biggest stack gives the dialog the highest honest maximum.
		bestCell = -1
		bestCount = 0
		for cellPos in xrange(player.INVENTORY_PAGE_SIZE * player.INVENTORY_PAGE_COUNT):
			if player.GetItemIndex(cellPos) != vnum:
				continue
			cnt = player.GetItemCount(cellPos)
			if cnt > bestCount:
				bestCell = cellPos
				bestCount = cnt
		return (bestCell, bestCount)

	def __OnClickPetStatPotion(self, statIdx):
		if statIdx < 0 or statIdx >= len(self.petStatPotionVnums):
			return
		vnum = self.petStatPotionVnums[statIdx]
		if not vnum or not hasattr(net, "SendPetStatPotion"):
			return
		if 0 == player.GetActivePetItemId():
			return
		# Drop flow: a potion stack dragged onto its row targets THAT stack;
		# any other attached item is just detached (no accidental sends).
		cell = -1
		count = 0
		if mousemodule.mouseController.isAttached():
			attachedType = mousemodule.mouseController.GetAttachedType()
			attachedCell = mousemodule.mouseController.GetAttachedSlotNumber()
			mousemodule.mouseController.DeattachObject()
			if attachedType != player.SLOT_TYPE_INVENTORY:
				return
			if player.GetItemIndex(attachedCell) != vnum:
				return
			cell = attachedCell
			count = player.GetItemCount(attachedCell)
		else:
			(cell, count) = self.__FindPetPotionStack(vnum)
		if cell < 0 or count <= 0:
			item.SelectItem(vnum)
			chat.AppendChat(chat.CHAT_TYPE_INFO,
				getattr(localeinfo, "COMPANION_PET_POTION_NONE", "You don't have any %s.") % item.GetItemName())
			return
		# NO count==1 shortcut: the dialog doubles as the confirmation (user feedback
		# 2026-07-05 -- a stray click on the row must never consume a potion directly).
		if not self.petPotionPickDlg:
			dlg = uicommon.PickItemDialog()
			dlg.SetAcceptEvent(ui.__mem_func__(self.__OnAcceptPetStatPotion))
			# The shared dialog ships an item-SPLIT section (USE_AUTO_SPLIT_ITEMS build):
			# meaningless -- and misleading -- for "apply N potions" (user feedback
			# 2026-07-05). This instance is private, so hide the split widgets and
			# compact the board back to the no-split layout (buttons at y58, h 90 --
			# the uiscript's own non-split constants). Only Y moves: X is kept from
			# the live widgets, so the RTL-mirrored layout stays intact.
			if dlg.GetChild2("split_thinboard_ui"):
				for wName in ("split_thinboard_ui", "split_text_ui", "split_button_ui"):
					w = dlg.GetChild2(wName)
					if w:
						w.Hide()
				for btn in (dlg.accept_button, dlg.close_button):
					(bx, by) = btn.GetLocalPosition()
					btn.SetPosition(bx, 58)
				dlg.board.SetSize(dlg.GetWidth(), 90)
				dlg.SetSize(dlg.GetWidth(), 90)
				dlg.height = 90   # Open() places the dialog above the mouse by self.height
			self.petPotionPickDlg = dlg
		item.SelectItem(vnum)
		self.petPotionPickDlg.SetTitleName(item.GetItemName())
		self.petPotionPickVnum = vnum
		self.petPotionPickDlg.SetMax(count)
		self.petPotionPickDlg.Open(cell, count)   # slot_index rides back into Accept as the cell

	def __OnAcceptPetStatPotion(self, cell, count, split = False):
		# PickItemDialog always passes 3 args (the split flag is meaningless here).
		# Stale-cell guard: the inventory may have shifted while the dialog was open,
		# and the potion's Value0 decides the stat SERVER-side -- a swapped stack at
		# this cell would be legitimately consumed for the wrong stat.
		if count <= 0:
			return
		if player.GetItemIndex(cell) != self.petPotionPickVnum:
			return
		net.SendPetStatPotion(cell, int(count))

	def __OnPetStatPotionOverIn(self, slotIndex):
		# Plain item tooltip for the ADVERTISED potion (proto preview, like the
		# upgrade-window material slots) -- tells the player what to go get.
		if slotIndex < 0 or slotIndex >= len(self.petStatPotionVnums):
			return
		vnum = self.petStatPotionVnums[slotIndex]
		if not vnum:
			return
		if not self.petPotionToolTip:
			self.petPotionToolTip = uitooltip.ItemToolTip()
		self.petPotionToolTip.ClearToolTip()
		self.petPotionToolTip.SetItemToolTip(vnum)

	def __OnPetStatPotionOverOut(self):
		if self.petPotionToolTip:
			self.petPotionToolTip.HideToolTip()

	def __OnPetSkillOverIn(self, slotIndex):
		petID = player.GetActivePetItemId()
		if 0 == petID:
			return
		tip = getattr(self.interface, "tooltipPetSkill", None) if self.interface else None
		if tip:
			tip.SetPetSkill(petID, slotIndex, slotIndex)   # builds + shows itself; empty slot = no-op

	def __OnPetSkillOverOut(self):
		tip = getattr(self.interface, "tooltipPetSkill", None) if self.interface else None
		if tip:
			tip.HideToolTip()

	def __GetAttachedPetBook(self):
		# Shared drop preamble: detach the mouse item and return (cell, subType) when it is a
		# MAIN-INVENTORY ITEM_TYPE_PET item (pet books never sort into special inventories),
		# else None. Leaves the item selected for item.GetItemName().
		if not mousemodule.mouseController.isAttached():
			return None
		attachedType = mousemodule.mouseController.GetAttachedType()
		attachedCell = mousemodule.mouseController.GetAttachedSlotNumber()
		mousemodule.mouseController.DeattachObject()
		if attachedType != player.SLOT_TYPE_INVENTORY:
			return None
		itemVnum = player.GetItemIndex(attachedCell)
		if not itemVnum:
			return None
		item.SelectItem(itemVnum)
		if item.GetItemType() != item.ITEM_TYPE_PET:
			return None
		return (attachedCell, item.GetItemSubType())

	def __OnPetSkillEmptySlotDrop(self, slotIndex):
		# Skill book dropped on an EMPTY slot -> learn (1 book, per the rework design).
		# Server re-validates everything (lock, emptiness, book at the cell).
		petID = player.GetActivePetItemId()
		if 0 == petID:
			return
		dropped = self.__GetAttachedPetBook()
		if not dropped:
			return
		(bookCell, bookSubType) = dropped
		if slotIndex < 0 or slotIndex >= PET_SKILL_SLOT_COUNT:
			return
		if bookSubType == item.PET_SKILL_DEL_BOOK:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_EMPTY_SKILL_SLOT_USE_ITEM)
			return
		if bookSubType != item.PET_SKILL:
			return
		# Level gate mirror (slots 0-2 @ lv90, 3-5 @ lv105) so the refusal is instant + named.
		(petLevel, evolLevel, birthday, petNick, s0, s1, s2) = player.GetPetItem(petID)
		open1 = getattr(player, "PET_GROWTH_SKILL_OPEN_LEVEL_1", 90)
		open2 = getattr(player, "PET_GROWTH_SKILL_OPEN_LEVEL_2", 105)
		tier1 = getattr(player, "PET_GROWTH_SKILL_SLOT_TIER1_COUNT", 3)
		needLevel = open1 if slotIndex < tier1 else open2
		if petLevel < needLevel:
			fmt = getattr(localeinfo, "COMPANION_PET_SKILL_SLOT_LOCKED", "This skill slot unlocks at pet level %s.")
			chat.AppendChat(chat.CHAT_TYPE_INFO, fmt % needLevel)
			return
		if hasattr(player, "GetPetSkillByIndex") and player.GetPetSkillByIndex(petID, slotIndex)[0]:
			return   # occupied after all (stale render); the filled-slot flow owns it
		self.petSkillBookSlot = slotIndex
		self.petSkillBookCell = bookCell
		self.__AskPetSkillQuestion(
			localeinfo.PET_SKILL_LEARN_QUESTION_DLG_MSG % (item.GetItemName()),
			ui.__mem_func__(self.__OnConfirmLearnSkill))

	def __OnPetSkillFilledSlotDrop(self, slotIndex):
		# Deletion book dropped on a FILLED slot -> forget that skill (frees the slot).
		# A learn book on a filled slot does nothing -- free the slot first.
		petID = player.GetActivePetItemId()
		if 0 == petID:
			return
		dropped = self.__GetAttachedPetBook()
		if not dropped:
			return
		(bookCell, bookSubType) = dropped
		if slotIndex < 0 or slotIndex >= PET_SKILL_SLOT_COUNT:
			return
		if bookSubType != item.PET_SKILL_DEL_BOOK:
			return
		if hasattr(player, "GetPetSkillByIndex") and not player.GetPetSkillByIndex(petID, slotIndex)[0]:
			return
		self.petSkillDelSlot = slotIndex
		self.petSkillDelCell = bookCell
		self.__AskPetSkillQuestion(
			localeinfo.PET_SKILL_DELETE_QUESTION_DLG_MSG1,
			ui.__mem_func__(self.__OnConfirmDeleteSkill))

	def __AskPetSkillQuestion(self, text, acceptFunc):
		if not self.petSkillQuestionDlg:
			dlg = uicommon.QuestionDialog()
			dlg.SetCancelEvent(ui.__mem_func__(self.__OnCancelPetSkillQuestion))
			self.petSkillQuestionDlg = dlg
		self.petSkillQuestionDlg.SetText(text)
		self.petSkillQuestionDlg.SetAcceptEvent(acceptFunc)
		self.petSkillQuestionDlg.SetTop()
		self.petSkillQuestionDlg.Open()

	def __OnCancelPetSkillQuestion(self):
		self.petSkillBookSlot = -1
		self.petSkillBookCell = -1
		self.petSkillDelSlot  = -1
		self.petSkillDelCell  = -1
		if self.petSkillQuestionDlg:
			self.petSkillQuestionDlg.Close()
		return True

	def __OnConfirmLearnSkill(self):
		slot, cell = self.petSkillBookSlot, self.petSkillBookCell
		self.__OnCancelPetSkillQuestion()   # close + reset pending state
		if slot >= 0 and cell >= 0 and player.GetActivePetItemId() and hasattr(net, "SendPetLearnSkill"):
			net.SendPetLearnSkill(slot, cell)   # server learns + pushes fresh info -> page refresh
		return True

	def __OnConfirmDeleteSkill(self):
		slot, cell = self.petSkillDelSlot, self.petSkillDelCell
		self.__OnCancelPetSkillQuestion()
		if slot >= 0 and cell >= 0 and player.GetActivePetItemId() and hasattr(net, "SendPetDeleteSkill"):
			net.SendPetDeleteSkill(slot, cell)
		return True

	def __OnClickPageTab(self, page):
		self.__SetPage(page)

	def __SetPage(self, page):
		# Switch the window between the buffi page and the pet placeholder page. Tab pressed-state
		# is kept in sync (radio buttons only auto-Down the clicked one), page-crossing popups are
		# dismissed, and __ApplyEmptyState re-resolves all widget visibility for the new page.
		if page == PAGE_RIDE and not self.rideTabAvailable:
			page = PAGE_BUFFI   # flag-off client: ride tab is hidden/unreachable, land on buffi instead
		self.currentPage = page
		for i in range(len(self.tabButtons)):
			btn = self.tabButtons[i]
			if not btn:
				continue
			if i == page:
				btn.Down()
			else:
				btn.SetUp()
		if self.expToolTip:
			self.expToolTip.HideToolTip()
		if self.oreToolTip:
			self.oreToolTip.HideToolTip()
		if self.nameToolTip:
			self.nameToolTip.HideToolTip()
		if self.durationConfirmDlg:
			self.durationConfirmDlg.Close()
		if self.petExpToolTip:
			self.petExpToolTip.HideToolTip()
		if self.petPotionToolTip:
			self.petPotionToolTip.HideToolTip()
		if self.petLockToolTip:
			self.petLockToolTip.HideToolTip()   # OnUpdate hover stops on the buffi page
		self.petLockHoverIdx = -1
		if self.petPotionPickDlg:
			self.petPotionPickDlg.Close()   # quantity dialog dies with the page
		tipPetSkill = getattr(self.interface, "tooltipPetSkill", None) if self.interface else None
		if tipPetSkill:
			tipPetSkill.HideToolTip()   # page switched mid skill-hover
		tipSkill = getattr(self.interface, "tooltipSkill", None) if self.interface else None
		if tipSkill:
			tipSkill.HideToolTip()      # same for the shared buffi/job skill tooltip
		self.__OnCancelPetSkillQuestion()   # pending learn/delete confirm dies with the page
		if self.rideUpgradeDlg:
			self.rideUpgradeDlg.Close()   # ride sub-dialogs die with the page, like the pet ones
		if self.rideSkillDlg:
			self.rideSkillDlg.Close()
		if self.rideExpToolTip:
			self.rideExpToolTip.HideToolTip()   # page switched mid EXP-hover
		if self.rideSkillToolTip:
			self.rideSkillToolTip.HideToolTip()   # page switched mid skill-hover
		if self.ridePortraitToolTip:
			self.ridePortraitToolTip.HideToolTip()   # page switched mid portrait-hover
		if self.rideUpgradeButton:
			self.rideUpgradeButton.DisableHoverPulse()   # page switched away -- pulse must not keep ticking off-screen
		self.__ApplyEmptyState(self.summonedNow)
		if page == PAGE_PET:
			self.RefreshPetPage()
		elif page == PAGE_RIDE:
			self.RefreshRidePage()

	def __OnClickDuration(self):
		# Click-to-consume a duration item -> CONFIRM first, then send on Accept only.
		# Why the confirm: this consumes a recharge/permanent item. A stray "ghost" click can fire this
		# handler when nothing was intended -- e.g. on login/warp the still-open window is re-centered and
		# the loading-screen mouse-up lands on this fixed-position button. Sending unconditionally then
		# either silently burns a recharge item the player owns, or (with none) spams the confusing
		# "You have no Buffi duration item to use" notice. Routing through a confirm dialog makes a ghost
		# click harmless (the player just cancels) and the consume deliberate.
		if not self.durationConfirmDlg:
			dlg = uicommon.QuestionDialog()
			dlg.SetAcceptEvent(ui.__mem_func__(self.__OnConfirmDuration))
			dlg.SetCancelEvent(ui.__mem_func__(self.__OnCancelDuration))
			self.durationConfirmDlg = dlg
		self.durationConfirmDlg.SetText(
			getattr(localeinfo, "COMPANION_DURATION_CONFIRM", "Consume a Buffi duration item to recharge it?"))
		self.durationConfirmDlg.Open()

	def __OnConfirmDuration(self):
		# Accept: close the dialog, then send. Server auto-finds the item (pos=0) and pushes fresh status.
		self.__OnCancelDuration()
		if hasattr(net, "SendBuffiPacket"):
			net.SendBuffiPacket(net.BUFFI_CG_RECHARGE, 0)
		return True

	def __OnCancelDuration(self):
		if self.durationConfirmDlg:
			self.durationConfirmDlg.Close()
		return True

	def __OnOreDropInsert(self, slotPos):
		# Drop an inventory item onto an empty ore slot -> ask the server to socket it. wPos = the dragged
		# item's INVENTORY cell (server picks the first free ore slot, validates Buffi-Ore, consumes one).
		if not mousemodule.mouseController.isAttached():
			return
		attachedType = mousemodule.mouseController.GetAttachedType()
		attachedPos  = mousemodule.mouseController.GetAttachedSlotNumber()
		mousemodule.mouseController.DeattachObject()
		if attachedType == player.SLOT_TYPE_INVENTORY and hasattr(net, "SendBuffiPacket"):
			net.SendBuffiPacket(net.BUFFI_CG_INSERT_ORE, attachedPos)

	# >>> SECTION BEGIN: ore removal disabled -- ores are consumed-on-socket + auto-expire (non-removable).
	# Handler kept (no longer wired) so the pop-back-to-inventory behavior can be revived without archaeology.
	def __OnOreSlotUse(self, slotPos):
		# Use / pick a filled ore slot -> server pops that ore back to inventory. wPos = ore slot index 0..2.
		mousemodule.mouseController.DeattachObject()
		if hasattr(net, "SendBuffiPacket"):
			net.SendBuffiPacket(net.BUFFI_CG_REMOVE_ORE, slotPos)
	# <<< SECTION END

	def __OnOreOverIn(self, slotIndex):
		# Hover a socketed ore -> show its name, INT bonus and remaining real-time lifetime.
		if slotIndex < 0 or slotIndex >= len(self.oreVnums):
			return
		vnum = self.oreVnums[slotIndex]
		if not vnum:
			return
		if not self.oreToolTip:
			self.oreToolTip = uitooltip.ToolTip()
		tip = self.oreToolTip
		tip.ClearToolTip()
		# Ore name (from item proto) as the title.
		item.SelectItem(vnum)
		oreName = item.GetItemName()
		if oreName:
			tip.AppendTextLine(oreName, 0xFFffd200)
		# INT bonus = proto value0, capped per slot.
		intBonus = item.GetValue(0)
		if intBonus > BUFFI_ORE_INT_EACH:
			intBonus = BUFFI_ORE_INT_EACH
		if intBonus < 0:
			intBonus = 0
		tip.AppendTextLine(localeinfo.COMPANION_ORE_INT_FMT % intBonus, 0xFF42e5f4)
		# Remaining wall-clock lifetime (server-synced clock); same tiered format as the duration gauge.
		expireAt = self.oreExpire[slotIndex]
		if expireAt:
			remain = expireAt - app.GetGlobalTimeStamp()
			if remain <= 0:
				tip.AppendTextLine(localeinfo.COMPANION_DURATION_EXPIRED, 0xFFff6666)
			else:
				tip.AppendTextLine(localeinfo.COMPANION_ORE_DURATION_FMT % self.__FormatRemain(remain), 0xFFcabdab)
		tip.ShowToolTip()

	def __OnOreOverOut(self):
		if self.oreToolTip:
			self.oreToolTip.HideToolTip()

	def __OnOverInExp(self):
		if not self.expToolTip:
			self.expToolTip = uitooltip.ToolTip()
		tip = self.expToolTip
		tip.ClearToolTip()
		if not self.hasBuffi:
			tip.AppendTextLine("-")
		elif self.expIsMax:
			tip.AppendTextLine(localeinfo.COMPANION_EXP_MAX)
		else:
			pct = 0
			if self.expNext > 0:
				pct = (self.expCur * 100) // self.expNext
			tip.AppendTextLine(localeinfo.COMPANION_EXP_TIP_FMT % (self.expCur, pct, self.expNext))
		tip.ShowToolTip()

	def __OnOverOutExp(self):
		if self.expToolTip:
			self.expToolTip.HideToolTip()

	def __OnOverInName(self, *args):
		# Nickname tooltip: remaining time + what the name grants (boss damage + the 2 unlocked buffs).
		if not self.nameToolTip:
			self.nameToolTip = uitooltip.ToolTip()
		tip = self.nameToolTip
		tip.ClearToolTip()
		if not self.isNamed:
			tip.AppendTextLine(getattr(localeinfo, "COMPANION_NAME_TIP_NONE", "Not named - use a name scroll."), 0xFFc7c7c7)
			tip.ShowToolTip()
			return
		tip.AppendTextLine(getattr(localeinfo, "COMPANION_NAME_TIP_ACTIVE", "Nickname active"), 0xFFffd200)
		# Remaining time (permanent sentinel -> "Permanent"; else the tiered d/h or h/m format).
		if self.nameExpire == BUFFI_DURATION_PERMANENT:
			left = localeinfo.COMPANION_DURATION_PERMANENT
		else:
			remain = self.nameExpire - app.GetGlobalTimeStamp()
			left = self.__FormatRemain(remain) if remain > 0 else localeinfo.COMPANION_DURATION_EXPIRED
		tip.AppendTextLine(getattr(localeinfo, "COMPANION_NAME_TIP_LEFT", "Time left: %s") % left, 0xFFcabdab)
		if self.bossPct > 0:
			tip.AppendTextLine(getattr(localeinfo, "COMPANION_NAME_TIP_BOSS", "+%d%% boss damage") % self.bossPct, 0xFF8fe18f)
		tip.AppendTextLine(getattr(localeinfo, "COMPANION_NAME_TIP_UNLOCK", "Unlocks: Speed + Attack"), 0xFF8fe18f)
		tip.ShowToolTip()

	def __OnOverOutName(self):
		if self.nameToolTip:
			self.nameToolTip.HideToolTip()

	def __ApplyEmptyState(self, summoned):
		# Page-aware visibility resolver.
		# Buffi page: when NO buffi is summoned, hide ALL buffi content (every named widget, so
		# future additions are covered automatically) and show only the chrome + the centered
		# notice; when summoned, show everything. A parked (dismissed-but-exists) buffi therefore
		# never shows stale exp/ore/etc.
		# Pet page: hide ALL buffi content (incl. the notice and the buffi "?" help) and show the
		# petPage container instead. The chrome + tab rail stay visible on both pages.
		# Pet-page widgets (names starting with "pet", declared inside the petPage container) are
		# NEVER touched by the buffi toggle -- their visibility belongs to the pet controller.
		# Ride page: same treatment as the pet page (names starting with "ride", inside ridePage;
		# visibility owned by RefreshRidePage / this method's ridePage Show/Hide block below).
		onPet  = (self.currentPage == PAGE_PET)
		onRide = (self.currentPage == PAGE_RIDE)
		onBuffiPage = not onPet and not onRide
		showBuffi = summoned and onBuffiPage
		keep = ("board", "background", "content", "emptyText", "helpButton", "tabBuffi", "tabPet", "tabRide")
		# Premium lock overlays are STATE-managed, not just summon-managed: visible only while the
		# buffi is unnamed (self.isNamed is cached before this runs). Handled here -- the single
		# owner of their visibility -- so a page switch can never blanket-Show them over a named
		# buffi (the reported visual bug) and a status push can never draw them over the pet page.
		lockNames = ("buffiSkillLock2", "buffiSkillLock3")
		for childName, child in self.ElementDictionary.items():
			if childName in keep:
				continue
			if childName.startswith("pet"):
				continue
			if childName.startswith("ride"):
				continue
			if childName in lockNames:
				if showBuffi and not self.isNamed:
					child.Show()
				else:
					child.Hide()
				continue
			if showBuffi:
				child.Show()
			else:
				child.Hide()
		# Code-created buffi children (not in ElementDictionary) ride the same toggle.
		if self.portraitRender:
			if showBuffi:
				self.portraitRender.Show()
			else:
				self.portraitRender.Hide()
		if self.bonusScrollBoard:
			if showBuffi:
				self.bonusScrollBoard.Show()
			else:
				self.bonusScrollBoard.Hide()
		# The "no buffi" notice and the titlebar "?" belong to the buffi page (the ride
		# page carries its own contextual "?"s beside the EXP and Skills sections).
		if self.emptyText:
			if summoned or not onBuffiPage:
				self.emptyText.Hide()
			else:
				self.emptyText.Show()
		if self.btnHelp:
			if onBuffiPage:
				self.btnHelp.Show()
			else:
				self.btnHelp.Hide()
		# The pet-page "?" is the exact inverse (same titlebar spot, one at a time).
		if self.btnPetHelp:
			if onPet:
				self.btnPetHelp.Show()
			else:
				self.btnPetHelp.Hide()
		if self.petPage:
			if onPet:
				self.petPage.Show()
			else:
				self.petPage.Hide()
		if self.ridePage:
			if onRide:
				self.ridePage.Show()
			else:
				self.ridePage.Hide()

	# ------------------------------------------------------------------
	# Network-driven refresh (binding point for BINARY_OnBuffiStatus)
	# ------------------------------------------------------------------
	def RefreshFromStatus(self, summoned, stage, level, intVal, exp, expToNext,
	                      expireAt, ore0, ore1, ore2, oreExp0, oreExp1, oreExp2, bossPct, nameExpire, name, evolveFail=0):
		if not self.board:
			return
		# Hide/show all content based on summon state (parked buffi shows the empty notice, not stale data).
		self.summonedNow = summoned
		self.buffiStage  = stage        # current evolution stage 0..3 (drives the Upgrade window)
		self.evolveFail  = evolveFail   # pity counter (consecutive fails); shown as "N / BUFFI_EVOL_PITY"
		# Nickname status MUST be cached BEFORE __ApplyEmptyState: it owns the premium lock overlays'
		# visibility (locks shown only while unnamed) and reads self.isNamed. Caching it after (the old
		# order) left the locks stale on the page-switch path. Also feeds the name-row hover tooltip.
		self.nameExpire = nameExpire
		self.bossPct    = bossPct
		self.isNamed    = (nameExpire != 0) and (nameExpire == BUFFI_DURATION_PERMANENT or nameExpire > app.GetGlobalTimeStamp())
		self.__ApplyEmptyState(summoned)
		if not summoned:
			self.durationExpireAt = 0   # stop the live countdown tick while unsummoned
			return
		self.expCur   = exp
		self.expNext  = expToNext
		self.hasBuffi = (summoned != 0) or (expireAt != 0)
		self.expIsMax = self.hasBuffi and (expToNext <= 0)
		if summoned:
			# Active companion -> show its live name / level / INT. A fresh buffi is
			# level 1 / INT 120 with no custom name; fall back to the default name.
			self.detailValues["name"].SetText(name or localeinfo.COMPANION_DEFAULT_NAME)
			self.detailValues["level"].SetText(str(level))
			self.detailValues["int"].SetText(str(intVal))
		else:
			# No active companion (dismissed / none) -> clear the live fields so the
			# panel visibly reflects the summon state instead of looking static.
			self.detailValues["name"].SetText("-")
			self.detailValues["level"].SetText("-")
			self.detailValues["int"].SetText("-")
		# EXP balls: each orb fills SMOOTHLY (vertical, bottom-up) instead of snapping full at each 25%.
		# Mirrors the taskbar EXP orbs (uitaskbar.SetExperience): the fill layer (progress.png) is clipped
		# per-orb via SetRenderingRect(0.0, ratio-1.0, 0.0, 0.0) -- ratio 0 -> fully clipped (the static
		# progress_empty.png orb behind shows through), ratio 1 -> no clip (full orb). Total level progress
		# is spread across the 4 orbs, so orb i shows the fraction of the [i/4 .. (i+1)/4] band.
		progress = 0.0
		if self.hasBuffi:
			if self.expIsMax:
				progress = 1.0
			elif self.expNext > 0:
				progress = float(self.expCur) / float(self.expNext)
				if progress < 0.0:
					progress = 0.0
				elif progress > 1.0:
					progress = 1.0
		for i in range(len(self.expBalls)):
			ballRatio = progress * 4.0 - i      # how full orb i is, before clamping to [0..1]
			if ballRatio < 0.0:
				ballRatio = 0.0
			elif ballRatio > 1.0:
				ballRatio = 1.0
			self.expBalls[i].SetRenderingRect(0.0, ballRatio - 1.0, 0.0, 0.0)
		# (Nickname status is cached at the top of this method, before __ApplyEmptyState.)
		# Duration gauge + remaining-time text, and the 3 ore slots (second section).
		self.__RefreshDuration(expireAt)
		self.__RefreshOres((ore0, ore1, ore2), (oreExp0, oreExp1, oreExp2))
		# Third section: skill icons + the exact bonus each buff gives (premium skills gated by the name).
		self.__RefreshSkillsSection(intVal, nameExpire)

	def __FormatRemain(self, remainSec):
		# Tiered remaining-time text used by EVERY duration display in this window:
		#   >= 1 day  -> days + hours
		#   <  1 day  -> hours + minutes
		if remainSec < 0:
			remainSec = 0
		if remainSec >= 86400:
			return localeinfo.COMPANION_DURATION_LEFT_FMT % (remainSec // 86400, (remainSec % 86400) // 3600)
		return localeinfo.COMPANION_DURATION_LEFT_MS_FMT % (remainSec // 3600, (remainSec % 3600) // 60)

	def __RefreshDuration(self, expireAt):
		# Gauge fills by remaining time vs the cap; text shows the tiered remaining time.
		# (Server-synced clock via app.GetGlobalTimeStamp so it matches the server's expire_at.)
		self.durationExpireAt = expireAt   # cached so OnUpdate can re-render the countdown each second
		ratio = 0.0
		text  = "-"
		if self.hasBuffi and expireAt != 0:
			if expireAt == BUFFI_DURATION_PERMANENT:
				ratio = 1.0
				text  = localeinfo.COMPANION_DURATION_PERMANENT
			else:
				remain = expireAt - app.GetGlobalTimeStamp()
				if remain <= 0:
					ratio = 0.0
					text  = localeinfo.COMPANION_DURATION_EXPIRED
				else:
					ratio = float(remain) / float(BUFFI_MAX_DURATION_SEC)
					if ratio > 1.0:
						ratio = 1.0
					text = self.__FormatRemain(remain)
		if self.durationGaugeFill:
			self.durationGaugeFill.SetRenderingRect(0.0, 0.0, -1.0 + ratio, 0.0)
		if self.durationText:
			self.durationText.SetText(text)

	def __RefreshOres(self, ores, oreExpires):
		# Show the socketed ore icon in each slot (0 = empty -> clear, the slot_runes bg shows through).
		# Stash the vnums + expiry so the hover tooltip can show +INT and the remaining real-time lifetime.
		self.oreVnums  = ores
		self.oreExpire = oreExpires
		if not self.oreSlotWindow:
			return
		for i in range(3):
			if ores[i]:
				self.oreSlotWindow.SetItemSlot(i, ores[i], 0)
			else:
				self.oreSlotWindow.ClearSlot(i)

	# ------------------------------------------------------------------
	# Third section: skill icons (+ "open reader") + the exact bonus each buff applies
	# ------------------------------------------------------------------
	def __OnClickSkillPlus(self):
		# All 4 buffi skills live on the same auto-skill-reader page (the buffi tab), so any "+" opens it.
		iface = getattr(self, "interface", None)
		if iface and hasattr(iface, "TryOpenAutoSkillReaderForBook"):
			iface.TryOpenAutoSkillReaderForBook(BUFFI_BOOK_VNUM)

	def __OnSkillOverIn(self, slotIndex):
		# Show the full skill tooltip for the hovered buffi skill (the tooltip applies the buffi INT
		# override itself for 163-166, so the values match the section). Mirrors uiautoskillreader.
		iface = getattr(self, "interface", None)
		if not iface or not getattr(iface, "tooltipSkill", None):
			return
		vnum  = BUFFI_SKILL_VNUM_START + slotIndex
		grade = player.GetSkillGradeNew(vnum)
		level = player.GetSkillLevelNew(vnum)
		# Pass the REGISTERED player-skill slot (130+i) as slotIndex: SetSkillNew uses it for the
		# efficiency lookup (GetSkillCurrentEfficientPercentage), and that's where the buffi skill's
		# efficiency is cached -- so the tooltip values match the bonus rows (which use the same slot).
		iface.tooltipSkill.SetSkillNew(BUFFI_SKILL_SLOT_START + slotIndex, vnum, grade, level)

	def __OnSkillOverOut(self):
		iface = getattr(self, "interface", None)
		if iface and getattr(iface, "tooltipSkill", None):
			iface.tooltipSkill.HideToolTip()

	def __ComputeSkillBonus(self, vnum, pct, suffix):
		# Primary affect value, computed exactly like the skill tooltip (INT override set by the caller).
		# Buffi skills are ACTIVE skills: their affect lives in the OLD AffectDataVector
		# (GetSkillAffectDescription), so the new-affect path is empty -> fall back like uitooltip does.
		try:
			if skill.GetNewAffectDataCount(vnum) > 0:
				affType, minV, maxV = skill.GetNewAffectData(vnum, 0, pct)
				return "%d%s" % (int(minV), suffix)
			if skill.GetSkillAffectDescriptionCount(vnum) > 0:
				desc = skill.GetSkillAffectDescription(vnum, 0, pct)
				if desc:
					return self.__ExtractValue(desc)   # full "<label> <value>" line -> just the value
		except:
			pass
		return "-"

	def __ExtractValue(self, s):
		# Old affect path returns a full localized "<label> <value>" line (no reliable ":" in every
		# locale). Pull out just the trailing numeric token (e.g. "35.6%", "+12.0%", "150") so the
		# cell shows the value, not the description (which already labels the row).
		allowed = "0123456789.+-%"
		end = len(s)
		while end > 0 and s[end - 1] in " \t":
			end -= 1
		start = end
		while start > 0 and s[start - 1] in allowed:
			start -= 1
		token = s[start:end].strip()
		return token if token else s.strip()

	def __BuildBonusList(self):
		# Scrollable bonus list: a clipped scrollBoard inside bonusViewport holding the 4 skill-bonus
		# rows + a boss-damage row. Each row = skill_value.png bg (scaled to BONUS_ROW_W) + a label +
		# a value cell, RTL-aware. The scrollbar moves the scrollBoard, so the list can grow freely.
		self.skillBonusText   = []
		self.bonusValueText   = []
		self.bonusWidgets     = []
		self.bossValueText    = None
		self.bonusScrollBoard = None
		vp = self.GetChild2("bonusViewport")
		self.bonusViewport = vp
		if not vp:
			return
		board = ui.Window()
		board.SetParent(vp)
		board.AddFlag("attach")
		board.AddFlag("not_pick")
		if app.USE_CLIP_MASK:
			board.SetClippingMaskWindow(vp)
		board.Show()
		self.bonusScrollBoard = board

		rtl = localeinfo.IsARABIC()
		labels = [
			localeinfo.COMPANION_BUFFI_SKILL0,
			localeinfo.COMPANION_BUFFI_SKILL1,
			localeinfo.COMPANION_BUFFI_SKILL2,
			localeinfo.COMPANION_BUFFI_SKILL3,
			getattr(localeinfo, "COMPANION_BUFFI_BOSS", "Boss damage"),
		]
		PAD = 10
		for i, label in enumerate(labels):
			y = i * BONUS_ROW_H
			bg = ui.ExpandedImageBox()
			bg.SetParent(board)
			bg.AddFlag("attach")
			bg.AddFlag("not_pick")
			bg.LoadImage(BUFFI_UI_PATH + "skill_value.png")
			bg.SetScale(float(BONUS_ROW_W) / 257.0, 1.0)
			bg.SetPosition(0, y)
			bg.Show()
			self.bonusWidgets.append(bg)
			cy = y + BONUS_IMG_H / 2
			lab = ui.TextLine()
			lab.SetParent(board)
			lab.AddFlag("attach")
			lab.AddFlag("not_pick")
			lab.SetOutline()
			lab.SetPackedFontColor(0xFFcabdab)
			lab.SetText(label)
			lab.SetVerticalAlignCenter()
			val = ui.TextLine()
			val.SetParent(board)
			val.AddFlag("attach")
			val.AddFlag("not_pick")
			val.SetOutline()
			val.SetPackedFontColor(0xFFd1b183)
			val.SetText("-")
			val.SetVerticalAlignCenter()
			if rtl:
				lab.SetHorizontalAlignLeft()
				lab.SetPosition(BONUS_ROW_W - PAD, cy)
				val.SetHorizontalAlignCenter()
				val.SetPosition(PAD + 18, cy)
			else:
				lab.SetHorizontalAlignLeft()
				lab.SetPosition(PAD, cy)
				val.SetHorizontalAlignRight()
				val.SetPosition(BONUS_ROW_W - PAD, cy)
			lab.Show()
			val.Show()
			self.bonusWidgets.append(lab)
			self.bonusWidgets.append(val)
			self.bonusValueText.append(val)
		# First 4 value cells feed the existing skill-bonus logic; the last is the boss-damage row.
		self.skillBonusText = self.bonusValueText[:BUFFI_SKILL_COUNT]
		self.bossValueText  = self.bonusValueText[BUFFI_SKILL_COUNT] if len(self.bonusValueText) > BUFFI_SKILL_COUNT else None

		self.bonusContentH = len(labels) * BONUS_ROW_H
		self.bonusViewH    = vp.GetHeight()
		board.SetSize(BONUS_ROW_W, self.bonusContentH)

		# Scrollbar: the uiscript-declared ui.ScrollBarNew (mirrors for RTL). Wire the scroll event;
		# show only when the content overflows the viewport.
		self.bonusScroll = self.GetChild2("bonusScroll")
		if self.bonusScroll:
			self.bonusScroll.SetScrollEvent(ui.__mem_func__(self.__OnBonusScroll))
			if self.bonusContentH > self.bonusViewH and self.bonusContentH > 0:
				self.bonusScroll.SetMiddleBarSize(float(self.bonusViewH) / float(self.bonusContentH))
				self.bonusScroll.SetPos(0.0)
				self.bonusScroll.Show()
			else:
				self.bonusScroll.Hide()

	def __OnBonusScroll(self):
		# Move the content window by the scrollbar fraction (0..1) -> top..bottom of the overflow.
		if not self.bonusScrollBoard or not self.bonusScroll:
			return
		maxScroll = self.bonusContentH - self.bonusViewH
		if maxScroll <= 0:
			self.bonusScrollBoard.SetPosition(0, 0)
			return
		self.bonusScrollBoard.SetPosition(0, -int(maxScroll * self.bonusScroll.GetPos()))

	def __RefreshSkillsSection(self, intVal, nameExpire):
		# "named" = the premium name-scroll window is active (permanent sentinel or a future expiry).
		isNamed = (nameExpire != 0) and (nameExpire == BUFFI_DURATION_PERMANENT or nameExpire > app.GetGlobalTimeStamp())

		# Skill icons (buffi skills need the grade-aware SetSkillSlotNew, not SetSkillSlot).
		if self.buffiSkillSlot:
			for i in range(BUFFI_SKILL_COUNT):
				vnum  = BUFFI_SKILL_VNUM_START + i
				player.SetSkill(BUFFI_SKILL_SLOT_START + i, vnum)
				grade = player.GetSkillGradeNew(vnum)
				level = player.GetSkillLevelNew(vnum)
				self.buffiSkillSlot.SetSkillSlotNew(i, vnum, grade, level)
				self.buffiSkillSlot.SetSlotCountNew(i, grade, level)
			self.buffiSkillSlot.RefreshSlot()

		# >>> SECTION BEGIN: lock toggling moved to __ApplyEmptyState (single owner). Toggling the
		# premium lock overlays here too caused the two-owner visual bug: a page switch blanket-
		# Show()ed them over a NAMED buffi, and a status push on the pet page Show()ed them over
		# the pet page. __ApplyEmptyState now resolves them from (page, summoned, self.isNamed).
		# for i, lock in self.skillLocks.items():
		# 	if lock:
		# 		(lock.Hide if isNamed else lock.Show)()
		# <<< SECTION END

		# Bonus values: exact, via the same INT-override affect path the tooltip uses.
		if app.__BUFFI_SUPPORT__:
			skill.SetBuffiIqOverride(intVal)
		for i in range(BUFFI_SKILL_COUNT):
			txt = self.skillBonusText[i] if i < len(self.skillBonusText) else None
			if not txt:
				continue
			if (i in BUFFI_PREMIUM_SKILLS) and not isNamed:
				txt.SetText("-")   # premium buff inactive until the buffi is named
				continue
			vnum   = BUFFI_SKILL_VNUM_START + i
			pct    = player.GetSkillCurrentEfficientPercentage(BUFFI_SKILL_SLOT_START + i)
			suffix = BUFFI_SKILL_SUFFIX[i] if i < len(BUFFI_SKILL_SUFFIX) else ""
			txt.SetText(self.__ComputeSkillBonus(vnum, pct, suffix))
		if app.__BUFFI_SUPPORT__:
			skill.SetBuffiIqOverride(-1)

		# Boss-damage row (granted by the nickname): show the % when named, else "-".
		if self.bossValueText:
			if self.isNamed and self.bossPct > 0:
				self.bossValueText.SetText("%d%%" % self.bossPct)
			else:
				self.bossValueText.SetText("-")

	# ------------------------------------------------------------------
	# Pet page controller (growth pet rework, U2 data binding).
	# Data sources: the SAME player getters the legacy pet window reads
	# (GetActivePetItemId / GetPetItem / GetPetLifeTime / GetPetExpPoints /
	# GetPetSkillByIndex) plus the rework Type push (GetPetTypeInfo, fed by
	# the GC pet-rework-info packet). Refresh triggers: page switch, Open,
	# interface.RefreshStatus (point deltas), and the GC push via
	# interface.RefreshCompanionPetPage.
	# ------------------------------------------------------------------
	def RefreshPetPage(self):
		# Cheap gate: only re-read everything while the pet page is actually visible.
		# Open() and the page switch both call this, so a hidden page can't go stale.
		if not self.isLoaded or not self.petPage:
			return
		if not self.IsShow() or self.currentPage != PAGE_PET:
			return
		petID = player.GetActivePetItemId()
		self.petHasPet = (petID != 0)
		if not petID:
			self.__ApplyPetEmptyState()
			return
		if self.petEmptyNotice:
			self.petEmptyNotice.Hide()
		# GetPetItem field order is (hp, def, sp) but the rework potions map
		# stat 0 -> HP, stat 1 -> SP (the Attack row), stat 2 -> DEF_GRADE (the
		# Elemental row) -- so def lands on row 2 and sp on row 1.
		(petLevel, evolLevel, birthday, petNick, statHp, statElem, statAtt) = player.GetPetItem(petID)
		if self.petIconSlot:
			self.petIconSlot.SetItemSlot(0, player.GetActivePetItemVNum(), 0)
		if self.petDetailValues.get("name"):
			self.petDetailValues["name"].SetText(petNick or "-")
		if self.petDetailValues.get("level"):
			self.petDetailValues["level"].SetText(str(petLevel))
		# Type row ("cur / max") + the Type stat-cap, from the rework info push.
		# Shows "-" until the first push lands (summon re-pushes, so this is brief).
		petType = 0
		typeMax = 0
		capPermille = 0
		if hasattr(player, "GetPetTypeInfo"):
			(petType, typeMax, _evoCeil, _fail, _pity, _chance, capPermille, _nextCap) = player.GetPetTypeInfo()
		if self.petDetailValues.get("type"):
			if petType:
				self.petDetailValues["type"].SetText("%d / %d" % (petType, typeMax))
			else:
				self.petDetailValues["type"].SetText("-")
		# EXP orbs: battle EXP spread across the 4 orbs with the same smooth per-orb
		# clip as the buffi page. Fed item EXP counts toward the same bar (it no
		# longer gates the level); the hover tooltip still splits the two numbers.
		(curEXP, nextEXP, itemEXP, itemMaxEXP) = player.GetPetExpPoints(petID)
		curEXP     = unsigned32(curEXP)
		nextEXP    = unsigned32(nextEXP)
		itemEXP    = unsigned32(itemEXP)
		itemMaxEXP = unsigned32(itemMaxEXP)
		self.petExpData = (curEXP, nextEXP, itemEXP, itemMaxEXP)
		progress = 0.0
		if nextEXP > 0:
			progress = float(curEXP + itemEXP) / float(nextEXP)
			if progress < 0.0:
				progress = 0.0
			elif progress > 1.0:
				progress = 1.0
		for i in range(len(self.petExpBalls)):
			ball = self.petExpBalls[i]
			if not ball:
				continue
			ballRatio = progress * 4.0 - i
			if ballRatio < 0.0:
				ballRatio = 0.0
			elif ballRatio > 1.0:
				ballRatio = 1.0
			ball.SetRenderingRect(0.0, ballRatio - 1.0, 0.0, 0.0)
		# Duration gauge + text (per-second live tick via OnUpdate).
		(endTime, maxTime) = player.GetPetLifeTime(petID)
		self.petDurationEnd = endTime
		self.petDurationMax = maxTime
		self.__RefreshPetDuration()
		# Stat rows: value text + fill-to-Type-cap bar + the potion the row still accepts.
		statPcts = (statHp, statAtt, statElem)   # row order: 0 Max HP, 1 Attack, 2 Elemental
		if capPermille <= 50:
			sizeClass = 0   # S potion covers the cap
		elif capPermille <= 100:
			sizeClass = 1   # M
		else:
			sizeClass = 2   # L
		for i in range(3):
			if i < len(self.petStatValues) and self.petStatValues[i]:
				self.petStatValues[i].SetText("+%0.1f%%" % statPcts[i])
			if i < len(self.petStatFills) and self.petStatFills[i]:
				ratio = 0.0
				if capPermille > 0:
					ratio = (statPcts[i] * 10.0) / float(capPermille)   # pct -> permille vs cap
					if ratio < 0.0:
						ratio = 0.0
					elif ratio > 1.0:
						ratio = 1.0
				self.petStatFills[i].SetRenderingRect(0.0, 0.0, -1.0 + ratio, 0.0)
			vnum = 0
			if petType:   # only advertise a potion once the Type info arrived
				vnum = PET_STAT_POTION_VNUMS[i][sizeClass]
			self.petStatPotionVnums[i] = vnum   # click/hover handlers read this
			if i < len(self.petStatIconSlots) and self.petStatIconSlots[i]:
				if vnum:
					self.petStatIconSlots[i].SetItemSlot(i, vnum, 0)   # slot index = row (uiscript)
				else:
					self.petStatIconSlots[i].ClearSlot(i)
		self.__RefreshPetSkills(petID, petLevel)

	def __ApplyPetEmptyState(self):
		# No pet summoned: clear every data cell, zero the fills, empty the slots,
		# show all 6 locks and the centered notice. Static chrome stays visible.
		self.petDurationEnd = 0
		self.petDurationMax = 0
		self.petExpData = (0, 0, 0, 0)
		for key in ("name", "type", "level"):
			if self.petDetailValues.get(key):
				self.petDetailValues[key].SetText("-")
		if self.petIconSlot:
			self.petIconSlot.ClearSlot(0)
		for ball in self.petExpBalls:
			if ball:
				ball.SetRenderingRect(0.0, -1.0, 0.0, 0.0)
		if self.petDurationGaugeFill:
			self.petDurationGaugeFill.SetRenderingRect(0.0, 0.0, -1.0, 0.0)
		if self.petDurationText:
			self.petDurationText.SetText("")
		for i in range(3):
			if i < len(self.petStatValues) and self.petStatValues[i]:
				self.petStatValues[i].SetText("")
			if i < len(self.petStatFills) and self.petStatFills[i]:
				self.petStatFills[i].SetRenderingRect(0.0, 0.0, -1.0, 0.0)
			if i < len(self.petStatIconSlots) and self.petStatIconSlots[i]:
				self.petStatIconSlots[i].ClearSlot(i)   # slot index = row (uiscript)
		self.petStatPotionVnums = [0, 0, 0]
		if self.petPotionToolTip:
			self.petPotionToolTip.HideToolTip()   # advertised potion vanished mid-hover
		if self.petPotionPickDlg:
			self.petPotionPickDlg.Close()         # pet dismissed with the quantity dialog open
		for i in range(PET_SKILL_SLOT_COUNT):
			if self.petSkillSlotWnd:
				self.petSkillSlotWnd.ClearSlot(i)
			if i < len(self.petSkillLocks) and self.petSkillLocks[i]:
				self.petSkillLocks[i].Show()
			if i < len(self.petSkillPluses) and self.petSkillPluses[i]:
				self.petSkillPluses[i].Hide()
		if self.petExpToolTip:
			self.petExpToolTip.HideToolTip()   # pet dismissed mid-hover: don't strand stale numbers
		tipPetSkill = getattr(self.interface, "tooltipPetSkill", None) if self.interface else None
		if tipPetSkill:
			tipPetSkill.HideToolTip()          # same strand class for the skill tooltip
		self.__OnCancelPetSkillQuestion()      # pet gone: a pending learn/delete confirm is void
		if self.petEmptyNotice:
			self.petEmptyNotice.Show()

	def __RefreshPetDuration(self):
		# Gauge fills by remaining lifetime vs THIS pet's max (per-pet, unlike the buffi's
		# fixed 30-day reference); text reuses the window's tiered remaining-time format.
		ratio = 0.0
		text  = "-"
		if self.petHasPet and self.petDurationEnd:
			remain = self.petDurationEnd - app.GetGlobalTimeStamp()
			if remain <= 0:
				ratio = 0.0
				text  = localeinfo.COMPANION_DURATION_EXPIRED
			else:
				if self.petDurationMax > 0:
					ratio = float(remain) / float(self.petDurationMax)
					if ratio > 1.0:
						ratio = 1.0
				text = self.__FormatRemain(remain)
		if self.petDurationGaugeFill:
			self.petDurationGaugeFill.SetRenderingRect(0.0, 0.0, -1.0 + ratio, 0.0)
		if self.petDurationText:
			self.petDurationText.SetText(text)

	def __RefreshPetSkills(self, petID, petLevel):
		# 6 slots: 0-2 unlock at pet lv90, 3-5 at lv105 (constants pushed by the client
		# binary; fall back to the shipped values if the exports are missing). Lock overlay
		# mirrors the server's RefreshSkillSlotLocks rule. Icons/levels come from
		# GetPetSkillByIndex -- the legacy GetPetSkill getter is 3-clamped and unusable here.
		open1 = getattr(player, "PET_GROWTH_SKILL_OPEN_LEVEL_1", 90)
		open2 = getattr(player, "PET_GROWTH_SKILL_OPEN_LEVEL_2", 105)
		tier1 = getattr(player, "PET_GROWTH_SKILL_SLOT_TIER1_COUNT", 3)
		maxLv = getattr(player, "PET_GROWTH_SKILL_LEVEL_MAX", 20)
		canRead = hasattr(player, "GetPetSkillByIndex")
		for i in range(PET_SKILL_SLOT_COUNT):
			if i < tier1:
				unlocked = (petLevel >= open1)
			else:
				unlocked = (petLevel >= open2)
			if i < len(self.petSkillLocks) and self.petSkillLocks[i]:
				if unlocked:
					self.petSkillLocks[i].Hide()
				else:
					self.petSkillLocks[i].Show()
			skillIdx = 0
			skillLv  = 0
			if unlocked and canRead:
				skillData = player.GetPetSkillByIndex(petID, i)
				skillIdx = skillData[0]
				skillLv  = skillData[1]
			if self.petSkillSlotWnd:
				if skillIdx:
					self.petSkillSlotWnd.SetPetSkillSlotNew(i, skillIdx)
					self.petSkillSlotWnd.SetSlotCount(i, skillLv)
				else:
					self.petSkillSlotWnd.ClearSlot(i)
			# "+" only where an upgrade is actually possible: learned skill below the ladder max.
			plus = self.petSkillPluses[i] if i < len(self.petSkillPluses) else None
			if plus:
				if skillIdx and skillLv < maxLv:
					plus.Show()
				else:
					plus.Hide()

	def __UpdatePetLockHover(self):
		# Show "unlocks at pet level N" while the mouse sits on a VISIBLE lock overlay.
		# Pure geometry against the live widget rects (RTL-safe: the user's mirrored
		# layout moved the locks, and these positions are read after that). State-keyed
		# on the hovered index so the tooltip is rebuilt/hidden only on transitions.
		idx = -1
		(mouseX, mouseY) = wndMgr.GetMousePosition()
		for i in range(len(self.petSkillLocks)):
			lock = self.petSkillLocks[i]
			if not lock or not lock.IsShow():
				continue
			(lockX, lockY) = lock.GetGlobalPosition()
			if lockX <= mouseX < lockX + lock.GetWidth() and lockY <= mouseY < lockY + lock.GetHeight():
				idx = i
				break
		if idx == self.petLockHoverIdx:
			return
		self.petLockHoverIdx = idx
		if idx < 0:
			if self.petLockToolTip:
				self.petLockToolTip.HideToolTip()
			return
		open1 = getattr(player, "PET_GROWTH_SKILL_OPEN_LEVEL_1", 90)
		open2 = getattr(player, "PET_GROWTH_SKILL_OPEN_LEVEL_2", 105)
		tier1 = getattr(player, "PET_GROWTH_SKILL_SLOT_TIER1_COUNT", 3)
		needLevel = open1 if idx < tier1 else open2
		if not self.petLockToolTip:
			self.petLockToolTip = uitooltip.ToolTip()
		tip = self.petLockToolTip
		tip.ClearToolTip()
		# Same key the book-drop refusal uses (%s-formatted, en+ae already shipped).
		fmt = getattr(localeinfo, "COMPANION_PET_SKILL_SLOT_LOCKED", "This skill slot unlocks at pet level %s.")
		tip.AutoAppendNewTextLineResize(fmt % needLevel)
		tip.ShowToolTip()

	def __OnOverInPetExp(self):
		if not self.petExpToolTip:
			self.petExpToolTip = uitooltip.ToolTip()
		tip = self.petExpToolTip
		tip.ClearToolTip()
		if not self.petHasPet:
			tip.AppendTextLine("-")
		else:
			(curEXP, nextEXP, itemEXP, itemMaxEXP) = self.petExpData
			# Legacy PET_INFO_EXP ships with a trailing colon in some locales -- strip it so the
			# uniform " : " separator doesn't double up. Arabic gets the value-first operand swap
			# the legacy pet window applies (RTL reading order).
			labelExp  = localeinfo.PET_INFO_EXP.rstrip(" :")
			labelItem = localeinfo.PET_INFO_ITEM_EXP.rstrip(" :")
			if localeinfo.IsARABIC():
				tip.AppendTextLine("%d / %d : %s" % (curEXP, nextEXP, labelExp))
				tip.AppendTextLine("%d / %d : %s" % (itemEXP, itemMaxEXP, labelItem))
			else:
				tip.AppendTextLine("%s : %d / %d" % (labelExp, curEXP, nextEXP))
				tip.AppendTextLine("%s : %d / %d" % (labelItem, itemEXP, itemMaxEXP))
		tip.ShowToolTip()

	def __OnOverOutPetExp(self):
		if self.petExpToolTip:
			self.petExpToolTip.HideToolTip()

	# ------------------------------------------------------------------
	# Ride page controller (growth mount rework, client Task 7).
	# Data source: self.rideStatus, cached verbatim from BINARY_OnGrowthMountStatus (Task 6, active
	# flag added Task 9): (active, level, exp, reqExp, gold, upMats, skillLevels, skillFails,
	# skillChances, skillMats). reqExp == 0 means max level; active == 0 means the mount isn't
	# summoned/ridden (__ApplyRideEmptyState hides content and shows the call-your-mount prompt).
	# Refresh triggers: page switch, Open, and every status push via OnGrowthMountStatus (only
	# takes effect while the ride page is actually visible).
	# ------------------------------------------------------------------
	def __RefreshRidePortrait(self):
		# Live equipped-mount icon: mount skin (if worn and not hidden) beats the costume, since
		# the skin is what actually renders on the ridden mount. Same accessor as the equipment
		# window's RefreshEquipSlotWindow/RefreshCostumeSlot (uiinventory.py) -- GetItemIndex at
		# EQUIPMENT_SLOT_START + the wear-slot constant. Falls back to the static glyph if neither
		# is worn.
		vnum = 0
		if app.USE_MOUNT_SKIN and not getattr(osfinfo, "HIDDEN_MOUNT_SKIN", 0):
			skinVnum = player.GetItemIndex(player.EQUIPMENT_SLOT_START + player.WEAR_MOUNT_SKIN)
			if skinVnum:
				vnum = skinVnum
		if not vnum:
			vnum = player.GetItemIndex(player.EQUIPMENT_SLOT_START + player.WEAR_COSTUME_MOUNT)
		self.ridePortraitVnum = vnum
		if vnum:
			if self.ridePortraitSlot:
				self.ridePortraitSlot.SetItemSlot(0, vnum, 0)
				self.ridePortraitSlot.RefreshSlot()
				self.ridePortraitSlot.Show()
			if self.ridePortraitIcon:
				self.ridePortraitIcon.Hide()
		else:
			if self.ridePortraitSlot:
				self.ridePortraitSlot.ClearSlot(0)
				self.ridePortraitSlot.Hide()
			if self.ridePortraitIcon:
				self.ridePortraitIcon.Show()

	def __OnRidePortraitOverIn(self, slotIndex):
		if not self.ridePortraitVnum:
			return
		if not self.ridePortraitToolTip:
			self.ridePortraitToolTip = uitooltip.ItemToolTip()
		self.ridePortraitToolTip.ClearToolTip()
		self.ridePortraitToolTip.SetItemToolTip(self.ridePortraitVnum)

	def __OnRidePortraitOverOut(self):
		if self.ridePortraitToolTip:
			self.ridePortraitToolTip.HideToolTip()

	def RefreshRidePage(self):
		if not self.isLoaded or not self.ridePage:
			return
		if not self.IsShow() or self.currentPage != PAGE_RIDE:
			return
		if self.rideStatus is None:
			if hasattr(net, "SendGrowthMountPacket"):
				net.SendGrowthMountPacket(net.GROWTH_MOUNT_CG_REQUEST_STATUS, 0)
			self.__ApplyRideEmptyState(False)   # no status yet -- render the empty state, not the stacked default
			return
		(active, level, exp, reqExp, gold, upMats, skillLevels, skillFails, skillChances, skillMats) = self.rideStatus
		if not active:
			self.__ApplyRideEmptyState(False)
			return
		self.__ApplyRideEmptyState(True)
		self.__RefreshRidePortrait()
		maxLevel = uicompanionride.RIDE_SKILL_UNLOCK_LEVEL[-1]
		unlockedCount = 0
		for unlockLevel in uicompanionride.RIDE_SKILL_UNLOCK_LEVEL:
			if level >= unlockLevel:
				unlockedCount += 1
		if self.rideDetailValues.get("name"):
			self.rideDetailValues["name"].SetText(getattr(localeinfo, "GROWTH_MOUNT_NAME", "Mount"))
		if self.rideDetailValues.get("level"):
			self.rideDetailValues["level"].SetText("%d / %d" % (level, maxLevel))
		if self.rideDetailValues.get("skills"):
			self.rideDetailValues["skills"].SetText("%d / %d" % (unlockedCount, uicompanionride.RIDE_SKILL_COUNT))
		# Gauge + orbs show the SAME level progress: gauge = one horizontal fill (the pet
		# lifetime-gauge idiom), orbs = the buffi per-orb smooth clip (orb i covers the
		# [i/4 .. (i+1)/4] band, fully lit once exp >= (i+1)*reqExp/4).
		isMax = (reqExp <= 0)
		progress = 0.0
		if isMax:
			progress = 1.0
		elif reqExp > 0:
			progress = float(exp) / float(reqExp)
			if progress < 0.0:
				progress = 0.0
			elif progress > 1.0:
				progress = 1.0
		if self.rideExpGaugeFill:
			self.rideExpGaugeFill.SetRenderingRect(0.0, 0.0, -1.0 + progress, 0.0)
		for i in range(len(self.rideExpBalls)):
			ball = self.rideExpBalls[i]
			if not ball:
				continue
			ballRatio = progress * 4.0 - i
			if ballRatio < 0.0:
				ballRatio = 0.0
			elif ballRatio > 1.0:
				ballRatio = 1.0
			ball.SetRenderingRect(0.0, ballRatio - 1.0, 0.0, 0.0)
		if self.rideExpText:
			if isMax:
				self.rideExpText.SetText(getattr(localeinfo, "COMPANION_EXP_MAX", "MAX"))
			else:
				self.rideExpText.SetText("%d / %d" % (exp, reqExp))
		if self.rideUpgradeButton:
			if (not isMax) and exp >= reqExp:
				self.rideUpgradeButton.Enable()
				self.rideUpgradeButton.EnableHoverPulse()
			else:
				self.rideUpgradeButton.Disable()
				self.rideUpgradeButton.DisableHoverPulse()
		self.__RefreshRideSkills(level, skillLevels)

	def __ApplyRideEmptyState(self, active):
		# Mount-called gate (Task 9): while the mount isn't summoned/ridden, hide every ride-page
		# content widget (every named widget starting with "ride", same idiom as __ApplyEmptyState's
		# buffi treatment) and the code-built bonus rows, and show only the centered prompt. The
		# ridePage container itself and the notice widget are the only two kept visible.
		if not active:
			if self.rideExpToolTip:
				self.rideExpToolTip.HideToolTip()   # mount dismissed mid EXP-hover
			if self.rideSkillToolTip:
				self.rideSkillToolTip.HideToolTip()   # mount dismissed mid skill-hover
			if self.ridePortraitToolTip:
				self.ridePortraitToolTip.HideToolTip()   # mount dismissed mid portrait-hover
		keep = ("ridePage", "rideEmptyText", "rideExpHelpButton", "rideSkillHelpButton")
		for childName, child in self.ElementDictionary.items():
			if not childName.startswith("ride"):
				continue
			if childName in keep:
				continue
			if active:
				child.Show()
			else:
				child.Hide()
		if not active and self.rideUpgradeButton:
			self.rideUpgradeButton.DisableHoverPulse()
		for widget in self.rideBonusWidgets:
			if active:
				widget.Show()
			else:
				widget.Hide()
		if self.rideEmptyText:
			if active:
				self.rideEmptyText.Hide()
			else:
				self.rideEmptyText.Show()

	def __BuildRideBonusList(self):
		# 4 fixed rows (one per mount skill): the buffi bonus-list row anatomy -- skill_value.png
		# row art + label + value cell, RTL-aware -- minus the scroll machinery (fixed row count,
		# native 257px row width fits rideBonusArea exactly).
		self.rideBonusValues  = []
		self.rideBonusWidgets = []
		area = self.GetChild2("rideBonusArea")
		self.rideBonusArea = area
		if not area:
			return
		rtl = localeinfo.IsARABIC()
		PAD = 10
		rowW = 257
		for i in range(uicompanionride.RIDE_SKILL_COUNT):
			y = i * BONUS_ROW_H
			bg = ui.ExpandedImageBox()
			bg.SetParent(area)
			bg.AddFlag("attach")
			bg.AddFlag("not_pick")
			bg.LoadImage(BUFFI_UI_PATH + "skill_value.png")
			bg.SetPosition(0, y)
			bg.Show()
			self.rideBonusWidgets.append(bg)
			cy = y + BONUS_IMG_H / 2
			lab = ui.TextLine()
			lab.SetParent(area)
			lab.AddFlag("attach")
			lab.AddFlag("not_pick")
			lab.SetOutline()
			lab.SetPackedFontColor(0xFFcabdab)
			lab.SetText(uicompanionride.RideSkillLabel(i))
			lab.SetVerticalAlignCenter()
			val = ui.TextLine()
			val.SetParent(area)
			val.AddFlag("attach")
			val.AddFlag("not_pick")
			val.SetOutline()
			val.SetPackedFontColor(0xFFd1b183)
			val.SetText("-")
			val.SetVerticalAlignCenter()
			if rtl:
				lab.SetHorizontalAlignLeft()
				lab.SetPosition(rowW - PAD, cy)
				val.SetHorizontalAlignCenter()
				val.SetPosition(PAD + 18, cy)
			else:
				lab.SetHorizontalAlignLeft()
				lab.SetPosition(PAD, cy)
				val.SetHorizontalAlignRight()
				val.SetPosition(rowW - PAD, cy)
			lab.Show()
			val.Show()
			self.rideBonusWidgets.append(lab)
			self.rideBonusWidgets.append(val)
			self.rideBonusValues.append(val)

	def __RefreshRideSkills(self, mountLevel, skillLevels):
		for i in range(uicompanionride.RIDE_SKILL_COUNT):
			unlockLevel = uicompanionride.RIDE_SKILL_UNLOCK_LEVEL[i]
			unlocked = mountLevel >= unlockLevel
			chainLocked = i > 0 and (skillLevels[i - 1] if i - 1 < len(skillLevels) else 0) < 1
			skillLv = skillLevels[i] if i < len(skillLevels) else 0
			lock = self.rideSkillLocks[i] if i < len(self.rideSkillLocks) else None
			if lock:
				if unlocked and not chainLocked:
					lock.Hide()
				else:
					lock.Show()
			plus = self.rideSkillPluses[i] if i < len(self.rideSkillPluses) else None
			if plus:
				if unlocked and not chainLocked and skillLv < uicompanionride.RIDE_SKILL_LEVEL_MAX:
					plus.Show()
				else:
					plus.Hide()
			# Bonus row value cell: RIDE_SKILL_PCT curve once unlocked, "-" while locked.
			val = self.rideBonusValues[i] if i < len(self.rideBonusValues) else None
			if val:
				if unlocked:
					val.SetText("+%d%%" % uicompanionride.RIDE_SKILL_PCT[skillLv])
				else:
					val.SetText("-")

	def __OnOverInRideExp(self):
		if not self.rideExpToolTip:
			self.rideExpToolTip = uitooltip.ToolTip()
		tip = self.rideExpToolTip
		tip.ClearToolTip()
		if self.rideExpText:
			tip.AppendTextLine("%s: %s" % (localeinfo.GROWTH_MOUNT_EXP, self.rideExpText.GetText()))
		else:
			tip.AppendTextLine("-")
		tip.ShowToolTip()

	def __OnOverOutRideExp(self):
		if self.rideExpToolTip:
			self.rideExpToolTip.HideToolTip()

	def __OnOverInRideSkillHover(self, idx):
		if not self.rideStatus:
			return
		if idx < 0 or idx >= uicompanionride.RIDE_SKILL_COUNT:
			return
		(active, level, exp, reqExp, gold, upMats, skillLevels, skillFails, skillChances, skillMats) = self.rideStatus
		unlockLevel = uicompanionride.RIDE_SKILL_UNLOCK_LEVEL[idx]
		unlocked = level >= unlockLevel
		chainLocked = idx > 0 and (skillLevels[idx - 1] if idx - 1 < len(skillLevels) else 0) < 1
		if not self.rideSkillToolTip:
			self.rideSkillToolTip = uitooltip.ToolTip()
		tip = self.rideSkillToolTip
		tip.ClearToolTip()
		if unlocked:
			skillLv = skillLevels[idx] if idx < len(skillLevels) else 0
			maxLv = uicompanionride.RIDE_SKILL_LEVEL_MAX
			tip.AppendTextLine(uicompanionride.RideSkillLabel(idx))
			curFmt = getattr(localeinfo, "GROWTH_MOUNT_SKILL_CUR_FMT", "Level %d/%d: +%d%%")
			tip.AppendTextLine(curFmt % (skillLv, maxLv, uicompanionride.RIDE_SKILL_PCT[skillLv]))
			if skillLv < maxLv:
				nextFmt = getattr(localeinfo, "GROWTH_MOUNT_SKILL_NEXT_FMT", "Next level: +%d%%")
				tip.AppendTextLine(nextFmt % uicompanionride.RIDE_SKILL_PCT[skillLv + 1])
			maxFmt = getattr(localeinfo, "GROWTH_MOUNT_SKILL_MAX_FMT", "Max (Level %d): +%d%%")
			tip.AppendTextLine(maxFmt % (maxLv, uicompanionride.RIDE_SKILL_PCT[maxLv]))
			if chainLocked:
				chainFmt = getattr(localeinfo, "GROWTH_MOUNT_SKILL_CHAIN", "Train the previous skill first")
				tip.AppendTextLine(chainFmt)
		else:
			fmt = getattr(localeinfo, "GROWTH_MOUNT_SKILL_LOCKED", "Unlocks at mount level %d")
			tip.AppendTextLine(fmt % unlockLevel)
		tip.ShowToolTip()

	def __OnOverOutRideSkillHover(self):
		if self.rideSkillToolTip:
			self.rideSkillToolTip.HideToolTip()

	def OnGrowthMountStatus(self, active, level, exp, reqExp, gold, upMats, skillLevels, skillFails, skillChances, skillMats):
		# Module-level cache so read-only consumers (wiki dungeon pages) can show
		# mount level/skills without a back-ref to this window.
		uicompanionride.LAST_STATUS = (active, level, tuple(skillLevels))
		if not self.board:
			return
		self.rideStatus = (active, level, exp, reqExp, gold, upMats, skillLevels, skillFails, skillChances, skillMats)
		self.RefreshRidePage()   # no-op unless the ride page is the visible page
		if not active:
			# Mount-called gate (Task 9): the sub-dialogs would show a level-up/skill-upgrade the
			# server will now refuse, so they die with the summon just like a page switch.
			if self.rideUpgradeDlg and self.rideUpgradeDlg.IsShow():
				self.rideUpgradeDlg.Close()
			if self.rideSkillDlg and self.rideSkillDlg.IsShow():
				self.rideSkillDlg.Close()
			return
		if self.rideUpgradeDlg and self.rideUpgradeDlg.IsShow():
			self.rideUpgradeDlg.OnStatus(level, gold, upMats)
		if self.rideSkillDlg and self.rideSkillDlg.IsShow():
			self.rideSkillDlg.OnStatus(skillLevels, skillFails, skillChances, skillMats)

	def OnUpdate(self):
		# Live countdown: re-render the duration text once per server-second so a < 1-day buffi visibly
		# ticks down (status pushes are state-change-only, so without this the seconds would be frozen).
		# Cheap: a single re-render, gated to once per second and only while a normal-expiry buffi is shown.
		# The pet page gets the same treatment for the pet's remaining lifetime.
		if not self.IsShow():
			return
		if self.currentPage == PAGE_PET:
			self.__UpdatePetLockHover()   # per-frame: hover is geometry, not an event (see Initialize)
			if self.petHasPet and self.petDurationEnd:
				now = app.GetGlobalTimeStamp()
				if now != self.petDurationTickLast:
					self.petDurationTickLast = now
					self.__RefreshPetDuration()
			return
		if not self.summonedNow or not self.durationExpireAt:
			return
		if self.durationExpireAt == BUFFI_DURATION_PERMANENT:
			return
		now = app.GetGlobalTimeStamp()
		if now == self.durationTickLast:
			return
		self.durationTickLast = now
		self.__RefreshDuration(self.durationExpireAt)

	# ------------------------------------------------------------------
	# Window lifecycle
	# ------------------------------------------------------------------
	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()
		self.__RequestStatus()
		if self.currentPage == PAGE_PET:
			self.RefreshPetPage()
		elif self.currentPage == PAGE_RIDE:
			self.RefreshRidePage()

	def OpenPetPage(self):
		# U9: the retired legacy pet window's openers (P key / taskbar pet button /
		# mini-window icon) land directly on the pet tab. __SetPage owns the tab
		# pressed-states, popup dismissal and the page refresh.
		self.__SetPage(PAGE_PET)

	def IsPetPageActive(self):
		return self.currentPage == PAGE_PET

	def OpenRidePage(self):
		self.__SetPage(PAGE_RIDE)

	def IsRidePageActive(self):
		return self.currentPage == PAGE_RIDE

	def __RequestStatus(self):
		# Server replies with BINARY_OnBuffiStatus -> interface.OnBuffiStatus ->
		# RefreshFromStatus (only while shown), so this never loops.
		if hasattr(net, "SendBuffiPacket"):
			net.SendBuffiPacket(net.BUFFI_CG_STATUS, 0)

	def OnMapChanged(self):
		# Status is not auto-pushed on warp/relog; re-request if the window is up.
		if self.IsShow():
			self.__RequestStatus()

	def Close(self):
		if self.expToolTip:
			self.expToolTip.HideToolTip()
		if self.petExpToolTip:
			self.petExpToolTip.HideToolTip()
		if self.petPotionToolTip:
			self.petPotionToolTip.HideToolTip()
		if self.petLockToolTip:
			self.petLockToolTip.HideToolTip()   # OnUpdate hover stops with the window hidden
		self.petLockHoverIdx = -1
		if self.petPotionPickDlg:
			self.petPotionPickDlg.Close()   # quantity dialog dies with the window
		tipPetSkill = getattr(self.interface, "tooltipPetSkill", None) if self.interface else None
		if tipPetSkill:
			tipPetSkill.HideToolTip()   # closed mid skill-hover: OverOut never fires on a hidden window
		tipSkill = getattr(self.interface, "tooltipSkill", None) if self.interface else None
		if tipSkill:
			tipSkill.HideToolTip()      # same for the shared buffi/job skill tooltip
		if self.oreToolTip:
			self.oreToolTip.HideToolTip()
		if self.nameToolTip:
			self.nameToolTip.HideToolTip()
		if self.durationConfirmDlg:
			self.durationConfirmDlg.Close()
		self.__OnCancelPetSkillQuestion()   # pending learn/delete confirm dies with the window
		if self.rideUpgradeDlg:
			self.rideUpgradeDlg.Close()   # ride sub-dialogs die with the window
		if self.rideSkillDlg:
			self.rideSkillDlg.Close()
		if self.rideExpToolTip:
			self.rideExpToolTip.HideToolTip()
		if self.rideSkillToolTip:
			self.rideSkillToolTip.HideToolTip()
		if self.ridePortraitToolTip:
			self.ridePortraitToolTip.HideToolTip()
		if self.rideUpgradeButton:
			self.rideUpgradeButton.DisableHoverPulse()   # window closed -- pulse must not keep ticking while hidden
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
