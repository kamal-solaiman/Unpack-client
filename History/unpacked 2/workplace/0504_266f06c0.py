import localeinfo
import app

# Define paths and sizes
PATTERN_PATH = "d:/ymir work/ui/pattern/"
PUBLIC_PATH = "d:/ymir work/ui/public/"

# --- Main Window Dimensions ---
WINDOW_WIDTH = 270 + 140
WINDOW_HEIGHT = 130

# --- Content Area (board_window) Dimensions ---
BOARD_WINDOW_WIDTH = 250 + 140
BOARD_WINDOW_HEIGHT = WINDOW_HEIGHT - 40 # Adjusted for content

# --- Pattern Calculations for the Content Area ---
PATTERN_X_COUNT = (BOARD_WINDOW_WIDTH - 32) / 16
PATTERN_Y_COUNT = (BOARD_WINDOW_HEIGHT - 32) / 16

window = {
	"name" : "AutoShoutWindow",
	"style" : ("movable", "float",),
	"x" : SCREEN_WIDTH / 2 - WINDOW_WIDTH / 2,
	"y" : SCREEN_HEIGHT / 2 - WINDOW_HEIGHT / 2,
	"width" : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,
	"children" :
	(
		## The Title Bar and outer frame
		{
			"name" : "board",
			"type" : "board_with_titlebar",
			"x" : 0, "y" : 0,
			"width" : WINDOW_WIDTH, "height" : WINDOW_HEIGHT,
			"title" : localeinfo.AUTOSHOUT_TITLE_TOOLTIP,
		},

		{
			"name" : "board_window",
			"type" : "window",
			"style" : ("attach", "ltr",),
			"x" : 10, "y" : 32,
			"width" : BOARD_WINDOW_WIDTH, "height" : BOARD_WINDOW_HEIGHT,
			"children" :
			(
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

				{ 
					"name" : "last_shout_text",
					"type" : "text",
					"x" : 190, "y" : 20,
					"text" : localeinfo.AUTOSHOUT_NO_MESSAGE, 
					"text_horizontal_align" : "center",
					"text_vertical_align" : "center",
				},
				{
					"name" : "enable_button",
					"type" : "toggle_button",
					"x" : 145, "y" : 47+10,
					"default_image" : PUBLIC_PATH + "large_button_01.sub",
					"over_image" : PUBLIC_PATH + "large_button_02.sub",
					"down_image" : PUBLIC_PATH + "large_button_03.sub",
					"text" : localeinfo.AUTOSHOUT_ENABLE,
				},
			),
		},
		
			
		## ToolTip Button
		{
			"name" : "ToolTipButton",
			"type" : "button",

			"x" : 25, "y" : WINDOW_HEIGHT - 8,
			"vertical_align" : "bottom",

			"default_image" : "d:/ymir work/ui/pattern/q_mark_01.tga",
			"over_image" : "d:/ymir work/ui/pattern/q_mark_02.tga",
			"down_image" : "d:/ymir work/ui/pattern/q_mark_01.tga",
		},
		
	),
}