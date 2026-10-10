# coding: latin_1

import app
import chr
import player

import dbg
import item
import grp
import wndMgr
import skill
import shop
import exchange
import grpText
import safebox
import localeinfo
import background
import nonplayer
import uiscriptlocale
import ui
import guild
import mousemodule
import constinfo
import chat
import game_data
import re

if app.USE_OFFLINESHOP:
	import uiofflineshop_ae

import osfinfo

if app.ENABLE_LOCATION_SCROLL_REWORK:
	import locationscroll

if app.ENABLE_MISSION_QUEST:
	import missionhelper

if app.USE_ACCE_SYSTEM:
	import acce

if app.ENABLE_DS_SET:
	import uidragonsoul

if app.ENABLE_MAILBOX:
	import mail
if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget
if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
	import offlineshop

# Only read when ENABLE_LOCATION_SCROLL_REWORK is off; the rework detects scrolls by their
# item_proto Value0 instead of by vnum.
WARP_SCROLLS = [22011, 22000, 22010]
BELT_SLOTS = [0, 1, 2, 4, 6, 9, 12, 16]

DESC_DEFAULT_MAX_COLS = 26
DESC_WESTERN_MAX_COLS = 35
DESC_WESTERN_MAX_WIDTH = 220

# Legacy shortcut strings embed their key combo as |E..|e / |I..|i image tags (some
# with plain "Ctrl +" words); the footer renders combos itself, so labels are the
# locale strings with those parts stripped at runtime -- the locale files stay
# byte-identical. Patterns are pure ASCII: safe on CP1256/UTF-8 byte strings.
_SHORTCUT_TAG = r"\|E[^|]*\|e|\|I[^|]*\|i"
_SHORTCUT_KEYWORD = r"\b(?:Alt|Ctrl|Shift|TAB|Tab|[Ll]eft [Cc]lick|[Rr]ight [Cc]lick)\b"
_SHORTCUT_UNIT = "(?:%s|%s)" % (_SHORTCUT_TAG, _SHORTCUT_KEYWORD)
SHORTCUT_COMBO_PATTERN = re.compile(r"%s(?:\s*\+\s*%s)+|%s" % (_SHORTCUT_UNIT, _SHORTCUT_UNIT, _SHORTCUT_TAG))
SHORTCUT_COLOR_PATTERN = re.compile(r"\|c[0-9a-fA-F]{8}|\|r")

def StripShortcutLabel(text):
	text = SHORTCUT_COLOR_PATTERN.sub("", text)
	text = SHORTCUT_COMBO_PATTERN.sub("", text)
	text = re.sub(r"[ \t]{2,}", " ", text).strip()
	while text[:1] in ("-", ":", "+"):
		text = text[1:].lstrip()
	text = re.sub(r"^(?:[Ll]eft [Cc]lick|[Rr]ight [Cc]lick)\s*", "", text)
	while text[:1] in ("-", ":", "+"):
		text = text[1:].lstrip()
	while text[-1:] in ("-", ":", "+"):
		text = text[:-1].rstrip()
	return text

def chop(n):
	return round(n - 0.5, 1)

if app.ENABLE_INGAME_WIKI or\
	app.USE_ITEM_ATTR_BACKUP_MODE or\
	app.__RANKING_SYSTEM__ or\
	app.ENABLE_GUILD_RENEWAL:
	def GET_AFFECT_STRING(affType, affValue):
		if affType == 0:
			return None

		try:
			affectString = ItemToolTip.AFFECT_DICT[affType]

			if type(affectString) != str:
				return affectString(affValue)

			if affectString.find("%d") != -1:
				return affectString % affValue
			else:
				return affectString
		except KeyError:
			return "UNKNOWN_TYPE[%s] %s" % (affType, affValue)

def SplitDescription(desc, limit):
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

# localeinfo is wrapped (system.py LocaleInfoWrapper) and returns the string
# "Locale not found: KEY" instead of raising, so getattr's default never fires on its own.
def LocaleText(key, default):
	value = getattr(localeinfo, key, default)
	if not value or value.startswith("Locale not found"):
		return default

	return value

def AutoChestRemainSeconds(itemVnum):
	deadline = constinfo.AUTO_CHEST_DEADLINES.get(itemVnum, 0)
	if deadline <= 0:
		return 0

	return max(0, deadline - app.GetGlobalTimeStamp())

# Ticks itself instead of overriding ItemToolTip.OnUpdate: HyperlinkItemToolTip
# overrides OnUpdate with pass, so a tooltip-level hook would freeze there.
class AutoChestGauge(ui.Gauge):
	def __init__(self):
		ui.Gauge.__init__(self)
		self.timerLine = None
		self.itemVnum = 0

	def __del__(self):
		ui.Gauge.__del__(self)
		self.timerLine = None

	def SetTimerLine(self, itemVnum, timerLine):
		self.itemVnum = itemVnum
		self.timerLine = timerLine
		self.Refresh()

	def Refresh(self):
		remain = AutoChestRemainSeconds(getattr(self, "itemVnum", 0))
		self.SetPercentage(remain, game_data.autoChestInterval)

		timerLine = getattr(self, "timerLine", None)
		if not timerLine:
			return

		clock = "%d:%02d" % (remain / 60, remain % 60)
		timerLine.SetText(LocaleText("AUTO_CHEST_TT_TIMER", "Auto-open in %s") % clock)

	def OnUpdate(self):
		self.Refresh()

class ToolTip(ui.ThinBoard):
	TOOL_TIP_WIDTH = 190
	TOOL_TIP_HEIGHT = 10

	TEXT_LINE_HEIGHT = 17

	SHORTCUT_ROW_HEIGHT = 20
	SHORTCUT_ROW_GAP = 2
	SHORTCUT_BAR_MARGIN = 8
	SHORTCUT_BAR_PADDING = 6
	SHORTCUT_BAR_COLOR = 0x96000000
	SHORTCUT_LABEL_COLOR = 0xFFE1DEC7
	SHORTCUT_HEADER_COLOR = 0xFF89B88D

	SALES_TITLE_COLOR = grp.GenerateColor(1.0, 0.9686, 0.3098, 1.0)

	TITLE_COLOR = grp.GenerateColor(0.9490, 0.9058, 0.7568, 1.0)
	SPECIAL_TITLE_COLOR = grp.GenerateColor(1.0, 0.7843, 0.0, 1.0)
	NORMAL_COLOR = grp.GenerateColor(0.7607, 0.7607, 0.7607, 1.0)
	FONT_COLOR = grp.GenerateColor(0.7607, 0.7607, 0.7607, 1.0)
	PRICE_COLOR = 0xffFFB96D

	HIGH_PRICE_COLOR = SPECIAL_TITLE_COLOR
	MIDDLE_PRICE_COLOR = grp.GenerateColor(0.85, 0.85, 0.85, 1.0)
	LOW_PRICE_COLOR = grp.GenerateColor(0.7, 0.7, 0.7, 1.0)

	NEW_RED = grp.GenerateColor(211/255.0, 84/255.0, 0/255.0, 1.0)
	NEW_GREEN = grp.GenerateColor(46/255.0, 204/255.0, 113/255.0, 1.0)

	ENABLE_COLOR = grp.GenerateColor(0.7607, 0.7607, 0.7607, 1.0)
	DISABLE_COLOR = grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0)

	NEGATIVE_COLOR = grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0)
	POSITIVE_COLOR = grp.GenerateColor(0.5411, 0.7254, 0.5568, 1.0)
	SPECIAL_POSITIVE_COLOR = grp.GenerateColor(0.6911, 0.8754, 0.7068, 1.0)
	SPECIAL_POSITIVE_COLOR2 = grp.GenerateColor(0.8824, 0.9804, 0.8824, 1.0)
	ITEM_BUFF_LEVEL_COLOR = 0xffffd300
	ITEM_BUFF_TYPE_COLOR = 0xfffc9c3a
	ITEM_BUFF_RATE_COLOR = 0xfff39c12
	ITEM_BUFF_DURATION_COLOR = 0xff16a085
	ITEM_BUFF_USAGE_COLOR = 0xffffffff
	if app.ENABLE_ATTR_6TH_7TH:
		ATTR_6TH_7TH_COLOR = grp.GenerateColor(1.0, 1.0, 0.6078, 1.0)

	SPECIAL_POSITIVE_COLOR_GOLD = 0xffffce9c

	if app.ENABLE_DS_SET:
		TEXTLINE_2ND_COLOR_DEFAULT = grp.GenerateColor(1.0, 1.0, 0.6078, 1.0)

	CONDITION_COLOR = 0xffBEB47D
	TYRANIS_TOOLTIP_COLOR = 0xff5FFFF3

	CAN_LEVEL_UP_COLOR = 0xff8EC292
	CANNOT_LEVEL_UP_COLOR = DISABLE_COLOR
	NEED_SKILL_POINT_COLOR = 0xff9A9CDB

	if app.ENABLE_CHANGE_LOOK_SYSTEM:
		CHANGELOOK_TITLE_COLOR = 0xff8BBDFF
		CHANGELOOK_ITEMNAME_COLOR = 0xffBCE55C

	if app.ENABLE_APPLY_RANDOM:
		APPLY_RANDOM_TEXT_COLOR = 0xff7AF6D4

	if app.ENABLE_INGAME_WIKI:
		NORMAL_WIKI_COLOR = grp.GenerateColor(255/255.0, 218/255.0, 121/255.0, 1.0)
	else:
		NORMAL_WIKI_COLOR = NORMAL_COLOR

	if app.ENABLE_CHEQUE_SYSTEM:
		CHEQUE_COLOR = grp.GenerateColor(0.0, 0.8470, 1.0, 1.0)

	if app.ENABLE_GEM_SYSTEM:
		GEM_COLOR = grp.GenerateColor(0.1, 0.9, 0.8, 1.0)

	def __init__(self, width = TOOL_TIP_WIDTH, isPickable=False):
		ui.ThinBoard.__init__(self, "TOP_MOST")
		if isPickable:
			pass
		else:
			self.AddFlag("not_pick")

		self.AddFlag("float")

		self.followFlag = True
		self.toolTipWidth = width

		self.xPos = -1
		self.yPos = -1

		if app.ENABLE_DS_SET:
			self.window_type = player.INVENTORY

		self.defFontName = localeinfo.UI_DEF_FONT

		if app.USE_MULTIPLE_SHOP_BUY:
			self.multipleBuyDialog = False
			self.multipleBuyCount = 1

		self.ClearToolTip()

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def ClearToolTip(self):
		self.toolTipHeight = 12
		self.childrenList = []
		self.shortcutBars = []
		self.pendingShortcuts = []
		self.shortcutFooterOpen = False
		self.shortcutHeaderShown = False

	def SetFollow(self, flag):
		self.followFlag = flag

	if app.USE_MULTIPLE_SHOP_BUY:
		def SetMultipleBuyDialog(self, flag):
			self.SetFollow(False if flag else True)

			self.multipleBuyDialog = flag
			self.multipleBuyCount = 1

	def SetDefaultFontName(self, fontName):
		self.defFontName = fontName

	def AppendSpace(self, size):
		self.toolTipHeight += size
		self.ResizeToolTip()

	def AppendHorizontalLine(self, x = 0):
		# for i in xrange(2):
			# horizontalLine = ui.Line()
			# horizontalLine.SetParent(self)
			# horizontalLine.SetPosition(x, self.toolTipHeight + 3 + i)
			# horizontalLine.SetWindowHorizontalAlignCenter()
			# horizontalLine.SetWindowHorizontalAlignLeft()
			# horizontalLine.SetSize(150, 0)
			# horizontalLine.Show()

			# if 0 == i:
				# horizontalLine.SetColor(0xff555555)
			# else:
				# horizontalLine.SetColor(0xff000000)

			# self.childrenList.append(horizontalLine)

		self.toolTipHeight += 11
		self.ResizeToolTip()

	def AlignHorizonalCenter(self):
		for child in self.childrenList:
			(x, y) = child.GetLocalPosition()
			child.SetPosition(self.toolTipWidth/2, y)

		self.ResizeToolTip()

	def AlignTextLineHorizonalCenter(self):
		for child in self.childrenList:
			if type(child).__name__ == "TextLine":
				(x, y) = child.GetLocalPosition()
				child.SetPosition(self.toolTipWidth / 2, y)

		self.ResizeToolTip()

	def AutoAppendTextLineAll(self, text, color = FONT_COLOR, centerAlign = True):
		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetFontName(self.defFontName)
		textLine.SetPackedFontColor(color)
		textLine.SetText(text)
		textLine.SetOutline()
		textLine.SetFeather(False)
		textLine.Show()
		if localeinfo.IsARABIC():
			textLine.SetHorizontalAlignRight()

		if centerAlign:
			textLine.SetPosition(self.toolTipWidth/2, self.toolTipHeight)
			textLine.SetHorizontalAlignCenter()
			textLine.shortcutRecenter = True
		else:
			textLine.SetPosition(10, self.toolTipHeight)

		self.childrenList.append(textLine)

		(textWidth, textHeight)=textLine.GetTextSize()

		textWidth += 40
		textHeight += 5

		if self.toolTipWidth < textWidth:
			self.toolTipWidth = textWidth

		self.toolTipHeight += textHeight
		#self.ResizeToolTip()

		return textLine

	#if app.USE_RENEWAL_AFFECT_SHOWER:
	def AutoAppendTextLine(self, text, color = FONT_COLOR, centerAlign = True):
		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetFontName(self.defFontName)
		textLine.SetPackedFontColor(color)
		textLine.SetText(text)
		textLine.SetOutline()
		textLine.SetFeather(False)
		textLine.Show()

		if centerAlign:
			textLine.SetPosition(self.toolTipWidth/2, self.toolTipHeight)
			textLine.SetHorizontalAlignCenter()
			textLine.shortcutRecenter = True
		else:
			textLine.SetPosition(10, self.toolTipHeight)

		self.childrenList.append(textLine)

		(textWidth, textHeight) = textLine.GetTextSize()

		textWidth += 40
		textHeight += 5
		
		if self.toolTipWidth < textWidth:
			self.toolTipWidth = textWidth
		
		self.toolTipHeight += textHeight
		
		return textLine

	def AutoAppendTextLineAE(self, text, color = FONT_COLOR, centerAlign = True):
		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetFontName(self.defFontName)
		textLine.SetPackedFontColor(color)
		textLine.SetText(text)
		textLine.SetOutline()
		textLine.SetFeather(False)
		textLine.Show()

		if centerAlign:
			textLine.SetPosition(self.toolTipWidth/2, self.toolTipHeight)
			textLine.SetHorizontalAlignCenter()
		else:
			textLine.SetPosition(10+170, self.toolTipHeight)

		self.childrenList.append(textLine)

		(textWidth, textHeight)=textLine.GetTextSize()

		textWidth += 40
		textHeight += 5

		if self.toolTipWidth < textWidth:
			self.toolTipWidth = textWidth

		self.toolTipHeight += textHeight

		return textLine


	def AutoAppendNewTextLineResize(self, text, color = FONT_COLOR, centerAlign = True):
		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetFontName(self.defFontName)
		textLine.SetPackedFontColor(color)
		textLine.SetText(text)
		textLine.SetOutline()
		textLine.SetFeather(False)
		textLine.Show()
		
		(textWidth, textHeight) = textLine.GetTextSize()
		textWidth += 30
		textHeight += 10
		if self.toolTipWidth < textWidth:
			self.toolTipWidth = textWidth
		
		if centerAlign:
			textLine.SetPosition(self.toolTipWidth/2, self.toolTipHeight)
			textLine.SetHorizontalAlignCenter()
		else:
			textLine.SetPosition(10, self.toolTipHeight)
		
		self.childrenList.append(textLine)
		
		self.toolTipHeight += self.TEXT_LINE_HEIGHT
		self.AlignHorizonalCenter()
		return textLine
	
	def AutoAppendNewTextLine(self, text,x, color = FONT_COLOR, centerAlign = True):
		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetFontName(self.defFontName)
		textLine.SetPackedFontColor(color)
		textLine.SetText(text)
		textLine.SetOutline()
		textLine.SetFeather(False)
		textLine.Show()
		textLine.SetPosition(x, self.toolTipHeight)
		
		self.childrenList.append(textLine)
		(textWidth, textHeight) = textLine.GetTextSize()
		textWidth += 30
		textHeight += 10
		if self.toolTipWidth < textWidth:
			self.toolTipWidth = textWidth
		
		self.toolTipHeight += textHeight
		self.ResizeToolTipText(textWidth, self.toolTipHeight)
		return textLine

	def SetThinBoardSize(self, width, height = 12):
		self.toolTipWidth = width 
		self.toolTipHeight = height

	def AppendSungmaTextLine(self, text, color = FONT_COLOR, centerAlign = True):
		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetFontName(self.defFontName)
		textLine.SetPackedFontColor(color)
		textLine.SetText(text)
		textLine.SetOutline()
		textLine.SetFeather(False)
		textLine.Show()

		if centerAlign:
			textLine.SetPosition(self.toolTipWidth/2, self.toolTipHeight)
			textLine.SetHorizontalAlignCenter()
		else:
			textLine.SetPosition(10+200, self.toolTipHeight)

		self.childrenList.append(textLine)

		self.toolTipHeight += self.TEXT_LINE_HEIGHT
		self.ResizeToolTip()

		return textLine

	def AppendTextLine(self, text, color = FONT_COLOR, centerAlign = True, resizeWidth = False):
		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetFontName(self.defFontName)
		textLine.SetPackedFontColor(color)
		textLine.SetText(text)
		textLine.SetOutline()
		textLine.SetFeather(False)
		textLine.Show()

		if centerAlign:
			textLine.SetPosition(self.toolTipWidth / 2, self.toolTipHeight)
			textLine.SetHorizontalAlignCenter()
			textLine.shortcutRecenter = True

		else:
			textLine.SetPosition(10, self.toolTipHeight)

		self.childrenList.append(textLine)

		if resizeWidth == True:
			_width = textLine.GetTextWidth() + 20
			if self.toolTipWidth < _width:
				self.toolTipWidth = _width

			if centerAlign == True:
				for _children in self.childrenList:
					_children.SetPosition(self.toolTipWidth / 2, _children.GetLocalPosition()[1])

		self.toolTipHeight += self.TEXT_LINE_HEIGHT
		self.ResizeToolTip()

		return textLine

	if app.ENABLE_DS_SET:
		def AppendTwoColorTextLine(self, text, color, text2, color2 = TEXTLINE_2ND_COLOR_DEFAULT, centerAlign = True):
			textLine = ui.TextLine()
			textLine.SetParent(self)
			textLine.SetFontName(self.defFontName)
			textLine.SetPackedFontColor(color)
			textLine.SetText(text)
			textLine.SetOutline()
			textLine.SetFeather(False)
			w, h = textLine.GetTextSize()

			textLine2 = ui.TextLine()
			textLine2.SetParent(textLine)
			textLine2.SetFontName(self.defFontName)
			textLine2.SetPackedFontColor(color2)
			textLine2.SetText(text2)
			textLine2.SetOutline()
			textLine2.SetFeather(False)
			textLine2.Show()

			w2, h2 = textLine2.GetTextSize()

			textLine.Show()

			if centerAlign:
				if localeinfo.IsARABIC():
					textLine.SetPosition(self.toolTipWidth / 2 + w2 / 2, self.toolTipHeight)
					textLine.SetHorizontalAlignCenter()
					textLine2.SetPosition(-w / 2, 0)
				else:
					textLine.SetPosition(self.toolTipWidth / 2 -w2 / 2, self.toolTipHeight)
					textLine.SetHorizontalAlignCenter()
					textLine2.SetPosition(w / 2, 0)
			else:
				textLine.SetPosition(10, self.toolTipHeight)

			self.childrenList.append(textLine)
			self.childrenList.append(textLine2)

			self.toolTipHeight += self.TEXT_LINE_HEIGHT
			self.ResizeToolTip()

			return textLine

	def AppendDescription(self, desc, limit, color = FONT_COLOR):
		if localeinfo.IsEUROPE():
			self.__AppendDescription_WesternLanguage(desc, color)
		else:
			self.__AppendDescription_EasternLanguage(desc, limit, color)

	def __AppendDescription_EasternLanguage(self, description, characterLimitation, color=FONT_COLOR):
		length = len(description)
		if 0 == length:
			return

		lineCount = grpText.GetSplitingTextLineCount(description, characterLimitation)
		for i in xrange(lineCount):
			if 0 == i:
				self.AppendSpace(5)
			self.AppendTextLine(grpText.GetSplitingTextLine(description, characterLimitation, i), color)

	def __AppendDescription_WesternLanguage(self, desc, color=FONT_COLOR):
		lines = SplitDescription(desc, DESC_WESTERN_MAX_COLS)
		if not lines:
			return

		self.AppendSpace(5)
		for line in lines:
			self.AppendTextLine(line, color)

	def ResizeToolTip(self):
		self.toolTipWidth = int(self.toolTipWidth)   # a float width (leaked from another render) crashes the int-only C++ SetSize
		self.SetSize(self.toolTipWidth, self.TOOL_TIP_HEIGHT + self.toolTipHeight)

		# Bars span the final width, which keeps growing while lines append (and
		# AlignHorizonalCenter re-centers every child, bars included) -- so re-anchor
		# them on every resize instead of sizing them once at append time.
		if self.shortcutBars:
			barWidth = self.toolTipWidth - self.SHORTCUT_BAR_MARGIN * 2
			for bar in self.shortcutBars:
				bar.SetPosition(self.SHORTCUT_BAR_MARGIN, bar.shortcutRowY)
				bar.SetSize(barWidth, self.SHORTCUT_ROW_HEIGHT)
				bar.shortcutLabelLine.SetPosition(barWidth - self.SHORTCUT_BAR_PADDING, self.SHORTCUT_ROW_HEIGHT / 2)

	def AppendShortcutRow(self, keyTokens, label, labelColor = None):
		if labelColor is None:
			labelColor = self.SHORTCUT_LABEL_COLOR
		label = StripShortcutLabel(label)

		bar = ui.Bar()
		bar.SetParent(self)
		bar.AddFlag("not_pick")
		bar.SetColor(self.SHORTCUT_BAR_COLOR)
		bar.shortcutRowY = self.toolTipHeight
		bar.Show()

		# Keycaps are laid out as ImageBoxes with an explicit x cursor: a TextLine of
		# |E tags gets right-anchored on the Arabic client and flows out of the bar.
		keyWidgets = []
		keysX = self.SHORTCUT_BAR_PADDING
		for token in keyTokens:
			if keyWidgets:
				plus = ui.TextLine()
				plus.SetParent(bar)
				plus.AddFlag("not_pick")
				plus.SetFontName(self.defFontName)
				plus.SetPackedFontColor(labelColor)
				plus.SetText("+")
				plus.SetOutline()
				plus.SetFeather(False)
				plus.SetHorizontalAlignCenter()
				plus.SetVerticalAlignCenter()
				plus.SetPosition(int(keysX + 5), self.SHORTCUT_ROW_HEIGHT / 2)
				plus.Show()
				keyWidgets.append(plus)
				keysX += 10

			img = ui.ImageBox()
			img.SetParent(bar)
			img.AddFlag("not_pick")
			img.LoadImage("icon/emoji/%s.png" % token)
			img.SetPosition(int(keysX), int((self.SHORTCUT_ROW_HEIGHT - img.GetHeight()) / 2))
			img.Show()
			keyWidgets.append(img)
			keysX += img.GetWidth() + 2

		labelLine = ui.TextLine()
		labelLine.SetParent(bar)
		labelLine.AddFlag("not_pick")
		labelLine.SetFontName(self.defFontName)
		labelLine.SetPackedFontColor(labelColor)
		labelLine.SetText(label)
		labelLine.SetOutline()
		labelLine.SetFeather(False)
		labelLine.SetVerticalAlignCenter()
		if not localeinfo.IsARABIC():
			# Arabic keeps the default left align: this engine right-anchors Arabic
			# glyphs from the given position (align-right breaks RTL shaping here).
			labelLine.SetHorizontalAlignRight()
		labelLine.Show()

		bar.shortcutKeyWidgets = keyWidgets
		bar.shortcutLabelLine = labelLine

		(labelWidth, labelHeight) = labelLine.GetTextSize()
		neededWidth = int(keysX) + int(labelWidth) + self.SHORTCUT_BAR_MARGIN * 2 + self.SHORTCUT_BAR_PADDING + 12
		if self.toolTipWidth < neededWidth:
			self.toolTipWidth = neededWidth
			for child in self.childrenList:
				if getattr(child, "shortcutRecenter", False):
					child.SetPosition(self.toolTipWidth / 2, child.GetLocalPosition()[1])

		self.childrenList.append(bar)
		self.shortcutBars.append(bar)

		self.toolTipHeight += self.SHORTCUT_ROW_HEIGHT + self.SHORTCUT_ROW_GAP
		self.ResizeToolTip()

	if app.ENABLE_FEATURES_OXEVENT:
		def AppendPlayersDesc(self, name, level, guild, empire, job, date, correct_answers):

			def IsExistKey(name):
				return (job == localeinfo.OXEVENT_TOOLTIP_EMPTY)
				
			if not IsExistKey(job):
				self.ClearToolTip()

				itemImage = ui.ImageBox()
				itemImage.SetParent(self)
				itemImage.LoadImage(job)
				itemImage.SetPosition(itemImage.GetWidth()/2 + 50, self.toolTipHeight)
				itemImage.Show()

				self.mainDescription = [
					name,
					level,
					guild,
					empire,
					date,
					correct_answers
				]			
						
				self.AppendSpace(50)	
				for i in xrange(len(self.mainDescription)):
					self.AppendTextLine(self.mainDescription[i], self.SPECIAL_POSITIVE_COLOR)

				self.toolTipHeight += 16
				self.childrenList.append(itemImage)
				self.ResizeToolTip()
			else:
				self.HideToolTip()

	def ResizeToolTipX(self, x):
		self.SetSize(x, self.TOOL_TIP_HEIGHT + self.toolTipHeight)

	def ResizeToolTipText(self, x, y):
		self.SetSize(x, y)

	def SetTitle(self, name):
		self.AppendTextLine(name, self.TITLE_COLOR)

	def GetLimitTextLineColor(self, curValue, limitValue):
		if curValue < limitValue:
			return self.DISABLE_COLOR

		return self.ENABLE_COLOR

	def GetMaxLimitTextLineColor(self, PlayerLv, limitValue):
		if PlayerLv <= limitValue:
			return self.ENABLE_COLOR

		return self.DISABLE_COLOR

	def GetChangeTextLineColor(self, value, isSpecial=False):
		if value > 0:
			if isSpecial:
				return self.SPECIAL_POSITIVE_COLOR
			else:
				return self.POSITIVE_COLOR

		if 0 == value:
			return self.NORMAL_COLOR

		return self.NEGATIVE_COLOR

	def SetToolTipPosition(self, x = -1, y = -1):
		self.xPos = x
		self.yPos = y

	def ShowToolTip(self):
		self.SetTop()
		self.Show()

		self.OnUpdate()

	def HideToolTip(self):
		self.Hide()

	if app.ENABLE_EXPRESSING_EMOTION:
		def AppendLastTime(self, endTime):
			leftSec = max(0, endTime - app.GetGlobalTimeStamp())
			if leftSec > 0:
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(leftSec), self.NORMAL_COLOR)

	def OnUpdate(self):
		if not self.followFlag:
			return

		x = 0
		y = 0
		width = self.GetWidth()
		height = self.toolTipHeight

		if -1 == self.xPos and -1 == self.yPos:
			(mouseX, mouseY) = wndMgr.GetMousePosition()

			if mouseY < wndMgr.GetScreenHeight() - 300:
				y = mouseY + 40
			else:
				y = mouseY - height - 30

			x = mouseX - width/2

		else:
			x = self.xPos - width/2
			y = self.yPos - height

		x = max(x, 0)
		y = max(y, 0)
		x = min(x + width/2, wndMgr.GetScreenWidth() - width/2) - width/2
		y = min(y + self.GetHeight(), wndMgr.GetScreenHeight()) - self.GetHeight()

		parentWindow = self.GetParentProxy()
		if parentWindow:
			(gx, gy) = parentWindow.GetGlobalPosition()
			x -= gx
			y -= gy

		self.SetPosition(x, y)

class RichItemToolTip(ToolTip):
	"""
	A rich tooltip that displays an item icon with a title and multiple description lines.
	Used for features like Battle Pass EXP Boost button.

	Layout:
	+----------------------------------+
	| [Title Text - Centered]          |
	| -------------------------------- |
	| [Icon] Description line 1        |
	|        Description line 2        |
	|        Description line 3        |
	| -------------------------------- |
	| [Footer Text - Centered]         |
	+----------------------------------+
	"""

	ICON_SIZE = 32
	ICON_PADDING_LEFT = 10
	ICON_PADDING_TOP = 8
	TEXT_PADDING_LEFT = 48  # ICON_PADDING_LEFT + ICON_SIZE + 6
	TEXT_LINE_HEIGHT = 15

	TITLE_COLOR = grp.GenerateColor(0.95, 0.95, 0.95, 1.0)  # Clean white
	DESC_COLOR = grp.GenerateColor(0.75, 0.82, 0.88, 1.0)  # Soft blue-gray
	HIGHLIGHT_COLOR = grp.GenerateColor(0.4, 0.8, 0.95, 1.0)  # Cyan/Sky blue
	FOOTER_COLOR = grp.GenerateColor(0.55, 0.6, 0.65, 1.0)  # Muted gray

	def __init__(self, width=220):
		# Initialize attributes BEFORE calling parent __init__
		# because parent calls ClearToolTip() which accesses these
		self.itemIcon = None
		self.itemVnum = 0
		self.titleText = None
		self.descLines = []
		self.footerText = None
		ToolTip.__init__(self, width)

	def __del__(self):
		self.ClearToolTip()
		ToolTip.__del__(self)

	def ClearToolTip(self):
		if hasattr(self, 'itemIcon') and self.itemIcon:
			self.itemIcon.Hide()
			self.itemIcon = None
		self.titleText = None
		self.descLines = []
		self.footerText = None
		ToolTip.ClearToolTip(self)

	def GetIconXPosition(self):
		"""Get the X position for the icon - centered horizontally"""
		return (self.toolTipWidth - self.ICON_SIZE) / 2

	def SetItemIcon(self, itemVnum):
		"""Set the item icon by vnum"""
		self.itemVnum = itemVnum

		if self.itemIcon:
			self.itemIcon.Hide()
			self.itemIcon = None

		item.SelectItem(itemVnum)
		iconPath = item.GetIconImageFileName()

		if iconPath:
			self.itemIcon = ui.ImageBox()
			self.itemIcon.SetParent(self)
			self.itemIcon.LoadImage(iconPath)
			self.itemIcon.SetPosition(self.GetIconXPosition(), self.toolTipHeight + self.ICON_PADDING_TOP)
			self.itemIcon.Show()
			self.childrenList.append(self.itemIcon)

	def SetIconImage(self, iconPath):
		"""Set the icon by direct image path"""
		if self.itemIcon:
			self.itemIcon.Hide()
			self.itemIcon = None

		if iconPath:
			self.itemIcon = ui.ImageBox()
			self.itemIcon.SetParent(self)
			self.itemIcon.LoadImage(iconPath)
			self.itemIcon.SetPosition(self.GetIconXPosition(), self.toolTipHeight + self.ICON_PADDING_TOP)
			self.itemIcon.Show()
			self.childrenList.append(self.itemIcon)

	def SetTitle(self, text, color=None):
		"""Set the title text (centered at top)"""
		if color is None:
			color = self.TITLE_COLOR
		self.AppendTextLine(text, color, True)

	def AppendDescriptionLine(self, text, color=None, indent=True):
		"""Add a centered description line"""
		if color is None:
			color = self.DESC_COLOR

		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetFontName(self.defFontName)
		textLine.SetPackedFontColor(color)
		textLine.SetText(text)
		textLine.SetOutline()
		textLine.SetFeather(False)
		textLine.Show()

		# Center the text
		textLine.SetHorizontalAlignCenter()
		textLine.SetPosition(self.toolTipWidth / 2, self.toolTipHeight)

		self.childrenList.append(textLine)
		self.descLines.append(textLine)

		self.toolTipHeight += self.TEXT_LINE_HEIGHT
		return textLine

	def AppendFooter(self, text, color=None):
		"""Add footer text (centered at bottom)"""
		if color is None:
			color = self.FOOTER_COLOR
		self.AppendSpace(3)
		self.AppendHorizontalLine()
		self.footerText = self.AppendTextLine(text, color, True)
		return self.footerText

	def ResizeToolTip(self):
		"""Override to reposition centered elements when width changes"""
		ToolTip.ResizeToolTip(self)
		centerX = self.toolTipWidth / 2

		# Reposition centered icon
		if self.itemIcon:
			currentPos = self.itemIcon.GetLocalPosition()
			self.itemIcon.SetPosition(self.GetIconXPosition(), currentPos[1])

		# Reposition centered description lines
		for textLine in self.descLines:
			if textLine:
				currentPos = textLine.GetLocalPosition()
				textLine.SetPosition(centerX, currentPos[1])

	def AddItemWithDescription(self, itemVnum, title, descriptions, footer=None):
		"""
		Convenience method to set up the entire tooltip at once.
		Icon is centered, followed by space, then centered description lines.

		Args:
			itemVnum: Item VNUM for the icon
			title: Title text displayed at top
			descriptions: List of (text, color) tuples or just strings
			footer: Optional footer text
		"""
		self.ClearToolTip()

		# Title
		self.SetTitle(title)
		self.AppendHorizontalLine()

		# Set up icon position (centered)
		iconStartY = self.toolTipHeight
		self.SetItemIcon(itemVnum)

		# Position icon centered
		if self.itemIcon:
			self.itemIcon.SetPosition(self.GetIconXPosition(), iconStartY + 4)

		# Add space after icon for visual separation
		self.toolTipHeight = iconStartY + self.ICON_SIZE + 16  # Icon height + spacing

		# Add description lines (centered)
		for desc in descriptions:
			if isinstance(desc, tuple):
				text, color = desc
			else:
				text = desc
				color = self.DESC_COLOR
			self.AppendDescriptionLine(text, color, indent=False)

		# Footer
		if footer:
			self.AppendFooter(footer)

		self.ResizeToolTip()

	def AddIconWithDescription(self, iconPath, title, descriptions, footer=None):
		"""
		Same as AddItemWithDescription but uses a direct image path instead of vnum.
		Icon is centered, followed by space, then centered description lines.
		"""
		self.ClearToolTip()

		# Title
		self.SetTitle(title)
		self.AppendHorizontalLine()

		# Set up icon position (centered)
		iconStartY = self.toolTipHeight
		self.SetIconImage(iconPath)

		# Position icon centered
		if self.itemIcon:
			self.itemIcon.SetPosition(self.GetIconXPosition(), iconStartY + 4)

		# Add space after icon for visual separation
		self.toolTipHeight = iconStartY + self.ICON_SIZE + 16  # Icon height + spacing

		# Add description lines (centered, no indent needed since icon is above)
		for desc in descriptions:
			if isinstance(desc, tuple):
				text, color = desc
			else:
				text = desc
				color = self.DESC_COLOR
			self.AppendDescriptionLine(text, color, indent=False)

		# Footer
		if footer:
			self.AppendFooter(footer)

		self.ResizeToolTip()

if app.ENABLE_PRIVATE_INSTANCE_LOBBY:
	# Private-instance "summon" items -> the metin stone race they spawn, plus a
	# recommended level. MUST stay in sync with the server CHAOS_ITEMS[] table in
	# srcs/server/game/private_instance_lobby.cpp (hardcoded by design).
	#   item vnum : (stone race vnum, recommended level)
	CHAOS_SUMMON_ITEMS = {
		90600: (8700, 35),
		90601: (8701, 45),
		90602: (8702, 60),
		90603: (8703, 70),
		90604: (8704, 80),
		90605: (8705, 90),
		90606: (8706, 105),
	}
	CHAOS_PREVIEW_W = 120
	CHAOS_PREVIEW_H = 140

class ItemToolTip(ToolTip):
	if not app.DISABLE_WOLFMAN_CREATION:
		CHARACTER_NAMES = (
			localeinfo.TOOLTIP_WARRIOR,
			localeinfo.TOOLTIP_ASSASSIN,
			localeinfo.TOOLTIP_SURA,
			localeinfo.TOOLTIP_SHAMAN,
			localeinfo.TOOLTIP_WOLFMAN
		)
	else:
		CHARACTER_NAMES = (
			localeinfo.TOOLTIP_WARRIOR,
			localeinfo.TOOLTIP_ASSASSIN,
			localeinfo.TOOLTIP_SURA,
			localeinfo.TOOLTIP_SHAMAN,
		)

	CHARACTER_COUNT = len(CHARACTER_NAMES)
	WEAR_NAMES = ( 
		localeinfo.TOOLTIP_ARMOR, 
		localeinfo.TOOLTIP_HELMET, 
		localeinfo.TOOLTIP_SHOES, 
		localeinfo.TOOLTIP_WRISTLET, 
		localeinfo.TOOLTIP_WEAPON, 
		localeinfo.TOOLTIP_NECK,
		localeinfo.TOOLTIP_EAR,
		localeinfo.TOOLTIP_UNIQUE,
		localeinfo.TOOLTIP_SHIELD,
		localeinfo.TOOLTIP_ARROW,
	)

	if app.USE_GLOVE_SYSTEM:
		WEAR_NAMES += (localeinfo.TOOLTIP_GLOVE,)

	WEAR_COUNT = len(WEAR_NAMES)

	AFFECT_DICT = {
		item.APPLY_MAX_HP : localeinfo.TOOLTIP_MAX_HP,
		item.APPLY_MAX_SP : localeinfo.TOOLTIP_MAX_SP,
		item.APPLY_CON : localeinfo.TOOLTIP_CON,
		item.APPLY_INT : localeinfo.TOOLTIP_INT,
		item.APPLY_STR : localeinfo.TOOLTIP_STR,
		item.APPLY_DEX : localeinfo.TOOLTIP_DEX,
		item.APPLY_ATT_SPEED : localeinfo.TOOLTIP_ATT_SPEED,
		item.APPLY_MOV_SPEED : localeinfo.TOOLTIP_MOV_SPEED,
		item.APPLY_CAST_SPEED : localeinfo.TOOLTIP_CAST_SPEED,
		item.APPLY_HP_REGEN : localeinfo.TOOLTIP_HP_REGEN,
		item.APPLY_SP_REGEN : localeinfo.TOOLTIP_SP_REGEN,
		item.APPLY_POISON_PCT : localeinfo.TOOLTIP_APPLY_POISON_PCT,
		item.APPLY_STUN_PCT : localeinfo.TOOLTIP_APPLY_STUN_PCT,
		item.APPLY_SLOW_PCT : localeinfo.TOOLTIP_APPLY_SLOW_PCT,
		item.APPLY_CRITICAL_PCT : localeinfo.TOOLTIP_APPLY_CRITICAL_PCT,
		item.APPLY_PENETRATE_PCT : localeinfo.TOOLTIP_APPLY_PENETRATE_PCT,
		
		item.APPLY_ATTBONUS_WARRIOR : localeinfo.TOOLTIP_APPLY_ATTBONUS_WARRIOR,
		item.APPLY_ATTBONUS_ASSASSIN : localeinfo.TOOLTIP_APPLY_ATTBONUS_ASSASSIN,
		item.APPLY_ATTBONUS_SURA : localeinfo.TOOLTIP_APPLY_ATTBONUS_SURA,
		item.APPLY_ATTBONUS_SHAMAN : localeinfo.TOOLTIP_APPLY_ATTBONUS_SHAMAN,
		item.APPLY_ATTBONUS_MONSTER : localeinfo.TOOLTIP_APPLY_ATTBONUS_MONSTER,
		
		item.APPLY_ATTBONUS_HUMAN : localeinfo.TOOLTIP_APPLY_ATTBONUS_HUMAN,
		item.APPLY_ATTBONUS_ANIMAL : localeinfo.TOOLTIP_APPLY_ATTBONUS_ANIMAL,
		item.APPLY_ATTBONUS_ORC : localeinfo.TOOLTIP_APPLY_ATTBONUS_ORC,
		item.APPLY_ATTBONUS_MILGYO : localeinfo.TOOLTIP_APPLY_ATTBONUS_MILGYO,
		item.APPLY_ATTBONUS_UNDEAD : localeinfo.TOOLTIP_APPLY_ATTBONUS_UNDEAD,
		item.APPLY_ATTBONUS_DEVIL : localeinfo.TOOLTIP_APPLY_ATTBONUS_DEVIL,
		item.APPLY_STEAL_HP : localeinfo.TOOLTIP_APPLY_STEAL_HP,
		item.APPLY_STEAL_SP : localeinfo.TOOLTIP_APPLY_STEAL_SP,
		item.APPLY_MANA_BURN_PCT : localeinfo.TOOLTIP_APPLY_MANA_BURN_PCT,
		item.APPLY_DAMAGE_SP_RECOVER : localeinfo.TOOLTIP_APPLY_DAMAGE_SP_RECOVER,
		item.APPLY_BLOCK : localeinfo.TOOLTIP_APPLY_BLOCK,
		item.APPLY_DODGE : localeinfo.TOOLTIP_APPLY_DODGE,
		item.APPLY_RESIST_SWORD : localeinfo.TOOLTIP_APPLY_RESIST_SWORD,
		item.APPLY_RESIST_TWOHAND : localeinfo.TOOLTIP_APPLY_RESIST_TWOHAND,
		item.APPLY_RESIST_DAGGER : localeinfo.TOOLTIP_APPLY_RESIST_DAGGER,
		item.APPLY_RESIST_BELL : localeinfo.TOOLTIP_APPLY_RESIST_BELL,
		item.APPLY_RESIST_FAN : localeinfo.TOOLTIP_APPLY_RESIST_FAN,
		item.APPLY_RESIST_BOW : localeinfo.TOOLTIP_RESIST_BOW,
		item.APPLY_RESIST_FIRE : localeinfo.TOOLTIP_RESIST_FIRE,
		item.APPLY_RESIST_ELEC : localeinfo.TOOLTIP_RESIST_ELEC,
		item.APPLY_RESIST_MAGIC : localeinfo.TOOLTIP_RESIST_MAGIC,
		item.APPLY_RESIST_WIND : localeinfo.TOOLTIP_APPLY_RESIST_WIND,
		item.APPLY_REFLECT_MELEE : localeinfo.TOOLTIP_APPLY_REFLECT_MELEE,
		item.APPLY_REFLECT_CURSE : localeinfo.TOOLTIP_APPLY_REFLECT_CURSE,
		item.APPLY_POISON_REDUCE : localeinfo.TOOLTIP_APPLY_POISON_REDUCE,
		item.APPLY_KILL_SP_RECOVER : localeinfo.TOOLTIP_APPLY_KILL_SP_RECOVER,
		item.APPLY_EXP_DOUBLE_BONUS : localeinfo.TOOLTIP_APPLY_EXP_DOUBLE_BONUS,
		item.APPLY_GOLD_DOUBLE_BONUS : localeinfo.TOOLTIP_APPLY_GOLD_DOUBLE_BONUS,
		item.APPLY_ITEM_DROP_BONUS : localeinfo.TOOLTIP_APPLY_ITEM_DROP_BONUS,
		item.APPLY_POTION_BONUS : localeinfo.TOOLTIP_APPLY_POTION_BONUS,
		item.APPLY_KILL_HP_RECOVER : localeinfo.TOOLTIP_APPLY_KILL_HP_RECOVER,
		item.APPLY_IMMUNE_STUN : localeinfo.TOOLTIP_APPLY_IMMUNE_STUN,
		item.APPLY_IMMUNE_SLOW : localeinfo.TOOLTIP_APPLY_IMMUNE_SLOW,
		item.APPLY_IMMUNE_FALL : localeinfo.TOOLTIP_APPLY_IMMUNE_FALL,
		item.APPLY_BOW_DISTANCE : localeinfo.TOOLTIP_BOW_DISTANCE,
		item.APPLY_DEF_GRADE_BONUS : localeinfo.TOOLTIP_DEF_GRADE,
		item.APPLY_ATT_GRADE_BONUS : localeinfo.TOOLTIP_ATT_GRADE,
		item.APPLY_MAGIC_ATT_GRADE : localeinfo.TOOLTIP_MAGIC_ATT_GRADE,
		item.APPLY_MAGIC_DEF_GRADE : localeinfo.TOOLTIP_MAGIC_DEF_GRADE,
		item.APPLY_MAX_STAMINA : localeinfo.TOOLTIP_MAX_STAMINA,
		item.APPLY_MALL_ATTBONUS : localeinfo.TOOLTIP_MALL_ATTBONUS,
		item.APPLY_MALL_DEFBONUS : localeinfo.TOOLTIP_MALL_DEFBONUS,
		item.APPLY_MALL_EXPBONUS : localeinfo.TOOLTIP_MALL_EXPBONUS,
		item.APPLY_MALL_ITEMBONUS : localeinfo.TOOLTIP_MALL_ITEMBONUS,
		item.APPLY_MALL_GOLDBONUS : localeinfo.TOOLTIP_MALL_GOLDBONUS,
		item.APPLY_SKILL_DAMAGE_BONUS : localeinfo.TOOLTIP_SKILL_DAMAGE_BONUS,
		item.APPLY_NORMAL_HIT_DAMAGE_BONUS : localeinfo.TOOLTIP_NORMAL_HIT_DAMAGE_BONUS,
		item.APPLY_SKILL_DEFEND_BONUS : localeinfo.TOOLTIP_SKILL_DEFEND_BONUS,
		item.APPLY_NORMAL_HIT_DEFEND_BONUS : localeinfo.TOOLTIP_NORMAL_HIT_DEFEND_BONUS,
		item.APPLY_PC_BANG_EXP_BONUS : localeinfo.TOOLTIP_MALL_EXPBONUS_P_STATIC,
		item.APPLY_PC_BANG_DROP_BONUS : localeinfo.TOOLTIP_MALL_ITEMBONUS_P_STATIC,
		item.APPLY_RESIST_WARRIOR : localeinfo.TOOLTIP_APPLY_RESIST_WARRIOR,
		item.APPLY_RESIST_ASSASSIN : localeinfo.TOOLTIP_APPLY_RESIST_ASSASSIN,
		item.APPLY_RESIST_SURA : localeinfo.TOOLTIP_APPLY_RESIST_SURA,
		item.APPLY_RESIST_SHAMAN : localeinfo.TOOLTIP_APPLY_RESIST_SHAMAN,
		item.APPLY_MAX_HP_PCT : localeinfo.TOOLTIP_APPLY_MAX_HP_PCT,
		item.APPLY_MAX_SP_PCT : localeinfo.TOOLTIP_APPLY_MAX_SP_PCT,
		item.APPLY_ENERGY : localeinfo.TOOLTIP_ENERGY,
		item.APPLY_COSTUME_ATTR_BONUS : localeinfo.TOOLTIP_COSTUME_ATTR_BONUS,
		
		item.APPLY_MAGIC_ATTBONUS_PER : localeinfo.TOOLTIP_MAGIC_ATTBONUS_PER,
		item.APPLY_MELEE_MAGIC_ATTBONUS_PER : localeinfo.TOOLTIP_MELEE_MAGIC_ATTBONUS_PER,
		item.APPLY_RESIST_ICE : localeinfo.TOOLTIP_RESIST_ICE,
		item.APPLY_RESIST_EARTH : localeinfo.TOOLTIP_RESIST_EARTH,
		item.APPLY_RESIST_DARK : localeinfo.TOOLTIP_RESIST_DARK,
		item.APPLY_ANTI_CRITICAL_PCT : localeinfo.TOOLTIP_ANTI_CRITICAL_PCT,
		item.APPLY_ANTI_PENETRATE_PCT : localeinfo.TOOLTIP_ANTI_PENETRATE_PCT,
	}

	if not app.DISABLE_WOLFMAN_CREATION:
		AFFECT_DICT[item.APPLY_BLEEDING_PCT] = localeinfo.TOOLTIP_APPLY_BLEEDING_PCT
		AFFECT_DICT[item.APPLY_BLEEDING_REDUCE] = localeinfo.TOOLTIP_APPLY_BLEEDING_REDUCE
		AFFECT_DICT[item.APPLY_ATTBONUS_WOLFMAN] = localeinfo.TOOLTIP_APPLY_ATTBONUS_WOLFMAN
		AFFECT_DICT[item.APPLY_RESIST_WOLFMAN] = localeinfo.TOOLTIP_APPLY_RESIST_WOLFMAN
		AFFECT_DICT[item.APPLY_RESIST_CLAW] = localeinfo.TOOLTIP_APPLY_RESIST_CLAW
	
	if app.ENABLE_MAGIC_REDUCTION:
		AFFECT_DICT[item.APPLY_RESIST_MAGIC_REDUCTION] = localeinfo.TOOLTIP_RESIST_MAGIC_REDUCTION

	# AFFECT_DICT[item.APPLY_ACCEDRAIN_RATE] = localeinfo.TOOLTIP_APPLY_ACCEDRAIN_RATE

	if app.ENABLE_ELEMENT_ADD:
		AFFECT_DICT[item.APPLY_ENCHANT_ELEC] = localeinfo.TOOLTIP_APPLY_ENCHANT_ELECT
		AFFECT_DICT[item.APPLY_ENCHANT_FIRE] = localeinfo.TOOLTIP_APPLY_ENCHANT_FIRE
		AFFECT_DICT[item.APPLY_ENCHANT_ICE] = localeinfo.TOOLTIP_APPLY_ENCHANT_ICE
		AFFECT_DICT[item.APPLY_ENCHANT_WIND] = localeinfo.TOOLTIP_APPLY_ENCHANT_WIND
		AFFECT_DICT[item.APPLY_ENCHANT_EARTH] = localeinfo.TOOLTIP_APPLY_ENCHANT_EARTH
		AFFECT_DICT[item.APPLY_ENCHANT_DARK] = localeinfo.TOOLTIP_APPLY_ENCHANT_DARK
		AFFECT_DICT[item.APPLY_ATTBONUS_CZ] = localeinfo.TOOLTIP_APPLY_ATTBONUS_CZ
		AFFECT_DICT[item.APPLY_ATTBONUS_INSECT] = localeinfo.TOOLTIP_APPLY_ATTBONUS_INSECT
		AFFECT_DICT[item.APPLY_ATTBONUS_DESERT] = localeinfo.TOOLTIP_APPLY_ATTBONUS_DESERT

		AFFECT_DICT[item.APPLY_RESIST_SWORD_REDUCTION] = localeinfo.TOOLTIP_APPLY_ATTBONUS_SWORD
		AFFECT_DICT[item.APPLY_RESIST_TWOHAND_REDUCTION]= localeinfo.TOOLTIP_APPLY_ATTBONUS_TWOHAND
		AFFECT_DICT[item.APPLY_RESIST_DAGGER_REDUCTION] = localeinfo.TOOLTIP_APPLY_ATTBONUS_DAGGER
		AFFECT_DICT[item.APPLY_RESIST_BELL_REDUCTION] = localeinfo.TOOLTIP_APPLY_ATTBONUS_BELL
		AFFECT_DICT[item.APPLY_RESIST_FAN_REDUCTION] = localeinfo.TOOLTIP_APPLY_ATTBONUS_FAN
		AFFECT_DICT[item.APPLY_RESIST_BOW_REDUCTION] = localeinfo.TOOLTIP_APPLY_ATTBONUS_BOW
		if not app.DISABLE_WOLFMAN_CREATION:
			AFFECT_DICT[item.APPLY_RESIST_CLAW_REDUCTION] = localeinfo.TOOLTIP_APPLY_ATTBONUS_CLAW
		AFFECT_DICT[item.APPLY_RESIST_HUMAN] = localeinfo.TOOLTIP_APPLY_RESIST_HUMAN
	AFFECT_DICT[item.APPLY_ATTBONUS_STONE] = localeinfo.TOOLTIP_ATTBONUS_STONE
	AFFECT_DICT[item.APPLY_ATTBONUS_BOSS] = localeinfo.TOOLTIP_ATTBONUS_BOSS
	# AFFECT_DICT[item.APPLY_RESIST_BOSS] = localeinfo.TOOLTIP_RESIST_BOSS
	AFFECT_DICT[item.APPLY_ATTBONUS_MEDI_PVM] = localeinfo.TOOLTIP_ATTBONUS_MEDI_PVM
	AFFECT_DICT[item.APPLY_RESIST_MONSTER] = localeinfo.TOOLTIP_RESIST_MONSTER
	#AFFECT_DICT[item.APPLY_PVM_CRITICAL_PCT] = localeinfo.TOOLTIP_PVM_CRITICAL_PCT

	if app.NEW_PVP_BONUSES:
		AFFECT_DICT[item.APPLY_ATTBONUS_PLAYERS] = localeinfo.TOOLTIP_ATTBONUS_PLAYERS
		AFFECT_DICT[item.APPLY_RESIST_PLAYERS] = localeinfo.TOOLTIP_RESIST_PLAYERS

	if app.ENABLE_ATTR_6TH_7TH_EXTEND:
		AFFECT_DICT[item.APPLY_NORMAL_HIT_DEFEND_BONUS_BOSS_OR_MORE] = localeinfo.TOOLTIP_NORMAL_HIT_DEFEND_BONUS_BOSS_OR_MORE
		AFFECT_DICT[item.APPLY_SKILL_DEFEND_BONUS_BOSS_OR_MORE] = localeinfo.TOOLTIP_SKILL_DEFEND_BONUS_BOSS_OR_MORE
		AFFECT_DICT[item.APPLY_NORMAL_HIT_DAMAGE_BONUS_BOSS_OR_MORE] = localeinfo.TOOLTIP_NORMAL_HIT_DAMAGE_BONUS_BOSS_OR_MORE
		AFFECT_DICT[item.APPLY_SKILL_DAMAGE_BONUS_BOSS_OR_MORE] = localeinfo.TOOLTIP_SKILL_DAMAGE_BONUS_BOSS_OR_MORE
		AFFECT_DICT[item.APPLY_FIRST_ATTRIBUTE_BONUS] = localeinfo.TOOLTIP_FIRST_ATTRIBUTE_BONUS
		AFFECT_DICT[item.APPLY_SECOND_ATTRIBUTE_BONUS] = localeinfo.TOOLTIP_SECOND_ATTRIBUTE_BONUS
		AFFECT_DICT[item.APPLY_THIRD_ATTRIBUTE_BONUS] = localeinfo.TOOLTIP_THIRD_ATTRIBUTE_BONUS
		AFFECT_DICT[item.APPLY_FOURTH_ATTRIBUTE_BONUS] = localeinfo.TOOLTIP_FOURTH_ATTRIBUTE_BONUS
		AFFECT_DICT[item.APPLY_FIFTH_ATTRIBUTE_BONUS] = localeinfo.TOOLTIP_FIFTH_ATTRIBUTE_BONUS

	AFFECT_DICT[item.APPLY_RESIST_ZC] = localeinfo.TOOLTIP_RESIST_ZC_TOOLTIP



	if app.ENABLE_CONQUEROR_LEVEL:
		AFFECT_DICT[item.APPLY_SUNGMA_STR] = localeinfo.TOOLTIP_SUNGMA_STR
		AFFECT_DICT[item.APPLY_SUNGMA_HP] = localeinfo.TOOLTIP_SUNGMA_HP
		AFFECT_DICT[item.APPLY_SUNGMA_MOVE] = localeinfo.TOOLTIP_SUNGMA_MOVE
		AFFECT_DICT[item.APPLY_SUNGMA_IMMUNE] = localeinfo.TOOLTIP_SUNGMA_IMMUNE

	if app.ENABLE_ELEMENT_ADD:
		AFFECT_DICT[item.APPLY_ELEMENTS] = getattr(localeinfo, "TOOLTIP_ELEMENTS", localeinfo.SA("Strength against all Elements +%d%%"))
	AFFECT_DICT[item.APPLY_BOSS_STONE] = getattr(localeinfo, "TOOLTIP_BOSS_STONE", localeinfo.SA("+%d%% strength against Metin Stones and Bosses"))
	AFFECT_DICT[item.APPLY_ATTBOUNS_AS_SU] = getattr(localeinfo, "TOOLTIP_ATTBOUNS_AS_SU", localeinfo.SA("+%d%% strength against Assassin and Sura"))
	AFFECT_DICT[item.APPLY_ATTBOUNS_WA_SH] = getattr(localeinfo, "TOOLTIP_ATTBOUNS_WA_SH", localeinfo.SA("+%d%% strength against Warrior and Shaman"))
	AFFECT_DICT[item.APPLY_RESIST_AS_SU] = getattr(localeinfo, "TOOLTIP_RESIST_AS_SU", localeinfo.SA("Defence against Assassin and Sura +%d%%"))
	AFFECT_DICT[item.APPLY_RESIST_WA_SH] = getattr(localeinfo, "TOOLTIP_RESIST_WA_SH", localeinfo.SA("Defence against Warrior and Shaman +%d%%"))
	AFFECT_DICT[item.APPLY_HIT_PCT] = localeinfo.TOOLTIP_HIT_PCT
	#if app.USE_RENEWAL_AFFECT_SHOWER:
	POINT_DICT = {item.GetApplyPoint(affect): name for affect, name in AFFECT_DICT.items()}
	# 99 = POINT_RESIST_NORMAL_DAMAGE: no item APPLY maps to it, so the comprehension above never adds it
	POINT_DICT[99] = getattr(localeinfo, "TOOLTIP_APPLY_RESIST_NORMAL", localeinfo.SA("Resistance against Body Damage +%d%%"))

	ATTRIBUTE_NEED_WIDTH = {
		16 : 230,
		23 : 270,
		24 : 230,
		25 : 230,
		26 : 220,
		27 : 280,

		35 : 210,
		36 : 210,
		37 : 210,
		38 : 210,
		39 : 210,
		40 : 210,
		41 : 210,

		42 : 220,
		43 : 230,
		45 : 230,
		78 : 255,
	}

	if not app.DISABLE_WOLFMAN_CREATION:
		ANTI_FLAG_DICT = {
			0 : item.ITEM_ANTIFLAG_WARRIOR,
			1 : item.ITEM_ANTIFLAG_ASSASSIN,
			2 : item.ITEM_ANTIFLAG_SURA,
			3 : item.ITEM_ANTIFLAG_SHAMAN,
			4 : item.ITEM_ANTIFLAG_WOLFMAN,
		}
	else:
		ANTI_FLAG_DICT = {
			0 : item.ITEM_ANTIFLAG_WARRIOR,
			1 : item.ITEM_ANTIFLAG_ASSASSIN,
			2 : item.ITEM_ANTIFLAG_SURA,
			3 : item.ITEM_ANTIFLAG_SHAMAN,
		}

	FONT_COLOR = grp.GenerateColor(0.7607, 0.7607, 0.7607, 1.0)

	def __init__(self, *args, **kwargs):
		ToolTip.__init__(self, *args, **kwargs)
		self.itemVnum = 0
		self.metinSlot = []
		self.isShopItem = False
		self.isShopItemNpc = False
		
		if app.ENABLE_12ZI:
			self.ShopSlotIndex = 0

		if app.ENABLE_DS_SET:
			self.interface = None
		
		if app.USE_OFFLINESHOP:
			self.isOfflineShopItem = 0
		
		self.bCannotUseItemForceSetDisableColor = True

		if app.ENABLE_PRIVATE_INSTANCE_LOBBY:
			# The stone preview is a CHILD of this tooltip (SetParent), so it hides with it
			# on every path - including the many callers that use plain .Hide().
			self.chaosStoneModel = None
			self.chaosBuilt = False

	def __del__(self):
		ToolTip.__del__(self)
		self.metinSlot = None

	if app.ENABLE_PRIVATE_INSTANCE_LOBBY:
		# every AddItemData path ends at ShowToolTip and sets self.itemVnum first, so this
		# is the one hook that covers inventory/shop/safebox/hyperlink. ClearToolTip resets
		# chaosBuilt, so a re-show without a rebuild cannot append the block twice.
		def ShowToolTip(self):
			if not self.chaosBuilt:
				self.__AppendChaosStone()
				self.chaosBuilt = True
			ToolTip.ShowToolTip(self)

		def __AppendChaosStone(self):
			info = CHAOS_SUMMON_ITEMS.get(self.itemVnum)
			if not info:
				if self.chaosStoneModel:
					self.chaosStoneModel.Hide()
				return

			(stoneVnum, recLevel) = info

			if self.chaosStoneModel is None:
				try:
					import ingamewikiui
					self.chaosStoneModel = ingamewikiui.WikiRenderTarget(CHAOS_PREVIEW_W, CHAOS_PREVIEW_H)
					self.chaosStoneModel.SetParent(self)
					self.chaosStoneModel.Hide()
				except Exception:
					self.chaosStoneModel = None

			self.AppendSpace(4)
			self.AutoAppendTextLine(localeinfo.CHAOS_STONE_TIP_HEADER, 0xFFFFCC00)

			# reserve the model's vertical band, then let the text below set the final width
			modelY = -1
			if self.chaosStoneModel:
				self.AppendSpace(2)
				modelY = self.toolTipHeight
				self.toolTipHeight += CHAOS_PREVIEW_H
				self.ResizeToolTip()

			try:
				stoneName = nonplayer.GetMonsterName(stoneVnum)
			except Exception:
				stoneName = ""
			if stoneName:
				self.AppendSpace(2)
				self.AutoAppendTextLine(stoneName, 0xFFE6E8EA)

			self.AutoAppendTextLine(localeinfo.CHAOS_STONE_TIP_LEVEL % recLevel, 0xFF9AA0A8)
			self.AutoAppendTextLine(localeinfo.CHAOS_STONE_TIP_SPAWN, 0xFF8FD9B0)
			self.AutoAppendTextLine(localeinfo.CHAOS_STONE_TIP_DROPS, 0xFFB0B0B0)

			if self.chaosStoneModel and modelY >= 0:
				self.chaosStoneModel.SetModel(stoneVnum)
				modelX = int((self.toolTipWidth - CHAOS_PREVIEW_W) / 2)
				self.chaosStoneModel.SetPosition(modelX, modelY)
				self.chaosStoneModel.Show()
				self.childrenList.append(self.chaosStoneModel)   # ClearToolTip wiped it; re-append

			self.ResizeToolTip()

	if app.ENABLE_DS_SET:
		def BindInterface(self, interface):
			from _weakref import proxy
			self.interface = proxy(interface)

	def SetCannotUseItemForceSetDisableColor(self, enable):
		self.bCannotUseItemForceSetDisableColor = enable

	def CanEquip(self):
		if not item.IsEquipmentVID(self.itemVnum):
			return True

		race = player.GetRace()
		job = chr.RaceToJob(race)
		itemType = item.GetItemType()
		IsCostume  = (itemType == item.ITEM_TYPE_COSTUME)
		if not self.ANTI_FLAG_DICT.has_key(job):
			return False

		if item.IsAntiFlag(self.ANTI_FLAG_DICT[job]):
			return False


		sex = chr.RaceToSex(race)

		MALE = 1
		FEMALE = 0

		if item.IsAntiFlag(item.ITEM_ANTIFLAG_MALE) and sex == MALE and not IsCostume:
			return False

		if item.IsAntiFlag(item.ITEM_ANTIFLAG_FEMALE) and sex == FEMALE and not IsCostume:
			return False

		for i in xrange(item.LIMIT_MAX_NUM):
			(limitType, limitValue) = item.GetLimit(i)

			if item.LIMIT_LEVEL == limitType:
				if player.GetStatus(player.LEVEL) < limitValue:
					return False

			elif item.LIMIT_MAX_LEVEL == limitType:
				if player.GetStatus(player.LEVEL) > limitValue:
					return False
			"""
			elif item.LIMIT_STR == limitType:
				if player.GetStatus(player.ST) < limitValue:
					return False
			elif item.LIMIT_DEX == limitType:
				if player.GetStatus(player.DX) < limitValue:
					return False
			elif item.LIMIT_INT == limitType:
				if player.GetStatus(player.IQ) < limitValue:
					return False
			elif item.LIMIT_CON == limitType:
				if player.GetStatus(player.HT) < limitValue:
					return False
			"""

		return True

	def AppendTextLineAcce(self, text, color = FONT_COLOR, centerAlign = True):
		return ToolTip.AppendTextLine(self, text, color, centerAlign)

	def AppendTextLine(self, text, color = FONT_COLOR, centerAlign = True):
		if not self.CanEquip() and self.bCannotUseItemForceSetDisableColor:
			color = self.DISABLE_COLOR

		return ToolTip.AppendTextLine(self, text, color, centerAlign)

	def AppendTextLineDontCheckColor(self, text, color = FONT_COLOR, centerAlign = True):
		return ToolTip.AppendTextLine(self, text, color, centerAlign)

	def ClearToolTip(self):
		if app.ENABLE_PRIVATE_INSTANCE_LOBBY:
			# runs from ToolTip.__init__ too, before our own attributes exist
			self.chaosBuilt = False
			model = getattr(self, "chaosStoneModel", None)
			if model:
				model.Hide()

		self.isShopItem = False
		self.isInventoryContext = 0
		if app.ENABLE_12ZI:
			self.ShopSlotIndex = 0

		if app.USE_OFFLINESHOP:
			self.isOfflineShopItem = 0
		
		self.toolTipWidth = self.TOOL_TIP_WIDTH
		ToolTip.ClearToolTip(self)

	# Shortcut hints declared while AddItemData builds the body are collected and
	# rendered as one footer (header + bar rows) at the end; hints declared after
	# the build (inventory/offlineshop/wiki windows, shop builders) join the open
	# footer as immediate rows. Shop builders flush themselves after the price.
	def DeclareShortcut(self, keyTokens, label, labelColor = None):
		if self.shortcutFooterOpen:
			self.__AppendShortcutHeader()
			self.AppendShortcutRow(keyTokens, label, labelColor)
		else:
			self.pendingShortcuts.append((keyTokens, label, labelColor))

	def __AppendShortcutHeader(self):
		if self.shortcutHeaderShown:
			return
		self.shortcutHeaderShown = True
		self.AppendSpace(6)
		ToolTip.AppendTextLine(self, StripShortcutLabel(localeinfo.TOOLTIP_SHORTCUTS), self.SHORTCUT_HEADER_COLOR)
		self.AppendSpace(3)

	def FlushShortcutFooter(self):
		self.shortcutFooterOpen = True
		for (keyTokens, label, labelColor) in self.pendingShortcuts:
			self.__AppendShortcutHeader()
			self.AppendShortcutRow(keyTokens, label, labelColor)
		self.pendingShortcuts = []

	if app.USE_COSTUME_ATTR_TRANSFER:
		def AddItemDataAttrTransfer(self, itemVnum, itemVnum_2, metinSlot, attrSlot, itemEnchantList, apply_random_list = None):
			self.itemVnum = itemVnum
			item.SelectItem(itemVnum)

			itemType = item.GetItemType()
			itemSubType = item.GetItemSubType()
			itemDesc = item.GetItemDescription()
			itemSummary = item.GetItemSummary()

			self.__AdjustMaxWidth(attrSlot, itemDesc)
			self.__SetItemTitle(itemVnum, metinSlot, attrSlot,0)
			self.AppendDescription(itemDesc, 26)
			self.AppendDescription(itemSummary, 26, self.CONDITION_COLOR)
			self.__AppendLimitInformation()
			self.__AppendAffectInformation()

			item.SelectItem(itemVnum_2)

			isAcce = False
			if app.USE_ACCE_SYSTEM:
				if item.GetItemType() == item.ITEM_TYPE_COSTUME and item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
					isAcce = True

			if isAcce:
				if app.ENABLE_APPLY_RANDOM:
					self.__AppendAcceDefaultItemApplyInformation(apply_random_list, metinSlot[acce.ABSORPTION_SOCKET])
				self.__AppendAttributeInformation(attrSlot, metinSlot[acce.ABSORPTION_SOCKET])
			else:
				self.__AppendAttributeInformation(attrSlot)

			if app.USE_ENCHANT_COSTUMES:
				self.__AppendEnchantInformation(itemEnchantList)

			item.SelectItem(itemVnum)
			self.AppendWearableInformation()

			bHasRealtimeFlag = 0
			for i in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(i)
				if item.LIMIT_REAL_TIME == limitType:
					bHasRealtimeFlag = 1

			if 1 == bHasRealtimeFlag:
				self.AppendMallItemLastTime(metinSlot[0])

			self.ShowToolTip()

		def SetInventoryItemAttrTransfer(self, slotIndex_1, slotIndex_2):
			itemVnum1 = player.GetItemIndex(player.INVENTORY, slotIndex_1)
			if itemVnum1 == 0:
				return

			itemVnum2 = player.GetItemIndex(player.INVENTORY, slotIndex_2)
			if itemVnum2 == 0:
				return

			self.ClearToolTip()

			metinSlot = [player.GetItemMetinSocket(player.INVENTORY, slotIndex_1, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
			attrSlot = [player.GetItemAttribute(player.INVENTORY, slotIndex_2, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

			apply_random_list = None
			if app.ENABLE_APPLY_RANDOM:
				apply_random_list = [player.GetItemApplyRandom(player.INVENTORY, slotIndex_2, i) for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]

			itemEnchantList = []
			if app.USE_ENCHANT_COSTUMES:
				itemEnchantList = [player.GetItemEnchant(player.INVENTORY, slotIndex_2, i) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]

			self.AddItemDataAttrTransfer(itemVnum1, itemVnum2, metinSlot, attrSlot, itemEnchantList, apply_random_list)

	def SetInventoryItem(self, slotIndex, window_type = player.INVENTORY, isOfflineShop = 0):
		if app.ENABLE_DS_SET:
			self.window_type = window_type

		itemVnum = player.GetItemIndex(window_type, slotIndex)
		if 0 == itemVnum:
			return

		if app.ENABLE_GROWTH_PET_SYSTEM:
			if window_type == player.PET_FEED:
				itemVnum = player.GetItemIndex(player.INVENTORY, slotIndex)

		self.ClearToolTip()

		self.isInventoryContext = 1

		if app.USE_OFFLINESHOP:
			self.isOfflineShopItem = isOfflineShop

		if shop.IsOpen():
			if not shop.IsPrivateShop():
				item.SelectItem(itemVnum)
				self.AppendSellingPrice(player.GetISellItemPrice(window_type, slotIndex))

		if app.ENABLE_GROWTH_PET_SYSTEM and window_type == player.PET_FEED:
			metinSlot = [player.GetItemMetinSocket(player.INVENTORY, slotIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
		else:
			metinSlot = [player.GetItemMetinSocket(window_type, slotIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]

		attrSlot = [player.GetItemAttribute(window_type, slotIndex, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

		apply_random_list = []
		if app.ENABLE_APPLY_RANDOM:
			apply_random_list = [player.GetItemApplyRandom(window_type, slotIndex, i) for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]

		itemEnchantList = []
		if app.USE_ENCHANT_COSTUMES:
			itemEnchantList = [player.GetItemEnchant(window_type, slotIndex, i) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]

		if app.ENABLE_SET_ITEM:
			set_value = player.GetItemSetValue(window_type, slotIndex)

		self.AddItemData(itemVnum, metinSlot, attrSlot, None, 0, 0, window_type, slotIndex, None, apply_random_list, 0, enchantList = itemEnchantList,iSetValue = set_value)

		if app.QUICK_SELL_SYSTEM:
			self.AppendQuckSellItem()


		if shop.IsOpen():
			#if not shop.IsPrivateShop():
			self.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_SELL_ITEM_QUICK)

		if getattr(app, "USE_QUICK_ATTR_TRANSFER", 0) and player.INVENTORY == window_type and not shop.IsOpen():
			item.SelectItem(itemVnum)
			if item.ITEM_TYPE_COSTUME == item.GetItemType():
				quickTransferSubTypes = [item.COSTUME_TYPE_BODY, item.COSTUME_TYPE_HAIR]
				for quickTransferSubTypeName in ("COSTUME_TYPE_WEAPON", "COSTUME_TYPE_MOUNT_SKIN", "COSTUME_TYPE_PET_SKIN"):
					quickTransferSubTypeValue = getattr(item, quickTransferSubTypeName, -1)
					if quickTransferSubTypeValue >= 0:
						quickTransferSubTypes.append(quickTransferSubTypeValue)
				if item.GetItemSubType() in quickTransferSubTypes:
					self.DeclareShortcut(("key_ctrl", "key_shift", "key_lclick"), getattr(localeinfo, "QUICKTRANSFER_TOOLTIP", "Ctrl + Shift + Left Click: Quick Bonus Transfer"))

	if app.ENABLE_SWITCHBOT and app.USE_ITEM_ATTR_BACKUP_MODE:
		def SetSwitchbotItem(self, itemSlotIndex):
			if app.ENABLE_DS_SET:
				self.window_type = player.SWITCHBOT

			self.ClearToolTip()

			itemVnum = player.GetItemIndex(player.SWITCHBOT, itemSlotIndex)
			if not itemVnum:
				return

			if app.USE_OFFLINESHOP:
				self.isOfflineShopItem = False

			itemMetinSlot = [player.GetItemMetinSocket(player.SWITCHBOT, itemSlotIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
			itemAttrSlot = [player.GetItemAttribute(player.SWITCHBOT, itemSlotIndex, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

			itemApplyList = []
			if app.ENABLE_APPLY_RANDOM:
				itemApplyList = [player.GetItemApplyRandom(player.SWITCHBOT, itemSlotIndex, i) for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]

			itemEnchantList = []
			if app.USE_ENCHANT_COSTUMES:
				itemEnchantList = [player.GetItemEnchant(player.SWITCHBOT, itemSlotIndex, i) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]

			if app.ENABLE_SET_ITEM:
				set_value = player.GetItemSetValue(player.SWITCHBOT, itemSlotIndex)

			self.AddItemData(itemVnum, itemMetinSlot, itemAttrSlot, window_type = player.SWITCHBOT, slotIndex = itemSlotIndex, apply_random_list = itemApplyList, enchantList = itemEnchantList,iSetValue = set_value)

	def SetResulItemAttrMove(self, baseSlotIndex, materialSlotIndex, window_type = player.INVENTORY):
		baseItemVnum = player.GetItemIndex(window_type, baseSlotIndex)

		if 0 == baseItemVnum:
			return

		materialItemVnum = player.GetItemIndex(window_type, materialSlotIndex)

		if 0 == materialItemVnum:
			return

		self.ClearToolTip()

		metinSlot = [player.GetItemMetinSocket(window_type, baseSlotIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
		attrSlot = [player.GetItemAttribute(window_type, materialSlotIndex, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

		self.AddItemData(baseItemVnum, metinSlot, attrSlot)

	if app.ENABLE_CHANGE_LOOK_SYSTEM:
		def AppendChangeLookInfoShopWindow(self, slotIndex):
			changelookvnum = shop.GetItemChangeLookVnum(slotIndex)
			if not changelookvnum == 0:
				self.AppendSpace(5)
				self.AppendTextLine("[ " + localeinfo.CHANGE_LOOK_TITLE + " ]", self.CHANGELOOK_TITLE_COLOR)
				itemName = item.GetItemNameByVnum(changelookvnum)

				if item.GetItemType() == item.ITEM_TYPE_COSTUME:
					if item.GetItemSubType() == item.COSTUME_TYPE_BODY:
						malefemale = ""
						if item.IsAntiFlag(item.ITEM_ANTIFLAG_MALE):
							malefemale = localeinfo.FOR_FEMALE

						if item.IsAntiFlag(item.ITEM_ANTIFLAG_FEMALE):
							malefemale = localeinfo.FOR_MALE
						itemName += " ( " + malefemale + " )"

				textLine = self.AppendTextLine(itemName, self.CHANGELOOK_ITEMNAME_COLOR, True)
				textLine.SetFeather()

	if app.ENABLE_CHANGE_LOOK_SYSTEM:
		def AppendChangeLookInfoItemVnum(self, changelookvnum):
			if not changelookvnum == 0:
				self.AppendSpace(5)
				self.AppendTextLine("[ " + localeinfo.CHANGE_LOOK_TITLE + " ]", self.CHANGELOOK_TITLE_COLOR)
				itemName = item.GetItemNameByVnum(changelookvnum)

				if item.GetItemType() == item.ITEM_TYPE_COSTUME:
					if item.GetItemSubType() == item.COSTUME_TYPE_BODY:
						malefemale = ""
						if item.IsAntiFlag(item.ITEM_ANTIFLAG_MALE):
							malefemale = localeinfo.FOR_FEMALE

						if item.IsAntiFlag(item.ITEM_ANTIFLAG_FEMALE):
							malefemale = localeinfo.FOR_MALE
						itemName += " ( " + malefemale + " )"

				textLine = self.AppendTextLine(itemName, self.CHANGELOOK_ITEMNAME_COLOR, True)
				textLine.SetFeather()

	if app.ENABLE_SHOPEX_RENEWAL:
		def FormatRestockTime(self, seconds):
			if seconds >= 86400:
				return getattr(localeinfo, "SHOPEX_RESTOCK_IN_DH", "Restocks in %dd %dh") % (int(seconds / 86400), int((seconds % 86400) / 3600))
			if seconds >= 3600:
				return getattr(localeinfo, "SHOPEX_RESTOCK_IN_HM", "Restocks in %dh %dm") % (int(seconds / 3600), int((seconds % 3600) / 60))
			return getattr(localeinfo, "SHOPEX_RESTOCK_IN_M", "Restocks in %dm") % (max(1, int(seconds / 60)),)

		def AppendShopExExtras(self, slotIndex):
			appended = False
			if app.ENABLE_SHOPEX_ACCOUNT_BIND_SELL and shop.IsItemAccountBound(slotIndex):
				self.AppendSpace(8)
				self.AppendTextLine(localeinfo.ACCOUNT_BOUND_ITEM, 0xFFFFA500)
				appended = True
			if app.ENABLE_SHOPEX_DAILY_LIMIT:
				stockLimit = shop.GetItemCharDailyLimit(slotIndex)
				if stockLimit > 0:
					left = stockLimit - shop.GetItemCharDailyBought(slotIndex)
					if left < 0:
						left = 0
					if not appended:
						self.AppendSpace(8)
					color = 0xFFecf0f1 if left > 0 else 0xFFEF5350
					self.AppendTextLine(getattr(localeinfo, "SHOPEX_STOCK_LEFT", "Stock: %d / %d") % (left, stockLimit), color)

					# restock_days -1 never comes back; otherwise show the countdown once the
					# period is running (remaining seconds are stamped at shop open / after a buy).
					getDays = getattr(shop, "GetItemRestockDays", None)
					restockDays = int(getDays(slotIndex)) if getDays else 1
					if restockDays < 0:
						self.AppendTextLine(getattr(localeinfo, "SHOPEX_ONE_TIME", "One-time purchase"), 0xFFecf0f1)
					else:
						getRemain = getattr(shop, "GetItemRestockRemainSec", None)
						remainSec = int(getRemain(slotIndex)) if getRemain else 0
						if remainSec > 0:
							self.AppendTextLine(self.FormatRestockTime(remainSec), 0xFFecf0f1)

	def SetShopItem(self, slotIndex):
		itemVnum = shop.GetItemID(slotIndex)
		if 0 == itemVnum:
			return

		price = shop.GetItemPrice(slotIndex)

		if app.USE_MULTIPLE_SHOP_BUY and self.multipleBuyDialog:
			price *= self.multipleBuyCount

		self.ClearToolTip()
		self.isShopItem = True
		if app.ENABLE_12ZI:
			self.ShopSlotIndex = slotIndex

		#if shop.IsOpen():
		#	if not shop.IsPrivateShop():
		self.isShopItemNpc = True

		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(shop.GetItemMetinSocket(slotIndex, i))
		attrSlot = []
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			attrSlot.append(shop.GetItemAttribute(slotIndex, i))
		apply_random_list = []
		if app.ENABLE_APPLY_RANDOM:
			for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
				apply_random_list.append(shop.GetItemApplyRandom(slotIndex, i))

		self.AddItemData(itemVnum, metinSlot, attrSlot, None, 0, 0, player.INVENTORY, slotIndex, None, apply_random_list, 0)
		if app.ENABLE_SHOPEX_RENEWAL: self.AppendShopExExtras(slotIndex)

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			self.AppendChangeLookInfoShopWindow(slotIndex)

		if app.ENABLE_CHEQUE_SYSTEM:
			cheque = shop.GetItemPriceCheque(slotIndex)
			self.AppendPrice(price, cheque)
		else:
			self.AppendPrice(price)

		if app.ENABLE_12ZI:
			if shop.IsLimitedItemShop():
				count = shop.GetLimitedCount(slotIndex)
				if count != 0:
					purchaseCount = shop.GetLimitedPurchaseCount(slotIndex)
					self.AppendLimitedCount(count, purchaseCount)
				else:
					if itemVnum == 33032:
						self.AppendLimitedCount(200, 0)
					elif itemVnum == 72329:
						self.AppendLimitedCount(1, 0)
					elif itemVnum == 50927:
						self.AppendLimitedCount(1, 0)
					else:
						self.AppendLimitedCount(50, 0)

		if app.USE_MULTIPLE_SHOP_BUY and not self.multipleBuyDialog and not shop.IsPrivateShop():
			self.DeclareShortcut(("key_ctrl", "key_rclick"), localeinfo.TOOLTIP_SHOP_MULTIPLE_BUY)

		self.FlushShortcutFooter()

	def SetShopItemBySecondaryCoin(self, slotIndex):
		itemVnum = shop.GetItemID(slotIndex)
		if 0 == itemVnum:
			return

		price = shop.GetItemPrice(slotIndex)

		if app.USE_MULTIPLE_SHOP_BUY and self.multipleBuyDialog:
			price *= self.multipleBuyCount

		self.ClearToolTip()
		self.isShopItem = True

		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(shop.GetItemMetinSocket(slotIndex, i))
		attrSlot = []
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			attrSlot.append(shop.GetItemAttribute(slotIndex, i))

		self.AddItemData(itemVnum, metinSlot, attrSlot)
		if app.ENABLE_SHOPEX_RENEWAL: self.AppendShopExExtras(slotIndex)
		self.AppendPriceBySecondaryCoin(price)

		if app.ENABLE_12ZI:
			if shop.IsLimitedItemShop():
				count = shop.GetLimitedCount(slotIndex)
				if count != 0:
					purchaseCount = shop.GetLimitedPurchaseCount(slotIndex)
					self.AppendLimitedCount(count, purchaseCount)
				else:
					if itemVnum == 33032:
						self.AppendLimitedCount(200, 0)
					elif itemVnum == 72329:
						self.AppendLimitedCount(1, 0)
					elif itemVnum == 50927:
						self.AppendLimitedCount(1, 0)
					else:
						self.AppendLimitedCount(50, 0)

		if app.USE_MULTIPLE_SHOP_BUY and not self.multipleBuyDialog and not shop.IsPrivateShop():
			self.DeclareShortcut(("key_ctrl", "key_rclick"), localeinfo.TOOLTIP_SHOP_MULTIPLE_BUY)

		self.FlushShortcutFooter()

	if app.ENABLE_SHOPEX_RENEWAL:
		def SetShopItemByShopEx(self, slotIndex, type):
			itemVnum = shop.GetItemID(slotIndex)
			if itemVnum == 0:
				return

			PriceVnum = shop.GetItemPriceVnum(slotIndex)

			if app.SHOPEX_RENEWAL_EXTEND_ITEM_VNUM_PRICES:
				if PriceVnum == 0 and type == 3:
					bExtendedVnum = False
					for i in xrange(shop.MAX_SHOPEX_NEW_ITEMVNUM_PRICES):
						vnum, count = shop.GetExtendedItemPrice(slotIndex, i)
						if vnum > 0 and count > 0:
							bExtendedVnum = True
							break

					if not bExtendedVnum:
						return
			else:
				if PriceVnum == 0 and type == 3:
					return

			price = shop.GetItemPrice(slotIndex)
			if app.ENABLE_SHOPEX_GAYA_CURRENCY and type == 5 and price == 0:
				return

			if app.USE_MULTIPLE_SHOP_BUY and self.multipleBuyDialog:
				price *= self.multipleBuyCount

			self.ClearToolTip()
			self.isShopItem = True

			metinSlot = []
			for i in xrange(player.METIN_SOCKET_MAX_NUM):
				metinSlot.append(shop.GetItemMetinSocket(slotIndex, i))
			attrSlot = []
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				attrSlot.append(shop.GetItemAttribute(slotIndex, i))

			self.AddItemData(itemVnum, metinSlot, attrSlot)
			self.AppendShopExExtras(slotIndex)
			self.AppendSpace(5)

			if app.ENABLE_SHOPEX_GAYA_CURRENCY and type == 5:
				self.AppendTextLine(localeinfo.TOOLTIP_BUYPRICE % (localeinfo.NumberToGayaString(price)), self.GetPriceColor(price))
			elif type == 3:
				if app.SHOPEX_RENEWAL_EXTEND_ITEM_VNUM_PRICES:
					hasTitleAlready = False
					if PriceVnum > 0:
						self.AddShopEXItem(PriceVnum, price)
						hasTitleAlready = True

					for i in xrange(shop.MAX_SHOPEX_NEW_ITEMVNUM_PRICES):
						vnum, count = shop.GetExtendedItemPrice(slotIndex, i)
						if app.USE_MULTIPLE_SHOP_BUY and self.multipleBuyDialog:
							count *= self.multipleBuyCount

						if vnum > 0 and count > 0:
							self.AddShopEXItem(vnum, count, hasTitleAlready)
				else:
					self.AddShopEXItem(PriceVnum, price)
			elif type == 6:
				self.AppendTextLine(localeinfo.TOOLTIP_BUYPRICE % (localeinfo.NumberToChequeString(price)), self.GetPriceColor(price))
			elif type == 7:
				self.AppendGuildCoinPrice(price)

			else:
				self.AppendTextLine(localeinfo.TOOLTIP_BUYPRICE % (localeinfo.NumberToShopEXP(price)), self.GetPriceColor(price))

			if app.USE_MULTIPLE_SHOP_BUY and not self.multipleBuyDialog and not shop.IsPrivateShop():
				self.DeclareShortcut(("key_ctrl", "key_rclick"), localeinfo.TOOLTIP_SHOP_MULTIPLE_BUY)
				isBox = 1 if item.GetItemTypeByVnum(itemVnum) == item.ITEM_TYPE_GIFTBOX else 0
				if isBox:
					self.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_VIEW_CHEST_CONTENT)
				else:
					self.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_WIKI_HOVER)

			self.FlushShortcutFooter()

		def AddShopEXItem(self, itemVnum, price, hasTitleAlready = False):
			item_count = player.GetItemCountByVnum(itemVnum)
			curMoney = player.GetMoney()

			if not hasTitleAlready:
				self.AppendTextLineDontCheckColor(localeinfo.CHEQUE_SYSTEM_SELL_PRICE, self.SALES_TITLE_COLOR)

			self.AppendSpace(2)
			item.SelectItem(itemVnum)
			if not itemVnum == 1:
				name = "%s %d / x%s  " % (item.GetItemName(),item_count,localeinfo.NumberToMoneyString(price))
			else :
				name = "%s %s" % (localeinfo.NumberToMoneyString(price), item.GetItemName())

			if itemVnum == 1:
				textColor = self.SPECIAL_TITLE_COLOR if curMoney >= price else self.NEGATIVE_COLOR
			else:
				textColor = self.POSITIVE_COLOR if item_count >= price else self.NEGATIVE_COLOR


			self.AutoAppendTextLine(name, textColor)
#stopped here 

			itemImage = ui.ImageBox()
			itemImage.SetParent(self)
			itemImage.Show()
			itemImage.LoadImage(item.GetIconImageFileName())
			itemImage.SetPosition(self.toolTipWidth / 2 - 16, self.toolTipHeight + 2.5)

			self.toolTipHeight += itemImage.GetHeight() + 2.5
			self.childrenList.append(itemImage)

			self.ResizeToolTip()

		def AppendGuildCoinPrice(self, price):
			myCoins = 0
			getCoins = getattr(guild, "GetMyGuildCoins", None)
			if getCoins:
				myCoins = getCoins()
			textColor = self.POSITIVE_COLOR if myCoins >= price else self.NEGATIVE_COLOR
			self.AppendTextLine(localeinfo.TOOLTIP_BUYPRICE % (localeinfo.NumberToMoneyString(price)), textColor)
			coinImage = ui.ImageBox()
			coinImage.SetParent(self)
			coinImage.Show()
			coinImage.LoadImage("icon/item/guild_coin.png")
			coinImage.SetPosition(int(self.toolTipWidth / 2 - 16), int(self.toolTipHeight + 2))
			self.toolTipHeight += coinImage.GetHeight() + 2
			self.childrenList.append(coinImage)
			label = getattr(localeinfo, "GUILD_SHOP_COIN_LABEL", "Guild Coins")
			self.AppendTextLine("%s: %s" % (label, localeinfo.NumberToMoneyString(myCoins)))
			self.ResizeToolTip()

	def SetExchangeOwnerItem(self, slotIndex):
		itemVnum = exchange.GetItemVnumFromSelf(slotIndex)

		if 0 == itemVnum:
			return
		
		self.ClearToolTip()
		
		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(exchange.GetItemMetinSocketFromSelf(slotIndex, i))
		
		attrSlot = []
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			attrSlot.append(exchange.GetItemAttributeFromSelf(slotIndex, i))
		apply_random_list = []
		if app.ENABLE_APPLY_RANDOM:
			for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
				apply_random_list.append(exchange.GetItemApplyRandomFromSelf(slotIndex, i))
		
		itemEnchantList=[]
		if app.USE_ENCHANT_COSTUMES:
			itemEnchantList=[exchange.GetItemEnchantFromSelf(slotIndex, i) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]
		
		skinVnum = 0
		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			skinVnum = exchange.GetChangeLookVnumFromSelf(slotIndex)

		if app.ENABLE_SET_ITEM:
			setValue = exchange.GetItemSetValueFromSelf(slotIndex)

		restrictInfo = None
		if app.ENABLE_EQUIPMENT_RESTRICTION:
			restrictInfo = exchange.GetItemRestrictionFromSelf(slotIndex)

		self.AddItemData(itemVnum, metinSlot, attrSlot, None, 0, 0, player.INVENTORY, slotIndex, None, apply_random_list, 0, transmutation = skinVnum, enchantList=itemEnchantList,iSetValue = setValue, restrictInfo = restrictInfo)

	def SetExchangeTargetItem(self, slotIndex):
		itemVnum = exchange.GetItemVnumFromTarget(slotIndex)
		if 0 == itemVnum:
			return

		self.ClearToolTip()

		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(exchange.GetItemMetinSocketFromTarget(slotIndex, i))
		attrSlot = []
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			attrSlot.append(exchange.GetItemAttributeFromTarget(slotIndex, i))
		apply_random_list = []
		if app.ENABLE_APPLY_RANDOM:
			for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
				apply_random_list.append(exchange.GetItemApplyRandomFromTarget(slotIndex, i))
		
		itemEnchantList=[]
		if app.USE_ENCHANT_COSTUMES:
			itemEnchantList=[exchange.GetItemEnchantFromTarget(slotIndex, i) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]
		
		skinVnum = 0
		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			skinVnum = exchange.GetChangeLookVnumFromTarget(slotIndex)

		if app.ENABLE_SET_ITEM:
			setValue = exchange.GetItemSetValueFromTarget(slotIndex)

		restrictInfo = None
		if app.ENABLE_EQUIPMENT_RESTRICTION:
			restrictInfo = exchange.GetItemRestrictionFromTarget(slotIndex)

		self.AddItemData(itemVnum, metinSlot, attrSlot, None, 0, 0, player.INVENTORY, slotIndex, None, apply_random_list, 0, transmutation = skinVnum, enchantList=itemEnchantList,iSetValue = setValue, restrictInfo = restrictInfo)

	def SetPrivateShopBuilderItem(self, invenType, invenPos, privateShopSlotIndex):
		itemVnum = player.GetItemIndex(invenType, invenPos)
		if 0 == itemVnum:
			return

		item.SelectItem(itemVnum)
		self.ClearToolTip()

		if app.ENABLE_CHEQUE_SYSTEM:
			self.AppendSellingPrice(shop.GetPrivateShopItemPrice(invenType, invenPos), shop.GetPrivateShopItemPriceCheque(invenType, invenPos), True)
		else:
			self.AppendSellingPrice(shop.GetPrivateShopItemPrice(invenType, invenPos))

		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(player.GetItemMetinSocket(invenPos, i))
		attrSlot = []
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			attrSlot.append(player.GetItemAttribute(invenPos, i))
		apply_random_list = []
		if app.ENABLE_APPLY_RANDOM:
			for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
				apply_random_list.append(player.GetItemApplyRandom(invenPos, i))

		self.AddItemData(itemVnum, metinSlot, attrSlot, None, 0, 0, invenType, invenPos, None, apply_random_list, 0)

	if app.ENABLE_CHANGE_LOOK_SYSTEM:
		def SetChangeLookWindowItem(self, slotIndex):
			inventoryslotindex = player.GetChangeLookItemInvenSlot(slotIndex)
			if inventoryslotindex == player.ITEM_SLOT_COUNT:
				return

			itemVnum = player.GetItemIndex(player.INVENTORY, inventoryslotindex)
			if 0 == itemVnum:
				return

			self.ClearToolTip()

			metinSlot = [player.GetItemMetinSocket(player.INVENTORY, inventoryslotindex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
			attrSlot = [player.GetItemAttribute(player.INVENTORY, inventoryslotindex, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
			apply_random_list = []
			if app.ENABLE_APPLY_RANDOM:
				for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
					apply_random_list.append(player.GetItemApplyRandom(inventoryslotindex, i))

			self.AddItemData(itemVnum, metinSlot, attrSlot, None, 0, 0, player.INVENTORY, inventoryslotindex, None, apply_random_list, 0)

	def SetSafeBoxItem(self, slotIndex):
		itemVnum = safebox.GetItemID(slotIndex)
		if 0 == itemVnum:
			return

		self.ClearToolTip()
		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(safebox.GetItemMetinSocket(slotIndex, i))
		attrSlot = []
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			attrSlot.append(safebox.GetItemAttribute(slotIndex, i))
		apply_random_list = []
		if app.ENABLE_APPLY_RANDOM:
			for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
				apply_random_list.append(safebox.GetItemApplyRandom(slotIndex, i))
		
		itemEnchantList=[]
		if app.USE_ENCHANT_COSTUMES:
			itemEnchantList=[safebox.GetItemEnchant(slotIndex, i) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]

		if app.ENABLE_SET_ITEM:
			set_value = safebox.GetItemSetValue(slotIndex)

		self.AddItemData(itemVnum, metinSlot, attrSlot, None, safebox.GetItemFlags(slotIndex), 0, player.SAFEBOX, slotIndex, None, apply_random_list, 0,enchantList=itemEnchantList,iSetValue = set_value)

	def SetMallItem(self, slotIndex):
		itemVnum = safebox.GetMallItemID(slotIndex)
		if 0 == itemVnum:
			return

		self.ClearToolTip()
		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(safebox.GetMallItemMetinSocket(slotIndex, i))
		attrSlot = []
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			attrSlot.append(safebox.GetMallItemAttribute(slotIndex, i))
		apply_random_list = []
		if app.ENABLE_APPLY_RANDOM:
			for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
				apply_random_list.append(safebox.GetMallItemApplyRandom(slotIndex, i))
		
		itemEnchantList=[]
		if app.USE_ENCHANT_COSTUMES:
			itemEnchantList=[safebox.GetMallItemEnchant(slotIndex, i) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]
		
		self.AddItemData(itemVnum, metinSlot, attrSlot, None, 0, 0, player.MALL, slotIndex, None, apply_random_list, 0,enchantList=itemEnchantList)

	def SetItemToolTip(self, itemVnum):
		self.ClearToolTip()
		metinSlot = []
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlot.append(0)
		attrSlot = []
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			attrSlot.append((0, 0))

		if app.ENABLE_ITEMSHOP:
			item.SelectItem(itemVnum)
			for i in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(i)
				if item.LIMIT_TIMER_BASED_ON_WEAR == limitType:
					metinSlot[0] = limitValue
				elif item.LIMIT_REAL_TIME == limitType or item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
					metinSlot[0] = app.GetGlobalTimeStamp()+limitValue
		if app.ENABLE_SET_ITEM:
			setValue = 0

		self.AddItemData(itemVnum, metinSlot, attrSlot,iSetValue = setValue)

	# def SetItemToolTip(self, itemVnum):
		# self.ClearToolTip()
		# metinSlot = []
		# for i in xrange(player.METIN_SOCKET_MAX_NUM):
			# metinSlot.append(0)
		# attrSlot = []
		# for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			# attrSlot.append((0, 0))

		# self.AddItemData(itemVnum, metinSlot, attrSlot)

	if app.ENABLE_MAILBOX:
		def SetMailBoxItem(self, index):
			item_data = mail.GetMailItemData(index)
			if None == item_data:
				return

			(vnum, count) = item_data

			self.ClearToolTip()
			metinSlot = []
			for i in xrange(player.METIN_SOCKET_MAX_NUM):
				metinSlot.append(mail.GetMailItemMetinSocket(index, i))
			attrSlot = []
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				attrSlot.append(mail.GetMailItemAttribute(index, i))
			apply_random_list = []
			if app.ENABLE_APPLY_RANDOM:
				for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
					apply_random_list.append(mail.GetItemApplyRandom(index, i))
			
			itemEnchantList=[]
			if app.USE_ENCHANT_COSTUMES:
				itemEnchantList=[mail.GetItemEnchant(index, i) for i in xrange(player.ENCHANT_SLOT_MAX_NUM)]

			if app.ENABLE_SET_ITEM:
				set_value = mail.GetItemSetValue(index)

			self.AddItemData(vnum, metinSlot, attrSlot, None, 0, 0, player.INVENTORY, index, None, apply_random_list, 0,enchantList=itemEnchantList,iSetValue = set_value)
			
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				changelookvnum = mail.GetItemChangeLookVnum(index)
				self.AppendChangeLookInfoItemVnum(changelookvnum)

	def __AppendAttackSpeedInfo(self, item):
		atkSpd = item.GetValue(0)

		if atkSpd < 80:
			stSpd = localeinfo.TOOLTIP_ITEM_VERY_FAST
		elif atkSpd <= 95:
			stSpd = localeinfo.TOOLTIP_ITEM_FAST
		elif atkSpd <= 105:
			stSpd = localeinfo.TOOLTIP_ITEM_NORMAL
		elif atkSpd <= 120:
			stSpd = localeinfo.TOOLTIP_ITEM_SLOW
		else:
			stSpd = localeinfo.TOOLTIP_ITEM_VERY_SLOW

		self.AppendTextLine(localeinfo.TOOLTIP_ITEM_ATT_SPEED % stSpd, self.NORMAL_COLOR)

	def __AppendAttackGradeInfo(self):
		atkGrade = item.GetValue(1)
		self.AppendTextLine(localeinfo.TOOLTIP_ITEM_ATT_GRADE % atkGrade, self.GetChangeTextLineColor(atkGrade))

	if app.USE_ACCE_SYSTEM:
		def CalcAcceValue(self, value, abs):
			if not value:
				return 0

			valueCalc = int((round(value * abs) / 100) - .5) + int(int((round(value * abs) / 100) - .5) > 0)
			if valueCalc <= 0 and value > 0:
				value = 1
			else:
				value = valueCalc

			return value

	if app.USE_ACCE_SYSTEM:
		def __AppendAttackPowerInfo(self, itemAbsChance = 0):
			minPower = item.GetValue(3)
			maxPower = item.GetValue(4)
			addPower = item.GetValue(5)

			if itemAbsChance:
				minPower = self.CalcAcceValue(minPower, itemAbsChance)
				maxPower = self.CalcAcceValue(maxPower, itemAbsChance)
				addPower = self.CalcAcceValue(addPower, itemAbsChance)

			if maxPower > minPower:
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_ATT_POWER % (minPower+addPower, maxPower+addPower), self.POSITIVE_COLOR)
			else:
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_ATT_POWER_ONE_ARG % (minPower+addPower), self.POSITIVE_COLOR)
	else:
		def __AppendAttackPowerInfo(self):
			minPower = item.GetValue(3)
			maxPower = item.GetValue(4)
			addPower = item.GetValue(5)
			if maxPower > minPower:
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_ATT_POWER % (minPower+addPower, maxPower+addPower), self.POSITIVE_COLOR)
			else:
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_ATT_POWER_ONE_ARG % (minPower+addPower), self.POSITIVE_COLOR)

	if app.USE_ACCE_SYSTEM:
		def __AppendMagicAttackInfo(self, itemAbsChance = 0):
			minMagicAttackPower = item.GetValue(1)
			maxMagicAttackPower = item.GetValue(2)
			addPower = item.GetValue(5)

			if itemAbsChance:
				minMagicAttackPower = self.CalcAcceValue(minMagicAttackPower, itemAbsChance)
				maxMagicAttackPower = self.CalcAcceValue(maxMagicAttackPower, itemAbsChance)
				addPower = self.CalcAcceValue(addPower, itemAbsChance)

			if minMagicAttackPower > 0 or maxMagicAttackPower > 0:
				if maxMagicAttackPower > minMagicAttackPower:
					self.AppendTextLine(localeinfo.TOOLTIP_ITEM_MAGIC_ATT_POWER % (minMagicAttackPower + addPower, maxMagicAttackPower + addPower), self.POSITIVE_COLOR)
				else:
					self.AppendTextLine(localeinfo.TOOLTIP_ITEM_MAGIC_ATT_POWER_ONE_ARG % (minMagicAttackPower + addPower), self.POSITIVE_COLOR)
	else:
		def __AppendMagicAttackInfo(self):
			minMagicAttackPower = item.GetValue(1)
			maxMagicAttackPower = item.GetValue(2)
			addPower = item.GetValue(5)

			if minMagicAttackPower > 0 or maxMagicAttackPower > 0:
				if maxMagicAttackPower > minMagicAttackPower:
					self.AppendTextLine(localeinfo.TOOLTIP_ITEM_MAGIC_ATT_POWER % (minMagicAttackPower+addPower, maxMagicAttackPower+addPower), self.POSITIVE_COLOR)
				else:
					self.AppendTextLine(localeinfo.TOOLTIP_ITEM_MAGIC_ATT_POWER_ONE_ARG % (minMagicAttackPower+addPower), self.POSITIVE_COLOR)

	if app.USE_ACCE_SYSTEM:
		def __AppendMagicDefenceInfo(self, itemAbsChance = 0):
			magicDefencePower = item.GetValue(0)

			if itemAbsChance:
				magicDefencePower = self.CalcAcceValue(magicDefencePower, itemAbsChance)

			if magicDefencePower > 0:
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_MAGIC_DEF_POWER % magicDefencePower, self.GetChangeTextLineColor(magicDefencePower))
	else:
		def __AppendMagicDefenceInfo(self):
			magicDefencePower = item.GetValue(0)

			if magicDefencePower > 0:
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_MAGIC_DEF_POWER % magicDefencePower, self.GetChangeTextLineColor(magicDefencePower))

	# app.USE_ACCE_SYSTEM: @_rate
	def __AppendAttributeInformation(self, attrSlot, _rate = -1):
		if 0 != attrSlot:
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				_type = attrSlot[i][0]

				if _type == 0:
					continue

				_value = attrSlot[i][1]

				if _value == 0:
					continue

				if _rate != -1:
					_value = self.CalcAcceValue(_value, _rate)

				affectString = self.__GetAffectString(_type, _value)

				if affectString:
					affectColor = self.__GetAttributeColor(i, _value)
					self.AppendTextLine(affectString, affectColor)

	if app.USE_ENCHANT_COSTUMES:
		def __AppendEnchantInformation(self, infoList):
			if app.USE_ENCHANT_COSTUMES_RENEWED:
				iLeftTime = 0
				iLeftTimeColor = self.NEGATIVE_COLOR
				bHave = False

			for i in xrange(len(infoList)):
				enchantType = infoList[i][0]
				enchantValue = infoList[i][1]
				enchantTime = infoList[i][2]

				if enchantType == 0 or enchantValue == 0 or enchantTime == 0:
					continue

				if bHave == False:
					bHave = True

				affectString = self.__GetAffectString(enchantType, enchantValue)
				if affectString:
					affectColor = self.NEGATIVE_COLOR

					leftTime = max(0, enchantTime-app.GetGlobalTimeStamp())
					if leftTime:
						affectColor = self.SPECIAL_TITLE_COLOR

						if app.USE_ENCHANT_COSTUMES_RENEWED:
							if leftTime > iLeftTime:
								iLeftTime = leftTime
								iLeftTimeColor = affectColor
						else:
							if leftTime <= 60:
								affectString = affectString + "I[" + localeinfo.TOOLTIP_LEFT_SECS % (leftTime) + "]I"
							else:
								affectString = "\\n" + affectString + "\\n" + localeinfo.newSecondToDHM(leftTime)
					else:
						if not app.USE_ENCHANT_COSTUMES_RENEWED:
							affectString = affectString + localeinfo.COSTUME_ENCHANT_EXPIRED

					self.AppendTextLine(affectString, affectColor)

			if app.USE_ENCHANT_COSTUMES_RENEWED and bHave == True:
				if iLeftTime > 0:
					self.AppendTextLine(localeinfo.COSTUME_ENCHANT_LEFT_RENEWED % localeinfo.newSecondToDHM(leftTime),  self.LOW_PRICE_COLOR)
				else:
					self.AppendTextLine(localeinfo.COSTUME_ENCHANT_EXPIRED_RENEWED, iLeftTimeColor)

	if app.ENABLE_67TH_BONUS:
		def __AppendRareAttributeInformation(self, attrSlot, metinSlot = []):
			if 0 != attrSlot:
				attrCount = 0
				for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
					if 0 == attrSlot[i][1]:
						continue

					attrCount += 1

				if attrCount < player.ATTRIBUTE_SLOT_MAX_NUM and attrCount >= (player.ATTRIBUTE_SLOT_MAX_NUM - 2):
					self.AppendTextLine(localeinfo.ATTR_6TH_7TH_POSSIBILITY, self.TEXTLINE_2ND_COLOR_DEFAULT)
	if app.ENABLE_APPLY_RANDOM:
		def __AppendDefaultItemApplyInformation(self, apply_random_list):
			if apply_random_list != None:
				for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
					type = apply_random_list[i][0]
					value = apply_random_list[i][1]

					if type == 0 or value == 0:
						continue

					affectString = self.__GetAffectString(type, value)
					if affectString:
						self.AppendTextLine(affectString, self.APPLY_RANDOM_TEXT_COLOR)

		if app.USE_ACCE_SYSTEM:
			def __AppendAcceDefaultItemApplyInformation(self, apply_random_list, socketPercentage):
				if apply_random_list != None:
					for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM):
						type = apply_random_list[i][0]
						value = apply_random_list[i][1]

						if 0 == value:
							continue

						affectValue = self.CalcAcceValue(value, socketPercentage)
						affectString = self.__GetAffectString(type, affectValue)
						if affectString:
							self.AppendTextLine(affectString, self.APPLY_RANDOM_TEXT_COLOR)

	if app.ENABLE_DS_SET:
		def __AppendDragonSoulAttributeInformation(self, attrSlot, dsType = 0, grade = 0):
			if 0 != attrSlot:
				if grade != 0:
					setWeightValue = item.GetDSSetWeight(dsType, grade)
					basicApplyCount = item.GetDSBasicApplyCount(dsType, grade)

					for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
						type = attrSlot[i][0]
						value = attrSlot[i][1]

						if 0 == value:
							continue

						affectString = self.__GetAffectString(type, value)
						if affectString:
							affectColor = self.__GetAttributeColor(i, value)

							setValue = 0
							if i < basicApplyCount:
								setValue = item.GetDSBasicApplyValue(dsType, type)
							else:
								setValue = item.GetDSAdditionalApplyValue(dsType, type)

							if setValue != 0:
								setValue = (setValue * setWeightValue - 1) / 100 + 1
								if affectString.find('%') == -1:
									self.AppendTwoColorTextLine(affectString, affectColor, " I[+%d]I" % (setValue))
								else:
									self.AppendTwoColorTextLine(affectString, affectColor, " I[+%d%%]I" % (setValue))
							else:
								self.AppendTextLine(affectString, affectColor)
				else:
					for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
						type = attrSlot[i][0]
						value = attrSlot[i][1]

						if 0 == value:
							continue

						affectString = self.__GetAffectString(type, value)
						if affectString:
							affectColor = self.__GetAttributeColor(i, value)
							self.AppendTextLine(affectString, affectColor)

	if app.ENABLE_ATTR_6TH_7TH:
		def __AppendAttribute6th7thPossibility(self, attrSlot):
			if 0 != attrSlot:
				attrCount = 0
				for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
					if 0 == attrSlot[i][1]:
						continue
					attrCount += 1

				if attrCount >= player.ATTRIBUTE_SLOT_MAX_NUM - 2 and attrCount < player.ATTRIBUTE_SLOT_MAX_NUM:
					self.AppendTextLine(localeinfo.ATTR_6TH_7TH_POSSIBILITY, self.ATTR_6TH_7TH_COLOR)


	def __GetAttributeColor(self, index, value):
		if value > 0:
			if index >= 5:
				if app.ENABLE_ATTR_6TH_7TH:
					return self.ATTR_6TH_7TH_COLOR
				else:
					return self.SPECIAL_POSITIVE_COLOR2
			else:
				return self.SPECIAL_POSITIVE_COLOR
		elif value == 0:
			return self.NORMAL_COLOR
		else:
			return self.NEGATIVE_COLOR

	def __IsPolymorphItem(self, itemVnum):
		item.SelectItem(itemVnum)
		if item.GetItemType() == item.ITEM_TYPE_POLYMORPH:
			return 1
		return 0

	def __SetPolymorphItemTitle(self, monsterVnum):
		countSuffix = ""
		countPrefix = ""

		if app.USE_MULTIPLE_SHOP_BUY and self.multipleBuyDialog:
			if localeinfo.IsARABIC():
				countSuffix = " x%d" % (self.multipleBuyCount)
			else:
				countPrefix = "x%d " % (self.multipleBuyCount)

		if localeinfo.IsVIETNAM():
			itemName = countPrefix + item.GetItemName() + " " + nonplayer.GetMonsterName(monsterVnum) + countSuffix
		else:
			itemName = countPrefix + nonplayer.GetMonsterName(monsterVnum) + " " + item.GetItemName() + countSuffix

		self.SetTitle(itemName)

	if app.ENABLE_SET_ITEM:
		def SetItemString(self, set_value):
			if set_value == 1:
				return localeinfo.TOOLTIP_SET_ITEM_1
				return "x(1)x"
			elif set_value == 2:
				return localeinfo.TOOLTIP_SET_ITEM_2
				return "x(2)x"
			elif set_value == 3:
				return localeinfo.TOOLTIP_SET_ITEM_3
				return "x(3)x"
			elif set_value == 4:
				return localeinfo.TOOLTIP_SET_ITEM_4
				return "x(4)x"
			elif set_value == 5:
				return localeinfo.TOOLTIP_SET_ITEM_5
			else:
				return ""

	def __SetNormalItemTitle(self, set_value, itemVnum):
		if app.USE_MULTIPLE_SHOP_BUY and not app.ENABLE_SET_ITEM:
			if self.multipleBuyDialog:
				if localeinfo.IsARABIC():
					itemName = item.GetItemName() + " x%d" % (self.multipleBuyCount)
				else:
					itemName = "x%d " % (self.multipleBuyCount) + item.GetItemName()
				self.SetTitle(itemName)
		elif app.USE_MULTIPLE_SHOP_BUY and app.ENABLE_SET_ITEM:
			if self.multipleBuyDialog:
				if localeinfo.IsARABIC():
					itemName = item.GetItemName() + " x%d" % (self.multipleBuyCount)
				else:
					itemName = "x%d " % (self.multipleBuyCount) + item.GetItemName()
				self.SetTitle(itemName)
			else:
				itemName = ""
				itemName += self.SetItemString(set_value)
				itemName += item.GetItemName()
				self.SetTitle(itemName)
		else:
			self.SetTitle(item.GetItemName())

	def __SetSpecialItemTitle(self, set_value, itemVnum):
		if app.USE_MULTIPLE_SHOP_BUY and not app.ENABLE_SET_ITEM:
			if self.multipleBuyDialog:
				if localeinfo.IsARABIC():
					itemName = item.GetItemName() + " x%d" % (self.multipleBuyCount)
				else:
					itemName = "x%d " % (self.multipleBuyCount) + item.GetItemName()
				self.AppendTextLine(itemName, self.SPECIAL_TITLE_COLOR)

		elif app.USE_MULTIPLE_SHOP_BUY and app.ENABLE_SET_ITEM:
			if self.multipleBuyDialog:
				if localeinfo.IsARABIC():
					itemName = item.GetItemName() + " x%d" % (self.multipleBuyCount)
				else:
					itemName = "x%d " % (self.multipleBuyCount) + item.GetItemName()
				self.AppendTextLine(itemName, self.SPECIAL_TITLE_COLOR)
			else:
				itemName = ""
				itemName += self.SetItemString(set_value)
				itemName += item.GetItemName()
				self.AppendTextLine(itemName, self.SPECIAL_TITLE_COLOR)
		else:
			self.AppendTextLine(item.GetItemName(), self.SPECIAL_TITLE_COLOR)

	def __SetItemTitle(self, itemVnum, metinSlot, attrSlot, set_value):
		# A renamed location scroll shows the player's label as its actual name.
		if app.ENABLE_LOCATION_SCROLL_REWORK and locationscroll.IsLocationScroll(itemVnum):
			if locationscroll.OverrideTitle(self, metinSlot):
				return

		if localeinfo.IsCANADA():
			if 72726 == itemVnum or 72730 == itemVnum:
				self.AppendTextLine(item.GetItemName(), grp.GenerateColor(1.0, 0.7843, 0.0, 1.0))
				return

		if self.__IsPolymorphItem(itemVnum):
			self.__SetPolymorphItemTitle(metinSlot[0])
		else:
			if self.__IsAttr(attrSlot):
				self.__SetSpecialItemTitle(set_value, itemVnum)
				return

			self.__SetNormalItemTitle(set_value, itemVnum)

	if app.ENABLE_RENDER_TARGET:
		def __AppendRenderTarget(self, itemVnum):
			if uiRenderTarget.IsCanShowItems(itemVnum):
				if app.USE_MULTIPLE_SHOP_BUY and self.multipleBuyDialog:
					return

				self.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_RENDER)

	def __IsAttr(self, attrSlot):
		if not attrSlot:
			return False

		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			type = attrSlot[i][0]
			if 0 != type:
				return True

		return False

	def AddRefineItemData(self, item_vnum, sockets, attributes, rare_attr_slot = None, flags = 0, refine_element = None, apply_random_list = None, set_value = 0, rSetValue = 0):
		# for i in xrange(player.METIN_SOCKET_MAX_NUM):
			# metinSlotData = sockets[i]
			# if self.GetMetinItemIndex(metinSlotData) == constinfo.ERROR_METIN_STONE:
				# sockets[i] = player.METIN_SOCKET_TYPE_SILVER

		self.AddItemData(item_vnum, (0, 0, 0, 0, 0, 0), attributes, rare_attr_slot, 0, 0, player.INVENTORY, -1, refine_element, apply_random_list, set_value, iSetValue = rSetValue )

	def AddItemData_Offline(self, itemVnum, itemDesc, itemSummary, metinSlot, attrSlot):
		self.__AdjustMaxWidth(attrSlot, itemDesc)
		self.__SetItemTitle(itemVnum, metinSlot, attrSlot)

		if self.__IsHair(itemVnum):
			self.__AppendHairIcon(itemVnum)

		### Description ###
		self.AppendDescription(itemDesc, 26)
		self.AppendDescription(itemSummary, 26, self.CONDITION_COLOR)

	if app.ENABLE_SOUL_SYSTEM:
		def __SoulItemToolTip(self, itemVnum, metinSlot, flags):
			self.itemVnum = itemVnum
			item.SelectItem(itemVnum)
			itemType = item.GetItemType()
			itemSubType = item.GetItemSubType()

			(limit_Type, limit_Value) = item.GetLimit(1)
			max_time = limit_Value

			if 0 != flags:
				metinSlot[2] = item.GetValue(2)

			data = metinSlot[2]
			keep_time = data / 10000
			remain_count = data % 10000

			## value3,4,5
			value_index = 2 + keep_time / 60
			if value_index < 3:
				value_index = 3
			if value_index > 5:
				value_index = 5
			damage_value = float(item.GetValue(value_index) / 10.0)

			self.ClearToolTip()
			## board size
			soul_desc = ""
			if item.RED_SOUL == itemSubType:
				soul_desc = localeinfo.SOUL_ITEM_TOOLTIP_RED1 % (keep_time, max_time)
				soul_desc += localeinfo.SOUL_ITEM_TOOLTIP_RED2 % (damage_value)
			elif item.BLUE_SOUL == itemSubType:
				soul_desc = localeinfo.SOUL_ITEM_TOOLTIP_BLUE1 % (keep_time, max_time)
				soul_desc += localeinfo.SOUL_ITEM_TOOLTIP_BLUE2 % (damage_value)

			self.__AdjustMaxWidth(0, soul_desc)

			self.__SetNormalItemTitle(0, itemVnum)

			## desc
			board_width = self.__AdjustDescMaxWidth(soul_desc)
			if keep_time < 60:
				desc_color = 0xfff15f5f # RGB(241,95,95)
			else:
				desc_color = 0xff86e57f # RGB(134,229,127)

			self.AppendDescription(soul_desc, 26, desc_color)

			self.AppendDescription(localeinfo.SOUL_ITEM_TOOLTIP_COMMON, 26, 0xfff15f5f) # RGB(241,95,95)
			self.AppendSpace(10)

			if metinSlot[1] and keep_time >= 60 and remain_count > 0:
				self.AppendTextLine(localeinfo.SOUL_ITEM_TOOLTIP_APPLY, 0xff86e57f ) # RGB(134,229,127)
			else:
				self.AppendTextLine(localeinfo.SOUL_ITEM_TOOLTIP_UNAPPLIED, 0xfff15f5f ) # RGB(241,95,95)
			self.AppendSpace(5)

			self.AppendTextLine(localeinfo.SOUL_ITEM_TOOLTIP_REMAIN_COUNT % remain_count)
			self.AppendSpace(5)

			if 0 == flags:
				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)
					if item.LIMIT_REAL_TIME == limitType:
						self.AppendSoulItemLastTime(metinSlot[0])
			else:
				(limitType, limitValue) = item.GetLimit(0)
				self.AppendSoulItemLastTime(limitValue + app.GetGlobalTimeStamp())

			self.FlushShortcutFooter()
			self.ShowToolTip()

		def AppendSoulItemLastTime(self, endTime):
			leftSec = max(0, endTime - app.GetGlobalTimeStamp())
			if leftSec > 0:
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.SOUL_ITEM_TOOLTIP_REMOVE_TIME + " : " + localeinfo.SecondToDHM(leftSec), self.NORMAL_COLOR)

	def __SandikIngoru(self, file):
		iconFile = str(file)

		itemImage = ui.ImageBox()
		itemImage.SetParent(self)
		itemImage.Show()

		itemImage.LoadImage(iconFile)

		itemImage.SetPosition(itemImage.GetWidth()/ 2 - 50+82, self.toolTipHeight)
		self.toolTipHeight += itemImage.GetHeight()
		self.childrenList.append(itemImage)
		self.ResizeToolTip()

	if app.USE_OFFLINESHOP:
		def AddRightClickForSale(self):
			self.DeclareShortcut(("key_rclick",), localeinfo.OFFLINESHOP_TOOLTIP_RIGHT_CLICK_FOR_SALE)

	def __AppendBuffiItemInfo(self, itemVnum):
		# Live summary block for the buffi SUMMON scroll only (ore/name/recharge/permanent get nothing).
		# When the player owns a buffi, show its real state -- name / level / Intelligence / equipped
		# ores / skill levels -- cached from the server status push (constinfo) + the player skill blob.
		# Otherwise just the generic "summons a buffi" line. (INT/level/ores reflect evolution + ore;
		# they are NOT the item's proto values.)
		L = lambda key, default: getattr(localeinfo, key, default)
		self.AppendSpace(5)
		if constinfo.BUFFI_TT_LEVEL <= 0:
			self.AppendTextLine(L("BUFFI_TT_SUMMON", "Summons your Buffi companion."), self.SPECIAL_POSITIVE_COLOR)
			item.SelectItem(itemVnum)
			return

		if constinfo.BUFFI_TT_NAME:
			self.AppendTextLine(L("BUFFI_TT_NAME_LINE", "Name: %s") % constinfo.BUFFI_TT_NAME, self.SPECIAL_POSITIVE_COLOR)
		self.AppendTextLine(L("BUFFI_TT_LEVEL_LINE", "Level: %d") % constinfo.BUFFI_TT_LEVEL, self.NORMAL_COLOR)
		self.AppendTextLine(L("BUFFI_TT_INT_LINE", "Intelligence: %d") % constinfo.BUFFI_TT_INT, self.NORMAL_COLOR)

		# Duration status -- THE critical line for a new player: a time-consumed buffi otherwise looks
		# identical to a working one here. Active -> remaining time (same server-synced clock + tiered
		# format as the Companion window's gauge); EXPIRED -> red notice + exactly what to do about it.
		expireAt = constinfo.BUFFI_TT_EXPIRE
		if expireAt:
			if expireAt == 0xFFFFFFFF:   # BUFFI_DURATION_PERMANENT sentinel (buffi.hpp)
				self.AppendTextLine(L("BUFFI_TT_DUR_LINE", "Duration: %s") % L("COMPANION_DURATION_PERMANENT", "Permanent"), self.SPECIAL_POSITIVE_COLOR)
			else:
				remain = expireAt - app.GetGlobalTimeStamp()
				if remain > 0:
					if remain >= 86400:
						left = L("COMPANION_DURATION_LEFT_FMT", "%dd %dh") % (remain // 86400, (remain % 86400) // 3600)
					else:
						left = L("COMPANION_DURATION_LEFT_MS_FMT", "%dh %dmin") % (remain // 3600, (remain % 3600) // 60)
					self.AppendTextLine(L("BUFFI_TT_DUR_LINE", "Duration: %s") % left, self.NORMAL_COLOR)
				else:
					self.AppendTextLine(L("BUFFI_TT_DUR_EXPIRED", "Duration expired - cannot be summoned!"), self.NEGATIVE_COLOR)
					self.AppendTextLine(L("BUFFI_TT_DUR_HINT", "Use a Buffi duration item to recharge it."), self.SPECIAL_POSITIVE_COLOR)

		# Equipped ores: the icons on ONE row, with the TOTAL INT underneath (cached vnums from the push).
		oreVnums = [v for v in constinfo.BUFFI_TT_ORES if v]
		if oreVnums:
			GAP = 4
			icons = []
			totalInt = 0
			for v in oreVnums:
				item.SelectItem(v)
				ico = ui.ImageBox()
				ico.SetParent(self)
				ico.LoadImage(item.GetIconImageFileName())
				ico.Show()
				icons.append(ico)
				oi = item.GetValue(0)
				if oi > 3:
					oi = 3
				totalInt += oi
			iconW = icons[0].GetWidth()
			iconH = icons[0].GetHeight()
			rowW = len(icons) * iconW + (len(icons) - 1) * GAP
			startX = self.toolTipWidth / 2 - rowW / 2
			y0 = self.toolTipHeight
			for k, ico in enumerate(icons):
				ico.SetPosition(startX + k * (iconW + GAP), y0)
				self.childrenList.append(ico)
			self.toolTipHeight += iconH
			self.ResizeToolTip()
			self.AppendTextLine(L("BUFFI_TT_ORE_PLUS", "+%d INT") % totalInt, self.SPECIAL_POSITIVE_COLOR)

		# Current buffi skills (read live from the player skill blob; 163..166). Show the GRADE the way
		# the skill window does -- M/G/P prefix + level-within-grade (GetSkillLevelNew is per-grade, so a
		# Master-1 and Grand-Master-1 both return 1; the prefix is what distinguishes them).
		self.AppendTextLine(L("BUFFI_TT_SKILLS_HDR", "Skills:"), self.NORMAL_COLOR)
		labels = (localeinfo.COMPANION_BUFFI_SKILL0, localeinfo.COMPANION_BUFFI_SKILL1,
		          localeinfo.COMPANION_BUFFI_SKILL2, localeinfo.COMPANION_BUFFI_SKILL3)
		fmt = L("BUFFI_TT_SKILL_LINE", "  %s: %s")
		for i in xrange(4):
			vnum  = 163 + i
			grade = player.GetSkillGradeNew(vnum)
			lv    = player.GetSkillLevelNew(vnum)
			if grade == 1:
				lvStr = "M%d" % lv
			elif grade == 2:
				lvStr = "G%d" % lv
			elif grade == 3:
				lvStr = "P%d" % lv
			elif lv > 0:
				lvStr = "%d" % lv
			else:
				lvStr = "-"
			self.AppendTextLine(fmt % (labels[i], lvStr), self.SPECIAL_POSITIVE_COLOR)

		item.SelectItem(itemVnum)   # restore the tooltip's item selection (we changed it for the ore icons)

	def __AppendMiningPickBonus(self, window_type, slotIndex):
		# Mining Rework: pickaxe upgrade (refine +0..+9) adds mining success, +0%..+50% (grade*50/9).
		grade = 0
		try:
			if slotIndex >= 0:
				grade = player.GetItemGrade(window_type, slotIndex)
			else:
				nm = item.GetItemName()
				if nm and "+" in nm:
					tail = nm[nm.rfind("+") + 1:]
					if tail.isdigit():
						grade = int(tail)
		except:
			grade = 0
		grade = max(0, min(9, grade))
		bonus = grade * 50 / 9
		self.AppendSpace(5)
		self.AppendTextLine(localeinfo.TOOLTIP_MINING_PICK_BONUS % bonus, self.POSITIVE_COLOR)
		if grade < 9:
			self.AppendTextLine(localeinfo.TOOLTIP_MINING_PICK_HINT, self.NORMAL_COLOR)

	def __AppendFishingRodBonus(self, window_type, slotIndex):
		# Fishing Rework: rod upgrade (refine +0..+9) adds fishing success, +0%..+50% (grade*50/9).
		grade = 0
		try:
			if slotIndex >= 0:
				grade = player.GetItemGrade(window_type, slotIndex)
			else:
				nm = item.GetItemName()
				if nm and "+" in nm:
					tail = nm[nm.rfind("+") + 1:]
					if tail.isdigit():
						grade = int(tail)
		except:
			grade = 0
		grade = max(0, min(9, grade))
		bonus = grade * 50 / 9
		self.AppendSpace(5)
		self.AppendTextLine(getattr(localeinfo, "TOOLTIP_FISHING_ROD_BONUS", "Fishing Success  +%d%%") % bonus, self.POSITIVE_COLOR)
		if grade < 9:
			self.AppendTextLine(getattr(localeinfo, "TOOLTIP_FISHING_ROD_HINT", "Upgrade the rod for more (max +50% at +9)"), self.NORMAL_COLOR)
	def __CombinedLootBoosterToolTip(self, itemVnum, metinSlot, attrSlot):
		self.__SetItemTitle(itemVnum, metinSlot, attrSlot, 0)
		self.AppendDescription(item.GetItemDescription(), 26)
		self.AppendSpace(5)
		ToolTip.AppendTextLine(self, getattr(localeinfo, "COMBINED_LOOT_TT_HEADER", "While active, all at once:"), self.CONDITION_COLOR, True, True)
		for key, default in (
			("COMBINED_LOOT_TT_DROP", "+50% item drop chance on every kill"),
			("COMBINED_LOOT_TT_STONE", "Metin stones: +20% loot, 3% chance to double the whole drop"),
			("COMBINED_LOOT_TT_DUNGEON", "Dungeons: +20% loot chance on every kill"),
			("COMBINED_LOOT_TT_BOSS", "Bosses: 5% chance to double the drop (2% in the open world)"),
		):
			ToolTip.AppendTextLine(self, getattr(localeinfo, key, default), self.SPECIAL_POSITIVE_COLOR, True, True)
		self.AppendSpace(5)
		ToolTip.AppendTextLine(self, getattr(localeinfo, "COMBINED_LOOT_TT_DURATION", "Duration: %s") % localeinfo.SecondToDHM(item.GetValue(3)), self.CONDITION_COLOR, True, True)
		self.FlushShortcutFooter()
		self.ShowToolTip()

	def __AppendPvPOrderBenefitTable(self):
		TBL_W = 260
		HEAD_H = 20
		ROW_H = 18
		if self.toolTipWidth < TBL_W + 24:
			self.toolTipWidth = TBL_W + 24

		self.AppendSpace(6)

		headers = [getattr(localeinfo, "PVP_ORDER_TT_COL_EFFECT", "Effect"), getattr(localeinfo, "PVP_ORDER_TT_COL_VALUE", "Value")]
		widths = [175, 85]
		noneTxt = getattr(localeinfo, "PVP_ORDER_TT_NONE", "None")
		rows = [
			(getattr(localeinfo, "PVP_ORDER_TT_BOOK_CD", "Skill Book / Soul Stone cooldown"), noneTxt, self.POSITIVE_COLOR),
			(getattr(localeinfo, "PVP_ORDER_TT_BOOK_SUCCESS", "Skill Book / Soul Stone success"), "100%", self.POSITIVE_COLOR),
			(getattr(localeinfo, "PVP_ORDER_TT_BIO_CHANCE", "Biologist mission chance"), "+30%", self.POSITIVE_COLOR),
			(getattr(localeinfo, "PVP_ORDER_TT_BIO_CD", "Biologist mission cooldown"), noneTxt, self.POSITIVE_COLOR),
			(getattr(localeinfo, "PVP_ORDER_TT_EXP", "Experience gained"), "+50%", self.POSITIVE_COLOR),
			(getattr(localeinfo, "PVP_ORDER_TT_STONE", "Damage to Metin Stones"), "-100%", self.NEGATIVE_COLOR),
			(getattr(localeinfo, "PVP_ORDER_TT_BOSS", "Damage to Bosses"), "-100%", self.NEGATIVE_COLOR),
		]

		data = [[label, value] for (label, value, color) in rows]
		cellColors = [[0, color] for (label, value, color) in rows]
		if localeinfo.IsARABIC():
			headers.reverse()
			widths.reverse()
			data = [r[::-1] for r in data]
			cellColors = [c[::-1] for c in cellColors]

		colors = [0xff555555, 0xdd1a1a1a, 0x99000000, 0xffffda79, 0xffe6e6e6]
		tbl = ui.Table(TBL_W, HEAD_H, colors)
		tbl.SetParent(self)
		tbl.SetPosition((self.toolTipWidth - TBL_W) / 2, self.toolTipHeight)
		tbl.set_columns(headers, widths)
		for i in xrange(len(data)):
			tbl.add_row(data[i], ROW_H, cellColors[i])
		tbl.Show()
		self.childrenList.append(tbl)

		self.toolTipHeight += tbl.GetHeight() + 6
		self.ResizeToolTip()

	def AddItemData(self, itemVnum, metinSlot, attrSlot = 0, rare_attr_slot = None, flags = 0, unbindTime = 0, window_type = player.INVENTORY, slotIndex = -1, refine_element = None, apply_random_list = None, set_value = 0, transmutation = -1, offlineshopShow = 0, noRender = 0, enchantList=[], iSetValue = 0, restrictInfo = None):
		self.itemVnum = itemVnum
		self.metinSlot = metinSlot

		item.SelectItem(itemVnum)
		itemType = item.GetItemType()
		itemSubType = item.GetItemSubType()

		if not item.GetItemDescription():
			self.__CalculateToolTipWidth()

		if 50026 == itemVnum:
			if 0 != metinSlot:
				name = item.GetItemName()
				if metinSlot[0] > 0:
					name += " "
					name += localeinfo.NumberToMoneyString(metinSlot[0])
				self.SetTitle(name)
				if app.ENABLE_SOUL_BIND_SYSTEM:
					self.__AppendSealInformation(window_type, slotIndex) ## cyh itemseal 2013 11 11
				self.FlushShortcutFooter()
				self.ShowToolTip()
			return

		### Skill Book ###
		if itemType == item.ITEM_TYPE_SKILLBOOK or itemType == item.ITEM_TYPE_SKILLFORGET:
			if metinSlot != 0 and metinSlot[0] == 0:
				self.ClearToolTip()

				self.SetTitle(item.GetItemName())
				self.AppendDescription(item.GetItemDescription(), 26)
				self.AppendDescription(item.GetItemSummary(), 26, self.CONDITION_COLOR)
				self.FlushShortcutFooter()
				self.ShowToolTip()
				return

		### Skill Book ###
		if 50300 == itemVnum:
			if 0 != metinSlot:
				self.__SetSkillBookToolTip(metinSlot[0], localeinfo.TOOLTIP_SKILLBOOK_NAME, 1)
				if app.ENABLE_SOUL_BIND_SYSTEM:
					self.__AppendSealInformation(window_type, slotIndex) ## cyh itemseal 2013 11 11
				self.FlushShortcutFooter()
				self.ShowToolTip()
			return
		elif 70037 == itemVnum:
			if 0 != metinSlot:
				self.__SetSkillBookToolTip(metinSlot[0], localeinfo.TOOLTIP_SKILL_FORGET_BOOK_NAME, 0)
				self.AppendDescription(item.GetItemDescription(), 26)
				self.AppendDescription(item.GetItemSummary(), 26, self.CONDITION_COLOR)
				if app.ENABLE_SOUL_BIND_SYSTEM:
					self.__AppendSealInformation(window_type, slotIndex) ## cyh itemseal 2013 11 11
				self.FlushShortcutFooter()
				self.ShowToolTip()
			return
		elif 70055 == itemVnum:
			if 0 != metinSlot:
				self.__SetSkillBookToolTip(metinSlot[0], localeinfo.TOOLTIP_SKILL_FORGET_BOOK_NAME, 0)
				self.AppendDescription(item.GetItemDescription(), 26)
				self.AppendDescription(item.GetItemSummary(), 26, self.CONDITION_COLOR)
				if app.ENABLE_SOUL_BIND_SYSTEM:
					self.__AppendSealInformation(window_type, slotIndex) ## cyh itemseal 2013 11 11
				self.FlushShortcutFooter()
				self.ShowToolTip()
			return
		###########################################################################################

		if app.ENABLE_SOUL_SYSTEM:
			if item.ITEM_TYPE_SOUL == itemType:
				self.__SoulItemToolTip(itemVnum, metinSlot, flags)
				return

		if itemVnum in (71016, 71046, 71097, 71098):
			self.__CombinedLootBoosterToolTip(itemVnum, metinSlot, attrSlot)
			return

		if slotIndex == -1:
			itemDesc = item.GetItemDescription()
		elif app.USE_ENCHANT_COSTUMES and\
			itemSubType in (item.USE_ENCHANT_BODY_COSTUME,item.USE_ENCHANT_HAIR_COSTUME,item.USE_ENCHANT_WEAPON_COSTUME,getattr(item,"USE_ENCHANT_MOUNT_SKIN",-1),getattr(item,"USE_ENCHANT_PET_SKIN",-2)):
			itemDesc = localeinfo.COSTUME_ENCHANT_DESCRIPTION % (localeinfo.SecondToDHM(item.GetValue(0)))
		else:
			itemDesc = item.GetItemDescription(slotIndex, window_type)

		itemSummary = item.GetItemSummary()

		isCostumeItem = 0
		isCostumeHair = 0
		isCostumeBody = 0
		isCostumeMount = 0
		isCostumeAcce = 0
		isCostumeWeapon = 0

		if app.USE_AURA_SYSTEM:
			isCostumeAura = 0

		if item.ITEM_TYPE_COSTUME == itemType:
			isCostumeItem = 1
			isCostumeHair = item.COSTUME_TYPE_HAIR == itemSubType
			isCostumeBody = item.COSTUME_TYPE_BODY == itemSubType
			if app.USE_MOUNT_COSTUME_SYSTEM:
				isCostumeMount = item.COSTUME_TYPE_MOUNT == itemSubType
			if app.USE_ACCE_SYSTEM:
				isCostumeAcce = item.COSTUME_TYPE_ACCE == itemSubType
			if app.USE_WEAPON_COSTUME_SYSTEM:
				isCostumeWeapon = item.COSTUME_TYPE_WEAPON == itemSubType

			if app.USE_AURA_SYSTEM:
				isCostumeAura = item.COSTUME_TYPE_AURA == itemSubType

		self.__AdjustMaxWidth(attrSlot, itemDesc)
		self.__SetItemTitle(itemVnum, metinSlot, attrSlot,iSetValue)


		if app.ENABLE_GROWTH_PET_SYSTEM and item.ITEM_TYPE_PET == itemType:
			if item.PET_UPBRINGING == itemSubType:
			
				pet_id = metinSlot[2]
				if pet_id:
					(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
					
					self.ClearToolTip()
					self.AppendTextLine(pet_nick, self.TITLE_COLOR)

		### Hair Preview Image ###
		if self.__IsHair(itemVnum):
			self.__AppendHairIcon(itemVnum)
		elif isinstance(self, HyperlinkItemToolTip):
			self.__AppendItemIcon(itemVnum)

		### Description ###
		self.AppendDescription(itemDesc, 26)
		self.AppendDescription(itemSummary, 26, self.CONDITION_COLOR)

		if 99180 == itemVnum and getattr(app, "ENABLE_PVP_ORDER", 0):
			self.__AppendPvPOrderBenefitTable()

		#if item.ITEM_TYPE_GACHA == itemType or\
		#	item.ITEM_TYPE_GIFTBOX == itemType and\
		#	itemVnum != 31374 and itemVnum != 50255 and itemVnum != 50187 and\
		#	itemVnum != 50197 and itemVnum != 50188 and itemVnum != 50189 and\
		#	itemVnum != 50190 and itemVnum != 50191 and itemVnum != 50192 and\
		#	itemVnum != 50193 and itemVnum != 50194 and itemVnum != 50195 and\
		#	itemVnum != 50196 and itemVnum != 50286 and itemVnum != 50285 and\
		#	itemVnum != 26030 and itemVnum != 26031 and itemVnum != 26032 and\
		#	itemVnum != 26033 and itemVnum != 26034 and itemVnum != 26035 and\
		#	itemVnum != 26036 and itemVnum != 26037 and itemVnum != 26038 and\
		#	itemVnum != 26039 and itemVnum != 26040 and itemVnum != 26041 and\
		#	itemVnum != 26042 and itemVnum != 26043 and itemVnum != 26044 and\
		#	itemVnum != 26045 and itemVnum != 26046 and itemVnum != 26047 and\
		#	itemVnum != 26048 and itemVnum != 26049 and itemVnum != 26050 and\
		#	itemVnum != 26051:
		#	# self.__SandikIngoru("d:/ymir work/ui/shift+sag.tga")
		#	# self.AppendTextLine(localeinfo.TOOLTIP_SHOW_BOX, self.SPECIAL_POSITIVE_COLOR)
		#	# self.AppendTextLine(localeinfo.TOOLTIP_SHOW_BOX1, self.SPECIAL_POSITIVE_COLOR)
		#	self.AppendSpace(2)#dream
		#	self.AppendTextLine(localeinfo.TOOLTIP_OPEN_BOX, self.TEXTLINE_2ND_COLOR_DEFAULT)

		if itemVnum >= 20570 and itemVnum <= 20574:
			self.DeclareShortcut(("key_shift", "key_e"), localeinfo.TOOLTIP_QUICKDEACTIVE_CAPE)
			self.DeclareShortcut(("key_ctrl", "key_e"), localeinfo.TOOLTIP_QUICKACTIVE_CAPE)

		if app.ENABLE_GEAR_SETS and itemVnum >= 50880 and itemVnum <= 50889:
			import net
			page = itemVnum - 50880   # the vnum encodes the page directly (robust; no proto Value0 dependency)
			setName = net.GetGearSetName(page)
			if not setName:   # default/un-renamed set, or names not cached yet (loadout window not opened this session)
				setName = localeinfo.FAST_EQUIPMENT_PAGE % localeinfo.NumberToRoman(page + 1)
			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.GEARSET_TOKEN_TOOLTIP % setName, self.SPECIAL_POSITIVE_COLOR)
			dungeonId = net.GetGearSetDungeon(page)
			if dungeonId:
				import uifastequip   # lazy import avoids the uifastequip<->uitooltip circular import at load
				for (dName, dId) in uifastequip.GEARSET_DUNGEONS:
					if dId == dungeonId:
						self.AppendTextLine(localeinfo.GEARSET_TOKEN_DUNGEON % dName, self.NORMAL_COLOR)
						break

		if item.ITEM_TYPE_COSTUME == itemType and item.COSTUME_PET_SKIN == itemSubType:
			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.COSTUME_PET_SKIN_TOOTIP, 0xFF54a0ff)

		if item.ITEM_TYPE_COSTUME == itemType and item.COSTUME_MOUNT_SKIN == itemSubType:
			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.COSTUME_PET_MOUNT_TOOLTIP, 0xFF54a0ff)

		# Buffi SUMMON scroll only: live buffi-summary block. Gate by VNUM (constinfo.BUFFI_SUMMON_VNUMS),
		# NOT subtype -- the client proto reads every buffi item's subtype as 0 unless rebuilt, which
		# would wrongly match the ore / name / recharge / permanent items (91120-91124).
		if constinfo.IS_BUFFI_SUMMON_ITEM(itemVnum):
			self.__AppendBuffiItemInfo(itemVnum)

		### Weapon ###
		if item.ITEM_TYPE_SHINING == itemType:
			GetColor = item.GetValue(0)
			self.__AppendAffectInformation()
			self.__AppendAttributeInformation(attrSlot)
			
			if app.USE_ENCHANT_COSTUMES:
				self.__AppendEnchantInformation(enchantList)
			
			SlotInfo = [localeinfo.TOOLTIP_WEAPON,localeinfo.TOOLTIP_ARMOR , localeinfo.PRIVATESHOPSEARCH_SHINING_SPECIAL]
			self.AppendTextLine(localeinfo.SHINNING_TYPE % SlotInfo[itemSubType],self.CHANGELOOK_ITEMNAME_COLOR )
			self.__AppendLimitInformation()
			bHasRealtimeFlag = 0
			for i in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(i)
				if item.LIMIT_REAL_TIME == limitType:
					bHasRealtimeFlag = 1
			if bHasRealtimeFlag == 1:
				self.AppendMallItemLastTime(metinSlot[0])
			
			if offlineshopShow==0 and noRender==0:
				self.AppendSpace(7)
				if app.USE_OFFLINESHOP and\
					self.isOfflineShopItem:
					self.DeclareShortcut(("key_rclick",), localeinfo.OFFLINESHOP_GET_ITEM)
				# else:
					# self.AppendTextLine(localeinfo.TOOLTIP_RENDER, self.TEXTLINE_2ND_COLOR_DEFAULT)
					# self.AppendSpace(2)
		elif item.ITEM_TYPE_WEAPON == itemType:
			self.__AppendLimitInformation()

			self.AppendSpace(5)

			if item.WEAPON_FAN == itemSubType:
				self.__AppendMagicAttackInfo()
				self.__AppendAttackPowerInfo()
			else:
				self.__AppendAttackPowerInfo()
				self.__AppendMagicAttackInfo()

			self.__AppendAffectInformation()
			if app.ENABLE_APPLY_RANDOM:
				self.__AppendDefaultItemApplyInformation(apply_random_list)
			self.__AppendAttributeInformation(attrSlot)

			if app.ENABLE_ATTR_6TH_7TH:
				self.__AppendAttribute6th7thPossibility(attrSlot)

			if app.USE_ENCHANT_COSTUMES:
				self.__AppendEnchantInformation(enchantList)


			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				self.AppendChangeLookInformation(window_type, slotIndex, transmutation, metinSlot)

			if app.ENABLE_COMBAT_POINTS:
				self.__AppendGearCPInfo(itemVnum, itemSubType)

			self.AppendWearableInformation()

			bHasRealtimeFlag = 0
			if app.ENABLE_QUIVER_SYSTEM:
				if item.WEAPON_QUIVER == itemSubType:
					if not self.isShopItem:
						for i in xrange(item.LIMIT_MAX_NUM):
							(limitType, limitValue) = item.GetLimit(i)

							if item.LIMIT_REAL_TIME == limitType:
								bHasRealtimeFlag = 1

						if 1 == bHasRealtimeFlag:
							self.AppendMallItemLastTime(metinSlot[0])
				else:
					for i in xrange(item.LIMIT_MAX_NUM):
						(limitType, limitValue) = item.GetLimit(i)

						if item.LIMIT_REAL_TIME == limitType:
							bHasRealtimeFlag = 1

					if 1 != bHasRealtimeFlag:
						self.__AppendMetinSlotInfo(metinSlot)
						self.AppendSpace(5)
			else:
				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)

					if item.LIMIT_REAL_TIME == limitType:
						bHasRealtimeFlag = 1

				if 1 != bHasRealtimeFlag:
					self.__AppendMetinSlotInfo(metinSlot)
			
			if app.ENABLE_NEW_USER_CARE:
				if item.WEAPON_QUIVER != itemSubType:
					self.__AppendRealTimeToolTip(itemVnum, metinSlot[0])
			
			if offlineshopShow==0 and noRender==0:
				self.AppendSpace(7)
				if app.USE_OFFLINESHOP and\
					self.isOfflineShopItem:
					self.DeclareShortcut(("key_rclick",), localeinfo.OFFLINESHOP_GET_ITEM)
				# else:
					# self.AppendTextLine(localeinfo.TOOLTIP_RENDER, self.TEXTLINE_2ND_COLOR_DEFAULT)
					# self.AppendSpace(2)
		### Armor ###
		elif item.ITEM_TYPE_ARMOR == itemType:
			self.__AppendLimitInformation()

			defGrade = item.GetValue(1)
			defBonus = item.GetValue(5)*2
			if defGrade > 0:
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_DEF_GRADE % (defGrade+defBonus), self.GetChangeTextLineColor(defGrade))

			self.__AppendMagicDefenceInfo()
			self.__AppendAffectInformation()
			if app.ENABLE_APPLY_RANDOM:
				self.__AppendDefaultItemApplyInformation(apply_random_list)
			self.__AppendAttributeInformation(attrSlot)
			
			if app.USE_ENCHANT_COSTUMES:
				self.__AppendEnchantInformation(enchantList)
			
			# if app.ENABLE_67TH_BONUS:
				# if itemSubType != item.ARMOR_GLOVE:
					# self.__AppendRareAttributeInformation(attrSlot)

			if app.ENABLE_ATTR_6TH_7TH:
				self.__AppendAttribute6th7thPossibility(attrSlot)

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				self.AppendChangeLookInformation(window_type, slotIndex, transmutation, metinSlot)

			if app.ENABLE_COMBAT_POINTS:
				self.__AppendGearCPInfo(itemVnum, itemSubType)

			self.AppendWearableInformation()

			if itemSubType in (item.ARMOR_WRIST, item.ARMOR_NECK, item.ARMOR_EAR):
				self.__AppendAccessoryMetinSlotInfo(metinSlot, constinfo.GET_ACCESSORY_MATERIAL_VNUM(itemVnum, itemSubType), apply_random_list)
			else:
				if app.USE_GLOVE_SYSTEM and itemSubType == item.ARMOR_GLOVE:
					self.__AppendGloveMetinSlotInfo(metinSlot)
				else:
					self.__AppendMetinSlotInfo(metinSlot)

			if itemSubType == item.ARMOR_BODY:
				if offlineshopShow==0 and noRender==0:
					self.AppendSpace(7)
					if app.USE_OFFLINESHOP and\
						self.isOfflineShopItem:
						self.DeclareShortcut(("key_rclick",), localeinfo.OFFLINESHOP_GET_ITEM)
					# else:
						# self.AppendTextLine(localeinfo.TOOLTIP_RENDER, self.TEXTLINE_2ND_COLOR_DEFAULT)
						# self.AppendSpace(2)
		### Ring Slot Item (Not UNIQUE) ###
		elif item.ITEM_TYPE_RING == itemType:
			#self.__AppendLimitInformation()
			self.__AppendAffectInformation()
			if app.ENABLE_APPLY_RANDOM:
				self.__AppendDefaultItemApplyInformation(apply_random_list)
			self.__AppendAttributeInformation(attrSlot)
			
			if app.USE_ENCHANT_COSTUMES:
				self.__AppendEnchantInformation(enchantList)

			if 0 != metinSlot:
				bHasRealtimeFlag = 0

				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)

					if item.LIMIT_REAL_TIME == limitType:
						bHasRealtimeFlag = 1

				if 1 == bHasRealtimeFlag:
					self.AppendMallItemLastTime(metinSlot[0])
				else:
					time = metinSlot[player.METIN_SOCKET_MAX_NUM-1]

					if 1 == item.GetValue(2):
						self.AppendMallItemLastTime(time)
					else:
						self.AppendUniqueItemLastTime(time)

			#self.__AppendAccessoryMetinSlotInfo(metinSlot, 99001)

		### Belt Item ###
		elif item.ITEM_TYPE_BELT == itemType:
			self.__AppendLimitInformation()
			self.__AppendAffectInformation()
			if app.ENABLE_APPLY_RANDOM:
				self.__AppendDefaultItemApplyInformation(apply_random_list)
			self.__AppendAttributeInformation(attrSlot)
			
			if app.USE_ENCHANT_COSTUMES:
				self.__AppendEnchantInformation(enchantList)
			
			if app.ENABLE_67TH_BONUS:
				self.__AppendRareAttributeInformation(attrSlot)

			if osfinfo.SHOW_BELT_SLOTS_TOOLTIP == True:
				self.AppendTextLine("%s: %s " % (localeinfo.TOOLTIP_ITEM_SLOTS, BELT_SLOTS[item.GetValue(0)]), self.SPECIAL_POSITIVE_COLOR)

			self.__AppendAccessoryMetinSlotInfo(metinSlot, constinfo.GET_BELT_MATERIAL_VNUM(itemVnum),apply_random_list)

		elif 0 != isCostumeItem:
			self.__AppendLimitInformation()

			if app.USE_ACCE_SYSTEM and isCostumeAcce:
				## ABSORPTION RATE
				absChance = int(metinSlot[acce.ABSORPTION_SOCKET])
				self.AppendTextLine(localeinfo.TOOLTIP_APPLY_ACCEDRAIN_RATE(absChance), self.CONDITION_COLOR)
				## END ABSOPRTION RATE

				itemAbsorbedVnum = int(metinSlot[acce.ABSORBED_SOCKET])
				if itemAbsorbedVnum:
					## ATTACK / DEFENCE
					item.SelectItem(itemAbsorbedVnum)
					if item.GetItemType() == item.ITEM_TYPE_WEAPON:
						if item.GetItemSubType() == item.WEAPON_FAN:
							self.__AppendMagicAttackInfo(metinSlot[acce.ABSORPTION_SOCKET])
							item.SelectItem(itemAbsorbedVnum)
							self.__AppendAttackPowerInfo(metinSlot[acce.ABSORPTION_SOCKET])
						else:
							self.__AppendAttackPowerInfo(metinSlot[acce.ABSORPTION_SOCKET])
							item.SelectItem(itemAbsorbedVnum)
							self.__AppendMagicAttackInfo(metinSlot[acce.ABSORPTION_SOCKET])
					elif item.GetItemType() == item.ITEM_TYPE_ARMOR:
						defGrade = item.GetValue(1)
						defBonus = item.GetValue(5) * 2
						defGrade = self.CalcAcceValue(defGrade, metinSlot[acce.ABSORPTION_SOCKET])
						defBonus = self.CalcAcceValue(defBonus, metinSlot[acce.ABSORPTION_SOCKET])

						if defGrade > 0:
							self.AppendSpace(5)
							self.AppendTextLine(localeinfo.TOOLTIP_ITEM_DEF_GRADE % (defGrade + defBonus), self.GetChangeTextLineColor(defGrade))

						item.SelectItem(itemAbsorbedVnum)
						self.__AppendMagicDefenceInfo(metinSlot[acce.ABSORPTION_SOCKET])
					## END ATTACK / DEFENCE

					## EFFECT
					item.SelectItem(itemAbsorbedVnum)
					for i in xrange(item.ITEM_APPLY_MAX_NUM):
						(affectType, affectValue) = item.GetAffect(i)
						affectValue = self.CalcAcceValue(affectValue, metinSlot[acce.ABSORPTION_SOCKET])
						affectString = self.__GetAffectString(affectType, affectValue)
						if affectString and affectValue > 0:
							self.AppendTextLine(affectString, self.GetChangeTextLineColor(affectValue))

						item.SelectItem(itemAbsorbedVnum)
					# END EFFECT

					item.SelectItem(itemVnum)
					if app.ENABLE_APPLY_RANDOM:
						self.__AppendAcceDefaultItemApplyInformation(apply_random_list, metinSlot[acce.ABSORPTION_SOCKET])
					self.__AppendAttributeInformation(attrSlot, metinSlot[acce.ABSORPTION_SOCKET])
					
					if app.USE_ENCHANT_COSTUMES:
						self.__AppendEnchantInformation(enchantList)
					# END ATTR
				else:
					# ATTR
					self.__AppendAttributeInformation(attrSlot)
					
					if app.USE_ENCHANT_COSTUMES:
						self.__AppendEnchantInformation(enchantList)
					
				if offlineshopShow==0 and noRender==0:
					self.AppendSpace(7)
					if app.USE_OFFLINESHOP and\
						self.isOfflineShopItem:
						self.DeclareShortcut(("key_rclick",), localeinfo.OFFLINESHOP_GET_ITEM)
					# else:
						# self.AppendTextLine(localeinfo.TOOLTIP_RENDER, self.TEXTLINE_2ND_COLOR_DEFAULT)
						# self.AppendSpace(2)
			elif app.USE_AURA_SYSTEM and isCostumeAura:
				if app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
					self.__AppendAffectInformation()
					self.__AppendAttributeInformation(attrSlot)

					if app.USE_ENCHANT_COSTUMES:
						self.__AppendEnchantInformation(enchantList)

					self.__AppendAffectInformationAura(window_type, slotIndex, metinSlot)
				else:
					self.__AppendAffectInformationAura(window_type, slotIndex, metinSlot)
					self.__AppendAuraItemAffectInformation(itemVnum, window_type, slotIndex, metinSlot)
					self.__AppendAttributeInformationAura(window_type, slotIndex, attrSlot, metinSlot)
					self.__AppendAuraBoostMetinSlotInfo(itemVnum, window_type, slotIndex, metinSlot)
			else:
				self.__AppendAffectInformation()
				self.__AppendAttributeInformation(attrSlot)

				if app.USE_ENCHANT_COSTUMES:
					self.__AppendEnchantInformation(enchantList)

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				costumeSubType = item.GetItemSubType()

				if costumeSubType == item.COSTUME_TYPE_WEAPON or\
					costumeSubType == item.COSTUME_TYPE_BODY or\
					costumeSubType == item.COSTUME_TYPE_MOUNT or\
					(app.USE_ACCE_SYSTEM and\
					costumeSubType == item.COSTUME_TYPE_ACCE):
					self.AppendChangeLookInformation(window_type, slotIndex, transmutation, metinSlot)

			self.AppendWearableInformation()

			bHasRealtimeFlag = 0
			bHasRealtimeFirstFlag = 0

			if app.USE_ACCE_SYSTEM:
				if item.GetItemSubType() != item.COSTUME_TYPE_ACCE:
					for i in xrange(item.LIMIT_MAX_NUM):
						(limitType, limitValue) = item.GetLimit(i)

						if item.LIMIT_REAL_TIME == limitType:
							bHasRealtimeFlag = 1

						if item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
							bHasRealtimeFirstFlag = 1

					if app.USE_MOUNT_COSTUME_SYSTEM:
						if item.GetItemSubType() == item.COSTUME_TYPE_MOUNT:
							if not bHasRealtimeFirstFlag:
								if 1 == bHasRealtimeFlag:
									if app.ENABLE_COSTUME_EXTENDED_RECHARGE:
										self.AppendMallItemLastTimeEx(metinSlot[0])
									else:
										self.AppendMallItemLastTime(metinSlot[0])
								else:
									time = metinSlot[player.METIN_SOCKET_MAX_NUM-1]

									if 1 == item.GetValue(2):
										self.AppendMallItemLastTime(time)
									else:
										if time <= 0:
											self.AppendSpace(5)
											self.AppendTextLine(localeinfo.INFINITE_USE, self.CONDITION_COLOR)
										else:
											self.AppendUniqueItemLastTime(time)
						else:
							if 1 == bHasRealtimeFlag:
								if app.ENABLE_COSTUME_EXTENDED_RECHARGE:
									self.AppendMallItemLastTimeEx(metinSlot[0])
								else:
									self.AppendMallItemLastTime(metinSlot[0])
					else:
						if 1 == bHasRealtimeFlag:
							if app.ENABLE_COSTUME_EXTENDED_RECHARGE:
								self.AppendMallItemLastTimeEx(metinSlot[0])
							else:
								self.AppendMallItemLastTime(metinSlot[0])
			else:
				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)

					if item.LIMIT_REAL_TIME == limitType:
						bHasRealtimeFlag = 1

					if item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
						bHasRealtimeFirstFlag = 1

				if app.USE_MOUNT_COSTUME_SYSTEM:
					if item.GetItemSubType() == item.COSTUME_TYPE_MOUNT:
						if not bHasRealtimeFirstFlag:
							if 1 == bHasRealtimeFlag:
								if app.ENABLE_COSTUME_EXTENDED_RECHARGE:
									self.AppendMallItemLastTimeEx(metinSlot[0])
								else:
									self.AppendMallItemLastTime(metinSlot[0])
							else:
								time = metinSlot[player.METIN_SOCKET_MAX_NUM - 1]

								if 1 == item.GetValue(2):
									self.AppendMallItemLastTime(time)
								else:
									if time <= 0:
										self.AppendSpace(5)
										self.AppendTextLine(localeinfo.INFINITE_USE, self.CONDITION_COLOR)
									else:
										self.AppendUniqueItemLastTime(time)
					else:
						if 1 == bHasRealtimeFlag:
							if app.ENABLE_COSTUME_EXTENDED_RECHARGE:
								self.AppendMallItemLastTimeEx(metinSlot[0])
							else:
								self.AppendMallItemLastTime(metinSlot[0])
				else:
					if 1 == bHasRealtimeFlag:
						if app.ENABLE_COSTUME_EXTENDED_RECHARGE:
							self.AppendMallItemLastTimeEx(metinSlot[0])
						else:
							self.AppendMallItemLastTime(metinSlot[0])

			if app.USE_AURA_SYSTEM and isCostumeAura and app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
				self.__AppendAccessoryMetinSlotInfo(metinSlot, item.ITEM_VNUM_AURA_ACCESORY_ADD)

			if osfinfo.SHOW_USE_IMAGE_TEXT_LINE == True:
				if item.GetItemSubType() == item.COSTUME_TYPE_BODY or\
					item.GetItemSubType() == item.COSTUME_TYPE_HAIR or\
					item.GetItemSubType() == item.COSTUME_TYPE_WEAPON or\
					(app.USE_MOUNT_COSTUME_SYSTEM and\
						item.GetItemSubType() == item.COSTUME_TYPE_MOUNT):
						if offlineshopShow==0 and noRender==0:
							self.AppendSpace(7)
							if app.USE_OFFLINESHOP and\
								self.isOfflineShopItem:
								self.DeclareShortcut(("key_rclick",), localeinfo.OFFLINESHOP_GET_ITEM)
							# else:
								# self.AppendTextLine(localeinfo.TOOLTIP_RENDER, self.TEXTLINE_2ND_COLOR_DEFAULT)
								# self.AppendSpace(2)
		## Rod ##				
		elif item.ITEM_TYPE_ROD == itemType:
			if 0 != metinSlot:
				curLevel = item.GetValue(0) / 10
				curEXP = metinSlot[0]
				maxEXP = item.GetValue(2)
				self.__AppendLimitInformation()
				self.__AppendRodInformation(curLevel, curEXP, maxEXP)
			self.__AppendFishingRodBonus(window_type, slotIndex)

		## Pick ##
		elif item.ITEM_TYPE_PICK == itemType:
			if 0 != metinSlot:
				curLevel = item.GetValue(0) / 10
				curEXP = metinSlot[0]
				maxEXP = item.GetValue(2)
				self.__AppendLimitInformation()
				self.__AppendPickInformation(curLevel, curEXP, maxEXP)
			self.__AppendMiningPickBonus(window_type, slotIndex)

		## Lottery ##
		elif item.ITEM_TYPE_LOTTERY == itemType:
			if 0 != metinSlot:
				ticketNumber = int(metinSlot[0])
				stepNumber = int(metinSlot[1])

				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.TOOLTIP_LOTTERY_STEP_NUMBER % (stepNumber), self.NORMAL_COLOR)
				self.AppendTextLine(localeinfo.TOOLTIP_LOTTO_NUMBER % (ticketNumber), self.NORMAL_COLOR);

		### Metin ###
		elif item.ITEM_TYPE_METIN == itemType:
			self.AppendMetinInformation()
			self.AppendMetinWearInformation()

		### Fish ###
		elif item.ITEM_TYPE_FISH == itemType:
			if 0 != metinSlot:
				self.__AppendFishInfo(metinSlot[0])

		## item.ITEM_TYPE_BLEND
		elif item.ITEM_TYPE_BLEND == itemType:
			self.__AppendLimitInformation()

			if metinSlot:
				affectType = metinSlot[0]
				affectValue = metinSlot[1]
				time = metinSlot[2]
				# Shop / item-mall preview shows the bare proto vnum with no rolled
				# sockets (affectType 0). Fall back to the baked blend table so the
				# effect + duration still display. game_data.GetBlendInfo is fail-soft.
				if 0 == affectType:
					blendInfo = game_data.GetBlendInfo(itemVnum)
					if blendInfo:
						(affectType, affectValue, time) = blendInfo
				self.AppendSpace(5)
				affectText = self.__GetAffectString(affectType, affectValue)

				self.AppendTextLine(affectText, self.NORMAL_COLOR)

				if app.ENABLE_EXTENDED_BLEND_AFFECT:
					status = metinSlot[3]

					self.AppendSpace(5)
					if status != 0:
						self.AppendTextLine(localeinfo.BLEND_ITEM_TOOLTIP_APPLY, 0xff86e57f) # RGB(134, 229, 127)
					else:
						self.AppendTextLine(localeinfo.BLEND_ITEM_TOOLTIP_UNAPPLIED, 0xfff15f5f) # RGB(241, 95, 95)

					self.AppendSpace(5)
					if time > item.MIN_INFINITE_DURATION:
						self.AppendTextLine(localeinfo.INFINITE_USE, self.CONDITION_COLOR)
					else:
						if time > 0:
							endTime = app.GetGlobalTimeStamp() + time
							leftSec = max(0, endTime - app.GetGlobalTimeStamp())
							self.AppendTextLine(localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHMS(leftSec), self.NORMAL_COLOR)
						else:
							self.AppendTextLine(localeinfo.BLEND_ITEM_TOOLTIP_NO_TIME)
				else:
					if time > 0:
						minute = (time / 60)
						second = (time % 60)
						timeString = localeinfo.TOOLTIP_POTION_TIME

						if minute > 0:
							timeString += str(minute) + localeinfo.TOOLTIP_POTION_MIN
						if second > 0:
							timeString += " " + str(second) + localeinfo.TOOLTIP_POTION_SEC

						self.AppendTextLine(timeString)
					#else:
					#	self.AppendTextLine(localeinfo.BLEND_POTION_NO_TIME)
			else:
				self.AppendTextLine("BLEND_POTION_NO_INFO")

		elif item.ITEM_TYPE_UNIQUE == itemType:
			self.__AppendAffectInformation()
			if 0 != metinSlot:
				bHasRealtimeFlag = 0

				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)

					if item.LIMIT_REAL_TIME == limitType:
						bHasRealtimeFlag = 1

				if 1 == bHasRealtimeFlag:
					self.AppendMallItemLastTime(metinSlot[0])
				else:
					time = metinSlot[player.METIN_SOCKET_MAX_NUM-1]

					if 1 == item.GetValue(2):
						self.AppendMallItemLastTime(time)
					else:
						self.AppendUniqueItemLastTime(time)

		elif item.ITEM_TYPE_EX == itemType:
			if 0 != metinSlot:
				bHasRealtimeFlag = 0

				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)

					if item.LIMIT_REAL_TIME == limitType:
						bHasRealtimeFlag = 1

				if 1 == bHasRealtimeFlag:
					self.AppendMallItemLastTime(metinSlot[0])
				else:
					time = metinSlot[player.METIN_SOCKET_MAX_NUM-1]

					if 1 == item.GetValue(2):
						self.AppendMallItemLastTime(time)
					else:
						self.AppendUniqueItemLastTime(time)


		### Use ###
		elif item.ITEM_TYPE_USE == itemType:
			self.__AppendLimitInformation()

			if item.USE_POTION == itemSubType or item.USE_POTION_NODELAY == itemSubType:
				self.__AppendPotionInformation()

			elif item.USE_ABILITY_UP == itemSubType:# to do : fish items
				self.__AppendAbilityPotionInformation()
				if itemVnum >= 37863 and itemVnum <= 37892:
					self.AppendTextLine(getattr(localeinfo, "TOOLTIP_FISH_PERMANENT", "Permanent until replaced or removed"), self.SPECIAL_POSITIVE_COLOR)
				elif itemVnum >= 27863 and itemVnum <= 27892:
					self.AppendTextLine(getattr(localeinfo, "TOOLTIP_FISH_COMBAT_TIME", "Drains only while fighting"), self.NORMAL_COLOR)

			# Item-triggered shop key (ENABLE_ITEM_SHOPS): right-click opens its shop.
			# Guard on app.ENABLE_ITEM_SHOPS first -- item.USE_OPEN_SHOP is only exposed
			# when the client is built with the flag, so the short-circuit avoids an
			# AttributeError on flag-off builds.
			elif app.ENABLE_ITEM_SHOPS and item.USE_OPEN_SHOP == itemSubType:
				self.DeclareShortcut(("key_rclick",), localeinfo.ITEMSHOPS_TOOLTIP_RCLICK)

			if 27989 == itemVnum or 76006 == itemVnum:
				if 0 != metinSlot:
					useCount = int(metinSlot[0])

					self.AppendSpace(5)
					self.AppendTextLine(localeinfo.TOOLTIP_REST_USABLE_COUNT % (6 - useCount), self.NORMAL_COLOR)

			elif 50004 == itemVnum:
				if 0 != metinSlot:
					useCount = int(metinSlot[0])

					self.AppendSpace(5)
					self.AppendTextLine(localeinfo.TOOLTIP_REST_USABLE_COUNT % (10 - useCount), self.NORMAL_COLOR)

			elif constinfo.IS_AUTO_POTION(itemVnum):
				if 0 != metinSlot:
					isActivated = int(metinSlot[0])
					usedAmount = float(metinSlot[1])
					totalAmount = float(metinSlot[2])
					if 0 == totalAmount:
						totalAmount = 1
					
					self.AppendSpace(5)
					
					if 0 != isActivated:
						self.AppendTextLine("(%s)" % (localeinfo.TOOLTIP_AUTO_POTION_USING), self.SPECIAL_POSITIVE_COLOR)
						self.AppendSpace(5)
					
					if app.USE_INFINITE_AUTO_RECOVERY_POTIONS and\
					itemVnum not in [72731, 72732]:
						self.AppendTextLine(localeinfo.TOOLTIP_AUTO_POTION_REST % (100.0 - ((usedAmount / totalAmount) * 100.0)), self.POSITIVE_COLOR)
					else:
						self.AppendTextLine(localeinfo.TOOLTIP_AUTO_POTION_REST % (100.0 - ((usedAmount / totalAmount) * 100.0)), self.POSITIVE_COLOR)
			elif app.ENABLE_LOCATION_SCROLL_REWORK and locationscroll.IsLocationScroll(itemVnum):
				locationscroll.AppendTooltip(self, metinSlot)

			elif not app.ENABLE_LOCATION_SCROLL_REWORK and itemVnum in WARP_SCROLLS:
				if 0 != metinSlot:
					xPos = int(metinSlot[0])
					yPos = int(metinSlot[1])

					if xPos != 0 and yPos != 0:
						(mapName, xBase, yBase) = background.GlobalPositionToMapInfo(xPos, yPos)

						localeMapName = localeinfo.MINIMAP_ZONE_NAME_DICT.get(mapName, "")

						self.AppendSpace(5)

						if localeMapName != "":
							self.AppendTextLine(localeinfo.TOOLTIP_MEMORIZED_POSITION % (localeMapName, int(xPos-xBase)/100, int(yPos-yBase)/100), self.NORMAL_COLOR)
						else:
							self.AppendTextLine(localeinfo.TOOLTIP_MEMORIZED_POSITION_ERROR % (int(xPos)/100, int(yPos)/100), self.NORMAL_COLOR)
							dbg.TraceError("NOT_EXIST_IN_MINIMAP_ZONE_NAME_DICT: %s" % mapName)
			#####
			if item.USE_SPECIAL == itemSubType:
				bHasRealtimeFlag = 0
				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)

					if item.LIMIT_REAL_TIME == limitType:
						bHasRealtimeFlag = 1

				if 1 == bHasRealtimeFlag:
					self.AppendMallItemLastTime(metinSlot[0])
				else:
					if 0 != metinSlot:
						time = metinSlot[player.METIN_SOCKET_MAX_NUM-1]

						if 1 == item.GetValue(2):
							self.AppendMallItemLastTime(time)

			elif item.USE_TIME_CHARGE_PER == itemSubType:
				bHasRealtimeFlag = 0
				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)
					if item.LIMIT_REAL_TIME == limitType:
						bHasRealtimeFlag = 1
				
				if self.isShopItemNpc:
					self.AppendTextLine(localeinfo.TOOLTIP_TIME_CHARGER_PER(100))
				else:
					if metinSlot[2]:
						self.AppendTextLine(localeinfo.TOOLTIP_TIME_CHARGER_PER(metinSlot[2]))
					else:
						self.AppendTextLine(localeinfo.TOOLTIP_TIME_CHARGER_PER(item.GetValue(0)))
				
				if 1 == bHasRealtimeFlag:
					self.AppendMallItemLastTime(metinSlot[0])
			elif item.USE_TIME_CHARGE_FIX == itemSubType:
				bHasRealtimeFlag = 0
				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)

					if item.LIMIT_REAL_TIME == limitType:
						bHasRealtimeFlag = 1

				if metinSlot[2]:
					self.AppendTextLine(localeinfo.TOOLTIP_TIME_CHARGER_FIX(metinSlot[2]))
				else:
					self.AppendTextLine(localeinfo.TOOLTIP_TIME_CHARGER_FIX(item.GetValue(0)))

				if 1 == bHasRealtimeFlag:
					self.AppendMallItemLastTime(metinSlot[0])
			elif app.USE_ENCHANT_COSTUMES and\
				itemSubType in (item.USE_ENCHANT_BODY_COSTUME,item.USE_ENCHANT_HAIR_COSTUME,item.USE_ENCHANT_WEAPON_COSTUME,getattr(item,"USE_ENCHANT_MOUNT_SKIN",-1),getattr(item,"USE_ENCHANT_PET_SKIN",-2)):
				self.AppendSpace(5)
				for i in xrange(item.ITEM_APPLY_MAX_NUM):
					(affectType, affectValue) = item.GetAffect(i)
					if affectType and affectValue:
						affectString = self.__GetAffectString(affectType, affectValue)
						self.AppendTextLine(affectString, self.SPECIAL_TITLE_COLOR)
		elif item.ITEM_TYPE_QUEST == itemType and item.QUEST_PET != itemSubType:

			if 79000 == itemVnum:
				if 0 != metinSlot:
					useCount = int(metinSlot[1])
					self.AppendSpace(5)
					self.AppendTextLine(localeinfo.BUFF_TEXT_3 , self.ITEM_BUFF_RATE_COLOR)
					self.AppendTextLine(localeinfo.BUFF_TEXT_7  %(25 - useCount), self.ITEM_BUFF_USAGE_COLOR)

			if 79001 == itemVnum:
				if 0 != metinSlot:
					useCount = int(metinSlot[1])

					self.AppendSpace(5)
					self.AppendTextLine(localeinfo.BUFF_TEXT_3 , self.ITEM_BUFF_RATE_COLOR)
					self.AppendTextLine(localeinfo.BUFF_TEXT_7  %(25 - useCount), self.ITEM_BUFF_USAGE_COLOR)

			if 79002 == itemVnum:
				if 0 != metinSlot:
					useCount = int(metinSlot[1])

					self.AppendSpace(5)
					self.AppendTextLine(localeinfo.BUFF_TEXT_4 , self.ITEM_BUFF_RATE_COLOR)
					self.AppendTextLine(localeinfo.BUFF_TEXT_7  %(25 - useCount), self.ITEM_BUFF_USAGE_COLOR)

			if 79003 == itemVnum:
				if 0 != metinSlot:
					useCount = int(metinSlot[1])

					self.AppendSpace(5)
					self.AppendTextLine(localeinfo.BUFF_TEXT_3 , self.ITEM_BUFF_RATE_COLOR)
					self.AppendTextLine(localeinfo.BUFF_TEXT_7  %(25 - useCount), self.ITEM_BUFF_USAGE_COLOR)

					
			if 79004 == itemVnum:
				if 0 != metinSlot:
					useCount = int(metinSlot[1])

					self.AppendSpace(5)
					self.AppendTextLine(localeinfo.BUFF_TEXT_3 , self.ITEM_BUFF_RATE_COLOR)
					self.AppendTextLine(localeinfo.BUFF_TEXT_7  %(25 - useCount), self.ITEM_BUFF_USAGE_COLOR)

			if 79005 == itemVnum:
				if 0 != metinSlot:
					useCount = int(metinSlot[1])

					self.AppendSpace(5)
					self.AppendTextLine(localeinfo.BUFF_TEXT_4 , self.ITEM_BUFF_RATE_COLOR)
					self.AppendTextLine(localeinfo.BUFF_TEXT_7  %(25 - useCount), self.ITEM_BUFF_USAGE_COLOR)


			if app.USE_PVP_TOURNAMENT and\
				itemVnum == 50999 and\
				metinSlot[0]:
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.MONEY_BAG_TOOLTIP % localeinfo.NumberToStringDotted(metinSlot[0]))
			
			#if itemVnum >= 53001 and itemVnum <= 53306:
			self.AppendSpace(5)
			
			for g in xrange(item.ITEM_APPLY_MAX_NUM):
				(affectType, affectValue) = item.GetAffect(g)
				affectString = self.__GetAffectString(affectType, affectValue)
				if affectString:
					affectColor = self.GetChangeTextLineColor(affectValue)
					self.AppendTextLine(affectString, affectColor)

			for i in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(i)

				if item.LIMIT_REAL_TIME == limitType:
					self.AppendMallItemLastTime(metinSlot[0])
		
		# app.ENABLE_PET_SYSTEM
		# elif item.ITEM_TYPE_QUEST == itemType and item.QUEST_PET == itemSubType:
			# self.__AppendAffectInformation()
			# self.__AppendAttributeInformation(attrSlot)
			# 
			# if app.USE_ENCHANT_COSTUMES:
			# 	self.__AppendEnchantInformation(enchantList)
			# 
			# for i in xrange(item.LIMIT_MAX_NUM):
				# (limitType, limitValue) = item.GetLimit(i)

				# if item.LIMIT_REAL_TIME == limitType:
					# self.AppendMallItemLastTime(metinSlot[0])

			# self.AppendSpace(5)
			# self.AppendTextLine("|Ikey/mouse_right|i - %s" % localeinfo.TOOLTIP_ITEM_SUMMON)
		elif item.ITEM_TYPE_QUEST == itemType and item.QUEST_PET == itemSubType:
			if osfinfo.PET_ITEM_ATTR_TOOLTIP == True:
				self.__AppendAffectInformation()
				self.__AppendAttributeInformation(attrSlot)
				
				if app.USE_ENCHANT_COSTUMES:
					self.__AppendEnchantInformation(enchantList)
			
			for i in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(i)

				if item.LIMIT_REAL_TIME == limitType:
					self.AppendMallItemLastTime(metinSlot[0])

			if osfinfo.SHOW_USE_IMAGE_TEXT_LINE == True:
				self.DeclareShortcut(("key_rclick",), localeinfo.TOOLTIP_ITEM_SUMMON)

			if offlineshopShow==0 and noRender==0:
				self.AppendSpace(7)
				if app.USE_OFFLINESHOP and\
					self.isOfflineShopItem:
					self.DeclareShortcut(("key_rclick",), localeinfo.OFFLINESHOP_GET_ITEM)
				# else:
					# self.AppendTextLine(localeinfo.TOOLTIP_RENDER, self.TEXTLINE_2ND_COLOR_DEFAULT)
					# self.AppendSpace(2)

		elif item.ITEM_TYPE_DS == itemType:
			self.AppendTextLine(self.__DragonSoulInfoString(itemVnum))

			if app.ENABLE_DS_SET:
				if window_type == player.EQUIPMENT and self.interface and self.interface.wndDragonSoul:
					self.__AppendDragonSoulAttributeInformation(attrSlot, itemVnum / 10000, self.interface.wndDragonSoul.GetDSSetGrade())
				else:
					self.__AppendDragonSoulAttributeInformation(attrSlot)
			else:
				self.__AppendAttributeInformation(attrSlot)
				
				if app.USE_ENCHANT_COSTUMES:
					self.__AppendEnchantInformation(enchantList)
		elif app.ENABLE_GROWTH_PET_SYSTEM and item.ITEM_TYPE_PET == itemType:		
			if item.PET_EGG == itemSubType:
				if window_type == player.INVENTORY:
					self.__AppendPetEggItemInformation(metinSlot)
				else:
					self.__AppendPetEggItemInformation(metinSlot, True)
						
			elif item.PET_UPBRINGING == itemSubType:
				self.__AppendUpBringingPetItemInfomation(metinSlot)
				
			elif item.PET_BAG == itemSubType:
				self.__AppendPetBagItemInfomation(metinSlot)

			elif item.PET_SKILL == itemSubType:
				self.__AppendPetSkillBookInfo()
		else:
			self.__AppendLimitInformation()

		# if item.ITEM_TYPE_GIFTBOX == itemType:
			# for i in xrange(item.LIMIT_MAX_NUM):
				# (limitType, limitValue) = item.GetLimit(i)

				# if item.LIMIT_REAL_TIME == limitType:
					# self.AppendMallItemLastTime(metinSlot[0])

		if app.ENABLE_GROWTH_PET_SYSTEM:
			if not (item.ITEM_TYPE_PET == itemType and item.PET_BAG == itemSubType):
				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)

					if item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
						self.AppendRealTimeStartFirstUseLastTime(item, metinSlot, i)

					elif item.LIMIT_TIMER_BASED_ON_WEAR == limitType:
						self.AppendTimerBasedOnWearLastTime(metinSlot)
		else:
			for i in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(i)

				if item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
					self.AppendRealTimeStartFirstUseLastTime(item, metinSlot, i)

				elif item.LIMIT_TIMER_BASED_ON_WEAR == limitType:
					self.AppendTimerBasedOnWearLastTime(metinSlot)

		if self.itemVnum in [79505, 79506]:
			if 0 != metinSlot[0]:
				self.AppendMallItemLastTime(metinSlot[0])

		# if app.ENABLE_10TH_EVENT:
		if self.itemVnum in [25101, 25103]:
			if 0 != metinSlot[0]:
				self.AppendMallItemLastTime(metinSlot[0])

		# if app.ENABLE_2017_RAMADAN:
		if self.itemVnum in [30315, 30317, 30318, 50183]:
			if 0 != metinSlot[0]:
				self.AppendMallItemLastTime(metinSlot[0])

		# if app.ENABLE_MINI_GAME_YUTNORI:
		if self.itemVnum in [79507, 79508]:
			if 0 != metinSlot[0]:
				self.AppendMallItemLastTime(metinSlot[0])

		#if app.ENABLE_BOSS_BOX:
		if item.ITEM_TYPE_GACHA == itemType:
			if metinSlot:
				useCount = int(metinSlot[0])

				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.TOOLTIP_REST_USABLE_COUNT % useCount, grp.GenerateColor(0.6705, 0.9490, 0.0, 1.0))

				if itemVnum == 71150:
					leftSec = max(0, metinSlot[1] - app.GetGlobalTimeStamp())
					if leftSec > 0:
						self.AppendSpace(5)
						self.AppendTextLine(localeinfo.TOOLTIP_ITEM_GACHA_EASTER_EGG % (localeinfo.SecondToDHM(leftSec)), self.NEW_RED)

		if app.ENABLE_SOUL_BIND_SYSTEM:
			self.__AppendSealInformation(window_type, slotIndex) ## cyh itemseal 2013 11 11

		if app.ENABLE_EQUIPMENT_RESTRICTION:
			self.__AppendRestrictionInformation(window_type, slotIndex, restrictInfo)


		if osfinfo.SHOW_ITEM_VNUM_TOOTIP == true:
			if chr.IsGameMaster(player.GetMainCharacterIndex()):
				if app.USE_OFFLINESHOP_EXTENDED_SLOTS and itemVnum == offlineshop.OFFLINESHOP_LOCKED_SLOT_ITEMVNUM:
					pass
				else:
					self.AppendSpace(5)
					self.AppendTextLine("VNUM %d" % itemVnum, self.NEW_GREEN)

		if constinfo.AUTO_CHEST_ACTIVE and itemVnum in game_data.autoChestDict:
			self.__AppendAutoChestInfo(itemVnum)

		# "Nx <item> will transform into: <result>" preview (ENABLE_ITEM_TRANSFORM),
		# placed directly under the item's own info, above the shortcuts footer.
		self.__AppendItemTransformInfo(itemVnum)

		self.AppendSpace(7)
		self.AppendAntiflagInformation(itemVnum, window_type, slotIndex)

		if osfinfo.SHOW_SELL_IMAGE_TEXT_LINE == True and not self.isShopItem:
			if slotIndex < player.EQUIPMENT_SLOT_START:
				if not player.IsAntiFlagBySlot(slotIndex, item.ANTIFLAG_SELL):
					if app.ENABLE_SWITCHBOT and window_type == player.SWITCHBOT:
						pass
					else:
						self.DeclareShortcut(("key_ctrl", "key_x", "key_lclick"), localeinfo.TOOLTIP_SHOP_REMOVE)

		if isCostumeMount:
			self.DeclareShortcut(("key_shift", "key_rclick"), localeinfo.MOUNT_INFO_TOOLTIP)

		if app.ENABLE_SWITCHBOT and window_type == player.SWITCHBOT:
			if app.USE_ITEM_ATTR_BACKUP_MODE and itemType == item.ITEM_TYPE_WEAPON and itemSubType in [item.WEAPON_SWORD, item.WEAPON_DAGGER, item.WEAPON_BOW, item.WEAPON_TWO_HANDED, item.WEAPON_BELL, item.WEAPON_FAN, item.WEAPON_CLAW]:
				self.AppendSpace(8)
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_ATTR_BACKUP_MODE)

				if player.GetItemBackup(window_type, slotIndex):
					self.AppendTextLine(localeinfo.TOOLTIP_ITEM_ATTR_BACKUP_MODE_ON, self.NEW_GREEN)
					self.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_ITEM_ATTR_BACKUP_MODE_DECIDE, self.NEW_RED)
				else:
					self.AppendTextLine(localeinfo.TOOLTIP_ITEM_ATTR_BACKUP_MODE_OFF, self.NEW_RED)
					self.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_ITEM_ATTR_BACKUP_MODE_ENABLE, self.NEW_GREEN)
		else:
			if app.ENABLE_RENDER_TARGET:
				self.__AppendRenderTarget(itemVnum)

		# Check if item is a mission submit target
		if app.ENABLE_MISSION_QUEST:
			missionProgress = missionhelper.GetItemMissionProgress(itemVnum)
			if missionProgress:
				progress, maxProgress, categoryName = missionProgress
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.MISSIONLIST_ITEM_TOOLTIP % (categoryName, progress, maxProgress), self.POSITIVE_COLOR)

		### Auto Skill Reader: append "used to level up" + skill icon + skill name to the normal tooltip ###
		if app.__AUTO_SKILL_READER__:
			import uiAutoSkillReader
			bookInfo = uiAutoSkillReader.GetBookTooltipInfo(itemVnum)
			if bookInfo:
				self.__AppendAutoSkillBookInfo(bookInfo)

		if not self.isShopItem:
			self.FlushShortcutFooter()

		self.ShowToolTip()

	def __AppendAutoChestInfo(self, itemVnum):
		amounts = game_data.autoChestDict.get(itemVnum)
		if not amounts or len(amounts) < 3:
			return

		cols = max(12, DESC_WESTERN_MAX_COLS * int(self.toolTipWidth) / DESC_WESTERN_MAX_WIDTH)

		self.AppendSpace(5)
		for line in SplitDescription(LocaleText("AUTO_CHEST_TT_HEADER", "This chest gives one of these"), cols):
			self.AppendTextLine(line, self.NORMAL_COLOR)

		for amount in amounts[:3]:
			self.AppendTextLine(localeinfo.NumberToMoneyString(amount), self.SPECIAL_POSITIVE_COLOR_GOLD)

		self.AppendSpace(5)

		# No clock for this vnum means the player holds none of it -- the wiki page and a
		# just-looted chest both land here. A bar with nothing to count would be noise.
		if itemVnum not in constinfo.AUTO_CHEST_DEADLINES:
			hint = LocaleText("AUTO_CHEST_TT_IDLE", "Opens %d min after looting") % (game_data.autoChestInterval / 60)
			for line in SplitDescription(hint, cols):
				self.AppendTextLine(line, self.NORMAL_COLOR)
			return

		gauge = AutoChestGauge()
		gauge.SetParent(self)
		gauge.MakeGauge(int(self.toolTipWidth) - 24, "yellow")
		gauge.SetPosition(12, self.toolTipHeight)
		gauge.Show()

		self.childrenList.append(gauge)
		self.toolTipHeight += gauge.GetHeight() + 4
		self.ResizeToolTip()

		gauge.SetTimerLine(itemVnum, self.AppendTextLine("", self.NORMAL_COLOR))

	# Show what a gather-material transforms into once the player collects enough.
	# Data is baked offline into cl_item_transform.json (tools/wiki_transform_baker)
	# and loaded by game_data.py. Fail-soft: empty dict -> nothing rendered.
	def __AppendItemTransformInfo(self, itemVnum):
		info = game_data.itemTransformDict.get(itemVnum)
		if not info:
			return

		resultVnum = info.get("result", 0)
		needCount = info.get("count", 0)
		if not resultVnum or not needCount:
			return

		# Header line: "10x Primordial Fragment will transform into:" (neutral, centered).
		item.SelectItem(itemVnum)
		srcName = item.GetItemName()
		self.AppendSpace(5)
		self.AppendTextLine(localeinfo.TOOLTIP_ITEM_TRANSFORM_HEADER % (needCount, srcName), self.NORMAL_COLOR)

		# Result icon, horizontally centered on its own row for readability.
		item.SelectItem(resultVnum)

		iconImage = ui.ImageBox()
		iconImage.SetParent(self)
		iconImage.Show()
		try:
			iconImage.LoadImage(item.GetIconImageFileName())
		except:
			dbg.TraceError("ItemToolTip.__AppendItemTransformInfo() - bad icon for vnum %d" % resultVnum)
		self.childrenList.append(iconImage)

		iconImage.SetPosition((self.toolTipWidth - iconImage.GetWidth()) / 2, self.toolTipHeight)
		self.toolTipHeight += iconImage.GetHeight() + 4
		self.ResizeToolTip()

		# Result name, centered below the icon and highlighted (gold).
		self.AppendTextLine(item.GetItemName(), self.SPECIAL_TITLE_COLOR)

	def __DragonSoulInfoString (self, dwVnum):
		step = (dwVnum / 100) % 10
		refine = (dwVnum / 10) % 10
		if 0 == step:
			return localeinfo.DRAGON_SOUL_STEP_LEVEL1 + " " + localeinfo.DRAGON_SOUL_STRENGTH(refine)
		elif 1 == step:
			return localeinfo.DRAGON_SOUL_STEP_LEVEL2 + " " + localeinfo.DRAGON_SOUL_STRENGTH(refine)
		elif 2 == step:
			return localeinfo.DRAGON_SOUL_STEP_LEVEL3 + " " + localeinfo.DRAGON_SOUL_STRENGTH(refine)
		elif 3 == step:
			return localeinfo.DRAGON_SOUL_STEP_LEVEL4 + " " + localeinfo.DRAGON_SOUL_STRENGTH(refine)
		elif 4 == step:
			return localeinfo.DRAGON_SOUL_STEP_LEVEL5 + " " + localeinfo.DRAGON_SOUL_STRENGTH(refine)
		else:
			return ""

	def __IsHair(self, itemVnum):
		if not itemVnum:
			return 0
		
		item.SelectItem(itemVnum)
		if not (item.GetItemType() == item.ITEM_TYPE_COSTUME and item.GetItemSubType() == item.COSTUME_TYPE_HAIR):
			return 0
		
		if self.__IsOldHair(itemVnum):
			return 1
		
		if self.__IsNewHair(itemVnum):
			return 1
		
		if self.__IsNewHair2(itemVnum):
			return 1
		
		if self.__IsNewHair2(itemVnum):
			return 1
		
		if self.__IsNewHair3(itemVnum):
			return 1
		
		if self.__IsCostumeHair(itemVnum):
			return 1
		
		return 0

	def __IsOldHair(self, itemVnum):
		return itemVnum > 73000 and itemVnum < 74000

	def __IsNewHair(self, itemVnum):
		return itemVnum > 74000 and itemVnum < 75000

	if app.QUICK_SELL_SYSTEM:
		def AppendQuckSellItem(self):
			if item.IsAntiFlag(item.ITEM_ANTIFLAG_SELL) or item.GetItemType() in (item.ITEM_TYPE_BLEND, item.ITEM_TYPE_PET):
				return
			else:
				self.DeclareShortcut(("key_tab", "key_lclick"), getattr(localeinfo, "QUICK_SELL_TOOLTIP", "TAB + Left click - add to the quick-sell list."))

	def __IsNewHair2(self, itemVnum):
		return itemVnum > 74000 and itemVnum < 75000

	def __IsNewHair3(self, itemVnum):
		if itemVnum >= 74751 and itemVnum <= 74766:
			return 1
		elif itemVnum >= 75601 and itemVnum <= 75616:
			return 1
		elif itemVnum >= 75401 and itemVnum <= 75416:
			return 1
		elif itemVnum >= 74501 and itemVnum <= 74516:
			return 1
		elif itemVnum >= 74251 and itemVnum <= 74266:
			return 1
		elif itemVnum >= 75201 and itemVnum <= 75216:
			return 1
		elif itemVnum >= 75001 and itemVnum <= 75016:
			return 1
		elif itemVnum >= 74001 and itemVnum <= 74016:
			return 1
		
		return ((74012 < itemVnum and itemVnum < 74022) or
			(74262 < itemVnum and itemVnum < 74272) or
			(74512 < itemVnum and itemVnum < 74522) or
			(74762 < itemVnum and itemVnum < 74772) or
			(45000 < itemVnum and itemVnum < 45119) or
			(45126 < itemVnum and itemVnum < 47000))

	def AppendIcon(self, itemVnum, itemCount):
		itemImage = ui.ImageBox()
		itemImage.SetParent(self)
		itemImage.Show()
		
		item.SelectItem(itemVnum)
		itemImage.LoadImage(item.GetIconImageFileName())

		if itemCount > 1:
			countNumberLine = ui.NumberLine()
			countNumberLine.SetParent(itemImage)
			countNumberLine.SetWindowHorizontalAlignRight()
			countNumberLine.SetHorizontalAlignRight()
			countNumberLine.SetNumber(str(itemCount))
			countNumberLine.SetPosition(3, itemImage.GetHeight() - 8)
			countNumberLine.Show()

		itemImage.SetPosition((self.GetWidth() - itemImage.GetWidth()) / 2, self.toolTipHeight)
		self.toolTipHeight += itemImage.GetHeight()

		self.childrenList.append(itemImage)
		if itemCount > 1:
			self.childrenList.append(countNumberLine)
		self.ResizeToolTip()


	def __IsCostumeHair(self, itemVnum):
		return self.__IsNewHair3(itemVnum - 100000)

	def __AppendHairIcon(self, itemVnum):
		import pack
		
		pathName = "d:/ymir work/item/quest/" + str(itemVnum) + ".tga"
		
		if not pack.Exist(pathName):
			pathName = "icon/hair/%d.sub" % (itemVnum)
			if not pack.Exist(pathName):
				pathName = "d:/ymir work/item/quest/" + str(itemVnum - 1000) + ".tga"
				if not pack.Exist(pathName):
					return
		
		itemImage = ui.ImageBox()
		itemImage.SetParent(self)
		itemImage.Show()
		itemImage.LoadImage(pathName)
		itemImage.SetPosition((self.toolTipWidth - itemImage.GetWidth()) / 2, self.toolTipHeight)
		#if self.__IsNewHair3(itemVnum):
		#	
		#	itemImage.LoadImage(pathName)
		#elif self.__IsOldHair(itemVnum):
		#	itemImage.LoadImage("d:/ymir work/item/quest/" + str(itemVnum) + ".tga")
		#elif self.__IsNewHair(itemVnum):
		#	if itemVnum > 74520 and itemVnum < 74751:
		#		itemImage.LoadImage("icon/hair/%d.sub" % (itemVnum))
		#	else:
		#		itemImage.LoadImage("d:/ymir work/item/quest/" + str(itemVnum-1000) + ".tga")
		#elif self.__IsNewHair2(itemVnum):
		#	itemImage.LoadImage("icon/hair/%d.sub" % (itemVnum))
		#elif self.__IsCostumeHair(itemVnum):
		#	itemImage.LoadImage("icon/hair/%d.sub" % (itemVnum - 100000))
		#

		itemImage.SetPosition(itemImage.GetWidth() / 2, self.toolTipHeight)

		self.toolTipHeight += itemImage.GetHeight()
		# self.toolTipWidth += itemImage.GetWidth() / 2
		self.childrenList.append(itemImage)
		self.ResizeToolTip()

	def __AppendItemIcon(self, itemVnum):
		itemImage = ui.ImageBox()
		itemImage.SetParent(self)
		item.SelectItem(itemVnum)
		itemImage.LoadImage(item.GetIconImageFileName())
		itemImage.SetPosition(self.toolTipWidth / 2 - itemImage.GetWidth() / 2, self.toolTipHeight)
		itemImage.Show()

		self.toolTipHeight += itemImage.GetHeight()
		self.childrenList.append(itemImage)
		self.ResizeToolTip()

	def ResizeToolTipWidth(self, width):
		self.toolTipWidth = width

	def __CalculateToolTipWidth(self):
		affectTextLineLenList = []

		metinSocket = self.metinSlot
		if metinSocket:
			for socketIndex in metinSocket:
				if socketIndex:
					item.SelectItem(socketIndex)

					affectType, affectValue = item.GetAffect(0)
					affectString = self.__GetAffectString(affectType, affectValue)
					if affectString:
						affectTextLineLenList.append(len(affectString))

			if self.itemVnum:
				item.SelectItem(self.itemVnum)
			self.metinSlot = None

		if self.toolTipWidth == self.TOOL_TIP_WIDTH:
			if affectTextLineLenList:
				self.toolTipWidth += max(affectTextLineLenList) + 10

		self.AlignTextLineHorizonalCenter()


	def __AdjustMaxWidth(self, attrSlot, desc):
		newToolTipWidth = self.toolTipWidth
		newToolTipWidth = max(self.__AdjustAttrMaxWidth(attrSlot), newToolTipWidth)
		newToolTipWidth = max(self.__AdjustDescMaxWidth(desc), newToolTipWidth)
		if newToolTipWidth > self.toolTipWidth:
			self.toolTipWidth = newToolTipWidth
			self.ResizeToolTip()

	def __AdjustAttrMaxWidth(self, attrSlot):
		if 0 == attrSlot:
			return self.toolTipWidth

		maxWidth = self.toolTipWidth
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			type = attrSlot[i][0]
			value = attrSlot[i][1]
			if self.ATTRIBUTE_NEED_WIDTH.has_key(type):
				if value > 0:
					maxWidth = max(self.ATTRIBUTE_NEED_WIDTH[type], maxWidth)

					# ATTR_CHANGE_TOOLTIP_WIDTH
					#self.toolTipWidth = max(self.ATTRIBUTE_NEED_WIDTH[type], self.toolTipWidth)
					#self.ResizeToolTip()
					# END_OF_ATTR_CHANGE_TOOLTIP_WIDTH

		return maxWidth

	def __AdjustDescMaxWidth(self, desc):
		if len(desc) < DESC_DEFAULT_MAX_COLS:
			return self.toolTipWidth

		return DESC_WESTERN_MAX_WIDTH

	def __AppendSkillIcon(self, skillIndex):
		# skill icons live in skilldesc (iconfilename -> .sub); GetIconImage returns that path under USE_V1.
		skillIcon = skill.GetIconImage(skillIndex)
		if not skillIcon:
			return
		skillImage = ui.ImageBox()
		skillImage.SetParent(self)
		skillImage.LoadImage(skillIcon)
		skillImage.SetPosition(self.toolTipWidth / 2 - skillImage.GetWidth() / 2, self.toolTipHeight)
		skillImage.Show()
		self.toolTipHeight += skillImage.GetHeight()
		self.childrenList.append(skillImage)
		self.ResizeToolTip()

	def __AppendAutoSkillBookInfo(self, bookInfo):
		# Appended to the NORMAL item tooltip (keeps the real book name + description).
		skillIndex, tier, total = bookInfo
		skillName = skill.GetSkillName(skillIndex)
		if not skillName:
			return

		gradeStr = { "M": localeinfo.SKILLBOOK_GRADE_M,
		             "G": localeinfo.SKILLBOOK_GRADE_G,
		             "P": localeinfo.SKILLBOOK_GRADE_P }.get(tier, "")

		self.AppendSpace(5)
		self.AppendTextLine(localeinfo.SKILLBOOK_TT_USE_FOR, self.NORMAL_COLOR)
		self.__AppendSkillIcon(skillIndex)
		self.AppendTextLine("%s %s" % (skillName, gradeStr), 0xffFFD200)
		self.AppendSpace(5)

	def __SetSkillBookToolTip(self, skillIndex, bookName, skillGrade):
		skillName = skill.GetSkillName(skillIndex)

		if not skillName:
			return

		if localeinfo.IsVIETNAM():
			itemName = bookName + " " + skillName
		else:
			itemName = skillName + " " + bookName
		self.SetTitle(itemName)

	def __AppendPickInformation(self, curLevel, curEXP, maxEXP):
		self.AppendSpace(5)
		self.AppendTextLine(localeinfo.TOOLTIP_PICK_LEVEL % (curLevel), self.NORMAL_COLOR)

		self.AppendTextLine(localeinfo.TOOLTIP_PICK_EXP % (curEXP, maxEXP), self.NORMAL_COLOR)

		if curEXP == maxEXP:
			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.TOOLTIP_PICK_UPGRADE1, self.NORMAL_COLOR)
			self.AppendTextLine(localeinfo.TOOLTIP_PICK_UPGRADE2, self.NORMAL_COLOR)
			self.AppendTextLine(localeinfo.TOOLTIP_PICK_UPGRADE3, self.NORMAL_COLOR)

	def __AppendRodInformation(self, curLevel, curEXP, maxEXP):
		self.AppendSpace(5)
		self.AppendTextLine(localeinfo.TOOLTIP_FISHINGROD_LEVEL % (curLevel), self.NORMAL_COLOR)

		self.AppendTextLine(localeinfo.TOOLTIP_FISHINGROD_EXP % (curEXP, maxEXP), self.NORMAL_COLOR)

		if curEXP == maxEXP:
			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.TOOLTIP_FISHINGROD_UPGRADE1, self.NORMAL_COLOR)
			self.AppendTextLine(localeinfo.TOOLTIP_FISHINGROD_UPGRADE2, self.NORMAL_COLOR)
			self.AppendTextLine(localeinfo.TOOLTIP_FISHINGROD_UPGRADE3, self.NORMAL_COLOR)

	def __AppendLimitInformation(self):
		appendSpace = False

		for i in xrange(item.LIMIT_MAX_NUM):
			(limitType, limitValue) = item.GetLimit(i)

			if limitValue > 0:
				if False == appendSpace:
					self.AppendSpace(5)
					appendSpace = True
			else:
				continue

			if item.LIMIT_LEVEL == limitType:
				color = self.GetLimitTextLineColor(player.GetStatus(player.LEVEL), limitValue)
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_LIMIT_LEVEL % (limitValue), color)
			elif item.LIMIT_MAX_LEVEL == limitType:
				color = self.GetMaxLimitTextLineColor(player.GetStatus(player.LEVEL), limitValue)
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_LIMIT_MAX_LEVEL % (limitValue), color)
			"""
			elif item.LIMIT_STR == limitType:
				color = self.GetLimitTextLineColor(player.GetStatus(player.ST), limitValue)
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_LIMIT_STR % (limitValue), color)
			elif item.LIMIT_DEX == limitType:
				color = self.GetLimitTextLineColor(player.GetStatus(player.DX), limitValue)
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_LIMIT_DEX % (limitValue), color)
			elif item.LIMIT_INT == limitType:
				color = self.GetLimitTextLineColor(player.GetStatus(player.IQ), limitValue)
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_LIMIT_INT % (limitValue), color)
			elif item.LIMIT_CON == limitType:
				color = self.GetLimitTextLineColor(player.GetStatus(player.HT), limitValue)
				self.AppendTextLine(localeinfo.TOOLTIP_ITEM_LIMIT_CON % (limitValue), color)
			"""

	if app.ENABLE_SOUL_BIND_SYSTEM:
		## cyh itemseal 2013 11 11
		def __AppendSealInformation(self, window_type, slotIndex):
			itemSealDate = player.GetItemSealDate(window_type, slotIndex)
			if itemSealDate == item.GetUnlimitedSealDate():
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.TOOLTIP_SEALED, self.NEGATIVE_COLOR)
			elif itemSealDate > 0:
				self.AppendSpace(5)
				hours, minutes = player.GetItemUnSealLeftTime(window_type, slotIndex)
				self.AppendTextLine(localeinfo.TOOLTIP_UNSEAL_LEFT_TIME % (hours, minutes), self.NEGATIVE_COLOR )
			elif itemSealDate < -1:
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.ACCOUNT_BOUND_ITEM, 0xFFFFA500)

	if app.ENABLE_EQUIPMENT_RESTRICTION:
		# red "restricted to join dungeons for <name>" line; restrictInfo = (typeMask, dungeonName)
		# explicit restrictInfo comes from exchange/offlineshop windows, else read the player item
		def __AppendRestrictionInformation(self, window_type, slotIndex, restrictInfo = None):
			if restrictInfo is None:
				if slotIndex < 0:
					return
				restrictInfo = player.GetItemRestriction(window_type, slotIndex)
			(restrictType, restrictName) = restrictInfo
			if (restrictType & player.RESTRICT_TYPE_DUNGEON) and restrictName:
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.TOOLTIP_EQUIP_RESTRICTION_DUNGEON % (restrictName), self.NEGATIVE_COLOR)

	def __GetAffectString(self, affectType, affectValue):
		if 0 == affectType:
			return None

		if 0 == affectValue:
			return None

		if app.ENABLE_APPLY_RANDOM:
			if affectType == item.APPLY_RANDOM:
				return None

		try:
			return self.AFFECT_DICT[affectType](affectValue)
		except TypeError:
			return "UNKNOWN_VALUE[%s] %s" % (affectType, affectValue)
		except KeyError:
			return "UNKNOWN_TYPE[%s] %s" % (affectType, affectValue)

	if app.ENABLE_BIOLOG_SYSTEM:
		def GetAffectBiologString(self, affectType, affectValue):
			if 0 == affectType:
				return "-"

			if 0 == affectValue:
				return "-"

			if app.ENABLE_APPLY_RANDOM:
				if item.APPLY_RANDOM == affectType:
					return "-"

			try:
				return self.AFFECT_DICT[affectType](affectValue)
			except TypeError:
				return "UNKNOWN_VALUE[%s] %s" % (affectType, affectValue)
			except KeyError:
				return "UNKNOWN_TYPE[%s] %s" % (affectType, affectValue)

	def __AppendAffectInformation(self):
		for i in xrange(item.ITEM_APPLY_MAX_NUM):
			(affectType, affectValue) = item.GetAffect(i)
			
			# >>> tooltip fan-out BEGIN - special multi-effect applies now render as a single
			# line through AFFECT_DICT instead of one line per sub-bonus (disabled)
			# docs/superpowers/specs/2026-08-12-special-multi-applies-design.md
			#if app.ENABLE_ELEMENT_ADD:
			#	if affectType == item.APPLY_ELEMENTS:
			#		elementsList = [\
			#							item.APPLY_ENCHANT_ELEC,
			#							item.APPLY_ENCHANT_FIRE,
			#							item.APPLY_ENCHANT_ICE,
			#							item.APPLY_ENCHANT_WIND,
			#							item.APPLY_ENCHANT_EARTH,
			#							item.APPLY_ENCHANT_DARK,
			#		]

			#		for element in elementsList:
			#			affectString = self.__GetAffectString(element, affectValue)
			#			if affectString:
			#				self.AppendTextLine(affectString, self.GetChangeTextLineColor(affectValue))

			#		continue

			#affect_mappings = {
			#	item.APPLY_BOSS_STONE: [item.APPLY_ATTBONUS_STONE, item.APPLY_ATTBONUS_BOSS],
			#	item.APPLY_ATTBOUNS_AS_SU: [item.APPLY_ATTBONUS_ASSASSIN, item.APPLY_ATTBONUS_SURA],
			#	item.APPLY_ATTBOUNS_WA_SH: [item.APPLY_ATTBONUS_WARRIOR, item.APPLY_ATTBONUS_SHAMAN],
			#	item.APPLY_RESIST_AS_SU: [item.APPLY_RESIST_ASSASSIN, item.APPLY_RESIST_SURA],
			#	item.APPLY_RESIST_WA_SH: [item.APPLY_RESIST_WARRIOR, item.APPLY_RESIST_SHAMAN],
			#}


			#if affectType in affect_mappings:
			#	for stuff in affect_mappings[affectType]:
			#		affectString = self.__GetAffectString(stuff, affectValue)
			#		if affectString:
			#			self.AppendTextLine(affectString, self.GetChangeTextLineColor(affectValue))
			#	continue
			# <<< tooltip fan-out END


			affectString = self.__GetAffectString(affectType, affectValue)
			if affectString:
				#if affectType == item.APPLY_ACCEDRAIN_RATE:
				#	self.AppendTextLine(affectString, self.CONDITION_COLOR)
				#else:
				#	self.AppendTextLine(affectString, self.GetChangeTextLineColor(affectValue))
				self.AppendTextLine(affectString, self.GetChangeTextLineColor(affectValue))

	if app.ENABLE_CHANGE_LOOK_SYSTEM:
		def AppendChangeLookInformation(self, window_type, slotIndex, transmutation = -1, metinSlot = []):
			if transmutation == -1:
				if window_type == player.SAFEBOX:
					skinVnum = safebox.GetItemChangeLookVnum(slotIndex)
				elif window_type == player.MALL:
					skinVnum = safebox.GetMallItemChangeLookVnum(slotIndex)
				else:
					skinVnum = player.GetChangeLookVnum(window_type, slotIndex)
			else:
				skinVnum = transmutation
			
			if skinVnum:
				self.AppendSpace(5)
				self.AppendTextLine("[ " + localeinfo.CHANGE_LOOK_TITLE + " ]", self.CHANGELOOK_TITLE_COLOR)
				itemName = item.GetItemNameByVnum(skinVnum)
				
				if item.GetItemType() == item.ITEM_TYPE_COSTUME:
					itemSubType = item.GetItemSubType()
					if itemSubType == item.COSTUME_TYPE_BODY:
						malefemale = ""
						if item.IsAntiFlag(item.ITEM_ANTIFLAG_MALE):
							malefemale = localeinfo.FOR_FEMALE
						
						if item.IsAntiFlag(item.ITEM_ANTIFLAG_FEMALE):
							malefemale = localeinfo.FOR_MALE
						
						itemName += " ( " + malefemale + " )"
					elif app.USE_ACCE_SYSTEM and\
						itemSubType == item.COSTUME_TYPE_ACCE and\
						len(metinSlot) >= 3:
						itemName += " (" + localeinfo.TOOLTIP_APPLY_ACCEDRAIN_RATE(metinSlot[2]) + ")"
				
				textLine = self.AppendTextLine(itemName, self.CHANGELOOK_ITEMNAME_COLOR, True)
				textLine.SetFeather()

	if app.ENABLE_COMBAT_POINTS:
		def __AppendGearCPInfo(self, itemVnum, itemSubType=0):
			import cpinfo
			gearCP = cpinfo.GetItemGearCP(itemVnum, itemSubType)
			if gearCP > 0:
				self.AppendSpace(5)
				self.AppendTextLine("+%s %s" % (localeinfo.NumberToMoneyStringNEW(gearCP),localeinfo.CP_GEAR_SCORE_HINT), 0xFF8BBDFF)

	def AppendWearableInformation(self):
		self.AppendSpace(5)
		self.AppendTextLine(localeinfo.TOOLTIP_ITEM_WEARABLE_JOB, self.NORMAL_COLOR)

		if not app.DISABLE_WOLFMAN_CREATION:
			flagList = (
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_WARRIOR),
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_ASSASSIN),
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_SURA),
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_SHAMAN),
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_WOLFMAN),
				)
		else:
			flagList = (
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_WARRIOR),
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_ASSASSIN),
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_SURA),
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_SHAMAN),
				)

		characterNames = ""
		for i in xrange(self.CHARACTER_COUNT):
			name = self.CHARACTER_NAMES[i]
			flag = flagList[i]

			if flag:
				characterNames += " "
				characterNames += name

		textLine = self.AppendTextLine(characterNames, self.NORMAL_COLOR, True)
		textLine.SetFeather()

		if item.IsAntiFlag(item.ITEM_ANTIFLAG_MALE):
			textLine = self.AppendTextLine(localeinfo.FOR_FEMALE, self.NORMAL_COLOR, True)
			textLine.SetFeather()

		if item.IsAntiFlag(item.ITEM_ANTIFLAG_FEMALE):
			textLine = self.AppendTextLine(localeinfo.FOR_MALE, self.NORMAL_COLOR, True)
			textLine.SetFeather()

	def __AppendPotionInformation(self):
		self.AppendSpace(5)

		healHP = item.GetValue(0)
		healSP = item.GetValue(1)
		healStatus = item.GetValue(2)
		healPercentageHP = item.GetValue(3)
		healPercentageSP = item.GetValue(4)

		if healHP > 0:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_HP_POINT % healHP, self.GetChangeTextLineColor(healHP))
		if healSP > 0:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_SP_POINT % healSP, self.GetChangeTextLineColor(healSP))
		if healStatus != 0:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_CURE)
		if healPercentageHP > 0:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_HP_PERCENT % healPercentageHP, self.GetChangeTextLineColor(healPercentageHP))
		if healPercentageSP > 0:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_SP_PERCENT % healPercentageSP, self.GetChangeTextLineColor(healPercentageSP))

	def __AppendAbilityPotionInformation(self):
		self.AppendSpace(5)

		abilityType = item.GetValue(0)
		time = item.GetValue(1)
		point = item.GetValue(2)

		if abilityType == item.APPLY_ATT_SPEED:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_ATTACK_SPEED % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_MOV_SPEED:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_MOVING_SPEED % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_MAX_HP:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_MAX_HP % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_MAX_SP:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_MAX_SP % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_ATTBONUS_ANIMAL:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_ATTBONUS_ANIMAL % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_ATTBONUS_ORC:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_ATTBONUS_ORC % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_ATTBONUS_MILGYO:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_ATTBONUS_MILGYO % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_ATTBONUS_UNDEAD:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_ATTBONUS_UNDEAD % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_ATTBONUS_DEVIL:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_ATTBONUS_DEVIL % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_ATTBONUS_HUMAN:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_ATTBONUS_HUMAN % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_POISON_PCT:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_POISON_PCT % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_CRITICAL_PCT:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_CRITICAL_PCT % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_PENETRATE_PCT:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_PENETRATE_PCT % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_STR:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_STR % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_DEX:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_DEX % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_INT:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_INT % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_CON:
				self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_CON % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_ATTBONUS_MONSTER:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_ATTBONUS_MONSTER % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_DEF_GRADE_BONUS:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_DEF_GRADE_BONUS % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_ATT_GRADE_BONUS:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_ATT_GRADE_BONUS % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_SKILL_DAMAGE_BONUS:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_SKILL_DAMAGE_BONUS % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_NORMAL_HIT_DAMAGE_BONUS:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_NORMAL_HIT_DAMAGE_BONUS % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_SKILL_DEFEND_BONUS:
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_SKILL_DEFEND_BONUS % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_EXP_DOUBLE_BONUS:#heredream
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_EXP_BONUS % point, self.GetChangeTextLineColor(point))
		elif abilityType == item.APPLY_ATTBONUS_MEDI_PVM:#heredream
			self.AppendTextLine(localeinfo.TOOLTIP_POTION_PLUS_MEDI_PVM % point, self.GetChangeTextLineColor(point))
		elif abilityType != 0 and point != 0 and self.AFFECT_DICT.has_key(abilityType):
			self.AppendTextLine(self.AFFECT_DICT[abilityType](point).replace("+-", "-"), self.GetChangeTextLineColor(point))

		for i in xrange(item.ITEM_APPLY_MAX_NUM):
			(useApplyType, useApplyValue) = item.GetAffect(i)
			if useApplyType == 0 or useApplyValue == 0:
				continue
			useApplyString = self.__GetAffectString(useApplyType, useApplyValue)
			if useApplyString:
				self.AppendTextLine(useApplyString.replace("+-", "-"), self.GetChangeTextLineColor(useApplyValue))

		if time > 0:
			minute = (time / 60)
			second = (time % 60)
			timeString = localeinfo.TOOLTIP_POTION_TIME

			if minute > 0:
				timeString += str(minute) + localeinfo.TOOLTIP_POTION_MIN
			if second > 0:
				timeString += " " + str(second) + localeinfo.TOOLTIP_POTION_SEC

			self.AppendTextLine(timeString)

	def GetPriceColor(self, price):
		if price>=constinfo.HIGH_PRICE:
			return self.HIGH_PRICE_COLOR
		if price>=constinfo.MIDDLE_PRICE:
			return self.MIDDLE_PRICE_COLOR
		else:
			return self.LOW_PRICE_COLOR

	if app.ENABLE_SET_ITEM:
		def GetAffectString(self, affectType, affectValue):
			if 0 == affectType:
				return None

			if 0 == affectValue:
				return None

			try:
				return self.AFFECT_DICT[affectType](affectValue)
			except TypeError:
				return "UNKNOWN_VALUE[%s] %s" % (affectType, affectValue)
			except KeyError:
				return "UNKNOWN_TYPE[%s] %s" % (affectType, affectValue)

	if app.ENABLE_CHEQUE_SYSTEM:
		def AppendPrice(self, price, cheque = 0):
			self.AppendSpace(5)
			self.AppendTextLineDontCheckColor(localeinfo.CHEQUE_SYSTEM_SELL_PRICE, self.SALES_TITLE_COLOR)

			if cheque > 0:
				self.AppendTextLineDontCheckColor(localeinfo.CHEQUE_SYSTEM_WON % (str(cheque)), grp.GenerateColor(0.0, 0.8470, 1.0, 1.0))

			if price >= 0:
				self.AppendTextLineDontCheckColor(localeinfo.CHEQUE_SYSTEM_YANG % (localeinfo.NumberToMoneyString(price)), self.GetPriceColor(price))
	else:
		def AppendPrice(self, price):
			self.AppendSpace(5)
			self.AppendTextLineDontCheckColor(localeinfo.TOOLTIP_BUYPRICE % (localeinfo.NumberToMoneyString(price)), self.GetPriceColor(price))

	def AppendPriceBySecondaryCoin(self, price):
		self.AppendSpace(5)
		self.AppendTextLineDontCheckColor(localeinfo.TOOLTIP_BUYPRICE % (localeinfo.NumberToSecondaryCoinString(price)), self.GetPriceColor(price))

	if app.ENABLE_CHEQUE_SYSTEM:
		def AppendSellingPrice(self, price, cheque = 0, isPrivateShopBuilder = False):
			if item.IsAntiFlag(item.ITEM_ANTIFLAG_SELL) and \
				not isPrivateShopBuilder:
				self.AppendTextLineDontCheckColor(localeinfo.TOOLTIP_ANTI_SELL, self.DISABLE_COLOR)
				self.AppendSpace(5)
			else:
				self.AppendTextLineDontCheckColor(localeinfo.CHEQUE_SYSTEM_SELL_PRICE, self.SALES_TITLE_COLOR)

				if cheque > 0:
					self.AppendTextLineDontCheckColor(localeinfo.CHEQUE_SYSTEM_WON % (str(cheque)), grp.GenerateColor(0.0, 0.8470, 1.0, 1.0))

				if price >= 0:
					self.AppendTextLineDontCheckColor(localeinfo.CHEQUE_SYSTEM_YANG % (localeinfo.NumberToMoneyString(price)), self.GetPriceColor(price))

				self.AppendSpace(5)
	else:
		def AppendSellingPrice(self, price):
			if item.IsAntiFlag(item.ITEM_ANTIFLAG_SELL):
				self.AppendTextLineDontCheckColor(localeinfo.TOOLTIP_ANTI_SELL, self.DISABLE_COLOR)
				self.AppendSpace(5)
			else:
				self.AppendTextLineDontCheckColor(localeinfo.TOOLTIP_SELLPRICE % (localeinfo.NumberToMoneyString(price)), self.GetPriceColor(price))
				self.AppendSpace(5)

	if app.ENABLE_12ZI:
		def AppendLimitedCount(self, count, purchaseCount):
			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.SHOP_LIMITED_ITEM_REMAIN_COUNT % (count - purchaseCount), grp.GenerateColor(1.0, 1.0, 1.0, 1.0))

		def RefreshShopToolTip(self):
			if self.IsShow() and self.isShopItem:
				self.SetShopItem(self.ShopSlotIndex)

	def AppendMetinInformation(self):
		affectType, affectValue = item.GetAffect(0)
		#affectType = item.GetValue(0)
		#affectValue = item.GetValue(1)

		affectString = self.__GetAffectString(affectType, affectValue)

		if affectString:
			self.AppendSpace(5)
			self.AppendTextLine(affectString, self.GetChangeTextLineColor(affectValue))

	def AppendMetinWearInformation(self):
		self.AppendSpace(5)
		self.AppendTextLine(localeinfo.TOOLTIP_SOCKET_REFINABLE_ITEM, self.NORMAL_COLOR)

		flagList = (
			item.IsWearableFlag(long(item.WEARABLE_BODY)),
			item.IsWearableFlag(long(item.WEARABLE_HEAD)),
			item.IsWearableFlag(long(item.WEARABLE_FOOTS)),
			item.IsWearableFlag(long(item.WEARABLE_WRIST)),
			item.IsWearableFlag(long(item.WEARABLE_WEAPON)),
			item.IsWearableFlag(long(item.WEARABLE_NECK)),
			item.IsWearableFlag(long(item.WEARABLE_EAR)),
			item.IsWearableFlag(long(item.WEARABLE_UNIQUE)),
			item.IsWearableFlag(long(item.WEARABLE_SHIELD)),
			item.IsWearableFlag(long(item.WEARABLE_ARROW)),
		)

		if app.USE_GLOVE_SYSTEM:
			flagList += (item.IsWearableFlag(long(item.WEARABLE_GLOVE)),)

		wearNames = ""
		for i in xrange(self.WEAR_COUNT):
			name = self.WEAR_NAMES[i]
			flag = flagList[i]

			if flag:
				wearNames += "	"
				wearNames += name

		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetFontName(self.defFontName)
		textLine.SetPosition(self.toolTipWidth/2, self.toolTipHeight)
		textLine.SetHorizontalAlignCenter()
		textLine.SetPackedFontColor(self.NORMAL_COLOR)
		textLine.SetText(wearNames)
		textLine.Show()
		self.childrenList.append(textLine)

		self.toolTipHeight += self.TEXT_LINE_HEIGHT
		self.ResizeToolTip()

	def GetMetinSocketType(self, number):
		if player.METIN_SOCKET_TYPE_NONE == number:
			return player.METIN_SOCKET_TYPE_NONE
		elif player.METIN_SOCKET_TYPE_SILVER == number:
			return player.METIN_SOCKET_TYPE_SILVER
		elif player.METIN_SOCKET_TYPE_GOLD == number:
			return player.METIN_SOCKET_TYPE_GOLD
		else:
			if app.ENABLE_NEW_USER_CARE:
				if item.SelectItem(number) == False:
					return player.METIN_SOCKET_TYPE_NONE
				else:
					if item.METIN_NORMAL == item.GetItemSubType():
						return player.METIN_SOCKET_TYPE_SILVER
					elif item.METIN_GOLD == item.GetItemSubType():
						return player.METIN_SOCKET_TYPE_GOLD
					elif app.USE_GLOVE_SYSTEM and item.GetItemSubType() == item.METIN_SUNGMA:
						return player.METIN_SOCKET_TYPE_SILVER
					elif "USE_PUT_INTO_ACCESSORY_SOCKET" == item.GetUseType(number):
						return player.METIN_SOCKET_TYPE_SILVER
					elif "USE_PUT_INTO_RING_SOCKET" == item.GetUseType(number):
						return player.METIN_SOCKET_TYPE_SILVER
					elif "USE_PUT_INTO_BELT_SOCKET" == item.GetUseType(number):
						return player.METIN_SOCKET_TYPE_SILVER
			else:
				item.SelectItem(number)
				if item.METIN_NORMAL == item.GetItemSubType():
					return player.METIN_SOCKET_TYPE_SILVER
				elif item.METIN_GOLD == item.GetItemSubType():
					return player.METIN_SOCKET_TYPE_GOLD
				elif app.USE_GLOVE_SYSTEM and item.GetItemSubType() == item.METIN_SUNGMA:
					return player.METIN_SOCKET_TYPE_SILVER
				elif "USE_PUT_INTO_ACCESSORY_SOCKET" == item.GetUseType(number):
					return player.METIN_SOCKET_TYPE_SILVER
				elif "USE_PUT_INTO_RING_SOCKET" == item.GetUseType(number):
					return player.METIN_SOCKET_TYPE_SILVER
				elif "USE_PUT_INTO_BELT_SOCKET" == item.GetUseType(number):
					return player.METIN_SOCKET_TYPE_SILVER

		return player.METIN_SOCKET_TYPE_NONE

	def GetMetinItemIndex(self, number):
		if player.METIN_SOCKET_TYPE_SILVER == number:
			return 0
		if player.METIN_SOCKET_TYPE_GOLD == number:
			return 0

		return number

	# def __AppendAccessoryMetinSlotInfo(self, metinSlot, mtrlVnum):
		# ACCESSORY_SOCKET_MAX_SIZE = 3

		# cur = min(metinSlot[0], ACCESSORY_SOCKET_MAX_SIZE)
		# end = min(metinSlot[1], ACCESSORY_SOCKET_MAX_SIZE)

		# affectType1, affectValue1 = item.GetAffect(0)
		# affectList1 = [0, max(1, affectValue1 * 10 / 100), max(2, affectValue1 * 20 / 100), max(3, affectValue1 * 40 / 100)]

		# affectType2, affectValue2 = item.GetAffect(1)
		# affectList2 = [0, max(1, affectValue2 * 10 / 100), max(2, affectValue2 * 20 / 100), max(3, affectValue2 * 40 / 100)]

		# affectType3, affectValue3 = item.GetAffect(2)
		# affectList3 = [0, max(1, affectValue3 * 10 / 100), max(2, affectValue3 * 20 / 100), max(3, affectValue3 * 40 / 100)]

		# mtrlPos = 0
		# mtrlList = [mtrlVnum] * cur + [player.METIN_SOCKET_TYPE_SILVER] * (end - cur)
		# for mtrl in mtrlList:
			# affectString1 = self.__GetAffectString(affectType1, affectList1[mtrlPos + 1] - affectList1[mtrlPos])
			# affectString2 = self.__GetAffectString(affectType2, affectList2[mtrlPos + 1] - affectList2[mtrlPos])
			# affectString3 = self.__GetAffectString(affectType3, affectList3[mtrlPos + 1] - affectList3[mtrlPos])

			# leftTime = 0
			# if cur == mtrlPos + 1:
				# leftTime = metinSlot[2]

			# self.__AppendMetinSlotInfo_AppendMetinSocketData(mtrlPos, mtrl, affectString1, affectString2, affectString3, leftTime)
			# mtrlPos += 1

	def AppendWikiAccessoryMaterials(self, itemVnum):
		# Wiki-only: show the upgrade ore this accessory uses as a single horizontal
		# row of 3 slotted ore icons, plus the total bonus from filling all 3 sockets.
		# Called by ingamewikiui after AddItemData; no-op for non-accessories.
		item.SelectItem(itemVnum)
		if item.GetItemType() != item.ITEM_TYPE_ARMOR:
			return

		itemSubType = item.GetItemSubType()
		if not itemSubType in (item.ARMOR_WRIST, item.ARMOR_NECK, item.ARMOR_EAR):
			return

		mtrlVnum = constinfo.GET_ACCESSORY_MATERIAL_VNUM(itemVnum, itemSubType)
		if not mtrlVnum:
			return

		ACCESSORY_SOCKET_MAX_SIZE = 3

		# Total bonus at full sockets, for every apply slot (accessory still selected).
		affectStrings = []
		for i in xrange(item.ITEM_APPLY_MAX_NUM):
			affType, affValue = item.GetAffect(i)
			if affType == 0 or affValue == 0:
				continue
			affectList = [0, max(1, affValue * 10 / 100), max(2, affValue * 20 / 100), max(3, affValue * 40 / 100)]
			affectStr = self.__GetAffectString(affType, affectList[ACCESSORY_SOCKET_MAX_SIZE])
			if affectStr:
				affectStrings.append(affectStr)

		item.SelectItem(mtrlVnum)
		mtrlName = item.GetItemName()
		iconFileName = item.GetIconImageFileName()

		# Section header.
		self.AppendSpace(5)
		self.AppendTextLineDontCheckColor("[%s]" % localeinfo.TOOLTIP_ACCESSORY_ORES, self.SPECIAL_TITLE_COLOR)

		self.AppendSpace(5)

		# Row of 3 ore icons, each on a slot background, centered.
		slotImages = []
		iconImages = []
		for i in xrange(ACCESSORY_SOCKET_MAX_SIZE):
			slotImage = ui.ImageBox()
			slotImage.SetParent(self)
			try:
				slotImage.LoadImage("d:/ymir work/ui/public/slot_base.sub")
			except:
				pass
			slotImage.Show()
			self.childrenList.append(slotImage)
			slotImages.append(slotImage)

			iconImage = ui.ImageBox()
			iconImage.SetParent(self)
			try:
				iconImage.LoadImage(iconFileName)
			except:
				pass
			iconImage.Show()
			self.childrenList.append(iconImage)
			iconImages.append(iconImage)

		slotWidth = slotImages[0].GetWidth()
		slotHeight = slotImages[0].GetHeight()
		if slotWidth <= 0:
			slotWidth = 32
		if slotHeight <= 0:
			slotHeight = 32
		iconWidth = iconImages[0].GetWidth()
		iconHeight = iconImages[0].GetHeight()
		if iconWidth <= 0:
			iconWidth = slotWidth
		if iconHeight <= 0:
			iconHeight = slotHeight

		gap = 6
		rowWidth = ACCESSORY_SOCKET_MAX_SIZE * slotWidth + (ACCESSORY_SOCKET_MAX_SIZE - 1) * gap
		startX = (self.toolTipWidth - rowWidth) / 2

		for i in xrange(ACCESSORY_SOCKET_MAX_SIZE):
			slotX = startX + i * (slotWidth + gap)
			slotImages[i].SetPosition(slotX, self.toolTipHeight)
			iconImages[i].SetPosition(slotX + (slotWidth - iconWidth) / 2, self.toolTipHeight + (slotHeight - iconHeight) / 2)

		self.toolTipHeight += slotHeight + 3
		self.ResizeToolTip()

		if mtrlName:
			self.AppendTextLineDontCheckColor(mtrlName, self.NORMAL_COLOR)

		for affectStr in affectStrings:
			self.AppendTextLineDontCheckColor(affectStr, self.POSITIVE_COLOR)

	def __AppendAccessoryMetinSlotInfo(self, metinSlot, mtrlVnum,apply_random_list = None):
		# Compact ore display: one icon row (filled ores + empty slots), then the ore
		# name, the total bonus at the current grade and the single shared downgrade
		# timer. The accessory ore system stores ONE timer (socket[2], reset on each
		# ore add) -- not a per-ore duration -- so one total + one time line is exact.
		ACCESSORY_SOCKET_MAX_SIZE = 3

		cur = min(metinSlot[0], ACCESSORY_SOCKET_MAX_SIZE)
		end = min(metinSlot[1], ACCESSORY_SOCKET_MAX_SIZE)

		if end <= 0:
			return

		# Resolve apply types/values up-front while the accessory is the selected item.
		affectData = []
		for i in xrange(item.ITEM_APPLY_MAX_NUM):
			affType, affValue = item.GetAffect(i)
			if app.ENABLE_APPLY_RANDOM and affType == item.APPLY_RANDOM and apply_random_list != None and len(apply_random_list) > i:
				affType = apply_random_list[i][0]
				affValue = apply_random_list[i][1]
			affectData.append((affType, affValue))

		# Section header (inventory only).
		self.AppendSpace(5)
		if self.isInventoryContext:
			self.AppendTextLineDontCheckColor("[%s]" % localeinfo.TOOLTIP_ACCESSORY_ORES, self.SPECIAL_TITLE_COLOR)
			self.AppendSpace(5)

		item.SelectItem(mtrlVnum)
		iconFileName = item.GetIconImageFileName()
		mtrlName = item.GetItemName()

		# One row: filled ore icons + empty slots, on metin-slot backgrounds.
		cellImages = []
		iconImages = []
		for i in xrange(end):
			cell = ui.ImageBox()
			cell.SetParent(self)
			cell.LoadImage("d:/ymir work/ui/game/windows/metin_slot_silver.sub")
			cell.Show()
			self.childrenList.append(cell)
			cellImages.append(cell)

			iconImage = None
			if i < cur:
				iconImage = ui.ImageBox()
				iconImage.SetParent(self)
				try:
					iconImage.LoadImage(iconFileName)
				except:
					pass
				iconImage.Show()
				self.childrenList.append(iconImage)
			iconImages.append(iconImage)

		cellWidth = cellImages[0].GetWidth()
		cellHeight = cellImages[0].GetHeight()
		if cellWidth <= 0:
			cellWidth = 32
		if cellHeight <= 0:
			cellHeight = 32

		gap = 6
		rowWidth = end * cellWidth + (end - 1) * gap
		startX = (self.toolTipWidth - rowWidth) / 2

		for i in xrange(end):
			cellX = startX + i * (cellWidth + gap)
			cellImages[i].SetPosition(cellX, self.toolTipHeight)
			if iconImages[i] != None:
				iconW = iconImages[i].GetWidth()
				iconH = iconImages[i].GetHeight()
				if iconW <= 0:
					iconW = cellWidth
				if iconH <= 0:
					iconH = cellHeight
				iconImages[i].SetPosition(cellX + (cellWidth - iconW) / 2, self.toolTipHeight + (cellHeight - iconH) / 2)

		self.toolTipHeight += cellHeight + 3
		self.ResizeToolTip()

		if cur <= 0:
			return

		# Ore name (inventory only) + total bonus at the current grade.
		if self.isInventoryContext and mtrlName:
			self.AppendTextLineDontCheckColor(mtrlName, self.NORMAL_COLOR)

		for affTuple in affectData:
			affType = affTuple[0]
			affValue = affTuple[1]
			if affType == 0 or affValue == 0:
				continue
			affectList = [0, max(1, affValue * 10 / 100), max(2, affValue * 20 / 100), max(3, affValue * 40 / 100)]
			affectStr = self.__GetAffectString(affType, affectList[cur])
			if affectStr:
				self.AppendTextLineDontCheckColor(affectStr, self.POSITIVE_COLOR)

		# Single shared downgrade timer (time until the top ore degrades).
		leftTime = metinSlot[2]
		if leftTime > 0:
			self.AppendTextLineDontCheckColor(localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(leftTime), self.NORMAL_COLOR)

	if app.USE_GLOVE_SYSTEM:
		def __AppendSungmaSocketData(self, metinSlot):
			data = metinSlot
			if data < 1000000:
				data = None

				slotType = self.GetMetinSocketType(metinSlot)
				itemIndex = self.GetMetinItemIndex(metinSlot)

				if slotType == 0:
					return
			else:
				affectType = (data / 10000) % 1000
				affectValue = data % 100

				itemIndex = item.ITEM_METIN_SUNGMA_VNUM_INDEX
				itemIndex += (((data / 1000) % 10) * 100)
				itemIndex += ((data / 100) % 10) - 1

			self.AppendSpace(5)

			slotImage = ui.ImageBox()
			slotImage.SetParent(self)
			slotImage.LoadImage("d:/ymir work/ui/game/windows/metin_slot_silver.sub")
			slotImage.Show()

			nameTextLine = ui.TextLine()
			nameTextLine.SetParent(self)
			nameTextLine.SetFontName(self.defFontName)
			nameTextLine.SetPackedFontColor(self.NORMAL_COLOR)
			nameTextLine.SetOutline()
			nameTextLine.SetFeather()
			nameTextLine.Show()

			self.childrenList.append(nameTextLine)
			self.childrenList.append(slotImage)

			if localeinfo.IsARABIC():
				slotImage.SetPosition(self.toolTipWidth - slotImage.GetWidth() - 9, self.toolTipHeight - 1)
				nameTextLine.SetPosition(self.toolTipWidth - 50, self.toolTipHeight + 2)
			else:
				slotImage.SetPosition(9, self.toolTipHeight - 1)
				nameTextLine.SetPosition(50, self.toolTipHeight + 2)

			metinImage = ui.ImageBox()
			metinImage.SetParent(self)
			metinImage.Show()
			self.childrenList.append(metinImage)

			if itemIndex:
				item.SelectItem(itemIndex)

				## Image
				try:
					metinImage.LoadImage(item.GetIconImageFileName())
				except:
					dbg.TraceError("ItemToolTip.__AppendSungmaSocketData() - Failed to find image file %d:%s" % (itemIndex, item.GetIconImageFileName()))

				nameTextLine.SetText(item.GetItemName())

				## Affect
				affectTextLine = ui.TextLine()
				affectTextLine.SetParent(self)
				affectTextLine.SetFontName(self.defFontName)
				affectTextLine.SetPackedFontColor(self.POSITIVE_COLOR)
				affectTextLine.SetOutline()
				affectTextLine.SetFeather()
				affectTextLine.Show()

				if localeinfo.IsARABIC():
					metinImage.SetPosition(self.toolTipWidth - metinImage.GetWidth() - 10, self.toolTipHeight)
					affectTextLine.SetPosition(self.toolTipWidth - 50, self.toolTipHeight + 16 + 2)
				else:
					metinImage.SetPosition(10, self.toolTipHeight)
					affectTextLine.SetPosition(50, self.toolTipHeight + 16 + 2)

				if itemIndex == constinfo.ERROR_METIN_STONE:
					affectTextLine.SetText(localeinfo.TOOLTIP_APPLY_NOAFFECT)
				else:
					if data and affectType != 0:
						affectString = self.__GetAffectString(affectType, affectValue)
						if affectString:
							affectTextLine.SetText(affectString)
					else:
						affectTextLine.SetText(localeinfo.TOOLTIP_SOCKET_EMPTY)

				self.childrenList.append(affectTextLine)
			else:
				nameTextLine.SetText(localeinfo.TOOLTIP_SOCKET_EMPTY)

			self.toolTipHeight += 35
			self.ResizeToolTip()

		def __AppendGloveMetinSlotInfo_IsEmptySlotList(self, metinSlot):
			if metinSlot == 0:
				return 1

			for i in xrange(player.METIN_SOCKET_MAX_NUM):
				metinSlotData = metinSlot[i]
				itemIndex = metinSlotData

				if metinSlotData >= 1000000:
					itemIndex = item.ITEM_METIN_SUNGMA_VNUM_INDEX
					itemIndex += (((metinSlotData / 1000) % 10) * 100)
					itemIndex += ((metinSlotData / 100) % 10) - 1

				if self.GetMetinSocketType(itemIndex) != 0:
					if self.GetMetinItemIndex(itemIndex) != 0:
						return 0

			return 1

		def __AppendGloveMetinSlotInfo(self, metinSlot):
			if self.__AppendGloveMetinSlotInfo_IsEmptySlotList(metinSlot):
				return

			for i in xrange(player.METIN_SOCKET_MAX_NUM):
				self.__AppendSungmaSocketData(metinSlot[i])

	def __AppendMetinSlotInfo(self, metinSlot):
		if self.__AppendMetinSlotInfo_IsEmptySlotList(metinSlot):
			return

		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			if app.ENABLE_ITEM_SOCKET5:
				if metinSlot[i] == -1:
					continue

			self.__AppendMetinSlotInfo_AppendMetinSocketData(i, metinSlot[i])

	def __AppendMetinSlotInfo_IsEmptySlotList(self, metinSlot):
		if 0 == metinSlot:
			return 1

		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			metinSlotData = metinSlot[i]
			if app.ENABLE_ITEM_SOCKET5:
				if metinSlotData == -1:
					continue

			if 0 != self.GetMetinSocketType(metinSlotData):
				if 0 != self.GetMetinItemIndex(metinSlotData):
					return 0

		return 1

	def __AppendMetinSlotInfo_AppendMetinSocketData_New(self, index, metinSlotData, height=0, end=0, leftTime=0):

		slotType = self.GetMetinSocketType(metinSlotData)
		itemIndex = self.GetMetinItemIndex(metinSlotData)

		if 0 == slotType:
			return

		slotImage = ui.ImageBox()
		slotImage.SetParent(self)
		slotImage.Show()

		## jweley name
		nameTextLine = ui.TextLine()
		nameTextLine.SetParent(self)
		nameTextLine.SetFontName(self.defFontName)
		nameTextLine.SetPackedFontColor(self.CONDITION_COLOR)
		nameTextLine.SetOutline()
		nameTextLine.SetFeather()
		nameTextLine.Show()

		self.childrenList.append(nameTextLine)

		if player.METIN_SOCKET_TYPE_SILVER == slotType:
			slotImage.LoadImage("d:/ymir work/ui/game/windows/metin_slot_silver.sub")
		elif player.METIN_SOCKET_TYPE_GOLD == slotType:
			slotImage.LoadImage("d:/ymir work/ui/game/windows/metin_slot_gold.sub")

		self.childrenList.append(slotImage)

		if index > 3:
			height += 35
			index = index-4

		if end > 4:
			end = 4

		calc_x = (self.toolTipWidth/2) - (17.5*end)

		slotImage.SetPosition(calc_x+index*40, height +20)

		nameTextLine.SetPosition((self.toolTipWidth / 2), self.toolTipHeight)
		#nameTextLine.SetHorizontalAlignLeft()
		nameTextLine.SetHorizontalAlignCenter()
		metinImage = ui.ImageBox()
		metinImage.SetParent(slotImage)
		metinImage.Show()
		self.childrenList.append(metinImage)

		if itemIndex:

			item.SelectItem(itemIndex)

			## Image
			try:
				metinImage.LoadImage(item.GetIconImageFileName())
			except:
				dbg.TraceError("ItemToolTip.__AppendMetinSocketData() - Failed to find image file %d:%s" %
					(itemIndex, item.GetIconImageFileName())
				)

			metinImage.SetPosition(1, 1)

			nameTextLine.SetText(item.GetItemName())

			if 0 != leftTime:
				timeText = (localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(leftTime)+"|cffFFD700" )

				timeTextLine = ui.TextLine()
				timeTextLine.SetParent(self)
				timeTextLine.SetFontName(self.defFontName)
				timeTextLine.SetPackedFontColor(self.POSITIVE_COLOR)
				timeTextLine.SetPosition((self.toolTipWidth / 2) , self.toolTipHeight + 55)
				#timeTextLine.SetHorizontalAlignLeft()dream
				timeTextLine.SetHorizontalAlignCenter()
				timeTextLine.SetOutline()
				timeTextLine.SetFeather()
				timeTextLine.Show()
				timeTextLine.SetText(timeText)
				self.childrenList.append(timeTextLine)
				self.toolTipHeight += 16 + 2

	def __AppendMetinSlotInfo_AppendMetinSocketData(self, index, metinSlotData, custumAffectString = "", custumAffectString2 = "", custumAffectString3 = "", leftTime = 0):
		slotType = self.GetMetinSocketType(metinSlotData)
		itemIndex = self.GetMetinItemIndex(metinSlotData)

		# 2019.12.17.owsap.Only show socket items
		# if app.ENABLE_ITEM_SOCKET5:
			# if itemIndex:
				# item.SelectItem(itemIndex)
				# if item.GetItemType() != item.ITEM_TYPE_METIN and\
					# item.GetUseType(itemIndex) != "USE_PUT_INTO_ACCESSORY_SOCKET" and\
					# item.GetUseType(itemIndex) != "USE_PUT_INTO_RING_SOCKET" and\
					# item.GetUseType(itemIndex) != "USE_PUT_INTO_BELT_SOCKET":
					# return

		if 0 == slotType:
			return

		self.AppendSpace(5)

		slotImage = ui.ImageBox()
		slotImage.SetParent(self)
		slotImage.Show()

		## Name
		nameTextLine = ui.TextLine()
		nameTextLine.SetParent(self)
		nameTextLine.SetFontName(self.defFontName)
		nameTextLine.SetPackedFontColor(self.NORMAL_COLOR)
		nameTextLine.SetOutline()
		nameTextLine.SetFeather()
		nameTextLine.Show()

		self.childrenList.append(nameTextLine)

		if player.METIN_SOCKET_TYPE_SILVER == slotType:
			slotImage.LoadImage("d:/ymir work/ui/game/windows/metin_slot_silver.sub")
		elif player.METIN_SOCKET_TYPE_GOLD == slotType:
			slotImage.LoadImage("d:/ymir work/ui/game/windows/metin_slot_gold.sub")

		self.childrenList.append(slotImage)

		if localeinfo.IsARABIC():
			slotImage.SetPosition(self.toolTipWidth - slotImage.GetWidth() - 9, self.toolTipHeight - 1)
			nameTextLine.SetPosition(self.toolTipWidth - 50, self.toolTipHeight + 2)
		else:
			slotImage.SetPosition(9, self.toolTipHeight - 1)
			nameTextLine.SetPosition(50, self.toolTipHeight + 2)

		metinImage = ui.ImageBox()
		metinImage.SetParent(self)
		metinImage.Show()
		self.childrenList.append(metinImage)

		if itemIndex:
			item.SelectItem(itemIndex)

			## Image
			try:
				metinImage.LoadImage(item.GetIconImageFileName())
			except:
				dbg.TraceError("ItemToolTip.__AppendMetinSocketData() - Failed to find image file %d:%s" % 
					(itemIndex, item.GetIconImageFileName())
				)

			nameTextLine.SetText(item.GetItemName())

			## Affect
			affectTextLine = ui.TextLine()
			affectTextLine.SetParent(self)
			affectTextLine.SetFontName(self.defFontName)
			affectTextLine.SetPackedFontColor(self.POSITIVE_COLOR)
			affectTextLine.SetOutline()
			affectTextLine.SetFeather()
			affectTextLine.Show()

			if localeinfo.IsARABIC():
				metinImage.SetPosition(self.toolTipWidth - metinImage.GetWidth() - 10, self.toolTipHeight)
				affectTextLine.SetPosition(self.toolTipWidth - 50, self.toolTipHeight + 16 + 2)
			else:
				metinImage.SetPosition(10, self.toolTipHeight)
				affectTextLine.SetPosition(50, self.toolTipHeight + 16 + 2)

			if custumAffectString:
				affectTextLine.SetText(custumAffectString)
			elif itemIndex != constinfo.ERROR_METIN_STONE:
				affectType, affectValue = item.GetAffect(0)
				affectString = self.__GetAffectString(affectType, affectValue)
				if affectString:
					affectTextLine.SetText(affectString)
			else:
				affectTextLine.SetText(localeinfo.TOOLTIP_APPLY_NOAFFECT)

			self.childrenList.append(affectTextLine)

			if custumAffectString2:
				affectTextLine = ui.TextLine()
				affectTextLine.SetParent(self)
				affectTextLine.SetFontName(self.defFontName)
				affectTextLine.SetPackedFontColor(self.POSITIVE_COLOR)
				if localeinfo.IsARABIC():
					affectTextLine.SetPosition(self.toolTipWidth - 50, self.toolTipHeight + 16 + 2 + 16 + 2)
				else:
					affectTextLine.SetPosition(50, self.toolTipHeight + 16 + 2 + 16 + 2)
				affectTextLine.SetOutline()
				affectTextLine.SetFeather()
				affectTextLine.Show()
				affectTextLine.SetText(custumAffectString2)
				self.childrenList.append(affectTextLine)
				self.toolTipHeight += 16 + 2

			if custumAffectString3:
				affectTextLine = ui.TextLine()
				affectTextLine.SetParent(self)
				affectTextLine.SetFontName(self.defFontName)
				affectTextLine.SetPackedFontColor(self.POSITIVE_COLOR)
				if localeinfo.IsARABIC():
					affectTextLine.SetPosition(self.toolTipWidth - 50, self.toolTipHeight + 16 + 2 + 16 + 2)
				else:
					affectTextLine.SetPosition(50, self.toolTipHeight + 16 + 2 + 16 + 2)
				affectTextLine.SetOutline()
				affectTextLine.SetFeather()
				affectTextLine.Show()
				affectTextLine.SetText(custumAffectString3)
				self.childrenList.append(affectTextLine)
				self.toolTipHeight += 16 + 2

			if 0 != leftTime:
				timeText = (localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(leftTime))
				timeTextLine = ui.TextLine()
				timeTextLine.SetParent(self)
				timeTextLine.SetFontName(self.defFontName)
				timeTextLine.SetPackedFontColor(self.POSITIVE_COLOR)
				if localeinfo.IsARABIC():
					timeTextLine.SetPosition(self.toolTipWidth - 50, self.toolTipHeight + 16 + 2 + 16 + 2)
				else:
					timeTextLine.SetPosition(50, self.toolTipHeight + 16 + 2 + 16 + 2)
				timeTextLine.SetOutline()
				timeTextLine.SetFeather()
				timeTextLine.Show()
				timeTextLine.SetText(timeText)
				self.childrenList.append(timeTextLine)
				self.toolTipHeight += 16 + 2

		else:
			nameTextLine.SetText(localeinfo.TOOLTIP_SOCKET_EMPTY)

		self.toolTipHeight += 35
		self.ResizeToolTip()

	def __AppendFishInfo(self, size):
		if size > 0:
			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.TOOLTIP_FISH_LEN % (float(size) / 100.0), self.NORMAL_COLOR)

	def AppendUniqueItemLastTime(self, restMin):
		restSecond = restMin * 60
		self.AppendSpace(5)
		self.AppendTextLine(localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(restSecond), self.NORMAL_COLOR)

	def AppendMallItemLastTime(self, endTime):
		leftSec = max(0, endTime - app.GetGlobalTimeStamp())

		if leftSec > 0:
			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(leftSec), self.NORMAL_COLOR)

	if app.ENABLE_COSTUME_EXTENDED_RECHARGE:
		def AppendMallItemLastTimeEx(self, endTime):
			leftSec = max(0, endTime - app.GetGlobalTimeStamp())

			if leftSec > item.MIN_INFINITE_DURATION:
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.INFINITE_USE, self.CONDITION_COLOR)
				return

			if leftSec > 0:
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(leftSec), self.NORMAL_COLOR)

	def AppendAntiflagInformation(self, itemVnum = 0, window_type = None, slotIndex = None):
		if app.USE_OFFLINESHOP_EXTENDED_SLOTS and itemVnum == offlineshop.OFFLINESHOP_LOCKED_SLOT_ITEMVNUM:
			return

		antiFlagDict = {
		"|Eemoji/antiflag_drop|e" : item.ITEM_ANTIFLAG_DROP, ## ++
		"|Eemoji/antiflag_sellprivate|e" : item.ITEM_ANTIFLAG_SELL, ## ++
		"|Eemoji/antiflag_trade|e" : item.ITEM_ANTIFLAG_GIVE,
		"|Eemoji/anti_stack|e" : item.ITEM_ANTIFLAG_STACK,
		"|Eemoji/antiflag_sellprivate|e" : item.ITEM_ANTIFLAG_MYSHOP, ## ++
		"|Eemoji/antiflag_safebox|e" : item.ITEM_ANTIFLAG_SAFEBOX, ## ++
		}

		antiFlagNames = [name for name, flag in antiFlagDict.iteritems() if item.IsAntiFlag(flag)]
		if app.ENABLE_ACCOUNT_BIND_ITEMS and window_type is not None and slotIndex is not None:
			if player.IsItemAccountBound(window_type, slotIndex):
				abindMarks = [
					"|Eemoji/antiflag_drop|e",
					"|Eemoji/antiflag_sellprivate|e",
					"|Eemoji/antiflag_trade|e",
					"|Eemoji/antiflag_sellprivate|e",
					"|Eemoji/antiflag_safebox|e",
				]
				for mark in abindMarks:
					if mark not in antiFlagNames:
						antiFlagNames.append(mark)

		if antiFlagNames:
			self.AppendSpace(5)
			textLine2 = self.AppendTextLine('| {} |'.format(''.join(antiFlagNames)), self.DISABLE_COLOR)
			textLine2.SetFeather()
			self.AppendSpace(2)
		# textLine1 = self.AppendTextLine(localeinfo.NOT_POSSIBLE, self.DISABLE_COLOR)
		# textLine1.SetFeather()



	def AppendTimerBasedOnWearLastTime(self, metinSlot):
		if 0 == metinSlot[0]:
			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.CANNOT_USE, self.DISABLE_COLOR)
		elif app.ENABLE_DSS_EXTENDED_RECHARGE and metinSlot[0] > item.MIN_INFINITE_DURATION:
			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.INFINITE_USE, self.CONDITION_COLOR)
		else:
			endTime = app.GetGlobalTimeStamp() + metinSlot[0]
			self.AppendMallItemLastTime(endTime)

	def AppendRealTimeStartFirstUseLastTime(self, item, metinSlot, limitIndex):
		useCount = metinSlot[1]
		endTime = metinSlot[0]

		if 0 == useCount:
			if 0 == endTime:
				(limitType, limitValue) = item.GetLimit(limitIndex)
				endTime = limitValue

			endTime += app.GetGlobalTimeStamp()

		self.AppendMallItemLastTime(endTime)

	if app.ENABLE_NEW_USER_CARE:
		def __AppendRealTimeToolTip(self, itemVnum, endTime):
			item.SelectItem(itemVnum)

			for i in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(i)

				if item.LIMIT_REAL_TIME == limitType and limitValue > 0:
					self.AppendSpace(5)
					leftSec = max(0, endTime - app.GetGlobalTimeStamp())
					if leftSec > 0:
						self.AppendTextLine(localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(leftSec), self.NORMAL_COLOR)
					return
				else:
					continue

	def AppendTextLineAbsorb(self, text, color = FONT_COLOR, centerAlign = True):
		return ToolTip.AppendTextLine(self, text, color, centerAlign)

	if app.USE_AURA_SYSTEM:
		def SetAuraWindowItem(self, slotIndex):
			itemVnum = player.GetAuraItemID(slotIndex)
			if 0 == itemVnum: return

			self.ClearToolTip()
			if shop.IsOpen() and not shop.IsPrivateShop():
				self.AppendSellingPrice(item.GetISellItemPrice(item.SelectItem(itemVnum)))

			metinSlot = [player.GetAuraItemMetinSocket(slotIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
			attrSlot = [player.GetAuraItemAttribute(slotIndex, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

			self.AddItemData(itemVnum, metinSlot, attrSlot, player.AURA_REFINE, slotIndex)

		def __AppendAffectInformationAura(self, windowType, slotIndex, metinSlot):
			socketLevelValue = 0

			if not app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
				socketBoostValue = 0

			if windowType == player.INVENTORY or (app.USE_AURA_SYSTEM and windowType == player.CHANGE_EQUIP):
				socketLevelValue = player.GetItemMetinSocket(windowType, slotIndex, player.ITEM_SOCKET_AURA_CURRENT_LEVEL)
				if metinSlot[player.ITEM_SOCKET_AURA_CURRENT_LEVEL] != 0 and socketLevelValue == 0:
					socketLevelValue = metinSlot[player.ITEM_SOCKET_AURA_CURRENT_LEVEL]

				if not app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
					socketBoostValue = player.GetItemMetinSocket(windowType, slotIndex, player.ITEM_SOCKET_AURA_BOOST)
					if metinSlot[player.ITEM_SOCKET_AURA_BOOST] != 0 and socketBoostValue == 0:
						socketBoostValue = metinSlot[player.ITEM_SOCKET_AURA_BOOST]
			elif windowType == player.AURA_REFINE:
				socketLevelValue = player.GetAuraItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_CURRENT_LEVEL)

				if not app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
					socketBoostValue = player.GetAuraItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_BOOST)
			elif windowType == player.SAFEBOX:
				socketLevelValue = safebox.GetItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_CURRENT_LEVEL)

				if not app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
					socketBoostValue = safebox.GetItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_BOOST)

			if socketLevelValue == 0:
				return

			curLevel = (socketLevelValue / 100000) - 1000
			curStep = player.GetAuraRefineInfo(curLevel, player.AURA_REFINE_INFO_STEP)
			if curStep < item.AURA_GRADE_RADIANT:
				curExpPer = 100.0 * (socketLevelValue % 100000) / player.GetAuraRefineInfo(curLevel, player.AURA_REFINE_INFO_NEED_EXP)

			self.AppendTextLine(localeinfo.AURA_LEVEL_STEP % (curLevel, curStep), self.CONDITION_COLOR)
			if curStep < item.AURA_GRADE_RADIANT:
				self.AppendTextLine(localeinfo.AURA_TOOLTIP_EXP % (curExpPer), self.CONDITION_COLOR)

			if not app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
				boostPercent = 0
				if socketBoostValue != 0:
					curBoostIndex = socketBoostValue / 100000000
					boostItemVnum = curBoostIndex + item.AURA_BOOST_ITEM_VNUM_BASE
					if boostItemVnum:
						item.SelectItem(boostItemVnum)
						boostPercent = item.GetValue(player.ITEM_VALUE_AURA_BOOST_PERCENT)

				if boostPercent > 0:
					self.AppendTextLine(localeinfo.AURA_DRAIN_BOOST_PER % (1.0 * curLevel / 10, boostPercent), self.CONDITION_COLOR)
				else:
					self.AppendTextLine(localeinfo.AURA_DRAIN_PER % (1.0 * curLevel / 10), self.CONDITION_COLOR)

		if not app.USE_AURA_ACCESSORY_SOCKET_RENEWED:
			def __AppendAuraItemAffectInformation(self, oriItemVnum, windowType, slotIndex, metinSlot):
				socketLevelValue = 0
				socketBoostValue = 0
				if windowType == player.INVENTORY or (app.USE_AURA_SYSTEM and windowType == player.CHANGE_EQUIP):
					socketLevelValue = player.GetItemMetinSocket(windowType, slotIndex, player.ITEM_SOCKET_AURA_CURRENT_LEVEL)
					if metinSlot[player.ITEM_SOCKET_AURA_CURRENT_LEVEL] != 0 and socketLevelValue == 0:
						socketLevelValue = metinSlot[player.ITEM_SOCKET_AURA_CURRENT_LEVEL]
					socketBoostValue = player.GetItemMetinSocket(windowType, slotIndex, player.ITEM_SOCKET_AURA_BOOST)
					if metinSlot[player.ITEM_SOCKET_AURA_BOOST] != 0 and socketBoostValue == 0:
						socketBoostValue = metinSlot[player.ITEM_SOCKET_AURA_BOOST]
				elif windowType == player.AURA_REFINE:
					socketLevelValue = player.GetAuraItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_CURRENT_LEVEL)
					socketBoostValue = player.GetAuraItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_BOOST)
				elif windowType == player.SAFEBOX:
					socketLevelValue = safebox.GetItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_CURRENT_LEVEL)
					socketBoostValue = safebox.GetItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_BOOST)

				if socketLevelValue == 0:
					return

				curLevel = (socketLevelValue / 100000) - 1000
				boostPercent = 0.0
				if socketBoostValue != 0:
					curBoostIndex = socketBoostValue / 100000000
					boostItemVnum = curBoostIndex + item.AURA_BOOST_ITEM_VNUM_BASE
					if boostItemVnum:
						item.SelectItem(boostItemVnum)
						boostPercent = item.GetValue(player.ITEM_VALUE_AURA_BOOST_PERCENT) / 100.0

				drainlate = curLevel / 10. / 100. + boostPercent

				socketInDrainItemVnum = 0
				if windowType == player.INVENTORY or (app.USE_AURA_SYSTEM and windowType == player.CHANGE_EQUIP):
					socketInDrainItemVnum = player.GetItemMetinSocket(windowType, slotIndex, player.ITEM_SOCKET_AURA_DRAIN_ITEM_VNUM)
					if not metinSlot[player.ITEM_SOCKET_AURA_DRAIN_ITEM_VNUM] == 0 and socketInDrainItemVnum == 0:
						socketInDrainItemVnum = metinSlot[player.ITEM_SOCKET_AURA_DRAIN_ITEM_VNUM]
				elif windowType == player.AURA_REFINE:
					socketInDrainItemVnum = player.GetAuraItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_DRAIN_ITEM_VNUM)
				elif windowType == player.SAFEBOX:
					socketInDrainItemVnum = safebox.GetItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_DRAIN_ITEM_VNUM)

				if socketInDrainItemVnum == 0:
					return

				item.SelectItem(socketInDrainItemVnum)
				itemType = item.GetItemType()
				if itemType == item.ITEM_TYPE_ARMOR:
					defBonus = item.GetValue(5)*2
					if item.GetValue(1) >= 1:
						defGrade = max(((item.GetValue(1) + defBonus) * drainlate) , 1)
						if defGrade > 0:
							self.AppendSpace(5)
							self.AppendTextLineAbsorb(localeinfo.TOOLTIP_ITEM_DEF_GRADE % (defGrade), self.GetChangeTextLineColor(defGrade))

				for i in xrange(item.ITEM_APPLY_MAX_NUM):
					(affectType, affectValue) = item.GetAffect(i)
					if affectValue > 0:
						affectValue = max((affectValue * drainlate), 1)
						affectString = self.__GetAffectString(affectType, affectValue)
						if affectString:
							self.AppendTextLineAbsorb(affectString, self.GetChangeTextLineColor(affectValue))

				item.SelectItem(oriItemVnum)

			def __AppendAttributeInformationAura(self, windowType, slotIndex, attrSlot, metinSlot):
				if 0 != attrSlot:
					socketLevelValue = 0
					socketBoostValue = 0
					if windowType == player.INVENTORY or (app.USE_AURA_SYSTEM and windowType == player.CHANGE_EQUIP):
						socketLevelValue = player.GetItemMetinSocket(windowType, slotIndex, player.ITEM_SOCKET_AURA_CURRENT_LEVEL)
						socketBoostValue = player.GetItemMetinSocket(windowType, slotIndex, player.ITEM_SOCKET_AURA_BOOST)
						if metinSlot[player.ITEM_SOCKET_AURA_CURRENT_LEVEL] != 0 and socketLevelValue == 0:
							socketLevelValue = metinSlot[player.ITEM_SOCKET_AURA_CURRENT_LEVEL]
						if metinSlot[player.ITEM_SOCKET_AURA_BOOST] != 0 and socketBoostValue == 0:
							socketBoostValue = metinSlot[player.ITEM_SOCKET_AURA_BOOST]
					elif windowType == player.AURA_REFINE:
						socketLevelValue = player.GetAuraItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_CURRENT_LEVEL)
						socketBoostValue = player.GetAuraItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_BOOST)
					elif windowType == player.SAFEBOX:
						socketLevelValue = safebox.GetItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_CURRENT_LEVEL)
						socketBoostValue = safebox.GetItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_BOOST)

					if socketLevelValue == 0:
						return

					curLevel = (socketLevelValue / 100000) - 1000
					boostPercent = 0.0
					if socketBoostValue != 0:
						curBoostIndex = socketBoostValue / 100000000
						boostItemVnum = curBoostIndex + item.AURA_BOOST_ITEM_VNUM_BASE
						if boostItemVnum:
							item.SelectItem(boostItemVnum)
							boostPercent = item.GetValue(player.ITEM_VALUE_AURA_BOOST_PERCENT) / 100.0

					drainlate = curLevel / 10. / 100. + boostPercent

					for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
						type = attrSlot[i][0]
						value = attrSlot[i][1]
						if 0 >= value:
							continue

						value = max(((value) * drainlate) , 1)
						affectString = self.__GetAffectString(type, value)

						if affectString:
							affectColor = self.__GetAttributeColor(i, value)
							self.AppendTextLine(affectString, affectColor)

			def __AppendAuraBoostMetinSlotInfo(self, oriItemVnum, windowType, slotIndex, metinSlot):
				socketBoostValue = 0
				if windowType == player.INVENTORY or (app.USE_AURA_SYSTEM and windowType == player.CHANGE_EQUIP):
					socketBoostValue = player.GetItemMetinSocket(windowType, slotIndex, player.ITEM_SOCKET_AURA_BOOST)
					if metinSlot[player.ITEM_SOCKET_AURA_BOOST] != 0 and socketBoostValue == 0:
						socketBoostValue = metinSlot[player.ITEM_SOCKET_AURA_BOOST]
				elif windowType == player.AURA_REFINE:
					socketBoostValue = player.GetAuraItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_BOOST)
				elif windowType == player.SAFEBOX:
					socketBoostValue = safebox.GetItemMetinSocket(slotIndex, player.ITEM_SOCKET_AURA_BOOST)

				if socketBoostValue == 0:
					return

				curBoostIndex = socketBoostValue / 100000000

				socketImageDict = {
					player.METIN_SOCKET_TYPE_SILVER : "d:/ymir work/ui/game/windows/metin_slot_silver.sub",
					player.METIN_SOCKET_TYPE_GOLD : "d:/ymir work/ui/game/windows/metin_slot_gold.sub",
				}
				socketType = player.METIN_SOCKET_TYPE_NONE
				if item.ITEM_AURA_BOOST_ERASER < curBoostIndex < item.ITEM_AURA_BOOST_ULTIMATE:
					socketType = player.METIN_SOCKET_TYPE_SILVER
				elif curBoostIndex == item.ITEM_AURA_BOOST_ULTIMATE:
					socketType = player.METIN_SOCKET_TYPE_GOLD

				if player.METIN_SOCKET_TYPE_NONE == socketType:
					return

				boostRemainTime = socketBoostValue % 100000000
				boostItemVnum = curBoostIndex + item.AURA_BOOST_ITEM_VNUM_BASE

				self.AppendSpace(5)

				slotImage = ui.ImageBox()
				slotImage.SetParent(self)
				slotImage.LoadImage(socketImageDict[socketType])
				slotImage.Show()
				self.childrenList.append(slotImage)

				## Name
				nameTextLine = ui.TextLine()
				nameTextLine.SetParent(self)
				nameTextLine.SetFontName(self.defFontName)
				nameTextLine.SetPackedFontColor(self.NORMAL_COLOR)
				nameTextLine.SetOutline()
				nameTextLine.SetFeather()
				nameTextLine.Show()
				self.childrenList.append(nameTextLine)

				if localeinfo.IsARABIC():
					slotImage.SetPosition(self.toolTipWidth - slotImage.GetWidth() - 9, self.toolTipHeight-1)
					nameTextLine.SetPosition(self.toolTipWidth - 50, self.toolTipHeight + 2)
				else:
					slotImage.SetPosition(9, self.toolTipHeight-1)
					nameTextLine.SetPosition(50, self.toolTipHeight + 2)

				boostItemImage = ui.ImageBox()
				boostItemImage.SetParent(self)
				boostItemImage.Show()
				self.childrenList.append(boostItemImage)

				if boostItemVnum:
					item.SelectItem(boostItemVnum)
					try:
						boostItemImage.LoadImage(item.GetIconImageFileName())
					except:
						dbg.TraceError("ItemToolTip.__AppendAuraBoostMetinSlotInfo() - Failed to find image file %d:%s" % (boostItemVnum, item.GetIconImageFileName()))

					nameTextLine.SetText(item.GetItemName())

					boostDrainTextLine = ui.TextLine()
					boostDrainTextLine.SetParent(self)
					boostDrainTextLine.SetFontName(self.defFontName)
					boostDrainTextLine.SetPackedFontColor(self.POSITIVE_COLOR)
					boostDrainTextLine.SetOutline()
					boostDrainTextLine.SetFeather()
					boostDrainTextLine.SetText(localeinfo.AURA_BOOST_DRAIN_PER % (item.GetValue(player.ITEM_VALUE_AURA_BOOST_PERCENT)))
					boostDrainTextLine.Show()
					self.childrenList.append(boostDrainTextLine)

					if localeinfo.IsARABIC():
						boostItemImage.SetPosition(self.toolTipWidth - boostItemImage.GetWidth() - 10, self.toolTipHeight)
						boostDrainTextLine.SetPosition(self.toolTipWidth - 50, self.toolTipHeight + 16 + 2)
					else:
						boostItemImage.SetPosition(10, self.toolTipHeight)
						boostDrainTextLine.SetPosition(50, self.toolTipHeight + 16 + 2)

					if 1 == item.GetValue(player.ITEM_VALUE_AURA_BOOST_UNLIMITED):
						boostRemainTime = 0

					if 0 != boostRemainTime:
						timeText = (localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(boostRemainTime))

						timeTextLine = ui.TextLine()
						timeTextLine.SetParent(self)
						timeTextLine.SetFontName(self.defFontName)
						timeTextLine.SetPackedFontColor(self.POSITIVE_COLOR)
						timeTextLine.SetPosition(50, self.toolTipHeight + 16 + 2 + 16 + 2)
						timeTextLine.SetOutline()
						timeTextLine.SetFeather()
						timeTextLine.Show()
						timeTextLine.SetText(timeText)
						self.childrenList.append(timeTextLine)
						self.toolTipHeight += 16 + 2

				self.toolTipHeight += 35
				self.ResizeToolTip()

	if app.USE_ACCE_SYSTEM:
		def SetAcceResultItem(self, slotIndex, window_type = player.INVENTORY):
			(itemVnum, MinAbs, MaxAbs) = acce.GetResultItem()
			if not itemVnum:
				return

			self.ClearToolTip()

			metinSlot = [player.GetItemMetinSocket(window_type, slotIndex, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
			attrSlot = [player.GetItemAttribute(window_type, slotIndex, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
			apply_random_list = []
			if app.ENABLE_APPLY_RANDOM:
				apply_random_list = [player.GetItemApplyRandom(window_type, slotIndex, i) for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]
			item.SelectItem(itemVnum)
			itemType = item.GetItemType()
			itemSubType = item.GetItemSubType()
			if itemType != item.ITEM_TYPE_COSTUME and itemSubType != item.COSTUME_TYPE_ACCE:
				return

			absChance = MaxAbs
			itemDesc = item.GetItemDescription()
			self.__AdjustMaxWidth(attrSlot, itemDesc)
			self.__SetItemTitle(itemVnum, metinSlot, attrSlot,0)# need to add setValue here
			self.AppendDescription(itemDesc, 26)
			self.AppendDescription(item.GetItemSummary(), 26, self.CONDITION_COLOR)
			self.__AppendLimitInformation()

			## ABSORPTION RATE
			if MinAbs == MaxAbs:
				self.AppendTextLine(localeinfo.TOOLTIP_APPLY_ACCEDRAIN_RATE(MinAbs), self.CONDITION_COLOR)
			else:
				self.AppendTextLine(localeinfo.TOOLTIP_APPLY_ACCEDRAIN_RATE(MinAbs) + " ~ %d%%" % (MaxAbs), self.CONDITION_COLOR)
			## END ABSOPRTION RATE

			itemAbsorbedVnum = int(metinSlot[acce.ABSORBED_SOCKET])
			if itemAbsorbedVnum:
				## ATTACK / DEFENCE
				item.SelectItem(itemAbsorbedVnum)
				if item.GetItemType() == item.ITEM_TYPE_WEAPON:
					if item.GetItemSubType() == item.WEAPON_FAN:
						self.__AppendMagicAttackInfo(absChance)
						item.SelectItem(itemAbsorbedVnum)
						self.__AppendAttackPowerInfo(absChance)
					else:
						self.__AppendAttackPowerInfo(absChance)
						item.SelectItem(itemAbsorbedVnum)
						self.__AppendMagicAttackInfo(absChance)
				elif item.GetItemType() == item.ITEM_TYPE_ARMOR:
					defGrade = item.GetValue(1)
					defBonus = item.GetValue(5) * 2
					defGrade = self.CalcAcceValue(defGrade, absChance)
					defBonus = self.CalcAcceValue(defBonus, absChance)

					if defGrade > 0:
						self.AppendSpace(5)
						self.AppendTextLine(localeinfo.TOOLTIP_ITEM_DEF_GRADE % (defGrade + defBonus), self.GetChangeTextLineColor(defGrade))

					item.SelectItem(itemAbsorbedVnum)
					self.__AppendMagicDefenceInfo(absChance)
				## END ATTACK / DEFENCE

				## EFFECT
				item.SelectItem(itemAbsorbedVnum)
				for i in xrange(item.ITEM_APPLY_MAX_NUM):
					(affectType, affectValue) = item.GetAffect(i)
					affectValue = self.CalcAcceValue(affectValue, absChance)
					affectString = self.__GetAffectString(affectType, affectValue)
					if affectString and affectValue > 0:
						self.AppendTextLine(affectString, self.GetChangeTextLineColor(affectValue))

					item.SelectItem(itemAbsorbedVnum)
				# END EFFECT

				if app.ENABLE_APPLY_RANDOM:
					self.__AppendAcceDefaultItemApplyInformation(apply_random_list, metinSlot[acce.ABSORPTION_SOCKET])

			item.SelectItem(itemVnum)
			## ATTR
			self.__AppendAttributeInformation(attrSlot, MaxAbs)
			# END ATTR

			self.AppendWearableInformation()
			self.ShowToolTip()

		def SetAcceResultAbsItem(self, slotIndex1, slotIndex2, window_type = player.INVENTORY):
			itemVnumAcce = player.GetItemIndex(window_type, slotIndex1)
			itemVnumTarget = player.GetItemIndex(window_type, slotIndex2)
			if not itemVnumAcce or not itemVnumTarget:
				return

			self.ClearToolTip()

			item.SelectItem(itemVnumAcce)
			itemType = item.GetItemType()
			itemSubType = item.GetItemSubType()
			if itemType != item.ITEM_TYPE_COSTUME and itemSubType != item.COSTUME_TYPE_ACCE:
				return

			metinSlot = [player.GetItemMetinSocket(window_type, slotIndex1, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
			attrSlot = [player.GetItemAttribute(window_type, slotIndex2, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
			apply_random_list = []
			if app.ENABLE_APPLY_RANDOM:
				apply_random_list = [player.GetItemApplyRandom(window_type, slotIndex2, i) for i in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]
			itemDesc = item.GetItemDescription()
			self.__AdjustMaxWidth(attrSlot, itemDesc)
			self.__SetItemTitle(itemVnumAcce, metinSlot, attrSlot,0)#need to add setValue here
			self.AppendDescription(itemDesc, 26)
			self.AppendDescription(item.GetItemSummary(), 26, self.CONDITION_COLOR)
			item.SelectItem(itemVnumAcce)
			self.__AppendLimitInformation()

			## ABSORPTION RATE
			self.AppendTextLine(localeinfo.TOOLTIP_APPLY_ACCEDRAIN_RATE(metinSlot[acce.ABSORPTION_SOCKET]), self.CONDITION_COLOR)
			## END ABSOPRTION RATE

			## ATTACK / DEFENCE
			itemAbsorbedVnum = itemVnumTarget
			item.SelectItem(itemAbsorbedVnum)
			if item.GetItemType() == item.ITEM_TYPE_WEAPON:
				if item.GetItemSubType() == item.WEAPON_FAN:
					self.__AppendMagicAttackInfo(metinSlot[acce.ABSORPTION_SOCKET])
					self.__AppendAttackPowerInfo(metinSlot[acce.ABSORPTION_SOCKET])
				else:
					self.__AppendAttackPowerInfo(metinSlot[acce.ABSORPTION_SOCKET])
					self.__AppendMagicAttackInfo(metinSlot[acce.ABSORPTION_SOCKET])
			elif item.GetItemType() == item.ITEM_TYPE_ARMOR:
				defGrade = item.GetValue(1)
				defBonus = item.GetValue(5) * 2
				defGrade = self.CalcAcceValue(defGrade, metinSlot[acce.ABSORPTION_SOCKET])
				defBonus = self.CalcAcceValue(defBonus, metinSlot[acce.ABSORPTION_SOCKET])

				if defGrade > 0:
					self.AppendSpace(5)
					self.AppendTextLine(localeinfo.TOOLTIP_ITEM_DEF_GRADE % (defGrade + defBonus), self.GetChangeTextLineColor(defGrade))

				self.__AppendMagicDefenceInfo(metinSlot[acce.ABSORPTION_SOCKET])
			## END ATTACK / DEFENCE

			## EFFECT
			item.SelectItem(itemAbsorbedVnum)
			for i in xrange(item.ITEM_APPLY_MAX_NUM):
				(affectType, affectValue) = item.GetAffect(i)
				affectValue = self.CalcAcceValue(affectValue, metinSlot[acce.ABSORPTION_SOCKET])
				affectString = self.__GetAffectString(affectType, affectValue)
				if affectString and affectValue > 0:
					self.AppendTextLine(affectString, self.GetChangeTextLineColor(affectValue))
			## END EFFECT

			if app.ENABLE_APPLY_RANDOM:
				self.__AppendAcceDefaultItemApplyInformation(apply_random_list, metinSlot[acce.ABSORPTION_SOCKET])

			## ATTR
			item.SelectItem(itemAbsorbedVnum)
			for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
				type = attrSlot[i][0]
				value = attrSlot[i][1]
				if not value:
					continue

				value = self.CalcAcceValue(value, metinSlot[acce.ABSORPTION_SOCKET])
				affectString = self.__GetAffectString(type, value)
				if affectString and value > 0:
					affectColor = self.__GetAttributeColor(i, value)
					self.AppendTextLine(affectString, affectColor)
			## END ATTR

			## WEARABLE
			item.SelectItem(itemVnumAcce)
			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.TOOLTIP_ITEM_WEARABLE_JOB, self.NORMAL_COLOR)

			item.SelectItem(itemVnumAcce)
			flagList = (
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_WARRIOR),
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_ASSASSIN),
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_SURA),
				not item.IsAntiFlag(item.ITEM_ANTIFLAG_SHAMAN)
			)

			if not app.DISABLE_WOLFMAN_CREATION:
				flagList += (not item.IsAntiFlag(item.ITEM_ANTIFLAG_WOLFMAN),)

			characterNames = ""
			for i in xrange(self.CHARACTER_COUNT):
				name = self.CHARACTER_NAMES[i]
				flag = flagList[i]
				if flag:
					characterNames += " "
					characterNames += name

			textLine = self.AppendTextLine(characterNames, self.NORMAL_COLOR, True)
			textLine.SetFeather()

			item.SelectItem(itemVnumAcce)
			if item.IsAntiFlag(item.ITEM_ANTIFLAG_MALE):
				textLine = self.AppendTextLine(localeinfo.FOR_FEMALE, self.NORMAL_COLOR, True)
				textLine.SetFeather()

			if item.IsAntiFlag(item.ITEM_ANTIFLAG_FEMALE):
				textLine = self.AppendTextLine(localeinfo.FOR_MALE, self.NORMAL_COLOR, True)
				textLine.SetFeather()
			## END WEARABLE

			self.ShowToolTip()

	if app.ENABLE_GROWTH_PET_SYSTEM:
		def AddHyperLinkPetItemData(self, itemVnum, metinSlot, attrSlot, pet_info):
			
			pet_level			= int(pet_info[0], 16)
			pet_birthday		= int(pet_info[1], 16)
			pet_evol_level		= int(pet_info[2], 16)
			pet_hp				= int(pet_info[3], 16) / 10.0
			pet_def				= int(pet_info[4], 16) / 10.0
			pet_sp				= int(pet_info[5], 16) / 10.0
			pet_life_time		= int(pet_info[6], 16)
			pet_life_time_max	= int(pet_info[7], 16)
			pet_skill_count		= int(pet_info[8], 16)
			pet_item_vnum		= int(pet_info[9], 16)
			pet_nick_name		= pet_info[10]
			
			pet_skill_vnum		= [0] * player.PET_SKILL_COUNT_MAX
			pet_skill_level		= [0] * player.PET_SKILL_COUNT_MAX
			
			skill_index = 11
			for index in range(player.PET_SKILL_COUNT_MAX):
				pet_skill_vnum[index] = int(pet_info[skill_index], 16)
				skill_index = skill_index + 1
				pet_skill_level[index] = int(pet_info[skill_index], 16)
				skill_index = skill_index + 1
			
			self.itemVnum = itemVnum
			item.SelectItem(itemVnum)
			itemType = item.GetItemType()
			itemSubType = item.GetItemSubType()
			itemDesc = item.GetItemDescription()
			itemSummary = item.GetItemSummary()

			if item.ITEM_TYPE_PET != itemType:
				return
			
			if itemSubType not in [item.PET_UPBRINGING, item.PET_BAG]:
				return
			
			if item.PET_BAG == itemSubType:
				self.itemVnum = pet_item_vnum
				item.SelectItem(pet_item_vnum)
				pet_bag_desc = localeinfo.PET_BAG_DESC % item.GetItemName()
				self.__AdjustMaxWidth(0, pet_bag_desc)
				self.itemVnum = itemVnum
				item.SelectItem(itemVnum)

			if item.PET_BAG == itemSubType:
				self.AppendTextLine( pet_nick_name + "(" + localeinfo.PET_TOOLTIP_TRADABLE + ")", self.TITLE_COLOR )
			elif item.PET_UPBRINGING == itemSubType:
				self.AppendTextLine( pet_nick_name, self.TITLE_COLOR)
				
			
			## ??
			if item.PET_UPBRINGING == itemSubType:
				self.AppendDescription(itemDesc, 26)
				self.AppendDescription(itemSummary, 26, self.CONDITION_COLOR)
			elif item.PET_BAG == itemSubType:
				self.AppendDescription(pet_bag_desc, 26)
				self.itemVnum = itemVnum
				item.SelectItem(itemVnum)

			self.AppendSpace(5)
			if item.PET_UPBRINGING == itemSubType:
				cur_time = app.GetGlobalTimeStamp()
				
				# Pet's age stops at their death
				if metinSlot[0] < cur_time:
					pet_birthday = max(0, metinSlot[0] - pet_birthday)
				else:
					pet_birthday = max(0, cur_time - pet_birthday)
					
			elif item.PET_BAG == itemSubType:
				cur_time	 = app.GetGlobalTimeStamp()
				pet_birthday = max(0, cur_time - pet_birthday + (cur_time - metinSlot[1]))
				
			self.AppendTextLine(localeinfo.PET_TOOLTIP_LEVEL + " " + str(pet_level) + " (" + localeinfo.SecondToDay(pet_birthday) + ")")				

			self.AppendSpace(5)
			if pet_skill_count:
				self.AppendTextLine( self.GetEvolName(pet_evol_level) + "(" + str(pet_skill_count) + ")")
			else:
				self.AppendTextLine( self.GetEvolName(pet_evol_level) )

			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.PET_TOOLTIP_HP + " +" + str("%0.1f" % pet_hp) + "%", self.SPECIAL_POSITIVE_COLOR)
			self.AppendTextLine(localeinfo.PET_TOOLTIP_DEF + " +" + str("%0.1f" % pet_def) + "%", self.SPECIAL_POSITIVE_COLOR)
			self.AppendTextLine(localeinfo.PET_TOOLTIP_SP + " +" + str("%0.1f" % pet_sp) + "%", self.SPECIAL_POSITIVE_COLOR)				

			for index in range(player.PET_SKILL_COUNT_MAX):
				if pet_skill_vnum[index]:
					self.AppendSpace(5)
					( pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time ) = skill.GetPetSkillInfo(pet_skill_vnum[index])
					self.AppendTextLine( localeinfo.PET_TOOLTUP_SKILL % (pet_skill_name, pet_skill_level[index]) , self.SPECIAL_POSITIVE_COLOR)
						
			for i in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(i)
				if item.LIMIT_REAL_TIME == limitType:
					self.AppendPetItemLastTime(metinSlot[0])
				if item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
					self.AppendPetItemLastTime(metinSlot[0])

			
			self.ShowToolTip()
			
		def GetEvolName(self, evol_level):
		
			if 1 == evol_level:
				return localeinfo.PET_INFORMATION_STAGE1
			elif 2 == evol_level:
				return localeinfo.PET_INFORMATION_STAGE2
			elif 3 == evol_level:
				return localeinfo.PET_INFORMATION_STAGE3
			elif 4 == evol_level:
				return localeinfo.PET_INFORMATION_STAGE4
				
			return localeinfo.PET_INFORMATION_STAGE1
		
		def __PetSkillBookValueText(self, valueFormat, skillId, value, actPct, durDeci):
			if chr.PET_SKILL_FEATHER == skillId:
				return valueFormat(actPct, durDeci / 10.0, value, value * 2)
			if chr.PET_SKILL_AFFECT_INVINCIBILITY == skillId:
				return valueFormat(actPct, value / 10.0)
			if chr.PET_SKILL_AFFECT_HEAL == skillId:
				return valueFormat(actPct, value)
			if chr.PET_SKILL_AFFECT_REMOVAL == skillId:
				return valueFormat(actPct, 0)
			if chr.PET_SKILL_AFFECT_GOLD_DROP == skillId:
				return valueFormat(float(value))
			return valueFormat(value)

		def __AppendPetSkillBookInfo(self):
			if not hasattr(app, "GetPetSkillCurve"):
				return

			skillId = item.GetValue(0)
			if 0 == skillId:
				return

			valueFormat = PetSkillToolTip.PET_SKILL_APPLY_DATA_DICT.get(skillId, None)
			if not valueFormat:
				return

			(skillName, skillDesc, skillUseType, skillCoolTime) = skill.GetPetSkillInfo(skillId)
			(value1, valueMax, valueType6, act1, actMax, dur1, durMax) = app.GetPetSkillCurve(skillId)

			levelLine = getattr(localeinfo, "PET_SKILL_BOOK_LEVEL_LINE", "")
			if not levelLine or levelLine.startswith("Locale not found"):
				levelLine = "Level %d: %s"
			type6Line = getattr(localeinfo, "PET_SKILL_BOOK_TYPE6_LINE", "")
			if not type6Line or type6Line.startswith("Locale not found"):
				type6Line = "Type 6 pet at max level: %s"

			maxLevel = player.PET_GROWTH_SKILL_LEVEL_MAX

			self.AppendSpace(5)
			self.AppendTextLine(levelLine % (1, self.__PetSkillBookValueText(valueFormat, skillId, value1, act1, dur1)), self.NORMAL_COLOR)
			self.AppendTextLine(levelLine % (maxLevel, self.__PetSkillBookValueText(valueFormat, skillId, valueMax, actMax, durMax)), self.SPECIAL_POSITIVE_COLOR)
			if valueType6:
				self.AppendTextLine(type6Line % self.__PetSkillBookValueText(valueFormat, skillId, valueType6, actMax, durMax), self.SPECIAL_POSITIVE_COLOR)
			if skill.PET_SKILL_USE_TYPE_AUTO == skillUseType:
				self.AppendTextLine(localeinfo.PET_SKILL_TOOLTIP_COOLTIME % (skillCoolTime), self.NORMAL_COLOR)

		def __AppendPetBagItemInfomation(self, metinSlot):
			pet_id = metinSlot[2]
			if pet_id:
				self.ClearToolTip()
				growhPetVNum = player.GetPetItemVNumInBag(pet_id)
				if 0 == growhPetVNum:
					return

				item.SelectItem(growhPetVNum)
				pet_bag_desc = localeinfo.PET_BAG_DESC % item.GetItemName()
				self.__AdjustMaxWidth(0, pet_bag_desc)

				(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
				self.AppendTextLine( pet_nick + "(" + localeinfo.PET_TOOLTIP_TRADABLE + ")", self.TITLE_COLOR )

				## DESC
				self.AppendDescription(pet_bag_desc, 26)
				
				item.SelectItem(self.itemVnum)

				(skill_count, pet_skill1, pet_skill_level1, pet_skill_cool1, pet_skill2, pet_skill_level2, pet_skill_cool2, pet_skill3, pet_skill_level3, pet_skill_cool3) = player.GetPetSkill(pet_id)

				self.AppendSpace(5)

				cur_time = app.GetGlobalTimeStamp()
				birthSec = max(0, cur_time - birthday - (cur_time - metinSlot[1]))
				
				self.AppendTextLine(localeinfo.PET_TOOLTIP_LEVEL + " " + str(pet_level) + " (" + localeinfo.SecondToDay(birthSec) + ")")

				## Pet Evolution/Skill Count
				self.AppendSpace(5)
				if skill_count:
					self.AppendTextLine( self.GetEvolName(evol_level) + "(" + str(skill_count) + ")")
				else:
					self.AppendTextLine( self.GetEvolName(evol_level) )
					
				## Pet Stats
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.PET_TOOLTIP_HP + " +" + str("%0.1f" % pet_hp) + "%", self.SPECIAL_POSITIVE_COLOR)
				self.AppendTextLine(localeinfo.PET_TOOLTIP_DEF + " +" + str("%0.1f" % pet_def) + "%", self.SPECIAL_POSITIVE_COLOR)
				self.AppendTextLine(localeinfo.PET_TOOLTIP_SP + " +" + str("%0.1f" % pet_sp) + "%", self.SPECIAL_POSITIVE_COLOR)				
				
				## Pet Skills
				if pet_skill1:
					self.AppendSpace(5)
					( pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time ) = skill.GetPetSkillInfo(pet_skill1)
					self.AppendTextLine( localeinfo.PET_TOOLTUP_SKILL % (pet_skill_name, pet_skill_level1) , self.SPECIAL_POSITIVE_COLOR)
				if pet_skill2:
					( pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time ) = skill.GetPetSkillInfo(pet_skill2)
					self.AppendTextLine( localeinfo.PET_TOOLTUP_SKILL % (pet_skill_name, pet_skill_level2) , self.SPECIAL_POSITIVE_COLOR)
				if pet_skill3:
					( pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time) = skill.GetPetSkillInfo(pet_skill3)
					self.AppendTextLine( localeinfo.PET_TOOLTUP_SKILL % (pet_skill_name, pet_skill_level3) , self.SPECIAL_POSITIVE_COLOR)

				## Bag Duration
				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)
					if item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
						self.AppendPetItemLastTime(metinSlot[0])

		def __AppendPetEggItemInformation(self, metinSlot, isFeedWindow = False):
			for i in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(i)
				if item.LIMIT_REAL_TIME == limitType:
					self.AppendMallItemLastTime(metinSlot[0])

		def __AppendUpBringingPetItemInfomation(self, metinSlot):
			pet_id = metinSlot[2]
			if pet_id:
				## Skills
				(skill_count, pet_skill1, pet_skill_level1, pet_skill_cool1, pet_skill2, pet_skill_level2, pet_skill_cool2, pet_skill3, pet_skill_level3, pet_skill_cool3) = player.GetPetSkill(pet_id)
				
				## Pet Level/Age
				(pet_level, evol_level, birthday, pet_nick, pet_hp, pet_def, pet_sp) = player.GetPetItem(pet_id)
				self.AppendSpace(5)
				
				curTime = app.GetGlobalTimeStamp()
				birthSec = 0
				
				# Pet's age stops at their death
				if metinSlot[0] < curTime:
					birthSec = max(0, metinSlot[0] - birthday)
				else:
					birthSec = max(0, curTime - birthday)
				self.AppendTextLine(localeinfo.PET_TOOLTIP_LEVEL + " " + str(pet_level) + " (" + localeinfo.SecondToDay(birthSec) + ")")
			
				## Pet Evolution/Skill Count
				self.AppendSpace(5)
				if skill_count:
					self.AppendTextLine( self.GetEvolName(evol_level) + "(" + str(skill_count) + ")")
				else:
					self.AppendTextLine( self.GetEvolName(evol_level) )
					
				## Pet Stats
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.PET_TOOLTIP_HP + " +" + str("%0.1f" % pet_hp) + "%", self.SPECIAL_POSITIVE_COLOR)
				self.AppendTextLine(localeinfo.PET_TOOLTIP_DEF + " +" + str("%0.1f" % pet_def) + "%", self.SPECIAL_POSITIVE_COLOR)
				self.AppendTextLine(localeinfo.PET_TOOLTIP_SP + " +" + str("%0.1f" % pet_sp) + "%", self.SPECIAL_POSITIVE_COLOR)						
				
				## Pet Skills
				if pet_skill1:
					self.AppendSpace(5)
					( pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time ) = skill.GetPetSkillInfo(pet_skill1)
					self.AppendTextLine( localeinfo.PET_TOOLTUP_SKILL % (pet_skill_name, pet_skill_level1) , self.SPECIAL_POSITIVE_COLOR)
				if pet_skill2:
					( pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time ) = skill.GetPetSkillInfo(pet_skill2)
					self.AppendTextLine( localeinfo.PET_TOOLTUP_SKILL % (pet_skill_name, pet_skill_level2) , self.SPECIAL_POSITIVE_COLOR)
				if pet_skill3:
					( pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time) = skill.GetPetSkillInfo(pet_skill3)
					self.AppendTextLine( localeinfo.PET_TOOLTUP_SKILL % (pet_skill_name, pet_skill_level3) , self.SPECIAL_POSITIVE_COLOR)
					
				## Pet Duration
				for i in xrange(item.LIMIT_MAX_NUM):
					(limitType, limitValue) = item.GetLimit(i)
					if item.LIMIT_REAL_TIME == limitType:
						self.AppendPetItemLastTime(metinSlot[0])
			
		def AppendPetItemLastTime(self, endTime):
			self.AppendSpace(5)
			
			leftSec = endTime - app.GetGlobalTimeStamp()
			if leftSec >= 0:
				self.AppendTextLine(localeinfo.LEFT_TIME + " : " + localeinfo.SecondToDHM(leftSec), self.NORMAL_COLOR)
			else:
				self.AppendTextLine(localeinfo.LEFT_TIME + " : " + localeinfo.PET_TOOLTIP_LIFETIME_OVER, self.DISABLE_COLOR)

class HyperlinkItemToolTip(ItemToolTip):
	def __init__(self):
		ItemToolTip.__init__(self, isPickable=True)

	def __del__(self):
		ItemToolTip.__del__(self)

	def SetHyperlinkItem(self, tokens):
		minTokenCount = chat.HYPER_LINK_ITEM_KEYWORD + chat.HYPER_LINK_ITEM_VNUM + chat.HYPER_LINK_ITEM_FLAGS
		minTokenCount += player.METIN_SOCKET_MAX_NUM

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			minTokenCount += 1

		if app.ENABLE_SET_ITEM:
			minTokenCount += 1

		if app.ENABLE_APPLY_RANDOM:
			minTokenCount += 2 * player.APPLY_RANDOM_SLOT_MAX_NUM

		if app.USE_ENCHANT_COSTUMES:
			minTokenCount += 3 * player.ENCHANT_SLOT_MAX_NUM

		maxTokenCount = minTokenCount + 2 * player.ATTRIBUTE_SLOT_MAX_NUM

		if tokens and len(tokens) >= minTokenCount and len(tokens) <= maxTokenCount:
			head, vnum, flag = tokens[:chat.HYPER_LINK_ITEM_KEYWORD + chat.HYPER_LINK_ITEM_VNUM + chat.HYPER_LINK_ITEM_FLAGS]
			itemVnum = int(vnum, 16)
			metinSlot = [int(metin, 16) for metin in tokens[chat.HYPER_LINK_ITEM_SOCKET0:chat.HYPER_LINK_ITEM_SOCKET0 + player.METIN_SOCKET_MAX_NUM + 1]]

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				changelookvnum = int(tokens[chat.HYPER_LINK_ITEM_CHANGE_LOOK], 16)

			set_value = int(tokens[chat.HYPER_LINK_ITEM_SET], 16) if app.ENABLE_SET_ITEM else 0

			if app.ENABLE_APPLY_RANDOM:
				apply_random = tokens[chat.HYPER_LINK_ITEM_APPLY_RANDOM_TYPE0:chat.HYPER_LINK_ITEM_APPLY_RANDOM_VALUE3 + 1]
				if apply_random:
					apply_random_list = []

					apply_random.reverse()
					while apply_random:
						key = int(apply_random.pop(), 16)
						if apply_random:
							val = int(apply_random.pop())
							apply_random_list.append((key, val))

					apply_random_list += [(0, 0)] * (player.APPLY_RANDOM_SLOT_MAX_NUM - len(apply_random_list))
				else:
					apply_random_list = [(0, 0)] * player.APPLY_RANDOM_SLOT_MAX_NUM

			if app.USE_ENCHANT_COSTUMES:
				enchants = tokens[chat.HYPER_LINK_ITEM_ENCHANT_TYPE0:chat.HYPER_LINK_ITEM_ENCHANT_TIME3 + 1]
				if enchants:
					itemEnchantList = []

					enchants.reverse()
					while enchants:
						key = int(enchants.pop(), 16)
						if enchants:
							val = int(enchants.pop(), 16)
							if val:
								time = int(enchants.pop())
								if time:
									itemEnchantList.append((key, val, time))

					itemEnchantList += [(0, 0, 0)] * (player.ENCHANT_SLOT_MAX_NUM - len(itemEnchantList))
				else:
					itemEnchantList = [(0, 0, 0)] * player.ENCHANT_SLOT_MAX_NUM

			rests = tokens[minTokenCount:]
			if rests:
				attrSlot = []

				rests.reverse()
				while rests:
					key = int(rests.pop(), 16)
					
					if rests:
						val = int(rests.pop())
						attrSlot.append((key, val))
				
				attrSlot += [(0, 0)] * (player.ATTRIBUTE_SLOT_MAX_NUM - len(attrSlot))
			else:
				attrSlot = [(0, 0)] * player.ATTRIBUTE_SLOT_MAX_NUM

			self.ClearToolTip()
			self.AddItemData(itemVnum, metinSlot, attrSlot, None, 0, 0, player.INVENTORY, -1, None, apply_random_list, enchantList = itemEnchantList, iSetValue = set_value)

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				self.AppendChangeLookInfoItemVnum(changelookvnum)

			# Hint: SHIFT+left-click on the hyperlink opens this item in the wiki.
			# Wired in game.py / uichat*.py / uiwhisper.py click handlers.
			if app.ENABLE_INGAME_WIKI:
				self.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.WIKI_HYPERLINK_HINT)

			ItemToolTip.OnUpdate(self)

	if app.ENABLE_GROWTH_PET_SYSTEM:
		def SetHyperlinkPetItem(self, tokens):
			defaultTokenCount = 3 + 3
			petTokenCount = defaultTokenCount + 11 + (player.PET_SKILL_COUNT_MAX * 2)
			
			if tokens and len(tokens) == petTokenCount:
				head, vnum, flag = tokens[:3]
				itemVnum = int(vnum, 16)
				metinSlot = [int(metin, 16) for metin in tokens[3:6]]
				attrSlot = [(0, 0)] * player.ATTRIBUTE_SLOT_MAX_NUM
				
				self.ClearToolTip()
				self.AddHyperLinkPetItemData(itemVnum, metinSlot, attrSlot, tokens[6:])
				ItemToolTip.OnUpdate(self)

	def OnUpdate(self):
		pass

	def OnMouseLeftButtonDown(self):
		self.Hide()

class SkillToolTip(ToolTip):
	POINT_NAME_DICT = {
		player.LEVEL : localeinfo.SKILL_TOOLTIP_LEVEL,
		player.IQ : localeinfo.SKILL_TOOLTIP_INT,
	}

	SKILL_TOOL_TIP_WIDTH = 200
	PARTY_SKILL_TOOL_TIP_WIDTH = 340

	PARTY_SKILL_EXPERIENCE_AFFECT_LIST = (
		( 2, 2, 10,),
		( 8, 3, 20,),
		(14, 4, 30,),
		(22, 5, 45,),
		(28, 6, 60,),
		(34, 7, 80,),
		(38, 8, 100,),
	)

	PARTY_SKILL_PLUS_GRADE_AFFECT_LIST = (
		( 4, 2, 1, 0,),
		(10, 3, 2, 0,),
		(16, 4, 2, 1,),
		(24, 5, 2, 2,),
	)

	PARTY_SKILL_ATTACKER_AFFECT_LIST = (
		( 36, 3, ),
		( 26, 1, ),
		( 32, 2, ),
	)

	SKILL_GRADE_NAME = {
		player.SKILL_GRADE_MASTER : localeinfo.SKILL_GRADE_NAME_MASTER,
		player.SKILL_GRADE_GRAND_MASTER : localeinfo.SKILL_GRADE_NAME_GRAND_MASTER,
		player.SKILL_GRADE_PERFECT_MASTER : localeinfo.SKILL_GRADE_NAME_PERFECT_MASTER,
	}

	AFFECT_NAME_DICT = {
		"HP" : localeinfo.TOOLTIP_SKILL_AFFECT_ATT_POWER,
		"ATT_GRADE" : localeinfo.TOOLTIP_SKILL_AFFECT_ATT_GRADE,
		"DEF_GRADE" : localeinfo.TOOLTIP_SKILL_AFFECT_DEF_GRADE,
		"ATT_SPEED" : localeinfo.TOOLTIP_SKILL_AFFECT_ATT_SPEED,
		"MOV_SPEED" : localeinfo.TOOLTIP_SKILL_AFFECT_MOV_SPEED,
		"DODGE" : localeinfo.TOOLTIP_SKILL_AFFECT_DODGE,
		"RESIST_NORMAL" : localeinfo.TOOLTIP_SKILL_AFFECT_RESIST_NORMAL,
		"REFLECT_MELEE" : localeinfo.TOOLTIP_SKILL_AFFECT_REFLECT_MELEE,
	}

	AFFECT_APPEND_TEXT_DICT = {
		"DODGE" : "%",
		"RESIST_NORMAL" : "%",
		"REFLECT_MELEE" : "%",
	}

	def __init__(self):
		ToolTip.__init__(self, self.SKILL_TOOL_TIP_WIDTH)
	def __del__(self):
		ToolTip.__del__(self)

	if app.USE_RENEWAL_AFFECT_SHOWER:
		def SetSkillEx(self, skillIndex):
			if not skillIndex:
				return
			
			slotIndex=player.GetSkillSlotIndex(skillIndex)
			
			if slotIndex==None:
				return
			else:
				skillCurrentPercentage = player.GetSkillCurrentEfficientPercentage(slotIndex)
				
				for i in xrange(skill.GetSkillAffectDescriptionCount(skillIndex)):
					self.AppendTextLine(skill.GetSkillAffectDescription(skillIndex, i, skillCurrentPercentage), self.ENABLE_COLOR)
				
				self.ResizeToolTip()

	PASSIVE_ABILITY_ALL = [210, 211, 212, 213, 214, 215, 216]

	def SetPassiveAbilityToolTip(self, skillIndex):
		self.ClearToolTip()
		self.SetTitle(skill.GetSkillName(skillIndex))
		self.AppendSpace(5)

		slotIndex = player.GetSkillSlotIndex(skillIndex)
		skillLevel = self.__AbsSkillLevel(player.GetSkillGrade(slotIndex), player.GetSkillLevel(slotIndex))

		if skillIndex in (210, 211, 212):
			applyType = skill.GetPassiveAbilityApply(skillIndex)
			curLevel = min(skillLevel, 40)
			self.AppendTextLine(localeinfo.TOOLTIP_SKILL_LEVEL % curLevel, self.NORMAL_COLOR)
			curAffect = GET_AFFECT_STRING(applyType, skill.GetPassiveAbilityValue(skillIndex, curLevel))
			if curAffect:
				self.AppendTextLine(curAffect, self.POSITIVE_COLOR)
			if skillLevel < 40:
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.TOOLTIP_SKILL_LEVEL % (skillLevel + 1), self.NEGATIVE_COLOR)
				nextAffect = GET_AFFECT_STRING(applyType, skill.GetPassiveAbilityValue(skillIndex, skillLevel + 1))
				if nextAffect:
					self.AppendTextLine(nextAffect, self.NEGATIVE_COLOR)
		elif skillIndex == 213 or skillIndex == 214:
			self.__AppendMasterPassiveToolTip(skillIndex)
		elif skillIndex == 215:
			self.__AppendTranscendTable()
		elif skillIndex == 216:
			self.__AppendPvmBalanceToolTip()

		self.ShowToolTip()

	# Skill Master (213) / Passive Master (214): list the required skills with a
	# check_1.tga (at Perfect Master) or check_0.tga (not yet), per the player's job.
	def __AppendPvmBalanceToolTip(self):
		import constinfo
		info = getattr(constinfo, "PVM_BALANCE", None)
		if not info:
			info = {"bound":0, "level":0, "grade":0, "bonusA":0, "bonusB":0}
		self.SetTitle(localeinfo.PVM_BALANCE_NAME)
		self.AppendSpace(5)
		self.AppendDescription(localeinfo.PVM_BALANCE_DESC, 32, self.NORMAL_COLOR)
		self.AppendSpace(5)
		bound = info.get("bound", 0)
		if 0 == bound:
			self.AppendTextLine(localeinfo.PVM_BALANCE_UNLINKED, self.NEGATIVE_COLOR)
			return
		GRADE = {0:"", 1:" (M)", 2:" (G)", 3:" (P)"}
		gradeTxt = GRADE.get(info.get("grade", 0), "")
		self.AppendTextLine(localeinfo.PVM_BALANCE_LINKED % (skill.GetSkillName(bound), info.get("level", 0), gradeTxt), self.NORMAL_COLOR)
		self.AppendSpace(3)
		if info.get("bonusA", 0) > 0:
			self.AppendTextLine(localeinfo.PVM_BALANCE_BONUS_A % info.get("bonusA", 0), self.POSITIVE_COLOR)
		if info.get("bonusB", 0) > 0:
			self.AppendTextLine(localeinfo.PVM_BALANCE_BONUS_B % info.get("bonusB", 0), self.POSITIVE_COLOR)
		self.AppendSpace(3)
		self.AppendTextLine(localeinfo.PVM_BALANCE_PVPNOTE, self.NORMAL_COLOR)

	def __AppendTranscendTable(self):
		rules = skill.GetTranscendRules()
		if not rules:
			return

		reqLabel = {
			player.ATT_SPEED           : localeinfo.TRANSCEND_REQ_ATTSPEED,
			player.POINT_CRITICAL_PCT  : localeinfo.TRANSCEND_REQ_CRIT,
			player.POINT_PENETRATE_PCT : localeinfo.TRANSCEND_REQ_PIERCE,
			player.CASTING_SPEED       : localeinfo.TRANSCEND_REQ_CASTSPEED,
		}

		TBL_W = 400
		ROW_H = 22
		if self.toolTipWidth < TBL_W + 24:
			self.toolTipWidth = TBL_W + 24

		self.AppendDescription(localeinfo.TRANSCEND_INTRO, 32, self.NORMAL_COLOR)
		self.AppendSpace(5)

		headers = [localeinfo.TRANSCEND_COL_REQ, localeinfo.TRANSCEND_COL_RATE, localeinfo.TRANSCEND_COL_CUR, localeinfo.TRANSCEND_COL_BONUS]
		widths = [140, 80, 50, 130]

		rows = []
		rowColors = []
		for (srcPoint, threshold, perUnits, grant, dstPoint, dstApply) in rules:
			cur = player.GetStatus(srcPoint)
			gain = 0
			if cur > threshold and perUnits > 0:
				gain = ((cur - threshold) / perUnits) * grant
			name = reqLabel.get(srcPoint, "%d") % threshold
			grantTxt = GET_AFFECT_STRING(dstApply, gain)
			if not grantTxt:
				grantTxt = "+%d" % gain
			rateTxt = "%d = +%d%s" % (perUnits, grant, ("%" if dstApply in (71, 72, item.APPLY_THIRD_ATTRIBUTE_BONUS) else ""))
			rows.append([name, rateTxt, str(cur), grantTxt])
			rowColors.append([0, 0, 0, (0xff66dd66 if gain > 0 else 0xff888888)])

		if localeinfo.IsARABIC():
			headers.reverse()
			widths.reverse()
			rows = [r[::-1] for r in rows]
			rowColors = [c[::-1] for c in rowColors]

		colors = [0xff555555, 0xdd1a1a1a, 0x99000000, 0xffffda79, 0xffe6e6e6]
		tbl = ui.Table(TBL_W, ROW_H, colors)
		tbl.SetParent(self)
		tbl.SetPosition((self.toolTipWidth - TBL_W) / 2, self.toolTipHeight)
		tbl.set_columns(headers, widths)
		for idx, rowData in enumerate(rows):
			tbl.add_row(rowData, ROW_H, rowColors[idx])
		tbl.Show()
		self.childrenList.append(tbl)

		self.toolTipHeight += tbl.GetHeight() + 5
		self.ResizeToolTip()

	def __AppendMasterPassiveToolTip(self, skillIndex):
		TBL_W = 290
		ICON_W, NAME_W, STAT_W = 40, 195, 55
		HEAD_H, ROW_H = 20, 36
		if self.toolTipWidth < TBL_W + 24:
			self.toolTipWidth = TBL_W + 24

		if skillIndex == 213:
			self.AppendDescription(localeinfo.PASSIVE_DESC_SKILLMASTER, 32, self.NORMAL_COLOR)
		else:
			self.AppendDescription(localeinfo.PASSIVE_DESC_PASSIVEMASTER, 32, self.NORMAL_COLOR)
		for (mApply, mValue) in skill.GetPassiveMasterBonusList():
			mAffect = GET_AFFECT_STRING(mApply, mValue)
			if mAffect:
				self.AppendTextLine(mAffect, self.NEGATIVE_COLOR)
		self.AppendSpace(8)

		rows = []
		if skillIndex == 213:
			for slot in xrange(1, 7):
				vnum = player.GetSkillIndex(slot)
				if 0 == vnum:
					continue
				rows.append((vnum, player.GetSkillGrade(slot), player.GetSkillLevel(slot), False))
		else:
			for vnum in skill.GetPassiveMasterReqList():
				reqGrade = player.GetSkillGradeNew(vnum)
				rows.append((vnum, reqGrade, self.__AbsSkillLevel(reqGrade, player.GetSkillLevelNew(vnum)), True))
		if not rows:
			return

		headers = ["", localeinfo.MASTER_COL_SKILL, localeinfo.MASTER_COL_STATUS]
		widths = [ICON_W, NAME_W, STAT_W]
		cellRows = [["", skill.GetSkillName(v), ""] for (v, g, l, p) in rows]

		arabic = localeinfo.IsARABIC()
		if arabic:
			headers.reverse()
			widths.reverse()
			cellRows = [r[::-1] for r in cellRows]

		tableX = (self.toolTipWidth - TBL_W) / 2
		tableY = self.toolTipHeight
		colors = [0xff555555, 0xdd1a1a1a, 0x99000000, 0xffffda79, 0xffe6e6e6]
		tbl = ui.Table(TBL_W, HEAD_H, colors)
		tbl.SetParent(self)
		tbl.SetPosition(tableX, tableY)
		tbl.set_columns(headers, widths)
		for row in cellRows:
			tbl.add_row(row, ROW_H)
		tbl.Show()
		self.childrenList.append(tbl)

		if arabic:
			iconColX = tableX + STAT_W + NAME_W
			statColX = tableX
		else:
			iconColX = tableX
			statColX = tableX + ICON_W + NAME_W

		iconWindow = ui.SlotWindow()
		iconWindow.SetParent(self)
		iconWindow.SetPosition(0, 0)
		iconWindow.SetSize(self.toolTipWidth, tableY + HEAD_H + len(rows) * ROW_H + 4)
		for i, (v, g, l, p) in enumerate(rows):
			sy = tableY + HEAD_H + i * ROW_H + (ROW_H - 32) / 2
			iconWindow.AppendSlot(i, iconColX + (ICON_W - 32) / 2, sy, 32, 32)
			if p:
				iconWindow.SetSkillSlot(i, v, l)
			else:
				iconWindow.SetSkillSlotNew(i, v, g, l)
		iconWindow.RefreshSlot()
		iconWindow.Show()
		self.childrenList.append(iconWindow)

		for i, (v, g, l, p) in enumerate(rows):
			isPerfect = (g == skill.SKILL_GRADE_COUNT) or (l >= 40)
			check = ui.ImageBox()
			check.SetParent(self)
			check.LoadImage("d:/ymir work/ui/game/renewal_pvp/check_%d.tga" % (1 if isPerfect else 0))
			check.SetPosition(statColX + (STAT_W - 18) / 2, tableY + HEAD_H + i * ROW_H + (ROW_H - 18) / 2)
			check.Show()
			self.childrenList.append(check)

		self.toolTipHeight = tableY + tbl.GetHeight() + 5
		self.ResizeToolTip()

	# SetSkillLevel_ (PythonPlayer.cpp) stores graded skills as in-grade levels (M1=raw20 -> 1); rebuild the raw 0-40 level.
	def __AbsSkillLevel(self, skillGrade, skillLevel):
		if 1 == skillGrade:
			return skillLevel + 19
		if 2 == skillGrade:
			return skillLevel + 29
		if 3 == skillGrade:
			return skillLevel + 39
		return skillLevel

	# Mining Rework: the mining skill's exact contribution at level lv (mirrors the server formula in mining.cpp).
	def __MiningSkillVals(self, lv):
		succ = (lv - 10) * 10 / 20     # +5% at M(20), +10% at G(30); 0 below ~lv10
		if succ < 0:
			succ = 0
		if succ > 10:
			succ = 10
		dbl = 0                        # double-ore: 0 until G(30), then +1%/level to 10% at P(40)
		if lv > 30:
			dbl = lv - 30
			if dbl > 10:
				dbl = 10
		return succ, dbl

	def __AppendMiningSkillInfo(self, level):
		(curSucc, curDbl) = self.__MiningSkillVals(level)
		self.AppendSpace(5)
		self.AppendTextLine(localeinfo.TOOLTIP_MINING_SKILL_SUCCESS % curSucc, self.POSITIVE_COLOR)
		if curDbl > 0:
			self.AppendTextLine(localeinfo.TOOLTIP_MINING_SKILL_DOUBLE % curDbl, self.POSITIVE_COLOR)
		if level < 40:                 # SKILL_MAX_LEVEL -- show what the next level grants
			(nxtSucc, nxtDbl) = self.__MiningSkillVals(level + 1)
			self.AppendTextLine(localeinfo.TOOLTIP_MINING_SKILL_NEXT % (nxtSucc, nxtDbl), self.DISABLE_COLOR)

	# Fishing Rework: the fishing skill's exact contribution at level lv (mirrors the server formula in fishing.cpp).
	def __FishingSkillVals(self, lv):
		succ = (lv - 10) * 10 / 20
		if succ < 0:
			succ = 0
		if succ > 10:
			succ = 10
		dbl = 0
		if lv > 30:
			dbl = lv - 30
			if dbl > 10:
				dbl = 10
		return succ, dbl

	def __AppendFishingSkillInfo(self, level):
		(curSucc, curDbl) = self.__FishingSkillVals(level)
		self.AppendSpace(5)
		self.AppendTextLine(getattr(localeinfo, "TOOLTIP_FISHING_SKILL_SUCCESS", "Fishing success  +%d%%") % curSucc, self.POSITIVE_COLOR)
		if curDbl > 0:
			self.AppendTextLine(getattr(localeinfo, "TOOLTIP_FISHING_SKILL_DOUBLE", "Double catch chance  +%d%%") % curDbl, self.POSITIVE_COLOR)
		if level < 40:
			(nxtSucc, nxtDbl) = self.__FishingSkillVals(level + 1)
			self.AppendTextLine(getattr(localeinfo, "TOOLTIP_FISHING_SKILL_NEXT", "Next level:  +%d%% success / +%d%% double") % (nxtSucc, nxtDbl), self.DISABLE_COLOR)
	def SetSkill(self, skillIndex, skillLevel = -1):
		if 0 == skillIndex:
			return

		if app.USE_PASSIVE_ABILITY and skillIndex in self.PASSIVE_ABILITY_ALL:
			self.SetPassiveAbilityToolTip(skillIndex)
			return

		if skill.SKILL_TYPE_GUILD == skill.GetSkillType(skillIndex):
			if self.SKILL_TOOL_TIP_WIDTH != self.toolTipWidth:
				self.toolTipWidth = self.SKILL_TOOL_TIP_WIDTH
				self.ResizeToolTip()

			self.AppendDefaultData(skillIndex)
			self.AppendSkillConditionData(skillIndex)
			self.AppendGuildSkillData(skillIndex, skillLevel)

		else:
			if self.SKILL_TOOL_TIP_WIDTH != self.toolTipWidth:
				self.toolTipWidth = self.SKILL_TOOL_TIP_WIDTH
				self.ResizeToolTip()

			slotIndex = player.GetSkillSlotIndex(skillIndex)
			skillGrade = player.GetSkillGrade(slotIndex)
			skillLevel = player.GetSkillLevel(slotIndex)
			skillCurrentPercentage = player.GetSkillCurrentEfficientPercentage(slotIndex)
			skillNextPercentage = player.GetSkillNextEfficientPercentage(slotIndex)

			self.AppendDefaultData(skillIndex)
			self.AppendSkillConditionData(skillIndex)
			self.AppendSkillDataNew(slotIndex, skillIndex, skillGrade, skillLevel, skillCurrentPercentage, skillNextPercentage)
			self.AppendSkillRequirement(skillIndex, skillLevel)

		self.ShowToolTip()

	def SetSkillNew(self, slotIndex, skillIndex, skillGrade, skillLevel):
		if 0 == skillIndex:
			return

		if app.USE_PASSIVE_ABILITY and skillIndex in self.PASSIVE_ABILITY_ALL:
			self.SetPassiveAbilityToolTip(skillIndex)
			return

		if player.SKILL_INDEX_TONGSOL == skillIndex:
			slotIndex = player.GetSkillSlotIndex(skillIndex)
			skillLevel = player.GetSkillLevel(slotIndex)

			self.AppendDefaultData(skillIndex)
			self.__AppendLeaderShipSkillData(skillGrade, skillLevel)

		elif player.SKILL_INDEX_INSIGHT == skillIndex:
			slotIndex = player.GetSkillSlotIndex(skillIndex)
			skillLevel = player.GetSkillLevel(slotIndex)

			self.AppendDefaultData(skillIndex)
			self.__AppendInSightSkillData(skillGrade, skillLevel)

		elif player.SKILL_INDEX_RIDING == skillIndex:
			slotIndex = player.GetSkillSlotIndex(skillIndex)
			self.AppendSupportSkillDefaultData(skillIndex, skillGrade, skillLevel, 30)

		elif player.SKILL_INDEX_SUMMON == skillIndex:
			maxLevel = 10

			self.ClearToolTip()
			self.__SetSkillTitle(skillIndex, skillGrade)

			## Description
			description = skill.GetSkillDescription(skillIndex)
			self.AppendDescription(description, 25)

			if skillLevel == 10:
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.TOOLTIP_SKILL_LEVEL_MASTER % (skillLevel), self.NORMAL_COLOR)
				self.AppendTextLine(localeinfo.SKILL_SUMMON_DESCRIPTION % (skillLevel * 10), self.NORMAL_COLOR)

			else:
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.TOOLTIP_SKILL_LEVEL % (skillLevel), self.NORMAL_COLOR)
				self.__AppendSummonDescription(skillLevel, self.NORMAL_COLOR)

				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.TOOLTIP_SKILL_LEVEL % (skillLevel + 1), self.NEGATIVE_COLOR)
				self.__AppendSummonDescription(skillLevel + 1, self.NEGATIVE_COLOR)

		elif skill.SKILL_TYPE_GUILD == skill.GetSkillType(skillIndex):
			if self.SKILL_TOOL_TIP_WIDTH != self.toolTipWidth:
				self.toolTipWidth = self.SKILL_TOOL_TIP_WIDTH
				self.ResizeToolTip()

			self.AppendDefaultData(skillIndex)
			self.AppendSkillConditionData(skillIndex)
			self.AppendGuildSkillData(skillIndex, skillLevel)

		elif player.SKILL_INDEX_ROLE_PROFICIENCY == skillIndex:
			slotIndex = player.GetSkillSlotIndex(skillIndex)
			skillLevel = player.GetSkillLevel(slotIndex)

			self.AppendDefaultData(skillIndex)
			self.__AppendRoleProficiencySkillData(skillGrade, skillLevel)

		else:
			if self.SKILL_TOOL_TIP_WIDTH != self.toolTipWidth:
				self.toolTipWidth = self.SKILL_TOOL_TIP_WIDTH
				self.ResizeToolTip()

			slotIndex = player.GetSkillSlotIndex(skillIndex)

			skillCurrentPercentage = player.GetSkillCurrentEfficientPercentage(slotIndex)
			skillNextPercentage = player.GetSkillNextEfficientPercentage(slotIndex)

			self.AppendDefaultData(skillIndex, skillGrade)
			self.AppendSkillConditionData(skillIndex)
			self.AppendSkillDataNew(slotIndex, skillIndex, skillGrade, skillLevel, skillCurrentPercentage, skillNextPercentage)
			self.AppendSkillRequirement(skillIndex, skillLevel)

		self.ShowToolTip()

	def __SetSkillTitle(self, skillIndex, skillGrade):
		self.SetTitle(skill.GetSkillName(skillIndex, skillGrade))
		self.__AppendSkillGradeName(skillIndex, skillGrade)

	def __AppendSkillGradeName(self, skillIndex, skillGrade):
		if self.SKILL_GRADE_NAME.has_key(skillGrade):
			self.AppendSpace(5)
			self.AppendTextLine(self.SKILL_GRADE_NAME[skillGrade] % (skill.GetSkillName(skillIndex, 0)), self.CAN_LEVEL_UP_COLOR)

	def SetSkillOnlyName(self, slotIndex, skillIndex, skillGrade):
		if 0 == skillIndex:
			return

		slotIndex = player.GetSkillSlotIndex(skillIndex)

		self.toolTipWidth = self.SKILL_TOOL_TIP_WIDTH
		self.ResizeToolTip()

		self.ClearToolTip()
		self.__SetSkillTitle(skillIndex, skillGrade)
		self.AppendDefaultData(skillIndex, skillGrade)
		self.AppendSkillConditionData(skillIndex)
		self.ShowToolTip()

	def AppendDefaultData(self, skillIndex, skillGrade = 0):
		self.ClearToolTip()
		self.__SetSkillTitle(skillIndex, skillGrade)

		## Level Limit
		levelLimit = skill.GetSkillLevelLimit(skillIndex)
		if levelLimit > 0:
			color = self.NORMAL_COLOR
			if player.GetStatus(player.LEVEL) < levelLimit:
				color = self.NEGATIVE_COLOR

			self.AppendSpace(5)
			self.AppendTextLine(localeinfo.TOOLTIP_ITEM_LIMIT_LEVEL % (levelLimit), color)

		## Description
		description = skill.GetSkillDescription(skillIndex)
		self.AppendDescription(description, 25)

	def AppendSupportSkillDefaultData(self, skillIndex, skillGrade, skillLevel, maxLevel):
		self.ClearToolTip()
		self.__SetSkillTitle(skillIndex, skillGrade)

		if 1 == skillGrade:
			skillLevel += 19
		elif 2 == skillGrade:
			skillLevel += 29
		elif 3 == skillGrade:
			skillLevel = 40

		## Description
		description = skill.GetSkillDescription(skillIndex)
		self.AppendDescription(description, 25)
		self.AppendSpace(5)
		self.AppendTextLine(localeinfo.TOOLTIP_SKILL_LEVEL_WITH_MAX % (skillLevel, maxLevel), self.NORMAL_COLOR)

	def AppendSkillConditionData(self, skillIndex):
		conditionDataCount = skill.GetSkillConditionDescriptionCount(skillIndex)
		if conditionDataCount > 0:
			self.AppendSpace(5)
			for i in xrange(conditionDataCount):
				self.AppendTextLine(skill.GetSkillConditionDescription(skillIndex, i), self.CONDITION_COLOR)

	def AppendGuildSkillData(self, skillIndex, skillLevel):
		skillMaxLevel = 7
		skillCurrentPercentage = float(skillLevel) / float(skillMaxLevel)
		skillNextPercentage = float(skillLevel+1) / float(skillMaxLevel)
		## Current Level
		if skillLevel > 0:
			if self.HasSkillLevelDescription(skillIndex, skillLevel):
				self.AppendSpace(5)
				if skillLevel == skillMaxLevel:
					self.AppendTextLine(localeinfo.TOOLTIP_SKILL_LEVEL_MASTER % (skillLevel), self.NORMAL_COLOR)
				else:
					self.AppendTextLine(localeinfo.TOOLTIP_SKILL_LEVEL % (skillLevel), self.NORMAL_COLOR)

				#####

				for i in xrange(skill.GetSkillAffectDescriptionCount(skillIndex)):
					self.AppendTextLine(skill.GetSkillAffectDescription(skillIndex, i, skillCurrentPercentage), self.ENABLE_COLOR)

				## Cooltime
				coolTime = skill.GetSkillCoolTime(skillIndex, skillCurrentPercentage)
				if coolTime > 0:
					self.AppendTextLine(localeinfo.TOOLTIP_SKILL_COOL_TIME + str(coolTime), self.ENABLE_COLOR)

				## SP
				needGSP = skill.GetSkillNeedSP(skillIndex, skillCurrentPercentage)
				if needGSP > 0:
					self.AppendTextLine(localeinfo.TOOLTIP_NEED_GSP % (needGSP), self.ENABLE_COLOR)

		## Next Level
		if skillLevel < skillMaxLevel:
			if self.HasSkillLevelDescription(skillIndex, skillLevel+1):
				self.AppendSpace(5)
				self.AppendTextLine(localeinfo.TOOLTIP_NEXT_SKILL_LEVEL_1 % (skillLevel+1, skillMaxLevel), self.DISABLE_COLOR)

				#####

				for i in xrange(skill.GetSkillAffectDescriptionCount(skillIndex)):
					self.AppendTextLine(skill.GetSkillAffectDescription(skillIndex, i, skillNextPercentage), self.DISABLE_COLOR)

				## Cooltime
				coolTime = skill.GetSkillCoolTime(skillIndex, skillNextPercentage)
				if coolTime > 0:
					self.AppendTextLine(localeinfo.TOOLTIP_SKILL_COOL_TIME + str(coolTime), self.DISABLE_COLOR)

				## SP
				needGSP = skill.GetSkillNeedSP(skillIndex, skillNextPercentage)
				if needGSP > 0:
					self.AppendTextLine(localeinfo.TOOLTIP_NEED_GSP % (needGSP), self.DISABLE_COLOR)

	def AppendSkillDataNew(self, slotIndex, skillIndex, skillGrade, skillLevel, skillCurrentPercentage, skillNextPercentage):
		self.skillMaxLevelStartDict = { 0 : 17, 1 : 7, 2 : 10, }
		self.skillMaxLevelEndDict = { 0 : 20, 1 : 10, 2 : 10, }

		skillLevelUpPoint = 1
		realSkillGrade = player.GetSkillGrade(slotIndex)
		skillMaxLevelStart = self.skillMaxLevelStartDict.get(realSkillGrade, 15)
		skillMaxLevelEnd = self.skillMaxLevelEndDict.get(realSkillGrade, 20)

		## Current Level
		if skillLevel > 0:
			if self.HasSkillLevelDescription(skillIndex, skillLevel):
				self.AppendSpace(5)
				if skillGrade == skill.SKILL_GRADE_COUNT:
					pass
				elif skillLevel == skillMaxLevelEnd:
					self.AppendTextLine(localeinfo.TOOLTIP_SKILL_LEVEL_MASTER % (skillLevel), self.NORMAL_COLOR)
				else:
					self.AppendTextLine(localeinfo.TOOLTIP_SKILL_LEVEL % (skillLevel), self.NORMAL_COLOR)
				self.AppendSkillLevelDescriptionNew(skillIndex, skillCurrentPercentage, self.ENABLE_COLOR)

		## Next Level
		if skillGrade != skill.SKILL_GRADE_COUNT:
			if skillLevel < skillMaxLevelEnd:
				if self.HasSkillLevelDescription(skillIndex, skillLevel+skillLevelUpPoint):
					self.AppendSpace(5)
					if skillIndex == 141 or skillIndex == 142:
						self.AppendTextLine(localeinfo.TOOLTIP_NEXT_SKILL_LEVEL_3 % (skillLevel+1), self.DISABLE_COLOR)
					else:
						self.AppendTextLine(localeinfo.TOOLTIP_NEXT_SKILL_LEVEL_1 % (skillLevel+1, skillMaxLevelEnd), self.DISABLE_COLOR)
					self.AppendSkillLevelDescriptionNew(skillIndex, skillNextPercentage, self.DISABLE_COLOR)

		# Mining Rework: exact per-level mining bonuses (this method is reached by SetSkill AND SetSkillNew).
		if 124 == skillIndex:
			self.__AppendMiningSkillInfo(self.__AbsSkillLevel(skillGrade, skillLevel))
		if 123 == skillIndex:
			self.__AppendFishingSkillInfo(self.__AbsSkillLevel(skillGrade, skillLevel))

	def AppendSkillLevelDescriptionNew(self, skillIndex, skillPercentage, color):
		if app.__BUFFI_SUPPORT__:
			skill.SetBuffiIqOverride(constinfo.BUFFI_TOOLTIP_INT if (163 <= skillIndex <= 166) else -1)
		affectDataCount = skill.GetNewAffectDataCount(skillIndex)
		if affectDataCount > 0:
			for i in xrange(affectDataCount):
				type, minValue, maxValue = skill.GetNewAffectData(skillIndex, i, skillPercentage)
				if not self.AFFECT_NAME_DICT.has_key(type):
					continue

				minValue = int(minValue)
				maxValue = int(maxValue)
				affectText = self.AFFECT_NAME_DICT[type]

				if "HP" == type:
					if minValue < 0 and maxValue < 0:
						minValue *= -1
						maxValue *= -1

					else:
						affectText = localeinfo.TOOLTIP_SKILL_AFFECT_HEAL

				affectText += str(minValue)
				if minValue != maxValue:
					affectText += " - " + str(maxValue)
				affectText += self.AFFECT_APPEND_TEXT_DICT.get(type, "")

				#import debuginfo
				#if debuginfo.IsDebugMode():
				#	affectText = "!!" + affectText

				self.AppendTextLine(affectText, color)

		else:
			for i in xrange(skill.GetSkillAffectDescriptionCount(skillIndex)):
				self.AppendTextLine(skill.GetSkillAffectDescription(skillIndex, i, skillPercentage), color)

		## Duration
		duration = skill.GetDuration(skillIndex, skillPercentage)
		if duration > 0:
			self.AppendTextLine(localeinfo.TOOLTIP_SKILL_DURATION % (duration), color)

		## Cooltime
		coolTime = skill.GetSkillCoolTime(skillIndex, skillPercentage)
		if coolTime > 0:
			self.AppendTextLine(localeinfo.TOOLTIP_SKILL_COOL_TIME + str(coolTime), color)

		## SP
		needSP = skill.GetSkillNeedSP(skillIndex, skillPercentage)
		if needSP != 0:
			continuationSP = skill.GetSkillContinuationSP(skillIndex, skillPercentage)

			if skill.IsUseHPSkill(skillIndex):
				self.AppendNeedHP(needSP, continuationSP, color)
			else:
				self.AppendNeedSP(needSP, continuationSP, color)

	def AppendSkillRequirement(self, skillIndex, skillLevel):
		skillMaxLevel = skill.GetSkillMaxLevel(skillIndex)

		if skillLevel >= skillMaxLevel:
			return

		isAppendHorizontalLine = False

		## Requirement
		if skill.IsSkillRequirement(skillIndex):
			if not isAppendHorizontalLine:
				isAppendHorizontalLine = True
				self.AppendHorizontalLine()

			requireSkillName, requireSkillLevel = skill.GetSkillRequirementData(skillIndex)

			color = self.CANNOT_LEVEL_UP_COLOR
			if skill.CheckRequirementSueccess(skillIndex):
				color = self.CAN_LEVEL_UP_COLOR
			self.AppendTextLine(localeinfo.TOOLTIP_REQUIREMENT_SKILL_LEVEL % (requireSkillName, requireSkillLevel), color)

		## Require Stat
		requireStatCount = skill.GetSkillRequireStatCount(skillIndex)
		if requireStatCount > 0:
			for i in xrange(requireStatCount):
				type, level = skill.GetSkillRequireStatData(skillIndex, i)
				if self.POINT_NAME_DICT.has_key(type):
					if not isAppendHorizontalLine:
						isAppendHorizontalLine = True
						self.AppendHorizontalLine()

					name = self.POINT_NAME_DICT[type]
					color = self.CANNOT_LEVEL_UP_COLOR
					if player.GetStatus(type) >= level:
						color = self.CAN_LEVEL_UP_COLOR
					self.AppendTextLine(localeinfo.TOOLTIP_REQUIREMENT_STAT_LEVEL % (name, level), color)

	def HasSkillLevelDescription(self, skillIndex, skillLevel):
		if skill.GetSkillAffectDescriptionCount(skillIndex) > 0:
			return True
		if skill.GetSkillCoolTime(skillIndex, skillLevel) > 0:
			return True
		if skill.GetSkillNeedSP(skillIndex, skillLevel) > 0:
			return True

		return False

	def AppendMasterAffectDescription(self, index, desc, color):
		self.AppendTextLine(desc, color)

	def AppendNextAffectDescription(self, index, desc):
		self.AppendTextLine(desc, self.DISABLE_COLOR)

	def AppendNeedHP(self, needSP, continuationSP, color):
		self.AppendTextLine(localeinfo.TOOLTIP_NEED_HP % (needSP), color)

		if continuationSP > 0:
			self.AppendTextLine(localeinfo.TOOLTIP_NEED_HP_PER_SEC % (continuationSP), color)

	def AppendNeedSP(self, needSP, continuationSP, color):
		if -1 == needSP:
			self.AppendTextLine(localeinfo.TOOLTIP_NEED_ALL_SP, color)
		else:
			self.AppendTextLine(localeinfo.TOOLTIP_NEED_SP % (needSP), color)

		if continuationSP > 0:
			self.AppendTextLine(localeinfo.TOOLTIP_NEED_SP_PER_SEC % (continuationSP), color)

	def __AppendRoleProficiencySkillData(self, skill_grade, skill_level):
		if 1 == skill_grade:
			skill_level += 19
		elif 2 == skill_grade:
			skill_level += 29
		elif 3 == skill_grade:
			skill_level = 40

		if skill_level <= 0:
			return

		skillIndex = player.SKILL_INDEX_ROLE_PROFICIENCY
		slotIndex = player.GetSkillSlotIndex(skillIndex)

		self.AppendSpace(5)
		self.AutoAppendTextLine(localeinfo.TOOLTIP_ROLE_PROFICIENCY_SKILL_LEVEL % skill_level, self.NORMAL_COLOR)
		self.AutoAppendTextLine(localeinfo.TOOLTIP_ROLE_PROFICIENCY_LEADER_EFFECT % int(skill_level))

		self.AlignHorizonalCenter()

	def __AppendInSightSkillData(self, skill_grade, skill_level):
		if 1 == skill_grade:
			skill_level += 19
		elif 2 == skill_grade:
			skill_level += 29
		elif 3 == skill_grade:
			skill_level = 40

		if skill_level <= 0:
			return

		skillIndex = player.SKILL_INDEX_INSIGHT
		slotIndex = player.GetSkillSlotIndex(skillIndex)
		skillPower = player.GetSkillCurrentEfficientPercentage(slotIndex)

		if localeinfo.IsBRAZIL() or localeinfo.IsNEWCIBN():
			k = skillPower
		else:
			# k = float(skill.GetSkillPowerByLevel(skill_level) ) /100
			k = player.GetSkillLevel(skillIndex) / 100.0

		self.AppendSpace(5)
		self.AutoAppendTextLine(localeinfo.TOOLTIP_INSIGHT_SKILL_LEVEL % skill_level, self.NORMAL_COLOR)

		if skill_level >= 10:
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_ATTACKER % int(20 + 60 * k))

		if skill_level >= 20:
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_BERSERKER % int(2 + 5 * k))
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_TANKER % int(660 + 1450 * k))

		if skill_level >= 25:
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_BUFFER % int(5 + 45 * k))

		if skill_level >= 35:
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_SKILL_MASTER % int(15 + 600 * k))

		if skill_level >= 40:
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_DEFENDER % int(5 + 30 * k))

		self.AlignHorizonalCenter()

	def __AppendLeaderShipSkillData(self, skill_grade, skill_level):
		if 1 == skill_grade:
			skill_level += 19
		elif 2 == skill_grade:
			skill_level += 29
		elif 3 == skill_grade:
			skill_level = 40

		if skill_level <= 0:
			return

		skillIndex = player.SKILL_INDEX_TONGSOL
		slotIndex = player.GetSkillSlotIndex(skillIndex)
		skillPower = player.GetSkillCurrentEfficientPercentage(slotIndex)

		if localeinfo.IsBRAZIL() or localeinfo.IsNEWCIBN():
			k = skillPower
		else:
			# k = float(skill.GetSkillPowerByLevel(skill_level) ) /100
			k = player.GetSkillLevel(skillIndex) / 100.0

		self.AppendSpace(5)
		self.AutoAppendTextLine(localeinfo.TOOLTIP_PARTY_SKILL_LEVEL % skill_level, self.NORMAL_COLOR)

		if skill_level >= 10:
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_ATTACKER % int(10 + 60 * k))

		if skill_level >= 20:
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_BERSERKER % int(1 + 5 * k))
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_TANKER % int(50 + 1450 * k))

		if skill_level >= 25:
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_BUFFER % int(5 + 45 * k))

		if skill_level >= 35:
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_SKILL_MASTER % int(25 + 600 * k))

		if skill_level >= 40:
			self.AutoAppendTextLine(localeinfo.PARTY_SKILL_DEFENDER % int(5 + 30 * k))

		self.AlignHorizonalCenter()

	def __AppendSummonDescription(self, skillLevel, color):
		if skillLevel > 1:
			self.AppendTextLine(localeinfo.SKILL_SUMMON_DESCRIPTION % (skillLevel * 10), color)
		elif 1 == skillLevel:
			self.AppendTextLine(localeinfo.SKILL_SUMMON_DESCRIPTION % (15), color)
		elif 0 == skillLevel:
			self.AppendTextLine(localeinfo.SKILL_SUMMON_DESCRIPTION % (10), color)

if app.ENABLE_GROWTH_PET_SYSTEM:
	class PetSkillToolTip(ToolTip):

		PET_SKILL_TOOL_TIP_WIDTH = 255

		PET_SKILL_APPLY_DATA_DICT =	{
				chr.PET_SKILL_AFFECT_JIJOONG_WARRIOR	: localeinfo.TOOLTIP_ATTBONUS_PLAYERS,		# %d%%
				chr.PET_SKILL_AFFECT_JIJOONG_SURA		: localeinfo.TOOLTIP_APPLY_RESIST_SURA,			# %d%%
				chr.PET_SKILL_AFFECT_JIJOONG_ASSASSIN	: localeinfo.TOOLTIP_APPLY_RESIST_ASSASSIN,		# %d%%
				chr.PET_SKILL_AFFECT_JIJOONG_SHAMAN		: localeinfo.TOOLTIP_APPLY_RESIST_SHAMAN,		# %d%%
				chr.PET_SKILL_AFFECT_ATT_STONE	: localeinfo.TOOLTIP_APPLY_ATTBONUS_STONE,		# %d%%
				chr.PET_SKILL_AFFECT_PACHEON			: localeinfo.TOOLTIP_MELEE_MAGIC_ATTBONUS_PER,	# %d%%
				chr.PET_SKILL_AFFECT_CHEONRYEONG		: localeinfo.TOOLTIP_RESIST_MAGIC_REDUCTION,	# %d%%
				chr.PET_SKILL_AFFECT_BANYA				: localeinfo.TOOLTIP_CAST_SPEED,				# %d%%
				chr.PET_SKILL_AFFECT_CHOEHOENBIMU		: localeinfo.TOOLTIP_APPLY_PENETRATE_PCT,		# %d%%
				chr.PET_SKILL_AFFECT_HEAL				: localeinfo.PET_SKILL_TOOLTIP_HEAL,			# %d%%, %d
				chr.PET_SKILL_AFFECT_STEALHP			: localeinfo.TOOLTIP_APPLY_STEAL_HP,			# %d%%
				chr.PET_SKILL_AFFECT_STEALMP			: localeinfo.TOOLTIP_APPLY_STEAL_SP,			# %d%%
				chr.PET_SKILL_AFFECT_BLOCK				: localeinfo.TOOLTIP_APPLY_BLOCK,				# %d%%
				chr.PET_SKILL_AFFECT_REFLECT_MELEE		: localeinfo.TOOLTIP_APPLY_REFLECT_MELEE,		# %d%%
				chr.PET_SKILL_AFFECT_GOLD_DROP			: localeinfo.TOOLTIP_MALL_GOLDBONUS,			# %.1f%%
				chr.PET_SKILL_AFFECT_BOW_DISTANCE		: localeinfo.TOOLTIP_BOW_DISTANCE,				# %dm
				chr.PET_SKILL_AFFECT_INVINCIBILITY		: localeinfo.PET_SKILL_TOOLTIP_INVINVIBILITY,	# %d%%, %.1f
				chr.PET_SKILL_AFFECT_REMOVAL			: localeinfo.PET_SKILL_TOOLTIP_REMOVAL,			# %d%%
				chr.PET_SKILL_AFFECT_ATT_WARRIOR				: localeinfo.TOOLTIP_APPLY_ATTBONUS_WARRIOR,		# %d%%
				chr.PET_SKILL_AFFECT_ATT_SURA			: localeinfo.TOOLTIP_APPLY_ATTBONUS_SURA,	# %d%%
				chr.PET_SKILL_AFFECT_ATT_BOSS				: localeinfo.TOOLTIP_APPLY_ATTBONUS_BOSS,		# %d%%
				chr.PET_SKILL_AFFECT_EXP				: localeinfo.TOOLTIP_MALL_EXPBONUS,				# %d%%
				chr.PET_SKILL_FEATHER					: localeinfo.PET_SKILL_TOOLTIP_FEATHER,			# %d%%, %.1f, %d - %d
				chr.PET_SKILL_AFFECT_ATT_ASSASIN				: localeinfo.TOOLTIP_APPLY_ATTBONUS_ASSASSIN,
				chr.PET_SKILL_AFFECT_ATT_SHAMAN				: localeinfo.TOOLTIP_APPLY_ATTBONUS_SHAMAN,
		}

		def __init__(self):
			ToolTip.__init__(self, self.PET_SKILL_TOOL_TIP_WIDTH)
		def __del__(self):
			ToolTip.__del__(self)

		def SetPetSkill(self, pet_id, slot, index):

			if 0 == pet_id:
				return
			
			self.ClearToolTip()
				
			( pet_skill_vnum, pet_skill_level, formula1, formula2, formula3, next_formula1, next_formula2, next_formula3, bonus_value ) = player.GetPetSkillByIndex( pet_id, slot )
			
			if 0 == pet_skill_vnum:
				return
			
			( pet_skill_name, pet_skill_desc, pet_skill_use_type , pet_skill_cool_time ) = skill.GetPetSkillInfo(pet_skill_vnum)			
			
			self.SetTitle(pet_skill_name)

			self.AppendDescription(pet_skill_desc, 30)

			self.AppendSpace(5)
			if bonus_value:
				self.AppendTextLine( (localeinfo.PET_TOOLTIP_SKILL_CUR_LEVEL % pet_skill_level) + " "+ localeinfo.PET_TOOLTIP_SKILL_BONUS_VALUE, self.NORMAL_COLOR)
			else:
				self.AppendTextLine( localeinfo.PET_TOOLTIP_SKILL_CUR_LEVEL % pet_skill_level, self.NORMAL_COLOR)

			if skill.PET_SKILL_USE_TYPE_PASSIVE == pet_skill_use_type:
				self.__AppendPassiveSkill(pet_skill_vnum, int(formula2), self.NORMAL_COLOR)
				
			elif skill.PET_SKILL_USE_TYPE_AUTO == pet_skill_use_type:
				self.__AppendAutoSkill(pet_skill_vnum, formula1, formula2, formula3, self.NORMAL_COLOR)
				self.__AppendCoolTime(pet_skill_cool_time, self.NORMAL_COLOR)
				
			nextSkillLevel	= pet_skill_level + 1
			maxSkillLevel	= player.PET_GROWTH_SKILL_LEVEL_MAX
			
			if nextSkillLevel <= maxSkillLevel:
				self.AppendHorizontalLine()
				self.__AppendNextLevel( nextSkillLevel, maxSkillLevel )

				if skill.PET_SKILL_USE_TYPE_PASSIVE == pet_skill_use_type:
					self.__AppendPassiveSkill(pet_skill_vnum, int(next_formula2), self.NEGATIVE_COLOR)
					
				elif skill.PET_SKILL_USE_TYPE_AUTO == pet_skill_use_type:
					self.__AppendAutoSkill(pet_skill_vnum, next_formula1, next_formula2, next_formula3, self.NEGATIVE_COLOR)
					self.__AppendCoolTime(pet_skill_cool_time, self.NEGATIVE_COLOR)
				
			self.ResizeToolTip()
			self.ShowToolTip()

		def __PassiveSkillExceptionDecsriptionValueChange(self, pet_skill_vnum, value):
			
			if chr.PET_SKILL_AFFECT_GOLD_DROP == pet_skill_vnum:
				if not hasattr(app, "GetPetSkillCurve"):
					value = value / 10.0
				
			return value	

		def __AppendPassiveSkill(self, pet_skill_vnum, value, color ):
			
			if 0 == pet_skill_vnum:
				return
				
			try:
				text = self.PET_SKILL_APPLY_DATA_DICT[pet_skill_vnum]
			except KeyError:
				print "except KeyError"
				return
				
			value = self.__PassiveSkillExceptionDecsriptionValueChange(pet_skill_vnum, value)
				
			self.AppendSpace(5)
			self.AppendTextLine( text(value), color)

		def __AppendAutoSkill(self, pet_skill_vnum, value1, value2, value3, color ):
			
			if 0 == pet_skill_vnum:
				return
				
			try:
				text = self.PET_SKILL_APPLY_DATA_DICT[pet_skill_vnum]
			except KeyError:
				print "except KeyError"
				return
				
			self.AppendSpace(5)
						
			if chr.PET_SKILL_AFFECT_INVINCIBILITY == pet_skill_vnum:
				value2 = value2 / 10.0
				if not hasattr(app, "GetPetSkillCurve"):
					value1 = value1 / 10.0
				
			if chr.PET_SKILL_FEATHER == pet_skill_vnum:
				value3 = value3 / 10.0
				textLine = self.AppendTextLine( text(value1, value3, value2, value2 * 2), color)
			else:
				textLine = self.AppendTextLine( text(value1, value2), color)

			(x, y) = textLine.GetLocalPosition()
			textLine.SetPosition(x, y)
			self.AppendSpace(5)

		def __AppendCoolTime(self, pet_skill_cool_time, color):
			self.AppendSpace(5)
			self.AutoAppendTextLine( localeinfo.PET_SKILL_TOOLTIP_COOLTIME % (pet_skill_cool_time), color)
			return
			
		def __AppendNextLevel(self, curLevel, maxLevel):
			self.AppendSpace(5)
			self.AutoAppendTextLine(localeinfo.PET_TOOLTIP_SKILL_NEXT_LEVEL % (curLevel, maxLevel) , self.NEGATIVE_COLOR)
