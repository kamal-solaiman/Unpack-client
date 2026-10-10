import app
import player

MOD_CTRL = 1
MOD_SHIFT = 2
MOD_ALT = 4

SAVE_FILE = "keybinds.txt"
SAVE_VERSION = 1
MAX_SLOTS = 2

_actions = []
_actionById = {}
_chordIndex = {}
_binds = {}
_unknownBinds = {}
_active = {}
_captureHandler = None
_gameWindow = None
_dirty = False
_altPageBase = -1

_MOD_DIKS = {}
_RESERVED_DIKS = {}

def _InitTables():
	global _MOD_DIKS, _RESERVED_DIKS
	_MOD_DIKS = {
		app.DIK_LCONTROL : MOD_CTRL, app.DIK_RCONTROL : MOD_CTRL,
		app.DIK_LSHIFT : MOD_SHIFT, app.DIK_RSHIFT : MOD_SHIFT,
		app.DIK_LALT : MOD_ALT, app.DIK_RALT : MOD_ALT,
	}
	_RESERVED_DIKS = { app.DIK_ESC : 1, app.DIK_RETURN : 1, app.DIK_TAB : 1 }

def CurrentMask():
	mask = 0
	if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
		mask |= MOD_CTRL
	if app.IsPressed(app.DIK_LSHIFT) or app.IsPressed(app.DIK_RSHIFT):
		mask |= MOD_SHIFT
	if app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT):
		mask |= MOD_ALT
	return mask

def Boot(gameWindow):
	global _gameWindow, _dirty, _captureHandler, _altPageBase
	import keyactions
	_InitTables()
	_gameWindow = gameWindow
	_captureHandler = None
	_altPageBase = -1
	del _actions[:]
	_actionById.clear()
	_active.clear()
	_binds.clear()
	_unknownBinds.clear()
	for act in keyactions.BuildActions():
		_actions.append(act)
		_actionById[act.id] = act
	_LoadFile()
	_RebuildIndex()
	_dirty = False

def Shutdown():
	global _gameWindow, _captureHandler
	if _dirty:
		SaveFile()
	_captureHandler = None
	_gameWindow = None
	_active.clear()

def GetActions():
	return _actions

def GetBinds(actionId):
	return list(_binds.get(actionId, ()))

def _RebuildIndex():
	_chordIndex.clear()
	for act in _actions:
		for chord in _binds.get(act.id, ()):
			if chord:
				_chordIndex[chord] = act

def _SetDefaults():
	_binds.clear()
	for act in _actions:
		_binds[act.id] = [tuple(c) for c in act.default]

def _LoadFile():
	_SetDefaults()
	try:
		f = open(SAVE_FILE, "rb")
		lines = f.read().split("\n")
		f.close()
	except IOError:
		return
	try:
		for line in lines:
			line = line.rstrip("\r")
			if not line or line.find("\t") < 0:
				continue
			actionId, value = line.split("\t", 1)
			if actionId == "version":
				continue
			chords = []
			for part in value.split(";"):
				part = part.strip()
				if not part:
					chords.append(None)
					continue
				maskStr, dikStr = part.split(",", 1)
				chords.append((int(maskStr), int(dikStr)))
			chords = chords[:MAX_SLOTS]
			if actionId in _actionById:
				_binds[actionId] = chords
			else:
				_unknownBinds[actionId] = chords
	except (ValueError, IndexError):
		import dbg
		dbg.TraceError("keybinds: malformed %s, using defaults" % SAVE_FILE)
		_SetDefaults()
		_unknownBinds.clear()

def _ChordsToLine(chords):
	parts = []
	for chord in chords:
		if chord:
			parts.append("%d,%d" % (chord[0], chord[1]))
		else:
			parts.append("")
	return ";".join(parts)

