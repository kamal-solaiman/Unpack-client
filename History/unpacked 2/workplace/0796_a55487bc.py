# coding: latin_1

import uiscriptlocale

ROOT_PATH = "d:/ymir work/ui/public/"

TEMPORARY_X = +13
TEXT_TEMPORARY_X = -10
BUTTON_TEMPORARY_X = 5
PVP_X = -10

if ENABLE_SHADOW_RENDER_QUALITY_OPTION:
	GRAPHIC_ON_OFF_WINDOW_Y = 315
	MULTI_LANGUAGE_WINDOW_Y = 490 if ENABLE_FOV_OPTION else 445
	window = {
		"name" : "SystemOptionDialog",
		"style" : ("movable", "float",),

		"x" : 0,
		"y" : 0,

		"width" : 305,
		"height" : 260 if ENABLE_FOV_OPTION else 280,

		"children" :
		[
			{
				"name" : "board",
				"type" : "board",

				"x" : 0,
				"y" : 0,

				"width" : 305,
				"height" : 260 if ENABLE_FOV_OPTION else 280,

				"children" :
				[
					## Title
					{
						"name" : "titlebar",
						"type" : "titlebar",
						"style" : ("attach",),

						"x" : 8,
						"y" : 8,

						"width" : 284,
						"color" : "gray",

						"children" :
						(
							{
								"name" : "titlename",
								"type" : "text",

								"x" : 0,
								"y" : 3,

								"horizontal_align" : "center",
								"text_horizontal_align" : "center",

								"text" : uiscriptlocale.SYSTEMOPTION_TITLE,
							},
						),
					},

					## Music
					{
						"name" : "music_name",
						"type" : "text",

						"x" : 30,
						"y" : 75,

						"text" : uiscriptlocale.OPTION_MUSIC,
					},

					{
						"name" : "music_volume_controller",
						"type" : "sliderbar",

						"x" : 110,
						"y" : 75,
					},

					{
						"name" : "bgm_button",
						"type" : "button",

						"x" : 20,
						"y" : 100,

						"text" : uiscriptlocale.OPTION_MUSIC_CHANGE,

						"default_image" : ROOT_PATH + "Middle_Button_01.sub",
						"over_image" : ROOT_PATH + "Middle_Button_02.sub",
						"down_image" : ROOT_PATH + "Middle_Button_03.sub",
					},

					{
						"name" : "bgm_file",
						"type" : "text",

						"x" : 100,
						"y" : 102,

						"text" : uiscriptlocale.OPTION_MUSIC_DEFAULT_THEMA,
					},

					## Sound
					{
						"name" : "sound_name",
						"type" : "text",

						"x" : 30,
						"y" : 50,

						"text" : uiscriptlocale.OPTION_SOUND,
					},

					{
						"name" : "sound_volume_controller",
						"type" : "sliderbar",

						"x" : 110,
						"y" : 50,
					},

					{
						"name" : "camera_mode",
						"type" : "text",

						"x" : 40 + TEXT_TEMPORARY_X,
						"y" : 135+2,

						"text" : uiscriptlocale.OPTION_CAMERA_DISTANCE,
					},

					{
						"name" : "camera_short",
						"type" : "radio_button",

						"x" : 110,
						"y" : 135,

						"text" : uiscriptlocale.OPTION_CAMERA_DISTANCE_SHORT,

						"default_image" : ROOT_PATH + "Middle_Button_01.sub",
						"over_image" : ROOT_PATH + "Middle_Button_02.sub",
						"down_image" : ROOT_PATH + "Middle_Button_03.sub",
					},

					{
						"name" : "camera_long",
						"type" : "radio_button",

						"x" : 110+70,
						"y" : 135,

						"text" : uiscriptlocale.OPTION_CAMERA_DISTANCE_LONG,

						"default_image" : ROOT_PATH + "Middle_Button_01.sub",
						"over_image" : ROOT_PATH + "Middle_Button_02.sub",
						"down_image" : ROOT_PATH + "Middle_Button_03.sub",
					},

					{
						"name" : "fog_mode",
						"type" : "text",

						"x" : 30,
						"y" : 160+2,

						"text" : uiscriptlocale.OPTION_FOG,
					},

					{
						"name" : "fog_on",
						"type" : "radio_button",

						"x" : 110,
						"y" : 160,

						"text" : uiscriptlocale.OPTION_FOG_ON,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "fog_off",
						"type" : "radio_button",

						"x" : 110+50,
						"y" : 160,

						"text" : uiscriptlocale.OPTION_FOG_OFF,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "night_mode",
						"type" : "text",

						"x" : 40 + TEXT_TEMPORARY_X,
						"y" : 185,

						"text" : uiscriptlocale.OPTION_NIGHT_MODE,
					},

					{
						"name" : "night_mode_on",
						"type" : "radio_button",

						"x" : 110,
						"y" : 185,

						"text" : uiscriptlocale.OPTION_NIGHT_MODE_ON,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "night_mode_off",
						"type" : "radio_button",

						"x" : 110+50,
						"y" : 185,

						"text" : uiscriptlocale.OPTION_NIGHT_MODE_OFF,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "snow_mode",
						"type" : "text",

						"x" : 40 + TEXT_TEMPORARY_X,
						"y" : 210,

						"text" : uiscriptlocale.OPTION_SNOW_MODE,
					},

					{
						"name" : "snow_mode_on",
						"type" : "radio_button",

						"x" : 110,
						"y" : 210,

						"text" : uiscriptlocale.OPTION_SNOW_MODE_ON,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "snow_mode_off",
						"type" : "radio_button",

						"x" : 110+50,
						"y" : 210,

						"text" : uiscriptlocale.OPTION_SNOW_MODE_OFF,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "snow_texture_mode",
						"type" : "text",

						"x" : 40 + TEXT_TEMPORARY_X,
						"y" : 235,

						"text" : uiscriptlocale.OPTION_SNOW_TEXTURE_MODE,
					},

					{
						"name" : "snow_texture_mode_on",
						"type" : "radio_button",

						"x" : 110,
						"y" : 235,

						"text" : uiscriptlocale.OPTION_SNOW_TEXTURE_MODE_ON,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "snow_texture_mode_off",
						"type" : "radio_button",

						"x" : 110+50,
						"y" : 235,

						"text" : uiscriptlocale.OPTION_SNOW_TEXTURE_MODE_OFF,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "shadow_target",
						"type" : "text",

						"x" : 40 + TEXT_TEMPORARY_X,
						"y" : 260+2,

						"text" : uiscriptlocale.OPTION_SHADOW_TARGET,
					},

					{
						"name" : "shadow_target_none",
						"type" : "radio_button",

						"x" : 110,
						"y" : 260,

						"text" : uiscriptlocale.OPTION_SHADOW_TARGET_NONE,
						"tooltip_text" : uiscriptlocale.OPTION_SHADOW_TARGET_NONE_TOOLTIP,

						"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
						"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
						"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
					},

					{
						"name" : "shadow_target_ground",
						"type" : "radio_button",

						"x" : 110 + 20,
						"y" : 260,

						"text" : uiscriptlocale.OPTION_SHADOW_TARGET_GROUND,
						"tooltip_text" : uiscriptlocale.OPTION_SHADOW_TARGET_GROUND_TOOLTIP,

						"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
						"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
						"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
					},

					{
						"name" : "shadow_target_ground_and_solo",
						"type" : "radio_button",

						"x" : 110 + 40,
						"y" : 260,

						"text" : uiscriptlocale.OPTION_SHADOW_TARGET_GROUND_AND_SOLO,
						"tooltip_text" : uiscriptlocale.OPTION_SHADOW_TARGET_GROUND_AND_SOLO_TOOLTIP,

						"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
						"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
						"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
					},

					{
						"name" : "shadow_target_all",
						"type" : "radio_button",

						"x" : 110 + 60,
						"y" : 260,

						"text" : uiscriptlocale.OPTION_SHADOW_TARGET_ALL,
						"tooltip_text" : uiscriptlocale.OPTION_SHADOW_TARGET_ALL_TOOLTIP,

						"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
						"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
						"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
					},
					{
						"name" : "shadow_quality",
						"type" : "text",

						"x" : 40 + TEXT_TEMPORARY_X,
						"y" : 285+2,

						"text" : uiscriptlocale.OPTION_SHADOW_QUALITY,
					},

					{
						"name" : "shadow_quality_bad",
						"type" : "radio_button",

						"x" : 110,
						"y" : 285,

						"text" : uiscriptlocale.OPTION_SHADOW_QUALITY_BAD,
						"tooltip_text" : uiscriptlocale.OPTION_SHADOW_QUALITY_BAD_TOOLTIP,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "shadow_quality_average",
						"type" : "radio_button",

						"x" : 110 + 50,
						"y" : 285,

						"text" : uiscriptlocale.OPTION_SHADOW_QUALITY_AVERAGE,
						"tooltip_text" : uiscriptlocale.OPTION_SHADOW_QUALITY_AVERAGE_TOOLTIP,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "shadow_quality_good",
						"type" : "radio_button",

						"x" : 110 + 100,
						"y" : 285,

						"text" : uiscriptlocale.OPTION_SHADOW_QUALITY_GOOD,
						"tooltip_text" : uiscriptlocale.OPTION_SHADOW_QUALITY_GOOD_TOOLTIP,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},
				],
			},
		],
	}

	window["height"] = window["height"] + 150
	window["children"][0]["height"] = window["children"][0]["height"] + 150
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "graphic_on_off_window",
			"type" : "window",

			"x" : 0,
			"y" : GRAPHIC_ON_OFF_WINDOW_Y,

			"width" : 305,
			"height" : 150,

			"children" :
			[
				{
					"name" : "effect_level",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 0+2,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL,
				},

				{
					"name" : "effect_level1",
					"type" : "radio_button",

					"x" : 112,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL1,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL1_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "effect_level2",
					"type" : "radio_button",

					"x" : 112 + 20,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL2,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL2_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "effect_level3",
					"type" : "radio_button",

					"x" : 112 + 40,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL3,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL3_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "effect_level4",
					"type" : "radio_button",

					"x" : 112 + 60,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL4,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL4_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "effect_level5",
					"type" : "radio_button",

					"x" : 112 + 80,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL5,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL5_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "effect_apply",
					"type" : "button",

					"x" : 110+105,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_APPLY,

					"default_image" : ROOT_PATH + "middle_Button_01.sub",
					"over_image" : ROOT_PATH + "middle_Button_02.sub",
					"down_image" : ROOT_PATH + "middle_Button_03.sub",
				},

				{
					"name" : "privateShop_level",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 25+2,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL,
				},

				{
					"name" : "privateShop_level1",
					"type" : "radio_button",

					"x" : 112,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL1,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL1_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "privateShop_level2",
					"type" : "radio_button",

					"x" : 112 + 20,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL2,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL2_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "privateShop_level3",
					"type" : "radio_button",

					"x" : 112 + 40,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL3,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL3_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "privateShop_level4",
					"type" : "radio_button",

					"x" : 112 + 60,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL4,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL4_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "privateShop_level5",
					"type" : "radio_button",

					"x" : 112 + 80,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL5,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL5_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "privateShop_apply",
					"type" : "button",

					"x" : 110+105,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_APPLY,

					"default_image" : ROOT_PATH + "middle_Button_01.sub",
					"over_image" : ROOT_PATH + "middle_Button_02.sub",
					"down_image" : ROOT_PATH + "middle_Button_03.sub",
				},

				{
					"name" : "dropItem_level",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 50+2,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL,
				},

				{
					"name" : "dropItem_level1",
					"type" : "radio_button",

					"x" : 112,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL1,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL1_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "dropItem_level2",
					"type" : "radio_button",

					"x" : 112 + 20,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL2,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL2_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "dropItem_level3",
					"type" : "radio_button",

					"x" : 112 + 40,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL3,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL3_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "dropItem_level4",
					"type" : "radio_button",

					"x" : 112 + 60,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL4,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL4_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "dropItem_level5",
					"type" : "radio_button",

					"x" : 112 + 80,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL5,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL5_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "dropItem_apply",
					"type" : "button",

					"x" : 110+105,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_APPLY,

					"default_image" : ROOT_PATH + "middle_Button_01.sub",
					"over_image" : ROOT_PATH + "middle_Button_02.sub",
					"down_image" : ROOT_PATH + "middle_Button_03.sub",
				},

				{
					"name" : "pet_status",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 75+2,

					"text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS,
				},

				{
					"name" : "pet_on",
					"type" : "radio_button",

					"x" : 110+20,
					"y" : 75,

					"text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_ON,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_ON_TOOLTIP,


					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
				},

				{
					"name" : "pet_off",
					"type" : "radio_button",

					"x" : 110 + 50+20,
					"y" : 75,

					"text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_OFF,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_OFF_TOOLTIP,

					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
				},

				{
					"name" : "npcName_status",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 100+2,

					"text" : uiscriptlocale.GRAPHICONOFF_NPC_NAME_STATUS,
				},

				{
					"name" : "npcName_on",
					"type" : "radio_button",

					"x" : 110+20,
					"y" : 100,

					"text" : uiscriptlocale.GRAPHICONOFF_NPC_NAME_STATUS_ON,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_NPC_NAME_STATUS_ON_TOOLTIP,

					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
				},

				{
					"name" : "npcName_off",
					"type" : "radio_button",

					"x" : 110 + 50+20,
					"y" : 100,

					"text" : uiscriptlocale.GRAPHICONOFF_NPC_NAME_STATUS_OFF,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_NPC_NAME_STATUS_OFF_TOOLTIP,

					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
				},
			],
		},
	]

	window["height"] = window["height"] + 110
	window["children"][0]["height"] = window["children"][0]["height"] + 110
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "language_change_window",
			"type" : "window",

			"x" : 0,
			"y" : MULTI_LANGUAGE_WINDOW_Y,
			"width" : 305,
			"height" : 22+110,

			"children" :
			(
				{
					"name" : "language_select_text",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 0,

					"text" : uiscriptlocale.OPTION_LANGUAGE_SELECT,
				},
				{
					"name" : "language_select_img",
					"type" : "image",
					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 20,
					"image" : "d:/ymir work/ui/quest_re/button_one.sub",
				},
				{
					"name" : "cur_language_text_window",
					"type" : "window",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 20,
					"width" : 210-16,
					"height" : 16,

					"children" :
					(
						{
							"name" : "cur_language_text",
							"type" : "text",

							"x" : 0,
							"y" : 0,

							"text" : "-",
							"all_align" : "center"
						},
					),
				},
				{
					"name" : "language_select_button",
					"type" : "button",

					"x" : 40 + TEXT_TEMPORARY_X + 210 -16,
					"y" : 20,

					"default_image" : "d:/ymir work/ui/game/party_match/arrow_default.sub",
					"over_image" : "d:/ymir work/ui/game/party_match/arrow_over.sub",
					"down_image" : "d:/ymir work/ui/game/party_match/arrow_down.sub",
				},
				{
					"name" : "language_change_button",
					"type" : "button",

					"x" : 40 + TEXT_TEMPORARY_X + 210 + 10,
					"y" : -3 + 20,

					"text" : uiscriptlocale.OPTION_LANGUAGE_CHANGE,

					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
					"disable_image" : ROOT_PATH + "small_Button_03.sub",
				},
				{
					"name" : "language_select_pivot_window",
					"type" : "window",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 16+20,
					"width" : 210,
					"height" : 0,
				},
				{
					"name" : "mouse_over_image",
					"type" : "expanded_image",
					"style" : ("not_pick",),
					"x" : 0 + 10,
					"y" : 0 + 32,
					"image" : "d:/ymir work/ui/quest_re/button_over.sub",
				},
			),
		},
	]
