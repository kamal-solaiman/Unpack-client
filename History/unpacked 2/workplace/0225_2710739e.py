# coding: utf-8

import player
import wndMgr

import ui

class DamageWindow(ui.Window):
	def Close(self):
		if not self.IsShow():
			return

		self.Hide()

	def OnUpdate(self):
		if self.alpha_delay == 0:
			self.alpha_delay = 45

			if self.image_damage:
				self.image_damage.SetAlpha(self.alpha_value)

			if self.alpha_count == 2:
				self.Hide()
				return

			if self.alpha_value == 0.0:
				self.alpha_value = 1.0
				self.alpha_count += 1
			else:
				self.alpha_value -= 1
		else:
			self.alpha_delay -= 1

	def Open(self, damage_type):
		if not self.image_damage:
			self.image_damage = ui.ExpandedImageBox()
			self.image_damage.SetParent(self)
			self.image_damage.SetPosition(0, 0)
			self.image_damage.Show()

		if damage_type == player.UI_DAMAGE_ICICLE:
			if self.damage_type == player.UI_DAMAGE_NONE:
				self.image_damage.LoadImage("d:/ymir work/ui/whitedragon_damage_01.dds")
			elif self.damage_type != damage_type:
				self.image_damage.UnloadImage()

			image_width = self.image_damage.GetWidth()
			image_height = self.image_damage.GetHeight()

			self.alpha_count = 0
			self.alpha_value = 1.0
			self.alpha_delay = 0

			self.image_damage.SetScale(float(self.screen_width) / float(image_width), float(self.screen_height) / float(image_height))

			self.Show()
		else:
			return

	def __init__(self):
		ui.Window.__init__(self)

		self.image_damage = None

		self.damage_type = player.UI_DAMAGE_NONE

		self.screen_width = wndMgr.GetScreenWidth()
		self.screen_height = wndMgr.GetScreenHeight()

		self.alpha_count = 0
		self.alpha_value = 1.0

		self.SetSize(0, 0)
		self.SetPosition(0, 0)

	def Destroy(self):
		self.Close()

		if self.image_damage:
			del self.image_damage
			self.image_damage = None

		self.damage_type = None

		self.screen_width = None
		self.screen_height = None

		self.alpha_count = None
		self.alpha_value = None

	def __del__(self):
		ui.Window.__del__(self)
