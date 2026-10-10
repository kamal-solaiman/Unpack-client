# coding: latin_1

import ui
import localeinfo
import player
import app
import item
import uitooltip
import chat
import wndMgr

obj_expend_img_path={
	0:{ "iconFilePath0":"d:/ymir work/ui/quest_re/tabcolor_1_main.tga",			"iconFilePath1":"d:/ymir work/ui/game/characterdetails/plus.dds",	"iconFilePath2":"d:/ymir work/ui/game/characterdetails/minus.dds",},
	1:{ "iconFilePath0":"d:/ymir work/ui/quest_re/tabcolor_2_sub.tga",			"iconFilePath1":"d:/ymir work/ui/game/characterdetails/plus.dds",	"iconFilePath2":"d:/ymir work/ui/game/characterdetails/minus.dds",},
	2:{ "iconFilePath0":"d:/ymir work/ui/quest_re/tabcolor_3_levelup.tga",		"iconFilePath1":"d:/ymir work/ui/game/characterdetails/plus.dds",	"iconFilePath2":"d:/ymir work/ui/game/characterdetails/minus.dds",},
	3:{ "iconFilePath0":"d:/ymir work/ui/quest_re/tabcolor_4_event.tga",		"iconFilePath1":"d:/ymir work/ui/game/characterdetails/plus.dds",	"iconFilePath2":"d:/ymir work/ui/game/characterdetails/minus.dds",},
	4:{ "iconFilePath0":"d:/ymir work/ui/quest_re/tabcolor_5_collection.tga",	"iconFilePath1":"d:/ymir work/ui/game/characterdetails/plus.dds",	"iconFilePath2":"d:/ymir work/ui/game/characterdetails/minus.dds",},
	5:{ "iconFilePath0":"d:/ymir work/ui/quest_re/tabcolor_6_system.tga",		"iconFilePath1":"d:/ymir work/ui/game/characterdetails/plus.dds",	"iconFilePath2":"d:/ymir work/ui/game/characterdetails/minus.dds",},
	6:{ "iconFilePath0":"d:/ymir work/ui/quest_re/tabcolor_7_scroll.tga",		"iconFilePath1":"d:/ymir work/ui/game/characterdetails/plus.dds",	"iconFilePath2":"d:/ymir work/ui/game/characterdetails/minus.dds",},
	7:{ "iconFilePath0":"d:/ymir work/ui/quest_re/tabcolor_8_daily.tga",		"iconFilePath1":"d:/ymir work/ui/game/characterdetails/plus.dds",	"iconFilePath2":"d:/ymir work/ui/game/characterdetails/minus.dds",}
}

INFO_CHARACTER_PAGE_DESC={
	"BONUS_PAGE":localeinfo.BONUS_PAGE_TOOLTIP,
	"OTHER_PAGE":localeinfo.OTHER_PAGE_TOOLTIP,
}

