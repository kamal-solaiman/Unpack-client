# coding: latin_1
#
# Casual Buff activation confirm dialog (ENABLE_CASUAL_BUFF) — "dashboard" rework.
#
# Goal: rich + instantly readable. Each benefit is an icon row; the boosted item
# SETS are shown in full (every vnum as a hoverable slot with the real item
# tooltip); the two daily numbers are gauge bars (the stones bar reddens as it
# nears the limit); plus limitations, the affected-character list, and the
# accept gate. The client never reads casual_buff.txt — the vnum sets arrive in
# the CASUAL_GC_INFO trailer (see CCasualBuffManager::SendInfoPacket).
#
# Engine gotcha baked in: a widget with no live Python ref gets GC'd and renders
# blank, so every transient widget is retained on the instance (self.keepRefs).

import app
import ui
import grp
import item
import localeinfo
import uitooltip


# --- geometry (tune here) --------------------------------------------------
WIDTH        = 384
HEIGHT       = 548
PAD          = 14                 # board edge -> section edge
INNER        = PAD + 10           # section edge -> content
ITEM_SLOT    = 38                 # boosted-item slot size
ITEM_STEP    = ITEM_SLOT + 4
MAX_VIS_SLOTS= 3                  # a set bigger than this cycles through these slots
CYCLE_SECONDS= 1.2

# TODAY stat-cards (icon + big number + plain sentence). Replaced the two
# look-alike gauges that pointed in opposite directions and confused new
# players: now each card states, in player-positive "remaining" terms, exactly
# what the number means.
CARD_ICON    = 36                 # stat-card icon size
CARD_NUM_W   = 66                 # big-number block width
CARD_GAP     = 10                 # gap between card columns

GAUGE_H      = 13
GAUGE_LABEL_W= 96                 # label block beside the bar
GAUGE_VALUE_W= 62                 # value block on the other side of the bar

# --- flat palette ----------------------------------------------------------
COL_HEAD = (0.93, 0.94, 0.97)     # section headers
COL_TEXT = (0.62, 0.66, 0.72)     # neutral body
COL_POS  = (0.36, 0.80, 0.56)     # gains / positive
COL_NEG  = (0.88, 0.46, 0.42)     # limitations
COL_VAL  = (0.96, 0.84, 0.45)     # benefit values (soft gold)

GAUGE_BG    = grp.GenerateColor(0.10, 0.10, 0.12, 1.0)
FILL_GREEN  = grp.GenerateColor(0.36, 0.80, 0.56, 1.0)
FILL_AMBER  = grp.GenerateColor(0.92, 0.70, 0.30, 1.0)
FILL_RED    = grp.GenerateColor(0.88, 0.34, 0.32, 1.0)

CHECK_IMAGE = "d:/ymir work/ui/public/check_image.sub"


def _is_rtl():
	try:
		return localeinfo.IsARABIC()
	except Exception:
		return False


def _big_font():
	# big stat number; keep the locale's font family (so Arabic digits shape
	# correctly) but bump the size — pattern from ingamewikiui font handling
	try:
		return localeinfo.UI_DEF_FONT.split(":")[0] + ":22"
	except Exception:
		return "Tahoma:22"


