# coding: latin_1

import uiscriptlocale
import localeinfo

IMG_DIR = "d:/ymir work/ui/game/gameoption/"

if localeinfo.IsARABIC():
	TITLE_IMAGE_TEXT_X = 30+50
else:
	TITLE_IMAGE_TEXT_X = 5

TITLE_IMAGE_TEXT_Y = 4

OPTION_START_X = 17
SLIDER_POSITION_X = 50

SLIDER_START_Y = 40
BUTTON_START_Y = 33
BUTTON_NEXT_Y = 20

RADIO_BUTTON_RANGE_X = 65
TOGGLE_BUTTON_RANGE_X = 65

if localeinfo.IsARABIC():
	RADIO_BUTTON_TEXT_X = 50
else:
	RADIO_BUTTON_TEXT_X = 25

if localeinfo.IsARABIC():
	TOGGLE_BUTTON_TEXT_X = 48
else:
	TOGGLE_BUTTON_TEXT_X = 20

SMALL_OPTION_HEIGHT = 65
NORMAL_OPTION_HEIGHT = 80
SLIDER_OPTION_HEIGHT = 65


window = {
	"name" : "GameOptionDialog",
	# Dont touch these lines!
	"style" : (),
	"x" : 171,
	"y" : 3,
	"width" : 300,
	"height" : 324,
	# Dont touch these lines!
	"children" :
	(
		{
			"name" : "sound_window",
			"type" : "window",
			"style" : ("ltr",),
			"x" : 0,
			"y" : 0,
			"width":304,
			"height":SLIDER_OPTION_HEIGHT,
			"children":
			(
				{
					"name" : "sound_title_img",
					"type" : "expanded_image",
					"style" : ("ltr",),
					"x" : 5,
					"y" : 0,
					"image" : IMG_DIR+"option_title.png",
					"children":
					(
						{
							"name" : "title_sound",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align":"center",
							"text" : uiscriptlocale.OPTION_SOUND,
						},
					),
				},
				{
					"name" : "sound_volume_controller",
					"type" : "sliderbar",
					"style" : ("ltr",),
					"x" : OPTION_START_X+SLIDER_POSITION_X,
					"y" : SLIDER_START_Y,
				},
			),
		},
		{
			"name" : "bgm_window",
			"type" : "window",
			"style" : ("ltr",),
			"x" : 0,
			"y" : SLIDER_OPTION_HEIGHT,
			"width":304,
			"height":SLIDER_OPTION_HEIGHT+SLIDER_OPTION_HEIGHT,
			"children":
			(
				{
					"name" : "bgm_title_img",
					"type" : "expanded_image",
					"style" : ("ltr",),
					"x" : 5,
					"y" : 0,
					"image" : IMG_DIR+"option_title.png",
					"children":
					(
						{
							"name" : "title_bgm",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align":"center",
							"text" : uiscriptlocale.OPTION_MUSIC,
						},
					),
				},
				{
					"name" : "music_volume_controller",
					"type" : "sliderbar",
					"style" : ("ltr",),
					"x" : OPTION_START_X+SLIDER_POSITION_X,
					"y" : SLIDER_START_Y,
				},
				{
					"name" : "bgm_file",
					"type" : "text",
					"text_horizontal_align":"center",
					"x" : 304/2,
					"y" : SLIDER_START_Y+20,
					"text":uiscriptlocale.OPTION_MUSIC_DEFAULT_THEMA,
				},
				{
					"name" : "bgm_button",
					"type" : "button",
					"style" : ("ltr",),
					"x" : 80,
					"y" : SLIDER_START_Y+20+20,
					
					"text" : uiscriptlocale.OPTION_MUSIC_CHANGE,
					"default_image" : IMG_DIR + "btn_cat_1.png",
					"over_image" : IMG_DIR + "btn_cat_2.png",
					"down_image" : IMG_DIR + "btn_cat_3.png",
				},
			),
		},
	),
}
