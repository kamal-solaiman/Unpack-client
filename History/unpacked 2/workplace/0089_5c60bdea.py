# Mission progress helper - checks if a target matches an active mission
# Used by uitarget.py and uitooltip.py to show mission progress

import nonplayer
import localeinfo

_missionWindow = None

# Mission type constants
TYPE_MONSTERS = 1
TYPE_STONES = 2
TYPE_BOSSES = 3
TYPE_MINING = 4
TYPE_FISHING = 5
TYPE_DUNGEON = 6
TYPE_USE_ITEM = 7


RANK_BOSS = 4  # nonplayer.BOSS
RANK_KING = 5  # nonplayer.KING

def SetMissionWindow(wnd):
	"""Register the mission window instance for lookups."""
	global _missionWindow
	_missionWindow = wnd

def GetMissionWindow():
	"""Get the registered mission window."""
	global _missionWindow
	return _missionWindow

def _IsMonsterMatchingType(monsterVnum, missionType):
	"""
	Check if a monster matches the mission type.

	Args:
		monsterVnum: The monster's VNUM
		missionType: TYPE_MONSTERS, TYPE_STONES, or TYPE_BOSSES

	Returns:
		True if monster matches the type, False otherwise
	"""
	if missionType == TYPE_STONES:
		# Check if monster is a metin stone
		return nonplayer.IsMonsterStone(monsterVnum)

	elif missionType == TYPE_BOSSES:
		# Check if monster is a boss (rank >= BOSS)
		try:
			rank = nonplayer.GetMonsterRank(monsterVnum)
			return rank >= RANK_BOSS
		except:
			return False

	elif missionType == TYPE_MONSTERS:
		# Regular monsters: not a stone and not a boss
		if nonplayer.IsMonsterStone(monsterVnum):
			return False
		try:
			rank = nonplayer.GetMonsterRank(monsterVnum)
			return rank < RANK_BOSS
		except:
			return True  # If we can't get rank, assume it's a regular monster

	return False

def GetMonsterMissionProgress(monsterVnum):
	"""
	Check if monster is a mission target.
	Returns (currentProgress, maxProgress, categoryName) or None

	Args:
		monsterVnum: The monster's VNUM to check

	Returns:
		Tuple of (progress, maxProgress, categoryName) if monster is a mission target
		None if monster is not a mission target
	"""
	global _missionWindow
	if not _missionWindow:
		return None

	if not hasattr(_missionWindow, 'dictMissionInfo'):
		return None

	# Check all mission slots
	for category in [0, 1]:  # Daily, Weekly
		for index in [0, 1, 2]:  # 3 slots each
			if category not in _missionWindow.dictMissionInfo:
				continue
			if index not in _missionWindow.dictMissionInfo[category]:
				continue
			if "info" not in _missionWindow.dictMissionInfo[category][index]:
				continue

			info = _missionWindow.dictMissionInfo[category][index]["info"]
			# info = [typeTarget, vnumTarget, progress, maxProgress, isCollected, minLevel, maxLevel, rewardVnum, rewardCount]
			if len(info) < 5:
				continue

			typeTarget = info[0]
			vnumTarget = info[1]
			progress = info[2]
			maxProgress = info[3]
			isCollected = info[4]

			# Skip completed missions
			if isCollected:
				continue

			# Check if this is a monster kill mission
			if typeTarget in [TYPE_MONSTERS, TYPE_STONES, TYPE_BOSSES]:
				# Specific monster target
				if vnumTarget != 0 and vnumTarget == monsterVnum:
					categoryName = localeinfo.MISSIONLIST_DAILY_SHORT if category == 0 else localeinfo.MISSIONLIST_WEEKLY_SHORT
					return (progress, maxProgress, categoryName)

				# vnumTarget == 0 means "any monster of this type"
				if vnumTarget == 0 and _IsMonsterMatchingType(monsterVnum, typeTarget):
					categoryName = localeinfo.MISSIONLIST_DAILY_SHORT if category == 0 else localeinfo.MISSIONLIST_WEEKLY_SHORT
					return (progress, maxProgress, categoryName)

	return None


def GetItemMissionProgress(itemVnum):
	"""
	Check if item is a mission submit target.
	Returns (currentProgress, maxProgress, categoryName) or None

	Args:
		itemVnum: The item's VNUM to check

	Returns:
		Tuple of (progress, maxProgress, categoryName) if item is a mission target
		None if item is not a mission target
	"""
	global _missionWindow
	if not _missionWindow:
		return None

	if not hasattr(_missionWindow, 'dictMissionInfo'):
		return None

	for category in [0, 1]:
		for index in [0, 1, 2]:
			if category not in _missionWindow.dictMissionInfo:
				continue
			if index not in _missionWindow.dictMissionInfo[category]:
				continue
			if "info" not in _missionWindow.dictMissionInfo[category][index]:
				continue

			info = _missionWindow.dictMissionInfo[category][index]["info"]
			if len(info) < 5:
				continue

			typeTarget = info[0]
			vnumTarget = info[1]
			progress = info[2]
			maxProgress = info[3]
			isCollected = info[4]

			if isCollected:
				continue

			# Check if this is an item submit mission
			if typeTarget == TYPE_USE_ITEM:
				if vnumTarget == itemVnum:
					categoryName = localeinfo.MISSIONLIST_DAILY_SHORT if category == 0 else localeinfo.MISSIONLIST_WEEKLY_SHORT
					return (progress, maxProgress, categoryName)

	return None


def HasActiveMissions():
	"""Check if there are any active (non-completed) missions."""
	global _missionWindow
	if not _missionWindow:
		return False

	if not hasattr(_missionWindow, 'dictMissionInfo'):
		return False

	for category in [0, 1]:
		for index in [0, 1, 2]:
			if category not in _missionWindow.dictMissionInfo:
				continue
			if index not in _missionWindow.dictMissionInfo[category]:
				continue
			if "info" not in _missionWindow.dictMissionInfo[category][index]:
				continue

			info = _missionWindow.dictMissionInfo[category][index]["info"]
			if len(info) < 5:
				continue

			isCollected = info[4]
			if not isCollected:
				return True

	return False
