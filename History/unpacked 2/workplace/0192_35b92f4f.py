# coding: utf-8

import app
import item
import player
import grp
import wndMgr

if app.USE_ACCE_SYSTEM:
	import acce

import ui
import constinfo
import localeinfo
import uitooltip

from weakref import proxy, ProxyType

import math
from operator import truediv

IMG_PATH = "d:/ymir work/ui/game/bonusboard/"

MAX_BONUS_NAME_SHOWN = 26

SCROLL_SPEED = 7.7
SCROLL_SPEED_ITEM = 20

SEARCH_FOUND_COLOR = grp.GenerateColor(0.8549, 0.8549, 0.8549, 1.0)
SEARCH_NOTFOUND_COLOR = grp.GenerateColor(1.0, 0.2, 0.2, 1.0)

bonus_page_show_status = False

PAGE_BONUSES = 1
PAGE_STATS = 2

CATEGORIES_DICT = {\
	0 : [\
			localeinfo.BONUS_PAGE_DAMAGE,
			[\
				[localeinfo.DETAILS_20, item.APPLY_CRITICAL_PCT],\
				[localeinfo.DETAILS_21, item.APPLY_PENETRATE_PCT],\
				[localeinfo.DETAILS_5, item.APPLY_ATTBONUS_MONSTER],\
				[localeinfo.DETAILS_0, item.APPLY_ATTBONUS_STONE],\
				[localeinfo.DETAILS_NEW_1, item.APPLY_ATTBONUS_BOSS],\
				[localeinfo.DETAILS_NEW_04, item.APPLY_FOURTH_ATTRIBUTE_BONUS],\
				[localeinfo.DETAILS_NEW_02, item.APPLY_SECOND_ATTRIBUTE_BONUS],\
				[localeinfo.DETAILS_NEW_2, item.APPLY_ATTBONUS_MEDI_PVM],\
				#[localeinfo.DETAILS_6, item.APPLY_ATTBONUS_CZ],\
				[localeinfo.DETAILS_NEW_01, item.APPLY_FIRST_ATTRIBUTE_BONUS],\
				[localeinfo.DETAILS_NEW_03, item.APPLY_THIRD_ATTRIBUTE_BONUS],\
				[localeinfo.DETAILS_3, item.APPLY_ATTBONUS_ORC],\
				[localeinfo.DETAILS_4, item.APPLY_ATTBONUS_UNDEAD],\
				[localeinfo.DETAILS_7, item.APPLY_ATTBONUS_ANIMAL],\
				[localeinfo.DETAILS_8, item.APPLY_ATTBONUS_MILGYO],\
				[localeinfo.DETAILS_9, item.APPLY_ATTBONUS_DEVIL],\
				[localeinfo.DETAILS_10, item.APPLY_ATTBONUS_DESERT],\
				[localeinfo.DETAILS_11, item.APPLY_ATTBONUS_INSECT],\
				[localeinfo.DETAILS_36, item.APPLY_ATTBONUS_WARRIOR],\
				[localeinfo.DETAILS_37, item.APPLY_ATTBONUS_ASSASSIN],\
				[localeinfo.DETAILS_38, item.APPLY_ATTBONUS_SURA],\
				[localeinfo.DETAILS_39, item.APPLY_ATTBONUS_SHAMAN],\
				[localeinfo.DETAILS_NEW_6, item.APPLY_ATTBONUS_PLAYERS],
				[localeinfo.DETAILS_1, item.APPLY_ATTBONUS_HUMAN],\
				[localeinfo.DETAILS_71, item.APPLY_MALL_ATTBONUS],\
				[localeinfo.DETAILS_12, item.APPLY_ATT_GRADE_BONUS],\
				[localeinfo.DETAILS_14, item.APPLY_NORMAL_HIT_DAMAGE_BONUS],\
				[localeinfo.DETAILS_16, item.APPLY_SKILL_DAMAGE_BONUS],\
				[localeinfo.DETAILS_18, item.APPLY_MELEE_MAGIC_ATTBONUS_PER],\
				[localeinfo.DETAILS_19, item.APPLY_MAGIC_ATTBONUS_PER],\
				[localeinfo.DETAILS_30, item.APPLY_ENCHANT_ELEC],\
				[localeinfo.DETAILS_31, item.APPLY_ENCHANT_ICE],\
				[localeinfo.DETAILS_32, item.APPLY_ENCHANT_DARK],\
				[localeinfo.DETAILS_33, item.APPLY_ENCHANT_FIRE],\
				[localeinfo.DETAILS_34, item.APPLY_ENCHANT_WIND],\
				[localeinfo.DETAILS_35, item.APPLY_ENCHANT_EARTH]\
			]\
		],\
	1 : [\
			localeinfo.BONUS_PAGE_DEFEND,
			[\
				[localeinfo.DETAILS_72, item.APPLY_MALL_DEFBONUS],\
				[localeinfo.DETAILS_13, item.APPLY_DEF_GRADE_BONUS],\
				[localeinfo.DETAILS_15, item.APPLY_NORMAL_HIT_DEFEND_BONUS],\
				[localeinfo.DETAILS_17, item.APPLY_SKILL_DEFEND_BONUS],\
				[localeinfo.DETAILS_22, item.APPLY_ANTI_CRITICAL_PCT],\
				[localeinfo.DETAILS_23, item.APPLY_ANTI_PENETRATE_PCT],\
				[localeinfo.DETAILS_NEW_23, item.APPLY_SKILL_DEFEND_BONUS_BOSS_OR_MORE],\
				[localeinfo.DETAILS_NEW_24, item.APPLY_RESIST_ZC],\
				[localeinfo.DETAILS_76, item.APPLY_RESIST_MAGIC],\
				[localeinfo.DETAILS_24, item.APPLY_RESIST_ELEC],\
				[localeinfo.DETAILS_25, item.APPLY_RESIST_ICE],\
				[localeinfo.DETAILS_26, item.APPLY_RESIST_DARK],\
				[localeinfo.DETAILS_27, item.APPLY_RESIST_FIRE],\
				[localeinfo.DETAILS_28, item.APPLY_RESIST_WIND],\
				[localeinfo.DETAILS_29, item.APPLY_RESIST_EARTH],\
				[localeinfo.DETAILS_41, item.APPLY_RESIST_WARRIOR],\
				[localeinfo.DETAILS_42, item.APPLY_RESIST_ASSASSIN],\
				[localeinfo.DETAILS_43, item.APPLY_RESIST_SURA],\
				[localeinfo.DETAILS_44, item.APPLY_RESIST_SHAMAN],\
				[localeinfo.DETAILS_NEW_7, item.APPLY_RESIST_PLAYERS],\
				[localeinfo.DETAILS_46, item.APPLY_RESIST_SWORD],\
				[localeinfo.DETAILS_47, item.APPLY_RESIST_TWOHAND],\
				[localeinfo.DETAILS_48, item.APPLY_RESIST_DAGGER],\
				[localeinfo.DETAILS_50, item.APPLY_RESIST_BELL],\
				[localeinfo.DETAILS_51, item.APPLY_RESIST_FAN],\
				[localeinfo.DETAILS_52, item.APPLY_RESIST_BOW],\
				[localeinfo.DETAILS_ATTBONUS_SWORD, item.APPLY_RESIST_SWORD_REDUCTION],\
				[localeinfo.DETAILS_ATTBONUS_TWOHAND, item.APPLY_RESIST_TWOHAND_REDUCTION],\
				[localeinfo.DETAILS_ATTBONUS_DAGGER, item.APPLY_RESIST_DAGGER_REDUCTION],\
				[localeinfo.DETAILS_ATTBONUS_BELL, item.APPLY_RESIST_BELL_REDUCTION],\
				[localeinfo.DETAILS_ATTBONUS_FAN, item.APPLY_RESIST_FAN_REDUCTION],\
				[localeinfo.DETAILS_ATTBONUS_BOW, item.APPLY_RESIST_BOW_REDUCTION]\
			]\
		],\
	2 : [\
			localeinfo.BONUS_PAGE_OTHER,
			[\
				[localeinfo.DETAILS_HIT_PCT, item.APPLY_HIT_PCT],\
				[localeinfo.DETAILS_75, item.APPLY_MALL_GOLDBONUS],\
				[localeinfo.DETAILS_73, item.APPLY_MALL_EXPBONUS],\
				[localeinfo.DETAILS_68, item.APPLY_EXP_DOUBLE_BONUS],\
				[localeinfo.DETAILS_69, item.APPLY_GOLD_DOUBLE_BONUS],\
				[localeinfo.DETAILS_70, item.APPLY_ITEM_DROP_BONUS],\
				[localeinfo.DETAILS_53, item.APPLY_STUN_PCT],\
				[localeinfo.DETAILS_54, item.APPLY_SLOW_PCT],\
				[localeinfo.DETAILS_55, item.APPLY_POISON_PCT],\
				[localeinfo.DETAILS_56, item.APPLY_POISON_REDUCE],\
				[localeinfo.DETAILS_59, item.APPLY_STEAL_HP],\
				[localeinfo.DETAILS_60, item.APPLY_STEAL_SP],\
				[localeinfo.DETAILS_61, item.APPLY_HP_REGEN],\
				[localeinfo.DETAILS_62, item.APPLY_SP_REGEN],\
				[localeinfo.DETAILS_63, item.APPLY_BLOCK],\
				[localeinfo.DETAILS_64, item.APPLY_DODGE],\
				[localeinfo.DETAILS_65, item.APPLY_REFLECT_MELEE],\
				[localeinfo.DETAILS_66, item.APPLY_KILL_HP_RECOVER],\
				[localeinfo.DETAILS_67, item.APPLY_KILL_SP_RECOVER]\
			]\
		]\
}

