# coding: latin_1

ROOT_PATH = "d:/ymir work/ui/game/fishing/"

TRACK_WIDTH = 540
TRACK_HEIGHT = 26

TRACK_X = 10
TRACK_Y = 64

WINDOW_WIDTH = TRACK_WIDTH + 20
WINDOW_HEIGHT = 122

window = {
	"name" : "FishingBdoWindow",
	"style" : ("float", "ltr", ),

	"x" : 0,
	"y" : 0,

	"width" : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,

	"children" :
	(
		{
			"name" : "round_text",
			"type" : "text",
			"style" : ("not_pick", "ltr", ),
			"x" : TRACK_X + 2,
			"y" : TRACK_Y - 18,
			"text" : "",
			"outline" : 1,
		},

		{
			"name" : "hits_text",
			"type" : "text",
			"style" : ("not_pick", "ltr", ),
			"x" : TRACK_X + TRACK_WIDTH - 2,
			"y" : TRACK_Y - 18,
			"text" : "",
			"text_horizontal_align" : "right",
			"outline" : 1,
		},

		{
			"name" : "status_text",
			"type" : "text",
			"style" : ("not_pick", "ltr", ),
			"x" : WINDOW_WIDTH / 2,
			"y" : TRACK_Y - 18,
			"text" : "",
			"text_horizontal_align" : "center",
			"outline" : 1,
		},

		{
			"name" : "track_bg",
			"type" : "image",
			"style" : ("not_pick", "ltr", ),
			"x" : TRACK_X,
			"y" : TRACK_Y,
			"image" : ROOT_PATH + "bg.png",
		},

		{
			"name" : "hint_text",
			"type" : "text",
			"style" : ("not_pick", "ltr", ),
			"x" : WINDOW_WIDTH / 2,
			"y" : TRACK_Y + TRACK_HEIGHT + 10,
			"text" : "",
			"text_horizontal_align" : "center",
			"outline" : 1,
		},
	),
}
