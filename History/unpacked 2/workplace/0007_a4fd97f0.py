# coding: latin_1

import app
import chrmgr
import net
import player

import os

WHISPER_CHAT_WINDOW = 1
MESSENGER_LAST_ONLINE = 1
GUILD_DUNGEON_TAB = 1

if app.USE_PREMIUM_FEATURES:
	player_premium_type = player.PREMIUM_TYPE_NONE

if app.ENABLE_VOICE_CHAT:
	VOICE_CHAT_CONFIG = {}
	VOICE_CHAT_CONFIG_LOADED = False
	def LoadVoiceChatConfig():
		global VOICE_CHAT_CONFIG_LOADED
		if VOICE_CHAT_CONFIG_LOADED:
			return

		with open("voicechat.cfg", "a+") as f:
			lines = f.readlines()

		for line in lines:
			data = line.replace("\n", "").split("\t")
			if len(data) < 2:
				continue

			try:
				VOICE_CHAT_CONFIG[data[0]] = float(data[1])
			except:
				pass

		VOICE_CHAT_CONFIG_LOADED = True

	def SendVoiceChatVolumes():
		for playerName, vol in VOICE_CHAT_CONFIG.items():
			try:
				volume = float(vol)#In case we have anything that isn't a number
				app.SetVoiceChatVolumeForSpeaker(playerName, volume)
			except:
				pass

	def GetVoiceChatVolume(playerName):
		global VOICE_CHAT_CONFIG_LOADED
		if not VOICE_CHAT_CONFIG_LOADED:
			LoadVoiceChatConfig()

		if playerName in VOICE_CHAT_CONFIG:
			return VOICE_CHAT_CONFIG[playerName]

		return 1.0 # Default to 100

	def GetVoiceChatConfig(option):
		global VOICE_CHAT_CONFIG_LOADED
		if not VOICE_CHAT_CONFIG_LOADED:
			LoadVoiceChatConfig()

		if option in VOICE_CHAT_CONFIG:
			return int(VOICE_CHAT_CONFIG[option])

		return 0

	def SetVoiceChatConfig(option, value):
		VOICE_CHAT_CONFIG[option] = value
		# SaveVoiceChatConfig()

	def SetVoiceChatVolume(playerName, vol):
		VOICE_CHAT_CONFIG[playerName] = vol
		# SaveVoiceChatConfig()

	def SaveVoiceChatConfig():
		lines = []
		for playerName, vol in VOICE_CHAT_CONFIG.items():
			lines.append("{}\t{}\n".format(playerName, vol))

		with open("voicechat.cfg", "w+") as f:
			f.writelines(lines)


if app.AUTO_HIDE_LOW_LEVELS_DUNGEONS:
	def IsDungeonHided(playerName, dungeonIndex):
		filePath = "UserData/dungeon/%s.cfg" % (playerName)

		if not os.path.exists(filePath):
			return 0

		try:
			infoFile = old_open(filePath, "rb")
			# dataFile = app.DecryptLocal(infoFile.read())
			dataFile = infoFile.read()
			infoFile.close()

			tmpDict = eval(dataFile)
			return tmpDict[dungeonIndex] if tmpDict.has_key(dungeonIndex) else False
		except:
			return 0

	def HideDungeon(playerName, dungeonIndex, isHIDED):
		folderPath = "UserData/dungeon/"

		if not os.path.exists(folderPath):
			os.makedirs(folderPath)

		filePath = folderPath + "%s.cfg" % (playerName)

		tmpDict = {}

		if os.path.exists(filePath):
			try:
				infoFile = old_open(filePath, "rb")
				# dataFile = app.DecryptLocal(infoFile.read())
				dataFile = infoFile.read()
				infoFile.close()

				tmpDict = eval(dataFile)
			except:
				pass

		tmpDict[dungeonIndex] = isHIDED

		try:
			infoFile = old_open(filePath, "wb")
			# encData = app.EncryptLocal(str(tmpDict))
			encData = str(tmpDict)
			infoFile.write(encData)
			infoFile.close()
		except:
			pass

