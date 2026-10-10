# coding: latin_1

import app

if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
	isExtraWindowWhenClosingInventory = 0

DEBUG_MODE = False # Debug mode (debug info and console)

USE_NEW_WHISPER_LETTER_CATEGORY = False # Use the new letter category for normal and gm players

WHISPER_ON_CHAT_LINE = True # Show whisper in chat line
PAST_HEALTH_ON_TARGET = True # Show past health on target (yellow gauge)
SHOW_LOADING_PROGRESS = True # Show loading progress
EXTENDED_LOADING_GUAGE = True # Loading guage extended with description
AFFECT_DISPLAY_IN_THINBOARD = False # Show align affect's using a ThinBoard
FILTER_EMOJI_NOTICE = True # Filter emojis on tip notice or big notice to chat line

SHOW_EMOJI_IN_CHAT_LINE = True # Show emoji in chat line
SHOW_EMOJI_IN_WHISPER_LINE = True # Show emoji in whisper line
SHOW_USE_IMAGE_TEXT_LINE = True # Show use item image text line in tooltip
SHOW_SELL_IMAGE_TEXT_LINE = False # Show sell item image text line in tooltip

SHOW_REFINE_ITEM_DESC = True # Show refine item description
ENABLE_OLD_QUEST_LETTER_LIST = True # Enable the old quest letter list

EVENT_BANNER = True # Show event banner instead of mini-game rumi button

SHOW_REFINE_PERCENTAGE = True # Show refine success percentage

MOUNT_ITEM_ATTR_TOOLTIP = True # Show quest item attributes on tooltip
PET_ITEM_ATTR_TOOLTIP = True # Show quest item attributes on tooltip
SHOW_BELT_SLOTS_TOOLTIP = False # Show maximum slots of belt item on tooltip
SHOW_ITEM_VNUM_TOOTIP = True # Show the item vnum

LOGIN_UI_MODIFY = False # Login countdown
NEW_SELECT_UI = True # New select character interface
NEW_CREATE_UI = True # New create character interface
SELECT_CHARACTER_ROTATION = True # Enables character rotation in select phase.

BETA_PVP = False #enable the beta for players

if app.ENABLE_SKILL_COLOR_SYSTEM:
	SKILL_COLOR_BUFF_ONLY = False # Enable skill color button on buffs only

##################################################################################

if app.ENABLE_EXPRESSING_EMOTION:
	import emotion
	EXPRESSING_EMOTIONS = {}

if app.ENABLE_HIDE_COSTUME_SYSTEM:
	HIDDEN_BODY_COSTUME = 0
	HIDDEN_HAIR_COSTUME = 0
	if app.USE_ACCE_SYSTEM:
		HIDDEN_ACCE_COSTUME = 0
	if app.USE_WEAPON_COSTUME_SYSTEM:
		HIDDEN_WEAPON_COSTUME = 0
	HIDDEN_AURA_COSTUME = 0
if app.ENABLE_HIDE_SHINING_SYSTEM:
	HIDDEN_SHINING_WEAPON = 0
	HIDDEN_SHINING_ARMOR = 0
	HIDDEN_SHINING_SPECIAL = 0
	if app.USE_MOUNT_SKIN:
		HIDDEN_MOUNT_SKIN = 0
	if app.USE_PET_SKIN:
		HIDDEN_PET_SKIN = 0
	if getattr(app, "USE_ACCE_SKIN", 0):
		HIDDEN_ACCE_SKIN = 0

if app.WHEEL_INGAME:
	rewardItem = 0
	WHEEL_METINSTONE_COUNT = 0

INPUT_IGNORE = 0

# MINI_GAME
if app.ENABLE_MINI_GAME_OKEY:
	RUMI_GAME_EVENT = True
if app.ENABLE_MINI_GAME_CATCH_KING:
	CATCH_KING_GAME_EVENT = True
if app.ENABLE_MINI_GAME_BNW:
	BNW_GAME_EVENT = True

if app.USE_BL_FISH_EVENT:
	JIGSAW_EVENT = True

# END_OF_MINI_GAME

