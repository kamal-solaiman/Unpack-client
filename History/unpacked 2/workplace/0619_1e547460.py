# coding: latin_1

import uiscriptlocale

BUTTON_ROOT = "d:/ymir work/ui/game/guild/guildbuttons/memberpage/"
ROOT_DIR = "d:/ymir work/ui/game/guild/guildmemberpage/"
GUILD_PATH = uiscriptlocale.GUILD_PATH

window = {
	"name" : "GuildWindow_MemberPage",

 	"x" : 8,
	"y" : 30,

	"width" : 360,
	"height" : 298,

	"children" :
	(
		## GuildGradeTItle
		{
			"name" : "GuildGradeTItle", "type" : "image", "x" : 3, "y" : 1, "image" : GUILD_PATH+"title.sub",
		},		
		## IndexName
		{
			"name" : "IndexName", "type" : "image", "x" : 43, "y" : 4, "image" : ROOT_DIR+"IndexName.sub",
		},
		## IndexGrade
		{
			"name" : "IndexGrade", "type" : "image", "x" : 119, "y" : 4, "image" : ROOT_DIR+"IndexGrade.sub",
		},
		## IndexJob
		{
			"name" : "IndexJob", "type" : "image", "x" : 177, "y" : 4, "image" : ROOT_DIR+"IndexJob.sub",
		},
		## IndexLevel
		{
			"name" : "IndexLevel", "type" : "image", "x" : 217, "y" : 4, "image" : ROOT_DIR+"IndexLevel.sub",
		},
		## IndexOffer
		{
			"name" : "IndexOffer", "type" : "image", "x" : 251, "y" : 4, "image" : ROOT_DIR+"IndexOffer.sub",
		},
		## IndexGeneral
		{
			"name" : "IndexGeneral", "type" : "image", "x" : 304, "y" : 4, "image" : ROOT_DIR+"IndexGeneral.sub",
		},
		## ScrollBar
		{
			"name" : "ScrollBar",
			"type" : "scrollbar",

			"x" : 341,
			"y" : 20,
			"scrollbar_type" : "normal",
			"size" : 270,
		},		

	),
}
