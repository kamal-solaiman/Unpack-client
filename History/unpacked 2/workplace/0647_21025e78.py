import localeinfo

window = {
	"name" : "LearnSkill",
	"style" : ("movable", "float",),

	"x" : 0,
	"y" : 0,

	"width" : 238+35,
	"height" : 190,

	"children" :
	(
		{
			"name" : "board",
			"type" : "board_with_titlebar",

			"x" : 0,
			"y" : 0,

			"width" : 238+35,
			"height" : 190,
			"title" : localeinfo.SKILL_LEARN_WINDOW,

			"children" :
			(
				
				{
					"name" : "button_bg",
					"type" : "thinboard_circle",
					
					"x" : 9,
					"y" : 30,
					
					"width" : 220+35,
					"height" : 30,
					
					"children" :
					
					(
						# {
							# "name" : "normal",
							# "type" : "radio_button",

							# "x" : -30,
							# "y" : 0,
							
							# "all_align" : "center",

							# "text" : "Normal",

							# "default_image" : "d:/ymir work/ui/game/windows/tab_button_middle_01.sub",
							# "over_image" : "d:/ymir work/ui/game/windows/tab_button_middle_02.sub",
							# "down_image" : "d:/ymir work/ui/game/windows/tab_button_middle_03.sub",
						# },
						
						# {
							# "name" : "passive",
							# "type" : "radio_button",

							# "x" : 30,
							# "y" : 0,
							
							# "all_align" : "center",

							# "text" : "Pasif",

							# "default_image" : "d:/ymir work/ui/game/windows/tab_button_middle_01.sub",
							# "over_image" : "d:/ymir work/ui/game/windows/tab_button_middle_02.sub",
							# "down_image" : "d:/ymir work/ui/game/windows/tab_button_middle_03.sub",
						# },
					),
					
				},
				
				{
					"name" : "normal_skill",
					"type" : "thinboard_circle",
					
					"x" : 9,
					"y" : 30+30,
					
					"width" : 220+35,
					"height" : 80,
					
					"children" :
					
					(
						{
							"name" : "normal_item_slot_text",
							"type" : "text",

							"x" : 5+20+35,
							"y" : 7,

							"text" : localeinfo.SKILL_LEARN_SELECT_SKILL_INFO,
							
						},
						
						
						{
							"name" : "normal_skill_slot",
							"type" : "slot",

							"x" : 9+20,
							"y" : 35,

							"width" : 200,
							"height" : 35,
							"image" : "d:/ymir work/ui/public/slot_base.sub",

							"slot" :	(
											{"index": 0, "x": 0, "y":  0, "width":32, "height":32},
											{"index": 1, "x": 34, "y":  0, "width":32, "height":32},
											{"index": 2, "x": 34*2, "y":  0, "width":32, "height":32},
											{"index": 3, "x": 34*3, "y":  0, "width":32, "height":32},
											{"index": 4, "x": 34*4, "y":  0, "width":32, "height":32},
											{"index": 5, "x": 34*5, "y":  0, "width":32, "height":32},

									),
						},
					),
					
				},
				{
					"name" : "event_button_bg",
					"type" : "thinboard_circle",
					
					"x" : 9,
					"y" : 30+30+80,
					
					"width" : 220+35,
					"height" : 40,
					
					"children" :
					
					(
						{
							"name" : "learn_once",
							"type" : "button",

							"x" :-40,
							"y" : 2,
							
							"all_align" : "center",

							"text" : localeinfo.SKILL_LEARN_LEARN,

							"default_image" : "d:/ymir work/ui/public/large_button_01.sub",
							"over_image" : "d:/ymir work/ui/public/large_button_02.sub",
							"down_image" : "d:/ymir work/ui/public/large_button_03.sub",
						},
						{
							"name" : "learn",
							"type" : "button",

							"x" : 45,
							"y" : 2,
							
							"all_align" : "center",

							"text" : localeinfo.SKILL_LEARN_FAST_LEARN,

							"default_image" : "d:/ymir work/ui/public/large_button_01.sub",
							"over_image" : "d:/ymir work/ui/public/large_button_02.sub",
							"down_image" : "d:/ymir work/ui/public/large_button_03.sub",
						},
					),
					
				},
			),
		},
	),
}