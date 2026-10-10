# coding: utf-8

import uiscriptlocale

BOARD_WIDTH = 300
BOARD_HEIGHT = 180

window = {
	"name" : "CapLevelDlg",
	"style" : ("movable", "float", "ltr",),
	"x" : 0,
	"y" : 0,
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	(
		{
			"name" : "ui_board",
			"type" : "board",
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"children" :
			(
				{
					"name" : "ui_titlebar",
					"type" : "titlebar",
					"style" : ("attach",),
					"x" : 6,
					"y" : 6,
					"width" : BOARD_WIDTH - 12,
					"color" : "yellow",
					"children" :
					(
						{
							"name" : "ui_titlename",
							"type" : "text",
							"x" : (BOARD_WIDTH - 12) / 2,
							"y" : 3,
							"text" : uiscriptlocale.DUNGEON_INFO_ADDON_LEVEL_TITLE,
							"text_horizontal_align" : "center"
						},
					),
				},
				{
					"name" : "ui_text1",
					"type" : "text",
					"x" : 0,
					"y" : 38,
					"text" : uiscriptlocale.DUNGEON_INFO_ADDON_LEVEL_CAP_MSG1,
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
				{
					"name" : "ui_text2",
					"type" : "text",
					"x" : 0,
					"y" : 58,
					"text" : uiscriptlocale.DUNGEON_INFO_ADDON_LEVEL_CAP_MSG2,
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
				{
					"name" : "ui_subboard",
					"type" : "thinboard_circle",
					"x" : 20,
					"y" : 72,
					"width" : BOARD_WIDTH - 40,
					"height" : 48,
				},
				{
					"name" : "ui_text3",
					"type" : "text",
					"x" : 0,
					"y" : 132,
					"text" : "",
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
				{
					"name" : "ui_accept_button",
					"type" : "button",
					"x" : -40,
					"y" : 146,
					"horizontal_align" : "center",
					"text" : uiscriptlocale.DUNGEON_INFO_ADDON_LEVEL_CAP_YES,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
				{
					"name" : "ui_close_button",
					"type" : "button",
					"x" : 40,
					"y" : 146,
					"horizontal_align" : "center",
					"text" : uiscriptlocale.DUNGEON_INFO_ADDON_LEVEL_CAP_NO,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
			),
		},
	),
}
