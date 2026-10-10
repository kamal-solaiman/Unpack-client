# coding: latin_1

import app
import ui
import net
import chat
import player
import localeinfo
import uicommon
import uibadge
import uitooltip
import uipartyfinderhelp

IS_AR = localeinfo.IsARABIC()

def _MirrorX(x, w, parentW):
	return parentW - x - w

def _LayoutX(xLtr, w, parentW):
	if IS_AR:
		return _MirrorX(xLtr, w, parentW)
	return xLtr

WINDOW_WIDTH = 556
WINDOW_HEIGHT = 312

PF_ART = "d:/ymir work/ui/game/party_finder/"
PF_ART2 = "d:/ymir work/ui/game/new_fast_equip/"
IMG_HEADER   = PF_ART + "header.png"
IMG_LEFT_BG  = PF_ART + "left_bg.png"
IMG_RIGHT_BG = PF_ART + "right_bg.png"
IMG_CARD_BG  = PF_ART + "party_big_bg.png"
IMG_REQ_BG   = PF_ART + "requesters_bg.png"
IMG_NOTE_BG  = PF_ART + "notes_bg.png"

BTN_ACT_UP   = PF_ART + "btn_activ_norm.png"
BTN_ACT_OVER = PF_ART + "btn_activ_hover.png"
BTN_ACT_DOWN = PF_ART + "btn_activ_select.png"

CLOSE_UP   = PF_ART + "btn_activ_norm.png"
CLOSE_OVER = PF_ART + "btn_activ_hover.png"
CLOSE_DOWN = PF_ART + "btn_activ_select.png"

BTN_UP   = PF_ART + "btn_activ_norm.png"
BTN_OVER = PF_ART + "btn_activ_hover.png"
BTN_DOWN = PF_ART + "btn_activ_select.png"

LARGE_BTN_UP   = PF_ART2 + "btn_norm.png"
LARGE_BTN_OVER = PF_ART2 + "btn_norm_hover.png"
LARGE_BTN_DOWN = PF_ART2 + "btn_norm_select.png"

SMALL_BTN_UP   = PF_ART + "btn_activ_norm.png"
SMALL_BTN_OVER = PF_ART + "btn_activ_hover.png"
SMALL_BTN_DOWN = PF_ART + "btn_activ_select.png"

# --- window frame ---
HEADER_X = 4
HEADER_Y = 28
HEADER_W = 548
HEADER_H = 30

BODY_Y = 58
BODY_H = 250

# --- left column: management (top) over requests (bottom) ---
LEFT_X = 3
LEFT_W = 205
LEFT_PAD = 10
LEFT_INNER_X = LEFT_X + LEFT_PAD
LEFT_INNER_W = 186

MG_TITLE_Y = BODY_Y + 7
MG_CONTENT_Y = BODY_Y + 30
REQ_TITLE_Y = BODY_Y + 130
REQ_CONTENT_Y = BODY_Y + 147
REQ_CONTENT_H = 100

NOTE_W = 186
NOTE_H = 21

ACT_BTN_W = 83
ACT_BTN_H = 23

# --- right column: browse list ---
RIGHT_X = LEFT_X + LEFT_W
RIGHT_W = 345
LIST_X = RIGHT_X + 9
LIST_Y = BODY_Y + 8
LIST_W = 326
LIST_H = 234
SCROLL_X = LIST_X + LIST_W + 2

EMPTY_BTN_W = 120
EMPTY_BTN_H = 24

# --- filter bar (on the header) ---
FILTER_Y = HEADER_Y + 5

PF_EXPIRE_SEC_CLIENT = 20 * 60
PF_PENDING_TTL_CLIENT = 5 * 60
PF_DECLINE_LOCK_CLIENT = 180
PF_MAX_LEVEL = 105

_PF_CATS = (
	(app.PF_CAT_DUNGEON, "PF_CAT_DUNGEON"),
	(app.PF_CAT_LEVELING, "PF_CAT_LEVELING"),
	(app.PF_CAT_OTHER, "PF_CAT_OTHER"),
)
_PF_CAT_ENGLISH_FALLBACK = ("Dungeon", "Leveling", "Other")

_PF_CAT_LABELS = dict((value, getattr(localeinfo, key, _PF_CAT_ENGLISH_FALLBACK[i]))
	for i, (value, key) in enumerate(_PF_CATS))

_PF_FILTER_ALL = -1

_PF_SORT_NEWEST = 0
_PF_SORT_SLOTS = 1
_PF_SORT_LEVEL = 2

_PF_SORTS = (
	(_PF_SORT_NEWEST, "PF_SORT_NEWEST"),
	(_PF_SORT_SLOTS, "PF_SORT_SLOTS"),
	(_PF_SORT_LEVEL, "PF_SORT_LEVEL"),
)
_PF_SORT_ENGLISH_FALLBACK = ("Newest", "Most open slots", "Level")
_PF_SORT_LABELS = dict((value, getattr(localeinfo, key, _PF_SORT_ENGLISH_FALLBACK[i]))
	for i, (value, key) in enumerate(_PF_SORTS))

# EPartyFinderJoinResult (m2_length.hpp); value 8 is not registered in `app`, keyed by raw int.
_PF_JOIN_REQUEST_EXPIRED = 8

_PF_RESULT_MAP = {
	app.PF_JOIN_OK             : ("PF_RESULT_OK", "Joined %s's party."),
	app.PF_JOIN_DECLINED       : ("PF_RESULT_DECLINED", "%s declined your request."),
	app.PF_JOIN_PARTY_FULL     : ("PF_RESULT_FULL", "%s's party is full."),
	app.PF_JOIN_LISTING_EXPIRED: ("PF_RESULT_EXPIRED", "That listing has expired."),
	app.PF_JOIN_DIFF_EMPIRE    : ("PF_RESULT_EMPIRE", "You cannot join a party from another empire."),
	app.PF_JOIN_LEVEL_BOUNDARY : ("PF_RESULT_LEVEL", "Your level does not match that party's range."),
	app.PF_JOIN_IN_DUNGEON     : ("PF_RESULT_DUNGEON", "%s's party is inside a dungeon."),
	app.PF_JOIN_UNAVAILABLE    : ("PF_RESULT_UNAVAILABLE", "That party is no longer available."),
	_PF_JOIN_REQUEST_EXPIRED   : ("PF_RESULT_REQUEST_EXPIRED", "Your join request expired."),
}

def _CatLabel(value):
	return _PF_CAT_LABELS.get(value, str(value))

def _Trunc(text, n):
	if len(text) > n:
		return text[:n] + ".."
	return text

MESSENGER_PATH = "d:/ymir work/ui/game/messenger/"

# bJob raw race (MAIN_RACE 0-8) -> class+gender portrait. 8 = wolfman, hidden.
PORTRAIT_IMG = {
	0: MESSENGER_PATH + "war_m.png",
	1: MESSENGER_PATH + "ninja_w.png",
	2: MESSENGER_PATH + "sura_m.png",
	3: MESSENGER_PATH + "sham_w.png",
	4: MESSENGER_PATH + "war_f.png",
	5: MESSENGER_PATH + "ninja_m.png",
	6: MESSENGER_PATH + "sura_w.png",
	7: MESSENGER_PATH + "sham_m.png",
}

WINDOWS_PATH = "d:/ymir work/ui/game/windows/"
ICON_ACCEPT = WINDOWS_PATH + "community_icon_request_accept_default.sub"
ICON_ACCEPT_OVER = WINDOWS_PATH + "community_icon_request_accept_mouse_over.sub"
ICON_ACCEPT_CLICK = WINDOWS_PATH + "community_icon_request_accept_click.sub"
ICON_DECLINE = WINDOWS_PATH + "community_icon_x_default.sub"
ICON_DECLINE_OVER = WINDOWS_PATH + "community_icon_x_mouse_over.sub"
ICON_DECLINE_CLICK = WINDOWS_PATH + "community_icon_x_click.sub"

