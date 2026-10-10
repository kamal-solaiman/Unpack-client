import ui
import uicommon
import uiscriptlocale
import player
import localeinfo
import net
import app
import constinfo
import grpImage
import grp
import event
import chr
import uiToolTip
import wndMgr
import snd
import chat
import random

DEFAULT_DESC_Y = 7
DESC_WIDTH_COUNT = 70
STATE_NONE = 0
STATE_WAITING = 1
STATE_PLAY = 2
STATE_RANK = 3

def LoadScript(self, fileName):
	pyScrLoader = ui.PythonScriptLoader()
	pyScrLoader.LoadScriptFile(self, fileName)
	
class BNWRankingPage(ui.ScriptWindow):
	BNW_DONATE_RANKING_SHOW_COUNT = 10

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		
		self.isLoaded = 0
		self.SetWindowName("MiniGameBNWRanking")
		
		self.donateButton = None
		self.donateQuestionDialog = None

		self.textList = []
		
		self.myRankPos = None
		self.myRankName = None
		self.myRankCount = None
		
		self.__LoadWindow()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)
	
	def __LoadWindow(self):
		if self.isLoaded == 1:
			return
			
		self.isLoaded = 1
		
		try:
			LoadScript(self, "UIScript/MiniGameBNWRankPage.py")
		except:
			import exception
			exception.Abort("MiniGameBNWRankPage.LoadWindow.LoadObject")
			
		try:
			self.GetChild("board").SetCloseEvent( ui.__mem_func__(self.Close) )
			self.donateButton = self.GetChild("donate_button")
			self.donateButton.SetEvent(ui.__mem_func__(self.__ClickDonateButton))

			for i in xrange(1, self.BNW_DONATE_RANKING_SHOW_COUNT + 1):
				self.textList.append( { "rankPos" : self.GetChild("rank%d_text" % i),
										"rankName" : self.GetChild("rank%d_name" % i),
										"rankCount" : self.GetChild("rank%d_donate_count_text" % i) } )

			for i, dict in enumerate(self.textList):
				for key, value in dict.iteritems():
					self.textList[i][key].SetText("")

			self.myRankPos = self.GetChild("rank_my_text")
			self.myRankName = self.GetChild("rank_my_name")
			self.myRankCount = self.GetChild("rank_my_donate_count_text")
			self.myRankPos.SetText("")
			self.myRankName.SetText("")
			self.myRankCount.SetText("")
		except:
			import exception
			exception.Abort("MiniGameBNWRankPage.LoadWindow.BindObject")

		self.Hide()
		
	def Close(self):
		self.Hide()
		self.CloseDonateDlg()
		
	def Destroy(self):
		self.isLoaded = 0

		for i, dict in enumerate(self.textList):
			for key, value in dict.iteritems():
				self.textList[i][key] = None
				
		self.myRankPos = None
		self.myRankName = None
		self.myRankCount = None
		
		self.donateButton = None
		self.CloseDonateDlg()
		
	def OnPressEscapeKey(self):
		self.Close()
		return True	
		
	def __ClickDonateButton(self):
		if None == self.donateQuestionDialog:
			self.donateQuestionDialog = uicommon.QuestionDialog2()
			self.donateQuestionDialog.SetText1(localeinfo.MINI_GAME_BNW_DONATE_QUESTION1)
			self.donateQuestionDialog.SetText2(localeinfo.MINI_GAME_BNW_DONATE_QUESTION2)
			self.donateQuestionDialog.SetAcceptEvent(ui.__mem_func__(self.__DonateAccept))
			self.donateQuestionDialog.SetCancelEvent(ui.__mem_func__(self.__DonateCancel))
			w,h = self.donateQuestionDialog.GetTextSize()
			self.donateQuestionDialog.SetWidth( w + 80 )
				
		self.donateQuestionDialog.Open()
	
	def CloseDonateDlg(self):
		if self.donateQuestionDialog:
			self.donateQuestionDialog.Close() 
			self.donateQuestionDialog = None
	
	def __DonateAccept(self):
		net.SendMiniGameBNW(4)
		self.CloseDonateDlg()
	
	def __DonateCancel(self):
		self.CloseDonateDlg()
				
	def Show(self):
		ui.ScriptWindow.Show(self)

	def ClearRanking(self):
		for i, dict in enumerate(self.textList):
			for key, value in dict.iteritems():
				self.textList[i][key].SetText("")

		self.myRankPos.SetText("")
		self.myRankName.SetText("")
		self.myRankCount.SetText("")

	def AddRanking(self, position, isMain, name, donations):
		if isMain and name == playerm2g2.GetName():
			self.myRankPos.SetText(str(position))
			self.myRankName.SetText(str(name))
			self.myRankCount.SetText(str(donations))

		realPos = position - 1
		if realPos < len(self.textList):
			self.textList[realPos]["rankPos"].SetText(str(position))
			self.textList[realPos]["rankName"].SetText(str(name))
			self.textList[realPos]["rankCount"].SetText(str(donations))

	def UpdateRanking(self):
		currentText = int(self.myRankCount.GetText())
		self.myRankCount.SetText(str(currentText + 1))
		
