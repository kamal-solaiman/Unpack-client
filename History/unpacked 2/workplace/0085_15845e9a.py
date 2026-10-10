# coding: latin_1
#
# Location Scroll (ENABLE_LOCATION_SCROLL_REWORK) - client-side label store.
#
# The label is cosmetic, so it lives on the client instead of costing a player table, a GD/DG
# packet pair and a GC sync packet. It is keyed by the saved COORDINATE rather than by item id:
# the client never learns an item's server id, and coordinate keying means a stack of 200 scrolls
# saved at one spot resolves to a single label, the label survives the scroll being spent, and the
# label never has to take part in stack identity.
#
# Format is one "x,y=name" per line - deliberately not eval()/pickle, which would execute whatever
# happens to be sitting in the file.

import math
import os

import app
import background
import item
import localeinfo
import player

FOLDER_PATH = "UserData/locationscroll/"

# Mirror srcs/share/m2_length.hpp. Keep in step with it.
PORTAL_MEMORY = 2
NAME_MAX_LEN = 24
MIN_DIST = 5000
BULK_MAX = 200

_names = {}
_loadedFor = None


def _Key(x, y):
	return "%d,%d" % (int(x), int(y))


def _FilePath(charName):
	return FOLDER_PATH + "%s.cfg" % (charName)


def Load(charName):
	global _names, _loadedFor

	_names = {}
	_loadedFor = charName

	if not charName:
		return

	filePath = _FilePath(charName)

	if not os.path.exists(filePath):
		return

	try:
		f = old_open(filePath, "rb")
		data = f.read()
		f.close()
	except:
		return

	for line in data.splitlines():
		line = line.strip()

		# A malformed line is skipped, never fatal - the file is user-editable by hand.
		if not line or line.startswith("#"):
			continue

		sep = line.find("=")

		if sep <= 0:
			continue

		_names[line[:sep].strip()] = line[sep + 1:].strip()


def _EnsureLoaded():
	global _loadedFor

	charName = player.GetMainCharacterName()

	if charName != _loadedFor:
		Load(charName)


def Save():
	if not _loadedFor:
		return

	try:
		if not os.path.exists(FOLDER_PATH):
			os.makedirs(FOLDER_PATH)

		f = old_open(_FilePath(_loadedFor), "wb")
		f.write("# Location Scroll labels - one x,y=name per line\n")

		for key, name in _names.items():
			f.write("%s=%s\n" % (key, name))

		f.close()
	except:
		pass


def GetName(x, y):
	if not x and not y:
		return ""

	_EnsureLoaded()
	return _names.get(_Key(x, y), "")


def SetName(x, y, name):
	if not x and not y:
		return

	_EnsureLoaded()

	# "|" would let a label inject a colour code or a hyperlink tag into any UI that renders it.
	name = name.replace("|", "").strip()[:NAME_MAX_LEN]

	if not name:
		ClearName(x, y)
		return

	_names[_Key(x, y)] = name
	Save()


def ClearName(x, y):
	_EnsureLoaded()

	key = _Key(x, y)

	if key in _names:
		del _names[key]
		Save()


def IsLocationScroll(itemVnum):
	if not itemVnum:
		return False

	item.SelectItem(itemVnum)

	if item.GetItemType() != item.ITEM_TYPE_USE:
		return False

	if item.GetItemSubType() != item.USE_TALISMAN:
		return False

	return item.GetValue(0) == PORTAL_MEMORY


def _L(key, fallback):
	return getattr(localeinfo, key, fallback)


def GetSavedPosition(metinSlot):
	"""(x, y) held by this scroll, or (0, 0) when it is blank."""
	if not metinSlot:
		return (0, 0)

	try:
		return (int(metinSlot[0]), int(metinSlot[1]))
	except (TypeError, ValueError, IndexError):
		return (0, 0)


def GetDistanceTo(x, y):
	"""World-unit distance from the player to (x, y), or -1 when unknown."""
	try:
		(px, py, pz) = player.GetMainCharacterPosition()
	except:
		return -1

	return math.sqrt((float(x) - px) ** 2 + (float(y) - py) ** 2)


def DescribePosition(x, y):
	"""(localised map name, local x, local y). Map name is "" when unmapped."""
	(mapName, xBase, yBase) = background.GlobalPositionToMapInfo(x, y)
	localeMapName = localeinfo.MINIMAP_ZONE_NAME_DICT.get(mapName, "")

	return (mapName, localeMapName, int(x - xBase) / 100, int(y - yBase) / 100)


def OverrideTitle(tooltip, metinSlot):
	"""Replace the scroll's displayed name with the player's own label.

	Returns True when a label was applied, so the caller skips the stock title.
	"""
	(xPos, yPos) = GetSavedPosition(metinSlot)

	if not xPos and not yPos:
		return False

	name = GetName(xPos, yPos)

	if not name:
		return False

	tooltip.SetTitle(name)
	return True


def AppendTooltip(tooltip, metinSlot):
	"""Render the location-scroll block into an open item tooltip."""
	(xPos, yPos) = GetSavedPosition(metinSlot)

	tooltip.AppendSpace(8)

	if not xPos and not yPos:
		tooltip.AppendTextLine(_L("LOCSCROLL_EMPTY", "No location saved."), tooltip.NORMAL_COLOR)
		tooltip.AppendTextLine(_L("LOCSCROLL_HINT_BULK", "Alt + Click to bulk save position"),
			tooltip.DISABLE_COLOR)
		return

	# The label is the tooltip title (see OverrideTitle), so it is not repeated here.
	(mapName, localeMapName, localX, localY) = DescribePosition(xPos, yPos)

	if localeMapName:
		tooltip.AppendTextLine(localeinfo.TOOLTIP_MEMORIZED_POSITION % (localeMapName, localX, localY),
			tooltip.NORMAL_COLOR)
	else:
		tooltip.AppendTextLine(localeinfo.TOOLTIP_MEMORIZED_POSITION_ERROR % (localX, localY),
			tooltip.NORMAL_COLOR)

	# The atlas renderer ships with the wiki; without it the tooltip stays text-only.
	if app.ENABLE_INGAME_WIKI:
		try:
			import ingamewikispawn
			# coords are local map units / 100 - the same scale the line above prints.
			ingamewikispawn.RenderMiniMapIntoTooltip(tooltip, mapName, [(localX, localY)])
		except:
			pass

	dist = GetDistanceTo(xPos, yPos)

	if dist >= 0:
		if dist < MIN_DIST:
			tooltip.AppendTextLine(_L("LOCSCROLL_TOO_CLOSE", "Too close to use from here."),
				tooltip.NEGATIVE_COLOR)
		else:
			tooltip.AppendTextLine(_L("LOCSCROLL_DISTANCE", "%s units away") % _Grouped(int(dist)),
				tooltip.NORMAL_COLOR)

	tooltip.AppendSpace(8)
	tooltip.AppendTextLine(_L("LOCSCROLL_HINT_RENAME", "Ctrl + Click to rename"), tooltip.DISABLE_COLOR)
	tooltip.AppendTextLine(_L("LOCSCROLL_HINT_CLEAR", "Shift + Click to clear location"),
		tooltip.DISABLE_COLOR)
	tooltip.AppendTextLine(_L("LOCSCROLL_HINT_RESAVE", "Alt + Click to save here instead"),
		tooltip.DISABLE_COLOR)


def _Grouped(n):
	s = str(int(n))
	out = ""

	while len(s) > 3:
		out = "," + s[-3:] + out
		s = s[:-3]

	return s + out
