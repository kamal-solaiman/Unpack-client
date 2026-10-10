# coding: latin_1

import app

AUTOBAN_QUIZ_ANSWER = "ANSWER"
AUTOBAN_QUIZ_REFRESH = "REFRESH"
AUTOBAN_QUIZ_REST_TIME = "REST_TIME"

OPTION_SHADOW = "SHADOW"

CODEPAGE = str(app.GetDefaultCodePage())

#CUBE_TITLE = "Cube Window"

def LoadLocaleFile(srcFileName, localeDict):
	localeDict["CUBE_INFO_TITLE"] = "Recipe"
	localeDict["CUBE_REQUIRE_MATERIAL"] = "Requirements"
	localeDict["CUBE_REQUIRE_MATERIAL_OR"] = "or"

	try:
		lines = open(srcFileName, "r").readlines()
	except IOError:
		import dbg
		dbg.LogBox("LoaduiscriptlocaleError(%(srcFileName)s)" % locals())
		app.Abort()

	for line in lines:
		tokens = line[:-1].split("\t")

		if len(tokens) >= 2:
			localeDict[tokens[0]] = tokens[1]
		else:
			print len(tokens), lines.index(line), line

if "locale/ymir" == app.GetLocalePath():
	LOCALE_UISCRIPT_PATH = "locale/ymir_ui/"

	WINDOWS_PATH = "d:/ymir work/ui/game/949_windows/"
	SELECT_PATH = "d:/ymir work/ui/intro/949_select/"
	GUILD_PATH = "d:/ymir work/ui/game/949_guild/"
	EMPIRE_PATH = "d:/ymir work/ui/intro/949_empire/"
	MAPNAME_PATH = "locale/ymir_ui/mapname/"
	LOGIN_PATH = "d:/ymir work/ui/intro/949_login/"

	JOBDESC_WARRIOR_PATH = "locale/ymir/desc_warrior.txt"
	JOBDESC_ASSASSIN_PATH = "locale/ymir/desc_assassin.txt"
	JOBDESC_SURA_PATH = "locale/ymir/desc_sura.txt"
	JOBDESC_SHAMAN_PATH = "locale/ymir/desc_shaman.txt"
	JOBDESC_WOLFMAN_PATH = "locale/ymir/desc_wolfman.txt"

	EMPIREDESC_A = "locale/ymir/desc_empire_a.txt"
	EMPIREDESC_B = "locale/ymir/desc_empire_b.txt"
	EMPIREDESC_C = "locale/ymir/desc_empire_c.txt"

	LOCALE_INTERFACE_FILE_NAME = "locale/ymir/locale_interface.txt"
	NEW_LOCALE_INTERFACE_FILE_NAME = "%s/new_locale_interface.txt" % (name)
else:
	if "HONGKONG" == app.GetLocaleServiceName():
		name = "locale/hongkong"
	elif "JAPAN" == app.GetLocaleServiceName():
		name = "locale/japan"
	elif "TAIWAN" == app.GetLocaleServiceName():
		name = "locale/taiwan"
	elif "NEWCIBN" == app.GetLocaleServiceName():
		name = "locale/newcibn"
	elif "EUROPE" == app.GetLocaleServiceName():
		name = app.GetLocalePath()
	else:
		name = "locale/ymir"

	LOCALE_UISCRIPT_PATH = "locale/common/ui/"
	LOGIN_PATH = "locale/common/ui/login/"
	EMPIRE_PATH = "%s/ui/empire/" % (name)
	GUILD_PATH = "locale/common/ui/guild/"
	SELECT_PATH = "%s/ui/select/" % (name)
	WINDOWS_PATH = "%s/ui/windows/" % (name)
	MAPNAME_PATH = "%s/ui/mapname/" % (name)

	JOBDESC_WARRIOR_PATH = "%s/jobdesc_warrior.txt" % (name)
	JOBDESC_ASSASSIN_PATH = "%s/jobdesc_assassin.txt" % (name)
	JOBDESC_SURA_PATH = "%s/jobdesc_sura.txt" % (name)
	JOBDESC_SHAMAN_PATH = "%s/jobdesc_shaman.txt" % (name)
	JOBDESC_WOLFMAN_PATH = "%s/jobdesc_wolfman.txt" % (name)

	EMPIREDESC_A = "%s/empiredesc_a.txt" % (name)
	EMPIREDESC_B = "%s/empiredesc_b.txt" % (name)
	EMPIREDESC_C = "%s/empiredesc_c.txt" % (name)

	BNW_EVENT_DESC = "%s/black_and_white_desc.txt" % (name)
	LOCALE_INTERFACE_FILE_NAME = "%s/locale_interface.txt" % (name)
	NEW_LOCALE_INTERFACE_FILE_NAME = "%s/new_locale_interface.txt" % (name)

	if app.ENABLE_LOADING_TIP:
		LOADING_TIP_LIST = "locale/common/loading_tip_list.txt"
		LOADING_TIP_VNUM = "%s/loading_tip_vnum.txt" % (name)

	if app.ENABLE_MINI_GAME_OKEY:
		MINIGAME_RUMI_DESC = "%s/mini_game_okey_desc.txt" % (name)
		MINIGAME_RUMI_SIMPLE_DESC = "%s/mini_game_okey_simple_desc.txt" % (name)

	if app.ENABLE_MINI_GAME_CATCH_KING:
		MINIGAME_CATCH_KING_DESC = "%s/catchking_event_desc.txt" % (name)
		MINIGAME_CATCH_KING_SIMPLE_DESC = "%s/catchking_event_simple_desc.txt" % (name)

	if app.ENABLE_GROWTH_PET_SYSTEM:
		PET_PRIMIUM_FEEDSTUFF_DESC = "%s/pet_primium_feedstuff_desc.txt" % (name)

if app.USE_BL_FISH_EVENT:
	FISH_EVENT_DESC = "%s/fish_event_desc.txt" % (name)

LoadLocaleFile(LOCALE_INTERFACE_FILE_NAME, locals())
LoadLocaleFile(NEW_LOCALE_INTERFACE_FILE_NAME, locals())