CATEGORIES_STATS_DICT = {\
	0 : [\
			localeinfo.BONUS_PAGE_PVM,
			[\
				[localeinfo.DETAILS_PVM_1, player.POINT_MONSTER_KILLED],\
				[localeinfo.DETAILS_PVM_2, player.POINT_STONE_KILLED],\
				[localeinfo.DETAILS_PVM_3, player.POINT_BOSS_KILLED]\
			]\
		],\
	1 : [\
			localeinfo.BONUS_PAGE_PVP,
			[\
				[localeinfo.DETAILS_PVP_1, player.POINT_BLUE_PLAYER_KILLED],\
				[localeinfo.DETAILS_PVP_2, player.POINT_YELLOW_PLAYER_KILLED],\
				[localeinfo.DETAILS_PVP_3, player.POINT_RED_PLAYER_KILLED]\
			]\
		],\
}

POINT_PLUS_DICT = {\
}

POINT_PER_DICT = {\
}

DS_DIAMOND_1 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT1
DS_RUBY_1 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT2
DS_JADE_1 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT3
DS_SAPPHIRE_1 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT4
DS_GARNET_1 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT5
DS_ONYX_1 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT6
DS_AMETHYST_1 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT7

DS_DIAMOND_2 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT1 + 7
DS_RUBY_2 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT2 + 7
DS_JADE_2 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT3 + 7
DS_SAPPHIRE_2 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT4 + 7
DS_GARNET_2 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT5 + 7
DS_ONYX_2 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT6 + 7
DS_AMETHYST_2 = player.DRAGON_SOUL_EQUIPMENT_SLOT_START + item.DS_SLOT7 + 7

SLOT_NUM_LIST = [\
	player.WEAR_BODY,\
	player.WEAR_HEAD,\
	player.WEAR_FOOTS,\
	player.WEAR_SHIELD,\
	player.WEAR_WEAPON,\
	player.WEAR_ARROW,\
	player.WEAR_WRIST,\
	player.WEAR_NECK,\
	player.WEAR_EAR,\
	player.WEAR_BELT,\
	player.WEAR_GLOVE,\
	player.WEAR_COSTUME_BODY,\
	player.WEAR_COSTUME_HAIR,\
	player.WEAR_COSTUME_WEAPON,\
	player.WEAR_PENDANT_FIRE,\
	player.WEAR_PENDANT_ICE,\
	player.WEAR_PENDANT_THUNDER,\
	player.WEAR_PENDANT_WIND,\
	player.WEAR_PENDANT_DARK,\
	player.WEAR_PENDANT_EARTH,\
	player.WEAR_PENDANT_SOUL_FIRST,\
	player.WEAR_PENDANT_SOUL_SECOND,\
	player.WEAR_PENDANT_YOHARA,\
	player.WEAR_UNIQUE1,\
	player.WEAR_UNIQUE2,\
	player.WEAR_COSTUME_MOUNT,\
	player.WEAR_RING1,\
	player.WEAR_RING2,\
	player.WEAR_COSTUME_ACCE,\
	player.WEAR_COSTUME_AURA,\
	player.WEAR_EX_THIEF_SLOT,\
	player.WEAR_EX_RING_SLOT,\
	player.WEAR_SHINING_WEAPON_1,\
	player.WEAR_SHINING_ARMOR_1,\
	player.WEAR_SHINING_SPECIAL,\
	DS_DIAMOND_1,\
	DS_RUBY_1,\
	DS_JADE_1,\
	DS_SAPPHIRE_1,\
	DS_GARNET_1,\
	DS_ONYX_1,\
	DS_AMETHYST_1,\
	DS_DIAMOND_2,\
	DS_RUBY_2,\
	DS_JADE_2,\
	DS_SAPPHIRE_2,\
	DS_GARNET_2,\
	DS_ONYX_2,\
	DS_AMETHYST_2,\
]

SLOT_DESC_DICT = {\
	player.WEAR_BODY : localeinfo.BONUS_PAGE_WEAR_BODY_DESCRIPTION,\
	player.WEAR_HEAD : localeinfo.BONUS_PAGE_WEAR_HEAD_DESCRIPTION,\
	player.WEAR_FOOTS : localeinfo.BONUS_PAGE_WEAR_FOOTS_DESCRIPTION,\
	player.WEAR_SHIELD : localeinfo.BONUS_PAGE_WEAR_SHIELD_DESCRIPTION,\
	player.WEAR_WEAPON : localeinfo.BONUS_PAGE_WEAR_WEAPON_DESCRIPTION,\
	player.WEAR_ARROW : localeinfo.BONUS_PAGE_WEAR_ARROW_DESCRIPTION,\
	player.WEAR_WRIST : localeinfo.BONUS_PAGE_WEAR_WRIST_DESCRIPTION,\
	player.WEAR_NECK : localeinfo.BONUS_PAGE_WEAR_NECK_DESCRIPTION,\
	player.WEAR_EAR : localeinfo.BONUS_PAGE_WEAR_EAR_DESCRIPTION,\
	player.WEAR_BELT : localeinfo.BONUS_PAGE_WEAR_BELT_DESCRIPTION,\
	player.WEAR_GLOVE : localeinfo.BONUS_PAGE_WEAR_GLOVE_DESCRIPTION,\
	player.WEAR_COSTUME_BODY : localeinfo.BONUS_PAGE_WEAR_COSTUME_BODY_DESCRIPTION,\
	player.WEAR_COSTUME_HAIR : localeinfo.BONUS_PAGE_WEAR_COSTUME_HAIR_DESCRIPTION,\
	player.WEAR_COSTUME_WEAPON : localeinfo.BONUS_PAGE_WEAR_COSTUME_WEAPON_DESCRIPTION,\
	player.WEAR_PENDANT_FIRE : localeinfo.BONUS_PAGE_WEAR_PENDANT_FIRE_DESCRIPTION,\
	player.WEAR_PENDANT_ICE : localeinfo.BONUS_PAGE_WEAR_PENDANT_ICE_DESCRIPTION,\
	player.WEAR_PENDANT_THUNDER : localeinfo.BONUS_PAGE_WEAR_PENDANT_THUNDER_DESCRIPTION,\
	player.WEAR_PENDANT_WIND : localeinfo.BONUS_PAGE_WEAR_PENDANT_WIND_DESCRIPTION,\
	player.WEAR_PENDANT_DARK : localeinfo.BONUS_PAGE_WEAR_PENDANT_DARK_DESCRIPTION,\
	player.WEAR_PENDANT_EARTH : localeinfo.BONUS_PAGE_WEAR_PENDANT_EARTH_DESCRIPTION,\
	player.WEAR_PENDANT_SOUL_FIRST : localeinfo.BONUS_PAGE_WEAR_PENDANT_SOUL_FIRST_DESCRIPTION,\
	player.WEAR_PENDANT_SOUL_SECOND : localeinfo.BONUS_PAGE_WEAR_PENDANT_SOUL_SECOND_DESCRIPTION,\
	player.WEAR_PENDANT_YOHARA : localeinfo.BONUS_PAGE_WEAR_PENDANT_YOHARA_DESCRIPTION,\
	player.WEAR_UNIQUE1 : localeinfo.BONUS_PAGE_WEAR_UNIQUE1_DESCRIPTION,\
	player.WEAR_UNIQUE2 : localeinfo.BONUS_PAGE_WEAR_UNIQUE2_DESCRIPTION,\
	player.WEAR_COSTUME_MOUNT : localeinfo.BONUS_PAGE_WEAR_COSTUME_MOUNT_DESCRIPTION,\
	player.WEAR_RING1 : localeinfo.BONUS_PAGE_WEAR_RING1_DESCRIPTION,\
	player.WEAR_RING2 : localeinfo.BONUS_PAGE_WEAR_RING2_DESCRIPTION,\
	player.WEAR_COSTUME_ACCE : localeinfo.BONUS_PAGE_WEAR_COSTUME_ACCE_DESCRIPTION,\
	player.WEAR_COSTUME_AURA : localeinfo.BONUS_PAGE_WEAR_COSTUME_AURA_DESCRIPTION,\
	player.WEAR_EX_THIEF_SLOT : localeinfo.BONUS_PAGE_WEAR_EX_THIEF_SLOT_DESCRIPTION,\
	player.WEAR_EX_RING_SLOT : localeinfo.BONUS_PAGE_WEAR_EX_RING_SLOT_DESCRIPTION,\
	player.WEAR_SHINING_WEAPON_1 : localeinfo.BONUS_PAGE_WEAR_SHINING_WEAPON_1_DESCRIPTION,\
	player.WEAR_SHINING_ARMOR_1 : localeinfo.BONUS_PAGE_WEAR_SHINING_ARMOR_1_DESCRIPTION,\
	player.WEAR_SHINING_SPECIAL : localeinfo.BONUS_PAGE_WEAR_SHINING_SPECIAL_DESCRIPTION,\
	DS_DIAMOND_1 : localeinfo.BONUS_PAGE_WEAR_DS_DIAMOND,\
	DS_RUBY_1 : localeinfo.BONUS_PAGE_WEAR_DS_RUBY,\
	DS_JADE_1 : localeinfo.BONUS_PAGE_WEAR_DS_JADE,\
	DS_SAPPHIRE_1 : localeinfo.BONUS_PAGE_WEAR_DS_SAPPHIRE,\
	DS_GARNET_1 : localeinfo.BONUS_PAGE_WEAR_DS_GARNET,\
	DS_ONYX_1 : localeinfo.BONUS_PAGE_WEAR_DS_ONYX,\
	DS_AMETHYST_1 : localeinfo.BONUS_PAGE_WEAR_DS_AMETHYST,\
	DS_DIAMOND_2 : localeinfo.BONUS_PAGE_WEAR_DS_DIAMOND,\
	DS_RUBY_2 : localeinfo.BONUS_PAGE_WEAR_DS_RUBY,\
	DS_JADE_2 : localeinfo.BONUS_PAGE_WEAR_DS_JADE,\
	DS_SAPPHIRE_2 : localeinfo.BONUS_PAGE_WEAR_DS_SAPPHIRE,\
	DS_GARNET_2 : localeinfo.BONUS_PAGE_WEAR_DS_GARNET,\
	DS_ONYX_2 : localeinfo.BONUS_PAGE_WEAR_DS_ONYX,\
	DS_AMETHYST_2 : localeinfo.BONUS_PAGE_WEAR_DS_AMETHYST\
}

