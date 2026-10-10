# coding: latin_1

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr

import ui
import grp

import wndMgr

import osfinfo

class TextBar(ui.Window):
	def __init__(self, width, height):
		ui.Window.__init__(self)
		self.handle = grp.CreateTextBar(width, height)

	def __del__(self):
		ui.Window.__del__(self)
		grp.DestroyTextBar(self.handle)

	def ClearBar(self):
		grp.ClearTextBar(self.handle)

	def SetClipRect(self, x1, y1, x2, y2):
		grp.SetTextBarClipRect(self.handle, x1, y1, x2, y2)

	def TextOut(self, x, y, text):
		grp.TextBarTextOut(self.handle, x, y, text)

	def OnRender(self):
		x, y = self.GetGlobalPosition()
		grp.RenderTextBar(self.handle, x, y)

	def SetTextColor(self, r, g, b):
		grp.TextBarSetTextColor(self.handle, r, g, b)

	def GetTextExtent(self, text):
		return grp.TextBarGetTextExtent(self.handle, text)
	if app.ENABLE_WINDOW_RESIZE:
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
					elif k == "clipRect":
						self.SetClipRect(int(v[0]), int(v[1]), int(v[2]), int(v[3]))

class TipBoard(ui.Bar):
	SCROLL_WAIT_TIME = 3.0
	TIP_DURATION = 5.0
	STEP_HEIGHT = 17

	def __init__(self):
		ui.Bar.__init__(self)

		self.AddFlag("not_pick")
		self.tipList = []
		self.curPos = 0
		self.dstPos = 0
		self.nextScrollTime = 0

		self.width = 370

		self.SetPosition(0, 70)

		self.SetSize(370, 20)

		self.SetColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.5))
		self.SetWindowHorizontalAlignCenter()

		self.__CreateTextBar()

	def __del__(self):
		ui.Bar.__del__(self)

	def __CreateTextBar(self):
		x, y = self.GetGlobalPosition()

		self.textBar = TextBar(370, 300)

		self.textBar.SetParent(self)
		self.textBar.SetPosition(3, 5)

		self.textBar.SetClipRect(0, y, wndMgr.GetScreenWidth(), y+18)
		if app.ENABLE_WINDOW_RESIZE:
			self.textBar.SetResizeDic({"clipRect" : (0, y, Expr("SCREEN_WIDTH"), y+18)})

		self.textBar.Show()

	def __CleanOldTip(self):
		leaveList = []
		for tip in self.tipList:
			madeTime = tip[0]
			if app.GetTime() - madeTime > self.TIP_DURATION:
				pass
			else:
				leaveList.append(tip)

		self.tipList = leaveList

		if not leaveList:
			self.textBar.ClearBar()
			self.Hide()
			return

		self.__RefreshBoard()

	def __RefreshBoard(self):
		self.textBar.ClearBar()

		index = 0
		for tip in self.tipList:
			text = tip[1]
			self.textBar.TextOut(0, index*self.STEP_HEIGHT, text)
			index += 1

	def SetTip(self, text):
		if not app.IsVisibleNotice():
			return

		# YMD.2019.12.01.Owsap - Color code bug fix
		if osfinfo.FILTER_EMOJI_NOTICE == True and osfinfo.IsEmojiFilter(text):
			return

		text = osfinfo.StripColor(text)

		curTime = app.GetTime()
		self.tipList.append((curTime, text))
		self.__RefreshBoard()

		self.nextScrollTime = app.GetTime() + 1.0

		if not self.IsShow():
			self.curPos = -self.STEP_HEIGHT
			self.dstPos = -self.STEP_HEIGHT
			self.textBar.SetPosition(3, 5 - self.curPos)
			self.Show()

	def OnUpdate(self):
		if not self.tipList:
			self.Hide()
			return

		if app.GetTime() > self.nextScrollTime:
			self.nextScrollTime = app.GetTime() + self.SCROLL_WAIT_TIME

			self.dstPos = self.curPos + self.STEP_HEIGHT

		if self.dstPos > self.curPos:
			self.curPos += 1
			self.textBar.SetPosition(3, 5 - self.curPos)

			if self.curPos > len(self.tipList)*self.STEP_HEIGHT:
				self.curPos = -self.STEP_HEIGHT
				self.dstPos = -self.STEP_HEIGHT

				self.__CleanOldTip()

class BigTextBar(TextBar):
	def __init__(self, width, height, fontSize):
		ui.Window.__init__(self)
		self.handle = grp.CreateBigTextBar(width, height, fontSize)

	def __del__(self):
		ui.Window.__del__(self)
		grp.DestroyTextBar(self.handle)

