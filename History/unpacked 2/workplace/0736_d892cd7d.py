# coding: latin_1
#
# Pet "Skill Upgrade" dialog layout (growth pet rework, U4).
# Opened by a skill slot's "+" on the Companion pet page. One page, no tab rail:
# header (skill name + Lv N -> N+1), 4 material columns, Yang strip, Confirm.
# Upgrades are NO-FAIL (server ladder); the visible costs ARE the confirmation.
# uipetupgrade.PetSkillUpgradeDialog binds the widgets and fills the rows.
#
# RTL note: the 4 material frames are symmetric about the content center (x=104)
# and the count boxes are declared at the MIRROR of their slot column (141-38i) --
# SlotWindow icons do not RTL-mirror, plain images do (companionupgradewindow.py).
import localeinfo
WINDOW_WIDTH  = 208
WINDOW_HEIGHT = 212
PATH = "d:/ymir work/ui/game/companion/evolve/"
SR   = "d:/ymir work/ui/game/companion/"
window = {
	"name"   : "PetSkillUpgradeWindow",
	"x"      : 0,
	"y"      : 0,
	"style"  : ("movable", "float",),
	"width"  : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,
	"children" :
	(
		{
			"name"   : "board",
			"type"   : "board_with_titlebar",
			"x"      : 0,
			"y"      : 0,
			"width"  : WINDOW_WIDTH,
			"height" : WINDOW_HEIGHT,
			"title"  : "",
		},
		### background.png (202x156, ends y210) -- background2.png is 190 tall and would hang
		### 32px below this 212 board; to use it instead, bump WINDOW_HEIGHT to 250. ###
		{ "name" : "panelBg", "type" : "image", "x" : 3, "y" : 54, "image" : PATH + "background.png", "style" : ("not_pick",), },
		### Header: "<skill name>  Lv N -> N+1" (or the max-level notice) ###
		{
			"name"  : "header", "type" : "image", "x" : 3, "y" : 27, "image" : PATH + "header_bg.png",
			"children" : ( { "name" : "headerText", "type" : "text", "outline" : 1, "x" : 101, "y" : 17,
				"text" : "", "color" : 0xFFcabdab,
				"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
		},
		{ "name" : "matBg0", "type" : "image", "x" : 29,  "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
		{ "name" : "matBg1", "type" : "image", "x" : 67,  "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
		{ "name" : "matBg2", "type" : "image", "x" : 105, "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
		{ "name" : "matBg3", "type" : "image", "x" : 143, "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
		{
			"name" : "materialSlot", "type" : "slot", "x" : 0, "y" : 72, "width" : 208, "height" : 40,
			"slot" : (
				{ "index" : 0, "x" : 31,  "y" : 2, "width" : 32, "height" : 32 },
				{ "index" : 1, "x" : 69,  "y" : 2, "width" : 32, "height" : 32 },
				{ "index" : 2, "x" : 107, "y" : 2, "width" : 32, "height" : 32 },
				{ "index" : 3, "x" : 145, "y" : 2, "width" : 32, "height" : 32 },
			),
		},
		### Count boxes at the MIRROR of their slot column (141 - 38*i) -- see RTL note above.
		{ "name" : "matCountBg0", "type" : "image", "x" : 141, "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
			"children" : ( { "name" : "matCount0", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
		{ "name" : "matCountBg1", "type" : "image", "x" : 103, "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
			"children" : ( { "name" : "matCount1", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
		{ "name" : "matCountBg2", "type" : "image", "x" : 65,  "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
			"children" : ( { "name" : "matCount2", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
		{ "name" : "matCountBg3", "type" : "image", "x" : 27,  "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
			"children" : ( { "name" : "matCount3", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
		### Yang price ###
		{
			"name"  : "goldBg", "type" : "image", "x" : 12, "y" : 140, "image" : PATH + "cost_title_bg.png",
			"children" : ( { "name" : "priceText", "type" : "text", "outline" : 1, "x" : 92, "y" : 10,
				"text" : "", "color" : 0xFFcabdab,
				"text_horizontal_align" : "center", "text_vertical_align" : "center", }, ),
		},
		{
			"name" : "acceptButton", "type" : "button", "x" : 38, "y" : 168,
			"text" : localeinfo.COMPANION_PET_UPGRADE, "text_outline" : 1, "text_color" : 0xFFcabdab,
			"default_image" : SR + "btn_evolve_norm.png",
			"over_image"    : SR + "btn_evolve_hover.png",
			"down_image"    : SR + "btn_evolve_select.png",
		},
	),
}
