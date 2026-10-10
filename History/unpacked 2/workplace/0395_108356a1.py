#author: dracaryS

#static
import ui, constinfo, localeinfo , osfinfo
from operator import truediv

#dynamic
import grp, player, wndMgr, item, net, skill, nonplayer , app
import net
import chat
import datetime
import uichallengetooltip
import uiofflineshop_ae
if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget
import ingamewiki

import systemSetting

IMG_DIR = "d:/ymir work/ui/game/reward_info/"
IMG_ICON_DIR = "d:/ymir work/ui/game/reward_info/icons/"

MEDAL_COLORS = [0xffffda79, 0xffc0c0c0, 0xffcd7f32]  # gold, silver, bronze
MEDAL_LABELS = ["1st", "2nd", "3rd"]
MEDAL_ICONS = ["1st.png", "2nd.png", "3rd.png"]
WINNER_X_POSITIONS = [336, 233, 130]
WINNER_Y = 16
MAX_NAME_DISPLAY = 12

IMG_CHALLENGE_DIR = "d:/ymir work/ui/game/challenges/"
TROPHY_ICONS = ["Throphy_Gold.png", "Throphy_Silver.png", "Throphy_Bronze.png"]
TAB_IMAGES = ["global_challenge", "solo_challenge"]

# Inner_Board.png paints a 3px frame on every side, so the usable interior is 493x376 -- not the
# full 499x382. Five rows therefore need a 75 step (375), not 76, or the last one clips the frame.
INNER_W, INNER_H = 499, 382
INNER_BORDER = 3
ROW_W, ROW_H, ROW_STEP = 481, 70, 75
ROWS_PER_PAGE = 5
# ui.ListBoxEx.GetItemViewCoord right-aligns items on an Arabic client with a hardcoded 10px
# margin (self.GetWidth() - itemWidth - 10). SetItemSize is what sets the list's width, so the
# list has to be told it is 10 wider than the row or every row lands at x -10.
LISTBOX_ARABIC_MARGIN = 10
LIST_H = ROWS_PER_PAGE * ROW_STEP
LIST_X, LIST_Y = INNER_BORDER + 1, INNER_BORDER
SCROLL_X = INNER_W - INNER_BORDER - 10

# BoardWithTitleBar puts its content below a 30px title bar; the footer matches the side margin
# so the frame closes evenly instead of leaving a dead strip under the last row.
BOARD_TITLE_H, BOARD_MARGIN = 30, 8
BOARD_W = INNER_W + BOARD_MARGIN * 2
BOARD_H = BOARD_TITLE_H + INNER_H + BOARD_MARGIN
# The tab strip starts level with the top of the inner board, not below it.
TAB_STRIP_W, TAB_Y, TAB_STEP = 30, BOARD_TITLE_H, 34

# Three bands, separators baked at y 22-25 and 45-48, so the interiors start here.
BAND_TOP = [3, 26, 49]
TEXT_X, TEXT_W = 140, 263
TEXT_RIGHT = TEXT_X + TEXT_W
SLOT_X = [7, 50, 93]        # 38x38 frames baked into the reward panel
SLOT_Y = 16
SLOT_ICON_OFFSET = 3        # a 32x32 item icon centres inside a 38px frame

# The row art runs rewards-left / deco-right, so every text field is anchored to the field's
# right edge and the placement pager sits at the far right of band 2.
PAGER_NEXT_X = TEXT_RIGHT - 5
TROPHY_X = PAGER_NEXT_X - 4 - 17
PAGER_PREV_X = TROPHY_X - 4 - 5
WINNER_NAME_RIGHT = PAGER_PREV_X - 6


# --- personal tab: weekly challenges -----------------------------------------------------
# The personal row art leaves the reward panel empty, which is exactly what lets the reward
# count vary 1-3: the slots are drawn here instead of being baked in like the global row's
# three 38px frames.
PERSONAL_ROW_NORMAL = "personal_challenges_normal.png"
PERSONAL_ROW_DONE = "personal_challenges_done.png"
PERSONAL_SLOT_IMAGE = "personal_slot.png"
PERSONAL_SLOT_SIZE = 32
PERSONAL_SLOT_GAP = 8
PERSONAL_PANEL_X, PERSONAL_PANEL_W = 2, 134

# Rewards and the Activate button share the empty left panel, stacked: the button is 138 wide
# and putting it in band 3 left the time line 117px of a 263px field, which does not hold
# "Time limit: 5 Minutes". The panel is the same side the reward strip is on, so the grouping
# also matches the design sketch. Panel interior is y 1-68 and 4+32+6+24 fills it exactly.
# These are the values to nudge against a live render -- docs/WEEKLY_CHALLENGES.md 4.0, decision 1.
PERSONAL_SLOT_Y = 6
ACTIVATE_W, ACTIVATE_H = 138, 24
ACTIVATE_Y = 42
ACTIVATE_X = max(1, PERSONAL_PANEL_X + (PERSONAL_PANEL_W - ACTIVATE_W) // 2)

CHALLENGE_AVAILABLE, CHALLENGE_ONGOING, CHALLENGE_COMPLETED, CHALLENGE_LOCKED = range(4)
MAX_CHALLENGE_REWARDS = 3

# One warm palette. The row used to carry seven unrelated hues -- a green title, a red one, a
# grey clock -- which read as decoration rather than meaning. Four roles, four colours.
CHALLENGE_TITLE_COLOR = 0xfff2e7c1           # mission title
CHALLENGE_OBJECTIVE_COLOR = 0xffc8b3a2       # mission description, and every quiet label
CHALLENGE_TARGET_COLOR = 0xfff1d985          # a hoverable name inside the description
CHALLENGE_TIME_COLOR = 0xffffc700            # a live countdown, and only that

# The state word is quiet unless the challenge is live, in which case it takes the clock's
# colour so the pair reads as one thing.
CHALLENGE_STATE_COLOR = CHALLENGE_OBJECTIVE_COLOR
CHALLENGE_STATE_LIVE_COLOR = CHALLENGE_TIME_COLOR

# Easy / normal / hard. One hue family, walked from quiet to loud rather than green-yellow-red:
# three saturations of the same warm tone still rank at a glance without adding two more hues.
CHALLENGE_TIER_COLORS = [0xffd8c6a4, 0xffd3a86a, 0xffc67f52]
# Two plates, three brightnesses. The quiet plate is the resting state and the warm one marks
# the challenge actually running, so the eye finds it without reading anything. Finished keeps
# the quiet plate and falls back further; locked falls back further still, and the level
# requirement overlays the objective line.
CHALLENGE_NORMAL_DIM = (1.0, 1.0, 1.0, 1.0)
CHALLENGE_DONE_DIM = (0.7, 0.7, 0.7, 1.0)
CHALLENGE_LOCKED_DIM = (0.45, 0.45, 0.45, 1.0)

# A band's interior between two baked separators.
BAND_H = 19
# Gap between the title and the tier word sharing band 1.
TIER_GAP = 8

# Objective marquee, the same shape uiguild's contract cards use. The label is never chopped --
# an ellipsis cut mid-word breaks Arabic glyph joining -- so the whole sentence always stands and
# a clip mask decides what is visible. Hovering the band slides it until the tail has been read,
# then it stops; leaving the band puts it back.
OBJ_MARQUEE_DELAY = 0.35
OBJ_MARQUEE_SPEED_PX = 100.0

CHALLENGE_TIER_NAMES = [
	("CHALLENGE_TIER_EASY", "Easy"),
	("CHALLENGE_TIER_NORMAL", "Normal"),
	("CHALLENGE_TIER_HARD", "Hard"),
]

# RewardLen -> (locale key, english default, subject kind). The subject kind is derived from
# the mission type and never stored per challenge, so the pool data and the renderer cannot
# disagree. Two %s = amount then name; one %s = amount alone.
CHALLENGE_VERB_SPEC = [
	("REWARD_MISSION_KILL_MONSTER", "CHALLENGE_VERB_KILL_MONSTER", "Defeat %sx %s", "mob"),
	("REWARD_MISSION_KILL_STONE", "CHALLENGE_VERB_KILL_STONE", "Destroy %sx %s", "mob"),
	("REWARD_MISSION_KILL_BOSS", "CHALLENGE_VERB_KILL_BOSS", "Defeat %sx %s", "mob"),
	("REWARD_MISSION_FIRST_ITEM", "CHALLENGE_VERB_FIRST_ITEM", "Obtain %sx %s", "item"),
	("REWARD_MISSION_USE_ITEM", "CHALLENGE_VERB_USE_ITEM", "Use %sx %s", "item"),
	("REWARD_MISSION_SELL_ITEM", "CHALLENGE_VERB_SELL_ITEM", "Sell %sx %s", "item"),
	("REWARD_MISSION_BUY_ITEM", "CHALLENGE_VERB_BUY_ITEM", "Buy %sx %s", "item"),
	("REWARD_MISSION_ENCHANT_ITEM", "CHALLENGE_VERB_ENCHANT_ITEM", "Upgrade %sx %s", "item"),
	("REWARD_MISSION_FISHING", "CHALLENGE_VERB_FISHING", "Catch %s fish", "none"),
	("REWARD_MISSION_MINING", "CHALLENGE_VERB_MINING", "Mine %s ores", "none"),
	("REWARD_MISSION_ALCHEMY", "CHALLENGE_VERB_ALCHEMY", "Refine alchemy %s times", "none"),
	("REWARD_MISSION_DUNGEON", "CHALLENGE_VERB_DUNGEON", "Clear %sx %s", "dungeon"),
	("REWARD_MISSION_DUNGEON_SOLO", "CHALLENGE_VERB_DUNGEON_SOLO", "Clear %sx %s alone", "dungeon"),
	("REWARD_MISSION_LEVEL_UP", "CHALLENGE_VERB_LEVEL_UP", "Reach level %s", "none"),
	("REWARD_MISSION_LEVEL_UP_PET", "CHALLENGE_VERB_LEVEL_UP_PET", "Reach pet level %s", "none"),
	("REWARD_MISSION_SKILL_UPGRADE", "CHALLENGE_VERB_SKILL_UPGRADE", "Upgrade skills %s times", "none"),
	("REWARD_MISSION_BIOLOG", "CHALLENGE_VERB_BIOLOG", "Complete %s biolog missions", "none"),
	("REWARD_MISSION_SHOUT", "CHALLENGE_VERB_SHOUT", "Shout %s times", "none"),
	("REWARD_MISSION_PLAYTIME", "CHALLENGE_VERB_PLAYTIME", "Play for %s minutes", "none"),
	("REWARD_MISSION_OFFLINESHOP_SLOT", "CHALLENGE_VERB_OFFLINESHOP_SLOT", "Unlock %s offline shop slots", "none"),
	("REWARD_MISSION_INVENTORY_SLOT", "CHALLENGE_VERB_INVENTORY_SLOT", "Unlock %s inventory pages", "none"),
]
CHALLENGE_VERB_FALLBACK = ("CHALLENGE_VERB_GENERIC", "Reach %s", "none")

# A short noun for a target with no name of its own -- either its vnum is 0, which the server
# uses for "any of them", or the type never had a subject (fishing, mining, dungeons). The
# objective line splices it into the verb where the name would go; the HUD prints it on its own,
# next to its own counter.
CHALLENGE_SUBJECT_SPEC = [
	("REWARD_MISSION_KILL_MONSTER", "CHALLENGE_SUBJECT_MONSTER", "monsters"),
	("REWARD_MISSION_KILL_STONE", "CHALLENGE_SUBJECT_STONE", "Metin Stones"),
	("REWARD_MISSION_KILL_BOSS", "CHALLENGE_SUBJECT_BOSS", "bosses"),
	("REWARD_MISSION_FIRST_ITEM", "CHALLENGE_SUBJECT_ITEM", "items"),
	("REWARD_MISSION_USE_ITEM", "CHALLENGE_SUBJECT_ITEM", "items"),
	("REWARD_MISSION_SELL_ITEM", "CHALLENGE_SUBJECT_ITEM", "items"),
	("REWARD_MISSION_BUY_ITEM", "CHALLENGE_SUBJECT_ITEM", "items"),
	("REWARD_MISSION_ENCHANT_ITEM", "CHALLENGE_SUBJECT_ITEM", "items"),
	("REWARD_MISSION_DUNGEON", "CHALLENGE_SUBJECT_DUNGEON", "dungeons"),
	("REWARD_MISSION_DUNGEON_SOLO", "CHALLENGE_SUBJECT_DUNGEON_SOLO", "dungeons"),
	("REWARD_MISSION_FISHING", "CHALLENGE_SUBJECT_FISHING", "fish"),
	("REWARD_MISSION_MINING", "CHALLENGE_SUBJECT_MINING", "ores"),
]
CHALLENGE_SUBJECT_FALLBACK = ("CHALLENGE_SUBJECT_GENERIC", "targets")

def BuildChallengeVerbs():
	verbs = {}
	for (constName, localeKey, default, kind) in CHALLENGE_VERB_SPEC:
		missionType = getattr(player, constName, None)
		if missionType is not None:
			verbs[missionType] = (localeKey, default, kind)

	return verbs

def BuildChallengeSubjects():
	subjects = {}
	for (constName, localeKey, default) in CHALLENGE_SUBJECT_SPEC:
		missionType = getattr(player, constName, None)
		if missionType is not None:
			subjects[missionType] = (localeKey, default)

	return subjects

CHALLENGE_VERBS = BuildChallengeVerbs()
CHALLENGE_SUBJECTS = BuildChallengeSubjects()

def GetChallengeSubject(missionType):
	return LocaleText(*CHALLENGE_SUBJECTS.get(missionType, CHALLENGE_SUBJECT_FALLBACK))

def GetChallengeSubjectKind(missionType):
	return CHALLENGE_VERBS.get(missionType, CHALLENGE_VERB_FALLBACK)[2]

# A DUNGEON event's sub_value is the first argument to the quest's d.complete_dungeon call,
# which is *usually* the dungeon's bossVnum but not always: Demon Tower reports 1093 while its
# boss is 1095. Anything not in this map is looked up by bossVnum.
CHALLENGE_DUNGEON_ALIAS = { 1093 : 1095 }
challenge_dungeon_by_boss = {}

def GetChallengeDungeon(subValue):
	"""The dungeon_info row a DUNGEON sub_value refers to, or None if the client has none.

	Meley, Erebus and Akzdur are absent from dungeon_info.json and ghostberan_lair reports a
	runtime vnum, so a miss here is expected and has to read as plain text rather than a broken
	name -- see docs/WEEKLY_CHALLENGES_CONTENT.md section 7."""
	if not challenge_dungeon_by_boss:
		try:
			import uidungeoninfo
			uidungeoninfo.LoadDungeons()
			for dungeon in uidungeoninfo.dungeonsDict.values():
				if dungeon.get("bossVnum"):
					challenge_dungeon_by_boss[dungeon["bossVnum"]] = dungeon
		except:
			return None

	return challenge_dungeon_by_boss.get(CHALLENGE_DUNGEON_ALIAS.get(subValue, subValue))

def GetChallengeDungeonName(subValue):
	dungeon = GetChallengeDungeon(subValue)
	if not dungeon:
		return ""

	# The map name is the only localized dungeon name the client owns; the window that lists
	# dungeons uses the same one. It answers an index it does not know with MAP_NONE rather
	# than with nothing, and map 221 is one of those, so that answer has to be caught here or
	# the objective reads "Clear 3x Unkown".
	nameOf = getattr(localeinfo, "GetMiniMapZoneNameByIdx", None)
	if not nameOf:
		return ""

	name = nameOf(dungeon.get("mapIndex", 0))
	return "" if name == getattr(localeinfo, "MAP_NONE", None) else name

# The tooltip and the wiki both speak mob/item. A dungeon answers with its boss, which is what
# makes the hover render a model rather than nothing.
def GetChallengeLookup(kind, vnum):
	if kind != "dungeon":
		return (kind, vnum)

	dungeon = GetChallengeDungeon(vnum)
	if not dungeon:
		return (None, 0)

	return ("mob", dungeon.get("renderMonsterVnum") or dungeon.get("bossVnum", 0))

# The side button counts challenges with work on the current map, so a target has to say
# whether it is here. Kill targets answer from the wiki's spawn bake; mining answers from the
# ore veins in the same file; everything else (fishing, items, dungeons -- their bosses are
# quest-spawned and absent from the bake) is not location-bound and never lights the button.
CHALLENGE_KILL_TYPES = set(missionType for missionType in (
	getattr(player, "REWARD_MISSION_KILL_MONSTER", None),
	getattr(player, "REWARD_MISSION_KILL_STONE", None),
	getattr(player, "REWARD_MISSION_KILL_BOSS", None)) if missionType is not None)
CHALLENGE_MINING_TYPE = getattr(player, "REWARD_MISSION_MINING", None)
CHALLENGE_VEIN_VNUMS = tuple(range(20047, 20060)) + (30301,)
challenge_spawn_maps = {}

def GetChallengeSpawnMaps(vnum):
	maps = challenge_spawn_maps.get(vnum)
	if maps is None:
		try:
			import game_data
			maps = set(entry.get("map", "") for entry in game_data.mobSpawnDict.get(vnum, []))
		except:
			maps = set()
		challenge_spawn_maps[vnum] = maps

	return maps

def IsChallengeTargetHere(target, mapName):
	if target[3] >= target[2]:
		return False
	if target[0] in CHALLENGE_KILL_TYPES and target[1]:
		return mapName in GetChallengeSpawnMaps(target[1])
	if target[0] == CHALLENGE_MINING_TYPE:
		for vnum in CHALLENGE_VEIN_VNUMS:
			if mapName in GetChallengeSpawnMaps(vnum):
				return True

	return False

# (challenges still to do at all, challenges with work on the current map). The first drives
# whether the side button exists, the second its badge and tooltip.
def GetChallengeMapCounts():
	try:
		import background
		mapName = str(background.GetCurrentMapName())
	except:
		mapName = ""

	total = 0
	here = 0
	for data in challenge_board.values():
		if data["state"] not in (CHALLENGE_AVAILABLE, CHALLENGE_ONGOING):
			continue
		total += 1
		for target in data["targets"]:
			if mapName and IsChallengeTargetHere(target, mapName):
				here += 1
				break

	return (total, here)

def GetChallengeTargetName(missionType, vnum):
	kind = GetChallengeSubjectKind(missionType)
	if kind == "mob":
		return nonplayer.GetMonsterName(vnum)
	if kind == "item":
		return item.GetItemNameByVnum(vnum)
	if kind == "dungeon":
		return GetChallengeDungeonName(vnum)

	return ""

# "<type>-<vnum>-<need>-<have>.<...>" -- lists, not tuples, because ChallengeProg rewrites
# the have field in place.
def ParseChallengeTargets(field):
	targets = []
	if not field:
		return targets

	for entry in field.split("."):
		parts = entry.split("-")
		if len(parts) == 4:
			targets.append([int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])])

	return targets

