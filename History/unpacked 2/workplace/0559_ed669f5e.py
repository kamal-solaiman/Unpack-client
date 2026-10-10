import uiScriptLocale
import localeInfo

TILE_IMG_PATH = "d:/ymir work/ui/event_rework/"

BG_WIDTH			= 430
BG_HEIGHT			= 155
TITLE_HEIGHT		= 27

IN_GAME_UI_WIDTH	= BG_WIDTH + 10
IN_GAME_UI_HEIGHT	= BG_HEIGHT + TITLE_HEIGHT + 10

DAY_BG_WIDTH		= 336
DAY_BG_HEIGHT		= 38
DAY_BG_X			= (BG_WIDTH - DAY_BG_WIDTH) / 2
DAY_BG_Y			= 14

window = {
	"name" : "InGameEventWindow",
	"type" : "window",
	"style" : ("movable", "float",),

	"x" : SCREEN_WIDTH - 160 - IN_GAME_UI_WIDTH,
	"y" : 15,

	"width" : IN_GAME_UI_WIDTH,
	"height" : IN_GAME_UI_HEIGHT,

	"children" :
	[
		#Background panel - begins under the titlebar, sized to the image
		{
			"name" : "board",
			"type" : "board",
			"style" : ("attach",),

			"x" : 0,
			"y" : 0,

			"width" : IN_GAME_UI_WIDTH + 10,
			"height" : IN_GAME_UI_HEIGHT,

			"children" :
			[
				{
					"name" : "Event_Title_Bar", "type" : "titlebar", "x" : 0, "y" : 5, "width" : IN_GAME_UI_WIDTH + 10 - 5, "height" : 21, "style" : ("attach",),
					"children" :
					(
						{"name":"TitleName", "type":"text", "x":0, "y":0, "text":uiScriptLocale.EVENT_ALARM_TITLE, "all_align" : "center"},
					),
				},
	
				{
					"name" : "main_bg",
					"type" : "expanded_image",
					"style" : ("attach",),

					"x" : 10,
					"y" : 28,

					"width" : BG_WIDTH,
					"height" : BG_HEIGHT,

					"image" : TILE_IMG_PATH + "new_event_bg.png",
				},

				#Day row background (sits behind the day-number boxes)
				# {
					# "name" : "day_bg",
					# "type" : "expanded_image",
					# "style" : ("attach",),

					# "x" : DAY_BG_X,
					# "y" : DAY_BG_Y,

					# "width" : DAY_BG_WIDTH,
					# "height" : DAY_BG_HEIGHT,

					# "image" : TILE_IMG_PATH + "new_event_day_bg.png",
				# },

				#Tile container for programmatic tile placement
				{
					"name" : "tile_container",
					"type" : "window",
					"style" : ("attach",),

					"x" : 9,
					"y" : 38,

					"width" : BG_WIDTH,
					"height" : BG_HEIGHT - 12,
				},

				#Navigation
				{
					"name" : "prev_button",
					"type" : "button",

					"x" : 22,
					"y" : 103,

					"tooltip_text" : localeInfo.UI_PREVPAGE,

					"default_image" : TILE_IMG_PATH + "left.png",
					"over_image" : TILE_IMG_PATH + "left.png",
					"down_image" : TILE_IMG_PATH + "left.png",
				},
				{
					"name" : "next_button",
					"type" : "button",

					"x" : 406,
					"y" : 103,

					"tooltip_text" : localeInfo.UI_NEXTPAGE,

					"default_image" : TILE_IMG_PATH + "right.png",
					"over_image" : TILE_IMG_PATH + "right.png",
					"down_image" : TILE_IMG_PATH + "right.png",
				},
			],
		},
	],
}
