import uiscriptlocale

if ENABLE_SORT_INVENTORY:
	SORT_X_ADJUST = 38
	SORT_TITLE_X_ADJUST = 20
else:
	SORT_X_ADJUST = 0
	SORT_TITLE_X_ADJUST = 0
ROOT_PATH = "d:/ymir work/ui/game/inv_manage/"
window = {
	"name" : "SpecialInventoryWindow",

	# "x" : 100,
	# "y" : 20,

	"x" : SCREEN_WIDTH - 176 - 287 - 10,
	"y" : SCREEN_HEIGHT - 37 - 525,

	"style" : ("movable", "float",),

	"width" : 176,
	"height" : 395 + 10+30,

	"children" :
	(
		{
			"name" : "ui_board",
			"type" : "board",

			"x" : 0,
			"y" : 0,

			"width" : 176,
			"height" : 395 + 10+30,

			"children" :
			(
				## Separate
				{
					"name" : "SeparateBaseImage",
					"type" : "image",
					"style" : ("attach",),
				
					"x" : 8,
					"y" : 7,
				
					"image" : "d:/ymir work/ui/pattern/titlebar_inv_refresh_baseframe.tga",
				
					"children" :
					(
						## Separate Button (38x24)
						{
							"name" : "SortInventoryButton",
							"type" : "button",
				
							"x" : 0,
							"y" : 0,
				
							"tooltip_text" : uiscriptlocale.INVENTORY_ITEM_SORT_TOOLTIP,
							"tooltip_x" : 0,
							"tooltip_y" : -23,
							"default_image" : ROOT_PATH + "btn-settings-1.png",
							"over_image" : ROOT_PATH + "btn-settings-2.png",
							"down_image" : ROOT_PATH + "btn-settings-3.png",
							#"disable_image" : "d:/ymir work/ui/game/inventory/refresh_small_button_04.sub",
						},
					),
				},

				## Title
				{
					"name" : "TitleBar",
					"type" : "titlebar",
					"style" : ("attach",),

					"x" : 8 + SORT_X_ADJUST,
					"y" : 7,

					"width" : 161 - SORT_X_ADJUST,

					"color" : "yellow",

					"children" :
					(
						{
							"name" : "TitleName",
							"type" : "text",

							"x" : 77 - SORT_TITLE_X_ADJUST,
							"y" : 3,

							"text" : uiscriptlocale.SPECIAL_INVENTORY_TITLE,
							"text_horizontal_align" : "center"
						},
					),
				},

				## Item Slot
				{
					"name" : "ItemSlot",
					"type" : "grid_table",

					"x" : 8,
					"y" : 35,

					"start_index" : 0,
					"x_count" : 5,
					"y_count" : 9,
					"x_step" : 32,
					"y_step" : 32,

					"image" : "d:/ymir work/ui/public/Slot_Base.sub"
				},

				{
					"name" : "Inventory_Tab_01",
					"type" : "radio_button",

					"x" : 6.5,
					"y" : 328,

					"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
					"tooltip_text" : uiscriptlocale.INVENTORY_PAGE_BUTTON_TOOLTIP_1,

					"children" :
					(
						{
							"name" : "Inventory_Tab_01_Print",
							"type" : "text",

							"x" : 0,
							"y" : 0,

							"all_align" : "center",

							"text" : "I",
						},
					),
				},
				{
					"name" : "Inventory_Tab_02",
					"type" : "radio_button",

					"x" : 6.5 + 32.5,
					"y" : 328,

					"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
					"tooltip_text" : uiscriptlocale.INVENTORY_PAGE_BUTTON_TOOLTIP_2,

					"children" :
					(
						{
							"name" : "Inventory_Tab_02_Print",
							"type" : "text",

							"x" : 0,
							"y" : 0,

							"all_align" : "center",

							"text" : "II",
						},
					),
				},
				{
					"name" : "Inventory_Tab_03",
					"type" : "radio_button",

					"x" : 6.5 + 32.5 + 32.5,
					"y" : 328,

					"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
					"tooltip_text" : uiscriptlocale.INVENTORY_PAGE_BUTTON_TOOLTIP_3,

					"children" :
					(
						{
							"name" : "Inventory_Tab_03_Print",
							"type" : "text",

							"x" : 0,
							"y" : 0,

							"all_align" : "center",

							"text" : "III",
						},
					),
				},
				{
					"name" : "Inventory_Tab_04",
					"type" : "radio_button",

					"x" : 6.5 + 32.5 + 32.5 + 32.5,
					"y" : 328,

					"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
					"tooltip_text" : uiscriptlocale.INVENTORY_PAGE_BUTTON_TOOLTIP_4,

					"children" :
					(
						{
							"name" : "Inventory_Tab_04_Print",
							"type" : "text",

							"x" : 0,
							"y" : 0,

							"all_align" : "center",

							"text" : "IV",
						},
					),
				},
				{
					"name" : "Inventory_Tab_05",
					"type" : "radio_button",

					"x" : 6.5 + 32.5 + 32.5 + 32.5 + 32.5,
					"y" : 328,

					"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
					"tooltip_text" : uiscriptlocale.INVENTORY_PAGE_BUTTON_TOOLTIP_5,

					"children" :
					(
						{
							"name" : "Inventory_Tab_05_Print",
							"type" : "text",

							"x" : 0,
							"y" : 0,

							"all_align" : "center",

							"text" : "V",
						},
					),
				},

				## Button
				{
					"name" : "SkillBookButton",
					"type" : "radio_button",

					"x" : 10,
					"y" : 47+37,

					"tooltip_text" : uiscriptlocale.SPECIAL_INVENTORY_SKILL_BOOK_TOOLTIP,
					"vertical_align" : "bottom",

					"default_image" : "d:/ymir work/ui/game/new_sinv/btn_skillbook_active.png",
					"over_image" : "d:/ymir work/ui/game/new_sinv/btn_skillbook_hover.png",
					"down_image" : "d:/ymir work/ui/game/new_sinv/btn_skillbook_active.png",
				},

				{
					"name" : "UpgradeItemsButton",
					"type" : "radio_button",

					"x" : 20 + 32.5,
					"y" : 47+37,

					"tooltip_text" : uiscriptlocale.SPECIAL_INVENTORY_MATERIAL_TOOLTIP,
					"vertical_align" : "bottom",

					"default_image" : "d:/ymir work/ui/game/new_sinv/btn_items_active.png",
					"over_image" : "d:/ymir work/ui/game/new_sinv/btn_items_hover.png",
					"down_image" : "d:/ymir work/ui/game/new_sinv/btn_items_active.png",
				},

				{
					"name" : "StoneButton",
					"type" : "radio_button",

					"x" : 20 + 70,
					"y" : 47+37,

					"tooltip_text" : uiscriptlocale.SPECIAL_INVENTORY_STONE_TOOLTIP,
					"vertical_align" : "bottom",

					"default_image" : "d:/ymir work/ui/game/new_sinv/btn_stones_active.png",
					"over_image" : "d:/ymir work/ui/game/new_sinv/btn_stones_hover.png",
					"down_image" : "d:/ymir work/ui/game/new_sinv/btn_stones_active.png",
				},

				{
					"name" : "GiftBoxButton",
					"type" : "radio_button",

					"x" : 20 + 110,
					"y" : 47+37,

					"tooltip_text" : uiscriptlocale.SPECIAL_INVENTORY_CHEST_TOOLTIP,
					"vertical_align" : "bottom",

					"default_image" : "d:/ymir work/ui/game/new_sinv/btn_safebox_active.png",
					"over_image" : "d:/ymir work/ui/game/new_sinv/btn_safebox_hover.png",
					"down_image" : "d:/ymir work/ui/game/new_sinv/btn_safebox_active.png",
				},
				{
					"name" : "SwitcherButton",
					"type" : "radio_button",

					"x" : 20 + 32.5,
					"y" : 45,

					"tooltip_text" : uiscriptlocale.SPECIAL_INVENTORY_SWITCHER_TOOLTIP,
					"vertical_align" : "bottom",

					"default_image" : "d:/ymir work/ui/game/new_sinv/btn_enchant_active.png",
					"over_image" : "d:/ymir work/ui/game/new_sinv/btn_enchant_hover.png",
					"down_image" : "d:/ymir work/ui/game/new_sinv/btn_enchant_active.png",
				},
				{
					"name" : "PotsButton",
					"type" : "radio_button",

					"x" : 20 + 70,
					"y" : 45,

					"tooltip_text" : uiscriptlocale.SPECIAL_INVENTORY_POTS_TOOLTIP,
					"vertical_align" : "bottom",

					"default_image" : "d:/ymir work/ui/game/new_sinv/btn_potions_active.png",
					"over_image" : "d:/ymir work/ui/game/new_sinv/btn_potions_hover.png",
					"down_image" : "d:/ymir work/ui/game/new_sinv/btn_potions_active.png",
				},
				
			),
		},
	),
}