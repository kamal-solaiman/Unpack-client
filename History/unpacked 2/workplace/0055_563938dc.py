# coding: latin_1

import app

if app.ENABLE_INGAME_WIKI:
	import ui
	import localeinfo
	import game_data


	# Atlas tile size in world units: 128 cells per tile x 200 sub-units per cell.
	# Same constant the working tooltip code uses.
	TILE_UNITS = 128 * 200

	# The stock waypoint sprite: a ring contracting onto a dot over 7 frames,
	# 30x30 each. mini_waypoint08..12 are NOT continuation frames -- they are
	# 10x10 subs from an unrelated atlas region.
	WAYPOINT_PATH_FMT = "d:/ymir work/ui/minimap/mini_waypoint%02d.sub"
	WAYPOINT_FRAMES = 7
	WAYPOINT_HALF = 15.0     # icon is 30x30; offset to center on the coordinate
	WAYPOINT_RATE = 1.15     # cycles per second
	# Share of the cycle spent ramping in at the start and out at the end; hides
	# the wrap from the last (smallest) frame back to the first (largest).
	WAYPOINT_EDGE = 0.22


	class SmoothPin(ui.Window):
		"""Waypoint marker that plays the stock sprite sequence continuously.

		ui.AniImageBox cuts between frames and snaps from the smallest frame back
		to the largest at the wrap. This keeps one image box per frame and
		cross-fades the visible pair instead, so the same artwork plays smoothly.
		LoadImage is therefore never called per frame: CImageBox::LoadImage
		reallocates the image instance and resets its diffuse colour.
		"""

		def __init__(self):
			ui.Window.__init__(self)
			self.frames = []
			self.curFrame = -1
			self.SetSize(int(WAYPOINT_HALF * 2), int(WAYPOINT_HALF * 2))
			for i in xrange(1, WAYPOINT_FRAMES + 1):
				box = ui.ExpandedImageBox()
				box.SetParent(self)
				box.LoadImage(WAYPOINT_PATH_FMT % i)
				box.AddFlag("not_pick")
				self.frames.append(box)

		def OnUpdate(self):
			if not self.frames:
				return
			t = (app.GetTime() * WAYPOINT_RATE) % 1.0
			f = t * WAYPOINT_FRAMES
			idx = int(f)
			if idx >= WAYPOINT_FRAMES:
				idx = WAYPOINT_FRAMES - 1
			nxt = (idx + 1) % WAYPOINT_FRAMES
			edge = min(t, 1.0 - t) / WAYPOINT_EDGE
			if edge > 1.0:
				edge = 1.0
			frac = f - idx

			if idx != self.curFrame:
				prev = self.curFrame
				if prev >= 0:
					self.frames[prev].Hide()
					self.frames[(prev + 1) % WAYPOINT_FRAMES].Hide()
				self.frames[idx].Show()
				self.frames[nxt].Show()
				self.curFrame = idx

			self.frames[idx].SetDiffuseColor(1.0, 1.0, 1.0, (1.0 - frac) * edge)
			self.frames[nxt].SetDiffuseColor(1.0, 1.0, 1.0, frac * edge)


	def GetSpawnData(vnum):
		"""Return list of {map, x, y, type} records for this vnum, or [] if none."""
		try:
			return game_data.mobSpawnDict.get(int(vnum), [])
		except (TypeError, ValueError):
			return []


	def RenderMiniMapIntoTooltip(tooltip, mapName, coords):
		"""Append a minimap atlas + animated waypoint dots to a uitooltip.ToolTip.

		Adds the atlas as a child of the tooltip with parented SmoothPin dots,
		using the tooltip's toolTipHeight / toolTipWidth / childrenList /
		ResizeToolTip so the tooltip resizes to fit. Caller is responsible for
		HideToolTip() / ShowToolTip() lifecycle.

		`coords` may be a list of (x, y) tuples or a list of {x, y} dicts -- both
		formats are accepted so the helper can serve the legacy npcOriginDict
		path AND the new mobSpawnDict path.

		Returns True if the minimap was added; False if the atlas or size info
		is unavailable -- caller can fall back to text-only.
		"""
		if not mapName:
			return False

		# Look up tile dimensions; without them we can't position dots.
		sizeXY = game_data.mapSizeDict.get(mapName)
		if not sizeXY:
			return False
		tilesX, tilesY = sizeXY
		if tilesX <= 0 or tilesY <= 0:
			return False

		# Atlas ImageBox parented to the tooltip.
		mapImage = ui.ImageBox()
		mapImage.SetParent(tooltip)
		mapImage.LoadImage("d:/ymir work/ui/atlas/{}/atlas.sub".format(mapName))

		mapW = mapImage.GetWidth()
		mapH = mapImage.GetHeight()
		if mapW <= 0 or mapH <= 0:
			# No atlas shipped for this map -- nothing visual to show.
			try:
				mapImage.Hide()
			except Exception:
				pass
			return False

		# Position the atlas under any text already in the tooltip.
		mapImage.SetPosition(0, tooltip.toolTipHeight + 4)
		mapImage.SetWindowHorizontalAlignCenter()
		mapImage.Show()

		# Compute pixel positions and create animated waypoint pins, parented
		# to the atlas so they move with it.
		worldW = float(tilesX * TILE_UNITS)
		worldH = float(tilesY * TILE_UNITS)

		dots = []
		for c in coords:
			if isinstance(c, dict):
				try:
					x = float(c["x"])
					y = float(c["y"])
				except (KeyError, TypeError, ValueError):
					continue
			else:
				try:
					x = float(c[0])
					y = float(c[1])
				except (TypeError, ValueError, IndexError):
					continue

			# Formula matches the user's working tooltip implementation.
			px = (x / worldW * mapW) * 100 - WAYPOINT_HALF
			py = (y / worldH * mapH) * 100 - WAYPOINT_HALF

			dot = SmoothPin()
			dot.SetParent(mapImage)
			dot.SetPosition(int(px), int(py))
			dot.Show()
			dots.append(dot)

		# Register children so the tooltip cleans them up on ClearToolTip().
		tooltip.childrenList.append(mapImage)
		tooltip.childrenList.extend(dots)

		# Grow the tooltip to fit the atlas plus a small bottom gap.
		tooltip.toolTipHeight += mapH + 6
		if tooltip.toolTipWidth < mapW + 20:
			tooltip.toolTipWidth = mapW + 20
		tooltip.ResizeToolTip()

		return True
