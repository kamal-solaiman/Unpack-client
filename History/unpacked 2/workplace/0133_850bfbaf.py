# coding: latin_1

import app

import ime
import grp
import snd
import wndMgr
import item
import skill
import localeinfo
import dbg
# MARK_BUG_FIX
import guild
# END_OF_MARK_BUG_FIX
import renderTarget

from _weakref import proxy
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr

import osfinfo
import player

if app.USE_BONUS_PAGE:
	from operator import truediv
	import math

BACKGROUND_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
DARK_COLOR = grp.GenerateColor(0.2, 0.2, 0.2, 1.0)
BRIGHT_COLOR = grp.GenerateColor(0.7, 0.7, 0.7, 1.0)

if localeinfo.IsCANADA():
	SELECT_COLOR = grp.GenerateColor(0.9, 0.03, 0.01, 0.4)
else:
	# SELECT_COLOR = grp.GenerateColor(0.0, 0.0, 0.5, 0.3)
	SELECT_COLOR = grp.GenerateColor(0.2, 0.0, 0.5, 0.8)

WHITE_COLOR = grp.GenerateColor(1.0, 1.0, 1.0, 0.5)
HALF_WHITE_COLOR = grp.GenerateColor(1.0, 1.0, 1.0, 0.2)
if app.ENABLE_KEYCHANGE_SYSTEM:
	RED_COLOR = grp.GenerateColor(1.0, 0.0, 0.0, 0.5)
	HALF_HALF_RED_COLOR = grp.GenerateColor(1.0, 0.0, 0.0, 0.4)
	HALF_RED_COLOR = grp.GenerateColor(1.0, 0.0, 0.0, 0.3)

DEFAULT_FONT_COLOR = grp.GenerateColor(0.7607, 0.7607, 0.7607, 1.0)
SELECT_FONT_COLOR = 0xff40407a

# Animation presets for window effects (optimized for fast-paced gameplay)
# Easing types: 0=cubic (smooth), 1=back (subtle overshoot), 2=expo (snappy)
ANIMATION_PRESETS = {
	"modal": {
		"scale_start": 0.90,
		"duration": 190,
		"easing": 0,
		"offset_x": 0,
		"offset_y": 10,
	},
	"panel_right": {
		"scale_start": 1.0,
		"duration": 200,
		"easing": 0,
		"offset_x": 30,
		"offset_y": 0,
	},
	"panel_left": {
		"scale_start": 1.0,
		"duration": 200,
		"easing": 0,
		"offset_x": -30,
		"offset_y": 0,
	},
	"dropdown": {
		"scale_start": 0.98,
		"duration": 120,
		"easing": 0,
		"offset_x": 0,
		"offset_y": -10,
	},
	"tooltip": {
		"scale_start": 1.0,
		"duration": 80,
		"easing": 0,
		"offset_x": 0,
		"offset_y": 0,
	},
	"popup": {
		"scale_start": 0.95,
		"duration": 150,
		"easing": 0,
		"offset_x": 0,
		"offset_y": 10,
	},
}

def RegisterAnimationPreset(name, config):
	"""Register a custom animation preset."""
	ANIMATION_PRESETS[name] = config

createToolTipWindowDict = {}
def RegisterCandidateWindowClass(codePage, candidateWindowClass):
	EditLine.candidateWindowClassDict[codePage] = candidateWindowClass
def RegisterToolTipWindow(type, createToolTipWindow):
	createToolTipWindowDict[type] = createToolTipWindow

app.SetDefaultFontName(localeinfo.UI_DEF_FONT)

def calculateRect(curValue, maxValue):
	try:
		return -1.0 + float(curValue) / float(maxValue)
	except:
		return 0.0

## Window Manager Event List##
##############################
## "OnMouseLeftButtonDown"
## "OnMouseLeftButtonUp"
## "OnMouseLeftButtonDoubleClick"
## "OnMouseRightButtonDown"
## "OnMouseRightButtonUp"
## "OnMouseRightButtonDoubleClick"
## "OnMouseDrag"
## "OnSetFocus"
## "OnKillFocus"
## "OnMouseOverIn"
## "OnMouseOverOut"
## "OnRender"
## "OnUpdate"
## "OnKeyDown"
## "OnKeyUp"
## "OnTop"
## "OnIMEUpdate" ## IME Only
## "OnIMETab"	## IME Only
## "OnIMEReturn" ## IME Only
##############################
## Window Manager Event List##


class __mem_func__:
	class __noarg_call__:
		def __init__(self, cls, obj, func):
			self.cls=cls
			self.obj=proxy(obj)
			self.func=proxy(func)

		def __call__(self, *arg):
			return self.func(self.obj)

	class __arg_call__:
		def __init__(self, cls, obj, func):
			self.cls=cls
			self.obj=proxy(obj)
			self.func=proxy(func)

		def __call__(self, *arg):
			return self.func(self.obj, *arg)

	def __init__(self, mfunc):
		if mfunc.im_func.func_code.co_argcount>1:
			self.call=__mem_func__.__arg_call__(mfunc.im_class, mfunc.im_self, mfunc.im_func)
		else:
			self.call=__mem_func__.__noarg_call__(mfunc.im_class, mfunc.im_self, mfunc.im_func)

	def __call__(self, *arg):
		return self.call(*arg)

class Window(object):
	def NoneMethod(cls):
		pass

	NoneMethod = classmethod(NoneMethod)

	def __init__(self, layer = "UI"):
		self.hWnd = None
		self.parentWindow = 0
		self.onMouseLeftButtonUpEvent = None
		if app.ENABLE_WINDOW_RESIZE:
			self.resizeDic = {}
		self.onRunMouseWheelEvent = None
		self.RegisterWindow(layer)

		self.eventDict={}

		self.eventFunc = {"MOUSE_LEFT_BUTTON_DOWN" : None,
							"mouse_click" : None,
							"mouse_over_in" : None,
							"mouse_over_out" : None,
							"MOUSE_RIGHT_BUTTON_UP" : None,
							"MOUSE_RIGHT_BUTTON_DOWN" : None,
							"MOUSE_RIGHT_DOWN" : None,
							"MOUSE_LEFT_DOWN" : None}

		self.eventArgs = {"MOUSE_LEFT_BUTTON_DOWN" : None,
							"mouse_click" : None,
							"mouse_over_in" : None,
							"mouse_over_out" : None,
							"MOUSE_RIGHT_BUTTON_UP" : None,
							"MOUSE_RIGHT_BUTTON_DOWN" : None,
							"MOUSE_RIGHT_DOWN" : None,
							"MOUSE_LEFT_DOWN" : None}

		if app.ENABLE_ULTIMATE_REGEN:
			self.exPos2 = (0, 0)
			self.itsRendered = False
			self.itsNeedDoubleRender = False
			self.sortIndex = 0
		
		if app.ENABLE_ITEMSHOP:
			self.exPos = (0,0)

		self.mouseLeftButtonUpEvent = None
		self.mouseLeftButtonUpArgs = None
		self.mouseLeftButtonDoubleClickEvent = None
		self.mouseRightButtonDownEvent = None
		self.mouseRightButtonDownArgs = None
		self.moveWindowEvent = None
		self.mouseOverInEvent = None
		self.mouseOverInArgs = None
		self.renderEvent = None
		self.renderArgs = None
		self.mouseOverOutEvent = None
		self.mouseOverOutArgs = None

		if app.ENABLE_INGAME_WIKI:
			self.mouseLeftButtonDownEvent = None
			self.mouseLeftButtonDownArgs = None
			self.mouseRightButtonUpEvent = None
			self.mouseRightButtonUpArgs = None
			self.overInEvent = None
			self.overInArgs = None
			self.overOutEvent = None
			self.overOutArgs = None
			self.SetWindowName("NONAME_Window")

		if app.ENABLE_QUEST_RENEWAL:
			self.propertyList = {}

		self.Hide()

	def __del__(self):
		wndMgr.Destroy(self.hWnd)
		self.eventFunc = None
		self.eventArgs = None

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.Register(self, layer)

	def Destroy(self):
		pass

	def GetWindowHandle(self):
		return self.hWnd

	def AddFlag(self, style):
		wndMgr.AddFlag(self.hWnd, style)

	def RemoveFlag(self, style):
		wndMgr.RemoveFlag(self.hWnd, style)

	# Animation configuration methods
	def SetAnimationDuration(self, ms):
		"""Set animation duration in milliseconds (50-1000)."""
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			wndMgr.SetAnimationDuration(self.hWnd, ms)

	def SetAnimationScale(self, startScale, endScale=1.0):
		"""Set animation scale range (0.0-1.0 for start, 0.0-2.0 for end)."""
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			wndMgr.SetAnimationScale(self.hWnd, startScale, endScale)

	def SetAnimationOffset(self, offsetX, offsetY):
		"""Set animation position offset in pixels (-200 to 200)."""
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			wndMgr.SetAnimationOffset(self.hWnd, offsetX, offsetY)

	def SetAnimationEasing(self, easingType):
		"""Set animation easing: 0=cubic (smooth), 1=back (subtle overshoot), 2=expo (snappy)."""
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			wndMgr.SetAnimationEasing(self.hWnd, easingType)

	def SetChildStagger(self, delayMs):
		"""Set stagger delay per child in milliseconds (0-100)."""
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			wndMgr.SetChildStagger(self.hWnd, delayMs)

	def IsAnimating(self):
		"""Check if window is currently animating."""
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			return wndMgr.IsAnimating(self.hWnd)
		return False

	def SetAnimationPreset(self, presetName):
		"""Apply a predefined animation preset by name."""
		if not app.ENABLE_WINDOW_SLIDE_EFFECT:
			return
		if presetName not in ANIMATION_PRESETS:
			return
		preset = ANIMATION_PRESETS[presetName]
		self.SetAnimationScale(preset.get("scale_start", 0.90), preset.get("scale_end", 1.0))
		self.SetAnimationDuration(preset.get("duration", 190))
		self.SetAnimationEasing(preset.get("easing", 0))
		self.SetAnimationOffset(preset.get("offset_x", 0), preset.get("offset_y", 0))

	def OnAnimationComplete(self, isShowAnimation):
		"""Called when window animation completes. Override in subclass to handle."""
		pass

	def IsRTL(self):
		return wndMgr.IsRTL(self.hWnd)

	def SetWindowName(self, Name):
		wndMgr.SetName(self.hWnd, Name)

	def GetWindowName(self):
		return wndMgr.GetName(self.hWnd)

	def SetParent(self, parent):
		wndMgr.SetParent(self.hWnd, parent.hWnd)

	def SetParentProxy(self, parent):
		self.parentWindow=proxy(parent)
		wndMgr.SetParent(self.hWnd, parent.hWnd)

	def SAFE_SetStringEvent(self, event, func, *args):
		self.eventDict[event] =__mem_func__(func)
		self.eventArgs[event] = args

	def GetParentProxy(self):
		return self.parentWindow

	def SetPickAlways(self):
		wndMgr.SetPickAlways(self.hWnd)

	def IsRendering(self):
		return wndMgr.IsRendering(self.hWnd)

	def SetWindowHorizontalAlignLeft(self):
		wndMgr.SetWindowHorizontalAlign(self.hWnd, wndMgr.HORIZONTAL_ALIGN_LEFT)

	def SetWindowHorizontalAlignCenter(self):
		wndMgr.SetWindowHorizontalAlign(self.hWnd, wndMgr.HORIZONTAL_ALIGN_CENTER)

	def SetWindowHorizontalAlignRight(self):
		wndMgr.SetWindowHorizontalAlign(self.hWnd, wndMgr.HORIZONTAL_ALIGN_RIGHT)

	def SetWindowVerticalAlignTop(self):
		wndMgr.SetWindowVerticalAlign(self.hWnd, wndMgr.VERTICAL_ALIGN_TOP)

	def SetWindowVerticalAlignCenter(self):
		wndMgr.SetWindowVerticalAlign(self.hWnd, wndMgr.VERTICAL_ALIGN_CENTER)

	def SetWindowVerticalAlignBottom(self):
		wndMgr.SetWindowVerticalAlign(self.hWnd, wndMgr.VERTICAL_ALIGN_BOTTOM)

	def SetTop(self):
		wndMgr.SetTop(self.hWnd)

	def Show(self):
		wndMgr.Show(self.hWnd)

	def Hide(self):
		wndMgr.Hide(self.hWnd)

	def Lock(self):
		wndMgr.Lock(self.hWnd)

	def Unlock(self):
		wndMgr.Unlock(self.hWnd)

	def IsShow(self):
		return wndMgr.IsShow(self.hWnd)

	def UpdateRect(self):
		wndMgr.UpdateRect(self.hWnd)

	def SetSize(self, width, height):
		wndMgr.SetWindowSize(self.hWnd, width, height)

	def GetWidth(self):
		return wndMgr.GetWindowWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetWindowHeight(self.hWnd)

	def GetLocalPosition(self):
		return wndMgr.GetWindowLocalPosition(self.hWnd)

	def GetLeft(self):
		x, y = self.GetLocalPosition()
		return x

	def GetGlobalLeft(self):
		x, y = self.GetGlobalPosition()
		return x

	def GetTop(self):
		x, y = self.GetLocalPosition()
		return y

	def GetGlobalTop(self):
		x, y = self.GetGlobalPosition()
		return y

	def GetRight(self):
		return self.GetLeft() + self.GetWidth()

	def GetBottom(self):
		return self.GetTop() + self.GetHeight()

	def GetGlobalPosition(self):
		return wndMgr.GetWindowGlobalPosition(self.hWnd)

	def GetMouseLocalPosition(self):
		return wndMgr.GetMouseLocalPosition(self.hWnd)

	def GetRect(self):
		return wndMgr.GetWindowRect(self.hWnd)

	def SetLeft(self, x):
		wndMgr.SetWindowPosition(self.hWnd, x, self.GetTop())

	def SetPosition(self, x, y, flag = False):
		if app.ENABLE_ITEMSHOP:
			if flag == True:
				self.exPos = (x,y)
		wndMgr.SetWindowPosition(self.hWnd, x, y)

	if app.ENABLE_ULTIMATE_REGEN:
		def SetPositionTrack(self, x, y, flag = False):
			if flag == True:
				self.exPos2 = (x, y)
			
			wndMgr.SetWindowPosition(self.hWnd, x, y)

	def SetCenterPosition(self, x = 0, y = 0):
		self.SetPosition((wndMgr.GetScreenWidth() - self.GetWidth()) / 2 + x, (wndMgr.GetScreenHeight() - self.GetHeight()) / 2 + y)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : ((Expr("SCREEN_WIDTH") - self.GetWidth())/2+x, (Expr("SCREEN_HEIGHT") - self.GetHeight())/2+y)})

	def IsFocus(self):
		return wndMgr.IsFocus(self.hWnd)

	def SetFocus(self):
		wndMgr.SetFocus(self.hWnd)

	def KillFocus(self):
		wndMgr.KillFocus(self.hWnd)

	def GetChildCount(self):
		return wndMgr.GetChildCount(self.hWnd)

	def IsInPosition(self):
		xMouse, yMouse = wndMgr.GetMousePosition()
		x, y = self.GetGlobalPosition()
		return xMouse >= x and xMouse < x + self.GetWidth() and yMouse >= y and yMouse < y + self.GetHeight()

	if app.ENABLE_INGAME_WIKI:
		# def IsInPosition(self):
			# xMouse, yMouse = wndMgr.GetMousePosition()
			# x, y = self.GetGlobalPosition()
			# return xMouse >= x and xMouse < x + self.GetWidth() and yMouse >= y and yMouse < y + self.GetHeight()

		def SetMouseLeftButtonDownEvent(self, event, *args):
			self.mouseLeftButtonDownEvent = event
			self.mouseLeftButtonDownArgs = args

		def OnMouseLeftButtonDown(self):
			if self.mouseLeftButtonDownEvent:
				apply(self.mouseLeftButtonDownEvent, self.mouseLeftButtonDownArgs)
			elif self.eventDict.has_key("MOUSE_LEFT_DOWN"):
				apply(self.eventDict["MOUSE_LEFT_DOWN"], self.argDict["MOUSE_LEFT_DOWN"])
			elif self.eventFunc["MOUSE_LEFT_BUTTON_DOWN"] :
				apply(self.eventFunc["MOUSE_LEFT_BUTTON_DOWN"], self.eventArgs["MOUSE_LEFT_BUTTON_DOWN"])

		def SetMouseRightButtonUpEvent(self, event, *args):
			self.mouseRightButtonUpEvent = event
			self.mouseRightButtonUpArgs = args

		def SAFE_SetOverInEvent(self, func, *args):
			self.overInEvent = __mem_func__(func)
			self.overInArgs = args

		def SAFE_SetOverOutEvent(self, func, *args):
			self.overOutEvent = __mem_func__(func)
			self.overOutArgs = args

		def SetOverInEvent(self, func, *args):
			self.overInEvent = func
			self.overInArgs = args

		def SetOverOutEvent(self, func, *args):
			self.overOutEvent = func
			self.overOutArgs = args

		def IsIn(self, checkChilds = False):
			return wndMgr.IsIn(self.hWnd, checkChilds)

		# opop
		# def GetRenderBox(self):
			# return wndMgr.GetRenderBox(self.hWnd)

		def SetInsideRender(self, val, isWheel = False):
			# opop
			# wndMgr.SetInsideRender(self.hWnd, val, isWheel)
			pass

		def OnMouseOverIn(self):
			if self.overInEvent:
				apply(self.overInEvent, self.overInArgs)

		def OnMouseOverOut(self):
			if self.overOutEvent:
				apply(self.overOutEvent, self.overOutArgs)

		def AdjustSize(self):
			x, y = self.GetTextSize()
			wndMgr.SetWindowSize(self.hWnd, x, y)
	else:
		def IsIn(self):
			return wndMgr.IsIn(self.hWnd)

	def SetMouseLeftButtonUpEvent(self, event, *args):
		self.mouseLeftButtonUpEvent = event
		self.mouseLeftButtonUpArgs = args

	def SetMouseOverInEvent(self, event, *args):
		self.mouseOverInEvent = event
		self.mouseOverInArgs = args

	def SetMouseOverOutEvent(self, event, *args):
		self.mouseOverOutEvent = event
		self.mouseOverOutArgs = args

	def SetOnMouseLeftButtonUpEvent(self, event, *args):
		self.onMouseLeftButtonUpEvent = event
		self.onMouseLeftButtonUpEventArgs = args

	def OnMouseLeftButtonUp(self):
		if self.onMouseLeftButtonUpEvent:
			apply(self.onMouseLeftButtonUpEvent, self.onMouseLeftButtonUpEventArgs)
	if app.ENABLE_WINDOW_RESIZE:
		def SetResizeDic(self, dic):
			self.resizeDic.update(dic)

		def OnResize(self):
			if self.resizeDic:
				for k, v in self.resizeDic.items():
					if k == "position":
						self.SetPosition(int(v[0]), int(v[1]))
					elif k == "size":
						self.SetSize(int(v[0]), int(v[1]))
					elif k == "scale":
						wndMgr.SetScale(self.hWnd, float(v[0]), float(v[1]))
					elif k == "rect":
						wndMgr.SetRenderingRect(self.hWnd, float(v[0]), float(v[1]), float(v[2]), float(v[3]))

	def SetMouseLeftButtonDoubleClickEvent(self, event):
		self.mouseLeftButtonDoubleClickEvent = event

	def OnMouseLeftButtonDoubleClick(self):
		if self.mouseLeftButtonDoubleClickEvent:
			self.mouseLeftButtonDoubleClickEvent()

	def SetMouseRightButtonDownEvent(self, event, *args):
		self.mouseRightButtonDownEvent = event
		self.mouseRightButtonDownArgs = args

	def OnMouseRightButtonUp(self):
		if self.mouseRightButtonUpEvent:
			apply(self.mouseRightButtonUpEvent, self.mouseRightButtonUpArgs)
		else:
			try:
				if self.eventFunc["MOUSE_RIGHT_BUTTON_UP"]:
					apply(self.eventFunc["MOUSE_RIGHT_BUTTON_UP"], self.eventArgs["MOUSE_RIGHT_BUTTON_UP"])
			except:
				return

	def OnMouseRightButtonDown(self):
		if self.mouseRightButtonDownEvent:
			apply(self.mouseRightButtonDownEvent, self.mouseRightButtonDownArgs)
		else:
			try:
				if self.eventDict.has_key("MOUSE_RIGHT_DOWN"):
					apply(self.eventDict["MOUSE_RIGHT_DOWN"], self.argDict["MOUSE_RIGHT_DOWN"])
				elif self.eventFunc["MOUSE_RIGHT_BUTTON_DOWN"] :
					apply(self.eventFunc["MOUSE_RIGHT_BUTTON_DOWN"], self.eventArgs["MOUSE_RIGHT_BUTTON_DOWN"])
			except:
				return

	def SetMoveWindowEvent(self, event):
		self.moveWindowEvent = event

	def SAFE_SetRenderEvent(self, event, *args):
		self.renderEvent = __mem_func__(event)
		self.renderArgs = args

	def ClearRenderEvent(self):
		self.renderEvent = None
		self.renderArgs = None

	def OnRender(self):
		if self.renderEvent:
			apply(self.renderEvent, self.renderArgs)

	def OnMoveWindow(self, x, y):
		if self.moveWindowEvent:
			self.moveWindowEvent(x, y)

	def SetOverInEvent(self, func, *args):
		self.overInEvent = func
		self.overInArgs = args

	def SetOverOutEvent(self, func, *args):
		self.overOutEvent = func
		self.overOutArgs = args

	if app.ENABLE_QUEST_RENEWAL:
		def SetProperty(self, propName, propValue):
			self.propertyList[propName] = propValue

		def GetProperty(self, propName):
			if propName in self.propertyList:
				return self.propertyList[propName]
			
			return None

	def SetOnRunMouseWheelEvent(self, event):
		self.onRunMouseWheelEvent = event

	def OnRunMouseWheel(self, nLen):
		if self.onRunMouseWheelEvent:
			apply(self.onRunMouseWheelEvent, (bool(nLen < 0), ))
			return True

		return False

	if app.USE_CLIP_MASK:
		def SetClippingMaskRect(self, left, top, right, bottom):
			wndMgr.SetClippingMaskRect(self.hWnd, left, top, right, bottom)

		def GetClippingMaskRect(self):
			return wndMgr.GetClippingMaskRect(self.hWnd)

		def SetClippingMaskWindow(self, clipping_mask_window):
			wndMgr.SetClippingMaskWindow(self.hWnd, clipping_mask_window.hWnd)

		def SetSubClippingMaskWindow(self, clipping_mask_window):
			wndMgr.SetSubClippingMaskWindow(self.hWnd, clipping_mask_window.hWnd)

class InvisibleBoard(Window):
	CORNER_WIDTH = 32
	CORNER_HEIGHT = 32
	LINE_WIDTH = 128
	LINE_HEIGHT = 128

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3


	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.skipMaxCheck = False

		self.MakeBoard()
		
	def MakeBoard(self):
		self.Corners = []
		self.Lines = []
		self.Base = None

	def __del__(self):
		Window.__del__(self)

	def SetSize(self, width, height):
		if not self.skipMaxCheck:
			width = max(self.CORNER_WIDTH*2, width)
			height = max(self.CORNER_HEIGHT*2, height)
			
		Window.SetSize(self, width, height)

class ListBoxNew(Window):
	def __del__(self):
		Window.__del__(self)
	def Destroy(self):
		for item in self.itemList:
			item.Destroy()
		self.itemList=[]
		self.scrollBar=None
		self.basePos=0
		self.scrollLen=0
		self.scrollLenExtra=0
		self.isHorizontal= 0
	def __init__(self, isHorizontal = False):
		Window.__init__(self)
		self.itemList=[]
		self.Destroy()
		self.isHorizontal= isHorizontal
	def RemoveAllItems(self):
		for item in self.itemList:
			item.Destroy()
		self.itemList=[]
		if self.scrollBar:
			self.scrollBar.SetPos(0)
		self.RefreshAll()
	def SetExtraScrollLen(self, extraLen):
		self.scrollLenExtra=extraLen
	def GetItems(self):
		return self.itemList
	def AppendItem(self, newItem):
		self.itemList.append(newItem)
	def SetScrollBar(self, scrollBar):
		scrollBar.SetScrollEvent(__mem_func__(self.__OnScroll))
		self.scrollBar=scrollBar
	def OnMouseWheel(self, nLen):
		if self.scrollBar:
			if self.scrollBar.IsShow():
				if nLen > 0:
					self.scrollBar.OnUp()
				else:
					self.scrollBar.OnDown()
				return True
		return False
	def __OnScroll(self):
		self.SetBasePos(int(self.scrollBar.GetPos()*self.scrollLen))
	def RefreshAll(self):
		windowHeight = self.GetHeight()
		scrollBar = self.scrollBar
		screenSize = 0
		for child in self.itemList:
			if child.exPos[1] > screenSize:
				screenSize = child.exPos[1]
		if screenSize > windowHeight:
			scrollLen = screenSize-windowHeight
			if scrollLen != 0:
				scrollLen += self.scrollLenExtra
			self.scrollLen = scrollLen
			scrollBar.SetMiddleBarSize(float(windowHeight-5)/float(screenSize))
		else:
			scrollBar.SetMiddleBarSize(1.0)
	def Render(self,basePos):
		for item in self.itemList:
			(ex,ey) = item.exPos
			if self.isHorizontal:
				item.SetPosition(ex-(basePos), ey)
			else:
				item.SetPosition(ex, ey-(basePos))
			item.OnRender()
	def SetBasePos(self, basePos):
		if self.basePos == basePos:
			return
		self.Render(basePos)
		self.basePos=basePos

if app.ENABLE_ULTIMATE_REGEN:
	class ListBoxNew2(Window):
		def __del__(self):
			Window.__del__(self)

		def Destroy(self):
			for item in self.itemList:
				item.Destroy()

			self.itemList = []
			self.scrollBar = None
			self.basePos = 0

			self.scrollLen = 0
			self.scrollLenExtra = 0
			self.isHorizontal = 0

		def __init__(self, isHorizontal = False):
			Window.__init__(self)

			self.itemList = []
			self.Destroy()

			self.scrollBar = None
			self.basePos = 0

			self.scrollLen = 0
			self.scrollLenExtra = 0
			self.isHorizontal = 0

		def RemoveAllItems(self):
			for item in self.itemList:
				item.Destroy()
				del item

			self.itemList = []

			if self.scrollBar:
				self.scrollBar.SetPos(0)

			self.RefreshAll()

		def SetExtraScrollLen(self, extraLen):
			self.scrollLenExtra = extraLen

		def GetItems(self):
			return self.itemList

		def AppendItem(self, newItem):
			self.itemList.append(newItem)

		def SetScrollBar(self, scrollBar):
			scrollBar.SetScrollEvent(__mem_func__(self.__OnScroll))
			self.scrollBar = scrollBar

		def OnMouseWheel(self, nLen):
			if self.scrollBar:
				if self.scrollBar.IsShow():
					if nLen > 0:
						self.scrollBar.OnUp()
					else:
						self.scrollBar.OnDown()

					return True

			return False

		def __OnScroll(self):
			self.SetBasePos(int(self.scrollBar.GetPos() * self.scrollLen))

		def RefreshAll(self):
			windowHeight = self.GetHeight()
			scrollBar = self.scrollBar
			screenSize = 0

			j = 0
			for child in self.itemList:
				j += 1
				child.exPos = child.GetGlobalPosition()
				if child.GetGlobalPosition()[1] > screenSize:
					screenSize = child.exPos[1]

			if screenSize > windowHeight:
				scrollLen = screenSize - windowHeight

				if scrollLen != 0:
					scrollLen += self.scrollLenExtra

				self.scrollLen = scrollLen
				self.scrollBar.SetMiddleBarSize(float(3) / j)
				# scrollBar.SetMiddleBarSize(float(3) / float(j))
				# scrollBar.SetMiddleBarSize(float(windowHeight - 5) / float(screenSize))
			else:
				scrollBar.SetMiddleBarSize(1.0)

		def Render(self, basePos):
			for item in self.itemList:
				(ex, ey) = item.exPos2

				if self.isHorizontal:
					item.SetPosition(ex - (basePos), ey)
				else:
					item.SetPosition(ex, ey - (basePos))

				item.OnRender()

		def SetBasePos(self, basePos):
			if self.basePos == basePos:
				return

			self.Render(basePos)
			self.basePos = basePos

if app.ENABLE_BIOLOG_SYSTEM:
	class CheckBox_Biolog(Window):

		STATE_UNSELECTED = 0
		STATE_SELECTED = 1

		def __init__(self, layer = "UI"):
			Window.__init__(self, layer)

			self.state = self.STATE_UNSELECTED
			self.eventFunc = None
			self.eventArgs = None

			self.overIn = ""

			self.btnBox = {
				self.STATE_UNSELECTED : self.__init_MakeButton("d:/ymir work/ui/checkbox/checkbox_new_unselected.tga"),
				self.STATE_SELECTED : self.__init_MakeButton("d:/ymir work/ui/checkbox/checkbox_new_selected.tga", "d:/ymir work/ui/checkbox/checkbox_new_selected.tga"),
			}

			text = TextLine()
			text.SetParent(self)
			text.SetWindowVerticalAlignCenter()
			text.SetVerticalAlignCenter()
			text.SetHorizontalAlignRight()
			text.Show()
			self.text = text

			self.__Refresh()

			self.SetWindowName("NONAME_CheckBox")

		def __del__(self):
			Window.__del__(self)

		def __ConvertPath(self, path, subStr):
			if path.find("%s") != -1:
				return path % subStr
			else:
				return path

		def __init_MakeButton(self, path, disablePath = None):
			btn = Button()
			btn.SetParent(self)
			btn.SetWindowVerticalAlignCenter()
			btn.SetUpVisual(self.__ConvertPath(path, "01"))
			btn.SetOverVisual(self.__ConvertPath(path, "02"))
			btn.SetDownVisual(self.__ConvertPath(path, "03"))
			if disablePath:
				btn.SetDisableVisual(disablePath)
			else:
				btn.SetDisableVisual(self.__ConvertPath(path, "01"))
			btn.SAFE_SetEvent(self.OnClickButton)
			btn.baseWidth = btn.GetWidth()
			return btn

		def __UpdateRect(self):
			if self.text.GetText():
				width = self.btnBox[self.state].baseWidth + 5 + self.text.GetTextWidth()
			else:
				width = self.btnBox[self.state].baseWidth
			height = max(self.btnBox[self.state].GetHeight(), self.text.GetTextHeight())
			self.SetSize(width, height)

			self.btnBox[self.state].SetSize(width, self.btnBox[self.state].GetHeight())
			self.text.SetPosition(self.btnBox[self.state].baseWidth + 5, 0)

			self.text.UpdateRect()
			self.btnBox[self.state].UpdateRect()
			self.UpdateRect()

		def __Refresh(self):
			self.__UpdateRect()

			self.btnBox[self.STATE_UNSELECTED].SetVisible(self.state == self.STATE_UNSELECTED)
			self.btnBox[self.STATE_SELECTED].SetVisible(self.state == self.STATE_SELECTED)

		def SAFE_SetOverInData(self, data):
			self.btnBox[self.state].SetToolTipText(data)

		def OnClickButton(self):
			if self.state == self.STATE_UNSELECTED:
				self.state = self.STATE_SELECTED
			else:
				self.state = self.STATE_UNSELECTED

			self.__Refresh()

			if self.eventFunc:
				apply(self.eventFunc, self.eventArgs)

		def SetChecked(self, state):
			self.state = state
			self.__Refresh()

		def IsChecked(self):
			return self.state != self.STATE_UNSELECTED

		def SetText(self, text):
			self.text.SetText(text)
			self.__UpdateRect()

		def SetEvent(self, event, *args):
			self.eventFunc = event
			self.eventArgs = args

		def SAFE_SetEvent(self, event, *args):
			self.eventFunc = __mem_func__(event)
			self.eventArgs = args

		def Disable(self):
			self.btnBox[self.STATE_UNSELECTED].Disable()
			self.btnBox[self.STATE_SELECTED].Disable()

		def Enable(self):
			self.btnBox[self.STATE_UNSELECTED].Enable()
			self.btnBox[self.STATE_SELECTED].Enable()

	class BoxedBoard(Window):
		BORDER_TOP = 0
		BORDER_RIGHT = 1
		BORDER_BOTTOM = 2
		BORDER_LEFT = 3
		
		DEFAULT_BORDER_COLOR = grp.GenerateColor(0.3, 0.3, 0.3, 1.0)
		DEFAULT_BASE_COLOR = grp.GenerateColor(0, 0, 0, 0.5)
		
		def __init__(self):
			Window.__init__(self)
			
			self.borderSize = 1
			
			# Create Borders
			self.borders = [
				Bar(),
				Bar(),
				Bar(),
				Bar()
			]
			
			for border in self.borders:
				border.SetParent(self)
				border.AddFlag("not_pick")
				border.Show()
			
			# Create Base
			self.base = Bar()
			self.base.SetParent(self)
			self.base.AddFlag("not_pick")
			self.base.Show()
			
			# Set Default Colors
			self.SetBorderColor(self.DEFAULT_BORDER_COLOR)
			self.SetBaseColor(self.DEFAULT_BASE_COLOR)
		
		def __del__(self):
			self.Destroy()
			Window.__del__(self)
		
		def Destroy(self):
			del self.borders[:]
			self.base = None
			
			Window.Destroy(self)
		
		def SetBorderColor(self, color):
			for border in self.borders:
				border.SetColor(color)
		
		def SetBorderSize(self, borderSize):
			self.borderSize = borderSize
			self.SetSize(self.GetWidth(), self.GetHeight())
		
		def SetBaseColor(self, color):
			self.base.SetColor(color)
		
		def SetSize(self, width, height):
			width = max(width, (2 * self.borderSize) + 1)
			height = max(height, (2 * self.borderSize) + 1)
			
			Window.SetSize(self, width, height)
			self.UpdateBoard()
		
		def UpdateBoard(self):
			width = self.GetWidth()
			height = self.GetHeight()
			
			top, right, bottom, left = self.borders
			
			# Top Border
			top.SetSize(width - self.borderSize, self.borderSize)
			
			# Right Border
			right.SetSize(self.borderSize, height - self.borderSize)
			right.SetPosition(width - self.borderSize, 0)
			
			# Bottom Border
			bottom.SetSize(width - self.borderSize, self.borderSize)
			bottom.SetPosition(self.borderSize, height - self.borderSize)
			
			# Left Border
			left.SetSize(self.borderSize, height - self.borderSize)
			left.SetPosition(0, self.borderSize)
			
			# Base
			self.base.SetSize(width - (2 * self.borderSize), height - (2 * self.borderSize))
			self.base.SetPosition(self.borderSize, self.borderSize)

class ListBoxEx(Window):
	class Item(Window):
		def __init__(self):
			Window.__init__(self)

		def __del__(self):
			Window.__del__(self)

		def SetParent(self, parent):
			Window.SetParent(self, parent)
			self.parent=proxy(parent)

		def OnMouseLeftButtonDown(self):
			self.parent.SelectItem(self)

		def OnRender(self):
			if self.parent.GetSelectedItem()==self:
				self.OnSelectedRender()

		def OnSelectedRender(self):
			x, y = self.GetGlobalPosition()
			grp.SetColor(grp.GenerateColor(0.0, 0.0, 0.7, 0.7))
			grp.RenderBar(x, y, self.GetWidth(), self.GetHeight())

	def __init__(self):
		Window.__init__(self)

		self.viewItemCount = 10
		self.basePos = 0
		self.itemHeight = 16
		self.itemStep = 20
		self.isGuildStatistics=False
		self.selItem = 0
		self.itemList=[]
		self.onSelectItemEvent = lambda *arg: None

		if localeinfo.IsARABIC():
			self.itemWidth = 130
		else:
			self.itemWidth = 100

		self.scrollBar = None
		self.__UpdateSize()

	def __del__(self):
		Window.__del__(self)

	def __UpdateSize(self):
		height = self.itemStep * self.__GetViewItemCount()

		self.SetSize(self.itemWidth, height)

	def IsEmpty(self):
		if len(self.itemList) == 0:
			return 1
		return 0

	def SAFE_SetSelectEvent(self, event):
		self.selectEvent=__mem_func__(event)
	
	def SetGuildLogStatistics(self):
		self.isGuildStatistics = True

	def SetItemStep(self, itemStep):
		self.itemStep = itemStep
		self.__UpdateSize()

	def SetItemSize(self, itemWidth, itemHeight):
		self.itemWidth = itemWidth
		self.itemHeight = itemHeight
		self.__UpdateSize()

	def SetViewItemCount(self, viewItemCount):
		self.viewItemCount = viewItemCount

	def SetSelectEvent(self, event):
		self.onSelectItemEvent = event

	def SetBasePos(self, basePos):
		for oldItem in self.itemList[self.basePos:self.basePos + self.viewItemCount]:
			oldItem.Hide()

		self.basePos = basePos

		pos = basePos
		for newItem in self.itemList[self.basePos : self.basePos + self.viewItemCount]:
			(x, y) = self.GetItemViewCoord(pos, newItem.GetWidth())
			newItem.SetPosition(x, y)
			newItem.Show()
			pos += 1

	def GetItemIndex(self, argItem):
		return self.itemList.index(argItem)

	def GetSelectedItem(self):
		return self.selItem

	def SelectIndex(self, index):
		if index >= len(self.itemList) or index < 0:
			self.selItem = None
			return

		try:
			self.selItem = self.itemList[index]
		except:
			pass

	# def SelectItem(self, selItem):
		# self.selItem = selItem
		# self.onSelectItemEvent(selItem)

	def SelectItem(self, selItem):
		if self.isGuildStatistics:
			if self.selItem:
				self.selItem.UnSelectedRender()

		self.selItem=selItem
		self.onSelectItemEvent(selItem)

		if self.isGuildStatistics:
			if self.selItem:
				self.selItem.OnSelectedRender()

	def RemoveAllItems(self):
		self.selItem = None
		self.itemList = []

		if self.scrollBar:
			self.scrollBar.SetPos(0)

	if app.ENABLE_SWITCHBOT:
		def GetItems(self):
			return self.itemList

	def RemoveItem(self, delItem):
		if delItem == self.selItem:
			self.selItem = None

		self.itemList.remove(delItem)

	def AppendItem(self, newItem):
		newItem.SetParent(self)
		newItem.SetSize(self.itemWidth, self.itemHeight)

		pos = len(self.itemList)
		if self.__IsInViewRange(pos):
			(x, y) = self.GetItemViewCoord(pos, newItem.GetWidth())
			newItem.SetPosition(x, y)
			newItem.Show()
		else:
			newItem.Hide()

		self.itemList.append(newItem)

	def AjustScrollBarPos(self):
		self.SetBasePos(self.__GetScrollLen())
		self.scrollBar.SetPos(1.0)
	def SetScrollBar(self, scrollBar):
		scrollBar.SetScrollEvent(__mem_func__(self.__OnScroll))
		self.scrollBar = scrollBar


	def UpdateScrollBarSize(self):
		lenList = self.__GetItemCount()
		maxView = self.__GetViewItemCount()
		
		if maxView == 0:
			return
		
		middlesizebar = 1.0
		if lenList > maxView:
			middlesizebar = float(maxView)/lenList
		
		if middlesizebar < 0.1:
			middlesizebar = 0.1
		
		self.scrollBar.SetMiddleBarSize(min(float(middlesizebar), 0.985))

	def __OnScroll(self):
		self.SetBasePos(int(self.scrollBar.GetPos() * self.__GetScrollLen()))

	def __GetScrollLen(self):
		scrollLen = self.__GetItemCount() - self.__GetViewItemCount()
		if scrollLen < 0:
			return 0

		return scrollLen

	def __GetViewItemCount(self):
		return self.viewItemCount

	def __GetItemCount(self):
		return len(self.itemList)

	if app.ENABLE_INGAME_WIKI:
		def GetItemCount(self):
			return len(self.itemList)

	def GetItemViewCoord(self, pos, itemWidth):
		if localeinfo.IsARABIC():
			return (self.GetWidth() - itemWidth - 10, (pos-self.basePos) * self.itemStep)
		else:
			return (0, (pos - self.basePos) * self.itemStep)

	def __IsInViewRange(self, pos):
		if pos < self.basePos:
			return 0

		if pos >= self.basePos + self.viewItemCount:
			return 0

		return 1

class CandidateListBox(ListBoxEx):

	HORIZONTAL_MODE = 0
	VERTICAL_MODE = 1

	class Item(ListBoxEx.Item):
		def __init__(self, text):
			ListBoxEx.Item.__init__(self)

			self.textBox=TextLine()
			self.textBox.SetParent(self)
			self.textBox.SetText(text)
			self.textBox.Show()

		def __del__(self):
			ListBoxEx.Item.__del__(self)

	def __init__(self, mode = HORIZONTAL_MODE):
		ListBoxEx.__init__(self)
		self.itemWidth=32
		self.itemHeight=32
		self.mode = mode

	def __del__(self):
		ListBoxEx.__del__(self)

	def SetMode(self, mode):
		self.mode = mode

	def AppendItem(self, newItem):
		ListBoxEx.AppendItem(self, newItem)

	def GetItemViewCoord(self, pos):
		if self.mode == self.HORIZONTAL_MODE:
			return ((pos-self.basePos)*self.itemStep, 0)
		elif self.mode == self.VERTICAL_MODE:
			return (0, (pos-self.basePos)*self.itemStep)

class TextLine(Window):
	def __init__(self, font = None):
		Window.__init__(self)
		self.max = 0
		if font == None:
			self.SetFontName(localeinfo.UI_DEF_FONT)
		else:
			self.SetFontName(font)

		if app.USE_GRAPHIC_TEXT_SEARCH_BOX_WIDTH_LIMIT:
			self.box_limited = False

	def __del__(self):
		if app.USE_GRAPHIC_TEXT_SEARCH_BOX_WIDTH_LIMIT:
			self.box_limited = None

		Window.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterTextLine(self, layer)

	if app.ENABLE_ULTIMATE_REGEN:
		def SetRenderingRect(self, left, top, right, bottom):
			wndMgr.SetRenderingRect(self.hWnd, left, top, right, bottom)

	# opop
	# if app.ENABLE_INGAME_WIKI:
		# def GetRenderPos(self):
			# return wndMgr.GetRenderPos(self.hWnd)

		# def SetFixedRenderPos(self, startPos, endPos):
			# wndMgr.SetFixedRenderPos(self.hWnd, startPos, endPos)

	def SetMax(self, max):
		self.max = max
		wndMgr.SetMax(self.hWnd, self.max)
		ime.SetMax(self.max)
		self.SetUserMax(self.max)

	def SetMaxSizeMode(self, forceWidht = -1):
		self.max_size = self.GetWidth() if forceWidht == -1 else forceWidht

	def SetUserMax(self, max):
		self.userMax = max
		ime.SetUserMax(self.userMax)

	def SetLimitWidth(self, width):
		wndMgr.SetLimitWidth(self.hWnd, width)

	def SetMultiLine(self):
		wndMgr.SetMultiLine(self.hWnd, True)

	if app.USE_CTEXTLINE_AUTO_WRAP:
		def SetAutoWrap(self, _flag):
			wndMgr.SetTextAutoWrap(self.hWnd, _flag)

		def GetAutoWrapLinesCount(self):
			return wndMgr.GetTextAutoWrapLinesCount(self.hWnd)

	def SetHorizontalAlignArabic(self):
		wndMgr.SetHorizontalAlign(self.hWnd, wndMgr.TEXT_HORIZONTAL_ALIGN_ARABIC)

	def SetHorizontalAlignLeft(self):
		wndMgr.SetHorizontalAlign(self.hWnd, wndMgr.TEXT_HORIZONTAL_ALIGN_LEFT)

	def SetHorizontalAlignRight(self):
		wndMgr.SetHorizontalAlign(self.hWnd, wndMgr.TEXT_HORIZONTAL_ALIGN_RIGHT)

	def SetHorizontalAlignCenter(self):
		wndMgr.SetHorizontalAlign(self.hWnd, wndMgr.TEXT_HORIZONTAL_ALIGN_CENTER)

	def SetVerticalAlignTop(self):
		wndMgr.SetVerticalAlign(self.hWnd, wndMgr.TEXT_VERTICAL_ALIGN_TOP)

	def SetVerticalAlignBottom(self):
		wndMgr.SetVerticalAlign(self.hWnd, wndMgr.TEXT_VERTICAL_ALIGN_BOTTOM)

	def SetVerticalAlignCenter(self):
		wndMgr.SetVerticalAlign(self.hWnd, wndMgr.TEXT_VERTICAL_ALIGN_CENTER)

	def SetSecret(self, Value=True):
		wndMgr.SetSecret(self.hWnd, Value)

	def SetOutline(self, Value=True):
		wndMgr.SetOutline(self.hWnd, Value)

	def SetFeather(self, value=True):
		wndMgr.SetFeather(self.hWnd, value)

	def SetFontName(self, fontName):
		wndMgr.SetFontName(self.hWnd, fontName)

	def SetDefaultFontName(self):
		wndMgr.SetFontName(self.hWnd, localeinfo.UI_DEF_FONT)

	def SetFontColor(self, red, green, blue):
		wndMgr.SetFontColor(self.hWnd, red, green, blue)

	def SetPackedFontColor(self, color):
		wndMgr.SetFontColor(self.hWnd, color)

	def SetText(self, text):
		wndMgr.SetText(self.hWnd, text)

	def GetText(self):
		return wndMgr.GetText(self.hWnd)

	def GetTextSize(self):
		return wndMgr.GetTextSize(self.hWnd)

	def GetTextWidth(self):
		w, h = self.GetTextSize()
		return w

	def GetTextHeight(self):
		w, h = self.GetTextSize()
		return h
		
	def AdjustSize(self):
		x, y = self.GetTextSize()
		wndMgr.SetWindowSize(self.hWnd, x, y)

	def GetRight(self):
		return self.GetLeft() + self.GetTextWidth()

	def GetBottom(self):
		return self.GetTop() + self.GetTextHeight()
		
	def SetCenter(self):
		wndMgr.SetWindowPosition(self.hWnd, self.GetLeft() - self.GetTextWidth()/2, self.GetTop())

	if app.__RENEWAL_BRAVE_CAPE__:
		def SetAllAlign(self):
			self.SetWindowHorizontalAlignCenter()
			self.SetWindowVerticalAlignCenter()
			self.SetHorizontalAlignCenter()
			self.SetVerticalAlignCenter()

	if app.USE_GRAPHIC_TEXT_SEARCH_BOX_WIDTH_LIMIT:
		def SetSearchBoxLimitWidth(self, width):
			self.box_limited = True
			wndMgr.SetSearchBoxLimitWidth(self.hWnd, width)

class EmptyCandidateWindow(Window):
	def __init__(self):
		Window.__init__(self)

	def __del__(self):
		Window.__del__(self)

	def Load(self):
		pass

	def SetCandidatePosition(self, x, y, textCount):
		pass

	def Clear(self):
		pass

	def Append(self, text):
		pass

	def Refresh(self):
		pass

	def Select(self):
		pass

class EditLine(TextLine):
	candidateWindowClassDict = {}

	def __init__(self):
		TextLine.__init__(self)

		self.eventReturn = Window.NoneMethod
		self.eventUpdate = Window.NoneMethod
		self.eventEscape = Window.NoneMethod
		self.eventUpdateArgs = None
		self.eventReturnArgs = None
		self.eventEscapeArgs = None
		self.eventSelect = None 
		self.backgroundText = TextLine()
		self.backgroundText.SetParent(self)
		self.backgroundText.SetPosition(100, 0)
		self.backgroundText.SetPackedFontColor(WHITE_COLOR)
		self.backgroundText.Hide()
		
		self.eventTab = None
		self.numberMode = False
		self.UseCodePage = True
		self.useIME = True

		self.bCodePage = False

		self.infoMsg = ""
		self.backText = None
		self.isNeedEmpty = True

		self.candidateWindowClass = None
		self.candidateWindow = None
		self.SetCodePage(app.GetDefaultCodePage())

		self.readingWnd = ReadingWnd()
		self.readingWnd.Hide()

		if app.ENABLE_INGAME_WIKI:
			self.eventUpdate = None
			
			self.overLay = TextLine()
			self.overLay.SetParent(self)
			if localeinfo.IsARABIC():
				self.overLay.SetHorizontalAlignLeft()
				self.overLay.SetPosition(0, 0)
			else:
				self.overLay.SetPosition(0, 0)
			self.overLay.SetPackedFontColor(WHITE_COLOR)
			self.overLay.Hide()

		self.placeHolder = TextLine()
		self.placeHolder.SetParent(self)
		self.placeHolder.SetText("")
		self.placeHolder.SetHorizontalAlignRight()
		self.placeHolder.Hide()

		self.update_event = None
		self.update_event_args = None
		
		self.CanClick = None

		self.max_size = -1
		self.last_text = ""

	def __del__(self):
		TextLine.__del__(self)

		self.eventReturn = Window.NoneMethod
		self.eventUpdate = Window.NoneMethod
		self.eventEscape = Window.NoneMethod
		
		self.eventUpdateArgs = None
		self.eventReturnArgs = None
		self.eventEscapeArgs = None
		self.backgroundText = None
		self.eventSelect = None
		self.eventTab = None
		self.CanClick = None
		
		self.placeHolder = None

		self.max_size = -1
		self.last_text = ""

	def SetCodePage(self, codePage):
		candidateWindowClass=EditLine.candidateWindowClassDict.get(codePage, EmptyCandidateWindow)
		self.__SetCandidateClass(candidateWindowClass)

	def SetInfoMessage(self, msg):
		self.infoMsg = msg
		if self.backText == None:
			self.backText = TextLine()
			self.backText.SetParent(self)
			self.backText.SetPosition(0,0)
			self.backText.SetFontColor(128,128,128)

		self.backText.SetText(msg)

		if self.isNeedEmpty:
			if len(self.GetText()) > 0:
				self.backText.Hide()
			else:
				self.backText.Show()
		else:
			self.backText.Show()

	def __SetCandidateClass(self, candidateWindowClass):
		if self.candidateWindowClass==candidateWindowClass:
			return

		self.candidateWindowClass = candidateWindowClass
		self.candidateWindow = self.candidateWindowClass()
		self.candidateWindow.Load()
		self.candidateWindow.Hide()

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterTextLine(self, layer)

	def SAFE_SetReturnEvent(self, event):
		self.eventReturn = __mem_func__(event)		
		self.eventReturnArgs = args

	def SetReturnEvent(self, event, *args):
		self.eventReturn = event
		self.eventReturnArgs = args

	def SetEscapeEvent(self, event, *args):
		self.eventEscape = event
		self.eventEscapeArgs = args

	def SetTabEvent(self, event, *args):
		self.eventTab = event
		self.eventArgs = args

	if app.ENABLE_INGAME_WIKI:
		def SetOverlayText(self, text):
			self.overLay.SetText(text)
			self.__RefreshOverlay()

		def SetOverlayTextAE(self, text):
			self.overLay.SetText(text)
			self.overLay.SetPosition(-25,0)
			self.__RefreshOverlay()

		def SetOverlayTextNew(self, text):
			self.overLay.SetText(text)
			self.overLay.SetPosition(90,0)
			self.__RefreshOverlay()

		def SetOverlayCoupon(self, text,x):
			self.overLay.SetText(text)
			self.overLay.SetPosition(x,0)
			self.__RefreshOverlay()

		def GetOverlayText(self):
			return self.overLay.GetText()

		def SetUpdateEvent(self, event):
			self.eventUpdate = event

		def GetDisplayText(self):
			if len(self.GetText()):
				return self.GetText()
			else:
				return self.overLay.GetText()

		def __RefreshOverlay(self):
			if len(self.GetText()):
				self.overLay.Hide()
			else:
				self.overLay.Show()

		def IsShowCursor(self):
			return wndMgr.IsShowCursor(self.hWnd)

	def SetBackgroundText(self, text):
		self.backgroundText.SetText(text)
		
		if not self.backgroundText.IsShow():
			self.backgroundText.Show()
		
	def GetBackgroundText(self):
		return self.backgroundText.GetText()

	def SetMax(self, max):
		self.max = max
		wndMgr.SetMax(self.hWnd, self.max)
		ime.SetMax(self.max)
		self.SetUserMax(self.max)
	
	def SetMaxSizeMode(self, forceWidht = -1):
		self.max_size = self.GetWidth() if forceWidht == -1 else forceWidht

	def SetUserMax(self, max):
		self.userMax = max
		ime.SetUserMax(self.userMax)

	def SetNumberMode(self):
		self.numberMode = True

	def SetSelectEvent(self, event):
		self.eventSelect = event

	def CanEdit(self, flag):
		self.CanClick = flag

	def SetUseCodePage(self, bUse = True):
		self.UseCodePage = bUse

	#def AddExceptKey(self, key):
	#	ime.AddExceptKey(key)

	#def ClearExceptKey(self):
	#	ime.ClearExceptKey()

	def SetIMEFlag(self, flag):
		self.useIME = flag

	def SetText(self, text):
		wndMgr.SetText(self.hWnd, text)
		if self.IsFocus():
			ime.SetText(text)
		
		if app.ENABLE_INGAME_WIKI:
			self.__RefreshOverlay()
		
		self.UpdatePlaceHolder()

	#PlaceHolder funcs
	def UpdatePlaceHolder(self):
		self.placeHolder.Show() if len(self.GetText()) <= 0 and self.CheckPlaceHolder() is True else self.placeHolder.Hide()

	def SetPlaceHolder(self, placeHolderText, placeHolderPos = (0, 0)):
		if not self.placeHolder:
			return
		
		self.placeHolder.SetText(placeHolderText)
		self.placeHolder.SetPosition(*placeHolderPos)
		self.UpdatePlaceHolder()
	
	def SetPlaceHolderColor(self, color):
		if not self.placeHolder:
			return
		
		self.placeHolder.SetPackedFontColor(color)

	def CheckPlaceHolder(self):
		return bool(len(self.placeHolder.GetText())) #return true or false
	##



	def Enable(self):
		wndMgr.ShowCursor(self.hWnd)

	def Disable(self):
		wndMgr.HideCursor(self.hWnd)

	def SetEndPosition(self):
		ime.MoveEnd()

	def CanEdit(self, flag):
		self.CanClick = flag

	def OnSetFocus(self):
		Text = self.GetText()
		ime.SetText(Text)
		ime.SetMax(self.max)
		ime.SetUserMax(self.userMax)
		ime.SetCursorPosition(-1)
		if self.numberMode:
			ime.SetNumberMode()
		else:
			ime.SetStringMode()
		ime.EnableCaptureInput()
		if self.useIME:
			ime.EnableIME()
		else:
			ime.DisableIME()

		wndMgr.ShowCursor(self.hWnd, True)

		self.UpdatePlaceHolder()

	def OnKillFocus(self):
		self.SetText(ime.GetText(self.bCodePage))
		self.OnIMECloseCandidateList()
		self.OnIMECloseReadingWnd()
		ime.DisableIME()
		ime.DisableCaptureInput()
		wndMgr.HideCursor(self.hWnd)

		self.UpdatePlaceHolder()

	def OnIMEChangeCodePage(self):
		self.SetCodePage(ime.GetCodePage())

	def OnIMEOpenCandidateList(self):
		self.candidateWindow.Show()
		self.candidateWindow.Clear()
		self.candidateWindow.Refresh()

		gx, gy = self.GetGlobalPosition()
		self.candidateWindow.SetCandidatePosition(gx, gy, len(self.GetText()))

		return True

	def OnIMECloseCandidateList(self):
		self.candidateWindow.Hide()
		return True

	def OnIMEOpenReadingWnd(self):
		gx, gy = self.GetGlobalPosition()
		textlen = len(self.GetText())-2
		reading = ime.GetReading()
		readinglen = len(reading)
		self.readingWnd.SetReadingPosition( gx + textlen*6-24-readinglen*6, gy )
		self.readingWnd.SetText(reading)
		if ime.GetReadingError() == 0:
			self.readingWnd.SetTextColor(0xffffffff)
		else:
			self.readingWnd.SetTextColor(0xffff0000)
		self.readingWnd.SetSize(readinglen * 6 + 4, 19)
		self.readingWnd.Show()
		return True

	def OnIMECloseReadingWnd(self):
		self.readingWnd.Hide()
		return True

	def IsNumber(self, text) :
		try :
			int(text)
			return True
		except ValueError :
			return False

	def IsIncludeCodePage(self, text) :
		textLen = len(text)
		idx = 0

		while(idx < textLen) :
			n = text.find("@", idx)

			if n == -1 :
				break
			elif n+4 < textLen and self.IsNumber(text[n+1:n+4]) == True:
				return True
			else:
				idx = n + 1

		return False

	def CheckMaxSize(self):
		if self.max_size == -1:
			return False
		
		if self.GetTextSize()[0] > self.max_size and\
			len(self.last_text) < len(ime.GetText(self.bCodePage)):
			return True
		
		return False


	def OnIMEUpdate(self):
		# MT-679 ?? ?? ???? CodePage ??
		if self.UseCodePage == False and self.IsIncludeCodePage(ime.GetText(self.bCodePage)) == True :
			ime.SetText("")

		if self.CheckMaxSize(): #Verifica se pode ou n? escrever o carater
			ime.SetText(self.last_text)

		snd.PlaySound("sound/ui/type.wav")
		
		TextLine.SetText(self, ime.GetText(self.bCodePage))

		if self.backText:
			if self.isNeedEmpty:
				if len(self.GetText()) > 0:
					self.backText.Hide()
				else:
					self.backText.Show()
			else:
				self.backText.Show()

		if app.ENABLE_INGAME_WIKI:
			self.__RefreshOverlay()
			
			if self.eventUpdate:
				self.eventUpdate()
		
		self.last_text = ime.GetText(self.bCodePage) #Atribui o ultimo texto escrito
		
		self.UpdatePlaceHolder()
		self.OnUpdateEvent()
	
	def SAFE_SetUpdateEvent(self, event, *args):
		self.eventUpdate = __mem_func__(event)		
		self.eventUpdateArgs = args
		
	def SetUpdateEvent(self, event, *args):
		self.eventUpdate = event
		self.eventUpdateArgs = args
	
	def OnUpdateEvent(self):
		if self.eventUpdate:
			if self.eventUpdateArgs:
				apply(self.eventUpdate, self.eventUpdateArgs)
			else:
				self.eventUpdate()
	
	def OnIMETab(self):
		if self.eventTab:
			self.eventTab()
			return True

		return False

	def OnIMEReturn(self):
		snd.PlaySound("sound/ui/click.wav")
		if self.eventReturn:
			if self.eventReturnArgs:
				apply(self.eventReturn, self.eventReturnArgs)
			else:
				self.eventReturn()

		return True

	def OnPressEscapeKey(self):
		if self.eventEscape:
			if self.eventEscapeArgs:
				apply(self.eventEscape, self.eventEscapeArgs)
			else:
				self.eventEscape()
		return True
	
	def OnKeyDown(self, key):
		if app.DIK_F1 == key:
			return False
		if app.DIK_F2 == key:
			return False
		if app.DIK_F3 == key:
			return False
		if app.DIK_F4 == key:
			return False
		if app.DIK_F5 == key:
			return False
		if app.DIK_F6 == key:
			return False
		if app.DIK_F7 == key:
			return False
		if app.DIK_F8 == key:
			return False
		if app.DIK_F9 == key:
			return False
		if app.DIK_F10 == key:
			return False
		if app.DIK_F11 == key:
			return False
		if app.DIK_F12 == key:
			return False
		if app.DIK_LALT == key:
			return False
		if app.DIK_SYSRQ == key:
			return False
		if app.DIK_LCONTROL == key:
			return False
		if app.DIK_V == key:
			if app.IsPressed(app.DIK_LCONTROL):
				ime.PasteTextFromClipBoard()

		return True

	def OnKeyUp(self, key):
		if app.DIK_F1 == key:
			return False
		if app.DIK_F2 == key:
			return False
		if app.DIK_F3 == key:
			return False
		if app.DIK_F4 == key:
			return False
		if app.DIK_LALT == key:
			return False
		if app.DIK_SYSRQ == key:
			return False
		if app.DIK_LCONTROL == key:
			return False

		return True

	def OnIMEKeyDown(self, key):
		# Left
		if app.VK_LEFT == key:
			ime.MoveLeft()
			return True
		# Right
		if app.VK_RIGHT == key:
			ime.MoveRight()
			return True

		# Home
		if app.VK_HOME == key:
			ime.MoveHome()
			return True
		# End
		if app.VK_END == key:
			ime.MoveEnd()
			return True

		# Delete
		if app.VK_DELETE == key:
			ime.Delete()
			TextLine.SetText(self, ime.GetText(self.bCodePage))
			return True

		return True
	
	def UpdateHolderPosition(self):
		init = 0
		text_lenght = len(self.GetText())
		while (init < text_lenght):
			ime.MoveRight()
			init += 1

	def OnMouseLeftButtonDown(self):
		if False == self.IsIn():
			return False

		if False == self.CanClick:
			return False

		self.SetFocus()

		if app.USE_GRAPHIC_TEXT_SEARCH_BOX_WIDTH_LIMIT and self.box_limited == True:
			ime.SetCursorPosition(-1)
		else:
			PixelPosition = wndMgr.GetCursorPosition(self.hWnd)
			ime.SetCursorPosition(PixelPosition)

if app.__COOL_REFRESH_EDITLINE__:
	class CoolRefreshTextLine(TextLine):
		def __del__(self):
			TextLine.__del__(self)
		def Destroy(self):
			self.currentValue = 0
			self.newValue = 0
			self.valueRange = 0
			self.status = False
			self.perSize = 0
			self.MAX_LOOP_COUNT = 0
		def __init__(self):
			TextLine.__init__(self)
			self.Destroy()
			self.SetWindowName("CoolRefreshTextLine")
			self.MAX_LOOP_COUNT = 15
		def SetText(self, newValue):
			self.newValue = int(newValue)
			if self.newValue != self.currentValue:
				self.status = True
				self.valueRange = self.newValue - self.currentValue
				self.perSize = 0
			else:
				self.status = False
				self.currentValue = newValue
				TextLine.SetText(self, localeinfo.MoneyFormat(self.currentValue))
		def OnUpdateCool(self):
			if self.status == True:
				if self.newValue > self.currentValue:
					self.currentValue += int(math.floor(float(self.valueRange)/float(self.MAX_LOOP_COUNT)))
				else:
					self.currentValue -= int(math.floor(float(self.valueRange)/float(self.MAX_LOOP_COUNT)))
				self.perSize += 1
				if self.perSize > self.MAX_LOOP_COUNT:
					self.currentValue = self.newValue
					self.status = False
				TextLine.SetText(self, localeinfo.MoneyFormat(self.currentValue))


class MarkBox(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

	def __del__(self):
		Window.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterMarkBox(self, layer)

	def Load(self):
		wndMgr.MarkBox_Load(self.hWnd)

	def SetScale(self, scale):
		wndMgr.MarkBox_SetScale(self.hWnd, scale)

	def SetIndex(self, guildID):
		MarkID = guild.GuildIDToMarkID(guildID)
		wndMgr.MarkBox_SetImageFilename(self.hWnd, guild.GetMarkImageFilenameByMarkID(MarkID))
		wndMgr.MarkBox_SetIndex(self.hWnd, guild.GetMarkIndexByMarkID(MarkID))

	def SetAlpha(self, alpha):
		wndMgr.MarkBox_SetDiffuseColor(self.hWnd, 1.0, 1.0, 1.0, alpha)

class ImageBoxOld(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.eventDict={}
		# Tooltip Extend Addition
		self.eventFunc = { #@M2NewsCode006
			"MOUSE_LEFT_BUTTON_UP" : None, 
			"MOUSE_LEFT_BUTTON_DOWN" : None, 
			"MOUSE_RIGHT_BUTTON_UP" : None, 
			"MOUSE_RIGHT_BUTTON_DOWN" : None, 
			"MOUSE_OVER_IN" : None, 
			"MOUSE_OVER_OUT" : None
		}
		self.eventArgs = { #@M2NewsCode006
			"MOUSE_LEFT_BUTTON_UP" : None, 
			"MOUSE_LEFT_BUTTON_DOWN" : None, 
			"MOUSE_RIGHT_BUTTON_UP" : None, 
			"MOUSE_RIGHT_BUTTON_DOWN" : None, 
			"MOUSE_OVER_IN" : None, 
			"MOUSE_OVER_OUT" : None
		}
		# Tooltip Extend Addition

	def __del__(self):
		Window.__del__(self)
		# Tooltip Extend Addition
		self.eventFunc = None #@M2NewsCode006
		self.eventArgs = None #@M2NewsCode006
		# Tooltip Extend Addition

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterImageBox(self, layer)

	def LoadImage(self, imageName):
		self.name=imageName
		wndMgr.LoadImage(self.hWnd, imageName)
		# if len(self.eventDict)!=0:
			# print "LOAD IMAGE", self, self.eventDict

	def SetAlpha(self, alpha):
		wndMgr.SetDiffuseColor(self.hWnd, 1.0, 1.0, 1.0, alpha)

	def SetColor(self, r, g, b, a): #@M2NewsCode005
		wndMgr.SetDiffuseColor(self.hWnd, r, g, b, a)

	def GetWidth(self):
		return wndMgr.GetWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetHeight(self.hWnd)

	# Tooltip Extend Addition
	def SetEvent(self, func, *args) : #@M2NewsCode006
		result = self.eventFunc.has_key(args[0])
		if result :
			self.eventFunc[args[0]] = func
			self.eventArgs[args[0]] = args
		else :
			print "[ERROR] ui.py SetEvent, Can`t Find has_key : %s" % args[0]

	def SAFE_SetEvent(self, func, *args): #@M2NewsCode006
		result = self.eventFunc.has_key(args[0])
		if result :
			self.eventFunc[args[0]] = __mem_func__(func)
			self.eventArgs[args[0]] = args
		else :
			print "[ERROR] ui.py SAFE_SetEvent, Can`t Find has_key : %s" % args[0]

	def OnMouseLeftButtonUp(self): #@M2NewsCode006
		if self.eventFunc["MOUSE_LEFT_BUTTON_UP"] :
			apply(self.eventFunc["MOUSE_LEFT_BUTTON_UP"], self.eventArgs["MOUSE_LEFT_BUTTON_UP"])

	def OnMouseLeftButtonDown(self): #@M2NewsCode006
		if self.eventFunc["MOUSE_LEFT_BUTTON_DOWN"] :
			apply(self.eventFunc["MOUSE_LEFT_BUTTON_DOWN"], self.eventArgs["MOUSE_LEFT_BUTTON_DOWN"])

	def OnMouseRightButtonUp(self): #@M2NewsCode006
		if self.eventFunc["MOUSE_RIGHT_BUTTON_UP"] :
			apply(self.eventFunc["MOUSE_RIGHT_BUTTON_UP"], self.eventArgs["MOUSE_RIGHT_BUTTON_UP"])

	def OnMouseOverIn(self):
		try:
			#@M2NewsCode006
			args = self.eventArgs.get("MOUSE_OVER_IN", None)
			if not args:
				self.eventDict["MOUSE_OVER_IN"]()
			else:
				apply(self.eventDict["MOUSE_OVER_IN"], args)
			#@M2NewsCode006

			#self.eventDict["MOUSE_OVER_IN"]()#@M2NewsCode006
		except KeyError:
			pass

	def OnMouseOverOut(self):
		try:
			#@M2NewsCode006
			args = self.eventArgs.get("MOUSE_OVER_OUT", None)
			if not args:
				self.eventDict["MOUSE_OVER_OUT"]()
			else:
				apply(self.eventDict["MOUSE_OVER_OUT"], args)
			#@M2NewsCode006

			#self.eventDict["MOUSE_OVER_OUT"]() #@M2NewsCode006
		except KeyError:
			pass

	# def SAFE_SetStringEvent(self, event, func): #@M2NewsCode006
		# self.eventDict[event]=__mem_func__(func)

	def SAFE_SetStringEvent(self, event, func, *args): #@M2NewsCode006
		self.eventDict[event] =__mem_func__(func)
		self.eventArgs[event] = args

	def SetOnMouseLeftButtonUpEvent(self, event, *args): #@M2NewsCode006
		self.eventFunc["MOUSE_LEFT_BUTTON_UP"] = event
		self.eventArgs["MOUSE_LEFT_BUTTON_UP"] = args
	# Tooltip Extend Addition

class ImageBox(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.eventDict = {}
		self.argDict = {}
		self.eventFunc = {"MOUSE_LEFT_BUTTON_DOWN" : None, "mouse_click" : None, "mouse_over_in" : None, "mouse_over_out" : None, "MOUSE_RIGHT_BUTTON_UP" : None,"MOUSE_RIGHT_BUTTON_DOWN" : None}
		self.eventArgs = {"MOUSE_LEFT_BUTTON_DOWN" : None, "mouse_click" : None, "mouse_over_in" : None, "mouse_over_out" : None, "MOUSE_RIGHT_BUTTON_UP" : None,"MOUSE_RIGHT_BUTTON_DOWN" : None}
		if app.ENABLE_ITEMSHOP:
			self.eventDictIS = {}
			self.eventArgsIS = {}

	def __del__(self):
		Window.__del__(self)
		self.eventDict = None
		self.argDict = None
		self.eventFunc = None
		self.eventArgs = None
		if app.ENABLE_ITEMSHOP:
			self.eventDictIS = None
			self.eventArgsIS = None

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterImageBox(self, layer)

	def LoadImage(self, imageName):
		self.name=imageName
		wndMgr.LoadImage(self.hWnd, imageName)

		if len(self.eventDict)!=0:
			print "LOAD IMAGE", self, self.eventDict

	if app.ENABLE_INGAME_WIKI:
		def UnloadImage(self):
			wndMgr.UnloadImage(self.hWnd)

	def SetAlpha(self, alpha):
		wndMgr.SetDiffuseColor(self.hWnd, 1.0, 1.0, 1.0, alpha)

	# if app.ENABLE_FISHING_GAME:
		# def SetDiffuseColor(self, r, g, b, alpha = 1.0):
			# wndMgr.SetDiffuseColor(self.hWnd, r, g, b, alpha)

	if app.ENABLE_SWITCHBOT:
		def SetSwitchBotIconColor(self):
			wndMgr.SetDiffuseColor(self.hWnd, (79.0/255.0), (79.0/255.0),(79.0/255.0), 1.0)
	
	def SetDiffuseColor(self, r, g, b, a = 1.0):
		wndMgr.SetDiffuseColor(self.hWnd, r, g, b, a)	
	
	def GetWidth(self):
		return wndMgr.GetWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetHeight(self.hWnd)

	if app.ENABLE_INGAME_WIKI:
		def SetStringEvent(self, event, func, *args):
			self.eventDict[event] = func
			self.argDict[event] = args

		def OnMouseLeftButtonDown(self):
			if self.eventDict.has_key("MOUSE_LEFT_DOWN"):
				apply(self.eventDict["MOUSE_LEFT_DOWN"], self.argDict["MOUSE_LEFT_DOWN"])
			elif self.eventFunc["MOUSE_LEFT_BUTTON_DOWN"]:
				apply(self.eventFunc["MOUSE_LEFT_BUTTON_DOWN"], self.eventArgs["MOUSE_LEFT_BUTTON_DOWN"])

	def OnMouseRightButtonUp(self):
		if self.mouseRightButtonUpEvent:
			apply(self.mouseRightButtonUpEvent, self.mouseRightButtonUpArgs)
		elif self.eventFunc["MOUSE_RIGHT_BUTTON_UP"] :
			apply(self.eventFunc["MOUSE_RIGHT_BUTTON_UP"], self.eventArgs["MOUSE_RIGHT_BUTTON_UP"])

	def OnMouseRightButtonDown(self):
		if self.mouseRightButtonDownEvent:
			apply(self.mouseRightButtonDownEvent, self.mouseRightButtonDownArgs)
		elif self.eventDict.has_key("MOUSE_RIGHT_DOWN"):
			apply(self.eventDict["MOUSE_RIGHT_DOWN"], self.argDict["MOUSE_RIGHT_DOWN"])
		elif self.eventFunc["MOUSE_RIGHT_BUTTON_DOWN"] :
			apply(self.eventFunc["MOUSE_RIGHT_BUTTON_DOWN"], self.eventArgs["MOUSE_RIGHT_BUTTON_DOWN"])

	def SAFE_SetStringEvent(self, event, func, *args):
		self.eventDict[event] =__mem_func__(func)
		self.eventArgs[event] = args

	if app.ENABLE_ITEMSHOP:
		def ITEMSHOP_SetStringEvent(self, event, func, *args):
			self.eventDictIS[event] = __mem_func__(func)
			self.eventArgsIS[event] = args

	def SetEvent(self, func, *args):
		result = self.eventFunc.has_key(args[0])
		if result:
			self.eventFunc[args[0]] = func
			self.eventArgs[args[0]] = args
		else:
			print "[ERROR] ui.py SetEvent, Can`t Find has_key : %s" % args[0]

	def SAFE_SetEvent(self, func, *args): #@M2NewsCode006
		result = self.eventFunc.has_key(args[0])
		if result :
			self.eventFunc[args[0]] = __mem_func__(func)
			self.eventArgs[args[0]] = args
		else :
			print "[ERROR] ui.py SAFE_SetEvent, Can`t Find has_key : %s" % args[0]

	def OnMouseLeftButtonUp(self) :
		Window.OnMouseLeftButtonUp(self)
		if self.eventFunc["mouse_click"]:
			apply(self.eventFunc["mouse_click"], self.eventArgs["mouse_click"])

	def OnMouseOverIn(self):
		try:
			if app.ENABLE_ITEMSHOP and self.eventDictIS.has_key("MOUSE_OVER_IN"):
				if self.eventArgsIS.has_key("MOUSE_OVER_IN"):
					apply(self.eventDictIS["MOUSE_OVER_IN"], self.eventArgsIS["MOUSE_OVER_IN"])
				else:
					self.eventDictIS["MOUSE_OVER_IN"]()

				return

			if self.eventDict.has_key("MOUSE_OVER_IN"):
				if self.argDict.has_key("MOUSE_OVER_IN"):
					apply(self.eventDict["MOUSE_OVER_IN"], self.argDict["MOUSE_OVER_IN"])
				elif self.eventArgs.has_key("MOUSE_OVER_IN"):
					apply(self.eventDict["MOUSE_OVER_IN"], self.eventArgs["MOUSE_OVER_IN"])
				else:
					self.eventDict["MOUSE_OVER_IN"]()

				return

			if self.eventFunc["mouse_over_in"]:
				apply(self.eventFunc["mouse_over_in"], self.eventArgs["mouse_over_in"])
		except KeyError:
			pass

	def OnMouseOverOut(self):
		try:
			if app.ENABLE_ITEMSHOP and self.eventDictIS.has_key("MOUSE_OVER_OUT"):
				if self.eventArgsIS.has_key("MOUSE_OVER_OUT"):
					apply(self.eventDictIS["MOUSE_OVER_OUT"], self.eventArgsIS["MOUSE_OVER_OUT"])
				else:
					self.eventDictIS["MOUSE_OVER_OUT"]()

				return

			if self.eventDict.has_key("MOUSE_OVER_OUT"):
				if self.argDict.has_key("MOUSE_OVER_OUT"):
					apply(self.eventDict["MOUSE_OVER_OUT"], self.argDict["MOUSE_OVER_OUT"])
				elif self.eventArgs.has_key("MOUSE_OVER_OUT"):
					apply(self.eventDict["MOUSE_OVER_OUT"], self.eventArgs["MOUSE_OVER_OUT"])
				else:
					self.eventDict["MOUSE_OVER_OUT"]()

				return

			if self.eventFunc["mouse_over_out"]:
				apply(self.eventFunc["mouse_over_out"], self.eventArgs["mouse_over_out"])
		except KeyError:
			pass

	def LeftRightReverse(self):
		wndMgr.LeftRightReverseImageBox(self.hWnd)

	def SetCoolTime(self, time):
		wndMgr.SetCoolTimeImageBox(self.hWnd, time)

	def SetStartCoolTime(self, time):
		wndMgr.SetStartCoolTimeImageBox(self.hWnd, time)

class ExpandedImageBox(ImageBox):
	def __init__(self, layer = "UI"):
		ImageBox.__init__(self, layer)
		if not app.ENABLE_INGAME_WIKI:
			self.eventDict={}
			self.argDict={}

	def __del__(self):
		ImageBox.__del__(self)

	def SetDiffuseColor(self, r, g, b, a):
		wndMgr.SetDiffuseColor(self.hWnd, r, g, b, a)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterExpandedImageBox(self, layer)

	def SetScale(self, xScale, yScale):
		wndMgr.SetScale(self.hWnd, xScale, yScale)

	def SetOrigin(self, x, y):
		wndMgr.SetOrigin(self.hWnd, x, y)

	def SetRotation(self, rotation):
		wndMgr.SetRotation(self.hWnd, rotation)

	def SetRenderingMode(self, mode):
		wndMgr.SetRenderingMode(self.hWnd, mode)

	if not app.ENABLE_INGAME_WIKI:
		def OnMouseOverIn(self):
			try:
				if self.eventDictIS["MOUSE_OVER_IN"]:
					if self.eventArgsIS:
						apply(self.eventDictIS["MOUSE_OVER_IN"], self.eventArgsIS["MOUSE_OVER_IN"])
					else:
						self.eventDictIS["MOUSE_OVER_IN"]()
			except KeyError:
				pass

		def OnMouseOverOut(self):
			try:
				if self.eventDictIS["MOUSE_OVER_OUT"]:
					if self.eventArgsIS:
						apply(self.eventDictIS["MOUSE_OVER_OUT"], self.eventArgsIS["MOUSE_OVER_OUT"])
					else:
						self.eventDictIS["MOUSE_OVER_OUT"]()
			except KeyError:
				pass

		def SetStringEvent(self, event, func, *args):
			self.eventDict[event] = func
			self.argDict[event] = args

		def SAFE_SetStringEvent(self, event, func,isa=FALSE):
			if not isa:
				self.eventDict[event]=mem_func(func)
			else:
				self.eventDict[event]=func

	def SetRenderingRect(self, left, top, right, bottom):
		wndMgr.SetRenderingRect(self.hWnd, left, top, right, bottom)

	if app.ENABLE_IMAGE_CLIP_RECT or app.ENABLE_EXTENDED_BATTLE_PASS:
		def SetClipRect(self, left, top, right, bottom, isVertical = False):
			wndMgr.SetClipRect(self.hWnd, left, top, right, bottom, isVertical)

	if app.ENABLE_EXTENDED_BATTLE_PASS:
		def SetPercentageEx(self, minValue, curValue, maxValue):
			if minValue and maxValue:
				self.SetRenderingRect(0.0, 0.0, -1.0 + (float(curValue) - float(minValue)) / (float(maxValue) - float(minValue)), 0.0)
			else:
				self.SetRenderingRect(0.0, 0.0, 0.0, 0.0)

	def SetPercentage(self, curValue, maxValue):
		if maxValue:
			self.SetRenderingRect(0.0, 0.0, -1.0 + float(curValue) / float(maxValue), 0.0)
		else:
			self.SetRenderingRect(0.0, 0.0, 0.0, 0.0)
	def SetPercentageDown(self, curValue, maxValue):
		if maxValue:
			self.SetRenderingRect(0.0, 0.0, 0.0, -1.0 + float(curValue) / float(maxValue))
		else:
			self.SetRenderingRect(0.0, 0.0, 0.0, 0.0)
	def GetWidth(self):
		return wndMgr.GetWindowWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetWindowHeight(self.hWnd)

class AniImageBox(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

		self.end_frame_event = None
		self.key_frame_event = None

		if app.ENABLE_MINI_GAME_CATCH_KING:
			self.end_frame_args = None

	def __del__(self):
		self.end_frame_event = None
		self.key_frame_event = None

		if app.ENABLE_MINI_GAME_CATCH_KING:
			self.end_frame_args = None

		Window.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterAniImageBox(self, layer)

	# def SetRotation(self, rotation):
		# wndMgr.SetRotationAni(self.hWnd, rotation)

	def SetDelay(self, delay):
		wndMgr.SetDelay(self.hWnd, delay)

	if app.ENABLE_FISHING_GAME:
		def SetRotation(self, rotation):
			wndMgr.SetRotation(self.hWnd, rotation)

	def AppendImage(self, filename):
		wndMgr.AppendImage(self.hWnd, filename)

	if app.ENABLE_IMAGE_SCALE:
		def AppendImageScale(self, filename, scale_x, scale_y):
			wndMgr.AppendImageScale(self.hWnd, filename, scale_x, scale_y)

	def SetPercentage(self, curValue, maxValue):
		wndMgr.SetRenderingRect(self.hWnd, 0.0, 0.0, -1.0 + float(curValue) / float(maxValue), 0.0)

	def SetPercentageWithScale(self, curValue, maxValue):
		wndMgr.SetRenderingRectWithScale(self.hWnd, 0.0, 0.0, -1.0 + float(curValue) / float(maxValue), 0.0)

	def SetScale(self, xScale, yScale):
		wndMgr.SetAniImgScale(self.hWnd, xScale, yScale)

	def ClearImages(self):
		wndMgr.ClearImages(self.hWnd)

	def SetPercentageReverse(self, curValue, maxValue):
		wndMgr.SetRenderingRect(self.hWnd,-1.0 + float(curValue) / float(maxValue), 0.0, 0.0, 0.0)

	if app.ENABLE_MINI_GAME_CATCH_KING:
		def OnEndFrame(self):
			if self.end_frame_event:
				apply(self.end_frame_event, self.end_frame_args)
	else:
		def OnEndFrame(self):
			if self.end_frame_event:
				self.end_frame_event()

	if app.ENABLE_MINI_GAME_CATCH_KING:
		def SetEndFrameEvent(self, event, *args):
			self.end_frame_event = event
			self.end_frame_args = args
	else:
		def SetEndFrameEvent(self, event):
			self.end_frame_event = event

	def ResetFrame(self):
		wndMgr.ResetFrame(self.hWnd)

	def OnKeyFrame(self, cur_frame):
		if self.key_frame_event:
			self.key_frame_event(cur_frame)

	def SetKeyFrameEvent(self, event):
		self.key_frame_event = event

class AniImageBoxButton(AniImageBox):
	"""
	AniImageBox with button-like interactivity (click, hover events).
	Use this when you need an animated image that responds to mouse input.

	Performance note: For animations with many frames, consider:
	- Using a higher delay value (SetDelay) to reduce frame rate
	- Reducing the number of frames if possible
	- Using OnEndFrame to pause animation when appropriate
	"""
	def __init__(self, layer = "UI"):
		AniImageBox.__init__(self, layer)
		# Event handlers
		self.clickEventFunc = None
		self.clickEventArgs = ()
		self.eventFunc = {
			"MOUSE_OVER_IN": None,
			"MOUSE_OVER_OUT": None,
			"MOUSE_LEFT_BUTTON_DOWN": None,
			"MOUSE_LEFT_BUTTON_UP": None,
		}
		self.eventArgs = {
			"MOUSE_OVER_IN": (),
			"MOUSE_OVER_OUT": (),
			"MOUSE_LEFT_BUTTON_DOWN": (),
			"MOUSE_LEFT_BUTTON_UP": (),
		}
		# Visual state tracking
		self.isMouseOver = False
		self.isMouseDown = False

	def __del__(self):
		self.clickEventFunc = None
		self.clickEventArgs = None
		self.eventFunc = None
		self.eventArgs = None
		AniImageBox.__del__(self)

	def SetEvent(self, func, eventType="MOUSE_CLICK"):
		"""
		Set event handler for various mouse events.

		eventType can be:
		- "MOUSE_CLICK" or "mouse_click": Click event (button up after button down)
		- "MOUSE_OVER_IN": Mouse enters the widget
		- "MOUSE_OVER_OUT": Mouse leaves the widget
		- "MOUSE_LEFT_BUTTON_DOWN": Mouse button pressed
		- "MOUSE_LEFT_BUTTON_UP": Mouse button released
		"""
		if eventType in ("MOUSE_CLICK", "mouse_click"):
			self.clickEventFunc = func
			self.clickEventArgs = ()
		elif eventType in self.eventFunc:
			self.eventFunc[eventType] = func
			self.eventArgs[eventType] = ()

	def SetEventArgs(self, eventType, *args):
		"""Set arguments for an event handler."""
		if eventType in ("MOUSE_CLICK", "mouse_click"):
			self.clickEventArgs = args
		elif eventType in self.eventArgs:
			self.eventArgs[eventType] = args

	def OnMouseOverIn(self):
		self.isMouseOver = True
		try:
			if self.eventFunc["MOUSE_OVER_IN"]:
				apply(self.eventFunc["MOUSE_OVER_IN"], self.eventArgs["MOUSE_OVER_IN"])
		except Exception:
			pass

	def OnMouseOverOut(self):
		self.isMouseOver = False
		self.isMouseDown = False
		try:
			if self.eventFunc["MOUSE_OVER_OUT"]:
				apply(self.eventFunc["MOUSE_OVER_OUT"], self.eventArgs["MOUSE_OVER_OUT"])
		except Exception:
			pass

	def OnMouseLeftButtonDown(self):
		self.isMouseDown = True
		try:
			if self.eventFunc["MOUSE_LEFT_BUTTON_DOWN"]:
				apply(self.eventFunc["MOUSE_LEFT_BUTTON_DOWN"], self.eventArgs["MOUSE_LEFT_BUTTON_DOWN"])
		except Exception:
			pass

	def OnMouseLeftButtonUp(self):
		# Only trigger click if mouse is still over the button
		wasDown = self.isMouseDown
		self.isMouseDown = False

		try:
			if self.eventFunc["MOUSE_LEFT_BUTTON_UP"]:
				apply(self.eventFunc["MOUSE_LEFT_BUTTON_UP"], self.eventArgs["MOUSE_LEFT_BUTTON_UP"])
		except Exception:
			pass

		# Click event only fires if button was pressed AND mouse is still over
		if wasDown and self.isMouseOver:
			try:
				if self.clickEventFunc:
					apply(self.clickEventFunc, self.clickEventArgs)
			except Exception:
				pass

class MoveImageBox(ImageBox):
	def __init__(self, layer = "UI"):
		ImageBox.__init__(self, layer)
		self.end_move_event = None
		if app.ENABLE_MINI_GAME_BNW:
			self.argsEndMove = None

	def __del__(self):
		ImageBox.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterMoveImageBox(self, layer)

	def MoveStart(self):
		wndMgr.MoveStart(self.hWnd)
	def MoveStop(self):
		wndMgr.MoveStop(self.hWnd)
	def GetMove(self):
		return wndMgr.GetMove(self.hWnd)

	def SetMovePosition(self, dst_x, dst_y):
		wndMgr.SetMovePosition(self.hWnd, dst_x, dst_y)

	def SetMoveSpeed(self, speed):
		wndMgr.SetMoveSpeed(self.hWnd, speed)

	def SetEndMoveEvent(self, event, *args):
		self.eventEndMove = event
		self.argsEndMove = args

	def OnEndMove(self):
		if self.end_move_event:
			if app.ENABLE_MINI_GAME_BNW:
				apply(self.end_move_event, self.argsEndMove)
			else:
				self.end_move_event()

	if app.ENABLE_MINI_GAME_BNW:
		def SetEndMoveEvent(self, event, *args):
			self.end_move_event = event
			self.argsEndMove = args
	else:
		def SetEndMoveEvent(self, event):
			self.end_move_event = event

class MoveTextLine(TextLine):
	def __init__(self):
		TextLine.__init__(self)
		self.end_move_event_func = None
		self.end_move_event_args = None

	def __del__(self):
		TextLine.__del__(self)
		self.end_move_event_func = None
		self.end_move_event_args = None

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterMoveTextLine(self, layer)

	def SetMovePosition(self, dst_x, dst_y):
		wndMgr.SetMovePosition(self.hWnd, dst_x, dst_y)

	def SetMoveSpeed(self, speed):
		wndMgr.SetMoveSpeed(self.hWnd, speed)

	def MoveStart(self):
		wndMgr.MoveStart(self.hWnd)

	def MoveStop(self):
		wndMgr.MoveStop(self.hWnd)

	def GetMove(self):
		return wndMgr.GetMove(self.hWnd)

	def OnEndMove(self):
		if self.end_move_event_func:
			apply(self.end_move_event_func, self.end_move_event_args)

	def SetEndMoveEvent(self, event, *args):
		self.end_move_event_func = event
		self.end_move_event_args = args

	def SetMoveAll(self, flag):
		wndMgr.SetMoveAll(self.hWnd, flag)

class MoveScaleImageBox(MoveImageBox):
	def __init__(self, layer = "UI"):
		MoveImageBox.__init__(self, layer)

	def __del__(self):
		MoveImageBox.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterMoveScaleImageBox(self, layer)

	def SetMaxScale(self, scale):
		wndMgr.SetMaxScale(self.hWnd, scale)

	def SetMaxScaleRate(self, pivot):
		wndMgr.SetMaxScaleRate(self.hWnd, pivot)

	def SetScalePivotCenter(self, flag):
		wndMgr.SetScalePivotCenter(self.hWnd, flag)

	def SetMoveAll(self, flag):
		wndMgr.SetMoveAll(self.hWnd, flag)

class Button(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.eventFunc = None
		self.eventArgs = None

		self.ButtonText = None
		self.ToolTipText = None

		self.TextChild = []

		# if app.USE_DUNGEON_COOLDOWN_MANAGER:
		self.overFunc = None
		self.overArgs = None
		self.overOutFunc = None
		self.overOutArgs = None

		self.showtooltipevent = None
		self.showtooltiparg = None
		self.hidetooltipevent = None
		self.hidetooltiparg = None
		self.tooltipHided = 0

		self.eventOverInFunc = None
		self.eventOverInArgs = None
		
		self.eventOverOutFunc = None
		self.eventOverOutArgs = None

	def SetFontName(self, fontName):
		wndMgr.SetFontName(self.hWnd, fontName)

	def __del__(self):
		Window.__del__(self)

		self.eventFunc = None
		self.eventArgs = None

		# if app.USE_DUNGEON_COOLDOWN_MANAGER:
		self.overFunc = None
		self.overArgs = None
		self.overOutFunc = None
		self.overOutArgs = None

		self.tooltipHided = 0

	if app.ENABLE_BIOLOG_SYSTEM:
		def SetVisible(self, flag):
			if flag:
				self.Show()
			else:
				self.Hide()

	def SetEventOverIn(self, func, *args):
		self.eventOverInFunc = func
		self.eventOverInArgs = args
	
	def SetEventOverOut(self, func, *args):
		self.eventOverOutFunc = func
		self.eventOverOutArgs = args

	if app.ENABLE_GAMEOPTION_RENEWAL:
		def SetRenderingRect(self, left, top, right, bottom):
			wndMgr.SetRenderingRect(self.hWnd, left, top, right, bottom)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterButton(self, layer)

	def SetUpVisual(self, filename):
		wndMgr.SetUpVisual(self.hWnd, filename)

	def SetOverVisual(self, filename):
		wndMgr.SetOverVisual(self.hWnd, filename)

	def SetDownVisual(self, filename):
		wndMgr.SetDownVisual(self.hWnd, filename)

	def SetDisableVisual(self, filename):
		wndMgr.SetDisableVisual(self.hWnd, filename)

	def GetUpVisualFileName(self):
		return wndMgr.GetUpVisualFileName(self.hWnd)

	def GetOverVisualFileName(self):
		return wndMgr.GetOverVisualFileName(self.hWnd)

	def GetDownVisualFileName(self):
		return wndMgr.GetDownVisualFileName(self.hWnd)

	def Flash(self):
		wndMgr.Flash(self.hWnd)

	def EnableFlash(self):
		wndMgr.EnableFlash(self.hWnd)

	def DisableFlash(self):
		wndMgr.DisableFlash(self.hWnd)

	def EnableHoverPulse(self):
		wndMgr.EnableHoverPulse(self.hWnd)

	def DisableHoverPulse(self):
		wndMgr.DisableHoverPulse(self.hWnd)

	def SetHoverPulseSpeed(self, speed):
		wndMgr.SetHoverPulseSpeed(self.hWnd, speed)

	def SetHoverPulseAlpha(self, minAlpha, maxAlpha):
		wndMgr.SetHoverPulseAlpha(self.hWnd, minAlpha, maxAlpha)

	def Enable(self):
		wndMgr.Enable(self.hWnd)

	def Disable(self):
		wndMgr.Disable(self.hWnd)

	def IsDisabled(self):
		return wndMgr.IsDisabled(self.hWnd)

	def Down(self):
		wndMgr.Down(self.hWnd)

	def SetUp(self):
		wndMgr.SetUp(self.hWnd)

	def SAFE_SetEvent(self, func, *args):
		self.eventFunc = __mem_func__(func)
		self.eventArgs = args

	def SetEvent(self, func, *args):
		self.eventFunc = func
		self.eventArgs = args

	def Over(self):
		wndMgr.Over(self.hWnd)

	def LeftRightReverse(self) :
		wndMgr.LeftRightReverse(self.hWnd)

	def SetTextColor(self, color):
		if not self.ButtonText:
			return
		self.ButtonText.SetPackedFontColor(color)

	def SetOutline(self, Value=True):
		if not self.ButtonText:
			return
		self.ButtonText.SetOutline(Value)

	def SetTextPosition(self, x, y):
		self.ButtonText.SetPosition(x, y)
		self.ButtonText.SetWindowHorizontalAlignCenter()
		self.ButtonText.SetWindowVerticalAlignCenter()

	def SetAlpha(self, alpha):
		wndMgr.SetButtonDiffuseColor(self.hWnd, 1.0, 1.0, 1.0, alpha)

	def GetText(self):
		if self.ButtonText:
			return self.ButtonText.GetText()
		else:
			return ""

	def IsDisable(self):
		return wndMgr.IsDisable(self.hWnd)

	def SetText(self, text, height = 4):
		if not self.ButtonText:
			textLine = TextLine()
			textLine.SetParent(self)
			textLine.SetPosition(self.GetWidth()/2, self.GetHeight()/2)
			textLine.SetVerticalAlignCenter()
			textLine.SetHorizontalAlignCenter()
			textLine.Show()
			self.ButtonText = textLine

		self.ButtonText.SetText(text)

	def AppendTextLineAllClear(self):
		self.TextChild = []

	def SetAppendTextChangeText(self, idx, text):
		if not len(self.TextChild):
			return

		self.TextChild[idx].SetText(text)

	def SetAppendTextColor(self, idx, color):
		if not len(self.TextChild):
			return

		self.TextChild[idx].SetPackedFontColor(color)

	def SetTextAddPos(self, text, x_add = 0, y_add = 0, height = 4):
		if not self.ButtonText:
			textLine = TextLine()
			textLine.SetParent(self)
			textLine.SetPosition(self.GetWidth() / 2 + x_add, self.GetHeight() / 2 + y_add)
			textLine.SetVerticalAlignCenter()
			textLine.SetHorizontalAlignCenter()
			textLine.Show()
			self.ButtonText = textLine
		self.ButtonText.SetText(text)
	def AppendTextLine(self, text
		, font_size = localeinfo.UI_DEF_FONT
		, font_color = DEFAULT_FONT_COLOR
		, text_sort = "center"
		, pos_x = None
		, pos_y = None) :
		textLine = TextLine()
		textLine.SetParent(self)
		textLine.SetFontName(font_size)
		textLine.SetPackedFontColor(font_color)
		textLine.SetText(text)
		textLine.Show()

		if not pos_x and not pos_y :
			textLine.SetPosition(self.GetWidth()/2, self.GetHeight()/2)
		else :
			textLine.SetPosition(pos_x, pos_y)

		textLine.SetVerticalAlignCenter()
		if "center" == text_sort:
			textLine.SetHorizontalAlignCenter()
		elif "right" == text_sort:
			textLine.SetHorizontalAlignRight()
		elif "left" == text_sort:
			textLine.SetHorizontalAlignLeft()

		self.TextChild.append(textLine)

	def HideToolTipText(self):
		if self.ToolTipText:
			self.tooltipHided = 1
			self.ToolTipText.Hide()

	def GetToolTipText(self):
		if self.ToolTipText:
			return self.ToolTipText.GetText()
		
		return ""

	def SetFormToolTipText(self, type, text, x, y):
		if not self.ToolTipText:
			toolTip = createToolTipWindowDict[type]()
			toolTip.SetParent(self)
			toolTip.SetSize(0, 0)
			toolTip.SetHorizontalAlignCenter()
			toolTip.SetOutline()
			toolTip.Hide()
			toolTip.SetPosition(x + self.GetWidth() / 2, y)
			self.ToolTipText = toolTip

		self.ToolTipText.SetText(text)

	def SetToolTipWindow(self, toolTip):
		self.ToolTipText=toolTip
		self.ToolTipText.SetParentProxy(self)

	def SetToolTipText(self, text, x=0, y = -19):
		self.SetFormToolTipText("TEXT", text, x, y)

	def CallEvent(self):
		snd.PlaySound("sound/ui/click.wav")

		if self.eventFunc:
			apply(self.eventFunc, self.eventArgs)

	def ShowToolTip(self):
		if self.ToolTipText and not self.tooltipHided:
			self.ToolTipText.Show()

		if self.eventOverInFunc:
			apply(self.eventOverInFunc, self.eventOverInArgs)

		if self.showtooltipevent:
			apply(self.showtooltipevent, self.showtooltiparg)

	def HideToolTip(self):
		if self.ToolTipText:
			self.ToolTipText.Hide()

		if self.eventOverOutFunc:
			apply(self.eventOverOutFunc, self.eventOverOutArgs)	

		if self.hidetooltipevent:
			apply(self.hidetooltipevent, self.hidetooltiparg)

	if app.ENABLE_12ZI:
		def SetAlwaysToolTip(self, bFlag):
			wndMgr.SetAlwaysToolTip(self.hWnd, bFlag)

	def SetShowToolTipEvent(self, func, *args):
		self.showtooltipevent = func
		self.showtooltiparg = args

	def SetHideToolTipEvent(self, func, *args):
		self.hidetooltipevent = func
		self.hidetooltiparg = args

	def IsDown(self):
		return wndMgr.IsDown(self.hWnd)

	# if app.USE_DUNGEON_COOLDOWN_MANAGER:
	def OnMouseOverIn(self):
		if self.overFunc:
			apply(self.overFunc, self.overArgs)

	def OnMouseOverOut(self):
		if self.overOutFunc:
			apply(self.overOutFunc, self.overOutArgs)

	def SetOverEvent(self, func, *args):
		self.overFunc = func
		self.overArgs = args

	def SetOverOutEvent(self, func, *args):
		self.overOutFunc = func
		self.overOutArgs = args

	if app.ENABLE_QUEST_RENEWAL or app.ENABLE_SKILL_COLOR_SYSTEM:
		def GetText(self):
			if not self.ButtonText:
				return ""

			return self.ButtonText.GetText()

		def SetTextAlignLeft(self, text, height = 4):
			if not self.ButtonText:
				textLine = TextLine()
				textLine.SetParent(self)
				textLine.SetPosition(202,self.GetHeight()/2)
				textLine.SetVerticalAlignCenter()
				textLine.SetHorizontalAlignLeft()
				textLine.Show()
				self.ButtonText = textLine

			#?��??� ���??� UI?? �A?� A�?? A�A�
			self.ButtonText.SetText(text)
			self.ButtonText.SetPosition(202,self.GetHeight()/2)
			self.ButtonText.SetVerticalAlignCenter()
			self.ButtonText.SetHorizontalAlignLeft()


		def SetTextAlignLeftNew(self, text, x = 4):
			if not self.ButtonText:
				textLine = TextLine()
				textLine.SetParent(self)
				textLine.SetPosition(x,self.GetHeight()/2)
				textLine.SetVerticalAlignCenter()
				textLine.SetHorizontalAlignLeft()
				textLine.Show()
				self.ButtonText = textLine

			#?��??� ���??� UI?? �A?� A�?? A�A�
			self.ButtonText.SetText(text)
			self.ButtonText.SetPosition(x,self.GetHeight()/2)
			self.ButtonText.SetVerticalAlignCenter()
			self.ButtonText.SetHorizontalAlignLeft()

		def SetTextAlignButton(self,text, x , y):
			if not self.ButtonText:
				textLine = TextLine()
				textLine.SetParent(self)
				textLine.SetPosition(x, y)
				textLine.SetVerticalAlignCenter()
				textLine.Show()
				self.ButtonText = textLine

			self.ButtonText.SetText(text)
			self.ButtonText.SetPosition(x, y)
			self.ButtonText.SetWindowHorizontalAlignRight()

		def SetTextAlignLeftCat(self, text, height = 4):
			if not self.ButtonText:
				textLine = TextLine()
				textLine.SetParent(self)
				textLine.SetPosition(202, self.GetHeight()/2)
				textLine.SetVerticalAlignCenter()
				textLine.SetHorizontalAlignLeft()
				textLine.Show()
				self.ButtonText = textLine

			#?��??� ���??� UI?? �A?� A�?? A�A�
			self.ButtonText.SetText(text)
			self.ButtonText.SetPosition(202, self.GetHeight()/2)
			self.ButtonText.SetVerticalAlignCenter()
			self.ButtonText.SetHorizontalAlignLeft()

		def SetTextAlignRight(self, text, height = 4):
			if not self.ButtonText:
				textLine = TextLine()
				textLine.SetParent(self)
				textLine.SetPosition(136,self.GetHeight()/2)
				textLine.SetVerticalAlignCenter()
				textLine.SetHorizontalAlignLeft()
				textLine.Show()
				self.ButtonText = textLine

			#?��??� ���??� UI?? �A?� A�?? A�A�
			self.ButtonText.SetText(text)
			self.ButtonText.SetPosition(136,self.GetHeight()/2)
			self.ButtonText.SetVerticalAlignCenter()
			self.ButtonText.SetHorizontalAlignLeft()


	def SetAlpha(self, alpha):
		self.SetButtonColor(1.0,1.0,1.0,alpha)

	def SetButtonColorRGB(self, r, g, b, alpha):
		self.buttonColorR = float(r)/255.0
		self.buttonColorG = float(g)/255.0
		self.buttonColorB = float(b)/255.0
		self.buttonColorA = alpha

		wndMgr.SetButtonColor(self.hWnd, float(r)/255.0, float(g)/255.0, float(b)/255.0, alpha)

	def SetButtonColor(self, r, g, b, alpha):
		self.buttonColorR = r
		self.buttonColorG = g
		self.buttonColorB = b
		self.buttonColorA = alpha

		wndMgr.SetButtonColor(self.hWnd, r, g, b, alpha)

	def GetButtonColor(self):
		return self.buttonColorR, self.buttonColorG, self.buttonColorB, self.buttonColorA


	def SetTextAddPos(self, text, x_add = 0, y_add = 0, height = 4):
		if not self.ButtonText:
			textLine = TextLine()
			textLine.SetParent(self)
			textLine.SetPosition(self.GetWidth() / 2 + x_add, self.GetHeight() / 2 + y_add)
			textLine.SetVerticalAlignCenter()
			textLine.SetHorizontalAlignCenter()
			textLine.Show()
			self.ButtonText = textLine
		self.ButtonText.SetText(text)

	def SetListText(self, text, x = 8):
		if not self.ButtonText:
			textLine = TextLine()
			textLine.SetParent(self)
			textLine.SetPosition(x, self.GetHeight()/2)
			textLine.SetVerticalAlignCenter()
			textLine.SetHorizontalAlignLeft()
			textLine.Show()
			self.ButtonText = textLine
		
		self.ButtonText.SetText(text)

class RadioButton(Button):
	def __init__(self):
		Button.__init__(self)

	def __del__(self):
		Button.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterRadioButton(self, layer)

class RadioButtonGroup:
	def __init__(self):
		self.buttonGroup = []
		self.selectedBtnIdx = -1

	def __del__(self):
		self.buttonGroup = []
		self.selectedBtnIdx = -1

	def Show(self):
		for (button, selectEvent, unselectEvent) in self.buttonGroup:
			button.Show()

	def Hide(self):
		for (button, selectEvent, unselectEvent) in self.buttonGroup:
			button.Hide()

	def SetText(self, idx, text):
		if idx >= len(self.buttonGroup):
			return
		(button, selectEvent, unselectEvent) = self.buttonGroup[idx]
		button.SetText(text)

	def SetTextPosition(self, idx, x, y):
		if idx >= len(self.buttonGroup):
			return
		(button, selectEvent, unselectEvent) = self.buttonGroup[idx]
		button.SetTextPosition(x, y)
	
	def SetToolTipText(self, idx, text):
		if idx >= len(self.buttonGroup):
			return
		(button, selectEvent, unselectEvent) = self.buttonGroup[idx]
		button.SetToolTipText(text)


	def OnClick(self, btnIdx):
		if btnIdx == self.selectedBtnIdx:
			return
		(button, selectEvent, unselectEvent) = self.buttonGroup[self.selectedBtnIdx]
		if unselectEvent:
			unselectEvent(self.selectedBtnIdx)
		button.SetUp()

		self.selectedBtnIdx = btnIdx
		(button, selectEvent, unselectEvent) = self.buttonGroup[btnIdx]
		if selectEvent:
			selectEvent(btnIdx)

		button.Down()

	def AddButton(self, button, selectEvent, unselectEvent):
		i = len(self.buttonGroup)
		button.SetEvent(__mem_func__(self.OnClick),i)
		self.buttonGroup.append([button, selectEvent, unselectEvent])
		button.SetUp()

	def Create(rawButtonGroup):
		radioGroup = RadioButtonGroup()
		for (button, selectEvent, unselectEvent) in rawButtonGroup:
			radioGroup.AddButton(button, selectEvent, unselectEvent)

		radioGroup.OnClick(0)

		return radioGroup

	Create=staticmethod(Create)

class ToggleButton(Button):
	def __init__(self):
		Button.__init__(self)

		self.eventUp = None
		self.eventDown = None

		self.eventUpArgs = None
		self.eventDownArgs = None

	def __del__(self):
		Button.__del__(self)

		self.eventUp = None
		self.eventDown = None

	def SetToggleUpEvent(self, event, *args):
		self.eventUp = event
		self.eventUpArgs = args

	def SetToggleDownEvent(self, event, *args):
		self.eventDown = event
		self.eventDownArgs = args

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterToggleButton(self, layer)

	def OnToggleUp(self):
		if self.eventUp:
			if self.eventUpArgs:
				apply(self.eventUp, self.eventUpArgs)
			else:
				self.eventUp()

	def OnToggleDown(self):
		if self.eventDown:
			if self.eventDownArgs:
				apply(self.eventDown, self.eventDownArgs)
			else:
				self.eventDown()

class DragButton(Button):
	def __init__(self):
		Button.__init__(self)
		self.AddFlag("movable")

		self.callbackEnable = True
		self.eventMove = lambda: None

		if app.ENABLE_INGAME_WIKI:
			self.upVisual = None
			self.overVisual = None
			self.downVisual = None

	def __del__(self):
		Button.__del__(self)

		self.eventMove = lambda: None

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterDragButton(self, layer)

	def SetMoveEvent(self, event):
		self.eventMove = event

	if app.ENABLE_INGAME_WIKI:
		def SetUpVisual(self, filename):
			self.upVisual = filename
			Button.SetUpVisual(self, filename)

		def SetOverVisual(self, filename):
			self.overVisual = filename
			Button.SetOverVisual(self, filename)

		def SetDownVisual(self, filename):
			self.downVisual = filename
			Button.SetDownVisual(self, filename)

	def SetRestrictMovementArea(self, x, y, width, height):
		wndMgr.SetRestrictMovementArea(self.hWnd, x, y, width, height)

	def TurnOnCallBack(self):
		self.callbackEnable = True

	def TurnOffCallBack(self):
		self.callbackEnable = False

	def OnMove(self):
		if self.callbackEnable:
			self.eventMove()

	if app.ENABLE_INGAME_WIKI:
		def OnMouseOverIn(self):
			if self.overVisual:
				self.SetOverVisual(self.overVisual)

		def OnMouseOverOut(self):
			if self.upVisual:
				self.SetUpVisual(self.upVisual)

		def OnMouseLeftButtonDown(self):
			if self.downVisual:
				self.SetDownVisual(self.downVisual)

		def OnMouseLeftButtonUp(self):
			if self.overVisual:
				self.SetUpVisual(self.overVisual)

class NumberLine(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

	def __del__(self):
		Window.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterNumberLine(self, layer)

	def SetHorizontalAlignCenter(self):
		wndMgr.SetNumberHorizontalAlignCenter(self.hWnd)

	def SetHorizontalAlignRight(self):
		wndMgr.SetNumberHorizontalAlignRight(self.hWnd)

	def SetPath(self, path):
		wndMgr.SetPath(self.hWnd, path)

	if app.ENABLE_CHEQUE_SYSTEM:
		def SetNumber(self, number, r = 1.0, g = 1.0, b = 1.0):
			wndMgr.SetNumber(self.hWnd, number, r, g, b)
	else:
		def SetNumber(self, number):
			wndMgr.SetNumber(self.hWnd, number)

###################################################################################################
## PythonScript Element
###################################################################################################

class Box(Window):
	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterBox(self, layer)

	def SetColor(self, color):
		wndMgr.SetColor(self.hWnd, color)

class Bar(Window):
	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterBar(self, layer)

	def SetColor(self, color):
		wndMgr.SetColor(self.hWnd, color)

class Line(Window):
	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterLine(self, layer)

	def SetColor(self, color):
		wndMgr.SetColor(self.hWnd, color)

class SlotBar(Window):
	def __init__(self):
		Window.__init__(self)

	def __del__(self):
		Window.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterBar3D(self, layer)

## Same with SlotBar
class Bar3D(Window):
	def __init__(self):
		Window.__init__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterBar3D(self, layer)

	def SetColor(self, left, right, center):
		wndMgr.SetColor(self.hWnd, left, right, center)

class SlotWindow(Window):
	def __init__(self):
		Window.__init__(self)

		self.StartIndex = 0

		self.eventSelectEmptySlot = None
		self.eventSelectItemSlot = None
		self.eventUnselectEmptySlot = None
		self.eventUnselectItemSlot = None
		self.eventUseSlot = None
		self.eventOverInItem = None
		self.eventOverOutItem = None
		self.eventPressedSlotButton = None

		self.eventSelectItemSlotArgs = None
		self.eventOverInItemArgs = None

		if app.USE_BL_FISH_EVENT:
			self.eventSelectEmptySlotWindow = None
			self.eventSelectItemSlotWindow = None
			self.eventOverInItemSlotWindow = None
			self.eventUnselectItemSlotWindow = None
			self.eventUseSlotWindow = None

	def __del__(self):
		if app.USE_BL_FISH_EVENT:
			self.eventSelectEmptySlotWindow = None
			self.eventSelectItemSlotWindow = None
			self.eventOverInItemSlotWindow = None
			self.eventUnselectItemSlotWindow = None
			self.eventUseSlotWindow = None

		Window.__del__(self)

		self.eventSelectEmptySlot = None
		self.eventSelectItemSlot = None
		self.eventUnselectEmptySlot = None
		self.eventUnselectItemSlot = None
		self.eventUseSlot = None
		self.eventOverInItem = None
		self.eventOverOutItem = None
		self.eventPressedSlotButton = None

		self.eventSelectItemSlotArgs = None
		self.eventOverInItemArgs = None

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterSlotWindow(self, layer)

	def SetSlotStyle(self, style):
		wndMgr.SetSlotStyle(self.hWnd, style)

	def HasSlot(self, slotIndex):
		return wndMgr.HasSlot(self.hWnd, slotIndex)

	def SetSlotScale(self, xScale, yScale):
		wndMgr.SetSlotScale(self.hWnd, xScale, yScale)

	def SetSlotCoolTimeColor(self, slotIndex, r, g, b, a):
		wndMgr.SetSlotCoolTimeColor(self.hWnd, slotIndex, r, g, b, a)

	def SetSlotCoolTimeInverse(self, slotIndex, coolTime, elapsedTime = 0.0):
		wndMgr.SetSlotCoolTimeInverse(self.hWnd, slotIndex, coolTime, elapsedTime)

	if app.ENABLE_GROWTH_PET_SYSTEM:
		def SetPetSkillSlotNew(self, renderingSlotNumber, petSkillIndex):
			petSkillIcon = skill.GetPetSkillIconImage(petSkillIndex)

			if app.USE_V1:
				if petSkillIcon == "":
					wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
					return
			else:
				if 0 == petSkillIcon:
					wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
					return

			wndMgr.SetSlot(self.hWnd, renderingSlotNumber, petSkillIndex, 1, 1, petSkillIcon)

	def SetSlotBaseImage(self, imageFileName, r, g, b, a):
		wndMgr.SetSlotBaseImage(self.hWnd, imageFileName, r, g, b, a)

	if app.ENABLE_IMAGE_SCALE:
		def SetSlotBaseImageScale(self, imageFileName, r, g, b, a, sx, sy):
			wndMgr.SetSlotBaseImageScale(self.hWnd, imageFileName, r, g, b, a, sx, sy)

	def SetBaseImageScale(self, xScale, yScale):
		wndMgr.SetBaseImageScale(self.hWnd, xScale, yScale)

	def SetCoverButton(self,\
						slotIndex,\
						upName="d:/ymir work/ui/public/slot_cover_button_01.sub",\
						overName="d:/ymir work/ui/public/slot_cover_button_02.sub",\
						downName="d:/ymir work/ui/public/slot_cover_button_03.sub",\
						disableName="d:/ymir work/ui/public/slot_cover_button_04.sub",\
						LeftButtonEnable = False,\
						RightButtonEnable = True):
		wndMgr.SetCoverButton(self.hWnd, slotIndex, upName, overName, downName, disableName, LeftButtonEnable, RightButtonEnable)

	def SetCorverButtonScale(self, slotIndex, xScale, yScale):
		wndMgr.SetCorverButtonScale(self.hWnd, slotIndex, xScale, yScale)

	def EnableCoverButton(self, slotIndex):
		wndMgr.EnableCoverButton(self.hWnd, slotIndex)

	def IsActiveSlot(self, slot_index):
		return wndMgr.IsActiveSlot(self.hWnd, slot_index)

	def DisableCoverButton(self, slotIndex):
		wndMgr.DisableCoverButton(self.hWnd, slotIndex)

	def SetAlwaysRenderCoverButton(self, slotIndex, bAlwaysRender = True):
		wndMgr.SetAlwaysRenderCoverButton(self.hWnd, slotIndex, bAlwaysRender)

	def AppendSlotButton(self, upName, overName, downName):
		wndMgr.AppendSlotButton(self.hWnd, upName, overName, downName)

	def ShowSlotButton(self, slotNumber):
		wndMgr.ShowSlotButton(self.hWnd, slotNumber)

	def HideAllSlotButton(self):
		wndMgr.HideAllSlotButton(self.hWnd)

	def AppendRequirementSignImage(self, filename):
		wndMgr.AppendRequirementSignImage(self.hWnd, filename)

	def ShowRequirementSign(self, slotNumber):
		wndMgr.ShowRequirementSign(self.hWnd, slotNumber)

	def HideRequirementSign(self, slotNumber):
		wndMgr.HideRequirementSign(self.hWnd, slotNumber)

	def ActivateSlot(self, slotNumber):
		wndMgr.ActivateSlot(self.hWnd, slotNumber)

	def DeactivateSlot(self, slotNumber):
		wndMgr.DeactivateSlot(self.hWnd, slotNumber)

	if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
		def SetSlotDiffuseColor(self, slotindex, colortype):
			wndMgr.SetSlotDiffuseColor(self.hWnd, slotindex, colortype)

		def SetSlotFlashEffect(self, slotindex, active):
			wndMgr.SetSlotFlashEffect(self.hWnd, slotindex, active)

	def SetSlotHighlightedGreeen(self, slotNumber):
		wndMgr.SetSlotHighlightedGreeen(self.hWnd, slotNumber)

	def DisableSlotHighlightedGreen(self, slotNumber):
		wndMgr.DisableSlotHighlightedGreen(self.hWnd, slotNumber)

	def ShowSlotBaseImage(self, slotNumber):
		wndMgr.ShowSlotBaseImage(self.hWnd, slotNumber)

	def HideSlotBaseImage(self, slotNumber):
		wndMgr.HideSlotBaseImage(self.hWnd, slotNumber)

	if app.USE_BL_FISH_EVENT:
		def SAFE_SetButtonEvent(self, button, state, event, window = None):
			if button == "LEFT":
				if state == "EMPTY":
					self.eventSelectEmptySlot = __mem_func__(event)
					self.eventSelectEmptySlotWindow = window
				elif state == "EXIST":
					self.eventSelectItemSlot = __mem_func__(event)
					self.eventSelectItemSlotWindow = window
				elif state == "ALWAYS":
					self.eventSelectEmptySlot = __mem_func__(event)
					self.eventSelectEmptySlotWindow = window
					self.eventSelectItemSlot = __mem_func__(event)
					self.eventSelectItemSlotWindow = window
			elif button == "RIGHT":
				if state == "EMPTY":
					self.eventUnselectEmptySlot = __mem_func__(event)
				elif state == "EXIST":
					self.eventUnselectItemSlot = __mem_func__(event)
					self.eventUnselectItemSlotWindow = window
				elif state == "ALWAYS":
					self.eventUnselectEmptySlot = __mem_func__(event)
					self.eventUnselectItemSlot = __mem_func__(event)
					self.eventUnselectItemSlotWindow = window
	else:
		def SAFE_SetButtonEvent(self, button, state, event):
			if button == "LEFT":
				if state == "EMPTY":
					self.eventSelectEmptySlot = __mem_func__(event)
				elif state == "EXIST":
					self.eventSelectItemSlot = __mem_func__(event)
				elif state == "ALWAYS":
					self.eventSelectEmptySlot = __mem_func__(event)
					self.eventSelectItemSlot = __mem_func__(event)
			elif button == "RIGHT":
				if state == "EMPTY":
					self.eventUnselectEmptySlot = __mem_func__(event)
				elif state == "EXIST":
					self.eventUnselectItemSlot = __mem_func__(event)
				elif state == "ALWAYS":
					self.eventUnselectEmptySlot = __mem_func__(event)
					self.eventUnselectItemSlot = __mem_func__(event)

	if app.USE_BL_FISH_EVENT:
		def SetSelectEmptySlotEvent(self, empty, window = None):
			self.eventSelectEmptySlot = empty
			self.eventSelectEmptySlotWindow = window

		def SetSelectItemSlotEvent(self, item, window = None, *args):
			self.eventSelectItemSlot = item
			self.eventSelectItemSlotWindow = window
			self.eventSelectItemSlotArgs = args

		def SetUnselectItemSlotEvent(self, item, window = None):
			self.eventUnselectItemSlot = item
			self.eventUnselectItemSlotWindow = window

		def SetOverInItemEvent(self, event, window = None, *args):
			self.eventOverInItem = event
			self.eventOverInItemArgs = args
			self.eventOverInItemSlotWindow = window
	else:
		def SetSelectEmptySlotEvent(self, empty):
			self.eventSelectEmptySlot = empty

		def SetSelectItemSlotEvent(self, item, *args):
			self.eventSelectItemSlot = item
			self.eventSelectItemSlotArgs = args

		def SetUnselectItemSlotEvent(self, item):
			self.eventUnselectItemSlot = item

		def SetOverInItemEvent(self, event, *args):
			self.eventOverInItem = event
			self.eventOverInItemArgs = args

	def SetUnselectEmptySlotEvent(self, empty):
		self.eventUnselectEmptySlot = empty

	def SetUseSlotEvent(self, use):
		self.eventUseSlot = use

	def SetOverOutItemEvent(self, event):
		self.eventOverOutItem = event

	def SetPressedSlotButtonEvent(self, event):
		self.eventPressedSlotButton = event

	def GetSlotCount(self):
		return wndMgr.GetSlotCount(self.hWnd)

	def SetUseMode(self, flag):
		"True??? ItemToItem ? ???? ????"
		wndMgr.SetUseMode(self.hWnd, flag)

	def SetUsableItem(self, flag):
		"True? ?? ??? ???? ItemToItem ?? ????"
		wndMgr.SetUsableItem(self.hWnd, flag)

	## Slot
	def SetSlotCoolTime(self, slotIndex, coolTime, elapsedTime = 0.0):
		wndMgr.SetSlotCoolTime(self.hWnd, slotIndex, coolTime, elapsedTime)

	def SetSlotCoolTimeColor(self, slotIndex, r, g, b, a):
		wndMgr.SetSlotCoolTimeColor(self.hWnd, slotIndex, r, g, b, a)

	def StoreSlotCoolTime(self, key, slotIndex, coolTime, elapsedTime = 0.0):
		wndMgr.StoreSlotCoolTime(self.hWnd, key, slotIndex, coolTime, elapsedTime)

	def RestoreSlotCoolTime(self, key):
		wndMgr.RestoreSlotCoolTime(self.hWnd, key)

	if app.WJ_ENABLE_TRADABLE_ICON:
		def SetCanMouseEventSlot(self, slotIndex):
			wndMgr.SetCanMouseEventSlot(self.hWnd, slotIndex)

		def SetCantMouseEventSlot(self, slotIndex):
			wndMgr.SetCantMouseEventSlot(self.hWnd, slotIndex)

		def SetUnusableSlotOnTopWnd(self, slotIndex):
			wndMgr.SetUnusableSlotOnTopWnd(self.hWnd, slotIndex)

		def SetUsableSlotOnTopWnd(self, slotIndex):
			wndMgr.SetUsableSlotOnTopWnd(self.hWnd, slotIndex)

	def DisableSlot(self, slotIndex):
		wndMgr.DisableSlot(self.hWnd, slotIndex)

	def EnableSlot(self, slotIndex):
		wndMgr.EnableSlot(self.hWnd, slotIndex)

	def LockSlot(self, slotIndex):
		wndMgr.LockSlot(self.hWnd, slotIndex)

	def UnlockSlot(self, slotIndex):
		wndMgr.UnlockSlot(self.hWnd, slotIndex)

	def RefreshSlot(self):
		wndMgr.RefreshSlot(self.hWnd)

	def ClearSlot(self, slotNumber):
		wndMgr.ClearSlot(self.hWnd, slotNumber)

	def ClearAllSlot(self):
		wndMgr.ClearAllSlot(self.hWnd)

	def GetSlotIndexList(self):
		return wndMgr.GetSlotIndexList(self.hWnd)

	def AppendSlot(self, index, x, y, width, height):
		wndMgr.AppendSlot(self.hWnd, index, x, y, width, height)

	def SetSlot(self, slotIndex, itemIndex, width, height, icon, diffuseColor = (1.0, 1.0, 1.0, 1.0)):
		wndMgr.SetSlot(self.hWnd, slotIndex, itemIndex, width, height, icon, diffuseColor)

	def SetGridSpecial(self, w, h):
		wndMgr.SetGridSpecial(self.hWnd, w, h)
	
	def GetEmptyGrid(self, item_size):
		return wndMgr.GetEmptyGrid(self.hWnd, item_size)
	
	def ClearGrid(self):
		wndMgr.ClearGrid(self.hWnd)
	
	def PutItemGrid(self, pos, size):
		wndMgr.PutItemGrid(self.hWnd, pos, size)
		
	def ClearItemGrid(self, pos, size):
		wndMgr.ClearItemGrid(self.hWnd, pos, size)

	# if app.ENABLE_IMAGE_SCALE:
		# def SetSlotScale(self, slotIndex, itemIndex, width, height, icon, sx, sy, diffuseColor = (1.0, 1.0, 1.0, 1.0)):
			# wndMgr.SetSlotScale(self.hWnd, slotIndex, itemIndex, width, height, icon, diffuseColor, sx, sy)

	def SetSlotCount(self, slotNumber, count):
		wndMgr.SetSlotCount(self.hWnd, slotNumber, count)

	def SetRealSlotNumber(self, slotNumber, realSlotNumber):
		wndMgr.SetSlotRealNumber(self.hWnd, slotNumber, realSlotNumber)

	def SetSlotCountNew(self, slotNumber, grade, count):
		wndMgr.SetSlotCountNew(self.hWnd, slotNumber, grade, count)

	if app.ENABLE_MINI_GAME_OKEY:
		def SetCardSlot(self, renderingSlotNumber, CardIndex, cardIcon, diffuseColor = (1.0, 1.0, 1.0, 1.0)):
			if 0 == CardIndex or None == CardIndex:
				wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
				return

			item.SelectItem(CardIndex)
			(width, height) = item.GetItemSize()

			if app.USE_V1:
				wndMgr.SetSlot(self.hWnd, renderingSlotNumber, CardIndex, width, height, cardIcon, diffuseColor)
			else:
				wndMgr.SetCardSlot(self.hWnd, renderingSlotNumber, CardIndex, width, height, cardIcon, diffuseColor)

	def SetItemSlot(self, renderingSlotNumber, ItemIndex, ItemCount = 0, diffuseColor = (1.0, 1.0, 1.0, 1.0)):
		if 0 == ItemIndex or None == ItemIndex:
			wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
			return

		item.SelectItem(ItemIndex)

		if app.USE_V1:
			itemIcon = item.GetIconImageFileName()
		else:
			itemIcon = item.GetIconImage()

		# common fix
		if app.USE_V1:
			if itemIcon == "":
				wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
				return
		else:
			if itemIcon == 0:
				wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
				return

		item.SelectItem(ItemIndex)
		(width, height) = item.GetItemSize()

		wndMgr.SetSlot(self.hWnd, renderingSlotNumber, ItemIndex, width, height, itemIcon, diffuseColor)
		wndMgr.SetSlotCount(self.hWnd, renderingSlotNumber, ItemCount)

	if app.ENABLE_DSS_ACTIVE_EFFECT_BUTTON:
		def SetRenderSlot(self, renderingSlotNumber, diffuseColor = (1.0, 1.0, 1.0, 1.0)):
			wndMgr.SetSlot(self.hWnd, renderingSlotNumber, 1, 1, 1, 0, diffuseColor)
			wndMgr.SetSlotCount(self.hWnd, renderingSlotNumber, 0)

	def SetSkillSlot(self, renderingSlotNumber, skillIndex, skillLevel):
		skillIcon = skill.GetIconImage(skillIndex)

		if app.USE_V1:
			if skillIcon == "":
				wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
				return
		else:
			if 0 == skillIcon:
				wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
				return

		wndMgr.SetSlot(self.hWnd, renderingSlotNumber, skillIndex, 1, 1, skillIcon)
		wndMgr.SetSlotCount(self.hWnd, renderingSlotNumber, skillLevel)

	def SetSkillSlotNew(self, renderingSlotNumber, skillIndex, skillGrade, skillLevel):
		skillIcon = skill.GetIconImageNew(skillIndex, skillGrade)

		if app.USE_V1:
			if skillIcon == "":
				wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
				return
		else:
			if 0 == skillIcon:
				wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
				return

		wndMgr.SetSlot(self.hWnd, renderingSlotNumber, skillIndex, 1, 1, skillIcon)

	def SetEmotionSlot(self, renderingSlotNumber, emotionIndex):
		icon = player.GetEmotionIconImage(emotionIndex)

		if app.USE_V1:
			if icon == "":
				wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
				return
		else:
			if 0 == icon:
				wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
				return

		wndMgr.SetSlot(self.hWnd, renderingSlotNumber, emotionIndex, 1, 1, icon)

	## Event
	if app.USE_BL_FISH_EVENT:
		def OnSelectEmptySlot(self, slotNumber):
			if self.eventSelectEmptySlot:
				if self.eventSelectEmptySlotWindow:
					self.eventSelectEmptySlot(slotNumber, self.eventSelectEmptySlotWindow)
				else:
					self.eventSelectEmptySlot(slotNumber)

		def OnSelectItemSlot(self, slotNumber):
			if self.eventSelectItemSlot:
				if self.eventSelectItemSlotWindow:
					if self.eventSelectItemSlotArgs:
						apply(self.eventSelectItemSlot, self.eventSelectItemSlotArgs)
					else:
						self.eventSelectItemSlot(slotNumber, self.eventSelectItemSlotWindow)
				else:
					if self.eventSelectItemSlotArgs:
						apply(self.eventSelectItemSlot, self.eventSelectItemSlotArgs)
					else:
						self.eventSelectItemSlot(slotNumber)

		def OnUnselectItemSlot(self, slotNumber):
			if self.eventUnselectItemSlot:
				if self.eventUnselectItemSlotWindow:
					self.eventUnselectItemSlot(slotNumber, self.eventUnselectItemSlotWindow)
				else:
					self.eventUnselectItemSlot(slotNumber)

		def OnUseSlot(self, slotNumber):
			if self.eventUseSlot:
				if self.eventUseSlotWindow:
					self.eventUseSlot(slotNumber, self.eventUseSlotWindow)
				else:
					self.eventUseSlot(slotNumber)

		def OnOverInItem(self, slotNumber):
			if self.eventOverInItem:
				if None == self.eventOverInItemSlotWindow:
					if self.eventOverInItemArgs:
						apply(self.eventOverInItem, self.eventOverInItemArgs)
					else:
						self.eventOverInItem(slotNumber)
				else:
					if self.eventOverInItemArgs:
						apply(self.eventOverInItem, self.eventOverInItemArgs)
					else:
						self.eventOverInItem(slotNumber, self.eventOverInItemSlotWindow)
	else:
		def OnSelectEmptySlot(self, slotNumber):
			if self.eventSelectEmptySlot:
				self.eventSelectEmptySlot(slotNumber)

		def OnSelectItemSlot(self, slotNumber):
			if self.eventSelectItemSlot:
				if self.eventSelectItemSlotArgs:
					apply(self.eventSelectItemSlot, self.eventSelectItemSlotArgs)
				else:
					self.eventSelectItemSlot(slotNumber)

		def OnUnselectItemSlot(self, slotNumber):
			if self.eventUnselectItemSlot:
				self.eventUnselectItemSlot(slotNumber)

		def OnUseSlot(self, slotNumber):
			if self.eventUseSlot:
				self.eventUseSlot(slotNumber)

		def OnOverInItem(self, slotNumber):
			if self.eventOverInItem:
				if self.eventOverInItemArgs:
					apply(self.eventOverInItem, self.eventOverInItemArgs)
				else:
					self.eventOverInItem(slotNumber)

	def OnUnselectEmptySlot(self, slotNumber):
		if self.eventUnselectEmptySlot:
			self.eventUnselectEmptySlot(slotNumber)

	def OnOverOutItem(self):
		if self.eventOverOutItem:
			self.eventOverOutItem()

	def OnPressedSlotButton(self, slotNumber):
		if self.eventPressedSlotButton:
			self.eventPressedSlotButton(slotNumber)

	def GetStartIndex(self):
		return 0

	def GetSlotGlobalPosition(self, index):
		return wndMgr.GetSlotGlobalPosition(self.hWnd, index)

	def GetSlotLocalPosition(self, index):
		return wndMgr.GetSlotLocalPosition(self.hWnd, index)

	if app.ENABLE_SLOT_COVER_IMAGE_SYSTEM:
		def SetSlotCoverImage(self, slotindex, filename):
			wndMgr.SetSlotCoverImage(self.hWnd, slotindex, filename)

		def EnableSlotCoverImage(self, slotindex, onoff):
			wndMgr.EnableSlotCoverImage(self.hWnd, slotindex, onoff)

	def SetSlotType(self, flag):
		wndMgr.SetSlotType(self.hWnd, flag)

	if app.ENABLE_HIGH_LIGHT_IMAGE:
		def AppendHighLightImage(self, index, fileName, alphaSpeed = 0.0, rotationSpeed = 0.0, curAlpha = 1.0, diffuse = 0xFFFFFFFF):
			wndMgr.AppendHighLightImage(self.hWnd, index, fileName, alphaSpeed, rotationSpeed, curAlpha, diffuse)

		def EnableHighLightImage(self, slotIndex):
			wndMgr.EnableHighLightImage(self.hWnd, slotIndex)

		def DisableHighLightImage(self, slotIndex):
			wndMgr.DisableHighLightImage(self.hWnd, slotIndex)

	if app.USE_OFFLINESHOP_EXTENDED_SLOTS:
		def GetItemIndex(self, slotIndex):
			return wndMgr.GetItemIndex(self.hWnd, slotIndex)

class GridSlotWindow(SlotWindow):

	def __init__(self):
		SlotWindow.__init__(self)

		self.startIndex = 0

	def __del__(self):
		SlotWindow.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterGridSlotWindow(self, layer)

	def ArrangeSlot(self, StartIndex, xCount, yCount, xSize, ySize, xBlank, yBlank):

		self.startIndex = StartIndex

		wndMgr.ArrangeSlot(self.hWnd, StartIndex, xCount, yCount, xSize, ySize, xBlank, yBlank)
		self.startIndex = StartIndex

	def GetStartIndex(self):
		return self.startIndex

class TitleBarWithoutButton(Window):
	BLOCK_WIDTH = 32
	BLOCK_HEIGHT = 23

	def __init__(self):
		Window.__init__(self)
		self.AddFlag("attach")

	def __del__(self):
		Window.__del__(self)

	def MakeTitleBar(self, width, color):


		width = max(64, width)

		imgLeft = ImageBox()
		imgCenter = ExpandedImageBox()
		imgRight = ImageBox()
		imgLeft.AddFlag("not_pick")
		imgCenter.AddFlag("not_pick")
		imgRight.AddFlag("not_pick")
		imgLeft.SetParent(self)
		imgCenter.SetParent(self)
		imgRight.SetParent(self)

		if localeinfo.IsARABIC():
			imgLeft.LoadImage("locale/ae/ui/pattern/titlebar_left_02.tga")
			imgCenter.LoadImage("locale/ae/ui/pattern/titlebar_center.tga")
			imgRight.LoadImage("locale/ae/ui/pattern/titlebar_right_02.tga")
		else:
			imgLeft.LoadImage("d:/ymir work/ui/pattern/titlebar_left_02.tga")
			imgCenter.LoadImage("d:/ymir work/ui/pattern/titlebar_center.tga")
			imgRight.LoadImage("d:/ymir work/ui/pattern/titlebar_right_02.tga")

		imgLeft.Show()
		imgCenter.Show()
		imgRight.Show()

		self.imgLeft = imgLeft
		self.imgCenter = imgCenter
		self.imgRight = imgRight

		self.SetWidth(width)

	def SetWidth(self, width):
		self.imgCenter.SetRenderingRect(0.0, 0.0, float((width - self.BLOCK_WIDTH*2) - self.BLOCK_WIDTH) / self.BLOCK_WIDTH, 0.0)
		self.imgCenter.SetPosition(self.BLOCK_WIDTH, 0)
		self.imgRight.SetPosition(width - self.BLOCK_WIDTH, 0)
			
		self.SetSize(width, self.BLOCK_HEIGHT)

class TitleBar(Window):

	BLOCK_WIDTH = 32
	BLOCK_HEIGHT = 23
	IS_SCALE = False

	POSITIONS = {
		"Q" : [27, 2],
		"C" : [3, 3]
	}
	IMAGES = {
		'TITLE' : {
			'PATH'          : "d:/ymir work/ui/pattern",
			'PATHS'          : "locale/ae/ui/pattern",
			'LEFT'          : 'titlebar_left.tga',
			'CENTER'        : 'titlebar_center.tga',
			'RIGHT'         : 'titlebar_right.tga',
			'RIGHT_SPECIAL' : 'titlebar_right_02.tga'
		},
	}

	def __init__(self):
		Window.__init__(self)
		self.AddFlag("attach")

	def __del__(self):
		Window.__del__(self)

	def MakeTitleBar(self, width, color):


		width = max(64, width)

		imgLeft = ImageBox()
		imgCenter = ExpandedImageBox()
		imgRight = ImageBox()
		imgLeft.AddFlag("not_pick")
		imgCenter.AddFlag("not_pick")
		imgRight.AddFlag("not_pick")
		imgLeft.SetParent(self)
		imgCenter.SetParent(self)
		imgRight.SetParent(self)

		if localeinfo.IsARABIC():
			imgLeft.LoadImage("locale/ae/ui/pattern/titlebar_left.tga")
			imgCenter.LoadImage("locale/ae/ui/pattern/titlebar_center.tga")
			imgRight.LoadImage("locale/ae/ui/pattern/titlebar_right.tga")
		else:
			imgLeft.LoadImage("d:/ymir work/ui/pattern/titlebar_left.tga")
			imgCenter.LoadImage("d:/ymir work/ui/pattern/titlebar_center.tga")
			imgRight.LoadImage("d:/ymir work/ui/pattern/titlebar_right.tga")

		imgLeft.Show()
		imgCenter.Show()
		imgRight.Show()

		btnClose = Button()
		btnClose.SetParent(self)
		btnClose.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")
		btnClose.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")
		btnClose.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")
		btnClose.SetToolTipText(localeinfo.UI_CLOSE, 0, -23)
		btnClose.Show()

		self.imgLeft = imgLeft
		self.imgCenter = imgCenter
		self.imgRight = imgRight
		self.btnClose = btnClose

		self.SetWidth(width)

	def SetWidth(self, width):
		self.imgCenter.SetRenderingRect(0.0, 0.0, float((width - self.BLOCK_WIDTH*2) - self.BLOCK_WIDTH) / self.BLOCK_WIDTH, 0.0)
		self.imgCenter.SetPosition(self.BLOCK_WIDTH, 0)
		self.imgRight.SetPosition(width - self.BLOCK_WIDTH, 0)

		if localeinfo.IsARABIC():
			self.btnClose.SetPosition(3, 3)# the problem causing the title bar to appear as small 
		else:
			self.btnClose.SetPosition(width - self.btnClose.GetWidth() - 3, 3)

		self.SetSize(width, self.BLOCK_HEIGHT)

	def SetCloseEvent(self, event):
		self.btnClose.SetEvent(event)

	if app.ENABLE_CAPTCHA_SYSTEM:
		def CloseButtonHide(self):
			if localeinfo.IsARABIC():
				self.imgLeft.LoadImage("d:/ymir work/locale/ae/ui/pattern/titlebar_right_02.tga")
				self.imgLeft.LeftRightReverse()
				self.btnClose.Hide()
			else:
				self.imgRight.LoadImage("d:/ymir work/ui/pattern/titlebar_right_02.tga")
				self.btnClose.Hide()

	def CloseButton(self, command):
		if command == "hide":
			self.imgRight.LoadImage("%s/%s" % (self.IMAGES['TITLE']['PATH'], self.IMAGES['TITLE']['RIGHT_SPECIAL']))
			self.btnClose.Hide()
		elif command == "show":
			self.imgRight.LoadImage("%s/%s" % (self.IMAGES['TITLE']['PATHS'], self.IMAGES['TITLE']['RIGHT']))
			self.btnClose.Show()

	def CloseButtonHide(self):
		if localeinfo.IsARABIC():
			self.imgLeft.LoadImage("d:/ymir work/ui/pattern/titlebar_right_02.tga")
			self.imgLeft.LeftRightReverse()
			self.btnClose.Hide()
		else:
			self.imgRight.LoadImage("d:/ymir work/ui/pattern/titlebar_right_02.tga")
			self.btnClose.Hide()

class SibTitleBar(Window):

	BLOCK_WIDTH = 21
	BLOCK_HEIGHT = 21

	def __init__(self):
		Window.__init__(self)
		self.AddFlag("attach")

	def __del__(self):
		Window.__del__(self)

	def MakeTitleBar(self, width, color):


		width = max(64, width)

		imgLeft = ImageBox()
		imgCenter = ExpandedImageBox()
		imgRight = ImageBox()
		imgLeft.AddFlag("not_pick")
		imgCenter.AddFlag("not_pick")
		imgRight.AddFlag("not_pick")
		imgLeft.SetParent(self)
		imgCenter.SetParent(self)
		imgRight.SetParent(self)
		imgLeft.LoadImage("d:/ymir work/ui/pattern/border_c_left.tga")
		imgCenter.LoadImage("d:/ymir work/ui/pattern/border_c_middle.tga")
		imgRight.LoadImage("d:/ymir work/ui/pattern/border_c_right.tga")

		imgLeft.Show()
		imgCenter.Show()
		imgRight.Show()

		btnClose = Button()
		btnClose.SetParent(self)
		btnClose.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")
		btnClose.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")
		btnClose.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")
		btnClose.SetToolTipText(localeinfo.UI_CLOSE, 0, -23)
		btnClose.Show()

		self.imgLeft = imgLeft
		self.imgCenter = imgCenter
		self.imgRight = imgRight
		self.btnClose = btnClose

		self.SetWidth(width)

	def SetWidth(self, width):
		self.imgCenter.SetRenderingRect(0.0, 0.0, float((width - self.BLOCK_WIDTH*2) - self.BLOCK_WIDTH) / self.BLOCK_WIDTH, 0.0)
		self.imgCenter.SetPosition(self.BLOCK_WIDTH, 0)
		self.imgRight.SetPosition(width - self.BLOCK_WIDTH, 0)
		self.btnClose.SetPosition(width - self.btnClose.GetWidth() - 3, 3)
		self.SetSize(width, self.BLOCK_HEIGHT)

	def SetCloseEvent(self, event):
		self.btnClose.SetEvent(event)

	def CloseButtonHide(self) :
		self.imgRight.LoadImage("d:/ymir work/ui/pattern/titlebar_right_02.tga")
		self.btnClose.Hide()

class TitleBarNEW(Window):

	BLOCK_WIDTH = 32
	BLOCK_HEIGHT = 23
	IS_SCALE = False

	POSITIONS = {
		"Q" : [27, 2],
		"C" : [3, 3]
	}
	IMAGES = {
		'TITLE' : {
			'PATH'          : "d:/ymir work/ui/pattern",
			'PATHS'          : "locale/ae/ui/pattern",
			'LEFT'          : 'titlebar_left.tga',
			'CENTER'        : 'titlebar_center.tga',
			'RIGHT'         : 'titlebar_right.tga',
			'RIGHT_SPECIAL' : 'titlebar_right_02.tga'
		},
	}

	def __init__(self):
		Window.__init__(self)
		self.AddFlag("attach")

	def __del__(self):
		Window.__del__(self)

	def MakeTitleBar(self, width, color):


		width = max(64, width)

		# imgLeft = ImageBox()
		# imgCenter = ExpandedImageBox()
		# imgRight = ImageBox()
		# imgLeft.AddFlag("not_pick")
		# imgCenter.AddFlag("not_pick")
		# imgRight.AddFlag("not_pick")
		# imgLeft.SetParent(self)
		# imgCenter.SetParent(self)
		# imgRight.SetParent(self)

		# if localeinfo.IsARABIC():
			# imgLeft.LoadImage("locale/ae/ui/pattern/titlebar_left.tga")
			# imgCenter.LoadImage("locale/ae/ui/pattern/titlebar_center.tga")
			# imgRight.LoadImage("locale/ae/ui/pattern/titlebar_right.tga")
		# else:
			# imgLeft.LoadImage("d:/ymir work/ui/pattern/titlebar_left.tga")
			# imgCenter.LoadImage("d:/ymir work/ui/pattern/titlebar_center.tga")
			# imgRight.LoadImage("d:/ymir work/ui/pattern/titlebar_right.tga")

		# imgLeft.Show()
		# imgCenter.Show()
		# imgRight.Show()

		btnClose = Button()
		btnClose.SetParent(self)
		btnClose.SetUpVisual("cream/shopbuilder/close_1.png")
		btnClose.SetOverVisual("cream/shopbuilder/close_2.png")
		btnClose.SetDownVisual("cream/shopbuilder/close_3.png")
		btnClose.SetToolTipText(localeinfo.UI_CLOSE, 0, -23)
		btnClose.Show()

		# self.imgLeft = imgLeft
		# self.imgCenter = imgCenter
		# self.imgRight = imgRight
		self.btnClose = btnClose

		self.SetWidth(width)

	def SetWidth(self, width):
		# self.imgCenter.SetRenderingRect(0.0, 0.0, float((width - self.BLOCK_WIDTH*2) - self.BLOCK_WIDTH) / self.BLOCK_WIDTH, 0.0)
		# self.imgCenter.SetPosition(self.BLOCK_WIDTH, 0)
		# self.imgRight.SetPosition(width - self.BLOCK_WIDTH, 0)

		if localeinfo.IsARABIC():
			self.btnClose.SetPosition(3, 3)# the problem causing the title bar to appear as small 
		else:
			self.btnClose.SetPosition(width - self.btnClose.GetWidth() - 3, 3)

		self.SetSize(width, self.BLOCK_HEIGHT)

	def SetCloseEvent(self, event):
		self.btnClose.SetEvent(event)



if app.ENABLE_QUEST_RENEWAL:
	class SubTitleBar(Button):
		def __init__(self):
			Button.__init__(self)

		def __del__(self):
			Button.__del__(self)

		def MakeSubTitleBar(self, width):
			width = max(64, width)
			self.SetWidth(width)
			if localeinfo.IsARABIC():
				self.SetUpVisual("d:/ymir work/ui/quest_re/quest_tab_01_ae.tga")
				self.SetOverVisual("d:/ymir work/ui/quest_re/quest_tab_01_ae.tga")
				self.SetDownVisual("d:/ymir work/ui/quest_re/quest_tab_01_ae.tga")
			else:
				self.SetUpVisual("d:/ymir work/ui/quest_re/quest_tab_01.tga")
				self.SetOverVisual("d:/ymir work/ui/quest_re/quest_tab_01.tga")
				self.SetDownVisual("d:/ymir work/ui/quest_re/quest_tab_01.tga")
			self.Show()

			scrollImage = ImageBox()
			scrollImage.SetParent(self)
			scrollImage.LoadImage("d:/ymir work/ui/quest_re/quest_down.tga")
			if localeinfo.IsARABIC():
				scrollImage.SetPosition(204.5, 2.5)
			else:
				scrollImage.SetPosition(5, 2.5)
			scrollImage.AddFlag("not_pick")
			scrollImage.Show()
			self.scrollImage = scrollImage

		def OpenCategory(self, qcount = 0):
			if qcount > 0:
				self.scrollImage.LoadImage("d:/ymir work/ui/quest_re/quest_up.tga")
			else:
				self.scrollImage.LoadImage("d:/ymir work/ui/quest_re/quest_down.tga")

		def CloseCategory(self, qcount = 0):
			self.scrollImage.LoadImage("d:/ymir work/ui/quest_re/quest_down.tga")

		def SetQuestLabel(self, filename, qcount):
			tabColor = ImageBox()
			tabColor.SetParent(self)
			tabColor.LoadImage(filename)
			tabColor.AddFlag("not_pick")
			tabColor.SetPosition(22, 12)
			if qcount > 0:
				tabColor.Show()
			else:
				tabColor.Hide()
			self.tabColor = tabColor

		def SetWidth(self, width):
			self.SetPosition(32, 0)
			self.SetSize(width, 23)

	class ListBar(Button):
		def __init__(self):
			Button.__init__(self)

		def __del__(self):
			Button.__del__(self)

		def MakeListBar(self, width, color):
			width = max(64, width)
			self.SetWidth(width)
			self.Show()

			checkbox = ImageBox()
			checkbox.SetParent(self)
			checkbox.LoadImage("d:/ymir work/ui/quest_re/quest_new.tga")
			checkbox.SetPosition(208, 9)
			checkbox.AddFlag("not_pick")
			checkbox.Show()
			self.checkbox = checkbox
			self.isChecked = False

		def SetWidth(self, width):
			self.SetPosition(32, 0)
			self.SetSize(width, 23)

		def CallEvent(self):
			self.OnClickEvent()
			super(ListBar, self).CallEvent()

		def OnClickEvent(self):
			self.checkbox.Hide()
			self.isChecked = True

		def SetSlot(self, slotIndex, itemIndex, width, height, icon, diffuseColor = (1.0, 1.0, 1.0, 1.0)):
			wndMgr.SetSlot(self.hWnd, slotIndex, itemIndex, width, height, icon, diffuseColor)

		def SetGridSpecial(self, w, h):
			wndMgr.SetGridSpecial(self.hWnd, w, h)
	
		def GetEmptyGrid(self, item_size):
			return wndMgr.GetEmptyGrid(self.hWnd, item_size)
	
		def ClearGrid(self):
			wndMgr.ClearGrid(self.hWnd)
	
		def PutItemGrid(self, pos, size):
			wndMgr.PutItemGrid(self.hWnd, pos, size)
		
		def ClearItemGrid(self, pos, size):
			wndMgr.ClearItemGrid(self.hWnd, pos, size)

class SibBar(Window):

	BLOCK_WIDTH = 21
	BLOCK_HEIGHT = 21

	def __init__(self):
		Window.__init__(self)
		self.AddFlag("attach")

	def __del__(self):
		Window.__del__(self)

	def Create(self, width):

		width = max(96, width)

		imgLeft = ImageBox()
		imgLeft.SetParent(self)
		imgLeft.AddFlag("not_pick")
		imgLeft.LoadImage("d:/ymir work/ui/pattern/border_c_left.tga")
		imgLeft.Show()

		imgCenter = ExpandedImageBox()
		imgCenter.SetParent(self)
		imgCenter.AddFlag("not_pick")
		imgCenter.LoadImage("d:/ymir work/ui/pattern/border_c_middle.tga")
		imgCenter.Show()

		imgRight = ImageBox()
		imgRight.SetParent(self)
		imgRight.AddFlag("not_pick")
		imgRight.LoadImage("d:/ymir work/ui/pattern/border_c_right.tga")
		imgRight.Show()

		self.imgLeft = imgLeft
		self.imgCenter = imgCenter
		self.imgRight = imgRight
		self.SetWidth(width)

	def SetWidth(self, width):
		self.imgCenter.SetRenderingRect(0.0, 0.0, float((width - self.BLOCK_WIDTH*2) - self.BLOCK_WIDTH) / self.BLOCK_WIDTH, 0.0)
		self.imgCenter.SetPosition(self.BLOCK_WIDTH, 0)
		self.imgRight.SetPosition(width - self.BLOCK_WIDTH, 0)
		self.SetSize(width, self.BLOCK_HEIGHT)


class HorizontalBar(Window):
	BLOCK_WIDTH = 32
	BLOCK_HEIGHT = 17

	def __init__(self):
		Window.__init__(self)
		self.AddFlag("attach")

	def __del__(self):
		Window.__del__(self)

	def Create(self, width):

		width = max(96, width)

		imgLeft = ImageBox()
		imgLeft.SetParent(self)
		imgLeft.AddFlag("not_pick")
		imgLeft.LoadImage("d:/ymir work/ui/pattern/horizontalbar_left.tga")
		imgLeft.Show()

		imgCenter = ExpandedImageBox()
		imgCenter.SetParent(self)
		imgCenter.AddFlag("not_pick")
		imgCenter.LoadImage("d:/ymir work/ui/pattern/horizontalbar_center.tga")
		imgCenter.Show()

		imgRight = ImageBox()
		imgRight.SetParent(self)
		imgRight.AddFlag("not_pick")
		imgRight.LoadImage("d:/ymir work/ui/pattern/horizontalbar_right.tga")
		imgRight.Show()

		self.imgLeft = imgLeft
		self.imgCenter = imgCenter
		self.imgRight = imgRight
		self.SetWidth(width)

	def SetWidth(self, width):
		self.imgCenter.SetRenderingRect(0.0, 0.0, float((width - self.BLOCK_WIDTH*2) - self.BLOCK_WIDTH) / self.BLOCK_WIDTH, 0.0)
		self.imgCenter.SetPosition(self.BLOCK_WIDTH, 0)
		self.imgRight.SetPosition(width - self.BLOCK_WIDTH, 0)
		self.SetSize(width, self.BLOCK_HEIGHT)

class Gauge(Window):
	SLOT_WIDTH = 16
	SLOT_HEIGHT = 7

	GAUGE_TEMPORARY_PLACE = 12
	GAUGE_WIDTH = 16

	def __init__(self):
		Window.__init__(self)
		self.width = 0
		self.showtooltipevent = None
		self.showtooltiparg = None
		self.hidetooltipevent = None
		self.hidetooltiparg = None
		self.ToolTipText = None

	def __del__(self):
		Window.__del__(self)
		self.showtooltipevent = None
		self.showtooltiparg = None
		self.hidetooltipevent = None
		self.hidetooltiparg = None

	def MakeGauge(self, width, color):
		self.width = max(48, width)

		imgSlotLeft = ImageBox()
		imgSlotLeft.SetParent(self)
		imgSlotLeft.LoadImage("d:/ymir work/ui/pattern/gauge_slot_left.tga")
		imgSlotLeft.Show()

		imgSlotRight = ImageBox()
		imgSlotRight.SetParent(self)
		imgSlotRight.LoadImage("d:/ymir work/ui/pattern/gauge_slot_right.tga")
		imgSlotRight.Show()
		imgSlotRight.SetPosition(width - self.SLOT_WIDTH, 0)

		imgSlotCenter = ExpandedImageBox()
		imgSlotCenter.SetParent(self)
		imgSlotCenter.LoadImage("d:/ymir work/ui/pattern/gauge_slot_center.tga")
		imgSlotCenter.Show()
		imgSlotCenter.SetRenderingRect(0.0, 0.0, float((width - self.SLOT_WIDTH*2) - self.SLOT_WIDTH) / self.SLOT_WIDTH, 0.0)
		imgSlotCenter.SetPosition(self.SLOT_WIDTH, 0)

		if osfinfo.PAST_HEALTH_ON_TARGET:
			imgGaugeBack = ExpandedImageBox()
			imgGaugeBack.SetParent(self)
			imgGaugeBack.LoadImage("d:/ymir work/ui/pattern/gauge_yellow.tga")
			imgGaugeBack.Hide()
			imgGaugeBack.SetRenderingRect(0.0, 0.0, 0.0, 0.0)
			imgGaugeBack.SetPosition(self.GAUGE_TEMPORARY_PLACE, 0)

		imgGauge = ExpandedImageBox()
		imgGauge.SetParent(self)
		imgGauge.LoadImage("d:/ymir work/ui/pattern/gauge_" + color + ".tga")
		imgGauge.Show()
		imgGauge.SetRenderingRect(0.0, 0.0, 0.0, 0.0)
		imgGauge.SetPosition(self.GAUGE_TEMPORARY_PLACE, 0)

		imgSlotLeft.AddFlag("attach")
		imgSlotCenter.AddFlag("attach")
		imgSlotRight.AddFlag("attach")

		if app.WJ_SHOW_PARTY_ON_MINIMAP:
			imgSlotLeft.AddFlag("not_pick")
			imgSlotCenter.AddFlag("not_pick")
			imgSlotRight.AddFlag("not_pick")
			imgGauge.AddFlag("not_pick")

		self.imgLeft = imgSlotLeft
		self.imgCenter = imgSlotCenter
		self.imgRight = imgSlotRight
		self.imgGauge = imgGauge
		if osfinfo.PAST_HEALTH_ON_TARGET:
			self.imgGaugeBack = imgGaugeBack
		self.curValue = 100
		self.maxValue = 100
		self.currentGaugeColor = color

		self.SetSize(width, self.SLOT_HEIGHT)
		
	def SetColor(self, color):
		if (self.currentGaugeColor == color):
			return
			
		self.currentGaugeColor = color
		self.imgGauge.LoadImage("d:/ymir work/ui/pattern/gauge_" + color + ".tga")
		self.SetPercentage(self.curValue, self.maxValue)

	def SetPercentage(self, curValue, maxValue):
		# PERCENTAGE_MAX_VALUE_ZERO_DIVISION_ERROR
		if maxValue > 0.0:
			percentage = min(1.0, float(curValue)/float(maxValue))
		else:
			percentage = 0.0
		# END_OF_PERCENTAGE_MAX_VALUE_ZERO_DIVISION_ERROR

		self.curValue = curValue
		self.maxValue = maxValue

		if osfinfo.PAST_HEALTH_ON_TARGET:
			self.lastCurValue = curValue
			self.lastMaxValue = maxValue

		gaugeSize = -1.0 + float(self.width - self.GAUGE_TEMPORARY_PLACE*2) * percentage / self.GAUGE_WIDTH
		self.imgGauge.SetRenderingRect(0.0, 0.0, gaugeSize, 0.0)

	if app.WJ_SHOW_PARTY_ON_MINIMAP:
		def GaugeImgBoxAddFlag(self, flag):
			self.imgLeft.AddFlag(flag)
			self.imgCenter.AddFlag(flag)
			self.imgRight.AddFlag(flag)
			self.imgGauge.AddFlag(flag)

	if osfinfo.PAST_HEALTH_ON_TARGET:
		def SetPercentageBack(self, curValue, maxValue):
			if not self.imgGaugeBack.IsShow():
				self.imgGaugeBack.Show()

			if maxValue > 0.0:
				percentage = min(1.0, float(curValue)/float(maxValue))
			else:
				percentage = 0.0

			gaugeSize = -1.0 + float(self.width - self.GAUGE_TEMPORARY_PLACE*2) * percentage / self.GAUGE_WIDTH
			self.imgGaugeBack.SetRenderingRect(0.0, 0.0, gaugeSize, 0.0)
	def SetShowToolTipEvent(self, func, *args):

		self.showtooltipevent = func
		self.showtooltiparg = args

	def SetHideToolTipEvent(self, func, *args):
		self.hidetooltipevent = func
		self.hidetooltiparg = args

	def ShowToolTip(self):
		if self.ToolTipText:
			self.ToolTipText.Show()

	def HideToolTip(self):
		if self.ToolTipText:
			self.ToolTipText.Hide()

	def SetToolTipText(self, text, x=0, y = -19):
		self.SetFormToolTipText("TEXT", text, x, y)

	def SetFormToolTipText(self, type, text, x, y):
		if not self.ToolTipText:       
			toolTip=createToolTipWindowDict[type]()
			toolTip.SetParent(self)
			toolTip.SetSize(0, 0)
			toolTip.SetHorizontalAlignCenter()
			toolTip.SetOutline()
			toolTip.Hide()
			toolTip.SetPosition(x + self.GetWidth()/2, y)
			self.ToolTipText=toolTip
		self.ToolTipText.SetText(text)

class BorderA(Window):
	CORNER_WIDTH = 16
	CORNER_HEIGHT = 16
	LINE_WIDTH = 16
	LINE_HEIGHT = 16
	BOARD_COLOR = grp.GenerateColor(0.17, 0.027, 0.0, 0.70)


	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		CornerFileNames = [ "d:/ymir work/ui/pattern/border_a/border_a_"+dir+".tga" for dir in ["Left_Top","Left_Bottom","Right_Top","Right_Bottom"] ]
		LineFileNames = [ "d:/ymir work/ui/pattern/border_a/border_a_"+dir+".tga" for dir in ["Left","Right","Top","Bottom"] ]
		#BaseFileName = "d:/ymir work/ui/pattern/border_a/border_center.tga"
		
		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		self.Base = ExpandedImageBox()
		self.Base.AddFlag("not_pick")
		self.Base.LoadImage("d:/ymir work/ui/pattern/border_a/border_a_center.tga")
		self.Base.SetParent(self)
		self.Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Base.Show()
		
		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def __del__(self):
		Window.__del__(self)

	def SetSize(self, width, height):

		width = max(self.CORNER_WIDTH*2, width)
		height = max(self.CORNER_HEIGHT*2, height)
		Window.SetSize(self, width, height)

		self.Corners[self.LB].SetPosition(0, height - self.CORNER_HEIGHT)
		self.Corners[self.RT].SetPosition(width - self.CORNER_WIDTH, 0)
		self.Corners[self.RB].SetPosition(width - self.CORNER_WIDTH, height - self.CORNER_HEIGHT)
		self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Lines[self.B].SetPosition(self.CORNER_HEIGHT, height - self.CORNER_HEIGHT)

		verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.LINE_HEIGHT) / self.LINE_HEIGHT
		horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.LINE_WIDTH) / self.LINE_WIDTH
		self.Lines[self.L].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.R].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.T].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		self.Lines[self.B].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)

		if self.Base:
			self.Base.SetRenderingRect(0, 0, horizontalShowingPercentage, verticalShowingPercentage)

	def ShowInternal(self):
		self.Base.Show()
		for wnd in self.Lines:
			wnd.Show()
		for wnd in self.Corners:
			wnd.Show()

	def HideInternal(self):
		self.Base.Hide()
		for wnd in self.Lines:
			wnd.Hide()
		for wnd in self.Corners:
			wnd.Hide()

# class Board(Window):
	# CORNER_WIDTH = 32
	# CORNER_HEIGHT = 32
	# LINE_WIDTH = 128
	# LINE_HEIGHT = 128

	# LT = 0
	# LB = 1
	# RT = 2
	# RB = 3
	# L = 0
	# R = 1
	# T = 2
	# B = 3

	# def __init__(self):
		# Window.__init__(self)
		# if app.ENABLE_IMAGE_CLIP_RECT:
			# self.skipMaxCheck = False

		# self.MakeBoard("d:/ymir work/ui/pattern/Board_Corner_", "d:/ymir work/ui/pattern/Board_Line_")
		# self.MakeBase()

	# def MakeBoard(self, cornerPath, linePath):

		# CornerFileNames = [ cornerPath+dir+".tga" for dir in ("LeftTop", "LeftBottom", "RightTop", "RightBottom", ) ]
		# LineFileNames = [ linePath+dir+".tga" for dir in ("Left", "Right", "Top", "Bottom", ) ]
		# """
		# CornerFileNames = (
							# "d:/ymir work/ui/pattern/Board_Corner_LeftTop.tga",
							# "d:/ymir work/ui/pattern/Board_Corner_LeftBottom.tga",
							# "d:/ymir work/ui/pattern/Board_Corner_RightTop.tga",
							# "d:/ymir work/ui/pattern/Board_Corner_RightBottom.tga",
							# )
		# LineFileNames = (
							# "d:/ymir work/ui/pattern/Board_Line_Left.tga",
							# "d:/ymir work/ui/pattern/Board_Line_Right.tga",
							# "d:/ymir work/ui/pattern/Board_Line_Top.tga",
							# "d:/ymir work/ui/pattern/Board_Line_Bottom.tga",
							# )
		# """

		# self.Corners = []
		# for fileName in CornerFileNames:
			# Corner = ExpandedImageBox()
			# Corner.AddFlag("not_pick")
			# Corner.LoadImage(fileName)
			# Corner.SetParent(self)
			# Corner.SetPosition(0, 0)
			# Corner.Show()
			# self.Corners.append(Corner)

		# self.Lines = []
		# for fileName in LineFileNames:
			# Line = ExpandedImageBox()
			# Line.AddFlag("not_pick")
			# Line.LoadImage(fileName)
			# Line.SetParent(self)
			# Line.SetPosition(0, 0)
			# Line.Show()
			# self.Lines.append(Line)

		# self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		# self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	# def MakeBase(self):
		# self.Base = ExpandedImageBox()
		# self.Base.AddFlag("not_pick")
		# self.Base.LoadImage("d:/ymir work/ui/pattern/Board_Base.tga")
		# self.Base.SetParent(self)
		# self.Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		# self.Base.Show()

	# def __del__(self):
		# Window.__del__(self)

	# def SetSize(self, width, height):
		# if app.ENABLE_IMAGE_CLIP_RECT:
			# if not self.skipMaxCheck:
				# width = max(self.CORNER_WIDTH * 2, width)
				# height = max(self.CORNER_HEIGHT * 2, height)
		# else:
			# width = max(self.CORNER_WIDTH * 2, width)
			# height = max(self.CORNER_HEIGHT * 2, height)
		# Window.SetSize(self, width, height)

		# self.Corners[self.LB].SetPosition(0, height - self.CORNER_HEIGHT)
		# self.Corners[self.RT].SetPosition(width - self.CORNER_WIDTH, 0)
		# self.Corners[self.RB].SetPosition(width - self.CORNER_WIDTH, height - self.CORNER_HEIGHT)
		# self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, self.CORNER_HEIGHT)
		# self.Lines[self.B].SetPosition(self.CORNER_HEIGHT, height - self.CORNER_HEIGHT)

		# verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.LINE_HEIGHT) / self.LINE_HEIGHT
		# horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.LINE_WIDTH) / self.LINE_WIDTH
		# self.Lines[self.L].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		# self.Lines[self.R].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		# self.Lines[self.T].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		# self.Lines[self.B].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)

		# if self.Base:
			# self.Base.SetRenderingRect(0, 0, horizontalShowingPercentage, verticalShowingPercentage)

class Board(Window):
	CORNER_WIDTH = 32
	CORNER_HEIGHT = 32
	LINE_WIDTH = 128
	LINE_HEIGHT = 128

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3
	
	BASE_PATH = "d:/ymir work/ui/pattern"
	IMAGES = {
		'CORNER' : {
			0 : "Board_Corner_LeftTop",
			1 : "Board_Corner_LeftBottom",
			2 : "Board_Corner_RightTop",
			3 : "Board_Corner_RightBottom"
		},
		'BAR' : {
			0 : "Board_Line_Left",
			1 : "Board_Line_Right",
			2 : "Board_Line_Top",
			3 : "Board_Line_Bottom"
		},
		'FILL' : "Board_Base"
	}

	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.skipMaxCheck = False

		self.MakeBoard()
		
	def MakeBoard(self):
		CornerFileNames = [ ]
		LineFileNames = [ ]
		
		for imageDictKey in (['CORNER', 'BAR']):
			for x in xrange(len(self.IMAGES[imageDictKey])):
				if imageDictKey == "CORNER":
					CornerFileNames.append("%s/%s.tga" % (self.BASE_PATH, self.IMAGES[imageDictKey][x]))
				elif imageDictKey == "BAR":
					LineFileNames.append("%s/%s.tga" % (self.BASE_PATH, self.IMAGES[imageDictKey][x]))
		
		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

		self.Base = ExpandedImageBox()
		self.Base.AddFlag("not_pick")
		self.Base.LoadImage("%s/%s.tga" % (self.BASE_PATH, self.IMAGES['FILL']))
		self.Base.SetParent(self)
		self.Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Base.Show()

	def __del__(self):
		Window.__del__(self)

	def SetSize(self, width, height):
		if not self.skipMaxCheck:
			width = max(self.CORNER_WIDTH*2, width)
			height = max(self.CORNER_HEIGHT*2, height)
			
		Window.SetSize(self, width, height)

		self.Corners[self.LB].SetPosition(0, height - self.CORNER_HEIGHT)
		self.Corners[self.RT].SetPosition(width - self.CORNER_WIDTH, 0)
		self.Corners[self.RB].SetPosition(width - self.CORNER_WIDTH, height - self.CORNER_HEIGHT)
		self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Lines[self.B].SetPosition(self.CORNER_HEIGHT, height - self.CORNER_HEIGHT)

		verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.LINE_HEIGHT) / self.LINE_HEIGHT
		horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.LINE_WIDTH) / self.LINE_WIDTH
		self.Lines[self.L].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.R].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.T].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		self.Lines[self.B].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)

		if self.Base:
			self.Base.SetRenderingRect(0, 0, horizontalShowingPercentage, verticalShowingPercentage)

class BoardNew(Window):
	CORNER_WIDTH = 32
	CORNER_HEIGHT = 32
	LINE_WIDTH = 128
	LINE_HEIGHT = 128

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3
	
	BASE_PATH = "d:/ymir work/ui/pattern/newdragonetc"
	IMAGES = {
		'CORNER' : {
			0 : "Board_Corner_LeftTop",
			1 : "Board_Corner_LeftBottom",
			2 : "Board_Corner_RightTop",
			3 : "Board_Corner_RightBottom"
		},
		'BAR' : {
			0 : "Board_Line_Left",
			1 : "Board_Line_Right",
			2 : "Board_Line_Top",
			3 : "Board_Line_Bottom"
		},
		'FILL' : "Board_Base"
	}

	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.skipMaxCheck = False

		self.MakeBoard()
		
	def MakeBoard(self):
		CornerFileNames = [ ]
		LineFileNames = [ ]
		
		for imageDictKey in (['CORNER', 'BAR']):
			for x in xrange(len(self.IMAGES[imageDictKey])):
				if imageDictKey == "CORNER":
					CornerFileNames.append("%s/%s.tga" % (self.BASE_PATH, self.IMAGES[imageDictKey][x]))
				elif imageDictKey == "BAR":
					LineFileNames.append("%s/%s.tga" % (self.BASE_PATH, self.IMAGES[imageDictKey][x]))
		
		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

		self.Base = ExpandedImageBox()
		self.Base.AddFlag("not_pick")
		self.Base.LoadImage("%s/%s.tga" % (self.BASE_PATH, self.IMAGES['FILL']))
		self.Base.SetParent(self)
		self.Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Base.Show()
		self.baseImgW = self.Base.GetWidth()
		self.baseImgH = self.Base.GetHeight()

	def __del__(self):
		Window.__del__(self)

	def SetSize(self, width, height):
		if not self.skipMaxCheck:
			width = max(self.CORNER_WIDTH*2, width)
			height = max(self.CORNER_HEIGHT*2, height)
			
		Window.SetSize(self, width, height)

		self.Corners[self.LB].SetPosition(0, height - self.CORNER_HEIGHT)
		self.Corners[self.RT].SetPosition(width - self.CORNER_WIDTH, 0)
		self.Corners[self.RB].SetPosition(width - self.CORNER_WIDTH, height - self.CORNER_HEIGHT)
		self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Lines[self.B].SetPosition(self.CORNER_HEIGHT, height - self.CORNER_HEIGHT)

		verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.LINE_HEIGHT) / self.LINE_HEIGHT
		horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.LINE_WIDTH) / self.LINE_WIDTH
		self.Lines[self.L].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.R].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.T].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		self.Lines[self.B].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)

		if self.Base:
			baseW = getattr(self, "baseImgW", 0) or self.LINE_WIDTH
			baseH = getattr(self, "baseImgH", 0) or self.LINE_HEIGHT
			self.Base.SetRenderingRect(0, 0,
				float(width - self.CORNER_WIDTH * 2) / baseW - 1.0,
				float(height - self.CORNER_HEIGHT * 2) / baseH - 1.0)


class SibBoard(Window):

	CORNER_WIDTH = 16
	CORNER_HEIGHT = 16
	LINE_WIDTH = 16
	LINE_HEIGHT = 16

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self):
		Window.__init__(self)

		self.MakeBoard("d:/ymir work/ui/pattern/border_a_", "d:/ymir work/ui/pattern/border_a_")
		self.MakeBase()

	def MakeBoard(self, cornerPath, linePath):

		CornerFileNames = [ cornerPath+dir+".tga" for dir in ("Left_Top", "Left_Bottom", "Right_Top", "Right_Bottom", ) ]
		LineFileNames = [ linePath+dir+".tga" for dir in ("Left", "Right", "Top", "Bottom", ) ]

		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def MakeBase(self):
		self.Base = ExpandedImageBox()
		self.Base.AddFlag("not_pick")
		self.Base.LoadImage("d:/ymir work/ui/pattern/border_a_center.tga")
		self.Base.SetParent(self)
		self.Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Base.Show()

	def __del__(self):
		Window.__del__(self)

	def SetSize(self, width, height):

		width = max(self.CORNER_WIDTH*2, width)
		height = max(self.CORNER_HEIGHT*2, height)
		Window.SetSize(self, width, height)

		self.Corners[self.LB].SetPosition(0, height - self.CORNER_HEIGHT)
		self.Corners[self.RT].SetPosition(width - self.CORNER_WIDTH, 0)
		self.Corners[self.RB].SetPosition(width - self.CORNER_WIDTH, height - self.CORNER_HEIGHT)
		self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Lines[self.B].SetPosition(self.CORNER_HEIGHT, height - self.CORNER_HEIGHT)

		verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.LINE_HEIGHT) / self.LINE_HEIGHT
		horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.LINE_WIDTH) / self.LINE_WIDTH
		self.Lines[self.L].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.R].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.T].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		self.Lines[self.B].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)

		if self.Base:
			self.Base.SetRenderingRect(0, 0, horizontalShowingPercentage, verticalShowingPercentage)


class BorderB(Board):
	CORNER_WIDTH = 16
	CORNER_HEIGHT = 16
	LINE_WIDTH = 16
	LINE_HEIGHT = 16
	
	BASE_PATH = "d:/ymir work/ui/pattern"

	IMAGES = {
		'CORNER' : {
			0 : "border_b_left_top",
			1 : "border_b_left_bottom",
			2 : "border_b_right_top",
			3 : "border_b_right_bottom"
		},
		'BAR' : {
			0 : "border_b_left",
			1 : "border_b_right",
			2 : "border_b_top",
			3 : "border_b_bottom"
		},
		'FILL' : "border_b_center"
	}
	
	def __init__(self):
		Board.__init__(self)
			
		self.eventFunc = {
			"MOUSE_LEFT_BUTTON_UP" : None, 
		}
		self.eventArgs = {
			"MOUSE_LEFT_BUTTON_UP" : None, 
		}

	def __del__(self):
		Board.__del__(self)
		self.eventFunc = None
		self.eventArgs = None

	def SetSize(self, width, height):
		Board.SetSize(self, width, height)
		
	def SetEvent(self, func, *args) :
		result = self.eventFunc.has_key(args[0])		
		if result :
			self.eventFunc[args[0]] = func
			self.eventArgs[args[0]] = args
		else :
			print "[ERROR] ui.py SetEvent, Can`t Find has_key : %s" % args[0]
			
	def OnMouseLeftButtonUp(self):
		if self.eventFunc["MOUSE_LEFT_BUTTON_UP"] :
			apply(self.eventFunc["MOUSE_LEFT_BUTTON_UP"], self.eventArgs["MOUSE_LEFT_BUTTON_UP"])


class BoardDragon(Window):
	CORNER_WIDTH = 32
	CORNER_HEIGHT = 32
	LINE_WIDTH = 128
	LINE_HEIGHT = 128

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self):
		Window.__init__(self)
		if app.ENABLE_IMAGE_CLIP_RECT:
			self.skipMaxCheck = False

		self.MakeBoard("d:/ymir work/ui/Board_Corner_", "d:/ymir work/ui/Board_Line_")
		self.MakeBase()

	def MakeBoard(self, cornerPath, linePath):

		CornerFileNames = [ cornerPath+dir+".tga" for dir in ("LeftTop", "LeftBottom", "RightTop", "RightBottom", ) ]
		LineFileNames = [ linePath+dir+".tga" for dir in ("Left", "Right", "Top", "Bottom", ) ]
		"""
		CornerFileNames = (
							"d:/ymir work/ui/pattern/Board_Corner_LeftTop.tga",
							"d:/ymir work/ui/pattern/Board_Corner_LeftBottom.tga",
							"d:/ymir work/ui/pattern/Board_Corner_RightTop.tga",
							"d:/ymir work/ui/pattern/Board_Corner_RightBottom.tga",
							)
		LineFileNames = (
							"d:/ymir work/ui/pattern/Board_Line_Left.tga",
							"d:/ymir work/ui/pattern/Board_Line_Right.tga",
							"d:/ymir work/ui/pattern/Board_Line_Top.tga",
							"d:/ymir work/ui/pattern/Board_Line_Bottom.tga",
							)
		"""

		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def MakeBase(self):
		self.Base = ExpandedImageBox()
		self.Base.AddFlag("not_pick")
		self.Base.LoadImage("d:/ymir work/ui/Board_Base.tga")
		self.Base.SetParent(self)
		self.Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Base.Show()

	def __del__(self):
		Window.__del__(self)

	def SetSize(self, width, height):
		if app.ENABLE_IMAGE_CLIP_RECT:
			if not self.skipMaxCheck:
				width = max(self.CORNER_WIDTH * 2, width)
				height = max(self.CORNER_HEIGHT * 2, height)
		else:
			width = max(self.CORNER_WIDTH * 2, width)
			height = max(self.CORNER_HEIGHT * 2, height)
		Window.SetSize(self, width, height)

		self.Corners[self.LB].SetPosition(0, height - self.CORNER_HEIGHT)
		self.Corners[self.RT].SetPosition(width - self.CORNER_WIDTH, 0)
		self.Corners[self.RB].SetPosition(width - self.CORNER_WIDTH, height - self.CORNER_HEIGHT)
		self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Lines[self.B].SetPosition(self.CORNER_HEIGHT, height - self.CORNER_HEIGHT)

		verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.LINE_HEIGHT) / self.LINE_HEIGHT
		horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.LINE_WIDTH) / self.LINE_WIDTH
		self.Lines[self.L].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.R].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.T].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		self.Lines[self.B].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)

		if self.Base:
			self.Base.SetRenderingRect(0, 0, horizontalShowingPercentage, verticalShowingPercentage)

class BoardWithTitleBar(Board):
	def __init__(self, withButton = False):
		Board.__init__(self)
		self.withButton = withButton
		titleBar = TitleBar()
		if self.withButton is True:
			titleBar = TitleBarWithoutButton()
		titleBar.SetParent(self)
		titleBar.MakeTitleBar(0, "red")
		titleBar.SetPosition(8, 7)
		titleBar.Show()

		titleName = TextLine()
		titleName.SetParent(titleBar)
		titleName.SetPosition(0, 2)
		titleName.SetWindowHorizontalAlignCenter()
		titleName.SetHorizontalAlignCenter()
		titleName.Show()

		self.titleBar = titleBar
		self.titleName = titleName

		if self.withButton is False:
			self.SetCloseEvent(self.Hide)

	def __del__(self):
		Board.__del__(self)
		self.titleBar = None
		self.titleName = None

	def SetSize(self, width, height):
		self.titleBar.SetWidth(width - 15)
		#self.pickRestrictWindow.SetSize(width, height - 30)
		Board.SetSize(self, width, height)
		self.titleName.UpdateRect()

	def SetTitleColor(self, color):
		self.titleName.SetPackedFontColor(color)

	def SetTitleName(self, name):
		self.titleName.SetText(name)

	def SetCloseEvent(self, event):
		if self.withButton is False:
			self.titleBar.SetCloseEvent(event)

class BoardNewWithTitleBar(BoardNew):
	def __init__(self, withButton = False):
		BoardNew.__init__(self)
		self.withButton = withButton
		titleBar = TitleBar()
		if self.withButton is True:
			titleBar = TitleBarWithoutButton()
		titleBar.SetParent(self)
		titleBar.MakeTitleBar(0, "red")
		titleBar.SetPosition(8, 7)
		titleBar.Show()

		titleName = TextLine()
		titleName.SetParent(titleBar)
		titleName.SetPosition(0, 2)
		titleName.SetWindowHorizontalAlignCenter()
		titleName.SetHorizontalAlignCenter()
		titleName.Show()

		self.titleBar = titleBar
		self.titleName = titleName

		if self.withButton is False:
			self.SetCloseEvent(self.Hide)

	def __del__(self):
		BoardNew.__del__(self)
		self.titleBar = None
		self.titleName = None

	def SetSize(self, width, height):
		self.titleBar.SetWidth(width - 15)
		#self.pickRestrictWindow.SetSize(width, height - 30)
		BoardNew.SetSize(self, width, height)
		self.titleName.UpdateRect()

	def SetTitleColor(self, color):
		self.titleName.SetPackedFontColor(color)

	def SetTitleName(self, name):
		self.titleName.SetText(name)

	def SetCloseEvent(self, event):
		if self.withButton is False:
			self.titleBar.SetCloseEvent(event)

class ThinBoard(Window):
	CORNER_WIDTH = 16
	CORNER_HEIGHT = 16
	LINE_WIDTH = 16
	LINE_HEIGHT = 16
	BOARD_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 0.51)

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	#if app.USE_DUNGEON_INFO
	def __init__(self, layer = "UI", v = 1):
		Window.__init__(self, layer)

		# v2 uses the new_thinboard reskin (textured base.png fill); v1/v3 keep the flat Bar.
		self.baseIsImage = bool((app.USE_DUNGEON_INFO or app.USE_LOG_EXCHANGE) and v == 2)

		if (app.USE_DUNGEON_INFO or app.USE_LOG_EXCHANGE) and v == 2:
			# >>> new_thinboard reskin BEGIN - dropped v2_thinboard_* assets, load the new designs
			# CornerFileNames = [ "d:/ymir work/ui/pattern/v2_thinboard_corner_" + dir + ".tga" for dir in ["lefttop", "leftbottom", "righttop", "rightbottom"] ]
			# LineFileNames = [ "d:/ymir work/ui/pattern/v2_thinboard_line_" + dir + ".tga" for dir in ["left", "right", "top", "bottom"] ]
			CornerFileNames = [ "d:/ymir work/ui/pattern/new_thinboard/thinboard_corner_" + dir + ".png" for dir in ["lefttop", "leftbottom", "righttop", "rightbottom"] ]
			LineFileNames = [ "d:/ymir work/ui/pattern/new_thinboard/thinboard_line_" + dir + ".png" for dir in ["left", "right", "top", "bottom"] ]
			# <<< new_thinboard reskin END
		elif (app.USE_DUNGEON_INFO or app.USE_LOG_EXCHANGE) and v == 3:
			CornerFileNames = [ "d:/ymir work/ui/pattern/v3_thinboard_corner_" + dir + ".tga" for dir in ["lefttop", "leftbottom", "righttop", "rightbottom"] ]
			LineFileNames = [ "d:/ymir work/ui/pattern/v3_thinboard_line_" + dir + ".tga" for dir in ["left", "right", "top", "bottom"] ]
		else:
			CornerFileNames = [ "d:/ymir work/ui/pattern/thinboard_corner_"+dir+".tga" for dir in ["lefttop", "leftbottom", "righttop", "rightbottom"] ]
			LineFileNames = [ "d:/ymir work/ui/pattern/thinboard_line_"+dir+".tga" for dir in ["left", "right", "top", "bottom"] ]

		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("attach")
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("attach")
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		if self.baseIsImage:
			# >>> new_thinboard reskin BEGIN - textured base.png fill instead of the flat Bar
			Base = ExpandedImageBox()
			Base.AddFlag("attach")
			Base.AddFlag("not_pick")
			Base.LoadImage("d:/ymir work/ui/pattern/new_thinboard/base.png")
			Base.SetParent(self)
			Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
			Base.Show()
			# <<< new_thinboard reskin END
		else:
			Base = Bar()
			Base.SetParent(self)
			Base.AddFlag("attach")
			Base.AddFlag("not_pick")
			Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
			Base.SetColor(self.BOARD_COLOR)
			Base.Show()
		self.Base = Base

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def __del__(self):
		Window.__del__(self)

	def ShowCorner(self, corner):
		self.Corners[corner].Show()
		self.SetSize(self.GetWidth(), self.GetHeight())

	def HideCorners(self, corner):
		self.Corners[corner].Hide()
		self.SetSize(self.GetWidth(), self.GetHeight())

	def ShowLine(self, line):
		self.Lines[line].Show()
		self.SetSize(self.GetWidth(), self.GetHeight())

	def HideLine(self, line):
		self.Lines[line].Hide()
		self.SetSize(self.GetWidth(), self.GetHeight())

	def SetSize(self, width, height):

		width = max(self.CORNER_WIDTH*2, width)
		height = max(self.CORNER_HEIGHT*2, height)
		Window.SetSize(self, width, height)

		if self.Corners[self.LT].IsShow():
			self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
			self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)
		else:
			self.Lines[self.L].SetPosition(0, 0)
			self.Lines[self.T].SetPosition(0, 0)

		self.Corners[self.LB].SetPosition(0, height - self.CORNER_HEIGHT)
		self.Corners[self.RT].SetPosition(width - self.CORNER_WIDTH, 0)
		self.Corners[self.RB].SetPosition(width - self.CORNER_WIDTH, height - self.CORNER_HEIGHT)

		if self.Corners[self.RT].IsShow():
			self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, self.CORNER_HEIGHT)
		else:
			self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, 0)
		if self.Corners[self.LB].IsShow():
			self.Lines[self.B].SetPosition(self.CORNER_HEIGHT, height - self.CORNER_HEIGHT)
		else:
			self.Lines[self.B].SetPosition(0, height - self.CORNER_HEIGHT)

		cornerCount = {}
		cornerCount[self.L] = self.Corners[self.LB].IsShow() + self.Corners[self.LT].IsShow()
		cornerCount[self.R] = self.Corners[self.RB].IsShow() + self.Corners[self.RT].IsShow()
		cornerCount[self.T] = self.Corners[self.LT].IsShow() + self.Corners[self.RT].IsShow()
		cornerCount[self.B] = self.Corners[self.LB].IsShow() + self.Corners[self.RB].IsShow()

		self.Lines[self.L].SetRenderingRect(0, 0, 0, float(height - self.LINE_HEIGHT - self.CORNER_HEIGHT * cornerCount[self.L]) / self.LINE_HEIGHT)
		self.Lines[self.R].SetRenderingRect(0, 0, 0, float(height - self.LINE_HEIGHT - self.CORNER_HEIGHT * cornerCount[self.R]) / self.LINE_HEIGHT)
		self.Lines[self.T].SetRenderingRect(0, 0, float(width - self.LINE_WIDTH - self.CORNER_WIDTH * cornerCount[self.T]) / self.LINE_WIDTH, 0)
		self.Lines[self.B].SetRenderingRect(0, 0, float(width - self.LINE_WIDTH - self.CORNER_WIDTH * cornerCount[self.B]) / self.LINE_WIDTH, 0)

		lineCount = []
		lineCount.append(self.Lines[self.T].IsShow() + self.Lines[self.B].IsShow())
		lineCount.append(self.Lines[self.L].IsShow() + self.Lines[self.R].IsShow())

		if self.Lines[self.L].IsShow():
			self.Base.SetPosition(self.CORNER_WIDTH, self.Base.GetTop())
		else:
			self.Base.SetPosition(0, self.Base.GetTop())
		if self.Lines[self.T].IsShow():
			self.Base.SetPosition(self.Base.GetLeft(), self.CORNER_HEIGHT)
		else:
			self.Base.SetPosition(self.Base.GetLeft(), 0)

		baseW = width - self.CORNER_WIDTH*lineCount[1]
		baseH = height - self.CORNER_HEIGHT*lineCount[0]
		self.Base.SetSize(baseW, baseH)
		if self.baseIsImage:
			# stretch the 16x16 base.png tile to fill the interior (same expansion math as the lines)
			self.Base.SetRenderingRect(0.0, 0.0, float(baseW - self.LINE_WIDTH) / self.LINE_WIDTH, float(baseH - self.LINE_HEIGHT) / self.LINE_HEIGHT)

	def ShowInternal(self):
		self.Base.Show()
		for wnd in self.Lines:
			wnd.Show()
		for wnd in self.Corners:
			wnd.Show()

	def HideInternal(self):
		self.Base.Hide()
		for wnd in self.Lines:
			wnd.Hide()
		for wnd in self.Corners:
			wnd.Hide()

	def SetAlpha(self, alpha):
		color  = grp.GenerateColor(0.0, 0.0, 0.0, alpha)
		self.Base.SetColor(color)
		for wnd in self.Lines:
			wnd.SetAlpha(alpha)
		for wnd in self.Corners:
			wnd.SetAlpha(alpha)

class ThinBoardGold(Window):
	CORNER_WIDTH = 16
	CORNER_HEIGHT = 16
	LINE_WIDTH = 16
	LINE_HEIGHT = 16

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		CornerFileNames = [ "d:/ymir work/ui/pattern/thinboardgold/ThinBoard_Corner_"+dir+"_Gold.tga" for dir in ["LeftTop","LeftBottom","RightTop","RightBottom"] ]
		LineFileNames = [ "d:/ymir work/ui/pattern/thinboardgold/ThinBoard_Line_"+dir+"_Gold.tga" for dir in ["Left","Right","Top","Bottom"] ]

		self.MakeBase()

		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("attach")
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("attach")
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def __del__(self):
		Window.__del__(self)

	def SetSize(self, width, height):

		width = max(self.CORNER_WIDTH*2, width)
		height = max(self.CORNER_HEIGHT*2, height)
		Window.SetSize(self, width, height)

		self.Corners[self.LB].SetPosition(0, height - self.CORNER_HEIGHT)
		self.Corners[self.RT].SetPosition(width - self.CORNER_WIDTH, 0)
		self.Corners[self.RB].SetPosition(width - self.CORNER_WIDTH, height - self.CORNER_HEIGHT)
		self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Lines[self.B].SetPosition(self.CORNER_HEIGHT, height - self.CORNER_HEIGHT)

		verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.LINE_HEIGHT) / self.LINE_HEIGHT
		horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.LINE_WIDTH) / self.LINE_WIDTH

		self.Lines[self.L].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.R].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.T].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		self.Lines[self.B].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)

		#self.Base.GetWidth()
		#self.Base.GetHeight()
		"""
			Defalt Width : 128, Height : 128 
			0.0 > 128, 1.0 > 256 
		"""
		if self.Base:
			self.Base.SetRenderingRect(0, 0, (float(width)-32)/float(self.Base.GetWidth()) - 1.0, (float(height)-32)/float(self.Base.GetHeight()) - 1.0)

	def MakeBase(self):
		self.Base = ExpandedImageBox()
		self.Base.AddFlag("not_pick")
		self.Base.LoadImage("d:/ymir work/ui/pattern/Board_Base.tga")
		self.Base.SetParent(self)
		self.Base.SetPosition(16, 16)
		self.Base.SetAlpha(0.8)
		self.Base.Show()

	def ShowInternal(self):
		self.Base.Show()
		for wnd in self.Lines:
			wnd.Show()
		for wnd in self.Corners:
			wnd.Show()

	def HideInternal(self):
		self.Base.Hide()
		for wnd in self.Lines:
			wnd.Hide()
		for wnd in self.Corners:
			wnd.Hide()

class NewBoard(Window):
	CORNER_WIDTH = 32
	CORNER_HEIGHT = 32
	LINE_WIDTH = 128
	LINE_HEIGHT = 128
	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self):
		Window.__init__(self)
		self.MakeBoard("d:/ymir work/ui/pattern/new_board/Board_Corner_", "d:/ymir work/ui/pattern/new_board/Board_Line_")
		self.MakeBase()

	def MakeBoard(self, cornerPath, linePath):

		CornerFileNames = [ cornerPath+dir+".tga" for dir in ("LeftTop", "LeftBottom", "RightTop", "RightBottom", ) ]
		LineFileNames = [ linePath+dir+".tga" for dir in ("Left", "Right", "Top", "Bottom", ) ]
		
		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def MakeBase(self):
		self.Base = ExpandedImageBox()
		self.Base.AddFlag("not_pick")
		self.Base.LoadImage("d:/ymir work/ui/pattern/new_board/Board_Base.tga")
		self.Base.SetParent(self)
		self.Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Base.Show()

	def __del__(self):
		Window.__del__(self)

	def SetSize(self, width, height):
		width = max(self.CORNER_WIDTH*2, width)
		height = max(self.CORNER_HEIGHT*2, height)
		Window.SetSize(self, width, height)

		self.Corners[self.LB].SetPosition(0, height - self.CORNER_HEIGHT)
		self.Corners[self.RT].SetPosition(width - self.CORNER_WIDTH, 0)
		self.Corners[self.RB].SetPosition(width - self.CORNER_WIDTH, height - self.CORNER_HEIGHT)
		self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Lines[self.B].SetPosition(self.CORNER_HEIGHT, height - self.CORNER_HEIGHT)

		verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.LINE_HEIGHT) / self.LINE_HEIGHT
		horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.LINE_WIDTH) / self.LINE_WIDTH
		self.Lines[self.L].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.R].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.T].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		self.Lines[self.B].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)

		if self.Base:
			self.Base.SetRenderingRect(0, 0, horizontalShowingPercentage, verticalShowingPercentage)

class NewBoardWithTitleBar(NewBoard):
	def __init__(self, withButton = False):
		NewBoard.__init__(self)

		self.withButton = withButton
		titleBar = TitleBar()
		if self.withButton is True:
			titleBar = TitleBarWithoutButton()
		titleBar.SetParent(self)
		titleBar.MakeTitleBar(0, "red")
		titleBar.SetPosition(8, 7)
		titleBar.Show()

		titleName = TextLine()
		titleName.SetParent(titleBar)
		titleName.SetPosition(0, 4)
		titleName.SetWindowHorizontalAlignCenter()
		titleName.SetHorizontalAlignCenter()
		titleName.Show()

		self.titleBar = titleBar
		self.titleName = titleName

		if self.withButton is False:
			self.SetCloseEvent(self.Hide)

	def __del__(self):
		NewBoard.__del__(self)
		self.titleBar = None
		self.titleName = None

	def SetSize(self, width, height):
		self.titleBar.SetWidth(width - 15)
		#self.pickRestrictWindow.SetSize(width, height - 30)
		NewBoard.SetSize(self, width, height)
		self.titleName.UpdateRect()

	def SetTitleColor(self, color):
		self.titleName.SetPackedFontColor(color)

	def SetTitleName(self, name):
		self.titleName.SetText(name)

	def SetCloseEvent(self, event):
		if self.withButton is False:
			self.titleBar.SetCloseEvent(event)

class ThinBoardCircle(Window):
	CORNER_WIDTH = 4
	CORNER_HEIGHT = 4
	LINE_WIDTH = 4
	LINE_HEIGHT = 4
	BOARD_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
	BOARD_COLOR_IN = grp.GenerateColor(0.0, 0.0, 0.7, 0.7)
	BOARD_COLOR_OUT = grp.GenerateColor(0.0, 0.0, 0.0, 0.51)

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		CornerFileNames = [ "d:/ymir work/ui/pattern/thinboardcircle/ThinBoard_Corner_"+dir+"_Circle.tga" for dir in ["LeftTop","LeftBottom","RightTop","RightBottom"] ]
		LineFileNames = [ "d:/ymir work/ui/pattern/thinboardcircle/ThinBoard_Line_"+dir+"_Circle.tga" for dir in ["Left","Right","Top","Bottom"] ]

		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("attach")
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("attach")
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		Base = Bar()
		Base.SetParent(self)
		Base.AddFlag("attach")
		Base.AddFlag("not_pick")
		Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		Base.SetColor(self.BOARD_COLOR)
		Base.Show()
		self.Base = Base

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def __del__(self):
		Window.__del__(self)

	def SetSize(self, width, height):

		width = max(self.CORNER_WIDTH*2, width)
		height = max(self.CORNER_HEIGHT*2, height)
		Window.SetSize(self, width, height)

		self.Corners[self.LB].SetPosition(0, height - self.CORNER_HEIGHT)
		self.Corners[self.RT].SetPosition(width - self.CORNER_WIDTH, 0)
		self.Corners[self.RB].SetPosition(width - self.CORNER_WIDTH, height - self.CORNER_HEIGHT)
		self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Lines[self.B].SetPosition(self.CORNER_HEIGHT, height - self.CORNER_HEIGHT)

		verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.LINE_HEIGHT) / self.LINE_HEIGHT
		horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.LINE_WIDTH) / self.LINE_WIDTH
		self.Lines[self.L].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.R].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.T].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		self.Lines[self.B].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		self.Base.SetSize(width - self.CORNER_WIDTH*2, height - self.CORNER_HEIGHT*2)

	def SetColor(self, color):
		self.Base.SetColor(color)

	def ShowInternal(self):
		self.Base.Show()
		for wnd in self.Lines:
			wnd.Show()
		for wnd in self.Corners:
			wnd.Show()

	def HideInternal(self):
		self.Base.Hide()
		for wnd in self.Lines:
			wnd.Hide()
		for wnd in self.Corners:
			wnd.Hide()

if app.ENABLE_MYSHOP_DECO:
	class ShopDecoTitle(Window):
		DEFAULT_VALUE = 16
		CORNER_WIDTH = 48
		CORNER_HEIGHT = 32
		LINE_WIDTH = 16
		LINE_HEIGHT = 32

		LT = 0
		LB = 1
		RT = 2
		RB = 3
		L = 0
		R = 1
		T = 2
		B = 3

		def __init__(self, type, layer = "UI"):
			Window.__init__(self, layer)

			CornerFileNames, LineFileNames = self.__GetFilePath(type)

			if CornerFileNames == None or LineFileNames == None :
				return

			self.Corners = []
			for fileName in CornerFileNames:
				Corner = ExpandedImageBox()
				Corner.AddFlag("attach")
				Corner.AddFlag("not_pick")
				Corner.LoadImage(fileName)
				Corner.SetParent(self)
				Corner.SetPosition(0, 0)
				Corner.Show()
				self.Corners.append(Corner)

			self.Lines = []
			for fileName in LineFileNames:
				Line = ExpandedImageBox()
				Line.AddFlag("attach")
				Line.AddFlag("not_pick")
				Line.LoadImage(fileName)
				Line.SetParent(self)
				Line.SetPosition(0, 0)
				Line.Show()
				self.Lines.append(Line)

		def __del__(self):
			Window.__del__(self)

		def __GetFilePath(self, type):
			import uiMyShopDecoration

			CornerFileNames = [ uiMyShopDecoration.DECO_SHOP_TITLE_LIST[type][1] + "_" + dir + ".tga" for dir in [ "left_top", "left_bottom", "right_top", "right_bottom" ] ]
			LineFileNames = [ uiMyShopDecoration.DECO_SHOP_TITLE_LIST[type][1] + "_" + dir + ".tga" for dir in [ "left", "right", "top", "bottom" ] ]

			return CornerFileNames, LineFileNames

		def SetSize(self, width, height):
			width = max(self.DEFAULT_VALUE * 2, width)
			height = max(self.DEFAULT_VALUE * 2, height)
			Window.SetSize(self, width, height)

			self.Corners[self.LT].SetPosition(-self.CORNER_WIDTH + self.DEFAULT_VALUE, -self.CORNER_HEIGHT + self.DEFAULT_VALUE)
			self.Corners[self.LB].SetPosition(-self.CORNER_WIDTH + self.DEFAULT_VALUE, height - self.CORNER_HEIGHT + self.DEFAULT_VALUE)

			self.Corners[self.RT].SetPosition(width - self.DEFAULT_VALUE, -self.CORNER_HEIGHT + self.DEFAULT_VALUE)
			self.Corners[self.RB].SetPosition(width - self.DEFAULT_VALUE, height - self.CORNER_HEIGHT + self.DEFAULT_VALUE)

			self.Lines[self.L].SetPosition(0, self.DEFAULT_VALUE)
			self.Lines[self.R].SetPosition(width - self.DEFAULT_VALUE, self.DEFAULT_VALUE)
			self.Lines[self.B].SetPosition(self.DEFAULT_VALUE, height - self.LINE_HEIGHT + self.DEFAULT_VALUE)
			self.Lines[self.T].SetPosition(self.DEFAULT_VALUE, -self.LINE_HEIGHT + self.DEFAULT_VALUE)

			verticalShowingPercentage = float((height - self.DEFAULT_VALUE * 2) - self.DEFAULT_VALUE) / self.DEFAULT_VALUE
			horizontalShowingPercentage = float((width - self.DEFAULT_VALUE * 2) - self.DEFAULT_VALUE) / self.DEFAULT_VALUE

			self.Lines[self.L].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
			self.Lines[self.R].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
			self.Lines[self.T].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
			self.Lines[self.B].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)

		def ShowInternal(self):
			for wnd in self.Lines:
				wnd.Show()
			for wnd in self.Corners:
				wnd.Show()

		def HideInternal(self):
			for wnd in self.Lines:
				wnd.Hide()
			for wnd in self.Corners:
				wnd.Hide()

class ScrollbarDyn(Window):
	BASE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 0.0)
	CORNERS_AND_LINES_COLOR = grp.GenerateColor(0.3961, 0.3804, 0.3647, 1.0)
	BAR_NUMB = 9

	class MiddleBar(DragButton):
		MIDDLE_BAR_COLOR = grp.GenerateColor(0.3, 0.3, 0.3, 1.0)

		def __init__(self, horizontal_scroll):
			DragButton.__init__(self)
			self.AddFlag("movable")

			self.horizontal_scroll = horizontal_scroll
			if horizontal_scroll:
				self.SetClippingMaskWindow(wikipedia.GetMainClass().itemContainerPage.itemContainerWindow)

			self.middle = Bar()
			self.middle.SetParent(self)
			self.middle.AddFlag("attach")
			self.middle.AddFlag("not_pick")
			self.middle.SetColor(self.MIDDLE_BAR_COLOR)
			self.middle.SetSize(1, 1)
			if horizontal_scroll:
				self.middle.SetClippingMaskWindow(wikipedia.GetMainClass().itemContainerPage.itemContainerWindow)
			self.middle.Show()

		def SetStaticScale(self, size):
			(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())

			if not self.horizontal_scroll:
				DragButton.SetSize(self, base_width, size)
				self.middle.SetSize(base_width, size)
			else:
				DragButton.SetSize(self, size, base_height)
				self.middle.SetSize(size, base_height)

		def SetSize(self, selfSize, fullSize):
			(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())

			if not self.horizontal_scroll:
				DragButton.SetSize(self, base_width, truediv(int(selfSize), int(fullSize)) * selfSize)
				self.middle.SetSize(base_width, truediv(int(selfSize), int(fullSize)) * selfSize)
			else:
				DragButton.SetSize(self, truediv(int(selfSize), int(fullSize)) * selfSize, base_height)
				self.middle.SetSize(truediv(int(selfSize), int(fullSize)) * selfSize, base_height)

		def SetStaticSize(self, size):
			size = max(2, size)

			if not self.horizontal_scroll:
				DragButton.SetSize(self, size, self.middle.GetHeight())
				self.middle.SetSize(size, self.middle.GetHeight())
			else:
				DragButton.SetSize(self, self.middle.GetWidth(), size)
				self.middle.SetSize(self.middle.GetWidth(), size)

	def __init__(self, horizontal_scroll=False):
		Window.__init__(self)

		self.horizontal_scroll = horizontal_scroll

		self.scrollEvent = None
		self.scrollSpeed = 1
		self.sizeScale = 1.0

		self.is_scrollable = True

		self.bars = []
		for i in xrange(self.BAR_NUMB):
			br = Bar()
			br.SetParent(self)
			br.AddFlag("attach")
			br.AddFlag("not_pick")
			br.SetColor([self.CORNERS_AND_LINES_COLOR, self.BASE_COLOR][i == (self.BAR_NUMB-1)])
			if horizontal_scroll:
				br.SetClippingMaskWindow(wikipedia.GetMainClass().itemContainerPage.itemContainerWindow)
			if not (i % 2 == 0): br.SetSize(1, 1)
			br.Show()

			self.bars.append(br)

		self.middleBar = self.MiddleBar(self.horizontal_scroll)
		self.middleBar.SetParent(self)
		self.middleBar.SetMoveEvent(__mem_func__(self.OnScrollMove))
		self.middleBar.Show()

	def OnScrollMove(self):
		if not self.scrollEvent:
			return

		arg = float(self.middleBar.GetLocalPosition()[1] - 1) / float(self.GetHeight() - 2 - self.middleBar.GetHeight()) if not self.horizontal_scroll else\
			float(self.middleBar.GetLocalPosition()[0] - 1) / float(self.GetWidth() - 2 - self.middleBar.GetWidth())

		self.scrollEvent(arg)

	def SetScrollEvent(self, func):
		self.scrollEvent = __mem_func__(func)

	def SetScrollSpeed(self, speed):
		self.scrollSpeed = speed

	def OnMouseWheel(self, length):
		if self.IsInPosition():
			if not self.horizontal_scroll:
				val = min(max(1, self.middleBar.GetLocalPosition()[1] - (length * 0.01) * self.scrollSpeed * self.sizeScale), self.GetHeight() - self.middleBar.GetHeight() - 1)
				self.middleBar.SetPosition(1, val)
			else:
				val = min(max(1, self.middleBar.GetLocalPosition()[0] - (length * 0.01) *  self.scrollSpeed * self.sizeScale), self.GetWidth() - self.middleBar.GetWidth() - 1)
				self.middleBar.SetPosition(val, 1)

			self.OnScrollMove()
			return True

		return False

	def OnHorizontalWheelEvent(self, length):
		if not self.horizontal_scroll:
			val = min(max(1, self.middleBar.GetLocalPosition()[1] - (length * 0.01) * self.scrollSpeed * self.sizeScale), self.GetHeight() - self.middleBar.GetHeight() - 1)
			self.middleBar.SetPosition(1, val)
		else:
			val = min(max(1, self.middleBar.GetLocalPosition()[0] - (length * 0.01) *  self.scrollSpeed * self.sizeScale), self.GetWidth() - self.middleBar.GetWidth() - 1)
			self.middleBar.SetPosition(val, 1)

		self.OnScrollMove()
		return True

	def OnMouseLeftButtonDown(self):
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()

		if not self.horizontal_scroll:
			if xMouseLocalPosition == 0 or xMouseLocalPosition == self.GetWidth():
				return

			y_pos = (yMouseLocalPosition - self.middleBar.GetHeight() / 2)
			self.middleBar.SetPosition(1, y_pos)
		else:
			if yMouseLocalPosition == 0 or yMouseLocalPosition == self.GetHeight():
				return

			x_pos = (xMouseLocalPosition - self.middleBar.GetWidth() / 2)
			self.middleBar.SetPosition(x_pos, 1)

		self.OnScrollMove()

	def SetSize(self, w, h):
		(width, height) = (max(3, w), max(3, h))

		Window.SetSize(self, width, height)

		self.bars[0].SetSize(1, (height - 2))
		self.bars[0].SetPosition(0, 1)
		self.bars[2].SetSize((width - 2), 1)
		self.bars[2].SetPosition(1, 0)
		self.bars[4].SetSize(1, (height - 2))
		self.bars[4].SetPosition((width - 1), 1)
		self.bars[6].SetSize((width - 2), 1)
		self.bars[6].SetPosition(1, (height - 1))
		self.bars[8].SetSize((width - 2), (height - 2))
		self.bars[8].SetPosition(1, 1)

		self.bars[1].SetPosition(0, 0)
		self.bars[3].SetPosition((width - 1), 0)
		self.bars[5].SetPosition((width - 1), (height - 1))
		self.bars[7].SetPosition(0, (height - 1))

		if not self.horizontal_scroll:
			self.middleBar.SetStaticSize(width - 2)
			self.middleBar.SetSize(12, self.GetHeight())
		else:
			self.middleBar.SetStaticSize(height - 2)
			self.middleBar.SetSize(12, self.GetWidth())

		self.middleBar.SetRestrictMovementArea(1, 1, width - 2, height - 2)

	def SetScale(self, selfSize, fullSize):
		self.sizeScale = float(selfSize / fullSize)
		self.middleBar.SetSize(selfSize, fullSize)

	def SetStaticScale(self, r_size):
		self.middleBar.SetStaticScale(r_size)

	def SetPosScale(self, fScale):
		pos = (math.ceil((self.GetHeight() - 2 - self.middleBar.GetHeight()) * fScale) + 1) if not self.horizontal_scroll else\
			(math.ceil((self.GetWidth() - 2 - self.middleBar.GetWidth()) * fScale) + 1)

		self.SetPos(pos)

	def SetPosScale(self, fScale):
		pos = (math.ceil((self.GetHeight() - 2 - self.middleBar.GetHeight()) * fScale) + 1) if not self.horizontal_scroll else\
				(math.ceil((self.GetWidth() - 2 - self.middleBar.GetWidth()) * fScale) + 1)

		self.SetPos(pos)

	def SetAnimatedScrollingSpeedNotAnimated(self):
		pass

	def RestoreAnimatedScrollingSpeed(self):
		pass

	def IsScrollable(self):
		return self.is_scrollable

	def SetScrollable(self, is_scrollable):
		self.is_scrollable = is_scrollable

	def SetPos(self, pos):
		wPos = (1, pos) if not self.horizontal_scroll else (pos, 1)
		self.middleBar.SetPosition(*wPos)


class ScrollBarNew(Window):
	SCROLLBAR_WIDTH = 12
	SCROLL_BTN_XDIST = 0
	SCROLL_BTN_YDIST = 0
	class MiddleBar(DragButton):
		SCROLL_BTN_POSX = 3
		SCROLL_BTN_POSY = 2
		def __init__(self):
			DragButton.__init__(self)
			self.AddFlag("movable")
			self.SetWindowName("scrollbar_middlebar")

		def MakeImage(self):
			top = ExpandedImageBox()
			top.SetParent(self)
			top.SetPosition(self.SCROLL_BTN_POSX, self.SCROLL_BTN_POSY)
			top.LoadImage("d:/ymir work/ui/game/scrollbar/scrollbar_top.tga")
			top.AddFlag("not_pick")
			top.Show()

			topScale = ExpandedImageBox()
			topScale.SetParent(self)
			topScale.SetPosition(self.SCROLL_BTN_POSX, top.GetHeight()+self.SCROLL_BTN_POSY)
			topScale.LoadImage("d:/ymir work/ui/game/scrollbar/scrollbar_scale.tga")
			topScale.AddFlag("not_pick")
			topScale.Show()

			bottom = ExpandedImageBox()
			bottom.SetParent(self)
			bottom.LoadImage("d:/ymir work/ui/game/scrollbar/scrollbar_bottom.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()

			bottomScale = ExpandedImageBox()
			bottomScale.SetParent(self)
			bottomScale.LoadImage("d:/ymir work/ui/game/scrollbar/scrollbar_scale.tga")
			bottomScale.AddFlag("not_pick")
			bottomScale.Show()

			middle = ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage("d:/ymir work/ui/game/scrollbar/scrollbar_mid.tga")
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
			DragButton.SetSize(self, 10, height)
			scale = (height - minHeight) / 2 

			extraScale = 0

			if (height - minHeight) % 2 == 1:
				extraScale = 1
			self.topScale.SetRenderingRect(0, 0, 0, scale - 1)
			self.middle.SetPosition(self.SCROLL_BTN_POSX, self.top.GetHeight() + scale)
			self.bottomScale.SetPosition(self.SCROLL_BTN_POSX, self.middle.GetBottom())
			self.bottomScale.SetRenderingRect(0, 0, 0, scale - 1 + extraScale)
			self.bottom.SetPosition(self.SCROLL_BTN_POSX, height - self.bottom.GetHeight())

	def __init__(self):
		Window.__init__(self)
		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = None
		self.eventArgs = None
		self.lockFlag = False
		self.CreateScrollBar()
		self.SetScrollBarSize(0)
		self.scrollStep = 0.4
		self.allow_on_run_mouse_wheel = True

	def __del__(self):
		self.allow_on_run_mouse_wheel = None
		Window.__del__(self)

	def CreateScrollBar(self):
		topImage = ExpandedImageBox()
		topImage.SetParent(self)
		topImage.AddFlag("not_pick")
		topImage.LoadImage("d:/ymir work/ui/game/scrollbar/scroll_top.tga")
		topImage.Show()

		bottomImage = ExpandedImageBox()
		bottomImage.SetParent(self)
		bottomImage.AddFlag("not_pick")
		bottomImage.LoadImage("d:/ymir work/ui/game/scrollbar/scroll_bottom.tga")
		bottomImage.Show()

		middleImage = ExpandedImageBox()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, topImage.GetHeight())
		middleImage.LoadImage("d:/ymir work/ui/game/scrollbar/scroll_mid.tga")
		middleImage.Show()

		self.topImage = topImage
		self.bottomImage = bottomImage
		self.middleImage = middleImage

		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
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
		self.middleBar.SetSize(int(pageScale * float(self.GetHeight() - (self.SCROLL_BTN_YDIST*2))))
		realHeight = self.GetHeight() - (self.SCROLL_BTN_YDIST*2) - self.middleBar.GetHeight()
		self.pageSize = realHeight

	def SetScrollBarSize(self, height):
		self.SetSize(self.SCROLLBAR_WIDTH, height)

		self.pageSize = height - self.SCROLL_BTN_YDIST*2 - self.middleBar.GetHeight()

		middleImageScale = float((height - self.SCROLL_BTN_YDIST*2) - self.middleImage.GetHeight()) / float(self.middleImage.GetHeight())
		self.middleImage.SetRenderingRect(0, 0, 0, middleImageScale)

		self.bottomImage.SetPosition(0, height - self.bottomImage.GetHeight())

		self.middleBar.SetRestrictMovementArea(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST, \
			self.middleBar.GetWidth(), height - self.SCROLL_BTN_YDIST * 2)

		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST)

	def SetScrollStep(self, step):
		self.scrollStep = step

	def OnUp(self):
		self.SetPos(self.curPos-self.scrollStep)

	def OnDown(self):
		self.SetPos(self.curPos+self.scrollStep)

	def GetScrollStep(self):
		return self.scrollStep

	def GetPos(self):
		return self.curPos

	def OnUp(self):
		self.SetPos(self.curPos-self.scrollStep)

	def OnDown(self):
		self.SetPos(self.curPos+self.scrollStep)

	def SetPos(self, pos, moveEvent = True):
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

	def RunMouseWheel(self, nLen):
		if nLen > 0:
			self.OnUp()
		else:
			self.OnDown()

	def OnRunMouseWheel(self, nLen):
		if self.allow_on_run_mouse_wheel == False:
			return False

		if nLen > 0:
			self.OnUp()
			return True
		elif nLen < 0:
			self.OnDown()
			return True

		return False

class SubTitleBarNew(Button):
	def __init__(self):
		Button.__init__(self)
		self.image_map = ["d:/ymir work/ui/quest_re/quest_down.tga", "d:/ymir work/ui/quest_re/quest_up.tga"]
	
	def __del__(self):
		Button.__del__(self)

	def MakeSubTitleBarNew(self, width, color, fileFolder, iconX, iconY):
		width = max(64, width)
		self.SetWidth(width)
		self.SetUpVisual(fileFolder)
		self.SetOverVisual(fileFolder)
		self.SetDownVisual(fileFolder)
		self.Show()

		scrollImage = ImageBox()
		scrollImage.SetParent(self)
		scrollImage.LoadImage(self.image_map[0])
		scrollImage.SetPosition(iconX, iconY)
		scrollImage.AddFlag("not_pick")
		scrollImage.Show()
		self.scrollImage = scrollImage

	def OpenCategory(self, qcount = 0):
		if qcount > 0:
			self.scrollImage.LoadImage(self.image_map[1])
		else:
			self.scrollImage.LoadImage(self.image_map[0])

	def CloseCategory(self, qcount = 0):
		self.scrollImage.LoadImage(self.image_map[0])
	
	def SetMiniImageNorm(self, image):
		self.image_map[0] = image
		self.scrollImage.LoadImage(self.image_map[0])
	
	def SetMiniImageOpen(self, image):
		self.image_map[1] = image

	def SetQuestLabel(self, filename, qcount, cX, cY):
		tabColor = ImageBox()
		tabColor.SetParent(self)
		if filename != "":
			tabColor.LoadImage(filename)
		tabColor.AddFlag("not_pick")
		tabColor.SetPosition(cX,cY)
		if qcount > 0:
			tabColor.Show()
		else:
			tabColor.Hide()
		self.tabColor = tabColor

	def SetWidth(self, width):
		self.SetPosition(32, 0)
		self.SetSize(width, 23)

class ScrollBar(Window):
	SCROLLBAR_WIDTH = 17
	SCROLLBAR_MIDDLE_HEIGHT = 9
	SCROLLBAR_BUTTON_WIDTH = 17
	SCROLLBAR_BUTTON_HEIGHT = 17
	MIDDLE_BAR_POS = 5
	MIDDLE_BAR_UPPER_PLACE = 3
	MIDDLE_BAR_DOWNER_PLACE = 4
	TEMP_SPACE = MIDDLE_BAR_UPPER_PLACE + MIDDLE_BAR_DOWNER_PLACE

	class MiddleBar(DragButton):
		def __init__(self):
			DragButton.__init__(self)
			self.AddFlag("movable")
			#self.AddFlag("restrict_x")

		def MakeImage(self):
			top = ImageBox()
			top.SetParent(self)
			top.LoadImage("d:/ymir work/ui/pattern/ScrollBar_Top.tga")
			top.SetPosition(0, 0)
			top.AddFlag("not_pick")
			top.Show()
			bottom = ImageBox()
			bottom.SetParent(self)
			bottom.LoadImage("d:/ymir work/ui/pattern/ScrollBar_Bottom.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()

			middle = ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage("d:/ymir work/ui/pattern/ScrollBar_Middle.tga")
			middle.SetPosition(0, 4)
			middle.AddFlag("not_pick")
			middle.Show()

			self.top = top
			self.bottom = bottom
			self.middle = middle

		def SetSize(self, height):
			height = max(12, height)
			DragButton.SetSize(self, 10, height)
			self.bottom.SetPosition(0, height-4)

			height -= 4*3
			self.middle.SetRenderingRect(0, 0, 0, float(height)/4.0)

	def __init__(self):
		Window.__init__(self)
		
		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = lambda *arg: None
		self.lockFlag = False
		self.scrollStep = 0.20

		self.UpScrollButtonEvent = lambda *arg: None
		self.DownScrollButtonEvent = lambda *arg: None

		self.eventFuncCall = True

		self.CreateScrollBar()

	def __del__(self):
		Window.__del__(self)

	def CreateScrollBar(self):
		barSlot = Bar3D()
		barSlot.SetParent(self)
		barSlot.AddFlag("not_pick")
		barSlot.Show()

		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(12)

		upButton = Button()
		upButton.SetParent(self)
		upButton.SetEvent(__mem_func__(self.OnUp))
		upButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_up_button_01.sub")
		upButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_up_button_02.sub")
		upButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_up_button_03.sub")
		upButton.Show()

		downButton = Button()
		downButton.SetParent(self)
		downButton.SetEvent(__mem_func__(self.OnDown))
		downButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_down_button_01.sub")
		downButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_down_button_02.sub")
		downButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_down_button_03.sub")
		downButton.Show()

		self.upButton = upButton
		self.downButton = downButton
		self.middleBar = middleBar
		self.barSlot = barSlot

		self.SCROLLBAR_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_MIDDLE_HEIGHT = self.middleBar.GetHeight()
		self.SCROLLBAR_BUTTON_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_BUTTON_HEIGHT = self.upButton.GetHeight()

	def Destroy(self):
		self.middleBar = None
		self.upButton = None
		self.downButton = None
		self.eventScroll = lambda *arg: None

		self.UpScrollButtonEvent = lambda *arg: None
		self.DownScrollButtonEvent = lambda *arg: None

		self.eventFuncCall = True

	def SetUpScrollButtonEvent(self, event):
		self.UpScrollButtonEvent = event

	def SetDownScrollButtonEvent(self, event):
		self.DownScrollButtonEvent = event

	def SetEvnetFuncCall(self, callable):
		self.eventFuncCall = callable

	def SetScrollEvent(self, event):
		self.eventScroll = event

	def SetMiddleBarSize(self, pageScale):
		realHeight = self.GetHeight() - self.SCROLLBAR_BUTTON_HEIGHT*2
		self.SCROLLBAR_MIDDLE_HEIGHT = int(pageScale * float(realHeight))
		self.middleBar.SetSize(self.SCROLLBAR_MIDDLE_HEIGHT)
		self.pageSize = (self.GetHeight() - self.SCROLLBAR_BUTTON_HEIGHT*2) - self.SCROLLBAR_MIDDLE_HEIGHT - (self.TEMP_SPACE)

	def SetScrollBarSize(self, height):
		self.pageSize = (height - self.SCROLLBAR_BUTTON_HEIGHT*2) - self.SCROLLBAR_MIDDLE_HEIGHT - (self.TEMP_SPACE)
		self.SetSize(self.SCROLLBAR_WIDTH, height)
		self.upButton.SetPosition(0, 0)
		self.downButton.SetPosition(0, height - self.SCROLLBAR_BUTTON_HEIGHT)
		self.middleBar.SetRestrictMovementArea(self.MIDDLE_BAR_POS, self.SCROLLBAR_BUTTON_HEIGHT + self.MIDDLE_BAR_UPPER_PLACE, self.MIDDLE_BAR_POS+2, height - self.SCROLLBAR_BUTTON_HEIGHT*2 - self.TEMP_SPACE)
		self.middleBar.SetPosition(self.MIDDLE_BAR_POS, 0)

		self.UpdateBarSlot()

	def UpdateBarSlot(self):
		self.barSlot.SetPosition(0, self.SCROLLBAR_BUTTON_HEIGHT)
		self.barSlot.SetSize(self.GetWidth() - 2, self.GetHeight() - self.SCROLLBAR_BUTTON_HEIGHT*2 - 2)

	def GetPos(self):
		return self.curPos

	def SetPos(self, pos, event_callable = True):
		pos = max(0.0, pos)
		pos = min(1.0, pos)

		newPos = float(self.pageSize) * pos
		if app.ENABLE_MAILBOX:
			self.middleBar.SetPosition(self.MIDDLE_BAR_POS, round(float(newPos) + self.SCROLLBAR_BUTTON_HEIGHT + self.MIDDLE_BAR_UPPER_PLACE))
		else:
			self.middleBar.SetPosition(self.MIDDLE_BAR_POS, int(newPos) + self.SCROLLBAR_BUTTON_HEIGHT + self.MIDDLE_BAR_UPPER_PLACE)

		self.OnMove(event_callable)

	def SetScrollStep(self, step):
		self.scrollStep = step

	def GetScrollStep(self):
		return self.scrollStep

	def OnUp(self):
		self.SetPos(self.curPos-self.scrollStep, self.eventFuncCall)
		self.UpScrollButtonEvent()

	def OnDown(self):
		self.SetPos(self.curPos+self.scrollStep, self.eventFuncCall)
		self.DownScrollButtonEvent()

	def OnMove(self, event_callable = True):
		if self.lockFlag:
			return

		if 0 == self.pageSize:
			return

		(xLocal, yLocal) = self.middleBar.GetLocalPosition()
		self.curPos = float(yLocal - self.SCROLLBAR_BUTTON_HEIGHT - self.MIDDLE_BAR_UPPER_PLACE) / float(self.pageSize)

		if event_callable:
			self.eventScroll()

	def OnMouseLeftButtonDown(self):
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		pickedPos = yMouseLocalPosition - self.SCROLLBAR_BUTTON_HEIGHT - self.SCROLLBAR_MIDDLE_HEIGHT/2
		newPos = float(pickedPos) / float(self.pageSize)
		self.SetPos(newPos)

	def LockScroll(self):
		self.lockFlag = True

	def UnlockScroll(self):
		self.lockFlag = False

	if app.ENABLE_MAILBOX:
		def SetUpButtonSizeRefresh(self):
			self.SCROLLBAR_WIDTH = self.upButton.GetWidth()
			self.SCROLLBAR_BUTTON_WIDTH = self.upButton.GetWidth()
			self.SCROLLBAR_BUTTON_HEIGHT = self.upButton.GetHeight()

		def SetUpButtonUpVisual(self, img_path):
			if self.upButton:
				self.upButton.SetUpVisual(img_path)

		def SetUpButtonOverVisual(self, img_path):
			if self.upButton:
				self.upButton.SetOverVisual(img_path)

		def SetUpButtonDownVisual(self, img_path):
			if self.upButton:
				self.upButton.SetDownVisual(img_path)

		def SetDownButtonUpVisual(self, img_path):
			if self.downButton:
				self.downButton.SetUpVisual(img_path)

		def SetDownButtonOverVisual(self, img_path):
			if self.downButton:
				self.downButton.SetOverVisual(img_path)

		def SetDownButtonDownVisual(self, img_path):
			if self.downButton:
				self.downButton.SetDownVisual(img_path)

		def RunMouseWheel(self, nLen):
			if nLen > 0:
				self.OnUp()
			else:
				self.OnDown()

		def OnRunMouseWheel(self, nLen):
			if nLen > 0:
				self.OnUp()
				return True
			elif nLen < 0:
				self.OnDown()
				return True
			
			return False

class NewScrollBar(Window):
	SCROLLBAR_WIDTH = 17
	SCROLLBAR_MIDDLE_HEIGHT = 9
	SCROLLBAR_BUTTON_WIDTH = 17
	SCROLLBAR_BUTTON_HEIGHT = 17
	MIDDLE_BAR_POS = 0
	MIDDLE_BAR_UPPER_PLACE = 3
	MIDDLE_BAR_DOWNER_PLACE = 4
	TEMP_SPACE = MIDDLE_BAR_UPPER_PLACE + MIDDLE_BAR_DOWNER_PLACE

	class MiddleBar(DragButton):
		def __init__(self):
			DragButton.__init__(self)
			self.AddFlag("movable")

		def MakeImage(self):

			middle = ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage("d:/ymir work/ui/pattern/new_scroll/scrollbar_middle.tga")
			middle.SetPosition(0, 0)
			middle.AddFlag("not_pick")
			middle.Show()

			self.middle = middle

		def SetSize(self, height):
			height = max(12, height)
			DragButton.SetSize(self, 10, height)

			height -= 4*3
			self.middle.SetRenderingRect(0, 0, 0, float(height)/4.0)

	def __init__(self):
		Window.__init__(self)
		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = lambda *arg: None
		self.lockFlag = False
		self.scrollStep = 0.20

		self.eventFuncCall = True

		self.CreateScrollBar()

	def __del__(self):
		Window.__del__(self)

	def CreateScrollBar(self):
		barSlot = ExpandedImageBox()
		barSlot.SetParent(self)
		barSlot.LoadImage("d:/ymir work/ui/pattern/new_scroll/base_scroll.tga")
		barSlot.AddFlag("not_pick")
		barSlot.Show()

		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(12)
		
		self.middleBar = middleBar
		self.barSlot = barSlot

		self.SCROLLBAR_WIDTH = self.middleBar.GetWidth()
		self.SCROLLBAR_MIDDLE_HEIGHT = self.middleBar.GetHeight()
		self.SCROLLBAR_BUTTON_WIDTH = self.middleBar.GetWidth()
		self.SCROLLBAR_BUTTON_HEIGHT = self.middleBar.GetHeight()

	def Destroy(self):
		self.middleBar = None
		self.eventScroll = lambda *arg: None

		self.eventFuncCall	= True

	def SetEvnetFuncCall(self, callable):
		self.eventFuncCall = callable

	def SetScrollEvent(self, event):
		self.eventScroll = event

	def SetMiddleBarSize(self, pageScale):
		realHeight = self.GetHeight() - self.SCROLLBAR_BUTTON_HEIGHT*2
		self.SCROLLBAR_MIDDLE_HEIGHT = int(pageScale * float(realHeight))
		self.middleBar.SetSize(self.SCROLLBAR_MIDDLE_HEIGHT)
		self.pageSize = (self.GetHeight() - self.SCROLLBAR_BUTTON_HEIGHT*2) - self.SCROLLBAR_MIDDLE_HEIGHT - (self.TEMP_SPACE)

	def SetScrollBarSize(self, height):
		self.pageSize = (height - self.SCROLLBAR_BUTTON_HEIGHT*2) - self.SCROLLBAR_MIDDLE_HEIGHT - (self.TEMP_SPACE)
		self.SetSize(self.SCROLLBAR_WIDTH, height)
		self.middleBar.SetRestrictMovementArea(self.MIDDLE_BAR_POS, self.SCROLLBAR_BUTTON_HEIGHT + self.MIDDLE_BAR_UPPER_PLACE, self.MIDDLE_BAR_POS+2, height - self.SCROLLBAR_BUTTON_HEIGHT*2 - self.TEMP_SPACE)
		self.middleBar.SetPosition(self.MIDDLE_BAR_POS, 0)

		self.UpdateBarSlot()

	def UpdateBarSlot(self):
		self.barSlot.SetPosition(0, self.SCROLLBAR_BUTTON_HEIGHT)
		height =  - self.SCROLLBAR_BUTTON_HEIGHT*2 - 2
		new_height = float(self.GetHeight()) / float(self.barSlot.GetHeight())
		self.barSlot.SetRenderingRect(0.0, 0.0, 0.0, new_height - 2.8)

	def GetPos(self):
		return self.curPos

	def SetPos(self, pos, event_callable = True):
		pos = max(0.0, pos)
		pos = min(1.0, pos)

		newPos = float(self.pageSize) * pos
		self.middleBar.SetPosition(self.MIDDLE_BAR_POS, int(newPos) + self.SCROLLBAR_BUTTON_HEIGHT + self.MIDDLE_BAR_UPPER_PLACE)

		self.OnMove(event_callable)

	def SetScrollStep(self, step):
		self.scrollStep = step

	def GetScrollStep(self):
		return self.scrollStep

	def OnUp(self):
		self.SetPos(self.curPos-self.scrollStep, self.eventFuncCall)

	def OnDown(self):
		self.SetPos(self.curPos+self.scrollStep, self.eventFuncCall)

	def OnMove(self, event_callable = True):
		if self.lockFlag:
			return

		if 0 == self.pageSize:
			return

		(xLocal, yLocal) = self.middleBar.GetLocalPosition()
		self.curPos = float(yLocal - self.SCROLLBAR_BUTTON_HEIGHT - self.MIDDLE_BAR_UPPER_PLACE) / float(self.pageSize)

		if event_callable:
			self.eventScroll()

	def OnMouseLeftButtonDown(self):
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		pickedPos = yMouseLocalPosition - self.SCROLLBAR_BUTTON_HEIGHT - self.SCROLLBAR_MIDDLE_HEIGHT/2
		newPos = float(pickedPos) / float(self.pageSize)
		self.SetPos(newPos)

	def LockScroll(self):
		self.lockFlag = True

	def UnlockScroll(self):
		self.lockFlag = False

	if app.ENABLE_MAILBOX:
		def SetUpButtonSizeRefresh(self):
			self.SCROLLBAR_WIDTH = self.upButton.GetWidth()
			self.SCROLLBAR_BUTTON_WIDTH = self.upButton.GetWidth()
			self.SCROLLBAR_BUTTON_HEIGHT = self.upButton.GetHeight()

		def SetUpButtonUpVisual(self, img_path):
			if self.upButton:
				self.upButton.SetUpVisual(img_path)

		def SetUpButtonOverVisual(self, img_path):
			if self.upButton:
				self.upButton.SetOverVisual(img_path)

		def SetUpButtonDownVisual(self, img_path):
			if self.upButton:
				self.upButton.SetDownVisual(img_path)

		def SetDownButtonUpVisual(self, img_path):
			if self.downButton:
				self.downButton.SetUpVisual(img_path)

		def SetDownButtonOverVisual(self, img_path):
			if self.downButton:
				self.downButton.SetOverVisual(img_path)

		def SetDownButtonDownVisual(self, img_path):
			if self.downButton:
				self.downButton.SetDownVisual(img_path)

	def RunMouseWheel(self, nLen):
		if nLen > 0:
			self.OnUp()
		else:
			self.OnDown()

	def OnRunMouseWheel(self, nLen):
		if nLen > 0:
			self.OnUp()
			return True
		elif nLen < 0:
			self.OnDown()
			return True
		
		return False

class ThinScrollBar(ScrollBar):
	def CreateScrollBar(self):
		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.SetUpVisual("d:/ymir work/ui/public/scrollbar_thin_middle_button_01.sub")
		middleBar.SetOverVisual("d:/ymir work/ui/public/scrollbar_thin_middle_button_02.sub")
		middleBar.SetDownVisual("d:/ymir work/ui/public/scrollbar_thin_middle_button_03.sub")

		upButton = Button()
		upButton.SetParent(self)
		upButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_thin_up_button_01.sub")
		upButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_thin_up_button_02.sub")
		upButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_thin_up_button_03.sub")
		upButton.SetEvent(__mem_func__(self.OnUp))
		upButton.Show()

		downButton = Button()
		downButton.SetParent(self)
		downButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_thin_down_button_01.sub")
		downButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_thin_down_button_02.sub")
		downButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_thin_down_button_03.sub")
		downButton.SetEvent(__mem_func__(self.OnDown))
		downButton.Show()

		self.middleBar = middleBar
		self.upButton = upButton
		self.downButton = downButton

		self.SCROLLBAR_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_MIDDLE_HEIGHT = self.middleBar.GetHeight()
		self.SCROLLBAR_BUTTON_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_BUTTON_HEIGHT = self.upButton.GetHeight()
		self.MIDDLE_BAR_POS = 0
		self.MIDDLE_BAR_UPPER_PLACE = 0
		self.MIDDLE_BAR_DOWNER_PLACE = 0
		self.TEMP_SPACE = 0

	def UpdateBarSlot(self):
		pass

class SmallThinScrollBar(ScrollBar):

	def CreateScrollBar(self):
		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.SetUpVisual("d:/ymir work/ui/public/scrollbar_small_thin_middle_button_01.sub")
		middleBar.SetOverVisual("d:/ymir work/ui/public/scrollbar_small_thin_middle_button_01.sub")
		middleBar.SetDownVisual("d:/ymir work/ui/public/scrollbar_small_thin_middle_button_01.sub")

		upButton = Button()
		upButton.SetParent(self)
		upButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_small_thin_up_button_01.sub")
		upButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_small_thin_up_button_02.sub")
		upButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_small_thin_up_button_03.sub")
		upButton.SetEvent(__mem_func__(self.OnUp))
		upButton.Show()

		downButton = Button()
		downButton.SetParent(self)
		downButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_small_thin_down_button_01.sub")
		downButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_small_thin_down_button_02.sub")
		downButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_small_thin_down_button_03.sub")
		downButton.SetEvent(__mem_func__(self.OnDown))
		downButton.Show()

		self.middleBar = middleBar
		self.upButton = upButton
		self.downButton = downButton

		self.SCROLLBAR_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_MIDDLE_HEIGHT = self.middleBar.GetHeight()
		self.SCROLLBAR_BUTTON_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_BUTTON_HEIGHT = self.upButton.GetHeight()
		self.MIDDLE_BAR_POS = 0
		self.MIDDLE_BAR_UPPER_PLACE = 0
		self.MIDDLE_BAR_DOWNER_PLACE = 0
		self.TEMP_SPACE = 0

	def UpdateBarSlot(self):
		pass

class SliderBar(Window):

	def __init__(self):
		Window.__init__(self)
		self.curPos = 1.0
		self.pageSize = 1.0
		self.eventChange = None

		self.__CreateBackGroundImage()
		self.__CreateCursor()
		if app.ENABLE_INGAME_WIKI:
			self.__CreateResetButton()
			self.OnTextButtonReset()

	def __del__(self):
		Window.__del__(self)

	def __CreateBackGroundImage(self):
		if app.ENABLE_GAMEOPTION_RENEWAL:
			img = ExpandedImageBox()
		else:
			img = ImageBox()
		
		img.SetParent(self)
		if app.ENABLE_INGAME_WIKI:
			img.LoadImage("d:/ymir work/ui/game/slider/slidebar01.tga")
		else:
			img.LoadImage("d:/ymir work/ui/game/windows/sliderbar.sub")
		img.Show()
		self.backGroundImage = img

		##
		self.SetSize(self.backGroundImage.GetWidth(), self.backGroundImage.GetHeight())

	def __CreateCursor(self):
		cursor = DragButton()
		cursor.AddFlag("movable")
		cursor.AddFlag("restrict_y")
		cursor.SetParent(self)
		cursor.SetMoveEvent(__mem_func__(self.__OnMove))
		if app.ENABLE_INGAME_WIKI:
			cursor.SetUpVisual("d:/ymir work/ui/game/slider/slidebar_button01.tga")
			cursor.SetOverVisual("d:/ymir work/ui/game/slider/slidebar_button02.tga")
			cursor.SetDownVisual("d:/ymir work/ui/game/slider/slidebar_button01.tga")
		else:
			cursor.SetUpVisual("d:/ymir work/ui/game/windows/sliderbar_cursor.sub")
			cursor.SetOverVisual("d:/ymir work/ui/game/windows/sliderbar_cursor.sub")
			cursor.SetDownVisual("d:/ymir work/ui/game/windows/sliderbar_cursor.sub")
		cursor.Show()
		self.cursor = cursor

		##
		self.cursor.SetRestrictMovementArea(0, 0, self.backGroundImage.GetWidth(), 0)
		self.pageSize = self.backGroundImage.GetWidth() - self.cursor.GetWidth()

	if app.ENABLE_INGAME_WIKI:
		def __CreateResetButton(self):
			resetButton = Button()
			resetButton.SetParent(self)
			resetButton.SetPosition(self.backGroundImage.GetWidth()-16, 0)
			resetButton.SetUpVisual("d:/ymir work/ui/game/slider/reset01.tga")
			resetButton.SetOverVisual("d:/ymir work/ui/game/slider/reset02.tga")
			resetButton.SetDownVisual("d:/ymir work/ui/game/slider/reset03.tga")
			resetButton.SetEvent(__mem_func__(self.OnReset))
			resetButton.Show()
			self.resetButton = resetButton

		def OnReset(self, pos=0.0):
			self.SetSliderPos(pos)

			if self.eventChange:
				self.eventChange()

		def OnTextButtonReset(self, x=0, y = -19):
			self.resetButton.SetToolTipText(localeinfo.OFFLINESHOP_SCRIPTFILE_RESET_FILTER_TEXT, x, y)


	def __OnMove(self):
		(xLocal, yLocal) = self.cursor.GetLocalPosition()
		self.curPos = float(xLocal) / float(self.pageSize)

		if self.eventChange:
			self.eventChange()

	def SetSliderPos(self, pos):
		self.curPos = pos
		self.cursor.SetPosition(int(self.pageSize * pos), 0)

	def GetSliderPos(self):
		return self.curPos

	def SetEvent(self, event):
		self.eventChange = event

	def Enable(self):
		self.cursor.Show()
		if app.ENABLE_INGAME_WIKI:
			self.resetButton.Show()

	def Disable(self):
		self.cursor.Hide()
		if app.ENABLE_INGAME_WIKI:
			self.resetButton.Hide()


class SliderBar_AdvancedGameOptions(Window):

	def __init__(self):
		Window.__init__(self)

		self.curPos = 1.0
		self.pageSize = 1.0
		self.eventChange = None

		self.__CreateBackGroundImage()
		self.__CreateCursor()
		self.__CreatePercentage()

	def __del__(self):
		Window.__del__(self)

	def __CreateBackGroundImage(self):
		if app.ENABLE_GAMEOPTION_RENEWAL:
			img = ExpandedImageBox()
		else:
			img = ImageBox()
		img.SetParent(self)
		img.LoadImage("d:/ymir work/ui/game/advanced_game_options/sliderbar.png")
		img.Show()
		self.backGroundImage = img

		##
		self.SetSize(self.backGroundImage.GetWidth(), self.backGroundImage.GetHeight())

	def __CreateCursor(self):
		cursor = DragButton()
		cursor.AddFlag("movable")
		cursor.AddFlag("restrict_y")
		cursor.SetParent(self)
		cursor.SetMoveEvent(__mem_func__(self.__OnMove))
		cursor.SetUpVisual("d:/ymir work/ui/game/advanced_game_options/sliderbar_cursor.png")
		cursor.SetOverVisual("d:/ymir work/ui/game/advanced_game_options/sliderbar_cursor.png")
		cursor.SetDownVisual("d:/ymir work/ui/game/advanced_game_options/sliderbar_cursor.png")
		cursor.Show()
		self.cursor = cursor

		##
		self.cursor.SetRestrictMovementArea(0, 0, self.backGroundImage.GetWidth(), 0)
		self.pageSize = self.backGroundImage.GetWidth() - self.cursor.GetWidth()

	PERCENTAGE_GAP = 10

	# LoadElementSliderBar never runs LoadChildren, so this bar never gets the
	# "rtl" flag the engine mirrors children with -- in Arabic every uiscript
	# label flips to the left of the track while this one would stay welded to
	# its right end, so the side is chosen here instead
	def __PercentageX(self):
		if localeinfo.IsARABIC():
			return -(self.percentageWidth + self.PERCENTAGE_GAP)
		return self.backGroundImage.GetWidth() + self.PERCENTAGE_GAP

	def __CreatePercentage(self):
		text = TextLine()
		text.SetParent(self)
		self.percentageWidth = 34
		text.SetPosition(self.__PercentageX(), 0)
		(xLocal, yLocal) = self.cursor.GetLocalPosition()
		self.curPos = float(xLocal) / float(self.pageSize)
		text.SetText(str(int(self.curPos * 100)) + "%")		
		text.SetText("0%")
		text.Show()
		self.percentage = text	

	def __OnMove(self):
		(xLocal, yLocal) = self.cursor.GetLocalPosition()
		self.curPos = float(xLocal) / float(self.pageSize)
		self.percentage.SetText(str(int(self.curPos * 100)) + "%")

		if self.eventChange:
			self.eventChange()

	def SetSliderPos(self, pos):
		self.curPos = pos
		self.cursor.SetPosition(int(self.pageSize * pos), 0)
		self.percentage.SetText(str(int(self.curPos * 100)) + "%")

	def GetSliderPos(self):
		return self.curPos

	def SetEvent(self, event):
		self.eventChange = event

	def Enable(self):
		self.cursor.Show()

	def Disable(self):
		self.cursor.Hide()

	def SetBackgroundVisual(self, filename):
		if self.backGroundImage:
			self.backGroundImage.LoadImage(filename)

			self.SetSize(self.backGroundImage.GetWidth(), self.backGroundImage.GetHeight())
			self.pageSize = self.backGroundImage.GetWidth() - self.cursor.GetWidth()
			self.percentage.SetPosition(self.__PercentageX(), 0)

		if self.cursor:
			self.cursor.SetRestrictMovementArea(0, 0, self.backGroundImage.GetWidth(), 0)

	def SetButtonVisual(self, path, up, over, down):
		if self.cursor:
			self.cursor.SetUpVisual(path + up)
			self.cursor.SetOverVisual(path + over)
			self.cursor.SetDownVisual(path + down)			


class NewSliderBar(Window):

	def __init__(self):
		Window.__init__(self)
		self.curPos = 1.0
		self.pageSize = 1.0
		self.eventChange = None

		self.__CreateBackGroundImage()
		self.__CreateCursor()

	def __del__(self):
		Window.__del__(self)

	def __CreateBackGroundImage(self):
		img = ImageBox()
		img.SetParent(self)
		img.LoadImage("d:/ymir work/ui/new_options/new_slidbar_bg.tga")
		img.Show()
		self.backGroundImage = img

		##
		self.SetSize(self.backGroundImage.GetWidth(), self.backGroundImage.GetHeight())

	def __CreateCursor(self):
		cursor = DragButton()
		cursor.AddFlag("movable")
		cursor.AddFlag("restrict_y")
		cursor.SetParent(self)
		cursor.SetMoveEvent(__mem_func__(self.__OnMove))
		cursor.SetUpVisual("d:/ymir work/ui/new_options/new_mid_bar_slidbar_bg.tga")
		cursor.SetOverVisual("d:/ymir work/ui/new_options/new_mid_bar_slidbar_bg.tga")
		cursor.SetDownVisual("d:/ymir work/ui/new_options/new_mid_bar_slidbar_bg.tga")
		cursor.Show()
		self.cursor = cursor

		##
		self.cursor.SetRestrictMovementArea(0, 0, self.backGroundImage.GetWidth(), 0)
		self.pageSize = self.backGroundImage.GetWidth() - self.cursor.GetWidth()

	def __OnMove(self):
		(xLocal, yLocal) = self.cursor.GetLocalPosition()
		self.curPos = float(xLocal) / float(self.pageSize)

		if self.eventChange:
			self.eventChange()

	def SetSliderPos(self, pos):
		self.curPos = pos
		self.cursor.SetPosition(int(self.pageSize * pos), 0)

	def GetSliderPos(self):
		return self.curPos

	def SetEvent(self, event):
		self.eventChange = event

	def Enable(self):
		self.cursor.Show()

	def Disable(self):
		self.cursor.Hide()

if app.USE_OFFLINESHOP:
	class OffshopCheckBox(Window):
		def __init__(self, images = {}):
			Window.__init__(self)
			self.clear()
			self.__loadCheckBox(images)
			self.SetOnMouseLeftButtonUpEvent(self.__OnClick)
			self.SetWindowName("checkbox")


		def clear(self):
			self.status = "disabled"
			self.bg_image = None
			self.tip_image = None



		def __del__(self):
			self.status		= "disabled"
			self.bg_image	= None
			self.tip_image	= None
			Window.__del__(self)
		
		
		def __loadCheckBox(self, images):
			bg = ImageBox()
			bg.SetParent(self)
			bg.SetPosition(0,0)

			if not images:
				bg.LoadImage("d:/ymir work/ui/pattern/checkbox_bg.png")
			else:
				bg.LoadImage(images['base'])

			bg.SetOnMouseLeftButtonUpEvent(self.__OnClick)
			bg.SetWindowName("checkbox_bg")
			self.SetSize(bg.GetWidth(), bg.GetHeight())
			bg.Show()
			
			
			self.bg_image = bg
			
			
			#tip image
			tip = ImageBox()
			tip.SetParent(self.bg_image)

			if not images:
				tip.LoadImage("d:/ymir work/ui/pattern/checkbox_tip.png")
			else:
				tip.LoadImage(images['tip'])

			tip.SetPosition(0 , 0)
			tip.Show()
			tip.SetWindowName("checkbox_tip")
			tip.SetOnMouseLeftButtonUpEvent(self.__OnClick)
			
			self.tip_image = tip
			
			self.__refreshView()
		
		
		
		def __refreshView(self):
			if self.status == "enabled":
				self.tip_image.Show()
			else:
				self.tip_image.Hide()
		
		
		def __OnClick(self):
			if self.status == "disabled":
				self.status = "enabled"
			
			else:
				self.status = "disabled"
			
			print("clicked!")
			self.__refreshView()
		


		def IsEnabled(self):
			return self.status == "enabled"
		
		
		
		def Enable(self):
			self.status = "enabled"
			self.__refreshView()
		
		def Disable(self):
			self.status = "disabled"
			self.__refreshView()
	
	
	class ExpandedButton(Window):


		STATUS_DEFAULT 	= 0
		STATUS_DOWN		= 1
		STATUS_OVER		= 2



		def __init__(self, template):
			Window.__init__(self)
			self.SetWindowName("ExpandedButton")

			self.defaultImage = None
			self.downImage = None
			self.overImage = None

			self.eventLeftClick = None
			self.updateEvent = None
			self.downEvent = None
			self.baseInfo = {}
			self.status = 0


			default = template.get('default', 	"")
			down	= template.get('down', 		"")
			over	= template.get('over',		"")
			event	= template.get('event',		None)
			update	= template.get('update',	None)
			rotation= template.get('rotation',	0)
			downEv	= template.get('downevent', None)



			if rotation!=0:
				self.baseInfo['rotated'] = True

			if not default or not down or not over:
				dbg.TraceError("RotatedButton : cannot set template [%s]"%str(template))
				return

			self.__SetDefaultVisual(default)
			self.__SetDownVisual(down)
			self.__SetOverVisual(over)

			if event:
				self.__SetEvent(event)

			if rotation:
				self.__SetRotation(rotation)

			self.SetOnMouseLeftButtonUpEvent(self.__OnClickMe)

			if update:
				self.updateEvent = update

			if downEv:
				self.downEvent = downEv

		def __del__(self):
			self.defaultImage = None
			self.downImage = None
			self.overImage = None

			self.eventLeftClick = None
			self.updateEvent = None
			self.baseInfo = {}
			self.status = 0
			self.downEvent = None

			Window.__del__(self)


		def __SetDefaultVisual(self, default):
			img = ExpandedImageBox()
			img.LoadImage(default)
			img.SetParent(self)
			img.SetPosition(0,0)
			img.Show()

			img.SetOnMouseLeftButtonUpEvent(self.__OnClickMe)
			img.OnMouseOverIn = self.__OverIn
			img.OnMouseOverOut= self.__OverOut
			img.OnMouseLeftButtonDown = self.__OnMouseDown

			img.SetWindowName("ExpandedButton_Default")

			self.baseInfo['default'] 	= {'width': img.GetWidth(), 'height': img.GetHeight(),}
			self.defaultImage 			= img

			self.SetSize(img.GetWidth(), img.GetHeight())

		def __SetDownVisual(self, down):
			img = ExpandedImageBox()
			img.LoadImage(down)
			img.SetParent(self)
			img.SetPosition(0, 0)
			img.Hide()

			img.SetOnMouseLeftButtonUpEvent(self.__OnClickMe)
			img.OnMouseOverIn = self.__OverIn
			img.OnMouseOverOut = self.__OverOut
			img.OnMouseLeftButtonDown = self.__OnMouseDown

			img.SetWindowName("ExpandedButton_Down")

			self.baseInfo['down'] = {'width': img.GetWidth(), 'height': img.GetHeight(), }
			self.downImage = img


		def __SetOverVisual(self, over):
			img = ExpandedImageBox()
			img.LoadImage(over)
			img.SetParent(self)
			img.SetPosition(0, 0)
			img.Hide()

			img.SetOnMouseLeftButtonUpEvent(self.__OnClickMe)
			img.OnMouseOverIn = self.__OverIn
			img.OnMouseOverOut = self.__OverOut
			img.OnMouseLeftButtonDown = self.__OnMouseDown

			img.SetWindowName("ExpandedButton_Over")

			self.baseInfo['over'] = {'width': img.GetWidth(), 'height': img.GetHeight(), }
			self.overImage = img

		def __SetEvent(self, event):
			self.eventLeftClick = event




		def __SetRotation(self, rotation):
			self.defaultImage.SetRotation(rotation)
			self.downImage.SetRotation(rotation)
			self.overImage.SetRotation(rotation)


		def __OnClickMe(self):
			if self.eventLeftClick:
				self.eventLeftClick()

			self.status = self.STATUS_DEFAULT
			self.__RefreshView()



		def __OverIn(self):
			if self.status==self.STATUS_DOWN:
				return

			self.status = self.STATUS_OVER
			self.__RefreshView()



		def __OverOut(self):
			if self.status != self.STATUS_DOWN:
				self.status = self.STATUS_DEFAULT
				self.__RefreshView()

			# todebug
			print("over out")

		def __OnMouseDown(self):
			self.status = self.STATUS_DOWN
			self.__RefreshView()
			if self.downEvent:
				self.downEvent()

			# todebug
			print("mouse down")




		def __RefreshView(self):
			images = {
				self.STATUS_DEFAULT : self.defaultImage,
				self.STATUS_DOWN	: self.downImage,
				self.STATUS_OVER	: self.overImage,
			}

			for image in images.values():
				image.Hide()

			images[self.status].Show()

		def OnUpdate(self):
			if self.updateEvent:
				self.updateEvent()

		def SetScale(self, x , y):
			self.defaultImage.SetScale(x,y)
			self.downImage.SetScale(x,y)
			self.overImage.SetScale(x,y)



			if self.baseInfo.get('rotated', False):
				width = self.baseInfo['default']['height']
				height= self.baseInfo['default']['width']


			else:
				height = self.baseInfo['default']['height']
				width = self.baseInfo['default']['width']



			newwidth  = int( float(width)  * x)
			newheight = int( float(height) * y)


			self.SetSize(newwidth, newheight)


	class CustomScrollBar(Window):



		HORIZONTAL 	= 1
		VERTICAL	= 2

		BOTTOM		= 1
		TOP			= 2
		RIGHT		= 3
		LEFT		= 4





		def __init__(self, template):
			Window.__init__(self)
			self.baseImage = None
			self.button1 = None
			self.button2 = None
			self.middleButton = None

			self.onScroll = None
			self.parent = None
			self.orientation = 0
			self.pos = 0.0
			self.middleScale = 0.1
			self.step = 0.1

			self.baseInfo = {}
			self.mouseOffset = {}


			base	= template.get('base', 			"")
			button1 = template.get('button1', 		{})
			button2 = template.get('button2', 		{})
			middle	= template.get('middle', 		{})
			onscroll= template.get('onscroll', 		None)
			orient	= template.get('orientation',	0)
			align	= template.get('align',			{})
			parent	= template.get('parent',		None)
			position= template.get('position',		{})

			if not base or not button1 or not button2 or not middle or not onscroll or not orient or not parent:
				dbg.TraceError("CustomScrollBar : cannot set template [%s]"%str(template))
				return

			self.__SetParent(parent)
			self.__SetOrientation(orient)
			self.__LoadBaseImage(base)
			self.__LoadButton1(button1)
			self.__LoadButton2(button2)
			self.__LoadMiddleButton(middle)

			self.__SetOnScrollEvent(onscroll)
			if template.has_key('align'):
				self.__SetAlign(align)

			elif template.has_key('position'):
				self.__SetPosition(position)



		def __SetParent(self, parent):
			if parent:
				self.parent = parent
				self.SetParent(parent)

		def __SetOrientation(self, orient):
			self.orientation = orient

		def __LoadBaseImage(self, base):
			bg = ExpandedImageBox()
			bg.LoadImage(base)
			bg.SetParent(self)
			bg.SetPosition(0,0)
			bg.Show()

			w , h = (bg.GetWidth() , bg.GetHeight())
			self.baseInfo = {'base' : {'width':w, 'height':h,}}
			self.SetSize(w,h)

			bg.OnMouseLeftButtonDown = self.__OnClickBaseImage
			self.baseImage = bg

		def __LoadButton1(self, button1):
			button1['event'] = self.__OnClickButton1

			btn = ExpandedButton(button1)
			btn.SetParent(self.baseImage)
			btn.SetPosition(0,0)
			btn.Show()

			self.button1 = btn


		def __LoadButton2(self, button2):
			button2['event'] = self.__OnClickButton2

			btn = ExpandedButton(button2)
			btn.SetParent(self.baseImage)

			if self.orientation == self.HORIZONTAL:
				leng = btn.GetWidth()
				btn.SetPosition(self.GetWidth() - leng , 0)

			elif self.orientation == self.VERTICAL:
				leng = btn.GetHeight()
				btn.SetPosition(0, self.GetHeight() - leng)
			btn.Show()

			self.button2 = btn



		def __LoadMiddleButton(self, middle):
			middle['downevent'] = self.__OnClickMiddle
			middle['update']	= self.__OnUpdateMiddleBar
			btn = ExpandedButton(middle)
			btn.SetParent(self.baseImage)


			if self.orientation == self.HORIZONTAL:
				btn.SetPosition(self.button1.GetWidth(), 0)

			elif self.orientation == self.VERTICAL:
				btn.SetPosition(0, self.button1.GetHeight())

			btn.Show()
			self.middleButton = btn



		def __SetOnScrollEvent(self, onscroll):
			self.onScroll = onscroll



		def __SetAlign(self, align):
			mode	= align['mode']
			offset1	= align.get('offset1',0)
			offset2	= align.get('offset2',0)

			if not self.parent:
				return

			if self.orientation == self.HORIZONTAL:
				if mode == self.TOP:
					self.SetPosition(offset1, 0)

				if mode == self.BOTTOM:
					self.SetPosition(offset1, self.parent.GetHeight() - self.GetHeight())

				self.SetScrollBarLength(self.parent.GetWidth() - (offset1 + offset2))


			elif self.orientation == self.VERTICAL:
				if mode == self.RIGHT:
					self.SetPosition(self.parent.GetWidth()-self.GetWidth(),  offset1 )

				elif mode == self.LEFT:
					self.SetPosition(0, offset1)

				self.SetScrollBarLength(self.parent.GetHeight() - (offset1 + offset2))



		def __SetPosition(self, position):
			self.SetPosition(position['x'] , position['y'])



		def SetScrollBarLength(self, leng):
			if self.orientation == self.VERTICAL:
				self.SetSize(self.GetWidth(), leng)


				baseScale = float(leng) / float(self.baseInfo['base']['height'])
				self.baseImage.SetScale(1.0, baseScale)

				scrollsize  = leng - (self.__GetElementLength(self.button1) + self.__GetElementLength(self.button2))
				middle_leng = int(self.middleScale * scrollsize)
				init_middle = float(self.middleButton.baseInfo['default']['height'])

				self.middleButton.SetScale(1.0, float(middle_leng)/init_middle)
				self.middleButton.SetPosition(0,self.__GetElementLength(self.button1) + int((scrollsize - self.__GetElementLength(self.middleButton))* self.pos))

				self.button2.SetPosition(0, self.GetHeight()-self.button2.GetHeight())

			elif self.orientation == self.HORIZONTAL:
				self.SetSize(leng, self.GetHeight())

				baseScale = float(leng) / float(self.baseInfo['base']['width'])
				self.baseImage.SetScale(baseScale, 1.0)


				scrollsize = leng - (self.__GetElementLength(self.button1) + self.__GetElementLength(self.button2))
				middle_leng = int(self.middleScale * scrollsize)
				init_middle = float(self.middleButton.baseInfo['default']['width'])

				self.middleButton.SetScale(float(middle_leng) / init_middle, 1.0)
				self.middleButton.SetPosition(self.__GetElementLength(self.button1) + int((scrollsize - self.__GetElementLength(self.middleButton)) * self.pos),0)

				self.button2.SetPosition(self.GetWidth() - self.button2.GetWidth(), 0)




		def __GetElementLength(self, element):
			if self.orientation == self.VERTICAL:
				return element.GetHeight()

			if self.orientation == self.HORIZONTAL:
				return element.GetWidth()
			return 0




		def __OnUpdateMiddleBar(self):
			if self.middleButton.status != ExpandedButton.STATUS_DOWN:
				return



			x,y 	= wndMgr.GetMousePosition()
			gx,gy	= self.middleButton.GetGlobalPosition()

			gx += self.mouseOffset.get('x',0)
			gy += self.mouseOffset.get('y',0)

			if self.orientation == self.VERTICAL:
				if y == gy:
					return

			elif self.orientation == self.HORIZONTAL:
				if x == gx:
					return

			self.__OnMoveMiddleBar(x,y)

		def __OnClickBaseImage(self):
			x,y 	= wndMgr.GetMousePosition()
			gx,gy	= self.middleButton.GetGlobalPosition()

			offset = self.__GetElementLength(self.middleButton)/2

			gx += offset
			gy += offset

			if self.orientation == self.VERTICAL:
				if y == gy:
					return

			elif self.orientation == self.HORIZONTAL:
				if x == gx:
					return

			self.mouseOffset = {'x' : offset, 'y': offset}
			self.__OnMoveMiddleBar(x,y)


		def __OnClickButton2(self):
			self.mouseOffset={'x' : 0, 'y' :0}
			gx,gy = self.middleButton.GetGlobalPosition()
			if self.orientation == self.VERTICAL:
				gy += self.__GetElementLength(self.middleButton)
			elif self.orientation == self.HORIZONTAL:
				gx += self.__GetElementLength(self.middleButton)

			self.__OnMoveMiddleBar(gx,gy)




		def __OnClickButton1(self):
			self.mouseOffset={'x' : 0, 'y' :0}
			gx, gy = self.middleButton.GetGlobalPosition()
			if self.orientation == self.VERTICAL:
				gy -= self.__GetElementLength(self.middleButton)
			elif self.orientation == self.HORIZONTAL:
				gx -= self.__GetElementLength(self.middleButton)

			self.__OnMoveMiddleBar(gx, gy)



		def __OnMoveMiddleBar(self, x , y):
			gx, gy = self.GetGlobalPosition()
			x -= self.mouseOffset.get('x', 0)
			y -= self.mouseOffset.get('y', 0)


			if self.orientation == self.VERTICAL:
				min_ = gy  + self.__GetElementLength(self.button1)
				max_ = min_ + (self.GetHeight() - (self.__GetElementLength(self.button1) + self.__GetElementLength(self.button2) + self.__GetElementLength(self.middleButton)))

				if max_ < y and self.pos == 1.0:
					return

				if min_ > y and self.pos == 0.0:
					return

				realy = max(y, min_)
				realy = min(realy, max_)
				scroll= max_-min_

				if scroll == 0.0:
					return


				self.pos = float(realy-min_) / float(scroll)
				self.middleButton.SetPosition(0, realy-gy)

				self.__OnScroll()

			elif self.orientation == self.HORIZONTAL:
				min_ = gx + self.__GetElementLength(self.button1)
				max_ = min_ + (self.GetWidth() - (self.__GetElementLength(self.button1) + self.__GetElementLength(self.button2) + self.__GetElementLength(self.middleButton)))

				if max_ < x and self.pos == 1.0:
					return

				if min_ > x and self.pos == 0.0:
					return

				realx = max(x, min_)
				realx = min(realx, max_)
				scroll = max_ - min_

				if scroll == 0.0:
					return

				self.pos = float(realx - min_) / float(scroll)
				self.middleButton.SetPosition(realx-gx, 0)

				self.__OnScroll()




		def __OnScroll(self):
			if self.onScroll:
				self.onScroll()




		def __OnClickMiddle(self):
			x,y 	= wndMgr.GetMousePosition()
			gx,gy	= self.middleButton.GetGlobalPosition()

			x-= gx
			y-= gy

			self.mouseOffset = {"x" : x, "y": y ,}

		def GetPos(self):
			return self.pos

		def GetStep(self):
			return self.step

		def SetScrollStep(self, step):
			step = min(1.0, max(0.1 , step))
			self.middleScale = step
			self.step = step

			self.SetScrollBarLength(self.__GetElementLength(self.baseImage))



class ListBox(Window):
	def GetSelectedItemText(self):
		return self.textDict.get(self.selectedLine, "")

	TEMPORARY_PLACE = 3

	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.overLine = -1
		self.selectedLine = -1
		self.width = 0
		self.height = 0
		self.stepSize = 17
		self.basePos = 0
		self.showLineCount = 0
		self.visibleLineCount = 10
		self.currentPosition = 0
		self.itemCenterAlign = TRUE
		self.itemList = []
		self.keyDict = {}
		self.textDict = {}
		self.event = lambda *arg: None
		
	def __del__(self):
		Window.__del__(self)

	def SetWidth(self, width):
		self.SetSize(width, self.height)

	def SetSize(self, width, height):
		Window.SetSize(self, width, height)
		self.width = width
		self.height = height

	def SetTextCenterAlign(self, flag):
		self.itemCenterAlign = flag

	def SetBasePos(self, pos):
		self.basePos = pos
		self._LocateItem()

	def ClearItem(self):
		self.keyDict = {}
		self.textDict = {}
		self.itemList = []
		self.overLine = -1
		self.selectedLine = -1

	def InsertItem2(self, number, text, textColor = 0x00000000):
		self.keyDict[len(self.itemList)] = number
		self.textDict[len(self.itemList)] = text

		textLine = TextLine()
		textLine.SetParent(self)
		textLine.SetText(text)
		# textLine.SetWindowHorizontalAlignRight()
		# textLine.SetHorizontalAlignLeft()
		if textColor != 0x00000000:
			textLine.SetPackedFontColor(textColor)
		textLine.Show()

		if self.itemCenterAlign:
			#textLine.SetWindowHorizontalAlignRight()
			textLine.SetWindowHorizontalAlignLeft()
			textLine.SetHorizontalAlignLeft()

			self.itemList.append(textLine)

			self._LocateItem()

	def InsertItem(self, number, text, textColor = 0x00000000):
		self.keyDict[len(self.itemList)] = number
		self.textDict[len(self.itemList)] = text

		textLine = TextLine()
		textLine.SetParent(self)
		textLine.SetText(text)
		if textColor != 0x00000000:
			textLine.SetPackedFontColor(textColor)
		textLine.Hide()

		if self.itemCenterAlign:
			textLine.SetWindowHorizontalAlignCenter()
			textLine.SetHorizontalAlignCenter()

		self.itemList.append(textLine)

		self._LocateItem()

	def ChangeItem(self, number, text):
		for key, value in self.keyDict.items():
			if value == number:
				self.textDict[key] = text

				if number < len(self.itemList):
					self.itemList[key].SetText(text)

				return

	def LocateItem(self):
		self._LocateItem()
		
	def SetVisibleLineCount(self, count):
		self.visibleLineCount = count
		
	def GetVisibleLineCount(self):
		return self.visibleLineCount
		
	def GetVisibleHeight(self):
		return self.visibleLineCount * self.stepSize

	def _LocateItem(self):
		yPos = 0
		self.showLineCount = 0

		if app.ENABLE_COMMON_CHANGES:
			skipCount = self.basePos
			for textLine in self.itemList:
				textLine.Hide()
				if skipCount > 0:
					skipCount -= 1
					continue
				
				if localeinfo.IsARABIC():
					w, h = textLine.GetTextSize()
					textLine.SetPosition(w+10, yPos + 3)
				else:
					textLine.SetPosition(0, yPos + 3)
				
				yPos += self.stepSize
				if yPos <= self.GetHeight():
					self.showLineCount += 1
					textLine.Show()
		else:
			i = 0
			for textLine in self.itemList:
				if i >= self.currentPosition and i < (self.currentPosition + self.GetVisibleLineCount()):
					if localeinfo.IsARABIC():
						w, h = textLine.GetTextSize()
						textLine.SetPosition(w+10, yPos + 3)
					else:
						textLine.SetPosition(0, yPos + 3)
					
					textLine.Show()
					yPos += self.stepSize
				else:
					textLine.Hide()

				self.showLineCount += 1
				i += 1

	def ArrangeItem(self):
		self.SetSize(self.width, len(self.itemList) * self.stepSize)
		self._LocateItem()

	def ArrangeItem2(self):
		self.SetSize(self.width, len(self.itemList) * self.stepSize)
		self._LocateItem()

	def GetViewItemCount(self):
		return int(self.GetHeight() / self.stepSize)

	def GetItemCount(self):
		return len(self.itemList)

	def SetEvent(self, event):
		self.event = event

	def SelectItem(self, line):

		if not self.keyDict.has_key(line):
			return

		if line == self.selectedLine:
			return

		self.selectedLine = line + self.currentPosition
		self.event(self.keyDict.get(self.selectedLine, 0), self.textDict.get(self.selectedLine, "None"))

	def GetSelectedItem(self):
		return self.keyDict.get(self.selectedLine, 0)

	def OnMouseLeftButtonDown(self):
		if self.overLine < 0:
			return

	def OnMouseLeftButtonUp(self):
		if self.overLine >= 0:
			self.SelectItem(self.overLine+self.basePos)
			
	def OnDown(self):
		if self.GetItemCount() > self.GetVisibleLineCount():
			self.currentPosition = min(self.GetItemCount() - self.GetVisibleLineCount(), self.currentPosition + 1)

			self._LocateItem()
		
	def OnUp(self):
		if self.GetItemCount() > self.GetVisibleLineCount():
			self.currentPosition = max(0, self.currentPosition - 1)

			self._LocateItem()
		
	def OnUpdate(self):
		self.overLine = -1

		if self.IsIn():
			x, y = self.GetGlobalPosition()
			height = self.GetHeight()
			xMouse, yMouse = wndMgr.GetMousePosition()

			if yMouse - y < height - 1:
				self.overLine = (yMouse - y) / self.stepSize

				if self.overLine < 0:
					self.overLine = -1
				if self.overLine >= len(self.itemList):
					self.overLine = -1

	def OnRender(self):
		xRender, yRender = self.GetGlobalPosition()
		yRender -= self.TEMPORARY_PLACE
		widthRender = self.width
		heightRender = self.height + self.TEMPORARY_PLACE*2
		if -1 != self.overLine:
			grp.SetColor(HALF_WHITE_COLOR)
			grp.RenderBar(xRender + 2, yRender + self.overLine*self.stepSize + 4, self.width - 3, self.stepSize)
		
		if -1 != self.selectedLine:
			if app.ENABLE_COMMON_CHANGES:
				if self.selectedLine >= self.basePos:
					if self.selectedLine - self.basePos < self.showLineCount:
						grp.SetColor(SELECT_COLOR)
						grp.RenderBar(xRender + 2, yRender + (self.selectedLine-self.basePos)*self.stepSize + 4, self.width - 3, self.stepSize)
			else:
				if self.selectedLine >= self.currentPosition and self.selectedLine < (self.currentPosition + self.GetVisibleLineCount()):
					if self.selectedLine - self.basePos < self.showLineCount:
						grp.SetColor(SELECT_COLOR)
						grp.RenderBar(xRender + 2, yRender + (self.selectedLine-self.basePos-self.currentPosition) * self.stepSize + 4, self.width - 3, self.stepSize)

class ListBox2(ListBox):
	def __init__(self, *args, **kwargs):
		ListBox.__init__(self, *args, **kwargs)
		self.rowCount = 10
		self.barWidth = 0
		self.colCount = 0

	def SetRowCount(self, rowCount):
		self.rowCount = rowCount

	def SetSize(self, width, height):
		ListBox.SetSize(self, width, height)
		self._RefreshForm()

	def ClearItem(self):
		ListBox.ClearItem(self)
		self._RefreshForm()

	def InsertItem(self, *args, **kwargs):
		ListBox.InsertItem(self, *args, **kwargs)
		self._RefreshForm()

	def OnUpdate(self):
		mpos = wndMgr.GetMousePosition()
		self.overLine = self._CalcPointIndex(mpos)

	def OnRender(self):
		x, y = self.GetGlobalPosition()
		pos = (x + 2, y)

		if -1 != self.overLine:
			grp.SetColor(HALF_WHITE_COLOR)
			self._RenderBar(pos, self.overLine)

		if -1 != self.selectedLine:
			if self.selectedLine >= self.basePos:
				if self.selectedLine - self.basePos < self.showLineCount:
					grp.SetColor(SELECT_COLOR)
					self._RenderBar(pos, self.selectedLine-self.basePos)

	def _CalcPointIndex(self, mpos):
		if self.IsIn():
			px, py = mpos
			gx, gy = self.GetGlobalPosition()
			lx, ly = px - gx, py - gy

			col = lx / self.barWidth
			row = ly / self.stepSize
			idx = col * self.rowCount + row
			if col >= 0 and col < self.colCount:
				if row >= 0 and row < self.rowCount:
					if idx >= 0 and idx < len(self.itemList):
						return idx

		return -1

	def _CalcRenderPos(self, pos, idx):
		x, y = pos
		row = idx % self.rowCount
		col = idx / self.rowCount
		return (x + col * self.barWidth, y + row * self.stepSize)

	def _RenderBar(self, basePos, idx):
		x, y = self._CalcRenderPos(basePos, idx)
		grp.RenderBar(x, y, self.barWidth - 3, self.stepSize)

	def _LocateItem(self):
		pos = (0, self.TEMPORARY_PLACE)

		self.showLineCount = 0
		for textLine in self.itemList:
			x, y = self._CalcRenderPos(pos, self.showLineCount)
			textLine.SetPosition(x, y)
			textLine.Show()

			self.showLineCount += 1

	def _RefreshForm(self):
		if len(self.itemList) % self.rowCount:
			self.colCount = len(self.itemList) / self.rowCount + 1
		else:
			self.colCount = len(self.itemList) / self.rowCount

		if self.colCount:
			self.barWidth = self.width / self.colCount
		else:
			self.barWidth = self.width

class ComboBoxImage(Window):
	class ListBoxWithBoard(ListBox):
		def __init__(self, layer):
			ListBox.__init__(self, layer)

		def __del__(self):
			ListBox.__del__(self)

		def OnRender(self):
			xRender, yRender = self.GetGlobalPosition()
			yRender -= self.TEMPORARY_PLACE
			widthRender = self.width
			heightRender = self.height + self.TEMPORARY_PLACE*2
			grp.SetColor(BACKGROUND_COLOR)
			grp.RenderBar(xRender, yRender, widthRender, heightRender)
			grp.SetColor(DARK_COLOR)
			grp.RenderLine(xRender, yRender, widthRender, 0)
			grp.RenderLine(xRender, yRender, 0, heightRender)
			ListBox.OnRender(self)

	def __init__(self, parent, name, x, y):
		Window.__init__(self)
		
		self.isSelected = False
		self.isOver = False
		self.isListOpened = False
		self.event = lambda *arg: None
		self.enable = True
		self.imagebox = None
		
		## ImageBox
		image = ExpandedImageBox()
		image.SetParent(parent)
		image.LoadImage(name)
		image.SetPosition(x, y)
		image.Show()
		self.imagebox = image
		
		## BaseSetting
		self.x = x + 1
		self.y = y + 1
		self.width = self.imagebox.GetWidth() - 3
		self.height = self.imagebox.GetHeight() - 3
		self.SetParent(parent)

		## TextLine
		self.textLine = MakeTextLine(self)
		self.textLine.SetText(localeinfo.UI_ITEM)
		
		## ListBox
		self.listBox = self.ListBoxWithBoard("TOP_MOST")
		self.listBox.SetPickAlways()
		self.listBox.SetParent(self)
		self.listBox.SetVisibleLineCount(12)
		self.listBox.SetEvent(__mem_func__(self.OnSelectItem))
		self.listBox.Hide()
		
		Window.SetPosition(self, self.x, self.y)
		Window.SetSize(self, self.width, self.height)
		self.textLine.UpdateRect()
		self.listBox.SetPosition(0, self.height + 5)
		self.__ArrangeListBox()

	def __del__(self):
		Window.__del__(self)

	def Destroy(self):
		self.event = lambda *arg: None
		
		if self.textLine:
			del self.textLine
			self.textLine = None
		
		if self.listBox:
			self.listBox.ClearItem()
			del self.listBox
			self.listBox = None
		
		if self.imagebox:
			del self.imagebox
			self.imagebox = None

	def SetPosition(self, x, y):
		Window.SetPosition(self, x, y)
		self.imagebox.SetPosition(x, y)
		self.x = x
		self.y = y
		self.__ArrangeListBox()

	def SetSize(self, width, height):
		Window.SetSize(self, width, height)
		self.width = width
		self.height = height
		self.textLine.UpdateRect()
		self.__ArrangeListBox()
		
	def SetImageScale(self, scale_x, scale_y):
		self.imagebox.SetScale(scale_x, scale_y)
		self.width = self.imagebox.GetWidth() - 3
		self.height = self.imagebox.GetHeight() - 3
		Window.SetSize(self, self.width, self.height)
		self.textLine.UpdateRect()
		self.__ArrangeListBox()
		
	def __ArrangeListBox(self):
		self.listBox.SetPosition(0, self.height + 5)

		if self.listBox.GetItemCount() <= self.listBox.GetVisibleLineCount():
			self.listBox.SetSize(self.width, self.listBox.GetHeight())
		else:
			self.listBox.SetSize(self.width, self.listBox.GetVisibleHeight())

	def Enable(self):
		self.enable = True

	def Disable(self):
		self.enable = False
		self.CloseListBox()

	def SetEvent(self, event):
		self.event = event

	def ClearItem(self):
		self.CloseListBox()
		self.listBox.ClearItem()

	def InsertItem(self, index, name):
		self.listBox.InsertItem(index, name)
		self.listBox.ArrangeItem()

	def InsertItem2(self, index, name):
		self.listBox.InsertItem2(index, name)
		self.listBox.ArrangeItem()

	def SetCurrentItem(self, text):
		self.textLine.SetText(text)

	def SelectItem(self, key):
		self.listBox.SelectItem(key)

	def OnSelectItem(self, index, name):
		self.CloseListBox()
		self.event(index)

	def CloseListBox(self):
		self.isListOpened = False
		
		if self.listBox:
			self.listBox.Hide()

	def OnMouseLeftButtonDown(self):
		if not self.enable:
			return

		self.isSelected = True

	def OnMouseLeftButtonUp(self):
		if not self.enable:
			return
		
		self.isSelected = False
		
		if self.isListOpened:
			self.CloseListBox()
		else:
			if self.listBox.GetItemCount() > 0:
				self.isListOpened = True
				self.listBox.Show()
				self.__ArrangeListBox()

	def OnRunMouseWheel(self, nLen):
		if nLen > 0:
			self.listBox.OnUp()
			return True
		elif nLen < 0:
			self.listBox.OnDown()
			return True
		
		return False

	def OnUpdate(self):
		if not self.enable:
			return

		if self.IsIn():
			self.isOver = True
		else:
			self.isOver = False

	def OnRender(self):
		self.x, self.y = self.GetGlobalPosition()
		xRender = self.x
		yRender = self.y
		widthRender = self.width
		heightRender = self.height
		
		if self.isOver:
			grp.SetColor(HALF_WHITE_COLOR)
			grp.RenderBar(xRender + 2, yRender + 3, self.width - 3, heightRender - 5)
			
			if self.isSelected:
				grp.SetColor(WHITE_COLOR)
				grp.RenderBar(xRender + 2, yRender + 3, self.width - 3, heightRender - 5)
		def SetSize(self, width, height):
			Window.SetSize(self, width, height)
			self.width = width
			self.height = height
			self.textLine.UpdateRect()
			self.__ArrangeListBox()

		def __ArrangeListBox(self):
			self.listBox.SetPosition(0, self.height + 5)
			self.listBox.SetWidth(self.width)

		def Enable(self):
			self.enable = True

		def Disable(self):
			self.enable = False
			self.textLine.SetText("")
			self.CloseListBox()

		def SetEvent(self, event):
			self.event = event

		def ClearItem(self):
			self.CloseListBox()
			self.listBox.ClearItem()

		def InsertItem(self, index, name):
			self.listBox.InsertItem(index, name)
			self.listBox.ArrangeItem()

		def SetCurrentItem(self, text):
			self.textLine.SetText(text)

		def SelectItem(self, key):
			self.listBox.SelectItem(key)

		def OnSelectItem(self, index, name):
			self.CloseListBox()
			self.event(index)

		def CloseListBox(self):
			self.isListOpened = False
			self.listBox.Hide()

		def OnMouseLeftButtonDown(self):
			if not self.enable:
				return

			self.isSelected = True

		def OnMouseLeftButtonUp(self):
			if not self.enable:
				return

			self.isSelected = False

			if self.isListOpened:
				self.CloseListBox()
			else:
				if self.listBox.GetItemCount() > 0:
					self.isListOpened = True
					self.listBox.Show()
					self.__ArrangeListBox()

		def OnUpdate(self):
			if not self.enable:
				return

			if self.IsIn():
				self.isOver = True
			else:
				self.isOver = False

		def OnRender(self):
			self.x, self.y = self.GetGlobalPosition()
			xRender = self.x
			yRender = self.y
			widthRender = self.width
			heightRender = self.height
			if self.isOver:
				grp.SetColor(HALF_WHITE_COLOR)
				grp.RenderBar(xRender + 2, yRender + 3, self.width - 3, heightRender - 5)
				if self.isSelected:
					grp.SetColor(WHITE_COLOR)
					grp.RenderBar(xRender + 2, yRender + 3, self.width - 3, heightRender - 5)

class ComboBox(Window):

	class ListBoxWithBoard(ListBox):

		def __init__(self, layer):
			ListBox.__init__(self, layer)

		def OnRender(self):
			xRender, yRender = self.GetGlobalPosition()
			yRender -= self.TEMPORARY_PLACE
			widthRender = self.width
			heightRender = self.height + self.TEMPORARY_PLACE*2
			grp.SetColor(BACKGROUND_COLOR)
			grp.RenderBar(xRender, yRender, widthRender, heightRender)
			grp.SetColor(DARK_COLOR)
			grp.RenderLine(xRender, yRender, widthRender, 0)
			grp.RenderLine(xRender, yRender, 0, heightRender)
			grp.SetColor(BRIGHT_COLOR)
			grp.RenderLine(xRender, yRender+heightRender, widthRender, 0)
			grp.RenderLine(xRender+widthRender, yRender, 0, heightRender)

			ListBox.OnRender(self)

	def __init__(self):
		Window.__init__(self)
		self.x = 0
		self.y = 0
		self.width = 0
		self.height = 0
		self.isSelected = False
		self.isOver = False
		self.isListOpened = False
		self.event = lambda *arg: None
		self.enable = True
		self.bIsShopSearch = False
		self.textLine = MakeTextLine(self)
		self.textLine.SetText(localeinfo.UI_ITEM)

		self.listBox = self.ListBoxWithBoard("TOP_MOST")
		self.listBox.SetPickAlways()
		self.listBox.SetParent(self)
		self.listBox.SetEvent(__mem_func__(self.OnSelectItem))
		self.listBox.Hide()

	def __del__(self):
		Window.__del__(self)

	def Destroy(self):
		self.textLine = None
		self.listBox = None

	def SetPosition(self, x, y):
		Window.SetPosition(self, x, y)
		self.x = x
		self.y = y
		self.__ArrangeListBox()

	def SetSize(self, width, height):
		Window.SetSize(self, width, height)
		self.width = width
		self.height = height
		self.textLine.UpdateRect()
		self.__ArrangeListBox()

	def __ArrangeListBox(self):
		self.listBox.SetPosition(0, self.height + 5)
		self.listBox.SetWidth(self.width)

	def Enable(self):
		self.enable = True

	def Disable(self):
		self.enable = False
		self.textLine.SetText("")
		self.CloseListBox()

	def SetEvent(self, event):
		self.event = event

	def ClearItem(self):
		self.CloseListBox()
		self.listBox.ClearItem()

	def InsertItem(self, index, name):
		self.listBox.InsertItem(index, name)
		self.listBox.ArrangeItem()

	def InsertItem2(self, index, name):
		self.listBox.InsertItem2(index, name)
		self.listBox.ArrangeItem2()

	def SetCurrentItem(self, text):
		self.textLine.SetText(text)

	def SetCurrentItem2(self, text):
		self.textLine.SetText(text)
		self.textLine.SetWindowHorizontalAlignCenter()


	def SelectItem(self, key):
		self.listBox.SelectItem(key)

	def SetEventNew(self, event):
		self.event = event
		self.bIsShopSearch = True

	def OnSelectItem(self, index, name):

		self.CloseListBox()
		if self.bIsShopSearch:
			self.event(self, index, name)
		else:
			self.event(index)

	def CloseListBox(self):
		self.isListOpened = False
		self.listBox.Hide()

	def OnMouseLeftButtonDown(self):
		if not self.enable:
			return

		self.isSelected = True

	def OnMouseLeftButtonUp(self):
		if not self.enable:
			return

		self.isSelected = False

		if self.isListOpened:
			self.CloseListBox()
		else:
			if self.listBox.GetItemCount() > 0:
				self.isListOpened = True
				self.listBox.Show()
				self.__ArrangeListBox()

	def OnUpdate(self):
		if not self.enable:
			return

		if self.IsIn():
			self.isOver = True
		else:
			self.isOver = False

	def OnRender(self):
		self.x, self.y = self.GetGlobalPosition()
		xRender = self.x
		yRender = self.y
		widthRender = self.width
		heightRender = self.height
		grp.SetColor(BACKGROUND_COLOR)
		grp.RenderBar(xRender, yRender, widthRender, heightRender)
		grp.SetColor(DARK_COLOR)
		grp.RenderLine(xRender, yRender, widthRender, 0)
		grp.RenderLine(xRender, yRender, 0, heightRender)
		grp.SetColor(BRIGHT_COLOR)
		grp.RenderLine(xRender, yRender+heightRender, widthRender, 0)
		grp.RenderLine(xRender+widthRender, yRender, 0, heightRender)

		if self.isOver:
			grp.SetColor(HALF_WHITE_COLOR)
			grp.RenderBar(xRender + 2, yRender + 3, self.width - 3, heightRender - 5)

			if self.isSelected:
				grp.SetColor(WHITE_COLOR)
				grp.RenderBar(xRender + 2, yRender + 3, self.width - 3, heightRender - 5)


class ComboBoxNew(Window):
	# ==========================================================================
	# Modern flat dropdown styled like uiadvancedgameoptions.ResolutionSelector /
	# ResolutionListBox (1px bordered bar + beige text + arrow_down.png), replacing
	# the legacy beveled black ComboBox look.  Public API is identical to ui.ComboBox
	# so switching a consumer is a one-line change (ui.ComboBox() -> ui.ComboBoxNew()).
	# The popup self-hosts on the TOP_MOST layer as a child of self (like the legacy
	# ComboBox) so __init__ takes no top-board argument and the popup auto-hides with
	# its parent window.  Scroll = ScrollBarNew + mouse wheel, capped at VISIBLE_ROWS
	# (basePos-driven, the ENABLE_COMMON_CHANGES-safe path used by ResolutionSelector).
	# ==========================================================================
	BORDER_COLOR = 0xff2e251f   # RES_BORDER_COLOR
	BOX_FILL     = 0xff4d463d   # RES_BOX_FILL   (closed box)
	LIST_FILL    = 0xff3a342c   # RES_LIST_FILL  (open popup)
	TEXT_COLOR   = 0xffafa496   # RES_TEXT_COLOR
	HOVER_FILL   = 0xff5a5249   # subtle lighten on hover (legacy flashed white)
	DISABLE_FILL = 0xff2a2620
	DISABLE_TEXT = 0xff6b645a
	ARROW_IMAGE  = "d:/ymir work/ui/game/advanced_game_options/arrow_down.png"
	VISIBLE_ROWS = 8            # scrollbar appears beyond this many rows

	class _ListBoxNew(ListBox):
		# ResolutionListBox clone: beige, left-aligned rows with Arabic RTL anchoring,
		# scrolled via basePos.  Inherits the base ListBox OnRender so hover/selected
		# rows draw with HALF_WHITE_COLOR / SELECT_COLOR exactly like the reference.
		def __init__(self, layer = "UI"):
			ListBox.__init__(self, layer)
			self.SetTextCenterAlign(False)
			self.itemTextColor = ComboBoxNew.TEXT_COLOR   # owner overrides this in __BuildPopup

		def __StyleLine(self, textLine):
			textLine.SetWindowHorizontalAlignLeft()
			textLine.SetHorizontalAlignLeft()
			textLine.SetPackedFontColor(self.itemTextColor)

		def InsertItem(self, number, text, textColor = 0x00000000):
			self.keyDict[len(self.itemList)] = number
			self.textDict[len(self.itemList)] = text
			textLine = TextLine()
			textLine.SetParent(self)
			textLine.SetText(text)
			self.__StyleLine(textLine)
			textLine.Hide()
			self.itemList.append(textLine)
			self._LocateItem()

		def InsertItem2(self, number, text, textColor = 0x00000000):
			self.InsertItem(number, text, textColor)

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

	def __init__(self, borderColor = None, boxFill = None, listFill = None, textColor = None, hoverFill = None, disableFill = None, disableText = None):
		Window.__init__(self)
		self.x = 0
		self.y = 0
		self.width = 0
		self.height = 0
		self.enable = True
		self.isOver = False
		self.isListOpened = False
		self.textCenter = False
		self.bIsShopSearch = False
		self.event = lambda *arg: None
		# Optional per-instance color overrides shadow the class defaults; pass any subset
		# (0xAARRGGBB), e.g. ui.ComboBoxNew(boxFill = 0xff112233, textColor = 0xffffffff).
		if borderColor is not None: self.BORDER_COLOR = borderColor
		if boxFill is not None: self.BOX_FILL = boxFill
		if listFill is not None: self.LIST_FILL = listFill
		if textColor is not None: self.TEXT_COLOR = textColor
		if hoverFill is not None: self.HOVER_FILL = hoverFill
		if disableFill is not None: self.DISABLE_FILL = disableFill
		if disableText is not None: self.DISABLE_TEXT = disableText
		self.__BuildBox()
		self.__BuildPopup()

	def __del__(self):
		Window.__del__(self)

	def Destroy(self):
		# Disable first: the window keeps ticking until GC, and OnUpdate/__ApplyBoxColors
		# would dereference the members we null below on the next hover transition.
		self.enable = False
		self.event = lambda *arg: None
		self.boxText = None
		self.arrow = None
		self.boxInner = None
		self.boxOuter = None
		self.listBox = None
		self.scrollBar = None
		self.popupInner = None
		self.popupOuter = None
		self.popup = None

	# ---- construction -------------------------------------------------------
	def __MakeBorderedBar(self, parent, fillColor):
		outer = Bar()
		outer.SetParent(parent)
		outer.SetPosition(0, 0)
		outer.SetColor(self.BORDER_COLOR)
		outer.AddFlag("not_pick")
		outer.Show()
		inner = Bar()
		inner.SetParent(outer)
		inner.SetPosition(1, 1)
		inner.SetColor(fillColor)
		inner.AddFlag("not_pick")
		inner.Show()
		return outer, inner

	def __SizeBorderedBar(self, outer, inner, w, h):
		outer.SetSize(w, h)
		inner.SetSize(max(0, w - 2), max(0, h - 2))

	def __BuildBox(self):
		(outer, inner) = self.__MakeBorderedBar(self, self.BOX_FILL)
		self.boxOuter = outer
		self.boxInner = inner

		boxText = TextLine()
		boxText.SetParent(self)
		boxText.SetHorizontalAlignLeft()
		boxText.SetPackedFontColor(self.TEXT_COLOR)
		boxText.AddFlag("not_pick")
		boxText.Show()
		self.boxText = boxText

		arrow = ImageBox()
		arrow.SetParent(self)
		arrow.AddFlag("not_pick")
		arrow.LoadImage(self.ARROW_IMAGE)
		arrow.Show()
		self.arrow = arrow

	def __BuildPopup(self):
		popup = Window("TOP_MOST")
		popup.SetParent(self)
		popup.Hide()
		self.popup = popup

		(outer, inner) = self.__MakeBorderedBar(popup, self.LIST_FILL)
		self.popupOuter = outer
		self.popupInner = inner

		listBox = self._ListBoxNew("TOP_MOST")
		listBox.itemTextColor = self.TEXT_COLOR   # honor a per-instance textColor override
		listBox.SetParent(popup)
		listBox.SetPosition(6, 4)
		listBox.SetPickAlways()
		listBox.SetEvent(__mem_func__(self.OnSelectItem))
		listBox.Show()
		self.listBox = listBox

		scrollBar = ScrollBarNew()
		scrollBar.SetParent(popup)
		scrollBar.SetScrollEvent(__mem_func__(self.__OnScroll))
		scrollBar.Hide()
		self.scrollBar = scrollBar

		popup.OnRunMouseWheel = __mem_func__(self.__OnWheel)
		listBox.OnRunMouseWheel = __mem_func__(self.__OnWheel)

	# ---- geometry -----------------------------------------------------------
	def SetPosition(self, x, y):
		Window.SetPosition(self, x, y)
		self.x = x
		self.y = y

	def SetSize(self, width, height):
		Window.SetSize(self, width, height)
		self.width = width
		self.height = height
		self.__LayoutBox()
		self.__RefreshPopupLayout()

	def __LayoutBox(self):
		self.__SizeBorderedBar(self.boxOuter, self.boxInner, self.width, self.height)

		arrowY = max(0, (self.height - self.arrow.GetHeight()) / 2)
		if localeinfo.IsARABIC():
			self.arrow.SetPosition(6, arrowY)
		else:
			self.arrow.SetPosition(self.width - self.arrow.GetWidth() - 6, arrowY)

		self.__LayoutBoxText()

	def __LayoutBoxText(self):
		textY = max(2, (self.height - 14) / 2)
		if self.textCenter:
			# WindowHorizontalAlignCenter already centers the label in the box at x=0
			# (C++ UpdateRect: left = parentWidth/2 - myWidth/2 + m_x); an extra x offset
			# would shove it past the right border, so keep m_x at 0.
			self.boxText.SetWindowHorizontalAlignCenter()
			self.boxText.SetHorizontalAlignCenter()
			self.boxText.SetPosition(0, textY)
		elif localeinfo.IsARABIC():
			# RTL: AlignLeft is the Arabic convention (engine right-anchors the glyphs and
			# flows them left). Position the label near the RIGHT edge, mirroring the popup
			# list rows (_ListBoxNew._LocateItem uses GetWidth()-10), so it sits inside the
			# box and clears the left-side arrow.
			self.boxText.SetWindowHorizontalAlignLeft()
			self.boxText.SetHorizontalAlignLeft()
			self.boxText.SetPosition(self.width - 10, textY)
		else:
			self.boxText.SetWindowHorizontalAlignLeft()
			self.boxText.SetHorizontalAlignLeft()
			self.boxText.SetPosition(10, textY)

	def __RefreshPopupLayout(self):
		count = self.listBox.GetItemCount()
		rows = min(count, self.VISIBLE_ROWS)
		if rows < 1:
			rows = 1
		listH = rows * self.listBox.stepSize
		popupW = self.width
		self.listBox.SetSize(popupW - 16, listH)
		self.listBox.SetBasePos(0)

		popupH = listH + 8
		self.popup.SetSize(popupW, popupH)
		self.__SizeBorderedBar(self.popupOuter, self.popupInner, popupW, popupH)

		if count > self.VISIBLE_ROWS:
			self.scrollBar.SetScrollBarSize(listH)
			self.scrollBar.SetMiddleBarSize(float(self.VISIBLE_ROWS) / float(count))
			self.scrollBar.SetPosition(popupW - 11, 4)
			self.scrollBar.SetPos(0)
			self.scrollBar.Show()
		else:
			self.scrollBar.Hide()

	# ---- state --------------------------------------------------------------
	def Enable(self):
		self.enable = True
		self.__ApplyBoxColors()

	def Disable(self):
		self.enable = False
		self.textCenter = False
		self.boxText.SetText("")
		self.CloseListBox()
		self.__ApplyBoxColors()

	def __ApplyBoxColors(self):
		if not self.enable:
			self.boxInner.SetColor(self.DISABLE_FILL)
			self.boxText.SetPackedFontColor(self.DISABLE_TEXT)
		elif self.isOver:
			self.boxInner.SetColor(self.HOVER_FILL)
			self.boxText.SetPackedFontColor(self.TEXT_COLOR)
		else:
			self.boxInner.SetColor(self.BOX_FILL)
			self.boxText.SetPackedFontColor(self.TEXT_COLOR)

	def SetEvent(self, event):
		self.event = event
		self.bIsShopSearch = False

	def SetEventNew(self, event):
		self.event = event
		self.bIsShopSearch = True

	# ---- items --------------------------------------------------------------
	def ClearItem(self):
		self.CloseListBox()
		self.listBox.ClearItem()
		self.__RefreshPopupLayout()

	def InsertItem(self, index, name):
		self.listBox.InsertItem(index, name)
		self.__RefreshPopupLayout()

	def InsertItem2(self, index, name):
		self.listBox.InsertItem2(index, name)
		self.__RefreshPopupLayout()

	def SetCurrentItem(self, text):
		self.textCenter = False
		self.boxText.SetText(text)
		self.__LayoutBoxText()

	def SetCurrentItem2(self, text):
		self.textCenter = True
		self.boxText.SetText(text)
		self.__LayoutBoxText()

	def SelectItem(self, key):
		self.listBox.SelectItem(key)

	def OnSelectItem(self, index, name):
		self.CloseListBox()
		if self.bIsShopSearch:
			self.event(self, index, name)
		else:
			self.event(index)

	# ---- open / close -------------------------------------------------------
	def Open(self):
		if self.listBox.GetItemCount() <= 0:
			return
		# SetParent drops the popup's TOP_MOST layer, so the dropped list renders in the
		# combo's place in its parent's child order -- under any sibling built after it.
		self.SetTop()
		self.__RefreshPopupLayout()
		self.popup.SetPosition(0, self.height + 2)
		self.popup.Show()
		self.popup.SetTop()
		self.isListOpened = True

	def CloseListBox(self):
		self.isListOpened = False
		if self.popup:
			self.popup.Hide()

	# ---- scroll -------------------------------------------------------------
	def __OnScroll(self):
		count = self.listBox.GetItemCount()
		if count <= self.VISIBLE_ROWS:
			return
		maxBase = count - self.VISIBLE_ROWS
		base = int(round(self.scrollBar.GetPos() * maxBase))
		base = max(0, min(base, maxBase))
		self.listBox.SetBasePos(base)

	def __OnWheel(self, nLen):
		if not self.isListOpened:
			return False
		if nLen > 0:
			self.scrollBar.OnUp()
		elif nLen < 0:
			self.scrollBar.OnDown()
		return True

	# ---- input --------------------------------------------------------------
	def OnMouseLeftButtonDown(self):
		return

	def OnMouseLeftButtonUp(self):
		if not self.enable:
			return
		if self.isListOpened:
			self.CloseListBox()
		else:
			self.Open()

	def OnUpdate(self):
		if not self.enable:
			return
		over = self.IsIn()
		if over != self.isOver:
			self.isOver = over
			self.__ApplyBoxColors()

###################################################################################################
## Python Script Loader
###################################################################################################

class ScriptWindow(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.Children = []
		self.ElementDictionary = {}
	def __del__(self):
		Window.__del__(self)

	def ClearDictionary(self):
		self.Children = []
		self.ElementDictionary = {}
	def InsertChild(self, name, child):
		self.ElementDictionary[name] = child

	def IsChild(self, name):
		return self.ElementDictionary.has_key(name)

	def GetChild(self, name):
		return self.ElementDictionary[name]

	def GetChild2(self, name):
		return self.ElementDictionary.get(name, None)


class PythonScriptLoader(object):

	BODY_KEY_LIST = ( "x", "y", "width", "height" )

	#####

	DEFAULT_KEY_LIST = ( "type", "x", "y", )
	WINDOW_KEY_LIST = ( "width", "height", )
	IMAGE_KEY_LIST = ( "image", )
	IMAGEOLD_KEY_LIST = ("image_old",)
	EXPANDED_IMAGE_KEY_LIST = ( "image", )
	ANI_IMAGE_KEY_LIST = ( "images", )
	SLOT_KEY_LIST = ( "width", "height", "slot", )
	CANDIDATE_LIST_KEY_LIST = ( "item_step", "item_xsize", "item_ysize", )
	GRID_TABLE_KEY_LIST = ( "start_index", "x_count", "y_count", "x_step", "y_step", )
	EDIT_LINE_KEY_LIST = ( "width", "height", "input_limit", )
	COMBO_BOX_KEY_LIST = ( "width", "height", "item", )
	TITLE_BAR_KEY_LIST = ( "width", )
	HORIZONTAL_BAR_KEY_LIST = ( "width", )
	BOARD_KEY_LIST = ( "width", "height", )
	BOARD_WITH_TITLEBAR_KEY_LIST = ( "width", "height", "title", )
	BOX_KEY_LIST = ( "width", "height", )
	BAR_KEY_LIST = ( "width", "height", )
	LINE_KEY_LIST = ( "width", "height", )
	SLOTBAR_KEY_LIST = ( "width", "height", )
	GAUGE_KEY_LIST = ( "width", "color", )
	SCROLLBAR_KEY_LIST = ( "size", )
	LIST_BOX_KEY_LIST = ( "width", "height", )
	RENDER_TARGET_KEY_LIST = ( "index", )
	OUTLINE_WINDOW_KEY_LIST = ( "width", "height", )
	# app.ENABLE_MONSTER_CARD or app.ENABLE_MYSHOP_DECO or app.ENABLE_MINI_GAME_YUTNORI

	if app.ENABLE_QUEST_RENEWAL:
		SUB_TITLE_BAR_KEY_LIST = ( "width", )
		LIST_BAR_KEY_LIST = ( "width", )

	if app.ENABLE_MAILBOX:
		RENDER_BOX_KEY_LIST = ( "color", )

	if app.USE_BL_FISH_EVENT:
		SP_GRID_TABLE_KEY_LIST = ( "start_index", "x_count", "y_count", "x_step", "y_step", )

	def __init__(self):
		self.Clear()

	def Clear(self):
		self.ScriptDictionary = { "SCREEN_WIDTH" : wndMgr.GetScreenWidth(), "SCREEN_HEIGHT" : wndMgr.GetScreenHeight() }
		self.InsertFunction = 0
		if app.ENABLE_WINDOW_RESIZE:
			self.ScriptDictionary["SCREEN_WIDTH"] = Expr("SCREEN_WIDTH")
			self.ScriptDictionary["SCREEN_HEIGHT"] = Expr("SCREEN_HEIGHT")
			self.ScriptDictionary["int"] = SandboxInt
			self.ScriptDictionary["float"] = SandboxFloat

	def LoadScriptFile(self, window, FileName):
		import os
		import exception
		self.Clear()
		
		print "===== Load Script File : %s" % (FileName)
		
		from utils import Sandbox
		sandbox = Sandbox(True, ["uiscriptlocale", "localeinfo", "sys", "item", "utils", "app", "player"])

		import app
		import chr

		if app.ENABLE_WINDOW_RESIZE:
			self.ScriptDictionary["SCREEN_WIDTH"] = Expr("SCREEN_WIDTH")
			self.ScriptDictionary["SCREEN_HEIGHT"] = Expr("SCREEN_HEIGHT")
		else:
			self.ScriptDictionary["SCREEN_WIDTH"] = wndMgr.GetScreenWidth()
			self.ScriptDictionary["SCREEN_HEIGHT"] = wndMgr.GetScreenHeight()
		self.ScriptDictionary["SPECIAL_ACTION_START_INDEX"] = app.SPECIAL_ACTION_START_INDEX
		self.ScriptDictionary["WJ_SHOW_MOB_INFO"] = app.WJ_SHOW_MOB_INFO
		self.ScriptDictionary["ENABLE_EXTEND_INVEN_SYSTEM"] = app.ENABLE_EXTEND_INVEN_SYSTEM
		self.ScriptDictionary["ENABLE_CHEQUE_SYSTEM"] = app.ENABLE_CHEQUE_SYSTEM
		self.ScriptDictionary["ENABLE_SORT_INVENTORY"] = app.ENABLE_SORT_INVENTORY
		self.ScriptDictionary["ENABLE_PASSIVE_ATTR"] = 0
		self.ScriptDictionary["ENABLE_OSF_MINIMAP_INFO"] = app.ENABLE_OSF_MINIMAP_INFO
		self.ScriptDictionary["ENABLE_RTT_STATISTICS"] = app.ENABLE_RTT_STATISTICS
		self.ScriptDictionary["ENABLE_MAILBOX"] = app.ENABLE_MAILBOX
		self.ScriptDictionary["CHEQUE_INPUT_LIMIT"] = app.CHEQUE_INPUT_LIMIT
		self.ScriptDictionary["ENABLE_MONSTER_CARD_ACHIEV"] = 0
		self.ScriptDictionary["ENABLE_WOLFMAN_CHARACTER"] = app.ENABLE_WOLFMAN_CHARACTER
		self.ScriptDictionary["ENABLE_BOSS_DUNGEON"] = 0
		self.ScriptDictionary["ENABLE_UI_EDITLINE_CHECK_WIDTH"] = 0
		self.ScriptDictionary["ENABLE_SHOPEX_TAB4"] = app.ENABLE_SHOPEX_TAB4
		self.ScriptDictionary["ENABLE_SHADOW_RENDER_QUALITY_OPTION"] = app.ENABLE_SHADOW_RENDER_QUALITY_OPTION
		self.ScriptDictionary["ENABLE_FOV_OPTION"] = app.ENABLE_FOV_OPTION
		self.ScriptDictionary["USE_BACKGROUND_FPS_CAP"] = app.USE_BACKGROUND_FPS_CAP
		self.ScriptDictionary["ENABLE_FPS"] = app.ENABLE_FPS
		self.ScriptDictionary["PLAYER_PER_ACCOUNT"] = app.PLAYER_PER_ACCOUNT
		self.ScriptDictionary["ENABLE_QUEST_RENEWAL"] = app.ENABLE_QUEST_RENEWAL
		self.ScriptDictionary["ENABLE_DS_REFINE_ALL"] = app.ENABLE_DS_REFINE_ALL
		self.ScriptDictionary["ENABLE_DS_GRADE_MYTH"] = app.ENABLE_DS_GRADE_MYTH
		self.ScriptDictionary["ENABLE_SERVER_SELECT_RENEWAL"] = app.ENABLE_SERVER_SELECT_RENEWAL
		self.ScriptDictionary["USE_GLOVE_SYSTEM"] = app.USE_GLOVE_SYSTEM
		self.ScriptDictionary["ENABLE_GUILD_PVE"] = 1
		self.ScriptDictionary["ENABLE_CONQUEROR_LEVEL"] = app.ENABLE_CONQUEROR_LEVEL
		self.ScriptDictionary["ENABLE_SPECIAL_INVENTORY_SYSTEM"] = app.ENABLE_SPECIAL_INVENTORY_SYSTEM
		self.ScriptDictionary["ENABLE_DAILY_GIFT_SYSTEM"] = 0
		self.ScriptDictionary["PLAYER_NAME_MAX_LEN"] = chr.PLAYER_NAME_MAX_LEN
		self.ScriptDictionary["DRAGON_SOUL_EQUIPMENT_SLOT_START"] = player.DRAGON_SOUL_EQUIPMENT_SLOT_START
		self.ScriptDictionary["BELT_INVENTORY_SLOT_START"] = item.BELT_INVENTORY_SLOT_START
		self.ScriptDictionary["COSTUME_START_INDEX"] = item.COSTUME_SLOT_START
		self.ScriptDictionary["SHINING_START_INDEX"] = item.SHINING_SLOT_START
		self.ScriptDictionary["COSTUME_SLOT_WEAPON"] = item.COSTUME_SLOT_WEAPON
		self.ScriptDictionary["EQUIPMENT_RING1"] = item.EQUIPMENT_RING1
		self.ScriptDictionary["EQUIPMENT_RING2"] = item.EQUIPMENT_RING2
		self.ScriptDictionary["EQUIPMENT_BELT"] = item.EQUIPMENT_BELT
		self.ScriptDictionary["PENDANT_FIRE_SLOT"] = item.PENDANT_FIRE_SLOT
		self.ScriptDictionary["PENDANT_ICE_SLOT"] = item.PENDANT_ICE_SLOT
		self.ScriptDictionary["PENDANT_THUNDER_SLOT"] = item.PENDANT_THUNDER_SLOT
		self.ScriptDictionary["PENDANT_WIND_SLOT"] = item.PENDANT_WIND_SLOT
		self.ScriptDictionary["PENDANT_DARK_SLOT"] = item.PENDANT_DARK_SLOT
		self.ScriptDictionary["PENDANT_EARTH_SLOT"] = item.PENDANT_EARTH_SLOT
		self.ScriptDictionary["PENDANT_FIRST_SOUL_SLOT"] = item.PENDANT_FIRST_SOUL_SLOT
		self.ScriptDictionary["PENDANT_SECOND_SOUL_SLOT"] = item.PENDANT_SECOND_SOUL_SLOT
		self.ScriptDictionary["EQUIPMENT_GLOVE"] = item.EQUIPMENT_GLOVE
		self.ScriptDictionary["FAST_EQUIP_WORLDARD"] = app.FAST_EQUIP_WORLDARD
		self.ScriptDictionary["ENABLE_KEYCHANGE_SYSTEM"] = app.ENABLE_KEYCHANGE_SYSTEM
		self.ScriptDictionary["ENABLE_GROWTH_PET_SYSTEM"] = app.ENABLE_GROWTH_PET_SYSTEM
		self.ScriptDictionary["ENABLE_SWITCHBOT"] = app.ENABLE_SWITCHBOT
		self.ScriptDictionary["ENABLE_INGAME_WIKI"] = app.ENABLE_INGAME_WIKI
		self.ScriptDictionary["ENABLE_ULTIMATE_REGEN"] = app.ENABLE_ULTIMATE_REGEN
		self.ScriptDictionary["ENABLE_CHATTING_WINDOW_RENEWAL"] = app.ENABLE_CHATTING_WINDOW_RENEWAL
		self.ScriptDictionary["LOCALE_PATH"] = app.GetLocalePath()
		self.ScriptDictionary["__GetCurrentTime"] = app.GetCurrentTime()
		self.ScriptDictionary["__GetTimeZone"] = app.GetTimeZone()
		self.ScriptDictionary["__GetPatch"] = app.GetPatch()
		self.ScriptDictionary["__VERSION"] = app.VERSION
		self.ScriptDictionary["AUTO_HUNT_RUBINUM"] = app.AUTO_HUNT_RUBINUM
		self.ScriptDictionary["USE_AUTO_SPLIT_ITEMS"] = app.USE_AUTO_SPLIT_ITEMS

		if app.FAST_EQUIP_WORLDARD:
			self.ScriptDictionary["CHANGE_EQUIP_START_INDEX"] = player.CHANGE_EQUIP_SLOT_START

		if app.ENABLE_FEATURES_OXEVENT:
			self.ScriptDictionary["COLOR_BACKGROUND_OXEVENT"] = grp.GenerateColor(0.0, 0.0, 0.0, 0.4)

		self.ScriptDictionary["AUTO_HIDE_LOW_LEVELS_DUNGEONS"] = app.AUTO_HIDE_LOW_LEVELS_DUNGEONS
		self.ScriptDictionary["ENABLE_GEM_SYSTEM"] = app.ENABLE_GEM_SYSTEM

		if USE_CYTHON:
			from os.path import splitext as op_splitext, basename as op_basename, dirname as op_dirname
			def GetModName(filename):
				return op_splitext(op_basename(filename))[0]

			def IsInUiPath(filename):
				def ICmp(s1, s2):
					return s1.lower() == s2.lower()

				return ICmp(op_dirname(filename), "uiscript")

			modname = GetModName(FileName)
			import rootlib

			tpl2Main = (
						"SCREEN_WIDTH",
						"SCREEN_HEIGHT",
						"SPECIAL_ACTION_START_INDEX",
						"WJ_SHOW_MOB_INFO",
						"ENABLE_EXTEND_INVEN_SYSTEM",
						"ENABLE_SORT_INVENTORY",
						"ENABLE_PASSIVE_ATTR",
						"ENABLE_OSF_MINIMAP_INFO",
						"ENABLE_RTT_STATISTICS",
						"ENABLE_MAILBOX",
						"CHEQUE_INPUT_LIMIT",
						"ENABLE_MONSTER_CARD_ACHIEV",
						"ENABLE_WOLFMAN_CHARACTER",
						"ENABLE_BOSS_DUNGEON",
						"ENABLE_UI_EDITLINE_CHECK_WIDTH",
						"ENABLE_SHOPEX_TAB4",
						"ENABLE_SHADOW_RENDER_QUALITY_OPTION",
						"ENABLE_FOV_OPTION",
						"USE_BACKGROUND_FPS_CAP",
						"ENABLE_FPS",
						"PLAYER_PER_ACCOUNT",
						"ENABLE_QUEST_RENEWAL",
						"ENABLE_DS_REFINE_ALL",
						"ENABLE_DS_GRADE_MYTH",
						"ENABLE_SERVER_SELECT_RENEWAL",
						"USE_GLOVE_SYSTEM",
						"ENABLE_GUILD_PVE",
						"ENABLE_CONQUEROR_LEVEL",
						"ENABLE_SPECIAL_INVENTORY_SYSTEM",
						"ENABLE_DAILY_GIFT_SYSTEM",
						"PLAYER_NAME_MAX_LEN",
						"DRAGON_SOUL_EQUIPMENT_SLOT_START",
						"BELT_INVENTORY_SLOT_START",
						"COSTUME_START_INDEX",
						"SHINING_START_INDEX",
						"COSTUME_SLOT_WEAPON",
						"EQUIPMENT_RING1",
						"EQUIPMENT_RING2",
						"EQUIPMENT_BELT",
						"PENDANT_FIRE_SLOT",
						"PENDANT_ICE_SLOT",
						"PENDANT_THUNDER_SLOT",
						"PENDANT_WIND_SLOT",
						"PENDANT_DARK_SLOT",
						"PENDANT_EARTH_SLOT",
						"PENDANT_FIRST_SOUL_SLOT",
						"PENDANT_SECOND_SOUL_SLOT",
						"EQUIPMENT_GLOVE",
						"ENABLE_KEYCHANGE_SYSTEM",
						"ENABLE_GROWTH_PET_SYSTEM",
						"ENABLE_SWITCHBOT",
						"ENABLE_INGAME_WIKI",
						"ENABLE_ULTIMATE_REGEN",
						"ENABLE_CHATTING_WINDOW_RENEWAL",
						"LOCALE_PATH",
						"__GetCurrentTime",
						"__GetTimeZone",
						"__GetPatch",
						"__VERSION",
						"AUTO_HUNT_RUBINUM",
						"AUTO_HIDE_LOW_LEVELS_DUNGEONS",
			)

			if app.FAST_EQUIP_WORLDARD:
				tpl2Main += ("CHANGE_EQUIP_START_INDEX",)

			if app.ENABLE_FEATURES_OXEVENT:
				tpl2Main += ("COLOR_BACKGROUND_OXEVENT",)

			if app.ENABLE_CHEQUE_SYSTEM:
				tpl2Main += ("ENABLE_CHEQUE_SYSTEM",)

			if app.ENABLE_GEM_SYSTEM:
				tpl2Main += ("ENABLE_GEM_SYSTEM",)

			if app.USE_AUTO_SPLIT_ITEMS:
				tpl2Main += ("USE_AUTO_SPLIT_ITEMS",)

			import __builtin__ as bt
			for idx in tpl2Main:
				tmpVal = self.ScriptDictionary[idx]
				exec "bt.%s = tmpVal" % idx in globals(), locals()

		try:
			if USE_CYTHON and IsInUiPath(FileName) and rootlib.isExist(modname):
				m1 = rootlib.moduleImport(modname)
				self.ScriptDictionary["window"] = m1.window.copy()

				del m1
			else:
				sandbox.execfile(FileName, self.ScriptDictionary)
		except IOError, err:
			import sys
			import dbg
			dbg.TraceError("Failed to load script file : %s" % (FileName))
			dbg.TraceError("error  : %s" % (err))
			exception.Abort("LoadScriptFile1")
		except RuntimeError, err:
			import sys
			import dbg
			dbg.TraceError("Failed to load script file : %s" % (FileName))
			dbg.TraceError("error  : %s" % (err))
			exception.Abort("LoadScriptFile2")
		except:
			import sys
			import dbg
			dbg.TraceError("Failed to load script file : %s" % (FileName))
			exception.Abort("LoadScriptFile!!!!!!!!!!!!!!")
		
		Body = self.ScriptDictionary["window"]
		self.CheckKeyList("window", Body, self.BODY_KEY_LIST)
		
		window.ClearDictionary()
		self.InsertFunction = window.InsertChild
		window.SetPosition(int(Body["x"]), int(Body["y"]))
		
		if localeinfo.IsARABIC():
			w = wndMgr.GetScreenWidth()
			h = wndMgr.GetScreenHeight()
			
			if Body.has_key("width"):
				w = int(Body["width"])
			
			if Body.has_key("height"):
				h = int(Body["height"])
			
			window.SetSize(w, h)
		else:
			window.SetSize(int(Body["width"]), int(Body["height"]))
			if True == Body.has_key("style"):
				for StyleList in Body["style"]:
					window.AddFlag(StyleList)
		
		if app.ENABLE_WINDOW_RESIZE:
			window.SetResizeDic(ExtractWindowScaling(Body))
		self.LoadChildren(window, Body)

	def LoadChildren(self, parent, dicChildren):

		if localeinfo.IsARABIC():
			parent.AddFlag( "rtl" )

		if True == dicChildren.has_key("style"):
			for style in dicChildren["style"]:
				parent.AddFlag(style)

		if False == dicChildren.has_key("children"):
			return False

		Index = 0

		ChildrenList = dicChildren["children"]
		parent.Children = range(len(ChildrenList))
		for ElementValue in ChildrenList:
			try:
				Name = ElementValue["name"]
			except KeyError:
				Name = ElementValue["name"] = "NONAME"

			try:
				Type = ElementValue["type"]
			except KeyError:
				Type = ElementValue["type"] = "window"

			if False == self.CheckKeyList(Name, ElementValue, self.DEFAULT_KEY_LIST):
				del parent.Children[Index]
				continue

			if Type == "window":
				parent.Children[Index] = ScriptWindow()
				parent.Children[Index].SetParent(parent)
				self.LoadElementWindow(parent.Children[Index], ElementValue, parent)

			elif Type == "button":
				parent.Children[Index] = Button()
				parent.Children[Index].SetParent(parent)
				self.LoadElementButton(parent.Children[Index], ElementValue, parent)
			elif app.ENABLE_BIOLOG_SYSTEM and Type == "checkbox_biolog":
				parent.Children[Index] = CheckBox_Biolog()
				parent.Children[Index].SetParent(parent)
				self.LoadElementCheckBox(parent.Children[Index], ElementValue, parent)
			elif app.ENABLE_BIOLOG_SYSTEM and Type == "boxed_board":
				parent.Children[Index] = BoxedBoard()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoxedBoard(parent.Children[Index], ElementValue, parent)
			elif Type == "radio_button":
				parent.Children[Index] = RadioButton()
				parent.Children[Index].SetParent(parent)
				self.LoadElementButton(parent.Children[Index], ElementValue, parent)

			elif Type == "toggle_button":
				parent.Children[Index] = ToggleButton()
				parent.Children[Index].SetParent(parent)
				self.LoadElementButton(parent.Children[Index], ElementValue, parent)

			elif Type == "mark":
				parent.Children[Index] = MarkBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementMark(parent.Children[Index], ElementValue, parent)

			elif Type == "image":
				parent.Children[Index] = ImageBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementImage(parent.Children[Index], ElementValue, parent)

			elif Type == "image_old":
				parent.Children[Index] = ImageBoxOld()
				parent.Children[Index].SetParent(parent)
				self.LoadElementImageOld(parent.Children[Index], ElementValue, parent)

			elif Type == "expanded_image":
				parent.Children[Index] = ExpandedImageBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementExpandedImage(parent.Children[Index], ElementValue, parent)

			elif Type == "ani_image":
				parent.Children[Index] = AniImageBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementAniImage(parent.Children[Index], ElementValue, parent)

			elif Type == "slot":
				parent.Children[Index] = SlotWindow()
				parent.Children[Index].SetParent(parent)
				self.LoadElementSlot(parent.Children[Index], ElementValue, parent)

			elif Type == "candidate_list":
				parent.Children[Index] = CandidateListBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementCandidateList(parent.Children[Index], ElementValue, parent)

			elif Type == "grid_table":
				parent.Children[Index] = GridSlotWindow()
				parent.Children[Index].SetParent(parent)
				self.LoadElementGridTable(parent.Children[Index], ElementValue, parent)

			elif Type == "text":
				parent.Children[Index] = TextLine()
				parent.Children[Index].SetParent(parent)
				self.LoadElementText(parent.Children[Index], ElementValue, parent)
			elif Type == "movable_text":
				parent.Children[Index] = MoveTextLine()
				parent.Children[Index].SetParent(parent)
				self.LoadElementMovableText(parent.Children[Index], ElementValue, parent)
			elif Type == "extended_text":
				parent.Children[Index] = ExtendedTextLine()
				parent.Children[Index].SetParent(parent)
				self.LoadElementExtendedText(parent.Children[Index], ElementValue, parent)

			elif Type == "editline":
				parent.Children[Index] = EditLine()
				parent.Children[Index].SetParent(parent)
				self.LoadElementEditLine(parent.Children[Index], ElementValue, parent)

			elif Type == "cool_text" and app.__COOL_REFRESH_EDITLINE__:
				parent.Children[Index] = CoolRefreshTextLine()
				parent.Children[Index].SetParent(parent)
				self.LoadElementText(parent.Children[Index], ElementValue, parent)


			elif Type == "titlebar":
				parent.Children[Index] = TitleBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementTitleBar(parent.Children[Index], ElementValue, parent)

			elif Type == "sibtitlebar":
				parent.Children[Index] = SibTitleBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementTitleBar(parent.Children[Index], ElementValue, parent)


			elif Type == "titlebar_without_button":
				parent.Children[Index] = TitleBarWithoutButton()
				parent.Children[Index].SetParent(parent)
				self.LoadElementTitleBar(parent.Children[Index], ElementValue, parent)

			elif Type == "horizontalbar":
				parent.Children[Index] = HorizontalBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementHorizontalBar(parent.Children[Index], ElementValue, parent)

			elif Type == "sibbar":
				parent.Children[Index] = SibBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementHorizontalBar(parent.Children[Index], ElementValue, parent)


			elif Type == "board":
				parent.Children[Index] = Board()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "sibboard":
				parent.Children[Index] = SibBoard()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "board_dragon":
				parent.Children[Index] = BoardDragon()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "invisibleboard":
				parent.Children[Index] = InvisibleBoard()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "board_with_titlebar":
				parent.Children[Index] = BoardWithTitleBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoardWithTitleBar(parent.Children[Index], ElementValue, parent)
			elif Type == "border_a":
				parent.Children[Index] = BorderA()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBorderA(parent.Children[Index], ElementValue, parent)
			elif Type == "board_with_titlebar_without_button":
				parent.Children[Index] = BoardWithTitleBar(True)
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoardWithTitleBar(parent.Children[Index], ElementValue, parent)

			elif Type == "new_board":
				parent.Children[Index] = NewBoard()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "new_board_with_titlebar":
				parent.Children[Index] = NewBoardWithTitleBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoardWithTitleBar(parent.Children[Index], ElementValue, parent)

			elif Type == "thinboard":
				parent.Children[Index] = ThinBoard()
				parent.Children[Index].SetParent(parent)
				self.LoadElementThinBoard(parent.Children[Index], ElementValue, parent)
			elif (app.USE_DUNGEON_INFO or app.USE_LOG_EXCHANGE) and Type == "v2_thinboard":
				parent.Children[Index] = ThinBoard("UI", 2)
				parent.Children[Index].SetParent(parent)
				self.LoadElementThinBoard(parent.Children[Index], ElementValue, parent)
			elif (app.USE_DUNGEON_INFO or app.USE_LOG_EXCHANGE) and Type == "v3_thinboard":
				parent.Children[Index] = ThinBoard("UI", 3)
				parent.Children[Index].SetParent(parent)
				self.LoadElementThinBoard(parent.Children[Index], ElementValue, parent)
			elif Type == "thinboard_gold":
				parent.Children[Index] = ThinBoardGold()
				parent.Children[Index].SetParent(parent)
				self.LoadElementThinBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "thinboard_circle":
				parent.Children[Index] = ThinBoardCircle()
				parent.Children[Index].SetParent(parent)
				self.LoadElementThinBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "box":
				parent.Children[Index] = Box()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBox(parent.Children[Index], ElementValue, parent)

			elif Type == "bar":
				parent.Children[Index] = Bar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBar(parent.Children[Index], ElementValue, parent)

			elif Type == "line":
				parent.Children[Index] = Line()
				parent.Children[Index].SetParent(parent)
				self.LoadElementLine(parent.Children[Index], ElementValue, parent)

			elif Type == "slotbar":
				parent.Children[Index] = SlotBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementSlotBar(parent.Children[Index], ElementValue, parent)

			elif Type == "gauge":
				parent.Children[Index] = Gauge()
				parent.Children[Index].SetParent(parent)
				self.LoadElementGauge(parent.Children[Index], ElementValue, parent)

			elif Type == "scrollbar":
				parent.Children[Index] = ScrollBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementScrollBar(parent.Children[Index], ElementValue, parent)
			elif Type == "scrollbarnew":
				parent.Children[Index] = ScrollBarNew()
				parent.Children[Index].SetParent(parent)
				self.LoadElementScrollBar(parent.Children[Index], ElementValue, parent)
			elif Type == "new_scrollbar":
				parent.Children[Index] = NewScrollBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementScrollBar(parent.Children[Index], ElementValue, parent)

			elif Type == "thin_scrollbar":
				parent.Children[Index] = ThinScrollBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementScrollBar(parent.Children[Index], ElementValue, parent)

			elif Type == "small_thin_scrollbar":
				parent.Children[Index] = SmallThinScrollBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementScrollBar(parent.Children[Index], ElementValue, parent)

			elif Type == "sliderbar":
				parent.Children[Index] = SliderBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementSliderBar(parent.Children[Index], ElementValue, parent)

			elif Type == "sliderbar_advancedgameoptions":
				parent.Children[Index] = SliderBar_AdvancedGameOptions()
				parent.Children[Index].SetParent(parent)
				self.LoadElementSliderBar(parent.Children[Index], ElementValue, parent)

			elif Type == "listbox":
				parent.Children[Index] = ListBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementListBox(parent.Children[Index], ElementValue, parent)

			elif Type == "listbox_new":
				parent.Children[Index] = ListBoxNew()
				parent.Children[Index].SetParent(parent)
				self.LoadElementListBox(parent.Children[Index], ElementValue, parent)
			elif app.ENABLE_ULTIMATE_REGEN and\
				Type == "listbox_new2":
				parent.Children[Index] = ListBoxNew2()
				parent.Children[Index].SetParent(parent)
				self.LoadElementListBox(parent.Children[Index], ElementValue, parent)
			elif Type == "listbox2":
				parent.Children[Index] = ListBox2()
				parent.Children[Index].SetParent(parent)
				self.LoadElementListBox2(parent.Children[Index], ElementValue, parent)

			elif Type == "listboxex":
				parent.Children[Index] = ListBoxEx()
				parent.Children[Index].SetParent(parent)
				self.LoadElementListBoxEx(parent.Children[Index], ElementValue, parent)
			elif Type == "outline_window":
				parent.Children[Index] = OutlineWindow()
				parent.Children[Index].SetParent(parent)
				self.LoadOutlineWindow(parent.Children[Index], ElementValue, parent)
			elif Type == "numberline": # ENABLE_12ZI
				parent.Children[Index] = NumberLine()
				parent.Children[Index].SetParent(parent)
				self.LoadElementNumberLine(parent.Children[Index], ElementValue, parent)

			# app.ENABLE_MONSTER_CARD or app.ENABLE_MYSHOP_DECO or app.ENABLE_MINI_GAME_YUTNORI
			elif Type == "render_target":	
				parent.Children[Index] = RenderTarget()
				parent.Children[Index].SetParent(parent)
				self.LoadElementRenderTarget(parent.Children[Index], ElementValue, parent)

			elif Type == "middleboard" and app.ENABLE_LOADING_TIP:
				parent.Children[Index] = ThinBoard()
				parent.Children[Index].SetParent(parent)
				self.LoadElementThinBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "subtitlebar" and app.ENABLE_QUEST_RENEWAL:
				parent.Children[Index] = SubTitleBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementSubTitleBar(parent.Children[Index], ElementValue, parent)

			elif Type == "listbar" and app.ENABLE_QUEST_RENEWAL:
				parent.Children[Index] = ListBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementListBar(parent.Children[Index], ElementValue, parent)

			elif Type == "renderbox":
				parent.Children[Index] = RenderBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementRenderBox(parent.Children[Index], ElementValue, parent)
			elif app.USE_BL_FISH_EVENT and Type == "fish_event_grid_table":
				parent.Children[Index] = FishEventGridSlotWindow()
				parent.Children[Index].SetParent(parent)
				self.LoadElementSpecialGridTable(parent.Children[Index], ElementValue, parent)
			else:
				Index += 1
				continue

			parent.Children[Index].SetWindowName(Name)
			if app.ENABLE_WINDOW_RESIZE:
				parent.Children[Index].SetResizeDic(ExtractWindowScaling(ElementValue))
			if 0 != self.InsertFunction:
				self.InsertFunction(Name, parent.Children[Index])

			self.LoadChildren(parent.Children[Index], ElementValue)
			Index += 1

	def CheckKeyList(self, name, value, key_list):

		for DataKey in key_list:
			if False == value.has_key(DataKey):
				print "Failed to find data key", "[" + name + "/" + DataKey + "]"
				return False

		return True

	def LoadDefaultData(self, window, value, parentWindow):
		loc_x = int(value["x"])
		loc_y = int(value["y"])
		if value.has_key("vertical_align"):
			if "center" == value["vertical_align"]:
				window.SetWindowVerticalAlignCenter()
			elif "bottom" == value["vertical_align"]:
				window.SetWindowVerticalAlignBottom()

		if parentWindow.IsRTL():
			loc_x = int(value["x"]) + window.GetWidth()
			if value.has_key("horizontal_align"):
				if "center" == value["horizontal_align"]:
					window.SetWindowHorizontalAlignCenter()
					loc_x = - int(value["x"])
				elif "right" == value["horizontal_align"]:
					window.SetWindowHorizontalAlignLeft()
					loc_x = int(value["x"]) - window.GetWidth()
					## loc_x = parentWindow.GetWidth() - int(value["x"]) + window.GetWidth()
			else:
				window.SetWindowHorizontalAlignRight()

			if value.has_key("all_align"):
				window.SetWindowVerticalAlignCenter()
				window.SetWindowHorizontalAlignCenter()
				loc_x = - int(value["x"])
		else:
			if value.has_key("horizontal_align"):
				if "center" == value["horizontal_align"]:
					window.SetWindowHorizontalAlignCenter()
				elif "right" == value["horizontal_align"]:
					window.SetWindowHorizontalAlignRight()

		window.SetPosition(loc_x, loc_y)
		window.Show()

	## Window
	def LoadElementWindow(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.WINDOW_KEY_LIST):
			return False

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Button
	def LoadElementButton(self, window, value, parentWindow):
		if value.has_key("width") and value.has_key("height"):
			window.SetSize(int(value["width"]), int(value["height"]))

		if True == value.has_key("default_image"):
			window.SetUpVisual(value["default_image"])
		if True == value.has_key("over_image"):
			window.SetOverVisual(value["over_image"])
		if True == value.has_key("down_image"):
			window.SetDownVisual(value["down_image"])
		if True == value.has_key("disable_image"):
			window.SetDisableVisual(value["disable_image"])

		if True == value.has_key("text"):
			if True == value.has_key("fontsize"):
				fontSize = value["fontsize"]

				if "LARGE" == fontSize:
					window.AppendTextLine(value["text"], localeinfo.UI_DEF_FONT_LARGE)
				elif "SMALL" == fontSize:
					window.AppendTextLine(value["text"], localeinfo.UI_DEF_FONT_SMALL)
				else:
					window.AppendTextLine(value["text"])
			else:
				if True == value.has_key("text_height"):
					window.SetText(value["text"], value["text_height"])
				elif TRUE == value.has_key("text_x") and app.ENABLE_GAMEOPTION_RENEWAL:
					window.SetListText(value["text"], value["text_x"])
				else:
					window.SetText(value["text"])

			if value.has_key("text_color"):
				window.SetTextColor(value["text_color"])

			if value.has_key("text_outline"):
				if value["text_outline"]:
					window.SetOutline()
					
		if True == value.has_key("tooltip_text"):
			if True == value.has_key("tooltip_x") and True == value.has_key("tooltip_y"):
				window.SetToolTipText(value["tooltip_text"], int(value["tooltip_x"]), int(value["tooltip_y"]))
			else:
				window.SetToolTipText(value["tooltip_text"])

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Mark
	def LoadElementMark(self, window, value, parentWindow):

		#if False == self.CheckKeyList(value["name"], value, self.MARK_KEY_LIST):
		#	return False

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Image
	def LoadElementImage(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.IMAGE_KEY_LIST):
			return False

		window.LoadImage(value["image"])

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## ImageOld
	def LoadElementImageOld(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.IMAGEOLD_KEY_LIST):
			return False

		window.LoadImage(value["image_old"])

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## AniImage
	def LoadElementAniImage(self, window, value, parentWindow):
		if False == self.CheckKeyList(value["name"], value, self.ANI_IMAGE_KEY_LIST):
			return False

		if True == value.has_key("delay"):
			window.SetDelay(value["delay"])

		if app.ENABLE_IMAGE_SCALE:
			if True == value.has_key("x_scale") and True == value.has_key("y_scale"):
				for image in value["images"]:
					window.AppendImageScale(image, float(value["x_scale"]), float(value["y_scale"]))
			else:
				for image in value["images"]:
					window.AppendImage(image)
		else:
			for image in value["images"]:
				window.AppendImage(image)

		if value.has_key("width") and value.has_key("height"):
			window.SetSize(value["width"], value["height"])

		if True == value.has_key("x_scale") and True == value.has_key("y_scale"):
			window.SetScale(float(value["x_scale"]), float(value["y_scale"]))

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Expanded Image
	def LoadElementExpandedImage(self, window, value, parentWindow):
		if False == self.CheckKeyList(value["name"], value, self.EXPANDED_IMAGE_KEY_LIST):
			return False

		window.LoadImage(value["image"])

		if True == value.has_key("x_origin") and True == value.has_key("y_origin"):
			window.SetOrigin(float(value["x_origin"]), float(value["y_origin"]))

		if True == value.has_key("x_scale") and True == value.has_key("y_scale"):
			window.SetScale(float(value["x_scale"]), float(value["y_scale"]))

		if True == value.has_key("rect"):
			RenderingRect = value["rect"]
			window.SetRenderingRect(RenderingRect[0], RenderingRect[1], RenderingRect[2], RenderingRect[3])

		if True == value.has_key("mode"):
			mode = value["mode"]
			if "MODULATE" == mode:
				window.SetRenderingMode(wndMgr.RENDERING_MODE_MODULATE)

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Slot
	def LoadElementSlot(self, window, value, parentWindow):
		if False == self.CheckKeyList(value["name"], value, self.SLOT_KEY_LIST):
			return False

		global_x = int(value["x"])
		global_y = int(value["y"])
		global_width = int(value["width"])
		global_height = int(value["height"])

		window.SetPosition(global_x, global_y)
		window.SetSize(global_width, global_height)
		window.Show()

		r = 1.0
		g = 1.0
		b = 1.0
		a = 1.0

		if True == value.has_key("image_r") and \
			True == value.has_key("image_g") and \
			True == value.has_key("image_b") and \
			True == value.has_key("image_a"):
			r = float(value["image_r"])
			g = float(value["image_g"])
			b = float(value["image_b"])
			a = float(value["image_a"])

		SLOT_ONE_KEY_LIST = ("index", "x", "y", "width", "height")

		for slot in value["slot"]:
			if True == self.CheckKeyList(value["name"] + " - one", slot, SLOT_ONE_KEY_LIST):
				wndMgr.AppendSlot(window.hWnd,
									int(slot["index"]),
									int(slot["x"]),
									int(slot["y"]),
									int(slot["width"]),
									int(slot["height"]))

		if True == value.has_key("x_scale") and True == value.has_key("y_scale"):
			window.SetSlotScale(float(value["x_scale"]), float(value["y_scale"]))

		if True == value.has_key("image"):
			if app.ENABLE_IMAGE_SCALE:
				if True == value.has_key("x_scale") and TRUE == value.has_key("y_scale"):
					wndMgr.SetSlotBaseImageScale(window.hWnd,
											value["image"],
											r, g, b, a, float(value["x_scale"]), float(value["y_scale"]))
				else:
					wndMgr.SetSlotBaseImage(window.hWnd,
											value["image"],
											r, g, b, a)
			else:
				wndMgr.SetSlotBaseImage(window.hWnd,
										value["image"],
										r, g, b, a)

		return True

	def LoadElementCandidateList(self, window, value, parentWindow):
		if False == self.CheckKeyList(value["name"], value, self.CANDIDATE_LIST_KEY_LIST):
			return False

		window.SetPosition(int(value["x"]), int(value["y"]))
		window.SetItemSize(int(value["item_xsize"]), int(value["item_ysize"]))
		window.SetItemStep(int(value["item_step"]))
		window.Show()

		return True

	## Table
	def LoadElementGridTable(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.GRID_TABLE_KEY_LIST):
			return False

		xBlank = 0
		yBlank = 0
		if True == value.has_key("x_blank"):
			xBlank = int(value["x_blank"])
		if True == value.has_key("y_blank"):
			yBlank = int(value["y_blank"])

		if localeinfo.IsARABIC():
			pass
		else:
			window.SetPosition(int(value["x"]), int(value["y"]))

		window.ArrangeSlot(	int(value["start_index"]),
							int(value["x_count"]),
							int(value["y_count"]),
							int(value["x_step"]),
							int(value["y_step"]),
							xBlank,
							yBlank)
		if True == value.has_key("image"):
			r = 1.0
			g = 1.0
			b = 1.0
			a = 1.0
			if True == value.has_key("image_r") and \
				True == value.has_key("image_g") and \
				True == value.has_key("image_b") and \
				True == value.has_key("image_a"):
				r = float(value["image_r"])
				g = float(value["image_g"])
				b = float(value["image_b"])
				a = float(value["image_a"])
			wndMgr.SetSlotBaseImage(window.hWnd, value["image"], r, g, b, a)

		if True == value.has_key("style"):
			if "select" == value["style"]:
				wndMgr.SetSlotStyle(window.hWnd, wndMgr.SLOT_STYLE_SELECT)
		if localeinfo.IsARABIC():
			self.LoadDefaultData(window, value, parentWindow)
		else:
			window.Show()

		return True

	## Text
	def LoadElementText(self, window, value, parentWindow):
		if value.has_key("multi_line"):
			if value["multi_line"]:
				window.SetMultiLine()

		if value.has_key("fontsize"):
			fontSize = value["fontsize"]

			if "LARGE" == fontSize:
				window.SetFontName(localeinfo.UI_DEF_FONT_LARGE)

		elif value.has_key("fontname"):
			fontName = value["fontname"]
			window.SetFontName(fontName)

		if value.has_key("text_horizontal_align"):
			if "left" == value["text_horizontal_align"]:
				window.SetHorizontalAlignLeft()
			elif "center" == value["text_horizontal_align"]:
				window.SetHorizontalAlignCenter()
			elif "right" == value["text_horizontal_align"]:
				window.SetHorizontalAlignRight()

		if value.has_key("text_vertical_align"):
			if "top" == value["text_vertical_align"]:
				window.SetVerticalAlignTop()
			elif "center" == value["text_vertical_align"]:
				window.SetVerticalAlignCenter()
			elif "bottom" == value["text_vertical_align"]:
				window.SetVerticalAlignBottom()

		if value.has_key("all_align"):
			window.SetHorizontalAlignCenter()
			window.SetVerticalAlignCenter()
			window.SetWindowHorizontalAlignCenter()
			window.SetWindowVerticalAlignCenter()

		if value.has_key("r") and value.has_key("g") and value.has_key("b"):
			window.SetFontColor(float(value["r"]), float(value["g"]), float(value["b"]))
		elif value.has_key("color"):
			window.SetPackedFontColor(value["color"])
		else:
			window.SetFontColor(0.8549, 0.8549, 0.8549)

		if value.has_key("outline"):
			if value["outline"]:
				window.SetOutline()
		if True == value.has_key("text"):
			window.SetText(value["text"])

		self.LoadDefaultData(window, value, parentWindow)

		return True

	def LoadElementMovableText(self, window, value, parentWindow):
		if value.has_key("multi_line") and value["multi_line"]:
			window.SetMultiLine()

		if value.has_key("fontsize"):
			if value["fontsize"] == "LARGE":
				window.SetFontName(localeinfo.UI_DEF_FONT_LARGE)
		elif value.has_key("fontname"):
			fontName = value["fontname"]
			window.SetFontName(fontName)

		if value.has_key("text_horizontal_align"):
			if "left" == value["text_horizontal_align"]:
				window.SetHorizontalAlignLeft()
			elif "center" == value["text_horizontal_align"]:
				window.SetHorizontalAlignCenter()
			elif "right" == value["text_horizontal_align"]:
				window.SetHorizontalAlignRight()

		if value.has_key("text_vertical_align"):
			if "top" == value["text_vertical_align"]:
				window.SetVerticalAlignTop()
			elif "center" == value["text_vertical_align"]:
				window.SetVerticalAlignCenter()
			elif "bottom" == value["text_vertical_align"]:
				window.SetVerticalAlignBottom()

		if value.has_key("all_align"):
			window.SetHorizontalAlignCenter()
			window.SetVerticalAlignCenter()
			window.SetWindowHorizontalAlignCenter()
			window.SetWindowVerticalAlignCenter()

		if value.has_key("r") and value.has_key("g") and value.has_key("b"):
			window.SetFontColor(float(value["r"]), float(value["g"]), float(value["b"]))
		elif value.has_key("color"):
			window.SetPackedFontColor(value["color"])
		else:
			window.SetFontColor(0.8549, 0.8549, 0.8549)

		if value.has_key("outline"):
			window.SetOutline(value["outline"])

		if value.has_key("text"):
			window.SetText(value["text"])

		if value.has_key("speed"):
			window.SetMoveSpeed(value["speed"])

		self.LoadDefaultData(window, value, parentWindow)
		return True

	## EditLine
	def LoadElementEditLine(self, window, value, parentWindow):
		if False == self.CheckKeyList(value["name"], value, self.EDIT_LINE_KEY_LIST):
			return False

		if value.has_key("secret_flag"):
			window.SetSecret(value["secret_flag"])
		if value.has_key("with_codepage"):
			if value["with_codepage"]:
				window.bCodePage = True
		if value.has_key("only_number"):
			if value["only_number"]:
				window.SetNumberMode()
		if value.has_key("enable_codepage"):
			window.SetIMEFlag(value["enable_codepage"])
		if value.has_key("enable_ime"):
			window.SetIMEFlag(value["enable_ime"])
		if value.has_key("limit_width"):
			window.SetLimitWidth(value["limit_width"])
		if value.has_key("multi_line"):
			if value["multi_line"]:
				window.SetMultiLine()

		window.SetMax(int(value["input_limit"]))
		window.SetSize(int(value["width"]), int(value["height"]))

		self.LoadElementText(window, value, parentWindow)

		return True

	## TitleBar
	def LoadElementTitleBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.TITLE_BAR_KEY_LIST):
			return False

		window.MakeTitleBar(int(value["width"]), value.get("color", "red"))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## HorizontalBar
	def LoadElementHorizontalBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.HORIZONTAL_BAR_KEY_LIST):
			return False

		window.Create(int(value["width"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Board
	def LoadElementBoard(self, window, value, parentWindow):
		if False == self.CheckKeyList(value["name"], value, self.BOARD_KEY_LIST):
			return False

		if app.ENABLE_IMAGE_CLIP_RECT:
			if True == value.has_key("size_skip"):
				window.skipMaxCheck = True

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Board With TitleBar
	def LoadElementBoardWithTitleBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.BOARD_WITH_TITLEBAR_KEY_LIST):
			return False

		window.SetSize(int(value["width"]), int(value["height"]))
		window.SetTitleName(value["title"])
		self.LoadDefaultData(window, value, parentWindow)

		return True

	def LoadElementBorderA(self, window, value, parentWindow):
		if False == self.CheckKeyList(value["name"], value, self.BOARD_KEY_LIST):
			return False
		
		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)
		return True

	## ThinBoard
	def LoadElementThinBoard(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.BOARD_KEY_LIST):
			return False

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	if app.ENABLE_QUEST_RENEWAL:
		## SubTitleBar
		def LoadElementSubTitleBar(self, window, value, parentWindow):
			if False == self.CheckKeyList(value["name"], value, self.SUB_TITLE_BAR_KEY_LIST):
				return False

			window.MakeSubTitleBar(int(value["width"]), value.get("color", "red"))
			self.LoadElementButton(window, value, parentWindow)
			window.Show()
			return True

		## ListBar
		def LoadElementListBar(self, window, value, parentWindow):
			if False == self.CheckKeyList(value["name"], value, self.LIST_BAR_KEY_LIST):
				return False

			window.MakeListBar(int(value["width"]), value.get("color", "red"))
			self.LoadElementButton(window, value, parentWindow)

			return True

	## Box
	def LoadElementBox(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.BOX_KEY_LIST):
			return False

		if True == value.has_key("color"):
			window.SetColor(value["color"])

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Bar
	def LoadElementBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.BAR_KEY_LIST):
			return False

		if True == value.has_key("color"):
			window.SetColor(value["color"])

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Line
	def LoadElementLine(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.LINE_KEY_LIST):
			return False

		if True == value.has_key("color"):
			window.SetColor(value["color"])

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Slot
	def LoadElementSlotBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.SLOTBAR_KEY_LIST):
			return False

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Gauge
	def LoadElementGauge(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.GAUGE_KEY_LIST):
			return False

		window.MakeGauge(value["width"], value["color"])
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## ScrollBar
	def LoadElementScrollBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.SCROLLBAR_KEY_LIST):
			return False

		window.SetScrollBarSize(value["size"])
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## SliderBar
	def LoadElementSliderBar(self, window, value, parentWindow):

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## ListBox
	def LoadElementListBox(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.LIST_BOX_KEY_LIST):
			return False

		if value.has_key("item_align"):
			window.SetTextCenterAlign(value["item_align"])

		window.SetSize(value["width"], value["height"])
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## ListBox2
	def LoadElementListBox2(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.LIST_BOX_KEY_LIST):
			return False

		window.SetRowCount(value.get("row_count", 10)) 
		window.SetSize(value["width"], value["height"])
		self.LoadDefaultData(window, value, parentWindow)

		if value.has_key("item_align"):
			window.SetTextCenterAlign(value["item_align"])

		return True

	## OutlineWindow
	def LoadOutlineWindow(self, window, value, parentWindow):
		if False == self.CheckKeyList(value["name"], value, self.OUTLINE_WINDOW_KEY_LIST):
			return False

		window.MakeOutlineWindow(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	def LoadElementListBoxEx(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.LIST_BOX_KEY_LIST):
			return False

		window.SetSize(value["width"], value["height"])
		self.LoadDefaultData(window, value, parentWindow)

		if value.has_key("itemsize_x") and value.has_key("itemsize_y"):
			window.SetItemSize(int(value["itemsize_x"]), int(value["itemsize_y"]))

		if value.has_key("itemstep"):
			window.SetItemStep(int(value["itemstep"]))

		if value.has_key("viewcount"):
			window.SetViewItemCount(int(value["viewcount"]))

		return True

	def LoadElementNumberLine(self, window, value, parentWindow):
		self.LoadDefaultData(window, value, parentWindow)
		return True

	# app.ENABLE_MONSTER_CARD or app.ENABLE_MYSHOP_DECO or app.ENABLE_MINI_GAME_YUTNORI
	def LoadElementRenderTarget(self, window, value, parentWindow):
		if False == self.CheckKeyList(value["name"], value, self.RENDER_TARGET_KEY_LIST):
			return False

		window.SetSize(value["width"], value["height"])
	
		if True == value.has_key("style"):
			for style in value["style"]:
				window.AddFlag(style)

		self.LoadDefaultData(window, value, parentWindow)
		self.Load()
		return True

	if app.ENABLE_MAILBOX:
		def LoadElementRenderBox(self, window, value, parentWindow):
			if False == self.CheckKeyList(value["name"], value, self.RENDER_BOX_KEY_LIST):
				return False

			window.SetSize(value["width"], value["height"])
			self.LoadDefaultData(window, value, parentWindow)

			if value.has_key("color"):
				window.SetColor(int(value["color"]))

			return True

	if app.ENABLE_BIOLOG_SYSTEM:
		def LoadElementCheckBox(self, window, value, parentWindow):
			if value.has_key("text"):
				window.SetText(value["text"])
			
			if value.has_key("checked") and value["checked"] == True:
				window.SetChecked(window.STATE_SELECTED)
			
			if value.has_key("disabled") and value["disabled"] == True:
				window.Disable()
			
			self.LoadDefaultData(window, value, parentWindow)

		def LoadElementBoxedBoard(self, window, value, parentWindow):
			if not self.CheckKeyList(value["name"], value, self.WINDOW_KEY_LIST):
				return False
			
			window.SetSize(value["width"], value["height"])
			
			if value.has_key("border_color"):
				window.SetBorderColor(value["border_color"])
			
			if value.has_key("border_size"):
				window.SetBorderSize(value["border_size"])
			
			if value.has_key("base_color"):
				window.SetBaseColor(value["base_color"])
			
			self.LoadDefaultData(window, value, parentWindow)
			return True

	if app.USE_BL_FISH_EVENT:
		def LoadElementSpecialGridTable(self, window, value, parentWindow):
			if self.CheckKeyList(value["name"], value, self.SP_GRID_TABLE_KEY_LIST) == False:
				return False

			xBlank = 0
			yBlank = 0

			if value.has_key("x_blank") == True:
				xBlank = int(value["x_blank"])

			if value.has_key("y_blank") == True:
				yBlank = int(value["y_blank"])

			if localeinfo.IsARABIC():
				pass
			else:
				window.SetPosition(int(value["x"]), int(value["y"]))

			window.ArrangeSlot(int(value["start_index"]),\
								int(value["x_count"]),\
								int(value["y_count"]),\
								int(value["x_step"]),\
								int(value["y_step"]),\
								xBlank,\
								yBlank)

			if value.has_key("image") == True:
				r = 1.0
				g = 1.0
				b = 1.0
				a = 1.0

				if value.has_key("image_r") == True and \
					value.has_key("image_g") == True and \
					value.has_key("image_b") == True and \
					value.has_key("image_a") == True:
					r = float(value["image_r"])
					g = float(value["image_g"])
					b = float(value["image_b"])
					a = float(value["image_a"])

				wndMgr.SetSlotBaseImage(window.hWnd, value["image"], r, g, b, a)

			if value.has_key("style") == True:
				if value["style"] == "select":
					wndMgr.SetSlotStyle(window.hWnd, wndMgr.SLOT_STYLE_SELECT)

			if localeinfo.IsARABIC():
				self.LoadDefaultData(window, value, parentWindow)
			else:
				window.Show()

			return True

class ReadingWnd(Bar):
	def __init__(self):
		Bar.__init__(self,"TOP_MOST")

		self.__BuildText()
		self.SetSize(80, 19)
		self.Show()

	def __del__(self):
		Bar.__del__(self)

	def __BuildText(self):
		self.text = TextLine()
		self.text.SetParent(self)
		self.text.SetPosition(4, 3)
		self.text.Show()

	def SetText(self, text):
		self.text.SetText(text)

	def SetReadingPosition(self, x, y):
		xPos = x + 2
		yPos = y  - self.GetHeight() - 2
		self.SetPosition(xPos, yPos)

	def SetTextColor(self, color):
		self.text.SetPackedFontColor(color)

if app.ENABLE_AUTO_REFINE or app.ENABLE_SKILL_COLOR_SYSTEM:
	class CheckBox(Window):
		def __init__(self):
			Window.__init__(self)
			self.backgroundImage = None
			self.checkImage = None

			self.eventFunc = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
			self.eventArgs = { "ON_CHECK" : None, "ON_UNCKECK" : None, }

			self.CreateElements()

		def __del__(self):
			Window.__del__(self)

			self.backgroundImage = None
			self.checkImage = None

			self.eventFunc = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
			self.eventArgs = { "ON_CHECK" : None, "ON_UNCKECK" : None, }

		def CreateElements(self):
			self.backgroundImage = ImageBox()
			self.backgroundImage.SetParent(self)
			self.backgroundImage.AddFlag("not_pick")
			self.backgroundImage.LoadImage("d:/ymir work/ui/game/refine/checkbox.tga")
			self.backgroundImage.Show()

			self.checkImage = ImageBox()
			self.checkImage.SetParent(self)
			self.checkImage.AddFlag("not_pick")
			self.checkImage.SetPosition(0, -4)
			self.checkImage.LoadImage("d:/ymir work/ui/game/refine/checked.tga")
			self.checkImage.Hide()

			self.textInfo = TextLine()
			self.textInfo.SetParent(self)
			self.textInfo.SetPosition(155, -2)
			self.textInfo.SetHorizontalAlignLeft()
			self.textInfo.Show()

			self.SetSize(self.backgroundImage.GetWidth() + self.textInfo.GetTextSize()[0], self.backgroundImage.GetHeight() + self.textInfo.GetTextSize()[1])

		def SetTextInfo(self, info):
			if self.textInfo:
				self.textInfo.SetText(info)

			self.SetSize(self.backgroundImage.GetWidth() + self.textInfo.GetTextSize()[0], self.backgroundImage.GetHeight() + self.textInfo.GetTextSize()[1])

		def SetCheckStatus(self, flag):
			if flag:
				self.checkImage.Show()
			else:
				self.checkImage.Hide()

		def GetCheckStatus(self):
			if self.checkImage:
				return self.checkImage.IsShow()

			return False

		def SetEvent(self, func, *args) :
			result = self.eventFunc.has_key(args[0])
			if result:
				self.eventFunc[args[0]] = func
				self.eventArgs[args[0]] = args
			else:
				print "[ERROR] ui.py SetEvent, Can`t Find has_key : %s" % args[0]

		def SetBaseCheckImage(self, image):
			if not self.backgroundImage:
				return
			
			self.backgroundImage.LoadImage(image)

		def OnMouseLeftButtonUp(self):
			if self.checkImage:
				if self.checkImage.IsShow():
					self.checkImage.Hide()

					if self.eventFunc["ON_UNCKECK"]:
						apply(self.eventFunc["ON_UNCKECK"], self.eventArgs["ON_UNCKECK"])
				else:
					self.checkImage.Show()

					if self.eventFunc["ON_CHECK"]:
						apply(self.eventFunc["ON_CHECK"], self.eventArgs["ON_CHECK"])

if app.USE_BL_FISH_EVENT:
	class FishEventGridSlotWindow(GridSlotWindow):
		def __init__(self):
			GridSlotWindow.__init__(self)
			self.startIndex = 0

		def __del__(self):
			GridSlotWindow.__del__(self)

		def RegisterWindow(self, layer):
			self.hWnd = wndMgr.RegisterFishEventGridSlotWindow(self, layer)

		def ArrangeSlot(self, StartIndex, xCount, yCount, xSize, ySize, xBlank, yBlank):
			self.startIndex = StartIndex

			wndMgr.ArrangeSlot(self.hWnd, StartIndex, xCount, yCount, xSize, ySize, xBlank, yBlank)
			self.startIndex = StartIndex

		def GetStartIndex(self):
			return self.startIndex

		def SetPickedAreaRender(self, flag):
			wndMgr.SetPickedAreaRender(self.hWnd, flag)

def MakeSlotBar(parent, x, y, width, height):
	slotBar = SlotBar()
	slotBar.SetParent(parent)
	slotBar.SetSize(width, height)
	slotBar.SetPosition(x, y)
	slotBar.Show()
	return slotBar

#app.USE_PORTABLE_TELEPORT_WITH_UI: @_show
def MakeImageBox(parent, name, x, y, _show = True):
	image = ImageBox()
	image.SetParent(parent)
	image.LoadImage(name)
	image.SetPosition(x, y)

	if _show == True:
		image.Show()

	return image

def MakeExpandedImageBox(parent, name, x, y):
	image = ExpandedImageBox()
	image.SetParent(parent)
	image.LoadImage(name)
	image.SetPosition(x, y)
	image.Show()
	return image

def MakeTextLine(parent):
	textLine = TextLine()
	textLine.SetParent(parent)
	textLine.SetWindowHorizontalAlignCenter()
	textLine.SetWindowVerticalAlignCenter()
	textLine.SetHorizontalAlignCenter()
	textLine.SetVerticalAlignCenter()
	textLine.Show()
	return textLine

if app.ENABLE_EXTENDED_BATTLE_PASS:
	def AddTextLine(parent, x, y, text, outline = 0):
		textLine = TextLine()
		textLine.SetParent(parent)
		textLine.SetPosition(x, y)
		if outline != 0:
			textLine.SetOutline()
		
		textLine.SetText(text)
		textLine.Show()
		return textLine

	def MakeNewTextLine(parent, horizontalAlign = True, verticalAlgin = True, x = 0, y = 0):
		textLine = TextLine()
		textLine.SetParent(parent)
		if horizontalAlign == True:
			textLine.SetWindowHorizontalAlignCenter()
		
		if verticalAlgin == True:
			textLine.SetWindowVerticalAlignCenter()

		textLine.SetHorizontalAlignCenter()
		textLine.SetVerticalAlignCenter()

		if x != 0 and y != 0:
			textLine.SetPosition(x, y)

		textLine.Show()
		return textLine

def MakeExpandedImageBox(parent, name, x, y, flag = ""):
	image = ExpandedImageBox()
	image.SetParent(parent)
	image.LoadImage(name)
	image.SetPosition(x, y)
	if flag != "":
		image.AddFlag(flag)
	
	image.Show()
	return image

def MakeTextLineWithouAlign(parent, text, x, y):
	textLine = TextLine()
	textLine.SetParent(parent)
	textLine.SetPosition(x, y)
	textLine.SetText(text)
	textLine.Show()
	return textLine

def MakeButtonRemoveStone(parent, x, y, tooltipText, path, up, over, down, button_text = ""):
	button = Button()
	button.SetParent(parent)
	button.SetPosition(x, y)
	button.SetUpVisual(path + up)
	button.SetOverVisual(path + over)
	button.SetDownVisual(path + down)
	button.SetToolTipText(tooltipText)
	button.SetText(button_text)
	button.Show()
	return button

def MakeButton(parent, x, y, tooltipText, path, up, over, down):
	button = Button()
	button.SetParent(parent)
	button.SetPosition(x, y)
	button.SetUpVisual(path + up)
	button.SetOverVisual(path + over)
	button.SetDownVisual(path + down)
	button.SetToolTipText(tooltipText)
	button.Show()
	return button

def MakeRadioButton(parent, x, y, buttonText, path, up, over, down, tooltip = ""):
	button = RadioButton()
	button.SetParent(parent)
	button.SetPosition(x, y)
	button.SetUpVisual(path + up)
	button.SetOverVisual(path + over)
	button.SetDownVisual(path + down)
	button.SetText(buttonText)
	button.SetToolTipText(tooltip)
	button.Show()
	return button

def MakeNewScrollBar(parent, x, y, height):
	scrollbar = NewScrollBar()
	scrollbar.SetParent(parent)
	scrollbar.SetPosition(x, y)
	scrollbar.SetScrollBarSize(height)
	scrollbar.Show()
	return scrollbar

def MakeOptionsCheckBox(parent, text, x, y):
	checkBox = CheckBox()
	checkBox.SetParent(parent)
	checkBox.SetPosition(x, y)
	checkBox.SetTextInfo(text)
	checkBox.SetBaseCheckImage("d:/ymir work/ui/new_options/options_checkbox.tga")
	checkBox.Show()
	return checkBox

def MakeSliderBar(parent, x, y, event):
	slideBar = NewSliderBar()
	slideBar.SetParent(parent)
	slideBar.SetEvent(event)
	slideBar.SetPosition(x, y)
	slideBar.Show()
	
	return slideBar

def RenderRoundBox(x, y, width, height, color):
	grp.SetColor(color)
	grp.RenderLine(x+2, y, width-3, 0)
	grp.RenderLine(x+2, y+height, width-3, 0)
	grp.RenderLine(x, y+2, 0, height-4)
	grp.RenderLine(x+width, y+1, 0, height-3)
	grp.RenderLine(x, y+2, 2, -2)
	grp.RenderLine(x, y+height-2, 2, 2)
	grp.RenderLine(x+width-2, y, 2, 2)
	grp.RenderLine(x+width-2, y+height, 2, -2)

def GenerateColor(r, g, b):
	r = float(r) / 255.0
	g = float(g) / 255.0
	b = float(b) / 255.0
	return grp.GenerateColor(r, g, b, 1.0)

def EnablePaste(flag):
	ime.EnablePaste(flag)

def GetHyperlink():
	return wndMgr.GetHyperlink()

if app.ENABLE_INGAME_WIKI:
	class WikiRenderTarget(Window):
		def __init__(self):
			Window.__init__(self)

		def __del__(self):
			Window.__del__(self)

		def RegisterWindow(self, layer):
			self.hWnd = wndMgr.RegisterWikiRenderTarget(self, layer)

	class InGameWikiCheckBox(Window):
		def __init__(self):
			Window.__init__(self)
			self.backgroundImage = None
			self.checkImage = None
			
			self.eventFunc = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
			self.eventArgs = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
			
			self.CreateElements()
		
		def __del__(self):
			Window.__del__(self)
			
			self.backgroundImage = None
			self.checkImage = None
			
			self.eventFunc = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
			self.eventArgs = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
		
		def CreateElements(self):
			self.backgroundImage = ImageBox()
			self.backgroundImage.SetParent(self)
			self.backgroundImage.AddFlag("not_pick")
			self.backgroundImage.LoadImage("d:/ymir work/ui/wiki/wiki_check_box_clean.tga")
			self.backgroundImage.Show()
			
			self.checkImage = ImageBox()
			self.checkImage.SetParent(self)
			self.checkImage.AddFlag("not_pick")
			self.checkImage.LoadImage("d:/ymir work/ui/wiki/wiki_check_box_checked.tga")
			self.checkImage.Hide()
			
			self.textInfo = TextLine()
			self.textInfo.SetParent(self)
			if localeinfo.IsARABIC():
				self.textInfo.SetPosition(-5, -1)
			else:
				self.textInfo.SetPosition(20, 0)
			self.textInfo.Show()
			
			self.SetSize(self.backgroundImage.GetWidth() + self.textInfo.GetTextSize()[0], self.backgroundImage.GetHeight() + self.textInfo.GetTextSize()[1])
		
		def SetTextInfo(self, info):
			if self.textInfo:
				# textLine.SetWindowHorizontalAlignRight()
				self.textInfo.SetWindowHorizontalAlignLeft()
				self.textInfo.SetText(info)
			
			self.SetSize(self.backgroundImage.GetWidth() + self.textInfo.GetTextSize()[0], self.backgroundImage.GetHeight() + self.textInfo.GetTextSize()[1])

		def SetTextInfoAe(self, info):
			if self.textInfo:
				self.textInfo.SetText(info)
			
			self.SetSize(self.backgroundImage.GetWidth() + self.textInfo.GetTextSize()[0], self.backgroundImage.GetHeight() + self.textInfo.GetTextSize()[1])

		def SetCheckStatus(self, flag):
			if flag:
				self.checkImage.Show()
			else:
				self.checkImage.Hide()
		
		def GetCheckStatus(self):
			if self.checkImage:
				return self.checkImage.IsShow()
			
			return False
		
		def SetEvent(self, func, *args) :
			result = self.eventFunc.has_key(args[0])
			if result:
				self.eventFunc[args[0]] = func
				self.eventArgs[args[0]] = args
			else:
				print "[ERROR] ui.py SetEvent, Can`t Find has_key : %s" % args[0]

		def SetBaseCheckImage(self, image):
			if not self.backgroundImage:
				return
			
			self.backgroundImage.LoadImage(image)

		def OnMouseLeftButtonUp(self):
			if self.checkImage:
				if self.checkImage.IsShow():
					self.checkImage.Hide()
					
					if self.eventFunc["ON_UNCKECK"]:
						apply(self.eventFunc["ON_UNCKECK"], self.eventArgs["ON_UNCKECK"])
				else:
					self.checkImage.Show()
					
					if self.eventFunc["ON_CHECK"]:
						apply(self.eventFunc["ON_CHECK"], self.eventArgs["ON_CHECK"])

RegisterToolTipWindow("TEXT", TextLine)

class RenderTarget(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

		self.renderIndex = 0

		self.children = {}
		self.children["totalPos"] = [0, 0]
		self.children["lastPos"] = [0, 0]
		self.children["isDrag"] = False

		self.SetMouseRightButtonDownEvent(__mem_func__(self.RenderMouseRightDown))
		self.SetMouseRightButtonUpEvent(__mem_func__(self.RenderMouseRightUp))

		self.eventDict = {}
		self.eventFunc = {"MOUSE_LEFT_BUTTON_DOWN" : None, "mouse_click" : None, "mouse_over_in" : None, "mouse_over_out" : None, "MOUSE_RIGHT_BUTTON_UP" : None,"MOUSE_RIGHT_BUTTON_DOWN" : None}
		self.eventArgs = {"MOUSE_LEFT_BUTTON_DOWN" : None, "mouse_click" : None, "mouse_over_in" : None, "mouse_over_out" : None, "MOUSE_RIGHT_BUTTON_UP" : None,"MOUSE_RIGHT_BUTTON_DOWN" : None}

	def Destroy(self):
		self.renderIndex = 0

		self.children = {}

		self.SetMouseRightButtonDownEvent(None)
		self.SetMouseRightButtonUpEvent(None)

		self.eventDict = {}
		self.eventFunc = 0
		self.eventArgs = 0

	def __del__(self):
		Window.__del__(self)

	def Load(self):
		self.renderIndex = wndMgr.LoadRenderTarget(self.hWnd)

	def GetIndex(self):
		return self.renderIndex

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterRenderTarget(self, layer)

	def CanCheckMouse(self):
		if renderTarget.IsShow(self.GetIndex()) != 1:
			return False
		if self.children.has_key("isDrag"):
			return self.children["isDrag"]

	def SetRenderingRect(self, left, top, right, bottom):
		wndMgr.SetRenderingRect(self.hWnd, left, top, right, bottom)

	def SetEvent(self, func, *args):
		result = self.eventFunc.has_key(args[0])
		if result:
			self.eventFunc[args[0]] = func
			self.eventArgs[args[0]] = args

	def OnUpdate(self):
		if self.CanCheckMouse():
			[currentMousePos, lastPos] = [app.GetCursorPosition(), self.children["lastPos"]]
			totalPos = self.children["totalPos"] if self.children.has_key("totalPos") else [0, 0]
			_x = (currentMousePos[0] - lastPos[0]) + totalPos[0]
			_y = (currentMousePos[1] - lastPos[1]) + totalPos[1]
			fNewPitchVelocity = _y * 0.3
			fNewRotationVelocity = _x * 0.3
			renderTarget.RotateEyeAroundTarget(self.GetIndex(), fNewPitchVelocity, fNewRotationVelocity)
			self.children["totalPos"] = [_x, _y]
			self.children["lastPos"] = currentMousePos

	def RenderMouseRightUp(self):
		app.SetCursor(app.NORMAL)
		self.children["isDrag"] = False
		return True

	def RenderMouseRightDown(self):
		app.SetCursor(app.CAMERA_ROTATE)
		self.children["isDrag"] = True
		self.children["lastPos"] = app.GetCursorPosition()
		return True

	def OnMouseWheel(self, nLen):
		renderIndex = self.GetIndex()
		if renderTarget.IsShow(renderIndex) != 1:
			return False

		renderTarget.Zoom(renderIndex, app.CAMERA_TO_NEGATIVE if nLen > 0 else app.CAMERA_TO_POSITIVE)
		return True

	def OnMouseLeftButtonUp(self) :
		Window.OnMouseLeftButtonUp(self)
		if self.eventFunc["mouse_click"]:
			apply(self.eventFunc["mouse_click"], self.eventArgs["mouse_click"])

	def OnMouseOverIn(self):
		if self.eventFunc["mouse_over_in"]:
			apply(self.eventFunc["mouse_over_in"], self.eventArgs["mouse_over_in"])

		if self.eventDict.has_key("MOUSE_OVER_IN"):
			if self.eventArgs["MOUSE_OVER_IN"]:
				apply(self.eventDict["MOUSE_OVER_IN"], self.eventArgs["MOUSE_OVER_IN"])
			else:
				self.eventDict["MOUSE_OVER_IN"]()

	def OnMouseOverOut(self):
		if self.eventFunc["mouse_over_out"]:
			apply(self.eventFunc["mouse_over_out"], self.eventArgs["mouse_over_out"])

		if self.eventDict.has_key("MOUSE_OVER_OUT"):
			if self.eventArgs["MOUSE_OVER_OUT"]:
				apply(self.eventDict["MOUSE_OVER_OUT"], self.eventArgs["MOUSE_OVER_OUT"])
			else:
				self.eventDict["MOUSE_OVER_OUT"]()

if app.ENABLE_MAILBOX:
	class RenderBox(Window):
		def __init__(self, layer = "UI"):
			Window.__init__(self, layer)
			
			self.color = 0xFF000000

		def __del__(self):
			Window.__del__(self)
			self.color = 0xFF000000

		def RegisterWindow(self, layer):
			self.hWnd = wndMgr.Register(self, layer)

		def SetColor(self, color):
			self.color = color

		def OnRender(self):
			(x, y, width, height) = self.GetRect()
			grp.SetColor(self.color)
			grp.RenderBar(x, y, width, height)

class MouseReflector(Window):
	def __init__(self, parent):
		Window.__init__(self)
		self.SetParent(parent)
		self.AddFlag("not_pick")
		self.width = self.height = 0
		self.isDown = False

	def __del__(self):
		Window.__del__(self)

	def Down(self):
		self.isDown = True

	def Up(self):
		self.isDown = False

	def OnRender(self):
		if self.isDown:
			grp.SetColor(WHITE_COLOR)
		else:
			grp.SetColor(HALF_WHITE_COLOR)
		
		x, y = self.GetGlobalPosition()
		grp.RenderBar(x + 2, y + 2, self.GetWidth() - 4, self.GetHeight() - 4)

class CheckBoxNew(ImageBox):
	def __init__(self, parent, x, y, event, filename = "d:/ymir work/ui/chat/chattingoption_check_box_off.sub"):
		ImageBox.__init__(self)
		self.SetParent(parent)
		self.SetPosition(x, y)
		self.LoadImage(filename)
		self.mouseReflector = MouseReflector(self)
		self.mouseReflector.SetSize(self.GetWidth(), self.GetHeight())
		image = MakeImageBox(self, "d:/ymir work/ui/public/check_image.sub", 0, 0)
		image.AddFlag("not_pick")
		image.SetWindowHorizontalAlignCenter()
		image.SetWindowVerticalAlignCenter()
		image.Hide()
		self.check = False
		self.enable = True
		self.image = image
		self.event = event
		self.Show()
		self.mouseReflector.UpdateRect()

	def __del__(self):
		ImageBox.__del__(self)

	def GetCheck(self):
		return self.check

	def SetCheck(self, flag):
		if flag:
			self.check = True
			self.image.Show()
		else:
			self.check = False
			self.image.Hide()

	def Disable(self):
		self.enable = False

	def OnMouseOverIn(self):
		if not self.enable:
			return
		
		self.mouseReflector.Show()

	def OnMouseOverOut(self):
		if not self.enable:
			return
		
		self.mouseReflector.Hide()

	def OnMouseLeftButtonDown(self):
		if not self.enable:
			return
		
		self.mouseReflector.Down()

	def OnMouseLeftButtonUp(self):
		if not self.enable:
			return
		
		self.mouseReflector.Up()
		self.event()

class MultiTextLine(Window):
	def __del__(self):
		Window.__del__(self)
	def Destroy(self):
		self.children = []
		self.rangeText = 0
	def __init__(self):
		Window.__init__(self)
		self.children = []
		self.rangeText = 15
		self.textType = ""
	def SetTextType(self, textType):
		self.textType = textType
		for text in self.children:
			self.AddTextType(self.textType.split("#"),text)
	def SetTextRange(self, range):
		self.rangeText = range
		yPosition = 0
		for text in self.children:
			text.SetPosition(0,yPosition)
			yPosition+=self.rangeText
	def AddTextType(self, typeArg, text):
		if len(typeArg) > 1:
			if typeArg[0] == "vertical":
				if typeArg[1] == "top":
					text.SetVerticalAlignTop()
				elif typeArg[1] == "bottom":
					text.SetVerticalAlignBottom()
				elif typeArg[1] == "center":
					text.SetVerticalAlignCenter()
			elif typeArg[0] == "horizontal":
				if typeArg[1] == "left":
					text.SetHorizontalAlignLeft()
				elif typeArg[1] == "right":
					text.SetHorizontalAlignRight()
				elif typeArg[1] == "center":
					text.SetHorizontalAlignCenter()
	def SetText(self, cmd):
		if len(self.children) > 1:
			self.children=[]
		multi_arg = cmd.split("\n")
		yPosition = 0
		for text in multi_arg:
			childText = TextLine()
			childText.SetParent(self)
			childText.SetPosition(0,yPosition)
			if self.textType != "":
				self.AddTextType(self.textType.split("#"),childText)
			childText.SetText(str(text))
			childText.Show()
			self.children.append(childText)
			yPosition+=self.rangeText

	def SetTextColor(self, cmd,color):
		if len(self.children) > 1:
			self.children=[]
		multi_arg = cmd.split("\n")
		yPosition = 0
		for text in multi_arg:
			childText = TextLine()
			childText.SetParent(self)
			childText.SetPosition(0,yPosition)
			if self.textType != "":
				self.AddTextType(self.textType.split("#"),childText)
			childText.SetText(str(text))
			childText.SetPackedFontColor(color)
			childText.Show()
			self.children.append(childText)
			yPosition+=self.rangeText

if app.USE_BONUS_PAGE:
	class AutoGrowingVerticalContainer(Window):
		def __init__(self, layer = "UI"):
			Window.__init__(self, layer)

			self.width = 0
			self.height = 0

			self.elementOffsetY = 0
			self.elementStartOffsetY = 0

			self.containerItems = []

		def __del__(self):
			self.width = 0
			self.height = 0

			self.elementOffsetY = 0
			self.elementStartOffsetY = 0

			for i in self.containerItems:
				del i

			self.containerItems = []

			Window.__del__(self)

		def SetWidth(self, width):
			self.width = width

		def SetElementOffset(self, offsetY):
			self.elementOffsetY = offsetY

		def AppendItem(self, item):
			self.height += item.GetHeight() + self.elementOffsetY
			self.containerItems.append(item)
			self.Update()

		def Update(self):
			self.SetSize(self.width, self.height)
			self.UpdateRect()

		def RecalculateHeight(self):
			self.height = 0
			for item in self.containerItems:
				self.height = self.height + item.GetHeight() + self.elementOffsetY

			self.Update()

		def GetElementByIndex(self, index):
			if index >= len(self.containerItems):
				return None

			return self.containerItems[index]

		def ClearItems(self):
			self.containerItems[:] = []
			self.RecalculateHeight()

	class AutoGrowingVerticalContainerEx(AutoGrowingVerticalContainer):
		def __init__(self):
			AutoGrowingVerticalContainer.__init__(self)

			self.elementStartOffsetY = 0
			self.elementCurrentOffsetY = 0
			self.elementOffsetX = 0

			self.oldItems = []

		def SetStartOffset(self, offset):
			self.elementStartOffsetY = offset
			self.height = offset

		def AppendItem(self, item):
			addHeight = item.GetHeight() + self.elementOffsetY
			self.height += addHeight
			self.containerItems.append(item)
			self.containerItems[-1].SetPosition(self.elementOffsetX, self.height - self.containerItems[-1].GetHeight())

			self.Update()

		def ShowItems(self):
			for item in self.containerItems:
				item.Show()

		def HideItems(self):
			for item in self.containerItems:
				item.Hide()

		def GetItems(self):
			return self.containerItems

		def RecalculateHeight(self):
			self.oldItems = self.containerItems
			self.height = self.elementStartOffsetY
			self.containerItems = []

			for item in self.oldItems:
				self.AppendItem(item)

	class ToggleAbleTitledWindow(Window):
		def __init__(self, imageFileName, imageFileNameOn, iconFileName = None, _text_x = -1, _text_y = -1, _font_name = None):
			Window.__init__(self)

			self.imageFileName = imageFileName
			self.imageFileNameOn = imageFileNameOn

			self.baseSize = [169, 25]
			self.eventsOpenCloseActive = True

			tmp = ExpandedImageBox()
			tmp.SetEvent(__mem_func__(self.OnMouseLeftButtonDoubleClick), "mouse_click")
			tmp.SetParent(self)
			tmp.LoadImage(imageFileName)
			tmp.Show()
			self.backGroundImage = tmp

			tmp = ExpandedImageBox()
			tmp.SetParent(self.backGroundImage)
			tmp.SetEvent(__mem_func__(self.OnToggle), "mouse_click")
			tmp.SetPosition(18, 5)
			tmp.Show()
			self.toggleIndicator = tmp

			tmp = TextLine()
			tmp.SetParent(self.backGroundImage)

			if _text_x != -1 and _text_y != -1:
				tmp.SetPosition(_text_x, _text_y)

				if _font_name != None:
					tmp.SetFontName(_font_name)
			else:
				tmp.SetPosition(40, 6)

			if localeinfo.IsARABIC():
				tmp.SetWindowHorizontalAlignRight()

			tmp.Show()
			self.titleText = tmp

			if iconFileName:
				tmp = ExpandedImageBox()
				tmp.SetEvent(__mem_func__(self.OnMouseLeftButtonDoubleClick), "mouse_click")
				tmp.SetParent(self.backGroundImage)
				tmp.LoadImage(iconFileName)
				tmp.SetPosition(5, 4)
				tmp.Show()
				self.iconImage = tmp
			else:
				self.iconImage = None

			tmp = AutoGrowingVerticalContainerEx()
			tmp.SetParent(self)
			tmp.SetStartOffset(0)
			tmp.SetPosition(0, self.backGroundImage.GetHeight())
			tmp.Show()
			self.toggleAbleContent = tmp

			self.eventFunc = {}
			self.eventArgs = {}

			self.toggleContentIsShown = False
			self.toggleShowFilename = ""
			self.toggleHideFilename = ""
			self.baseSize[1] = self.backGroundImage.GetHeight()
			self.width = 0

		def __del__(self):
			self.eventFunc = {}
			self.eventArgs = {}

			self.imageFileName = ""
			self.imageFileNameOn = ""

			Window.__del__(self)

		def OnMouseLeftButtonDoubleClick(self):
			self.OnToggle()
			return True

		def SetOpenCloseEventStatus(self, status):
			self.eventsOpenCloseActive = status

		def SetWidth(self, width):
			self.baseSize[0] = width

			self.toggleAbleContent.SetWidth(width)
			self.width = width
			self.SetSize(width, self.GetHeight())

		def SetTitle(self, title):
			self.titleText.SetText(title)

		def SetbackGroundImage(self, filename):
			self.backGroundImage = ImageBox()
			self.backGroundImage.SetParent(self)
			self.backGroundImage.LoadImage(filename)
			self.backGroundImage.Show()

		def SetToggleShowFilename(self, filename):
			self.toggleShowFilename = filename
			if not self.toggleContentIsShown:
				self.toggleIndicator.LoadImage(self.toggleShowFilename)

		def SetToggleHideFilename(self, filename):
			self.toggleHideFilename = filename
			if self.toggleContentIsShown:
				self.toggleIndicator.LoadImage(self.toggleHideFilename)

		def SetOnToggleEvent(self, event, *args):
			self.eventFunc["toggle"] = event
			self.eventArgs["toggle"] = args

		def SetOnGrowEvent(self, event, *args):
			self.eventFunc["grow"] = event
			self.eventArgs["grow"] = args

		def SetOpenEvent(self, event, *args):
			self.eventFunc["open"] = event
			self.eventArgs["open"] = args

		def SetCloseEvent(self, event, *args):
			self.eventFunc["close"] = event
			self.eventArgs["close"] = args

		def AppendToToggleContent(self, item):
			self.toggleAbleContent.AppendItem(item)
			item.SetParent(self.toggleAbleContent)

			if self.eventFunc.has_key("grow"):
				apply(self.eventFunc["grow"], self.eventArgs["grow"])

			self.Update()

		def Update(self):
			if self.toggleContentIsShown:
				self.SetSize(self.baseSize[0], self.baseSize[1] + self.toggleAbleContent.GetHeight())
			else:
				self.SetSize(*self.baseSize)

			self.UpdateRect()

		def Close(self):
			self.backGroundImage.UnloadImage()
			self.backGroundImage.LoadImage(self.imageFileName)
			self.backGroundImage.SetDiffuseColor(1.0, 1.0, 1.0, 1.0)

			if len(self.toggleShowFilename) != 0:
				self.toggleIndicator.UnloadImage()
				self.toggleIndicator.LoadImage(self.toggleShowFilename)

			self.toggleAbleContent.Hide()
			self.toggleAbleContent.HideItems()

			self.toggleContentIsShown = False

			self.Update()

			if self.eventsOpenCloseActive and self.eventFunc.has_key("close"):
				apply(self.eventFunc["close"], self.eventArgs["close"])

		def Open(self):
			self.backGroundImage.UnloadImage()
			self.backGroundImage.LoadImage(self.imageFileNameOn)

			if len(self.toggleHideFilename) != 0:
				self.toggleIndicator.UnloadImage()
				self.toggleIndicator.LoadImage(self.toggleHideFilename)

			self.toggleAbleContent.Show()
			self.toggleAbleContent.ShowItems()
			self.toggleContentIsShown = True

			self.Update()

			if self.eventsOpenCloseActive and self.eventFunc.has_key("open"):
				apply(self.eventFunc["open"], self.eventArgs["open"])

		def OnToggle(self):
			self.eventsOpenCloseActive = False

			if self.toggleContentIsShown:
				self.Close()
			else:
				self.Open()

			self.eventsOpenCloseActive = True

			if self.eventFunc.has_key("toggle"):
				apply(self.eventFunc["toggle"], self.eventArgs["toggle"])

	class ScrollBarToggle(Window):
		BASE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
		CORNERS_AND_LINES_COLOR = grp.GenerateColor(0.3411, 0.3411, 0.3411, 1.0)
		BAR_NUMB = 9

		class MiddleBar(DragButton):
			MIDDLE_BAR_COLOR = grp.GenerateColor(0.6470, 0.6470, 0.6470, 1.0)

			def __init__(self):
				DragButton.__init__(self)
				self.AddFlag("movable")

				self.middle = Bar()
				self.middle.SetParent(self)
				self.middle.AddFlag("attach")
				self.middle.AddFlag("not_pick")
				self.middle.SetColor(self.MIDDLE_BAR_COLOR)
				self.middle.SetSize(1, 1)
				self.middle.Show()

			def __del__(self):
				DragButton.__del__(self)

			def SetStaticScale(self, size):
				(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
				DragButton.SetSize(self, base_width, size)
				self.middle.SetSize(base_width, size)

			def SetSize(self, selfSize, fullSize):
				(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
				DragButton.SetSize(self, base_width, truediv(int(selfSize), int(fullSize)) * selfSize)
				self.middle.SetSize(base_width, truediv(int(selfSize), int(fullSize)) * selfSize)

			def SetStaticSize(self, size):
				size = max(2, size)
				DragButton.SetSize(self, size, self.middle.GetHeight())
				self.middle.SetSize(size, self.middle.GetHeight())

		def __init__(self):
			Window.__init__(self)

			self.run_in_wheel = True

			self.scrollEvent = None
			self.scrollSpeed = 1
			self.sizeScale = 1.0

			self.bars = []
			for i in xrange(self.BAR_NUMB):
				br = Bar()
				br.SetParent(self)
				br.AddFlag("attach")
				br.AddFlag("not_pick")
				br.SetColor([self.CORNERS_AND_LINES_COLOR, self.BASE_COLOR][i == (self.BAR_NUMB - 1)])

				if not (i % 2 == 0):
					br.SetSize(1, 1)

				br.Show()

				self.bars.append(br)

			self.middleBar = self.MiddleBar()
			self.middleBar.SetParent(self)
			self.middleBar.SetMoveEvent(__mem_func__(self.OnScrollMove))
			self.middleBar.Show()

		def __del__(self):
			Window.__del__(self)

		def Destroy(self):
			for e in self.bars:
				del e

			self.bars = []

			if self.middleBar:
				del self.middleBar
				self.middleBar = None

		def OnScrollMove(self):
			if not self.scrollEvent:
				return

			arg = float(self.middleBar.GetLocalPosition()[1] - 1) / float(self.GetHeight() - 2 - self.middleBar.GetHeight())
			self.scrollEvent(arg)

		def ResetScrollEvent(self):
			self.scrollEvent = None

		def SetScrollEvent(self, func):
			self.scrollEvent = __mem_func__(func)

		def SetScrollSpeed(self, speed):
			self.scrollSpeed = speed

		def OnRunMouseWheel(self, length):
			if not self.run_in_wheel:
				return False

			if self.IsInPosition():
				val = min(max(1, self.middleBar.GetLocalPosition()[1] - (length * 0.01) * self.scrollSpeed * self.sizeScale), self.GetHeight() - self.middleBar.GetHeight() - 1)
				self.middleBar.SetPosition(1, val)

				self.OnScrollMove()
				return True

			return False

		def OnMouseLeftButtonDown(self):
			(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
			if xMouseLocalPosition == 0 or xMouseLocalPosition == self.GetWidth():
				return

			y_pos = (yMouseLocalPosition - self.middleBar.GetHeight() / 2)
			self.middleBar.SetPosition(1, y_pos)

			self.OnScrollMove()

		def SetSize(self, w, h):
			(width, height) = (max(3, w), max(3, h))

			Window.SetSize(self, width, height)

			self.bars[0].SetSize(1, (height - 2))
			self.bars[0].SetPosition(0, 1)
			self.bars[2].SetSize((width - 2), 1)
			self.bars[2].SetPosition(1, 0)
			self.bars[4].SetSize(1, (height - 2))
			self.bars[4].SetPosition((width - 1), 1)
			self.bars[6].SetSize((width - 2), 1)
			self.bars[6].SetPosition(1, (height - 1))
			self.bars[8].SetSize((width - 2), (height - 2))
			self.bars[8].SetPosition(1, 1)

			self.bars[1].SetPosition(0, 0)
			self.bars[3].SetPosition((width - 1), 0)
			self.bars[5].SetPosition((width - 1), (height - 1))
			self.bars[7].SetPosition(0, (height - 1))

			self.middleBar.SetStaticSize(width - 2)
			self.middleBar.SetSize(12, self.GetHeight())

			self.middleBar.SetRestrictMovementArea(1, 1, width - 2, height - 2)

		def SetScale(self, selfSize, fullSize):
			self.sizeScale = float(selfSize/fullSize)
			self.middleBar.SetSize(selfSize, fullSize)

		def SetStaticScale(self, r_size):
			self.middleBar.SetStaticScale(r_size)

		def SetPosScale(self, fScale):
			pos = (math.ceil((self.GetHeight() - 2 - self.middleBar.GetHeight()) * fScale) + 1)
			self.SetPos(pos)

		def SetPos(self, pos):
			wPos = (1, pos)
			self.middleBar.SetPosition(*wPos)

class ExpandedImageBoxButton(ImageBox):
	def __init__(self, layer = "UI"):
		ImageBox.__init__(self, layer)
		self.ButtonText = None
		# Initialize visual states
		self.normal_visual = ""
		self.over_visual = ""
		self.down_visual = ""
		# FIX: Add separate click event storage (like Button class)
		self.clickEventFunc = None
		self.clickEventArgs = ()
		# FIX: Add uppercase event keys for mouse over events (OnMouseOverIn/Out use these)
		self.eventFunc["MOUSE_OVER_IN"] = None
		self.eventFunc["MOUSE_OVER_OUT"] = None
		self.eventArgs["MOUSE_OVER_IN"] = ()
		self.eventArgs["MOUSE_OVER_OUT"] = ()

	def __del__(self):
		ImageBox.__del__(self)
		self.clickEventFunc = None
		self.clickEventArgs = None

	# FIX: Override SetEvent to work like Button class for click events
	def SetEvent(self, func, eventType="MOUSE_CLICK"):
		if eventType == "MOUSE_CLICK":
			self.clickEventFunc = func
			self.clickEventArgs = ()
		elif eventType in ("MOUSE_OVER_IN", "MOUSE_OVER_OUT"):
			# Store in eventFunc dict with correct uppercase key
			self.eventFunc[eventType] = func
			self.eventArgs[eventType] = ()
		else:
			# Fall back to parent's SetEvent for other event types
			ImageBox.SetEvent(self, func, eventType)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterExpandedImageBox(self, layer)

	def SetScale(self, xScale, yScale):
		wndMgr.SetScale(self.hWnd, xScale, yScale)

	def SetOrigin(self, x, y):
		wndMgr.SetOrigin(self.hWnd, x, y)

	def SetRotation(self, rotation):
		wndMgr.SetRotation(self.hWnd, rotation)

	def SetRenderingMode(self, mode):
		wndMgr.SetRenderingMode(self.hWnd, mode)

	def SetRenderingRect(self, left, top, right, bottom):
		wndMgr.SetRenderingRect(self.hWnd, left, top, right, bottom)

	def SetClipRect(self, left, top, right, bottom, isVertical = False):
		wndMgr.SetClipRect(self.hWnd, left, top, right, bottom, isVertical)

	def SetPercentage(self, curValue, maxValue):
		if maxValue:
			self.SetRenderingRect(0.0, 0.0, -1.0 + float(curValue) / float(maxValue), 0.0)
		else:
			self.SetRenderingRect(0.0, 0.0, 0.0, 0.0)

	def GetWidth(self):
		return wndMgr.GetWindowWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetWindowHeight(self.hWnd)
	
	def SetUpVisual(self, path):
		self.normal_visual = path
		self.LoadImage(self.normal_visual)

	def SetOverVisual(self, path):
		self.over_visual = path
	
	def SetDownVisual(self, path):
		self.down_visual = path
	
	def SetText(self, text, height = 4):
		if not self.ButtonText:
			textLine = TextLine()
			textLine.SetParent(self)
			textLine.SetPosition(self.GetWidth()/2, self.GetHeight()/2)
			textLine.SetVerticalAlignCenter()
			textLine.SetHorizontalAlignCenter()
			textLine.Show()
			self.ButtonText = textLine

		self.ButtonText.SetText(text)
	
	def OnMouseLeftButtonDown(self):
		self.LoadImage(self.down_visual)
		
		try:
			if self.eventDict.__contains__("MOUSE_LEFT_DOWN"):
				self.eventDict["MOUSE_LEFT_DOWN"](* self.argDict["MOUSE_LEFT_DOWN"])
		except Exception:
			pass

	def OnMouseLeftButtonUp(self):
		if self.normal_visual:
			self.LoadImage(self.normal_visual)

		try:
			# FIX: Use clickEventFunc instead of eventFunc dict
			if self.clickEventFunc:
				apply(self.clickEventFunc, self.clickEventArgs)
		except Exception as e:
			import dbg
			dbg.TraceError("ExpandedImageBoxButton.OnMouseLeftButtonUp error: %s" % str(e))

		Window.OnMouseLeftButtonUp(self)

	def OnMouseOverIn(self):
		self.LoadImage(self.over_visual)
		
		try:
			if self.eventFunc["MOUSE_OVER_IN"]:
				apply(self.eventFunc["MOUSE_OVER_IN"], self.eventArgs["MOUSE_OVER_IN"])
			
			if self.eventDict.has_key("MOUSE_OVER_IN"):
				if self.eventArgs["MOUSE_OVER_IN"]:
					apply(self.eventDict["MOUSE_OVER_IN"], self.eventArgs["MOUSE_OVER_IN"])
				else:
					self.eventDict["MOUSE_OVER_IN"]()
		except Exception:
			pass
	
	def OnMouseOverOut(self):
		self.LoadImage(self.normal_visual)
		
		try:
			if self.eventFunc["MOUSE_OVER_OUT"]:
				apply(self.eventFunc["MOUSE_OVER_OUT"], self.eventArgs["MOUSE_OVER_OUT"])

			if self.eventDict.has_key("MOUSE_OVER_OUT"):
				if self.eventArgs["MOUSE_OVER_OUT"]:
					apply(self.eventDict["MOUSE_OVER_OUT"], self.eventArgs["MOUSE_OVER_OUT"])
				else:
					self.eventDict["MOUSE_OVER_OUT"]()
		except Exception:
			pass


class NewBpScrollBar(Window):

	SCROLLBAR_WIDTH = 12
	SCROLLBAR_MIDDLE_HEIGHT = 1
	SCROLLBAR_BUTTON_WIDTH = 17
	SCROLLBAR_BUTTON_HEIGHT = 17
	SCROLL_BTN_XDIST = 0
	SCROLL_BTN_YDIST = 2

	class MiddleBar(DragButton):
		def __init__(self):
			DragButton.__init__(self)
			self.AddFlag("movable")

			self.SetWindowName("NONAME_ScrollBar_MiddleBar")

		def MakeImage(self):
			top = ImageBox()
			top.SetParent(self)
			top.LoadImage("d:/ymir work/ui/pattern/slimscroll/ScrollBar_Middle_Top_bottom.tga")
			top.AddFlag("not_pick")
			top.SetPosition(0, 0)
			top.Show()
			topScale = ExpandedImageBox()
			topScale.SetParent(self)
			topScale.SetPosition(0, top.GetHeight())
			topScale.LoadImage("d:/ymir work/ui/pattern/slimscroll/ScrollBar_Middle_TopScale.tga")
			topScale.AddFlag("not_pick")
			topScale.Show()

			bottom = ImageBox()
			bottom.SetParent(self)
			bottom.LoadImage("d:/ymir work/ui/pattern/slimscroll/ScrollBar_Middle_Top_bottom.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()
			bottomScale = ExpandedImageBox()
			bottomScale.SetParent(self)
			bottomScale.LoadImage("d:/ymir work/ui/pattern/slimscroll/ScrollBar_Middle_TopScale.tga")
			bottomScale.AddFlag("not_pick")
			bottomScale.Show()

			middle = ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage("d:/ymir work/ui/pattern/slimscroll/ScrollBar_Middle_Middle.tga")
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
			DragButton.SetSize(self, 10, height)

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
		Window.__init__(self)

		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = None
		self.eventArgs = None
		self.lockFlag = False

		self.CreateScrollBar()
		self.SetScrollBarSize(0)

		self.scrollStep = 0.20
		self.SetWindowName("NONAME_ScrollBar")

	def __del__(self):
		Window.__del__(self)

	def CreateScrollBar(self):
		middleImage = ExpandedImageBox()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, 1)
		middleImage.LoadImage("d:/ymir work/ui/pattern/slimscroll/SlimScrollBar_Middle.tga")
		middleImage.Show()
		self.middleImage = middleImage

		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(0) # set min height
		self.middleBar = middleBar

	def Destroy(self):
		self.eventScroll = None
		self.eventArgs = None

	def SetScrollEvent(self, event, *args):
		self.eventScroll = event
		self.eventArgs = args

	def SetMiddleBarSize(self, pageScale):
		self.middleBar.SetSize(int(pageScale * float(self.GetHeight() - self.SCROLL_BTN_YDIST*2)))
		realHeight = self.GetHeight() - self.SCROLL_BTN_YDIST*2 - self.middleBar.GetHeight()
		self.pageSize = realHeight

	def SetScrollBarSize(self, height):
		self.SetSize(self.SCROLLBAR_WIDTH, height)

		self.pageSize = height - self.SCROLL_BTN_YDIST*2 - self.middleBar.GetHeight()

		middleImageScale = float((height - self.SCROLL_BTN_YDIST*2) - self.middleImage.GetHeight()) / float(self.middleImage.GetHeight())
		self.middleImage.SetRenderingRect(0, 0, 0, middleImageScale)

		self.middleBar.SetRestrictMovementArea(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST, \
			self.middleBar.GetWidth(), height - self.SCROLL_BTN_YDIST * 2)
		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST)

	def SetScrollStep(self, step):
		self.scrollStep = step

	def GetScrollStep(self):
		return self.scrollStep

	def GetPos(self):
		return self.curPos

	def OnUp(self):
		self.SetPos(self.curPos-self.scrollStep)

	def OnDown(self):
		self.SetPos(self.curPos+self.scrollStep)

	def SetPos(self, pos, moveEvent = True):
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

	def OnMouseWheel(self, nLen):
		if nLen > 0:
			self.OnUp()
		else:
			self.OnDown()

class ImageBoxAeldra(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

		self.eventDict={}
		self.argDict={}
		self.name=""
		self.eventFunc = {"mouse_click" : None, "mouse_over_in" : None, "mouse_over_out" : None}
		self.eventArgs = {"mouse_click" : None, "mouse_over_in" : None, "mouse_over_out" : None}

	def __del__(self):
		Window.__del__(self)
		self.eventFunc = None
		self.eventArgs = None

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterImageBox(self, layer)

	def LoadImage(self, imageName):
		self.name=imageName
		wndMgr.LoadImage(self.hWnd, imageName)

		if len(self.eventDict)!=0:
			print "LOAD IMAGE", self, self.eventDict

	def SetScale(self, xScale, yScale):
		wndMgr.SetScale(self.hWnd, xScale, yScale)

	def SetProcent(self, fProcent): # UPDATE 0.4 i think idk bro 
		wndMgr.SetImageProcent(self.hWnd, fProcent)

	def GetImageName(self):
		return self.name

	def SetAlpha(self, alpha):
		wndMgr.SetDiffuseColor(self.hWnd, 1.0, 1.0, 1.0, alpha)

	def GetWidth(self):
		return wndMgr.GetWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetHeight(self.hWnd)

	def __OnMouseOverIn(self):
		try:
			apply(self.eventDict["MOUSE_OVER_IN"], self.argDict["MOUSE_OVER_IN"])
		except KeyError:
			pass

	def __OnMouseOverOut(self):
		try:
			apply(self.eventDict["MOUSE_OVER_OUT"], self.argDict["MOUSE_OVER_OUT"])
		except KeyError:
			pass

	def OnMouseLeftButtonDown(self):
		if self.eventDict.has_key("MOUSE_LEFT_DOWN"):
			apply(self.eventDict["MOUSE_LEFT_DOWN"], self.argDict["MOUSE_LEFT_DOWN"])

	def OnMouseLeftButtonUp(self):
		if self.eventDict.has_key("MOUSE_LEFT_UP"):
			apply(self.eventDict["MOUSE_LEFT_UP"], self.argDict["MOUSE_LEFT_UP"])
		if self.eventFunc["mouse_click"] :
			apply(self.eventFunc["mouse_click"], self.eventArgs["mouse_click"])

	def OnMouseLeftButtonDoubleClick(self):
		if self.eventDict.has_key("MOUSE_LEFT_DOUBLE_CLICK"):
			apply(self.eventDict["MOUSE_LEFT_DOUBLE_CLICK"], self.argDict["MOUSE_LEFT_DOUBLE_CLICK"])

	def SetStringEvent(self, event, func, *args):
		self.eventDict[event]=func
		self.argDict[event]=args

	def SAFE_SetStringEvent(self, event, func, *args):
		self.eventDict[event]=__mem_func__(func)
		self.argDict[event]=args

	def SetEvent(self, func, *args) :
		result = self.eventFunc.has_key(args[0])		
		if result :
			self.eventFunc[args[0]] = func
			self.eventArgs[args[0]] = args
		else :
			print "[ERROR] ui.py SetEvent, Can`t Find has_key : %s" % args[0]

	def OnMouseOverIn(self) :
		if self.eventFunc["mouse_over_in"] :
			apply(self.eventFunc["mouse_over_in"], self.eventArgs["mouse_over_in"])
		else:
			self.__OnMouseOverIn()

	def OnMouseOverOut(self) :
		if self.eventFunc["mouse_over_out"] :
			apply(self.eventFunc["mouse_over_out"], self.eventArgs["mouse_over_out"])
		else :
			self.__OnMouseOverOut()

	def SetDiffuseColor(self, r, g, b, a):
		wndMgr.SetDiffuseColor(self.hWnd, r, g, b, a)

class OutlineWindow(Window):
	PATTERN_PATH = "d:/ymir work/ui/pattern/border_a/"

	def __init__(self):
		Window.__init__(self)
		self.__Initialize()

	def __del__(self):
		Window.__del__(self)
		self.__Initialize()

	def __Initialize(self):
		self.pattern_x_count = 0
		self.pattern_y_count = 0
		self.left_top_img = None
		self.right_top_img = None
		self.left_bottom_img = None
		self.right_bottom_img = None
		self.top_center_img = None
		self.left_center_img = None
		self.right_center_img = None
		self.bottom_center_img = None
		self.center_img = None

	def MakeOutlineWindow(self, window_width, window_height):			
		self.AddFlag("ltr")
		self.AddFlag("attach")
		self.SetWindowName("outline_window")
		self.SetSize(window_width, window_height)
		
		self.pattern_x_count = (window_width - 32) / 16
		self.pattern_y_count = (window_height - 32) / 16
		
		self.left_top_img = ImageBox()
		self.left_top_img.SetParent(self)
		self.left_top_img.LoadImage(OutlineWindow.PATTERN_PATH + "border_A_left_top.tga")
		self.left_top_img.SetPosition(0, 0)
		self.left_top_img.Show()

		self.right_top_img = ImageBox()
		self.right_top_img.SetParent(self)
		self.right_top_img.LoadImage(OutlineWindow.PATTERN_PATH + "border_A_right_top.tga")
		self.right_top_img.SetPosition(window_width - 16, 0)
		self.right_top_img.Show()

		self.left_bottom_img = ImageBox()
		self.left_bottom_img.SetParent(self)
		self.left_bottom_img.LoadImage(OutlineWindow.PATTERN_PATH + "border_A_left_bottom.tga")
		self.left_bottom_img.SetPosition(0, window_height - 16)
		self.left_bottom_img.Show()

		self.right_bottom_img = ImageBox()
		self.right_bottom_img.SetParent(self)
		self.right_bottom_img.LoadImage(OutlineWindow.PATTERN_PATH + "border_A_right_bottom.tga")
		self.right_bottom_img.SetPosition(window_width - 16, window_height - 16)
		self.right_bottom_img.Show()

		self.top_center_img = ExpandedImageBox()
		self.top_center_img.SetParent(self)
		self.top_center_img.LoadImage(OutlineWindow.PATTERN_PATH + "border_A_top.tga")
		self.top_center_img.SetPosition(16, 0)
		self.top_center_img.SetRenderingRect(0.0, 0.0, self.pattern_x_count, 0.0)
		self.top_center_img.Show()

		self.left_center_img = ExpandedImageBox()
		self.left_center_img.SetParent(self)
		self.left_center_img.LoadImage(OutlineWindow.PATTERN_PATH + "border_A_left.tga")
		self.left_center_img.SetPosition(0, 16)
		self.left_center_img.SetRenderingRect(0.0, 0.0, 0.0, self.pattern_y_count)
		self.left_center_img.Show()

		self.right_center_img = ExpandedImageBox()
		self.right_center_img.SetParent(self)
		self.right_center_img.LoadImage(OutlineWindow.PATTERN_PATH + "border_A_right.tga")
		self.right_center_img.SetPosition(window_width - 16, 16)
		self.right_center_img.SetRenderingRect(0.0, 0.0, 0.0, self.pattern_y_count)
		self.right_center_img.Show()

		self.bottom_center_img = ExpandedImageBox()
		self.bottom_center_img.SetParent(self)
		self.bottom_center_img.LoadImage(OutlineWindow.PATTERN_PATH + "border_A_bottom.tga")
		self.bottom_center_img.SetPosition(16, window_height - 16)
		self.bottom_center_img.SetRenderingRect(0.0, 0.0, self.pattern_x_count, 0.0)
		self.bottom_center_img.Show()

		self.center_img = ExpandedImageBox()
		self.center_img.SetParent(self)
		self.center_img.LoadImage(OutlineWindow.PATTERN_PATH + "border_A_center.tga")
		self.center_img.SetPosition(16, 16)
		self.center_img.SetRenderingRect(0.0, 0.0, self.pattern_x_count, self.pattern_y_count)
		self.center_img.Show()

		# self.Show()


def MakeBoardWithTitleBar(parent, flag, title, closeEvent, width, height):
	board = BoardWithTitleBar()
	board.SetParent(parent)
	board.SetSize(width, height)
	board.AddFlag(flag)
	board.SetTitleName(title)
	board.SetCloseEvent(closeEvent)
	board.Show()
	return board

def MakeImageBox(parent, name, x, y):
	image = ImageBox()

	if parent:
		image.SetParent(parent)

	image.LoadImage(name)
	image.SetPosition(x, y)
	image.Show()
	return image

def MakeExpandedImageBox(parent, name, x, y, flag = ""):
	image = ExpandedImageBox()
	image.SetParent(parent)
	image.LoadImage(name)
	image.SetPosition(x, y)
	if flag != "":
		image.AddFlag(flag)
	image.Show()
	return image

def MakeImageBoxAE(parent, name, x, y, flag = ""):
	image = ImageBoxAeldra()
	image.SetParent(parent)
	image.LoadImage(name)
	image.SetPosition(x, y)

	if flag != "":
		image.AddFlag(flag)

	image.Show()

	return image

def MakeTextLine(parent, horizontalAlign = True, verticalAlgin = True, x = 0, y = 0):
	textLine = TextLine()
	textLine.SetParent(parent)
	
	if horizontalAlign == True:
		textLine.SetWindowHorizontalAlignCenter()
		
	if verticalAlgin == True:
		textLine.SetWindowVerticalAlignCenter()
		
	textLine.SetHorizontalAlignCenter()
	textLine.SetVerticalAlignCenter()
	
	if x != 0 and y != 0:
		textLine.SetPosition(x, y)
		
	textLine.Show()
	return textLine
	
def MakeTextLineNew(parent, x, y, text):
	textLine = TextLine()
	textLine.SetParent(parent)
	textLine.SetPosition(x, y)
	textLine.SetText(text)
	textLine.SetPackedFontColor(0xFFdad5ac)
	textLine.Show()
	return textLine

def MakeTextLineColor(parent, x, y, text, color):
	textLine = TextLine()
	textLine.SetParent(parent)
	textLine.SetPosition(x, y)
	textLine.SetText(text)
	textLine.SetPackedFontColor(color)#dream
	textLine.Show()
	return textLine


def MakeButtonNew(parent, x, y, text, path, up, over, down):
	button = Button()
	button.SetParent(parent)
	button.SetPosition(x, y)
	button.SetUpVisual(path + up)
	button.SetOverVisual(path + over)
	button.SetDownVisual(path + down)
	button.SetText(text)
	button.UpdateRect()
	button.Show()
	return button


def MakeWindow(window, parent, windowFlags, windowPos, windowArgument = "", windowPositionRule = "", windowSize = (-1, -1), windowFontName = -1, windowColor = 0, windowIsOutline = False):
	if parent: window.SetParent(parent)
	for flag in windowFlags: window.AddFlag(flag)
	window.SetPosition(*windowPos)
	if windowSize != (-1, -1): window.SetSize(*windowSize)
	if windowColor != 0:
		if isinstance(window, TextLine): window.SetPackedFontColor(windowColor)
	if windowIsOutline:
		if isinstance(window, TextLine): window.SetOutline()
	if windowArgument != "" and windowArgument != None:
		if isinstance(window, TextLine):
			if windowFontName != -1: window.SetFontName(windowFontName)
			window.SetText(windowArgument)
		elif isinstance(window, NumberLine):
			window.SetNumber(windowArgument)
		elif isinstance(window, Line) or isinstance(window, Bar) or isinstance(window, Box):
			window.SetColor(windowArgument)
		elif isinstance(window, Button) or isinstance(window, RadioButton) or isinstance(window, ToggleButton):
			if isinstance(windowArgument, list):
				window.SetUpVisual(windowArgument[0])
				window.SetOverVisual(windowArgument[1] if len(windowArgument) >= 2 else windowArgument[0])
				window.SetDownVisual(windowArgument[2] if len(windowArgument) >= 3 else windowArgument[0])
				if len(windowArgument) == 4: window.SetDisableVisual(windowArgument[3])
		elif isinstance(window, ExpandedImageBox) or isinstance(window, ImageBox):
			window.LoadImage(windowArgument)
	if windowPositionRule:
		splitList = windowPositionRule.split(":")
		if len(splitList) == 2:
			(alignType, mode) = (splitList[0], splitList[1])
			if alignType == "all":
				window.SetHorizontalAlignCenter()
				window.SetVerticalAlignCenter()
				window.SetWindowHorizontalAlignCenter()
				window.SetWindowVerticalAlignCenter()
			elif alignType == "horizontal":
				if isinstance(window, TextLine):
					if mode == "center": window.SetHorizontalAlignCenter()
					elif mode == "right": window.SetHorizontalAlignRight()
					elif mode == "left": window.SetHorizontalAlignLeft()
				else:
					if mode == "center": window.SetWindowHorizontalAlignCenter()
					elif mode == "right": window.SetWindowHorizontalAlignRight()
					elif mode == "left": window.SetWindowHorizontalAlignLeft()
			elif alignType == "vertical":
				if isinstance(window, TextLine):
					if mode == "center": window.SetVerticalAlignCenter()
					elif mode == "top": window.SetVerticalAlignTop()
					elif mode == "bottom": window.SetVerticalAlignBottom()
				else:
					if mode == "top": window.SetWindowVerticalAlignTop()
					elif mode == "center": window.SetWindowVerticalAlignCenter()
					elif mode == "bottom": window.SetWindowVerticalAlignBottom()
	window.Show()
	return window


class Table(Window):
	# colors = [lineColor, headerBgColor, rowBgColor, headerTextColor, defaultCellTextColor]
	def __init__(self, width, head_height, colors):
		Window.__init__(self, "UI")
		self.width = width
		self.head_height = head_height
		self.table_height = head_height
		self.colors = colors
		self.headers = []
		self.widths = []
		self.row_heights = []
		self._tchildren = {}
		self.SetSize(width, head_height)

	def __del__(self):
		Window.__del__(self)

	def Destroy(self):
		self._tchildren = {}

	def CreateTitleBar(self):
		self._tchildren["title_base"] = MakeWindow(Bar(), self, ["not_pick"], (0, 0), self.colors[1], "", (self.width, self.head_height))
		self._tchildren["title_tl"] = MakeWindow(Line(), self, ["not_pick"], (0, 0), self.colors[0], "", (self.width, 0))
		self._tchildren["title_bl"] = MakeWindow(Line(), self, ["not_pick"], (0, self.head_height), self.colors[0], "", (self.width, 0))
		self._tchildren["title_ll"] = MakeWindow(Line(), self, ["not_pick"], (0, 0), self.colors[0], "", (0, self.head_height))
		self._tchildren["title_rl"] = MakeWindow(Line(), self, ["not_pick"], (self.width, 0), self.colors[0], "", (0, self.head_height))

	def set_columns(self, headers, widths):
		if len(headers) != len(widths):
			return
		self.headers = headers
		self.widths = widths
		self.CreateTitleBar()
		count = len(headers)
		cumulative_width = 0
		for i in xrange(count):
			wnd = MakeWindow(Window(), self._tchildren["title_base"], ["not_pick"], (cumulative_width, 0), "", "", (self.widths[i], self._tchildren["title_base"].GetHeight()))
			self._tchildren["title_w%d" % (i)] = wnd
			self._tchildren["title_t%d" % (i)] = MakeWindow(TextLine(), wnd, ["not_pick"], (0, 0), self.headers[i], "all:center", (-1, -1), -1, self.colors[3], True)
			if i < count - 1:
				self._tchildren["title_s%d" % (i)] = MakeWindow(Line(), wnd, ["not_pick"], (self.widths[i], 0), self.colors[0], "", (0, wnd.GetHeight()))
			cumulative_width += self.widths[i]

	# cell_icons: optional list parallel to data. Each entry is None (no icon),
	# an int item vnum, or a direct image-path string. An icon cell renders the
	# image at the leading edge (right edge for right-aligned cells, so RTL works)
	# with the text beside it. icon_size forces a square side; 0 = fit row height.
	# row_bg: optional per-row background color override (0 = use table default),
	# e.g. for zebra striping.
	def add_row(self, data, height, cell_colors = None, cell_aligns = None, cell_icons = None, icon_size = 0, row_bg = 0):
		if len(data) != len(self.widths):
			return
		row_index = len(self.row_heights)
		self.row_heights.append(height)
		cumulative_width = 0
		y_position = self.head_height + sum(self.row_heights[:row_index])
		bg_color = row_bg if row_bg != 0 else self.colors[2]
		for i, value in enumerate(data):
			color = self.colors[4]
			if cell_colors and i < len(cell_colors) and cell_colors[i] != 0:
				color = cell_colors[i]
			align = "all:center"
			if cell_aligns and i < len(cell_aligns) and cell_aligns[i]:
				align = cell_aligns[i]
			icon = cell_icons[i] if (cell_icons and i < len(cell_icons)) else None
			wnd = MakeWindow(Window(), self, ["not_pick"], (cumulative_width, y_position), "", "", (self.widths[i], height))
			self._tchildren["row_%d_b%d" % (row_index, i)] = MakeWindow(Bar(), wnd, ["not_pick"], (0, 0), bg_color, "", (self.widths[i], height))
			self._tchildren["row_%d_c%d" % (row_index, i)] = wnd
			# Centered text can use MakeWindow's "all:center" rule directly; any
			# left/right-aligned cell (or any icon cell) needs explicit padding +
			# vertical centering, which MakeWindow's "horizontal:*" rule does NOT do.
			if icon or align != "all:center":
				self.__make_aligned_cell(row_index, i, wnd, value, color, align, icon, height, icon_size)
			else:
				self._tchildren["row_%d_t%d" % (row_index, i)] = MakeWindow(TextLine(), wnd, ["not_pick"], (0, 0), value, align, (-1, -1), -1, color, True)
			if i < len(self.widths) - 1:
				self._tchildren["row_%d_s%d" % (row_index, i)] = MakeWindow(Line(), wnd, ["not_pick"], (self.widths[i], 0), self.colors[0], "", (0, height))
			cumulative_width += self.widths[i]
		hline_y_position = self.head_height + sum(self.row_heights[:row_index + 1])
		self._tchildren["row_%d_hline" % (row_index)] = MakeWindow(Line(), self, ["not_pick"], (0, hline_y_position), self.colors[0], "", (self.width, 0))
		self.table_height = self.head_height + sum(self.row_heights)
		self.SetSize(self.width, self.table_height)
		self._tchildren["title_ll"].SetSize(0, self.table_height)
		self._tchildren["title_rl"].SetSize(0, self.table_height)

	# Renders a left/right-aligned, vertically-centered text cell, optionally with
	# an icon at the leading edge. Used for any non-center cell so alignment and
	# vertical centering stay consistent across icon and text-only cells.
	def __make_aligned_cell(self, row_index, i, wnd, value, color, align, icon, height, icon_size):
		PAD = 4
		cell_width = self.widths[i]
		rightAlign = ("right" in align)
		drawW = 0

		if icon:
			side = icon_size if icon_size > 0 else (height - 4)
			iconImg = ExpandedImageBox()
			iconImg.SetParent(wnd)
			iconImg.AddFlag("not_pick")
			if isinstance(icon, (int, long)):
				item.SelectItem(icon)
				iconImg.LoadImage(item.GetIconImageFileName())
			else:
				iconImg.LoadImage(icon)

			ow, oh = iconImg.GetWidth(), iconImg.GetHeight()
			if ow > 0 and oh > 0:
				scale = min(float(side) / ow, float(side) / oh)
				iconImg.SetScale(scale, scale)
				drawW, drawH = int(ow * scale), int(oh * scale)
			else:
				drawW = drawH = side

			if rightAlign:
				iconImg.SetPosition(cell_width - PAD - drawW, (height - drawH) / 2)
			else:
				iconImg.SetPosition(PAD, (height - drawH) / 2)
			iconImg.Show()
			self._tchildren["row_%d_i%d" % (row_index, i)] = iconImg

		iconSpan = (drawW + PAD) if drawW else 0
		textLine = TextLine()
		textLine.SetParent(wnd)
		textLine.AddFlag("not_pick")
		textLine.SetPackedFontColor(color)
		textLine.SetOutline()
		textLine.SetText(value)
		textLine.SetVerticalAlignCenter()
		if rightAlign:
			textLine.SetHorizontalAlignLeft()
			textLine.SetPosition(cell_width - PAD - iconSpan, height / 2)
		else:
			textLine.SetHorizontalAlignLeft()
			textLine.SetPosition(PAD + iconSpan, height / 2)
		textLine.Show()
		self._tchildren["row_%d_t%d" % (row_index, i)] = textLine



if app.ENABLE_WINDOW_RESIZE:
	def IsDependOnScreen(expr):
		if not isinstance(expr, Expr):
			return False

		if expr.name in ("SCREEN_WIDTH", "SCREEN_HEIGHT"):
			return True

		return (IsDependOnScreen(expr.left) or IsDependOnScreen(expr.right))

	def ScanValue(value):
		if isinstance(value, Expr):
			return IsDependOnScreen(value)
		elif isinstance(value, (tuple, list)):
			for v in value:
				if ScanValue(v):
					return True
		return False

	def CheckPair(dic, x, y):
		x = dic.get(x)
		y = dic.get(y)

		if x is None or y is None:
			return None

		if (ScanValue(x) or ScanValue(y)):
			return (x, y)

		return None

	def ExtractWindowScaling(dic):
		scaling = {}

		position = CheckPair(dic, "x", "y")
		if position:
			scaling["position"] = position

		size = CheckPair(dic, "width", "height")
		if size:
			scaling["size"] = size

		scale = CheckPair(dic, "x_scale", "y_scale")
		if scale:
			scaling["scale"] = scale

		rect = dic.get("rect")
		if rect and ScanValue(rect):
			scaling["rect"] = rect

		return scaling

	def SandboxInt(x):
		if isinstance(x, Expr):
			return Expr(op='int', left=x)
		return int(x)

	def SandboxFloat(x):
		if isinstance(x, Expr):
			return Expr(op='float', left=x)
		return float(x)