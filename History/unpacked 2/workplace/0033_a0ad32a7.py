# coding: latin_1

import app
import player
import net

import localeinfo

IS_TEST_SERVER = 1

BOSS_CHEST_VNUMS = [
50288,53587,54701,53586,54700,
33330,33331,33332,33333,33334,33335,33336,33337,33338,33339,
33064,54703,33344,33345,54702,33342,33343,54704,33348,33349,
50270,33352,33353,71775,71776
]

# Metin-stone vnum lists for the redesigned wiki sub-categories.
# Lists are populated manually -- no level-based filtering. Empty lists
# render as an empty panel (the wiki redesign's bossWindow swap accepts
# an empty list and just shows no rows). Edit these freely.
STONE_TIER1_VNUMS = [8085,8086,8087,range(8001,8020)]   # Field Metin Stones (Low)
STONE_TIER2_VNUMS = [range(8025,8028)]   # Field Metin Stones (Medium)
STONE_TIER3_VNUMS = [range(8051,8059)]   # Field Metin Stones (High)
STONE_CHAOS_VNUMS = [range(8700,8707)]   # Chaos Metin Stones
STONE_EVENT_VNUMS = [range(8257,8260),range(8041,8051)]   # Event Metin Stones

# Boss vnum lists for the redesigned wiki sub-categories. Same pattern
# as the stones above: each entry can be a bare vnum or a range(a,b);
# the _BossShowRedesign hook flattens one level. Only vnums listed here
# show up in the corresponding sub-category -- no engine-side filtering.
# Edit freely; an empty list just renders an empty panel.
BOSS_TIER1_VNUMS = [
	# First City
	155,    # Li-An
	191,    # Lycos
	193,    # Bera
	194,    # Tigress
	# Second City
	591,    # Wild Leader
	533,    # Wild Archer
	492,    # Bo
	491,    # Mahon
	493,    # Go-Bi
	534,    # Wild Specialist
	532,    # Wild Maniac
	531,    # Wild Soldier
	494,    # Shoo-ng
]
BOSS_TIER2_VNUMS = [
	# Valley
	531,    # Wild Soldier        (also in Tier 1)
	534,    # Wild Specialist     (also in Tier 1)
	532,    # Wild Maniac         (also in Tier 1)
	533,    # Wild Archer         (also in Tier 1)
	601,    # Ghoul
	602,    # Ghoul Spy
	603,    # Ghoul Fighter
	604,    # Ghoul Sorcerer
	691,    # Super Ghoul
	# Temple
	791,    # Evil Leader
	993,    # Giant Rabies Carrier
	1304,   # Yellow Tiger Spirit
	# Mt Sohan
	6433,   # Big Ice Witch
	1901,   # Nine Tails
	# Desert
	2191,   # Big Desert Turtle
	2192,   # Dark Desert Turtle
	# Land of Fire
	2291,   # Red Dragon
	2206,   # Fire King
	# Spider Queen
	2091,   # Spider Queen
]
BOSS_TIER3_VNUMS = [
	# Ghost Forest
	2306,   # Old Ghost Tree
	# Red Forest
	2307,   # Master Ghost Tree
	# Curse Cave
	2495,   # General Hwa-Shin
]
BOSS_TIER4_VNUMS = [
	# Tier 4 = level 90 maps. 4599 spawns on all four maps below; 3590
	# spawns on Dragon Rock + Nephrite Bay. Listed once each (AddItem
	# dedupes by vnum anyway).
	# Dragon Rock + Nephrite Bay + Thunder Mountains + Guatama Cliff
	4599,   # Dannan, Treasure Guardian (multi-map)
	# Dragon Rock + Nephrite Bay
	3590,   # Bone Face (multi-map)
	# Dragon Rock
	3090,   # Lord Genis
	3290,   # Rakshasa
	3091,   # Genis High Guardian
	3291,   # Martyaxwar
	# Nephrite Bay
	3591,   # Red Leader
	3491,   # Triton
	3490,   # General Kelba
	3691,   # Crab King
	3690,   # General Lobster
	# Thunder Mountains
	3791,   # King Wooba
	3190,   # Argis
	3595,   # Bloody Bone Face
	3596,   # Bloody Red Leader
	3790,   # Gargamel
	3191,   # Polyphemus
	# Guatama Cliff
	3891,   # Big Ghoul
	3890,   # Captain Shrook
	3391,   # Lemurian Bodyguard
	3390,   # Lemurian Prince
	# Enchanted Forest
	6407,   # Antai Ruler
]
BOSS_DUNGEON_MINI_VNUMS  = [694,1093,2092,2598,2493,5623,6191,6091]   # Dungeon mini bosses (populate manually)
BOSS_DUNGEON_VNUMS       = [694,1093,2092,2598,2493,5623,6191,6091]   # Dungeon bosses (populate manually)
BOSS_SPECIAL_VNUMS       = []   # Special bosses (populate manually)
EVENT_CHEST_VNUMS = [50011,50265,50269,50268,50267,50930,50929,50928,50037,50920]
ALT_CHEST_VNUMS = [range(50187,50197),range(50109,50116),70711,70713,
50070,50073,50076,50077,50078,50079,50125,50121,70712,70714,70722,55009,50036,50285,
25107,27987,
30093,30094,30095,30096,30097,30098,30099,30100,31238,38050,50182,50252,
51501,51511,51512,51513,51514,51515,51516,51517,51518,51519,51520,51521,51522,51547,51549,51550,
60600,60602,60603,60604,60605,60608,60610,70451,70715,70732,70733,
71150,71168,71770,71771,71772,72058,
83001,83002,83003,83011,83014,83016,83017,
83023,83027,83032,83100,83115
]

