# coding: latin_1

import uiscriptlocale
import localeinfo
import constinfo

IMG_PATH = "d:/ymir work/ui/public/teleportpanel/"
TAB_IMG_PATH = "d:/ymir work/ui/public/teleportpanel/tab/"

GOLD_COLOR	= 0xFFFEE3AE

BOARD_WIDTH = 680
BOARD_HEIGT = 500

window = {
	"name" : "TeleportPanel",

	"x" : (SCREEN_WIDTH / 2) - (BOARD_WIDTH / 2),
	"y" : (SCREEN_HEIGHT / 2) - (BOARD_HEIGT / 2) ,

	"style" : ("movable", "float",),

	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGT,

	"children" :
	(
		{
			"name" : "board",
			"type" : "board_with_titlebar",

			"x" : 0,
			"y" : 0,

			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGT,
			"title" : uiscriptlocale.TELEPORT_PANEL_TITLE,
			"children" :
			(
				{
					"name" : "MapArea",
					"type" : "border_a",

					"x" : 15,
					"y" : 35 + 29,

					"width" : 450,
					"height" : BOARD_HEIGT - 50 - 29,
					"children" :
					(
						{ "name" : "MapList", "x" : 6, "y" : 7 , "width" : 424, "height" : 407 },
						{
							"name" : "ScrollBarBG", "type" : "bar", "x" : 16, "y" : 6, "width" : 11, "height" : 409, "horizontal_align" : "right",
							"color" : 0xFF0C0C0C,
							"children" :
							(
								{
									"name" : "ActiveScrollBar", "x" : 0, "y" : 0 , "width" : 11, "height" : 409,
									"children" :
									(
										{ "type" : "bar", "x" : 0, "y" : 0, "width" : 11, "height" : 409, "color" : 0xFF000000, },
										{ "type" : "bar", "x" : 1, "y" : 1, "width" : 9, "height" : 407, "color" : 0xFF6b655a, },
										{ "type" : "bar", "x" : 2, "y" : 2, "width" : 7, "height" : 405, "color" : 0xFF0c0c0c, },
										{ "name" : "ScrollBarPlace", "x" : 3, "y" : 3 , "width" : 5, "height" : 403 }
									),
								},
							),
						},
					),
				},
				
				## Info Area
				
				{
					"name" : "InfoArea",
					"type" : "border_a",

					"x" : 15 + 450 + 10,
					"y" : 35,

					"width" : 190,
					"height" : BOARD_HEIGT - 50,
					"children" :
					(
						{
							"name" : "Titlebar1", "type" : "image",
							"x" : 3, "y" : 3,
							"image" : IMG_PATH+"titlebar.sub",
							"children" :
							(
								{ "name" : "Titlebar1_Text", "type":"text", "x": 0, "y": -1, "text" : uiscriptlocale.TELEPORT_PANEL_INFO_TITLE, "color" : GOLD_COLOR, "all_align":"center", "outline" : 1},
							),
						},
						{
							"name" : "slider_picture_1", "type" : "image",
							"x" : 3, "y" : 24,
							"image" : IMG_PATH+"slider/picture_1.tga",
						},
						{
							"name" : "slider_picture_2", "type" : "image",
							"x" : 3, "y" : 24,
							"image" : IMG_PATH+"slider/picture_2.tga",
						},
						{
							"name" : "info_layer", "type" : "image",
							"x" : 3, "y" : 24,
							"image" : IMG_PATH+"info_layer.tga",
							"children" :
							(
								{ "name" : "text_info_boss", "type":"text", "x": 0, "y": 155, "text" : uiscriptlocale.TELEPORT_PANEL_INFO_BOSS, "color" : GOLD_COLOR, "horizontal_align":"center", "text_horizontal_align" : "center", "text_vertical_align" : "center", "outline" : 1},
								{ "name" : "text_info_minlv", "type":"text", "x": 0, "y": 170, "text" : uiscriptlocale.TELEPORT_PANEL_INFO_MINLV, "color" : GOLD_COLOR, "horizontal_align":"center", "text_horizontal_align" : "center", "text_vertical_align" : "center", "outline" : 1},
								{ "name" : "text_info_maxlv", "type":"text", "x": 0, "y": 185, "text" : uiscriptlocale.TELEPORT_PANEL_INFO_MAXLV, "color" : GOLD_COLOR, "horizontal_align":"center", "text_horizontal_align" : "center", "text_vertical_align" : "center", "outline" : 1},
								{ "name" : "text_info_cost", "type":"text", "x": 0, "y": 200, "text" : uiscriptlocale.TELEPORT_PANEL_INFO_COST, "color" : GOLD_COLOR, "horizontal_align":"center", "text_horizontal_align" : "center", "text_vertical_align" : "center", "outline" : 1},
								{ "name" : "text_info_required_item_desc", "type":"text", "x": 0, "y": 216, "text" : uiscriptlocale.TELEPORT_PANEL_INFO_ITEM_COST_DESC, "color" : GOLD_COLOR, "horizontal_align":"center", "text_horizontal_align" : "center", "text_vertical_align" : "center", "outline" : 1},
								{ "name" : "text_info_required_item_text", "type":"text", "x": 0, "y": 233, "text" : uiscriptlocale.TELEPORT_PANEL_INFO_ITEM_COST_TEXT, "horizontal_align":"center", "text_horizontal_align" : "center", "text_vertical_align" : "center", "outline" : 1},
								{
									"name" : "item_slot", "type" : "image", "x" : 75, "y" : 244,
									"image" : IMG_PATH+"item_slot.tga",
									"children" :
									(
										{
											"name" : "item_icon", "type" : "image", "x" : 3, "y" : 3,
										},
									),
								},
							),
						},
						{
							"name" : "Titlebar2", "type" : "image",
							"x" : 3, "y" : 309,
							"image" : IMG_PATH+"titlebar.sub",
							"children" :
							(
								{ "name" : "Titlebar2_Text", "type":"text", "x": 0, "y": -1, "text" : "", "color" : GOLD_COLOR, "all_align":"center", "outline" : 1},
							),
						},
					),
				},
			),
		},
	),
}

