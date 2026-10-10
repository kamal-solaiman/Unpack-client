import localeinfo
BOARD_WIDTH = 498
BOARD_HEIGHT = 406

window = {
	"name" : "PlayerRankWindow",

	"x" : 0,
	"y" : 0,

	"style" : ("movable", "float",),

	"width" : BOARD_WIDTH,
	"height" : BOARD_HEIGHT,

	"children" :
	(
		{
			"name" : "board",
			"type" : "board",
			"style" : ("attach",),

			"x" : 0,
			"y" : 0,

			"width" : BOARD_WIDTH,
			"height" : BOARD_HEIGHT,
		
			"children" :
			(
				## Title
				{
					"name" : "TitleBar",
					"type" : "titlebar",
					"style" : ("attach",),

					"x" : 6,
					"y" : 6,

					"width" : BOARD_WIDTH - 13,
					"color" : "yellow",

					"children" :
					(
						{ "name":"TitleName", "type":"text", "x":BOARD_WIDTH/2, "y":2, "text":localeinfo.PARTY_WAR_TEXT1, "outline" : 1, "text_horizontal_align":"center" },
					),
				},
				
				
				{
					"name" : "MainBackground",
					"type" : "thinboard",
					"x" : 0, "y" : 41, "width" : 470, "height" : BOARD_HEIGHT - 60,
					"horizontal_align" : "center",
				},

				{
					"name" : "RankingBackground",
					"type" : "thinboard_circle",
					"x" : 103, "y" : 41 + 40, "width" : BOARD_WIDTH /2 + 10, "height" : BOARD_HEIGHT - 105,
					"horizontal_align" : "center",
					"children" :
					[
						
						{
							"name" : "TitleBackGround",
							"type" : "image",
							"x" : 0, "y" : - 13,
							"horizontal_align" : "center",
							"image" : "d:/ymir work/ui/pattern/canal_theme/canal_title_small.png",
							"children" :
							[
								{
									"name" : "TitleText", "type" : "text",
									"all_align" : "center", "x" : 0, "y" : -2 , 
									"text" : localeinfo.PARTY_WAR_RANKING,
									"outline" : 1,
								},
							],
						},
					],
				},

				{
					"name" : "TipsBackground",
					"type" : "thinboard_circle",
					"x" : -130, "y" : 41 + 40, "width" : BOARD_WIDTH /2 - 50, "height" : BOARD_HEIGHT - 105,
					"horizontal_align" : "center",
					"children" :
					[
						
						{
							"name" : "TitleBackGround",
							"type" : "image",
							"x" : 0, "y" : - 13,
							"horizontal_align" : "center",
							"image" : "d:/ymir work/ui/pattern/canal_theme/canal_title_small.png",
							"children" :
							[
								{
									"name" : "TitleText", "type" : "text",
									"all_align" : "center", "x" : 0, "y" : -2 , 
									"text" : localeinfo.PARTY_WAR_EVENT_TITLE,
									"outline" : 1,
								},
							],
						},
					],
				},
				
				{
					"name" : "RankTiTleImg",
					"type" : "image",
					"x" : 24,
					"y" : 44,
					"image" : "d:/ymir work/ui/pattern/canal_theme/ranked/ranking_list_menu.png",
					"children" :
					[
						{
							"name" : "LeftTimeText", "type" : "text", "x" : 30, "y" : 0 ,  "text" : "", "outline" : 1,
						},
						{
							"name" : "RankTiTleClock",
							"type" : "image",
							"x" : 10,
							"y" : 0,
							"image" : "d:/ymir work/ui/pattern/canal_theme/clock.png",
						},
					],
				},
				{
					"name" : "RankKillsImg",
					"type" : "image",
					"x" : 103+150,
					"y" : 41 + 40 + 1,
					"image" : "d:/ymir work/ui/pattern/canal_theme/ranked/6.png",
				},
			),
		},
	),
}

