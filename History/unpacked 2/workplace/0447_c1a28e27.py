# coding: latin_1

import ui
import net
import localeinfo


MESSENGER_PATH = "d:/ymir work/ui/game/messenger/"
ROW_IMG = MESSENGER_PATH + "friend_box.png"
ROW_IMG_HOVER = MESSENGER_PATH + "friend_box_hover.png"
ROW_IMG_DOWN = MESSENGER_PATH + "friend_box_down.png"
LOCK_IMG = "d:/ymir work/ui/new_guild/shop/32x32_background_lock.png"

# Native size of friend_box.png - the plate is never scaled.
ROW_WIDTH = 255
ROW_HEIGHT = 35

ROW_SIDE_MARGIN = 12
ROW_REMAIN_WIDTH = 84
ROW_COLUMN_GAP = 6
ROW_TEXT_Y = 10

LOCK_SIZE = 32
LOCK_MARGIN = 8

LABEL_HEIGHT = 16
CAPTION_MARGIN = 10
SCROLL_GAP = 11

COLOR_CAPTION = 0xFFFFCE9C
COLOR_LOCKED = 0xFF808080
COLOR_REMAIN = 0xFFAAAAAA

SECONDS_PER_DAY = 86400
SECONDS_PER_HOUR = 3600

ALPHA_OPAQUE = 0xFF000000


# getattr(localeinfo, key, default) never falls back -- the wrapper answers
# "Locale not found: KEY" instead of raising, and that placeholder renders.
def LocaleText(key, default):
	value = getattr(localeinfo, key, default)
	if not value or value.startswith("Locale not found"):
		return default

	return value


def FormatRemain(remainSec):
	if remainSec <= 0:
		return LocaleText("TITLE_WINDOW_PERMANENT", "Permanent")

	days = remainSec // SECONDS_PER_DAY
	if days > 0:
		return LocaleText("TITLE_WINDOW_DAYS_LEFT", "%d days left") % days

	hours = remainSec // SECONDS_PER_HOUR
	if hours < 1:
		hours = 1

	return LocaleText("TITLE_WINDOW_HOURS_LEFT", "%d hours left") % hours


