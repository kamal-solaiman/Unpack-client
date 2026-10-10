# coding: latin_1

import uiscriptlocale

IMG_DIR = "d:/ymir work/ui/game/gameoption/"

TITLE_IMAGE_TEXT_X = 5
TITLE_IMAGE_TEXT_Y = 4

OPTION_START_X = 17
SLIDER_POSITION_X = 50

SLIDER_START_Y = 40
BUTTON_START_Y = 33
BUTTON_NEXT_Y = 20

RADIO_BUTTON_RANGE_X = 65
TOGGLE_BUTTON_RANGE_X = 65

RADIO_BUTTON_TEXT_X = 25
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
			"name" : "tiling_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : 0,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children":
			(
				{
					"name" : "graphic_mode_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR+"option_title.png",
					"children":
					(
						{
							"name" : "title_graphic_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align":"left",
							"text" : uiscriptlocale.OPTION_TILING,
						},
					),
				},
				{
					"name" : "tiling_cpu",
					"type" : "radio_button",
					"x" : OPTION_START_X+RADIO_BUTTON_RANGE_X*0,
					"y" : 33,
					"text" : uiscriptlocale.OPTION_TILING_CPU,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
				{
					"name" : "tiling_gpu",
					"type" : "radio_button",
					"x" : OPTION_START_X+RADIO_BUTTON_RANGE_X*1,
					"y" : 33,
					"text" : uiscriptlocale.OPTION_TILING_GPU,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},
				{
					"name" : "tiling_apply",
					"type" : "button",
					"x" : OPTION_START_X+RADIO_BUTTON_RANGE_X*2,
					"y" : 31,
					"text" : uiscriptlocale.OPTION_TILING_APPLY,
					"default_image" : IMG_DIR + "btn_cat_1.png",
					"over_image" : IMG_DIR + "btn_cat_2.png",
					"down_image" : IMG_DIR + "btn_cat_3.png",
				},
			),
		},
		{
			"name" : "show_name_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT,
			"width":304,
			"height":SMALL_OPTION_HEIGHT,
			"children":
			(
				{
					"name" : "show_damage_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR+"option_title.png",
					"children":
					(
						{
							"name" : "title_show_damage",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align":"left",
							"text" : uiscriptlocale.OPTION_EFFECT,
						},
					),
				},
				{
					"name" : "show_damage_on_button",
					"type" : "radio_button",
					"x" : OPTION_START_X+RADIO_BUTTON_RANGE_X*0,
					"y" : 33,
					"text" : uiscriptlocale.OPTION_VIEW_CHAT_ON,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.tga",
					"over_image" : IMG_DIR + "radio_unselected.tga",
					"down_image" : IMG_DIR + "radio_selected.tga",
				},

				{
					"name" : "show_damage_off_button",
					"type" : "radio_button",
					"x" : OPTION_START_X+RADIO_BUTTON_RANGE_X*1,
					"y" : 33,
					"text" : uiscriptlocale.OPTION_VIEW_CHAT_OFF,
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
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 3,
			"width":304,
			"height":SLIDER_OPTION_HEIGHT,
			"children":
			(
				{
					"name" : "stonesize_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title.png",
					"children":
					(
						{
							"name" : "title_stonesize",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align":"left",
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
							"text" : uiscriptlocale.OPTION_STONESIZE,
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