class BigBoard(ui.Bar):
	SCROLL_WAIT_TIME = 5.0
	TIP_DURATION = 10.0
	FONT_WIDTH = 18
	FONT_HEIGHT = 18
	LINE_WIDTH = 500
	LINE_HEIGHT = FONT_HEIGHT + 5
	STEP_HEIGHT = LINE_HEIGHT * 2
	LINE_CHANGE_LIMIT_WIDTH = 350

	FRAME_IMAGE_FILE_NAME_LIST = [
		"d:/ymir work/ui/interface/oxevent/frame_0.sub",
		"d:/ymir work/ui/interface/oxevent/frame_1.sub",
		"d:/ymir work/ui/interface/oxevent/frame_2.sub",
	]

	FRAME_IMAGE_STEP = 256

	FRAME_BASE_X = -20
	FRAME_BASE_Y = -12

	def __init__(self):
		ui.Bar.__init__(self)

		self.AddFlag("not_pick")
		self.tipList = []
		self.curPos = 0
		self.dstPos = 0
		self.nextScrollTime = 0

		self.SetPosition(0, 150)
		self.SetSize(512, 55)
		self.SetColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.5))
		self.SetWindowHorizontalAlignCenter()

		self.__CreateTextBar()
		self.__LoadFrameImages()

	def __LoadFrameImages(self):
		x = self.FRAME_BASE_X
		y = self.FRAME_BASE_Y
		self.imgList = []
		for imgFileName in self.FRAME_IMAGE_FILE_NAME_LIST:
			self.imgList.append(self.__LoadImage(x, y, imgFileName))
			x += self.FRAME_IMAGE_STEP

	def __LoadImage(self, x, y, fileName):
		img = ui.ImageBox()
		img.SetParent(self)
		img.AddFlag("not_pick")
		img.LoadImage(fileName)
		img.SetPosition(x, y)
		img.Show()
		return img

	def __del__(self):
		ui.Bar.__del__(self)

	def __CreateTextBar(self):
		x, y = self.GetGlobalPosition()

		self.textBar = BigTextBar(self.LINE_WIDTH, 300, self.FONT_HEIGHT)
		self.textBar.SetParent(self)
		self.textBar.SetPosition(6, 8)
		self.textBar.SetTextColor(242, 231, 193)
		self.textBar.SetClipRect(0, y+8, wndMgr.GetScreenWidth(), y+8+self.STEP_HEIGHT)
		if app.ENABLE_WINDOW_RESIZE:
			self.textBar.SetResizeDic({"clipRect" : (0, y+8, Expr("SCREEN_WIDTH"), y+8+self.STEP_HEIGHT)})
		self.textBar.Show()

	def __CleanOldTip(self):
		curTime = app.GetTime()
		leaveList = []
		for madeTime, text in self.tipList:
			if curTime + self.TIP_DURATION <= madeTime:
				leaveList.append(text)

		self.tipList = leaveList

		if not leaveList:
			self.textBar.ClearBar()
			self.Hide()
			return

		self.__RefreshBoard()

	def __RefreshBoard(self):
		self.textBar.ClearBar()

		if len(self.tipList) == 1:
			checkTime, text = self.tipList[0]
			(text_width, text_height) = self.textBar.GetTextExtent(text)
			self.textBar.TextOut((500-text_width)/2, (self.STEP_HEIGHT-8-text_height)/2, text)
		else:
			index = 0
			for checkTime, text in self.tipList:
				(text_width, text_height) = self.textBar.GetTextExtent(text)
				self.textBar.TextOut((500-text_width)/2, index*self.LINE_HEIGHT, text)
				index += 1

	def SetTip(self, text):
		if not app.IsVisibleNotice():
			return

		curTime = app.GetTime()
		self.__AppendText(curTime, text)
		self.__RefreshBoard()

		self.nextScrollTime = curTime + 1.0

		if not self.IsShow():
			self.curPos = -self.STEP_HEIGHT
			self.dstPos = -self.STEP_HEIGHT
			self.textBar.SetPosition(3, 8 - self.curPos)
			self.Show()

	def __AppendText(self, curTime, text):
		import dbg
		prevPos = 0
		while 1:
			# YMD.2019.12.01.Owsap - Color code bug fix
			if osfinfo.FILTER_EMOJI_NOTICE == True and osfinfo.IsEmojiFilter(text):
				return

			text = osfinfo.StripColor(text)

			curPos = text.find(" ", prevPos)
			if curPos < 0:
				break

			(text_width, text_height) = self.textBar.GetTextExtent(text[:curPos])
			if text_width > self.LINE_CHANGE_LIMIT_WIDTH:
				self.tipList.append((curTime, text[:prevPos]))
				self.tipList.append((curTime, text[prevPos:]))
				return

			prevPos = curPos + 1

		self.tipList.append((curTime, text))

	def OnUpdate(self):
		if not self.tipList:
			self.Hide()
			return

		if app.GetTime() > self.nextScrollTime:
			self.nextScrollTime = app.GetTime() + self.SCROLL_WAIT_TIME

			self.dstPos = self.curPos + self.STEP_HEIGHT

		if self.dstPos > self.curPos:
			self.curPos += 1
			self.textBar.SetPosition(3, 8 - self.curPos)

			if self.curPos > len(self.tipList)*self.LINE_HEIGHT:
				self.curPos = -self.STEP_HEIGHT
				self.dstPos = -self.STEP_HEIGHT

				self.__CleanOldTip()