# ---------------------------------------------------------------------------
# flat scrollbar (ported from ingamewikiui.WikiScrollBar; ui+grp only, so we
# don't pull the whole wiki module in). The stock ui.ThinScrollBar is broken
# (its MiddleBar has no 'bottom' image -> SetSize crashes).
# ---------------------------------------------------------------------------
class _FlatScrollBar(ui.Window):
	BASE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
	LINE_COLOR = grp.GenerateColor(0.34, 0.34, 0.34, 1.0)
	BAR_NUMB   = 9

	class MiddleBar(ui.DragButton):
		MIDDLE_COLOR = grp.GenerateColor(0.55, 0.58, 0.63, 1.0)

		def __init__(self):
			ui.DragButton.__init__(self)
			self.AddFlag("movable")
			self.middle = ui.Bar()
			self.middle.SetParent(self)
			self.middle.AddFlag("attach")
			self.middle.AddFlag("not_pick")
			self.middle.SetColor(self.MIDDLE_COLOR)
			self.middle.SetSize(1, 1)
			self.middle.Show()

		def SetStaticWidth(self, w):
			w = max(2, w)
			ui.DragButton.SetSize(self, w, self.middle.GetHeight())
			self.middle.SetSize(w, self.middle.GetHeight())

		def SetThumbHeight(self, h):
			h = max(12, int(h))
			w = self.middle.GetWidth()
			ui.DragButton.SetSize(self, w, h)
			self.middle.SetSize(w, h)

	def __init__(self):
		ui.Window.__init__(self)
		self.scrollEvent = None
		self.bars = []
		for i in xrange(self.BAR_NUMB):
			br = ui.Bar()
			br.SetParent(self)
			br.AddFlag("attach")
			br.AddFlag("not_pick")
			br.SetColor(self.BASE_COLOR if i == self.BAR_NUMB - 1 else self.LINE_COLOR)
			if i % 2 != 0:
				br.SetSize(1, 1)
			br.Show()
			self.bars.append(br)

		self.middleBar = self.MiddleBar()
		self.middleBar.SetParent(self)
		self.middleBar.SetMoveEvent(ui.__mem_func__(self.__OnMove))
		self.middleBar.Show()

	def SetScrollEvent(self, func):
		self.scrollEvent = ui.__mem_func__(func)

	def __OnMove(self):
		if not self.scrollEvent:
			return
		denom = float(self.GetHeight() - 2 - self.middleBar.GetHeight())
		if denom <= 0:
			return
		arg = float(self.middleBar.GetLocalPosition()[1] - 1) / denom
		self.scrollEvent(min(1.0, max(0.0, arg)))

	def OnMouseLeftButtonDown(self):
		(mx, my) = self.GetMouseLocalPosition()
		if mx == 0 or mx == self.GetWidth():
			return
		self.middleBar.SetPosition(1, my - self.middleBar.GetHeight() / 2)
		self.__OnMove()

	def OnRunMouseWheel(self, length):
		if not self.IsInPosition():
			return False
		val = min(max(1, self.middleBar.GetLocalPosition()[1] - (length * 0.01) * 16),
				  self.GetHeight() - self.middleBar.GetHeight() - 1)
		self.middleBar.SetPosition(1, val)
		self.__OnMove()
		return True

	def SetSize(self, w, h):
		(width, height) = (max(3, w), max(3, h))
		ui.Window.SetSize(self, width, height)
		self.bars[0].SetSize(1, height - 2);         self.bars[0].SetPosition(0, 1)
		self.bars[2].SetSize(width - 2, 1);          self.bars[2].SetPosition(1, 0)
		self.bars[4].SetSize(1, height - 2);         self.bars[4].SetPosition(width - 1, 1)
		self.bars[6].SetSize(width - 2, 1);          self.bars[6].SetPosition(1, height - 1)
		self.bars[8].SetSize(width - 2, height - 2); self.bars[8].SetPosition(1, 1)
		self.bars[1].SetPosition(0, 0)
		self.bars[3].SetPosition(width - 1, 0)
		self.bars[5].SetPosition(width - 1, height - 1)
		self.bars[7].SetPosition(0, height - 1)
		self.middleBar.SetStaticWidth(width - 2)
		self.middleBar.SetRestrictMovementArea(1, 1, width - 2, height - 2)

	def SetThumbScale(self, frac):
		track = self.GetHeight() - 2
		self.middleBar.SetThumbHeight(track * min(1.0, max(0.06, frac)))

	def SetPosScale(self, frac):
		denom = self.GetHeight() - 2 - self.middleBar.GetHeight()
		self.middleBar.SetPosition(1, int(round(denom * min(1.0, max(0.0, frac)))) + 1)


# ---------------------------------------------------------------------------
# pickable icon image -> raises the item tooltip on hover (its owner exposes
# hoverEvent / outEvent / GetCurrentVnum)
# ---------------------------------------------------------------------------
class _HoverIcon(ui.ImageBox):
	def __init__(self):
		ui.ImageBox.__init__(self)
		self.owner = None

	def __del__(self):
		ui.ImageBox.__del__(self)

	def OnMouseOverIn(self):
		if self.owner and self.owner.hoverEvent:
			self.owner.hoverEvent(self.owner.GetCurrentVnum())

	def OnMouseOverOut(self):
		if self.owner and self.owner.outEvent:
			self.owner.outEvent()