if IS_TEST_SERVER == 0 :
	COSTUME_WEAPON_VNUMS = [
	range(43083,43111),#christams
	range(43034,43062),#halloween25
	40999,43000,
	range(43001,43006),#wheel
	range(40992,40999),#bp
	range(40978,40992),#summer
	range(40971,40978),#easter
	range(40957,40971),#easter
	range(40915,40922),#yinyang anaconda
	range(40908,40915),#yinyang anaconda
	range(40866,40894),#newyear
	range(40831,40859),#halloween
	range(40775,40782),#bp
	range(40789,40803),#wheel
	range(40369,40376),#syrax hzmh
	range(40278,40285),#syrax hzmh
	range(40691,40698),
	range(40607,40614),
	range(40348,40355),
	range(40719,40726),
	range(40698,40705),
	range(40705,40712),
	range(40726,40733),
	range(40194,40199),
	range(40411,40418),
	range(40229,40236),
	range(40684,40691),
	range(40236,40243),
	#range(40719,40726),
	range(40565, 40572)
	# range(40101, 40114)
	# ,
	# range(40115,40121)
	# ,
	# range(40122,40128)
	# ,
	# range(40129,40135)
	# ,
	# range(40136,40142)
	# ,
	# range(40143,40149)
	# ,
	# range(40150,40156)
	# ,
	# range(40157,40163)
	# ,
	# range(40167,40173)
	# ,
	# range(40178,40184)
	# ,
	# range(40185,40191)
	# ,
	# range(40194,40341)
	# ,
	# range(40642, 40677),
	# range(40621, 40642),
	# range(40593, 40614),
	# range(40348, 40551),# black 12zi  40599
	# range(40558,40572),
	# range(40101, 40107),range(40155, 40121),range(40122, 40127),range(40229, 40236),
	# range(40243, 40257),range(40243, 40257)

	# 
	# ,



	]
else :
	COSTUME_WEAPON_VNUMS = [
	range(61000,61007),
	range(61011,61018),
	range(61022,61029),
40101
,40102
,40103
,40104
,40105
,40106
,40115
,40116
,40117
,40118
,40119
,40120
,40122
,40123
,40124
,40125
,40126
,40127
,40129
,40130
,40131
,40132
,40133
,40134
,40136
,40137
,40138
,40139
,40140
,40141
,40143
,40144
,40145
,40146
,40147
,40148
,40167
,40168
,40169
,40170
,40171
,40172
,40178
,40179
,40180
,40181
,40182
,40183
,40184
,40185
,40186
,40187
,40188
,40189
,40190
,40191
,40194
,40195
,40196
,40197
,40198
,40199
,40200
,40201
,40202
,40203
,40204
,40205
,40206
,40207
,40943
,40944
,40945
,40946
,40947
,40948
,40949
,40950
,40951
,40952
,40953
,40954
,40955
,40956
,40495
,40496
,40497
,40498
,40499
,40500
,40501
,40502
,40503
,40504
,40505
,40506
,40507
,40508
,40509
,40510
,40511
,40512
,40513
,40514
,40515
,40565
,40566
,40567
,40568
,40569
,40570
,40571
,40614
,40615
,40616
,40617
,40618
,40619
,40620
,40670
,40671
,40672
,40673
,40674
,40675
,40676
,40677
,40678
,40679
,40680
,40681
,40682
,40683
,40684
,40685
,40686
,40687
,40688
,40689
,40690
,40691
,40692
,40693
,40694
,40695
,40696
,40697




	]

if IS_TEST_SERVER == 0 :
	COSTUME_ARMOR_VNUMS = [
	range(42181,42189),#christams
	range(42163,42171),#halloween25
	42153,42154,#wheel
	42151,42152,#bp
	42147,42148,#summer
	42149,42150,#summer
	42145,42146,#bp
	range(42141,42145),#easter
	range(42133,42135),#yinyang anaconda
	range(42131,42133),#yinyang anaconda
	range(42119, 42127),#newyear
	range(42109, 42117),#halloween
	42093,42094,#bp
	42097,42098,#wheel
	42099,42100,#wheel
	41971,41972,#syrax hzmh
	41939,41940,#syrax hzmh
	42061,42062,
	42033,42034,
	41966,41965,
	42077,42078,
	42071,42072,
	42073,42074,
	42079,42080,
	42057,42058,
	41983,41984,
	41925,41926,
	42055,42056,
	41718,41719,
	42029,42030,
	25023,25024
	# range(41901,42053)
	# ,range(42037,42043)
	# ,range(42029,42035)
	# ,range(41965, 42023)# black 12zi  40599
	# ,25025,25026,41925,41926,41929,41930,41933,41934
	 # ,25021
	 # ,25022
	 # ,25023
	 # ,25024
	 # ,25027
	 # ,25028
	 # ,41959
	 # ,41960
	 # ,41961
	 # ,41962
	 # ,41963
	 # ,41964
	 # ,41925
	 # ,41926
	 # ,41929
	 # ,41930
	 # ,41933
	 # ,41934
	 # ,41937
	 # ,41938
	 # ,41941
	 # ,41942
	 # ,41945
	 # ,41946
	 # ,41951
	 # ,41952
	 # ,41955
	 # ,41956
	 # ,range(25001, 25004)
	 # ,range(25005, 25013)
	 # ,range(25014, 25021)
	]
