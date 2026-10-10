# coding: latin_1

import app
import ui
import player
import wndMgr
import localeinfo

TRACK_WIDTH = 540
ZONE_IMAGE_WIDTH = 53

FISH_FRAME_COUNT = 127
FISH_FRAME_STEP = 2

EFFECT_FRAME_COUNT = 9
EFFECT_WIDTH = 132
EFFECT_HEIGHT = 38
EFFECT_SCALE = 1.5

ROOT_PATH = "d:/ymir work/ui/game/fishing/"
EFFECT_PATH = "d:/ymir work/ui/game/common/animation/"

COLOR_GOOD = 0xFF7CE87C
COLOR_BAD = 0xFFE87C7C


class FishingBdoWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__Initialize()
		self.__Load()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __Initialize(self):
		self.roundText = None
		self.hitsText = None
		self.statusText = None
		self.hintText = None
		self.trackImage = None
		self.zoneImage = None
		self.fishImage = None
		self.successAni = None
		self.failAni = None
		self.criticalAni = None

		self.roundsTotal = 0
		self.hitsRequired = 0
		self.hitsSoFar = 0
		self.roundIndex = 0
		self.fishMoving = False
		self.roundStartTime = 0.0
		self.roundTravelSec = 0.0
		self.fishRunPixels = 0
		self.statusClearTime = 0.0
		self.autoCloseTime = 0.0
		self.gameEnded = False

	def Destroy(self):
		self.ClearDictionary()
		self.__Initialize()

	def __Load(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/FishingBdoWindow.py")

			self.roundText = self.GetChild("round_text")
			self.hitsText = self.GetChild("hits_text")
			self.statusText = self.GetChild("status_text")
			self.hintText = self.GetChild("hint_text")
			self.trackImage = self.GetChild("track_bg")
		except:
			import exception
			exception.Abort("FishingBdoWindow.__Load")

		if self.hintText:
			self.hintText.SetText(getattr(localeinfo, "FISHING_BDO_HINT", "Press SPACE when the fish is fully inside the green zone!"))

		self.__CreateZoneImage()
		self.__CreateFishImage()
		self.successAni = self.__CreateEffectAni("effect_success")
		self.failAni = self.__CreateEffectAni("effect_failed")
		self.criticalAni = self.__CreateEffectAni("effect_critical")

	def __CreateZoneImage(self):
		image = ui.ExpandedImageBox()
		image.SetParent(self.trackImage)
		image.SetPosition(0, 0)
		image.LoadImage(ROOT_PATH + "bar.png")
		image.AddFlag("not_pick")
		image.Hide()
		self.zoneImage = image

	def __CreateFishImage(self):
		image = ui.AniImageBox()
		image.SetParent(self.trackImage)
		image.SetPosition(0, 0)
		image.SetDelay(3)
		for frame in xrange(0, FISH_FRAME_COUNT, FISH_FRAME_STEP):
			image.AppendImage(ROOT_PATH + "fish/fish_%03d.png" % frame)
		image.AddFlag("not_pick")
		image.Hide()
		self.fishImage = image

	def __CreateEffectAni(self, folderName):
		ani = ui.AniImageBox()
		ani.SetParent(self)
		ani.SetDelay(3)
		for frame in xrange(1, EFFECT_FRAME_COUNT + 1):
			ani.AppendImage(EFFECT_PATH + folderName + "/%d.png" % frame)
		ani.SetScale(EFFECT_SCALE, EFFECT_SCALE)
		ani.SetPosition(int((self.GetWidth() - EFFECT_WIDTH * EFFECT_SCALE) / 2), 4)
		ani.AddFlag("not_pick")
		ani.SetEndFrameEvent(ui.__mem_func__(self.__OnEffectEnd))
		ani.Hide()
		return ani

	def __OnEffectEnd(self):
		if self.successAni:
			self.successAni.Hide()
		if self.failAni:
			self.failAni.Hide()
		if self.criticalAni:
			self.criticalAni.Hide()

	def __PlayEffect(self, ani):
		if not ani:
			return
		ani.ResetFrame()
		ani.Show()

	def Open(self, roundsTotal, hitsRequired):
		self.roundsTotal = max(1, roundsTotal)
		self.hitsRequired = hitsRequired
		self.hitsSoFar = 0
		self.roundIndex = 0
		self.fishMoving = False
		self.roundStartTime = 0.0
		self.roundTravelSec = 0.0
		self.statusClearTime = 0.0
		self.autoCloseTime = 0.0
		self.gameEnded = False

		self.__RefreshCounters()
		if self.statusText:
			self.statusText.SetText("")
		if self.zoneImage:
			self.zoneImage.Hide()
		if self.fishImage:
			self.fishImage.Hide()
		if self.successAni:
			self.successAni.Hide()
		if self.failAni:
			self.failAni.Hide()
		if self.criticalAni:
			self.criticalAni.Hide()

		self.SetPosition(int((wndMgr.GetScreenWidth() - self.GetWidth()) / 2), int(wndMgr.GetScreenHeight() / 5))
		self.SetTop()
		self.Show()

	def StartRound(self, roundIndex, zoneStartPm, zoneWidthPm, travelMs):
		if not self.IsShow():
			return

		self.roundIndex = roundIndex
		self.__RefreshCounters()

		trackPm = getattr(app, "FISHING_BDO_TRACK_PM", 1000)
		fishPm = getattr(app, "FISHING_BDO_FISH_PM", 98)
		zoneX = int(TRACK_WIDTH * zoneStartPm / trackPm)
		zoneWidth = max(1, int(TRACK_WIDTH * zoneWidthPm / trackPm))

		if self.zoneImage:
			self.zoneImage.SetPosition(zoneX, 0)
			self.zoneImage.SetScale(float(zoneWidth) / float(ZONE_IMAGE_WIDTH), 1.0)
			self.zoneImage.SetDiffuseColor(1.0, 1.0, 1.0, 0.8)
			self.zoneImage.Show()

		if self.fishImage:
			self.fishImage.SetPosition(0, 0)
			self.fishImage.Show()

		self.fishRunPixels = int(TRACK_WIDTH * (trackPm - fishPm) / trackPm)
		self.roundStartTime = app.GetTime()
		self.roundTravelSec = travelMs / 1000.0
		self.fishMoving = True

		if self.statusText:
			self.statusText.SetText("")

	def OnRoundResult(self, roundIndex, hit, hitsSoFar):
		self.hitsSoFar = hitsSoFar
		self.fishMoving = False
		self.__RefreshCounters()

		if self.statusText:
			if hit:
				self.statusText.SetPackedFontColor(COLOR_GOOD)
				self.statusText.SetText(getattr(localeinfo, "FISHING_BDO_HIT", "Hooked!"))
			else:
				self.statusText.SetPackedFontColor(COLOR_BAD)
				self.statusText.SetText(getattr(localeinfo, "FISHING_BDO_MISS", "Missed!"))

		if self.zoneImage:
			if hit:
				self.zoneImage.SetDiffuseColor(0.6, 1.0, 0.6, 1.0)
			else:
				self.zoneImage.SetDiffuseColor(1.0, 0.5, 0.5, 1.0)

		self.statusClearTime = app.GetTime() + 0.6

	def OnGameEnd(self, success, doubled=0):
		self.gameEnded = True
		self.fishMoving = False
		self.statusClearTime = 0.0

		if self.statusText:
			self.statusText.SetText("")

		if success and doubled:
			self.__PlayEffect(self.criticalAni)
		elif success:
			self.__PlayEffect(self.successAni)
		else:
			self.__PlayEffect(self.failAni)

		self.autoCloseTime = app.GetTime() + 1.5

	def OnServerQuit(self):
		self.fishMoving = False
		self.statusClearTime = 0.0
		self.autoCloseTime = 0.0
		self.Hide()

	def PressSpace(self):
		if not self.IsShow():
			return
		if self.gameEnded:
			return
		player.FishingBdoPress()

	def RequestQuit(self):
		if not self.gameEnded:
			player.FishingBdoQuit()
		self.fishMoving = False
		self.statusClearTime = 0.0
		self.autoCloseTime = 0.0
		self.Hide()

	def OnPressEscapeKey(self):
		self.RequestQuit()
		return True

	def __RefreshCounters(self):
		if self.roundText:
			shownRound = min(self.roundIndex + 1, self.roundsTotal)
			self.roundText.SetText(getattr(localeinfo, "FISHING_BDO_ROUND", "Round %d / %d") % (shownRound, self.roundsTotal))
		if self.hitsText:
			self.hitsText.SetText(getattr(localeinfo, "FISHING_BDO_HITS", "Catches %d / %d") % (self.hitsSoFar, self.hitsRequired))

	def OnUpdate(self):
		now = app.GetTime()

		if self.fishMoving and self.fishImage and self.roundTravelSec > 0:
			progress = (now - self.roundStartTime) / self.roundTravelSec
			if progress < 0.0:
				progress = 0.0
			elif progress > 1.0:
				progress = 1.0
			self.fishImage.SetPosition(int(self.fishRunPixels * progress), 0)

		if self.statusClearTime and now >= self.statusClearTime:
			self.statusClearTime = 0.0
			if self.statusText:
				self.statusText.SetText("")
			if self.zoneImage:
				self.zoneImage.SetDiffuseColor(1.0, 1.0, 1.0, 0.8)

		if self.autoCloseTime and now >= self.autoCloseTime:
			self.autoCloseTime = 0.0
			self.Hide()
