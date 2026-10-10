#author: dracaryS

#static
import ui, math

#dynamic
import app, item, net, wndMgr , localeinfo , uiofflineshop_ae, grp, player
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr

import systemSetting

if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions

IMG_DIR = "spin_wheel/"

# >>> DAILY_ALCHEMY_ORE: enable/disable toggle-button art (replaces the decorative spin image, same slot/size)
TOGGLE_IMG_DIR = "d:/ymir work/ui/game/wheel/"
# <<< DAILY_ALCHEMY_ORE

TOTAL_NEED_KILL_COUNT_NORMAL = 50
TOTAL_NEED_KILL_COUNT_DUNGEON = 10

WHEEL_TYPE_NORMAL = 0
WHEEL_TYPE_MISSION_QUEST = -1  # Special wheel type for mission quest rewards

if app.__SPIN_WHEEL_DUNGEON__:
	WHEEL_TYPE_DUNGEON = WHEEL_TYPE_NORMAL + 1

class InfoWindow(ui.BoardWithTitleBar):
	def __init__(self, wheel_type = WHEEL_TYPE_NORMAL, alchemyRewards = None):
		ui.BoardWithTitleBar.__init__(self)
		self.wheel_type = wheel_type
		# >>> DAILY_ALCHEMY_ORE: server-driven reward list for the normal wheel
		self.alchemyRewards = alchemyRewards if alchemyRewards else []
		# <<< DAILY_ALCHEMY_ORE
		# >>> DAILY_ALCHEMY_ORE: system-help popup (lazily created on first '?' click)
		self.helpWnd = None
		# <<< DAILY_ALCHEMY_ORE
		self.__LoadWindow()
	def Destroy(self):
		# >>> DAILY_ALCHEMY_ORE: tear down the help popup with the window
		hw = getattr(self, "helpWnd", None)
		if hw:
			hw.Close()
			hw.Destroy()
			self.helpWnd = None
		# <<< DAILY_ALCHEMY_ORE
		self.__children = {}
	def __LoadWindow(self):
		self.Destroy()
		
		self.AddFlag("movable")
		self.AddFlag("attach")
		self.AddFlag("float")
		self.SetCloseEvent(self.Close)
		self.SetTitleName(localeinfo.SPINWHEEL_REWARD if self.wheel_type == WHEEL_TYPE_NORMAL else localeinfo.SPINWHEEL_REWARDS_D_INFO)

		bg = CreateWindow(ui.ImageBox(), self, (8, 30), IMG_DIR + "info_bg.png")
		self.__children["bg"] = bg

		backBtn = CreateWindow(ui.Button(), bg, (37, 5))
		backBtn.SetUpVisual(IMG_DIR + "left_01.png")
		backBtn.SetOverVisual(IMG_DIR + "left_02.png")
		backBtn.SetDownVisual(IMG_DIR + "left_03.png")
		backBtn.SAFE_SetEvent(self.__ClickDirection, "back")
		self.__children["backBtn"] = backBtn
	
		nextBtn = CreateWindow(ui.Button(), bg, (176, 5))
		nextBtn.SetUpVisual(IMG_DIR + "right_01.png")
		nextBtn.SetOverVisual(IMG_DIR + "right_02.png")
		nextBtn.SetDownVisual(IMG_DIR + "right_03.png")
		nextBtn.SAFE_SetEvent(self.__ClickDirection, "next")
		self.__children["nextBtn"] = nextBtn

		titleImg = CreateWindow(ui.ImageBox(), bg, (63, 5), IMG_DIR + "level_range_background.png")
		self.__children["titleImg"] = titleImg

		self.__children["titleText"] = CreateWindow(ui.TextLine(), titleImg, (titleImg.GetWidth() / 2, 2), "-", "horizontal:center")

		self.SetSize(8 + bg.GetWidth() + 8, 30 + bg.GetHeight() + 8)
		self.SetCenterPosition()
		# >>> DAILY_ALCHEMY_ORE: "?" system-help button (ore wheel only)
		if app.ENABLE_DAILY_ALCHEMY_ORE and self.wheel_type == WHEEL_TYPE_NORMAL:
			helpBtn = CreateWindow(ui.Button(), self, (12, 8))
			if localeinfo.IsARABIC():
				helpBtn.SetPosition(self.GetWidth() - 12 - 14, 8)
			helpBtn.SetUpVisual(IMG_DIR + "question_mark.png")
			helpBtn.SetOverVisual(IMG_DIR + "question_mark_1.png")
			helpBtn.SetDownVisual(IMG_DIR + "question_mark_2.png")
			helpBtn.SetToolTipText(getattr(localeinfo, "ALCHEMY_HELP_BTN_TIP", "How it works"))
			helpBtn.SAFE_SetEvent(self.__ClickHelp, "mouse_click")
			self.__children["helpBtn"] = helpBtn
		# <<< DAILY_ALCHEMY_ORE
		
		# self.__children["data"] = {
			# # 0 : {
				# # "name" : localeinfo.SPINWHEEL_LEVEL_RANGE % (1,89),
				# # "items" : [[0, 71151, 10], [0, 71084, 5], [0, 70722, 5], [0, 38050, 3], [0, 27987, 1], [0, 50999, 50], [0, 50999, 60], [0, 25040, 2], [1, 30169, 50], [1, 30170, 50], [1, 30171, 50], [1, 70722, 20], [1, 30181, 2], [1, 30184, 1], [2, 30182, 1], [2, 73703, 1], [2, 73704, 1]],
				# # "jackpot" : [3, 60700, 1],
			# # },
			# # 1 : {
				# # "name" : localeinfo.SPINWHEEL_LEVEL_RANGE % (90,120),
				# # "items" : [[0, 51501, 1], [0, 51501, 2], [1, 51501, 4], [1, 51501, 6], [2, 51501, 8], [2, 51501, 10], [2, 51501, 12], [2, 51501, 14]],
				# # "jackpot" : [3, 60701, 1],
			# # },
			# 0: {
				# "name": localeinfo.SPINWHEEL_LEVEL_RANGE % (1, 89),
				# "items": [
					# [0, 71151, 50], [0, 71151, 100], [0, 71151, 150], [0, 39028, 20], [0, 39028, 30],
					# [0, 39028, 50], [0, 70722, 20], [0, 38050, 20], [0, 27987, 5], [0, 25040, 10],
					# [1, 71151, 70], [1, 71151, 150], [1, 70705, 200], [1, 30169, 250], [1, 30170, 250],
					# [1, 30171, 250], [1, 70722, 40], [1, 38050, 40], [1, 27987, 10], [1, 25040, 5],
					# [2, 30182, 2], [2, 30182, 3], [2, 73704, 1]
				# ],
				# "jackpot": [3, 60700, 1],
			# },
			# 1: {
				# "name": localeinfo.SPINWHEEL_LEVEL_RANGE % (90, 120),
				# "items": [
					# [0, 51501, 10], [0, 51501, 20], [0, 51501, 30], [0, 39028, 100], [0, 39028, 110],
					# [0, 30181, 3], [0, 30181, 5], [0, 70706, 30], [0, 51001, 30], [0, 55028, 20],
					# [1, 51501, 60], [1, 51501, 80], [1, 39028, 200], [1, 39028, 220], [1, 70706, 60],
					# [1, 50701, 250], [1, 50705, 250], [1, 50708, 250], [1, 51001, 50], [1, 55031, 5],
					# [2, 30182, 5], [2, 30182, 6], [2, 73703, 1], [2, 73704, 1]
				# ],
				# "jackpot": [3, 60702, 1],
			# },
			# 2 : {
				# "name" : localeinfo.SPINWHEEL_LEVEL_CONQ_RANGE % (1,30),
				# "items": [
					# [0, 51505, 5],
					# [0, 51505, 10],
					# [0, 51505, 15],
					# [0, 10783, 100],
					# [0, 10783, 110],
					
					# [0, 30181, 3],
					# [0, 30181, 5],
					# [0, 70707, 30],
					# [1, 50733, 100],
					# [1, 50734, 100],
					
					# [1, 51505, 30],
					# [1, 51505, 40],
					# [1, 10783, 200],
					# [1, 10783, 220],
					# [1, 70707, 60],
					
					# [1, 50735, 100],
					# [1, 50736, 100],
					# [1, 50737, 100],
					# [1, 50738, 100],
					# [1, 55031, 5],
					
					# [2, 30182, 5],
					# [2, 30182, 6],
					# [2, 73703, 1],
					# [2, 73704, 1]
				# ],
				# "jackpot" : [3, 60703, 1],
			# },
			# # 3 : {
				# # "name" : localeinfo.SPINWHEEL_LEVEL_RANGE % (105,120),
				# # "items" : [[0, 51501, 1], [0, 51501, 2], [1, 51501, 4], [1, 51501, 6], [2, 51501, 8], [2, 51501, 10], [2, 51501, 12], [2, 51501, 14]],
				# # "jackpot" : [3, 71073, 1],
			# # },
		# }
		normal_data = {
			0: {
				"name": localeinfo.SPINWHEEL_LEVEL_RANGE % (30, 89),
				"items": [
					# easy appearance items
					[0, 71151, 50],
					[0, 70705, 20],
					[0, 70102, 15],
					[0, 39028, 20],
					[0, 39028, 30],
					[0, 39028, 50],
					[0, 70722, 10],
					[0, 38050, 10],
					[0, 27987, 5],
					[0, 25040, 5],

					# normal appearance items
					[1, 70102, 20],
					[1, 71151, 100],
					[1, 70705, 50],
					[1, 30169, 50],
					[1, 30170, 50],
					[1, 30171, 50],
					[1, 70722, 20],
					[1, 38050, 20],
					[1, 27987, 10],
					[1, 25040, 10],

					# hard appearance items
					[2, 70035, 1],
					[2, 50513, 1],
					[2, 30183, 2],
					[2, 30183, 3],
					[2, 73704, 1],
				],
				"jackpot": [3, 60700, 1],
			},

			1: {
				"name": localeinfo.SPINWHEEL_LEVEL_RANGE % (90, 105),
				"items": [
					# easy appearance items
					[0, 51501, 5],
					[0, 51501, 10],
					[0, 50513, 2],
					[0, 39028, 50],
					[0, 39028, 60],
					[0, 30184, 3],
					[0, 71026, 1],
					[0, 70706, 20],
					[0, 51001, 30],
					[0, 51001, 40],

					# normal appearance items
					[1, 51501, 20],
					[1, 51501, 25],
					[1, 39028, 80],
					[1, 39028, 100],
					[1, 70706, 40],
					[1, 30169, 100],
					[1, 30170, 100],
					[1, 30171, 100],
					[1, 51001, 50],
					[1, 71025, 1],

					# hard appearance items
					[2, 51001, 150],
					[2, 30182, 1],
					[2, 30182, 2],
					[2, 73703, 1],
					[2, 73704, 1],
				],
				"jackpot": [3, 60702, 1],
			},
		}



		dungeon_data = {
			0: {
				"name": localeinfo.SPINWHEEL_LEVEL_RANGE % (1, 69),
				"items": [
					# easy appearance items
					[0, 50288, 1],
					[0, 54701, 1],
					[0, 53586, 1],

					# normal appearance items
					[1, 33330, 1],
					[1, 33334, 1],
					[1, 33336, 1],

					# hard appearance items
					[2, 33331, 1],
					[2, 33335, 1],
					[2, 33337, 1],
				],
				"jackpot": [3, 83104, 1],
			},

			1: {
				"name": localeinfo.SPINWHEEL_LEVEL_RANGE % (70, 120),
				"items": [
					# easy appearance items
					[0, 50288, 1],
					[0, 53587, 1],
					[0, 54701, 1],
					[0, 53586, 1],
					[0, 54700, 1],
					[1, 33064, 1],
					[1, 54703, 1],
					[1, 54702, 1],
					[1, 54704, 1],
					[1, 50270, 1],

					# normal appearance items
					[1, 33330, 1],
					[1, 33332, 1],
					[1, 33334, 1],
					[1, 33336, 1],
					[1, 33338, 1],
					[1, 33064, 2],
					[1, 33344, 1],
					[1, 33342, 1],
					[1, 33348, 1],
					[1, 33352, 1],

					# hard appearance items
					[2, 33331, 1],
					[2, 33333, 1],
					[2, 33335, 1],
					[2, 33337, 1],
					[2, 33339, 1],
					[2, 33064, 3],
					[2, 33345, 1],
					[2, 33343, 1],
					[2, 33349, 1],
					[2, 33353, 1],
					[2, 71775, 1],
					[2, 71776, 1],
				],
				"jackpot": [3, 83105, 1],
			},
		}



		if app.__SPIN_WHEEL_DUNGEON__ and self.wheel_type == WHEEL_TYPE_DUNGEON:
			self.__children["data"] = dungeon_data
		elif app.ENABLE_DAILY_ALCHEMY_ORE and self.wheel_type == WHEEL_TYPE_NORMAL:
			# >>> DAILY_ALCHEMY_ORE: build pages from the accumulated server reward list.
			self.__children["data"] = self.__BuildAlchemyData()
			# <<< DAILY_ALCHEMY_ORE
		else:
			self.__children["data"] = normal_data
		# >>> DAILY_ALCHEMY_ORE: open on the player's current level bracket
		startPage = 0
		if app.ENABLE_DAILY_ALCHEMY_ORE and self.wheel_type == WHEEL_TYPE_NORMAL:
			startPage = self.__DefaultAlchemyPage()
		self.SetPage(startPage)
		# <<< DAILY_ALCHEMY_ORE

	def __BuildAlchemyData(self):
		# Turn the accumulated [rarity, vnum, count, weight] records into paginated
		# {pageIdx: {"name", "items":[[rarity,vnum,count],...], "jackpot":[...]}} data.
		# SetPage renders 25 item slots + 1 jackpot slot per page.
		recs = self.alchemyRewards
		data = {}
		if not recs:
			data[0] = {
				"name": localeinfo.SPINWHEEL_REWARD,
				"items": [],
				"jackpot": [0, -1, 0],
			}
			return data
		# group rewards into level brackets by their min_level (restores the old
		# per-level pages). Each distinct min_level = one bracket; label = "lv..next-1"
		# (last bracket ..120). A bracket with >25 rewards spills onto extra pages.
		levels = sorted(set([r[4] for r in recs]))
		PER_PAGE = 25
		page = 0
		for li in xrange(len(levels)):
			lv = levels[li]
			hi = (levels[li + 1] - 1) if (li + 1) < len(levels) else 120
			bracket = [r for r in recs if r[4] == lv]
			i = 0
			while i < len(bracket):
				chunk = bracket[i:i + PER_PAGE]
				items = [[r[0], r[1], r[2]] for r in chunk]
				# jackpot slot = highest-rarity record on this page (visual highlight only)
				best = chunk[0]
				for r in chunk:
					if r[0] > best[0]:
						best = r
				data[page] = {
					"name": localeinfo.SPINWHEEL_LEVEL_RANGE % (lv, hi),
					"items": items,
					"jackpot": [best[0], best[1], best[2]],
					"min_level": lv,
				}
				i += PER_PAGE
				page += 1
		return data

	def __DefaultAlchemyPage(self):
		# open on the bracket whose min_level is the highest the player qualifies for
		data = self.__children["data"]
		try:
			lv = player.GetStatus(player.LEVEL)
		except:
			lv = 1
		targetLv = None
		for pageIdx in data.keys():
			mlv = data[pageIdx].get("min_level", 0)
			if mlv <= lv and (targetLv is None or mlv > targetLv):
				targetLv = mlv
		if targetLv is None:
			return 0
		best = None
		for pageIdx in data.keys():
			if data[pageIdx].get("min_level", 0) == targetLv:
				if best is None or pageIdx < best:
					best = pageIdx
		return best if best is not None else 0

	def __ClickDirection(self, direction):
		pageIdx = self.__children["pageIdx"]
		if direction == "back":
			pageIdx -= 1
			if not self.__children["data"].has_key(pageIdx):
				return
			self.SetPage(pageIdx)
		else:
			pageIdx += 1
			if not self.__children["data"].has_key(pageIdx):
				return
			self.SetPage(pageIdx)

	def SetPage(self, pageIdx):
		self.__children["pageIdx"] = pageIdx
		pageData = self.__children["data"][pageIdx]
		self.__children["titleText"].SetText(pageData["name"])
		if pageIdx == 2:
			self.__children["titleText"].SetOutline()
			self.__children["titleText"].SetPackedFontColor(0xff7ed6df)
		else:
			self.__children["titleText"].SetOutline()
			self.__children["titleText"].SetPackedFontColor(0xff27ae60)
		xCount = 0
		_x = 3
		_y = 31
		bg = self.__children["bg"]
		itemList = []
		for j in xrange(25):
			try:
				itemList.append(CreateWindow(SpinItem(*pageData["items"][j]), bg, (_x, _y)))
			except:
				itemList.append(CreateWindow(SpinItem(0, -1, 0), bg, (_x, _y)))
			xCount+=1
			if xCount == 5:
				xCount = 0
				_x = 3
				_y += 44
			else:
				_x += 46
		itemList.append(CreateWindow(SpinItem(*pageData["jackpot"]), bg, (95, 272)))
		self.__children["itemList"] = itemList

	# >>> DAILY_ALCHEMY_ORE: open/close the ore-system help popup beside the reward window
	def __ClickHelp(self):
		if not self.helpWnd:
			import uialchemyorehelp
			self.helpWnd = uialchemyorehelp.AlchemyOreHelpWindow()
		if self.helpWnd.IsShow():
			self.helpWnd.Close()
		else:
			self.helpWnd.OpenAt(self)
	# <<< DAILY_ALCHEMY_ORE
	def Open(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.ApplySavedPosition(self, "SPINWHEEL_INFO")
		self.Show()
		self.SetTop()
	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.SaveOnClose(self, "SPINWHEEL_INFO")
		# >>> DAILY_ALCHEMY_ORE: hide the help popup alongside the reward window
		hw = getattr(self, "helpWnd", None)
		if hw:
			hw.Close()
		# <<< DAILY_ALCHEMY_ORE
		self.Hide()
	def OnMoveWindow(self, x, y):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.OnWindowMove("SPINWHEEL_INFO", x, y)
	def OnPressEscapeKey(self):
		self.Close()
		return True

class SpinItem(ui.ExpandedImageBox):
	def __init__(self, rarityType, itemIdx, itemCount):
		ui.ExpandedImageBox.__init__(self)
		self.__Load(rarityType, itemIdx, itemCount)
		if app.ENABLE_INGAME_WIKI:
			wndWiki = None
	def __Load(self, rarityType, itemIdx, itemCount):
		rarityImages = ["rarity_blue.png", "rarity_pink.png", "rarity_red.png", "jackpot_slot.png"]
		try:
			self.LoadImage(IMG_DIR + rarityImages[rarityType])
		except:
			self.LoadImage(IMG_DIR + rarityImages[0])

		if itemIdx < 0:
			return

		item.SelectItem(itemIdx)

		self.itemData = [itemIdx, itemCount]

		self.itemImg = CreateWindow(ui.ExpandedImageBox(), self, (6, 5), item.GetIconImageFileName())
		self.itemImg.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OverInItem, itemIdx)
		self.itemImg.SAFE_SetStringEvent("MOUSE_OVER_OUT",self.__OverOutItem)
		self.itemImg.SetStringEvent("MOUSE_RIGHT_DOWN", self._ItemShortcuts, itemIdx)

		self.itemCount = CreateWindow(ui.NumberLine(), self, (5+25, 5 + 20), str(itemCount))

	def SetAlpha(self, alpha):
		self.itemImg.SetAlpha(alpha)
		ui.ExpandedImageBox.SetAlpha(self, alpha)
	
	def __OverOutItem(self):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.HideToolTip()

	def __OverInItem(self, itemIdx):
		interfaceHandler = systemSetting.GetInterfaceHandler()
		if interfaceHandler and interfaceHandler.tooltipItem:
			interfaceHandler.tooltipItem.SetItemToolTip(itemIdx)
			interfaceHandler.tooltipItem.DeclareShortcut(("key_shift", "key_lclick"), localeinfo.TOOLTIP_WIKI_HOVER)
			interfaceHandler.tooltipItem.DeclareShortcut(("key_alt", "key_rclick"), localeinfo.TOOLTIP_QUICKSEARCH_OFFLINESHOP)

	def _ItemShortcuts(self, itemIdx):
		if app.USE_OFFLINESHOP and\
			not uiofflineshop_ae.IsBuildingShop() and\
			(app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT)):
			interfaceHandler = systemSetting.GetInterfaceHandler()
			if interfaceHandler:
				wndShopOffline = interfaceHandler.wndShopOffline
				if wndShopOffline:
					wndSearchShop = wndShopOffline.wndSearchShop
					if wndSearchShop:
						wndSearchShop.SearchByName(item.GetItemNameByVnum(itemIdx))
						return

		if app.IsPressed(app.DIK_LSHIFT): #wiki for chest open chest window else open normal page
			isBox = 1 if item.GetItemTypeByVnum(itemIdx) == item.ITEM_TYPE_GIFTBOX else 0
			if app.IsPressed(app.DIK_LSHIFT):
				import wiki
				wiki.GetBaseClass().OpenSpecialWikiPage(itemIdx,isBox)

