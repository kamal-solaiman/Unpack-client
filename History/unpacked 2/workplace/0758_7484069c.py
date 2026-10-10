# coding: latin_1

import uiscriptlocale
import localeinfo
window = {
	"name" : "QuestionDialog",
	"style" : ("movable",),
	"x" : SCREEN_WIDTH/2 - 125,
	"y" : SCREEN_HEIGHT/2 - 52,
	"width" : 210,
	"height" : 50,
	"children" :
	(
		{
			"name" : "board",
			"type" : "board",
			"x" : 0,
			"y" : 0,
			"width" : 210,
			"height" : 50,
			"children" :
			(
				{
					"name" : "message",
					"type" : "text",
					"x" : 0,
					"y" : 20,
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},

				{
					"name" : "accept",
					"type" : "button",
					"x" : -65,
					"y" : 35,
					"width" : 61,
					"height" : 21,
					"horizontal_align" : "center",
					"text" : uiscriptlocale.YES,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},
				{
					"name" : "remove",
					"type" : "button",
					"x" : 0,
					"y" : 35,
					"width" : 61,
					"height" : 21,
					"horizontal_align" : "center",
					"text" : localeinfo.REMOVE,
					"default_image" : "d:/ymir work/ui/public/middle_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/middle_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/middle_button_03.sub",
				},

				{
					"name" : "cancel",
					"type" : "button",
					"x" : 65,
					"y" : 35,
					"width" : 61,
					"height" : 21,
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