if app.ENABLE_AUTO_REFINE:
	AUTO_REFINE = False
	IS_AUTO_REFINE = False
	AUTO_REFINE_TYPE = 0
	AUTO_REFINE_DATA = {
		"ITEM" : [-1, -1],
		"NPC" : [0, -1, -1, 0]
	}

def IsDebugMode():
	if DEBUG_MODE == True:
		return True

	return False

def IS_PET_SEAL(itemVnum):
	if itemVnum >= 53001 and itemVnum <= 53309 :
		return 1
	elif itemVnum >= 34321 and itemVnum <= 34459 :
		return 1
	elif itemVnum == 54280 or itemVnum == 54283 :
		return 1
	elif itemVnum == 54301 or itemVnum == 54302 :
		return 1
	elif itemVnum == 54303 or itemVnum == 54008 :
		return 1
	elif itemVnum == 54304 or itemVnum == 54305 :
		return 1
	elif itemVnum == 54306 or itemVnum == 54307 :
		return 1
	elif itemVnum == 54018 or itemVnum == 54021 :
		return 1
	elif itemVnum >=  72802 and itemVnum <= 72808 :
		return 1
	return 0

def IS_ANTI_EXP_RING(itemVnum):
	if itemVnum == 72501:
		return 1

	return 0

if app.ENABLE_EXTENDED_BLEND_AFFECT:
	def IS_BLEND_POTION(itemVnum):
		return itemVnum in {51002, 27209, 27212} or 50842 <= itemVnum <= 50847 or 50821 <= itemVnum <= 50832 or 99139 <= itemVnum <= 99144 or \
			itemVnum in {27213,27214,27215,27216,39017, 39217, 39018, 39218, 39019, 39219, 39020, 39220, 71044, 39224, 71045, 39225}

	def NORMAL_BLEND_COLOR(itemVnum):
		return 50821 <= itemVnum <= 50832 or 99139 <= itemVnum <= 99144 or 27213 <= itemVnum <= 27216 or 50842 <= itemVnum <= 50847

	def DRAGON_GOD_COLOR(itemVnum):
		return itemVnum in {39017, 39217, 39018, 39218, 39019, 39219, 39020, 39220, 71044, 39224, 71045, 39225,51002}

	def OTHER_ITEMS_COLOR(itemVnum):
		return itemVnum in {27209, 27212}

	def IS_EXTENDED_BLEND_POTION(itemVnum):
		return itemVnum in {951002, 939024, 939025, 927209, 927212} or 950821 <= itemVnum <= 950826 or \
			939017 <= itemVnum <= 939020 or \
			950830 <= itemVnum <= 950832

if app.ENABLE_EXPRESSING_EMOTION:
	def GET_SPECIAL_EMOTION_NAME(idx):
		if idx >= app.SPECIAL_ACTION_START_INDEX and idx <= emotion.EMOTION_WHIRL:
			return emotion.SPECIAL_EMOTION_DICT[idx]["name"]

def StripColor(text):
	import re

	regex = '\|c([a-zA-Z0-9]){0,8}|'
	search = re.search(regex, text)
	if search:
		text = re.sub(regex, '', text)

	return text

def IsEmojiFilter(text):
	import re

	regex = '\|I.*\|i'
	search = re.search(regex, text)
	if search:
		return True

	return False

def IsHyperLinkFilter(text):
	import re

	regex = '\|H.*\|h'
	search = re.search(regex, text)
	if search:
		return True

	return False

def EmojiFilter(text):
	import re

	EMOJI_DIC = {
		':o' : 'emoji/amazed',
		':)' : 'emoji/happiness',
		':D' : 'emoji/happy',
		':\\' : 'emoji/indifferent',
		':p' : 'emoji/tongue',
		':P' : 'emoji/tongue',
		'xP' : 'emoji/dead',
		':X' : 'emoji/muted',
		':x' : 'emoji/muted',
		'>:D' : 'emoji/evil',
		':J' : 'emoji/in-love',
		'<3' : 'emoji/heart',
		':*' : 'emoji/kiss',
		':O' : 'emoji/surprised',
		'>:(' : 'emoji/angry',
		':||' : 'emoji/quiet',
	}

	for emoji_str, emoji_img in EMOJI_DIC.iteritems():
		text = text.replace(emoji_str, "|I" + emoji_img + "|i")

	return text
