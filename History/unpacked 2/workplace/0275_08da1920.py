# coding: latin_1

import app
import ui
import net
import player
import guild
import localeinfo
import uibadge

IS_AR = localeinfo.IsARABIC()

def _L(key, default):
	# localeinfo's wrapper returns "Locale not found: KEY" instead of raising,
	# so a plain getattr default never fires.
	value = getattr(localeinfo, key, default)
	if not value or value.startswith("Locale not found"):
		return default
	return value

def _MirrorX(x, w, parentW):
	return parentW - x - w

def _LayoutX(xLtr, w, parentW):
	if IS_AR:
		return _MirrorX(xLtr, w, parentW)
	return xLtr

def _C(name, default):
	return getattr(app, name, default)

MODE_CLOSED = _C("GF_MODE_CLOSED", 0)
MODE_OPEN = _C("GF_MODE_OPEN", 1)
MODE_APPROVAL = _C("GF_MODE_APPROVAL", 2)

LIST_COOLDOWN_SEC = _C("GF_LIST_COOLDOWN_MS", 3000) / 1000.0
MANAGE_COOLDOWN_SEC = _C("GF_MANAGE_COOLDOWN_MS", 1000) / 1000.0
DETAIL_COOLDOWN_SEC = _C("GF_DETAIL_COOLDOWN_MS", 500) / 1000.0

ART = "d:/ymir work/ui/new_guild/guild_application/"
IMG_FILTER_BG = ART + "bg_filter.png"
IMG_LIST_BG = ART + "bg_list.png"
IMG_APPS_BG = ART + "bg_list_application.png"
IMG_DETAIL_BG = ART + "details_bg.png"
IMG_NOTIF_BG = ART + "bg_notif.png"
IMG_LIST_TITLE = ART + "title_list.png"
IMG_APPS_TITLE = ART + "car_title_application.png"
IMG_DESC_BG = ART + "desc_bg.png"
IMG_EDIT_BG = ART + "editline_bg.png"
IMG_ROW = ART + "list_item.png"
IMG_ROW_HOVER = ART + "list_item_hover.png"
IMG_ROW_SELECT = ART + "list_item_select.png"
IMG_EMPIRE = {
	1: ART + "empire_1.png",
	2: ART + "empire_2.png",
	3: ART + "empire_3.png",
}

TAB_GUILD_UP = ART + "tab_guild_norm.png"
TAB_GUILD_OVER = ART + "tab_guild_hover.png"
TAB_GUILD_DOWN = ART + "tab_guild_select.png"
TAB_APPLY_UP = ART + "tab_apply_norm.png"
TAB_APPLY_OVER = ART + "tab_apply_hover.png"
TAB_APPLY_DOWN = ART + "tab_apply_select.png"

BTN_ACTION_UP = ART + "btn_apply_norm.png"
BTN_ACTION_OVER = ART + "btn_apply_hover.png"
BTN_ACTION_DOWN = ART + "btn_apply_select.png"
BTN_ACTION_DISABLE = ART + "btn_apply_disable.png"

PAGE_ART = "cream/searchshop/"
BTN_PAGE_UP = "btn_page_norm.png"
BTN_PAGE_OVER = "btn_page_hover.png"
BTN_PAGE_DOWN = "btn_page_down.png"

PAD = 10
GAP = 5

# every panel background carries a 25px title recess at its own top edge
STRIP_H = 25
STRIP_TEXT_Y = 6

# Page-tab rail, same shape as the companion window: a 36px column beside the
# board, so the tabs sit outside the frame instead of floating on top of it.
# The rail is part of the window rect - a child placed outside its parent
# renders but never gets picked.
RAIL_W = 40
TAB_X = 2
TAB_Y = 34
TAB_W = 36
TAB_H = 36
TAB_STEP = 38

BODY_Y = 40
PANEL_H = 298

FILTER_X = PAD
FILTER_W = 121
LIST_X = FILTER_X + FILTER_W + GAP
LIST_W = 306
DETAIL_X = LIST_X + LIST_W + GAP
DETAIL_W = 174

BOARD_W = DETAIL_X + DETAIL_W + PAD
WINDOW_WIDTH = RAIL_W + BOARD_W
WINDOW_HEIGHT = BODY_Y + PANEL_H + PAD

# the Applications tab reuses the browse tab's two left slots exactly:
# bg_filter (121) for the recruitment settings, bg_list_application (485) for
# the inbox - 10 + 121 + 5 + 485 + 10 lands on the same board width
SET_X = FILTER_X
SET_W = FILTER_W
APPS_X = LIST_X
APPS_W = 485
APPS_TITLE_W = 477

F_LABEL_X = 8
F_CTRL_X = 5
F_CTRL_W = 111
F_CTRL_H = 21
F_TYPE_LABEL_Y = 34
F_TYPE_CTRL_Y = 50
F_EMPIRE_LABEL_Y = 78
F_EMPIRE_CTRL_Y = 94
F_LEVEL_LABEL_Y = 122
F_LEVEL_CTRL_Y = 138
F_NAME_LABEL_Y = 166
F_NAME_CTRL_Y = 182
F_EDIT_INSET_X = 5
F_EDIT_INSET_Y = 4
F_EDIT_W = 101
F_EDIT_H = 15

REFRESH_W = 95
REFRESH_H = 26
REFRESH_X = (FILTER_W - REFRESH_W) // 2
REFRESH_Y = 214

LIST_TITLE_X = 2
LIST_TITLE_Y = 0
LIST_TITLE_W = 302
LIST_TITLE_H = 25

ROW_X = 5
ROW_Y0 = 30
ROW_W = 296
ROW_H = 29
ROW_STEP = 30
PAGE_SIZE = 8

MARK_W = 16
MARK_H = 12
COL_MARK_X = 7
COL_MARK_Y = 8
COL_NAME_X = 29
COL_NAME_W = 108
COL_LEVEL_X = 145
COL_LEVEL_W = 40
COL_MEMBERS_X = 191
COL_MEMBERS_W = 62
COL_EMPIRE_X = 262
COL_EMPIRE_W = 22
COL_EMPIRE_H = 14
ROW_TEXT_Y = 8
ROW_FLAG_Y = 7

PAGER_Y = 271
PAGER_BTN_W = 24
PAGER_BTN_H = 23
PAGER_STEP = 26
PAGER_SLOTS = 5

# details_bg.png already draws every frame this panel needs; these are the
# interiors of those frames, measured off the art, and nothing may be painted
# on top of them
D_MARK_SLOT_X = 21
D_MARK_SLOT_Y = 56
D_MARK_SLOT_W = 34
D_MARK_SLOT_H = 20
D_MARK_SCALE = 1.5
D_MARK_X = D_MARK_SLOT_X + (D_MARK_SLOT_W - int(MARK_W * D_MARK_SCALE)) // 2
D_MARK_Y = D_MARK_SLOT_Y + (D_MARK_SLOT_H - int(MARK_H * D_MARK_SCALE)) // 2

D_BOX_X = 76
D_BOX_W = 87
D_BOX_TEXT_DY = 3
D_NAME_Y = 35
D_LEVEL_Y = 60
D_EMPIRE_Y = 85

D_FLAG_W = 22
D_FLAG_H = 14
D_FLAG_X = D_BOX_X + (D_BOX_W - D_FLAG_W) // 2
D_FLAG_Y = D_EMPIRE_Y + 3

D_ROW_X = 9
D_ROW_W = 154
D_MEMBERS_Y = 120
D_ONLINE_Y = 145
D_REQ_Y = 170

D_DESC_X = 9
D_DESC_Y = 195
D_DESC_W = 154
D_DESC_H = 57
D_DESC_TEXT_X = D_DESC_X + 7
D_DESC_TEXT_Y = D_DESC_Y + 5
D_DESC_TEXT_W = D_DESC_W - 14
D_DESC_LINE_STEP = 13
D_DESC_LINES = 3
D_BTN_W = 95
D_BTN_H = 26
D_BTN_X = (DETAIL_W - D_BTN_W) // 2
D_BTN_Y = 262

NOTIF_W = 362
NOTIF_H = 132
NOTIF_X = (BOARD_W - NOTIF_W) // 2
NOTIF_Y = BODY_Y + (PANEL_H - NOTIF_H) // 2
NOTIF_TEXT_W = 320
NOTIF_LINE_STEP = 15
NOTIF_LINES = 3
NOTIF_SHOW_SEC = 4.0

ELLIPSIS = "..."

TAB_BROWSE = 0
TAB_APPS = 1

FILTER_ALL = -1

COLOR_TEXT = 0xffe8dcc8
COLOR_DIM = 0xff9a9184
COLOR_TITLE = 0xffe1c289
COLOR_WARN = 0xffd63333

DESC_MAX_LEN = _C("GF_DESC_MAX_LEN", 96)

MESSENGER_ART = "d:/ymir work/ui/game/messenger/"

# applicant bJob is the raw race (MAIN_RACE 0-8); 8 is the wolfman and has no portrait art
PORTRAIT_IMG = {
	0: MESSENGER_ART + "war_m.png",
	1: MESSENGER_ART + "ninja_w.png",
	2: MESSENGER_ART + "sura_m.png",
	3: MESSENGER_ART + "sham_w.png",
	4: MESSENGER_ART + "war_f.png",
	5: MESSENGER_ART + "ninja_m.png",
	6: MESSENGER_ART + "sura_w.png",
	7: MESSENGER_ART + "sham_m.png",
}

IMG_APP_ROW = ART + "list_item_application.png"
BTN_ACCEPT_UP = ART + "btn_accept_norm.png"
BTN_ACCEPT_OVER = ART + "btn_accept_hover.png"
BTN_ACCEPT_DOWN = ART + "btn_accept_select.png"
BTN_REJECT_UP = ART + "btn_reject_norm.png"
BTN_REJECT_OVER = ART + "btn_reject_hover.png"
BTN_REJECT_DOWN = ART + "btn_reject_select.png"

