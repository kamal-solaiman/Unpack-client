# coding: latin_1

import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import net
import player

import chr
import ui
import uiscriptlocale
import wndMgr
import miniMap
import localeinfo
import colorinfo
import constinfo
import background
import uicommon
if app.BL_KILL_BAR:
	import playersettingmodule
	import item
if app.ENABLE_MAILBOX:
	import mail
	import uitooltip
if app.ENABLE_ATLAS_BOSS:
	import grp
if app.ENABLE_NEW_ATLAS_BOSS:
	import wiki
if app.ENABLE_EXTENDED_BATTLE_PASS:
	import uibattlepassextended

import systemSetting

if app.WJ_SHOW_PARTY_ON_MINIMAP:
	QUEST_TOOLTIP_COLOR = 0xfff2cb61

class MapTextToolTip(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)

		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetOutline()
		if app.WJ_SHOW_PARTY_ON_MINIMAP:
			if localeinfo.IsARABIC():
				textLine.SetHorizontalAlignLeft()
			else:
				textLine.SetHorizontalAlignRight()
		else:
			textLine.SetHorizontalAlignRight()
		textLine.Show()
		self.textLine = textLine
		if app.ENABLE_ATLAS_BOSS:
			textLine2 = ui.TextLine()
			textLine2.SetParent(self)
			textLine2.SetOutline()
			textLine2.SetHorizontalAlignLeft()
			textLine2.Show()
			self.textLine2 = textLine2

	def __del__(self):
		ui.Window.__del__(self)

	def SetText(self, text):
		self.textLine.SetText(text)

	if app.ENABLE_ATLAS_BOSS:
		def SetText2(self, text):
			self.textLine2.SetText(text)

		def ShowText2(self):
			self.textLine2.Show()

		def HideText2(self):
			self.textLine2.Hide()

	def SetTooltipPosition(self, PosX, PosY):
		if app.ENABLE_ATLAS_BOSS:
			PosY -= 24	
		if app.WJ_SHOW_PARTY_ON_MINIMAP:
			self.textLine.SetPosition(PosX - 5, PosY)
			if app.ENABLE_ATLAS_BOSS:
				self.textLine2.SetPosition(PosX - 5, PosY + 10)	
		else:
			if localeinfo.IsARABIC():
				w, h = self.textLine.GetTextSize()
				self.textLine.SetPosition(PosX - w - 5, PosY)
				if app.ENABLE_ATLAS_BOSS:
					self.textLine2.SetPosition(PosX - w - 5, PosY + 10)				
			else:
				self.textLine.SetPosition(PosX - 5, PosY)

	def SetTextColor(self, TextColor):
		self.textLine.SetPackedFontColor(TextColor)
		if app.ENABLE_ATLAS_BOSS:
			self.textLine2.SetPackedFontColor(TextColor)

	def GetTextSize(self):
		return self.textLine.GetTextSize()

	def SetHorizontalAlignLeft(self):
		if self.textLine:
			self.textLine.SetHorizontalAlignLeft()