class TitleRow(ui.Window):

	def __init__(self, width):
		ui.Window.__init__(self)

		self.titleId = 0
		self.owned = False
		self.active = False
		self.hovered = False
		self.filled = False
		self.currentImage = ""
		self.clickEvent = None
		self.wheelEvent = None

		width = int(width)
		self.SetSize(width, ROW_HEIGHT)

		self.background = ui.ImageBox()
		self.background.SetParent(self)
		self.background.AddFlag("not_pick")
		self.background.SetPosition(0, 0)
		self.background.LoadImage(ROW_IMG)
		self.background.Hide()
		self.currentImage = ROW_IMG

		nameWidth = width - ROW_SIDE_MARGIN * 2 - ROW_REMAIN_WIDTH - ROW_COLUMN_GAP
		if nameWidth < 40:
			nameWidth = 40

		# CTextLine::OnChangePosition anchors at m_rect.right under CP_ARABIC and
		# m_rect.left otherwise, so sizing each label is what right-aligns ae text.
		# Only the column order needs an explicit swap.
		if localeinfo.IsARABIC():
			remainX = ROW_SIDE_MARGIN
			nameX = width - nameWidth - ROW_SIDE_MARGIN
			lockX = LOCK_MARGIN
		else:
			nameX = ROW_SIDE_MARGIN
			remainX = width - ROW_REMAIN_WIDTH - ROW_SIDE_MARGIN
			lockX = width - LOCK_SIZE - LOCK_MARGIN

		self.nameLine = ui.TextLine()
		self.nameLine.SetParent(self)
		self.nameLine.AddFlag("not_pick")
		self.nameLine.SetPosition(nameX, ROW_TEXT_Y)
		self.nameLine.SetSize(nameWidth, LABEL_HEIGHT)
		# SetSize only sizes the rect; CGraphicTextInstance keeps drawing past
		# it until a limit width is set, so a long title would run over the
		# remaining-time column.
		self.nameLine.SetLimitWidth(nameWidth)
		self.nameLine.Hide()

		self.remainLine = ui.TextLine()
		self.remainLine.SetParent(self)
		self.remainLine.AddFlag("not_pick")
		self.remainLine.SetPosition(remainX, ROW_TEXT_Y)
		self.remainLine.SetSize(ROW_REMAIN_WIDTH, LABEL_HEIGHT)
		self.remainLine.SetLimitWidth(ROW_REMAIN_WIDTH)
		self.remainLine.SetPackedFontColor(COLOR_REMAIN)
		self.remainLine.Hide()

		# Locked rows carry the padlock instead of a remaining-time value, so the
		# two never share the column.
		self.lockIcon = ui.ImageBox()
		self.lockIcon.SetParent(self)
		self.lockIcon.AddFlag("not_pick")
		self.lockIcon.SetPosition(lockX, (ROW_HEIGHT - LOCK_SIZE) // 2)
		self.lockIcon.LoadImage(LOCK_IMG)
		self.lockIcon.Hide()

	def __del__(self):
		ui.Window.__del__(self)

	def SetRowEvents(self, clickEvent, wheelEvent):
		self.clickEvent = clickEvent
		self.wheelEvent = wheelEvent

	def SetData(self, titleId, text, fontColor, remainText, owned, active):
		self.titleId = titleId
		self.owned = owned
		self.active = active
		self.filled = True

		self.nameLine.SetText(text)
		self.nameLine.SetPackedFontColor(fontColor)
		self.nameLine.Show()

		if owned:
			self.remainLine.SetText(remainText)
			self.remainLine.Show()
			self.lockIcon.Hide()
		else:
			self.remainLine.SetText("")
			self.remainLine.Hide()
			self.lockIcon.Show()

		self.background.Show()
		self.RefreshVisual()

	def Clear(self):
		self.titleId = 0
		self.owned = False
		self.active = False
		self.hovered = False
		self.filled = False

		self.nameLine.SetText("")
		self.nameLine.Hide()
		self.remainLine.SetText("")
		self.remainLine.Hide()
		self.lockIcon.Hide()
		self.background.Hide()

	def SetActive(self, active):
		self.active = active
		self.RefreshVisual()

	def ClearHover(self):
		self.hovered = False
		self.RefreshVisual()

	def RefreshVisual(self):
		if not self.filled:
			return

		if self.active and self.titleId:
			image = ROW_IMG_DOWN
		elif self.hovered and self.owned and self.titleId:
			image = ROW_IMG_HOVER
		else:
			image = ROW_IMG

		# LoadImage re-resolves the texture, so only touch it on a real change.
		if image != self.currentImage:
			self.currentImage = image
			self.background.LoadImage(image)

	def OnMouseOverIn(self):
		self.hovered = True
		self.RefreshVisual()

	def OnMouseOverOut(self):
		self.hovered = False
		self.RefreshVisual()

	def OnMouseLeftButtonDown(self):
		if not self.owned or not self.titleId:
			return
		if self.clickEvent:
			self.clickEvent(self.titleId)

	def OnRunMouseWheel(self, nLen):
		if not self.IsInPosition():
			return False
		if self.wheelEvent:
			return self.wheelEvent(nLen)

		return False


class TitleWindow(ui.ScriptWindow):

	VISIBLE_ROW_COUNT = 7

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__Initialize()
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __Initialize(self):
		self.board = None
		self.activeCaption = None
		self.activePlate = None
		self.activeValue = None
		self.activeRemain = None
		self.unequipButton = None
		self.listCaption = None
		self.listPanel = None
		self.listArea = None
		self.scrollBar = None
		self.rowWidgets = []

		self.titleList = []
		self.pendingList = []
		self.pendingActive = 0
		self.activeTitleId = 0
		self.scrollPos = 0
		self.positioned = False

	def __LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/titlewindow.py")
		except:
			import exception
			exception.Abort("TitleWindow.LoadWindow.LoadScript")
			return

		try:
			GetObject = self.GetChild
			self.board = GetObject("Board")
			self.activeCaption = GetObject("ActiveCaption")
			self.activePlate = GetObject("ActivePlate")
			self.activeValue = GetObject("ActiveValue")
			self.activeRemain = GetObject("ActiveRemain")
			self.unequipButton = GetObject("UnequipButton")
			self.listCaption = GetObject("ListCaption")
			self.listPanel = GetObject("ListPanel")
			self.listArea = GetObject("ListArea")
		except:
			import exception
			exception.Abort("TitleWindow.LoadWindow.BindObject")
			return

		self.board.SetTitleName(LocaleText("TITLE_WINDOW_TITLE", "Titles"))
		self.board.SetCloseEvent(ui.__mem_func__(self.Close))

		self.activePlate.AddFlag("not_pick")

		panelWidth = GetObject("ActivePanel").GetWidth()
		captionWidth = panelWidth - CAPTION_MARGIN * 2

		self.activeCaption.SetSize(captionWidth, LABEL_HEIGHT)
		self.activeCaption.SetLimitWidth(captionWidth)
		self.activeCaption.SetPackedFontColor(COLOR_CAPTION)
		self.activeCaption.SetText(LocaleText("TITLE_WINDOW_ACTIVE", "Active title"))

		self.listCaption.SetSize(captionWidth, LABEL_HEIGHT)
		self.listCaption.SetLimitWidth(captionWidth)
		self.listCaption.SetPackedFontColor(COLOR_CAPTION)
		self.listCaption.SetText(LocaleText("TITLE_WINDOW_ALL", "All titles"))

		# The equipped title reads as a preview of the name tag, so it sits on
		# the same plate the rows use, centred in both locales.
		# No SetSize here: CTextLine anchors ae text at m_rect.right, which would
		# drag the centred label off the plate. Button.SetText centres the same way.
		self.activeValue.SetLimitWidth(ROW_WIDTH - ROW_SIDE_MARGIN * 2)
		self.activeValue.SetHorizontalAlignCenter()
		self.activeValue.SetVerticalAlignCenter()

		self.unequipButton.SetText(LocaleText("TITLE_WINDOW_UNEQUIP", "Unequip"))
		self.unequipButton.SetEvent(ui.__mem_func__(self.__OnClickUnequip))

		# The remaining-time label and the Unequip button share the strip under
		# the plate. The panel is ("ltr",) and the engine never mirrors
		# code-positioned children, so ae has to swap their sides by hand --
		# otherwise both anchor right and the label draws under the button.
		buttonX, buttonY = self.unequipButton.GetLocalPosition()
		buttonWidth = self.unequipButton.GetWidth()
		remainY = self.activeRemain.GetLocalPosition()[1]

		if localeinfo.IsARABIC():
			buttonX = CAPTION_MARGIN + 2
			self.unequipButton.SetPosition(buttonX, buttonY)
			remainX = buttonX + buttonWidth + 12
			remainWidth = panelWidth - remainX - CAPTION_MARGIN
		else:
			remainX = CAPTION_MARGIN + 10
			remainWidth = buttonX - remainX - 12

		self.activeRemain.SetPosition(remainX, remainY)
		self.activeRemain.SetSize(remainWidth, LABEL_HEIGHT)
		self.activeRemain.SetLimitWidth(remainWidth)
		self.activeRemain.SetPackedFontColor(COLOR_REMAIN)

		# Row count follows the uiscript's list area, so retuning the layout
		# there never leaves rows hanging outside the panel.
		self.VISIBLE_ROW_COUNT = max(1, self.listArea.GetHeight() // ROW_HEIGHT)

		rowWidth = self.listArea.GetWidth()
		for index in xrange(self.VISIBLE_ROW_COUNT):
			row = TitleRow(rowWidth)
			row.SetParent(self.listArea)
			row.SetPosition(0, index * ROW_HEIGHT)
			row.SetRowEvents(ui.__mem_func__(self.__OnClickRow), ui.__mem_func__(self.__OnRowWheel))
			row.Show()
			self.rowWidgets.append(row)

		# uiadvancedgameoptions.ScrollBarNew (the 7px "adv" bar) has no uiscript
		# type, so it is built here; its API matches the thin bar it replaces.
		# Imported lazily because only uisystem pulls that module at boot.
		import uiadvancedgameoptions

		areaX, areaY = self.listArea.GetLocalPosition()
		self.scrollBar = uiadvancedgameoptions.ScrollBarNew()
		self.scrollBar.SetParent(self.listPanel)
		self.scrollBar.SetScrollBarSize(self.listArea.GetHeight())
		self.scrollBar.SetPosition(areaX + self.listArea.GetWidth() + SCROLL_GAP, areaY)
		self.scrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		self.scrollBar.Hide()

		# CWindow::SetSize writes m_rect.right without re-running
		# OnChangePosition, and CTextLine anchors ae text at m_rect.right --
		# so the labels resized above need one cascade before they draw.
		self.UpdateRect()

		self.__RefreshActive()
		self.__RefreshList()

	def Destroy(self):
		self.Close()
		if self.scrollBar:
			self.scrollBar.Destroy()

		self.ClearDictionary()
		self.__Initialize()

	def Open(self):
		if not self.positioned:
			self.SetCenterPosition()
			self.positioned = True

		self.SetTop()
		self.Show()
		net.SendChatPacket("/title_ui")

	def Close(self):
		# Hiding a window fires no OnMouseOverOut, so a row hovered at close
		# time would come back highlighted on the next open.
		for row in self.rowWidgets:
			row.ClearHover()

		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	# --- server pushes -------------------------------------------------

	def RecvTitleWinBegin(self, activeId):
		self.pendingList = []
		self.pendingActive = int(activeId)

	def RecvTitleWinItem(self, payload):
		parts = payload.split('#', 5)
		if len(parts) < 6:
			return

		titleId = int(parts[0])
		color = int(parts[1])
		remainSec = int(parts[2])
		owned = int(parts[3]) != 0
		text = parts[5].replace('\x1f', ' ')

		self.pendingList.append((titleId, color, remainSec, owned, text))

	def RecvTitleWinEnd(self):
		self.titleList = sorted(self.pendingList, key = lambda entry: (not entry[3], entry[0]))
		self.pendingList = []
		self.activeTitleId = self.pendingActive
		self.scrollPos = 0

		if self.scrollBar:
			self.scrollBar.SetPos(0.0, False)

		self.__RefreshActive()
		self.__RefreshList()

	def RecvTitleWinActive(self, activeId):
		self.activeTitleId = int(activeId)
		self.pendingActive = self.activeTitleId
		self.__RefreshActive()

		for row in self.rowWidgets:
			row.SetActive(row.titleId == self.activeTitleId and row.titleId != 0)

	# --- rendering -----------------------------------------------------

	def __FindEntry(self, titleId):
		for entry in self.titleList:
			if entry[0] == titleId:
				return entry

		return None

	def __RefreshActive(self):
		if not self.activeValue:
			return

		entry = self.__FindEntry(self.activeTitleId)

		if 0 == self.activeTitleId:
			self.activeValue.SetText(LocaleText("TITLE_WINDOW_NONE", "No title equipped"))
			self.activeValue.SetPackedFontColor(COLOR_LOCKED)
			self.activeRemain.SetText("")
			self.unequipButton.Disable()
			return

		self.unequipButton.Enable()

		# A TitleWinActive for an id the streamed catalog does not carry (a
		# custom title granted mid-session) must not blank the panel -- keep
		# the last known text; reopening the window re-requests the catalog.
		if entry is None:
			return

		self.activeValue.SetText(entry[4])
		self.activeValue.SetPackedFontColor(ALPHA_OPAQUE | entry[1])
		self.activeRemain.SetText(FormatRemain(entry[2]))

	def __RefreshList(self):
		if not self.rowWidgets:
			return

		total = len(self.titleList)
		maxStart = max(0, total - self.VISIBLE_ROW_COUNT)
		if self.scrollPos > maxStart:
			self.scrollPos = maxStart

		for index in xrange(len(self.rowWidgets)):
			row = self.rowWidgets[index]
			dataIndex = index + self.scrollPos
			if dataIndex >= total:
				row.Clear()
				continue

			titleId, color, remainSec, owned, text = self.titleList[dataIndex]
			if owned:
				fontColor = ALPHA_OPAQUE | color
				remainText = FormatRemain(remainSec)
			else:
				fontColor = COLOR_LOCKED
				remainText = ""

			row.SetData(titleId, text, fontColor, remainText, owned, titleId == self.activeTitleId)

		if self.scrollBar:
			if total > self.VISIBLE_ROW_COUNT:
				# OnUp/OnDown step a fraction of the WHOLE range, so a fixed step
				# pages the list once it gets long -- keep one notch at two rows.
				self.scrollBar.SetScrollStep(min(1.0, 2.0 / float(maxStart)))
				# ScrollBarNew sizes its thumb from an explicit page scale rather
				# than deriving one, so feed it the visible fraction.
				self.scrollBar.SetMiddleBarSize(max(0.15, min(0.8, float(self.VISIBLE_ROW_COUNT) / float(total))))
				self.scrollBar.Show()
			else:
				self.scrollBar.Hide()

	# --- events --------------------------------------------------------

	def __OnScroll(self):
		if not self.scrollBar:
			return

		# ScrollBar.OnMove derives curPos from the dragged bar rect, so it can
		# land a hair outside 0..1 -- an unclamped index would wrap the list.
		maxStart = max(0, len(self.titleList) - self.VISIBLE_ROW_COUNT)
		newPos = int(maxStart * self.scrollBar.GetPos() + 0.5)
		newPos = max(0, min(maxStart, newPos))
		if newPos != self.scrollPos:
			self.scrollPos = newPos
			self.__RefreshList()

	def __OnRowWheel(self, nLen):
		if not self.scrollBar or not self.scrollBar.IsShow():
			return False

		if nLen > 0:
			self.scrollBar.OnUp()
		else:
			self.scrollBar.OnDown()

		return True

	def __OnClickRow(self, titleId):
		if titleId == self.activeTitleId:
			return

		net.SendChatPacket("/title %d" % titleId)

	def __OnClickUnequip(self):
		if 0 == self.activeTitleId:
			return

		net.SendChatPacket("/title 0")