else :
	COSTUME_ARMOR_VNUMS = [
	61007,61008,
	61018,61019,
	61029,61030,
41959
,41960
,41961
,41962
,41963
,41964
,42007
,42008
,42009
,42010
,42011
,42012
,42053
,42054
,42055
,42056
,42057
,42058
,42059
,42060
,42061
,42062
,42063
,42064
,42065
,42066
,42067
,42068
,25001
,25002
,25003
,25004
,25005
,25006
,25007
,25008
,25009
,25019
,25010
,25011
,25012
,25013
,25014
,25015
,25016
,25017
,25018
,25020
,25021
,25022
,25023
,25024
,25025
,25026
,25027
,25028





	]


if IS_TEST_SERVER == 0 :
	COSTUME_HAIR_VNUMS = [
	range(420123,420131),#christams
	range(420107,420115),#halloween25
	420097,420098,#wheel
	420095,420096,#bp
	420091,420092,#summer
	420093,420094,#summer
	420089,420090,#bp
	range(420085,420089),#easter
	range(420077,420079),#yinyang anaconda
	range(420075,420077),#yinyang anaconda
	range(420063, 420071),#newyear
	range(420051, 420059),#halloween
	420035,420036,#bp
	420039,420040,#wheel
	420041,420042,#wheel
	75771,75772,#syrax hzmh
	75745,75746,#syrax hzmh
	420007,420008,
	75827,75828,
	75765,75766,
	420021,420022,
	420015,420016,
	420017,420019,
	420019,420020,
	420005,420006,
	75783,75784,
	75731,75732,

	420003,420004,
	45393,45394,
	75823,75824,
	45162,45163
	# range(75701, 75845)
	# ,45120
	# ,45124
	# ,range(26001,26013)
	# ,range(45119,45127)

	# range(75837, 75845)
	# ,range(75831, 75837)
	# ,range(75823, 75829)
	# ,range(75813, 75817)
	# ,range(75765, 75813)
	# ,45120
	# ,45124
	# ,75731
	# ,75732
	# ,75735
	# ,75736
	# ,75737
	# ,75738
	# # black 12zi  40599
	# ,range(26001,26013)
	# ,range(45119,45127)

	 # ,75741
	 # ,75742
	 # ,75745
	 # ,75746
	 # ,75749
	 # ,75750
	 # ,75753
	 # ,75754
	 # ,75757
	 # ,75758
	 # ,75761
	 # ,75762
	 # ,75709
	 # ,75710
	 # ,75741
	 # ,75742 
	 # ,75745
	 # ,75746 
	 # ,75749
	 # ,75750

	]
else :
	COSTUME_HAIR_VNUMS = [
	61009,61010,
	61020,61021,
	61031,61032,
420001
,420002
,420003
,420004
,420005
,420006
,420007
,420008
,420009
,420010
,420011
,420012
,420013
,420014
,420039
,420040
,421001
,421002
,421003
,421004
,421005
,421006
,421007
,421008
,421009
,421010
,421011
,421012
,421013
,421014
,421015
,421016
,421017
,421018
,421019
,421020
,421021
,421022
,421023
,421024
,421025
,421026
,421027
,421028
,421029
,421030
,421031
,421032
,421033
,421034
,421035
,421036
,421037
,421038
,75765
,75766
,75767
,75768
,45120
,45124
,26001
,26002
,26003
,26004
,26005
,26006
,26007
,26008
,26009
,26010
,26011
,26012

	]
	

COSTUME_PET_VNUMS = [

72802,
72803


# range(53001,53027),range(53218,53310),range(54301,54318),range(53311,53323),range(34321,34356)
# range(34349,34356),34345,34346,34347,34348,range(34321, 34345)

]
COSTUME_MOUNT_VNUMS = [
72902,
72903
]

if app.INGAME_WIKI_WOLFMAN:
	COSTUME_WEAPON_VNUMS.extend([40107])

if IS_TEST_SERVER == 0 :
	COSTUME_SASH_VNUMS = [\
	86848,#christmas
	86854,#christmas
	86858,#christmas
	86864,#christmas
	86818,#halloween
	86824,#halloween
	86828,#halloween
	86834,#halloween
	86788,
	86784,
	86774,
	86778,#summer
	86768,
	86758,
	86764,
	86738,
	86734,
	86704,#newyear
	86708,#newyear
	86714,#newyear
	86718,#newyear
	86678,#halloween
	86684,#halloween
	86688,#halloween
	86694,#halloween
	86644,#bp
	86654,#wheel
	86658,#wheel
	86474,
	86428,
	86148,
	86495,
	86341,
	86485,
	86601,
	86311,
	86154,
	86174
	# 86464,
	# 86448,
	# 86454,
	# 86458,
	# 86434,
	# 86438,
	# 86444,
	# 86418,
	# 86424,
	# 86428,
	# 86148,
	# 86168,
	# 86178,
	# 86075,
	# 86094,
	# 86098,
	# 86184,86188,86194,86198, 86204,86208,86214,86218,
	# 86224,86228,86234,86238,86244,86248,86254,86258,
	# 86268,86264,86278,86274,86284,86288,
	# 86304,86308,86314,86318,
	# 86324,86328,86334,86338,86344,86348,86354,86358,
	# 86368,86364,86378,86374,86384,86388,86394,86398,
	# 86144,86154,86158,
	# 86164,86174,
	# 86104,
	# 86108,86114,86118,86124,
	# 86134,86138
	]