def SaveFile():
	global _dirty
	lines = ["version\t%d" % SAVE_VERSION]
	for act in _actions:
		lines.append("%s\t%s" % (act.id, _ChordsToLine(_binds.get(act.id, ()))))
	for actionId in _unknownBinds:
		lines.append("%s\t%s" % (actionId, _ChordsToLine(_unknownBinds[actionId])))
	tmpName = SAVE_FILE + ".tmp"
	import os
	try:
		f = open(tmpName, "wb")
		f.write("\n".join(lines))
		f.close()
		try:
			os.remove(SAVE_FILE)
		except OSError:
			pass
		os.rename(tmpName, SAVE_FILE)
	except (IOError, OSError):
		import dbg
		dbg.TraceError("keybinds: save failed %s" % SAVE_FILE)
		return
	_dirty = False

def SetBind(actionId, slot, mask, dik):
	global _dirty
	act = _actionById.get(actionId)
	if not act or act.fixed or slot >= act.slots:
		return None
	if dik in _MOD_DIKS or dik in _RESERVED_DIKS:
		return None
	chord = (mask, dik)
	stolenId = None
	owner = _chordIndex.get(chord)
	if owner and owner.id != actionId:
		stolenId = owner.id
		_binds[owner.id] = [None if c == chord else c for c in _binds.get(owner.id, ())]
	elif owner and owner.id == actionId:
		_binds[actionId] = [c for c in _binds[actionId] if c != chord]
	chords = _binds.get(actionId, [])
	while len(chords) <= slot:
		chords.append(None)
	chords[slot] = chord
	_binds[actionId] = chords
	_RebuildIndex()
	_dirty = True
	return stolenId

def FindOwner(mask, dik):
	act = _chordIndex.get((mask, dik))
	if act:
		return act.id
	return None

def ClearBind(actionId, slot):
	global _dirty
	chords = _binds.get(actionId)
	if not chords or slot >= len(chords):
		return
	chords[slot] = None
	_RebuildIndex()
	_dirty = True

def ResetDefaults():
	global _dirty
	_SetDefaults()
	_RebuildIndex()
	_dirty = True

def Snapshot():
	snap = {}
	for actionId in _binds:
		snap[actionId] = list(_binds[actionId])
	return snap

def Restore(snap):
	global _dirty
	_binds.clear()
	for actionId in snap:
		_binds[actionId] = list(snap[actionId])
	_RebuildIndex()
	_dirty = True

def IsDirtySince(snap):
	if len(snap) != len(_binds):
		return True
	for actionId in _binds:
		if snap.get(actionId) != _binds[actionId]:
			return True
	return False

def SetCaptureHandler(fn):
	global _captureHandler
	_captureHandler = fn

def _AltPageDown():
	global _altPageBase
	if _altPageBase < 0:
		_altPageBase = player.GetQuickPage()
		player.SetQuickPage(_altPageBase + 1)
		if _gameWindow:
			_gameWindow.ShowName()

def _AltPageUp():
	global _altPageBase
	if _altPageBase >= 0:
		page = _altPageBase
		if page < 0 or page > 3:
			page = 0
		player.SetQuickPage(page)
		_altPageBase = -1
	if _gameWindow:
		_gameWindow.HideName()

def OnKeyDown(dik):
	if _captureHandler:
		if dik in _MOD_DIKS:
			return
		fn = _captureHandler
		fn(CurrentMask(), dik)
		return
	if dik in _MOD_DIKS:
		if _MOD_DIKS[dik] == MOD_ALT:
			_AltPageDown()
		return
	act = _chordIndex.get((CurrentMask(), dik))
	if not act:
		return
	_active[dik] = act
	if act.down:
		act.down(_gameWindow)

def OnKeyUp(dik):
	if _captureHandler:
		return
	if dik in _MOD_DIKS:
		if _MOD_DIKS[dik] == MOD_ALT:
			_AltPageUp()
		return
	act = _active.pop(dik, None)
	if act and act.up:
		act.up(_gameWindow)

def ChordName(mask, dik):
	import keyactions
	parts = []
	if mask & MOD_CTRL:
		parts.append(keyactions.DikName(app.DIK_LCONTROL))
	if mask & MOD_SHIFT:
		parts.append(keyactions.DikName(app.DIK_LSHIFT))
	if mask & MOD_ALT:
		parts.append(keyactions.DikName(app.DIK_LALT))
	parts.append(keyactions.DikName(dik))
	return " + ".join(parts)
