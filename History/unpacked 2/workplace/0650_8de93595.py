import uiScriptLocale
import localeinfo

NEW  = "d:/ymir work/ui/newlogin/"
OLD  = "dragon3/login/"

PANEL_W = 410

window = {
	"name" : "LoginWindow",
	"x" : 0, "y" : 0,
	"width" : SCREEN_WIDTH,
	"height" : SCREEN_HEIGHT,
	"children" :
	(
		# ---- full-screen backdrop (single server: both point at same art) ----
		{
			"name" : "bg_dragon",
			"type" : "expanded_image",
			"x" : 0, "y" : 0,
			"horizontal_align" : "center",
			"x_scale" : float(SCREEN_WIDTH) / 1920.0,
			"y_scale" : float(SCREEN_HEIGHT) / 1080.0,
			"width" : SCREEN_WIDTH,
			"height" : SCREEN_HEIGHT,
			"image" : NEW + "background.jpg",
		},
		{
			"name" : "bg_syrax",
			"type" : "expanded_image",
			"x" : 0, "y" : 0,
			"horizontal_align" : "center",
			"x_scale" : float(SCREEN_WIDTH) / 1920.0,
			"y_scale" : float(SCREEN_HEIGHT) / 1080.0,
			"width" : SCREEN_WIDTH,
			"height" : SCREEN_HEIGHT,
			"image" : NEW + "background.jpg",
		},

		# ---- right-anchored full-height side panel (LTR authoring -> mirrors right for Arabic) ----
		{
			"name" : "panel",
			"type" : "expanded_image",
			"x" : 0, "y" : 0,
			"width" : PANEL_W,
			"height" : SCREEN_HEIGHT,
			"x_scale" : 1.0,
			"y_scale" : float(SCREEN_HEIGHT) / 1080.0,
			"image" : NEW + "LeftBG.png",
			"children" :
			(
				# logo
				{
					"name" : "logo",
					"type" : "image",
					"x" : 0, "y" : 29,
					"horizontal_align" : "center",
					"image" : NEW + "logo.png",
				},

				# close
				{
					"name" : "exit_button",
					"type" : "button",
					"x" : 192, "y" : 18,
					"horizontal_align" : "center",
					"default_image" : NEW + "close_button_01.png",
					"over_image" : NEW + "close_button_02.png",
					"down_image" : NEW + "close_button_03.png",
				},

				# username
				{
					"name" : "input_user",
					"type" : "image",
					"x" : 0, "y" : 141,
					"horizontal_align" : "center",
					"image" : NEW + "username_image.png",
					"children" :
					(
						{
							"name" : "id",
							"type" : "editline",
							"x" : 40, "y" : 16,
							"width" : 250, "height" : 16,
							"input_limit" : 16,
						},
					),
				},

				# password
				{
					"name" : "input_password",
					"type" : "image",
					"x" : 0, "y" : 205,
					"horizontal_align" : "center",
					"image" : NEW + "password_image.png",
					"children" :
					(
						{
							"name" : "pwd",
							"type" : "editline",
							"x" : 40, "y" : 16,
							"width" : 250, "height" : 16,
							"input_limit" : 16,
							"secret_flag" : 1,
						},
					),
				},

				# saved-last-character checkbox (visual placeholder; wired in a later phase)
				{
					"name" : "saved_char_check",
					"type" : "image",
					"x" : -140, "y" : 265,
					"horizontal_align" : "center",
					"image" : NEW + "unchecked.png",
				},
				{
					"name" : "saved_char_label",
					"type" : "text",
					"x" : -112, "y" : 267,
					"horizontal_align" : "center",
					"text" : getattr(localeinfo, "QUICK_LOGIN_AUTOSAVE_TIP", "Saved last played character"),
					"color" : 0xffd4c1a5,
				},

				# login
				{
					"name" : "login_button",
					"type" : "button",
					"x" : 0, "y" : 314,
					"horizontal_align" : "center",
					"default_image" : NEW + "login_01.png",
					"over_image" : NEW + "login_02.png",
					"down_image" : NEW + "login_03.png",
				},

				# quick-login trigger (portrait-strip reskin comes in a later phase)
				{
					"name" : "fast_login_btn",
					"type" : "button",
					"x" : 0, "y" : 929,
					"horizontal_align" : "center",
					"default_image" : OLD + "btn_quick_01.png",
					"over_image" : OLD + "btn_quick_02.png",
					"down_image" : OLD + "btn_quick_03.png",
				},

				# ---- channel selector (collapsed row; click toggles the list) ----
				{
					"name" : "channel_selector",
					"type" : "button",
					"x" : 0, "y" : 392,
					"horizontal_align" : "center",
					"default_image" : NEW + "ch_03.png",
					"over_image" : NEW + "ch_02.png",
					"down_image" : NEW + "ch_03.png",
					"children" :
					(
						{ "name" : "channel_selector_text", "type" : "text", "style" : ("not_pick",), "x" : 0, "y" : 12, "fontsize" : "LARGE", "text" : localeinfo.PANEL_CHANNEL_1, "color" : 0xffd4c1a5, "outline" : 1, "horizontal_align" : "center", "text_horizontal_align" : "center", },
						{ "name" : "channel_selector_dot", "type" : "image", "style" : ("not_pick",), "x" : 18, "y" : 8, "image" : NEW + "off_image.png", },
					),
				},

				# ---- channel list (dropdown container; shown only when open) ----
				{
					"name" : "channel_list_bg",
					"type" : "image",
					"x" : 0, "y" : 436,
					"horizontal_align" : "center",
					"image" : NEW + "channels_accounts_big.png",
					"children" :
					(
						{
							"name" : "select_btn_ch1",
							"type" : "radio_button",
							"x" : 0, "y" : 3,
							"horizontal_align" : "center",
							"default_image" : NEW + "ch_01.png",
							"over_image" : NEW + "ch_02.png",
							"down_image" : NEW + "ch_03.png",
							"children" :
							(
								{ "name" : "state_ch1", "type" : "text", "x" : 0, "y" : 12, "fontsize" : "LARGE", "text" : localeinfo.PANEL_CHANNEL_1, "color" : 0xffd4c1a5, "outline" : 1, "horizontal_align" : "center", "text_horizontal_align" : "center", },
								{ "name" : "ch1_online",  "type" : "image", "x" : 18, "y" : 8, "image" : NEW + "on_image.png", },
								{ "name" : "ch1_offline", "type" : "image", "x" : 20, "y" : 10, "image" : NEW + "off_image.png", },
							),
						},
						{
							"name" : "select_btn_ch2",
							"type" : "radio_button",
							"x" : 0, "y" : 44,
							"horizontal_align" : "center",
							"default_image" : NEW + "ch_01.png",
							"over_image" : NEW + "ch_02.png",
							"down_image" : NEW + "ch_03.png",
							"children" :
							(
								{ "name" : "state_ch2", "type" : "text", "x" : 0, "y" : 12, "fontsize" : "LARGE", "text" : localeinfo.PANEL_CHANNEL_2, "color" : 0xffd4c1a5, "outline" : 1, "horizontal_align" : "center", "text_horizontal_align" : "center", },
								{ "name" : "ch2_online",  "type" : "image", "x" : 18, "y" : 8, "image" : NEW + "on_image.png", },
								{ "name" : "ch2_offline", "type" : "image", "x" : 20, "y" : 10, "image" : NEW + "off_image.png", },
							),
						},
						{
							"name" : "select_btn_ch3",
							"type" : "radio_button",
							"x" : 0, "y" : 86,
							"horizontal_align" : "center",
							"default_image" : NEW + "ch_01.png",
							"over_image" : NEW + "ch_02.png",
							"down_image" : NEW + "ch_03.png",
							"children" :
							(
								{ "name" : "state_ch3", "type" : "text", "x" : 0, "y" : 12, "fontsize" : "LARGE", "text" : localeinfo.PANEL_CHANNEL_3, "color" : 0xffd4c1a5, "outline" : 1, "horizontal_align" : "center", "text_horizontal_align" : "center", },
								{ "name" : "ch3_online",  "type" : "image", "x" : 18, "y" : 8, "image" : NEW + "on_image.png", },
								{ "name" : "ch3_offline", "type" : "image", "x" : 20, "y" : 10, "image" : NEW + "off_image.png", },
							),
						},
						{
							"name" : "select_btn_ch4",
							"type" : "radio_button",
							"x" : 0, "y" : 128,
							"horizontal_align" : "center",
							"default_image" : NEW + "ch_01.png",
							"over_image" : NEW + "ch_02.png",
							"down_image" : NEW + "ch_03.png",
							"children" :
							(
								{ "name" : "state_ch4", "type" : "text", "x" : 0, "y" : 12, "fontsize" : "LARGE", "text" : localeinfo.PANEL_CHANNEL_4, "color" : 0xffd4c1a5, "outline" : 1, "horizontal_align" : "center", "text_horizontal_align" : "center", },
								{ "name" : "ch4_online",  "type" : "image", "x" : 18, "y" : 8, "image" : NEW + "on_image.png", },
								{ "name" : "ch4_offline", "type" : "image", "x" : 20, "y" : 10, "image" : NEW + "off_image.png", },
							),
						},
					),
				},

				# page cycler for saved accounts (retired once the scroll list lands)
				{
					"name" : "account_dropdown",
					"type" : "button",
					"x" : 150, "y" : 648,
					"horizontal_align" : "center",
					"default_image" : OLD + "btn_drop_01.png",
					"over_image" : OLD + "btn_drop_02.png",
					"down_image" : OLD + "btn_drop_03.png",
				},

				# ---- saved accounts: clip viewport + scroll content (all 12 rows f1-f12) ----
				{
					"name" : "accounts_viewport",
					"type" : "window",
					"x" : 0, "y" : 610 + 22,
					"width" : 316, "height" : 183,
					"horizontal_align" : "center",
					"children" :
					(
					{
						"name" : "accounts_bg",
						"type" : "image",
						"x" : 0, "y" : 0,
						"image" : NEW + "accounts_big.png",
						"style" : ("not_pick",),
					},
					{
						"name" : "accounts_content",
						"type" : "window",
						"x" : 0, "y" : 0,
						"width" : 316, "height" : 552,
						"horizontal_align" : "center",
						"children" :
						(
				{
					"name" : "BoardRight_1",
					"type" : "window",
					"x" : 0, "y" : 0,
					"width" : 316, "height" : 184,
					"horizontal_align" : "center",
					"children" :
					(
						{
							"name" : "f1_login_button", "type" : "button", "x" : 5, "y" : 1, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f1_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f1_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f1_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
						{
							"name" : "f2_login_button", "type" : "button", "x" : 5, "y" : 46 + 1, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f2_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f2_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f2_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
						{
							"name" : "f3_login_button", "type" : "button", "x" : 5, "y" : 92 + 1, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f3_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f3_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f3_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
						{
							"name" : "f4_login_button", "type" : "button", "x" : 5, "y" : 138 + 1, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f4_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f4_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f4_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
					),
				},

				# ---- saved accounts page 2 (F5-F8, hidden by code until dropdown cycles) ----
				{
					"name" : "BoardRight_2",
					"type" : "window",
					"x" : 0, "y" : 184,
					"width" : 316, "height" : 184,
					"horizontal_align" : "center",
					"children" :
					(
						{
							"name" : "f5_login_button", "type" : "button", "x" : 5, "y" : 1, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f5_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f5_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f5_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
						{
							"name" : "f6_login_button", "type" : "button", "x" : 5, "y" : 47, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f6_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f6_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f6_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
						{
							"name" : "f7_login_button", "type" : "button", "x" : 5, "y" : 93, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f7_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f7_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f7_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
						{
							"name" : "f8_login_button", "type" : "button", "x" : 5, "y" : 139, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f8_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f8_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f8_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
					),
				},

				# ---- saved accounts page 3 (F9-F12, hidden by code) ----
				{
					"name" : "BoardRight_3",
					"type" : "window",
					"x" : 0, "y" : 368,
					"width" : 316, "height" : 184,
					"horizontal_align" : "center",
					"children" :
					(
						{
							"name" : "f9_login_button", "type" : "button", "x" : 5, "y" : 1, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f9_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f9_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f9_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
						{
							"name" : "f10_login_button", "type" : "button", "x" : 5, "y" : 47, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f10_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f10_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f10_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
						{
							"name" : "f11_login_button", "type" : "button", "x" : 5, "y" : 93, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f11_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f11_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f11_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
						{
							"name" : "f12_login_button", "type" : "button", "x" : 5, "y" : 139, "horizontal_align" : "center",
							"default_image" : NEW + "account_button_01.png", "over_image" : NEW + "account_button_02.png", "down_image" : NEW + "account_button_03.png",
							"children" :
							(
								{ "name" : "f12_account_text", "type" : "text", "x" : 60, "y" : 14, "fontsize" : "LARGE", "text" : "Free Slot", },
								{ "name" : "f12_save_button",   "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "save_acc_01.png",   "over_image" : NEW + "save_acc_02.png",   "down_image" : NEW + "save_acc_03.png", },
								{ "name" : "f12_delete_button", "type" : "button", "x" : 262, "y" : 10, "default_image" : NEW + "delete_acc_01.png", "over_image" : NEW + "delete_acc_02.png", "down_image" : NEW + "delete_acc_03.png", },
							),
						},
					),
				},

						),
						},
					),
				},

				# ---- button area: forgot links (bottom-anchored in code) ----
				{
					"name" : "button_area",
					"type" : "window",
					"x" : 0, "y" : 880,
					"width" : PANEL_W, "height" : 64,
					"horizontal_align" : "center",
					"children" :
					(
						# row 1 - forgot password (plate -> text -> button)
						{
							"name" : "forgot_pw_bg", "type" : "image",
							"x" : -5, "y" : 3, "horizontal_align" : "center",
							"style" : ("not_pick",),
							"image" : NEW + "forgot_bg.png",
						},
						{
							"name" : "forgot_pw_text", "type" : "text",
							"x" : -25, "y" : 2, "horizontal_align" : "center", "text_horizontal_align" : "center",
							"text" : getattr(localeinfo, "LOGIN_FORGOT_PASSWORD", "Forgot your password?"),
							"color" : 0xffd4c1a5, "outline" : 1,
						},
						{
							"name" : "register_btn", "type" : "button",
							"x" : 75, "y" : 0, "horizontal_align" : "center",
							"default_image" : NEW + "forgot_norm.png",
							"over_image" : NEW + "forgot_hover.png",
							"down_image" : NEW + "forgot_down.png",
						},

						# row 2 - forgot username (plate -> text -> button)
						{
							"name" : "forgot_user_bg", "type" : "image",
							"x" : -5, "y" : 35, "horizontal_align" : "center",
							"style" : ("not_pick",),
							"image" : NEW + "forgot_bg.png",
						},
						{
							"name" : "forgot_user_text", "type" : "text",
							"x" : -25, "y" : 34, "horizontal_align" : "center", "text_horizontal_align" : "center",
							"text" : getattr(localeinfo, "LOGIN_FORGOT_USERNAME", "Forgot your username?"),
							"color" : 0xffd4c1a5, "outline" : 1,
						},
						{
							"name" : "forgot_user_btn", "type" : "button",
							"x" : 75, "y" : 32, "horizontal_align" : "center",
							"default_image" : NEW + "forgot_norm.png",
							"over_image" : NEW + "forgot_hover.png",
							"down_image" : NEW + "forgot_down.png",
						},
					),
				},

				# hidden server-select radios (kept for binding; single server for now)
				{
					"name" : "newselect1",
					"type" : "radio_button",
					"x" : 0, "y" : 940,
					"horizontal_align" : "center",
					"default_image" : OLD + "srv_drg_normal.png",
					"over_image" : OLD + "srv_drg_hover.png",
					"down_image" : OLD + "srv_drg_down.png",
				},
				{
					"name" : "newselect2",
					"type" : "radio_button",
					"x" : 0, "y" : 990,
					"horizontal_align" : "center",
					"default_image" : OLD + "srv_syr_normal.png",
					"over_image" : OLD + "srv_syr_hover.png",
					"down_image" : OLD + "srv_syr_down.png",
				},
			),
		},
	),
}
