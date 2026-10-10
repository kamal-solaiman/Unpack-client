# Grid geometry has to match what the engine actually draws: an item icon is 32 px per
# proto slot tall, so a 2- or 3-slot item owns that many cells. GAP is the air between
# cells. uiquicksell.py derives its column count from Viewport's width - keep them in step.
CELL = 32
GAP = 4
PITCH = CELL + GAP

COLS = 6
VISIBLE_ROWS = 5

GRID_WIDTH = COLS * PITCH - GAP
GRID_HEIGHT = VISIBLE_ROWS * PITCH - GAP

VIEWPORT_X = 16
VIEWPORT_Y = 42

SCROLL_X = VIEWPORT_X + GRID_WIDTH + 6
SCROLL_WIDTH = 15

PANEL_X = 10
PANEL_Y = 36
PANEL_WIDTH = SCROLL_X + SCROLL_WIDTH + 7 - PANEL_X
PANEL_HEIGHT = GRID_HEIGHT + 12

BOARD_WIDTH = PANEL_X * 2 + PANEL_WIDTH
BOARD_HEIGHT = 336

LABEL_X = 16
LABEL_COLOR = 0xffd0c2b7
TOTAL_COLOR = 0xffffc800
HINT_COLOR = 0xff9a8f85

HINT_Y = PANEL_Y + PANEL_HEIGHT + 8
COUNT_Y = HINT_Y + 22
TOTAL_Y = COUNT_Y + 22

MONEY_ICON = "d:/ymir work/ui/game/windows/money_icon.sub"

BTN_PATH = "d:/ymir work/ui/public/"
BTN_WIDTH = 61
BTN_HEIGHT = 21
BTN_Y = TOTAL_Y + 28
BTN_LEFT_X = (BOARD_WIDTH - (BTN_WIDTH * 2 + 10)) / 2
BTN_RIGHT_X = BTN_LEFT_X + BTN_WIDTH + 10

window = {
	"name" : "QuickSellConfirmWindow",
	"style" : ("movable", "float", "ltr",),

	"x" : 0,
	"y" : 0,

	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,

	"children" :
	(
		{
			"name" : "board",
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
					"name" : "GridPanel",
					"type" : "v2_thinboard",
					"style" : ("attach", "ltr",),

					"x" : PANEL_X,
					"y" : PANEL_Y,

					"width" : PANEL_WIDTH,
					"height" : PANEL_HEIGHT,
				},
				{
					"name" : "Viewport",
					"type" : "window",
					"style" : ("ltr",),

					"x" : VIEWPORT_X,
					"y" : VIEWPORT_Y,

					"width" : GRID_WIDTH,
					"height" : GRID_HEIGHT,
				},
				{
					"name" : "ScrollBarSlot",
					"type" : "window",
					"style" : ("ltr",),

					"x" : SCROLL_X,
					"y" : VIEWPORT_Y,

					"width" : SCROLL_WIDTH,
					"height" : GRID_HEIGHT,
				},
				{
					"name" : "HintLabel",
					"type" : "text",

					"x" : LABEL_X,
					"y" : HINT_Y,

					"text_horizontal_align" : "left",
					"text" : "",
					"outline" : 1,
					"color" : HINT_COLOR,
				},
				{
					"name" : "CountLabel",
					"type" : "text",

					"x" : LABEL_X,
					"y" : COUNT_Y,

					"text_horizontal_align" : "left",
					"text" : "",
					"outline" : 1,
					"color" : LABEL_COLOR,
				},
				{
					"name" : "TotalLabel",
					"type" : "text",

					"x" : LABEL_X,
					"y" : TOTAL_Y,

					"text_horizontal_align" : "left",
					"text" : "",
					"outline" : 1,
					"color" : TOTAL_COLOR,
				},
				{
					"name" : "MoneyIcon",
					"type" : "image",
					"style" : ("ltr",),

					"x" : LABEL_X,
					"y" : TOTAL_Y + 1,

					"image" : MONEY_ICON,
				},
				{
					"name" : "AcceptButton",
					"type" : "button",
					"style" : ("ltr",),

					"x" : BTN_LEFT_X,
					"y" : BTN_Y,

					"width" : BTN_WIDTH,
					"height" : BTN_HEIGHT,

					"default_image" : BTN_PATH + "acceptbutton00.sub",
					"over_image" : BTN_PATH + "acceptbutton01.sub",
					"down_image" : BTN_PATH + "acceptbutton02.sub",
				},
				{
					"name" : "CancelButton",
					"type" : "button",
					"style" : ("ltr",),

					"x" : BTN_RIGHT_X,
					"y" : BTN_Y,

					"width" : BTN_WIDTH,
					"height" : BTN_HEIGHT,

					"default_image" : BTN_PATH + "canclebutton00.sub",
					"over_image" : BTN_PATH + "canclebutton01.sub",
					"down_image" : BTN_PATH + "canclebutton02.sub",
				},
			),
		},
	),
}
