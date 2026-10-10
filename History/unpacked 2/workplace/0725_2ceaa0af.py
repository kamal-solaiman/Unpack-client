import localeinfo

window = {
	"name" : "PartyMemberWindow",
	"x" : 20,
	"y" : 250,
	"style" : ("float","movable",),
	"width" : 200,
	"height" : 200,
	"children" :
	(
		{
			"name" : "board",
			"type" : "image",
			"x" : 0,
			"y" : 0,
			"style" : ("not_pick",),
			"horizontal_align" : "center",
			"vertical_align" : "center",
			"image" : "d:/ymir work/ui/game/event_partywar.png",
			
			
			"children" :
			(

				{
					"name" : "TitleText1",
					"type" : "text",
					"x" : 0,
					"y" : 65,
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
					"text" : localeinfo.PARTY_WAR_TIME_TO_START,
					"fontname" : "Tahoma Bold:15",
					"children" :
					(
						
						{ "name" : "LeftTime", "type" : "text", "x" : 0, "y" : 20, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : "None" ,"fontname" : "Tahoma Bold:15",},
					),
				},
			),
		},
		{
			"name" : "buttonJoin",
			"type" : "button",
			"x" : 0,
			"y" : 80,
			"horizontal_align" : "center",
			"vertical_align" : "center",
			"default_image" : "d:/ymir work/ui/public/large_button_01.sub",
			"over_image" : "d:/ymir work/ui/public/large_button_02.sub",
			"down_image" : "d:/ymir work/ui/public/large_button_03.sub",
			"text" : localeinfo.PARTY_WAR_JOIN,
		},
	),
}