# A target renders as pieces -- (text, kind, vnum) with kind None for the plain words --
# because the name needs to be its own widget to be hovered and clicked on its own. Where
# the name sits in the sentence comes from the locale string, not from us: Arabic may well
# put it first, so the verb is formatted with a marker and split on it.
NAME_MARK = "\x02"

def GetChallengeTargetPieces(target):
	(localeKey, default, kind) = CHALLENGE_VERBS.get(target[0], CHALLENGE_VERB_FALLBACK)
	amount = "%d/%d" % (target[3], target[2]) if target[3] > 0 else str(target[2])
	verb = LocaleText(localeKey, default)
	if kind == "none":
		return [(verb % amount, None, 0)]

	# vnum 0 is the server's "any of them". There is no name to show, and the client does not
	# answer an unknown vnum with an empty string -- it answers with whatever was selected last,
	# which is how a reward token's name ended up inside an objective. The subject noun goes
	# where the name would, as a plain piece: there is nothing to hover or click.
	if target[1] == 0:
		return [(verb % (amount, GetChallengeSubject(target[0])), None, 0)]

	# A dungeon the client has no row for (Meley, Erebus, ghostberan's runtime vnum) resolves to
	# nothing. It reads as the plain subject rather than as an empty gap with a hit region on it.
	name = GetChallengeTargetName(target[0], target[1])
	if not name:
		return [(verb % (amount, GetChallengeSubject(target[0])), None, 0)]

	pieces = []
	for (index, part) in enumerate((verb % (amount, NAME_MARK)).split(NAME_MARK)):
		if index:
			pieces.append((name, kind, target[1]))
		if part:
			pieces.append((part, None, 0))

	return pieces

# The HUD prints one short label per target and supplies its own "have / need", so it wants the
# subject alone rather than a sentence: the mob or item name where there is one, the subject noun
# where there is not.
def ComposeChallengeTarget(target):
	return GetChallengeTargetName(target[0], target[1]) or GetChallengeSubject(target[0])

def GetChallengeObjectivePieces(targets):
	pieces = []
	joiner = " %s " % LocaleText("CHALLENGE_AND", "and")
	for target in targets:
		if pieces:
			pieces.append((joiner, None, 0))

		pieces += GetChallengeTargetPieces(target)

	return pieces

def ServerNow():
	try:
		return int(app.GetGlobalTimeStamp())
	except:
		return 0

def GetChallengeRemaining(data):
	deadline = data.get("deadline", 0)
	return max(0, deadline - ServerNow()) if deadline else 0

def FormatChallengeClock(seconds):
	seconds = max(0, int(seconds))
	return "%02d:%02d:%02d" % (seconds // 3600, (seconds % 3600) // 60, seconds % 60)

def FormatChallengeDuration(seconds):
	return LocaleText("CHALLENGE_MINUTES", "%s Minutes") % max(1, int(seconds) // 60)

def GetChallengeTitle(data):
	return LocaleText(data["title_key"], "Challenge %d" % data["id"])

def GetRewardItemsForPlacement(rewardData, placementIdx):
	"""Get reward items for a specific placement (0=1st, 1=2nd, 2=3rd).
	Supports both old format (reward_items) and new per-placement format."""
	keys = ["reward_items_1st", "reward_items_2nd", "reward_items_3rd"]
	if rewardData.has_key(keys[placementIdx]):
		return rewardData[keys[placementIdx]]
	if rewardData.has_key("reward_items"):
		return rewardData["reward_items"]
	return []

# Repeated vnums collapse into one stack so three slots always suffice. Verified to reproduce
# the hand-written lists below exactly on all 48 of them, so the server feed changes nothing.
def MergeRewardPairs(rewardList):
	order = []
	counts = {}
	for vnum, count in rewardList:
		if not counts.has_key(vnum):
			order.append(vnum)
			counts[vnum] = 0
		counts[vnum] += count

	return [[vnum, counts[vnum]] for vnum in order]

def ParseRewardPairs(field):
	rewardList = []
	if not field:
		return rewardList

	for pair in field.split("."):
		vnumCount = pair.split("-")
		if len(vnumCount) == 2:
			rewardList.append([int(vnumCount[0]), int(vnumCount[1])])

	return MergeRewardPairs(rewardList)

def ParseVnumList(field):
	if not field:
		return []

	return [int(vnum) for vnum in field.split(".") if vnum]

def ParseWearGroups(field):
	groups = []
	if not field:
		return groups

	for group in field.split(":"):
		slotVnums = group.split("-")
		if len(slotVnums) == 2:
			groups.append((int(slotVnums[0]), ParseVnumList(slotVnums[1])))

	return groups

# localeinfo is wrapped (system.py LocaleInfoWrapper) and returns the string
# "Locale not found: KEY" instead of raising, so getattr's default never fires on its own.
def LocaleText(key, default):
	value = getattr(localeinfo, key, default)
	if not value or value.startswith("Locale not found"):
		return default

	return value

# "<name>;<epoch>;<guild>|<...>|<...>" -- spaces in a guild name travel as \x1f because the
# client's command dispatcher splits the line on whitespace.
def ParsePlacementFields(field):
	playerNames = ["", "", ""]
	playerTimes = ["", "", ""]
	playerGuilds = ["", "", ""]

	placements = field.split("|")
	for i in range(min(3, len(placements))):
		parts = placements[i].split(";")
		playerNames[i] = parts[0].replace("\x1f", " ") if len(parts) > 0 else ""
		playerTimes[i] = parts[1] if len(parts) > 1 else ""
		playerGuilds[i] = parts[2].replace("\x1f", " ") if len(parts) > 2 else ""

	return (playerNames, playerTimes, playerGuilds)

def FormatWinTime(epochText):
	if not epochText:
		return ""

	try:
		return datetime.datetime.fromtimestamp(int(epochText)).strftime("%Y-%m-%d %H:%M:%S")
	except (ValueError, TypeError):
		return ""

# Align-left puts the anchor on the far side of the glyph flow: LTR text grows right from it,
# Arabic grows left. So the same call right-anchors Arabic when x is the field's right edge --
# SetHorizontalAlignRight pushes the text off the row instead. See feedback_arabic_text_align.
def PlaceRowText(textLine, y, leftX = None, rightX = None):
	textLine.SetHorizontalAlignLeft()
	textLine.SetPosition(
		(TEXT_RIGHT if rightX is None else rightX) if localeinfo.IsARABIC() else (TEXT_X if leftX is None else leftX),
		y)

# The mirror of PlaceRowText: hugs the edge the language reads towards. Align-left anchors on the
# far side of the glyph flow, so an Arabic line occupies [x - width, x] and its anchor has to be
# pushed a full width inwards to sit against the left edge.
def PlaceRowTextTrailing(textLine, y, leftX = None, rightX = None):
	textLine.SetHorizontalAlignLeft()
	left = TEXT_X if leftX is None else leftX
	right = TEXT_RIGHT if rightX is None else rightX
	width = int(textLine.GetTextWidth())
	textLine.SetPosition(left + width if localeinfo.IsARABIC() else right - width, y)

def IsGlobalMissionFinished(rewardData):
	playerNames = rewardData["player_names"] if rewardData.has_key("player_names") else []
	if len(playerNames) < 3:
		return False

	return playerNames[0] != "" and playerNames[1] != "" and playerNames[2] != ""

def IsSoloMissionFinished(rewardData):
	maxValue = rewardData["max_value"] if rewardData.has_key("max_value") else 0
	value = rewardData["value"] if rewardData.has_key("value") else 0
	return maxValue > 0 and value >= maxValue

def GetPlacementName(placement):
	if placement < 1 or placement > 3:
		return ""

	keys = ["REWARD_PLACE_1", "REWARD_PLACE_2", "REWARD_PLACE_3"]
	return LocaleText(keys[placement - 1], MEDAL_LABELS[placement - 1])

# Server-fed by ChallengeBoard: {slot: {...}}. Empty until a board arrives, which is what
# keeps the personal tab on the legacy solo rows while ENABLE_WEEKLY_CHALLENGES is off --
# with the flag off the command simply never comes.
challenge_board = {}
# Set the first time a ChallengeBoard command arrives and never cleared. Two jobs: it tells
# an empty board apart from a server that has no weekly challenges at all (the legacy solo
# rows are the fallback for the second case only), and it is what makes it safe to send
# /challenge open -- an unknown command answers the player with a visible error line, so the
# client may only use it after the server has proved it speaks this protocol.
challenge_seen = [False]

# What each mission counts, fed by RewardTargets: {missionIdx: {"items": [vnum], "wear": [(slot, [vnum])]}}
global_reward_targets = {}

# Display only. The server sends target lists for FIRST_ITEM and WEAR_SET missions; every
# other kind carries nothing on the wire, so what its tooltip shows is described here.
# Keyed on (type, subValue) -- subValue None matches any -- so a mission that changes its
# number stops matching instead of quietly showing the old picture.
REWARD_TIP_SPEC = [
	("REWARD_MISSION_DUNGEON_SOLO", 6191, [("mob", [6191])], "REWARD_TIP_DUNGEON_SOLO"),
	("REWARD_MISSION_GUILD_DUNGEON", None, [("mob", [6791])], "REWARD_TIP_GUILD_DUNGEON"),
	("REWARD_MISSION_BIOLOG", 19, [("item", [31137])], "REWARD_TIP_BIOLOG"),
	("REWARD_MISSION_CUSTOM_SASH", 25, [("item", [85004])], "REWARD_TIP_SASH"),
	("REWARD_MISSION_ALCHEMY", 1, [("item", [115460, 125460, 135460, 145460, 155460, 165460])], "REWARD_TIP_ALCHEMY"),
	("REWARD_MISSION_USE_PENDENT", 1, [("item", [9620, 9850, 10080, 10310, 10540, 10770])], "REWARD_TIP_PENDENT"),
	("REWARD_MISSION_AVERAGE_BONUS", 55, [("item", [189, 3169, 1139, 2179, 5129, 199])], "REWARD_TIP_AVERAGE"),
	("REWARD_MISSION_PET_TYPE", 6, [("item", [55701])], "REWARD_TIP_PET"),
	("REWARD_MISSION_BUFFI", 105, [("item", [91110])], "REWARD_TIP_BUFFI"),
	("REWARD_MISSION_HORSE", 30, [("item", [71131])], "REWARD_TIP_HORSE"),
]

def BuildRewardTips():
	tips = {}
	for (constName, subValue, groups, captionKey) in REWARD_TIP_SPEC:
		missionType = getattr(player, constName, None)
		if missionType is not None:
			tips[(missionType, subValue)] = (groups, captionKey)

	return tips

REWARD_TIPS = BuildRewardTips()

def GetRewardTip(missionType, subValue):
	tip = REWARD_TIPS.get((missionType, subValue))
	return tip if tip else REWARD_TIPS.get((missionType, None))

# Server-fed: CHARACTER_MANAGER::SendGlobalRewardDefs pushes RewardDefs on window open and
# RewardDefs() below fills this in. The table itself lives in
# share/systems/config_systems/reward_global.json -- it is not duplicated here any more.
global_reward_info = {}

solo_reward_info = {
	0: {
		"type": player.REWARD_MISSION_KILL_STONE,
		"subValue": 0,
		"max_value": 50000,
		"level_difference": 15,
		"icon_name": "new_stone",
		"reward_items": [[60700, 10], [60702, 10], [39028, 2000], [25041, 1]]
	},
	1: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 0,
		"max_value": 2500,
		"level_difference": 0,
		"icon_name": "new_bosses",
		"reward_items": [[50513, 10], [51501, 30], [39113, 50], [51001, 250], [25041, 1], [72006, 3]]
	},
	2: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 694,
		"max_value": 75,
		"level_difference": 0,
		"icon_name": "orc",
		"reward_items": [[51501, 25], [38016, 30], [30182, 5], [25041, 1]]
	},
	3: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 1093,
		"max_value": 75,
		"level_difference": 0,
		"icon_name": "new_reaper",
		"reward_items": [[50288, 20], [51501, 30], [38016, 30], [30182, 5], [25041, 1]]
	},
	4: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 2092,
		"max_value": 75,
		"level_difference": 0,
		"icon_name": "new_barone",
		"reward_items": [[54701, 20], [51501, 30], [38016, 30], [30182, 5], [25041, 1]]
	},
	5: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 2598,
		"max_value": 75,
		"level_difference": 0,
		"icon_name": "new_cata",
		"reward_items": [[53586, 20], [51501, 30], [38016, 30], [30182, 5], [25041, 1]]
	},
	6: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 2493,
		"max_value": 100,
		"level_difference": 0,
		"icon_name": "new_beran",
		"reward_items": [[54700, 25], [51501, 40], [38016, 40], [30182, 6], [25041, 2]]
	},
	7: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 1095,
		"max_value": 100,
		"level_difference": 0,
		"icon_name": "new_reaper",
		"reward_items": [[53587, 25], [51501, 40], [38016, 40], [30182, 6], [25041, 2]]
	},
	8: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 5623,
		"max_value": 100,
		"level_difference": 0,
		"icon_name": "berandark",
		"reward_items": [[33064, 25], [51501, 40], [38016, 40], [30182, 6], [25041, 2]]
	},
	9: {
		"type": player.REWARD_MISSION_DUNGEON,
		"subValue": 0,
		"max_value": 500,
		"level_difference": 0,
		"icon_name": "new_dungeon",
		"reward_items": [[50288, 25], [54701, 25], [53586, 25], [54700, 25], [53587, 25], [53587, 25]]
	},
	10: {
		"type": player.REWARD_MISSION_SKILL_UPGRADE,
		"subValue": 1,
		"max_value": 1,
		"level_difference": 0,
		"icon_name": "new_skill",
		"reward_items": [[51501, 25], [39028, 2000]]
	},
	11: {
		"type": player.REWARD_MISSION_OFFLINESHOP_SLOT,
		"subValue": 1,
		"max_value": 40,
		"level_difference": 0,
		"icon_name": "new_offshop",
		"reward_items": [[51501, 50], [25041, 1], [71153, 1], [100700, 2], [72703, 1]]
	},
	12: {
		"type": player.REWARD_MISSION_ENCHANT_ITEM,
		"subValue": 71151,
		"max_value": 50000,
		"level_difference": 0,
		"icon_name": "new_enchant_low",
		"reward_items": [[39028, 500], [51501, 15], [27987, 50]]
	},
	13: {
		"type": player.REWARD_MISSION_ENCHANT_ITEM,
		"subValue": 71084,
		"max_value": 100000,
		"level_difference": 0,
		"icon_name": "new_enchant",
		"reward_items": [[39028, 2000], [51501, 25], [25041, 1]]
	},
	14: {
		"type": player.REWARD_MISSION_FISHING,
		"subValue": 1,
		"max_value": 1500,
		"level_difference": 0,
		"icon_name": "fishing",
		"reward_items": [[25041, 2], [51501, 50], [30182, 5], [72703, 1], [71153, 1], [100700, 2]]
	},
}

