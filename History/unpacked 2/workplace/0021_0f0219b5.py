# coding: latin_1

import app, dbg

if __DEBUG__:
	import time

craftingDict = {}
npcOriginDict = {}
shopDict = {}
itemShopDict = {}

# Shop NPC vnums the wiki must not list (USE_EXTENDED_WIKI_SHOP):
# shop_table_ex groups whose "Group ShopNPC" entry points at no NPC standing
# in the world -- remote shops (NPC column 0) and shops opened by a use-item.
# Baked into wiki_shop_hidden.txt by tools/wiki server to client/convert.py.
shopHiddenNpcSet = set()

# Wiki spawn map view (ENABLE_INGAME_WIKI):
#   mobSpawnDict[vnum] -> [ {map, x, y, type}, ... ]
#       Built by tools/wiki_spawn_baker/bake.py from server regen files.
#   mapSizeDict[map_name] -> (tiles_x, tiles_y)
#       Parsed from atlasinfo.txt -- needed by the spawn map widget to convert
#       world coordinates to pixel positions on the minimap atlas.
mobSpawnDict = {}
mapSizeDict = {}

# Wiki drop-chance tags (ENABLE_INGAME_WIKI):
#   mobDropDict[mob_vnum] -> { item_vnum: chance_ppm }
#       1,000,000 PPM = 100% drop (neutral base rate). Built by
#       tools/wiki_drop_baker/bake.py from mob_drop_item.txt, covering all
#       group types (interval / drop / limit / kill). Empty when the bake
#       file is absent; the wiki just won't show tier tags.
mobDropDict = {}

# Wiki drop-source class (ENABLE_INGAME_WIKI):
#   mobClassDict[mob_vnum] -> source_class_id (0 regular, 1 stone, 2 miniboss,
#       3 boss, 4 world boss). Built alongside mobDropDict by wiki_drop_baker
#       from mob_proto Rank+Type. Lets the wiki tier the SAME drop % rarer for
#       low-kill-volume sources (a 2.5% boss drop is rarer than 2.5% on a stone
#       you break thousands of). Missing mob -> treated as regular (class 0).
mobClassDict = {}

# Wiki stone damage-cap table (ENABLE_STONE_DAMAGE_LIMIT):
#   stoneCapDict[vnum] -> [warrior, assassin, sura, shaman] (JOB enum order).
#   stoneCapDefaults -> same 4-element shape, used for stones absent from
#       the table. Built offline by tools/stone_cap_baker/bake.py from the
#       server's stone_damage_limit.json. Fail-soft: missing file leaves
#       GetStoneCaps returning None.
stoneCapDict = {}
stoneCapDefaults = []

# Wiki "Used for Refining" reverse index (USE_REFINE_PROTO_TXT):
#   refineReverseDict[material_vnum] -> [refined_output_vnum, ...]
#       Built offline by tools/wiki_refine_baker/bake.py from server-side
#       refine_proto.txt + item_proto.txt. Empty until that bake runs AND
#       the USE_REFINE_PROTO_TXT define is enabled.
refineReverseDict = {}

# Item-transformation table (ENABLE_ITEM_TRANSFORM):
#   itemTransformDict[input_vnum] -> {"count": n, "result": vnum, "resultCount": n}
#       Built offline by tools/wiki_transform_baker/bake.py from the server's
#       item_transform.txt. Powers the tooltip "Nx <item> will transform into:"
#       preview (uitooltip.py). Fail-soft: missing JSON just hides the preview.
itemTransformDict = {}

# Blend-item display table (__EXTENDED_BLEND_AFFECT__):
#   blendDict[item_vnum] -> {"a": apply_index, "v": value, "d": duration_sec}
#       Built offline by tools/blend_baker/bake.py from the server's blend.txt.
#       Lets blend tooltips show the effect + duration when the item has no rolled
#       sockets (NPC shop / item-mall preview show the bare proto vnum -> all-zero
#       sockets -> blank effect). Fail-soft: missing JSON just falls back to the
#       old blank behaviour.
blendDict = {}

