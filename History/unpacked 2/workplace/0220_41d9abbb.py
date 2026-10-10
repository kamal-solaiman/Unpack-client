import app
import ui
import wndMgr
import localeinfo
import net

class CouponWindow(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.IsLoaded = 0
		self.BuildWindow()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)
		
	def BuildWindow(self):
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(250, 200)
		self.Board.SetCenterPosition()
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.Board.AddFlag("animated_board")
		self.Board.AddFlag('attach')
		self.Board.AddFlag('movable')
		self.Board.AddFlag('float')
		self.Board.SetTitleName(localeinfo.COUPON_TITLE)
		self.Board.SetCloseEvent(self.Close)
		self.Board.Show()
		
		self.Background = ui.ThinBoard()
		self.Background.SetParent(self.Board)
		self.Background.SetSize(230, 153)
		self.Background.SetPosition(10, 35+2)
		self.Background.Show()

		self.backgroundPic = ui.ImageBox()
		self.backgroundPic.SetParent(self.Background)
		self.backgroundPic.SetSize(215, 52)
		self.backgroundPic.SetPosition(7, 10)
		self.backgroundPic.LoadImage("d:/ymir work/ui/coupon/bg.png")
		self.backgroundPic.Show()


		self.backgroundEditline = ui.ImageBox()
		self.backgroundEditline.SetParent(self.Background)
		self.backgroundEditline.SetPosition(15, 10+60)
		self.backgroundEditline.SetSize(205, 25)
		self.backgroundEditline.LoadImage("d:/ymir work/ui/coupon/editline_bg.tga")
		self.backgroundEditline.Show()
		
		self.EditLine = ui.EditLine()
		self.EditLine.SetParent(self.backgroundEditline)
		self.EditLine.SetSize(200, 20)
		self.EditLine.SetPosition(4, 4)
		self.EditLine.SetMax(20)
		self.EditLine.SetLimitWidth(200)
		self.EditLine.SetOverlayCoupon(localeinfo.COUPON_TEXT,190)
		self.EditLine.Show()
		
		self.AcceptButton = ui.Button()
		self.AcceptButton.SetParent(self.Background)
		self.AcceptButton.SetPosition(100+20, 60-5+60)
		self.AcceptButton.SetUpVisual("d:/ymir work/ui/coupon/enter_1.png")
		self.AcceptButton.SetOverVisual("d:/ymir work/ui/coupon/enter_2.png")
		self.AcceptButton.SetDownVisual("d:/ymir work/ui/coupon/enter_3.png")
		self.AcceptButton.SetText(localeinfo.PVP_OK)
		self.AcceptButton.SetEvent(lambda : self.AcceptCoupon(self.EditLine.GetDisplayText()))
		self.AcceptButton.Show()
		
		self.DeclineButton = ui.Button()
		self.DeclineButton.SetParent(self.Background)
		self.DeclineButton.SetPosition(50-20-5, 60-5+60)
		self.DeclineButton.SetUpVisual("d:/ymir work/ui/coupon/cancel_1.png")
		self.DeclineButton.SetOverVisual("d:/ymir work/ui/coupon/cancel_2.png")
		self.DeclineButton.SetDownVisual("d:/ymir work/ui/coupon/cancel_3.png")
		self.DeclineButton.SetText(localeinfo.COUPON_CLEAR)
		self.DeclineButton.SetEvent(lambda : self.ClearCoupon())
		self.DeclineButton.Show()
		
		#self.CouponText = self.EditLine.GetDisplayText()
		
	def OpenWindow(self):
		if self.IsLoaded == 0:
			self.Board.Show()
		else:
			self.Board.Hide()

	def Open(self):
		self.Board.Show()

	def AcceptCoupon(self, coupon):
		net.SendChatPacket("/coupon %s" % coupon)
		self.ClearCoupon()
		
	def ClearCoupon(self):
		self.EditLine.SetText("")
		
	def Close(self):
		self.Board.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def Destroy(self):
		self.Board.Hide()