# coding: latin_1

import app
import chr
import player
import net

import ui
import localeinfo
import item
import skill
import guild
import uitooltip
import math
import uicommon
import constinfo

import systemSetting

# One knob for every affect-bar icon: 32px source art * scale = on-screen size.
# Keep AffectShower.IMAGE_STEP >= 32 * AFFECT_ICON_SCALE + gap.
AFFECT_ICON_SCALE = 0.8125

if app.USE_PERSO_SIZE_ON_AFFECT_SHOWER:
	import wndMgr

if app.USE_RENEWAL_AFFECT_SHOWER:
	import player
	from _weakref import proxy

	import uicommon
	import uitooltip

	overInImage=None
	affectDict={}

	def TypeToAffect(affect):
		_dict = {
			chr.AFFECT_JEONGWI:3,
			chr.AFFECT_GEOMGYEONG:4,
			chr.AFFECT_CHEONGEUN:19,
			chr.AFFECT_GYEONGGONG:49,
			chr.AFFECT_EUNHYEONG:34,
			chr.AFFECT_GWIGEOM:63,
			chr.AFFECT_GONGPO:64,
			chr.AFFECT_JUMAGAP:65,
			chr.AFFECT_HOSIN:94,
			chr.AFFECT_BOHO:95,
			chr.AFFECT_KWAESOK:110,
			chr.AFFECT_HEUKSIN:79,
			chr.AFFECT_MUYEONG:78,
			chr.AFFECT_GICHEON:96,
			chr.AFFECT_JEUNGRYEOK:111,
			chr.AFFECT_PABEOP:66,
		}
		
		return _dict[affect] if _dict.has_key(affect) else affect

	def TypeToAffectReal(affect):
		if app.ENABLE_ITEM_BUFF_SYSTEM:
			_dict = {
				chr.AFFECT_JEONGWI:3,
				chr.AFFECT_GEOMGYEONG:4,
				chr.AFFECT_CHEONGEUN:19,
				chr.AFFECT_EUNHYEONG:34,
				chr.AFFECT_GYEONGGONG:49,
				chr.AFFECT_GWIGEOM:63,
				chr.AFFECT_GONGPO:64,
				chr.AFFECT_JUMAGAP:65,
				chr.AFFECT_MUYEONG:78,
				chr.AFFECT_HEUKSIN:79,
				chr.AFFECT_HOSIN:94,
				chr.AFFECT_BOHO:95,
				chr.AFFECT_GICHEON:96,
				chr.AFFECT_KWAESOK:110,
				chr.AFFECT_JEUNGRYEOK:111,
				chr.NEW_AFFECT_POLYMORPH:220,
				chr.AFFECT_SKILL_RESIST_BUFF:832,
				chr.AFFECT_SKILL_CRITICAL_BUFF:833,
				chr.AFFECT_SKILL_REFLECT_BUFF:834,
			}
		else:
			_dict = {
				chr.AFFECT_JEONGWI:3,
				chr.AFFECT_GEOMGYEONG:4,
				chr.AFFECT_CHEONGEUN:19,
				chr.AFFECT_EUNHYEONG:34,
				chr.AFFECT_GYEONGGONG:49,
				chr.AFFECT_GWIGEOM:63,
				chr.AFFECT_GONGPO:64,
				chr.AFFECT_JUMAGAP:65,
				chr.AFFECT_MUYEONG:78,
				chr.AFFECT_HEUKSIN:79,
				chr.AFFECT_HOSIN:94,
				chr.AFFECT_BOHO:95,
				chr.AFFECT_GICHEON:96,
				chr.AFFECT_KWAESOK:110,
				chr.AFFECT_JEUNGRYEOK:111,
				chr.NEW_AFFECT_POLYMORPH:220,
			}

		return _dict[affect] if _dict.has_key(affect) else affect

if app.USE_PREMIUM_FEATURES:
	PREMIUM_AFFECT_TUPLE = (chr.AFFECT_PREMIUM_NORMAL, chr.AFFECT_PREMIUM_PLUS,)

if app.ENABLE_CONQUEROR_LEVEL:
	class SungMaAffectImage(ui.ExpandedImageBox):

		TITLE_COLOR = 0xffF1E6C0
		FONT_COLOR = 0xffC1C1C1

		def __init__(self):
			ui.ExpandedImageBox.__init__(self)

			self.toolTip = uitooltip.ToolTip(280)
			self.toolTip.HideToolTip()

		def __del__(self):
			ui.ExpandedImageBox.__del__(self)

		def SetSungmaValue(self, str, hp, move, immune):
			self.str = str
			self.hp = hp
			self.move = move
			self.immune = immune

			try:
				self.LoadImage("d:/ymir work/ui/skill/common/affect/sungma_buff.sub")
			except:
				import dbg
				dbg.TraceError("SungMaAffectImage.SetSungmaValue(str=%d, hp=%d, move=%d, immune=%d) - LoadError %s" % (str, hp, move, immune, fileName))

			self.SetScale(AFFECT_ICON_SCALE, AFFECT_ICON_SCALE)

			self.toolTip.ClearToolTip()
			if localeinfo.IsARABIC():
				self.toolTip.AppendSungmaTextLine(localeinfo.TOOLTIP_AFFECT_SUNGMA_DESC, self.TITLE_COLOR, False)
				self.toolTip.AppendSungmaTextLine((localeinfo.TOOLTIP_AFFECT_SUNGMA_STR % self.str), self.FONT_COLOR, False)
				self.toolTip.AppendSungmaTextLine((localeinfo.TOOLTIP_AFFECT_SUNGMA_HP % self.hp), self.FONT_COLOR, False)
				self.toolTip.AppendSungmaTextLine((localeinfo.TOOLTIP_AFFECT_SUNGMA_MOVE % self.move), self.FONT_COLOR, False)
				self.toolTip.AppendSungmaTextLine((localeinfo.TOOLTIP_AFFECT_SUNGMA_IMMUNE % self.immune), self.FONT_COLOR, False)
			else:
				self.toolTip.AppendTextLine(localeinfo.TOOLTIP_AFFECT_SUNGMA_DESC, self.TITLE_COLOR, False)
				self.toolTip.AppendTextLine((localeinfo.TOOLTIP_AFFECT_SUNGMA_STR % self.str), self.FONT_COLOR, False)
				self.toolTip.AppendTextLine((localeinfo.TOOLTIP_AFFECT_SUNGMA_HP % self.hp), self.FONT_COLOR, False)
				self.toolTip.AppendTextLine((localeinfo.TOOLTIP_AFFECT_SUNGMA_MOVE % self.move), self.FONT_COLOR, False)
				self.toolTip.AppendTextLine((localeinfo.TOOLTIP_AFFECT_SUNGMA_IMMUNE % self.immune), self.FONT_COLOR, False)
				
		def OnMouseOverIn(self):
			self.toolTip.ShowToolTip()

		def OnMouseOverOut(self):
			self.toolTip.HideToolTip()