class BNWWaitingPage(ui.ScriptWindow):
	VISIBLE_LINE_COUNT = 15

	class DescriptionBox(ui.Window):
		def __init__(self):
			ui.Window.__init__(self)
			self.descIndex = -1
		def __del__(self):
			ui.Window.__del__(self)
		def SetIndex(self, index):
			self.descIndex = index
		def OnRender(self):
			event.RenderEventSet( self.descIndex )
	
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		
		self.isLoaded = 0
		self.SetWindowName("MiniGameBNWDescription")
		
		self.shopButton = None
		self.rankingButton = None
		self.startButton = None
		self.prevButton = None
		self.nextButton = None
		
		self.descBoard = None
		self.descriptionBox = None
		self.descIndex = -1
		self.descY = DEFAULT_DESC_Y

		self.startQuestionDialog	= None
		
		self.__LoadWindow()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)
	
	def __LoadWindow(self):
		if self.isLoaded == 1:
			return
			
		self.isLoaded = 1
		
		try:
			LoadScript(self, "UIScript/MiniGameBNWWaitingPage.py")
		except:
			import exception
			exception.Abort("MiniGameBNWWaitingPage.LoadWindow.LoadObject")
			
		try:
			self.GetChild("board").SetCloseEvent( ui.__mem_func__(self.Close) )
			self.startButton = self.GetChild("game_start_button")
			self.startButton.SetEvent(ui.__mem_func__(self.__ClickStartButton))

			self.shopButton = self.GetChild("reward_trade_button")
			self.shopButton.SetEvent(ui.__mem_func__(self.__ClickShopButton))

			self.rankingButton = self.GetChild("rank_button")
			self.rankingButton.SetEvent(ui.__mem_func__(self.__ClickRankingButton))

			self.descBoard = self.GetChild("desc_board")
			self.descriptionBox = self.DescriptionBox()
			self.descriptionBox.SetParent(self.descBoard)
			self.descriptionBox.Hide()

			self.prevButton = self.GetChild("prev_button")
			self.nextButton = self.GetChild("next_button")
			self.prevButton.SetEvent(ui.__mem_func__(self.PrevDescriptionPage))
			self.nextButton.SetEvent(ui.__mem_func__(self.NextDescriptionPage))

			if localeinfo.IsARABIC():
				self.prevButton.LeftRightReverse()
				self.nextButton.LeftRightReverse()
		except:
			import exception
			exception.Abort("MiniGameBNWWaitingPage.LoadWindow.BindObject")

		self.Hide()
		
	def Close(self):
		self.Hide()
		
		self.CloseStartDlg()
		
		event.ClearEventSet(self.descIndex)
		self.descIndex = -6

		if self.descriptionBox:
			self.descriptionBox.Hide()
						
		self.descY = DEFAULT_DESC_Y
		
	def Destroy(self):
		self.isLoaded = 0
		
		self.shopButton = None
		self.rankingButton = None
		self.startButton = None
		self.prevButton = None
		self.nextButton = None
		
		self.descBoard = None
		self.descriptionBox = None
		self.descIndex = -1
		self.descY = DEFAULT_DESC_Y
		
		self.CloseStartDlg()
		
	def OnPressEscapeKey(self):
		self.Close()
		return True	
		

		
	def __ClickStartButton(self):
		if None == self.startQuestionDialog:
			self.startQuestionDialog = uicommon.QuestionDialog()
			self.startQuestionDialog.SetText(localeinfo.MINI_GAME_BNW_START_QUESTION)
			self.startQuestionDialog.SetAcceptEvent(ui.__mem_func__(self.__StartAccept))
			self.startQuestionDialog.SetCancelEvent(ui.__mem_func__(self.__StartCancel))
			(w, h) = self.startQuestionDialog.GetTextSize()
			self.startQuestionDialog.SetWidth( w + 60 )
				
		self.startQuestionDialog.Open()
	
	def CloseStartDlg(self):
		if self.startQuestionDialog:
			self.startQuestionDialog.Close() 
			self.startQuestionDialog = None
	
	def __StartAccept(self):
		net.SendMiniGameBNW(0)
		chat.AppendChat(chat.CHAT_TYPE_INFO, "SendMiniGameBNW(0)")#dream
	
	def __StartCancel(self):
		self.CloseStartDlg()
				
	def __ClickShopButton(self):
		net.SendMiniGameBNW(2)
		
	def __ClickRankingButton(self):
		net.SendMiniGameBNW(3)
	def Show(self):
		ui.ScriptWindow.Show(self)

		event.ClearEventSet(self.descIndex)
		self.descIndex = event.RegisterEventSet(uiscriptlocale.BNW_EVENT_DESC)
		event.SetFontColor( self.descIndex, 0.7843, 0.7843, 0.7843 )
		event.SetVisibleLineCount( self.descIndex, self.VISIBLE_LINE_COUNT )
		event.SetRestrictedCount(self.descIndex, DESC_WIDTH_COUNT)
		if localeinfo.IsARABIC():
			event.SetEventSetWidth(self.descIndex, self.descBoard.GetWidth() - 350)
		event.Skip(self.descIndex)

		if self.descriptionBox:
			self.descriptionBox.Show()

		if event.GetTotalLineCount(self.descIndex) > self.VISIBLE_LINE_COUNT:
			self.prevButton.Show()
			self.nextButton.Show()
		else:
			self.prevButton.Hide()
			self.nextButton.Hide()
		# total_line = event.GetTotalLineCount(self.descIndex)

		# if localeinfo.IsARABIC():
			# event.SetEventSetWidth(self.descIndex, self.descBoard.GetWidth() - 20)

		# event.SetRestrictedCount(self.descIndex, DESC_WIDTH_COUNT)

		# if self.VISIBLE_LINE_COUNT >= total_line :
			# self.prevButton.Hide()
			# self.nextButton.Hide()
		# else :
			# self.prevButton.Show()
			# self.nextButton.Show()

		# if self.descriptionBox:
			# self.descriptionBox.Show()

	def OnUpdate(self):
		(xposEventSet, yposEventSet) = self.descBoard.GetGlobalPosition()
		event.UpdateEventSet(self.descIndex, xposEventSet + 7 + 335, -(yposEventSet + self.descY))
		self.descriptionBox.SetIndex(self.descIndex)
		
	def PrevDescriptionPage(self):
		curStartLine = event.GetVisibleStartLine(self.descIndex)

		if curStartLine - self.VISIBLE_LINE_COUNT < 0:
			return

		event.SetVisibleStartLine(self.descIndex, curStartLine - self.VISIBLE_LINE_COUNT)
		self.descY += self.VISIBLE_LINE_COUNT * 16

	def NextDescriptionPage(self):
		curStartLine = event.GetVisibleStartLine(self.descIndex)
		lineCount = event.GetLineCount(self.descIndex) + 1
		increaseCount = self.VISIBLE_LINE_COUNT

		if curStartLine + increaseCount >= lineCount:
			increaseCount = lineCount - curStartLine

		if increaseCount < 0 or curStartLine + increaseCount >= lineCount:
			return

		event.SetVisibleStartLine(self.descIndex, curStartLine + increaseCount)
		self.descY -= increaseCount * 16

