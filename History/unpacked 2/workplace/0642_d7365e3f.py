# coding: latin_1

import uiscriptlocale

BOARDWIDTH = 126
BOARDHEIGHT = 70

MAINFOLDER = "locale/common/ui/"

window = {
	"name" : "ItemBox",

	"x" : SCREEN_WIDTH/2-BOARDWIDTH/2,
	"y" : SCREEN_HEIGHT /2-BOARDHEIGHT/2,

	"style" : ("float",),

	"width" : BOARDWIDTH,
	"height" : BOARDHEIGHT,

	"children" :
	(
		{
			"name" : "Background",
			"type" : "image",
			"style" : ("attach",),

			"x" : 0,
			"y" : 0,
			

			"image" : MAINFOLDER + "itemshop/item_main_box_norm.sub",

			"children" :
			(
				{
					"name" : "TimeBox",
					"type" : "image",
					"x" : 0,
					"y" : -19,
					"image" : MAINFOLDER+"itemshop/grey_medium_slotbar.sub",

					"children" :
					(
						## Countdown
						{
							"name" : "tx_countdown",
							"type" : "text",
							"text" : "Xh Xm Xs",
							"x" : 20,
							"y" : 3,
						},
					),
				},
				## Itemname
				{
					"name" : "tx_itemName",
					"type" : "text",
					"text" : "XXX",
					"x" : 6+10+20,
					"y" : 3,
				},
				## Item icon
				{
					"name" : "icon_box",
					"type" : "image",
					"x" : 4,
					"y" : 17,
					"image" : MAINFOLDER+"itemshop/item_icon_box.sub",

					"children" :
					(
						{
							"name" : "icon_item",
							"type" : "expanded_image",
							"x" : 7-20,
							"y" : 2+10,
							"image" : MAINFOLDER+"itemshop/item_icon_box.sub",
						},
						{
							"name" : "tx_itemPrice",
							"type" : "text",
							"text" : "XXX äÞæÏ",
							# "x" : 7,
							"x" : 67,
							"y" : 30-25,
						},
					),
				},
				## buy button
				{
					"name" : "btn_buy", 
					"type" : "button",
					"x" : 67-14,
					"y" : 44,
					"text" : "ÔÑÇÁ",
					"default_image" : MAINFOLDER+"itemshop/btn_buy_norm.sub",
					"over_image" : MAINFOLDER+"itemshop/btn_buy_hover.sub",
					"down_image" : MAINFOLDER+"itemshop/btn_buy_press.sub",
				},
				## amount
				{
					"name" : "sb_amount",
					"type" : "image",
					"x" : 66,
					"y" : 26,
					"image": MAINFOLDER + "itemshop/black_small_slotbar.sub",
							
					"children" :
					(
						{
							"name" : "ed_amount",
							"type" : "editline",
									
							"width" : 57,
							"height" : 18,
							"input_limit" : 3,
							"enable_codepage" : 0,
									
							"x" : 3,
							"y" : 1,
						},
						{
							"name" : "tx_itemAmountText",
							"type" : "text",
							"text" : " ÇáÚÏÏ ",
							"x" : 22,
							"y" : -2,
						},
					),
				},
				{
					"name" : "PercentBox",
					"type" : "image",
					"x" : 90,
					"y" : -15,
					"image" : MAINFOLDER+"itemshop/discount_percent_box.sub",
					
					"children" : 
					(
						{
							"name" : "tx_percent",
							"type" : "text",
							"text" : "10%",
							"fontsize" : "LARGE",
							"outline" : "true",
							"r": 1.000,
							"g": 0.549,
							"b": 0.000,
							"x" : 5,
							"y" : 5,
						},
					),
				},
			),
		},
	),
}