# coding: latin_1
#
# Growth Mount wiki page: two-column section nav + banner header, then six
# system sections (overview / leveling / skills / skill training / items /
# good-to-know). Every number comes from uicompanionride.GetGrowthMountData()
# (the cl_growth_mount.json bake of the server's growth_mount.txt) or the
# uicompanionride constants -- no table in this module can drift from the
# ride page. Live rows read uicompanionride.LAST_STATUS (None until the
# first GC push) and the Companion window's full rideStatus tuple.

import app
import ui
import wndMgr
import item
import net
import localeinfo
import ingamewikidungeon
import uicompanionride

LocaleText = ingamewikidungeon.LocaleText

_ART = "d:/ymir work/ui/wiki/wiki_new/dungeons/"
_SKILL_ICON_FMT = "icon/item/item_mount/skill_%d.png"

# USE_ENCHANT_MOUNT_SKIN scrolls (1-day / 3-day), the mount twins of the pet
# page's 79771/79773 pair.
_MOUNT_SKIN_ENCHANT_ITEMS = (79770, 79772)

_COL_NAME = 0xffffffff
_COL_ITEM_TITLE = 0xffcabdab
_COL_DESC = 0xffa09080
_COL_LEVEL = 0xffffe6a0
_COL_OK = 0xff8ab98e
_COL_STOP = 0xffc98a8a
_COL_NAV = 0xffcabdab
_COL_NAV_HOVER = 0xffffe6a0

_STATUS_PREFETCHED = 0


def _Money(n):
	try:
		n = int(n)
	except (TypeError, ValueError):
		return str(n)
	s = str(n)
	out = ""
	while len(s) > 3:
		out = "," + s[-3:] + out
		s = s[:-3]
	return s + out


def _PrefetchStatus():
	# LAST_STATUS fills from the GC push even with the Companion window
	# closed (the cache write precedes the board guard), so one silent
	# REQUEST_STATUS per session gives the page live rows without the
	# player ever opening the Ride tab.
	global _STATUS_PREFETCHED
	if _STATUS_PREFETCHED:
		return
	if uicompanionride.LAST_STATUS is not None:
		_STATUS_PREFETCHED = 1
		return
	try:
		if hasattr(net, "SendGrowthMountPacket") and hasattr(net, "GROWTH_MOUNT_CG_REQUEST_STATUS"):
			net.SendGrowthMountPacket(net.GROWTH_MOUNT_CG_REQUEST_STATUS, 0)
			_STATUS_PREFETCHED = 1
	except Exception:
		pass


def _LastStatus():
	ls = uicompanionride.LAST_STATUS
	if ls and len(ls) >= 3:
		return ls
	return None


def _RideStatus():
	try:
		import systemSetting
		wnd = getattr(systemSetting.GetInterfaceHandler(), "wndCompanion", None)
		rs = getattr(wnd, "rideStatus", None)
		if rs and len(rs) >= 10:
			return rs
	except Exception:
		pass
	return None


def _SkillLevelMax():
	return getattr(uicompanionride, "RIDE_SKILL_LEVEL_MAX", len(uicompanionride.RIDE_SKILL_PCT) - 1)


def _MountSkinVnums():
	# Single source with the Costumes > Mount sidebar category.
	try:
		import ingamewikiconfig
		vnums = tuple(v for v in ingamewikiconfig.COSTUME_MOUNT_VNUMS if isinstance(v, int))
		if vnums:
			return vnums
	except Exception:
		pass
	return (72902, 72903)


class _NavRow(ui.Window):
	# Click/hover catcher (growthpet clone): plain pickable Window, no
	# "attach" -- FLAG_ATTACH would send the button events to GetRoot()
	# and clicks would die silently.
	def __init__(self):
		ui.Window.__init__(self)
		self.navText = None
		self.navEvent = None
		self.navKey = None

	def SetNav(self, textLine, event, key):
		self.navText = textLine
		self.navEvent = event
		self.navKey = key

	def OnMouseOverIn(self):
		t = getattr(self, "navText", None)
		if t:
			t.SetPackedFontColor(_COL_NAV_HOVER)

	def OnMouseOverOut(self):
		t = getattr(self, "navText", None)
		if t:
			t.SetPackedFontColor(_COL_NAV)

	def OnMouseLeftButtonDown(self):
		ev = getattr(self, "navEvent", None)
		if ev:
			ev(self.navKey)
		return True


