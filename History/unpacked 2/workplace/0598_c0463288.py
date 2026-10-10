# coding: latin_1
#
# Guild Contracts ranking popup layout. Mirrors the companion window pattern:
# the OUTER window is the movable container and is wider than the panel by the
# tab rail, so the arrow buttons (children of the window, in the rail) fall
# inside the window pick rect and stay clickable. The board_with_titlebar is a
# panel-sized child; uicompanion-style, its titlebar drags the movable window.
# uiguild.py binds board/prevBtn/nextBtn and builds the dynamic content in code.
RANK = "d:/ymir work/ui/new_guild/ranking/"
RAIL_W = 31
PANEL_W = 337
PANEL_H = 315
WINDOW_WIDTH = RAIL_W + PANEL_W
WINDOW_HEIGHT = PANEL_H

window = {
	"name"   : "GuildRankingPopup",
	"x"      : 0,
	"y"      : 0,
	"style"  : ("movable", "float",),
	"width"  : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,
	"children" :
	(
		### PANEL: the whole ranking board; content is built + parented in code. ###
		{
			"name"   : "board",
			"type"   : "board_with_titlebar",
			"x"      : RAIL_W,
			"y"      : 0,
			"width"  : PANEL_W,
			"height" : PANEL_H,
			"title"  : "",
		},
		### TAB RAIL (left column; RTL mirrors it to the right edge). The two arrow
		### buttons cycle the ranking type. Wired in uiguild.__Build. ###
		{
			"name" : "prevBtn",
			"type" : "button",
			"x" : 0,
			"y" : 120,
			"default_image" : RANK + "btn_up2_norm.png",
			"over_image"    : RANK + "btn_up2_hover.png",
			"down_image"    : RANK + "btn_up2_select.png",
		},
		{
			"name" : "nextBtn",
			"type" : "button",
			"x" : 0,
			"y" : 168,
			"default_image" : RANK + "btn_up2_norm.png",
			"over_image"    : RANK + "btn_up2_hover.png",
			"down_image"    : RANK + "btn_up2_select.png",
		},
	),
}