if app.__RENEWAL_NOTICE__:
	# >>> SECTION BEGIN  Legacy typewriter TipBoardNew (replaced by the toast-stack rework) <<<
	# Players disliked the original renewal notice board: it typed each notice
	# out one character at a time, showed only one notice at a time (a burst of
	# notices became a slow backlog), grew its own width while typing, and
	# reverse-deleted the text on close. Preserved below so it can be revived
	# without git archaeology.
	# 	class TipBoardNew(ui.ThinBoard):
	# 		def __del__(self):
	# 			ui.ThinBoard.__del__(self)
	# 		def Destroy(self):
	# 			self.__tipList=[]
	# 			self.__min_width=0
	# 			self.__max_duration=0.0
	# 			self.__process_duration=0.0
	# 			self.__text_duration=0.0
	# 			self.__sleepTime=0.0
	# 			self.__currentTip=""
	# 			self.__textBar=None
	# 			self.processType = False
	# 			self.__open_max_duration =  0.0
	# 			self.__open_text_duration =  0.0
	# 			self.__close_max_duration =  0.0
	# 			self.__close_text_duration =  0.0
	# 			self.__click_close_max_duration =  0.0
	# 			self.__click_close_text_duration = 0.0
	# 		def __init__(self):
	# 			ui.ThinBoard.__init__(self)
	# 			self.SetWindowHorizontalAlignCenter()
	# 			self.Destroy()
	#
	# 			# config
	# 			self.__min_width=40
	# 			self.__min_height=30
	# 			self.__yPos=70
	#
	# 			self.processType = True
	#
	# 			self.__open_max_duration = 5.0
	# 			self.__open_text_duration = 0.30
	#
	# 			self.__close_max_duration = 1.0
	# 			self.__close_text_duration = 0.1
	#
	# 			self.__click_close_max_duration = 0.7
	# 			self.__click_close_text_duration = 0.05
	#
	# 			textBar = ui.TextLine()
	# 			textBar.SetParent(self)
	# 			textBar.AddFlag("not_pick")
	# 			textBar.SetOutline()
	# 			textBar.SetHorizontalAlignCenter()
	# 			textBar.SetVerticalAlignCenter()
	# 			textBar.SetWindowHorizontalAlignCenter()
	# 			textBar.SetWindowVerticalAlignCenter()
	# 			self.__textBar = textBar
	#
	# 			self.AddFlag("attach")
	# 			self.AddFlag("movable")
	# 			self.AddFlag("float")
	# 			self.SetMouseOverInEvent(ui.__mem_func__(self.OnMouseOverIn))
	# 			self.SetMouseOverOutEvent(ui.__mem_func__(self.OnMouseOverOut))
	# 			self.SetMouseLeftButtonUpEvent(ui.__mem_func__(self.OnMouseClick))
	# 		def OnMouseClick(self):
	# 			self.processType = False
	# 			self.__process_duration = app.GetTime()+self.__click_close_max_duration
	# 			self.__text_duration = (self.__click_close_text_duration/(len(self.__currentTip)))
	# 		def SetYPos(self, globalY):
	# 			self.__yPos = globalY
	# 		def OnMouseOverIn(self):
	# 			self.SetAlpha(0.5)
	# 		def OnMouseOverOut(self):
	# 			self.SetAlpha(1.0)
	# 		def SetDefaultData(self):
	# 			self.__sleepTime = 0.0
	# 			self.__text_duration = 0.0
	# 			self.__process_text = 0.0
	# 			self.__process_duration = 0.0
	# 			self.__currentTip = ""
	# 		def SetNewTipHideData(self):
	# 			self.__process_text = 0.0
	# 			self.__process_duration = app.GetTime()+self.__close_max_duration
	# 			self.__text_duration = (self.__close_text_duration/(len(self.__currentTip)))
	# 			self.processType = False
	# 		def SetNewTipOpenData(self, tipMessage):
	# 			self.__textBar.SetText("")
	# 			self.__process_text = 0.0
	# 			self.__process_duration = app.GetTime()+self.__open_max_duration
	# 			self.__currentTip = tipMessage
	# 			self.__text_duration = (self.__open_text_duration/(len(self.__currentTip)))
	# 			self.processType = True
	# 			self.SetPosition(0, self.__yPos)
	# 			if not self.__textBar.IsShow():
	# 				self.__textBar.Show()
	# 				self.__textBar.SetTop()
	# 				self.SetSize(self.__min_width+self.__textBar.GetTextSize()[0],self.__min_height)
	# 				self.SetPosition(0, self.__yPos)
	# 		def SetTip(self, newTip):
	# 			if self.__process_duration != 0.0:
	# 				self.__tipList.append(newTip)
	# 				return
	# 			self.__sleepTime = app.GetTime()+0.5
	# 			self.__alpha_duration = 0.0
	# 			self.__alphaValue = 0.0
	# 			self.__alpha = 0.5/30.0
	# 			self.SetNewTipOpenData(newTip)
	# 			self.Show()
	# 		def OnUpdate(self):
	# 			if self.__sleepTime >= app.GetTime():
	# 				if app.GetTime() >= self.__alpha_duration:
	# 					self.__alphaValue += self.__alpha
	# 					self.__alpha_duration = app.GetTime()+0.01
	# 					if self.processType:
	# 						self.SetAlpha(0.5+self.__alphaValue)
	# 					else:
	# 						self.SetAlpha(1.0-self.__alphaValue)
	# 				return
	# 			if self.__process_duration != 0:
	# 				lastDuration = self.__process_duration-app.GetTime()
	# 				if self.processType:
	# 					if app.GetTime() > self.__process_text:
	# 						self.__process_text = app.GetTime()+self.__text_duration
	# 						nextChar = len(self.__textBar.GetText())
	# 						if nextChar < len(self.__currentTip):
	# 							self.__textBar.SetText(self.__textBar.GetText()+self.__currentTip[nextChar])
	# 						if lastDuration <= 0.0:
	# 							self.SetNewTipHideData()
	# 				else:
	# 					if app.GetTime() > self.__process_text:
	# 						self.__process_text = app.GetTime()+self.__text_duration
	# 						nextChar = len(self.__textBar.GetText())
	# 						if nextChar > 0:
	# 							self.__textBar.SetText(self.__textBar.GetText()[:nextChar-1])
	#
	# 							if len(self.__textBar.GetText()) == 0:
	# 								if len(self.__tipList) > 0:
	# 									lastDuration = 0
	# 								else:
	# 									self.__sleepTime = app.GetTime()+0.5
	# 									self.__alpha_duration = 0.0
	# 									self.__alphaValue = 0.0
	# 									self.__alpha = 0.5/30.0
	# 						else:
	# 							lastDuration = 0.0
	# 					if lastDuration <= 0.0:
	# 						if len(self.__tipList)>0:
	# 							self.SetNewTipOpenData(self.__tipList[0])
	# 							del self.__tipList[0]
	# 							return
	# 						self.SetDefaultData()
	# 						self.Hide()
	# 				self.SetSize(self.__min_width+self.__textBar.GetTextSize()[0],self.__min_height)
	# 				self.SetPosition(0, self.__yPos)
	# <<< SECTION END  Legacy typewriter TipBoardNew <<<

	class NoticeToast(ui.ThinBoard):
		# A single auto-sized notice "card" (single line). Fade in/out, lifetime
		# and vertical stacking are driven by the TipBoardNew controller below,
		# so the card carries no OnUpdate of its own.
		# NOTE: single line on purpose. The engine's multi-line auto-wrap does
		# NOT render reliably for centred Arabic (RTL) text (it showed an empty
		# panel), whereas single-line shaping is solid -- same as the chat log.
		# The card hugs its text; an over-long notice is width-capped and simply
		# centre-overflows rather than wrapping.
		MAX_WIDTH = 900
		MIN_SCREEN_MARGIN = 40
		PAD_X = 15
		PAD_Y = 9
		TEXT_COLOR = (0.96, 0.91, 0.77)
		BG_ALPHA = 0.6

		def __init__(self):
			ui.ThinBoard.__init__(self)
			self.AddFlag("not_pick")
			self.AddFlag("float")

			self.cardWidth = NoticeToast.MAX_WIDTH
			self.cardHeight = NoticeToast.PAD_Y * 2
			self.targetY = 0.0
			self.curY = 0.0
			self.bornTime = 0.0
			self.holdEndTime = 0.0
			self.deadTime = 0.0
			self.__r = NoticeToast.TEXT_COLOR[0]
			self.__g = NoticeToast.TEXT_COLOR[1]
			self.__b = NoticeToast.TEXT_COLOR[2]

			textLine = ui.TextLine()
			textLine.SetParent(self)
			textLine.AddFlag("not_pick")
			textLine.SetOutline()
			textLine.SetHorizontalAlignCenter()
			textLine.SetVerticalAlignCenter()
			textLine.SetWindowHorizontalAlignCenter()
			textLine.SetWindowVerticalAlignCenter()
			textLine.Show()
			self.textLine = textLine

		def __del__(self):
			ui.ThinBoard.__del__(self)

		def Destroy(self):
			if self.textLine:
				self.textLine.Hide()
			self.textLine = None
			self.Hide()

		def Build(self, text):
			# Single line: size the card to the (reliably shaped) text and cap the
			# width so a very long notice centre-overflows instead of pushing the
			# card off-screen.
			self.textLine.SetText(text)
			textWidth, textHeight = self.textLine.GetTextSize()

			maxCardWidth = wndMgr.GetScreenWidth() - NoticeToast.MIN_SCREEN_MARGIN * 2
			if maxCardWidth > NoticeToast.MAX_WIDTH:
				maxCardWidth = NoticeToast.MAX_WIDTH

			cardWidth = textWidth + NoticeToast.PAD_X * 2
			if cardWidth > maxCardWidth:
				cardWidth = maxCardWidth

			self.cardWidth = cardWidth
			self.cardHeight = textHeight + NoticeToast.PAD_Y * 2
			self.SetSize(self.cardWidth, self.cardHeight)
			self.SetCardAlpha(0.0)

		def SetCardAlpha(self, alpha):
			if alpha < 0.0:
				alpha = 0.0
			elif alpha > 1.0:
				alpha = 1.0
			# Keep the dark panel translucent (never a solid black slab) and fade
			# the text WITH its outline: the outline colour does not follow the
			# fill, so without this the glyphs read as solid black while fading.
			self.SetAlpha(alpha * NoticeToast.BG_ALPHA)
			if self.textLine:
				self.textLine.SetPackedFontColor(grp.GenerateColor(self.__r, self.__g, self.__b, alpha))
				wndMgr.SetOutlineColor(self.textLine.GetWindowHandle(), grp.GenerateColor(0.0, 0.0, 0.0, alpha))

	class TipBoardNew(ui.Window):
		# Toast-stack notice board (replaces the old typewriter board). Every
		# server notice becomes an independent card that appears instantly with
		# its full, word-wrapped text, holds for a read-time proportional to its
		# length, then fades out on its own timer. Cards stack downward with the
		# newest on top, so a burst of notices is shown all at once instead of
		# being queued one-at-a-time.
		TOP_Y = 70
		GAP = 6
		MAX_TOASTS = 2
		HARD_MAX_TOASTS = 3
		FADE_IN = 0.18
		FADE_OUT = 0.40
		HOLD_MIN = 4.0
		HOLD_MAX = 9.0
		HOLD_PER_CHAR = 0.06
		SLIDE_SPEED = 14.0

		def __init__(self):
			ui.Window.__init__(self)
			self.__toasts = []
			self.__lastUpdate = 0.0
			self.SetPosition(0, 0)
			self.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())
			self.AddFlag("not_pick")
			if app.ENABLE_WINDOW_RESIZE:
				self.SetResizeDic({"size" : (Expr("SCREEN_WIDTH"), Expr("SCREEN_HEIGHT"))})

		def __del__(self):
			ui.Window.__del__(self)

		def Destroy(self):
			for toast in self.__toasts:
				toast.Destroy()
			self.__toasts = []
			self.Hide()

		if app.ENABLE_WINDOW_RESIZE:
			def OnResize(self):
				ui.Window.OnResize(self)
				self.__Reflow()

		def __ComputeHold(self, text):
			hold = TipBoardNew.HOLD_MIN + len(text) * TipBoardNew.HOLD_PER_CHAR
			if hold > TipBoardNew.HOLD_MAX:
				hold = TipBoardNew.HOLD_MAX
			return hold

		def __Reflow(self):
			y = TipBoardNew.TOP_Y
			for toast in self.__toasts:
				toast.targetY = float(y)
				y += toast.cardHeight + TipBoardNew.GAP

		def __EnforceCap(self, now):
			# Anything past the soft cap starts fading out immediately; the hard
			# cap removes the very oldest outright, so the stack can never grow
			# without bound during a notice flood.
			index = 0
			for toast in self.__toasts:
				if index >= TipBoardNew.MAX_TOASTS and toast.holdEndTime > now:
					toast.holdEndTime = now
					toast.deadTime = now + TipBoardNew.FADE_OUT
				index += 1
			while len(self.__toasts) > TipBoardNew.HARD_MAX_TOASTS:
				toast = self.__toasts.pop()
				toast.Destroy()

		def SetTip(self, text):
			if not text:
				return

			toast = NoticeToast()
			toast.SetParent(self)
			toast.Build(text)

			now = app.GetTime()
			toast.bornTime = now
			toast.holdEndTime = now + TipBoardNew.FADE_IN + self.__ComputeHold(text)
			toast.deadTime = toast.holdEndTime + TipBoardNew.FADE_OUT
			toast.curY = float(TipBoardNew.TOP_Y)
			toast.targetY = float(TipBoardNew.TOP_Y)

			# Newest card on top of the stack.
			self.__toasts.insert(0, toast)
			self.__EnforceCap(now)
			self.__Reflow()

			screenWidth = wndMgr.GetScreenWidth()
			toast.SetPosition(int((screenWidth - toast.cardWidth) / 2), int(toast.curY))
			toast.Show()

			self.__lastUpdate = now
			self.Show()
			self.SetTop()

		def OnUpdate(self):
			if not self.__toasts:
				self.Hide()
				return

			now = app.GetTime()
			dt = now - self.__lastUpdate
			self.__lastUpdate = now
			if dt < 0.0:
				dt = 0.0
			slide = dt * TipBoardNew.SLIDE_SPEED
			if slide > 1.0:
				slide = 1.0

			alive = []
			for toast in self.__toasts:
				if now >= toast.deadTime:
					toast.Destroy()
					continue
				if now < toast.bornTime + TipBoardNew.FADE_IN:
					alpha = (now - toast.bornTime) / TipBoardNew.FADE_IN
				elif now < toast.holdEndTime:
					alpha = 1.0
				else:
					alpha = 1.0 - (now - toast.holdEndTime) / TipBoardNew.FADE_OUT
				toast.SetCardAlpha(alpha)
				alive.append(toast)

			if len(alive) != len(self.__toasts):
				self.__toasts = alive
				self.__Reflow()

			if not self.__toasts:
				self.Hide()
				return

			screenWidth = wndMgr.GetScreenWidth()
			for toast in self.__toasts:
				diff = toast.targetY - toast.curY
				if diff > -0.5 and diff < 0.5:
					toast.curY = toast.targetY
				else:
					toast.curY += diff * slide
				toast.SetPosition(int((screenWidth - toast.cardWidth) / 2), int(toast.curY))


