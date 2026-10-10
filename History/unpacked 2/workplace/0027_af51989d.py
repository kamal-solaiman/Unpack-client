# coding: latin_1

import app

import item
import ui
import ingamewikiui
import localeinfo
import wiki
import wndMgr

class InGameWiki(ui.Window):
	def __init__(self):
		self.searchEdit = None
		
		ui.Window.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.SetWindowName("InGameWiki")
		wiki.RegisterClass(self)
		
		self.objList = {}
		self.windowHistory = []
		self.currSelected = 0
		self.IsOpenWiki = 0
		self.BuildUI()
		self.SetCenterPosition()

		# Item shop catalog + wheel odds are server-pushed, not baked. Ask for
		# them now: this window is built lazily on first open, so players who
		# never open the wiki never pay for it. Guarded because a failure here
		# would otherwise abort wiki construction entirely.
		if app.USE_EXTENDED_WIKI_USAGE:
			try:
				import ingamewikipremium
				ingamewikipremium.Prefetch()
			except Exception:
				import dbg, traceback
				dbg.TraceError("wiki premium prefetch: " + traceback.format_exc())

		self.Hide()
	
	def __del__(self):
		wiki.UnregisterClass()
		
		ui.Window.__del__(self)
	
	def Show(self):
		if (self.IsOpenWiki == 0):
			wndMgr.Show(self.hWnd)
			wiki.ShowModelViewManager(True)
		else:
			self.Hide()
			wndMgr.Show(self.hWnd)
			wiki.ShowModelViewManager(True)

		self.IsOpenWiki = 1

	def Hide(self):
		wndMgr.Hide(self.hWnd)
		
		wiki.ShowModelViewManager(False)
		self.IsOpenWiki = 0
		if self.searchEdit:
			self.searchEdit.KillFocus()
	
	def Close(self):
		self.Hide()
	
	def OnPressEscapeKey(self):
		self.Close()
		return True
	
	def BINARY_LoadInfo(self, objID, vnum):
		# import chat
		# chat.AppendChat(1,"gsd %d"%(vnum))
		if objID in self.objList:
			# chat.AppendChat(1,"bbb %d"%(vnum))
			self.objList[objID].NoticeMe()
		# else:
			# chat.AppendChat(1,"aaa %d"%(vnum))

	def BuildUI(self):
		# Wiki redesign (Phase 1: skeleton). When the flag is on, the new
		# landscape layout in ingamewikiui_new.py builds the window. The
		# legacy portrait wiki keeps running unchanged when the flag is off.
		if app.ENABLE_WIKI_REDESIGN:
			import ingamewikiui_new
			ingamewikiui_new.InitMainWindow(self)
			ingamewikiui_new.BuildBaseMain(self)
		else:
			ingamewikiui.InitMainWindow(self)
			ingamewikiui.BuildBaseMain(self)
	
	def OpenSpecialPage(self, oldWindow, vnum, isMonster = False):
		del self.windowHistory[self.currSelected + 1:]

		# Track whether we already hid the previous page so we can revive
		# it if SpecialPageWindow construction throws -- otherwise the wiki
		# stays blank (old page hidden, new page never appended).
		hiddenPrev = False
		hiddenWindow = None

		try:
			if oldWindow:
				del self.windowHistory[:]

				self.currSelected = 0
				self.windowHistory.append(oldWindow)

			if len(self.windowHistory) > 0:
				hiddenWindow = self.windowHistory[-1]
				hiddenWindow.Hide()
				hiddenPrev = True

			newSpec = ingamewikiui.SpecialPageWindow(vnum, isMonster)
			newSpec.AddFlag("attach")
			newSpec.SetParent(self)
			newSpec.SetPosition(ingamewikiui.mainBoardPos[0] + 7, ingamewikiui.mainBoardPos[1] + 7)
			newSpec.Show()

			self.windowHistory.append(newSpec)
			self.currSelected = self.windowHistory.index(newSpec)

			self.prevButt.Enable() if self.currSelected > 0 else self.prevButt.Disable()
			self.nextButt.Disable()
		except ReferenceError:
			# Dead proxy on a stale parent window -- nothing useful to do,
			# leave the wiki as-is. Same legacy behavior the older except
			# arm preserved.
			pass
		except Exception:
			# Any other failure during SpecialPageWindow construction (a
			# bad vnum, a missing asset, a recently regressed import) used
			# to leave the wiki blank because we already hid the previous
			# page. Log the traceback so syserr captures the real cause,
			# then restore the previous page so the player isn't stuck.
			import traceback
			import dbg
			dbg.TraceError(
				"InGameWiki.OpenSpecialPage(vnum=%s, isMonster=%s) failed:\n%s"
				% (vnum, isMonster, traceback.format_exc()))
			if hiddenPrev and hiddenWindow is not None:
				try:
					hiddenWindow.Show()
				except Exception:
					pass

	def OnPressNameEscapeKey(self):
		if not self.searchEdit:
			return

		if not self.searchEdit.IsShowCursor() or self.searchEdit.GetText() == "":
			self.OnPressEscapeKey()
		else:
			self.searchEdit.SetText("")
			if hasattr(self, "searchResults") and self.searchResults:
				self.searchResults.Hide()
			self._HideSearchHint()

	def Search_RefreshResults(self):
		if not hasattr(self, "searchResults") or not self.searchResults:
			return
		typed = self.searchEdit.GetText() or ""
		self.searchResults.Refresh(typed)
		self._UpdateSearchHint(typed)

	def _HideSearchHint(self):
		if hasattr(self, "searchHint") and self.searchHint:
			self.searchHint.SetText("")
			self.searchHint.Hide()

	def _UpdateSearchHint(self, typed):
		# Inline gray hint showing what Tab/Enter will resolve to. Two cases:
		#   PREFIX  : typed is a true prefix of the suggested completion ->
		#             render only the missing suffix right after the typed run
		#             ("Dem" + gray "on Blade").
		#   SUBSTR  : typed is not a prefix but matches the highlighted row's
		#             name elsewhere -- render the FULL name at the edit's
		#             right edge as a "did you mean" hint, since a suffix
		#             would be misleading.
		if not hasattr(self, "searchHint") or not self.searchHint:
			return
		if not typed:
			self._HideSearchHint()
			return
		# TODO: Arabic positioning. The naive (editX + typedW, editY) anchor
		# lands the hint outside the edit -- the RTL engine renders Arabic
		# glyphs differently than the latin caret model assumes, so the
		# suffix needs an anchor derived from the typed text's LEFT edge
		# (= editW - typedW) with SetHorizontalAlignLeft so glyphs flow
		# further left. Until that's wired and tested in-game, skip.
		if localeinfo.IsARABIC():
			self._HideSearchHint()
			return
		# Mirror OnPressSearchTab's lookup order so what Tab autofills and
		# what the hint advertises are always the same string.
		completion = self.searchResults.GetTopPrefixCompletion()
		if not completion:
			completion = self.searchResults.GetHighlightedName()
		if not completion or completion.lower() == typed.lower():
			self._HideSearchHint()
			return

		typedLower = typed.lower()
		completionLower = completion.lower()
		editX, editY = self.searchEdit.GetLocalPosition()

		if completionLower.startswith(typedLower) and len(completion) > len(typed):
			# PREFIX form -- gray suffix flush against typed text.
			self.searchHint.SetText(completion[len(typed):])
			typedW = self.searchEdit.GetTextSize()[0]
			self.searchHint.SetPosition(editX + typedW, editY)
			self.searchHint.Show()
		elif typedLower in completionLower:
			# SUBSTRING form -- full name right-aligned inside the edit so
			# it reads as a separate hint instead of fighting the typed run.
			self.searchHint.SetText(completion)
			editW = self.searchEdit.GetWidth()
			hintW = self.searchHint.GetTextSize()[0]
			self.searchHint.SetPosition(editX + editW - hintW, editY)
			self.searchHint.Show()
		else:
			# Completion doesn't include the typed text at all (shouldn't
			# happen with current indices, but be defensive).
			self._HideSearchHint()

	def OnPressSearchTab(self):
		# Tab fills the box with the HIGHLIGHTED dropdown row (so arrow-nav + Tab agree),
		# falling back to the first-prefix ghost completion when nothing is highlighted.
		if not hasattr(self, "searchResults") or not self.searchResults:
			return
		if not self.searchEdit:
			return
		completion = self.searchResults.GetHighlightedName()
		if not completion:
			completion = self.searchResults.GetTopPrefixCompletion()
		if not completion:
			return
		typed = self.searchEdit.GetText() or ""
		if completion.lower() == typed.lower():
			return
		self.searchEdit.SetText(completion)
		self.Search_RefreshResults()

	def StartSearch(self):
		# Enter in the search box -- pick the first dropdown result.
		if hasattr(self, "searchResults") and self.searchResults:
			self.searchResults.PickFirst()

	def OnSearchResultPicked(self, vnum, isMob):
		# Fired by WikiSearchResults when a row is clicked, or when Enter in
		# the search edit picks the first match.
		vnum = int(vnum)
		self.searchEdit.SetText("")
		self._HideSearchHint()
		self.searchResults.Hide()
		self.CloseBaseWindows()
		if isMob:
			self.OpenSpecialPage(None, vnum, True)
		else:
			item.SelectItem(vnum)
			openVnum = (int(vnum / 10) * 10) if wiki.CanIncrRefineLevel() else vnum
			self.OpenSpecialPage(None, openVnum, False)

	def OpenSpecialWikiPage(self, vnum, isBox, isMonster = False):
		if not self.IsShow():
			self.Show()
			self.SetTop()

		self.CloseBaseWindows()
		if isBox:
			self.mainChestWindow.Show([vnum,])
			#self.OpenSpecialPage(None, vnum, isMonster)
		else:
			self.OpenSpecialPage(None, vnum, isMonster)

	def GoToLanding(self):
		self.CloseBaseWindows()
		self.categ.NotifyCategorySelect(None)
		try:
			self.customPageWindow.LoadFile("landingpage.txt")
		except Exception:
			# Defense in depth: LoadFile is itself hardened, but never let the
			# landing page leave the wiki blank after CloseBaseWindows hid it.
			import traceback, dbg
			dbg.TraceError("InGameWiki.GoToLanding failed:\n" + traceback.format_exc())

	def GoToCustomPage(self, fileName):
		self.CloseBaseWindows()
		self.categ.NotifyCategorySelect(None)
		try:
			self.customPageWindow.LoadFile(fileName)
		except Exception:
			import traceback, dbg
			dbg.TraceError("InGameWiki.GoToCustomPage(%s) failed:\n%s" % (fileName, traceback.format_exc()))

	def OnPressNextButton(self):
		if len(self.windowHistory) - 1 > self.currSelected:
			self.windowHistory[self.currSelected].Hide()
			self.currSelected += 1
			self.windowHistory[self.currSelected].OpenWindow()

			self.prevButt.Enable()
			if len(self.windowHistory) - 1 == self.currSelected:
				self.nextButt.Disable()
	
	def OnPressPrevButton(self):
		if self.currSelected > 0:
			self.windowHistory[self.currSelected].Hide()
			self.currSelected -= 1
			self.windowHistory[self.currSelected].OpenWindow()
			
			self.nextButt.Enable()
			if self.currSelected == 0:
				self.prevButt.Disable()
	
	def OpenDungeonRoute(self, arg):
		# Dungeons category dispatcher. Integer arg -> data-driven dungeon
		# page; string arg -> legacy .txt page (dungeons not yet migrated).
		try:
			dungeonId = int(arg)
		except (TypeError, ValueError):
			self.customPageWindow.LoadFile(arg)
			return
		self.dungeonPageWindow.OpenDungeon(dungeonId)

	def OpenSystemRoute(self, arg):
		# Systems category dispatcher. "PAGE:" entries open dedicated page
		# windows; anything else stays a legacy .txt page.
		if arg == "PAGE:biolog":
			self.biologPageWindow.OpenPage()
			return
		if arg == "PAGE:dragonsoul":
			self.dragonSoulPageWindow.OpenPage()
			return
		if arg == "PAGE:growthpet":
			self.growthPetPageWindow.OpenPage()
			return
		if arg == "PAGE:growthmount":
			self.growthMountPageWindow.OpenPage()
			return
		if arg == "PAGE:gemshop":
			self.gemShopPageWindow.OpenPage()
			return
		if arg == "PAGE:buffi":
			self.buffiPageWindow.OpenPage()
			return
		self.customPageWindow.LoadFile(arg)

	def CloseBaseWindows(self):
		self.mainWeaponWindow.Hide()
		self.mainChestWindow.Hide()
		self.mainBossWindow.Hide()
		self.customPageWindow.Hide()
		self.costumePageWindow.Hide()
		self.dungeonPageWindow.Hide()
		self.biologPageWindow.Hide()
		self.dragonSoulPageWindow.Hide()
		self.growthPetPageWindow.Hide()
		self.growthMountPageWindow.Hide()
		self.gemShopPageWindow.Hide()
		self.buffiPageWindow.Hide()

		if app.USE_EXTENDED_WIKI_CRAFT:
			self.craftItemPageWindow.Hide()

		if app.USE_EXTENDED_WIKI_SHOP:
			self.shopPageWindow.Hide()

		if app.ENABLE_ITEM_SHOPS:
			self.shopItemPageWindow.Hide()

		del self.windowHistory[:]
		self.prevButt.Disable()
		self.nextButt.Disable()
		self.currSelected = 0
