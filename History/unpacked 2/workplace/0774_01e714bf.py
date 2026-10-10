# coding: latin_1

import uiscriptlocale
import localeinfo

BOARD_WIDTH = 520
BOARD_HEIGHT = 160
PATH_ROOT = "cream/searchshop/"
window = {
	"name" : "RoutesPvPWindow",
	"style" : ("movable", "float",),
	
	"x" : 0,
	"y" : 0,
	
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	
	"children" :
	(
		{
			"name" : "board",
			"type" : "board_with_titlebar",
			"style" : ("attach",),
			
			"x" : 0,
			"y" : 0,
			
			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
			
			"title" : localeinfo.PVP_ROUTES_TITLE,
			"children" :
			(
				{
					"name" : "itemicon",
					"type" : "expanded_image",
					"style" : ("ltr",),
					"x" : 75-55,
					"y" : 45,
					
					"image" : "icon/item/ruta3.tga",
				},
				{
					"name" : "itemicon1",
					"type" : "expanded_image",
					"style" : ("ltr",),
					
					"x" : 75+65-40,
					"y" : 45,
					
					"image" : "icon/item/ruta1.tga",
				},
				{
					"name" : "itemicon2",
					"type" : "expanded_image",
					"style" : ("ltr",),
					
					"x" : 75+65+65-40,
					"y" : 45,
					
					"image" : "icon/item/ruta1.tga",
				},
				{
					"name" : "itemicon3",
					"type" : "expanded_image",
					"style" : ("ltr",),
					
					"x" : 75+65+65+65-40,
					"y" : 45,
					
					"image" : "icon/item/ruta1.tga",
				},
				{
					"name" : "itemicon4",
					"type" : "expanded_image",
					"style" : ("ltr",),
					
					"x" : 75+65+65+65+65-40,
					"y" : 45,
					
					"image" : "icon/item/ruta2.tga",
				},
				{
					"name" : "itemicon5",
					"type" : "expanded_image",
					"style" : ("ltr",),
					
					"x" : 75+65+65+65+65+65-40,
					"y" : 45,
					
					"image" : "icon/item/ruta1.tga",
				},
				{
					"name" : "itemicon6",
					"type" : "expanded_image",
					"style" : ("ltr",),
					
					"x" : 75+65+65+65+65+65+65-40,
					"y" : 45,
					
					"image" : "icon/item/ruta1.tga",
				},
				{
					"name" : "type0button",
					"type" : "button",
					"style" : ("ltr",),
					
					"horizontal_align" : "center",
					"vertical_align" : "bottom",
					
					"x" : 0,
					"y" : 40,
					
					"text" : localeinfo.PVP_ROUTES_GET,
					
					"default_image" : PATH_ROOT+"category_norm.dds",
					"over_image" : PATH_ROOT+"category_hover.dds",
					"down_image" : PATH_ROOT+"category_down.dds",
				},
				{
					"name" : "textpuntos",
					"type" : "text",
					
					"horizontal_align" : "right",
					"vertical_align" : "bottom",
					
					"x" : 20+20+50+50,
					"y" : 38,
					
					"color" : 0xFFFEE3AE,
					"text" : "",
				},
			),
		},
	),
}