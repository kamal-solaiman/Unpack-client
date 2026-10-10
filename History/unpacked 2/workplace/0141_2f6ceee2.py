# coding: latin_1
# Advanced Game Options Window - Integrates old game options into new UI system

import app
import pack
import net
import player
import dbg
import chat
import wndMgr
import systemSetting
import snd
import background
import time

import ui
import constinfo
import uiselectmusic
import musicinfo
import localeinfo
import uiscriptlocale
import uidamagecolorpicker

if app.ENABLE_COMMUNITY_SYSTEM:
	import community
	_COMM_BLOCK_MASTERS = (
		community.COMMUNITY_CFG_BLOCK_EXCHANGE,
		community.COMMUNITY_CFG_BLOCK_PARTY_INVITE,
		community.COMMUNITY_CFG_BLOCK_GUILD_INVITE,
		community.COMMUNITY_CFG_BLOCK_WHISPER,
		community.COMMUNITY_CFG_BLOCK_FRIEND_REQUEST,
		community.COMMUNITY_CFG_BLOCK_PARTY_REQUEST,
	)

if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
	import uiphasecurtain

MUSIC_FILENAME_MAX_LEN = 25
blockMode = 0
IMG_DIR = "d:/ymir work/ui/game/advanced_game_options/"
TEXT_MAIN_COLOR = "|cffcab5a4"

if app.ENABLE_GRAPHIC_ON_OFF:
	GRAPHIC_LEVEL_MAX_NUM = 5

# Category structure for the advanced game options
# Each category maps to a game_option_*.py file
option_data = [
	{
		"category": localeinfo.GAME_OPTIONS_MAIN_0,  # game_option_0.py
		"icon": "interface",
		"subcategories": []
	},
	{
		"category": localeinfo.GAME_OPTIONS_MAIN,  # game_option_1.py
		"icon": "gameplay",
		"subcategories": []
	},
	{
		"category": localeinfo.GAME_OPTIONS_MAIN2,  # game_option_2.py
		"icon": "graphics",
		"subcategories": []
	},
	{
		"category": localeinfo.GAME_OPTIONS_MAIN_7,  # game_option_3.py
		"icon": "environment",
		"subcategories": []
	},
	{
		"category": localeinfo.GAME_OPTIONS_MAIN_2,  # game_option_4.py
		"icon": "sound",
		"subcategories": []
	}
]

