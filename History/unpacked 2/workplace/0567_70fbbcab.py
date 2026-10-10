# coding: latin_1
#
# Gear Sets (ENABLE_GEAR_SETS) window layout - new_fast_equip skin.
# Layout: equipment paper-doll panels on the LEFT (page1 = main gear, page2 = costume/special),
#         set page list on the RIGHT (10 sets, 8 rows visible, mousewheel for the last 2).
# Rows + rename pencils are created dynamically in uifastequip.py (parented to "thinboard_presets").
#
# NOTE: the slot x/y below are FIRST-PASS estimates of where the frames sit inside page1.png /
# page2.png and will need a quick in-client tune. The slot INDICES (CHANGE_EQUIP_START_INDEX + wear
# cell) are correct and must not change - the link/equip logic keys off them.

import uiscriptlocale

ART = "d:/ymir work/ui/game/new_fast_equip/"

WINDOW_X = 494
WINDOW_Y = 288

# left equipment panel (bg_right.png = 323x250)
EQUIP_X = 11
EQUIP_Y = 30
# right page-list panel (bg_left.png = 138x250)
PAGE_X = 11 + 323 + 8
PAGE_Y = 30

window = {
	"name":"FastEquipWindows",
	"x":SCREEN_WIDTH/2-(WINDOW_X/2),
	"y":SCREEN_HEIGHT/2-(WINDOW_Y/2),
	"style":("movable","float"),
	"width":WINDOW_X,
	"height":WINDOW_Y,
	"children":
	(
		{
			"name":"board",
			"type":"board",
			"x":0,
			"y":0,
			"width":WINDOW_X,
			"height":WINDOW_Y,
			"children":
			(
				{
					"name":"TitleBar",
					"type":"titlebar",
					"x":8,
					"y":7,
					"width":WINDOW_X-15,
					"color":"yellow",
					"children":
					(
						{
							"name":"TitleName", "type":"text",
							"x":WINDOW_X/2, "y":3,
							"text":uiscriptlocale.FAST_EQUIPMENT_CHANGE_TITLE,
							"text_horizontal_align":"center"
						},
					),
				},

				# ---------------- LEFT: equipment panels ----------------
				{
					"name":"equip_bg",
					"type":"image",
					"x":EQUIP_X, "y":EQUIP_Y,
					"image":ART + "bg_right.png",
					"children":
					(
						{ "name":"page1_img", "type":"image", "x":163,   "y":8, "image":ART + "page1.png" },
						{ "name":"page2_img", "type":"image", "x":4, "y":8, "image":ART + "page2.png" },
						{
							# ONE slot widget overlays BOTH page1 (x 4..159) and page2 (x 163..318).
							"name":"Equipament",
							"type":"slot",
							"x":4, "y":8,
							"width":314, "height":187,
							"slot":
							(
								# --- page1: main equipment ---
								# Weapon
								{"index":CHANGE_EQUIP_START_INDEX+4,  "x":6,   "y":4,   "width":32, "height":96},
								# Helm
								{"index":CHANGE_EQUIP_START_INDEX+1,  "x":44,  "y":4,   "width":32, "height":32},
								# Armor (body)
								{"index":CHANGE_EQUIP_START_INDEX+0,  "x":44,  "y":40,  "width":32, "height":64},
								# Shoes
								{"index":CHANGE_EQUIP_START_INDEX+2,  "x":45,  "y":148, "width":32, "height":32},
								# Bracelet (wrist)
								{"index":CHANGE_EQUIP_START_INDEX+3,  "x":81,  "y":70,   "width":32, "height":32},
								# Necklace
								{"index":CHANGE_EQUIP_START_INDEX+5,  "x":117,  "y":69,  "width":32, "height":32},
								# Earrings
								{"index":CHANGE_EQUIP_START_INDEX+6,  "x":119,  "y":38,  "width":32, "height":32},
								# Shield
								{"index":CHANGE_EQUIP_START_INDEX+10, "x":81,  "y":39, "width":32, "height":32},
								# Belt
								{"index":CHANGE_EQUIP_START_INDEX+26, "x":44, "y":110,   "width":32, "height":32},
								# Glove
								{"index":CHANGE_EQUIP_START_INDEX+35, "x":119, "y":5,  "width":32, "height":32},

								# --- page2: costume / special (x offset ~159) ---
								# Body costume
								{"index":CHANGE_EQUIP_START_INDEX+19, "x":249, "y":50,   "width":32, "height":64},
								# Weapon costume
								{"index":CHANGE_EQUIP_START_INDEX+23, "x":196, "y":17,   "width":32, "height":96},
								# Hair costume
								{"index":CHANGE_EQUIP_START_INDEX+20, "x":248, "y":19,  "width":32, "height":32},
								# Sash
								{"index":CHANGE_EQUIP_START_INDEX+22, "x":81, "y":5, "width":32, "height":32},
								# Aura
								{"index":CHANGE_EQUIP_START_INDEX+36, "x":5, "y":111,   "width":32, "height":32},
							),
						},
					),
				},

				# Equip + Get-Token(stub) buttons, under the equipment panels
				{
					"name":"Change_Equipament",
					"type":"button",
					"x":EQUIP_X + 30, "y":245,
					"text":uiscriptlocale.FASTEQ_CHANGE,
					"default_image":ART + "btn_norm.png",
					"over_image":ART + "btn_hover.png",
					"down_image":ART + "btn_select.png",
				},
				{
					"name":"GetTokenButton",
					"type":"button",
					"x":EQUIP_X + 168, "y":245,
					"text":uiscriptlocale.FASTEQ_GET_TOKEN,
					"default_image":ART + "btn_norm.png",
					"over_image":ART + "btn_hover.png",
					"down_image":ART + "btn_select.png",
				},

				# ---------------- RIGHT: set page list ----------------
				{
					# page rows + rename pencils are created dynamically in uifastequip.py (parented here).
					"name":"thinboard_presets",
					"type":"image",
					"x":PAGE_X, "y":PAGE_Y,
					"image":ART + "bg_left.png",
				},
			),
		},
	),
}
