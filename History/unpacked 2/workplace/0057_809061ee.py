# coding: latin_1
#
# "What upgrade does this item feed?" -- the system-usage rows in the wiki's
# buy column. Answers, for a material vnum, which growth-pet / buffi / growth-
# mount step consumes it.
#
# Every source here is already client-side, so this is a pure local reverse
# index with no network round trip:
#   pet Type / skill  -> app.GetPetTypeUpgradeReq / app.GetPetSkillUpgradeReq
#                        (srcs/share/growth_pet_tables.hpp -- the same tables
#                        the server consumes, so no pet need be summoned)
#   pet stat potions  -> uicompanion.PET_STAT_POTION_VNUMS
#   pet evolution     -> uipetinfo.EVOLVE_MATERIALS_DICT
#   buffi evolution   -> app.GetBuffiEvolveInfo  (srcs/share/buffi.hpp)
#   growth mount      -> game_data.growthMountData  (cl_growth_mount.json)
#
# Each source is independently guarded: a flag that is off, a module that fails
# to import, or an empty table contributes nothing instead of raising. A wiki
# page must never fail to open because a companion system is disabled.

import app

if app.ENABLE_INGAME_WIKI and app.USE_EXTENDED_WIKI_USAGE:
	import localeinfo


	def LocaleText(key, default):
		# localeinfo's wrapper returns "Locale not found: KEY" rather than
		# raising, so a bare getattr default never fires.
		value = getattr(localeinfo, key, default)
		if not value or value.startswith("Locale not found"):
			return default

		return value


	# System ids -- also select the help popup a row's click opens.
	SYS_PET_TYPE     = "pet_type"
	SYS_PET_SKILL    = "pet_skill"
	SYS_PET_STAT     = "pet_stat"
	SYS_PET_EVOLVE   = "pet_evolve"
	SYS_BUFFI_EVOLVE = "buffi_evolve"
	SYS_MOUNT_LEVEL  = "mount_level"
	SYS_MOUNT_SKILL  = "mount_skill"
	SYS_MOUNT_EXP    = "mount_exp"

	_TAG_KEYS = {
		SYS_PET_TYPE     : ("WIKI_USE_TAG_PET_TYPE",     "[Pet Type]"),
		SYS_PET_SKILL    : ("WIKI_USE_TAG_PET_SKILL",    "[Pet Skill]"),
		SYS_PET_STAT     : ("WIKI_USE_TAG_PET_STAT",     "[Pet Stat]"),
		SYS_PET_EVOLVE   : ("WIKI_USE_TAG_PET_EVOLVE",   "[Pet Evolve]"),
		SYS_BUFFI_EVOLVE : ("WIKI_USE_TAG_BUFFI_EVOLVE", "[Buffi Evolve]"),
		SYS_MOUNT_LEVEL  : ("WIKI_USE_TAG_MOUNT_LEVEL",  "[Mount Level]"),
		SYS_MOUNT_SKILL  : ("WIKI_USE_TAG_MOUNT_SKILL",  "[Mount Skill]"),
		SYS_MOUNT_EXP    : ("WIKI_USE_TAG_MOUNT_EXP",    "[Mount Feed]"),
	}

	# systemId -> (interface method name, mode) for the row click. A system with
	# no dedicated help page maps to None and its rows are informational only.
	_HELP_TARGET = {
		SYS_PET_TYPE     : ("OpenPetUpgradeHelp",   1),   # uipetupgradehelp.MODE_TYPE
		SYS_PET_EVOLVE   : ("OpenPetUpgradeHelp",   0),   # uipetupgradehelp.MODE_EVOLVE
		SYS_PET_STAT     : ("OpenPetHelp",          0),   # uipethelp.MODE_GENERAL
		SYS_PET_SKILL    : ("OpenWikiToGrowthPet",  None),  # wiki Systems > Pet page
		SYS_BUFFI_EVOLVE : ("OpenCompanionHelp",    None),
		SYS_MOUNT_LEVEL  : ("OpenCompanionRideHelp", 0),  # uicompanionridehelp.MODE_LEVEL
		SYS_MOUNT_SKILL  : ("OpenCompanionRideHelp", 1),  # uicompanionridehelp.MODE_SKILL
		SYS_MOUNT_EXP    : ("OpenCompanionRideHelp", 0),
	}

	# vnum -> [ {sys, detail, mats, yang}, ... ]
	_index = None


	def _Add(idx, vnum, count, systemId, detail, mats, yang):
		try:
			vnum = int(vnum)
		except (TypeError, ValueError):
			return
		if not vnum:
			return
		idx.setdefault(vnum, []).append({
			"sys"    : systemId,
			"detail" : detail,
			"mats"   : mats,
			"yang"   : yang,
			"count"  : count,
		})


	def _AddMatList(idx, mats, systemId, detail, yang):
		for pair in (mats or []):
			if not pair:
				continue
			try:
				_Add(idx, pair[0], int(pair[1]), systemId, detail, mats, yang)
			except (TypeError, ValueError, IndexError):
				continue


	def _CollectPet(idx):
		# Type ladder: index 2..GROWTH_PET_MAX_TYPE (the shared table's own cap;
		# the getter clamps, so walking past the end is harmless but pointless).
		if hasattr(app, "GetPetTypeUpgradeReq"):
			detailFmt = LocaleText("WIKI_USE_DETAIL_PET_TYPE", "Type %d")
			for target in xrange(2, 7):
				try:
					(yang, _chance, mats) = app.GetPetTypeUpgradeReq(target)
				except Exception:
					continue
				_AddMatList(idx, mats, SYS_PET_TYPE, detailFmt % target, yang)

		# Skill ladder: target levels 2..20.
		if hasattr(app, "GetPetSkillUpgradeReq"):
			detailFmt = LocaleText("WIKI_USE_DETAIL_PET_SKILL", "Level %d")
			for target in xrange(2, 21):
				try:
					(yang, mats) = app.GetPetSkillUpgradeReq(target)
				except Exception:
					continue
				_AddMatList(idx, mats, SYS_PET_SKILL, detailFmt % target, yang)

		# Stat potions: a forward table of vnums, no counts.
		try:
			import uicompanion
			families = uicompanion.PET_STAT_POTION_VNUMS
		except Exception:
			families = None
		if families:
			statNames = (
				LocaleText("COMPANION_PET_STAT_HP", "Max HP"),
				LocaleText("COMPANION_PET_STAT_ATT", "Attack"),
				LocaleText("COMPANION_PET_STAT_ATTVALUE", "Elemental"),
			)
			for i, family in enumerate(families):
				name = statNames[i] if i < len(statNames) else str(i)
				for vnum in (family or []):
					_Add(idx, vnum, 1, SYS_PET_STAT, name, [], 0)

		# Legacy evolution materials (only defined with the new evolve window).
		try:
			import uipetinfo
			evolve = uipetinfo.EVOLVE_MATERIALS_DICT
		except Exception:
			evolve = None
		if evolve:
			detailFmt = LocaleText("WIKI_USE_DETAIL_EVOLVE", "Evolution %d")
			for stage, mats in evolve.items():
				_AddMatList(idx, mats, SYS_PET_EVOLVE, detailFmt % int(stage), 0)


	def _CollectBuffi(idx):
		if not hasattr(app, "GetBuffiEvolveInfo"):
			return
		detailFmt = LocaleText("WIKI_USE_DETAIL_EVOLVE", "Evolution %d")
		for stage in xrange(1, 4):
			try:
				info = app.GetBuffiEvolveInfo(stage)
			except Exception:
				continue
			if not info or len(info) < 6:
				continue
			yang = info[2]
			mats = info[5]
			_AddMatList(idx, mats, SYS_BUFFI_EVOLVE, detailFmt % stage, yang)


	def _CollectMount(idx):
		try:
			import game_data
			data = game_data.growthMountData or {}
		except Exception:
			return
		if not data:
			return

		# Level-up costs: {targetLevel: {"gold": g, "mats": [[vnum, count], ...]}}
		detailFmt = LocaleText("WIKI_USE_DETAIL_MOUNT_LEVEL", "Level %d")
		for target, cost in (data.get("levelCost") or {}).items():
			if not isinstance(cost, dict):
				continue
			_AddMatList(idx, cost.get("mats"), SYS_MOUNT_LEVEL,
						detailFmt % int(target), cost.get("gold", 0))

		# Skill costs: [ {targetLevel: {"chance": c, "mats": [...]}} ] * 4
		detailFmt = LocaleText("WIKI_USE_DETAIL_MOUNT_SKILL", "Skill %d Lv %d")
		for slot, perLevel in enumerate(data.get("skills") or []):
			if not isinstance(perLevel, dict):
				continue
			for target, step in perLevel.items():
				if not isinstance(step, dict):
					continue
				_AddMatList(idx, step.get("mats"), SYS_MOUNT_SKILL,
							detailFmt % (slot + 1, int(target)), 0)

		# EXP feed items: [[vnum, exp], ...]
		detailFmt = LocaleText("WIKI_USE_DETAIL_MOUNT_EXP", "+%d EXP")
		for pair in (data.get("expItems") or []):
			if not pair:
				continue
			try:
				_Add(idx, pair[0], 1, SYS_MOUNT_EXP, detailFmt % int(pair[1]), [], 0)
			except (TypeError, ValueError, IndexError):
				continue


	def _BuildIndex():
		global _index
		if _index is not None:
			return _index

		idx = {}
		for collect in (_CollectPet, _CollectBuffi, _CollectMount):
			try:
				collect(idx)
			except Exception:
				# One broken system must not cost the others their rows.
				import dbg, traceback
				dbg.TraceError("wiki system-use index: " + traceback.format_exc())

		_index = idx
		return idx


	def GetSystemUsages(vnum):
		"""[{sys, detail, mats, yang, count}, ...] -- every upgrade step that
		consumes this vnum, across pet / buffi / growth mount."""
		try:
			return list(_BuildIndex().get(int(vnum), []))
		except (TypeError, ValueError):
			return []


	def GetRowLabel(usage):
		(key, default) = _TAG_KEYS.get(usage["sys"], ("", ""))
		tag = LocaleText(key, default) if key else ""
		return ("%s %s" % (tag, usage["detail"])).strip()


	def GetRowTooltipLines(usage):
		"""[(text, dim), ...] -- the materials + yang for this upgrade step."""
		import item as itemModule

		lines = []
		mats = usage.get("mats") or []
		if mats:
			lines.append((LocaleText("WIKI_USE_TIP_MATERIALS", "Materials"), False))
			for pair in mats:
				if not pair:
					continue
				try:
					matVnum = int(pair[0])
					matCount = int(pair[1])
				except (TypeError, ValueError, IndexError):
					continue
				if not matVnum or not matCount:
					continue
				try:
					itemModule.SelectItem(matVnum)
					name = itemModule.GetItemName() or ("#%d" % matVnum)
				except Exception:
					name = "#%d" % matVnum
				lines.append(("%dx %s" % (matCount, name), True))

		yang = usage.get("yang") or 0
		if yang:
			lines.append((LocaleText("WIKI_USE_TIP_YANG", "Yang: %s") % _Thousands(yang), True))

		if _HELP_TARGET.get(usage["sys"]):
			lines.append((LocaleText("WIKI_USE_TIP_OPEN_HELP",
									 "Click to open the system guide"), True))

		return lines


	def _Thousands(value):
		try:
			s = str(long(value))
		except (TypeError, ValueError):
			return str(value)
		out = ""
		while len(s) > 3:
			out = "," + s[-3:] + out
			s = s[:-3]
		return s + out


	def MakeHelpAction(systemId):
		"""Zero-arg callable opening this system's help popup, or None."""
		target = _HELP_TARGET.get(systemId)
		if not target:
			return None

		(methodName, mode) = target

		def _open():
			try:
				import systemSetting
				iface = systemSetting.GetInterfaceHandler()
			except Exception:
				return
			if not iface:
				return
			method = getattr(iface, methodName, None)
			if not method:
				return
			try:
				if mode is None:
					method()
				else:
					method(mode)
			except Exception:
				pass

		return _open
