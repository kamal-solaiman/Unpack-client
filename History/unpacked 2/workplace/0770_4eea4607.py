# coding: latin_1

import localeinfo

WINDOW_WIDTH = 410
WINDOW_HEIGHT = 440
FONT_COLOR = 0xFFF5E6BA

window = {
	"name" : "RenderTargetWindow",

	"x" : 0,
	"y" : 0,

	"style" : ("movable", "float","ltr",),

	"width" : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT,

	"children":
	(
		{
			"name" : "board",
			"type" : "board",
			"style" : ("attach",),

			"x" : 0,
			"y" : 0,

			"width" : WINDOW_WIDTH,
			"height" : WINDOW_HEIGHT,

			"children" :
			(
				## Title
				{
					"name" : "TitleBar",
					"type" : "titlebar",
					"style" : ("attach",),

					"x" : 8,
					"y" : 7,

					"width" : WINDOW_WIDTH - 15,
					"color" : "yellow",

					"children" :
					(
						{ "name":"TitleName", "type":"text", "x": (WINDOW_WIDTH - 15) / 2, "y":3, "text" : localeinfo.RENDER_TITLE, "text_horizontal_align":"center" },
					),
				},

				# RenderView
				{
					"name" : "RenderTarget",
					"type" : "render_target",
					"style" : ("attach","ltr",),

					"x" : 10,
					"y" : 30,

					"width" : 390,
					"height" : 400,
					"children" :
					(
						{
							"name" : "MoveUp",
							"type" : "button",
							"style" : ("ltr",),
							"x" : -5,
							"y" : 380,
							"color" : FONT_COLOR,
							"text" : localeinfo.RENDER_UP,

							"default_image" : "d:/ymir work/ui/render/new/render_up_normal.tga",
							"over_image" : "d:/ymir work/ui/render/new/render_up_hover.tga",
							"down_image" : "d:/ymir work/ui/render/new/render_up_down.tga",
						},

						{
							"name" : "MoveDown",
							"type" : "button",
							"style" : ("ltr",),
							"x" : 50,
							"y" : 380,
							"color" : FONT_COLOR,
							"text" : localeinfo.RENDER_DOWN,

							"default_image" : "d:/ymir work/ui/render/new/render_up_normal.tga",
							"over_image" : "d:/ymir work/ui/render/new/render_up_hover.tga",
							"down_image" : "d:/ymir work/ui/render/new/render_up_down.tga",
						},
						{
							"name" : "RotateLeft",
							"type" : "button",
							"style" : ("ltr",),
							"x" : 105,
							"y" : 380,
							"color" : FONT_COLOR,
							"text" : localeinfo.RENDER_LEFT,

							"default_image" : "d:/ymir work/ui/render/new/render_up_normal.tga",
							"over_image" : "d:/ymir work/ui/render/new/render_up_hover.tga",
							"down_image" : "d:/ymir work/ui/render/new/render_up_down.tga",
						},

						{
							"name" : "RotateRight",
							"type" : "button",
							"style" : ("ltr",),
							"x" : 215,
							"y" : 380,
							"color" : FONT_COLOR,
							"text" : localeinfo.RENDER_RIGHT,

							"default_image" : "d:/ymir work/ui/render/new/render_up_normal.tga",
							"over_image" : "d:/ymir work/ui/render/new/render_up_hover.tga",
							"down_image" : "d:/ymir work/ui/render/new/render_up_down.tga",
						},

						{
							"name" : "Refresh",
							"type" : "button",
							"style" : ("ltr",),
							"x" : 160,
							"y" : 380,
							"color" : FONT_COLOR,
							"text" : localeinfo.RENDER_REFRESH,

							"default_image" : "d:/ymir work/ui/render/new/render_up_normal.tga",
							"over_image" : "d:/ymir work/ui/render/new/render_up_hover.tga",
							"down_image" : "d:/ymir work/ui/render/new/render_up_down.tga",
						},
						{
							"name" : "ZoomIn",
							"type" : "button",
							"style" : ("ltr",),
							"x" : 270,
							"y" : 380,
							"color" : FONT_COLOR,
							"text" : localeinfo.RENDER_ZOOMIN,

							"default_image" : "d:/ymir work/ui/render/new/render_up_normal.tga",
							"over_image" : "d:/ymir work/ui/render/new/render_up_hover.tga",
							"down_image" : "d:/ymir work/ui/render/new/render_up_down.tga",
						},

						{
							"name" : "ZoomOut",
							"type" : "button",
							"style" : ("ltr",),
							"x" : 325,
							"y" : 380,
							"color" : FONT_COLOR,
							"text" : localeinfo.RENDER_ZOOMOUT,

							"default_image" : "d:/ymir work/ui/render/new/render_up_normal.tga",
							"over_image" : "d:/ymir work/ui/render/new/render_up_hover.tga",
							"down_image" : "d:/ymir work/ui/render/new/render_up_down.tga",
						},
					),
				},
			),
		},
	),
}