# coding: latin_1

import localeinfo

BOARD_WIDTH = 180
BOARD_HEIGHT = 212

window = {
	"name" : "HistoryPopupWindowUI",
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
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"x" : 0,
			"y" : 0,
			"children" :
			(
				{
					"name" : "ui_desc1_text",
					"type" : "text",
					"x" : 0,
					"y" : 8,
					"text" : "",
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
				},
				{
					"name" : "ui_desc2_text",
					"type" : "text",
					"x" : 0,
					"y" : 26,
					"text" : "",
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
				},
				{
					"name" : "ui_desc3_text",
					"type" : "text",
					"x" : 0,
					"y" : 158,
					"text" : "",
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
				},
				{
					"name" : "ui_board_item",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 44,
					"image" : "cream/shopseller/bg_item.png",
					"horizontal_align" : "center",
					"children" :
					(
						{
							"name" : "ui_board_item_icon",
							"type" : "expanded_image",
							"x" : 0,
							"y" : 0,
							"width" : 32,
							"height": 96,
							"image" : "icon/item/money.tga",
							"horizontal_align" : "center",
							"vertical_align" : "center",
						},
					),
				},
				{
					"name" : "ui_cancel_btn",
					"type" : "button",
					"x" : 0,
					"y" : 176,
					"horizontal_align" : "center",
					"text" : localeinfo.OFFLINESHOP_HISTORY_POPUP_CLOSE,
					"default_image" : "cream/shopseller/btn_norm.png",
					"over_image" : "cream/shopseller/btn_hover.png",
					"down_image" : "cream/shopseller/btn_down.png",
				},
			),
		},
	),
}
