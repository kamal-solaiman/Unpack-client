# coding: latin_1

import localeinfo

IMG_DIR = "d:/ymir work/ui/game/wb_rework/"

WINDOW_WIDTH = 641 + 20
WINDOW_HEIGHT = 371 + 45

BG_X = 10
BG_Y = 35

window = {
	"name": "WorldBossWindow",
	"x": 0,
	"y": 0,
	"style": ("movable", "float",),
	"width": WINDOW_WIDTH,
	"height": WINDOW_HEIGHT,
	"children":
	(
		{
			"name": "board",
			"type": "board",
			"style": ("movable", "attach", "float",),
			"x": 0,
			"y": 0,
			"width": WINDOW_WIDTH,
			"height": WINDOW_HEIGHT,
			"children":
			(
				{
					"name": "TitleBar",
					"type": "titlebar",
					"style": ("attach",),
					"x": 6,
					"y": 6,
					"width": WINDOW_WIDTH - 15,
					"color": "yellow",
					"children":
					(
						{
							"name": "TitleName",
							"type": "text",
							"x": (WINDOW_WIDTH - 15) / 2,
							"y": 3,
							"text": localeinfo.TRACK_WINDOW_TITLE,
							"text_horizontal_align": "center",
						},
					),
				},
				{
					"name": "bg",
					"type": "image",
					"x": BG_X,
					"y": BG_Y,
					"image": IMG_DIR + "bg.png",
				},

				## Boss selector buttons — 3 bosses
				{
					"name": "boss_btn_0",
					"type": "button",
					"x": BG_X + 8,
					"y": BG_Y + 3,
					"default_image": IMG_DIR + "avail_4901_1.png",
					"over_image": IMG_DIR + "avail_4901_2.png",
					"down_image": IMG_DIR + "avail_4901_3.png",
					"text": "",
				},
				{
					"name": "boss_btn_1",
					"type": "button",
					"x": BG_X + 8 + 105,
					"y": BG_Y + 3,
					"default_image": IMG_DIR + "avail_4902_1.png",
					"over_image": IMG_DIR + "avail_4902_2.png",
					"down_image": IMG_DIR + "avail_4902_3.png",
					"text": "",
				},
				{
					"name": "boss_btn_2",
					"type": "button",
					"x": BG_X + 8 + 210,
					"y": BG_Y + 3,
					"default_image": IMG_DIR + "avail_4903_1.png",
					"over_image": IMG_DIR + "avail_4903_2.png",
					"down_image": IMG_DIR + "avail_4903_3.png",
					"text": "",
				},
				{
					"name": "boss_btn_3",
					"type": "button",
					"x": BG_X + 8 + 315,
					"y": BG_Y + 3,
					"default_image": IMG_DIR + "btn_boss_1.png",
					"over_image": IMG_DIR + "btn_boss_2.png",
					"down_image": IMG_DIR + "btn_boss_3.png",
					"text": "",
				},

				## Boss name (top of right panel, above render)
				{
					"name": "boss_name_text",
					"type": "text",
					"x": BG_X + 90,
					"y": BG_Y + 30 + 23,
					"text": "",
					"text_horizontal_align": "center",
					"fontcolor": 0xFFDBA54E,
				},

				## Boss render window (right panel)
				{
					"name": "boss_render_window",
					"type": "window",
					"x": BG_X + 8,
					"y": BG_Y + 45 + 33,
					"width": 212,
					"height": 249,
				},

				## Reward info button
				{
					"name": "reward_info_btn",
					"type": "button",
					"x": 593,
					"y": 89,
					"default_image": "d:/ymir work/ui/pattern/q_mark_01.tga",
					"over_image": "d:/ymir work/ui/pattern/q_mark_02.tga",
					"down_image": "d:/ymir work/ui/pattern/q_mark_02.tga",
				},

				## Middle panel top — Boss Info rows
				{
					"name": "status_img",
					"type": "image",
					"x": 300,
					"y": 119,
					"image": IMG_DIR + "dead.png",
				},
				{
					"name": "timer_label",
					"type": "text",
					"x": BG_X + 230,
					"y": BG_Y + 122,
					"text": localeinfo.WB_RESPAWN,
					"color" : 0xFFb1aa8c,
				},
				{
					"name": "timer_value",
					"type": "text",
					"x": BG_X + 328,
					"y": BG_Y + 122,
					"text": "",
					"color" : 0xFFb1aa8c,
				},
				{
					"name": "coin_label",
					"type": "text",
					"x": BG_X + 230,
					"y": BG_Y + 156,
					"text": localeinfo.WB_WALLET_TITLE,
					"color" : 0xFFb1aa8c,
				},
				{
					"name": "coin_value",
					"type": "text",
					"x": BG_X + 328,
					"y": BG_Y + 156,
					"text": "-",
					"text_horizontal_align": "left",
				},
				{
					"name": "coin_hover",
					"type": "window",
					"x": BG_X + 225,
					"y": BG_Y + 152,
					"width": 200,
					"height": 22,
				},

				## Middle panel bottom — Contribution rows
				{
					"name": "wb_points_label",
					"type": "text",
					"x": BG_X + 230,
					"y": BG_Y + 232,
					"text": localeinfo.PVP_ROUTES_POINTS,
					"color" : 0xFFb1aa8c,
				},
				{
					"name": "wb_points_value",
					"type": "text",
					"x": BG_X + 328,
					"y": BG_Y + 232,
					"text": "0",
					"text_horizontal_align": "left",
					"color": 0xFFDBA54E,
				},
				{
					"name": "daily_cap_label",
					"type": "text",
					"x": BG_X + 230,
					"y": BG_Y + 266,
					"text": localeinfo.WB_DAILY_LIMIT,
					"color" : 0xFFb1aa8c,
				},
				{
					"name": "daily_cap_value",
					"type": "text",
					"x": BG_X + 328,
					"y": BG_Y + 266,
					"text": "0/100",
					"text_horizontal_align": "left",
				},
				{
					"name": "your_damage_label",
					"type": "text",
					"x": BG_X + 230,
					"y": BG_Y + 300,
					"text": localeinfo.WB_YOUR_DMG,
				},
				{
					"name": "your_damage_value",
					"type": "text",
					"x": BG_X + 328,
					"y": BG_Y + 300,
					"text": "0",
					"text_horizontal_align": "left",
					"color": 0xFFDBA54E,
				},
				{
					"name": "your_tier_label",
					"type": "text",
					"x": BG_X + 230,
					"y": BG_Y + 334,
					"text": localeinfo.WB_DMG_TIER,
					"color" : 0xFFb1aa8c,
				},
				{
					"name": "your_tier_value",
					"type": "text",
					"x": BG_X + 328,
					"y": BG_Y + 334,
					"text": "-",
					"text_horizontal_align": "left",
				},

				## Weekly reset timer (above ranking)
				{
					"name": "weekly_reset_text",
					"type": "text",
					"x": 537,
					"y": 50,
					"text": "",
					"text_horizontal_align": "center",
					"color": 0xFFb1aa8c,
				},

				## Right panel — Ranking rows
				## Rows 0-2: top 3 with crown backgrounds (1.png, 2.png, 3.png)
				## Rows 3-9: normal rows (4.png)
				## Row 10: "me" row pinned at bottom (me.png)

				{"name": "rank_row_0", "type": "image", "x": 441, "y": 114, "image": IMG_DIR + "1.png",},
				{"name": "rank_row_1", "type": "image", "x": 441, "y": 140, "image": IMG_DIR + "2.png",},
				{"name": "rank_row_2", "type": "image", "x": 441, "y": 140 + 26, "image": IMG_DIR + "3.png",},
				{"name": "rank_row_3", "type": "image", "x": 441, "y": 140 + 26 + 26, "image": IMG_DIR + "4.png",},
				{"name": "rank_row_4", "type": "image", "x": 441, "y": 140 + 26 + 26 + 26, "image": IMG_DIR + "4.png",},
				{"name": "rank_row_5", "type": "image", "x": 441, "y": 140 + 26 + 26 + 26 + 26, "image": IMG_DIR + "4.png",},
				{"name": "rank_row_6", "type": "image", "x": 441, "y": 140 + 26 + 26 + 26 + 26 + 26, "image": IMG_DIR + "4.png",},
				{"name": "rank_row_7", "type": "image", "x": 441, "y": 140 + 26 + 26 + 26 + 26 + 26 + 26, "image": IMG_DIR + "4.png",},
				{"name": "rank_row_8", "type": "image", "x": 441, "y": 140 + 26 + 26 + 26 + 26 + 26 + 26 + 26, "image": IMG_DIR + "4.png",},
				{"name": "rank_row_9", "type": "image", "x": 441, "y": 140 + 26 + 26 + 26 + 26 + 26 + 26 + 26 + 26, "image": IMG_DIR + "4.png",},
				{"name": "rank_row_me", "type": "image", "x": 441, "y": 374, "image": IMG_DIR + "me.png",},

				## Bottom buttons (below boss render)
				{
					"name": "teleport_btn",
					"type": "button",
					"x": BG_X + 10,
					"y": BG_Y + 338,
					"default_image": IMG_DIR + "btn_1.png",
					"over_image": IMG_DIR + "btn_2.png",
					"down_image": IMG_DIR + "btn_3.png",
					"text": localeinfo.TRACK_TELEPORT,
				},
				{
					"name": "shop_btn",
					"type": "button",
					"x": BG_X + 112,
					"y": BG_Y + 338,
					"default_image": IMG_DIR + "btn_1.png",
					"over_image": IMG_DIR + "btn_2.png",
					"down_image": IMG_DIR + "btn_3.png",
					"text": localeinfo.TRACK_OPEN_SHOP,
				},
			),
		},
	),
}