else:
	GRAPHIC_ON_OFF_WINDOW_Y = 270
	MULTI_LANGUAGE_WINDOW_Y = 395

	window = {
		"name" : "SystemOptionDialog",
		"style" : ("movable", "float",),

		"x" : 0,
		"y" : 0,

		"width" : 305,
		"height" : 280,

		"children" :
		[
			{
				"name" : "board",
				"type" : "board",

				"x" : 0,
				"y" : 0,

				"width" : 305,
				"height" : 280,

				"children" :
				[
					## Title
					{
						"name" : "titlebar",
						"type" : "titlebar",
						"style" : ("attach",),

						"x" : 8,
						"y" : 8,

						"width" : 284,
						"color" : "gray",

						"children" :
						(
							{
								"name" : "titlename",
								"type" : "text",

								"x" : 0,
								"y" : 3,

								"horizontal_align" : "center",
								"text_horizontal_align" : "center",

								"text" : uiscriptlocale.SYSTEMOPTION_TITLE,
							},
						),
					},

					## Music
					{
						"name" : "music_name",
						"type" : "text",

						"x" : 30,
						"y" : 75,

						"text" : uiscriptlocale.OPTION_MUSIC,
					},

					{
						"name" : "music_volume_controller",
						"type" : "sliderbar",

						"x" : 110,
						"y" : 75,
					},

					{
						"name" : "bgm_button",
						"type" : "button",

						"x" : 20,
						"y" : 100,

						"text" : uiscriptlocale.OPTION_MUSIC_CHANGE,

						"default_image" : ROOT_PATH + "Middle_Button_01.sub",
						"over_image" : ROOT_PATH + "Middle_Button_02.sub",
						"down_image" : ROOT_PATH + "Middle_Button_03.sub",
					},

					{
						"name" : "bgm_file",
						"type" : "text",

						"x" : 100,
						"y" : 102,

						"text" : uiscriptlocale.OPTION_MUSIC_DEFAULT_THEMA,
					},

					## Sound
					{
						"name" : "sound_name",
						"type" : "text",

						"x" : 30,
						"y" : 50,

						"text" : uiscriptlocale.OPTION_SOUND,
					},

					{
						"name" : "sound_volume_controller",
						"type" : "sliderbar",

						"x" : 110,
						"y" : 50,
					},

					{
						"name" : "camera_mode",
						"type" : "text",

						"x" : 40 + TEXT_TEMPORARY_X,
						"y" : 135+2,

						"text" : uiscriptlocale.OPTION_CAMERA_DISTANCE,
					},

					{
						"name" : "camera_short",
						"type" : "radio_button",

						"x" : 110,
						"y" : 135,

						"text" : uiscriptlocale.OPTION_CAMERA_DISTANCE_SHORT,

						"default_image" : ROOT_PATH + "Middle_Button_01.sub",
						"over_image" : ROOT_PATH + "Middle_Button_02.sub",
						"down_image" : ROOT_PATH + "Middle_Button_03.sub",
					},

					{
						"name" : "camera_long",
						"type" : "radio_button",

						"x" : 110+70,
						"y" : 135,

						"text" : uiscriptlocale.OPTION_CAMERA_DISTANCE_LONG,

						"default_image" : ROOT_PATH + "Middle_Button_01.sub",
						"over_image" : ROOT_PATH + "Middle_Button_02.sub",
						"down_image" : ROOT_PATH + "Middle_Button_03.sub",
					},

					{
						"name" : "fog_mode",
						"type" : "text",

						"x" : 30,
						"y" : 160+2,

						"text" : uiscriptlocale.OPTION_FOG,
					},

					{
						"name" : "fog_on",
						"type" : "radio_button",

						"x" : 110,
						"y" : 160,

						"text" : uiscriptlocale.OPTION_FOG_ON,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "fog_off",
						"type" : "radio_button",

						"x" : 110+50,
						"y" : 160,

						"text" : uiscriptlocale.OPTION_FOG_OFF,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "night_mode",
						"type" : "text",

						"x" : 40 + TEXT_TEMPORARY_X,
						"y" : 185,

						"text" : uiscriptlocale.OPTION_NIGHT_MODE,
					},

					{
						"name" : "night_mode_on",
						"type" : "radio_button",

						"x" : 110,
						"y" : 185,

						"text" : uiscriptlocale.OPTION_NIGHT_MODE_ON,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "night_mode_off",
						"type" : "radio_button",

						"x" : 110+50,
						"y" : 185,

						"text" : uiscriptlocale.OPTION_NIGHT_MODE_OFF,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "snow_mode",
						"type" : "text",

						"x" : 40 + TEXT_TEMPORARY_X,
						"y" : 210,

						"text" : uiscriptlocale.OPTION_SNOW_MODE,
					},

					{
						"name" : "snow_mode_on",
						"type" : "radio_button",

						"x" : 110,
						"y" : 210,

						"text" : uiscriptlocale.OPTION_SNOW_MODE_ON,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "snow_mode_off",
						"type" : "radio_button",

						"x" : 110+50,
						"y" : 210,

						"text" : uiscriptlocale.OPTION_SNOW_MODE_OFF,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "snow_texture_mode",
						"type" : "text",

						"x" : 40 + TEXT_TEMPORARY_X,
						"y" : 235,

						"text" : uiscriptlocale.OPTION_SNOW_TEXTURE_MODE,
					},

					{
						"name" : "snow_texture_mode_on",
						"type" : "radio_button",

						"x" : 110,
						"y" : 235,

						"text" : uiscriptlocale.OPTION_SNOW_TEXTURE_MODE_ON,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},

					{
						"name" : "snow_texture_mode_off",
						"type" : "radio_button",

						"x" : 110+50,
						"y" : 235,

						"text" : uiscriptlocale.OPTION_SNOW_TEXTURE_MODE_OFF,

						"default_image" : ROOT_PATH + "small_Button_01.sub",
						"over_image" : ROOT_PATH + "small_Button_02.sub",
						"down_image" : ROOT_PATH + "small_Button_03.sub",
					},
				],
			},
		],
	}

	window["height"] = window["height"] + 150
	window["children"][0]["height"] = window["children"][0]["height"] + 150
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "graphic_on_off_window",
			"type" : "window",

			"x" : 0,
			"y" : GRAPHIC_ON_OFF_WINDOW_Y,

			"width" : 305,
			"height" : 150,

			"children" :
			[
				{
					"name" : "effect_level",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 0+2,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL,
				},

				{
					"name" : "effect_level1",
					"type" : "radio_button",

					"x" : 112,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL1,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL1_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "effect_level2",
					"type" : "radio_button",

					"x" : 112 + 20,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL2,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL2_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "effect_level3",
					"type" : "radio_button",

					"x" : 112 + 40,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL3,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL3_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "effect_level4",
					"type" : "radio_button",

					"x" : 112 + 60,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL4,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL4_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "effect_level5",
					"type" : "radio_button",

					"x" : 112 + 80,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL5,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_EFFECT_LEVEL5_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "effect_apply",
					"type" : "button",

					"x" : 110+105,
					"y" : 0,

					"text" : uiscriptlocale.GRAPHICONOFF_EFFECT_APPLY,

					"default_image" : ROOT_PATH + "middle_Button_01.sub",
					"over_image" : ROOT_PATH + "middle_Button_02.sub",
					"down_image" : ROOT_PATH + "middle_Button_03.sub",
				},

				{
					"name" : "privateShop_level",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 25+2,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL,
				},

				{
					"name" : "privateShop_level1",
					"type" : "radio_button",

					"x" : 112,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL1,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL1_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "privateShop_level2",
					"type" : "radio_button",

					"x" : 112 + 20,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL2,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL2_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "privateShop_level3",
					"type" : "radio_button",

					"x" : 112 + 40,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL3,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL3_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "privateShop_level4",
					"type" : "radio_button",

					"x" : 112 + 60,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL4,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL4_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "privateShop_level5",
					"type" : "radio_button",

					"x" : 112 + 80,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL5,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_LEVEL5_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "privateShop_apply",
					"type" : "button",

					"x" : 110+105,
					"y" : 25,

					"text" : uiscriptlocale.GRAPHICONOFF_PRIVATE_SHOP_APPLY,

					"default_image" : ROOT_PATH + "middle_Button_01.sub",
					"over_image" : ROOT_PATH + "middle_Button_02.sub",
					"down_image" : ROOT_PATH + "middle_Button_03.sub",
				},

				{
					"name" : "dropItem_level",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 50+2,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL,
				},

				{
					"name" : "dropItem_level1",
					"type" : "radio_button",

					"x" : 112,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL1,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL1_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "dropItem_level2",
					"type" : "radio_button",

					"x" : 112 + 20,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL2,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL2_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "dropItem_level3",
					"type" : "radio_button",

					"x" : 112 + 40,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL3,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL3_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "dropItem_level4",
					"type" : "radio_button",

					"x" : 112 + 60,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL4,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL4_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "dropItem_level5",
					"type" : "radio_button",

					"x" : 112 + 80,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL5,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_LEVEL5_TOOLTIP,

					"default_image" : ROOT_PATH + "minimize_empty_button_01.sub",
					"over_image" : ROOT_PATH + "minimize_empty_button_02.sub",
					"down_image" : ROOT_PATH + "minimize_empty_button_03.sub",
				},

				{
					"name" : "dropItem_apply",
					"type" : "button",

					"x" : 110+105,
					"y" : 50,

					"text" : uiscriptlocale.GRAPHICONOFF_DROP_ITEM_APPLY,

					"default_image" : ROOT_PATH + "middle_Button_01.sub",
					"over_image" : ROOT_PATH + "middle_Button_02.sub",
					"down_image" : ROOT_PATH + "middle_Button_03.sub",
				},

				{
					"name" : "pet_status",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 75+2,

					"text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS,
				},

				{
					"name" : "pet_on",
					"type" : "radio_button",

					"x" : 110+20,
					"y" : 75,

					"text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_ON,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_ON_TOOLTIP,


					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
				},

				{
					"name" : "pet_off",
					"type" : "radio_button",

					"x" : 110 + 50+20,
					"y" : 75,

					"text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_OFF,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_OFF_TOOLTIP,

					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
				},

				{
					"name" : "npcName_status",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 100+2,

					"text" : uiscriptlocale.GRAPHICONOFF_NPC_NAME_STATUS,
				},

				{
					"name" : "npcName_on",
					"type" : "radio_button",

					"x" : 110+20,
					"y" : 100,

					"text" : uiscriptlocale.GRAPHICONOFF_NPC_NAME_STATUS_ON,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_NPC_NAME_STATUS_ON_TOOLTIP,

					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
				},

				{
					"name" : "npcName_off",
					"type" : "radio_button",

					"x" : 110 + 50+20,
					"y" : 100,

					"text" : uiscriptlocale.GRAPHICONOFF_NPC_NAME_STATUS_OFF,
					"tooltip_text" : uiscriptlocale.GRAPHICONOFF_NPC_NAME_STATUS_OFF_TOOLTIP,

					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
				},
			],
		},
	]

	window["height"] = window["height"] + 15 + 20
	window["children"][0]["height"] = window["children"][0]["height"] + 15 + 20
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "language_change_window",
			"type" : "window",

			"x" : 0,
			"y" : MULTI_LANGUAGE_WINDOW_Y,
			"width" : 305,
			"height" : 22+20,

			"children" :
			(
				{
					"name" : "language_select_text",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 0,

					"text" : uiscriptlocale.OPTION_LANGUAGE_SELECT,
				},
				{
					"name" : "language_select_img",
					"type" : "image",
					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 20,
					"image" : "d:/ymir work/ui/quest_re/button_one.sub",
				},
				{
					"name" : "cur_language_text_window",
					"type" : "window",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 20,
					"width" : 210-16,
					"height" : 16,

					"children" :
					(
						{
							"name" : "cur_language_text",
							"type" : "text",

							"x" : 0,
							"y" : 0,

							"text" : "-",
							"all_align" : "center"
						},
					),
				},
				{
					"name" : "language_select_button",
					"type" : "button",

					"x" : 40 + TEXT_TEMPORARY_X + 210 -16,
					"y" : 20,

					"default_image" : "d:/ymir work/ui/game/party_match/arrow_default.sub",
					"over_image" : "d:/ymir work/ui/game/party_match/arrow_over.sub",
					"down_image" : "d:/ymir work/ui/game/party_match/arrow_down.sub",
				},
				{
					"name" : "language_change_button",
					"type" : "button",

					"x" : 40 + TEXT_TEMPORARY_X + 210 + 10,
					"y" : -3 + 20,

					"text" : uiscriptlocale.OPTION_LANGUAGE_CHANGE,

					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
					"disable_image" : ROOT_PATH + "small_Button_03.sub",
				},
				{
					"name" : "language_select_pivot_window",
					"type" : "window",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 16+20,
					"width" : 210,
					"height" : 0,
				},
				{
					"name" : "mouse_over_image",
					"type" : "expanded_image",
					"style" : ("not_pick",),
					"x" : 0 + 10,
					"y" : 0 + 32,
					"image" : "d:/ymir work/ui/quest_re/button_over.sub",
				},
			),
		},
	]

