import localeinfo

PATTERN_PATH = "d:/ymir work/ui/pattern/"
PATH = "d:/ymir work/ui/game/notification/"

# Window dimensions - wider and taller
WINDOW_WIDTH = 420
WINDOW_HEIGHT = 310  # Title bar (~30) + header bar (~25) + 4 items (45 each) + bottom padding + clear button

# Header bar area (for column labels)
HEADER_HEIGHT = 25
HEADER_Y = 32

# List area (below header)
LIST_WIDTH = 390
LIST_HEIGHT = 180  # 4 items * 45 = 180
LIST_Y = HEADER_Y + HEADER_HEIGHT

# Scrollbar
SCROLLBAR_HEIGHT = LIST_HEIGHT

window = {
	"name": "NotificationHistoryWindow",
	"style": ("movable", "float",),
	"x": 0,
	"y": 0,
	"width": WINDOW_WIDTH,
	"height": WINDOW_HEIGHT,
	"children": (
		# Main board with title bar
		{
			"name": "board",
			"type": "board_with_titlebar",
			"x": 0,
			"y": 0,
			"width": WINDOW_WIDTH,
			"height": WINDOW_HEIGHT,
			"title": localeinfo.NOTIFICATION_HISTORY_TITLE if hasattr(localeinfo, "NOTIFICATION_HISTORY_TITLE") else "Notifications History",
		},

		# Header bar background
		{
			"name": "header_bg",
			"type": "window",
			"x": 10,
			"y": HEADER_Y + 10,
			"width": LIST_WIDTH,
			"height": HEADER_HEIGHT,
		},

		# List container (below header)
		{
			"name": "list_container",
			"type": "window",
			"x": 10,
			"y": LIST_Y + 25,
			"width": LIST_WIDTH,
			"height": LIST_HEIGHT,
		},

		# Clear History button
		{
			"name": "btn_clear",
			"type": "button",
			"x": 162,
			"y": 268,
			"default_image": "d:/ymir work/ui/public/large_button_01.sub",
			"over_image": "d:/ymir work/ui/public/large_button_02.sub",
			"down_image": "d:/ymir work/ui/public/large_button_03.sub",
			"text": localeinfo.NOTIFICATION_HISTORY_CLEAR if hasattr(localeinfo, "NOTIFICATION_HISTORY_CLEAR") else "Clear History",
		},

		# Empty message (shown when no history)
		{
			"name": "empty_text",
			"type": "text",
			"x": - 50,
			"y": LIST_Y + 70,
			"text": localeinfo.NOTIFICATION_HISTORY_EMPTY if hasattr(localeinfo, "NOTIFICATION_HISTORY_EMPTY") else "No recent notifications.",
			"horizontal_align": "center",
			"r": 0.6,
			"g": 0.6,
			"b": 0.6,
		},
	),
}
