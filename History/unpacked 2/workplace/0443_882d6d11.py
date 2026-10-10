# coding: latin_1

import app
import chr
import net
import player

import ui
from _weakref import proxy
import item
import wndMgr
import constinfo
import localeinfo
import uiscriptlocale
import uiToolTip
import nonplayer
import chat
import time
import grp
import event
import snd

TAB_COUNT = 3	# Min = 3 / Max = 6

IMG_PATH = "d:/ymir work/ui/public/teleportpanel/"
MAP_IMG_PATH = "d:/ymir work/ui/public/teleportpanel/map_img/"
SLIDER_IMG_PATH = "d:/ymir work/ui/public/teleportpanel/slider/"

SLIDER_TIME_TO_REFRESH = 10			# in seconds
SLIDER_ANI_DURATION = 3 				# in seconds
SLIDER_DICT = {
	0 : SLIDER_IMG_PATH + "picture_1.tga",
	1 : SLIDER_IMG_PATH + "picture_2.tga",
	2 : SLIDER_IMG_PATH + "picture_3.tga",
}

# Note: Always write the map pictures in the MAP_DICT without the additions "_normal.tga", "_hover.tga" and "_down.tga" !!!!

MAP_DICT = {
	##############################################################################################################################################################################
	"TAB_1" :
	{
		0 : {
			"map_img" : "3in1_kingdom", "desc_text" : uiscriptlocale.TELEPORT_MAP_MAP_1, "map_desc" : uiscriptlocale.TELEPORT_MAP_MAP_1_DESC, 
			"boss_vnum" : 0, "min_lv" : 1, "max_lv" : 120, "money_cost" : 0, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "m1_red" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_RED_EMPIRE, "button_text_color" : 0xFFFF2828, "button_disable_text_color" : 0xFFB21B1B },
				1 : {"command" : "m1_yel" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_YELLOW_EMPIRE, "button_text_color" : 0xFFFFD903, "button_disable_text_color" : 0xFFBB9F00 },
				2 : {"command" : "m1_blu" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_BLUE_EMPIRE, "button_text_color" : 0xFF007BFF, "button_disable_text_color" : 0xFF0050A6 },
			},
		},
		1 : {
			"map_img" : "3in1", "desc_text" : uiscriptlocale.TELEPORT_MAP_MAP_2, "map_desc" : uiscriptlocale.TELEPORT_MAP_MAP_2_DESC,  
			"boss_vnum" : 0, "min_lv" : 1, "max_lv" : 120, "money_cost" : 0, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "village_shop" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_START, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
		2 : {
			"map_img" : "pvp_map", "desc_text" : uiscriptlocale.TELEPORT_MAP_YONGBI, "map_desc" : uiscriptlocale.TELEPORT_MAP_YONGBI_DESC,  
			"boss_vnum" : 0, "min_lv" : 55, "max_lv" : 120, "money_cost" : 0, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "yongbi_middle" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_MIDDLE, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
		3 : {
			"map_img" : "pvp_char_1", "desc_text" : uiscriptlocale.TELEPORT_MAP_YONGBI_1, "map_desc" : uiscriptlocale.TELEPORT_MAP_YONGBI_DESC,  
			"boss_vnum" : 0, "min_lv" : 55, "max_lv" : 120, "money_cost" : 0, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "pvp_warrior" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_WARRIOR, "button_text_color" : 0, "button_disable_text_color" : 0 },
				1 : {"command" : "pvp_ninja" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_NINJA, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
		4 : {
			"map_img" : "pvp_char_2", "desc_text" : uiscriptlocale.TELEPORT_MAP_YONGBI_1, "map_desc" : uiscriptlocale.TELEPORT_MAP_YONGBI_DESC,  
			"boss_vnum" : 0, "min_lv" : 55, "max_lv" : 120, "money_cost" : 0, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "pvp_sura" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_SURA, "button_text_color" : 0, "button_disable_text_color" : 0 },
				1 : {"command" : "pvp_shaman" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_SHAMAN, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
	},
	##############################################################################################################################################################################
	"TAB_2" : 
	{
		0 : {
			"map_img" : "dungeon_spiderdungeon02", "desc_text" : uiscriptlocale.TELEPORT_MAP_SPIDERDUNGEON_02, "map_desc" : "",  
			"boss_vnum" : 0, "min_lv" : 55, "max_lv" : 120, "money_cost" : 0, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "sd2_start" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_START, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
		1 : {#stones map
			"map_img" : "metin2_map", "desc_text" : uiscriptlocale.TELEPORT_MAP_STONESMAP, "map_desc" : uiscriptlocale.TELEPORT_MAP_STONES_DESC,   
			"boss_vnum" : 0, "min_lv" : 55, "max_lv" : 120, "money_cost" : 0, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "pvm_middle_1" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_STONES_1, "button_text_color" : 0, "button_disable_text_color" : 0 },
				1 : {"command" : "pvm_middle_2" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_STONES_2, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
		2 : {#stones map
			"map_img" : "metin2_map", "desc_text" : uiscriptlocale.TELEPORT_MAP_STONESMAP_1, "map_desc" : uiscriptlocale.TELEPORT_MAP_STONES_DESC,   
			"boss_vnum" : 0, "min_lv" : 55, "max_lv" : 120, "money_cost" : 0, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "pvm_hard_1" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_STONES_3, "button_text_color" : 0, "button_disable_text_color" : 0 },
				1 : {"command" : "pvm_hard_2" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_STONES_4, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
		3 : {
			"map_img" : "dungeon_skipia", "desc_text" : uiscriptlocale.TELEPORT_MAP_SKIPIA_DUNGEON, "map_desc" : "",  
			"boss_vnum" : 0, "min_lv" : 75, "max_lv" : 120, "money_cost" : 0, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "skipia2" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_SKIPIA_2, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
	},
	##############################################################################################################################################################################
	"TAB_3" : 
	{
		0 : {#enchanted forest
			"map_img" : "enhcanted_forest", "desc_text" : uiscriptlocale.TELEPORT_MAP_ENCHANTEDFOREST, "map_desc" : "",   
			"boss_vnum" : 0, "min_lv" : 95, "max_lv" : 120, "money_cost" : 100000, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "ecnhantedforest_start" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_START, "button_text_color" : 0, "button_disable_text_color" : 0 },
				1 : {"command" : "ecnhantedforest_middle" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_MIDDLE, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
		1 : {#TELEPORT_MAP_ELEMENT_ELEC TELEPORT_MAP_ELEMENT_ELEC TELEPORT_MAP_ELEMENT_ELEC
			"map_img" : "elements", "desc_text" : uiscriptlocale.TELEPORT_MAP_ELEMENT_ELEC, "map_desc" : "",   
			"boss_vnum" : 0, "min_lv" : 95, "max_lv" : 120, "money_cost" : 0, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "elelemt_elec_start" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_START, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
		2 : {#TELEPORT_MAP_SNAKES_NEW
			"map_img" : "snakes", "desc_text" : uiscriptlocale.TELEPORT_MAP_SNAKES_NEW, "map_desc" : "",  
			"boss_vnum" : 0, "min_lv" : 100, "max_lv" : 120, "money_cost" : 1000000, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "snakes_new_start" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_START, "button_text_color" : 0, "button_disable_text_color" : 0 },
				#1 : {"command" : "elelemt_dark_top" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_END, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
		3 : {#TELEPORT_MAP_ALESTOR
			"map_img" : "alastor", "desc_text" : uiscriptlocale.TELEPORT_MAP_ALESTOR, "map_desc" : "",  
			"boss_vnum" : 0, "min_lv" : 105, "max_lv" : 120, "money_cost" : 1000000, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "alestor_start" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_START, "button_text_color" : 0, "button_disable_text_color" : 0 },
				#1 : {"command" : "snow_new_middle" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_MIDDLE, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
		4 : {#TELEPORT_MAP_ALESTOR
			"map_img" : "ghosts", "desc_text" : uiscriptlocale.TELEPORT_MAP_GHOSTS, "map_desc" : "",  
			"boss_vnum" : 0, "min_lv" : 105, "max_lv" : 120, "money_cost" : 1000000, "item_cost" : 0, "item_cost_count" : 0,
			"BUTTONS" : { # Max Buttons = 3
				0 : {"command" : "ghosts_start" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_START, "button_text_color" : 0, "button_disable_text_color" : 0 },
				#1 : {"command" : "snow_new_middle" , "button_text" : uiscriptlocale.TELEPORT_BUTTON_MIDDLE, "button_text_color" : 0, "button_disable_text_color" : 0 },
			}
		},
	},
	##############################################################################################################################################################################
	"TAB_4" : {
	},
	##############################################################################################################################################################################
	"TAB_5" : {
	},
	##############################################################################################################################################################################
	"TAB_6" : {
	},
}


class TeleportPanel(ui.ScriptWindow):
	def __init__(self):
		self.__questReciveString = ""
		self.__questSendString = ""
		self.__questID = 0
		self.pageindex = 0
		self.IconItemVnum = 0
		self.__commands = { 'SET_QUEST_ID' : self.__SetQuestId, 'GET_QUEST_CMD' : self.__GetQuestCmd }
		
		self.MapAreaLists = []
		self.ScrollBarPositions = {}
		self.ScrollBarAniStart = 0
		self.ScrollBarAniStartTime = 0
		self.ScrollBarNextPos = 0.0
		self.ScrollBarStep = 0.25

		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__LoadWindow()
		
	def __del__(self):
		self.MapAreaLists = []
		
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.seclectedMapOnState = ""
		self.selectedMap = 0
		self.sliderNextPictureTime = app.GetTime() + SLIDER_TIME_TO_REFRESH
		self.showStartIndex = 0
		self.startTimeSlidePicture = 0
		self.activePicture = 0
		self.IconItemVnum = 0
		self.sliderImgRotation = 1
		ui.ScriptWindow.Show(self)

	def Close(self):
		self.Hide()
		
	def Destroy(self):
		ui.ScriptWindow.__del__(self)

	def __LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/teleportpanel.py")
		except:
			import exception
			exception.Abort("uiTeleportPanel.Open.TeleportPanel.py")
	
		try:
			self.tooltipItem = uiToolTip.ItemToolTip()
			self.GetChild("board").SetCloseEvent(self.Close)
			
			self.tabNameDict = {}
			self.tabDict = {}
			self.tabButtonDict = {}
			
			self.tabNameDict[0] = "TAB_1"
			self.tabNameDict[1] = "TAB_2"
			self.tabNameDict[2] = "TAB_3"
			self.tabDict["TAB_1"] = self.GetChild("Tab_01")
			self.tabDict["TAB_2"] = self.GetChild("Tab_02")
			self.tabDict["TAB_3"] = self.GetChild("Tab_03")
			self.tabButtonDict["TAB_1"] = self.GetChild("Tab_Button_01")
			self.tabButtonDict["TAB_2"] = self.GetChild("Tab_Button_02")
			self.tabButtonDict["TAB_3"] = self.GetChild("Tab_Button_03")

			if TAB_COUNT > 3:
				self.tabNameDict[3] = "TAB_4"
				self.tabDict["TAB_4"] = self.GetChild("Tab_04")
				self.tabButtonDict["TAB_4"] = self.GetChild("Tab_Button_04")
			if TAB_COUNT > 4:
				self.tabNameDict[4] = "TAB_5"
				self.tabDict["TAB_5"] = self.GetChild("Tab_05")
				self.tabButtonDict["TAB_5"] = self.GetChild("Tab_Button_05")
			if TAB_COUNT > 5:
				self.tabNameDict[5] = "TAB_6"
				self.tabDict["TAB_6"] = self.GetChild("Tab_06")
				self.tabButtonDict["TAB_6"] = self.GetChild("Tab_Button_06")

			for (stateKey, tabButton) in self.tabButtonDict.items():
				tabButton.SetEvent(ui.__mem_func__(self.__OnClickTabButton), stateKey)

			self.scrollBar = MapScrollBar()
			self.scrollBar.SetParent(self.GetChild("ScrollBarPlace"))
			self.scrollBar.SetScrollEvent(ui.__mem_func__(self.OnScroll))
			self.scrollBar.SetTexture(IMG_PATH + "scrollbar.sub")
			self.scrollBar.SetMovementArea(0, 0, 5, 403)
			self.scrollBar.SetPosition(0, 0)
			self.scrollBar.Show()
			
			self.GetChild("item_icon").SetEvent(ui.__mem_func__(self.OverInItem), "mouse_over_in")
			self.GetChild("item_icon").SetEvent(ui.__mem_func__(self.OverOutItem), "mouse_over_out")
			
			self.CreateMapLists()
			self.SetState("TAB_1")
			self.GetChild("info_layer").Hide()

		except:
			import exception
			exception.Abort("uiTeleportPanel.LoadWindow.BindObject")
	

	def __OnClickTabButton(self, stateKey):
		self.SetState(stateKey)

	def SetState(self, stateKey):
		ACTIVE_COLOR	= 0xFFFEE3AE
		DISABLE_COLOR	= 0xFF9C8C6D
		
		self.state = stateKey

		for (tabKey, tabButton) in self.tabButtonDict.items():
			if stateKey!=tabKey:
				tabButton.SetTextColor(DISABLE_COLOR)
				tabButton.SetUp()
			else:
				tabButton.SetTextColor(ACTIVE_COLOR)

		for tabValue in self.tabDict.itervalues():
			tabValue.Hide()
			
		self.tabDict[stateKey].Show()
		
		self.ScrollBarPositions[self.pageindex] = self.scrollBar.GetPos()
		
		for tabidx in self.tabNameDict:
			if self.tabNameDict[tabidx] == stateKey:
				self.pageindex = tabidx
				self.MapAreaLists[tabidx].Show()
				if self.MapAreaLists[tabidx].GetMapCount() > 4:
					self.scrollBar.Show()
					self.GetChild("ActiveScrollBar").Show()
					if self.ScrollBarPositions.has_key(self.pageindex):
						self.scrollBar.SetPos(self.ScrollBarPositions[self.pageindex])
					else:
						self.scrollBar.SetPos(0)
				else:
					self.scrollBar.Hide()
					self.GetChild("ActiveScrollBar").Hide()
			else:
				self.MapAreaLists[tabidx].Hide()
	
	def CreateMapLists(self):
		self.MapAreaLists = []
		for tabidx in xrange(TAB_COUNT):
			MapList = ListBoxMap()
			MapList.SetParent(self.GetChild("MapList"))
			MapList.SetGlobalParent(self)
			MapList.SetSize(424, 407)
			MapList.SetPosition(0, 0)
			#MapList.Show()
			
			self.MapAreaLists.append(MapList)
			
			tab_name = self.tabNameDict[tabidx]
			
			for mapidx in xrange(len(MAP_DICT[tab_name])):
				map_name = MAP_DICT[tab_name][mapidx]["desc_text"]
				default_img = MAP_IMG_PATH + MAP_DICT[tab_name][mapidx]["map_img"] + "_normal.tga"
				hover_img = MAP_IMG_PATH + MAP_DICT[tab_name][mapidx]["map_img"] + "_hover.tga"
				down_img = MAP_IMG_PATH + MAP_DICT[tab_name][mapidx]["map_img"] + "_down.tga"
				self.MapAreaLists[tabidx].AppendMap(mapidx, map_name, default_img, hover_img, down_img, 5)

	def SetMapInfo(self, mapindex):
		
		selDictInfo = MAP_DICT[self.state][mapindex]
		
		for i in xrange(len(self.MapAreaLists)):
			if self.tabNameDict.has_key(i) and self.tabNameDict[i] != self.state: 
				self.MapAreaLists[i].DelSelectAll()
		
		self.SetMapDesc(selDictInfo["map_desc"])
		
		self.GetChild("info_layer").Show()
		self.GetChild("Titlebar2_Text").SetText(selDictInfo["desc_text"])
		if selDictInfo["boss_vnum"] != 0:
			self.GetChild("text_info_boss").SetText(uiscriptlocale.TELEPORT_PANEL_INFO_BOSS % nonplayer.GetMonsterName(selDictInfo["boss_vnum"]))
		else:
			self.GetChild("text_info_boss").SetText(uiscriptlocale.TELEPORT_PANEL_INFO_BOSS_EMPTY)
		if selDictInfo["min_lv"] != 0:
			if player.GetStatus(player.LEVEL) > selDictInfo["min_lv"]:
				self.GetChild("text_info_minlv").SetText((uiscriptlocale.TELEPORT_PANEL_INFO_MINLV + "|cff5af053 %d") % selDictInfo["min_lv"])
			else:
				self.GetChild("text_info_minlv").SetText((uiscriptlocale.TELEPORT_PANEL_INFO_MINLV + "|cffd74949 %d") % selDictInfo["min_lv"])
		else:
			self.GetChild("text_info_minlv").SetText(uiscriptlocale.TELEPORT_PANEL_INFO_MINLV_EMPTY)
		if selDictInfo["max_lv"] != 0:
			if player.GetStatus(player.LEVEL) < selDictInfo["max_lv"]:
				self.GetChild("text_info_maxlv").SetText((uiscriptlocale.TELEPORT_PANEL_INFO_MAXLV + "|cff5af053 %d") % selDictInfo["max_lv"])
			else:
				self.GetChild("text_info_maxlv").SetText((uiscriptlocale.TELEPORT_PANEL_INFO_MAXLV + "|cffd74949 %d") % selDictInfo["max_lv"])
		else:
			self.GetChild("text_info_maxlv").SetText(uiscriptlocale.TELEPORT_PANEL_INFO_MAXLV_EMPTY)
		if selDictInfo["money_cost"] != 0:
			if player.GetMoney() >= selDictInfo["money_cost"]:
				self.GetChild("text_info_cost").SetText((uiscriptlocale.TELEPORT_PANEL_INFO_COST + "|cff5af053 %s") % localeinfo.NumberToMoneyString(int(selDictInfo["money_cost"])))
			else:
				self.GetChild("text_info_cost").SetText((uiscriptlocale.TELEPORT_PANEL_INFO_COST + "|cffd74949 %s") % localeinfo.NumberToMoneyString(int(selDictInfo["money_cost"])))
		else:
			self.GetChild("text_info_cost").SetText(uiscriptlocale.TELEPORT_PANEL_INFO_COST_EMPTY)
		if selDictInfo["item_cost"] != 0:
			item.SelectItem(selDictInfo["item_cost"])
			if player.GetItemCountByVnum(selDictInfo["item_cost"]) >= selDictInfo["item_cost_count"]:
				self.GetChild("text_info_required_item_text").SetText((uiscriptlocale.TELEPORT_PANEL_INFO_ITEM_COST_TEXT + " |cff5af053 ["+str(player.GetItemCountByVnum(selDictInfo["item_cost"]))+"]") % (selDictInfo["item_cost_count"], item.GetItemName()))
			else:
				self.GetChild("text_info_required_item_text").SetText((uiscriptlocale.TELEPORT_PANEL_INFO_ITEM_COST_TEXT + " |cffd74949 ["+str(player.GetItemCountByVnum(selDictInfo["item_cost"]))+"]") % (selDictInfo["item_cost_count"], item.GetItemName()))
			self.GetChild("item_icon").LoadImage(item.GetIconImageFileName())
			self.GetChild("item_icon").Show()
			self.IconItemVnum = selDictInfo["item_cost"]
		else:
			self.GetChild("text_info_required_item_text").SetText(uiscriptlocale.TELEPORT_PANEL_INFO_ITEM_COST_TEXT_EMPTY)
			self.GetChild("item_icon").Hide()
			self.IconItemVnum = 0
	
		self.selectButtonList = []
		self.buttonYRange = 338
		for button in xrange(len(selDictInfo["BUTTONS"])):
			self.SelectButton = ui.Button()
			self.SelectButton.SetParent(self.GetChild("InfoArea"))
			#self.SelectButton.SetWindowHorizontalAlignCenter()
			self.SelectButton.SetPosition(13, self.buttonYRange)
			self.SelectButton.SetUpVisual(IMG_PATH + "button_default.sub")
			self.SelectButton.SetOverVisual(IMG_PATH + "button_hover.sub")
			self.SelectButton.SetDownVisual(IMG_PATH + "button_down.sub")
			self.SelectButton.SetDisableVisual(IMG_PATH + "button_disable.sub")
			self.SelectButton.SetText(selDictInfo["BUTTONS"][button]["button_text"])
			if selDictInfo["BUTTONS"][button]["button_text_color"] != 0:
				self.SelectButton.SetTextColor(selDictInfo["BUTTONS"][button]["button_text_color"])
			else:
				self.SelectButton.SetTextColor(0xFFFEE3AE)
			self.SelectButton.SetOutline()
			if player.GetStatus(player.LEVEL) < selDictInfo["min_lv"] or player.GetStatus(player.LEVEL) > selDictInfo["max_lv"] or player.GetMoney() < selDictInfo["money_cost"] or player.GetItemCountByVnum(selDictInfo["item_cost"]) < selDictInfo["item_cost_count"]:
				self.SelectButton.Disable()
				if selDictInfo["BUTTONS"][button]["button_disable_text_color"] != 0:
					self.SelectButton.SetTextColor(selDictInfo["BUTTONS"][button]["button_disable_text_color"])
				else:
					self.SelectButton.SetTextColor(0xFFB29A6B)
			
			self.SelectButton.SetEvent(ui.__mem_func__(self.ClickButton), selDictInfo["BUTTONS"][button]["command"])
			self.SelectButton.Show()
			self.selectButtonList.append(self.SelectButton)
			self.buttonYRange += 37
	
	def ClickButton(self, command):
		self.SendQuestCommand('TELEPORTING#%s' % (str(command)))
		self.Close()
			
	def OnScroll(self):
		self.MapAreaLists[self.pageindex].OnScroll(self.scrollBar.GetPos())
		
	def SetMapDesc(self, desc):
		self.childrenList = []
		lines = self.SplitDescription(desc, 35)
		if not lines:
			return
			
		self.toolTipHeight = 7
		for line in lines:
			textLine = ui.TextLine()
			textLine.SetParent(self.GetChild("info_layer"))
			textLine.SetPackedFontColor(0xFFFFFFFF)
			#textLine.SetFontName(localeinfo.UI_DEF_FONT_SLARGE)
			textLine.SetText(line)
			textLine.SetOutline()
			#textLine.SetFeather(False)
			textLine.Show()

			textLine.SetPosition(0, self.toolTipHeight)
			textLine.SetWindowHorizontalAlignCenter()
			textLine.SetHorizontalAlignCenter()

			self.childrenList.append(textLine)

			self.toolTipHeight += 17

	def OnRunMouseWheel(self, nLen):
		if self.scrollBar.IsShow():
			self.ScrollBarAniStart = 1
			if self.ScrollBarAniStartTime < time.clock():
				self.ScrollBarAniStartTime = time.clock()
			if nLen > 0:
				pos = self.scrollBar.GetPos() - self.ScrollBarStep
			else:
				pos = self.scrollBar.GetPos() + self.ScrollBarStep
			pos = max(0.0, pos)
			pos = min(1.0, pos)

			self.ScrollBarStartPos = self.scrollBar.GetPos()
			self.ScrollBarNextPos = pos
	
	def OverInItem(self):
		if None != self.tooltipItem and self.IconItemVnum != 0:
			self.tooltipItem.SetItemToolTip(self.IconItemVnum)
			
	def OverOutItem(self):
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OnUpdate(self):
		if self.ScrollBarAniStart != 0:
			if self.ScrollBarNextPos != self.scrollBar.GetPos():
				progress = float(min((time.clock() - self.ScrollBarAniStartTime) / 0.30, 1))
				if progress < 1:
					position = (progress * (self.ScrollBarNextPos - self.scrollBar.GetPos()) + self.scrollBar.GetPos())
					self.scrollBar.SetPos(position)
				else:
					self.ScrollBarAniStart = 0
					self.ScrollBarNextPos = 0.0
			else:
				self.ScrollBarAniStart = 0
				self.ScrollBarNextPos = 0.0
					
		if self.sliderNextPictureTime < app.GetTime():
			self.sliderNextPictureTime = app.GetTime() + SLIDER_TIME_TO_REFRESH
			self.startTimeSlidePicture = time.clock()
			self.sliderImgRotation += 1
			if self.sliderImgRotation >= len(SLIDER_DICT):
				self.sliderImgRotation = 0
			if self.activePicture == 0:
				self.GetChild("slider_picture_1").LoadImage(SLIDER_DICT[self.sliderImgRotation])
			elif self.activePicture == 1:
				self.GetChild("slider_picture_2").LoadImage(SLIDER_DICT[self.sliderImgRotation])
	
		if self.startTimeSlidePicture != 0:
			progress = float(min((time.clock() - self.startTimeSlidePicture) / SLIDER_ANI_DURATION, 1))
			if progress < 1:
				alphaValueOff = float(1.0 - progress)
				alphaValueOn = float(0.0 + progress)
				
				if self.activePicture == 0:
					self.GetChild("slider_picture_2").SetAlpha(alphaValueOff)
					self.GetChild("slider_picture_1").SetAlpha(alphaValueOn)
				if self.activePicture == 1:
					self.GetChild("slider_picture_1").SetAlpha(alphaValueOff)
					self.GetChild("slider_picture_2").SetAlpha(alphaValueOn)
			else:
				self.startTimeSlidePicture = 0
				if self.activePicture == 0:
					self.activePicture = 1
				elif self.activePicture == 1:
					self.activePicture = 0

	def SplitDescription(self, desc, limit):
		total_tokens = desc.split()
		line_tokens = []
		line_len = 0
		lines = []
		for token in total_tokens:
			if "|" in token:
				sep_pos = token.find("|")
				line_tokens.append(token[:sep_pos])

				lines.append(" ".join(line_tokens))
				line_len = len(token) - (sep_pos + 1)
				line_tokens = [token[sep_pos+1:]]
			else:
				line_len += len(token)
				if len(line_tokens) + line_len > limit:
					lines.append(" ".join(line_tokens))
					line_len = len(token)
					line_tokens = [token]
				else:
					line_tokens.append(token)

		if line_tokens:
			lines.append(" ".join(line_tokens))

		return lines

	def SendQuestCommand(self, send_command):
		self.__questSendString = send_command
		event.QuestButtonClick(self.__questID)
	
	def ReceiveQuestCommand(self, recive_command):
		self.__questReciveString += recive_command
		close_pos = self.__questReciveString.find(')')
		if close_pos != -1:
			open_pos = self.__questReciveString.find('(')
			
			command = self.__questReciveString[:open_pos]
			args = self.__questReciveString[open_pos+1:close_pos].replace("#","").split(",")
			self.__questReciveString = ''
			if command in self.__commands:
				if args[0]:
					self.__commands[command](*args)
				else:
					self.__commands[command]()
			
	def __SetQuestId(self, quest_id):
		self.__questID = int(quest_id)
		
	def __GetQuestCmd(self):
		net.SendQuestInputStringPacket(self.__questSendString)
		self.__questSendString = ""

class ListBoxMap(ui.Window):
	class Item(ui.Window):
		def __init__(self, parent, map_index, mapname, image_default, image_over, image_down):
			ui.Window.__init__(self)
			
			ui.Window.SetParent(self, parent)
			self.parent = proxy(parent)
			
			self.SetWindowName("ListBoxMap_Item")
			self.bIsSelected = False
			self.xBase, self.yBase = 0, 0
			
			self.MapIndex = map_index
			self.MapName = mapname
			self.ImageDefault = image_default
			self.ImageOver = image_over
			self.ImageDown = image_down
			
			self.MapImage = ui.MakeExpandedImageBox(self, self.ImageDefault, 0, 0, "not_pick")
			
			self.MapNameText = ui.TextLine()
			self.MapNameText.SetParent(self.MapImage)
			#self.MapNameText.SetFontName(localeinfo.UI_DEF_FONT_LARGE)
			self.MapNameText.SetPosition(0, 75)
			self.MapNameText.SetHorizontalAlignCenter()
			self.MapNameText.SetWindowHorizontalAlignCenter()
			self.MapNameText.SetText(self.MapName)
			self.MapNameText.Show()

		def __del__(self):
			ui.Window.__del__(self)
			self.bIsSelected = False
			self.xBase, self.yBase = 0, 0
			self.MapIndex = 0
			self.MapName = ""
			self.ImageDefault = ""
			self.ImageOver = ""
			self.ImageDown = ""
			self.MapImage = None
			self.MapName = None

		def SetBasePosition(self, x, y):
			self.xBase = x
			self.yBase = y

		def GetBasePosition(self):
			return (self.xBase, self.yBase)

		def OnMouseOverIn(self):
			self.MapImage.LoadImage(self.ImageOver)
		
		def OnMouseOverOut(self):
			if self.bIsSelected == True:
				self.MapImage.LoadImage(self.ImageDown)
			else:
				self.MapImage.LoadImage(self.ImageDefault)

		def OnMouseLeftButtonUp(self):
			snd.PlaySound("sound/ui/click.wav")
			self.Select()
			
		def Select(self):
			self.bIsSelected = True
			self.parent.SetSelectMap(self.MapIndex)
			self.MapImage.LoadImage(self.ImageDown)

		def Deselect(self):
			self.bIsSelected = False
			self.MapImage.LoadImage(self.ImageDefault)

		def GetMapIndex(self):
			return self.MapIndex

		def Show(self):
			ui.Window.Show(self)
		
		def OnRender(self):
			xList, yList = self.parent.GetGlobalPosition()

			if self.MapImage:
				self.MapImage.SetClipRect(xList, yList, xList + self.parent.GetWidth(), yList + self.parent.GetHeight())

			if self.MapNameText:
				xText, yText = self.MapNameText.GetGlobalPosition()
				wText, hText = self.MapNameText.GetTextSize()

				if yText < yList or (yText + hText > yList + self.parent.GetHeight()):
					self.MapNameText.Hide()
				else:
					self.MapNameText.Show()

	def __init__(self):
		ui.Window.__init__(self)
		self.SetWindowName("ListBoxMap")
		self.globalParent = None
		self.maplist = []

	def __del__(self):
		ui.Window.__del__(self)
		self.globalParent = None
		self.maplist = []

	def SetSelectMap(self, mapindex):
		if len(self.maplist) != 0:
			for i in xrange(len(self.maplist)):
				if mapindex != self.maplist[i].GetMapIndex():
					self.maplist[i].Deselect()

			if self.globalParent:
				self.globalParent.SetMapInfo(mapindex)

	def GetSelectedMap(self):
		return self.selectedMap

	def DelSelectAll(self):
		if len(self.maplist) != 0:
			for i in xrange(len(self.maplist)):
				self.maplist[i].Deselect()

	def GetMapCount(self):
		count = 0
		for i in xrange(len(self.maplist)):
			count += 1
		return count

	def SetGlobalParent(self, parent):
		self.globalParent = proxy(parent)

	def OnScroll(self, scrollPos):
		totalHeight = 0
		for item in self.maplist:
			totalHeight += item.GetHeight() 

		totalHeight -= self.GetHeight()

		for i in xrange(len(self.maplist)):
			x, y = self.maplist[i].GetLocalPosition()
			xB, yB = self.maplist[i].GetBasePosition()
			setPos = yB - int(scrollPos * totalHeight)
			self.maplist[i].SetPosition(xB, setPos)

	def AppendMap(self, map_index, mapname, image_default, image_over, image_down, space_y):
		item = self.Item(self, map_index, mapname, image_default, image_over, image_down)
		item.SetSize(424, 98 + space_y)

		if len(self.maplist) == 0:
			item.SetPosition(0, 0)
			item.SetBasePosition(0, 0)
		else:
			x, y = self.maplist[-1].GetLocalPosition()
			item.SetPosition(0, y + self.maplist[-1].GetHeight())
			item.SetBasePosition(0, y + self.maplist[-1].GetHeight())
		
		item.Show()
		self.maplist.append(item)

class MapScrollBar(ui.DragButton):
	def __init__(self):
		ui.DragButton.__init__(self)
		self.AddFlag("float")
		self.AddFlag("movable")
		self.AddFlag("restrict_x")

		self.eventScroll = lambda *arg: None
		self.movearea = 0
		self.currentPos = 0.0

	def __del__(self):
		ui.DragButton.__del__(self)
		self.movearea = 0
		self.currentPos = 0.0
		self.eventScroll = lambda *arg: None

	def SetMovementArea(self, x, y, width, height):
		self.movearea = height - y - self.GetHeight()
		self.SetRestrictMovementArea(x, y, width, height)
	
	def SetTexture(self, image):
		self.SetUpVisual(image)
		self.SetOverVisual(image)
		self.SetDownVisual(image)

	def SetScrollEvent(self, event):
		self.eventScroll = event

	def SetPos(self, pos):
		pos = max(0.0, pos)
		pos = min(1.0, pos)

		yPos = float(pos * self.movearea)

		self.SetPosition(12, yPos)
		self.OnMove()

	def GetPos(self):
		return self.currentPos
		
	def OnMove(self):
		(xLocal, yLocal) = self.GetLocalPosition()
		self.currentPos = float(yLocal) / float(self.movearea) 

		self.eventScroll()