if app.USE_DUNGEON_COOLDOWN_MANAGER:
	cooldownMapIndexAlert = 0

	def GetCooldownAlert(playerName, mapIndex):
		filePath = "UserData/cooldown/_%s.cfg" % (playerName)

		if not os.path.exists(filePath):
			return False

		try:
			infoFile = old_open(filePath, "rb")
			# dataFile = app.DecryptLocal(infoFile.read())
			dataFile = infoFile.read()
			infoFile.close()

			tmpDict = eval(dataFile)
			return tmpDict[mapIndex] if tmpDict.has_key(mapIndex) else False
		except:
			return False

	def GetCooldownsAlert(playerName):
		filePath = "UserData/cooldown/_%s.cfg" % (playerName)

		if not os.path.exists(filePath):
			return {}

		try:
			infoFile = old_open(filePath, "rb")
			# dataFile = app.DecryptLocal(infoFile.read())
			dataFile = infoFile.read()
			infoFile.close()

			return eval(dataFile)
		except:
			return {}

	def SetCooldownAlert(playerName, mapIndex, isON):
		folderPath = "UserData/cooldown/"

		if not os.path.exists(folderPath):
			os.makedirs(folderPath)

		filePath = folderPath + "_%s.cfg" % (playerName)

		tmpDict = {}

		if os.path.exists(filePath):
			try:
				infoFile = old_open(filePath, "rb")
				# dataFile = app.DecryptLocal(infoFile.read())
				dataFile = infoFile.read()
				infoFile.close()

				tmpDict = eval(dataFile)
			except:
				pass

		tmpDict[mapIndex] = isON

		try:
			infoFile = old_open(filePath, "wb")
			# encData = app.EncryptLocal(str(tmpDict))
			encData = str(tmpDict)
			infoFile.write(encData)
			infoFile.close()
		except:
			pass

		global cooldownMapIndexAlert
		cooldownMapIndexAlert = mapIndex

if app.USE_OFFLINESHOP:
	shopSearchTimeWait = 0.3  # offlineshop search rework: was 5s; now a tiny silent client debounce (server search is O(matches) + 250ms no-wipe)
	shopSearchWaitTime = 0

if app.ENABLE_FEATURES_OXEVENT:
	if not os.path.exists("UserData"):
		os.makedirs("UserData")
	
	if not os.path.exists("UserData\item_proto_list"):
		fileName = file("UserData\item_proto_list", "w")

if app.USE_WHEEL_OF_FORTUNE:
	dragon_coins=0

lastSentenceStack = []
lastSentencePos = 0
ip_adresses = ""
ENABLE_MAP_WEATHER = True
if ENABLE_MAP_WEATHER:
	CURRENT_WEATHER_INDEX = -1
	CURRENT_WEATHER_MAP = ""
	MAP_WEATHER_CONFIG = {
		"hisham_map_5": {
			"WEATHER_LIST": {
				0:"d",
				1:"d",
				2:"d:/ymir work/environment/hisham_ice.msenv",
				3:"d:/ymir work/environment/hisham_lava.msenv",
				4:"d:/ymir work/environment/hisham_dark.msenv",
				5:"d:/ymir work/environment/hisham_forst.msenv",
			},
			"WEATHER_POS_LIST": [
				{"From": {"x": 0, "y": 0}, "To": {"x": 0, "y": 0}},
				{"From": {"x": 0, "y": 0}, "To": {"x": 0, "y": 0}},
				{"From": {"x": 0, "y": 0}, "To": {"x": 360, "y": 370}},
				{"From": {"x": 0, "y": 380}, "To": {"x": 400, "y": 768}},
				{"From": {"x": 410, "y": 408}, "To": {"x": 768, "y": 768}},
				{"From": {"x": 368, "y": 0}, "To": {"x": 768, "y": 380}},
			],
		},
		"different_map_10": {
			"WEATHER_LIST": {
				0:"d",
				1:"d",
				2:"d:/ymir work/environment/h_1.msenv",
				3:"d:/ymir work/environment/h_2.msenv",
				4:"d:/ymir work/environment/h_5.msenv",
				5:"d:/ymir work/environment/h_4.msenv",
				6:"d:/ymir work/environment/h_5.msenv",
			},
			"WEATHER_POS_LIST": [
				{"From": {"x": 0, "y": 0}, "To": {"x": 0, "y": 0}},
				{"From": {"x": 0, "y": 0}, "To": {"x": 0, "y": 0}},
				{"From": {"x": 0, "y": 1300}, "To": {"x": 600, "y": 1792}},
				{"From": {"x": 601, "y": 863}, "To": {"x": 1024, "y": 1792}},
				{"From": {"x": 295, "y": 0}, "To": {"x": 1024, "y": 781}},
				{"From": {"x": 0, "y": 0}, "To": {"x": 294, "y": 524}},
				{"From": {"x": 0, "y": 525}, "To": {"x": 513, "y": 1177}},
			],
		},
	}
