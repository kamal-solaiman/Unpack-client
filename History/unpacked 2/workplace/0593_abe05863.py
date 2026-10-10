# coding: utf-8

import uiscriptlocale

BOARD_WIDTH = 248
BOARD_HEIGHT = 150

window = {
	"name" : "GrowthPetEvolve_Dialog",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	(
		{
			"name" : "board_ui",
			"type" : "board",
			"style" : ("attach",),
			"x" : 0,
			"y" : 0,
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			"children" :
			(
				{
					"name" : "titlebar_ui",
					"type" : "titlebar",
					"style" : ("attach",),
					"x" : 6,
					"y" : 6,
					"width" : BOARD_WIDTH - 6,
					"color" : "yellow",
					"children" :
					(
						{
							"name" : "titlename_ui",
							"type" : "text",
							"x" : BOARD_WIDTH / 2,
							"y" : 3,
							"text" : uiscriptlocale.GROWTH_PET_EVOLVE_TITLE,
							"text_horizontal_align" : "center"
						},
					),
				},
				{
					"name" : "subboard_ui",
					"type" : "thinboard_circle",
					"style" : ("attach",),
					"x" : 12,
					"y" : 40,
					"width" : BOARD_WIDTH - 24,
					"height" : 71,
				},
				{
					"name" : "subboard_ui",
					"type" : "v3_thinboard",
					"style" : ("attach",),
					"x" : 12,
					"y" : 40,
					"width" : BOARD_WIDTH - 24,
					"height" : 71,
					"children" :
					(
						{
							"name" : "itemslot_ui",
							"type" : "grid_table",
							"x" : -3,
							"y" : 8,
							"start_index" : 0,
							"x_count" : 5,
							"y_count" : 1,
							"x_step" : 44,
							"y_step" : 32,
							"image" : "d:/ymir work/ui/public/slot_base.sub"
						},
						{
							"name" : "splitbar1_ui",
							"type" : "bar",
							"x" : 45,
							"y" : 1,
							"width" : 2,
							"height" : 71 - 3,
							"color" : 0xFF5F5F5F
						},
						{
							"name" : "splitbar2_ui",
							"type" : "bar",
							"x" : (45 * 2) - 1,
							"y" : 1,
							"width" : 2,
							"height" : 71 - 3,
							"color" : 0xFF5F5F5F
						},
						{
							"name" : "splitbar3_ui",
							"type" : "bar",
							"x" : (45 * 3) - 2,
							"y" : 1,
							"width" : 2,
							"height" : 71 - 3,
							"color" : 0xFF5F5F5F
						},
						{
							"name" : "splitbar5_ui",
							"type" : "bar",
							"x" : (45 * 4) - 3,
							"y" : 1,
							"width" : 2,
							"height" : 71 - 3,
							"color" : 0xFF5F5F5F
						},
						{
							"name" : "splitbar4_ui",
							"type" : "bar",
							"x" : 1,
							"y" : 45,
							"width" : BOARD_WIDTH - 24 - 2,
							"height" : 2,
							"color" : 0xFF5F5F5F
						},
						{
							"name" : "contentwindow5_ui",
							"type" : "window",
							"x" : 3,
							"y" : 1 + 45 + 2,
							"width" : 40,
							"height" : 20,
							"children" :
							(
								{
									"name" : "counttext5_ui",
									"type" : "text",
									"x" : 40 / 2,
									"y" : 3,
									"text" : "1 / 1",
									"text_horizontal_align" : "center"
								},
							),
						},
						{
							"name" : "contentwindow4_ui",
							"type" : "window",
							"x" : 48,
							"y" : 1 + 45 + 2,
							"width" : 40,
							"height" : 20,
							"children" :
							(
								{
									"name" : "counttext4_ui",
									"type" : "text",
									"x" : 40 / 2,
									"y" : 3,
									"text" : "1 / 1",
									"text_horizontal_align" : "center"
								},
							),
						},
						{
							"name" : "contentwindow3_ui",
							"type" : "window",
							"x" : 92,
							"y" : 1 + 45 + 2,
							"width" : 40,
							"height" : 20,
							"children" :
							(
								{
									"name" : "counttext3_ui",
									"type" : "text",
									"x" : 40 / 2,
									"y" : 3,
									"text" : "1 / 1",
									"text_horizontal_align" : "center"
								},
							),
						},
						{
							"name" : "contentwindow2_ui",
							"type" : "window",
							"x" : 137,
							"y" : 1 + 45 + 2,
							"width" : 40,
							"height" : 20,
							"children" :
							(
								{
									"name" : "counttext2_ui",
									"type" : "text",
									"x" : 40 / 2,
									"y" : 3,
									"text" : "1 / 1",
									"text_horizontal_align" : "center"
								},
							),
						},
						{
							"name" : "contentwindow1_ui",
							"type" : "window",
							"x" : 181,
							"y" : 1 + 45 + 2,
							"width" : 40,
							"height" : 20,
							"children" :
							(
								{
									"name" : "counttext1_ui",
									"type" : "text",
									"x" : 40 / 2,
									"y" : 3,
									"text" : "1 / 1",
									"text_horizontal_align" : "center"
								},
							),
						},
					),
				},
				{
					"name" : "evolvebutton_ui",
					"type" : "button",
					"x" : 0,
					"y" : 40 + 80,
					"horizontal_align" : "center",
					"default_image" : "d:/ymir work/ui/pet/feed_button/feed_button_default.sub",
					"over_image" : "d:/ymir work/ui/pet/feed_button/feed_button_over.sub",
					"down_image" : "d:/ymir work/ui/pet/feed_button/feed_button_down.sub",
					"text" : uiscriptlocale.GROWTH_PET_EVOLVE_BUTTON_TEXT,
					"text_color" : 0xFFFEE3AE
				},
			),
		},
	),
}