SLOT_NUM_CATEGORY_NUM_DICT = {\
	player.WEAR_BODY : 1,\
	player.WEAR_HEAD : 1,\
	player.WEAR_FOOTS : 1,\
	player.WEAR_SHIELD : 1,\
	player.WEAR_WEAPON : 2,\
	player.WEAR_ARROW : 2,\
	player.WEAR_WRIST : 3,\
	player.WEAR_NECK : 3,\
	player.WEAR_EAR : 3,\
	player.WEAR_BELT : 3,\
	player.WEAR_GLOVE : 3,\
	player.WEAR_COSTUME_BODY : 4,\
	player.WEAR_COSTUME_HAIR : 4,\
	player.WEAR_COSTUME_WEAPON : 4,\
	player.WEAR_PENDANT_FIRE : 5,\
	player.WEAR_PENDANT_ICE : 5,\
	player.WEAR_PENDANT_THUNDER : 5,\
	player.WEAR_PENDANT_WIND : 5,\
	player.WEAR_PENDANT_DARK : 5,\
	player.WEAR_PENDANT_EARTH : 5,\
	player.WEAR_PENDANT_SOUL_FIRST : 5,\
	player.WEAR_PENDANT_SOUL_SECOND : 5,\
	player.WEAR_PENDANT_YOHARA : 5,\
	player.WEAR_UNIQUE1 : 7,\
	player.WEAR_UNIQUE2 : 7,\
	player.WEAR_COSTUME_MOUNT : 7,\
	player.WEAR_RING1 : 7,\
	player.WEAR_RING2 : 7,\
	player.WEAR_COSTUME_ACCE : 7,\
	player.WEAR_COSTUME_AURA : 7,\
	player.WEAR_EX_THIEF_SLOT : 7,\
	player.WEAR_EX_RING_SLOT : 7,\
	player.WEAR_SHINING_WEAPON_1 : 7,\
	player.WEAR_SHINING_ARMOR_1 : 7,\
	player.WEAR_SHINING_SPECIAL : 7,\
	DS_DIAMOND_1 : 6,\
	DS_RUBY_1 : 6,\
	DS_JADE_1 : 6,\
	DS_SAPPHIRE_1 : 6,\
	DS_GARNET_1 : 6,\
	DS_ONYX_1 : 6,\
	DS_AMETHYST_1 : 6,\
	DS_DIAMOND_2 : 6,\
	DS_RUBY_2 : 6,\
	DS_JADE_2 : 6,\
	DS_SAPPHIRE_2 : 6,\
	DS_GARNET_2 : 6,\
	DS_ONYX_2 : 6,\
	DS_AMETHYST_2 : 6\
}

CATEGORY_NUM_DICT = {\
	1 : localeinfo.BONUS_PAGE_WEAR_CATEGORY_ARMOR,\
	2 : localeinfo.BONUS_PAGE_WEAR_CATEGORY_WEAPON,\
	3 : localeinfo.BONUS_PAGE_WEAR_CATEGORY_ACCESSORIES,\
	4 : localeinfo.BONUS_PAGE_WEAR_CATEGORY_COSTUMES,\
	5 : localeinfo.BONUS_PAGE_WEAR_CATEGORY_PENDANTS,\
	6 : localeinfo.BONUS_PAGE_WEAR_CATEGORY_DS,\
	7 : localeinfo.BONUS_PAGE_WEAR_CATEGORY_BOOST
}

