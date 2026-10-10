# coding: latin_1
#
# Hover tooltip listing what a challenge actually counts.
#
# Shared on purpose: the global tab feeds it item vnums from RewardTargets, and the personal tab
# feeds it monster vnums through the same SetTargets() call. Groups are (kind, [vnum]) pairs, so
# a mission that wants one item per equipment slot is just several groups.

import ui
import app
import item
import nonplayer
import localeinfo
import wndMgr
if app.ENABLE_RENDER_TARGET:
	import renderTarget

ICON_SIZE = 32      # one inventory cell; the floor for a row's height, not a fixed icon size
ICON_GAP = 6
PAD = 14

# Every vertical gap is named so spacing can be tuned without hunting through the layout.
TITLE_H = 18        # the title line itself
LINE_H = 18         # any other text line
GAP_TITLE = 8       # under the title
GAP_CAPTION = 8     # under the caption, before the first icon row
GAP_ICONS = 8       # between an icon row and the names beneath it
GAP_GROUP = 12      # between one group and the next

MIN_W = 200

# A monster has no flat icon, so its group renders a live model instead. Each render target is
# its own D3D texture and costs a render pass per frame while visible, so they are pooled and
# capped rather than created per target -- see the 2026-08-08 decision in docs/WEEKLY_CHALLENGES.md.
# Past the cap a target degrades to its name, which is still readable.
MODEL_W, MODEL_H = 64  * 2 , 76 * 2
MAX_MODELS = 3
CURSOR_GAP = 16     # clearance from the pointer so the board never sits under it
# Without a cap a 12-target mission produces one enormous line and a board wider than the window.
MAX_TEXT_W = 300

# Same three roles as a challenge row, so the same three colours.
TITLE_COLOR = 0xfff2e7c1
CAPTION_COLOR = 0xffc8b3a2
NAME_COLOR = 0xfff1d985

# localeinfo is wrapped and answers "Locale not found: KEY" instead of raising, so getattr's
# default never fires on its own. Same guard as uirewardspeed.LocaleText.
def LocaleText(key, default):
	value = getattr(localeinfo, key, default)
	if not value or value.startswith("Locale not found"):
		return default

	return value

def GetTargetName(kind, vnum):
	if kind == "mob":
		return nonplayer.GetMonsterName(vnum)

	return item.GetItemNameByVnum(vnum)

def GetTargetIcon(kind, vnum):
	if kind == "mob":
		return ""

	item.SelectItem(vnum)
	return item.GetIconImageFileName()

