# coding: latin_1

MESSENGER_PATH = "d:/ymir work/ui/game/messenger/"
ROW_IMAGE = MESSENGER_PATH + "friend_box.png"

# Rows and the active-title plate reuse the messenger friend box at its native
# size - scaling it would blur the border.
ROW_WIDTH = 255
ROW_HEIGHT = 35
VISIBLE_ROWS = 7

MARGIN = 8
TITLEBAR_HEIGHT = 30

BOARD_WIDTH = 306
PANEL_WIDTH = BOARD_WIDTH - MARGIN * 2

CAPTION_X = 10
CAPTION_Y = 6

PLATE_X = (PANEL_WIDTH - ROW_WIDTH) // 2
PLATE_Y = 26

ACTIVE_X = MARGIN
ACTIVE_Y = TITLEBAR_HEIGHT + 2
ACTIVE_HEIGHT = 93

REMAIN_X = 20
REMAIN_Y = PLATE_Y + ROW_HEIGHT + 7

UNEQUIP_WIDTH = 62
UNEQUIP_HEIGHT = 20
UNEQUIP_X = PANEL_WIDTH - UNEQUIP_WIDTH - 12
UNEQUIP_Y = PLATE_Y + ROW_HEIGHT + 5

LIST_X = MARGIN
LIST_Y = ACTIVE_Y + ACTIVE_HEIGHT + 6

LIST_AREA_X = 6
LIST_AREA_Y = 24
LIST_AREA_HEIGHT = ROW_HEIGHT * VISIBLE_ROWS

LIST_HEIGHT = LIST_AREA_Y + LIST_AREA_HEIGHT + 6

BOARD_HEIGHT = LIST_Y + LIST_HEIGHT + MARGIN

# The panels force ("ltr",) because every row widget below is built in code and
# code-created children are never mirrored by the engine - one shared layout for
# both locales, with the Arabic anchoring done per label in uititle.py.
window = {
	"name" : "TitleWindow",

	"x" : 0,
	"y" : 0,

	"style" : ("movable", "float", "ltr",),

	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,

	"children" :
	(
		{
			"name" : "Board",
			"type" : "board_with_titlebar",
			"style" : ("attach", "ltr",),

			"x" : 0,
			"y" : 0,

			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,

			"title" : "",

			"children" :
			(
				{
					"name" : "ActivePanel",
					"type" : "v2_thinboard",
					"style" : ("attach", "ltr",),

					"x" : ACTIVE_X,
					"y" : ACTIVE_Y,

					"width" : PANEL_WIDTH,
					"height" : ACTIVE_HEIGHT,

					"children" :
					(
						{
							"name" : "ActiveCaption",
							"type" : "text",

							"x" : CAPTION_X,
							"y" : CAPTION_Y,

							"text" : "",
						},
						{
							"name" : "ActivePlate",
							"type" : "image",

							"x" : PLATE_X,
							"y" : PLATE_Y,

							"image" : ROW_IMAGE,
						},
						{
							"name" : "ActiveValue",
							"type" : "text",

							"x" : PLATE_X + ROW_WIDTH // 2,
							"y" : PLATE_Y + ROW_HEIGHT // 2,

							"text" : "",
						},
						{
							"name" : "ActiveRemain",
							"type" : "text",

							"x" : REMAIN_X,
							"y" : REMAIN_Y,

							"text" : "",
						},
						{
							"name" : "UnequipButton",
							"type" : "button",

							"x" : UNEQUIP_X,
							"y" : UNEQUIP_Y,

							"default_image" : "d:/ymir work/ui/public/small_thin_button_01.sub",
							"over_image" : "d:/ymir work/ui/public/small_thin_button_02.sub",
							"down_image" : "d:/ymir work/ui/public/small_thin_button_03.sub",
						},
					),
				},
				{
					"name" : "ListPanel",
					"type" : "v2_thinboard",
					"style" : ("attach", "ltr",),

					"x" : LIST_X,
					"y" : LIST_Y,

					"width" : PANEL_WIDTH,
					"height" : LIST_HEIGHT,

					"children" :
					(
						{
							"name" : "ListCaption",
							"type" : "text",

							"x" : CAPTION_X,
							"y" : CAPTION_Y,

							"text" : "",
						},
						{
							"name" : "ListArea",
							"type" : "window",

							"x" : LIST_AREA_X,
							"y" : LIST_AREA_Y,

							"width" : ROW_WIDTH,
							"height" : LIST_AREA_HEIGHT,
						},
					),
				},
			),
		},
	),
}
