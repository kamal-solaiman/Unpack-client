# coding: latin_1
#
# Companion window layout: a left page-tab rail (buffi / pet) + the page content.
# The buffi page is the original layout, wrapped in the "content" container so the
# rail can occupy the left column without renumbering any child. The pet page is an
# empty placeholder container ("petPage") the growth-pet rework will fill in later.
# uicompanion.py only binds the widgets (GetChild), wires the button events, and
# attaches the 3D buffi render target.
import localeinfo
CONTENT_WIDTH = 279              # original window body width (the "content" container)
RAIL_W        = 36               # left page-tab rail column (btn_buffi/btn_pet are 36x36)
WINDOW_WIDTH  = RAIL_W + CONTENT_WIDTH
WINDOW_HEIGHT = 412
PATH = "d:/ymir work/ui/game/companion/"
SR   = "d:/ymir work/ui/game/skillreader/"   # levelup_* art reused as the per-skill "+" (open skill reader)

# Pet skill-row lock overlays: the ae loader RIGHT-MIRRORS every image child of petPage
# (rendered left = 267 - x - 32) while the slot window's CELLS never mirror -- so the ae
# declarations must be the PRE-MIRROR of each lock's own slot cell (the "+" buttons already
# follow this rule), while en renders declarations as-is. Index i = skill slot i.
if localeinfo.IsARABIC():
	PET_SKILL_LOCK_X = (21, 59, 96, 135, 172, 210)
else:
	PET_SKILL_LOCK_X = (206, 168, 130, 92, 54, 16)