class NoticeBoxBoard(ui.Window):
	# 9-slice board built from the custom notice_box art (uniform 11px slices),
	# using the exact same slicing approach as ui.ThinBoardCircle -- 4 corners
	# (fixed), 4 edges (stretched along their axis), and a stretched centre.
	# The centre is an image (noti_box_center) instead of a solid colour bar, so
	# the art alone defines the look. Drop-in replacement for the board inside
	# ImportantPopup. If the art slice size changes, update SLICE.
	ROOT = "d:/ymir work/ui/pattern/notice_box/noti_box_"
	SLICE = 11

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self):
		ui.Window.__init__(self)
		s = NoticeBoxBoard.SLICE

		self.Center = self.__MakeImage("center")
		self.Center.SetPosition(s, s)

		self.Corners = []
		for name in ("left_top", "left_bot", "right_top", "right_bot"):
			self.Corners.append(self.__MakeImage(name))

		self.Lines = []
		for name in ("left", "right", "top", "bot"):
			self.Lines.append(self.__MakeImage(name))

		self.Lines[self.L].SetPosition(0, s)
		self.Lines[self.T].SetPosition(s, 0)

	def __del__(self):
		ui.Window.__del__(self)

	def __MakeImage(self, name):
		img = ui.ExpandedImageBox()
		img.AddFlag("attach")
		img.AddFlag("not_pick")
		img.LoadImage(NoticeBoxBoard.ROOT + name + ".png")
		img.SetParent(self)
		img.SetPosition(0, 0)
		img.Show()
		return img

	def SetSize(self, width, height):
		s = NoticeBoxBoard.SLICE
		width = max(s * 2, width)
		height = max(s * 2, height)
		ui.Window.SetSize(self, width, height)

		self.Corners[self.LT].SetPosition(0, 0)
		self.Corners[self.RT].SetPosition(width - s, 0)
		self.Corners[self.LB].SetPosition(0, height - s)
		self.Corners[self.RB].SetPosition(width - s, height - s)

		self.Lines[self.L].SetPosition(0, s)
		self.Lines[self.R].SetPosition(width - s, s)
		self.Lines[self.T].SetPosition(s, 0)
		self.Lines[self.B].SetPosition(s, height - s)
		self.Center.SetPosition(s, s)

		midW = width - s * 2
		midH = height - s * 2
		hScale = float(midW - s) / s
		vScale = float(midH - s) / s

		self.Lines[self.L].SetRenderingRect(0.0, 0.0, 0.0, vScale)
		self.Lines[self.R].SetRenderingRect(0.0, 0.0, 0.0, vScale)
		self.Lines[self.T].SetRenderingRect(0.0, 0.0, hScale, 0.0)
		self.Lines[self.B].SetRenderingRect(0.0, 0.0, hScale, 0.0)
		self.Center.SetRenderingRect(0.0, 0.0, hScale, vScale)