_PF_CAT_COLORS = {
	app.PF_CAT_DUNGEON : 0xFF4A90D9,
	app.PF_CAT_GRIND   : 0xFF6FCF6F,
	app.PF_CAT_METIN   : 0xFFCF6F4A,
	app.PF_CAT_BOSS    : 0xFFE6B450,
	app.PF_CAT_LEVELING: 0xFF9B6FCF,
	app.PF_CAT_QUEST   : 0xFF5FCFCF,
	app.PF_CAT_OTHER   : 0xFFAAAAAA,
}

_PF_NAME_COLOR = 0xFFFFFFFF
_PF_NAME_OWN_COLOR = 0xFFFFD700
_PF_NOTE_COLOR = 0xFFAAAAAA
_PF_AGE_COLOR = 0xFF888888
_PF_RIBBON_FIT_COLOR = 0xFF6FCF6F
_PF_RIBBON_UNFIT_COLOR = 0xFF808080
_PF_PIP_FILLED_COLOR = 0xFFE0A030
_PF_PIP_OPEN_COLOR = 0xFF404040
_PF_CARD_BG_IDLE = 0x18FFFFFF
_PF_CARD_BG_HOVER = 0x40FFFFFF

CARD_W = 326
CARD_H = 51
CARD_PORTRAIT_W = 29
CARD_PORTRAIT_X = 5
CARD_PORTRAIT_Y = (CARD_H - CARD_PORTRAIT_W) / 2
CARD_TEXT_X = CARD_PORTRAIT_X + CARD_PORTRAIT_W + 6
CARD_TEXT_W = 5
CARD_NAME_Y = 6
CARD_NOTE_Y = 26
CARD_META_X = 115
CARD_META_W = 60
CARD_CHIP_Y = 6
CARD_RIBBON_Y = 24
CARD_PIP_COUNT = 8
CARD_PIP_SIZE = 6
CARD_PIP_GAP = 1
CARD_PIPS_W = CARD_PIP_COUNT * CARD_PIP_SIZE + (CARD_PIP_COUNT - 1) * CARD_PIP_GAP
CARD_PIP_Y = 40
CARD_BTN_W = ACT_BTN_W
CARD_BTN_H = ACT_BTN_H
CARD_BTN_MARGIN = 5
CARD_BTN_X = CARD_W - CARD_BTN_W - CARD_BTN_MARGIN
CARD_BTN_Y = (CARD_H - CARD_BTN_H) / 2
CARD_BTN_TOP_Y = 3
CARD_BTN_BOT_Y = CARD_H - CARD_BTN_H - 3

REQROW_W = 169
REQROW_H = 32
REQROW_GAP = 3
REQROW_X = (LEFT_INNER_W - REQROW_W) / 2
REQROW_PORTRAIT_X = 3
REQROW_PORTRAIT_Y = 3
REQROW_PORTRAIT_W = 26
REQROW_TEXT_X = REQROW_PORTRAIT_X + REQROW_PORTRAIT_W + 4
REQROW_TEXT_Y = 3
REQROW_BAR_Y = 22
REQROW_BAR_H = 3
REQROW_BTN_W = 22
REQROW_BTN_GAP = 3
REQROW_BTN_MARGIN = 3
REQROW_BTN_Y = 5
REQROW_BTN_BLOCK_W = REQROW_BTN_W * 2 + REQROW_BTN_GAP
REQROW_TEXT_W = REQROW_W - REQROW_TEXT_X - REQROW_BTN_BLOCK_W - REQROW_BTN_GAP - REQROW_BTN_MARGIN

class ListingCard(ui.Window):
	def __init__(self, owner, data, serverNow, myLv, ownName, requestState, onRequestSent, onEditOwn, onDeleteOwn):
		ui.Window.__init__(self)
		self.owner = owner
		self.data = data
		self.leaderPid = data[0]
		self.isOwn = False
		self.state = None
		self.onRequestSent = onRequestSent
		self.onEditOwn = onEditOwn
		self.onDeleteOwn = onDeleteOwn

		self.SetSize(CARD_W, CARD_H)

		portraitX = _LayoutX(CARD_PORTRAIT_X, CARD_PORTRAIT_W, CARD_W)
		textX = _LayoutX(CARD_TEXT_X, CARD_TEXT_W, CARD_W)
		metaX = _LayoutX(CARD_META_X, CARD_META_W, CARD_W)
		pipsX = _LayoutX(CARD_META_X, CARD_PIPS_W, CARD_W)
		btnX = _LayoutX(CARD_BTN_X, CARD_BTN_W, CARD_W)

		self.bg = ui.ImageBox()
		self.bg.SetParent(self)
		self.bg.AddFlag("not_pick")
		self.bg.SetPosition(0, 0)
		self.bg.LoadImage(IMG_CARD_BG)
		self.bg.Show()

		self.hoverBar = ui.Bar()
		self.hoverBar.SetParent(self)
		self.hoverBar.AddFlag("not_pick")
		self.hoverBar.SetPosition(0, 0)
		self.hoverBar.SetSize(int(CARD_W), int(CARD_H))
		self.hoverBar.SetColor(_PF_CARD_BG_IDLE)
		self.hoverBar.Show()

		self.portrait = ui.ImageBox()
		self.portrait.SetParent(self)
		self.portrait.AddFlag("not_pick")
		self.portrait.SetPosition(int(portraitX), int(CARD_PORTRAIT_Y))
		self.portrait.Hide()

		self.nameLine = ui.TextLine()
		self.nameLine.SetParent(self)
		self.nameLine.AddFlag("not_pick")
		self.nameLine.SetPosition(int(textX), int(CARD_NAME_Y))
		if IS_AR:
			self.nameLine.SetHorizontalAlignLeft()
		self.nameLine.Show()

		self.noteLine = ui.TextLine()
		self.noteLine.SetParent(self)
		self.noteLine.AddFlag("not_pick")
		self.noteLine.SetPosition(int(textX), int(CARD_NOTE_Y))
		if IS_AR:
			self.noteLine.SetHorizontalAlignLeft()
		self.noteLine.SetPackedFontColor(_PF_NOTE_COLOR)
		self.noteLine.Show()

		self.chipLine = ui.TextLine()
		self.chipLine.SetParent(self)
		self.chipLine.AddFlag("not_pick")
		self.chipLine.SetPosition(int(metaX), int(CARD_CHIP_Y))
		if IS_AR:
			self.chipLine.SetHorizontalAlignLeft()
		self.chipLine.Show()

		self.ribbonLine = ui.TextLine()
		self.ribbonLine.SetParent(self)
		self.ribbonLine.AddFlag("not_pick")
		self.ribbonLine.SetPosition(int(metaX), int(CARD_RIBBON_Y))
		if IS_AR:
			self.ribbonLine.SetHorizontalAlignLeft()
		self.ribbonLine.Show()

		self.pips = []
		for i in range(CARD_PIP_COUNT):
			pip = ui.Bar()
			pip.SetParent(self)
			pip.AddFlag("not_pick")
			pip.SetSize(CARD_PIP_SIZE, CARD_PIP_SIZE)
			pip.SetPosition(int(pipsX + i * (CARD_PIP_SIZE + CARD_PIP_GAP)), int(CARD_PIP_Y))
			pip.SetColor(_PF_PIP_OPEN_COLOR)
			pip.Show()
			self.pips.append(pip)

		self.btnRequest = self.__MakeActButton(btnX, CARD_BTN_Y, getattr(localeinfo, "PF_REQUEST", "Request"), self.__OnRequest)

		stateLine = ui.TextLine()
		stateLine.SetParent(self)
		stateLine.AddFlag("not_pick")
		stateLine.SetPosition(int(btnX), int(CARD_BTN_Y + 4))
		if IS_AR:
			stateLine.SetHorizontalAlignLeft()
		stateLine.Hide()
		self.stateLine = stateLine

		self.btnEdit = self.__MakeActButton(btnX, CARD_BTN_TOP_Y, getattr(localeinfo, "PF_EDIT", "Edit"), self.__OnEdit)
		self.btnDelete = self.__MakeActButton(btnX, CARD_BTN_BOT_Y, getattr(localeinfo, "PF_DELETE", "Delete"), self.__OnDelete)
		self.btnEdit.Hide()
		self.btnDelete.Hide()

		self.SetOverInEvent(ui.__mem_func__(self.__OnOverIn))
		self.SetOverOutEvent(ui.__mem_func__(self.__OnOverOut))

		self.__Fill(data, serverNow, myLv, ownName, requestState)

	def __MakeActButton(self, x, y, text, handler):
		btn = ui.Button()
		btn.SetParent(self)
		btn.SetPosition(int(x), int(y))
		btn.SetUpVisual(BTN_ACT_UP)
		btn.SetOverVisual(BTN_ACT_OVER)
		btn.SetDownVisual(BTN_ACT_DOWN)
		btn.SetText(text)
		btn.SetEvent(ui.__mem_func__(handler))
		btn.Show()
		return btn

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.owner = None
		self.data = None
		self.bg = None
		self.hoverBar = None
		self.portrait = None
		self.nameLine = None
		self.noteLine = None
		self.ribbonLine = None
		self.chipLine = None
		self.pips = []
		self.btnRequest = None
		self.stateLine = None
		self.btnEdit = None
		self.btnDelete = None
		self.onRequestSent = None
		self.onEditOwn = None
		self.onDeleteOwn = None
		self.isOwn = False
		self.state = None

	def __Fill(self, data, serverNow, myLv, ownName, requestState):
		leaderPid, name, level, race, category, lvMin, lvMax, slotsOpen, note, postTime = data

		self.nameLine.SetText("%s - Lv%d" % (_Trunc(name, 14), level))
		self.nameLine.SetPackedFontColor(_PF_NAME_OWN_COLOR if name == ownName else _PF_NAME_COLOR)

		self.noteLine.SetText(_Trunc(note, 22))

		self.chipLine.SetText(_CatLabel(category))
		self.chipLine.SetPackedFontColor(_PF_CAT_COLORS.get(category, _PF_NAME_COLOR))

		if race in PORTRAIT_IMG:
			self.portrait.LoadImage(PORTRAIT_IMG[race])
			self.portrait.Show()
		else:
			self.portrait.Hide()

		filledCount = CARD_PIP_COUNT - slotsOpen
		for i, pip in enumerate(self.pips):
			pip.SetColor(_PF_PIP_FILLED_COLOR if i < filledCount else _PF_PIP_OPEN_COLOR)

		self.ribbonLine.SetText("Lv %d-%d" % (lvMin, lvMax))
		if lvMin <= myLv <= lvMax:
			self.ribbonLine.SetPackedFontColor(_PF_RIBBON_FIT_COLOR)
		else:
			self.ribbonLine.SetPackedFontColor(_PF_RIBBON_UNFIT_COLOR)

		self.isOwn = (name == ownName)
		if self.isOwn:
			self.state = None
			self.btnRequest.Hide()
			self.stateLine.Hide()
			self.btnEdit.Show()
			self.btnDelete.Show()
		else:
			self.btnEdit.Hide()
			self.btnDelete.Hide()
			stateInfo = requestState.get(leaderPid) if requestState else None
			if stateInfo:
				state, untilTime = stateInfo
				self.RefreshState(state, untilTime - app.GetTime())
			else:
				self.RefreshState(None, 0)

	def RefreshState(self, state, remaining):
		if self.isOwn:
			self.state = None
			self.btnRequest.Hide()
			self.stateLine.Hide()
			return
		if state == "SENT" and remaining <= 0:
			state = None
		self.state = state
		if state is None:
			self.btnRequest.Show()
			self.stateLine.Hide()
			return
		self.btnRequest.Hide()
		self.stateLine.Show()
		if state == "SENT":
			self.stateLine.SetText("%s %ds" % (getattr(localeinfo, "PF_SENT", "Sent"), int(remaining)))
		else:
			self.stateLine.SetText(getattr(localeinfo, "PF_LOCKED", "Locked"))

	def __OnRequest(self):
		if self.state in ("SENT", "LOCKED"):
			return
		net.SendPartyFinderJoinRequest(self.leaderPid)
		if self.onRequestSent:
			self.onRequestSent(self.leaderPid)

	def __OnEdit(self):
		if self.onEditOwn:
			self.onEditOwn(self.data)

	def __OnDelete(self):
		if self.onDeleteOwn:
			self.onDeleteOwn(self.leaderPid)

	def __OnOverIn(self):
		self.hoverBar.SetColor(_PF_CARD_BG_HOVER)

	def __OnOverOut(self):
		self.hoverBar.SetColor(_PF_CARD_BG_IDLE)

