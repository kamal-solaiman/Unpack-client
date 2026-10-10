# coding: latin_1

import uiscriptlocale

ROOT = "d:/ymir work/ui/game/taskbar/"

BUTTON_COUNT = 3

if AUTO_HUNT_RUBINUM:
	BUTTON_COUNT += 2

window = {
	"name" : "ButtonWindow",
	"x" : 0,
	"y" : 0,
	"width" : 32,
	"height" : 32 * BUTTON_COUNT,
	"children" :
	(
		{
			"name" : "button_move_and_attack",
			"type" : "button",
			"x" : 0,
			"y" : 0,
			"tooltip_text" : uiscriptlocale.MOUSEBUTTON_ATTACK,
			"tooltip_x" : -20,
			"tooltip_y" : 9,
			"tooltip_text_sort" : "right",
			"default_image" : ROOT + "Mouse_Button_Attack_01.sub",
			"over_image" : ROOT + "Mouse_Button_Attack_02.sub",
			"down_image" : ROOT + "Mouse_Button_Attack_03.sub",
		},
		{
			"name" : "button_auto_attack",
			"type" : "button",
			"x" : 0,
			"y" : 32,
			"tooltip_text" : uiscriptlocale.MOUSEBUTTON_AUTO_ATTACK,
			"tooltip_x" : -20,
			"tooltip_y" : 9,
			"tooltip_text_sort" : "right",
			"default_image" : ROOT + "Mouse_Button_Auto_Attack_01.sub",
			"over_image" : ROOT + "Mouse_Button_Auto_Attack_02.sub",
			"down_image" : ROOT + "Mouse_Button_Auto_Attack_03.sub",
		},
		{
			"name" : "button_camera",
			"type" : "button",
			"x" : 0,
			"y" : 64,
			"tooltip_text" : uiscriptlocale.MOUSEBUTTON_CAMERA,
			"tooltip_x" : -20,
			"tooltip_y" : 9,
			"tooltip_text_sort" : "right",
			"default_image" : ROOT + "Mouse_Button_Camera_01.sub",
			"over_image" : ROOT + "Mouse_Button_Camera_02.sub",
			"down_image" : ROOT + "Mouse_Button_Camera_03.sub",
		},
		{
			"name" : "button_auto_attack_queue",
			"type" : "button",
			"x" : 0,
			"y" : 64 + 32,
			"tooltip_text" : getattr(uiscriptlocale, "MOUSEBUTTON_AUTO_ATTACK_QUEUE_LEFT", uiscriptlocale.MOUSEBUTTON_AUTO_ATTACK_QUEUE),
			"tooltip_x" : -20,
			"tooltip_y" : 9,
			"tooltip_text_sort" : "right",
			"default_image" : "d:/ymir work/ui/ltaskbar_metin_queue_2_normal.png",
			"over_image" : "d:/ymir work/ui/ltaskbar_metin_queue_2_hover.png",
			"down_image" : "d:/ymir work/ui/ltaskbar_metin_queue_2_down.png",
		},
		{
			"name" : "button_auto_attack_queue_area",
			"type" : "button",
			"x" : 0,
			"y" : 64 + 64,
			"tooltip_text" : getattr(uiscriptlocale, "MOUSEBUTTON_AUTO_ATTACK_QUEUE_AREA", uiscriptlocale.MOUSEBUTTON_AUTO_ATTACK_QUEUE),
			"tooltip_x" : -20,
			"tooltip_y" : 9,
			"tooltip_text_sort" : "right",
			"default_image" : "d:/ymir work/ui/only_taskbar_metin_queue_2_normal.png",
			"over_image" : "d:/ymir work/ui/only_taskbar_metin_queue_2_hover.png",
			"down_image" : "d:/ymir work/ui/only_taskbar_metin_queue_2_down.png",
		},
	),
}