class ImportantPopup(ui.Window):
	# Animated "important message" popup (engine animated_board pop: scale +
	# fade + slide-up). NOT a static tip board. Driven from the server by an
	# idx-flagged ChatPacketNew; also kept in the chat log. Single line (the
	# engine multi-line auto-wrap is unreliable for centred Arabic). One message
	# at a time, with a queue and de-dup of repeats.
	#
	# Re-entrancy safety: Show()/Hide() reassign the engine animation tween, so
	# they are called ONLY from ShowPopup or OnUpdate, NEVER from inside
	# OnAnimationComplete. Reassigning the tween from within its own step
	# callback froze the popup ("stuck until relog"). The window stays shown
	# across queued messages (re-popping in place) and only hides when the queue
	# drains. OnUpdate also watchdogs every state so it can never get stuck.
	HEIGHT = 42
	PAD_X = 32
	MIN_WIDTH = 150
	MAX_WIDTH = 700
	BOTTOM_OFFSET = 210
	HOLD = 3.5
	QUEUE_HOLD = 1.8
	SHOW_MS = 240
	SCALE_START = 0.72
	SLIDE_UP = 22
	QUEUE_MAX = 8
	TEXT_COLOR = (1.0, 0.93, 0.88)

	STATE_IDLE = 0
	STATE_SHOWING = 1
	STATE_HOLDING = 2
	STATE_HIDING = 3

	def __init__(self):
		ui.Window.__init__(self)
		self.__queue = []
		self.__current = ""
		self.__state = ImportantPopup.STATE_IDLE
		self.__hideTime = 0.0
		self.__showStart = 0.0
		self.__hideStart = 0.0

		self.AddFlag("not_pick")
		self.AddFlag("float")
		self.AddFlag("animated_board")
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.SetAnimationScale(ImportantPopup.SCALE_START, 1.0)
			self.SetAnimationDuration(ImportantPopup.SHOW_MS)
			self.SetAnimationOffset(0, ImportantPopup.SLIDE_UP)

		board = NoticeBoxBoard()
		board.SetParent(self)
		board.AddFlag("not_pick")
		board.Show()
		self.__board = board

		text = ui.TextLine()
		text.SetParent(board)
		text.AddFlag("not_pick")
		text.SetOutline()
		text.SetHorizontalAlignCenter()
		text.SetVerticalAlignCenter()
		text.SetWindowHorizontalAlignCenter()
		text.SetWindowVerticalAlignCenter()
		text.Show()
		self.__text = text

		self.Hide()

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.__queue = []
		self.__state = ImportantPopup.STATE_IDLE
		self.__board = None
		self.__text = None
		self.Hide()

	def __ApplyColors(self):
		tr, tg, tb = ImportantPopup.TEXT_COLOR
		self.__text.SetPackedFontColor(grp.GenerateColor(tr, tg, tb, 1.0))
		wndMgr.SetOutlineColor(self.__text.GetWindowHandle(), grp.GenerateColor(0.0, 0.0, 0.0, 1.0))

	# Configure + play the pop-in. Safe ONLY from ShowPopup / OnUpdate.
	def __Begin(self, message):
		self.__current = message
		self.__text.SetText(message)

		width = self.__text.GetTextSize()[0] + ImportantPopup.PAD_X * 2
		if width < ImportantPopup.MIN_WIDTH:
			width = ImportantPopup.MIN_WIDTH
		if width > ImportantPopup.MAX_WIDTH:
			width = ImportantPopup.MAX_WIDTH

		self.SetSize(width, ImportantPopup.HEIGHT)
		self.__board.SetSize(width, ImportantPopup.HEIGHT)
		self.__board.SetPosition(0, 0)
		self.__ApplyColors()

		x = (wndMgr.GetScreenWidth() - width) // 2
		y = wndMgr.GetScreenHeight() - ImportantPopup.BOTTOM_OFFSET
		self.SetPosition(x, y)

		self.__state = ImportantPopup.STATE_SHOWING
		self.__showStart = app.GetTime()
		self.Show()
		self.SetTop()
		if not app.ENABLE_WINDOW_SLIDE_EFFECT:
			# No engine animation -> no OnAnimationComplete; advance now.
			self.__EnterHold()

	def __EnterHold(self):
		self.__state = ImportantPopup.STATE_HOLDING
		hold = ImportantPopup.HOLD
		if self.__queue:
			hold = ImportantPopup.QUEUE_HOLD
		self.__hideTime = app.GetTime() + hold

	def ShowPopup(self, message):
		if not message:
			return

		# Recover if the window was hidden out from under us (phase change /
		# HideAllWindows) while we still thought it was active.
		if self.__state != ImportantPopup.STATE_IDLE and not self.IsShow():
			self.__state = ImportantPopup.STATE_IDLE
			self.__current = ""

		if self.__state == ImportantPopup.STATE_IDLE or self.__state == ImportantPopup.STATE_HIDING:
			# IDLE -> show now. HIDING -> cancel the pop-out and show now (safe:
			# ShowPopup is never called from inside a tween step).
			self.__Begin(message)
			return

		# SHOWING / HOLDING -> queue it.
		if message == self.__current:
			if self.__state == ImportantPopup.STATE_HOLDING:
				self.__hideTime = app.GetTime() + ImportantPopup.HOLD
			return
		if message in self.__queue:
			return
		if len(self.__queue) < ImportantPopup.QUEUE_MAX:
			self.__queue.append(message)
			# Drain the queue sooner: don't sit on the current message too long.
			if self.__state == ImportantPopup.STATE_HOLDING:
				soon = app.GetTime() + ImportantPopup.QUEUE_HOLD
				if soon < self.__hideTime:
					self.__hideTime = soon

	# Engine callback. ONLY flips state flags -- never calls Show()/Hide().
	def OnAnimationComplete(self, isShowAnimation):
		if isShowAnimation:
			if self.__state == ImportantPopup.STATE_SHOWING:
				self.__EnterHold()
		else:
			self.__state = ImportantPopup.STATE_IDLE
			self.__current = ""

	def OnUpdate(self):
		now = app.GetTime()

		if self.__state == ImportantPopup.STATE_SHOWING:
			# Watchdog: advance even if the completion callback never arrives.
			if now - self.__showStart > (ImportantPopup.SHOW_MS / 1000.0) + 0.5:
				self.__EnterHold()
			return

		if self.__state == ImportantPopup.STATE_HOLDING:
			if now >= self.__hideTime:
				if self.__queue:
					# Re-pop the next message in place; the window stays shown so
					# OnUpdate keeps driving the queue (no re-entrant chaining).
					self.__Begin(self.__queue.pop(0))
				else:
					self.__state = ImportantPopup.STATE_HIDING
					self.__hideStart = now
					self.Hide()
			return

		if self.__state == ImportantPopup.STATE_HIDING:
			# Watchdog: never get stuck mid pop-out.
			if now - self.__hideStart > 1.0:
				self.__state = ImportantPopup.STATE_IDLE
				self.__current = ""
				if self.__queue:
					self.__Begin(self.__queue.pop(0))
			return


