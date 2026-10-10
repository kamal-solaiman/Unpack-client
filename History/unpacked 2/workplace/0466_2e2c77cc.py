# coding: latin_1
# World Boss V2 — Live Damage Meter HUD
# Gated by app.ENABLE_WORLDBOSS_V2_DAMAGE_METER on the client side.

import ui
import wndMgr
import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import uiworldboss
import localeinfo

HUD_WIDTH = 290
HUD_HEIGHT = 236

ROW_H = 22
ROW_START_Y = 58
GAUGE_WIDTH = 140
GAUGE_X = 80
NAME_X = 26
DAMAGE_X = HUD_WIDTH - 50
ESCROW_Y = ROW_START_Y + 5 * ROW_H + 8 + ROW_H + 8


STALE_TIMEOUT_SEC = 8

COLOR_NEUTRAL = 0xFFDDDDDD
COLOR_ME = 0xFFDBA54E
COLOR_DIM = 0xFFB1AA8C


def _FormatDamage(dmg):
	if dmg >= 1000000000:
		return "%.1fB" % (dmg / 1000000000.0)
	if dmg >= 1000000:
		return "%.1fM" % (dmg / 1000000.0)
	if dmg >= 1000:
		return "%.1fK" % (dmg / 1000.0)
	return str(int(dmg))


def _FormatElapsed(sec):
	if sec < 0:
		sec = 0
	m = sec / 60
	s = sec % 60
	return "%d:%02d" % (m, s)


def _BossName(vnum):
	try:
		return uiworldboss.BOSS_NAMES.get(int(vnum), "Boss %d" % int(vnum))
	except:
		return "Boss %s" % str(vnum)


class _MeterRow(ui.Window):
	def __init__(self, parent, index):
		ui.Window.__init__(self)
		self.SetParent(parent)
		self.AddFlag("not_pick")
		self.SetSize(HUD_WIDTH, ROW_H)

		self.index = index
		self.isMe = False

		self.rankText = ui.TextLine()
		self.rankText.SetParent(self)
		self.rankText.SetPosition(8, 3)
		self.rankText.SetHorizontalAlignRight()
		self.rankText.SetText("")
		self.rankText.Show()

		self.nameText = ui.TextLine()
		self.nameText.SetParent(self)
		self.nameText.SetPosition(NAME_X, 3)
		self.nameText.SetHorizontalAlignRight()
		self.nameText.SetText("")
		self.nameText.Show()

		self.gauge = ui.Gauge()
		self.gauge.SetParent(self)
		self.gauge.AddFlag("not_pick")
		self.gauge.MakeGauge(GAUGE_WIDTH, "red")
		self.gauge.SetPosition(GAUGE_X, 6)
		self.gauge.Hide()

		self.dmgText = ui.TextLine()
		self.dmgText.SetParent(self)
		self.dmgText.SetHorizontalAlignRight()
		self.dmgText.SetPosition(DAMAGE_X, 3)
		self.dmgText.SetText("")
		self.dmgText.Show()

	def Clear(self):
		self.rankText.SetText("")
		self.nameText.SetText("")
		self.dmgText.SetText("")
		self.gauge.Hide()
		self.isMe = False

	def SetData(self, rank, name, damage, top1Damage, isMe):
		self.isMe = isMe
		color = COLOR_ME if isMe else COLOR_NEUTRAL

		self.rankText.SetText("%d." % rank)
		self.rankText.SetPackedFontColor(color)
		self.nameText.SetText(name)
		self.nameText.SetPackedFontColor(color)
		self.dmgText.SetText(_FormatDamage(damage))
		self.dmgText.SetPackedFontColor(color)

		if top1Damage > 0:
			self.gauge.SetPercentage(damage, top1Damage)
		else:
			self.gauge.SetPercentage(0, 1)
		self.gauge.Show()


