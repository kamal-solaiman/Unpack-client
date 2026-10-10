# coding: latin_1
#
# Layout for the reworked "Stone Correction" refine window (RefineDialogRenewal in
# uirefine.py). All positions / sizes / image paths live here so the window can be
# tuned without touching Python. STATIC size = background.png natural size (265x482);
# phase 1 builds the top area, the lower area is reserved for cost/buttons/pity.
# The attribute tooltip lives inside DescBg and scrolls by mouse wheel (no scrollbar).
# Only the full-window Background carries not_pick (else it swallows the titlebar
# close button); every other element stays pickable for the in-game UI debugger.
#
# Bottom section (phase 2): BottomPanel (bottom_bg) holds the pity row - PityBar
# (pity_bg) with PityIcon (pity_icon, hover = pity tooltip). The pity pips (one
# pitty_empty per point, overlaid with pitty_full when earned) are built in Python
# inside PityBar, since their count is data-driven by the server's pity max.
import localeinfo
NR = "d:/ymir work/ui/game/new_refine/"
FE = "d:/ymir work/ui/game/new_fast_equip/"

WINDOW_WIDTH  = 280
WINDOW_HEIGHT = 510

window = {
	"name" : "RefineDialogRenewal",
	"style" : ("movable", "float",),

	"x" : SCREEN_WIDTH - 400,
	"y" : 70 * 800 / SCREEN_HEIGHT,

	"width" : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,

	"children" :
	(
		{
			"name" : "board",
			"type" : "board_with_titlebar",

			"x" : 0, "y" : 0,
			"width" : WINDOW_WIDTH, "height" : WINDOW_HEIGHT,
			"title" : "Stone Correction",

			"children" :
			(
				{
					"name" : "Background",
					"type" : "image",
					"x" : 8, "y" : 28,
					"image" : NR + "background.png",
					#"style" : ("not_pick",),
				},

				{
					"name" : "Header1",
					"type" : "image",
					"x" : 2 + 8, "y" : 30,
					"image" : NR + "title_bg.png",
					"children" :
					(
						{
							"name" : "Header1Text", "type" : "text",
							"x" : 0, "y" : 8, "text" : "Upgrade Result",
							"horizontal_align" : "center", "text_horizontal_align" : "center",
						},
					),
				},

				{
					"name" : "ItemPanel",
					"type" : "image",
					"x" : 12, "y" : 59,
					"image" : NR + "bg_item.png",
					"children" :
					(
						{ "name" : "ItemSlotBg", "type" : "image", "x" : 10, "y" : 15, "image" : NR + "slot_item.png" },
						{ "name" : "DescBg",     "type" : "image", "x" : 64, "y" : 5,  "image" : NR + "bg_desc.png" },
					),
				},

				{
					"name" : "Header2",
					"type" : "image",
					"x" : 2 + 8, "y" : 195,
					"image" : NR + "title_bg.png",
					"children" :
					(
						{
							"name" : "Header2Text", "type" : "text",
							"x" : 0, "y" : 8, "text" : "Requirements",
							"horizontal_align" : "center", "text_horizontal_align" : "center",
						},
					),
				},

				{
					"name" : "MatPanel",
					"type" : "image",
					"x" : 11, "y" : 223,
					"image" : NR + "material_bg.png",
				},

				{
					"name" : "BottomPanel",
					"type" : "image",
					"x" : 11, "y" : 296,
					"image" : NR + "bottom_bg.png",
					"children" :
					(
						{
							"name" : "PityBar",
							"type" : "image",
							"x" : 5, "y" : 8,
							"image" : NR + "pity_bg.png",
							"children" :
							(
								{
									"name" : "experienceHeader_text",
									"type" : "text",
									"outline" : 1,
									"x" : 50, "y" : 6,
									"text" : localeinfo.PITTY_REFINE_TITLE,
									"color" : 0xFFcabdab,
									"text_horizontal_align" : "center",
								},
								{
									"name" : "PityIcon",
									"type" : "image",
									"x" : 189, "y" : 9,
									"image" : NR + "pity_icon.png",
								},
							),
						},

						{
							"name" : "ChanceBgSuccess",
							"type" : "image",
							"x" : 5, "y" : 48,
							"image" : NR + "bg_chance_success.png",
						},
						{
							"name" : "ChanceBgFail",
							"type" : "image",
							"x" : 5, "y" : 48,
							"image" : NR + "bg_could_fail.png",
						},
						{
							"name" : "ChanceText",
							"type" : "text",
							"outline" : 1,
							"x" : 128, "y" : 51,
							"text" : "",
							"color" : 0xFFcabdab,
							"text_horizontal_align" : "center",
						},
						{
							"name" : "GeneralBar",
							"type" : "image",
							"x" : 5, "y" : 76,
							"image" : NR + "bg_general.png",
							"children" :
							(
								{
									"name" : "ChkKeepOpen",
									"type" : "button",
									"x" : 6, "y" : 3,
									"default_image" : NR + "check_unselect.png",
									"over_image" : NR + "check_unselect.png",
									"down_image" : NR + "check_unselect.png",
								},
								{
									"name" : "KeepOpenLabel",
									"type" : "text",
									"x" : 27, "y" : 6,
									"text" : localeinfo.REFINE_AUTO,
									"color" : 0xFFcabdab,
									"outline" : 1,
								},
							),
						},
						{
							"name" : "PriceBar",
							"type" : "image",
							"x" : 5, "y" : 102,
							"image" : NR + "bg_general.png",
							"children" :
							(
								{
									"name" : "PriceText",
									"type" : "text",
									"x" : 218, "y" : 6,
									"text" : "",
									"color" : 0xFFffe6a0,
									"outline" : 1,
								},
								{
									"name" : "YangIcon",
									"type" : "image",
									"x" : 221, "y" : 5,
									"image" : NR + "yang.png",
								},
							),
						},
						{
							"name" : "BonusRow",
							"type" : "image",
							"x" : 5, "y" : 128,
							"image" : NR + "bg_chance_success.png",
							"children" :
							(
								{
									"name" : "BonusText",
									"type" : "text",
									"x" : 123, "y" : 6,
									"text" : "",
									"color" : 0xFFcabdab,
									"outline" : 1,
									"text_horizontal_align" : "center",
								},
							),
						},
						{
							"name" : "OKButton",
							"type" : "button",
							"x" : 2, "y" : 174,
							"default_image" : FE + "btn_norm.png",
							"over_image" : FE + "btn_hover.png",
							"down_image" : FE + "btn_select.png",
						},
						{
							"name" : "CancelButton",
							"type" : "button",
							"x" : 129, "y" : 174,
							"default_image" : FE + "btn_norm.png",
							"over_image" : FE + "btn_hover.png",
							"down_image" : FE + "btn_select.png",
						},
					),
				},
			),
		},
	),
}
