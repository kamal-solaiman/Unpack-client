# coding: latin_1

PATH = "d:/ymir work/ui/new_panels/"

FONT_COLOR = 0xFFc3af9a


window = {
	"name" : "CreateCharacterWindow",
	
	"x" : 0,
	"y" : 0,
	
	"width" : SCREEN_WIDTH,
	"height" : SCREEN_HEIGHT,
	
	"children" :
	(
		{
			"name" : "BackGround",
			"type" : "expanded_image",
			
			"x" : 0,
			"y" : 0,
			
			"x_scale" : float(SCREEN_WIDTH) / 1920,
			"y_scale" : float(SCREEN_HEIGHT) / 1080,
			
			"image" : PATH + "create_character/background.tga",
			
			"children" :
			(
				{
					"name" : "server_logo",
					"type" : "image",

					"horizontal_align" : "center",

					"x" : 0,
					"y" : 15,

					"image" : PATH + "login/logo.tga",
				},

				{
					"name" : "character_name_slot",
					"type" : "image",

					"horizontal_align" : "left",
					"vertical_align" : "center",
							
					"x" : 18 + 8,
					"y" : 20,
							
					"image" : PATH + "create_character/inputs/character_name.tga",
							
					"children" :
					(
						{
							"name" : "character_name_value",
							"type" : "editline",

							"width" : 253,
							"height" : 19,

							"x" : 7,
							"y" : 9,
									
							"color" : FONT_COLOR,
							"input_limit" : 12,
						},
					),
				},

				{
					"name" : "create_button",
					"type" : "button",

					"horizontal_align" : "left",
					"vertical_align" : "center",
							
					"x" : 18 + 8,
					"y" : 20 + 50,
							
					"default_image" : PATH + "create_character/buttons/create_default.tga",
					"over_image" : PATH + "create_character/buttons/create_default.tga",
					"down_image" : PATH + "create_character/buttons/create_default.tga",

					"text" : "Create",
				},

				{
					"name" : "cancel_button",
					"type" : "button",

					"horizontal_align" : "left",
					"vertical_align" : "center",
							
					"x" : 18 + 19 + 8,
					"y" : 20 + 50 + 56,
							
					"default_image" : PATH + "create_character/buttons/back_default.tga",
					"over_image" : PATH + "create_character/buttons/back_default.tga",
					"down_image" : PATH + "create_character/buttons/back_default.tga",

					"children" :
					(
						{
							"name" : "cancel_button_text",
							"type" : "text",

							"horizontal_align" : "center",
							"text_horizontal_align" : "center",

							"x" : 0,
							"y" : 7,

							"color" : FONT_COLOR,
							"text" : "Back",
						},
					),
				},

				{
					"name" : "exit_button",
					"type" : "button",

					"horizontal_align" : "left",
					"vertical_align" : "center",
							
					"x" : 18 + 146 + 8,
					"y" : 20 + 50 + 56,
							
					"default_image" : PATH + "create_character/buttons/exit_default.tga",
					"over_image" : PATH + "create_character/buttons/exit_default.tga",
					"down_image" : PATH + "create_character/buttons/exit_default.tga",

					"children" :
					(
						{
							"name" : "exit_button_text",
							"type" : "text",

							"horizontal_align" : "center",
							"text_horizontal_align" : "center",

							"x" : 0,
							"y" : 7,

							"color" : FONT_COLOR,
							"text" : "Exit Game",
						},
					),
				},
			),
		},
	),
}
