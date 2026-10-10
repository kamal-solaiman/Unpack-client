import uiscriptlocale

ROOT = "d:/ymir work/ui/skillcolor/"
BTN = "d:/ymir work/ui/game/new_fast_equip/"

BOARD_WIDTH = 300
BOARD_HEIGHT = 512

GRADIENT_SIZE = 225
GRADIENT_X = 37
GRADIENT_Y = 36

PANEL_X = 12
PANEL_Y = 272
PANEL_WIDTH = 276
PANEL_HEIGHT = 186

LABEL_COLOR = 0xffd0c2b7
LINE_COLOR = 0xff4a443e

BTN_WIDTH = 126
BTN_HEIGHT = 30
BTN_Y = 468
BTN_LEFT_X = 18
BTN_RIGHT_X = 156

window = {
	"name" : "DamageColorPicker",
	"style" : ("movable", "float", "ltr",),

	"x" : 0,
	"y" : 0,

	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,

	"children" :
	(
		{
			"name" : "board",
			"type" : "board_with_titlebar",
			"style" : ("attach", "ltr",),

			"x" : 0,
			"y" : 0,

			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,

			"title" : uiscriptlocale.OPTION_DMGCOLOR_TITLE,

			"children" :
			(
				{
					"name" : "PickerImage",
					"type" : "image",
					"style" : ("ltr",),

					"x" : GRADIENT_X,
					"y" : GRADIENT_Y,

					"image" : ROOT + "color_picker_background.tga",

					"children" :
					(
						{
							"name" : "PickerButton",
							"type" : "button",
							"style" : ("ltr",),

							"x" : 0,
							"y" : 0,

							"width" : GRADIENT_SIZE,
							"height" : GRADIENT_SIZE,
						},
						{
							"name" : "PickerDotImage",
							"type" : "image",
							"style" : ("ltr",),

							"x" : 0,
							"y" : 0,

							"image" : ROOT + "color_picker_dot.tga",
						},
					),
				},
				{
					"name" : "ControlPanel",
					"type" : "v2_thinboard",
					"style" : ("attach", "ltr",),

					"x" : PANEL_X,
					"y" : PANEL_Y,

					"width" : PANEL_WIDTH,
					"height" : PANEL_HEIGHT,

					"children" :
					(
						{
							"name" : "PresetLabel",
							"type" : "text",

							"x" : 12,
							"y" : 9,

							"text_horizontal_align" : "left",
							"text" : "Presets",
							"outline" : 1,
							"color" : LABEL_COLOR,
						},
						{
							"name" : "PresetBar",
							"type" : "window",
							"style" : ("ltr",),

							"x" : 12,
							"y" : 27,

							"width" : 250,
							"height" : 16,
						},
						{
							"name" : "SepLine1",
							"type" : "line",

							"x" : 10,
							"y" : 53,

							"width" : PANEL_WIDTH - 20,
							"height" : 0,

							"color" : LINE_COLOR,
						},
						{
							"name" : "HexLabel",
							"type" : "text",

							"x" : 12,
							"y" : 65,

							"text_horizontal_align" : "left",
							"text" : "Hex",
							"outline" : 1,
							"color" : LABEL_COLOR,
						},
						{
							"name" : "HexSlotImage",
							"type" : "image",
							"style" : ("ltr",),

							"x" : 52,
							"y" : 61,

							"image" : "d:/ymir work/ui/public/Parameter_Slot_02.sub",

							"children" :
							(
								{
									"name" : "HexEditLine",
									"type" : "editline",
									"style" : ("ltr",),

									"x" : 6,
									"y" : 3,

									"width" : 70,
									"height" : 16,

									"input_limit" : 7,
									"enable_codepage" : 0,
								},
							),
						},
						{
							"name" : "CurrentSwatchSlot",
							"type" : "window",
							"style" : ("ltr",),

							"x" : 196,
							"y" : 61,

							"width" : 68,
							"height" : 20,
						},
						{
							"name" : "SepLine2",
							"type" : "line",

							"x" : 10,
							"y" : 91,

							"width" : PANEL_WIDTH - 20,
							"height" : 0,

							"color" : LINE_COLOR,
						},
						{
							"name" : "PreviewLabel",
							"type" : "text",

							"x" : 12,
							"y" : 101,

							"text_horizontal_align" : "left",
							"text" : "Preview",
							"outline" : 1,
							"color" : LABEL_COLOR,
						},
						{
							"name" : "PreviewBar",
							"type" : "window",
							"style" : ("ltr",),

							"x" : 5,
							"y" : 118,

							"width" : 266,
							"height" : 64,
						},
					),
				},
				{
					"name" : "DefaultButton",
					"type" : "button",
					"style" : ("ltr",),

					"x" : BTN_LEFT_X,
					"y" : BTN_Y,

					"width" : BTN_WIDTH,
					"height" : BTN_HEIGHT,

					"default_image" : BTN + "btn_norm.png",
					"over_image" : BTN + "btn_hover.png",
					"down_image" : BTN + "btn_select.png",

					"text" : "",
				},
				{
					"name" : "ApplyButton",
					"type" : "button",
					"style" : ("ltr",),

					"x" : BTN_RIGHT_X,
					"y" : BTN_Y,

					"width" : BTN_WIDTH,
					"height" : BTN_HEIGHT,

					"default_image" : BTN + "btn_norm.png",
					"over_image" : BTN + "btn_hover.png",
					"down_image" : BTN + "btn_select.png",

					"text" : "",
				},
			),
		},
	),
}
