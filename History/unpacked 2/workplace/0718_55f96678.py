# coding: latin_1

import localeinfo

WINDOW_WIDTH = 255
WINDOW_HEIGHT = 30

MEMBER_BUTTON_PATH = "d:/ymir work/ui/game/windows/"

window = {
	"name" : "ChangeCurrencyWindow",
	"style" : ("float",),
	"x" : 274,
	"y" : (SCREEN_HEIGHT - 398) / 2,
	"width" : WINDOW_WIDTH,
	"height" : WINDOW_HEIGHT * 2,
	"children":
	(
		{
			"name" : "board",
			"type" : "board",
			"style" : ("attach", "ltr"),
			"x" : 0,
			"y" : 0,
			"width" : WINDOW_WIDTH,
			"height" : WINDOW_HEIGHT,
			"children":
			(
				{
					"name" : "border_a",
					"type" : "border_a",
					"size_skip" : True,
					"x" : 7,
					"y" : 8,
					"width" : 240,
					"height" : 48,
					"children" :
					(
						{
							"name" : "AttackerButton",
							"type" : "button",
							"x" : 13,
							"y" : 5,
							"default_image" : MEMBER_BUTTON_PATH + "party_state_attacker_01.sub",
							"over_image" : MEMBER_BUTTON_PATH + "party_state_attacker_02.sub",
							"down_image" : MEMBER_BUTTON_PATH + "party_state_attacker_03.sub",
						},
						{
							"name" : "BerserkerButton",
							"type" : "button",
							"x" : 13 + 38,
							"y" : 5,
							"default_image" : MEMBER_BUTTON_PATH + "party_state_berserker_01.sub",
							"over_image" : MEMBER_BUTTON_PATH + "party_state_berserker_02.sub",
							"down_image" : MEMBER_BUTTON_PATH + "party_state_berserker_03.sub",
						},	
						{
							"name" : "TankerButton",
							"type" : "button",
							"x" : 13 + 38 * 2,
							"y" : 5,
							"default_image" : MEMBER_BUTTON_PATH + "party_state_tanker_01.sub",
							"over_image" : MEMBER_BUTTON_PATH + "party_state_tanker_02.sub",
							"down_image" : MEMBER_BUTTON_PATH + "party_state_tanker_03.sub",
						},
						{
							"name" : "DefenderButton",
							"type" : "button",
							"x" : 13 + 38 * 3,
							"y" : 5,
							"default_image" : MEMBER_BUTTON_PATH + "party_state_defender_01.sub",
							"over_image" : MEMBER_BUTTON_PATH + "party_state_defender_02.sub",
							"down_image" : MEMBER_BUTTON_PATH + "party_state_defender_03.sub",
						},
						{
							"name" : "BufferButton",
							"type" : "button",
							"x" : 13 + 38 * 4,
							"y" : 5,
							"default_image" : MEMBER_BUTTON_PATH + "party_state_buffer_01.sub",
							"over_image" : MEMBER_BUTTON_PATH + "party_state_buffer_02.sub",
							"down_image" : MEMBER_BUTTON_PATH + "party_state_buffer_03.sub",
						},
						{
							"name" : "SkillMasterButton",
							"type" : "button",
							"x" : 13 + 38 * 5,
							"y" : 5,
							"default_image" : MEMBER_BUTTON_PATH + "party_state_skill_master_01.sub",
							"over_image" : MEMBER_BUTTON_PATH + "party_state_skill_master_02.sub",
							"down_image" : MEMBER_BUTTON_PATH + "party_state_skill_master_03.sub",
						},
					),
				},
			),
		},
	),
}
