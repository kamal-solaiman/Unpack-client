# coding: latin_1

import uiscriptlocale
#import item

window = {
	"name" : "sideBarBoard",

	"x" : -40,
	"y" : 3,

	"width" : 60,
	"height" : 123,


	"style" : ("attach", "float"),

	"children" :
	(
		{
			"name" : "board",
			"type" : "invisibleboard",
			"style" : ("attach",),

			"x" : 0,
			"y" : 0,

			"width" : 60,
			"height" : 123,

			"children" : 
			(
				## Search Shop
				{
					"name" : "SearchShopButton",
					"type" : "button",

					"x" : 6,
					"y" : 7,

					"default_image" : "d:/ymir work/ui/game/windows/button_search_shop_01.tga",
					"over_image" : "d:/ymir work/ui/game/windows/button_search_shop_02.tga",
					"down_image" : "d:/ymir work/ui/game/windows/button_search_shop_03.tga",
				},
				## Switch Bot
				{
					"name" : "SwitchBotButton",
					"type" : "button",

					"x" : 6,
					"y" : 11+35,

					"default_image" : "d:/ymir work/ui/game/windows/button_switch_bot_01.tga",
					"over_image" : "d:/ymir work/ui/game/windows/button_switch_bot_02.tga",
					"down_image" : "d:/ymir work/ui/game/windows/button_switch_bot_03.tga",
				},
				## Inventaire speciale
				{
					"name" : "SpecialInventoryButton",
					"type" : "button",

					"x" : 6,
					"y" : 15 + 35*2,

					"default_image" : "d:/ymir work/ui/game/windows/inventaire_special_button_01.tga",
					"over_image" : "d:/ymir work/ui/game/windows/inventaire_special_button_02.tga",
					"down_image" : "d:/ymir work/ui/game/windows/inventaire_special_button_03.tga",
				},		
			),
		},
	),
}