# option
if app.DEATHMATCH_EVENT:	
	DEATHMATCH_WINDOW_IS_SHOWED = 0	
Hava = 0
Page = 0
CONSOLE_ENABLE = 0
GIFT_INPUT = 0
INPUT_IGNORE = 0
PVPMODE_ENABLE = 1
#PVPMODE_TEST_ENABLE = 0
PVPMODE_ACCELKEY_ENABLE = 1
PVPMODE_ACCELKEY_DELAY = 0.5
PVPMODE_PROTECTED_LEVEL = 30

FOG_LEVEL0 = 4800.0
FOG_LEVEL1 = 9600.0
FOG_LEVEL2 = 12800.0
FOG_LEVEL = FOG_LEVEL0
FOG_LEVEL_LIST=[FOG_LEVEL0, FOG_LEVEL1, FOG_LEVEL2]

CAMERA_MAX_DISTANCE_SHORT = 2500.0
CAMERA_MAX_DISTANCE_LONG = 3500.0 * 2
if app.ENABLE_12ZI:
	CAMERA_MAX_DISTANCE_12ZI = 5000.0
CAMERA_MAX_DISTANCE_LIST=[CAMERA_MAX_DISTANCE_SHORT, CAMERA_MAX_DISTANCE_LONG]
CAMERA_MAX_DISTANCE = CAMERA_MAX_DISTANCE_SHORT

CHRNAME_COLOR_INDEX = 0

ENVIRONMENT_NIGHT="d:/ymir work/environment/moonlight04.msenv"
SHOW_INTROLOADING = True
PLAYER_IN_GAME = False
SELECTED_CHANNEL = 0
FAST_LOGIN_PENDING_PWD = ""
FAST_LOGIN_ATTEMPTED = False
FAST_LOGIN_AUTO_SLOT = -1
FAST_LOGIN_AUTOSAVE = True
HP_ANIMATION_SHOW = True
# constant
HIGH_PRICE = 500000
MIDDLE_PRICE = 50000
ERROR_METIN_STONE = 28960
SUB2_LOADING_ENABLE = 1
EXPANDED_COMBO_ENABLE = 1
CONVERT_EMPIRE_LANGUAGE_ENABLE = 1
USE_ITEM_WEAPON_TABLE_ATTACK_BONUS = 0
ADD_DEF_BONUS_ENABLE = 1
LOGIN_COUNT_LIMIT_ENABLE = 0

USE_SKILL_EFFECT_UPGRADE_ENABLE = 1

VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD = 1
GUILD_MONEY_PER_GSP = 100
GUILD_WAR_TYPE_SELECT_ENABLE = 1
TWO_HANDED_WEAPON_ATT_SPEED_DECREASE_VALUE = 0
if app.ENABLE_PVP_ROUTES:
	RoutesPvPSystem = {
		'puntos' : 0,
		'recompensa' : 0,
	}