class RequestRow(ui.Window):
	def __init__(self, pid, name, level, race, expireAt):
		ui.Window.__init__(self)
		self.pid = pid
		self.reqName = name
		self.reqLevel = level
		self.answered = False
		self.expireAt = expireAt
		self.toolTip = None

		self.SetSize(REQROW_W, REQROW_H)

		portraitX = _LayoutX(REQROW_PORTRAIT_X, REQROW_PORTRAIT_W, REQROW_W)
		textX = _LayoutX(REQROW_TEXT_X, 0, REQROW_W)
		barX = _LayoutX(REQROW_TEXT_X, REQROW_TEXT_W, REQROW_W)
		acceptXLtr = REQROW_W - REQROW_BTN_MARGIN - REQROW_BTN_BLOCK_W
		if IS_AR:
			declineX = _MirrorX(acceptXLtr, REQROW_BTN_BLOCK_W, REQROW_W)
			acceptX = declineX + REQROW_BTN_W + REQROW_BTN_GAP
		else:
			acceptX = acceptXLtr
			declineX = acceptX + REQROW_BTN_W + REQROW_BTN_GAP

		self.bg = ui.ImageBox()
		self.bg.SetParent(self)
		self.bg.AddFlag("not_pick")
		self.bg.SetPosition(0, 0)
		self.bg.LoadImage(IMG_REQ_BG)
		self.bg.Show()

		self.portrait = ui.ImageBox()
		self.portrait.SetParent(self)
		self.portrait.AddFlag("not_pick")
		self.portrait.SetPosition(int(portraitX), int(REQROW_PORTRAIT_Y))
		if race in PORTRAIT_IMG:
			self.portrait.LoadImage(PORTRAIT_IMG[race])
			self.portrait.Show()
		else:
			self.portrait.Hide()

		self.nameLine = ui.TextLine()
		self.nameLine.SetParent(self)
		self.nameLine.AddFlag("not_pick")
		self.nameLine.SetPosition(int(textX), int(REQROW_TEXT_Y))
		if IS_AR:
			self.nameLine.SetHorizontalAlignLeft()
		self.nameLine.SetText("%s - Lv%d" % (_Trunc(name, 8), level))
		self.nameLine.Show()

		self.barBg = ui.Bar()
		self.barBg.SetParent(self)
		self.barBg.AddFlag("not_pick")
		self.barBg.SetPosition(int(barX), int(REQROW_BAR_Y))
		self.barBg.SetSize(int(REQROW_TEXT_W), REQROW_BAR_H)
		self.barBg.SetColor(_PF_PIP_OPEN_COLOR)
		self.barBg.Show()

		self.bar = ui.Bar()
		self.bar.SetParent(self)
		self.bar.AddFlag("not_pick")
		self.bar.SetPosition(int(barX), int(REQROW_BAR_Y))
		self.bar.SetSize(int(REQROW_TEXT_W), REQROW_BAR_H)
		self.bar.SetColor(_PF_PIP_FILLED_COLOR)
		self.bar.Show()

		self.btnAccept = ui.Button()
		self.btnAccept.SetParent(self)
		self.btnAccept.SetPosition(int(acceptX), int(REQROW_BTN_Y))
		self.btnAccept.SetUpVisual(ICON_ACCEPT)
		self.btnAccept.SetOverVisual(ICON_ACCEPT_OVER)
		self.btnAccept.SetDownVisual(ICON_ACCEPT_CLICK)
		self.btnAccept.SetEvent(ui.__mem_func__(self.__OnAccept))
		self.btnAccept.Show()

		self.btnDecline = ui.Button()
		self.btnDecline.SetParent(self)
		self.btnDecline.SetPosition(int(declineX), int(REQROW_BTN_Y))
		self.btnDecline.SetUpVisual(ICON_DECLINE)
		self.btnDecline.SetOverVisual(ICON_DECLINE_OVER)
		self.btnDecline.SetDownVisual(ICON_DECLINE_CLICK)
		self.btnDecline.SetEvent(ui.__mem_func__(self.__OnDecline))
		self.btnDecline.Show()

		self.SetOverInEvent(ui.__mem_func__(self.__OnOverIn))
		self.SetOverOutEvent(ui.__mem_func__(self.__OnOverOut))

	def __del__(self):
		ui.Window.__del__(self)

	def __OnOverIn(self):
		self.__HideToolTip()
		tt = uitooltip.ToolTip()
		text = "%s - Lv%d" % (self.reqName, self.reqLevel)
		if IS_AR:
			tt.AutoAppendTextLineAE(text)
		else:
			tt.AutoAppendTextLine(text)
		tt.ResizeToolTip()
		tt.ShowToolTip()
		self.toolTip = tt

	def __OnOverOut(self):
		self.__HideToolTip()

	def __HideToolTip(self):
		if self.toolTip:
			self.toolTip.HideToolTip()
			self.toolTip = None

	def Destroy(self):
		self.__HideToolTip()
		self.pid = 0
		self.reqName = ""
		self.reqLevel = 0
		self.answered = False
		self.expireAt = 0.0
		self.bg = None
		self.portrait = None
		self.nameLine = None
		self.barBg = None
		self.bar = None
		self.btnAccept = None
		self.btnDecline = None

	def Tick(self, now):
		remaining = self.expireAt - now
		if remaining <= 0:
			return True
		frac = remaining / float(PF_PENDING_TTL_CLIENT)
		self.bar.SetSize(int(REQROW_TEXT_W * frac), REQROW_BAR_H)
		return False

	def __OnAccept(self):
		if self.answered:
			return
		self.answered = True
		net.SendPartyFinderJoinAnswer(self.pid, 1)

	def __OnDecline(self):
		if self.answered:
			return
		self.answered = True
		net.SendPartyFinderJoinAnswer(self.pid, 0)

