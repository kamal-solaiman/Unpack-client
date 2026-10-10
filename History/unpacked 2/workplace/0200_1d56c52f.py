# coding: latin_1

import app
import ui
import wndMgr
import net
import guild
import player
import messenger
import community
import localeinfo
import uiscriptlocale
import uitooltip
import uicommon
import uibadge

from _weakref import proxy


def _L(key, default):
	val = getattr(localeinfo, key, None)
	if val is None:
		val = getattr(uiscriptlocale, key, None)
	if val is None:
		return default
	return val


ROOT_PATH = "d:/ymir work/ui/game/windows/"
GAME_PATH = "d:/ymir work/ui/game/"
PUBLIC_PATH = "d:/ymir work/ui/public/"

MEMBER_INFO_BAR_BG = ROOT_PATH + "community_info_bar_default.sub"
MEMBER_INFO_BAR_HOVER = ROOT_PATH + "community_info_bar_mouse_over.sub"
FAMILY_INFO_BAR_BG = ROOT_PATH + "community_info_bar_family_default.sub"

SUB_TAB_FRIEND_IMG = ROOT_PATH + "community_friend_member.sub"
SUB_TAB_BLOCK_IMG = ROOT_PATH + "community_friend_block.sub"
SUB_TAB_REQUEST_IMG = ROOT_PATH + "community_friend_request.sub"

TAB_OVER_MEMBER = ROOT_PATH + "community_tab_mouse_over_member.sub"
TAB_OVER_BLOCK = ROOT_PATH + "community_tab_mouse_over_block.sub"
TAB_OVER_REQUEST = ROOT_PATH + "community_tab_mouse_over_request.sub"

STATE_GREEN = ROOT_PATH + "community_state_green.sub"
STATE_YELLOW = ROOT_PATH + "community_state_yellow.sub"
STATE_BLUE = ROOT_PATH + "community_state_blue.sub"
STATE_RED = ROOT_PATH + "community_state_red.sub"
STATE_DEEP_RED = ROOT_PATH + "community_state_deep_red.sub"

DROP_LIST_TOP = ROOT_PATH + "community_drop_list_top.sub"
DROP_LIST_MIDDLE = ROOT_PATH + "community_drop_list_middle.sub"
DROP_LIST_BOTTOM = ROOT_PATH + "community_drop_list_bottom.sub"
DROP_MOUSE_OVER = ROOT_PATH + "community_drop_mouse_over.sub"

ICON_POSITION = ROOT_PATH + "community_icon_position_default.sub"
ICON_POSITION_OVER = ROOT_PATH + "community_icon_position_mouse_over.sub"
ICON_WISHLIST = ROOT_PATH + "community_icon_wishlist_default.sub"
ICON_WISHLIST_OVER = ROOT_PATH + "community_icon_wishlist_mouse_over.sub"
ICON_WISHLIST_CLICK = ROOT_PATH + "community_icon_wishlist_click.sub"
ICON_PARTY = ROOT_PATH + "community_icon_party_invite_default.sub"
ICON_PARTY_OVER = ROOT_PATH + "community_icon_party_invite_mouse_over.sub"
ICON_PARTY_CLICK = ROOT_PATH + "community_icon_party_invite_click.sub"
ICON_X = ROOT_PATH + "community_icon_x_default.sub"
ICON_X_OVER = ROOT_PATH + "community_icon_x_mouse_over.sub"
ICON_X_CLICK = ROOT_PATH + "community_icon_x_click.sub"
ICON_ACCEPT = ROOT_PATH + "community_icon_request_accept_default.sub"
ICON_ACCEPT_OVER = ROOT_PATH + "community_icon_request_accept_mouse_over.sub"
ICON_ACCEPT_CLICK = ROOT_PATH + "community_icon_request_accept_click.sub"
ICON_FAMILY = ROOT_PATH + "community_icon_family_default.sub"
ICON_FAMILY_OVER = ROOT_PATH + "community_icon_family_mouse_over.sub"
ICON_FRIEND = ROOT_PATH + "community_icon_friend.sub"
ICON_GUILD_MEMBER = ROOT_PATH + "community_icon_guild_member.sub"
ICON_LEVEL = ROOT_PATH + "community_icon_level.sub"

CHECK_BOX = GAME_PATH + "common/checkbox_selected.png"
UNCHECK_BOX = GAME_PATH + "common/checkbox_normal.png"

ON_OFF_BTN_UP = PUBLIC_PATH + "small_button_01.sub"
ON_OFF_BTN_OVER = PUBLIC_PATH + "small_button_02.sub"
ON_OFF_BTN_DOWN = PUBLIC_PATH + "small_button_03.sub"

MEMBER_INFO_BAR_W = 258
MEMBER_INFO_BAR_H = 34
MEMBER_INFO_BAR_DEFAULT_X = 3
BUTTON_INTERVAL_X = 30

LIST_PANEL_X = 27
LIST_PANEL_Y = 110
LIST_PANEL_W = 266
LIST_PANEL_H = 255
LIST_ROW_Y_OFFSET = 3
LIST_LINE_HEIGHT = 36
LIST_X = LIST_PANEL_X + MEMBER_INFO_BAR_DEFAULT_X
LIST_START_Y = LIST_PANEL_Y + LIST_ROW_Y_OFFSET
VISIBLE_ROWS = 7

SCROLL_X = 278
SCROLL_Y = LIST_PANEL_Y
SCROLL_SIZE = 253

ROW_ICON_X_BASE = MEMBER_INFO_BAR_W - 28
ROW_ICON_POS_X = ROW_ICON_X_BASE - (BUTTON_INTERVAL_X * 2)
ROW_ICON_FAVORITE_X = ROW_ICON_X_BASE - BUTTON_INTERVAL_X
ROW_ICON_PARTY_X = ROW_ICON_X_BASE
ROW_ICON_Y = 4
ROW_STATE_X = 7
ROW_STATE_Y = 12
ROW_NAME_X = 125
ROW_NAME_Y = 10
ROW_NAME_PICKER_W = ROW_ICON_POS_X - 25
ROW_NAME_PICKER_H = 18
ROW_LEVEL_X = ROW_ICON_POS_X - 25
ROW_LEVEL_COLOR = -7751539

ROW_BLOCK_ICON_W = 24
ROW_UNBLOCK_X = int((MEMBER_INFO_BAR_W - ROW_BLOCK_ICON_W) / 1.2)
ROW_UNBLOCK_Y = (MEMBER_INFO_BAR_H - ROW_BLOCK_ICON_W) // 2
ROW_REQUEST_ACCEPT_X = ROW_ICON_X_BASE - BUTTON_INTERVAL_X
ROW_REQUEST_REFUSE_X = ROW_ICON_X_BASE

FAMILY_INFO_BAR_X = 15
FAMILY_INFO_BAR_Y = 42
FAMILY_BTN_X_BASE = MEMBER_INFO_BAR_W - 15
FAMILY_BTN_POS_X = FAMILY_BTN_X_BASE - (BUTTON_INTERVAL_X * 2)
FAMILY_BTN_PARTY_X = FAMILY_BTN_X_BASE - BUTTON_INTERVAL_X
FAMILY_BTN_LOVE_X = FAMILY_BTN_X_BASE
FAMILY_BTN_Y = 4

HDR_DROP_X = 8
HDR_DROP_Y = 28
HDR_STATE_X = 10
HDR_STATE_Y = 12

DROP_W = 170
DROP_ITEM_H = 16
DROP_ICON_X = 8
DROP_ICON_W = 10
DROP_TEXT_X = 24
DROP_TEXT_Y = 2

SUB_TAB_PICKER_X = (13, 58, 103)
SUB_TAB_PICKER_Y = 88
FRIEND_ACTION_X_BASE = 160
FRIEND_ACTION_INTERVAL_X = 30

GUILD_PANEL_X = 10
GUILD_PANEL_Y = 45
GUILD_LIST_PANEL_X = 14
GUILD_LIST_PANEL_Y = 33
GUILD_LIST_PANEL_W = LIST_PANEL_W
GUILD_LIST_PANEL_H = 252
GUILD_LIST_X = GUILD_LIST_PANEL_X + MEMBER_INFO_BAR_DEFAULT_X
GUILD_LIST_START_Y = GUILD_LIST_PANEL_Y + LIST_ROW_Y_OFFSET
GUILD_SCROLL_X = 268
GUILD_SCROLL_Y = GUILD_LIST_PANEL_Y
GUILD_SCROLL_SIZE = 246

CONFIG_PANEL_X = 11
CONFIG_PANEL_Y = 1
CONFIG_PANEL_W = 266
CONFIG_PANEL_H = 325
CONFIG_CONTENT_X = 2
CONFIG_CLIP_X = 1
CONFIG_CLIP_Y = 1
CONFIG_MAIN_TOPIC_W = 258
CONFIG_MAIN_TOPIC_TITLE_H = 25
CONFIG_SUB_TOPIC_W = 258
CONFIG_SUB_TOPIC_H_WITH_CHECKS = 65
CONFIG_SUB_TOPIC_H_PLAIN = 30
CONFIG_SUB_TITLE_W = 202
CONFIG_SUB_TITLE_X = 0
CONFIG_SUB_TITLE_Y = -2
CONFIG_ON_OFF_BTN_GAP = 5
CONFIG_ON_OFF_BTN_X = CONFIG_SUB_TITLE_W + CONFIG_ON_OFF_BTN_GAP
CONFIG_ON_OFF_BTN_Y = 2
CONFIG_CHECK_ITEM_W = 50
CONFIG_CHECK_ITEM_H = 25
CONFIG_CHECK_BOX_X = 30
CONFIG_CHECK_BOX_Y = 5
CONFIG_CHECK_ITEM_INTERVAL_X = 77
CONFIG_CHECK_ROW_Y = 28
CONFIG_MAIN_TOPIC_GAP = 8

SCROLL_STEP_COUNT = 3
CONFIG_SCROLL_STEP = 0.16666666666666666
TWINKLE_TIME_INTERVAL = 0.5
HDR_ALIGNMENT_TOOLTIP_W = 120

TOOLTIP_MIN_W = 65
TOOLTIP_ACTION_W = 100
CONFIG_TOOLTIP_MIN_W = 220

MAIN_FRIEND = 0
MAIN_GUILD = 1
MAIN_CONFIG = 2

SUB_FRIEND = 0
SUB_BLOCK = 1
SUB_REQUEST = 2

CONFIG_DEFAULT = community.COMMUNITY_CFG_DEFAULT

STATE_IMAGE = {
	community.COMMUNITY_PRESENCE_CONNECT: STATE_GREEN,
	community.COMMUNITY_PRESENCE_LEFT_SEAT: STATE_DEEP_RED,
	community.COMMUNITY_PRESENCE_AUTO_HUNT: STATE_BLUE,
	community.COMMUNITY_PRESENCE_SHOP_OPEN: STATE_YELLOW,
	community.COMMUNITY_PRESENCE_DISCONNECT: STATE_RED,
}

STATE_LOCALE_KEY = {
	community.COMMUNITY_PRESENCE_CONNECT: ("COMMUNITY_CONNECT", "Online"),
	community.COMMUNITY_PRESENCE_LEFT_SEAT: ("COMMUNITY_LEFT_SEAT", "AFK"),
	community.COMMUNITY_PRESENCE_AUTO_HUNT: ("COMMUNITY_AUTO_HUNT", "Auto-hunting"),
	community.COMMUNITY_PRESENCE_SHOP_OPEN: ("COMMUNITY_SHOP_OPEN", "Shop open"),
	community.COMMUNITY_PRESENCE_DISCONNECT: ("COMMUNITY_DISCONNECT", "Offline"),
}

STATE_OPTIONS = (
	community.COMMUNITY_PRESENCE_CONNECT,
	community.COMMUNITY_PRESENCE_LEFT_SEAT,
	community.COMMUNITY_PRESENCE_AUTO_HUNT,
	community.COMMUNITY_PRESENCE_SHOP_OPEN,
	community.COMMUNITY_PRESENCE_DISCONNECT,
)

STATE_CONFIRM_KEY = {
	community.COMMUNITY_PRESENCE_LEFT_SEAT: ("COMMUNITY_LEFT_SEAT_DIALOG", "Set your status to AFK?"),
	community.COMMUNITY_PRESENCE_DISCONNECT: ("COMMUNITY_DISCONNECT_DIALOG", "Appear offline?"),
}

CHECK_GUILD = 0
CHECK_GUILD_LOGIN = 1
CHECK_FRIEND = 2
CHECK_FRIEND_LOGIN = 3
CHECK_FAMILY = 4
CHECK_FAMILY_LOGIN = 5
CHECK_LEVEL = 6
CHECK_LOCATION = 7

CHECK_ICON_PATH = {
	CHECK_GUILD: ICON_GUILD_MEMBER,
	CHECK_GUILD_LOGIN: ICON_GUILD_MEMBER,
	CHECK_FRIEND: ICON_FRIEND,
	CHECK_FRIEND_LOGIN: ICON_FRIEND,
	CHECK_FAMILY: ICON_FAMILY,
	CHECK_FAMILY_LOGIN: ICON_FAMILY,
	CHECK_LEVEL: ICON_LEVEL,
	CHECK_LOCATION: ICON_POSITION,
}

CHECK_TOOLTIP_KEY = {
	CHECK_GUILD: ("COMMUNITY_CONFIG_ALLOW_GUILD_MEMBER", "Allow guild members"),
	CHECK_GUILD_LOGIN: ("COMMUNITY_CONFIG_GUILD_MEMBER_LOGIN_ALARM", "Guild member login alarm"),
	CHECK_FRIEND: ("COMMUNITY_CONFIG_ALLOW_FRIEND_MEMBER", "Allow friends"),
	CHECK_FRIEND_LOGIN: ("COMMUNITY_CONFIG_FRIEND_MEMBER_LOGIN_ALARM", "Friend login alarm"),
	CHECK_FAMILY: ("COMMUNITY_CONFIG_ALLOW_FAMILY_MEMBER", "Allow spouse"),
	CHECK_FAMILY_LOGIN: ("COMMUNITY_CONFIG_FAMILY_MEMBER_LOGIN_ALARM", "Family member login alarm"),
	CHECK_LEVEL: ("COMMUNITY_CONFIG_LEVEL_INFO_SHOW", "Show level information"),
	CHECK_LOCATION: ("COMMUNITY_CONFIG_LOCATION_INFO_SHOW", "Show location information"),
}