window = {
	"name"   : "CompanionWindow",
	"x"      : 0,
	"y"      : 0,
	"style"  : ("movable", "float",),
	"width"  : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,
	"children" :
	(
		### PAGE TAB RAIL (left column, always visible): switches between the buffi page and
		### the pet placeholder page. radio_buttons so the active tab stays visually pressed;
		### wired in uicompanion (__OnClickPageTab). RTL mirrors the rail to the right edge. ###
		{
			"name" : "tabBuffi",
			"type" : "radio_button",
			"x" : 5,
			"y" : 31,
			"default_image" : PATH + "btn_buffi_norm.png",
			"over_image"    : PATH + "btn_buffi_hover.png",
			"down_image"    : PATH + "btn_buffi_select.png",
		},
		{
			"name" : "tabPet",
			"type" : "radio_button",
			"x" : 5,
			"y" : 65,
			"default_image" : PATH + "btn_pet_norm.png",
			"over_image"    : PATH + "btn_pet_hover.png",
			"down_image"    : PATH + "btn_pet_select.png",
		},
		{
			"name" : "tabRide",
			"type" : "radio_button",
			"x" : 5,
			"y" : 99,
			"default_image" : PATH + "btn_horse_norm.png",
			"over_image"    : PATH + "btn_horse_hover.png",
			"down_image"    : PATH + "btn_horse_select.png",
		},
		### CONTENT WRAPPER: the whole original layout lives inside this container so the tab
		### rail can occupy the left column -- every child keeps its original coordinates,
		### now relative to this wrapper (which is what RTL-mirrors as one unit too). ###
		{
		"name"   : "content",
		"type"   : "window",
		"x"      : RAIL_W,
		"y"      : 0,
		"width"  : CONTENT_WIDTH,
		"height" : WINDOW_HEIGHT,
		"children" :
		(
		{
			"name"   : "board",
			"type"   : "board_with_titlebar",
			"x"      : 0,
			"y"      : 0,
			"width"  : CONTENT_WIDTH,
			"height" : WINDOW_HEIGHT,
			"title"  : "",
		},
		### HELP "?" BUTTON (opens the buffi-system explainer popup; always visible, even with no buffi) ####
		### Declared at a LOW x so RTL mirroring keeps it clear of the titlebar close button on both sides:
		### EN close = top-right -> "?" stays top-left; AE close = top-left -> "?" mirrors to top-right. ###
		{
			"name" : "helpButton",
			"type" : "button",
			"x" : 19,
			"y" : 9,
			"default_image" : "spin_wheel/question_mark.png",
			"over_image"    : "spin_wheel/question_mark_1.png",
			"down_image"    : "spin_wheel/question_mark_2.png",
		},
		### PET-PAGE HELP "?" BUTTON (opens the general pet explainer; same titlebar spot
		### as the buffi "?" -- the page toggle shows exactly ONE of the two, so they
		### never render together). ###
		{
			"name" : "petHelpButton",
			"type" : "button",
			"x" : 19,
			"y" : 9,
			"default_image" : "spin_wheel/question_mark.png",
			"over_image"    : "spin_wheel/question_mark_1.png",
			"down_image"    : "spin_wheel/question_mark_2.png",
		},
		### BACKGROUND PANEL ####
		{
			"name" : "background",
			"type" : "image",
			"x" : 6,
			"y" : 29,
			"image" : PATH + "background.png",
			"style" : ("not_pick",),
		},
		### PORTRAIT (3D buffi render target attached in code; before the detail
		### rows so they render on top) ####
		{
			"name" : "portraitFrame",
			"type" : "image",
			"x" : 10,
			"y" : 35,
			"image" : PATH + "buffi_bg.png",
			#"style" : ("not_pick",),
		},
		### NAME ####
		{
			"name" : "detailsName",
			"type" : "image",
			"x" : 75,
			"y" : 36 - 4,
			"image" : PATH + "detail_title.png",
			"children" :
			(
				{
					"name" : "detailsName_text",
					"type" : "text",
					"outline" : 1,
					"x" : 48, "y" : 10,
					"text" : localeinfo.COMPANION_NAME,
					"color" : 0xFFcabdab,
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
			),
		},
		{
			"name" : "detailsNameValue",
			"type" : "image",
			"x" : 168,
			"y" : 36 - 4,
			"image" : PATH + "detail_value.png",
			"children" :
			(
				{
					"name" : "detailsName_text_value",
					"type" : "text",
					"outline" : 1,
					"x" : 48, "y" : 10,
					"text" : "",
					"color" : 0xFFd1b183,
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
			),
		},
		### NAME HOVER (transparent pick target over the name row -> tooltip: nickname remaining
		### time + boss% + unlocked buffs. Declared after the name images so it renders on top;
		### in the uiscript so it RTL-mirrors with the name row.) ####
		{ "name" : "nameHover", "type" : "window", "x" : 75, "y" : 31, "width" : 189, "height" : 24 },
		### LEVEL ####
		{
			"name" : "detailsLevel",
			"type" : "image",
			"x" : 75,
			"y" : 58 - 4,
			"image" : PATH + "detail_title.png",
			"children" :
			(
				{
					"name" : "detailsLevel_text1",
					"type" : "text",
					"outline" : 1,
					"x" : 48, "y" : 10,
					"text" : localeinfo.COMPANION_LEVEL,
					"color" : 0xFFcabdab,
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
			),
		},
		{
			"name" : "detailsLevelValue",
			"type" : "image",
			"x" : 168,
			"y" : 58 - 4,
			"image" : PATH + "detail_value.png",
			"children" :
			(
				{
					"name" : "detailslevel_text_value",
					"type" : "text",
					"outline" : 1,
					"x" : 48, "y" : 10,
					"text" : "",
					"color" : 0xFFd1b183,
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
			),
		},
		### INTELLIGENCE ####
		{
			"name" : "detailsInt",
			"type" : "image",
			"x" : 75,
			"y" : 80 - 4,
			"image" : PATH + "detail_title.png",
			"children" :
			(
				{
					"name" : "detailsInt_text1",
					"type" : "text",
					"outline" : 1,
					"x" : 48, "y" : 10,
					"text" : localeinfo.COMPANION_INTELLIGENCE,
					"color" : 0xFFcabdab,
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
			),
		},
		{
			"name" : "detailsIntValue",
			"type" : "image",
			"x" : 168,
			"y" : 80 - 4,
			"image" : PATH + "detail_value.png",
			"children" :
			(
				{
					"name" : "detailsInt_text_value",
					"type" : "text",
					"outline" : 1,
					"x" : 48, "y" : 10,
					"text" : "",
					"color" : 0xFFd1b183,
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
			),
		},
		### EXPERIENCE SUBHEADER ####
		{
			"name" : "experienceHeader",
			"type" : "image",
			"x" : 8,
			"y" : 95,
			"image" : PATH + "subheader_bg.png",
			#"style" : ("not_pick",),
			"children" :
			(
				{
					"name" : "experienceHeader_text",
					"type" : "text",
					"outline" : 1,
					"x" : 66, "y" : 6,
					"text" : localeinfo.COMPANION_EXPERIENCE,
					"color" : 0xFFcabdab,
					"text_horizontal_align" : "center",
				},
			),
		},
		### 4 EXPERIENCE BALLS: a static progress_empty.png orb per quarter, with a progress.png FILL
		### layer (expanded_image) on top -- clipped per-orb via SetRenderingRect in code so each orb
		### fills SMOOTHLY (vertical, bottom-up) like the taskbar EXP orbs, not in whole-orb 25% jumps.
		### The empty orbs are declared first so the fill layers render on top of them. ####
		{ "name" : "expbg", "type" : "image", "x" : 9, "y" : 118, "image" : PATH + "detail_exp_bg.png", },
		{ "name" : "expBallBg0", "type" : "image", "x" : 18, "y" : 129 - 5, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
		{ "name" : "expBallBg1", "type" : "image", "x" : 45, "y" : 129 - 5, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
		{ "name" : "expBallBg2", "type" : "image", "x" : 72, "y" : 129 - 5, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
		{ "name" : "expBallBg3", "type" : "image", "x" : 99, "y" : 129 - 5, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
		{ "name" : "expBall0", "type" : "expanded_image", "x" : 18, "y" : 129 - 5, "image" : PATH + "progress.png", "style" : ("not_pick",), },
		{ "name" : "expBall1", "type" : "expanded_image", "x" : 45, "y" : 129 - 5, "image" : PATH + "progress.png", "style" : ("not_pick",), },
		{ "name" : "expBall2", "type" : "expanded_image", "x" : 72, "y" : 129 - 5, "image" : PATH + "progress.png", "style" : ("not_pick",), },
		{ "name" : "expBall3", "type" : "expanded_image", "x" : 99, "y" : 129 - 5, "image" : PATH + "progress.png", "style" : ("not_pick",), },
		### EXP HOVER (transparent pick target spanning the 4 balls; tooltip events bound in code) ####
		{ "name" : "expHover", "type" : "window", "x" : 10, "y" : 121, "width" : 128, "height" : 32 },
		### EVOLVE / DURATION BUTTONS (text baked into the 131x33 art) ####
		{
			"name" : "evolveButton",
			"type" : "button",
			"x" : 138,
			"y" : 95,
			"text" : localeinfo.COMPANION_EVOLVE,
			"text_outline" : 1,
			"text_color" :  0xFFcabdab,
			"default_image" : PATH + "btn_evolve_norm.png",
			"over_image"    : PATH + "btn_evolve_hover.png",
			"down_image"    : PATH + "btn_evolve_select.png",
		},
		{
			"name" : "durationButton",
			"type" : "button",
			"x" : 138,
			"y" : 125,
			"text" : localeinfo.COMPANION_DURATION,
			"text_outline" : 1,
			"text_color" :  0xFFcabdab,
			"default_image" : PATH + "btn_duration_norm.png",
			"over_image"    : PATH + "btn_duration_hover.png",
			"down_image"    : PATH + "btn_duration_select.png",
		},
		
		{
			"name" : "secondsection",
			"type" : "image",
			"x" : 8,
			"y" : 155,
			"image" : PATH + "header_title.png",
			"children" :
			(
				{
					"name" : "secondsection_text1",
					"type" : "text",
					"outline" : 1,
					"x" : 129, "y" : 15,
					"text" : localeinfo.COMPANION_SECTIONTWO,
					"color" : 0xFFcabdab,
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
			),
		},
		{ "name" : "secondsectionbg", "type" : "image", "x" :9, "y" : 183, "image" : PATH + "skill_pet_bg.png", },
		### --- SECOND SECTION CONTENT (RTL: ores render-LEFT = high x; duration render-RIGHT = low x) --- ###
		### DURATION: gauge_empty frame + gauge_full fill (clipped in code) + remaining-time text below ####
		{ "name" : "durationGaugeBg",   "type" : "image",          "x" : 14, "y" : 196 - 5, "image" : PATH + "gauge_empty.png", },
		{ "name" : "durationGaugeFill", "type" : "expanded_image", "x" : 16, "y" : 198 - 5, "image" : PATH + "gauge_full.png", },
		{
			"name" : "durationText", "type" : "text", "x" : 73, "y" : 222 - 5,
			"text" : "", "outline" : 1, "color" : 0xFFcabdab,
			"text_horizontal_align" : "center", "text_vertical_align" : "center",
		},
		### ORES: slot_runes backgrounds (not_pick) + a SlotWindow on top for icons + drag-insert/click-remove ####
		{ "name" : "oreSlot0", "type" : "image", "x" : 150, "y" : 193 - 5, "image" : PATH + "slot_runes.png",  },
		{ "name" : "oreSlot1", "type" : "image", "x" : 188, "y" : 193 - 5, "image" : PATH + "slot_runes.png", },
		{ "name" : "oreSlot2", "type" : "image", "x" : 226, "y" : 193 - 5, "image" : PATH + "slot_runes.png", },
		{
			"name" : "oreSlotWindow", "type" : "slot", "x" : 19, "y" : 193 - 5, "width" : 112, "height" : 36,
			"slot" : (
				{ "index" : 0, "x" : 77,  "y" : 2, "width" : 32, "height" : 32 },
				{ "index" : 1, "x" : 38, "y" : 2, "width" : 32, "height" : 32 },
				{ "index" : 2, "x" : 1, "y" : 2, "width" : 32, "height" : 32 },
			),
		},
		### EMPTY-STATE NOTICE (shown only while NO buffi is summoned; all other content is hidden) ####
		{
			"name" : "emptyText",
			"type" : "text",
			"x" : 139, "y" : 210,
			"text" : localeinfo.COMPANION_NO_BUFFI,
			"outline" : 1,
			"color" : 0xFFcabdab,
			"text_horizontal_align" : "center",
			"text_vertical_align" : "center",
		},

		{
			"name" : "thirdsection",
			"type" : "image",
			"x" : 8,
			"y" : 226,
			"image" : PATH + "header_title.png",
			"children" :
			(
				{
					"name" : "thirdsection_text1",
					"type" : "text",
					"outline" : 1,
					"x" : 129, "y" : 15,
					"text" : localeinfo.COMPANION_SECTIONTHREE,
					"color" : 0xFFcabdab,
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
			),
		},
		{ "name" : "thirdsectionbg", "type" : "image", "x" :9, "y" : 252, "image" : PATH + "skill_pet_bg.png", },

		### THIRD SECTION SKILL ICONS: 4 slot_skill backdrops (not_pick) + a SlotWindow on top (icons set via
		### SetSkillSlotNew) + a 13x13 "+" per skill (opens the auto-skill-reader buffi page) + lock overlays on
		### the 2 premium/name-gated skills (index 2 Kwaesok, 3 Jeungryeok), shown while the buffi is unnamed.
		### Positions are easy to nudge (RTL: low x renders right -> index 0 = rightmost). ###
		{ "name" : "buffiSkillBg0", "type" : "image", "x" : 28,  "y" : 254, "image" : PATH + "slot_skill.png",  },
		{ "name" : "buffiSkillBg1", "type" : "image", "x" : 86,  "y" : 254, "image" : PATH + "slot_skill.png",  },
		{ "name" : "buffiSkillBg2", "type" : "image", "x" : 144, "y" : 254, "image" : PATH + "slot_skill.png",  },
		{ "name" : "buffiSkillBg3", "type" : "image", "x" : 202, "y" : 254, "image" : PATH + "slot_skill.png",  },
		{
			"name" : "buffiSkillSlot", "type" : "slot", "x" : 41, "y" : 257, "width" : 214, "height" : 40,
			"slot" : (
				{ "index" : 0, "x" : 0,   "y" : 0, "width" : 40, "height" : 40 },
				{ "index" : 1, "x" : 58,  "y" : 0, "width" : 40, "height" : 40 },
				{ "index" : 2, "x" : 116, "y" : 0, "width" : 40, "height" : 40 },
				{ "index" : 3, "x" : 174, "y" : 0, "width" : 40, "height" : 40 },
			),
		},
		{ "name" : "buffiSkillLock2", "type" : "image", "x" : 32, "y" : 257, "image" : PATH + "slot_locked.png", },
		{ "name" : "buffiSkillLock3", "type" : "image", "x" : 90, "y" : 257, "image" : PATH + "slot_locked.png", },
		{ "name" : "buffiSkillPlus0", "type" : "button", "x" : 56,  "y" : 281, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_normal.png", "down_image" : SR + "levelup_down.png", },
		{ "name" : "buffiSkillPlus1", "type" : "button", "x" : 114, "y" : 281, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_normal.png", "down_image" : SR + "levelup_down.png", },
		{ "name" : "buffiSkillPlus2", "type" : "button", "x" : 172, "y" : 281, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_normal.png", "down_image" : SR + "levelup_down.png", },
		{ "name" : "buffiSkillPlus3", "type" : "button", "x" : 230, "y" : 281, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_normal.png", "down_image" : SR + "levelup_down.png", },

		### BONUS ROWS -> a SCROLLABLE list built in code (uicompanion.py __BuildBonusList):
		### a clip viewport + thin scrollbar so the list can grow (boss-damage row, future rows)
		### without breaking the fixed window. The 4 skill-bonus rows + the boss row are created as
		### children of a clipped scrollBoard inside bonusViewport. (Old skill0bg..skill3bg fixed
		### rows removed -- they could not scroll.) Geometry below is a starting point; nudge freely. ###
		{ "name" : "bonusViewport", "type" : "window",         "x" : 10,  "y" : 296, "width" : 243, "height" : 104 },
		{ "name" : "bonusScroll",   "type" : "scrollbarnew",   "x" : 255, "y" : 296, "size" : 102 },

		### PET PAGE (growth-pet rework, U1 skeleton): buffi-position parity -- every coordinate
		### below is the matching buffi widget's, shifted into this container (petPage sits at the
		### background origin, so rel = abs - (6,29)). CONVENTION: every pet-page widget name MUST
		### start with "pet" (uicompanion's page/empty-state logic keys on that prefix). Static
		### widgets only; the pet controller (U2+) binds data, fills and events. Nudge freely. ###
		{ "name" : "petPage", "type" : "window", "x" : 6, "y" : 29, "width" : 267, "height" : 377,
		"children" :
		(
			### PORTRAIT (frame art reused; the summon-item ICON is set into the slot in code) ###
			{ "name" : "petPortraitFrame", "type" : "image", "x" : 4, "y" : 3, "image" : PATH + "pet_bg.png", },
			{
				"name" : "petIconSlot", "type" : "slot", "x" : 211, "y" : 18, "width" : 36, "height" : 36,
				"slot" : ( { "index" : 0, "x" : 0, "y" : 0, "width" : 32, "height" : 32 }, ),
			},
			### NAME / TYPE / LEVEL rows (same geometry as the buffi Name/Level/INT rows) ###
			{
				"name" : "petNameTitle", "type" : "image", "x" : 69, "y" : 3, "image" : PATH + "detail_title.png",
				"children" : ( { "name" : "petName_text", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : localeinfo.COMPANION_NAME, "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "petNameValue", "type" : "image", "x" : 162, "y" : 3, "image" : PATH + "detail_value.png",
				"children" : ( { "name" : "petName_text_value", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : "", "color" : 0xFFd1b183,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "petTypeTitle", "type" : "image", "x" : 69, "y" : 25, "image" : PATH + "detail_title.png",
				"children" : ( { "name" : "petType_text", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : localeinfo.COMPANION_PET_TYPE, "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "petTypeValue", "type" : "image", "x" : 162, "y" : 25, "image" : PATH + "detail_value.png",
				"children" : ( { "name" : "petType_text_value", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : "", "color" : 0xFFd1b183,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "petLevelTitle", "type" : "image", "x" : 69, "y" : 47, "image" : PATH + "detail_title.png",
				"children" : ( { "name" : "petLevel_text", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : localeinfo.COMPANION_LEVEL, "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "petLevelValue", "type" : "image", "x" : 162, "y" : 47, "image" : PATH + "detail_value.png",
				"children" : ( { "name" : "petLevel_text_value", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : "", "color" : 0xFFd1b183,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			### EXPERIENCE: subheader + 4 orbs (empty art + clipped fill layers, exactly like the buffi
			### page) + a hover pick-target. Fill layers start zero-clipped in code. ###
			{
				"name" : "petExpHeader", "type" : "image", "x" : 2, "y" : 66, "image" : PATH + "subheader_bg.png",
				"children" : ( { "name" : "petExpHeader_text", "type" : "text", "outline" : 1, "x" : 66, "y" : 6,
					"text" : localeinfo.COMPANION_EXPERIENCE, "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", }, ),
			},
			### EXP HELP "?" (opens the leveling-journey explainer). Declared AFTER the
			### header so it renders on top of the bar; low x mirrors clear in RTL. ###
			{
				"name" : "petExpHelpButton",
				"type" : "button",
				"x" : 8,
				"y" : 69,
				"default_image" : "spin_wheel/question_mark.png",
				"over_image"    : "spin_wheel/question_mark_1.png",
				"down_image"    : "spin_wheel/question_mark_2.png",
			},
			{ "name" : "petExpBg", "type" : "image", "x" : 3, "y" : 89, "image" : PATH + "detail_exp_bg.png", },
			{ "name" : "petExpBallBg0", "type" : "image", "x" : 12, "y" : 95, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
			{ "name" : "petExpBallBg1", "type" : "image", "x" : 39, "y" : 95, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
			{ "name" : "petExpBallBg2", "type" : "image", "x" : 66, "y" : 95, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
			{ "name" : "petExpBallBg3", "type" : "image", "x" : 93, "y" : 95, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
			{ "name" : "petExpBall0", "type" : "expanded_image", "x" : 12, "y" : 95, "image" : PATH + "progress.png", "style" : ("not_pick",), },
			{ "name" : "petExpBall1", "type" : "expanded_image", "x" : 39, "y" : 95, "image" : PATH + "progress.png", "style" : ("not_pick",), },
			{ "name" : "petExpBall2", "type" : "expanded_image", "x" : 66, "y" : 95, "image" : PATH + "progress.png", "style" : ("not_pick",), },
			{ "name" : "petExpBall3", "type" : "expanded_image", "x" : 93, "y" : 95, "image" : PATH + "progress.png", "style" : ("not_pick",), },
			{ "name" : "petExpHover", "type" : "window", "x" : 4, "y" : 92, "width" : 128, "height" : 32 },
			### UPGRADE / FEED buttons (the page's ONLY 2 buttons -- each opens a 2-tab sub-window
			### in U3/U5; art reused from the buffi evolve/duration buttons) ###
			{
				"name" : "petUpgradeButton", "type" : "button", "x" : 132, "y" : 66,
				"text" : localeinfo.COMPANION_PET_UPGRADE, "text_outline" : 1, "text_color" : 0xFFcabdab,
				"default_image" : PATH + "btn_refine_norm.png",
				"over_image"    : PATH + "btn_refine_hover.png",
				"down_image"    : PATH + "btn_refine_select.png",
			},
			{
				"name" : "petFeedButton", "type" : "button", "x" : 132, "y" : 96,
				"text" : localeinfo.COMPANION_PET_FEED, "text_outline" : 1, "text_color" : 0xFFcabdab,
				"default_image" : PATH + "btn_feed_norm.png",
				"over_image"    : PATH + "btn_feed_hover.png",
				"down_image"    : PATH + "btn_feed_select.png",
			},
			### DURATION section (gauge geometry = the buffi one; right half of the body is
			### intentionally free -- no ore slots on the pet page) ###
			{ "name" : "petDurationBg", "type" : "image", "x" : 3, "y" : 126, "image" : PATH + "skill_pet_bg.png", },
			{ "name" : "petDurationGaugeBg",   "type" : "image",          "x" : 8,  "y" : 131, "image" : PATH + "gauge_empty.png", },
			{ "name" : "petDurationGaugeFill", "type" : "expanded_image", "x" : 10, "y" : 133, "image" : PATH + "gauge_full.png", },
			{
				"name" : "petDurationText", "type" : "text", "x" : 200, "y" : 140,
				"text" : "", "outline" : 1, "color" : 0xFFcabdab,
				"text_horizontal_align" : "center", "text_vertical_align" : "center",
			},
			### STATS section: 3 rows on pet_bonus_value.png row art (icon frame + value pill are
			### baked into the art). The left slot shows the row's stat-potion ITEM -- vnum is set
			### in code and varies with the pet's Type (U2). Gauge = pet_gauge_bg + colored fill
			### (fill-to-Type-cap), zero-clipped in code until data arrives. ###
			{
				"name" : "petStatsHeader", "type" : "image", "x" : 2, "y" : 152, "image" : PATH + "header_title.png",
				"children" : ( { "name" : "petStatsHeader_text", "type" : "text", "outline" : 1, "x" : 129, "y" : 15,
					"text" : localeinfo.COMPANION_PET_STATS, "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			# { "name" : "petStatBar0Bg",   "type" : "image",          "x" : 8,  "y" : 228, "image" : PATH + "gauge_empty.png", },
			# { "name" : "petStatBar0Fill", "type" : "expanded_image", "x" : 10, "y" : 230, "image" : PATH + "gauge_full.png", },
			# {
				# "name" : "petStatLabel0", "type" : "text", "x" : 67, "y" : 238, "text" : localeinfo.COMPANION_PET_STAT_HP,
				# "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center",
			# },
			# {
				# "name" : "petStatValue0", "type" : "image", "x" : 162, "y" : 227, "image" : PATH + "detail_value.png",
				# "children" : ( { "name" : "petStatValue0_text", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					# "text" : "", "color" : 0xFFd1b183,
					# "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			# },
			# { "name" : "petStatBar1Bg",   "type" : "image",          "x" : 8,  "y" : 252, "image" : PATH + "gauge_empty.png", },
			# { "name" : "petStatBar1Fill", "type" : "expanded_image", "x" : 10, "y" : 254, "image" : PATH + "gauge_full.png", },
			# {
				# "name" : "petStatLabel1", "type" : "text", "x" : 67, "y" : 262, "text" : localeinfo.COMPANION_PET_STAT_ATT,
				# "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center",
			# },
			# {
				# "name" : "petStatValue1", "type" : "image", "x" : 162, "y" : 251, "image" : PATH + "detail_value.png",
				# "children" : ( { "name" : "petStatValue1_text", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					# "text" : "", "color" : 0xFFd1b183,
					# "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			# },
			# { "name" : "petStatBar2Bg",   "type" : "image",          "x" : 8,  "y" : 276, "image" : PATH + "gauge_empty.png", },
			# { "name" : "petStatBar2Fill", "type" : "expanded_image", "x" : 10, "y" : 278, "image" : PATH + "gauge_full.png", },
			# {
				# "name" : "petStatLabel2", "type" : "text", "x" : 67, "y" : 286, "text" : localeinfo.COMPANION_PET_STAT_ATTVALUE,
				# "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center",
			# },
			# {
				# "name" : "petStatValue2", "type" : "image", "x" : 162, "y" : 275, "image" : PATH + "detail_value.png",
				# "children" : ( { "name" : "petStatValue2_text", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					# "text" : "", "color" : 0xFFd1b183,
					# "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			# },
			{ "name" : "petStatRow0Bg", "type" : "image", "x" : 5, "y" : 182 - 2, "image" : PATH + "pet_bonus_value.png", },
			{
				"name" : "petStatIconSlot0", "type" : "slot", "x" : 223, "y" : 187 - 2, "width" : 32, "height" : 32,
				"slot" : ( { "index" : 0, "x" : 0, "y" : 0, "width" : 32, "height" : 32 }, ),
			},
			{
				"name" : "petStatLabel0", "type" : "text", "x" : 51, "y" : 195 - 2, "text" : localeinfo.COMPANION_PET_STAT_HP,
				"outline" : 1, "color" : 0xFFcabdab, "text_vertical_align" : "center",
			},
			{ "name" : "petStatGaugeBg0",   "type" : "image",          "x" : 51, "y" : 207 - 2, "image" : PATH + "pet_gauge_bg.png", },
			{ "name" : "petStatGaugeFill0", "type" : "expanded_image", "x" : 54, "y" : 210 - 2, "image" : PATH + "pet_gauge_full_red.png", },
			{
				"name" : "petStatValue0", "type" : "text", "x" : 227, "y" : 203 - 2, "text" : "",
				"outline" : 1, "color" : 0xFFd1b183, "text_horizontal_align" : "center", "text_vertical_align" : "center",
			},
			{ "name" : "petStatRow1Bg", "type" : "image", "x" : 5, "y" : 225 - 2, "image" : PATH + "pet_bonus_value.png", },
			{
				"name" : "petStatIconSlot1", "type" : "slot", "x" : 223, "y" : 230 - 2, "width" : 32, "height" : 32,
				# slot index = stat row (the shared click/hover handlers key on it)
				"slot" : ( { "index" : 1, "x" : 0, "y" : 0, "width" : 32, "height" : 32 }, ),
			},
			{
				"name" : "petStatLabel1", "type" : "text", "x" : 51, "y" : 238 - 2, "text" : localeinfo.COMPANION_PET_STAT_ATT,
				"outline" : 1, "color" : 0xFFcabdab, "text_vertical_align" : "center",
			},
			{ "name" : "petStatGaugeBg1",   "type" : "image",          "x" : 51, "y" : 250 - 2, "image" : PATH + "pet_gauge_bg.png", },
			{ "name" : "petStatGaugeFill1", "type" : "expanded_image", "x" : 54, "y" : 253 - 2, "image" : PATH + "pet_gauge_full_blue.png", },
			{
				"name" : "petStatValue1", "type" : "text", "x" : 227, "y" : 246 - 2, "text" : "",
				"outline" : 1, "color" : 0xFFd1b183, "text_horizontal_align" : "center", "text_vertical_align" : "center",
			},
			{ "name" : "petStatRow2Bg", "type" : "image", "x" : 5, "y" : 268 - 2, "image" : PATH + "pet_bonus_value.png", },
			{
				"name" : "petStatIconSlot2", "type" : "slot", "x" : 223, "y" : 273 - 2, "width" : 32, "height" : 32,
				# slot index = stat row (the shared click/hover handlers key on it)
				"slot" : ( { "index" : 2, "x" : 0, "y" : 0, "width" : 32, "height" : 32 }, ),
			},
			{
				"name" : "petStatLabel2", "type" : "text", "x" : 51, "y" : 281 - 2, "text" : localeinfo.COMPANION_PET_STAT_ATTVALUE,
				"outline" : 1, "color" : 0xFFcabdab, "text_vertical_align" : "center",
			},
			{ "name" : "petStatGaugeBg2",   "type" : "image",          "x" : 51, "y" : 293 - 2, "image" : PATH + "pet_gauge_bg.png", },
			{ "name" : "petStatGaugeFill2", "type" : "expanded_image", "x" : 54, "y" : 296 - 2, "image" : PATH + "pet_gauge_full_green.png", },
			{
				"name" : "petStatValue2", "type" : "text", "x" : 227, "y" : 289 - 2, "text" : "",
				"outline" : 1, "color" : 0xFFd1b183, "text_horizontal_align" : "center", "text_vertical_align" : "center",
			},
			### SKILLS section: 6 slots in one row (38px pitch, ore-slot art), lock overlays (visibility
			### wired by level gates in U4) + a 13x13 "+" per slot (skill-upgrade dialog in U4) ###
			{
				"name" : "petSkillsHeader", "type" : "image", "x" : 2, "y" : 311 - 3, "image" : PATH + "header_title.png",
				"children" : ( { "name" : "petSkillsHeader_text", "type" : "text", "outline" : 1, "x" : 129, "y" : 15,
					"text" : localeinfo.COMPANION_PET_SKILLS, "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{ "name" : "petSkillBg5", "type" : "image", "x" : 8 + 8,   "y" : 338 - 2, "image" : PATH + "slot_runes.png", },
			{ "name" : "petSkillBg4", "type" : "image", "x" : 46 + 8,  "y" : 338 - 2, "image" : PATH + "slot_runes.png", },
			{ "name" : "petSkillBg3", "type" : "image", "x" : 84 + 8,  "y" : 338 - 2, "image" : PATH + "slot_runes.png", },
			{ "name" : "petSkillBg2", "type" : "image", "x" : 122 + 8, "y" : 338 - 2, "image" : PATH + "slot_runes.png", },
			{ "name" : "petSkillBg1", "type" : "image", "x" : 160 + 8, "y" : 338 - 2, "image" : PATH + "slot_runes.png", },
			{ "name" : "petSkillBg0", "type" : "image", "x" : 198 + 8, "y" : 338 - 2, "image" : PATH + "slot_runes.png", },
			{
				"name" : "petSkillSlot", "type" : "slot", "x" : 7, "y" : 336, "width" : 255, "height" : 38,
				"slot" : (
					{ "index" : 0, "x" : 209,   "y" : 3, "width" : 32, "height" : 32 },
					{ "index" : 1, "x" : 171,  "y" : 3, "width" : 32, "height" : 32 },
					{ "index" : 2, "x" : 134,  "y" : 3, "width" : 32, "height" : 32 },
					{ "index" : 3, "x" : 95, "y" : 3, "width" : 32, "height" : 32 },
					{ "index" : 4, "x" : 58, "y" : 3, "width" : 32, "height" : 32 },
					{ "index" : 5, "x" : 20, "y" : 3, "width" : 32, "height" : 32 },
				),
			},
			{ "name" : "petSkillLock0", "type" : "image", "x" : PET_SKILL_LOCK_X[0], "y" : 341, "image" : PATH + "slot_locked.png", "style" : ("not_pick",), },
			{ "name" : "petSkillLock1", "type" : "image", "x" : PET_SKILL_LOCK_X[1], "y" : 341, "image" : PATH + "slot_locked.png", "style" : ("not_pick",), },
			{ "name" : "petSkillLock2", "type" : "image", "x" : PET_SKILL_LOCK_X[2], "y" : 341, "image" : PATH + "slot_locked.png", "style" : ("not_pick",), },
			{ "name" : "petSkillLock3", "type" : "image", "x" : PET_SKILL_LOCK_X[3], "y" : 341, "image" : PATH + "slot_locked.png", "style" : ("not_pick",), },
			{ "name" : "petSkillLock4", "type" : "image", "x" : PET_SKILL_LOCK_X[4], "y" : 341, "image" : PATH + "slot_locked.png", "style" : ("not_pick",), },
			{ "name" : "petSkillLock5", "type" : "image", "x" : PET_SKILL_LOCK_X[5], "y" : 341, "image" : PATH + "slot_locked.png", "style" : ("not_pick",), },
			{ "name" : "petSkillPlus0", "type" : "button", "x" : 39,  "y" : 339, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_hover.png", "down_image" : SR + "levelup_down.png", },
			{ "name" : "petSkillPlus1", "type" : "button", "x" : 77,  "y" : 339, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_hover.png", "down_image" : SR + "levelup_down.png", },
			{ "name" : "petSkillPlus2", "type" : "button", "x" : 115, "y" : 339, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_hover.png", "down_image" : SR + "levelup_down.png", },
			{ "name" : "petSkillPlus3", "type" : "button", "x" : 153, "y" : 339, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_hover.png", "down_image" : SR + "levelup_down.png", },
			{ "name" : "petSkillPlus4", "type" : "button", "x" : 191, "y" : 339, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_hover.png", "down_image" : SR + "levelup_down.png", },
			{ "name" : "petSkillPlus5", "type" : "button", "x" : 229, "y" : 339, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_hover.png", "down_image" : SR + "levelup_down.png", },
			### EMPTY-STATE NOTICE (pet page's own "no pet" line, centered on the duration strip;
			### RefreshPetPage shows it only while no pet is summoned and clears the duration text) ###
			{
				"name" : "petEmptyText", "type" : "text", "x" : 133, "y" : 140,
				"text" : localeinfo.COMPANION_PET_NO_PET, "outline" : 1, "color" : 0xFFcabdab,
				"text_horizontal_align" : "center", "text_vertical_align" : "center",
			},
		),
		},

		### RIDE PAGE (growth mount rework, client Task 7): buffi/pet-position parity -- same
		### background origin as petPage (rel = abs - (6,29)). CONVENTION: every ride-page widget
		### name MUST start with "ride" (uicompanion's page/empty-state logic keys on that prefix).
		### Server contract (Task 6; active flag added Task 9): BINARY_OnGrowthMountStatus(active,
		### level, exp, reqExp, gold, upMats, skillLevels, skillFails, skillChances, skillMats) --
		### reqExp==0 means max level, active==0 means the mount isn't summoned/ridden (rideEmptyText
		### shown, all other ride widgets hidden). Skill unlock levels 5/12/21/30, max skill level 8.
		### The 4 bonus rows (skill_value.png row art) are code-built, RTL-aware, in
		### uicompanion.__BuildRideBonusList inside rideBonusArea. ###
		{ "name" : "ridePage", "type" : "window", "x" : 6, "y" : 29, "width" : 267, "height" : 377,
		"children" :
		(
			### PORTRAIT (frame art reused from the pet page; static mount glyph inside) ###
			{ "name" : "ridePortraitFrame", "type" : "image", "x" : 4, "y" : 3, "image" : PATH + "pet_bg.png", },
			{ "name" : "ridePortraitIcon", "type" : "image", "x" : 214, "y" : 19, "image" : "icon/item/new/mount_voucher.png", "style" : ("not_pick",), },
			### Live equipped-mount icon (costume / skin), toggled with ridePortraitIcon in
			### uicompanion.__RefreshRidePortrait -- SlotWindow so a real item vnum icon can load
			### (an image widget can't), same shape as the ride dialogs' materialSlot. ###
			{ "name" : "ridePortraitSlot", "type" : "slot", "x" : 214, "y" : 19, "width" : 32, "height" : 32,
				"slot" : ( { "index" : 0, "x" : 0, "y" : 0, "width" : 32, "height" : 32 }, ),
			},
			### NAME / LEVEL / UNLOCKED-SKILLS rows (same geometry as the pet Name/Type/Level rows) ###
			{
				"name" : "rideNameTitle", "type" : "image", "x" : 69, "y" : 3, "image" : PATH + "detail_title.png",
				"children" : ( { "name" : "rideName_text", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : localeinfo.COMPANION_NAME, "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "rideNameValue", "type" : "image", "x" : 162, "y" : 3, "image" : PATH + "detail_value.png",
				"children" : ( { "name" : "rideName_text_value", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : "", "color" : 0xFFd1b183,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "rideLevelTitle", "type" : "image", "x" : 69, "y" : 25, "image" : PATH + "detail_title.png",
				"children" : ( { "name" : "rideLevel_text", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : localeinfo.GROWTH_MOUNT_LEVEL, "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "rideLevelValue", "type" : "image", "x" : 162, "y" : 25, "image" : PATH + "detail_value.png",
				"children" : ( { "name" : "rideLevel_text_value", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : "", "color" : 0xFFd1b183,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "rideSkillsTitle", "type" : "image", "x" : 69, "y" : 47, "image" : PATH + "detail_title.png",
				"children" : ( { "name" : "rideSkills_text", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : getattr(localeinfo, "GROWTH_MOUNT_SKILLS", "Skills"), "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "rideSkillsValue", "type" : "image", "x" : 162, "y" : 47, "image" : PATH + "detail_value.png",
				"children" : ( { "name" : "rideSkills_text_value", "type" : "text", "outline" : 1, "x" : 48, "y" : 10,
					"text" : "", "color" : 0xFFd1b183,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			### EXPERIENCE: subheader + Upgrade button (pet upgrade-button art), then the SAME level
			### progress twice, side by side -- gauge (render-LEFT, pet lifetime-gauge art) + the 4
			### orbs (render-RIGHT, buffi orb art) -- both driven from exp/reqExp by RefreshRidePage.
			### Fill layers start zero-clipped in code, exactly like the buffi/pet pages. ###
			{
				"name" : "rideExpHeader", "type" : "image", "x" : 2, "y" : 72, "image" : PATH + "subheader_bg.png",
				"children" : ( { "name" : "rideExpHeader_text", "type" : "text", "outline" : 1, "x" : 66, "y" : 6,
					"text" : localeinfo.GROWTH_MOUNT_EXP, "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", }, ),
			},
			### LEVELING HELP "?" (opens the level-browser explainer, mode 0). Declared AFTER
			### the header so it renders on top; low x mirrors clear in RTL (petExpHelpButton
			### precedent). Kept visible by the __ApplyRideEmptyState keep-set. ###
			{
				"name" : "rideExpHelpButton",
				"type" : "button",
				"x" : 8,
				"y" : 75,
				"default_image" : "spin_wheel/question_mark.png",
				"over_image"    : "spin_wheel/question_mark_1.png",
				"down_image"    : "spin_wheel/question_mark_2.png",
			},
			{
				"name" : "rideUpgradeButton", "type" : "button", "x" : 132, "y" : 72,
				"text" : localeinfo.GROWTH_MOUNT_UPGRADE, "text_outline" : 1, "text_color" : 0xFFcabdab,
				"default_image" : PATH + "btn_refine_norm.png",
				"over_image"    : PATH + "btn_refine_hover.png",
				"down_image"    : PATH + "btn_refine_select.png",
			},
			{ "name" : "rideExpGaugeBg",   "type" : "image",          "x" : 5, "y" : 116, "image" : PATH + "gauge_empty.png", },
			{ "name" : "rideExpGaugeFill", "type" : "expanded_image", "x" : 7, "y" : 118, "image" : PATH + "gauge_full.png", },
			{
				"name" : "rideExpText", "type" : "text", "x" : 64, "y" : 142,
				"text" : "", "outline" : 1, "color" : 0xFFcabdab,
				"text_horizontal_align" : "center", "text_vertical_align" : "center",
			},
			{ "name" : "rideExpBg", "type" : "image", "x" : 134, "y" : 106, "image" : PATH + "detail_exp_bg.png", },
			{ "name" : "rideExpBallBg0", "type" : "image", "x" : 143, "y" : 112, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
			{ "name" : "rideExpBallBg1", "type" : "image", "x" : 170, "y" : 112, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
			{ "name" : "rideExpBallBg2", "type" : "image", "x" : 197, "y" : 112, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
			{ "name" : "rideExpBallBg3", "type" : "image", "x" : 224, "y" : 112, "image" : PATH + "progress_empty.png", "style" : ("not_pick",), },
			{ "name" : "rideExpBall0", "type" : "expanded_image", "x" : 143, "y" : 112, "image" : PATH + "progress.png", "style" : ("not_pick",), },
			{ "name" : "rideExpBall1", "type" : "expanded_image", "x" : 170, "y" : 112, "image" : PATH + "progress.png", "style" : ("not_pick",), },
			{ "name" : "rideExpBall2", "type" : "expanded_image", "x" : 197, "y" : 112, "image" : PATH + "progress.png", "style" : ("not_pick",), },
			{ "name" : "rideExpBall3", "type" : "expanded_image", "x" : 224, "y" : 112, "image" : PATH + "progress.png", "style" : ("not_pick",), },
			### EXP hover pick-targets (gauge + ball cluster), same idiom as the pet page's petExpHover:
			### plain pickable windows sitting on top, bound in uicompanion to an EXP-state tooltip. ###
			{ "name" : "rideExpGaugeHover", "type" : "window", "x" : 5,   "y" : 116, "width" : 119, "height" : 30 },
			{ "name" : "rideExpBallHover",  "type" : "window", "x" : 135, "y" : 109, "width" : 128, "height" : 32 },
			### BONUSES: section header + a container the 4 skill-bonus rows are code-built into
			### (skill_value.png row art, label + value cell -- the buffi bonus-list anatomy). ###
			{
				"name" : "rideBonusHeader", "type" : "image", "x" : 2, "y" : 150, "image" : PATH + "header_title.png",
				"children" : ( { "name" : "rideBonusHeader_text", "type" : "text", "outline" : 1, "x" : 129, "y" : 15,
					"text" : getattr(localeinfo, "GROWTH_MOUNT_BONUSES", "Bonuses"), "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{ "name" : "rideBonusArea", "type" : "window", "x" : 5, "y" : 181, "width" : 257, "height" : 104 },
			### SKILLS: 4 slot_skill slots on the pet-skill strip, each a static glyph
			### (icon/item/item_mount/skill_1..4.png), a slot_locked overlay while below the unlock
			### level and a "+" that opens the skill-upgrade dialog once unlocked. ###
			{
				"name" : "rideSkillsHeader", "type" : "image", "x" : 2, "y" : 293, "image" : PATH + "header_title.png",
				"children" : ( { "name" : "rideSkillsHeader_text", "type" : "text", "outline" : 1, "x" : 129, "y" : 15,
					"text" : localeinfo.COMPANION_PET_SKILLS, "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			### SKILLS HELP "?" (opens the skill-browser explainer, mode 1). Same anatomy as
			### rideExpHelpButton; kept visible by the __ApplyRideEmptyState keep-set. ###
			{
				"name" : "rideSkillHelpButton",
				"type" : "button",
				"x" : 8,
				"y" : 301,
				"default_image" : "spin_wheel/question_mark.png",
				"over_image"    : "spin_wheel/question_mark_1.png",
				"down_image"    : "spin_wheel/question_mark_2.png",
			},
			{ "name" : "rideSkillsBg", "type" : "image", "x" : 3, "y" : 323, "image" : PATH + "skill_pet_bg.png", },
			{ "name" : "rideSkillBg0", "type" : "image", "x" : 22,  "y" : 325, "image" : PATH + "slot_skill.png", },
			{ "name" : "rideSkillBg1", "type" : "image", "x" : 80,  "y" : 325, "image" : PATH + "slot_skill.png", },
			{ "name" : "rideSkillBg2", "type" : "image", "x" : 138, "y" : 325, "image" : PATH + "slot_skill.png", },
			{ "name" : "rideSkillBg3", "type" : "image", "x" : 196, "y" : 325, "image" : PATH + "slot_skill.png", },
			{ "name" : "rideSkillIcon0", "type" : "image", "x" : 26,  "y" : 329, "image" : "icon/item/item_mount/skill_1.png", "style" : ("not_pick",), },
			{ "name" : "rideSkillIcon1", "type" : "image", "x" : 84,  "y" : 329, "image" : "icon/item/item_mount/skill_2.png", "style" : ("not_pick",), },
			{ "name" : "rideSkillIcon2", "type" : "image", "x" : 142, "y" : 329, "image" : "icon/item/item_mount/skill_3.png", "style" : ("not_pick",), },
			{ "name" : "rideSkillIcon3", "type" : "image", "x" : 200, "y" : 329, "image" : "icon/item/item_mount/skill_4.png", "style" : ("not_pick",), },
			{ "name" : "rideSkillLock0", "type" : "image", "x" : 26,  "y" : 329, "image" : PATH + "slot_locked.png", "style" : ("not_pick",), },
			{ "name" : "rideSkillLock1", "type" : "image", "x" : 84,  "y" : 329, "image" : PATH + "slot_locked.png", "style" : ("not_pick",), },
			{ "name" : "rideSkillLock2", "type" : "image", "x" : 142, "y" : 329, "image" : PATH + "slot_locked.png", "style" : ("not_pick",), },
			{ "name" : "rideSkillLock3", "type" : "image", "x" : 200, "y" : 329, "image" : PATH + "slot_locked.png", "style" : ("not_pick",), },
			### SKILL hover pick-targets: one per slot, covering icon + lock overlay (both not_pick).
			### Bound per-index in uicompanion (SetOverInEvent Pattern B) -> locked/unlocked tooltip. ###
			{ "name" : "rideSkillHover0", "type" : "window", "x" : 22,  "y" : 325, "width" : 40, "height" : 40 },
			{ "name" : "rideSkillHover1", "type" : "window", "x" : 80,  "y" : 325, "width" : 40, "height" : 40 },
			{ "name" : "rideSkillHover2", "type" : "window", "x" : 138, "y" : 325, "width" : 40, "height" : 40 },
			{ "name" : "rideSkillHover3", "type" : "window", "x" : 196, "y" : 325, "width" : 40, "height" : 40 },
			{ "name" : "rideSkillPlus0", "type" : "button", "x" : 50,  "y" : 352, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_hover.png", "down_image" : SR + "levelup_down.png", },
			{ "name" : "rideSkillPlus1", "type" : "button", "x" : 108, "y" : 352, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_hover.png", "down_image" : SR + "levelup_down.png", },
			{ "name" : "rideSkillPlus2", "type" : "button", "x" : 166, "y" : 352, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_hover.png", "down_image" : SR + "levelup_down.png", },
			{ "name" : "rideSkillPlus3", "type" : "button", "x" : 224, "y" : 352, "default_image" : SR + "levelup_normal.png", "over_image" : SR + "levelup_hover.png", "down_image" : SR + "levelup_down.png", },
			### EMPTY-STATE NOTICE (mount-called gate, Task 9): the ride page's own "call your
			### mount" line, centered over the page; RefreshRidePage/__ApplyRideEmptyState show it
			### only while the mount isn't summoned/ridden and hide every other ride widget. ###
			{
				"name" : "rideEmptyText", "type" : "text", "x" : 133, "y" : 180,
				"text" : getattr(localeinfo, "GROWTH_MOUNT_CALL_PROMPT", "Summon your mount to manage it."),
				"outline" : 1, "color" : 0xFFcabdab,
				"text_horizontal_align" : "center", "text_vertical_align" : "center",
			},
		),
		},

		),
		},

	),
}
