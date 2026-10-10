#author: dracaryS

#static
import ui, constinfo, localeinfo
from operator import truediv

#dynamic
import grp, player, wndMgr, item, net, skill, nonplayer , app
import net
import uiofflineshop_ae
if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget
import ingamewiki

import systemSetting

IMG_DIR = "d:/ymir work/ui/game/reward_info/"
IMG_ICON_DIR = "d:/ymir work/ui/game/reward_info/icons/"

MEDAL_COLORS = [0xffffd700, 0xffc0c0c0, 0xffcd7f32]  # gold, silver, bronze
MEDAL_LABELS = ["1st", "2nd", "3rd"]
MEDAL_ICONS = ["1st.png", "2nd.png", "3rd.png"]
WINNER_X_POSITIONS = [274, 192, 110]
WINNER_Y = 18
MAX_NAME_DISPLAY = 10

def GetRewardItemsForPlacement(rewardData, placementIdx):
	"""Get reward items for a specific placement (0=1st, 1=2nd, 2=3rd).
	Supports both old format (reward_items) and new per-placement format."""
	keys = ["reward_items_1st", "reward_items_2nd", "reward_items_3rd"]
	if rewardData.has_key(keys[placementIdx]):
		return rewardData[keys[placementIdx]]
	if rewardData.has_key("reward_items"):
		return rewardData["reward_items"]
	return []