class AdvancedGameOptionsWindow(ui.BoardWithTitleBar):
	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def Destroy(self):
		self.pvpModeButtonDict = {}
		self.blockButtonList = []
		self.viewChatButtonList = []
		self.viewChatToggle = None
		self.nameColorModeButtonList = []
		self.viewTargetBoardButtonList = []
		self.hideNamesToggle = None
		self.hideShopsToggle = None
		self.hideNpcToggle = None
		self.outlineNameToggle = None
		self.hideDamageAllToggle = None
		self.hideDamageMobsToggle = None
		self.damageColorSwatches = []
		self.autoHuntColorSwatch = None
		self.damageColorPicker = None
		self.cameraModeButtonList = []
		self.scrollbar_is_show = False

		if app.ENABLE_AUTO_SHOUT_V2:
			self.showAutoShoutToggle = None

		if app.ENABLE_WINDOW_RESIZE:
			self.resolutionSelector = None

		# Sound controls
		self.ctrlSoundVolume = None
		self.ctrlMusicVolume = None
		self.selectMusicFile = None
		self.selectMusicButton = None
		self.musicListDlg = None

		# Tiling mode
		self.tilingMode = 0
		self.tilingModeButtonList = []
		self.tilingApplyButton = None

		# Conditional feature controls
		if app.ENABLE_FOV_OPTION:
			self.fovController = None
			self.fovValueText = None
			self.fovResetButton = None

		if app.USE_METIN_STONE_SCALE:
			self.metinstoneSize = None

		if app.__SCALE_EFFECT_DAMAGE__:
			self.changeScaleEffDamage = None

		if app.USE_IMPROVEMENTS:
			self.effectController = None

		if app.USE_OFFLINESHOP_VIEW_RANGE:
			self.privateshop_range_controller = None

		if app.WJ_SHOW_MOB_INFO:
			self.showMobInfoButtonList = []

		if app.ENABLE_GRAPHIC_ON_OFF:
			self.petStatusButtonList = []
			self.MountStatusButtonList = []
			# Effect visibility toggles
			self.hideBuffToggle = None
			self.hideSkillToggle = None
			self.hideGeneralToggle = None
			self.hideMonsterToggle = None
			# self.hideProjectilesToggle = None
			self.bossEffectToggle = None

		if app.ENABLE_FPS:
			self.fpsButtonList = []

		if app.USE_BACKGROUND_FPS_CAP:
			self.backgroundFpsToggle = None

		if app.ENABLE_POST_PROCESSING:
			self.ppToggle = None
			self.ppQualityButtonList = []
			self.ppVignetteToggle = None
			self.ppVignetteLabel = None
			self.ppSharpenSlider = None
			self.ppSharpenValueText = None
			self.ppSharpenLabel = None
			self.ppColorGradeLabel = None
			self.ppLUTButtonList = []
			self.ppLUTStrengthSlider = None
			self.ppLUTStrengthValueText = None
			self.ppLUTStrengthLabel = None

		if app.ENABLE_FOG_FIX:
			self.fogButtonList = []

		if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
			self.nightModeToggle = None
			self.snowModeButtonList = []
			self.snowTextureModeButtonList = []

		# Weather Selection System
		self.showNightButtonList = []
		self.saveEnvToggle = None

		if app.ENABLE_SHADOW_RENDER_QUALITY_OPTION:
			self.shadowTargetButtonList = []
			self.shadowQualityButtonList = []
		else:
			self.ctrlShadowQuality = 0

		self.treeShadowButtonList = []
		self.treeLodButtonList = []

		if app.ENABLE_KEYCHANGE_SYSTEM:
			self.keyboardButton = None

		if app.ENABLE_EXTENDED_PICKUP:
			self.pickupIgnoreButtonList = []

		for j in xrange(10):
			for x in xrange(10):
				if self.children.has_key("optionWindow%d" % (j)):
					window = self.children["optionWindow%d" % (j)]
					if window:
						window.Hide()
						window.scrollBar = None
						window.ClearDictionary()
						window.Destroy()
		self.children = {}
		self.Hide()

	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.children = {}
		self.Destroy()
		self.scrollbar_is_show = False
		self.__LoadWindow()
		self.SetTitleName(uiscriptlocale.GAMEOPTION_TITLE)
		self.last_update_time = time.time()
		self.marquee = {}            # TextLine -> cached {full, short, fullW, over}
		self.marqueeHot = None       # the one TextLine currently animating
		self.marqueeHotSince = 0.0
		self.marqueeOffset = 0.0
		self.marqueeDone = False
		self.marqueeHitTime = 0.0
		self.animation_interval = 0.02  # Base interval (40ms)
		self.animation_delay = 0.4  # Delay before animation starts (300ms)
		self.animation_end_pause = 1.0  # Pause at end before reset (500ms)
		self.text_directions = {}
		self.original_texts = {}
		self.expected_ending_texts = {}
		self.default_texts = {}
		self.text_iteration = {}
		self.text_length = {}
		self.text_nr_of_letters_hidden = {}
		self.text_nr_of_letters_revealed = {}
		self.text_hover_start_time = {}  # Track when hover started for delay
		self.text_animation_paused = {}  # Track if animation is paused at end
		self.text_animation_complete = {}

		# Environment effect curtain
		if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
			self.curtain = uiphasecurtain.PhaseCurtain()
			self.curtain.speed = 0.03
			self.curtain.Hide()

	def __LoadWindow(self):
		self.AddFlag("movable")
		self.AddFlag("attach")

		bg = ui.ImageBox()
		bg.SetParent(self)
		bg.AddFlag("attach")
		bg.SetPosition(10, 33)
		bg.LoadImage(IMG_DIR + "background.png")
		bg.OnRunMouseWheel = ui.__mem_func__(self.OnMouseWheel)
		bg.Show()
		self.children["bg"] = bg

		categoryScrollBoard = ui.Window()
		categoryScrollBoard.SetParent(self)
		categoryScrollBoard.SetPosition(10, 33)
		categoryScrollBoard.SetSize(218, 406)
		categoryScrollBoard.Show()
		self.children["categoryScrollBoard"] = categoryScrollBoard

		searchBoard = ui.Window()
		searchBoard.SetParent(self)
		searchBoard.SetPosition(10, 33)
		searchBoard.SetSize(218, 36)
		searchBoard.Show()
		self.children["searchBoard"] = searchBoard

		self.search_bg = ui.ImageBox()
		self.search_bg.SetParent(self.children["searchBoard"])
		self.search_bg.SetPosition(5, 5)
		self.search_bg.LoadImage(IMG_DIR + "search_bg.png")
		self.search_bg.Show()

		self.searchButton = ui.Button()
		self.searchButton.SetParent(self.search_bg)
		self.searchButton.SetUpVisual(IMG_DIR + "btn_search_1.png")
		self.searchButton.SetOverVisual(IMG_DIR + "btn_search_2.png")
		self.searchButton.SetDownVisual(IMG_DIR + "btn_search_3.png")
		self.searchButton.SetPosition(self.search_bg.GetWidth() - self.searchButton.GetWidth() + 3, -2)
		self.searchButton.SAFE_SetEvent(self.StartSearch)
		self.searchButton.Show()

		self.CancelSearchButton = ui.Button()
		self.CancelSearchButton.SetParent(self.search_bg)
		self.CancelSearchButton.SetUpVisual(IMG_DIR + "search_btn_x_0.png")
		self.CancelSearchButton.SetOverVisual(IMG_DIR + "search_btn_x_1.png")
		self.CancelSearchButton.SetDownVisual(IMG_DIR + "search_btn_x_2.png")
		self.CancelSearchButton.SetPosition(self.search_bg.GetWidth() - 56, self.search_bg.GetHeight() / 2 - self.search_bg.GetHeight() / 2 + 2)
		self.CancelSearchButton.SAFE_SetEvent(self.OnPressNameEscapeKey)
		self.CancelSearchButton.Hide()

		self.searchEdit = ui.EditLine()
		self.searchEdit.SetParent(self.search_bg)
		self.searchEdit.SetMax(50)
		self.searchEdit.SetSize(self.search_bg.GetWidth() - self.searchButton.GetWidth() - self.CancelSearchButton.GetWidth() - 10, 15)
		self.searchEdit.SetPosition(36, self.search_bg.GetHeight() / 2 - 15 / 2)
		self.searchEdit.SetLimitWidth(self.searchEdit.GetWidth())
		self.searchEdit.SetEscapeEvent(ui.__mem_func__(self.OnPressNameEscapeKey))
		self.searchEdit.SetReturnEvent(ui.__mem_func__(self.StartSearch))
		self.searchEdit.SetOutline()
		self.searchEdit.Show()

		self.children["filteringEnabled"] = False

		self.scrollBar2 = ScrollBarNew()
		self.scrollBar2.SetParent(self.children["categoryScrollBoard"])
		self.scrollBar2.SetPosition(5, self.search_bg.GetHeight() + 10)
		self.scrollBar2.SetScrollBarSize(bg.GetHeight() - self.search_bg.GetHeight() - 14)
		self.scrollBar2.SetScrollEvent(ui.__mem_func__(self.OnScroll))
		self.scrollBar2.Show()
		self.children["categoryScrollBoard"].OnRunMouseWheel = ui.__mem_func__(self.OnMouseWheelCategories)

		self.categoryButtons = []

		self.GetTitleTextLines()

		for optionIndex, category_data in enumerate(option_data):
			key = category_data["category"]

			categoryButton = ui.Button()
			categoryButton.SetParent(self.children["categoryScrollBoard"])
			categoryButton.SetUpVisual(IMG_DIR + "btn_cat_1.png")
			categoryButton.SetOverVisual(IMG_DIR + "btn_cat_2.png")
			categoryButton.SetDownVisual(IMG_DIR + "btn_cat_3.png")
			categoryButton.SetPosition(14, self.search_bg.GetHeight() + 10 + (optionIndex * (categoryButton.GetHeight() + 5)))
			#categoryButton.SetTextAlignLeft(TEXT_MAIN_COLOR + key, 50)
			categoryButton.SetTextAlignLeftNew(TEXT_MAIN_COLOR + key,150)
			categoryButton.SAFE_SetEvent(self.ClickCategory, optionIndex)

			# the icon file is keyed off the layout index, never the display name:
			# "category" holds localised text, so key.lower() built an Arabic path
			iconPath = IMG_DIR + "category_icons/" + category_data["icon"] + ".png"
			category_icon = ui.Button()
			category_icon.SetParent(categoryButton)
			category_icon.SetUpVisual(iconPath)
			category_icon.SetOverVisual(iconPath)
			category_icon.SetDownVisual(iconPath)
			category_icon.SetPosition(160, 0)
			category_icon.SAFE_SetEvent(self.ClickCategory, optionIndex)
			category_icon.Show()

			expand_icon = ui.Button()
			expand_icon.SetParent(categoryButton)
			expand_icon.SetUpVisual(IMG_DIR + "arrow_up.png")
			expand_icon.SetOverVisual(IMG_DIR + "arrow_up.png")
			expand_icon.SetDownVisual(IMG_DIR + "arrow_up.png")
			expand_icon.SetPosition(13, categoryButton.GetHeight() / 2 - expand_icon.GetHeight() / 2)
			expand_icon.SAFE_SetEvent(self.ClickCategory, optionIndex)
			expand_icon.Show()

			categoryButton.Show()
			self.children["titleBtn%d" % optionIndex] = categoryButton
			self.children["category_icon%d" % optionIndex] = category_icon
			self.children["expand_icon%d" % optionIndex] = expand_icon
			self.categoryButtons.append(categoryButton)

			self.children["is_expanded%d" % optionIndex] = False

			for categoryIndex, keyEx in enumerate(category_data["subcategories"]):
				subcategoryButton = ui.Button()
				subcategoryButton.SetParent(self.children["categoryScrollBoard"])
				subcategoryButton.SetUpVisual(IMG_DIR + "subcat_1.png")
				subcategoryButton.SetOverVisual(IMG_DIR + "subcat_2.png")
				subcategoryButton.SetDownVisual(IMG_DIR + "subcat_3.png")
				subcategoryButton.SetPosition(14, 10 + categoryButton.GetHeight() + (categoryIndex * (subcategoryButton.GetHeight())))
				subcategoryButton.SAFE_SetEvent(self.ClickSubcategory, optionIndex, categoryIndex)
				#subcategoryButton.SetTextAlignLeft(TEXT_MAIN_COLOR + keyEx, 13)
				subcategoryButton.SetText(keyEx)
				#subcategoryButton.SetTextColor(TEXT_MAIN_COLOR)
				subcategoryButton.Hide()
				self.children["subcategoryButton%d%d" % (optionIndex, categoryIndex)] = subcategoryButton

			# Create option window for this category (outside subcategory loop)
			optionWindow = self.CreateOptionWindow(bg, optionIndex)
			self.children["optionWindow%d" % (optionIndex)] = optionWindow

		self.ClickCategory(0)
		self.scrollBar2.SetPos(0)
		self.SetSize(bg.GetWidth() + 21, bg.GetHeight() + 44)
		self.SetCenterPosition()
		self.UpdateScrollBar()

	def ShowHideCancelSearchButton(self):
		if not self.searchEdit:
			return

		if self.searchEdit.GetText() == "":
			self.CancelSearchButton.Hide()
		else:
			self.CancelSearchButton.Show()

	def OnPressNameEscapeKey(self):
		if not self.searchEdit:
			return

		if not self.searchEdit.IsShowCursor() or self.searchEdit.GetText() == "":
			self.OnPressEscapeKey()
		else:
			self.searchEdit.SetText("")
			self.ShowHideCancelSearchButton()

	def __GetComponentText(self, component):
		"""Safely get text from a UI component"""
		if hasattr(component, 'GetText'):
			try:
				return component.GetText()
			except:
				pass
		return ""

	def __TextContains(self, text, searchText):
		"""Check if text contains searchText (case-insensitive for Latin, exact for Arabic)"""
		if not text or not searchText:
			return False
		try:
			# Try case-insensitive comparison
			return searchText.lower() in text.lower()
		except:
			# Fallback to exact match if lower() fails (encoding issues)
			return searchText in text

	def __SearchInComponent(self, component, searchText):
		"""Search for text in a component and its children"""
		# Check direct text
		compText = self.__GetComponentText(component)
		if compText and self.__TextContains(compText, searchText):
			return True

		# Check children for ALL component types (not just ExpandedImageBox)
		if hasattr(component, 'Children'):
			for child in component.Children:
				childText = self.__GetComponentText(child)
				if childText and self.__TextContains(childText, searchText):
					return True
				# Also check grandchildren (for text inside ExpandedImageBox)
				if hasattr(child, 'Children'):
					for grandchild in child.Children:
						grandchildText = self.__GetComponentText(grandchild)
						if grandchildText and self.__TextContains(grandchildText, searchText):
							return True

		return False

	def StartSearch(self):
		searchText = self.searchEdit.GetText()

		# If search text is empty, reset to normal view
		if not searchText or searchText.strip() == "":
			self.children["filteringEnabled"] = False
			if self.children.has_key("filterWindow"):
				self.children["filterWindow"].Hide()
			# Show first category by default
			if len(option_data) > 0:
				self.ClickCategory(0)
			return

		self.children["filteringEnabled"] = True

		# Hide all option windows first
		for categoryIndex in xrange(len(option_data)):
			if self.children.has_key("optionWindow%d" % categoryIndex):
				self.children["optionWindow%d" % categoryIndex].Hide()

		# Hide previous filter window if exists
		if self.children.has_key("filterWindow"):
			self.children["filterWindow"].Hide()

		scriptWindow = ui.ScriptWindow()
		scriptWindow.SetParent(self.children["bg"])
		pyScrLoader = ui.PythonScriptLoader()

		windowHeight = 0
		yPos = 5
		foundCount = 0
		loadSuccess = False

		# Try to load the filter file
		fileName = "UIScript/game_option_filter.py"
		try:
			pyScrLoader.LoadScriptFile(scriptWindow, fileName)
			loadSuccess = True
		except:
			loadSuccess = False

		if loadSuccess and hasattr(scriptWindow, 'Children'):
			scriptChildrens = scriptWindow.Children
			self.children["filteredWindow"] = scriptWindow

			for optionParent in scriptChildrens:
				found = False

				# Search through all children of this option window
				if hasattr(optionParent, 'Children'):
					for component in optionParent.Children:
						if self.__SearchInComponent(component, searchText):
							found = True
							break

				if not found:
					optionParent.Hide()
				else:
					optionParent.Show()
					# Preserve original x position (important for RTL Arabic mode)
					(_origX, _) = optionParent.GetLocalPosition()
					optionParent.SetPosition(_origX, yPos, True)  # True sets exPos
					yPos += optionParent.GetHeight()
					foundCount += 1

			windowHeight = yPos
			# Load all category options since filter contains elements from all categories
			for catIndex in xrange(len(option_data)):
				self.LoadCategoryOptions(scriptWindow, catIndex)
			self.children["filterWindow"] = scriptWindow
		else:
			# Fallback: search through existing category windows
			for categoryIndex in xrange(len(option_data)):
				if self.children.has_key("optionWindow%d" % categoryIndex):
					categoryWindow = self.children["optionWindow%d" % categoryIndex]
					if hasattr(categoryWindow, 'Children'):
						for optionParent in categoryWindow.Children:
							found = False
							if hasattr(optionParent, 'Children'):
								for component in optionParent.Children:
									if self.__SearchInComponent(component, searchText):
										found = True
										break
							if found:
								optionParent.Show()
								foundCount += 1
							else:
								optionParent.Hide()
						if foundCount > 0:
							categoryWindow.Show()
							self.children["filteredWindow"] = categoryWindow
							self.children["filterWindow"] = categoryWindow
							windowHeight = categoryWindow.GetHeight()
							break

		if foundCount > 0 and windowHeight > 0:
			self.children["filteredWindowHeight"] = windowHeight
			scrollBar = ScrollBarNew()
			scrollBar.SetParent(scriptWindow)
			scrollBar.SetPosition(0, 3)
			scrollBar.SetScrollBarSize(scriptWindow.GetHeight() - 6)
			scrollBar.Hide()
			scrollBar.SetScrollEvent(ui.__mem_func__(self.UpdateScrollBar))
			scriptWindow.scrollBar = scrollBar
			scriptWindow.OnRunMouseWheel = ui.__mem_func__(self.OnMouseWheel)

			# Only set exPos for visible children (matched search results)
			scriptChildrens = scriptWindow.Children
			for child in scriptChildrens:
				if child.IsShow():
					(_x, _y) = child.GetLocalPosition()
					child.SetPosition(_x, _y, True)

			# Set up clipping mask for all children to properly clip when scrolling
			if app.USE_CLIP_MASK:
				for child in scriptChildrens:
					if child.IsShow():
						if hasattr(child, 'SetClippingMaskWindow'):
							child.SetClippingMaskWindow(scriptWindow)
						self.__SetClippingMaskRecursive(child, scriptWindow)

			scriptWindow.Show()
		else:
			scriptWindow.scrollBar = None
			scriptWindow.Show()

		self.UpdateScrollBar()

	def Open(self):
		self.RefreshBlock()
		self.Show()

	def __CloseResolutionDropdown(self):
		if hasattr(self, "resolutionSelector") and self.resolutionSelector and self.resolutionSelector.isOpen:
			self.resolutionSelector.Close()
			return True
		return False

	def OnPressEscapeKey(self):
		if app.ENABLE_WINDOW_RESIZE and self.__CloseResolutionDropdown():
			return True
		self.Hide()
		return True

	if app.ENABLE_WINDOW_RESIZE:
		def OnMoveWindow(self, x, y):
			self.__CloseResolutionDropdown()
			ui.BoardWithTitleBar.OnMoveWindow(self, x, y)

		def Hide(self):
			self.__CloseResolutionDropdown()
			picker = getattr(self, "damageColorPicker", None)
			if picker:
				picker.Hide()
			ui.BoardWithTitleBar.Hide(self)

	def __ClickRadioButton(self, buttonList, buttonIndex):
		try:
			btn = buttonList[buttonIndex]
		except IndexError:
			return
		for eachButton in buttonList:
			eachButton.SetUp()
		btn.Down()

	def IsCanContinue(self, dictKey):
		if dictKey == "index":
			return True
		return False

	def GetTitleTextLines(self):
		title_text_lines = []
		scriptWindow = ui.ScriptWindow()
		scriptWindow.SetParent(self)
		title_text_lines_with_y = []
		for category_data in option_data:
			category_data["subcategories"] = []
		for categoryIndex, category_data in enumerate(option_data):
			fileName = "UIScript/game_option_%d.py" % (categoryIndex)

			pyScrLoader = ui.PythonScriptLoader()
			try:
				pyScrLoader.LoadScriptFile(scriptWindow, fileName)
				elementDictionary = scriptWindow.ElementDictionary
				for childName, child in elementDictionary.items():
					if childName.startswith("title_"):
						child_y = child.GetGlobalPosition()[1] - scriptWindow.GetGlobalPosition()[1]
						title_text_lines_with_y.append([categoryIndex, child.GetText(), child_y])
			except:
				pass

		title_text_lines_with_y.sort(key=lambda x: (x[0], x[2]))
		for child in title_text_lines_with_y:
			option_data[child[0]]["subcategories"].append(child[1])

	def ClickCategory(self, optionType):
		is_expanded = self.children["is_expanded%d" % optionType]
		self.children["is_expanded%d" % optionType] = not is_expanded
		is_expanded = not is_expanded

		for j in xrange(len(option_data)):
			if self.children.has_key("titleBtn%d" % j):
				categoryBtn = self.children["titleBtn%d" % j]
				expand_icon = self.children["expand_icon%d" % j]
				if j == optionType:
					if is_expanded:
						categoryBtn.SetUpVisual(IMG_DIR + "btn_cat_3.png")
						categoryBtn.SetOverVisual(IMG_DIR + "btn_cat_3.png")
						categoryBtn.SetDownVisual(IMG_DIR + "btn_cat_3.png")
						expand_icon.SetUpVisual(IMG_DIR + "arrow_down.png")
						expand_icon.SetOverVisual(IMG_DIR + "arrow_down.png")
						expand_icon.SetDownVisual(IMG_DIR + "arrow_down.png")

					else:
						categoryBtn.SetUpVisual(IMG_DIR + "btn_cat_1.png")
						categoryBtn.SetOverVisual(IMG_DIR + "btn_cat_2.png")
						categoryBtn.SetDownVisual(IMG_DIR + "btn_cat_3.png")
						expand_icon.SetUpVisual(IMG_DIR + "arrow_up.png")
						expand_icon.SetOverVisual(IMG_DIR + "arrow_up.png")
						expand_icon.SetDownVisual(IMG_DIR + "arrow_up.png")

		for j in xrange(10):
			if self.children.has_key("subcategoryButton%d%d" % (optionType, j)):
				subcategoryButton = self.children["subcategoryButton%d%d" % (optionType, j)]
				if is_expanded:
					subcategoryButton.Hide()
				else:
					subcategoryButton.Show()

		if is_expanded:
			self.ClickSubcategory(optionType, 0)
		self.RepositionCategoryButtons()
		self.OnScroll()

	def ClickSubcategory(self, optionType, categoryType):
		if self.children.has_key("filteringEnabled"):
			self.children["filteringEnabled"] = False
			if self.children.has_key("filterWindow"):
				self.children["filterWindow"].Hide()
		if self.children.has_key("optionType"):
			if self.children["optionType"] != optionType:
				self.scrollbar_is_show = False
		for j in xrange(len(option_data)):
			if self.children.has_key("optionWindow%d" % (j)):
				self.children["optionWindow%d" % (j)].Hide()

		for j in xrange(len(option_data)):
			for x in xrange(10):
				if self.children.has_key("subcategoryButton%d%d" % (j, x)):
					subcategoryBtn = self.children["subcategoryButton%d%d" % (j, x)]
					if j == optionType and x == categoryType:
						subcategoryBtn.SetUpVisual(IMG_DIR + "subcat_3.png")
						subcategoryBtn.SetOverVisual(IMG_DIR + "subcat_3.png")
						subcategoryBtn.SetDownVisual(IMG_DIR + "subcat_3.png")
						subcategoryBtn.Down()
					else:
						subcategoryBtn.SetUpVisual(IMG_DIR + "subcat_1.png")
						subcategoryBtn.SetOverVisual(IMG_DIR + "subcat_2.png")
						subcategoryBtn.SetDownVisual(IMG_DIR + "subcat_3.png")
						subcategoryBtn.SetUp()

		self.children["optionType"] = optionType
		self.children["categoryType"] = categoryType
		if self.children.has_key("optionWindow%d" % (optionType)):
			self.LoadCategoryOptions(self.children["optionWindow%d" % (optionType)], optionType)
			self.children["optionWindow%d" % (optionType)].Show()

		self.UpdateScrollBar()
		subcats = option_data[optionType]["subcategories"]
		if subcats and categoryType < len(subcats):
			self.GoToSubcategory(subcats[categoryType])

	def RepositionCategoryButtons(self):
		yPos = self.search_bg.GetHeight() + 10
		for i in xrange(len(option_data)):
			if self.children.has_key("titleBtn%d" % i):
				categoryButton = self.children["titleBtn%d" % i]
				categoryButton.SetPosition(14, yPos)
				yPos += categoryButton.GetHeight() + 5

				if self.children.has_key("is_expanded%d" % i):
					is_expanded = self.children["is_expanded%d" % i]
					if is_expanded:
						for j in xrange(10):
							if self.children.has_key("subcategoryButton%d%d" % (i, j)):
								subcategoryButton = self.children["subcategoryButton%d%d" % (i, j)]
								subcategoryButton.SetPosition(14, yPos - 5)
								subcategoryButton.Show()
								yPos += subcategoryButton.GetHeight()
							else:
								break
					else:
						for j in xrange(10):
							if self.children.has_key("subcategoryButton%d%d" % (i, j)):
								subcategoryButton = self.children["subcategoryButton%d%d" % (i, j)]
								subcategoryButton.Hide()

		totalHeight = yPos
		visibleHeight = self.children["bg"].GetHeight()
		if totalHeight > visibleHeight:
			self.scrollBar2.SetMiddleBarSize(float(visibleHeight) / float(totalHeight))
			self.scrollBar2.SetScrollStep(min(1.0, self.WHEEL_STEP_PIXELS / float(totalHeight - visibleHeight)))
			self.scrollBar2.Show()
			# SetPos re-runs the scroll event; OnMouseLeftButtonDown would too, but
			# it derives the new position from wherever the cursor happens to be
			self.scrollBar2.SetPos(self.scrollBar2.GetPos())
		else:
			self.scrollBar2.SetPos(0)
			self.OnScroll()
			self.scrollBar2.Hide()
		self.UpdateCategoryRenderingRect()

	def CalculateTotalHeight(self):
		yPos = self.search_bg.GetHeight() + 10
		for i in xrange(len(option_data)):
			if self.children.has_key("titleBtn%d" % i):
				categoryButton = self.children["titleBtn%d" % i]
				yPos += categoryButton.GetHeight() + 5

				if self.children.has_key("is_expanded%d" % i):
					is_expanded = self.children["is_expanded%d" % i]
					if is_expanded:
						for j in xrange(10):
							if self.children.has_key("subcategoryButton%d%d" % (i, j)):
								subcategoryButton = self.children["subcategoryButton%d%d" % (i, j)]
								yPos += subcategoryButton.GetHeight()
							else:
								break
		return yPos

	def OnScroll(self):
		pos = self.scrollBar2.GetPos()
		totalHeight = self.CalculateTotalHeight()
		visibleHeight = self.children["bg"].GetHeight()
		scrollHeight = totalHeight - visibleHeight

		yPos = self.search_bg.GetHeight() + 10 - int(pos * scrollHeight)
		for i in xrange(len(option_data)):
			if self.children.has_key("titleBtn%d" % i):
				categoryButton = self.children["titleBtn%d" % i]
				categoryButton.SetPosition(14, yPos)
				yPos += categoryButton.GetHeight() + 5

				if self.children.has_key("is_expanded%d" % i):
					is_expanded = self.children["is_expanded%d" % i]
					if is_expanded:
						for j in xrange(10):
							if self.children.has_key("subcategoryButton%d%d" % (i, j)):
								subcategoryButton = self.children["subcategoryButton%d%d" % (i, j)]
								subcategoryButton.SetPosition(14, yPos - 5)
								subcategoryButton.Show()
								yPos += subcategoryButton.GetHeight()
							else:
								break
					else:
						for j in xrange(10):
							if self.children.has_key("subcategoryButton%d%d" % (i, j)):
								subcategoryButton = self.children["subcategoryButton%d%d" % (i, j)]
								subcategoryButton.Hide()

		self.UpdateCategoryRenderingRect()

	def UpdateCategoryRenderingRect(self):
		visibleHeight = self.children["bg"].GetHeight() - 4 - (self.search_bg.GetHeight() + 10)
		for i in xrange(len(option_data)):
			if self.children.has_key("titleBtn%d" % i):
				categoryButton = self.children["titleBtn%d" % i]
				categoryButtonHeight = categoryButton.GetHeight()
				(categoryButtonX, categoryButtonY) = categoryButton.GetLocalPosition()
				categoryButtonY -= self.search_bg.GetHeight() + 10
				if categoryButtonY < 0:
					categoryButton.SetRenderingRect(0, ui.calculateRect(categoryButtonHeight - abs(categoryButtonY), categoryButtonHeight), 0, 0)
				elif categoryButtonY + categoryButtonHeight > visibleHeight:
					calculate = (visibleHeight - categoryButtonY) - categoryButtonHeight
					if calculate == 0:
						return
					f = ui.calculateRect(categoryButtonHeight - abs(calculate), categoryButtonHeight)
					categoryButton.SetRenderingRect(0, 0, 0, f)
				else:
					categoryButton.SetRenderingRect(0, 0, 0, 0)

				if categoryButtonY < -15 or categoryButtonY + categoryButtonHeight > visibleHeight + 13:
					categoryButton.ButtonText.Hide()
				else:
					categoryButton.ButtonText.Show()

				category_icon = self.children["category_icon%d" % i]
				category_iconHeight = category_icon.GetHeight()
				category_iconY = categoryButtonY + categoryButtonHeight / 2 - category_iconHeight / 2
				if category_iconY < 0:
					category_icon.SetRenderingRect(0, ui.calculateRect(category_iconHeight - abs(category_iconY), category_iconHeight), 0, 0)
				elif category_iconY + category_iconHeight > visibleHeight:
					calculate = (visibleHeight - category_iconY) - category_iconHeight
					if calculate == 0:
						return
					f = ui.calculateRect(category_iconHeight - abs(calculate), category_iconHeight)
					category_icon.SetRenderingRect(0, 0, 0, f)
				else:
					category_icon.SetRenderingRect(0, 0, 0, 0)

				expand_icon = self.children["expand_icon%d" % i]
				expand_iconHeight = expand_icon.GetHeight()
				expand_iconY = categoryButtonY + categoryButtonHeight / 2 - expand_iconHeight / 2
				if expand_iconY < 0:
					expand_icon.SetRenderingRect(0, ui.calculateRect(expand_iconHeight - abs(expand_iconY), expand_iconHeight), 0, 0)
				elif expand_iconY + expand_iconHeight > visibleHeight:
					calculate = (visibleHeight - expand_iconY) - expand_iconHeight
					if calculate == 0:
						return
					f = ui.calculateRect(expand_iconHeight - abs(calculate), expand_iconHeight)
					expand_icon.SetRenderingRect(0, 0, 0, f)
				else:
					expand_icon.SetRenderingRect(0, 0, 0, 0)

				if self.children.has_key("is_expanded%d" % i):
					is_expanded = self.children["is_expanded%d" % i]
					if is_expanded:
						for j in xrange(10):
							if self.children.has_key("subcategoryButton%d%d" % (i, j)):
								subcategoryButton = self.children["subcategoryButton%d%d" % (i, j)]
								subcategoryButtonHeight = subcategoryButton.GetHeight()
								(subcategoryButtonX, subcategoryButtonY) = subcategoryButton.GetLocalPosition()
								subcategoryButtonY -= self.search_bg.GetHeight() + 10
								if subcategoryButtonY < 0:
									subcategoryButton.SetRenderingRect(0, ui.calculateRect(subcategoryButtonHeight - abs(subcategoryButtonY), subcategoryButtonHeight), 0, 0)
								elif subcategoryButtonY + subcategoryButtonHeight > visibleHeight:
									calculate = (visibleHeight - subcategoryButtonY) - subcategoryButtonHeight
									if calculate == 0:
										return
									f = ui.calculateRect(subcategoryButtonHeight - abs(calculate), subcategoryButtonHeight)
									subcategoryButton.SetRenderingRect(0, 0, 0, f)
								else:
									subcategoryButton.SetRenderingRect(0, 0, 0, 0)

								if subcategoryButtonY < -10 or subcategoryButtonY + subcategoryButtonHeight > visibleHeight + 8:
									subcategoryButton.ButtonText.Hide()
								else:
									subcategoryButton.ButtonText.Show()

	# Hover marquee. Two things keep this cheap: the hit-test (which must walk every
	# label) runs on its own slow interval, and the visible window only re-measures on
	# the ticks where the character index actually advances -- not every frame.
	MARQUEE_LIMIT_PX = 250
	MARQUEE_SPEED_PX = 100.0
	MARQUEE_HIT_INTERVAL = 0.1

	def __MarqueeInfo(self, item):
		info = self.marquee.get(item)
		if info is not None:
			return info
		full = item.GetText()
		if not full:
			return None
		w, h = item.GetTextSize()
		info = {"full" : full, "short" : full, "fullW" : w, "h" : h, "over" : w > self.MARQUEE_LIMIT_PX}
		if info["over"]:
			cut = full
			while cut and item.GetTextSize()[0] > self.MARQUEE_LIMIT_PX - 10:
				cut = cut[:-1]
				item.SetText(cut)
			info["short"] = cut + ".."
			item.SetText(info["short"])
		self.marquee[item] = info
		return info

	def __MarqueeMask(self, item, info, offset):
		# the label itself is what moves, so the box it must stay inside is derived by
		# undoing the current offset -- that keeps the clip correct while the list scrolls;
		# RTL labels are align-right windows (screen x = parentRight - localX), so lowering
		# localX slides them right and the offset is undone with the opposite sign
		gx, gy = item.GetGlobalPosition()
		if localeinfo.IsARABIC():
			base = gx - offset
			item.SetClippingMaskRect(int(base - self.MARQUEE_LIMIT_PX), int(gy), int(base + 20), int(gy + info["h"]))
		else:
			base = gx + offset
			item.SetClippingMaskRect(int(base), int(gy), int(base + self.MARQUEE_LIMIT_PX), int(gy + info["h"]))

	def __MarqueeRest(self):
		item = self.marqueeHot
		offset = self.marqueeOffset
		self.marqueeHot = None
		self.marqueeOffset = 0.0
		self.marqueeDone = False
		if not item:
			return
		info = self.marquee.get(item)
		if not info:
			return
		if "baseX" in info:
			item.SetPosition(info["baseX"], item.GetLocalPosition()[1])
		item.SetText(info["short"])
		# the mask cannot be switched off, so widen it past anything it could clip
		item.SetClippingMaskRect(0, 0, wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())

	def __MarqueeHitTest(self):
		window = self.GetCurrentWindow()
		if window is None:
			return None
		xMouse, yMouse = wndMgr.GetMousePosition()
		rtl = localeinfo.IsARABIC()
		for childName, child in window.ElementDictionary.items():
			if not isinstance(child, ui.TextLine):
				continue
			info = self.__MarqueeInfo(child)
			if not info or not info["over"]:
				continue
			x, y = child.GetGlobalPosition()
			# TextLine never calls SetSize, so GetHeight() is 0 -- the glyph height is the only real one
			h = info["h"]
			w = self.MARQUEE_LIMIT_PX
			if rtl:
				inside = (xMouse >= x - w and xMouse < x + 20 and yMouse >= y and yMouse < y + h)
			else:
				inside = (xMouse >= x and xMouse < x + w and yMouse >= y and yMouse < y + h)
			if inside:
				return child
		return None

	def OnUpdate(self):
		current_time = time.time()
		dt = current_time - self.last_update_time
		if dt <= 0.0:
			return
		self.last_update_time = current_time

		if current_time - self.marqueeHitTime >= self.MARQUEE_HIT_INTERVAL:
			self.marqueeHitTime = current_time
			hot = self.__MarqueeHitTest()
			if hot is not self.marqueeHot:
				self.__MarqueeRest()
				if hot:
					self.marqueeHot = hot
					self.marqueeHotSince = current_time

		item = self.marqueeHot
		if not item:
			return
		info = self.marquee.get(item)
		if not info or not info["over"]:
			return
		if current_time - self.marqueeHotSince < self.animation_delay:
			return

		if item.GetText() != info["full"]:
			info["baseX"] = item.GetLocalPosition()[0]
			item.SetText(info["full"])
			self.marqueeOffset = 0.0
			self.__MarqueeMask(item, info, 0.0)
			return

		travel = info["fullW"] - self.MARQUEE_LIMIT_PX
		if travel <= 0:
			return
		if not self.marqueeDone:
			self.marqueeOffset += self.MARQUEE_SPEED_PX * dt
			if self.marqueeOffset >= travel:
				self.marqueeOffset = float(travel)
				self.marqueeDone = True
			baseX = info.get("baseX", item.GetLocalPosition()[0])
			y = item.GetLocalPosition()[1]
			item.SetPosition(int(baseX - self.marqueeOffset), y)
		self.__MarqueeMask(item, info, self.marqueeOffset)

	def __SetClippingMaskRecursive(self, window, maskWindow):
		"""Recursively set clipping mask on all children"""
		if not hasattr(window, 'Children'):
			return
		for child in window.Children:
			if hasattr(child, 'SetClippingMaskWindow'):
				child.SetClippingMaskWindow(maskWindow)
			self.__SetClippingMaskRecursive(child, maskWindow)

	def CreateOptionWindow(self, windowBG, optionIndex):
		scriptWindow = ui.ScriptWindow()
		scriptWindow.SetParent(windowBG)
		try:
			fileName = "UIScript/game_option_%d.py" % (optionIndex)
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(scriptWindow, fileName)
			self.LoadCategoryOptions(scriptWindow, optionIndex)
		except Exception, msg:
			dbg.TraceError("AdvancedGameOptions.LoadScript - %s" % (msg))
		if scriptWindow.GetWidth() > 0:

			scrollBar = ScrollBarNew()
			scrollBar.SetParent(scriptWindow)
			scrollBar.SetPosition(0, 3)
			scrollBar.SetScrollBarSize(scriptWindow.GetHeight() - 6)
			scrollBar.Hide()
			scrollBar.SetScrollEvent(ui.__mem_func__(self.UpdateScrollBar))
			scriptWindow.scrollBar = scrollBar
			scriptWindow.OnRunMouseWheel = ui.__mem_func__(self.OnMouseWheel)

			scriptChildrens = scriptWindow.Children
			for child in scriptChildrens:
				(_x, _y) = child.GetLocalPosition()
				child.SetPosition(_x, _y, True)

			# Set up clipping mask for all children to properly clip when scrolling
			if app.USE_CLIP_MASK:
				for child in scriptChildrens:
					if hasattr(child, 'SetClippingMaskWindow'):
						child.SetClippingMaskWindow(scriptWindow)
					self.__SetClippingMaskRecursive(child, scriptWindow)

			scriptWindow.Show()
		else:
			scriptWindow.scrollBar = None

		return scriptWindow

	def __ClickResolution(self, index):
		sel = self.resolutionSelector
		if sel is None or index < 0 or index >= len(sel.resList):
			return
		(rw, rh) = sel.resList[index]
		app.SetWindowSize(rw, rh)

	# the advanced sliderbar draws its own "NN%"; rows that already own a value
	# label (degrees, 0.50, 1.00) must suppress it or two readouts overlap
	def __HideSliderPercentage(self, slider):
		if hasattr(slider, "percentage"):
			slider.percentage.Hide()

	def LoadCategoryOptions(self, scriptWindow, optionIndex):
		try:
			GetObject = scriptWindow.GetChild

			# Category 0: Interface
			if optionIndex == 0 or self.children["filteringEnabled"]:
				if app.ENABLE_WINDOW_RESIZE:
					try:
						resWindow = GetObject("resolution_window")
						if self.resolutionSelector is None:
							resList = []
							resSeen = {}
							for i in xrange(systemSetting.GetResolutionCount()):
								(rw, rh, rbpp) = systemSetting.GetResolution(i)
								if (rw, rh) in resSeen:
									continue
								resSeen[(rw, rh)] = 1
								resList.append((rw, rh))

							(cw, ch, cbpp) = systemSetting.GetCurrentResolution()
							self.resolutionSelector = ResolutionSelector(self, resWindow, 56, 38)
							self.resolutionSelector.SetResolutions(resList, cw, ch)
							self.resolutionSelector.SetSelectEvent(ui.__mem_func__(self.__ClickResolution))
					except Exception, e:
						dbg.TraceError("ResolutionSelector init failed: %s" % e)
				# View Chat - New Toggle Style
				try:
					self.viewChatToggle = GetObject("view_chat_toggle")
					self.viewChatToggle.SetToggleUpEvent(self.__OnClickViewChatToggle)
					self.viewChatToggle.SetToggleDownEvent(self.__OnClickViewChatToggle)
					self.RefreshViewChatToggle()
				except:
					# Fallback for old style (filter window may still use old style)
					self.viewChatButtonList = []
					self.viewChatButtonList.append(GetObject("view_chat_on_button"))
					self.viewChatButtonList[0].SAFE_SetEvent(self.__OnClickViewChat)
					self.viewChatButtonList.append(GetObject("view_chat_off_button"))
					self.viewChatButtonList[1].SAFE_SetEvent(self.__OnClickViewChat)
					self.RefreshViewChat()

				if app.ENABLE_AUTO_SHOUT_V2:
					try:
						self.showAutoShoutToggle = GetObject("show_auto_shout_toggle")
						self.showAutoShoutToggle.SetToggleUpEvent(self.__OnClickShowAutoShoutToggle)
						self.showAutoShoutToggle.SetToggleDownEvent(self.__OnClickShowAutoShoutToggle)
						self.RefreshShowAutoShoutToggle()
					except:
						self.showAutoShoutToggle = None

				# Name Visibility Toggle Buttons
				self.hideNamesToggle = GetObject("hide_names_toggle")
				self.hideNamesToggle.SetToggleUpEvent(self.__OnClickHideNamesToggle)
				self.hideNamesToggle.SetToggleDownEvent(self.__OnClickHideNamesToggle)
				self.RefreshHideNamesToggle()

				self.hideShopsToggle = GetObject("hide_shops_toggle")
				self.hideShopsToggle.SetToggleUpEvent(self.__OnClickHideShopsToggle)
				self.hideShopsToggle.SetToggleDownEvent(self.__OnClickHideShopsToggle)
				self.RefreshHideShopsToggle()

				self.hideNpcToggle = GetObject("hide_npc_toggle")
				self.hideNpcToggle.SetToggleUpEvent(self.__OnClickHideNpcToggle)
				self.hideNpcToggle.SetToggleDownEvent(self.__OnClickHideNpcToggle)
				self.RefreshHideNpcToggle()

				self.outlineNameToggle = GetObject("outline_name_toggle")
				self.outlineNameToggle.SetToggleUpEvent(self.__OnClickOutlineNameToggle)
				self.outlineNameToggle.SetToggleDownEvent(self.__OnClickOutlineNameToggle)
				self.RefreshOutlineNameToggle()


				self.hideDamageAllToggle = GetObject("hide_damage_all_toggle")
				self.hideDamageAllToggle.SetToggleUpEvent(self.__OnClickHideDamageAllToggle)
				self.hideDamageAllToggle.SetToggleDownEvent(self.__OnClickHideDamageAllToggle)
				self.RefreshHideDamageAllToggle()

				self.hideDamageMobsToggle = GetObject("hide_damage_mobs_toggle")
				self.hideDamageMobsToggle.SetToggleUpEvent(self.__OnClickHideDamageMobsToggle)
				self.hideDamageMobsToggle.SetToggleDownEvent(self.__OnClickHideDamageMobsToggle)
				self.RefreshHideDamageMobsToggle()

				if app.__SCALE_EFFECT_DAMAGE__:
					try:
						self.changeScaleEffDamage = GetObject("scaleEff_Slider")
						self.changeScaleEffDamage.SetSliderPos(float(systemSetting.GetScaleEffDamageLevel()) / 5.0)
						self.changeScaleEffDamage.SetEvent(ui.__mem_func__(self.OnChangeScaleEffDamage))
					except:
						pass

				if app.ENABLE_DAMAGE_COLOR_CUSTOM:
					try:
						self.damageColorSwatches = []
						for i in xrange(3):
							slotWin = GetObject("damage_color_slot_%d" % i)
							swatch = uidamagecolorpicker.ColorSwatch()
							swatch.SetParent(slotWin)
							swatch.SetPosition(0, 0)
							swatch.SetSize(60, 18)
							swatch.SetClickEvent(ui.__mem_func__(self.__OnClickDamageColorSwatch), i)
							swatch.Show()
							self.damageColorSwatches.append(swatch)
						self.RefreshDamageColorSwatches()
					except:
						self.damageColorSwatches = []

				if app.ENABLE_AUTO_HUNT_EFFECT_COLOR:
					try:
						slotWin = GetObject("auto_hunt_color_slot")
						swatch = uidamagecolorpicker.ColorSwatch()
						swatch.SetParent(slotWin)
						swatch.SetPosition(0, 0)
						swatch.SetSize(60, 18)
						swatch.SetClickEvent(ui.__mem_func__(self.__OnClickAutoHuntColorSwatch))
						swatch.Show()
						self.autoHuntColorSwatch = swatch
						self.RefreshAutoHuntColorSwatch()
					except:
						self.autoHuntColorSwatch = None

				self.viewTargetBoardButtonList = []
				self.viewTargetBoardButtonList.append(GetObject("target_board_view"))
				self.viewTargetBoardButtonList[0].SAFE_SetEvent(self.__SetTargetBoardViewMode)
				self.viewTargetBoardButtonList.append(GetObject("target_board_no_view"))
				self.viewTargetBoardButtonList[1].SAFE_SetEvent(self.__SetTargetBoardViewMode)
				self.RefreshTargetBoard()

				self.nameColorModeButtonList = []
				self.nameColorModeButtonList.append(GetObject("name_color_normal"))
				self.nameColorModeButtonList[0].SAFE_SetEvent(self.__OnClickNameColorMode)
				self.nameColorModeButtonList.append(GetObject("name_color_empire"))
				self.nameColorModeButtonList[1].SAFE_SetEvent(self.__OnClickNameColorMode)
				self.RefreshNameColor()

			# Category 1: Game
			if optionIndex == 1 or self.children["filteringEnabled"]:
				self.pvpModeButtonDict = {}
				self.pvpModeButtonDict[player.PK_MODE_PEACE] = GetObject("pvp_peace")
				self.pvpModeButtonDict[player.PK_MODE_PEACE].SAFE_SetEvent(self.__OnClickPvPModePeaceButton)
				self.pvpModeButtonDict[player.PK_MODE_REVENGE] = GetObject("pvp_revenge")
				self.pvpModeButtonDict[player.PK_MODE_REVENGE].SAFE_SetEvent(self.__OnClickPvPModeRevengeButton)
				self.pvpModeButtonDict[player.PK_MODE_GUILD] = GetObject("pvp_guild")
				self.pvpModeButtonDict[player.PK_MODE_GUILD].SAFE_SetEvent(self.__OnClickPvPModeGuildButton)
				self.pvpModeButtonDict[player.PK_MODE_FREE] = GetObject("pvp_free")
				self.pvpModeButtonDict[player.PK_MODE_FREE].SAFE_SetEvent(self.__OnClickPvPModeFreeButton)
				self.__SetPeacePKMode()

				self.blockButtonList = []
				block_exchange_button = GetObject("block_exchange_button")
				block_exchange_button.SetToggleUpEvent(self.__OnClickBlockExchangeButton)
				block_exchange_button.SetToggleDownEvent(self.__OnClickBlockExchangeButton)
				self.blockButtonList.append(block_exchange_button)

				block_party_button = GetObject("block_party_button")
				block_party_button.SetToggleUpEvent(self.__OnClickBlockPartyButton)
				block_party_button.SetToggleDownEvent(self.__OnClickBlockPartyButton)
				self.blockButtonList.append(block_party_button)

				block_guild_button = GetObject("block_guild_button")
				block_guild_button.SetToggleUpEvent(self.__OnClickBlockGuildButton)
				block_guild_button.SetToggleDownEvent(self.__OnClickBlockGuildButton)
				self.blockButtonList.append(block_guild_button)

				block_whisper_button = GetObject("block_whisper_button")
				block_whisper_button.SetToggleUpEvent(self.__OnClickBlockWhisperButton)
				block_whisper_button.SetToggleDownEvent(self.__OnClickBlockWhisperButton)
				self.blockButtonList.append(block_whisper_button)

				block_friend_button = GetObject("block_friend_button")
				block_friend_button.SetToggleUpEvent(self.__OnClickBlockFriendButton)
				block_friend_button.SetToggleDownEvent(self.__OnClickBlockFriendButton)
				self.blockButtonList.append(block_friend_button)

				block_party_request_button = GetObject("block_party_request_button")
				block_party_request_button.SetToggleUpEvent(self.__OnClickBlockPartyRequest)
				block_party_request_button.SetToggleDownEvent(self.__OnClickBlockPartyRequest)
				self.blockButtonList.append(block_party_request_button)
				self.RefreshBlock()

				if app.ENABLE_EXTENDED_PICKUP:
					self.pickupIgnoreButtonList = []
					for type in ["weapon", "armor", "head", "shield", "wrist", "foots", "neck", "ear"]:
						self.pickupIgnoreButtonList.append(GetObject("drops_ignore_" + type))

					for i in xrange(len(self.pickupIgnoreButtonList)):
						self.pickupIgnoreButtonList[i].SetToggleUpEvent(lambda arg=i: self.__OnClickPickupIgnoreButton(arg, False))
						self.pickupIgnoreButtonList[i].SetToggleDownEvent(lambda arg=i: self.__OnClickPickupIgnoreButton(arg, True))

					self.__RefreshPickupIgnoreButtons()

				#to be weather
				self.nightModeToggle = GetObject("night_mode_toggle")
				self.nightModeToggle.SetToggleUpEvent(self.__OnClickNightModeToggle)
				self.nightModeToggle.SetToggleDownEvent(self.__OnClickNightModeToggle)
				self.RefreshNightModeToggle()

				# Weather Selection Buttons
				self.showNightButtonList = []
				for i in [1, 2, 3, 4, 5, 6, 7, 8, 10]:  # Note: no 9
					btn = GetObject("showNight_%d_button" % i)
					btn.SAFE_SetEvent(self.__OnClickWeatherButton, i)
					self.showNightButtonList.append(btn)
				self.RefreshWeatherButtons()

				# Save Environment Toggle
				self.saveEnvToggle = GetObject("save_env_toggle")
				self.saveEnvToggle.SetToggleUpEvent(self.__OnClickSaveEnvToggle)
				self.saveEnvToggle.SetToggleDownEvent(self.__OnClickSaveEnvToggle)
				self.RefreshSaveEnvToggle()

				# Load saved weather on window open (if enabled)
				self.LoadSavedWeather()

				self.tilingModeButtonList = []
				self.tilingModeButtonList.append(GetObject("tiling_cpu"))
				self.tilingModeButtonList.append(GetObject("tiling_gpu"))
				self.tilingModeButtonList[0].SAFE_SetEvent(self.__OnClickTilingModeCPUButton)
				self.tilingModeButtonList[1].SAFE_SetEvent(self.__OnClickTilingModeGPUButton)
				self.tilingApplyButton = GetObject("tiling_apply")
				self.tilingApplyButton.SAFE_SetEvent(self.__OnClickTilingApplyButton)
				self.__SetCurTilingMode()



				if app.ENABLE_KEYCHANGE_SYSTEM:
					try:
						self.keyboardButton = GetObject("keyboard_settings_button")
						self.keyboardButton.SetEvent(ui.__mem_func__(self.OpenKeyChangeWindow))
					except:
						pass

			# Category 2: Graphics
			if optionIndex == 2 or self.children["filteringEnabled"]:
				# self.cameraModeButtonList = []
				# self.cameraModeButtonList.append(GetObject("camera_level0"))
				# self.cameraModeButtonList[0].SAFE_SetEvent(self.__OnClickCameraMode, 0)
				# self.cameraModeButtonList.append(GetObject("camera_level1"))
				# self.cameraModeButtonList[1].SAFE_SetEvent(self.__OnClickCameraMode, 1)
				# self.RefreshCameraMode()

				if app.ENABLE_FOV_OPTION:
					try:
						self.fovController = GetObject("fov_controller")
						self.fovValueText = GetObject("fov_value_text")
						self.fovResetButton = GetObject("fov_reset_button")

						# Normalize: (current - min) / (max - min)
						fovMin = float(systemSetting.MIN_CAMERA_PERSPECTIVE)
						fovMax = float(systemSetting.MAX_CAMERA_PERSPECTIVE)
						fovNormalized = (float(systemSetting.GetFOV()) - fovMin) / (fovMax - fovMin)

						self.fovController.SetSliderPos(fovNormalized)
						self.fovController.SetEvent(ui.__mem_func__(self.__OnChangeFOV))
						self.__HideSliderPercentage(self.fovController)

						self.fovValueText.SetText(str(int(systemSetting.GetFOV())) + chr(176))
						self.fovResetButton.SetEvent(ui.__mem_func__(self.__OnClickFOVResetButton))
					except:
						pass

				if app.USE_METIN_STONE_SCALE:
					try:
						self.metinstoneSize = GetObject("stonesize_controller")
						self.metinstoneSize.SetSliderPos(float(systemSetting.GetMetinStoneSize()))
						self.metinstoneSize.SetEvent(ui.__mem_func__(self.OnChangeMetinStoneSize))
					except:
						pass


				if app.USE_IMPROVEMENTS:
					try:
						self.effectController = GetObject("effect_controller")
						self.effectController.SetSliderPos(float(systemSetting.GetEffectRenderRange()))
						self.effectController.SetEvent(ui.__mem_func__(self.__OnChangeEffectDistance))
					except:
						pass

				if app.ENABLE_GRAPHIC_ON_OFF:
					try:
						# Effect visibility toggles
						self.hideBuffToggle = GetObject("hide_buff_toggle")
						self.hideBuffToggle.SetToggleUpEvent(self.__OnToggleHideBuffEffects)
						self.hideBuffToggle.SetToggleDownEvent(self.__OnToggleHideBuffEffects)

						self.hideSkillToggle = GetObject("hide_skill_toggle")
						self.hideSkillToggle.SetToggleUpEvent(self.__OnToggleHideSkillEffects)
						self.hideSkillToggle.SetToggleDownEvent(self.__OnToggleHideSkillEffects)

						self.hideGeneralToggle = GetObject("hide_general_toggle")
						self.hideGeneralToggle.SetToggleUpEvent(self.__OnToggleHideGeneralEffects)
						self.hideGeneralToggle.SetToggleDownEvent(self.__OnToggleHideGeneralEffects)

						self.hideMonsterToggle = GetObject("hide_monster_toggle")
						self.hideMonsterToggle.SetToggleUpEvent(self.__OnToggleHideMonsterEffects)
						self.hideMonsterToggle.SetToggleDownEvent(self.__OnToggleHideMonsterEffects)

						# self.hideProjectilesToggle = GetObject("hide_projectiles_toggle")
						# self.hideProjectilesToggle.SetToggleUpEvent(self.__OnToggleHideProjectiles)
						# self.hideProjectilesToggle.SetToggleDownEvent(self.__OnToggleHideProjectiles)

						self.bossEffectToggle = GetObject("boss_effect_toggle")
						self.bossEffectToggle.SetToggleUpEvent(self.__OnToggleBossEffect)
						self.bossEffectToggle.SetToggleDownEvent(self.__OnToggleBossEffect)

						self.RefreshEffectVisibilityToggles()

						self.petStatusButtonList = []
						self.petStatusButtonList.append(GetObject("pet_off"))
						self.petStatusButtonList.append(GetObject("pet_on"))
						self.petStatusButtonList[0].SAFE_SetEvent(self.__OnClickPetStatusButton, 1)
						self.petStatusButtonList[1].SAFE_SetEvent(self.__OnClickPetStatusButton, 0)
						self.RefreshPetStatus()

						self.MountStatusButtonList = []
						self.MountStatusButtonList.append(GetObject("mount_off"))
						self.MountStatusButtonList.append(GetObject("mount_on"))
						self.MountStatusButtonList[0].SAFE_SetEvent(self.__OnClickMountStatusButton, 1)
						self.MountStatusButtonList[1].SAFE_SetEvent(self.__OnClickMountStatusButton, 0)
						self.RefreshMountStatus()

					except:
						pass

				if app.USE_OFFLINESHOP_VIEW_RANGE:
					try:
						self.privateshop_range_controller = GetObject("privateshop_range_controller_ui")
						self.privateshop_range_controller.SetSliderPos(float(systemSetting.GetPrivateShopViewRange()))
						self.privateshop_range_controller.SetEvent(ui.__mem_func__(self.__SetPrivateShopViewRange))
					except:
						pass

				if app.WJ_SHOW_MOB_INFO:
					try:
						self.showMobInfoButtonList = []
						self.showMobInfoButtonList.append(GetObject("show_mob_level_button"))
						self.showMobInfoButtonList.append(GetObject("show_mob_AI_flag_button"))
						self.showMobInfoButtonList[0].SetToggleUpEvent(self.__OnClickShowMobLevelButton)
						self.showMobInfoButtonList[0].SetToggleDownEvent(self.__OnClickShowMobLevelButton)
						self.showMobInfoButtonList[1].SetToggleUpEvent(self.__OnClickShowMobAIFlagButton)
						self.showMobInfoButtonList[1].SetToggleDownEvent(self.__OnClickShowMobAIFlagButton)
						self.RefreshShowMobInfo()
					except:
						pass

				if app.ENABLE_FPS:
					try:
						self.fpsButtonList = []
						for i in xrange(5):
							self.fpsButtonList.append(GetObject("fps_mode%d" % i))
							self.fpsButtonList[i].SAFE_SetEvent(self.__OnClickFPSButton, i)
						self.RefreshFPS()
					except:
						pass

				if app.USE_BACKGROUND_FPS_CAP:
					try:
						self.backgroundFpsToggle = GetObject("background_fps_toggle")
						self.backgroundFpsToggle.SetToggleUpEvent(self.__OnToggleBackgroundFps, 0)
						self.backgroundFpsToggle.SetToggleDownEvent(self.__OnToggleBackgroundFps, 1)
						self.RefreshBackgroundFps()
					except:
						pass

				if app.ENABLE_POST_PROCESSING:
					try:
						self.ppToggle = GetObject("pp_toggle")
						self.ppToggle.SetToggleUpEvent(self.__OnClickPostProcessToggle)
						self.ppToggle.SetToggleDownEvent(self.__OnClickPostProcessToggle)

						self.ppQualityButtonList = []
						self.ppQualityButtonList.append(GetObject("pp_quality_low"))
						self.ppQualityButtonList[0].SAFE_SetEvent(self.__OnClickPostProcessQuality, app.PP_QUALITY_LOW)
						self.ppQualityButtonList.append(GetObject("pp_quality_medium"))
						self.ppQualityButtonList[1].SAFE_SetEvent(self.__OnClickPostProcessQuality, app.PP_QUALITY_MEDIUM)
						self.ppQualityButtonList.append(GetObject("pp_quality_high"))
						self.ppQualityButtonList[2].SAFE_SetEvent(self.__OnClickPostProcessQuality, app.PP_QUALITY_HIGH)
						self.ppQualityButtonList.append(GetObject("pp_quality_ultra"))
						self.ppQualityButtonList[3].SAFE_SetEvent(self.__OnClickPostProcessQuality, app.PP_QUALITY_ULTRA)

						self.ppVignetteLabel = GetObject("pp_vignette_label")
						self.ppVignetteToggle = GetObject("pp_vignette_toggle")
						self.ppVignetteToggle.SetToggleUpEvent(self.__OnClickPPVignette, 0)
						self.ppVignetteToggle.SetToggleDownEvent(self.__OnClickPPVignette, 1)

						self.ppSharpenLabel = GetObject("pp_sharpen_label")
						self.ppSharpenSlider = GetObject("pp_sharpen_slider")
						self.ppSharpenValueText = GetObject("pp_sharpen_value")
						self.ppSharpenSlider.SetEvent(ui.__mem_func__(self.__OnChangePPSharpen))
						self.__HideSliderPercentage(self.ppSharpenSlider)

						self.ppColorGradeLabel = GetObject("pp_colorgrade_label")
						self.ppLUTButtonList = []
						self.ppLUTButtonList.append(GetObject("pp_lut_none"))
						self.ppLUTButtonList[0].SAFE_SetEvent(self.__OnClickPPLUT, app.PP_LUT_NONE)
						self.ppLUTButtonList.append(GetObject("pp_lut_cinematic"))
						self.ppLUTButtonList[1].SAFE_SetEvent(self.__OnClickPPLUT, app.PP_LUT_CINEMATIC)
						self.ppLUTButtonList.append(GetObject("pp_lut_fantasy"))
						self.ppLUTButtonList[2].SAFE_SetEvent(self.__OnClickPPLUT, app.PP_LUT_FANTASY)

						self.ppLUTStrengthLabel = GetObject("pp_lut_strength_label")
						self.ppLUTStrengthSlider = GetObject("pp_lut_strength_slider")
						self.ppLUTStrengthValueText = GetObject("pp_lut_strength_value")
						self.ppLUTStrengthSlider.SetEvent(ui.__mem_func__(self.__OnChangePPLUTStrength))
						self.__HideSliderPercentage(self.ppLUTStrengthSlider)

						self.LoadPostProcessConfig()
					except:
						pass

			# Category 3: Environment
			if optionIndex == 3 or self.children["filteringEnabled"]:
				if app.ENABLE_FOG_FIX:
					try:
						self.fogButtonList = []
						self.fogButtonList.append(GetObject("fog_off"))
						self.fogButtonList.append(GetObject("fog_on"))
						self.fogButtonList[0].SAFE_SetEvent(self.__OnClickFogModeOffButton)
						self.fogButtonList[1].SAFE_SetEvent(self.__OnClickFogModeOnButton)
						self.RefreshFogMode()
					except:
						pass

				if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
					try:

						self.snowModeButtonList = []
						self.snowModeButtonList.append(GetObject("snow_mode_off"))
						self.snowModeButtonList.append(GetObject("snow_mode_on"))
						self.snowModeButtonList[0].SAFE_SetEvent(self.__OnClickSnowModeOffButton)
						self.snowModeButtonList[1].SAFE_SetEvent(self.__OnClickSnowModeOnButton)
						self.RefreshSnowMode()

						self.snowTextureModeButtonList = []
						self.snowTextureModeButtonList.append(GetObject("snowtexture_mode_off"))
						self.snowTextureModeButtonList.append(GetObject("snowtexture_mode_on"))
						self.snowTextureModeButtonList[0].SAFE_SetEvent(self.__OnClickSnowTextureModeOffButton)
						self.snowTextureModeButtonList[1].SAFE_SetEvent(self.__OnClickSnowTextureModeOnButton)
						self.RefreshSnowTextureMode()
					except:
						pass

				if app.ENABLE_SHADOW_RENDER_QUALITY_OPTION:
					try:
						self.shadowTargetButtonList = []
						self.shadowTargetButtonList.append(GetObject("shadow_target_none"))
						self.shadowTargetButtonList[0].SAFE_SetEvent(self.__OnClickChangeShadowTarget, 0)
						self.shadowTargetButtonList.append(GetObject("shadow_target_ground"))
						self.shadowTargetButtonList[1].SAFE_SetEvent(self.__OnClickChangeShadowTarget, 1)
						self.shadowTargetButtonList.append(GetObject("shadow_target_ground_and_solo"))
						self.shadowTargetButtonList[2].SAFE_SetEvent(self.__OnClickChangeShadowTarget, 2)
						self.shadowTargetButtonList.append(GetObject("shadow_target_all"))
						self.shadowTargetButtonList[3].SAFE_SetEvent(self.__OnClickChangeShadowTarget, 3)
						self.__ClickRadioButton(self.shadowTargetButtonList, systemSetting.GetShadowTargetLevel())

						self.shadowQualityButtonList = []
						self.shadowQualityButtonList.append(GetObject("shadow_quality_bad"))
						self.shadowQualityButtonList[0].SAFE_SetEvent(self.__OnClickChangeShadowQuality, 0)
						self.shadowQualityButtonList.append(GetObject("shadow_quality_average"))
						self.shadowQualityButtonList[1].SAFE_SetEvent(self.__OnClickChangeShadowQuality, 1)
						self.shadowQualityButtonList.append(GetObject("shadow_quality_good"))
						self.shadowQualityButtonList[2].SAFE_SetEvent(self.__OnClickChangeShadowQuality, 2)
						self.__ClickRadioButton(self.shadowQualityButtonList, systemSetting.GetShadowQualityLevel())
					except:
						pass
				else:
					try:
						self.ctrlShadowQuality = GetObject("shadow_bar")
						self.ctrlShadowQuality.SetSliderPos(float(systemSetting.GetShadowLevel()) / 5.0)
						self.ctrlShadowQuality.SetEvent(ui.__mem_func__(self.OnChangeShadowQuality))
					except:
						pass

				# Tree Shadow toggle
				try:
					self.treeShadowButtonList = []
					self.treeShadowButtonList.append(GetObject("tree_shadow_on"))
					self.treeShadowButtonList[0].SAFE_SetEvent(self.__OnClickTreeShadow, 1)
					self.treeShadowButtonList.append(GetObject("tree_shadow_off"))
					self.treeShadowButtonList[1].SAFE_SetEvent(self.__OnClickTreeShadow, 0)
					if hasattr(systemSetting, "GetTreeShadow"):
						treeShadowEnabled = systemSetting.GetTreeShadow()
					else:
						treeShadowEnabled = background.GetTreeShadow() if hasattr(background, "GetTreeShadow") else 1
					self.__ClickRadioButton(self.treeShadowButtonList, 0 if treeShadowEnabled else 1)
				except:
					pass

				# Tree LOD Quality
				try:
					self.treeLodButtonList = []
					self.treeLodButtonList.append(GetObject("tree_lod_low"))
					self.treeLodButtonList[0].SAFE_SetEvent(self.__OnClickTreeLod, 0)
					self.treeLodButtonList.append(GetObject("tree_lod_medium"))
					self.treeLodButtonList[1].SAFE_SetEvent(self.__OnClickTreeLod, 1)
					self.treeLodButtonList.append(GetObject("tree_lod_high"))
					self.treeLodButtonList[2].SAFE_SetEvent(self.__OnClickTreeLod, 2)
					savedLodIdx = systemSetting.GetTreeLodIndex() if hasattr(systemSetting, "GetTreeLodIndex") else 1
					if savedLodIdx < 0 or savedLodIdx > 2:
						savedLodIdx = 1
					self.__ClickRadioButton(self.treeLodButtonList, savedLodIdx)
				except:
					pass

			# Category 4: Sound
			if optionIndex == 4 or self.children["filteringEnabled"]:
				self.ctrlSoundVolume = GetObject("sound_volume_controller")
				self.ctrlSoundVolume.SetSliderPos(float(systemSetting.GetSoundVolume()) / 5.0)
				self.ctrlSoundVolume.SetEvent(ui.__mem_func__(self.OnChangeSoundVolume))

				self.ctrlMusicVolume = GetObject("music_volume_controller")
				self.ctrlMusicVolume.SetSliderPos(float(systemSetting.GetMusicVolume()))
				self.ctrlMusicVolume.SetEvent(ui.__mem_func__(self.OnChangeMusicVolume))

				self.selectMusicButton = GetObject("bgm_button")
				self.selectMusicButton.SAFE_SetEvent(self.__OnClickChangeMusicButton)
				self.selectMusicFile = GetObject("bgm_file")

		except Exception, msg:
			dbg.TraceError("LoadCategoryOptions : %s" % (msg))

	# Scrollbar and window helpers - Dont Touch
	def GetCurrentWindow(self):
		if self.children.has_key("optionType"):
			optionType = self.children["optionType"]
			if self.children.has_key("filteringEnabled"):
				if self.children["filteringEnabled"]:
					if self.children.has_key("filteredWindow"):
						return self.children["filteredWindow"]
					return None
				else:
					if self.children.has_key("optionWindow%d" % (optionType)):
						return self.children["optionWindow%d" % (optionType)]
		return None

	def GetCurrentScrollBar(self):
		window = self.GetCurrentWindow()
		if window != None:
			return window.scrollBar
		return None

	# the engine walks the whole board subtree on every wheel tick regardless of
	# cursor position, so an ungated handler steals the event from the panel beside
	# it -- and, through the root fallback, from the camera behind the window
	def OnMouseWheel(self, nLen):
		window = self.GetCurrentWindow()
		if window is None or not window.IsInPosition():
			return False
		scrollBar = window.scrollBar
		if scrollBar is None or not scrollBar.IsShow():
			return False
		if nLen > 0:
			scrollBar.OnUp()
		else:
			scrollBar.OnDown()
		return True

	def OnMouseWheelCategories(self, nLen):
		if not self.children["categoryScrollBoard"].IsInPosition():
			return False
		if self.scrollBar2 is None or not self.scrollBar2.IsShow():
			return False
		if nLen > 0:
			self.scrollBar2.OnUp()
		else:
			self.scrollBar2.OnDown()
		return True

	def GoToSubcategory(self, subcategoryName):
		if not self.scrollbar_is_show:
			return
		window = self.GetCurrentWindow()
		if window is None:
			return

		scrollBar = window.scrollBar
		if scrollBar is None:
			return

		scrollLen = self.__GetContentHeight(window) - window.GetHeight()
		if scrollLen <= 0:
			return

		for childName, child in window.ElementDictionary.items():
			if not childName.startswith("title_"):
				continue
			if child.GetText() != subcategoryName:
				continue
			# the label already carries the live scroll offset, so add it back to
			# recover the unscrolled position the target is measured against
			onScreen = child.GetGlobalPosition()[1] - window.GetGlobalPosition()[1]
			target = onScreen + int(scrollBar.GetPos() * scrollLen) - 5
			scrollBar.SetPos(max(0.0, min(1.0, float(target) / float(scrollLen))))
			self.UpdateScrollBar()
			return

	WHEEL_STEP_PIXELS = 60.0

	def __GetContentHeight(self, window):
		if self.children.get("filteringEnabled", False):
			if self.children.has_key("filteredWindowHeight"):
				return self.children["filteredWindowHeight"]
		height = 0
		for child in window.Children:
			bottom = child.exPos[1] + child.GetHeight()
			if bottom > height:
				height = bottom
		return height

	def UpdateScrollBar(self):
		window = self.GetCurrentWindow()
		if window == None:
			return
		scrollBar = window.scrollBar
		if scrollBar == None:
			return
		scriptChildrens = window.Children
		if len(scriptChildrens) == 0:
			return

		windowHeight = window.GetHeight()
		screenSize = self.__GetContentHeight(window)

		if screenSize > windowHeight:
			scrollLen = screenSize - windowHeight
			basePos = int(scrollBar.GetPos() * scrollLen)
			isFiltering = self.children.get("filteringEnabled", False)
			for child in scriptChildrens:
				# When filtering, only process visible (matched) children
				if isFiltering and not child.IsShow():
					continue
				(_x, _y) = child.exPos
				child.SetPosition(_x, _y - basePos)

			scrollBar.SetMiddleBarSize(float(windowHeight) / float(screenSize))
			scrollBar.SetScrollStep(min(1.0, self.WHEEL_STEP_PIXELS / float(scrollLen)))
			scrollBar.Show()
			self.scrollbar_is_show = True
		else:
			scrollBar.Hide()
			self.scrollbar_is_show = False

		_wy = window.GetGlobalPosition()[1]
		isFiltering = self.children.get("filteringEnabled", False)
		elementDictionary = window.ElementDictionary
		for childName, child in elementDictionary.items():
			# When filtering, skip elements that are not visible
			if isFiltering and hasattr(child, 'GetParent'):
				parent = child.GetParent()
				if parent and hasattr(parent, 'IsShow') and not parent.IsShow():
					continue
			(_x, _y) = child.GetGlobalPosition()
			childHeight = child.GetHeight()
			textLines = []
			images = []
			if isinstance(child, ui.ExpandedImageBox):
				images.append(child)
			elif isinstance(child, ui.TextLine):
				textLines.append(child)
			elif isinstance(child, ui.ToggleButton) or isinstance(child, ui.RadioButton or isinstance(child, ui.Button)):
				if child.ButtonText != None:
					textLines.append(child.ButtonText)
				images.append(child)
			elif isinstance(child, ui.SliderBar):
				if child.backGroundImage != None:
					images.append(child.backGroundImage)
				if child.cursor != None:
					images.append(child.cursor)
			elif isinstance(child, ui.SliderBar_AdvancedGameOptions):
				if child.backGroundImage != None:
					images.append(child.backGroundImage)
				if child.cursor != None:
					images.append(child.cursor)
				if child.percentage != None:
					textLines.append(child.percentage)

			for childItem in textLines:
				if _y < _wy:
					if childItem.IsShow():
						childItem.Hide()
				elif _y > (_wy + windowHeight - 20):
					if childItem.IsShow():
						childItem.Hide()
				else:
					if not childItem.IsShow():
						childItem.Show()

			for childItem in images:
				if _y < _wy:
					childItem.SetRenderingRect(0, ui.calculateRect(childHeight - abs(_y - _wy), childHeight), 0, 0)
				elif _y + childHeight > (_wy + windowHeight - 4):
					calculate = (_wy + windowHeight - 4) - (_y + childHeight)
					if calculate == 0:
						continue
					f = ui.calculateRect(childHeight - abs(calculate), childHeight)
					childItem.SetRenderingRect(0, 0, 0, f)
				else:
					childItem.SetRenderingRect(0, 0, 0, 0)

	# ==================== EVENT HANDLERS ====================

	# PvP Mode
	def __SetPeacePKMode(self):
		self.__SetPKMode(player.PK_MODE_PEACE)

	def __SetPKMode(self, mode):
		for btn in self.pvpModeButtonDict.values():
			btn.SetUp()
		if self.pvpModeButtonDict.has_key(mode):
			self.pvpModeButtonDict[mode].Down()

	def __CheckPvPProtectedLevelPlayer(self):
		if player.GetStatus(player.LEVEL) < constinfo.PVPMODE_PROTECTED_LEVEL:
			self.__SetPeacePKMode()
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_PROTECT % (constinfo.PVPMODE_PROTECTED_LEVEL))
			return True
		return False

	def __RefreshPVPButtonList(self):
		self.__SetPKMode(player.GetPKMode())

	def __OnClickPvPModePeaceButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if constinfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 0", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_NOT_SUPPORT)

	def __OnClickPvPModeRevengeButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if constinfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 1", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_NOT_SUPPORT)

	def __OnClickPvPModeFreeButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if constinfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 2", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_NOT_SUPPORT)

	def __OnClickPvPModeGuildButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if 0 == player.GetGuildID():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_CANNOT_SET_GUILD_MODE)
			return
		if constinfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 4", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OPTION_PVPMODE_NOT_SUPPORT)

	def OnChangePKMode(self):
		self.__RefreshPVPButtonList()

	# Block Mode
	def RefreshBlock(self):
		if app.ENABLE_COMMUNITY_SYSTEM:
			cfg = community.GetMyConfig()
			for i in xrange(len(self.blockButtonList)):
				if cfg & _COMM_BLOCK_MASTERS[i]:
					self.blockButtonList[i].Down()
				else:
					self.blockButtonList[i].SetUp()
			return
		global blockMode
		for i in xrange(len(self.blockButtonList)):
			if 0 != (blockMode & (1 << i)):
				self.blockButtonList[i].Down()
			else:
				self.blockButtonList[i].SetUp()

	def OnBlockMode(self, mode):
		global blockMode
		blockMode = mode
		self.RefreshBlock()

	def __OnClickBlockExchangeButton(self):
		if app.ENABLE_COMMUNITY_SYSTEM:
			net.SendCommunitySetConfig(community.GetMyConfig() ^ community.COMMUNITY_CFG_BLOCK_EXCHANGE)
			return
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_EXCHANGE))

	def __OnClickBlockPartyButton(self):
		if app.ENABLE_COMMUNITY_SYSTEM:
			net.SendCommunitySetConfig(community.GetMyConfig() ^ community.COMMUNITY_CFG_BLOCK_PARTY_INVITE)
			return
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_PARTY))

	def __OnClickBlockGuildButton(self):
		if app.ENABLE_COMMUNITY_SYSTEM:
			net.SendCommunitySetConfig(community.GetMyConfig() ^ community.COMMUNITY_CFG_BLOCK_GUILD_INVITE)
			return
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_GUILD))

	def __OnClickBlockWhisperButton(self):
		if app.ENABLE_COMMUNITY_SYSTEM:
			net.SendCommunitySetConfig(community.GetMyConfig() ^ community.COMMUNITY_CFG_BLOCK_WHISPER)
			return
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_WHISPER))

	def __OnClickBlockFriendButton(self):
		if app.ENABLE_COMMUNITY_SYSTEM:
			net.SendCommunitySetConfig(community.GetMyConfig() ^ community.COMMUNITY_CFG_BLOCK_FRIEND_REQUEST)
			return
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_FRIEND))

	def __OnClickBlockPartyRequest(self):
		if app.ENABLE_COMMUNITY_SYSTEM:
			net.SendCommunitySetConfig(community.GetMyConfig() ^ community.COMMUNITY_CFG_BLOCK_PARTY_REQUEST)
			return
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_PARTY_REQUEST))

	# Chat Mode - New Toggle Style
	def RefreshViewChatToggle(self):
		if hasattr(self, 'viewChatToggle') and self.viewChatToggle:
			if systemSetting.IsViewChat():
				self.viewChatToggle.Down()
			else:
				self.viewChatToggle.SetUp()

	def __OnClickViewChatToggle(self):
		systemSetting.SetViewChatFlag(not systemSetting.IsViewChat())
		self.RefreshViewChatToggle()

	# Chat Mode - Old Radio Button Style (for backwards compatibility)
	def RefreshViewChat(self):
		if hasattr(self, 'viewChatButtonList') and len(self.viewChatButtonList) >= 2:
			if systemSetting.IsViewChat():
				self.viewChatButtonList[0].Down()
				self.viewChatButtonList[1].SetUp()
			else:
				self.viewChatButtonList[0].SetUp()
				self.viewChatButtonList[1].Down()

	def __OnClickViewChat(self):
		systemSetting.SetViewChatFlag(not systemSetting.IsViewChat())
		self.RefreshViewChat()

	# Name Color Mode
	def __OnClickNameColorMode(self):
		newIdx = not constinfo.GET_CHRNAME_COLOR_INDEX()
		constinfo.SET_CHRNAME_COLOR_INDEX(newIdx)
		if hasattr(systemSetting, "SetNameColorMode"):
			systemSetting.SetNameColorMode(1 if newIdx else 0)
			systemSetting.SaveConfig()
		self.RefreshNameColor()

	def RefreshNameColor(self):
		index = constinfo.GET_CHRNAME_COLOR_INDEX()
		self.nameColorModeButtonList[index].Down()
		self.nameColorModeButtonList[not index].SetUp()

	# Target Board Mode
	def RefreshTargetBoard(self):
		index = constinfo.GET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD()
		self.viewTargetBoardButtonList[index].Down()
		self.viewTargetBoardButtonList[not index].SetUp()

	def __SetTargetBoardViewMode(self):
		newVal = not constinfo.GET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD()
		constinfo.SET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD(newVal)
		if hasattr(systemSetting, "SetViewOtherEmpireTargetBoard"):
			systemSetting.SetViewOtherEmpireTargetBoard(1 if newVal else 0)
			systemSetting.SaveConfig()
		self.RefreshTargetBoard()

	# Hide Names Toggle (inverted: toggle ON = names hidden = AlwaysShowName OFF)
	def RefreshHideNamesToggle(self):
		if hasattr(self, 'hideNamesToggle') and self.hideNamesToggle:
			if systemSetting.IsAlwaysShowName():
				self.hideNamesToggle.SetUp()  # Names shown = toggle off
			else:
				self.hideNamesToggle.Down()   # Names hidden = toggle on

	def __OnClickHideNamesToggle(self):
		systemSetting.SetAlwaysShowNameFlag(not systemSetting.IsAlwaysShowName())
		self.RefreshHideNamesToggle()

	# Outline Name Toggle (toggle ON = outline enabled)
	def RefreshOutlineNameToggle(self):
		if hasattr(self, 'outlineNameToggle') and self.outlineNameToggle:
			if systemSetting.IsShowOutline():
				self.outlineNameToggle.Down()   # Outline enabled = toggle on
			else:
				self.outlineNameToggle.SetUp()  # Outline disabled = toggle off

	def __OnClickOutlineNameToggle(self):
		systemSetting.SetShowOutlineFlag(not systemSetting.IsShowOutline())
		self.RefreshOutlineNameToggle()

	# Hide Damage All Toggle (inverted: toggle ON = damage hidden = ShowDamage OFF)
	def RefreshHideDamageAllToggle(self):
		if hasattr(self, 'hideDamageAllToggle') and self.hideDamageAllToggle:
			if systemSetting.IsShowDamage():
				self.hideDamageAllToggle.SetUp()  # Damage shown = toggle off
			else:
				self.hideDamageAllToggle.Down()   # Damage hidden = toggle on

	def __OnClickHideDamageAllToggle(self):
		systemSetting.SetShowDamageFlag(not systemSetting.IsShowDamage())
		self.RefreshHideDamageAllToggle()

	# Hide Damage Mobs Toggle (toggle ON = mob damage hidden)
	def RefreshHideDamageMobsToggle(self):
		if hasattr(self, 'hideDamageMobsToggle') and self.hideDamageMobsToggle:
			if systemSetting.IsHideMobDamage():
				self.hideDamageMobsToggle.Down()   # Mob damage hidden = toggle on
			else:
				self.hideDamageMobsToggle.SetUp()  # Mob damage shown = toggle off

	def __OnClickHideDamageMobsToggle(self):
		systemSetting.SetHideMobDamageFlag(not systemSetting.IsHideMobDamage())
		self.RefreshHideDamageMobsToggle()

	if app.ENABLE_AUTO_SHOUT_V2:
		# Show Auto-Shouts Toggle (toggle ON = auto-shouts visible, config default)
		def RefreshShowAutoShoutToggle(self):
			if getattr(self, 'showAutoShoutToggle', None):
				if systemSetting.IsShowAutoShout():
					self.showAutoShoutToggle.Down()
				else:
					self.showAutoShoutToggle.SetUp()

		def __OnClickShowAutoShoutToggle(self):
			systemSetting.SetShowAutoShoutFlag(not systemSetting.IsShowAutoShout())
			self.RefreshShowAutoShoutToggle()

	def __OnClickDamageColorSwatch(self, slotIndex):
		if not self.damageColorPicker:
			self.damageColorPicker = uidamagecolorpicker.DamageColorPicker()
		self.damageColorPicker.Open(slotIndex, ui.__mem_func__(self.__OnDamageColorApplied))

	def __OnDamageColorApplied(self, slotIndex):
		self.RefreshDamageColorSwatches()

	def RefreshDamageColorSwatches(self):
		swatches = getattr(self, "damageColorSwatches", [])
		for i in xrange(len(swatches)):
			swatches[i].ResetHover()
			swatches[i].SetRGB(systemSetting.GetDamageColor(i))

	def __OnClickAutoHuntColorSwatch(self):
		if not self.damageColorPicker:
			self.damageColorPicker = uidamagecolorpicker.DamageColorPicker()
		self.damageColorPicker.Open(
			0,
			ui.__mem_func__(self.__OnAutoHuntColorApplied),
			uidamagecolorpicker.GetAutoHuntEffectColor,
			uidamagecolorpicker.SetAutoHuntEffectColor,
			getattr(localeinfo, "AUTO_HUNT_COLOR_PICKER_TITLE", "Auto-Hunt Aura Color"),
			False,
			uidamagecolorpicker.AUTO_HUNT_DEFAULT_COLOR,
			uidamagecolorpicker.AUTO_HUNT_PRESET_COLORS)

	def __OnAutoHuntColorApplied(self, slotIndex):
		self.RefreshAutoHuntColorSwatch()

	def RefreshAutoHuntColorSwatch(self):
		swatch = getattr(self, "autoHuntColorSwatch", None)
		if swatch:
			swatch.ResetHover()
			swatch.SetRGB(systemSetting.GetAutoHuntEffectColor() or uidamagecolorpicker.AUTO_HUNT_DEFAULT_COLOR)

	# Hide Shops Toggle (inverted: toggle ON = shops hidden = ShowSalesText OFF)
	def RefreshHideShopsToggle(self):
		if hasattr(self, 'hideShopsToggle') and self.hideShopsToggle:
			if systemSetting.IsShowSalesText():
				self.hideShopsToggle.SetUp()  # Shops shown = toggle off
			else:
				self.hideShopsToggle.Down()   # Shops hidden = toggle on

	def __OnClickHideShopsToggle(self):
		newState = not systemSetting.IsShowSalesText()
		systemSetting.SetShowSalesTextFlag(newState)
		if app.USE_OFFLINESHOP:
			import offlineshop
			if newState:
				offlineshop.ShowShopNames()
			else:
				offlineshop.HideShopNames()
		self.RefreshHideShopsToggle()

	# Tiling Mode
	def __NotifyChatLine(self, text):
		chat.AppendChat(chat.CHAT_TYPE_INFO, text)

	def __SetTilingMode(self, index):
		self.__ClickRadioButton(self.tilingModeButtonList, index)
		self.tilingMode = index

	def __OnClickTilingModeCPUButton(self):
		self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_CPU_TILING_1)
		self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_CPU_TILING_2)
		self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_CPU_TILING_3)
		self.__SetTilingMode(0)

	def __OnClickTilingModeGPUButton(self):
		self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_GPU_TILING_1)
		self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_GPU_TILING_2)
		self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_GPU_TILING_3)
		self.__SetTilingMode(1)

	def __SetCurTilingMode(self):
		# Repurposed GPU/CPU toggle -> GPU skinning (instant runtime toggle, no restart).
		if app.IsGPUSkinningSupported() and app.IsGPUSkinningEnable():
			self.__SetTilingMode(1)
		else:
			self.__SetTilingMode(0)

	def __OnClickTilingApplyButton(self):
		# Repurposed: toggle GPU skinning at runtime (tilingMode 1=GPU, 0=CPU). No restart needed.
		if not app.IsGPUSkinningSupported():
			self.__NotifyChatLine(localeinfo.SYSTEM_OPTION_CPU_TILING_1)
			self.__SetTilingMode(0)
			return
		app.SetGPUSkinningEnable(self.tilingMode)
		systemSetting.SetGPUSkinning(self.tilingMode)
		systemSetting.SaveConfig()

	# Camera Mode
	# def RefreshCameraMode(self):
		# index = constinfo.GET_CAMERA_MAX_DISTANCE_INDEX()
		# self.cameraModeButtonList[index].Down()
		# self.cameraModeButtonList[not index].SetUp()

	# def __OnClickCameraMode(self, index):
		# constinfo.SET_CAMERA_MAX_DISTANCE_INDEX(not constinfo.GET_CAMERA_MAX_DISTANCE_INDEX())
		# self.RefreshCameraMode()

	# Sound Mode
	def OnChangeSoundVolume(self):
		pos = self.ctrlSoundVolume.GetSliderPos()
		snd.SetSoundVolumef(pos)
		systemSetting.SetSoundVolumef(pos)

	# Music Mode
	def OnChangeMusicVolume(self):
		pos = self.ctrlMusicVolume.GetSliderPos()
		snd.SetMusicVolume(pos * net.GetFieldMusicVolume())
		systemSetting.SetMusicVolume(pos)

	def __OnChangeMusic(self, fileName):
		self.selectMusicFile.SetText(fileName[:MUSIC_FILENAME_MAX_LEN])
		if musicinfo.fieldMusic != "":
			snd.FadeOutMusic("BGM/" + musicinfo.fieldMusic)
		if fileName == uiselectmusic.DEFAULT_THEMA:
			musicinfo.fieldMusic = musicinfo.METIN2THEMA
		else:
			musicinfo.fieldMusic = fileName
		musicinfo.SaveLastPlayFieldMusic()
		if musicinfo.fieldMusic != "":
			snd.FadeInMusic("BGM/" + musicinfo.fieldMusic)

	def __OnClickChangeMusicButton(self):
		if not self.musicListDlg:
			self.musicListDlg = uiselectmusic.FileListDialog()
			self.musicListDlg.SAFE_SetSelectEvent(self.__OnChangeMusic)
		self.musicListDlg.Open()

	# ==================== CONDITIONAL FEATURE HANDLERS ====================

	if app.ENABLE_KEYCHANGE_SYSTEM:
		def OpenKeyChangeWindow(self):
			if self.keyboardButton:
				self.keyboardButton.SetUp()
			player.OpenKeyChangeWindow()

	if app.ENABLE_FOV_OPTION:
		def __OnChangeFOV(self):
			if not self.fovController:
				return

			pos = self.fovController.GetSliderPos()
			fovMin = float(systemSetting.MIN_CAMERA_PERSPECTIVE)
			fovMax = float(systemSetting.MAX_CAMERA_PERSPECTIVE)
			fovValue = fovMin + (pos * (fovMax - fovMin))

			systemSetting.SetFOV(fovValue)
			if self.fovValueText:
				self.fovValueText.SetText(str(int(systemSetting.GetFOV())) + chr(176))

		def __OnClickFOVResetButton(self):
			fovMin = float(systemSetting.MIN_CAMERA_PERSPECTIVE)
			fovMax = float(systemSetting.MAX_CAMERA_PERSPECTIVE)
			fovDefault = float(systemSetting.DEFAULT_CAMERA_PERSPECTIVE)

			defaultNormalized = (fovDefault - fovMin) / (fovMax - fovMin)
			if self.fovController:
				self.fovController.SetSliderPos(defaultNormalized)
			systemSetting.SetFOV(fovDefault)
			if self.fovValueText:
				self.fovValueText.SetText(str(int(systemSetting.GetFOV())) + chr(176))

	if app.USE_METIN_STONE_SCALE:
		def OnChangeMetinStoneSize(self):
			if not self.metinstoneSize:
				return
			systemSetting.SetMetinStoneScale(float(self.metinstoneSize.GetSliderPos()))

	if app.__SCALE_EFFECT_DAMAGE__:
		def OnChangeScaleEffDamage(self):
			if not self.changeScaleEffDamage:
				return
			pos = float(self.changeScaleEffDamage.GetSliderPos())
			systemSetting.SetScaleEffDamageLevel(int(pos / 0.2))

	if app.USE_IMPROVEMENTS:
		def __OnChangeEffectDistance(self):
			systemSetting.SetEffectRenderRange(float(self.effectController.GetSliderPos()))

	if app.USE_OFFLINESHOP_VIEW_RANGE:
		def __SetPrivateShopViewRange(self):
			systemSetting.SetPrivateShopViewRange(float(self.privateshop_range_controller.GetSliderPos()))

	if app.WJ_SHOW_MOB_INFO:
		def RefreshShowMobInfo(self):
			if systemSetting.IsShowMobLevel():
				self.showMobInfoButtonList[0].Down()
			else:
				self.showMobInfoButtonList[0].SetUp()
			if systemSetting.IsShowMobAIFlag():
				self.showMobInfoButtonList[1].Down()
			else:
				self.showMobInfoButtonList[1].SetUp()

		def __OnClickShowMobLevelButton(self):
			systemSetting.SetShowMobLevel(not systemSetting.IsShowMobLevel())
			self.RefreshShowMobInfo()

		def __OnClickShowMobAIFlagButton(self):
			systemSetting.SetShowMobAIFlag(not systemSetting.IsShowMobAIFlag())
			self.RefreshShowMobInfo()

	if app.ENABLE_GRAPHIC_ON_OFF:
		def RefreshPetStatus(self):
			if systemSetting.IsPetStatus():
				self.petStatusButtonList[1].SetUp()
				self.petStatusButtonList[0].Down()
			else:
				self.petStatusButtonList[1].Down()
				self.petStatusButtonList[0].SetUp()

		def __OnClickPetStatusButton(self, flag):
			systemSetting.SetPetStatusFlag(flag)
			self.RefreshPetStatus()

		def RefreshMountStatus(self):
			if systemSetting.IsMountStatus():
				self.MountStatusButtonList[1].SetUp()
				self.MountStatusButtonList[0].Down()
			else:
				self.MountStatusButtonList[1].Down()
				self.MountStatusButtonList[0].SetUp()

		def __OnClickMountStatusButton(self, flag):
			systemSetting.SetMountStatusFlag(flag)
			self.RefreshMountStatus()

		# Effect visibility toggle handlers
		def RefreshEffectVisibilityToggles(self):
			if self.hideBuffToggle:
				if systemSetting.IsHideBuffEffects():
					self.hideBuffToggle.Down()
				else:
					self.hideBuffToggle.SetUp()

			if self.hideSkillToggle:
				if systemSetting.IsHideSkillEffects():
					self.hideSkillToggle.Down()
				else:
					self.hideSkillToggle.SetUp()

			if self.hideGeneralToggle:
				if systemSetting.IsHideGeneralEffects():
					self.hideGeneralToggle.Down()
				else:
					self.hideGeneralToggle.SetUp()

			if self.hideMonsterToggle:
				if systemSetting.IsHideMonsterEffects():
					self.hideMonsterToggle.Down()
				else:
					self.hideMonsterToggle.SetUp()

			# if self.hideProjectilesToggle:
				# if systemSetting.IsHideProjectiles():
					# self.hideProjectilesToggle.Down()
				# else:
					# self.hideProjectilesToggle.SetUp()

			if self.bossEffectToggle:
				if systemSetting.IsBossEffectException():
					self.bossEffectToggle.Down()
				else:
					self.bossEffectToggle.SetUp()

		def __OnToggleHideBuffEffects(self):
			isDown = self.hideBuffToggle.IsDown() if self.hideBuffToggle else False
			systemSetting.SetHideBuffEffects(isDown)

		def __OnToggleHideSkillEffects(self):
			isDown = self.hideSkillToggle.IsDown() if self.hideSkillToggle else False
			systemSetting.SetHideSkillEffects(isDown)

		def __OnToggleHideGeneralEffects(self):
			isDown = self.hideGeneralToggle.IsDown() if self.hideGeneralToggle else False
			systemSetting.SetHideGeneralEffects(isDown)

		def __OnToggleHideMonsterEffects(self):
			isDown = self.hideMonsterToggle.IsDown() if self.hideMonsterToggle else False
			systemSetting.SetHideMonsterEffects(isDown)

		# def __OnToggleHideProjectiles(self):
			# isDown = self.hideProjectilesToggle.IsDown() if self.hideProjectilesToggle else False
			# systemSetting.SetHideProjectiles(isDown)

		def __OnToggleBossEffect(self):
			isDown = self.bossEffectToggle.IsDown() if self.bossEffectToggle else False
			systemSetting.SetBossEffectException(isDown)

	# Hide NPC Names Toggle (inverted: toggle ON = NPC names hidden = NpcNameStatus OFF)
	def RefreshHideNpcToggle(self):
		if hasattr(self, 'hideNpcToggle') and self.hideNpcToggle:
			if systemSetting.IsNpcNameStatus():
				self.hideNpcToggle.SetUp()  # NPC names shown = toggle off
			else:
				self.hideNpcToggle.Down()   # NPC names hidden = toggle on

	def __OnClickHideNpcToggle(self):
		systemSetting.SetNpcNameStatusFlag(not systemSetting.IsNpcNameStatus())
		self.RefreshHideNpcToggle()

	if app.ENABLE_SHADOW_RENDER_QUALITY_OPTION:
		def __OnClickChangeShadowTarget(self, shadow_target):
			systemSetting.SetShadowTargetLevel(shadow_target)
			background.SetShadowTargetLevel(shadow_target)
			self.__ClickRadioButton(self.shadowTargetButtonList, shadow_target)

		def __OnClickChangeShadowQuality(self, shadow_quality):
			systemSetting.SetShadowQualityLevel(shadow_quality)
			background.SetShadowQualityLevel(shadow_quality)
			self.__ClickRadioButton(self.shadowQualityButtonList, shadow_quality)
	else:
		def OnChangeShadowQuality(self):
			pos = self.ctrlShadowQuality.GetSliderPos()
			systemSetting.SetShadowLevel(int(pos / 0.2))

	def __OnClickTreeShadow(self, bEnabled):
		if hasattr(background, "SetTreeShadow"):
			background.SetTreeShadow(bEnabled)
		if hasattr(systemSetting, "SetTreeShadow"):
			systemSetting.SetTreeShadow(1 if bEnabled else 0)
			systemSetting.SaveConfig()
		self.__ClickRadioButton(self.treeShadowButtonList, 0 if bEnabled else 1)

	TREE_LOD_BIAS_VALUES = [0.5, 1.0, 1.5]

	def __OnClickTreeLod(self, lodIndex):
		if hasattr(background, "SetTreeLodBias"):
			background.SetTreeLodBias(self.TREE_LOD_BIAS_VALUES[lodIndex])
		if hasattr(systemSetting, "SetTreeLodIndex"):
			systemSetting.SetTreeLodIndex(lodIndex)
			systemSetting.SaveConfig()
		self.__ClickRadioButton(self.treeLodButtonList, lodIndex)

	if app.USE_BACKGROUND_FPS_CAP:
		def RefreshBackgroundFps(self):
			if not self.backgroundFpsToggle:
				return

			if systemSetting.GetBackgroundFpsCap():
				self.backgroundFpsToggle.Down()
			else:
				self.backgroundFpsToggle.SetUp()

		def __OnToggleBackgroundFps(self, enabled):
			systemSetting.SetBackgroundFpsCap(enabled)
			systemSetting.SaveConfig()

	if app.ENABLE_FPS:
		def RefreshFPS(self):
			for btn in self.fpsButtonList:
				btn.SetUp()
			fpsIndex = systemSetting.GetFPS()
			# 255 = AUTO preset (match monitor refresh) has no fixed button here
			if fpsIndex < len(self.fpsButtonList):
				self.fpsButtonList[fpsIndex].Down()

		def __OnClickFPSButton(self, mode):
			systemSetting.SetFPS(mode)
			if app.IsVisible():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.FPS_WINDOW_ALERT)
			self.RefreshFPS()

	if app.ENABLE_POST_PROCESSING:
		def RefreshPostProcessing(self):
			quality = app.GetPostProcessQuality()
			isEnabled = quality != app.PP_QUALITY_OFF

			# Update toggle
			if hasattr(self, 'ppToggle') and self.ppToggle:
				if isEnabled:
					self.ppToggle.Down()
				else:
					self.ppToggle.SetUp()

			# Update quality radio buttons
			for btn in self.ppQualityButtonList:
				btn.SetUp()

			if isEnabled and quality >= app.PP_QUALITY_LOW:
				btnIndex = quality - app.PP_QUALITY_LOW
				if 0 <= btnIndex < len(self.ppQualityButtonList):
					self.ppQualityButtonList[btnIndex].Down()

			# Show/hide advanced controls based on enabled state
			advControls = [
				self.ppVignetteToggle, self.ppVignetteLabel,
				self.ppSharpenLabel, self.ppSharpenSlider, self.ppSharpenValueText,
				self.ppColorGradeLabel,
				self.ppLUTStrengthLabel,
				self.ppLUTStrengthSlider,
				self.ppLUTStrengthValueText,
			]
			for ctrl in advControls:
				if ctrl:
					ctrl.Show() if isEnabled else ctrl.Hide()
			for btn in self.ppLUTButtonList:
				btn.Show() if isEnabled else btn.Hide()

			# Refresh LUT radio button selection
			if isEnabled:
				lutPreset = app.GetColorLUTPreset()
				for i, btn in enumerate(self.ppLUTButtonList):
					if i == lutPreset:
						btn.Down()
					else:
						btn.SetUp()

		def LoadPostProcessConfig(self):
			# Sync UI to current engine state only - no Set calls, quality was applied at startup
			vignetteOn = app.GetPostProcessEnabled(app.PP_EFFECT_VIGNETTE)
			if self.ppVignetteToggle:
				self.ppVignetteToggle.Down() if vignetteOn else self.ppVignetteToggle.SetUp()

			sharpenVal = app.GetSharpenIntensity()
			if self.ppSharpenSlider:
				self.ppSharpenSlider.SetSliderPos(sharpenVal)
			if self.ppSharpenValueText:
				self.ppSharpenValueText.SetText("%.2f" % sharpenVal)

			strengthVal = app.GetColorLUTStrength()
			if self.ppLUTStrengthSlider:
				self.ppLUTStrengthSlider.SetSliderPos(strengthVal / 1.5)
			if self.ppLUTStrengthValueText:
				self.ppLUTStrengthValueText.SetText("%.2f" % strengthVal)

			self.RefreshPostProcessing()

		def __OnClickPostProcessToggle(self):
			quality = app.GetPostProcessQuality()
			if quality == app.PP_QUALITY_OFF:
				app.SetPostProcessQuality(app.PP_QUALITY_LOW)
				systemSetting.SetPostProcessQuality(app.PP_QUALITY_LOW)
			else:
				app.SetPostProcessQuality(app.PP_QUALITY_OFF)
				systemSetting.SetPostProcessQuality(app.PP_QUALITY_OFF)
			systemSetting.SaveConfig()
			self.RefreshPostProcessing()

		def __OnClickPostProcessQuality(self, quality):
			app.SetPostProcessQuality(quality)
			systemSetting.SetPostProcessQuality(quality)
			systemSetting.SaveConfig()
			self.RefreshPostProcessing()

		def __OnClickPPVignette(self, enabled):
			app.SetPostProcessEnabled(app.PP_EFFECT_VIGNETTE, enabled)
			systemSetting.SetPPVignetteEnabled(enabled)
			systemSetting.SaveConfig()

		def __OnChangePPSharpen(self):
			if not self.ppSharpenSlider:
				return
			val = self.ppSharpenSlider.GetSliderPos()
			app.SetSharpenIntensity(val)
			systemSetting.SetPPSharpenIntensity(val)
			systemSetting.SaveConfig()
			if self.ppSharpenValueText:
				self.ppSharpenValueText.SetText("%.2f" % val)

		def __OnClickPPLUT(self, preset):
			app.SetColorLUTPreset(preset)
			systemSetting.SetPPLUTPreset(preset)
			systemSetting.SaveConfig()
			for i, btn in enumerate(self.ppLUTButtonList):
				if i == preset:
					btn.Down()
				else:
					btn.SetUp()

		def __OnChangePPLUTStrength(self):
			if not self.ppLUTStrengthSlider:
				return
			val = self.ppLUTStrengthSlider.GetSliderPos() * 1.5
			app.SetColorLUTStrength(val)
			systemSetting.SetPPLUTStrength(val)
			systemSetting.SaveConfig()
			if self.ppLUTStrengthValueText:
				self.ppLUTStrengthValueText.SetText("%.2f" % val)

	if app.ENABLE_FOG_FIX:
		def RefreshFogMode(self):
			if background.GetFogMode():
				self.fogButtonList[1].Down()
				self.fogButtonList[0].SetUp()
			else:
				self.fogButtonList[1].SetUp()
				self.fogButtonList[0].Down()

		def __OnClickFogModeOnButton(self):
			systemSetting.SetFogMode(True)
			background.SetFogMode(True)
			self.RefreshFogMode()

		def __OnClickFogModeOffButton(self):
			systemSetting.SetFogMode(False)
			background.SetFogMode(False)
			self.RefreshFogMode()

	if app.ENABLE_ENVIRONMENT_EFFECT_OPTION:
		def __DayMode_OnCompleteChangeToLight(self):
			background.ChangeEnvironmentData(background.DAY_MODE_LIGHT)
			self.curtain.FadeIn()

		def __DayMode_OnCompleteChangeToDark(self):
			background.RegisterEnvironmentData(background.DAY_MODE_DARK, constinfo.ENVIRONMENT_NIGHT)
			background.ChangeEnvironmentData(background.DAY_MODE_DARK)
			self.curtain.FadeIn()

		def __SetNightMode(self, index):
			systemSetting.SetNightModeOption(index)
			if not background.GetDayMode():
				return

			if not background.IsBoomMap():
				return

			if 1 == index:
				self.curtain.SAFE_FadeOut(self.__DayMode_OnCompleteChangeToDark)
			else:
				self.curtain.SAFE_FadeOut(self.__DayMode_OnCompleteChangeToLight)

			self.RefreshNightModeToggle()

		def RefreshNightModeToggle(self):
			if hasattr(self, 'nightModeToggle') and self.nightModeToggle:
				if systemSetting.GetNightModeOption():
					self.nightModeToggle.Down()
				else:
					self.nightModeToggle.SetUp()

		def __OnClickNightModeToggle(self):
			newMode = 0 if systemSetting.GetNightModeOption() else 1
			self.__SetNightMode(newMode)
			self.RefreshNightModeToggle()

		# Weather Selection System Methods
		def __OnClickWeatherButton(self, index):
			# Map button index to actual weather index (1-9)
			weatherIndex = index if index <= 8 else 9

			if weatherIndex == 1:
				# Reset to map default
				background.SetEnvironmentData(0)
			else:
				# Apply custom skybox
				skyboxMap = {
					2: constinfo.WEATHER_SKYBOX_1,
					3: constinfo.WEATHER_SKYBOX_2,
					4: constinfo.WEATHER_SKYBOX_3,
					5: constinfo.WEATHER_SKYBOX_4,
					6: constinfo.WEATHER_SKYBOX_5,
					7: constinfo.WEATHER_SKYBOX_6,
					8: constinfo.WEATHER_SKYBOX_7,
					9: constinfo.WEATHER_SKYBOX_8,
				}
				if weatherIndex in skyboxMap:
					background.RegisterEnvironmentData(2, skyboxMap[weatherIndex])
					background.SetEnvironmentData(2)

			constinfo.WeatherIndex = weatherIndex
			self.RefreshWeatherButtons()

			# Save if toggle is enabled
			if constinfo.SaveWeatherEnabled:
				self.SaveWeatherToFile(weatherIndex)

		def RefreshWeatherButtons(self):
			if not hasattr(self, 'showNightButtonList') or not self.showNightButtonList:
				return

			currentWeather = constinfo.WeatherIndex
			buttonIndices = [1, 2, 3, 4, 5, 6, 7, 8, 10]

			for i, btn in enumerate(self.showNightButtonList):
				btnIndex = buttonIndices[i]
				expectedWeather = btnIndex if btnIndex <= 8 else 9

				if expectedWeather == currentWeather:
					btn.Down()
				else:
					btn.SetUp()

		def __OnClickSaveEnvToggle(self):
			# Toggle based on current file state (if file exists, we're turning OFF)
			import os
			filePath = "UserData/environment/{}.cfg".format(player.GetName())
			fileExists = os.path.exists(filePath)

			if fileExists:
				# Currently ON, turn OFF - delete file first
				self.DeleteWeatherFile()
				constinfo.SaveWeatherEnabled = False
			else:
				# Currently OFF, turn ON - save file first
				self.SaveWeatherToFile(constinfo.WeatherIndex)
				constinfo.SaveWeatherEnabled = True

			# Update UI after file operation
			self.RefreshSaveEnvToggle()

		def RefreshSaveEnvToggle(self):
			if hasattr(self, 'saveEnvToggle') and self.saveEnvToggle:
				# Check if config file exists to determine toggle state
				import os
				filePath = "UserData/environment/{}.cfg".format(player.GetName())
				constinfo.SaveWeatherEnabled = os.path.exists(filePath)
				if constinfo.SaveWeatherEnabled:
					self.saveEnvToggle.Down()
				else:
					self.saveEnvToggle.SetUp()

		def SaveWeatherToFile(self, weatherIndex):
			try:
				import os
				folderPath = "UserData/environment/"
				if not os.path.exists(folderPath):
					os.makedirs(folderPath)

				filePath = folderPath + "{}.cfg".format(player.GetName())
				f = open(filePath, "w")
				f.write(str(weatherIndex))
				f.close()
			except:
				pass

		def DeleteWeatherFile(self):
			try:
				import os
				filePath = "UserData/environment/{}.cfg".format(player.GetName())
				if os.path.exists(filePath):
					os.remove(filePath)
			except:
				pass

		def LoadSavedWeather(self):
			# This is now handled in game.py after map loads
			pass

		def __OnClickSnowModeOffButton(self):
			systemSetting.SetSnowModeOption(0)
			self.RefreshSnowMode()

		def __OnClickSnowModeOnButton(self):
			systemSetting.SetSnowModeOption(1)
			self.RefreshSnowMode()

		def RefreshSnowMode(self):
			if systemSetting.GetSnowModeOption():
				self.snowModeButtonList[1].Down()
				self.snowModeButtonList[0].SetUp()
			else:
				self.snowModeButtonList[1].SetUp()
				self.snowModeButtonList[0].Down()

		def __OnClickSnowTextureModeOffButton(self):
			systemSetting.SetSnowTextureModeOption(0)
			self.RefreshSnowTextureMode()

		def __OnClickSnowTextureModeOnButton(self):
			systemSetting.SetSnowTextureModeOption(1)
			self.RefreshSnowTextureMode()

		def RefreshSnowTextureMode(self):
			if systemSetting.GetSnowTextureModeOption():
				self.snowTextureModeButtonList[1].Down()
				self.snowTextureModeButtonList[0].SetUp()
			else:
				self.snowTextureModeButtonList[1].SetUp()
				self.snowTextureModeButtonList[0].Down()

	if app.ENABLE_EXTENDED_PICKUP:
		def __OnClickPickupIgnoreButton(self, type, ignore):
			systemSetting.SetPickupIgnore(type, ignore)
			self.__RefreshPickupIgnoreButtons()

		def __RefreshPickupIgnoreButtons(self):
			for i in xrange(len(self.pickupIgnoreButtonList)):
				if systemSetting.GetPickupIgnore(i):
					self.pickupIgnoreButtonList[i].Down()
				else:
					self.pickupIgnoreButtonList[i].SetUp()


