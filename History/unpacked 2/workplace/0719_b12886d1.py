# coding: latin_1
#
# Party Finder "Help" popup layout (the recruiting-board explainer).
#
# Only the board chrome lives here. The explanation itself is built in code
# (uipartyfinderhelp.py) out of ui.Table grids -- tables are inherently code-built
# (same as the in-game wiki) and use the shared project table colour scheme. The
# board is resized to the generated content height at runtime.
WINDOW_WIDTH  = 440
WINDOW_HEIGHT = 500
window = {
	"name"   : "PartyFinderHelpWindow",
	"x"      : 0,
	"y"      : 0,
	"style"  : ("movable", "float",),
	"width"  : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,
	"children" :
	(
		{
			"name"   : "board",
			"type"   : "board_with_titlebar",
			"x"      : 0,
			"y"      : 0,
			"width"  : WINDOW_WIDTH,
			"height" : WINDOW_HEIGHT,
			"title"  : "",
		},
	),
}
