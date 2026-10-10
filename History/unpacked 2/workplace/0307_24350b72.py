# coding: latin_1

import app
import net
import player

import ui
import uiscriptlocale
import wndMgr
import localeinfo
import constinfo
import osfinfo

import uiminigamerumi

if app.ENABLE_MINI_GAME_CATCH_KING:
	import uiminigamecatchking
if app.ENABLE_MINI_GAME_BNW:
	import uiMiniGameBNW

import systemSetting

MINIGAME_TYPE_RUMI = 1
if app.ENABLE_MINI_GAME_CATCH_KING:
	MINIGAME_CATCH_KING = 2
if app.ENABLE_MINI_GAME_BNW:
	MINIGAME_TYPE_BNW = 3
MINIGAME_TYPE_MAX = 3

RUMI_ROOT = "d:/ymir work/ui/minigame/rumi/"

if app.ENABLE_MINI_GAME_OKEY:
	button_gap = 10
	button_height = 25

	class MiniGameDialog(ui.ScriptWindow):
		def __init__(self):
			ui.ScriptWindow.__init__(self)
			
			if app.ENABLE_WINDOW_SLIDE_EFFECT:
				self.AddFlag("animated_board")
			
			self.isLoaded = 0

			self.board = None
			self.close_button = None

			self.button_dict = {}

			self.__LoadWindow()

		def __del__(self):
			ui.ScriptWindow.__del__(self)
			self.Destroy()

		def Destroy(self):
			self.isLoaded = 0

			self.board = None
			self.close_button = None

			self.button_dict = {}

		def Show(self):
			self.__LoadWindow()
			ui.ScriptWindow.Show(self)

		def Close(self):
			self.Hide()

		def OnPressEscapeKey(self):
			self.Close()
			return True

		def __LoadWindow(self):
			if self.isLoaded == 1:
				return

			self.isLoaded = 1

			try:
				pyScrLoader = ui.PythonScriptLoader()
				pyScrLoader.LoadScriptFile(self, "UIScript/MiniGameDialog.py")
			except:
				import exception
				exception.Abort("MiniGameDialog.LoadWindow.LoadObject")

			try:
				self.board = self.GetChild("board")
				self.close_button = self.GetChild("close_button")
				self.close_button.SetEvent(ui.__mem_func__(self.Close))

			except:
				import exception
				exception.Abort("MiniGameDialog.LoadWindow.BindObject")

			self.Hide()

		def AppendButton(self, name, func):
			if self.button_dict.has_key(name):
				return

			button = ui.Button()
			button.SetParent(self.board)
			button_count = len(self.button_dict)
			pos_y = (button_gap * (button_count + 1)) + button_count * button_height
			button.SetPosition(10, pos_y)
			button.SetUpVisual("d:/ymir work/ui/public/XLarge_Button_01.sub")
			button.SetOverVisual("d:/ymir work/ui/public/XLarge_Button_02.sub")
			button.SetDownVisual("d:/ymir work/ui/public/XLarge_Button_03.sub")

			if name:
				button.SetText(name)

			if func:
				button.SetEvent(ui.__mem_func__(func))

			button.Show()
			self.button_dict[name] = button

		def DeleteButton(self, name):
			if not self.button_dict.has_key(name):
				return

			self.button_dict[name].Hide()
			del self.button_dict[name]

		def DeleteAllButton(self):
			for button in self.button_dict.values():
				button.Hide()
				del button

			self.button_dict.clear()

		def RefreshDialog(self):
			total_len = len(self.button_dict) + 1
			board_height = (button_height * total_len) + (button_gap * (total_len + 1))
			self.board.SetSize(200, board_height)
			self.SetSize(200, board_height)

			dict_len = len(self.button_dict)
			pos_y = (button_gap * (dict_len + 1)) + dict_len * button_height

			if localeinfo.IsARABIC():
				(lx,ly) = self.close_button.GetLocalPosition()
				self.close_button.SetPosition(lx, pos_y)
			else:
				self.close_button.SetPosition(10, pos_y)