HAIR_COLOR_ENABLE = 1
ARMOR_SPECULAR_ENABLE = 1
WEAPON_SPECULAR_ENABLE = 1
KEEP_ACCOUNT_CONNETION_ENABLE = 1
MINIMAP_POSITIONINFO_ENABLE = 0
CONVERT_EMPIRE_LANGUAGE_ENABLE = 0
USE_ITEM_WEAPON_TABLE_ATTACK_BONUS = 0
ADD_DEF_BONUS_ENABLE = 0
LOGIN_COUNT_LIMIT_ENABLE = 0
PVPMODE_PROTECTED_LEVEL = 15
TWO_HANDED_WEAPON_ATT_SPEED_DECREASE_VALUE = 10
CHEST_DROP_INFO_DATA = {}
isItemQuestionDialog = 0

ALREADY_NOTIFY_LIST = []
if app.QUICK_SELL_SYSTEM:
	# quick-sell cart, shared by every bag window: {(windowType, slot): (vnum, count)}
	QUICK_SELL_ITEMS = {}

def GET_ITEM_QUESTION_DIALOG_STATUS():
	global isItemQuestionDialog
	return isItemQuestionDialog

def GetFlag(flagname):
	global py_Flag
	return py_Flag.get(flagname, None)
def SetFlag(flagname,value):
	global py_Flag
	py_Flag[flagname] = value


def SET_ITEM_QUESTION_DIALOG_STATUS(flag):
	global isItemQuestionDialog
	isItemQuestionDialog = flag

def SET_DEFAULT_FOG_LEVEL():
	global FOG_LEVEL
	app.SetMinFog(FOG_LEVEL)

def SET_FOG_LEVEL_INDEX(index):
	global FOG_LEVEL
	global FOG_LEVEL_LIST
	try:
		FOG_LEVEL=FOG_LEVEL_LIST[index]
	except IndexError:
		FOG_LEVEL=FOG_LEVEL_LIST[0]
	app.SetMinFog(FOG_LEVEL)

def GET_FOG_LEVEL_INDEX():
	global FOG_LEVEL
	global FOG_LEVEL_LIST
	return FOG_LEVEL_LIST.index(FOG_LEVEL)

def SET_DEFAULT_CAMERA_MAX_DISTANCE():
	global CAMERA_MAX_DISTANCE
	app.SetCameraMaxDistance(CAMERA_MAX_DISTANCE)

def SET_CAMERA_MAX_DISTANCE_INDEX(index):
	global CAMERA_MAX_DISTANCE
	global CAMERA_MAX_DISTANCE_LIST
	try:
		CAMERA_MAX_DISTANCE=CAMERA_MAX_DISTANCE_LIST[index]
	except:
		CAMERA_MAX_DISTANCE=CAMERA_MAX_DISTANCE_LIST[0]

	app.SetCameraMaxDistance(CAMERA_MAX_DISTANCE)

def GET_CAMERA_MAX_DISTANCE_INDEX():
	global CAMERA_MAX_DISTANCE
	global CAMERA_MAX_DISTANCE_LIST
	return CAMERA_MAX_DISTANCE_LIST.index(CAMERA_MAX_DISTANCE)

if app.ENABLE_12ZI:
	def SET_CAMERA_MAX_DISTANCE_12ZI():
		app.SetCameraMaxDistance(CAMERA_MAX_DISTANCE_12ZI)

def SET_DEFAULT_CHRNAME_COLOR():
	global CHRNAME_COLOR_INDEX
	chrmgr.SetEmpireNameMode(CHRNAME_COLOR_INDEX)

def SET_CHRNAME_COLOR_INDEX(index):
	global CHRNAME_COLOR_INDEX
	CHRNAME_COLOR_INDEX=index
	chrmgr.SetEmpireNameMode(index)

