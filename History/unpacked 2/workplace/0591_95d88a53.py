# coding: latin_1
# Filter View: Combined view of all game options for search/filtering
# This file combines all options from Categories 0-4 into a single scrollable view

import uiscriptlocale
import localeinfo
import app

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
SLIDER_BAR_X = 31
SLIDER_VALUE_X = 330
SMALL_OPTION_HEIGHT = 80
TOGGLE_OPTION_HEIGHT = 80
NAME_VISIBILITY_HEIGHT = SMALL_OPTION_HEIGHT + 70

PRIMARY_COLOR = 0xffd0c2b7
SECONDARY_COLOR = 0xff9f9892
DESCRIPTION_COLOR = 0xff8a8078

# Calculate cumulative Y positions for each section
Y_POS = 0

_auto_shout_children = ()
if app.ENABLE_AUTO_SHOUT_V2:
	_auto_shout_children = (
		{
			"name" : "auto_shout_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 5 + 210,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "auto_shout_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_auto_shout",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : getattr(uiscriptlocale, "OPTION_AUTO_SHOUT_TITLE", "Auto-Shout"),
						},
					),
				},
				{
					"name" : "show_auto_shout_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y - 5,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "show_auto_shout_label",
					"type" : "text",
					"x" : OPTION_START_X + 90,
					"y" : BUTTON_START_Y - 3,
					"text_horizontal_align" : "left",
					"text" : getattr(uiscriptlocale, "OPTION_SHOW_AUTO_SHOUT", "Show auto-shouts"),
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
			),
		},
	)

