# coding: latin_1

import app
import re
import time
import ui
import net
import chat
import player
import ime
import localeinfo
import osfinfo
import uicommon
import constinfo
import messagescache
from _weakref import proxy

IMG_DIR = "d:/ymir work/ui/game/whisper/"

COLOR_CODE_PATTERN = re.compile(r"\|c[0-9a-fA-F]{8}")
HYPERLINK_PATTERN = re.compile(r"\|H[^|]*\|h")

def MakePlainText(text):
	if "|" not in text:
		return text
	text = COLOR_CODE_PATTERN.sub("", text)
	text = HYPERLINK_PATTERN.sub("", text)
	return text.replace("|h", "").replace("|r", "")

# survives the per-teleport interface rebuild; owner-keyed so it never bleeds
# across a character switch within the same client process
_minimizedOwner = ""
_minimizedName = ""

def SetMinimizedConversation(name):
	global _minimizedOwner, _minimizedName
	_minimizedOwner = player.GetName()
	_minimizedName = name

def GetMinimizedConversation():
	if _minimizedName and _minimizedOwner == player.GetName():
		return _minimizedName
	return ""

def ClearMinimizedConversation(name):
	global _minimizedOwner, _minimizedName
	if _minimizedName == name:
		_minimizedOwner = ""
		_minimizedName = ""

def ListRestoreButtons():
	result = []
	minimizedName = GetMinimizedConversation()
	for conv in messagescache.ListConversations():
		name, direction, epoch = conv[0], conv[1], conv[3]
		unread = (direction == messagescache.DIR_THEIRS
			and epoch > messagescache.GetSeenTime(name))
		if unread:
			result.append((name, True))
		elif name == minimizedName:
			result.append((name, False))
	return result

# >>> BUBBLES BEGIN - ChatTextRenderer (CWhisper-backed transcript) replaced by the
# MessageBubble transcript below; hyperlink hover/click interactivity returns in a later
# increment at bubble level. See docs/MESSENGER_RENEWAL.md. (disabled)
# class ChatTextRenderer(ui.Window):
# 	def __init__(self):
# 		ui.Window.__init__(self)
# 		self.targetName = ""
# 		self.interface = None
# 		self.scrollCallback = None
#
# 	def SetTargetName(self, targetName):
# 		self.targetName = targetName
#
# 	def SetInterface(self, interface):
# 		self.interface = interface
#
# 	def SetScrollCallback(self, callback):
# 		self.scrollCallback = callback
#
# 	def OnRender(self):
# 		if self.targetName:
# 			(x, y) = self.GetGlobalPosition()
# 			if localeinfo.IsARABIC():
# 				chat.RenderWhisper(self.targetName, x + self.GetWidth(), y)
# 			else:
# 				chat.RenderWhisper(self.targetName, x, y)
#
# 	def OnMouseWheel(self, length):
# 		if self.scrollCallback:
# 			return self.scrollCallback(length)
# 		return False
#
# 	def OnMouseLeftButtonDown(self):
# 		hyperlink = ui.GetHyperlink()
# 		if hyperlink:
# 			if app.IsPressed(app.DIK_LALT):
# 				link = chat.GetLinkFromHyperlink(hyperlink)
# 				ime.PasteString(link)
# 			elif self.interface:
# 				self.interface.MakeHyperlinkTooltip(hyperlink)
#
# 	def OnMouseRightButtonDown(self):
# 		if app.ENABLE_INGAME_WIKI and app.IsPressed(app.DIK_LSHIFT):
# 			hyperlink = ui.GetHyperlink()
# 			if hyperlink and self.interface:
# 				self.interface.OpenWikiFromHyperlink(hyperlink)
# <<< BUBBLES END

class BubbleBoard(ui.Window):
	# new_thinboard art at half scale: 8px slices keep the textured look intact on
	# slim bubble heights where the 16px v2 slices degenerate
	SLICE = 8
	PATTERN_DIR = "d:/ymir work/ui/game/whisper/bubble/"
	BASE_TILE = 16.0

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self):
		ui.Window.__init__(self, "UI")

		self.Corners = []
		for name in ["lefttop", "leftbottom", "righttop", "rightbottom"]:
			piece = ui.ExpandedImageBox()
			piece.SetParent(self)
			piece.AddFlag("attach")
			piece.AddFlag("not_pick")
			piece.LoadImage(self.PATTERN_DIR + "thinboard_corner_" + name + ".png")
			piece.SetPosition(0, 0)
			piece.Show()
			self.Corners.append(piece)

		self.Lines = []
		for name in ["left", "right", "top", "bottom"]:
			piece = ui.ExpandedImageBox()
			piece.SetParent(self)
			piece.AddFlag("attach")
			piece.AddFlag("not_pick")
			piece.LoadImage(self.PATTERN_DIR + "thinboard_line_" + name + ".png")
			piece.SetPosition(0, 0)
			piece.Show()
			self.Lines.append(piece)

		self.Base = ui.ExpandedImageBox()
		self.Base.SetParent(self)
		self.Base.AddFlag("attach")
		self.Base.AddFlag("not_pick")
		self.Base.LoadImage(self.PATTERN_DIR + "base.png")
		self.Base.SetPosition(self.SLICE, self.SLICE)
		self.Base.Show()

	def SetSize(self, width, height):
		s = self.SLICE
		width = max(s * 3, width)
		height = max(s * 3, height)
		ui.Window.SetSize(self, width, height)

		self.Corners[self.LB].SetPosition(0, height - s)
		self.Corners[self.RT].SetPosition(width - s, 0)
		self.Corners[self.RB].SetPosition(width - s, height - s)
		self.Lines[self.L].SetPosition(0, s)
		self.Lines[self.T].SetPosition(s, 0)
		self.Lines[self.R].SetPosition(width - s, s)
		self.Lines[self.B].SetPosition(s, height - s)

		# under USE_CLIP_MASK the masked ExpandedImageBox render path ignores
		# SetRenderingRect (GrpExpandedImageInstance builds the quad from image size x
		# scale only) - SetScale is honored on both paths, so stretch via scale
		lineVert = float(height - s * 2) / s
		lineHorz = float(width - s * 2) / s
		self.Lines[self.L].SetScale(1.0, lineVert)
		self.Lines[self.R].SetScale(1.0, lineVert)
		self.Lines[self.T].SetScale(lineHorz, 1.0)
		self.Lines[self.B].SetScale(lineHorz, 1.0)

		self.Base.SetPosition(s, s)
		self.Base.SetScale(float(width - s * 2) / self.BASE_TILE, float(height - s * 2) / self.BASE_TILE)

	def SetTint(self, r, g, b):
		for piece in self.Corners + self.Lines:
			piece.SetDiffuseColor(r, g, b, 1.0)
		self.Base.SetDiffuseColor(r, g, b, 1.0)

ADV_IMG_DIR = "d:/ymir work/ui/game/advanced_game_options/"

