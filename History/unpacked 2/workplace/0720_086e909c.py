# coding: latin_1
import uiscriptlocale

def _loc(key, default):
	return getattr(uiscriptlocale, key, default)

WINDOW_WIDTH = 556
WINDOW_HEIGHT = 312

window = {
	"name" : "party_finder_window",
	"style" : ("movable", "float",),
	"x" : SCREEN_WIDTH / 2 - WINDOW_WIDTH / 2,
	"y" : SCREEN_HEIGHT / 2 - WINDOW_HEIGHT / 2,
	"width" : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,
	"children" :
	(
		{
			"name" : "board",
			"type" : "board_with_titlebar",
			"x" : 0, "y" : 0,
			"width" : WINDOW_WIDTH, "height" : WINDOW_HEIGHT,
			"title" : _loc("PF_TITLE", "Party Finder"),
		},
	),
}
