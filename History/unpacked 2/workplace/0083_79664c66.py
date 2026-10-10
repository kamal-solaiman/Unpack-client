# coding: latin_1

import app
if app.ENABLE_GENDER_ALIGNMENT:
	import chr
	import net

import constinfo
import background

# if app.USE_BONUS_PAGE:
	# def capitalize_first_char(s: str) -> str:
		# if s and s[0].isalpha():
			# return s[0].upper() + s[1:]

		# return s

if app.USE_SHIP_DEFENSE or (app.ENABLE_INGAME_WIKI and app.USE_EXTENDED_WIKI_CRAFT):
	def NumToStr(n):
		if n <= 0:
			return "0"

		return "%s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))


if app.FAST_EQUIP_WORLDARD or app.USE_OFFLINESHOP:
	def NumberToRoman(n):
		NumeralMatrix = [\
			["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"],
			["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"],
			["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"],
			["", "M", "MM", "MMM"]
		]

		rn = ""
		d = []

		while (n!=0):
			d.append(n%10)
			n =int(n/10)

		for i in range(len(d), 0, -1):
			rn += NumeralMatrix[i-1][d[i-1]]

		return rn

if app.ENABLE_MINI_GAME_BNW:
	def DO_YOU_BUY_SPECIAL(buyItemName, buyItemCount, buyItemPrice):
		if buyItemCount > 1:
			return DO_YOU_BUY_SPECIAL2 % (buyItemName, buyItemCount, buyItemPrice)
		else:
			return DO_YOU_BUY_SPECIAL1 % (buyItemName, buyItemPrice)

if app.ENABLE_BIOLOG_SYSTEM:
	def SecondToHMS(time):
		try:
			time = int(time)
		except ValueError:
			return "0 " + SECOND
		
		if int(time) <= 0:
			return "0 " + SECOND
		
		second = int(time % 60)
		minute = int((time / 60) % 60)
		hour = int((time / 60) / 60)
		
		text = ""
		
		if hour > 0:
			text += str(hour) + HOUR
			if minute > 0:
				text += " "
		
		if minute > 0:
			text += str(minute) + MINUTE
			if second > 0:
				text += " "
		
		if second > 0:
			text += str(second) + " " + SECOND
		
		return text

def NumberToStringDotted(n) :
	if n <= 0 :
		return "0"
	return "%s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))

if app.ENABLE_EXTENDED_BATTLE_PASS:
	def NumberWithPoint(n) :
		if n <= 0 :
			return "0"
		
		return "%s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))

if app.ENABLE_SHOPEX_GAYA_CURRENCY:
	def NumberToGayaString(n):
		if n <= 0 :
			return "0 %s" % (GEM_SYSTEM_NAME)
		
		n = str(n)
		return "%s %s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]), GEM_SYSTEM_NAME)


if app.ENABLE_GENDER_ALIGNMENT:
	GENDER_FEMALE = 0
	GENDER_MALE = 1

MAP_TRENT02 = "MAP_TRENT02"
MAP_WL = "MAP_WL"
MAP_NUSLUCK = "MAP_NUSLUCK"
MAP_TREE2 = "MAP_TREE2"

BLEND_POTION_NO_TIME = "BLEND_POTION_NO_TIME"
BLEND_POTION_NO_INFO = "BLEND_POTION_NO_INFO"

APP_TITLE = "HISTORY | "

GUILD_HEADQUARTER = "Main Building"
GUILD_FACILITY = "Facility"
GUILD_OBJECT = "Object"
GUILD_MEMBER_COUNT_INFINITY = "INFINITY"

LOGIN_FAILURE_WEB_BLOCK = "BLOCK_LOGIN(WEB)"
LOGIN_FAILURE_BLOCK_LOGIN = "BLOCK_LOGIN"
LOGIN_FAILURE_DEVICE_LIMIT = "This account already has 2 registered devices. Remove one on the website (a device can be deleted 24h after it was added) to log in from this PC."
CHANNEL_NOTIFY_FULL = "CHANNEL_NOTIFY_FULL"

# Wiki "Obtained from" row prefix for NPC shop sellers.
# Python-side default so the constant exists in every locale; the locale
# .txt files can override the translation.

GUILD_BUILDING_LIST_TXT = app.GetLocalePath() + "/GuildBuildingList.txt"

GUILD_MARK_MIN_LEVEL = "1"
GUILD_MARK_NOT_ENOUGH_LEVEL = "Minimum level of 1 required"

ERROR_MARK_UPLOAD_NEED_RECONNECT = "UploadMark: Reconnect to game"
ERROR_MARK_CHECK_NEED_RECONNECT = "CheckMark: Reconnect to game"

VIRTUAL_KEY_ALPHABET_LOWERS = r"[1234567890]/qwertyuiop\=asdfghjkl;`'zxcvbnm.,"
VIRTUAL_KEY_ALPHABET_UPPERS = r'{1234567890}?QWERTYUIOP|+ASDFGHJKL:~"ZXCVBNM<>'
VIRTUAL_KEY_SYMBOLS = '!@#$%^&*()_+|{}:"<>?~'
VIRTUAL_KEY_NUMBERS = "1234567890-=\[];',./`"
VIRTUAL_KEY_SYMBOLS_BR = '!@#$%^&*()_+|{}:"<>?~'

__IS_ENGLISH = "ENGLISH" == app.GetLocaleServiceName()
__IS_HONGKONG = "HONGKONG" == app.GetLocaleServiceName()
__IS_NEWCIBN = "locale/newcibn" == app.GetLocalePath()
__IS_EUROPE = "EUROPE" == app.GetLocaleServiceName()
__IS_CANADA = "locale/ca" == app.GetLocalePath()
__IS_BRAZIL = "locale/br" == app.GetLocalePath()
__IS_SINGAPORE = "locale/sg" == app.GetLocalePath()
__IS_VIETNAM = "locale/vn" == app.GetLocalePath()
__IS_ARABIC = "locale/ae" == app.GetLocalePath()
__IS_CIBN10 = "locale/cibn10" == app.GetLocalePath()
__IS_WE_KOREA = "locale/we_korea" == app.GetLocalePath()
__IS_TAIWAN = "locale/taiwan" == app.GetLocalePath()
__IS_JAPAN = "locale/japan" == app.GetLocalePath()
LOGIN_FAILURE_WRONG_SOCIALID = "ASDF"
LOGIN_FAILURE_SHUTDOWN_TIME = "ASDF"