class LovePointImage(ui.ExpandedImageBox):
	def __del__(self):
		ui.ExpandedImageBox.__del__(self)

	def __init__(self):
		ui.ExpandedImageBox.__init__(self)
		self.loverName=""
		self.lovePoint=0

	def SetLoverInfo(self,name,lovePoint):
		self.loverName=name
		self.lovePoint=lovePoint
		self.__Refresh()

	def OnUpdateLovePoint(self,lovePoint):
		self.lovePoint=lovePoint
		self.__Refresh()

	def __Refresh(self):
		self.lovePoint=max(0,self.lovePoint)
		self.lovePoint=min(100,self.lovePoint)
		
		loveGrade=0 if 0==self.lovePoint else self.lovePoint / 25 + 1
		FILE_PATH="d:/ymir work/ui/pattern/LovePoint/"
		FILE_DICT={
			0:FILE_PATH + "01.dds",
			1:FILE_PATH + "02.dds",
			2:FILE_PATH + "02.dds",
			3:FILE_PATH + "03.dds",
			4:FILE_PATH + "04.dds",
			5:FILE_PATH + "05.dds",
		}
		
		fileName=FILE_DICT.get(loveGrade,FILE_PATH+"00.dds")
		try:
			self.LoadImage(fileName)
			self.SetScale(AFFECT_ICON_SCALE, AFFECT_ICON_SCALE)
		except:
			import dbg
			dbg.TraceError("LovePointImage.SetLoverInfo(lovePoint=%d) - LoadError %s" % (self.lovePoint,fileName))

	def OnMouseOverIn(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.ClearToolTip()
			interfaceHandler.tooltipItem.AutoAppendNewTextLineResize(self.loverName,0xffE9E7D2)
			interfaceHandler.tooltipItem.AppendSpace(5)
			interfaceHandler.tooltipItem.AutoAppendNewTextLineResize(localeinfo.AFF_LOVE_POINT % self.lovePoint)
			interfaceHandler.tooltipItem.ShowToolTip()

	def OnMouseOverOut(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.HideToolTip()

class HorseImage(ui.ExpandedImageBox):
	def __del__(self):
		ui.ExpandedImageBox.__del__(self)

	def __init__(self):
		ui.ExpandedImageBox.__init__(self)
		self.descriptions=[]

	def __GetHorseGrade(self,level):
		return 0 if level==0 else (level-1)/10 + 1

	def SetState(self,level,health,battery):
		self.descriptions=[]
		if level>0:
			try:
				grade=self.__GetHorseGrade(level)
				self.__AppendText(localeinfo.LEVEL_LIST[grade])
			except IndexError:
				return
			
			try:
				healthName=localeinfo.HEALTH_LIST[health]
				if len(healthName)>0:
					self.__AppendText(healthName)
			except IndexError:
				return
			
			if health>0 and battery==0:
				self.__AppendText(localeinfo.NEEFD_REST)
			
			try:
				FILE_PATH="d:/ymir work/ui/pattern/HorseState/"
				FILE_DICT={
					00:FILE_PATH+"00.dds",
					01:FILE_PATH+"00.dds",
					02:FILE_PATH+"00.dds",
					03:FILE_PATH+"00.dds",
					10:FILE_PATH+"10.dds",
					11:FILE_PATH+"11.dds",
					12:FILE_PATH+"12.dds",
					13:FILE_PATH+"13.dds",
					20:FILE_PATH+"20.dds",
					21:FILE_PATH+"21.dds",
					22:FILE_PATH+"22.dds",
					23:FILE_PATH+"23.dds",
					30:FILE_PATH+"30.dds",
					31:FILE_PATH+"31.dds",
					32:FILE_PATH+"32.dds",
					33:FILE_PATH+"33.dds",
				}
				fileName=FILE_DICT[health*10+battery]
			except KeyError:
				return
			
			try:
				self.LoadImage(fileName)
				self.SetScale(AFFECT_ICON_SCALE, AFFECT_ICON_SCALE)
			except:
				return

	def __AppendText(self,text):
		self.descriptions.append(text)

	def OnMouseOverIn(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.ClearToolTip()

			for text in self.descriptions:
				interfaceHandler.tooltipItem.AutoAppendNewTextLineResize(text)

			if len(self.descriptions):
				interfaceHandler.tooltipItem.ShowToolTip()

	def OnMouseOverOut(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.HideToolTip()

class PvPOrderImage(ui.ExpandedImageBox):

	def __init__(self):
		ui.ExpandedImageBox.__init__(self)

		self.toolTip = uitooltip.ToolTip(280)
		self.toolTip.HideToolTip()

	def __del__(self):
		ui.ExpandedImageBox.__del__(self)

	def Setup(self):
		# TBD ASSET: placeholder icon until the final PvP Order art lands
		try:
			self.LoadImage("icon/affectshower/pvp_aura.png")
		except:
			import dbg
			dbg.TraceError("PvPOrderImage.Setup - LoadError icon/affectshower/buff_1.tga")

		tt = self.toolTip
		tt.ClearToolTip()
		self.__AppendLine(getattr(localeinfo, "PVP_ORDER_NAME", "PvP Order"), tt.TITLE_COLOR)
		tt.AppendSpace(5)
		self.__AppendLine(getattr(localeinfo, "PVP_ORDER_TOOLTIP_BENEFITS", "[Benefits]"), tt.FONT_COLOR)
		for i in xrange(1, 6):
			text = getattr(localeinfo, "PVP_ORDER_TOOLTIP_BENEFIT%d" % i, "")
			if text:
				self.__AppendLine(text, tt.SPECIAL_POSITIVE_COLOR)
		tt.AppendSpace(5)
		self.__AppendLine(getattr(localeinfo, "PVP_ORDER_TOOLTIP_LIMITS", "[Limitations]"), tt.FONT_COLOR)
		for i in xrange(1, 3):
			text = getattr(localeinfo, "PVP_ORDER_TOOLTIP_LIMIT%d" % i, "")
			if text:
				self.__AppendLine(text, tt.NEGATIVE_COLOR)

	def __AppendLine(self, text, color):
		self.toolTip.AppendTextLine(text, color, True, True)

	def OnMouseOverIn(self):
		self.toolTip.ShowToolTip()

	def OnMouseOverOut(self):
		self.toolTip.HideToolTip()

if app.ENABLE_GROWTH_PET_SYSTEM:
	class GrowthPetImage(ui.ExpandedImageBox):
		def __init__(self):
			ui.ExpandedImageBox.__init__(self)
			
			self.toolTipText=None
			self.description=None

		def __del__(self):
			ui.ExpandedImageBox.__del__(self)

		def SetToolTipText(self,text,x=0,y=-19):
			if not self.toolTipText:
				textLine=ui.TextLine()
				textLine.SetParent(self)
				textLine.SetSize(0,0)
				textLine.SetOutline()
				textLine.Hide()
				self.toolTipText=textLine

			self.toolTipText.SetText(text)
			w,h=self.toolTipText.GetTextSize()
			if localeinfo.IsARABIC():
				self.toolTipText.SetPosition(w+20,y)
			else:
				self.toolTipText.SetPosition(max(0,x + self.GetWidth()/2 - w/2),y)

		def SetDescription(self,description):
			self.description=description

		def OnMouseOverIn(self):
			if self.toolTipText:
				self.toolTipText.Show()

		def OnMouseOverOut(self):
			if self.toolTipText:
				self.toolTipText.Hide()

class AffectImage(ui.ExpandedImageBox):
	def __init__(self):
		ui.ExpandedImageBox.__init__(self)
		
		self.toolTipText=None
		self.isSkillAffect=False
		self.description=None
		self.endTime=0
		self.affect=None
		self.isClocked=True

		if app.USE_RENEWAL_AFFECT_SHOWER:
			self.isCanRemove=False

		if app.USE_PREMIUM_FEATURES:
			self.tool_tip = None

	def __del__(self):
		if app.USE_PREMIUM_FEATURES and self.tool_tip:
			self.tool_tip.ClearToolTip()
			del self.tool_tip
			self.tool_tip = None

		ui.ExpandedImageBox.__del__(self)

	def SetAffect(self,affect):
		self.affect=affect

	def GetAffect(self):
		return self.affect

	def SetDescription(self,description):
		self.description=description

	def SetDuration(self,duration):
		self.endTime=0
		if duration > 0:
			self.endTime=app.GetGlobalTimeStamp() + duration

	if app.USE_RENEWAL_AFFECT_SHOWER:
		def FormatTime(self,seconds):
			if seconds <= 0:
				return "0s"
			
			m,s=divmod(seconds,60)
			h,m=divmod(m,60)
			d,h=divmod(h,24)
			timeText=""
			
			if d > 0:
				timeText += "{}{}".format(d,localeinfo.NEW_AFFECT_DAY)
				timeText += " "
			
			if h > 0:
				timeText += "{}{}".format(h,localeinfo.NEW_AFFECT_HOUR)
				timeText += " "
			
			if m > 0:
				timeText += "{}{}".format(m,localeinfo.NEW_AFFECT_MIN)
				timeText += " "
			
			if s > 0:
				timeText += "{}{}".format(s,localeinfo.NEW_AFFECT_SECOND)
			
			return timeText

		def AddAffect(self,pointIdx,pointVal):
			if not [pointIdx,pointVal] in self.affectList:
				self.affectList.append([pointIdx,pointVal])

		def RemoveAffect(self,pointIdx,pointVal):
			if [pointIdx,pointVal] in self.affectList:
				del self.affectList[self.affectList.index([pointIdx,pointVal])]
	else:
		def SetToolTipText(self,text,x=0,y=-19):
			if not self.toolTipText:
				textLine=uitooltip.ToolTip()
				textLine.ClearToolTip()
				textLine.AutoAppendTextLine(text)
				textLine.AlignHorizonalCenter()
				textLine.Hide()

				self.toolTipText=textLine

		def UpdateAutoPotionDescription(self):
			potionType=0
			if self.affect==chr.NEW_AFFECT_AUTO_HP_RECOVERY:
				potionType=player.AUTO_POTION_TYPE_HP
			else:
				potionType=player.AUTO_POTION_TYPE_SP

			isActivated,currentAmount,totalAmount,slotIndex=player.GetAutoPotionInfo(potionType)
			
			amountPercent=0.0
			
			try:
				amountPercent=(float(currentAmount) / totalAmount) * 100.0
			except:
				amountPercent=100.0
			
			self.SetToolTipText(self.description % amountPercent,0,40)

		def SetClock(self,isClocked):
			self.isClocked=isClocked

		def UpdateDescription(self):
			if not self.isClocked:
				self.__UpdateDescription2()
				return
			
			if not self.description:
				return
			
			toolTip=self.description
			if self.endTime > 0:
				leftTime=localeinfo.SecondToDHM(self.endTime - app.GetGlobalTimeStamp())
				toolTip += " (%s:%s)" % (localeinfo.LEFT_TIME,leftTime)
			
			self.SetToolTipText(toolTip,0,40)

		def __UpdateDescription2(self):
			if not self.description:
				return
			
			toolTip=self.description
			self.SetToolTipText(toolTip,0,40)

	def SetSkillAffectFlag(self,flag):
		self.isSkillAffect=flag

	def IsSkillAffect(self):
		return self.isSkillAffect

	def OnMouseOverIn(self):
		if app.USE_RENEWAL_AFFECT_SHOWER:
			global overInImage

		if app.USE_PREMIUM_FEATURES:
			if self.affect in PREMIUM_AFFECT_TUPLE:
				if not self.tool_tip:
					self.tool_tip = uitooltip.ToolTip()
					self.tool_tip.ClearToolTip()

					self.tool_tip.AppendTextLine(localeinfo.PREMIUM_NORMAL_TOOLTIP_TITLE if self.affect == chr.AFFECT_PREMIUM_NORMAL else localeinfo.PREMIUM_PLUS_TOOLTIP_TITLE, self.tool_tip.TITLE_COLOR)
					self.tool_tip.AppendSpace(5)

					self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFITS, resizeWidth = True)
					self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT1, resizeWidth = True)
					self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT2, resizeWidth = True)
					self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT3, resizeWidth = True)
					self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT4, resizeWidth = True)
					self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT5, resizeWidth = True)

					if self.affect == chr.AFFECT_PREMIUM_PLUS:
						self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT6, resizeWidth = True)
						self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT7, resizeWidth = True)
						self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT8, resizeWidth = True)
						self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT9, resizeWidth = True)
						self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT10, resizeWidth = True)
						self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT11, resizeWidth = True)
						self.tool_tip.AppendTextLine(localeinfo.PREMIUM_TOOLTIP_BENEFIT12, resizeWidth = True)

					self.tool_tip.AppendSpace(5)
					self.tool_tip.AppendTextLine(localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(self.endTime - app.GetGlobalTimeStamp()), resizeWidth = True)

				self.tool_tip.ShowToolTip()
				return

		if app.USE_RENEWAL_AFFECT_SHOWER:
			interface = systemSetting.GetInterfaceHandler()
			if interface:
				tooltip=interface.tooltipSkill if self.IsSkillAffect() else interface.tooltipItem
				if tooltip:
					tooltip.ClearToolTip()
					
					global affectDict
					overInImage=proxy(self)
					affect=TypeToAffect(self.GetAffect()) if self.IsSkillAffect() else self.GetAffect()

					if affect==chr.NEW_AFFECT_AUTO_HP_RECOVERY or\
						affect==chr.NEW_AFFECT_AUTO_SP_RECOVERY:
						potionType=player.AUTO_POTION_TYPE_HP if affect==chr.NEW_AFFECT_AUTO_HP_RECOVERY\
								else player.AUTO_POTION_TYPE_SP
						
						(isActivated,currentAmount,totalAmount,slotIndex)=player.GetAutoPotionInfo(potionType)
						amountPercent=0.0
						
						try:
							amountPercent=(float(currentAmount) / totalAmount) * 100.0
						except:
							amountPercent=100.0
						
						tooltip.AutoAppendNewTextLineResize(self.description % amountPercent,0xffC5C7C4)
					else:
						affectData=affectDict[affect] if affectDict.has_key(affect) else {}
						affectList=affectData["affect"] if affectData.has_key("affect") else []
						maxDuration=affectData["duration"] if affectData.has_key("duration") else 0
						if self.description:
							tooltip.AutoAppendNewTextLineResize(self.description,0xffE9E7D2)
							tooltip.AppendSpace(5)
						
						if affect == chr.NEW_AFFECT_MINING_AURA:   # Mining Rework: aura buff bonus
							tooltip.AutoAppendNewTextLineResize(localeinfo.TOOLTIP_MINING_AURA_DESC, 0xff95A693)
						elif affect == getattr(chr, "NEW_AFFECT_FISHING_AURA", 681):   # Fishing Rework: aura buff bonus
							tooltip.AutoAppendNewTextLineResize(getattr(localeinfo, "TOOLTIP_FISHING_AURA_DESC", "Fishing success rate  +20%"), 0xff95A693)
						isPoison = chr.AFFECT_POISON == affect and not self.IsSkillAffect()
						if self.IsSkillAffect() and not isPoison:
							isBuffiAffect = affectData.get("buffi", False)
							slotIndex=player.GetSkillSlotIndex(affect)
							if slotIndex==None or isBuffiAffect:
								for data in affectList:
									if data[0] != 0 and uitooltip.ItemToolTip.POINT_DICT.has_key(data[0]):
										effectText = uitooltip.ItemToolTip.POINT_DICT[data[0]](data[1])
										if isBuffiAffect:
											effectText = "%s %s" % (effectText, getattr(localeinfo, "TOOLTIP_BUFFI_PVM_ONLY", "(PvM only)"))
										tooltip.AutoAppendNewTextLineResize(effectText,0xff95A693)
							else:
								tooltip.SetSkillEx(affect)
						elif affect == chr.NEW_AFFECT_FISHES:
							for data in affectList:
								if data[0] != 0 and uitooltip.ItemToolTip.POINT_DICT.has_key(data[0]):
									fishLine = uitooltip.ItemToolTip.POINT_DICT[data[0]](data[1]).replace("+-", "-")
									tooltip.AutoAppendNewTextLineResize(fishLine, 0xffCC6666 if data[1] < 0 else 0xff95A693)
							fishEnds = affectData.get("fish_ends", {}).values()
							if [end for end in fishEnds if end == 0]:
								tooltip.AutoAppendNewTextLineResize(getattr(localeinfo, "TOOLTIP_FISH_PERMANENT", "Permanent until replaced or removed"), 0xffE9E7D2)
							if [end for end in fishEnds if end > 0]:
								tooltip.AutoAppendNewTextLineResize(getattr(localeinfo, "TOOLTIP_FISH_COMBAT_TIME", "Drains only while fighting"), 0xffC5C7C4)
						elif affect == getattr(chr, "NEW_AFFECT_SOLO_LEADERSHIP", 901):
							# Which of the six roles is active (and its value) comes from the
							# server's LeadershipBonus push, not from this affect's point list.
							roleIdx = constinfo.SOLO_LEADERSHIP_ACTIVE
							if 1 <= roleIdx <= 6:
								tooltip.AutoAppendNewTextLineResize(getattr(localeinfo, "SOLO_LEADERSHIP_ROLE_%d" % roleIdx), 0xffFFD200)
								tooltip.AutoAppendNewTextLineResize(getattr(localeinfo, "SOLO_LEADERSHIP_GRANT_%d" % roleIdx) % constinfo.SOLO_LEADERSHIP_BONUS[roleIdx - 1], 0xff95A693)
						elif affect == getattr(chr, "NEW_AFFECT_DS_SET", 543):
							# Dragon Soul set bonus: the flat stats live in the DS window (fed by the
							# server's DSSetBonus command), not in this affect's point list -- pull them.
							dsWnd = getattr(systemSetting.GetInterfaceHandler(), "wndDragonSoul", None)
							dsState = dsWnd.GetSetBonusState() if dsWnd and hasattr(dsWnd, "GetSetBonusState") else None
							if dsState and dsState[0] >= 0:
								dsTier, dsPoints, dsNext, dsApplys = dsState
								tooltip.AutoAppendNewTextLineResize(getattr(localeinfo, "DRAGONSOUL_SET_TIER_NAME", "Tier %d") % (dsTier + 1,), 0xffFFD200)
								for (dsType, dsValue) in dsApplys:
									dsLine = tooltip.GetAffectString(dsType, dsValue)
									if dsLine:
										tooltip.AutoAppendNewTextLineResize(dsLine, tooltip.GetChangeTextLineColor(dsValue))
						else:
							for data in affectList:
								if data[0] != 0 and uitooltip.ItemToolTip.POINT_DICT.has_key(data[0]):
									tooltip.AutoAppendNewTextLineResize(uitooltip.ItemToolTip.POINT_DICT[data[0]](data[1]),0xff95A693)
						
						if self.endTime > 0:# and (self.endTime - app.GetGlobalTimeStamp()) < 2592000:
							tooltip.AppendSpace(5)
							tooltip.AutoAppendNewTextLineResize("%s: %s" % (localeinfo.LEFT_TIME,self.FormatTime(self.endTime - app.GetGlobalTimeStamp())),0xffC5C7C4)
						elif maxDuration > 0 and (maxDuration - app.GetGlobalTimeStamp()) < 2592000:
							tooltip.AppendSpace(5)
							tooltip.AutoAppendNewTextLineResize("%s: %s" % (localeinfo.LEFT_TIME,self.FormatTime(maxDuration - app.GetGlobalTimeStamp())),0xffC5C7C4)
						
						if self.isCanRemove:
							tooltip.AppendSpace(7)
							tooltip.AppendShortcutRow(("key_lclick",), localeinfo.AFFECTSHOWER_REMOVE_TEXT)
					
					tooltip.ShowToolTip()
		else:
			if self.toolTipText:
				self.toolTipText.Show()

	def OnMouseOverOut(self):
		if app.USE_RENEWAL_AFFECT_SHOWER:
			global overInImage
			overInImage = None

		if self.tool_tip:
			self.tool_tip.HideToolTip()

		if app.USE_RENEWAL_AFFECT_SHOWER:
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				if interfaceHandler.tooltipItem:
					interfaceHandler.tooltipItem.HideToolTip()

				if interfaceHandler.tooltipSkill:
					interfaceHandler.tooltipSkill.HideToolTip()
		else:
			if self.toolTipText:
				self.toolTipText.Hide()