# (mainTitleKey, mainDefault, ((subTitleKey, subDefault, masterBit, ((checkItem, bit), ...)), ...))
# A block blocks everyone; a block sub-topic's check items ALLOW that relation through
# (an exception). Unticked = that relation stays blocked. No allow exists where it cannot apply.
CONFIG_TOPICS = (
	("COMMUNITY_CONFIG_MAIN_LOGIN_ALARM", "Login alarm", (
		("COMMUNITY_CONFIG_SUB_LOGIN_ALARM", "Login alarm", community.COMMUNITY_CFG_ALARM, (
			(CHECK_GUILD_LOGIN, community.COMMUNITY_CFG_ALARM_GUILD),
			(CHECK_FRIEND_LOGIN, community.COMMUNITY_CFG_ALARM_FRIEND),
			(CHECK_FAMILY_LOGIN, community.COMMUNITY_CFG_ALARM_FAMILY),
		)),
	)),
	("COMMUNITY_CONFIG_MAIN_MY_INFO_ALARM", "My information", (
		("COMMUNITY_CONFIG_SUB_MY_INFO_ALARM", "My information alarm", community.COMMUNITY_CFG_SHOW, (
			(CHECK_LEVEL, community.COMMUNITY_CFG_SHOW_LEVEL),
			(CHECK_LOCATION, community.COMMUNITY_CFG_SHOW_LOCATION),
		)),
	)),
	("COMMUNITY_CONFIG_MAIN_BLOCK", "Block exceptions", (
		("COMMUNITY_CONFIG_SUB_BLOCK_EXCHANGE", "Block trade requests", community.COMMUNITY_CFG_BLOCK_EXCHANGE, (
			(CHECK_GUILD, community.COMMUNITY_CFG_BLOCK_EXCHANGE_GUILD),
			(CHECK_FRIEND, community.COMMUNITY_CFG_BLOCK_EXCHANGE_FRIEND),
			(CHECK_FAMILY, community.COMMUNITY_CFG_BLOCK_EXCHANGE_FAMILY),
		)),
		("COMMUNITY_CONFIG_SUB_BLOCK_PARTY_INVITE", "Block party invitations", community.COMMUNITY_CFG_BLOCK_PARTY_INVITE, (
			(CHECK_GUILD, community.COMMUNITY_CFG_BLOCK_PARTY_INVITE_GUILD),
			(CHECK_FRIEND, community.COMMUNITY_CFG_BLOCK_PARTY_INVITE_FRIEND),
			(CHECK_FAMILY, community.COMMUNITY_CFG_BLOCK_PARTY_INVITE_FAMILY),
		)),
		("COMMUNITY_CONFIG_SUB_BLOCK_PARTY_REQUEST", "Block party requests", community.COMMUNITY_CFG_BLOCK_PARTY_REQUEST, (
			(CHECK_GUILD, community.COMMUNITY_CFG_BLOCK_PARTY_REQUEST_GUILD),
			(CHECK_FRIEND, community.COMMUNITY_CFG_BLOCK_PARTY_REQUEST_FRIEND),
			(CHECK_FAMILY, community.COMMUNITY_CFG_BLOCK_PARTY_REQUEST_FAMILY),
		)),
		("COMMUNITY_CONFIG_SUB_BLOCK_WHISPER", "Block whispers", community.COMMUNITY_CFG_BLOCK_WHISPER, (
			(CHECK_GUILD, community.COMMUNITY_CFG_BLOCK_WHISPER_GUILD),
			(CHECK_FRIEND, community.COMMUNITY_CFG_BLOCK_WHISPER_FRIEND),
			(CHECK_FAMILY, community.COMMUNITY_CFG_BLOCK_WHISPER_FAMILY),
		)),
		("COMMUNITY_CONFIG_SUB_BLOCK_FRIEND_REQUEST", "Block friend requests", community.COMMUNITY_CFG_BLOCK_FRIEND_REQUEST, (
			(CHECK_GUILD, community.COMMUNITY_CFG_BLOCK_FRIEND_REQUEST_GUILD),
			(CHECK_FAMILY, community.COMMUNITY_CFG_BLOCK_FRIEND_REQUEST_FAMILY),
		)),
		("COMMUNITY_CONFIG_SUB_BLOCK_GUILD_INVITE", "Block guild invitations", community.COMMUNITY_CFG_BLOCK_GUILD_INVITE, (
			(CHECK_FRIEND, community.COMMUNITY_CFG_BLOCK_GUILD_INVITE_FRIEND),
			(CHECK_FAMILY, community.COMMUNITY_CFG_BLOCK_GUILD_INVITE_FAMILY),
		)),
	)),
)


def IsFlagSet(config, bit):
	return (config & bit) == bit


def GetStateImage(state):
	return STATE_IMAGE.get(state, STATE_GREEN)


def GetStateLabel(state):
	key, default = STATE_LOCALE_KEY.get(state, ("COMMUNITY_CONNECT", "Online"))
	return _L(key, default)


def GetMapName(mapIndex):
	resolver = getattr(localeinfo, "GetMiniMapZoneNameByIdx", None)
	if not resolver:
		return ""
	try:
		return resolver(mapIndex)
	except:
		return ""


def ApplyClipMask(widget, clipWindow):
	if not app.USE_CLIP_MASK or not clipWindow or not widget:
		return
	if hasattr(widget, "SetClippingMaskWindow"):
		widget.SetClippingMaskWindow(clipWindow)
	if isinstance(widget, ui.Button):
		buttonText = getattr(widget, "ButtonText", None)
		if buttonText:
			ApplyClipMask(buttonText, clipWindow)


def MakeIconButton(parent, x, y, upPath, overPath, downPath):
	button = ui.Button()
	button.SetParent(parent)
	button.SetPosition(int(x), int(y))
	button.SetUpVisual(upPath)
	button.SetOverVisual(overPath)
	button.SetDownVisual(downPath)
	button.SetDisableVisual(upPath)
	button.Show()
	button.communityUpPath = upPath
	button.communityOverPath = overPath
	button.communityDownPath = downPath
	return button


def SetIconButtonEnabled(button, isEnabled):
	if not button:
		return
	upPath = button.communityUpPath
	button.SetUpVisual(upPath)
	button.SetDisableVisual(upPath)
	if isEnabled:
		button.SetOverVisual(button.communityOverPath)
		button.SetDownVisual(button.communityDownPath)
		button.Enable()
	else:
		button.SetOverVisual(upPath)
		button.SetDownVisual(upPath)
		button.Disable()


class ToolTipHelper(object):
	def __init__(self):
		self.toolTip = None

	def Hide(self):
		if self.toolTip:
			self.toolTip.HideToolTip()
			self.toolTip = None

	def Show(self, lines, minWidth=TOOLTIP_MIN_W):
		self.Hide()
		if not lines:
			return
		toolTip = uitooltip.ToolTip(minWidth)
		for line in lines:
			toolTip.AutoAppendTextLine(line)
		toolTip.AlignTextLineHorizonalCenter()
		toolTip.ResizeToolTip()
		toolTip.ShowToolTip()
		self.toolTip = toolTip


class StateDropDownList(ui.Window):
	def __init__(self, owner):
		ui.Window.__init__(self)
		self.owner = owner
		self.rows = []
		self.hovers = []
		self.AddFlag("float")
		self.SetSize(DROP_W, DROP_ITEM_H * len(STATE_OPTIONS))
		self.__Build()
		self.Hide()

	def __del__(self):
		ui.Window.__del__(self)

	def __Build(self):
		last = len(STATE_OPTIONS) - 1
		for index, state in enumerate(STATE_OPTIONS):
			if index == 0:
				bgPath = DROP_LIST_TOP
			elif index == last:
				bgPath = DROP_LIST_BOTTOM
			else:
				bgPath = DROP_LIST_MIDDLE

			row = ui.ImageBox()
			row.SetParent(self)
			row.LoadImage(bgPath)
			row.SetPosition(0, DROP_ITEM_H * index)
			row.SetEvent(ui.__mem_func__(self.__OnClickRow), "mouse_click", index)
			row.SetEvent(ui.__mem_func__(self.__OnOverInRow), "mouse_over_in", index)
			row.SetEvent(ui.__mem_func__(self.__OnOverOutRow), "mouse_over_out", index)
			row.Show()

			hover = ui.ImageBox()
			hover.SetParent(row)
			hover.AddFlag("not_pick")
			hover.LoadImage(DROP_MOUSE_OVER)
			hover.SetPosition(2, 1)
			hover.Hide()

			icon = ui.ImageBox()
			icon.SetParent(row)
			icon.AddFlag("not_pick")
			icon.LoadImage(GetStateImage(state))

			text = ui.TextLine()
			text.SetParent(row)
			text.AddFlag("not_pick")
			text.SetText(GetStateLabel(state))

			if localeinfo.IsARABIC():
				icon.SetPosition(DROP_W - DROP_ICON_X - DROP_ICON_W, 3)
				text.SetPosition(DROP_W - DROP_TEXT_X, DROP_TEXT_Y)
				text.SetHorizontalAlignLeft()
			else:
				icon.SetPosition(DROP_ICON_X, 3)
				text.SetPosition(DROP_TEXT_X, DROP_TEXT_Y)

			icon.Show()
			text.Show()

			self.rows.append((row, icon, text))
			self.hovers.append(hover)

	def __OnClickRow(self, eventKey, index):
		self.Hide()
		self.owner.OnSelectPresence(STATE_OPTIONS[index])

	def __OnOverInRow(self, eventKey, index):
		self.hovers[index].Show()

	def __OnOverOutRow(self, eventKey, index):
		self.hovers[index].Hide()

	def Toggle(self):
		if self.IsShow():
			self.Hide()
		else:
			self.SetTop()
			self.Show()


class StatusMessageDialog(ui.BoardWithTitleBar):
	WIDTH = 380
	HEIGHT = 85

	def __init__(self, owner):
		ui.BoardWithTitleBar.__init__(self)
		self.owner = owner
		self.editLine = None
		self.editBar = None
		self.saveButton = None
		self.deleteButton = None
		self.__Build()

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def __Build(self):
		self.SetSize(self.WIDTH, self.HEIGHT)
		self.SetTitleName(_L("COMMUNITY_MY_STATUS_MESSAGE", "My status message"))
		self.SetCloseEvent(ui.__mem_func__(self.Close))
		self.AddFlag("movable")
		self.AddFlag("float")

		self.editBar = ui.SlotBar()
		self.editBar.SetParent(self)
		self.editBar.SetPosition(15, 32)
		self.editBar.SetSize(self.WIDTH - 30, 20)
		self.editBar.Show()

		self.editLine = ui.EditLine()
		self.editLine.SetParent(self.editBar)
		self.editLine.SetPosition(4, 3)
		self.editLine.SetSize(self.WIDTH - 40, 16)
		self.editLine.SetMax(community.COMMUNITY_STATUS_MESSAGE_MAX_LEN)
		self.editLine.SetReturnEvent(ui.__mem_func__(self.__OnSave))
		self.editLine.SetEscapeEvent(ui.__mem_func__(self.Close))
		self.editLine.Show()

		self.saveButton = ui.Button()
		self.saveButton.SetParent(self)
		self.saveButton.SetPosition(self.WIDTH - 115, 58)
		self.saveButton.SetUpVisual(ROOT_PATH + "community_button_default.sub")
		self.saveButton.SetOverVisual(ROOT_PATH + "community_button_mouse_over.sub")
		self.saveButton.SetDownVisual(ROOT_PATH + "community_button_click.sub")
		self.saveButton.SetText(_L("COMMUNITY_CONFIG_SAVE", "Save"))
		self.saveButton.SetEvent(ui.__mem_func__(self.__OnSave))
		self.saveButton.Show()

		self.deleteButton = ui.Button()
		self.deleteButton.SetParent(self)
		self.deleteButton.SetPosition(15, 58)
		self.deleteButton.SetUpVisual(ROOT_PATH + "community_button_default.sub")
		self.deleteButton.SetOverVisual(ROOT_PATH + "community_button_mouse_over.sub")
		self.deleteButton.SetDownVisual(ROOT_PATH + "community_button_click.sub")
		self.deleteButton.SetText(_L("OFFLINESHOP_SEARCH_FILTER_DELETE", "Delete"))
		self.deleteButton.SetEvent(ui.__mem_func__(self.__OnDelete))
		self.deleteButton.Show()

		self.Hide()

	def Open(self, statusMessage):
		self.editLine.SetText(statusMessage)
		self.SetCenterPosition()
		self.SetTop()
		self.Show()
		self.editLine.SetFocus()

	def Close(self):
		if self.editLine:
			self.editLine.KillFocus()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def __OnSave(self):
		text = self.editLine.GetText()
		self.Close()
		self.owner.OnApplyStatusMessage(text)

	def __OnDelete(self):
		self.editLine.SetText("")
		self.Close()
		self.owner.OnApplyStatusMessage("")


class MemberRow(ui.Window):
	def __init__(self, owner):
		ui.Window.__init__(self)
		self.owner = owner
		self.name = ""
		self.level = 0
		self.presence = community.COMMUNITY_PRESENCE_DISCONNECT
		self.isSelected = False
		self.toolTip = ToolTipHelper()

		self.AddFlag("float")
		self.SetSize(MEMBER_INFO_BAR_W, MEMBER_INFO_BAR_H)
		self.SetMouseLeftButtonDownEvent(ui.__mem_func__(self.__OnClickRow))

		self.background = ui.ImageBox()
		self.background.SetParent(self)
		self.background.AddFlag("not_pick")
		self.background.LoadImage(MEMBER_INFO_BAR_BG)
		self.background.Show()

		self.stateIcon = ui.ImageBox()
		self.stateIcon.SetParent(self)
		self.stateIcon.AddFlag("not_pick")
		self.stateIcon.SetPosition(ROW_STATE_X, ROW_STATE_Y)
		self.stateIcon.LoadImage(STATE_RED)
		self.stateIcon.Show()

		self.stateIconPicker = ui.Window()
		self.stateIconPicker.SetParent(self)
		self.stateIconPicker.SetPosition(ROW_STATE_X, ROW_STATE_Y)
		self.stateIconPicker.SetSize(10, 10)
		self.stateIconPicker.SetOverInEvent(ui.__mem_func__(self.__OnOverStateIcon))
		self.stateIconPicker.SetOverOutEvent(ui.__mem_func__(self.__OnOverOut))
		self.stateIconPicker.SetMouseLeftButtonDownEvent(ui.__mem_func__(self.__OnClickRow))
		self.stateIconPicker.Show()

		self.nameText = ui.TextLine()
		self.nameText.SetParent(self)
		self.nameText.AddFlag("not_pick")
		self.nameText.SetPosition(ROW_NAME_X, ROW_NAME_Y)
		self.nameText.Show()

		self.namePicker = ui.Window()
		self.namePicker.SetParent(self)
		self.namePicker.SetPosition(ROW_NAME_X, ROW_NAME_Y - 2)
		self.namePicker.SetSize(ROW_NAME_PICKER_W, ROW_NAME_PICKER_H)
		self.namePicker.SetOverInEvent(ui.__mem_func__(self.OnOverName))
		self.namePicker.SetOverOutEvent(ui.__mem_func__(self.__OnOverOut))
		self.namePicker.SetMouseLeftButtonDownEvent(ui.__mem_func__(self.__OnClickRow))
		self.namePicker.Show()

		self.levelText = ui.TextLine()
		self.levelText.SetParent(self)
		self.levelText.AddFlag("not_pick")
		self.levelText.SetPosition(ROW_LEVEL_X, ROW_NAME_Y)
		self.levelText.SetHorizontalAlignRight()
		self.levelText.SetPackedFontColor(ROW_LEVEL_COLOR)
		self.levelText.Hide()

	def __del__(self):
		ui.Window.__del__(self)

	def GetName(self):
		return self.name

	def IsOnline(self):
		return self.presence != community.COMMUNITY_PRESENCE_DISCONNECT

	def SetSelected(self, isSelected):
		self.isSelected = isSelected
		if isSelected:
			self.background.LoadImage(MEMBER_INFO_BAR_HOVER)
		else:
			self.background.LoadImage(MEMBER_INFO_BAR_BG)

	def SetPresence(self, presence):
		self.presence = presence
		self.stateIcon.LoadImage(GetStateImage(presence))

	def SetLevelText(self, level):
		self.level = level
		if level > 0:
			self.levelText.SetText(str(level))
			self.levelText.Show()
		else:
			self.levelText.Hide()

	def ShowToolTip(self, lines, minWidth=TOOLTIP_MIN_W):
		self.toolTip.Show(lines, minWidth)

	def __OnOverOut(self):
		self.toolTip.Hide()

	def __OnOverStateIcon(self):
		self.ShowToolTip((GetStateLabel(self.presence),))

	def OnOverName(self):
		pass

	def __OnClickRow(self):
		self.owner.OnSelectRow(self.name)