def GetLoadedBonus():
	objBonusItemsInfo={
		0:{
			localeinfo.BONUS_PAGE_DAMAGE :
			[
				(localeinfo.DETAILS_20,item.GetApplyPoint(item.APPLY_CRITICAL_PCT)),
				(localeinfo.DETAILS_21,item.GetApplyPoint(item.APPLY_PENETRATE_PCT)),
				(localeinfo.DETAILS_5,item.GetApplyPoint(item.APPLY_ATTBONUS_MONSTER)),
				(localeinfo.DETAILS_0,item.GetApplyPoint(item.APPLY_ATTBONUS_STONE)),
				(localeinfo.DETAILS_NEW_1,item.GetApplyPoint(item.APPLY_ATTBONUS_BOSS)),
				(localeinfo.DETAILS_NEW_2,item.GetApplyPoint(item.APPLY_ATTBONUS_MEDI_PVM)),
				(localeinfo.DETAILS_3,item.GetApplyPoint(item.APPLY_ATTBONUS_ORC)),
				#(localeinfo.DETAILS_6,item.GetApplyPoint(item.APPLY_ATTBONUS_CZ)),
				(localeinfo.DETAILS_NEW_01,item.GetApplyPoint(item.APPLY_FIRST_ATTRIBUTE_BONUS)),
				(localeinfo.DETAILS_4,item.GetApplyPoint(item.APPLY_ATTBONUS_UNDEAD)),
				(localeinfo.DETAILS_7,item.GetApplyPoint(item.APPLY_ATTBONUS_ANIMAL)),
				(localeinfo.DETAILS_8,item.GetApplyPoint(item.APPLY_ATTBONUS_MILGYO)),
				(localeinfo.DETAILS_9,item.GetApplyPoint(item.APPLY_ATTBONUS_DEVIL)),
				(localeinfo.DETAILS_10,item.GetApplyPoint(item.APPLY_ATTBONUS_DESERT)),
				(localeinfo.DETAILS_11,item.GetApplyPoint(item.APPLY_ATTBONUS_INSECT)),
				(localeinfo.DETAILS_36,item.GetApplyPoint(item.APPLY_ATTBONUS_WARRIOR)),
				(localeinfo.DETAILS_37,item.GetApplyPoint(item.APPLY_ATTBONUS_ASSASSIN)),
				(localeinfo.DETAILS_38,item.GetApplyPoint(item.APPLY_ATTBONUS_SURA)),
				(localeinfo.DETAILS_39,item.GetApplyPoint(item.APPLY_ATTBONUS_SHAMAN)),
				(localeinfo.DETAILS_NEW_6,item.GetApplyPoint(item.APPLY_ATTBONUS_PLAYERS)),#if app.ENABLE_WOLFMAN:
				(localeinfo.DETAILS_1,item.GetApplyPoint(item.APPLY_ATTBONUS_HUMAN)),
				(localeinfo.DETAILS_71,item.GetApplyPoint(item.APPLY_MALL_ATTBONUS)),
				(localeinfo.DETAILS_12,item.GetApplyPoint(item.APPLY_ATT_GRADE_BONUS)),
				(localeinfo.DETAILS_14,item.GetApplyPoint(item.APPLY_NORMAL_HIT_DAMAGE_BONUS)),
				(localeinfo.DETAILS_16,item.GetApplyPoint(item.APPLY_SKILL_DAMAGE_BONUS)),
				(localeinfo.DETAILS_18,item.GetApplyPoint(item.APPLY_MELEE_MAGIC_ATTBONUS_PER)),
				(localeinfo.DETAILS_19,item.GetApplyPoint(item.APPLY_MAGIC_ATTBONUS_PER)),
				(localeinfo.DETAILS_30,item.GetApplyPoint(item.APPLY_ENCHANT_ELEC)),
				(localeinfo.DETAILS_31,item.GetApplyPoint(item.APPLY_ENCHANT_ICE)),
				(localeinfo.DETAILS_32,item.GetApplyPoint(item.APPLY_ENCHANT_DARK)),
				(localeinfo.DETAILS_33,item.GetApplyPoint(item.APPLY_ENCHANT_FIRE)),
				(localeinfo.DETAILS_34,item.GetApplyPoint(item.APPLY_ENCHANT_WIND)),
				(localeinfo.DETAILS_35,item.GetApplyPoint(item.APPLY_ENCHANT_EARTH)),
			],
		},

		1:{
			localeinfo.BONUS_PAGE_DEFEND :
			[
				(localeinfo.DETAILS_72,item.GetApplyPoint(item.APPLY_MALL_DEFBONUS)),
				(localeinfo.DETAILS_13,item.GetApplyPoint(item.APPLY_DEF_GRADE_BONUS)),
				(localeinfo.DETAILS_15,item.GetApplyPoint(item.APPLY_NORMAL_HIT_DEFEND_BONUS)),
				(localeinfo.DETAILS_17,item.GetApplyPoint(item.APPLY_SKILL_DEFEND_BONUS)),
				(localeinfo.DETAILS_22,item.GetApplyPoint(item.APPLY_ANTI_CRITICAL_PCT)),
				(localeinfo.DETAILS_23,item.GetApplyPoint(item.APPLY_ANTI_PENETRATE_PCT)),
				(localeinfo.DETAILS_NEW_23,item.GetApplyPoint(item.APPLY_SKILL_DEFEND_BONUS_BOSS_OR_MORE)),
				(localeinfo.DETAILS_NEW_24,item.GetApplyPoint(item.APPLY_RESIST_ZC)),
				(localeinfo.DETAILS_76,item.GetApplyPoint(item.APPLY_RESIST_MAGIC)),
				(localeinfo.DETAILS_24,item.GetApplyPoint(item.APPLY_RESIST_ELEC)),
				(localeinfo.DETAILS_25,item.GetApplyPoint(item.APPLY_RESIST_ICE)),
				(localeinfo.DETAILS_26,item.GetApplyPoint(item.APPLY_RESIST_DARK)),
				(localeinfo.DETAILS_27,item.GetApplyPoint(item.APPLY_RESIST_FIRE)),
				(localeinfo.DETAILS_28,item.GetApplyPoint(item.APPLY_RESIST_WIND)),
				(localeinfo.DETAILS_29,item.GetApplyPoint(item.APPLY_RESIST_EARTH)),
				(localeinfo.DETAILS_41,item.GetApplyPoint(item.APPLY_RESIST_WARRIOR)),
				(localeinfo.DETAILS_42,item.GetApplyPoint(item.APPLY_RESIST_ASSASSIN)),
				(localeinfo.DETAILS_43,item.GetApplyPoint(item.APPLY_RESIST_SURA)),
				(localeinfo.DETAILS_44,item.GetApplyPoint(item.APPLY_RESIST_SHAMAN)),
				(localeinfo.DETAILS_NEW_7,item.GetApplyPoint(item.APPLY_RESIST_PLAYERS)),#if app.ENABLE_WOLFMAN:
				(localeinfo.DETAILS_46,item.GetApplyPoint(item.APPLY_RESIST_SWORD)),
				(localeinfo.DETAILS_47,item.GetApplyPoint(item.APPLY_RESIST_TWOHAND)),
				(localeinfo.DETAILS_48,item.GetApplyPoint(item.APPLY_RESIST_DAGGER)),
				(localeinfo.DETAILS_50,item.GetApplyPoint(item.APPLY_RESIST_BELL)),
				(localeinfo.DETAILS_51,item.GetApplyPoint(item.APPLY_RESIST_FAN)),
				(localeinfo.DETAILS_52,item.GetApplyPoint(item.APPLY_RESIST_BOW)),
				(localeinfo.DETAILS_ATTBONUS_SWORD,item.GetApplyPoint(item.APPLY_RESIST_SWORD_REDUCTION)),
				(localeinfo.DETAILS_ATTBONUS_TWOHAND,item.GetApplyPoint(item.APPLY_RESIST_TWOHAND_REDUCTION)),
				(localeinfo.DETAILS_ATTBONUS_DAGGER,item.GetApplyPoint(item.APPLY_RESIST_DAGGER_REDUCTION)),
				(localeinfo.DETAILS_ATTBONUS_BELL,item.GetApplyPoint(item.APPLY_RESIST_BELL_REDUCTION)),
				(localeinfo.DETAILS_ATTBONUS_FAN,item.GetApplyPoint(item.APPLY_RESIST_FAN_REDUCTION)),
				(localeinfo.DETAILS_ATTBONUS_BOW,item.GetApplyPoint(item.APPLY_RESIST_BOW_REDUCTION)),
			],
		},
		2:{
			localeinfo.BONUS_PAGE_OTHER :
			[
				(localeinfo.DETAILS_HIT_PCT,item.GetApplyPoint(item.APPLY_HIT_PCT)),
				(localeinfo.DETAILS_75,item.GetApplyPoint(item.APPLY_MALL_GOLDBONUS)),
				(localeinfo.DETAILS_73,item.GetApplyPoint(item.APPLY_MALL_EXPBONUS)),
				(localeinfo.DETAILS_68,item.GetApplyPoint(item.APPLY_EXP_DOUBLE_BONUS)),
				(localeinfo.DETAILS_69,item.GetApplyPoint(item.APPLY_GOLD_DOUBLE_BONUS)),
				(localeinfo.DETAILS_70,item.GetApplyPoint(item.APPLY_ITEM_DROP_BONUS)),
				(localeinfo.DETAILS_53,item.GetApplyPoint(item.APPLY_STUN_PCT)),
				(localeinfo.DETAILS_54,item.GetApplyPoint(item.APPLY_SLOW_PCT)),
				(localeinfo.DETAILS_55,item.GetApplyPoint(item.APPLY_POISON_PCT)),
				(localeinfo.DETAILS_56,item.GetApplyPoint(item.APPLY_POISON_REDUCE)),
				(localeinfo.DETAILS_59,item.GetApplyPoint(item.APPLY_STEAL_HP)),
				(localeinfo.DETAILS_60,item.GetApplyPoint(item.APPLY_STEAL_SP)),
				(localeinfo.DETAILS_61,item.GetApplyPoint(item.APPLY_HP_REGEN)),
				(localeinfo.DETAILS_62,item.GetApplyPoint(item.APPLY_SP_REGEN)),
				(localeinfo.DETAILS_63,item.GetApplyPoint(item.APPLY_BLOCK)),
				(localeinfo.DETAILS_64,item.GetApplyPoint(item.APPLY_DODGE)),
				(localeinfo.DETAILS_65,item.GetApplyPoint(item.APPLY_REFLECT_MELEE)),
				(localeinfo.DETAILS_66,item.GetApplyPoint(item.APPLY_KILL_HP_RECOVER)),
				(localeinfo.DETAILS_67,item.GetApplyPoint(item.APPLY_KILL_SP_RECOVER)),
			],
		},
	}
	return objBonusItemsInfo

