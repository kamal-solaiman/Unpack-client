# coding: utf-8

import app
import uiscriptlocale

window = {
	"name" : "GameWindow",
	"style" : ("not_pick",),
	"x" : 0,
	"y" : 0,
	"width" : SCREEN_WIDTH,
	"height" : SCREEN_HEIGHT,
	"children" :
	[
		{
			"name" : "HelpButton",
			"type" : "button",
			"x" : 50,
			"y" : SCREEN_HEIGHT - 170,
			"default_image" : "d:/ymir work/ui/game/windows/btn_bigplus_up.sub",
			"over_image" : "d:/ymir work/ui/game/windows/btn_bigplus_over.sub",
			"down_image" : "d:/ymir work/ui/game/windows/btn_bigplus_down.sub",
			"children" :
			(
				{
					"name" : "HelpButtonLabel",
					"type" : "text",
					"x" : 16,
					"y" : 40,
					"text" : uiscriptlocale.GAME_HELP,
					"r" : 1.0,
					"g" : 1.0,
					"b" : 1.0,
					"a" : 1.0,
					"text_horizontal_align" : "center",
				},
			),
		},
		{
			"name" : "QuestButton",
			"type" : "button",
			"x" : SCREEN_WIDTH - 50 - 32,
			"y" : SCREEN_HEIGHT - 170,
			"default_image" : "d:/ymir work/ui/game/windows/btn_bigplus_up.sub",
			"over_image" : "d:/ymir work/ui/game/windows/btn_bigplus_over.sub",
			"down_image" : "d:/ymir work/ui/game/windows/btn_bigplus_down.sub",
			"children" : 
			(
				{
					"name" : "QuestButtonLabel",
					"type" : "text",
					"x" : 16,
					"y" : 40,
					"text" : uiscriptlocale.GAME_QUEST,
					"r" : 1.0,
					"g" : 1.0,
					"b" : 1.0,
					"a" : 1.0,
					"text_horizontal_align" : "center",
				},
			),
		},
		{
			"name" : "StatusPlusButton",
			"type" : "button",
			"x" : SCREEN_WIDTH - 80,
			"y" : SCREEN_HEIGHT - 230,
			"default_image" : "d:/ymir work/ui/game/windows/btn_bigplus_up.sub",
			"over_image" : "d:/ymir work/ui/game/windows/btn_bigplus_over.sub",
			"down_image" : "d:/ymir work/ui/game/windows/btn_bigplus_down.sub",
			"children" :
			(
				{
					"name" : "StatusPlusLabel",
					"type" : "text",
					"x" : 16,
					"y" : 40,
					"text" : uiscriptlocale.GAME_STAT_UP,
					"r" : 1.0,
					"g" : 1.0,
					"b" : 1.0,
					"a" : 1.0,
					"text_horizontal_align" : "center",
				},
			),
		},
		{
			"name" : "SkillPlusButton",
			"type" : "button",
			"x" : SCREEN_WIDTH - 80,
			"y" : SCREEN_HEIGHT - 300,
			"default_image" : "d:/ymir work/ui/game/windows/btn_bigplus_up.sub",
			"over_image" : "d:/ymir work/ui/game/windows/btn_bigplus_over.sub",
			"down_image" : "d:/ymir work/ui/game/windows/btn_bigplus_down.sub",
			"children" :
			(
				{
					"name" : "SkillPlusLabel",
					"type" : "text",
					"x" : 16,
					"y" : 40,
					"text" : uiscriptlocale.GAME_SKILL_UP,
					"r" : 1.0,
					"g" : 1.0,
					"b" : 1.0,
					"a" : 1.0,
					"text_horizontal_align" : "center",
				},
			),
		},
		{
			"name" : "ExitObserver",
			"type" : "button",
			"x" : SCREEN_WIDTH - 50 - 32,
			"y" : SCREEN_HEIGHT - 170,
			"default_image" : "d:/ymir work/ui/game/windows/btn_bigplus_up.sub",
			"over_image" : "d:/ymir work/ui/game/windows/btn_bigplus_over.sub",
			"down_image" : "d:/ymir work/ui/game/windows/btn_bigplus_down.sub",
			"children" :
			(
				{
					"name" : "ExitObserverButtonName",
					"type" : "text",
					"x" : 16,
					"y" : 40,
					"text" : uiscriptlocale.GAME_EXIT_OBSERVER,
					"r" : 1.0,
					"g" : 1.0,
					"b" : 1.0,
					"a" : 1.0,
					"text_horizontal_align" : "center",
				},
			),
		},
		{
			"name" : "BuildGuildBuilding",
			"type" : "button",
			"x" : SCREEN_WIDTH - 50 - 32,
			"y" : SCREEN_HEIGHT - 170,
			"default_image" : "d:/ymir work/ui/game/windows/btn_bigplus_up.sub",
			"over_image" : "d:/ymir work/ui/game/windows/btn_bigplus_over.sub",
			"down_image" : "d:/ymir work/ui/game/windows/btn_bigplus_down.sub",
			"children" :
			(
				{
					"name" : "BuildGuildBuildingButtonName",
					"type" : "text",
					"x" : 16,
					"y" : 40,
					"text": uiscriptlocale.GUILD_BUILDING_TITLE,
					"r" : 1.0,
					"g" : 1.0,
					"b" : 1.0,
					"a" : 1.0,
					"text_horizontal_align" : "center",
				},
			),
		},
		{
			"name" : "levelcap_button",
			"type" : "button",
			"x" : 68,
			"y" : SCREEN_HEIGHT - 190,
			"default_image" : "d:/ymir work/ui/game/level_cap/button_normal.png",
			"over_image" : "d:/ymir work/ui/game/level_cap/button_hover.png",
			"down_image" : "d:/ymir work/ui/game/level_cap/button_down.png",
			"tooltip_text" : uiscriptlocale.DUNGEON_INFO_ADDON_LEVEL_TITLE,
		},
	],
}

if app.ENABLE_REWARD_SYSTEM:
	window["children"].append({
		"name" : "ChallengeMapButton",
		"type" : "button",
		"x" : SCREEN_WIDTH - 135,
		"y" : SCREEN_HEIGHT - 300,
		"width" : 37,
		"height" : 37,
		"default_image" : "d:/ymir work/ui/game/new_taskbar/btn_challenge_norm.png",
		"over_image" : "d:/ymir work/ui/game/new_taskbar/btn_challenge_hover.png",
		"down_image" : "d:/ymir work/ui/game/new_taskbar/btn_challenge_select.png",
		"children" :
		(
			{
				"name" : "ChallengeMapLabel",
				"type" : "text",
				"x" : 18,
				"y" : 40,
				"text" : getattr(uiscriptlocale, "GAME_CHALLENGE_MAP", "Challenges"),
				"r" : 1.0,
				"g" : 1.0,
				"b" : 1.0,
				"a" : 1.0,
				"text_horizontal_align" : "center",
			},
		),
	})