class WikiGrowthMountWindow(ingamewikidungeon.WikiDungeonWindow):

	_NAV_ROW_CENTERS = (21, 57, 93)
	_TBL_X0 = 40
	_TBL_W = 476
	_TBL_HEADER_H = 24
	_SIG_POLL_INTERVAL = 0.5
	_MARQUEE_DELAY = 0.35
	_MARQUEE_SPEED = 40.0
	_MARQUEE_PAD = 4

	def OpenPage(self):
		self._ClearContent()
		self._sectionAnchors = {}
		self._trainIdx = getattr(self, "_trainIdx", 0)
		self._liveSigAtRender = self._LiveSig()
		self._lastSigPoll = 0.0
		self._marqueeItems = []
		self._marqueeHot = None
		self._marqueeOffset = 0.0
		self._marqueeDone = False
		self._marqueeSince = 0.0
		self._marqueeTime = 0.0
		self._swapRows = []
		self._swapPhase = -1
		_PrefetchStatus()

		y = 4
		y = self._RenderHeader(y)
		self._sectionAnchors["overview"] = y
		y = self._RenderOverview(y)
		self._sectionAnchors["leveling"] = y
		y = self._RenderLeveling(y)
		self._sectionAnchors["skills"] = y
		y = self._RenderSkills(y)
		self._sectionAnchors["training"] = y
		y = self._RenderTraining(y)
		self._sectionAnchors["items"] = y
		y = self._RenderItems(y)
		self._sectionAnchors["rules"] = y
		y = self._RenderRules(y)

		deco = self._Img(_ART + "page_end_deco.png", 0, y)
		self._FitWide(deco)
		y += 19 + 8

		self.scrollBoard.SetSize(self.peekWindow.GetWidth(), max(y, self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, 0)
		self.ChangeScrollbar()
		self.Show()

	def _FitWide(self, img):
		w = img.GetWidth() or 1
		pw = self.peekWindow.GetWidth()
		if w > pw:
			s = float(pw) / w
			img.SetScale(s, s)

	def _RTL(self):
		try:
			return localeinfo.IsARABIC()
		except:
			return 0

	# -- live-state signature gate ------------------------------------------

	def _LiveSig(self):
		parts = []
		ls = _LastStatus()
		if ls:
			try:
				parts.append((int(ls[0]), int(ls[1]), tuple(ls[2])))
			except Exception:
				pass
		rs = _RideStatus()
		if rs:
			try:
				parts.append((int(rs[2]), int(rs[3]), tuple(rs[6]), tuple(rs[7])))
			except Exception:
				pass
		return tuple(parts)

	def OnUpdate(self):
		if not self.IsShow():
			return
		self._MarqueeTick()
		now = app.GetTime()

		rows = getattr(self, "_swapRows", None)
		if rows:
			phase = int(now)
			if phase != getattr(self, "_swapPhase", -1):
				self._swapPhase = phase
				for nameLine, entries in rows:
					idx = phase % len(entries)
					for i in xrange(len(entries)):
						if i == idx:
							entries[i][0].Show()
						else:
							entries[i][0].Hide()
					nameLine.SetText(entries[idx][1])

		if now - getattr(self, "_lastSigPoll", 0.0) < self._SIG_POLL_INTERVAL:
			return
		self._lastSigPoll = now
		sig = self._LiveSig()
		if sig == getattr(self, "_liveSigAtRender", sig):
			return
		pos = self.scrollBoard.GetLocalPosition()[1]
		self.OpenPage()
		span = self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()
		if span > 0 and pos < 0:
			self.scrollBoard.SetPosition(0, max(pos, -span))
			self.ChangeScrollbar()

	# -- header --------------------------------------------------------------

	def _RenderHeader(self, y):
		rtl = self._RTL()
		pw = self.peekWindow.GetWidth()
		leftX = 8
		rightX = pw - 200 - 8

		navCols = (
			(
				("overview", LocaleText("WIKI_MOUNT_NAV_OVERVIEW", "Overview")),
				("leveling", LocaleText("WIKI_MOUNT_NAV_LEVELING", "Leveling")),
				("skills", LocaleText("WIKI_MOUNT_NAV_SKILLS", "Skills")),
			),
			(
				("training", LocaleText("WIKI_MOUNT_NAV_TRAINING", "Skill Training")),
				("items", LocaleText("WIKI_MOUNT_NAV_ITEMS", "Items")),
				("rules", LocaleText("WIKI_MOUNT_NAV_RULES", "Good to Know")),
			),
		)
		for ci in xrange(2):
			navX = (leftX, rightX)[(1 - ci) if rtl else ci]
			labelX = (navX + 152) if rtl else (navX + 48)
			self._Img(_ART + "title_list_3.png", navX, y + 2)
			for i in xrange(len(navCols[ci])):
				key, label = navCols[ci][i]
				rowCy = y + 2 + self._NAV_ROW_CENTERS[i]
				t = self._Text(label, labelX, rowCy - 8, _COL_NAV)
				row = _NavRow()
				row.SetParent(self.scrollBoard)
				row.SetSize(200, 30)
				row.SetPosition(navX, rowCy - 15)
				row.SetNav(t, ui.__mem_func__(self._OnNavClick), key)
				row.Show()
				self.elements.append(row)

		gap = rightX - (leftX + 200)
		scale = min(0.62, float(gap - 8) / 204.0)
		banner = self._Img(_ART + "banners/6.png", 0, y)
		banner.SetScale(scale, scale)
		bw = int(204 * scale)
		bh = int(133 * scale)
		banner.SetPosition((pw - bw) / 2, y + 2 + (127 - bh) / 2)

		deco = self._Img(_ART + "page_title_deco.png", 0, y + 133)
		self._FitWide(deco)
		return y + 133 + 20 + 8

	def _OnNavClick(self, key):
		anchors = getattr(self, "_sectionAnchors", None) or {}
		target = anchors.get(key)
		if target is None:
			return
		span = self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()
		if span <= 0:
			return
		self.scrollBoard.SetPosition(0, -min(max(int(target) - 6, 0), span))
		self.ChangeScrollbar()

	# -- shared bits ---------------------------------------------------------

	def _SectionTitle(self, y, label):
		self._Img(_ART + "subtitle.png", (556 - 495) / 2, y)
		self._Text(label, 447 if self._RTL() else 108, y + 11, _COL_NAME)
		return y + 48

	def _TableGrid(self, x0, top, w, seq, colX, colW, rowBounds):
		tableH = rowBounds[-1] - top
		for li in seq[:-1]:
			self._Bar(colX[li] + colW[li], top, 1, tableH, self._COL_TABLE_BORDER)
		self._Bar(x0, top, w, 1, self._COL_TABLE_BORDER)
		self._Bar(x0, top + self._TBL_HEADER_H, w, 1, self._COL_TABLE_BORDER)
		for by in rowBounds:
			self._Bar(x0, by, w, 1, self._COL_TABLE_BORDER)
		self._Bar(x0, top, 1, tableH, self._COL_TABLE_BORDER)
		self._Bar(x0 + w - 1, top, 1, tableH, self._COL_TABLE_BORDER)

	def _TableLayout(self, widths, order):
		seq = tuple(reversed(order)) if self._RTL() else tuple(order)
		colX = {}
		x = self._TBL_X0
		for li in seq:
			colX[li] = x
			x += widths[li]
		return seq, colX

	def _TableHeader(self, top, seq, colX, widths, headers):
		self._Bar(self._TBL_X0, top, self._TBL_W, self._TBL_HEADER_H, self._COL_TABLE_HEADER_BG)
		for li in seq:
			self._CellText(headers[li], colX[li], widths[li], top + 6, ingamewikidungeon._COL_TAN)

	def _CellText(self, s, cellX, cellW, y, color, align="center"):
		# Marquee-aware cell text (growthpet clone): overflowing text anchors
		# at the reading edge and slides on hover inside a screen-space clip
		# rect re-applied each tick by _MarqueeTick.
		pad = self._MARQUEE_PAD
		rtl = self._RTL()
		if align == "center":
			t = self._Text(s, cellX + cellW / 2, y, color, align="center")
		else:
			t = self._Text(s, (cellX + cellW - pad) if rtl else (cellX + pad), y, color)
		if not s or not app.USE_CLIP_MASK:
			return t
		try:
			fullW = t.GetTextSize()[0]
		except Exception:
			return t
		viewW = cellW - pad * 2
		if fullW <= viewW:
			return t
		t.SetHorizontalAlignLeft()
		baseX = (cellX + cellW - pad) if rtl else (cellX + pad)
		t.SetPosition(int(baseX), int(y))
		self._marqueeItems.append({
			"obj": t,
			"baseX": int(baseX),
			"y": int(y),
			"boxX": int(cellX + pad),
			"viewW": int(viewW),
			"fullW": int(fullW),
			"rtl": rtl,
		})
		return t

	def _MarqueeTick(self):
		items = getattr(self, "_marqueeItems", None)
		if not items:
			return
		now = app.GetTime()
		dt = now - getattr(self, "_marqueeTime", 0.0)
		self._marqueeTime = now
		if dt <= 0.0 or dt > 0.5:
			dt = 0.0
		sbX, sbY = self.scrollBoard.GetGlobalPosition()
		pkX, pkY = self.peekWindow.GetGlobalPosition()
		pkR = pkX + self.peekWindow.GetWidth()
		pkB = pkY + self.peekWindow.GetHeight()
		mx, my = wndMgr.GetMousePosition()

		hot = None
		for e in items:
			bx = sbX + e["boxX"]
			by = sbY + e["y"] - 2
			if mx >= bx and mx < bx + e["viewW"] and my >= by and my < by + 18:
				hot = e
				break
		if hot is not getattr(self, "_marqueeHot", None):
			old = getattr(self, "_marqueeHot", None)
			if old is not None:
				old["obj"].SetPosition(old["baseX"], old["y"])
			self._marqueeHot = hot
			self._marqueeOffset = 0.0
			self._marqueeDone = False
			self._marqueeSince = now

		hot = self._marqueeHot
		if hot is not None and not self._marqueeDone and now - self._marqueeSince >= self._MARQUEE_DELAY:
			travel = hot["fullW"] - hot["viewW"]
			self._marqueeOffset += self._MARQUEE_SPEED * dt
			if self._marqueeOffset >= travel:
				self._marqueeOffset = float(travel)
				self._marqueeDone = True
			# Arabic text grows leftward from its anchor, so revealing the
			# hidden head means sliding the anchor the other way.
			if hot["rtl"]:
				hot["obj"].SetPosition(int(hot["baseX"] + self._marqueeOffset), hot["y"])
			else:
				hot["obj"].SetPosition(int(hot["baseX"] - self._marqueeOffset), hot["y"])

		for e in items:
			l = sbX + e["boxX"]
			r = l + e["viewW"]
			t = sbY + e["y"] - 2
			b = t + 18
			l = max(l, pkX)
			r = min(r, pkR)
			t = max(t, pkY)
			b = min(b, pkB)
			if r < l:
				r = l
			if b < t:
				b = t
			try:
				e["obj"].SetClippingMaskRect(int(l), int(t), int(r), int(b))
			except Exception:
				pass

	def _ItemEffectTable(self, top, rows):
		widths = (48, 150, 278)
		COL_ICON, COL_ITEM, COL_EFFECT = 0, 1, 2
		seq, colX = self._TableLayout(widths, (COL_ICON, COL_ITEM, COL_EFFECT))
		headers = (
			"",
			LocaleText("PET_UP_HELP_COL_ITEM", "Item"),
			LocaleText("WIKI_PET_COL_EFFECT", "Effect"),
		)
		self._TableHeader(top, seq, colX, widths, headers)
		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for vnum, effect in rows:
			rowH = 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			textY = rowY + rowH / 2 - 7
			iconX = colX[COL_ICON] + (widths[COL_ICON] - 32) / 2
			self._ItemIcon(vnum, iconX, rowY + (rowH - 32) / 2, cellW=32, cellH=32)
			self._CellText(self._ItemName(vnum), colX[COL_ITEM], widths[COL_ITEM], textY, ingamewikidungeon._COL_TAN)
			self._CellText(effect, colX[COL_EFFECT], widths[COL_EFFECT], textY, self._COL_TABLE_VALUE)
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)
		return rowY

	def _MatStrip(self, mats, colXv, colWv, rowY, rowH):
		mats = [m for m in (mats or []) if m and m[0]]
		if not mats:
			self._Text("-", colXv + colWv / 2, rowY + rowH / 2 - 7, self._COL_TABLE_VALUE, align="center")
			return
		pitch = 34
		startX = colXv + (colWv - len(mats) * pitch) / 2 + 1
		iconY = rowY + (rowH - 32) / 2
		for i in xrange(len(mats)):
			try:
				cnt = int(mats[i][1])
			except (TypeError, ValueError, IndexError):
				cnt = 0
			self._ItemIcon(mats[i][0], startX + i * pitch, iconY, cnt, cellW=32, cellH=32)

	def _ItemName(self, vnum):
		try:
			item.SelectItem(vnum)
			name = item.GetItemName()
			if name:
				return name
		except Exception:
			pass
		return str(vnum)

	def _SkillIcon(self, idx, x, y):
		img = self._Img(_SKILL_ICON_FMT % (idx + 1), x, y)
		w = img.GetWidth() or 32
		if w != 32:
			s = 32.0 / w
			img.SetScale(s, s)
		return img

	# -- Overview ------------------------------------------------------------

	def _RenderOverview(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_MOUNT_NAV_OVERVIEW", "Overview"))
		rtl = self._RTL()
		pw = self.peekWindow.GetWidth()
		circleX = (pw - 44 - 48) if rtl else 44
		textX = (circleX - 8) if rtl else 116

		data = uicompanionride.GetGrowthMountData()
		medals = tuple(int(p[0]) for p in (data.get("expItems") or []) if p and p[0])
		stones = tuple(self._SkillUnlockers(data))
		rows = []
		if medals:
			rows.append((medals, LocaleText("WIKI_MOUNT_OV_FEED", "Feed these medals to fill the EXP bar - see Leveling")))
		if stones:
			rows.append((stones, LocaleText("WIKI_MOUNT_OV_STONE", "Horse Stones teach the 4 passive skills - see Skill Training")))
		rows.append((_MountSkinVnums(), LocaleText("WIKI_MOUNT_SKIN_DESC", "Changes your mount's look + its own bonus")))
		rows.append((_MOUNT_SKIN_ENCHANT_ITEMS, LocaleText("WIKI_MOUNT_SKIN_ENCH_DESC", "Enchants a mount skin with extra timed bonuses")))
		rowY = top
		for vnums, desc in rows:
			circle = self._Img(_ART + "itemcircle1.png", circleX, rowY)
			circle.SetScale(0.68, 0.68)
			entries = []
			for vnum in vnums:
				icon = self._ItemIcon(vnum, circleX + 8, rowY + 10, cellW=32, cellH=32)
				entries.append((icon, self._ItemName(vnum)))
			nameLine = self._Text(entries[0][1], textX, rowY + 8, _COL_ITEM_TITLE)
			self._Text(desc, textX, rowY + 26, _COL_DESC)
			if len(entries) > 1:
				for e in entries[1:]:
					e[0].Hide()
				self._swapRows.append((nameLine, entries))
			rowY += 58

		rowY += 6
		rowY = self._RuleTable(rowY, (
			("WIKI_MOUNT_RULE1_A", "Your horse and mount are one companion - every character"),
			("WIKI_MOUNT_RULE1_B", "owns it from the start, no taming or buying needed."),
			("WIKI_MOUNT_RULE2_A", "Open the Companion window (P), Ride tab, to feed your"),
			("WIKI_MOUNT_RULE2_B", "mount, level it up and train its skills."),
			("WIKI_MOUNT_RULE3_A", "Feeding, level-ups and skill training only work while"),
			("WIKI_MOUNT_RULE3_B", "the mount is summoned or you are riding it."),
		))

		maxLv = uicompanionride.RIDE_LEVEL_MAX
		ls = _LastStatus()
		rs = _RideStatus()
		line = None
		if rs:
			try:
				if int(rs[3]):
					line = LocaleText("WIKI_MOUNT_LIVE_FMT", "Your horse: Lv. %s/%s - EXP %s/%s") % (
						int(rs[1]), maxLv, int(rs[2]), int(rs[3]))
				else:
					line = LocaleText("WIKI_MOUNT_LIVE_MAX_FMT", "Your horse: Lv. %s/%s - maximum level!") % (
						int(rs[1]), maxLv)
			except Exception:
				line = None
		if line is None and ls:
			try:
				line = LocaleText("WIKI_MOUNT_LIVE_LV_FMT", "Your horse: Lv. %s/%s") % (int(ls[1]), maxLv)
			except Exception:
				line = None
		if line is not None:
			rowY += 6
			self._Bar(self._TBL_X0, rowY, self._TBL_W, 26, self._COL_TABLE_HEADER_BG)
			self._CellText(line, self._TBL_X0, self._TBL_W, rowY + 6, _COL_LEVEL)
			rowY += 26
			status = rs or ls
			if status is not None and not int(status[0]):
				self._Text(LocaleText("GROWTH_MOUNT_CALL_PROMPT", "Summon your mount to manage it."),
					(pw - 46) if rtl else 46, rowY + 4, _COL_STOP)
				rowY += 21

		return rowY + 12

	def _SkillUnlockers(self, data):
		# The materials that appear only on a skill's first level are its
		# unlocker stones; the bake is the single source, so a config retune
		# reshuffles this list by itself.
		out = []
		skills = data.get("skills") or []
		for idx in xrange(len(skills)):
			per = skills[idx]
			l2v = {}
			for m in (per.get(2) or {}).get("mats") or []:
				if m and m[0]:
					l2v[int(m[0])] = 1
			for m in (per.get(1) or {}).get("mats") or []:
				v = m and int(m[0]) or 0
				if v and v not in l2v and v not in out:
					out.append(v)
		return out

	# -- Leveling ------------------------------------------------------------

	def _RenderLeveling(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_MOUNT_NAV_LEVELING", "Leveling"))

		data = uicompanionride.GetGrowthMountData()
		expFmt = LocaleText("GROWTH_MOUNT_HELP_EXP_FMT", "+%d EXP")

		self._Text(LocaleText("WIKI_MOUNT_FEED_TITLE", "EXP Items"), self._TBL_X0 + self._TBL_W / 2, top, _COL_ITEM_TITLE, align="center")
		top += 20
		feedRows = []
		for pair in data.get("expItems") or []:
			if pair and pair[0]:
				feedRows.append((int(pair[0]), expFmt % int(pair[1])))
		rowY = self._ItemEffectTable(top, feedRows) if feedRows else top

		rowY += 10
		rowY = self._RuleTable(rowY, (
			("WIKI_MOUNT_LV_RULE1_A", "Feeding past a full bar is refused - the medal is"),
			("WIKI_MOUNT_LV_RULE1_B", "never wasted."),
			("WIKI_MOUNT_LV_RULE2_A", "With a full bar the Upgrade button glows - leveling up"),
			("WIKI_MOUNT_LV_RULE2_B", "never fails, it only costs Yang and materials."),
			("WIKI_MOUNT_LV_RULE3_A", "Your riding skill and the horse's look follow the"),
			("WIKI_MOUNT_LV_RULE3_B", "mount level automatically."),
		)) + 10

		self._Text(LocaleText("WIKI_MOUNT_COST_TITLE", "Level-Up Costs"), self._TBL_X0 + self._TBL_W / 2, rowY, _COL_ITEM_TITLE, align="center")
		rowY += 20

		levelExp = data.get("levelExp") or {}
		levelCost = data.get("levelCost") or {}
		maxLv = uicompanionride.RIDE_LEVEL_MAX
		ls = _LastStatus()
		curLevel = ls and int(ls[1]) or 0

		widths = (56, 84, 252, 84)
		COL_TARGET, COL_EXP, COL_MATS, COL_YANG = 0, 1, 2, 3
		seq, colX = self._TableLayout(widths, (COL_TARGET, COL_EXP, COL_MATS, COL_YANG))
		headers = (
			LocaleText("WIKI_PET_COL_TARGET", "Level"),
			LocaleText("GROWTH_MOUNT_HELP_REQ_EXP", "EXP needed"),
			LocaleText("WIKI_PET_COL_MATS", "Materials"),
			LocaleText("PET_UP_HELP_YANG", "Yang"),
		)
		cTop = rowY
		self._TableHeader(cTop, seq, colX, widths, headers)

		totalYang = 0
		rowY = cTop + self._TBL_HEADER_H
		rowBounds = []
		for target in xrange(2, maxLv + 1):
			cost = levelCost.get(target) or {}
			mats = cost.get("mats") or []
			gold = int(cost.get("gold") or 0)
			exp = int(levelExp.get(target - 1) or 0)
			totalYang += gold
			rowH = 36 if mats else 26
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			if curLevel and target == curLevel + 1:
				self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, 0x1effe6a0)
			textY = rowY + rowH / 2 - 7
			self._Text(str(target), colX[COL_TARGET] + widths[COL_TARGET] / 2, textY, _COL_LEVEL, align="center")
			self._Text(_Money(exp), colX[COL_EXP] + widths[COL_EXP] / 2, textY, self._COL_TABLE_VALUE, align="center")
			self._MatStrip(mats, colX[COL_MATS], widths[COL_MATS], rowY, rowH)
			self._Text(_Money(gold), colX[COL_YANG] + widths[COL_YANG] / 2, textY, self._COL_TABLE_VALUE, align="center")
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, cTop, self._TBL_W, seq, colX, widths, rowBounds)

		rowY += 8
		if totalYang:
			totalFmt = LocaleText("WIKI_MOUNT_TOTAL_FMT", "Total from level 1 to %s: %s Yang")
			rowY = self._RuleTableRows(rowY, [[totalFmt % (maxLv, _Money(totalYang))]])

		return rowY + 12

	# -- Skills --------------------------------------------------------------

	def _RenderSkills(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_MOUNT_NAV_SKILLS", "Skills"))

		top = self._RuleTable(top, (
			("WIKI_MOUNT_SK_RULE1_A", "The four skills are permanent passive bonuses - they"),
			("WIKI_MOUNT_SK_RULE1_B", "work even while you are not riding."),
			("WIKI_MOUNT_SK_RULE2_A", "Each skill unlocks at the shown mount level; all four"),
			("WIKI_MOUNT_SK_RULE2_B", "share the same bonus curve below."),
		)) + 8

		unlockLevels = uicompanionride.RIDE_SKILL_UNLOCK_LEVEL
		skillMax = _SkillLevelMax()
		lvFmt = LocaleText("WIKI_PET_COL_LVMAX_FMT", "Lv %s")
		ls = _LastStatus()

		widths = (48, 190, 110, 128)
		COL_ICON, COL_SKILL, COL_UNLOCK, COL_MY = 0, 1, 2, 3
		seq, colX = self._TableLayout(widths, (COL_ICON, COL_SKILL, COL_UNLOCK, COL_MY))
		headers = (
			"",
			LocaleText("WIKI_PET_COL_SKILL", "Skill"),
			LocaleText("WIKI_MOUNT_COL_UNLOCK", "Unlocks at"),
			LocaleText("WIKI_MOUNT_COL_MY", "Your Horse"),
		)
		self._TableHeader(top, seq, colX, widths, headers)

		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for idx in xrange(len(unlockLevels)):
			rowH = 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			textY = rowY + rowH / 2 - 7
			iconX = colX[COL_ICON] + (widths[COL_ICON] - 32) / 2
			self._SkillIcon(idx, iconX, rowY + (rowH - 32) / 2)
			myLevel = None
			if ls:
				try:
					myLevel = int(ls[2][idx])
				except Exception:
					myLevel = None
			nameColor = _COL_OK if myLevel else ingamewikidungeon._COL_TAN
			self._CellText(uicompanionride.RideSkillLabel(idx), colX[COL_SKILL], widths[COL_SKILL], textY, nameColor)
			self._CellText(lvFmt % unlockLevels[idx], colX[COL_UNLOCK], widths[COL_UNLOCK], textY, self._COL_TABLE_VALUE)
			if myLevel is None:
				myText, myColor = "-", self._COL_TABLE_VALUE
			else:
				myText = "%d / %d" % (myLevel, skillMax)
				myColor = _COL_LEVEL if myLevel else self._COL_TABLE_VALUE
			self._Text(myText, colX[COL_MY] + widths[COL_MY] / 2, textY, myColor, align="center")
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)

		rowY += 14
		self._Text(LocaleText("WIKI_MOUNT_CURVE_TITLE", "Bonus per skill level"), self._TBL_X0 + self._TBL_W / 2, rowY, _COL_ITEM_TITLE, align="center")
		rowY += 20

		pct = uicompanionride.RIDE_SKILL_PCT
		cols = skillMax
		base = self._TBL_W / cols
		widths = tuple([base] * (cols - 1) + [self._TBL_W - base * (cols - 1)])
		order = tuple(xrange(cols))
		seq, colX = self._TableLayout(widths, order)
		headers = tuple(lvFmt % (i + 1) for i in xrange(cols))
		cTop = rowY
		self._TableHeader(cTop, seq, colX, widths, headers)
		rowY = cTop + self._TBL_HEADER_H
		rowH = 26
		self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
		textY = rowY + rowH / 2 - 7
		for i in xrange(cols):
			try:
				val = "+%d%%" % int(pct[i + 1])
			except (IndexError, TypeError, ValueError):
				val = "-"
			self._Text(val, colX[i] + widths[i] / 2, textY, _COL_OK, align="center")
		rowY += rowH
		self._TableGrid(self._TBL_X0, cTop, self._TBL_W, seq, colX, widths, [rowY])

		return rowY + 12

	# -- Skill Training ------------------------------------------------------

	def _RenderTraining(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_MOUNT_NAV_TRAINING", "Skill Training"))

		top = self._RuleTable(top, (
			("WIKI_MOUNT_TR_RULE1_A", "Skills must be trained in order - the previous skill"),
			("WIKI_MOUNT_TR_RULE1_B", "needs at least level 1 first."),
			("WIKI_MOUNT_TR_RULE2_A", "A failed attempt consumes the materials - after 2 fails"),
			("WIKI_MOUNT_TR_RULE2_B", "the 3rd attempt always succeeds."),
		)) + 10

		data = uicompanionride.GetGrowthMountData()
		skills = data.get("skills") or []
		count = len(skills) or 4
		sel = max(0, min(count - 1, getattr(self, "_trainIdx", 0)))
		self._trainIdx = sel

		rtl = self._RTL()
		pitch = 56
		stripW = count * pitch - (pitch - 32)
		startX = self._TBL_X0 + (self._TBL_W - stripW) / 2
		for idx in xrange(count):
			vis = (count - 1 - idx) if rtl else idx
			x = startX + vis * pitch
			self._SkillIcon(idx, x, top)
			if idx == sel:
				self._Bar(x, top + 34, 32, 2, _COL_LEVEL)
			row = _NavRow()
			row.SetParent(self.scrollBoard)
			row.SetSize(40, 40)
			row.SetPosition(x - 4, top - 4)
			row.SetNav(None, ui.__mem_func__(self._OnTrainClick), idx)
			row.Show()
			self.elements.append(row)
		top += 44
		self._Text(uicompanionride.RideSkillLabel(sel), self._TBL_X0 + self._TBL_W / 2, top, _COL_ITEM_TITLE, align="center")
		top += 20

		perLevel = skills[sel] if sel < len(skills) else {}
		skillMax = _SkillLevelMax()
		ls = _LastStatus()
		curSkill = None
		if ls:
			try:
				curSkill = int(ls[2][sel])
			except Exception:
				curSkill = None

		widths = (56, 90, 330)
		COL_TARGET, COL_CHANCE, COL_MATS = 0, 1, 2
		seq, colX = self._TableLayout(widths, (COL_TARGET, COL_CHANCE, COL_MATS))
		headers = (
			LocaleText("WIKI_PET_COL_TARGET", "Level"),
			LocaleText("WIKI_PET_COL_CHANCE", "Success"),
			LocaleText("WIKI_PET_COL_MATS", "Materials"),
		)
		self._TableHeader(top, seq, colX, widths, headers)

		rowY = top + self._TBL_HEADER_H
		rowBounds = []
		for target in xrange(1, skillMax + 1):
			step = perLevel.get(target) or {}
			mats = step.get("mats") or []
			chance = int(step.get("chance") or 0)
			rowH = 36
			self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, self._COL_TABLE_ROW_BG)
			if curSkill is not None and target == curSkill + 1:
				self._Bar(self._TBL_X0, rowY, self._TBL_W, rowH, 0x1effe6a0)
			textY = rowY + rowH / 2 - 7
			self._Text(str(target), colX[COL_TARGET] + widths[COL_TARGET] / 2, textY, _COL_LEVEL, align="center")
			self._Text(("%d%%" % chance) if chance else "-", colX[COL_CHANCE] + widths[COL_CHANCE] / 2, textY,
				_COL_OK if chance >= 100 else self._COL_TABLE_VALUE, align="center")
			self._MatStrip(mats, colX[COL_MATS], widths[COL_MATS], rowY, rowH)
			rowY += rowH
			rowBounds.append(rowY)
		self._TableGrid(self._TBL_X0, top, self._TBL_W, seq, colX, widths, rowBounds)

		rowY += 8
		rs = _RideStatus()
		if rs:
			try:
				fails = int(rs[7][sel])
			except Exception:
				fails = 0
			if fails > 0:
				pityMax = getattr(uicompanionride, "RIDE_SKILL_PITY_MAX", 2)
				pityFmt = LocaleText("WIKI_MOUNT_TR_PITY_FMT", "%s: failed attempts %s/%s - the next one is guaranteed after %s.")
				self._Text(pityFmt % (uicompanionride.RideSkillLabel(sel), fails, pityMax, pityMax),
					(self.peekWindow.GetWidth() - 46) if rtl else 46, rowY, _COL_STOP)
				rowY += 17

		return rowY + 12

	def _OnTrainClick(self, idx):
		if idx == getattr(self, "_trainIdx", 0):
			return
		self._trainIdx = idx
		pos = self.scrollBoard.GetLocalPosition()[1]
		self.OpenPage()
		span = self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()
		if span > 0 and pos < 0:
			self.scrollBoard.SetPosition(0, max(pos, -span))
			self.ChangeScrollbar()

	# -- Items ---------------------------------------------------------------

	def _RenderItems(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_MOUNT_NAV_ITEMS", "Items"))

		data = uicompanionride.GetGrowthMountData()
		rows = []
		seen = {}
		expFmt = LocaleText("GROWTH_MOUNT_HELP_EXP_FMT", "+%d EXP")
		for pair in data.get("expItems") or []:
			if pair and pair[0]:
				v = int(pair[0])
				rows.append((v, expFmt % int(pair[1])))
				seen[v] = 1

		# Leveling materials (relic stones, horns, mithril) stay out of this
		# table by owner decision -- the Leveling cost table already shows
		# them with their exact levels and counts.
		stoneFmt = LocaleText("WIKI_MOUNT_IT_STONE_FMT", "Skill material - needed to learn: %s")
		skills = data.get("skills") or []
		for idx in xrange(len(skills)):
			l2v = {}
			for m in (skills[idx].get(2) or {}).get("mats") or []:
				if m and m[0]:
					l2v[int(m[0])] = 1
			for m in (skills[idx].get(1) or {}).get("mats") or []:
				v = m and int(m[0]) or 0
				if v and v not in l2v and v not in seen:
					rows.append((v, stoneFmt % uicompanionride.RideSkillLabel(idx)))
					seen[v] = 1

		rowY = self._ItemEffectTable(top, rows) if rows else top
		return rowY + 12

	# -- Good to Know --------------------------------------------------------

	def _RenderRules(self, y):
		top = self._SectionTitle(y, LocaleText("WIKI_MOUNT_NAV_RULES", "Good to Know"))

		rowY = self._RuleTable(top, (
			("WIKI_MOUNT_GK_RULE1_A", "Mount and mount-skin items on this server are permanent -"),
			("WIKI_MOUNT_GK_RULE1_B", "they never expire."),
			("WIKI_MOUNT_GK_RULE2_A", "Mount skins only change the look - browse them under"),
			("WIKI_MOUNT_GK_RULE2_B", "Costumes in the sidebar."),
			("WIKI_MOUNT_GK_RULE3_A", "Your riding skill level follows the mount level - the old"),
			("WIKI_MOUNT_GK_RULE3_B", "horse quests and survival feeding are gone."),
			("WIKI_MOUNT_GK_RULE4_A", "The horse cannot starve or die - there is no HP, stamina"),
			("WIKI_MOUNT_GK_RULE4_B", "or lifetime to manage."),
		))

		return rowY + 12
