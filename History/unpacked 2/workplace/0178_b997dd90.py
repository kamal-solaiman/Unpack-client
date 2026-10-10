#
# Title: uiCaptcha.py
# Description: CAPTCHA Challenge
#
# Author: Owsap
# Web: https://owsap.dev/
# M2Dev: https://metin2.dev/profile/544-owsap/
# GitHub: https://github.com/Owsap
#
# Discord: owsap
# Skype: owsap.
# Email: support@owsap.dev
#
# 0x1019717545235857468
#

import app
import ui
import localeinfo
import net

if app.USE_CAPTCHA_IMPRISONMENT:
	import player

import wndMgr

SLOT_IMAGE = "d:/ymir work/ui/public/slot_base.sub"
SLOT_SIZE = 32

DESC_DICT = {
				0 : localeinfo.CAPTCHA_DESC_0,
				1 : localeinfo.CAPTCHA_DESC_1,
				2 : localeinfo.CAPTCHA_DESC_2,
				3 : localeinfo.CAPTCHA_DESC_3,
				4 : localeinfo.CAPTCHA_DESC_4,
				5 : localeinfo.CAPTCHA_DESC_5,
				6 : localeinfo.CAPTCHA_DESC_6,
				7 : localeinfo.CAPTCHA_DESC_7,
				8 : localeinfo.CAPTCHA_DESC_8,
				9 : localeinfo.CAPTCHA_DESC_9,
				10 : localeinfo.CAPTCHA_DESC_10,
				11 : localeinfo.CAPTCHA_DESC_11,
}