if __IS_CANADA:
	__IS_EUROPE = True

def IsYMIR():
	return "locale/ymir" == app.GetLocalePath()

def IsJAPAN():
	return "locale/japan" == app.GetLocalePath()

def IsENGLISH():
	global __IS_ENGLISH
	return __IS_ENGLISH

def IsHONGKONG():
	global __IS_HONGKONG
	return __IS_HONGKONG

def IsTAIWAN():
	return "locale/taiwan" == app.GetLocalePath()

def IsNEWCIBN():
	return "locale/newcibn" == app.GetLocalePath()

def IsCIBN10():
	global __IS_CIBN10
	return __IS_CIBN10

def IsEUROPE():
	global __IS_EUROPE
	return __IS_EUROPE

def IsCANADA():
	global __IS_CANADA
	return __IS_CANADA

def IsBRAZIL():
	global __IS_BRAZIL
	return __IS_BRAZIL

def IsVIETNAM():
	global __IS_VIETNAM
	return __IS_VIETNAM

def IsSINGAPORE():
	global __IS_SINGAPORE
	return __IS_SINGAPORE

def IsARABIC():
	global __IS_ARABIC
	return __IS_ARABIC

def IsWE_KOREA():
	return "locale/we_korea" == app.GetLocalePath()

# SUPPORT_NEW_KOREA_SERVER
def LoadLocaleData():
	app.LoadLocaleData(app.GetLocalePath())

def IsCHEONMA():
	return IsYMIR()
# END_OF_SUPPORT_NEW_KOREA_SERVER

def mapping(**kwargs): return kwargs

def SNA(text):
	def f(x):
		return text
	return f

def SA(text):
	def f(x):
		return text % x
	return f

def FormatTime(time):
	m, s = divmod(time, 60)
	h, m = divmod(m, 60)
	# return "%02d:%02d:%02d" % (h, m, s)

	# app.USE_NORTHWIND_DEEPS_DUNGEON
	if h > 0:
		return "%02d:%02d:%02d" % (h, m, s)
	else:
		return "%02d:%02d" % (m, s)

def SAA(text):
	def f(x1, x2):
		return text % (x1, x2)
	return f

def SAAAA(text):
	def f(x1, x2, x3, x4):
		return text % (x1, x2, x3, x4)
	return f

def SAN(text):
	def f(x1, x2):
		return text % x1
	return f

def LoadLocaleFile(srcFileName, localeDict):
	funcDict = {"SA":SA, "SNA":SNA, "SAA":SAA, "SAN":SAN, "SAAAA":SAAAA,}

	lineIndex = 1

	lines = []
	try:
		lines = open(srcFileName, "r").readlines()
	except IOError:
		import dbg
		dbg.LogBox("LoadLocaleError(%(srcFileName)s)" % locals())
		app.Abort()

	for line in lines:
		try:
			tokens = line[:-1].split("\t")
			if len(tokens) == 2:
				localeDict[tokens[0]] = tokens[1]
			elif len(tokens) >= 3:
				type = tokens[2].strip()
				if type:
					localeDict[tokens[0]] = funcDict[type](tokens[1])
				else:
					localeDict[tokens[0]] = tokens[1]
			else:
				raise RuntimeError, "Unknown TokenSize"

			lineIndex += 1
		except:
			import dbg
			dbg.LogBox("%s: line(%d): %s" % (srcFileName, lineIndex, line), "Error")
			raise

all = ["locale", "error"]

if IsEUROPE() and IsBRAZIL():
	FN_GM_MARK = "locale/common/effect/gm.mse"
	LOCALE_FILE_NAME = "%s/locale_game.txt" % app.GetLocalePath()
	NEW_LOCALE_FILE_NAME = "%s/new_locale_game.txt" % app.GetLocalePath()

	constinfo.IN_GAME_SHOP_ENABLE = 0
elif IsSINGAPORE():
	FN_GM_MARK = "locale/common/effect/gm.mse"
	LOCALE_FILE_NAME = "%s/locale_game.txt" % app.GetLocalePath()
	NEW_LOCALE_FILE_NAME = "%s/new_locale_game.txt" % app.GetLocalePath()

	constinfo.IN_GAME_SHOP_ENABLE = 0
elif IsNEWCIBN():
	APP_TITLE = "HISTORY | "
	FN_GM_MARK = "locale/common/effect/gm.mse"
	LOCALE_FILE_NAME = "%s/locale_game.txt" % app.GetLocalePath()
	NEW_LOCALE_FILE_NAME = "%s/new_locale_game.txt" % app.GetLocalePath()

	constinfo.IN_GAME_SHOP_ENABLE = 1
elif IsTAIWAN():
	APP_TITLE = "HISTORY | "
	FN_GM_MARK = "locale/common/effect/gm.mse"
	LOCALE_FILE_NAME = "%s/locale_game.txt" % app.GetLocalePath()
	NEW_LOCALE_FILE_NAME = "%s/new_locale_game.txt" % app.GetLocalePath()

	constinfo.IN_GAME_SHOP_ENABLE = 1
else:
	FN_GM_MARK = "locale/common/effect/gm.mse"
	LOCALE_FILE_NAME = "%s/locale_game.txt" % app.GetLocalePath()
	NEW_LOCALE_FILE_NAME = "%s/new_locale_game.txt" % app.GetLocalePath()

	constinfo.IN_GAME_SHOP_ENABLE = 1

LoadLocaleFile(LOCALE_FILE_NAME, locals())
LoadLocaleFile(NEW_LOCALE_FILE_NAME, locals())

locale = mapping(
)

