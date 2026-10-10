# coding: latin_1

import uiscriptlocale

ROOT_PATH			= "d:/ymir work/ui/game/premium_private_shop/"

WINDOW_WIDTH		= 196
WINDOW_HEIGHT		= 448

if ENABLE_CHEQUE_SYSTEM:
	window = {
		"name" : "PremiumPrivateShopDialog",
		"style" : ("movable", "float",),
		
		"x" : SCREEN_WIDTH / 2 - WINDOW_WIDTH / 2,
		"y" : SCREEN_HEIGHT / 2 - WINDOW_HEIGHT / 2,

		"width"		: WINDOW_WIDTH,
		"height"	: WINDOW_HEIGHT,

		"children" :
		(
			{
				"name" : "board",
				"type" : "board_with_titlebar",
				"style" : ("attach", "ltr",),

				"x" : 0,
				"y" : 0,

				"width"		: WINDOW_WIDTH,
				"height"	: WINDOW_HEIGHT,
				"title"		: uiscriptlocale.PREMIUM_PRIVATE_SHOP_TITLE,

				"children" :
				(
					# Shop Position Icon
					{
						"name"	: "position_icon",
						"type"	: "image",
						"x"		: 7,
						"y"		: 39,
						"image"	: ROOT_PATH + "position_icon.sub",
					},
					
					# Shop Title
					{
						"name" : "shop_name_text_window", "type" : "window", "style" : ("attach",), "x" : 27, "y" : 36, "width" : 158, "height" : 19,
						"children" :
						(
							{ 
								"name" : "shop_name_text_button", 
								"type":"button", 
								
								"x":0, 
								"y":0, 
								
								"default_image" : ROOT_PATH + "shop_name_text_bg.sub", 
								"over_image" : ROOT_PATH + "shop_name_text_bg.sub", 
								"down_image" : ROOT_PATH + "shop_name_text_bg.sub", 
								
								"image" : ROOT_PATH + "shop_name_text_bg.sub", 
								# "style" : ("not_pick",), 
							},
							{ "name" : "shop_name_text", "type" : "text", "x" : 0, "y" : 0, "all_align" : "center", "text" : "", "style" : ("not_pick",), },
						),
					},
					
					# Shop Notice Text
					{
						"name" : "shop_notice_window", "type" : "window", "style" : ("attach",), "x" : 11, "y" : 55, "width" : 173, "height" : 19,
						"children" :
						(
							{ "name" : "shop_notice_bg", "type":"image", "x":0, "y":0, "image" : ROOT_PATH + "notice_bg.sub", },
							{ "name" : "shop_notice_text", "type" : "text", "x" : 0, "y" : 0, "all_align" : "center", "text" : "", },
						),
					},
					
					## Item Slot
					{
						"name" : "item_slot",
						"type" : "grid_table",

						"x" : 17,
						"y" : 75,

						"start_index" : 0,
						"x_count" : 5,
						"y_count" : 8,
						"x_step" : 32,
						"y_step" : 32,

						"image" : "d:/ymir work/ui/public/Slot_Base.sub",
					},
					
					{
						"name" : "btnpage0",
						"type" : "radio_button",
						"x" : (WINDOW_WIDTH / 2) - 66,
						"y" : 334,
						"text" : "I",
						"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
						"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
						"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
					},
					{
						"name" : "btnpage1",
						"type" : "radio_button",
						"x" : (WINDOW_WIDTH / 2) - 33,
						"y" : 334,
						"text" : "II",
						"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
						"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
						"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
					},
					{
						"name" : "btnpage2",
						"type" : "radio_button",
						"x" : (WINDOW_WIDTH / 2),
						"y" : 334,
						"text" : "III",
						"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
						"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
						"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
					},
					{
						"name" : "btnpage3",
						"type" : "radio_button",
						"x" : (WINDOW_WIDTH / 2) + 33,
						"y" : 334,
						"text" : "IV",
						"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
						"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
						"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
					},
					# Sandglass Icon
					{
						"name"	: "sandglass_icon",
						"type"	: "image",
						"x"		: 16,
						"y"		: 358,
						"image"	: ROOT_PATH + "sandglass_icon.sub",
					},
					
					# Remanining Time Text
					{
						"name" : "remain_time_text_window", "type" : "window", "style" : ("attach",), "x" : 40, "y" : 357, "width" : 137, "height" : 18,
						"children" :
						(
							{ "name" : "remain_time_text_bg", "type":"image", "x":0, "y":0, "image" : ROOT_PATH + "remain_time_text_bg.sub", },
							{ "name" : "remain_time_text", "type" : "text", "x" : 0, "y" : 0, "all_align" : "center", "text" : "", },
						),
					},
					
					# Won Icon
					{
						"name":"cheque_icon",
						"type":"image",
						
						"x": 16,
						"y": 380,

						"image":"d:/ymir work/ui/game/windows/cheque_icon.sub",
					},
					# Won Text
					{
						"name" : "cheque_text_window", "type" : "window", "style" : ("attach",), "x" : 40, "y" : 378, "width" : 24, "height" : 18,
						"children" :
						(
							{ "name" : "cheque_text_bg", "type":"image", "x":0, "y":0, "image" : ROOT_PATH + "won_text_bg.sub", },
							{ "name" : "cheque_text", "type" : "text", "x" : 0, "y" : 0, "all_align" : "center", "text" : "", },
						),
					},
					
					# Yang Icon
					{
						"name":"gold_icon",
						"type":"image",
						
						"x": 69,
						"y": 380,

						"image":"d:/ymir work/ui/game/windows/money_icon.sub",
					},
					
					## Yang Text
					{
						"name" : "gold_text_window", "type" : "window", "style" : ("attach",), "x" : 87, "y" : 378, "width" : 90, "height" : 18,
						"children" :
						(
							{ "name" : "gold_text_bg", "type":"image", "x":0, "y":0, "image" : ROOT_PATH + "yang_text_bg.sub", },
							{ "name" : "gold_text", "type" : "text", "x" : 0, "y" : 0, "all_align" : "center", "text" : "", },
						),
					},
					
					# Modify Button
					{
						"name" : "modify_button",
						"type" : "button",

						"x" : 12,
						"y" : 410,
						
						"default_image" : ROOT_PATH + "modify_button_default.sub",
						"over_image" : ROOT_PATH + "modify_button_over.sub",
						"down_image" : ROOT_PATH + "modify_button_down.sub",
					},
					
					# Reopen Button
					{
						"name" : "reopen_button",
						"type" : "button",

						"x" : 70,
						"y" : 410,

						"default_image" : ROOT_PATH + "reopen_button_default.sub",
						"over_image" : ROOT_PATH + "reopen_button_over.sub",
						"down_image" : ROOT_PATH + "reopen_button_down.sub",
					},
					
					# Tax Adjustment Button
					{
						"name" : "tax_adjustment_button",
						"type" : "button",

						"x" : 70,
						"y" : 410,
						
						"default_image" : ROOT_PATH + "tax_adjustment_button_default.sub",
						"over_image" : ROOT_PATH + "tax_adjustment_button_over.sub",
						"down_image" : ROOT_PATH + "tax_adjustment_button_down.sub",
					},
					
					# Shop Close Button
					{
						"name" : "shop_close_button",
						"type" : "button",

						"x" : 128,
						"y" : 409,
						
						"default_image" : ROOT_PATH + "shop_close_button_default.sub",
						"over_image" : ROOT_PATH + "shop_close_button_over.sub",
						"down_image" : ROOT_PATH + "shop_close_button_down.sub",
					},
				),
			},
		),
	}