class AdvScrollBar(ui.Window):
	# copy of uiadvancedgameoptions.py's local ScrollBarNew (same precedent as
	# ingamewikiui_new.AdvScrollBar), widened to 10px for the messenger
	SCROLLBAR_WIDTH = 10
	SCROLL_BTN_XDIST = 1
	SCROLL_BTN_YDIST = 1

	class MiddleBar(ui.DragButton):
		def __init__(self):
			ui.DragButton.__init__(self)
			self.AddFlag("movable")
			self.SetWindowName("scrollbar_middlebar")

		def MakeImage(self):
			top = ui.ExpandedImageBox()
			top.SetParent(self)
			top.LoadImage(ADV_IMG_DIR + "scrollbar/scrollbar_top.tga")
			top.AddFlag("not_pick")
			top.Show()
			topScale = ui.ExpandedImageBox()
			topScale.SetParent(self)
			topScale.SetPosition(0, top.GetHeight())
			topScale.LoadImage(ADV_IMG_DIR + "scrollbar/scrollbar_scale.tga")
			topScale.AddFlag("not_pick")
			topScale.Show()
			bottom = ui.ExpandedImageBox()
			bottom.SetParent(self)
			bottom.LoadImage(ADV_IMG_DIR + "scrollbar/scrollbar_bottom.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()
			bottomScale = ui.ExpandedImageBox()
			bottomScale.SetParent(self)
			bottomScale.LoadImage(ADV_IMG_DIR + "scrollbar/scrollbar_scale.tga")
			bottomScale.AddFlag("not_pick")
			bottomScale.Show()
			middle = ui.ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage(ADV_IMG_DIR + "scrollbar/scrollbar_mid.tga")
			middle.AddFlag("not_pick")
			middle.Show()
			self.top = top
			self.topScale = topScale
			self.bottom = bottom
			self.bottomScale = bottomScale
			self.middle = middle

		def SetSize(self, height):
			minHeight = self.top.GetHeight() + self.bottom.GetHeight() + self.middle.GetHeight()
			height = max(minHeight, height)
			ui.DragButton.SetSize(self, 10, height)
			scale = (height - minHeight) / 2
			extraScale = 0
			if (height - minHeight) % 2 == 1:
				extraScale = 1
			self.topScale.SetRenderingRect(0, 0, 0, scale - 1)
			self.middle.SetPosition(0, self.top.GetHeight() + scale)
			self.bottomScale.SetPosition(0, self.middle.GetBottom())
			self.bottomScale.SetRenderingRect(0, 0, 0, scale - 1 + extraScale)
			self.bottom.SetPosition(0, height - self.bottom.GetHeight())

	def __init__(self):
		ui.Window.__init__(self)
		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = None
		self.eventArgs = None
		self.lockFlag = False
		self.CreateScrollBar()
		self.SetScrollBarSize(0)
		self.scrollStep = 0.4
		self.SetWindowName("AdvScrollBar")

	def __del__(self):
		ui.Window.__del__(self)

	def CreateScrollBar(self):
		topImage = ui.ExpandedImageBox()
		topImage.SetParent(self)
		topImage.AddFlag("not_pick")
		topImage.LoadImage(ADV_IMG_DIR + "scrollbar/scroll_top.tga")
		topImage.Show()
		bottomImage = ui.ExpandedImageBox()
		bottomImage.SetParent(self)
		bottomImage.AddFlag("not_pick")
		bottomImage.LoadImage(ADV_IMG_DIR + "scrollbar/scroll_bottom.tga")
		bottomImage.Show()
		middleImage = ui.ExpandedImageBox()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, topImage.GetHeight())
		middleImage.LoadImage(ADV_IMG_DIR + "scrollbar/scroll_mid.tga")
		middleImage.Show()
		self.topImage = topImage
		self.bottomImage = bottomImage
		self.middleImage = middleImage
		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(ui.__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(12)
		self.middleBar = middleBar

	def Destroy(self):
		self.eventScroll = None
		self.eventArgs = None

	def SetScrollEvent(self, event, *args):
		self.eventScroll = event
		self.eventArgs = args

	def SetMiddleBarSize(self, pageScale):
		self.middleBar.SetSize(int(pageScale * float(self.GetHeight() - (self.SCROLL_BTN_YDIST * 2))))
		realHeight = self.GetHeight() - (self.SCROLL_BTN_YDIST * 2) - self.middleBar.GetHeight()
		self.pageSize = realHeight

	def SetScrollBarSize(self, height):
		self.SetSize(self.SCROLLBAR_WIDTH, height)
		self.pageSize = height - self.SCROLL_BTN_YDIST * 2 - self.middleBar.GetHeight()
		middleImageScale = float((height - self.SCROLL_BTN_YDIST * 2) - self.middleImage.GetHeight()) / float(self.middleImage.GetHeight())
		self.middleImage.SetRenderingRect(0, 0, 0, middleImageScale)
		self.bottomImage.SetPosition(0, height - self.bottomImage.GetHeight())
		self.middleBar.SetRestrictMovementArea(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST,
			self.middleBar.GetWidth(), height - self.SCROLL_BTN_YDIST * 2)
		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST)

	def SetScrollStep(self, step):
		self.scrollStep = step

	def OnUp(self):
		self.SetPos(self.curPos - self.scrollStep)

	def OnDown(self):
		self.SetPos(self.curPos + self.scrollStep)

	def GetScrollStep(self):
		return self.scrollStep

	def GetPos(self):
		return self.curPos

	def SetPos(self, pos, moveEvent=True):
		pos = max(0.0, pos)
		pos = min(1.0, pos)
		newPos = float(self.pageSize) * pos
		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, int(newPos) + self.SCROLL_BTN_YDIST)
		if moveEvent == True:
			self.OnMove()
		else:
			self.curPos = pos

	def OnMove(self):
		if self.lockFlag:
			return
		if 0 == self.pageSize:
			return
		(xLocal, yLocal) = self.middleBar.GetLocalPosition()
		self.curPos = float(yLocal - self.SCROLL_BTN_YDIST) / float(self.pageSize)
		if self.eventScroll:
			apply(self.eventScroll, self.eventArgs)

	def OnMouseLeftButtonDown(self):
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		newPos = float(yMouseLocalPosition) / float(self.GetHeight())
		self.SetPos(newPos)

	def LockScroll(self):
		self.lockFlag = True

	def UnlockScroll(self):
		self.lockFlag = False

	def OnRunMouseWheel(self, nLen):
		if not self.IsInPosition():
			return False
		if nLen > 0:
			self.OnUp()
			return True
		elif nLen < 0:
			self.OnDown()
			return True
		return False