class WorldBossDamageMeter(ui.ThinBoard):
	def __init__(self):
		ui.ThinBoard.__init__(self)
		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetSize(HUD_WIDTH, HUD_HEIGHT)


		x = wndMgr.GetScreenWidth() - HUD_WIDTH - 180
		y = 100
		self.SetPosition(x, y)
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - HUD_WIDTH - 180, 100)})

		self.currentBossVnum = 0

		self.bossNameText = ui.TextLine()
		self.bossNameText.SetParent(self)
		self.bossNameText.SetPosition(HUD_WIDTH / 2, 10)
		self.bossNameText.SetPackedFontColor(COLOR_ME)
		self.bossNameText.SetHorizontalAlignCenter()
		self.bossNameText.SetText("")
		self.bossNameText.Show()

		self.elapsedText = ui.TextLine()
		self.elapsedText.SetParent(self)
		self.elapsedText.SetHorizontalAlignRight()
		self.elapsedText.SetPosition(HUD_WIDTH - 40, 10)
		self.elapsedText.SetPackedFontColor(COLOR_DIM)
		self.elapsedText.SetText("")
		self.elapsedText.Show()

		self.moreBossesText = ui.TextLine()
		self.moreBossesText.SetParent(self)
		self.moreBossesText.SetPosition(HUD_WIDTH / 2, 30)
		self.moreBossesText.SetPackedFontColor(COLOR_DIM)
		self.moreBossesText.SetHorizontalAlignCenter()
		self.moreBossesText.SetText("")
		self.moreBossesText.Show()

		self.rows = []
		for i in xrange(5):
			row = _MeterRow(self, i)
			row.SetPosition(0, ROW_START_Y + i * ROW_H)
			row.Show()
			self.rows.append(row)

		self.selfRow = _MeterRow(self, 5)
		self.selfRow.SetPosition(0, ROW_START_Y + 5 * ROW_H + 8)
		self.selfRow.Hide()

		if getattr(app, "ENABLE_WORLDBOSS_V3", 0):
			self.escrowLine = ui.TextLine()
			self.escrowLine.SetParent(self)
			self.escrowLine.SetPosition(HUD_WIDTH / 2, ESCROW_Y)
			self.escrowLine.SetPackedFontColor(COLOR_DIM)
			self.escrowLine.SetHorizontalAlignCenter()
			self.escrowLine.SetText("")
			self.escrowLine.Show()
		else:
			self.escrowLine = None

		self.lastUpdateTime = 0

		self.Hide()

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def Destroy(self):
		self.rows = []
		self.selfRow = None
		self.escrowLine = None
		self.Hide()

	def Close(self):
		self.currentBossVnum = 0
		self.lastUpdateTime = 0
		for row in self.rows:
			row.Clear()
		if self.selfRow:
			self.selfRow.Clear()
			self.selfRow.Hide()
		if self.escrowLine:
			self.escrowLine.SetText("")
		self.Hide()

	def OnUpdate(self):
		# Auto-hide if server stops broadcasting (teleport off boss map, disconnect,
		# player switched focus to another boss on the same map, boss despawned etc.)
		if not self.IsShow() or self.lastUpdateTime == 0:
			return
		if app.GetGlobalTimeStamp() - self.lastUpdateTime > STALE_TIMEOUT_SEC:
			self.Close()

	def IsShowingBoss(self, bossVnum):
		return self.IsShow() and int(self.currentBossVnum) == int(bossVnum)

	def Update(self, bossVnum, elapsed, participants, aliveCount, myDmg, myRank, topList):
		# topList: list of (name, damage, isMe) tuples, already ordered by damage
		self.currentBossVnum = int(bossVnum)
		self.lastUpdateTime = app.GetGlobalTimeStamp()

		self.bossNameText.SetText(_BossName(bossVnum))
		self.elapsedText.SetText(_FormatElapsed(int(elapsed)))

		if int(aliveCount) > 1:
			extra = int(aliveCount) - 1
			self.moreBossesText.SetText(localeinfo.WB_MOREBOSS_ALIVE % extra if extra == 1 else localeinfo.WB_MOREBOSSES_ALIVE % extra)
		else:
			self.moreBossesText.SetText("")

		top1Damage = topList[0][1] if topList else 0
		meInTop = False

		for i, row in enumerate(self.rows):
			if i < len(topList):
				name, dmg, isMe = topList[i]
				row.SetData(i + 1, name, dmg, top1Damage, bool(isMe))
				if isMe:
					meInTop = True
			else:
				row.Clear()

		if not meInTop and int(myRank) > 0:
			self.selfRow.SetData(int(myRank), localeinfo.WB_YOU, int(myDmg), top1Damage, True)
			self.selfRow.Show()
		else:
			self.selfRow.Clear()
			self.selfRow.Hide()

		if not self.IsShow():
			self.Show()

	if getattr(app, "ENABLE_WORLDBOSS_V3", 0):
		def OnWBEscrow(self, coins, bounty):
			if not self.escrowLine:
				return

			coins = int(coins)
			bounty = int(bounty)
			text = getattr(localeinfo, "WB_ESCROW_INFO", "Escrow: %s coins (+%s bounty) - paid when the boss dies")
			self.escrowLine.SetText(text % (coins, bounty))
