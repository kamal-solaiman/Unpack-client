# coding: latin_1

import localeinfo
import uiscriptlocale

BOARD_WIDTH = 158+20
BOARD_HEIGHT = 78+20
ROOT_PATH = "d:/ymir work/ui/game/inv_manage/"

window = {
	"name" : "OrganizeItemsDialogWindow",
	"style" : ("movable", "float","attach"),
	"x" : 0,
	"y" : 0,
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	(
		{
			"name" : "board",
			"type": "board",
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"children" :
			(
				{
					"name" : "WindowBG",
					"type" : "expanded_image",
					"x" : 10,
					"y" : 10,
					"image" : ROOT_PATH + "frame.png",
				},
				{
					"name" : "TitleBar",
					"type" : "titlebar",
					"style" : ("attach",),
					"x" : 6,
					"y" : 6,
					"width" : BOARD_WIDTH - 10,
					"color" : "yellow",
					"children" :
					(
						{
							"name":"TitleName",
							"type":"text",
							"x":95-20,
							"y":3,
							"text" : localeinfo.CHOOSE_SORT_OR_STACK,
							"text_horizontal_align":"center"
						},
					),
				},
				{
					"name" : "ui_sort_button",
					"type" : "button",
					"x" : 89 - 30,
					"y" : 45,
					"default_image" : ROOT_PATH + "btn-sort-1.png",
					"over_image" : ROOT_PATH + "btn-sort-2.png",
					"down_image" : ROOT_PATH + "btn-sort-3.png",
					"tooltip_text": uiscriptlocale.ITEM_SORT_OPTION,
				},
				{
					"name" : "ui_stack_button",
					"type" : "button",
					"x" : 89 + 10,
					"y" : 45,
					"default_image" : ROOT_PATH + "btn-stack-1.png",
					"over_image" : ROOT_PATH + "btn-stack-2.png",
					"down_image" : ROOT_PATH + "btn-stack-3.png",
					"tooltip_text": uiscriptlocale.ITEM_STACK_OPTION,
				},
				{
					"name" : "ui_activate_button",
					"type" : "button",
					"x" : 89 - 30,
					"y" : 73,
					"default_image" : ROOT_PATH + "btn-pots-1.png",
					"over_image" : ROOT_PATH + "btn-pots-2.png",
					"down_image" : ROOT_PATH + "btn-pots-3.png",
					"tooltip_text": uiscriptlocale.ITEM_AUTO_ACTIVATE_POTION_OPTION,
				},
				{
					"name" : "ui_deactivate_button",
					"type" : "button",
					"x" : 89 + 10,
					"y" : 73,
					"default_image" : ROOT_PATH + "btn-dispots-1.png",
					"over_image" : ROOT_PATH + "btn-dispots-2.png",
					"down_image" : ROOT_PATH + "btn-dispots-3.png",
					"tooltip_text": uiscriptlocale.ITEM_AUTO_DEACTIVATE_POTION_OPTION,
				},
				{
					"name" : "ui_close_button",
					"type" : "button",
					"x" : 30,
					"y" : 73,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
			),
		},
	),
}