class BNWGamePage(ui.ScriptWindow):
	BNW_CARD_ODD_NUMBER_COUNT = 4
	BNW_CARD_EVEN_NUMBER_COUNT = 5
	BNW_CARD_NUMBER_COUNT_MAX = 9

	EVENT_TYPE_INSERT_DELAY = 1
	EVENT_TYPE_DELAY = 2
	EVENT_TYPE_SET_TURN = 3
	EVENT_TYPE_CARD_THROW = 4
	EVENT_TYPE_CARD_RESULT = 5
	EVENT_TYPE_CUR_CARD_HIDE = 6
	EVENT_TYPE_END_PROCESS = 7
	EVENT_TYPE_SET_CARD_CLICK_LOCK = 8
	EVENT_TYPE_CARD_FLASH_PROCESS = 9
	EVENT_TYPE_CARD_FLASH_END = 10
	EVENT_TYPE_CUR_CARD_FLASH = 11

	BNW_PLAYER_MAX = 2
	BNW_ALARM_TEXT_GROUP_COUNT = 2
	TEXT_MOVE_SPEED = 3.0
	CARD_MOVE_SPEED = 20.0

	def __init__(self, wndMiniGameBNW):
		import exception

		if not wndMiniGameBNW:
			exception.Abort("wndMiniGameBNW parameter must be set to MiniGameWND")
			return
			
		ui.Window.__init__(self)
		self.__Initialize()
		
		self.wndMiniGameBNW = wndMiniGameBNW
		self.__LoadWindow()

	def __del__(self):
		ui.Window.__del__(self)
		
	def __Initialize(self):
		self.isLoaded = 0
		
		self.wndMiniGameBNW = None
		
		self.board = None
		
		self.playerCards = []
		self.playerCardsOver = []
		self.playerCardsCross = []
		
		self.opponentCards = []
		self.opponentCardsOver = []
		self.opponentCardsCross = []
		
		self.playerName = None
		self.playerScore = None
		self.playerCurCard = None
		self.playerCurCardOver = None
		
		self.opponentName = None
		self.opponentScore = None
		self.opponentCurCard = None
		self.opponentCurCardOver = None
		
		self.playerCurCardAlpha = 1.0
		self.playerCurCardEffect = False
		
		self.overCount = 0
		self.overAlpha = 1.0
		self.overEffect = False
		self.overEffectType = 0
		
		self.cardMoveImage = None
		
		self.winIndex = -1
		self.pickedCard = -1
		self.myScore = 0
		self.randomEvenCards = [0, 2, 4, 6, 8]
		self.randomOddCards = [1, 3, 5, 7]
		
		self.playerIntScore = 0
		self.opponentIntScore = 0
		
		self.nextRoundStart = 0
		
		self.alarmTextTop = None
		self.alarmTextBottom = None
		
		self.isGameEnd = False
		
	def __DestroyObjects(self):
		if self.playerCards:
			del self.playerCards[:]
			
		if self.playerCardsOver:
			del self.playerCardsOver[:]
			
		if self.playerCardsCross:
			del self.playerCardsCross[:]
			
		if self.opponentCards:
			del self.opponentCards[:]
			
		if self.opponentCardsOver:
			del self.opponentCardsOver[:]
			
		if self.opponentCardsCross:
			del self.opponentCardsCross[:]
			
	def Destroy(self):
		self.__DestroyObjects()
		self.__Initialize()
		
	def OnPressEscapeKey(self):
		self.Close()
		return True
		
	def Show(self):
		self.__LoadWindow()
		ui.Window.Show(self)
			
	def Close(self):
		self.Hide()
			
	def __LoadWindow(self):
		if self.isLoaded == 1:
			return
			
		self.isLoaded = 1

		try:
			LoadScript(self, "UIScript/MiniGameBNWGamePage.py")
		except:
			import exception
			exception.Abort("BNWGamePage.LoadWindow.LoadObject")

		try:
			self.__BindObject()
		except:
			import exception
			exception.Abort("BNWGamePage.LoadWindow.__BindObject")

		try:	
			self.__BindEvent()
		except:
			import exception
			exception.Abort("BNWGamePage.LoadWindow.__BindEvent")
			
		self.Hide()
		
	def __BindObject(self):
		self.board = self.GetChild("board")
		for i in xrange(self.BNW_CARD_NUMBER_COUNT_MAX):
			playerCard = self.GetChild("player1_card%d" % i)
			playerCard.SetShowToolTipEvent(ui.__mem_func__(self.OnPlayerCardOver), i)
			playerCard.SetHideToolTipEvent(ui.__mem_func__(self.OnPlayerCardOverOut), i)
			playerCard.SetEvent(ui.__mem_func__(self.OnPlayerCardClick), i)
			
			self.playerCards.append(playerCard)
			self.playerCardsOver.append(self.GetChild("player1_card%d_over" % i))
			self.playerCardsCross.append(self.GetChild("player1_card%d_cross" % i))
			
			self.opponentCards.append(self.GetChild("player2_card%d" % i))
			self.opponentCardsOver.append(self.GetChild("player2_card%d_over" % i))
			self.opponentCardsCross.append(self.GetChild("player2_card%d_cross" % i))
			
		self.playerName = self.GetChild("player1_name_text")
		self.playerScore = self.GetChild("player1_score_text")
		self.playerCurCard = self.GetChild("player1_cur_card")
		self.playerCurCardOver = self.GetChild("player1_cur_card_over")
		
		self.opponentName = self.GetChild("player2_name_text")
		self.opponentScore = self.GetChild("player2_score_text")
		self.opponentCurCard = self.GetChild("player2_cur_card")
		self.opponentCurCardOver = self.GetChild("player2_cur_card_over")
		
		self.cardMoveImage = ui.MoveImageBox()
		self.cardMoveImage.SetParent( self.GetChild("board") )
		self.cardMoveImage.SetMoveSpeed(self.CARD_MOVE_SPEED)
		self.cardMoveImage.Hide()
		
		self.alarmTextTop = self.GetChild("alarm_text_top")
		self.alarmTextBottom = self.GetChild("alarm_text_bottom")
	
	def __BindEvent(self):
		if self.board:
			self.board.SetCloseEvent(ui.__mem_func__(self.Close))
			
	def Clear(self):
		for cardOver in self.playerCardsOver:
			cardOver.Hide()
		
		for cardCross in self.playerCardsCross:
			cardCross.Hide()
			
		for cardOver in self.opponentCardsOver:
			cardOver.Hide()
		
		for cardCross in self.opponentCardsCross:
			cardCross.Hide()
		
		self.playerName.SetText(player.GetName())
		self.playerScore.SetText("0")
		self.playerCurCard.Hide()
		self.playerCurCardOver.Hide()
	
		self.opponentName.SetText(uiscriptlocale.BNW_GAME_UI_COM)
		self.opponentScore.SetText("0")
		self.opponentCurCard.Hide()
		self.opponentCurCardOver.Hide()
		
		self.playerCurCardAlpha = 1.0
		self.playerCurCardEffect = False
		
		self.overCount = 0
		self.overAlpha = 1.0
		self.overEffect = False
		
		self.winIndex = -1
		self.pickedCard = -1
		self.myScore = 0
		
		self.playerIntScore = 0
		self.opponentIntScore = 0
		
		self.nextRoundStart = 0
		
		self.alarmTextTop.Hide()
		self.alarmTextBottom.Hide()
		
		self.isGameEnd = False
		
	def Open(self):
		ui.ScriptWindow.Show(self)
		
		self.EnableOverEffect(True)

	def OnUpdate(self):
		if self.playerCurCardEffect:
			if self.playerCurCardAlpha <= 0.0:
				self.playerCurCardAlpha = 1.0
				
			self.playerCurCardOver.SetAlpha(self.playerCurCardAlpha)
			
			self.playerCurCardAlpha -= 0.015
			
		if self.overEffect:	
			if self.overAlpha <= 0.0:
				if self.overCount >= 1:
					self.DisableOverEffect()
				else:
					self.overAlpha = 1.0
					self.overCount += 1

			if self.overEffectType == self.EVENT_TYPE_INSERT_DELAY:
				for cardOver in self.playerCardsOver:
					cardOver.SetAlpha(self.overAlpha)
			else:
				for cardOver in self.opponentCardsOver:
					cardOver.SetAlpha(self.overAlpha)

			self.overAlpha -= 0.03
			
		if self.nextRoundStart != 0 and app.GetGlobalTime() > self.nextRoundStart:
			self.StartNextRound()
			self.nextRoundStart = 0
			
	def EnablePlayerCurCardEffect(self):
		self.playerCurCardOver.Show()
		
		self.playerCurCardAlpha = 1.0
		self.playerCurCardEffect = True
		
	def DisablePlayerCurCardEffect(self):
		self.playerCurCardAlpha = 1.0
		self.playerCurCardEffect = False
		
		self.playerCurCardOver.Hide()
			
	def EnableOverEffect(self, isPlayer):
		self.overEffectType = self.EVENT_TYPE_INSERT_DELAY if isPlayer else self.EVENT_TYPE_DELAY

		if isPlayer:
			for cardOver in self.playerCardsOver:
				cardOver.Show()
		else:
			for cardOver in self.opponentCardsOver:
				cardOver.Show()	
			
		self.overCount = 0
		self.overAlpha = 1.0
		self.overEffect = True

	def DisableOverEffect(self):
		self.overCount = 0
		self.overAlpha = 1.0
		self.overEffect = False

		if self.overEffectType == self.EVENT_TYPE_INSERT_DELAY:
			for cardOver in self.playerCardsOver:
				cardOver.SetAlpha(1.0)
				cardOver.Hide()
			self.EnablePlayerCurCardEffect()
		elif self.overEffectType == self.EVENT_TYPE_DELAY:
			for cardOver in self.opponentCardsOver:
				cardOver.SetAlpha(1.0)
				cardOver.Hide()

			self.StartMoveOpponentCard()
		
	def OnPlayerCardClick(self, cardNumber):
		if not self.playerCurCardEffect:
			return
			
		if cardNumber >= 0 and cardNumber < self.BNW_CARD_NUMBER_COUNT_MAX and cardNumber < len(self.playerCardsCross):
			if not self.overEffect and not self.playerCardsCross[cardNumber].IsShow():
				net.SendMiniGameBNW(1, cardNumber)

	def OnPlayerCardOver(self, cardNumber):
		if cardNumber >= 0 and cardNumber < self.BNW_CARD_NUMBER_COUNT_MAX and cardNumber < len(self.playerCardsOver) and cardNumber < len(self.playerCardsCross):
			if not self.overEffect and not self.playerCardsCross[cardNumber].IsShow():
				self.playerCardsOver[cardNumber].Show()
			
	def OnPlayerCardOverOut(self, cardNumber):
		if cardNumber >= 0 and cardNumber < self.BNW_CARD_NUMBER_COUNT_MAX and cardNumber < len(self.playerCardsOver):
			if not self.overEffect:
				self.playerCardsOver[cardNumber].Hide()
				
	def CardCompare(self, winIndex, playerCard, opponentCard, myScore):
		self.winIndex = winIndex
		self.pickedCard = opponentCard
		self.myScore = myScore

		if playerCard >= 0 and playerCard < self.BNW_CARD_NUMBER_COUNT_MAX:
			self.DisablePlayerCurCardEffect()
			self.playerCardsCross[playerCard].Show()
			
			self.alarmTextTop.Hide()
			self.alarmTextBottom.Hide()
			
			self.cardMoveImage.LoadImage("d:/ymir work/ui/minigame/bnw/number%d.sub" % playerCard)
			
			(srcX, srcY) = self.playerCards[playerCard].GetLocalPosition()
			self.cardMoveImage.SetPosition(srcX, srcY)
			
			(dstX, dstY) = self.playerCurCard.GetGlobalPosition()
			self.cardMoveImage.SetMovePosition(dstX, dstY)
			
			self.cardMoveImage.Show()
			self.cardMoveImage.MoveStart()
			
			self.cardMoveImage.SetEndMoveEvent(ui.__mem_func__(self.CardMoveEndEvent), True, playerCard)
			
	def CardMoveEndEvent(self, isPlayer, cardIndex):
		self.cardMoveImage.Hide()
		
		if isPlayer:
			self.playerCurCard.LoadImage("d:/ymir work/ui/minigame/bnw/number%d.sub" % cardIndex)
			self.playerCurCard.Show()
			self.EnableOverEffect(False)
		else:
			if cardIndex % 2 == 0:
				self.opponentCurCard.LoadImage("d:/ymir work/ui/minigame/bnw/back_black.sub")
			else:
				self.opponentCurCard.LoadImage("d:/ymir work/ui/minigame/bnw/back_white.sub")
				
			self.opponentCurCard.Show()
			self.CheckWinIndex()
			
	def ShuffleCards(self):
		random.shuffle(self.randomEvenCards)
		random.shuffle(self.randomOddCards)
		
	def GetRealCardIndex(self, cardIndex, isEven):
		realEvenList = [0, 2, 4, 6, 8]
		realOddList = [1, 3, 5, 7]
		
		if isEven:
			return realEvenList[cardIndex]
		else:
			return realOddList[cardIndex]
		
	def StartMoveOpponentCard(self):
		cardindex = -1
		isEven = False
		if self.pickedCard % 2 == 0: # even, search in even
			for i in xrange(len(self.randomEvenCards)):
				if self.randomEvenCards[i] == self.pickedCard:
					cardindex = i
					isEven = True
		else:
			for i in xrange(len(self.randomOddCards)):
				if self.randomOddCards[i] == self.pickedCard:
					cardindex = i
	
		if cardindex != -1:
			if self.pickedCard % 2 == 0:
				self.cardMoveImage.LoadImage("d:/ymir work/ui/minigame/bnw/back_black.sub")
			else:
				self.cardMoveImage.LoadImage("d:/ymir work/ui/minigame/bnw/back_white.sub")
				
			realCardIndex = self.GetRealCardIndex(cardindex, isEven)
			if realCardIndex >= 0 and realCardIndex < self.BNW_CARD_NUMBER_COUNT_MAX:
				self.opponentCardsCross[realCardIndex].Show()
			
			(srcX, srcY) = self.opponentCards[realCardIndex].GetLocalPosition()
			self.cardMoveImage.SetPosition(srcX, srcY)
			
			(dstX, dstY) = self.opponentCurCard.GetGlobalPosition()
			self.cardMoveImage.SetMovePosition(dstX, dstY)
			
			self.cardMoveImage.Show()
			self.cardMoveImage.MoveStart()
			
			self.cardMoveImage.SetEndMoveEvent(ui.__mem_func__(self.CardMoveEndEvent), False, self.pickedCard)
			
	def CheckWinIndex(self):
		if self.winIndex == 0:
			self.opponentIntScore += 1
			self.opponentScore.SetText(str(self.opponentIntScore))
			self.alarmTextTop.SetText(localeinfo.MINI_GAME_BNW_RESULT_LOSE1)
			self.alarmTextBottom.SetText(localeinfo.MINI_GAME_BNW_RESULT_LOSE2)
		elif self.winIndex == 1:
			self.playerIntScore += 1
			self.playerScore.SetText(str(self.playerIntScore))
			self.alarmTextTop.SetText(localeinfo.MINI_GAME_BNW_RESULT_WIN1)
			self.alarmTextBottom.SetText(localeinfo.MINI_GAME_BNW_RESULT_WIN2)
		else:
			self.alarmTextTop.SetText(localeinfo.MINI_GAME_BNW_RESULT_DRAW1)
			self.alarmTextBottom.SetText(localeinfo.MINI_GAME_BNW_RESULT_DRAW2)
			
		self.alarmTextTop.Show()
		self.alarmTextBottom.Show()
			
		if self.winIndex > 2:
			self.nextRoundStart = app.GetGlobalTime() + 2000
			self.isGameEnd = True
		else:
			self.nextRoundStart = app.GetGlobalTime() + 1000
		
	def StartNextRound(self):
		self.playerCurCard.Hide()
		self.opponentCurCard.Hide()
		
		if self.isGameEnd:
			if self.wndMiniGameBNW:
				self.wndMiniGameBNW.FinishGame(self.winIndex, self.myScore)
		else:
			self.EnableOverEffect(True)
		