# >>> COMBINED BLEND PANEL BEGIN
# The blend-potion / dragon-god affects below used to render one floating icon each.
# They are now collapsed into a single "Dragon God Bonuses" icon (CombinedBlendIcon)
# whose hover opens one combined board (CombinedBlendBoard). Pure client UI - the affects
# themselves are unchanged. Gated by the already-on ENABLE_NEW_BLEND_AFFECT flag.
if app.ENABLE_NEW_BLEND_AFFECT:
	try:
		from _weakref import proxy as _wproxy
	except ImportError:
		def _wproxy(x):
			return x

	def _BlendLocale(key, default):
		# Locale string overrides the English fallback when present (never crashes on a missing key).
		return getattr(localeinfo, key, default)

	# Short per-row titles (fallback). The item's own localized name is preferred at render time.
	COMBINED_BLEND_TITLES = {
		chr.AFFECT_BLEND_POTION_1: _BlendLocale("AFFECT_TITLE_BLEND_POTION_1", "Critical Strike"),
		chr.AFFECT_BLEND_POTION_2: _BlendLocale("AFFECT_TITLE_BLEND_POTION_2", "Piercing Strike"),
		chr.AFFECT_BLEND_POTION_3: _BlendLocale("AFFECT_TITLE_BLEND_POTION_3", "Attack Speed"),
		chr.AFFECT_BLEND_POTION_4: _BlendLocale("AFFECT_TITLE_BLEND_POTION_4", "Magic Resistance"),
		chr.AFFECT_BLEND_POTION_5: _BlendLocale("AFFECT_TITLE_BLEND_POTION_5", "Attack Value"),
		chr.AFFECT_BLEND_POTION_6: _BlendLocale("AFFECT_TITLE_BLEND_POTION_6", "Defence"),
		chr.AFFECT_ENERGY:         _BlendLocale("AFFECT_TITLE_ENERGY", "Energy"),
		chr.AFFECT_DRAGON_GOD_1:   _BlendLocale("AFFECT_TITLE_DRAGON_GOD_1", "Dragon God Life"),
		chr.AFFECT_DRAGON_GOD_2:   _BlendLocale("AFFECT_TITLE_DRAGON_GOD_2", "Dragon God Attack"),
		chr.AFFECT_DRAGON_GOD_3:   _BlendLocale("AFFECT_TITLE_DRAGON_GOD_3", "Dragon God Spirit"),
		chr.AFFECT_DRAGON_GOD_4:   _BlendLocale("AFFECT_TITLE_DRAGON_GOD_4", "Dragon God Defence"),
		chr.AFFECT_CRITICAL:       _BlendLocale("AFFECT_TITLE_CRITICAL", "Critical Strike"),
		chr.AFFECT_PENETRATE:      _BlendLocale("AFFECT_TITLE_PENETRATE", "Piercing Strike"),
	}

	# Item vnum whose icon + (localized) name represent each affect in the panel.
	# Item icons are small and uniform (vs the oversized affectshower images), and the
	# names come pre-localized from item_proto (AE shows Arabic automatically).
	COMBINED_BLEND_ITEM_VNUM = {
		chr.AFFECT_BLEND_POTION_1: 50821,
		chr.AFFECT_BLEND_POTION_2: 50822,
		chr.AFFECT_BLEND_POTION_3: 50823,
		chr.AFFECT_BLEND_POTION_4: 50824,
		chr.AFFECT_BLEND_POTION_5: 50825,
		chr.AFFECT_BLEND_POTION_6: 50826,
		chr.AFFECT_ENERGY:         51002,
		chr.AFFECT_DRAGON_GOD_1:   39017,
		chr.AFFECT_DRAGON_GOD_2:   39018,
		chr.AFFECT_DRAGON_GOD_3:   39019,
		chr.AFFECT_DRAGON_GOD_4:   39020,
		chr.AFFECT_CRITICAL:       71044,
		chr.AFFECT_PENETRATE:      71045,
	}

	COMBINED_BLEND_TIME_LABEL  = _BlendLocale("COMBINED_BLEND_TIME_LABEL", "Time Remaining")

	COMBINED_BLEND_COLOR_TITLE  = 0xffF1E6C0
	COMBINED_BLEND_COLOR_EFFECT = 0xffC1C1C1
	COMBINED_BLEND_COLOR_TIME   = 0xffFFD200

	# Each group = its own collapsed bar icon + its own combined panel (identical layout).
	class _CombinedGroup:
		def __init__(self, key, title, icon, affects, persistent = 0, active_only = ()):
			self.key = key
			self.title = title
			self.icon = icon
			self.affects = affects
			self.persistent = persistent   # 1 = icon shown whenever in a guild + board lists every affect (active/inactive)
			self.active_only = active_only   # affects routed here but shown as a row ONLY while active (e.g. guild name dye)

	COMBINED_GROUPS = [
		_CombinedGroup(
			"dragongod",
			_BlendLocale("COMBINED_BLEND_TITLE", "Dragon God Bonuses"),
			"icon/affectshower/dgod.png",
			(chr.AFFECT_ENERGY,
			 chr.AFFECT_DRAGON_GOD_1, chr.AFFECT_DRAGON_GOD_2, chr.AFFECT_DRAGON_GOD_3, chr.AFFECT_DRAGON_GOD_4,
			 chr.AFFECT_CRITICAL, chr.AFFECT_PENETRATE),
		),
		_CombinedGroup(
			"dew",
			_BlendLocale("DEW_COLLECTION_TITLE", "Dew Collection"),
			"icon/affectshower/blend.png",
			(chr.AFFECT_BLEND_POTION_1, chr.AFFECT_BLEND_POTION_2, chr.AFFECT_BLEND_POTION_3,
			 chr.AFFECT_BLEND_POTION_4, chr.AFFECT_BLEND_POTION_5, chr.AFFECT_BLEND_POTION_6),
		),
	]

	# Guild systems: collapse the guild-skill icons into one group; add the persistent guild-blessing panel.
	GUILD_BLESS_EFFECT_TEXT = {}
	if getattr(app, "GUILD_CONTRACTS_SKILLS", 0):
		_GUILD_SKILL_AFFECTS = (chr.NEW_AFFECT_GUILD_SKILL_MONSTER, chr.NEW_AFFECT_GUILD_SKILL_STONE,
			chr.NEW_AFFECT_GUILD_SKILL_BOSS, chr.NEW_AFFECT_GUILD_SKILL_CRIT,
			chr.NEW_AFFECT_GUILD_SKILL_PIERCE, chr.NEW_AFFECT_GUILD_SKILL_BLESSING)
		_GUILD_SKILL_NAMEKEY = ("NEW_AFFECT_GUILD_SKILL_MONSTER", "NEW_AFFECT_GUILD_SKILL_STONE",
			"NEW_AFFECT_GUILD_SKILL_BOSS", "NEW_AFFECT_GUILD_SKILL_CRIT",
			"NEW_AFFECT_GUILD_SKILL_PIERCE", "NEW_AFFECT_GUILD_SKILL_BLESSING")
		_GUILD_SKILL_NAMEDEF = ("Guild: Strong vs Monsters", "Guild: Strong vs Stones", "Guild: Strong vs Bosses",
			"Guild: Critical", "Guild: Piercing", "Guild Blessing")
		for _bi, _baff in enumerate(_GUILD_SKILL_AFFECTS):
			COMBINED_BLEND_TITLES[_baff] = getattr(localeinfo, _GUILD_SKILL_NAMEKEY[_bi], _GUILD_SKILL_NAMEDEF[_bi])
		COMBINED_GROUPS.append(_CombinedGroup(
			"guildskill",
			_BlendLocale("COMBINED_GUILD_SKILL_TITLE", "Guild Skills"),
			"icon/affectshower/guild_skill_affect.png",
			_GUILD_SKILL_AFFECTS,
		))

	if hasattr(chr, "NEW_AFFECT_GUILD_BLESS_EXP"):
		_GUILD_BLESS_AFFECTS = (chr.NEW_AFFECT_GUILD_BLESS_EXP, chr.NEW_AFFECT_GUILD_BLESS_DROP,
			chr.NEW_AFFECT_GUILD_BLESS_STONE, chr.NEW_AFFECT_GUILD_BLESS_BOSS,
			chr.NEW_AFFECT_GUILD_BLESS_HARVEST, chr.NEW_AFFECT_GUILD_BLESS_GUILDSMAN)
		_GUILD_BLESS_VNUM = (99165, 99166, 99167, 99168, 99169, 99170)
		_GUILD_BLESS_NAMEKEY = ("GUILD_BLESS_NAME_EXP", "GUILD_BLESS_NAME_DROP", "GUILD_BLESS_NAME_STONE",
			"GUILD_BLESS_NAME_BOSS", "GUILD_BLESS_NAME_HARVEST", "GUILD_BLESS_NAME_GUILDSMAN")
		_GUILD_BLESS_NAMEDEF = ("Experience's Blessing", "Treasure's Blessing", "Stonebreaker's Blessing",
			"Slayer's Blessing", "Harvest's Blessing", "Guildsman's Blessing")
		_GUILD_BLESS_EFFKEY = ("GUILD_BLESS_EFF_EXP", "GUILD_BLESS_EFF_DROP", "GUILD_BLESS_EFF_STONE",
			"GUILD_BLESS_EFF_BOSS", "GUILD_BLESS_EFF_HARVEST", "GUILD_BLESS_EFF_GUILDSMAN")
		_GUILD_BLESS_EFFDEF = ("EXP +50%", "Item drop rate +50%", "Metin stone double-loot chance +10%",
			"Boss double-loot chance +10%", "Mining double-ore chance +10%", "Contract reputation +10%")
		for _bi, _baff in enumerate(_GUILD_BLESS_AFFECTS):
			COMBINED_BLEND_ITEM_VNUM[_baff] = _GUILD_BLESS_VNUM[_bi]
			COMBINED_BLEND_TITLES[_baff] = getattr(localeinfo, _GUILD_BLESS_NAMEKEY[_bi], _GUILD_BLESS_NAMEDEF[_bi])
			GUILD_BLESS_EFFECT_TEXT[_baff] = getattr(localeinfo, _GUILD_BLESS_EFFKEY[_bi], _GUILD_BLESS_EFFDEF[_bi])
		COMBINED_GROUPS.append(_CombinedGroup(
			"guildbless",
			_BlendLocale("COMBINED_GUILD_BLESS_TITLE", "Guild Blessings"),
			"icon/affectshower/guild_buffs.png",
			_GUILD_BLESS_AFFECTS,
			1,
		))

	# Guild Name Dye (GUILD_CONTRACTS_DYE): an active-only timer row hosted in the guild-blessings
	# panel when present, else the guild-skills panel (dye requires SKILLS, so one always exists).
	if hasattr(chr, "NEW_AFFECT_GUILD_DYE"):
		_dyeHost = None
		for _grp in COMBINED_GROUPS:
			if _grp.key == "guildbless":
				_dyeHost = _grp
				break
		if _dyeHost is None:
			for _grp in COMBINED_GROUPS:
				if _grp.key == "guildskill":
					_dyeHost = _grp
					break
		if _dyeHost is not None:
			_dyeHost.active_only = tuple(_dyeHost.active_only) + (chr.NEW_AFFECT_GUILD_DYE,)
			COMBINED_BLEND_TITLES[chr.NEW_AFFECT_GUILD_DYE] = getattr(localeinfo, "GUILD_DYE_AFFECT_NAME", "Guild Name Dye")
			GUILD_BLESS_EFFECT_TEXT[chr.NEW_AFFECT_GUILD_DYE] = getattr(localeinfo, "GUILD_DYE_AFFECT_EFF", "Guild name color active")

	# Thief's Gloves combined booster (server grants NEW_AFFECT_LOOT_DROP as its drop component;
	# numeric fallback keeps the pack loadable on a client exe that predates the constant).
	# The drop component renders in the Premium group below, so only stone/dungeon stay here.
	_LOOT_AFFECTS = (getattr(chr, "NEW_AFFECT_LOOT_DROP", 841), chr.NEW_AFFECT_LOOT_STONE, chr.NEW_AFFECT_LOOT_DUNGEON)
	_LOOT_TITLEKEY = ("LOOT_BOOST_NAME_DROP", "LOOT_BOOST_NAME_STONE", "LOOT_BOOST_NAME_DUNGEON")
	_LOOT_TITLEDEF = ("Item Drop Chance", "Metin Stone Loot", "Dungeon & Boss Loot")
	for _bi, _baff in enumerate(_LOOT_AFFECTS):
		COMBINED_BLEND_TITLES[_baff] = getattr(localeinfo, _LOOT_TITLEKEY[_bi], _LOOT_TITLEDEF[_bi])
	COMBINED_GROUPS.append(_CombinedGroup(
		"lootboost",
		_BlendLocale("COMBINED_LOOT_TITLE", "Thief's Gloves"),
		"icon/item/70043.tga",
		_LOOT_AFFECTS[1:],
	))

	# Premium bonuses: mining aura + fishing aura + the drop-chance booster under one bar icon.
	_PREMIUM_AFFECTS = (chr.NEW_AFFECT_MINING_AURA,
		getattr(chr, "NEW_AFFECT_FISHING_AURA", 681),
		getattr(chr, "NEW_AFFECT_LOOT_DROP", 841))
	COMBINED_BLEND_TITLES[chr.NEW_AFFECT_MINING_AURA] = getattr(localeinfo, "TOOLTIP_MINING_AURA_NAME", "Mining Aura")
	COMBINED_BLEND_TITLES[getattr(chr, "NEW_AFFECT_FISHING_AURA", 681)] = getattr(localeinfo, "TOOLTIP_FISHING_AURA_NAME", "Fishing Aura")
	COMBINED_GROUPS.append(_CombinedGroup(
		"premium",
		_BlendLocale("COMBINED_PREMIUM_TITLE", "Premium Bonuses"),
		"icon/affectshower/premium.png",
		_PREMIUM_AFFECTS,
	))

	# affect type -> the group it belongs to (fast lookup for the add/remove interceptions).
	COMBINED_AFFECT_TO_GROUP = {}
	for _grp in COMBINED_GROUPS:
		for _aff in _grp.affects:
			COMBINED_AFFECT_TO_GROUP[_aff] = _grp
		for _aff in getattr(_grp, "active_only", ()):
			COMBINED_AFFECT_TO_GROUP[_aff] = _grp

	class CombinedBlendIcon(ui.ExpandedImageBox):
		def __init__(self, owner, group):
			ui.ExpandedImageBox.__init__(self)
			self.owner = _wproxy(owner)
			self.group = group
			try:
				self.LoadImage(group.icon)
			except:
				pass
			self.SetScale(AFFECT_ICON_SCALE, AFFECT_ICON_SCALE)

		def __del__(self):
			ui.ExpandedImageBox.__del__(self)

		def OnMouseOverIn(self):
			if self.owner:
				self.owner.ShowCombinedBlendBoard(self.group)

		def OnMouseOverOut(self):
			if self.owner:
				self.owner.HideCombinedBlendBoard(self.group)

	# Reuses the standard affect-tooltip widget (uitooltip.ToolTip == ui.ThinBoard background,
	# TOP_MOST + not_pick) so the panel looks like every other affect tooltip. Layout is manual
	# (icon + 3 text lines per row) via a fixed pool of row slots; follow-mouse is disabled so
	# the panel stays anchored under the collapsed icon.
	class CombinedBlendBoard(uitooltip.ToolTip):
		MIN_WIDTH = 180
		PAD = 12
		TITLE_H = 28
		ROW_H = 58             # per-item row height - extra gap between items for readability
		ICON_X = 10
		ICON_FALLBACK = 32     # assumed icon size when the width cannot be measured
		ICON_MAX = 32          # row icons clamp to standard item-icon size (large affect art scales down)
		TEXT_GAP = 10
		LINE_SPACING = 16      # vertical gap between the 3 text lines inside one row
		TEXT_BLOCK_H = 45      # height of the 3-line text block (used to vertically center the icon)

		def __init__(self, title, rowCount):
			uitooltip.ToolTip.__init__(self, self.MIN_WIDTH)
			self.SetFollow(False)

			titleLine = ui.TextLine()
			titleLine.SetParent(self)
			titleLine.SetWindowHorizontalAlignCenter()
			titleLine.SetHorizontalAlignCenter()
			titleLine.SetPosition(0, 8)
			titleLine.SetPackedFontColor(COMBINED_BLEND_COLOR_TITLE)
			titleLine.SetText(title)
			titleLine.SetOutline()
			titleLine.Show()
			self.titleLine = titleLine

			self.rowSlots = []
			for i in xrange(rowCount):
				self.rowSlots.append(self.__MakeRowSlot())

			self.activeRows = []

		def __del__(self):
			uitooltip.ToolTip.__del__(self)

		def __MakeRowSlot(self):
			icon = ui.ExpandedImageBox()
			icon.SetParent(self)
			icon.AddFlag("not_pick")
			icon.Hide()

			titleLine = ui.TextLine()
			titleLine.SetParent(self)
			titleLine.SetPackedFontColor(COMBINED_BLEND_COLOR_TITLE)
			titleLine.SetOutline()
			titleLine.Hide()

			effectLine = ui.TextLine()
			effectLine.SetParent(self)
			effectLine.SetPackedFontColor(COMBINED_BLEND_COLOR_EFFECT)
			effectLine.SetOutline()
			effectLine.Hide()

			timeLine = ui.TextLine()
			timeLine.SetParent(self)
			timeLine.SetPackedFontColor(COMBINED_BLEND_COLOR_TIME)
			timeLine.SetOutline()
			timeLine.Hide()

			# Arabic is RTL: anchor text on the right edge with align-left so glyphs flow left.
			for line in (titleLine, effectLine, timeLine):
				line.SetHorizontalAlignLeft()

			return {"icon": icon, "title": titleLine, "effect": effectLine, "time": timeLine}

		def Refresh(self, rows):
			self.activeRows = rows
			count = len(rows)

			# Pass 1: fill texts + icons at NATIVE size, measure widest icon + text.
			maxTextW = 0
			maxIconW = 0
			for i in xrange(count):
				slot = self.rowSlots[i]
				row = rows[i]

				try:
					slot["icon"].LoadImage(row["icon"])
					slot["icon"].SetScale(1.0, 1.0)
				except:
					pass

				iw = slot["icon"].GetWidth()
				ih = slot["icon"].GetHeight()
				if iw > self.ICON_MAX or ih > self.ICON_MAX:
					iconScale = min(float(self.ICON_MAX) / max(1, iw), float(self.ICON_MAX) / max(1, ih))
					slot["icon"].SetScale(iconScale, iconScale)
					iw = int(iw * iconScale)
					slot["scaledH"] = int(ih * iconScale)
				else:
					slot["scaledH"] = ih
				if iw > maxIconW:
					maxIconW = iw

				slot["title"].SetText(row["title"])
				slot["effect"].SetText(row["effect"])
				slot["time"].SetText(row.get("timeText") or self.__FormatTimeText(row["endTime"]))

				for key in ("title", "effect", "time"):
					tw = slot[key].GetTextWidth()
					if tw > maxTextW:
						maxTextW = tw

			if maxIconW <= 0:
				maxIconW = self.ICON_FALLBACK

			width = self.ICON_X + maxIconW + self.TEXT_GAP + maxTextW + 14
			titleW = self.titleLine.GetTextWidth() + 24
			if titleW > width:
				width = titleW
			if width < self.MIN_WIDTH:
				width = self.MIN_WIDTH

			if localeinfo.IsARABIC():
				iconX = width - self.ICON_X - maxIconW
				textX = iconX - self.TEXT_GAP
			else:
				iconX = self.ICON_X
				textX = self.ICON_X + maxIconW + self.TEXT_GAP

			# Pass 2: position the visible rows, hide the rest.
			for i, slot in enumerate(self.rowSlots):
				if i < count:
					y = self.TITLE_H + i * self.ROW_H
					ih = slot.get("scaledH", slot["icon"].GetHeight())
					slot["icon"].SetPosition(iconX, y + max(0, (self.TEXT_BLOCK_H - ih) // 2))
					slot["icon"].Show()

					slot["title"].SetPosition(textX, y)
					slot["title"].Show()
					slot["effect"].SetPosition(textX, y + self.LINE_SPACING)
					slot["effect"].Show()
					slot["time"].SetPosition(textX, y + 2 * self.LINE_SPACING)
					slot["time"].Show()
				else:
					slot["icon"].Hide()
					slot["title"].Hide()
					slot["effect"].Hide()
					slot["time"].Hide()

			height = self.TITLE_H + max(1, count) * self.ROW_H + self.PAD
			self.SetSize(width, height)
			self.titleLine.UpdateRect()

		def UpdateTimes(self):
			for i, row in enumerate(self.activeRows):
				if i < len(self.rowSlots):
					self.rowSlots[i]["time"].SetText(row.get("timeText") or self.__FormatTimeText(row["endTime"]))

		def __FormatTimeText(self, endTime):
			if endTime <= 0:
				return ""
			remain = endTime - app.GetGlobalTimeStamp()
			if remain < 0:
				remain = 0
			return "%s: %s" % (COMBINED_BLEND_TIME_LABEL, localeinfo.SecondToDHM(remain))

	# >>> PET SKILL PANEL BEGIN
	# The growth-pet skill affects used to render one floating icon per skill (up to 6
	# under the skill rework). They now collapse into ONE "Pet Skills" bar icon whose
	# hover board lists each active skill with its own SKILL icon, name and the CURRENT
	# granted value (read live from GetPetSkillByIndex on every refresh). Pet skill
	# affects have no duration, so the board deliberately has no timer line.
	PET_SKILL_PANEL_TITLE = _BlendLocale("COMBINED_PET_SKILL_TITLE", "Pet Skills")

	class PetSkillPanelIcon(ui.ExpandedImageBox):
		def __init__(self, owner):
			ui.ExpandedImageBox.__init__(self)
			self.owner = _wproxy(owner)
			self.iconLoaded = 0   # retried on every add until an image actually loads

		def __del__(self):
			ui.ExpandedImageBox.__del__(self)

		def RefreshIcon(self, iconPath):
			# Bar icon = the first active skill's own icon (native pet-skill art at the
			# shared affect-bar scale the retired per-skill icons used) -- no bespoke art needed.
			# A zero-size imageless box can never receive OnMouseOverIn, so the caller
			# keeps retrying (with later skills' paths) until one load succeeds.
			if not iconPath:
				return
			try:
				self.LoadImage(iconPath)
				self.SetScale(AFFECT_ICON_SCALE, AFFECT_ICON_SCALE)
				self.iconLoaded = 1
			except:
				pass

		def OnMouseOverIn(self):
			if self.owner:
				self.owner.ShowPetSkillBoard()

		def OnMouseOverOut(self):
			if self.owner:
				self.owner.HidePetSkillBoard()

	class PetSkillPanelBoard(CombinedBlendBoard):
		# 2-line rows (name + granted value). The inherited third "time" line is fed
		# endTime=0 rows, so it always renders empty; the row metrics shrink to match.
		ROW_H = 42
		TEXT_BLOCK_H = 30
	# <<< PET SKILL PANEL END

	# >>> FISH GROUP PANEL: one board row per active fish buff, each with its own timer.
	# Registered AFTER the COMBINED_AFFECT_TO_GROUP build on purpose - fish routes through
	# its own per-point add/remove path, not the per-type blend interception.
	class FishPanelBoard(CombinedBlendBoard):
		# 2-line rows: bonus text + its own time line (the middle "effect" line is fed "").
		ROW_H = 42
		TEXT_BLOCK_H = 30
		LINE_SPACING = 8

	FISH_PANEL_GROUP = _CombinedGroup(
		"fish",
		_BlendLocale("TOOLTIP_NEW_AFFECT_FISHES", "Fish Bonuses"),
		"icon/affectshower/fish2.png",
		(),
	)
	COMBINED_GROUPS.append(FISH_PANEL_GROUP)

	# point type -> granting fish vnum, read from the client item proto (value0 apply -> point).
	# Built on first board render so the proto is guaranteed loaded.
	FISH_POINT_ITEM_CACHE = {"built": 0, "timed": {}, "perma": {}}

	def _BuildFishPointItems():
		cache = FISH_POINT_ITEM_CACHE
		if cache["built"]:
			return cache
		for first, key in ((27863, "timed"), (37863, "perma")):
			table = cache[key]
			for vnum in xrange(first, first + 30):
				try:
					item.SelectItem(vnum)
					applyType = item.GetValue(0)
					if not applyType:
						continue
					point = item.GetApplyPoint(applyType)
				except:
					continue
				if point and not table.has_key(point):
					table[point] = vnum
		cache["built"] = 1
		return cache

	def _FishRowIcon(vnum):
		if not vnum:
			return ""
		try:
			item.SelectItem(vnum)
			path = item.GetIconImageFileName()
			if path and path.find("gr2") == -1:
				return path
		except:
			pass
		return ""
	# <<< FISH GROUP PANEL
# <<< COMBINED BLEND PANEL END

class AffectShower(ui.Window):


	MALL_DESC_IDX_START=1000

	IMAGE_STEP = 29

	if app.USE_PERSO_SIZE_ON_AFFECT_SHOWER:
		MAX_IMAGE_X_LINE = 10
		IMG_EXPAND_PATH = "d:/ymir work/ui/"
		IMG_EXPAND_DOWN = "d:/ymir work/ui/affect_expand_down.png"
		IMG_EXPAND_DOWN_HOVER = "d:/ymir work/ui/affect_expand_up_hover.png"
		IMG_EXPAND_DOWN_DOWN = "d:/ymir work/ui/affect_expand_up_down.png"
		
		IMG_EXPAND_UP = "d:/ymir work/ui/affect_expand_up.png"
		IMG_EXPAND_UP_HOVER = "d:/ymir work/ui/affect_expand_down_hover.png"
		IMG_EXPAND_UP_DOWN = "d:/ymir work/ui/affect_expand_down_down.png"

	AFFECT_MAX_NUM=32
	INFINITE_AFFECT_DURATION=0x1FFFFFFF
	AFFECT_DATA_DICT={\
		chr.AFFECT_POISON:(localeinfo.SKILL_TOXICDIE,"d:/ymir work/ui/skill/common/affect/poison.sub", 4, 0),
		chr.AFFECT_BLEEDING:(localeinfo.SKILL_BLEEDING,"d:/ymir work/ui/skill/common/affect/poison.sub", 4, 0),
		chr.AFFECT_SLOW:(localeinfo.SKILL_SLOW,"icon/affectshower/slow.tga"),
		chr.AFFECT_STUN:(localeinfo.SKILL_STUN,"icon/affectshower/stun.tga"),
		#
		chr.AFFECT_ATT_SPEED_POTION:(localeinfo.SKILL_INC_ATKSPD,"d:/ymir work/ui/skill/common/affect/Increase_Attack_Speed.sub", 3, 0),
		chr.AFFECT_MOV_SPEED_POTION:(localeinfo.SKILL_INC_MOVSPD,"d:/ymir work/ui/skill/common/affect/Increase_Move_Speed.sub", 3, 0),
		chr.AFFECT_FISH_MIND:(localeinfo.SKILL_FISHMIND,"d:/ymir work/ui/skill/common/affect/fishmind.sub", 3, 0),
		#
		chr.AFFECT_JEONGWI:(localeinfo.SKILL_JEONGWI,"d:/ymir work/ui/skill/warrior/jeongwi_03.sub", 2, 0),
		chr.AFFECT_GEOMGYEONG:(localeinfo.SKILL_GEOMGYEONG,"d:/ymir work/ui/skill/warrior/geomgyeong_03.sub", 2, 0),
		chr.AFFECT_CHEONGEUN:(localeinfo.SKILL_CHEONGEUN,"d:/ymir work/ui/skill/warrior/cheongeun_03.sub", 2, 0),
		chr.AFFECT_GYEONGGONG:(localeinfo.SKILL_GYEONGGONG,"d:/ymir work/ui/skill/assassin/gyeonggong_03.sub", 2, 0),
		chr.AFFECT_EUNHYEONG:(localeinfo.SKILL_EUNHYEONG,"d:/ymir work/ui/skill/assassin/eunhyeong_03.sub", 2, 0),
		chr.AFFECT_GWIGEOM:(localeinfo.SKILL_GWIGEOM,"d:/ymir work/ui/skill/sura/gwigeom_03.sub", 2, 0),
		chr.AFFECT_GONGPO:(localeinfo.SKILL_GONGPO,"d:/ymir work/ui/skill/sura/gongpo_03.sub", 2, 0),
		chr.AFFECT_JUMAGAP:(localeinfo.SKILL_JUMAGAP,"d:/ymir work/ui/skill/sura/jumagap_03.sub", 2, 0),
		chr.AFFECT_HOSIN:(localeinfo.SKILL_HOSIN,"d:/ymir work/ui/skill/shaman/hosin_03.sub", 2, 0),
		chr.AFFECT_BOHO:(localeinfo.SKILL_BOHO,"d:/ymir work/ui/skill/shaman/boho_03.sub", 2, 0),
		chr.AFFECT_KWAESOK:(localeinfo.SKILL_KWAESOK,"d:/ymir work/ui/skill/shaman/kwaesok_03.sub", 2, 0),
		chr.AFFECT_HEUKSIN:(localeinfo.SKILL_HEUKSIN,"d:/ymir work/ui/skill/sura/heuksin_03.sub", 2, 0),
		chr.AFFECT_MUYEONG:(localeinfo.SKILL_MUYEONG,"d:/ymir work/ui/skill/sura/muyeong_03.sub", 2, 0),
		chr.AFFECT_GICHEON:(localeinfo.SKILL_GICHEON,"d:/ymir work/ui/skill/shaman/gicheon_03.sub", 2, 0),
		chr.AFFECT_JEUNGRYEOK:(localeinfo.SKILL_JEUNGRYEOK,"d:/ymir work/ui/skill/shaman/jeungryeok_03.sub", 2, 0),
		chr.AFFECT_PABEOP:(localeinfo.SKILL_PABEOP,"d:/ymir work/ui/skill/sura/pabeop_03.sub", 2, 0),
		chr.AFFECT_FALLEN_CHEONGEUN:(localeinfo.SKILL_CHEONGEUN,"d:/ymir work/ui/skill/warrior/cheongeun_03.sub", 2, 0),
		28:(localeinfo.SKILL_FIRE,"d:/ymir work/ui/skill/sura/hwayeom_03.sub", 2, 0),
		chr.AFFECT_CHINA_FIREWORK:(localeinfo.SKILL_POWERFUL_STRIKE,"d:/ymir work/ui/skill/common/affect/powerfulstrike.sub", 2, 0),
		chr.AFFECT_RED_POSSESSION:(localeinfo.SKILL_GWIGEOM,"d:/ymir work/ui/skill/wolfman/red_possession_03.sub", 2, 0),
		chr.AFFECT_BLUE_POSSESSION:(localeinfo.SKILL_CHEONGEUN,"d:/ymir work/ui/skill/wolfman/blue_possession_03.sub", 2, 0),
		#
		chr.NEW_AFFECT_EXP_BONUS:(localeinfo.TOOLTIP_MALL_EXPBONUS_STATIC,"d:/ymir work/ui/skill/common/affect/exp_bonus.sub", 3, 0),
		#chr.NEW_AFFECT_ITEM_BONUS:(localeinfo.TOOLTIP_MALL_ITEMBONUS_STATIC,"d:/ymir work/ui/skill/common/affect/item_bonus.sub", 3, 0),
		#chr.NEW_AFFECT_SAFEBOX:(localeinfo.TOOLTIP_MALL_SAFEBOX,"d:/ymir work/ui/skill/common/affect/safebox.sub", 3, 0),
		#chr.NEW_AFFECT_AUTOLOOT:(localeinfo.TOOLTIP_MALL_AUTOLOOT,"d:/ymir work/ui/skill/common/affect/autoloot.sub", 3, 0),
		chr.NEW_AFFECT_FISH_MIND:(localeinfo.TOOLTIP_MALL_FISH_MIND,"icon/affectshower/27610.tga"),
		chr.NEW_AFFECT_MARRIAGE_FAST:(localeinfo.TOOLTIP_MALL_MARRIAGE_FAST,"d:/ymir work/ui/skill/common/affect/marriage_fast.sub", 3, 0),
		chr.NEW_AFFECT_GOLD_BONUS:(localeinfo.TOOLTIP_MALL_GOLDBONUS_STATIC,"d:/ymir work/ui/skill/common/affect/gold_bonus.sub", 3, 0),
		chr.NEW_AFFECT_NO_DEATH_PENALTY:(localeinfo.TOOLTIP_APPLY_NO_DEATH_PENALTY,"d:/ymir work/ui/skill/common/affect/gold_premium.sub", 3, 0),
		chr.NEW_AFFECT_SKILL_BOOK_BONUS:(localeinfo.TOOLTIP_APPLY_SKILL_BOOK_BONUS,"icon/affectshower/book_bonus.tga"),
		chr.NEW_AFFECT_SKILL_BOOK_NO_DELAY:(localeinfo.TOOLTIP_APPLY_SKILL_BOOK_NO_DELAY,"icon/affectshower/book_no_delay.tga"),
		chr.NEW_AFFECT_AUTO_HP_RECOVERY:(localeinfo.TOOLTIP_AUTO_POTION_REST,"icon/affectshower/72725.tga"),
		chr.NEW_AFFECT_AUTO_SP_RECOVERY:(localeinfo.TOOLTIP_AUTO_POTION_REST,"icon/affectshower/72729.tga"),

		434:(localeinfo.SKLL_COLOR,"d:/ymir work/ui/pattern/auto_spgauge/05.dds", 3, 2), # skill color

		MALL_DESC_IDX_START + player.ATT_BONUS:(localeinfo.TOOLTIP_MALL_ATTBONUS_STATIC,"d:/ymir work/ui/skill/common/affect/att_bonus.sub", 3, 0),
		MALL_DESC_IDX_START + player.DEF_BONUS:(localeinfo.TOOLTIP_MALL_DEFBONUS_STATIC,"d:/ymir work/ui/skill/common/affect/def_bonus.sub", 3, 0),
		MALL_DESC_IDX_START + player.POINT_MALL_ATTBONUS:(localeinfo.TOOLTIP_MALL_ATTBONUS_STATIC,"d:/ymir work/ui/skill/common/affect/att_bonus.sub", 3, 0),
		MALL_DESC_IDX_START + player.POINT_MALL_DEFBONUS:(localeinfo.TOOLTIP_MALL_DEFBONUS_STATIC,"d:/ymir work/ui/skill/common/affect/def_bonus.sub", 3, 0),
		MALL_DESC_IDX_START + player.POINT_MALL_EXPBONUS:(localeinfo.TOOLTIP_MALL_EXPBONUS,"icon/affectshower/exp.tga"),
		MALL_DESC_IDX_START + player.POINT_MALL_ITEMBONUS:(localeinfo.TOOLTIP_MALL_ITEMBONUS,"d:/ymir work/ui/skill/common/affect/item_bonus.sub", 3, 0),
		MALL_DESC_IDX_START + player.POINT_MALL_GOLDBONUS:(localeinfo.TOOLTIP_MALL_GOLDBONUS,"d:/ymir work/ui/skill/common/affect/gold_bonus.sub", 3, 0),
		MALL_DESC_IDX_START + player.POINT_CRITICAL_PCT:(localeinfo.TOOLTIP_APPLY_CRITICAL_PCT,"d:/ymir work/ui/skill/common/affect/critical.sub", 3, 0),
		MALL_DESC_IDX_START + player.POINT_PENETRATE_PCT:(localeinfo.TOOLTIP_APPLY_PENETRATE_PCT,"d:/ymir work/ui/skill/common/affect/gold_premium.sub", 3, 0),
		MALL_DESC_IDX_START + player.POINT_MAX_HP_PCT:(localeinfo.TOOLTIP_MAX_HP_PCT,"d:/ymir work/ui/skill/common/affect/gold_premium.sub", 3, 0),
		MALL_DESC_IDX_START + player.POINT_MAX_SP_PCT:(localeinfo.TOOLTIP_MAX_SP_PCT,"d:/ymir work/ui/skill/common/affect/gold_premium.sub", 3, 0),
		MALL_DESC_IDX_START + player.POINT_PC_BANG_EXP_BONUS:(localeinfo.TOOLTIP_MALL_EXPBONUS_P_STATIC,"d:/ymir work/ui/skill/common/affect/EXP_Bonus_p_on.sub", 3, 0),
		MALL_DESC_IDX_START + player.POINT_PC_BANG_DROP_BONUS: (localeinfo.TOOLTIP_MALL_ITEMBONUS_P_STATIC,"d:/ymir work/ui/skill/common/affect/Item_Bonus_p_on.sub", 3, 0),
		#MALL_DESC_IDX_START + player.POINT_MELEE_MAGIC_ATT_BONUS_PER:(localeinfo.TOOLTIP_MALL_ATTBONUS_STATIC,"d:/ymir work/ui/skill/common/affect/att_bonus.sub", 3, 0),
	}

	#if app.ENABLE_PREMIUM_FEATURES_ACCOUNT:
	#	AFFECT_DATA_DICT[chr.NEW_AFFECT_PREMIUM_ACCOUNT]=(localeinfo.NEW_AFFECT_PREMIUM_ACCOUNT,"d:/ymir work/ui/game/affect/premium_account.tga", 3, 0)

	#if app.ENABLE_PREMIUM_FEATURES_PLAYER:
	#	AFFECT_DATA_DICT[chr.NEW_AFFECT_PREMIUM_PLAYER]=(localeinfo.NEW_AFFECT_PREMIUM_PLAYER,"d:/ymir work/ui/game/affect/premium_player.tga", 3, 0)

	if app.ENABLE_DRAGON_SOUL_SYSTEM:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_DRAGON_SOUL_DECK1]=(localeinfo.TOOLTIP_DRAGON_SOUL_DECK1,"icon/affectshower/dragon1_affect.png")
		AFFECT_DATA_DICT[chr.NEW_AFFECT_DRAGON_SOUL_DECK2]=(localeinfo.TOOLTIP_DRAGON_SOUL_DECK2,"icon/affectshower/dragon2_affect.png")

	if app.ENABLE_DS_SET:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_DS_SET]=(localeinfo.TOOLTIP_DS_SET,"icon/affectshower/dsslot_affect.png")

	AFFECT_DATA_DICT[chr.NEW_AFFECT_COLLECT]=(localeinfo.TOOLTIP_AFFECT_BIO_EFFECTS,"icon/affectshower/bio_effects.tga")
	AFFECT_DATA_DICT[chr.AFFECT_RESEARCHER_ELIXIR]=(localeinfo.TOOLTIP_AFFECT_RESEARCHER_ELIXIR,"d:/ymir work/ui/skill/common/affect/researcher_elixir.sub")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_SAFE_BOX_BUFF]=(localeinfo.TOOLTIP_AFFECT_SAFEBOX_BUFF_01,"d:/ymir work/ui/skill/common/affect/safebox_buff.sub")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_FISHES]=(localeinfo.TOOLTIP_NEW_AFFECT_FISHES,"icon/affectshower/fish.png")
	AFFECT_DATA_DICT[getattr(chr, "NEW_AFFECT_FISHING_AURA", 681)]=(getattr(localeinfo, "TOOLTIP_FISHING_AURA_DESC", "Fishing success rate  +20%"),"icon/affectshower/fish2.png")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_MINING_AURA]=(localeinfo.TOOLTIP_MINING_AURA_DESC,"icon/affectshower/herbo_skill.png")

	if app.ENABLE_NEW_BLEND_AFFECT:
		AFFECT_DATA_DICT[chr.AFFECT_BLEND_POTION_1]=(localeinfo.TOOLTIP_AFFECT_BLEND_POTION_1,"icon/affectshower/50821.tga")
		AFFECT_DATA_DICT[chr.AFFECT_BLEND_POTION_2]=(localeinfo.TOOLTIP_AFFECT_BLEND_POTION_2,"icon/affectshower/50822.tga")
		AFFECT_DATA_DICT[chr.AFFECT_BLEND_POTION_3]=(localeinfo.TOOLTIP_AFFECT_BLEND_POTION_3,"icon/affectshower/50823.tga")
		AFFECT_DATA_DICT[chr.AFFECT_BLEND_POTION_4]=(localeinfo.TOOLTIP_AFFECT_BLEND_POTION_4,"icon/affectshower/50824.tga")
		AFFECT_DATA_DICT[chr.AFFECT_BLEND_POTION_5]=(localeinfo.TOOLTIP_AFFECT_BLEND_POTION_5,"icon/affectshower/50825.tga")
		AFFECT_DATA_DICT[chr.AFFECT_BLEND_POTION_6]=(localeinfo.TOOLTIP_AFFECT_BLEND_POTION_6,"icon/affectshower/50826.tga")
		AFFECT_DATA_DICT[chr.AFFECT_ENERGY]=(localeinfo.TOOLTIP_AFFECT_ENERGY,"icon/affectshower/51002.tga")
		AFFECT_DATA_DICT[chr.AFFECT_DRAGON_GOD_1]=(localeinfo.TOOLTIP_AFFECT_DRAGON_GOD_1,"icon/affectshower/71027.tga")
		AFFECT_DATA_DICT[chr.AFFECT_DRAGON_GOD_2]=(localeinfo.TOOLTIP_AFFECT_DRAGON_GOD_2,"icon/affectshower/71028.tga")
		AFFECT_DATA_DICT[chr.AFFECT_DRAGON_GOD_3]=(localeinfo.TOOLTIP_AFFECT_DRAGON_GOD_3,"icon/affectshower/71029.tga")
		AFFECT_DATA_DICT[chr.AFFECT_DRAGON_GOD_4]=(localeinfo.TOOLTIP_AFFECT_DRAGON_GOD_4,"icon/affectshower/71030.tga")
		AFFECT_DATA_DICT[chr.AFFECT_CRITICAL]=(localeinfo.TOOLTIP_AFFECT_CRITICAL,"icon/affectshower/71044.tga")
		AFFECT_DATA_DICT[chr.AFFECT_PENETRATE]=(localeinfo.TOOLTIP_AFFECT_PENETRATE,"icon/affectshower/71045.tga")
		AFFECT_DATA_DICT[chr.AFFECT_ATTACK_SPEED]=(localeinfo.TOOLTIP_AFFECT_ATTACK_SPEED,"icon/affectshower/27209.tga")
		AFFECT_DATA_DICT[chr.AFFECT_MOVE_SPEED]=(localeinfo.TOOLTIP_AFFECT_MOVE_SPEED,"icon/affectshower/27212.tga")
		AFFECT_DATA_DICT[chr.AFFECT_BLEND_POTION_7]=(localeinfo.TOOLTIP_AFFECT_BLEND_POTION_7,"icon/affectshower/50830.tga")
		AFFECT_DATA_DICT[chr.AFFECT_BLEND_POTION_8]=(localeinfo.TOOLTIP_AFFECT_BLEND_POTION_8,"icon/affectshower/50832.tga")
		AFFECT_DATA_DICT[chr.AFFECT_BLEND_POTION_9]=(localeinfo.TOOLTIP_AFFECT_BLEND_POTION_9,"icon/affectshower/50831.tga")

	if app.ENABLE_12ZI:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_CZ_UNLIMIT_ENTER]=(localeinfo.TOOLTIP_AFFECT_CZ_UNLIMIT_ENTER, "d:/ymir work/ui/skill/common/affect/cz_unlimit_enter.sub", 3, 0)

	if app.USE_PREMIUM_FEATURES:
		AFFECT_DATA_DICT[chr.AFFECT_PREMIUM_NORMAL]=(localeinfo.TOOLTIP_AFFECT_PREMIUM_NORMAL,"icon/affectshower/premium_norm.tga")
		AFFECT_DATA_DICT[chr.AFFECT_PREMIUM_PLUS]=(localeinfo.TOOLTIP_AFFECT_PREMIUM_PLUS,"icon/affectshower/premium_plus.tga")

	if app.RENEWAL_PICKUP_AFFECT:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_PICKUP_ENABLE]=(localeinfo.NEW_AFFECT_PICKUP_ENABLE,"icon/affectshower/auto_pickup.tga")
		AFFECT_DATA_DICT[chr.NEW_AFFECT_PICKUP_DEACTIVE]=(localeinfo.NEW_AFFECT_PICKUP_DEACTIVE,"icon/affectshower/auto_pickup_off.tga")

	AFFECT_DATA_DICT[getattr(chr, "NEW_AFFECT_DOUBLE_RUN", 842)] = (getattr(localeinfo, "DOUBLE_RUN_ON", "Double Run (active)"), "icon/affectshower/dungeon_double.png")
	AFFECT_DATA_DICT[getattr(chr, "NEW_AFFECT_DOUBLE_RUN_OFF", 843)] = (getattr(localeinfo, "DOUBLE_RUN_OFF", "Double Run (paused)"), "icon/affectshower/dungeon_double_off.png")

	if app.__SKILL_TREE__:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_SKILL_TREE] = (localeinfo.NEW_AFFECT_SKILL_TREE, "icon/affectshower/skill_tree.tga", 3, 0)

	if app.__RENEWAL_BRAVE_CAPE__:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_BRAVE_CAPE] = (localeinfo.NEW_AFFECT_BRAVE_CAPE, "icon/affectshower/cape.tga")

	if app.ENABLE_PARTY_BOUNS:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_PARTY_BONUS]=(localeinfo.NEW_AFFECT_PARTY_BONUS,"icon/affectshower/bio_affect.tga")

	if app.AUTO_HUNT_RUBINUM:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_RUBI_HUNT]=(localeinfo.NEW_AFFECT_RUBI_HUNT,"icon/affectshower/stone_hunt.tga")

	if getattr(app, "GUILD_CONTRACTS_SKILLS", 0):
		# guild-skill affect icons: d:/ymir work/ui/new_guild/skills (32x32 png)
		AFFECT_DATA_DICT[chr.NEW_AFFECT_GUILD_SKILL_MONSTER]=(getattr(localeinfo, "NEW_AFFECT_GUILD_SKILL_MONSTER", "Guild: Strong vs Monsters"),"d:/ymir work/ui/new_guild/skills/skill_attack_force_buff.png")
		AFFECT_DATA_DICT[chr.NEW_AFFECT_GUILD_SKILL_STONE]=(getattr(localeinfo, "NEW_AFFECT_GUILD_SKILL_STONE", "Guild: Strong vs Stones"),"d:/ymir work/ui/new_guild/skills/sungmahee_tower_buff.png")
		AFFECT_DATA_DICT[chr.NEW_AFFECT_GUILD_SKILL_BOSS]=(getattr(localeinfo, "NEW_AFFECT_GUILD_SKILL_BOSS", "Guild: Strong vs Bosses"),"d:/ymir work/ui/new_guild/skills/iron_dragon_bless_buff.png")
		AFFECT_DATA_DICT[chr.NEW_AFFECT_GUILD_SKILL_CRIT]=(getattr(localeinfo, "NEW_AFFECT_GUILD_SKILL_CRIT", "Guild: Critical"),"d:/ymir work/ui/new_guild/skills/mount_upgrade_skill_random_strong.png")
		AFFECT_DATA_DICT[chr.NEW_AFFECT_GUILD_SKILL_PIERCE]=(getattr(localeinfo, "NEW_AFFECT_GUILD_SKILL_PIERCE", "Guild: Piercing"),"d:/ymir work/ui/new_guild/skills/has_poisoned.png")
		AFFECT_DATA_DICT[chr.NEW_AFFECT_GUILD_SKILL_BLESSING]=(getattr(localeinfo, "NEW_AFFECT_GUILD_SKILL_BLESSING", "Guild Blessing"),"d:/ymir work/ui/new_guild/skills/white_dragon_bless_buff.png")

	if hasattr(chr, "NEW_AFFECT_GUILD_DYE"):
		# icon-only entry: empty name keeps __FormatBlendEffect from overriding the dye effect text.
		AFFECT_DATA_DICT[chr.NEW_AFFECT_GUILD_DYE] = ("", "icon/affectshower/guild_buffs.png")

	if app.ENABLE_CONQUEROR_LEVEL:
		AFFECT_DATA_DICT[chr.AFFECT_CHEONUN] = (localeinfo.TOOLTIP_AFFECT_CHEONUN, "d:/ymir work/ui/skill/shaman/cheonun_03.sub")

	if app.USE_QUEST_PET_NAME:
		AFFECT_DATA_DICT[chr.AFFECT_PETNAME] = (localeinfo.AFFECT_PETNAME_TOOLTIP, "icon/affectshower/pet_name.tga")

	if app.USE_QUEST_MOUNT_NAME:
		AFFECT_DATA_DICT[chr.AFFECT_MOUNTNAME] = (localeinfo.AFFECT_MOUNTNAME_TOOLTIP, "icon/affectshower/mount_name.tga")

	AFFECT_DATA_DICT[chr.NEW_AFFECT_PET_EXP] = (localeinfo.AFFECT_PET_EXP_TOOLTIP, "icon/affectshower/99102.tga")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_MOONLIGHT_BUFF] = (localeinfo.AFFECT_MOONLIGHT_BUFF_TOOLTIP, "icon/affectshower/99100.tga")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_BIO_BUFF] = (localeinfo.AFFECT_BIO_BUFF_TOOLTIP, "icon/affectshower/99101.tga")

	if app.ENABLE_MULTIFARM_BLOCK:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_MULTI_FARM] = (localeinfo.MULTI_FARM_PREMIUM_EFFECT, "icon/affectshower/farmeron.png")

	AFFECT_DATA_DICT[chr.NEW_AFFECT_DAILY_BUFF] = (localeinfo.AFFECT_DAILY_BUFF_TOOLTIP, "icon/affectshower/daily.tga")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_LOOT_STONE] = (localeinfo.AFFECT_LOOT_STONE_TOOLTIP, "icon/affectshower/stone_loot.tga")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_LOOT_DUNGEON] = (localeinfo.AFFECT_LOOT_DUNGEON_TOOLTIP, "icon/affectshower/dungeon_loot.tga")
	AFFECT_DATA_DICT[getattr(chr, "NEW_AFFECT_LOOT_DROP", 841)] = (getattr(localeinfo, "COMBINED_LOOT_TT_DROP", "+50% item drop chance"), "d:/ymir work/ui/skill/common/affect/item_bonus.sub", 3, 0)

	if app.ENABLE_SOLO_LEADERSHIP_BONUS:
		# Solo leadership role bonus (server affect 901, infinite). The role name and its
		# value are pushed separately as constinfo.SOLO_LEADERSHIP_*, so the tooltip branch
		# in OnMouseOverIn reads them from there instead of the affect's point list.
		AFFECT_DATA_DICT[getattr(chr, "NEW_AFFECT_SOLO_LEADERSHIP", 901)] = (localeinfo.SOLO_LEADERSHIP_TITLE, "icon/affectshower/commandement_affect.png")

	if app.__RANKING_SYSTEM__:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_RANK] = (localeinfo.NEW_AFFECT_RANK, "icon/affectshower/rank.tga")
		AFFECT_DATA_DICT[chr.NEW_AFFECT_RANK_GUILD] = (localeinfo.NEW_AFFECT_RANK_GUILD, "icon/affectshower/rank.tga")
		AFFECT_DATA_DICT[chr.NEW_AFFECT_RANK_WEEKLY] =  (localeinfo.NEW_AFFECT_RANK, "icon/affectshower/rank.tga")
		AFFECT_DATA_DICT[chr.NEW_AFFECT_RANK_GUILD_WEEKLY] =  (localeinfo.NEW_AFFECT_RANK_GUILD, "icon/affectshower/rank.tga")

	if app.ENABLE_WORLDBOSS:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_WORLDBOSS_RANK] = (localeinfo.NEW_AFFECT_WORLDBOSS_RANK, "icon/affectshower/rank.tga")


	AFFECT_DATA_DICT[chr.NEW_AFFECT_EID_BUFF] = (localeinfo.AFFECT_EID_BUFF_TOOLTIP, "icon/affectshower/eid.tga")

	AFFECT_DATA_DICT[chr.NEW_AFFECT_WATCHES_BUFF] = (localeinfo.AFFECT_WATCHES_BUFF_TOOLTIP, "icon/affectshower/time.tga")
	if app.ENABLE_ITEM_BUFF_SYSTEM:
		AFFECT_DATA_DICT[chr.AFFECT_SKILL_RESIST_BUFF] = (localeinfo.SKILL_HOSIN_NEW, "d:/ymir work/ui/skill/shaman/hosin_03.sub", 2, 0)
		AFFECT_DATA_DICT[chr.AFFECT_SKILL_CRITICAL_BUFF] = (localeinfo.SKILL_GICHEON_NEW, "d:/ymir work/ui/skill/shaman/gicheon_03.sub", 2, 0)
		AFFECT_DATA_DICT[chr.AFFECT_SKILL_REFLECT_BUFF] = (localeinfo.SKILL_BOHO_NEW, "d:/ymir work/ui/skill/shaman/boho_03.sub", 2, 0)

	if app.ENABLE_QUEEN_NETHIS:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_SUNGMA_STR_DEBUFF] = (localeinfo.AFFECT_SUNGMA_STR_DEBUFF_TOOLTIP, "icon/affectshower/power_debuff.tga")
		AFFECT_DATA_DICT[chr.NEW_AFFECT_SUNGMA_MOVE_DEBUFF] = (localeinfo.AFFECT_SUNGMA_MOVE_DEBUFF_TOOLTIP, "icon/affectshower/move_debuff.tga")


	AFFECT_DATA_DICT[chr.NEW_AFFECT_HALLOWEEN_BUFF] = (localeinfo.AFFECT_HALLOWEEN_BUFF_TOOLTIP, "icon/affectshower/halloween.tga")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_CHRISTMAS_BUFF] = (localeinfo.AFFECT_CHRISTMAS_BUFF_TOOLTIP, "icon/affectshower/xmas.tga")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_BATTLEPASS_BUFF] = (localeinfo.AFFECT_BATTLEPASS_BUFF_TOOLTIP, "icon/affectshower/bp.tga")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_YOHARA_POTIONS] = (localeinfo.AFFECT_YOHARA_POTIONS, "icon/affectshower/blend_new.tga")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_RAMADAN_BUFF] = (localeinfo.AFFECT_RAMADAN_BUFF_TOOLTIP, "icon/affectshower/ramadan.tga")
	AFFECT_DATA_DICT[chr.NEW_AFFECT_SUMMER_BUFF] = (localeinfo.AFFECT_SUMMER_BUFF_TOOLTIP, "icon/affectshower/summer.tga")
	if app.ENABLE_SET_ITEM:
		AFFECT_DATA_DICT[chr.NEW_AFFECT_SET_ITEM] = (localeinfo.TOOLTIP_SET_ITEM, "d:/ymir work/ui/skill/common/affect/set_bonus.sub")


	def __init__(self):
		if app.USE_PERSO_SIZE_ON_AFFECT_SHOWER:
			self.expand_button = None

		ui.Window.__init__(self)
		self.yohara_apply_count = 0  # dream addons
		self.affectImageDict={}

		if app.RENEWAL_PICKUP_AFFECT:
			self.premiumPickupDialog=None

		if app.ENABLE_GROWTH_PET_SYSTEM:
			self.petSkillaffectImageDict={}

		self.Destroy()

		if app.USE_RENEWAL_AFFECT_SHOWER:
			self.ySize=0

		if app.USE_PERSO_SIZE_ON_AFFECT_SHOWER:
			self.is_expanded = False

			self.expand_button = ui.MakeButton(self, 0, 0, "", "d:/ymir work/ui/", "affect_expand_down.png", "affect_expand_up_hover.png", "affect_expand_up_down.png")
			self.expand_button.Hide()
			self.expand_button.SetEvent(ui.__mem_func__(self.OnExpand))
			
			# self.is_expanded = False
			# self.expand_button = ui.Button()

			# self.expand_button.SetUpVisual(self.IMG_EXPAND_DOWN)
			# self.expand_button.SetOverVisual(self.IMG_EXPAND_DOWN)
			# self.expand_button.SetDownVisual(self.IMG_EXPAND_DOWN)
			
			# self.expand_button.Hide()
			# self.expand_button.SetEvent(ui.__mem_func__(self.OnExpand))

			# self.expand_button.SetParent(self)
			# self.expand_button = ui.MakeButton(self, 0, 0, "", "d:/ymir work/ui/", "affect_expand_up.png", "affect_expand_up.png", "affect_expand_up.png")
			# self.expand_button.Hide()
			# self.expand_button.SetEvent(ui.__mem_func__(self.OnExpand))

		self.SetPosition(10,10)
		self.Show()

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		if app.USE_PERSO_SIZE_ON_AFFECT_SHOWER and self.expand_button:
			self.expand_button.SetEvent(None)
			del self.expand_button
			self.expand_button = None

		self.ClearAllAffects()

		self.serverPlayTime=0
		self.clientPlayTime=0
		self.lastUpdateTime=0
		
		if app.USE_RENEWAL_AFFECT_SHOWER:
			self.removeAffectDialog=None
			global affectDict,overInImage
			affectDict={}
			overInImage=None
		if app.ENABLE_MULTIFARM_BLOCK:
			self.multiFarmBlockDialog=None
			self.farmStatusImage=None
		self.horseImage=None
		self.lovePointImage=None
		self.pvpOrderImage=None

		if app.ENABLE_GROWTH_PET_SYSTEM:
			self.petSkillaffectImageDict={}
			# >>> PET SKILL PANEL: combined-panel state (affect vnum -> skill slot index)
			self.petSkillPanelActive = {}
			self.petSkillPanelIcon = None
			self.petSkillPanelBoard = None
			# <<< PET SKILL PANEL

		if app.ENABLE_CONQUEROR_LEVEL:
			self.sungmaImage=None

	if app.USE_PERSO_SIZE_ON_AFFECT_SHOWER:
		def Show(self):
			if self.expand_button:
				self.expand_button.Show()

			wndMgr.Show(self.hWnd)

		def Hide(self):
			if self.expand_button:
				self.expand_button.Hide()

			wndMgr.Hide(self.hWnd)

	if app.USE_PERSO_SIZE_ON_AFFECT_SHOWER:
		# def OnExpand(self):
			# if self.is_expanded:
				# self.is_expanded = False
			# else:
				# self.is_expanded = True

			# self.__ArrangeImageList()

		def OnExpand(self):
			if self.is_expanded:
				self.is_expanded = False

				self.expand_button.SetUpVisual(self.IMG_EXPAND_UP)
				self.expand_button.SetOverVisual(self.IMG_EXPAND_UP_HOVER)
				self.expand_button.SetDownVisual(self.IMG_EXPAND_UP_DOWN)
			else:
				self.is_expanded = True

				self.expand_button.SetUpVisual(self.IMG_EXPAND_DOWN)
				self.expand_button.SetOverVisual(self.IMG_EXPAND_DOWN_DOWN)
				self.expand_button.SetDownVisual(self.IMG_EXPAND_DOWN_HOVER)

			self.__ArrangeImageList()


	def ClearAllAffects(self):
		self.horseImage=None
		self.lovePointImage=None
		self.pvpOrderImage=None
		if app.RENEWAL_PICKUP_AFFECT:
			self.premiumPickupDialog=None

		if app.ENABLE_CONQUEROR_LEVEL:
			self.sungmaImage=None
		if app.ENABLE_MULTIFARM_BLOCK:
			self.multiFarmBlockDialog=None
			self.farmStatusImage=None		
		if app.ENABLE_NEW_BLEND_AFFECT:
			if getattr(self, "combinedGroupState", None):
				for _st in self.combinedGroupState.values():
					if _st["board"]:
						_st["board"].Hide()
			self.combinedGroupState = {}
			for _g in COMBINED_GROUPS:
				self.combinedGroupState[_g.key] = {"active": {}, "icon": None, "board": None}
		# >>> PET SKILL PANEL: same teardown discipline as the blend groups
		if app.ENABLE_GROWTH_PET_SYSTEM:
			if getattr(self, "petSkillPanelBoard", None):
				self.petSkillPanelBoard.Hide()
			self.petSkillPanelActive = {}
			self.petSkillPanelIcon = None
			self.petSkillPanelBoard = None
		# <<< PET SKILL PANEL
		self.fishCombatActive = False
		self.fishPausedAt = 0
		self.affectImageDict={}
		self.__ArrangeImageList()

	def ClearAffects(self):
		self.living_affectImageDict={}
		for key,image in self.affectImageDict.items():
			if not image.IsSkillAffect():
				self.living_affectImageDict[key]=image
		
		self.affectImageDict=self.living_affectImageDict
		self.__ArrangeImageList()

	def BINARY_NEW_AddAffect(self,type,pointIdx,value,duration):
		if type==chr.NEW_AFFECT_MALL:
			affect=self.MALL_DESC_IDX_START + pointIdx
		else:
			affect=type

		if type == chr.NEW_AFFECT_YOHARA_POTIONS:
			self.yohara_apply_count += 1  # Increment counter

		# >>> COMBINED BLEND PANEL BEGIN: route grouped affects into their own panel
		if app.ENABLE_NEW_BLEND_AFFECT and type in COMBINED_AFFECT_TO_GROUP:
			self.__AddCombinedBlend(COMBINED_AFFECT_TO_GROUP[type], type, pointIdx, value, duration)
			return
		# <<< COMBINED BLEND PANEL END

		if app.USE_RENEWAL_AFFECT_SHOWER:
			global affectDict
			affectNew = self.AffectToRealIndex(affect)
			affectData = affectDict[affectNew] if affectDict.has_key(affectNew) else {}
			affectList = affectData["affect"] if affectData.has_key("affect") else []
			maxDuration = affectData["duration"] if affectData.has_key("duration") else 0
			
			if type == chr.NEW_AFFECT_FISHES:
				for data in affectList:
					if data[0] == pointIdx:
						data[1] = value
						break
				else:
					affectList.append([pointIdx, value])
				fishEnds = affectData.get("fish_ends", {})
				fishEnds[pointIdx] = 0 if duration >= self.FISH_PERMANENT_SECONDS else app.GetGlobalTimeStamp() + duration
				affectData["fish_ends"] = fishEnds
			elif not [pointIdx, value] in affectList:
				affectList.append([pointIdx, value])
			if duration+app.GetGlobalTimeStamp() > maxDuration:
				affectData["duration"] = duration+app.GetGlobalTimeStamp()
			
			if affectNew in (94, 96, 110, 111):
				affectData["buffi"] = affect in (163, 164, 166)	# Kwaesok (165) keeps full value in PvP - no tag
			affectData["affect"] = affectList
			affectDict[affectNew] = affectData

			if type == chr.NEW_AFFECT_FISHES and app.ENABLE_NEW_BLEND_AFFECT:
				self.__AddFishPanel()
				return
			
			# if type < 500 and self.CheckRemoveAffect(type) == False:
			if type < 500:
				if app.ENABLE_NEW_BLEND_AFFECT:
					exceptList = [chr.AFFECT_BLEND_POTION_1, chr.AFFECT_BLEND_POTION_2, chr.AFFECT_BLEND_POTION_3,
									chr.AFFECT_BLEND_POTION_4, chr.AFFECT_BLEND_POTION_5, chr.AFFECT_BLEND_POTION_6,
									chr.AFFECT_BLEND_POTION_7, chr.AFFECT_BLEND_POTION_8, chr.AFFECT_BLEND_POTION_9,
									chr.NEW_AFFECT_YOHARA_POTIONS,
									chr.AFFECT_ENERGY, chr.AFFECT_DRAGON_GOD_1, chr.AFFECT_DRAGON_GOD_1, chr.AFFECT_DRAGON_GOD_1,
									chr.AFFECT_DRAGON_GOD_2, chr.AFFECT_DRAGON_GOD_3, chr.AFFECT_DRAGON_GOD_4,
									chr.AFFECT_CRITICAL, chr.AFFECT_PENETRATE, chr.AFFECT_ATTACK_SPEED,
									chr.AFFECT_MOVE_SPEED, chr.AFFECT_RESEARCHER_ELIXIR, 434,]
				
				if not type in exceptList:
					return
		else:
			if type < 500:
				if app.ENABLE_NEW_BLEND_AFFECT:
					exceptList = [chr.AFFECT_BLEND_POTION_1, chr.AFFECT_BLEND_POTION_2, chr.AFFECT_BLEND_POTION_3,
									chr.AFFECT_BLEND_POTION_4, chr.AFFECT_BLEND_POTION_5, chr.AFFECT_BLEND_POTION_6,
									chr.AFFECT_BLEND_POTION_7, chr.AFFECT_BLEND_POTION_8, chr.AFFECT_BLEND_POTION_9,
									chr.AFFECT_ENERGY, chr.AFFECT_DRAGON_GOD_1, chr.AFFECT_DRAGON_GOD_1, chr.AFFECT_DRAGON_GOD_1,
									chr.AFFECT_DRAGON_GOD_2, chr.AFFECT_DRAGON_GOD_3, chr.AFFECT_DRAGON_GOD_4,
									chr.AFFECT_CRITICAL, chr.AFFECT_PENETRATE, chr.AFFECT_ATTACK_SPEED,
									chr.AFFECT_MOVE_SPEED, chr.AFFECT_RESEARCHER_ELIXIR,]
				
				if not type in exceptList:
					return
		if self.affectImageDict.has_key(affect):
			if affect == chr.NEW_AFFECT_FISHES:
				self.__RefreshFishImage()
			return

		if not self.AFFECT_DATA_DICT.has_key(affect):
			return
		
		if affect==chr.NEW_AFFECT_NO_DEATH_PENALTY or\
			affect==chr.NEW_AFFECT_SKILL_BOOK_BONUS or\
			affect==chr.NEW_AFFECT_AUTO_SP_RECOVERY or\
			affect==chr.NEW_AFFECT_AUTO_HP_RECOVERY or\
			affect==chr.NEW_AFFECT_SKILL_BOOK_NO_DELAY or\
			affect==getattr(chr, "NEW_AFFECT_DOUBLE_RUN", 842) or\
			affect==getattr(chr, "NEW_AFFECT_DOUBLE_RUN_OFF", 843) or\
			affect==getattr(chr, "NEW_AFFECT_SOLO_LEADERSHIP", 901):
			duration=0
		
		affectData=self.AFFECT_DATA_DICT[affect]
		description=affectData[0]
		filename=affectData[1]
		
		if pointIdx==player.POINT_MALL_ITEMBONUS:
			# Sold drop boosters carry half their advertised value (docs/DROP_BONUS_UNIFICATION.md) - show the advertised number.
			value=float(value) * 2.0
		elif pointIdx==player.POINT_MALL_GOLDBONUS:
			value=float(value) * 100.0 / 100.0
		
		if affect==chr.NEW_AFFECT_SAFE_BOX_BUFF:
			if pointIdxplayer.POINT_MALL_EXPBONUS:
				description=localeinfo.TOOLTIP_AFFECT_SAFEBOX_BUFF_01
			elif pointIdxplayer.POINT_MALL_DEFBONUS:
				description=localeinfo.TOOLTIP_AFFECT_SAFEBOX_BUFF_02
			elif pointIdxplayer.POINT_MAX_HP_PCT:
				description=localeinfo.TOOLTIP_AFFECT_SAFEBOX_BUFF_03
			elif pointIdxplayer.POINT_ATTBONUS_MONSTER:
				description=localeinfo.TOOLTIP_AFFECT_SAFEBOX_BUFF_04
			else:
				description=affectData[0]
		
		if affect != chr.NEW_AFFECT_AUTO_SP_RECOVERY and\
			affect != chr.NEW_AFFECT_AUTO_HP_RECOVERY and\
			callable(description):
			try:
				description = description(float(value))
			except Exception as e:
				import dbg
				dbg.TraceError(str(e))
				dbg.TraceError(str(affect))

		image = AffectImage()
		image.SetParent(self)
		image.LoadImage(filename)
		image.SetDescription(description)
		image.SetDuration(duration)
		image.SetAffect(affect)

		if app.USE_RENEWAL_AFFECT_SHOWER:
			if self.CheckRemoveAffectReal(affect):
				image.isCanRemove=True
				image.SetEvent(ui.__mem_func__(self.__OnClickAffect),"mouse_click", affect, description)
		else:
			if affect == chr.NEW_AFFECT_EXP_BONUS_EURO_FREE or affect == chr.NEW_AFFECT_EXP_BONUS_EURO_FREE_UNDER_15 or self.INFINITE_AFFECT_DURATION < duration:
				image.SetClock(FALSE)
				image.UpdateDescription()
			elif affect == chr.NEW_AFFECT_AUTO_SP_RECOVERY or affect == chr.NEW_AFFECT_AUTO_HP_RECOVERY:
				image.UpdateAutoPotionDescription()
			else:
				image.UpdateDescription()

		if app.RENEWAL_PICKUP_AFFECT:
			if affect == chr.NEW_AFFECT_PICKUP_ENABLE or affect == chr.NEW_AFFECT_PICKUP_DEACTIVE:
				image.SetEvent(ui.__mem_func__(self.ClickPremiumPickup), "mouse_click", affect)

		if affect == getattr(chr, "NEW_AFFECT_DOUBLE_RUN", 842) or affect == getattr(chr, "NEW_AFFECT_DOUBLE_RUN_OFF", 843):
			image.SetEvent(ui.__mem_func__(self.ClickDoubleRun), "mouse_click", affect)

		image.SetScale(AFFECT_ICON_SCALE, AFFECT_ICON_SCALE)
		image.Show()
		self.affectImageDict[affect] = image
		if affect == chr.NEW_AFFECT_FISHES:
			self.__RefreshFishImage()
		self.__ArrangeImageList()

	if app.RENEWAL_PICKUP_AFFECT:
		def OnClosePremiumPick(self, answer):
			if not self.premiumPickupDialog:
				return
			if answer:
				net.SendChatPacket("/pickup_affect")
			self.premiumPickupDialog.Close()
			self.premiumPickupDialog = None
		def ClickPremiumPickup(self, emptyArg, currentAffectType):
			premiumPickupDialog = uicommon.QuestionDialog()
			if currentAffectType == chr.NEW_AFFECT_PICKUP_ENABLE:
				premiumPickupDialog.SetText(localeinfo.NEW_AFFECT_PREMIUM_PICK_DEACTIVE_TEXT)
			elif currentAffectType == chr.NEW_AFFECT_PICKUP_DEACTIVE:
				premiumPickupDialog.SetText(localeinfo.NEW_AFFECT_PREMIUM_PICK_ACTIVE_TEXT)
			premiumPickupDialog.SetAcceptEvent(lambda arg = True: self.OnClosePremiumPick(arg))
			premiumPickupDialog.SetCancelEvent(lambda arg = False: self.OnClosePremiumPick(arg))
			premiumPickupDialog.Open()
			self.premiumPickupDialog = premiumPickupDialog

	def ClickDoubleRun(self, emptyArg, currentAffectType):
		net.SendChatPacket("/double_run")

	def BINARY_NEW_RemoveAffect(self,type,pointIdx):
		if type==chr.NEW_AFFECT_MALL:
			affect=self.MALL_DESC_IDX_START + pointIdx
		else:
			affect=type

		# >>> COMBINED BLEND PANEL BEGIN
		if app.ENABLE_NEW_BLEND_AFFECT and type in COMBINED_AFFECT_TO_GROUP:
			self.__RemoveCombinedBlend(COMBINED_AFFECT_TO_GROUP[type], type)
			return
		# <<< COMBINED BLEND PANEL END

		if app.USE_RENEWAL_AFFECT_SHOWER:
			global affectDict
			affectNew = self.AffectToRealIndex(affect)
			

			
			
			affectData = affectDict[affectNew] if affectDict.has_key(affectNew) else {}
			affectList = affectData["affect"] if affectData.has_key("affect") else []
			removeIndex = -1
			
			for data in affectList:
				if data[0] == pointIdx:
					removeIndex = affectList.index(data)
					break
			
			if removeIndex != -1:
				del affectList[removeIndex]
				affectData["affect"] = affectList
				affectDict[affectNew] = affectData
	
		if type == chr.NEW_AFFECT_YOHARA_POTIONS:
			if self.yohara_apply_count > 0:
				self.yohara_apply_count -= 1  # counter

			# Remove icon
			if self.yohara_apply_count <= 0 and affect in self.affectImageDict:
				del self.affectImageDict[affect]
				self.__ArrangeImageList()
			return  # Skip

		if type == chr.NEW_AFFECT_FISHES and app.USE_RENEWAL_AFFECT_SHOWER:
			fishData = affectDict.get(chr.NEW_AFFECT_FISHES, {})
			fishData.get("fish_ends", {}).pop(pointIdx, None)
			if app.ENABLE_NEW_BLEND_AFFECT:
				self.__RemoveFishPanel(bool(fishData.get("affect")))
				return
			if fishData.get("affect"):
				self.__RefreshFishImage()
				return

		self.__RemoveAffect(affect)
		self.__ArrangeImageList()

	FISH_PERMANENT_SECONDS = 60 * 60 * 24 * 365

	def __RefreshFishImage(self):
		if not app.USE_RENEWAL_AFFECT_SHOWER:
			return
		image = self.affectImageDict.get(chr.NEW_AFFECT_FISHES)
		if not image:
			return
		fishEnds = affectDict.get(chr.NEW_AFFECT_FISHES, {}).get("fish_ends", {})
		finiteEnds = [end for end in fishEnds.values() if end > 0]
		if finiteEnds:
			image.SetDuration(max(0, max(finiteEnds) - app.GetGlobalTimeStamp()))
		else:
			image.SetDuration(0)

	def SetFishCombatState(self, state):
		self.fishCombatActive = bool(state)
		if not state:
			self.fishPausedAt = app.GetGlobalTimeStamp()
		if not app.ENABLE_NEW_BLEND_AFFECT:
			return
		groupState = self.combinedGroupState.get(FISH_PANEL_GROUP.key)
		if groupState and groupState["board"] and groupState["board"].IsShow():
			groupState["board"].Refresh(self.__BuildFishRows())

	def __AddFishPanel(self):
		state = self.combinedGroupState[FISH_PANEL_GROUP.key]
		if not getattr(self, "fishCombatActive", False) and not getattr(self, "fishPausedAt", 0):
			self.fishPausedAt = app.GetGlobalTimeStamp()
		if not state["icon"]:
			icon = CombinedBlendIcon(self, FISH_PANEL_GROUP)
			icon.SetParent(self)
			icon.SetEvent(ui.__mem_func__(self.__OnClickAffect), "mouse_click", chr.NEW_AFFECT_FISHES, FISH_PANEL_GROUP.title)
			icon.Show()
			state["icon"] = icon
		if state["board"] and state["board"].IsShow():
			state["board"].Refresh(self.__BuildFishRows())
		self.__ArrangeImageList()

	def __RemoveFishPanel(self, hasRemaining):
		state = self.combinedGroupState[FISH_PANEL_GROUP.key]
		if hasRemaining:
			if state["board"] and state["board"].IsShow():
				state["board"].Refresh(self.__BuildFishRows())
		else:
			if state["board"]:
				state["board"].Hide()
			state["icon"] = None
			state["board"] = None
		self.__ArrangeImageList()

	def __BuildFishRows(self):
		rows = []
		data = affectDict.get(chr.NEW_AFFECT_FISHES, {})
		ends = data.get("fish_ends", {})
		now = app.GetGlobalTimeStamp()
		pausedAt = getattr(self, "fishPausedAt", 0) or now
		active = getattr(self, "fishCombatActive", False)
		pointDict = uitooltip.ItemToolTip.POINT_DICT
		fishItems = _BuildFishPointItems()
		permaVnum = 0
		for pair in data.get("affect", []):
			if ends.get(pair[0], -1) == 0:
				permaVnum = fishItems["perma"].get(pair[0], 0)
				if permaVnum:
					break
		for pair in data.get("affect", [])[:12]:
			pointIdx = pair[0]
			value = pair[1]
			if pointIdx == 0 or not pointDict.has_key(pointIdx):
				continue
			try:
				title = pointDict[pointIdx](value).replace("+-", "-")
			except:
				continue
			end = ends.get(pointIdx, 0)
			if end == 0:
				endTime = 0
				timeText = getattr(localeinfo, "TOOLTIP_FISH_PERMANENT", "Permanent until replaced or removed")
			elif not active:
				remain = max(0, end - pausedAt)
				endTime = 0
				timeText = "%s: %s (%s)" % (COMBINED_BLEND_TIME_LABEL, localeinfo.SecondToDHM(remain), getattr(localeinfo, "FISH_TIME_PAUSED", "paused"))
			else:
				endTime = end
				timeText = None
			if end == 0:
				rowVnum = fishItems["perma"].get(pointIdx, 0) or permaVnum or fishItems["timed"].get(pointIdx, 0)
			else:
				rowVnum = fishItems["timed"].get(pointIdx, 0) or fishItems["perma"].get(pointIdx, 0)
			iconPath = _FishRowIcon(rowVnum) or "icon/affectshower/fishing_normal.tga"
			rows.append({"icon": iconPath, "title": title, "effect": "", "endTime": endTime, "timeText": timeText})
		return rows

	def SetAffect(self,affect):
		self.__AppendAffect(affect)
		self.__ArrangeImageList()

	def ResetAffect(self,affect):
		self.__RemoveAffect(affect)
		self.__ArrangeImageList()

	def SetLoverInfo(self,name,lovePoint):
		image=LovePointImage()
		image.SetParent(self)
		image.SetLoverInfo(name,lovePoint)
		self.lovePointImage=image
		
		self.__ArrangeImageList()

	if app.ENABLE_MULTIFARM_BLOCK:
		def __OnClickMultiFarm(self, emptyArg):
			multiFarmBlockDialog = uicommon.QuestionDialog()
			if self.farmStatusImage.multiFarmStatus:
				multiFarmBlockDialog.SetText(localeinfo.MULTI_FARM_DEACTIVE_TEXT)
			else:
				multiFarmBlockDialog.SetText(localeinfo.MULTI_FARM_ACTIVE_TEXT)
			multiFarmBlockDialog.SetAcceptEvent(lambda arg = True: self.OnCloseMultiFarm(arg))
			multiFarmBlockDialog.SetCancelEvent(lambda arg = False: self.OnCloseMultiFarm(arg))
			multiFarmBlockDialog.Open()
			self.multiFarmBlockDialog = multiFarmBlockDialog
		def OnCloseMultiFarm(self, answer):
			if not self.multiFarmBlockDialog:
				return
			if answer:
				net.SendChatPacket("/multi_farm")
			self.multiFarmBlockDialog.Close()
			self.multiFarmBlockDialog = None
		def SetMultiFarmPlayer(self, playerName):
			if self.farmStatusImage:
				self.farmStatusImage.players.append(playerName)
		def SetMultiFarmInfo(self, farmStatus):
			image = MultiFarmImage()
			image.SetParent(self)
			image.SetMultiFarmInfo(farmStatus)
			image.SetEvent(ui.__mem_func__(self.__OnClickMultiFarm),"mouse_click")
			image.Show()
			self.farmStatusImage = image
			self.__ArrangeImageList()

	def ShowLoverState(self):
		if self.lovePointImage:
			self.lovePointImage.Show()
			self.__ArrangeImageList()

	def HideLoverState(self):
		if self.lovePointImage:
			self.lovePointImage.Hide()
			self.__ArrangeImageList()

	def ClearLoverState(self):
		self.lovePointImage=None
		self.__ArrangeImageList()

	def OnUpdateLovePoint(self,lovePoint):
		if self.lovePointImage:
			self.lovePointImage.OnUpdateLovePoint(lovePoint)

	def SetHorseState(self,level,health,battery):
		if level==0:
			self.horseImage=None
		else:
			image=HorseImage()
			image.SetParent(self)
			image.SetState(level,health,battery)
			image.Show()
			self.horseImage=image
			
			self.__ArrangeImageList()

	def SetPlayTime(self,playTime):
		self.serverPlayTime=playTime
		self.clientPlayTime=app.GetTime()

	if app.ENABLE_CONQUEROR_LEVEL:
		def SetSungMaAffectImage(self, str, hp, move, immune):
			image = SungMaAffectImage()
			image.SetParent(self)
			image.SetSungmaValue(str, hp, move, immune)
			image.Show()

			self.sungmaImage=image
			self.__ArrangeImageList()

	def SetPvPOrderState(self, state):
		if state:
			image=PvPOrderImage()
			image.SetParent(self)
			image.Setup()
			image.Show()
			self.pvpOrderImage=image
		else:
			self.pvpOrderImage=None

		self.__ArrangeImageList()

	def __AppendAffect(self,affect):
		if self.affectImageDict.has_key(affect):
			return
		
		try:
			affectData=self.AFFECT_DATA_DICT[affect]
		except KeyError:
			return
		
		name=affectData[0]
		filename=affectData[1]
		
		skillIndex=player.AffectIndexToSkillIndex(affect)
		if 0 != skillIndex:
			name=skill.GetSkillName(skillIndex)
		
		image=AffectImage()
		image.SetParent(self)
		
		if not app.USE_RENEWAL_AFFECT_SHOWER:
			image.SetAffect(affect)
		
		__blockedAffects = [chr.AFFECT_POISON, chr.AFFECT_SLOW, chr.AFFECT_STUN]
		if not affect in __blockedAffects:
			image.SetSkillAffectFlag(TRUE)
		try:
			image.LoadImage(filename)
			
			if not app.USE_RENEWAL_AFFECT_SHOWER:
				image.SetToolTipText(name,0,40)
			
			if app.USE_RENEWAL_AFFECT_SHOWER:
				image.SetAffect(affect)
				image.SetDescription(name)
				
				if self.CheckRemoveAffectReal(affect):
					image.isCanRemove=True
					image.SetEvent(ui.__mem_func__(self.__OnClickAffect),"mouse_click",affect,name)
			
			image.SetScale(AFFECT_ICON_SCALE, AFFECT_ICON_SCALE)
			image.Show()
			
			self.affectImageDict[affect]=image
		except:
			pass

	def __RemoveAffect(self, affect):
		if not self.affectImageDict.has_key(affect):
			return
		
		del self.affectImageDict[affect]
		self.__ArrangeImageList()

	def get_idx(self, j):
		return j[0]

	#if app.USE_PERSO_SIZE_ON_AFFECT_SHOWER: bFromExpand
	def __ArrangeImageList(self):
		order_tuple = ()

		if self.lovePointImage:
			order_tuple += (self.lovePointImage,)

		if self.horseImage:
			order_tuple += (self.horseImage,)

		if app.ENABLE_CONQUEROR_LEVEL and self.sungmaImage:
			order_tuple += (self.sungmaImage,)

		if self.pvpOrderImage:
			order_tuple += (self.pvpOrderImage,)

		if app.ENABLE_NEW_BLEND_AFFECT:
			for _g in COMBINED_GROUPS:
				_gicon = self.combinedGroupState[_g.key]["icon"]
				if _gicon:
					order_tuple += (_gicon,)

		if app.ENABLE_MULTIFARM_BLOCK and self.farmStatusImage:
			order_tuple += (self.farmStatusImage,)

		if app.ENABLE_GROWTH_PET_SYSTEM:
			# >>> PET SKILL PANEL: one collapsed icon in place of the per-skill row
			# (the legacy dict stays empty while the panel path is active)
			if app.ENABLE_NEW_BLEND_AFFECT and getattr(self, "petSkillPanelIcon", None):
				order_tuple += (self.petSkillPanelIcon,)
			# <<< PET SKILL PANEL
			for k, v in sorted(self.petSkillaffectImageDict.items()):
				order_tuple += (v[1],)

		for k, v in sorted(self.affectImageDict.items()):
			order_tuple += (v,)

		order_tuple_len = len(order_tuple)

		if order_tuple_len > self.MAX_IMAGE_X_LINE and not self.is_expanded:
			for v in order_tuple:
				v.Hide()

		width = self.MAX_IMAGE_X_LINE if order_tuple_len > self.MAX_IMAGE_X_LINE else order_tuple_len
		width *= self.IMAGE_STEP
		height = round(float(order_tuple_len) / float(self.MAX_IMAGE_X_LINE) + 0.49) * self.IMAGE_STEP

		if app.USE_PERSO_SIZE_ON_AFFECT_SHOWER and self.expand_button:
			if order_tuple_len > self.MAX_IMAGE_X_LINE:
				if not self.is_expanded:
					height = self.IMAGE_STEP

				self.expand_button.SetPosition(-2, height)
				self.expand_button.Show()

				height += self.expand_button.GetHeight()
			else:
				self.expand_button.Hide()

		self.SetSize(width, height)

		c = 0
		h = 0
		for v in order_tuple:
			if c >= self.MAX_IMAGE_X_LINE:
				if app.USE_PERSO_SIZE_ON_AFFECT_SHOWER and not self.is_expanded:
					break

				c = 0
				h += self.IMAGE_STEP

			v.SetPosition(self.IMAGE_STEP * c, h)
			v.Show()
			c += 1

		order_tuple = ()

	if app.ENABLE_GROWTH_PET_SYSTEM:
		def SetPetSkillAffect(self,index,affect):
			# >>> PET SKILL PANEL: collapse into the combined panel when available
			if app.ENABLE_NEW_BLEND_AFFECT:
				self.__AddPetSkillPanel(index, affect)
				return
			# <<< PET SKILL PANEL (legacy one-icon-per-skill path below)
			if self.__AppendPetSkillAffect(index,affect):
				self.__ArrangeImageList()

		def ClearPetSkillAffect(self):
			# >>> PET SKILL PANEL: the feeders clear-then-readd on every skill update,
			# so a full state drop here is the blend groups' remove-to-empty case.
			if app.ENABLE_NEW_BLEND_AFFECT:
				if self.petSkillPanelBoard:
					self.petSkillPanelBoard.Hide()
				self.petSkillPanelActive = {}
				self.petSkillPanelIcon = None
				self.petSkillPanelBoard = None
			# <<< PET SKILL PANEL
			self.petSkillaffectImageDict.clear()
			self.__ArrangeImageList()

		# >>> PET SKILL PANEL BEGIN
		def __AddPetSkillPanel(self, index, affect):
			# Feeders pass slot+1 (the legacy 1/2/3 convention) -- store the raw slot,
			# it keys the live value lookup and the board's row order.
			slotIdx = index - 1
			# The SLOT is the identity: a delete+learn swap re-adds a new vnum at the
			# same slot without a Clear in between (RefreshStatus never clears), so the
			# old vnum must be evicted here or stale entries accumulate past the
			# board's fixed row pool (IndexError on hover) and ghost-row forever.
			for oldAffect in self.petSkillPanelActive.keys():
				if self.petSkillPanelActive[oldAffect] == slotIdx and oldAffect != affect:
					del self.petSkillPanelActive[oldAffect]
			self.petSkillPanelActive[affect] = slotIdx
			if not self.petSkillPanelIcon:
				icon = PetSkillPanelIcon(self)
				icon.SetParent(self)
				icon.Show()
				self.petSkillPanelIcon = icon
			if not self.petSkillPanelIcon.iconLoaded:
				self.petSkillPanelIcon.RefreshIcon(self.__FirstPetSkillIconPath())
			if self.petSkillPanelBoard and self.petSkillPanelBoard.IsShow():
				self.petSkillPanelBoard.Refresh(self.__BuildPetSkillRows())
			self.__ArrangeImageList()

		def __FirstPetSkillIconPath(self):
			for affect, slotIdx in sorted(self.petSkillPanelActive.items(), key=lambda kv: kv[1]):
				path = skill.GetPetSkillIconPath(affect)
				if path:
					return path
			return ""

		def ShowPetSkillBoard(self):
			if not self.petSkillPanelActive or not self.petSkillPanelIcon:
				return
			if not self.petSkillPanelBoard:
				self.petSkillPanelBoard = PetSkillPanelBoard(
					PET_SKILL_PANEL_TITLE, getattr(player, "PET_SKILL_COUNT_MAX", 6))
			self.petSkillPanelBoard.Refresh(self.__BuildPetSkillRows())
			(gx, gy) = self.petSkillPanelIcon.GetGlobalPosition()
			self.petSkillPanelBoard.SetPosition(gx, gy + self.IMAGE_STEP + 4)
			self.petSkillPanelBoard.SetTop()
			self.petSkillPanelBoard.Show()

		def HidePetSkillBoard(self):
			if self.petSkillPanelBoard:
				self.petSkillPanelBoard.Hide()

		def __BuildPetSkillRows(self):
			# One row per active skill in slot order: skill icon + name + CURRENT granted
			# value, re-read live on every hover/refresh so upgrades show immediately.
			# endTime=0 keeps the inherited time line empty -- no timer by design.
			rows = []
			pet_id = player.GetActivePetItemId()
			if not pet_id:
				return rows
			# Hard clamp to the board's row pool (belt over the slot-eviction braces --
			# the inherited Refresh indexes rowSlots[i] unguarded).
			maxRows = getattr(player, "PET_SKILL_COUNT_MAX", 6)
			canReadIdx = hasattr(player, "GetPetSkillByIndex")
			for affect, slotIdx in sorted(self.petSkillPanelActive.items(), key=lambda kv: kv[1]):
				if len(rows) >= maxRows:
					break
				(name, desc, useType, coolTime) = skill.GetPetSkillInfo(affect)
				effect = ""
				if canReadIdx and slotIdx >= 0:
					data = player.GetPetSkillByIndex(pet_id, slotIdx)
					if data[0] == affect and data[1]:
						effect = self.__FormatPetSkillEffect(affect, useType, data[2], data[3], data[4])
				rows.append({
					"icon": skill.GetPetSkillIconPath(affect),
					"title": name,
					"effect": effect,
					"endTime": 0,
				})
			return rows

		def __FormatPetSkillEffect(self, vnum, useType, f1, f2, f3):
			# Mirrors PetSkillToolTip's formatting (same locale format strings, same unit
			# exceptions) so the panel and the Companion skill tooltip always agree.
			applyDict = None
			if hasattr(uitooltip, "PetSkillToolTip"):
				applyDict = getattr(uitooltip.PetSkillToolTip, "PET_SKILL_APPLY_DATA_DICT", None)
			if not applyDict or vnum not in applyDict:
				return ""
			fmt = applyDict[vnum]
			try:
				if skill.PET_SKILL_USE_TYPE_PASSIVE == useType:
					value = int(f2)
					if chr.PET_SKILL_AFFECT_GOLD_DROP == vnum:
						value = value / 10.0
					return fmt(value)
				elif skill.PET_SKILL_USE_TYPE_AUTO == useType:
					if chr.PET_SKILL_AFFECT_INVINCIBILITY == vnum:
						return fmt(f1 / 10.0, f2 / 10.0)
					if chr.PET_SKILL_FEATHER == vnum:
						return fmt(f1, f3 / 10.0, f2, f2 * 2)
					return fmt(f1, f2)
			except:
				return ""
			return ""
		# <<< PET SKILL PANEL END

		def __AppendPetSkillAffect(self,index,affect):
			if self.petSkillaffectImageDict.has_key(affect):
				return False
			
			filename=skill.GetPetSkillIconPath(affect)
			if filename=="":
				return False
			
			(pet_skill_name,pet_skill_desc,pet_skill_use_type,pet_skill_cool_time )=skill.GetPetSkillInfo(affect)
			
			image=GrowthPetImage()
			image.SetParent(self)
			
			try:
				image.LoadImage(filename)
				image.SetToolTipText(pet_skill_name,0,40)
				image.SetDescription(pet_skill_desc)
				image.SetScale(AFFECT_ICON_SCALE, AFFECT_ICON_SCALE)
				image.Show()
				self.petSkillaffectImageDict[affect]=[index,image]
			except:
				return False
			
			return True

	# >>> COMBINED BLEND PANEL BEGIN
	def __AddCombinedBlend(self, group, type, pointIdx, value, duration):
		state = self.combinedGroupState[group.key]
		active = state["active"]

		now = app.GetGlobalTimeStamp()
		endTime = now + duration if duration > 0 else 0

		entry = active.get(type, None)
		if entry is None:
			entry = {"endTime": endTime, "effects": []}
			active[type] = entry
		else:
			if duration <= 0:
				entry["endTime"] = 0
			elif entry["endTime"] != 0 and endTime > entry["endTime"]:
				entry["endTime"] = endTime

		entry["effects"] = [e for e in entry["effects"] if e[0] != pointIdx]
		entry["effects"].append([pointIdx, value])

		if not state["icon"]:
			icon = CombinedBlendIcon(self, group)
			icon.SetParent(self)
			icon.Show()
			state["icon"] = icon

		if state["board"] and state["board"].IsShow():
			state["board"].Refresh(self.__BuildCombinedBlendRows(group))

		self.__ArrangeImageList()

	def __RemoveCombinedBlend(self, group, type):
		state = self.combinedGroupState[group.key]
		active = state["active"]

		if type in active:
			del active[type]

		if not active and not getattr(group, "persistent", 0):
			if state["board"]:
				state["board"].Hide()
			state["icon"] = None
			state["board"] = None
		elif state["board"] and state["board"].IsShow():
			state["board"].Refresh(self.__BuildCombinedBlendRows(group))

		self.__ArrangeImageList()

	def ShowCombinedBlendBoard(self, group):
		state = self.combinedGroupState[group.key]
		if not state["icon"]:
			return
		if group.key == "fish":
			if not (app.USE_RENEWAL_AFFECT_SHOWER and affectDict.get(chr.NEW_AFFECT_FISHES, {}).get("affect")):
				return
		elif not state["active"] and not getattr(group, "persistent", 0):
			return

		if not state["board"]:
			if group.key == "fish":
				state["board"] = FishPanelBoard(group.title, 12)
			else:
				state["board"] = CombinedBlendBoard(group.title, len(group.affects) + len(getattr(group, "active_only", ())))

		state["board"].Refresh(self.__BuildCombinedBlendRows(group))

		(gx, gy) = state["icon"].GetGlobalPosition()
		state["board"].SetPosition(gx, gy + self.IMAGE_STEP + 4)
		state["board"].SetTop()
		state["board"].Show()

	def HideCombinedBlendBoard(self, group):
		state = self.combinedGroupState[group.key]
		if state["board"]:
			state["board"].Hide()

	def __RefreshPersistentGroups(self):
		# Persistent groups (guild blessings) keep their bar icon while the player is in a guild,
		# even with zero active affects, so the hover board can advertise every possible blessing.
		inGuild = guild.GetGuildID() != 0
		changed = 0
		for _g in COMBINED_GROUPS:
			if not getattr(_g, "persistent", 0):
				continue
			state = self.combinedGroupState[_g.key]
			if inGuild:
				if not state["icon"]:
					icon = CombinedBlendIcon(self, _g)
					icon.SetParent(self)
					icon.Show()
					state["icon"] = icon
					changed = 1
			elif state["icon"] and not state["active"]:
				if state["board"]:
					state["board"].Hide()
				state["icon"] = None
				state["board"] = None
				changed = 1
		if changed:
			self.__ArrangeImageList()

	def __BuildCombinedBlendRows(self, group):
		if group.key == "fish":
			return self.__BuildFishRows()
		rows = []
		active = self.combinedGroupState[group.key]["active"]
		persistent = getattr(group, "persistent", 0)
		activeOnly = getattr(group, "active_only", ())
		for affect in tuple(group.affects) + tuple(activeOnly):
			entry = active.get(affect, None)
			# active_only affects (e.g. dye) never show an inactive placeholder row
			if entry is None and (not persistent or affect in activeOnly):
				continue

			# Prefer the item's own (localized) icon + name; fall back to the affect art / locale title.
			iconPath = ""
			name = ""
			vnum = COMBINED_BLEND_ITEM_VNUM.get(affect, 0)
			if vnum:
				item.SelectItem(vnum)
				iconPath = item.GetIconImageFileName()
				name = item.GetItemName()
				if iconPath and iconPath.find("gr2") != -1:
					iconPath = ""   # 3D-model icon, not a flat image

			if not name:
				name = COMBINED_BLEND_TITLES.get(affect, "")
			if not iconPath and affect in self.AFFECT_DATA_DICT:
				iconPath = self.AFFECT_DATA_DICT[affect][1]

			if entry is not None:
				effect = self.__FormatBlendEffect(affect, entry["effects"])
				endTime = entry["endTime"]
				timeText = None
			else:
				effect = ""
				endTime = 0
				timeText = getattr(localeinfo, "COMBINED_GUILD_BLESS_INACTIVE", "Not active")
			if not effect:
				effect = GUILD_BLESS_EFFECT_TEXT.get(affect, "")

			rows.append({
				"icon": iconPath,
				"title": name,
				"effect": effect,
				"endTime": endTime,
				"timeText": timeText,
			})
		return rows

	def __FormatBlendEffect(self, affect, effects):
		parts = []
		pointDict = uitooltip.ItemToolTip.POINT_DICT
		for data in effects:
			pointIdx = data[0]
			value = data[1]
			if value == 0 or pointIdx == 0:   # POINT_NONE = collision bucket in POINT_DICT; carries no real stat
				continue
			if pointIdx == player.POINT_MALL_ITEMBONUS:
				value = value * 2   # sold drop boosters: half-real / double-shown
			try:
				if pointIdx in pointDict:
					parts.append(pointDict[pointIdx](value))
			except:
				pass

		if parts:
			return ", ".join(parts)

		if affect in self.AFFECT_DATA_DICT:
			desc = self.AFFECT_DATA_DICT[affect][0]
			try:
				return desc(0) if callable(desc) else desc
			except:
				pass
		return ""
	# <<< COMBINED BLEND PANEL END

	def OnUpdate(self):
		try:
			# Time display bug when disguised as MT-342
			if app.GetGlobalTimeStamp() > self.lastUpdateTime:
			#if app.GetGlobalTime() - self.lastUpdateTime > 500:
			#if 0 < app.GetGlobalTime():
				# Time display bug when disguised as MT-342
				#self.lastUpdateTime = app.GetGlobalTime()
				self.lastUpdateTime = app.GetGlobalTimeStamp()
				if app.ENABLE_NEW_BLEND_AFFECT:
					self.__RefreshPersistentGroups()
					for _g in COMBINED_GROUPS:
						_gboard = self.combinedGroupState[_g.key]["board"]
						if _gboard and _gboard.IsShow():
							_gboard.UpdateTimes()
				if app.USE_RENEWAL_AFFECT_SHOWER:
					global overInImage
					if overInImage:
						overInImage.OnMouseOverIn()
				else:
					for image in self.affectImageDict.values():
						if image.GetAffect() == chr.NEW_AFFECT_AUTO_HP_RECOVERY or image.GetAffect() == chr.NEW_AFFECT_AUTO_SP_RECOVERY:
							image.UpdateAutoPotionDescription()
							continue
						if not image.IsSkillAffect():
							image.UpdateDescription()
		except Exception, e:
			print "AffectShower::OnUpdate error : ", e


	if app.USE_RENEWAL_AFFECT_SHOWER:
		def AffectToRealIndex(self,affect):
			_dict = {\
						209:chr.AFFECT_POISON,
						211:chr.AFFECT_SLOW,
						210:chr.AFFECT_STUN,
						201:chr.AFFECT_ATT_SPEED_POTION,
						200:chr.AFFECT_MOV_SPEED_POTION,
						208:chr.AFFECT_FISH_MIND,
						163:94, 164:96, 165:110, 166:111,	# buffi-typed twins (__BUFFI_PVM_ONLY__) share the shaman buff entries
			}
			
			return _dict[affect] if _dict.has_key(affect) else affect

		def __OnClickAffect(self,arg,affect,name):
			if self.removeAffectDialog:
				self.removeAffectDialog.Close()
				del self.removeAffectDialog
				self.removeAffectDialog=None
			
			self.removeAffectDialog = uicommon.QuestionDialog()
			self.removeAffectDialog.SetText(localeinfo.AFFECT_REMOVE_QUESTION % name)
			self.removeAffectDialog.SetAcceptEvent(lambda arg = True: self.OnCloseRemoveAffect(arg))
			self.removeAffectDialog.SetCancelEvent(lambda arg = False: self.OnCloseRemoveAffect(arg))
			self.removeAffectDialog.affect = affect
			self.removeAffectDialog.Open()

		def OnCloseRemoveAffect(self,answer):
			if not self.removeAffectDialog:
				return
			
			if answer:
				net.SendChatPacket("/remove_affect %d"%TypeToAffectReal(self.removeAffectDialog.affect))
			
			self.removeAffectDialog.Close()
			del self.removeAffectDialog
			self.removeAffectDialog = None

		def CheckRemoveAffect(self,type):
			if type == chr.NEW_AFFECT_POLYMORPH:
				return True
			
			return True if TypeToAffect(type) != type else False

		def CheckRemoveAffectReal(self,type):
			if type == 831 or type == 832 or type == 833:
				return True
			if type == chr.NEW_AFFECT_FISHES:
				return True
			else:
				return True if TypeToAffectReal(type) != type else False
			#return True if TypeToAffectReal(type) != type else False
			