class CaptchaWindow(ui.Board):

	BOARD_WIDTH = 300
	BOARD_HEIGHT = 250

	class DragImage(ui.DragButton):
		def __init__(self, parent, crc, file, token = None):
			ui.DragButton.__init__(self)

			self.parent = parent
			self.crc = crc
			self.file = file
			self.token = token
			self.x = 0
			self.y = 0

			self.pending = False
			self.icon_img = None

			grid = self.parent.grid_img
			self.restrict_width = grid.GetWidth()
			self.restrict_height = grid.GetHeight()

			self.SetParent(self.parent.grid_img)

			# Native inventory slot as the button background; the item icon sits on top of it.
			self.SetUpVisual(SLOT_IMAGE)
			self.SetOverVisual(SLOT_IMAGE)
			self.SetDownVisual(SLOT_IMAGE)

			icon_img = ui.ImageBox()
			icon_img.SetParent(self)
			icon_img.AddFlag("not_pick")
			icon_img.LoadImage(self.file)
			icon_img.SetPosition(int((SLOT_SIZE - icon_img.GetWidth()) / 2), int((SLOT_SIZE - icon_img.GetHeight()) / 2))
			icon_img.Show()
			self.icon_img = icon_img

			self.SetPosition(app.GetRandom(80, 150), app.GetRandom(15, self.restrict_height - 50))
			self.SetEvent(ui.__mem_func__(self.OnClick))
			self.SetMoveEvent(ui.__mem_func__(self.OnMove))
			self.SetRestrictMovementArea(0, 0, self.restrict_width, self.restrict_height)
			self.Show()

		def __del__(self):
			ui.DragButton.__del__(self)

		if app.USE_CAPTCHA_IMPRISONMENT:
			def Order(self):
				self.pending = False
				self.SetPosition(app.GetRandom(80, 150), app.GetRandom(15, self.restrict_height - 50))

		def OnClick(self):
			if not self.parent.grid_lock:
				return

			if self.parent.is_v2:
				if self.pending:
					return

				self.pending = True
				net.SendCaptchaV2Packet(self.parent.nonce, self.token)
				return

			if app.USE_CAPTCHA_IMPRISONMENT:
				if self.pending:
					return

				self.pending = True
			else:
				self.parent.Close()

			net.SendCaptchaPacket(self.crc, self.parent.grid_type, self.x, self.y)

		def OnMove(self):
			if self.parent.grid_lock:
				self.SetPosition(self.x, self.y)
				return

			(global_drag_img_x, global_drag_img_y) = self.GetGlobalPosition()
			(global_grid_img_x, global_grid_img_y) = self.parent.grid_img.GetGlobalPosition()

			self.x = global_drag_img_x - global_grid_img_x
			self.y = global_drag_img_y - global_grid_img_y

			attached = False

			if self.parent.grid_type == 1:
				if self.x >= 21 and self.x <= 23 and self.y >= 21 and self.y <= 24:
					attached = True

			elif self.parent.grid_type == 2:
				if self.x >= 219 and self.x <= 221 and self.y >= 21 and self.y <= 24:
					attached = True

			elif self.parent.grid_type == 3:
				if self.x >= 21 and self.x <= 23 and self.y >= 87 and self.y <= 90:
					attached = True

			elif self.parent.grid_type == 4:
				if self.x >= 219 and self.x <= 221 and self.y >= 87 and self.y <= 90:
					attached = True

			if attached:
				self.parent.grid_bar.SetColor(0xAF008000)
				self.parent.arrow_img.Hide()

				local_grid_bar_x, local_grid_bar_y = self.parent.grid_bar.GetLocalPosition()
				self.x = local_grid_bar_x + 1
				self.y = local_grid_bar_y + 1

				self.parent.LockGrid(1)
			else:
				self.parent.grid_bar.SetColor(0x00000000)
				self.parent.arrow_img.Show()

				self.parent.LockGrid(0)

	def __init__(self):
		ui.Board.__init__(self)
		self.imprisoned = False
		self.__Initialize()
		try:
			self.__LoadBoard()
		except:
			import exception
			exception.Abort("CaptchaWindow.__LoadBoard.SetObject")

	def __del__(self):
		ui.Board.__del__(self)

	def __Initialize(self):
		self.title_bar = None
		self.title_text_line = None
		self.board_text_line = None
		self.grid_img = None
		self.grid_bar= None
		self.grid_bar_img = None
		self.arrow_img = None
		self.timer_base_img = None
		self.timer_gauge_img = None

		self.grid_type = 0
		self.grid_type_dict = {}

		self.drag_img_list = []
		self.timer_gauge_value = 10
		self.timer_gauge_left_sec = 0
		self.grid_lock = 0

		self.is_v2 = False
		self.nonce = None
		self.round = 1
		self.total_rounds = 1

	def __LoadBoard(self):
		## Board
		self.AddFlag("movable")
		self.SetSize(self.BOARD_WIDTH, self.BOARD_HEIGHT)
		self.SetCenterPosition()

		## Title Bar
		title_bar = ui.TitleBar()
		title_bar.SetParent(self)
		title_bar.MakeTitleBar(0, "red")
		title_bar.CloseButtonHide()
		title_bar.SetWidth(self.BOARD_WIDTH - 17)
		title_bar.SetPosition(8, 7)
		title_bar.Show()
		self.title_bar = title_bar

		## Title Name
		title_text_line = ui.TextLine()
		title_text_line.SetParent(self.title_bar)
		title_text_line.SetPosition(0, 4)
		title_text_line.SetWindowHorizontalAlignCenter()
		title_text_line.SetHorizontalAlignCenter()
		title_text_line.SetText(localeinfo.CAPTCHA_TITLE)
		title_text_line.UpdateRect()
		title_text_line.Show()
		self.title_text_line = title_text_line

		## Text Line
		board_text_line = ui.TextLine()
		board_text_line.SetParent(self)
		board_text_line.SetPosition(0, 35)
		board_text_line.SetWindowHorizontalAlignCenter()
		board_text_line.SetHorizontalAlignCenter()
		board_text_line.SetText(localeinfo.CAPTCHA_DESCRIPTION)
		board_text_line.Show()
		self.board_text_line = board_text_line

		## Grid Image
		grid_img = ui.ImageBox()
		grid_img.SetParent(self)
		grid_img.LoadImage("d:/ymir work/ui/game/captcha/grid.tga")
		grid_img.SetPosition(0, 60)
		grid_img.SetWindowHorizontalAlignCenter()
		grid_img.Show()
		self.grid_img = grid_img

		## Grid Bar
		grid_bar = ui.Bar()
		grid_bar.SetParent(self.grid_img)
		grid_bar.SetSize(34, 35)
		grid_bar.SetPosition(0, 0)
		grid_bar.SetColor(0x00000000)
		grid_bar.Show()
		self.grid_bar = grid_bar

		grid_bar_img = ui.ImageBox()
		grid_bar_img.SetParent(self.grid_bar)
		grid_bar_img.AddFlag("not_pick")
		grid_bar_img.LoadImage(SLOT_IMAGE)
		grid_bar_img.SetPosition(1, 1)
		grid_bar_img.SetAlpha(0.5)
		grid_bar_img.Show()
		self.grid_bar_img = grid_bar_img

		## Arrow Animation Image
		arrow_img = ui.AniImageBox()
		arrow_img.SetParent(self)
		arrow_img.AddFlag("not_pick")
		arrow_img.AddFlag("float")
		arrow_img.SetSize(0, 0)
		arrow_img.SetPosition(0, 0)
		arrow_img.SetDelay(6)
		arrow_img.SetPickAlways()
		arrow_img.AppendImage("d:/ymir work/ui/minigame/yutnori/move_arrow/1.sub")
		arrow_img.AppendImage("d:/ymir work/ui/minigame/yutnori/move_arrow/2.sub")
		arrow_img.AppendImage("d:/ymir work/ui/minigame/yutnori/move_arrow/3.sub")
		arrow_img.AppendImage("d:/ymir work/ui/minigame/yutnori/move_arrow/4.sub")
		arrow_img.AppendImage("d:/ymir work/ui/minigame/yutnori/move_arrow/5.sub")
		arrow_img.AppendImage("d:/ymir work/ui/minigame/yutnori/move_arrow/4.sub")
		arrow_img.AppendImage("d:/ymir work/ui/minigame/yutnori/move_arrow/3.sub")
		arrow_img.AppendImage("d:/ymir work/ui/minigame/yutnori/move_arrow/2.sub")
		arrow_img.Hide()
		self.arrow_img = arrow_img

		## Timer Base Image
		timer_base_img = ui.ImageBox()
		timer_base_img.SetParent(self)
		timer_base_img.LoadImage("d:/ymir work/ui/game/fishing/fishing_timer_base.sub")
		timer_base_img.SetPosition(0, 40)
		timer_base_img.SetWindowHorizontalAlignCenter()
		timer_base_img.SetWindowVerticalAlignBottom()
		timer_base_img.Show()
		self.timer_base_img = timer_base_img

		## Timer Gauge Image
		timer_gauge_img = ui.ExpandedImageBox()
		timer_gauge_img.SetParent(self.timer_base_img)
		timer_gauge_img.LoadImage("d:/ymir work/ui/game/fishing/fishing_timer_gauge.sub")
		timer_gauge_img.SetPosition(0, 0)
		timer_gauge_img.Show()
		self.timer_gauge_img = timer_gauge_img

		self.grid_type_dict = {
			0 : "d:/ymir work/ui/game/captcha/grid.tga",
			1 : "d:/ymir work/ui/game/captcha/grid_top_left.tga",
			2 : "d:/ymir work/ui/game/captcha/grid_top_right.tga",
			3 : "d:/ymir work/ui/game/captcha/grid_bottom_left.tga",
			4 : "d:/ymir work/ui/game/captcha/grid_bottom_right.tga",
		}

	def Show(self):
		screen_width = wndMgr.GetScreenWidth()
		screen_height = wndMgr.GetScreenHeight()

		window_width = self.GetWidth()
		window_height = self.GetHeight()

		max_x = screen_width - window_width
		max_y = screen_height - window_height

		random_x = app.GetRandom(0, max_x)
		random_y = app.GetRandom(0, max_y)

		self.SetPosition(random_x, random_y)
		self.SetTop()

		ui.Board.Show(self)

	def Close(self):
		self.Hide()

	def OnPressEscapeKey(self): return True
	def OnPressExitKey(self): return True

	def OnUpdate(self):
		if app.USE_CAPTCHA_IMPRISONMENT and self.imprisoned:
			return

		limit_time = max(0, self.timer_gauge_left_sec - app.GetTime())
		self.timer_gauge_img.SetPercentage(limit_time, self.timer_gauge_value)

		if limit_time <= 0:
			if app.USE_CAPTCHA_IMPRISONMENT:
				self.imprisoned = True

				gameWindow = player.GetGameWindow()
				if gameWindow:
					gameWindow.ImprisonedPopUp()
			else:
				self.Close()
		elif limit_time <= 5:
			self.timer_gauge_img.SetDiffuseColor(1, 0, 0, 1.0)

	def __RefreshGrid(self):
		if not self.arrow_img:
			return

		grid_img_width = self.grid_img.GetWidth()
		grid_img_height = self.grid_img.GetHeight()

		if self.grid_type == 1:
			self.grid_bar.SetPosition(21, 21)

			self.arrow_img.SetPosition(42, 45)
			self.arrow_img.Show()

		elif self.grid_type == 2:
			self.grid_bar.SetPosition(219, 21)

			self.arrow_img.SetPosition(grid_img_width - 32, 45)
			self.arrow_img.Show()

		elif self.grid_type == 3:
			self.grid_bar.SetPosition(21, 87)

			self.arrow_img.SetPosition(42, grid_img_height - 30)
			self.arrow_img.Show()

		elif self.grid_type == 4:
			self.grid_bar.SetPosition(219, 87)

			self.arrow_img.SetPosition(grid_img_width - 32, grid_img_height - 30)
			self.arrow_img.Show()

		else:
			self.arrow_img.SetPosition(0, 0)
			self.arrow_img.Hide()

	def Process(self, desc, grid_type, crc_dict, time):
		self.imprisoned = False

		## Text Line
		if self.board_text_line:
			if DESC_DICT.has_key(desc):
				self.board_text_line.SetText(DESC_DICT[desc])
			else:
				self.board_text_line.SetText(localeinfo.CAPTCHA_DESC_UNKNOWN)

		## Timer Gauge Image
		if self.timer_gauge_img:
			self.timer_gauge_img.SetDiffuseColor(1, 1, 1, 1.0)

		## Grid Bar
		if self.grid_bar:
			self.grid_bar.SetColor(0x00000000)

		## Grid Type Orientation
		self.grid_type = grid_type
		if grid_type in self.grid_type_dict:
			self.grid_img.LoadImage(self.grid_type_dict[grid_type])

		## Arrow Animation Image
		self.__RefreshGrid()

		## Images
		self.drag_img_list = []
		if isinstance(crc_dict, dict):
			for crc, file in crc_dict.items():
				drag_img = self.DragImage(self, crc, file)
				self.drag_img_list.append(drag_img)

		## Timer Gauge Value
		self.timer_gauge_value = time
		self.timer_gauge_left_sec = app.GetTime() + self.timer_gauge_value

		## Grid Lock
		self.grid_lock = 0

	if app.ENABLE_CAPTCHA_REWORK:
		def ProcessV2(self, nonce, grid_type, timer, round, total_rounds, token_file_list, desc):
			self.imprisoned = False
			self.is_v2 = True
			self.nonce = nonce
			self.round = round
			self.total_rounds = total_rounds

			## Text Line
			if self.board_text_line:
				prefix = getattr(localeinfo, "CAPTCHA_V2_INSTRUCTION", "Drag the image showing: %s")
				item_key = "CAPTCHA_ITEM_" + desc.upper().replace(" ", "_")
				label = getattr(localeinfo, item_key, desc)
				try:
					text = prefix % label
				except:
					text = prefix + " " + label
				self.board_text_line.SetText(text)

			## Timer Gauge Image
			if self.timer_gauge_img:
				self.timer_gauge_img.SetDiffuseColor(1, 1, 1, 1.0)

			## Grid Bar
			if self.grid_bar:
				self.grid_bar.SetColor(0x00000000)

			## Grid Type Orientation
			self.grid_type = grid_type
			if grid_type in self.grid_type_dict:
				self.grid_img.LoadImage(self.grid_type_dict[grid_type])

			## Arrow Animation Image
			self.__RefreshGrid()

			## Images
			self.drag_img_list = []
			for token, filepath in token_file_list:
				drag_img = self.DragImage(self, 0, filepath, token)
				self.drag_img_list.append(drag_img)

			## Timer Gauge Value
			self.timer_gauge_value = timer
			self.timer_gauge_left_sec = app.GetTime() + self.timer_gauge_value

			## Grid Lock
			self.grid_lock = 0

	def LockGrid(self, flag):
		self.grid_lock = flag

		for drag_img in self.drag_img_list:
			if app.USE_CAPTCHA_IMPRISONMENT:
				drag_img.RemoveFlag("movable" if flag else "attach")

			drag_img.AddFlag("attach" if flag else "movable")

	if app.USE_CAPTCHA_IMPRISONMENT:
		def Order(self):
			self.__RefreshGrid()

			for child in self.drag_img_list:
				child.Order()

			self.grid_bar.SetColor(0x00000000)

			self.LockGrid(0)

	def IsGridLocked(self):
		return self.grid_lock