else:
	COSTUME_SASH_VNUMS = [\
	86181,
	86185,
	86191,
	86091,
	86095,
	86101,
	86105,
	86111,
	86115,
	86121,
	86125,
	86131,
	86181,
	86185,
	86191,
	86195
	]


COSTUME_WEAPONS_EFFECT_VNUMS = list(range(65000, 65001))

COSTUME_ARMORS_EFFECT_VNUMS = list(range(65100, 65101))


# The key may predate the locale .epk repack; localeinfo synthesizes a
# "Locale not found" sentinel instead of raising, so check for it.
_BIOLOG_TITLE = localeinfo.WIKI_SUBCATEGORY_BIOLOG
if not _BIOLOG_TITLE or str(_BIOLOG_TITLE).startswith("Locale not found"):
	_BIOLOG_TITLE = "Biologist"

_GROWTH_PET_TITLE = getattr(localeinfo, "WIKI_SUBCATEGORY_PET", "")
if not _GROWTH_PET_TITLE or str(_GROWTH_PET_TITLE).startswith("Locale not found"):
	_GROWTH_PET_TITLE = "Pet"

# Shares the Costumes "Mount" label (growthpet precedent: WIKI_SUBCATEGORY_PET
# is also reused across both categories).
_GROWTH_MOUNT_TITLE = getattr(localeinfo, "WIKI_SUBCATEGORY_MOUNT", "")
if not _GROWTH_MOUNT_TITLE or str(_GROWTH_MOUNT_TITLE).startswith("Locale not found"):
	_GROWTH_MOUNT_TITLE = "Mount"

_GEM_SHOP_TITLE = getattr(localeinfo, "WIKI_GEMSHOP_TITLE", "")
if not _GEM_SHOP_TITLE or str(_GEM_SHOP_TITLE).startswith("Locale not found"):
	_GEM_SHOP_TITLE = "Gaya Shop"

_BUFFI_TITLE = getattr(localeinfo, "WIKI_SUBCATEGORY_BUFFI", "")
if not _BUFFI_TITLE or str(_BUFFI_TITLE).startswith("Locale not found"):
	_BUFFI_TITLE = "Buffi"

# The legacy WIKI_SUBCATEGORY_*_EFFECT labels are bare "Weapons"/"Armors";
# inside Costumes those collide with its own Weapons/Armor rows, so the
# moved rows use their own keys.
_WEAPON_SHINING_TITLE = getattr(localeinfo, "WIKI_SUBCATEGORY_WEAPONS_SHINING", "")
if not _WEAPON_SHINING_TITLE or str(_WEAPON_SHINING_TITLE).startswith("Locale not found"):
	_WEAPON_SHINING_TITLE = "Weapon Effects"

_ARMOR_SHINING_TITLE = getattr(localeinfo, "WIKI_SUBCATEGORY_ARMORS_SHINING", "")
if not _ARMOR_SHINING_TITLE or str(_ARMOR_SHINING_TITLE).startswith("Locale not found"):
	_ARMOR_SHINING_TITLE = "Armor Effects"

