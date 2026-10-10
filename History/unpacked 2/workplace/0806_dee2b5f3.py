# coding: latin_1

import uiscriptlocale
import localeinfo

IMG_DIR = "d:/ymir work/ui/game/whisper/"

# the ae RTL loader right-aligns every uiscript child (rendered left = 660 - x - width);
# per-locale x values pin each panel to the same absolute spot on both locales
if localeinfo.IsARABIC():
	CHAT_BG_X = 204
	SIDEBAR_BG_X = 15
	HEADER_BG_X = 206
	TARGET_NAME_X = 247
	INPUT_BAR_X = 213
else:
	CHAT_BG_X = 15
	SIDEBAR_BG_X = 459
	HEADER_BG_X = 17
	TARGET_NAME_X = 58
	INPUT_BAR_X = 23

window = {
	"name" : "WhisperChatWindow",

	"x" : (SCREEN_WIDTH - 660) / 2,
	"y" : (SCREEN_HEIGHT - 436) / 2,

	"style" : ("movable", "float",),

	"width" : 660,
	"height" : 436,

	"children" :
	(

		{
			"name" : "board",
			"type" : "board_with_titlebar",

			"x" : 0,
			"y" : 0,

			"width" : 660,
			"height" : 436,
			"title" : getattr(uiscriptlocale, "WHISPERCHAT_TITLE", "Messenger"),
		},

		{
			"name" : "chat_bg",
			"type" : "expanded_image",
			"x" : CHAT_BG_X,
			"y" : 33,
			"style" : ("not_pick",),
			"image" : IMG_DIR+"background_right.png",
		},

		{
			"name" : "sidebar_bg",
			"type" : "expanded_image",
			"x" : SIDEBAR_BG_X,
			"y" : 33,
			"style" : ("not_pick",),
			"image" : IMG_DIR+"background_left.png",
		},

		{
			"name" : "header_bg",
			"type" : "expanded_image",
			"x" : HEADER_BG_X,
			"y" : 36,
			#"style" : ("not_pick",),
			"image" : IMG_DIR+"header_right.png",
		},

		{
			"name" : "chat_target_name",
			"type" : "text",
			"x" : TARGET_NAME_X,
			"y" : 48,
			"text" : "",
		},

		{
			"name" : "input_bar",
			"type" : "expanded_image",
			"x" : INPUT_BAR_X,
			"y" : 359,
			"image" : IMG_DIR+"input_msg_bg.png",
			"children" : (
				{
					"name" : "send_btn",
					"type" : "button",
					"x" : 335,
					"y" : 12,
					"default_image" : IMG_DIR+"btn_send_norm.png",
					"over_image" : IMG_DIR+"btn_send_hover.png",
					"down_image" : IMG_DIR+"btn_send_select.png",
				},
			),
		},

	),
}
