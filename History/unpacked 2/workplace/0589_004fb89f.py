# coding: latin_1
# Category 3: Environment - Weather, lighting, and world effects
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
		# Fog Mode (conditional)
		{
			"name" : "fog_mode_window",
			"type" : "window",
			"x" : 2,
			"y" : 8,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "fog_mode_title_img",
					"type" : "expanded_image",
					"x" : 5,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_fog_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_FOG,
						},
					),
				},
				{
					"name" : "fog_on",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_FOG_ON,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "fog_off",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_FOG_OFF,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Night Mode (conditional)

		# Snow Mode (conditional)
		{
			"name" : "snow_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : 5 + SMALL_OPTION_HEIGHT,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "snow_mode_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_snow_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_SNOW_MODE,
						},
					),
				},
				{
					"name" : "snow_mode_on",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SNOW_MODE_ON,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "snow_mode_off",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SNOW_MODE_OFF,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Snow Texture Mode (conditional)
		{
			"name" : "snowtexture_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : 5 + SMALL_OPTION_HEIGHT * 2,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "snowtexture_mode_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_snowtexture_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_SNOW_TEXTURE_MODE,
						},
					),
				},
				{
					"name" : "snowtexture_mode_on",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SNOW_TEXTURE_MODE_ON,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "snowtexture_mode_off",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SNOW_TEXTURE_MODE_OFF,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		{
			"name" : "shadow_target_window",
			"type" : "window",
			"x" : 0,
			"y" : 5 + SMALL_OPTION_HEIGHT * 3,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "shadow_target_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_shadow_target",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "left",
							"text" : uiscriptlocale.OPTION_SHADOW_TARGET,
						},
					),
				},
				{
					"name" : "shadow_target_none",
					"type" : "radio_button",
					"x" : OPTION_START_X + 55 * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SHADOW_TARGET_NONE,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_SHADOW_TARGET_NONE,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "shadow_target_ground",
					"type" : "radio_button",
					"x" : OPTION_START_X + 55 * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SHADOW_TARGET_GROUND,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_SHADOW_TARGET_GROUND,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "shadow_target_ground_and_solo",
					"type" : "radio_button",
					"x" : OPTION_START_X + 55 * 2,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SHADOW_TARGET_GROUND_AND_SOLO,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_SHADOW_TARGET_GROUND_AND_SOLO,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "shadow_target_all",
					"type" : "radio_button",
					"x" : OPTION_START_X + 55 * 3,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SHADOW_TARGET_ALL,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_SHADOW_TARGET_ALL,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Shadow Quality (conditional)
		{
			"name" : "shadow_quality_window",
			"type" : "window",
			"x" : 0,
			"y" : 5 + SMALL_OPTION_HEIGHT * 4,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "shadow_quality_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_shadow_quality",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "left",
							"text" : uiscriptlocale.OPTION_SHADOW_QUALITY,
						},
					),
				},
				{
					"name" : "shadow_quality_bad",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SHADOW_QUALITY_BAD,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "shadow_quality_average",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SHADOW_QUALITY_AVERAGE,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "shadow_quality_good",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SHADOW_QUALITY_GOOD,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Tree Shadow (on/off toggle)
		{
			"name" : "tree_shadow_window",
			"type" : "window",
			"x" : 0,
			"y" : 5 + SMALL_OPTION_HEIGHT * 5,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "tree_shadow_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_tree_shadow",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : localeinfo.NEW_OPTION_SHADOW,
						},
					),
				},
				{
					"name" : "tree_shadow_on",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_FOG_ON,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "tree_shadow_off",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_FOG_OFF,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Tree LOD Quality
		{
			"name" : "tree_lod_window",
			"type" : "window",
			"x" : 0,
			"y" : 5 + SMALL_OPTION_HEIGHT * 6,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "tree_lod_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_tree_lod",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : localeinfo.NEW_OPTION_SHADOW_QUALITY,
						},
					),
				},
				{
					"name" : "tree_lod_low",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SHADOW_QUALITY_BAD,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "tree_lod_medium",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SHADOW_QUALITY_AVERAGE,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "tree_lod_high",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SHADOW_QUALITY_GOOD,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
	),
}
