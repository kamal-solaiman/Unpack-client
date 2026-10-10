import localeinfo
window = {
	"name" : "PartyMemberWindow",
	"x" : 20,
	"y" : 250,
	"style" : ("float",),#"animate",),
	"width" : 180,
	"height" : 54,
	"children" :
	(
		{
			"name" : "board",
			"type" : "image",
			"x" : 0,
			"y" : 0,
			"image" : "d:/ymir work/ui/game/partywar_timer.png",
			"children" :
			(

				{
					"name" : "TitleText1",
					"type" : "text",
					"x" : -15,
					"y" : 5,
					"horizontal_align" : "center",
					"text_horizontal_align" : "center",
					"text" : localeinfo.PARTY_WAR_TIME_REMAIN,
					"fontname" : "Tahoma Bold:15",
					"children" :
					(
						
						{ "name" : "LeftTime", "type" : "text", "x" : 0, "y" : 20, "horizontal_align" : "center", "text_horizontal_align" : "center", "text" : "None" ,"fontname" : "Tahoma Bold:15",},
					),
				},
			),
		},
	),
}
