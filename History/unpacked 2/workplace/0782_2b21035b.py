# coding: latin_1

PATH = "d:/ymir work/ui/new_panels/"
FONT_COLOR = 0xFFc3af9a

window = {
	"name" : "selectcharacterwindow",
	
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
			
			"image" : PATH + "select_character/background.tga",
			
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
					"name" : "board",
					"type" : "image",

					"horizontal_align" : "left",
					"vertical_align" : "center",
					
					"x" : 20,
					"y" : -50,

					"image" : PATH + "select_character/main_board.tga",
					
					"children" :
					(
						{
							"name" : "character_details_window",
							"type" : "window",

							"width" : 252,
							"height" : 22,

							"x" : 6,
							"y" : 29,

							"children" :
							(
								{
									"name" : "character_details_window_text",
									"type" : "text",

									"horizontal_align" : "center",
									"text_horizontal_align" : "center",

									"x" : 0,
									"y" : 0,

									"color" : FONT_COLOR,
									"text" : "Character Details",
								},
							),
						},

						{
							"name" : "character_stats_window",
							"type" : "window",

							"width" : 252,
							"height" : 22,

							"x" : 6,
							"y" : 184,

							"children" :
							(
								{
									"name" : "character_stats_window_text",
									"type" : "text",

									"horizontal_align" : "center",
									"text_horizontal_align" : "center",

									"x" : 0,
									"y" : 0,

									"color" : FONT_COLOR,
									"text" : "Character Stats",
								},
							),
						},

						{
							"name" : "name_slotbar_text",
							"type" : "text",

							"x" : 17,
							"y" : 70,

							"color" : FONT_COLOR,
							"text" : "Name:",
						},

						{
							"name" : "name_slotbar",
							"type" : "image",

							"x" : 129,
							"y" : 62,

							"image" : PATH + "select_character/inputs/slotbar_large.tga",

							"children" :
							(
								{
									"name" : "name",
									"type" : "text",

									"horizontal_align" : "center",
									"text_horizontal_align" : "center",

									"x" : 0,
									"y" : 5,

									"color" : FONT_COLOR,
									"text" : "",
								},
							),
						},

						{
							"name" : "level_slotbar_text",
							"type" : "text",

							"x" : 17,
							"y" : 70 + 29,

							"color" : FONT_COLOR,
							"text" : "Level:",
						},

						{
							"name" : "level_slotbar",
							"type" : "image",

							"x" : 129,
							"y" : 62 + 29,

							"image" : PATH + "select_character/inputs/slotbar_large.tga",

							"children" :
							(
								{
									"name" : "level",
									"type" : "text",

									"horizontal_align" : "center",
									"text_horizontal_align" : "center",

									"x" : 0,
									"y" : 5,

									"color" : FONT_COLOR,
									"text" : "",
								},
							),
						},
						
						{
							"name" : "guild_slotbar_text",
							"type" : "text",

							"x" : 17,
							"y" : 70 + 29 * 2,

							"color" : FONT_COLOR,
							"text" : "Guild:",
						},

						{
							"name" : "guild_slotbar",
							"type" : "image",

							"x" : 129,
							"y" : 62 + 29 * 2,

							"image" : PATH + "select_character/inputs/slotbar_large.tga",

							"children" :
							(
								{
									"name" : "guild",
									"type" : "text",

									"horizontal_align" : "center",
									"text_horizontal_align" : "center",

									"x" : 0,
									"y" : 5,

									"color" : FONT_COLOR,
									"text" : "",
								},
							),
						},
						
						{
							"name" : "time_slotbar_text",
							"type" : "text",

							"x" : 17,
							"y" : 70 + 29 * 3,

							"color" : FONT_COLOR,
							"text" : "Play time:",
						},

						{
							"name" : "time_slotbar",
							"type" : "image",

							"x" : 129,
							"y" : 62 + 29 * 3,

							"image" : PATH + "select_character/inputs/slotbar_large.tga",

							"children" :
							(
								{
									"name" : "time",
									"type" : "text",

									"horizontal_align" : "center",
									"text_horizontal_align" : "center",

									"x" : 0,
									"y" : 5,

									"color" : FONT_COLOR,
									"text" : "",
								},
							),
						},
						
						{
							"name" : "hth_gauge_text",
							"type" : "text",

							"x" : 17,
							"y" : 225,

							"color" : FONT_COLOR,
							"text" : "HP:",
						},

						{
							"name" : "hth_gauge_empty",
							"type" : "image",

							"x" : 49,
							"y" : 227,

							"image" : PATH + "select_character/gauges/empty.tga",
						},

						{
							"name" : "hth_gauge_full",
							"type" : "expanded_image",

							"x" : 49,
							"y" : 227,

							"image" : PATH + "select_character/gauges/full.tga",
						},

						{
							"name" : "hth_slotbar",
							"type" : "image",

							"x" : 213,
							"y" : 217,

							"image" : PATH + "select_character/inputs/slotbar_small.tga",

							"children" :
							(
								{
									"name" : "hth_slotbar_text",
									"type" : "text",

									"horizontal_align" : "center",
									"text_horizontal_align" : "center",

									"x" : 0,
									"y" : 5,

									"color" : FONT_COLOR,
									"text" : "",
								},
							),
						},

						{
							"name" : "int_gauge_text",
							"type" : "text",

							"x" : 17,
							"y" : 225 + 29,

							"color" : FONT_COLOR,
							"text" : "INT:",
						},

						{
							"name" : "int_gauge_empty",
							"type" : "image",

							"x" : 49,
							"y" : 227 + 29,

							"image" : PATH + "select_character/gauges/empty.tga",
						},

						{
							"name" : "int_gauge_full",
							"type" : "expanded_image",

							"x" : 49,
							"y" : 227 + 29,

							"image" : PATH + "select_character/gauges/full.tga",
						},

						{
							"name" : "int_slotbar",
							"type" : "image",

							"x" : 213,
							"y" : 217 + 29,

							"image" : PATH + "select_character/inputs/slotbar_small.tga",

							"children" :
							(
								{
									"name" : "int_slotbar_text",
									"type" : "text",

									"horizontal_align" : "center",
									"text_horizontal_align" : "center",

									"x" : 0,
									"y" : 5,

									"color" : FONT_COLOR,
									"text" : "",
								},
							),
						},
						
						{
							"name" : "str_gauge_text",
							"type" : "text",

							"x" : 17,
							"y" : 225 + 29 * 2,

							"color" : FONT_COLOR,
							"text" : "STR:",
						},

						{
							"name" : "str_gauge_empty",
							"type" : "image",

							"x" : 49,
							"y" : 227 + 29 * 2,

							"image" : PATH + "select_character/gauges/empty.tga",
						},

						{
							"name" : "str_gauge_full",
							"type" : "expanded_image",

							"x" : 49,
							"y" : 227 + 29 * 2,

							"image" : PATH + "select_character/gauges/full.tga",
						},

						{
							"name" : "str_slotbar",
							"type" : "image",

							"x" : 213,
							"y" : 217 + 29 * 2,

							"image" : PATH + "select_character/inputs/slotbar_small.tga",

							"children" :
							(
								{
									"name" : "str_slotbar_text",
									"type" : "text",

									"horizontal_align" : "center",
									"text_horizontal_align" : "center",

									"x" : 0,
									"y" : 5,

									"color" : FONT_COLOR,
									"text" : "",
								},
							),
						},
						
						{
							"name" : "dex_gauge_text",
							"type" : "text",

							"x" : 17,
							"y" : 225 + 29 * 3,

							"color" : FONT_COLOR,
							"text" : "DEX:",
						},

						{
							"name" : "dex_gauge_empty",
							"type" : "image",

							"x" : 49,
							"y" : 227 + 29 * 3,

							"image" : PATH + "select_character/gauges/empty.tga",
						},

						{
							"name" : "dex_gauge_full",
							"type" : "expanded_image",

							"x" : 49,
							"y" : 227 + 29 * 3,

							"image" : PATH + "select_character/gauges/full.tga",
						},

						{
							"name" : "dex_slotbar",
							"type" : "image",

							"x" : 213,
							"y" : 217 + 29 * 3,

							"image" : PATH + "select_character/inputs/slotbar_small.tga",

							"children" :
							(
								{
									"name" : "dex_slotbar_text",
									"type" : "text",

									"horizontal_align" : "center",
									"text_horizontal_align" : "center",

									"x" : 0,
									"y" : 5,

									"color" : FONT_COLOR,
									"text" : "",
								},
							),
						},
					),
				},
				{
					"name" : "enter_button", 
					"type" : "button",

					"horizontal_align" : "left",
					"vertical_align" : "center",
							
					"x" : 20, 
					"y" : 165,
							
					"default_image" : PATH + "select_character/buttons/enter_default.tga",
					"over_image" : PATH + "select_character/buttons/enter_default.tga",
					"down_image" : PATH + "select_character/buttons/enter_default.tga",
					"disable_image" : PATH + "select_character/buttons/enter_default.tga",

					"text" : "Play",
				},

				{
					"name" : "back_button", 
					"type" : "button",

					"horizontal_align" : "left",
					"vertical_align" : "center",
							
					"x" : 39, 
					"y" : 221,
							
					"default_image" : PATH + "select_character/buttons/back_default.tga",
					"over_image" : PATH + "select_character/buttons/back_default.tga",
					"down_image" : PATH + "select_character/buttons/back_default.tga",
					"disable_image" : PATH + "select_character/buttons/back_default.tga",

					"children" :
					(
						{
							"name" : "back_button_text",
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
							
					"x" : 165, 
					"y" : 221,
							
					"default_image" : PATH + "select_character/buttons/exit_default.tga",
					"over_image" : PATH + "select_character/buttons/exit_default.tga",
					"down_image" : PATH + "select_character/buttons/exit_default.tga",
					"disable_image" : PATH + "select_character/buttons/exit_default.tga",

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

				{
					"name" : "board2",
					"type" : "thinboard",
					
					"x" : 38,
					"y" : 182,
					
					"width" : 324,
					"height" : 60,
					
					"horizontal_align" : "right",
					"vertical_align" : "center",
					
					"children" :
					(
						{
							"name" : "delete_button", 
							"type" : "button",
							
							"x" : 0, 
							"y" : 0,
							
							"default_image" : "d:/ymir work/ui/public/window_files/select/delete_button_0.tga",
							"over_image" : "d:/ymir work/ui/public/window_files/select/delete_button_1.tga",
							"down_image" : "d:/ymir work/ui/public/window_files/select/delete_button_2.tga",
							"disable_image" : "d:/ymir work/ui/public/window_files/select/delete_button_2.tga",
						},
						{
							"name" : "left_button",
							"type" : "button",
							
							"x" : 13,
							"y" : 12,
							
							"default_image" : "d:/ymir work/ui/public/window_files/select/left_button_0.tga",
							"over_image" : "d:/ymir work/ui/public/window_files/select/left_button_1.tga",
							"down_image" : "d:/ymir work/ui/public/window_files/select/left_button_2.tga",
						},
						
						{
							"name" : "create_button",
							"type" : "button",
							
							"x" : 98,
							"y" : 12,
							
							"default_image" : "d:/ymir work/ui/public/window_files/select/create_button_0.tga",
							"over_image" : "d:/ymir work/ui/public/window_files/select/create_button_1.tga",
							"down_image" : "d:/ymir work/ui/public/window_files/select/create_button_2.tga",
							"disable_image" : "d:/ymir work/ui/public/window_files/select/create_button_2.tga",
						},
						
						{
							"name" : "right_button",
							"type" : "button",
							
							"x" : 235,
							"y" : 12,
							
							"default_image" : "d:/ymir work/ui/public/window_files/select/right_button_0.tga",
							"over_image" : "d:/ymir work/ui/public/window_files/select/right_button_1.tga",
							"down_image" : "d:/ymir work/ui/public/window_files/select/right_button_2.tga",
						},
					),
				},
			),
		},
	),
}