# coding: latin_1

import localeinfo

WINDOW_WIDTH = 636
WINDOW_HEIGHT = 408

IMG_DIR = "d:/ymir work/ui/game/track/ymirdesign/"

window = {
	"name" : "Track_Window",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float","ltr",),
	"width" : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,
	"children" :
	(
		{
			"name" : "board",
			"type" : "board",
			"style" : ("movable", "attach", "float","ltr",),
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
					"width" : WINDOW_WIDTH - 15,
					"color" : "yellow",
					"children" :
					(
						{
							"name" : "TitleName",
							"type" : "text",
							"x" : (WINDOW_WIDTH - 15) / 2,
							"y" : 3,
							"text" : localeinfo.TRACK_WINDOW_TITLE,
							"text_horizontal_align" : "center"
						},
					),
				},
				{
					"name" : "bg",
					"type" : "image",
					"style" : ("movable","attach", "float","ltr",),
					"x" : 10,
					"y" : 36,
					"image" : IMG_DIR + "bg_new.png",
				},
				{
					"name" : "worldboss_info",
					"type" : "button",
					"style" : ("ltr",),
					"x" : WINDOW_WIDTH - 171,
					"y" : 55,
					"default_image" : IMG_DIR + "info_bg.tga",
					"over_image" : IMG_DIR + "info_bg.tga",
					"down_image" : IMG_DIR + "info_bg.tga",
					"text" : "",
				},
				{
					"name" : "open_shop",
					"type" : "button",
					"style" : ("ltr",),
					"x" : WINDOW_WIDTH - 171,
					"y" : 100,
					"default_image" : IMG_DIR + "open_shop_0.tga",
					"over_image" : IMG_DIR + "open_shop_1.tga",
					"down_image" : IMG_DIR + "open_shop_2.tga",
					"text" : localeinfo.TRACK_OPEN_SHOP,
				},
				{
					"name" : "wiki_button",
					"type" : "button",
					"x" : WINDOW_WIDTH - 171 + 20,
					"y" : 180,
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
							"text": localeinfo.TRACK_DROP_FIRST,
						},
					),
				},
				{
					"name" : "wiki_button2",
					"type" : "button",
					"x" : WINDOW_WIDTH - 171 + 20,
					"y" : 230,
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
							"text": localeinfo.TRACK_DROP_SECOND,
						},
					),
				},
				{
					"name" : "wiki_button3",
					"type" : "button",
					"x" : WINDOW_WIDTH - 171 + 20,
					"y" : 275,
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
							"text": localeinfo.TRACK_DROP_THIRD,
						},
					),
				},
				{
					"name" : "wiki_button4",
					"type" : "button",
					"x" : WINDOW_WIDTH - 171 + 20,
					"y" : 320,
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
							"text": localeinfo.TRACK_DROP_FOURTH,
						},
					),
				},
				# {
					# "name" : "worldboss_info_notice",
					# "type" : "toggle_button",
					# "style" : ("ltr",),
					# "x" : WINDOW_WIDTH - 171,
					# "y" : WINDOW_HEIGHT - 42,
					# "default_image" : IMG_DIR + "checkbox.tga",
					# "over_image" : IMG_DIR + "checkbox.tga",
					# "down_image" : IMG_DIR + "checked.tga",
					# "children":
					# (
						# {
							# "name" : "dungeon_info_notice_text",
							# "type" : "multi_text2",
							# "x" : 50,
							# "y" : -5,
							# "text" : localeinfo.TRACK_BOSS_NOTICE_INFORMATION,
							# "text_type" : "horizontal#right",
							# "text_range" : 11,
						# },
					# ),
				# },
				{
					"name" : "listbox",
					"type" : "listbox_new2",
					"style" : ("ltr",),
					"x" : 18,
					"y" : 50,
					"width" : 405,
					"height" : 342,
				},
			),
		},
	),
}