if app.ENABLE_12ZI:
	class MissionBoard(ui.Bar):
		FONT_HEIGHT	= 15
		LINE_HEIGHT	= FONT_HEIGHT + 5
		STEP_HEIGHT	= LINE_HEIGHT + 5
		LONG_TEXT_START_X	= 300
		SCREEN_WIDTH	= wndMgr.GetScreenWidth()

		def __init__(self):
			ui.Bar.__init__(self)

			self.AddFlag("not_pick")
			self.missionText = None
			self.missionFullText = None
			self.curPos = 0
			self.dstPos = -5
			self.nextScrollTime = 0
			self.flowMode = False
			self.ScrollStartTime = 0.0

			self.SetPosition(0, 100)
			self.SetSize(self.SCREEN_WIDTH, 35)
			self.SetColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.5))
			self.SetWindowHorizontalAlignCenter()

			self.__CreateTextBar()

		def __del__(self):
			ui.Bar.__del__(self)

		def __CreateTextBar(self):
			x, y = self.GetGlobalPosition()

			self.textBar = BigTextBar(self.SCREEN_WIDTH*2, 300, self.FONT_HEIGHT)
			self.textBar.SetParent(self)
			self.textBar.SetPosition(6, 8)
			self.textBar.SetTextColor(242, 231, 193)
			self.textBar.SetClipRect(0, y, self.SCREEN_WIDTH, y+8+self.STEP_HEIGHT)
			self.textBar.Show()

		def CleanMission(self):
			self.missionText = None
			self.missionFullText = None
			self.textBar.ClearBar()
			self.Hide()

		def __RefreshBoard(self):
			self.textBar.ClearBar()

			if self.missionFullText:
				(text_width, text_height) = self.textBar.GetTextExtent(self.missionFullText)

				if text_width>self.SCREEN_WIDTH:
					self.textBar.TextOut(0, (self.STEP_HEIGHT-8-text_height)/2, self.missionFullText)
					self.flowMode = True
				else:
					self.textBar.TextOut((wndMgr.GetScreenWidth()-text_width)/2, (self.STEP_HEIGHT-8-text_height)/2, self.missionFullText)
					self.flowMode = False

		def SetMission(self, text):
			self.__AppendText(text)
			self.__RefreshBoard()

			if self.flowMode:
				self.dstPos = -text_width
				self.curPos = self.LONG_TEXT_START_X
				self.textBar.SetPosition(3 + self.curPos, 8)
			else:
				self.dstPos = 0
				self.curPos = self.STEP_HEIGHT
				self.textBar.SetPosition(3, 8 + self.curPos)

			if not self.IsShow():
				self.Show()

		def SetSubMission(self, text):
			self.missionFullText = self.missionText + text

			preflowMode = self.flowMode

			self.__RefreshBoard()

			if preflowMode != self.flowMode:
				if self.flowMode:
					self.dstPos = -text_width
					self.curPos = self.LONG_TEXT_START_X
					self.textBar.SetPosition(3 + self.curPos, 8)
				else:
					self.dstPos = 0
					self.curPos = self.STEP_HEIGHT
					self.textBar.SetPosition(3, 8 + self.curPos)

		def __AppendText(self, text):
			if text == "":
				self.CleanMission()
				return

			self.missionText = text
			self.missionFullText = text

		def OnUpdate(self):
			if self.missionFullText == None:
				self.Hide()
				return

			if self.dstPos < self.curPos:
				self.curPos -= 1
				if self.flowMode:
					self.textBar.SetPosition(3 + self.curPos, 8)
				else:
					self.textBar.SetPosition(3, 8 + self.curPos)
			else:
				if self.flowMode:
					self.curPos = self.SCREEN_WIDTH
