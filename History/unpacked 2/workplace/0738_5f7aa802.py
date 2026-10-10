# coding: latin_1
#
# Pet "Upgrade" sub-window layout (growth pet rework, U3).
# Opened by the Companion pet page's Upgrade button. A left tab rail (Evolve /
# Upgrade Type) + two page containers sharing the buffi evolve-window art -- the
# same rail-outside-the-board pattern as the Companion window itself.
# uipetupgrade.py binds the widgets, wires the events and owns ALL page/tab
# visibility -- both pages ship visible here; the binder resolves them.
#
# RTL note: every image row is laid out SYMMETRIC about the content center
# (x=104) so the Arabic mirror maps frames onto each other; the count boxes are
# declared at the MIRROR of their slot column (SlotWindow icons do not mirror,
# plain images do -- see companionupgradewindow.py for the original note).
import localeinfo
CONTENT_WIDTH = 208              # body width (matches the buffi Upgrade window)
RAIL_W        = 36               # left page-tab rail column (36x36 buttons)
WINDOW_WIDTH  = RAIL_W + CONTENT_WIDTH
WINDOW_HEIGHT = 250              # pity strip ends y241 -> 9px clearance off the board's bottom border
PATH = "d:/ymir work/ui/game/companion/evolve/"
SR   = "d:/ymir work/ui/game/companion/"
window = {
	"name"   : "PetUpgradeWindow",
	"x"      : 0,
	"y"      : 0,
	"style"  : ("movable", "float",),
	"width"  : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,
	"children" :
	(
		### PAGE TAB RAIL (left column): Evolve / Upgrade Type. radio_buttons so the active
		### tab stays pressed; wired in uipetupgrade. RTL mirrors the rail to the right edge.
		### Tab icons: btn_up2 = Evolve, btn_up1 = Upgrade Type. ###
		{
			"name" : "tabEvolve",
			"type" : "radio_button",
			"x" : 5,
			"y" : 31,
			"default_image" : SR + "btn_up2_norm.png",
			"over_image"    : SR + "btn_up2_hover.png",
			"down_image"    : SR + "btn_up2_select.png",
		},
		{
			"name" : "tabType",
			"type" : "radio_button",
			"x" : 5,
			"y" : 65,
			"default_image" : SR + "btn_up1_norm.png",
			"over_image"    : SR + "btn_up1_hover.png",
			"down_image"    : SR + "btn_up1_select.png",
		},
		### CONTENT WRAPPER (board + both pages; original coordinates, rail-shifted) ###
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
		### ================= EVOLVE PAGE =================
		### Header (evolution N -> N+1), 5 material columns, requirement strip, Evolve button.
		### not_pick: the full-size page containers must not swallow clicks meant for the
		### titlebar underneath (drag-to-move / close) -- children are still picked normally.
		{
		"name" : "evolvePage", "type" : "window", "x" : 0, "y" : 0, "width" : CONTENT_WIDTH, "height" : WINDOW_HEIGHT, "style" : ("not_pick",),
		"children" :
		(
			{ "name" : "evoPanelBg", "type" : "image", "x" : 3, "y" : 54, "image" : PATH + "background2.png", "style" : ("not_pick",), },
			{
				"name"  : "evoHeader", "type" : "image", "x" : 3, "y" : 27, "image" : PATH + "header_bg.png",
				"children" : ( { "name" : "evoHeaderText", "type" : "text", "outline" : 1, "x" : 101, "y" : 17,
					"text" : "", "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{ "name" : "evoMatBg0", "type" : "image", "x" : 11,  "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
			{ "name" : "evoMatBg1", "type" : "image", "x" : 49,  "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
			{ "name" : "evoMatBg2", "type" : "image", "x" : 87,  "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
			{ "name" : "evoMatBg3", "type" : "image", "x" : 125, "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
			{ "name" : "evoMatBg4", "type" : "image", "x" : 163, "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
			{
				"name" : "evoMaterialSlot", "type" : "slot", "x" : 0, "y" : 72, "width" : 208, "height" : 40,
				"slot" : (
					{ "index" : 0, "x" : 13,  "y" : 2, "width" : 32, "height" : 32 },
					{ "index" : 1, "x" : 51,  "y" : 2, "width" : 32, "height" : 32 },
					{ "index" : 2, "x" : 89,  "y" : 2, "width" : 32, "height" : 32 },
					{ "index" : 3, "x" : 127, "y" : 2, "width" : 32, "height" : 32 },
					{ "index" : 4, "x" : 165, "y" : 2, "width" : 32, "height" : 32 },
				),
			},
			### Count boxes at the MIRROR of their slot column (159 - 38*i) -- see RTL note above.
			{ "name" : "evoMatCountBg0", "type" : "image", "x" : 159, "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
				"children" : ( { "name" : "evoMatCount0", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
			{ "name" : "evoMatCountBg1", "type" : "image", "x" : 121, "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
				"children" : ( { "name" : "evoMatCount1", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
			{ "name" : "evoMatCountBg2", "type" : "image", "x" : 83,  "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
				"children" : ( { "name" : "evoMatCount2", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
			{ "name" : "evoMatCountBg3", "type" : "image", "x" : 45,  "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
				"children" : ( { "name" : "evoMatCount3", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
			{ "name" : "evoMatCountBg4", "type" : "image", "x" : 7,   "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
				"children" : ( { "name" : "evoMatCount4", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
			### Requirement strip: "Requires Pet Lv. X" (or the final-evolution notice) ###
			{
				"name"  : "evoReqBg", "type" : "image", "x" : 12, "y" : 140, "image" : PATH + "cost_title_bg.png",
				"children" : ( { "name" : "evoReqText", "type" : "text", "outline" : 1, "x" : 92, "y" : 10,
					"text" : "", "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "evoAcceptButton", "type" : "button", "x" : 38, "y" : 170,
				"text" : localeinfo.COMPANION_EVOLVE, "text_outline" : 1, "text_color" : 0xFFcabdab,
				"default_image" : SR + "btn_evolve_norm.png",
				"over_image"    : SR + "btn_evolve_hover.png",
				"down_image"    : SR + "btn_evolve_select.png",
			},
		),
		},
		### ================= UPGRADE TYPE PAGE =================
		### Header (Type N -> N+1 + stat-cap change), 5 material columns, chance strip,
		### Yang strip, Confirm button, pity strip.
		{
		"name" : "typePage", "type" : "window", "x" : 0, "y" : 0, "width" : CONTENT_WIDTH, "height" : WINDOW_HEIGHT, "style" : ("not_pick",),
		"children" :
		(
			{ "name" : "typPanelBg", "type" : "image", "x" : 3, "y" : 54, "image" : PATH + "background2.png", "style" : ("not_pick",), },
			{
				"name"  : "typHeader", "type" : "image", "x" : 3, "y" : 27, "image" : PATH + "header_bg.png",
				"children" : (
					{ "name" : "typHeaderText", "type" : "text", "outline" : 1, "x" : 101, "y" : 17,
						"text" : "", "color" : 0xFFcabdab,
						"text_horizontal_align" : "center", "text_vertical_align" : "center", },
					# >>> SECTION BEGIN: cap line moved into the strip below (user feedback 2026-07-04 --
					# two lines crowded the 34px header; the strip now always shows the cap change).
					# { "name" : "typCapText", "type" : "text", "outline" : 1, "x" : 101, "y" : 25,
					# 	"text" : "", "color" : 0xFFd1b183,
					# 	"text_horizontal_align" : "center", "text_vertical_align" : "center", },
					# <<< SECTION END
				),
			},
			{ "name" : "typMatBg0", "type" : "image", "x" : 11,  "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
			{ "name" : "typMatBg1", "type" : "image", "x" : 49,  "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
			{ "name" : "typMatBg2", "type" : "image", "x" : 87,  "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
			{ "name" : "typMatBg3", "type" : "image", "x" : 125, "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
			{ "name" : "typMatBg4", "type" : "image", "x" : 163, "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
			{
				"name" : "typMaterialSlot", "type" : "slot", "x" : 0, "y" : 72, "width" : 208, "height" : 40,
				"slot" : (
					{ "index" : 0, "x" : 13,  "y" : 2, "width" : 32, "height" : 32 },
					{ "index" : 1, "x" : 51,  "y" : 2, "width" : 32, "height" : 32 },
					{ "index" : 2, "x" : 89,  "y" : 2, "width" : 32, "height" : 32 },
					{ "index" : 3, "x" : 127, "y" : 2, "width" : 32, "height" : 32 },
					{ "index" : 4, "x" : 165, "y" : 2, "width" : 32, "height" : 32 },
				),
			},
			### Count boxes at the MIRROR of their slot column (159 - 38*i) -- see RTL note above.
			{ "name" : "typMatCountBg0", "type" : "image", "x" : 159, "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
				"children" : ( { "name" : "typMatCount0", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
			{ "name" : "typMatCountBg1", "type" : "image", "x" : 121, "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
				"children" : ( { "name" : "typMatCount1", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
			{ "name" : "typMatCountBg2", "type" : "image", "x" : 83,  "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
				"children" : ( { "name" : "typMatCount2", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
			{ "name" : "typMatCountBg3", "type" : "image", "x" : 45,  "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
				"children" : ( { "name" : "typMatCount3", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
			{ "name" : "typMatCountBg4", "type" : "image", "x" : 7,   "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
				"children" : ( { "name" : "typMatCount4", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
			### Success chance (or the evolve-first / maxed notice) ###
			{
				"name"  : "typChanceBg", "type" : "image", "x" : 12, "y" : 138, "image" : PATH + "bg_chance_success.png",
				"children" : ( { "name" : "typChanceText", "type" : "text", "outline" : 1, "x" : 92, "y" : 10,
					"text" : "", "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			### Yang price ###
			{
				"name"  : "typGoldBg", "type" : "image", "x" : 12, "y" : 162, "image" : PATH + "cost_title_bg.png",
				"children" : ( { "name" : "typPriceText", "type" : "text", "outline" : 1, "x" : 92, "y" : 10,
					"text" : "", "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
			{
				"name" : "typAcceptButton", "type" : "button", "x" : 38, "y" : 186,
				"text" : localeinfo.COMPANION_PET_UPGRADE, "text_outline" : 1, "text_color" : 0xFFcabdab,
				"default_image" : SR + "btn_evolve_norm.png",
				"over_image"    : SR + "btn_evolve_hover.png",
				"down_image"    : SR + "btn_evolve_select.png",
			},
			### Pity: "Failure before 100%: N / 3" ###
			{
				"name"  : "typPityBg", "type" : "image", "x" : 12, "y" : 221, "image" : PATH + "cost_title_bg.png",
				"children" : ( { "name" : "typPityText", "type" : "text", "outline" : 1, "x" : 92, "y" : 10,
					"text" : "", "color" : 0xFFcabdab,
					"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
			},
		),
		},
		### "?" -> the Upgrade explainer popup (uipetupgradehelp). Declared AFTER the
		### pages so it draws above them on the titlebar; low x so the RTL mirror keeps
		### it clear of the close button on both sides (companion helpButton pattern).
		{
			"name" : "helpButton",
			"type" : "button",
			"x" : 10,
			"y" : 9,
			"default_image" : "spin_wheel/question_mark.png",
			"over_image"    : "spin_wheel/question_mark_1.png",
			"down_image"    : "spin_wheel/question_mark_2.png",
		},
		),
		},
	),
}