# --- Friend-row portrait card (step 1 redesign) -----------------------------
MESSENGER_PATH = "d:/ymir work/ui/game/messenger/"
FRIEND_BOX_IMG = MESSENGER_PATH + "friend_box.png"
FRIEND_BOX_HOVER_IMG = MESSENGER_PATH + "friend_box_hover.png"
FRIEND_BOX_DOWN_IMG = MESSENGER_PATH + "friend_box_down.png"
STATUS_ONLINE_IMG = MESSENGER_PATH + "online_image.png"
STATUS_OFFLINE_IMG = MESSENGER_PATH + "offline_image.png"

# Friend presence -> status dot (all 5 states, not just online/offline).
STATUS_DOT_IMG = {
	community.COMMUNITY_PRESENCE_CONNECT: STATUS_ONLINE_IMG,
	community.COMMUNITY_PRESENCE_LEFT_SEAT: MESSENGER_PATH + "afk_image.png",
	community.COMMUNITY_PRESENCE_AUTO_HUNT: MESSENGER_PATH + "auto_hunt_image.png",
	community.COMMUNITY_PRESENCE_SHOP_OPEN: MESSENGER_PATH + "offlineshop_image.png",
	community.COMMUNITY_PRESENCE_DISCONNECT: STATUS_OFFLINE_IMG,
}

# bJob is the raw race (MAIN_RACE_ 0-8) from the server; map it to the class+gender portrait.
# 8 = wolfman (no portrait -> hidden). Order matches the server enum in char.h.
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

CARD_W = 255
CARD_H = 35
CARD_PORTRAIT_X = 3
CARD_PORTRAIT_Y = 3
CARD_TEXT_X = 40
CARD_NAME_Y = 4 - 2
CARD_DOT_X = 40
CARD_DOT_Y = 20
CARD_LOC_TEXT_X = 55
CARD_LOC_Y = 19 - 2
CARD_STAR_X = 226
CARD_STAR_Y = 6
CARD_STAR_X_RTL = 5
CARD_PORTRAIT_W = 29
CARD_DOT_W = 11
CARD_LOC_COLOR = -5592400

# Context menu styled like the shop-search ComboBoxNew popup (uishopsearch_new colors).
CTX_MENU_W = 160
CTX_ROW_H = 20
CTX_PAD = 4
CTX_MENU_H = CTX_PAD * 2 + CTX_ROW_H * 5
CTX_TEXT_X = 10
CTX_BG_COLOR = 0xff171411
CTX_HOVER_COLOR = 0xff312a21
CTX_BORDER_COLOR = 0xff3b332a
CTX_COLOR_ENABLED = 0xffafa496
CTX_COLOR_DISABLED = 0xff6b645a

# Search + GM strip (replaces the removed spouse info bar).
SEARCH_FIELD_IMG = MESSENGER_PATH + "search_field.png"
BTN_SEARCH_NORM = MESSENGER_PATH + "btn_search_norm.png"
BTN_SEARCH_HOVER = MESSENGER_PATH + "btn_search_hover.png"
BTN_SEARCH_SELECT = MESSENGER_PATH + "btn_search_select.png"
GM_BTN_NORM = MESSENGER_PATH + "support_0.png"
GM_BTN_HOVER = MESSENGER_PATH + "support_01.png"
GM_BTN_DOWN = MESSENGER_PATH + "support_02.png"

STRIP_X = 38
STRIP_Y = 45
STRIP_W = 246
STRIP_H = 30
GM_BTN_W = 24
GM_BTN_GAP = 6
SEARCH_FIELD_W = 216
SEARCH_EDIT_X = 8
SEARCH_EDIT_Y = 7
SEARCH_EDIT_W = 176
SEARCH_MAG_X = 186
SEARCH_MAG_Y = 4

# GM-list popup (dark ComboBox style, shared CTX_* colors).
GM_POPUP_W = 190
GM_POPUP_ROW_H = 20
GM_POPUP_HEADER_H = 22
GM_POPUP_MAX_ROWS = 15

class FriendRow(MemberRow):
	def __init__(self, owner):
		MemberRow.__init__(self, owner)
		self.SetSize(CARD_W, CARD_H)

		if localeinfo.IsARABIC():
			portraitX = CARD_W - CARD_PORTRAIT_X - CARD_PORTRAIT_W
			dotX = CARD_W - CARD_DOT_X - CARD_DOT_W
			nameX = CARD_W - CARD_TEXT_X
			locX = CARD_W - CARD_LOC_TEXT_X
			starX = CARD_STAR_X_RTL
		else:
			portraitX = CARD_PORTRAIT_X
			dotX = CARD_DOT_X
			nameX = CARD_TEXT_X
			locX = CARD_LOC_TEXT_X
			starX = CARD_STAR_X

		self.isFavorite = False
		self.channel = 0
		self.mapIndex = 0
		self.empire = 0
		self.race = 0
		self.statusMessage = ""

		# The base state icon + name/level widgets are replaced by the card.
		self.stateIcon.Hide()
		self.stateIconPicker.Hide()
		self.nameText.Hide()
		self.namePicker.Hide()
		self.levelText.Hide()

		self.background.LoadImage(FRIEND_BOX_IMG)

		self.portrait = ui.ImageBox()
		self.portrait.SetParent(self)
		self.portrait.AddFlag("not_pick")
		self.portrait.SetPosition(portraitX, CARD_PORTRAIT_Y)
		self.portrait.Hide()

		self.statusDot = ui.ImageBox()
		self.statusDot.SetParent(self)
		self.statusDot.AddFlag("not_pick")
		self.statusDot.SetPosition(dotX, CARD_DOT_Y)
		self.statusDot.LoadImage(STATUS_OFFLINE_IMG)
		self.statusDot.Show()

		self.nameLine = ui.TextLine()
		self.nameLine.SetParent(self)
		self.nameLine.AddFlag("not_pick")
		self.nameLine.SetPosition(nameX, CARD_NAME_Y)
		if localeinfo.IsARABIC():
			self.nameLine.SetHorizontalAlignLeft()
		self.nameLine.Show()

		self.locLine = ui.TextLine()
		self.locLine.SetParent(self)
		self.locLine.AddFlag("not_pick")
		self.locLine.SetPosition(locX, CARD_LOC_Y)
		if localeinfo.IsARABIC():
			self.locLine.SetHorizontalAlignLeft()
		self.locLine.SetPackedFontColor(CARD_LOC_COLOR)
		self.locLine.Show()

		self.favoriteButton = MakeIconButton(self, starX, CARD_STAR_Y,
			ICON_WISHLIST, ICON_WISHLIST_OVER, ICON_WISHLIST_CLICK)
		self.favoriteButton.SetOverEvent(ui.__mem_func__(self.__OnOverFavorite))
		self.favoriteButton.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutButton))
		self.favoriteButton.SetEvent(ui.__mem_func__(self.__OnClickFavorite))

		self.SetMouseLeftButtonDownEvent(ui.__mem_func__(self.__OnClickFriend))
		self.SetMouseLeftButtonDoubleClickEvent(ui.__mem_func__(self.__OnDoubleClickFriend))
		self.SetMouseRightButtonUpEvent(ui.__mem_func__(self.__OnRightClick))
		self.SetOverInEvent(ui.__mem_func__(self.__OnOverRow))
		self.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutRow))

	def SetSelected(self, isSelected):
		self.isSelected = isSelected
		if isSelected:
			self.background.LoadImage(FRIEND_BOX_DOWN_IMG)
		else:
			self.background.LoadImage(FRIEND_BOX_IMG)

	def SetData(self, name, presence, level, favorite, statusMessage, channel, mapIndex, empire, race):
		self.name = name
		self.presence = presence
		self.level = level
		self.isFavorite = bool(favorite)
		self.channel = channel
		self.mapIndex = mapIndex
		self.empire = empire
		self.race = race
		self.statusMessage = statusMessage
		self.__RefreshCard()

	def __RefreshCard(self):
		online = self.IsOnline()

		if self.race in PORTRAIT_IMG:
			self.portrait.LoadImage(PORTRAIT_IMG[self.race])
			self.portrait.Show()
		else:
			self.portrait.Hide()

		self.statusDot.LoadImage(STATUS_DOT_IMG.get(self.presence, STATUS_OFFLINE_IMG))

		if self.level > 0:
			self.nameLine.SetText(_L("COMMUNITY_ROW_NAME_LEVEL", "Lv. %d  %s") % (self.level, self.name))
		else:
			self.nameLine.SetText(self.name)

		if not online:
			self.locLine.SetText(_L("COMMUNITY_DISCONNECT", "Offline"))
		else:
			zone = GetMapName(self.mapIndex)
			if self.channel > 0 and zone:
				self.locLine.SetText(_L("COMMUNITY_ROW_CH_MAP", "CH %d - %s") % (self.channel, zone))
			elif self.channel > 0:
				self.locLine.SetText(_L("COMMUNITY_ROW_CH", "CH %d") % self.channel)
			else:
				self.locLine.SetText(GetStateLabel(self.presence))

		self.__RefreshFavoriteVisual()

	def __RefreshFavoriteVisual(self):
		if self.isFavorite:
			self.favoriteButton.communityUpPath = ICON_WISHLIST_OVER
			self.favoriteButton.communityOverPath = ICON_WISHLIST_CLICK
			self.favoriteButton.communityDownPath = ICON_WISHLIST_CLICK
		else:
			self.favoriteButton.communityUpPath = ICON_WISHLIST
			self.favoriteButton.communityOverPath = ICON_WISHLIST_OVER
			self.favoriteButton.communityDownPath = ICON_WISHLIST_CLICK
		SetIconButtonEnabled(self.favoriteButton, True)

	def __OnOverOutButton(self):
		self.toolTip.Hide()

	def __OnOverFavorite(self):
		self.ShowToolTip((_L("COMMUNITY_FAVORITE_BUTTON", "Favorites"),), TOOLTIP_ACTION_W)

	def __OnOverRow(self):
		if not self.isSelected:
			self.background.LoadImage(FRIEND_BOX_HOVER_IMG)
		lines = [GetStateLabel(self.presence)]
		if self.statusMessage:
			lines.append(self.statusMessage)
		self.ShowToolTip(lines, TOOLTIP_ACTION_W)

	def __OnOverOutRow(self):
		if not self.isSelected:
			self.background.LoadImage(FRIEND_BOX_IMG)
		self.toolTip.Hide()

	def __OnClickFavorite(self):
		self.toolTip.Hide()
		self.owner.OnRowFavorite(self.name, not self.isFavorite)

	def __OnClickFriend(self):
		self.toolTip.Hide()
		self.owner.OnSelectRow(self.name)
		if app.IsPressed(app.DIK_LSHIFT) and self.IsOnline():
			self.owner.OnRowParty(self.name)

	def __OnDoubleClickFriend(self):
		self.owner.OnRowWhisper(self.name)

	def __OnRightClick(self):
		self.toolTip.Hide()
		gx, gy = wndMgr.GetMousePosition()
		self.owner.OnRowContext(self.name, self.isFavorite, self.IsOnline(), gx, gy)

