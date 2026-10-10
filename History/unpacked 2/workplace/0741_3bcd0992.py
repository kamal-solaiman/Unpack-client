# coding: utf-8

import localeinfo
import uiscriptlocale

BOARD_WIDTH = 230 if localeinfo.IsARABIC() else 186
BOARD_HEIGHT = 90

EXTRA_CHEQUE_HEIGHT = 22 if ENABLE_CHEQUE_SYSTEM else 0

BOARD_HEIGHT += EXTRA_CHEQUE_HEIGHT

window = {
	"name" : "PickMoneyDialog_Window",
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
			"title" : uiscriptlocale.PICK_MONEY_TITLE,
			"children" :
			[
				{
					"name" : "money_slot",
					"type" : "expanded_image",
					"x" : 20 + 15,
					"y" : 34 + EXTRA_CHEQUE_HEIGHT,
					"image" : "d:/ymir work/ui/public/parameter_slot_02.sub",
					"x_scale" : 1.3 if localeinfo.IsARABIC() else 1.0,
					"y_scale" : 1.0,
					"children" :
					[
						{
							"name" : "icon_ui",
							"type" : "image",
							"x" : -22,
							"y" : 2,
							"image" : "d:/ymir work/ui/game/windows/money_icon.sub",
						},
						{
							"name" : "value_ui",
							"type" : "editline",
							"x" : 3,
							"y" : 1 if localeinfo.IsARABIC() else 2,
							"width" : 61 - 3 + 18 + 2 if localeinfo.IsARABIC() else 61 - 3,
							"height" : 18,
							"input_limit" : 10,
							"only_number" : 0,
							"text" : "1",
						},
						{
							"name" : "max_count_ui",
							"type" : "text",
							"x" : 62 + 18 + 2 if localeinfo.IsARABIC() else 62,
							"y" : 1 if localeinfo.IsARABIC() else 2,
							"text" : "",
						},
					],
				},
				{
					"name" : "accept_button_ui",
					"type" : "button",
					"x" : BOARD_WIDTH / 2 - 61 - 5,
					"y" : BOARD_HEIGHT - 32,
					"text" : uiscriptlocale.OK,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
				{
					"name" : "close_button_ui",
					"type" : "button",
					"x" : BOARD_WIDTH / 2 + 5,
					"y" : BOARD_HEIGHT - 32,
					"text" : uiscriptlocale.CANCEL,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
			],
		},
	],
}

if ENABLE_CHEQUE_SYSTEM:
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "cheque_slot",
			"type" : "expanded_image",
			"x" : 20 + 15,
			"y" : 34,
			"image" : "d:/ymir work/ui/public/parameter_slot_02.sub",
			"x_scale" : 1.3 if localeinfo.IsARABIC() else 1.0,
			"y_scale" : 1.0,
			"children" :
			[
				{
					"name":"cheque_icon_ui",
					"type":"image",
					"x" : -22,
					"y" : 2,
					"image":"d:/ymir work/ui/game/windows/cheque_icon.sub",
				},
				{
					"name" : "cheque_value_ui",
					"type" : "editline",
					"x" : 3,
					"y" : 1 if localeinfo.IsARABIC() else 2,
					"width" : 61 - 3 + 18 + 2 if localeinfo.IsARABIC() else 61 - 3,
					"height" : 18,
					"input_limit" : 3,
					"only_number" : 1,
					"text" : "0",
				},
				{
					"name" : "max_cheque_count_ui",
					"type" : "text",
					"x" : 62 + 18 + 2 if localeinfo.IsARABIC() else 62,
					"y" : 1 if localeinfo.IsARABIC() else 2,
					"text" : "",
				},
			],
		},
	]
