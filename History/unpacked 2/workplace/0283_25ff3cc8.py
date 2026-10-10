# coding: utf-8
#
# Horse Upgrade - Client-side mission config loader.
# Mirrors the server-side share/systems/horse_upgrade/horse_upgrade.txt mission list
# so the UI (tooltip + mission window) can render mission details locally
# without an extra packet round-trip for static data.
#
# Loads data/horse_upgrade/horse_upgrade.txt into a dict-of-dicts and caches
# it after the first call. Python 2.7.

import app
import item

_cache = None

# Map config-file APPLY names to the integer values the client uses for
# affect-string lookups (item.APPLY_*). The server-side parser uses
# FN_get_apply_type which expects APPLY_* names, so the txt files use APPLY_*.
# These must match the dict keys built by ItemToolTip.AFFECT_DICT in
# uitooltip.py — otherwise GET_AFFECT_STRING falls back to "UNKNOWN_TYPE".
def _safe(name):
	return getattr(item, name, 0)

APPLY_TYPE_IDS = {
	"ATTBONUS_STONE":   _safe("APPLY_ATTBONUS_STONE"),
	"ATTBONUS_BOSS":    _safe("APPLY_ATTBONUS_BOSS"),
	"ATTBONUS_MONSTER": _safe("APPLY_ATTBONUS_MONSTER"),
	"MAX_HP":           _safe("APPLY_MAX_HP"),
}

def _ParseFile(path):
	missions = {}
	try:
		f = open(path, "r")
	except IOError:
		return missions

	text = f.read()
	f.close()

	tokens = text.replace("{", " { ").replace("}", " } ").split()
	i = 0
	cur_mission = None
	cur_data = None
	while i < len(tokens):
		t = tokens[i]
		if t == "Group":
			if i + 1 < len(tokens):
				name = tokens[i+1]
				if name.startswith("Mission"):
					cur_mission = int(name[len("Mission"):])
					cur_data = {"rewards": []}
					missions[cur_mission] = cur_data
				i += 2
			else:
				i += 1
			continue
		if t == "{" or t == "}":
			i += 1
			continue
		key = t
		# RewardN keys take TWO tokens (apply-name + numeric value), space-separated:
		#   Reward1  POINT_ATTBONUS_STONE  1
		if key.startswith("Reward") and i + 2 < len(tokens):
			apply_name = tokens[i + 1]
			try:
				reward_value = int(tokens[i + 2])
			except ValueError:
				reward_value = 0
			if cur_data is not None:
				cur_data["rewards"].append({
					"apply_type":  APPLY_TYPE_IDS.get(apply_name, 0),
					"apply_name":  apply_name,
					"value":       reward_value,
				})
			i += 3
			continue
		if i + 1 >= len(tokens):
			i += 1
			continue
		# Quoted compound value (legacy format) — kept for backward compat.
		if tokens[i+1].startswith('"'):
			j = i + 1
			buf = tokens[j]
			while not tokens[j].endswith('"') or (j == i+1 and len(tokens[j]) == 1):
				j += 1
				if j >= len(tokens):
					break
				buf += " " + tokens[j]
			val = buf.strip('"')
			i = j + 1
		else:
			val = tokens[i+1]
			i += 2
		if cur_data is None:
			continue
		try:
			cur_data[key] = int(val)
		except ValueError:
			cur_data[key] = val
	return missions

def GetMission(n):
	global _cache
	if _cache is None:
		_cache = _ParseFile("horse_upgrade/horse_upgrade.txt")
	return _cache.get(n, None)

def GetAllMissions():
	global _cache
	if _cache is None:
		_cache = _ParseFile("horse_upgrade/horse_upgrade.txt")
	return _cache
