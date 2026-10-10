# coding: latin_1
# Category 2: Graphics - Rendering, camera, and performance settings

import uiscriptlocale

IMG_DIR = "d:/ymir work/ui/game/advanced_game_options/"

TITLE_IMAGE_TEXT_X = 155
TITLE_IMAGE_TEXT_Y = 2

OPTION_START_X = 12
OPTION_START_X_NEW = 12
SLIDER_POSITION_X = 50

SLIDER_START_Y = 40
BUTTON_START_Y = 33
BUTTON_NEXT_Y = 20

# Post-processing advanced controls layout
# Tune these 3 values to adjust all positions at once:
_PP_DY  = 28   # slider row pitch
_PP_SG  = 12   # extra gap at section boundaries
_PP_VIG = 84   # first slider Y offset from BUTTON_START_Y
# Derived (do not edit manually):
_PP_SHP = _PP_VIG + _PP_DY              # Sharpen
_PP_CLR = _PP_SHP + _PP_DY + _PP_SG    # Color Grade label
_PP_LUT = _PP_CLR + 20                  # LUT radio buttons
_PP_STR = _PP_LUT + _PP_DY + _PP_SG    # LUT Strength slider
_PP_WH  = BUTTON_START_Y + _PP_STR + 26 # PP window height

RADIO_BUTTON_RANGE_X = 65 + 15 
TOGGLE_BUTTON_RANGE_X = 65 + 30

RADIO_BUTTON_TEXT_X = - 15
TOGGLE_BUTTON_TEXT_X = - 10

