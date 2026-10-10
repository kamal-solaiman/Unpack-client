# coding: latin_1

import uiscriptlocale
import localeinfo

IMG_DIR = "d:/ymir work/ui/game/gameoption/"

if localeinfo.IsARABIC():
	TITLE_IMAGE_TEXT_X = 30+55
else:
	TITLE_IMAGE_TEXT_X = 5

TITLE_IMAGE_TEXT_Y = 4

OPTION_START_X = 17
SLIDER_POSITION_X = 50

SLIDER_START_Y = 40
BUTTON_START_Y = 33
BUTTON_NEXT_Y = 20

if localeinfo.IsARABIC():
	RADIO_BUTTON_RANGE_X = 80
else:
	RADIO_BUTTON_RANGE_X = 65

if localeinfo.IsARABIC():
	TOGGLE_BUTTON_RANGE_X = 85
else:
	TOGGLE_BUTTON_RANGE_X = 65

if localeinfo.IsARABIC():
	RADIO_BUTTON_TEXT_X = 55
else:
	RADIO_BUTTON_TEXT_X = 25

TOGGLE_BUTTON_TEXT_X = 20

SMALL_OPTION_HEIGHT = 65
NORMAL_OPTION_HEIGHT = 80
SLIDER_OPTION_HEIGHT = 65

window = {
	"name" : "GameOptionDialog",
	"style" : (),
	"x" : 171,
	"y" : 3,
	"width" : 300,
	"height" : 324,
	"children" :
	(
		{
			"name" : "pickup_mode_window",
			"type" : "window",
			"style" : ("ltr",),
			"x" : 0,
			"y" : 0,
			"width":304,
			"height": SMALL_OPTION_HEIGHT * 2,
			"children":
			(
				{
					"name" : "pickup_mode_title_img",
					"type" : "expanded_image",
					"style" : ("ltr",),
					"x" : 5,
					"y" : 0,
					"image" : IMG_DIR+"option_title.png",
					"children":
					(
						{
							"name" : "title_pickup_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align":"center",
							"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_LABEL,
						},
					),
				},
				{
					"name" : "shadow_target_none",
					"type" : "radio_button",
					"style" : ("ltr",),
					"x" : OPTION_START_X+TOGGLE_BUTTON_RANGE_X*0,
					"y" : 33,
					"text" : "1",
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_SHADOW_TARGET_NONE,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
				{
					"name" : "shadow_target_ground",
					"type" : "radio_button",
					"style" : ("ltr",),
					"x" : OPTION_START_X+TOGGLE_BUTTON_RANGE_X*1,
					"y" : 33,
					"text" : "2",
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_SHADOW_TARGET_GROUND,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
				{
					"name" : "shadow_target_ground_and_solo",
					"type" : "radio_button",
					"style" : ("ltr",),
					"x" : OPTION_START_X+TOGGLE_BUTTON_RANGE_X*2,
					"y" : 33,
					"text" : "3",
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_SHADOW_TARGET_GROUND_AND_SOLO,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
				{
					"name" : "shadow_target_all",
					"type" : "radio_button",
					"style" : ("ltr",),
					"x" : OPTION_START_X+TOGGLE_BUTTON_RANGE_X*0,
					"y" : 33 * 2,
					"text" : "4",
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_SHADOW_TARGET_ALL,

					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
			),
		},
		{
			"name" : "shadows_quality",
			"type" : "window",
			"style" : ("ltr",),
			"x" : 0,
			"y" : (SMALL_OPTION_HEIGHT * 3) - 80,
			"width":304,
			"height": SMALL_OPTION_HEIGHT * 2,
			"children":
			(
				{
					"name" : "shadows_quality_img",
					"type" : "expanded_image",
					"style" : ("ltr",),
					"x" : 5,
					"y" : 0,
					"image" : IMG_DIR+"option_title.png",
					"children":
					(
						{
							"name" : "shadows_quality_text",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align":"center",
							"text" : uiscriptlocale.EXTENDED_PICKUP_SHADOWS_QUALITY_LABEL,
						},
					),
				},
				{
					"name" : "shadow_quality_bad",
					"type" : "radio_button",
					"style" : ("ltr",),
					"x" : OPTION_START_X+TOGGLE_BUTTON_RANGE_X*0,
					"y" : 33,
					"text" : "1",
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_SHADOW_QUALITY_BAD,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
				{
					"name" : "shadow_quality_average",
					"type" : "radio_button",
					"style" : ("ltr",),
					"x" : OPTION_START_X+TOGGLE_BUTTON_RANGE_X*1,
					"y" : 33,
					"text" : "2",
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_SHADOW_QUALITY_AVERAGE,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
				{
					"name" : "shadow_quality_good",
					"type" : "radio_button",
					"style" : ("ltr",),
					"x" : OPTION_START_X+TOGGLE_BUTTON_RANGE_X*2,
					"y" : 33,
					"text" : "3",
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_SHADOW_QUALITY_GOOD,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
			),
		},
	),
}
