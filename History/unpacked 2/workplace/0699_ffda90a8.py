# coding: latin_1

import localeinfo

ELEMENT_BASE_Y = 26
ELEMENT_Y_DIF = 14

BOARD_WIDTH = 242
BOARD_HEIGHT = 507

EXTRA_Y = 0

DESC_BASE_X = 22

window = {
	"name" : "MoneyInputDialogNew",
	"x" : 0,
	"y" : 0,
	"style" : ("movable", "float",),
	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,
	"children" :
	[
		{
			"name" : "ui_board",
			"type" : "image",
			"style" : ("attach",),
			"x" : 0,
			"y" : 0,
			"image" : "cream/shopseller/bg_big.png",
			"children" :
			[
				{
					"name" : "ui_desc1_text",
					"type" : "text",
					"x" : 0,
					"y" : ELEMENT_BASE_Y,
					"text" : localeinfo.OFFLINESHOP_SELL_DESC1,
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
				},
				{
					"name" : "ui_desc2_text",
					"type" : "text",
					"x" : 0,
					"y" : ELEMENT_BASE_Y + ELEMENT_Y_DIF,
					"text" : localeinfo.OFFLINESHOP_SELL_DESC2,
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
				},
				{
					"name" : "ui_input_bg_aftertax",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 8 + ELEMENT_BASE_Y + (ELEMENT_Y_DIF * 2),
					"image" : "cream/shopseller/price_with_tax.png",
					"horizontal_align" : "center",
					"children" :
					[
						{
							"name" : "ui_bg_aftertext_insert",
							"type" : "window",
							"x" : 1,
							"y" : 1,
							"width" : 160,
							"height" : 24,
							"children" :
							[
								{
									"name" : "ui_bg_aftertext_text",
									"type" : "text",
									"x" : -50,
									"y" : 6,
									"text" : "",
									"horizontal_align" : "center",
									"text_horizontal_align" : "left",
								},
							],
						},
					],
				},
				{
					"name" : "ui_tax_button",
					"type" : "button",
					"x" : 0,
					"y" : 8 + ELEMENT_BASE_Y + (ELEMENT_Y_DIF * 3) + 18,
					"horizontal_align" : "center",
					"tooltip_text": localeinfo.OFFLINESHOP_TAX_TOOLTIP,
					"default_image" : "cream/shopseller/tax_button.png",
					"over_image" : "cream/shopseller/tax_button_hover.png",
					"down_image" : "cream/shopseller/tax_button_down.png",
				},
				{
					"name" : "ui_input_bg",
					"type" : "expanded_image",
					"x" : 0,
					"y" : 8 + ELEMENT_BASE_Y + (ELEMENT_Y_DIF * 3) + (28 * 2),
					"image" : "cream/shopseller/price.png",
					"horizontal_align" : "center",
					"children" :
					[
						{
							"name" : "ui_input_value",
							"type" : "editline",
							"x" : 26,
							"y" : 6,
							"width" : 160,
							"height" : 19,
							"input_limit" : 11,
							#"only_number" : 1,
							"horizontal_align" : "center",
						},
					],
				},
				{
					"name" : "ui_board_option1",
					"type" : "window",
					"x" : 0,
					"y" : 8 + ELEMENT_BASE_Y + (ELEMENT_Y_DIF * 6) + (28 * 2) + EXTRA_Y,
					"width" : 187,
					"height" : 18,
					"horizontal_align" : "center",
					"children" :
					[
						{
							"name" : "ui_board_option1_tick",
							"type" : "radio_button",
							"x" : 0,
							"y" : 0,
							"default_image" : "cream/shopseller/box_uncheck.png",
							"over_image" : "cream/shopseller/box_checked.png",
							"down_image" : "cream/shopseller/box_checked.png",
						},
						{
							"name" : "ui_board_option1_desc",
							"type" : "text",
							"x" : DESC_BASE_X,
							"y" : 0,
							"text" : "",
						},
					],
				},
				{
					"name" : "ui_board_option2",
					"type" : "window",
					"x" : 0,
					"y" : 8 + ELEMENT_BASE_Y + (ELEMENT_Y_DIF * 8) + (28 * 2) + EXTRA_Y,
					"width" : 187,
					"height" : 18,
					"horizontal_align" : "center",
					"children" :
					[
						{
							"name" : "ui_board_option2_tick",
							"type" : "toggle_button",
							"x" : 0,
							"y" : 0,
							"default_image" : "cream/shopseller/box_uncheck.png",
							"over_image" : "cream/shopseller/box_checked.png",
							"down_image" : "cream/shopseller/box_checked.png",
						},
						{
							"name" : "ui_board_option2_desc",
							"type" : "text",
							"x" : DESC_BASE_X,
							"y" : 0,
							"text" : localeinfo.OFFLINESHOP_OPTION2_DESC,
						},
					],
				},
				{
					"name" : "ui_board_option3",
					"type" : "window",
					"x" : 0,
					"y" : 8 + ELEMENT_BASE_Y + (ELEMENT_Y_DIF * 10) + (28 * 2) + EXTRA_Y,
					"width" : 187,
					"height" : 18,
					"horizontal_align" : "center",
					"children" :
					[
						{
							"name" : "ui_board_option3_tick",
							"type" : "toggle_button",
							"x" : 0,
							"y" : 0,
							"default_image" : "cream/shopseller/box_uncheck.png",
							"over_image" : "cream/shopseller/box_checked.png",
							"down_image" : "cream/shopseller/box_checked.png",
						},
						{
							"name" : "ui_board_option3_desc",
							"type" : "text",
							"x" : DESC_BASE_X,
							"y" : 0,
							"text" : localeinfo.OFFLINESHOP_OPTION3_DESC,
						},
					],
				},
				{
					"name" : "ui_board_option4",
					"type" : "window",
					"x" : 0,
					"y" : 8 + ELEMENT_BASE_Y + (ELEMENT_Y_DIF * 12) + (28 * 2) + EXTRA_Y,
					"width" : 187,
					"height" : 18,
					"horizontal_align" : "center",
					"children" :
					[
						{
							"name" : "ui_board_option4_tick",
							"type" : "toggle_button",
							"x" : 0,
							"y" : 2,
							"default_image" : "cream/shopseller/box_uncheck.png",
							"over_image" : "cream/shopseller/box_checked.png",
							"down_image" : "cream/shopseller/box_checked.png",
						},
						{
							"name" : "ui_board_option4_slotbar",
							"type" : "slotbar",
							"x" : DESC_BASE_X,
							"y" : 0,
							"width" : 24,
							"height" : 18,
							"children" :
							[
								{
									"name" : "ui_board_option4_input",
									"type" : "editline",
									"x" : 3,
									"y" : 3,
									"width" : 24,
									"height" : 18,
									"input_limit" : 3,
									"only_number" : 1,
									"text" : "0",
								},
							],
						},
						{
							"name" : "ui_board_option4_desc",
							"type" : "text",
							"x" : 18 + 24 + 10,
							"y" : 2,
							"text" : localeinfo.OFFLINESHOP_OPTION4_DESC,
						},
					],
				},
				{
					"name" : "ui_itemboard_title",
					"type" : "text",
					"x" : 0,
					"y" : BOARD_HEIGHT - 64 - (ELEMENT_Y_DIF * 3) - 110,
					"text" : "",
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
				},
				{
					"name" : "ui_board_sell",
					"type" : "expanded_image",
					"x" : 0,
					"y" : BOARD_HEIGHT - 64 - (ELEMENT_Y_DIF * 2) - 110 + 7,
					"image" : "cream/shopseller/bg_item.png",
					"horizontal_align" : "center",
					"children" :
					[
						{
							"name" : "ui_board_sell_icon",
							"type" : "expanded_image",
							"x" : 0,
							"y" : 0,
							"width" : 32,
							"height": 96,
							"image" : "icon/item/money.tga",
							"horizontal_align" : "center",
							"vertical_align" : "center",
						},
					],
				},
				{
					"name" : "ui_average_price",
					"type" : "text",
					"x" : 0,
					"y" : BOARD_HEIGHT - 64 - ELEMENT_Y_DIF,
					"text" : "...",
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
				},
				{
					"name" : "ui_accept_btn",
					"type" : "button",
					"x" : -54,
					"y" : BOARD_HEIGHT - 50,
					"horizontal_align" : "center",
					"text" : localeinfo.OFFLINESHOP_OK,
					"default_image" : "cream/shopseller/btn_norm.png",
					"over_image" : "cream/shopseller/btn_hover.png",
					"down_image" : "cream/shopseller/btn_down.png",
				},
				{
					"name" : "ui_cancel_btn",
					"type" : "button",
					"x" : 50,
					"y" : BOARD_HEIGHT - 50,
					"horizontal_align" : "center",
					"text" : localeinfo.OFFLINESHOP_NO,
					"default_image" : "cream/shopseller/btn_norm.png",
					"over_image" : "cream/shopseller/btn_hover.png",
					"down_image" : "cream/shopseller/btn_down.png",
				},
			],
		},
	],
}