window = {
	"name" : "GameOptionDialog",
	"style" : (),
	"x" : 222,
	"y" : 1,
	"width" : 371,
	"height" : 404,
	"children" :
	(
		# ============================================================================
		# CATEGORY 0: INTERFACE - Display and visibility settings
		# ============================================================================

		# View Chat
		{
			"name" : "chat_window",
			"type" : "window",
			"x" : 0,
			"y" : 0,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "chat_mode_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 2,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_view_chat",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_VIEW_CHAT,
						},
					),
				},
				{
					"name" : "view_chat_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "view_chat_description",
					"type" : "text",
					"x" : OPTION_START_X + 90,
					"y" : BUTTON_START_Y + 5,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_VIEW_CHAT_DESC,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
			),
		},
		# Name Visibility Options
		{
			"name" : "name_visibility_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT + 130,
			"children" :
			(
				{
					"name" : "name_visibility_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_name_visibility",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_HIDE_TITLE,
						},
					),
				},
				# Row 1: General Hide Names
				{
					"name" : "hide_names_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y - 5,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "hide_names_label",
					"type" : "text",
					"x" : OPTION_START_X + 90,
					"y" : BUTTON_START_Y - 3,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_HIDE_NAMES,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				# Row 2: Shop Names Hide
				{
					"name" : "hide_shops_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y - 5 + 35,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "hide_shops_label",
					"type" : "text",
					"x" : OPTION_START_X + 90,
					"y" : BUTTON_START_Y - 3 + 35,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_HIDE_SHOPS,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				# Row 3: NPC Names Hide
				{
					"name" : "hide_npc_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y - 5 + 70,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "hide_npc_label",
					"type" : "text",
					"x" : OPTION_START_X + 90,
					"y" : BUTTON_START_Y - 3 + 70,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_HIDE_NPC,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				# Row 4: NAME OUTLINE
				{
					"name" : "outline_name_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y - 5 + 105,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "outline_name_label",
					"type" : "text",
					"x" : OPTION_START_X + 90,
					"y" : BUTTON_START_Y - 3 + 105,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_SHOW_OUTLINE,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Show Damage
		{
			"name" : "show_damage_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 2 + 130,
			"width" : 360,
			"height" : SMALL_OPTION_HEIGHT + 190,
			"children" :
			(
				{
					"name" : "show_damage_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_show_damage",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_SHOWDMG_TITLE,
						},
					),
				},
				{
					"name" : "hide_damage_mobs_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y - 5,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "hide_damage_mobs_label",
					"type" : "text",
					"x" : OPTION_START_X + 90,
					"y" : BUTTON_START_Y - 3,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_SHOWMOB_ONLY,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "hide_damage_all_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y - 5 + 40,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "hide_damage_all_label",
					"type" : "text",
					"x" : OPTION_START_X + 90,
					"y" : BUTTON_START_Y - 3 + 40,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_SHOWDMG_ALL,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "scaleEff_label",
					"type" : "text",
					"x" : SLIDER_BAR_X,
					"y" : BUTTON_START_Y + 72,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_DMGSIZE,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "scaleEff_Slider",
					"type" : "sliderbar_advancedgameoptions",
					"x" : SLIDER_BAR_X,
					"y" : BUTTON_START_Y + 90,
				},
				{
					"name" : "damage_color_title",
					"type" : "text",
					"x" : OPTION_START_X - 20,
					"y" : BUTTON_START_Y + 115,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_DMGCOLOR_TITLE,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "damage_color_label_0",
					"type" : "text",
					"x" : OPTION_START_X - 20,
					"y" : BUTTON_START_Y + 138,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_DMGCOLOR_NORMAL,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				{
					"name" : "damage_color_slot_0",
					"type" : "window",
					"x" : 200,
					"y" : BUTTON_START_Y + 136,
					"width" : 60,
					"height" : 18,
				},
				{
					"name" : "damage_color_label_1",
					"type" : "text",
					"x" : OPTION_START_X - 20,
					"y" : BUTTON_START_Y + 164,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_DMGCOLOR_CRITICAL,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				{
					"name" : "damage_color_slot_1",
					"type" : "window",
					"x" : 200,
					"y" : BUTTON_START_Y + 162,
					"width" : 60,
					"height" : 18,
				},
				{
					"name" : "damage_color_label_2",
					"type" : "text",
					"x" : OPTION_START_X - 20,
					"y" : BUTTON_START_Y + 190,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_DMGCOLOR_PIERCE,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				{
					"name" : "damage_color_slot_2",
					"type" : "window",
					"x" : 200,
					"y" : BUTTON_START_Y + 188,
					"width" : 60,
					"height" : 18,
				},
			),
		},
		# Auto-Hunt Aura Color
		{
			"name" : "auto_hunt_color_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 3 + 210,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "auto_hunt_color_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_auto_hunt_color",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_AUTO_HUNT_COLOR_TITLE,
						},
					),
				},
				{
					"name" : "auto_hunt_color_label",
					"type" : "text",
					"x" : OPTION_START_X - 20,
					"y" : BUTTON_START_Y + 8,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_AUTO_HUNT_COLOR,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				{
					"name" : "auto_hunt_color_slot",
					"type" : "window",
					"x" : 200,
					"y" : BUTTON_START_Y + 6,
					"width" : 60,
					"height" : 18,
				},
			),
		},
		# Target Board
		{
			"name" : "target_board_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 4 + 210,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "target_board_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_target_board",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_TARGET_BOARD,
						},
					),
				},
				{
					"name" : "target_board_view",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_TARGET_BOARD_VIEW,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "target_board_no_view",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_TARGET_BOARD_NO_VIEW,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},
		# Name Color Mode
		{
			"name" : "name_color_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 4 + 210,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "name_color_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 0,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_name_color",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_NAME_COLOR,
						},
					),
				},
				{
					"name" : "name_color_normal",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_NAME_COLOR_NORMAL,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "name_color_empire",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					"y" : BUTTON_START_Y,
					"text" : uiscriptlocale.OPTION_NAME_COLOR_EMPIRE,
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},

		)
		+ _auto_shout_children
		+ (
		# ============================================================================
		# CATEGORY 1: GAME - Gameplay and interaction settings
		# ============================================================================

		# PvP Mode
		{
			"name" : "pvp_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 5 + 210,
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
			"y" : SMALL_OPTION_HEIGHT * 6 + 210,
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
		# Pickup Ignore Mode
		{
			"name" : "pickup_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 7 + 230,
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
			),
		},
		# Night/Sky Mode
		{
			"name" : "night_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 8 + 270,
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
					"x" : 205,
					"y" : BUTTON_START_Y + 10,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
				},
				{
					"name" : "save_enve_label",
					"type" : "text",
					"x" : 205 + 20,
					"y" : BUTTON_START_Y + 8,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_ENV_SAVE,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
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
					"y" : BUTTON_START_Y + 115,
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
					"y" : BUTTON_START_Y + 115,
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
					"y" : BUTTON_START_Y + 115,
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
					"y" : BUTTON_START_Y + 170,
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
					"y" : BUTTON_START_Y + 170,
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
					"y" : BUTTON_START_Y + 170,
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
			"y" : SMALL_OPTION_HEIGHT * 8 + 530,
			"width" : 304,
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
		# Keyboard Settings
		{
			"name" : "keyboard_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 9 + 530,
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

		# ============================================================================
		# CATEGORY 2: GRAPHICS - Rendering, camera, and performance settings
		# ============================================================================

		# FOV Option
		{
			"name" : "fov_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 10 + 530,
			"width" : 360,
			"height" : SLIDER_OPTION_HEIGHT,
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
					"y" : SLIDER_START_Y + 15,
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
		# Metin Stone Scale
		{
			"name" : "stonesize_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 10 + 530 + SLIDER_OPTION_HEIGHT,
			"width" : 360,
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
		# Effect Render Distance
		{
			"name" : "effect_distance_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 10 + 530 + SLIDER_OPTION_HEIGHT * 2,
			"width" : 360,
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
		# Hide Effects Section - Row 1
		{
			"name" : "effect_visibility_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 10 + 530 + SLIDER_OPTION_HEIGHT * 3,
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
		# Hide Effects Section - Row 2
		{
			"name" : "effect_visibility_window_2",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 11 + 530 + SLIDER_OPTION_HEIGHT * 3,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
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
		# Private Shop Range
		{
			"name" : "privateshop_range_window_ui",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 11 + 530 + SLIDER_OPTION_HEIGHT * 3 + 50,
			"width" : 360,
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
		# Pet Status
		{
			"name" : "pet_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 11 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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
		# Mount Status
		{
			"name" : "mount_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 12 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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
		# Monster Info
		{
			"name" : "monster_info_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 13 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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
		# FPS Settings
		{
			"name" : "fps_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 14 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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

		# ============================================================================
		# CATEGORY 3: ENVIRONMENT - Weather, lighting, and world effects
		# ============================================================================

		# Fog Mode
		{
			"name" : "fog_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 15 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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
		# Snow Mode
		{
			"name" : "snow_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 16 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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
		# Snow Texture Mode
		{
			"name" : "snowtexture_mode_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 17 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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
		# Shadow Target
		{
			"name" : "shadow_target_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 18 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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
		# Shadow Quality
		{
			"name" : "shadow_quality_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 19 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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

		# Tree Shadow
		{
			"name" : "tree_shadow_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 20 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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
							"text" : "Tree Shadow",
						},
					),
				},
				{
					"name" : "tree_shadow_on",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : "ON",
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
					"text" : "OFF",
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
			"y" : SMALL_OPTION_HEIGHT * 21 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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
							"text" : "Tree Quality",
						},
					),
				},
				{
					"name" : "tree_lod_low",
					"type" : "radio_button",
					"x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					"y" : BUTTON_START_Y,
					"text" : "Low",
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
					"text" : "Medium",
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
					"text" : "High",
					"text_x" : RADIO_BUTTON_TEXT_X,
					"default_image" : IMG_DIR + "radio_unselected.png",
					"over_image" : IMG_DIR + "radio_unselected.png",
					"down_image" : IMG_DIR + "radio_selected.png",
					"color" : PRIMARY_COLOR,
				},
			),
		},

		# ============================================================================
		# CATEGORY 4: SOUND - Audio and music settings
		# ============================================================================

		# Volume Controls
		{
			"name" : "volume_window",
			"type" : "window",
			"x" : 0,
			"y" : SMALL_OPTION_HEIGHT * 22 + 530 + SLIDER_OPTION_HEIGHT * 4 + 50,
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
			"y" : SMALL_OPTION_HEIGHT * 22 + 530 + SLIDER_OPTION_HEIGHT * 6 + 50,
			"width" : 304,
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