class ChallengeTargetToolTip(ui.ThinBoard):

	def __init__(self):
		ui.ThinBoard.__init__(self, "TOP_MOST", 1)
		self.widgets = []
		self.probe = None
		self.models = []
		self.modelsUsed = 0
		# Never take the cursor: the tooltip sits next to the pointer, and stealing the pick
		# would fire the row's over-out and flicker it in and out.
		self.AddFlag("not_pick")

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def Destroy(self):
		self.widgets = []

	# Grown on demand up to MAX_MODELS and then reused for the life of the tooltip. The widgets
	# are deliberately not in self.widgets: that list is rebuilt per hover, and a pooled model
	# has to outlive it.
	def __AcquireModel(self, vnum):
		if not app.ENABLE_RENDER_TARGET or self.modelsUsed >= MAX_MODELS:
			return None

		if self.modelsUsed >= len(self.models):
			model = ui.RenderTarget()
			model.SetParent(self)
			model.SetSize(MODEL_W, MODEL_H)
			model.Load()		# always after SetSize, or the target allocates at the wrong size
			model.AddFlag("not_pick")
			self.models.append(model)

		model = self.models[self.modelsUsed]
		self.modelsUsed += 1
		renderTarget.SetVisibility(model.GetIndex(), True)
		renderTarget.SelectModel(model.GetIndex(), vnum)
		model.Show()
		return model

	# Visibility off, not just hidden: an invisible render target still costs its pass.
	def ReleaseModels(self, keep = 0):
		for i in range(keep, len(self.models)):
			model = self.models[i]
			renderTarget.SetVisibility(model.GetIndex(), False)
			model.Hide()

	# Greedy wrap measured in pixels rather than characters -- Arabic glyph widths make any
	# character budget meaningless.
	def __WrapNames(self, names, maxWidth):
		if self.probe is None:
			self.probe = ui.TextLine()
			self.probe.SetParent(self)
			self.probe.AddFlag("not_pick")
			self.probe.Hide()

		lines = []
		current = []
		for name in names:
			self.probe.SetText(", ".join(current + [name]))
			if current and int(self.probe.GetTextWidth()) > maxWidth:
				lines.append(", ".join(current))
				current = [name]
			else:
				current.append(name)

		if current:
			lines.append(", ".join(current))

		return lines

	# entries are (icon, name, iconWidth, iconHeight); returns the row's widgets plus the
	# measurements pass 2 needs to place a mixed-height row.
	def __BuildRow(self, entries, widgets):
		icons = [entry[0] for entry in entries if entry[0]]
		rowHeight = max([entry[3] for entry in entries] + [ICON_SIZE])
		rowWidth = sum([entry[2] for entry in entries]) + ICON_GAP * max(0, len(entries) - 1)

		nameLines = []
		for line in self.__WrapNames([entry[1] for entry in entries], MAX_TEXT_W):
			textLine = self.__MakeText(line, NAME_COLOR)
			widgets.append(textLine)
			nameLines.append(textLine)

		return (icons, rowHeight, rowWidth, nameLines)

	def __MakeText(self, text, color):
		textLine = ui.TextLine()
		textLine.SetParent(self)
		# Centred, so the anchor is the board's midline and the RTL/LTR distinction drops out.
		textLine.SetHorizontalAlignCenter()
		textLine.SetText(text)
		textLine.SetPackedFontColor(color)
		textLine.AddFlag("not_pick")
		textLine.Show()
		return textLine

	# Built in two passes. A text line's anchor depends on the board's width and the board's
	# width depends on the text, so nothing can be positioned until every string is measured --
	# placing as we go is what made the Arabic layout flow out of the board.
	#
	# Every widget is created in code, so each one has to stay referenced on self or SetParent
	# alone will not keep it alive.
	# captionKey "" means "decide from the shape": more than one target reads as any-of.
	# A caller with something specific to say passes its own key, which shows even for one.
	def SetTargets(self, title, groups, captionKey = ""):
		self.widgets = []
		isArabic = localeinfo.IsARABIC()

		# ---- pass 1: create and measure, no positions yet
		rows = []
		widgets = []

		titleLine = self.__MakeText(title, TITLE_COLOR)
		widgets.append(titleLine)

		caption = None
		captionText = LocaleText(captionKey, "") if captionKey else (
			LocaleText("REWARD_TARGETS_CAPTION", "Any of the following:")
			if sum(len(vnums) for (kind, vnums) in groups) > 1 else "")
		if captionText:
			caption = self.__MakeText(captionText, CAPTION_COLOR)
			widgets.append(caption)

		# Item icons are 1, 2 or 3 inventory cells tall and 1 or 2 wide, so a fixed 32x32 step
		# overlaps them. Each ImageBox is measured after LoadImage and rows wrap on accumulated
		# pixel width, not on a count.
		self.modelsUsed = 0
		for (kind, vnums) in groups:
			entries = []
			for vnum in vnums:
				icon = None
				(iconW, iconH) = (0, 0)

				if kind == "mob":
					icon = self.__AcquireModel(vnum)
				else:
					iconPath = GetTargetIcon(kind, vnum)
					if iconPath:
						icon = ui.ImageBox()
						icon.SetParent(self)
						icon.LoadImage(iconPath)
						icon.AddFlag("not_pick")
						icon.Show()
						widgets.append(icon)

				if icon:
					(iconW, iconH) = (icon.GetWidth(), icon.GetHeight())

				entries.append((icon, GetTargetName(kind, vnum), iconW, iconH))

			chunk = []
			chunkWidth = 0
			for entry in entries:
				addWidth = entry[2] + (ICON_GAP if chunk else 0)
				if chunk and chunkWidth + addWidth > MAX_TEXT_W:
					rows.append(self.__BuildRow(chunk, widgets))
					(chunk, chunkWidth) = ([entry], entry[2])
				else:
					chunk.append(entry)
					chunkWidth += addWidth

			if chunk:
				rows.append(self.__BuildRow(chunk, widgets))

		width = MIN_W
		for (icons, rowHeight, rowWidth, nameLines) in rows:
			width = max(width, PAD * 2 + rowWidth)
		for widget in widgets:
			if isinstance(widget, ui.TextLine):
				width = max(width, PAD * 2 + min(MAX_TEXT_W, int(widget.GetTextWidth())))

		# ---- pass 2: the width is known, so anchors are too
		textX = width / 2
		y = PAD

		titleLine.SetPosition(textX, y)
		y += TITLE_H + GAP_TITLE

		if caption:
			caption.SetPosition(textX, y)
			y += LINE_H + GAP_CAPTION

		for (icons, rowHeight, rowWidth, nameLines) in rows:
			# The row is centred on the board; Arabic still fills it right-to-left, so each icon
			# steps back by its own width first. Mixed heights sit on a common centre line.
			x = (width + rowWidth) / 2 if isArabic else (width - rowWidth) / 2

			for icon in icons:
				iconW = icon.GetWidth()
				if isArabic:
					x -= iconW

				icon.SetPosition(x, y + (rowHeight - icon.GetHeight()) / 2)
				x += -ICON_GAP if isArabic else iconW + ICON_GAP

			y += rowHeight + GAP_ICONS
			for textLine in nameLines:
				textLine.SetPosition(textX, y)
				y += LINE_H

			y += GAP_GROUP

		self.widgets = widgets
		self.ReleaseModels(self.modelsUsed)
		self.SetSize(width, y - GAP_GROUP + PAD)

	# Sits against the cursor, trailing it on the side the language reads from, and flips to the
	# other side or above when it would run off the screen.
	def ShowNearMouse(self):
		(mouseX, mouseY) = wndMgr.GetMousePosition()
		(screenW, screenH) = (wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())

		if localeinfo.IsARABIC():
			posX = mouseX - self.GetWidth() - CURSOR_GAP
			if posX < 4:
				posX = mouseX + CURSOR_GAP
		else:
			posX = mouseX + CURSOR_GAP
			if posX + self.GetWidth() > screenW - 4:
				posX = mouseX - self.GetWidth() - CURSOR_GAP

		posY = mouseY + CURSOR_GAP
		if posY + self.GetHeight() > screenH - 4:
			posY = mouseY - self.GetHeight() - CURSOR_GAP

		self.SetPosition(
			max(4, min(posX, screenW - self.GetWidth() - 4)),
			max(4, min(posY, screenH - self.GetHeight() - 4)))
		self.SetTop()
		self.Show()

__toolTip = None

def GetToolTip():
	global __toolTip
	if __toolTip is None:
		__toolTip = ChallengeTargetToolTip()

	return __toolTip

def HideToolTip():
	if __toolTip is not None:
		__toolTip.ReleaseModels()
		__toolTip.Hide()
