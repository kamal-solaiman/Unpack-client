# coding: latin_1
# uishopsearch_new.py -- redesigned offlineshop search window.
# Parallel replacement for uishopsearch.py (which stays frozen as the revert path).
# Switched on via `import uishopsearch_new as uishopsearch` in uiofflineshop_ae.py.

import app
import ui
import net
import wndMgr
import item
import player
import chat
import grp
import math
import uicommon
import uitooltip
import localeinfo
import constinfo
import offlineshop
import uiswitchbot
import systemSetting
import shop_deal_rating
if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget

PATH_ROOT = "shop_search/"
PATH_CAT  = "shop_search/categories/"
PATH_OLD  = "cream/searchshop/"		# gap assets reused: yang.png, box_checked/box_uncheck

IS_AR = localeinfo.IsARABIC()

# row-local X anchors (LTR / mirrored AR)
if localeinfo.IsARABIC():
	COL = {"icon": 491, "qty": 475, "name": 420, "coin": 250, "price": 245, "seller": 130, "btnoff1": 22, "btnoff2": 44}
else:
	COL = {"icon": 10, "qty": 62, "name": 125, "coin": 262, "price": 283, "seller": 415, "btnoff1": 22, "btnoff2": 44}
HDR = {"qty": 62, "name": 155, "price": 300, "seller": 440}		# header label centers (mirror: ROW_W - x)

WND_W, WND_H   = 770, 470
TOP_Y          = 35
LEFT_X, LEFT_W = 15, 194
INPUT_H        = 49
CAT_Y, CAT_H   = 90, 345
RIGHT_X        = 216
HEADER_H       = 20
LIST_Y         = 57
LIST_W, LIST_H = 540, 361
FOOTER_Y       = 420
FOOTER_H       = 33
ROW_W          = 533
ROW_HEIGHTS    = {1: 51, 2: 85, 3: 116}
MAX_ITEMS_APPEND = 25

def GetTime():
	return app.GetTime()

# ---- saved search-filter presets (client-local, no server involvement) ----
try:
	import ast as _ast
except Exception:
	_ast = None

SAVED_FILTERS_FILE = "shop_search_filters.cfg"
MAX_SAVED_FILTERS = 10

def _LoadSavedFilters():
	out = []		# list of (name, tuple17)
	try:
		f = open(SAVED_FILTERS_FILE, "rb")
		# Keep the raw bytes: preset names are client-codepage byte strings (Arabic =
		# CP1256). Decoding to unicode here made SetText() fail to render the name
		# (row showed blank) and would mojibake Arabic -- so we split on raw bytes.
		lines = f.read().split("\n")
		f.close()
	except Exception:
		return out
	for line in lines:
		line = line.rstrip("\r")
		if "\t" not in line:
			continue
		name, raw = line.split("\t", 1)
		try:
			if _ast is not None:
				t = _ast.literal_eval(raw)
			else:
				t = eval(raw, {"__builtins__": None, "True": True, "False": False}, {})
			if isinstance(t, tuple) and len(t) == 17:
				out.append((name, t))
		except Exception:
			continue
	return out

def _SaveSavedFilters(entries):
	# Names are already client-codepage byte strings; calling .encode() on them
	# triggers an implicit ASCII *decode* under Py2 that throws on Arabic, aborting
	# the write AFTER "wb" already truncated the file (wiping every preset). Build the
	# whole payload first, then write raw bytes in one shot. repr(tuple) is ASCII-safe.
	try:
		payload = "".join("%s\t%s\n" % (name, repr(t)) for (name, t) in entries)
	except Exception:
		return
	try:
		f = open(SAVED_FILTERS_FILE, "wb")
		try:
			f.write(payload)
		finally:
			f.close()
	except Exception:
		pass

def _MakeThinScrollBar():
	# User-requested: the exact thin scrollbar model from the new wiki page
	# (AdvScrollBar, 7px tga-skinned drag bar). API-compatible with the stock
	# bar for everything this window uses (SetScrollBarSize/SetScrollEvent/
	# SetScrollStep/GetPos/SetPos/SetMiddleBarSize/OnUp/OnDown/IsInPosition).
	# Falls back to ui.ScrollBarNew if the wiki module is unavailable so the
	# window can always open.
	try:
		import ingamewikiui_new
		return ingamewikiui_new.AdvScrollBar()
	except Exception:
		return ui.ScrollBarNew()

def _IsSearchPremium():
	# Premium gates ONLY: sort modes + price-range filter. Same rule as the old window.
	if not app.USE_PREMIUM_FEATURES:
		return True
	return constinfo.player_premium_type != player.PREMIUM_TYPE_NONE

def _BuildCategoryTree():
	# (label, iconFile or None, fire(type,subtype) or None, subs list or None)
	# fire None => row only expands. subs: (label, (type, subtype)).
	L, I = localeinfo, item
	return [
		(L.OFFLINESHOP_SEARCH_ALL, "all items.png", (-1, -1), None),
		(L.OFFLINESHOP_SEARCH_C1_1, "weapons.png", (I.ITEM_TYPE_WEAPON, 255), [
			(L.OFFLINESHOP_SEARCH_SUB_SWORD,   (I.ITEM_TYPE_WEAPON, I.WEAPON_SWORD)),
			(L.OFFLINESHOP_SEARCH_SUB_DAGGER,  (I.ITEM_TYPE_WEAPON, I.WEAPON_DAGGER)),
			(L.OFFLINESHOP_SEARCH_SUB_BOW,     (I.ITEM_TYPE_WEAPON, I.WEAPON_BOW)),
			(L.OFFLINESHOP_SEARCH_SUB_TWOHAND, (I.ITEM_TYPE_WEAPON, I.WEAPON_TWO_HANDED)),
			(L.OFFLINESHOP_SEARCH_SUB_BELL,    (I.ITEM_TYPE_WEAPON, I.WEAPON_BELL)),
			(L.OFFLINESHOP_SEARCH_SUB_FAN,     (I.ITEM_TYPE_WEAPON, I.WEAPON_FAN)),
			(L.OFFLINESHOP_SEARCH_SUB_CLAW,    (I.ITEM_TYPE_WEAPON, I.WEAPON_CLAW)),
		]),
		(L.OFFLINESHOP_SEARCH_C1, "equipment.png", (I.ITEM_TYPE_ARMOR, 255), [
			(L.OFFLINESHOP_SEARCH_C1_2, (I.ITEM_TYPE_ARMOR, I.ARMOR_BODY)),
			(L.OFFLINESHOP_SEARCH_C1_3, (I.ITEM_TYPE_ARMOR, I.ARMOR_HEAD)),
			(L.OFFLINESHOP_SEARCH_C1_4, (I.ITEM_TYPE_ARMOR, I.ARMOR_SHIELD)),
			(L.OFFLINESHOP_SEARCH_C1_5, (I.ITEM_TYPE_ARMOR, I.ARMOR_EAR)),
			(L.OFFLINESHOP_SEARCH_C1_6, (I.ITEM_TYPE_ARMOR, I.ARMOR_NECK)),
			(L.OFFLINESHOP_SEARCH_C1_7, (I.ITEM_TYPE_ARMOR, I.ARMOR_WRIST)),
			(L.OFFLINESHOP_COMBOBOX_ARMOR_FOOTS, (I.ITEM_TYPE_ARMOR, I.ARMOR_FOOTS)),
			(L.OFFLINESHOP_SEARCH_C1_8, (I.ITEM_TYPE_ARMOR, I.ARMOR_PENDANT_FIRE)),
			(L.OFFLINESHOP_SEARCH_C1_9, (I.ITEM_TYPE_BELT, 255)),
		]),
		(L.OFFLINESHOP_SEARCH_C2, "costumes.png", (I.ITEM_TYPE_COSTUME, 255), [
			(L.OFFLINESHOP_SEARCH_C2_1, (I.ITEM_TYPE_COSTUME, I.COSTUME_TYPE_HAIR)),
			(L.OFFLINESHOP_SEARCH_C2_2, (I.ITEM_TYPE_COSTUME, I.COSTUME_TYPE_BODY)),
			(L.OFFLINESHOP_SEARCH_C2_3, (I.ITEM_TYPE_COSTUME, I.COSTUME_TYPE_ACCE)),
			(L.OFFLINESHOP_SEARCH_C2_4, (I.ITEM_TYPE_COSTUME, I.COSTUME_TYPE_WEAPON)),
			(L.OFFLINESHOP_SEARCH_C2_5, (I.ITEM_TYPE_COSTUME, I.COSTUME_TYPE_MOUNT)),
			(L.OFFLINESHOP_SEARCH_C2_22, (I.ITEM_TYPE_COSTUME, I.COSTUME_MOUNT_SKIN)),
			(L.OFFLINESHOP_SEARCH_C2_23, (I.ITEM_TYPE_COSTUME, I.COSTUME_PET_SKIN)),
			(L.OFFLINESHOP_SEARCH_C2_6, (I.ITEM_TYPE_SHINING, I.SHINING_WEAPON)),
			(L.OFFLINESHOP_SEARCH_C2_7, (I.ITEM_TYPE_SHINING, I.SHINING_ARMOR)),
			(L.OFFLINESHOP_SEARCH_C8,  (I.ITEM_TYPE_QUEST, I.QUEST_PET)),
		]),
		(L.OFFLINESHOP_SEARCH_CAT_ALCHEMY, "alchemy.png", (I.ITEM_TYPE_DS, 255), None),
		(L.OFFLINESHOP_SEARCH_CAT_BOOKS, "books.png", (I.ITEM_TYPE_SKILLBOOK, 255), None),
		(L.OFFLINESHOP_SEARCH_CAT_CONSUMABLES, "consumables.png", (I.ITEM_TYPE_USE, 255), None),
		(L.OFFLINESHOP_SEARCH_C4, "enchant.png", None, [
			(L.OFFLINESHOP_SEARCH_C4_1, (I.ITEM_TYPE_USE, I.ITEM_ENCHANT)),
			(L.OFFLINESHOP_SEARCH_C4_2, (I.ITEM_TYPE_USE, I.USE_ENCHANT_BODY_COSTUME)),
			(L.OFFLINESHOP_SEARCH_C4_3, (I.ITEM_TYPE_USE, I.USE_ENCHANT_HAIR_COSTUME)),
			(L.OFFLINESHOP_SEARCH_C4_4, (I.ITEM_TYPE_USE, I.USE_ENCHANT_WEAPON_COSTUME)),
		]),
		(L.OFFLINESHOP_SEARCH_CATEGORY_OTHERS, "items.png", None, [
			(L.OFFLINESHOP_SEARCH_C3,  (I.ITEM_TYPE_GIFTBOX, 255)),
			(L.OFFLINESHOP_SEARCH_C11, (I.ITEM_TYPE_EX_SLOT, 255)),
			(L.OFFLINESHOP_SEARCH_C5,  (I.ITEM_TYPE_METIN, 255)),
			(L.OFFLINESHOP_SEARCH_C6,  (I.ITEM_TYPE_MATERIAL, 255)),
			(L.OFFLINESHOP_SEARCH_C10, (I.ITEM_TYPE_QUEST, 0)),
		]),
	]


