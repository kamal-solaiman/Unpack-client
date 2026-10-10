# coding: latin_1
import os
import wndMgr

# Module state
_positions = {}    # {window_id: {"x": x, "y": y, "screen_w": w, "screen_h": h}}
_loaded = False    # Whether we've loaded positions from file

# Constants
SAVE_FILE = "UserData/window_positions.cfg"
MARGIN = 50  # Minimum pixels window must remain visible on screen


def _EnsureFolder():
	"""Ensure the UserData folder exists."""
	folder = "UserData"
	if not os.path.exists(folder):
		os.makedirs(folder)


def Load():
	"""Load positions from file. Called once on game start."""
	global _positions, _loaded

	_positions = {}
	_loaded = True

	if not os.path.exists(SAVE_FILE):
		return

	try:
		infoFile = old_open(SAVE_FILE, "rb")
		content = infoFile.read()
		infoFile.close()
		_positions = eval(content)
	except:
		_positions = {}


def Save():
	global _positions

	_EnsureFolder()

	try:
		content = str(_positions)
		infoFile = old_open(SAVE_FILE, "wb")
		infoFile.write(content)
		infoFile.close()
	except:
		pass  # Silent fail


def GetPosition(windowId):
	global _loaded

	if not _loaded:
		Load()

	if windowId not in _positions:
		return None

	data = _positions[windowId]
	x, y = data["x"], data["y"]
	savedW = data.get("screen_w", 0)
	savedH = data.get("screen_h", 0)


	currentW = wndMgr.GetScreenWidth()
	currentH = wndMgr.GetScreenHeight()


	if savedW > 0 and savedH > 0:
		if savedW != currentW or savedH != currentH:
			x = int(x * currentW / savedW)
			y = int(y * currentH / savedH)


	x = max(-MARGIN, min(x, currentW - MARGIN))
	y = max(0, min(y, currentH - MARGIN))

	return (x, y)


def SetPosition(windowId, x, y):
	global _positions

	_positions[windowId] = {
		"x": x,
		"y": y,
		"screen_w": wndMgr.GetScreenWidth(),
		"screen_h": wndMgr.GetScreenHeight()
	}


def ApplySavedPosition(window, windowId):
	pos = GetPosition(windowId)
	if pos:
		x, y = pos
		window.SetPosition(x, y)
		return True
	return False


def OnWindowMove(windowId, x, y):
	SetPosition(windowId, x, y)


def SaveOnClose(window, windowId):
	"""
	Save current window position to memory, then flush to disk.
	Call this in window's Close() or Hide() method.
	"""
	try:
		x, y = window.GetGlobalPosition()
		SetPosition(windowId, x, y)
	except:
		pass  # Window may not have valid position

	Save()
