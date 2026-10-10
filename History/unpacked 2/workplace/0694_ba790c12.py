# coding: latin_1

import uiscriptlocale
ROOT = "d:/ymir work/ui/minimap/"
PATH = "d:/ymir work/ui/new_minimap/"

window = {
	"name" : "MiniMap",

	"x" : SCREEN_WIDTH - 200,
	"y" : 0,

	"width" : 200,
	"height" : 210,

	"children" :
	[
		## OpenWindow
		{
			"name" : "OpenWindow",
			"type" : "window",

			"x" : 0,
			"y" : 0,

			"width" : 200,
			"height" : 210,

			"children" :
			[
				{
					"name" : "OpenWindowBGI",
					"type" : "image",
					"x" : 0,
					"y" : 0,
					"image" : PATH + "minimap.png",
				},
				## MiniMapWindow
				{
					"name" : "MiniMapWindow",
					"type" : "window",

					"x" : 4,
					"y" : 5,

					"width" : 200,
					"height" : 200,
				},
				## RankingShowButton
				{
					"name" : "RankingShowButton",
					"type" : "button",

					"x" : 1,
					"y" : 77,

					"default_image" : PATH + "btn_ranking_01.png",
					"over_image" : PATH + "btn_ranking_02.png",
					"down_image" : PATH + "btn_ranking_03.png",

				},
				## InGameEventButton

				## ScaleUpButton
				{
					"name" : "ScaleUpButton",
					"type" : "button",

					"x" : 169,
					"y" : 59,

					"default_image" : PATH + "btn_plus_01.png",
					"over_image" : PATH + "btn_plus_02.png",
					"down_image" : PATH + "btn_plus_03.png",
				},
				## ScaleDownButton
				{
					"name" : "ScaleDownButton",
					"type" : "button",

					"x" : 168,
					"y" : 97,

					"default_image" : PATH + "btn_mini_01.png",
					"over_image" : PATH + "btn_mini_01.png",
					"down_image" : PATH + "btn_mini_01.png",
				},
				## MiniMapHideButton
				{
					"name" : "MiniMapHideButton",
					"type" : "button",

					"x" : 27,
					"y" : 15,

					"default_image" : PATH + "btn_close_01.png",
					"over_image" : PATH + "btn_close_02.png",
					"down_image" : PATH + "btn_close_03.png",
				},
				## AtlasShowButton
				{
					"name" : "AtlasShowButton",
					"type" : "button",

					"x" : 150,
					"y" : 133,

					"default_image" : PATH + "btn_atlas_01.png",
					"over_image" : PATH + "btn_atlas_02.png",
					"down_image" : PATH + "btn_atlas_03.png",
				},
				## ServerInfo
				{
					"name" : "ServerInfo",
					"type" : "text",

					"text_horizontal_align" : "center",

					"outline" : 1,

					"x" : 64,
					"y" : 180,
					"color" : 0xff857492,

					"text" : "",
				},
				## PositionInfo
				{
					"name" : "PositionInfo",
					"type" : "text",

					"text_horizontal_align" : "center",

					"outline" : 1,

					"x" : 70,
					"y" : 160,

					"text" : "",
				},
				## ObserverCount
				{
					"name" : "ObserverCount",
					"type" : "text",

					"text_horizontal_align" : "center",

					"outline" : 1,

					"x" : 70,
					"y" : 180,

					"text" : "",
				},
			],
		},
		{
			"name" : "CloseWindow",
			"type" : "window",

			"x" : 67,
			"y" : 0,

			"width" : 132,
			"height" : 48,

			"children" :
			[
				## ShowButton
				{
					"name" : "MiniMapShowButton",
					"type" : "button",

					"x" : 100,
					"y" : 4,

					"default_image" : ROOT + "minimap_open_default.sub",
					"over_image" : ROOT + "minimap_open_default.sub",
					"down_image" : ROOT + "minimap_open_default.sub",
				},
			],
		},
		{
			"name" : "mast_board_ui",
			"type" : "thinboard",
			"x" : 29,
			"y" : 198 + 14,
			"width" : 140,
			"height" : 62,
			"children" :
			(
				{
					"name" : "mast_text_ui",
					"type" : "text",
					"x" : 140 / 2,
					"y" : 6,
					"text_horizontal_align" : "center",
					"text" : uiscriptlocale.SHIP_DEFENSE_MAST,
				},
				{
					"name" : "mast_text2_ui",
					"type" : "text",
					"x" : 140 / 2,
					"y" : 27,
					"text_horizontal_align" : "center",
					"text" : uiscriptlocale.SHIP_DEFENSE_MAST,
				},
				{
					"name" : "mast_hp_gauge_ui",
					"type" : "gauge",
					"x" : (140 - 85) / 2,
					"y" : 27 + 17,
					"width" : 85,
					"color" : "red",
				},
			),
		},
	],
}