def GetAuxiliaryWordType(text):
	textLength = len(text)

	if textLength > 1:
		singleWord = text[-1]

		if (singleWord >= '0' and singleWord <= '9') or\
			(singleWord >= 'a' and singleWord <= 'z') or\
			(singleWord >= 'A' and singleWord <= 'Z'):
			if not dictSingleWord.has_key(singleWord):
				return 1

		elif dictDoubleWord.has_key(text[-2:]):
			return 1

	return 0

def CutMoneyString(sourceText, startIndex, endIndex, insertingText, backText):
	sourceLength = len(sourceText)

	if sourceLength < startIndex:
		return backText

	text = sourceText[max(0, sourceLength-endIndex):sourceLength-startIndex]

	if not text:
		return backText

	if int(text) <= 0:
		return backText

	text = str(int(text))

	if backText:
		backText = " " + backText

	return text + insertingText + backText

if app.ENABLE_GEM_SYSTEM:
	def SecondToHMGolbal(time):
		if time < 60:
			return "00:01"

		minute = int((time / 60) % 60)
		hour = int((time / 60) / 60)

		text = ""

		if hour > 0:
			if hour >= 10:
				text += str(hour) + ":"
			else:
				text += "0" + str(hour) + ":"
		else:
			text += "00:"

		if minute > 0:
			if minute >= 10:
				text += str(minute)
			else:
				text += "0" + str(minute)

		return text

def SecondToDHMS(time):
	if time < 60:
		if IsARABIC():
			return "%.2f %s" % (time, SECOND)
		else:
			return "%.2f %s" % (time, SECOND)

	second = int(time % 60)
	minute = int((time / 60) % 60)
	hour = int((time / 60) / 60) % 24
	day = int(int((time / 60) / 60) / 24)

	text = ""

	if day > 0:
		text += str(day) + DAY
		text += " "

	if hour > 0:
		text += str(hour) + HOUR
		text += " "

	if minute > 0:
		text += str(minute) + MINUTE
		text += " "

	if second > 0:
		text += str(second) + SECOND
		text += " "

	return text

def newSecondToDHM(time):
	if time < 60:
		return str(time) + SECOND

	second = int(time % 60)
	minute = int((time / 60) % 60)
	hour = int((time / 60) / 60) % 24
	day = int(int((time / 60) / 60) / 24)

	text = ""

	if day > 0:
		text += str(day) + DAY
		text += " "

	if hour > 0:
		text += str(hour) + HOUR
		text += " "

	if minute > 0:
		text += str(minute) + MINUTE

	return text

def SecondToDHM(time):
	if time < 60:
		if IsARABIC():
			return "%.2f %s" % (time, SECOND)
		else:
			return "0" + MINUTE

	second = int(time % 60)
	minute = int((time / 60) % 60)
	hour = int((time / 60) / 60) % 24
	day = int(int((time / 60) / 60) / 24)

	text = ""

	if day > 0:
		text += str(day) + DAY
		text += " "

	if hour > 0:
		text += str(hour) + HOUR
		text += " "

	if minute > 0:
		text += str(minute) + MINUTE

	return text
	
	
def SecondToDHMNew(time):
	if time < 60:
		if IsARABIC():
			return "%.2f %s" % (time, SECOND)
		else:
			return "0" + MINUTE

	second = int(time % 60)
	minute = int((time / 60) % 60)
	hour = int((time / 60) / 60) % 24
	day = int(int((time / 60) / 60) / 24)

	text = ""

	if day > 0:
		text += str(day) + DAY
		text += " "

	if hour > 0:
		text += str(hour) + HOUR
		text += " "

	if minute > 0:
		text += str(minute) + MINUTE
		text += " "

	if second > 0 and day <= 0:
		text += str(second) + SECOND
		text += " "

	return text

def SecondToHM(time):
	if time < 60:
		if IsARABIC():
			return "%.2f %s" % (time, SECOND)
		else:
			return "0" + MINUTE

	second = int(time % 60)
	minute = int((time / 60) % 60)
	hour = int((time / 60) / 60)

	text = ""

	if hour > 0:
		text += str(hour) + HOUR
		if hour > 0:
			text += " "

	if minute > 0:
		text += str(minute) + MINUTE

	return text

def SecondToDay(time):
	if time < 60:
		return "1" + DAY

	second = int(time % 60)
	minute = int((time / 60) % 60)
	hour = int((time / 60) / 60) % 24
	day = int(int((time / 60) / 60) / 24)

	if day < 1:
		day = 1

	if day > 9999:
		day = 9999

	text = str(day) + DAY
	return text

def SecondToDayNumber(time):
	if time < 60:
		return 1

	second = int(time % 60)
	minute = int((time / 60) % 60)
	hour = int((time / 60) / 60) % 24
	day = int(int((time / 60) / 60) / 24)

	if day < 1:
		day = 1

	if day > 9999:
		day = 9999

	return day

def SecondToH(time):
	hour = int((time / 60) / 60)

	text = ""
	hour = max(0, hour)
	text += str(hour)

	return text

if app.ENABLE_12ZI:
	def SecondToColonTypeHMS(time):
		if time < 60:
			return "00:00:%02d" % (time)

		second = int(time % 60)
		minute = int((time / 60) % 60)
		hour = int((time / 60) / 60)

		return "%02d:%02d:%02d" % (hour, minute, second)

	def SecondToColonTypeMS(time):
		second = int(time % 60)
		minute = int((time / 60) % 60)

		return "%02d:%02d" % (minute, second)

if app.ENABLE_GENDER_ALIGNMENT:
	def GetAlignmentTitleName(currentAlignment):
		titleNameTuple = TITLE_NAME_DICT.get(chr.RaceToSex(net.GetMainActorRace()), ('UNKNOWN_GENDER',))

		for alignmentIndex, alignmentValue in enumerate((12000, 8000, 4000, 1000, 0, -4000, -8000, -12000)):
			if currentAlignment >= alignmentValue:
				return titleNameTuple[alignmentIndex]

		return titleNameTuple[-1]
