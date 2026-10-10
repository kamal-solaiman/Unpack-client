# coding: latin_1

import ui
import localeinfo

IS_AR = localeinfo.IsARABIC()

BADGE_IMG_1DIGIT = "d:/ymir work/ui/badge/notification_badge_1.png"
BADGE_IMG_2DIGIT = "d:/ymir work/ui/badge/notification_badge_2.png"
BADGE_COLOR = 0xffd63333
BADGE_TEXT_COLOR = 0xffffffff
BADGE_H = 16
BADGE_W_1DIGIT = 16
BADGE_W_2DIGIT = 22
BADGE_OVERHANG = 5
BADGE_CAP_TEXT = "9+"

class Badge(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.AddFlag("not_pick")
		self.SetSize(BADGE_W_1DIGIT, BADGE_H)
		self.count = 0
		self.wideLook = False
		self.anchorParentWidth = 0

		img = ui.ImageBox()
		img.SetParent(self)
		img.AddFlag("not_pick")
		try:
			img.LoadImage(BADGE_IMG_1DIGIT)
			img.Show()
		except:
			img = None
		self.img = img

		bar = None
		if not img:
			bar = ui.Bar()
			bar.SetParent(self)
			bar.AddFlag("not_pick")
			bar.SetColor(BADGE_COLOR)
			bar.SetSize(BADGE_W_1DIGIT, BADGE_H)
			bar.Show()
		self.fallbackBar = bar

		text = ui.TextLine()
		text.SetParent(self)
		text.AddFlag("not_pick")
		text.SetWindowHorizontalAlignCenter()
		text.SetHorizontalAlignCenter()
		text.SetPosition(0, -1)
		text.SetPackedFontColor(BADGE_TEXT_COLOR)
		text.Show()
		self.textLine = text

		self.Hide()

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.textLine = None
		self.img = None
		self.fallbackBar = None

	def SetAnchorParent(self, parent):
		self.SetParent(parent)
		self.anchorParentWidth = parent.GetWidth()
		self.__Reposition()

	def SetCount(self, count):
		count = int(count)
		if count == self.count:
			return
		self.count = count
		if count <= 0:
			self.Hide()
			return
		if count > 9:
			self.__ApplyLook(True)
			self.textLine.SetText(BADGE_CAP_TEXT)
		else:
			self.__ApplyLook(False)
			self.textLine.SetText(str(count))
		self.__Reposition()
		self.Show()

	def __ApplyLook(self, wide):
		if wide == self.wideLook:
			return
		if self.img:
			try:
				if wide:
					self.img.LoadImage(BADGE_IMG_2DIGIT)
				else:
					self.img.LoadImage(BADGE_IMG_1DIGIT)
			except:
				return	# keep the old look-state so the next count change retries the load
		self.wideLook = wide
		if wide:
			w = BADGE_W_2DIGIT
		else:
			w = BADGE_W_1DIGIT
		self.SetSize(w, BADGE_H)
		if self.fallbackBar:
			self.fallbackBar.SetSize(w, BADGE_H)

	def __Reposition(self):
		if IS_AR:
			self.SetPosition(-BADGE_OVERHANG, -BADGE_OVERHANG)
		else:
			self.SetPosition(self.anchorParentWidth - self.GetWidth() + BADGE_OVERHANG, -BADGE_OVERHANG)

_badgeDict = {}
# counts pushed before the anchor widget exists; replayed by Attach
_pendingDict = {}

def Attach(name, parentButton):
	badge = Badge()
	badge.SetAnchorParent(parentButton)
	_badgeDict[name] = badge
	count = _pendingDict.pop(name, 0)
	if count:
		badge.SetCount(count)
	return badge

def Detach(name):
	if name in _badgeDict:
		_badgeDict[name].Destroy()
		del _badgeDict[name]
	if name in _pendingDict:
		del _pendingDict[name]

def ClearAll():
	for badge in _badgeDict.values():
		badge.Destroy()
	_badgeDict.clear()
	_pendingDict.clear()

def SetCount(name, count):
	badge = _badgeDict.get(name, None)
	if badge:
		badge.SetCount(count)
	else:
		_pendingDict[name] = int(count)
