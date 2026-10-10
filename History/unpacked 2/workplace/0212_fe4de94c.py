import app
import ui
import wndMgr
import localeinfo
import net
import player

class CouponWindow(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.IsLoaded = 0
		self.BuildWindow()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)
		
	def BuildWindow(self):
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(250, 200+20)
		self.Board.SetCenterPosition()
		self.Board.AddFlag('movable')
		self.Board.AddFlag('float')
		self.Board.SetTitleName(localeinfo.COUPON_TITLE)
		self.Board.Hide()
		
		self.Background = ui.ThinBoard()
		self.Background.SetParent(self.Board)
		self.Background.SetSize(230, 153+20)
		self.Background.SetPosition(10, 35+2)
		self.Background.Show()
		
		##COUPON NAME EDITLINE
		self.backgroundNameEditline = ui.ImageBox()
		self.backgroundNameEditline.SetParent(self.Background)
		self.backgroundNameEditline.SetPosition(15, 10)
		self.backgroundNameEditline.SetSize(205, 25)
		self.backgroundNameEditline.LoadImage("d:/ymir work/ui/coupon/editline_bg.tga")
		self.backgroundNameEditline.Show()
		
		self.NameEditLine = ui.EditLine()
		self.NameEditLine.SetParent(self.backgroundNameEditline)
		self.NameEditLine.SetSize(200, 20)
		self.NameEditLine.SetPosition(5, 5)
		self.NameEditLine.SetMax(20)
		self.NameEditLine.SetLimitWidth(200)
		self.NameEditLine.SetOverlayCoupon(localeinfo.COUPON_TEXT,190)
		self.NameEditLine.Show()
		##
		
		##DAYS EDITLINE
		self.backgroundDaysEditline = ui.ImageBox()
		self.backgroundDaysEditline.SetParent(self.Background)
		self.backgroundDaysEditline.SetPosition(15, 10+25+10)
		self.backgroundDaysEditline.SetSize(30, 25)
		self.backgroundDaysEditline.LoadImage("d:/ymir work/ui/coupon/editline_bg_thirty.tga")
		self.backgroundDaysEditline.Show()
		
		self.DaysEditLine = ui.EditLine()
		self.DaysEditLine.SetParent(self.backgroundDaysEditline)
		self.DaysEditLine.SetSize(30, 20)
		self.DaysEditLine.SetPosition(-1, 5)
		self.DaysEditLine.SetMax(5)
		self.DaysEditLine.SetLimitWidth(30)
		self.DaysEditLine.SetOverlayCoupon(localeinfo.COUPON_DAYS,20)
		self.DaysEditLine.SetNumberMode()
		self.DaysEditLine.Show()
		##
		
		##VNUM EDITLINE
		self.backgroundVnumEditline = ui.ImageBox()
		self.backgroundVnumEditline.SetParent(self.Background)
		self.backgroundVnumEditline.SetPosition(15+60+15-4-30-5, 10+25+10)
		self.backgroundVnumEditline.SetSize(60, 25)
		self.backgroundVnumEditline.LoadImage("d:/ymir work/ui/coupon/editline_bg_sixty.tga")
		self.backgroundVnumEditline.Show()
		
		self.VnumEditLine = ui.EditLine()
		self.VnumEditLine.SetParent(self.backgroundVnumEditline)
		self.VnumEditLine.SetSize(60, 20)
		self.VnumEditLine.SetPosition(-1, 5)
		self.VnumEditLine.SetMax(10)
		self.VnumEditLine.SetLimitWidth(60)
		self.VnumEditLine.SetOverlayCoupon(localeinfo.COUPON_VNUM,50)
		self.VnumEditLine.SetNumberMode()
		self.VnumEditLine.Show()
		##
		
		##COUNT EDITLINE
		self.backgroundCountEditline = ui.ImageBox()
		self.backgroundCountEditline.SetParent(self.Background)
		self.backgroundCountEditline.SetPosition(15+60+15+60+15-7-30-10, 10+25+10)
		self.backgroundCountEditline.SetSize(35, 25)
		self.backgroundCountEditline.LoadImage("d:/ymir work/ui/coupon/editline_bg_thirtyfive.tga")
		self.backgroundCountEditline.Show()
		
		self.CountEditLine = ui.EditLine()
		self.CountEditLine.SetParent(self.backgroundCountEditline)
		self.CountEditLine.SetSize(35, 20)
		self.CountEditLine.SetPosition(-1, 5)
		self.CountEditLine.SetMax(5)
		self.CountEditLine.SetLimitWidth(35)
		self.CountEditLine.SetOverlayCoupon(localeinfo.COUPON_COUNT,35)
		self.CountEditLine.SetNumberMode()
		self.CountEditLine.Show()
		##
		
		##VALUE EDITLINE
		self.backgroundValueEditline = ui.ImageBox()
		self.backgroundValueEditline.SetParent(self.Background)
		self.backgroundValueEditline.SetPosition(15+60+15+60+15-7, 10+25+10)
		self.backgroundValueEditline.SetSize(60, 25)
		self.backgroundValueEditline.LoadImage("d:/ymir work/ui/coupon/editline_bg_sixty.tga")
		self.backgroundValueEditline.Show()
		
		self.ValueEditLine = ui.EditLine()
		self.ValueEditLine.SetParent(self.backgroundValueEditline)
		self.ValueEditLine.SetSize(60, 20)
		self.ValueEditLine.SetPosition(-1, 5)
		self.ValueEditLine.SetMax(10)
		self.ValueEditLine.SetLimitWidth(60)
		self.ValueEditLine.SetOverlayCoupon(localeinfo.COUPON_VALUE,50)
		self.ValueEditLine.SetNumberMode()
		self.ValueEditLine.Show()
		##
		
		# #SELECT BTN TEXTLINES
		# self.TypeYangTextLine = ui.TextLine()
		# self.TypeYangTextLine.SetParent(self.Background)
		# self.TypeYangTextLine.SetPosition(15+20-2, 10+25+10+30+5)
		# self.TypeYangTextLine.Show()
		
		# self.TypeItemTextLine = ui.TextLine()
		# self.TypeItemTextLine.SetParent(self.Background)
		# self.TypeItemTextLine.SetPosition(15+20+67+2, 10+25+10+30+5)
		# self.TypeItemTextLine.Show()
		
		# self.TypeDcTextLine = ui.TextLine()
		# self.TypeDcTextLine.SetParent(self.Background)
		# self.TypeDcTextLine.SetPosition(15+20+67+67+8, 10+25+10+30+5)
		# self.TypeDcTextLine.Show()
		# ##
		
		##SELECT BTNS
		self.TypeYangBtn = ui.RadioButton()
		self.TypeYangBtn.SetParent(self.Background)
		self.TypeYangBtn.SetPosition(15+20+10-5-4, 10+25+10+10+30+5+5 - 10)
		self.TypeYangBtn.SetUpVisual("d:/ymir work/ui/coupon/yang_1.png")
		self.TypeYangBtn.SetOverVisual("d:/ymir work/ui/coupon/yang_3.png")
		self.TypeYangBtn.SetDownVisual("d:/ymir work/ui/coupon/yang_2.png")
		self.TypeYangBtn.SetText("")
		self.TypeYangBtn.Show()
		
		self.TypeItemBtn = ui.RadioButton()
		self.TypeItemBtn.SetParent(self.Background)
		self.TypeItemBtn.SetPosition(15+20+10+67-5-2, 10+25+10+10+30+5+5 - 10)
		self.TypeItemBtn.SetUpVisual("d:/ymir work/ui/coupon/item_1.png")
		self.TypeItemBtn.SetOverVisual("d:/ymir work/ui/coupon/item_3.png")
		self.TypeItemBtn.SetDownVisual("d:/ymir work/ui/coupon/item_2.png")
		self.TypeItemBtn.SetText("")
		self.TypeItemBtn.Show()
		
		self.TypeDcBtn = ui.RadioButton()
		self.TypeDcBtn.SetParent(self.Background)
		self.TypeDcBtn.SetPosition(15+20+10+67+67-5, 10+25+10+10+30+5+5 - 10)
		self.TypeDcBtn.SetUpVisual("d:/ymir work/ui/coupon/coins_1.png")
		self.TypeDcBtn.SetOverVisual("d:/ymir work/ui/coupon/coins_3.png")
		self.TypeDcBtn.SetDownVisual("d:/ymir work/ui/coupon/coins_2.png")
		self.TypeDcBtn.SetText("")
		self.TypeDcBtn.Show()
		##
		
		self.AcceptButton = ui.Button()
		self.AcceptButton.SetParent(self.Background)
		self.AcceptButton.SetPosition(100+20, 60-5+65+5 +15)
		self.AcceptButton.SetUpVisual("d:/ymir work/ui/coupon/enter_1.png")
		self.AcceptButton.SetOverVisual("d:/ymir work/ui/coupon/enter_2.png")
		self.AcceptButton.SetDownVisual("d:/ymir work/ui/coupon/enter_3.png")
		self.AcceptButton.SetText(localeinfo.PVP_OK)
		self.AcceptButton.SetEvent(lambda : self.AcceptCoupon(self.VnumEditLine.GetDisplayText(), self.ValueEditLine.GetDisplayText(), self.NameEditLine.GetDisplayText(), self.CountEditLine.GetDisplayText(), self.DaysEditLine.GetDisplayText()))
		self.AcceptButton.Show()
		
		self.DeclineButton = ui.Button()
		self.DeclineButton.SetParent(self.Background)
		self.DeclineButton.SetPosition(50-20-5, 60-5+65+5 +15)
		self.DeclineButton.SetUpVisual("d:/ymir work/ui/coupon/cancel_1.png")
		self.DeclineButton.SetOverVisual("d:/ymir work/ui/coupon/cancel_2.png")
		self.DeclineButton.SetDownVisual("d:/ymir work/ui/coupon/cancel_3.png")
		self.DeclineButton.SetText(localeinfo.COUPON_CLEAR)
		self.DeclineButton.SetEvent(lambda : self.ClearCoupon())
		self.DeclineButton.Show()
		
		self.TypeBtn = []
		self.TypeBtn.append(self.TypeYangBtn)
		self.TypeBtn.append(self.TypeItemBtn)
		self.TypeBtn.append(self.TypeDcBtn)

		self.TypeBtn[0].SetEvent(lambda arg = 0 : self.SetType(arg))
		self.TypeBtn[1].SetEvent(lambda arg = 1 : self.SetType(arg))
		self.TypeBtn[2].SetEvent(lambda arg = 2 : self.SetType(arg))
		self.TypeBtn[0].Down()
		self.CurrentType = 0
		
	def OpenWindow(self):
		# if not "[DEV]Thors" in player.GetName():
			# return
			
		if self.IsLoaded == 0:
			self.Board.Show()
		else:
			self.Board.Hide()
		
	def AcceptCoupon(self, vnum, value, coupon, count, days):
		if not vnum:
			vnum = 0
		if not value:
			value = 0
		if not coupon:
			coupon = "none"
		if not count:
			count = 0
		if not days:
			days = 0

		net.SendChatPacket("/create_coupon %d %d %d %s %d %d" % (int(self.CurrentType), int(vnum), int(value), str(coupon), int(count), int(days)))
		self.ClearCoupon()
		
	def SetType(self, cuType):
		self.TypeBtn[self.CurrentType].SetUp()
		self.CurrentType = cuType
		self.TypeBtn[self.CurrentType].Down()
		
	def ClearCoupon(self):
		self.NameEditLine.SetText("")
		self.NameEditLine.SetPlaceHolder("Type your coupon code...")
		self.DaysEditLine.SetText("")
		self.DaysEditLine.SetPlaceHolder("Days")
		self.VnumEditLine.SetText("")
		self.VnumEditLine.SetPlaceHolder("Vnum")
		self.CountEditLine.SetText("")
		self.CountEditLine.SetPlaceHolder("Count")
		self.ValueEditLine.SetText("")
		self.ValueEditLine.SetPlaceHolder("Value")
		self.SetType(0)
		
		
	def Close(self):
		self.Board.Hide()
		
	def Destroy(self):
		self.Board.Hide()