else:
	def GetAlignmentTitleName(alignment):
		if alignment >= 12000:
			return TITLE_NAME_LIST[0]
		elif alignment >= 8000:
			return TITLE_NAME_LIST[1]
		elif alignment >= 4000:
			return TITLE_NAME_LIST[2]
		elif alignment >= 1000:
			return TITLE_NAME_LIST[3]
		elif alignment >= 0:
			return TITLE_NAME_LIST[4]
		elif alignment > -4000:
			return TITLE_NAME_LIST[5]
		elif alignment > -8000:
			return TITLE_NAME_LIST[6]
		elif alignment > -12000:
			return TITLE_NAME_LIST[7]

		return TITLE_NAME_LIST[8]

RESOLUTION = "Resolution"

OPTION_PVPMODE_MESSAGE_DICT = {
	0 : PVP_MODE_NORMAL,
	1 : PVP_MODE_REVENGE,
	2 : PVP_MODE_KILL,
	3 : PVP_MODE_PROTECT,
	4 : PVP_MODE_GUILD,
}

error = mapping(
	CREATE_WINDOW = GAME_INIT_ERROR_MAIN_WINDOW,
	CREATE_CURSOR = GAME_INIT_ERROR_CURSOR,
	CREATE_NETWORK = GAME_INIT_ERROR_NETWORK,
	CREATE_ITEM_PROTO = GAME_INIT_ERROR_ITEM_PROTO,
	CREATE_MOB_PROTO = GAME_INIT_ERROR_MOB_PROTO,
	CREATE_NO_DIRECTX = GAME_INIT_ERROR_DIRECTX,
	CREATE_DEVICE = GAME_INIT_ERROR_GRAPHICS_NOT_EXIST,
	CREATE_NO_APPROPRIATE_DEVICE = GAME_INIT_ERROR_GRAPHICS_BAD_PERFORMANCE,
	CREATE_FORMAT = GAME_INIT_ERROR_GRAPHICS_NOT_SUPPORT_32BIT,
	NO_ERROR = ""
)

GUILDWAR_NORMAL_DESCLIST = [GUILD_WAR_USE_NORMAL_MAP, GUILD_WAR_LIMIT_30MIN, GUILD_WAR_WIN_CHECK_SCORE]
GUILDWAR_WARP_DESCLIST = [GUILD_WAR_USE_BATTLE_MAP, GUILD_WAR_WIN_WIPE_OUT_GUILD, GUILD_WAR_REWARD_POTION]
GUILDWAR_CTF_DESCLIST = [GUILD_WAR_USE_BATTLE_MAP, GUILD_WAR_WIN_TAKE_AWAY_FLAG1, GUILD_WAR_WIN_TAKE_AWAY_FLAG2, GUILD_WAR_REWARD_POTION]

MINIMAP_ZONE_NAME_DICT = {
	"metin2_map_1" :					MAP_ALL_NEW,
	"metin2_map_a1" :					MAP_A1,
	"map_a2" :							MAP_A2,
	"metin2_map_a3" :					MAP_A3,
	"metin2_map_b1" :					MAP_B1,
	"map_b2" :							MAP_B2,
	"metin2_map_b3" :					MAP_B3,
	"metin2_map_c1" :					MAP_C1,
	"map_c2" :							MAP_C2,
	"metin2_map_c3" :					MAP_C3,
	"map_n_snowm_01" :					MAP_SNOW,
	"metin2_map_n_desert_01" :			MAP_DESERT,
	"metin2_map_milgyo" :				MAP_TEMPLE,
	"metin2_map_spiderdungeon" :		MAP_SPIDERDUNGEON,
	"metin2_map_deviltower1" :			MAP_DEVILTOWER1,
	"metin2_map_deviltower2" :			MAP_DEVILTOWER1,
	"metin2_map_guild_01" :				MAP_AG,
	"metin2_map_guild_02" :				MAP_BG,
	"metin2_map_guild_03" :				MAP_CG,
	"metin2_map_trent" :				MAP_TREE,
	"metin2_map_trent02" :				MAP_TREE2,
	"metin2_map_WL_01" :		MAP_WL,
	"metin2_map_nusluck01" :	MAP_NUSLUCK,
	"Metin2_map_CapeDragonHead" :		MAP_CAPE,
	"metin2_map_Mt_Thunder" :			MAP_THUNDER,
	"metin2_map_dawnmistwood" :			MAP_DAWN,
	"metin2_map_BayBlackSand" :			MAP_BAY,
	"different_3in1_kingdoms" :			MAP_ALL_KINGDOMS,
	"metin2_map_spiderdungeon_02"  : MAP_SPIDERDUNGEON_02,
	"metin2_map_spiderdungeon_03"  : MAP_SPIDERDUNGEON_03,
	"metin2_map_skipia_dungeon_01"  : MAP_SKIPIA_DUNGEON_01,
	"metin2_map_skipia_dungeon_02"  : MAP_SKIPIA_DUNGEON_02,
	"map_n_threeway"  : MAP_N_THREEWAY,
	"metin2_map_n_flame_01"  : MAP_N_FLAME_01,
	"season1/metin2_map_nusluck01" : MAP_NUSLUCK,
	"Metin2_map_CapeDragonHead" : MAP_CAPE,
	"season1/metin2_map_WL_01" : MAP_WL,
	"map_tree2" : MAP_TREE2,
}

JOBINFO_TITLE = [
	[JOB_WARRIOR0, JOB_WARRIOR1, JOB_WARRIOR2,],
	[JOB_ASSASSIN0, JOB_ASSASSIN1, JOB_ASSASSIN2,],
	[JOB_SURA0, JOB_SURA1, JOB_SURA2,],
	[JOB_SHAMAN0, JOB_SHAMAN1, JOB_SHAMAN2,],
	[JOB_WOLFMAN0, JOB_WOLFMAN1, JOB_WOLFMAN1,],
]