def GET_CHRNAME_COLOR_INDEX():
	global CHRNAME_COLOR_INDEX
	return CHRNAME_COLOR_INDEX

def SET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD(index):
	global VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD
	VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD = index

def GET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD():
	global VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD
	return VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD

def SET_DEFAULT_CONVERT_EMPIRE_LANGUAGE_ENABLE():
	global CONVERT_EMPIRE_LANGUAGE_ENABLE
	net.SetEmpireLanguageMode(CONVERT_EMPIRE_LANGUAGE_ENABLE)

def SET_DEFAULT_USE_ITEM_WEAPON_TABLE_ATTACK_BONUS():
	global USE_ITEM_WEAPON_TABLE_ATTACK_BONUS
	player.SetWeaponAttackBonusFlag(USE_ITEM_WEAPON_TABLE_ATTACK_BONUS)

def SET_DEFAULT_USE_SKILL_EFFECT_ENABLE():
	global USE_SKILL_EFFECT_UPGRADE_ENABLE
	app.SetSkillEffectUpgradeEnable(USE_SKILL_EFFECT_UPGRADE_ENABLE)

def SET_TWO_HANDED_WEAPON_ATT_SPEED_DECREASE_VALUE():
	global TWO_HANDED_WEAPON_ATT_SPEED_DECREASE_VALUE
	app.SetTwoHandedWeaponAttSpeedDecreaseValue(TWO_HANDED_WEAPON_ATT_SPEED_DECREASE_VALUE)

def ConvertMoneyText(text, powers = dict(k = 10**3, m = 10**6, b = 10**9)):
	match = re.search(r'(\d+)({:s}+)?'.format('+|'.join(powers.keys())), text.lower(), re.I)
	if match:
		moneyValue, suffixName = match.groups()
		moneyValue = int(moneyValue)
		if not suffixName:
			return moneyValue

		return moneyValue * (powers[suffixName[0]] ** len(suffixName))

	return 0
def CanSwitchItemBonus(itemIndex):
	if (itemIndex >= 41005 and itemIndex <= 41010 or itemIndex >= 40136 and itemIndex <= 40153):
		return False;
	

	if (itemIndex == 45274 or itemIndex == 45276):
		return False;
	

	if (itemIndex >= 73001 and itemIndex <= 73012 or itemIndex >= 75001 and itemIndex <= 75012):
		return False;


	if (itemIndex >= 73251 and itemIndex <= 73262 or itemIndex >= 75201 and itemIndex <= 75212):
		return False;


	if (itemIndex >= 73501 and itemIndex <= 73512 or itemIndex >= 75401 and itemIndex <= 75412):
		return False;


	if (itemIndex >= 73751 and itemIndex <= 73762 or itemIndex >= 75601 and itemIndex <= 75612):
		return False;
	

	if (itemIndex >= 11901 and itemIndex <= 11904 or itemIndex >= 11911 and itemIndex <= 11914):
		return False;
	

	if (itemIndex == 50201 or itemIndex == 50202):
		return False;
	
	return True


if app.ENABLE_SWITCHBOT:
	def CanPutItemInSwitchbot(itemIndex):
		item.SelectItem(itemIndex)

		if not CanSwitchItemBonus(itemIndex):
			return False
		
		if not item.GetItemType() in [item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR, item.ITEM_TYPE_COSTUME]:
			return False
		
		if item.GetItemType() == item.ITEM_TYPE_WEAPON and\
			item.GetItemSubType() in [item.WEAPON_ARROW,item.WEAPON_QUIVER]:
			return False

		if item.GetItemType() == item.ITEM_TYPE_ARMOR and\
			not item.GetItemSubType() in [item.ARMOR_BODY, item.ARMOR_HEAD, item.ARMOR_SHIELD, item.ARMOR_WRIST, item.ARMOR_FOOTS, item.ARMOR_NECK, item.ARMOR_EAR, item.ARMOR_PENDANT_FIRE, item.ARMOR_PENDANT_ICE, item.ARMOR_PENDANT_THUNDER, item.ARMOR_PENDANT_WIND, item.ARMOR_PENDANT_EARTH, item.ARMOR_PENDANT_DARK]:
			return False

		if item.GetItemType() == item.ITEM_TYPE_COSTUME and\
			not item.GetItemSubType() in [item.COSTUME_TYPE_BODY, item.COSTUME_TYPE_HAIR, item.COSTUME_TYPE_WEAPON]:
			return False
		
		return True

