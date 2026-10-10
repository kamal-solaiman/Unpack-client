# coding: latin_1
#
# Solo Leadership role picker (ENABLE_SOLO_LEADERSHIP_BONUS).
#
# Reuses the party-leadership role banner icons (party_state_*), laid out as a
# single horizontal strip so it matches the in-game party role UI exactly.
# Role order left->right = /leadership_bonus index 1..6:
#   1 Attacker  2 Tanker  3 Buffer  4 Skill Master  5 Berserker(Haste)  6 Defender
# uicharacter.py binds role_button_1..6, sets each tooltip from the
# constinfo.SOLO_LEADERSHIP_* cache, and marks the active role by pressing it
# down. Clicking a role sends "/leadership_bonus <idx>"; the server answers with
# a fresh LeadershipBonus push that re-enters RefreshSoloLeadership.

ROLE_ICON_PATH = "d:/ymir work/ui/game/windows/"

ICON_WIDTH  = 22
ICON_HEIGHT = 36
ICON_Y      = 8
ICON_STEP   = 34
LEFT_PAD    = 11

BOARD_WIDTH  = LEFT_PAD * 2 + ICON_WIDTH + ICON_STEP * 5
BOARD_HEIGHT = ICON_Y * 2 + ICON_HEIGHT

window = {
	"name" : "LeadershipBoard",
	"style" : ("movable", "float",),

	"x" : 0,
	"y" : 0,

	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,

	"children" :
	(
		{
			"name" : "board",
			"type" : "thinboard",
			"style" : ("attach",),

			"x" : 0,
			"y" : 0,

			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,

			"children" :
			(
				{
					"name" : "role_button_1",
					"type" : "button",
					"x" : LEFT_PAD + ICON_STEP * 0,
					"y" : ICON_Y,
					"default_image" : ROLE_ICON_PATH + "party_state_attacker_01.sub",
					"over_image"    : ROLE_ICON_PATH + "party_state_attacker_02.sub",
					"down_image"    : ROLE_ICON_PATH + "party_state_attacker_03.sub",
				},
				{
					"name" : "role_button_2",
					"type" : "button",
					"x" : LEFT_PAD + ICON_STEP * 1,
					"y" : ICON_Y,
					"default_image" : ROLE_ICON_PATH + "party_state_tanker_01.sub",
					"over_image"    : ROLE_ICON_PATH + "party_state_tanker_02.sub",
					"down_image"    : ROLE_ICON_PATH + "party_state_tanker_03.sub",
				},
				{
					"name" : "role_button_3",
					"type" : "button",
					"x" : LEFT_PAD + ICON_STEP * 2,
					"y" : ICON_Y,
					"default_image" : ROLE_ICON_PATH + "party_state_buffer_01.sub",
					"over_image"    : ROLE_ICON_PATH + "party_state_buffer_02.sub",
					"down_image"    : ROLE_ICON_PATH + "party_state_buffer_03.sub",
				},
				{
					"name" : "role_button_4",
					"type" : "button",
					"x" : LEFT_PAD + ICON_STEP * 3,
					"y" : ICON_Y,
					"default_image" : ROLE_ICON_PATH + "party_state_skill_master_01.sub",
					"over_image"    : ROLE_ICON_PATH + "party_state_skill_master_02.sub",
					"down_image"    : ROLE_ICON_PATH + "party_state_skill_master_03.sub",
				},
				{
					"name" : "role_button_5",
					"type" : "button",
					"x" : LEFT_PAD + ICON_STEP * 4,
					"y" : ICON_Y,
					"default_image" : ROLE_ICON_PATH + "party_state_berserker_01.sub",
					"over_image"    : ROLE_ICON_PATH + "party_state_berserker_02.sub",
					"down_image"    : ROLE_ICON_PATH + "party_state_berserker_03.sub",
				},
				{
					"name" : "role_button_6",
					"type" : "button",
					"x" : LEFT_PAD + ICON_STEP * 5,
					"y" : ICON_Y,
					"default_image" : ROLE_ICON_PATH + "party_state_defender_01.sub",
					"over_image"    : ROLE_ICON_PATH + "party_state_defender_02.sub",
					"down_image"    : ROLE_ICON_PATH + "party_state_defender_03.sub",
				},
			),
		},
	),
}