class CategoryList(ui.Window):
	"""Expandable category tree drawn from _BuildCategoryTree(). One flat list of
	row-windows; sub-rows carry a hide flag toggled by their parent row."""

	MAIN_H, SUB_H, GAP = 35, 20, 2

	class Row(ui.Window):
		def __init__(self, owner, label, icon, fire, isSub, hasSubs):
			ui.Window.__init__(self)
			self.owner = owner			# CategoryList (plain ref; owner outlives rows)
			self.fire = fire			# (type, subtype) or None
			self.isSub = isSub
			self.hasSubs = hasSubs
			self.expanded = False
			self.hiddenBySection = isSub	# subs start collapsed
			self.selected = False
			base = "subcategory_" if isSub else "btn_categ_"
			self.imgNorm, self.imgHover, self.imgDown = base + "normal.png", base + "hover.png", base + "down.png"
			# old pack naming: main rows use _norm not _normal
			if not isSub:
				self.imgNorm = base + "norm.png"

			self.bg = ui.ExpandedImageBox()
			self.bg.SetParent(self)
			self.bg.LoadImage(PATH_ROOT + self.imgNorm)
			self.bg.OnMouseOverIn = ui.__mem_func__(self.__OnOverIn)
			self.bg.OnMouseOverOut = ui.__mem_func__(self.__OnOverOut)
			self.bg.OnMouseLeftButtonDown = ui.__mem_func__(self.__OnClick)
			self.bg.Show()
			self.SetSize(self.bg.GetWidth(), self.bg.GetHeight())

			self.icon = None
			if icon:
				self.icon = ui.ExpandedImageBox()
				self.icon.SetParent(self.bg)
				self.icon.LoadImage(PATH_CAT + icon)
				self.icon.AddFlag("not_pick")
				self.icon.SetPosition(146 if IS_AR else 4, 2)
				self.icon.Show()

			self.arrow = None
			if hasSubs:
				self.arrow = ui.ExpandedImageBox()
				self.arrow.SetParent(self.bg)
				self.arrow.LoadImage(PATH_ROOT + "arrow_down.png")
				self.arrow.AddFlag("not_pick")
				self.arrow.SetPosition(8 if IS_AR else 164, 15)
				self.arrow.Show()

			self.text = ui.TextLine()
			self.text.SetParent(self.bg)
			self.text.AddFlag("not_pick")
			self.text.SetText(label)
			self.text.SetVerticalAlignCenter()
			self.text.SetWindowVerticalAlignCenter()
			if IS_AR:
				self.text.SetPosition(140 if not isSub else 170, 0)
				self.text.SetHorizontalAlignLeft()
			else:
				self.text.SetPosition(40 if not isSub else 12, 0)
			self.text.Show()

		def __OnOverIn(self):
			if not self.selected:
				self.bg.LoadImage(PATH_ROOT + self.imgHover)

		def __OnOverOut(self):
			self.bg.LoadImage(PATH_ROOT + (self.imgDown if self.selected else self.imgNorm))

		def __OnClick(self):
			self.owner.OnRowClicked(self)

		def SetSelected(self, flag):
			self.selected = flag
			self.bg.LoadImage(PATH_ROOT + (self.imgDown if flag else self.imgNorm))

		def SetExpanded(self, flag):
			self.expanded = flag
			if self.arrow:
				self.arrow.LoadImage(PATH_ROOT + ("arrow_up.png" if flag else "arrow_down.png"))

		def OnRender(self):
			# clip against the CategoryList viewport (framework has no scissor for these)
			px, py = self.owner.GetGlobalPosition()
			ph = self.owner.GetHeight()
			for img in (self.bg, self.icon, self.arrow):
				if img:
					img.SetClipRect(px, py, px + self.owner.GetWidth(), py + ph)
			tx, ty = self.text.GetGlobalPosition()
			if ty < py or ty + self.text.GetTextSize()[1] > py + ph:
				self.text.Hide()
			else:
				self.text.Show()

	def __init__(self):
		ui.Window.__init__(self)
		self.rows = []			# flat list; each row knows its section
		self.sections = []		# (mainRow, [subRows])
		self.selectEvent = None
		self.scrollBar = None

	def Destroy(self):
		self.selectEvent = None
		self.scrollBar = None
		self.rows = []
		self.sections = []

	def SetSelectEvent(self, fn):
		self.selectEvent = fn

	def SetScrollBar(self, bar):
		bar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		bar.SetScrollStep(0.2)
		self.scrollBar = bar

	def Build(self):
		for (label, icon, fire, subs) in _BuildCategoryTree():
			main = self.Row(self, label, icon, fire, False, bool(subs))
			main.SetParent(self)
			main.Show()
			self.rows.append(main)
			subRows = []
			for (subLabel, subFire) in (subs or []):
				sub = self.Row(self, subLabel, None, subFire, True, False)
				sub.SetParent(self)
				sub.Hide()
				self.rows.append(sub)
				subRows.append(sub)
			main.subRows = subRows		# toggled directly by __ToggleSection (identity lookup is proxy-unsafe)
			self.sections.append((main, subRows))
		self.__Layout()

	def OnRowClicked(self, row):
		if row.hasSubs and row.fire is None:
			# pure expander (Enchants / Other)
			self.__ToggleSection(row)
			return
		if row.hasSubs and not row.isSub:
			# main with a fire target: first click expands, the fire happens too
			self.__ToggleSection(row)
		if row.fire is None:
			return
		if self.selectEvent:
			ok = self.selectEvent(row.fire[0], row.fire[1])
			if ok:
				for r in self.rows:
					r.SetSelected(False)
				row.SetSelected(True)

	def __ToggleSection(self, mainRow):
		# mainRow is a weakref proxy (ui.__mem_func__ passes proxy(self) to the click
		# handler), so `mainRow is <real row in self.sections>` is ALWAYS False. Toggle
		# the clicked row directly instead -- the proxy forwards attr reads + method
		# calls to the real row, and its subRows are real objects we can mutate.
		newExpanded = not mainRow.expanded
		mainRow.SetExpanded(newExpanded)
		for s in getattr(mainRow, "subRows", []):
			s.hiddenBySection = not newExpanded
		self.__Layout()

	def ResetSelection(self):
		for r in self.rows:
			r.SetSelected(False)

	def __TotalHeight(self):
		h = 2
		for r in self.rows:
			if r.hiddenBySection:
				continue
			h += (self.SUB_H if r.isSub else self.MAIN_H) + self.GAP
		return h

	def __OnScroll(self):
		self.__Layout()

	def __Layout(self):
		scrollPos = self.scrollBar.GetPos() if self.scrollBar else 0.0
		overflow = max(0, self.__TotalHeight() - self.GetHeight())
		y = 2 - int(scrollPos * overflow)
		for r in self.rows:
			if r.hiddenBySection:
				r.Hide()
				continue
			r.Show()
			r.SetPosition(1, y)
			y += (self.SUB_H if r.isSub else self.MAIN_H) + self.GAP
		if self.scrollBar:
			total = float(self.__TotalHeight())
			self.scrollBar.SetMiddleBarSize(min(float(self.GetHeight()) / total, 1.0) if total else 1.0)