def NumberToStrRomanNumerals(number):
	ROMAN = [
		(1000, "M"),
		( 900, "CM"),
		( 500, "D"),
		( 400, "CD"),
		( 100, "C"),
		(  90, "XC"),
		(  50, "L"),
		(  40, "XL"),
		(  10, "X"),
		(   9, "IX"),
		(   5, "V"),
		(   4, "IV"),
		(   1, "I"),
	]
	
	result = ""
	for (arabic, roman) in ROMAN:
		(factor, number) = divmod(number, arabic)
		result += roman * factor
	return result

import item

ACCESSORY_MATERIAL_LIST = [50623, 50624, 50625, 50626, 50627, 50628, 50629, 50630, 50631, 50632, 50633, 50634, 50635, 50636, 50637, 50638, 50639
							,50661,50662,50663,50664]


JewelAccessoryInfos = [
		[ 50634, 14420, 16220, 17220 ],
		[ 50635, 14500, 16500, 17500 ],
		[ 50636, 14520, 16520, 17520 ],
		[ 50637, 14540, 16540, 17540 ],
		[ 50638, 14560, 16560, 17560 ],
		[ 50639, 14570, 16570, 11980 ],
		[ 50661, 14590, 16590, 17580 ],
		[ 50662, 14600, 16600, 17591 ],
		[ 50663, 14610, 16610, 17600 ],
		[ 50664, 14580, 16580, 17570 ],
		[ 50664, 84610, 86610, 87600 ],
		[ 50637, 16720, 16710, 16730 ],
	]

def GET_ACCESSORY_MATERIAL_VNUM(vnum, subType):
	ret = vnum
	item_base = (vnum / 10) * 10
	for info in JewelAccessoryInfos:
		if item.ARMOR_WRIST == subType:
			if info[1] == item_base:
				return info[0]
		elif item.ARMOR_NECK == subType:
			if info[2] == item_base:
				return info[0]
		elif item.ARMOR_EAR == subType:
			if info[3] == item_base:
				return info[0]
 
	if vnum >= 16210 and vnum <= 16219:
		return 50625

	if item.ARMOR_WRIST == subType:
		WRIST_ITEM_VNUM_BASE = 14000
		ret -= WRIST_ITEM_VNUM_BASE
	elif item.ARMOR_NECK == subType:
		NECK_ITEM_VNUM_BASE = 16000
		ret -= NECK_ITEM_VNUM_BASE
	elif item.ARMOR_EAR == subType:
		EAR_ITEM_VNUM_BASE = 17000
		ret -= EAR_ITEM_VNUM_BASE

	type = ret/20

	if type<0 or type>=len(ACCESSORY_MATERIAL_LIST):
		type = (ret-170) / 20
		if type<0 or type>=len(ACCESSORY_MATERIAL_LIST):
			return 0

	return ACCESSORY_MATERIAL_LIST[type]

def GET_BELT_MATERIAL_VNUM(vnum, subType = 0):
	return 18900

def IS_AUTO_POTION(itemVnum):
	return IS_AUTO_POTION_HP(itemVnum) or IS_AUTO_POTION_SP(itemVnum)

