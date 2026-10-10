# coding: latin_1
#
# PvM Class Balance dialogs (code-built + draggable, styled after uicasualconfirm):
#   PvmBalanceIntroDialog   - one-time intro on login (server pushes "PvmBalanceIntro")
#   PvmBalanceConfirmDialog - rich confirm gate before binding the passive to the
#                             first attack skill (opened from uicharacter)
#
# Engine gotcha (from uicasualconfirm): a widget with no live Python ref is GC'd
# and renders blank, so every transient widget is retained in self.keepRefs.

import app
import ui
import localeinfo


WIDTH  = 340
HEIGHT = 300
PAD    = 14
INNER  = PAD + 10
ICON_BOX = 40

# flat palette (RGB 0..1), matching uicasualconfirm's vocabulary
COL_HEAD = (0.93, 0.94, 0.97)   # headline
COL_TEXT = (0.62, 0.66, 0.72)   # neutral body
COL_GOLD = (0.96, 0.84, 0.45)   # the key concept (skill / linked)
COL_POS  = (0.36, 0.80, 0.56)   # gains
COL_WARN = (0.95, 0.74, 0.30)   # caution

ICON_IMAGE = "d:/ymir work/ui/passive/monster_passive.png"  # placeholder; swap to pvm_balance.png

# PvM Class Balance passive vnum. Hovering the dialog icon drives the shared
# SkillToolTip, which renders the SAME rich tooltip as the skill window
# (bound/unbound state, bonus A/B, PvP note) via SetPassiveAbilityToolTip.
PASSIVE_VNUM = 216


def _is_rtl():
	try:
		return localeinfo.IsARABIC()
	except Exception:
		return False


class _PvmDialogBase(ui.ScriptWindow):
	"""Shared chrome/helpers for the PvM dialogs: draggable board, framed icon,
	RTL-aware labels, framed sections, large buttons. Subclasses set self.w/self.h
	and call the builders from their own __Build()."""

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.AddFlag("movable")
		self.AddFlag("float")
		if getattr(app, "ENABLE_WINDOW_SLIDE_EFFECT", 0):
			self.AddFlag("animated_board")
		self.rtl = _is_rtl()
		self.keepRefs = []
		self.board = None
		self.icon = None
		self.skillToolTip = None   # shared uitooltip.SkillToolTip, set by the opener
		self.w = WIDTH
		self.h = HEIGHT

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def _Board(self, title):
		board = ui.BoardNewWithTitleBar()
		board.SetParent(self)
		board.SetSize(self.w, self.h)
		board.SetTitleName(title)
		board.SetCloseEvent(ui.__mem_func__(self.Close))
		board.Show()
		self.board = board
		self.SetSize(self.w, self.h)

	def _Label(self, x, y, text, color, align = "auto"):
		t = ui.TextLine()
		t.SetParent(self)
		if align == "center":
			t.SetPosition(x, y)
			t.SetHorizontalAlignCenter()
		elif self.rtl:
			t.SetPosition(self.w - x, y)
			t.SetHorizontalAlignLeft()
		else:
			t.SetPosition(x, y)
		if text:
			t.SetText(text)
		t.SetFontColor(*color)
		t.Show()
		self.keepRefs.append(t)
		return t

	def _Section(self, y, h):
		ow = ui.OutlineWindow()
		ow.SetParent(self)
		ow.MakeOutlineWindow(self.w - PAD * 2, h)
		ow.SetPosition(PAD, y)
		ow.AddFlag("not_pick")
		ow.Show()
		self.keepRefs.append(ow)
		return ow

	def _Icon(self, y):
		slot = ui.OutlineWindow()
		slot.SetParent(self)
		slot.MakeOutlineWindow(ICON_BOX, ICON_BOX)
		slot.SetPosition((self.w - ICON_BOX) / 2, y)
		slot.AddFlag("not_pick")
		slot.Show()
		self.keepRefs.append(slot)

		icon = ui.ImageBox()
		icon.SetParent(self)
		# NO not_pick -- the icon must be pickable so it receives mouse-over and
		# can drive the shared SkillToolTip (rich passive tooltip).
		icon.LoadImage(ICON_IMAGE)
		iw = icon.GetWidth() or 32
		ih = icon.GetHeight() or 32
		icon.SetPosition((self.w - iw) / 2, y + (ICON_BOX - ih) / 2)
		icon.SAFE_SetEvent(self.__OnIconOverIn, "mouse_over_in")
		icon.SAFE_SetEvent(self.__OnIconOverOut, "mouse_over_out")
		icon.Show()
		self.icon = icon
		self.keepRefs.append(icon)

	def _IconButton(self, prefix, tooltip, event):
		# accept/cancel icon buttons (acceptbutton / canclebutton 00/01/02.sub) -- tooltip
		# ONLY, no text on top. Caller positions via SetPosition() after GetWidth().
		b = ui.Button()
		b.SetParent(self)
		b.SetUpVisual("d:/ymir work/ui/public/%sbutton00.sub" % prefix)
		b.SetOverVisual("d:/ymir work/ui/public/%sbutton01.sub" % prefix)
		b.SetDownVisual("d:/ymir work/ui/public/%sbutton02.sub" % prefix)
		b.SetToolTipText(tooltip)
		b.SetEvent(event)
		b.Show()
		self.keepRefs.append(b)
		return b

	def SetSkillToolTip(self, toolTip):
		# Share the canonical SkillToolTip (owned by interfacemodule / character
		# window). Hovering the icon then renders the EXACT same rich passive
		# tooltip as the skill window -- single source of truth, no duplication.
		self.skillToolTip = toolTip

	def __OnIconOverIn(self, *args):
		if self.skillToolTip:
			self.skillToolTip.SetPassiveAbilityToolTip(PASSIVE_VNUM)

	def __OnIconOverOut(self, *args):
		if self.skillToolTip:
			self.skillToolTip.HideToolTip()

	def Close(self):
		if self.skillToolTip:
			self.skillToolTip.HideToolTip()
		self.Hide()

	def Destroy(self):
		self.Close()
		self.keepRefs = []
		self.board = None

	def OnPressEscapeKey(self):
		self.Close()
		return True