class MiniGameBNW(ui.Window):
	wndWaitingPage		= None
	wndGamePage			= None
	
	def __init__(self):
		ui.Window.__init__(self)
		
		self.finishPopup = None
		
		self.wndRankingPage = BNWRankingPage()
		self.wndWaitingPage = BNWWaitingPage()
		self.wndGamePage = BNWGamePage(self)
		
		self.isPlaying = False

	def __del__(self):
		ui.Window.__del__(self)
		
	def Destroy(self):
		if self.wndRankingPage:
			self.wndRankingPage.Destroy()
			self.wndRankingPage = None
			
		if self.wndWaitingPage:
			self.wndWaitingPage.Destroy()
			self.wndWaitingPage = None
			
		if self.wndGamePage:
			self.wndGamePage.Destroy()
			self.wndGamePage = None
			
		if self.finishPopup:
			self.finishPopup.Destroy()
			self.finishPopup = None
			
		self.isPlaying = False
		
	def IsPlaying(self):
		return self.isPlaying
		
	def Open(self):
		if self.wndGamePage:
			if self.wndGamePage.IsShow():
				return

		if self.isPlaying:
			if self.wndGamePage:
				self.wndGamePage.Show()
		else:
			if self.wndWaitingPage:
				self.wndWaitingPage.Show()

	def Close(self):
		if self.wndRankingPage:
			if self.wndRankingPage.IsShow():
				self.wndRankingPage.Close()
				
		if self.wndWaitingPage:
			if self.wndWaitingPage.IsShow():
				self.wndWaitingPage.Close()

		if self.wndGamePage:
			if self.wndGamePage.IsShow():
				self.wndGamePage.Close()
				
	def GameStart(self):
		if self.wndWaitingPage:
			if self.wndWaitingPage.IsShow():
				self.wndWaitingPage.Close()
	
		if self.wndGamePage:
			self.wndGamePage.Clear()
		
			self.isPlaying = True
			
			self.wndGamePage.ShuffleCards()
			self.wndGamePage.Open()

	def GameEnd(self):
		if self.wndGamePage:
			self.isPlaying = False
			
			self.wndGamePage.Clear()
			self.wndGamePage.Close()
			
	def CardCompare(self, winIndex, playerCard, opponentCard, myScore):
		if self.wndGamePage:
			self.wndGamePage.CardCompare(winIndex, playerCard, opponentCard, myScore)
			
	def FinishGame(self, winIndex, myScore):
		self.GameEnd()
		
		if not self.finishPopup:
			self.finishPopup = uicommon.PopupDialog2()
			
		if winIndex == 3:
			self.finishPopup.SetText1(localeinfo.MINI_GAME_BNW_GAME_RESULT_WIN % myScore)
		elif winIndex == 4:
			self.finishPopup.SetText1(localeinfo.MINI_GAME_BNW_GAME_RESULT_LOSE % myScore)
		elif winIndex == 5:
			self.finishPopup.SetText1(localeinfo.MINI_GAME_BNW_GAME_RESULT_DRAW % myScore)
			
		self.finishPopup.SetText2(localeinfo.MINI_GAME_BNW_GAME_RESULT_SCORE % myScore)
		self.finishPopup.Open()

	def AddRanking(self, position, isMain, name, donations):
		if self.wndRankingPage:
			self.wndRankingPage.AddRanking(position, isMain, name, donations)

	def OpenRanking(self):
		self.Close()
		
		if self.wndRankingPage:
			self.wndRankingPage.Show()
			
	def UpdateRanking(self):
		if self.wndRankingPage:
			self.wndRankingPage.UpdateRanking()

	def ClearRanking(self):
		if self.wndRankingPage:
			self.wndRankingPage.ClearRanking()