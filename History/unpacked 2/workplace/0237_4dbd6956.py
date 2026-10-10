import app
import ui
import localeinfo
import wndMgr
import chat
import player
import item
import time
import uitooltip

class Window(ui.ThinBoard):

	NORMAL_COLOR = 0xFFC2C2C2
	YELLOW_COLOR = 0xFFFFC800
	OPEN_TIME = 15
	SLIDE_TIME = 4
	GAP = 12
	SLOT_PIXEL_HEIGHT = 32

	BOARD_SIZE = [205, 326]
	RECT_SIZE = [205, 300]

	"""
	You can use the following values to sort the items
		"gold"
		"count"
		"none"
	"""
	SORT_MODE = "gold"

	def __init__(self):
		ui.ThinBoard.__init__(self)
		self.SetSize(self.BOARD_SIZE[0], self.BOARD_SIZE[1])

		self.children = {}
		self.dropInformation = []
		self.cachedSorted = []
		self.sortDirty = True
		self.cachedTotalHeight = 0
		self.heightDirty = True
		self.scrollOffset = 0.0
		self.drop_slot_animating = False

		self.isActiveSlide = False
		self.isActiveSlideOut = False
		self.isActiveSlideOutEnded = True
		self.isVisible = False
		self.endTime = 0

		self.tooltipItem = uitooltip.ItemToolTip()
		self.tooltipItem.Hide()

		self.CreateWindow()

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def CreateWindow(self):
		self.AddFlag("movable")
		self.AddFlag("float")

		rectWindow = ui.Window()
		rectWindow.SetParent(self)
		rectWindow.SetSize(self.RECT_SIZE[0], self.RECT_SIZE[1])
		rectWindow.SetPosition(0, 15)
		rectWindow.Show()
		self.rectWindow = rectWindow

		scrollbarWindow = ui.Window()
		scrollbarWindow.SetParent(self)
		scrollbarWindow.SetPosition(190, 5)
		scrollbarWindow.SetSize(7, 360)
		scrollbarWindow.Show()
		self.scrollbarWindow = scrollbarWindow

		scrollBar = ui.ScrollbarDyn()
		scrollBar.SetParent(self.scrollbarWindow)
		scrollBar.SetPosition(0, 8)
		scrollBar.SetSize(5, self.GetHeight() - 25)
		scrollBar.SetScrollEvent(self.OnScrollBar)
		scrollBar.SetScrollSpeed(25)
		scrollBar.Hide()
		self.scrollBar = scrollBar

	def _InvalidateCache(self):
		self.sortDirty = True
		self.heightDirty = True

	def GetSortedDropInformation(self):
		if not self.sortDirty:
			return self.cachedSorted

		if self.SORT_MODE == "gold":
			gold = [info for info in self.dropInformation if info["vnum"] == 1]
			others = [info for info in self.dropInformation if info["vnum"] != 1]
			self.cachedSorted = gold + others
		elif self.SORT_MODE == "count":
			self.cachedSorted = sorted(self.dropInformation, key=lambda x: x["count"], reverse=True)
		else:
			self.cachedSorted = self.dropInformation[:]

		self.sortDirty = False
		return self.cachedSorted

	def GetTotalHeight(self):
		if not self.heightDirty:
			return self.cachedTotalHeight

		total = 0
		for data in self.dropInformation:
			total += data["slotHeight"] + self.GAP
		self.cachedTotalHeight = total
		self.heightDirty = False
		return total

	def SlideIn(self):
		if self.isActiveSlide or self.isActiveSlideOut:
			return

		self.SetTop()
		self.Show()

		self.wndWidth = self.GetWidth()
		self.wndHeight = self.GetHeight()

		screen_w = wndMgr.GetScreenWidth()
		screen_h = wndMgr.GetScreenHeight()

		start_x = -self.wndWidth

		center_y = (screen_h - self.wndHeight) // 2
		offset = int(screen_h * 0.05)
		target_y = center_y + offset
		target_y = max(10, min(target_y, screen_h - self.wndHeight - 10))

		self.SetPosition(start_x, target_y)

		self.isActiveSlide = True
		self.isActiveSlideOut = False
		self.isActiveSlideOutEnded = False
		self.endTime = app.GetGlobalTimeStamp() + self.OPEN_TIME

	def Open(self):

		if not self.isVisible and not self.isActiveSlide and not self.isActiveSlideOut:
			self.SlideIn()

	def _DestroyAllSlots(self):
		for widget in self.children.itervalues():
			widget.Hide()
		self.children = {}

	def Close(self):
		if self.isActiveSlide or self.isActiveSlideOut or not self.isVisible:
			return

		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

		self._DestroyAllSlots()
		self.dropInformation = []
		self._InvalidateCache()
		self.scrollOffset = 0.0
		self.isActiveSlideOut = True

	def Destroy(self):
		self._DestroyAllSlots()
		self.dropInformation = []
		self._InvalidateCache()
		self.scrollOffset = 0.0
		self.isActiveSlide = False
		self.isActiveSlideOut = False
		self.isActiveSlideOutEnded = True
		self.isVisible = False
		self.endTime = 0

	def _ResizeBoard(self):
		totalHeight = self.GetTotalHeight()
		maxHeight = self.BOARD_SIZE[1]
		baseHeight = 26

		if totalHeight + baseHeight <= maxHeight:
			self.SetSize(self.GetWidth(), totalHeight + baseHeight)
			self.rectWindow.SetSize(205, totalHeight)
			self.scrollbarWindow.SetSize(7, totalHeight + 5)
			self.scrollBar.SetSize(5, totalHeight - 25)
		else:
			self.SetSize(self.GetWidth(), maxHeight)
			self.rectWindow.SetSize(205, maxHeight - baseHeight)
			self.scrollbarWindow.SetSize(7, maxHeight)
			self.scrollBar.SetSize(5, maxHeight - 25)

	def AppendDropInfo(self, vnum, count):
		for entry in self.dropInformation:
			if entry["vnum"] == vnum:
				entry["count"] += count
				self.UpdateSlotText(vnum, entry["count"])
				if self.SORT_MODE == "count":
					self._InvalidateCache()
				break
		else:
			item.SelectItem(vnum)
			size = item.GetItemSize()[1]
			slotHeight = size * self.SLOT_PIXEL_HEIGHT

			self.dropInformation.insert(0, {"vnum": vnum, "count": count, "size": size, "slotHeight": slotHeight})
			self._InvalidateCache()

			self._DestroyAllSlots()
			for index, info in enumerate(self.GetSortedDropInformation()):
				self.CreateDropSlot(info, index)

			self._ResizeBoard()
			self.UpdateSlotPositions()
			self.ChangeScrollbar()

			self.drop_slot_anim_start_time = time.clock()
			self.drop_slot_animating = True

		self.endTime = app.GetGlobalTimeStamp() + self.OPEN_TIME

		if not self.isVisible and not self.isActiveSlide and not self.isActiveSlideOut:
			self.SlideIn()

	def AppendChatInfo(self, vnum, count):
		item.SelectItem(vnum)
		name = item.GetItemName()

		if vnum == 1:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GAME_PICK_MONEY % localeinfo.MoneyFormat(count))
		elif count > 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DROP_INFO_TEXT_1 % (name, count))
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.DROP_INFO_TEXT_2 % name)


	def CreateDropSlot(self, data, index):
		if data["vnum"] == 0:
			return

		vnum = data["vnum"]
		item.SelectItem(vnum)
		name = item.GetItemName()
		size = data["size"]
		itemIcon = item.GetIconImageFileName()

		slotImage = ui.MakeImageBox(self, "d:/ymir work/ui/dropinfo/slot_{}.tga".format(size), 150, 0)

		itemFlare = ui.MakeImageBox(slotImage, "d:/ymir work/ui/dropinfo/name.tga", -120, -13)
		itemName = ui.MakeTextLineColor(itemFlare, 105, 20, name, self.NORMAL_COLOR)
		itemName.SetHorizontalAlignLeft()
		iconImage = ui.MakeImageBox(slotImage, itemIcon, 0, 0)

		itemCountBG = ui.MakeImageBox(slotImage, "d:/ymir work/ui/dropinfo/line.tga", -120, 13)
		if vnum == 1:
			itemCountText = ui.MakeTextLineColor(itemCountBG, 10, 0, localeinfo.GAME_PICK_MONEY % localeinfo.MoneyFormat(data["count"]), self.YELLOW_COLOR)
		else:
			itemCountText = ui.MakeTextLineColor(itemCountBG, 25, 10, localeinfo.DROP_INFO_COUNT % data["count"], self.YELLOW_COLOR)
		itemCountText.SetOutline()
		for widget in [slotImage, iconImage, itemFlare, itemName, itemCountBG, itemCountText]:
			widget.SetClippingMaskWindow(self.rectWindow)


		metinSlot = [0] * player.METIN_SOCKET_MAX_NUM
		attrSlot = [ (0, 0) ] * player.ATTRIBUTE_SLOT_MAX_NUM

		iconImage.OnMouseOverIn = lambda arg=self, vnum=vnum: arg.OverInItem(vnum, metinSlot, attrSlot)
		iconImage.OnMouseOverOut = ui.__mem_func__(self.OverOutItem)

		self.children["slotImage_%d" % index] = slotImage
		self.children["iconImage_%d" % index] = iconImage
		self.children["ItemFlare_%d" % index] = itemFlare
		self.children["ItemName_%d" % index] = itemName
		self.children["ItemCountBG_%d" % index] = itemCountBG
		self.children["ItemCountText_%d" % index] = itemCountText

	def UpdateSlotText(self, vnum, new_count):
		for i, data in enumerate(self.GetSortedDropInformation()):
			if data["vnum"] == vnum:
				countText = self.children.get("ItemCountText_%d" % i)
				if countText:
					if vnum == 1:
						countText.SetText(localeinfo.GAME_PICK_MONEY % localeinfo.MoneyFormat(new_count))
					else:
						countText.SetText(localeinfo.DROP_INFO_COUNT % new_count)
				break

	def UpdateSlotPositions(self):
		current_y = 15 + self.scrollOffset
		for i, data in enumerate(self.GetSortedDropInformation()):
			slot = self.children.get("slotImage_%d" % i)
			if slot:
				slot.SetPosition(150, current_y)
				current_y += data["slotHeight"] + self.GAP

	def UpdateDropSlotAnimation(self):
		if not self.drop_slot_animating:
			return

		elapsed = time.clock() - self.drop_slot_anim_start_time
		duration = 0.3
		t = min(1.0, elapsed / duration)
		eased_t = 1 - (1 - t) ** 2

		start_y_offset = -50
		current_y = 15 + self.scrollOffset

		for i, data in enumerate(self.GetSortedDropInformation()):
			target_y = current_y
			animated_y = target_y + start_y_offset * (1 - eased_t)

			slot = self.children.get("slotImage_%d" % i)
			if slot:
				slot.SetPosition(150, animated_y)
			current_y += data["slotHeight"] + self.GAP

		if t >= 1.0:
			self.drop_slot_animating = False

	def OnUpdate(self):
		self.UpdateDropSlotAnimation()

		current_time = app.GetGlobalTimeStamp()

		if self.isActiveSlide:
			x, y = self.GetLocalPosition()
			target_x = 10

			delta_x = min(self.SLIDE_TIME, target_x - x)
			self.SetPosition(x + delta_x, y)

			if x >= target_x:
				self.isActiveSlide = False
				self.isVisible = True
				self.endTime = current_time + self.OPEN_TIME

		elif self.isActiveSlideOut:
			x, y = self.GetLocalPosition()
			target_x = -self.wndWidth - 10
			delta_x = max(-self.SLIDE_TIME, target_x - x)
			self.SetPosition(x + delta_x, y)

			if x <= target_x:
				self.Hide()
				self.isActiveSlideOut = False
				self.isActiveSlideOutEnded = True
				self.isVisible = False

		if not self.isActiveSlide and not self.isActiveSlideOut and current_time >= self.endTime:
			self.Close()

	def OverInItem(self, itemVnum, metinSlot, attrSlot):
		if not self.tooltipItem:
			return
		self.tooltipItem.ClearToolTip()
		self.tooltipItem.AddItemData(itemVnum, metinSlot, attrSlot)
		self.tooltipItem.ShowToolTip()

	def OverOutItem(self):
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

	# --- Scrollbar ---
	def ScrollContent(self, offset):
		self.scrollOffset = offset
		self.UpdateSlotPositions()

	def OnRunMouseWheel(self, length):
		if self.IsInPosition():
			self.UpdateScrollbar(length * 0.28)
			return True
		return False

	def OnScrollBar(self, scale):
		totalHeight = self.GetTotalHeight()
		visibleHeight = self.rectWindow.GetHeight()

		if totalHeight <= visibleHeight:
			return

		offset = min(0, max(int((totalHeight - visibleHeight) * scale * -1.0), visibleHeight - totalHeight))
		self.ScrollContent(offset)

	def UpdateScrollbar(self, val=0):
		totalHeight = self.GetTotalHeight()
		visibleHeight = self.rectWindow.GetHeight()
		newOffset = min(0, max(self.scrollOffset + val, visibleHeight - totalHeight))
		self.ScrollContent(newOffset)
		self.ChangeScrollbar()

	def ChangeScrollbar(self):
		if not self.scrollBar:
			return

		totalHeight = self.GetTotalHeight()
		visibleHeight = self.rectWindow.GetHeight()

		if totalHeight <= visibleHeight:
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(visibleHeight, totalHeight)
			progress = abs(self.scrollOffset) / float(totalHeight - visibleHeight)
			self.scrollBar.SetPosScale(progress)
			self.scrollBar.Show()