class MiniMapTextToolTip(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		textLine = ui.TextLine()
		textLine.SetParent(self)
		textLine.SetOutline()
		textLine.SetHorizontalAlignRight()
		
		textLine.Show()
		self.textLine = textLine

	def __del__(self):
		ui.Window.__del__(self)

	def SetText(self, text):
		self.textLine.SetText(text)

	def SetTooltipPosition(self, PosX, PosY):
		self.textLine.SetPosition(PosX, PosY)

	def SetTextColor(self, TextColor):
		self.textLine.SetPackedFontColor(TextColor)

	def GetTextSize(self):
		return self.textLine.GetTextSize()

if app.ENABLE_NEW_ATLAS_BOSS:
	class BossAtlasTooltip(ui.Window):
		TOOLTIP_WIDTH = 220
		TOOLTIP_PADDING = 10
		LINE_HEIGHT = 18

		def __init__(self):
			ui.Window.__init__(self)
			self.bossVnum = 0
			self.posX = 0
			self.posY = 0
			self.cursedRespawnAt = 0
			self.cursedAlive = False
			self.BuildWindow()

		def __del__(self):
			ui.Window.__del__(self)

		def BuildWindow(self):
			self.board = ui.ThinBoard()
			self.board.SetParent(self)
			self.board.AddFlag("not_pick")
			self.board.Show()

			# Boss name
			self.nameText = ui.TextLine()
			self.nameText.SetParent(self.board)
			self.nameText.SetPosition(self.TOOLTIP_WIDTH / 2, self.TOOLTIP_PADDING)
			self.nameText.SetHorizontalAlignCenter()
			self.nameText.Show()

			# Coordinates
			self.coordText = ui.TextLine()
			self.coordText.SetParent(self.board)
			self.coordText.SetPosition(self.TOOLTIP_WIDTH / 2, self.TOOLTIP_PADDING + self.LINE_HEIGHT)
			self.coordText.SetHorizontalAlignCenter()
			self.coordText.Show()

			# Status/Respawn time
			self.statusText = ui.TextLine()
			self.statusText.SetParent(self.board)
			self.statusText.SetPosition(self.TOOLTIP_WIDTH / 2, self.TOOLTIP_PADDING + self.LINE_HEIGHT * 2)
			self.statusText.SetHorizontalAlignCenter()
			self.statusText.Show()


			# Wiki hint
			self.wikiHint = ui.TextLine()
			self.wikiHint.SetParent(self.board)
			self.wikiHint.SetPosition(self.TOOLTIP_WIDTH / 2, self.TOOLTIP_PADDING + self.LINE_HEIGHT * 3 + 5 + 8)
			self.wikiHint.SetHorizontalAlignCenter()
			self.wikiHint.SetText(localeinfo.ATLAS_BOSS_HINT_WIKI)
			self.wikiHint.Show()

			# Teleport hint
			self.teleportHint = ui.TextLine()
			self.teleportHint.SetParent(self.board)
			self.teleportHint.SetPosition(self.TOOLTIP_WIDTH / 2, self.TOOLTIP_PADDING + self.LINE_HEIGHT * 4 + 7 + 8)
			self.teleportHint.SetHorizontalAlignCenter()
			self.teleportHint.SetText(localeinfo.ATLAS_BOSS_HINT_TELEPORT)
			self.teleportHint.Show()

			# Teleport cost
			self.costText = ui.TextLine()
			self.costText.SetParent(self.board)
			self.costText.SetPosition(self.TOOLTIP_WIDTH / 2, self.TOOLTIP_PADDING + self.LINE_HEIGHT * 5 + 7 + 8)
			self.costText.SetHorizontalAlignCenter()
			self.costText.SetPackedFontColor(grp.GenerateColor(1.0, 0.85, 0.0, 1.0))
			self.costText.SetText(localeinfo.ATLAS_BOSS_TELEPORT_COST)
			self.costText.Show()

			self.AddFlag("not_pick")
			self._UpdateSize()

		def _UpdateSize(self):
			height = self.TOOLTIP_PADDING * 2 + self.LINE_HEIGHT * 7 + 8
			self.board.SetSize(self.TOOLTIP_WIDTH, height)
			self.SetSize(self.TOOLTIP_WIDTH, height)

		def SetBossInfo(self, name, x, y, vnum, isAlive, remainingTime, respawnInterval):
			self.bossVnum = vnum
			self.posX = x
			self.posY = y
			self.cursedRespawnAt = 0
			self.cursedAlive = False
			self.RestoreBossHints()

			self.nameText.SetText(name)
			self.coordText.SetText("%d, %d" % (x, y))

			if isAlive:
				# Show respawn interval (how long it takes to respawn when killed)
				minutes = respawnInterval / 60
				self.statusText.SetText(localeinfo.ATLAS_BOSS_RESPAWN_TIME % minutes)
				self.statusText.SetPackedFontColor(grp.GenerateColor(0.0, 1.0, 0.0, 1.0))
			else:
				# Show countdown until respawn
				minutes = remainingTime / 60
				seconds = remainingTime % 60
				self.statusText.SetText(localeinfo.ATLAS_BOSS_RESPAWN_COUNTDOWN % (minutes, seconds))
				self.statusText.SetPackedFontColor(grp.GenerateColor(1.0, 0.3, 0.3, 1.0))

		def SetCursedInfo(self, name, isAlive, remainSec, stockLeft, stockMax):
			# One language per line: mixing the Arabic boss name with a tag in the
			# same TextLine produces bidi reordering. Numbers get their own line,
			# formatted without spaces so the digit run cannot be split by bidi.
			self.bossVnum = 0
			self.cursedRespawnAt = 0 if isAlive else app.GetGlobalTimeStamp() + remainSec
			self.cursedAlive = isAlive

			self.nameText.SetText(name)
			self.nameText.SetPackedFontColor(grp.GenerateColor(1.0, 0.43, 0.47, 1.0))

			self.coordText.SetText(getattr(localeinfo, "CURSED_ATLAS_TITLE", "[Cursed - CH1]"))
			self.coordText.SetPackedFontColor(grp.GenerateColor(0.86, 0.65, 0.31, 1.0))

			if isAlive:
				self.statusText.SetText(getattr(localeinfo, "CURSED_ATLAS_ALIVE", "Risen now!"))
				self.statusText.SetPackedFontColor(grp.GenerateColor(1.0, 0.35, 0.35, 1.0))
			else:
				self.__RefreshCursedCountdown()

			self.wikiHint.SetText(getattr(localeinfo, "CURSED_ATLAS_SPOTS", "Coin spots left"))
			self.wikiHint.SetPackedFontColor(grp.GenerateColor(0.69, 0.67, 0.55, 1.0))
			self.wikiHint.Show()

			self.teleportHint.SetText("%d/%d" % (stockLeft, stockMax))
			self.teleportHint.SetPackedFontColor(grp.GenerateColor(0.86, 0.65, 0.31, 1.0))
			self.teleportHint.Show()

			self.costText.Hide()

		def __RefreshCursedCountdown(self):
			left = max(0, self.cursedRespawnAt - app.GetGlobalTimeStamp())
			self.statusText.SetText(getattr(localeinfo, "CURSED_ATLAS_RESPAWN", "Rises in: %s") % ("%d:%02d" % (left / 60, left % 60)))
			self.statusText.SetPackedFontColor(grp.GenerateColor(0.6, 0.6, 1.0, 1.0))

		def RestoreBossHints(self):
			self.nameText.SetPackedFontColor(grp.GenerateColor(1.0, 1.0, 1.0, 1.0))
			self.coordText.SetPackedFontColor(grp.GenerateColor(1.0, 1.0, 1.0, 1.0))
			self.wikiHint.SetText(localeinfo.ATLAS_BOSS_HINT_WIKI)
			self.wikiHint.SetPackedFontColor(grp.GenerateColor(1.0, 1.0, 1.0, 1.0))
			self.wikiHint.Show()
			self.teleportHint.SetText(localeinfo.ATLAS_BOSS_HINT_TELEPORT)
			self.teleportHint.SetPackedFontColor(grp.GenerateColor(1.0, 1.0, 1.0, 1.0))
			self.teleportHint.Show()
			self.costText.SetText(localeinfo.ATLAS_BOSS_TELEPORT_COST)
			self.costText.Show()

		def SetTooltipPosition(self, x, y):
			self.SetPosition(x + 10, y + 10)

		def GetBossVnum(self):
			return self.bossVnum

		def GetBossPosition(self):
			return (self.posX, self.posY)

class AtlasWindow(ui.ScriptWindow):
	BOSS_COLOR = grp.GenerateColor(1.0, 1.0, 1.0, 1.0)
	class AtlasRenderer(ui.Window):
		def __init__(self):
			ui.Window.__init__(self)
			self.AddFlag("not_pick")

		def __del__(self):
			ui.Window.__del__(self)

		def OnUpdate(self):
			miniMap.UpdateAtlas()

		def OnRender(self):
			(x, y) = self.GetGlobalPosition()
			fx = float(x)
			fy = float(y)
			miniMap.RenderAtlas(fx, fy)

		def HideAtlas(self):
			miniMap.HideAtlas()

		def ShowAtlas(self):
			miniMap.ShowAtlas()

	def __init__(self):
		self.tooltipInfo = MapTextToolTip()
		self.tooltipInfo.Hide()
		self.infoGuildMark = ui.MarkBox()
		self.infoGuildMark.Hide()
		self.AtlasMainWindow = None
		self.mapName = ""
		self.board = 0
		self.IsShowWindowValue = False
		self.questionDialog = None
		if app.ENABLE_LOCATION_SCROLL_REWORK:
			self.coordText = None
		if app.ENABLE_NEW_ATLAS_BOSS:
			self.bossTooltip = None
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def SetMapName(self, mapName):
		if 949 == app.GetDefaultCodePage():
			try:
				self.board.SetTitleName(localeinfo.MINIMAP_ZONE_NAME_DICT[mapName])
			except:
				pass

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/AtlasWindow.py")
		except:
			import exception
			exception.Abort("AtlasWindow.LoadWindow.LoadScript")

		try:
			self.board = self.GetChild("board")

		except:
			import exception
			exception.Abort("AtlasWindow.LoadWindow.BindObject")

		self.AtlasMainWindow = self.AtlasRenderer()
		self.board.SetCloseEvent(self.Close)
		self.AtlasMainWindow.SetParent(self.board)
		self.AtlasMainWindow.SetPosition(7, 30)
		self.tooltipInfo.SetParent(self.board)
		self.infoGuildMark.SetParent(self.board)
		self.SetPosition(wndMgr.GetScreenWidth() - 136 - 256 - 10 - 165, 78)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - 136 - 256 - 10 - 165, 78)})
		self.board.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.EventMouseLeftButtonUp))#new
		if self.questionDialog != None:
			del self.questionDialog
		
		self.questionDialog = uicommon.QuestionDialog2()
		self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCancelQuestion))
		self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnAcceptQuestion))
		self.questionDialog.iPosX = 0
		self.questionDialog.iPosY = 0
		self.questionDialog.Hide()

		if app.ENABLE_NEW_ATLAS_BOSS:
			if self.bossTooltip != None:
				del self.bossTooltip
			self.bossTooltip = BossAtlasTooltip()
			self.bossTooltip.SetParent(self)
			self.bossTooltip.Hide()

		if app.ENABLE_LOCATION_SCROLL_REWORK:
			# Held on self: SetParent does not keep a child alive.
			self.coordText = ui.TextLine()
			self.coordText.SetParent(self.board)
			self.coordText.SetOutline()
			self.coordText.Hide()

		self.Hide()#endnew

		miniMap.RegisterAtlasWindow(self)

	def Destroy(self):
		miniMap.UnregisterAtlasWindow()
		self.ClearDictionary()
		self.AtlasMainWindow = None
		self.tooltipAtlasClose = 0
		self.tooltipInfo = None
		self.infoGuildMark = None
		if app.ENABLE_LOCATION_SCROLL_REWORK:
			self.coordText = None
		self.board = None
		if self.questionDialog != None:
			del self.questionDialog

		self.questionDialog = None

		if app.ENABLE_NEW_ATLAS_BOSS:
			if self.bossTooltip != None:
				del self.bossTooltip
			self.bossTooltip = None

	def OnCancelQuestion(self):
		if self.questionDialog == None:
			return
		elif not self.questionDialog.IsShow():
			return
		
		self.questionDialog.iPosX = 0
		self.questionDialog.iPosY = 0
		self.questionDialog.Close()

	def OnAcceptQuestion(self):
		if self.questionDialog == None:
			return
		
		net.SendChatPacket("/gotoxy %d %d" % (self.questionDialog.iPosX, self.questionDialog.iPosY))
		self.OnCancelQuestion()

	def OnMoveWindow(self, x, y):
		self.OnCancelQuestion()

	# Clicking bare map does nothing for a player; for a GM it is a free warp to the spot
	# under the cursor. /goto is GM_LOW_WIZARD and takes the same local metre coords the
	# corner readout shows, so no gold and no cooldown -- unlike the player /gotoxy path.
	def __TryGameMasterWarp(self, mouseX, mouseY):
		if not app.ENABLE_LOCATION_SCROLL_REWORK:
			return

		if not chr.IsGameMaster(player.GetMainCharacterIndex()):
			return

		(bGet, localX, localY) = miniMap.GetAtlasPositionFromScreen(mouseX, mouseY)
		if not bGet:
			return

		net.SendChatPacket("/goto %d %d" % (int(localX), int(localY)))

	def EventMouseLeftButtonUp(self):
		(mouseX, mouseY) = wndMgr.GetMousePosition()
		if app.ENABLE_NEW_ATLAS_BOSS:
			(bFind, sName, iPosX, iPosY, dwTextColor, dwGuildID, respawnInterval, remainingTime, vnum, isAlive) = miniMap.GetAtlasInfo(mouseX, mouseY)
		elif app.ENABLE_ATLAS_BOSS:
			(bFind, sName, iPosX, iPosY, dwTextColor, dwGuildID, time) = miniMap.GetAtlasInfo(mouseX, mouseY)
			vnum = 0
		else:
			(bFind, sName, iPosX, iPosY, dwTextColor, dwGuildID) = miniMap.GetAtlasInfo(mouseX, mouseY)
			vnum = 0

		if self.questionDialog.IsShow():
			self.questionDialog.SetTop()

		if False == bFind:
			self.__TryGameMasterWarp(mouseX, mouseY)
			return 1

		# Boss click behavior with ENABLE_NEW_ATLAS_BOSS
		if app.ENABLE_NEW_ATLAS_BOSS and vnum > 0:
			if app.IsPressed(app.DIK_LSHIFT):
				# Shift+Click = Show teleport confirmation with cost
				self.questionDialog.SetText1(localeinfo.ATLASINFO_QUESTIONDIALOG1 % (sName))
				self.questionDialog.SetText2(localeinfo.ATLASINFO_QUESTIONDIALOG2)
				self.questionDialog.iPosX = iPosX
				self.questionDialog.iPosY = iPosY
				self.questionDialog.SetWidth(170 + len(sName * 5))
				self.questionDialog.Open()
			else:
				# Click = Open wiki page
				wikiInst = wiki.GetBaseClass()
				if wikiInst:
					if not wikiInst.IsShow():
						net.ToggleWikiWindow()
					wikiInst.CloseBaseWindows()
					wikiInst.OpenSpecialPage(None, vnum, True)
		else:
			# Original teleport-only behavior for non-boss items
			self.questionDialog.SetText1(localeinfo.ATLASINFO_QUESTIONDIALOG1 % (sName))
			self.questionDialog.SetText2(localeinfo.ATLASINFO_QUESTIONDIALOG2)
			self.questionDialog.iPosX = iPosX
			self.questionDialog.iPosY = iPosY
			self.questionDialog.SetWidth(170 + len(sName * 5))
			self.questionDialog.Open()
		return 1

	if app.ENABLE_LOCATION_SCROLL_REWORK:
		def __UpdateCoordText(self, mouseX, mouseY):
			# The atlas works in coordinates local to the current map, and the module wrapper
			# already applies the /100 display scale - the same numbers the player marker shows.
			# Do NOT run these through GlobalPositionToMapInfo: subtracting the map base a second
			# time is what made this readout wrong.
			(bGet, localX, localY) = miniMap.GetAtlasPositionFromScreen(mouseX, mouseY)

			if not bGet:
				return

			# Parked in a fixed corner rather than trailing the cursor, which sat on top of the
			# map detail the player is trying to read.
			self.coordText.SetText("%d, %d" % (localX, localY))
			self.coordText.SetPosition(14, self.board.GetHeight() - 24)
			self.coordText.Show()

	def OnUpdate(self):
		if not self.tooltipInfo:
			return

		if not self.infoGuildMark:
			return

		self.infoGuildMark.Hide()
		self.tooltipInfo.Hide()

		if app.ENABLE_LOCATION_SCROLL_REWORK and self.coordText:
			self.coordText.Hide()

		if False == self.board.IsIn():
			return

		(mouseX, mouseY) = wndMgr.GetMousePosition()
		time = 0  # Default value for fallback

		if app.ENABLE_LOCATION_SCROLL_REWORK and self.coordText:
			self.__UpdateCoordText(mouseX, mouseY)

		if getattr(app, "ENABLE_CURSED_BOSS", 0) and self.bossTooltip:
			(bCursed, sCursedName, iCursedAlive, iCursedRemain, iCursedStock, iCursedStockMax) = miniMap.GetCursedAtlasInfo(mouseX, mouseY)
			if bCursed:
				(gx, gy) = self.GetGlobalPosition()
				self.tooltipInfo.Hide()
				self.bossTooltip.SetCursedInfo(sCursedName, iCursedAlive != 0, iCursedRemain, iCursedStock, iCursedStockMax)
				self.bossTooltip.SetTooltipPosition(mouseX - gx, mouseY - gy)
				self.bossTooltip.Show()
				self.bossTooltip.SetTop()
				return

		if app.ENABLE_NEW_ATLAS_BOSS:
			(bFind, sName, iPosX, iPosY, dwTextColor, dwGuildID, respawnInterval, remainingTime, vnum, isAlive) = miniMap.GetAtlasInfo(mouseX, mouseY)
		elif app.ENABLE_ATLAS_BOSS:
			(bFind, sName, iPosX, iPosY, dwTextColor, dwGuildID, time) = miniMap.GetAtlasInfo(mouseX, mouseY)
			vnum = 0
		else:
			(bFind, sName, iPosX, iPosY, dwTextColor, dwGuildID) = miniMap.GetAtlasInfo(mouseX, mouseY)
			vnum = 0

		if False == bFind:
			if app.ENABLE_NEW_ATLAS_BOSS and self.bossTooltip:
				self.bossTooltip.Hide()
			return

		if "empty_guild_area" == sName:
			sName = localeinfo.GUILD_EMPTY_AREA

		(x, y) = self.GetGlobalPosition()

		# Boss tooltip with ENABLE_NEW_ATLAS_BOSS
		if app.ENABLE_NEW_ATLAS_BOSS and vnum > 0:
			self.tooltipInfo.Hide()
			self.bossTooltip.SetBossInfo(sName, iPosX, iPosY, vnum, isAlive, remainingTime, respawnInterval)
			self.bossTooltip.SetTooltipPosition(mouseX - x, mouseY - y)
			self.bossTooltip.Show()
			self.bossTooltip.SetTop()
		else:
			if app.ENABLE_NEW_ATLAS_BOSS and self.bossTooltip:
				self.bossTooltip.Hide()

			if localeinfo.IsARABIC() and sName[-1].isalnum():
				self.tooltipInfo.SetText("(%s)%d, %d" % (sName, iPosX, iPosY))
			else:
				self.tooltipInfo.SetText("%s(%d, %d)" % (sName, iPosX, iPosY))

			self.tooltipInfo.SetTooltipPosition(mouseX - x, mouseY - y)

			# Original: Static respawn time display (only when ENABLE_ATLAS_BOSS without NEW)
			if app.ENABLE_ATLAS_BOSS and not app.ENABLE_NEW_ATLAS_BOSS:
				if time > 0:
					self.tooltipInfo.SetText2(localeinfo.MINIMAP_BOSS_RESPAWN_TIME % (time / 60))
					self.tooltipInfo.SetTextColor(self.BOSS_COLOR)
					self.tooltipInfo.ShowText2()
				else:
					self.tooltipInfo.SetTextColor(dwTextColor)
					self.tooltipInfo.HideText2()
			else:
				self.tooltipInfo.SetTextColor(dwTextColor)
				if app.ENABLE_ATLAS_BOSS:
					self.tooltipInfo.HideText2()

			self.tooltipInfo.Show()
			self.tooltipInfo.SetTop()

		if 0 != dwGuildID:
			textWidth, textHeight = self.tooltipInfo.GetTextSize()
			self.infoGuildMark.SetIndex(dwGuildID)
			self.infoGuildMark.SetPosition(mouseX - x - textWidth - 18 - 5, mouseY - y)
			self.infoGuildMark.Show()

	def Hide(self):
		if self.AtlasMainWindow:
			self.AtlasMainWindow.HideAtlas()
			self.AtlasMainWindow.Hide()
		
		self.OnCancelQuestion()
		ui.ScriptWindow.Hide(self)

	def Show(self):
		if self.AtlasMainWindow:
			(bGet, iSizeX, iSizeY) = miniMap.GetAtlasSize()
			if bGet:
				self.SetSize(iSizeX + 15, iSizeY + 38)

				if localeinfo.IsARABIC():
					self.board.SetPosition(iSizeX+15, 0)

				self.board.SetSize(iSizeX + 15, iSizeY + 38)
				self.SetPosition(wndMgr.GetScreenWidth() - 136 - iSizeX - 25 - 200, 78)
				if app.ENABLE_WINDOW_RESIZE:
					self.SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - 136 - iSizeX - 25 - 200, 78)})
				#self.AtlasMainWindow.SetSize(iSizeX, iSizeY)
				self.AtlasMainWindow.ShowAtlas()
				self.AtlasMainWindow.Show()
		ui.ScriptWindow.Show(self)
		self.IsShowWindowValue = True

	def Close(self):
		self.IsShowWindowValue = False
		self.Hide()

	def IsShowWindow(self):
		return self.IsShowWindowValue

	def SetCenterPositionAdjust(self, x, y):
		self.SetPosition((wndMgr.GetScreenWidth() - self.GetWidth()) / 2 + x, (wndMgr.GetScreenHeight() - self.GetHeight()) / 2 + y)

	def OnPressEscapeKey(self):
		self.Close()
		return True