class CharacterDetailsUI(ui.ScriptWindow):
	def OnOverInBonus(self, _name, _number, _point_number, _point_number_plus, _point_number_per):
		if not self.item_tool_tip:
			self.item_tool_tip = uitooltip.ItemToolTip()

		self.item_tool_tip.ClearToolTip()

		_tmp_dict = {}
		_tmp_value = 0
		_tmp_total_value = 0

		_total_value = player.GetStatus(_point_number)

		if _point_number_plus != 0:
			_total_value += player.GetStatus(_point_number_plus)

		if _total_value != 0 and _point_number_per != 0:
			_pct = player.GetStatus(_point_number_per)
			if _pct != 0:
				_total_value += int(max((_total_value * _pct) / 100, 1))

		for _num in SLOT_NUM_LIST:
			_slot_num = _num

			_is_ds = True if SLOT_NUM_CATEGORY_NUM_DICT[_num] == 6 else False

			if _is_ds == False:
				_slot_num += player.EQUIPMENT_SLOT_START

			_item_vnum = player.GetItemIndex(_slot_num)
			if _item_vnum == 0:
				continue

			if _is_ds == True:
				if player.GetItemMetinSocket(_slot_num, 2) == 0:
					continue

				if player.GetItemMetinSocket(_slot_num, 0) < 1:
					continue

			_tmp_value = 0

			item.SelectItem(_item_vnum)

			_item_type = item.GetItemType()
			_item_sub_type = item.GetItemSubType()

			_is_sash_shoulder = False
			# _is_aura = False

			if (app.USE_ACCE_SYSTEM or app.USE_AURA_SYSTEM) and _item_type == item.ITEM_TYPE_COSTUME:
				if app.USE_ACCE_SYSTEM and _item_sub_type == item.COSTUME_TYPE_ACCE:
					_is_sash_shoulder = True

				# if app.USE_AURA_SYSTEM and _item_sub_type == item.COSTUME_TYPE_AURA:
					# _is_aura = True

			_apply_list = [item.GetAffect(i) for i in xrange(item.ITEM_APPLY_MAX_NUM)]

			for _apply in _apply_list:
				_type = _apply[0]
				_value = _apply[1]

				if _type == _number and _value != 0:
					_tmp_value += _value
					_tmp_total_value += _value
					break

			_attr_list = [player.GetItemAttribute(_slot_num, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

			# if _is_sash_shoulder == False and _is_aura == False:
			if _is_sash_shoulder == False:
				for _attr in _attr_list:
					_type = _attr[0]
					_value = _attr[1]

					if _type == _number and _value != 0:
						_tmp_value += _value
						_tmp_total_value += _value
						break

			if app.ENABLE_APPLY_RANDOM:
				_apply_random_list = [player.GetItemApplyRandom(_slot_num, i) for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]

				# if _is_sash_shoulder == False and _is_aura == False:
				if _is_sash_shoulder == False:
					for _apply in _apply_random_list:
						_type = _apply[0]
						_value = _apply[1]

						if _type == _number and _value != 0:
							_tmp_value += _value
							_tmp_total_value += _value
							break

			if app.USE_ENCHANT_COSTUMES:
				_enchant_list = [player.GetItemEnchant(_slot_num, i) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]

				# if _is_sash_shoulder == False and _is_aura == False:
				if _is_sash_shoulder == False:
					for _enchant in _enchant_list:
						_left_time = max(0, _enchant[2] - app.GetGlobalTimeStamp())
						if _left_time > 0:
							_type = _enchant[0]
							_value = _enchant[1]

							if _type == _number and _value != 0:
								_tmp_value += _value
								_tmp_total_value += _value
								break

			_show_refinements = False

			if _is_sash_shoulder == True:
				_abosrbed_vnum = player.GetItemMetinSocket(_slot_num, acce.ABSORBED_SOCKET)
				if _abosrbed_vnum > 0:
					_rate = player.GetItemMetinSocket(_slot_num, acce.ABSORPTION_SOCKET)
					if _rate > 0:
						for _attr in _attr_list:
							_type = _attr[0]
							_value = _attr[1]

							if _type == _number and _value > 0:
								_value_rounded = int((round(_value * _rate) / 100) - .5) + int(int((round(_value * _rate) / 100) - .5) > 0)

								if _value_rounded <= 0:
									_value = 1
								else:
									_value = _value_rounded

								_tmp_value += _value
								_tmp_total_value += _value
								break

						if app.ENABLE_APPLY_RANDOM:
							for _apply in _apply_random_list:
								_type = _apply[0]
								_value = _apply[1]

								if _type == _number and _value > 0:
									_value_rounded = int((round(_value * _rate) / 100) - .5) + int(int((round(_value * _rate) / 100) - .5) > 0)

									if _value_rounded <= 0:
										_value = 1
									else:
										_value = _value_rounded

									_tmp_value += _value
									_tmp_total_value += _value
									break

						if app.USE_ENCHANT_COSTUMES:
							for _enchant in _enchant_list:
								_left_time = max(0, _enchant[2] - app.GetGlobalTimeStamp())
								if _left_time > 0:
									_type = _enchant[0]
									_value = _enchant[1]

									if _type == _number and _value > 0:
										_value_rounded = int((round(_value * _rate) / 100) - .5) + int(int((round(_value * _rate) / 100) - .5) > 0)

										if _value_rounded <= 0:
											_value = 1
										else:
											_value = _value_rounded

										_tmp_value += _value
										_tmp_total_value += _value
										break
			elif _item_type == item.ITEM_TYPE_ARMOR:
				if _item_sub_type == item.ARMOR_BODY:
					for i in xrange(player.METIN_SOCKET_MAX_NUM):
						_socket = player.GetItemMetinSocket(_slot_num, i)

						if app.ENABLE_ITEM_SOCKET5 and _socket == -1:
							continue

						_slot_type = self.item_tool_tip.GetMetinSocketType(_socket)
						if _slot_type == 0:
							continue

						_slot_item_index = self.item_tool_tip.GetMetinItemIndex(_socket)
						if _slot_item_index == 0 or _slot_item_index == constinfo.ERROR_METIN_STONE:
							continue

						item.SelectItem(_slot_item_index)

						_type, _value = item.GetAffect(0)
						if _type == _number and _value != 0:
							_tmp_value += _value
							_tmp_total_value += _value
							break
				elif _item_sub_type in (\
										item.ARMOR_WRIST,\
										item.ARMOR_NECK,\
										item.ARMOR_EAR):
					_show_refinements = True
				elif app.USE_GLOVE_SYSTEM and _item_sub_type == item.ARMOR_GLOVE:
					for i in xrange(player.METIN_SOCKET_MAX_NUM):
						_socket = player.GetItemMetinSocket(_slot_num, i)

						if app.ENABLE_ITEM_SOCKET5 and _socket == -1:
							continue
						elif _socket < 1000000:
							continue

						__item_index = _socket

						if _socket >= 1000000:
							__item_index = item.ITEM_METIN_SUNGMA_VNUM_INDEX
							__item_index += (((_socket / 1000) % 10) * 100)
							__item_index += ((_socket / 100) % 10) - 1

						_slot_type = self.item_tool_tip.GetMetinSocketType(__item_index)
						if _slot_type == 0:
							continue

						_slot_item_index = self.item_tool_tip.GetMetinItemIndex(__item_index)
						if _slot_item_index == 0 or _slot_item_index == constinfo.ERROR_METIN_STONE:
							continue

						_type = (_socket / 10000) % 1000
						_value = _socket % 100
						if _type == _number and _value != 0:
							_tmp_value += _value
							_tmp_total_value += _value
							break
			elif _item_type == item.ITEM_TYPE_WEAPON:
				if _item_sub_type in (\
										item.WEAPON_SWORD,\
										item.WEAPON_DAGGER,\
										item.WEAPON_BOW,\
										item.WEAPON_TWO_HANDED,\
										item.WEAPON_BELL,\
										item.WEAPON_FAN,\
										item.WEAPON_CLAW):
					for i in xrange(player.METIN_SOCKET_MAX_NUM):
						_socket = player.GetItemMetinSocket(_slot_num, i)

						if app.ENABLE_ITEM_SOCKET5 and _socket == -1:
							continue

						_slot_type = self.item_tool_tip.GetMetinSocketType(_socket)
						if _slot_type == 0:
							continue

						_slot_item_index = self.item_tool_tip.GetMetinItemIndex(_socket)
						if _slot_item_index == 0 or _slot_item_index == constinfo.ERROR_METIN_STONE:
							continue

						item.SelectItem(_slot_item_index)

						_type, _value = item.GetAffect(0)
						if _type == _number and _value != 0:
							_tmp_value += _value
							_tmp_total_value += _value
							break
			elif _item_type == item.ITEM_TYPE_BELT:
				_show_refinements = True

			if _show_refinements == True and player.GetItemMetinSocket(_slot_num, 2) > 0:
				_material_vnum = constinfo.GET_ACCESSORY_MATERIAL_VNUM(_item_vnum, _item_sub_type)

				ACCESSORY_SOCKET_MAX_SIZE = 3
				_curr = min(player.GetItemMetinSocket(_slot_num, 0), ACCESSORY_SOCKET_MAX_SIZE)
				_end = min(player.GetItemMetinSocket(_slot_num, 1), ACCESSORY_SOCKET_MAX_SIZE)

				_type1 = _apply_list[0][0]

				if app.ENABLE_APPLY_RANDOM and _type1 == item.APPLY_RANDOM:
					_type1 = _apply_random_list[0][0]
					_value = _apply_random_list[0][1]
				else:
					_value = _apply_list[0][1]

				_value_list1 = [0, max(1, _value * 10 / 100), max(2, _value * 20 / 100), max(3, _value * 40 / 100)]

				_type2 = _apply_list[1][0]

				if app.ENABLE_APPLY_RANDOM and _type2 == item.APPLY_RANDOM:
					_type2 = _apply_random_list[1][0]
					_value = _apply_random_list[1][1]
				else:
					_value = _apply_list[1][1]

				_value_list2 = [0, max(1, _value * 10 / 100), max(2, _value * 20 / 100), max(3, _value * 40 / 100)]

				_type3 = _apply_list[2][0]

				if app.ENABLE_APPLY_RANDOM and _type3 == item.APPLY_RANDOM:
					_type3 = _apply_random_list[2][0]
					_value = _apply_random_list[2][1]
				else:
					_value = _apply_list[2][1]

				_value_list3 = [0, max(1, _value * 10 / 100), max(2, _value * 20 / 100), max(3, _value * 40 / 100)]

				_material_pos = 0
				_material_list = [_material_vnum] * _curr + [player.METIN_SOCKET_TYPE_SILVER] * (_end - _curr)

				for _material in _material_list:
					_value = _value_list1[_material_pos + 1] - _value_list1[_material_pos]

					if _type1 == _number and _value != 0:
						_tmp_value += _value
						_tmp_total_value += _value

					_value = _value_list2[_material_pos + 1] - _value_list2[_material_pos]

					if _type2 == _number and _value != 0:
						_tmp_value += _value
						_tmp_total_value += _value

					_value = _value_list3[_material_pos + 1] - _value_list3[_material_pos]

					if _type3 == _number and _value != 0:
						_tmp_value += _value
						_tmp_total_value += _value

					_material_pos += 1

			if _tmp_value == 0:
				continue

			_text = SLOT_DESC_DICT[_num]

			if _tmp_value > 0:
				_text += " {}%|cFF8AB98E".format(_tmp_value)
			else:
				_text += " |cFFE67976{}%|r".format(_tmp_value)

			_cat_num = SLOT_NUM_CATEGORY_NUM_DICT[_num]

			if not _tmp_dict.has_key(_cat_num):
				_tmp_dict[_cat_num] = _text
			else:
				_tmp_dict[_cat_num] += ", {}".format(_text)

		self.item_tool_tip.AppendTextLine(_name, self.item_tool_tip.TITLE_COLOR)

		if len(_tmp_dict) == 0:
			self.item_tool_tip.AppendSpace(5)
			self.item_tool_tip.AppendTextLine(localeinfo.BONUS_PAGE_SOURCE_CAME_FROM_NONE)
		else:
			for _key, _value in sorted(_tmp_dict.items()):
				self.item_tool_tip.AppendSpace(5)
				self.item_tool_tip.AppendTextLine(CATEGORY_NUM_DICT[_key])
				self.item_tool_tip.AppendTextLine("{}.".format(_value))

		if _total_value != _tmp_total_value:
			_value_difference = _total_value - _tmp_total_value

			if _value_difference != 0:
				_text = ""

				if _value_difference > 0:
					_text = " {}%|cFF8AB98E".format(_value_difference)
				else:
					_text = " |cFFE67976{}%|r.".format(_value_difference)

				self.item_tool_tip.AppendSpace(5)
				self.item_tool_tip.AppendTextLine(localeinfo.BONUS_PAGE_WEAR_CATEGORY_OTHER)
				self.item_tool_tip.AppendTextLine(_text)

		self.item_tool_tip.Show()

	def OnOverOutBonus(self):
		if self.item_tool_tip:
			self.item_tool_tip.Hide()

	def RefreshStatus(self, _open = False):
		if not _open and not self.IsShow():
			return

		for _category in self.container_elements_dict.values():
			for _element in _category:
				_bonus = _element[5]
				_value = player.GetStatus(_bonus.point_type)

				if _bonus.point_plus_type != 0:
					_value += player.GetStatus(_bonus.point_plus_type)

				if _value != 0 and _bonus.point_per_type != 0:
					_pct = player.GetStatus(_bonus.point_per_type)
					if _pct != 0:
						_value += int(max((_value * _pct) / 100, 1))

				_bonus.SetText(str(_value))

		for _category in self.container_stats_elements_dict.values():
			for _element in _category:
				_bonus = _element[5]
				_value = player.GetStatus(_bonus.point_type)

				_bonus.SetText(str(_value))

		for i in range(2):
			for _element in self.search_elements_dict[i].values():
				_bonus = _element[5]
				_value = player.GetStatus(_bonus.point_type)

				if i == 0:
					if _bonus.point_plus_type != 0:
						_value += player.GetStatus(_bonus.point_plus_type)

					if _value != 0 and _bonus.point_per_type != 0:
						_pct = player.GetStatus(_bonus.point_per_type)
						if _pct != 0:
							_value += int(max((_value * _pct) / 100, 1))

				_bonus.SetText(str(_value))

	def AdjustPosition(self, x, y):
		self.SetPosition(x, y)

	def Open(self):
		self.RefreshStatus(True)
		self.Show()

	def Hide(self):
		if self.search_input and self.search_input.IsFocus():
			self.search_input.KillFocus()

		self.OnOverOutBonus()
		wndMgr.Hide(self.hWnd)

	def Close(self):
		self.Hide()

	def ChangeScrollbar(self):
		if not self.scrollBar:
			return

		_hide = False

		if self.container_board.IsShow():
			if self.container.GetHeight() <= self.scroll_board.GetHeight():
				_hide = True
			else:
				self.scrollBar.SetScale(self.scroll_board.GetHeight(), self.container.GetHeight())
				self.scrollBar.SetPosScale(truediv(abs(self.container.GetLocalPosition()[1]), (self.container.GetHeight() - self.scroll_board.GetHeight())))
		elif self.container_board_stats.IsShow():
			if self.container_stats.GetHeight() <= self.scroll_board_stats.GetHeight():
				_hide = True
			else:
				self.scrollBar.SetScale(self.scroll_board_stats.GetHeight(), self.container_stats.GetHeight())
				self.scrollBar.SetPosScale(truediv(abs(self.container_stats.GetLocalPosition()[1]), (self.container_stats.GetHeight() - self.scroll_board_stats.GetHeight())))
		elif self.search_container_board.IsShow():
			if self.scroll_search_board.GetHeight() <= self.search_peek_board.GetHeight():
				_hide = True
			else:
				self.scrollBar.SetScale(self.search_peek_board.GetHeight(), self.scroll_search_board.GetHeight())
				self.scrollBar.SetPosScale(truediv(abs(self.scroll_search_board.GetLocalPosition()[1]), (self.scroll_search_board.GetHeight() - self.search_peek_board.GetHeight())))
				self.scrollBar.Show()
		else:
			_hide = True

		if _hide:
			self.scrollBar.Hide()

			self.mainboard.SetSize(self.original_mainboard_width, self.original_mainboard_height)
			self.board.SetSize(self.original_board_width, self.original_board_height)
			self.SetSize(self.original_board_width, self.original_board_height)

			self.title_bar.SetWidth(self.original_titlebar_width)
			self.title_name.SetPosition(self.original_titlebar_width / 2, 3)
			self.search_image.SetPosition(self.original_search_image_board_x, self.original_search_image_board_y)
			self.search_button_reset.SetPosition(self.original_search_button_reset_board_x, self.original_search_button_reset_board_y)
			self.type_bonuses_button.SetPosition(self.original_type_bonuses_button_board_x, self.original_type_bonuses_button_board_y)
			self.type_stats_button.SetPosition(self.original_type_stats_button_board_x, self.original_type_stats_button_board_y)
		else:
			self.SetSize(self.original_board_width + 11, self.original_board_height)
			self.board.SetSize(self.original_board_width + 11, self.original_board_height)
			self.mainboard.SetSize(self.original_mainboard_width + 11, self.original_mainboard_height)

			self.title_bar.SetWidth(self.original_titlebar_width + 11)
			self.title_name.SetPosition((self.original_titlebar_width + 11) / 2, 3)

			if localeinfo.IsARABIC():
				self.search_image.SetPosition(self.original_search_image_board_x - 5, self.original_search_image_board_y)
				self.search_button_reset.SetPosition(self.original_search_button_reset_board_x - 5, self.original_search_button_reset_board_y)
			else:
				self.search_image.SetPosition(self.original_search_image_board_x + 5, self.original_search_image_board_y)
				self.search_button_reset.SetPosition(self.original_search_button_reset_board_x + 5, self.original_search_button_reset_board_y)

			self.type_bonuses_button.SetPosition(self.original_type_bonuses_button_board_x + 5, self.original_type_bonuses_button_board_y)
			self.type_stats_button.SetPosition(self.original_type_stats_button_board_x + 5, self.original_type_stats_button_board_y)

			self.scrollBar.Show()

	def UpdateScrollbar(self, val = 0):
		if self.container_board.IsShow():
			curr = min(0, max(self.container.GetLocalPosition()[1] + val, -self.container.GetHeight() + self.scroll_board.GetHeight()))
			self.container.SetPosition(0, curr)
		elif self.container_board_stats.IsShow():
			curr = min(0, max(self.container_stats.GetLocalPosition()[1] + val, -self.container_stats.GetHeight() + self.scroll_board_stats.GetHeight()))
			self.container_stats.SetPosition(0, curr)
		elif self.search_container_board.IsShow():
			curr = min(0, max(self.scroll_search_board.GetLocalPosition()[1] + val, -self.scroll_search_board.GetHeight() + self.search_peek_board.GetHeight()))
			self.scroll_search_board.SetPosition(0, curr)

		self.ChangeScrollbar()

	def OnScrollBar(self, fScale):
		if self.container_board.IsShow():
			curr = min(0, max(math.ceil((self.container.GetHeight() - self.scroll_board.GetHeight()) * fScale * -1.0), -self.container.GetHeight() + self.scroll_board.GetHeight()))
			self.container.SetPosition(0, curr)
		elif self.container_board_stats.IsShow():
			curr = min(0, max(math.ceil((self.container_stats.GetHeight() - self.scroll_board_stats.GetHeight()) * fScale * -1.0), -self.container_stats.GetHeight() + self.scroll_board_stats.GetHeight()))
			self.container_stats.SetPosition(0, curr)
		elif self.search_container_board.IsShow():
			curr = min(0, max(math.ceil((self.scroll_search_board.GetHeight() - self.search_peek_board.GetHeight()) * fScale * -1.0), -self.scroll_search_board.GetHeight() + self.search_peek_board.GetHeight()))
			self.scroll_search_board.SetPosition(0, curr)

	def OnRunMouseWheel(self, _length):
		if self.scrollBar and self.scrollBar.IsShow():
			if self.container_board and self.container_board.IsShow():
				if self.scrollBar.IsInPosition() or self.container_board.IsInPosition():
					self.UpdateScrollbar(int((_length * 0.01) * SCROLL_SPEED))
					return True
			elif self.container_board_stats and self.container_board_stats.IsShow():
				if self.scrollBar.IsInPosition() or self.container_board_stats.IsInPosition():
					self.UpdateScrollbar(int((_length * 0.01) * SCROLL_SPEED))
					return True
			elif self.search_container_board and self.search_container_board.IsShow():
				if self.scrollBar.IsInPosition() or self.search_container_board.IsInPosition():
					self.UpdateScrollbar(int((_length * 0.01) * SCROLL_SPEED))
					return True

		return False

	def OnToggleCategory(self, _page_type, _i):
		if _page_type == PAGE_BONUSES:
			self.container.RecalculateHeight()
		else:
			self.container_stats.RecalculateHeight()

		self.UpdateScrollbar()

	def GetBonusByHint(self, _hint):
		_results_list = []

		if isinstance(_hint, str) and len(_hint) > 0:
			hint_lower = _hint.lower()

			if self.page_type == PAGE_BONUSES:
				for _key, _value in self.search_elements_dict[0].items():
					if isinstance(_value[0], str) and len(_value[0]) > 0:
						name_lower = _value[0].lower()

						# if len(name_lower) < len(hint_lower):
							# continue

						# if name_lower.startswith(hint_lower):
							# _results_list.append(_key)

						if hint_lower in name_lower:
							_results_list.append(_key)
			else:
				for _key, _value in self.search_elements_dict[1].items():
					if isinstance(_value[0], str) and len(_value[0]) > 0:
						name_lower = _value[0].lower()

						# if len(name_lower) < len(hint_lower):
							# continue

						# if name_lower.startswith(hint_lower):
							# _results_list.append(_key)

						if hint_lower in name_lower:
							_results_list.append(_key)

		return _results_list

	def OnUpdateNameInput(self):
		self.search_input_result = None
		self.search_input_hint.SetText("")
		self.search_input.SetPackedFontColor(SEARCH_FOUND_COLOR)

		_hint = self.search_input.GetText()

		if isinstance(_hint, str) and len(_hint) > 0:
			if self.page_type == PAGE_BONUSES:
				if app.USE_CLIP_MASK:
					self.container_board.Hide()
				else:
					self.peek_board.Hide()
			else:
				if app.USE_CLIP_MASK:
					self.container_board_stats.Hide()
				else:
					self.peek_board_stats.Hide()

			_list = self.GetBonusByHint(_hint)
			_list_len = len(_list)

			if _list_len > 0:
				_list_sorted = tuple(sorted(_list))
				_list_sorted_hash = hash(_list_sorted)

				if self.page_type == PAGE_BONUSES:
					self.search_input_result = self.search_elements_dict[0][_list[0]][0]
					self.search_input_hint.SetText(_hint + " " + self.search_elements_dict[0][_list[0]][0][len(_hint):])

					if _list_sorted_hash != self.last_list_sorted_hash:
						self.search_container_board.Hide()

						self.last_list_sorted_hash = _list_sorted_hash

						i = 0

						for v in self.search_elements_dict[1].values():
							v[1].Hide()

						for k, v in self.search_elements_dict[0].items():
							if k in _list_sorted:
								v[1].SetPosition(0, (25 + 3) * i)
								v[1].Show()

								i += 1
							else:
								v[1].Hide()

						self.scroll_search_board.SetSize(self.scroll_search_board.GetWidth(), ((25 + 3) * _list_len) - 3)
						self.scroll_search_board.Show()

				else:
					self.search_input_result = self.search_elements_dict[1][_list[0]][0]
					self.search_input_hint.SetText(_hint + " " + self.search_elements_dict[1][_list[0]][0][len(_hint):])

					if _list_sorted_hash != self.last_list_sorted_hash:
						self.search_container_board.Hide()

						self.last_list_sorted_hash = _list_sorted_hash

						i = 0

						for v in self.search_elements_dict[0].values():
							v[1].Hide()

						for k, v in self.search_elements_dict[1].items():
							if k in _list_sorted:
								v[1].SetPosition(0, (25 + 3) * i)
								v[1].Show()

								i += 1
							else:
								v[1].Hide()

						self.scroll_search_board.SetSize(self.scroll_search_board.GetWidth(), ((25 + 3) * _list_len) - 3)
						self.scroll_search_board.Show()

				self.search_container_board.Show()
			else:
				self.search_input.SetPackedFontColor(SEARCH_NOTFOUND_COLOR)

				self.scroll_search_board.SetSize(self.scroll_search_board.GetWidth(), 0)
				self.scroll_search_board.Hide()

				self.search_container_board.Show()
		else:
			self.search_container_board.Hide()

			if self.page_type == PAGE_BONUSES:
				if app.USE_CLIP_MASK:
					self.container_board.Show()
				else:
					self.peek_board.Show()
			else:
				if app.USE_CLIP_MASK:
					self.container_board_stats.Show()
				else:
					self.peek_board_stats.Show()

		self.UpdateScrollbar()

	def OnAutoCompleteInput(self):
		if isinstance(self.search_input_result, str) and len(self.search_input_result) > 0:
			self.search_input.SetText(self.search_input_result)
			self.OnUpdateNameInput()

		self.search_input.SetEndPosition()

	def ResetSearchField(self, _escape):
		if _escape:
			if not self.search_input.IsFocus():
				if self.main_parent:
					self.main_parent.Close()
					return True

		if self.search_input.IsFocus():
			self.search_input.KillFocus()

		self.search_input.SetText("")
		self.OnUpdateNameInput()
		return True

	def OnPressEscapeKey(self):
		if self.main_parent:
			self.main_parent.Close()

		return True

	def SetMainParent(self, _parent):
		if _parent:
			if isinstance(_parent, ProxyType):
				self.main_parent = _parent
			else:
				self.main_parent = proxy(_parent)

	def TitleBarClose(self):
		if self.main_parent:
			self.main_parent.ClickMinimizeButton()

	def SetBonusesPage(self):
		self.page_type = PAGE_BONUSES

		self.type_stats_button.SetUp()
		self.type_bonuses_button.Down()

		if app.USE_CLIP_MASK:
			self.container_board_stats.Hide()
			self.container_board.Show()
		else:
			self.peek_board_stats.Hide()
			self.peek_board.Show()

		self.ResetSearchField(False)

	def SetStatsPage(self):
		self.page_type = PAGE_STATS

		self.type_bonuses_button.SetUp()
		self.type_stats_button.Down()

		if app.USE_CLIP_MASK:
			self.container_board.Hide()
			self.container_board_stats.Show()
		else:
			self.peek_board.Hide()
			self.peek_board_stats.Show()

		self.ResetSearchField(False)

	def __Build(self):
		try:
			pyScriptLoader = ui.PythonScriptLoader()
			pyScriptLoader.LoadScriptFile(self, "uiscript/characterdetailswindow.py")

			self.search_board = self.GetChild("ui_search_board")
			self.board = self.GetChild("ui_board")
			self.title_bar = self.GetChild("ui_titlebar")
			self.title_name = self.GetChild("ui_titlename")
			self.mainboard = self.GetChild("ui_mainboard")

			self.container_board = self.GetChild("ui_container_board")
			self.peek_board = self.GetChild("ui_peek_board")

			if not app.USE_CLIP_MASK and app.ENABLE_INGAME_WIKI:
				self.peek_board.SetInsideRender(True)

			self.scroll_board = ui.Window()

			if app.USE_CLIP_MASK:
				self.scroll_board.SetParent(self.container_board)
			else:
				self.scroll_board.SetParent(self.peek_board)

			self.scroll_board.AddFlag("attach")
			self.scroll_board.AddFlag("not_pick")
			self.scroll_board.SetSize(self.peek_board.GetWidth(), self.peek_board.GetHeight())
			self.scroll_board.SetPosition(4 if app.USE_CLIP_MASK else 0, 4 if app.USE_CLIP_MASK else 0)

			if app.USE_CLIP_MASK:
				self.scroll_board.SetClippingMaskWindow(self.peek_board)

			self.scroll_board.Show()

			self.container_board_stats = self.GetChild("ui_container_board_stats")
			self.peek_board_stats = self.GetChild("ui_peek_board_stats")

			self.scroll_board_stats = ui.Window()

			if app.USE_CLIP_MASK:
				self.scroll_board_stats.SetParent(self.container_board_stats)
			else:
				self.scroll_board_stats.SetParent(self.peek_board_stats)

			self.scroll_board_stats.AddFlag("attach")
			self.scroll_board_stats.AddFlag("not_pick")
			self.scroll_board_stats.SetSize(self.peek_board_stats.GetWidth(), self.peek_board_stats.GetHeight())
			self.scroll_board_stats.SetPosition(4 if app.USE_CLIP_MASK else 0, 4 if app.USE_CLIP_MASK else 0)

			if app.USE_CLIP_MASK:
				self.scroll_board_stats.SetClippingMaskWindow(self.peek_board_stats)

			self.scroll_board_stats.Show()

			self.search_container_board = self.GetChild("ui_search_container_board")
			self.search_container_board.Hide()

			self.search_peek_board = self.GetChild("ui_search_peek_board")

			if not app.USE_CLIP_MASK and app.ENABLE_INGAME_WIKI:
				self.search_peek_board.SetInsideRender(True)

			self.scroll_search_board = ui.Window()

			self.scroll_search_board.SetParent(self.search_peek_board)

			self.scroll_search_board.AddFlag("attach")
			self.scroll_search_board.AddFlag("not_pick")
			self.scroll_search_board.SetSize(self.search_peek_board.GetWidth(), self.search_peek_board.GetHeight())
			self.scroll_search_board.SetPosition(0, 0)

			if app.USE_CLIP_MASK:
				self.scroll_search_board.SetClippingMaskWindow(self.search_peek_board)

			self.scroll_search_board.Show()

			self.search_image = self.GetChild("ui_search_image")

			self.search_input_result = None

			self.search_input = ui.EditLine()
			self.search_input.SetParent(self.search_image)
			self.search_input.SetMax(24 * 2)

			if localeinfo.IsARABIC():
				self.search_input.SetPosition(0, 5)
				self.search_input.SetSize(self.search_image.GetWidth() - 8, self.search_image.GetHeight())
			else:
				self.search_input.SetSize(self.search_image.GetWidth() - 4, self.search_image.GetHeight())
				self.search_input.SetPosition(6, 5)

			if app.USE_GRAPHIC_TEXT_SEARCH_BOX_WIDTH_LIMIT:
				self.search_input.SetSearchBoxLimitWidth(self.search_input.GetWidth() - 6)

			self.search_input.SetEscapeEvent(ui.__mem_func__(self.ResetSearchField), True)
			self.search_input.SetUpdateEvent(ui.__mem_func__(self.OnUpdateNameInput))
			self.search_input.SetTabEvent(ui.__mem_func__(self.OnAutoCompleteInput))
			self.search_input.Show()

			self.search_input_hint = ui.TextLine()
			self.search_input_hint.SetParent(self.search_input)
			self.search_input_hint.SetLimitWidth(self.search_input.GetWidth() - 6)
			self.search_input_hint.SetPackedFontColor(ui.WHITE_COLOR)

			if localeinfo.IsARABIC():
				self.search_input_hint.SetPosition(self.search_input.GetWidth(), 0)

			self.search_input_hint.Show()

			self.search_button_reset = self.GetChild("ui_search_button_reset")

			self.page_type = PAGE_BONUSES

			self.type_bonuses_button = self.GetChild("ui_type_bonuses_button")
			self.type_bonuses_button.SetEvent(ui.__mem_func__(self.SetBonusesPage))

			self.type_stats_button = self.GetChild("ui_type_stats_button")
			self.type_stats_button.SetEvent(ui.__mem_func__(self.SetStatsPage))
		except:
			import exception
			exception.Abort("CharacterDetailsUI.Get")

		try:
			self.title_bar.SetCloseEvent(ui.__mem_func__(self.TitleBarClose))

			self.search_button_reset.SetEvent(ui.__mem_func__(self.ResetSearchField), False)
			self.last_list_sorted_hash = None

			self.search_elements_dict = []
			self.search_elements_dict.append({})
			self.search_elements_dict.append({})

			_idx = 0

			self.container = ui.AutoGrowingVerticalContainerEx()
			self.container.SetParent(self.scroll_board)
			self.container.SetPosition(0, 0)
			self.container.SetWidth(self.scroll_board.GetWidth())

			self.container_elements_dict = {}

			for k, v in sorted(CATEGORIES_DICT.items()):
				tmp = None

				if localeinfo.IsARABIC():
					tmp = ui.ToggleAbleTitledWindow(IMG_PATH + "ae_category_off.png", IMG_PATH + "ae_category_on.png", None, 32, 6)#165
				else:
					tmp = ui.ToggleAbleTitledWindow(IMG_PATH + "category_off.png", IMG_PATH + "category_on.png", None, 32, 6,localeinfo.UI_BOLD_FONT)

				tmp.SetParent(self.container)
				tmp.SetWidth(self.scroll_board.GetWidth())
				tmp.SetPosition(0, 0)
				tmp.SetTitle(v[0])

				if len(v[1]) > 0:
					tmp.toggleIndicator.SetPosition(181 if localeinfo.IsARABIC() else 6, 8)
					tmp.SetToggleHideFilename(IMG_PATH + "plus.png")
					tmp.SetToggleShowFilename(IMG_PATH + "minus.png")

				tmp.SetOnToggleEvent(ui.__mem_func__(self.OnToggleCategory), PAGE_BONUSES, k)

				tmp.Close()
				tmp.Show()

				self.container.AppendItem(tmp)

				self.container_elements_dict[k] = []

				i = 0

				if len(v[1]) > 0:
					for bns_name, bns_number in v[1]:
						_point_number = item.GetApplyPoint(bns_number)
						_point_number_plus = POINT_PLUS_DICT[_point_number] if POINT_PLUS_DICT.has_key(_point_number) else 0
						_point_number_per = POINT_PER_DICT[_point_number] if POINT_PER_DICT.has_key(_point_number) else 0

						tmp_image = ui.ExpandedImageBox()
						tmp_image.LoadImage(IMG_PATH + "element.png")
						tmp_image.SetPosition(0, 0)
						tmp_image.Show()

						self.container.GetElementByIndex(k).AppendToToggleContent(tmp_image)

						tmp_name_wnd = ui.Window()
						tmp_name_wnd.SetParent(tmp_image)
						tmp_name_wnd.AddFlag("attach")
						tmp_name_wnd.SetSize(142, 18)
						tmp_name_wnd.SetPosition(2, 2)
						tmp_name_wnd.Show()
						tmp_name_wnd.SetOverInEvent(ui.__mem_func__(self.OnOverInBonus),\
													bns_name,\
													bns_number,\
													_point_number,\
													_point_number_plus,\
													_point_number_per)
						tmp_name_wnd.SetOverOutEvent(ui.__mem_func__(self.OnOverOutBonus))

						tmp_name_text = ui.MakeTextLine(tmp_name_wnd)
						tmp_name_text.SetLimitWidth(tmp_name_wnd.GetWidth())
						tmp_name_text.Show()

						tmp_name_text.SetText(bns_name)

						tmp_value_wnd = ui.Window()
						tmp_value_wnd.SetParent(tmp_image)
						tmp_value_wnd.SetSize(41, 18)
						tmp_value_wnd.SetPosition(154, 2)
						tmp_value_wnd.Show()

						tmp_value_text = ui.MakeTextLine(tmp_value_wnd)
						tmp_value_text.point_type = _point_number
						tmp_value_text.point_plus_type = _point_number_plus
						tmp_value_text.point_per_type = _point_number_per
						tmp_value_text.Show()

						self.container_elements_dict[k].append([i, tmp_image, tmp_name_wnd, tmp_name_text, tmp_value_wnd, tmp_value_text])

						tmp_image = ui.ExpandedImageBox()
						tmp_image.SetParent(self.scroll_search_board)
						tmp_image.LoadImage(IMG_PATH + "element.png")
						tmp_image.SetPosition(0, 0)
						tmp_image.Show()

						tmp_name_wnd = ui.Window()
						tmp_name_wnd.SetParent(tmp_image)
						tmp_name_wnd.AddFlag("attach")
						tmp_name_wnd.SetSize(142, 18)
						tmp_name_wnd.SetPosition(2, 2)
						tmp_name_wnd.Show()
						tmp_name_wnd.SetOverInEvent(ui.__mem_func__(self.OnOverInBonus),\
													bns_name,\
													bns_number,\
													_point_number,\
													_point_number_plus,\
													_point_number_per)
						tmp_name_wnd.SetOverOutEvent(ui.__mem_func__(self.OnOverOutBonus))

						tmp_name_text = ui.MakeTextLine(tmp_name_wnd)
						tmp_name_text.SetLimitWidth(tmp_name_wnd.GetWidth())
						tmp_name_text.Show()
						tmp_name_text.SetText(bns_name)

						tmp_value_wnd = ui.Window()
						tmp_value_wnd.SetParent(tmp_image)
						tmp_value_wnd.SetSize(41, 18)
						tmp_value_wnd.SetPosition(154, 2)
						tmp_value_wnd.Show()

						tmp_value_text = ui.MakeTextLine(tmp_value_wnd)
						tmp_value_text.point_type = _point_number
						tmp_value_text.point_plus_type = _point_number_plus
						tmp_value_text.point_per_type = _point_number_per
						tmp_value_text.Show()

						self.search_elements_dict[0][_idx] = [bns_name, tmp_image, tmp_name_wnd, tmp_name_text, tmp_value_wnd, tmp_value_text]

						i += 1
						_idx += 1

			self.container.Show()
			self.container.RecalculateHeight()

			self.container_stats = ui.AutoGrowingVerticalContainerEx()
			self.container_stats.SetParent(self.scroll_board_stats)
			self.container_stats.SetPosition(0, 0)
			self.container_stats.SetWidth(self.scroll_board_stats.GetWidth())

			self.container_stats_elements_dict = {}

			for k, v in sorted(CATEGORIES_STATS_DICT.items()):
				tmp = None

				if localeinfo.IsARABIC():
					tmp = ui.ToggleAbleTitledWindow(IMG_PATH + "ae_category_off.png", IMG_PATH + "ae_category_on.png", None, 32, 6)#165
				else:
					tmp = ui.ToggleAbleTitledWindow(IMG_PATH + "category_off.png", IMG_PATH + "category_on.png", None, 32, 6,localeinfo.UI_BOLD_FONT)

				tmp.SetParent(self.container_stats)
				tmp.SetWidth(self.scroll_board_stats.GetWidth())
				tmp.SetPosition(0, 0)
				tmp.SetTitle(v[0])

				if len(v[1]) > 0:
					tmp.toggleIndicator.SetPosition(181 if localeinfo.IsARABIC() else 6, 8)
					tmp.SetToggleHideFilename(IMG_PATH + "plus.png")
					tmp.SetToggleShowFilename(IMG_PATH + "minus.png")

				tmp.SetOnToggleEvent(ui.__mem_func__(self.OnToggleCategory), PAGE_STATS, k)

				tmp.Close()
				tmp.Show()

				self.container_stats.AppendItem(tmp)

				self.container_stats_elements_dict[k] = []

				i = 0

				if len(v[1]) > 0:
					for stat_name, point_number in v[1]:
						tmp_image = ui.ExpandedImageBox()
						tmp_image.LoadImage(IMG_PATH + "element.png")
						tmp_image.SetPosition(0, 0)
						tmp_image.Show()

						self.container_stats.GetElementByIndex(k).AppendToToggleContent(tmp_image)

						tmp_name_wnd = ui.Window()
						tmp_name_wnd.SetParent(tmp_image)
						tmp_name_wnd.AddFlag("attach")
						tmp_name_wnd.SetSize(142, 18)
						tmp_name_wnd.SetPosition(2, 2)
						tmp_name_wnd.Show()

						tmp_name_text = ui.MakeTextLine(tmp_name_wnd)
						tmp_name_text.SetLimitWidth(tmp_name_wnd.GetWidth())
						tmp_name_text.Show()

						tmp_name_text.SetText(stat_name)

						tmp_value_wnd = ui.Window()
						tmp_value_wnd.SetParent(tmp_image)
						tmp_value_wnd.SetSize(41, 18)
						tmp_value_wnd.SetPosition(154, 2)
						tmp_value_wnd.Show()

						tmp_value_text = ui.MakeTextLine(tmp_value_wnd)
						tmp_value_text.point_type = point_number
						tmp_value_text.Show()

						self.container_stats_elements_dict[k].append([i, tmp_image, tmp_name_wnd, tmp_name_text, tmp_value_wnd, tmp_value_text])

						tmp_image = ui.ExpandedImageBox()
						tmp_image.SetParent(self.scroll_search_board)
						tmp_image.LoadImage(IMG_PATH + "element.png")
						tmp_image.SetPosition(0, 0)
						tmp_image.Show()

						tmp_name_wnd = ui.Window()
						tmp_name_wnd.SetParent(tmp_image)
						tmp_name_wnd.AddFlag("attach")
						tmp_name_wnd.SetSize(142, 18)
						tmp_name_wnd.SetPosition(2, 2)
						tmp_name_wnd.Show()

						tmp_name_text = ui.MakeTextLine(tmp_name_wnd)
						tmp_name_text.SetLimitWidth(tmp_name_wnd.GetWidth())
						tmp_name_text.Show()
						tmp_name_text.SetText(stat_name)

						tmp_value_wnd = ui.Window()
						tmp_value_wnd.SetParent(tmp_image)
						tmp_value_wnd.SetSize(41, 18)
						tmp_value_wnd.SetPosition(154, 2)
						tmp_value_wnd.Show()

						tmp_value_text = ui.MakeTextLine(tmp_value_wnd)
						tmp_value_text.point_type = point_number
						tmp_value_text.Show()

						self.search_elements_dict[1][_idx] = [stat_name, tmp_image, tmp_name_wnd, tmp_name_text, tmp_value_wnd, tmp_value_text]

						i += 1
						_idx += 1

			self.container_stats.Show()
			self.container_stats.RecalculateHeight()

			self.original_board_width = self.GetWidth()
			self.original_board_height = self.GetHeight()

			self.original_mainboard_width = self.mainboard.GetWidth()
			self.original_mainboard_height = self.mainboard.GetHeight()

			self.original_titlebar_width = self.title_bar.GetWidth()
			self.original_titlebar_height = self.title_bar.GetHeight()

			self.original_search_image_board_x, self.original_search_image_board_y = self.search_image.GetLocalPosition()
			self.original_search_button_reset_board_x, self.original_search_button_reset_board_y = self.search_button_reset.GetLocalPosition()

			self.original_type_bonuses_button_board_x, self.original_type_bonuses_button_board_y = self.type_bonuses_button.GetLocalPosition()
			self.original_type_stats_button_board_x, self.original_type_stats_button_board_y = self.type_stats_button.GetLocalPosition()

			self.scrollBar = ui.ScrollBarToggle()
			self.scrollBar.run_in_wheel = False
			self.scrollBar.SetParent(self)
			self.scrollBar.SetPosition(11 + self.container_board.GetWidth() + 3, self.container_board.GetGlobalPosition()[1])
			self.scrollBar.SetSize(9, self.container_board.GetHeight())
			self.scrollBar.SetScrollEvent(self.OnScrollBar)
			self.scrollBar.SetScrollSpeed(SCROLL_SPEED)

			if not app.ENABLE_INGAME_WIKI and app.USE_CLIP_MASK:
				self.scroll_board.SetClippingMaskWindow(self.peek_board)
		except Exception as msg:
			import exception
			exception.Abort("CharacterDetailsUI.Bind")

		self.SetBonusesPage()

	def __init__(self):
		self.main_parent = None
		self.search_input = None
		self.item_tool_tip = None

		ui.ScriptWindow.__init__(self)
		self.__Build()

	def Destroy(self):
		if self.item_tool_tip:
			self.item_tool_tip.ClearToolTip()
			del self.item_tool_tip
			self.item_tool_tip = None

		self.parent = None

		# self.title_bar.SetCloseEvent(None)
		self.title_bar = None

		self.title_name = None

		self.search_image = None

		if self.search_input.IsFocus():
			self.search_input.KillFocus()

		self.search_button_reset.SetEvent(None)
		self.search_button_reset = None

		for _dict in self.search_elements_dict:
			for _element in _dict.values():
				del _element[5]
				del _element[4]
				del _element[3]

				_element[2].SetOverInEvent(None)
				_element[2].SetOverOutEvent(None)

				del _element[2]
				del _element[1]

			self.search_elements_dict = None

		del self.search_input_hint
		self.search_input_hint = None

		self.search_input.SetEscapeEvent(None)
		self.search_input.SetUpdateEvent(None)
		self.search_input.SetTabEvent(None)

		self.search_input_result = None

		self.scrollBar.ResetScrollEvent()
		self.scrollBar = None

		self.last_list_sorted_hash = None

		del self.search_input
		self.search_input = None

		del self.scroll_search_board
		self.scroll_search_board = None

		self.search_container_board = None
		self.search_peek_board = None

		del self.container
		self.container = None

		del self.scroll_board
		self.scroll_board = None

		for _category in self.container_elements_dict.values():
			for _element in _category:
				del _element[5]
				del _element[4]
				del _element[3]

				_element[2].SetOverInEvent(None)
				_element[2].SetOverOutEvent(None)

				del _element[2]
				del _element[1]

		self.container_elements_dict = None

		self.container_board = None
		self.peek_board = None

		self.search_container_board_stats = None
		self.search_peek_board_stats = None

		del self.container_stats
		self.container_stats = None

		del self.scroll_board_stats
		self.scroll_board_stats = None

		for _category in self.container_stats_elements_dict.values():
			for _element in _category:
				del _element[5]
				del _element[4]
				del _element[3]
				del _element[2]
				del _element[1]

		self.container_stats_elements_dict = None

		self.container_board_stats = None
		self.peek_board_stats = None

		self.search_board = None
		self.board = None
		self.mainboard = None

		self.original_board_width = None
		self.original_board_height = None

		self.original_mainboard_width = None
		self.original_mainboard_height = None

		self.original_titlebar_width = None
		self.original_titlebar_height = None

		self.original_search_image_board_x = None
		self.original_search_image_board_y = None

		self.original_search_button_reset_board_x = None
		self.original_search_button_reset_board_y = None

		self.original_type_bonuses_button_board_x = None
		self.original_type_bonuses_button_board_y = None

		self.original_type_stats_button_board_x = None
		self.original_type_stats_button_board_y = None

		self.main_parent = None

		self.type_bonuses_button.SetEvent(None)
		self.type_bonuses_button = None

		self.type_stats_button.SetEvent(None)
		self.type_stats_button = None

		self.ClearDictionary()

	def __del__(self):
		ui.ScriptWindow.__del__(self)
