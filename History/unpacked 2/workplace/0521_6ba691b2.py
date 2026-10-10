# coding: latin_1

import localeinfo

BOARD_WIDTH = 145
BOARD_HEIGHT = 137+15

window = {
	"name" : "BraveCapeWindow",
	"x" : SCREEN_WIDTH - 176 - BOARD_WIDTH,
	"y" : SCREEN_HEIGHT - 37 - 565 + 112,
	"style" : ("float",),
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	(
		{
			"name" : "expand",
			"type" : "button",
			"x" : 2,
			"y" : 15,
			"default_image" : "d:/ymir work/ui/game/belt_inventory/btn_expand_normal.tga",
			"over_image" : "d:/ymir work/ui/game/belt_inventory/btn_expand_over.tga",
			"down_image" : "d:/ymir work/ui/game/belt_inventory/btn_expand_down.tga",
			"disable_image" : "d:/ymir work/ui/game/belt_inventory/btn_expand_disabled.tga",
		},
		{
			"name" : "layer",
			"type" : "board",
			"style" : ("attach", "float"),
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"children" :
			(
				{
					"name" : "minimize",
					"type" : "button",
					"x" : 2,
					"y" : 35,
					"width" : 10,
					"default_image" : "d:/ymir work/ui/game/belt_inventory/btn_minimize_normal.tga",
					"over_image" : "d:/ymir work/ui/game/belt_inventory/btn_minimize_over.tga",
					"down_image" : "d:/ymir work/ui/game/belt_inventory/btn_minimize_down.tga",
					"disable_image" : "d:/ymir work/ui/game/belt_inventory/btn_minimize_disabled.tga",
				},
				{
					"name" : "bg",
					"type" : "image",
					"style" : ("attach", "float"),
					"x" : 8,
					"y" : 9,
					"width" : 129,
					"height" : 160,
					"image" : "d:/ymir work/ui/game/bravery_cape/bg.tga",
					"children" :
					(
						{
							"name" : "item",
							"type" : "slot",
							"x" : 49,
							"y" : 12,
							"width" : 32,
							"height" : 32,
							"slot" :
							(
								{"index" : 0, "x" : 0, "y" : 0, "width" : 32, "height" : 32},
							),
						},
						{
							"name" : "start",
							"type" : "radio_button",
							"x" : 6,
							"y" : 160 - 50,
							"default_image" : "d:/ymir work/ui/game/bravery_cape/start_btn_0.tga",
							"over_image" : "d:/ymir work/ui/game/bravery_cape/start_btn_1.tga",
							"down_image" : "d:/ymir work/ui/game/bravery_cape/start_btn_2.tga",
							"disable_image" : "d:/ymir work/ui/game/bravery_cape/start_btn_2.tga",
							"text" : localeinfo.BRAVERY_CAPE_START,
						},
						{
							"name" : "stop",
							"type" : "radio_button",
							"x" : 66,
							"y" : 160 - 50,
							"default_image" : "d:/ymir work/ui/game/bravery_cape/stop_btn_0.tga",
							"over_image" : "d:/ymir work/ui/game/bravery_cape/stop_btn_1.tga",
							"down_image" : "d:/ymir work/ui/game/bravery_cape/stop_btn_2.tga",
							"disable_image" : "d:/ymir work/ui/game/bravery_cape/stop_btn_2.tga",
							"text" : localeinfo.BRAVERY_CAPE_STOP,
						},
					),
				},
			),
		},
	),
}