else:
	window = {
		"name" : "PremiumPrivateShopDialog",
		"style" : ("movable", "float",),
		
		"x" : SCREEN_WIDTH / 2 - WINDOW_WIDTH / 2,
		"y" : SCREEN_HEIGHT / 2 - WINDOW_HEIGHT / 2,

		"width"		: WINDOW_WIDTH,
		"height"	: WINDOW_HEIGHT,

		"children" :
		(
			{
				"name" : "board",
				"type" : "board_with_titlebar",
				"style" : ("attach", "ltr",),

				"x" : 0,
				"y" : 0,

				"width"		: WINDOW_WIDTH,
				"height"	: WINDOW_HEIGHT,
				"title"		: uiscriptlocale.PREMIUM_PRIVATE_SHOP_TITLE,

				"children" :
				(
					# Shop Position Icon
					{
						"name"	: "position_icon",
						"type"	: "image",
						"x"		: 7,
						"y"		: 39,
						"image"	: ROOT_PATH + "position_icon.sub",
					},
					
					# Shop Title
					{
						"name" : "shop_name_text_window", "type" : "window", "style" : ("attach",), "x" : 27, "y" : 36, "width" : 158, "height" : 19,
						"children" :
						(
							{ 
								"name" : "shop_name_text_button", 
								"type":"button", 
								
								"x":0, 
								"y":0, 
								
								"default_image" : ROOT_PATH + "shop_name_text_bg.sub", 
								"over_image" : ROOT_PATH + "shop_name_text_bg.sub", 
								"down_image" : ROOT_PATH + "shop_name_text_bg.sub", 
								
								"image" : ROOT_PATH + "shop_name_text_bg.sub", 
								# "style" : ("not_pick",), 
							},
							{ "name" : "shop_name_text", "type" : "text", "x" : 0, "y" : 0, "all_align" : "center", "text" : "", "style" : ("not_pick",), },
						),
					},
					
					# Shop Notice Text
					{
						"name" : "shop_notice_window", "type" : "window", "style" : ("attach",), "x" : 11, "y" : 55, "width" : 173, "height" : 19,
						"children" :
						(
							{ "name" : "shop_notice_bg", "type":"image", "x":0, "y":0, "image" : ROOT_PATH + "notice_bg.sub", },
							{ "name" : "shop_notice_text", "type" : "text", "x" : 0, "y" : 0, "all_align" : "center", "text" : "", },
						),
					},
					
					## Item Slot
					{
						"name" : "item_slot",
						"type" : "grid_table",

						"x" : 17,
						"y" : 75,

						"start_index" : 0,
						"x_count" : 5,
						"y_count" : 8,
						"x_step" : 32,
						"y_step" : 32,

						"image" : "d:/ymir work/ui/public/Slot_Base.sub",
					},
					
					## Tab 1
					{
						"name" : "tab1",
						"type" : "radio_button",
						
						"x" : WINDOW_WIDTH/2 - 32,
						"y" : 334,

						"text" : "I",

						"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
						"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
						"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
					},

					## Tab 2
					{
						"name" : "tab2",
						"type" : "radio_button",
						
						"x" : WINDOW_WIDTH/2 + 1,
						"y" : 334,

						"text" : "II",

						"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
						"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
						"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
					},
					
					# Sandglass Icon
					{
						"name"	: "sandglass_icon",
						"type"	: "image",
						"x"		: 16,
						"y"		: 358,
						"image"	: ROOT_PATH + "sandglass_icon.sub",
					},
					
					# Remanining Time Text
					{
						"name" : "remain_time_text_window", "type" : "window", "style" : ("attach",), "x" : 40, "y" : 357, "width" : 137, "height" : 18,
						"children" :
						(
							{ "name" : "remain_time_text_bg", "type":"image", "x":0, "y":0, "image" : ROOT_PATH + "remain_time_text_bg.sub", },
							{ "name" : "remain_time_text", "type" : "text", "x" : 0, "y" : 0, "all_align" : "center", "text" : "", },
						),
					},

					
					# Yang Icon
					{
						"name":"gold_icon",
						"type":"image",
						
						"x": 16,
						"y": 380,

						"image":"d:/ymir work/ui/game/windows/money_icon.sub",
					},
					
					## Yang Text
					{
						"name" : "gold_text_window", "type" : "window", "style" : ("attach",), "x" : 40, "y" : 378, "width" : 137, "height" : 18,
						"children" :
						(
							{ "name" : "gold_text_bg", "type":"image", "x":0, "y":0, "image" : ROOT_PATH + "remain_time_text_bg.sub", },
							{ "name" : "gold_text", "type" : "text", "x" : 0, "y" : 0, "all_align" : "center", "text" : "", },
						),
					},
					
					# Modify Button
					{
						"name" : "modify_button",
						"type" : "button",

						"x" : 12,
						"y" : 410,
						
						"default_image" : ROOT_PATH + "modify_button_default.sub",
						"over_image" : ROOT_PATH + "modify_button_over.sub",
						"down_image" : ROOT_PATH + "modify_button_down.sub",
					},
					
					# Reopen Button
					{
						"name" : "reopen_button",
						"type" : "button",

						"x" : 70,
						"y" : 410,

						"default_image" : ROOT_PATH + "reopen_button_default.sub",
						"over_image" : ROOT_PATH + "reopen_button_over.sub",
						"down_image" : ROOT_PATH + "reopen_button_down.sub",
					},
					
					# Tax Adjustment Button
					{
						"name" : "tax_adjustment_button",
						"type" : "button",

						"x" : 70,
						"y" : 410,
						
						"default_image" : ROOT_PATH + "tax_adjustment_button_default.sub",
						"over_image" : ROOT_PATH + "tax_adjustment_button_over.sub",
						"down_image" : ROOT_PATH + "tax_adjustment_button_down.sub",
					},
					
					# Shop Close Button
					{
						"name" : "shop_close_button",
						"type" : "button",

						"x" : 128,
						"y" : 409,
						
						"default_image" : ROOT_PATH + "shop_close_button_default.sub",
						"over_image" : ROOT_PATH + "shop_close_button_over.sub",
						"down_image" : ROOT_PATH + "shop_close_button_down.sub",
					},
				),
			},
		),
	}