window["children"][0]["children"] = window["children"][0]["children"] + [
	## InGameEventButton
	{
		"name" : "DungeonInfoShowButton",
		"type" : "button",

		"x" : 23,
		"y" : 137,

		"default_image" : PATH + "btn_search_01.png",
		"over_image" : PATH + "btn_search_01.png",
		"down_image" : PATH + "btn_search_01.png",
	},
	{
		"name" : "BiologShowButton",
		"type" : "button",

		"x" : 8,
		"y" : 34,

		"default_image" : PATH + "btn_bio_01.png",
		"over_image" : PATH + "btn_bio_02.png",
		"down_image" : PATH + "btn_bio_03.png",
	},
	{
		"name" : "SearchShowButton",
		"type" : "button",

		"x" : 23,
		"y" : 137,

		"default_image" : PATH + "btn_search_01.png",
		"over_image" : PATH + "btn_search_01.png",
		"down_image" : PATH + "btn_search_01.png",

	},
	
	{
		"name" : "TreeShowButton",
		"type" : "button",

		"x" : 150-30,
		"y" : 133+10,

		"default_image" : PATH + "skilltree_active_default_a.png",
		"over_image" : PATH + "skilltree_active_hover_a.png",
		"down_image" : PATH + "skilltree_active_down_a.png",

	},
	{
		"name" : "RewardShowButton",
		"type" : "button",

		"x" : 81+20,
		"y" : 133+15,

		"default_image" : PATH + "reward_default.png",
		"over_image" : PATH + "reward_hover.png",
		"down_image" : PATH + "reward_down.png",

	},
]

if ENABLE_OSF_MINIMAP_INFO:
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "DateTimeTextLine",
			"type" : "text",

			"x" : 0,
			"y" : 160,

			"text" : __GetCurrentTime,
			"horizontal_align" : "center",
			"text_horizontal_align" : "center",
		},
		{
			"name" : "TimeZoneTextLine",
			"type" : "text",

			"x" : 0,
			"y" : 160 + 15,

			"text" : __GetTimeZone,
			"horizontal_align" : "center",
			"text_horizontal_align" : "center",
		},
	]
if ENABLE_RTT_STATISTICS:
	window["children"][0]["children"] = window["children"][0]["children"] + [
		{
			"name" : "RTTTextLine",
			"type" : "text",

			"x" : 0,
			"y" : 160 + 55,

			"horizontal_align" : "center",
			"text_horizontal_align" : "center",

			"text" : "",
			"outline" : 1,
		},
		{
			"name" : "PacketLossTextLine",
			"type" : "text",

			"x" : 0,
			"y" : 160 + 55 + 15,

			"horizontal_align" : "center",
			"text_horizontal_align" : "center",

			"text" : "",
			"outline" : 1,
		},
	]


if ENABLE_MAILBOX:
	window["children"][0]["children"] = window["children"][0]["children"] + [
		## MailBox
		{
			"name" : "MailBoxButton",
			"type" : "button",

			"x" : 80-23,
			"y" : 120,

			"default_image" : "d:/ymir work/ui/game/mailbox/post_minimap.sub",
			"over_image" : "d:/ymir work/ui/game/mailbox/post_minimap.sub",
			"down_image" : "d:/ymir work/ui/game/mailbox/post_minimap.sub",
		},
		{
			"name" : "MailBoxEffect",
			"type" : "ani_image",

			"x" : 80-23,
			"y" : 120,

			"delay" : 6,

			"images" :
			(
				"d:/ymir work/ui/game/mailbox/minimap_flash/2.sub",
				"d:/ymir work/ui/game/mailbox/minimap_flash/3.sub",
				"d:/ymir work/ui/game/mailbox/minimap_flash/4.sub",
				"d:/ymir work/ui/game/mailbox/minimap_flash/5.sub",
				"d:/ymir work/ui/game/mailbox/minimap_flash/4.sub",
				"d:/ymir work/ui/game/mailbox/minimap_flash/3.sub",
				"d:/ymir work/ui/game/mailbox/minimap_flash/2.sub",
				"d:/ymir work/ui/game/mailbox/minimap_flash/1.sub",
				"d:/ymir work/ui/game/mailbox/minimap_flash/1.sub",
				"d:/ymir work/ui/game/mailbox/minimap_flash/1.sub",
				"d:/ymir work/ui/game/mailbox/minimap_flash/1.sub",
				"d:/ymir work/ui/game/mailbox/minimap_flash/1.sub",
			),
		},
	]

#app.USE_NORTHWIND_DEEPS_DUNGEON
window["children"][0]["children"] = window["children"][0]["children"] + [
	{
		"name" : "ui_dungeon_time_limit_text",
		"type" : "text",
		"x" : 0,
		"y" : 232,
		"r" : 1.0,
		"g" : 1.0,
		"b" : 1.0,
		"a" : 1.0,
		"text" : "",
		"fontname" : "Tahoma:16",
		"horizontal_align" : "center",
		"text_horizontal_align" : "center",
	},
	{
		"name" : "ui_dungeon_debuff_level_window",
		"type" : "window",
		"x" : 58,
		"y" : 232 + 20,
		"width" : 0,
		"height" : 0,
		"children" : [
			{
				"name" : "ui_dungeon_debuff_level_icon",
				"type" : "expanded_image",
				"x" : 0,
				"y" : 0,
				"image" : "d:/ymir work/ui/skill/common/affect/white_dragon_cave_curse.sub",
				"x_scale" : 0.75,
				"y_scale" : 0.75,
			},
			{
				"name" : "ui_dungeon_debuff_level_text_window",
				"type" : "window",
				"x" : 23,
				"y" : 0,
				"width" : 119,
				"height" : 24,
				"children" : [
					{
						"name" : "ui_dungeon_debuff_level_bg",
						"type" : "expanded_image",
						"x" : 0,
						"y" : 0,
						"image" : "d:/ymir work/ui/game/sungmahee_tower/buff_debuff.sub",
						"children" : 
						[
							{
								"name" : "ui_dungeon_debuff_level_text",
								"type" : "movable_text",
								"x" : 119,
								"y" : 5,
								"text" : "",
								"speed" : 0.5,
							},
						],
					},
				],
			},
		],
	},
]
