# coding: latin_1

import localeinfo
PATH = "d:/ymir work/ui/game/new_panels/"

ROOT_PATH = "lava_login/login/"

FONT_COLOR = 0xFFF5E6BA
INPUR_COLOR = 0xFF88705D

window = {
	"name" : "loginwindow",
	"sytle" : ("movable",),

	"x" : 0, 
	"y" : 0,

	"width" : SCREEN_WIDTH,
	"height" : SCREEN_HEIGHT,

	"children" :
	(
		{
			"name" : "Background",
			"type" : "ani_image",

			"x" : 0,
			"y" : 0,

			"x_scale" : float(SCREEN_WIDTH) / 1920.0,
			"y_scale" : float(SCREEN_HEIGHT) / 1080.0,

			"width" : SCREEN_WIDTH,
			"height" : SCREEN_HEIGHT,

			"images" : ("%sbackground/%03d.dds" % (ROOT_PATH, i + 1) for i in xrange(94)),

			"children" :
			(
				{
					"name": "exit_button",
					"type": "button",

					"x": SCREEN_WIDTH - 25 - 20 - 30,
					"y": 20,

					"default_image": ROOT_PATH + "close_button_01.sub",
					"over_image": ROOT_PATH + "close_button_02.sub",
					"down_image": ROOT_PATH + "close_button_02.sub",

				},


				{
					"name" : "server_button_01",
					"type" : "radio_button",

					"x" : 104,
					"y" :  150 * float(SCREEN_HEIGHT) / 1080.0 + 36,

					"default_image" : ROOT_PATH + "server1_button_01.sub",
					"over_image" : ROOT_PATH + "server1_button_02.sub",
					"down_image" : ROOT_PATH + "server1_button_03.sub",
				},
				{
					"name" : "server_button_02",
					"type" : "radio_button",

					"x" : 154,
					"y" :  150 * float(SCREEN_HEIGHT) / 1080.0 + 36,

					"horizontal_align" : "right",

					"default_image" : ROOT_PATH + "server2_button_01.sub",
					"over_image" : ROOT_PATH + "server2_button_02.sub",
					"down_image" : ROOT_PATH + "server2_button_03.sub",
				},

				{
					"name" : "login_board",
					"type" : "image",

					"horizontal_align" : "center",
					"vertical_align" : "center",

					"x" : 0,
					"y" : 150 * float(SCREEN_HEIGHT) / 1080.0,
					
					"image" : ROOT_PATH + "login_board.sub",

					"children" :
					(
						{
							"name" : "login_input",
							"type" : "image",

							"x" : 0,
							"y" : 54,

							"horizontal_align" : "center",

							"image" : ROOT_PATH + "login_header_text.sub",
						},
						{
							"name" : "login_input",
							"type" : "expanded_image",

							"x" : 0,
							"y" : 130,

							"horizontal_align" : "center",

							"image" : ROOT_PATH + "input_login_slot.tga",

							"children" :
							(
								{
									"name" : "id",
									"type" : "editline",

									"width" : 209,
									"height" : 19, 

									"x" : 62,
									"y" : 20,

									"color" : INPUR_COLOR,

									"input_limit" : 16,
								},
							),
						},

						{
							"name" : "password_input",
							"type" : "expanded_image",

							"x" : 0,
							"y" : 170,

							"horizontal_align" : "center",

							"image" : ROOT_PATH + "input_password_slot.tga",

							"children" :
							(
								{
									"name" : "pwd",
									"type" : "editline",

									"width" : 209,
									"height" : 19, 

									"x" : 62,
									"y" : 20,

									"color" : INPUR_COLOR,

									"input_limit" : 16,
									"secret_flag" : True,
								},
							),
						},
						{
							"name" : "register_button",
							"type" : "button",

							"x" : 0,
							"y" : 235,

							"horizontal_align" : "center",

							"default_image" : ROOT_PATH + "register_text_01.sub",
							"over_image" : ROOT_PATH + "register_text_02.sub",
							"down_image" : ROOT_PATH + "register_text_03.sub",
						},
						{
							"name" : "login_button",
							"type" : "button",

							"x" : 0,
							"y" : 284,

							"horizontal_align" : "center",

							"default_image" : ROOT_PATH + "login_button_01.sub",
							"over_image" : ROOT_PATH + "login_button_02.sub",
							"down_image" : ROOT_PATH + "login_button_03.sub",
						},
						{
							"name" : "account_board",
							"type" : "window",
							
							"x" : 33,
							"y" : 110,
							
							"width" : 190,
							"height" : 167,
							
							"children" : (
								{
									"name" : "account_header_text",
									"type" : "image",

									"x" : 0,
									"y" : 2,

									"horizontal_align" : "center",

									"image" : ROOT_PATH + "account_header_text.sub",
								},
								{
									"name" : "arrow_left_button",
									"type" : "button",

									"x" : 0,
									"y" : 0,

									"default_image" : ROOT_PATH + "arrow_left_01.sub",
									"over_image" : ROOT_PATH + "arrow_left_02.sub",
									"down_image" : ROOT_PATH + "arrow_left_03.sub",
								},
								{
									"name" : "arrow_right_button",
									"type" : "button",

									"x" : 13,
									"y" : 0,
									
									"horizontal_align" : "right",

									"default_image" : ROOT_PATH + "arrow_right_01.sub",
									"over_image" : ROOT_PATH + "arrow_right_02.sub",
									"down_image" : ROOT_PATH + "arrow_right_03.sub",
								},
								{
									"name" : "account_window_01",
									"type" : "window",
									
									"x" : 0,
									"y" : 40,
									
									
									"width" : 190,
									"height" : 127,
									
									"children" : (
										{
											"name" : "account_slot_01",
											"type" : "image",

											"x" : 0,
											"y" : 0,

											"image" : ROOT_PATH + "account_slot.sub",

											"children" : (
												{
													"name" : "account_text_01",
													"type" : "text",

													"x" : 26,
													"y" : -1,

													"vertical_align" : "center",
													"text_vertical_align" : "center",

													"color" : FONT_COLOR,

													"text" : "FilipDev.com",
												},
												{
													"name" : "account_load_button_01",
													"type" : "button",

													"x" : 49,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_load_button_01.sub",
													"over_image" : ROOT_PATH + "account_load_button_02.sub",
													"down_image" : ROOT_PATH + "account_load_button_03.sub",
												},
												{
													"name" : "account_delete_button_01",
													"type" : "button",

													"x" : 31,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_delete_button_01.sub",
													"over_image" : ROOT_PATH + "account_delete_button_02.sub",
													"down_image" : ROOT_PATH + "account_delete_button_03.sub",
												},
											),
										},
										{
											"name" : "account_slot_02",
											"type" : "image",

											"x" : 0,
											"y" : 31,

											"image" : ROOT_PATH + "account_slot.sub",

											"children" : (
												{
													"name" : "account_text_02",
													"type" : "text",

													"x" : 26,
													"y" : -1,

													"vertical_align" : "center",
													"text_vertical_align" : "center",

													"color" : FONT_COLOR,

													"text" : "FilipDev.com",
												},
												{
													"name" : "account_load_button_02",
													"type" : "button",

													"x" : 49,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_load_button_01.sub",
													"over_image" : ROOT_PATH + "account_load_button_02.sub",
													"down_image" : ROOT_PATH + "account_load_button_03.sub",
												},
												{
													"name" : "account_delete_button_02",
													"type" : "button",

													"x" : 31,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_delete_button_01.sub",
													"over_image" : ROOT_PATH + "account_delete_button_02.sub",
													"down_image" : ROOT_PATH + "account_delete_button_03.sub",
												},
											),
										},
										{
											"name" : "account_slot_03",
											"type" : "image",

											"x" : 0,
											"y" : 62,

											"image" : ROOT_PATH + "account_slot.sub",

											"children" : (
												{
													"name" : "account_text_03",
													"type" : "text",

													"x" : 26,
													"y" : -1,

													"vertical_align" : "center",
													"text_vertical_align" : "center",

													"color" : FONT_COLOR,

													"text" : "FilipDev.com",
												},
												{
													"name" : "account_load_button_03",
													"type" : "button",

													"x" : 49,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_load_button_01.sub",
													"over_image" : ROOT_PATH + "account_load_button_02.sub",
													"down_image" : ROOT_PATH + "account_load_button_03.sub",
												},
												{
													"name" : "account_delete_button_03",
													"type" : "button",

													"x" : 31,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_delete_button_01.sub",
													"over_image" : ROOT_PATH + "account_delete_button_02.sub",
													"down_image" : ROOT_PATH + "account_delete_button_03.sub",
												},
											),
										},
										{
											"name" : "account_slot_04",
											"type" : "image",

											"x" : 0,
											"y" : 93,

											"image" : ROOT_PATH + "account_slot.sub",

											"children" : (
												{
													"name" : "account_text_04",
													"type" : "text",

													"x" : 26,
													"y" : -1,

													"vertical_align" : "center",
													"text_vertical_align" : "center",

													"color" : FONT_COLOR,

													"text" : "FilipDev.com",
												},
												{
													"name" : "account_load_button_04",
													"type" : "button",

													"x" : 49,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_load_button_01.sub",
													"over_image" : ROOT_PATH + "account_load_button_02.sub",
													"down_image" : ROOT_PATH + "account_load_button_03.sub",
												},
												{
													"name" : "account_delete_button_04",
													"type" : "button",

													"x" : 31,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_delete_button_01.sub",
													"over_image" : ROOT_PATH + "account_delete_button_02.sub",
													"down_image" : ROOT_PATH + "account_delete_button_03.sub",
												},
											),
										},
									),
								},
								{
									"name" : "account_window_02",
									"type" : "window",
									
									"x" : 0,
									"y" : 40,
									
									
									"width" : 190,
									"height" : 127,
									
									"children" : (
										{
											"name" : "account_slot_05",
											"type" : "image",

											"x" : 0,
											"y" : 0,

											"image" : ROOT_PATH + "account_slot.sub",

											"children" : (
												{
													"name" : "account_text_05",
													"type" : "text",

													"x" : 26,
													"y" : -1,

													"vertical_align" : "center",
													"text_vertical_align" : "center",

													"color" : FONT_COLOR,

													"text" : "FilipDev.com",
												},
												{
													"name" : "account_load_button_05",
													"type" : "button",

													"x" : 49,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_load_button_01.sub",
													"over_image" : ROOT_PATH + "account_load_button_02.sub",
													"down_image" : ROOT_PATH + "account_load_button_03.sub",
												},
												{
													"name" : "account_delete_button_05",
													"type" : "button",

													"x" : 31,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_delete_button_01.sub",
													"over_image" : ROOT_PATH + "account_delete_button_02.sub",
													"down_image" : ROOT_PATH + "account_delete_button_03.sub",
												},
											),
										},
										{
											"name" : "account_slot_06",
											"type" : "image",

											"x" : 0,
											"y" : 31,

											"image" : ROOT_PATH + "account_slot.sub",

											"children" : (
												{
													"name" : "account_text_06",
													"type" : "text",

													"x" : 26,
													"y" : -1,

													"vertical_align" : "center",
													"text_vertical_align" : "center",

													"color" : FONT_COLOR,

													"text" : "FilipDev.com",
												},
												{
													"name" : "account_load_button_06",
													"type" : "button",

													"x" : 49,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_load_button_01.sub",
													"over_image" : ROOT_PATH + "account_load_button_02.sub",
													"down_image" : ROOT_PATH + "account_load_button_03.sub",
												},
												{
													"name" : "account_delete_button_06",
													"type" : "button",

													"x" : 31,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_delete_button_01.sub",
													"over_image" : ROOT_PATH + "account_delete_button_02.sub",
													"down_image" : ROOT_PATH + "account_delete_button_03.sub",
												},
											),
										},
										{
											"name" : "account_slot_07",
											"type" : "image",

											"x" : 0,
											"y" : 62,

											"image" : ROOT_PATH + "account_slot.sub",

											"children" : (
												{
													"name" : "account_text_07",
													"type" : "text",

													"x" : 26,
													"y" : -1,

													"vertical_align" : "center",
													"text_vertical_align" : "center",

													"color" : FONT_COLOR,

													"text" : "FilipDev.com",
												},
												{
													"name" : "account_load_button_07",
													"type" : "button",

													"x" : 49,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_load_button_01.sub",
													"over_image" : ROOT_PATH + "account_load_button_02.sub",
													"down_image" : ROOT_PATH + "account_load_button_03.sub",
												},
												{
													"name" : "account_delete_button_07",
													"type" : "button",

													"x" : 31,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_delete_button_01.sub",
													"over_image" : ROOT_PATH + "account_delete_button_02.sub",
													"down_image" : ROOT_PATH + "account_delete_button_03.sub",
												},
											),
										},
										{
											"name" : "account_slot_08",
											"type" : "image",

											"x" : 0,
											"y" : 93,

											"image" : ROOT_PATH + "account_slot.sub",

											"children" : (
												{
													"name" : "account_text_08",
													"type" : "text",

													"x" : 26,
													"y" : -1,

													"vertical_align" : "center",
													"text_vertical_align" : "center",

													"color" : FONT_COLOR,

													"text" : "FilipDev.com",
												},
												{
													"name" : "account_load_button_08",
													"type" : "button",

													"x" : 49,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_load_button_01.sub",
													"over_image" : ROOT_PATH + "account_load_button_02.sub",
													"down_image" : ROOT_PATH + "account_load_button_03.sub",
												},
												{
													"name" : "account_delete_button_08",
													"type" : "button",

													"x" : 31,
													"y" : 0,

													"horizontal_align" : "right",
													"vertical_align" : "center",

													"default_image" : ROOT_PATH + "account_delete_button_01.sub",
													"over_image" : ROOT_PATH + "account_delete_button_02.sub",
													"down_image" : ROOT_PATH + "account_delete_button_03.sub",
												},
											),
										},
									),
								},
							),
						},
						{
							"name" : "channel_board",
							"type" : "window",

							"x" : 219,
							"y" : 150,

							"horizontal_align" : "right",
							
							"width" : 190,
							"height" : 127,
							
							"children" : (
								{
									"name" : "channel_header_text",
									"type" : "image",

									"x" : 0,
									"y" : -38,

									"horizontal_align" : "center",

									"image" : ROOT_PATH + "channel_header_text.sub",
								},
								{
									"name" : "channel_button_01",
									"type" : "radio_button",

									"x" : 0,
									"y" : 0,

									"default_image" : ROOT_PATH + "channel_button_01.sub",
									"over_image" : ROOT_PATH + "channel_button_02.sub",
									"down_image" : ROOT_PATH + "channel_button_03.sub",

									"children" : (
										{
											"name" : "channel_text_01",
											"type" : "text",

											"x" : 26,
											"y" : -1,

											"vertical_align" : "center",
											"text_vertical_align" : "center",

											"color" : FONT_COLOR,

											"text" : localeinfo.PANEL_CHANNEL_1,
										},
										{
											"name" : "channel_select_01",
											"type" : "image",

											"x" : 33,
											"y" : 0,

											"horizontal_align" : "right",
											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_select.sub",
										},
										{
											"name" : "channel_select_01",
											"type" : "image",

											"x" : 33,
											"y" : 0,

											"horizontal_align" : "right",
											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_select.sub",
										},
										{
											"name" : "channel_status_off_01",
											"type" : "image",

											"x" : 0,
											"y" : 0,

											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_status_off.sub",
										},
										{
											"name" : "channel_status_on_01",
											"type" : "image",

											"x" : 0,
											"y" : 0,

											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_status_on.sub",
										},
									),
								},
								{
									"name" : "channel_button_02",
									"type" : "radio_button",

									"x" : 0,
									"y" : 31,

									"default_image" : ROOT_PATH + "channel_button_01.sub",
									"over_image" : ROOT_PATH + "channel_button_02.sub",
									"down_image" : ROOT_PATH + "channel_button_03.sub",

									"children" : (
										{
											"name" : "channel_text_02",
											"type" : "text",

											"x" : 26,
											"y" : -1,

											"vertical_align" : "center",
											"text_vertical_align" : "center",

											"color" : FONT_COLOR,

											"text" : localeinfo.PANEL_CHANNEL_2,
										},
										{
											"name" : "channel_select_02",
											"type" : "image",

											"x" : 33,
											"y" : 0,

											"horizontal_align" : "right",
											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_select.sub",
										},
										{
											"name" : "channel_select_02",
											"type" : "image",

											"x" : 33,
											"y" : 0,

											"horizontal_align" : "right",
											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_select.sub",
										},
										{
											"name" : "channel_status_off_02",
											"type" : "image",

											"x" : 0,
											"y" : 0,

											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_status_off.sub",
										},
										{
											"name" : "channel_status_on_02",
											"type" : "image",

											"x" : 0,
											"y" : 0,

											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_status_on.sub",
										},
									),
								},
								{
									"name" : "channel_button_03",
									"type" : "radio_button",

									"x" : 0,
									"y" : 62,

									"default_image" : ROOT_PATH + "channel_button_01.sub",
									"over_image" : ROOT_PATH + "channel_button_02.sub",
									"down_image" : ROOT_PATH + "channel_button_03.sub",

									"children" : (
										{
											"name" : "channel_text_03",
											"type" : "text",

											"x" : 26,
											"y" : -1,

											"vertical_align" : "center",
											"text_vertical_align" : "center",

											"color" : FONT_COLOR,

											"text" : localeinfo.PANEL_CHANNEL_3,
										},
										{
											"name" : "channel_select_03",
											"type" : "image",

											"x" : 33,
											"y" : 0,

											"horizontal_align" : "right",
											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_select.sub",
										},
										{
											"name" : "channel_select_03",
											"type" : "image",

											"x" : 33,
											"y" : 0,

											"horizontal_align" : "right",
											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_select.sub",
										},
										{
											"name" : "channel_status_off_03",
											"type" : "image",

											"x" : 0,
											"y" : 0,

											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_status_off.sub",
										},
										{
											"name" : "channel_status_on_03",
											"type" : "image",

											"x" : 0,
											"y" : 0,

											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_status_on.sub",
										},
									),
								},
								{
									"name" : "channel_button_04",
									"type" : "radio_button",

									"x" : 0,
									"y" : 93,

									"default_image" : ROOT_PATH + "channel_button_01.sub",
									"over_image" : ROOT_PATH + "channel_button_02.sub",
									"down_image" : ROOT_PATH + "channel_button_03.sub",

									"children" : (
										{
											"name" : "channel_text_04",
											"type" : "text",

											"x" : 26,
											"y" : -1,

											"vertical_align" : "center",
											"text_vertical_align" : "center",

											"color" : FONT_COLOR,

											"text" : localeinfo.PANEL_CHANNEL_4,
										},
										{
											"name" : "channel_select_04",
											"type" : "image",

											"x" : 33,
											"y" : 0,

											"horizontal_align" : "right",
											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_select.sub",
										},
										{
											"name" : "channel_select_04",
											"type" : "image",

											"x" : 33,
											"y" : 0,

											"horizontal_align" : "right",
											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_select.sub",
										},
										{
											"name" : "channel_status_off_04",
											"type" : "image",

											"x" : 0,
											"y" : 0,

											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_status_off.sub",
										},
										{
											"name" : "channel_status_on_04",
											"type" : "image",

											"x" : 0,
											"y" : 0,

											"vertical_align" : "center",

											"image" : ROOT_PATH + "channel_status_on.sub",
										},
									),
								},
								
							),
						},
					),
				},
			),
		},
	),
}