global_reward_info = {
	0: {
		"type": player.REWARD_MISSION_LEVEL_UP,
		"subValue": 120,
		"icon_name": "lvl_120",
		"reward_items_1st": [[80016, 3]],
		"reward_items_2nd": [[80016, 2]],
		"reward_items_3rd": [[80016, 1]]
	},
	1: {
		"type": player.REWARD_MISSION_ZODIAC_DUNGEON,
		"subValue": 1,
		"icon_name": "zodiac_dungeon",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	2: {
		"type": player.REWARD_MISSION_FIRST_ITEM,
		"subValue": 319,
		"icon_name": "zodiac_9",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	3: {
		"type": player.REWARD_MISSION_AVERAGE_BONUS_NEW,
		"subValue": 55,
		"icon_name": "average_55",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	4: {
		"type": player.REWARD_MISSION_AVERAGE_BONUS,
		"subValue": 59,
		"icon_name": "average_55_low",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	5: {
		"type": player.REWARD_MISSION_CUSTOM_SASH_ZODIAC,
		"subValue": 25,
		"icon_name": "sash_25",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	6: {
		"type": player.REWARD_MISSION_CUSTOM_SASH,
		"subValue": 1,
		"icon_name": "sash_25_1",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	7: {
		"type": player.REWARD_MISSION_USE_PENDENT,
		"subValue": 1,
		"icon_name": "soul",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	8: {
		"type": player.REWARD_MISSION_LEVEL_UP_PET,
		"subValue": 105,
		"icon_name": "pet_lv_115",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	9: {
		"type": player.REWARD_MISSION_DUNGEON,
		"subValue": 6118,
		"icon_name": "meley_dungeon",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	10: {
		"type": player.REWARD_MISSION_DUNGEON,
		"subValue": 3962,
		"icon_name": "hydra_dungeon",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	11: {
		"type": player.REWARD_MISSION_COMPLETE_SKILL,
		"subValue": 0,
		"icon_name": "perfect_master_1",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	12: {
		"type": player.REWARD_MISSION_FIRST_ITEM,
		"subValue": 88079,
		"icon_name": "tourmaline_bell_9",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	13: {
		"type": player.REWARD_MISSION_FIRST_ITEM,
		"subValue": 19299,
		"icon_name": "first_zodiac",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	14: {
		"type": player.REWARD_MISSION_FIRST_ITEM,
		"subValue": 12059,
		"icon_name": "first_kyanit",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	15: {
		"type": player.REWARD_MISSION_BATTLEPASS,
		"subValue": 0,
		"icon_name": "battlepass",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	16: {
		"type": player.REWARD_MISSION_BIOLOG,
		"subValue": 17,
		"icon_name": "bio_94",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	17: {
		"type": player.REWARD_MISSION_OFFLINESHOP_SLOT,
		"subValue": 160,
		"icon_name": "offlineshop_slot",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	18: {
		"type": player.REWARD_MISSION_FIRST_ITEM,
		"subValue": 939018,
		"icon_name": "first_blend",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	},
	19: {
		"type": player.REWARD_MISSION_FIRST_ITEM,
		"subValue": 49006,
		"icon_name": "aura",
		"reward_items_1st": [[80016, 2]],
		"reward_items_2nd": [[80016, 1]],
		"reward_items_3rd": [[80016, 1]]
	}
}

solo_reward_info = {
	0: {
		"type": player.REWARD_MISSION_KILL_STONE,
		"subValue": 0,
		"max_value": 500000,
		"level_difference": 15,
		"icon_name": "metinstone",
		"reward_items": [[60700, 10], [60702, 10], [39028, 2000], [25041, 1]]
	},
	1: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 0,
		"max_value": 2500,
		"level_difference": 0,
		"icon_name": "boss",
		"reward_items": [[50513, 10], [51501, 30], [39113, 50], [51001, 250], [25041, 1], [72006, 3]]
	},
	2: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 694,
		"max_value": 75,
		"level_difference": 0,
		"icon_name": "chief_orc",
		"reward_items": [[51501, 25], [38016, 30], [30182, 5], [25041, 1]]
	},
	3: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 1093,
		"max_value": 75,
		"level_difference": 0,
		"icon_name": "grim_reaper",
		"reward_items": [[50288, 20], [51501, 30], [38016, 30], [30182, 5], [25041, 1]]
	},
	4: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 2092,
		"max_value": 75,
		"level_difference": 0,
		"icon_name": "barones",
		"reward_items": [[54701, 20], [51501, 30], [38016, 30], [30182, 5], [25041, 1]]
	},
	5: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 2598,
		"max_value": 75,
		"level_difference": 0,
		"icon_name": "azrail",
		"reward_items": [[53586, 20], [51501, 30], [38016, 30], [30182, 5], [25041, 1]]
	},
	6: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 2493,
		"max_value": 100,
		"level_difference": 0,
		"icon_name": "beran",
		"reward_items": [[54700, 25], [51501, 40], [38016, 40], [30182, 6], [25041, 2]]
	},
	7: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 1095,
		"max_value": 100,
		"level_difference": 0,
		"icon_name": "blue_death",
		"reward_items": [[53587, 25], [51501, 40], [38016, 40], [30182, 6], [25041, 2]]
	},
	8: {
		"type": player.REWARD_MISSION_KILL_BOSS,
		"subValue": 5623,
		"max_value": 100,
		"level_difference": 0,
		"icon_name": "beran_dark",
		"reward_items": [[33064, 25], [51501, 40], [38016, 40], [30182, 6], [25041, 2]]
	},
	9: {
		"type": player.REWARD_MISSION_DUNGEON,
		"subValue": 0,
		"max_value": 500,
		"level_difference": 0,
		"icon_name": "dungeon",
		"reward_items": [[50288, 25], [54701, 25], [53586, 25], [54700, 25], [53587, 25], [33064, 25]]
	},
	10: {
		"type": player.REWARD_MISSION_SKILL_UPGRADE,
		"subValue": 1,
		"max_value": 2,
		"level_difference": 0,
		"icon_name": "perfect_master",
		"reward_items": [[51501, 25], [99100, 1], [39028, 2000]]
	},
	11: {
		"type": player.REWARD_MISSION_OFFLINESHOP_SLOT,
		"subValue": 1,
		"max_value": 40,
		"level_difference": 0,
		"icon_name": "offlineshop_slot",
		"reward_items": [[51501, 50], [25041, 1], [71153, 1], [100700, 2], [72703, 1]]
	},
	12: {
		"type": player.REWARD_MISSION_ENCHANT_ITEM,
		"subValue": 71151,
		"max_value": 50000,
		"level_difference": 0,
		"icon_name": "enchant_green",
		"reward_items": [[39028, 500], [51501, 15], [27987, 50]]
	},
	13: {
		"type": player.REWARD_MISSION_ENCHANT_ITEM,
		"subValue": 71084,
		"max_value": 100000,
		"level_difference": 0,
		"icon_name": "enchant",
		"reward_items": [[39028, 2000], [51501, 25], [25041, 1], [99101, 1]]
	},
	14: {
		"type": player.REWARD_MISSION_FISHING,
		"subValue": 1,
		"max_value": 1500,
		"level_difference": 0,
		"icon_name": "fishing",
		"reward_items": [[25041, 2], [51501, 50], [30182, 5], [72703, 1], [71153, 1], [100700, 2]]
	},
	15: {
		"type": player.REWARD_MISSION_SHOUT,
		"subValue": 1,
		"max_value": 3000,
		"level_difference": 0,
		"icon_name": "shout",
		"reward_items": [[25041, 1], [51501, 25], [30182, 3], [50513, 5], [38050, 50]]
	},
}

SCROLLBAR_HEIGHT = 337

def GetMissionName(pageIdx, type, subValue, levelDifference = 0):
	__localeText = {
		player.REWARD_MISSION_LEVEL_UP : localeinfo.REWARD_SYSTEM_MISSION_1,
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
	}
	missionName = ""
	if not __localeText.has_key(type):
		if type == player.REWARD_MISSION_PASSIVE_SKILL_COMPLETE:
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
					6118 : localeinfo.MAP_N_FLAME_DRAGON,#meley
					3962 : localeinfo.MAP_DEFENSE_WAVE#hydra
				}
				missionName = localeinfo.REWARD_SYSTEM_NAME_16 % (__dungeonNames[subValue] if __dungeonNames.has_key(subValue) else "Unknown")
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
			self.LoadImage(IMG_DIR+"item_0.png")
			self.Destroy()
			self.__children["rewardIndex"] = rewardIndex
			self.__children["selectedPlacement"] = 0

			self.__children["rewardImage"] = CreateWindow(ui.ImageBox(), self, (366, 0), IMG_ICON_DIR+rewardData["icon_name"]+".png")

			rewardName = CreateWindow(ui.TextLine(), self, (352, 55), GetMissionName(pageIdx, rewardData["type"], rewardData["subValue"]), "horizontal:left")
			rewardName.SetPackedFontColor(0xffdfe6e9)
			self.__children["rewardName"] = rewardName

			# Placement indicator icon (shows current placement trophy)
			placeIndicator = CreateWindow(ui.ImageBox(), self, (47, 64), IMG_DIR + MEDAL_ICONS[0])
			self.__children["placeIndicator"] = placeIndicator

			# Prev/Next arrow buttons
			prevBtn = ui.Button()
			prevBtn.SetParent(self)
			prevBtn.SetPosition(25, 64)
			prevBtn.SetUpVisual("d:/ymir work/ui/public/public_intro_btn/prev_btn_01.sub")
			prevBtn.SetDownVisual("d:/ymir work/ui/public/public_intro_btn/prev_btn_02.sub")
			prevBtn.SetOverVisual("d:/ymir work/ui/public/public_intro_btn/prev_btn_01.sub")
			prevBtn.SetEvent(ui.__mem_func__(self.OnPrevPlacement))
			prevBtn.Show()
			self.__children["prevBtn"] = prevBtn

			nextBtn = ui.Button()
			nextBtn.SetParent(self)
			nextBtn.SetPosition(69, 64)
			nextBtn.SetUpVisual("d:/ymir work/ui/public/public_intro_btn/next_btn_01.sub")
			nextBtn.SetDownVisual("d:/ymir work/ui/public/public_intro_btn/next_btn_02.sub")
			nextBtn.SetOverVisual("d:/ymir work/ui/public/public_intro_btn/next_btn_01.sub")
			nextBtn.SetEvent(ui.__mem_func__(self.OnNextPlacement))
			nextBtn.Show()
			self.__children["nextBtn"] = nextBtn

			self.SetRewardPlayers(rewardData["player_names"])
			self.RefreshRewardItems(rewardData, 0)

		def SetRewardPlayers(self, playerNames):
			for i in range(3):
				xPos = WINNER_X_POSITIONS[i]

				if i < len(playerNames) and playerNames[i] != "":
					trophyIcon = CreateWindow(ui.ImageBox(), self, (xPos, WINNER_Y), IMG_DIR + MEDAL_ICONS[i])
					self.__children["placeIcon_%d" % i] = trophyIcon

					displayName = playerNames[i]
					if len(displayName) > MAX_NAME_DISPLAY:
						displayName = displayName[:MAX_NAME_DISPLAY] + ".."
					nameText = CreateWindow(ui.TextLine(), self, (xPos + 18, WINNER_Y), displayName, "horizontal:left")
					nameText.SetPackedFontColor(MEDAL_COLORS[i])
					self.__children["player_%d" % i] = nameText

			allFilled = len(playerNames) >= 3 and all(n != "" for n in playerNames[:3])
			if allFilled:
				rewardDone = CreateWindow(ui.ImageBox(), self, (366, 0), IMG_ICON_DIR+"done.png")
				self.__children["rewardDone"] = rewardDone

		def RefreshRewardItems(self, rewardData, placementIdx):
			rewardItemsList = GetRewardItemsForPlacement(rewardData, placementIdx)

			grid = Grid(3,1)
			grid.reset()

			if self.__children.has_key("rewardItems"):
				rewardItems = self.__children["rewardItems"]
				rewardItems.ClearAllSlot()
				rewardItems.ArrangeSlot(0, 3, 1, 32, 32, 0, 0)
				rewardItems.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
			else:
				rewardItems = CreateWindow(ui.GridSlotWindow(), self, (8, 35))
				rewardItems.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
				rewardItems.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
				rewardItems.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
				rewardItems.SetUnselectItemSlotEvent(ui.__mem_func__(self.SearchInWiki))
				rewardItems.SAFE_SetButtonEvent("LEFT", "EXIST", self.RenderTarget)
				rewardItems.ArrangeSlot(0, 3, 1, 32, 32, 0, 0)
				rewardItems.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
				self.__children["rewardItems"] = rewardItems

			for rewardItem in rewardItemsList:
				(itemVnum,itemCount) = (rewardItem[0],rewardItem[1])
				item.SelectItem(itemVnum)
				(width,height) = item.GetItemSize()
				pos = grid.find_blank(width, height)
				grid.put(pos, width, height)
				rewardItems.SetItemSlot(pos, itemVnum, itemCount)
			rewardItems.RefreshSlot()

			# Update placement indicator icon
			if self.__children.has_key("placeIndicator"):
				self.__children["placeIndicator"].LoadImage(IMG_DIR + MEDAL_ICONS[placementIdx])

		def OnPrevPlacement(self):
			current = self.__children.get("selectedPlacement", 0)
			newIdx = (current - 1) % 3
			self.__children["selectedPlacement"] = newIdx
			rewardIndex = self.__children["rewardIndex"]
			rewardData = global_reward_info.get(rewardIndex)
			if rewardData:
				self.RefreshRewardItems(rewardData, newIdx)

		def OnNextPlacement(self):
			current = self.__children.get("selectedPlacement", 0)
			newIdx = (current + 1) % 3
			self.__children["selectedPlacement"] = newIdx
			rewardIndex = self.__children["rewardIndex"]
			rewardData = global_reward_info.get(rewardIndex)
			if rewardData:
				self.RefreshRewardItems(rewardData, newIdx)

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

	class RewardItemSolo(ui.ImageBox):
		def Destroy(self):
			self.__children = {}
		def GetRewardIndex(self):
			return self.__children["rewardIndex"] if self.__children.has_key("rewardIndex") else 0
		def __init__(self, pageIdx, rewardIndex, rewardData):
			ui.ImageBox.__init__(self)
			self.LoadReward(pageIdx, rewardIndex, rewardData)
		def LoadReward(self, pageIdx, rewardIndex, rewardData):
			self.LoadImage(IMG_DIR+"item_1.png")
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
				rewardDoneSolo = CreateWindow(ui.ImageBox(), self, (366, 0), IMG_ICON_DIR+"done.png")
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

			if app.IsPressed(app.DIK_LSHIFT) and interface.OpenRenderTargetWindow(0, itemVnum):
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler:
					interfaceHandler.OpenRenderTargetWindow(0, itemVnum)

	def Destroy(self):
		self.__children = {}

	def __init__(self):
		ui.Window.__init__(self)
		self.__LoadWindow()

	def __LoadWindow(self):
		self.Destroy()

		self.AddFlag("movable")
		self.AddFlag("attach")
		self.AddFlag("float")
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		board = CreateWindow(ui.BoardWithTitleBar(), self, (0, 0), "", "", (484, 385))
		board.AddFlag("attach")
		board.SetCloseEvent(self.Close)
		self.__children["board"] = board

		boardImage = CreateWindow(ui.ImageBox(), board, (8, 30), IMG_DIR+"board.tga")
		self.__children["boardImage"] = boardImage

		scrollBar = CreateWindow(ScrollBarSpecial(False), boardImage, (459, 1), "", "", (9, SCROLLBAR_HEIGHT))
		scrollBar.SetScale(SCROLLBAR_HEIGHT/2, SCROLLBAR_HEIGHT)
		self.__children["scrollBar"] = scrollBar

		listBox = CreateWindow(ui.ListBoxEx(), boardImage, (4+10, 4), "", "", (boardImage.GetWidth(), boardImage.GetHeight()))
		listBox.SetViewItemCount(4)
		listBox.OnMouseWheel = ui.__mem_func__(self.OnMouseWheel)
		listBox.SetItemSize(450, 81)
		listBox.SetItemStep(83)
		listBox.SetScrollBar(scrollBar)
		self.__children["listBox"] = listBox

		pageBtnImg = CreateWindow(ui.ImageBox(), self, (3, 30 + boardImage.GetHeight() + 5), IMG_DIR+"page_0.tga")
		self.__children["pageBtnImg"] = pageBtnImg

		pageBtn = CreateWindow(ui.ImageBox(), pageBtnImg, (0, 0), IMG_DIR+"btn.tga")
		self.__children["pageBtn"] = pageBtn

		self.SetSize(484, 420)
		self.SetCenterPosition()

		for key, data in global_reward_info.items():
			if data["type"] == player.REWARD_MISSION_ZODIAC_DUNGEON and data["subValue"] == 1:
				continue
			data["player_names"] = ["", "", ""]

		for key, data in solo_reward_info.items():
			data["value"] = 0

		self.__SetPage("", 0)

	def __SetPage(self, emptyArg, pageIdx):
		self.__children["pageIdx"] = pageIdx

		self.__children["pageBtn"].SetPosition(14 if pageIdx else 75, 8)
		self.__children["pageBtn"].SetEvent(ui.__mem_func__(self.__SetPage), "mouse_click", 0 if pageIdx else 1)
		self.__children["pageBtnImg"].LoadImage("{}page_{}.tga".format(IMG_DIR, pageIdx))

		listBox = self.__children["listBox"] if self.__children.has_key("listBox") else None
		scrollBar = self.__children["scrollBar"] if self.__children.has_key("scrollBar") else None
		listBox.RemoveAllItems()

		scrollBar.SetPos(0)

		totalY = 0
		if pageIdx == 0:
			#global
			for key, data in global_reward_info.items():
				if data["type"] == player.REWARD_MISSION_ZODIAC_DUNGEON and data["subValue"] == 1:
					continue
				listBox.AppendItem(self.RewardItemGlobal(pageIdx, key, data))
				totalY += 83
		elif pageIdx == 1:
			for key, data in solo_reward_info.items():
				listBox.AppendItem(self.RewardItemSolo(pageIdx, key, data))
				totalY += 83

		self.__children["board"].SetTitleName([localeinfo.REWARD_SYSTEM_GLOBAL, localeinfo.REWARD_SYSTEM_SOLO][pageIdx])
		scrollBar.SetScale(SCROLLBAR_HEIGHT, totalY if totalY > SCROLLBAR_HEIGHT else SCROLLBAR_HEIGHT)

	def RewardData(self, isGlobal, isNeedClean, commandText):
		pageIdx = self.__children["pageIdx"]
		if isGlobal:
			if isNeedClean:
				for key, data in global_reward_info.items():
					if data["type"] == player.REWARD_MISSION_ZODIAC_DUNGEON and data["subValue"] == 1:
						continue
					data["player_names"] = ["", "", ""]

			if commandText != "empty":
				dataList = commandText.split("#")
				for data in dataList:
					dataSplit = data.split("?")
					if len(dataSplit) == 2:
						idx = int(dataSplit[0])
						if global_reward_info.has_key(idx):
							if global_reward_info[idx]["type"] == player.REWARD_MISSION_ZODIAC_DUNGEON and global_reward_info[idx]["subValue"] == 1:
								continue
							# Parse "name1|name2|name3" format
							names = dataSplit[1].split("|")
							playerNames = ["", "", ""]
							for i in range(min(3, len(names))):
								playerNames[i] = names[i]
							global_reward_info[idx]["player_names"] = playerNames

						if pageIdx == 0:
							listBox = self.__children["listBox"] if self.__children.has_key("listBox") else None
							for child in listBox.itemList:
								if child.GetRewardIndex() == idx:
									child.SetRewardPlayers(playerNames)
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
		self.SetTop()
		self.Show()
	def Close(self):
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
