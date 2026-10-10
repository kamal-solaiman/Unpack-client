# coding: latin_1

import uiscriptlocale
import item

window = {
	"name" : "CostumeWindow",

	"x" : SCREEN_WIDTH - 175 - 140,
	"y" : SCREEN_HEIGHT - 37 - 565,

	"style" : ("movable", "float",),

	#"width" : 113+27,
	#"height" : (176 + 51),

	"width" : 226+27,
	"height" : (235 - 0),
	"children" :
	(
		{
			"name" : "board",
			"type" : "board",
			"style" : ("attach",),

			"x" : 0,
			"y" : 0,

			#"width" : 140,
			#"height" : (180 + 47),
			
			"width" : 226+27,
			"height" : (235 + 0),
			
			"children" :
			(
				## Title
				{
					"name" : "TitleBar",
					"type" : "titlebar",
					"style" : ("attach",),

					"x" : 6,
					"y" : 6,

					#"width" : 130,
					"width" : 226+27-10,
					"color" : "yellow",

					"children" :
					(
						{ "name":"TitleName", "type":"text", "x":60+50, "y":3, "text":uiscriptlocale.COSTUME_WINDOW_TITLE, "text_horizontal_align":"center" },
					),
				},

				## Equipment Slot
				{
					"name" : "Costume_Base",
					"type" : "image",

					"x" : 13-4,
					"y" : 38-8,

					"image" : uiscriptlocale.LOCALE_UISCRIPT_PATH + "costume/costume.tga",

					"children" :
					(
						{
							"name" : "Costume_Page",
							"type" : "window",
							"style" : ("attach",),

							"x" : 0,
							"y" : 0,

							#"width" : 127,
							"width" : 226+27-13,
							"height" : 235-5,

							"children" :
							(
							{
								"name" : "CostumeSlot",
								"type" : "slot",

								"x" : 0,
								"y" : 0,

								"width" : 226+27-13,
								"height" : 235-25,

								"slot" : (
									{"index":COSTUME_START_INDEX+0, "x":120-3-8 , "y":34+34+6, "width":32, "height":64},
									{"index":COSTUME_START_INDEX+1, "x":120-3-8, "y":34+6, "width":32, "height":32},
									{"index":COSTUME_START_INDEX+2, "x":160+25-8, "y":34+34+34+6, "width":32, "height":32},
									{"index":item.COSTUME_SLOT_ACCE, "x":160+25-8, "y":34+6, "width":32, "height":32},#¾Ç¼¼¼­¸®
									{"index":COSTUME_SLOT_WEAPON, "x":68-8, "y":35+6, "width":32, "height":96},#¹«±â
									{"index":item.EQUIPMENT_AURA, "x" : 160+25-8, "y" : 34+34+6, "width" : 32, "height" : 32 }, # ¿µ±â
									## shinings
									{"index":item.SHINING_SLOT_START+0, "x":68-30-8, "y":35+6, "width":32, "height":32},
									{"index":item.PENDANT_YOHARA_SLOT, "x":68-30-8, "y":35+30+6, "width":32, "height":32},
									#{"index":item.SHINING_SLOT_START+2, "x":68-30-8, "y":35+30+30+6, "width":32, "height":32},
									#Armor
									{"index":item.SHINING_SLOT_START+1, "x":120+30-8, "y":34+34+6, "width":32, "height":32},
									#{"index":item.SHINING_SLOT_START+4, "x":120+30-8, "y":34+34+30+6, "width":32, "height":32},
									#Special
									{"index":item.SHINING_SLOT_START+2, "x":120+30-8, "y":35+6, "width":32, "height":32},
									#item uniqu
									{"index":item.EQUIPMENT_UNIQUE1, "x":120-8, "y":34+34+30+40+6, "width":32, "height":32},#
									{"index":item.EQUIPMENT_UNIQUE2, "x":120+30-8, "y":34+34+30+40+6, "width":32, "height":32},
									{"index":item.WEAR_EX_THIEF_SLOT, "x":68-5, "y":34+34+30+40+4, "width":32, "height":32},
									{"index":item.WEAR_EX_RING_SLOT, "x":68-30-10, "y":34+34+30+40+4, "width":32, "height":32},

								),
							},
							),
						},

						## ENABLE_HIDE_COSTUME_SYSTEM
						{ "name" : "VisibleBodySlotImg", "type" : "expanded_image", "x" : 120-25+8, "y" : 70+6, "image" : "d:/ymir work/ui/game/costume/hideslot_02.tga" },
						{ "name" : "VisibleHairSlotImg", "type" : "expanded_image", "x" : 120-25+8, "y" : 35+6, "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{ "name" : "VisibleAcceSlotImg", "type" : "expanded_image", "x" : 35-10+8, "y" : 35+6, "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{ "name" : "VisibleAuraSlotImg", "type" : "expanded_image", "x" : 35-10+8, "y" : 35+6 + 35, "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{ "name" : "VisibleWeaponSlotImg", "type" : "expanded_image", "x" : 120+20+8, "y" : 35+5+6, "image" : "d:/ymir work/ui/game/costume/hideslot_03.tga" },

						## ENABLE_HIDE_COSTUME_SYSTEM
						{
							"name" : "BodyToolTipButton",
							"type" : "toggle_button",

							"x" : 55+28+10,
							"y" : 45+20+8,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/costume/eye_normal_01.tga",
							"over_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
							"down_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
						},
						{
							"name" : "HairToolTipButton",
							"type" : "toggle_button",

							"x" : 55+28+10,
							"y" : 13+15+8,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/costume/eye_normal_01.tga",
							"over_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
							"down_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
						},
						{
							"name" : "AcceToolTipButton",
							"type" : "toggle_button",

							"x" : 10+10,
							"y" : 13+15+8,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/costume/eye_normal_01.tga",
							"over_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
							"down_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
						},
						{
							"name" : "WeaponToolTipButton",
							"type" : "toggle_button",

							"x" : 55+70+10,
							"y" : 13+15+8,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/costume/eye_normal_01.tga",
							"over_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
							"down_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
						},
						{
							"name" : "AuraToolTipButton",
							"type" : "toggle_button",
							"x" : 10+10,
							"y" : 45+20+8,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,
							"default_image" : "d:/ymir work/ui/game/costume/eye_normal_01.tga",
							"over_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
							"down_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
						},
						## END_ENABLE_HIDE_COSTUME_SYSTEM

						## ENABLE_HIDE_SHINING_SYSTEM
						{ "name" : "VisibleShiningWeaponSlotImg",  "type" : "expanded_image", "x" : 68-30-8,  "y" : 35+6,    "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{ "name" : "VisibleShiningArmorSlotImg",   "type" : "expanded_image", "x" : 120+30-8, "y" : 34+34+6, "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },
						{ "name" : "VisibleShiningSpecialSlotImg", "type" : "expanded_image", "x" : 120+30-8, "y" : 35+6,    "image" : "d:/ymir work/ui/game/costume/hideslot_01.tga" },

						{
							"name" : "ShiningWeaponToolTipButton",
							"type" : "toggle_button",

							"x" : 68-30-8+18,
							"y" : 35+6+8,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/costume/eye_normal_01.tga",
							"over_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
							"down_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
						},
						{
							"name" : "ShiningArmorToolTipButton",
							"type" : "toggle_button",

							"x" : 120+30-8+18,
							"y" : 34+34+6+8,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/costume/eye_normal_01.tga",
							"over_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
							"down_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
						},
						{
							"name" : "ShiningSpecialToolTipButton",
							"type" : "toggle_button",

							"x" : 120+30-8+18,
							"y" : 35+6+8,
							"tooltip_text" : uiscriptlocale.HIDE_COSTUME,

							"default_image" : "d:/ymir work/ui/game/costume/eye_normal_01.tga",
							"over_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
							"down_image" : "d:/ymir work/ui/game/costume/eye_normal_02.tga",
						},
						## END_ENABLE_HIDE_SHINING_SYSTEM
					),
				},
			),
		},
	),
}