class ScrollBarNew(ui.Window):
	SCROLLBAR_WIDTH = 7
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
			top.LoadImage(IMG_DIR + "scrollbar/scrollbar_top.tga")
			top.AddFlag("not_pick")
			top.Show()
			topScale = ui.ExpandedImageBox()
			topScale.SetParent(self)
			topScale.SetPosition(0, top.GetHeight())
			topScale.LoadImage(IMG_DIR + "scrollbar/scrollbar_scale.tga")
			topScale.AddFlag("not_pick")
			topScale.Show()
			bottom = ui.ExpandedImageBox()
			bottom.SetParent(self)
			bottom.LoadImage(IMG_DIR + "scrollbar/scrollbar_bottom.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()
			bottomScale = ui.ExpandedImageBox()
			bottomScale.SetParent(self)
			bottomScale.LoadImage(IMG_DIR + "scrollbar/scrollbar_scale.tga")
			bottomScale.AddFlag("not_pick")
			bottomScale.Show()
			middle = ui.ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage(IMG_DIR + "scrollbar/scrollbar_mid.tga")
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
		self.SetWindowName("NONAME_ScrollBar")

	def __del__(self):
		ui.Window.__del__(self)

	def CreateScrollBar(self):
		topImage = ui.ExpandedImageBox()
		topImage.SetParent(self)
		topImage.AddFlag("not_pick")
		topImage.LoadImage(IMG_DIR + "scrollbar/scroll_top.tga")
		topImage.Show()
		bottomImage = ui.ExpandedImageBox()
		bottomImage.SetParent(self)
		bottomImage.AddFlag("not_pick")
		bottomImage.LoadImage(IMG_DIR + "scrollbar/scroll_bottom.tga")
		bottomImage.Show()
		middleImage = ui.ExpandedImageBox()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, topImage.GetHeight())
		middleImage.LoadImage(IMG_DIR + "scrollbar/scroll_mid.tga")
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