class WheelWindow(ui.Board):
	def __init__(self, wheel_type):
		ui.Board.__init__(self)
		self.wheel_type = wheel_type
		self.__LoadWindow()

	def Destroy(self):
		self.__children = {}
	def __LoadWindow(self):
		self.Destroy()
		self.AddFlag("attach")
		#self.AddFlag("float")
		bg = CreateWindow(ui.ThinBoardCircle(), self, (8, 8), "", "", ((46 * 4) + 4, 42 + 4))
		self.__children["bg"] = bg

		self.SetSize(8 + bg.GetWidth() + 8, 8 + bg.GetHeight() + 8)
		self.SetCenterPosition()

		renderWnd = CreateWindow(ui.Window(), bg, (2, 2), "", "", ((46 * 4), 42))
		# renderWnd.SetInsideRender(True,True)
		self.__children["renderWnd"] = renderWnd

		if app.USE_CLIP_MASK:
			self.__children["containerWnd"] = CreateWindow(ui.Window(), bg, (2, 2), "", "", ((46 * 4), 42))
			self.__children["renderWnd"].SetClippingMaskWindow(self.__children["containerWnd"])

		self.__children["needleImg"] = CreateWindow(ui.ImageBox(), bg, (bg.GetWidth() / 2 - 6, -5), IMG_DIR + "needle.png")

	def SetSpin(self, selectedItemIdx, selectedItemCount, cmdData):
		spinItemList = []
		self.__children["selectedItemData"] = [selectedItemIdx, selectedItemCount]
		if cmdData != "-":
			cmdSplit = cmdData.split("?")
			xPos = 0
			renderWnd = self.__children["renderWnd"]
			for cmd in cmdSplit:
				itemList = cmd.split("|")
				if len(itemList) == 3:
					spinItemList.append(CreateWindow(SpinItem(int(itemList[0]), int(itemList[1]), int(itemList[2])), renderWnd, (xPos, 0)))
					xPos += 44
		self.__children["spinItemList"] = spinItemList
		self.__children["spinStatus"] = True
		self.__children["spinTime"] = app.GetTime() + float(app.GetRandom(3, 6))

	def OnUpdate(self):
		currentTime = app.GetTime()
		
		spinStatus = self.__children["spinStatus"] if self.__children.has_key("spinStatus") else False
		if not spinStatus:
			leftTimeForClose = self.__children["leftTimeForClose"] if self.__children.has_key("leftTimeForClose") else False
			if leftTimeForClose < currentTime:
				self.Hide()
			return
		spinLeftTime = self.__children["spinTime"] - currentTime
		spinCurrentX = (spinLeftTime*2) * 2 if spinLeftTime > 0 else 1
		spinItemList = self.__children["spinItemList"] if self.__children.has_key("spinItemList") else []
		
		for child in spinItemList:
			idx = spinItemList.index(child)
			xPos = child.GetLocalPosition()[0] - math.ceil(spinCurrentX)
			child.SetPosition(xPos, 0)
			if spinLeftTime < 0:
				selectedItemData = self.__children["selectedItemData"]
				if child.itemData == selectedItemData:
					if xPos >= 50 and xPos <= 75:
						self.__children["spinStatus"] = False
						self.__children["leftTimeForClose"] = currentTime + 2.0
						# Send appropriate ani_done command based on wheel type
						if self.wheel_type == WHEEL_TYPE_MISSION_QUEST:
							net.SendChatPacket("/q_mission_quest ani_done")
						elif app.__SPIN_WHEEL_DUNGEON__ and self.wheel_type == WHEEL_TYPE_DUNGEON:
							net.SendChatPacket("/dungeon_spin_wheel ani_done")
						elif app.ENABLE_DAILY_ALCHEMY_ORE and self.wheel_type == WHEEL_TYPE_NORMAL:
							# >>> DAILY_ALCHEMY_ORE: normal wheel is now the ore system
							net.SendChatPacket("/alchemy_ore ani_done")
							# <<< DAILY_ALCHEMY_ORE
						else:
							net.SendChatPacket("/spin_wheel ani_done")
						for childEx in spinItemList:
							if childEx != child:
								childEx.SetAlpha(0.6)
						return
		for child in spinItemList:
			if child.GetLocalPosition()[0] < -50:
				xPosHighest = 0
				for childEx in spinItemList:
					if xPosHighest < childEx.GetLocalPosition()[0] + 44:
						xPosHighest = childEx.GetLocalPosition()[0] + 44
				child.SetPosition(xPosHighest, 0)
	def Open(self):
		self.Show()
		self.SetTop()
	def Close(self):
		self.Hide()
	def OnPressEscapeKey(self):
		return True

