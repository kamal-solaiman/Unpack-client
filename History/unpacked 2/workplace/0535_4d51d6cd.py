# coding: latin_1
#
# Growth Mount contextual-help popup layout. Board chrome only -- the content is
# built in code (uicompanionridehelp.py) per mode and the board is resized to the
# generated height at runtime.
WINDOW_WIDTH  = 360
WINDOW_HEIGHT = 280
window = {
	"name"   : "CompanionRideHelpWindow",
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
