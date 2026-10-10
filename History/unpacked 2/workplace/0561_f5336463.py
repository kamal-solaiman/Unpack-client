# coding: utf-8

import localeinfo
import uiscriptlocale

BOARD_WIDTH = 170
BOARD_HEIGHT = 90

window = {
	"name" : "ExchangeCurrencyDialog_Window",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	(
		{
			"name" : "board_ui",
			"type" : "board_with_titlebar",
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"title" : "",
			"children" :
			(
				{
					"name" : "input_slot_ui",
					"type" : "slotbar",
					"x" : (BOARD_WIDTH - 26) / 2 - 12,
					"y" : 34,
					"width" : 28 if localeinfo.IsARABIC() else 26,
					"height" : 18,
					"children" :
					(
						{
							"name" : "input_value_ui",
							"type" : "editline",
							"x" : 3,
							"y" : 3,
							"width" : 25 if localeinfo.IsARABIC() else 23,
							"height" : 18,
							"only_number" : 1,
							"input_limit" : 3,
						},
						{
							"name" : "max_count_ui",
							"type" : "text",
							"x" : (28 if localeinfo.IsARABIC() else 26) + 3,
							"y" : 2,
							"text" : "",
						},
					),
				},
				{
					"name" : "accept_button_ui",
					"type" : "button",
					"x" : -61 - 5 + 30,
					"y" : 58,
					"horizontal_align" : "center",
					"text" : uiscriptlocale.OK,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
				{
					"name" : "close_button_ui",
					"type" : "button",
					"x" : 5 + 30,
					"y" : 58,
					"horizontal_align" : "center",
					"text" : uiscriptlocale.CANCEL,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
			),
		},
	),
}
