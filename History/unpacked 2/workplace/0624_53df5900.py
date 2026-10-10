# coding: latin_1

import localeinfo
MAIN_WIDTH = 500
MAIN_HEIGTH = 385

PATH = "guild_missions/"

window = {
	"name" : "MissionWindow",
	"style" : ("movable", "float","ltr",),
	"x" : 0,
	"y" : 0,

	"width" : MAIN_WIDTH,
	"height" : MAIN_HEIGTH,

	"children" :
	(
		{
			"name" : "board",
			"type" : "board",

			"x" : 0,
			"y" : 0,

			"width" : MAIN_WIDTH,
			"height" : MAIN_HEIGTH,

			"children" :
			(
				## Title
				{
					"name" : "titlebar",
					"type" : "titlebar",
					"style" : ("attach",),

					"x" : 8,
					"y" : 8,

					"width" : MAIN_WIDTH - 15,
					"color" : "gray",

					"children" :
					(
						{ "name":"titlename", "type":"text", "x":0, "y":3, 
						"text" : localeinfo.GUILDMISSION_TITLE, 
						"horizontal_align":"center", "text_horizontal_align":"center" },
					),
				},

				{
					"name" : "bg",
					"type" : "image",
					"style" : ("ltr",),
					"x" : 15,
					"y" : 35,
					"image" : PATH + "kenarbg.tga",
				},

				{
					"name" : "ScrollBar",
					"type" : "scrollbarnew",
					"x" : 30,
					"y" : 40,
					"size" : 85*4 - 20,
					"horizontal_align" : "right",
				},

				{
					"name" : "ListBox",
					"type" : "listboxex",
					"x" : 20,
					"y" : 40,
					"width" : 444,
					"height" : 85*4,
				},
			),
		},
	),
}
