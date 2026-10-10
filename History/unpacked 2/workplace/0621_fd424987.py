# coding: latin_1

import uiscriptlocale
import localeinfo

BOARD_WIDTH = 472
BOARD_HEIGHT = 380

window = {
	"name" : "GuildWindow_RolesPopup",

	"x" : 0,
	"y" : 0,

	"style" : ("movable", "float",),

	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,

	"children" :
	(
		{
			"name" : "Board",
			"type" : "board_with_titlebar",

			"x" : 0,
			"y" : 0,

			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,

			"title" : getattr(localeinfo, "GUILD_ROLES_TITLE", "Guild Roles"),

			"children" :
			(
			),
		},
	),
}
