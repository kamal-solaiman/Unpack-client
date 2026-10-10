import localeinfo
IMG_DIR = "d:/ymir work/ui/game/gameoption/"
window = {
	"name" : "PartyWarBoard",
	"style" : ("movable", "float",),

	"x" : 0,
	"y" : 50,

	"width" : 340,
	"height" : 345,

	"children" :
	[
		{
			"name" : "board",
			"type" : "board",

			"x" : 0,
			"y" : 0,

			"width" : 340,
			"height" : 345,

			"children" :
			[
				########### Title ########### 
				{
					"name" : "titlebar",
					"type" : "titlebar",
					"style" : ("attach",),

					"x" : 8,
					"y" : 8,

					"width" : 340-21,
					"color" : "gray",

					"children" :
					[
						{ "name" : "titlename", "type" : "text", "x" : 0, "y" : 2, "horizontal_align" : "center", "outline" : 1, "text_horizontal_align" : "center", "text": localeinfo.PARTY_WAR_TEXT1},
					],
				},

				########### Pages ###########
				{
					"name" : "BoardBg",
					"type" : "image",
					"style" : ("attach",),

					"x" : 0,
					"y" : 35,

					"image" : "d:/ymir work/ui/game/board_bg.png",
					"horizontal_align" : "center",

					"children" :
					[
						{
							"name": "Page1",
							"type": "window",

							"x": 0,
							"y": 0,

							"width" : 310,
							"height" : 345,
							"children":
							[
								{ "name" : "Title", "type" : "text", "x" : 0, "y" : 12, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : localeinfo.PARTY_WAR_TEXT2 },
								
								{
									"name" : "SetButton", "type" : "button", "x" : 0, "y" : 210, "horizontal_align" : "center",

									"default_image" : "d:/ymir work/ui/public/acceptbutton00.sub",
									"over_image" : "d:/ymir work/ui/public/acceptbutton01.sub",
									"down_image" : "d:/ymir work/ui/public/acceptbutton02.sub",
								},
								

								#####################################################################################################################################################################
								{ "name" : "Title", "type" : "text", "x" : 0, "y" : 80+5, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : localeinfo.PARTY_WAR_TEXT3 },
								{
									"name" : "member_button0", "type" : "radio_button", "x" : -100, "y" : 80+30,"horizontal_align" : "center",
									"default_image" : IMG_DIR + "radio_unselected.tga","over_image" : IMG_DIR + "radio_selected.tga","down_image" : IMG_DIR + "radio_selected.tga",
									"children" :
									(
										{ "name" : "Title", "type" : "text", "x" : 12, "y" : -2, "horizontal_align" : "center", "text_horizontal_align" : "left", "text" : "2" },
									),
								},
								{
									"name" : "member_button1", "type" : "radio_button", "x" : -40, "y" : 80+30,"horizontal_align" : "center",
									"default_image" : IMG_DIR + "radio_unselected.tga","over_image" : IMG_DIR + "radio_selected.tga","down_image" : IMG_DIR + "radio_selected.tga",
									"children" :
									(
										{ "name" : "Title", "type" : "text", "x" : 12, "y" : -2, "horizontal_align" : "center", "text_horizontal_align" : "left", "text" : "3" },
									),
								},
								{
									"name" : "member_button2", "type" : "radio_button", "x" : 20, "y" : 80+30,"horizontal_align" : "center",
									"default_image" : IMG_DIR + "radio_unselected.tga","over_image" : IMG_DIR + "radio_selected.tga","down_image" : IMG_DIR + "radio_selected.tga",
									"children" :
									(
										{ "name" : "Title", "type" : "text", "x" : 12, "y" : -2, "horizontal_align" : "center", "text_horizontal_align" : "left", "text" : "4" },
									),
								},
								{
									"name" : "member_button3", "type" : "radio_button", "x" : 80, "y" : 80+30,"horizontal_align" : "center",
									"default_image" : IMG_DIR + "radio_unselected.tga","over_image" : IMG_DIR + "radio_selected.tga","down_image" : IMG_DIR + "radio_selected.tga",
									"children" :
									(
										{ "name" : "Title", "type" : "text", "x" : 12, "y" : -2, "horizontal_align" : "center", "text_horizontal_align" : "left", "text" : "5" },
									),
								},
								#####################################################################################################################################################################
								## Input Slot
								
								{
									"name" : "InputSlot",
									"type" : "slotbar",

									"x" : -50,
									"y" : 160,
									"width" : 70,
									"height" : 18,
									"horizontal_align" : "center",

									"children" :
									(
										{
											"name" : "inputReward",
											"type" : "editline",

											"x" : 3,
											"y" : 3,

											"width" : 70,
											"height" : 18,

											"input_limit" : 8,
										},
										{ "name" : "Title", "type" : "text", "x" : 0, "y" : -12, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : localeinfo.PARTY_WAR_TEXT4 },
									),
								},
								
								{
									"name" : "InputSlot",
									"type" : "slotbar",

									"x" : 50,
									"y" : 160,
									"width" : 70,
									"height" : 18,
									"horizontal_align" : "center",

									"children" :
									(
										{
											"name" : "inputGroups",
											"type" : "editline",

											"x" : 3,
											"y" : 3,

											"width" : 70,
											"height" : 18,

											"input_limit" : 8,
										},
										{ "name" : "Title", "type" : "text", "x" : 0, "y" : -12, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : localeinfo.PARTY_WAR_TEXT5 },
									),
								},
							],
						},

						######################

						{
							"name": "Page2",
							"type": "window",

							"x": 0,
							"y": 0,

							"width" : 310,
							"height" : 345,
							"children":
							[
								{
									"name" : "BoardBg2",
									"type" : "image",
									"style" : ("attach",),

									"x" : -3,
									"y" : 0,

									"image" : "d:/ymir work/ui/game/board_bg2.png",
									"horizontal_align" : "center",
								},
								
								{ "name" : "Title", "type" : "text", "x" : 0, "y" : 12, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : localeinfo.PARTY_WAR_TEXT6 },

								## regist slot
								{
									"name" : "ItemImage", "type" : "slot", "x" : 55+5+5, "y" : 50, "width" : 132, "height" : 132, "slot" : ( {"index":0, "x":6, "y":6, "width":32, "height":32}, )
								},
								
								
								{ "name" : "Title", "type" : "text", "x" : -90-20, "y" : 80+90-25, "horizontal_align" : "center", "text_horizontal_align" : "left", "text" : localeinfo.PARTY_WAR_TEXT7 },

								{
									"name" : "type_button0", "type" : "radio_button", "x" : -70, "y" : 80+90,"horizontal_align" : "center",
									"default_image" : IMG_DIR + "radio_unselected.tga","over_image" : IMG_DIR + "radio_selected.tga","down_image" : IMG_DIR + "radio_selected.tga",
									"children" :
									(
										{ "name" : "Title", "type" : "text", "x" : 12, "y" : -2, "horizontal_align" : "center", "text_horizontal_align" : "left", "text" : localeinfo.PARTY_WAR_TEXT8 },
									),
								},
								{
									"name" : "type_button1", "type" : "radio_button", "x" : 30, "y" : 80+90,"horizontal_align" : "center",
									"default_image" : IMG_DIR + "radio_unselected.tga","over_image" : IMG_DIR + "radio_selected.tga","down_image" : IMG_DIR + "radio_selected.tga",
									"children" :
									(
										{ "name" : "Title", "type" : "text", "x" : 12, "y" : -2, "horizontal_align" : "center", "text_horizontal_align" : "left", "text" : localeinfo.PARTY_WAR_TEXT9 },
									),
								},
								
								{ "name" : "Title", "type" : "text", "x" : -90-20, "y" : 80+130-23, "horizontal_align" : "center", "text_horizontal_align" : "left", "text" : localeinfo.PARTY_WAR_TEXT10 },
								{
									"name" : "time_button0", "type" : "radio_button", "x" : -90-20, "y" : 80+130,"horizontal_align" : "center",
									"default_image" : IMG_DIR + "radio_unselected.tga","over_image" : IMG_DIR + "radio_selected.tga","down_image" : IMG_DIR + "radio_selected.tga",
									"children" :
									(
										{ "name" : "Title", "type" : "text", "x" : 12, "y" : -2, "horizontal_align" : "center", "text_horizontal_align" : "left", "text" : localeinfo.PARTY_WAR_TEXT11 },
									),
								},
								{
									"name" : "time_button1", "type" : "radio_button", "x" : 0-20-15, "y" : 80+130,"horizontal_align" : "center",
									"default_image" : IMG_DIR + "radio_unselected.tga","over_image" : IMG_DIR + "radio_selected.tga","down_image" : IMG_DIR + "radio_selected.tga",
									"children" :
									(
										{ "name" : "Title", "type" : "text", "x" : 12, "y" : -2, "horizontal_align" : "center", "text_horizontal_align" : "left", "text" : localeinfo.PARTY_WAR_TEXT12 },
									),
								},
								{
									"name" : "time_button2", "type" : "radio_button", "x" : 90-20-15, "y" : 80+130,"horizontal_align" : "center",
									"default_image" : IMG_DIR + "radio_unselected.tga","over_image" : IMG_DIR + "radio_selected.tga","down_image" : IMG_DIR + "radio_selected.tga",
									"children" :
									(
										{ "name" : "Title", "type" : "text", "x" : 12, "y" : -2, "horizontal_align" : "center", "text_horizontal_align" : "left", "text" : localeinfo.PARTY_WAR_TEXT13 },
									),
								},
								
								{
									"name" : "StartButton", "type" : "button", "x" : -40, "y" : 230, "horizontal_align" : "center",

									"default_image" : "d:/ymir work/ui/public/acceptbutton00.sub",
									"over_image" : "d:/ymir work/ui/public/acceptbutton01.sub",
									"down_image" : "d:/ymir work/ui/public/acceptbutton02.sub",
								},
								
								{
									"name" : "StopButton", "type" : "button", "x" : 40, "y" : 230, "horizontal_align" : "center",

									"default_image" : "d:/ymir work/ui/public/canclebutton00.sub",
									"over_image" : "d:/ymir work/ui/public/canclebutton01.sub",
									"down_image" : "d:/ymir work/ui/public/canclebutton02.sub",
								},
								

								{ 
									"name" : "MembersCount",
									"type" : "text", "x" : -55, "y" : 70 ,
									"horizontal_align" : "center", "text_horizontal_align" : "center" ,
									"text" : "None" ,
									"children" :
									(
										{ 
											"name" : "MembersCountTxt", "type" : "text",
											"x" : 0,"y" : -20,
											"horizontal_align" : "center", "text_horizontal_align" : "center" ,
											#"fontname" : "Tahoma Bold:14",
											"text" : localeinfo.PARTY_WAR_MEMBER_COUNT 
										},
									),
								},
								
								
								{ 
									"name" : "GroupsCount",
									"type" : "text", "x" : -55, "y" : 110 ,
									"horizontal_align" : "center", "text_horizontal_align" : "center" ,
									"text" : "None" ,
									"children" :
									(
										{ 
											"name" : "GroupsCountTxt", "type" : "text",
											"x" : 0,"y" : -20,
											"horizontal_align" : "center", "text_horizontal_align" : "center" ,
											#"fontname" : "Tahoma Bold:14",
											"text" : localeinfo.PARTY_WAR_PT_COUNT 
										},
									),
								},
								
								
							],
						},
						######################

					],
				},
				
				############################
				
				########### Tabs ###########

				{ "name" : "Tab1", "type" : "radio_button", "x" : -70, "y" : 140, "text" : "I",
					"default_image" : "d:/ymir work/ui/public/large_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/large_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/large_button_03.sub",
					"all_align" : "center",
				},

				{ "name" : "Tab2", "type" : "radio_button", "x" : 70, "y" : 140, "text" : "II",
					"default_image" : "d:/ymir work/ui/public/large_button_01.sub",
					"over_image" : "d:/ymir work/ui/public/large_button_02.sub",
					"down_image" : "d:/ymir work/ui/public/large_button_03.sub",
					"all_align" : "center",
				},
				
				############################

			],
		},
	],
}