# if uiteleportpanel.TAB_COUNT == 3:
window["children"][0]["children"] = window["children"][0]["children"] + (
				{
					"name" : "TabArea", "x" : 15, "y" : 35 , "width" : 450, "height" : 32,
					"children" :
					(
						## Image
						{ "name" : "Tab_01", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_3_1.sub", },
						{ "name" : "Tab_02", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_3_2.sub", },
						{ "name" : "Tab_03", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_3_3.sub", },
						## RadioButton
						{ "name" : "Tab_Button_01", "type" : "radio_button", "x" : 303, "y" : 4, "width" : 144, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_1, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
						{ "name" : "Tab_Button_02", "type" : "radio_button", "x" : 154, "y" : 4, "width" : 143, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_2, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
						{ "name" : "Tab_Button_03", "type" : "radio_button", "x" : 4, "y" : 4, "width" : 143, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_3, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
					),
				},
			)



# if uiteleportpanel.TAB_COUNT == 4:
	# window["children"][0]["children"] = window["children"][0]["children"] + (
					# {
						# "name" : "TabArea", "x" : 15, "y" : 35 , "width" : 450, "height" : 32,
						# "children" :
						# (
							# ## Image
							# { "name" : "Tab_01", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_4_1.sub", },
							# { "name" : "Tab_02", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_4_2.sub", },
							# { "name" : "Tab_03", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_4_3.sub", },
							# { "name" : "Tab_04", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_4_4.sub", },
							# ## RadioButton
							# { "name" : "Tab_Button_01", "type" : "radio_button", "x" : 4, "y" : 4, "width" : 106, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_1, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_02", "type" : "radio_button", "x" : 116, "y" : 4, "width" : 106, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_2, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_03", "type" : "radio_button", "x" : 228, "y" : 4, "width" : 106, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_3, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_04", "type" : "radio_button", "x" : 340, "y" : 4, "width" : 106, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_4, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
						# ),
					# },
				# )
				


# if uiteleportpanel.TAB_COUNT == 5:
	# window["children"][0]["children"] = window["children"][0]["children"] + (
					# {
						# "name" : "TabArea", "x" : 15, "y" : 35 , "width" : 450, "height" : 32,
						# "children" :
						# (
							# ## Image
							# { "name" : "Tab_01", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_5_1.sub", },
							# { "name" : "Tab_02", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_5_2.sub", },
							# { "name" : "Tab_03", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_5_3.sub", },
							# { "name" : "Tab_04", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_5_4.sub", },
							# { "name" : "Tab_05", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_5_5.sub", },
							# ## RadioButton
							# { "name" : "Tab_Button_01", "type" : "radio_button", "x" : 4, "y" : 4, "width" : 84, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_1, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_02", "type" : "radio_button", "x" : 94, "y" : 4, "width" : 84, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_2, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_03", "type" : "radio_button", "x" : 184, "y" : 4, "width" : 83, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_3, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_04", "type" : "radio_button", "x" : 273, "y" : 4, "width" : 83, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_4, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_05", "type" : "radio_button", "x" : 362, "y" : 4, "width" : 84, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_5, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
						# ),
					# },
				# )



# if uiteleportpanel.TAB_COUNT == 6:
	# window["children"][0]["children"] = window["children"][0]["children"] + (
					# {
						# "name" : "TabArea", "x" : 15, "y" : 35 , "width" : 450, "height" : 32,
						# "children" :
						# (
							# ## Image
							# { "name" : "Tab_01", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_6_1.sub", },
							# { "name" : "Tab_02", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_6_2.sub", },
							# { "name" : "Tab_03", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_6_3.sub", },
							# { "name" : "Tab_04", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_6_4.sub", },
							# { "name" : "Tab_05", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_6_5.sub", },
							# { "name" : "Tab_06", "type" : "image", "x" : 0, "y" : 0, "image" : TAB_IMG_PATH+"tab_6_6.sub", },
							# ## RadioButton
							# { "name" : "Tab_Button_01", "type" : "radio_button", "x" : 4, "y" : 4, "width" : 69, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_1, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_02", "type" : "radio_button", "x" : 79, "y" : 4, "width" : 69, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_2, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_03", "type" : "radio_button", "x" : 154, "y" : 4, "width" : 69, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_3, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_04", "type" : "radio_button", "x" : 229, "y" : 4, "width" : 69, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_4, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_05", "type" : "radio_button", "x" : 304, "y" : 4, "width" : 66, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_5, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
							# { "name" : "Tab_Button_06", "type" : "radio_button", "x" : 376, "y" : 4, "width" : 70, "height" : 21, "text" : uiscriptlocale.TELEPORT_PANEL_TAB_NAME_6, "text_y" : -1, "text_outline" : 1, "text_fontsize":"LARGE" },
						# ),
					# },
				# )