# recruitment settings, in the same bg_filter panel the browse tab uses for filters
S_MODE_LABEL_Y = F_TYPE_LABEL_Y
S_MODE_CTRL_Y = F_TYPE_CTRL_Y
S_LEVEL_LABEL_Y = F_EMPIRE_LABEL_Y
S_LEVEL_CTRL_Y = F_EMPIRE_CTRL_Y
S_DESC_LABEL_Y = F_LEVEL_LABEL_Y
S_DESC_BOX_X = F_CTRL_X
S_DESC_BOX_Y = F_LEVEL_CTRL_Y
S_DESC_BOX_W = 111
S_DESC_BOX_H = 59
S_DESC_EDIT_X = S_DESC_BOX_X + 6
S_DESC_EDIT_Y = S_DESC_BOX_Y + 5
S_DESC_EDIT_W = S_DESC_BOX_W - 12
S_DESC_EDIT_H = 48
S_COUNT_Y = S_DESC_BOX_Y + S_DESC_BOX_H + 3
S_SAVE_W = REFRESH_W
S_SAVE_X = REFRESH_X
S_SAVE_Y = REFRESH_Y

A_STRIP_X = 4
A_STRIP_W = APPS_TITLE_W
A_STRIP_H = 23
A_HEAD1_Y = 2
A_HEAD_TEXT_X = 14
A_HEAD_TEXT_DY = 5

A_ROW_X = 2
A_ROW_W = 481
A_ROW_H = 29
A_ROW_Y0 = 32
A_ROW_STEP = 30
A_PAGE_SIZE = 8
A_EMPTY_Y = 140

A_PORTRAIT_X = 3
A_NAME_X = 40
A_LEVEL_X = 210
A_ROW_TEXT_Y = 8
A_BTN_W = 50
A_BTN_H = 21
A_BTN_Y = 4
A_ACCEPT_X = A_ROW_W - 10 - A_BTN_W * 2 - 4
A_REJECT_X = A_ROW_W - 10 - A_BTN_W

A_PAGER_Y = A_ROW_Y0 + A_ROW_STEP * A_PAGE_SIZE + 3
A_PAGER_BTN_W = 24
A_PAGER_NEXT_X = A_ROW_X + A_ROW_W - A_PAGER_BTN_W
A_PAGER_LABEL_X = A_PAGER_NEXT_X - 46
A_PAGER_PREV_X = A_PAGER_NEXT_X - 74

_MODE_ITEMS = (
	(MODE_CLOSED, "GUILD_FINDER_TYPE_CLOSED", "Not recruiting"),
	(MODE_OPEN, "GUILD_FINDER_TYPE_OPEN", "Open"),
	(MODE_APPROVAL, "GUILD_FINDER_TYPE_APPROVAL", "By application"),
)

BROWSE_COMBOS = ("typeCombo", "empireCombo")
BROWSE_EDITS = ("levelEdit", "nameEdit")
APPS_COMBOS = ("setModeCombo",)
APPS_EDITS = ("setLevelEdit", "setDescEdit")

_TYPE_FILTERS = (
	(FILTER_ALL, "GUILD_FINDER_TYPE_ALL", "All"),
	(MODE_OPEN, "GUILD_FINDER_TYPE_OPEN", "Open"),
	(MODE_APPROVAL, "GUILD_FINDER_TYPE_APPROVAL", "By application"),
	(MODE_CLOSED, "GUILD_FINDER_TYPE_CLOSED", "Not recruiting"),
)

_EMPIRE_FILTERS = (
	(FILTER_ALL, "GUILD_FINDER_TYPE_ALL", "All"),
	(1, "GUILDWINDOW_LIST_EMPIRE_A", "Shinsoo"),
	(2, "GUILDWINDOW_LIST_EMPIRE_B", "Chunjo"),
	(3, "GUILDWINDOW_LIST_EMPIRE_C", "Jinno"),
)

_RESULT_SPEC = (
	("GF_OK", "GUILD_FINDER_OK_ANSWERED", "Application handled."),
	("GF_OK_APPLIED", "GUILD_FINDER_OK_APPLIED", "Application sent."),
	("GF_OK_CANCELED", "GUILD_FINDER_OK_CANCELED", "Application withdrawn."),
	("GF_OK_JOINED", "GUILD_FINDER_OK_JOINED", "You joined the guild."),
	("GF_OK_SETTINGS_SAVED", "GUILD_FINDER_SETTINGS_SAVED", "Recruitment settings saved."),
	("GF_APP_ACCEPTED", "GUILD_FINDER_APP_ACCEPTED", "Your application was accepted."),
	("GF_APP_REJECTED", "GUILD_FINDER_APP_REJECTED", "Your application was declined."),
	("GF_ERR_COOLDOWN", "GUILD_FINDER_ERR_COOLDOWN", "Please wait a moment before trying again."),
	("GF_ERR_WRONG_EMPIRE", "GUILD_FINDER_BTN_WRONG_EMPIRE", "Different kingdom"),
	("GF_ERR_LEVEL_LOW", "GUILD_FINDER_BTN_LEVEL_LOW", "Level too low"),
	("GF_ERR_GUILD_FULL", "GUILD_FINDER_ERR_GUILD_FULL", "That guild is full."),
	("GF_ERR_CLOSED", "GUILD_FINDER_ERR_CLOSED", "This guild does not accept this request."),
	("GF_ERR_DUP_APP", "GUILD_FINDER_ERR_DUP_APP", "You already applied to this guild."),
	("GF_ERR_TOO_MANY_APPS", "GUILD_FINDER_ERR_TOO_MANY_APPS", "You have too many open applications."),
	("GF_ERR_REJECTED_RECENTLY", "GUILD_FINDER_ERR_REJECTED_RECENTLY", "This guild turned you down recently. Try again later."),
	("GF_ERR_NO_AUTH", "GUILD_FINDER_ERR_NO_AUTH", "You are not allowed to do that."),
	("GF_ERR_APPLICANT_GONE", "GUILD_FINDER_ERR_APPLICANT_GONE", "That applicant is no longer available."),
	("GF_ERR_HAS_GUILD", "GUILD_FINDER_BTN_HAS_GUILD", "Already in a guild"),
	("GF_ERR_JOIN_PENALTY", "GUILD_FINDER_ERR_JOIN_PENALTY", "You cannot join a guild yet."),
	("GF_ERR_BANWORD", "GUILD_FINDER_ERR_BANWORD", "That text contains a forbidden word."),
	("GF_ERR_GUILD_GONE", "GUILD_FINDER_ERR_GUILD_GONE", "That guild no longer exists."),
	("GF_ERR_APP_EXPIRED", "GUILD_FINDER_ERR_APP_EXPIRED", "That application has expired."),
	("GF_ERR_DB_FROZEN", "GUILD_FINDER_ERR_DB_FROZEN", "The service is busy. Try again shortly."),
)

RESULT_TEXT = {}
for _name, _key, _default in _RESULT_SPEC:
	_value = getattr(app, _name, None)
	if _value is not None:
		RESULT_TEXT[_value] = _L(_key, _default)
del _name, _key, _default, _value