NORMAL_OPTION_HEIGHT = 80
SLIDER_OPTION_HEIGHT = 65
SLIDER_SECTION_WIDTH = 360
SLIDER_BAR_X = 31
SLIDER_VALUE_X = 330
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
		# FOV Option - SLIDER VERSION
		{
			"name" : "fov_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : 0,
			"width" : SLIDER_SECTION_WIDTH,
			"height" : SLIDER_OPTION_HEIGHT + 8,
			"children" :
			(
				{
					"name" : "fov_mode_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 2,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_fov_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.FOV_OPTION,
						},
					),
				},
				{
					"name" : "fov_controller",
					"type" : "sliderbar_advancedgameoptions",
					"x" : SLIDER_BAR_X,
					"y" : SLIDER_START_Y,
				},
				{
					"name" : "fov_value_text",
					"type" : "text",
					"x" : SLIDER_VALUE_X,
					"y" : SLIDER_START_Y + 1,
					"text_horizontal_align" : "center",
					"text" : "45",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "fov_reset_button",
					"type" : "button",
					"x" : 275,
					"y" : 10,
					"default_image" : "d:/ymir work/ui/game/windows/reset_badge_button_default.tga",
					"over_image" : "d:/ymir work/ui/game/windows/reset_badge_button_over.tga",
					"down_image" : "d:/ymir work/ui/game/windows/reset_badge_button_down.tga",
				},
			),
		},
		# Metin Stone Scale (conditional)
		{
			"name" : "stonesize_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT,
			"width" : SLIDER_SECTION_WIDTH,
			"height" : SLIDER_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "stonesize_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_stonesize",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_STONESIZE,
						},
					),
				},
				{
					"name" : "stonesize_controller",
					"type" : "sliderbar_advancedgameoptions",
					"x" : SLIDER_BAR_X,
					"y" : SLIDER_START_Y,
				},
			),
		},
		# Damage Effect Scale (conditional)
		# {
			# "name" : "dmgsize_window",
			# "type" : "window",
			# "x" : 0,
			# "y" : SMALL_OPTION_HEIGHT * 2 + SLIDER_OPTION_HEIGHT,
			# "width" : 304,
			# "height" : SLIDER_OPTION_HEIGHT,
			# "children" :
			# (
				# {
					# "name" : "dmgsize_title_img",
					# "type" : "expanded_image",
					# "x" : 0,
					# "y" : 0,
					# "image" : IMG_DIR + "option_title_2.png",
					# "children" :
					# (
						# {
							# "name" : "title_dmgsize",
							# "type" : "text",
							# "x" : TITLE_IMAGE_TEXT_X,
							# "y" : TITLE_IMAGE_TEXT_Y,
							# "text_horizontal_align" : "left",
							# "text" : uiscriptlocale.OPTION_DMGSIZE,
						# },
					# ),
				# },
				# {
					# "name" : "scaleEff_Slider",
					# "type" : "sliderbar",
					# "x" : OPTION_START_X + SLIDER_POSITION_X,
					# "y" : SLIDER_START_Y,
				# },
			# ),
		# },
		# Effect Render Distance (conditional)
		{
			"name" : "effect_distance_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 2 ,
			"width" : SLIDER_SECTION_WIDTH,
			"height" : SLIDER_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "effect_distance_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_effect_distance",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_EFFECT_RENDERING_DIST,
						},
					),
				},
				{
					"name" : "effect_controller",
					"type" : "sliderbar_advancedgameoptions",
					"x" : SLIDER_BAR_X,
					"y" : SLIDER_START_Y,
				},
			),
		},
		# Hide Effects Section - Row 1 (Buff, Skill, General)
		{
			"name" : "effect_visibility_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 3,
			"width" : 304,
			"height" : TOGGLE_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "effect_visibility_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_effect_visibility",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.GRAPHICONOFF_HIDE_EFFECTS,
						},
					),
				},
				{
					"name" : "hide_buff_toggle",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.GRAPHICONOFF_BUFF,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "hide_skill_toggle",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.GRAPHICONOFF_SKILL,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "hide_general_toggle",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.GRAPHICONOFF_GENERAL,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Hide Effects Section - Row 2 (Monsters, Projectiles)
		{
			"name" : "effect_visibility_window_2",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 4,
			"width" : 304,
			"height" : TOGGLE_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "hide_monster_toggle",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y - 25,
					"text" : uiscriptlocale.GRAPHICONOFF_MONSTERS,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "boss_effect_toggle",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y - 25,
					"text" : uiscriptlocale.GRAPHICONOFF_BOSS_EFFECT_DESC,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Private Shop Range (conditional)
		{
			"name" : "privateshop_range_window_ui",
			"type" : "window",
			"x" : 0,
			"y" : 20 + SMALL_OPTION_HEIGHT * 2 + SLIDER_OPTION_HEIGHT * 3,
			"width" : SLIDER_SECTION_WIDTH,
			"height" : SLIDER_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "privateshop_range_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_privateshop_range",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_PRIVATE_SHOP_RANGE_VIEW,
						},
					),
				},
				{
					"name" : "privateshop_range_controller_ui",
					"type" : "sliderbar_advancedgameoptions",
					"x" : SLIDER_BAR_X,
					"y" : SLIDER_START_Y,
				},
			),
		},
		# Pet Status (conditional)
		{
			"name" : "pet_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : 20 + SMALL_OPTION_HEIGHT * 2 + SLIDER_OPTION_HEIGHT * 4,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "pet_mode_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_pet_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS,
						},
					),
				},
				{
					"name" : "pet_off",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_OFF,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pet_on",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_ON,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Mount Status (conditional)
		{
			"name" : "mount_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : 20 + SMALL_OPTION_HEIGHT * 2 + SLIDER_OPTION_HEIGHT * 5,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "mount_mode_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_mount_mode",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.GRAPHICONOFF_MOUNT_STATUS,
						},
					),
				},
				{
					"name" : "mount_off",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_OFF,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "mount_on",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_ON,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# # NPC Name Status (conditional)
		# {
			# "name" : "npc_mode_window",
			# "type" : "window",
			# "x" : 0,
			# "y" : SMALL_OPTION_HEIGHT * 6 + SLIDER_OPTION_HEIGHT * 4,
			# "width" : 304,
			# "height" : SMALL_OPTION_HEIGHT,
			# "children" :
			# (
				# {
					# "name" : "npc_mode_title_img",
					# "type" : "expanded_image",
					# "x" : 0,
					# "y" : 0,
					# "image" : IMG_DIR + "option_title_2.png",
					# "children" :
					# (
						# {
							# "name" : "title_npc_mode",
							# "type" : "text",
							# "x" : TITLE_IMAGE_TEXT_X,
							# "y" : TITLE_IMAGE_TEXT_Y,
							# "text_horizontal_align" : "left",
							# "text" : uiscriptlocale.GRAPHICONOFF_NPC_NAME_STATUS,
						# },
					# ),
				# },
				# {
					# "name" : "npcName_off",
					# "type" : "radio_button",
					# "x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					# "y" : BUTTON_START_Y,
					# "text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_OFF,
					# "text_x" : RADIO_BUTTON_TEXT_X,
					# "default_image" : IMG_DIR + "radio_unselected.png",
					# "over_image" : IMG_DIR + "radio_unselected.png",
					# "down_image" : IMG_DIR + "radio_selected.png",
					# "color" : PRIMARY_COLOR,
				# },
				# {
					# "name" : "npcName_on",
					# "type" : "radio_button",
					# "x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					# "y" : BUTTON_START_Y,
					# "text" : uiscriptlocale.GRAPHICONOFF_PET_STATUS_ON,
					# "text_x" : RADIO_BUTTON_TEXT_X,
					# "default_image" : IMG_DIR + "radio_unselected.png",
					# "over_image" : IMG_DIR + "radio_unselected.png",
					# "down_image" : IMG_DIR + "radio_selected.png",
					# "color" : PRIMARY_COLOR,
				# },
			# ),
		# },
		# Monster Info (conditional)
		{
			"name" : "monster_info_window",
			"type" : "window",
			"x" : 0,
			"y" : 20 + SMALL_OPTION_HEIGHT * 2 + SLIDER_OPTION_HEIGHT * 6,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "monster_info_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_monster_info",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "left",
							"text" : uiscriptlocale.OPTION_MOB_INFO,
						},
					),
				},
				{
					"name" : "show_mob_level_button",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_MOB_INFO_LEVEL,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "show_mob_AI_flag_button",
					"type" : "toggle_button",
					"x" : OPTION_START_X + TOGGLE_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_MOB_INFO_AGGR,
					"text_x" : TOGGLE_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Shadow Target (conditional)

		# Shadow Level Slider (alternative to target+quality)
		# {
			# "name" : "shadow_slider_window",
			# "type" : "window",
			# "x" : 0,
			# "y" : SMALL_OPTION_HEIGHT * 10 + SLIDER_OPTION_HEIGHT * 4,
			# "width" : 304,
			# "height" : SLIDER_OPTION_HEIGHT,
			# "children" :
			# (
				# {
					# "name" : "shadow_slider_title_img",
					# "type" : "expanded_image",
					# "x" : 0,
					# "y" : 0,
					# "image" : IMG_DIR + "option_title_2.png",
					# "children" :
					# (
						# {
							# "name" : "title_shadow_slider",
							# "type" : "text",
							# "x" : TITLE_IMAGE_TEXT_X,
							# "y" : TITLE_IMAGE_TEXT_Y,
							# "text_horizontal_align" : "left",
							# "text" : uiscriptlocale.OPTION_SHADOW,
						# },
					# ),
				# },
				# {
					# "name" : "shadow_bar",
					# "type" : "sliderbar",
					# "x" : OPTION_START_X + SLIDER_POSITION_X,
					# "y" : SLIDER_START_Y,
				# },
			# ),
		# },
		# FPS Settings (conditional)
		{
			"name" : "fps_window",
			"type" : "window",
			"x" : 0,
			"y" : 25 + SMALL_OPTION_HEIGHT * 2 + SLIDER_OPTION_HEIGHT * 7,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "fps_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_fps",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "left",
							"text" : uiscriptlocale.OPTION_FPS,
						},
					),
				},
				{
					"name" : "fps_mode0",
					"type" : "radio_button",
					"x" : OPTION_START_X + 50 * 0,
					"y" : BUTTON_START_Y,
					"text" : "60",
					"text_x" : RADIO_BUTTON_TEXT_X + 10,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "fps_mode1",
					"type" : "radio_button",
					"x" : OPTION_START_X + 50 * 1,
					"y" : BUTTON_START_Y,
					"text" : "90",
					"text_x" : RADIO_BUTTON_TEXT_X + 10,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "fps_mode2",
					"type" : "radio_button",
					"x" : OPTION_START_X + 50 * 2,
					"y" : BUTTON_START_Y,
					"text" : "120",
					"text_x" : RADIO_BUTTON_TEXT_X + 10,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "fps_mode3",
					"type" : "radio_button",
					"x" : OPTION_START_X + 50 * 3,
					"y" : BUTTON_START_Y,
					"text" : "144",
					"text_x" : RADIO_BUTTON_TEXT_X + 10,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "fps_mode4",
					"type" : "radio_button",
					"x" : OPTION_START_X + 50 * 4,
					"y" : BUTTON_START_Y,
					"text" : "180",
					"text_x" : RADIO_BUTTON_TEXT_X + 10,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		{
			"name" : "background_fps_window",
			"type" : "window",
			"x" : 0,
			"y" : 25 + SMALL_OPTION_HEIGHT * 2 + SLIDER_OPTION_HEIGHT * 8,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "background_fps_title_img",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_background_fps",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "left",
							"text" : uiscriptlocale.OPTION_BACKGROUND_FPS,
						},
					),
				},
				{
					"name" : "background_fps_toggle",
					"type" : "toggle_button",
					"x" : 60,
					"y" : BUTTON_START_Y,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image"    : IMG_DIR + "toggle_unselected.png",
					"down_image"    : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "background_fps_label",
					"type" : "text",
					"x" : 60 + 50,
					"y" : BUTTON_START_Y + 4,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_BACKGROUND_FPS_LABEL,
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Post-Processing (conditional - ENABLE_POST_PROCESSING)
		{
			"name" : "post_processing_window",
			"type" : "window",
			"x" : 0,
			"y" : 25 + SMALL_OPTION_HEIGHT * 2 + SLIDER_OPTION_HEIGHT * 9,
			"width" : 371,
			"height" : _PP_WH + 35,
			"children" :
			(
				{
					"name" : "post_processing_title_img",
					"type" : "expanded_image",
					"x" : 5,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_post_processing",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_POST_PROCESSING,
						},
					),
				},
				# Toggle on/off
				{
					"name" : "pp_toggle",
					"type" : "toggle_button",
					"x" : 60,
					"y" : BUTTON_START_Y + 5,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "pp_toggle_label",
					"type" : "text",
					"x" : 60 + 50,
					"y" : BUTTON_START_Y + 5,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_PP_ENABLE,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				# Description text
				{
					"name" : "pp_description",
					"type" : "text",
					"x" : 15,
					"y" : BUTTON_START_Y + 30,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_PP_DESC,
					"color" : DESCRIPTION_COLOR,
				},
				# Quality radio buttons row
				{
					"name" : "pp_quality_low",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y + 55,
					"text" : uiscriptlocale.OPTION_PP_QUALITY_LOW,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pp_quality_medium",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y + 55,
					"text" : uiscriptlocale.OPTION_PP_QUALITY_MEDIUM,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pp_quality_high",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 2,
					"y" : BUTTON_START_Y + 55,
					"text" : uiscriptlocale.OPTION_PP_QUALITY_HIGH,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pp_quality_ultra",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 3,
					"y" : BUTTON_START_Y + 55,
					"text" : uiscriptlocale.OPTION_PP_QUALITY_ULTRA,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				# Advanced per-effect controls (shown/hidden from Python based on PP enabled state)
				# Vignette (on/off toggle)
				{
					"name" : "pp_vignette_toggle",
					"type" : "toggle_button",
					"x" : 60,
					"y" : BUTTON_START_Y + _PP_VIG,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image"    : IMG_DIR + "toggle_unselected.png",
					"down_image"    : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "pp_vignette_label",
					"type" : "text",
					"x" : 60 + 50,
					"y" : BUTTON_START_Y + _PP_VIG + 4,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_PP_VIGNETTE,
					"color" : PRIMARY_COLOR,
				},
				# Sharpen
				{
					"name" : "pp_sharpen_label",
					"type" : "text",
					"x" : 15,
					"y" : 10 + BUTTON_START_Y + _PP_SHP + 4,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_PP_SHARPEN,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pp_sharpen_slider",
					"type" : "sliderbar_advancedgameoptions",
					"x" : 15,
					"y" : 20 + BUTTON_START_Y + _PP_SHP + 10,
				},
				{
					"name" : "pp_sharpen_value",
					"type" : "text",
					"x" : 304,
					"y" : 20 + BUTTON_START_Y + _PP_SHP + 4 + 10,
					"text_horizontal_align" : "center",
					"text" : "0.50",
					"color" : SECONDARY_COLOR,
				},
				# Color Grade section
				{
					"name" : "pp_colorgrade_label",
					"type" : "text",
					"x" : 15,
					"y" : 10 + BUTTON_START_Y + _PP_CLR + 4,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_PP_COLOR_GRADE,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pp_lut_none",
					"type" : "radio_button",
					"x" : 43 + OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : 15 + BUTTON_START_Y + _PP_LUT,
					"text" : uiscriptlocale.OPTION_PP_LUT_NONE,
					"text_x" : RADIO_BUTTON_TEXT_X + 10,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pp_lut_cinematic",
					"type" : "radio_button",
					"x" : 33 + OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : 15 + BUTTON_START_Y + _PP_LUT,
					"text" : uiscriptlocale.OPTION_PP_LUT_CINEMATIC,
					"text_x" : RADIO_BUTTON_TEXT_X + 10,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pp_lut_fantasy",
					"type" : "radio_button",
					"x" : 43 + OPTION_START_X + RADIO_BUTTON_RANGE_X * 2,
					"y" : 15 + BUTTON_START_Y + _PP_LUT,
					"text" : uiscriptlocale.OPTION_PP_LUT_FANTASY,
					"text_x" : RADIO_BUTTON_TEXT_X + 10,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				# LUT Strength
				{
					"name" : "pp_lut_strength_label",
					"type" : "text",
					"x" : 15,
					"y" : 10 + BUTTON_START_Y + _PP_STR + 4,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_PP_LUT_STRENGTH,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "pp_lut_strength_slider",
					"type" : "sliderbar_advancedgameoptions",
					"x" : 15,
					"y" : 10 + BUTTON_START_Y + _PP_STR + 10,
				},
				{
					"name" : "pp_lut_strength_value",
					"type" : "text",
					"x" : 304,
					"y" : 25 + BUTTON_START_Y + _PP_STR + 4,
					"text_horizontal_align" : "center",
					"text" : "1.00",
					"color" : SECONDARY_COLOR,
				},
			),
		},
	),
}