if app.WJ_SHOW_PARTY_ON_MINIMAP or app.USE_DUNGEON_INFO or app.ENABLE_INGAME_WIKI:
	MINIMAP_ZONE_NAME_DICT_BY_IDX = {
		0 : "",
		1 : MAP_A1,
		3 : MAP_A3,
		4 : MAP_GUILD_01,
		5 : MAP_MONKEY_DUNGEON_11,
		6 : GUILD_VILLAGE_01,
		10 : MAP_ALL_NEW,
		21 : MAP_B1,
		23 : MAP_B3,
		24 : MAP_GUILD_02,
		25 : MAP_MONKEY_DUNGEON_12,
		26 : GUILD_VILLAGE_02,
		41 : MAP_C1,
		43 : MAP_C3,
		44 : MAP_GUILD_03,
		45 : MAP_MONKEY_DUNGEON_13,
		46 : GUILD_VILLAGE_03,
		47 : MAP_ORC_DUNGEON,
		29 : MAP_ORC_DUNGEON,
		30 : MAP_MONKEY_DUNGEON,
		61 : MAP_N_SNOWM_01,
		62 : MAP_N_FLAME_01,
		63 : MAP_N_DESERT_01,
		64 : MAP_N_THREEWAY,
		65 : MAP_MILGYO,
		66 : MAP_DEVILTOWER1,
		67 : MAP_TRENT,
		68 : MAP_TRENT02,
		69 : MAP_WL_01,
		70 : MAP_NUSLUCK01,
		71 : MAP_SPIDERDUNGEON_02,
		72 : MAP_SKIPIA_DUNGEON_01,
		73 : MAP_SKIPIA_DUNGEON_02,
		74 : MAP_N_SNOWM_02,
		75 : MAP_N_FLAME_02,
		76 : MAP_N_DESERT_02,
		77 : MAP_A2_1,
		78 : MAP_MILGYO_A,
		79 : MAP_TRENT_A,
		80 : MAP_TRENT02_A,
		81 : MAP_WEDDING_01,
		91 : MAP_E,
		92 : MAP_E,
		93 : MAP_E,
		96 : MAP_CHARDUN,
		101 : MAP_ALL_KINGDOMS,
		102 : MAP_DUNGEONS,
		103 : MAP_T1,
		104 : MAP_SPIDERDUNGEON,
		105 : MAP_T2,
		107 : MAP_MONKEY_DUNGEON,
		108 : MAP_MONKEY_DUNGEON2,
		109 : MAP_MONKEY_DUNGEON3,
		110 : MAP_T3,
		111 : MAP_T4,
		112 : MAP_DUEL,
		113 : MAP_OXEVENT,
		114 : MAP_SUNGZI,
		118 : MAP_SUNGZI_FLAME_HILL_01,
		119 : MAP_SUNGZI_FLAME_HILL_02,
		120 : MAP_SUNGZI_FLAME_HILL_03,
		121 : MAP_SUNGZI_SNOW,
		122 : MAP_SUNGZI_SNOW_PASS01,
		123 : MAP_SUNGZI_SNOW_PASS02,
		124 : MAP_SUNGZI_SNOW_PASS03,
		125 : MAP_SUNGZI_DESERT_01,
		126 : MAP_SUNGZI_DESERT_HILL_01,
		127 : MAP_SUNGZI_DESERT_HILL_02,
		128 : MAP_SUNGZI_DESERT_HILL_03,
		130 : GUILD_WAR1,
		131 : GUILD_WAR2,
		132 : GUILD_WAR3,
		133 : GUILD_WAR4,
		144 : SHADOW_DUNGEON,
		145 : SHADOW_DUNGEON_ENTERANCE,
		163 : MAP_RAMADAN,
		165 : MAP_WOKUNG,
		166 : MAP_GHOSTS_DUNGEON,
		167 : MAP_GHOSTS,
		180 : METIN_HALLOWEEN,
		181 : MAP_EMPIREWAR01,
		182 : MAP_EMPIREWAR02,
		183 : MAP_EMPIREWAR03,
		184 : MAP_SKIPIA_DUNGEON_011,
		185 : MAP_SKIPIA_DUNGEON_021,
		186 : MAP_SKIPIA_DUNGEON_012,
		187 : MAP_SKIPIA_DUNGEON_022,
		188 : MAP_SKIPIA_DUNGEON_013,
		189 : MAP_SKIPIA_DUNGEON_023,
		192 : MAP_ZODIAC_FARM,
		193 : MAP_SPIDERDUNGEON_02_1,
		194 : MAP_HOLYPLACE_FLAME,
		195 : MAP_PATHWAY_FLAME_01,
		196 : MAP_PATHWAY_FLAME_02,
		197 : MAP_PATHWAY_FLAME_03,
		198 : MAP_HOLYPLACE_ICE,
		199 : MAP_PATHWAY_ICE_01,
		200 : MAP_PATHWAY_ICE_02,
		201 : MAP_PATHWAY_ICE_03,
		202 : MAP_HOLYPLACE_DESERT,
		203 : MAP_PATHWAY_DESERT_01,
		204 : MAP_PATHWAY_DESERT_02,
		205 : MAP_PATHWAY_DESERT_03,
		208 : MAP_SKIPIA_DUNGEON_BOSS,
		209 : MAP_SKIPIA_DUNGEON_BOSS_1,
		210 : MAP_SKIPIA_DUNGEON_BOSS_2,
		211 : MAP_SKIPIA_DUNGEON_BOSS_3,
		212 : MAP_N_FLAME_DRAGON,
		216 : MAP_DEVILCATACOMB,
		218 : MAP_SPIDERDUNGEON_03,
		231 : MAP_HALLWOEEN,
		301 : MAP_CAPEDRAGONHEAD,
		302 : MAP_DAWNMISTWOOD,
		303 : MAP_BAYBLACKSAND,
		304 : MAP_MT_THUNDER,
		342 : MAP_AKZ_HARD,
		351 : MAP_N_FLAME_DUNGEON_01,
		352 : MAP_N_SNOW_DUNGEON_01,
		353 : MAP_DAWNMIST_DUNGEON_01,
		354 : MAP_MT_TH_DUNGEON_01,
		355 : MAP_CZ_DUNGEON,
		357 : MAP_BATTLE_FIELD,
		358 : MAP_DEFENSE_WAVE,
		359 : MAP_DEFENSE_WAVE_PORT,
		360 : MAP_MISTS_OF_ISLAND,
		361 : MAP_MINIBOSS_01,
		362 : MAP_MINIBOSS_02,
		363 : MAP_BOSS_LABYRINTH,
		364 : MAP_BOSS_CRACK_SKIPIA,
		365 : MAP_BOSS_CRACK_FLAME,
		366 : MAP_BOSS_CRACK_SNOW,
		367 : MAP_BOSS_CRACK_DAWNMIST,
		368 : MAP_BOSS_AWAKEN_SKIPIA,
		369 : MAP_BOSS_AWAKEN_FLAME,
		370 : MAP_BOSS_AWAKEN_SNOW,
		371 : MAP_BOSS_AWAKEN_DAWNMIST,
		372 : MAP_GUILD_PVE,
		373 : MAP_EASTPLAIN_01,
		374 : MAP_EMPIRECASTLE,
		375 : MAP_BATTLE_ROYALE,
		376 : MAP_EASTPLAIN_02,
		377 : MAP_EASTPLAIN_03,
		378 : MAP_ELEMENTAL_DUNGEON,
		379 : MAP_ELEMENTAL_DUNGEON,
		380 : MAP_ELEMENTAL_DUNGEON,
		381 : MAP_ELEMENTAL_DUNGEON,
		382 : MAP_MAZE_DUNGEON_01,
		383 : MAP_MAZE_DUNGEON_02,
		384 : MAP_MAZE_DUNGEON_03,
		385 : MAP_SNAKE_VALLEY,
		386 : MAP_SUNGMAHEE_TOWER_WAIT,
		387 : MAP_SUNGMAHEE_TOWER_DUNGEON,
		388 : MAP_ICE_CRYSTALS_CAVE,
		389 : MAP_WHITE_DRAGON_VALLEY,
		390 : MAP_SNAKE_TEMPLE_1,
		391 : MAP_SNAKE_TEMPLE_2,
		392 : MAP_PRIVATE_SHOP_MAP,
		393 : MAP_WHITE_DRAGON_CAVE_01,
		394 : MAP_WHITE_DRAGON_CAVE_02,
#		395 : MAP_WHITE_DRAGON_CAVE_BOSS,
		396 : MAP_FARMING_DUNGEON,
		399 : MAP_SECRET_DUNGEON,
		400 : MAP_OTHER_WORLD_01,
		401 : MAP_OTHER_WORLD_02,
		402 : MAP_OTHER_WORLD_03,
		403 : MAP_OTHER_WORLD_04,
	}

	if app.USE_NORTHWIND_DEEPS_DUNGEON:
		MINIMAP_ZONE_NAME_DICT_BY_IDX[397] = MAP_WHITE_DRAGON_CAVE_BOSS_01
		MINIMAP_ZONE_NAME_DICT_BY_IDX[398] = MAP_WHITE_DRAGON_CAVE_BOSS_02

	def GetMiniMapZoneNameByIdx(idx):
		if idx in MINIMAP_ZONE_NAME_DICT_BY_IDX:
			return MINIMAP_ZONE_NAME_DICT_BY_IDX[idx]

		return MAP_NONE