class FriendContextMenu(ui.Window):
	ITEM_COUNT = 5

	def __init__(self, owner):
		ui.Window.__init__(self)
		self.owner = owner
		self.targetName = ""
		self.targetFavorite = False
		self.enabled = [True] * self.ITEM_COUNT
		self.hovers = []
		self.texts = []
		self.pickers = []
		self.AddFlag("float")
		self.SetSize(CTX_MENU_W, CTX_MENU_H)

		self.outer = ui.Bar()
		self.outer.SetParent(self)
		self.outer.SetPosition(0, 0)
		self.outer.SetSize(CTX_MENU_W, CTX_MENU_H)
		self.outer.SetColor(CTX_BORDER_COLOR)
		self.outer.AddFlag("not_pick")
		self.outer.Show()

		self.inner = ui.Bar()
		self.inner.SetParent(self.outer)
		self.inner.SetPosition(1, 1)
		self.inner.SetSize(CTX_MENU_W - 2, CTX_MENU_H - 2)
		self.inner.SetColor(CTX_BG_COLOR)
		self.inner.AddFlag("not_pick")
		self.inner.Show()

		self.__Build()
		self.Hide()

	def __del__(self):
		ui.Window.__del__(self)

	def __Build(self):
		rowW = CTX_MENU_W - 4
		for index in xrange(self.ITEM_COUNT):
			y = CTX_PAD + CTX_ROW_H * index

			hoverBar = ui.Bar()
			hoverBar.SetParent(self)
			hoverBar.AddFlag("not_pick")
			hoverBar.SetPosition(2, y)
			hoverBar.SetSize(rowW, CTX_ROW_H)
			hoverBar.SetColor(CTX_HOVER_COLOR)
			hoverBar.Hide()

			text = ui.TextLine()
			text.SetParent(self)
			text.AddFlag("not_pick")
			if localeinfo.IsARABIC():
				text.SetPosition(CTX_MENU_W - 2 - CTX_TEXT_X, y + 3)
				text.SetHorizontalAlignLeft()
			else:
				text.SetPosition(2 + CTX_TEXT_X, y + 3)
			text.Show()

			picker = ui.Window()
			picker.SetParent(self)
			picker.SetPosition(2, y)
			picker.SetSize(rowW, CTX_ROW_H)
			picker.SetMouseLeftButtonDownEvent(ui.__mem_func__(self.__OnClickRow), index)
			picker.SetOverInEvent(ui.__mem_func__(self.__OnOverIn), index)
			picker.SetOverOutEvent(ui.__mem_func__(self.__OnOverOut), index)
			picker.Show()

			self.hovers.append(hoverBar)
			self.texts.append(text)
			self.pickers.append(picker)

	def Open(self, name, favorite, online, x, y):
		self.targetName = name
		self.targetFavorite = favorite
		if favorite:
			favLabel = _L("COMMUNITY_CTX_UNFAVORITE", "Remove from favorites")
		else:
			favLabel = _L("COMMUNITY_CTX_FAVORITE", "Add to favorites")
		labels = (
			_L("COMMUNITY_MESSENGER_WHISPER", "Whisper"),
			_L("COMMUNITY_PARTY_INVITE", "Invite to party"),
			favLabel,
			_L("COMMUNITY_MESSENGER_FRIEND_DELETE", "Remove from friend list"),
			_L("COMMUNITY_MESSENGER_BLOCK", "Block"),
		)
		self.enabled = [online, online, True, True, True]
		for index in xrange(self.ITEM_COUNT):
			self.texts[index].SetText(labels[index])
			if self.enabled[index]:
				self.texts[index].SetPackedFontColor(CTX_COLOR_ENABLED)
			else:
				self.texts[index].SetPackedFontColor(CTX_COLOR_DISABLED)
			self.hovers[index].Hide()
		self.SetPosition(int(x), int(y))
		self.SetTop()
		self.Show()

	def __OnOverIn(self, index):
		if self.enabled[index]:
			self.hovers[index].Show()

	def __OnOverOut(self, index):
		self.hovers[index].Hide()

	def __OnClickRow(self, index):
		if not self.enabled[index]:
			return
		self.Hide()
		name = self.targetName
		if not name:
			return
		if index == 0:
			self.owner.OnRowWhisper(name)
		elif index == 1:
			self.owner.OnRowParty(name)
		elif index == 2:
			self.owner.OnRowFavorite(name, not self.targetFavorite)
		elif index == 3:
			self.owner.OnRowFriendDelete(name)
		elif index == 4:
			self.owner.OnRowBlockAdd(name)

class GMListPopup(ui.Window):
	def __init__(self, owner):
		ui.Window.__init__(self)
		self.owner = owner
		self.names = []
		self.rowCount = 0
		self.AddFlag("float")
		self.SetSize(GM_POPUP_W, CTX_PAD * 2 + GM_POPUP_HEADER_H + GM_POPUP_ROW_H)

		self.outer = ui.Bar()
		self.outer.SetParent(self)
		self.outer.SetPosition(0, 0)
		self.outer.SetColor(CTX_BORDER_COLOR)
		self.outer.AddFlag("not_pick")
		self.outer.Show()

		self.inner = ui.Bar()
		self.inner.SetParent(self.outer)
		self.inner.SetPosition(1, 1)
		self.inner.SetColor(CTX_BG_COLOR)
		self.inner.AddFlag("not_pick")
		self.inner.Show()

		self.header = ui.TextLine()
		self.header.SetParent(self)
		self.header.AddFlag("not_pick")
		self.header.SetPackedFontColor(CTX_COLOR_DISABLED)
		self.header.SetText(_L("COMMUNITY_GM_LIST_TITLE", "Online Game Masters"))
		if localeinfo.IsARABIC():
			self.header.SetPosition(GM_POPUP_W - 2 - CTX_TEXT_X, CTX_PAD + 3)
			self.header.SetHorizontalAlignLeft()
		else:
			self.header.SetPosition(2 + CTX_TEXT_X, CTX_PAD + 3)
		self.header.Show()

		self.emptyText = ui.TextLine()
		self.emptyText.SetParent(self)
		self.emptyText.AddFlag("not_pick")
		self.emptyText.SetPackedFontColor(CTX_COLOR_DISABLED)
		self.emptyText.SetText(_L("COMMUNITY_GM_LIST_EMPTY", "No Game Masters online"))
		if localeinfo.IsARABIC():
			self.emptyText.SetPosition(GM_POPUP_W - 2 - CTX_TEXT_X, CTX_PAD + GM_POPUP_HEADER_H + 3)
			self.emptyText.SetHorizontalAlignLeft()
		else:
			self.emptyText.SetPosition(2 + CTX_TEXT_X, CTX_PAD + GM_POPUP_HEADER_H + 3)
		self.emptyText.Hide()

		self.hovers = []
		self.texts = []
		self.pickers = []
		rowW = GM_POPUP_W - 4
		for index in xrange(GM_POPUP_MAX_ROWS):
			hoverBar = ui.Bar()
			hoverBar.SetParent(self)
			hoverBar.AddFlag("not_pick")
			hoverBar.SetSize(rowW, GM_POPUP_ROW_H)
			hoverBar.SetColor(CTX_HOVER_COLOR)
			hoverBar.Hide()

			text = ui.TextLine()
			text.SetParent(self)
			text.AddFlag("not_pick")
			text.Hide()

			picker = ui.Window()
			picker.SetParent(self)
			picker.SetSize(rowW, GM_POPUP_ROW_H)
			picker.SetMouseLeftButtonDownEvent(ui.__mem_func__(self.__OnClickRow), index)
			picker.SetOverInEvent(ui.__mem_func__(self.__OnOverIn), index)
			picker.SetOverOutEvent(ui.__mem_func__(self.__OnOverOut), index)
			picker.Hide()

			self.hovers.append(hoverBar)
			self.texts.append(text)
			self.pickers.append(picker)

		self.Hide()

	def __del__(self):
		ui.Window.__del__(self)

	def Open(self, entries, x, y):
		ar = localeinfo.IsARABIC()
		self.names = []
		count = min(len(entries), GM_POPUP_MAX_ROWS)
		self.rowCount = count

		baseY = CTX_PAD + GM_POPUP_HEADER_H
		for index in xrange(GM_POPUP_MAX_ROWS):
			if index < count:
				name, channel = entries[index]
				self.names.append(name)
				rowY = baseY + GM_POPUP_ROW_H * index
				label = _L("COMMUNITY_GM_LIST_ROW", "%s  CH %d") % (name, channel)
				self.texts[index].SetText(label)
				self.texts[index].SetPackedFontColor(CTX_COLOR_ENABLED)
				if ar:
					self.texts[index].SetPosition(GM_POPUP_W - 2 - CTX_TEXT_X, rowY + 3)
					self.texts[index].SetHorizontalAlignLeft()
				else:
					self.texts[index].SetPosition(2 + CTX_TEXT_X, rowY + 3)
				self.texts[index].Show()
				self.hovers[index].SetPosition(2, rowY)
				self.hovers[index].Hide()
				self.pickers[index].SetPosition(2, rowY)
				self.pickers[index].Show()
			else:
				self.texts[index].Hide()
				self.hovers[index].Hide()
				self.pickers[index].Hide()

		if count == 0:
			self.emptyText.Show()
			rows = 1
		else:
			self.emptyText.Hide()
			rows = count

		height = CTX_PAD * 2 + GM_POPUP_HEADER_H + GM_POPUP_ROW_H * rows
		self.SetSize(GM_POPUP_W, height)
		self.outer.SetSize(GM_POPUP_W, height)
		self.inner.SetSize(GM_POPUP_W - 2, height - 2)

		self.SetPosition(int(x), int(y))
		self.SetTop()
		self.Show()

	def __OnOverIn(self, index):
		if index < self.rowCount:
			self.hovers[index].Show()

	def __OnOverOut(self, index):
		self.hovers[index].Hide()

	def __OnClickRow(self, index):
		if index >= self.rowCount:
			return
		self.Hide()
		name = self.names[index]
		if name:
			self.owner.OnRowWhisper(name)

class BlockRow(MemberRow):
	def __init__(self, owner):
		MemberRow.__init__(self, owner)
		self.unblockButton = MakeIconButton(self, ROW_UNBLOCK_X, ROW_UNBLOCK_Y,
			ICON_X, ICON_X_OVER, ICON_X_CLICK)
		self.unblockButton.SetOverEvent(ui.__mem_func__(self.__OnOverUnblock))
		self.unblockButton.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutButton))
		self.unblockButton.SetEvent(ui.__mem_func__(self.__OnClickUnblock))
		self.levelText.Hide()

	def SetData(self, name, connected):
		self.name = name
		self.nameText.SetText(name)
		if connected:
			self.SetPresence(community.COMMUNITY_PRESENCE_CONNECT)
		else:
			self.SetPresence(community.COMMUNITY_PRESENCE_DISCONNECT)

	def __OnOverOutButton(self):
		self.toolTip.Hide()

	def __OnOverUnblock(self):
		self.ShowToolTip((_L("COMMUNITY_MESSENGER_BLOCK_DELETE", "Remove from block list"),), TOOLTIP_ACTION_W)

	def __OnClickUnblock(self):
		self.toolTip.Hide()
		self.owner.OnRowBlockDelete(self.name)


class RequestRow(MemberRow):
	def __init__(self, owner):
		MemberRow.__init__(self, owner)
		self.acceptButton = MakeIconButton(self, ROW_REQUEST_ACCEPT_X, ROW_ICON_Y,
			ICON_ACCEPT, ICON_ACCEPT_OVER, ICON_ACCEPT_CLICK)
		self.refuseButton = MakeIconButton(self, ROW_REQUEST_REFUSE_X, ROW_ICON_Y,
			ICON_X, ICON_X_OVER, ICON_X_CLICK)

		self.acceptButton.SetOverEvent(ui.__mem_func__(self.__OnOverAccept))
		self.acceptButton.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutButton))
		self.acceptButton.SetEvent(ui.__mem_func__(self.__OnClickAccept))
		self.refuseButton.SetOverEvent(ui.__mem_func__(self.__OnOverRefuse))
		self.refuseButton.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutButton))
		self.refuseButton.SetEvent(ui.__mem_func__(self.__OnClickRefuse))

		self.stateIcon.Hide()
		self.stateIconPicker.Hide()

	def SetData(self, name, level):
		self.name = name
		self.nameText.SetText(name)
		self.SetLevelText(level)

	def __OnOverOutButton(self):
		self.toolTip.Hide()

	def __OnOverAccept(self):
		self.ShowToolTip((_L("COMMUNITY_ACCEPT", "Accept"),), TOOLTIP_ACTION_W)

	def __OnOverRefuse(self):
		self.ShowToolTip((_L("COMMUNITY_REFUSE", "Refuse"),), TOOLTIP_ACTION_W)

	def __OnClickAccept(self):
		self.toolTip.Hide()
		self.owner.OnRowRequestAccept(self.name)

	def __OnClickRefuse(self):
		self.toolTip.Hide()
		self.owner.OnRowRequestRefuse(self.name)


class GuildRow(MemberRow):
	def __init__(self, owner):
		MemberRow.__init__(self, owner)
		self.SetSize(CARD_W, CARD_H)
		self.race = 0

		if localeinfo.IsARABIC():
			portraitX = CARD_W - CARD_PORTRAIT_X - CARD_PORTRAIT_W
			dotX = CARD_W - CARD_DOT_X - CARD_DOT_W
			nameX = CARD_W - CARD_TEXT_X
			locX = CARD_W - CARD_LOC_TEXT_X
		else:
			portraitX = CARD_PORTRAIT_X
			dotX = CARD_DOT_X
			nameX = CARD_TEXT_X
			locX = CARD_LOC_TEXT_X

		self.stateIcon.Hide()
		self.stateIconPicker.Hide()
		self.nameText.Hide()
		self.namePicker.Hide()
		self.levelText.Hide()

		self.background.LoadImage(FRIEND_BOX_IMG)

		self.portrait = ui.ImageBox()
		self.portrait.SetParent(self)
		self.portrait.AddFlag("not_pick")
		self.portrait.SetPosition(portraitX, CARD_PORTRAIT_Y)
		self.portrait.Hide()

		self.statusDot = ui.ImageBox()
		self.statusDot.SetParent(self)
		self.statusDot.AddFlag("not_pick")
		self.statusDot.SetPosition(dotX, CARD_DOT_Y)
		self.statusDot.LoadImage(STATUS_OFFLINE_IMG)
		self.statusDot.Show()

		self.nameLine = ui.TextLine()
		self.nameLine.SetParent(self)
		self.nameLine.AddFlag("not_pick")
		self.nameLine.SetPosition(nameX, CARD_NAME_Y)
		if localeinfo.IsARABIC():
			self.nameLine.SetHorizontalAlignLeft()
		self.nameLine.Show()

		self.locLine = ui.TextLine()
		self.locLine.SetParent(self)
		self.locLine.AddFlag("not_pick")
		self.locLine.SetPosition(locX, CARD_LOC_Y)
		if localeinfo.IsARABIC():
			self.locLine.SetHorizontalAlignLeft()
		self.locLine.SetPackedFontColor(CARD_LOC_COLOR)
		self.locLine.Show()

		self.SetMouseLeftButtonDownEvent(ui.__mem_func__(self.__OnClickGuild))
		self.SetMouseLeftButtonDoubleClickEvent(ui.__mem_func__(self.__OnDoubleClickGuild))
		self.SetOverInEvent(ui.__mem_func__(self.__OnOverRow))
		self.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutRow))

	def SetSelected(self, isSelected):
		self.isSelected = isSelected
		if isSelected:
			self.background.LoadImage(FRIEND_BOX_DOWN_IMG)
		else:
			self.background.LoadImage(FRIEND_BOX_IMG)

	def SetData(self, name, level, online, race):
		self.name = name
		self.level = level
		self.race = race
		if online:
			self.presence = community.COMMUNITY_PRESENCE_CONNECT
		else:
			self.presence = community.COMMUNITY_PRESENCE_DISCONNECT
		self.__RefreshCard()

	def __RefreshCard(self):
		if self.race in PORTRAIT_IMG:
			self.portrait.LoadImage(PORTRAIT_IMG[self.race])
			self.portrait.Show()
		else:
			self.portrait.Hide()
		self.statusDot.LoadImage(STATUS_DOT_IMG.get(self.presence, STATUS_OFFLINE_IMG))
		if self.level > 0:
			self.nameLine.SetText(_L("COMMUNITY_ROW_NAME_LEVEL", "Lv. %d  %s") % (self.level, self.name))
		else:
			self.nameLine.SetText(self.name)
		self.locLine.SetText(GetStateLabel(self.presence))

	def __OnOverRow(self):
		if not self.isSelected:
			self.background.LoadImage(FRIEND_BOX_HOVER_IMG)
		self.ShowToolTip((GetStateLabel(self.presence),), TOOLTIP_ACTION_W)

	def __OnOverOutRow(self):
		if not self.isSelected:
			self.background.LoadImage(FRIEND_BOX_IMG)
		self.toolTip.Hide()

	def __OnClickGuild(self):
		self.toolTip.Hide()
		self.owner.OnSelectRow(self.name)
		if app.IsPressed(app.DIK_LSHIFT) and self.IsOnline():
			self.owner.OnRowParty(self.name)

	def __OnDoubleClickGuild(self):
		self.owner.OnRowWhisper(self.name)

