# coding: latin_1

import uiscriptlocale
import localeinfo
import item
import player

EQUIPMENT_START_INDEX = 0

if ENABLE_EXTEND_INVEN_SYSTEM:
	EQUIPMENT_START_INDEX = 180
else:
	EQUIPMENT_START_INDEX = 90

if ENABLE_SORT_INVENTORY:
	SORT_X_ADJUST = 38
	SORT_TITLE_X_ADJUST = 20
else:
	SORT_X_ADJUST = 0
	SORT_TITLE_X_ADJUST = 0
ROOT_PATH = "d:/ymir work/ui/game/inv_manage/"
EXTEND_Y = 0

window = {
	"name" : "InventoryWindow",
	"x" : SCREEN_WIDTH - 176,
	"y" : SCREEN_HEIGHT - 37 - 563 - EXTEND_Y,
	"style" : ("movable", "float",),
	"width" : 176,
	"height" : 563 - 22 + EXTEND_Y,
	"children" :
	(
		{
			"name" : "board",
			"type" : "board",
			"style" : ("attach",),
			"x" : 0,
			"y" : 0,
			"width" : 176,
			"height" : 563 - 22 + EXTEND_Y,
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
							"y" : 3-3,
				
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
				{
					"name" : "TitleBar",
					"type" : "titlebar",
					"style" : ("attach",),
					"x" : 8 + SORT_X_ADJUST,
					"y" : 7,
					"width" : 176 - 15 - SORT_X_ADJUST,
					"color" : "yellow",
					"children" :
					(
						{
							"name" : "TitleName",
							"type" : "text",
							"x" : 77 - SORT_TITLE_X_ADJUST,
							"y" : 3,
							"text" : uiscriptlocale.INVENTORY_TITLE,
							"text_horizontal_align" : "center"
						},
					),
				},
				
				
				{
					"name" : "Equipment_Base_Tab_0",
					"type" : "image",
					"x" : 10,
					"y" : 33,
					"image" : "d:/ymir work/ui/game/inventory/equipment_new_base.dds",
					"children" :
					(
						{
							"name" : "EquipmentSlot_0",
							"type" : "slot",
							"x" : 26,
							"y" : 3,
							"width" : 150,
							"height" : 182,
							"slot" : (
										{"index":EQUIPMENT_START_INDEX+0, "x":39, "y":38, "width":32, "height":64},#body
										{"index":EQUIPMENT_START_INDEX+1, "x":39, "y":2, "width":32, "height":32},#head
										{"index":EQUIPMENT_START_INDEX+2, "x":39, "y":142, "width":32, "height":32},#shoe
										{"index":EQUIPMENT_START_INDEX+3, "x":75, "y":67, "width":32, "height":32},#wrist
										{"index":EQUIPMENT_START_INDEX+4, "x":3, "y":3, "width":32, "height":96},#weapon
										{"index":EQUIPMENT_START_INDEX+5, "x":114, "y":67, "width":32, "height":32},#neck
										{"index":EQUIPMENT_START_INDEX+6, "x":114, "y":35, "width":32, "height":32},#ear
										#{"index":EQUIPMENT_START_INDEX+9, "x":114, "y":2, "width":32, "height":32},#arrow
										{"index":EQUIPMENT_START_INDEX+10, "x":75, "y":35, "width":32, "height":32},#shield
										{"index":EQUIPMENT_BELT, "x":40, "y":105, "width":32, "height":32},
										{"index":getattr(item, "EQUIPMENT_ACCE_SKIN", item.EQUIPMENT_AURA), "x":114, "y":2, "width":32, "height":32},
										{"index":item.COSTUME_SLOT_ACCE, "x":75, "y":2, "width":32, "height":32},
										{"index":item.WEAR_EX_THIEF_SLOT, "x":3, "y":105, "width":32, "height":32},#shoe1
										{"index":item.WEAR_EX_RING_SLOT, "x":75, "y":105, "width":32, "height":32},
										{"index":EQUIPMENT_GLOVE, "x":114, "y":105, "width":32, "height":32},

							),
						},
						{ "name" : "VisibleAuraSlotImg", "type" : "expanded_image", "x" : 75-28-28 -8, "y" : 2, "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{ "name" : "VisibleAcceSlotImg", "type" : "expanded_image", "x" : 75-28, "y" : 2, "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{
							"name" : "AcceToolTipButton",
							"type" : "toggle_button",

							"x" : 75-35,
							"y" : 2,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/btn_hide_01.png",
							"over_image" : "d:/ymir work/ui/game/btn_hide_02.png",
							"down_image" : "d:/ymir work/ui/game/btn_hide_02.png",
						},
						{
							"name" : "AuraToolTipButton",
							"type" : "toggle_button",
							"x" : 75-35-35-6,
							"y" : 2,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,
							"default_image" : "d:/ymir work/ui/game/btn_hide_01.png",
							"over_image" : "d:/ymir work/ui/game/btn_hide_02.png",
							"down_image" : "d:/ymir work/ui/game/btn_hide_02.png",
						},
						{
							"name" : "MallButton",
							"type" : "button",
							"x" : 8,
							"y" : 148,
							"tooltip_text" : uiscriptlocale.MALL_TITLE,
							"default_image" : "d:/ymir work/ui/game/new_sinv/storage_btn.png",
							"over_image" : "d:/ymir work/ui/game/new_sinv/storage_btn_over.png",
							"down_image" : "d:/ymir work/ui/game/new_sinv/storage_btn_down.png",
						},
						{
							"name" : "OfflineshopButton",
							"type" : "button",
							"x" : 47,
							"y" : 148,
							"tooltip_text" : uiscriptlocale.OFFLINESHOP_TITLE,
							"default_image" : "d:/ymir work/ui/game/new_sinv/shop_btn.png",
							"over_image" : "d:/ymir work/ui/game/new_sinv/shop_btn_over.png",
							"down_image" : "d:/ymir work/ui/game/new_sinv/shop_btn_down.png",
						},
						{
							"name" : "ExchangelogButton",
							"type" : "button",
							"x" : 3 + 30 + 8+ 30 + 8+ 30 + 8,
							"y" : 147,
							"tooltip_text" : localeinfo.BIOLOG_MANAGER_TITLE,
							"default_image" : "d:/ymir work/ui/game/special_inventory/bio_1.tga",
							"over_image" : "d:/ymir work/ui/game/special_inventory/bio_2.tga",
							"down_image" : "d:/ymir work/ui/game/special_inventory/bio_3.tga",
						},
						# {
							# "name" : "BioButton",
							# "type" : "button",
							# "x" : 3 + 30 + 8+ 30 + 8+ 30 + 8,
							# "y" : 147,
							# "tooltip_text" : localeinfo.BIOLOG_MANAGER_TITLE,
							# "default_image" : "d:/ymir work/ui/game/special_inventory/bio_1.tga",
							# "over_image" : "d:/ymir work/ui/game/special_inventory/bio_2.tga",
							# "down_image" : "d:/ymir work/ui/game/special_inventory/bio_3.tga",
						# },
						{
							"name" : "Equipment_Tab_01",
							"type" : "radio_button",
							"x" : 86,
							"y" : 161,
							"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
							"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
							"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
							"children" :
							(
								{
									"name" : "Equipment_Tab_01_Print",
									"type" : "text",
									"x" : 0,
									"y" : 0,
									"all_align" : "center",
									"text" : "I",
								},
							),
						},
						{
							"name" : "Equipment_Tab_02",
							"type" : "radio_button",
							"x" : 86 + 32,
							"y" : 161,
							"default_image" : "d:/ymir work/ui/game/windows/tab_button_small_01.sub",
							"over_image" : "d:/ymir work/ui/game/windows/tab_button_small_02.sub",
							"down_image" : "d:/ymir work/ui/game/windows/tab_button_small_03.sub",
							"children" :
							(
								{
									"name" : "Equipment_Tab_02_Print",
									"type" : "text",
									"x" : 0,
									"y" : 0,
									"all_align" : "center",
									"text" : "II",
								},
							),
						},

					),
				},
				{
					"name" : "Equipment_Base_Tab_1",
					"type" : "image",
					"style" : ("attach","ltr",),
					"x" : 10,
					"y" : 33,
					"image" : "d:/ymir work/ui/game/inventory/equipment_new_costume.dds",
					"children" :
					(
						{
							"name" : "EquipmentSlot_1",
							"type" : "slot",
							"x" : 26,
							"y" : 3,
							"width" : 150,
							"height" : 182,
							"slot" : ( 
									{"index":COSTUME_START_INDEX+0, "x":55 , "y":68, "width":32, "height":64},
									{"index":COSTUME_START_INDEX+1, "x":58, "y":29, "width":32, "height":32},
									{"index":COSTUME_START_INDEX+2, "x":106, "y":53, "width":32, "height":32},#mount
									{"index":EQUIPMENT_START_INDEX+9, "x":106, "y":53 - 40, "width":32, "height":32},#arrow
									{"index":COSTUME_SLOT_WEAPON, "x":8, "y":10, "width":32, "height":96},#����
									{"index":item.EQUIPMENT_UNIQUE1, "x":106, "y":40+40+15, "width":32, "height":32},#
									{"index":item.EQUIPMENT_UNIQUE2, "x":106, "y":40+40+15 + 40, "width":32, "height":32},

									{"index":item.EQUIPMENT_RING1, "x":55, "y":40+40+25 + 40, "width":32, "height":32},#
									{"index":item.EQUIPMENT_RING2, "x":10, "y":40+40+25 + 40, "width":32, "height":32},


							),
						},
						{ "name" : "VisibleBodySlotImg", "type" : "expanded_image", "x" : 120-25-15+3, "y" : 70+6, "image" : "d:/ymir work/ui/game/costume/hideslot_02.tga" },
						{ "name" : "VisibleHairSlotImg", "type" : "expanded_image", "x" : 120-25-15+3, "y" : 35+6-10, "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{ "name" : "VisibleWeaponSlotImg", "type" : "expanded_image", "x" : 10+25, "y" : 10+5, "image" : "d:/ymir work/ui/game/costume/hideslot_03.tga" },
						{
							"name" : "BodyToolTipButton",
							"type" : "toggle_button",

							"x" : 55+28+10+10,
							"y" : 45+20+3,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/btn_hide_01.png",
							"over_image" : "d:/ymir work/ui/game/btn_hide_02.png",
							"down_image" : "d:/ymir work/ui/game/btn_hide_02.png",
						},
						{
							"name" : "HairToolTipButton",
							"type" : "toggle_button",

							"x" : 55+28+10+10,
							"y" : 13+15,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/btn_hide_01.png",
							"over_image" : "d:/ymir work/ui/game/btn_hide_02.png",
							"down_image" : "d:/ymir work/ui/game/btn_hide_02.png",
						},
						{
							"name" : "WeaponToolTipButton",
							"type" : "toggle_button",

							"x" : 10+50,
							"y" : 10,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/btn_hide_01.png",
							"over_image" : "d:/ymir work/ui/game/btn_hide_02.png",
							"down_image" : "d:/ymir work/ui/game/btn_hide_02.png",
						},
					),
				},
				{
					"name" : "Equipment_Base_Tab_2",
					"type" : "image",
					"style" : ("attach", "ltr",),
					"x" : 10,
					"y" : 33,
					"image" : "d:/ymir work/ui/game/inventory/equipment_new_buffi.dds",
					"children" :
					(
						{
							"name" : "EquipmentSlot_2",
							"type" : "slot",
							"x" : 26,
							"y" : 3,
							"width" : 150,
							"height" : 182,
							"slot" : (
									## shinings
									{"index":item.SHINING_SLOT_START+0, "x":21, "y":35+27, "width":32, "height":32},
									#{"index":item.SHINING_SLOT_START+1, "x":30, "y":18+35, "width":32, "height":32},
									#{"index":item.SHINING_SLOT_START+2, "x":30, "y":16+35+35, "width":32, "height":32},
									#Armor
									{"index":item.SHINING_SLOT_START+1, "x":98, "y":35+26, "width":32, "height":32},
									#{"index":item.PENDANT_YOHARA_SLOT, "x":22, "y":36+36+36+24, "width":32, "height":32},
									#Special
									{"index":item.SHINING_SLOT_START+2, "x":59, "y":22, "width":32, "height":32},
									{ "index" : player.EQUIPMENT_SLOT_START + player.WEAR_PET_SKIN, "x" : 22, "y" : 36+36+36+24, "width" : 32, "height" : 32},
									{ "index" : player.EQUIPMENT_SLOT_START + player.WEAR_MOUNT_SKIN, "x" : 96, "y" : 36+36+36+24, "width" : 32, "height" : 32},
							),
						},
						## ENABLE_HIDE_SHINING_SYSTEM
						{ "name" : "VisibleShiningWeaponSlotImg",  "type" : "expanded_image", "x" : 26+21, "y" : 3+35+27, "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{ "name" : "VisibleShiningArmorSlotImg",   "type" : "expanded_image", "x" : 26+98, "y" : 3+35+26, "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{ "name" : "VisibleShiningSpecialSlotImg", "type" : "expanded_image", "x" : 26+59, "y" : 3+22,    "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },

						{
							"name" : "ShiningWeaponToolTipButton",
							"type" : "toggle_button",

							"x" : 26+21+18,
							"y" : 3+35+27+8 - 13,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/btn_hide_01.png",
							"over_image" : "d:/ymir work/ui/game/btn_hide_02.png",
							"down_image" : "d:/ymir work/ui/game/btn_hide_02.png",
						},
						{
							"name" : "ShiningArmorToolTipButton",
							"type" : "toggle_button",

							"x" : 26+98+18,
							"y" : 3+35+26+8 - 13,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/btn_hide_01.png",
							"over_image" : "d:/ymir work/ui/game/btn_hide_02.png",
							"down_image" : "d:/ymir work/ui/game/btn_hide_02.png",
						},
						{
							"name" : "ShiningSpecialToolTipButton",
							"type" : "toggle_button",

							"x" : 26+59+18,
							"y" : 3+22+8 - 13,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/btn_hide_01.png",
							"over_image" : "d:/ymir work/ui/game/btn_hide_02.png",
							"down_image" : "d:/ymir work/ui/game/btn_hide_02.png",
						},
						## END_ENABLE_HIDE_SHINING_SYSTEM
						{ "name" : "VisibleMountSkinSlotImg", "type" : "expanded_image", "x" : 96 + 28, "y" : 36+36+36+28, "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{ "name" : "VisiblePetSkinSlotImg", "type" : "expanded_image", "x" : 35 + 16, "y" : 36+36+36+28, "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{
							"name" : "MountSkinToolTipButton",
							"type" : "toggle_button",

							"x" : 104 + 35 + 5,
							"y" : 36+36+36+20,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/btn_hide_01.png",
							"over_image" : "d:/ymir work/ui/game/btn_hide_02.png",
							"down_image" : "d:/ymir work/ui/game/btn_hide_02.png",
						},
						{
							"name" : "PetSkinToolTipButton",
							"type" : "toggle_button",
							"x" : 35+35+2,
							"y" : 36+36+36+20,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,
							"default_image" : "d:/ymir work/ui/game/btn_hide_01.png",
							"over_image" : "d:/ymir work/ui/game/btn_hide_02.png",
							"down_image" : "d:/ymir work/ui/game/btn_hide_02.png",
						},
					),
				},
				{
					"name" : "Equipment_Base_Tab_3",
					"type" : "image",
					"style" : ("attach","ltr",),
					"x" : 10,
					"y" : 33,
					"image" : "d:/ymir work/ui/game/inventory/equipment_new_pendants.dds",
					"children" :
					(

						{
							"name" : "EquipmentSlot_3",
							"type" : "slot",
							"x" : 26,
							"y" : 3,
							"width" : 150,
							"height" : 182,
							"slot" : (),
						},
						{
							"name" : "pendant_page_0",
							"type" : "radio_button",
							"x" : 26+9,
							"y" : 3+109+10+25,
							"default_image" : "d:/ymir work/ui/game/inventory/talisman1-icon-1.png",
							"over_image" : "d:/ymir work/ui/game/inventory/talisman1-icon-2.png",
							"down_image" : "d:/ymir work/ui/game/inventory/talisman1-icon-3.png",
						},
						{
							"name" : "pendant_page_1",
							"type" : "radio_button",
							"x" : 26+110,
							"y" : 3+109+10+25,
							"default_image" : "d:/ymir work/ui/game/inventory/talisman2-icon-1.png",
							"over_image" : "d:/ymir work/ui/game/inventory/talisman2-icon-2.png",
							"down_image" : "d:/ymir work/ui/game/inventory/talisman2-icon-3.png",
						},
					),
				},
				# {
					# "name" : "extra_btn_0_element",
					# "type" : "button",
					# "x" : 3+8,
					# "y" : 147 + 32 + 6 +37,
					# "tooltip_text" : uiscriptlocale.SPECIAL_INVENTORY_SKILL_BOOK_TOOLTIP,
					# "default_image" : "d:/ymir work/ui/game/special_inventory/skill_book_1.tga",
					# "over_image" : "d:/ymir work/ui/game/special_inventory/skill_book_2.tga",
					# "down_image" : "d:/ymir work/ui/game/special_inventory/skill_book_3.tga",
				# },
				# {
					# "name" : "extra_btn_1_element",
					# "type" : "button",
					# "x" : 3 + 30 + 8+8,
					# "y" : 147 + 32 + 6 +36,
					# "tooltip_text" : uiscriptlocale.SPECIAL_INVENTORY_MATERIAL_TOOLTIP,
					# "default_image" : "d:/ymir work/ui/game/special_inventory/material_1.tga",
					# "over_image" : "d:/ymir work/ui/game/special_inventory/material_2.tga",
					# "down_image" : "d:/ymir work/ui/game/special_inventory/material_3.tga",
				# },
				# {
					# "name" : "extra_btn_2_element",
					# "type" : "button",
					# "x" : 3 + 30 + 8+ 30 + 8+8,
					# "y" : 147 + 32 + 6 +37,
					# "tooltip_text" : uiscriptlocale.SPECIAL_INVENTORY_STONE_TOOLTIP,
					# "default_image" : "d:/ymir work/ui/game/special_inventory/stone_1.tga",
					# "over_image" : "d:/ymir work/ui/game/special_inventory/stone_2.tga",
					# "down_image" : "d:/ymir work/ui/game/special_inventory/stone_3.tga",
				# },
				# {
					# "name" : "extra_btn_3_element",
					# "type" : "button",
					# "x" : 3 + 30 + 8+ 30 + 8+ 30 + 8+8,
					# "y" : 147 + 32 + 6 +37,
					# "tooltip_text" : uiscriptlocale.SPECIAL_INVENTORY_CHEST_TOOLTIP,
					# "default_image" : "d:/ymir work/ui/game/special_inventory/chest_1.tga",
					# "over_image" : "d:/ymir work/ui/game/special_inventory/chest_2.tga",
					# "down_image" : "d:/ymir work/ui/game/special_inventory/chest_3.tga",
				# },
				{
					"name" : "Inventory_Tab_01",
					"type" : "radio_button",
					"x" : 10,
					"y" : 33 + 189 + EXTEND_Y,
					"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_03.sub",
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
					"x" : 10 + 39,
					"y" : 33 + 189 + EXTEND_Y,
					"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_03.sub",
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
					"x" : 10 + 39 + 39,
					"y" : 33 + 189 + EXTEND_Y,
					"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_03.sub",
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
					"x" : 10 + 39 + 39 + 39,
					"y" : 33 + 189 + EXTEND_Y,
					"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_half_03.sub",
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
					"name" : "ItemSlot",
					"type" : "grid_table",
					"x" : 8,
					"y" : 244 + EXTEND_Y,
					"start_index" : 0,
					"x_count" : 5,
					"y_count" : 9,
					"x_step" : 32,
					"y_step" : 32,
					"image" : "d:/ymir work/ui/public/Slot_Base.sub"
				},
			),
		},
	),
}