# ==========================================================================
# Resolution dropdown - flat slate/gunmetal theme (matches the settings mockup).
# Tune these four colors (0xAARRGGBB) to taste.
# ==========================================================================
RES_BORDER_COLOR = 0xff2e251f
RES_BOX_FILL     = 0xff4d463d
RES_LIST_FILL    = 0xff3a342c
RES_TEXT_COLOR   = 0xffafa496

class ResolutionListBox(ui.ListBox):
	def __init__(self, layer = "UI"):
		ui.ListBox.__init__(self, layer)
		self.SetTextCenterAlign(False)

	def InsertItem(self, number, text, textColor = 0x00000000):
		self.keyDict[len(self.itemList)] = number
		self.textDict[len(self.itemList)] = text
		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetText(text)
		textLine.SetWindowHorizontalAlignLeft()
		textLine.SetHorizontalAlignLeft()
		textLine.SetPackedFontColor(RES_TEXT_COLOR)
		textLine.Hide()
		self.itemList.append(textLine)
		self._LocateItem()

	def _LocateItem(self):
		yPos = 0
		self.showLineCount = 0
		skipCount = self.basePos
		for textLine in self.itemList:
			textLine.Hide()
			if skipCount > 0:
				skipCount -= 1
				continue
			if localeinfo.IsARABIC():
				textLine.SetPosition(self.GetWidth() - 10, yPos + 3)
			else:
				textLine.SetPosition(4, yPos + 3)
			yPos += self.stepSize
			if yPos <= self.GetHeight():
				self.showLineCount += 1
				textLine.Show()


