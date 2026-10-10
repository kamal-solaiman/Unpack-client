# coding: utf-8

import uiscriptlocale
import localeinfo

BOARD_WIDTH = 229
BOARD_HEIGHT = 405

if localeinfo.IsARABIC():
	BONUSE_X = BOARD_WIDTH / 2 + 2
	STATE_X = BOARD_WIDTH / 2 - 98 - 2
else:
	BONUSE_X = BOARD_WIDTH / 2 - 98 - 2
	STATE_X = BOARD_WIDTH / 2 + 2

IMG_PATH = "d:/ymir work/ui/game/bonusboard/"

window = {
	"name" : "CharacterDetailsUI_Window",
	"style" : ("float", "ltr"),
	"x" : 0,
	"y" : 0,
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	[
		{
			"name" : "ui_board",
			"type" : "board",
			"style" : ("attach", "ltr"),
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"children" : [
				{
					"name" : "ui_titlebar",
					"type" : "titlebar",
					"style" : ("attach",),
					"x" : 8,
					"y" : 7,
					"width" : BOARD_WIDTH - 16,
					"color" : "yellow",
					"children" :
					[
						{
							"name" : "ui_titlename",
							"type" : "text",
							"x" : (BOARD_WIDTH - 16) / 2,
							"y" : 3,
							"text" : uiscriptlocale.CHARACTER_DETAILS_TITLE,
							"text_horizontal_align" : "center",
						},
					],
				},
				{
					"name" : "ui_type_bonuses_button",
					"type" : "radio_button",
					"x" : BONUSE_X,
					"y" : 33,
					"default_image" : IMG_PATH + "type_button_normal.png",
					"over_image" : IMG_PATH + "type_button_hover.png",
					"down_image" : IMG_PATH + "type_button_down.png",
					"text" : uiscriptlocale.CHARACTER_DETAILS_BONUSES_TITLE,
				},
				{
					"name" : "ui_type_stats_button",
					"type" : "radio_button",
					"x" : STATE_X,
					"y" : 33,
					"default_image" : IMG_PATH + "type_button_normal.png",
					"over_image" : IMG_PATH + "type_button_hover.png",
					"down_image" : IMG_PATH + "type_button_down.png",
					"text" : uiscriptlocale.CHARACTER_DETAILS_STATS_TITLE,
				},
				{
					"name" : "ui_mainboard",
					"type" : "v2_thinboard",
					"style" : ("attach", "ltr"),
					"x" : 8,
					"y" : 33 + 23,
					"width" : BOARD_WIDTH - 16,
					"height" : BOARD_HEIGHT - 33 + 23 - 2 - 54,
					"children" : [
						{
							"name" : "ui_search_board",
							"type" : "window",
							"style" : ("attach",),
							"x" : (BOARD_WIDTH - 16 - 160) / 2,
							"y" : 6,
							"width" : 160,
							"height" : 23,
							"children" : [
								{
									"name" : "ui_search_image",
									"type" : "image",
									"image" : IMG_PATH + "bg_search.png",
									"x" : 0,
									"y" : 0,
								},
								{
									"name" : "ui_search_button_reset",
									"type" : "button",
									"default_image" : IMG_PATH + "btn_reset_normal.png",
									"over_image" : IMG_PATH + "btn_reset_hover.png",
									"down_image" : IMG_PATH + "btn_reset_down.png",
									"x" : 129 + 2,
									"y" : 0,
								},
							],
						},
						{
							"name" : "ui_search_container_board",
							"type" : "thinboard_circle",
							"style" : ("attach",),
							"x" : 4,
							"y" : 6 + 23 + 4,
							"width" : BOARD_WIDTH - 16 - 8,
							"height" : BOARD_HEIGHT - 33 + 23 - 2 - 23 - 6 - 4 - 58,
							"children" : [
								{
									"name" : "ui_search_peek_board",
									"type" : "window",
									"style" : ("attach",),
									"x" : 4,
									"y" : 4,
									"width" : BOARD_WIDTH - 16 - 8,
									"height" : BOARD_HEIGHT - 33 + 23 - 2 - 23 - 6 - 4 - 8 - 58,
								},
							],
						},
						{
							"name" : "ui_container_board",
							"type" : "thinboard_circle",
							"style" : ("attach",),
							"x" : 4,
							"y" : 6 + 23 + 4,
							"width" : BOARD_WIDTH - 16 - 8,
							"height" : BOARD_HEIGHT - 33 + 23 - 2 - 23 - 6 - 4 - 58,
							"children" : [
								{
									"name" : "ui_peek_board",
									"type" : "window",
									"style" : ("attach",),
									"x" : 4,
									"y" : 4,
									"width" : BOARD_WIDTH - 16 - 8,
									"height" : BOARD_HEIGHT - 33 + 23 - 2 - 23 - 6 - 4 - 8 - 58,
								},
							],
						},
						{
							"name" : "ui_container_board_stats",
							"type" : "thinboard_circle",
							"style" : ("attach",),
							"x" : 4,
							"y" : 6 + 23 + 4,
							"width" : BOARD_WIDTH - 16 - 8,
							"height" : BOARD_HEIGHT - 33 + 23 - 2 - 23 - 6 - 4 - 58,
							"children" : [
								{
									"name" : "ui_peek_board_stats",
									"type" : "window",
									"style" : ("attach",),
									"x" : 4,
									"y" : 4,
									"width" : BOARD_WIDTH - 16 - 8,
									"height" : BOARD_HEIGHT - 33 + 23 - 2 - 23 - 6 - 4 - 8 - 58,
								},
							],
						},
					],
				},
			],
		},
	],
}
