# coding: latin_1

import localeinfo

DIF_W = 28
DIF_H = 40

BOARD_WIDTH = 380 + DIF_W
BOARD_HEIGHT = 365 + DIF_H

window = {
	"name" : "HistoryWindowUI",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	(
		{
			"name" : "ui_board",
			"type" : "board",
			"style" : ("attach",),
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"x" : 0,
			"y" : 0,
			"children" :
			(
				{
					"name" : "ui_titlebar",
					"type" : "titlebar",
					"style" : ("attach",),
					"x" : 6,
					"y" : 6,
					"width" : BOARD_WIDTH - 12,
					"color" : "yellow",
					"children" :
					(
						{
							"name" : "ui_titlename",
							"type" : "text",
							"x" : (BOARD_WIDTH - 12) / 2,
							"y" : 3,
							"text" : localeinfo.OFFLINESHOP_HISTORY,
							"text_horizontal_align" : "center",
						},
					),
				},
				{
					"name" : "ui_bg",
					"type" : "image",
					"style" : ("ltr",),
					"x" : 8+12,
					"y" : 29,
					"image" : "cream/shopseller/history_window_title.png",
					"children" :
					(
						{
							"name" : "ui_itemane_bg",
							"type" : "window",
							"style" : ("ltr",),
							"width" : 94,
							"height" : 23,
							"x" : 3,
							"y" : 3,
							"children" :
							(
								{
									"name" : "ui_itemname_text",
									"type" : "text",
									"x" : 94 / 2,
									"y" : 6,
									"text" : localeinfo.OFFLINESHOP_HISTORY_ITEMNAME,
									"text_horizontal_align" : "center",
								},
							),
						},
						{
							"name" : "ui_buyername_bg",
							"type" : "window",
							"style" : ("ltr",),
							"width" : 95,
							"height" : 23,
							"x" : 100,
							"y" : 3,
							"children" :
							(
								{
									"name" : "ui_buyername_text",
									"type" : "text",
									"x" : 95 / 2,
									"y" : 6,
									"text" : localeinfo.OFFLINESHOP_HISTORY_BUYERNAME,
									"text_horizontal_align" : "center",
								},
							),
						},
						{
							"name" : "ui_price_bg",
							"type" : "window",
							"style" : ("ltr",),
							"width" : 86,
							"height" : 23,
							"x" : 199,
							"y" : 3,
							"children" :
							(
								{
									"name" : "ui_price_text",
									"type" : "text",
									"x" : 86 / 2,
									"y" : 6,
									"text" : localeinfo.OFFLINESHOP_HISTORY_PRICE,
									"text_horizontal_align" : "center",
								},
							),
						},
						{
							"name" : "ui_time_bg",
							"type" : "window",
							"style" : ("ltr",),
							"width" : 87,
							"height" : 23,
							"x" : 289,
							"y" : 3,
							"children" :
							(
								{
									"name" : "ui_time_text",
									"type" : "text",
									"x" : 87 / 2,
									"y" : 6,
									"text" : localeinfo.OFFLINESHOP_HISTORY_DATE,
									"text_horizontal_align" : "center",
								},
							),
						},
					),
				},
			),
		},
	),
}
