# coding: latin_1

IMG = "d:/ymir work/ui/game/horse/"

WINDOW_WIDTH = 440
WINDOW_HEIGHT = 400

window = {
	"name" : "HorseUpgradeWindow",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
	"width" : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,
	"children" :
	(
		{
			"name" : "board",
			"type" : "board",
			"style" : ("movable", "attach", "float",),
			"x" : 0,
			"y" : 0,
			"width" : WINDOW_WIDTH,
			"height" : WINDOW_HEIGHT,
			"children" :
			(
				{
					"name" : "TitleBar",
					"type" : "titlebar",
					"style" : ("attach",),
					"x" : 6,
					"y" : 6,
					"width" : WINDOW_WIDTH - 12,
					"color" : "yellow",
					"children" :
					(
						{
							"name" : "TitleName",
							"type" : "text",
							"x" : (WINDOW_WIDTH - 12) / 2,
							"y" : 3,
							"text" : "",
							"text_horizontal_align" : "center",
						},
					),
				},

				## Main background panel (bg.png, 420x310)
				{
					"name" : "bg_main",
					"type" : "image",
					"x" : 10,
					"y" : 30,
					"image" : IMG + "bg.png",
				},

				## ====================================================
				## Header strip: nextlevel.png (left) + header.png (right)
				## ====================================================
				{
					"name" : "nextlevel_image",
					"type" : "image",
					"x" : 15,
					"y" : 33,
					"image" : IMG + "webp/nextlevel.png",
				},
				{
					"name" : "next_level_text",
					"type" : "text",
					"x" : 15 + (114 / 2),
					"y" : 37,
					"text" : "",
					"text_horizontal_align" : "center",
				},
				{
					"name" : "header_image",
					"type" : "image",
					"x" : 129,
					"y" : 33,
					"image" : IMG + "header.png",
				},
				{
					"name" : "current_level_text",
					"type" : "text",
					"x" : 129 + (302 / 2),
					"y" : 37,
					"text" : "",
					"text_horizontal_align" : "center",
				},

				## ====================================================
				## bg_1.png panel (top info, 414x95) @ (14, 53)
				## ====================================================
				{
					"name" : "bg_1_image",
					"type" : "image",
					"x" : 14,
					"y" : 53,
					"image" : IMG + "bg_1.png",
				},

				## Required-item slot (left dark square of bg_1)
				{
					"name" : "item_slot_icon",
					"type" : "image",
					"x" : 389 + 32,
					"y" : 109,
					"image" : "",
				},
				{
					"name" : "item_slot_count",
					"type" : "text",
					"x" : 374 + 32,
					"y" : 123 + 10,
					"text" : "",
					"text_horizontal_align" : "center",
				},

				## Row 1 — Defeat mob
				{
					"name" : "mission_defeat_text",
					"type" : "text",
					"x" : 112 + 30,
					"y" : 60,
					"text" : "",
				},
				{
					"name" : "mission_defeat_icon",
					"type" : "image",
					"x" : 110,
					"y" : 60,
					"image" : IMG + "icon_1.png",
				},

				## Row 2 — Player level
				{
					"name" : "mission_level_text",
					"type" : "text",
					"x" : 112 + 30,
					"y" : 84,
					"text" : "",
				},
				{
					"name" : "mission_level_icon",
					"type" : "image",
					"x" : 112,
					"y" : 84,
					"image" : IMG + "icon_2.png",
				},

				## Row 3 — Required item name
				{
					"name" : "mission_item_text",
					"type" : "text",
					"x" : 112 + 30,
					"y" : 108,
					"text" : "",
				},
				{
					"name" : "mission_item_icon",
					"type" : "image",
					"x" : 112,
					"y" : 108,
					"image" : IMG + "icon_item.png",
				},

				## Row 4 — Yang cost
				{
					"name" : "mission_yang_text",
					"type" : "text",
					"x" : 112 + 30,
					"y" : 129,
					"text" : "",
				},
				{
					"name" : "mission_yang_icon",
					"type" : "image",
					"x" : 113,
					"y" : 129,
					"image" : IMG + "icon_yang.png",
				},

				## Target render area (right square of bg_1)
				{
					"name" : "target_render_board",
					"type" : "thinboard",
					"x" : 15,
					"y" : 57,
					"width" : 90,
					"height" : 87,
				},

				## ====================================================
				## Gauge (between bg_1 and bg_2) @ (10, 151) 420x22
				## ====================================================
				{
					"name" : "gauge_empty",
					"type" : "image",
					"x" : 10,
					"y" : 151,
					"image" : IMG + "gauge_empty.png",
				},
				{
					"name" : "gauge_fill",
					"type" : "expanded_image",
					"x" : 12,
					"y" : 153,
					"image" : IMG + "gauge_content.png",
				},
				{
					"name" : "gauge_text",
					"type" : "text",
					"x" : 220,
					"y" : 156,
					"text" : "",
					"text_horizontal_align" : "center",
				},

				## ====================================================
				## bg_2.png panel (time row + helper items, 414x125) @ (13, 175)
				## ====================================================
				{
					"name" : "bg_2_image",
					"type" : "image",
					"x" : 13,
					"y" : 175,
					"image" : IMG + "bg_2.png",
				},

				## Time row (top of bg_2) — icon 20x18 @ (16, 179)
				{
					"name" : "time_icon",
					"type" : "image",
					"x" : 16,
					"y" : 179,
					"image" : IMG + "icon_time.png",
				},
				{
					"name" : "time_text",
					"type" : "text",
					"x" : 50,
					"y" : 180,
					"text" : "",
				},
				## Live-popup toggle is constructed in code (ImageBox checkbox +
				## label) — see HorseUpgradeWindow.__BuildPopupToggle.

				## Chance breakdown (between time row and helper slots)
				{
					"name" : "chance_breakdown_text",
					"type" : "text",
					"x" : 40 + 35,
					"y" : 200,
					"text" : "",
				},

				## Helper slot 1: Reset (32x32) @ (29, 212)
				{
					"name" : "helper_reset_btn",
					"type" : "image",
					"x" : 29 + 32,
					"y" : 212,
					"image" : "",
				},
				{
					"name" : "helper_reset_text",
					"type" : "text",
					"x" : 70,
					"y" : 212 + 10,
					"text" : "",
				},

				## Helper slot 2: Chance (32x32) @ (29, 257)
				{
					"name" : "helper_chance_btn",
					"type" : "image",
					"x" : 29 + 32,
					"y" : 257,
					"image" : "",
				},
				{
					"name" : "helper_chance_text",
					"type" : "text",
					"x" : 70,
					"y" : 257 + 10,
					"text" : "",
				},

				## ====================================================
				## Start button (414x36) @ (12, 303)
				## ====================================================
				{
					"name" : "start_btn",
					"type" : "button",
					"x" : 12,
					"y" : 303,
					"default_image" : IMG + "webp/btn_start_quest.png",
					"over_image" : IMG + "webp/btn_start_quest_hover.png",
					"down_image" : IMG + "webp/btn_start_quest_clicked.png",
					"text" : "",
				},
			),
		},
	),
}
