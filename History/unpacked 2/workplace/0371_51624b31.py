# coding: latin_1

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import net

import chat
import grp
import wndMgr
import uicommon
import uiguild
import uitooltip
import ui
import constinfo
import localeinfo

class Window(ui.Window):
	def __init__(self):
		self.role = 0
		ui.Window.__init__(self)

	def __del__(self):
		self.role = 0
		ui.Window.__del__(self)

	def Initialize(self):
		self.main = {}
		self.role = 0
		
		self.main["background"] = ui.ExpandedImageBox()
		self.main["background"].SetParent(self)
		self.main["background"].LoadImage("interfaz/stats_pvp.jpg")
		self.main["background"].SetPosition(wndMgr.GetScreenWidth() - 100, wndMgr.GetScreenHeight() - 178)
		if app.ENABLE_WINDOW_RESIZE:
			self.main["background"].SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - 100, Expr("SCREEN_HEIGHT") - 178)})
		#self.main["background"].SetScale(0.9, 0.9)
		self.main["background"].Show()
		
		self.main["text"] = {}
		
		self.main["text"]["muertes"] = ui.TextLine()
		self.main["text"]["muertes"].SetParent(self.main["background"])
		self.main["text"]["muertes"].SetPosition(52+10, 16)
		self.main["text"]["muertes"].SetFontName("Roman:14")
		self.main["text"]["muertes"].SetPackedFontColor(0xffDE9617)
		self.main["text"]["muertes"].SetHorizontalAlignLeft()
		self.main["text"]["muertes"].SetText("0")
		self.main["text"]["muertes"].Show()
		
		self.main["text"]["puntos"] = ui.TextLine()
		self.main["text"]["puntos"].SetParent(self.main["background"])
		self.main["text"]["puntos"].SetPosition(52+10, 16+29)
		self.main["text"]["puntos"].SetFontName("Roman:14")
		self.main["text"]["puntos"].SetPackedFontColor(0xffDE9617)
		self.main["text"]["puntos"].SetHorizontalAlignLeft()
		self.main["text"]["puntos"].SetText("0")
		self.main["text"]["puntos"].Show()
		
		self.main["text"]["team"] = ui.TextLine()
		self.main["text"]["team"].SetParent(self.main["background"])
		self.main["text"]["team"].SetPosition(52+20, 16+29+29)
		self.main["text"]["team"].SetFontName("Roman:14")
		self.main["text"]["team"].SetPackedFontColor(0xffDE1717)
		self.main["text"]["team"].SetHorizontalAlignLeft()
		self.main["text"]["team"].SetText("Red")
		self.main["text"]["team"].Show()
		
		self.main["text"]["otros"] = ui.TextLine()
		self.main["text"]["otros"].SetParent(self.main["background"])
		self.main["text"]["otros"].SetPosition(52+10, 16+29+29+29)
		self.main["text"]["otros"].SetFontName("Roman:14")
		self.main["text"]["otros"].SetPackedFontColor(0xffDE9617)
		self.main["text"]["otros"].SetHorizontalAlignLeft()
		self.main["text"]["otros"].SetText("0")
		self.main["text"]["otros"].Hide()
		
		self.main["icons"] = {}
		
		self.main["icons"]["muertes"] = ui.ExpandedImageBox()
		self.main["icons"]["muertes"].SetParent(self.main["background"])
		self.main["icons"]["muertes"].SetPosition(22, 12)
		self.main["icons"]["muertes"].LoadImage("interfaz/stats_pvp_kills.png")
		self.main["icons"]["muertes"].Show()
		
		self.main["icons"]["puntos"] = ui.ExpandedImageBox()
		self.main["icons"]["puntos"].SetParent(self.main["background"])
		self.main["icons"]["puntos"].SetPosition(22, 12+29)
		self.main["icons"]["puntos"].LoadImage("interfaz/stats_pvp_points.png")
		self.main["icons"]["puntos"].Show()
		
		self.main["icons"]["team"] = ui.ExpandedImageBox()
		self.main["icons"]["team"].SetParent(self.main["background"])
		self.main["icons"]["team"].SetPosition(22, 12+29+29)
		self.main["icons"]["team"].LoadImage("interfaz/stats_pvp_team.png")
		self.main["icons"]["team"].Show()
		
		self.main["icons"]["otros"] = ui.ExpandedImageBox()
		self.main["icons"]["otros"].SetParent(self.main["background"])
		self.main["icons"]["otros"].SetPosition(22, 12+29+29+29)
		self.main["icons"]["otros"].LoadImage("interfaz/stats_pvp_crystal.png")
		self.main["icons"]["otros"].Hide()
		
		self.main["icons"]["role"] = ui.ExpandedImageBox()
		self.main["icons"]["role"].SetParent(self.main["background"])
		self.main["icons"]["role"].SetPosition(41, 12+29+29+29+31)
		self.main["icons"]["role"].LoadImage("interfaz/stats_pvp_attack.png")
		self.main["icons"]["role"].Hide()
		
	def AddStatsPvP(self, tokens):
		if not tokens[0]:
			self.Hide()
			return

		self.Show()
		if (tokens[0] == 1):
			self.main["background"].LoadImage("interfaz/stats_pvp_minim.jpg")
			self.main["background"].SetPosition(wndMgr.GetScreenWidth() - 100, wndMgr.GetScreenHeight() - 109)
			if app.ENABLE_WINDOW_RESIZE:
				self.main["background"].SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - 100, Expr("SCREEN_HEIGHT") - 109)})
			self.main["icons"]["otros"].Hide()
			self.main["icons"]["role"].Hide()
		elif (tokens[0] == 2):
			self.main["background"].LoadImage("interfaz/stats_pvp.jpg")
			self.main["background"].SetPosition(wndMgr.GetScreenWidth() - 100, wndMgr.GetScreenHeight() - 173)
			if app.ENABLE_WINDOW_RESIZE:
				self.main["background"].SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - 100, Expr("SCREEN_HEIGHT") - 173)})
			self.main["icons"]["otros"].LoadImage("interfaz/stats_pvp_metin.png")
			self.main["icons"]["otros"].Show()
			self.main["text"]["otros"].Show()
			self.main["icons"]["role"].Show()
		elif (tokens[0] == 3):
			self.main["background"].LoadImage("interfaz/stats_pvp_mini.jpg")
			self.main["background"].SetPosition(wndMgr.GetScreenWidth() - 100, wndMgr.GetScreenHeight() - 143)
			if app.ENABLE_WINDOW_RESIZE:
				self.main["background"].SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - 100, Expr("SCREEN_HEIGHT") - 143)})
			self.main["icons"]["otros"].LoadImage("interfaz/stats_pvp_crystal.png")
			self.main["icons"]["otros"].Show()
			self.main["text"]["otros"].Show()
			self.main["icons"]["role"].Hide()
		elif (tokens[0] == 4):
			self.main["background"].LoadImage("interfaz/stats_pvp_mini.jpg")
			self.main["background"].SetPosition(wndMgr.GetScreenWidth() - 100, wndMgr.GetScreenHeight() - 143)
			if app.ENABLE_WINDOW_RESIZE:
				self.main["background"].SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - 100, Expr("SCREEN_HEIGHT") - 143)})
			self.main["icons"]["otros"].LoadImage("interfaz/stats_pvp_flag.png")
			self.main["icons"]["otros"].Show()
			self.main["text"]["otros"].Show()
			self.main["icons"]["role"].Hide()
		
		if (tokens[1] != -1):
			self.main["text"]["muertes"].SetText(str(tokens[1]))
			
		if (tokens[2] != -1):
			self.main["text"]["otros"].SetText(str(tokens[2]))
			
		if (tokens[3] != -1):
			puntos = tokens[3]
			if ((tokens[0] == 1 or tokens[0] == 2 or tokens[0] == 3 or tokens[0] == 4) and puntos > 1000):
				puntos = 1000
			self.main["text"]["puntos"].SetText(str(puntos))
			
		if (tokens[4] != -1):
			if (tokens[4] == 1):
				self.main["text"]["team"].SetPackedFontColor(0xffDE1717)
				self.main["text"]["team"].SetText("Reds")
			elif (tokens[4] == 2):
				self.main["text"]["team"].SetPackedFontColor(0xff177BDE)
				self.main["text"]["team"].SetText("Blue")
			
		if (tokens[5] != -1):
			if (tokens[5] == 1):
				self.main["icons"]["role"].LoadImage("interfaz/stats_pvp_attack.png")
				self.role = 1
			elif (tokens[5] == 2):
				self.main["icons"]["role"].LoadImage("interfaz/stats_pvp_defend.png")
				self.role = 2
				

		#if (tokens[1] != -1 and tokens[3] != -1):
		#	if (tokens[0] == 1):
		#		puntos = tokens[3]
		#		self.main["text"]["puntos"].SetText(str(puntos))
		#	elif (tokens[0] == 2):
		#		puntos = tokens[3]+tokens[1]+tokens[2]*3
		#		if (self.role == 1):
		#			puntos = tokens[3]+tokens[1]*2+tokens[2]*4
		#		elif (self.role == 2):
		#			puntos = tokens[3]+tokens[1]*4+tokens[2]*2
		#		
		#		if puntos > 600:
		#			puntos = 600
		#			
		#		self.main["text"]["puntos"].SetText(str(puntos))
		#	elif (tokens[0] == 3):
		#		puntos = tokens[3]+tokens[2]*15
		#		self.main["text"]["puntos"].SetText(str(puntos))

	def Destroy(self):
		self.ClearDictionary()