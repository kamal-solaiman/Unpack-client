import localeinfo


PATTERN_PATH = "d:/ymir work/ui/pattern/"
PUBLIC_PATH = "d:/ymir work/ui/public/"
PATH = "d:/ymir work/ui/game/notification/"


POPUP_WIDTH = 265
POPUP_HEIGHT = 85


BOARD_WINDOW_WIDTH = POPUP_WIDTH # 20
BOARD_WINDOW_HEIGHT = POPUP_HEIGHT # 40


PATTERN_X_COUNT = (BOARD_WINDOW_WIDTH - 32) / 16
PATTERN_Y_COUNT = (BOARD_WINDOW_HEIGHT - 32) / 16


ICON_SIZE = 32
ICON_X = 207
ICON_Y = 26


TEXT_X = ICON_X - ICON_SIZE + 5
TEXT_X_CENTERED = ICON_X - ICON_SIZE - 150
TEXT_Y_TITLE = 12 + 8
TEXT_Y_MESSAGE = 35 + 8


COUNT_TEXT_X = ICON_X - ICON_SIZE + 5
COUNT_TEXT_Y = ICON_Y + ICON_SIZE - 10

window = {
	"name": "NotificationPopup",
	"style" : ("movable", "float",),
	"x": 0,
	"y": 0,
	"width": POPUP_WIDTH,
	"height": POPUP_HEIGHT,
	"children": (
		## The Title Bar and outer frame
		{
			"name": "board",
			"type" : "invisibleboard",
			"x": 0,
			"y": 0,
			"width": POPUP_WIDTH,
			"height": POPUP_HEIGHT,
			"title" : localeinfo.NOTIFICATION_SYSTEM_TITLE,
		},

		## Inner content area with pattern borders
		{
			"name": "board_window",
			"type": "window",
			"style" : ("attach", "ltr",),
			"x": 0,
			"y": 0,
			"width": BOARD_WINDOW_WIDTH,
			"height": BOARD_WINDOW_HEIGHT,
			"children": (
				## --- Border Images ---
				{ "name" : "LeftTop", "type" : "image", "style" : ("ltr",), "x" : 0, "y" : 0, "image" : PATTERN_PATH + "border_A_left_top.tga", },
				{ "name" : "RightTop", "type" : "image", "style" : ("ltr",), "x" : BOARD_WINDOW_WIDTH - 16, "y" : 0, "image" : PATTERN_PATH + "border_A_right_top.tga", },
				{ "name" : "LeftBottom", "type" : "image", "style" : ("ltr",), "x" : 0, "y" : BOARD_WINDOW_HEIGHT - 16, "image" : PATTERN_PATH + "border_A_left_bottom.tga", },
				{ "name" : "RightBottom", "type" : "image", "style" : ("ltr",), "x" : BOARD_WINDOW_WIDTH - 16, "y" : BOARD_WINDOW_HEIGHT - 16, "image" : PATTERN_PATH + "border_A_right_bottom.tga", },
				{ "name" : "TopCenterImg", "type" : "expanded_image", "style" : ("ltr",), "x" : 16, "y" : 0, "image" : PATTERN_PATH + "border_A_top.tga", "rect" : (0.0, 0.0, PATTERN_X_COUNT, 0), },
				{ "name" : "LeftCenterImg", "type" : "expanded_image", "style" : ("ltr",), "x" : 0, "y" : 16, "image" : PATTERN_PATH + "border_A_left.tga", "rect" : (0.0, 0.0, 0, PATTERN_Y_COUNT), },
				{ "name" : "RightCenterImg", "type" : "expanded_image", "style" : ("ltr",), "x" : BOARD_WINDOW_WIDTH - 16, "y" : 16, "image" : PATTERN_PATH + "border_A_right.tga", "rect" : (0.0, 0.0, 0, PATTERN_Y_COUNT), },
				{ "name" : "BottomCenterImg", "type" : "expanded_image", "style" : ("ltr",), "x" : 16, "y" : BOARD_WINDOW_HEIGHT - 16, "image" : PATTERN_PATH + "border_A_bottom.tga", "rect" : (0.0, 0.0, PATTERN_X_COUNT, 0), },
				{ "name" : "CenterImg", "type" : "expanded_image", "style" : ("ltr",), "x" : 16, "y" : 16, "image" : PATTERN_PATH + "border_A_center.tga", "rect" : (0.0, 0.0, PATTERN_X_COUNT, PATTERN_Y_COUNT), },

				## --- Content Elements ---
				{
					"name": "notification_bg",
					"type": "expanded_image",
					"x": 186,
					"y": 5,
					"image": PATH + "quest_any_frame.png",
				},
				{
					"name": "item_icon",
					"type": "image",
					"x": ICON_X,
					"y": ICON_Y,
					"image": "d:/ymir work/ui/game/notification/monthly.png",
				},
				{
					"name": "title_text",
					"type": "text",
					"x": TEXT_X_CENTERED,
					"y": TEXT_Y_TITLE,
					"horizontal_align": "center",
					"text": "",
					"fontname" : "Tahoma:16",
					"r": 1.0,
					"g": 0.84,
					"b": 0.0,
				},
				{
					"name": "message_text",
					"type": "text",
					"x": TEXT_X,
					"y": TEXT_Y_MESSAGE,
					"text": "",
					"r": 0.9,
					"g": 0.9,
					"b": 0.9,
				},
				{
					"name": "count_text",
					"type": "text",
					"x": COUNT_TEXT_X,
					"y": COUNT_TEXT_Y,
					"horizontal_align": "right",
					"text": "",
					"r": 1.0,
					"g": 1.0,
					"b": 1.0,
					"outline": 1,
				},
			),
		},
	),
}
