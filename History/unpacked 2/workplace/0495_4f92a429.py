# coding: utf-8

import uiscriptlocale

BOARD_WIDTH = 205
BOARD_HEIGHT = 380

window = {
	"name" : "Item_Combination_Window",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	(
		{
			"name" : "board",
			"type" : "board",
			"style" : ("attach",),
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"children" :
			(
				{
					"name" : "titlebar_ui",
					"type" : "titlebar",
					"style" : ("attach",),
					"x" : 6,
					"y" : 6,
					"width" : BOARD_WIDTH - 12,
					"color" : "yellow",
					"children" :
					(
						{
							"name" : "titlename_ui",
							"type" : "text",
							"x" : (BOARD_WIDTH - 12) / 2,
							"y" : 3,
							"text" : uiscriptlocale.COMB_TITLE2,
							"text_horizontal_align" : "center",
						},
					),
				},
				{
					"name" : "background_ui",
					"type" : "image",
					"x" : 8,
					"y" : 30,
					"image" : uiscriptlocale.LOCALE_UISCRIPT_PATH + "combination/comb1.tga",
				},
				{
					"name" : "mediumslot_ui",
					"type" : "slot",
					"image" : "d:/ymir work/ui/public/slot_base.sub",
					"x" : 8,
					"y" : 30,
					"width" : 190,
					"height" : 40,
					"slot" :
					(
						{ "index" : 0, "x" : 78, "y" : 12, "width" : 32, "height" : 32 },
					),
					"children" :
					(
						{
							"name" : "slotname0_ui",
							"type" : "text",
							"x" : 190 / 2,
							"y" : 49,
							"text" : uiscriptlocale.COMB_TRANSFER,
							"text_horizontal_align" : "center",
						},
					),
				},
				{
					"name" : "combslot_ui",
					"type" : "slot",
					"x" : 8,
					"y" : 90,
					"width" : 190,
					"height" : 300,
					"slot" :
					(
						{ "index" : 1, "x" : 28, "y" : 8, "width" : 32, "height" : 96},
						{ "index" : 2, "x" : 129, "y" : 8, "width" : 32, "height" : 96},
						{ "index" : 3, "x" : 79, "y" : 125, "width" : 32, "height" : 96},
					),
					"children" :
					(
						{
							"name" : "slotname1_ui",
							"type" : "text",
							"x" : 43,
							"y" : 110,
							"text" : uiscriptlocale.COMB_APPEARANCE2,
							"text_horizontal_align" : "center",
						},
						{
							"name" : "slotname2_ui",
							"type" : "text",
							"x" : 143,
							"y" : 110,
							"text" : uiscriptlocale.COMB_ATTRIBUTE2,
							"text_horizontal_align" : "center",
						},
						{
							"name" : "slotname3_ui",
							"type" : "text",
							"x" : 190 / 2,
							"y" : 229,
							"text" : uiscriptlocale.COMB_RESULT2,
							"text_horizontal_align" : "center",
						},
					),
				},
				{
					"name" : "acceptbutton_ui",
					"type" : "button",
					"x" : 40,
					"y" : 345,
					"text" : uiscriptlocale.OK,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
				{
					"name" : "closebutton_ui",
					"type" : "button",
					"x" : 114,
					"y" : 345,
					"text" : uiscriptlocale.CANCEL,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
			),
		},
	),
}
