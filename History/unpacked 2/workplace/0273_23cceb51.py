# coding: latin_1
#
# Guild Name Dye colour picker (GUILD_CONTRACTS_DYE).
#
# A member with contract authority recolours the guild's ACTIVE name dye. The
# grid is the purchasable palette (MUST match c_aGuildDyeColor[] in
# srcs/client/UserInterface/PythonTextTail.cpp, index 1..10); the "Original"
# swatch (index 0) reverts to the guild's EARNED colour (prestige band, or the
# default nametag colour) while keeping the paid dye time. The preview line
# draws the guild name in the picked colour so it can be judged before Apply.
# Apply sends the colour index (0 = original) to the server
# (net.SendGuildDyeSetColorPacket); the server re-checks permission + active
# dye, persists, and re-broadcasts the guild name so every client recolours it.
#
# Engine gotcha: a widget with no live Python ref gets GC'd and renders blank,
# so every transient widget is retained on the instance (self.keepRefs).

import app
import ui
import grp
import net
import guild
import localeinfo


# purchasable palette (index 1..10) MUST stay in sync with c_aGuildDyeColor[] (PythonTextTail.cpp)
DYE_RGB = (
	(0xE0 / 255.0, 0x24 / 255.0, 0x5E / 255.0),
	(0xFF / 255.0, 0x8C / 255.0, 0x00 / 255.0),
	(0xFF / 255.0, 0xD2 / 255.0, 0x00 / 255.0),
	(0x7F / 255.0, 0xE8 / 255.0, 0x17 / 255.0),
	(0x10 / 255.0, 0xB9 / 255.0, 0x81 / 255.0),
	(0x14 / 255.0, 0xB8 / 255.0, 0xC4 / 255.0),
	(0x2E / 255.0, 0x7D / 255.0, 0xFF / 255.0),
	(0x7C / 255.0, 0x5C / 255.0, 0xFF / 255.0),
	(0xE2 / 255.0, 0x3A / 255.0, 0xC4 / 255.0),
	(1.0, 1.0, 1.0),
)

# earned/prestige colours (MUST match c_aGuildBandNameColor[] in PythonTextTail.cpp);
# index 0 = default nametag colour, 1..4 = prestige bands.
BAND_RGB = (
	(0xEF / 255.0, 0xD3 / 255.0, 0xFF / 255.0),
	(0xBE / 255.0, 0xA0 / 255.0, 0x6B / 255.0),
	(0xC2 / 255.0, 0x3E / 255.0, 0x2C / 255.0),
	(0x80 / 255.0, 0xD3 / 255.0, 0xF5 / 255.0),
	(0xCC / 255.0, 0x38 / 255.0, 0x29 / 255.0),
)


def _band(level):
	# mirror GetGuildPrestigeBand() (srcs/share/m2_length.hpp)
	if level >= 30:
		return 4
	if level >= 25:
		return 3
	if level >= 20:
		return 2
	if level >= 10:
		return 1
	return 0


WIDTH  = 262
PAD    = 14
SWATCH = 30
SEL    = 3
GAP    = 6
COLS   = 5
CELL   = SWATCH + SEL * 2

BORDER_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
SEL_COLOR    = grp.GenerateColor(0.96, 0.90, 0.40, 1.0)
PREVIEW_BG   = grp.GenerateColor(0.08, 0.08, 0.10, 1.0)


def _L(key, default):
	return getattr(localeinfo, key, default)


def _is_rtl():
	try:
		return localeinfo.IsARABIC()
	except Exception:
		return False