# window["height"] = window["height"] + 15
# window["children"][0]["height"] = window["children"][0]["height"] + 15
# window["children"][0]["children"] = window["children"][0]["children"] + [
		# {
			# "name" : "fps_change_btn",
			# "type" : "button",
			# "x" : 40 + TEXT_TEMPORARY_X,
			# "y" : 460, # modify y

			# "text" : uiscriptlocale.OPTION_MUSIC_CHANGE,
			# "default_image" : ROOT_PATH + "small_Button_01.sub",
			# "over_image" : ROOT_PATH + "small_Button_02.sub",
			# "down_image" : ROOT_PATH + "small_Button_03.sub",
		# },
# ]

if ENABLE_FPS:
	DOG_MODE_WINDOW_Y = 440

	window["height"] = window["height"] + 15
	window["children"][0]["height"] = window["children"][0]["height"] + 15
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "dog_mode_on_off_window",
			"type" : "window",

			"x" : 0,
			"y" : DOG_MODE_WINDOW_Y,

			"width" : 305,
			"height" : 22+20,

			"children" :
			[
				{
					"name" : "dogMode_status",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 0+2,

					"text" : "FPS",
				},

				{
					"name" : "fps_change_btn",
					"type" : "button",

					"x" : 40 + TEXT_TEMPORARY_X + 210 + 10,
					"y" : 0+2,

					"text" : uiscriptlocale.OPTION_MUSIC_CHANGE,
					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
				},

			],
		},
	]