class LoverInfoBar(ui.Window):
	def __init__(self, owner):
		ui.Window.__init__(self)
		self.owner = owner
		self.name = ""
		self.lovePoint = 0
		self.online = False
		self.toolTip = ToolTipHelper()

		self.SetSize(MEMBER_INFO_BAR_W, MEMBER_INFO_BAR_H)

		self.background = ui.ImageBox()
		self.background.SetParent(self)
		self.background.AddFlag("not_pick")
		self.background.LoadImage(FAMILY_INFO_BAR_BG)
		self.background.Show()

		self.stateIcon = ui.ImageBox()
		self.stateIcon.SetParent(self)
		self.stateIcon.AddFlag("not_pick")
		self.stateIcon.SetPosition(ROW_STATE_X, ROW_STATE_Y)
		self.stateIcon.LoadImage(STATE_RED)
		self.stateIcon.Show()

		self.nameText = ui.TextLine()
		self.nameText.SetParent(self)
		self.nameText.AddFlag("not_pick")
		self.nameText.SetPosition(ROW_NAME_X, ROW_NAME_Y)
		self.nameText.Show()

		self.locationButton = MakeIconButton(self, FAMILY_BTN_POS_X, FAMILY_BTN_Y,
			ICON_POSITION, ICON_POSITION_OVER, ICON_POSITION)
		self.partyButton = MakeIconButton(self, FAMILY_BTN_PARTY_X, FAMILY_BTN_Y,
			ICON_PARTY, ICON_PARTY_OVER, ICON_PARTY_CLICK)
		self.loveButton = MakeIconButton(self, FAMILY_BTN_LOVE_X, FAMILY_BTN_Y,
			ICON_FAMILY, ICON_FAMILY_OVER, ICON_FAMILY)

		self.partyButton.SetEvent(ui.__mem_func__(self.__OnClickParty))
		self.partyButton.SetOverEvent(ui.__mem_func__(self.__OnOverParty))
		self.partyButton.SetOverOutEvent(ui.__mem_func__(self.__OnOverOut))
		self.loveButton.SetOverEvent(ui.__mem_func__(self.__OnOverLove))
		self.loveButton.SetOverOutEvent(ui.__mem_func__(self.__OnOverOut))

		SetIconButtonEnabled(self.locationButton, False)
		self.Clear()

	def __del__(self):
		ui.Window.__del__(self)

	def Clear(self):
		self.name = ""
		self.lovePoint = 0
		self.online = False
		self.nameText.SetText("")
		self.stateIcon.LoadImage(STATE_RED)
		SetIconButtonEnabled(self.partyButton, False)
		SetIconButtonEnabled(self.loveButton, False)

	def SetLover(self, name, lovePoint):
		self.name = name
		self.lovePoint = lovePoint
		self.nameText.SetText(name)
		SetIconButtonEnabled(self.loveButton, True)
		self.__RefreshState()

	def SetLovePoint(self, lovePoint):
		self.lovePoint = lovePoint

	def SetOnline(self, online):
		self.online = online
		self.__RefreshState()

	def __RefreshState(self):
		if not self.name:
			return
		if self.online:
			self.stateIcon.LoadImage(STATE_GREEN)
		else:
			self.stateIcon.LoadImage(STATE_RED)
		SetIconButtonEnabled(self.partyButton, self.online)

	def __OnOverOut(self):
		self.toolTip.Hide()

	def __OnOverParty(self):
		self.toolTip.Show((_L("COMMUNITY_PARTY_INVITE", "Invite to party"),), TOOLTIP_ACTION_W)

	def __OnOverLove(self):
		if not self.name:
			return
		self.toolTip.Show((_L("COMMUNITY_TOOLTIP_LOVE_POINT", "Affinity: %d%%") % self.lovePoint,), TOOLTIP_ACTION_W)

	def __OnClickParty(self):
		self.toolTip.Hide()
		if self.name:
			self.owner.OnRowParty(self.name)


class ConfigCheckItem(ui.Window):
	def __init__(self, owner, parentSubTopic, itemMode, toggleFlag):
		ui.Window.__init__(self)
		self.owner = owner
		self.parentSubTopic = parentSubTopic
		self.itemMode = itemMode
		self.toggleFlag = toggleFlag
		self.isChecked = False
		self.toolTip = ToolTipHelper()
		self.SetSize(CONFIG_CHECK_ITEM_W, CONFIG_CHECK_ITEM_H)

		self.itemImage = ui.ImageBox()
		self.itemImage.SetParent(self)
		self.itemImage.LoadImage(CHECK_ICON_PATH[itemMode])
		self.itemImage.SetPosition(0, 2)
		self.itemImage.Show()

		self.checkImage = ui.ImageBox()
		self.checkImage.SetParent(self)
		self.checkImage.LoadImage(CHECK_BOX)
		self.checkImage.SetPosition(CONFIG_CHECK_BOX_X, CONFIG_CHECK_BOX_Y)
		self.checkImage.SetEvent(ui.__mem_func__(self.__OnClickCheck), "mouse_click")
		self.checkImage.Hide()

		self.unCheckImage = ui.ImageBox()
		self.unCheckImage.SetParent(self)
		self.unCheckImage.LoadImage(UNCHECK_BOX)
		self.unCheckImage.SetPosition(CONFIG_CHECK_BOX_X, CONFIG_CHECK_BOX_Y)
		self.unCheckImage.SetEvent(ui.__mem_func__(self.__OnClickCheck), "mouse_click")
		self.unCheckImage.Show()

		for widget in (self.itemImage, self.checkImage, self.unCheckImage):
			widget.SetEvent(ui.__mem_func__(self.__OnOverIn), "mouse_over_in")
			widget.SetEvent(ui.__mem_func__(self.__OnOverOut), "mouse_over_out")

	def __del__(self):
		ui.Window.__del__(self)

	def ApplyClipMask(self, clipWindow):
		ApplyClipMask(self, clipWindow)
		for widget in (self.itemImage, self.checkImage, self.unCheckImage):
			ApplyClipMask(widget, clipWindow)

	def __OnOverIn(self, eventKey):
		key, default = CHECK_TOOLTIP_KEY[self.itemMode]
		self.toolTip.Show((_L(key, default),), CONFIG_TOOLTIP_MIN_W)

	def __OnOverOut(self, eventKey):
		self.toolTip.Hide()

	def __OnClickCheck(self, eventKey):
		if not self.parentSubTopic.IsOn():
			return
		self.owner.OnToggleConfigFlag(self.toggleFlag)

	def UpdateByFlag(self, config):
		self.isChecked = IsFlagSet(config, self.toggleFlag)
		if self.isChecked:
			self.checkImage.Show()
			self.unCheckImage.Hide()
		else:
			self.checkImage.Hide()
			self.unCheckImage.Show()