def _MakeThinScrollBar():
	try:
		import ingamewikiui_new
		return ingamewikiui_new.AdvScrollBar()
	except Exception:
		return ui.ScrollBarNew()

class _PFList(ui.Window):
	ROW_HEIGHT = CARD_H
	ROW_GAP = 4

	def __init__(self):
		ui.Window.__init__(self)
		self.rows = []
		self.scrollBar = None

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		for row in self.rows:
			row.Destroy()
		self.rows = []
		self.scrollBar = None

	def SetScrollBar(self, bar):
		bar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		bar.SetScrollStep(0.2)
		self.scrollBar = bar

	def SetRows(self, dataList, serverNow, requestState, onRequestSent, onEditOwn, onDeleteOwn):
		for row in self.rows:
			row.Destroy()
		self.rows = []
		myLv = min(PF_MAX_LEVEL, player.GetStatus(player.LEVEL))
		ownName = player.GetName()
		for data in dataList:
			row = ListingCard(self, data, serverNow, myLv, ownName, requestState, onRequestSent, onEditOwn, onDeleteOwn)
			row.SetParent(self)
			if app.USE_CLIP_MASK:
				row.SetClippingMaskWindow(self)
			row.Show()
			self.rows.append(row)
		if self.scrollBar:
			self.scrollBar.SetPos(0)
		self.__AdjustScrollBar()
		self.__Layout()

	def __TotalHeight(self):
		return len(self.rows) * (self.ROW_HEIGHT + self.ROW_GAP)

	def __AdjustScrollBar(self):
		if not self.scrollBar:
			return
		total = float(self.__TotalHeight())
		self.scrollBar.SetMiddleBarSize(min(float(self.GetHeight()) / total, 1.0) if total else 1.0)

	def __OnScroll(self):
		self.__Layout()

	def __Layout(self):
		scrollPos = self.scrollBar.GetPos() if self.scrollBar else 0.0
		overflow = max(0, self.__TotalHeight() - self.GetHeight())
		y = -int(scrollPos * overflow)
		for row in self.rows:
			if y + self.ROW_HEIGHT <= 0 or y >= self.GetHeight():
				row.Hide()
			else:
				row.Show()
				row.SetPosition(0, y)
			y += self.ROW_HEIGHT + self.ROW_GAP

class PartyFinderWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		self.board = None
		self.imgHeader = None
		self.imgLeftBg = None
		self.imgRightBg = None
		self.btnHelp = None
		self.wndHelp = None

		self.filterCategoryCombo = None
		self.sortCombo = None
		self.fitsCheckBox = None
		self.fitsLabel = None
		self.btnRefresh = None

		self.rowList = None
		self.listScrollBar = None
		self.emptyLine = None
		self.emptyCtaBtn = None

		self.mgTitleLine = None
		self.mgLockedLine = None
		self.categoryCombo = None
		self.noteBg = None
		self.editNote = None
		self.noteCounterLine = None
		self.btnPost = None
		self.mgCatLine = None
		self.mgNoteLine = None
		self.mgStatusLine = None
		self.btnShare = None

		self.reqTitleLine = None
		self.reqPanel = None
		self.requestRows = []
		self.reqScrollY = 0

		self.mgMode = None
		self.pfLvLo = 1
		self.pfLvHi = 999
		self.pfLvMin = 1
		self.pfLvMax = 999

		self.entries = []
		self.serverNow = 0
		self.postCategory = _PF_CATS[0][0]
		self.filterCategory = _PF_FILTER_ALL
		self.filterFits = True
		self.sortMode = _PF_SORT_NEWEST
		self.requestState = {}

		self.promptQueue = []
		self.promptDialog = None
		self.currentPromptPid = 0
		self.currentPromptData = None
		self.unseenRequestCount = 0

		self.tickTime = 0.0
		self.boardReceivedAt = 0.0

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		if self.wndHelp:
			self.wndHelp.Destroy()
			self.wndHelp = None
		if self.promptDialog:
			self.promptDialog.Close()
			self.promptDialog = None
		self.promptQueue = []
		self.currentPromptPid = 0
		self.currentPromptData = None
		for row in self.requestRows:
			row.Destroy()
		self.requestRows = []
		if self.rowList:
			self.rowList.Destroy()
		self.rowList = None

		self.board = None
		self.imgHeader = None
		self.imgLeftBg = None
		self.imgRightBg = None
		self.btnHelp = None

		self.filterCategoryCombo = None
		self.sortCombo = None
		self.fitsCheckBox = None
		self.fitsLabel = None
		self.btnRefresh = None

		self.listScrollBar = None
		self.emptyLine = None
		self.emptyCtaBtn = None

		self.mgTitleLine = None
		self.mgLockedLine = None
		self.categoryCombo = None
		self.noteBg = None
		self.editNote = None
		self.noteCounterLine = None
		self.btnPost = None
		self.mgCatLine = None
		self.mgNoteLine = None
		self.mgStatusLine = None
		self.btnShare = None

		self.reqTitleLine = None
		self.reqPanel = None
		self.reqScrollY = 0

		self.mgMode = None
		self.tickTime = 0.0
		self.boardReceivedAt = 0.0

		self.pfLvLo = 1
		self.pfLvHi = 999
		self.pfLvMin = 1
		self.pfLvMax = 999

		self.entries = []
		self.serverNow = 0
		self.postCategory = _PF_CATS[0][0]
		self.filterCategory = _PF_FILTER_ALL
		self.filterFits = True
		self.sortMode = _PF_SORT_NEWEST
		self.requestState = {}
		self.unseenRequestCount = 0
		self.ClearDictionary()

	def __LoadWindow(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/partyfinderwindow.py")

		self.__BuildFrame()
		self.__BuildList()
		self.__BuildRequests()
		self.__BuildManagement()
		self.__BuildFilterBar()

	def __MakeBg(self, img, x, w, y):
		box = ui.ImageBox()
		box.SetParent(self)
		box.AddFlag("not_pick")
		box.SetPosition(int(_LayoutX(x, w, WINDOW_WIDTH)), int(y))
		box.LoadImage(img)
		box.Show()
		return box

	def __BuildFrame(self):
		self.board = self.GetChild("board")
		self.board.SetCloseEvent(ui.__mem_func__(self.Hide))

		self.imgHeader = self.__MakeBg(IMG_HEADER, HEADER_X, HEADER_W, HEADER_Y)
		self.imgLeftBg = self.__MakeBg(IMG_LEFT_BG, LEFT_X, LEFT_W, BODY_Y)
		self.imgRightBg = self.__MakeBg(IMG_RIGHT_BG, RIGHT_X, RIGHT_W, BODY_Y)

		btnHelp = ui.Button()
		btnHelp.SetParent(self)
		btnHelp.SetPosition(_LayoutX(19, 16, WINDOW_WIDTH), 9)
		btnHelp.SetUpVisual("spin_wheel/question_mark.png")
		btnHelp.SetOverVisual("spin_wheel/question_mark_1.png")
		btnHelp.SetDownVisual("spin_wheel/question_mark_2.png")
		btnHelp.SetEvent(ui.__mem_func__(self.__OnClickHelp))
		btnHelp.SetToolTipText(getattr(localeinfo, "PF_HELP_TITLE", "Party Finder - Help"), 0, -16)
		btnHelp.Show()
		self.btnHelp = btnHelp

	def Show(self):
		ui.ScriptWindow.Show(self)
		net.SendPartyFinderListRequest()
		self.__RefreshManagement()
		self.__DrainPromptQueueIntoRows()
		self.unseenRequestCount = 0
		uibadge.SetCount("party_finder", 0)

	def OnPressEscapeKey(self):
		self.Hide()
		return True

	def __PruneHiddenQueue(self, now):
		if not self.promptQueue:
			return
		alive = [data for data in self.promptQueue if now - data[4] < PF_PENDING_TTL_CLIENT]
		if len(alive) != len(self.promptQueue):
			self.promptQueue = alive

	def __OnClickHelp(self):
		if not self.wndHelp:
			self.wndHelp = uipartyfinderhelp.PartyFinderHelpWindow()
			self.wndHelp.Hide()
		if self.wndHelp.IsShow():
			self.wndHelp.Close()
		else:
			self.wndHelp.Open()

	def __BuildFilterBar(self):
		filterCombo = ui.ComboBoxNew()
		filterCombo.SetParent(self)
		filterCombo.SetPosition(_LayoutX(34, 104, WINDOW_WIDTH), FILTER_Y)
		filterCombo.SetSize(104, 21)
		filterCombo.SetEventNew(ui.__mem_func__(self.__OnCategoryFilterCombo))
		filterCombo.Show()
		self.filterCategoryCombo = filterCombo

		sortCombo = ui.ComboBoxNew()
		sortCombo.SetParent(self)
		sortCombo.SetPosition(_LayoutX(142, 104, WINDOW_WIDTH), FILTER_Y)
		sortCombo.SetSize(104, 21)
		sortCombo.SetEventNew(ui.__mem_func__(self.__OnSortCombo))
		for i, (value, key) in enumerate(_PF_SORTS):
			sortCombo.InsertItem2(i, _PF_SORT_LABELS[value])
		sortCombo.SetCurrentItem(_PF_SORT_LABELS[self.sortMode])
		sortCombo.Show()
		self.sortCombo = sortCombo

		checkBoxXLtr = 254
		checkBox = ui.CheckBoxNew(self, checkBoxXLtr, FILTER_Y + 3, ui.__mem_func__(self.__OnToggleFits))
		checkBox.SetPosition(_LayoutX(checkBoxXLtr, checkBox.GetWidth(), WINDOW_WIDTH), FILTER_Y + 3)
		checkBox.SetCheck(self.filterFits)
		checkBox.Show()
		self.fitsCheckBox = checkBox

		fitsLabel = ui.TextLine()
		fitsLabel.SetParent(self)
		fitsLabel.SetPosition(_LayoutX(checkBoxXLtr + checkBox.GetWidth() + 4, 0, WINDOW_WIDTH), FILTER_Y + 5)
		if IS_AR:
			fitsLabel.SetHorizontalAlignLeft()
		fitsLabel.SetText(getattr(localeinfo, "PF_FILTER_FITS", "Fits my level"))
		fitsLabel.Show()
		self.fitsLabel = fitsLabel

		btnRefresh = ui.Button()
		btnRefresh.SetParent(self)
		btnRefresh.SetPosition(_LayoutX(400, ACT_BTN_W, WINDOW_WIDTH), FILTER_Y - 1)
		btnRefresh.SetUpVisual(BTN_ACT_UP)
		btnRefresh.SetOverVisual(BTN_ACT_OVER)
		btnRefresh.SetDownVisual(BTN_ACT_DOWN)
		btnRefresh.SetText(getattr(localeinfo, "PF_REFRESH", "Refresh"))
		btnRefresh.SetEvent(ui.__mem_func__(self.__OnClickRefresh))
		btnRefresh.Show()
		self.btnRefresh = btnRefresh

		self.__RebuildCategoryCombo()

	def __BuildList(self):
		listWnd = _PFList()
		listWnd.SetParent(self)
		listWnd.SetPosition(_LayoutX(LIST_X, LIST_W, WINDOW_WIDTH), LIST_Y)
		listWnd.SetSize(LIST_W, LIST_H)
		listWnd.Show()
		self.rowList = listWnd

		scrollBar = _MakeThinScrollBar()
		scrollBar.allow_on_run_mouse_wheel = False
		scrollBar.SetParent(self)
		scrollBar.SetScrollBarSize(LIST_H - 14)
		scrollBar.SetPosition(_LayoutX(LIST_X + LIST_W + 2, scrollBar.GetWidth(), WINDOW_WIDTH), LIST_Y + 6)
		listWnd.SetScrollBar(scrollBar)
		scrollBar.Show()
		self.listScrollBar = scrollBar

		self.__BuildEmptyState(listWnd)

	def __BuildEmptyState(self, listWnd):
		emptyLine = ui.TextLine()
		emptyLine.SetParent(listWnd)
		emptyLine.AddFlag("not_pick")
		emptyLine.SetWindowHorizontalAlignCenter()
		emptyLine.SetHorizontalAlignCenter()
		emptyLine.SetPosition(0, int(LIST_H / 2 - 20))
		emptyLine.SetText(getattr(localeinfo, "PF_EMPTY", "No parties recruiting right now."))
		emptyLine.Hide()
		self.emptyLine = emptyLine

		emptyCtaBtn = ui.Button()
		emptyCtaBtn.SetParent(listWnd)
		emptyCtaBtn.SetWindowHorizontalAlignCenter()
		emptyCtaBtn.SetPosition(int(-EMPTY_BTN_W / 2), int(LIST_H / 2 + 6))
		emptyCtaBtn.SetUpVisual(LARGE_BTN_UP)
		emptyCtaBtn.SetOverVisual(LARGE_BTN_OVER)
		emptyCtaBtn.SetDownVisual(LARGE_BTN_DOWN)
		#emptyCtaBtn.SetSize(EMPTY_BTN_W, EMPTY_BTN_H)
		emptyCtaBtn.SetText(getattr(localeinfo, "PF_EMPTY_CTA", "Post yours"))
		emptyCtaBtn.SetEvent(ui.__mem_func__(self.__OnClickEmptyCta))
		emptyCtaBtn.Hide()
		self.emptyCtaBtn = emptyCtaBtn

	def __BuildManagement(self):
		title = ui.TextLine()
		title.SetParent(self)
		title.AddFlag("not_pick")
		title.SetPosition(_LayoutX(LEFT_INNER_X + 10, 0, WINDOW_WIDTH), MG_TITLE_Y)
		if IS_AR:
			title.SetHorizontalAlignLeft()
		title.SetText(getattr(localeinfo, "PF_YOUR_LISTING", "Your Listing"))
		title.Show()
		self.mgTitleLine = title

		locked = ui.TextLine()
		locked.SetParent(self)
		locked.AddFlag("not_pick")
		locked.SetPosition(_LayoutX(LEFT_INNER_X, 0, WINDOW_WIDTH), MG_CONTENT_Y)
		if IS_AR:
			locked.SetHorizontalAlignLeft()
		locked.SetPackedFontColor(_PF_AGE_COLOR)
		locked.SetText(getattr(localeinfo, "PF_ONLY_LEADER", "Only the leader can post."))
		locked.Hide()
		self.mgLockedLine = locked

		combo = ui.ComboBoxNew()
		combo.SetParent(self)
		combo.SetPosition(_LayoutX(LEFT_INNER_X, LEFT_INNER_W, WINDOW_WIDTH), MG_CONTENT_Y)
		combo.SetSize(LEFT_INNER_W, 21)
		combo.SetEventNew(ui.__mem_func__(self.__OnCategoryCombo))
		for i, (value, key) in enumerate(_PF_CATS):
			combo.InsertItem2(i, _PF_CAT_LABELS[value])
		combo.SetCurrentItem(_PF_CAT_LABELS[_PF_CATS[0][0]])
		combo.Show()
		self.categoryCombo = combo

		noteBg = ui.ImageBox()
		noteBg.SetParent(self)
		noteBg.AddFlag("not_pick")
		noteBg.SetPosition(_LayoutX(LEFT_INNER_X, NOTE_W, WINDOW_WIDTH), MG_CONTENT_Y + 28)
		noteBg.LoadImage(IMG_NOTE_BG)
		noteBg.Show()
		self.noteBg = noteBg

		edNote = ui.EditLine()
		edNote.SetParent(self)
		edNote.SetPosition(_LayoutX(LEFT_INNER_X + 4, NOTE_W - 8, WINDOW_WIDTH), MG_CONTENT_Y + 31)
		edNote.SetSize(NOTE_W - 8, 15)
		edNote.SetMax(app.PF_NOTE_MAX_LEN)
		edNote.SetEscapeEvent(ui.__mem_func__(self.Hide))
		hintNote = getattr(localeinfo, "PF_NOTE_HINT", "Note")
		if IS_AR:
			edNote.SetOverlayTextNew(hintNote)
		else:
			edNote.SetOverlayText(hintNote)
		edNote.SetUpdateEvent(ui.__mem_func__(self.__OnNoteUpdate))
		edNote.Show()
		self.editNote = edNote

		counter = ui.TextLine()
		counter.SetParent(self)
		counter.AddFlag("not_pick")
		counter.SetPosition(_LayoutX(LEFT_INNER_X, 0, WINDOW_WIDTH), MG_CONTENT_Y + 50)
		if IS_AR:
			counter.SetHorizontalAlignLeft()
		counter.SetPackedFontColor(_PF_AGE_COLOR)
		counter.Show()
		self.noteCounterLine = counter

		btnPost = ui.Button()
		btnPost.SetParent(self)
		btnPost.SetPosition(_LayoutX(LEFT_INNER_X + (LEFT_INNER_W - ACT_BTN_W) / 2, ACT_BTN_W, WINDOW_WIDTH), MG_CONTENT_Y + 50)
		btnPost.SetUpVisual(BTN_ACT_UP)
		btnPost.SetOverVisual(BTN_ACT_OVER)
		btnPost.SetDownVisual(BTN_ACT_DOWN)
		btnPost.SetText(getattr(localeinfo, "PF_POST", "Post"))
		btnPost.SetEvent(ui.__mem_func__(self.__OnClickPost))
		btnPost.Show()
		self.btnPost = btnPost

		catLine = ui.TextLine()
		catLine.SetParent(self)
		catLine.AddFlag("not_pick")
		catLine.SetPosition(_LayoutX(LEFT_INNER_X, 0, WINDOW_WIDTH), MG_CONTENT_Y)
		if IS_AR:
			catLine.SetHorizontalAlignLeft()
		catLine.Hide()
		self.mgCatLine = catLine

		noteLine = ui.TextLine()
		noteLine.SetParent(self)
		noteLine.AddFlag("not_pick")
		noteLine.SetPosition(_LayoutX(LEFT_INNER_X, 0, WINDOW_WIDTH), MG_CONTENT_Y + 20)
		if IS_AR:
			noteLine.SetHorizontalAlignLeft()
		noteLine.SetPackedFontColor(_PF_NOTE_COLOR)
		noteLine.Hide()
		self.mgNoteLine = noteLine

		statusLine = ui.TextLine()
		statusLine.SetParent(self)
		statusLine.AddFlag("not_pick")
		statusLine.SetPosition(_LayoutX(LEFT_INNER_X, 0, WINDOW_WIDTH), MG_CONTENT_Y + 40)
		if IS_AR:
			statusLine.SetHorizontalAlignLeft()
		statusLine.SetPackedFontColor(_PF_AGE_COLOR)
		statusLine.Hide()
		self.mgStatusLine = statusLine

		btnShare = ui.Button()
		btnShare.SetParent(self)
		btnShare.SetPosition(_LayoutX(LEFT_INNER_X + (LEFT_INNER_W - ACT_BTN_W) / 2, ACT_BTN_W, WINDOW_WIDTH), MG_CONTENT_Y + 58)
		btnShare.SetUpVisual(BTN_ACT_UP)
		btnShare.SetOverVisual(BTN_ACT_OVER)
		btnShare.SetDownVisual(BTN_ACT_DOWN)
		btnShare.SetText(getattr(localeinfo, "PF_SHARE", "Share"))
		btnShare.SetEvent(ui.__mem_func__(self.__OnClickShare))
		btnShare.Hide()
		self.btnShare = btnShare

	def __BuildRequests(self):
		title = ui.TextLine()
		title.SetParent(self)
		title.AddFlag("not_pick")
		title.SetPosition(_LayoutX(LEFT_INNER_X, 0, WINDOW_WIDTH), REQ_TITLE_Y)
		if IS_AR:
			title.SetHorizontalAlignLeft()
		title.Show()
		self.reqTitleLine = title
		self.__RefreshRequestsTitle()

		panel = ui.Window()
		panel.SetParent(self)
		panel.SetPosition(_LayoutX(LEFT_INNER_X, LEFT_INNER_W, WINDOW_WIDTH), REQ_CONTENT_Y)
		panel.SetSize(LEFT_INNER_W, REQ_CONTENT_H)
		panel.Show()
		self.reqPanel = panel

	def __HasOwnListing(self):
		ownName = player.GetName()
		for data in self.entries:
			if data[1] == ownName:
				return True
		return False

	def __ComputeMode(self):
		inParty = player.IsPartyMember(player.GetMainCharacterIndex())
		isLeader = player.IsPartyLeader(player.GetMainCharacterIndex())
		if inParty and not isLeader:
			return "LOCKED"
		if self.__HasOwnListing():
			return "LISTED"
		return "POST"

	def __RefreshManagement(self):
		mode = self.__ComputeMode()
		if mode != self.mgMode:
			self.mgMode = mode
			if mode == "POST":
				self.__ShowManagementPost()
			elif mode == "LOCKED":
				self.__ShowManagementLocked()
			else:
				self.__ShowManagementListed()
		elif mode == "LISTED":
			self.__RefreshListedInfo()
		self.__UpdateEmptyState()

	def __HideAllManagement(self):
		self.mgLockedLine.Hide()
		self.categoryCombo.Hide()
		self.noteBg.Hide()
		self.editNote.Hide()
		self.noteCounterLine.Hide()
		self.btnPost.Hide()
		self.mgCatLine.Hide()
		self.mgNoteLine.Hide()
		self.mgStatusLine.Hide()
		self.btnShare.Hide()

	def __ShowManagementPost(self):
		self.__HideAllManagement()
		self.categoryCombo.Show()
		self.noteBg.Show()
		self.editNote.Show()
		self.noteCounterLine.Show()
		self.btnPost.Show()

		myLv = player.GetStatus(player.LEVEL)
		self.pfLvLo = max(1, min(PF_MAX_LEVEL, myLv - 30))
		self.pfLvHi = max(1, min(PF_MAX_LEVEL, myLv + 30))
		self.pfLvMin = self.pfLvLo
		self.pfLvMax = self.pfLvHi

		self.postCategory = _PF_CATS[0][0]
		self.categoryCombo.SetCurrentItem(_PF_CAT_LABELS[self.postCategory])
		self.editNote.SetText("")
		self.__RefreshNoteCounter()

	def __ShowManagementLocked(self):
		self.__HideAllManagement()
		self.mgLockedLine.Show()
		self.__ClearAllRequests()

	def __ShowManagementListed(self):
		self.__HideAllManagement()
		self.mgCatLine.Show()
		self.mgNoteLine.Show()
		self.mgStatusLine.Show()
		self.btnShare.Show()
		self.__RefreshListedInfo()

	def __ClearAllRequests(self):
		for row in self.requestRows:
			row.Destroy()
		self.requestRows = []
		self.reqScrollY = 0
		self.promptQueue = []
		if self.promptDialog and self.promptDialog.IsShow():
			self.promptDialog.Close()
		self.currentPromptPid = 0
		self.currentPromptData = None
		self.__RefreshRequestsTitle()

	def __FindOwnEntry(self):
		ownName = player.GetName()
		for data in self.entries:
			if data[1] == ownName:
				return data
		return None

	def __RefreshListedInfo(self):
		entry = self.__FindOwnEntry()
		if not entry:
			return
		leaderPid, name, level, race, category, lvMin, lvMax, slotsOpen, note, postTime = entry
		self.mgCatLine.SetText(_CatLabel(category))
		self.mgCatLine.SetPackedFontColor(_PF_CAT_COLORS.get(category, _PF_NAME_COLOR))
		self.mgNoteLine.SetText(_Trunc(note, 26))
		self.__TickExpiryLabel()

	def __TickExpiryLabel(self):
		if not self.mgStatusLine:
			return
		entry = self.__FindOwnEntry()
		if not entry:
			self.mgStatusLine.SetText("")
			return
		slotsOpen = entry[7]
		postTime = entry[9]
		serverNowLocal = self.serverNow + (app.GetTime() - self.boardReceivedAt)
		remaining = int(PF_EXPIRE_SEC_CLIENT - (serverNowLocal - postTime))
		if remaining < 0:
			remaining = 0
		fmt = getattr(localeinfo, "PF_EXPIRES_IN", "Expires in %s")
		expiry = fmt % ("%02d:%02d" % (remaining // 60, remaining % 60))
		self.mgStatusLine.SetText("%s - %d open" % (expiry, slotsOpen))

	def __OnEditOwnListing(self, data):
		leaderPid, name, level, race, category, lvMin, lvMax, slotsOpen, note, postTime = data
		self.mgMode = "POST"
		self.__ShowManagementPost()
		self.postCategory = category
		self.categoryCombo.SetCurrentItem(_PF_CAT_LABELS.get(category, _PF_CAT_LABELS[_PF_CATS[0][0]]))
		self.editNote.SetText(note)
		self.__RefreshNoteCounter()
		self.editNote.SetFocus()

	def __OnDeleteOwnListing(self, leaderPid):
		net.SendPartyFinderClose()

	def __RefreshNoteCounter(self):
		length = len(self.editNote.GetText())
		self.noteCounterLine.SetText("%d/%d" % (length, app.PF_NOTE_MAX_LEN))

	def __OnNoteUpdate(self):
		self.__RefreshNoteCounter()

	def __OnCategoryCombo(self, wnd, index, name):
		wnd.SetCurrentItem(name)
		self.postCategory = _PF_CATS[index][0]

	def __OnCategoryFilterCombo(self, wnd, index, name):
		wnd.SetCurrentItem(name)
		if index <= 0:
			self.filterCategory = _PF_FILTER_ALL
		else:
			self.filterCategory = _PF_CATS[index - 1][0]
		self.__ApplyFilterSort()

	def __OnToggleFits(self):
		self.fitsCheckBox.SetCheck(not self.fitsCheckBox.GetCheck())
		self.filterFits = self.fitsCheckBox.GetCheck()
		self.__ApplyFilterSort()

	def __OnSortCombo(self, wnd, index, name):
		wnd.SetCurrentItem(name)
		self.sortMode = _PF_SORTS[index][0]
		self.__ApplyFilterSort()

	def __CountByCategory(self):
		counts = {}
		for data in self.entries:
			cat = data[4]
			counts[cat] = counts.get(cat, 0) + 1
		return counts

	def __CategoryIndex(self, value):
		if value == _PF_FILTER_ALL:
			return 0
		for i, (catValue, key) in enumerate(_PF_CATS):
			if catValue == value:
				return i + 1
		return 0

	def __RebuildCategoryCombo(self):
		combo = self.filterCategoryCombo
		if not combo:
			return
		counts = self.__CountByCategory()
		labels = ["%s (%d)" % (getattr(localeinfo, "PF_FILTER_ALL", "All"), len(self.entries))]
		for value, key in _PF_CATS:
			labels.append("%s (%d)" % (_PF_CAT_LABELS[value], counts.get(value, 0)))
		combo.ClearItem()
		for i, label in enumerate(labels):
			combo.InsertItem2(i, label)
		combo.SetCurrentItem(labels[self.__CategoryIndex(self.filterCategory)])

	def __ApplyFilterSort(self):
		if not self.rowList:
			return
		ownName = player.GetName()
		myLevel = min(PF_MAX_LEVEL, player.GetStatus(player.LEVEL))
		ownEntry = None
		rows = []
		for data in self.entries:
			if data[1] == ownName:
				ownEntry = data
				continue
			if self.filterCategory != _PF_FILTER_ALL and data[4] != self.filterCategory:
				continue
			if self.filterFits and not (data[5] <= myLevel <= data[6]):
				continue
			rows.append(data)
		if self.sortMode == _PF_SORT_SLOTS:
			rows = sorted(rows, key = lambda data: data[7], reverse = True)
		elif self.sortMode == _PF_SORT_LEVEL:
			rows = sorted(rows, key = lambda data: data[5])
		else:
			rows = sorted(rows, key = lambda data: data[9], reverse = True)
		if ownEntry is not None:
			rows = [ownEntry] + rows
		self.rowList.SetRows(rows, self.serverNow, self.requestState, ui.__mem_func__(self.__OnCardRequestSent), ui.__mem_func__(self.__OnEditOwnListing), ui.__mem_func__(self.__OnDeleteOwnListing))
		self.__UpdateEmptyState()

	def __OnClickRefresh(self):
		net.SendPartyFinderListRequest()

	def __OnClickShare(self):
		keyword = getattr(localeinfo, "PARTY_SHARE_KEYWORD", "")
		if keyword:
			net.SendChatPacket(keyword)

	def __OnClickPost(self):
		note = self.editNote.GetText()
		net.SendPartyFinderPost(int(self.postCategory), int(self.pfLvMin), int(self.pfLvMax), note)

	def OnRunMouseWheel(self, nLen):
		if self.requestRows and self.reqPanel and self.reqPanel.IsInPosition():
			self.__ScrollRequests(nLen)
			return True
		if self.listScrollBar and self.listScrollBar.IsShow():
			if self.listScrollBar.IsInPosition() or (self.rowList and self.rowList.IsInPosition()):
				if nLen > 0:
					self.listScrollBar.OnUp()
				else:
					self.listScrollBar.OnDown()
				return True
		return False

	def __ScrollRequests(self, nLen):
		step = REQROW_H + REQROW_GAP
		if nLen > 0:
			self.reqScrollY -= step
		else:
			self.reqScrollY += step
		self.__LayoutRequestRows()

	def OnBoard(self, serverNow, entries):
		self.boardReceivedAt = app.GetTime()
		self.serverNow = serverNow
		self.entries = entries
		self.__RebuildCategoryCombo()
		self.__ApplyFilterSort()
		self.__RefreshManagement()

	def __IsPidPending(self, pid):
		for row in self.requestRows:
			if row.pid == pid:
				return True
		for data in self.promptQueue:
			if data[0] == pid:
				return True
		return pid != 0 and pid == self.currentPromptPid

	def OnJoinPrompt(self, pid, name, level, race):
		if self.__IsPidPending(pid):
			return
		if self.IsShow():
			self.__CreateRequestRow(pid, name, level, race, app.GetTime() + PF_PENDING_TTL_CLIENT)
			self.__LayoutRequestRows()
			self.__RefreshRequestsTitle()
		else:
			self.promptQueue.append((pid, name, level, race, app.GetTime()))
			self.unseenRequestCount += 1
			uibadge.SetCount("party_finder", self.unseenRequestCount)
			fmt = getattr(localeinfo, "PF_REQUEST_WAITING", "%s wants to join your party - open the Party Finder to answer.")
			if "%s" in fmt:
				chat.AppendChat(chat.CHAT_TYPE_INFO, fmt % name)
			else:
				chat.AppendChat(chat.CHAT_TYPE_INFO, fmt)

	def __CreateRequestRow(self, pid, name, level, race, expireAt):
		row = RequestRow(pid, name, level, race, expireAt)
		row.SetParent(self.reqPanel)
		if app.USE_CLIP_MASK:
			row.SetClippingMaskWindow(self.reqPanel)
		row.Show()
		self.requestRows.append(row)
		return row

	def __DrainQueue(self, now):
		expired = 0
		for pid, name, level, race, arriveTime in self.promptQueue:
			if now - arriveTime >= PF_PENDING_TTL_CLIENT:
				expired += 1
				continue
			self.__CreateRequestRow(pid, name, level, race, arriveTime + PF_PENDING_TTL_CLIENT)
		self.promptQueue = []
		if expired > 0:
			fmt = getattr(localeinfo, "PF_REQUESTS_EXPIRED", "%d join request(s) expired before you opened the Party Finder.")
			if "%d" in fmt:
				chat.AppendChat(chat.CHAT_TYPE_INFO, fmt % expired)
			else:
				chat.AppendChat(chat.CHAT_TYPE_INFO, fmt)

	def __LayoutRequestRows(self):
		step = REQROW_H + REQROW_GAP
		maxScroll = max(0, len(self.requestRows) * step - REQ_CONTENT_H)
		self.reqScrollY = max(0, min(self.reqScrollY, maxScroll))
		for i, row in enumerate(self.requestRows):
			y = i * step - self.reqScrollY
			if y + REQROW_H <= 0 or y >= REQ_CONTENT_H:
				row.Hide()
			else:
				row.SetPosition(int(REQROW_X), int(y))
				row.Show()

	def __RefreshRequestsTitle(self):
		if not self.reqTitleLine:
			return
		count = len(self.requestRows) + len(self.promptQueue)
		fmt = getattr(localeinfo, "PF_REQUESTS", "Requests")
		self.reqTitleLine.SetText("%s (%d)" % (fmt, count))

	def __RetireRow(self, row):
		if row in self.requestRows:
			self.requestRows.remove(row)
		row.Destroy()
		self.__DrainQueue(app.GetTime())
		self.__LayoutRequestRows()
		self.__RefreshRequestsTitle()

	def __TickRequestRows(self, now):
		if not self.requestRows:
			return
		for row in list(self.requestRows):
			if getattr(row, "answered", False):
				self.__RetireRow(row)
			elif row.Tick(now):
				self.__RetireRow(row)

	def __DrainPromptQueueIntoRows(self):
		if self.promptDialog and self.promptDialog.IsShow() and self.currentPromptData:
			self.promptQueue.insert(0, self.currentPromptData)
			self.promptDialog.Close()
			self.currentPromptPid = 0
			self.currentPromptData = None
		self.__DrainQueue(app.GetTime())
		self.__LayoutRequestRows()
		self.__RefreshRequestsTitle()

	def __ShowNextPrompt(self):
		if not self.promptQueue:
			return
		if self.promptDialog and self.promptDialog.IsShow():
			return
		data = self.promptQueue.pop(0)
		pid, name, level, race = data[:4]
		self.currentPromptPid = pid
		self.currentPromptData = data

		if not self.promptDialog:
			dlg = uicommon.QuestionDialog()
			dlg.SetAcceptEvent(ui.__mem_func__(self.__OnPromptAccept))
			dlg.SetCancelEvent(ui.__mem_func__(self.__OnPromptCancel))
			self.promptDialog = dlg

		fmt = getattr(localeinfo, "PF_JOIN_PROMPT_QUESTION", "%s Lv%s wants to join your party.")
		self.promptDialog.SetText(fmt % (name, level))
		self.promptDialog.Open()

	def __OnPromptAccept(self):
		net.SendPartyFinderJoinAnswer(self.currentPromptPid, 1)
		self.__ClosePrompt()

	def __OnPromptCancel(self):
		net.SendPartyFinderJoinAnswer(self.currentPromptPid, 0)
		self.__ClosePrompt()

	def __ClosePrompt(self):
		if self.promptDialog:
			self.promptDialog.Close()
		self.currentPromptPid = 0
		self.currentPromptData = None
		self.__ShowNextPrompt()

	def OnUpdate(self):
		if not getattr(self, "reqPanel", None):
			return
		now = app.GetTime()
		if now < getattr(self, "tickTime", 0.0):
			return
		self.tickTime = now + 1.0
		if not self.IsShow():
			self.__PruneHiddenQueue(now)
			return
		if self.mgMode == "LISTED":
			self.__TickExpiryLabel()
		self.__TickRequestRows(now)
		self.__TickRequestState(now)

	def __OnCardRequestSent(self, leaderPid):
		self.requestState[leaderPid] = ("SENT", app.GetTime() + PF_PENDING_TTL_CLIENT)
		self.__RefreshCardState(leaderPid)

	def __FindPidByName(self, name):
		for data in self.entries:
			if data[1] == name:
				return data[0]
		return None

	def __RefreshCardState(self, leaderPid):
		if not self.rowList:
			return
		stateInfo = self.requestState.get(leaderPid)
		now = app.GetTime()
		for card in self.rowList.rows:
			if card.leaderPid == leaderPid:
				if stateInfo:
					state, untilTime = stateInfo
					card.RefreshState(state, untilTime - now)
				else:
					card.RefreshState(None, 0)
				break

	def __TickRequestState(self, now):
		if not self.requestState:
			return
		expired = []
		for pid, stateInfo in self.requestState.items():
			state, untilTime = stateInfo
			if now >= untilTime:
				expired.append(pid)
			elif state == "SENT":
				self.__RefreshCardState(pid)
		for pid in expired:
			del self.requestState[pid]
			self.__RefreshCardState(pid)

	def __UpdateEmptyState(self):
		if not self.emptyLine:
			return
		isEmpty = not self.rowList.rows if self.rowList else False
		if not isEmpty:
			self.emptyLine.Hide()
			self.emptyCtaBtn.Hide()
			return
		self.emptyLine.Show()
		if self.mgMode == "LOCKED":
			self.emptyCtaBtn.Hide()
		else:
			self.emptyCtaBtn.Show()

	def __OnClickEmptyCta(self):
		if self.mgMode == "LOCKED":
			return
		if self.mgMode != "POST":
			self.mgMode = "POST"
			self.__ShowManagementPost()
		self.editNote.SetFocus()

	def OnJoinResult(self, result, leaderName):
		key, fallback = _PF_RESULT_MAP.get(result, ("PF_RESULT_UNAVAILABLE", "That party is no longer available."))
		text = getattr(localeinfo, key, fallback)
		if "%s" in text:
			text = text % leaderName
		chat.AppendChat(chat.CHAT_TYPE_INFO, text)

		leaderPid = self.__FindPidByName(leaderName)
		if leaderPid is not None:
			if result == app.PF_JOIN_DECLINED:
				self.requestState[leaderPid] = ("LOCKED", app.GetTime() + PF_DECLINE_LOCK_CLIENT)
			elif leaderPid in self.requestState:
				del self.requestState[leaderPid]
			self.__RefreshCardState(leaderPid)