class _ItemSlot(ui.Window):
	"""A single framed item icon (OutlineWindow slot + centred hoverable icon)."""

	def __init__(self, size):
		ui.Window.__init__(self)
		self.size = size
		self.vnum = 0
		self.hoverEvent = None
		self.outEvent = None
		self.SetSize(size, size)

		slot = ui.OutlineWindow()
		slot.SetParent(self)
		slot.MakeOutlineWindow(size, size)
		slot.SetPosition(0, 0)
		slot.AddFlag("not_pick")
		slot.Show()
		self.slot = slot

		icon = _HoverIcon()
		icon.SetParent(self)
		icon.owner = self
		icon.Show()
		self.icon = icon

	def GetCurrentVnum(self):
		return self.vnum

	def SetItem(self, vnum, hoverEvent, outEvent):
		self.vnum = vnum
		self.hoverEvent = hoverEvent
		self.outEvent = outEvent
		item.SelectItem(vnum)
		path = item.GetIconImageFileName()
		if not path:
			self.icon.Hide()
			return
		self.icon.LoadImage(path)
		iw = self.icon.GetWidth() or 32
		ih = self.icon.GetHeight() or 32
		self.icon.SetPosition((self.size - iw) / 2, (self.size - ih) / 2)
		self.icon.Show()


class _Gauge(ui.Window):
	"""Flat progress bar: dark track + coloured fill. The 'cur / max' text is a
	separate label placed beside the bar by the dialog (keeps it off the fill)."""

	def __init__(self, w):
		ui.Window.__init__(self)
		self.w = w
		self.SetSize(w, GAUGE_H)

		bg = ui.Bar()
		bg.SetParent(self)
		bg.AddFlag("attach")
		bg.AddFlag("not_pick")
		bg.SetColor(GAUGE_BG)
		bg.SetSize(w, GAUGE_H)
		bg.SetPosition(0, 0)
		bg.Show()
		self.bg = bg

		fill = ui.Bar()
		fill.SetParent(self)
		fill.AddFlag("attach")
		fill.AddFlag("not_pick")
		fill.SetColor(FILL_GREEN)
		fill.SetSize(1, GAUGE_H)
		fill.SetPosition(0, 0)
		fill.Show()
		self.fill = fill

	def SetFrac(self, frac, color):
		frac = min(1.0, max(0.0, frac))
		self.fill.SetColor(color)
		self.fill.SetSize(max(1, int(self.w * frac)), GAUGE_H)