# Bundle-box contents table (wiki Task 6/7):
#   bundleBoxDict[box_vnum] -> {"categories": [{"label", "pick", "items": [[vnum,count,sex,job], ...]}, ...],
#                               "guaranteed": [[vnum, count], ...]}
#   Built offline by the bundle-box baker from the server's bundle_box config.
#   Powers the wiki "Contents" section on the box's own item page plus the
#   "Contained in bundle" reverse links on each contained item's page
#   (ingamewikireverse.GetBundleSources). Fail-soft: missing JSON just means
#   neither section renders -- the rest of the wiki still works.
bundleBoxDict = {}

autoChestDict = {}
autoChestInterval = 1200

# Growth-mount requirement table (ENABLE_GROWTH_MOUNT):
#   growthMountData = {"expItems": [[vnum, exp], ...],
#                      "levelExp": {level: exp},
#                      "levelCost": {target: {"gold": g, "mats": [[vnum, count], ...]}},
#                      "skills": [{target: {"chance": c, "mats": [...]}}] * 4}
#       Built offline by tools/growth_mount_baker/bake.py from the server's
#       growth_mount.txt. Fail-soft: empty dict -> the ride help falls back to
#       the uicompanionride constants.
growthMountData = {}

teleportData = None

def GetBlendInfo(vnum):
	# Returns (apply_index, value, duration_sec) or None. Fail-soft by design.
	try:
		info = blendDict.get(int(vnum))
	except (TypeError, ValueError):
		return None
	if not info:
		return None
	return (info.get("a", 0), info.get("v", 0), info.get("d", 0))

def GetStoneCaps(vnum):
	try:
		row = stoneCapDict.get(int(vnum))
	except (TypeError, ValueError):
		return None
	if row:
		return row
	if len(stoneCapDefaults) == 4:
		return stoneCapDefaults
	return None