SCROLLBAR_HEIGHT = 337

def GetMissionName(pageIdx, type, subValue, levelDifference = 0):
	__localeText = {
		player.REWARD_MISSION_LEVEL_UP : localeinfo.REWARD_SYSTEM_MISSION_1_1,
		player.REWARD_MISSION_LEVEL_UP_PET : localeinfo.REWARD_SYSTEM_MISSION_2,
		player.REWARD_MISSION_INVENTORY_SLOT : localeinfo.REWARD_SYSTEM_MISSION_3,
		player.REWARD_MISSION_OFFLINESHOP_SLOT : localeinfo.REWARD_SYSTEM_MISSION_4,
		player.REWARD_MISSION_AVERAGE_BONUS : localeinfo.REWARD_SYSTEM_MISSION_5,
		player.REWARD_MISSION_BATTLEPASS : localeinfo.REWARD_SYSTEM_MISSION_6,
		player.REWARD_MISSION_CUSTOM_SASH : localeinfo.REWARD_SYSTEM_MISSION_7_1,
		player.REWARD_MISSION_BIOLOG : localeinfo.REWARD_SYSTEM_MISSION_8,
		player.REWARD_MISSION_COMPLETE_SKILL : localeinfo.REWARD_SYSTEM_MISSION_9,
		player.REWARD_MISSION_AVERAGE_BONUS_NEW : localeinfo.REWARD_SYSTEM_MISSION_27,
		player.REWARD_MISSION_USE_PENDENT : localeinfo.REWARD_SYSTEM_MISSION_28,
		player.REWARD_MISSION_ZODIAC_DUNGEON : localeinfo.REWARD_SYSTEM_MISSION_29,
		player.REWARD_MISSION_CUSTOM_SASH_ZODIAC : localeinfo.REWARD_SYSTEM_MISSION_7,
		player.REWARD_MISSION_WEAR_SET : localeinfo.REWARD_SYSTEM_MISSION_10,
		player.REWARD_MISSION_WEAR_SET2 : localeinfo.REWARD_SYSTEM_MISSION_11,
		player.REWARD_MISSION_WEAR_SET3 : localeinfo.REWARD_SYSTEM_MISSION_12,
		player.REWARD_MISSION_ITEM_SET : localeinfo.REWARD_SYSTEM_MISSION_13,
		player.REWARD_MISSION_SKILL_TREE : localeinfo.REWARD_SYSTEM_MISSION_14,
		player.REWARD_MISSION_GUILD_SKILLS : localeinfo.REWARD_SYSTEM_MISSION_15,
		player.REWARD_MISSION_WEAR_SET4 : localeinfo.REWARD_SYSTEM_MISSION_16,
		player.REWARD_MISSION_LEVEL_UP_PET2 : localeinfo.REWARD_SYSTEM_MISSION_17,
		player.REWARD_MISSION_FISHING : localeinfo.REWARD_SYSTEM_MISSION_18,
		player.REWARD_MISSION_SHOUT : localeinfo.REWARD_SYSTEM_MISSION_19,
		player.REWARD_MISSION_MINING : localeinfo.REWARD_SYSTEM_MISSION_20,
		player.REWARD_MISSION_ALCHEMY : localeinfo.REWARD_SYSTEM_MISSION_21,
	}
	for (constName, localeKey, default) in (
		("REWARD_MISSION_PET_TYPE", "REWARD_SYSTEM_MISSION_PET_TYPE", "Growth pet Type %s"),
		("REWARD_MISSION_BUFFI", "REWARD_SYSTEM_MISSION_BUFFI", "Companion level %s with 180 INT"),
		("REWARD_MISSION_HORSE", "REWARD_SYSTEM_MISSION_HORSE", "Horse level %s with every skill"),
		("REWARD_MISSION_GUILD_DUNGEON", "REWARD_SYSTEM_MISSION_GUILD_DUNGEON", "First guilds to clear the guild dungeon")):
		missionType = getattr(player, constName, None)
		if missionType is not None:
			__localeText[missionType] = LocaleText(localeKey, default)
	missionName = ""
	if not __localeText.has_key(type):
		if hasattr(player, "REWARD_MISSION_GUILD_LEVEL") and type == player.REWARD_MISSION_GUILD_LEVEL:
			missionName = getattr(localeinfo, "REWARD_SYSTEM_MISSION_GUILD_LEVEL", "First guilds to reach Guild Level %s") % str(subValue)
		elif type == player.REWARD_MISSION_PASSIVE_SKILL_COMPLETE:
			missionName = localeinfo.REWARD_SYSTEM_NAME_1 % skill.GetSkillName(subValue)
		elif type == player.REWARD_MISSION_SKILL_UPGRADE:
			skillGradeName = "P"
			if subValue >= 50:
				skillGradeName = localeinfo.REWARD_SYSTEM_NAME_2
			elif subValue >= 40:
				skillGradeName = localeinfo.REWARD_SYSTEM_NAME_3
			elif subValue >= 30:
				skillGradeName = localeinfo.REWARD_SYSTEM_NAME_4
			elif subValue >= 20:
				skillGradeName = localeinfo.REWARD_SYSTEM_NAME_5
			missionName = localeinfo.REWARD_SYSTEM_NAME_6 % skillGradeName
		elif type == player.REWARD_MISSION_FIRST_ITEM:
			if subValue == 0:
				missionName = localeinfo.REWARD_SYSTEM_NAME_7
			else:
				if subValue == 509 or subValue == 19299 or subValue == 12059:
					item.SelectItem(subValue)
					missionName = localeinfo.REWARD_SYSTEM_NAME_30 % item.GetItemName()
				elif subValue == 23059:
					missionName = localeinfo.REWARD_SYSTEM_NAME_30_1
				elif subValue == 81009:
					missionName = localeinfo.REWARD_SYSTEM_NAME_30_2
				elif subValue == 21225:
					missionName = localeinfo.REWARD_SYSTEM_NAME_30_3
				elif subValue == 335:
					missionName = localeinfo.REWARD_SYSTEM_NAME_30_4
				elif subValue == 279:
					missionName = localeinfo.REWARD_SYSTEM_NAME_30_5
				elif subValue == 5623:
					missionName = localeinfo.REWARD_SYSTEM_NAME_30_6
				elif subValue == 20769:
					missionName = localeinfo.REWARD_SYSTEM_NAME_30_7
				elif subValue == 12699:
					missionName = localeinfo.REWARD_SYSTEM_NAME_30_8
				
				else:
					item.SelectItem(subValue)
					missionName = localeinfo.REWARD_SYSTEM_NAME_8 % item.GetItemName()

		elif type == player.REWARD_MISSION_KILL_BOSS:
			if subValue == 0:
				missionName = localeinfo.REWARD_SYSTEM_NAME_9
			else:
				missionName = localeinfo.REWARD_SYSTEM_NAME_10 % nonplayer.GetMonsterName(subValue)
		elif type == player.REWARD_MISSION_KILL_STONE:
			if subValue == 0:
				missionName = localeinfo.REWARD_SYSTEM_NAME_11
			else:
				missionName = localeinfo.REWARD_SYSTEM_NAME_12 % nonplayer.GetMonsterName(subValue)
		elif type == player.REWARD_MISSION_KILL_MONSTER:
			if subValue == 0:
				missionName = localeinfo.REWARD_SYSTEM_NAME_13
			else:
				missionName = localeinfo.REWARD_SYSTEM_NAME_14 % nonplayer.GetMonsterName(subValue)
		elif type == player.REWARD_MISSION_DUNGEON:
			if subValue == 0:
				missionName = localeinfo.REWARD_SYSTEM_NAME_15
			else:
				__dungeonNames = {
					6118 : localeinfo.MAP_N_FLAME_DRAGON, #meley
					3962 : localeinfo.MAP_DEFENSE_WAVE, #hydra
					6192 : localeinfo.REWARD_SYSTEM_GLOBAL_JOT, #jotun
					6790 : localeinfo.REWARD_SYSTEM_GLOBAL_ALASTOR, #ALASTOR hard
					6856 : localeinfo.REWARD_SYSTEM_GLOBAL_SNAKE #SNAKE
				}
				missionName = localeinfo.REWARD_SYSTEM_NAME_16 % (__dungeonNames[subValue] if __dungeonNames.has_key(subValue) else "Unknown")

		elif type == player.REWARD_MISSION_DUNGEON_SOLO:
			if subValue == 0:
				missionName = localeinfo.REWARD_SYSTEM_NAME_15_2
			else:
				__dungeonNames = {
					6118 : localeinfo.MAP_N_FLAME_DRAGON, #meley
					3962 : localeinfo.MAP_DEFENSE_WAVE, #hydra
					6192 : localeinfo.REWARD_SYSTEM_GLOBAL_JOT, #jotun
					6790 : localeinfo.REWARD_SYSTEM_GLOBAL_ALASTOR, #ALASTOR hard
					6856 : localeinfo.REWARD_SYSTEM_GLOBAL_SNAKE, #SNAKE
					5623 : localeinfo.REWARD_SYSTEM_GLOBAL_DARK, #SNAKE
					6191 : LocaleText("GEARSET_DUN_NEMERE", "Nemere's Watchtower")
				}
				missionName = localeinfo.REWARD_SYSTEM_NAME_16_2 % (__dungeonNames[subValue] if __dungeonNames.has_key(subValue) else "Unknown")


		elif type == player.REWARD_MISSION_USE_ITEM:
			if subValue == 0:
				missionName = localeinfo.REWARD_SYSTEM_NAME_17
			else:
				item.SelectItem(subValue)
				missionName = localeinfo.REWARD_SYSTEM_NAME_18 % item.GetItemName()
		elif type == player.REWARD_MISSION_ENCHANT_ITEM:
			if subValue == 0:
				missionName = localeinfo.REWARD_SYSTEM_NAME_25
			else:
				item.SelectItem(subValue)
				missionName = localeinfo.REWARD_SYSTEM_NAME_18 % item.GetItemName()
		elif type == player.REWARD_MISSION_SELL_ITEM:
			if subValue == 0:
				missionName = localeinfo.REWARD_SYSTEM_NAME_26
			else:
				item.SelectItem(subValue)
				missionName = localeinfo.REWARD_SYSTEM_NAME_20 % item.GetItemName()
		elif type == player.REWARD_MISSION_BUY_ITEM:
			if subValue == 0:
				missionName = localeinfo.REWARD_SYSTEM_NAME_21
			else:
				item.SelectItem(subValue)
				missionName = localeinfo.REWARD_SYSTEM_NAME_22 % item.GetItemName()
		elif type == player.REWARD_MISSION_PLAYTIME:
			missionName = localeinfo.REWARD_SYSTEM_NAME_23 % localeinfo.SecondToDHM(subValue)
	else:
		try:
			missionName = __localeText[type] % subValue
		except:
			missionName = __localeText[type]
	if levelDifference != 0:
		missionName += " " + (localeinfo.REWARD_SYSTEM_NAME_24 % levelDifference)
	return missionName

