# coding: latin_1

import app
import chr
import net
import player

import ui
import shop
import mousemodule
import uicommon
import localeinfo
import chat
import item
import systemSetting 

if app.USE_PREMIUM_FEATURES:
	import constinfo

HAVE_RENDER_TARGET = True
try:
	import renderTarget
except Exception:
	HAVE_RENDER_TARGET = False

PATH_ROOT = "cream/shopbuilder/cosmetic/"
PATH = "cream/shopbuilder/"

class OfflineShopDecoration(ui.ScriptWindow):
	def __init__(self):
		self.SelectedBanner = 0
		self.SelectedDeco = 0
		ui.ScriptWindow.__init__(self, "TOP_MOST")
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

		self.__LoadWindow()

	def Destroy(self):
		if HAVE_RENDER_TARGET and self.ModelPreview:
			self.ModelPreview.Destroy()
			del self.ModelPreview
			self.ModelPreview = None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadWindow(self):
		self.AddFlag("movable")
	
		self.Board = ui.ExpandedImageBox()
		self.Board.SetParent(self)
		self.Board.LoadImage(PATH_ROOT + "bg.png")
		self.Board.AddFlag("not_pick")
		self.Board.Show()
		
		self.SetSize(self.Board.GetWidth(), self.Board.GetHeight())
		
		self.btnClose = ui.MakeButton(self, 165-15, 275, False, PATH_ROOT, "btn_normal.png", "btn_hover.png", "btn_down.png")
		self.btnClose.SetText(localeinfo.OFFLINESHOP_CLOSESHOP)
		self.btnClose.SetEvent(ui.__mem_func__(self.Close))

		self.btnSave = ui.MakeButton(self, 245+10, 275, False, PATH_ROOT, "btn_normal.png", "btn_hover.png", "btn_down.png")
		self.btnSave.SetText(localeinfo.OFFLINESHOP_OK)
		self.btnSave.SetEvent(ui.__mem_func__(self.Close))
		
		if HAVE_RENDER_TARGET:
			self.ModelPreview = ui.RenderTarget()
			self.ModelPreview.SetParent(self)
			self.ModelPreview.SetSize(136, 225)

			# always after setting the size!
			self.ModelPreview.Load()
			self.renderIndex = self.ModelPreview.GetIndex()

			self.ModelPreview.SetPosition(172, 30)
			self.ModelPreview.Show()

			renderTarget.SetVisibility(self.renderIndex, True)
			renderTarget.SelectModel(self.renderIndex, 30000)
		else:
			self.ModelPreview = ui.Window()
			self.ModelPreview.SetParent(self)
			self.ModelPreview.SetSize(136, 225)
			self.ModelPreview.SetPosition(172, 30)
			self.ModelPreview.Show()
			
		self.dictShops = {
		0 : localeinfo.OFFLINESHOP_DECO_1,
		1 : localeinfo.OFFLINESHOP_DECO_2,
		2 : localeinfo.OFFLINESHOP_DECO_3,
		3 : localeinfo.OFFLINESHOP_DECO_4,
		4 : localeinfo.OFFLINESHOP_DECO_5,
		5 : localeinfo.OFFLINESHOP_DECO_6,
		6 : localeinfo.OFFLINESHOP_DECO_7,
		}
	
		self.dictButtons = {}
		for index in xrange(len(self.dictShops)):
			self.dictButtons[index] = ui.MakeButton(self, 16, 43+ index*23, False, PATH_ROOT, "slot_normal.png", "slot_hover.png", "slot_selected.png")
			self.dictButtons[index].SetText(self.dictShops[index])
			self.dictButtons[index].SetEvent(ui.__mem_func__(self.SetRenderTarget), index)

		self.dictBanner = {
		0 : localeinfo.OFFLINESHOP_BANNER_1,
		1 : localeinfo.OFFLINESHOP_BANNER_2,
		2 : localeinfo.OFFLINESHOP_BANNER_3,
		3 : localeinfo.OFFLINESHOP_BANNER_4,
		4 : localeinfo.OFFLINESHOP_BANNER_5,
		5 : localeinfo.OFFLINESHOP_BANNER_6,
		}

		self.BoardBanner = ui.ExpandedImageBox()
		self.BoardBanner.SetParent(self.ModelPreview)
		self.BoardBanner.SetPosition(-1, 5)
		self.BoardBanner.LoadImage(PATH_ROOT  + "banners/1.png")
		self.BoardBanner.SetScale(0.7, 0.7)
		self.BoardBanner.Show()
	
		self.dictButtons2 = {}
		for index in xrange(len(self.dictBanner)):
			self.dictButtons2[index] = ui.MakeButton(self, 319, 43+ index*23, False, PATH_ROOT, "slot_normal.png", "slot_hover.png", "slot_selected.png")
			self.dictButtons2[index].SetText(self.dictBanner[index])
			self.dictButtons2[index].SetEvent(ui.__mem_func__(self.SetBanner), index)

	def SetBanner(self, index):
		self.SelectedBanner = index
		# chat.AppendChat(1, str(self.SelectedBanner))
		
		if index == 0:
			self.BoardBanner.Hide()
			return
	
		self.BoardBanner.LoadImage(PATH_ROOT + "banners/%d.png" % (index - 1))
		self.BoardBanner.SetScale(0.7, 0.7)
		self.BoardBanner.Show()
		
	
	def SetRenderTarget(self, index):
		if HAVE_RENDER_TARGET and self.ModelPreview:
			self.ModelPreview.Show()
			renderTarget.SetVisibility(self.renderIndex, True)
			renderTarget.SelectModel(self.renderIndex, 30000 + index)

		self.SelectedDeco = index
		# chat.AppendChat(1, str(self.SelectedDeco))

	def GetTypeShop(self):
		return self.SelectedDeco

	def GetTypeBanner(self):
		return self.SelectedBanner

	def Show(self):
		ui.ScriptWindow.Show(self)
		self.SetCenterPosition()

	def Close(self):
		if HAVE_RENDER_TARGET and self.ModelPreview:
			self.ModelPreview.Hide()
			renderTarget.SetVisibility(self.renderIndex, False)

		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
