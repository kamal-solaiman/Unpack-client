# coding: latin_1

#
# Title: Legendary Enchantment (Custom Select Attributes)
# Description: A legendary enchantment item that allows you to select all 5 bonuses.
# Author: Owsap
# Last Date: 2021.11.24 (YMD)
#
# Skype: owsap.
# Discord: Owsap#7928
#
# Web: https://owsap.dev/
# GitHub: https://github.com/Owsap
#
# 0x0
#

import app
import uiscriptlocale

ROOT = "d:/ymir work/ui/game/setcustomattribute/"

WINDOW_WIDTH = 440
WINDOW_HEIGHT = 228

ITEM_SLOT_WINDOW_WIDTH = 100
ITEM_SLOT_WINDOW_HEIGHT = 184

ATTR_SELECT_WINDOW_WIDTH = 300
ATTR_SELECT_WINDOW_HEIGHT = 184

ATTR_SELECT_TEXT_SLOT_WIDTH = 280

window = {
	"name" : "CustomSelectAttrWindow",
	"style" : ("movable", "float",),

	"x" : SCREEN_WIDTH / 2 - WINDOW_WIDTH / 2,
	"y" : SCREEN_HEIGHT / 2 - WINDOW_HEIGHT / 2,

	"width" : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,

	"children" :
	(
		## Main Board
		{
			"name" : "Board",
			"type" : "board_with_titlebar",

			"x" : 0, "y" : 0,
			"width" : WINDOW_WIDTH, "height" : WINDOW_HEIGHT,

			"title" : uiscriptlocale.SET_CUSTOM_ATTR_TITLE,
		},

		## Board Image
		{
			"name" : "BoardImage",
			"type" : "image",
			"style" : ("ltr",),

			"x" : 8, "y" : 30,

			"image" : ROOT + "backgroundpct.png",
		},

		## Enchantment Probability Window
		{
			"name" : "EnchantProbabilityWindow",
			"type" : "window",
			"style" : ("attach", "ltr",),

			"x" : 51, "y" : 41,
			"vertical_align" : "bottom",
			"width" : 35, "height" : 13,

			"children" :
			(
				## Probability Text
				{
					"name" : "EnchantProbabilityText",
					"type" : "text",

					"x" : 2, "y" : 0,
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",

					"text" : "0%",
				},
			),
		},

		## Item Slot Window
		{
			"name" : "ItemSlotWindow",
			"type" : "window",
			"style" : ("attach", "ltr",),

			"x" : 10, "y" : 32,
			"width" : ITEM_SLOT_WINDOW_WIDTH, "height" : ITEM_SLOT_WINDOW_HEIGHT,

			"children" :
			(
				## Item Slot Image
				{
					"name" : "ItemSlotImage",
					"type" : "window",
					"style" : ("ltr",),

					"x" : 60 - 40, "y" : 68 - 45,
					"height" : 80, "width" : 32,

					"children" :
					(
						## Item Slot
						{
							"name" : "ItemSlot",
							"type" : "slot",

							"x" : 0, "y" : 0,
							"width" : 44, "height" : 107,

							"slot" : ( { "index" : 0, "x" : 6, "y" : 6, "width" : 32, "height" : 96}, )
						},
					),
				},
			),
		},

		## Attribute Select Window
		{
			"name" : "AttrSelectWindow",
			"type" : "window",
			"style" : ("attach", "ltr",),

			"x" : 115, "y" : 20,
			"width" : ATTR_SELECT_WINDOW_WIDTH, "height" : ATTR_SELECT_WINDOW_HEIGHT,

			"children" :
			(
				## Attribute Slot 1
				{
					"name" : "AttrSlot1", "type" : "thinboard_circle", "x" : 0, "y" : 30, "width" : ATTR_SELECT_TEXT_SLOT_WIDTH, "height" : 21, "horizontal_align" : "center",
					"children" : (
						{ "name" : "AttrSlotText1", "type" : "text", "x" : 0, "y" : 3, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : "", },
						{ "name" : "AttrSlotText1Previous", "type" : "button", "x" : 4, "y" : 4, "default_image" : ROOT + "left_arrow_default.png", "over_image" : ROOT + "left_arrow_over.png", "down_image" : ROOT + "left_arrow_down.png", },
						{ "name" : "AttrSlotText1Next", "type" : "button", "x" : ATTR_SELECT_TEXT_SLOT_WIDTH - 18, "y" : 4, "default_image" : ROOT + "right_arrow_default.png", "over_image" : ROOT + "right_arrow_over.png", "down_image" : ROOT + "right_arrow_down.png", },
					),
				},
				## Attribute Slot 2
				{
					"name" : "AttrSlot2", "type" : "thinboard_circle", "x" : 0, "y" : 30 + 25, "width" : ATTR_SELECT_TEXT_SLOT_WIDTH, "height" : 21, "horizontal_align" : "center",
					"children" : (
						{ "name" : "AttrSlotText2", "type" : "text", "x" : 0, "y" : 3, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : "", },
						{ "name" : "AttrSlotText2Previous", "type" : "button", "x" : 4, "y" : 4, "default_image" : ROOT + "left_arrow_default.png", "over_image" : ROOT + "left_arrow_over.png", "down_image" : ROOT + "left_arrow_down.png", },
						{ "name" : "AttrSlotText2Next", "type" : "button", "x" : ATTR_SELECT_TEXT_SLOT_WIDTH - 18, "y" : 4, "default_image" : ROOT + "right_arrow_default.png", "over_image" : ROOT + "right_arrow_over.png", "down_image" : ROOT + "right_arrow_down.png", },
					),
				},
				## Attribute Slot 3
				{
					"name" : "AttrSlot3", "type" : "thinboard_circle", "x" : 0, "y" : 30 + 25 + 25, "width" : ATTR_SELECT_TEXT_SLOT_WIDTH, "height" : 21, "horizontal_align" : "center",
					"children" : (
						{ "name" : "AttrSlotText3", "type" : "text", "x" : 0, "y" : 3, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : "", },
						{ "name" : "AttrSlotText3Previous", "type" : "button", "x" : 4, "y" : 4, "default_image" : ROOT + "left_arrow_default.png", "over_image" : ROOT + "left_arrow_over.png", "down_image" : ROOT + "left_arrow_down.png", },
						{ "name" : "AttrSlotText3Next", "type" : "button", "x" : ATTR_SELECT_TEXT_SLOT_WIDTH - 18, "y" : 4, "default_image" : ROOT + "right_arrow_default.png", "over_image" : ROOT + "right_arrow_over.png", "down_image" : ROOT + "right_arrow_down.png", },
					),
				},
				## Attribute Slot 4
				{
					"name" : "AttrSlot4", "type" : "thinboard_circle", "x" : 0, "y" : 30 + 25 + 25 + 25, "width" : ATTR_SELECT_TEXT_SLOT_WIDTH, "height" : 21, "horizontal_align" : "center",
					"children" : (
						{ "name" : "AttrSlotText4", "type" : "text", "x" : 0, "y" : 3, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : "", },
						{ "name" : "AttrSlotText4Previous", "type" : "button", "x" : 4, "y" : 4, "default_image" : ROOT + "left_arrow_default.png", "over_image" : ROOT + "left_arrow_over.png", "down_image" : ROOT + "left_arrow_down.png", },
						{ "name" : "AttrSlotText4Next", "type" : "button", "x" : ATTR_SELECT_TEXT_SLOT_WIDTH - 18, "y" : 4, "default_image" : ROOT + "right_arrow_default.png", "over_image" : ROOT + "right_arrow_over.png", "down_image" : ROOT + "right_arrow_down.png", },
					),
				},
				## Attribute Slot 5
				{
					"name" : "AttrSlot5", "type" : "thinboard_circle", "x" : 0, "y" : 30 + 25 + 25 + 25 + 25, "width" : ATTR_SELECT_TEXT_SLOT_WIDTH, "height" : 21, "horizontal_align" : "center",
					"children" : (
						{ "name" : "AttrSlotText5", "type" : "text", "x" : 0, "y" : 3, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : "", },
						{ "name" : "AttrSlotText5Previous", "type" : "button", "x" : 4, "y" : 4, "default_image" : ROOT + "left_arrow_default.png", "over_image" : ROOT + "left_arrow_over.png", "down_image" : ROOT + "left_arrow_down.png", },
						{ "name" : "AttrSlotText5Next", "type" : "button", "x" : ATTR_SELECT_TEXT_SLOT_WIDTH - 18, "y" : 4, "default_image" : ROOT + "right_arrow_default.png", "over_image" : ROOT + "right_arrow_over.png", "down_image" : ROOT + "right_arrow_down.png", },
					),
				},

				## Change Button
				{
					"name" : "EnchantButton",
					"type" : "button",

					"x" : 0, "y" : 22,
					"horizontal_align" : "center",
					"vertical_align" : "bottom",

					"text" : uiscriptlocale.SET_CUSTOM_ATTR_ENCHANT_BUTTON,

					"default_image" :"d:/ymir work/ui/public/xLarge_Button_01.sub",
					"over_image" :"d:/ymir work/ui/public/xLarge_Button_02.sub",
					"down_image" :"d:/ymir work/ui/public/xLarge_Button_03.sub",
				},
			),
		},

		## ToolTip Button
		{
			"name" : "ToolTipButton",
			"type" : "button",

			"x" : 60, "y" : 60,
			"vertical_align" : "bottom",

			"default_image" : "d:/ymir work/ui/pattern/q_mark_01.tga",
			"over_image" : "d:/ymir work/ui/pattern/q_mark_02.tga",
			"down_image" : "d:/ymir work/ui/pattern/q_mark_01.tga",
		},
	),
}