if ENABLE_FOV_OPTION:
	FOV_MODE_WINDOW_Y = 440 + 25

	window["height"] = window["height"] + 15 + 10
	window["children"][0]["height"] = window["children"][0]["height"] + 15 + 10
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "fov_mode_on_off_window",
			"type" : "window", 

			"x" : 0,
			"y" : FOV_MODE_WINDOW_Y,

			"width" : 305,
			"height" : 22+20,

			"children" :
			[
				{
					"name" : "fov_option",
					"type" : "text",

					"x" : 40 + TEXT_TEMPORARY_X,
					"y" : 0+2,

					"text" : uiscriptlocale.FOV_OPTION,
				},

				{
					"name" : "fov_on",
					"type" : "radio_button",

					"x" : 110,
					"y" : 0,

					"text" : uiscriptlocale.FOV_OPTION_ON,
					"tooltip_text" : uiscriptlocale.FOV_OPTION_ON_TOOLTIP,

					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
				},

				{
					"name" : "fov_off",
					"type" : "radio_button",

					"x" : 110 + 50,
					"y" : 0,

					"text" : uiscriptlocale.FOV_OPTION_OFF,
					"tooltip_text" : uiscriptlocale.FOV_OPTION_OFF_TOOLTIP,

					"default_image" : ROOT_PATH + "small_Button_01.sub",
					"over_image" : ROOT_PATH + "small_Button_02.sub",
					"down_image" : ROOT_PATH + "small_Button_03.sub",
				},
			],
		},
	]