# Mini Game Button Area
class MiniGameWindow(ui.ScriptWindow):
	def __init__(self):
		self.isLoaded = 0
		self.main_game = None
		self.rumi_game = None
		self.rumi_simple_waiting = None
		self.wndBNWGame = None

		if app.USE_BL_FISH_EVENT:
			self.wndJigsaw = None

		if app.ENABLE_MINI_GAME_OKEY or app.ENABLE_MINI_GAME_CATCH_KING:
			self.mini_game_dialog = None
			self.isshow_mini_game_dialog = False

		if app.ENABLE_MINI_GAME_CATCH_KING:
			self.catch_king_game	= None

		self.game_type = MINIGAME_TYPE_MAX
		self.tooltipitem = None

		ui.ScriptWindow.__init__(self)
		
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()
		ui.ScriptWindow.Show(self)
		
		if app.ENABLE_MINI_GAME_OKEY or app.ENABLE_MINI_GAME_CATCH_KING:
			if self.mini_game_dialog and self.isshow_mini_game_dialog:
				self.mini_game_dialog.Show()

	def Close(self):
		self.Hide()

	def Hide(self):
		if app.ENABLE_MINI_GAME_OKEY or app.ENABLE_MINI_GAME_CATCH_KING:
			if self.mini_game_dialog:
				self.isshow_mini_game_dialog = self.mini_game_dialog.IsShow()
				self.mini_game_dialog.Hide()

		wndMgr.Hide(self.hWnd)

	def Destroy(self):
		self.isLoaded = 0

		self.main_game = None

		if self.rumi_simple_waiting:
			self.rumi_simple_waiting.Destroy()
			self.rumi_simple_waiting = None

		if self.rumi_game:
			self.rumi_game.Destroy()
			self.rumi_game = None

		if app.ENABLE_MINI_GAME_OKEY or app.ENABLE_MINI_GAME_CATCH_KING:
			if self.mini_game_dialog:
				self.mini_game_dialog.Destroy()
				self.mini_game_dialog = None

		if app.ENABLE_MINI_GAME_CATCH_KING:
			if self.catch_king_game:
				self.catch_king_game.Destroy()
				self.catch_king_game = None

		if app.ENABLE_MINI_GAME_BNW:
			if self.wndBNWGame:
				self.wndBNWGame.Destroy()
				self.wndBNWGame = None

		self.game_type = MINIGAME_TYPE_MAX
		self.tooltipitem = None

	def SetItemToolTip(self, tooltip):
		self.tooltipitem = tooltip

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			self.__LoadScript("UIScript/MiniGameWindow.py")

		except:
			import exception
			exception.Abort("MiniGameWindow.LoadWindow.LoadObject")

		try:
			self.minigame_rumi_button = self.GetChild("minigame_rumi_button")
			self.minigame_rumi_button.SetEvent(ui.__mem_func__(self.__ClickRumiButton))
			self.minigame_rumi_button.Hide()

			self.minigame_rumi_button_effect = self.GetChild("minigame_rumi_button_effect")
			self.minigame_rumi_button_effect.Hide()

			if localeinfo.IsARABIC():
				mini_game_window = self.GetChild("mini_game_window")
				window_width = mini_game_window.GetWidth()
				rumi_button_width = self.minigame_rumi_button.GetWidth()
				adjust_pos_x = window_width - rumi_button_width
				(lx,ly) = self.minigame_rumi_button.GetLocalPosition()
				self.minigame_rumi_button.SetPosition(lx + adjust_pos_x, 0)
				self.minigame_rumi_button_effect.SetWindowHorizontalAlignLeft()
		except:
			import exception
			exception.Abort("MiniGameWindow.LoadWindow.Okey.BindObject")


		if app.ENABLE_MINI_GAME_OKEY or app.ENABLE_MINI_GAME_CATCH_KING:
			try:
				mini_game_window = self.GetChild("mini_game_window")
				self.event_banner_button = ui.Button()
				self.event_banner_button.SetParent(mini_game_window)
				self.event_banner_button.SetPosition(-10, 0)
				self.event_banner_button.SetUpVisual("d:/ymir work/ui/minigame/banner.sub")
				self.event_banner_button.SetOverVisual("d:/ymir work/ui/minigame/banner.sub")
				self.event_banner_button.SetDownVisual("d:/ymir work/ui/minigame/banner.sub")
				self.event_banner_button.SetEvent(ui.__mem_func__(self.__ClickIntegrationEventBannerButton))
				self.event_banner_button.Hide()
				self.event_banner_button_enable = False

			except:
				import exception
				exception.Abort("MiniGameWindow.LoadWindow.EventBannerButton.BindObject")

			try:
				## Mini Game Integration Event Button Dialog
				self.mini_game_dialog = MiniGameDialog()
				self.mini_game_dialog.Hide()
			except:
				import exception
				exception.Abort("MiniGameWindow.LoadWindow.MiniGameDialog")

		self.Show()

	def __LoadScript(self, fileName):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, fileName)

	def MiniGameOkeyEvent(self, enable):
		if enable:
			self.minigame_rumi_button.Show()
		else:
			self.minigame_rumi_button.Hide()
			self.minigame_rumi_button_effect.Hide()

		if self.rumi_simple_waiting:
			self.rumi_simple_waiting.Destroy()
			self.rumi_simple_waiting = None

		if self.rumi_game:
			self.rumi_game.Destroy()
			self.rumi_game = None

		if self.game_type == MINIGAME_TYPE_RUMI:
			self.main_game = None

	if app.ENABLE_EVENT_MANAGER:
		def __ClickEventManager(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				(x, y) = self.mini_game_dialog.GetLocalPosition()
				interfaceHandler.ToggleInGameEvent(x, y)

	def __ClickRumiButton(self):
		if app.ENABLE_MINI_GAME_OKEY:
			self.__CloseAll(MINIGAME_TYPE_RUMI)

		if app.ENABLE_MINI_GAME_OKEY or app.ENABLE_MINI_GAME_CATCH_KING:
			if self.mini_game_dialog:
				self.mini_game_dialog.Close()

		if not self.rumi_game:
			self.rumi_game = uiminigamerumi.CardsInfoWindow()
			self.rumi_simple_waiting = uiminigamerumi.CardsSimpleWaitingPage(self.rumi_game)
			self.rumi_game.SetSimpleWaitingPage(self.rumi_simple_waiting)

		self.main_game = self.rumi_game
		self.game_type = MINIGAME_TYPE_RUMI
		self.main_game.Open()


	if app.ENABLE_MINI_GAME_BNW:
		def __ClickBNWButton(self):
			self.__CloseAll(MINIGAME_TYPE_BNW)

			if self.mini_game_dialog:
				self.mini_game_dialog.Close()

			if not self.wndBNWGame:
				self.wndBNWGame = uiMiniGameBNW.MiniGameBNW()

			self.main_game = self.wndBNWGame
			self.game_type = MINIGAME_TYPE_BNW
			self.main_game.Open()

		def MiniGameBNWStart(self):
			if self.wndBNWGame:
				self.wndBNWGame.GameStart()

		def MiniGameBNWCompare(self, winIndex, playerCard, opponentCard, myScore):
			if self.wndBNWGame:
				self.wndBNWGame.CardCompare(winIndex, playerCard, opponentCard, myScore)

		def MiniGameBNWAddRanking(self, position, isMain, name, donations):
			if self.wndBNWGame:
				self.wndBNWGame.AddRanking(position, isMain, name, donations)

		def MiniGameBNWClearRanking(self):
			if self.wndBNWGame:
				self.wndBNWGame.ClearRanking()

		def MiniGameBNWOpenRanking(self):
			if self.wndBNWGame:
				self.wndBNWGame.OpenRanking()

		def MiniGameBNWUpdateRanking(self):
			if self.wndBNWGame:
				self.wndBNWGame.UpdateRanking()

		def ClickBNWEventButton(self):
			if self.wndBNWGame:
				self.wndBNWGame.Open()

	if app.ENABLE_MINI_GAME_CATCH_KING:
		def __ClickCatchKingButton(self):
			self.__CloseAll(MINIGAME_CATCH_KING)

			if self.mini_game_dialog:
				self.mini_game_dialog.Close()

			if not self.catch_king_game:
				self.catch_king_game = uiminigamecatchking.MiniGameCatchKing()

			self.main_game = self.catch_king_game
			self.game_type = MINIGAME_CATCH_KING
			self.main_game.Open()

		def MiniGameCatchKingEventStart(self, bigScore):
			if self.catch_king_game:
				self.catch_king_game.GameStart(bigScore)

		def MiniGameCatchKingSetHandCard(self, cardNumber):
			if self.catch_king_game:
				self.catch_king_game.CatchKingSetHandCard(cardNumber)

		def MiniGameCatchKingResultField(self, score, rowType, cardPos, cardValue, keepFieldCard, destroyHandCard, getReward, isFiveNear):
			if self.catch_king_game:
				self.catch_king_game.CatchKingResultField(score, rowType, cardPos, cardValue, keepFieldCard, destroyHandCard, getReward, isFiveNear)

		def MiniGameCatchKingSetEndCard(self, cardPos, cardNumber):
			if self.catch_king_game:
				self.catch_king_game.CatchKingSetEndCard(cardPos, cardNumber)

		def MiniGameCatchKingReward(self, rewardCode):
			if self.catch_king_game:
				self.catch_king_game.CatchKingReward(rewardCode)

	def MiniGameStart(self):
		if not self.main_game:
			return

		self.minigame_rumi_button.SetUpVisual(RUMI_ROOT + "rumi_button_max.sub")
		self.minigame_rumi_button.SetOverVisual(RUMI_ROOT + "rumi_button_max.sub")
		self.minigame_rumi_button.SetDownVisual(RUMI_ROOT + "rumi_button_max.sub")

		if not app.ENABLE_MINI_GAME_OKEY:
			if self.minigame_rumi_button_effect:
				self.minigame_rumi_button_effect.ResetFrame()
				self.minigame_rumi_button_effect.Show()

		self.main_game.GameStart()

	def	MiniGameEnd(self):
		if not self.main_game:
			return

		self.minigame_rumi_button.SetUpVisual(RUMI_ROOT + "rumi_button_min.sub")
		self.minigame_rumi_button.SetOverVisual(RUMI_ROOT + "rumi_button_min.sub")
		self.minigame_rumi_button.SetDownVisual(RUMI_ROOT + "rumi_button_min.sub")

		if not app.ENABLE_MINI_GAME_OKEY:
			if self.minigame_rumi_button_effect:
				self.minigame_rumi_button_effect.Hide()

		self.main_game.GameEnd()

	def RumiMoveCard(self, srcCard, dstCard):
		if MINIGAME_TYPE_RUMI != self.game_type:
			return

		self.main_game.RumiMoveCard(srcCard, dstCard)

	def MiniGameRumiSetDeckCount(self, deck_card_count):
		if MINIGAME_TYPE_RUMI != self.game_type:
			return

		self.main_game.SetDeckCount(deck_card_count)

	def RumiIncreaseScore(self, score, total_score):
		if MINIGAME_TYPE_RUMI != self.game_type:
			return

		self.main_game.RumiIncreaseScore(score, total_score)

	if app.ENABLE_MINI_GAME_OKEY or app.ENABLE_MINI_GAME_CATCH_KING:
		def __ClickIntegrationEventBannerButton(self):
			if not self.mini_game_dialog:
				return

			if self.mini_game_dialog.IsShow():
				self.mini_game_dialog.Close()
			else:
				self.mini_game_dialog.Show()

		if app.USE_BL_FISH_EVENT:
			def __ClickJigsaw(self):
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler:
					interfaceHandler.ClickFishEventButton()

		def IntegrationMiniGame(self, enable):
			if enable:
				self.event_banner_button.Show()
				self.event_banner_button_enable = True
			else:
				self.event_banner_button.Hide()
				self.event_banner_button_enable = False

			if app.ENABLE_MINI_GAME_OKEY:
				if self.rumi_simple_waiting:
					self.rumi_simple_waiting.Destroy()
					self.rumi_simple_waiting = None

				if self.rumi_game:
					self.rumi_game.Destroy()
					self.rumi_game = None

			if app.ENABLE_MINI_GAME_CATCH_KING:
				if self.catch_king_game:
					self.catch_king_game.Destroy()
					self.catch_king_game = None

			if app.ENABLE_MINI_GAME_BNW:
				if self.wndBNWGame:
					self.wndBNWGame.Destroy()
					self.wndBNWGame = None

			if self.mini_game_dialog:
				self.mini_game_dialog.DeleteAllButton()

				if False == enable:
					self.mini_game_dialog.Hide()
				else:
					if app.ENABLE_EVENT_MANAGER:
						self.mini_game_dialog.AppendButton(uiscriptlocale.EVENT_MANAGER_TITLE, self.__ClickEventManager)

					if app.ENABLE_MINI_GAME_OKEY:
						if osfinfo.RUMI_GAME_EVENT == True:
							self.mini_game_dialog.AppendButton(uiscriptlocale.BANNER_OKEY_BUTTON, self.__ClickRumiButton)
					if app.ENABLE_MINI_GAME_CATCH_KING:
						if osfinfo.CATCH_KING_GAME_EVENT == True:
							self.mini_game_dialog.AppendButton(uiscriptlocale.BANNER_CATCHKING_BUTTON, self.__ClickCatchKingButton)
					if app.ENABLE_MINI_GAME_BNW:
						if osfinfo.BNW_GAME_EVENT == True:
							self.mini_game_dialog.AppendButton(uiscriptlocale.BANNER_BNWBUTTON, self.__ClickBNWButton)

					if app.USE_BL_FISH_EVENT:
						self.mini_game_dialog.AppendButton(uiscriptlocale.BANNER_FISH_BUTTON, self.__ClickJigsaw)

				self.mini_game_dialog.RefreshDialog()

				self.game_type = MINIGAME_TYPE_MAX
				self.main_game = None

	if app.ENABLE_MINI_GAME_OKEY or app.ENABLE_MINI_GAME_CATCH_KING:
		def __CloseAll(self, except_game = MINIGAME_TYPE_MAX):
			if self.rumi_simple_waiting and except_game != MINIGAME_TYPE_RUMI:
				self.rumi_simple_waiting.Close()

			if self.rumi_game and except_game != MINIGAME_TYPE_RUMI:
				self.rumi_game.Close()

			if app.ENABLE_MINI_GAME_CATCH_KING:
				if self.catch_king_game and except_game != MINIGAME_CATCH_KING:
					self.catch_king_game.Close()

			if app.ENABLE_MINI_GAME_BNW:
				if self.wndBNWGame and except_game != MINIGAME_TYPE_BNW:
					self.wndBNWGame.Close()

		def SetOkeyNormalBG(self):
			if not self.rumi_game:
				return

			self.rumi_game.SetOkeyNormalBG()

	def hide_mini_game_dialog(self):
		if self.event_banner_button:
			if self.event_banner_button.IsShow():
				self.event_banner_button.Hide()

		if self.mini_game_dialog:
			if self.mini_game_dialog.IsShow():
				self.mini_game_dialog.Hide()

	def show_mini_game_dialog(self):
		if self.event_banner_button:
			if self.event_banner_button_enable:
				self.event_banner_button.Show()