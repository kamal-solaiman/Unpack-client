# coding: latin_1
# Category 1: Game - Gameplay and interaction settings

import uiscriptlocale

IMG_DIR = "d:/ymir work/ui/game/advanced_game_options/"
IMG_SKY = "d:/ymir work/ui/game/advanced_game_options/sky/"

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
		# PvP Mode
		{
			"name" : "pvp_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : 0,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "pvp_mode_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 2,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_pvp_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_PVPMODE,
						},
					),
				},
				{
					"name" : "pvp_peace",
					"type" : "radio_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_PVPMODE_PEACE,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pvp_revenge",
					"type" : "radio_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_PVPMODE_REVENGE,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pvp_guild",
					"type" : "radio_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_PVPMODE_GUILD,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pvp_free",
					"type" : "radio_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 3,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_PVPMODE_FREE,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Block Mode
		{
			"name" : "block_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT,
			"width" : 304,
			"height" : NORMAL_OPTION_HEIGHT + 20,
			"children" :
			(
				{
					"name" : "block_mode_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_block_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_BLOCK,
						},
					),
				},
				{
					"name" : "block_exchange_button",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_BLOCK_EXCHANGE,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "block_party_button",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_BLOCK_PARTY,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "block_guild_button",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_BLOCK_GUILD,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "block_whisper_button",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y + BUTTON_NEXT_Y + 10,
					"text" : uiscriptlocale.OPTION_BLOCK_WHISPER,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "block_friend_button",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y + BUTTON_NEXT_Y + 10,
					"text" : uiscriptlocale.OPTION_BLOCK_FRIEND,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "block_party_request_button",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y + BUTTON_NEXT_Y + 10,
					"text" : uiscriptlocale.OPTION_BLOCK_PARTY_REQUEST,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},

				
			),
		},
		
		
		# pickup ignore modes Mode
		{
			"name" : "pickup_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT + NORMAL_OPTION_HEIGHT + 20,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT + 40,
			"children" :
			(
				{
					"name" : "pickup_mode_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 2,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_pickup_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.EXTENDED_PICKUP_TITLE,
						},
					),
				},
				{
					"name" : "drops_ignore_weapon",
					"type" : "toggle_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_WEAPON_LABEL,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected_2.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "drops_ignore_armor",
					"type" : "toggle_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_ARMOR_LABEL,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected_2.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "drops_ignore_head",
					"type" : "toggle_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_HEAD_LABEL,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected_2.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "drops_ignore_shield",
					"type" : "toggle_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 3,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_SHIELD_LABEL,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected_2.png",
					"color" : PRIMARY_COLOR,
				},
				
				{
					"name" : "drops_ignore_wrist",
					"type" : "toggle_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y + 40,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_WRIST_LABEL,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected_2.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "drops_ignore_foots",
					"type" : "toggle_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y + 40,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_FOOTS_LABEL,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected_2.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "drops_ignore_neck",
					"type" : "toggle_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y + 40,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_NECK_LABEL,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected_2.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "drops_ignore_ear",
					"type" : "toggle_button",
					"x" : OPTION_START_X_NEW + RADIO_BUTTON_RANGE_X * 3,
					"y" : BUTTON_START_Y + 40,
					"text" : uiscriptlocale.EXTENDED_PICKUP_IGNORE_EAR_LABEL,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected_2.png",
					"color" : PRIMARY_COLOR,
				},
				
				{
					"name" : "pickup_description",
					"type" : "text",
					"x" : 64,
					"y" : BUTTON_START_Y + 70,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_PICKUP_DESC,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				
				
			),
		},
		#new sky and dark mode
		{
			"name" : "night_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : 80 + SMALL_OPTION_HEIGHT + NORMAL_OPTION_HEIGHT * 2,
			"width" : 334,
			"height" : 260,
			"children" :
			(
				{
					"name" : "night_mode_title_img",
					"type" : "expanded_image",
					"x" : 5,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_night_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_ENV_MODE,
						},
					),
				},
				{
					"name" : "night_mode_toggle",
					"type" : "toggle_button",
					"x" : 60,
					"y" : BUTTON_START_Y + 5,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "night_mode_label",
					"type" : "text",
					"x" : 60 + 50,
					"y" : BUTTON_START_Y + 5,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_NIGHT_MODE,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "save_env_toggle",
					"type" : "toggle_button",
					"x" : 205 ,
					"y" : BUTTON_START_Y + 5 + 5,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
				},
				{
					"name" : "save_enve_label",
					"type" : "text",
					"x" : 205 + 20,
					"y" : BUTTON_START_Y + 3 + 5,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_ENV_SAVE,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "save_enve_description",
					"type" : "text",
					"x" : 64 + 40,
					"y" : BUTTON_START_Y + 30,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_ENV_SAVE_DESC,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				{
					"name" : "showNight_1_button",
					"type" : "radio_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y + 60,
					"text" : "",
					"text_x" : 0,
					"default_image" : IMG_SKY + "sky2_d.dds",
					"over_image" : IMG_SKY + "sky2.dds",
					"down_image" : IMG_SKY + "sky2_o.dds",
				},
				{
					"name" : "showNight_2_button",
					"type" : "radio_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y + 60,
					"text" : "",
					"text_x" : 0,
					"default_image" : IMG_SKY + "sky3_d.dds",
					"over_image" : IMG_SKY + "sky3.dds",
					"down_image" : IMG_SKY + "sky3_o.dds",
				},
				{
					"name" : "showNight_3_button",
					"type" : "radio_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y + 60,
					"text" : "",
					"text_x" : 0,
					"default_image" : IMG_SKY + "sky4_d.dds",
					"over_image" : IMG_SKY + "sky4.dds",
					"down_image" : IMG_SKY + "sky4_o.dds",
				},
				
				{
					"name" : "showNight_4_button",
					"type" : "radio_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y + 40 + 55 + 20 ,
					"text" : "",
					"text_x" : 0,
					"default_image" : IMG_SKY + "sky5.dds",
					"over_image" : IMG_SKY + "sky5.dds",
					"down_image" : IMG_SKY + "sky5o.dds",
				},
				{
					"name" : "showNight_5_button",
					"type" : "radio_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y + 40 + 55 + 20,
					"text" : "",
					"text_x" : 0,
					"default_image" : IMG_SKY + "sky6.dds",
					"over_image" : IMG_SKY + "sky6d.dds",
					"down_image" : IMG_SKY + "sky6o.dds",
				},
				{
					"name" : "showNight_6_button",
					"type" : "radio_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y + 40 + 55 + 20,
					"text" : "",
					"text_x" : 0,
					"default_image" : IMG_SKY + "sky7.dds",
					"over_image" : IMG_SKY + "sky7d.dds",
					"down_image" : IMG_SKY + "sky7o.dds",
				},
				
				{
					"name" : "showNight_7_button",
					"type" : "radio_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y + 40 + 55 + 55 + 20,
					"text" : "",
					"text_x" : 0,
					"default_image" : IMG_SKY + "sky8.dds",
					"over_image" : IMG_SKY + "sky8.dds",
					"down_image" : IMG_SKY + "sky8o.dds",
				},
				{
					"name" : "showNight_8_button",
					"type" : "radio_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y + 40 + 55 + 55 + 20,
					"text" : "",
					"text_x" : 0,
					"default_image" : IMG_SKY + "sky9.dds",
					"over_image" : IMG_SKY + "sky9d.dds",
					"down_image" : IMG_SKY + "sky9o.dds",
				},
				{
					"name" : "showNight_10_button",
					"type" : "radio_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y + 40 + 55 + 55 + 20,
					"text" : "",
					"text_x" : 0,
					"default_image" : IMG_SKY + "sky10.dds",
					"over_image" : IMG_SKY + "sky10d.dds",
					"down_image" : IMG_SKY + "sky10o.dds",
				},
				
			),
		},
		# Tiling Mode
		{
			"name" : "tiling_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : 110 + SMALL_OPTION_HEIGHT + NORMAL_OPTION_HEIGHT * 5,
			"width" : 340,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "tiling_mode_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_tiling_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_TILING,
						},
					),
				},
				{
					"name" : "tiling_cpu",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_TILING_CPU,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "tiling_gpu",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_TILING_GPU,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "tiling_apply",
					"type" : "button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y - 2,
					"text" : uiscriptlocale.OPTION_TILING_APPLY,
					"default_image" : IMG_DIR + "btn_0.png",
					"over_image" : IMG_DIR + "btn_1.png",
					"down_image" : IMG_DIR + "btn_2.png",
				},
			),
		},
		# Keyboard Settings (conditional)
		{
			"name" : "keyboard_window",
			"type" : "window",
			"x" : 0,
			"y" : 110 + SMALL_OPTION_HEIGHT + NORMAL_OPTION_HEIGHT * 6,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "keyboard_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_keyboard",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_KEY_SETTING,
						},
					),
				},
				{
					"name" : "keyboard_settings_button",
					"type" : "button",
					"x" : OPTION_START_X,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_SETTING,
					"default_image" : IMG_DIR + "btn_0.png",
					"over_image" : IMG_DIR + "btn_1.png",
					"down_image" : IMG_DIR + "btn_2.png",
				},
			),
		},
	),
}
