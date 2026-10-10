# coding: latin_1

import uiscriptlocale

BUTTON_WIDTH = 34
BUTTON_HEIGHT = 34
BUTTON_SPACING = 32

window = {
	"name" : "EquipmentTabWindow",
	"style" : ("float",),
	"x" : 0,
	"y" : 0,
	"width" : BUTTON_WIDTH,
	"height" : BUTTON_HEIGHT * 4 + BUTTON_SPACING,
	"children" :
	(
		{
			"name" : "Equipment_Tab_0",
			"type" : "radio_button",
			"x" : 0,
			"y" : 0,
			"tooltip_text" : uiscriptlocale.NEW_INV_PAGE_1,
			"default_image" : "d:/ymir work/ui/game/new_sinv/tab1_active.png",
			"over_image" : "d:/ymir work/ui/game/new_sinv/tab1_hover.png",
			"down_image" : "d:/ymir work/ui/game/new_sinv/tab1_clicked.png",
		},
		{
			"name" : "Equipment_Tab_1",
			"type" : "radio_button",
			"x" : 0,
			"y" : BUTTON_SPACING * 1,
			"tooltip_text" : uiscriptlocale.NEW_INV_PAGE_2,
			"default_image" : "d:/ymir work/ui/game/new_sinv/tab2_active.png",
			"over_image" : "d:/ymir work/ui/game/new_sinv/tab2_hover.png",
			"down_image" : "d:/ymir work/ui/game/new_sinv/tab2_clicked.png",
		},
		{
			"name" : "Equipment_Tab_2",
			"type" : "radio_button",
			"x" : 0,
			"y" : BUTTON_SPACING * 2,
			"tooltip_text" : uiscriptlocale.NEW_INV_PAGE_3,
			"default_image" : "d:/ymir work/ui/game/new_sinv/tab4_active.png",
			"over_image" : "d:/ymir work/ui/game/new_sinv/tab4_hover.png",
			"down_image" : "d:/ymir work/ui/game/new_sinv/tab4_clicked.png",
		},
		{
			"name" : "Equipment_Tab_3",
			"type" : "radio_button",
			"x" : 0,
			"y" : BUTTON_SPACING * 3,
			"tooltip_text" : uiscriptlocale.NEW_INV_PAGE_4,
			"default_image" : "d:/ymir work/ui/game/new_sinv/tab3_active.png",
			"over_image" : "d:/ymir work/ui/game/new_sinv/tab3_hover.png",
			"down_image" : "d:/ymir work/ui/game/new_sinv/tab3_clicked.png",
		},
	),
}