if app.ENABLE_MULTIFARM_BLOCK:
	class MultiFarmImage(ui.ExpandedImageBox):
		def __del__(self):
			ui.ExpandedImageBox.__del__(self)

		def Destroy(self):
			self.multiFarmStatus = 0
			self.players = []

		def __init__(self):
			ui.ExpandedImageBox.__init__(self)
			self.Destroy()

		def SetMultiFarmInfo(self, multiFarmStatus):
			self.multiFarmStatus = multiFarmStatus
			if multiFarmStatus:
				self.LoadImage("icon/affectshower/farmeron.png")
			else:
				self.LoadImage("icon/affectshower/farmeroff.png")
			self.SetScale(AFFECT_ICON_SCALE, AFFECT_ICON_SCALE)

		def OnMouseOverIn(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.tooltipItem:
				interfaceHandler.tooltipItem.ClearToolTip()
				interfaceHandler.tooltipItem.AutoAppendNewTextLineResize(localeinfo.MULTI_FARM_TITLE + "|cffF1E6C0")
				interfaceHandler.tooltipItem.AppendSpace(5)

				for name in self.players:
					interfaceHandler.tooltipItem.AutoAppendNewTextLineResize("|cffF1E6C0"+name)

				interfaceHandler.tooltipItem.AppendSpace(6)
				interfaceHandler.tooltipItem.AppendShortcutRow(("key_lclick",), localeinfo.MULTI_FARM_TEXT)
				interfaceHandler.tooltipItem.ShowToolTip()

		def OnMouseOverOut(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.tooltipItem:
				interfaceHandler.tooltipItem.HideToolTip()
