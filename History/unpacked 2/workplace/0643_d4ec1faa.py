import uiscriptlocale

ROOT = "d:/ymir work/ui/game/keyboard/"
INV_ROOT = "d:/ymir work/ui/game/inv_manage/"

window = {
	"name" : "KeyBindWindow",
	"style" : ("movable", "float",),
	"x" : 0, "y" : 0,
	"width" : 430, "height" : 420,
	"children" :
	(
		{
			"name" : "board", "type" : "board",
			"style" : ("attach",),
			"x" : 0, "y" : 0, "width" : 430, "height" : 420,
			"children" :
			(
				{
					"name" : "Background", "type" : "expanded_image",
					"style" : ("not_pick",),
					"x" : 9, "y" : 30,
					"x_scale" : 1.0, "y_scale" : 1.124,
					"image" : ROOT + "background.png",
				},
				{
					"name" : "ResetBase", "type" : "image",
					"style" : ("attach",),
					"x" : 8, "y" : 7,
					"image" : "d:/ymir work/ui/pattern/titlebar_inv_refresh_baseframe.tga",
					"children" :
					(
						{
							"name" : "ResetButton", "type" : "button",
							"x" : 0, "y" : 0,
							"tooltip_text" : uiscriptlocale.KEYBIND_RESET_CONFIRM,
							"default_image" : INV_ROOT + "btn-settings-1.png",
							"over_image" : INV_ROOT + "btn-settings-2.png",
							"down_image" : INV_ROOT + "btn-settings-3.png",
						},
					),
				},
				{
					"name" : "TitleBar", "type" : "titlebar",
					"style" : ("attach",),
					"x" : 8 + 38, "y" : 7, "width" : 430 - 15 - 38,
					"color" : "red",
					"children" :
					(
						{
							"name" : "TitleName", "type" : "text",
							"x" : 188, "y" : 3,
							"text" : uiscriptlocale.KEYBIND_TITLE,
							"text_horizontal_align" : "center",
						},
					),
				},
				{
					"name" : "SearchBack", "type" : "expanded_image",
					"x" : 14, "y" : 32,
					"x_scale" : 4.409, "y_scale" : 1.0,
					"image" : ROOT + "input_bg.png",
					"children" :
					(
						{
							"name" : "SearchInput", "type" : "editline",
							"x" : 4, "y" : 2, "width" : 380, "height" : 16,
							"input_limit" : 24,
						},
					),
				},
				{
					"name" : "ListArea", "type" : "window",
					"x" : 12, "y" : 56, "width" : 390, "height" : 348,
				},
				{
					"name" : "ListScrollBar", "type" : "scrollbar",
					"x" : 406, "y" : 56, "size" : 348,
				},
			),
		},
	),
}
