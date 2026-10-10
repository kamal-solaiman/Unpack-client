# coding: utf-8

import localeinfo

ROOT = "d:/ymir work/ui/game/"

BOARD_WIDTH = 130 if localeinfo.IsARABIC() else 108
BOARD_HEIGHT = 40

EXTRA_CHEQUE_WIDTH = (41 if ENABLE_CHEQUE_SYSTEM else 0) if localeinfo.IsARABIC() else (40 if ENABLE_CHEQUE_SYSTEM else 0)
EXTRA_GEM_WIDTH = (64 if ENABLE_GEM_SYSTEM else 0) if localeinfo.IsARABIC() else (60 if ENABLE_GEM_SYSTEM else 0)

BOARD_WIDTH += EXTRA_CHEQUE_WIDTH + EXTRA_GEM_WIDTH

window = {
	"name" : "ExpandedMoneyTaskbar_Window",
	"x" : SCREEN_WIDTH - BOARD_WIDTH,
	"y" : SCREEN_HEIGHT - 65,
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"style" : ("float",),
	"children" :
	[
		{
			"name" : "ExpanedMoneyTaskBar_Board",
			"type" : "board",
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"children" :
			[
				{
					"name" : "money_icon_ui",
					"type" : "image",
					"x" : 9 + EXTRA_CHEQUE_WIDTH + EXTRA_GEM_WIDTH,
					"y" : 11,
					"image" : "d:/ymir work/ui/game/windows/money_icon.sub",
				},
				{
					"name" : "money_slot_ui",
					"type" : "expanded_image",
					"x" : (11 + 15 + EXTRA_CHEQUE_WIDTH + EXTRA_GEM_WIDTH) if localeinfo.IsARABIC() else (9 + 15 + EXTRA_CHEQUE_WIDTH + EXTRA_GEM_WIDTH),
					"y" : 9,
					"image" : "d:/ymir work/ui/public/parameter_slot_03.sub",
					"x_scale" : 1.06 if localeinfo.IsARABIC() else 0.8,
					"y_scale" : 1.0,
					"children" :
					(
						{
							"name" : "money_text_ui",
							"type" : "text",
							"x" : 3,
							"y" : 2 if localeinfo.IsARABIC() else 3,
							"horizontal_align" : "right",
							"text_horizontal_align" : "right",
							"text" : "0",
						},
					),
				}, 
			],
		},
	],
}

if ENABLE_CHEQUE_SYSTEM:
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "cheque_icon_ui",
			"type" : "expanded_image",
			"x" : 9 + EXTRA_GEM_WIDTH,
			"y" : 13,
			"image" : "d:/ymir work/ui/game/windows/cheque_icon.sub",
			"x_scale" : 0.8,
			"y_scale" : 0.8,
		},
		{
			"name" : "cheque_slot_ui",
			"type" : "expanded_image",
			"x" : 9 + 15 + EXTRA_GEM_WIDTH,
			"y" : 9,
			"image" : "d:/ymir work/ui/public/parameter_slot_03.sub",
			"x_scale" : 0.28 if localeinfo.IsARABIC() else 0.26,
			"y_scale" : 1.0,
			"children" :
			(
				{
					"name" : "cheque_text_ui",
					"type" : "text",
					"x" : 3,
					"y" : 2 if localeinfo.IsARABIC() else 3,
					"horizontal_align" : "right",
					"text_horizontal_align" : "right",
					"text" : "",
				},
			),
		},
	]

if ENABLE_GEM_SYSTEM:
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "gem_icon_ui",
			"type" : "image",
			"x" : 9,
			"y" : 13,
			"image" : "d:/ymir work/ui/gemshop/gemshop_gemicon.sub",
		},
		{
			"name" : "gem_slot_ui",
			"type" : "expanded_image",
			"x" : 9 + 15,
			"y" : 9,
			"image" : "d:/ymir work/ui/public/parameter_slot_03.sub",
			"x_scale" : 0.52 if localeinfo.IsARABIC() else 0.44,
			"y_scale" : 1.0,
			"children" :
			(
				{
					"name" : "gem_text_ui",
					"type" : "text",
					"x" : 3,
					"y" : 2 if localeinfo.IsARABIC() else 3,
					"horizontal_align" : "right",
					"text_horizontal_align" : "right",
					"text" : "",
				},
			),
		},
	]
