# coding: latin_1

import uiscriptlocale

BOARD_WIDTH = 220
BOARD_HEIGHT = 181

window = {
	"name" : "AntiMultipleFarmWnd",
	"style" : ("movable", "float",),

	"x" : 0,
	"y" : 0,

	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,

	"children" :
	[
		## BOARD
		{
			"name" : "board",
			"type" : "board_with_titlebar_without_button",
			"style" : ("ltr",),

			"x" : 0,
			"y" : 0,

			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,

			"title" : uiscriptlocale.ANTI_MULTIPLE_FARM_WND_TITLE,
			"children" :
			[
				{
					"name" : "anti_farm_bg_layer",
					"type" : "expanded_image",
					"style" : ("ltr",),
					
					"x" : 7,
					"y" : 32,
					
					"image" : "d:/ymir work/ui/anti_multiple_farm/anti_farm_bg_layer.tga",
					"children" :
					[
						{
							"name" : "base_text_info",
							"type" : "text",
							
							"x" : 0,
							"y" : 3,
							
							"text_horizontal_align" : "center",
							"horizontal_align" : "center",
							
							"text" : uiscriptlocale.ANTI_MULTIPLE_FARM_BASE_TEXT,
						},
					],
				},
				{
					"name" : "scrollbar",
					"type" : "new_scrollbar",
					"style" : ("ltr",),

					"x" : 170+25,
					"y" : 40,
					"size" : 130,
				},
				{
					"name" : "view_window",
					"type" : "window",
					"style" : ("attach","ltr",),
					
					"width" : 210,#168
					"height" : 21,
					
					"x" : 0,
					"y" : 153,
					
					"children" :
					[
						{
							"name" : "edit_button",
							"type" : "button",
							"style" : ("ltr",),
							
							"x" : 15+60,
							"y" : 0,

							"width" : 61,
							"height" : 21,

							"default_image" : "d:/ymir work/ui/anti_multiple_farm/edit_norm.tga",
							"over_image" : "d:/ymir work/ui/anti_multiple_farm/edit_hover.tga",
							"down_image" : "d:/ymir work/ui/anti_multiple_farm/edit_down.tga",
						},
						{
							"name" : "close_button",
							"type" : "button",
							"style" : ("ltr",),

							"x" : -40+47,
							"y" : 0,

							"width" : 41,
							"height" : 21,

							"default_image" : "d:/ymir work/ui/new_options/close_norm.tga",
							"over_image" : "d:/ymir work/ui/new_options/close_hover.tga",
							"down_image" : "d:/ymir work/ui/new_options/close_down.tga",
						},

						{
							"name" : "refresh_button",
							"type" : "button",
							"style" : ("ltr",),

							"x" : 90+47,
							"y" : 0,

							"width" : 41,
							"height" : 21,

							"default_image" : "d:/ymir work/ui/new_options/reload_norm.tga",
							"over_image" : "d:/ymir work/ui/new_options/reload_hover.tga",
							"down_image" : "d:/ymir work/ui/new_options/reload_down.tga",
						},
					],
				},
				{
					"name" : "edit_window",
					"type" : "window",
					"style" : ("attach","ltr",),
					
					"width" : 168,
					"height" : 21,
					
					"x" : 0,
					"y" : 153,
					
					"children" :
					[
						{
							"name" : "save_edit_button",
							"type" : "button",
							"style" : ("ltr",),

							"x" : 15,
							"y" : 0,

							"width" : 61,
							"height" : 21,

							"default_image" : "d:/ymir work/ui/new_options/ok_norm.tga",
							"over_image" : "d:/ymir work/ui/new_options/ok_hover.tga",
							"down_image" : "d:/ymir work/ui/new_options/ok_down.tga",
						},
						{
							"name" : "close_edit_button",
							"type" : "button",
							"style" : ("ltr",),

							"x" : 60,
							"y" : 0,

							"width" : 41,
							"height" : 21,

							"default_image" : "d:/ymir work/ui/new_options/close_norm.tga",
							"over_image" : "d:/ymir work/ui/new_options/close_hover.tga",
							"down_image" : "d:/ymir work/ui/new_options/close_down.tga",
						},
					],
				},
			],
		},
	],
}