class Window(ui.Window):
	__children = {}
	def __init__(self, wheel_type):
		ui.Window.__init__(self)

		self.wheel_type = wheel_type
		self.last_spin_time = 0
		self.requires_update = False

		# >>> DAILY_ALCHEMY_ORE: per-instance ore state (normal wheel only)
		self.alchemyOreCount = 0
		self.alchemyDailyCap = 0
		self.alchemySpun = 0
		self.alchemyEnabled = 1
		self.alchemyRewards = []   # accumulated [rarity, vnum, count, weight] records
		self.alchemyToggle = None  # enable/disable toggle button (replaces spinBtn while filling)
		# <<< DAILY_ALCHEMY_ORE

		self.__LoadWindow()
	
	def GetTotalNeedKillCount(self):
		if app.__SPIN_WHEEL_DUNGEON__ and self.wheel_type == WHEEL_TYPE_DUNGEON:
			return TOTAL_NEED_KILL_COUNT_DUNGEON
		return TOTAL_NEED_KILL_COUNT_NORMAL

	def Destroy(self):
		self.last_spin_time = 0
		self.requires_update = False

		# >>> DAILY_ALCHEMY_ORE: release the toggle-button ref held to keep it alive
		if hasattr(self, "alchemyToggle") and self.alchemyToggle:
			self.alchemyToggle = None
		# <<< DAILY_ALCHEMY_ORE

		wheelWindow = self.__children["wheelWindow"] if self.__children.has_key("wheelWindow") else None
		if wheelWindow:
			wheelWindow.Close()
			wheelWindow.Destroy()
			self.__children["wheelWindow"] = None
		infoWindow = self.__children["infoWindow"] if self.__children.has_key("infoWindow") else None
		if infoWindow:
			infoWindow.Close()
			infoWindow.Destroy()
			self.__children["infoWindow"] = None
		self.__children = {}

	def __LoadWindow(self):
		self.Destroy()
		self.AddFlag("attach")
		#self.AddFlag("float")

		bg = CreateWindow(ui.ExpandedImageBox(), self, (0, 0), IMG_DIR + "bg.png")
		self.__children["bg"] = bg
		self.SetSize(bg.GetWidth(), bg.GetHeight())
		self.SetCenterPosition()

		gaugeImg = CreateWindow(ui.ExpandedImageBox(), bg, (37, 14), IMG_DIR + "unavailable.png")
		gaugeImg.imageFolder = IMG_DIR + "unavailable.png"
		self.__children["gaugeImg"] = gaugeImg

		total_kill_count = self.GetTotalNeedKillCount()
		gaugeText = CreateWindow(ui.TextLine(), bg, (37 + (self.__children["gaugeImg"].GetWidth() / 2), 12), "0 / " + str(total_kill_count) , "horizontal:center")
		gaugeText.SetOutline()
		self.__children["gaugeText"] = gaugeText

		realSpinBtn = CreateWindow(ui.Button(), bg, (0, 5))
		realSpinBtn.SetUpVisual(IMG_DIR + ("spin_can_normal.png" if self.wheel_type == WHEEL_TYPE_NORMAL else "spin_d_1.png"))
		realSpinBtn.SetOverVisual(IMG_DIR + ("spin_can_over.png" if self.wheel_type == WHEEL_TYPE_NORMAL else "spin_d_2.png"))
		realSpinBtn.SetDownVisual(IMG_DIR + ("spin_can_down.png" if self.wheel_type == WHEEL_TYPE_NORMAL else "spin_d_3.png"))
		realSpinBtn.SetDisableVisual(IMG_DIR + "spin_0.png")
		realSpinBtn.SetToolTipText(localeinfo.SPINWHEEL_SPIN_NORMAL if self.wheel_type == WHEEL_TYPE_NORMAL else localeinfo.SPINWHEEL_SPIN_DUNGEON )
		realSpinBtn.SetEvent(ui.__mem_func__(self.__ClickSpin), "mouse_click")
		self.__children["realSpinBtn"] = realSpinBtn

		spinBtn = CreateWindow(ui.Button(), bg, (0, 5))
		spinBtn.SetUpVisual(IMG_DIR + ("spin_1.png" if self.wheel_type == WHEEL_TYPE_NORMAL else "spin_d_1.png"))
		spinBtn.SetOverVisual(IMG_DIR + ("spin_2.png" if self.wheel_type == WHEEL_TYPE_NORMAL else "spin_d_2.png"))
		spinBtn.SetDownVisual(IMG_DIR + ("spin_2.png" if self.wheel_type == WHEEL_TYPE_NORMAL else "spin_d_3.png"))
		spinBtn.SetDisableVisual(IMG_DIR + ("spin_0.png" if self.wheel_type == WHEEL_TYPE_NORMAL else "spin_d_0.png"))
		self.__children["spinBtn"] = spinBtn

		questionMark = CreateWindow(ui.Button(), bg, (144, 13))
		questionMark.SetUpVisual(IMG_DIR + "question_mark.png")
		questionMark.SetOverVisual(IMG_DIR + "question_mark_1.png")
		questionMark.SetDownVisual(IMG_DIR + "question_mark_2.png")
		questionMark.SetToolTipText(localeinfo.SPINWHEEL_REWARDS_INFO if self.wheel_type == WHEEL_TYPE_NORMAL else localeinfo.SPINWHEEL_REWARDS_D_INFO )
		questionMark.SAFE_SetEvent(self.__ClickMark, "mouse_click")
		#questionMark.SetEvent(ui.__mem_func__(self.__ClickMark), "mouse_click")
		self.__children["questionMark"] = questionMark

		# >>> DAILY_ALCHEMY_ORE: enable/disable TOGGLE button (normal wheel only) in the old
		# decorative spin-image slot; morphs to realSpinBtn at cap. Replaces the checkbox.
		if app.ENABLE_DAILY_ALCHEMY_ORE and self.wheel_type == WHEEL_TYPE_NORMAL:
			spinBtn.Hide()   # the toggle owns this slot for the ore wheel
			self.__children["realSpinBtn"].Hide()
			# hold a python ref (self.alchemyToggle): a SetParent child is NOT kept alive by the parent
			toggleBtn = CreateWindow(ui.Button(), bg, (0, 5))
			toggleBtn.SAFE_SetEvent(self.__ClickAlchemyToggle, "mouse_click")
			self.alchemyToggle = toggleBtn
			self.__children["alchemyToggle"] = toggleBtn
			self.__RefreshAlchemyToggle()
		# <<< DAILY_ALCHEMY_ORE

	def RefreshPosition(self):
		if self.wheel_type == WHEEL_TYPE_NORMAL:
			self.SetPosition(135, wndMgr.GetScreenHeight() - 100)
			if app.ENABLE_WINDOW_RESIZE:
				self.SetResizeDic({"position" : (135, Expr("SCREEN_HEIGHT") - 100)})
		elif app.__SPIN_WHEEL_DUNGEON__ and self.wheel_type == WHEEL_TYPE_DUNGEON:
			if app.ENABLE_DAILY_ALCHEMY_ORE:
				interfaceHandler = systemSetting.GetInterfaceHandler()
				if interfaceHandler and interfaceHandler.wndSpinWheel and interfaceHandler.wndSpinWheel.IsShow():
					self.SetPosition(135, wndMgr.GetScreenHeight() - 100 - 40 - 8)
					if app.ENABLE_WINDOW_RESIZE:
						self.SetResizeDic({"position" : (135, Expr("SCREEN_HEIGHT") - 100 - 40 - 8)})
					return

			self.SetPosition(135, wndMgr.GetScreenHeight() - 100)
			if app.ENABLE_WINDOW_RESIZE:
				self.SetResizeDic({"position" : (135, Expr("SCREEN_HEIGHT") - 100)})

	def __ClickMark(self):
		infoWindow = self.__children["infoWindow"] if self.__children.has_key("infoWindow") else None
		# >>> DAILY_ALCHEMY_ORE: for the normal wheel rebuild the info window each open so it
		# reflects the latest server-driven (accumulated) reward list.
		if app.ENABLE_DAILY_ALCHEMY_ORE and self.wheel_type == WHEEL_TYPE_NORMAL:
			if infoWindow and infoWindow.IsShow():
				infoWindow.Close()
				return
			if infoWindow:
				infoWindow.Close()
				infoWindow.Destroy()
			infoWindow = InfoWindow(self.wheel_type, self.alchemyRewards)
			self.__children["infoWindow"] = infoWindow
			infoWindow.Open()
			return
		# <<< DAILY_ALCHEMY_ORE
		if not infoWindow:
			infoWindow = InfoWindow(self.wheel_type)
			self.__children["infoWindow"] = infoWindow
		
		if infoWindow.IsShow():
			infoWindow.Close()
		else:
			infoWindow.Open()

	def IsSpinWindow(self):
		infoWindow = self.__children["infoWindow"] if self.__children.has_key("infoWindow") else None
		if not infoWindow:
			infoWindow = InfoWindow(self.wheel_type)
			self.__children["infoWindow"] = infoWindow
		
		if infoWindow.IsShow():
			return True
		else:
			return False


	def SetSpinReward(self, selectedItemIdx, selectedItemCount, cmdData):
		wheelWindow = WheelWindow(self.wheel_type)
		(x, y) = self.GetGlobalPosition()
		wheelWindow.SetPosition(x + 30, y - 60)
		wheelWindow.SetSpin(int(selectedItemIdx), int(selectedItemCount), cmdData)
		wheelWindow.Show()
		self.__children["wheelWindow"] = wheelWindow

	def SetDungeonSpinReward(self, selectedItemIdx, selectedItemCount, cmdData):
		wheelWindow = WheelWindow(self.wheel_type)
		(x, y) = self.GetGlobalPosition()
		wheelWindow.SetPosition(x + 30, y - 60)
		wheelWindow.SetSpin(int(selectedItemIdx), int(selectedItemCount), cmdData)
		wheelWindow.Show()
		self.__children["wheelWindow"] = wheelWindow

	# >>> DAILY_ALCHEMY_ORE: server-driven daily ore system (normal wheel only)
	def SetAlchemyOre(self, oreCount, dailyCap, spun, enabled, secsToMidnight):
		# store full UI state
		self.alchemyOreCount = int(oreCount)
		self.alchemyDailyCap = int(dailyCap)
		self.alchemySpun = int(spun)
		self.alchemyEnabled = int(enabled)
		self.alchemySecsToMidnight = int(secsToMidnight)

		# a fresh SetAlchemyOre (login / count change / reset) starts a new reward list;
		# following SetAlchemyRewards commands append to rebuild it cleanly.
		self.alchemyRewards = []

		# update the progress gauge (oreCount / dailyCap) and the "X / cap" label
		cap = self.alchemyDailyCap if self.alchemyDailyCap > 0 else 1
		count = self.alchemyOreCount
		if count < 0:
			count = 0
		if count > cap:
			count = cap

		gaugeImg = self.__children["gaugeImg"] if self.__children.has_key("gaugeImg") else None
		if gaugeImg:
			newImageFolder = IMG_DIR + "full.png" if count >= cap else IMG_DIR + "unavailable.png"
			if newImageFolder != gaugeImg.imageFolder:
				gaugeImg.LoadImage(newImageFolder)
				gaugeImg.imageFolder = newImageFolder
			gaugeImg.SetRenderingRect(0.0, 0.0, -1.0 + float(count) / float(cap), 0.0)

		gaugeText = self.__children["gaugeText"] if self.__children.has_key("gaugeText") else None
		if gaugeText:
			gaugeText.SetText(str(self.alchemyOreCount) + " / " + str(self.alchemyDailyCap))

		# refresh the enable/disable toggle button (art + tooltip) from server state
		self.__RefreshAlchemyToggle()

		# dim the gauge while ore drops are disabled so the off-state reads at a glance
		if gaugeImg:
			gaugeImg.SetAlpha(1.0 if self.alchemyEnabled else 0.5)

		# cap reached & not yet spun -> real SPIN button; otherwise the toggle stays
		self.requires_update = False
		canSpin = (self.alchemyOreCount >= self.alchemyDailyCap) and (self.alchemySpun == 0) and (self.alchemyDailyCap > 0)
		self.__children["spinBtn"].Hide()
		if canSpin:
			if self.alchemyToggle:
				self.alchemyToggle.Hide()
			self.__children["realSpinBtn"].Show()
		else:
			self.__children["realSpinBtn"].Hide()
			if self.alchemyToggle:
				self.alchemyToggle.Show()

		# if already spun today hide the whole window; otherwise show it
		if self.alchemySpun == 1:
			self.Hide()
		else:
			self.Show()

	def SetAlchemyRewards(self, cmdData):
		# APPEND-parse "rarity|vnum|count|weight#rarity|vnum|count|weight#..." records
		if not cmdData or cmdData == "-":
			return
		for rec in cmdData.split("#"):
			rec = rec.strip()
			if not rec:
				continue
			parts = rec.split("|")
			if len(parts) < 4:
				continue
			try:
				rarity = int(parts[0])
				vnum = int(parts[1])
				count = int(parts[2])
				weight = int(parts[3])
				min_level = int(parts[4]) if len(parts) >= 5 else 1
			except:
				continue
			self.alchemyRewards.append([rarity, vnum, count, weight, min_level])

	def SetAlchemyResult(self, vnum, count):
		# drive the reveal: build a scrolling strip from the accumulated reward list and
		# land on the won item, then WheelWindow.OnUpdate confirms via /alchemy_ore ani_done.
		vnum = int(vnum)
		count = int(count)

		# rarity of the winner (fallback rarity 0)
		winRarity = 0
		for rec in self.alchemyRewards:
			if rec[1] == vnum:
				winRarity = rec[0]
				break

		# build a strip of "rarity|vnum|count" slots. WheelWindow lands on the slot whose
		# itemData == [vnum, count], so the winner MUST appear with that exact count.
		slots = []
		for rec in self.alchemyRewards:
			slots.append("%d|%d|%d" % (rec[0], rec[1], rec[2]))
		# guarantee the exact winner slot (vnum + count) is present
		winnerSlot = "%d|%d|%d" % (winRarity, vnum, count)
		if winnerSlot not in slots:
			slots.append(winnerSlot)
		# ensure enough slots for the scroll to wrap and land cleanly
		if len(slots) < 6:
			base = list(slots)
			while len(slots) < 6 and base:
				slots.extend(base)
			slots = slots[:max(6, len(base))]

		cmdData = "?".join(slots)

		wheelWindow = WheelWindow(self.wheel_type)
		(x, y) = self.GetGlobalPosition()
		wheelWindow.SetPosition(x + 30, y - 60)
		wheelWindow.SetSpin(vnum, count, cmdData)
		wheelWindow.Show()
		self.__children["wheelWindow"] = wheelWindow

	def __RefreshAlchemyToggle(self):
		# skin the toggle button (enabled vs disabled art) + tooltip from current state
		if not self.alchemyToggle:
			return
		if self.alchemyEnabled:
			self.alchemyToggle.SetUpVisual(TOGGLE_IMG_DIR + "enabled_norm.png")
			self.alchemyToggle.SetOverVisual(TOGGLE_IMG_DIR + "enabled_hover.png")
			self.alchemyToggle.SetDownVisual(TOGGLE_IMG_DIR + "enabled_down.png")
			try:
				self.alchemyToggle.SetToolTipText(localeinfo.ALCHEMY_ORE_TOOLTIP_ON % (self.alchemyOreCount, self.alchemyDailyCap))
			except:
				pass
		else:
			self.alchemyToggle.SetUpVisual(TOGGLE_IMG_DIR + "enabled_disabled.png")
			self.alchemyToggle.SetOverVisual(TOGGLE_IMG_DIR + "disabled_hover.png")
			self.alchemyToggle.SetDownVisual(TOGGLE_IMG_DIR + "disabled_down.png")
			try:
				self.alchemyToggle.SetToolTipText(localeinfo.ALCHEMY_ORE_TOOLTIP_OFF)
			except:
				pass

	def __ClickAlchemyToggle(self):
		# optimistic flip for instant feedback; server echoes authoritative state via SetAlchemyOre
		self.alchemyEnabled = 0 if self.alchemyEnabled else 1
		self.__RefreshAlchemyToggle()
		gaugeImg = self.__children["gaugeImg"] if self.__children.has_key("gaugeImg") else None
		if gaugeImg:
			gaugeImg.SetAlpha(1.0 if self.alchemyEnabled else 0.5)
		net.SendChatPacket("/alchemy_ore toggle")
	# <<< DAILY_ALCHEMY_ORE

	def OnUpdate(self):
		total_kill_count = self.GetTotalNeedKillCount()
		if self.requires_update and self.__children["currentCount"] >= total_kill_count:
			if self.last_spin_time < app.GetGlobalTimeStamp():
				self.requires_update = False

				self.__children["spinBtn"].Hide()
				self.__children["realSpinBtn"].Show()

	def SetSpinData(self, count, last_spin_time):
		if count < 0:
			count = 0

		total_kill_count = self.GetTotalNeedKillCount()
		self.__children["currentCount"] = count
		newImageFolder = IMG_DIR + "unavailable.png" if count != total_kill_count else IMG_DIR + "full.png"
		gaugeImg = self.__children["gaugeImg"]
		if newImageFolder != gaugeImg.imageFolder:
			gaugeImg.LoadImage(newImageFolder)
			gaugeImg.imageFolder = newImageFolder
		gaugeImg.SetRenderingRect(0.0, 0.0, -1.0 + float(count) / float(total_kill_count), 0.0)
		self.__children["gaugeText"].SetText(str(count) + " / " + str(total_kill_count))

		self.last_spin_time = int(last_spin_time)
		self.requires_update = False

		self.__children["realSpinBtn"].Hide()
		self.__children["spinBtn"].Show()

		if count < total_kill_count:
			self.__children["spinBtn"].Disable()
		elif self.last_spin_time == 0:
			self.__children["spinBtn"].Hide()
			self.__children["realSpinBtn"].Show()
		elif last_spin_time > app.GetGlobalTimeStamp():
			self.requires_update = True
		else:
			self.__children["spinBtn"].Hide()
			self.__children["realSpinBtn"].Show()

	def __ClickSpin(self, emptyArg):
		# >>> DAILY_ALCHEMY_ORE: normal wheel is now the ore system (own gate + command)
		if app.ENABLE_DAILY_ALCHEMY_ORE and self.wheel_type == WHEEL_TYPE_NORMAL:
			# only valid when oreCount >= dailyCap and not spun yet today
			if self.alchemyDailyCap <= 0:
				return
			if self.alchemyOreCount < self.alchemyDailyCap:
				return
			if self.alchemySpun != 0:
				return
			net.SendChatPacket("/alchemy_ore spin")
			return
		# <<< DAILY_ALCHEMY_ORE
		total_kill_count = self.GetTotalNeedKillCount()
		if self.__children["currentCount"] != total_kill_count:
			return

		net.SendChatPacket("/{} spin".format("dungeon_spin_wheel" if (app.__SPIN_WHEEL_DUNGEON__ and self.wheel_type == WHEEL_TYPE_DUNGEON) else "spin_wheel"))

	def Open(self):
		self.Show()
		self.SetTop()
	def Close(self):
		self.Hide()