class PvmBalanceIntroDialog(_PvmDialogBase):
	def __init__(self):
		_PvmDialogBase.__init__(self)
		self.__Build()

	def __Build(self):
		self._Board(localeinfo.PVM_BALANCE_POPUP_TITLE)
		self._Icon(40)
		self._Section(92, 152)
		cx = self.w / 2
		self._Label(cx, 104, localeinfo.PVM_BALANCE_POPUP_L0,   COL_HEAD, "center")
		self._Label(cx, 128, localeinfo.PVM_BALANCE_POPUP_L1,   COL_TEXT, "center")
		self._Label(cx, 146, localeinfo.PVM_BALANCE_POPUP_L2,   COL_GOLD, "center")
		self._Label(cx, 174, localeinfo.PVM_BALANCE_POPUP_L3,   COL_TEXT, "center")
		self._Label(cx, 192, localeinfo.PVM_BALANCE_POPUP_L4,   COL_TEXT, "center")
		self._Label(cx, 216, localeinfo.PVM_BALANCE_POPUP_WARN, COL_WARN, "center")
		ok = self._IconButton("accept", localeinfo.PVM_BALANCE_POPUP_OK, ui.__mem_func__(self.Close))
		bw = ok.GetWidth() or 32
		ok.SetPosition(144, 262)

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()


class PvmBalanceConfirmDialog(_PvmDialogBase):
	def __init__(self):
		_PvmDialogBase.__init__(self)
		self.acceptEvent = None
		self.skillNameLabel = None
		self.__Build()

	def __Build(self):
		self.w = 360
		self.h = 332
		self._Board(localeinfo.PVM_BALANCE_CONFIRM_TITLE)
		self._Icon(40)
		cx = self.w / 2
		self._Label(cx, 92, localeinfo.PVM_BALANCE_CONFIRM_PROMPT, COL_HEAD, "center")
		self.skillNameLabel = self._Label(cx, 112, "", COL_GOLD, "center")
		self._Section(144, 108)
		self._Label(cx, 152, localeinfo.PVM_BALANCE_CONFIRM_DESC, COL_TEXT, "center")
		self._Label(cx, 174, localeinfo.PVM_BALANCE_CONFIRM_G1,   COL_POS,  "center")
		self._Label(cx, 192, localeinfo.PVM_BALANCE_CONFIRM_G2,   COL_POS,  "center")
		self._Label(cx, 222, localeinfo.PVM_BALANCE_CONFIRM_PERM, COL_WARN, "center")
		ab = self._IconButton("accept", localeinfo.UI_ACCEPT, ui.__mem_func__(self.__OnAccept))
		cb = self._IconButton("cancle", localeinfo.UI_CANCEL, ui.__mem_func__(self.Close))
		bw = ab.GetWidth() or 32
		gap = 14
		by = self.h - bw - 14
		sx = (self.w - (bw * 2 + gap)) / 2
		ab.SetPosition(209, 280)
		cb.SetPosition(100, 280)

	def Open(self, skillName, acceptEvent):
		self.acceptEvent = acceptEvent
		if self.skillNameLabel:
			self.skillNameLabel.SetText(skillName)
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def __OnAccept(self):
		ev = self.acceptEvent
		self.Close()
		if ev:
			ev()