class ConfigSubTopic(ui.Window):
	def __init__(self, owner, titleKey, titleDefault, masterBit, masterInGameOptions = False):
		ui.Window.__init__(self)
		self.owner = owner
		self.masterBit = masterBit
		self.masterInGameOptions = masterInGameOptions
		self.checkItemList = []
		self.isOn = False
		self.SetSize(CONFIG_SUB_TOPIC_W, CONFIG_SUB_TOPIC_H_PLAIN)

		self.titleBg = ui.ImageBox()
		self.titleBg.SetParent(self)
		self.titleBg.AddFlag("not_pick")
		self.titleBg.LoadImage(ROOT_PATH + "community_config_sub_title.sub")
		self.titleBg.SetPosition(CONFIG_SUB_TITLE_X, CONFIG_SUB_TITLE_Y)
		self.titleBg.Show()

		self.titleText = ui.TextLine()
		self.titleText.SetParent(self.titleBg)
		self.titleText.AddFlag("not_pick")
		self.titleText.SetPosition(int(self.titleBg.GetWidth() // 2), int(self.titleBg.GetHeight() // 2))
		self.titleText.SetVerticalAlignCenter()
		self.titleText.SetHorizontalAlignCenter()
		self.titleText.SetText(_L(titleKey, titleDefault))
		self.titleText.Show()

		self.onOffButton = ui.ToggleButton()
		self.onOffButton.SetParent(self)
		self.onOffButton.SetUpVisual(ON_OFF_BTN_UP)
		self.onOffButton.SetOverVisual(ON_OFF_BTN_OVER)
		self.onOffButton.SetDownVisual(ON_OFF_BTN_DOWN)
		self.onOffButton.SetPosition(CONFIG_ON_OFF_BTN_X, CONFIG_ON_OFF_BTN_Y)
		self.onOffButton.SetToggleUpEvent(ui.__mem_func__(self.__OnClickOnOff))
		self.onOffButton.SetToggleDownEvent(ui.__mem_func__(self.__OnClickOnOff))
		self.onOffButton.Show()

		# The block on/off master lives in Advanced Game Options; here we only edit exceptions.
		if self.masterInGameOptions:
			self.onOffButton.Hide()

	def __del__(self):
		ui.Window.__del__(self)

	def ApplyClipMask(self, clipWindow):
		ApplyClipMask(self, clipWindow)
		ApplyClipMask(self.titleBg, clipWindow)
		ApplyClipMask(self.titleText, clipWindow)
		ApplyClipMask(self.onOffButton, clipWindow)
		for checkItem in self.checkItemList:
			checkItem.ApplyClipMask(clipWindow)

	def AppendCheckItem(self, itemMode, toggleFlag):
		checkItem = ConfigCheckItem(self.owner, self, itemMode, toggleFlag)
		checkItem.SetParent(self)
		index = len(self.checkItemList)
		checkItem.SetPosition(2 + (CONFIG_CHECK_ITEM_INTERVAL_X * index), CONFIG_CHECK_ROW_Y)
		checkItem.Show()
		self.checkItemList.append(checkItem)
		self.SetSize(CONFIG_SUB_TOPIC_W, CONFIG_SUB_TOPIC_H_WITH_CHECKS)
		return checkItem

	def IsOn(self):
		return self.isOn

	def __OnClickOnOff(self):
		if self.masterInGameOptions:
			return
		self.owner.OnToggleConfigFlag(self.masterBit)

	def __RefreshOnOffButton(self):
		if self.isOn:
			self.onOffButton.SetText(_L("COMMUNITY_CONFIG_ON", "On"))
			self.onOffButton.Down()
		else:
			self.onOffButton.SetText(_L("COMMUNITY_CONFIG_OFF", "Off"))
			self.onOffButton.SetUp()

	def UpdateByFlag(self, config):
		self.isOn = IsFlagSet(config, self.masterBit)
		self.__RefreshOnOffButton()
		for checkItem in self.checkItemList:
			checkItem.UpdateByFlag(config)


class ConfigMainTopic(ui.Window):
	def __init__(self, owner, titleKey, titleDefault):
		ui.Window.__init__(self)
		self.owner = owner
		self.subTopicList = []
		self.SetSize(CONFIG_MAIN_TOPIC_W, CONFIG_MAIN_TOPIC_TITLE_H)

		self.titleBg = ui.ImageBox()
		self.titleBg.SetParent(self)
		self.titleBg.AddFlag("not_pick")
		self.titleBg.LoadImage(ROOT_PATH + "community_config_main_title.sub")
		self.titleBg.SetPosition(0, 0)
		self.titleBg.Show()

		self.titleText = ui.TextLine()
		self.titleText.SetParent(self.titleBg)
		self.titleText.AddFlag("not_pick")
		self.titleText.SetPosition(int(CONFIG_MAIN_TOPIC_W // 2), int(CONFIG_MAIN_TOPIC_TITLE_H // 2))
		self.titleText.SetVerticalAlignCenter()
		self.titleText.SetHorizontalAlignCenter()
		self.titleText.SetText(_L(titleKey, titleDefault))
		self.titleText.Show()

	def __del__(self):
		ui.Window.__del__(self)

	def ApplyClipMask(self, clipWindow):
		ApplyClipMask(self, clipWindow)
		ApplyClipMask(self.titleBg, clipWindow)
		ApplyClipMask(self.titleText, clipWindow)
		for subTopic in self.subTopicList:
			subTopic.ApplyClipMask(clipWindow)

	def AppendSubTopic(self, subTopic):
		subTopic.SetParent(self)
		subTopic.Show()
		self.subTopicList.append(subTopic)
		return subTopic

	def Relayout(self):
		y = CONFIG_MAIN_TOPIC_TITLE_H
		for subTopic in self.subTopicList:
			subTopic.SetPosition(0, y)
			y += subTopic.GetHeight()
		self.SetSize(CONFIG_MAIN_TOPIC_W, y)
		return y

	def UpdateByFlag(self, config):
		for subTopic in self.subTopicList:
			subTopic.UpdateByFlag(config)


class CommunityWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		self.isLoaded = 0
		self.mainTab = MAIN_FRIEND
		self.subTab = SUB_FRIEND
		self.startLine = 0
		self.guildStartLine = 0
		self.selectedName = ""
		self.searchText = ""

		self.rows = []
		self.friendRows = {}
		self.blockRows = {}
		self.requestRows = {}
		self.guildRows = {}
		self.guildOnline = {}
		self.friendOrder = []
		self.blockOrder = []
		self.requestOrder = []
		self.guildOrder = []

		self.mainTopics = []
		self.subTopics = []
		self.workConfig = CONFIG_DEFAULT

		self.dropDownList = None
		self.statusDialog = None
		self.questionDialog = None
		self.inputDialog = None
		self.loverBar = None
		self.contextMenu = None
		self.gmPopup = None
		self.subTabHovers = []
		self.headerToolTip = ToolTipHelper()
		self.twinkleActive = False
		self.twinkleShown = False
		self.lastTwinkleTime = 0.0

		self.whisperEvent = lambda *arg: None
		self.partyInviteEvent = lambda *arg: None
		self.guildButtonEvent = lambda *arg: None
		if app.ENABLE_GUILD_FINDER:
			self.guildFinderEvent = lambda *arg: None

		self.GUILD_GROUP = getattr(messenger, "MESSENGER_GRUOP_INDEX_GUILD", 1)

		self.__LoadWindow()

		community.RegisterHandler(self)
		messenger.SetMessengerHandler(self)

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		community.Destroy()
		messenger.SetMessengerHandler(None)

		self.__ClearRows()
		self.mainTopics = []
		self.subTopics = []
		self.subTabHovers = []
		self.dropDownList = None
		self.statusDialog = None
		self.questionDialog = None
		self.inputDialog = None
		self.loverBar = None
		self.contextMenu = None
		self.gmPopup = None
		self.headerToolTip = None
		self.listPanel = None
		self.listPanelbg = None
		self.guildListPanel = None
		self.guildListPanelbg = None
		self.configPanel = None
		self.configScrollBar = None
		self.guildScrollBar = None
		self.scrollBar = None
		self.ClearDictionary()

	# ------------------------------------------------------------- construction
	def __LoadWindow(self):
		if self.isLoaded:
			return
		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/communitywindow.py")
		except:
			import exception
			exception.Abort("CommunityWindow.LoadWindow.LoadScriptFile")

		try:
			self.board = self.GetChild("main_bg")
			self.myInfoBar = self.GetChild("my_info_bg")
			self.dropButton = self.GetChild("my_info_state_drop_list_button")
			self.myGuildText = self.GetChild("my_info_main_player_guild_name")
			self.myNameText = self.GetChild("my_info_main_player_name")
			self.myNameCollision = self.GetChild("my_info_main_player_name_collision")
			self.statusButton = self.GetChild("my_info_my_message_button")

			self.messengerView = self.GetChild("messenger_view_window")
			self.guildView = self.GetChild("guild_view_window")
			self.configView = self.GetChild("config_view_window")

			self.subTabImages = (
				self.GetChild("messenger_friend_member_tab_image"),
				self.GetChild("messenger_block_member_tab_image"),
				self.GetChild("messenger_request_member_tab_image"),
			)

			self.subTabButtons = (
				self.GetChild("messenger_friend_member_tab_button"),
				self.GetChild("messenger_block_member_tab_button"),
				self.GetChild("messenger_request_member_tab_button"),
			)
			self.requestTwinkle = self.GetChild("community_request_button_twinkle")

			self.friendInviteButton = self.GetChild("friend_invite")
			self.friendBlockButton = self.GetChild("friend_block")
			self.friendWhisperButton = self.GetChild("friend_whisper")
			self.friendDeleteButton = self.GetChild("friend_delete")
			self.scrollBar = self.GetChild("messenger_scroll_bar")

			self.guildHasGuildWindow = self.GetChild("guild_player_has_guild_window")
			self.guildNoGuildWindow = self.GetChild("guild_player_no_guild_window")
			self.guildMemberTabButton = self.GetChild("guild_member_tab_button")
			self.guildInviteButton = self.GetChild("guild_invite")
			self.guildBlockButton = self.GetChild("guild_block")
			self.guildWhisperButton = self.GetChild("guild_whisper")
			self.guildDeleteButton = self.GetChild("guild_delete")
			self.guildInfoButton = self.GetChild("guild_info_button")
			self.guildListButton = self.GetChild("guild_view_guild_list_button")

			self.configPanel = self.GetChild("config_info_bg")
			self.configScrollBar = self.GetChild("config_scroll_bar")
			self.configSaveButton = self.GetChild("config_setting_save_button")
			self.configInitButton = self.GetChild("config_setting_init_button")

			self.mainTabImages = (
				self.GetChild("community_messenger_tab_image"),
				self.GetChild("community_guild_tab_image"),
				self.GetChild("community_config_tab_image"),
			)
			self.mainTabButtons = (
				self.GetChild("community_messenger_tab_button"),
				self.GetChild("community_guild_tab_button"),
				self.GetChild("community_config_tab_button"),
			)
			if localeinfo.IsARABIC():
				
				self.GetChild("messenger_friend_member_tab_button").LeftRightReverse()
				self.GetChild("messenger_block_member_tab_button").LeftRightReverse()
				self.GetChild("messenger_request_member_tab_button").LeftRightReverse()
				self.GetChild("guild_member_tab_image").LeftRightReverse()

				self.GetChild("guild_member_tab_button").LeftRightReverse()
				self.GetChild("guild_invite").LeftRightReverse()
				self.GetChild("guild_block").LeftRightReverse()
				self.GetChild("guild_whisper").LeftRightReverse()
				self.GetChild("guild_delete").LeftRightReverse()
				self.GetChild("guild_info_button").LeftRightReverse()
				self.GetChild("guild_view_guild_list_button").LeftRightReverse()
				

				self.GetChild("config_setting_save_button").LeftRightReverse()
				self.GetChild("config_setting_init_button").LeftRightReverse()

				self.GetChild("community_request_button_twinkle").LeftRightReverse()
				
				self.GetChild("my_info_state_drop_list_button").LeftRightReverse()

				#self.GetChild("my_info_main_player_name_collision").LeftRightReverse()
				self.GetChild("my_info_my_message_button").LeftRightReverse()

				#self.GetChild("messenger_view_window").LeftRightReverse()
				#self.GetChild("guild_view_window").LeftRightReverse()
				#self.GetChild("config_view_window").LeftRightReverse()
				

				self.GetChild("messenger_friend_member_tab_image").LeftRightReverse()
				self.GetChild("messenger_block_member_tab_image").LeftRightReverse()
				self.GetChild("messenger_request_member_tab_image").LeftRightReverse()
				self.GetChild("community_messenger_tab_image").LeftRightReverse()
				self.GetChild("community_guild_tab_image").LeftRightReverse()
				self.GetChild("community_config_tab_image").LeftRightReverse()
				self.GetChild("community_messenger_tab_button").LeftRightReverse()
				self.GetChild("community_guild_tab_button").LeftRightReverse()
				self.GetChild("community_config_tab_button").LeftRightReverse()
				
		except:
			import exception
			exception.Abort("CommunityWindow.LoadWindow.BindObject")

		self.board.SetCloseEvent(ui.__mem_func__(self.Close))

		# my_info_bg is declared before the three full-size view windows, so they cover
		# it in draw order and swallow its clicks in PickWindow's reverse child walk.
		# SetTop() needs FLAG_FLOAT. Never SetPosition() here: under an RTL parent the
		# loader stores a right-anchored m_x (x + width), which a raw x would clobber.
		self.myInfoBar.AddFlag("float")
		self.myInfoBar.SetTop()

		self.__BuildHeader()
		self.__BuildMessengerPage()
		self.__BuildGuildPage()
		self.__BuildConfigPage()
		self.__BuildMainTabs()

		self.SetMainTab(MAIN_FRIEND)
		self.SetSubTab(SUB_FRIEND)
		self.Hide()

	def __BuildHeader(self):
		self.myStateIcon = ui.ImageBox()
		self.myStateIcon.SetParent(self.myInfoBar)
		self.myStateIcon.AddFlag("not_pick")
		self.myStateIcon.SetPosition(HDR_STATE_X, HDR_STATE_Y)
		self.myStateIcon.LoadImage(STATE_GREEN)
		self.myStateIcon.Show()

		self.dropButton.SetEvent(ui.__mem_func__(self.OnPressPresence))
		self.statusButton.SetEvent(ui.__mem_func__(self.OnPressStatusMessage))

		self.myNameCollision.SetOverInEvent(ui.__mem_func__(self.__OnOverMyName))
		self.myNameCollision.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutMyName))

		self.dropDownList = StateDropDownList(self)
		# PickWindow skips a child whose rect does not contain the cursor, so a list
		# hanging below my_info_bg would never be reachable. Hang it off the board at
		# the bar's rendered offset, which RTL places differently from its uiscript x.
		self.dropDownList.SetParent(self.board)
		barX, barY = self.myInfoBar.GetGlobalPosition()
		boardX, boardY = self.board.GetGlobalPosition()
		self.dropDownList.SetPosition(int(barX - boardX) + HDR_DROP_X, int(barY - boardY) + HDR_DROP_Y)

		self.statusDialog = StatusMessageDialog(self)

	def __BuildMessengerPage(self):
		self.__BuildSearchStrip()

		self.listPanelbg = ui.ThinBoard("UI", 2)
		self.listPanelbg.SetParent(self.messengerView)
		self.listPanelbg.SetPosition(LIST_PANEL_X, LIST_PANEL_Y)
		self.listPanelbg.SetSize(LIST_PANEL_W, LIST_PANEL_H)
		self.listPanelbg.Show()

		self.listPanel = ui.Window()
		self.listPanel.SetParent(self.messengerView)
		self.listPanel.SetPosition(LIST_PANEL_X, LIST_PANEL_Y)
		self.listPanel.SetSize(LIST_PANEL_W, LIST_PANEL_H)
		self.listPanel.Show()

		hoverImages = (TAB_OVER_MEMBER, TAB_OVER_BLOCK, TAB_OVER_REQUEST)
		tooltips = (
			("COMMUNITY_MESSENGER_SUB_TAB_FRIEND", "Friend list"),
			("COMMUNITY_MESSENGER_SUB_TAB_BLOCK", "Block list"),
			("COMMUNITY_MESSENGER_SUB_TAB_REQUEST", "Friend requests"),
		)
		self.subTabHovers = []
		for index in xrange(3):
			hover = ui.ImageBox()
			hover.SetParent(self.messengerView)
			hover.AddFlag("not_pick")
			hover.LoadImage(hoverImages[index])
			hover.SetPosition(SUB_TAB_PICKER_X[index] + 1, SUB_TAB_PICKER_Y + 1)
			hover.Hide()
			self.subTabHovers.append(hover)

			button = self.subTabButtons[index]
			button.SetEvent(ui.__mem_func__(self.OnClickSubTab), index)
			button.SetOverEvent(ui.__mem_func__(self.__OnOverSubTab), index)
			button.SetOverOutEvent(ui.__mem_func__(self.__OnOverOutSubTab), index)
			key, default = tooltips[index]
			button.SetToolTipText(_L(key, default))

		self.requestTwinkle.Hide()

		self.friendInviteButton.SetEvent(ui.__mem_func__(self.OnPressAddFriend))
		self.friendInviteButton.SetToolTipText(_L("MESSENGER_ADD_FRIEND", "Add friend"))
		self.friendBlockButton.SetEvent(ui.__mem_func__(self.OnPressAddBlock))
		self.friendBlockButton.SetToolTipText(_L("HWID_BTN_BAN", "Block"))
		self.friendWhisperButton.SetEvent(ui.__mem_func__(self.OnPressWhisperSelected))
		self.friendWhisperButton.SetToolTipText(_L("COMMUNITY_MESSENGER_WHISPER", "Whisper"))
		self.friendDeleteButton.SetEvent(ui.__mem_func__(self.OnPressDeleteSelected))
		self.friendDeleteButton.SetToolTipText(_L("COMMUNITY_MESSENGER_FRIEND_DELETE", "Remove from friend list"))

		self.scrollBar.SetScrollEvent(ui.__mem_func__(self.OnScroll))
		self.scrollBar.SetPos(0)

		self.contextMenu = FriendContextMenu(self)
		self.contextMenu.SetParent(self.board)

		self.gmPopup = GMListPopup(self)
		self.gmPopup.SetParent(self.board)

	def __BuildSearchStrip(self):
		ar = localeinfo.IsARABIC()
		if ar:
			gmX = STRIP_W - GM_BTN_W
			fieldX = 0
		else:
			gmX = 0
			fieldX = GM_BTN_W + GM_BTN_GAP

		self.searchStrip = ui.Window()
		self.searchStrip.SetParent(self.messengerView)
		self.searchStrip.SetPosition(STRIP_X, STRIP_Y)
		self.searchStrip.SetSize(STRIP_W, STRIP_H)
		self.searchStrip.Show()

		self.gmButton = ui.Button()
		self.gmButton.SetParent(self.searchStrip)
		self.gmButton.SetPosition(gmX, 3)
		self.gmButton.SetUpVisual(GM_BTN_NORM)
		self.gmButton.SetOverVisual(GM_BTN_HOVER)
		self.gmButton.SetDownVisual(GM_BTN_DOWN)
		self.gmButton.SetEvent(ui.__mem_func__(self.OnPressGMList))
		self.gmButton.SetToolTipText(_L("COMMUNITY_GM_LIST_TOOLTIP", "Show online Game Masters"))
		self.gmButton.Show()

		self.searchFieldBg = ui.ImageBox()
		self.searchFieldBg.SetParent(self.searchStrip)
		self.searchFieldBg.AddFlag("not_pick")
		self.searchFieldBg.LoadImage(SEARCH_FIELD_IMG)
		self.searchFieldBg.SetPosition(fieldX, 0)
		self.searchFieldBg.Show()

		self.searchInput = ui.EditLine()
		self.searchInput.SetParent(self.searchFieldBg)
		self.searchInput.SetMax(24)
		self.searchInput.SetSize(SEARCH_EDIT_W, 17)
		self.searchInput.SetPosition(SEARCH_EDIT_X, SEARCH_EDIT_Y)
		self.searchInput.SetLimitWidth(SEARCH_EDIT_W)
		hint = _L("COMMUNITY_SEARCH_HINT", "Search...")
		if ar:
			self.searchInput.SetOverlayTextNew(hint)
		else:
			self.searchInput.SetOverlayText(hint)
		self.searchInput.SetReturnEvent(ui.__mem_func__(self.OnSearchReturn))
		self.searchInput.SetEscapeEvent(ui.__mem_func__(self.Close))
		self.searchInput.SetUpdateEvent(ui.__mem_func__(self.OnSearchUpdate))
		self.searchInput.SetOutline()
		self.searchInput.Show()

		self.searchButton = ui.Button()
		self.searchButton.SetParent(self.searchFieldBg)
		self.searchButton.SetPosition(SEARCH_MAG_X, SEARCH_MAG_Y)
		self.searchButton.SetUpVisual(BTN_SEARCH_NORM)
		self.searchButton.SetOverVisual(BTN_SEARCH_HOVER)
		self.searchButton.SetDownVisual(BTN_SEARCH_SELECT)
		self.searchButton.SetEvent(ui.__mem_func__(self.OnSearchReturn))
		self.searchButton.Show()

	def OnSearchUpdate(self):
		text = self.searchInput.GetText()
		self.searchText = text.lower() if text else ""
		self.startLine = 0
		if self.scrollBar:
			self.scrollBar.SetPos(0)
		self.__RelayoutList()

	def OnSearchReturn(self):
		self.OnSearchUpdate()

	def OnSearchEscape(self):
		self.searchInput.SetText("")
		self.searchText = ""
		self.startLine = 0
		self.__RelayoutList()
		return True

	def OnPressGMList(self):
		if hasattr(net, "SendCommunityGMListRequest"):
			net.SendCommunityGMListRequest()

	def OnCommunityGMList(self):
		if not self.gmPopup or not hasattr(community, "GetGMCount"):
			return
		entries = []
		for i in xrange(community.GetGMCount()):
			name, channel = community.GetGM(i)
			entries.append((name, channel))

		shown = min(len(entries), GM_POPUP_MAX_ROWS)
		rows = shown if shown > 0 else 1
		height = CTX_PAD * 2 + GM_POPUP_HEADER_H + GM_POPUP_ROW_H * rows

		gx, gy = self.gmButton.GetGlobalPosition()
		bx, by = self.board.GetGlobalPosition()
		lx = int(gx - bx)
		ly = int(gy - by) + GM_BTN_W + 2
		if ly + height > self.board.GetHeight():
			ly = int(gy - by) - height - 2
		if lx + GM_POPUP_W > self.board.GetWidth():
			lx = self.board.GetWidth() - GM_POPUP_W
		if lx < 0:
			lx = 0
		if ly < 0:
			ly = 0
		self.gmPopup.Open(entries, lx, ly)

	def __BuildGuildPage(self):
		
		self.guildListPanelbg = ui.ThinBoard("UI", 2)
		self.guildListPanelbg.SetParent(self.guildHasGuildWindow)
		self.guildListPanelbg.SetPosition(GUILD_LIST_PANEL_X, GUILD_LIST_PANEL_Y)
		self.guildListPanelbg.SetSize(GUILD_LIST_PANEL_W, GUILD_LIST_PANEL_H)
		self.guildListPanelbg.Show()

		self.guildListPanel = ui.Window()
		self.guildListPanel.SetParent(self.guildHasGuildWindow)
		self.guildListPanel.SetPosition(GUILD_LIST_PANEL_X, GUILD_LIST_PANEL_Y)
		self.guildListPanel.SetSize(GUILD_LIST_PANEL_W, GUILD_LIST_PANEL_H)
		self.guildListPanel.Show()

		self.guildScrollBar = ui.ScrollBar()
		self.guildScrollBar.SetParent(self.guildHasGuildWindow)
		self.guildScrollBar.SetPosition(GUILD_SCROLL_X, GUILD_SCROLL_Y)
		self.guildScrollBar.SetScrollBarSize(GUILD_SCROLL_SIZE)
		self.guildScrollBar.SetScrollEvent(ui.__mem_func__(self.OnGuildScroll))
		self.guildScrollBar.SetPos(0)
		self.guildScrollBar.Show()

		self.guildMemberTabButton.SetToolTipText(
			_L("COMMUNITY_MESSENGER_SUB_TAB_GUILD_MEMBER", "Guild members"))
		self.guildMemberTabButton.Down()

		self.guildInviteButton.SetEvent(ui.__mem_func__(self.OnPressAddFriend))
		self.guildInviteButton.SetToolTipText(_L("MESSENGER_ADD_FRIEND", "Add friend"))
		self.guildBlockButton.SetEvent(ui.__mem_func__(self.OnPressAddBlock))
		self.guildBlockButton.SetToolTipText(_L("HWID_BTN_BAN", "Block"))
		self.guildWhisperButton.SetEvent(ui.__mem_func__(self.OnPressWhisperSelected))
		self.guildWhisperButton.SetToolTipText(_L("COMMUNITY_MESSENGER_WHISPER", "Whisper"))
		self.guildDeleteButton.SetEvent(ui.__mem_func__(self.OnPressDeleteSelected))
		self.guildDeleteButton.SetToolTipText(_L("COMMUNITY_MESSENGER_FRIEND_DELETE", "Remove from friend list"))
		self.guildInfoButton.SetEvent(ui.__mem_func__(self.OnPressGuildInfo))
		if app.ENABLE_GUILD_FINDER:
			self.guildListButton.SetEvent(ui.__mem_func__(self.OnPressGuildList))
		else:
			self.guildListButton.SetEvent(ui.__mem_func__(self.OnPressGuildInfo))

	def __BuildConfigPage(self):
		self.configContent = ui.Window()
		self.configContent.SetParent(self.configPanel)
		self.configContent.SetPosition(CONFIG_CONTENT_X, 0)
		self.configContent.SetSize(CONFIG_MAIN_TOPIC_W, CONFIG_PANEL_H)
		self.configContent.Show()

		for mainKey, mainDefault, subTopicList in CONFIG_TOPICS:
			mainTopic = ConfigMainTopic(self, mainKey, mainDefault)
			mainTopic.SetParent(self.configContent)
			mainTopic.Show()

			bMasterInGameOptions = (mainKey == "COMMUNITY_CONFIG_MAIN_BLOCK")
			for subKey, subDefault, masterBit, checkItemList in subTopicList:
				subTopic = ConfigSubTopic(self, subKey, subDefault, masterBit, bMasterInGameOptions)
				mainTopic.AppendSubTopic(subTopic)
				for itemMode, bit in checkItemList:
					subTopic.AppendCheckItem(itemMode, bit)
				self.subTopics.append(subTopic)

			self.mainTopics.append(mainTopic)

		self.configContentHeight = self.__RelayoutConfig(0)

		for mainTopic in self.mainTopics:
			mainTopic.ApplyClipMask(self.configPanel)

		self.configScrollBar.SetScrollEvent(ui.__mem_func__(self.OnConfigScroll))
		self.configScrollBar.SetPos(0)

		self.configSaveButton.SetEvent(ui.__mem_func__(self.OnConfigSave))
		self.configInitButton.SetEvent(ui.__mem_func__(self.OnConfigReset))

	def __RelayoutConfig(self, scrollOffset):
		y = CONFIG_CLIP_Y - scrollOffset
		for mainTopic in self.mainTopics:
			mainTopic.SetPosition(0, int(y))
			y += mainTopic.Relayout() + CONFIG_MAIN_TOPIC_GAP
		return int(y + scrollOffset)

	def __BuildMainTabs(self):
		tooltips = (
			("COMMUNITY_MAIN_TAB_FRIEND", "Friend"),
			("COMMUNITY_MAIN_TAB_GUILD", "Guild"),
			("COMMUNITY_MAIN_TAB_CONFIG", "Options"),
		)
		for index in xrange(3):
			button = self.mainTabButtons[index]
			button.SetEvent(ui.__mem_func__(self.OnClickMainTab), index)
			key, default = tooltips[index]
			button.SetToolTipText(_L(key, default))

	# ------------------------------------------------------------- interface glue
	def SetWhisperEvent(self, event):
		self.whisperEvent = event

	def SetWhisperButtonEvent(self, event):
		self.whisperEvent = event

	def SetPartyInviteEvent(self, event):
		self.partyInviteEvent = event

	def SetGuildButtonEvent(self, event):
		self.guildButtonEvent = event

	if app.ENABLE_GUILD_FINDER:
		def SetGuildFinderEvent(self, event):
			self.guildFinderEvent = event

	def BindInterface(self, interface):
		pass

	def Show(self):
		self.RefreshAll()
		ui.ScriptWindow.Show(self)

	def Close(self):
		self.__CloseDropDown()
		if self.mainTab == MAIN_CONFIG and self.IsConfigDirty():
			self.__OpenQuestion(_L("COMMUNITY_CONFIG_QUESTION_SAVE", "Save your settings?"),
				lambda w=proxy(self): w.DoSaveAndCloseWindow(),
				lambda w=proxy(self): w.DoDiscardAndCloseWindow())
			return
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def DoSaveAndCloseWindow(self):
		net.SendCommunitySetConfig(self.workConfig)
		self.__CloseQuestion()
		self.Hide()
		return True

	def DoDiscardAndCloseWindow(self):
		self.workConfig = community.GetMyConfig()
		self.__RefreshConfigToggles()
		self.__CloseQuestion()
		self.Hide()
		return True

	def OnPressEscapeKey(self):
		self.Close()
		return True

	# ------------------------------------------------------------- lover (wedding)
	def OnAddLover(self, name, lovePoint):
		if self.loverBar:
			self.loverBar.SetLover(name, lovePoint)

	def OnUpdateLovePoint(self, lovePoint):
		if self.loverBar:
			self.loverBar.SetLovePoint(lovePoint)

	def OnLoginLover(self):
		if self.loverBar:
			self.loverBar.SetOnline(True)

	def OnLogoutLover(self):
		if self.loverBar:
			self.loverBar.SetOnline(False)

	def ClearLoverInfo(self):
		if self.loverBar:
			self.loverBar.Clear()

	# ------------------------------------------------------------- messenger handler (guild online)
	def OnLogin(self, groupIndex, key, name=None):
		if groupIndex == self.GUILD_GROUP:
			self.guildOnline[key] = True
			self.__RebuildGuild()

	def OnLogout(self, groupIndex, key, name=None):
		if groupIndex == self.GUILD_GROUP:
			self.guildOnline[key] = False
			self.__RebuildGuild()

	def OnRemoveList(self, groupIndex, key):
		if groupIndex == self.GUILD_GROUP:
			if key in self.guildOnline:
				del self.guildOnline[key]
			self.__RebuildGuild()

	def OnRemoveAllList(self, groupIndex):
		if groupIndex == self.GUILD_GROUP:
			self.guildOnline = {}
			self.__RebuildGuild()

	def RefreshMessenger(self):
		if self.isLoaded:
			self.__RebuildGuild()

	def ClearGuildMember(self):
		self.guildOnline = {}
		if self.isLoaded:
			self.__RebuildGuild()

	# ------------------------------------------------------------- community handler (C++)
	def OnCommunityRefreshAll(self):
		self.RefreshAll()

	def OnCommunityFriendUpdate(self, name):
		self.__RebuildFriends()

	def OnCommunityRequestUpdate(self):
		self.__RebuildRequests()
		self.__RefreshRequestTwinkle()
		self.RefreshRequestBadge()

	def OnCommunityMyInfo(self):
		self.workConfig = community.GetMyConfig()
		self.__RefreshHeader()
		self.__RefreshConfigToggles()

	# ------------------------------------------------------------- refresh
	def RefreshAll(self):
		if not self.isLoaded:
			return
		self.workConfig = community.GetMyConfig()
		self.__RebuildFriends()
		self.__RebuildBlocks()
		self.__RebuildRequests()
		messenger.RefreshGuildMember()
		self.__RebuildGuild()
		self.__RefreshHeader()
		self.__RefreshConfigToggles()
		self.__RefreshRequestTwinkle()
		self.RefreshRequestBadge()

	def __RefreshHeader(self):
		self.myNameText.SetText(player.GetName())
		guildName = guild.GetGuildName()
		if guildName:
			self.myGuildText.SetText(guildName)
		else:
			self.myGuildText.SetText(_L("COMMUNITY_NO_GUILD", "No guild"))
		self.myStateIcon.LoadImage(GetStateImage(community.GetMyPresence()))

		statusMessage = community.GetMyStatusMessage()
		if statusMessage:
			self.statusButton.SetToolTipText(statusMessage)
		else:
			self.statusButton.SetToolTipText(
				_L("COMMUNITY_MOUSE_OVER_IN_STATUS_MESSAGE_BUTTON", "Set a status message"))

	def __OnOverMyName(self):
		point, grade = player.GetAlignmentData()
		if grade >= len(localeinfo.ALIGNMENT_GRADE_THRESHOLDS) - 1:
			return
		if app.ENABLE_GENDER_ALIGNMENT:
			title = localeinfo.GetAlignmentTitleName(point)
		else:
			title = localeinfo.TITLE_NAME_LIST[grade]
		fmt = _L("ALIGNMENT_TOOLTIP_PROGRESS", "%d / %d")
		progress = fmt % (point, localeinfo.ALIGNMENT_GRADE_THRESHOLDS[grade])
		self.headerToolTip.Show((title, progress), HDR_ALIGNMENT_TOOLTIP_W)

	def __OnOverOutMyName(self):
		self.headerToolTip.Hide()

	def __ClearRows(self):
		self.rows = []
		self.friendRows = {}
		self.blockRows = {}
		self.requestRows = {}
		self.guildRows = {}

	def __RebuildFriends(self):
		for row in self.friendRows.itervalues():
			row.Hide()
		self.friendRows = {}
		self.friendOrder = []

		count = community.GetFriendCount()
		for i in xrange(count):
			name, presence, level, job, empire, channel, mapIndex, favorite, statusMessage = community.GetFriend(i)
			row = FriendRow(self)
			row.SetParent(self.listPanel)
			row.SetData(name, presence, level, favorite, statusMessage, channel, mapIndex, empire, job)
			self.friendRows[name] = row
			self.friendOrder.append(name)

		def _key(name):
			row = self.friendRows[name]
			return (0 if row.isFavorite else 1, 0 if row.IsOnline() else 1, name.lower())

		self.friendOrder.sort(key=_key)
		self.__RelayoutList()

	def __RebuildBlocks(self):
		for row in self.blockRows.itervalues():
			row.Hide()
		self.blockRows = {}
		self.blockOrder = []

		count = community.GetBlockCount()
		for i in xrange(count):
			name, connected = community.GetBlock(i)
			row = BlockRow(self)
			row.SetParent(self.listPanel)
			row.SetData(name, connected)
			self.blockRows[name] = row
			self.blockOrder.append(name)

		self.blockOrder.sort(key=lambda n: n.lower())
		self.__RelayoutList()

	def __RebuildRequests(self):
		for row in self.requestRows.itervalues():
			row.Hide()
		self.requestRows = {}
		self.requestOrder = []

		count = community.GetRequestCount()
		for i in xrange(count):
			name, level, createdAt = community.GetRequest(i)
			row = RequestRow(self)
			row.SetParent(self.listPanel)
			row.SetData(name, level)
			self.requestRows[name] = row
			self.requestOrder.append(name)

		self.__RelayoutList()

	def __RebuildGuild(self):
		if not self.isLoaded:
			return
		for row in self.guildRows.itervalues():
			row.Hide()
		self.guildRows = {}
		self.guildOrder = []

		myName = player.GetName()
		count = guild.GetMemberCount()
		for i in xrange(count):
			data = guild.GetMemberData(i)
			name = data[1]
			level = data[4]
			if not name or name == myName:
				continue
			online = self.guildOnline.get(name, False)
			race = data[3]
			row = GuildRow(self)
			row.SetParent(self.guildListPanel)
			row.SetData(name, level, online, race)
			self.guildRows[name] = row
			self.guildOrder.append(name)

		self.guildOrder.sort(key=lambda n: (0 if self.guildOnline.get(n, False) else 1, n.lower()))
		self.__RelayoutGuildList()
		self.__RefreshGuildPage()

	def __RefreshGuildPage(self):
		if guild.GetGuildID():
			self.guildHasGuildWindow.Show()
			self.guildNoGuildWindow.Hide()
		else:
			self.guildHasGuildWindow.Hide()
			self.guildNoGuildWindow.Show()

	# ------------------------------------------------------------- list layout / scroll
	def __ActiveOrder(self):
		if self.subTab == SUB_BLOCK:
			order, rows = self.blockOrder, self.blockRows
		elif self.subTab == SUB_REQUEST:
			order, rows = self.requestOrder, self.requestRows
		else:
			order, rows = self.friendOrder, self.friendRows
		if self.searchText:
			order = [name for name in order if self.searchText in name.lower()]
		return order, rows

	def __RelayoutList(self):
		order, rows = self.__ActiveOrder()

		for group in (self.friendRows, self.blockRows, self.requestRows):
			for row in group.itervalues():
				row.Hide()

		total = len(order)
		maxStart = max(0, total - VISIBLE_ROWS)
		if self.startLine > maxStart:
			self.startLine = maxStart

		for index in xrange(VISIBLE_ROWS):
			dataIndex = self.startLine + index
			if dataIndex >= total:
				break
			name = order[dataIndex]
			row = rows[name]
			row.SetPosition(MEMBER_INFO_BAR_DEFAULT_X, LIST_ROW_Y_OFFSET + index * LIST_LINE_HEIGHT)
			row.SetSelected(name == self.selectedName)
			row.Show()

		if total > VISIBLE_ROWS:
			self.scrollBar.SetMiddleBarSize(float(VISIBLE_ROWS) / float(total))
			self.scrollBar.Show()
		else:
			self.scrollBar.Hide()

	def __RelayoutGuildList(self):
		for row in self.guildRows.itervalues():
			row.Hide()

		total = len(self.guildOrder)
		maxStart = max(0, total - VISIBLE_ROWS)
		if self.guildStartLine > maxStart:
			self.guildStartLine = maxStart

		for index in xrange(VISIBLE_ROWS):
			dataIndex = self.guildStartLine + index
			if dataIndex >= total:
				break
			name = self.guildOrder[dataIndex]
			row = self.guildRows[name]
			row.SetPosition(MEMBER_INFO_BAR_DEFAULT_X, LIST_ROW_Y_OFFSET + index * LIST_LINE_HEIGHT)
			row.SetSelected(name == self.selectedName)
			row.Show()

		if total > VISIBLE_ROWS:
			self.guildScrollBar.SetMiddleBarSize(float(VISIBLE_ROWS) / float(total))
			self.guildScrollBar.Show()
		else:
			self.guildScrollBar.Hide()

	def OnScroll(self):
		self.__CloseDropDown()
		order, rows = self.__ActiveOrder()
		maxStart = max(0, len(order) - VISIBLE_ROWS)
		self.startLine = int(self.scrollBar.GetPos() * maxStart + 0.5)
		self.__RelayoutList()

	def OnGuildScroll(self):
		maxStart = max(0, len(self.guildOrder) - VISIBLE_ROWS)
		self.guildStartLine = int(self.guildScrollBar.GetPos() * maxStart + 0.5)
		self.__RelayoutGuildList()

	def __ScrollRows(self, scrollBar, startLine, total, delta):
		maxStart = max(0, total - VISIBLE_ROWS)
		if maxStart <= 0:
			return
		newStart = min(maxStart, max(0, startLine + delta))
		scrollBar.SetPos(float(newStart) / float(maxStart))

	def OnRunMouseWheel(self, nLen):
		delta = -SCROLL_STEP_COUNT if nLen > 0 else SCROLL_STEP_COUNT
		if self.mainTab == MAIN_CONFIG:
			step = -CONFIG_SCROLL_STEP if nLen > 0 else CONFIG_SCROLL_STEP
			self.configScrollBar.SetPos(min(1.0, max(0.0, self.configScrollBar.GetPos() + step)))
		elif self.mainTab == MAIN_GUILD:
			self.__ScrollRows(self.guildScrollBar, self.guildStartLine, len(self.guildOrder), delta)
		else:
			order, rows = self.__ActiveOrder()
			self.__ScrollRows(self.scrollBar, self.startLine, len(order), delta)
		return True

	def OnConfigScroll(self):
		viewHeight = CONFIG_PANEL_H - CONFIG_CLIP_Y
		maxOffset = max(0, self.configContentHeight - viewHeight)
		offset = int(self.configScrollBar.GetPos() * maxOffset + 0.5)
		self.__RelayoutConfig(offset)

	# ------------------------------------------------------------- tabs
	def SetMainTab(self, index):
		self.mainTab = index
		for i in xrange(3):
			if i == index:
				self.mainTabImages[i].Show()
				self.mainTabButtons[i].Down()
			else:
				self.mainTabImages[i].Hide()
				self.mainTabButtons[i].SetUp()

		self.messengerView.Hide()
		self.guildView.Hide()
		self.configView.Hide()

		if index == MAIN_CONFIG:
			self.__CloseDropDown()
			self.statusDialog.Close()
			self.myInfoBar.Hide()
		else:
			self.myInfoBar.Show()

		if index == MAIN_FRIEND:
			self.messengerView.Show()
		elif index == MAIN_GUILD:
			self.guildView.Show()
			self.__RefreshGuildPage()
		else:
			self.configView.Show()

	def SetSubTab(self, index):
		self.subTab = index
		self.startLine = 0
		self.selectedName = ""
		for i in xrange(3):
			if i == index:
				self.subTabImages[i].Show()
				self.subTabButtons[i].Down()
			else:
				self.subTabImages[i].Hide()
				self.subTabButtons[i].SetUp()

		self.scrollBar.SetPos(0)
		self.__RelayoutList()
		self.__RefreshRequestTwinkle()

	def IsConfigDirty(self):
		return self.workConfig != community.GetMyConfig()

	def OnClickMainTab(self, index):
		self.__CloseDropDown()
		if self.mainTab == MAIN_CONFIG and index != MAIN_CONFIG and self.IsConfigDirty():
			self.__OpenQuestion(_L("COMMUNITY_CONFIG_QUESTION_SAVE", "Save your settings?"),
				lambda i=index, w=proxy(self): w.DoSaveAndLeaveConfig(i),
				lambda i=index, w=proxy(self): w.DoDiscardAndLeaveConfig(i))
			return
		self.SetMainTab(index)

	def DoSaveAndLeaveConfig(self, index):
		net.SendCommunitySetConfig(self.workConfig)
		self.__CloseQuestion()
		self.SetMainTab(index)
		return True

	def DoDiscardAndLeaveConfig(self, index):
		self.workConfig = community.GetMyConfig()
		self.__RefreshConfigToggles()
		self.__CloseQuestion()
		self.SetMainTab(index)
		return True

	def OnClickSubTab(self, index):
		self.__CloseDropDown()
		self.SetSubTab(index)

	def __OnOverSubTab(self, index):
		if index != self.subTab:
			self.subTabHovers[index].Show()

	def __OnOverOutSubTab(self, index):
		self.subTabHovers[index].Hide()

	def __RefreshRequestTwinkle(self):
		self.twinkleActive = (community.GetRequestCount() > 0 and self.subTab != SUB_REQUEST)
		if not self.twinkleActive:
			self.requestTwinkle.Hide()

	def RefreshRequestBadge(self):
		if self.IsShow():
			uibadge.SetCount("messenger", 0)
		else:
			uibadge.SetCount("messenger", community.GetRequestCount())

	def OnUpdate(self):
		if not self.twinkleActive:
			return

		now = app.GetTime()
		if now - self.lastTwinkleTime < TWINKLE_TIME_INTERVAL:
			return

		self.lastTwinkleTime = now
		self.twinkleShown = not self.twinkleShown
		if self.twinkleShown:
			self.requestTwinkle.Show()
		else:
			self.requestTwinkle.Hide()

	# ------------------------------------------------------------- selection + toolbar
	def OnSelectRow(self, name):
		self.__CloseDropDown()
		self.selectedName = name
		self.__RelayoutList()
		self.__RelayoutGuildList()

	def __GetSelectedName(self):
		return self.selectedName

	def OnPressWhisperSelected(self):
		name = self.__GetSelectedName()
		if name:
			self.whisperEvent(name)

	def OnPressDeleteSelected(self):
		name = self.__GetSelectedName()
		if not name:
			return
		if self.subTab == SUB_BLOCK and self.mainTab == MAIN_FRIEND:
			self.OnRowBlockDelete(name)
		elif self.subTab == SUB_REQUEST and self.mainTab == MAIN_FRIEND:
			self.OnRowRequestRefuse(name)
		else:
			self.OnRowFriendDelete(name)

	def OnPressAddFriend(self):
		name = self.__GetSelectedName()
		if name:
			net.SendCommunityRequestByName(name)
			return
		self.__OpenInput(_L("MESSENGER_ADD_FRIEND", "Add friend"),
			ui.__mem_func__(self.__OnAcceptAddFriend))

	def __OnAcceptAddFriend(self):
		name = self.inputDialog.GetText()
		self.__CloseInput()
		if name:
			net.SendCommunityRequestByName(name)
		return True

	def OnPressAddBlock(self):
		name = self.__GetSelectedName()
		if name:
			net.SendCommunityBlockAddByName(name)
			return
		self.__OpenInput(_L("HWID_BTN_BAN", "Block"),
			ui.__mem_func__(self.__OnAcceptAddBlock))

	def __OnAcceptAddBlock(self):
		name = self.inputDialog.GetText()
		self.__CloseInput()
		if name:
			net.SendCommunityBlockAddByName(name)
		return True

	def OnPressGuildInfo(self):
		self.guildButtonEvent()

	if app.ENABLE_GUILD_FINDER:
		def OnPressGuildList(self):
			# the no-guild panel's only outcome used to be the "you have no guild" chat line
			if not guild.GetGuildID():
				self.guildFinderEvent()
				return
			self.guildButtonEvent()

	# ------------------------------------------------------------- row actions
	def OnRowWhisper(self, name):
		self.whisperEvent(name)

	def OnRowBlockAdd(self, name):
		net.SendCommunityBlockAddByName(name)

	def OnRowContext(self, name, favorite, online, gx, gy):
		self.selectedName = name
		self.__RelayoutList()
		bx, by = self.board.GetGlobalPosition()
		lx = int(gx - bx)
		ly = int(gy - by)
		if ly + CTX_MENU_H > self.board.GetHeight():
			ly = ly - CTX_MENU_H
		if lx + CTX_MENU_W > self.board.GetWidth():
			lx = self.board.GetWidth() - CTX_MENU_W
		if lx < 0:
			lx = 0
		if ly < 0:
			ly = 0
		self.contextMenu.Open(name, favorite, online, lx, ly)

	def OnRowParty(self, name):
		self.partyInviteEvent(name)

	def OnRowFriendDelete(self, name):
		self.__OpenQuestion(
			_L("COMMUNITY_MESSENGER_FRIEND_DELETE", "Remove from friend list"),
			lambda n=name, s=proxy(self): s.DoFriendDelete(n))

	def DoFriendDelete(self, name):
		net.SendCommunityFriendDelete(name)
		self.__CloseQuestion()
		return True

	def OnRowBlockDelete(self, name):
		net.SendCommunityBlockDelete(name)

	def OnRowRequestAccept(self, name):
		net.SendCommunityRequestAccept(name)

	def OnRowRequestRefuse(self, name):
		net.SendCommunityRequestRefuse(name)

	def OnRowFavorite(self, name, favorite):
		if favorite:
			text = _L("COMMUNITY_ADD_FAVORITE_QUESTION", "Add this player to your favorites?")
		else:
			text = _L("COMMUNITY_DELETE_FAVORITE_QUESTION", "Remove this player from your favorites?")
		self.__OpenQuestion(text, lambda n=name, f=favorite, s=proxy(self): s.DoFavorite(n, f))

	def DoFavorite(self, name, favorite):
		net.SendCommunityFavorite(name, int(favorite))
		self.__CloseQuestion()
		return True

	# ------------------------------------------------------------- presence + status
	def OnPressPresence(self):
		self.dropDownList.Toggle()

	def __CloseDropDown(self):
		if self.dropDownList:
			self.dropDownList.Hide()
		if self.contextMenu:
			self.contextMenu.Hide()
		if self.gmPopup:
			self.gmPopup.Hide()

	def OnSelectPresence(self, state):
		if state in STATE_CONFIRM_KEY:
			key, default = STATE_CONFIRM_KEY[state]
			self.__OpenQuestion(_L(key, default),
				lambda s=state, w=proxy(self): w.DoSetPresence(s))
			return
		self.DoSetPresence(state)

	def DoSetPresence(self, state):
		net.SendCommunitySetPresence(state)
		self.__CloseQuestion()
		return True

	def OnPressStatusMessage(self):
		self.statusDialog.Open(community.GetMyStatusMessage())

	def OnApplyStatusMessage(self, text):
		net.SendCommunitySetStatusMessage(text)

	# ------------------------------------------------------------- config
	def OnToggleConfigFlag(self, bit):
		if (self.workConfig & bit) != 0:
			self.workConfig &= ~bit
		else:
			self.workConfig |= bit
		self.__RefreshConfigToggles()

	def __RefreshConfigToggles(self):
		for mainTopic in self.mainTopics:
			mainTopic.UpdateByFlag(self.workConfig)

	def OnConfigSave(self):
		# Reference saves directly on click; only Reset is confirmed.
		net.SendCommunitySetConfig(self.workConfig)

	def DoConfigSave(self):
		net.SendCommunitySetConfig(self.workConfig)
		self.__CloseQuestion()
		return True

	def OnConfigReset(self):
		self.__OpenQuestion(_L("COMMUNITY_CONFIG_INIT_QUESTION", "Reset your settings?"),
			lambda s=proxy(self): s.DoConfigReset())

	def DoConfigReset(self):
		self.workConfig = community.COMMUNITY_CFG_DEFAULT
		net.SendCommunitySetConfig(self.workConfig)
		self.__RefreshConfigToggles()
		self.__CloseQuestion()
		return True

	# ------------------------------------------------------------- dialogs
	def __OpenQuestion(self, text, acceptEvent, cancelEvent=None):
		self.__CloseQuestion()
		dialog = uicommon.QuestionDialog()
		dialog.SetText(text)
		dialog.SetAcceptEvent(acceptEvent)
		if cancelEvent:
			dialog.SetCancelEvent(cancelEvent)
		else:
			dialog.SetCancelEvent(ui.__mem_func__(self.__CloseQuestion))
		dialog.Open()
		self.questionDialog = dialog

	def __CloseQuestion(self):
		if self.questionDialog:
			self.questionDialog.Close()
			self.questionDialog = None
		return True

	def __OpenInput(self, title, acceptEvent):
		self.__CloseInput()
		dialog = uicommon.InputDialog()
		dialog.SetTitle(title)
		dialog.SetMaxLength(12)
		dialog.SetAcceptEvent(acceptEvent)
		dialog.SetCancelEvent(ui.__mem_func__(self.__CloseInput))
		dialog.Open()
		self.inputDialog = dialog

	def __CloseInput(self):
		if self.inputDialog:
			self.inputDialog.Close()
			self.inputDialog = None
		return True
