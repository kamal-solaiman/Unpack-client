# coding: latin_1

import ui
import localeinfo
import systemSetting
import wndMgr

PRESET_COLORS = [0xFFE000, 0xFF3030, 0xFF00E0, 0x9B30FF, 0x00CCFF, 0x30FF60, 0xFF8000, 0xFFFFFF]
CLASSIC_COLOR = 0xFFE000
DIGIT_PATH = "d:/ymir work/effect/affect/damagevalue/"

# CTextLine anchors its text at m_rect.right under CP_ARABIC and at m_rect.left otherwise,
# and the uiscript text loader never sizes the window - an unsized label collapses both
# anchors onto x and the ae client draws the text leftwards out of the panel.
LABEL_WIDE = 252
LABEL_NARROW = 34
LABEL_HEIGHT = 16

SLOT_TITLES = (
	getattr(localeinfo, "DMGCOLOR_PICKER_TITLE_NORMAL", "Damage Color - Normal"),
	getattr(localeinfo, "DMGCOLOR_PICKER_TITLE_CRITICAL", "Damage Color - Critical"),
	getattr(localeinfo, "DMGCOLOR_PICKER_TITLE_PIERCE", "Damage Color - Piercing"),
)

PREVIEW_SWATCH_WIDTH = 266
PREVIEW_SWATCH_HEIGHT = 24
PREVIEW_SWATCH_Y = 20

# ColorFactor baked into cylinder_effect_gold.mse - what slot 0 draws
AUTO_HUNT_DEFAULT_COLOR = 0xA1892A

# Hue wheel at the stock gold's own saturation/lightness (H 48, S 59%, L 40%),
# so every choice sits in the same tonal family as the untouched aura.
AUTO_HUNT_PRESET_COLORS = [0xA1892A, 0xA1482A, 0xA12A48, 0xA12AA1, 0x5C2AA1, 0x2A6FA1, 0x2AA183, 0x48A12A]


def GetAutoHuntEffectColor(slotIndex):
	return systemSetting.GetAutoHuntEffectColor()


def SetAutoHuntEffectColor(slotIndex, rgb):
	systemSetting.SetAutoHuntEffectColor(rgb)


HOVER_FRAME_COLOR = 0xFFFFFFFF
HOVER_FRAME_SIZE = 1
HOVER_LIGHTEN = 0.30


def MixRGB(rgb, target, amount):
	out = 0
	for shift in (16, 8, 0):
		c = (rgb >> shift) & 0xFF
		t = (target >> shift) & 0xFF
		out |= int(c + (t - c) * amount) << shift
	return out


class ColorSwatch(ui.Bar):
	def __init__(self):
		ui.Bar.__init__(self)
		self.clickEvent = None
		self.clickArgs = ()
		self.rgb = CLASSIC_COLOR
		self.isMouseOver = False

		self.frames = []
		for i in xrange(4):
			frame = ui.Bar()
			frame.SetParent(self)
			frame.AddFlag("not_pick")
			frame.SetColor(HOVER_FRAME_COLOR)
			frame.Hide()
			self.frames.append(frame)

	def __del__(self):
		ui.Bar.__del__(self)

	def SetClickEvent(self, event, *args):
		self.clickEvent = event
		self.clickArgs = args

	def SetRGB(self, rgb):
		if not rgb:
			rgb = CLASSIC_COLOR
		self.rgb = rgb
		self.__RefreshColor()

	def SetSize(self, width, height):
		ui.Bar.SetSize(self, width, height)
		self.__RefreshFrame()

	def __RefreshColor(self):
		rgb = self.rgb
		if getattr(self, "isMouseOver", False):
			rgb = MixRGB(rgb, 0xFFFFFF, HOVER_LIGHTEN)
		self.SetColor(0xFF000000 | rgb)

	def __RefreshFrame(self):
		frames = getattr(self, "frames", None)
		if not frames:
			return

		width = self.GetWidth()
		height = self.GetHeight()
		size = HOVER_FRAME_SIZE
		top, right, bottom, left = frames

		top.SetSize(width, size)
		top.SetPosition(0, 0)
		bottom.SetSize(width, size)
		bottom.SetPosition(0, height - size)
		left.SetSize(size, height)
		left.SetPosition(0, 0)
		right.SetSize(size, height)
		right.SetPosition(width - size, 0)

	def __ShowFrame(self, isShow):
		for frame in getattr(self, "frames", []):
			if isShow:
				frame.Show()
			else:
				frame.Hide()

	# a window hidden while hovered never gets OnMouseOverOut
	def ResetHover(self):
		self.isMouseOver = False
		self.__RefreshColor()
		self.__ShowFrame(False)

	def OnMouseOverIn(self):
		if not self.clickEvent:
			return
		self.isMouseOver = True
		self.__RefreshColor()
		self.__ShowFrame(True)

	def OnMouseOverOut(self):
		self.isMouseOver = False
		self.__RefreshColor()
		self.__ShowFrame(False)

	def OnMouseLeftButtonDown(self):
		if self.clickEvent:
			self.clickEvent(*self.clickArgs)
		return True