def CreateWindow(window, parent, windowPos, windowArgument = "", windowPositionRule = "", windowSize = (-1, -1), windowFontName = -1):
	window.SetParent(parent)
	if windowSize != (-1, -1):
		window.SetSize(*windowSize)
	if windowPositionRule:
		splitList = windowPositionRule.split(":")
		if len(splitList) == 2:
			(type, mode) = (splitList[0], splitList[1])
			if type == "horizontal":
				if isinstance(window, ui.TextLine):
					if mode == "center":
						window.SetHorizontalAlignCenter()
					elif mode == "right":
						window.SetHorizontalAlignRight()
					elif mode == "left":
						window.SetHorizontalAlignLeft()
				else:
					if mode == "center":
						window.SetWindowHorizontalAlignCenter()
					elif mode == "right":
						window.SetWindowHorizontalAlignRight()
					elif mode == "left":
						window.SetWindowHorizontalAlignLeft()
			elif type == "vertical":
				if isinstance(window, ui.TextLine):
					if mode == "center":
						window.SetVerticalAlignCenter()
					elif mode == "top":
						window.SetVerticalAlignTop()
					elif mode == "bottom":
						window.SetVerticalAlignBottom()
				else:
					if mode == "top":
						window.SetWindowVerticalAlignTop()
					elif mode == "center":
						window.SetWindowVerticalAlignCenter()
					elif mode == "bottom":
						window.SetWindowVerticalAlignBottom()
	if windowArgument:
		if isinstance(window, ui.TextLine):
			if windowFontName != -1:
				window.SetFontName(windowFontName)
			window.SetText(windowArgument)
		elif isinstance(window, ui.NumberLine):
			window.SetNumber(windowArgument)
		elif isinstance(window, ui.ExpandedImageBox) or isinstance(window, ui.ImageBox):
			window.LoadImage(windowArgument if windowArgument.find("gr2") == -1 else "icon/item/27995.tga")
	window.SetPosition(*windowPos)
	window.Show()
	return window
