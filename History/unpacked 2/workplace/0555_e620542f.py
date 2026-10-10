# coding: latin_1

import uiscriptlocale

BOARD_WIDTH = 651
BOARD_HEIGHT = 508

LIST_WIDTH = 411
LIST_HEIGHT = BOARD_HEIGHT - 48

EXTRA_LIST_WIDTH = BOARD_WIDTH - LIST_WIDTH - 31
EXTRA_LIST_HEIGHT = LIST_HEIGHT

IMG_PATH = "d:/ymir work/ui/game/dungeoninfo/"
REWORK_PATH = "d:/ymir work/ui/dungeoninfo_rework/"

HIDE_BUTTON_WIDTH_ADJUST = 0

if AUTO_HIDE_LOW_LEVELS_DUNGEONS:
	HIDE_BUTTON_WIDTH_ADJUST = 40

window = {
	"name" : "DungeonInfo_Window",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	(
		{
			"name" : "board_ui",
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
					"x" : 8 + HIDE_BUTTON_WIDTH_ADJUST,
					"y" : 7,
					"width" : BOARD_WIDTH - 16 - HIDE_BUTTON_WIDTH_ADJUST,
					"color" : "yellow",
					"children" :
					(
						{
							"name" : "titlename_ui",
							"type" : "text",
							"x" : (BOARD_WIDTH - 16 - HIDE_BUTTON_WIDTH_ADJUST) / 2,
							"y" : 3,
							"text" : uiscriptlocale.DUNGEON_INFO_TITLE,
							"text_horizontal_align" : "center"
						},
					),
				},
				{
					"name" : "reset_hided_button_ui",
					"type" : "button",
					"x" : 8,
					"y" : 7,
					"default_image" : IMG_PATH + "reset_hided_button_normal.png",
					"over_image" : IMG_PATH + "reset_hided_button_over.png",
					"down_image" : IMG_PATH + "reset_hided_button_down.png",
				},
				# {
					# "name" : "boardersBG",
					# "type" : "expanded_image",
					# "x" : 10,
					# "y" : 34,
					# "image" : "d:/ymir work/ui/boarders_test.png",
				# },
				{
					"name" : "WindowBG",
					"type" : "expanded_image",
					"x" : 10,
					"y" : 34,
					"image" : "d:/ymir work/ui/dungeoninfo_rework/bg.png",
				},
				{
					"name" : "list_ui",
					"type" : "v3_thinboard",
					"style" : ("attach",),
					"x" : 10,
					"y" : 34,
					"width" : LIST_WIDTH,
					"height" : LIST_HEIGHT,
				},
				{
					"name" : "extra_list_ui",
					"type" : "v3_thinboard",
					"style" : ("attach",),
					"x" : 20 + LIST_WIDTH,
					"y" : 34,
					"width" : EXTRA_LIST_WIDTH,
					"height" : EXTRA_LIST_HEIGHT,
					"children" :
					(
						#{
						#	"name" : "informations_ui",
						#	"type" : "thinboard_circle",
						#	"style" : ("attach",),
						#	"x" : 10,
						#	"y" : 27,
						#	"width" : EXTRA_LIST_WIDTH - 20,
						#	"height" : 86,
						#	"children":
						#	(
						#		{
						#			"name" : "drop_button_ui",
						#			"type" : "button",
						#			"default_image" : IMG_PATH + "button_normal.png",
						#			"over_image" : IMG_PATH + "button_hover.png",
						#			"down_image" : IMG_PATH + "button_down.png",
						#			"x" : 0,
						#			"y" : 8 + (16 * 3),
						#			"horizontal_align" : "center",
						#			"text" : uiscriptlocale.DUNGEON_INFO_DROP,
						#		},
						#	),
						#},
						{
							"name" : "top0_button_ui",
							"type" : "button",
							"default_image" : REWORK_PATH + "btn_dmg_0.png",
							"over_image" :  REWORK_PATH + "btn_dmg_1.png",
							"down_image" :  REWORK_PATH + "btn_dmg_2.png",
							"x" : 4,
							"y" : 414,
							"text" : "",
							"tooltip_text" : uiscriptlocale.DUNGEON_INFO_RANK0_TITLE,
						},
						{
							"name" : "top1_button_ui",
							"type" : "button",
							"default_image" : REWORK_PATH + "btn_time_0.png",
							"over_image" :  REWORK_PATH + "btn_time_1.png",
							"down_image" :  REWORK_PATH + "btn_time_2.png",
							"x" : 72,
							"y" : 414,
							"text" : "",
							"tooltip_text" : uiscriptlocale.DUNGEON_INFO_RANK1_TITLE,
						},
						{
							"name" : "top2_button_ui",
							"type" : "button",
							"default_image" : REWORK_PATH + "btn_count_0.png",
							"over_image" :  REWORK_PATH + "btn_count_1.png",
							"down_image" :  REWORK_PATH + "btn_count_2.png",
							"x" : 140,
							"y" : 414,
							"text" : "",
							"tooltip_text" : uiscriptlocale.DUNGEON_INFO_RANK2_TITLE,
						},
						{
							"name" : "teleport_button_ui",
							"type" : "button",
							"default_image" : REWORK_PATH + "btn_0.png",
							"over_image" :  REWORK_PATH + "btn_1.png",
							"down_image" :  REWORK_PATH + "btn_2.png",
							"x" : 45,
							"y" : 379,
							"horizontal_align" : "center",
							"text" : uiscriptlocale.DUNGEON_INFO_TELEPORT,
						},
						{
							"name" : "fast_enter_button_ui",
							"type" : "button",
							"default_image" : REWORK_PATH + "btn_0.png",
							"over_image" :  REWORK_PATH + "btn_1.png",
							"down_image" :  REWORK_PATH + "btn_2.png",
							"x" : -40,
							"y" : 379,
							"horizontal_align" : "center",
							"text" : uiscriptlocale.PIL_FAST_ENTER_BUTTON,
						},
					),
				},
			),
		},
	),
}
