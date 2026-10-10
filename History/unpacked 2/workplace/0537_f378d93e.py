# coding: latin_1
#
# Growth Mount "Level Up" sub-window layout (client Task 7).
# Cloned from companionupgradewindow.py's geometry (same board/header/background chrome,
# same 5-column material row) -- swap "INT gained" for "target level" in the header and
# drop the pity row (level-up is a flat gold+material cost, no gamble).
# uicompanionride.py binds the widgets (GetChild) + wires events.
import localeinfo
WINDOW_WIDTH  = 208
WINDOW_HEIGHT = 214
PATH = "d:/ymir work/ui/game/companion/evolve/"
SR = "d:/ymir work/ui/game/companion/"
window = {
	"name"   : "RideUpgradeWindow",
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
		### HEADER STRIP (202x34) -- shows the target level the mount will reach ####
		{
			"name"  : "header",
			"type"  : "image",
			"x"     : 3,
			"y"     : 27,
			"image" : PATH + "header_bg.png",
			"children" :
			(
				{
					"name" : "targetLevelValue",
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
		},
		### REQUIREMENTS: 5 material columns (frame + count box) + a SlotWindow on top for the item icons
		### (GROWTH_MOUNT_MAT_MAX = 5). Layout identical to companionupgradewindow.py's materialSlot. ####
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
		### Count boxes: REVERSE x order vs the slot icons (RTL mirror parity -- see companionupgradewindow.py). ####
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
			"name" : "rideUpgradeAcceptButton",
			"type" : "button",
			"x" : 38,
			"y" : 169,
			"text" : localeinfo.GROWTH_MOUNT_UPGRADE,
			"text_outline" : 1,
			"text_color" :  0xFFcabdab,
			"default_image" : SR + "btn_evolve_norm.png",
			"over_image"    : SR + "btn_evolve_hover.png",
			"down_image"    : SR + "btn_evolve_select.png",
		},
	),
}
