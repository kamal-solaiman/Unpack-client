# coding: latin_1

#########################################
# title_name		: System Pack		#
# filename			: uiscript			#
# author			: Bvural41			#
# version			: Version 0.0.2		#
# date				: 2015 04 11		#
# update			: 2019 02 05		#
#########################################

import uiscriptlocale
import localeinfo

ROOT = "d:/ymir work/ui/game/"
FACE_SLOT_FILE = "d:/ymir work/ui/game/windows/box_face.sub"

window = {
	"name" : "ExchangeDialog",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
	"width" : 400 + 42,
	"height" : 200 + 50 + 90 -80 + 30, 
	"children" :
	(
		{
			"name" : "ExchangeLogs",
			"type" : "thinboard",
			"style" : ("attach",),
			"x" : 0,
			"y" : 235 - 50 + 30,
			"width" : 392,
			"height" : 80,
			"horizontal_align" : "center",
		},
		
		{
			"name" : "board",
			"type" : "board",
			"style" : ("attach",),
			"x" : 0,
			"y" : 0,
			"width" : 400 + 42,
			"height" : 200 + 30,
			"children" :
			(
				{
					"name" : "TitleBar",
					"type" : "titlebar",
					"style" : ("attach",),
					"x" : 8,
					"y" : 8,
					"width" : 384 + 42 + 2,
					"color" : "gray",
					"children" :
					(
						{
							"name" : "TitleName",
							"type" : "text",
							"x" : 192 + 10,
							"y" : 3,
							"text" : uiscriptlocale.EXCHANGE_TITLE,
							"text_horizontal_align" : "center"
						},
					),
				},
				{
					"name" : "Owner",
					"type" : "window",
					"x" : 10,
					"y" : 33 + 2 + 21,
					"width" : 200,
					"height" : 150 + 36,
					"children" :
					(
						{
							"name" : "Owner_Slot",
							"type" : "grid_table",
							"start_index" : 0,
							"x" : 0,
							"y" : 25,
							"x_count" : 6,
							"y_count" : 4,
							"x_step" : 32,
							"y_step" : 32,
							"x_blank" : 0,
							"y_blank" : 0,
							"image" : "d:/ymir work/ui/public/slot_base.sub",
						},
						{
							"name" : "Owner_Money",
							"type" : "button",
							"x" : 2,
							"y" : 1,
							"default_image" : "d:/ymir work/ui/public/parameter_slot_03.sub",
							"over_image" : "d:/ymir work/ui/public/parameter_slot_03.sub",
							"down_image" : "d:/ymir work/ui/public/parameter_slot_03.sub",
							"children" :
							(
								{
									"name" : "Owner_Money_Value",
									"type" : "text",
									"x" : 87,
									"y" : 2,
									"text" : "1234567",
									"text_horizontal_align" : "right",
								},
							),
						},
						# won simgesi owner
						{
							"name":"Cheque_Icon_owner",
							"type":"image",

							"x":177,
							"y":2,

							"image":"d:/ymir work/ui/game/windows/cheque_icon.sub",
						},						
						{
							"name":"wonn",
							"type":"text",

							"x":177 - 34,
							"y":2 - 20,

							"text" : localeinfo.EXCHANGE_WON,
							"text_horizontal_align" : "center",
						},						
						{
							"name":"yangg",
							"type":"text",

							"x":95 - 32 - 15,
							"y":2 - 20,

							"text" : localeinfo.EXCHANGE_YANG,
							"text_horizontal_align" : "center",
						},
						# yang simgesi owner
						{
							"name":"Cheque_Icon_owner",
							"type":"image",

							"x":95,
							"y":2,

							"image":"d:/ymir work/ui/game/windows/money_icon.sub",
						},
						{
							"name" : "Owner_Cheque",
							"type" : "button",
							"x" : 112,
							"y" : 1,
							"default_image" : "d:/ymir work/ui/public/parameter_slot_02.sub",
							"over_image" : "d:/ymir work/ui/public/parameter_slot_02.sub",
							"down_image" : "d:/ymir work/ui/public/parameter_slot_02.sub",
							"children" :
							(
								{
									"name" : "Owner_Cheque_Value",
									"type" : "text",
									"x" : 58,
									"y" : 2,
									"text" : "1234567",
									"text_horizontal_align" : "right",
								},
							),
						},
					),
				},
				{
					"name" : "Target",
					"type" : "window",
					"x" : 200 + 38,
					"y" : 33 + 2 + 21,
					"width" : 200,
					"height" : 150 + 36,
					"children" :
					(
						{
							"name" : "Target_Slot",
							"type" : "grid_table",
							"start_index" : 0,
							"x" : 0,
							"y" : 25,
							"x_count" : 6,
							"y_count" : 4,
							"x_step" : 32,
							"y_step" : 32,
							"x_blank" : 0,
							"y_blank" : 0,
							"image" : "d:/ymir work/ui/public/slot_base.sub",
						},
						{
							"name" : "Target_Money",
							"type" : "image",
							"x" : 0,
							"y" : 1,
							"image" : "d:/ymir work/ui/public/parameter_slot_03.sub",
							"children" :
							(
								{
									"name" : "Target_Money_Value",
									"type" : "text",
									"x" : 87,
									"y" : 2,
									"text" : "1234567",
									"text_horizontal_align" : "right",
								},
							),
						},
						# won simgesi owner
						{
							"name":"Cheque_Icon_owner",
							"type":"image",

							"x":176,
							"y":2,                   

							"image":"d:/ymir work/ui/game/windows/cheque_icon.sub",
						},
												
						{
							"name":"wonnt",
							"type":"text",

							"x":177 - 34,
							"y":2 - 20,

							"text" : localeinfo.EXCHANGE_WON,
							"text_horizontal_align" : "center",
						},						
						{
							"name":"yanggt",
							"type":"text",

							"x":95 - 32 - 15,
							"y":2 - 20,

							"text" : localeinfo.EXCHANGE_YANG,
							"text_horizontal_align" : "center",
						},
						
						# yang simgesi owner
						{
							"name":"Cheque_Icon_owner",
							"type":"image",

							"x":93,
							"y":2,                            

							"image":"d:/ymir work/ui/game/windows/money_icon.sub",
						},
						{
							"name" : "Target_Cheque",
							"type" : "image",

							"x" : 111,
							"y" : 1,
							"image" : "d:/ymir work/ui/public/parameter_slot_02.sub",
							"children" :
							(
								{
									"name" : "Target_Cheque_Value",
									"type" : "text",
									"x" : 58,
									"y" : 2,
									"text" : "1234567",
									"text_horizontal_align" : "right",
								},
							),
						},
					),
				},
				{
					"name" : "Owner_Accept_Button",
					"type" : "toggle_button",
					"text" : " ",
					"x" : 33 + 50 + 2 + 25 + 1 + 64 + 30,
					"y" : 200 + 18 - 96 + 38 - 50,
					"default_image" : "d:/ymir work/ui/game/exchange/own_arrow_01.tga",
					"over_image" : "d:/ymir work/ui/game/exchange/own_arrow_02.tga",
					"down_image" : "d:/ymir work/ui/game/exchange/own_arrow_03.tga",
				},
				{
					"name" : "Target_Accept_Button",
					"type" : "toggle_button",
					"text" : " ",
					"x" : 33 + 50 + 2 + 25 + 1 + 64 + 30,
					"y" : 200 + 18 - 96 + 38 + 18 - 50,
					"default_image" : "d:/ymir work/ui/game/exchange/target_arrow_01.tga",
					"over_image" : "d:/ymir work/ui/game/exchange/target_arrow_01.tga",
					"down_image" : "d:/ymir work/ui/game/exchange/target_arrow_03.tga",
				},
			),
		},
	),
}