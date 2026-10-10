# coding: latin_1
# Category 0: Interface - Display and visibility settings

import uiscriptlocale
import app

IMG_DIR = "d:/ymir work/ui/game/advanced_game_options/"

TITLE_IMAGE_TEXT_X = 155
TITLE_IMAGE_TEXT_Y = 2

OPTION_START_X = 72
SLIDER_POSITION_X = 50


SLIDER_START_Y = 40
BUTTON_START_Y = 38
BUTTON_NEXT_Y = 20

RADIO_BUTTON_RANGE_X = 65 + 65
TOGGLE_BUTTON_RANGE_X = 65

RADIO_BUTTON_TEXT_X = - 20
TOGGLE_BUTTON_TEXT_X = 20

SMALL_OPTION_HEIGHT = 80
NORMAL_OPTION_HEIGHT = 80
SLIDER_OPTION_HEIGHT = 65
SLIDER_SECTION_WIDTH = 360
SLIDER_BAR_X = 31
TOGGLE_OPTION_HEIGHT = 80
NAME_VISIBILITY_HEIGHT = SMALL_OPTION_HEIGHT + 70  # Height for the 3-toggle name visibility section

PRIMARY_COLOR = 0xffd0c2b7
SECONDARY_COLOR = 0xff9f9892
DESCRIPTION_COLOR = 0xff8a8078

RES_SHIFT = 0
_resolution_children = ()
if app.ENABLE_WINDOW_RESIZE:
	RES_SHIFT = SMALL_OPTION_HEIGHT
	_resolution_children = (
		{
			"name" : "resolution_window",
			"type" : "window",
			"x" : 0,
			"y" : 0,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT,
			"children" :
			(
				{
					"name" : "resolution_title_img",
					"type" : "expanded_image",
					"x" : 8,
					"y" : 2,
					"image" : IMG_DIR + "option_title_2.png",
					"children" :
					(
						{
							"name" : "title_resolution",
							"type" : "text",
							"x" : TITLE_IMAGE_TEXT_X,
							"y" : TITLE_IMAGE_TEXT_Y,
							"text_horizontal_align" : "center",
							"text" : uiscriptlocale.OPTION_RESOLUTION,
						},
					),
				},
				{
					"name" : "resolution_description",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y + 25,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_RESOLUTION_DESC,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
			),
		},
	)

AURA_SHIFT = 0
_auto_hunt_color_children = ()
if app.ENABLE_AUTO_HUNT_EFFECT_COLOR:
	AURA_SHIFT = SMALL_OPTION_HEIGHT
	_auto_hunt_color_children = (
		{
			"name" : "auto_hunt_color_window",
			"type" : "window",
			"x" : 0,
			"y" : 110 + 10 + TOGGLE_OPTION_HEIGHT + NAME_VISIBILITY_HEIGHT + SMALL_OPTION_HEIGHT * 3 + RES_SHIFT,
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
					"y" : BUTTON_START_Y + 3,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_AUTO_HUNT_COLOR,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				{
					"name" : "auto_hunt_color_slot",
					"type" : "window",
					"x" : 200,
					"y" : BUTTON_START_Y + 1,
					"width" : 60,
					"height" : 18,
				},
			),
		},
	)

