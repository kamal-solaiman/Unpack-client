# coding: latin_1

import localeinfo

WINDOW_WIDTH = 405
WINDOW_HEIGHT = 114

IMG_DIR_AVATAR = "d:/ymir work/ui/game/track/avatar/"
IMG_DIR = "d:/ymir work/ui/game/track/ymirdesign/"

window = {
	"name" : "TrackWindow",
	"x" : 0,
	"y" : 0,
	"width" : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,
	"children" :
	(
		{
			"name" : "board",
			"type" : "expanded_image",
			"x" : 0,
			"y" : 0,
			"image" : IMG_DIR + "dungeon_closed.tga",
			"children" :
			(
				{
					"name" : "avatar",
					"type" : "expanded_image",
					"x" : 5,
					"y" : 5,
					"image":IMG_DIR_AVATAR + "4901.tga",
				},
				{
					"name" : "name_field",
					"type" : "text",
					"x" : 123,
					"y" : 19,
					"text" : "",
					"color" : 0xFFFFAF00,
				},
				{
					"name" : "group_field",
					"type" : "text",
					"x" : 123,
					"y" : 19 + (2*18),
					"text" : "",
				},
				{
					"name" : "cooldown_field",
					"type" : "text",
					"x" : 123,
					"y" : 19 + (3*18),
					"text" : "",
				},
				{
					"name" : "status_field",
					"type" : "text",
					"x" : 123,
					"y" : 19 + (4*18),
					"text" : "",
				},
				{
					"name" : "teleport_button",
					"type" : "button",
					"x" : WINDOW_WIDTH - 114,
					"y" : WINDOW_HEIGHT - 35,
					"default_image" : "d:/ymir work/ui/settings/btn_cat_2.png",
					"over_image" : "d:/ymir work/ui/settings/btn_cat_4.png",
					"down_image" : "d:/ymir work/ui/settings/btn_cat_1.png",
					"children" :
					(
						{
							"name" : "teleport_button_text",
							"type" : "text",
							"x" : 0,
							"y" : 0,
							"all_align" : 1,
							"text": localeinfo.TRACK_TELEPORT,
						},
					),
				},
			),
		},
	),
}