WHISPER_ERROR = {
	1 : CANNOT_WHISPER_NOT_LOGON,
	2 : CANNOT_WHISPER_DEST_REFUSE,
	3 : CANNOT_WHISPER_SELF_REFUSE,
}

NOTIFY_MESSAGE = {
	"CANNOT_EQUIP_SHOP" : CANNOT_EQUIP_IN_SHOP,
	"CANNOT_EQUIP_EXCHANGE" : CANNOT_EQUIP_IN_EXCHANGE,
}

ATTACK_ERROR_TAIL_DICT = {
	"IN_SAFE" : CANNOT_ATTACK_SELF_IN_SAFE,
	"DEST_IN_SAFE" : CANNOT_ATTACK_DEST_IN_SAFE,
}

SHOT_ERROR_TAIL_DICT = {
	"EMPTY_ARROW" : CANNOT_SHOOT_EMPTY_ARROW,
	"IN_SAFE" : CANNOT_SHOOT_SELF_IN_SAFE,
	"DEST_IN_SAFE" : CANNOT_SHOOT_DEST_IN_SAFE,
}

USE_SKILL_ERROR_TAIL_DICT = {
	"IN_SAFE" : CANNOT_SKILL_SELF_IN_SAFE,
	"NEED_TARGET" : CANNOT_SKILL_NEED_TARGET,
	"NEED_EMPTY_BOTTLE" : CANNOT_SKILL_NEED_EMPTY_BOTTLE,
	"NEED_POISON_BOTTLE" : CANNOT_SKILL_NEED_POISON_BOTTLE,
	"REMOVE_FISHING_ROD" : CANNOT_SKILL_REMOVE_FISHING_ROD,
	"NOT_YET_LEARN" : CANNOT_SKILL_NOT_YET_LEARN,
	"NOT_MATCHABLE_WEAPON" : CANNOT_SKILL_NOT_MATCHABLE_WEAPON,
	"WAIT_COOLTIME" : CANNOT_SKILL_WAIT_COOLTIME,
	"NOT_ENOUGH_HP" : CANNOT_SKILL_NOT_ENOUGH_HP,
	"NOT_ENOUGH_SP" : CANNOT_SKILL_NOT_ENOUGH_SP,
	"CANNOT_USE_SELF" : CANNOT_SKILL_USE_SELF,
	"ONLY_FOR_ALLIANCE" : CANNOT_SKILL_ONLY_FOR_ALLIANCE,
	"CANNOT_ATTACK_ENEMY_IN_SAFE_AREA" : CANNOT_SKILL_DEST_IN_SAFE,
	"CANNOT_APPROACH" : CANNOT_SKILL_APPROACH,
	"CANNOT_ATTACK" : CANNOT_SKILL_ATTACK,
	"ONLY_FOR_CORPSE" : CANNOT_SKILL_ONLY_FOR_CORPSE,
	"EQUIP_FISHING_ROD" : CANNOT_SKILL_EQUIP_FISHING_ROD, 
	"NOT_HORSE_SKILL" : CANNOT_SKILL_NOT_HORSE_SKILL,
	"HAVE_TO_RIDE" : CANNOT_SKILL_HAVE_TO_RIDE,
}

