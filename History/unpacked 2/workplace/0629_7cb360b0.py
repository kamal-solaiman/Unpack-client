import grp
import localeinfo

BOARD_X = 600
BOARD_Y = 300
COLOR_LINE = 0xff5b5e5e
ROOT_PATH = "d:/ymir work/ui/public/"

window = {
	"name" : "WhisperManager",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
	"width" : BOARD_X-200,
	"height" : BOARD_Y-10,
	"children" :
	(
		{
			"name" : "board",
			"type" : "board",
			"x" : 0,
			"y" : 0,
			"width" : BOARD_X-200,
			"height" : BOARD_Y-10,
			"children" :
			(
				{
					"name" : "titlebar",
					"type" : "titlebar",
					"style" : ("attach",),

					"x" : 8,
					"y" : 8,

					"width" : BOARD_X - 213,
					"color" : "gray",

					"children" :
					(
						{
							"name" : "TitleName",
							"type" : "text",
							"x" : 0,
							"y" : 3,
							"horizontal_align" : "center",
							"text" : localeinfo.HWID_WINDOW_TITLE,
							"text_horizontal_align":"center"
						},
					),
				},

## LINES
				{ "name" : "LINE_BGCREATE_LEFT", "type" : "line", "x" : 8, "y" : 30, "width" : 0, "height" : BOARD_Y-50, "color" : COLOR_LINE, },
				{ "name" : "LINE_BGCREATE_RIGHT", "type" : "line", "x" : BOARD_X-210, "y" : 30, "width" : 0, "height" : BOARD_Y-50, "color" : COLOR_LINE, },
				{ "name" : "LINE_BGCREATE_DOWN", "type" : "line", "x" : 8, "y" : BOARD_Y-20, "width" : BOARD_X-217, "height" : 0, "color" : COLOR_LINE, },
				{ "name" : "LINE_BGCREATE_UP", "type" : "line", "x" : 8, "y" : 30, "width" : BOARD_X-217, "height" : 0, "color" : COLOR_LINE, },		
				# { "name" : "LINE_FLAG_DOWN", "type" : "line", "x" : 8, "y" : 49, "width" : BOARD_X-217, "height" : 0, "color" : COLOR_LINE, },	
				{ "name" : "LINE_BAR_END", "type" : "line", "x" : 9, "y" : 149+100, "width" : BOARD_X-219, "height" : 0, "color" : COLOR_LINE, },	

## PLAYER FELD
				{
					"name": "PlayerNameBG",
					"type":"sibbar",
					"x": 9,
					"y": 32,
					"height": 30,
					"width": BOARD_X-219,
					"children" :
					(
						{
							"name":"NameTitleText",
							"type":"text",
							"x": 5,
							"y": 3,
							"text": localeinfo.HWID_PLAYER_NAME,
							"color" : 0xffc3b168,
						},
						{
							"name": "input_image",
							"type":"expanded_image",
							"x": 45,
							"y": -2,
							"height": 30,
							"width": BOARD_X-219,
							"image" : "d:/ymir work/ui/public/public_intro/name_bg.tga",
						},

						{
							"name" : "playerName_Value",
							"type" : "editline",
							"x" : 193-45-40,
							"y" : 3,
							"width" : 105,
							"height" : 18,
							"input_limit" : 24,
						},
					),
				},

## Mode Berreich
				{
					"name": "ModeBG",
					"type":"sibboard",
					"x": 9,
					"y": 56,
					"width": BOARD_X-219,
					"height": 70,
					"children" :
					(
						{
							"name" : "hwid_unban",
							"type" : "radio_button",

							"x" : 3,
							"y" : 40,

							"text" : localeinfo.HWID_BTN_UNBAN,
							"tooltip_text" : localeinfo.HWID_BTN_UNBAN_TOOLTIP,

							"default_image" : "d:/ymir work/ui/public/public_intro/button_1.tga",
							"over_image" : "d:/ymir work/ui/public/public_intro/button_3.tga",
							"down_image" : "d:/ymir work/ui/public/public_intro/button_2.tga",
						},
						{
							"name" : "hwid_ban",
							"type" : "radio_button",

							"x" : 3,
							"y" : 10,

							"text" : localeinfo.HWID_BTN_BAN,
							"tooltip_text" : localeinfo.HWID_BTN_BAN_TOOLTIP,

							"default_image" : "d:/ymir work/ui/public/public_intro/button_1.tga",
							"over_image" : "d:/ymir work/ui/public/public_intro/button_3.tga",
							"down_image" : "d:/ymir work/ui/public/public_intro/button_2.tga",
						},
						{
							"name" : "hwid_hwidban",
							"type" : "radio_button",

							"x" : 129,
							"y" : 10,

							"text" : localeinfo.HWID_BTN_HWID_BAN,
							"tooltip_text" : localeinfo.HWID_BTN_HWID_BAN_TOOLTIP,

							"default_image" : "d:/ymir work/ui/public/public_intro/button_1.tga",
							"over_image" : "d:/ymir work/ui/public/public_intro/button_3.tga",
							"down_image" : "d:/ymir work/ui/public/public_intro/button_2.tga",
						},
						{
							"name" : "hwid_deletehwidban",
							"type" : "radio_button",

							"x" : 129,
							"y" : 40,

							"text" : localeinfo.HWID_BTN_DELETE_HWID_BAN,
							"tooltip_text" : localeinfo.HWID_BTN_DELETE_HWID_BAN_TOOLTIP,

							"default_image" : "d:/ymir work/ui/public/public_intro/button_1.tga",
							"over_image" : "d:/ymir work/ui/public/public_intro/button_3.tga",
							"down_image" : "d:/ymir work/ui/public/public_intro/button_2.tga",
						},
						{
							"name" : "hwid_totalhwidban",
							"type" : "radio_button",

							"x" : 255,
							"y" : 10,

							"text" : localeinfo.HWID_BTN_TOTAL_HWID_BAN,
							"tooltip_text" : localeinfo.HWID_BTN_TOTAL_HWID_BAN_TOOLTIP,

							"default_image" : "d:/ymir work/ui/public/public_intro/button_1.tga",
							"over_image" : "d:/ymir work/ui/public/public_intro/button_3.tga",
							"down_image" : "d:/ymir work/ui/public/public_intro/button_2.tga",
						},
						{
							"name" : "hwid_chatban",
							"type" : "radio_button",

							"x" : 255,
							"y" : 40,

							"text" : localeinfo.HWID_BTN_CHAT_BAN,
							"tooltip_text" : localeinfo.HWID_BTN_CHAT_BAN_TOOLTIP,

							"default_image" : "d:/ymir work/ui/public/public_intro/button_1.tga",
							"over_image" : "d:/ymir work/ui/public/public_intro/button_3.tga",
							"down_image" : "d:/ymir work/ui/public/public_intro/button_2.tga",
						},
					),
				},

##UNTERES_FELD
				{
					"name": "horizontalbar",
					"type":"sibbar",
					"x": 9,
					"y": 130, #232
					"width": BOARD_X-219,
					"children" :
					(
						{
							"name":"ReasonText",
							"type":"text",
							"x": 5,
							"y": 3,
							"text": "",
							"color" : 0xffc3b168,
						},
						{
							"name":"textLine1",
							"type":"text",
							"x": 178,
							"y": 3,
							"text": "",
							"color" : 0xffc3b168,
						},
						{
							"name":"textLine2",
							"type":"text",
							"x": 342,
							"y": 3,
							"text": "",
							"color" : 0xffc3b168,
						},
					),
				},

## Grund 
				{
					"name" : "ReasonBG",
					"type" : "bar",
					"x" : 9,
					"y" : 151,
					"width" : BOARD_X-226+6,
					"height" : 96,
				},

				{
					"name" : "currentLine_Value",
					"type" : "editline",
					"x" : 14,
					"y" : 152,
					"width" : BOARD_X-226,
					"height" : 96,
					"input_limit" : 512,
					"multi_line" : 1,
					"limit_width" : BOARD_X-226,
				},

## Final Buttons
				{
					"name" : "accept_button",
					"type" : "button",
					"x" : 13,
					"y" : 255,
					"text" : localeinfo.HWID_SEND_BUTTON,
					"default_image" : "d:/ymir work/ui/public/public_intro/button_1.tga",
					"over_image" : "d:/ymir work/ui/public/public_intro/button_3.tga",
					"down_image" : "d:/ymir work/ui/public/public_intro/button_2.tga",
				},

				{
					"name" : "clear_button",
					"type" : "button",
					"x" : 139,
					"y" : 255,
					"text" : localeinfo.HWID_CLEAR_BUTTON,
					"default_image" : "d:/ymir work/ui/public/public_intro/button_1.tga",
					"over_image" : "d:/ymir work/ui/public/public_intro/button_3.tga",
					"down_image" : "d:/ymir work/ui/public/public_intro/button_2.tga",
				},
				
				{
					"name" : "cancel_button",
					"type" : "button",
					"x" : 265,
					"y" : 255,
					"text" : localeinfo.HWID_CANCEL_BUTTON,
					"default_image" : "d:/ymir work/ui/public/public_intro/button_1.tga",
					"over_image" : "d:/ymir work/ui/public/public_intro/button_3.tga",
					"down_image" : "d:/ymir work/ui/public/public_intro/button_2.tga",
				},
			),
		},
	),
}