def __RegisterMiniMapColor(type, rgb):
	miniMap.RegisterColor(type, rgb[0], rgb[1], rgb[2])

class MiniMap(ui.ScriptWindow):
	CANNOT_SEE_INFO_MAP_DICT = {
		"metin2_map_monkeydungeon" : False,
		"metin2_map_monkeydungeon_02" : False,
		"metin2_map_monkeydungeon_03" : False,
		"metin2_map_devilsCatacomb" : False,
		"metin2_12zi_stage" : False,
		"metin2_map_maze_dungeon1" : False,
		"metin2_map_maze_dungeon2" : False,
		"metin2_map_maze_dungeon3" : False,
	}

	if app.BL_KILL_BAR:
		KILL_BAR_COOLTIME = 4.0
		KILL_BAR_MOVE_SPEED = 3.0
		KILL_BAR_MOVE_DISTANCE = 33.0
		KILL_BAR_MAX_ITEM = 5

		KILL_BAR_RACE = {
			playersettingmodule.RACE_WARRIOR_M: "|Ekill_bar/warrior_m|e",
			playersettingmodule.RACE_ASSASSIN_W	: "|Ekill_bar/assassin_w|e",
			playersettingmodule.RACE_SURA_M		: "|Ekill_bar/sura_m|e",
			playersettingmodule.RACE_SHAMAN_W	: "|Ekill_bar/shaman_w|e",
			playersettingmodule.RACE_WARRIOR_W	: "|Ekill_bar/warrior_w|e",
			playersettingmodule.RACE_ASSASSIN_M	: "|Ekill_bar/assassin_m|e",
			playersettingmodule.RACE_SURA_W		: "|Ekill_bar/sura_w|e",
			playersettingmodule.RACE_SHAMAN_M	: "|Ekill_bar/shaman_m|e",
		}

		KILL_BAR_WEAPON_TYPE = {
			"FIST": "|Ekill_bar/fist|e",
			item.WEAPON_SWORD: "|Ekill_bar/sword|e",
			item.WEAPON_DAGGER: "|Ekill_bar/dagger|e",
			item.WEAPON_BOW: "|Ekill_bar/bow|e",
			item.WEAPON_TWO_HANDED: "|Ekill_bar/twohand|e",
			item.WEAPON_BELL: "|Ekill_bar/bell|e",
			item.WEAPON_FAN: "|Ekill_bar/fan|e",
		}

	#if app.USE_INGAME_CHANGE_CHANNEL:
	def RefreshServerName(self):
		channelID = net.GetConnectedChannelNum()

		if self.serverinfo:
			if channelID == 99:
				self.serverinfo.SetText("%s, %s" % (net.GetServerInfo(), localeinfo.CHANNEL_99))
			else:
				self.serverinfo.SetText("%s, %s %d" % (net.GetServerInfo(), localeinfo.CHANNEL_NAME, channelID))

	def __init__(self):
		if app.__RANKING_SYSTEM__:
			self.rankingWindow = None
		ui.ScriptWindow.__init__(self)
		self.__Initialize()

		miniMap.Create()
		miniMap.SetScale(2.0)

		self.AtlasWindow = AtlasWindow()
		self.AtlasWindow.LoadWindow()
		self.AtlasWindow.Hide()

		self.tooltipMiniMapOpen = MapTextToolTip()
		self.tooltipMiniMapOpen.SetText(localeinfo.MINIMAP)
		self.tooltipMiniMapOpen.Show()
		self.tooltipMiniMapClose = MapTextToolTip()
		self.tooltipMiniMapClose.SetText(localeinfo.UI_CLOSE)
		self.tooltipMiniMapClose.Show()
		self.tooltipScaleUp = MapTextToolTip()
		self.tooltipScaleUp.SetText(localeinfo.MINIMAP_INC_SCALE)
		self.tooltipScaleUp.Show()
		self.tooltipScaleDown = MapTextToolTip()
		self.tooltipScaleDown.SetText(localeinfo.MINIMAP_DEC_SCALE)
		self.tooltipScaleDown.Show()
		self.tooltipAtlasOpen = MapTextToolTip()
		self.tooltipAtlasOpen.SetText(localeinfo.MINIMAP_SHOW_AREAMAP)
		self.tooltipAtlasOpen.Show()
		
		if app.ENABLE_ULTIMATE_REGEN:
			self.tooltipTrackOpen = MapTextToolTip()
			self.tooltipTrackOpen.SetText(localeinfo.TRACK_WINDOW_TITLE)
			self.tooltipTrackOpen.Show()

		if app.USE_DUNGEON_INFO:
			self.tooltipDungeonInfoOpen = MapTextToolTip()
			self.tooltipDungeonInfoOpen.SetText(uiscriptlocale.DUNGEON_INFO_TITLE)
			self.tooltipDungeonInfoOpen.Show()

		if app.ENABLE_BIOLOG_SYSTEM:
			self.tooltipBioInfoOpen = MapTextToolTip()
			self.tooltipBioInfoOpen.SetText(localeinfo.MINIMAP_SHOW_BIOLOG)
			self.tooltipBioInfoOpen.Show()


		if app.USE_OFFLINESHOP:
			self.tooltipSearchInfoOpen = MapTextToolTip()
			self.tooltipSearchInfoOpen.SetText(localeinfo.MINIMAP_SHOW_SEARCH_INFO)
			self.tooltipSearchInfoOpen.Show()

		if app.__SKILL_TREE__:
			self.tooltipTreeInfoOpen = MapTextToolTip()
			self.tooltipTreeInfoOpen.SetText(localeinfo.MINIMAP_SHOW_TREE_INFO)
			self.tooltipTreeInfoOpen.Show()

		if app.ENABLE_REWARD_SYSTEM:
			self.tooltipRewardInfoOpen = MapTextToolTip()
			self.tooltipRewardInfoOpen.SetText(localeinfo.MINIMAP_SHOW_REWARD_INFO)
			self.tooltipRewardInfoOpen.Show()

		if app.__RANKING_SYSTEM__:
			self.tooltipRankingOpen = MapTextToolTip()
			self.tooltipRankingOpen.SetText(localeinfo.MINIMAP_SHOW_RANKING)
			self.tooltipRankingOpen.Show()

		self.tooltipInfo = MapTextToolTip()
		self.tooltipInfo.Show()

		if miniMap.IsAtlas():
			self.tooltipAtlasOpen.SetText(localeinfo.MINIMAP_SHOW_AREAMAP)
		else:
			self.tooltipAtlasOpen.SetText(localeinfo.MINIMAP_CAN_NOT_SHOW_AREAMAP)

		self.tooltipAtlasOpen.SetHorizontalAlignLeft()
		
		if app.ENABLE_ULTIMATE_REGEN:
			self.tooltipTrackOpen.SetHorizontalAlignLeft()

		if app.USE_DUNGEON_INFO:
			self.tooltipDungeonInfoOpen.SetHorizontalAlignLeft()

		if app.ENABLE_BIOLOG_SYSTEM:
			self.tooltipBioInfoOpen.SetHorizontalAlignLeft()

		if app.USE_OFFLINESHOP:
			self.tooltipSearchInfoOpen.SetHorizontalAlignLeft()

		if app.__SKILL_TREE__:
			self.tooltipTreeInfoOpen.SetHorizontalAlignLeft()

		if app.ENABLE_REWARD_SYSTEM:
			self.tooltipRewardInfoOpen.SetHorizontalAlignLeft()

		if app.__RANKING_SYSTEM__:
			self.tooltipRankingOpen.SetHorizontalAlignLeft()
		if app.ENABLE_MAILBOX:
			self.MailBoxGMButton = None
			self.MailBoxButton = None
			self.MailBoxEffect = None
			self.tooltipMailBoxGM = uitooltip.ToolTip()
			self.tooltipMailBoxGM.Hide()
			self.tooptipMailBox = uitooltip.ToolTip()
			self.tooptipMailBox.Hide()

		self.mapName = ""

		self.isLoaded = 0
		self.canSeeInfo = True

		# AUTOBAN
		self.imprisonmentDuration = 0
		self.imprisonmentEndTime = 0
		self.imprisonmentEndTimeText = ""
		# END_OF_AUTOBAN

	def __del__(self):
		if app.ENABLE_MAILBOX:
			if self.MailBoxGMButton:
				del self.MailBoxGMButton
				self.MailBoxGMButton = None

			if self.tooltipMailBoxGM:
				del self.tooltipMailBoxGM
				self.tooltipMailBoxGM = None

			if self.tooptipMailBox:
				del self.tooptipMailBox
				self.tooptipMailBox = None

		self.dungeonTimeLimitText = None

		miniMap.Destroy()
		ui.ScriptWindow.__del__(self)

	def __Initialize(self):
		self.positionInfo = 0
		self.observerCount = 0

		self.OpenWindow = 0
		self.CloseWindow = 0
		self.ScaleUpButton = 0
		self.ScaleDownButton = 0
		self.MiniMapHideButton = 0
		self.MiniMapShowButton = 0
		self.AtlasShowButton = 0
		if app.ENABLE_ULTIMATE_REGEN:
			self.buttonTrackOpen = 0
			self.tooltipTrackOpen = 0

		if app.USE_DUNGEON_INFO:
			self.DungeonInfoShowButton = 0
			self.tooltipDungeonInfoOpen = 0

		if app.ENABLE_BIOLOG_SYSTEM:
			self.BiologShowButton = 0

		if app.USE_OFFLINESHOP:
			self.SearchShowButton = 0

		if app.__SKILL_TREE__:
			self.TreeShowButton = 0

		if app.ENABLE_REWARD_SYSTEM:
			self.RewardShowButton = 0

		if app.__RANKING_SYSTEM__:
			self.RankingShowButton = 0

		self.tooltipMiniMapOpen = 0
		self.tooltipMiniMapClose = 0
		self.tooltipScaleUp = 0
		self.tooltipScaleDown = 0
		self.tooltipAtlasOpen = 0
		
		if app.__RANKING_SYSTEM__:
			self.tooltipRankingOpen = 0

		if app.ENABLE_BIOLOG_SYSTEM:
			self.tooltipBioInfoOpen = 0
		if app.USE_OFFLINESHOP:
			self.tooltipSearchInfoOpen = 0

		if app.__SKILL_TREE__:
			self.tooltipTreeInfoOpen = 0

		if app.ENABLE_REWARD_SYSTEM:
			self.tooltipRewardInfoOpen = 0

		self.tooltipInfo = None
		self.serverinfo = None

		if app.BL_KILL_BAR:
			self.KillList = list()


		if app.ENABLE_MAILBOX:
			self.MailBoxGMButton = None
			self.MailBoxButton = None
			self.MailBoxEffect = None
			self.tooltipMailBoxGM = None
			self.tooptipMailBox = None

		if app.ENABLE_BIOLOG_SYSTEM:
			self.isFirstOpeningExtBattlePass = False

		if app.USE_SHIP_DEFENSE:
			self.mastGauge = None
			self.mastBoard = None
			self.mastText = None

		# app.USE_NORTHWIND_DEEPS_DUNGEON:
		self.dungeonTimeLimitValue = 0
		self.dungeonTimeLimitText = None

		self.dungeonDebuffLevelPercent = 0
		self.dungeonDebuffLevelEach = 0
		self.dungeonDebuffLevelCount = 0

		self.dungeonDebuffLevelWindow = None

		self.dungeonDebuffLevelText = None
		self.dungeonDebuffLevelTextWidth = 0
		self.dungeonDebuffLevelTextX = -1
		self.dungeonDebuffLevelTextY = -1

	def SetMapName(self, mapName):
		self.mapName = mapName
		self.AtlasWindow.SetMapName(mapName)
		self.canSeeInfo = True
		self.ShowMiniMap()
		self.tooltipMiniMapOpen.SetText(localeinfo.MINIMAP)
		# if self.CANNOT_SEE_INFO_MAP_DICT.has_key(mapName):
			# self.canSeeInfo = False
			# self.HideMiniMap()
			# self.tooltipMiniMapOpen.SetText(localeinfo.MINIMAP_CANNOT_SEE)
		# else:
			# self.canSeeInfo = True
			# self.ShowMiniMap()
			# self.tooltipMiniMapOpen.SetText(localeinfo.MINIMAP)


	# AUTOBAN
	def SetImprisonmentDuration(self, duration):
		self.imprisonmentDuration = duration
		self.imprisonmentEndTime = app.GetGlobalTimeStamp() + duration

		self.__UpdateImprisonmentDurationText()

	def __UpdateImprisonmentDurationText(self):
		restTime = max(self.imprisonmentEndTime - app.GetGlobalTimeStamp(), 0)

		imprisonmentEndTimeText = localeinfo.SecondToDHM(restTime)
		if imprisonmentEndTimeText != self.imprisonmentEndTimeText:
			self.imprisonmentEndTimeText = imprisonmentEndTimeText
			self.serverinfo.SetText("%s: %s" % (uiscriptlocale.AUTOBAN_QUIZ_REST_TIME, self.imprisonmentEndTimeText))
	# END_OF_AUTOBAN

	def Show(self):
		self.__LoadWindow()

		ui.ScriptWindow.Show(self)

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			if localeinfo.IsARABIC():
				pyScrLoader.LoadScriptFile(self, "uiscript/ae_MiniMap.py")
			else:
				pyScrLoader.LoadScriptFile(self, "uiscript/minimap_window.py")
		except:
			import exception
			exception.Abort("MiniMap.LoadWindow.LoadScript")

		try:
			self.OpenWindow = self.GetChild("OpenWindow")
			self.OpenWindowBGI = self.GetChild("OpenWindowBGI")
			self.MiniMapWindow = self.GetChild("MiniMapWindow")
			self.ScaleUpButton = self.GetChild("ScaleUpButton")
			self.ScaleDownButton = self.GetChild("ScaleDownButton")
			self.MiniMapHideButton = self.GetChild("MiniMapHideButton")
			self.AtlasShowButton = self.GetChild("AtlasShowButton")
			self.CloseWindow = self.GetChild("CloseWindow")
			self.MiniMapShowButton = self.GetChild("MiniMapShowButton")
			self.positionInfo = self.GetChild("PositionInfo")
			self.observerCount = self.GetChild("ObserverCount")
			self.serverinfo = self.GetChild("ServerInfo")
			self.rect = self.GetChild("rect")
			
			if app.USE_DUNGEON_INFO:
				self.DungeonInfoShowButton = self.GetChild("DungeonInfoShowButton")

			if app.ENABLE_BIOLOG_SYSTEM:
				self.BiologShowButton = self.GetChild("BiologShowButton")
				
			if app.USE_OFFLINESHOP:
				self.SearchShowButton = self.GetChild("SearchShowButton")

			if app.__SKILL_TREE__:
				self.TreeShowButton = self.GetChild("TreeShowButton")
				self.TreeShowButton.Hide()

			if app.ENABLE_REWARD_SYSTEM:
				self.RewardShowButton = self.GetChild("RewardShowButton")


			if app.__RANKING_SYSTEM__:
				self.RankingShowButton = self.GetChild("RankingShowButton")


			# if localeinfo.IsARABIC():
				# self.OpenWindowBGI.LeftRightReverse()

			if app.ENABLE_OSF_MINIMAP_INFO:
				self.dateTimeTextLine = self.GetChild("DateTimeTextLine")
				self.dateTimeTextLine.SetOutline()

				# self.timeZoneTextLine = self.GetChild("TimeZoneTextLine")
				# self.timeZoneTextLine.SetOutline()


			if app.ENABLE_MAILBOX:
				self.MakeGmMailButton()
				self.MailBoxButton = self.GetChild("MailBoxButton")
				self.MailBoxButton.Hide()
				self.MailBoxEffect = self.GetChild("MailBoxEffect")
				self.MailBoxEffect.Hide()

				if localeinfo.IsARABIC():
					(mailbox_effect_x, mailbox_effect_y) = self.MailBoxEffect.GetLocalPosition()
					self.MailBoxEffect.SetPosition(mailbox_effect_x + 26, mailbox_effect_y)

			if app.USE_SHIP_DEFENSE:
				self.mastBoard = self.GetChild("mast_board_ui")
				self.mastGauge = self.GetChild("mast_hp_gauge_ui")
				self.mastText = self.GetChild("mast_text2_ui")
			else:
				self.GetChild("mast_board_ui").Hide()

			# app.USE_NORTHWIND_DEEPS_DUNGEON:
			self.dungeonTimeLimitValue = 0

			self.dungeonTimeLimitText = self.GetChild("ui_dungeon_time_limit_text")
			self.dungeonTimeLimitText.Hide()

			self.dungeonDebuffLevelPercent = 0
			self.dungeonDebuffLevelEach = 0
			self.dungeonDebuffLevelCount = 0

			self.dungeonDebuffLevelWindow = self.GetChild("ui_dungeon_debuff_level_window")
			self.dungeonDebuffLevelWindow.Hide()

			self.dungeonDebuffLevelText = self.GetChild("ui_dungeon_debuff_level_text")

			if app.USE_CLIP_MASK:
				self.dungeonDebuffLevelText.SetClippingMaskWindow(self.GetChild("ui_dungeon_debuff_level_bg"))

			(self.dungeonDebuffLevelTextX, self.dungeonDebuffLevelTextY) = self.dungeonDebuffLevelText.GetLocalPosition()
			self.dungeonDebuffLevelTextWidth = 0

			if localeinfo.IsARABIC():
				self.dungeonDebuffLevelTextX = -1
		except:
			import exception
			exception.Abort("MiniMap.LoadWindow.Bind")

		if constinfo.MINIMAP_POSITIONINFO_ENABLE == 0:
			self.positionInfo.Hide()

		#if app.USE_INGAME_CHANGE_CHANNEL:
		self.RefreshServerName()
		#else:
		#	self.serverinfo.SetText(net.GetServerInfo())

		self.ScaleUpButton.SetEvent(ui.__mem_func__(self.ScaleUp))
		self.ScaleDownButton.SetEvent(ui.__mem_func__(self.ScaleDown))
		self.MiniMapHideButton.SetEvent(ui.__mem_func__(self.HideMiniMap))
		self.MiniMapShowButton.SetEvent(ui.__mem_func__(self.ShowMiniMap))

		if miniMap.IsAtlas():
			self.AtlasShowButton.SetEvent(ui.__mem_func__(self.ShowAtlas))

		if app.USE_DUNGEON_INFO:
			self.DungeonInfoShowButton.SetEvent(ui.__mem_func__(self.ShowDungeonInfo))

		if app.ENABLE_BIOLOG_SYSTEM:
			self.BiologShowButton.SetEvent(ui.__mem_func__(self.OnClickBioWindow))

		if app.USE_OFFLINESHOP:
			self.SearchShowButton.SetEvent(ui.__mem_func__(self.OpenSearchShop))

		if app.__SKILL_TREE__:
			self.TreeShowButton.SetEvent(ui.__mem_func__(self.OpenSkillTree))

		if app.ENABLE_REWARD_SYSTEM:
			self.RewardShowButton.SetEvent(ui.__mem_func__(self.OpenReward))


