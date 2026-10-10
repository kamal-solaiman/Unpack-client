# coding: latin_1

import localeinfo

MAX_BUTTONS = 2
BOARD_WIDTH = 210
BOARD_HEIGHT = 80

window = {
	"name" : "BoxMenuWindow",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	(
		{
			"name" : "board",
			"type" : "board_with_titlebar",
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"title" : localeinfo.INVENTORY_TEXT,
			"children" : 
			(
				{
					"name" : "btn1",
					"type" : "button",
					"x" : 35,
					"y" : 40,
					"text" : localeinfo.INVENTORY_TEXT1,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
				{
					"name" : "btn2",
					"type" : "button",
					"x" : 105,
					"y" : 40,
					"text" : localeinfo.INVENTORY_TEXT3,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
			),
		},
	),
}
