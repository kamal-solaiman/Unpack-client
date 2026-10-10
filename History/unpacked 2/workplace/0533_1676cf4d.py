# coding: latin_1

import uiscriptlocale
import app


def _loc(key, default):
	return getattr(uiscriptlocale, key, default)


ROOT_PATH = "d:/ymir work/ui/game/windows/"

WINDOW_WIDTH = 302
WINDOW_HEIGHT = 424

UPPER_OUTLINE_WIDTH = 280
UPPER_OUTLINE_HEIGHT = 76

MEMBER_INFO_WINDOW_WIDTH = 266
MEMBER_INFO_WINDOW_HEIGHT = 255

MAIN_WINDOW_POS_X = 0
MAIN_WINDOW_POS_Y = 30

LOWER_MAIN_TAB_IMAGE_HEIGHT = 68

window = {
	"name"		: "community_window",
	"style"		: ("movable", "float",),

	"x"			: SCREEN_WIDTH / 2 - WINDOW_WIDTH / 2,
	"y"			: SCREEN_HEIGHT / 2 - WINDOW_HEIGHT / 2,

	"width"		: WINDOW_WIDTH,
	"height"	: WINDOW_HEIGHT,

	"children" :
	(
		{
			"name"		: "main_bg",
			"type"		: "board_with_titlebar",

			"x"			: 0,
			"y"			: 0,

			"width"		: WINDOW_WIDTH,
			"height"	: WINDOW_HEIGHT,

			"title"		: _loc("COMMUNITY_MAIN_TITLE", "Community"),

			"children"	:
			(
				{
					"name"		: "my_info_bg",
					"type"		: "image",
					"style" : ("ltr",),

					"x"			: 11,
					"y"			: UPPER_OUTLINE_HEIGHT / 2 - 3,

					"image"		: ROOT_PATH + "community_info_bar_player.sub",

					"children"	:
					(
						{
							"name"			: "my_info_state_drop_list_button",
							"type"			: "button",

							"x"				: 26,
							"y"				: 9,

							"default_image"	: ROOT_PATH + "community_drop_button_default.sub",
							"over_image"	: ROOT_PATH + "community_drop_button_mouse_over.sub",
							"down_image"	: ROOT_PATH + "community_drop_button_click.sub",
						},

						{
							"name"					: "my_info_main_player_guild_name",
							"type"					: "text",

							"x"						: 95,
							"y"						: 0,

							"vertical_align"		: "center",
							"horizontal_align"		: "left",
							"text_vertical_align"	: "center",
							"text_horizontal_align"	: "center",

							"text"					: _loc("COMMUNITY_NO_GUILD", "No guild"),
						},

						{
							"name"					: "my_info_main_player_name",
							"type"					: "text",
							"style"					: ("not_pick",),

							"x"						: 205,
							"y"						: 0,

							"vertical_align"		: "center",
							"horizontal_align"		: "left",
							"text_vertical_align"	: "center",
							"text_horizontal_align"	: "center",

							"text"					: _loc("COMMUNITY_ERROR", "Unknown"),
						},

						{
							"name"		: "my_info_main_player_name_collision",
							"type"		: "window",

							"x"			: 150,
							"y"			: 8,

							"width"		: 110,
							"height"	: 17,
						},

						{
							"name"			: "my_info_my_message_button",
							"type"			: "button",

							"x"				: 259,
							"y"				: 8,

							"default_image"	: ROOT_PATH + "community_icon_my_message_default.sub",
							"over_image"	: ROOT_PATH + "community_icon_my_message_mouse_over.sub",
							"down_image"	: ROOT_PATH + "community_icon_my_message_click.sub",
						},
					),
				},

				{
					"name"		: "messenger_view_window",
					"type"		: "window",

					"x"			: MAIN_WINDOW_POS_X,
					"y"			: MAIN_WINDOW_POS_Y,

					"width"		: WINDOW_WIDTH,
					"height"	: WINDOW_HEIGHT,

					"children"	:
					(
						{
							"name"		: "messenger_upper_outline_window",
							"type"		: "outline_window",

							"x"			: 11,
							"y"			: 4,

							"width"		: UPPER_OUTLINE_WIDTH,
							"height"	: UPPER_OUTLINE_HEIGHT,
						},

						{
							"name"		: "messenger_friend_member_tab_image",
							"type"		: "image",

							"x"			: 10,
							"y"			: 82,

							"image"		: ROOT_PATH + "community_friend_member.sub",
						},

						{
							"name"		: "messenger_block_member_tab_image",
							"type"		: "image",

							"x"			: 10,
							"y"			: 82,

							"image"		: ROOT_PATH + "community_friend_block.sub",
						},

						{
							"name"		: "messenger_request_member_tab_image",
							"type"		: "image",

							"x"			: 10,
							"y"			: 82,

							"image"		: ROOT_PATH + "community_friend_request.sub",
						},

						{
							"name"		: "messenger_friend_member_tab_button",
							"type"		: "radio_button",

							"x"			: 13,
							"y"			: 88,

							"width"		: 46,
							"height"	: 20,
						},

						{
							"name"		: "messenger_block_member_tab_button",
							"type"		: "radio_button",

							"x"			: 58,
							"y"			: 88,

							"width"		: 46,
							"height"	: 20,
						},

						{
							"name"		: "messenger_request_member_tab_button",
							"type"		: "radio_button",

							"x"			: 103,
							"y"			: 88,

							"width"		: 46,
							"height"	: 20,
						},

						{
							"name"		: "community_request_button_twinkle",
							"type"		: "image",
							"style"		: ("not_pick",),

							"x"			: 104,
							"y"			: 89,

							"image"		: ROOT_PATH + "community_request_button_twinkle.sub",
						},

						{
							"name"			: "friend_invite",
							"type"			: "button",

							"x"				: 160,
							"y"				: 112 - MAIN_WINDOW_POS_Y,

							"default_image"	: ROOT_PATH + "community_icon_friend_invite_default.sub",
							"over_image"	: ROOT_PATH + "community_icon_friend_invite_mouse_over.sub",
							"down_image"	: ROOT_PATH + "community_icon_friend_invite_click.sub",
						},

						{
							"name"			: "friend_block",
							"type"			: "button",

							"x"				: 160 + 30,
							"y"				: 112 - MAIN_WINDOW_POS_Y,

							"default_image"	: ROOT_PATH + "community_icon_block_default.sub",
							"over_image"	: ROOT_PATH + "community_icon_block_mouse_over.sub",
							"down_image"	: ROOT_PATH + "community_icon_block_click.sub",
						},

						{
							"name"			: "friend_whisper",
							"type"			: "button",

							"x"				: 160 + 60,
							"y"				: 112 - MAIN_WINDOW_POS_Y,

							"default_image"	: ROOT_PATH + "community_icon_whisper_default.sub",
							"over_image"	: ROOT_PATH + "community_icon_whisper_mouse_over.sub",
							"down_image"	: ROOT_PATH + "community_icon_whisper_click.sub",
						},

						{
							"name"			: "friend_delete",
							"type"			: "button",

							"x"				: 160 + 90,
							"y"				: 112 - MAIN_WINDOW_POS_Y,

							"default_image"	: ROOT_PATH + "community_icon_delete_default.sub",
							"over_image"	: ROOT_PATH + "community_icon_delete_mouse_over.sub",
							"down_image"	: ROOT_PATH + "community_icon_delete_click.sub",
						},

						{
							"name"		: "messenger_scroll_bar",
							"type"		: "scrollbar",

							"x"			: 278,
							"y"			: 109,

							"size"		: 253,
						},
					),
				},

				{
					"name"		: "guild_view_window",
					"type"		: "window",

					"x"			: MAIN_WINDOW_POS_X,
					"y"			: MAIN_WINDOW_POS_Y,

					"width"		: WINDOW_WIDTH,
					"height"	: WINDOW_HEIGHT,

					"children"	:
					(
						{
							"name"		: "guild_player_has_guild_window",
							"type"		: "window",

							"x"			: 10,
							"y"			: 45,

							"width"		: UPPER_OUTLINE_WIDTH,
							"height"	: MEMBER_INFO_WINDOW_HEIGHT + LOWER_MAIN_TAB_IMAGE_HEIGHT,

							"children"	:
							(
								{
									"name"		: "guild_member_tab_image",
									"type"		: "image",

									"x"			: 0,
									"y"			: 0,

									"image"		: ROOT_PATH + "community_guild_member.sub",
								},

								{
									"name"		: "guild_member_tab_button",
									"type"		: "radio_button",

									"x"			: 3,
									"y"			: 5,

									"width"		: 46,
									"height"	: 20,
								},

								{
									"name"			: "guild_invite",
									"type"			: "button",

									"x"				: 150,
									"y"				: 0,

									"default_image"	: ROOT_PATH + "community_icon_friend_invite_default.sub",
									"over_image"	: ROOT_PATH + "community_icon_friend_invite_mouse_over.sub",
									"down_image"	: ROOT_PATH + "community_icon_friend_invite_click.sub",
								},

								{
									"name"			: "guild_block",
									"type"			: "button",

									"x"				: 150 + 30,
									"y"				: 0,

									"default_image"	: ROOT_PATH + "community_icon_block_default.sub",
									"over_image"	: ROOT_PATH + "community_icon_block_mouse_over.sub",
									"down_image"	: ROOT_PATH + "community_icon_block_click.sub",
								},

								{
									"name"			: "guild_whisper",
									"type"			: "button",

									"x"				: 150 + 60,
									"y"				: 0,

									"default_image"	: ROOT_PATH + "community_icon_whisper_default.sub",
									"over_image"	: ROOT_PATH + "community_icon_whisper_mouse_over.sub",
									"down_image"	: ROOT_PATH + "community_icon_whisper_click.sub",
								},

								{
									"name"			: "guild_delete",
									"type"			: "button",

									"x"				: 150 + 90,
									"y"				: 0,

									"default_image"	: ROOT_PATH + "community_icon_delete_default.sub",
									"over_image"	: ROOT_PATH + "community_icon_delete_mouse_over.sub",
									"down_image"	: ROOT_PATH + "community_icon_delete_click.sub",
								},

								{
									"name"			: "guild_info_button",
									"type"			: "button",

									"x"				: 165,
									"y"				: 295,

									"default_image"	: ROOT_PATH + "community_button_default.sub",
									"over_image"	: ROOT_PATH + "community_button_mouse_over.sub",
									"down_image"	: ROOT_PATH + "community_button_click.sub",

									"text"			: _loc("COMMUNITY_GUILD_INFO", "Guild information"),
								},
							),
						},

						{
							"name"		: "guild_player_no_guild_window",
							"type"		: "outline_window",

							"x"			: 10,
							"y"			: 72,

							"width"		: MEMBER_INFO_WINDOW_WIDTH + 15,
							"height"	: MEMBER_INFO_WINDOW_HEIGHT,

							"children"	:
							(
								{
									"name"					: "guild_has_no_guild_text",
									"type"					: "text",

									"x"						: 140,
									"y"						: -35,

									"horizontal_align"		: "left",
									"vertical_align"		: "center",
									"text_vertical_align"	: "center",
									"text_horizontal_align"	: "center",

									"text"					: _loc("COMMUNITY_HAS_NO_GUILD", "You are not in a guild."),
								},

								{
									"name"					: "guild_has_no_guild_text_2",
									"type"					: "text",

									"x"						: 140,
									"y"						: 0,

									"horizontal_align"		: "left",
									"vertical_align"		: "center",
									"text_vertical_align"	: "center",
									"text_horizontal_align"	: "center",

									"text"					: _loc("COMMUNITY_HAS_NO_GUILD_2", "View guilds you can join"),
								},

								{
									"name"			: "guild_view_guild_list_button",
									"type"			: "button",

									"x"				: 95,
									"y"				: 165,

									"default_image"	: "d:/ymir work/ui/game/guild/guildbuttons/infopage/GuildListButton00.sub",
									"over_image"	: "d:/ymir work/ui/game/guild/guildbuttons/infopage/GuildListButton01.sub",
									"down_image"	: "d:/ymir work/ui/game/guild/guildbuttons/infopage/GuildListButton02.sub",
								},
							),
						},
					),
				},

				{
					"name"		: "config_view_window",
					"type"		: "window",

					"x"			: MAIN_WINDOW_POS_X,
					"y"			: MAIN_WINDOW_POS_Y,

					"width"		: WINDOW_WIDTH,
					"height"	: WINDOW_HEIGHT,

					"children"	:
					(
						{
							"name"		: "config_info_bg",
							"type"		: "outline_window",

							"x"			: 11,
							"y"			: 1,

							"width"		: 266,
							"height"	: 325,
						},

						{
							"name"		: "config_scroll_bar",
							"type"		: "scrollbar",

							"x"			: 278,
							"y"			: 10,

							"size"		: 335,
						},

						{
							"name"			: "config_setting_save_button",
							"type"			: "button",

							"x"				: 175,
							"y"				: 335,

							"default_image"	: ROOT_PATH + "community_button_default.sub",
							"over_image"	: ROOT_PATH + "community_button_mouse_over.sub",
							"down_image"	: ROOT_PATH + "community_button_click.sub",

							"text"			: _loc("COMMUNITY_CONFIG_SAVE", "Save"),
						},

						{
							"name"			: "config_setting_init_button",
							"type"			: "button",

							"x"				: 12,
							"y"				: 335,

							"default_image"	: ROOT_PATH + "community_button_default.sub",
							"over_image"	: ROOT_PATH + "community_button_mouse_over.sub",
							"down_image"	: ROOT_PATH + "community_button_click.sub",

							"text"			: _loc("COMMUNITY_CONFIG_INIT", "Reset"),
						},
					),
				},

				{
					"name"		: "community_messenger_tab_image",
					"type"		: "image",

					"x"			: 0,
					"y"			: 396,

					"image"		: ROOT_PATH + "community_lower_tab_friend.sub",
				},

				{
					"name"		: "community_guild_tab_image",
					"type"		: "image",

					"x"			: 0,
					"y"			: 396,

					"image"		: ROOT_PATH + "community_lower_tab_guild.sub",
				},

				{
					"name"		: "community_config_tab_image",
					"type"		: "image",

					"x"			: 0,
					"y"			: 396,

					"image"		: ROOT_PATH + "community_lower_tab_config.sub",
				},

				{
					"name"		: "community_messenger_tab_button",
					"type"		: "radio_button",

					"x"			: 10,
					"y"			: 400,

					"width"		: 95,
					"height"	: 30,
				},

				{
					"name"		: "community_guild_tab_button",
					"type"		: "radio_button",

					"x"			: 105,
					"y"			: 400,

					"width"		: 95,
					"height"	: 30,
				},

				{
					"name"		: "community_config_tab_button",
					"type"		: "radio_button",

					"x"			: 200,
					"y"			: 400,

					"width"		: 95,
					"height"	: 30,
				},
			),
		},
	),
}
