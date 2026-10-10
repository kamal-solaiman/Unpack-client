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
	"style" : (),
	"x" : 171,
	"y" : 3,
	"width" : 300,
	"height" : 324,
	"children" :
	(
		{
			"name" : "camera_mode_window",
			"type" : "window",
			"style" : ("ltr",),
			"x" : 0,
			"y" : 0,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children":
			(
				{
					"name" : "camera_mode_title_img",
					"type" : "expanded_image",
					"style" : ("ltr",),
					"x" : 5,
					"y" : 0,
					"image" : IMG_DIR+"option_title.png",
					"children":
					(
						{
							"name" : "title_camera_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align":"center",
							"text" : uiscriptlocale.GAME_OPTIONS_TYPE,
						},
					),
				},
				{
					"name" : "camera_level0",
					"type" : "radio_button",
					"style" : ("ltr",),
					"x" : OPTION_START_X+RADIO_BUTTON_RANGE_X*0,
					"y" : 33,
					"text" : uiscriptlocale.OPTION_CAMERA_DISTANCE_SHORT,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
				{
					"name" : "camera_level1",
					"type" : "radio_button",
					"style" : ("ltr",),
					"x" : OPTION_START_X+RADIO_BUTTON_RANGE_X*1,
					"y" : 33,
					"text" : uiscriptlocale.OPTION_CAMERA_DISTANCE_LONG,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
			),
		},
		{
			"name" : "fov_mode_window",
			"type" : "window",
			"style" : ("ltr",),
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children":
			(
				{
					"name" : "fov_mode_title_img",
					"type" : "expanded_image",
					"style" : ("ltr",),
					"x" : 5,
					"y" : 0,
					"image" : IMG_DIR+"option_title.png",
					"children":
					(
						{
							"name" : "title_fov_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align":"center",
							"text" : uiscriptlocale.FOV_OPTION,
						},
					),
				},
				{
					"name" : "fov_off",
					"type" : "radio_button",
					"style" : ("ltr",),
					"x" : OPTION_START_X+RADIO_BUTTON_RANGE_X*0,
					"y" : 33,
					"text" : uiscriptlocale.FOV_OPTION_OFF,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
				{
					"name" : "fov_on",
					"type" : "radio_button",
					"style" : ("ltr",),
					"x" : OPTION_START_X+RADIO_BUTTON_RANGE_X*1,
					"y" : 33,
					"text" : uiscriptlocale.FOV_OPTION_ON,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
			),
		},
		{
			"name" : "stonesize_window",
			"type" : "window",
			"style" : ("ltr",),
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT+NORMAL_OPTION_HEIGHT,
			"width":304,
			"height":SLIDER_OPTION_HEIGHT,
			"children":
			(
				{
					"name" : "stonesize_title_img",
					"type" : "expanded_image",
					"style" : ("ltr",),
					"x" : 5,
					"y" : 0,
					"image" : IMG_DIR + "option_title.png",
					"children":
					(
						{
							"name" : "title_stonesize",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align":"center",
							"text" : uiscriptlocale.OPTION_STONESIZE,
						},
					),
				},
				{
					"name" : "stonesize_controller",
					"type" : "sliderbar",
					"x" : OPTION_START_X + SLIDER_POSITION_X,
					"y" : SLIDER_START_Y,
				},
			),
		},
		{
			"name" : "dmgsize_window",
			"type" : "window",
			"style" : ("ltr",),
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT+NORMAL_OPTION_HEIGHT+SMALL_OPTION_HEIGHT,
			"width":304,
			"height":SLIDER_OPTION_HEIGHT,
			"children":
			(
				{
					"name" : "dmgsize_title_img",
					"type" : "expanded_image",
					"style" : ("ltr",),
					"x" : 5,
					"y" : 0,
					"image" : IMG_DIR + "option_title.png",
					"children":
					(
						{
							"name" : "title_dmgsize",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align":"center",
							"text" : uiscriptlocale.OPTION_DMGSIZE,
						},
					),
				},
				{
					"name" : "scaleEff_Slider",
					"type" : "sliderbar",
					"x" : OPTION_START_X + SLIDER_POSITION_X,
					"y" : SLIDER_START_Y,
				},
			),
		},
	),
}