def Load():
	if __DEBUG__:
		start_time = time.time()

	fileName = "npc_origin.txt"

	try:
		file = open(fileName, "rb")
		data = file.read()
		file.close()

		global npcOriginDict
		npcOriginDict = eval(data)
	except:
		dbg.LogBox("{} cannot be loaded.".format(fileName))
		app.Abort()

	if app.USE_CRAFT_ITEM_SYSTEM:
		fileName = "cl_craft_item.json"

		try:
			file = open(fileName, "rb")
			data = file.read()
			file.close()

			global craftingDict
			craftingDict = eval(data)
		except:
			dbg.LogBox("{} cannot be loaded.".format(fileName))
			app.Abort()

	fileName = "shops.txt"

	try:
		file = open(fileName, "rb")
		data = file.read()
		file.close()

		global shopDict
		shopDict = eval(data)
	except:
		dbg.LogBox("{} cannot be loaded.".format(fileName))
		app.Abort()

	if app.ENABLE_ITEM_SHOPS:
		# Item-triggered shops: { item_vnum : {"shop_vnum":X, "items":[...]} } for the wiki
		# "Shop Items" page. Fail-soft: a missing file just leaves the page empty; the
		# rest of the wiki/client still works (don't Abort like the mandatory shops.txt).
		try:
			file = open("item_shops.txt", "rb")
			data = file.read()
			file.close()

			global itemShopDict
			itemShopDict = eval(data)
		except:
			itemShopDict = {}

	if app.USE_EXTENDED_WIKI_SHOP:
		# Fail-soft: a missing file just restores the old behaviour of giving
		# every shopDict key its own wiki category, placeholder NPCs included.
		try:
			file = open("wiki_shop_hidden.txt", "rb")
			data = file.read()
			file.close()

			global shopHiddenNpcSet
			shopHiddenNpcSet = set(eval(data))
		except:
			shopHiddenNpcSet = set()

	try:
		file = open("cl_auto_chest.json", "rb")
		data = file.read()
		file.close()

		global autoChestDict
		global autoChestInterval
		raw = eval(data)
		autoChestDict = {}
		autoChestInterval = int(raw.get("interval", 1200))
		for vnumKey, amounts in raw.get("chests", {}).iteritems():
			try:
				autoChestDict[int(vnumKey)] = [int(a) for a in amounts]
			except (TypeError, ValueError):
				continue
	except:
		autoChestDict = {}
		autoChestInterval = 1200

	if app.ENABLE_INGAME_WIKI:
		# Spawn coordinate data (mobs / bosses / stones / NPCs) for the wiki
		# spawn map view. Fail-soft: a missing file just hides the spawn map;
		# the rest of the wiki still works.
		try:
			file = open("cl_mob_spawn.json", "rb")
			data = file.read()
			file.close()

			global mobSpawnDict
			# JSON forces string keys; convert to int so int-vnum lookups work
			# the same way as npcOriginDict (which is a Python literal with int
			# keys). Without this, mobSpawnDict.get(int_vnum) always returns [].
			raw = eval(data)
			mobSpawnDict = {}
			for k, v in raw.iteritems():
				try:
					mobSpawnDict[int(k)] = v
				except (TypeError, ValueError):
					pass
		except:
			mobSpawnDict = {}

		# Drop-chance data for the wiki's monster-drop tier tags. Same
		# fail-soft pattern -- missing file just means no tier tags.
		# Outer keys: mob vnum (int). Inner keys: item vnum (int).
		# Values: chance in PPM (1,000,000 = 100%).
		try:
			file = open("cl_mob_drop.json", "rb")
			data = file.read()
			file.close()

			global mobDropDict
			raw = eval(data)
			mobDropDict = {}
			for mobKey, itemMap in raw.iteritems():
				try:
					mob_vnum = int(mobKey)
				except (TypeError, ValueError):
					continue
				inner = {}
				if isinstance(itemMap, dict):
					for itemKey, ppm in itemMap.iteritems():
						try:
							inner[int(itemKey)] = int(ppm)
						except (TypeError, ValueError):
							continue
				if inner:
					mobDropDict[mob_vnum] = inner
		except:
			mobDropDict = {}

		# Drop-source class per mob (stone / boss / ...). Same fail-soft
		# pattern; missing file -> every mob defaults to regular at lookup.
		try:
			file = open("cl_mob_class.json", "rb")
			data = file.read()
			file.close()

			global mobClassDict
			raw = eval(data)
			mobClassDict = {}
			for mobKey, classId in raw.iteritems():
				try:
					mobClassDict[int(mobKey)] = int(classId)
				except (TypeError, ValueError):
					continue
		except:
			mobClassDict = {}

		# Per-class per-hit damage caps for wiki stone pages. Same fail-soft
		# pattern; rows are JOB order: warrior, assassin, sura, shaman.
		try:
			file = open("cl_stone_caps.json", "rb")
			data = file.read()
			file.close()

			global stoneCapDict, stoneCapDefaults
			raw = eval(data)
			stoneCapDict = {}
			stoneCapDefaults = []
			for key, row in raw.iteritems():
				try:
					if key == "defaults":
						stoneCapDefaults = [int(x) for x in row]
					else:
						stoneCapDict[int(key)] = [int(x) for x in row]
				except (TypeError, ValueError):
					continue
		except:
			stoneCapDict = {}
			stoneCapDefaults = []

		# Bundle-box contents (wiki "Contents" section + reverse "Contained in
		# bundle" links). Same fail-soft pattern; missing file just means
		# neither wiki surface renders for any box.
		try:
			file = open("cl_bundle_box.json", "rb")
			data = file.read()
			file.close()

			global bundleBoxDict
			raw = eval(data)
			bundleBoxDict = {}
			for boxKey, boxData in raw.iteritems():
				try:
					bundleBoxDict[int(boxKey)] = boxData
				except (TypeError, ValueError):
					continue
		except:
			bundleBoxDict = {}

		# Atlas size table -- needed to convert world (cx, cy) to pixel position
		# on the atlas.sub minimap texture. Format per line:
		#   map_name<TAB>base_x<TAB>base_y<TAB>tiles_x<TAB>tiles_y
		# Path matches what the C++ side uses
		# (PythonBackground.cpp -- "locale/common/atlasinfo.txt").
		try:
			file = open("locale/common/atlasinfo.txt", "rb")
			data = file.read()
			file.close()

			global mapSizeDict
			for rawLine in data.splitlines():
				line = rawLine.strip()
				if not line or line.startswith("//"):
					continue
				parts = line.split("\t")
				if len(parts) < 5:
					continue
				name = parts[0].strip()
				try:
					tilesX = int(parts[3])
					tilesY = int(parts[4])
				except ValueError:
					continue
				if name:
					mapSizeDict[name] = (tilesX, tilesY)
		except:
			mapSizeDict = {}

		# atlasinfo.txt is keyed by the CLIENT map names, and for 42 maps those
		# differ from the server folder names the spawn records use (server
		# index 64 is map_n_threeway in the server tree, map_a2 in atlasinfo)
		# or are absent entirely -- those maps got no minimap at all.
		# cl_map_size.json carries the same tile counts read from each map's
		# own Setting.txt, keyed the way the spawn records are. Fill in only
		# what atlasinfo could not name: the two agree on all 128 maps they
		# share, so nothing that already worked changes.
		try:
			file = open("cl_map_size.json", "rb")
			data = file.read()
			file.close()

			for name, size in eval(data).iteritems():
				if name in mapSizeDict:
					continue
				try:
					mapSizeDict[name] = (int(size[0]), int(size[1]))
				except (TypeError, ValueError, IndexError):
					continue
		except:
			pass

	if app.USE_REFINE_PROTO_TXT:
		# Wiki reverse-lookup: which items can be REFINED using this vnum as
		# a material. Baked offline (tools/wiki_refine_baker) from server's
		# refine_proto.txt + item_proto.txt. Fail-soft: if the JSON is
		# missing the "Used for Refining" column just stays empty -- nothing
		# else in the wiki depends on it.
		try:
			file = open("cl_refine_reverse.json", "rb")
			data = file.read()
			file.close()

			global refineReverseDict
			raw = eval(data)
			refineReverseDict = {}
			for k, v in raw.iteritems():
				try:
					refineReverseDict[int(k)] = v
				except (TypeError, ValueError):
					pass
		except:
			refineReverseDict = {}

	if app.USE_PORTABLE_TELEPORT_WITH_UI:
		# Teleport panel data (tools/teleport_baker). Fail-soft: missing file
		# opens the window with the bare atlas and no regions.
		try:
			file = open("cl_teleport.json", "rb")
			data = file.read()
			file.close()

			global teleportData
			teleportData = eval(data)
		except:
			teleportData = None

	# Item-transformation preview data (ENABLE_ITEM_TRANSFORM). Baked offline
	# (tools/wiki_transform_baker) from the server's item_transform.txt.
	# Fail-soft: if the JSON is missing the tooltip preview just stays hidden.
	try:
		file = open("cl_item_transform.json", "rb")
		data = file.read()
		file.close()

		global itemTransformDict
		raw = eval(data)
		itemTransformDict = {}
		for k, v in raw.iteritems():
			try:
				itemTransformDict[int(k)] = v
			except (TypeError, ValueError):
				pass
	except:
		itemTransformDict = {}

	# Blend display table (__EXTENDED_BLEND_AFFECT__). Baked offline
	# (tools/blend_baker) from the server's blend.txt. Fail-soft: if the JSON is
	# missing, blend tooltips just keep the old blank-in-shop behaviour.
	try:
		file = open("cl_blend.json", "rb")
		data = file.read()
		file.close()

		global blendDict
		raw = eval(data)
		blendDict = {}
		for k, v in raw.iteritems():
			try:
				blendDict[int(k)] = v
			except (TypeError, ValueError):
				pass
	except:
		blendDict = {}

	# Growth-mount requirement data (ENABLE_GROWTH_MOUNT). Baked offline
	# (tools/growth_mount_baker) from the server's growth_mount.txt. Fail-soft:
	# if the JSON is missing the ride help falls back to the client constants.
	try:
		file = open("cl_growth_mount.json", "rb")
		data = file.read()
		file.close()

		global growthMountData
		raw = eval(data)
		levelExp = {}
		for k, v in raw["levelExp"].iteritems():
			levelExp[int(k)] = int(v)
		levelCost = {}
		for k, v in raw["levelCost"].iteritems():
			levelCost[int(k)] = v
		skills = []
		for skillMap in raw["skills"]:
			perLevel = {}
			for k, v in skillMap.iteritems():
				perLevel[int(k)] = v
			skills.append(perLevel)
		growthMountData = {"expItems": raw["expItems"], "levelExp": levelExp, "levelCost": levelCost, "skills": skills}
	except:
		growthMountData = {}

	if __DEBUG__:
		print "--- game_data::Load(): loaded in %s second(s) ---" % (time.time() - start_time)
