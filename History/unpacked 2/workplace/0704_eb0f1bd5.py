# coding: utf-8

import uiscriptlocale

BOARD_WIDTH = 240
BOARD_HEIGHT = 328

window = {
	"name" : "MultipleBuyDialogWindow",
	"x" : 0,
	"y" : 0,
	"style" : ("float",),
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	(
		{
			"name" : "ui_board",
			"type" : "board",
			"style" : ("attach",),
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"children" :
			(
				{
					"name" : "ui_titlebar",
					"type" : "titlebar_without_button",
					"style" : ("attach",),
					"x" : 8,
					"y" : 8,
					"width" : BOARD_WIDTH - 16,
					"color" : "yellow",
					"children" :
					(
						{
							"name" : "ui_titlename",
							"type" : "text",
							"x" : (BOARD_WIDTH - 16) / 2,
							"y" : 4,
							"text" : uiscriptlocale.TITLE_SHOP_MULTIPLE_BUY,
							"text_horizontal_align" : "center"
						},
					),
				},
				{
					"name" : "ui_slotbar",
					"type" : "slotbar",
					"x" : 0,
					"y" : 32,
					"width" : 50,
					"height" : 18,
					"horizontal_align" : "center",
					"children" :
					(
						{
							"name" : "ui_editline",
							"type" : "editline",
							"x" : 3,
							"y" : 3,
							"width" : 50,
							"height" : 18,
							"input_limit" : 3,
							"only_number" : 1,
							"text" : "1",
						},
					),
				},
				{
					"name" : "ui_button_accept",
					"type" : "button",
					"x" : 0,
					"y" : 0,
					"horizontal_align" : "center",
					"text" : uiscriptlocale.SHOP_MULTIPLE_BUY,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
				{
					"name" : "ui_button_close",
					"type" : "button",
					"x" : 0,
					"y" : 0,
					"horizontal_align" : "center",
					"text" : uiscriptlocale.SHOP_MULTIPLE_CLOSE,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
			),
		},
	),
}