# ==========================================================================
# Custom resolution dropdown (ENABLE_WINDOW_RESIZE).  Popup hangs on the top-level
# board (SetTop = on top, unclipped); ScrollBarNew drives the ListBox basePos
# (works under ENABLE_COMMON_CHANGES, where the stock combobox wheel-scroll is broken).
# ==========================================================================
class ResolutionSelector(ui.Window):
	ROW_HEIGHT = 17
	VISIBLE_ROWS = 7
	BOX_WIDTH = 132
	BOX_HEIGHT = 20

	def __init__(self, topBoard, parentWnd, x, y):
		ui.Window.__init__(self)
		self.topBoard = topBoard
		self.resList = []
		self.selectEvent = None
		self.isOpen = False
		self.SetParent(parentWnd)
		self.SetPosition(x, y)
		self.SetSize(self.BOX_WIDTH, self.BOX_HEIGHT)
		self.__BuildBox()
		self.__BuildPopup(topBoard)
		self.Show()

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.selectEvent = None
		self.resList = []

	def __MakeBorderedBar(self, parent, fillColor):
		outer = ui.Bar()
		outer.SetParent(parent)
		outer.SetPosition(0, 0)
		outer.SetColor(RES_BORDER_COLOR)
		outer.AddFlag("not_pick")
		outer.Show()
		inner = ui.Bar()
		inner.SetParent(outer)
		inner.SetPosition(1, 1)
		inner.SetColor(fillColor)
		inner.AddFlag("not_pick")
		inner.Show()
		return outer, inner

	def __SizeBorderedBar(self, outer, inner, w, h):
		outer.SetSize(w, h)
		inner.SetSize(w - 2, h - 2)

	def __BuildBox(self):
		(outer, inner) = self.__MakeBorderedBar(self, RES_BOX_FILL)
		self.__SizeBorderedBar(outer, inner, self.BOX_WIDTH, self.BOX_HEIGHT)
		self.boxOuter = outer

		boxText = ui.TextLine()
		boxText.SetParent(self)
		boxText.SetHorizontalAlignLeft()
		boxText.SetPackedFontColor(RES_TEXT_COLOR)
		boxText.AddFlag("not_pick")
		boxText.Show()
		self.boxText = boxText

		arrow = ui.ImageBox()
		arrow.SetParent(self)
		arrow.AddFlag("not_pick")
		arrow.LoadImage(IMG_DIR + "arrow_down.png")
		arrow.Show()
		self.arrow = arrow

		arrowY = (self.BOX_HEIGHT - arrow.GetHeight()) / 2
		if localeinfo.IsARABIC():
			boxText.SetPosition(self.BOX_WIDTH - 20, 4)
			arrow.SetPosition(6, arrowY)
		else:
			boxText.SetPosition(10, 4)
			arrow.SetPosition(self.BOX_WIDTH - arrow.GetWidth() - 6, arrowY)

	def __BuildPopup(self, topBoard):
		popup = ui.Window("TOP_MOST")
		popup.Hide()
		self.popup = popup

		(outer, inner) = self.__MakeBorderedBar(popup, RES_LIST_FILL)
		self.popupOuter = outer
		self.popupInner = inner

		listBox = ResolutionListBox()
		listBox.SetParent(popup)
		listBox.SetPosition(6, 4)
		listBox.SetPickAlways()
		listBox.SetEvent(ui.__mem_func__(self.__OnSelectItem))
		listBox.Show()
		self.listBox = listBox

		scrollBar = ScrollBarNew()
		scrollBar.SetParent(popup)
		scrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		scrollBar.Hide()
		self.scrollBar = scrollBar

		popup.OnRunMouseWheel = ui.__mem_func__(self.__OnWheel)
		listBox.OnRunMouseWheel = ui.__mem_func__(self.__OnWheel)

	def OnMouseLeftButtonUp(self):
		self.__ToggleOpen()
		return True

	def SetSelectEvent(self, event):
		self.selectEvent = event

	def SetResolutions(self, resList, curW, curH):
		self.resList = resList
		self.listBox.ClearItem()
		for i in xrange(len(resList)):
			(w, h) = resList[i]
			self.listBox.InsertItem(i, "%d x %d" % (w, h))

		rows = min(len(resList), self.VISIBLE_ROWS)
		if rows < 1:
			rows = 1
		listH = rows * self.ROW_HEIGHT
		popupW = self.BOX_WIDTH
		listW = popupW - 16
		self.listBox.SetSize(listW, listH)
		self.listBox.SetBasePos(0)
		self.boxText.SetText("%d x %d" % (curW, curH))

		popupH = listH + 8
		self.popup.SetSize(popupW, popupH)
		self.__SizeBorderedBar(self.popupOuter, self.popupInner, popupW, popupH)

		if len(resList) > self.VISIBLE_ROWS:
			self.scrollBar.SetScrollBarSize(listH)
			self.scrollBar.SetMiddleBarSize(float(self.VISIBLE_ROWS) / float(len(resList)))
			self.scrollBar.SetPosition(popupW - 11, 4)
			self.scrollBar.SetPos(0)
			self.scrollBar.Show()
		else:
			self.scrollBar.Hide()

	def __ToggleOpen(self):
		if self.isOpen:
			self.Close()
		else:
			self.Open()

	def Open(self):
		if len(self.resList) == 0:
			return
		(bx, by) = self.GetGlobalPosition()
		self.popup.SetPosition(bx, by + self.GetHeight())
		self.popup.Show()
		self.popup.SetTop()
		self.isOpen = True

	def Close(self):
		self.popup.Hide()
		self.isOpen = False

	def __OnScroll(self):
		total = len(self.resList)
		if total <= self.VISIBLE_ROWS:
			return
		maxBase = total - self.VISIBLE_ROWS
		base = int(round(self.scrollBar.GetPos() * maxBase))
		if base < 0:
			base = 0
		if base > maxBase:
			base = maxBase
		self.listBox.SetBasePos(base)

	def __OnWheel(self, nLen):
		if not self.isOpen:
			return False
		if nLen > 0:
			self.scrollBar.OnUp()
		elif nLen < 0:
			self.scrollBar.OnDown()
		return True

	def __OnSelectItem(self, index, name):
		self.Close()
		if index < 0 or index >= len(self.resList):
			return
		(w, h) = self.resList[index]
		self.boxText.SetText("%d x %d" % (w, h))
		if self.selectEvent:
			self.selectEvent(index)