class WheelWindow(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.wheelCallback = None
		self.interface = None

	def SetWheelCallback(self, callback):
		self.wheelCallback = callback

	def SetInterfaceRef(self, interface):
		self.interface = interface

	# bubble text lines stay not_pick; the engine's per-instance hyperlink
	# hover hit-test (ui.GetHyperlink) does the precision work, the viewport
	# just receives the click - same pattern as the old ChatTextRenderer
	def OnMouseLeftButtonDown(self):
		hyperlink = ui.GetHyperlink()
		if hyperlink:
			if app.IsPressed(app.DIK_LALT):
				link = chat.GetLinkFromHyperlink(hyperlink)
				ime.PasteString(link)
			elif self.interface:
				self.interface.MakeHyperlinkTooltip(hyperlink)

	def OnMouseRightButtonDown(self):
		if app.ENABLE_INGAME_WIKI and app.IsPressed(app.DIK_LSHIFT):
			hyperlink = ui.GetHyperlink()
			if hyperlink and self.interface:
				self.interface.OpenWikiFromHyperlink(hyperlink)

	def OnMouseWheel(self, length):
		if self.wheelCallback:
			return self.wheelCallback(length)
		return False

	# ENABLE_REVIEWED_MOUSEWHEEL clients dispatch wheel via OnRunMouseWheel
	# tree traversal, not OnMouseWheel - gate on hover like AdvScrollBar
	def OnRunMouseWheel(self, nLen):
		if not self.IsInPosition():
			return False
		if self.wheelCallback:
			return self.wheelCallback(nLen)
		return False

class ConvRow(ui.Window):
	# conv_item art geometry: name strip x29-130/y15-35 with the avatar slot to
	# its left, preview inset x7-167/y45-68
	WIDTH = 175
	HEIGHT = 78

	def __init__(self):
		ui.Window.__init__(self)
		self.contactName = ""
		self.isGM = False
		self.selected = False
		self.hovered = False
		self.clickEvent = None
		self.deleteEvent = None
		self.wheelEvent = None
		self.SetSize(self.WIDTH, self.HEIGHT)

		self.bg = ui.ExpandedImageBox()
		self.bg.SetParent(self)
		self.bg.AddFlag("not_pick")
		self.bg.SetPosition(0, 0)
		self.bg.Show()

		self.avatar = ui.ExpandedImageBox()
		self.avatar.SetParent(self)
		self.avatar.AddFlag("not_pick")
		self.avatar.SetPosition(1, 12)
		self.avatar.Hide()

		arabic = localeinfo.IsARABIC()
		smallFont = getattr(localeinfo, "UI_DEF_FONT_SMALL", None)

		self.statusDot = ui.ExpandedImageBox()
		self.statusDot.SetParent(self)
		self.statusDot.AddFlag("not_pick")
		self.statusDot.SetPosition(19, 28)
		self.statusDot.Hide()

		self.unreadIcon = ui.ExpandedImageBox()
		self.unreadIcon.SetParent(self)
		self.unreadIcon.AddFlag("not_pick")
		self.unreadIcon.LoadImage(IMG_DIR + "mp_close.png")
		self.unreadIcon.SetScale(0.6, 0.6)
		if arabic:
			self.unreadIcon.SetPosition(5, 2)
		else:
			self.unreadIcon.SetPosition(156, 2)
		self.unreadIcon.Hide()

		self.nameLine = ui.TextLine()
		self.nameLine.SetParent(self)
		self.nameLine.AddFlag("not_pick")
		self.nameLine.SetFontColor(0.878, 0.800, 0.733)
		self.nameLine.SetOutline()
		if arabic:
			self.nameLine.SetPosition(126, 18)
		else:
			self.nameLine.SetPosition(34, 18)
		self.nameLine.Show()

		self.timeLine = ui.TextLine()
		self.timeLine.SetParent(self)
		self.timeLine.AddFlag("not_pick")
		if smallFont:
			self.timeLine.SetFontName(smallFont)
		self.timeLine.SetFontColor(0.620, 0.550, 0.500)
		# right edge at x=169 on both locales: en ALIGN_RIGHT anchors right,
		# ae default align already anchors right
		if not arabic:
			self.timeLine.SetHorizontalAlignRight()
		self.timeLine.SetPosition(169, 19)
		self.timeLine.Show()

		self.previewLine = ui.TextLine()
		self.previewLine.SetParent(self)
		self.previewLine.AddFlag("not_pick")
		if smallFont:
			self.previewLine.SetFontName(smallFont)
		self.previewLine.SetFontColor(0.700, 0.640, 0.580)
		if arabic:
			self.previewLine.SetPosition(161, 50)
		else:
			self.previewLine.SetPosition(13, 50)
		self.previewLine.Show()

		self.deleteBtn = ui.Button()
		self.deleteBtn.SetParent(self)
		if arabic:
			self.deleteBtn.SetPosition(11, 51)
		else:
			self.deleteBtn.SetPosition(151, 51)
		self.deleteBtn.SetUpVisual(IMG_DIR + "close_btn_norm.png")
		self.deleteBtn.SetOverVisual(IMG_DIR + "close_btn_hover.png")
		self.deleteBtn.SetDownVisual(IMG_DIR + "close_btn_select.png")
		self.deleteBtn.SetToolTipText(getattr(localeinfo, "WHISPERCHAT_DELETE", "Delete conversation"))
		self.deleteBtn.SetEvent(ui.__mem_func__(self.__OnDelete))
		self.deleteBtn.Show()

	def SetRowEvents(self, clickEvent, deleteEvent, wheelEvent):
		self.clickEvent = clickEvent
		self.deleteEvent = deleteEvent
		self.wheelEvent = wheelEvent

	def SetData(self, contactName, isGM, avatarPath, timeText, previewText, selected, unread, statusPath):
		self.contactName = contactName
		self.isGM = isGM
		self.selected = selected
		if avatarPath:
			try:
				self.avatar.LoadImage(avatarPath)
				self.avatar.Show()
			except:
				self.avatar.Hide()
		else:
			self.avatar.Hide()
		if statusPath:
			try:
				self.statusDot.LoadImage(statusPath)
				self.statusDot.Show()
			except:
				self.statusDot.Hide()
		else:
			self.statusDot.Hide()
		self.nameLine.SetText(contactName)
		self.timeLine.SetText(timeText)
		self.previewLine.SetText(previewText)
		if unread:
			self.nameLine.SetFontColor(1.0, 0.85, 0.5)
			self.timeLine.SetFontColor(0.95, 0.78, 0.42)
			self.unreadIcon.Show()
		else:
			self.nameLine.SetFontColor(0.878, 0.800, 0.733)
			self.timeLine.SetFontColor(0.620, 0.550, 0.500)
			self.unreadIcon.Hide()
		self.__RefreshBg()

	def __RefreshBg(self):
		if self.isGM:
			prefix = "conv_item_gm_"
		else:
			prefix = "conv_item_"
		if self.selected:
			state = "select"
		elif self.hovered:
			state = "hover"
		else:
			state = "norm"
		try:
			self.bg.LoadImage(IMG_DIR + prefix + state + ".png")
		except:
			pass

	def __OnDelete(self):
		if self.deleteEvent and self.contactName:
			self.deleteEvent(self.contactName)

	def OnMouseOverIn(self):
		self.hovered = True
		self.__RefreshBg()

	def OnMouseOverOut(self):
		self.hovered = False
		self.__RefreshBg()

	def OnMouseLeftButtonDown(self):
		if self.clickEvent and self.contactName:
			self.clickEvent(self.contactName)

	def OnRunMouseWheel(self, nLen):
		if not self.IsInPosition():
			return False
		if self.wheelEvent:
			return self.wheelEvent(nLen)
		return False

class WhisperChatWindow(ui.ScriptWindow):

	CHAT_AREA_LEFT = 18
	CHAT_AREA_TOP = 79
	CHAT_BOX_W = 425
	CHAT_BOX_H = 272

	SCROLLBAR_X = 442
	SCROLLBAR_Y = 74
	SCROLLBAR_H = 285

	SIDEBAR_X = 459
	SIDEBAR_Y = 33
	SIDEBAR_ROW_X = 464
	SIDEBAR_ROWS_TOP = 69
	SIDEBAR_ROW_PITCH = 80
	SIDEBAR_VISIBLE_ROWS = 4
	SIDEBAR_PREVIEW_MAX_W = 133

	# same order as uicommunity.PORTRAIT_IMG: bJob is the raw MAIN_RACE_ 0-8,
	# 8 = wolfman (no icon -> generic player icon)
	RACE_ICONS = {
		0: "warrior_m.png",
		1: "assassin_w.png",
		2: "sura_m.png",
		3: "shaman_w.png",
		4: "warrior_w.png",
		5: "assassin_m.png",
		6: "sura_w.png",
		7: "shaman_m.png",
	}

	BUBBLE_MAX_W = 300
	BUBBLE_PAD_X = 10
	BUBBLE_PAD_Y = 7
	BUBBLE_GAP = 6
	ROW_MARGIN = 4
	TIME_GAP = 8
	LINE_LEADING = 2
	TRANSCRIPT_TOP_PAD = 6
	TRANSCRIPT_BOTTOM_PAD = 6
	WHEEL_STEP = 40
	BUILD_MAX = 60

	MINE_TINT = (1.0, 0.66, 0.58)
	TEXT_COLOR = (0.878, 0.800, 0.733)
	TIME_COLOR = (0.620, 0.550, 0.500)
	SYSTEM_COLOR = (0.800, 0.620, 0.520)

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.__Initialize()

	def __Initialize(self):
		self.board = None
		self.interface = None
		self.guildButtonEvent = None
		self.isLoaded = 0
		self.contactRaces = {}
		self.lastMessageTimes = {}
		self.lastOnlineTimes = {}
		self.activeConversationName = ""

		self.headerIcon = None
		self.headerStatusIcon = None
		self.lastStatusPollTime = 0
		self.headerBg = None
		self.headerAddBtn = None
		self.headerBlockBtn = None
		self.headerShopBtn = None
		self.headerTeleportBtn = None
		self.chatTargetName = None
		self.chatTargetLevel = None
		self.chatViewport = None
		self.chatScrollBar = None
		self.chatContent = None
		self.measureText = None
		self.measureTime = None
		self.bubbles = []
		self.contentHeight = 0
		self.contentY = 0
		self.shownMessageCount = 0
		self.lastDayKey = None
		self.lineHeight = 15
		self.timeHeight = 11
		self.inputBar = None
		self.chatLine = None
		self.chatSendBtn = None
		self.noChatText = None
		self.newConversationDialog = None
		self.sidebarSearchBg = None
		self.sidebarSearchLine = None
		self.sidebarSearchBtn = None
		self.sidebarCreateBtn = None
		self.sidebarRows = []
		self.sidebarConversations = []
		self.sidebarFiltered = []
		self.sidebarScrollOffset = 0
		self.sidebarSearchText = ""
		self.deleteQuestionDialog = None
		self.pendingDeleteName = ""
		self.sidebarEmptyText = None
		self.noChatImage = None
		self.headerLastSeen = None
		self.transcriptLimit = self.BUILD_MAX
		self.lastSeenRequestTimes = {}

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		if self.activeConversationName:
			SetMinimizedConversation(self.activeConversationName)
		self.ClearDictionary()
		self.__Initialize()

	def BindInterface(self, interface):
		if interface:
			self.interface = proxy(interface)
			if self.chatViewport:
				self.chatViewport.SetInterfaceRef(self.interface)

	def SetGuildButtonEvent(self, event):
		self.guildButtonEvent = event

	def Show(self):
		if self.isLoaded == 0:
			self.isLoaded = 1
			self.__LoadWindow()
		if self.activeConversationName:
			messagescache.MarkSeen(self.activeConversationName)
			if self.interface:
				self.interface.DestroyWhisperButtonByName(self.activeConversationName)
		self.__RefreshSidebar(True)
		ui.ScriptWindow.Show(self)

	def Close(self):
		if self.newConversationDialog:
			self.newConversationDialog.Close()
			self.newConversationDialog = None
		self.__CloseDeleteDialog()
		if self.sidebarSearchLine:
			self.sidebarSearchLine.KillFocus()
		if self.chatLine:
			self.chatLine.KillFocus()
		if self.activeConversationName:
			SetMinimizedConversation(self.activeConversationName)
			if self.interface:
				self.interface.MakeWhisperButton(self.activeConversationName)
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def __LoadWindow(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/whisperchatwindow.py")

		try:
			self.board = self.GetChild("board")
			self.headerBg = self.GetChild("header_bg")
			self.chatTargetName = self.GetChild("chat_target_name")
			self.inputBar = self.GetChild("input_bar")
			self.chatSendBtn = self.GetChild("send_btn")
		except:
			import exception
			exception.Abort("WhisperChatWindow.__LoadWindow.__Bind")

		self.board.SetCloseEvent(ui.__mem_func__(self.Close))

		self.chatTargetName.SetFontName(localeinfo.UI_DEF_FONT_LARGE)
		self.chatTargetName.SetFontColor(0.878, 0.800, 0.733)
		self.chatTargetName.SetOutline()

		self.chatTargetLevel = ui.TextLine()
		self.chatTargetLevel.SetParent(self)
		levelFont = getattr(localeinfo, "UI_DEF_FONT_SMALL", None)
		if levelFont:
			self.chatTargetLevel.SetFontName(levelFont)
		self.chatTargetLevel.SetFontColor(0.700, 0.620, 0.550)
		self.chatTargetLevel.SetOutline()
		self.chatTargetLevel.AddFlag("not_pick")
		if localeinfo.IsARABIC():
			# chat_target_name is window-aligned RIGHT by the RTL loader, so its
			# local x counts from the parent's right edge - mirror the level too
			self.chatTargetLevel.SetWindowHorizontalAlignRight()
		self.chatTargetLevel.Hide()

		self.headerIcon = ui.ExpandedImageBox()
		self.headerIcon.SetParent(self)
		self.headerIcon.SetPosition(25, 43)
		self.headerIcon.AddFlag("not_pick")
		self.headerIcon.Hide()

		self.headerStatusIcon = ui.ExpandedImageBox()
		self.headerStatusIcon.SetParent(self)
		self.headerStatusIcon.SetPosition(43, 59)
		self.headerStatusIcon.AddFlag("not_pick")
		self.headerStatusIcon.Hide()

		self.headerLastSeen = ui.TextLine()
		self.headerLastSeen.SetParent(self)
		lastSeenFont = getattr(localeinfo, "UI_DEF_FONT_SMALL", None)
		if lastSeenFont:
			self.headerLastSeen.SetFontName(lastSeenFont)
		self.headerLastSeen.SetFontColor(0.620, 0.550, 0.500)
		self.headerLastSeen.SetOutline()
		self.headerLastSeen.SetHorizontalAlignCenter()
		# abs midfield between the name zone and the header buttons is free on
		# both locales (en buttons right, ae buttons left + right-anchored name)
		self.headerLastSeen.SetPosition(250, 52)
		self.headerLastSeen.AddFlag("not_pick")
		self.headerLastSeen.Hide()

		self.__CreateHeaderButtons()
		self.__CreateSidebar()

		self.chatViewport = WheelWindow()
		self.chatViewport.SetParent(self)
		self.chatViewport.SetPosition(self.CHAT_AREA_LEFT, self.CHAT_AREA_TOP)
		self.chatViewport.SetSize(self.CHAT_BOX_W, self.CHAT_BOX_H)
		self.chatViewport.SetWheelCallback(ui.__mem_func__(self.__OnChatWheel))
		if self.interface:
			self.chatViewport.SetInterfaceRef(self.interface)
		self.chatViewport.Show()

		self.chatContent = ui.Window()
		self.chatContent.SetParent(self.chatViewport)
		self.chatContent.AddFlag("not_pick")
		self.chatContent.SetPosition(0, 0)
		self.chatContent.SetSize(self.CHAT_BOX_W, self.CHAT_BOX_H)
		if app.USE_CLIP_MASK:
			self.chatContent.SetClippingMaskWindow(self.chatViewport)
		self.chatContent.Show()

		self.chatScrollBar = AdvScrollBar()
		self.chatScrollBar.SetParent(self)
		self.chatScrollBar.SetPosition(self.SCROLLBAR_X, self.SCROLLBAR_Y)
		self.chatScrollBar.SetScrollBarSize(self.SCROLLBAR_H)
		self.chatScrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScrollBar))

		self.measureText = ui.TextLine()
		self.measureText.SetParent(self)
		self.measureText.Hide()

		self.measureTime = ui.TextLine()
		self.measureTime.SetParent(self)
		timeFont = getattr(localeinfo, "UI_DEF_FONT_SMALL", None)
		if timeFont:
			self.measureTime.SetFontName(timeFont)
		self.measureTime.Hide()

		self.chatLine = ui.EditLine()
		self.chatLine.SetParent(self.inputBar)
		self.chatLine.SetPosition(10, 8)
		self.chatLine.SetSize(310, 40)
		self.chatLine.SetMax(200)
		self.chatLine.SetLimitWidth(310)
		self.chatLine.SetMultiLine()
		self.chatLine.SetReturnEvent(ui.__mem_func__(self.SendWhisper))
		self.chatLine.SetEscapeEvent(ui.__mem_func__(self.Close))
		if app.USE_CLIP_MASK:
			self.chatLine.SetClippingMaskWindow(self.inputBar)
		self.chatLine.Hide()

		self.chatSendBtn.SetEvent(ui.__mem_func__(self.SendWhisper))

		if localeinfo.IsARABIC():
			self.chatLine.SetPosition(104, 10)

		self.noChatImage = ui.ExpandedImageBox()
		self.noChatImage.SetParent(self)
		self.noChatImage.LoadImage(IMG_DIR + "mail_empty.png")
		self.noChatImage.SetPosition(self.CHAT_AREA_LEFT + self.CHAT_BOX_W / 2 - 20, self.CHAT_AREA_TOP + self.CHAT_BOX_H / 2 - 45)
		self.noChatImage.AddFlag("not_pick")
		self.noChatImage.Show()

		self.noChatText = ui.TextLine()
		self.noChatText.SetParent(self)
		self.noChatText.SetText(getattr(localeinfo, "WHISPERCHAT_NO_CHAT", "Start a conversation"))
		self.noChatText.SetFontColor(0.737, 0.573, 0.553)
		self.noChatText.SetOutline()
		self.noChatText.SetHorizontalAlignCenter()
		self.noChatText.SetPosition(self.CHAT_AREA_LEFT + self.CHAT_BOX_W / 2, self.CHAT_AREA_TOP + self.CHAT_BOX_H / 2)
		self.noChatText.AddFlag("not_pick")
		self.noChatText.Show()

		self.__HideChatPanel()

	#####################################################################################
	## Conversation panel

	def __HideChatPanel(self):
		self.activeConversationName = ""
		self.__ClearTranscript()
		if self.chatLine:
			self.chatLine.KillFocus()
			self.chatLine.Hide()
		if self.chatTargetName:
			self.chatTargetName.SetText("")
			self.chatTargetName.Hide()
		if self.chatTargetLevel:
			self.chatTargetLevel.Hide()
		if self.headerIcon:
			self.headerIcon.Hide()
		if self.headerStatusIcon:
			self.headerStatusIcon.Hide()
		if self.headerLastSeen:
			self.headerLastSeen.Hide()
		if self.noChatText:
			self.noChatText.Show()
		if self.noChatImage:
			self.noChatImage.Show()

	def __ShowChatPanel(self, name):
		self.chatTargetName.SetText(name)
		self.chatTargetName.Show()
		self.__UpdateHeaderIcon(name)
		self.__UpdateHeaderLevel(name)
		self.__UpdateHeaderStatus(name)
		self.__UpdateHeaderLastSeen(name)
		self.__UpdateHeaderBlockBtn(name)
		self.chatLine.SetText("")
		self.chatLine.Show()
		self.chatLine.SetFocus()
		if self.noChatText:
			self.noChatText.Hide()
		if self.noChatImage:
			self.noChatImage.Hide()

	def __UpdateHeaderIcon(self, name):
		if not self.headerIcon:
			return
		try:
			isGM = False
			if self.interface:
				try:
					isGM = self.interface.IsGameMasterName(name)
				except:
					pass
			self.headerIcon.LoadImage(self.__GetContactAvatar(name, isGM))
			self.headerIcon.Show()
		except:
			self.headerIcon.Hide()

	def __FindCommunityFriend(self, name):
		# (name, presence, level, job, empire, channel, mapIndex, favorite, statusMessage)
		if not getattr(net, "SendCommunityRequestByName", None):
			return None
		try:
			import community
			for i in xrange(community.GetFriendCount()):
				info = community.GetFriend(i)
				if info[0] == name:
					return info
		except:
			pass
		return None

	def __GetContactLevelText(self, name):
		info = self.__FindCommunityFriend(name)
		if info:
			try:
				if int(info[2]) > 0:
					return "Lv." + str(int(info[2]))
			except:
				pass
		return messagescache.GetContactLevelText(name)

	def __UpdateHeaderStatus(self, name):
		if not self.headerStatusIcon:
			return
		info = self.__FindCommunityFriend(name)
		if info:
			try:
				import uicommunity
				self.headerStatusIcon.LoadImage(uicommunity.GetStateImage(int(info[1])))
				self.headerStatusIcon.Show()
			except:
				self.headerStatusIcon.Hide()
			return
		# non-friends: one-shot /lastonline reply (0 = online right now)
		ts = self.lastOnlineTimes.get(name)
		if ts is None:
			self.headerStatusIcon.Hide()
			return
		try:
			import community
			import uicommunity
			if ts == 0:
				state = community.COMMUNITY_PRESENCE_CONNECT
			else:
				state = community.COMMUNITY_PRESENCE_DISCONNECT
			self.headerStatusIcon.LoadImage(uicommunity.GetStateImage(state))
			self.headerStatusIcon.Show()
		except:
			self.headerStatusIcon.Hide()

	def __UpdateHeaderLastSeen(self, name):
		if not self.headerLastSeen:
			return
		info = self.__FindCommunityFriend(name)
		if info:
			try:
				import community
				if int(info[1]) != community.COMMUNITY_PRESENCE_DISCONNECT:
					self.headerLastSeen.Hide()
					return
			except:
				self.headerLastSeen.Hide()
				return
		ts = self.lastOnlineTimes.get(name)
		if not ts:
			self.headerLastSeen.Hide()
			return
		self.headerLastSeen.SetText(self.__FormatLastSeen(ts))
		self.headerLastSeen.Show()

	def __FormatLastSeen(self, ts):
		delta = int(time.time()) - int(ts)
		if delta < 0:
			delta = 0
		if delta < 60:
			whenText = getattr(localeinfo, "WHISPERCHAT_JUST_NOW", "Just now")
		elif delta < 3600:
			whenText = getattr(localeinfo, "WHISPERCHAT_MIN_AGO", "%d min ago") % (delta / 60)
		elif delta < 86400:
			whenText = getattr(localeinfo, "WHISPERCHAT_HOURS_AGO", "%d hours ago") % (delta / 3600)
		else:
			whenText = getattr(localeinfo, "WHISPERCHAT_DAYS_AGO", "%d days ago") % (delta / 86400)
		try:
			return getattr(localeinfo, "WHISPERCHAT_LAST_SEEN", "Last seen: %s") % whenText
		except:
			return whenText

	def __RequestLastOnline(self, name):
		if not name or not getattr(constinfo, "MESSENGER_LAST_ONLINE", 0):
			return
		now = time.time()
		if now - self.lastSeenRequestTimes.get(name, 0) < 60.0:
			return
		self.lastSeenRequestTimes[name] = now
		net.SendChatPacket("/lastonline " + name)

	def __IsContactBlocked(self, name):
		if not getattr(net, "SendCommunityBlockDelete", None):
			return False
		try:
			import community
			for i in xrange(community.GetBlockCount()):
				if community.GetBlock(i)[0] == name:
					return True
		except:
			pass
		return False

	def __UpdateHeaderBlockBtn(self, name):
		if not self.headerBlockBtn:
			return
		if self.__IsContactBlocked(name):
			self.headerBlockBtn.SetUpVisual(IMG_DIR + "block_select.png")
			self.headerBlockBtn.SetToolTipText(getattr(localeinfo, "WHISPERCHAT_UNBLOCK", "Unblock player"))
		else:
			self.headerBlockBtn.SetUpVisual(IMG_DIR + "block_norm.png")
			self.headerBlockBtn.SetToolTipText(getattr(localeinfo, "WHISPERCHAT_BLOCK", "Block player"))

	def OnUpdate(self):
		if not self.isLoaded or not self.IsShow():
			return
		now = time.time()
		if now - self.lastStatusPollTime < 2.0:
			return
		self.lastStatusPollTime = now
		if self.activeConversationName:
			self.__UpdateHeaderStatus(self.activeConversationName)
			self.__UpdateHeaderLastSeen(self.activeConversationName)
			self.__UpdateHeaderBlockBtn(self.activeConversationName)
			self.__UpdateHeaderTeleportBtn(self.activeConversationName)
		self.__BindSidebarRows()

	def __UpdateHeaderLevel(self, name):
		if not self.chatTargetLevel or not self.chatTargetName:
			return
		levelText = self.__GetContactLevelText(name)
		if not levelText:
			self.chatTargetLevel.Hide()
			return
		self.chatTargetLevel.SetText(levelText)
		nameX, nameY = self.chatTargetName.GetLocalPosition()
		nameW = self.chatTargetName.GetTextSize()[0]
		# same formula both locales: the level window mirrors the name's window
		# alignment, so local x always grows AWAY from the name's anchored edge
		self.chatTargetLevel.SetPosition(int(nameX + nameW + 8), int(nameY + 2))
		self.chatTargetLevel.Show()

	def __CreateHeaderButtons(self):
		if not self.headerBg:
			return
		if localeinfo.IsARABIC():
			xShop, xBlock, xAdd, xTele = 45, 79, 113, 147
		else:
			xShop, xBlock, xAdd, xTele = 402, 368, 334, 300
		self.headerAddBtn = self.__MakeHeaderButton(xAdd, "add_norm.png", "add_hover.png", "add_selct.png",
			getattr(localeinfo, "WHISPERCHAT_ADD_FRIEND", "Add friend"), self.__OnHeaderAddFriend)
		self.headerBlockBtn = self.__MakeHeaderButton(xBlock, "block_norm.png", "block_hover.png", "block_select.png",
			getattr(localeinfo, "WHISPERCHAT_BLOCK", "Block player"), self.__OnHeaderBlock)
		self.headerShopBtn = self.__MakeHeaderButton(xShop, "shop_norm.png", "shop_hover.png", "shop_select.png",
			getattr(localeinfo, "WHISPERCHAT_OPEN_SHOP", "Open player's shop"), self.__OnHeaderShop)
		if app.USE_PREMIUM_FEATURES:
			self.headerTeleportBtn = self.__MakeHeaderButton(xTele, "teleports_normal.png", "teleports_hover.png", "teleports_down.png",
				getattr(localeinfo, "PREMIUM_TELEPORT", "Teleport"), self.__OnHeaderTeleport)
			self.__UpdateHeaderTeleportBtn(self.activeConversationName)

	def __MakeHeaderButton(self, x, up, over, down, tooltip, event):
		btn = ui.Button()
		btn.SetParent(self.headerBg)
		btn.SetPosition(x, 4)
		btn.SetUpVisual(IMG_DIR + up)
		btn.SetOverVisual(IMG_DIR + over)
		btn.SetDownVisual(IMG_DIR + down)
		btn.SetToolTipText(tooltip)
		btn.SetEvent(ui.__mem_func__(event))
		btn.Show()
		return btn

	def __OnHeaderAddFriend(self):
		name = self.activeConversationName
		if not name:
			return
		sendCommunity = getattr(net, "SendCommunityRequestByName", None)
		if sendCommunity:
			sendCommunity(name)
			return
		net.SendMessengerAddByNamePacket(name)

	def __OnHeaderBlock(self):
		name = self.activeConversationName
		if not name:
			return
		if self.__IsContactBlocked(name):
			net.SendCommunityBlockDelete(name)
			return
		sendCommunity = getattr(net, "SendCommunityBlockAddByName", None)
		if sendCommunity:
			sendCommunity(name)
			return
		sendBlock = getattr(net, "SendMessengerBlockAddByNamePacket", None)
		if sendBlock:
			sendBlock(name)

	def __OnHeaderShop(self):
		name = self.activeConversationName
		if not name or not app.USE_OFFLINESHOP:
			return
		import offlineshop
		board = offlineshop.GetOfflineshopBoard()
		if not board:
			return
		wndShop = getattr(board, "wndOffShop", None)
		wndSearch = getattr(wndShop, "wndSearchShop", None)
		if not wndSearch:
			return
		wndSearch.SearchByOwnerName(name)
		if wndSearch.IsShow():
			wndSearch.SetTop()

	def __OnHeaderTeleport(self):
		name = self.activeConversationName
		if not name:
			return
		net.SendChatPacket("/pmwarp " + name)

	def __UpdateHeaderTeleportBtn(self, name):
		if not self.headerTeleportBtn:
			return
		if app.USE_PREMIUM_FEATURES and constinfo.player_premium_type != player.PREMIUM_TYPE_NONE:
			self.headerTeleportBtn.Show()
		else:
			self.headerTeleportBtn.Hide()

	def OpenConversation(self, name):
		if not name:
			return
		if self.isLoaded == 0:
			self.isLoaded = 1
			self.__LoadWindow()
		self.activeConversationName = name
		self.transcriptLimit = self.BUILD_MAX
		self.__ClearTranscript()

		messages = messagescache.LoadMessages(name)
		self.shownMessageCount = len(messages)
		for direction, msgType, epoch, msgText in messages[-self.transcriptLimit:]:
			self.__AppendBubble(direction, msgType, epoch, msgText)
		self.__RelayoutTranscript(True)
		self.__ShowChatPanel(name)
		messagescache.MarkSeen(name)
		if self.interface:
			self.interface.DestroyWhisperButtonByName(name)
		self.__RequestLastOnline(name)
		self.__RefreshSidebar(False)

	def CloseConversation(self):
		self.__HideChatPanel()
		self.__BindSidebarRows()

	def GetActiveConversation(self):
		return self.activeConversationName

	def NotifyWhisper(self, name, fromLiveChat=False):
		self.lastMessageTimes[name] = time.time()
		# error/system whisper replies route here too - only a real incoming
		# chat message proves the contact is online right now
		if fromLiveChat:
			self.lastOnlineTimes[name] = 0

		if self.isLoaded and self.IsShow():
			self.__RefreshSidebar(True)

		if self.activeConversationName != name or self.isLoaded == 0:
			return
		self.__UpdateHeaderIcon(name)
		self.__UpdateHeaderLevel(name)
		self.__UpdateHeaderStatus(name)
		self.__UpdateHeaderLastSeen(name)
		if self.IsShow():
			messagescache.MarkSeen(name)
		messages = messagescache.LoadMessages(name)
		newMessages = messages[self.shownMessageCount:]
		if not newMessages:
			self.shownMessageCount = min(self.shownMessageCount, len(messages))
			return
		stick = self.__IsAtBottom()
		for direction, msgType, epoch, msgText in newMessages:
			self.__AppendBubble(direction, msgType, epoch, msgText)
		self.shownMessageCount = len(messages)
		self.__RelayoutTranscript(stick)

	def UpdateContactRace(self, name, race):
		self.contactRaces[name] = race

	def OnLastOnline(self, name, timestamp):
		# server sends the offline AGE in seconds (subtracted DB-side, so a
		# skewed server clock cancels); anchor it to the client clock here
		try:
			age = int(timestamp)
		except ValueError:
			return
		if age <= 0:
			self.lastOnlineTimes[name] = 0
		else:
			self.lastOnlineTimes[name] = int(time.time()) - age
		if name == self.activeConversationName and self.isLoaded:
			self.__UpdateHeaderStatus(name)
			self.__UpdateHeaderLastSeen(name)

	#####################################################################################
	## Bubble transcript

	def __MeasureLine(self, text):
		self.measureText.SetText(text)
		w, h = self.measureText.GetTextSize()
		if h > 0:
			self.lineHeight = h
		return w

	def __MeasureTimeText(self, text):
		self.measureTime.SetText(text)
		w, h = self.measureTime.GetTextSize()
		if h > 0:
			self.timeHeight = h
		return w

	def __SplitTokens(self, text):
		# spaces inside a |H..|h..|h hyperlink block must not split it across lines
		tokens = []
		token = ""
		phase = 0
		i = 0
		length = len(text)
		while i < length:
			c = text[i]
			if c == "|" and i + 1 < length:
				nxt = text[i + 1]
				if phase == 0 and nxt == "H":
					phase = 1
				elif nxt == "h":
					if phase == 1:
						phase = 2
					else:
						phase = 0
				token += c + nxt
				i += 2
				continue
			if c == " " and phase == 0:
				if token:
					tokens.append(token)
				token = ""
				i += 1
				continue
			token += c
			i += 1
		if token:
			tokens.append(token)
		return tokens

	def __WrapText(self, text, limitWidth):
		if self.__MeasureLine(text) <= limitWidth:
			return [text]
		lines = []
		current = ""
		for token in self.__SplitTokens(text):
			if current:
				candidate = current + " " + token
			else:
				candidate = token
			if self.__MeasureLine(candidate) <= limitWidth:
				current = candidate
				continue
			if current:
				lines.append(current)
				current = ""
			if "|" in token or self.__MeasureLine(token) <= limitWidth:
				current = token
				continue
			piece = ""
			for ch in token:
				grown = piece + ch
				if piece and self.__MeasureLine(grown) > limitWidth:
					lines.append(piece)
					piece = ch
				else:
					piece = grown
			current = piece
		if current:
			lines.append(current)
		if not lines:
			return [text]
		return lines

	def __FormatTime(self, epoch):
		if epoch <= 0:
			return ""
		try:
			return time.strftime("%H:%M", time.localtime(epoch))
		except:
			return ""

	def __AppendBubble(self, direction, msgType, epoch, msgText):
		if not msgText:
			return
		self.__AppendDaySeparatorIfNeeded(epoch)
		if direction == messagescache.DIR_SYSTEM:
			self.__AppendSystemRow(MakePlainText(msgText))
			return
		# raw markup stays: the text instance parses |cff color + |H..|h links
		# itself (colored, hover-tracked); clicks land on the viewport
		arabic = localeinfo.IsARABIC()
		maxTextW = self.BUBBLE_MAX_W - self.BUBBLE_PAD_X * 2
		lines = self.__WrapText(msgText, maxTextW)
		widths = []
		for line in lines:
			widths.append(self.__MeasureLine(line))
		textW = max(widths)
		lineStep = self.lineHeight + self.LINE_LEADING

		timeText = self.__FormatTime(epoch)
		timeW = 0
		if timeText:
			timeW = self.__MeasureTimeText(timeText)

		inlineTime = 0
		bubbleW = textW + self.BUBBLE_PAD_X * 2
		rawH = self.BUBBLE_PAD_Y * 2 + lineStep * len(lines) - self.LINE_LEADING
		if timeText:
			if widths[-1] + self.TIME_GAP + timeW <= maxTextW:
				inlineTime = 1
				bubbleW = max(bubbleW, widths[-1] + self.TIME_GAP + timeW + self.BUBBLE_PAD_X * 2)
			else:
				rawH += self.timeHeight + self.LINE_LEADING
				bubbleW = max(bubbleW, timeW + self.BUBBLE_PAD_X * 2)
		bubbleW = max(24, min(int(bubbleW), self.BUBBLE_MAX_W))
		bubbleH = max(24, int(rawH))
		padTop = self.BUBBLE_PAD_Y

		board = BubbleBoard()
		board.SetParent(self.chatContent)
		board.AddFlag("not_pick")
		board.SetSize(bubbleW, bubbleH)
		mine = (direction == messagescache.DIR_MINE)
		if mine:
			board.SetTint(self.MINE_TINT[0], self.MINE_TINT[1], self.MINE_TINT[2])
			x = self.CHAT_BOX_W - self.ROW_MARGIN - bubbleW
		else:
			x = self.ROW_MARGIN
		if self.contentHeight == 0:
			y = self.TRANSCRIPT_TOP_PAD
		else:
			y = self.contentHeight + self.BUBBLE_GAP
		board.SetPosition(int(x), int(y))
		board.Show()

		texts = []
		textY = padTop
		for line in lines:
			textLine = ui.TextLine()
			textLine.SetParent(board)
			textLine.AddFlag("not_pick")
			textLine.SetFontColor(self.TEXT_COLOR[0], self.TEXT_COLOR[1], self.TEXT_COLOR[2])
			textLine.SetText(line)
			if arabic:
				textLine.SetPosition(bubbleW - self.BUBBLE_PAD_X, int(textY))
			else:
				textLine.SetPosition(self.BUBBLE_PAD_X, int(textY))
			textLine.Show()
			texts.append(textLine)
			textY += lineStep

		timeLine = None
		if timeText:
			timeLine = ui.TextLine()
			timeLine.SetParent(board)
			timeLine.AddFlag("not_pick")
			timeFont = getattr(localeinfo, "UI_DEF_FONT_SMALL", None)
			if timeFont:
				timeLine.SetFontName(timeFont)
			timeLine.SetFontColor(self.TIME_COLOR[0], self.TIME_COLOR[1], self.TIME_COLOR[2])
			timeLine.SetText(timeText)
			if inlineTime:
				timeY = textY - lineStep + max(0, self.lineHeight - self.timeHeight)
			else:
				timeY = textY
			# ae + ALIGN_RIGHT falls into the engine's LTR default branch: anchor left, draw
			# rightward - so the same align flag mirrors the time stamp on both locales
			timeLine.SetHorizontalAlignRight()
			if arabic:
				timeLine.SetPosition(self.BUBBLE_PAD_X, int(timeY))
			else:
				timeLine.SetPosition(bubbleW - self.BUBBLE_PAD_X, int(timeY))
			timeLine.Show()

		self.bubbles.append({"widgets": [board], "texts": texts, "time": timeLine})
		self.contentHeight = y + bubbleH

	def __AppendDaySeparatorIfNeeded(self, epoch):
		if epoch <= 0:
			return
		try:
			lt = time.localtime(epoch)
			dayKey = (lt.tm_year, lt.tm_yday)
			nowLt = time.localtime()
			yLt = time.localtime(time.time() - 86400)
			if dayKey == (nowLt.tm_year, nowLt.tm_yday):
				dateText = getattr(localeinfo, "WHISPERCHAT_TODAY", "Today")
			elif dayKey == (yLt.tm_year, yLt.tm_yday):
				dateText = getattr(localeinfo, "WHISPERCHAT_YESTERDAY", "Yesterday")
			else:
				dateText = time.strftime("%d/%m", lt)
		except:
			return
		if dayKey == self.lastDayKey:
			return
		self.lastDayKey = dayKey

		if self.contentHeight == 0:
			y = self.TRANSCRIPT_TOP_PAD
		else:
			y = self.contentHeight + self.BUBBLE_GAP
		dateW = self.__MeasureTimeText(dateText)
		centerX = self.CHAT_BOX_W / 2
		gap = 10
		margin = 20
		widgets = []

		textLine = ui.TextLine()
		textLine.SetParent(self.chatContent)
		textLine.AddFlag("not_pick")
		dateFont = getattr(localeinfo, "UI_DEF_FONT_SMALL", None)
		if dateFont:
			textLine.SetFontName(dateFont)
		textLine.SetFontColor(self.TIME_COLOR[0], self.TIME_COLOR[1], self.TIME_COLOR[2])
		textLine.SetHorizontalAlignCenter()
		textLine.SetText(dateText)
		textLine.SetPosition(int(centerX), int(y))
		textLine.Show()
		widgets.append(textLine)

		lineTargetW = centerX - dateW / 2 - gap - margin
		if lineTargetW > 4:
			lineY = y + self.timeHeight / 2
			for xPos in (margin, centerX + dateW / 2 + gap):
				img = ui.ExpandedImageBox()
				img.SetParent(self.chatContent)
				img.AddFlag("not_pick")
				img.LoadImage(IMG_DIR + "line_conv.png")
				img.SetScale(float(lineTargetW) / max(1, img.GetWidth()), 1.0)
				img.SetPosition(int(xPos), int(lineY))
				img.Show()
				widgets.append(img)

		self.bubbles.append({"widgets": widgets, "texts": [], "time": None})
		self.contentHeight = y + max(self.timeHeight, 12)

	def __AppendSystemRow(self, msgText):
		lines = self.__WrapText(msgText, self.CHAT_BOX_W - 60)
		lineStep = self.lineHeight + self.LINE_LEADING
		if self.contentHeight == 0:
			y = self.TRANSCRIPT_TOP_PAD
		else:
			y = self.contentHeight + self.BUBBLE_GAP
		widgets = []
		for line in lines:
			textLine = ui.TextLine()
			textLine.SetParent(self.chatContent)
			textLine.AddFlag("not_pick")
			textLine.SetFontColor(self.SYSTEM_COLOR[0], self.SYSTEM_COLOR[1], self.SYSTEM_COLOR[2])
			textLine.SetHorizontalAlignCenter()
			textLine.SetText(line)
			textLine.SetPosition(self.CHAT_BOX_W / 2, int(y))
			textLine.Show()
			widgets.append(textLine)
			y += lineStep
		self.bubbles.append({"widgets": widgets, "texts": widgets, "time": None})
		self.contentHeight = y - self.LINE_LEADING

	def __ClearTranscript(self):
		for bubble in self.bubbles:
			for widget in bubble["widgets"]:
				widget.Hide()
		self.bubbles = []
		self.contentHeight = 0
		self.contentY = 0
		self.shownMessageCount = 0
		self.lastDayKey = None
		if self.chatContent:
			self.chatContent.SetSize(self.CHAT_BOX_W, self.CHAT_BOX_H)
			self.chatContent.SetPosition(0, 0)
		self.__SyncScrollBar()

	def __GetContentTotalHeight(self):
		if self.contentHeight == 0:
			return 0
		return self.contentHeight + self.TRANSCRIPT_BOTTOM_PAD

	def __RelayoutTranscript(self, stickBottom):
		if not self.chatContent:
			return
		viewH = self.CHAT_BOX_H
		contentH = self.__GetContentTotalHeight()
		self.chatContent.SetSize(self.CHAT_BOX_W, max(viewH, contentH))
		minY = min(0, viewH - contentH)
		if stickBottom:
			self.contentY = minY
		else:
			self.contentY = max(minY, min(0, self.contentY))
		self.chatContent.SetPosition(0, int(self.contentY))
		self.__SyncScrollBar()

	def __SyncScrollBar(self):
		if not self.chatScrollBar:
			return
		viewH = self.CHAT_BOX_H
		contentH = self.__GetContentTotalHeight()
		minY = min(0, viewH - contentH)
		if minY >= 0:
			self.chatScrollBar.Hide()
			return
		self.chatScrollBar.SetMiddleBarSize(max(0.05, float(viewH) / float(contentH)))
		self.chatScrollBar.SetScrollStep(float(self.WHEEL_STEP) / float(-minY))
		self.chatScrollBar.SetPos(float(self.contentY) / float(minY), False)
		self.chatScrollBar.Show()

	def __OnScrollBar(self):
		if not self.activeConversationName or not self.chatContent:
			return
		minY = min(0, self.CHAT_BOX_H - self.__GetContentTotalHeight())
		if minY >= 0:
			return
		self.contentY = int(minY * self.chatScrollBar.GetPos())
		self.chatContent.SetPosition(0, self.contentY)

	def __IsAtBottom(self):
		minY = min(0, self.CHAT_BOX_H - self.__GetContentTotalHeight())
		return self.contentY <= minY + 1

	#####################################################################################
	## Chat scroll / send

	def OnMouseWheel(self, length):
		if self.activeConversationName:
			return self.__OnChatWheel(length)
		return False

	def __OnChatWheel(self, length):
		if not self.activeConversationName:
			return False
		if length > 0 and self.contentY >= 0 and self.shownMessageCount > self.transcriptLimit:
			self.__ExtendTranscript()
			return True
		minY = min(0, self.CHAT_BOX_H - self.__GetContentTotalHeight())
		if minY >= 0:
			return True
		if length > 0:
			self.contentY = min(0, self.contentY + self.WHEEL_STEP)
		else:
			self.contentY = max(minY, self.contentY - self.WHEEL_STEP)
		self.chatContent.SetPosition(0, int(self.contentY))
		self.__SyncScrollBar()
		return True

	def __ExtendTranscript(self):
		# wheel-up at the very top: prepend the next page of cached history,
		# keeping the previously-topmost message in view
		name = self.activeConversationName
		if not name or not self.chatContent:
			return
		messages = messagescache.LoadMessages(name)
		if len(messages) <= self.transcriptLimit:
			self.shownMessageCount = len(messages)
			return
		oldContentH = self.__GetContentTotalHeight()
		self.transcriptLimit = min(len(messages), self.transcriptLimit + self.BUILD_MAX)
		self.__ClearTranscript()
		for direction, msgType, epoch, msgText in messages[-self.transcriptLimit:]:
			self.__AppendBubble(direction, msgType, epoch, msgText)
		self.shownMessageCount = len(messages)
		newContentH = self.__GetContentTotalHeight()
		viewH = self.CHAT_BOX_H
		self.chatContent.SetSize(self.CHAT_BOX_W, max(viewH, newContentH))
		minY = min(0, viewH - newContentH)
		self.contentY = max(minY, min(0, -(newContentH - oldContentH)))
		self.chatContent.SetPosition(0, int(self.contentY))
		self.__SyncScrollBar()

	def SendWhisper(self):
		if not self.activeConversationName:
			return

		text = self.chatLine.GetText()
		if len(text) == 0:
			return

		if net.IsInsultIn(text):
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CHAT_INSULT_STRING)
			return

		if osfinfo.SHOW_EMOJI_IN_WHISPER_LINE == True:
			text = osfinfo.EmojiFilter(text)

		name = self.activeConversationName
		conquerorLevel = player.GetStatus(player.POINT_CONQUEROR_LEVEL)
		if conquerorLevel > 0:
			net.SendWhisperPacket(name, "cLv." + str(conquerorLevel) + ": " + text)
		else:
			net.SendWhisperPacket(name, "Lv." + str(player.GetStatus(player.LEVEL)) + ": " + text)
		self.chatLine.SetText("")

		messagescache.SaveMessage(name, messagescache.DIR_MINE, chat.WHISPER_TYPE_CHAT, text)
		self.__AppendBubble(messagescache.DIR_MINE, chat.WHISPER_TYPE_CHAT, int(time.time()), text)
		self.shownMessageCount = len(messagescache.LoadMessages(name))
		self.__RelayoutTranscript(True)
		self.lastMessageTimes[name] = time.time()
		self.__RefreshSidebar(True)

	#####################################################################################
	## Contact sidebar

	def __CreateSidebar(self):
		arabic = localeinfo.IsARABIC()

		searchBg = ui.ExpandedImageBox()
		searchBg.SetParent(self)
		searchBg.SetPosition(self.SIDEBAR_X + 5, self.SIDEBAR_Y + 3)
		searchBg.LoadImage(IMG_DIR + "input_search.png")
		searchBg.Show()
		self.sidebarSearchBg = searchBg

		searchBtn = ui.Button()
		searchBtn.SetParent(searchBg)
		if arabic:
			searchBtn.SetPosition(147, 4)
		else:
			searchBtn.SetPosition(146, 4)
		searchBtn.SetUpVisual(IMG_DIR + "btn_search_norm.png")
		searchBtn.SetOverVisual(IMG_DIR + "btn_search_hover.png")
		searchBtn.SetDownVisual(IMG_DIR + "btn_search_select.png")
		searchBtn.SetEvent(ui.__mem_func__(self.__OnSearchButton))
		searchBtn.Show()
		self.sidebarSearchBtn = searchBtn

		searchLine = ui.EditLine()
		searchLine.SetParent(searchBg)
		if arabic:
			searchLine.SetPosition(10, 7)
		else:
			searchLine.SetPosition(8, 7)
		searchLine.SetSize(132, 16)
		searchLine.SetMax(24)
		searchLine.SetLimitWidth(130)
		searchLine.SetUpdateEvent(ui.__mem_func__(self.__OnSearchUpdate))
		searchLine.SetReturnEvent(ui.__mem_func__(self.__OnSearchReturn))
		searchLine.SetEscapeEvent(ui.__mem_func__(self.Close))
		placeText = getattr(localeinfo, "WHISPERCHAT_SEARCH", "Search...")
		if arabic:
			# placeholder textline inherits the ae right-anchor: park it at the box's right edge
			searchLine.SetPlaceHolder(placeText, (130, 0))
		else:
			searchLine.SetPlaceHolder(placeText)
		searchLine.SetPlaceHolderColor(0xFF9E8C7A)
		searchLine.Show()
		self.sidebarSearchLine = searchLine

		self.sidebarRows = []
		for i in xrange(self.SIDEBAR_VISIBLE_ROWS):
			row = ConvRow()
			row.SetParent(self)
			row.SetPosition(self.SIDEBAR_ROW_X, self.SIDEBAR_ROWS_TOP + i * self.SIDEBAR_ROW_PITCH)
			row.SetRowEvents(ui.__mem_func__(self.__OnRowClick),
				ui.__mem_func__(self.__OnRowDelete),
				ui.__mem_func__(self.__OnSidebarWheel))
			row.Hide()
			self.sidebarRows.append(row)

		emptyText = ui.TextLine()
		emptyText.SetParent(self)
		emptyFont = getattr(localeinfo, "UI_DEF_FONT_SMALL", None)
		if emptyFont:
			emptyText.SetFontName(emptyFont)
		emptyText.SetFontColor(0.700, 0.640, 0.580)
		emptyText.SetOutline()
		emptyText.SetHorizontalAlignCenter()
		emptyText.SetPosition(self.SIDEBAR_ROW_X + 87, self.SIDEBAR_ROWS_TOP + 120)
		emptyText.AddFlag("not_pick")
		emptyText.Hide()
		self.sidebarEmptyText = emptyText

		createBtn = ui.Button()
		createBtn.SetParent(self)
		createBtn.SetPosition(self.SIDEBAR_X + 7, self.SIDEBAR_Y + 356)
		createBtn.SetUpVisual(IMG_DIR + "btn_create_norm.png")
		createBtn.SetOverVisual(IMG_DIR + "btn_create_hover.png")
		createBtn.SetDownVisual(IMG_DIR + "btn_create_select.png")
		createBtn.SetText(getattr(localeinfo, "WHISPERCHAT_CREATE_MESSAGE", "Create Message"))
		createBtn.SetEvent(ui.__mem_func__(self.OpenNewConversationDialog))
		createBtn.Show()
		self.sidebarCreateBtn = createBtn

	def __RefreshSidebar(self, rescan):
		if not self.sidebarRows:
			return
		if rescan:
			self.sidebarConversations = messagescache.ListConversations()
		self.__ApplySidebarFilter()
		self.__BindSidebarRows()

	def __ApplySidebarFilter(self):
		needle = self.sidebarSearchText.lower()
		if needle:
			self.sidebarFiltered = [conv for conv in self.sidebarConversations
				if needle in conv[0].lower() or needle in MakePlainText(conv[4]).lower()]
		else:
			self.sidebarFiltered = list(self.sidebarConversations)
		maxOffset = max(0, len(self.sidebarFiltered) - self.SIDEBAR_VISIBLE_ROWS)
		self.sidebarScrollOffset = max(0, min(self.sidebarScrollOffset, maxOffset))

	def __BindSidebarRows(self):
		for i in xrange(len(self.sidebarRows)):
			row = self.sidebarRows[i]
			idx = self.sidebarScrollOffset + i
			if idx >= len(self.sidebarFiltered):
				row.Hide()
				continue
			name, direction, msgType, epoch, text = self.sidebarFiltered[idx]
			isGM = False
			if self.interface:
				try:
					isGM = self.interface.IsGameMasterName(name)
				except:
					pass
			preview = self.__TruncateSidebarText(MakePlainText(text), self.SIDEBAR_PREVIEW_MAX_W)
			unread = (direction == messagescache.DIR_THEIRS
				and name != self.activeConversationName
				and epoch > messagescache.GetSeenTime(name))
			row.SetData(name, isGM, self.__GetContactAvatar(name, isGM),
				self.__FormatSidebarTime(epoch), preview,
				name == self.activeConversationName,
				unread, self.__GetRowStatusImage(name))
			row.Show()
		if self.sidebarEmptyText:
			if self.sidebarFiltered:
				self.sidebarEmptyText.Hide()
			else:
				if self.sidebarSearchText:
					self.sidebarEmptyText.SetText(getattr(localeinfo, "WHISPERCHAT_NO_RESULTS", "No results found"))
				else:
					self.sidebarEmptyText.SetText(getattr(localeinfo, "WHISPERCHAT_NO_CONVERSATIONS", "No conversations yet"))
				self.sidebarEmptyText.Show()

	def __GetRowStatusImage(self, name):
		info = self.__FindCommunityFriend(name)
		if not info:
			return None
		try:
			import uicommunity
			return uicommunity.GetStateImage(int(info[1]))
		except:
			return None

	def __OnSearchReturn(self):
		if not self.sidebarSearchLine:
			return
		text = self.sidebarSearchLine.GetText().strip()
		if self.sidebarFiltered:
			self.OpenConversation(self.sidebarFiltered[0][0])
		elif text:
			self.OpenConversation(text)
		self.sidebarSearchLine.KillFocus()

	def __GetContactAvatar(self, name, isGM):
		if isGM:
			return IMG_DIR + "gm_icon_mini.png"
		info = self.__FindCommunityFriend(name)
		if info:
			try:
				icon = self.RACE_ICONS.get(int(info[3]))
				if icon:
					return IMG_DIR + icon
			except:
				pass
		return IMG_DIR + "player_icon_mini.png"

	def __FormatSidebarTime(self, epoch):
		if epoch <= 0:
			return ""
		try:
			lt = time.localtime(epoch)
			now = time.localtime()
			if lt.tm_year == now.tm_year and lt.tm_yday == now.tm_yday:
				return time.strftime("%H:%M", lt)
			return time.strftime("%d/%m", lt)
		except:
			return ""

	def __TruncateSidebarText(self, text, maxW):
		if not text:
			return ""
		text = text[:60]
		if self.__MeasureTimeText(text) <= maxW:
			return text
		while len(text) > 1 and self.__MeasureTimeText(text + "..") > maxW:
			text = text[:-1]
		return text + ".."

	def __OnSidebarWheel(self, nLen):
		maxOffset = max(0, len(self.sidebarFiltered) - self.SIDEBAR_VISIBLE_ROWS)
		if maxOffset == 0:
			return True
		if nLen > 0:
			newOffset = max(0, self.sidebarScrollOffset - 1)
		else:
			newOffset = min(maxOffset, self.sidebarScrollOffset + 1)
		if newOffset == self.sidebarScrollOffset:
			return True
		self.sidebarScrollOffset = newOffset
		self.__BindSidebarRows()
		return True

	def __OnRowClick(self, name):
		if name == self.activeConversationName:
			return
		self.OpenConversation(name)

	def __OnRowDelete(self, name):
		self.pendingDeleteName = name
		if self.deleteQuestionDialog:
			self.deleteQuestionDialog.Close()
		dialog = uicommon.QuestionDialog()
		confirmFormat = getattr(localeinfo, "WHISPERCHAT_DELETE_CONFIRM", "Delete conversation with %s?")
		try:
			confirmText = confirmFormat % name
		except:
			confirmText = confirmFormat
		dialog.SetText(confirmText)
		dialog.SetAcceptEvent(ui.__mem_func__(self.__OnAcceptDelete))
		dialog.SetCancelEvent(ui.__mem_func__(self.__OnCancelDelete))
		dialog.Open()
		self.deleteQuestionDialog = dialog

	def __OnAcceptDelete(self):
		name = self.pendingDeleteName
		self.__CloseDeleteDialog()
		if not name:
			return True
		messagescache.DeleteConversation(name)
		chat.ClearWhisper(name)
		ClearMinimizedConversation(name)
		if self.interface:
			self.interface.DestroyWhisperButtonByName(name)
		if name == self.activeConversationName:
			self.CloseConversation()
		self.__RefreshSidebar(True)
		return True

	def __OnCancelDelete(self):
		self.__CloseDeleteDialog()
		return True

	def __CloseDeleteDialog(self):
		if self.deleteQuestionDialog:
			self.deleteQuestionDialog.Close()
		self.deleteQuestionDialog = None
		self.pendingDeleteName = ""

	def __OnSearchUpdate(self):
		if not self.sidebarSearchLine:
			return
		text = self.sidebarSearchLine.GetText()
		if text == self.sidebarSearchText:
			return
		self.sidebarSearchText = text
		self.sidebarScrollOffset = 0
		self.__ApplySidebarFilter()
		self.__BindSidebarRows()

	def __OnSearchButton(self):
		if self.sidebarSearchLine:
			self.sidebarSearchLine.SetFocus()

	def __OnSearchEscape(self):
		if self.sidebarSearchLine:
			self.sidebarSearchLine.KillFocus()
		return True

	#####################################################################################
	## New conversation dialog

	def OpenNewConversationDialog(self):
		dialog = uicommon.InputDialog()
		dialog.SetTitle(getattr(localeinfo, "WHISPERCHAT_NEW_CONV", "Whisper"))
		dialog.SetAcceptEvent(ui.__mem_func__(self.OnAcceptNewConversation))
		dialog.SetCancelEvent(ui.__mem_func__(self.OnCancelNewConversation))
		dialog.Open()
		dialog.SetTop()
		self.newConversationDialog = dialog

	def OnAcceptNewConversation(self):
		name = self.newConversationDialog.GetText()
		self.newConversationDialog.Close()
		self.newConversationDialog = None
		if name:
			self.OpenConversation(name)
		elif self.chatLine and self.chatLine.IsShow():
			self.chatLine.SetFocus()
		return True

	def OnCancelNewConversation(self):
		if self.newConversationDialog:
			self.newConversationDialog.Close()
		self.newConversationDialog = None
		if self.chatLine and self.chatLine.IsShow():
			self.chatLine.SetFocus()
		return True
