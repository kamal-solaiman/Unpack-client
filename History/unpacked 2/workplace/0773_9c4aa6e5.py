# coding: latin_1

import uiscriptlocale

ROOT = "d:/ymir work/ui/game/taskbar/"

BUTTON_COUNT = 3

if AUTO_HUNT_RUBINUM:
	BUTTON_COUNT += 2

window = {
	"name" : "RightButtonWindow",
	"x" : 0,
	"y" : 0,
	"width" : 32 * BUTTON_COUNT,
	"height" : 32,
	"children" :
	(
		{
			"name" : "button_move_and_attack",
			"type" : "button",
			"x" : 0,
			"y" : 0,
			"tooltip_text" : uiscriptlocale.MOUSEBUTTON_ATTACK,
			"tooltip_x" : -40,
			"tooltip_y" : 9,
			"default_image" : ROOT + "Mouse_Button_Attack_01.sub",
			"over_image" : ROOT + "Mouse_Button_Attack_02.sub",
			"down_image" : ROOT + "Mouse_Button_Attack_03.sub",
		},
		{
			"name" : "button_camera",
			"type" : "button",
			"x" : 32,
			"y" : 0,
			"tooltip_text" : uiscriptlocale.MOUSEBUTTON_CAMERA,
			"tooltip_x" : -40,
			"tooltip_y" : 9,
			"default_image" : ROOT + "Mouse_Button_Camera_01.sub",
			"over_image" : ROOT + "Mouse_Button_Camera_02.sub",
			"down_image" : ROOT + "Mouse_Button_Camera_03.sub",
		},
		{
			"name" : "button_skill",
			"type" : "button",
			"x" : 64,
			"y" : 0,
			"tooltip_text" : uiscriptlocale.MOUSEBUTTON_SKILL,
			"tooltip_x" : -40,
			"tooltip_y" : 9,
			"default_image" : ROOT + "Mouse_Button_Skill_01.sub",
			"over_image" : ROOT + "Mouse_Button_Skill_02.sub",
			"down_image" : ROOT + "Mouse_Button_Skill_03.sub",
		},
		{
			"name" : "button_auto_attack_queue",
			"type" : "button",
			"x" : 96,
			"y" : 0,
			"tooltip_text" : uiscriptlocale.MOUSEBUTTON_AUTO_ATTACK_QUEUE,
			"tooltip_x" : -40,
			"tooltip_y" : 9,
			"default_image" : "d:/ymir work/ui/taskbar_metin_queue_2_normal.png",
			"over_image" : "d:/ymir work/ui/taskbar_metin_queue_2_hover.png",
			"down_image" : "d:/ymir work/ui/taskbar_metin_queue_2_down.png",
		},
		{
			"name" : "button_auto_attack_queue_area",
			"type" : "button",
			"x" : 128,
			"y" : 0,
			"tooltip_text" : getattr(uiscriptlocale, "MOUSEBUTTON_AUTO_ATTACK_QUEUE_AREA", uiscriptlocale.MOUSEBUTTON_AUTO_ATTACK_QUEUE),
			"tooltip_x" : -40,
			"tooltip_y" : 9,
			"default_image" : "d:/ymir work/ui/only_taskbar_metin_queue_2_normal.png",
			"over_image" : "d:/ymir work/ui/only_taskbar_metin_queue_2_hover.png",
			"down_image" : "d:/ymir work/ui/only_taskbar_metin_queue_2_down.png",
		},
	),
}