class DamageColorPicker(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.slotIndex = 0
		self.applyEvent = None
		self.getEvent = None
		self.setEvent = None
		self.useDigitPreview = True
		self.defaultColor = CLASSIC_COLOR
		self.presetColors = PRESET_COLORS
		self.curColor = 0
		self.presetSwatches = []
		self.previewImages = []
		self.previewSwatch = None
		self.currentSwatch = None
		self.pickerImage = None
		self.pickerButton = None
		self.pickerDotImage = None
		self.hexEditLine = None
		self.defaultButton = None
		self.applyButton = None
		self.board = None
		self.isLoaded = False
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadWindow(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "UIScript/DamageColorPicker.py")

		self.board = self.GetChild("board")
		self.board.SetCloseEvent(ui.__mem_func__(self.Close))

		self.pickerImage = self.GetChild("PickerImage")
		self.pickerButton = self.GetChild("PickerButton")
		self.pickerDotImage = self.GetChild("PickerDotImage")
		self.pickerDotImage.Hide()
		self.pickerButton.SetEvent(ui.__mem_func__(self.__OnClickGradient))

		self.hexEditLine = self.GetChild("HexEditLine")
		self.hexEditLine.SetReturnEvent(ui.__mem_func__(self.__OnHexEnter))

		presetBar = self.GetChild("PresetBar")
		self.presetSwatches = []
		for i in xrange(len(PRESET_COLORS)):
			swatch = ColorSwatch()
			swatch.SetParent(presetBar)
			swatch.SetPosition(i * 31, 0)
			swatch.SetSize(26, 16)
			swatch.SetRGB(PRESET_COLORS[i])
			swatch.SetClickEvent(ui.__mem_func__(self.__OnClickPreset), i)
			swatch.Show()
			self.presetSwatches.append(swatch)

		self.currentSwatch = ColorSwatch()
		self.currentSwatch.SetParent(self.GetChild("CurrentSwatchSlot"))
		self.currentSwatch.SetPosition(0, 0)
		self.currentSwatch.SetSize(68, 20)
		self.currentSwatch.Show()

		previewBar = self.GetChild("PreviewBar")
		self.previewImages = []
		for i in xrange(10):
			img = ui.ImageBox()
			img.SetParent(previewBar)
			img.SetPosition(i * 26, 0)
			img.Show()
			self.previewImages.append(img)

		self.previewSwatch = ColorSwatch()
		self.previewSwatch.SetParent(previewBar)
		self.previewSwatch.SetPosition(0, PREVIEW_SWATCH_Y)
		self.previewSwatch.SetSize(PREVIEW_SWATCH_WIDTH, PREVIEW_SWATCH_HEIGHT)
		self.previewSwatch.Hide()

		self.__SetupLabel("PresetLabel", getattr(localeinfo, "DMGCOLOR_PICKER_PRESETS", "Presets"), LABEL_WIDE)
		self.__SetupLabel("HexLabel", getattr(localeinfo, "DMGCOLOR_PICKER_HEX", "Hex"), LABEL_NARROW)
		self.__SetupLabel("PreviewLabel", getattr(localeinfo, "DMGCOLOR_PICKER_PREVIEW", "Preview"), LABEL_WIDE)

		self.defaultButton = self.GetChild("DefaultButton")
		self.defaultButton.SetText(getattr(localeinfo, "DMGCOLOR_PICKER_DEFAULT", "Default"))
		self.defaultButton.SetEvent(ui.__mem_func__(self.__OnDefault))

		self.applyButton = self.GetChild("ApplyButton")
		self.applyButton.SetText(getattr(localeinfo, "DMGCOLOR_PICKER_APPLY", "Apply"))
		self.applyButton.SetEvent(ui.__mem_func__(self.__OnApply))

		self.isLoaded = True

	def __SetupLabel(self, childName, text, width):
		label = self.GetChild(childName)
		label.SetText(text)
		label.SetSize(width, LABEL_HEIGHT)
		return label

	def __OnClickPreset(self, index):
		if index < len(self.presetColors):
			self.__SetColor(self.presetColors[index])

	def Open(self, slotIndex, applyEvent, getEvent = None, setEvent = None, title = None, useDigitPreview = True, defaultColor = CLASSIC_COLOR, presetColors = None):
		self.slotIndex = slotIndex
		self.applyEvent = applyEvent
		self.getEvent = getEvent
		self.setEvent = setEvent
		self.useDigitPreview = useDigitPreview
		self.defaultColor = defaultColor
		self.presetColors = presetColors or PRESET_COLORS
		self.__RefreshPresetSwatches()
		if self.board:
			self.board.SetTitleName(title or SLOT_TITLES[slotIndex])
		if self.pickerDotImage:
			self.pickerDotImage.Hide()
		self.__SetColor(self.__LoadColor())
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def __RefreshPresetSwatches(self):
		for i in xrange(len(self.presetSwatches)):
			swatch = self.presetSwatches[i]
			swatch.ResetHover()
			if i < len(self.presetColors):
				swatch.SetRGB(self.presetColors[i])
				swatch.Show()
			else:
				swatch.Hide()

	def __LoadColor(self):
		if self.getEvent:
			return self.getEvent(self.slotIndex)
		return systemSetting.GetDamageColor(self.slotIndex)

	def __StoreColor(self, rgb):
		if self.setEvent:
			self.setEvent(self.slotIndex, rgb)
		else:
			systemSetting.SetDamageColor(self.slotIndex, rgb)

	def Close(self):
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def __SetColor(self, rgb):
		self.curColor = rgb
		if self.currentSwatch:
			self.currentSwatch.SetRGB(rgb or self.defaultColor)
		if self.hexEditLine:
			self.hexEditLine.SetText("%06X" % (rgb if rgb else self.defaultColor))
		self.__RefreshPreview()

	def __RefreshPreview(self):
		if not self.useDigitPreview:
			for img in self.previewImages:
				img.Hide()
			if self.previewSwatch:
				self.previewSwatch.SetRGB(self.curColor or self.defaultColor)
				self.previewSwatch.Show()
			return

		if self.previewSwatch:
			self.previewSwatch.Hide()

		for i in xrange(10):
			img = self.previewImages[i]
			if self.curColor:
				img.LoadImage(DIGIT_PATH + "target_white_%d.dds" % i)
				r = ((self.curColor >> 16) & 0xFF) / 255.0
				g = ((self.curColor >> 8) & 0xFF) / 255.0
				b = (self.curColor & 0xFF) / 255.0
				img.SetDiffuseColor(r, g, b, 1.0)
			else:
				img.LoadImage(DIGIT_PATH + "target_%d.dds" % i)
				img.SetDiffuseColor(1.0, 1.0, 1.0, 1.0)

	def __OnHexEnter(self):
		text = self.hexEditLine.GetText().lstrip("#")
		try:
			rgb = int(text, 16) & 0xFFFFFF
		except ValueError:
			self.__SetColor(self.curColor)
			return
		if rgb == 0:
			self.__OnDefault()
			return
		if ((rgb >> 16) & 0xFF) <= 20 and ((rgb >> 8) & 0xFF) <= 20 and (rgb & 0xFF) <= 20:
			self.__SetColor(self.curColor)
			return
		self.__SetColor(rgb)

	def __OnClickGradient(self):
		xMouse, yMouse = wndMgr.GetRealMousePosition()
		rgbColor = wndMgr.GetColorAtPosition(xMouse, yMouse)
		r, g, b = int(rgbColor[0]), int(rgbColor[1]), int(rgbColor[2])
		if r <= 20 and g <= 20 and b <= 20:
			return
		xImg, yImg = self.pickerImage.GetGlobalPosition()
		xMousePos, yMousePos = wndMgr.GetMousePosition()
		self.pickerDotImage.SetPosition(
			int(xMousePos - xImg - self.pickerDotImage.GetWidth() / 2),
			int(yMousePos - yImg - self.pickerDotImage.GetHeight() / 2))
		self.pickerDotImage.Show()
		self.__SetColor((r << 16) | (g << 8) | b)

	def __OnDefault(self):
		self.curColor = 0
		self.__StoreColor(0)
		systemSetting.SaveConfig()
		self.__SetColor(0)
		if self.applyEvent:
			self.applyEvent(self.slotIndex)
		self.Close()

	def __OnApply(self):
		self.__StoreColor(self.curColor)
		systemSetting.SaveConfig()
		if self.applyEvent:
			self.applyEvent(self.slotIndex)
		self.Close()

	def Destroy(self):
		self.presetSwatches = []
		self.previewImages = []
		self.previewSwatch = None
		self.currentSwatch = None
		self.applyEvent = None
		self.getEvent = None
		self.setEvent = None
		ui.ScriptWindow.Destroy(self)