class ResultList(ui.Window):
	class Row(ui.Window):
		def __init__(self, owner, index, data, isSelected):
			ui.Window.__init__(self)
			self.owner = owner
			self.InfoData = data
			self.Index = index
			self.bIsBlocked = False
			self.IsSelected = isSelected

			vnum, count, price = data["vnum"], data["count"], data["price"]
			item.SelectItem(vnum)
			_, self.itemSize = item.GetItemSize()
			self.Vnum = vnum

			self.bg = ui.ExpandedImageBox()
			self.bg.SetParent(self)
			self.bg.OnMouseOverIn = ui.__mem_func__(self.__OnOverIn)
			self.bg.OnMouseOverOut = ui.__mem_func__(self.__OnOverOut)
			self.bg.OnMouseLeftButtonDown = ui.__mem_func__(self.__OnClick)
			self.bg.Show()
			self.__RefreshBg()
			self.SetSize(ROW_W, ROW_HEIGHTS.get(self.itemSize, 51))

			self.slotIcon = ui.ExpandedImageBox()
			self.slotIcon.SetParent(self.bg)
			self.slotIcon.LoadImage(item.GetIconImageFileName())
			self.slotIcon.SetPosition(COL["icon"], 0)
			self.slotIcon.SetWindowVerticalAlignCenter()
			self.slotIcon.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__IconOverIn)
			self.slotIcon.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__IconOverOut)
			self.slotIcon.SetStringEvent("MOUSE_LEFT_DOWN", ui.__mem_func__(self.__IconPreview), vnum)
			self.slotIcon.Show()

			self.txtQty = ui.TextLine()
			self.txtQty.SetParent(self.bg)
			self.txtQty.AddFlag("not_pick")
			self.txtQty.SetPosition(COL["qty"], 0)
			self.txtQty.SetText("x%d" % max(1, count))
			self.txtQty.SetWindowVerticalAlignCenter()
			self.txtQty.SetVerticalAlignCenter()
			self.txtQty.Show()

			name = item.GetItemName()
			if len(name) >= 28:
				name = name[:28] + ".."
			self.txtName = ui.TextLine()
			self.txtName.SetParent(self.bg)
			self.txtName.AddFlag("not_pick")
			self.txtName.SetPosition(COL["name"], 0)
			if IS_AR:
				self.txtName.SetHorizontalAlignLeft()
			self.txtName.SetText(name)
			self.txtName.SetPackedFontColor(0xfff1e6c0)
			self.txtName.SetWindowVerticalAlignCenter()
			self.txtName.SetVerticalAlignCenter()
			self.txtName.Show()

			self.imgTrans = ui.ExpandedImageBox()
			self.imgTrans.SetParent(self.slotIcon)
			self.imgTrans.AddFlag("not_pick")
			self.imgTrans.LoadImage("icon/item/ingame_convert_Mark.tga")
			self.imgTrans.SetPosition(1, 1)
			if data.get("trans", 0) > 0:
				self.imgTrans.Show()
			else:
				self.imgTrans.Hide()

			self.imgCoin = ui.ExpandedImageBox()
			self.imgCoin.SetParent(self.bg)
			self.imgCoin.LoadImage(PATH_OLD + "yang.png")
			self.imgCoin.SetPosition(COL["coin"], 0)
			self.imgCoin.SetWindowVerticalAlignCenter()
			# premium price-deal dashboard: hover the coin (mirrors the item-icon hover model).
			# Clicking the coin no longer selects the row -- same as the item icon, which is
			# already a non-selecting hover target.
			self.imgCoin.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__PriceOverIn)
			self.imgCoin.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__PriceOverOut)
			self.imgCoin.Show()

			self.txtPrice = ui.TextLine()
			self.txtPrice.SetParent(self.bg)
			self.txtPrice.AddFlag("not_pick")
			self.txtPrice.SetPosition(COL["price"], 0)
			if IS_AR:
				self.txtPrice.SetHorizontalAlignLeft()
			self.txtPrice.SetText(str(localeinfo.NumberToMoneyString(price)))
			self.txtPrice.SetOutline()
			self.txtPrice.SetPackedFontColor(0xffe8a710 if price <= 100000000 else 0xffe88510)
			self.txtPrice.SetWindowVerticalAlignCenter()
			self.txtPrice.SetVerticalAlignCenter()
			self.txtPrice.Show()

			rawName = data["owner_name"]
			seller = rawName[:rawName.find('@')] if '@' in rawName else "NONAME"
			self.txtSeller = ui.TextLine()
			self.txtSeller.SetParent(self.bg)
			self.txtSeller.AddFlag("not_pick")
			self.txtSeller.SetPosition(COL["seller"], 0)
			self.txtSeller.SetHorizontalAlignCenter()
			self.txtSeller.SetText(str(seller))
			self.txtSeller.SetWindowVerticalAlignCenter()
			self.txtSeller.SetVerticalAlignCenter()
			self.txtSeller.Show()

			self.btnWhisper = ui.MakeButton(self.bg, COL["btnoff1"], 2, "", PATH_ROOT, "whisper_btn_norm.png", "whisper_btn_hover.png", "whisper_btn_select.png")
			if not IS_AR:
				self.btnWhisper.SetWindowHorizontalAlignRight()
			self.btnWhisper.SetWindowVerticalAlignCenter()
			self.btnWhisper.SetEvent(ui.__mem_func__(self.__OnWhisper))

			self.btnVisit = ui.MakeButton(self.bg, COL["btnoff2"], 1, localeinfo.OFFLINESHOP_SEARCH_VISIT_SHOP, PATH_ROOT, "player_shop_norm.png", "player_shop_hover.png", "player_shop_down.png")
			if not IS_AR:
				self.btnVisit.SetWindowHorizontalAlignRight()
			self.btnVisit.SetWindowVerticalAlignCenter()
			self.btnVisit.SetEvent(ui.__mem_func__(self.__OnVisitShop))

		def __RefreshBg(self):
			state = "hover" if self.IsSelected else "norm"
			self.bg.LoadImage(PATH_ROOT + "bg_item_%d_%s.png" % (self.itemSize, state))

		def __OnOverIn(self):
			self.bg.LoadImage(PATH_ROOT + "bg_item_%d_hover.png" % self.itemSize)

		def __OnOverOut(self):
			self.__RefreshBg()

		def __OnClick(self):
			# toggle selection; owner tells us the new state
			self.IsSelected = self.owner.OnRowToggled(self.InfoData)
			self.__RefreshBg()

		def SetSelectedState(self, flag):
			self.IsSelected = flag
			self.__RefreshBg()

		def __OnWhisper(self):
			self.owner.OnWhisper(self.txtSeller.GetText())

		def __OnVisitShop(self):
			pid = self.InfoData.get("owner", 0)
			if pid:
				offlineshop.SendOpenShop(pid)

		def __IconOverIn(self):
			self.owner.OnIconOverIn(self.InfoData)

		def __IconOverOut(self):
			self.owner.OnIconOverOut()

		def __PriceOverIn(self):
			self.owner.OnPriceOverIn(self.InfoData)

		def __PriceOverOut(self):
			self.owner.OnPriceOverOut()

		def __IconPreview(self, itemVnum = 0):
			if itemVnum == 0:
				return
			if app.ENABLE_RENDER_TARGET and app.IsPressed(app.DIK_LSHIFT):
				handler = systemSetting.GetInterfaceHandler()
				if handler and handler.tooltipItem:
					if uiRenderTarget.IsCanShowItems(itemVnum):
						trans = player.GetChangeLookVnum(itemVnum)
						handler.OpenRenderTargetWindow(0, trans if trans else itemVnum)

		def SetBlock(self):
			self.bIsBlocked = True

		def OnRender(self):
			px, py = self.owner.GetGlobalPosition()
			pw, ph = self.owner.GetWidth(), self.owner.GetHeight()
			for img in (self.bg, self.slotIcon, self.imgTrans, self.imgCoin):
				if img:
					img.SetClipRect(px, py, px + pw, py + ph)
			for t in (self.txtQty, self.txtName, self.txtPrice, self.txtSeller):
				ty = t.GetGlobalPosition()[1]
				if ty < py or ty + t.GetTextSize()[1] > py + ph:
					t.Hide()
				else:
					t.Show()
			for b in (self.btnWhisper, self.btnVisit):
				by = b.GetGlobalPosition()[1]
				if by < py or by + b.GetHeight() > py + ph:
					b.Hide()
				else:
					b.Show()

	def __init__(self):
		ui.Window.__init__(self)
		self.tooltipItem = uitooltip.ItemToolTip()
		self.tooltipItem.Hide()
		self.rows = []
		self.scrollBar = None
		self.toggleEvent = None
		self.whisperEvent = None
		self.isSelectedFn = None
		self.priceAvgCacheRef = None
		self.priceDealTip = PriceDealTip()
		self.priceDealTip.Hide()

	def Destroy(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()
			self.tooltipItem = None
		if self.priceDealTip:
			self.priceDealTip.HideToolTip()
			self.priceDealTip = None
		self.rows = []
		self.scrollBar = None
		self.toggleEvent = None
		self.whisperEvent = None
		self.isSelectedFn = None
		self.priceAvgCacheRef = None

	def SetToggleEvent(self, fn):		self.toggleEvent = fn
	def SetWhisperEvent(self, fn):		self.whisperEvent = fn
	def SetIsSelectedFn(self, fn):		self.isSelectedFn = fn
	def SetPriceAvgCache(self, d):		self.priceAvgCacheRef = d

	def SetScrollBar(self, bar):
		bar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		bar.SetScrollStep(0.2)
		self.scrollBar = bar

	def OnRowToggled(self, data):
		if self.toggleEvent:
			return self.toggleEvent(data)
		return False

	def OnWhisper(self, name):
		if self.whisperEvent:
			self.whisperEvent(name)

	def OnIconOverIn(self, data):
		if not self.tooltipItem or not data:
			return
		self.tooltipItem.ClearToolTip()
		sockets = [data["socket"][n] for n in xrange(player.METIN_SOCKET_MAX_NUM)]
		attrs = [(data["attr"][n]['type'], data["attr"][n]['value']) for n in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
		itemApplyList = None
		if app.ENABLE_APPLY_RANDOM_SHOP:
			itemApplyList = [(data["rand"][n]["type"], data["rand"][n]["value"], data["rand"][n]["path"]) for n in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]
		itemEnchantList = None
		if app.USE_ENCHANT_COSTUMES:
			itemEnchantList = [(data["enchant"][n]["type"], data["enchant"][n]["value"], data["enchant"][n]["time"]) for n in xrange(player.ENCHANT_SLOT_MAX_NUM)]
		setItem = data["setItem"] if app.ENABLE_SET_ITEM else 0
		restrictInfo = None
		if app.ENABLE_EQUIPMENT_RESTRICTION and data.has_key("restrict"):
			restrictInfo = data["restrict"]
		self.tooltipItem.AddItemData(data["vnum"], sockets, attrs, None, 0, 0, player.INVENTORY, -1, None, itemApplyList, 0, data["trans"], enchantList = itemEnchantList, iSetValue = setItem, restrictInfo = restrictInfo)
		# market-% (premium): moved off the row into the tooltip per spec
		if app.USE_OFFLINESHOP_PRICE_AVERAGE and _IsSearchPremium() and self.priceAvgCacheRef:
			avg = self.priceAvgCacheRef.get(data["vnum"], 0)
			if avg > 0:
				# avg is PER-UNIT: rate the per-unit price, not the stack total,
				# else a fairly-priced x20 stack reads as wildly overpriced.
				count = max(1, data["count"])
				pct = int(round(100.0 * (float(data["price"]) / count) / float(avg)))
				if pct < 95:
					color = 0xFF2ecc71
				elif pct > 105:
					color = 0xFFe74c3c
				else:
					color = 0xFFbdc3c7
				self.tooltipItem.AppendSpace(5)
				self.tooltipItem.AppendTextLine(localeinfo.OFFLINESHOP_SEARCH_MARKET_PCT % pct, color)
				self.tooltipItem.ResizeToolTip()

	def OnIconOverOut(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OnPriceOverIn(self, data):
		# Premium-only price-deal dashboard on the coin hover. Zero server calls:
		# reads the already-cached average, does client-side math.
		if not self.priceDealTip or not data:
			return
		if not (app.USE_OFFLINESHOP_PRICE_AVERAGE and _IsSearchPremium()):
			return
		price = data["price"]
		count = max(1, data["count"])
		# The cached average is PER-UNIT. The listing price is the whole stack, so the
		# rating (and the vs-avg %) must run on the per-unit price -- comparing the stack
		# total to a per-unit avg falsely reads a fair x20 stack as "+1900% overpriced".
		unitPrice = float(price) / count
		avg = self.priceAvgCacheRef.get(data["vnum"], 0) if self.priceAvgCacheRef else 0

		grey  = 0xffbdc3c7
		white = 0xffffffff
		rows = [(localeinfo.OFFLINESHOP_DEAL_PRICE, str(localeinfo.NumberToMoneyString(price)), grey, white)]
		# per-unit right under the stack price so it lines up with the per-unit avg below
		if count > 1:
			rows.append((localeinfo.OFFLINESHOP_DEAL_PER_UNIT % count, str(localeinfo.NumberToMoneyString(int(round(unitPrice)))), grey, white))
		if avg > 0:
			rows.append((localeinfo.OFFLINESHOP_DEAL_AVG, str(localeinfo.NumberToMoneyString(avg)), grey, white))

		tier, delta = shop_deal_rating.compute_deal_rating(unitPrice, avg)
		labelKey, color = _DEAL_TIER_UI[tier]
		label = getattr(localeinfo, labelKey)
		deltaStr = "" if delta is None else (localeinfo.OFFLINESHOP_DEAL_VS_AVG % ("%+.1f%%" % delta))
		rows.append((label, deltaStr, color, color))		# rating verdict row (tier-coloured)

		self.priceDealTip.Set(rows)
		self.priceDealTip.ShowToolTip()

	def OnPriceOverOut(self):
		if self.priceDealTip:
			self.priceDealTip.HideToolTip()

	def SetRows(self, dataList, baseIndex = 0):
		self.Clear()
		for i in xrange(len(dataList)):
			data = dataList[i]
			isSel = bool(self.isSelectedFn and self.isSelectedFn(data["id"]))
			row = self.Row(self, baseIndex + i, data, isSel)
			row.SetParent(self)
			row.Show()
			self.rows.append(row)
		if self.scrollBar:
			self.scrollBar.SetPos(0)
		self.__AdjustScrollBar()
		self.__Layout()

	def RemoveItemBought(self, owner, itemID):
		for row in self.rows:
			if row.InfoData["owner"] == owner and row.InfoData["id"] == itemID:
				row.SetBlock()
				row.Hide()
				break
		self.__AdjustScrollBar()
		self.__Layout()

	def Clear(self):
		for row in self.rows:
			row.Hide()
		self.rows = []

	def __TotalHeight(self):
		h = 0
		for row in self.rows:
			if row.bIsBlocked:
				continue
			h += row.GetHeight() + 2
		return h

	def __AdjustScrollBar(self):
		if not self.scrollBar:
			return
		total = float(self.__TotalHeight())
		self.scrollBar.SetMiddleBarSize(min(float(self.GetHeight()) / total, 1.0) if total else 1.0)

	def __OnScroll(self):
		self.__Layout()

	def __Layout(self):
		scrollPos = self.scrollBar.GetPos() if self.scrollBar else 0.0
		overflow = max(0, self.__TotalHeight() - self.GetHeight())
		y = -int(scrollPos * overflow)
		for row in self.rows:
			if row.bIsBlocked:
				continue
			row.SetPosition(0, y)
			y += row.GetHeight() + 2


# shop-search ComboBoxNew colors (user-specified, 0xffRRGGBB): bg 171411, hover 312a21,
# edge 3b332a. Passed per-instance so the shared widget's default look is untouched.
# The in-popup row-highlight is the shared ListBox.SELECT_COLOR and is left alone.
_COMBO_BG     = 0xff171411
_COMBO_HOVER  = 0xff312a21
_COMBO_BORDER = 0xff3b332a

# price-deal dashboard: rating tier -> (localeinfo attr name, packed ARGB colour)
_DEAL_TIER_UI = {
	"GREAT":  ("OFFLINESHOP_DEAL_GREAT",  0xff2ecc71),
	"GOOD":   ("OFFLINESHOP_DEAL_GOOD",   0xff58d68d),
	"FAIR":   ("OFFLINESHOP_DEAL_FAIR",   0xffbdc3c7),
	"ABOVE":  ("OFFLINESHOP_DEAL_ABOVE",  0xfff39c12),
	"OVER":   ("OFFLINESHOP_DEAL_OVER",   0xffe74c3c),
	"NODATA": ("OFFLINESHOP_DEAL_NODATA", 0xff95a5a6),
}


class PriceDealTip(ui.Window):
	"""Cursor-following hover popup that renders the deal info as a lined ui.Table
	(syshelp palette). Built on ui.Window (NOT uitooltip.ToolTip -- the live client's
	packed uitooltip exposes no module-level ToolTip base) with a Bar fill + Box frame;
	the table is rebuilt per hover and old widgets are dropped so GC tears them down."""

	# syshelp table palette: [line, headerBg, rowBg, headerText, cellText]
	SCHEME = [0xff756657, 0xff281f1a, 0xff1a1615, 0xffcabdab, 0xffc7c7c7]
	LINE_C = 0xff756657
	BG_C   = 0xff1a1615
	PAD    = 8
	ROW_H  = 19
	COL_L  = 112
	COL_V  = 108

	def __init__(self):
		ui.Window.__init__(self, "TOP_MOST")
		self.AddFlag("float")		# float so SetTop actually lifts it above the search window
		self.AddFlag("not_pick")	# passive display -- never intercept the mouse
		self.bg = ui.Bar()
		self.bg.SetParent(self)
		self.bg.AddFlag("attach")
		self.bg.AddFlag("not_pick")
		self.bg.SetPosition(0, 0)
		self.bg.SetColor(self.BG_C)
		self.bg.Show()
		self.frame = ui.Box()
		self.frame.SetParent(self)
		self.frame.AddFlag("attach")
		self.frame.AddFlag("not_pick")
		self.frame.SetPosition(0, 0)
		self.frame.SetColor(self.LINE_C)
		self.frame.Show()
		self.table = None
		self.gridBars = []
		self.Hide()

	def __ClearTable(self):
		for w in self.gridBars:
			w.Hide()
		self.gridBars = []
		if self.table:
			self.table.Hide()
			self.table = None

	def Set(self, rows):
		# rows: list of (labelText, valueText, labelColor, valueColor)
		self.__ClearTable()
		if IS_AR:
			widths = [self.COL_V, self.COL_L]		# label reads on the right under RTL
		else:
			widths = [self.COL_L, self.COL_V]
		tbl = ui.Table(self.COL_L + self.COL_V, 0, self.SCHEME)	# head_height 0 -> no header bar
		tbl.SetParent(self)
		tbl.SetPosition(self.PAD, self.PAD)
		tbl.set_columns(["", ""], widths)
		rowHeights = []
		for (lab, val, lc, vc) in rows:
			if IS_AR:
				data, colors, aligns = [val, lab], [vc, lc], ["horizontal:right", "horizontal:right"]
			else:
				data, colors, aligns = [lab, val], [lc, vc], ["horizontal:left", "horizontal:right"]
			tbl.add_row(data, self.ROW_H, cell_colors = colors, cell_aligns = aligns)
			rowHeights.append(self.ROW_H)
		tbl.Show()
		self.table = tbl
		self.__DrawGrid(self.PAD, self.PAD, widths, rowHeights)
		w = self.COL_L + self.COL_V + self.PAD * 2
		h = tbl.table_height + self.PAD * 2
		self.SetSize(w, h)
		self.bg.SetSize(w, h)
		self.frame.SetSize(w, h)

	def __DrawGrid(self, x, y, widths, rowHeights):
		# ui.Table's own inner Lines get covered by each row's opaque bg -> redraw the
		# whole grid as not_pick Bars on top (same fix the wiki/syshelp tables use).
		totalW = sum(widths)
		ys = [y]
		cum = y
		for h in rowHeights:
			cum += h
			ys.append(cum)
		totalH = cum - y
		for yy in ys:
			bar = ui.Bar()
			bar.SetParent(self)
			bar.AddFlag("attach")
			bar.AddFlag("not_pick")
			bar.SetPosition(x, yy)
			bar.SetSize(totalW + 1, 1)
			bar.SetColor(self.LINE_C)
			bar.Show()
			self.gridBars.append(bar)
		xs = [x]
		cx = x
		for w in widths:
			cx += w
			xs.append(cx)
		for xx in xs:
			bar = ui.Bar()
			bar.SetParent(self)
			bar.AddFlag("attach")
			bar.AddFlag("not_pick")
			bar.SetPosition(xx, y)
			bar.SetSize(1, totalH + 1)
			bar.SetColor(self.LINE_C)
			bar.Show()
			self.gridBars.append(bar)

	def ShowToolTip(self):
		self.SetTop()
		self.Show()
		self.__Reposition()

	def HideToolTip(self):
		self.Hide()

	def OnUpdate(self):
		if self.IsShow():
			self.__Reposition()

	def __Reposition(self):
		w, h = self.GetWidth(), self.GetHeight()
		mx, my = wndMgr.GetMousePosition()
		if my < wndMgr.GetScreenHeight() - (h + 40):
			y = my + 30
		else:
			y = my - h - 20
		x = mx - w / 2
		x = max(0, min(x, wndMgr.GetScreenWidth() - w))
		y = max(0, y)
		self.SetPosition(x, y)


class FilterPanel(ui.Window):
	"""Search-narrowing controls that swap in behind the funnel button, inside the
	bgCategory viewport (same rect CategoryList occupies). The control stack is
	taller than the ~311px viewport, so every widget parents to an inner
	self.content window driven by the shared catScroll (see ShopSearch.OnFilterManage,
	which repoints catScroll here while the panel is open, and back to CategoryList
	when it closes)."""

	def __init__(self, owner):
		ui.Window.__init__(self)
		self.owner = owner
		self.attrRows = {}
		self.rowWidgets = []			# top-level widgets shown/hidden per scroll pos (OnRender)
		self.premiumRowWidgets = []		# subset of rowWidgets also gated by _IsSearchPremium()
		self.premiumOn = True
		self.contentHeight = 0
		self.scrollBar = None

		self.content = ui.Window()
		self.content.SetParent(self)
		self.content.SetPosition(0, 0)
		self.content.Show()		# MUST show: children render only if this ancestor is shown

		# (gender + class toggles removed per design -- raceflag/sex now always neutral)

		# min/max edit pairs on input_filter_bg (93x23)
		def Pair(labelMin, labelMax, y):
			mins = self.__Edit(labelMin, 4, y)
			maxs = self.__Edit(labelMax, 96, y)
			return mins, maxs
		self.edStackMin, self.edStackMax = Pair(localeinfo.SEARCH_FILTER_STACK_MIN, localeinfo.SEARCH_FILTER_STACK_MAX, 32)
		self.edAvgMin,   self.edAvgMax   = Pair(localeinfo.SEARCH_FILTER_AVG_MIN, localeinfo.SEARCH_FILTER_AVG_MAX, 58)
		self.edSkillMin, self.edSkillMax = Pair(localeinfo.SEARCH_FILTER_SK_MIN, localeinfo.SEARCH_FILTER_SK_MAX, 84)
		self.edAbsMin,   self.edAbsMax   = Pair(localeinfo.SEARCH_FILTER_ABS_MIN, localeinfo.SEARCH_FILTER_ABS_MAX, 110)

		# NOTE: all ComboBoxNew dropdowns are created LAST (end of __init__) so their
		# downward-opening popups render on top of the widgets below them -- see there.

		# bonus (attribute) rows: bonus_filter_title header + 5 picker rows
		self.bonusTitle = ui.MakeImageBox(self.content, PATH_ROOT + "bonus_filter_title.png", 0, 188)
		self.bonusTitle.AddFlag("not_pick")
		self.rowWidgets.append(self.bonusTitle)
		self.contentHeight = max(self.contentHeight, 188 + self.bonusTitle.GetHeight())
		for i in xrange(5):
			attr = uiswitchbot.SwitchbotAttribute()
			attr.SetParent(self.content)
			attr.Create(178, i)
			y = 212 + 27 * i
			attr.SetPosition(2, y)
			attr.SetSearchEvent(ui.__mem_func__(self.__OnSearchAttribute))
			attr.attributeUpdateEvent = None
			attr.SetEscapeEvent(ui.__mem_func__(self.owner.Close))
			attr.keyAttr = 0
			attr.Show()
			self.attrRows[i] = attr
			self.rowWidgets.append(attr)
			self.contentHeight = max(self.contentHeight, y + attr.GetHeight())
		self.attributeSearchWindow = None
		self.attrSearchIdx = -1

		# premium: price range (sort combo is created with the other combos at the end)
		self.edYangMin = self.__Edit(localeinfo.SEARCH_FILTER_YANG_MIN, 4, 350, premium = True)
		self.edYangMax = self.__Edit(localeinfo.SEARCH_FILTER_YANG_MAX, 96, 350, premium = True)

		# top row: save preset (left) + reset filter (right)
		self.btnSave = ui.MakeButton(self.content, 4, 2, "", PATH_ROOT, "save_normal.png", "save_hover.png", "save_down.png")
		self.btnSave.SetText(localeinfo.OFFLINESHOP_SEARCH_FILTER_SAVE)
		self.btnSave.SetEvent(ui.__mem_func__(self.__OnSaveClicked))
		self.rowWidgets.append(self.btnSave)
		self.contentHeight = max(self.contentHeight, 2 + self.btnSave.GetHeight())

		self.btnReset = ui.MakeButton(self.content, 96, 2, "", PATH_ROOT, "save_normal.png", "save_hover.png", "save_down.png")
		self.btnReset.SetText(localeinfo.SEARCH_SHOP_FILTER_RESET)
		self.btnReset.SetEvent(ui.__mem_func__(self.Reset))
		self.rowWidgets.append(self.btnReset)
		self.contentHeight = max(self.contentHeight, 2 + self.btnReset.GetHeight())

		# --- combos LAST so their popups render above everything below them ---
		# ComboBoxNew popups are TOP_MOST but SetParent drops them into this content
		# subtree's render order, so creation order decides z. Create bottom-to-top so an
		# upper combo's downward popup also covers the combos beneath it.
		self.cbSort = self.__Combo(4, 376, [localeinfo.SEARCH_FILTER_SORT_UNIT_ASC, localeinfo.SEARCH_FILTER_SORT_UNIT_DESC, localeinfo.SEARCH_FILTER_SORT_TOTAL_ASC, localeinfo.SEARCH_FILTER_SORT_TOTAL_DESC, localeinfo.SEARCH_FILTER_SORT_LEVEL, localeinfo.SEARCH_FILTER_SORT_RECENT], width = 185, premium = True)
		self.cbDsGrade = self.__Combo(4, 162, [localeinfo.SEARCH_FILTER_ALCHEMY_GRADE, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE1, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE2, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE3, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE4, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE5, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE6])
		self.cbDsLevel = self.__Combo(96, 162, [localeinfo.SEARCH_FILTER_ALCHEMY_LV, "+0", "+1", "+2", "+3", "+4", "+5", "+6"])
		self.cbRefineMin = self.__Combo(4, 136, [localeinfo.SEARCH_FILTER_REFINE_MIN, "+2", "+3", "+4", "+5", "+6", "+7", "+8", "+9"])
		self.cbRefineMax = self.__Combo(96, 136, [localeinfo.SEARCH_FILTER_REFINE_MAX, "+2", "+3", "+4", "+5", "+6", "+7", "+8", "+9"])

		self.contentHeight += 10		# bottom margin
		self.content.SetSize(182, self.contentHeight)

	def Destroy(self):
		self.scrollBar = None
		self.attrRows = {}
		self.rowWidgets = []
		self.premiumRowWidgets = []
		self.attributeSearchWindow = None

	def __Edit(self, overlay, x, y, premium = False):
		box = ui.MakeImageBox(self.content, PATH_ROOT + "input_filter_bg.png", x, y)
		ed = ui.EditLine()
		ed.SetParent(box)
		ed.SetMax(12)
		ed.SetSize(box.GetWidth() - 6, 17)
		ed.SetPosition(3, 4)
		ed.SetLimitWidth(box.GetWidth() - 6)
		if IS_AR:
			# SetOverlayTextAE hardcodes a -25 offset that shoves this placeholder LEFT into
			# the neighbouring box; place it inside THIS field instead, right-anchored like
			# the combo box-text (mirrors the popup list rows).
			ed.SetOverlayText(overlay)
			ed.overLay.SetWindowHorizontalAlignLeft()
			ed.overLay.SetHorizontalAlignLeft()
			ed.overLay.SetPosition(ed.GetWidth() - 10, 0)
		else:
			ed.SetOverlayText(overlay)
		ed.SetOutline()
		ed.Show()
		box.edit = ed		# keep the EditLine alive (SetParent holds no ref)
		self.rowWidgets.append(box)
		self.contentHeight = max(self.contentHeight, y + box.GetHeight())
		if premium:
			self.premiumRowWidgets.append(box)
		return ed

	def __Combo(self, x, y, texts, width = 93, premium = False):
		# ComboBoxNew: modern flat dropdown (draws its own bordered bar + arrow), so
		# no combobox_background.png frame behind it. API-identical to the old ComboBox.
		cb = ui.ComboBoxNew(borderColor = _COMBO_BORDER, boxFill = _COMBO_BG, listFill = _COMBO_BG, hoverFill = _COMBO_HOVER)
		cb.SetParent(self.content)
		cb.SetPosition(x, y)
		cb.SetSize(width, 21)
		cb.SetEventNew(ui.__mem_func__(self.__OnCombo))
		for i in xrange(len(texts)):
			cb.InsertItem2(i, texts[i])
		cb.SetCurrentItem(texts[0])
		cb.Show()
		self.rowWidgets.append(cb)
		self.contentHeight = max(self.contentHeight, y + 21)
		if premium:
			self.premiumRowWidgets.append(cb)
		return cb

	def __OnCombo(self, wnd, index, name):
		wnd.SetCurrentItem(name)

	def __OnSearchAttribute(self, attrIdx):
		# opens the switchbot attribute chooser (same flow as the old panel)
		if self.attributeSearchWindow:
			self.attributeSearchWindow.Close()
			self.attributeSearchWindow = None
		self.attrSearchIdx = attrIdx
		wnd = uiswitchbot.SearchListWindow()
		wnd.MakeWindow(260, 260)
		wnd.SetTitleName(localeinfo.SWITCHBOT_SELECT_ATTR)
		wnd.SetAcceptArgsType("KEY_VALUE")
		(mx, my) = wndMgr.GetMousePosition()
		wnd.SetPosition(max(0, min(mx - 130, wndMgr.GetScreenWidth() - 260)), max(0, min(my - 130, wndMgr.GetScreenHeight() - 260)))
		for addonType, maxValue in uiswitchbot.ADDON_TYPES.iteritems():
			s = uiswitchbot.GetAffectString(addonType, maxValue)
			if s:
				wnd.AppendItem(addonType, s)
		for t in xrange(200):
			s = uiswitchbot.GetAffectString(t, 0)
			if not s or s.find("UNKNOWN_TYPE") != -1:
				continue
			wnd.AppendItem(t, s)
		wnd.SetAcceptEvent(ui.__mem_func__(self.__OnAcceptAttribute))
		wnd.SetCancelEvent(ui.__mem_func__(self.__OnCancelAttribute))
		wnd.SetTop()
		wnd.Open()
		self.attributeSearchWindow = wnd

	def __OnCancelAttribute(self):
		pass

	def __OnAcceptAttribute(self, key, value):
		row = self.attrRows.get(self.attrSearchIdx, None)
		if not row:
			return
		row.keyAttr = key
		row.SetAttribute(value, uiswitchbot.ADDON_TYPES.get(key, 0))

	def __Int(self, ed):
		t = ed.GetText()
		try:
			return int(t) if t else 0
		except Exception:
			return 0

	def SetScrollBar(self, bar):
		bar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		bar.SetScrollStep(0.15)
		self.scrollBar = bar
		self.__Layout()

	def __OnScroll(self):
		self.__Layout()

	def __Layout(self):
		scrollPos = self.scrollBar.GetPos() if self.scrollBar else 0.0
		overflow = max(0, self.contentHeight - self.GetHeight())
		y = -int(scrollPos * overflow)
		self.content.SetPosition(0, y)
		if self.scrollBar:
			total = float(self.contentHeight)
			self.scrollBar.SetMiddleBarSize(min(float(self.GetHeight()) / total, 1.0) if total else 1.0)

	def OnRender(self):
		# this engine's SetClipRect is a no-op on anything but CExpandedImageBox
		# (confirmed in PythonWindowManagerModule.cpp: wndSetClipRect only calls
		# SetImageClipRect when IsType(CExpandedImageBox)) -- ui.MakeImageBox here
		# returns a plain ImageBox and self.content is a plain Window, so a single
		# clip call on either would silently do nothing. Fall back to per-row
		# show/hide against the viewport, same technique CategoryList.Row.OnRender
		# and ResultList.Row.OnRender already use in this file.
		py = self.GetGlobalPosition()[1]
		ph = self.GetHeight()
		for w in self.rowWidgets:
			if w in self.premiumRowWidgets and not self.premiumOn:
				w.Hide()
				continue
			wy = w.GetGlobalPosition()[1]
			wh = w.GetHeight()
			if wy < py or wy + wh > py + ph:
				w.Hide()
			else:
				w.Show()

	def UpdatePremiumWidgets(self):
		self.premiumOn = _IsSearchPremium()

	def __OnSaveClicked(self):
		self.owner.OnSaveFilterClicked()

	def Reset(self):
		for ed in (self.edStackMin, self.edStackMax, self.edAvgMin, self.edAvgMax, self.edSkillMin, self.edSkillMax, self.edAbsMin, self.edAbsMax, self.edYangMin, self.edYangMax):
			ed.SetText("")
		for cb, text0 in ((self.cbRefineMin, localeinfo.SEARCH_FILTER_REFINE_MIN), (self.cbRefineMax, localeinfo.SEARCH_FILTER_REFINE_MAX), (self.cbDsGrade, localeinfo.SEARCH_FILTER_ALCHEMY_GRADE), (self.cbDsLevel, localeinfo.SEARCH_FILTER_ALCHEMY_LV)):
			cb.SetCurrentItem(text0)
			cb.listBox.selectedLine = -1		# ComboBox has no SetSelectedItem(); reset the backing ListBox directly
		for i in self.attrRows:
			self.attrRows[i].keyAttr = 0
			self.attrRows[i].SetAttribute(localeinfo.SWITCHBOT_EMPTY_ATTR, 0)

	def BuildFilterTuple(self, type, subtype, name, bIsPlayerName, page, sortMode):
		raceflag = 0		# gender + class toggles removed -> no race/sex filtering
		lvMin = self.cbRefineMin.listBox.GetSelectedItem()
		lvMax = self.cbRefineMax.listBox.GetSelectedItem()
		if lvMin != 0:
			lvMin += 1
		if lvMax != 0:
			lvMax += 1
		dsGrade = self.cbDsGrade.listBox.GetSelectedItem()
		dsLevel = self.cbDsLevel.listBox.GetSelectedItem()
		dsGrade = 255 if dsGrade == 0 else dsGrade - 1
		dsLevel = 255 if dsLevel == 0 else dsLevel - 1
		attributes = []
		for i in xrange(5):
			row = self.attrRows[i]
			val = 0
			t = row.valueEditLine.GetText()
			if t:
				try:
					val = int(t)
				except Exception:
					val = 0
			attributes.append((row.keyAttr if val else 0, val))
		yangMin, yangMax = self.__Int(self.edYangMin), self.__Int(self.edYangMax)
		if not _IsSearchPremium():
			yangMin, yangMax, sortMode = 0, 0, 0
		else:
			panelSort = self.cbSort.listBox.GetSelectedItem()
			if panelSort:
				sortMode = panelSort
		if type == -1:
			type, subtype = 0, 255
		if subtype == -1:
			subtype = 255
		return (type, subtype, name, bIsPlayerName,
			(self.__Int(self.edStackMin), self.__Int(self.edStackMax)),
			(lvMin, lvMax),
			(self.__Int(self.edAvgMin), self.__Int(self.edAvgMax)),
			(self.__Int(self.edSkillMin), self.__Int(self.edSkillMax)),
			(self.__Int(self.edAbsMin), self.__Int(self.edAbsMax)),
			(dsGrade, dsLevel), (False, False),
			raceflag, tuple(attributes), (yangMin, yangMax), page, MAX_ITEMS_APPEND, sortMode)


class BuyDialog(ui.ScriptWindow):
	ROTATE_SEC = 0.9
	DLG_W, DLG_H = 247, 160

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		# top-level (NOT parented to the search window): the engine drags a titlebar's
		# GetRoot(), so a child dialog's drag would grab the search window instead.
		# "float" + SetTop() render it above the search window's dim layer.
		self.AddFlag("movable")
		self.AddFlag("float")
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		self.entries = []
		self.rotIndex = 0
		self.rotNextAt = 0.0
		self.acceptEvent = None
		self.closeEvent = None

		self.tooltipItem = uitooltip.ItemToolTip()
		self.tooltipItem.Hide()

		self.board = ui.MakeBoardWithTitleBar(self, "", localeinfo.OFFLINESHOP_SEARCH_BUY_TITLE, ui.__mem_func__(self.Close), self.DLG_W, self.DLG_H)
		self.SetSize(self.DLG_W, self.DLG_H)

		self.bg = ui.MakeImageBox(self.board, PATH_ROOT + "buy_bg.png", 8, 32)
		# preview frame is baked into buy_bg on the LEFT; mirror the whole content under AR
		self.iconX = 179 if IS_AR else 18
		self.textX = 24 if IS_AR else 92		# left edge of the text block

		self.icon = ui.ExpandedImageBox()
		self.icon.SetParent(self.bg)
		self.icon.SetPosition(self.iconX, 8)
		self.icon.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__IconOverIn)
		self.icon.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__IconOverOut)
		self.icon.Show()

		self.txtSub = ui.TextLine()
		self.txtSub.SetParent(self.bg)
		self.txtSub.SetPosition(self.textX + 62, 8)
		self.txtSub.SetHorizontalAlignCenter()
		self.txtSub.Show()

		self.txtCountLabel, self.txtCountValue = self.__MakeKV(localeinfo.OFFLINESHOP_SEARCH_BUY_COUNT, 35)
		self.txtPriceLabel, self.txtPriceValue = self.__MakeKV(localeinfo.OFFLINESHOP_SEARCH_BUY_PRICE, 62)
		self.txtPriceValue.SetPackedFontColor(0xfff39c12)

		bx = self.textX + 8
		self.btnYes = ui.MakeButtonNew(self.bg, bx, 92, localeinfo.OFFLINESHOP_BUY_ITEM_QUESTION_ACCEPT, PATH_ROOT, "btn_activ_norm.png", "btn_activ_hover.png", "btn_activ_select.png")
		self.btnNo  = ui.MakeButtonNew(self.bg, bx + 60, 92, localeinfo.OFFLINESHOP_BUY_ITEM_QUESTION_CANCEL, PATH_ROOT, "btn_activ_norm.png", "btn_activ_hover.png", "btn_activ_select.png")
		if IS_AR:
			# mirrored order: Yes on the right
			self.btnNo.SetPosition(2, 92)
			self.btnYes.SetPosition(86, 92)
		self.btnYes.SetEvent(ui.__mem_func__(self.OnAccept))
		self.btnNo.SetEvent(ui.__mem_func__(self.Close))
		self.Hide()

	def __MakeKV(self, labelText,y):
		label = ui.TextLine()
		label.SetParent(self.bg)
		value = ui.TextLine()
		value.SetParent(self.bg)
		if IS_AR:
			label.SetPosition(self.textX + 124, y)
			label.SetHorizontalAlignLeft()
			value.SetPosition(self.textX, y)
		else:
			label.SetPosition(self.textX, y)
			value.SetPosition(self.textX + 124, y)
			value.SetHorizontalAlignRight()
		label.SetText(labelText)
		label.Show()
		value.Show()
		return label, value

	def SetCloseEvent(self, fn):
		self.closeEvent = fn

	def Open(self, entries, acceptEvent, posX = None, posY = None):
		if not entries:
			return
		self.entries = entries
		self.acceptEvent = acceptEvent
		self.rotIndex = 0
		self.rotNextAt = GetTime() + self.ROTATE_SEC
		self.__ShowEntry(0)
		count = len(entries)
		if count > 1:
			self.txtSub.SetText(localeinfo.OFFLINESHOP_SEARCH_MULTIBUY)
		else:
			item.SelectItem(entries[0]["vnum"])
			self.txtSub.SetText(item.GetItemName())
		self.txtCountValue.SetText(str(count))
		self.txtCountValue.SetHorizontalAlignRight()
		total = 0
		for e in entries:
			total += e["price"]
		self.txtPriceValue.SetText(str(localeinfo.NumberToMoneyString(total)))
		self.txtPriceValue.SetHorizontalAlignRight()
		if posX is not None and posY is not None:
			self.SetPosition(posX, posY)
		else:
			self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def __ShowEntry(self, idx):
		item.SelectItem(self.entries[idx]["vnum"])
		self.icon.LoadImage(item.GetIconImageFileName())
		# keep the hover tooltip in sync with the rotating preview
		if self.tooltipItem and self.tooltipItem.IsShow():
			self.__ShowEntryTooltip(idx)

	def __ShowEntryTooltip(self, idx):
		# full tooltip from the captured result dict (sockets/attrs/etc); vnum-only fallback
		if not self.tooltipItem or idx < 0 or idx >= len(self.entries):
			return
		self.tooltipItem.ClearToolTip()
		entry = self.entries[idx]
		data = entry.get("data")
		if data:
			sockets = [data["socket"][n] for n in xrange(player.METIN_SOCKET_MAX_NUM)]
			attrs = [(data["attr"][n]['type'], data["attr"][n]['value']) for n in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]
			itemApplyList = None
			if app.ENABLE_APPLY_RANDOM_SHOP:
				itemApplyList = [(data["rand"][n]["type"], data["rand"][n]["value"], data["rand"][n]["path"]) for n in xrange(player.APPLY_RANDOM_SLOT_MAX_NUM)]
			itemEnchantList = None
			if app.USE_ENCHANT_COSTUMES:
				itemEnchantList = [(data["enchant"][n]["type"], data["enchant"][n]["value"], data["enchant"][n]["time"]) for n in xrange(player.ENCHANT_SLOT_MAX_NUM)]
			setItem = data["setItem"] if app.ENABLE_SET_ITEM else 0
			restrictInfo = None
			if app.ENABLE_EQUIPMENT_RESTRICTION and data.has_key("restrict"):
				restrictInfo = data["restrict"]
			self.tooltipItem.AddItemData(data["vnum"], sockets, attrs, None, 0, 0, player.INVENTORY, -1, None, itemApplyList, 0, data["trans"], enchantList = itemEnchantList, iSetValue = setItem, restrictInfo = restrictInfo)
		else:
			self.tooltipItem.AddItemData(entry["vnum"], [0, 0, 0], [(0, 0) for n in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)])
		self.tooltipItem.ShowToolTip()

	def __IconOverIn(self):
		self.__ShowEntryTooltip(self.rotIndex)

	def __IconOverOut(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OnUpdate(self):
		# rotate the preview through the selected items (>1 only)
		if self.IsShow() and len(self.entries) > 1 and GetTime() >= self.rotNextAt:
			self.rotIndex = (self.rotIndex + 1) % len(self.entries)
			self.__ShowEntry(self.rotIndex)
			self.rotNextAt = GetTime() + self.ROTATE_SEC

	def OnAccept(self):
		if self.acceptEvent:
			self.acceptEvent(self.entries)
		self.Close()

	def Close(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()
		self.entries = []
		self.acceptEvent = None
		self.Hide()
		if self.closeEvent:
			self.closeEvent()

	def OnPressEscapeKey(self):
		self.Close()
		return True


class SavedFiltersPopup(ui.ScriptWindow):
	"""List of client-local saved search-filter presets (Task 8). Rebuilt from
	_LoadSavedFilters() every time it's opened, so it always reflects disk state."""

	ROW_H  = 24
	WND_W  = 220
	TOP_Y  = 32
	BTN_W  = 40

	def __init__(self, owner):
		ui.ScriptWindow.__init__(self)
		self.owner = owner			# ShopSearch instance (plain ref; owner outlives us)
		self.AddFlag("movable")
		self.AddFlag("float")
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		self.rows = []			# list of per-row widget tuples (bg, border, txt, btnApply, btnDelete)

		self.board = ui.MakeBoardWithTitleBar(self, "", localeinfo.OFFLINESHOP_SEARCH_SAVED_FILTERS, ui.__mem_func__(self.Close), self.WND_W, self.TOP_Y + 10)
		self.SetSize(self.board.GetWidth(), self.board.GetHeight())
		self.Hide()

	def Destroy(self):
		self.__ClearRows()
		self.owner = None
		self.board = None

	def __ClearRows(self):
		for widgets in self.rows:
			for w in widgets:
				w.Hide()
		self.rows = []

	def Open(self):
		self.__Rebuild()
		self.SetCenterPosition()
		self.SetTop()
		ui.ScriptWindow.Show(self)

	def Close(self):
		self.Hide()

	def __Rebuild(self):
		self.__ClearRows()
		entries = _LoadSavedFilters()
		rowCount = max(len(entries), 1)
		height = self.TOP_Y + rowCount * self.ROW_H + 10
		self.board.SetSize(self.WND_W, height)
		self.SetSize(self.WND_W, height)

		rowW = self.WND_W - 16			# framed row spans the board with an 8px side margin
		# Mirror the row for the Arabic client: action buttons hug the LEFT edge and the
		# preset name is right-anchored; LTR keeps buttons on the right, name on the left.
		if IS_AR:
			bxApply  = 10
			bxDelete = 10 + self.BTN_W
			nameX    = self.WND_W - 14
		else:
			bxDelete = self.WND_W - self.BTN_W - 10
			bxApply  = bxDelete - self.BTN_W
			nameX    = 14

		for i in xrange(len(entries)):
			(name, tup) = entries[i]
			y = self.TOP_Y + i * self.ROW_H

			# framed background: fill (ui.Bar) + outline (ui.Box), reusing the window's
			# dark-table palette, so each preset reads as a distinct row. Created first
			# in the row so the name/buttons render on top of it.
			bg = ui.Bar()
			bg.SetParent(self.board)
			bg.SetPosition(8, y)
			bg.SetSize(rowW, self.ROW_H - 2)
			bg.SetColor(_COMBO_BG)
			bg.Show()
			border = ui.Box()
			border.SetParent(self.board)
			border.SetPosition(8, y)
			border.SetSize(rowW, self.ROW_H - 2)
			border.SetColor(_COMBO_BORDER)
			border.Show()

			txt = ui.TextLine()
			txt.SetParent(self.board)
			txt.SetPosition(nameX, y + 6)
			if IS_AR:
				txt.SetHorizontalAlignLeft()	# fork RTL convention: right-anchored text
			txt.SetText(name)
			txt.Show()

			btnApply = ui.MakeButton(self.board, bxApply, y + 2, localeinfo.OFFLINESHOP_SEARCH_FILTER_APPLY, PATH_ROOT, "btn_ok_normal.png", "btn_ok_hover.png", "btn_ok_down.png")
			btnApply.SetEvent(ui.__mem_func__(self.__OnApply), i)
			btnDelete = ui.MakeButton(self.board, bxDelete, y + 2, localeinfo.OFFLINESHOP_SEARCH_FILTER_DELETE, PATH_ROOT, "btn_delete_normal.png", "btn_delete_hover.png", "btn_delete_down.png")
			btnDelete.SetEvent(ui.__mem_func__(self.__OnDelete), i)

			self.rows.append((bg, border, txt, btnApply, btnDelete))

	def __OnApply(self, index = 0):
		entries = _LoadSavedFilters()
		if index < 0 or index >= len(entries):
			return
		(name, tup) = entries[index]
		if self.owner:
			self.owner.ApplySavedFilter(tup)
		self.Close()

	def __OnDelete(self, index = 0):
		entries = _LoadSavedFilters()
		if index < 0 or index >= len(entries):
			return
		del entries[index]
		_SaveSavedFilters(entries)
		self.__Rebuild()

	def OnPressEscapeKey(self):
		self.Close()
		return True


class ShopSearch(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		self.loaded = 0
		self.interface = None
		self.SearchFilterShopItemResult = []
		self.selected = {}				# itemID -> {"owner":pid, "price":price, "vnum":vnum}
		self.priceAvgCache = {}			# vnum -> 30d average price
		self.sortMode = 0				# 0 unit-asc .. 5 recent (server enum)
		self.sCategory = -1
		self.sSubCategory = -1
		self.currentPage = 1
		self.pageCount = 1
		self._liveSearchPending = False
		self._liveSearchAt = 0
		self._lastLiveSearchText = None
		self.savedFiltersPopup = None
		self.saveFilterDialog = None
		self.LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def LoadWindow(self):
		if self.loaded == 1:
			return
		self.loaded = 1
		self.AddFlag("movable")

		self.Board = ui.MakeBoardWithTitleBar(self, "", localeinfo.OFFLINESHOP_SEARCH, ui.__mem_func__(self.CloseGame), WND_W, WND_H)
		self.SetSize(self.Board.GetWidth(), self.Board.GetHeight())

		# background zones (positions mirror under Arabic)
		lx = (WND_W - LEFT_X - LEFT_W) if IS_AR else LEFT_X
		rx = (WND_W - RIGHT_X - LIST_W) if IS_AR else RIGHT_X
		self.bgInput    = ui.MakeImageBox(self.Board, PATH_ROOT + "bg_input.png", lx, TOP_Y)
		self.bgCategory = ui.MakeImageBox(self.Board, PATH_ROOT + "bg_category.png", lx, CAT_Y)
		self.bgHeader   = ui.MakeImageBox(self.Board, PATH_ROOT + "shop_items_title.png", rx + 2, TOP_Y)
		self.bgList     = ui.MakeImageBox(self.Board, PATH_ROOT + "bg_item_list.png", rx, LIST_Y)
		self.bgFooter   = ui.MakeImageBox(self.Board, PATH_ROOT + "footer_page_bg.png", rx, FOOTER_Y)
		self.leftX, self.rightX = lx, rx

		# --- search input kit (on bg_input) ---
		self.inputField = ui.MakeImageBox(self.bgInput, PATH_ROOT + "input_name_bg.png", 28 if IS_AR else 7, 5)
		self.searchInput = ui.EditLine()
		self.searchInput.SetParent(self.inputField)
		self.searchInput.SetMax(45)
		self.searchInput.SetSize(self.inputField.GetWidth() - 22, 17)
		self.searchInput.SetPosition(18 if IS_AR else 4, 4)
		self.searchInput.SetLimitWidth(self.inputField.GetWidth() - 22)
		if IS_AR:
			self.searchInput.SetOverlayTextNew(localeinfo.OFFLINESHOP_SEARCH_NAME)
		else:
			self.searchInput.SetOverlayText(localeinfo.OFFLINESHOP_SEARCH_NAME)
		self.searchInput.SetReturnEvent(ui.__mem_func__(self.OnSearchReturn))
		self.searchInput.SetEscapeEvent(ui.__mem_func__(self.OnPressNameEscapeKey))
		self.searchInput.SetTabEvent(ui.__mem_func__(self.OnSearchTab))
		self.searchInput.SetUpdateEvent(ui.__mem_func__(self.Search_RefreshTextHint))
		self.searchInput.SetOutline()
		self.searchInput.Show()

		self.searchHint = ui.TextLine()
		self.searchHint.SetParent(self.searchInput)
		self.searchHint.SetPackedFontColor(grp.GenerateColor(1.0, 1.0, 1.0, 0.5))
		self.searchHint.SetPosition(0, 0)
		self.searchHint.AddFlag("not_pick")
		self.searchHint.Show()

		self.btnClearSearch = ui.MakeButton(self.inputField, 3 if IS_AR else self.inputField.GetWidth() - 16, 5, localeinfo.SEARCH_SHOP_RESET, PATH_ROOT, "x_btn_normal.png", "x_btn_hover.png", "x_btn_down.png")
		self.btnClearSearch.SetEvent(ui.__mem_func__(self.OnResetSearch))

		self.btnSearch = ui.MakeButton(self.bgInput, 3 if IS_AR else LEFT_W - 31, 3, False, PATH_ROOT, "btn_search_normal.png", "btn_search_hover.png", "btn_search_down.png")
		self.btnSearch.SetEvent(ui.__mem_func__(self.OnSearch))

		# "search by player name" checkbox (checkbox art reused from old pack)
		self.chkPlayerName = ui.ExpandedImageBox()
		self.chkPlayerName.SetParent(self.bgInput)
		self.chkPlayerName.LoadImage(PATH_OLD + "box_uncheck.png")
		self.chkPlayerName.SetPosition(LEFT_W - 20 if IS_AR else 7, 30)
		self.chkPlayerName.IsChecked = False
		self.chkPlayerName.OnMouseLeftButtonDown = ui.__mem_func__(self.OnTogglePlayerName)
		self.chkPlayerName.Show()
		self.txtPlayerName = ui.TextLine()
		self.txtPlayerName.SetParent(self.bgInput)
		self.txtPlayerName.SetText(localeinfo.OFFLINESHOP_SEARCH_BYNAME)
		if IS_AR:
			self.txtPlayerName.SetPosition(LEFT_W - 26, 31)
			self.txtPlayerName.SetHorizontalAlignLeft()
		else:
			self.txtPlayerName.SetPosition(24, 31)
		self.txtPlayerName.Show()
		# NOTE: one blank row is deliberately reserved under this checkbox for the
		# future "Exact Search" (needs a wire pass; spec 'non-goals').

		# --- filter title bar + icon buttons ---
		self.barFilter = ui.MakeImageBox(self.Board, PATH_ROOT + "filter_title.png", self.leftX + 2, CAT_Y + 4)
		self.btnFilter = ui.MakeButton(self.barFilter, 4 if IS_AR else 144, 0, localeinfo.SEARCH_SHOP_FILTER, PATH_ROOT, "btn_filter_normal.png", "btn_filter_hover.png", "btn_filter_down.png")
		self.btnFilter.SetEvent(ui.__mem_func__(self.OnFilterManage))
		self.btnSavedFilters = ui.MakeButton(self.barFilter, 27 if IS_AR else 167, 0, False, PATH_ROOT, "saved_fitlers_normal.png", "saved_fitlers_hover.png", "saved_fitlers_down.png")
		self.btnSavedFilters.SetEvent(ui.__mem_func__(self.OnOpenSavedFilters))
		self.btnSavedFilters.Show()

		# --- category tree ---
		self.catScroll = _MakeThinScrollBar()
		self.catScroll.allow_on_run_mouse_wheel = False
		self.catScroll.SetParent(self)
		self.catScroll.SetScrollBarSize(CAT_H - 47)
		# 7px AdvScrollBar sits flush inside the panel edge; the freed width goes to the rows
		self.catScroll.SetPosition((self.leftX + 1) if IS_AR else (self.leftX + LEFT_W - 8), CAT_Y + 30)
		self.catScroll.Show()

		self.CategoryList = CategoryList()
		self.CategoryList.SetParent(self.bgCategory)
		# 182 wide: the 180px row art fits fully (1px margin), thin bar takes the rest
		self.CategoryList.SetPosition(10 if IS_AR else 4, 28)
		self.CategoryList.SetSize(182, CAT_H - 34)
		self.CategoryList.SetScrollBar(self.catScroll)
		self.CategoryList.SetSelectEvent(ui.__mem_func__(self.OnSearchByValue))
		self.CategoryList.Build()
		self.CategoryList.Show()

		# --- results header ---
		self.headerTexts = []
		for key, lockey in (("qty", "OFFLINESHOP_SEARCH_COL_QUANTITY"), ("name", "OFFLINESHOP_SEARCH_COL_NAME"), ("price", "OFFLINESHOP_SEARCH_COL_PRICE"), ("seller", "OFFLINESHOP_SEARCH_COL_SELLER")):
			t = ui.TextLine()
			t.SetParent(self.bgHeader)
			hx = HDR[key]
			if IS_AR:
				hx = 536 - hx
			t.SetPosition(hx, 4)
			t.SetHorizontalAlignCenter()
			t.SetOutline()
			t.SetText(getattr(localeinfo, lockey))
			t.Show()
			self.headerTexts.append(t)

		# Price header = the one clickable sort (server modes 0/1). Arrows show active direction.
		self.priceHeaderHit = ui.Window()
		self.priceHeaderHit.SetParent(self.bgHeader)
		px = (536 - HDR["price"]) if IS_AR else HDR["price"]
		self.priceHeaderHit.SetPosition(px - 35, 0)
		self.priceHeaderHit.SetSize(70, HEADER_H)
		self.priceHeaderHit.OnMouseLeftButtonDown = ui.__mem_func__(self.OnTogglePriceSort)
		self.priceHeaderHit.Show()
		self.sortArrow = ui.ExpandedImageBox()
		self.sortArrow.SetParent(self.bgHeader)
		self.sortArrow.LoadImage(PATH_ROOT + "arrow_up.png")
		self.sortArrow.SetPosition(px + 32, 7)
		if _IsSearchPremium():
			self.sortArrow.Show()
		else:
			self.sortArrow.Hide()

		self.ItemList = ResultList()
		self.ItemList.SetParent(self.bgList)
		self.ItemList.SetPosition(3, 3)
		self.ItemList.SetSize(ROW_W, LIST_H - 6)
		self.ItemList.SetIsSelectedFn(ui.__mem_func__(self._IsRowSelected))
		self.ItemList.SetPriceAvgCache(self.priceAvgCache)
		self.ItemList.SetWhisperEvent(ui.__mem_func__(self.OnWhisper))
		self.ItemList.SetToggleEvent(ui.__mem_func__(self.OnToggleRow))
		self.ItemList.Show()

		self.listScroll = _MakeThinScrollBar()
		self.listScroll.allow_on_run_mouse_wheel = False
		self.listScroll.SetParent(self)
		self.listScroll.SetScrollBarSize(LIST_H - 14)
		self.listScroll.SetPosition((self.rightX - 7) if IS_AR else (self.rightX + LIST_W + 2), LIST_Y + 6)
		self.ItemList.SetScrollBar(self.listScroll)
		self.listScroll.Show()

		self.emptyState = ui.TextLine()
		self.emptyState.SetParent(self.bgList)
		self.emptyState.SetWindowHorizontalAlignCenter()
		self.emptyState.SetHorizontalAlignCenter()
		self.emptyState.SetPosition(0, 170)
		self.emptyState.SetText(localeinfo.OFFLINESHOP_SEARCH_EMPTY)
		self.emptyState.Hide()

		self.resultCount = ui.TextLine()
		self.resultCount.SetParent(self.Board)
		self.resultCount.SetPosition(self.leftX + 20, CAT_Y + CAT_H + 4)
		self.resultCount.SetText("")
		self.resultCount.Show()

		# --- footer: selection total + confirm + pagination ---
		fx = self.rightX
		self.totalField = ui.MakeImageBox(self.bgFooter, PATH_ROOT + "price_input.png", (LIST_W - 169) if IS_AR else 6, 5)
		self.txtTotal = ui.TextLine()
		self.txtTotal.SetParent(self.totalField)
		self.txtTotal.SetPosition(0, 4)
		self.txtTotal.SetWindowHorizontalAlignCenter()
		self.txtTotal.SetHorizontalAlignCenter()
		self.txtTotal.Show()

		self.btnBuySelected = ui.MakeButton(self.bgFooter, 346 if IS_AR else 172, 4, localeinfo.OFFLINESHOP_SEARCH_BUY, PATH_ROOT, "btn_ok_normal.png", "btn_ok_hover.png", "btn_ok_down.png")
		#self.btnBuySelected.SetText(localeinfo.OFFLINESHOP_SEARCH_BUY)
		self.btnBuySelected.SetEvent(ui.__mem_func__(self.AskBuySelectedItems))

		self.pageButtons = []
		for i in xrange(5):
			b = ui.MakeButton(self.bgFooter, 0, 5, False, PATH_ROOT, "btn_page_inactive.png", "btn_page_active.png", "btn_page_active.png")
			b.SetText(str(i + 1))
			self.pageButtons.append(b)
		self.btnPrevPage  = ui.MakeButton(self.bgFooter, 0, 5, False, PATH_ROOT, "btn_page_inactive.png", "btn_page_active.png", "btn_page_active.png")
		self.btnPrevPage.SetText("<")
		self.btnFirstPage = ui.MakeButton(self.bgFooter, 0, 5, False, PATH_ROOT, "btn_page_inactive.png", "btn_page_active.png", "btn_page_active.png")
		self.btnFirstPage.SetText("<<")
		self.btnNextPage  = ui.MakeButton(self.bgFooter, 0, 5, False, PATH_ROOT, "btn_page_inactive.png", "btn_page_active.png", "btn_page_active.png")
		self.btnNextPage.SetText(">")
		self.btnLastPage  = ui.MakeButton(self.bgFooter, 0, 5, False, PATH_ROOT, "btn_page_inactive.png", "btn_page_active.png", "btn_page_active.png")
		self.btnLastPage.SetText(">>")
		self.btnPrevPage.SetEvent(ui.__mem_func__(self.PrevPage))
		self.btnFirstPage.SetEvent(ui.__mem_func__(self.FirstPage))
		self.btnNextPage.SetEvent(ui.__mem_func__(self.NextPage))
		self.btnLastPage.SetEvent(ui.__mem_func__(self.LastPage))
		self._RefreshTotal()

		# Wiki-style live item-name dropdown -- created LAST (but before the modal dim
		# layer/buy dialog) so it renders above every panel/scrollbar yet below the modal.
		self.searchDropdown = None
		if app.ENABLE_INGAME_WIKI:
			try:
				import ingamewikisearch
				self.searchDropdown = ingamewikisearch.WikiSearchResults(width = max(self.searchInput.GetWidth() + 60, 180), itemsOnly = True)
				self.searchDropdown.SetParent(self)
				self.searchDropdown.SetPosition(0, 0)
				self.searchDropdown.SetPickEvent(ui.__mem_func__(self.OnSearchNamePicked))
				self.searchDropdown.Hide()
			except Exception:
				self.searchDropdown = None

		# modal dim layer: swallows clicks on the search window while the buy dialog is up
		self.dimmer = ui.Bar()
		self.dimmer.SetParent(self)
		self.dimmer.SetPosition(0, 0)
		self.dimmer.SetSize(WND_W, WND_H)
		self.dimmer.SetColor(0x96000000)
		self.dimmer.Hide()

		# top-level (no SetParent) so its titlebar drags the DIALOG, not the search window
		self.buyDialog = BuyDialog()
		self.buyDialog.SetCloseEvent(ui.__mem_func__(self.OnBuyDialogClosed))

	def SetInterface(self, interface):
		self.interface = interface

	def Show(self):
		self.LoadWindow()
		self.SetCenterPosition()
		self.CategoryList.ResetSelection()
		last = getattr(self, "SearchFilterLastUsedSetting", None)
		if last:
			if constinfo.shopSearchWaitTime - GetTime() <= 0:	# silent cooldown check, no chat warning
				offlineshop.SendFilterRequest(*last)		# remember-last-search on reopen
				self.currentPage = 1
				self._ArmCooldown()
			# else: still cooling down -> keep the already-rendered list, send nothing
			for r in self.CategoryList.rows:
				if r.fire is not None and r.fire == (self.sCategory, self.sSubCategory):
					r.SetSelected(True)
					break
		else:
			self.OnSearchByValue(-1, -1, True, True)	# browse-all; byPass skips the cooldown so opening always loads
		ui.ScriptWindow.Show(self)

	def Close(self, IsFromGame = False):
		if getattr(self, "buyDialog", None) and self.buyDialog.IsShow():
			self.buyDialog.Close()
		if getattr(self, "ItemList", None):
			self.ItemList.OnIconOverOut()
		if getattr(self, "savedFiltersPopup", None) and self.savedFiltersPopup.IsShow():
			self.savedFiltersPopup.Close()
		if getattr(self, "saveFilterDialog", None):
			self.saveFilterDialog.Close()
			self.saveFilterDialog = None
		fp = getattr(self, "filterPanel", None)
		if fp and getattr(fp, "attributeSearchWindow", None):
			fp.attributeSearchWindow.Close()
			fp.attributeSearchWindow = None
		self.Hide()

	def CloseGame(self):
		self.Close(True)

	def OnPressEscapeKey(self):
		self.Close(True)
		return True

	def OnPressNameEscapeKey(self):
		if not self.searchInput.IsShowCursor() or self.searchInput.GetText() == "":
			self.OnPressEscapeKey()
		else:
			self.searchInput.SetText("")
			self.searchHint.SetText("")
		if self.searchDropdown:
			self.searchDropdown.Hide()

	def Search_RefreshTextHint(self):
		BASE = grp.GenerateColor(0.8549, 0.8549, 0.8549, 1.0)
		NOTFOUND = grp.GenerateColor(1.0, 0.2, 0.2, 1.0)
		self.searchHint.SetText("")
		self.searchInput.SetPackedFontColor(BASE)
		text = self.searchInput.GetText()
		if len(text) and not self.chkPlayerName.IsChecked:
			(hintName, vnum) = item.GetItemDataByNamePart(text)
			if vnum == -1:
				self.searchInput.SetPackedFontColor(NOTFOUND)
			else:
				self.searchHint.SetText(text + " " + hintName[len(text):])
		if self.searchDropdown:
			if len(text) and not self.chkPlayerName.IsChecked:
				bx, by = self.searchInput.GetGlobalPosition()
				sx, sy = self.GetGlobalPosition()
				self.searchDropdown.SetPosition(bx - sx - 40, by - sy + self.searchInput.GetHeight() + 2)
				self.searchDropdown.Refresh(text)
			else:
				self.searchDropdown.Hide()
		# debounced live search: re-run shortly after typing stops
		self._liveSearchPending = True
		self._liveSearchAt = GetTime() + 0.35

	def OnUpdate(self):
		if getattr(self, "_liveSearchPending", False) and GetTime() >= self._liveSearchAt:
			self._liveSearchPending = False
			self._FireLiveSearch()

	def _FireLiveSearch(self):
		text = self.searchInput.GetText() or ""
		if text == getattr(self, "_lastLiveSearchText", None):
			return
		self._lastLiveSearchText = text
		self._ClearSelection()
		self.SearchFilterLastUsedSetting = self.GetSearchFilterSettings(self.sCategory, self.sSubCategory)
		offlineshop.SendFilterRequest(*self.SearchFilterLastUsedSetting)
		self.currentPage = 1
		self._ArmCooldown()

	def OnSearchNamePicked(self, vnum, isMob):
		if self.searchDropdown:
			self.searchDropdown.Hide()
		item.SelectItem(vnum)
		name = item.GetItemName()
		if name:
			self.searchInput.SetText(name)
			self.searchInput.SetEndPosition()
			self.searchHint.SetText("")
		self.OnSearch()

	def OnSearchReturn(self):
		if self.searchDropdown and self.searchDropdown.IsShow():
			if self.searchDropdown.PickFirst():
				return
		self.OnSearch()

	def OnSearchTab(self):
		if self.searchDropdown and self.searchDropdown.IsShow():
			vnum = self.searchDropdown.GetHighlightedVnum()
			if vnum:
				item.SelectItem(vnum)
				name = item.GetItemName()
				if name:
					self.searchInput.SetText(name)
					self.searchInput.SetEndPosition()
					self.searchHint.SetText("")
					self.searchDropdown.Hide()
					return
		if self.searchHint.GetText():
			old = self.searchInput.GetText()
			self.searchInput.SetText(old + self.searchHint.GetText()[len(old) + 1:])
			self.searchInput.SetEndPosition()
			self.Search_RefreshTextHint()

	def Destroy(self):
		if getattr(self, "buyDialog", None):
			self.buyDialog.Close()
			self.buyDialog = None
		self.dimmer = None
		if getattr(self, "ItemList", None):
			self.ItemList.Destroy()
			self.ItemList = None
		if getattr(self, "filterPanel", None):
			self.filterPanel.Destroy()
			self.filterPanel = None
		if getattr(self, "savedFiltersPopup", None):
			self.savedFiltersPopup.Close()
			self.savedFiltersPopup.Destroy()
			self.savedFiltersPopup = None
		if getattr(self, "saveFilterDialog", None):
			self.saveFilterDialog.Close()
			self.saveFilterDialog = None
		if getattr(self, "CategoryList", None):
			self.CategoryList.Destroy()
			self.CategoryList = None
		self.searchDropdown = None
		self.interface = None
		self.SearchFilterShopItemResult = []
		self.selected = {}
		self.priceAvgCache = {}

	def _CooldownBlocked(self):
		dif = constinfo.shopSearchWaitTime - GetTime()
		if dif > 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.OFFLINESHOP_RENEWAL_WAIT % (str(dif)[:3]))
			return True
		return False

	def _ArmCooldown(self):
		constinfo.shopSearchWaitTime = GetTime() + constinfo.shopSearchTimeWait

	def GetSearchFilterSettings(self, type = 0, subtype = 255, page = 1):
		name = self.searchInput.GetText() or ""
		sortMode = self.sortMode if _IsSearchPremium() else 0
		if type == -1:
			type, subtype = 0, 255
		if subtype == -1:
			subtype = 255
		if getattr(self, "filterPanel", None):		# Task 7 provides the real filters
			return self.filterPanel.BuildFilterTuple(type, subtype, name, self.chkPlayerName.IsChecked, page, sortMode)
		attributes = tuple([(0, 0) for _ in xrange(5)])
		return (type, subtype, name, self.chkPlayerName.IsChecked,
			(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (255, 255), (False, False),
			0, attributes, (0, 0), page, MAX_ITEMS_APPEND, sortMode)

	def OnSearchByValue(self, Type, SubType, bySearch = False, byPass = False):
		if not byPass and self._CooldownBlocked():
			return False
		self._ArmCooldown()
		self.sCategory = Type
		self.sSubCategory = SubType
		self._ClearSelection()
		self.SearchFilterLastUsedSetting = self.GetSearchFilterSettings(Type, SubType)
		offlineshop.SendFilterRequest(*self.SearchFilterLastUsedSetting)
		self.currentPage = 1
		return True

	def OnSearch(self):
		if self._CooldownBlocked():
			return
		self._ArmCooldown()
		self._ClearSelection()
		self.SearchFilterLastUsedSetting = self.GetSearchFilterSettings(self.sCategory, self.sSubCategory)
		offlineshop.SendFilterRequest(*self.SearchFilterLastUsedSetting)
		self.currentPage = 1

	def OnResetSearch(self):
		self.searchInput.SetText("")
		self.searchHint.SetText("")
		if self.searchDropdown:
			self.searchDropdown.Hide()

	def OnTogglePlayerName(self):
		self.chkPlayerName.IsChecked = not self.chkPlayerName.IsChecked
		self.chkPlayerName.LoadImage(PATH_OLD + ("box_checked.png" if self.chkPlayerName.IsChecked else "box_uncheck.png"))

	def OnFilterManage(self):
		if not getattr(self, "filterPanel", None):
			self.filterPanel = FilterPanel(self)
			self.filterPanel.SetParent(self.bgCategory)
			self.filterPanel.SetPosition(3, 28)
			self.filterPanel.SetSize(LEFT_W - 16, CAT_H - 34)
			self.filterPanel.Hide()
		if self.filterPanel.IsShow():
			self.filterPanel.Hide()
			self.CategoryList.SetScrollBar(self.catScroll)		# rebind FIRST so SetPos(0) drives CategoryList.__OnScroll
			self.CategoryList.Show()
			self.catScroll.Show()
			self.catScroll.SetPos(0)							# now runs CategoryList.__Layout: repositions rows + resets middle-bar size
		else:
			self.CategoryList.Hide()
			self.filterPanel.SetScrollBar(self.catScroll)		# rebind FIRST (SetScrollBar itself lays out); SetPos(0) last for consistency
			self.catScroll.Show()
			self.filterPanel.UpdatePremiumWidgets()
			self.filterPanel.Show()
			self.catScroll.SetPos(0)

	# ---- saved search-filter presets (Task 8) ----
	def OnOpenSavedFilters(self):
		if not getattr(self, "savedFiltersPopup", None):
			self.savedFiltersPopup = SavedFiltersPopup(self)
		self.savedFiltersPopup.Open()

	def OnSaveFilterClicked(self):
		if getattr(self, "saveFilterDialog", None):
			self.saveFilterDialog.Close()
			self.saveFilterDialog = None
		dlg = uicommon.InputDialog()
		dlg.SetTitle(localeinfo.OFFLINESHOP_SEARCH_FILTER_NAME)
		dlg.SetMaxLength(20)
		dlg.SetAcceptEvent(ui.__mem_func__(self.OnSaveFilterAccept))
		dlg.SetCancelEvent(ui.__mem_func__(self.OnSaveFilterCancel))
		dlg.Open()
		self.saveFilterDialog = dlg		# held so it isn't GC'd while open

	def OnSaveFilterAccept(self):
		dlg = getattr(self, "saveFilterDialog", None)
		if not dlg:
			return
		name = (dlg.GetText() or "").strip()
		name = name.replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()
		dlg.Close()
		self.saveFilterDialog = None
		if not name or not getattr(self, "filterPanel", None):
			return
		tup = self.filterPanel.BuildFilterTuple(self.sCategory, self.sSubCategory, self.searchInput.GetText() or "", self.chkPlayerName.IsChecked, 1, self.sortMode)
		entries = _LoadSavedFilters()
		entries.append((name, tup))
		if len(entries) > MAX_SAVED_FILTERS:
			entries = entries[-MAX_SAVED_FILTERS:]		# drop oldest beyond the cap
		_SaveSavedFilters(entries)

	def OnSaveFilterCancel(self):
		dlg = getattr(self, "saveFilterDialog", None)
		if dlg:
			dlg.Close()
		self.saveFilterDialog = None

	def ApplySavedFilter(self, tup):
		if self._CooldownBlocked():
			return
		self._ArmCooldown()
		self._ClearSelection()
		self.sCategory = tup[0]
		self.sSubCategory = tup[1]
		self.SearchFilterLastUsedSetting = tup
		offlineshop.SendFilterRequest(*tup)
		self.currentPage = 1

	def OnTogglePriceSort(self):
		if not _IsSearchPremium():
			return
		self.sortMode = 1 if self.sortMode == 0 else 0
		self.sortArrow.LoadImage(PATH_ROOT + ("arrow_down.png" if self.sortMode == 1 else "arrow_up.png"))
		self.OnSearch()

	def OnRunMouseWheel(self, nLen):
		if getattr(self, "buyDialog", None) and self.buyDialog.IsShow():
			return True	# modal: swallow wheel too, don't let it fall through to the dimmed lists
		if self.catScroll and self.catScroll.IsShow():
			if self.catScroll.IsInPosition() or self.CategoryList.IsInPosition() or (getattr(self, "filterPanel", None) and self.filterPanel.IsShow() and self.filterPanel.IsInPosition()):
				if nLen > 0:
					self.catScroll.OnUp()
				else:
					self.catScroll.OnDown()
				return True
		if self.listScroll and self.listScroll.IsShow():
			if self.listScroll.IsInPosition() or self.ItemList.IsInPosition():
				if nLen > 0:
					self.listScroll.OnUp()
				else:
					self.listScroll.OnDown()
				return True
		return False

	# ---- public wire-facing interface ----
	def ShopFilterResult(self, size, total = None, page = None):
		self.SearchFilterShopItemResult = []
		if app.USE_OFFLINESHOP_SEARCH_PAGINATION and total is not None:
			self.serverTotalMatches = total
			if page is not None and page > 0:
				self.currentPage = page

	def ShopFilterResultItem_Alloc(self):
		self.SearchFilterShopItemResult.append({})

	def ShopFilterResultItem_SetDict(self, index, d):
		self.SearchFilterShopItemResult.append(d)

	def ShopFilterResultItem_SetValue(self, key, index, *args):
		if key in ("id", "vnum", "count", "price", "owner", "owner_name", "trans", "setItem"):
			self.SearchFilterShopItemResult[index][key] = args[0]
		elif app.ENABLE_EQUIPMENT_RESTRICTION and key == "restrict":
			self.SearchFilterShopItemResult[index][key] = (args[0], args[1])
		elif key == "attr":
			bucket = self.SearchFilterShopItemResult[index].setdefault(key, {})
			bucket[args[0]] = {"type": args[1], "value": args[2]}
		elif app.ENABLE_APPLY_RANDOM_SHOP and key == "rand":
			bucket = self.SearchFilterShopItemResult[index].setdefault(key, {})
			bucket[args[0]] = {"type": args[1], "value": args[2], "path": args[3]}
		elif key == "socket":
			bucket = self.SearchFilterShopItemResult[index].setdefault(key, {})
			bucket[args[0]] = args[1]
		elif app.USE_ENCHANT_COSTUMES and key == "enchant":
			bucket = self.SearchFilterShopItemResult[index].setdefault(key, {})
			bucket[args[0]] = {"type": args[1], "value": args[2], "time": args[3]}

	def ShopFilterResult_Show(self):
		count = len(self.SearchFilterShopItemResult)
		if app.USE_OFFLINESHOP_SEARCH_PAGINATION:
			total = getattr(self, "serverTotalMatches", count)
		else:
			total = count
		self.resultCount.SetText(localeinfo.OFFLINESHOP_SEARCH_RESULT_COUNT % total)
		if count == 0:
			self.emptyState.Show()
		else:
			self.emptyState.Hide()
		self.pageCount = max(1, int(math.ceil(float(total) / float(MAX_ITEMS_APPEND))))
		if self.currentPage > self.pageCount:
			self.currentPage = self.pageCount
		if self.currentPage < 1:
			self.currentPage = 1
		self.RefreshList()
		self.RefreshPaginationButtons()

	def RefreshList(self):
		base = (self.currentPage - 1) * MAX_ITEMS_APPEND
		self.ItemList.SetRows(self.SearchFilterShopItemResult, base)
		if app.USE_OFFLINESHOP_PRICE_AVERAGE and _IsSearchPremium():
			seen = {}
			for d in self.SearchFilterShopItemResult:
				v = d.get("vnum", 0)
				if v and v not in seen:
					seen[v] = 1
					offlineshop.RequestAveragePrice(v)

	def OnWhisper(self, name):
		if self.interface:
			self.interface.OpenWhisperDialog(name)

	def OnToggleRow(self, data):
		itemID = data["id"]
		if itemID in self.selected:
			del self.selected[itemID]
			newState = False
		else:
			# capture owner+price+vnum AT SELECTION TIME so page flips can't zero the
			# total or the buy packet (fixes the old cross-page GetItemPrice()==0 bug).
			# keep the whole result dict too so the buy-dialog preview can build a full tooltip.
			self.selected[itemID] = {"owner": data["owner"], "price": data["price"], "vnum": data["vnum"], "data": data}
			newState = True
		self._RefreshTotal()
		return newState

	def _IsRowSelected(self, itemID):
		return itemID in self.selected

	def _SelectionTotal(self):
		total = 0
		for entry in self.selected.values():
			total += entry["price"]
		return total

	def _RefreshTotal(self):
		self.txtTotal.SetText(localeinfo.OFFLINESHOP_SEARCH_TOTAL_YANG % str(localeinfo.NumberToMoneyString(self._SelectionTotal())))

	def _ClearSelection(self):
		self.selected = {}
		self._RefreshTotal()

	def AskBuySelectedItems(self):
		if not self.selected:
			return
		entries = []
		for itemID, e in self.selected.items():
			entries.append({"id": itemID, "owner": e["owner"], "price": e["price"], "vnum": e["vnum"], "data": e.get("data")})
		self.dimmer.Show()
		# center the dialog over the search window (wherever it currently sits), not the screen
		px, py = self.GetGlobalPosition()
		cx = px + (WND_W - BuyDialog.DLG_W) / 2
		cy = py + (WND_H - BuyDialog.DLG_H) / 2
		self.buyDialog.Open(entries, ui.__mem_func__(self.OnConfirmBuy), cx, cy)

	def OnConfirmBuy(self, entries):
		for e in entries:
			offlineshop.SendBuyItemFromSearch(e["owner"], e["id"], e["price"])
		# rows vanish + store entries drop as the server confirms each buy
		# (SearchFilter_BuyFromSearch), so nothing else to clean here.

	def OnBuyDialogClosed(self):
		self.dimmer.Hide()

	def SearchFilter_BuyFromSearch(self, ownerid, itemid):
		self.ItemList.RemoveItemBought(ownerid, itemid)
		for d in self.SearchFilterShopItemResult:
			if d.get("id") == itemid and d.get("owner") == ownerid:
				self.SearchFilterShopItemResult.remove(d)
				break
		if itemid in self.selected:
			del self.selected[itemid]
			self._RefreshTotal()

	# ---- pagination (server-driven; page echo in ShopFilterResult sets currentPage) ----
	def __RequestServerPage(self, page):
		pc = max(1, getattr(self, "pageCount", 1))
		page = max(1, min(page, pc))
		self.SearchFilterLastUsedSetting = self.GetSearchFilterSettings(self.sCategory, self.sSubCategory, page)
		offlineshop.SendFilterRequest(*self.SearchFilterLastUsedSetting)

	def GotoPage(self, page):
		if app.USE_OFFLINESHOP_SEARCH_PAGINATION:
			self.__RequestServerPage(page)
		else:
			self.currentPage = page
			self.RefreshList()

	def FirstPage(self):	self.GotoPage(1)
	def LastPage(self):		self.GotoPage(getattr(self, "pageCount", 1))
	def NextPage(self):		self.GotoPage(self.currentPage + 1)
	def PrevPage(self):		self.GotoPage(self.currentPage - 1)

	def RefreshPaginationButtons(self):
		group = (self.currentPage - 1) // 5			# which 5-page window
		shown = min(self.pageCount - group * 5, 5)
		for i in xrange(5):
			pageNo = group * 5 + i + 1
			b = self.pageButtons[i]
			b.SetUp()
			b.Enable()
			b.SetText("%d" % pageNo)
			b.SetEvent(ui.__mem_func__(self.GotoPage), pageNo)
			if i < shown:
				b.Show()
			else:
				b.Hide()
		active = self.currentPage - group * 5 - 1
		self.pageButtons[active].Down()
		self.pageButtons[active].Disable()
		# grouped '<< < [pages] > >>' laid out from a fixed right edge (mirrored under AR)
		STEP = 34
		order = [self.btnFirstPage, self.btnPrevPage] + [self.pageButtons[i] for i in xrange(shown)] + [self.btnNextPage, self.btnLastPage]
		if IS_AR:
			order.reverse()
		x = LIST_W - 8 - STEP * len(order)
		if IS_AR:
			x = 8
		for b in order:
			b.SetPosition(x, 5)
			x += STEP

	def Recv_PriceAverage(self, vnum, price):
		self.priceAvgCache[vnum] = price

	def SearchByOwnerName(self, ownerName):
		if len(ownerName) < 1 or self._CooldownBlocked():
			return
		self._ArmCooldown()
		if not self.IsShow():
			self.LoadWindow()
			self.SetCenterPosition()
			ui.ScriptWindow.Show(self)
		self.CategoryList.ResetSelection()
		self.chkPlayerName.IsChecked = True
		self.chkPlayerName.LoadImage(PATH_OLD + "box_checked.png")
		self.searchInput.SetText(ownerName)
		self.OnSearchByValue(0, 0, True, True)
		self.searchInput.SetText("")
		self.searchHint.SetText("")
		self.searchInput.KillFocus()

	def SearchByName(self, itemName):
		if len(itemName) < 1 or self._CooldownBlocked():
			return
		self._ArmCooldown()
		if not self.IsShow():
			self.LoadWindow()
			self.SetCenterPosition()
			ui.ScriptWindow.Show(self)
		self.CategoryList.ResetSelection()
		self.chkPlayerName.IsChecked = False
		self.chkPlayerName.LoadImage(PATH_OLD + "box_uncheck.png")
		self.searchInput.SetText(itemName)
		self.OnSearchByValue(0, 0, True, True)
		self.searchInput.SetText("")
		self.searchHint.SetText("")
		self.searchInput.KillFocus()
