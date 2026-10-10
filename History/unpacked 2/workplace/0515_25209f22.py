# coding: latin_1

import uiscriptlocale
import localeinfo

BOARD_WIDTH = 374
BOARD_HEIGHT = 390

PAGE_LEFT_X_DIST = 10
PAGE_RIGHT_X_DIST = 10
PAGE_X_DIST = PAGE_LEFT_X_DIST + PAGE_RIGHT_X_DIST

PAGE_TOP_DIST = 33
PAGE_BOT_DIST = 10

TAB_Y = PAGE_TOP_DIST
TAB_HEIGHT = 25
CONTENT_Y = TAB_Y + TAB_HEIGHT
CONTENT_HEIGHT = BOARD_HEIGHT - (CONTENT_Y + PAGE_BOT_DIST)

ROOT_PATH = "biolog_manager/"
NEW_PATH = "d:/ymir work/ui/bio_rework/"

# Background image (328x279) centered in content area
BG_X = (BOARD_WIDTH - PAGE_X_DIST - 328) / 2
BG_Y = (CONTENT_HEIGHT - 279) / 2

window = {
	"name" : "BiologManagerWindow",
	"style" : ("movable", "float",),

	"x" : 0,
	"y" : 0,

	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,

	"children" :
	[
		{
			"name" : "BiologBoard",
			"type" : "board",
			"style" : ("attach", "ltr"),

			"x" : 0,
			"y" : 0,

			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,

			"children" :
			[
				{
					"name" : "TitleBar",
					"type" : "titlebar",
					"style" : ("attach",),

					"x" : 8,
					"y" : 7,

					"width" : BOARD_WIDTH - 15,
					"color" : "yellow",

					"children" :
					(
						{ "name":"TitleName", "type":"text", "x": (BOARD_WIDTH - 15) / 2, "y":3, "text":uiscriptlocale.BIOLOG_MANAGER_TITLE, "text_horizontal_align":"center" },
					),
				},

				## Tab Buttons
				{
					"name" : "TabCurrent",
					"type" : "radio_button",

					"x" : 193,
					"y" : 32,

					"default_image" : NEW_PATH + "overview_button_down.png",
					"over_image" : NEW_PATH + "overview_button_over.png",
					"down_image" : NEW_PATH + "overview_button_normal.png",

					"text" : localeinfo.BIOLOG_OVERVIEW_TAB_CURRENT,
					"outline" : 1
				},
				{
					"name" : "TabOverview",
					"type" : "radio_button",

					"x" : 22,
					"y" : 32,

					"default_image" : NEW_PATH + "overview_button_down.png",
					"over_image" : NEW_PATH + "overview_button_over.png",
					"down_image" : NEW_PATH + "overview_button_normal.png",

					"text" : localeinfo.BIOLOG_OVERVIEW_TAB_ALL,
				},

				## Current Mission Content (new UI)
				{
					"name" : "ThinBoardMain",
					"type" : "v2_thinboard",

					"x" : PAGE_LEFT_X_DIST,
					"y" : CONTENT_Y,

					"width" : BOARD_WIDTH - PAGE_X_DIST,
					"height" : CONTENT_HEIGHT,
					"children" :
					[
						## Background image
						{
							"name" : "MainBG",
							"type" : "image",
							"x" : BG_X,
							"y" : BG_Y,
							"image" : NEW_PATH + "background_image_2.png",
						},

						## Section 1: Level header + NPC portrait + delievery text and gauge
						{
							"name" : "SeonImage",
							"type" : "image",
							"x" : BG_X + 280,
							"y" : BG_Y + 2,
							"image" : ROOT_PATH + "seon_image.png",
						},
						{
							"name" : "BiologRequiredLevel",
							"type" : "text",
							"x" : BG_X + 180,
							"y" : BG_Y + 7,
							"text_horizontal_align" : "center",
							"text" : "Mission Biolog: Lv 30",
						},
						{
							"name" : "DeliveryGaugeEmpty",
							"type" : "image",
							"x" : 137,
							"y" : 53,
							"image" : NEW_PATH + "fill_count-empty.png",
						},

						## Section 2: Delivery progress (item slot + buttons + checkboxes)  + reminder checkbox and image
						{
							"name" : "BiologRequiredItem",
							"type" : "slot",
							"x" : 297,
							"y" : 93,
							"width" : 32,
							"height" : 32,
							"slot" : ({"index":0, "x":0, "y":0, "width":32, "height":32},),
						},

						{
							"name" : "BiologItemInfo",
							"type" : "text",
							"x" : BG_X + 77,
							"y" : BG_Y + 30,
							"text_horizontal_align" : "left",
							"text" : "",
						},
						{
							"name" : "AdditionalCheckbox_0",
							"type" : "checkbox_biolog",
							"x" : BG_X + 74,
							"y" : 102 - 18,
						},
						{
							"name" : "AdditionalItem_0",
							"type" : "slot",
							"x" : 190,
							"y" : 102,
							"width" : 32,
							"height" : 32,
							"slot" : ({"index":0, "x":0, "y":0, "width":32, "height":32},),
						},
						# {
							# "name" : "AdditionalItem_2",
							# "type" : "slot",
							# "x" : 190,
							# "y" : 101,
							# "width" : 32,
							# "height" : 32,
							# "slot" : ({"index":0, "x":0, "y":0, "width":32, "height":32},),
						# },
						{
							"name" : "AdditionalCheckbox_1",
							"type" : "checkbox_biolog",
							"x" : BG_X + 130,
							"y" : 102 - 18,
							
						},
						{
							"name" : "AdditionalItem_1",
							"type" : "slot",
							"x" : 242,
							"y" : 102,
							"width" : 32,
							"height" : 32,
							"slot" : ({"index":0, "x":0, "y":0, "width":32, "height":32},),
						},
						{
							"name" : "SubmitMissionButton",
							"type" : "button",
							"x" : 169,
							"y" : 110,
							"default_image" : NEW_PATH + "deliver_button_normal.png",
							"over_image" : NEW_PATH + "deliver_button_over.png",
							"down_image" : NEW_PATH + "deliver_button_down.png",
							"disable_image" : NEW_PATH + "deliver_button_down.png",
						},
						{
							"name" : "SubmitSubMissionButton",
							"type" : "button",
							"x" : 169,
							"y" : 110,
							"default_image" : NEW_PATH + "deliver_button_normal.png",
							"over_image" : NEW_PATH + "deliver_button_over.png",
							"down_image" : NEW_PATH + "deliver_button_down.png",
							"disable_image" : NEW_PATH + "deliver_button_down.png",
						},
						{
							"name" : "BiologShop",
							"type" : "button",
							"Tooltip_text" : localeinfo.BIO_SHOP_NAME,
							"x" : 256,
							"y" : 110,
							"default_image" : NEW_PATH + "shop_button_normal.png",
							"over_image" : NEW_PATH + "shop_button_over.png",
							"down_image" : NEW_PATH + "shop_button_down.png",
						},
						
						{
							"name" : "CheckBoxReminder",
							"type" : "checkbox_biolog",
							"x" : BG_X + 200,
							"y" : 102 - 15,
						},
						{
							"name" : "CooldownImage",
							"type" : "image",
							"x" : 189,
							"y" : 85,
							"image" : ROOT_PATH + "clock.tga",
						},

						## Section 3: Timer 
						{
							"name" : "BiologCooldownInfo",
							"type" : "text",
							"x" : BG_X + 75,
							"y" : BG_Y + 130,
							"text_horizontal_align" : "center",
							"text" : "",
						},


						## Section 4: Cooldown timer gauge
						{
							"name" : "CooldownGaugeEmpty",
							"type" : "image",
							"x" : 155,
							"y" : 154,
							"image" : NEW_PATH + "fill_time_remaining.png",
						},

						## Section 5: Effects + reward
						{
							"name" : "BiologRewardItem",
							"type" : "slot",
							"x" : BG_X + 270,
							"y" : BG_Y + 215,
							"width" : 32,
							"height" : 32,
							"slot" : ({"index":0, "x":0, "y":0, "width":32, "height":32},),
						},
						{
							"name" : "RewardsStorage",
							"type" : "listboxex",
							"x" : 97,
							"y" : 210,
							"width" : 240,
							"height" : 70,
							"itemsize_x" : 240,
							"itemsize_y" : 15,
							"itemstep" : 15,
							"viewcount" : 5,
						},
					],
				},

				## Overview Content (hidden by default)
				{
					"name" : "OverviewBoard",
					"type" : "v2_thinboard",

					"x" : PAGE_LEFT_X_DIST,
					"y" : CONTENT_Y,

					"width" : BOARD_WIDTH - PAGE_X_DIST,
					"height" : CONTENT_HEIGHT,

					"children" :
					[
						{
							"name" : "OverviewList",
							"type" : "listboxex",

							"x" : 8,
							"y" : 30,

							"width" : 312,
							"height" : 270,

							"itemsize_x" : 312,
							"itemsize_y" : 34,

							"itemstep" : 34,
							"viewcount" : 8,
						},
						{
							"name" : "OverviewScrollBar",
							"type" : "scrollbarnew",

							"x" : 332,
							"y" : 29,

							"size" : 272,
						},
					],
				},
			],
		},
	],
}
