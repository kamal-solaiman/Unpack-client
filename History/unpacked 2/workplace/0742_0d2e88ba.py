# coding: latin_1

import uiscriptlocale

BOARD_WIDTH = 220
BOARD_HEIGHT = 180

DROPS_LINE_X = 15
DROPS_LINE_X_2 = DROPS_LINE_X + 100

DEFAULT_BTN_IMAGE = "d:/ymir work/ui/public/middle_button_01.sub"
OVER_BTN_IMAGE = "d:/ymir work/ui/public/middle_button_02.sub"
DOWN_BTN_IMAGE = "d:/ymir work/ui/public/middle_button_03.sub"

window = {
	"name" : "PickupOptionDialog",
	"style" : ["float",],
	"x" : (SCREEN_WIDTH + BOARD_WIDTH) / 2,
	"y" : (SCREEN_HEIGHT + BOARD_HEIGHT) / 2,
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
			"title" : uiscriptlocale.EXTENDED_PICKUP_TITLE,
			"children" :
			(
				{
					"name" : "drops_ignore",
					"type" : "text",
					"x" : DROPS_LINE_X,
					"y" : 40,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_LABEL,
				},
				{
					"name" : "drops_ignore_weapon",
					"type" : "toggle_button",
					"x" : DROPS_LINE_X,
					"y" : 62,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_WEAPON_LABEL,
					"default_image" : DEFAULT_BTN_IMAGE,
					"over_image" : OVER_BTN_IMAGE,
					"down_image" : DOWN_BTN_IMAGE,
				},
				{
					"name" : "drops_ignore_armor",
					"type" : "toggle_button",
					"x" : DROPS_LINE_X,
					"y" : 92,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_ARMOR_LABEL,
					"default_image" : DEFAULT_BTN_IMAGE,
					"over_image" : OVER_BTN_IMAGE,
					"down_image" : DOWN_BTN_IMAGE,
				},
				{
					"name" : "drops_ignore_head",
					"type" : "toggle_button",
					"x" : DROPS_LINE_X,
					"y" : 122,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_HEAD_LABEL,
					"default_image" : DEFAULT_BTN_IMAGE,
					"over_image" : OVER_BTN_IMAGE,
					"down_image" : DOWN_BTN_IMAGE,
				},
				{
					"name" : "drops_ignore_shield",
					"type" : "toggle_button",
					"x" : DROPS_LINE_X,
					"y" : 152,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_SHIELD_LABEL,
					"default_image" : DEFAULT_BTN_IMAGE,
					"over_image" : OVER_BTN_IMAGE,
					"down_image" : DOWN_BTN_IMAGE,
				},
				{
					"name" : "drops_ignore_wrist",
					"type" : "toggle_button",
					"x" : DROPS_LINE_X_2,
					"y" : 62,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_WRIST_LABEL,
					"default_image" : DEFAULT_BTN_IMAGE,
					"over_image" : OVER_BTN_IMAGE,
					"down_image" : DOWN_BTN_IMAGE,
				},
				{
					"name" : "drops_ignore_foots",
					"type" : "toggle_button",
					"x" : DROPS_LINE_X_2,
					"y" : 92,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_FOOTS_LABEL,
					"default_image" : DEFAULT_BTN_IMAGE,
					"over_image" : OVER_BTN_IMAGE,
					"down_image" : DOWN_BTN_IMAGE,
				},
				{
					"name" : "drops_ignore_neck",
					"type" : "toggle_button",
					"x" : DROPS_LINE_X_2,
					"y" : 122,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_NECK_LABEL,
					"default_image" : DEFAULT_BTN_IMAGE,
					"over_image" : OVER_BTN_IMAGE,
					"down_image" : DOWN_BTN_IMAGE,
				},
				{
					"name" : "drops_ignore_ear",
					"type" : "toggle_button",
					"x" : DROPS_LINE_X_2,
					"y" : 152,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_EAR_LABEL,
					"default_image" : DEFAULT_BTN_IMAGE,
					"over_image" : OVER_BTN_IMAGE,
					"down_image" : DOWN_BTN_IMAGE,
				},
			),
		},
	),
}