def GetLoadedStats():
	objStatsItemsInfo={
		0:{
			localeinfo.BONUS_PAGE_PVM :
			[
				(localeinfo.DETAILS_PVM_1,player.POINT_MONSTER_KILLED),
				(localeinfo.DETAILS_PVM_2,player.POINT_STONE_KILLED),
				(localeinfo.DETAILS_PVM_3,player.POINT_BOSS_KILLED),
			],
		},
		1:{
			localeinfo.BONUS_PAGE_PVP :
			[
				(localeinfo.DETAILS_PVP_1,player.POINT_BLUE_PLAYER_KILLED),
				(localeinfo.DETAILS_PVP_2,player.POINT_YELLOW_PLAYER_KILLED),
				(localeinfo.DETAILS_PVP_3,player.POINT_RED_PLAYER_KILLED),
			],
		},
	}
	return objStatsItemsInfo


class LabelDictListCreate(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.base_pos=(0,0)
		self.bonusSlot=None
		self.bonusName=None
		self.bonusValue=None
		self.apply_value=None

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)
	
	def __LoadWindow(self):
		self.SetSize(210,20)

		self.bonusSlot=ui.ImageBoxOld()
		self.bonusSlot.SetParent(self)
		self.bonusSlot.LoadImage("d:/ymir work/ui/game/characterdetails/bonus_item.tga")
		self.bonusSlot.SetPosition(10+3,0)
		self.bonusSlot.Show()

		self.bonusName=ui.TextLine()
		self.bonusName.SetParent(self.bonusSlot)
		self.bonusName.SetPosition(10+10,3)
		self.bonusName.SetWindowHorizontalAlignRight()
		self.bonusName.Show()

		self.bonusValue=ui.TextLine()
		self.bonusValue.SetParent(self.bonusSlot)
		self.bonusValue.SetPosition(-75,3)
		self.bonusValue.SetWindowHorizontalAlignCenter()
		self.bonusValue.SetHorizontalAlignCenter()
		self.bonusValue.Show()

	def SetBasePosition(self,x,y):
		self.base_pos=(x,y)
		self.SetPosition(x,y)

	def GetBasePosition(self):
		return self.base_pos

	def SetName(self,name):
		self.bonusName.SetText(str(name))

	def SetApplyValue(self,value):
		self.apply_value=value

	def RefreshApplyValue(self):
		if self.apply_value != None:
			value=0
			if self.apply_value == -1:
				value=0
			else:
				value=player.GetStatus(self.apply_value)
			self.bonusValue.SetText("{}".format(value))

