# coding: utf-8
#
# Combat Points - Client-side gear CP lookup
# Mirrors server gear_cp.txt for item tooltip display
#

import app

GEAR_CP_TABLE = {}

# Standard upgrade multiplier +0..+9 (must match server)
STANDARD_MULTIPLIER = [1.00, 1.08, 1.17, 1.28, 1.40, 1.55, 1.73, 1.94, 2.20, 2.50]

# Pendant upgrade multiplier +0..+25 (must match server)
PENDANT_MULTIPLIER = []

# Pendant subtypes (must match server ARMOR_PENDANT_* values)
PENDANT_SUBTYPES = (7, 8, 9, 10, 11, 12, 13, 14)

def _BuildPendantMultiplier():
	global PENDANT_MULTIPLIER
	maxBonus = 5.0
	exponent = 1.25
	maxLevel = 25
	PENDANT_MULTIPLIER = []
	for i in xrange(maxLevel + 1):
		ratio = float(i) / float(maxLevel)
		PENDANT_MULTIPLIER.append(1.0 + (maxBonus - 1.0) * (ratio ** exponent))

_BuildPendantMultiplier()

def LoadGearCPTable(filename="gear_cp.txt"):
	global GEAR_CP_TABLE
	GEAR_CP_TABLE = {}

	try:
		f = open(filename, "r")
	except IOError:
		return False

	for line in f:
		line = line.strip()
		if not line or line.startswith("#"):
			continue

		parts = line.split()
		if len(parts) < 2:
			continue

		try:
			vnum = int(parts[0])
			baseCP = int(parts[1])
			GEAR_CP_TABLE[vnum] = baseCP
		except ValueError:
			continue

	f.close()
	return True

def GetItemGearCP(itemVnum, itemSubType=0):
	"""Returns the GearCP contribution of a single item.
	Walks back from itemVnum to find the base +0 vnum in the table."""
	if not GEAR_CP_TABLE:
		return 0

	maxRefine = 25 if itemSubType in PENDANT_SUBTYPES else 9

	for refineLevel in xrange(0, maxRefine + 1):
		baseVnum = itemVnum - refineLevel
		if baseVnum in GEAR_CP_TABLE:
			baseCP = GEAR_CP_TABLE[baseVnum]

			if itemSubType in PENDANT_SUBTYPES:
				multiplier = PENDANT_MULTIPLIER[min(refineLevel, 25)]
			else:
				multiplier = STANDARD_MULTIPLIER[min(refineLevel, 9)]

			return int(baseCP * multiplier)

	return 0