LEVEL_LIST = ["", HORSE_LEVEL1, HORSE_LEVEL2, HORSE_LEVEL3]

HEALTH_LIST = [
	HORSE_HEALTH0,
	HORSE_HEALTH1,
	HORSE_HEALTH2,
	HORSE_HEALTH3,
]

USE_SKILL_ERROR_CHAT_DICT = {
	"NEED_EMPTY_BOTTLE" : SKILL_NEED_EMPTY_BOTTLE,
	"NEED_POISON_BOTTLE" : SKILL_NEED_POISON_BOTTLE,
	"ONLY_FOR_GUILD_WAR" : SKILL_ONLY_FOR_GUILD_WAR,
}


SHOP_ERROR_DICT = {
	"NOT_ENOUGH_MONEY" : SHOP_NOT_ENOUGH_MONEY,
	"SOLDOUT" : SHOP_SOLDOUT,
	"INVENTORY_FULL" : SHOP_INVENTORY_FULL,
	"INVALID_POS" : SHOP_INVALID_POS,
	"NOT_ENOUGH_MONEY_EX" : SHOP_NOT_ENOUGH_MONEY_EX,

}

if app.ENABLE_SHOPEX_RENEWAL:
	SHOP_ERROR_DICT["NOT_ENOUGH_ITEM"]=SHOP_NOT_ENOUGH_ITEM
	SHOP_ERROR_DICT["NOT_ENOUGH_EXP"]=SHOP_NOT_ENOUGH_EXP
	SHOP_ERROR_DICT["LIMITED_PURCHASE_OVER"]=SHOP_LIMITED_PURCHASE_OVER
	if app.ENABLE_SHOPEX_DAILY_LIMIT:
		SHOP_ERROR_DICT["SHOPEX_DAILY_OVER"] = SHOPEX_DAILY_OVER

if app.ENABLE_WORLDBOSS:
	SHOP_ERROR_DICT["NOT_ENOUGH_WB_POINTS"]=NOT_ENOUGH_WB_POINTS_TEXT

	if app.ENABLE_SHOPEX_GAYA_CURRENCY:
		SHOP_ERROR_DICT["NOT_ENOUGH_GAYA"] = SHOP_NOT_ENOUGH_GAYA

STAT_MINUS_DESCRIPTION = {
	"HTH-" : STAT_MINUS_CON,
	"INT-" : STAT_MINUS_INT,
	"STR-" : STAT_MINUS_STR,
	"DEX-" : STAT_MINUS_DEX,
}

if app.AUTO_HUNT_RUBINUM:
	METIN_STONE_QUEUE_MSG_DICT = {
		"REMOVED" : METIN_STONE_QUEUE_MSG_REMOVED,
		"MAX_NORMAL" : METIN_STONE_QUEUE_MSG_MAX_NORMAL,
		"MAX" : METIN_STONE_QUEUE_MSG_MAX,
	}

MODE_NAME_LIST = (PVP_OPTION_NORMAL, PVP_OPTION_REVENGE, PVP_OPTION_KILL, PVP_OPTION_PROTECT,)
if app.ENABLE_GENDER_ALIGNMENT:
	TITLE_NAME_DICT = {
		GENDER_FEMALE : (PVP_LEVEL0_F, PVP_LEVEL1_F, PVP_LEVEL2_F, PVP_LEVEL3_F, PVP_LEVEL4_F, PVP_LEVEL5_F, PVP_LEVEL6_F, PVP_LEVEL7_F, PVP_LEVEL8_F,),
		GENDER_MALE : (PVP_LEVEL0_M, PVP_LEVEL1_M, PVP_LEVEL2_M, PVP_LEVEL3_M, PVP_LEVEL4_M, PVP_LEVEL5_M, PVP_LEVEL6_M, PVP_LEVEL7_M, PVP_LEVEL8_M,),
	}
else:
	TITLE_NAME_LIST = (PVP_LEVEL0, PVP_LEVEL1, PVP_LEVEL2, PVP_LEVEL3, PVP_LEVEL4, PVP_LEVEL5, PVP_LEVEL6, PVP_LEVEL7, PVP_LEVEL8,)

# Alignment grade boundary thresholds (displayed scale = raw/10)
# index i = upper bound of grade i; index i+1 = lower bound of grade i
ALIGNMENT_GRADE_THRESHOLDS = (20000, 12000, 8000, 4000, 1000, 0, -4000, -8000, -12000, -20000)

# Alignment grade bonus strings (index = grade 0–8), loaded from locale file
ALIGNMENT_GRADE_BONUSES = (
	ALIGNMENT_BONUS_0, ALIGNMENT_BONUS_1, ALIGNMENT_BONUS_2, ALIGNMENT_BONUS_3,
	ALIGNMENT_BONUS_4,
	ALIGNMENT_BONUS_5, ALIGNMENT_BONUS_6, ALIGNMENT_BONUS_7, ALIGNMENT_BONUS_8,
)

if app.ENABLE_GUILD_LEADER_GRADE_NAME:
	GUILD_LEADER_GRADE_NAME_LIST = (GUILD_LEADER_GRADE0, GUILD_LEADER_GRADE1)

def GetLetterImageName():
	return "icon/item/scroll_close.tga"
def GetLetterOpenImageName():
	return "icon/item/scroll_open.tga"
def GetLetterCloseImageName():
	return "icon/item/scroll_close.tga"

def GetBlueLetterImageName():
	return "icon/item/scroll_close_blue.tga"
