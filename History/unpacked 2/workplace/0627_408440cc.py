# coding: latin_1

IMG = "d:/ymir work/ui/game/horse/"

WINDOW_WIDTH = 340
WINDOW_HEIGHT = 100
CENTER_X = WINDOW_WIDTH / 2

window = {
	"name" : "HorseUpgradeProgressPopup",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
	"width" : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,
	"children" :
	(
		{
			"name" : "popup_board",
			"type" : "thinboard",
			"style" : ("attach",),
			"x" : 0,
			"y" : 0,
			"width" : WINDOW_WIDTH,
			"height" : WINDOW_HEIGHT,
			"children" :
			(
				## Centered title — works visually in both LTR and RTL.
				{
					"name" : "popup_title_text",
					"type" : "text",
					"x" : CENTER_X,
					"y" : 14,
					"text" : "",
					"text_horizontal_align" : "center",
				},

				## Icon, close X, gauge, time icon, time text — all created in
				## code via ui.ImageBox / ui.TextLine so absolute positions are
				## honoured under both LTR and RTL locales.

				## ---- Divider line under the title ----
				{
					"name" : "popup_divider",
					"type" : "bar",
					"x" : 12,
					"y" : 42,
					"width" : WINDOW_WIDTH - 24,
					"height" : 1,
					"color" : 0x60FFFFFF,
				},
			),
		},
	),
}