class RewardWindow(ui.Window):

	class RewardItemGlobal(ui.ImageBox):
		def Destroy(self):
			self.__children = {}
		def GetRewardIndex(self):
			return self.__children["rewardIndex"] if self.__children.has_key("rewardIndex") else 0
		def __init__(self, pageIdx, rewardIndex, rewardData):
			ui.ImageBox.__init__(self)
			self.SetPosition(10,1)
			self.LoadReward(pageIdx, rewardIndex, rewardData)

		def LoadReward(self, pageIdx, rewardIndex, rewardData):
			allFilled = IsGlobalMissionFinished(rewardData)
			self.LoadImage(IMG_CHALLENGE_DIR + ("challenges_finished.png" if allFilled else "challenges_normal.png"))
			self.Destroy()
			self.__children["rewardIndex"] = rewardIndex
			self.__children["selectedPlacement"] = 0
			self.__children["playerNames"] = rewardData["player_names"] if rewardData.has_key("player_names") else ["", "", ""]
			self.__children["playerTimes"] = rewardData["player_times"] if rewardData.has_key("player_times") else ["", "", ""]
			self.__children["playerGuilds"] = rewardData["player_guilds"] if rewardData.has_key("player_guilds") else ["", "", ""]

			rewardName = CreateWindow(ui.TextLine(), self, (TEXT_X, BAND_TOP[0] + 3), GetMissionName(pageIdx, rewardData["type"], rewardData["subValue"]))
			rewardName.SetPackedFontColor(0xffdfe6e9)
			PlaceRowText(rewardName, BAND_TOP[0] + 3)
			self.__children["rewardName"] = rewardName

			# A TextLine is not pickable, so band 1 gets an invisible hit region over it.
			titleHover = ui.Window()
			titleHover.SetParent(self)
			titleHover.SetPosition(TEXT_X, BAND_TOP[0])
			titleHover.SetSize(TEXT_W, BAND_TOP[1] - BAND_TOP[0] - 4)
			titleHover.SetOverInEvent(ui.__mem_func__(self.OnTitleOverIn))
			titleHover.SetOverOutEvent(ui.__mem_func__(self.OnTitleOverOut))
			titleHover.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.OnTitleClick))
			titleHover.Show()
			self.__children["titleHover"] = titleHover

			# Band 2 pages through the three placements; band 3 is reserved for the win timestamp,
			# which the server does not record yet.
			prevBtn = ui.Button()
			prevBtn.SetParent(self)
			prevBtn.SetPosition(PAGER_PREV_X, BAND_TOP[1] + 5)
			prevBtn.SetUpVisual(IMG_CHALLENGE_DIR + "arrow-left.png")
			prevBtn.SetDownVisual(IMG_CHALLENGE_DIR + "arrow-left.png")
			prevBtn.SetOverVisual(IMG_CHALLENGE_DIR + "arrow-left.png")
			prevBtn.SetEvent(ui.__mem_func__(self.OnPrevPlacement))
			prevBtn.Show()
			self.__children["prevBtn"] = prevBtn

			nextBtn = ui.Button()
			nextBtn.SetParent(self)
			nextBtn.SetPosition(PAGER_NEXT_X, BAND_TOP[1] + 5)
			nextBtn.SetUpVisual(IMG_CHALLENGE_DIR + "arrow-right.png")
			nextBtn.SetDownVisual(IMG_CHALLENGE_DIR + "arrow-right.png")
			nextBtn.SetOverVisual(IMG_CHALLENGE_DIR + "arrow-right.png")
			nextBtn.SetEvent(ui.__mem_func__(self.OnNextPlacement))
			nextBtn.Show()
			self.__children["nextBtn"] = nextBtn

			trophyIcon = CreateWindow(ui.ImageBox(), self, (TROPHY_X, BAND_TOP[1] + 2), IMG_CHALLENGE_DIR + TROPHY_ICONS[0])
			self.__children["trophyIcon"] = trophyIcon

			winnerName = CreateWindow(ui.TextLine(), self, (TEXT_X, BAND_TOP[1] + 3), "")
			PlaceRowText(winnerName, BAND_TOP[1] + 3, TEXT_X, WINNER_NAME_RIGHT)
			self.__children["winnerName"] = winnerName

			# Band 3 carries the win time and, when the winner had one, their guild -- one text
			# line rather than two, so it needs a single anchor in either reading direction.
			winInfo = CreateWindow(ui.TextLine(), self, (TEXT_X, BAND_TOP[2] + 3), "")
			winInfo.SetPackedFontColor(0xff9aa5ab)
			PlaceRowText(winInfo, BAND_TOP[2] + 3)
			self.__children["winInfo"] = winInfo

			self.RefreshPlacement(rewardData, 0)

		def SetRewardPlayers(self, playerNames, playerTimes = None, playerGuilds = None):
			self.__children["playerNames"] = playerNames
			if playerTimes is not None:
				self.__children["playerTimes"] = playerTimes
			if playerGuilds is not None:
				self.__children["playerGuilds"] = playerGuilds

			# A win can land while the window is open, so the finished art is re-evaluated here
			# too, not only at load time.
			if IsGlobalMissionFinished({"player_names" : playerNames}):
				self.LoadImage(IMG_CHALLENGE_DIR + "challenges_finished.png")

			rewardData = global_reward_info.get(self.__children["rewardIndex"])
			if rewardData:
				self.RefreshPlacement(rewardData, self.__children.get("selectedPlacement", 0))

		# One placement at a time -- the pager arrows move through 1st/2nd/3rd, and the trophy,
		# the winner's name and the reward slots all follow the same index.
		def RefreshPlacement(self, rewardData, placementIdx):
			self.__children["selectedPlacement"] = placementIdx

			playerNames = self.__children.get("playerNames", ["", "", ""])
			displayName = playerNames[placementIdx] if placementIdx < len(playerNames) else ""
			if len(displayName) > MAX_NAME_DISPLAY:
				displayName = displayName[:MAX_NAME_DISPLAY] + ".."

			self.__children["trophyIcon"].LoadImage(IMG_CHALLENGE_DIR + TROPHY_ICONS[placementIdx])
			self.__children["winnerName"].SetText(displayName)
			self.__children["winnerName"].SetPackedFontColor(MEDAL_COLORS[placementIdx])

			playerTimes = self.__children.get("playerTimes", ["", "", ""])
			playerGuilds = self.__children.get("playerGuilds", ["", "", ""])
			winTime = FormatWinTime(playerTimes[placementIdx] if placementIdx < len(playerTimes) else "")
			winGuild = playerGuilds[placementIdx] if placementIdx < len(playerGuilds) else ""
			self.__children["winInfo"].SetText("%s  |  %s" % (winGuild, winTime) if winGuild and winTime else (winGuild or winTime))

			self.RefreshRewardItems(rewardData, placementIdx)

		def RefreshRewardItems(self, rewardData, placementIdx):
			rewardItemsList = GetRewardItemsForPlacement(rewardData, placementIdx)

			grid = Grid(3,1)
			grid.reset()

			# The 38x38 frames are baked into the row art at x 7/50/93, so no slot base is drawn
			# on top; a 32x32 icon centres in a 38px frame at +3, giving a 43px step.
			if self.__children.has_key("rewardItems"):
				rewardItems = self.__children["rewardItems"]
				rewardItems.ClearAllSlot()
				rewardItems.ArrangeSlot(0, 3, 1, 32, 32, SLOT_X[1] - SLOT_X[0] - 32, 0)
			else:
				rewardItems = CreateWindow(ui.GridSlotWindow(), self, (SLOT_X[0] + SLOT_ICON_OFFSET, SLOT_Y + SLOT_ICON_OFFSET))
				rewardItems.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
				rewardItems.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
				rewardItems.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
				rewardItems.SetUnselectItemSlotEvent(ui.__mem_func__(self.SearchInWiki))
				rewardItems.SAFE_SetButtonEvent("LEFT", "EXIST", self.RenderTarget)
				rewardItems.ArrangeSlot(0, 3, 1, 32, 32, SLOT_X[1] - SLOT_X[0] - 32, 0)
				self.__children["rewardItems"] = rewardItems

			for rewardItem in rewardItemsList:
				(itemVnum,itemCount) = (rewardItem[0],rewardItem[1])
				item.SelectItem(itemVnum)
				(width,height) = item.GetItemSize()
				pos = grid.find_blank(width, height)
				grid.put(pos, width, height)
				rewardItems.SetItemSlot(pos, itemVnum, itemCount)
			rewardItems.RefreshSlot()

		# A wear requirement is every slot; an item list is any one of them. The tooltip
		# caption has to say which, or a full-set mission reads as a pick-one.
		def IsAllOfTargets(self):
			targets = global_reward_targets.get(self.__children["rewardIndex"])
			return bool(targets) and bool(targets["wear"]) and not targets["items"]

		def GetRewardTip(self):
			rewardData = global_reward_info.get(self.__children["rewardIndex"])
			if not rewardData:
				return None

			return GetRewardTip(rewardData["type"], rewardData["subValue"])

		# The wire wins when it has something; the spec only fills the silence.
		def GetTargetCaptionKey(self):
			targets = global_reward_targets.get(self.__children["rewardIndex"])
			if not targets or not (targets["items"] or targets["wear"]):
				tip = self.GetRewardTip()
				return tip[1] if tip else ""

			return "REWARD_TARGETS_CAPTION_ALL" if self.IsAllOfTargets() else ""

		def GetTargetGroups(self):
			targets = global_reward_targets.get(self.__children["rewardIndex"])
			if not targets or not (targets["items"] or targets["wear"]):
				tip = self.GetRewardTip()
				return tip[0] if tip else []

			groups = []
			if targets["items"]:
				groups.append(("item", targets["items"]))

			for (slot, vnums) in targets["wear"]:
				if vnums:
					groups.append(("item", vnums))

			return groups

		def OnTitleOverIn(self):
			groups = self.GetTargetGroups()
			if not groups:
				return

			rewardData = global_reward_info.get(self.__children["rewardIndex"])
			if not rewardData:
				return

			toolTip = uichallengetooltip.GetToolTip()
			toolTip.SetTargets(GetMissionName(0, rewardData["type"], rewardData["subValue"]), groups,
				self.GetTargetCaptionKey())
			toolTip.ShowNearMouse()

		def OnTitleOverOut(self):
			uichallengetooltip.HideToolTip()

		# Click opens the wiki page of the mission's first target, mirroring the reward slots.
		def OnTitleClick(self):
			groups = self.GetTargetGroups()
			if not groups:
				return

			(kind, vnums) = groups[0]
			if kind != "item" or not vnums:
				return

			import wiki
			wiki.GetBaseClass().OpenSpecialWikiPage(vnums[0], 1 if item.GetItemTypeByVnum(vnums[0]) == item.ITEM_TYPE_GIFTBOX else 0)

		def OnPrevPlacement(self):
			current = self.__children.get("selectedPlacement", 0)
			rewardData = global_reward_info.get(self.__children["rewardIndex"])
			if rewardData:
				self.RefreshPlacement(rewardData, (current - 1) % 3)

		def OnNextPlacement(self):
			current = self.__children.get("selectedPlacement", 0)
			rewardData = global_reward_info.get(self.__children["rewardIndex"])
			if rewardData:
				self.RefreshPlacement(rewardData, (current + 1) % 3)

		def OverInItem(self, index):
			rewardIndex = self.__children["rewardIndex"]
			global global_reward_info
			rewardData = global_reward_info[rewardIndex] if global_reward_info.has_key(rewardIndex) else None
			if not rewardData:
				return

			placementIdx = self.__children.get("selectedPlacement", 0)
			rewardItemsList = GetRewardItemsForPlacement(rewardData, placementIdx)
			if index >= len(rewardItemsList):
				return

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.tooltipItem:
				interfaceHandler.tooltipItem.SetItemToolTip(rewardItemsList[index][0])
				interfaceHandler.tooltipItem.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_WIKI_HOVER)
				interfaceHandler.tooltipItem.DeclareShortcut(("key_alt", "key_rclick"), localeinfo.TOOLTIP_QUICKSEARCH_OFFLINESHOP)

		def OverOutItem(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.tooltipItem:
				interfaceHandler.tooltipItem.HideToolTip()

		def SearchInWiki(self, index):
			rewardIndex = self.__children["rewardIndex"]
			global global_reward_info
			rewardData = global_reward_info[rewardIndex] if global_reward_info.has_key(rewardIndex) else None

			placementIdx = self.__children.get("selectedPlacement", 0)
			rewardItemsList = GetRewardItemsForPlacement(rewardData, placementIdx)
			if index >= len(rewardItemsList):
				return
			itemVnum = rewardItemsList[index][0]
			isBox = 1 if item.GetItemTypeByVnum(itemVnum) == item.ITEM_TYPE_GIFTBOX else 0
			if app.IsPressed(app.DIK_LSHIFT):
				import wiki
				wiki.GetBaseClass().OpenSpecialWikiPage(itemVnum,isBox)

			if app.USE_OFFLINESHOP and\
				not uiofflineshop_ae.IsBuildingShop() and\
				(app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT)):
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler:
					wndShopOffline = interfaceHandler.wndShopOffline
					if wndShopOffline:
						wndSearchShop = wndShopOffline.wndSearchShop
						if wndSearchShop:
							wndSearchShop.SearchByName(item.GetItemNameByVnum(itemVnum))

		def RenderTarget(self, index):
			rewardIndex = self.__children["rewardIndex"]
			global global_reward_info
			rewardData = global_reward_info[rewardIndex] if global_reward_info.has_key(rewardIndex) else None

			placementIdx = self.__children.get("selectedPlacement", 0)
			rewardItemsList = GetRewardItemsForPlacement(rewardData, placementIdx)
			if index >= len(rewardItemsList):
				return
			itemVnum = rewardItemsList[index][0]

			if app.IsPressed(app.DIK_LSHIFT) and uiRenderTarget.IsCanShowItems(itemVnum):
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler:
					interfaceHandler.OpenRenderTargetWindow(0,itemVnum)

	class RewardItemChallenge(ui.ImageBox):
		def Destroy(self):
			self.__children = {}

		def GetRewardIndex(self):
			return self.__children["slot"] if self.__children.has_key("slot") else 0

		def __init__(self, pageIdx, slot, data):
			ui.ImageBox.__init__(self)
			self.LoadReward(pageIdx, slot, data)

		def LoadReward(self, pageIdx, slot, data):
			# The plate is left to Refresh at the end of this method -- Destroy() below clears the
			# state it is guarded on, so applying it here would only load the same image twice.
			self.Destroy()
			self.__children["slot"] = slot

			tierIdx = data["tier"] if data["tier"] < len(CHALLENGE_TIER_COLORS) else 0

			title = CreateWindow(ui.TextLine(), self, (TEXT_X, BAND_TOP[0] + 3), GetChallengeTitle(data))
			title.SetPackedFontColor(CHALLENGE_TITLE_COLOR)
			PlaceRowText(title, BAND_TOP[0] + 3)
			self.__children["title"] = title

			# The tier used to be nothing but the title's colour, which is unreadable if you do not
			# already know the code. It gets the far end of band 1, in the same colour.
			tier = CreateWindow(ui.TextLine(), self, (TEXT_X, BAND_TOP[0] + 3), LocaleText(*CHALLENGE_TIER_NAMES[tierIdx]))
			tier.SetPackedFontColor(CHALLENGE_TIER_COLORS[tierIdx])
			PlaceRowTextTrailing(tier, BAND_TOP[0] + 3)
			self.__children["tier"] = tier

			# Whatever is left of band 1 belongs to the title. It does not marquee -- a title is
			# authored short -- but it is clipped so it can never run under the tier word.
			budget = TEXT_W - int(tier.GetTextWidth()) - TIER_GAP
			self.__children["titleOver"] = int(title.GetTextWidth()) > budget
			self.__children["titleClip"] = (TEXT_RIGHT - budget, TEXT_RIGHT) if localeinfo.IsARABIC() \
				else (TEXT_X, TEXT_X + budget)

			# The objective line is rebuilt from pieces on every refresh, so all it needs up front
			# is somewhere to hold them and an off-screen line to measure with.
			self.__children["objectiveLines"] = []
			self.__children["objectiveHovers"] = []

			probe = ui.TextLine()
			probe.SetParent(self)
			probe.AddFlag("not_pick")
			probe.Hide()
			self.__children["probe"] = probe

			# Band 3 reads state-then-clock: the state word leads, the time trails. Available and
			# Locked had no word at all before, and Ongoing lived only on a disabled button.
			stateLine = CreateWindow(ui.TextLine(), self, (TEXT_X, BAND_TOP[2] + 3), "")
			PlaceRowText(stateLine, BAND_TOP[2] + 3)
			self.__children["stateLine"] = stateLine

			timeLine = CreateWindow(ui.TextLine(), self, (TEXT_X, BAND_TOP[2] + 3), "")
			PlaceRowTextTrailing(timeLine, BAND_TOP[2] + 3)
			self.__children["timeLine"] = timeLine

			activate = ui.Button()
			activate.SetParent(self)
			activate.SetUpVisual(IMG_CHALLENGE_DIR + "btn_activate_norm.png")
			activate.SetOverVisual(IMG_CHALLENGE_DIR + "btn_activate_hover.png")
			activate.SetDownVisual(IMG_CHALLENGE_DIR + "btn_activate_down.png")
			activate.SetPosition(ACTIVATE_X, ACTIVATE_Y)
			activate.SAFE_SetEvent(self.OnActivate)
			self.__children["activate"] = activate

			self.__BuildRewardSlots(data["rewards"])
			self.Refresh(data)

		# Called on every state change, not only at build: a run that expires locally flips back to
		# Available without the board being rebuilt, and the plate has to follow it.
		def ApplyRowSkin(self, state):
			if state == self.__children.get("skinState"):
				return

			self.__children["skinState"] = state
			self.LoadImage(IMG_CHALLENGE_DIR + (PERSONAL_ROW_NORMAL if state == CHALLENGE_ONGOING else PERSONAL_ROW_DONE))

			if state == CHALLENGE_LOCKED:
				dim = CHALLENGE_LOCKED_DIM
			elif state == CHALLENGE_COMPLETED:
				dim = CHALLENGE_DONE_DIM
			else:
				dim = CHALLENGE_NORMAL_DIM

			self.SetDiffuseColor(*dim)

		# 1 to 3 slots, centred in the empty reward panel. The frames are plain siblings created
		# before the GridSlotWindow: a SlotWindow's own children paint over its item icons, so an
		# underlay has to be an earlier sibling.
		def __BuildRewardSlots(self, rewards):
			rewards = rewards[:MAX_CHALLENGE_REWARDS]
			self.__children["rewards"] = rewards
			if not rewards:
				return

			count = len(rewards)
			step = PERSONAL_SLOT_SIZE + PERSONAL_SLOT_GAP
			originX = PERSONAL_PANEL_X + (PERSONAL_PANEL_W - (count * PERSONAL_SLOT_SIZE + (count - 1) * PERSONAL_SLOT_GAP)) // 2

			self.__children["slotBases"] = [
				CreateWindow(ui.ImageBox(), self, (originX + i * step, PERSONAL_SLOT_Y), IMG_CHALLENGE_DIR + PERSONAL_SLOT_IMAGE)
				for i in range(count)]

			rewardItems = CreateWindow(ui.GridSlotWindow(), self, (originX, PERSONAL_SLOT_Y))
			rewardItems.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
			rewardItems.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
			rewardItems.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			rewardItems.SetUnselectItemSlotEvent(ui.__mem_func__(self.SearchInWiki))
			rewardItems.ArrangeSlot(0, count, 1, PERSONAL_SLOT_SIZE, PERSONAL_SLOT_SIZE, PERSONAL_SLOT_GAP, 0)
			for i in range(count):
				rewardItems.SetItemSlot(i, rewards[i][0], rewards[i][1])
			rewardItems.RefreshSlot()
			self.__children["rewardItems"] = rewardItems

		def Refresh(self, data):
			self.__children["data"] = data

			if data["state"] == CHALLENGE_LOCKED:
				pieces = [(LocaleText("CHALLENGE_UNLOCKS_AT", "Unlocks at Level %s") % data["level_min"], None, 0)]
				color = CHALLENGE_OBJECTIVE_COLOR
			else:
				pieces = self.__ObjectivePieces(data["targets"])
				color = CHALLENGE_OBJECTIVE_COLOR

			# Tab switches and state changes re-run this with an unchanged sentence; skipping the
			# teardown then keeps the hit regions alive under the cursor.
			if (pieces, color) != self.__children.get("objectiveShape"):
				self.__children["objectiveShape"] = (pieces, color)
				self.__BuildObjective(pieces, color)

			self.ApplyRowSkin(data["state"])
			self.__RefreshButton(data)
			self.Tick()

		# >>> OBJ-COLLAPSE BEGIN -- replaced by the hover marquee (disabled)
		# A sentence wider than the 263px field used to collapse to its first target plus a count,
		# which meant a two-target challenge only ever showed one of them. The field now clips and
		# the line slides on hover instead, so nothing is dropped. Kept in case the marquee is ever
		# pulled -- docs/WEEKLY_CHALLENGES.md, Phase 3 UI pass.
		# def __Measure(self, pieces):
		# 	probe = self.__children["probe"]
		# 	total = 0
		# 	for (text, kind, vnum) in pieces:
		# 		probe.SetText(text)
		# 		total += int(probe.GetTextWidth())
		#
		# 	return total
		#
		# def __ObjectivePieces(self, targets):
		# 	pieces = GetChallengeObjectivePieces(targets)
		# 	if len(targets) < 2 or self.__Measure(pieces) <= TEXT_W:
		# 		return pieces
		#
		# 	return GetChallengeTargetPieces(targets[0]) + [
		# 		(" " + (LocaleText("CHALLENGE_MORE_TARGETS", "+%s") % (len(targets) - 1)), None, 0)]
		# <<< OBJ-COLLAPSE END

		def __ObjectivePieces(self, targets):
			return GetChallengeObjectivePieces(targets)

		# One TextLine per piece, laid out by accumulated width, with an invisible hit region over
		# each name -- a TextLine is not pickable, and one region for the whole line could only ever
		# act on one arbitrary target. Align-left anchors on the far side of the glyph flow, so an
		# Arabic piece occupies [x - width, x] and the cursor walks the field right to left.
		def __BuildObjective(self, pieces, color):
			# The regions about to be dropped may be the one under the cursor, and a destroyed
			# window never fires OverOut -- its tooltip would sit there until the next hover.
			if self.__children.get("objectiveHovers"):
				uichallengetooltip.HideToolTip()

			self.__children["objectiveLines"] = []
			self.__children["objectiveHovers"] = []
			self.__children["objectivePieces"] = []
			self.__children["objectiveOffset"] = 0.0
			self.__children["objectiveDone"] = False
			self.__children["objectiveSince"] = 0.0
			self.__children["clipStamp"] = None
			isArabic = localeinfo.IsARABIC()
			built = []
			total = 0

			for (text, kind, vnum) in pieces:
				textLine = ui.TextLine()
				textLine.SetParent(self)
				textLine.SetHorizontalAlignLeft()
				textLine.SetText(text)
				textLine.SetPackedFontColor(CHALLENGE_TARGET_COLOR if kind else color)
				textLine.Show()
				width = int(textLine.GetTextWidth())
				built.append((textLine, kind, vnum, width))
				total += width

			# Everything past the field edge is reachable by hovering the band, so the sentence is
			# never shortened. travel is how far it has to slide for the tail to arrive.
			self.__children["objectiveOver"] = total > TEXT_W
			self.__children["objectiveTravel"] = max(0, total - TEXT_W)

			x = TEXT_RIGHT if isArabic else TEXT_X
			for (textLine, kind, vnum, width) in built:
				textLine.SetPosition(x, BAND_TOP[1] + 3)
				left = x - width if isArabic else x
				self.__children["objectiveLines"].append(textLine)

				hover = None
				if kind:
					hover = ui.Window()
					hover.SetParent(self)
					hover.SetPosition(left, BAND_TOP[1])
					hover.SetSize(width, BAND_H)
					hover.SetOverInEvent(ui.__mem_func__(self.OnTargetOverIn), kind, vnum)
					hover.SetOverOutEvent(ui.__mem_func__(self.OnTargetOverOut))
					hover.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.OnTargetClick), kind, vnum)
					hover.Show()
					self.__children["objectiveHovers"].append(hover)

				self.__children["objectivePieces"].append(
					{"line" : textLine, "hover" : hover, "anchorX" : x, "width" : width})

				x += -width if isArabic else width

			self.ApplyClips(0.0)

		# The clip rects are screen-space and the row both scrolls inside the list and rides a
		# draggable window, so they are recomputed every frame rather than cached.
		def ApplyClips(self, offset):
			(rowX, rowY) = self.GetGlobalPosition()

			# Everything below is screen-space arithmetic that only changes when the row moves or
			# the marquee does. Standing still is the common case and costs nothing.
			stamp = (rowX, rowY, offset)
			if stamp == self.__children.get("clipStamp"):
				return

			self.__children["clipStamp"] = stamp

			if self.__children.get("titleOver"):
				(clipL, clipR) = self.__children["titleClip"]
				top = int(rowY + BAND_TOP[0])
				self.__children["title"].SetClippingMaskRect(
					int(rowX + clipL), top, int(rowX + clipR), top + BAND_H)

			if not self.__children.get("objectiveOver"):
				return

			isArabic = localeinfo.IsARABIC()
			left = int(rowX + TEXT_X)
			right = int(rowX + TEXT_RIGHT)
			top = int(rowY + BAND_TOP[1])

			for piece in self.__children.get("objectivePieces", []):
				anchor = piece["anchorX"] + offset if isArabic else piece["anchorX"] - offset
				piece["line"].SetPosition(int(anchor), BAND_TOP[1] + 3)
				piece["line"].SetClippingMaskRect(left, top, right, top + BAND_H)

				hover = piece["hover"]
				if hover is None:
					continue

				# A name that has slid out of the field must stop being clickable, so the region is
				# trimmed to the part still showing rather than travelling with the text.
				pieceLeft = (anchor - piece["width"]) if isArabic else anchor
				visibleLeft = max(pieceLeft, TEXT_X)
				visibleRight = min(pieceLeft + piece["width"], TEXT_RIGHT)
				if visibleRight - visibleLeft < 2:
					hover.Hide()
					continue

				hover.SetPosition(int(visibleLeft), BAND_TOP[1])
				hover.SetSize(int(visibleRight - visibleLeft), BAND_H)
				hover.Show()

		def IsObjectiveHot(self, mx, my):
			if not self.__children.get("objectiveOver") or not self.IsShow():
				return False

			(rowX, rowY) = self.GetGlobalPosition()
			return (mx >= rowX + TEXT_X and mx < rowX + TEXT_RIGHT
				and my >= rowY + BAND_TOP[1] and my < rowY + BAND_TOP[1] + BAND_H)

		# Driven every frame from RewardWindow.OnUpdate, not once a second like Tick.
		def MarqueeTick(self, now, dt, isHot):
			over = self.__children.get("objectiveOver")
			if not over and not self.__children.get("titleOver"):
				return

			offset = 0.0
			if over and not isHot:
				self.__children["objectiveOffset"] = 0.0
				self.__children["objectiveDone"] = False
				self.__children["objectiveSince"] = 0.0
			elif over:
				if not self.__children.get("objectiveSince"):
					self.__children["objectiveSince"] = now

				offset = self.__children.get("objectiveOffset", 0.0)
				if not self.__children.get("objectiveDone") \
					and now - self.__children["objectiveSince"] >= OBJ_MARQUEE_DELAY:
					travel = self.__children.get("objectiveTravel", 0)
					offset += OBJ_MARQUEE_SPEED_PX * dt
					if offset >= travel:
						offset = float(travel)
						self.__children["objectiveDone"] = True

				self.__children["objectiveOffset"] = offset

			self.ApplyClips(offset)

		def __RefreshButton(self, data):
			activate = self.__children["activate"]
			if data["state"] == CHALLENGE_ONGOING:
				activate.SetText(LocaleText("CHALLENGE_BTN_ONGOING", "Ongoing"))
				activate.Disable()
				activate.Show()
			elif data["state"] == CHALLENGE_AVAILABLE and data["limit"] > 0:
				activate.SetText(LocaleText("CHALLENGE_BTN_ACTIVATE", "Activate"))
				activate.Enable()
				activate.Show()
			else:
				activate.Hide()

		# Called every server second by RewardWindow.OnUpdate; only an ongoing row moves.
		def Tick(self):
			data = self.__children.get("data")
			if not data:
				return

			# The server expires a run lazily, on the next event it sees, so the row would otherwise
			# sit at 00:00:00 with a dead "Ongoing" button until then. This is the same state its
			# lazy check produces, and Activate works again immediately.
			if data["state"] == CHALLENGE_ONGOING and GetChallengeRemaining(data) <= 0:
				data["state"] = CHALLENGE_AVAILABLE
				data["deadline"] = 0
				self.ApplyRowSkin(CHALLENGE_AVAILABLE)
				self.__RefreshButton(data)

			state = data["state"]
			color = CHALLENGE_STATE_COLOR

			if state == CHALLENGE_LOCKED:
				(stateText, text) = (LocaleText("CHALLENGE_STATE_LOCKED", "Locked"), "")
			elif state == CHALLENGE_COMPLETED:
				(stateText, text) = (LocaleText("CHALLENGE_COMPLETED", "Completed"), "")
			elif state == CHALLENGE_ONGOING:
				stateText = LocaleText("CHALLENGE_STATE_ONGOING", "Ongoing")
				text = LocaleText("CHALLENGE_TIME_LEFT", "Time left: %s") % FormatChallengeClock(GetChallengeRemaining(data))
				color = CHALLENGE_STATE_LIVE_COLOR
			else:
				stateText = LocaleText("CHALLENGE_STATE_AVAILABLE", "Available")
				text = LocaleText("CHALLENGE_TIME_LIMIT", "Time limit: %s") % FormatChallengeDuration(data["limit"]) \
					if data["limit"] > 0 else LocaleText("CHALLENGE_UNTIMED", "Runs for the whole week")

			stateLine = self.__children["stateLine"]
			stateLine.SetText(stateText)
			stateLine.SetPackedFontColor(color)
			PlaceRowText(stateLine, BAND_TOP[2] + 3)

			# Gold is reserved for a clock that is actually running. "Time limit: 5 Minutes" and
			# "Runs for the whole week" describe a rule, not a countdown, and in gold they pulled
			# harder than the one line on the board that is ticking.
			timeLine = self.__children["timeLine"]
			timeLine.SetText(text)
			timeLine.SetPackedFontColor(
				CHALLENGE_TIME_COLOR if state == CHALLENGE_ONGOING else CHALLENGE_OBJECTIVE_COLOR)
			# Re-anchored on every tick: a countdown changes width as it passes each digit boundary.
			PlaceRowTextTrailing(timeLine, BAND_TOP[2] + 3)

		def OnActivate(self):
			data = self.__children.get("data")
			if not data or data["state"] != CHALLENGE_AVAILABLE:
				return

			net.SendChatPacket("/challenge activate %d" % self.__children["slot"])

		# The hover and the click both act on the one name under the cursor.
		def OnTargetOverIn(self, kind, vnum):
			(kind, vnum) = GetChallengeLookup(kind, vnum)
			if not kind:
				return

			toolTip = uichallengetooltip.GetToolTip()
			toolTip.SetTargets(GetChallengeTitle(self.__children["data"]), [(kind, [vnum])])
			toolTip.ShowNearMouse()

		def OnTargetOverOut(self):
			uichallengetooltip.HideToolTip()

		def OnTargetClick(self, kind, vnum):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			(kind, vnum) = GetChallengeLookup(kind, vnum)
			if not interfaceHandler or not kind:
				return

			if kind == "mob":
				interfaceHandler.OpenWikiToMonster(vnum)
			else:
				interfaceHandler.OpenWikiToItem(vnum, item.GetItemTypeByVnum(vnum) == item.ITEM_TYPE_GIFTBOX)

		def OverInItem(self, index):
			rewards = self.__children.get("rewards", [])
			if index >= len(rewards):
				return

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.tooltipItem:
				interfaceHandler.tooltipItem.SetItemToolTip(rewards[index][0])
				interfaceHandler.tooltipItem.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_WIKI_HOVER)

		def OverOutItem(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.tooltipItem:
				interfaceHandler.tooltipItem.HideToolTip()

		def SearchInWiki(self, index):
			rewards = self.__children.get("rewards", [])
			if index >= len(rewards) or not app.IsPressed(app.DIK_LSHIFT):
				return

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				itemVnum = rewards[index][0]
				interfaceHandler.OpenWikiToItem(itemVnum, item.GetItemTypeByVnum(itemVnum) == item.ITEM_TYPE_GIFTBOX)

	class RewardItemSolo(ui.ImageBox):
		def Destroy(self):
			self.__children = {}
		def GetRewardIndex(self):
			return self.__children["rewardIndex"] if self.__children.has_key("rewardIndex") else 0
		def __init__(self, pageIdx, rewardIndex, rewardData):
			ui.ImageBox.__init__(self)
			self.LoadReward(pageIdx, rewardIndex, rewardData)
		def LoadReward(self, pageIdx, rewardIndex, rewardData):
			self.LoadImage(IMG_DIR+"eldor_bg_personal.png")
			self.Destroy()
			self.__children["rewardIndex"] = rewardIndex

			self.__children["rewardImage"] = CreateWindow(ui.ImageBox(), self, (366, 0), IMG_ICON_DIR+rewardData["icon_name"]+".png")
			self.__children["bar"] = CreateWindow(ui.ExpandedImageBox(), self, (366-181, 32), IMG_DIR+"bar.tga")

			rewardName = CreateWindow(ui.TextLine(), self, (352, 55), GetMissionName(pageIdx, rewardData["type"], rewardData["subValue"], rewardData["level_difference"] if rewardData.has_key("level_difference") else 0), "horizontal:left")
			rewardName.SetPackedFontColor(0xffdfe6e9)
			self.__children["rewardName"] = rewardName

			self.SetRewardValue(rewardData["value"])

			grid = Grid(3,2)
			grid.reset()

			rewardItems = CreateWindow(ui.GridSlotWindow(), self, (8, 9))
			rewardItems.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
			rewardItems.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
			rewardItems.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
			rewardItems.SetUnselectItemSlotEvent(ui.__mem_func__(self.SearchInWiki)) #to do : add wiki 
			rewardItems.SAFE_SetButtonEvent("LEFT", "EXIST", self.RenderTarget)
			rewardItems.ArrangeSlot(0, 3, 2, 32, 32, 0, 0)
			rewardItems.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
			for rewardItem in rewardData["reward_items"]:
				(itemVnum,itemCount) = (rewardItem[0],rewardItem[1])
				item.SelectItem(itemVnum)
				(width,height) = item.GetItemSize()
				pos = grid.find_blank(width, height)
				grid.put(pos, width, height)
				rewardItems.SetItemSlot(pos, itemVnum, itemCount)
			rewardItems.RefreshSlot()
			self.__children["rewardItems"] = rewardItems

		def SetRewardValue(self, value):
			maxValue = solo_reward_info[self.GetRewardIndex()]["max_value"]

			self.__children["value"] = CreateWindow(ui.TextLine(), self, (355, 11), NumberToDecimalString(value)+" / "+NumberToDecimalString(maxValue),"horizontal:left")
			if value:
				self.__children["bar"].Show()
				self.__children["bar"].SetScale(float(value) * (1.0 / float(maxValue)), 1.0)
			else:
				self.__children["bar"].Hide()

			if value >= maxValue:#my addons
				rewardDoneSolo = CreateWindow(ui.ImageBox(), self, (366, 0), IMG_ICON_DIR+"new_done.png")
				self.__children["rewardDoneSolo"] = rewardDoneSolo#end of my addons

		def SearchInWiki(self, index):
			rewardIndex = self.__children["rewardIndex"]
			global solo_reward_info
			rewardData = solo_reward_info[rewardIndex] if solo_reward_info.has_key(rewardIndex) else None
			itemVnum = rewardData["reward_items"][index][0]
			isBox = 1 if item.GetItemTypeByVnum(itemVnum) == item.ITEM_TYPE_GIFTBOX else 0
			if app.IsPressed(app.DIK_LSHIFT):
				import wiki
				wiki.GetBaseClass().OpenSpecialWikiPage(itemVnum,isBox)

			if app.USE_OFFLINESHOP and\
				not uiofflineshop_ae.IsBuildingShop() and\
				(app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT)):
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler:
					wndShopOffline = interfaceHandler.wndShopOffline
					if wndShopOffline:
						wndSearchShop = wndShopOffline.wndSearchShop
						if wndSearchShop:
							wndSearchShop.SearchByName(item.GetItemNameByVnum(itemVnum))

		def OverInItem(self, index):#to do : this only shows the first index which is 0
			rewardIndex = self.__children["rewardIndex"]
			global solo_reward_info
			rewardData = solo_reward_info[rewardIndex] if solo_reward_info.has_key(rewardIndex) else None
			if not rewardData:
				return

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.tooltipItem:
				interfaceHandler.tooltipItem.SetItemToolTip(rewardData["reward_items"][index][0])
				interfaceHandler.tooltipItem.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_WIKI_HOVER)
				interfaceHandler.tooltipItem.DeclareShortcut(("key_alt", "key_rclick"), localeinfo.TOOLTIP_QUICKSEARCH_OFFLINESHOP)

		def OverOutItem(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.tooltipItem:
				interfaceHandler.tooltipItem.HideToolTip()

		def RenderTarget(self, index):
			rewardIndex = self.__children["rewardIndex"]
			global solo_reward_info
			rewardData = solo_reward_info[rewardIndex] if solo_reward_info.has_key(rewardIndex) else None
			itemVnum = rewardData["reward_items"][index][0]

			if app.IsPressed(app.DIK_LSHIFT) and uiRenderTarget.IsCanShowItems(itemVnum):
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler:
					interfaceHandler.OpenRenderTargetWindow(0, itemVnum)

	def Destroy(self):
		self.__children = {}

	def __init__(self):
		self.__children = {}
		ui.Window.__init__(self)
		self.__LoadWindow()

	def __LoadWindow(self):
		self.Destroy()

		self.AddFlag("movable")
		self.AddFlag("attach")
		self.AddFlag("float")
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		# >>> REWARD_V2 BEGIN -- replaced by the Inner_Board shell below (disabled)
		# board = CreateWindow(ui.BoardWithTitleBar(), self, (0, 0), "", "", (484, 385))
		# board.AddFlag("attach")
		# board.SetCloseEvent(self.Close)
		# self.__children["board"] = board
		#
		# boardImage = CreateWindow(ui.ImageBox(), board, (8, 30), IMG_DIR+"board.tga")
		# self.__children["boardImage"] = boardImage
		#
		# scrollBar = CreateWindow(ScrollBarSpecial(False), boardImage, (459, 1), "", "", (9, SCROLLBAR_HEIGHT))
		# scrollBar.SetScale(SCROLLBAR_HEIGHT/2, SCROLLBAR_HEIGHT)
		# self.__children["scrollBar"] = scrollBar
		#
		# listBox = CreateWindow(ui.ListBoxEx(), boardImage, (4+10, 4), "", "", (boardImage.GetWidth(), boardImage.GetHeight()))
		# listBox.SetViewItemCount(4)
		# listBox.OnMouseWheel = ui.__mem_func__(self.OnMouseWheel)
		# listBox.SetItemSize(450, 81)
		# listBox.SetItemStep(83)
		# listBox.SetScrollBar(scrollBar)
		# self.__children["listBox"] = listBox
		#
		# pageBtnImg = CreateWindow(ui.ImageBox(), self, (3, 30 + boardImage.GetHeight() + 5), IMG_DIR+"page_0.tga")
		# self.__children["pageBtnImg"] = pageBtnImg
		#
		# pageBtn = CreateWindow(ui.ImageBox(), pageBtnImg, (0, 0), IMG_DIR+"btn.tga")
		# self.__children["pageBtn"] = pageBtn
		#
		# self.SetSize(484, 420)
		# <<< REWARD_V2 END

		board = CreateWindow(ui.BoardWithTitleBar(), self, (TAB_STRIP_W, 0), "", "", (BOARD_W, BOARD_H))
		board.AddFlag("attach")
		board.SetCloseEvent(self.Close)
		self.__children["board"] = board

		boardImage = CreateWindow(ui.ImageBox(), board, (BOARD_MARGIN, BOARD_TITLE_H), IMG_CHALLENGE_DIR+"Inner_Board.png")
		self.__children["boardImage"] = boardImage

		scrollBar = CreateWindow(ScrollBarSpecial(False), boardImage, (SCROLL_X, LIST_Y), "", "", (9, LIST_H))
		scrollBar.SetScale(LIST_H/2, LIST_H)
		self.__children["scrollBar"] = scrollBar

		listBox = CreateWindow(ui.ListBoxEx(), boardImage, (LIST_X, LIST_Y), "", "", (ROW_W, LIST_H))
		listBox.SetViewItemCount(ROWS_PER_PAGE)
		listBox.OnMouseWheel = ui.__mem_func__(self.OnMouseWheel)
		listBox.SetItemSize(ROW_W + LISTBOX_ARABIC_MARGIN, ROW_H)
		listBox.SetItemStep(ROW_STEP)
		listBox.SetScrollBar(scrollBar)
		self.__children["listBox"] = listBox

		# Shown only when the server has sent a board and that board has no rows. Without it an
		# empty board is indistinguishable from no board and the tab silently shows the retired
		# solo missions, frozen, because nothing feeds them any more.
		emptyNotice = CreateWindow(ui.TextLine(), boardImage, (LIST_X + ROW_W // 2, LIST_Y + LIST_H // 2))
		emptyNotice.SetHorizontalAlignCenter()
		emptyNotice.SetText(LocaleText("CHALLENGE_NONE_AVAILABLE", "No challenges are available for your level this week."))
		emptyNotice.SetPackedFontColor(CHALLENGE_OBJECTIVE_COLOR)
		emptyNotice.Hide()
		self.__children["emptyNotice"] = emptyNotice

		# The tab strip hangs off the board's left edge, so the window is wider than the board.
		tabs = []
		for tabIdx, imageName in enumerate(TAB_IMAGES):
			tab = CreateWindow(ui.Button(), self, (0, TAB_Y + tabIdx * TAB_STEP))
			tab.SetUpVisual(IMG_CHALLENGE_DIR + imageName + "_normal.png")
			tab.SetOverVisual(IMG_CHALLENGE_DIR + imageName + "_hover.png")
			tab.SetDownVisual(IMG_CHALLENGE_DIR + imageName + "_hover.png")
			tab.SAFE_SetEvent(self.__OnClickTab, "", tabIdx)
			# Icon-only buttons with no label, so the tab name lives in a tooltip. Reuses the
			# strings the title bar already shows for each page.
			tab.SetToolTipText([localeinfo.REWARD_SYSTEM_GLOBAL_SYR, localeinfo.REWARD_SYSTEM_SOLO][tabIdx])
			tab.Show()
			tabs.append(tab)
		self.__children["tabs"] = tabs

		# Inside the title bar, opposite the close button. SetText resizes the widget, so the
		# right-anchored position can only be computed afterwards.
		onlyUnfinished = CreateWindow(ui.CheckBox_Biolog(), board, (0, 9))
		onlyUnfinished.SetText(LocaleText("REWARD_ONLY_UNFINISHED", "Show only unfinished"))
		onlyUnfinished.SetPosition(BOARD_W - onlyUnfinished.GetWidth() - 14, 9)
		onlyUnfinished.SAFE_SetEvent(self.__OnToggleUnfinished)
		onlyUnfinished.Show()
		self.__children["onlyUnfinished"] = onlyUnfinished

		self.SetSize(TAB_STRIP_W + BOARD_W, BOARD_H)
		self.SetCenterPosition()

		for key, data in global_reward_info.items():
			# if data["type"] == player.REWARD_MISSION_ZODIAC_DUNGEON and data["subValue"] == 1:
				# continue
			data["player_names"] = ["", "", ""]

		for key, data in solo_reward_info.items():
			data["value"] = 0

		self.__SetPage("", 0)

	# Only the tab strip routes through here. __SetPage is also called from the board handler,
	# and telling the server from there would answer every board with a request for another.
	def __OnClickTab(self, emptyArg, pageIdx):
		if pageIdx != self.__children.get("pageIdx"):
			self.__NotifyChallengeWindow(pageIdx == 1)

		self.__SetPage(emptyArg, pageIdx)

	# A warp rebuilds the interface and this window with it, and nothing calls Close() on the
	# way out. The fresh window is on the global tab and hidden, so telling the server it is
	# closed is both true and what stops the progress commands.
	def NotifyChallengeClosed(self):
		self.__NotifyChallengeWindow(False)

	# The login board is pushed while the client is still in its loading phase, where
	# CPythonNetworkStream::ServerCommand has no game-phase window to hand it to and drops
	# the command. Nothing re-sends it -- /challenge open is itself gated on a board having
	# arrived -- so the tab stayed blank for the rest of the session. Asking from here, once
	# the interface exists, cannot race; the reply clears and replaces whatever is held, so
	# it also drops the previous character's board after a character swap.
	def RequestChallengeBoard(self):
		net.SendChatPacket("/reward_system challenge")

	# Nothing is sent until a board has arrived: see challenge_seen.
	def __NotifyChallengeWindow(self, isOpen):
		if not challenge_seen[0]:
			return

		net.SendChatPacket("/challenge open" if isOpen else "/challenge close")

	def __SetPage(self, emptyArg, pageIdx):
		self.__children["pageIdx"] = pageIdx

		for tabIdx, tab in enumerate(self.__children["tabs"]):
			suffix = "_hover" if tabIdx == pageIdx else "_normal"
			tab.SetUpVisual(IMG_CHALLENGE_DIR + TAB_IMAGES[tabIdx] + suffix + ".png")

		# The rows that own the hover regions are about to be destroyed.
		uichallengetooltip.HideToolTip()

		listBox = self.__children["listBox"] if self.__children.has_key("listBox") else None
		scrollBar = self.__children["scrollBar"] if self.__children.has_key("scrollBar") else None
		listBox.RemoveAllItems()

		scrollBar.SetPos(0)

		onlyUnfinished = self.__children["onlyUnfinished"].IsChecked()

		totalY = 0
		if pageIdx == 0:
			#global
			for key, data in global_reward_info.items():
				if onlyUnfinished and IsGlobalMissionFinished(data):
					continue
				listBox.AppendItem(self.RewardItemGlobal(pageIdx, key, data))
				totalY += ROW_STEP
		elif pageIdx == 1:
			# The weekly board takes the tab over as soon as one has arrived, rows or no rows. The
			# legacy solo missions render only while nothing has ever arrived, which is the
			# ENABLE_WEEKLY_CHALLENGES-off path and nothing else -- task 4.8 stopped feeding them.
			if challenge_seen[0]:
				for slot in sorted(challenge_board.keys()):
					data = challenge_board[slot]
					if onlyUnfinished and data["state"] == CHALLENGE_COMPLETED:
						continue
					listBox.AppendItem(self.RewardItemChallenge(pageIdx, slot, data))
					totalY += ROW_STEP
			else:
				for key, data in solo_reward_info.items():
					if onlyUnfinished and IsSoloMissionFinished(data):
						continue
					listBox.AppendItem(self.RewardItemSolo(pageIdx, key, data))
					totalY += ROW_STEP

		emptyNotice = self.__children.get("emptyNotice")
		if emptyNotice:
			if pageIdx == 1 and challenge_seen[0] and not challenge_board:
				emptyNotice.Show()
			else:
				emptyNotice.Hide()

		self.__children["board"].SetTitleName([localeinfo.REWARD_SYSTEM_GLOBAL_SYR, localeinfo.REWARD_SYSTEM_SOLO][pageIdx])
		scrollBar.SetScale(LIST_H, totalY if totalY > LIST_H else LIST_H)

	def __OnToggleUnfinished(self):
		self.__SetPage("", self.__children["pageIdx"])

	def RewardDefs(self, isNeedClean, commandText):
		if isNeedClean:
			global_reward_info.clear()

		if commandText == "empty":
			self.__RedrawGlobalPage()
			return

		for data in commandText.split("#"):
			dataSplit = data.split("?")
			if len(dataSplit) != 2:
				continue

			fields = dataSplit[1].split(",")
			if len(fields) < 5:
				continue

			idx = int(dataSplit[0])
			rewardData = global_reward_info[idx] if global_reward_info.has_key(idx) else {}
			rewardData["type"] = int(fields[0])
			rewardData["subValue"] = int(fields[1])
			rewardData["reward_items_1st"] = ParseRewardPairs(fields[2])
			rewardData["reward_items_2nd"] = ParseRewardPairs(fields[3])
			rewardData["reward_items_3rd"] = ParseRewardPairs(fields[4])
			if not rewardData.has_key("player_names"):
				rewardData["player_names"] = ["", "", ""]

			global_reward_info[idx] = rewardData

		self.__RedrawGlobalPage()

	def RewardTargets(self, isNeedClean, commandText):
		if isNeedClean:
			global_reward_targets.clear()

		if commandText == "empty":
			self.__RedrawGlobalPage()
			return

		for data in commandText.split("#"):
			dataSplit = data.split("?")
			if len(dataSplit) != 2:
				continue

			fields = dataSplit[1].split(",")
			if len(fields) < 2:
				continue

			global_reward_targets[int(dataSplit[0])] = {
				"items" : ParseVnumList(fields[0]),
				"wear" : ParseWearGroups(fields[1]),
			}

		self.__RedrawGlobalPage()

	# The global list is built when the window is constructed, long before the first
	# /reward_system update can answer, so it is built from nothing. The defs and targets
	# that follow only filled the dicts -- RewardData updates rows in place and there were
	# no rows to update -- so the tab stayed blank until a tab click rebuilt it.
	def __RedrawGlobalPage(self):
		if self.__children.get("pageIdx") == 0:
			self.__SetPage("", 0)

	def RewardWin(self, missionIdx, placement, playerName):
		if not global_reward_info.has_key(missionIdx):
			return

		rewardData = global_reward_info[missionIdx]
		missionName = GetMissionName(0, rewardData["type"], rewardData["subValue"])
		placeName = GetPlacementName(placement)
		if not placeName:
			return

		chat.AppendChat(chat.CHAT_TYPE_NOTICE,
			LocaleText("REWARD_WIN_NOTICE", "%s took %s place in: %s") % (playerName, placeName, missionName))

		if playerName == player.GetMainCharacterName():
			chat.AppendChat(chat.CHAT_TYPE_INFO,
				LocaleText("REWARD_WIN_MINE", "You took %s place in: %s") % (placeName, missionName))

	def ChallengeBoard(self, isNeedClean, commandText):
		challenge_seen[0] = True
		if isNeedClean:
			challenge_board.clear()

		if commandText != "empty":
			now = ServerNow()
			for data in commandText.split("#"):
				dataSplit = data.split("?")
				if len(dataSplit) != 2:
					continue

				fields = dataSplit[1].split(",")
				if len(fields) < 9:
					continue

				# The server sends seconds remaining, not an absolute time, so the countdown never
				# depends on the two clocks agreeing.
				remain = int(fields[4])
				challenge_board[int(dataSplit[0])] = {
					"id" : int(fields[0]),
					"tier" : int(fields[1]),
					"state" : int(fields[2]),
					"limit" : int(fields[3]),
					"level_min" : int(fields[5]),
					"title_key" : fields[6],
					"targets" : ParseChallengeTargets(fields[7]),
					"rewards" : ParseRewardPairs(fields[8]),
					"deadline" : (now + remain) if remain else 0,
				}

		if self.__children.get("pageIdx") == 1:
			self.__SetPage("", 1)

		self.RefreshTracker()

	def ChallengeProg(self, slot, progressText):
		if not challenge_board.has_key(slot):
			return

		targets = challenge_board[slot]["targets"]
		values = [int(value) for value in progressText.split(".") if value]
		for i in range(min(len(values), len(targets))):
			targets[i][3] = values[i]

		if self.__children.get("pageIdx") == 1:
			listBox = self.__children.get("listBox")
			for child in (listBox.itemList if listBox else []):
				if child.GetRewardIndex() == slot:
					child.Refresh(challenge_board[slot])
					break

		self.RefreshTracker()

	# The tracker follows the one running timed challenge, window open or closed. Untimed
	# challenges never raise it -- they would leave a board on screen all week.
	# interfaceHandler is passed in during MakeInterface, when the module-level handler is not
	# published yet -- a warp rebuilds the interface and drops the tracker, and the run has to get
	# its board back straight away rather than at the next progress event.
	def RefreshTracker(self, interfaceHandler = None):
		if not interfaceHandler:
			interfaceHandler = systemSetting.GetInterfaceHandler()
		if not interfaceHandler:
			return

		(total, here) = GetChallengeMapCounts()
		interfaceHandler.ChallengeMapButtonRefresh(total, here)

		for slot in sorted(challenge_board.keys()):
			data = challenge_board[slot]
			if data["state"] != CHALLENGE_ONGOING:
				continue

			# (name, have, need, kind, vnum): the HUD hovers its target names the same way the
			# window does, and needs what to look up as well as what to print.
			targets = [(ComposeChallengeTarget(target), target[3], target[2])
				+ GetChallengeLookup(GetChallengeSubjectKind(target[0]), target[1])
				for target in data["targets"]]
			interfaceHandler.ChallengeHudOn(GetChallengeTitle(data), data["deadline"], targets)
			return

		interfaceHandler.ChallengeHudOff()

	# Two cadences. The marquee and its clip rects run every frame -- the rects are screen-space
	# and the list scrolls -- while the clocks only need the server second.
	def OnUpdate(self):
		if not challenge_board or self.__children.get("pageIdx") != 1:
			return

		listBox = self.__children.get("listBox")
		items = listBox.itemList if listBox else []

		clock = app.GetTime()
		dt = clock - self.__children.get("marqueeClock", clock)
		self.__children["marqueeClock"] = clock
		if dt < 0.0 or dt > 0.5:
			dt = 0.0

		# Slot index rather than the row object: a handler's self is a weakref proxy here and
		# identity comparisons on those quietly fail.
		hotSlot = -1
		if self.IsShow():
			(mouseX, mouseY) = wndMgr.GetMousePosition()
			for child in items:
				if child.IsObjectiveHot(mouseX, mouseY):
					hotSlot = child.GetRewardIndex()
					break

		for child in items:
			child.MarqueeTick(clock, dt, child.GetRewardIndex() == hotSlot)

		now = ServerNow()
		if now == self.__children.get("lastTick"):
			return

		self.__children["lastTick"] = now
		for child in items:
			child.Tick()

	def RewardData(self, isGlobal, isNeedClean, commandText):
		pageIdx = self.__children["pageIdx"]
		if isGlobal:
			if isNeedClean:
				for key, data in global_reward_info.items():
					# if data["type"] == player.REWARD_MISSION_ZODIAC_DUNGEON and data["subValue"] == 1:
						# continue
					data["player_names"] = ["", "", ""]
					data["player_times"] = ["", "", ""]
					data["player_guilds"] = ["", "", ""]

			if commandText != "empty":
				dataList = commandText.split("#")
				for data in dataList:
					dataSplit = data.split("?")
					if len(dataSplit) != 2:
						continue

					idx = int(dataSplit[0])
					if not global_reward_info.has_key(idx):
						continue

					(playerNames, playerTimes, playerGuilds) = ParsePlacementFields(dataSplit[1])
					global_reward_info[idx]["player_names"] = playerNames
					global_reward_info[idx]["player_times"] = playerTimes
					global_reward_info[idx]["player_guilds"] = playerGuilds

					if pageIdx == 0:
						listBox = self.__children["listBox"] if self.__children.has_key("listBox") else None
						for child in listBox.itemList:
							if child.GetRewardIndex() == idx:
								child.SetRewardPlayers(playerNames, playerTimes, playerGuilds)
								break
		else:
			if isNeedClean:
				for key, data in solo_reward_info.items():
					data["value"] = 0
			if commandText != "empty":
				dataList = commandText.split("#")
				for data in dataList:
					dataSplit = data.split("?")
					if len(dataSplit) == 2:
						idx = int(dataSplit[0])
						if solo_reward_info.has_key(idx):
							solo_reward_info[idx]["value"] = int(dataSplit[1])

						if pageIdx == 1:
							listBox = self.__children["listBox"] if self.__children.has_key("listBox") else None
							for child in listBox.itemList:
								if child.GetRewardIndex() == idx:
									child.SetRewardValue(int(dataSplit[1]))
									break

	def OnMouseWheel(self, length):
		scrollBar = self.__children["scrollBar"] if self.__children.has_key("scrollBar") else None
		if scrollBar:
			if scrollBar.IsShow():
				scrollBar.OnMouseWheel(length)
				return True
		return False

	def Open(self):
		packetStatus = self.__children["packetStatus"] if self.__children.has_key("packetStatus") else False
		if not packetStatus:
			net.SendChatPacket("/reward_system update")
			self.__children["packetStatus"] = True
		if self.__children.get("pageIdx") == 1:
			self.__NotifyChallengeWindow(True)
		self.SetTop()
		self.Show()
	def OpenChallenges(self):
		if self.IsShow() and self.__children.get("pageIdx") == 1:
			self.Close()
			return

		self.Open()
		if self.__children.get("pageIdx") != 1:
			self.__OnClickTab("", 1)

	def Close(self):
		uichallengetooltip.HideToolTip()
		if self.__children.get("pageIdx") == 1:
			self.__NotifyChallengeWindow(False)
		self.Hide()
	def OnPressEscapeKey(self):
		self.Close()
		return True

class ScrollBarSpecial(ui.Window):
	BASE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
	CORNERS_AND_LINES_COLOR = grp.GenerateColor(0.3411, 0.3411, 0.3411, 1.0)
	BAR_NUMB = 9 #This is static value! Please dont touch in him.
	SCROLL_WIDTH= 8
	class MiddleBar(ui.DragButton):
		MIDDLE_BAR_COLOR = grp.GenerateColor(0.6470, 0.6470, 0.6470, 1.0)
		def __init__(self, horizontal_scroll):
			ui.DragButton.__init__(self)
			self.AddFlag("movable")
			self.horizontal_scroll = horizontal_scroll
			self.middle = ui.Bar()
			self.middle.SetParent(self)
			self.middle.AddFlag("attach")
			self.middle.AddFlag("not_pick")
			self.middle.SetColor(self.MIDDLE_BAR_COLOR)
			self.middle.SetSize(1, 1)
			self.middle.Show()
		def SetStaticScale(self, size):
			(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
			if not self.horizontal_scroll:
				ui.DragButton.SetSize(self, base_width, size)
				self.middle.SetSize(base_width, size)
			else:
				ui.DragButton.SetSize(self, size, base_height)
				self.middle.SetSize(size, base_height)
		def SetSize(self, selfSize, fullSize):
			(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
			
			if not self.horizontal_scroll:
				ui.DragButton.SetSize(self, base_width, truediv(int(selfSize), int(fullSize)) * selfSize)
				self.middle.SetSize(base_width, truediv(int(selfSize), int(fullSize)) * selfSize)
			else:
				ui.DragButton.SetSize(self, truediv(int(selfSize), int(fullSize)) * selfSize, base_height)
				self.middle.SetSize(truediv(int(selfSize), int(fullSize)) * selfSize, base_height)
		def SetStaticSize(self, size):
			size = max(2, size)
			
			if not self.horizontal_scroll:
				ui.DragButton.SetSize(self, size, self.middle.GetHeight())
				self.middle.SetSize(size, self.middle.GetHeight())
			else:
				ui.DragButton.SetSize(self, self.middle.GetWidth(), size)
				self.middle.SetSize(self.middle.GetWidth(), size)
	def __init__(self, horizontal_scroll = False):
		ui.Window.__init__(self)
		self.horizontal_scroll = horizontal_scroll
		self.scrollEvent = None
		self.scrollSpeed = 50
		self.sizeScale = 1.0
		self.bars = []
		for i in xrange(self.BAR_NUMB):
			br = ui.Bar()
			br.SetParent(self)
			br.AddFlag("attach")
			br.AddFlag("not_pick")
			br.SetColor([self.CORNERS_AND_LINES_COLOR, self.BASE_COLOR][i == (self.BAR_NUMB-1)])
			if not (i % 2 == 0): br.SetSize(1, 1)
			br.Show()
			self.bars.append(br)
		self.middleBar = self.MiddleBar(self.horizontal_scroll)
		self.middleBar.SetParent(self)
		self.middleBar.SetMoveEvent(ui.__mem_func__(self.OnScrollMove))
		self.middleBar.Show()
	def OnScrollMove(self):
		if not self.scrollEvent:
			return
		arg = float(self.middleBar.GetLocalPosition()[1] - 1) / float(self.GetHeight() - 2 - self.middleBar.GetHeight()) if not self.horizontal_scroll else\
				float(self.middleBar.GetLocalPosition()[0] - 1) / float(self.GetWidth() - 2 - self.middleBar.GetWidth())
		self.scrollEvent(arg)
	def SetScrollEvent(self, func):
		self.scrollEvent = func
	def SetScrollSpeed(self, speed):
		self.scrollSpeed = speed
	def OnRunMouseWheel(self, length):
		if not self.IsShow():
			return False
		length = int((length * 0.01) * self.scrollSpeed)
		if not self.horizontal_scroll:
			val = min(max(1, self.middleBar.GetLocalPosition()[1] - (length * 0.01) * self.scrollSpeed * self.sizeScale), self.GetHeight() - self.middleBar.GetHeight() - 1)
			self.middleBar.SetPosition(1, val)
		else:
			val = min(max(1, self.middleBar.GetLocalPosition()[0] - (length * 0.01) *  self.scrollSpeed * self.sizeScale), self.GetWidth() - self.middleBar.GetWidth() - 1)
			self.middleBar.SetPosition(val, 1)
		self.OnScrollMove()
		return True
	def GetPos(self):
		return float(self.middleBar.GetLocalPosition()[1] - 1) / float(self.GetHeight() - 2 - self.middleBar.GetHeight()) if not self.horizontal_scroll else float(self.middleBar.GetLocalPosition()[0] - 1) / float(self.GetWidth() - 2 - self.middleBar.GetWidth())
	def OnMouseLeftButtonDown(self):
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		if not self.horizontal_scroll:
			if xMouseLocalPosition == 0 or xMouseLocalPosition == self.GetWidth():
				return
			y_pos = (yMouseLocalPosition - self.middleBar.GetHeight() / 2)
			self.middleBar.SetPosition(1, y_pos)
		else:
			if yMouseLocalPosition == 0 or yMouseLocalPosition == self.GetHeight():
				return
			x_pos = (xMouseLocalPosition - self.middleBar.GetWidth() / 2)
			self.middleBar.SetPosition(x_pos, 1)
		self.OnScrollMove()
	def SetSize(self, w, h):
		(width, height) = (max(3, w), max(3, h))
		ui.Window.SetSize(self, width, height)
		self.bars[0].SetSize(1, (height - 2))
		self.bars[0].SetPosition(0, 1)
		self.bars[2].SetSize((width - 2), 1)
		self.bars[2].SetPosition(1, 0)
		self.bars[4].SetSize(1, (height - 2))
		self.bars[4].SetPosition((width - 1), 1)
		self.bars[6].SetSize((width - 2), 1)
		self.bars[6].SetPosition(1, (height - 1))
		self.bars[8].SetSize((width - 2), (height - 2))
		self.bars[8].SetPosition(1, 1)
		self.bars[1].SetPosition(0, 0)
		self.bars[3].SetPosition((width - 1), 0)
		self.bars[5].SetPosition((width - 1), (height - 1))
		self.bars[7].SetPosition(0, (height - 1))
		if not self.horizontal_scroll:
			self.middleBar.SetStaticSize(width - 2)
			self.middleBar.SetSize(12, self.GetHeight())
		else:
			self.middleBar.SetStaticSize(height - 2)
			self.middleBar.SetSize(12, self.GetWidth())
		self.middleBar.SetRestrictMovementArea(1, 1, width - 2, height - 2)
	def SetScale(self, selfSize, fullSize):
		self.sizeScale = float(selfSize)/float(fullSize)
		if self.sizeScale <= 0.0305:
			self.sizeScale = 0.05
		self.middleBar.SetSize(selfSize, fullSize)
	def SetStaticScale(self, r_size):
		self.middleBar.SetStaticScale(r_size)
	def SetPosScale(self, fScale):
		pos = (math.ceil((self.GetHeight() - 2 - self.middleBar.GetHeight()) * fScale) + 1) if not self.horizontal_scroll else (math.ceil((self.GetWidth() - 2 - self.middleBar.GetWidth()) * fScale) + 1)
		self.SetPos(pos)
	def SetPos(self, pos):
		wPos = (1, pos) if not self.horizontal_scroll else (pos, 1)
		self.middleBar.SetPosition(*wPos)
		self.OnScrollMove()

class Grid:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.reset()
	def find_blank(self, width, height):
		if width > self.width or height > self.height:
			return -1
		for row in range(self.height):
			for col in range(self.width):
				index = row * self.width + col
				if self.is_empty(index, width, height):
					return index
		return -1
	def put(self, pos, width, height):
		if not self.is_empty(pos, width, height):
			return False
		for row in range(height):
			start = pos + (row * self.width)
			self.grid[start] = True
			col = 1
			while col < width:
				self.grid[start + col] = True
				col += 1
		return True
	def clear(self, pos, width, height):
		if pos < 0 or pos >= (self.width * self.height):
			return
		for row in range(height):
			start = pos + (row * self.width)
			self.grid[start] = True
			col = 1
			while col < width:
				self.grid[start + col] = False
				col += 1
	def is_empty(self, pos, width, height):
		if pos < 0:
			return False
		row = pos // self.width
		if (row + height) > self.height:
			return False
		if (pos + width) > ((row * self.width) + self.width):
			return False
		for row in range(height):
			start = pos + (row * self.width)
			if self.grid[start]:
				return False
			col = 1
			while col < width:
				if self.grid[start + col]:
					return False
				col += 1
		return True
	def get_size(self):
		return self.width * self.height
	def reset(self):
		self.grid = [False] * (self.width * self.height)

def CreateWindow(window, parent, windowPos, windowArgument = "", windowPositionRule = "", windowSize = (-1, -1), windowFontName = -1):
	window.SetParent(parent)
	window.SetPosition(*windowPos)
	if windowSize != (-1, -1):
		window.SetSize(*windowSize)
	if windowPositionRule:
		splitList = windowPositionRule.split(":")
		if len(splitList) == 2:
			(type, mode) = (splitList[0], splitList[1])
			if type == "horizontal":
				if isinstance(window, ui.TextLine):
					if mode == "center":
						window.SetHorizontalAlignCenter()
					elif mode == "right":
						window.SetHorizontalAlignRight()
					elif mode == "left":
						window.SetHorizontalAlignLeft()
				else:
					if mode == "center":
						window.SetWindowHorizontalAlignCenter()
					elif mode == "right":
						window.SetWindowHorizontalAlignRight()
					elif mode == "left":
						window.SetWindowHorizontalAlignLeft()
			elif type == "vertical":
				if isinstance(window, ui.TextLine):
					if mode == "center":
						window.SetVerticalAlignCenter()
					elif mode == "top":
						window.SetVerticalAlignTop()
					elif mode == "bottom":
						window.SetVerticalAlignBottom()
				else:
					if mode == "top":
						window.SetWindowVerticalAlignTop()
					elif mode == "center":
						window.SetWindowVerticalAlignCenter()
					elif mode == "bottom":
						window.SetWindowVerticalAlignBottom()
	if windowArgument:
		if isinstance(window, ui.TextLine):
			if windowFontName != -1:
				window.SetFontName(windowFontName)
			window.SetText(windowArgument)
		elif isinstance(window, ui.NumberLine):
			window.SetNumber(windowArgument)
		elif isinstance(window, ui.ExpandedImageBox) or isinstance(window, ui.ImageBox):
			window.LoadImage(windowArgument if windowArgument.find("gr2") == -1 else "icon/item/27995.tga")
	window.Show()
	return window

def NumberToDecimalString(n):
	return str('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))