class CharacterDetailsUI_New(ui.ScriptWindow):
	OBJ_SCROL_HEIGHT_POS=20
	SUB_MENU_POS_X=4+12
	SUB_MENU_POS_Y=2
	SUB_MENU_ICON_POS_X=5
	SUB_MENU_ICON_POS_Y=7

	def __init__(self,parent):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.isLoaded=0
		self.uiCharacterStatus=parent
		
		self.objTabButtonList=None
		self.statusImageTooltipDict=None
		
		self.objBonusElementary={}
		self.objStatsElementary={}
		
		self.firstPageClick=0
		
		self.objBonusItemsInfo={}
		self.objBonusCategoryList=[]
		self.objBonusCategoryBasePos=[]
		self.objBonusObjectList=[]
		self.objBonusSelectedCategory=-1
		
		self.objStatsItemsInfo={}
		self.objStatsCategoryList=[]
		self.objStatsCategoryBasePos=[]
		self.objStatsObjectList=[]
		self.objStatsSelectedCategory=-1
		
		self.toolTip=uitooltip.ToolTip()
		self.__LoadWindow()

	def __del__(self):
		self.uiCharacterStatus=0
		
		if self.toolTip!=0:
			self.toolTip.ClearToolTip()
			self.toolTip.HideToolTip()
			del self.toolTip
			self.toolTip=0
		
		self.ClearDictionary()
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.objTabButtonList=None
		self.statusImageTooltipDict=None
		
		self.objBonusElementary={}
		self.objStatsElementary={}
		
		self.firstPageClick=0
		
		self.objBonusItemsInfo={}
		self.objBonusCategoryList=[]
		self.objBonusCategoryBasePos=[]
		self.objBonusObjectList=[]
		self.objBonusSelectedCategory=-1
		
		self.objStatsItemsInfo={}
		self.objStatsCategoryList=[]
		self.objStatsCategoryBasePos=[]
		self.objStatsObjectList=[]
		self.objStatsSelectedCategory=-1
		
		self.ClearDictionary()

	def Open(self):
		self.RefreshStatus()
		self.Show()
		if app.__BL_MOUSE_WHEEL_TOP_WINDOW__:
			wndMgr.SetWheelTopWindow(self.hWnd)


	def Close(self):
		self.Hide()
		if app.__BL_MOUSE_WHEEL_TOP_WINDOW__:
			wndMgr.ClearWheelTopWindow()

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return
		
		self.isLoaded=1
		
		try:
			pyScrLoader=ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self,"UIScript/CharacterDetailsWindow.py")
		except:
			import exception
			exception.Abort("uiCharacterdetails_new.CharacterDetailsUI_New.LoadScriptFile.UIScript/CharacterDetailsWindow.py")
		
		try:
			self.objBonusItemsInfo=GetLoadedBonus()
			self.objStatsItemsInfo=GetLoadedStats()
		except:
			import exception
			exception.Abort("uiCharacterdetails_new.CharacterDetailsUI_New.__LoadedBonus.UIScript/CharacterDetailsWindow.py")
		
		try:
			self.__BindObject()
		except:
			import exception
			exception.Abort("uiCharacterdetails_new.CharacterDetailsUI_New.__BindObject.UIScript/CharacterDetailsWindow.py")
		
		try:
			self.__BindEvent()
		except:
			import exception
			exception.Abort("uiCharacterdetails_new.CharacterDetailsUI_New.__BindEvent.UIScript/CharacterDetailsWindow.py")

	def __BindObject(self):
		self.Width=253-3
		self.GetChild("TitleBar").CloseButtonHide()
		
		self.characterPageDict={
			0:self.GetChild("bonus_window"),
			1:self.GetChild("special_other_window")
		}
		
		self.objTabButtonList={
			0: self.GetChild("change_bonus_button"),
			1: self.GetChild("change_other_button"),
		}
		
		self.statusImageTooltipDict={
			"BONUS_PAGE":(self.GetChild("bonus_base_tooltip_image"),0),
			"OTHER_PAGE":(self.GetChild("special_base_tooltip_image"),0),
		}
		
		for statusImageKey in self.statusImageTooltipDict.keys():
			statusImageButton,statusImageDescKey=self.statusImageTooltipDict[statusImageKey]
			statusImageButton.Show()
			statusImageButton.Show()
		
		self.objBonusElementary={
			"window":self.GetChild("bonus_window"),
			"scrollbar":self.GetChild("bonus_scrollbar"),
			"max_height":300,
			"scroll_distance":0,
		}
		
		self.objBonusElementary["scrollbar"].Hide()
		
		self.objStatsElementary={\
			"window":self.GetChild("special_other_window"),
			"scrollbar":self.GetChild("special_scrollbar"),
			"max_height":300,
			"scroll_distance":0,
		}
		
		self.objStatsElementary["scrollbar"].Hide()

	def __BindEvent(self):
		for (tabCharacterKey,tabCharacterButton) in self.objTabButtonList.items():
			tabCharacterButton.SetEvent(ui.__mem_func__(self.SetStatusPage),tabCharacterKey)
			tabCharacterButton.ShowToolTip=lambda arg=tabCharacterKey: self.__OverInCharacterButton(arg)
			tabCharacterButton.HideToolTip=lambda arg=tabCharacterKey: self.__OverOutStatusImage()
		
		for statusImageKey in self.statusImageTooltipDict.keys():
			statusImageButton,statusImageDescKey=self.statusImageTooltipDict[statusImageKey]
			statusImageButton.SAFE_SetStringEvent("MOUSE_OVER_IN",self.__OverInStatusImage,statusImageKey,statusImageDescKey)
			statusImageButton.SAFE_SetStringEvent("MOUSE_OVER_OUT",self.__OverOutStatusImage)
		
		self.objBonusElementary["scrollbar"].SetScrollEvent(ui.__mem_func__(self.__OnScrollBonusPage))
		self.objStatsElementary["scrollbar"].SetScrollEvent(ui.__mem_func__(self.__OnScrollSpecialPage))
		
		self.SetStatusPage(self.firstPageClick)
		self.__LoadBonusPagesCategory()
		self.__LoadStaticInfoPagesCategory()

	def AdjustPosition(self,x,y):
		self.SetPosition(x + self.Width,y)

	def __LoadBonusPagesCategory(self):
		if not self.objBonusItemsInfo:
			return

		for (index,info) in self.objBonusItemsInfo.items():
			name=list(info.keys())[0]
			bonus=info[name]

			# fileName=obj_expend_img_path[index]['iconFilePath0']
			fileNameEx=obj_expend_img_path[index]['iconFilePath1']
			fileNameEx2=obj_expend_img_path[index]['iconFilePath2']

			separator=ui.SubTitleBarNew()
			separator.SetParent(self.objBonusElementary["window"])
			separator.MakeSubTitleBarNew(210,"red","d:/ymir work/ui/game/characterdetails/object_category_bg.tga",self.SUB_MENU_ICON_POS_X,self.SUB_MENU_ICON_POS_Y)
			separator.SetSize(210,22)
			separator.SetPosition(self.SUB_MENU_POS_X,self.SUB_MENU_POS_Y+(18 * index) + (7 * index))
			separator.SetTextAlignButton(name,0,10)
			# separator.SetQuestLabel("",len(bonus),178,18)
			separator.SetMiniImageNorm(fileNameEx)
			separator.SetMiniImageOpen(fileNameEx2)
			separator.SetEvent(ui.__mem_func__(self.__OnClickBonusPageSeparator),index,bonus)
			separator.Show()
			self.objBonusCategoryList.append((separator,bonus))
	
	def GetBonusBoardEndPosition(self):
		return self.objBonusElementary["max_height"]
	
	def GetFirstBonusPageObjectPosition(self):
		return (self.objBonusCategoryList[0][0].GetLocalPosition()[1])
	
	def GetLastBonusPageObjectPosition(self):
		if (self.objBonusSelectedCategory +1) == len(self.objBonusCategoryList):
			return (self.objBonusObjectList[-1].GetLocalPosition()[1] + self.OBJ_SCROL_HEIGHT_POS)
		
		return (self.objBonusCategoryList[-1][0].GetLocalPosition()[1] + self.objBonusCategoryList[-1][0].GetHeight())
	
	def GetOpenedCategorySize(self):
		if not self.objBonusObjectList:
			self.ClearOnList(0)
			return
		
		return (self.objBonusObjectList[-1].GetLocalPosition()[1] + self.OBJ_SCROL_HEIGHT_POS)-self.objBonusObjectList[0].GetLocalPosition()[1]
	
	def RefreshCategoryBasePosition(self):
		self.objBonusCategoryBasePos=[]
		for (label,_) in self.objBonusCategoryList:
			self.objBonusCategoryBasePos.append(label.GetLocalPosition())
	
	def RefreshScrollDistance(self):
		distance=self.GetLastBonusPageObjectPosition()-self.GetBonusBoardEndPosition()
		self.objBonusElementary["scroll_distance"]=distance
	
	def RefreshScrollBarState(self):
		self.objBonusElementary["scrollbar"].SetPos(0)
		canShowScroll=bool(self.GetLastBonusPageObjectPosition() > self.GetBonusBoardEndPosition())
		
		categoryLen={}
		categoryStep=-0.0
		
		for (index,info) in self.objBonusItemsInfo.items():
			name=list(info.keys())[0]
			bonus=info[name]
			categoryLen[index]=len(bonus)
			if self.objBonusSelectedCategory == index:
				categoryStep=categoryLen[index]
		
		self.objBonusElementary["scrollbar"].SetScrollStep(0.051 if categoryStep >= 15 and categoryStep <= 25 else float("0.0{}".format(categoryStep)))
		self.objBonusElementary["scrollbar"].SetMiddleBarSize(float(1.0) / float(len(self.objBonusCategoryList)))
		self.objBonusElementary["scrollbar"].Show() if canShowScroll else self.objBonusElementary["scrollbar"].Hide()

	def RefreshBonusPageItemInfo(self):
		for bonusObject in self.objBonusObjectList:
			bonusObject.RefreshApplyValue()
	
	def CloseAllBonusPageCat(self):
		for object in self.objBonusObjectList:	
			object.Hide()

		for ((label,_),index) in zip(self.objBonusCategoryList,xrange(len(self.objBonusCategoryList))):
			label.OpenCategory(0)
			label.SetPosition(self.SUB_MENU_POS_X,self.SUB_MENU_POS_Y+(18 * index) + (7 * index))
			label.Show()
			label.SetTop()

		self.objBonusObjectList=[]

	def SetBonusPageCategory(self,category):
		self.objBonusSelectedCategory=category

	def __OnClickBonusPageSeparator(self,catIndex,bonus):
		if self.objBonusSelectedCategory == catIndex :
			self.ClearOnList(0)
			return

		self.CloseAllBonusPageCat()
		self.objBonusCategoryList[catIndex][0].OpenCategory(1)
		self.SetBonusPageCategory(catIndex)

		catLabel=self.objBonusCategoryList[catIndex][0]
		catLabel_x,catLabel_y=catLabel.GetLocalPosition()
		
		for (bonus_info,index) in zip(bonus,xrange(len(bonus))):
			tmpCreatedObject=LabelDictListCreate()
			tmpCreatedObject.SetParent(self.objBonusElementary["window"])
			tmpCreatedObject.SetBasePosition(catLabel_x,catLabel_y + 30 + (self.OBJ_SCROL_HEIGHT_POS* index) + (2 * index))
			bonusDesc,bonusType=bonus_info
			tmpCreatedObject.SetName(bonusDesc)
			tmpCreatedObject.SetApplyValue(bonusType)
			tmpCreatedObject.RefreshApplyValue()
			tmpCreatedObject.Show()
			tmpCreatedObject.SetTop()
			self.objBonusObjectList.append(tmpCreatedObject)
		
		categorySize=self.GetOpenedCategorySize()
		for ((label,_),labelKey) in zip(self.objBonusCategoryList,xrange(len(self.objBonusCategoryList))):
			if labelKey <= catIndex:
				continue
		
			label_x,label_y=label.GetLocalPosition()
			label.SetPosition(label_x,label_y + categorySize + (self.OBJ_SCROL_HEIGHT_POS/2))
		
		self.RefreshCategoryBasePosition()
		self.RefreshScrollDistance()
		self.RefreshScrollBarState()
		self.CheckBonusPageRect()
	
	def __OnScrollBonusPage(self):
		scrollDistance=self.objBonusElementary["scroll_distance"]
		scrollPos=self.objBonusElementary["scrollbar"].GetPos()
		
		heightDistance=int(scrollPos * scrollDistance)

		for bonusObject in self.objBonusObjectList:
			bonusObject_x,bonusObject_y=bonusObject.GetBasePosition()
			bonusObject.SetPosition(bonusObject_x,int(bonusObject_y-heightDistance))

		for categoryKey in xrange(len(self.objBonusCategoryList)):
			catObject=self.objBonusCategoryList[categoryKey][0]
			category_x,category_y=self.objBonusCategoryBasePos[categoryKey]
			catObject.SetPosition(category_x,category_y-heightDistance)

		self.CheckBonusPageRect()

	def CheckBonusPageRect(self):
		def CanShow(posY,height):
			if posY < 1 or posY + height > self.GetBonusBoardEndPosition():
				return False
			return True
		
		for bonusObject in self.objBonusObjectList:
			bonusObject_x,bonusObject_y=bonusObject.GetLocalPosition()
			bonusObject_height=bonusObject.GetHeight()
			
			bonusObject.Show() if CanShow(bonusObject_y,bonusObject_height) else bonusObject.Hide()
		
		for (label,_) in self.objBonusCategoryList:
			blabel_x,label_y=label.GetLocalPosition()
			label_height=label.GetHeight()
			
			label.Show() if CanShow(label_y,label_height) else label.Hide()
	#b end

	#s start
	SUB_SPE_MENU_POS_X=4+12
	SUB_SPE_MENU_POS_Y=2
	SUB_SPE_MENU_ICON_POS_X=5
	SUB_SPE_MENU_ICON_POS_Y=7
	def __LoadStaticInfoPagesCategory(self):
		if not self.objStatsItemsInfo:
			return

		for (index,info) in self.objStatsItemsInfo.items():
			name=list(info.keys())[0]
			bonus=info[name]

			# fileName=obj_expend_img_path[index]['iconFilePath0']
			fileNameEx=obj_expend_img_path[index]['iconFilePath1']
			fileNameEx2=obj_expend_img_path[index]['iconFilePath2']

			separator=ui.SubTitleBarNew()
			separator.SetParent(self.objStatsElementary["window"])
			separator.MakeSubTitleBarNew(210,"red","d:/ymir work/ui/game/characterdetails/object_category_bg.tga",self.SUB_SPE_MENU_ICON_POS_X,self.SUB_SPE_MENU_ICON_POS_Y)
			separator.SetSize(210,22)
			separator.SetPosition(self.SUB_SPE_MENU_POS_X,self.SUB_SPE_MENU_POS_Y+(18 * index) + (7 * index))
			separator.SetTextAlignButton(name,0,10)
			# separator.SetQuestLabel(fileName,len(bonus),178,18)
			separator.SetMiniImageNorm(fileNameEx)
			separator.SetMiniImageOpen(fileNameEx2)
			separator.SetEvent(ui.__mem_func__(self.__OnClickSpecialPageSeparator),index,bonus)
			separator.Show()
			self.objStatsCategoryList.append((separator,bonus))
	
	def GetSpecialBoardEndPosition(self):
		return self.objStatsElementary["max_height"]
	
	def GetFirstSpecialPageObjectPosition(self):
		return (self.objStatsCategoryList[0][0].GetLocalPosition()[1])
	
	def GetLastSpecialPageObjectPosition(self):
		if (self.objStatsSelectedCategory +1) == len(self.objStatsCategoryList):
			return (self.objStatsObjectList[-1].GetLocalPosition()[1] + self.OBJ_SCROL_HEIGHT_POS)
		
		return (self.objStatsCategoryList[-1][0].GetLocalPosition()[1] + self.objStatsCategoryList[-1][0].GetHeight())
	
	def GetOpenedSpecialCategorySize(self):
		if not self.objStatsObjectList:
			self.ClearOnList(1)
			return

		return (self.objStatsObjectList[-1].GetLocalPosition()[1] + self.OBJ_SCROL_HEIGHT_POS)-self.objStatsObjectList[0].GetLocalPosition()[1]
	
	def RefreshSpecialCategoryBasePosition(self):
		self.objStatsCategoryBasePos=[]
		for (label,_) in self.objStatsCategoryList:
			self.objStatsCategoryBasePos.append(label.GetLocalPosition())
	
	def RefreshSpecialScrollDistance(self):
		distance=self.GetLastSpecialPageObjectPosition()-self.GetSpecialBoardEndPosition()
		self.objStatsElementary["scroll_distance"]=distance
	
	def RefreshSpecialScrollBarState(self):
		self.objStatsElementary["scrollbar"].SetPos(0)
		canShowScroll=bool(self.GetLastSpecialPageObjectPosition() > self.GetSpecialBoardEndPosition())

		categoryLen={}
		categoryStep=-0.0

		for (index,info) in self.objStatsItemsInfo.items():
			name=list(info.keys())[0]
			bonus=info[name]
			categoryLen[index]=len(bonus)
			if self.objStatsSelectedCategory == index:
				categoryStep=categoryLen[index]

		self.objStatsElementary["scrollbar"].SetScrollStep(0.051 if categoryStep >= 15 and categoryStep <= 25 else float("0.0{}".format(categoryStep)))
		self.objStatsElementary["scrollbar"].Show() if canShowScroll else self.objStatsElementary["scrollbar"].Hide()

	def RefreshSpecialPageItemInfo(self):
		for bonusObject in self.objStatsObjectList:
			bonusObject.RefreshApplyValue()

	def CloseAllSpecialPageCat(self):
		for object in self.objStatsObjectList:
			object.Hide()
		for ((label,_),index) in zip(self.objStatsCategoryList,xrange(len(self.objStatsCategoryList))):
			label.OpenCategory(0)
			label.SetPosition(self.SUB_SPE_MENU_POS_X,self.SUB_SPE_MENU_POS_Y+(18 * index) + (7 * index))
			label.Show()
			label.SetTop()
		
		self.objStatsObjectList=[]
	
	def SetSpecialPageCategory(self,category):
		self.objStatsSelectedCategory=category
	
	def __OnClickSpecialPageSeparator(self,catIndex,bonus):
		if self.objStatsSelectedCategory == catIndex:
			self.ClearOnList(1)
			return
		
		self.CloseAllSpecialPageCat()
		self.objStatsCategoryList[catIndex][0].OpenCategory(1)
		self.SetSpecialPageCategory(catIndex)
		
		catLabel=self.objStatsCategoryList[catIndex][0]
		catLabel_x,catLabel_y=catLabel.GetLocalPosition()
		
		for (bonus_info,index) in zip(bonus,xrange(len(bonus))):
			tmpCreatedObject=LabelDictListCreate()
			tmpCreatedObject.SetParent(self.objStatsElementary["window"])
			tmpCreatedObject.SetBasePosition(catLabel_x,catLabel_y + 30 + (self.OBJ_SCROL_HEIGHT_POS* index) + (2 * index))
			bonusDesc,bonusType=bonus_info
			tmpCreatedObject.SetName(bonusDesc)
			tmpCreatedObject.SetApplyValue(bonusType)
			tmpCreatedObject.RefreshApplyValue()
			tmpCreatedObject.Show()
			tmpCreatedObject.SetTop()
			self.objStatsObjectList.append(tmpCreatedObject)
		
		categorySize=self.GetOpenedSpecialCategorySize()
		for ((label,_),labelKey) in zip(self.objStatsCategoryList,xrange(len(self.objStatsCategoryList))):
			if labelKey <= catIndex:
				continue
			
			label_x,label_y=label.GetLocalPosition()
			label.SetPosition(label_x,label_y + categorySize + (self.OBJ_SCROL_HEIGHT_POS/2))
		
		self.RefreshSpecialCategoryBasePosition()
		self.RefreshSpecialScrollDistance()
		self.RefreshSpecialScrollBarState()
		self.CheckSpecialPageRect()
	
	def __OnScrollSpecialPage(self):
		scrollDistance=self.objStatsElementary["scroll_distance"]
		scrollPos=self.objStatsElementary["scrollbar"].GetPos()
		
		heightDistance=scrollPos * scrollDistance
		
		for bonusObject in self.objStatsObjectList:
			bonusObject_x,bonusObject_y=bonusObject.GetBasePosition()
			bonusObject.SetPosition(bonusObject_x,bonusObject_y-heightDistance)
		
		for categoryKey in xrange(len(self.objStatsCategoryList)):
			catObject=self.objStatsCategoryList[categoryKey][0]
			category_x,category_y=self.objStatsCategoryBasePos[categoryKey]
			catObject.SetPosition(category_x,category_y-heightDistance)
		
		self.CheckSpecialPageRect()
	
	def CheckSpecialPageRect(self):
		def CanShow(posY,height):
			if posY < 1 or posY + height > self.GetSpecialBoardEndPosition():
				return False
			return True
		
		for bonusObject in self.objStatsObjectList:
			bonusObject_x,bonusObject_y=bonusObject.GetLocalPosition()
			bonusObject_height=bonusObject.GetHeight()
			
			bonusObject.Show() if CanShow(bonusObject_y,bonusObject_height) else bonusObject.Hide()
		
		for (label,_) in self.objStatsCategoryList:
			blabel_x,label_y=label.GetLocalPosition()
			label_height=label.GetHeight()
			
			label.Show() if CanShow(label_y,label_height) else label.Hide()

	def ClearIstrOnList(self):
		self.SetBonusPageCategory(-1)
		self.CloseAllBonusPageCat()
		self.objBonusElementary["scrollbar"].Hide()
	#s end

	def ClearOnList(self,catKey):
		if catKey == 0:
			self.SetBonusPageCategory(-1)
			self.CloseAllBonusPageCat()
			self.objBonusElementary["scrollbar"].Hide()
		else:
			self.SetSpecialPageCategory(-1)
			self.CloseAllSpecialPageCat()
			self.objStatsElementary["scrollbar"].Hide()

	def GetStatusPage(self):
		return self.firstPageClick

	def SetStatusPage(self,statusPage):
		self.firstPageClick=statusPage
		for key,label in self.characterPageDict.items():
			label.Show() if key == statusPage else label.Hide()
		
		for key_b,button  in self.objTabButtonList.items():
			button.SetUp() if key_b != statusPage else button.Down()

	def OnRunMouseWheel(self,nLen):
		if self.GetStatusPage() == 0:
			if self.objBonusElementary["scrollbar"].IsShow():
				if nLen > 0:
					self.objBonusElementary["scrollbar"].OnUp()
				else:
					self.objBonusElementary["scrollbar"].OnDown()
		elif self.GetStatusPage() == 1:
			if self.objStatsElementary["scrollbar"].IsShow():
				if nLen > 0:
					self.objStatsElementary["scrollbar"].OnUp()
				else:
					self.objStatsElementary["scrollbar"].OnDown()
		return True

	# if app.__BL_MOUSE_WHEEL_TOP_WINDOW__:
		# def OnMouseWheelButtonUp(self):
			# if self.GetStatusPage() == 0:
				# if self.objBonusElementary["scrollbar"].IsShow():
					# self.objBonusElementary["scrollbar"].OnUp()

			# elif self.GetStatusPage() == 1:
				# if self.objStatsElementary["scrollbar"].IsShow():
					# self.objStatsElementary["scrollbar"].OnUp()
					# return True

			# return False

		# def OnMouseWheelButtonDown(self):
			# if self.GetStatusPage() == 0:
				# if self.objBonusElementary["scrollbar"].IsShow():
					# self.objBonusElementary["scrollbar"].OnDown()

			# elif self.GetStatusPage() == 1:
				# if self.objStatsElementary["scrollbar"].IsShow():
					# self.objStatsElementary["scrollbar"].OnDown()
					# return True

			# return False

	def __OverInStatusImage(self,stat,statType):
		try:
			manage_desc=[]
			if statType == 0:
				manage_desc=INFO_CHARACTER_PAGE_DESC
			
			self.__ShowStateImageTooltip(manage_desc[stat])
		except KeyError:
			pass

	def __OverOutStatusImage(self):
		self.toolTip.Hide()

	def __ShowStateImageTooltip(self,statDesc):
		self.toolTip.ClearToolTip()
		self.toolTip.AppendTextLine(statDesc)
		self.toolTip.Show()

	def __OverInCharacterButton(self,stat):
		m_text_tooltip=[localeinfo.BONUS_PAGE_TOOLTIP,localeinfo.STATUS_PAGE_TOOLTIP, localeinfo.OTHER_PAGE_TOOLTIP]
		self.toolTip.ClearToolTip()
		self.toolTip.AppendTextLine(m_text_tooltip[stat])
		self.toolTip.Show()

	def RefreshStatus(self):
		self.RefreshBonusPageItemInfo()
		self.RefreshSpecialPageItemInfo()

	def OnMoveWindow(self, x, y):
		if self.uiCharacterStatus:
			self.uiCharacterStatus.AdjustPosition(x, y, self.Width)