def IS_AUTO_POTION_HP(itemVnum):
	if 72723 <= itemVnum and 72726 >= itemVnum:
		return 1
	elif itemVnum >= 76021 and itemVnum <= 76022:
		return 1
	elif itemVnum == 79012:
		return 1
	
	if app.USE_INFINITE_AUTO_RECOVERY_POTIONS and\
		itemVnum == 72731:
		return 1
	
	return 0

def IS_AUTO_POTION_SP(itemVnum):
	if 72727 <= itemVnum and 72730 >= itemVnum:
		return 1
	elif itemVnum >= 76004 and itemVnum <= 76005:
		return 1
	elif itemVnum == 79013:
		return 1
	
	if app.USE_INFINITE_AUTO_RECOVERY_POTIONS and\
		itemVnum == 72732:
		return 1
	
	return 0

if app.ENABLE_GROWTH_PET_SYSTEM:
	def IS_PET_ITEM(itemVnum):
		if itemVnum == 0:
			return 0
			
		item.SelectItem(itemVnum)
		itemType = item.GetItemType()
		itemSubType = item.GetItemSubType()
		
		if itemType == item.ITEM_TYPE_PET and itemSubType == item.PET_UPBRINGING:
			return 1
			
		return 0

ENABLE_MULTI_RANKING=1

WeatherIndex = 1  # Current weather selection (1-9)
SaveWeatherEnabled = False  # Whether to persist weather across sessions

#WEATHER_SKYBOX_1 = "d:/ymir work/environment/different_kingdoms.msenv"
WEATHER_SKYBOX_1 = "d:/ymir work/environment/skysun.msenv"
#WEATHER_SKYBOX_2 = "d:/ymir work/environment/hisham_dark.msenv"
#WEATHER_SKYBOX_3 = "d:/ymir work/environment/hisham_forst.msenv"
#WEATHER_SKYBOX_4 = "d:/ymir work/environment/hisham_ice.msenv"
#WEATHER_SKYBOX_5 = "d:/ymir work/environment/hisham_normal.msenv"
#WEATHER_SKYBOX_6 = "d:/ymir work/environment/horus_pvp.msenv"
#WEATHER_SKYBOX_7 = "d:/ymir work/environment/ridack_day2.msenv"
#WEATHER_SKYBOX_8 = "d:/ymir work/environment/map_dd.msenv"

ALCHEMY_SKYBOX_01="d:/ymir work/environment/noapteok.msenv"
WEATHER_SKYBOX_2="d:/ymir work/environment/noonsky.msenv"
WEATHER_SKYBOX_3="d:/ymir work/environment/storm.msenv"

WEATHER_SKYBOX_4="d:/ymir work/environment/cernou.msenv"
WEATHER_SKYBOX_5="d:/ymir work/environment/ziua.msenv"
WEATHER_SKYBOX_6="d:/ymir work/environment/wow.msenv"

WEATHER_SKYBOX_7="d:/ymir work/environment/CerApus.msenv"
WEATHER_SKYBOX_8="d:/ymir work/environment/CerRosu.msenv"
ALCHEMY_SKYBOX_09="d:/ymir work/environment/CerApus2.msenv"
ALCHEMY_SKYBOX_10="d:/ymir work/environment/cerapus3.msenv"
ALCHEMY_SKYBOX_11="d:/ymir work/environment/cerapus4.msenv"
ALCHEMY_SKYBOX_12="d:/ymir work/environment/cernou.msenv"
ALCHEMY_SKYBOX_13="d:/ymir work/environment/ziua.msenv"
ALCHEMY_SKYBOX_14="d:/ymir work/environment/wow.msenv"
ALCHEMY_SKYBOX_15="d:/ymir work/environment/baf.msenv"
ALCHEMY_SKYBOX_16="d:/ymir work/environment/storm.msenv"


WEATHER_SKIP_MAPS = (
	"metin2_map_deviltower1",
	"metin2_map_spiderdungeon",
	"metin2_map_spiderdungeon_02",
	"metin2_map_spiderdungeon_03",
	"metin2_map_skipia_dungeon_01",
	"metin2_map_skipia_dungeon_02",
)

