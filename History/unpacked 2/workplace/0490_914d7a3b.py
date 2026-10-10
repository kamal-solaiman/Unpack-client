# coding: latin_1
#
# Daily Alchemy Ore "Help" popup layout (the ore-system explainer).
#
# Only the board chrome lives here. The five icon rows themselves are built in code
# (uialchemyorehelp.py) out of a ui.Table grid -- tables are inherently code-built
# (same as the in-game wiki / the buffi Companion help) and use the shared project
# table colour scheme. The board is resized to the generated content height at runtime.
WINDOW_WIDTH  = 300
WINDOW_HEIGHT = 320
window = {
	"name"   : "AlchemyOreHelpWindow",
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