_auto_shout_children = ()
if app.ENABLE_AUTO_SHOUT_V2:
	_auto_shout_children = (
		{
			"name" : "auto_shout_window",
			"type" : "window",
			"x" : 0,
			"y" : 110 + TOGGLE_OPTION_HEIGHT + NAME_VISIBILITY_HEIGHT + SMALL_OPTION_HEIGHT * 5 + RES_SHIFT + AURA_SHIFT,
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
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y - 3,
					"text_horizontal_align" : "left",
					"text" : getattr(uiscriptlocale, "OPTION_SHOW_AUTO_SHOUT", "Show auto-shouts"),
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "show_auto_shout_description",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y + 12,
					"text_horizontal_align" : "left",
					"text" : getattr(uiscriptlocale, "OPTION_SHOW_AUTO_SHOUT_DESC", "Show shouts sent automatically by other players"),
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
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
	"children" : _resolution_children + _auto_hunt_color_children + _auto_shout_children +
	(
		# View Chat - New Toggle Style with Description
		{
			"name" : "chat_window",
			"type" : "window",
			"x" : 0,
			"y" : 0 + RES_SHIFT,
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
					"y" : BUTTON_START_Y - 5,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "view_chat_description",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y + 15,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_VIEW_CHAT_DESC,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
			),
		},
		# Name Visibility Options - Three toggle options grouped under one title
		{
			"name" : "name_visibility_window",
			"type" : "window",
			"x" : 0,
			"y" : TOGGLE_OPTION_HEIGHT + RES_SHIFT,
			"width" : 304,
			"height" : SMALL_OPTION_HEIGHT + 70 + 50,
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
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y - 3,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_HIDE_NAMES,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "hide_names_description",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y + 12,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_HIDE_NAMES_DESC,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				# Row 2: Shop Names Hide
				{
					"name" : "hide_shops_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y - 5 + 40,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "hide_shops_label",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y - 3 + 40,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_HIDE_SHOPS,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "hide_shops_description",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y + 12 + 40,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_HIDE_SHOPS_DESC,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				# Row 3: NPC Names Hide
				{
					"name" : "hide_npc_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y - 5 + 80,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "hide_npc_label",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y - 3 + 80,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_HIDE_NPC,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "hide_npc_description",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y + 12 + 80,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_HIDE_NPC_DESC,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				
				# Row 4: NAME OUTLINE
				{
					"name" : "outline_name_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y - 5 + 120,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "outline_name_label",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y - 3 + 120,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_SHOW_OUTLINE,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "outline_name_description",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y + 12 + 120,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_SHOW_OUTLINE_DESC,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				
			),
		},
		# # Sales Text Display Show names of the shops in the ci
		# {
			# "name" : "sales_text_window",
			# "type" : "window",
			# "x" : 0,
			# "y" : TOGGLE_OPTION_HEIGHT + SMALL_OPTION_HEIGHT,
			# "width" : 304,
			# "height" : SMALL_OPTION_HEIGHT,
			# "children" :
			# (
				# {
					# "name" : "sales_text_title_img",
					# "type" : "expanded_image",
					# "x" : 8,
					# "y" : 0,
					# "image" : IMG_DIR + "option_title_2.png",
					# "children" :
					# (
						# {
							# "name" : "title_sales_text",
							# "type" : "text",
							# "x" : TITLE_IMAGE_TEXT_X,
							# "y" : TITLE_IMAGE_TEXT_Y,
							# "text_horizontal_align" : "center",
							# "text" : uiscriptlocale.OPTION_SALESTEXT,
						# },
					# ),
				# },
				# {
					# "name" : "salestext_on_button",
					# "type" : "radio_button",
					# "x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					# "y" : BUTTON_START_Y,
					# "text" : uiscriptlocale.OPTION_VIEW_CHAT_ON,
					# "text_x" : RADIO_BUTTON_TEXT_X,
					# "default_image" : IMG_DIR + "radio_unselected.png",
					# "over_image" : IMG_DIR + "radio_unselected.png",
					# "down_image" : IMG_DIR + "radio_selected.png",
					# "color" : PRIMARY_COLOR,
				# },
				# {
					# "name" : "salestext_off_button",
					# "type" : "radio_button",
					# "x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					# "y" : BUTTON_START_Y,
					# "text" : uiscriptlocale.OPTION_VIEW_CHAT_OFF,
					# "text_x" : RADIO_BUTTON_TEXT_X,
					# "default_image" : IMG_DIR + "radio_unselected.png",
					# "over_image" : IMG_DIR + "radio_unselected.png",
					# "down_image" : IMG_DIR + "radio_selected.png",
					# "color" : PRIMARY_COLOR,
				# },
			# ),
		# },
		# Name Display Type (Outline) show outline or not
		# {
			# "name" : "name_type_window",
			# "type" : "window",
			# "x" : 0,
			# "y" : TOGGLE_OPTION_HEIGHT + NAME_VISIBILITY_HEIGHT,
			# "width" : 304,
			# "height" : SMALL_OPTION_HEIGHT,
			# "children" :
			# (
				# {
					# "name" : "name_type_title_img",
					# "type" : "expanded_image",
					# "x" : 8,
					# "y" : 0,
					# "image" : IMG_DIR + "option_title_2.png",
					# "children" :
					# (
						# {
							# "name" : "title_name_type",
							# "type" : "text",
							# "x" : TITLE_IMAGE_TEXT_X,
							# "y" : TITLE_IMAGE_TEXT_Y,
							# "text_horizontal_align" : "center",
							# "text" : uiscriptlocale.GAMEOPTION_TITLE,
						# },
					# ),
				# },

			# ),
		# },

		# Show Damage
		{
			"name" : "show_damage_window",
			"type" : "window",
			"x" : 0,
			"y" : TOGGLE_OPTION_HEIGHT + NAME_VISIBILITY_HEIGHT + SMALL_OPTION_HEIGHT + RES_SHIFT,
			"width" : SLIDER_SECTION_WIDTH,
			"height" : SMALL_OPTION_HEIGHT + 200,
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
				# Row 1: NEW ADDON : HIDE ALL DMG TAKEN FROM MOBS ONLY (will show ur dmg)
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
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y - 3,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_SHOWMOB_ONLY,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "hide_damage_mobs_description",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y + 12,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_SHOWMOB_ONLY_DESC,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				# Row 1: HIDE ALL DMG TAKEN AND GIVING
				{
					"name" : "hide_damage_all_toggle",
					"type" : "toggle_button",
					"x" : 56,
					"y" : BUTTON_START_Y - 5 + 50,
					"default_image" : IMG_DIR + "toggle_unselected.png",
					"over_image" : IMG_DIR + "toggle_unselected.png",
					"down_image" : IMG_DIR + "toggle_selected.png",
				},
				{
					"name" : "hide_damage_all_label",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y - 3 + 50,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_SHOWDMG_ALL,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "hide_damage_all_description",
					"type" : "text",
					"x" : OPTION_START_X + 30,
					"y" : BUTTON_START_Y + 12 + 50,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_SHOWDMG_ALL_DESC,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				{
					"name" : "scaleEff_label",
					"type" : "text",
					"x" : SLIDER_BAR_X,
					"y" : BUTTON_START_Y - 3 + 84,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_DMGSIZE,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "scaleEff_Slider",
					"type" : "sliderbar_advancedgameoptions",
					"x" : SLIDER_BAR_X,
					"y" : BUTTON_START_Y + 12 + 90,
				},
				{
					"name" : "damage_color_title",
					"type" : "text",
					"x" : OPTION_START_X - 20,
					"y" : BUTTON_START_Y + 135,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_DMGCOLOR_TITLE,
					"outline" : 1,
					"color" : PRIMARY_COLOR,
				},
				{
					"name" : "damage_color_label_0",
					"type" : "text",
					"x" : OPTION_START_X - 20,
					"y" : BUTTON_START_Y + 158,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_DMGCOLOR_NORMAL,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				{
					"name" : "damage_color_slot_0",
					"type" : "window",
					"x" : 200,
					"y" : BUTTON_START_Y + 156,
					"width" : 60,
					"height" : 18,
				},
				{
					"name" : "damage_color_label_1",
					"type" : "text",
					"x" : OPTION_START_X - 20,
					"y" : BUTTON_START_Y + 184,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_DMGCOLOR_CRITICAL,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				{
					"name" : "damage_color_slot_1",
					"type" : "window",
					"x" : 200,
					"y" : BUTTON_START_Y + 182,
					"width" : 60,
					"height" : 18,
				},
				{
					"name" : "damage_color_label_2",
					"type" : "text",
					"x" : OPTION_START_X - 20,
					"y" : BUTTON_START_Y + 210,
					"text_horizontal_align" : "left",
					"text" : uiscriptlocale.OPTION_DMGCOLOR_PIERCE,
					"outline" : 1,
					"color" : DESCRIPTION_COLOR,
				},
				{
					"name" : "damage_color_slot_2",
					"type" : "window",
					"x" : 200,
					"y" : BUTTON_START_Y + 208,
					"width" : 60,
					"height" : 18,
				},
				# {
					# "name" : "show_damage_on_button",
					# "type" : "radio_button",
					# "x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 0,
					# "y" : BUTTON_START_Y,
					# "text" : uiscriptlocale.OPTION_VIEW_CHAT_ON,
					# "text_x" : RADIO_BUTTON_TEXT_X,
					# "default_image" : IMG_DIR + "radio_unselected.png",
					# "over_image" : IMG_DIR + "radio_unselected.png",
					# "down_image" : IMG_DIR + "radio_selected.png",
					# "color" : PRIMARY_COLOR,
				# },
				# {
					# "name" : "show_damage_off_button",
					# "type" : "radio_button",
					# "x" : OPTION_START_X + RADIO_BUTTON_RANGE_X * 1,
					# "y" : BUTTON_START_Y,
					# "text" : uiscriptlocale.OPTION_VIEW_CHAT_OFF,
					# "text_x" : RADIO_BUTTON_TEXT_X,
					# "default_image" : IMG_DIR + "radio_unselected.png",
					# "over_image" : IMG_DIR + "radio_unselected.png",
					# "down_image" : IMG_DIR + "radio_selected.png",
					# "color" : PRIMARY_COLOR,
				# },
			),
		},
		# Target Board
		{
			"name" : "target_board_window",
			"type" : "window",
			"x" : 0,
			"y" : 110 + 10 + TOGGLE_OPTION_HEIGHT + NAME_VISIBILITY_HEIGHT + SMALL_OPTION_HEIGHT * 3 + RES_SHIFT + AURA_SHIFT,
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
			"y" : 110 + TOGGLE_OPTION_HEIGHT + NAME_VISIBILITY_HEIGHT + SMALL_OPTION_HEIGHT * 4 + RES_SHIFT + AURA_SHIFT,
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
	),
}
