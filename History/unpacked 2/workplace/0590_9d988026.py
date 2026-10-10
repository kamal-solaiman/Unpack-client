# coding: latin_1
# Category 4: Sound - Audio and music settings
import uiscriptlocale
import localeinfo

IMG_DIR = "d:/ymir work/ui/game/advanced_game_options/"

TITLE_IMAGE_TEXT_X = 155
TITLE_IMAGE_TEXT_Y = 2

OPTION_START_X = 12
OPTION_START_X_NEW = 12
SLIDER_POSITION_X = 50

SLIDER_START_Y = 40
BUTTON_START_Y = 33
BUTTON_NEXT_Y = 20

RADIO_BUTTON_RANGE_X = 65 + 15
TOGGLE_BUTTON_RANGE_X = 65 + 30

RADIO_BUTTON_TEXT_X = - 15
TOGGLE_BUTTON_TEXT_X = - 10

NORMAL_OPTION_HEIGHT = 80
SLIDER_OPTION_HEIGHT = 65
SLIDER_BAR_X = 31
SMALL_OPTION_HEIGHT = 80
TOGGLE_OPTION_HEIGHT = 80
NAME_VISIBILITY_HEIGHT = SMALL_OPTION_HEIGHT + 70  # Height for the 3-toggle name visibility section


PRIMARY_COLOR = 0xffd0c2b7
SECONDARY_COLOR = 0xff9f9892
DESCRIPTION_COLOR = 0xff8a8078

window = {
	"name" : "GameOptionDialog",
	"style" : (),
	"x" : 222,
	"y" : 1,
	"width" : 371,
	"height" : 404,
	"children" :
	(
		# Volume Controls
		{
			"name" : "volume_window",
			"type" : "window",
			"x" : 0,
			"y" : 5,
			"width" : 360,
			"height" : SLIDER_OPTION_HEIGHT * 2,
			"children" :
			(
				{
					"name" : "volume_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 2,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_volume",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : localeinfo.GAME_OPTIONS_MAIN_2,
						},
					),
				},
				{
					"name" : "sound_text",
					"type" : "text",
					"text_horizontal_align" : "left",
					"x" : SLIDER_BAR_X,
					"y" : SLIDER_START_Y - 20,
					"text" : uiscriptlocale.OPTION_SOUND,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "sound_volume_controller",
					"type" : "sliderbar_advancedgameoptions",
					"x" : SLIDER_BAR_X,
					"y" : SLIDER_START_Y,
				},
				{
					"name" : "music_text",
					"type" : "text",
					"text_horizontal_align" : "left",
					"x" : SLIDER_BAR_X,
					"y" : SLIDER_START_Y * 2 - 20,
					"text" : uiscriptlocale.OPTION_MUSIC,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "music_volume_controller",
					"type" : "sliderbar_advancedgameoptions",
					"x" : SLIDER_BAR_X,
					"y" : SLIDER_START_Y * 2,
				},
			),
		},
		# BGM Selection
		{
			"name" : "bgm_window",
			"type" : "window",
			"x" : 0,
			"y" : 5 + SLIDER_OPTION_HEIGHT * 2,
			"width" : 320,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "bgm_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_bgm",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.MUSICLIST_TITLE,
						},
					),
				},
				{
					"name" : "bgm_file",
					"type" : "text",
					"text_horizontal_align" : "left",
					"x" : OPTION_START_X,
					"y" : BUTTON_START_Y + 5,
					"text" : uiscriptlocale.OPTION_MUSIC_DEFAULT_THEMA,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "bgm_button",
					"type" : "button",
					"x" : 155,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_MUSIC_CHANGE,
					"default_image" : IMG_DIR + "btn_0.png",
					"over_image" : IMG_DIR + "btn_1.png",
					"down_image" : IMG_DIR + "btn_2.png",
				},
			),
		},
	),
}