WIKI_CATEGORIES = [
	[
		localeinfo.WIKI_CATEGORY_EQUIPEMENT,
		[
			[localeinfo.WIKI_SUBCATEGORY_WEAPONS, (0,), "d:/ymir work/ui/wiki/banners/banner_weapons.tga"],
			[localeinfo.WIKI_SUBCATEGORY_ARMOR, (1,), "d:/ymir work/ui/wiki/banners/armor.tga"],
			[localeinfo.WIKI_SUBCATEGORY_HELMET, (4,), "d:/ymir work/ui/wiki/banners/helmets.tga"],
			[localeinfo.WIKI_SUBCATEGORY_SHIELD, (6,), "d:/ymir work/ui/wiki/banners/shield.tga"],
			[localeinfo.WIKI_SUBCATEGORY_EARRINGS, (2,), "d:/ymir work/ui/wiki/banners/earrings.tga"],
			[localeinfo.WIKI_SUBCATEGORY_BRACELET, (7,), "d:/ymir work/ui/wiki/banners/bracelests.tga"],
			[localeinfo.WIKI_SUBCATEGORY_NECKLACE, (5,), "d:/ymir work/ui/wiki/banners/neck.tga"],
			[localeinfo.WIKI_SUBCATEGORY_SHOES, (3,), "d:/ymir work/ui/wiki/banners/shoes.tga"],
			[localeinfo.WIKI_SUBCATEGORY_BELTS, (9,), "d:/ymir work/ui/wiki/banners/belts.tga"],
			[localeinfo.WIKI_SUBCATEGORY_TALISMANS, (10,), "d:/ymir work/ui/wiki/banners/talisman.tga"],
		]
	],
	[
		localeinfo.WIKI_CATEGORY_CHESTS,
		[
			[localeinfo.WIKI_SUBCATEGORY_CHESTS, (BOSS_CHEST_VNUMS,), "d:/ymir work/ui/wiki/banners/bosschests.png"],
			[localeinfo.WIKI_SUBCATEGORY_EVENT_CHESTS, (EVENT_CHEST_VNUMS,), "d:/ymir work/ui/wiki/banners/bosschests.png"],
			[localeinfo.WIKI_SUBCATEGORY_ALTERNATIVE_CHESTS, (ALT_CHEST_VNUMS,), "d:/ymir work/ui/wiki/banners/bosschests.png"]
		]
	],
	[
		localeinfo.WIKI_CATEGORY_BOSSES,
		[
			# Manual vnum lists -- defined at the top of this file. Same
			# pattern as the metin-stone sub-cats: the redesign's
			# WikiMainBossWindow.Show patch detects the single-list arg
			# shape and feeds AddItem(vnum) directly, bypassing
			# wiki.LoadClassMobs / engine-side level filtering.
			[localeinfo.WIKI_SUBCATEGORY_BOSS_TIER1,        (BOSS_TIER1_VNUMS,),        "d:/ymir work/ui/wiki/banners/bosses.tga"],
			[localeinfo.WIKI_SUBCATEGORY_BOSS_TIER2,        (BOSS_TIER2_VNUMS,),        "d:/ymir work/ui/wiki/banners/bosses.tga"],
			[localeinfo.WIKI_SUBCATEGORY_BOSS_TIER3,        (BOSS_TIER3_VNUMS,),        "d:/ymir work/ui/wiki/banners/bosses.tga"],
			[localeinfo.WIKI_SUBCATEGORY_BOSS_TIER4,        (BOSS_TIER4_VNUMS,),        "d:/ymir work/ui/wiki/banners/bosses.tga"],
			[localeinfo.WIKI_SUBCATEGORY_BOSS_DUNGEON_MINI, (BOSS_DUNGEON_MINI_VNUMS,), "d:/ymir work/ui/wiki/banners/bosses.tga"],
			[localeinfo.WIKI_SUBCATEGORY_BOSS_DUNGEON,      (BOSS_DUNGEON_VNUMS,),      "d:/ymir work/ui/wiki/banners/bosses.tga"],
			[localeinfo.WIKI_SUBCATEGORY_BOSS_SPECIAL,      (BOSS_SPECIAL_VNUMS,),      "d:/ymir work/ui/wiki/banners/bosses.tga"],
			# >>> SECTION BEGIN: legacy level-based sub-cats (replaced by manual lists 2026-06-29)
			# [localeinfo.WIKI_SUBCATEGORY_LV1_75, (0, 1, 75), "d:/ymir work/ui/wiki/banners/bosses.tga"],
			# [localeinfo.WIKI_SUBCATEGORY_LV76_100, (0, 76, 115), "d:/ymir work/ui/wiki/banners/bosses.tga"]
			# <<< SECTION END
		]
	],
	[
		localeinfo.WIKI_CATEGORY_MONSTERS,
		[
			[localeinfo.WIKI_SUBCATEGORY_LV1_75, (1, 1, 75), "d:/ymir work/ui/wiki/banners/monster.tga"],
			[localeinfo.WIKI_SUBCATEGORY_LV76_100, (1, 76, 115), "d:/ymir work/ui/wiki/banners/monster.tga"]
		]
	],
	[
		localeinfo.WIKI_CATEGORY_METINSTONES,
		[
			# Manual vnum lists -- defined at the top of this file. The
			# redesign's WikiMainBossWindow.Show patch detects a single
			# list arg and feeds AddItem(vnum) directly, bypassing
			# wiki.LoadClassMobs.
			[localeinfo.WIKI_SUBCATEGORY_STONE_FIELD_LOW,  (STONE_TIER1_VNUMS,), "d:/ymir work/ui/wiki/banners/metin.tga"],
			[localeinfo.WIKI_SUBCATEGORY_STONE_FIELD_MED,  (STONE_TIER2_VNUMS,), "d:/ymir work/ui/wiki/banners/metin.tga"],
			[localeinfo.WIKI_SUBCATEGORY_STONE_FIELD_HIGH, (STONE_TIER3_VNUMS,), "d:/ymir work/ui/wiki/banners/metin.tga"],
			[localeinfo.WIKI_SUBCATEGORY_STONE_CHAOS,      (STONE_CHAOS_VNUMS,), "d:/ymir work/ui/wiki/banners/metin.tga"],
			[localeinfo.WIKI_SUBCATEGORY_STONE_EVENT,      (STONE_EVENT_VNUMS,), "d:/ymir work/ui/wiki/banners/metin.tga"],
		]
	],
	# [
		# localeinfo.WIKI_CATEGORY_DUNGEONS,
		# [
			# [localeinfo.WIKI_SUBCATEGORY_ORCMAZE, ("dungeons/orc_maze.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_SPIDER_BARONESS, ("dungeons/spider_baroness.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_AZRAEL, ("dungeons/azrael.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_BERAN_SETAOU, ("dungeons/beran_setaou.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_SHIPDEFENSE, ("dungeons/ship_defense.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_JOTUN_THRYM, ("dungeons/jotun_thrym.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_CRYSTAL_DRAGON, ("dungeons/crystal_dragon.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_MELEY, ("dungeons/meley.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_THRANDUILS_LAIR, ("dungeons/thranduil.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_ZODIAC, ("dungeons/zodiac.txt",)],
		# ]
	# ],
	[
		localeinfo.WIKI_CATEGORY_COSTUMES,
		[
			[localeinfo.WIKI_SUBCATEGORY_WEAPONS, (COSTUME_WEAPON_VNUMS,), "d:/ymir work/ui/wiki/banners/costume_weapon.tga"],
			[localeinfo.WIKI_SUBCATEGORY_ARMOR, (COSTUME_ARMOR_VNUMS,), "d:/ymir work/ui/wiki/banners/costume_armor.tga"],
			[localeinfo.WIKI_SUBCATEGORY_HAIRSTYLES, (COSTUME_HAIR_VNUMS,), "d:/ymir work/ui/wiki/banners/costume_hairstyle.tga"],
			[localeinfo.WIKI_SUBCATEGORY_PET, (COSTUME_PET_VNUMS,), "d:/ymir work/ui/wiki/banners/costume_pet.tga"],
			[localeinfo.WIKI_SUBCATEGORY_MOUNT, (COSTUME_MOUNT_VNUMS,), "d:/ymir work/ui/wiki/banners/costume_mount.tga"],
			[localeinfo.WIKI_SUBCATEGORY_COSTUME_SASH, (COSTUME_SASH_VNUMS,), "d:/ymir work/ui/wiki/banners/costume_sash.tga"],
			[_WEAPON_SHINING_TITLE, (COSTUME_WEAPONS_EFFECT_VNUMS,), "d:/ymir work/ui/wiki/banners/costume_weapon.tga"],
			[_ARMOR_SHINING_TITLE, (COSTUME_ARMORS_EFFECT_VNUMS,), "d:/ymir work/ui/wiki/banners/costume_armor.tga"],
		]
	],
	[
		# >>> EFFECTS BEGIN -- rows moved into Costumes above (disabled)
		# The entry itself stays so the index-keyed parent-click funclist in
		# both sidebar builders keeps its numbering; WIKI_HIDDEN_CATEGORIES
		# below stops the row from being drawn.
		localeinfo.WIKI_CATEGORY_EFFECTS,
		[
			# [localeinfo.WIKI_SUBCATEGORY_WEAPONS_EFFECT, (COSTUME_WEAPONS_EFFECT_VNUMS,), "d:/ymir work/ui/wiki/banners/costume_weapon.tga"],
			# [localeinfo.WIKI_SUBCATEGORY_ARMORS_EFFECT, (COSTUME_ARMORS_EFFECT_VNUMS,), "d:/ymir work/ui/wiki/banners/costume_armor.tga"],
		],
		# <<< EFFECTS END
	],
	# [
		# localeinfo.WIKI_CATEGORY_EVENTS,
		# [
			# [localeinfo.WIKI_SUBCATEGORY_OKAY_CARD, ("events/okey_card.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_FISHPUZZLE, ("events/fishpuzzle.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_BOSS_HUNT, ("events/boss_hunt.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_MOONLIGHT_CHESTS, ("events/moonlight_chests.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_HEXAGONAL_CHESTS, ("events/hexagonal_chests.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_TAG_TEAM, ("events/tag_team.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_EMPIRE_WAR, ("events/empire_war.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_PVP_TOURNAMENT, ("events/pvp_tournament.txt",)]
		# ]
	# ],
	[
		localeinfo.WIKI_CATEGORY_GUIDES,
		[
			[localeinfo.WIKI_SUBCATEGORY_THE_START, ("guides/the_start.txt",)],
			#[localeinfo.WIKI_SUBCATEGORY_RUNES, ("systems/pets.txt",)],
			[localeinfo.WIKI_SUBCATEGORY_105_AND_NOW, ("guides/35-75.txt",)],
			[localeinfo.WIKI_SUBCATEGORY_106_AND_NOW, ("guides/75-105.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_108_AND_NOW, ("guides/110-120.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_BIO, ("guides/bio.txt",)],
		]
	],
	[
		localeinfo.WIKI_CATEGORY_SYSTEMS,
		[
			[_BIOLOG_TITLE, ("PAGE:biolog",)],
			[localeinfo.WIKI_SUBCATEGORY_DRAGONALCHEMY, ("PAGE:dragonsoul",)],
			# [localeinfo.WIKI_SUBCATEGORY_DRAGONALCHEMY, ("systems/dragon_alchemy.txt",)],  # legacy text page, replaced by PAGE:dragonsoul
			[_GROWTH_PET_TITLE, ("PAGE:growthpet",)],
			[_GEM_SHOP_TITLE, ("PAGE:gemshop",)],
			[_BUFFI_TITLE, ("PAGE:buffi",)],
			# [localeinfo.WIKI_SUBCATEGORY_RUNES, ("systems/pets.txt",)],  # dead target (file never existed), replaced by PAGE:growthpet
			# [localeinfo.WIKI_SUBCATEGORY_COSTUME_SASH, ("systems/costume_sash.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_BATTLEPASS, ("systems/battlepass.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_COSTUMES, ("systems/costumes.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_GAYA, ("systems/gaya.txt",)],  # legacy text page, replaced by PAGE:gemshop
			# [localeinfo.WIKI_SUBCATEGORY_SKILL_COLOR, ("systems/skill_color.txt",)],
			# [localeinfo.WIKI_SUBCATEGORY_CONTER_BOOST, ("systems/conter_boost.txt",)]
		]
	],
	[
		localeinfo.WIKI_CATEGORY_DUNGEONS,
		[
			[localeinfo.WIKI_SUBCATEGORY_ORCMAZE, (9,)],
			[localeinfo.WIKI_SUBCATEGORY_MONKEY_DUNGEON, (10,)],
			[localeinfo.WIKI_SUBCATEGORY_CRYSTAL_DRAGON, (3,)],
			[localeinfo.WIKI_SUBCATEGORY_SPIDER_BARONESS, (2,)],
			[localeinfo.WIKI_SUBCATEGORY_AZRAEL, (4,)],
			[localeinfo.WIKI_SUBCATEGORY_BERAN_SETAOU, (5,)],
			[localeinfo.WIKI_SUBCATEGORY_NEMERE, (7,)],
			[localeinfo.WIKI_SUBCATEGORY_RAZADOR, (6,)],
			# Legacy .txt guide pages hidden until each dungeon gets its data-driven entry.
			#[localeinfo.WIKI_SUBCATEGORY_DEMONTOWER_OFFITIOAL, ("dungeons/demontower_offitioal.txt",)],
			#[localeinfo.WIKI_SUBCATEGORY_SHADOW_BERAN_SETAOU, ("dungeons/shadow_beran_setaou.txt",)],
			#[localeinfo.WIKI_SUBCATEGORY_SHIPDEFENSE, ("dungeons/ship_defense.txt",)],
		]
	],
]

# Categories that stay defined above but are not drawn in the sidebar.
# Removing the entries instead would shift every later index, and the
# parent-click funclist in the sidebar builders is index-keyed.
WIKI_HIDDEN_CATEGORIES = [
	localeinfo.WIKI_CATEGORY_MONSTERS,
	localeinfo.WIKI_CATEGORY_GUIDES,
	localeinfo.WIKI_CATEGORY_EFFECTS,
]

#if app.USE_GLOVE_SYSTEM:
#	WIKI_CATEGORIES[0][1].append([localeinfo.WIKI_SUBCATEGORY_GLOVES, (11,), "d:/ymir work/ui/wiki/banners/gloves.tga"],)

# Growth-mount page entry, right under Pet; flag-off clients have no
# net.SendGrowthMountPacket binding and skip the row entirely.
if hasattr(net, "SendGrowthMountPacket"):
	for _cat in WIKI_CATEGORIES:
		if _cat[0] == localeinfo.WIKI_CATEGORY_SYSTEMS:
			for _i in xrange(len(_cat[1])):
				if _cat[1][_i][1] == ("PAGE:growthpet",):
					_cat[1].insert(_i + 1, [_GROWTH_MOUNT_TITLE, ("PAGE:growthmount",)])
					break
			else:
				_cat[1].append([_GROWTH_MOUNT_TITLE, ("PAGE:growthmount",)])
			break

if app.USE_EXTENDED_WIKI_CRAFT:
	craft_loaded = 0

	def LoadCrafting():
		global craft_loaded
		if craft_loaded == 1:
			return

		craft_loaded = 1

		import game_data
		import nonplayer

		if len(game_data.craftingDict) > 0:
			WIKI_CATEGORIES.append([localeinfo.WIKI_CATEGORY_CRAFTING, []])

			for k, v in sorted(game_data.craftingDict.items()):
				craft_len = len(v)
				craft_list = []

				if craft_len:
						for k2, v2 in sorted(v.items()):
							craft_list.append(k2)

				WIKI_CATEGORIES[-1][1].append([nonplayer.GetMonsterName(k), (k, craft_len, craft_list), "d:/ymir work/ui/wiki/banners/cube.tga"])

# Shop NPCs to leave out of the wiki "Shops" category, on top of the ones
# convert.py derives into wiki_shop_hidden.txt (groups with no NPC in the
# world). Category listing ONLY -- a hidden shop still shows its [SHOP] row
# on every item it sells. Add shop NPC vnums freely.
WIKI_SHOP_HIDDEN_NPC_VNUMS = [
]

if app.USE_EXTENDED_WIKI_SHOP:
	shop_loaded = 0

	def LoadShop():
		global shop_loaded
		if shop_loaded == 1:
			return

		shop_loaded = 1

		import game_data
		import nonplayer

		if len(game_data.shopDict) > 0:
			WIKI_CATEGORIES.append([localeinfo.WIKI_CATEGORY_SHOP, []])

			for k, v in sorted(game_data.shopDict.items()):
				if k in game_data.shopHiddenNpcSet or k in WIKI_SHOP_HIDDEN_NPC_VNUMS:
					continue

				shop_len = len(v)
				shop_list = []

				if shop_len:
						for k2, v2 in sorted(v.items()):
							shop_list.append(k2)

				WIKI_CATEGORIES[-1][1].append([nonplayer.GetMonsterName(k), (k, shop_len, shop_list), "d:/ymir work/ui/wiki/banners/shop.tga"])

if app.ENABLE_ITEM_SHOPS:
	item_shops_loaded = 0

	def LoadItemShops():
		global item_shops_loaded
		if item_shops_loaded == 1:
			return

		item_shops_loaded = 1

		import game_data

		# Single category + single subcategory: every shop-item vnum on one flat page (mirrors
		# the costume page's vnum-list layout). The (vnums,) tuple is applied to Show(vnums).
		if len(game_data.itemShopDict) > 0:
			vnums = sorted(game_data.itemShopDict.keys())
			WIKI_CATEGORIES.append([localeinfo.WIKI_CATEGORY_SHOP_ITEMS, [[localeinfo.WIKI_SUBCATEGORY_SHOP_ITEMS, (vnums,), "d:/ymir work/ui/wiki/banners/shop.tga"]]])

def Load():
	if app.USE_EXTENDED_WIKI_CRAFT:
		LoadCrafting()

	if app.USE_EXTENDED_WIKI_SHOP:
		LoadShop()

	if app.ENABLE_ITEM_SHOPS:
		LoadItemShops()

#/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\
#/!\/!\/!\ OTHER STUFF /!\/!\/!\

ITEM_BLACKLIST = [
range(14520, 14530),
range(15430, 15440),
range(15220, 15250),
range(17520, 17530),
range(20810, 20860),
range(20760, 20790),
91040,
91041,
range(1140, 1170),
range(20, 130),
range(2010, 2129),
range(3000, 3120),
range(3170, 3190),
range(3200, 3210),
range(210, 269),
range(260, 269),
#range(13160, 13169),
7200,
91000,
#armors
13189,
91030,
# pendant soul
10790,
10791,
# --- Kyanite weapons ---
range(500, 510),
range(1500, 1510),
range(2500, 2510),
range(3500, 3510),
range(5500, 5510),
range(6500, 6510),
range(7500, 7510),
# --- Kyanite armors ---
range(12050, 12100),
# --- belts: hide leather+9, royal+9 / dark / runic / great bear ---
#range(18049, 18080),
# --- lvl>=99 items NOT produced by cube.txt (hide from wiki) ---
# weapons
range(6090, 6100),
range(6120, 6130),
range(9510, 9520),
# armor body
range(12910, 12920),
range(12920, 12930),
range(12930, 12940),
range(12940, 12950),
range(20800, 20810),
range(20850, 20860),
range(20900, 20910),
range(20910, 20920),
range(20920, 20930),
range(20930, 20940),
range(20940, 20950),
range(20950, 20960),
range(21090, 21100),
range(21200, 21210),
# earrings
#range(17520, 17530),
#range(17560, 17570),
# helmet
#range(12770, 12780),
range(21550, 21560),
# necklace
range(16520, 16530),
# bracelet
#range(14520, 14530),
#range(14560, 14570),
]

MOB_WHITELIST = [
151,153,154,155,191,192,193,194,401,402,403,404,405,406,
454,455,456,491,492,493,494,502,503,504,531,532,533,534,
591,601,602,603,604,636,637,656,691,692,694,701,702,703,
704,705,706,707,751,752,753,754,755,756,757,791,993,1001,1002,
1032,1091,1092,1093,1094,1095,1104,1106,1107,1108,1131,1137,1138,
1192,1291,1292,1302,1304,1305,
1332,1401,1402,1403,1501,1502,1503,1601,1602,1603,1901,2001,
2002,2003,2004,2005,2031,2032,2033,2034,2035,2036,2037,2052,
2064,2065,2074,2075,2091,2092,2094,2103,2104,2105,2108,2132,2191,2192,
2203,2205,2206,2291,2301,2302,2303,2304,2305,2306,2307,2311,2312,
2313,2314,2315,2401,2402,2403,2404,2411,2412,2413,2414,2415,
2451,2452,2453,2492,2493,2495,2508,2596,2597,2598,3770,3771,3772,
3773,4901,4902,5004,5005,5121,5122,5123,5124,5125,5126,5127,
5161,5162,5163,5621,5622,5623,6433,7556,7563,7570,8001,8002,8003,8004,8005,8006,8007,8008,
8009,8010,8011,8012,8013,8014,8018,8019,8024,8025,8026,8027,8038,8041,
8042,8043,8044,8045,8046,8047,8048,8049,8050,8257,8258,14934,
14954,20924,24934,25984,59012,59013,
3090,3091,3190,3191,3290,3291,3390,3391,3490,3491,3590,3591,3595,3596,
3690,3691,3790,3791,3890,3891,3905,3906,3910,3911,3912,3913,3966,
6091,6191,6192,6407,6500,
8051,8052,8053,8054,8055,8056,8057,8058,8059,8061,
3001,3102,3201,3302,3402,3502,3552,3601,3701,3801
]

HAIRSTYLE_CAMERA_CFG = {
	player.MAIN_RACE_WARRIOR_M : ([311.4753, -16.3934, 150.0000], [0.0000, 0.0000, 152.3934]),
	player.MAIN_RACE_ASSASSIN_W : ([344.2622, -16.3934, 150.0000], [0.0000, 0.0000, 147.3934]),
	player.MAIN_RACE_SURA_M : ([311.4753, -16.3934, 150.0000], [0.0000, 0.0000, 172.1804]),
	player.MAIN_RACE_SHAMAN_W : ([344.2622, -16.3934, 150.0000], [0.0000, 0.0000, 147.3934]),
	player.MAIN_RACE_WARRIOR_W : ([344.2622, -16.3934, 150.0000], [0.0000, 0.0000, 147.3934]),
	player.MAIN_RACE_ASSASSIN_M : ([344.2622, -16.3934, 150.0000], [0.0000, 0.0000, 156.7869]),
	player.MAIN_RACE_SURA_W : ([311.4753, -16.3934, 150.0000], [0.0000, 0.0000, 156.7869]),
	player.MAIN_RACE_SHAMAN_M : ([377.0492, -16.3934, 150.0000], [0.0000, 0.0000, 163.7869])
}

if app.INGAME_WIKI_WOLFMAN:
	LYCAN_HAIRSTYLE_CAMERA_CFG = {
		player.MAIN_RACE_WOLFMAN_M : ([311.4753, -16.3934, 150.0000], [0.0000, 0.0000, 192.1804]),
	}

	HAIRSTYLE_CAMERA_CFG.update(LYCAN_HAIRSTYLE_CAMERA_CFG)
