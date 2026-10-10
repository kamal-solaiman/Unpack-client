# coding: utf-8

import localeinfo
import uiscriptlocale

BOARD_WIDTH = 160
BOARD_HEIGHT = 132 if USE_AUTO_SPLIT_ITEMS else 90

window = {
	"name" : "PickItemDialog_Window",
	"x" : 100,
	"y" : 100,
	"style" : ("movable", "float",),
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	[
		{
			"name" : "board_ui",
			"type" : "board_with_titlebar",
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"title" : localeinfo.PICK_ITEM_TITLE,
			"children" :
			[
				{
					"name" : "pick_slot_ui",
					"type" : "expanded_image",
					"x" : (BOARD_WIDTH) / 2 - (54 if localeinfo.IsARABIC() else 63),
					"y" : 34,
					"image" : "d:/ymir work/ui/public/parameter_slot_03.sub",
					"x_scale" : 0.4 if localeinfo.IsARABIC() else 0.3,
					"y_scale" : 1.0,
					"children" :
					[
						{
							"name" : "pick_value_ui",
							"type" : "editline",
							"x" : 3,
							"y" : 2 if localeinfo.IsARABIC() else 3,
							"width" : 90 - (54 if localeinfo.IsARABIC() else 63),
							"height" : 18,
							"input_limit" : 4,
							"only_number" : 1,
							"text" : "",
						},
						{
							"name" : "max_count_ui",
							"type" : "text",
							"x" : (36 + 2 if localeinfo.IsARABIC() else 27) + 3,
							"y" : 2,
							"text" : "",
						},
					],
				},
				{
					"name" : "accept_button_ui",
					"type" : "button",
					"x" : BOARD_WIDTH / 2 - 61 - 5,
					"y" : 102 if USE_AUTO_SPLIT_ITEMS else 58,
					"text" : uiscriptlocale.OK,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
				{
					"name" : "close_button_ui",
					"type" : "button",
					"x" : BOARD_WIDTH / 2 + 5,
					"y" : 102 if USE_AUTO_SPLIT_ITEMS else 58,
					"text" : uiscriptlocale.CANCEL,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
			],
		},
	],
}

if USE_AUTO_SPLIT_ITEMS:
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "split_thinboard_ui",
			"type" : "v2_thinboard",
			"x" : 20,
			"y" : 58,
			"height" : 38,
			"width" : BOARD_WIDTH - 40,
		},
		{
			"name" : "split_text_ui",
			"type" : "text",
			"x" : BOARD_WIDTH / 2,
			"y" : 60,
			"text" : uiscriptlocale.DIVISION_STACK,
			"text_horizontal_align":"center",
		},
		{
			"name" : "split_button_ui",
			"type" : "toggle_button",
			"x" : (BOARD_WIDTH - 14) / 2,
			"y" : 78,
			"default_image" : "d:/ymir work/ui/game/itemsplit/btn_normal.tga",
			"over_image" : "d:/ymir work/ui/game/itemsplit/btn_hover.tga",
			"down_image" : "d:/ymir work/ui/game/itemsplit/btn_down.tga",
		},
	]