class _Swatch(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.index = 0
		self.event = None
		self.SetSize(CELL, CELL)

		self.ring = ui.Bar()
		self.ring.SetParent(self)
		self.ring.AddFlag("not_pick")
		self.ring.SetColor(SEL_COLOR)
		self.ring.SetSize(CELL, CELL)
		self.ring.SetPosition(0, 0)
		self.ring.Hide()

		self.border = ui.Bar()
		self.border.SetParent(self)
		self.border.AddFlag("not_pick")
		self.border.SetColor(BORDER_COLOR)
		self.border.SetSize(SWATCH + 2, SWATCH + 2)
		self.border.SetPosition(SEL - 1, SEL - 1)
		self.border.Show()

		self.fill = ui.Bar()
		self.fill.SetParent(self)
		self.fill.AddFlag("not_pick")
		self.fill.SetSize(SWATCH, SWATCH)
		self.fill.SetPosition(SEL, SEL)
		self.fill.Show()

	def __del__(self):
		ui.Window.__del__(self)

	def Set(self, index, rgb, event):
		self.index = index
		self.event = event
		self.fill.SetColor(grp.GenerateColor(rgb[0], rgb[1], rgb[2], 1.0))

	def SetSelected(self, on):
		if on:
			self.ring.Show()
		else:
			self.ring.Hide()

	# capture the click: without handling Down, the movable board grabs the
	# drag and Up never reaches the swatch (selection would never commit).
	def OnMouseLeftButtonDown(self):
		return True

	def OnMouseLeftButtonUp(self):
		if self.event:
			self.event(self.index)
		return True


class GuildDyeColorWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.AddFlag("movable")
		self.AddFlag("float")
		if getattr(app, "ENABLE_WINDOW_SLIDE_EFFECT", 0):
			self.AddFlag("animated_board")
		self.rtl = _is_rtl()
		self.keepRefs = []
		self.swatches = []
		self.origSwatch = None
		self.selected = 0
		self.preview = None
		self.board = None
		self.__Build()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __Build(self):
		rows = (len(DYE_RGB) + COLS - 1) / COLS
		step = CELL + GAP
		origY = 100
		gridY = origY + CELL + 12
		height = gridY + rows * step + 44

		board = ui.BoardWithTitleBar()
		board.SetParent(self)
		board.SetSize(WIDTH, height)
		board.SetTitleName(_L("GUILD_DYE_TITLE", "Guild Name Colour"))
		board.SetCloseEvent(ui.__mem_func__(self.Close))
		board.Show()
		self.board = board
		self.SetSize(WIDTH, height)

		pv = ui.Bar()
		pv.SetParent(self)
		pv.AddFlag("not_pick")
		pv.SetColor(PREVIEW_BG)
		pv.SetSize(WIDTH - PAD * 2, 34)
		pv.SetPosition(PAD, 40)
		pv.Show()
		self.keepRefs.append(pv)

		name = ui.TextLine()
		name.SetParent(self)
		name.AddFlag("not_pick")
		name.SetPosition(WIDTH / 2, 50)
		name.SetHorizontalAlignCenter()
		name.Show()
		self.preview = name
		self.keepRefs.append(name)

		hint = ui.TextLine()
		hint.SetParent(self)
		hint.AddFlag("not_pick")
		hint.SetPosition(WIDTH / 2, 82)
		hint.SetHorizontalAlignCenter()
		hint.SetFontColor(0.60, 0.63, 0.68)
		hint.SetText(_L("GUILD_DYE_HINT", "Pick a colour, then Apply"))
		hint.Show()
		self.keepRefs.append(hint)

		# "Original" swatch (index 0) — reverts to the guild's earned colour.
		orig = _Swatch()
		orig.SetParent(self)
		orig.SetPosition(PAD + 10, origY)
		orig.Set(0, BAND_RGB[0], self.__OnPickColor)
		orig.Show()
		self.origSwatch = orig

		origLabel = ui.TextLine()
		origLabel.SetParent(self)
		origLabel.AddFlag("not_pick")
		origLabel.SetPosition(PAD + 10 + CELL + 10, origY + CELL / 2 - 6)
		origLabel.SetHorizontalAlignLeft()
		origLabel.SetFontColor(0.82, 0.84, 0.88)
		origLabel.SetText(_L("GUILD_DYE_ORIGINAL", "Original (earned colour)"))
		origLabel.Show()
		self.keepRefs.append(origLabel)

		gridW = COLS * CELL + (COLS - 1) * GAP
		startX = (WIDTH - gridW) / 2
		for i in xrange(len(DYE_RGB)):
			sw = _Swatch()
			sw.SetParent(self)
			col = i % COLS
			row = i / COLS
			sw.SetPosition(startX + col * step, gridY + row * step)
			sw.Set(i + 1, DYE_RGB[i], self.__OnPickColor)
			sw.Show()
			self.swatches.append(sw)

		by = gridY + rows * step + 8
		self.applyButton = self.__Button(WIDTH / 2 - 95, by, _L("GUILD_DYE_APPLY", "Apply"), self.__OnApply)
		self.cancelButton = self.__Button(WIDTH / 2 + 5, by, getattr(localeinfo, "UI_CANCEL", "Cancel"), self.Close)

	def __Button(self, x, y, text, event):
		b = ui.Button()
		b.SetParent(self)
		b.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		b.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		b.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		b.SetText(text)
		b.SetPosition(int(x), int(y))
		b.SetEvent(ui.__mem_func__(event))
		b.Show()
		self.keepRefs.append(b)
		return b

	def __OrigRGB(self):
		lvl = 0
		try:
			lvl = guild.GetGuildLevel()
		except Exception:
			lvl = 0
		return BAND_RGB[_band(lvl)]

	def __OnPickColor(self, index):
		self.__Select(index)

	def __Select(self, index):
		if index < 0 or index > len(DYE_RGB):
			return
		self.selected = index
		if self.origSwatch:
			self.origSwatch.SetSelected(index == 0)
		for i in xrange(len(self.swatches)):
			self.swatches[i].SetSelected(i + 1 == index)
		rgb = self.__OrigRGB() if index == 0 else DYE_RGB[index - 1]
		if self.preview:
			self.preview.SetFontColor(rgb[0], rgb[1], rgb[2])

	def __RefreshPreviewName(self):
		nm = ""
		try:
			nm = guild.GetGuildName()
		except Exception:
			nm = ""
		if not nm:
			nm = _L("GUILD_DYE_SAMPLE", "Guild Name")
		if self.preview:
			self.preview.SetText(nm)

	def __OnApply(self):
		if not hasattr(net, "SendGuildDyeSetColorPacket"):
			self.Close()
			return
		net.SendGuildDyeSetColorPacket(self.selected)
		self.Close()

	def Open(self):
		if self.origSwatch:
			self.origSwatch.Set(0, self.__OrigRGB(), self.__OnPickColor)
		cur = 0
		try:
			cur = guild.GetGuildDyeColor()
		except Exception:
			cur = 0
		self.__RefreshPreviewName()
		if 1 <= cur <= len(DYE_RGB):
			self.__Select(cur)
		else:
			self.__Select(0)   # active-original (sentinel) or none -> Original
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
