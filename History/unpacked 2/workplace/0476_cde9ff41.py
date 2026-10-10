# coding: latin_1

import uiScriptLocale
import localeinfo

ROOT_PATH = "d:/ymir work/ui/public/"
ROOT_PATH2 = "d:/ymir work/ui/"
ROOT_PATH3 = "d:/ymir work/interface/inventory/inventory_buttons/"

TEMPORARY_X = +13
TEXT_TEMPORARY_X = -10
BUTTON_TEMPORARY_X = 5
PVP_X = -10

window = {
	"name" : "SystemOptionDialog",
	"style" : ("movable", "float",),

	"x" : 0,
	"y" : 0,

	"width" : 390,
	"height" : 350,

	"children" :
	(
		{
			"name" : "board",
			"type" : "board",

			"x" : 0,
			"y" : 0,

			"width" : 390,
			"height" : 350,

			"children" :
			(
				## Title
				{
					"name" : "titlebar",
					"type" : "titlebar",
					"style" : ("attach",),

					"x" : 2,
					"y" : 8,

					"width" : 383,
					"color" : "gray",

					"children" :
					(
						{ 
						"name":"titlename", "type":"text", "x":0, "y":3, 
						"horizontal_align":"center", "text_horizontal_align":"center",
						"text" : localeinfo.SKY_TITLE,
						 },
					),
				},
########################################################################### ARKA PLAN ##########################################################################
				#{
				#	"name" : "maviruh_board1",
				#	"type" : "thinboard",

				#	"x" : 9,
				#	"y" : 37,

				#	"width" : 500,
				#	"height" : 80,
				#},
				#{
				#	"name" : "maviruh_board2",
				#	"type" : "thinboard",

				#	"x" : 9,
				#	"y" : 117,

				#	"width" : 500,
				#	"height" : 80,
				#},
				#{
				#	"name" : "maviruh_board3",
				#	"type" : "thinboard",

				#	"x" : 9,
				#	"y" : 197,

				#	"width" : 500,
				#	"height" : 80,
				#},
########################################################################### ARKA PLAN ##########################################################################

########################################################################### 1. SAYFA ###########################################################################
				{
					"name" : "maviruh",
					"type" : "button",
					"style" : ("attach",),
					"x" : 9,
					"y" : 37,
					"width" : 520,
					"height" : 290,
					#"image" : "fake.tga",
					"children" :
					(
						{
							"name" : "skyboxbutton10",
							"type" : "radio_button",

							"x" : 9,
							"y" : 6,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/1_1.tga",
							"over_image" : "skybox_system/1_2.tga",
							"down_image" : "skybox_system/1_3.tga",
						},
						{
							"name" : "skyboxbutton11",
							"type" : "radio_button",

							"x" : 9,
							"y" : 83,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/2_1.tga",
							"over_image" : "skybox_system/2_2.tga",
							"down_image" : "skybox_system/2_3.tga",
						},
						{
							"name" : "skyboxbutton3",
							"type" : "radio_button",

							"x" : 9,
							"y" : 160,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/3_1.tga",
							"over_image" : "skybox_system/3_2.tga",
							"down_image" : "skybox_system/3_3.tga",
						},
					),
				},
########################################################################### 1. SAYFA ###########################################################################

########################################################################### 2. SAYFA ###########################################################################
				{
					"name" : "maviruh2",
					"type" : "button",
					"style" : ("attach",),
					"x" : 9,
					"y" : 37,
					"width" : 520,
					"height" : 290,
					#"image" : "fake.tga",
					"children" :
					(
						{
							"name" : "skyboxbutton4",
							"type" : "radio_button",

							"x" : 9,
							"y" : 6,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/4_1.tga",
							"over_image" : "skybox_system/4_2.tga",
							"down_image" : "skybox_system/4_3.tga",
						},
						{
							"name" : "skyboxbutton5",
							"type" : "radio_button",

							"x" : 9,
							"y" : 83,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/5_1.tga",
							"over_image" : "skybox_system/5_2.tga",
							"down_image" : "skybox_system/5_3.tga",
						},
						{
							"name" : "skyboxbutton6",
							"type" : "radio_button",

							"x" : 9,
							"y" : 160,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/6_1.tga",
							"over_image" : "skybox_system/6_2.tga",
							"down_image" : "skybox_system/6_3.tga",
						},
					),
				},
########################################################################### 2. SAYFA ###########################################################################

########################################################################### 3. SAYFA ###########################################################################
				{
					"name" : "maviruh3",
					"type" : "button",
					"style" : ("attach",),
					"x" : 9,
					"y" : 37,
					"width" : 520,
					"height" : 290,
					#"image" : "fake.tga",
					"children" :
					(
						{
							"name" : "skyboxbutton7",
							"type" : "radio_button",

							"x" : 9,
							"y" : 6,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/7_1.tga",
							"over_image" : "skybox_system/7_2.tga",
							"down_image" : "skybox_system/7_3.tga",
						},
						{
							"name" : "skyboxbutton8",
							"type" : "radio_button",

							"x" : 9,
							"y" : 83,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/8_1.tga",
							"over_image" : "skybox_system/8_2.tga",
							"down_image" : "skybox_system/8_3.tga",
						},
						{
							"name" : "skyboxbutton9",
							"type" : "radio_button",

							"x" : 9,
							"y" : 160,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/9_1.tga",
							"over_image" : "skybox_system/9_2.tga",
							"down_image" : "skybox_system/9_3.tga",
						},
					),
				},
########################################################################### 3. SAYFA ###########################################################################

########################################################################### 4. SAYFA ###########################################################################
				{
					"name" : "maviruh4",
					"type" : "button",
					"style" : ("attach",),
					"x" : 9,
					"y" : 37,
					"width" : 520,
					"height" : 290,
					#"image" : "fake.tga",
					"children" :
					(
						{
							"name" : "skyboxbutton12",
							"type" : "radio_button",

							"x" : 9,
							"y" : 6,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/10_1.tga",
							"over_image" : "skybox_system/10_2.tga",
							"down_image" : "skybox_system/10_3.tga",
						},
						{
							"name" : "skyboxbutton13",
							"type" : "radio_button",

							"x" : 9,
							"y" : 83,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/11_1.tga",
							"over_image" : "skybox_system/11_2.tga",
							"down_image" : "skybox_system/11_3.tga",
						},
						{
							"name" : "skyboxbutton14",
							"type" : "radio_button",

							"x" : 9,
							"y" : 160,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/12_1.tga",
							"over_image" : "skybox_system/12_2.tga",
							"down_image" : "skybox_system/12_3.tga",
						},
					),
				},
########################################################################### 4. SAYFA ###########################################################################

########################################################################### 5. SAYFA ###########################################################################
				{
					"name" : "maviruh5",
					"type" : "button",
					"style" : ("attach",),
					"x" : 9,
					"y" : 37,
					"width" : 520,
					"height" : 290,
					#"image" : "fake.tga",
					"children" :
					(
						{
							"name" : "skyboxbutton15",
							"type" : "radio_button",

							"x" : 9,
							"y" : 6,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/13_1.tga",
							"over_image" : "skybox_system/13_2.tga",
							"down_image" : "skybox_system/13_3.tga",
						},
						{
							"name" : "skyboxbutton16",
							"type" : "radio_button",

							"x" : 9,
							"y" : 83,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/14_1.tga",
							"over_image" : "skybox_system/14_2.tga",
							"down_image" : "skybox_system/14_3.tga",
						},
						{
							"name" : "skyboxbutton17",
							"type" : "radio_button",

							"x" : 9,
							"y" : 160,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/15_1.tga",
							"over_image" : "skybox_system/15_2.tga",
							"down_image" : "skybox_system/15_3.tga",
						},
					),
				},
########################################################################### 5. SAYFA ###########################################################################

########################################################################### 6. SAYFA ###########################################################################
				{
					"name" : "maviruh6",
					"type" : "button",
					"style" : ("attach",),
					"x" : 9,
					"y" : 37,
					"width" : 520,
					"height" : 290,
					#"image" : "fake.tga",
					"children" :
					(
						{
							"name" : "skyboxbutton18",
							"type" : "radio_button",

							"x" : 9,
							"y" : 6,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/16_1.tga",
							"over_image" : "skybox_system/16_2.tga",
							"down_image" : "skybox_system/16_3.tga",
						},
						{
							"name" : "skyboxbutton19",
							"type" : "radio_button",

							"x" : 9,
							"y" : 83,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/17_1.tga",
							"over_image" : "skybox_system/17_2.tga",
							"down_image" : "skybox_system/17_3.tga",
						},
						{
							"name" : "skyboxbutton20",
							"type" : "radio_button",

							"x" : 9,
							"y" : 160,

							#"text" : uiScriptLocale.SKYBOX_SELECT,

							"default_image" : "skybox_system/18_1.tga",
							"over_image" : "skybox_system/18_2.tga",
							"down_image" : "skybox_system/18_3.tga",
						},
					),
				},
########################################################################### 6. SAYFA ###########################################################################

####################################################################### SAYFA BUTONLARI ########################################################################
				{
					"name" : "page_button7",
					"type" : "radio_button",

					"x" : 30,
					"y" : 284,
					"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_03.sub",
					"children" :
					(
						{
							"name" : "page_button7_text",
							"type" : "text",
							"x" : 0,
							"y" : 0,
							"all_align" : "center",
							"text" : "I",
						},
					),
				},
				{
					"name" : "page_button8",
					"type" : "radio_button",

					"x" : 155,
					"y" : 284,
					"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_03.sub",
					"children" :
					(
						{
							"name" : "page_button8_text",
							"type" : "text",
							"x" : 0,
							"y" : 0,
							"all_align" : "center",
							"text" : "II",
						},
					),
				},
				{
					"name" : "page_button3",
					"type" : "radio_button",

					"x" : 280,
					"y" : 284,
					"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_03.sub",
					"children" :
					(
						{
							"name" : "page_button3_text",
							"type" : "text",
							"x" : 0,
							"y" : 0,
							"all_align" : "center",
							"text" : "III",
						},
					),
				},
				{
					"name" : "page_button4",
					"type" : "radio_button",

					"x" : 30,
					"y" : 314,
					"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_03.sub",
					"children" :
					(
						{
							"name" : "page_button4_text",
							"type" : "text",
							"x" : 0,
							"y" : 0,
							"all_align" : "center",
							"text" : "IV",
						},
					),
				},
				{
					"name" : "page_button5",
					"type" : "radio_button",
					"x" : 155,
					"y" : 314,
					"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_03.sub",
					"children" :
					(
						{
							"name" : "page_button5_text",
							"type" : "text",
							"x" : 0,
							"y" : 0,
							"all_align" : "center",
							"text" : "V",
						},
					),
				},
				{
					"name" : "page_button6",
					"type" : "radio_button",
					"x" : 280,
					"y" : 314,
					"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_01.sub",
					"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_02.sub",
					"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_03.sub",
					"children" :
					(
						{
							"name" : "page_button6_text",
							"type" : "text",
							"x" : 0,
							"y" : 0,
							"all_align" : "center",
							"text" : "VI",
						},
					),
				},
####################################################################### SAYFA BUTONLARI ########################################################################

##################################### KESINLIKLE KULLANMAYIN BU 4 BUTONU #####################################
				{
					"name" : "skyboxbutton1",
					"type" : "radio_button",

					"x" : 20 + 50 + 5,
					"y" : 40 + 25 + 25 + 10,

					#"text" : "Skybox - 1",

					#"default_image" : ROOT_PATH + "empty_01_normal.tga",
					#"over_image" : ROOT_PATH + "filled_02_hover.tga",
					#"down_image" : ROOT_PATH + "filled_03_active.tga",
				},
				{
					"name" : "skyboxbutton2",
					"type" : "radio_button",

					"x" : 20 + 100 + 20 + 5,
					"y" : 40 + 25 + 25 + 10,

					#"text" : "Skybox - 2",

					#"default_image" : ROOT_PATH + "empty_01_normal.tga",
					#"over_image" : ROOT_PATH + "filled_02_hover.tga",
					#"down_image" : ROOT_PATH + "filled_03_active.tga",
				},
				{
					"name" : "page_button1",
					"type" : "radio_button",

					"x" : 30,
					"y" : 284,
					#"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_01.sub",
					#"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_02.sub",
					#"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_03.sub",
				},
				{
					"name" : "page_button2",
					"type" : "radio_button",

					"x" : 155,
					"y" : 284,
					#"default_image" : "d:/ymir work/ui/game/windows/tab_button_large_01.sub",
					#"over_image" : "d:/ymir work/ui/game/windows/tab_button_large_02.sub",
					#"down_image" : "d:/ymir work/ui/game/windows/tab_button_large_03.sub",
				},
##################################### KESINLIKLE KULLANMAYIN BU 4 BUTONU #####################################
			),
		},
	),
}
