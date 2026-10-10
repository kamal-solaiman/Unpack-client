# coding: latin_1
#
# Pet "Upgrade Help" popup layout (growth pet rework).
#
# Only the board chrome lives here. The explanation itself is built in code
# (uipetupgradehelp.py) out of ui.Table grids -- tables are inherently code-built
# (same as the in-game wiki / buffi help) and use the shared project table colour
# scheme. The board is resized to the generated content height at runtime.
WINDOW_WIDTH  = 360
WINDOW_HEIGHT = 500
window = {
	"name"   : "PetUpgradeHelpWindow",
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
