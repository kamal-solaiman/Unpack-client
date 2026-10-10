# coding: latin_1
# Cursed Boss HUD - spots / qualification progress / live rank.
# Gated by app.ENABLE_CURSED_BOSS. Data arrives via the "CursedHud" server command.

import ui
import wndMgr
import app
import localeinfo

HUD_WIDTH = 230
HUD_HEIGHT = 126

STALE_TIMEOUT_SEC = 30

COLOR_TITLE = 0xFFFF6E79
COLOR_GOLD = 0xFFDBA54E
COLOR_DIM = 0xFFB1AA8C
COLOR_GOOD = 0xFF6AFF84
COLOR_DANGER = 0xFFFF6E79


def _FormatDamage(dmg):
	if dmg >= 1000000000:
		return "%.1fB" % (dmg / 1000000000.0)
	if dmg >= 1000000:
		return "%.1fM" % (dmg / 1000000.0)
	if dmg >= 1000:
		return "%.1fK" % (dmg / 1000.0)
	return str(int(dmg))


class CursedBossHud(ui.ThinBoard):

	def __init__(self):
		ui.ThinBoard.__init__(self, "UI", 2)
		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetSize(HUD_WIDTH, HUD_HEIGHT)
		self.SetPosition(wndMgr.GetScreenWidth() - HUD_WIDTH - 180, 100)

		self.coinIcon = ui.ImageBox()
		self.coinIcon.SetParent(self)
		self.coinIcon.AddFlag("not_pick")
		self.coinIcon.LoadImage("icon/item/44722.png")
		self.coinIcon.SetPosition(10, 8)
		self.coinIcon.Show()

		self.titleText = ui.TextLine()
		self.titleText.SetParent(self)
		self.titleText.SetPosition(HUD_WIDTH / 2 + 8, 14)
		self.titleText.SetHorizontalAlignCenter()
		self.titleText.SetPackedFontColor(COLOR_TITLE)
		self.titleText.SetText(getattr(localeinfo, "CURSED_HUD_TITLE", "CURSED BOSS"))
		self.titleText.Show()

		self.spotsLabel = ui.TextLine()
		self.spotsLabel.SetParent(self)
		self.spotsLabel.SetPosition(HUD_WIDTH - 16, 40)
		self.spotsLabel.SetHorizontalAlignRight()
		self.spotsLabel.SetPackedFontColor(COLOR_DIM)
		self.spotsLabel.SetText(getattr(localeinfo, "CURSED_HUD_SPOTS", "Coin spots left"))
		self.spotsLabel.Show()

		self.spotsValue = ui.TextLine()
		self.spotsValue.SetParent(self)
		self.spotsValue.SetPosition(16, 40)
		self.spotsValue.SetPackedFontColor(COLOR_GOLD)
		self.spotsValue.SetText("")
		self.spotsValue.Show()

		self.gauge = ui.Gauge()
		self.gauge.SetParent(self)
		self.gauge.AddFlag("not_pick")
		self.gauge.MakeGauge(HUD_WIDTH - 92, "red")
		self.gauge.SetPosition(16, 64)
		self.gauge.Show()

		self.gaugeValue = ui.TextLine()
		self.gaugeValue.SetParent(self)
		self.gaugeValue.SetPosition(HUD_WIDTH - 16, 61)
		self.gaugeValue.SetHorizontalAlignRight()
		self.gaugeValue.SetPackedFontColor(COLOR_DIM)
		self.gaugeValue.SetText("")
		self.gaugeValue.Show()

		self.statusText = ui.TextLine()
		self.statusText.SetParent(self)
		self.statusText.SetPosition(HUD_WIDTH / 2, 84)
		self.statusText.SetHorizontalAlignCenter()
		self.statusText.SetPackedFontColor(COLOR_DIM)
		self.statusText.SetText("")
		self.statusText.Show()

		self.hintText = ui.TextLine()
		self.hintText.SetParent(self)
		self.hintText.SetPosition(HUD_WIDTH / 2, 103)
		self.hintText.SetHorizontalAlignCenter()
		self.hintText.SetPackedFontColor(COLOR_DIM)
		self.hintText.SetText("")
		self.hintText.Show()

		self.lastUpdateTime = 0

		self.Hide()

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def Destroy(self):
		self.coinIcon = None
		self.titleText = None
		self.spotsLabel = None
		self.spotsValue = None
		self.gauge = None
		self.gaugeValue = None
		self.statusText = None
		self.hintText = None
		self.Hide()

	def UpdateData(self, spotsLeft, spotsMax, myDmg, threshold, qualified, rank, qualifiedCount):
		self.lastUpdateTime = app.GetGlobalTimeStamp()

		self.spotsValue.SetText("%d/%d" % (spotsLeft, spotsMax))
		self.spotsValue.SetPackedFontColor(COLOR_DANGER if spotsLeft <= 0 else COLOR_GOLD)

		if threshold > 0:
			self.gauge.SetPercentage(min(myDmg, threshold), threshold)
		else:
			self.gauge.SetPercentage(0, 1)

		if qualified:
			self.gaugeValue.SetText(_FormatDamage(myDmg))
			self.gaugeValue.SetPackedFontColor(COLOR_GOOD)

			outranked = rank > spotsMax
			if outranked:
				self.statusText.SetText(getattr(localeinfo, "CURSED_HUD_OUTRANKED", "Outranked - fight back!"))
				self.statusText.SetPackedFontColor(COLOR_DANGER)
			else:
				self.statusText.SetText(getattr(localeinfo, "CURSED_HUD_QUALIFIED", "Booked - hold your rank!"))
				self.statusText.SetPackedFontColor(COLOR_GOOD)

			self.hintText.SetText("%d/%d - %s" % (rank, qualifiedCount, getattr(localeinfo, "CURSED_HUD_STAY", "be there when it dies")))
			self.hintText.SetPackedFontColor(COLOR_DANGER if outranked else COLOR_DIM)
		else:
			self.gaugeValue.SetText("%s/%s" % (_FormatDamage(myDmg), _FormatDamage(threshold)))
			self.gaugeValue.SetPackedFontColor(COLOR_DIM)

			self.statusText.SetText(getattr(localeinfo, "CURSED_HUD_PROGRESS", "Deal damage to book a coin"))
			self.statusText.SetPackedFontColor(COLOR_DIM)

			self.hintText.SetText("")

		if not self.IsShow():
			self.Show()
			self.SetTop()

	def Close(self):
		self.lastUpdateTime = 0
		self.Hide()

	def OnUpdate(self):
		if not self.IsShow() or self.lastUpdateTime == 0:
			return
		if app.GetGlobalTimeStamp() - self.lastUpdateTime > STALE_TIMEOUT_SEC:
			self.Close()