py_Flag = {}
def GetFlag(flagname):
	global py_Flag
	return py_Flag.get(flagname, None)
def SetFlag(flagname,value):
	global py_Flag
	py_Flag[flagname] = value

# ENABLE_CASUAL_BUFF: mirrored by interfacemodule.OnCasualBuffInfo so any
# widget can read the buff state without coupling to the character window
CASUAL_BUFF_ACTIVE = 0

# ENABLE_PVM_CLASS_BALANCE: latest PvM-balance state pushed by the server
# (game.RecvPvmBalanceInfo). Read by uitooltip + the intro popup.
PVM_BALANCE = {"bound":0, "level":0, "grade":0, "bonusA":0, "bonusB":0}
PVM_BALANCE_ACTIVE = 0  # set to 1 by game.RecvPvmBalanceInfo when the server reports the feature live (non-warrior)

# Buffi: live summary cache for the skill-tab tooltip + the summon-scroll item tooltip. BUFFI_SUMMONED
# / BUFFI_TOOLTIP_INT are kept current by the server "BuffiInt" command; the rest are cached on every
# buffi status push (interface.OnBuffiStatus) so the summon-item tooltip can show a live buffi summary
# (name / level / ores) without opening the Companion window. (Skills are read live from the player.)
BUFFI_SUMMONED    = 0
BUFFI_TOOLTIP_INT = 90
BUFFI_TT_INT      = 0           # real INT from the full status push (decoupled from BuffiInt's unsummon reset)
BUFFI_TT_LEVEL    = 0
BUFFI_TT_NAME     = ""
BUFFI_TT_ORES     = (0, 0, 0)   # socketed ore item vnums
BUFFI_TT_EXPIRE   = 0           # duration expire_at unix ts (0 = no buffi yet, 0xFFFFFFFF = permanent)

# Buffi item type + subtypes (mirror of server EItemTypes/EBuffiSubTypes -- ITEM_BUFFI=46; the client
# proto carries the same numeric type, but there is no item.ITEM_TYPE_BUFFI Python constant, so we
# detect buffi items numerically here). Used for the active-item icon highlight + the item tooltip.
ITEM_TYPE_BUFFI       = 46
BUFFI_SUBTYPE_SUMMON  = 0   # tier summon scroll (active while the buffi is summoned)
BUFFI_SUBTYPE_NAME    = 1   # name scroll
BUFFI_SUBTYPE_ORE     = 2   # +INT ore (socketed)
BUFFI_SUBTYPE_RECHARGE = 3  # adds uptime days
BUFFI_SUBTYPE_PERMANENT = 4 # permanent uptime

# Buffi SUMMON-scroll vnums. NOTE: the buffi item *subtype* is unreliable client-side unless the
# item_proto is rebuilt with the BUFFI_* subtype mapping, so we identify the summon scroll(s) by vnum
# instead (the ore/name/recharge/permanent items 91120-91124 must NOT match). Add tier vnums here.
BUFFI_SUMMON_VNUMS = (91110,)

def IS_BUFFI_SUMMON_ITEM(itemVnum):
	# True only for a buffi SUMMON scroll (the item that stays "active" while the buffi is out, and the
	# only one that gets the live summary tooltip / the active-icon highlight). Vnum-based on purpose --
	# the proto subtype reads as 0 for all buffi items on an un-rebuilt client.
	return 1 if itemVnum in BUFFI_SUMMON_VNUMS else 0

# Solo Leadership Bonus (ENABLE_SOLO_LEADERSHIP_BONUS)
SOLO_LEADERSHIP_ACTIVE = 0
SOLO_LEADERSHIP_BONUS = [0, 0, 0, 0, 0, 0]

# PVP Order (ENABLE_PVP_ORDER)
PVP_ORDER = 0

AUTO_CHEST_DEADLINES = {}
AUTO_CHEST_ACTIVE = 0