class CasualConfirmDialog(ui.ScriptWindow):
	CHAR_VIEW = 3

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.AddFlag("movable")
		self.AddFlag("float")
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.rtl = _is_rtl()
		self.activateEvent = None
		self.checkBox = None
		self.acceptButton = None
		# TODAY stat-cards: icon + big number per card (see __StatCard)
		self.stoneCardNum = None
		self.stoneCardIcon = None
		self.chaosCardNum = None
		self.chaosCardIcon = None
		self.charLines = []
		self.charScrollBar = None
		self.charBasePos = 0
		self.charList = []
		self.itemToolTip = None
		self.acceptEnabled = False
		self.keepRefs = []
		# a row whose set is larger than MAX_VIS_SLOTS shows that many slots and
		# cycles a sliding window of vnums through them (advanced from OnUpdate)
		self.shardCycle = {"vnums": [], "slots": [], "offset": 0, "cycle": False}
		self.chaosCycle = {"vnums": [], "slots": [], "offset": 0, "cycle": False}
		self.cycleNext = 0.0
		self.__Build()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	# -- builders -----------------------------------------------------------
	def __Label(self, x, y, text, color, align = "auto"):
		t = ui.TextLine()
		t.SetParent(self)
		if align == "center":
			t.SetPosition(x, y)
			t.SetHorizontalAlignCenter()
		elif self.rtl:
			t.SetPosition(WIDTH - x, y)
			t.SetHorizontalAlignLeft()
		else:
			t.SetPosition(x, y)
		if text:
			t.SetText(text)
		t.SetFontColor(*color)
		t.Show()
		self.keepRefs.append(t)
		return t

	def __Section(self, y, h):
		ow = ui.OutlineWindow()
		ow.SetParent(self)
		ow.MakeOutlineWindow(WIDTH - PAD * 2, h)
		ow.SetPosition(PAD, y)
		ow.Show()
		self.keepRefs.append(ow)
		return ow

	def __Check(self, x, y):
		img = ui.ImageBox()
		img.SetParent(self)
		img.AddFlag("not_pick")
		img.LoadImage(CHECK_IMAGE)
		img.SetPosition(x, y)
		img.Show()
		self.keepRefs.append(img)
		return img

	def __BenefitRow(self, y, labelText):
		"""check glyph + label, one line."""
		gW = 12
		if self.rtl:
			self.__Check(WIDTH - INNER - gW, y + 2)
		else:
			self.__Check(INNER, y + 2)
		self.__Label(INNER + gW + 6, y, labelText, COL_TEXT)

	def __ItemRowHeader(self, y, labelText):
		"""check glyph + label for an item-benefit row (slots added separately so
		the header isn't recreated when the slot count is known)."""
		gW = 12
		if self.rtl:
			self.__Check(WIDTH - INNER - gW, y + 11)
		else:
			self.__Check(INNER, y + 11)
		self.__Label(INNER + gW + 6, y + 9, labelText, COL_TEXT)

	def __ItemRow(self, y, count):
		"""`count` item slots on the side opposite the header label."""
		slots = []
		startX = INNER if self.rtl else (WIDTH - INNER - count * ITEM_STEP)
		for k in xrange(count):
			s = _ItemSlot(ITEM_SLOT)
			s.SetParent(self)
			s.SetPosition(startX + k * ITEM_STEP, y)
			s.Show()
			self.keepRefs.append(s)
			slots.append(s)
		return slots

	def __Build(self):
		board = ui.BoardWithTitleBar()
		board.SetParent(self)
		board.SetSize(WIDTH, HEIGHT)
		board.SetTitleName(localeinfo.CASUAL_CONFIRM_TITLE)
		board.SetCloseEvent(ui.__mem_func__(self.Close))
		board.Show()
		self.board = board
		self.SetSize(WIDTH, HEIGHT)

		# ---- BENEFITS ----
		self.__Section(38, 156)
		self.__Label(INNER, 46, localeinfo.CASUAL_CONFIRM_BENEFITS, COL_HEAD)
		self.__BenefitRow(68, localeinfo.CASUAL_CONFIRM_BENEFIT_CD)
		self.__BenefitRow(88, localeinfo.CASUAL_CONFIRM_BENEFIT_DAILY)
		# item-benefit headers; the slot rows themselves are built in Open() once
		# the actual vnum sets are known (counts come from the server)
		self.shardRowY = 110
		self.chaosRowY = 154
		self.__ItemRowHeader(self.shardRowY, localeinfo.CASUAL_CONFIRM_SHARD_TITLE)
		self.__ItemRowHeader(self.chaosRowY, localeinfo.CASUAL_CONFIRM_CHAOS_TITLE)

		# ---- TODAY (plain-language stat cards) ----
		self.__Section(202, 124)
		self.__Label(INNER, 210, localeinfo.CASUAL_CONFIRM_TODAY, COL_HEAD)
		# two self-explanatory cards instead of two look-alike gauges: each is
		# icon + big number + a one-sentence "what this means" caption.
		self.stoneCardIcon, self.stoneCardNum = self.__StatCard(
			232, localeinfo.CASUAL_CONFIRM_CARD_STONES_1, localeinfo.CASUAL_CONFIRM_CARD_STONES_2)
		self.__CardDivider(276)
		self.chaosCardIcon, self.chaosCardNum = self.__StatCard(
			284, localeinfo.CASUAL_CONFIRM_CARD_CHAOS_1, localeinfo.CASUAL_CONFIRM_CARD_CHAOS_2)

		# ---- LIMITATIONS ----
		self.__Section(334, 56)
		self.__Label(INNER, 340, localeinfo.CASUAL_CONFIRM_LIMITS, COL_HEAD)
		self.__Label(INNER, 358, localeinfo.CASUAL_CONFIRM_LIMIT_STONES, COL_NEG)
		self.__Label(INNER, 372, localeinfo.CASUAL_CONFIRM_LIMIT_MIDNIGHT, COL_NEG)

		# ---- AFFECTED CHARACTERS ----
		self.__Label(INNER, 398, localeinfo.CASUAL_CONFIRM_AFFECTED, COL_HEAD)
		self.__BuildCharList(416)

		# ---- accept + buttons ----
		self.checkBox = ui.CheckBoxNew(self, PAD + 10, 480,
			ui.__mem_func__(self.__OnToggleCheck))
		cbW = self.checkBox.GetWidth()
		if self.rtl:
			self.checkBox.SetPosition(WIDTH - PAD - 10 - cbW, 480)
		self.checkBox.Show()
		self.__Label(PAD + 10 + cbW + 6, 482, localeinfo.CASUAL_CONFIRM_ACCEPT, COL_HEAD)

		self.acceptButton = self.__Button(WIDTH / 2 - 95, 510, localeinfo.UI_ACCEPT, self.__OnAccept, True)
		self.cancelButton = self.__Button(WIDTH / 2 + 5, 510, localeinfo.UI_CANCEL, self.__OnCancel, False)

		self.itemToolTip = uitooltip.ItemToolTip()
		self.itemToolTip.Hide()

	def __Button(self, x, y, text, event, isAccept):
		b = ui.Button()
		b.SetParent(self)
		b.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		b.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		b.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		if isAccept:
			b.SetDisableVisual("d:/ymir work/ui/public/large_button_03.sub")
		b.SetText(text)
		b.SetPosition(x, y)
		b.SetEvent(ui.__mem_func__(event))
		b.Show()
		self.keepRefs.append(b)
		return b

	def __StatCard(self, cardY, cap1, cap2):
		"""A self-explanatory stat row: framed item icon + a big number + a
		two-line plain-language caption ("what this number means"). Laid out as
		three columns (icon | number | caption), mirrored for RTL. The icon image
		and number text are filled in Open() once the server data is known."""
		iconY = cardY + 2
		numY  = cardY + 6
		cap1Y = cardY + 5
		cap2Y = cardY + 21

		if self.rtl:
			iconX = WIDTH - INNER - CARD_ICON
			numX  = iconX - CARD_GAP - CARD_NUM_W
		else:
			iconX = INNER
			numX  = INNER + CARD_ICON + CARD_GAP
		# caption logical-left inset (same value both directions; __Label mirrors)
		capLogX = INNER + CARD_ICON + CARD_GAP + CARD_NUM_W + CARD_GAP

		icon = ui.ImageBox()
		icon.SetParent(self)
		icon.AddFlag("not_pick")
		icon.SetPosition(iconX, iconY)
		icon.baseX = iconX
		icon.baseY = iconY
		icon.Show()
		self.keepRefs.append(icon)

		num = ui.TextLine()
		num.SetParent(self)
		num.SetFontName(_big_font())
		num.SetPosition(numX + CARD_NUM_W / 2, numY)
		num.SetHorizontalAlignCenter()
		num.SetFontColor(*COL_POS)
		num.Show()
		self.keepRefs.append(num)

		# two plain-language caption lines (__Label mirrors logical x for RTL)
		self.__Label(capLogX, cap1Y, cap1, COL_TEXT)
		self.__Label(capLogX, cap2Y, cap2, COL_HEAD)
		return icon, num

	def __CardDivider(self, y):
		bar = ui.Bar()
		bar.SetParent(self)
		bar.AddFlag("attach")
		bar.AddFlag("not_pick")
		bar.SetColor(grp.GenerateColor(0.28, 0.29, 0.32, 1.0))
		bar.SetSize(WIDTH - INNER * 2, 1)
		bar.SetPosition(INNER, y)
		bar.Show()
		self.keepRefs.append(bar)

	def __SetCardIcon(self, icon, vnum):
		if not icon:
			return
		if not vnum:
			icon.Hide()
			return
		item.SelectItem(vnum)
		path = item.GetIconImageFileName()
		if not path:
			icon.Hide()
			return
		icon.LoadImage(path)
		iw = icon.GetWidth() or 32
		ih = icon.GetHeight() or 32
		icon.SetPosition(icon.baseX + (CARD_ICON - iw) / 2, icon.baseY + (CARD_ICON - ih) / 2)
		icon.Show()

	# >>> SECTION BEGIN: replaced by __StatCard (gauge row builder kept for revival)
	# def __MakeGaugeRow(self, y, labelText):
	# 	"""label on one side, value on the other, the bar between them (so the
	# 	value never overlaps the fill). __Label auto-places the label on the
	# 	correct side (right for RTL); the value is centred in its own block."""
	# 	barW = (WIDTH - INNER * 2) - GAUGE_LABEL_W - GAUGE_VALUE_W - 12
	# 	g = _Gauge(barW)
	# 	g.SetParent(self)
	# 	cy = y + (16 - GAUGE_H) / 2
	# 	self.__Label(INNER, y, labelText, COL_TEXT)
	# 	if self.rtl:
	# 		barX = INNER + GAUGE_VALUE_W + 6
	# 		valCenterX = INNER + GAUGE_VALUE_W / 2
	# 	else:
	# 		barX = INNER + GAUGE_LABEL_W + 6
	# 		valCenterX = barX + barW + 6 + GAUGE_VALUE_W / 2
	# 	g.SetPosition(barX, cy)
	# 	g.Show()
	# 	self.keepRefs.append(g)
	# 	val = ui.TextLine()
	# 	val.SetParent(self)
	# 	val.SetPosition(valCenterX, y)
	# 	val.SetHorizontalAlignCenter()
	# 	val.SetFontColor(0.96, 0.96, 0.98)
	# 	val.Show()
	# 	self.keepRefs.append(val)
	# 	return g, val
	# <<< SECTION END

	def __BuildCharList(self, y):
		self.__Section(y, self.CHAR_VIEW * 16 + 8)
		self.charLines = []
		for i in xrange(self.CHAR_VIEW):
			t = ui.TextLine()
			t.SetParent(self)
			if self.rtl:
				t.SetPosition(WIDTH - INNER, y + 6 + i * 16)
				t.SetHorizontalAlignLeft()
			else:
				t.SetPosition(INNER, y + 6 + i * 16)
			t.SetFontColor(*COL_TEXT)
			t.Show()
			self.charLines.append(t)

		sb = _FlatScrollBar()
		sb.SetParent(self)
		if self.rtl:
			sb.SetPosition(PAD + 3, y + 4)
		else:
			sb.SetPosition(WIDTH - PAD - 10, y + 4)
		sb.SetSize(6, self.CHAR_VIEW * 16)
		sb.SetScrollEvent(self.__OnScrollChars)
		sb.Hide()
		self.charScrollBar = sb

	# -- open / data --------------------------------------------------------
	def Open(self, info, charList, shardVnums, chaosVnums, activateEvent):
		"""info = (active, chaosAllowed, stonesToday, stoneLimit, chaosLeft,
		          chaosMax, secsToMidnight)"""
		self.activateEvent = activateEvent
		self.charList = charList or []

		self.__FillItemRow("shardCycle", self.shardRowY, shardVnums or [])
		self.__FillItemRow("chaosCycle", self.chaosRowY, chaosVnums or [])

		(active, chaosAllowed, stonesToday, stoneLimit, chaosLeft, chaosMax, secs) = info

		# STONE card: stones you can STILL farm today (player-positive remaining,
		# not a count creeping toward a cap). Number reddens as you run out
		# (0 left = open-world stones drop nothing for the rest of the day).
		if stoneLimit > 0:
			remain = max(0, stoneLimit - stonesToday)
			frac = float(remain) / float(stoneLimit)
			numColor = COL_NEG if remain <= 0 else (COL_VAL if frac <= 0.30 else COL_POS)
			self.stoneCardNum.SetText("%d" % remain)
			self.stoneCardNum.SetFontColor(*numColor)
		else:
			self.stoneCardNum.SetText(localeinfo.CASUAL_CONFIRM_UNLIMITED)
			self.stoneCardNum.SetFontColor(*COL_POS)

		# CHAOS card: guaranteed drops you'll actually receive — the honest pool,
		# capped to the stones you have left today (so it never over-promises).
		previewPool = chaosMax
		if stoneLimit > 0:
			previewPool = min(chaosMax, max(0, stoneLimit - stonesToday))
		self.chaosCardNum.SetText("%d" % previewPool)
		self.chaosCardNum.SetFontColor(*(COL_POS if previewPool > 0 else COL_TEXT))

		# card icons (loaded from the trailer vnum sets — guaranteed to exist):
		# the stone card borrows the shard icon (the loot stones give), the chaos
		# card uses the first chaos vnum.
		self.__SetCardIcon(self.stoneCardIcon, (list(shardVnums or []) + [0])[0])
		self.__SetCardIcon(self.chaosCardIcon, (list(chaosVnums or []) + [0])[0])

		self.__RefreshCharList()
		self.checkBox.SetCheck(False)
		self.__SetAcceptEnabled(False)

		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def __FillItemRow(self, key, rowY, vnums):
		# (re)build the slot row: show up to MAX_VIS_SLOTS slots; if the set is
		# bigger, those slots cycle a sliding window of vnums (see __Advance)
		c = getattr(self, key)
		for s in c["slots"]:
			s.Hide()
			if s in self.keepRefs:
				self.keepRefs.remove(s)

		visible = min(len(vnums), MAX_VIS_SLOTS)
		slots = self.__ItemRow(rowY, visible)
		c["vnums"] = list(vnums)
		c["slots"] = slots
		c["offset"] = 0
		c["cycle"] = len(vnums) > MAX_VIS_SLOTS

		for i, s in enumerate(slots):
			if i < len(vnums):
				s.SetItem(vnums[i], self.__ShowIconTip, self.__HideIconTip)

		self.cycleNext = app.GetTime() + CYCLE_SECONDS

	def SetCharList(self, charList):
		self.charList = charList or []
		self.__RefreshCharList()

	def Close(self):
		self.__HideIconTip()
		self.Hide()

	def __RefreshCharList(self):
		n = len(self.charList)
		if n > self.CHAR_VIEW:
			self.charScrollBar.SetThumbScale(float(self.CHAR_VIEW) / float(n))
			self.charScrollBar.SetPosScale(0.0)
			self.charScrollBar.Show()
		else:
			self.charScrollBar.Hide()
		self.charBasePos = 0
		self.__RenderCharRows()

	def __RenderCharRows(self):
		n = len(self.charList)
		for i in xrange(self.CHAR_VIEW):
			idx = self.charBasePos + i
			if idx < n:
				(name, level) = self.charList[idx]
				self.charLines[i].SetText(localeinfo.CASUAL_CONFIRM_CHAR_ROW % (level, name))
			else:
				self.charLines[i].SetText("")

	def __OnScrollChars(self, frac):
		maxBase = max(0, len(self.charList) - self.CHAR_VIEW)
		self.charBasePos = int(round(frac * maxBase))
		self.__RenderCharRows()

	# -- events -------------------------------------------------------------
	def __OnToggleCheck(self):
		self.checkBox.SetCheck(not self.checkBox.GetCheck())
		self.__SetAcceptEnabled(self.checkBox.GetCheck())

	def __SetAcceptEnabled(self, enabled):
		self.acceptEnabled = enabled
		if enabled:
			self.acceptButton.Enable()
		else:
			self.acceptButton.Disable()

	def __OnAccept(self):
		if not self.acceptEnabled:
			return
		if self.activateEvent:
			self.activateEvent()
		self.Close()

	def __OnCancel(self):
		self.Close()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def __ShowIconTip(self, vnum):
		if vnum and self.itemToolTip:
			self.itemToolTip.SetItemToolTip(vnum)

	def __HideIconTip(self):
		if self.itemToolTip:
			self.itemToolTip.HideToolTip()

	def OnUpdate(self):
		if not (self.shardCycle["cycle"] or self.chaosCycle["cycle"]):
			return
		now = app.GetTime()
		if now < self.cycleNext:
			return
		self.cycleNext = now + CYCLE_SECONDS
		self.__Advance(self.shardCycle)
		self.__Advance(self.chaosCycle)

	def __Advance(self, c):
		if not c["cycle"]:
			return
		vnums = c["vnums"]
		slots = c["slots"]
		n = len(vnums)
		if n == 0 or not slots:
			return
		c["offset"] = (c["offset"] + 1) % n
		off = c["offset"]
		for i, s in enumerate(slots):
			s.SetItem(vnums[(off + i) % n], self.__ShowIconTip, self.__HideIconTip)