def GetBlueLetterOpenImageName():
	return "icon/item/scroll_open_blue.tga"
def GetBlueLetterCloseImageName():
	return "icon/item/scroll_close_blue.tga"

def DO_YOU_SELL_ITEM(sellItemName, sellItemCount, sellItemPrice):
	if sellItemCount > 1:
		return DO_YOU_SELL_ITEM2 % (sellItemName, sellItemCount, NumberToMoneyString(sellItemPrice))
	else:
		return DO_YOU_SELL_ITEM1 % (sellItemName, NumberToMoneyString(sellItemPrice))

if app.ENABLE_CHEQUE_SYSTEM:
	def DO_YOU_BUY_ITEM(buyItemName, buyItemCount, buyItemPrice, sellItemCheque = 0):
		if sellItemCheque > 0:
			if buyItemCount > 1:
				return DO_YOU_BUY_ITEM4 % (buyItemName, buyItemCount, sellItemCheque, buyItemPrice)
			else:
				return DO_YOU_BUY_ITEM3 % (buyItemName, sellItemCheque, buyItemPrice)
		else:
			if buyItemCount > 1:
				return DO_YOU_BUY_ITEM2 % (buyItemName, buyItemCount, buyItemPrice)
			else:
				return DO_YOU_BUY_ITEM1 % (buyItemName, buyItemPrice)
else:
	def DO_YOU_BUY_ITEM(buyItemName, buyItemCount, buyItemPrice):
		if buyItemCount > 1:
			return DO_YOU_BUY_ITEM2 % (buyItemName, buyItemCount, buyItemPrice)
		else:
			return DO_YOU_BUY_ITEM1 % (buyItemName, buyItemPrice)

def REFINE_FAILURE_CAN_NOT_ATTACH(attachedItemName):
	return REFINE_FAILURE_CAN_NOT_ATTACH0 % (attachedItemName)

def REFINE_FAILURE_NO_SOCKET(attachedItemName):
	return REFINE_FAILURE_NO_SOCKET0 % (attachedItemName)

def REFINE_FAILURE_NO_GOLD_SOCKET(attachedItemName):
	return REFINE_FAILURE_NO_GOLD_SOCKET0 % (attachedItemName)

def HOW_MANY_ITEM_DO_YOU_DROP(dropItemName, dropItemCount):
	if dropItemCount > 1:
		return HOW_MANY_ITEM_DO_YOU_DROP2 % (dropItemName, dropItemCount)
	else:
		return HOW_MANY_ITEM_DO_YOU_DROP1 % (dropItemName)

def FISHING_NOTIFY(isFish, fishName):
	if isFish:
		return FISHING_NOTIFY1 % (fishName)
	else:
		return FISHING_NOTIFY2 % (fishName)

def FISHING_SUCCESS(isFish, fishName):
	if isFish:
		return FISHING_SUCCESS1 % (fishName)
	else:
		return FISHING_SUCCESS2 % (fishName)



if app.ENABLE_CHEQUE_SYSTEM:
	def NumberToMoneyString(n):
		if n <= 0:
			return "0"

		return "%s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))

	def NumberToChequeString(n):
		if n <= 0:
			return "0 %s" % (CHEQUE_SYSTEM_UNIT_WON)

		return "%s %s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]),CHEQUE_SYSTEM_UNIT_WON)

else:
	def NumberToMoneyString(n):
		if n <= 0:
			return "0 %s" % (MONETARY_UNIT0)

		return "%s %s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]), MONETARY_UNIT0)

def NumberToGemString(n) :
	if n <= 0 :
		return "0"
	return "%s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))


def NumberToMoneyStringNEW(n) :
	if n <= 0 :
		return "0"
	return "%s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))


def NumberToSecondaryCoinStringNew(n, coinType) :
	if n <= 0:
		n = 0

	coinTypeString = ""

	if app.ENABLE_ACHIEVEMENT_SYSTEM and coinType == shop.SHOP_COIN_TYPE_ACHIEVEMENT:
		coinTypeString = ACHIEVEMENT_COIN
	else:
		return "Not Valied"

	return "%s %s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]), coinTypeString)


def NumberToSecondaryCoinString(n):
	if n <= 0:
		return "0 %s" % (MONETARY_UNIT_JUN)

	return "%s %s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]), MONETARY_UNIT_JUN)

def NumberToDisplayedCount(n):
	if n <= 0 :
		return "0 %s" % (MONETARY_UNIT0)

	return "%s %s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]), MONETARY_UNIT0)

def NumberToDecimal(n):
	return "%s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))

def NumberToDecimalStringQuickSell(n):
	return "%s" % ('.'.join([i - 3 < 0 and str(n / 5)[:i] or str(n / 5)[i - 3:i] for i in range(len(str(n / 5)) % 3, len(str(n / 5)) + 1, 3) if i]))

def FormatVersion(n):
	return "Ver. %s" % ('.'.join([ i-1<0 and str(n)[:i] or str(n)[i-1:i] for i in range(len(str(n))%1, len(str(n))+1, 1) if i ]))

if app.ENABLE_SHOPEX_RENEWAL:
	def NumberToShopEXP(n):
		if n <= 0 :
			return "0 %s" % ("EXP")
		n = str(n)
		return "%s %s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]), "EXP")

def NumberToMoneyStringNoUnit(n) :
	if n <= 0 :
		return "0"

	return "%s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ])) 

def NumberToEXPString(n) :
	if n <= 0 :
		return "0"

	return "%s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))


def NumberToAchivString(n):
	if n <= 0:
		return "0 %s" % (ACHIEVEMENT_COIN)

	return "%s %s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]),ACHIEVEMENT_COIN)

def SecondToMS(time):
	if time < 60:
		return "%d%s" % (time, SECOND)

	second = int(time % 60)
	minute = int((time / 60) % 60)

	text = ""

	if minute > 0:
		text += str(minute) + MINUTE
		if minute > 0:
			text += " "

	if second > 0:
		text += str(second) + SECOND

	return text
