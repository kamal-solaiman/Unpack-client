# coding: utf-8

import localeinfo
import uiscriptlocale

BOARD_WIDTH = 260 if localeinfo.IsARABIC() else 220
BOARD_HEIGHT = 90

window = {
	"name" : "PickEtcDialog_Window",
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
			"title" : "",
			"children" :
			[
				{
					"name" : "pick_slot_ui",
					"type" : "image",
					"x" : (BOARD_WIDTH) / 2 - 90,
					"y" : 34,
					"image" : "d:/ymir work/ui/public/parameter_slot_03.sub",
					"children" :
					[
						{
							"name" : "pick_value_ui",
							"type" : "editline",
							"x" : 3,
							"y" : 2 if localeinfo.IsARABIC() else 3,
							"width" : 90 - 3,
							"height" : 18,
							"input_limit" : 0,
							"only_number" : 1,
							"text" : "",
						},
						{
							"name" : "max_count_ui",
							"type" : "text",
							"x" : 90 + 3 + 3 if localeinfo.IsARABIC() else 90 + 3,
							"y" : 2,
							"text" : "",
						},
					],
				},
				{
					"name" : "accept_button_ui",
					"type" : "button",
					"x" : BOARD_WIDTH / 2 - 61 - 5,
					"y" : 58,
					"text" : uiscriptlocale.OK,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
				{
					"name" : "close_button_ui",
					"type" : "button",
					"x" : BOARD_WIDTH / 2 + 5,
					"y" : 58,
					"text" : uiscriptlocale.CANCEL,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
			],
		},
	],
}