class _GuildRow(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.SetSize(int(ROW_W), int(ROW_H))

		self.rowGid = 0
		self.rowEvent = None
		self.rowSelected = False

		bg = ui.ImageBox()
		bg.SetParent(self)
		bg.AddFlag("not_pick")
		bg.SetPosition(0, 0)
		bg.LoadImage(IMG_ROW)
		bg.Show()
		self.bg = bg

		mark = ui.MarkBox()
		mark.SetParent(self)
		mark.AddFlag("not_pick")
		mark.SetPosition(int(_LayoutX(COL_MARK_X, MARK_W, ROW_W)), int(COL_MARK_Y))
		mark.Hide()
		self.markBox = mark

		self.nameLine = self.__MakeText(COL_NAME_X, COL_NAME_W, COLOR_TEXT)
		self.levelLine = self.__MakeText(COL_LEVEL_X, COL_LEVEL_W, COLOR_TEXT)
		self.membersLine = self.__MakeText(COL_MEMBERS_X, COL_MEMBERS_W, COLOR_TEXT)

		flag = ui.ImageBox()
		flag.SetParent(self)
		flag.AddFlag("not_pick")
		flag.SetPosition(int(_LayoutX(COL_EMPIRE_X, COL_EMPIRE_W, ROW_W)), int(ROW_FLAG_Y))
		flag.Hide()
		self.flagBox = flag

	def __MakeText(self, xLtr, w, color):
		line = ui.TextLine()
		line.SetParent(self)
		line.AddFlag("not_pick")
		# Arabic anchors text at the mirrored column's right edge, so the box
		# width must not be subtracted a second time.
		line.SetPosition(int(_LayoutX(xLtr, 0, ROW_W)), int(ROW_TEXT_Y))
		if IS_AR:
			line.SetHorizontalAlignLeft()
		line.SetPackedFontColor(color)
		line.Show()
		return line

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.rowEvent = None
		self.bg = None
		self.markBox = None
		self.nameLine = None
		self.levelLine = None
		self.membersLine = None
		self.flagBox = None
		self.rowGid = 0
		self.rowSelected = False

	def SetRowEvent(self, event):
		self.rowEvent = event

	def SetData(self, entry):
		self.rowGid = entry[0]
		if self.rowGid:
			self.markBox.SetIndex(self.rowGid)
			self.markBox.Show()
		else:
			self.markBox.Hide()
		self.nameLine.SetText(entry[1])
		self.levelLine.SetText("%d" % entry[2])
		self.membersLine.SetText("%d/%d" % (entry[3], entry[4]))
		image = IMG_EMPIRE.get(entry[5])
		if image:
			self.flagBox.LoadImage(image)
			self.flagBox.Show()
		else:
			self.flagBox.Hide()

	def SetSelected(self, flag):
		self.rowSelected = flag
		self.__ApplyBackground(False)

	def __ApplyBackground(self, over):
		bg = getattr(self, "bg", None)
		if not bg:
			return
		if self.rowSelected:
			bg.LoadImage(IMG_ROW_SELECT)
		elif over:
			bg.LoadImage(IMG_ROW_HOVER)
		else:
			bg.LoadImage(IMG_ROW)

	def OnMouseOverIn(self):
		self.__ApplyBackground(True)

	def OnMouseOverOut(self):
		self.__ApplyBackground(False)

	def OnMouseLeftButtonDown(self):
		event = getattr(self, "rowEvent", None)
		if event:
			event(self.rowGid)
		return True


class _ApplicantRow(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.SetSize(int(A_ROW_W), int(A_ROW_H))

		self.rowPid = 0
		self.answerEvent = None

		bg = ui.ImageBox()
		bg.SetParent(self)
		bg.AddFlag("not_pick")
		bg.SetPosition(0, 0)
		bg.LoadImage(IMG_APP_ROW)
		bg.Show()
		self.bg = bg

		portrait = ui.ImageBox()
		portrait.SetParent(self)
		portrait.AddFlag("not_pick")
		portrait.SetPosition(int(_LayoutX(A_PORTRAIT_X, 29, A_ROW_W)), 0)
		portrait.Hide()
		self.portrait = portrait

		self.nameLine = self.__MakeText(A_NAME_X, COLOR_TEXT)
		self.levelLine = self.__MakeText(A_LEVEL_X, COLOR_DIM)

		self.btnAccept = self.__MakeButton(A_ACCEPT_X, BTN_ACCEPT_UP, BTN_ACCEPT_OVER, BTN_ACCEPT_DOWN,
			_L("GUILD_FINDER_BTN_ACCEPT", "Accept"), self.__OnClickAccept)
		self.btnReject = self.__MakeButton(A_REJECT_X, BTN_REJECT_UP, BTN_REJECT_OVER, BTN_REJECT_DOWN,
			_L("GUILD_FINDER_BTN_REJECT", "Reject"), self.__OnClickReject)

	def __MakeText(self, xLtr, color):
		line = ui.TextLine()
		line.SetParent(self)
		line.AddFlag("not_pick")
		line.SetPosition(int(_LayoutX(xLtr, 0, A_ROW_W)), int(A_ROW_TEXT_Y))
		if IS_AR:
			line.SetHorizontalAlignLeft()
		line.SetPackedFontColor(color)
		line.Show()
		return line

	def __MakeButton(self, xLtr, up, over, down, tooltip, handler):
		btn = ui.Button()
		btn.SetParent(self)
		btn.SetPosition(int(_LayoutX(xLtr, A_BTN_W, A_ROW_W)), int(A_BTN_Y))
		btn.SetUpVisual(up)
		btn.SetOverVisual(over)
		btn.SetDownVisual(down)
		btn.SetDisableVisual(down)
		btn.SetToolTipText(tooltip, 0, -16)
		btn.SetEvent(ui.__mem_func__(handler))
		btn.Show()
		return btn

	def SetAnswerEnabled(self, enabled):
		for name in ("btnAccept", "btnReject"):
			btn = getattr(self, name, None)
			if not btn:
				continue
			if enabled:
				btn.Enable()
				btn.SetUp()
			else:
				btn.Disable()

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.answerEvent = None
		self.bg = None
		self.portrait = None
		self.nameLine = None
		self.levelLine = None
		self.btnAccept = None
		self.btnReject = None
		self.rowPid = 0

	def SetAnswerEvent(self, event):
		self.answerEvent = event

	def SetData(self, applicant):
		self.rowPid = applicant[0]
		self.nameLine.SetText(applicant[1])
		self.levelLine.SetText("%s %d" % (_L("GUILD_FINDER_COL_LEVEL", "Lv"), applicant[2]))
		image = PORTRAIT_IMG.get(applicant[3])
		if image:
			self.portrait.LoadImage(image)
			self.portrait.Show()
		else:
			self.portrait.Hide()

	def __Answer(self, accept):
		event = getattr(self, "answerEvent", None)
		pid = getattr(self, "rowPid", 0)
		if event and pid:
			event(pid, accept)

	def __OnClickAccept(self):
		self.__Answer(1)

	def __OnClickReject(self):
		self.__Answer(0)


class _NoticePanel(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.SetSize(int(NOTIF_W), int(NOTIF_H))

	def __del__(self):
		ui.Window.__del__(self)

	def OnMouseLeftButtonDown(self):
		self.Hide()
		return True


class GuildFinderWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.content = None
		self.board = None
		self.btnTabGuilds = None
		self.btnTabApps = None
		self.btnRefresh = None

		self.filterPanel = None
		self.filterBg = None
		self.filterTitle = None
		self.typeLabel = None
		self.typeCombo = None
		self.empireLabel = None
		self.empireCombo = None
		self.levelLabel = None
		self.levelEditBg = None
		self.levelEdit = None
		self.nameLabel = None
		self.nameEditBg = None
		self.nameEdit = None

		self.listPanel = None
		self.listBg = None
		self.listTitleImg = None
		self.headerLines = []
		self.rows = []
		self.emptyLine = None
		self.pageButtons = []
		self.btnPrevPage = None
		self.btnNextPage = None

		self.detailPanel = None
		self.detailBg = None
		self.detailTitle = None
		self.detailMark = None
		self.detailName = None
		self.detailLeaderLine = None
		self.detailFlag = None
		self.detailLevel = None
		self.detailMembersLine = None
		self.detailOnlineLine = None
		self.detailReqLine = None
		self.detailDescLines = []
		self.btnAction = None

		self.setPanel = None
		self.setBg = None
		self.setTitle = None
		self.inboxPanel = None
		self.inboxBg = None
		self.inboxTitleImg = None
		self.inboxTitle = None
		self.setModeLabel = None
		self.setModeCombo = None
		self.setLevelLabel = None
		self.setLevelEditBg = None
		self.setLevelEdit = None
		self.setDescLabel = None
		self.setDescCount = None
		self.setDescBg = None
		self.setDescEdit = None
		self.btnSaveSettings = None
		self.appRows = []
		self.appEmptyLine = None
		self.btnAppPrev = None
		self.btnAppNext = None
		self.appPageLine = None

		self.noticePanel = None
		self.noticeBg = None
		self.noticeLines = []

		self.measureLine = None

		self.entries = []
		self.filtered = []
		self.myAppGids = []
		self.currentTab = TAB_BROWSE
		self.currentPage = 1
		self.pageCount = 1
		self.paginationGroup = 1
		self.shownPages = 1

		self.filterMode = FILTER_ALL
		self.filterEmpire = FILTER_ALL
		self.filterMaxReqLevel = 0
		self.filterName = ""

		self.selectedGid = 0
		self.detailGid = 0
		self.detailLeader = ""
		self.detailMembers = 0
		self.detailMax = 0
		self.detailOnline = 0
		self.detailDesc = ""
		self.actionMode = None

		self.refreshReadyTime = 0.0
		self.detailReadyTime = 0.0
		self.detailPendingGid = 0
		self.noticeHideTime = 0.0
		self.closeAfterNotice = False

		self.inboxGid = 0
		self.inboxMode = MODE_CLOSED
		self.inboxMinLevel = 0
		self.inboxDesc = ""
		self.inboxApplicants = []
		self.pendingAnswers = []
		self.inboxRefreshTime = 0.0
		self.manageReadyTime = 0.0
		self.setMode = MODE_CLOSED
		self.appsPage = 1
		self.appsPageCount = 1

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		for row in self.rows:
			row.Destroy()
		self.rows = []
		for row in self.appRows:
			row.Destroy()
		self.appRows = []
		if self.typeCombo:
			self.typeCombo.Destroy()
		if self.empireCombo:
			self.empireCombo.Destroy()
		if self.setModeCombo:
			self.setModeCombo.Destroy()

		self.content = None
		self.board = None
		self.btnTabGuilds = None
		self.btnTabApps = None
		self.btnRefresh = None

		self.filterPanel = None
		self.filterBg = None
		self.filterTitle = None
		self.typeLabel = None
		self.typeCombo = None
		self.empireLabel = None
		self.empireCombo = None
		self.levelLabel = None
		self.levelEditBg = None
		self.levelEdit = None
		self.nameLabel = None
		self.nameEditBg = None
		self.nameEdit = None

		self.listPanel = None
		self.listBg = None
		self.listTitleImg = None
		self.headerLines = []
		self.emptyLine = None
		self.pageButtons = []
		self.btnPrevPage = None
		self.btnNextPage = None

		self.detailPanel = None
		self.detailBg = None
		self.detailTitle = None
		self.detailMark = None
		self.detailName = None
		self.detailLeaderLine = None
		self.detailFlag = None
		self.detailLevel = None
		self.detailMembersLine = None
		self.detailOnlineLine = None
		self.detailReqLine = None
		self.detailDescLines = []
		self.btnAction = None

		self.setPanel = None
		self.setBg = None
		self.setTitle = None
		self.inboxPanel = None
		self.inboxBg = None
		self.inboxTitleImg = None
		self.inboxTitle = None
		self.setModeLabel = None
		self.setModeCombo = None
		self.setLevelLabel = None
		self.setLevelEditBg = None
		self.setLevelEdit = None
		self.setDescLabel = None
		self.setDescCount = None
		self.setDescBg = None
		self.setDescEdit = None
		self.btnSaveSettings = None
		self.appEmptyLine = None
		self.btnAppPrev = None
		self.btnAppNext = None
		self.appPageLine = None

		self.noticePanel = None
		self.noticeBg = None
		self.noticeLines = []
		self.measureLine = None

		self.entries = []
		self.filtered = []
		self.myAppGids = []
		self.currentTab = TAB_BROWSE
		self.currentPage = 1
		self.pageCount = 1
		self.paginationGroup = 1
		self.shownPages = 1
		self.filterMode = FILTER_ALL
		self.filterEmpire = FILTER_ALL
		self.filterMaxReqLevel = 0
		self.filterName = ""
		self.selectedGid = 0
		self.detailGid = 0
		self.detailLeader = ""
		self.detailMembers = 0
		self.detailMax = 0
		self.detailOnline = 0
		self.detailDesc = ""
		self.actionMode = None
		self.refreshReadyTime = 0.0
		self.detailReadyTime = 0.0
		self.detailPendingGid = 0
		self.noticeHideTime = 0.0
		self.closeAfterNotice = False
		self.inboxGid = 0
		self.inboxMode = MODE_CLOSED
		self.inboxMinLevel = 0
		self.inboxDesc = ""
		self.inboxApplicants = []
		self.pendingAnswers = []
		self.inboxRefreshTime = 0.0
		self.manageReadyTime = 0.0
		self.setMode = MODE_CLOSED
		self.appsPage = 1
		self.appsPageCount = 1
		self.ClearDictionary()

	# ---- construction -------------------------------------------------------

	def __LoadWindow(self):
		self.SetSize(int(WINDOW_WIDTH), int(WINDOW_HEIGHT))
		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetCenterPosition()

		self.__BuildFrame()
		self.__BuildFilterPanel()
		self.__BuildListPanel()
		self.__BuildDetailPanel()
		self.__BuildSettingsPanel()
		self.__BuildInboxPanel()
		self.__BuildNotice()

		self.__SelectTab(TAB_BROWSE)
		self.__RefreshAppsTabAvailability()
		self.__RefreshActionButton()

	def __BuildFrame(self):
		content = ui.Window()
		content.SetParent(self)
		content.SetPosition(int(_LayoutX(RAIL_W, BOARD_W, WINDOW_WIDTH)), 0)
		content.SetSize(int(BOARD_W), int(WINDOW_HEIGHT))
		content.Show()
		self.content = content

		board = ui.BoardWithTitleBar()
		board.SetParent(content)
		board.SetPosition(0, 0)
		board.SetSize(int(BOARD_W), int(WINDOW_HEIGHT))
		board.SetTitleName(_L("GUILD_FINDER_TITLE", "Guild Finder"))
		board.SetCloseEvent(ui.__mem_func__(self.Close))
		board.Show()
		self.board = board

		self.btnTabGuilds = self.__MakeTab(0, TAB_GUILD_UP, TAB_GUILD_OVER, TAB_GUILD_DOWN,
			_L("GUILD_FINDER_TAB_GUILDS", "Guilds"), self.__OnClickTabGuilds)
		self.btnTabApps = self.__MakeTab(1, TAB_APPLY_UP, TAB_APPLY_OVER, TAB_APPLY_DOWN,
			_L("GUILD_FINDER_TAB_APPLICATIONS", "Applications"), self.__OnClickTabApps)

		measure = ui.TextLine()
		measure.SetParent(self)
		measure.AddFlag("not_pick")
		measure.SetPosition(0, 0)
		measure.Hide()
		self.measureLine = measure

	def __MakeTab(self, index, up, over, down, tooltip, handler):
		btn = ui.Button()
		btn.SetParent(self)
		btn.SetPosition(int(_LayoutX(TAB_X, TAB_W, WINDOW_WIDTH)), int(TAB_Y + index * TAB_STEP))
		btn.SetUpVisual(up)
		btn.SetOverVisual(over)
		btn.SetDownVisual(down)
		btn.SetToolTipText(tooltip, 0, -16)
		btn.SetEvent(ui.__mem_func__(handler))
		btn.Show()
		return btn

	def __MakePanel(self, xLtr, w, image, parentW = BOARD_W):
		panel = ui.Window()
		panel.SetParent(self.content)
		panel.SetPosition(int(_LayoutX(xLtr, w, parentW)), int(BODY_Y))
		panel.SetSize(int(w), int(PANEL_H))
		panel.Show()

		bg = ui.ImageBox()
		bg.SetParent(panel)
		bg.AddFlag("not_pick")
		bg.SetPosition(0, 0)
		bg.LoadImage(image)
		bg.Show()
		return panel, bg

	def __MakeLabel(self, parent, xLtr, y, parentW, text, color):
		line = ui.TextLine()
		line.SetParent(parent)
		line.AddFlag("not_pick")
		line.SetPosition(int(_LayoutX(xLtr, 0, parentW)), int(y))
		if IS_AR:
			line.SetHorizontalAlignLeft()
		line.SetPackedFontColor(color)
		line.SetText(text)
		line.Show()
		return line

	def __BuildFilterPanel(self):
		panel, bg = self.__MakePanel(FILTER_X, FILTER_W, IMG_FILTER_BG)
		self.filterPanel = panel
		self.filterBg = bg

		self.filterTitle = self.__MakeCenteredLine(panel, STRIP_TEXT_Y, COLOR_TITLE)
		self.filterTitle.SetText(_L("GUILD_FINDER_FILTER_TITLE", "Filter"))
		self.typeLabel = self.__MakeLabel(panel, F_LABEL_X, F_TYPE_LABEL_Y, FILTER_W,
			_L("GUILD_FINDER_FILTER_TYPE", "Type"), COLOR_DIM)
		self.empireLabel = self.__MakeLabel(panel, F_LABEL_X, F_EMPIRE_LABEL_Y, FILTER_W,
			_L("GUILD_FINDER_FILTER_EMPIRE", "Kingdom"), COLOR_DIM)
		self.levelLabel = self.__MakeLabel(panel, F_LABEL_X, F_LEVEL_LABEL_Y, FILTER_W,
			_L("GUILD_FINDER_FILTER_MIN_LEVEL", "Required level"), COLOR_DIM)
		self.nameLabel = self.__MakeLabel(panel, F_LABEL_X, F_NAME_LABEL_Y, FILTER_W,
			_L("GUILD_FINDER_FILTER_NAME", "Guild name"), COLOR_DIM)

		self.levelEditBg, self.levelEdit = self.__MakeEdit(panel, F_LEVEL_CTRL_Y, 3, True,
			self.__OnLevelFilterUpdate)
		self.nameEditBg, self.nameEdit = self.__MakeEdit(panel, F_NAME_CTRL_Y, 12, False,
			self.__OnNameFilterUpdate)

		btnRefresh = ui.Button()
		btnRefresh.SetParent(panel)
		btnRefresh.SetPosition(int(_LayoutX(REFRESH_X, REFRESH_W, FILTER_W)), int(REFRESH_Y))
		btnRefresh.SetUpVisual(BTN_ACTION_UP)
		btnRefresh.SetOverVisual(BTN_ACTION_OVER)
		btnRefresh.SetDownVisual(BTN_ACTION_DOWN)
		btnRefresh.SetDisableVisual(BTN_ACTION_DISABLE)
		btnRefresh.SetText(_L("GUILD_FINDER_BTN_REFRESH", "Refresh"))
		btnRefresh.SetEvent(ui.__mem_func__(self.__OnClickRefresh))
		btnRefresh.Show()
		self.btnRefresh = btnRefresh

		# built last so the dropped filter lists order above the widgets under them
		self.typeCombo = self.__MakeCombo(panel, F_TYPE_CTRL_Y, _TYPE_FILTERS, self.__OnTypeCombo)
		self.empireCombo = self.__MakeCombo(panel, F_EMPIRE_CTRL_Y, _EMPIRE_FILTERS, self.__OnEmpireCombo)

	def __MakeCombo(self, parent, y, spec, handler, xLtr = F_CTRL_X, w = F_CTRL_W, parentW = FILTER_W):
		combo = ui.ComboBoxNew()
		combo.SetParent(parent)
		combo.SetPosition(int(_LayoutX(xLtr, w, parentW)), int(y))
		combo.SetSize(int(w), int(F_CTRL_H))
		combo.SetEventNew(ui.__mem_func__(handler))
		for index, item in enumerate(spec):
			combo.InsertItem2(index, _L(item[1], item[2]))
		combo.SetCurrentItem(_L(spec[0][1], spec[0][2]))
		combo.Show()
		return combo

	def __MakeEdit(self, parent, y, maxLen, numberMode, handler,
			xLtr = F_CTRL_X, w = F_CTRL_W, parentW = FILTER_W, editW = F_EDIT_W):
		bg = ui.ImageBox()
		bg.SetParent(parent)
		bg.AddFlag("not_pick")
		bg.SetPosition(int(_LayoutX(xLtr, w, parentW)), int(y))
		bg.LoadImage(IMG_EDIT_BG)
		bg.Show()

		edit = ui.EditLine()
		edit.SetParent(parent)
		edit.SetPosition(int(_LayoutX(xLtr + F_EDIT_INSET_X, editW, parentW)),
			int(y + F_EDIT_INSET_Y))
		edit.SetSize(int(editW), int(F_EDIT_H))
		edit.SetMax(maxLen)
		if numberMode:
			edit.SetNumberMode()
		edit.SetEscapeEvent(ui.__mem_func__(self.Close))
		if handler:
			edit.SetUpdateEvent(ui.__mem_func__(handler))
		edit.Show()
		return bg, edit

	def __BuildListPanel(self):
		panel, bg = self.__MakePanel(LIST_X, LIST_W, IMG_LIST_BG)
		self.listPanel = panel
		self.listBg = bg

		titleImg = ui.ImageBox()
		titleImg.SetParent(panel)
		titleImg.AddFlag("not_pick")
		titleImg.SetPosition(int(_LayoutX(LIST_TITLE_X, LIST_TITLE_W, LIST_W)), int(LIST_TITLE_Y))
		titleImg.LoadImage(IMG_LIST_TITLE)
		titleImg.Show()
		self.listTitleImg = titleImg

		headerSpec = (
			(COL_MARK_X, COL_NAME_W, "GUILD_FINDER_COL_NAME", "Guild"),
			(COL_LEVEL_X, COL_LEVEL_W, "GUILD_FINDER_COL_LEVEL", "Lv"),
			(COL_MEMBERS_X, COL_MEMBERS_W, "GUILD_FINDER_COL_MEMBERS", "Members"),
			(COL_EMPIRE_X, COL_EMPIRE_W, "GUILD_FINDER_COL_EMPIRE", "Kingdom"),
		)
		self.headerLines = []
		for xLtr, w, key, default in headerSpec:
			line = ui.TextLine()
			line.SetParent(panel)
			line.AddFlag("not_pick")
			line.SetPosition(int(_LayoutX(ROW_X + xLtr, 0, LIST_W)), int(STRIP_TEXT_Y))
			if IS_AR:
				line.SetHorizontalAlignLeft()
			line.SetPackedFontColor(COLOR_TITLE)
			line.SetText(_L(key, default))
			line.Show()
			self.headerLines.append(line)

		self.rows = []
		for index in xrange(PAGE_SIZE):
			row = _GuildRow()
			row.SetParent(panel)
			row.SetPosition(int(_LayoutX(ROW_X, ROW_W, LIST_W)), int(ROW_Y0 + index * ROW_STEP))
			row.SetRowEvent(ui.__mem_func__(self.__OnClickRow))
			row.Hide()
			self.rows.append(row)

		empty = ui.TextLine()
		empty.SetParent(panel)
		empty.AddFlag("not_pick")
		empty.SetWindowHorizontalAlignCenter()
		empty.SetHorizontalAlignCenter()
		empty.SetPosition(0, int(ROW_Y0 + 100))
		empty.SetPackedFontColor(COLOR_DIM)
		empty.SetText(_L("GUILD_FINDER_NO_RESULTS", "No guilds match your filters."))
		empty.Hide()
		self.emptyLine = empty

		prevGlyph, nextGlyph = ("<", ">")
		if IS_AR:
			prevGlyph, nextGlyph = (">", "<")
		self.btnPrevPage = self.__MakePageButton(panel, prevGlyph, self.__OnClickPrevPage)
		self.pageButtons = []
		for index in xrange(PAGER_SLOTS):
			self.pageButtons.append(self.__MakePageButton(panel, "%d" % (index + 1), None))
		self.btnNextPage = self.__MakePageButton(panel, nextGlyph, self.__OnClickNextPage)

	def __MakePageButton(self, parent, text, handler):
		btn = ui.Button()
		btn.SetParent(parent)
		btn.SetPosition(0, int(PAGER_Y))
		btn.SetUpVisual(PAGE_ART + BTN_PAGE_UP)
		btn.SetOverVisual(PAGE_ART + BTN_PAGE_OVER)
		btn.SetDownVisual(PAGE_ART + BTN_PAGE_DOWN)
		btn.SetDisableVisual(PAGE_ART + BTN_PAGE_DOWN)
		btn.SetText(text)
		if handler:
			btn.SetEvent(ui.__mem_func__(handler))
		btn.Hide()
		return btn

	def __BuildDetailPanel(self):
		panel, bg = self.__MakePanel(DETAIL_X, DETAIL_W, IMG_DETAIL_BG)
		self.detailPanel = panel
		self.detailBg = bg

		self.detailTitle = self.__MakeCenteredLine(panel, STRIP_TEXT_Y, COLOR_TITLE)
		self.detailTitle.SetText(_L("GUILD_FINDER_DETAILS_TITLE", "Guild Details"))

		mark = ui.MarkBox()
		mark.SetParent(panel)
		mark.AddFlag("not_pick")
		mark.SetPosition(int(D_MARK_X), int(D_MARK_Y))
		mark.SetScale(D_MARK_SCALE)
		mark.Hide()
		self.detailMark = mark

		self.detailName = self.__MakeBoxLine(panel, D_BOX_X, D_BOX_W, D_NAME_Y, COLOR_TITLE)
		self.detailLevel = self.__MakeBoxLine(panel, D_BOX_X, D_BOX_W, D_LEVEL_Y, COLOR_TEXT)

		flag = ui.ImageBox()
		flag.SetParent(panel)
		flag.AddFlag("not_pick")
		flag.SetPosition(int(D_FLAG_X), int(D_FLAG_Y))
		flag.Hide()
		self.detailFlag = flag

		self.detailMembersLine = self.__MakeBoxLine(panel, D_ROW_X, D_ROW_W, D_MEMBERS_Y, COLOR_TEXT)
		self.detailOnlineLine = self.__MakeBoxLine(panel, D_ROW_X, D_ROW_W, D_ONLINE_Y, COLOR_TEXT)
		self.detailReqLine = self.__MakeBoxLine(panel, D_ROW_X, D_ROW_W, D_REQ_Y, COLOR_TEXT)

		self.detailLeaderLine = self.__MakeDescLine(panel, D_DESC_TEXT_Y, COLOR_DIM)
		self.detailDescLines = []
		for index in xrange(D_DESC_LINES):
			self.detailDescLines.append(self.__MakeDescLine(panel,
				D_DESC_TEXT_Y + (index + 1) * D_DESC_LINE_STEP, COLOR_TEXT))

		btn = ui.Button()
		btn.SetParent(panel)
		btn.SetPosition(int(D_BTN_X), int(D_BTN_Y))
		btn.SetUpVisual(BTN_ACTION_UP)
		btn.SetOverVisual(BTN_ACTION_OVER)
		btn.SetDownVisual(BTN_ACTION_DOWN)
		btn.SetDisableVisual(BTN_ACTION_DISABLE)
		btn.SetEvent(ui.__mem_func__(self.__OnClickAction))
		btn.Show()
		self.btnAction = btn

	def __MakeCenteredLine(self, parent, y, color):
		line = ui.TextLine()
		line.SetParent(parent)
		line.AddFlag("not_pick")
		line.SetWindowHorizontalAlignCenter()
		line.SetHorizontalAlignCenter()
		line.SetPosition(0, int(y))
		line.SetPackedFontColor(color)
		line.Show()
		return line

	# details_bg.png is an asymmetric image and does not mirror, so nothing anchored
	# to one of its frames may be laid out through _LayoutX
	def __MakeBoxLine(self, parent, x, w, y, color):
		line = ui.TextLine()
		line.SetParent(parent)
		line.AddFlag("not_pick")
		line.SetHorizontalAlignCenter()
		line.SetPosition(int(x + w // 2), int(y + D_BOX_TEXT_DY))
		line.SetPackedFontColor(color)
		line.Show()
		return line

	def __MakeDescLine(self, parent, y, color):
		line = ui.TextLine()
		line.SetParent(parent)
		line.AddFlag("not_pick")
		x = D_DESC_TEXT_X
		if IS_AR:
			# Arabic anchors a line at its reading start, i.e. the box's right edge
			x = D_DESC_X + D_DESC_W - (D_DESC_TEXT_X - D_DESC_X)
			line.SetHorizontalAlignLeft()
		line.SetPosition(int(x), int(y))
		line.SetPackedFontColor(color)
		line.Hide()
		return line

	def __BuildSettingsPanel(self):
		panel, bg = self.__MakePanel(SET_X, SET_W, IMG_FILTER_BG)
		self.setPanel = panel
		self.setBg = bg

		self.setTitle = self.__MakeCenteredLine(panel, STRIP_TEXT_Y, COLOR_TITLE)
		self.setTitle.SetText(_L("GUILD_FINDER_SETTINGS_TITLE", "Recruitment"))

		self.setModeLabel = self.__MakeLabel(panel, F_LABEL_X, S_MODE_LABEL_Y, SET_W,
			_L("GUILD_FINDER_SETTINGS_MODE", "Mode"), COLOR_DIM)
		self.setLevelLabel = self.__MakeLabel(panel, F_LABEL_X, S_LEVEL_LABEL_Y, SET_W,
			_L("GUILD_FINDER_SETTINGS_MIN_LEVEL", "Minimum level"), COLOR_DIM)
		self.setDescLabel = self.__MakeLabel(panel, F_LABEL_X, S_DESC_LABEL_Y, SET_W,
			_L("GUILD_FINDER_SETTINGS_DESC", "Description"), COLOR_DIM)

		self.setLevelEditBg, self.setLevelEdit = self.__MakeEdit(panel, S_LEVEL_CTRL_Y, 3, True, None)

		descBg = ui.ImageBox()
		descBg.SetParent(panel)
		descBg.AddFlag("not_pick")
		descBg.SetPosition(int(_LayoutX(S_DESC_BOX_X, S_DESC_BOX_W, SET_W)), int(S_DESC_BOX_Y))
		descBg.LoadImage(IMG_DESC_BG)
		descBg.Show()
		self.setDescBg = descBg

		descEdit = ui.EditLine()
		descEdit.SetParent(panel)
		descEdit.SetPosition(int(_LayoutX(S_DESC_EDIT_X, S_DESC_EDIT_W, SET_W)), int(S_DESC_EDIT_Y))
		descEdit.SetSize(int(S_DESC_EDIT_W), int(S_DESC_EDIT_H))
		descEdit.SetMax(DESC_MAX_LEN)
		descEdit.SetLimitWidth(int(S_DESC_EDIT_W - 4))
		descEdit.SetMultiLine()
		descEdit.SetEscapeEvent(ui.__mem_func__(self.Close))
		descEdit.SetUpdateEvent(ui.__mem_func__(self.__OnDescUpdate))
		descEdit.Show()
		self.setDescEdit = descEdit

		self.setDescCount = self.__MakeCenteredLine(panel, S_COUNT_Y, COLOR_DIM)

		btnSave = ui.Button()
		btnSave.SetParent(panel)
		btnSave.SetPosition(int(_LayoutX(S_SAVE_X, S_SAVE_W, SET_W)), int(S_SAVE_Y))
		btnSave.SetUpVisual(BTN_ACTION_UP)
		btnSave.SetOverVisual(BTN_ACTION_OVER)
		btnSave.SetDownVisual(BTN_ACTION_DOWN)
		btnSave.SetDisableVisual(BTN_ACTION_DISABLE)
		btnSave.SetText(_L("GUILD_FINDER_SETTINGS_SAVE", "Save"))
		btnSave.SetEvent(ui.__mem_func__(self.__OnClickSaveSettings))
		btnSave.Show()
		self.btnSaveSettings = btnSave

		# built last so the dropped mode list orders above the widgets under it
		self.setModeCombo = self.__MakeCombo(panel, S_MODE_CTRL_Y, _MODE_ITEMS, self.__OnModeCombo,
			F_CTRL_X, F_CTRL_W, SET_W)

		self.__RefreshDescCounter()
		panel.Hide()

	def __BuildInboxPanel(self):
		panel, bg = self.__MakePanel(APPS_X, APPS_W, IMG_APPS_BG)
		self.inboxPanel = panel
		self.inboxBg = bg

		self.inboxTitleImg = self.__MakeStrip(panel, A_HEAD1_Y)
		self.inboxTitle = self.__MakeLabel(panel, A_HEAD_TEXT_X, A_HEAD1_Y + A_HEAD_TEXT_DY, APPS_W,
			_L("GUILD_FINDER_INBOX_TITLE", "Applications"), COLOR_TITLE)

		prevGlyph, nextGlyph = ("<", ">")
		if IS_AR:
			prevGlyph, nextGlyph = (">", "<")
		self.btnAppPrev = self.__MakeAppPageButton(panel, A_PAGER_PREV_X, prevGlyph, self.__OnClickAppPrev)
		self.btnAppNext = self.__MakeAppPageButton(panel, A_PAGER_NEXT_X, nextGlyph, self.__OnClickAppNext)
		self.appPageLine = self.__MakeLabel(panel, A_PAGER_LABEL_X, A_PAGER_Y + A_HEAD_TEXT_DY, APPS_W,
			"", COLOR_DIM)

		self.appRows = []
		for index in xrange(A_PAGE_SIZE):
			row = _ApplicantRow()
			row.SetParent(panel)
			row.SetPosition(int(_LayoutX(A_ROW_X, A_ROW_W, APPS_W)), int(A_ROW_Y0 + index * A_ROW_STEP))
			row.SetAnswerEvent(ui.__mem_func__(self.__OnAnswerApplicant))
			row.Hide()
			self.appRows.append(row)

		empty = ui.TextLine()
		empty.SetParent(panel)
		empty.AddFlag("not_pick")
		empty.SetWindowHorizontalAlignCenter()
		empty.SetHorizontalAlignCenter()
		empty.SetPosition(0, int(A_EMPTY_Y))
		empty.SetPackedFontColor(COLOR_DIM)
		empty.SetText(_L("GUILD_FINDER_INBOX_EMPTY", "No applications right now."))
		empty.Hide()
		self.appEmptyLine = empty

		self.__RefreshApplicantRows()
		panel.Hide()

	def __MakeStrip(self, parent, y):
		strip = ui.ImageBox()
		strip.SetParent(parent)
		strip.AddFlag("not_pick")
		strip.SetPosition(int(_LayoutX(A_STRIP_X, A_STRIP_W, APPS_W)), int(y))
		strip.LoadImage(IMG_APPS_TITLE)
		strip.Show()
		return strip

	def __MakeAppPageButton(self, parent, xLtr, text, handler):
		btn = ui.Button()
		btn.SetParent(parent)
		btn.SetPosition(int(_LayoutX(xLtr, A_PAGER_BTN_W, APPS_W)), int(A_PAGER_Y))
		btn.SetUpVisual(PAGE_ART + BTN_PAGE_UP)
		btn.SetOverVisual(PAGE_ART + BTN_PAGE_OVER)
		btn.SetDownVisual(PAGE_ART + BTN_PAGE_DOWN)
		btn.SetDisableVisual(PAGE_ART + BTN_PAGE_DOWN)
		btn.SetText(text)
		btn.SetEvent(ui.__mem_func__(handler))
		btn.Hide()
		return btn

	def __BuildNotice(self):
		panel = _NoticePanel()
		panel.SetParent(self.content)
		panel.SetPosition(int(NOTIF_X), int(NOTIF_Y))
		panel.Hide()
		self.noticePanel = panel

		bg = ui.ImageBox()
		bg.SetParent(panel)
		bg.AddFlag("not_pick")
		bg.SetPosition(0, 0)
		bg.LoadImage(IMG_NOTIF_BG)
		bg.Show()
		self.noticeBg = bg

		self.noticeLines = []
		for index in xrange(NOTIF_LINES):
			line = ui.TextLine()
			line.SetParent(panel)
			line.AddFlag("not_pick")
			line.SetWindowHorizontalAlignCenter()
			line.SetHorizontalAlignCenter()
			line.SetPosition(0, int(NOTIF_H // 2 - 20 + index * NOTIF_LINE_STEP))
			line.SetPackedFontColor(COLOR_TEXT)
			line.Hide()
			self.noticeLines.append(line)

	# ---- lifecycle ----------------------------------------------------------

	def Open(self):
		self.Show()
		self.SetTop()

	def Close(self):
		self.Hide()

	def Show(self):
		ui.ScriptWindow.Show(self)
		self.__RefreshAppsTabAvailability()
		# Reopening the window must not defeat the list cooldown.
		if self.refreshReadyTime <= 0.0 or app.GetTime() >= self.refreshReadyTime:
			net.SendGuildFinderListRequest()
			self.__StartRefreshCooldown()
		if self.currentTab == TAB_APPS:
			self.__ClearBadge()

	def Hide(self):
		notice = getattr(self, "noticePanel", None)
		if notice:
			notice.Hide()
		self.noticeHideTime = 0.0
		self.closeAfterNotice = False
		self.inboxRefreshTime = 0.0
		self.__ReleaseInputs(BROWSE_COMBOS + APPS_COMBOS, BROWSE_EDITS + APPS_EDITS)
		ui.ScriptWindow.Hide(self)

	def __ReleaseInputs(self, comboNames, editNames):
		# a hidden EditLine keeps keyboard focus and still fires its escape event,
		# so every path that hides a panel has to release its inputs
		for name in comboNames:
			combo = getattr(self, name, None)
			if combo:
				combo.CloseListBox()
		for name in editNames:
			edit = getattr(self, name, None)
			if edit:
				edit.KillFocus()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnUpdate(self):
		btnRefresh = getattr(self, "btnRefresh", None)
		if not btnRefresh:
			return
		now = app.GetTime()
		readyTime = getattr(self, "refreshReadyTime", 0.0)
		if readyTime > 0.0 and now >= readyTime:
			self.refreshReadyTime = 0.0
			btnRefresh.Enable()
			btnRefresh.SetUp()
		manageTime = getattr(self, "manageReadyTime", 0.0)
		if manageTime > 0.0 and now >= manageTime:
			self.manageReadyTime = 0.0
			self.__RefreshManageControls()

		detailTime = getattr(self, "detailReadyTime", 0.0)
		if detailTime > 0.0 and now >= detailTime:
			self.detailReadyTime = 0.0
			pendingGid = getattr(self, "detailPendingGid", 0)
			if pendingGid:
				self.__RequestDetail(pendingGid)

		dueTime = getattr(self, "inboxRefreshTime", 0.0)
		if dueTime > 0.0 and now >= dueTime:
			self.inboxRefreshTime = 0.0
			if self.__IsApplicationsVisible():
				self.__RequestInbox()

		hideTime = getattr(self, "noticeHideTime", 0.0)
		if hideTime > 0.0 and now >= hideTime:
			self.noticeHideTime = 0.0
			notice = getattr(self, "noticePanel", None)
			if notice:
				notice.Hide()
			if getattr(self, "closeAfterNotice", False):
				self.closeAfterNotice = False
				self.Close()

	# ---- tabs ---------------------------------------------------------------

	def OpenApplicationsTab(self):
		self.Open()
		if self.__CanManageApplications():
			self.__SelectTab(TAB_APPS)

	def __CanManageApplications(self):
		# mirrors GFHasManageAuth (game/guild_finder.cpp): master, or a grade carrying
		# the invite bit. Grade + member data arrive with SendAllGradePacket/SendListPacket
		# at guild login, so this answers correctly without opening the guild window.
		if guild.GetGuildID() == 0:
			return False
		if guild.GetGuildMasterName() == player.GetMainCharacterName():
			return True
		return guild.MainPlayerHasAuthority(guild.AUTH_ADD_MEMBER) != 0

	def __RefreshAppsTabAvailability(self):
		btn = getattr(self, "btnTabApps", None)
		if not btn:
			return
		if self.__CanManageApplications():
			btn.Show()
		else:
			btn.Hide()
			if getattr(self, "currentTab", TAB_BROWSE) != TAB_BROWSE:
				self.__SelectTab(TAB_BROWSE)

	def __OnClickTabGuilds(self):
		self.__SelectTab(TAB_BROWSE)

	def __OnClickTabApps(self):
		if not self.__CanManageApplications():
			return
		self.__SelectTab(TAB_APPS)

	def __SelectTab(self, tab):
		if tab == TAB_APPS and not self.__CanManageApplications():
			tab = TAB_BROWSE
		self.currentTab = tab
		browse = (tab == TAB_BROWSE)

		self.__SetTabVisual(self.btnTabGuilds, TAB_GUILD_UP, TAB_GUILD_OVER, TAB_GUILD_DOWN, browse)
		self.__SetTabVisual(self.btnTabApps, TAB_APPLY_UP, TAB_APPLY_OVER, TAB_APPLY_DOWN, not browse)

		if browse:
			self.__ReleaseInputs(APPS_COMBOS, APPS_EDITS)
		else:
			self.__ReleaseInputs(BROWSE_COMBOS, BROWSE_EDITS)

		for panel in (self.filterPanel, self.listPanel, self.detailPanel):
			if not panel:
				continue
			if browse:
				panel.Show()
			else:
				panel.Hide()
		for panel in (self.setPanel, self.inboxPanel):
			if not panel:
				continue
			if browse:
				panel.Hide()
			else:
				panel.Show()

		if not browse:
			self.__ClearBadge()
			self.__RequestInbox()

	def __SetTabVisual(self, btn, up, over, down, active):
		if not btn:
			return
		if active:
			btn.SetUpVisual(down)
			btn.SetOverVisual(down)
		else:
			btn.SetUpVisual(up)
			btn.SetOverVisual(over)
		btn.SetDownVisual(down)
		btn.SetUp()

	# ---- refresh ------------------------------------------------------------

	def __StartRefreshCooldown(self):
		btnRefresh = getattr(self, "btnRefresh", None)
		if not btnRefresh:
			return
		self.refreshReadyTime = app.GetTime() + LIST_COOLDOWN_SEC
		btnRefresh.Disable()

	def __OnClickRefresh(self):
		if getattr(self, "refreshReadyTime", 0.0) > 0.0:
			return
		net.SendGuildFinderListRequest()
		self.__StartRefreshCooldown()

	# ---- filters ------------------------------------------------------------

	def __OnTypeCombo(self, wnd, index, name):
		wnd.SetCurrentItem(name)
		self.filterMode = _TYPE_FILTERS[index][0]
		self.__ApplyFilters()

	def __OnEmpireCombo(self, wnd, index, name):
		wnd.SetCurrentItem(name)
		self.filterEmpire = _EMPIRE_FILTERS[index][0]
		self.__ApplyFilters()

	def __OnLevelFilterUpdate(self):
		edit = getattr(self, "levelEdit", None)
		if not edit:
			return
		text = edit.GetText().strip()
		if text.isdigit():
			self.filterMaxReqLevel = int(text)
		else:
			self.filterMaxReqLevel = 0
		self.__ApplyFilters()

	def __OnNameFilterUpdate(self):
		edit = getattr(self, "nameEdit", None)
		if not edit:
			return
		self.filterName = edit.GetText().strip().lower()
		self.__ApplyFilters()

	def __PassesFilters(self, entry):
		if self.filterMode != FILTER_ALL and entry[6] != self.filterMode:
			return False
		if self.filterEmpire != FILTER_ALL and entry[5] != self.filterEmpire:
			return False
		if self.filterMaxReqLevel > 0 and entry[7] > self.filterMaxReqLevel:
			return False
		if self.filterName and entry[1].lower().find(self.filterName) < 0:
			return False
		return True

	def __ApplyFilters(self):
		# List comprehension keeps the server's best-first ordering intact.
		self.filtered = [entry for entry in self.entries if self.__PassesFilters(entry)]
		self.pageCount = max(1, (len(self.filtered) + PAGE_SIZE - 1) // PAGE_SIZE)
		if self.currentPage > self.pageCount:
			self.currentPage = self.pageCount
		if self.currentPage < 1:
			self.currentPage = 1
		self.__RefreshRows()
		self.__RefreshPagination()

	# ---- list ---------------------------------------------------------------

	def __RefreshRows(self):
		if not self.rows:
			return
		start = (self.currentPage - 1) * PAGE_SIZE
		page = self.filtered[start:start + PAGE_SIZE]
		for index, row in enumerate(self.rows):
			if index < len(page):
				row.SetData(page[index])
				row.SetSelected(page[index][0] == self.selectedGid)
				row.Show()
			else:
				row.SetSelected(False)
				row.Hide()
		if self.emptyLine:
			if page:
				self.emptyLine.Hide()
			else:
				self.emptyLine.Show()

	def __RefreshPagination(self):
		if not self.pageButtons:
			return
		self.paginationGroup = (self.currentPage + PAGER_SLOTS - 1) // PAGER_SLOTS
		remaining = self.pageCount - (PAGER_SLOTS * (self.paginationGroup - 1))
		self.shownPages = max(1, min(remaining, PAGER_SLOTS))

		for index in xrange(PAGER_SLOTS):
			pageNumber = index + ((self.paginationGroup - 1) * PAGER_SLOTS) + 1
			btn = self.pageButtons[index]
			btn.SetUp()
			btn.Enable()
			btn.SetText("%d" % pageNumber)
			btn.SetEvent(ui.__mem_func__(self.__GotoPage), pageNumber)
			btn.Hide()

		for index in xrange(self.shownPages):
			self.pageButtons[index].Show()

		activeSlot = (self.currentPage - ((self.paginationGroup - 1) * PAGER_SLOTS)) - 1
		if 0 <= activeSlot < PAGER_SLOTS:
			self.pageButtons[activeSlot].Down()
			self.pageButtons[activeSlot].Disable()

		total = (self.shownPages + 2) * PAGER_STEP
		startX = int((LIST_W - total) // 2)
		order = [self.btnPrevPage]
		for index in xrange(self.shownPages):
			order.append(self.pageButtons[index])
		order.append(self.btnNextPage)
		if IS_AR:
			order.reverse()
		posX = startX
		for btn in order:
			btn.SetPosition(int(posX), int(PAGER_Y))
			posX += PAGER_STEP

		if self.pageCount > 1:
			self.btnPrevPage.Show()
			self.btnNextPage.Show()
		else:
			self.btnPrevPage.Hide()
			self.btnNextPage.Hide()

	def __GotoPage(self, page):
		if page < 1:
			page = 1
		if page > self.pageCount:
			page = self.pageCount
		self.currentPage = page
		self.__RefreshRows()
		self.__RefreshPagination()

	def __OnClickPrevPage(self):
		self.__GotoPage(self.currentPage - 1)

	def __OnClickNextPage(self):
		self.__GotoPage(self.currentPage + 1)

	def __OnClickRow(self, guildID):
		if not guildID:
			return
		if guildID != self.selectedGid:
			self.selectedGid = guildID
			self.__RefreshRows()
		# re-clicking the row whose detail is already loaded must not cost a db round-trip
		if guildID == self.detailGid:
			self.detailPendingGid = 0
			return
		self.__RequestDetail(guildID)

	# DETAIL_REQ carries its own GF_DETAIL_COOLDOWN_MS clock server-side (guild_finder.cpp)
	# and a send inside it is dropped with no reply, so hold the newest pick and fire it when
	# the clock expires instead of leaving the panel on the previously selected guild
	def __RequestDetail(self, guildID):
		now = app.GetTime()
		readyTime = getattr(self, "detailReadyTime", 0.0)
		if readyTime > 0.0 and now < readyTime:
			self.detailPendingGid = guildID
			return
		self.detailPendingGid = 0
		self.detailReadyTime = now + DETAIL_COOLDOWN_SEC
		net.SendGuildFinderDetailRequest(guildID)

	def __FindEntry(self, guildID):
		for entry in self.entries:
			if entry[0] == guildID:
				return entry
		return None

	# ---- details ------------------------------------------------------------

	def __SplitLongWord(self, word, maxPixels):
		measure = self.measureLine
		measure.SetText(word)
		if measure.GetTextSize()[0] <= maxPixels:
			return [word]
		parts = []
		current = ""
		for char in word:
			measure.SetText(current + char)
			if current and measure.GetTextSize()[0] > maxPixels:
				parts.append(current)
				current = char
			else:
				current += char
		if current:
			parts.append(current)
		return parts

	def __WrapText(self, text, maxPixels, maxLines):
		measure = getattr(self, "measureLine", None)
		if not measure or not text:
			return []
		words = []
		for word in text.split(" "):
			words.extend(self.__SplitLongWord(word, maxPixels))
		lines = []
		current = ""
		for word in words:
			trial = word if not current else (current + " " + word)
			measure.SetText(trial)
			if current and measure.GetTextSize()[0] > maxPixels:
				lines.append(current)
				if len(lines) >= maxLines:
					lines[-1] = lines[-1] + ELLIPSIS
					return lines
				current = word
			else:
				current = trial
		if current and len(lines) < maxLines:
			lines.append(current)
		return lines

	def __RefreshDetails(self):
		if not self.detailPanel:
			return
		entry = self.__FindEntry(self.detailGid)

		if entry:
			self.detailMark.SetIndex(entry[0])
			self.detailMark.Show()
			self.detailName.SetText(entry[1])
			self.detailLevel.SetText("%s %d" % (_L("GUILD_FINDER_COL_LEVEL", "Lv"), entry[2]))
			self.detailReqLine.SetText("%s %d" % (_L("GUILD_FINDER_DETAIL_REQ_LEVEL", "Required level"), entry[7]))
			image = IMG_EMPIRE.get(entry[5])
			if image:
				self.detailFlag.LoadImage(image)
				self.detailFlag.Show()
			else:
				self.detailFlag.Hide()
		else:
			self.detailMark.Hide()
			self.detailName.SetText("")
			self.detailLevel.SetText("")
			self.detailReqLine.SetText("")
			self.detailFlag.Hide()

		if self.detailLeader:
			self.detailLeaderLine.SetText("%s %s" % (
				_L("GUILD_FINDER_DETAIL_LEADER", "Leader"), self.detailLeader))
			self.detailLeaderLine.Show()
		else:
			self.detailLeaderLine.SetText("")
			self.detailLeaderLine.Hide()

		if self.detailGid:
			self.detailMembersLine.SetText("%s %d/%d" % (
				_L("GUILD_FINDER_DETAIL_MEMBERS", "Members"), self.detailMembers, self.detailMax))
			self.detailOnlineLine.SetText("%s %d" % (
				_L("GUILD_FINDER_DETAIL_ONLINE", "Online"), self.detailOnline))
		else:
			self.detailMembersLine.SetText("")
			self.detailOnlineLine.SetText("")

		wrapped = self.__WrapText(self.detailDesc, D_DESC_TEXT_W, D_DESC_LINES)
		for index, line in enumerate(self.detailDescLines):
			if index < len(wrapped):
				line.SetText(wrapped[index])
				line.Show()
			else:
				line.SetText("")
				line.Hide()

		self.__RefreshActionButton()

	def __RefreshActionButton(self):
		btn = getattr(self, "btnAction", None)
		if not btn:
			return

		entry = self.__FindEntry(self.detailGid)
		if not entry:
			self.actionMode = None
			btn.SetText("")
			btn.Disable()
			return

		applied = self.detailGid in self.myAppGids
		hasGuild = guild.GetGuildID() != 0
		myLevel = player.GetStatus(player.LEVEL)
		myEmpire = net.GetEmpireID()
		mode = entry[6]

		if applied:
			self.actionMode = "cancel"
			btn.SetText(_L("GUILD_FINDER_BTN_APPLIED_CANCEL", "Applied - cancel"))
			btn.Enable()
			btn.SetUp()
			return

		self.actionMode = None
		if hasGuild:
			btn.SetText(_L("GUILD_FINDER_BTN_HAS_GUILD", "Already in a guild"))
		elif entry[5] != myEmpire:
			btn.SetText(_L("GUILD_FINDER_BTN_WRONG_EMPIRE", "Different kingdom"))
		elif mode == MODE_CLOSED:
			btn.SetText(_L("GUILD_FINDER_BTN_CLOSED", "Not recruiting"))
		elif myLevel < entry[7]:
			btn.SetText(_L("GUILD_FINDER_BTN_LEVEL_LOW", "Level too low"))
		elif entry[4] > 0 and entry[3] >= entry[4]:
			btn.SetText(_L("GUILD_FINDER_BTN_FULL", "Guild is full"))
		elif mode == MODE_OPEN:
			self.actionMode = "join"
			btn.SetText(_L("GUILD_FINDER_BTN_JOIN", "Join"))
		elif mode == MODE_APPROVAL:
			self.actionMode = "apply"
			btn.SetText(_L("GUILD_FINDER_BTN_APPLY", "Apply"))
		else:
			btn.SetText(_L("GUILD_FINDER_BTN_CLOSED", "Not recruiting"))

		if self.actionMode:
			btn.Enable()
			btn.SetUp()
		else:
			btn.Disable()

	def __OnClickAction(self):
		mode = getattr(self, "actionMode", None)
		guildID = getattr(self, "detailGid", 0)
		if not mode or not guildID:
			return
		if mode == "join":
			net.SendGuildFinderJoin(guildID)
		elif mode == "apply":
			net.SendGuildFinderApply(guildID)
		elif mode == "cancel":
			net.SendGuildFinderCancel(guildID)

	# ---- applications -------------------------------------------------------

	def __ClearBadge(self):
		uibadge.SetCount("guild_finder", 0)

	# ANSWER, SETTINGS and INBOX_REQ share one GF_MANAGE_COOLDOWN_MS clock server-side
	# (guild_finder.cpp), and a send inside it is dropped with no reply at all. Sending
	# anyway would leave pendingAnswers correlated against a result that never comes, so
	# the client holds the same clock and never issues a manage packet it cannot pair.
	def __ManageReadyIn(self):
		readyTime = getattr(self, "manageReadyTime", 0.0)
		if readyTime <= 0.0:
			return 0.0
		remain = readyTime - app.GetTime()
		if remain <= 0.0:
			return 0.0
		return remain

	def __NoteManageSent(self):
		self.manageReadyTime = app.GetTime() + MANAGE_COOLDOWN_SEC
		self.__RefreshManageControls()

	def __RefreshManageControls(self):
		enabled = self.__ManageReadyIn() <= 0.0
		btnSave = getattr(self, "btnSaveSettings", None)
		if btnSave:
			if enabled:
				btnSave.Enable()
				btnSave.SetUp()
			else:
				btnSave.Disable()
		for row in getattr(self, "appRows", None) or []:
			row.SetAnswerEnabled(enabled)

	def __ShowCooldownNotice(self):
		self.__ShowNotice(_L("GUILD_FINDER_ERR_COOLDOWN", "Please wait a moment before trying again."))

	def __RequestInbox(self):
		remain = self.__ManageReadyIn()
		if remain > 0.0:
			self.inboxRefreshTime = app.GetTime() + remain
			return
		self.inboxRefreshTime = 0.0
		net.SendGuildFinderInboxRequest()
		self.__NoteManageSent()

	def __IsApplicationsVisible(self):
		return self.IsShow() and getattr(self, "currentTab", TAB_BROWSE) == TAB_APPS

	def __OnModeCombo(self, wnd, index, name):
		wnd.SetCurrentItem(name)
		self.setMode = _MODE_ITEMS[index][0]

	def __OnDescUpdate(self):
		self.__RefreshDescCounter()

	def __RefreshDescCounter(self):
		label = getattr(self, "setDescCount", None)
		edit = getattr(self, "setDescEdit", None)
		if not label or not edit:
			return
		# GetText returns the client codepage bytes (CP1256 for the Arabic client),
		# which is exactly what the server counts against GF_DESC_MAX_LEN.
		used = len(edit.GetText())
		label.SetText("%d/%d" % (used, DESC_MAX_LEN))
		if used > DESC_MAX_LEN:
			label.SetPackedFontColor(COLOR_WARN)
		else:
			label.SetPackedFontColor(COLOR_DIM)

	def __RefreshSettingsWidgets(self):
		combo = getattr(self, "setModeCombo", None)
		if combo:
			label = None
			for item in _MODE_ITEMS:
				if item[0] == self.inboxMode:
					label = _L(item[1], item[2])
					break
			if label:
				combo.SetCurrentItem(label)
		self.setMode = self.inboxMode

		edit = getattr(self, "setLevelEdit", None)
		if edit:
			edit.SetText("%d" % self.inboxMinLevel)

		descEdit = getattr(self, "setDescEdit", None)
		if descEdit:
			descEdit.SetText(self.inboxDesc)
		self.__RefreshDescCounter()

	def __OnClickSaveSettings(self):
		edit = getattr(self, "setLevelEdit", None)
		descEdit = getattr(self, "setDescEdit", None)
		if not edit or not descEdit:
			return

		if self.__ManageReadyIn() > 0.0:
			self.__ShowCooldownNotice()
			return

		text = edit.GetText().strip()
		minLevel = 0
		if text.isdigit():
			minLevel = int(text)
		if minLevel < 0:
			minLevel = 0
		if minLevel > 255:
			minLevel = 255

		desc = descEdit.GetText()[:DESC_MAX_LEN]
		net.SendGuildFinderSettings(self.setMode, minLevel, desc)
		self.__NoteManageSent()

	def __RefreshApplicantRows(self):
		rows = getattr(self, "appRows", None)
		if not rows:
			return

		total = len(self.inboxApplicants)
		self.appsPageCount = max(1, (total + A_PAGE_SIZE - 1) // A_PAGE_SIZE)
		if self.appsPage > self.appsPageCount:
			self.appsPage = self.appsPageCount
		if self.appsPage < 1:
			self.appsPage = 1

		start = (self.appsPage - 1) * A_PAGE_SIZE
		page = self.inboxApplicants[start:start + A_PAGE_SIZE]
		for index, row in enumerate(rows):
			if index < len(page):
				row.SetData(page[index])
				row.Show()
			else:
				row.Hide()

		if self.appEmptyLine:
			if page:
				self.appEmptyLine.Hide()
			else:
				self.appEmptyLine.Show()

		if self.appPageLine:
			if self.appsPageCount > 1:
				self.appPageLine.SetText("%d/%d" % (self.appsPage, self.appsPageCount))
				self.appPageLine.Show()
			else:
				self.appPageLine.SetText("")
				self.appPageLine.Hide()

		for btn in (self.btnAppPrev, self.btnAppNext):
			if not btn:
				continue
			if self.appsPageCount > 1:
				btn.Show()
			else:
				btn.Hide()

		self.__RefreshManageControls()

	def __GotoAppPage(self, page):
		if page < 1:
			page = 1
		if page > self.appsPageCount:
			page = self.appsPageCount
		self.appsPage = page
		self.__RefreshApplicantRows()

	def __OnClickAppPrev(self):
		self.__GotoAppPage(self.appsPage - 1)

	def __OnClickAppNext(self):
		self.__GotoAppPage(self.appsPage + 1)

	def __DropApplicant(self, applicantPid):
		if not applicantPid:
			return
		self.inboxApplicants = [a for a in self.inboxApplicants if a[0] != applicantPid]
		self.__RefreshApplicantRows()

	def __ScheduleInboxRefresh(self):
		# arm it now; __RequestInbox defers itself while the manage cooldown holds
		self.inboxRefreshTime = app.GetTime()

	def __OnAnswerApplicant(self, applicantPid, accept):
		if not applicantPid:
			return
		if self.__ManageReadyIn() > 0.0:
			self.__ShowCooldownNotice()
			return
		# the row is removed when GF_OK confirms it, not on the click: the answer
		# survives GF_ERR_GUILD_FULL with the application still pending
		self.pendingAnswers.append(applicantPid)
		net.SendGuildFinderAnswer(applicantPid, accept)
		self.__NoteManageSent()

	# ---- notice -------------------------------------------------------------

	def __ShowNotice(self, text):
		panel = getattr(self, "noticePanel", None)
		if not panel or not text:
			return
		wrapped = self.__WrapText(text, NOTIF_TEXT_W, NOTIF_LINES)
		if not wrapped:
			wrapped = [text]
		for index, line in enumerate(self.noticeLines):
			if index < len(wrapped):
				line.SetText(wrapped[index])
				line.Show()
			else:
				line.SetText("")
				line.Hide()
		panel.Show()
		panel.SetTop()
		self.noticeHideTime = app.GetTime() + NOTIF_SHOW_SEC

	# ---- server callbacks ---------------------------------------------------

	def __ClearDetail(self):
		self.selectedGid = 0
		self.detailGid = 0
		self.detailPendingGid = 0
		self.detailLeader = ""
		self.detailMembers = 0
		self.detailMax = 0
		self.detailOnline = 0
		self.detailDesc = ""

	def OnList(self, entries, myAppGids):
		self.entries = list(entries)
		self.myAppGids = list(myAppGids)
		if self.selectedGid and not self.__FindEntry(self.selectedGid):
			self.__ClearDetail()
		self.currentPage = 1
		self.__ApplyFilters()
		self.__RefreshDetails()

	def OnDetail(self, guildID, leaderName, members, maxMembers, online, myApplied, desc):
		# a reply for a row the player has already clicked away from must not
		# repaint the panel that now belongs to a different guild
		if guildID != getattr(self, "selectedGid", 0):
			return
		self.detailGid = guildID
		self.detailLeader = leaderName
		self.detailMembers = members
		self.detailMax = maxMembers
		self.detailOnline = online
		self.detailDesc = desc
		if myApplied:
			if guildID not in self.myAppGids:
				self.myAppGids.append(guildID)
		elif guildID in self.myAppGids:
			self.myAppGids.remove(guildID)
		self.__RefreshDetails()

	def OnResult(self, guildID, result):
		text = RESULT_TEXT.get(result)
		if text:
			self.__ShowNotice(text)

		okAnswered = getattr(app, "GF_OK", None)
		okApplied = getattr(app, "GF_OK_APPLIED", None)
		okCanceled = getattr(app, "GF_OK_CANCELED", None)
		okJoined = getattr(app, "GF_OK_JOINED", None)
		errDup = getattr(app, "GF_ERR_DUP_APP", None)
		appAccepted = getattr(app, "GF_APP_ACCEPTED", None)
		appRejected = getattr(app, "GF_APP_REJECTED", None)

		# GF_OK is the only reply that means the application actually left the
		# server's inbox; every error path leaves it there for the next read
		if result == okAnswered and self.pendingAnswers:
			self.__DropApplicant(self.pendingAnswers.pop(0))
		elif self.pendingAnswers:
			self.pendingAnswers.pop(0)

		if result in (okApplied, errDup):
			if guildID and guildID not in self.myAppGids:
				self.myAppGids.append(guildID)
			self.__RefreshActionButton()
		elif result in (okCanceled, appRejected):
			if guildID in self.myAppGids:
				self.myAppGids.remove(guildID)
			self.__RefreshActionButton()
		elif result in (okJoined, appAccepted):
			self.myAppGids = []
			self.__ClearDetail()
			self.__RefreshActionButton()
			# the notice board is a child of this window, so closing now would
			# hide the confirmation with it; let the notice timer close instead
			if text and self.noticeHideTime > 0.0:
				self.closeAfterNotice = True
			else:
				self.Close()

	def OnInbox(self, guildID, mode, minLevel, desc, applicants):
		self.inboxGid = guildID
		self.inboxMode = mode
		self.inboxMinLevel = minLevel
		self.inboxDesc = desc
		self.inboxApplicants = list(applicants)
		self.pendingAnswers = []
		self.inboxRefreshTime = 0.0
		self.appsPage = 1
		self.__RefreshSettingsWidgets()
		self.__RefreshApplicantRows()
		if self.__IsApplicationsVisible():
			self.__ClearBadge()

	def OnBadge(self, count):
		# seen-clears: an open Applications tab means the player is already looking
		# at the inbox, so a fresh push must not raise the badge behind the window.
		# The server pushes a badge after every answer too, which makes this the
		# authoritative "the inbox changed" signal to reconcile the rows against.
		if self.__IsApplicationsVisible():
			self.__ClearBadge()
			self.__ScheduleInboxRefresh()
			return
		uibadge.SetCount("guild_finder", count)
