# coding: latin_1
#
# Companion "Upgrade Type" (Evolve) sub-window layout.
# Skeleton only: board_with_titlebar chrome + the header strip + the main panel bg.
# The requirement rows / item slots / yang / confirm button get placed on top of
# these later. uicompanionupgrade.py binds the widgets (GetChild) + wires events.
import localeinfo
WINDOW_WIDTH  = 208
WINDOW_HEIGHT = 230
PATH = "d:/ymir work/ui/game/companion/evolve/"
SR = "d:/ymir work/ui/game/companion/"
window = {
	"name"   : "CompanionUpgradeWindow",
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
		### HEADER STRIP (202x34) -- shows the INT the buffi will gain by evolving (current -> new) ####
		{
			"name"  : "header",
			"type"  : "image",
			"x"     : 3,
			"y"     : 27,
			"image" : PATH + "header_bg.png",
			#"style" : ("not_pick",),
			"children" :
			(
				{
					"name" : "newIntValue",
					"type" : "text",
					"outline" : 1,
					"x" : 101, "y" : 17,
					"text" : "",
					"color" : 0xFFcabdab,
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
			),
		},
		### MAIN PANEL BG (202x156) -- the middle area the requirement rows go on ####
		{
			"name"  : "background",
			"type"  : "image",
			"x"     : 3,
			"y"     : 54,
			"image" : PATH + "background.png",
			#"style" : ("not_pick",),
		},
		### REQUIREMENTS: 5 material columns (frame + count box) + a SlotWindow on top for the item icons.
		### Compact + centered: step 38 (36px frames -> 2px gap), row spans x10..198 leaving ~7px margins
		### each side of the 202px panel. Column centers: 28/66/104/142/180 (symmetric about 104). The count
		### text under each slot is colored green (player has enough) / red (not enough) by the binder.
		{ "name" : "matBg0", "type" : "image", "x" : 10,  "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
		{ "name" : "matBg1", "type" : "image", "x" : 48,  "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
		{ "name" : "matBg2", "type" : "image", "x" : 86,  "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
		{ "name" : "matBg3", "type" : "image", "x" : 124, "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
		{ "name" : "matBg4", "type" : "image", "x" : 162, "y" : 72, "image" : SR + "slot_runes.png", "style" : ("not_pick",), },
		{
			"name" : "materialSlot", "type" : "slot", "x" : 0, "y" : 72, "width" : 208, "height" : 40,
			"slot" : (
				{ "index" : 0, "x" : 12,  "y" : 2, "width" : 32, "height" : 32 },
				{ "index" : 1, "x" : 50,  "y" : 2, "width" : 32, "height" : 32 },
				{ "index" : 2, "x" : 88,  "y" : 2, "width" : 32, "height" : 32 },
				{ "index" : 3, "x" : 126, "y" : 2, "width" : 32, "height" : 32 },
				{ "index" : 4, "x" : 164, "y" : 2, "width" : 32, "height" : 32 },
			),
		},
		### Count boxes are declared in REVERSE x order vs the slot icons: a SlotWindow's slots are NOT
		### RTL-mirrored but plain images ARE, so a count box must be placed at the mirror of its slot's
		### column (160-38*i) to land under the right icon in the Arabic client. matCount{i} pairs with
		### material slot index i.
		{ "name" : "matCountBg0", "type" : "image", "x" : 160, "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
			"children" : ( { "name" : "matCount0", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
		{ "name" : "matCountBg1", "type" : "image", "x" : 122, "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
			"children" : ( { "name" : "matCount1", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
		{ "name" : "matCountBg2", "type" : "image", "x" : 84,  "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
			"children" : ( { "name" : "matCount2", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
		{ "name" : "matCountBg3", "type" : "image", "x" : 46,  "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
			"children" : ( { "name" : "matCount3", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
		{ "name" : "matCountBg4", "type" : "image", "x" : 8,   "y" : 110, "image" : PATH + "count_bg.png", "style" : ("not_pick",),
			"children" : ( { "name" : "matCount4", "type" : "text", "x" : 20, "y" : 11, "text" : "", "outline" : 1, "color" : 0xFFcabdab, "text_horizontal_align" : "center", "text_vertical_align" : "center", }, ), },
		{
			"name"  : "goldbg",
			"type"  : "image",
			"x"     : 11,
			"y"     : 146,
			"image" : PATH + "cost_title_bg.png",
			"children" :
			(
				{
					"name" : "priceValue",
					"type" : "text",
					"outline" : 1,
					"x" : 90, "y" : 9,
					"text" : "",
					"color" : 0xFFcabdab,
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
			),
		},
		{
			"name" : "evolveAcceptButton",
			"type" : "button",
			"x" : 38,
			"y" : 169,
			"text" : localeinfo.COMPANION_EVOLVE,
			"text_outline" : 1,
			"text_color" :  0xFFcabdab,
			"default_image" : SR + "btn_evolve_norm.png",
			"over_image"    : SR + "btn_evolve_hover.png",
			"down_image"    : SR + "btn_evolve_select.png",
		},
		{
			"name"  : "pitybg",
			"type"  : "image",
			"x"     : 11,
			"y"     : 202,
			"image" : PATH + "cost_title_bg.png",
			#"style" : ("not_pick",),
			"children" :
			(
				{
					"name" : "failValue",
					"type" : "text",
					"outline" : 1,
					"x" : 90, "y" : 11,
					"text" : "",
					"color" : 0xFFcabdab,
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
			),
		},
	),
}