#OpenSkillTree

		if app.__RANKING_SYSTEM__:
			self.RankingShowButton.SetEvent(ui.__mem_func__(self.OpenRanking))

		(ButtonPosX, ButtonPosY) = self.MiniMapShowButton.GetGlobalPosition()
		self.tooltipMiniMapOpen.SetTooltipPosition(ButtonPosX + 35, ButtonPosY + 10)

		(ButtonPosX, ButtonPosY) = self.MiniMapHideButton.GetGlobalPosition()
		self.tooltipMiniMapClose.SetTooltipPosition(ButtonPosX + 35, ButtonPosY + 10)

		(ButtonPosX, ButtonPosY) = self.ScaleUpButton.GetGlobalPosition()
		self.tooltipScaleUp.SetTooltipPosition(ButtonPosX + 35, ButtonPosY + 10)

		(ButtonPosX, ButtonPosY) = self.ScaleDownButton.GetGlobalPosition()
		self.tooltipScaleDown.SetTooltipPosition(ButtonPosX + 35, ButtonPosY + 10)

		(ButtonPosX, ButtonPosY) = self.AtlasShowButton.GetGlobalPosition()
		self.tooltipAtlasOpen.SetTooltipPosition(ButtonPosX + 35, ButtonPosY + 10)

		if app.USE_DUNGEON_INFO:
			(ButtonPosX, ButtonPosY) = self.DungeonInfoShowButton.GetGlobalPosition()
			self.tooltipDungeonInfoOpen.SetTooltipPosition(ButtonPosX + 35, ButtonPosY + 10)

		if app.ENABLE_MAILBOX:
			if self.MailBoxButton and self.tooptipMailBox:
				(ButtonPosX, ButtonPosY) = self.MailBoxButton.GetGlobalPosition()
				self.tooptipMailBox.SetToolTipPosition(ButtonPosX + 35, ButtonPosY + 10)
		
		if app.ENABLE_BIOLOG_SYSTEM:
			(ButtonPosX, ButtonPosY) = self.BiologShowButton.GetGlobalPosition()
			self.tooltipBioInfoOpen.SetTooltipPosition(ButtonPosX + 35, ButtonPosY + 10)

		if app.USE_OFFLINESHOP:
			(ButtonPosX, ButtonPosY) = self.SearchShowButton.GetGlobalPosition()
			self.tooltipSearchInfoOpen.SetTooltipPosition(ButtonPosX + 35, ButtonPosY + 10)

		if app.__SKILL_TREE__:
			(ButtonPosX, ButtonPosY) = self.TreeShowButton.GetGlobalPosition()
			self.tooltipTreeInfoOpen.SetTooltipPosition(ButtonPosX + 35, ButtonPosY + 10)

		if app.ENABLE_REWARD_SYSTEM:
			(ButtonPosX, ButtonPosY) = self.RewardShowButton.GetGlobalPosition()
			self.tooltipRewardInfoOpen.SetTooltipPosition(ButtonPosX + 35, ButtonPosY + 10)



		if app.__RANKING_SYSTEM__:
			(ButtonPosX, ButtonPosY) = self.RankingShowButton.GetGlobalPosition()
			self.tooltipRankingOpen.SetTooltipPosition(ButtonPosX +35 , ButtonPosY + 10)

		if app.USE_SHIP_DEFENSE:
			self.mastGauge.SetPercentage(100, 100)
			self.mastBoard.Hide()

		self.ShowMiniMap()

	def Destroy(self):
		if app.USE_SHIP_DEFENSE:
			self.mastGauge = None
			self.mastBoard = None
			self.mastText = None

		self.HideMiniMap()

		self.AtlasWindow.Destroy()
		self.AtlasWindow = None
		if app.BL_KILL_BAR:
			self.KillList = None

		self.ClearDictionary()

		self.__Initialize()

	def UpdateObserverCount(self, observerCount):
		if observerCount>0:
			self.observerCount.Show()
		elif observerCount<=0:
			self.observerCount.Hide()

		self.observerCount.SetText(localeinfo.MINIMAP_OBSERVER_COUNT % observerCount)

	def OnUpdate(self):
		(x, y, z) = player.GetMainCharacterPosition()
		miniMap.Update(x, y)

		self.positionInfo.SetText("(%.0f, %.0f)" % (x/100, y/100))

		if app.ENABLE_OSF_MINIMAP_INFO:
			if self.dateTimeTextLine:
				self.dateTimeTextLine.SetText(app.GetCurrentTime())
				#self.timeZoneTextLine.SetText(app.GetTimeZone())

		if app.ENABLE_RTT_STATISTICS:
			if self.rttTextLine and self.pktLossTextLine:
				rtt = app.GetRTT()
				pktLossPct = app.GetPacketLossPct()

				if rtt > 300:
					self.rttTextLine.SetFontColor((255.00 / 255), (0.00 / 255), (0.00 / 255)) # r, g, b
				elif rtt > 100 and rtt < 300:
					self.rttTextLine.SetFontColor((255.00 / 255), (255.00 / 255), (0.00 / 255)) # r, g, b
				else:
					self.rttTextLine.SetFontColor((0.00 / 255), (255.00 / 255), (0.00 / 255)) # r, g, b

				self.rttTextLine.SetText("Ping: %s%dms" % ("+" if rtt > 999 else "", 999 if rtt > 999 else rtt))
				self.pktLossTextLine.SetText("%.2f%% pkt loss" % (pktLossPct))

		if self.tooltipInfo:
			if 1 == self.MiniMapWindow.IsIn():
				(mouseX, mouseY) = wndMgr.GetMousePosition()
				(bFind, sName, iPosX, iPosY, dwTextColor) = miniMap.GetInfo(mouseX, mouseY)
				if bFind == 0:
					self.tooltipInfo.Hide()
				elif not self.canSeeInfo:
					self.tooltipInfo.SetText("%s(%s)" % (sName, localeinfo.UI_POS_UNKNOWN))
					self.tooltipInfo.SetTooltipPosition(mouseX - 5, mouseY)
					self.tooltipInfo.SetTextColor(dwTextColor)
					self.tooltipInfo.Show()
				else:
					if localeinfo.IsARABIC() and sName[-1].isalnum():
						self.tooltipInfo.SetText("(%s)%d, %d" % (sName, iPosX, iPosY))
					else:
						self.tooltipInfo.SetText("%s(%d, %d)" % (sName, iPosX, iPosY))
					self.tooltipInfo.SetTooltipPosition(mouseX - 5, mouseY)
					self.tooltipInfo.SetTextColor(dwTextColor)
					self.tooltipInfo.Show()
			else:
				self.tooltipInfo.Hide()

			# AUTOBAN
			if self.imprisonmentDuration:
				self.__UpdateImprisonmentDurationText()
			# END_OF_AUTOBAN

		# if app.USE_NORTHWIND_DEEPS_DUNGEON:
		if self.dungeonTimeLimitText.IsShow():
			if self.dungeonTimeLimitValue > app.GetGlobalTimeStamp():
				self.dungeonTimeLimitText.SetText(localeinfo.FormatTime(self.dungeonTimeLimitValue - app.GetGlobalTimeStamp()))
			else:
				self.dungeonTimeLimitText.Hide()

		if True == self.MiniMapShowButton.IsIn():
			self.tooltipMiniMapOpen.Show()
		else:
			self.tooltipMiniMapOpen.Hide()

		if True == self.MiniMapHideButton.IsIn():
			self.tooltipMiniMapClose.Show()
		else:
			self.tooltipMiniMapClose.Hide()

		if True == self.ScaleUpButton.IsIn():
			self.tooltipScaleUp.Show()
		else:
			self.tooltipScaleUp.Hide()

		if True == self.ScaleDownButton.IsIn():
			self.tooltipScaleDown.Show()
		else:
			self.tooltipScaleDown.Hide()

		if True == self.AtlasShowButton.IsIn():
			self.tooltipAtlasOpen.Show()
		else:
			self.tooltipAtlasOpen.Hide()

		if app.BL_KILL_BAR:
			if self.KillList:
				currentTime = app.GetTime()
				newKillList = []

				for obj in self.KillList:
					remainingTime = obj["CoolTime"] - currentTime

					if remainingTime > 0.0:
						(xLocal, yLocal) = obj["ThinBoard"].GetLocalPosition()

						# Smooth move X
						if obj["MOVE_X"] > 0.0:
							moveXStep = min(obj["MOVE_X"], MiniMap.KILL_BAR_MOVE_SPEED)
							obj["ThinBoard"].SetPosition(xLocal - moveXStep, yLocal)
							obj["MOVE_X"] -= moveXStep

						# Smooth move Y
						if obj["MOVE_Y"] > 0.0:
							moveYStep = min(obj["MOVE_Y"], MiniMap.KILL_BAR_MOVE_SPEED)
							obj["ThinBoard"].SetPosition(xLocal, yLocal + moveYStep)
							obj["MOVE_Y"] -= moveYStep

						# Fade out (last 1.0 second)
						fadeOutStart = 1.0  # seconds before disappearing
						if remainingTime < fadeOutStart:
							alpha = remainingTime / fadeOutStart
							alpha = max(0.0, min(alpha, 1.0))
							#obj["TextLine"].SetAlpha(alpha)
							obj["ThinBoard"].SetAlpha(alpha)
							if "TextColor" in obj:
								r, g, b = obj["TextColor"]
								obj["TextLine"].SetFontColor(r * alpha, g * alpha, b * alpha)
						# Keep in list
						newKillList.append(obj)

				# Update list
				self.KillList = newKillList

		if app.USE_DUNGEON_INFO:
			if True == self.DungeonInfoShowButton.IsIn():
				self.tooltipDungeonInfoOpen.Show()
			else:
				self.tooltipDungeonInfoOpen.Hide()

		if app.ENABLE_MAILBOX:
			if self.MailBoxGMButton:
				if True == self.MailBoxGMButton.IsIn():
					self.tooltipMailBoxGM.Show()
				else:
					self.tooltipMailBoxGM.Hide()

			if self.MailBoxButton:
				if True == self.MailBoxButton.IsIn():
					if self.MailBoxEffect:
						self.MailBoxEffect.Hide()
					self.tooptipMailBox.Show()
				else:
					self.tooptipMailBox.Hide()
		
		if app.ENABLE_BIOLOG_SYSTEM:
			if True == self.BiologShowButton.IsIn():
				self.tooltipBioInfoOpen.Show()
			else:
				self.tooltipBioInfoOpen.Hide()

		if app.USE_OFFLINESHOP:
			if True == self.SearchShowButton.IsIn():
				self.tooltipSearchInfoOpen.Show()
			else:
				self.tooltipSearchInfoOpen.Hide()

		if app.__SKILL_TREE__:
			if True == self.TreeShowButton.IsIn():
				self.tooltipTreeInfoOpen.Show()
			else:
				self.tooltipTreeInfoOpen.Hide()

		if app.ENABLE_REWARD_SYSTEM:
			if True == self.RewardShowButton.IsIn():
				self.tooltipRewardInfoOpen.Show()
			else:
				self.tooltipRewardInfoOpen.Hide()


		if app.__RANKING_SYSTEM__:
			if True == self.RankingShowButton.IsIn():
				self.tooltipRankingOpen.Show()
			else:
				self.tooltipRankingOpen.Hide()

	def OnRender(self):
		(x, y) = self.GetGlobalPosition()
		fx = float(x)
		fy = float(y)
		if app.ENABLE_12ZI and not localeinfo.IsARABIC():
			miniMap.Render(fx + 19.0, fy + 5.0)
		else:
			miniMap.Render(fx + 22.0, fy + 13.0)

	def Close(self):
		self.HideMiniMap()

	if app.BL_KILL_BAR:
		def RepositionKillBar(self, obj):
			obj["MOVE_Y"] += MiniMap.KILL_BAR_MOVE_DISTANCE
			return obj

		def AddKillInfo(self, killer, victim, killer_race, victim_race, weapon_type, color_type):
			if len(self.KillList) >= MiniMap.KILL_BAR_MAX_ITEM:
				self.KillList.sort(
					key=lambda obj: obj["CoolTime"], reverse=True)
				del self.KillList[-1]
			
			if self.KillList:
				self.KillList = map(self.RepositionKillBar, self.KillList)

			width = 30
			height = 10
			base_x = 20
			base_y = 230

			TBoard = ui.ThinBoard()
			TBoard.SetParent(self)
			TBoard.SetSize(width, height)
			TBoard.SetPosition(base_x, base_y)
			TBoard.Show()

			KillText = ui.TextLine()
			if killer_race <= 10:
				arrow = "<-" if color_type in (0, 1, 2) else "->"
				KillText.SetText(" {} {} {} {} ".format(
					victim,
					arrow,
					MiniMap.KILL_BAR_WEAPON_TYPE.get(int(weapon_type),MiniMap.KILL_BAR_WEAPON_TYPE.get("FIST")),
					killer
					#MiniMap.KILL_BAR_RACE.get(int(victim_race), ""),
					#MiniMap.KILL_BAR_RACE.get(int(killer_race), ""),
				))
			else:
				KillText.SetText(" {}  |Ekill_bar/monster|e ".format(killer))


			KillText.SetParent(TBoard)
			KillText.SetWindowHorizontalAlignCenter()
			KillText.SetWindowVerticalAlignCenter()
			KillText.SetHorizontalAlignCenter()
			KillText.SetVerticalAlignCenter()

			if color_type == 1:
				textColor = (0.0, 0.8, 1.0)  # Blue (Party)
			elif color_type == 2:
				textColor = (0.0, 1.0, 0.0)  # Green (Guild)
			elif color_type == 3:
				textColor = (1.0, 0.0, 0.0)  # Red (Guild dead)
			else:
				textColor = (1.0, 1.0, 1.0)  # White (Normal)

			# Set color
			KillText.SetFontColor(*textColor)
				
			KillText.Show()

			size_x, size_y = KillText.GetTextSize()
			TBoard.SetSize(size_x + width, height)
			TBoard.SetPosition((base_x + 120) - size_x, base_y)

			KillDict = dict()
			KillDict["ThinBoard"] = TBoard
			KillDict["TextLine"] = KillText
			KillDict["CoolTime"] = app.GetTime() + MiniMap.KILL_BAR_COOLTIME
			KillDict["MOVE_X"] = MiniMap.KILL_BAR_MOVE_DISTANCE
			KillDict["MOVE_Y"] = 0.0
			KillDict["TextColor"] = textColor

			self.KillList.append(KillDict)

	def HideMiniMap(self):
		miniMap.Hide()
		self.OpenWindow.Hide()
		self.CloseWindow.Show()

	def ShowMiniMap(self):
		if not self.canSeeInfo:
			return

		miniMap.Show()
		self.OpenWindow.Show()
		self.CloseWindow.Hide()

	if app.ENABLE_ULTIMATE_REGEN:
		def __PressTrackOpen(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.OpenTrackWindow()

	if app.USE_DUNGEON_INFO:
		def ShowDungeonInfo(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.ToggleDungeonInfo()

	if app.ENABLE_EVENT_MANAGER:
		def ToggleInGameEvent(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.ToggleInGameEvent()

	def isShowMiniMap(self):
		return miniMap.isShow()

	def ScaleUp(self):
		miniMap.ScaleUp()

	def ScaleDown(self):
		miniMap.ScaleDown()

	def ShowAtlas(self):
		if not miniMap.IsAtlas():
			return

		if not self.AtlasWindow.IsShow():
			self.AtlasWindow.Show()
		else:
			self.AtlasWindow.Hide()

	def ToggleAtlasWindow(self):
		if not miniMap.IsAtlas():
			return

		if self.AtlasWindow.IsShow():
			self.AtlasWindow.Hide()
		else:
			self.AtlasWindow.Show()

	if app.ENABLE_BIOLOG_SYSTEM:
		def OnClickBioWindow(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.BiologManagerOpen()

	if app.ENABLE_EXTENDED_BATTLE_PASS:
		def ToggleBattlePass(self):
			if self.isFirstOpeningExtBattlePass == False:
				net.SendExtBattlePassAction(1)

			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.ToggleBattlePassExtended()

	if app.USE_OFFLINESHOP:
		def OpenSearchShop(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.wndShopOffline:
				interfaceHandler.wndShopOffline.OpenSearch()

	if app.ENABLE_PVP_ROUTES:
		def ShowRoutes(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler and interfaceHandler.wndRoutesPvPSystem:
				interfaceHandler.wndRoutesPvPSystem.Open()

	if app.__SKILL_TREE__:
		def OpenSkillTree(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.OpenSkillTree()

	if app.ENABLE_REWARD_SYSTEM:
		def OpenReward(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.OpenRewardWindow()

	if app.ENABLE_ASLAN_TELEPORTPANEL:
		def ShowTeleport(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.ToggleTeleportPanel()

	if app.ENABLE_MAILBOX:
		def MiniMapMailProcess(self, type, data):
			if mail.MAILBOX_GC_UNREAD_DATA == type:
				self.MiniMapMailRefresh(data)

			elif mail.MAILBOX_GC_SYSTEM_CLOSE == type:
				self.MiniMapMailSystemClose()

		def MiniMapMailRefresh(self, data):
			(is_flash, total_count, item_count, common_count, is_gm_post_visible) = data

			if 0 == total_count:
				if self.MailBoxButton:
					self.MailBoxButton.Hide()
				if self.MailBoxEffect:
					self.MailBoxEffect.Hide()
			else:
				if self.MailBoxButton:
					self.MailBoxButton.Show()

				if True == is_flash and self.MailBoxEffect:
					self.MailBoxEffect.ResetFrame()
					self.MailBoxEffect.Show()
				else:
					self.MailBoxEffect.Hide()

				if self.tooptipMailBox:
					text1 = localeinfo.MAILBOX_POST_NOT_CONFIRM_INFO_1 % (total_count)
					text2 = localeinfo.MAILBOX_POST_NOT_CONFIRM_INFO_2 % (common_count, item_count)
					self.tooptipMailBox.ClearToolTip()
					self.tooptipMailBox.SetThinBoardSize(11 * len(text1))
					self.tooptipMailBox.AppendTextLine(text1)
					self.tooptipMailBox.AppendTextLine(text2)
			
			self.MailBoxGMButtonVisible(is_gm_post_visible)

		def	MiniMapMailSystemClose(self):
			if self.MailBoxButton:
				self.MailBoxButton.Hide()
			if self.MailBoxEffect:
				self.MailBoxEffect.Hide()
			if self.tooptipMailBox:
				self.tooptipMailBox.Hide()
			if self.MailBoxGMButton:
				self.MailBoxGMButton.Hide()
			if self.tooltipMailBoxGM:
				self.tooltipMailBoxGM.Hide()

		def MakeGmMailButton(self):
			SCREEN_WIDTH = wndMgr.GetScreenWidth()
			# create button
			self.MailBoxGMButton = ui.ExpandedImageBox()
			self.MailBoxGMButton.LoadImage("d:/ymir work/ui/game/mailbox/mailbox_icon_gm.sub")
			self.MailBoxGMButton.SetScale(0.8, 0.8)
			self.MailBoxGMButton.SetPosition(SCREEN_WIDTH - 136 - 30, 0)
			self.MailBoxGMButton.Hide()
			self.MailBoxGMButton.SetEvent(ui.__mem_func__(self.MailBoxGMButtonOverInEvent), "mouse_over_in", 0)
			self.MailBoxGMButton.SetEvent(ui.__mem_func__(self.MailBoxGMButtonOverOutEvent), "mouse_over_out", 0)

			if localeinfo.IsARABIC():
				self.MailBoxGMButton.SetPosition(SCREEN_WIDTH-136-30-10, 0)

			# tooltip setting
			text = localeinfo.MAILBOX_POST_GM_ARRIVE
			self.tooltipMailBoxGM.ClearToolTip()
			self.tooltipMailBoxGM.SetThinBoardSize(11 * len(text))
			self.tooltipMailBoxGM.AppendTextLine(text)

		def MailBoxGMButtonOverInEvent(self):
			if self.tooltipMailBoxGM:
				self.tooltipMailBoxGM.Show()

		def MailBoxGMButtonOverOutEvent(self):
			if self.tooltipMailBoxGM:
				self.tooltipMailBoxGM.Hide()

		def MailBoxGMButtonVisible(self, visible):
			if not self.MailBoxGMButton:
				return
			if not self.tooltipMailBoxGM:
				return

			if True == visible:
				self.MailBoxGMButton.Show()
				self.MailBoxGMButton.SetTop()
			else:
				self.MailBoxGMButton.Hide()
				self.tooltipMailBoxGM.Hide()

	if app.__RANKING_SYSTEM__:
		def OpenRanking(self):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				interfaceHandler.OpenRanking()

	if app.USE_SHIP_DEFENSE:
		def SetMastWindow(self, isON):
			if not self.mastBoard:
				return

			if isON:
				self.mastBoard.Show()
			else:
				self.mastBoard.Hide()

		def SetMastHP(self, hp, maxhp):
			self.mastGauge.SetPercentage(hp, maxhp)
			self.mastText.SetText("%s / %s" % (localeinfo.NumToStr(hp), localeinfo.NumToStr(maxhp)))

	if app.USE_NORTHWIND_DEEPS_DUNGEON:
		def NorthWindDeeps_Timer(self, start_time):
			self.dungeonTimeLimitValue = start_time

			if self.dungeonTimeLimitValue > app.GetGlobalTimeStamp():
				self.dungeonTimeLimitText.SetText(localeinfo.FormatTime(self.dungeonTimeLimitValue - app.GetGlobalTimeStamp()))
				self.dungeonTimeLimitText.Show()
			else:
				self.dungeonTimeLimitText.Hide()

		def OnResetPositionDebuffLevelText(self):
			self.dungeonDebuffLevelText.Hide()

			self.dungeonDebuffLevelText.SetPosition(self.dungeonDebuffLevelTextX, self.dungeonDebuffLevelTextY)

			self.dungeonDebuffLevelText.Show()

			(x, y) = self.dungeonDebuffLevelText.GetGlobalPosition()
			self.dungeonDebuffLevelText.SetMovePosition(x - self.dungeonDebuffLevelTextWidth - 119, y)

			self.dungeonDebuffLevelText.SetEndMoveEvent(ui.__mem_func__(self.OnResetPositionDebuffLevelText))
			self.dungeonDebuffLevelText.MoveStart()

		def NorthWindDeeps_Debuff(self, percent, count, each):
			oldDungeonDebuffLevelCount = self.dungeonDebuffLevelCount

			self.dungeonDebuffLevelPercent = percent
			self.dungeonDebuffLevelEach = each
			self.dungeonDebuffLevelCount = count

			if self.dungeonDebuffLevelCount > 0:
				if oldDungeonDebuffLevelCount != self.dungeonDebuffLevelCount:
					self.dungeonDebuffLevelText.SetText(localeinfo.WHITE_DRAGON_CAVE_COOLING_CURSE.format(self.dungeonDebuffLevelEach, self.dungeonDebuffLevelPercent, self.dungeonDebuffLevelCount))
					self.dungeonDebuffLevelTextWidth = self.dungeonDebuffLevelText.GetTextWidth() + (0 if localeinfo.IsARABIC() else 119)

					if localeinfo.IsARABIC() and self.dungeonDebuffLevelTextX == -1:
						self.dungeonDebuffLevelTextX = 0
						self.dungeonDebuffLevelText.SetPosition(-self.dungeonDebuffLevelTextWidth, self.dungeonDebuffLevelTextY)
						self.dungeonDebuffLevelTextX = self.dungeonDebuffLevelText.GetLocalPosition()[0]

				if not self.dungeonDebuffLevelWindow.IsShow():
					self.dungeonDebuffLevelText.SetPosition(self.dungeonDebuffLevelTextX, self.dungeonDebuffLevelTextY)

					(x, y) = self.dungeonDebuffLevelText.GetGlobalPosition()
					self.dungeonDebuffLevelText.SetMovePosition(x - self.dungeonDebuffLevelTextWidth - 119, y)

					self.dungeonDebuffLevelText.SetEndMoveEvent(ui.__mem_func__(self.OnResetPositionDebuffLevelText))

					self.dungeonDebuffLevelWindow.Show()
					self.dungeonDebuffLevelText.MoveStart()
			elif self.dungeonDebuffLevelWindow.IsShow():
				self.dungeonDebuffLevelWindow.Hide()
				self.dungeonDebuffLevelText.MoveEnd()
