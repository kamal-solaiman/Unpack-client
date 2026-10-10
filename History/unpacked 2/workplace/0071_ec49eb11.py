import app
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import net
import snd
import ime
import wndMgr
import ServerStateChecker

import ui
import musicinfo
import systemSetting
import localeinfo
import constinfo
import uiscriptlocale
import serverinfo

import time
import _winreg
from _weakref import proxy

if getattr(app, "ENABLE_FAST_LOGIN", 0):
	import os

REGISTER_LINK = "https://history2.ae/register"
FORGOT_PASSWORD_LINK = "https://history2.ae/forgot-password"
FORGOT_USERNAME_LINK = "https://history2.ae/forgot-username"
REG_PATH = r"SOFTWARE\Classic2"

LOGIN_PANEL_WIDTH = 410
NEW_LOGIN_PATH = "d:/ymir work/ui/newlogin/"
CHANNEL_LIST_DELTA = 180
ACC_ROW_H = 46
ACC_VIEW_H = 183
ACC_CONTENT_H = 552
ACC_OVERFLOW = 369
ACC_SCROLLBAR_X = 304
ACC_FKEY_X = 250
ACC_NAME_X = 149
ACC_TEXT_Y = 13
SCROLLBAR_BASE = NEW_LOGIN_PATH + "scrollbar_base.png"
SCROLLBAR_MOVE = NEW_LOGIN_PATH + "scrollbar_move.png"
BUTTON_AREA_BOTTOM = 200

#135.125.188.80

def set_reg(name, value):
	try:
		_winreg.CreateKey(_winreg.HKEY_CURRENT_USER, REG_PATH)
		registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATH, 0, _winreg.KEY_WRITE)
		_winreg.SetValueEx(registry_key, name, 0, _winreg.REG_SZ, value)
		_winreg.CloseKey(registry_key)
		return True
	except WindowsError:
		return False

def get_reg(name):
	try:
		registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATH, 0, _winreg.KEY_READ)
		value, regtype = _winreg.QueryValueEx(registry_key, name)
		_winreg.CloseKey(registry_key)
		return str(value)
	except WindowsError:
		return None

if getattr(app, "ENABLE_FAST_LOGIN", 0):
	class FastLoginManager(object):
		_instance = None
		MAX_SLOTS = 5
		FILE_PATH = 'FastLogin.bin'

		AES_KEY = (
			'\x01\x02\x03\x04\x05\x06\x07\x08'
			'\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10'
			'\x11\x12\x13\x14\x15\x16\x17\x18'
			'\x19\x1A\x1B\x1C\x1D\x1E\x1F\x20'
		)

		AES_IV = (
			'\x0F\x0E\x0D\x0C'
			'\x0B\x0A\x09\x08'
			'\x07\x06\x05\x04'
			'\x03\x02\x01\x00'
		)

		FACE_ICONS = {
			0: "d:/ymir work/bin/icon/face/warrior_m.tga",
			1: "d:/ymir work/bin/icon/face/assassin_w.tga",
			2: "d:/ymir work/bin/icon/face/sura_m.tga",
			3: "d:/ymir work/bin/icon/face/shaman_w.tga",
			4: "d:/ymir work/bin/icon/face/warrior_w.tga",
			5: "d:/ymir work/bin/icon/face/assassin_m.tga",
			6: "d:/ymir work/bin/icon/face/sura_w.tga",
			7: "d:/ymir work/bin/icon/face/shaman_m.tga",
			8: "d:/ymir work/bin/icon/face/wolfman_m.tga",
		}

		# New portraits exist only for warrior/assassin (races 0/1/4/5); the
		# rest fall back to the legacy TGA icons until the art lands.
		NEW_FACE_ICONS = {
			0: NEW_LOGIN_PATH + "face/warrior_m.png",
			1: NEW_LOGIN_PATH + "face/assassin_w.png",
			4: NEW_LOGIN_PATH + "face/warrior_w.png",
			5: NEW_LOGIN_PATH + "face/assassin_m.png",
		}

		SERVER_NAMES = {
			1: "Dragon",
			2: "Syrax",
		}

		@classmethod
		def GetInstance(cls):
			if cls._instance is None:
				cls._instance = cls()
			return cls._instance

		@classmethod
		def GetFacePath(cls, race):
			path = cls.NEW_FACE_ICONS.get(race)
			if path:
				return path
			return cls.FACE_ICONS.get(race, "")

		def __init__(self):
			self.cachedData = None

		@staticmethod
		def _JsonEncode(obj):
			if obj is None:
				return "null"
			if isinstance(obj, bool):
				return "true" if obj else "false"
			if isinstance(obj, int):
				return str(obj)
			if isinstance(obj, float):
				return str(obj)
			if isinstance(obj, str):
				return '"' + obj.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t') + '"'
			if isinstance(obj, unicode):
				return FastLoginManager._JsonEncode(obj.encode('utf-8'))
			if isinstance(obj, list):
				return '[' + ', '.join(FastLoginManager._JsonEncode(v) for v in obj) + ']'
			if isinstance(obj, dict):
				pairs = []
				for k, v in obj.items():
					pairs.append(FastLoginManager._JsonEncode(str(k)) + ': ' + FastLoginManager._JsonEncode(v))
				return '{' + ', '.join(pairs) + '}'
			return '"' + str(obj) + '"'

		@staticmethod
		def _JsonDecode(s):
			s = s.strip()
			if not s:
				return {}
			value, _ = FastLoginManager._JsonParseValue(s, 0)
			return value

		@staticmethod
		def _JsonSkipWs(s, i):
			n = len(s)
			while i < n and s[i] in ' \t\r\n':
				i += 1
			return i

		@staticmethod
		def _JsonParseValue(s, i):
			i = FastLoginManager._JsonSkipWs(s, i)
			if i >= len(s):
				raise ValueError("unexpected end of data")
			c = s[i]
			if c == '{':
				return FastLoginManager._JsonParseObject(s, i)
			if c == '[':
				return FastLoginManager._JsonParseArray(s, i)
			if c == '"':
				return FastLoginManager._JsonParseString(s, i)
			if s[i:i + 4] == 'true':
				return True, i + 4
			if s[i:i + 5] == 'false':
				return False, i + 5
			if s[i:i + 4] == 'null':
				return None, i + 4
			return FastLoginManager._JsonParseNumber(s, i)

		@staticmethod
		def _JsonParseString(s, i):
			i += 1
			out = []
			n = len(s)
			while i < n:
				c = s[i]
				if c == '\\':
					i += 1
					if i >= n:
						raise ValueError("bad escape")
					out.append({'n': '\n', 'r': '\r', 't': '\t'}.get(s[i], s[i]))
					i += 1
				elif c == '"':
					return ''.join(out), i + 1
				else:
					out.append(c)
					i += 1
			raise ValueError("unterminated string")

		@staticmethod
		def _JsonParseNumber(s, i):
			n = len(s)
			start = i
			if i < n and s[i] in '+-':
				i += 1
			isFloat = False
			while i < n and (s[i].isdigit() or s[i] in '.eE+-'):
				if s[i] in '.eE':
					isFloat = True
				i += 1
			token = s[start:i]
			if not token:
				raise ValueError("bad number")
			return (float(token) if isFloat else int(token)), i

		@staticmethod
		def _JsonParseArray(s, i):
			i += 1
			arr = []
			i = FastLoginManager._JsonSkipWs(s, i)
			if i < len(s) and s[i] == ']':
				return arr, i + 1
			while True:
				value, i = FastLoginManager._JsonParseValue(s, i)
				arr.append(value)
				i = FastLoginManager._JsonSkipWs(s, i)
				if i >= len(s):
					raise ValueError("unterminated array")
				if s[i] == ',':
					i += 1
					continue
				if s[i] == ']':
					return arr, i + 1
				raise ValueError("bad array separator")

		@staticmethod
		def _JsonParseObject(s, i):
			i += 1
			obj = {}
			i = FastLoginManager._JsonSkipWs(s, i)
			if i < len(s) and s[i] == '}':
				return obj, i + 1
			while True:
				i = FastLoginManager._JsonSkipWs(s, i)
				if i >= len(s) or s[i] != '"':
					raise ValueError("bad object key")
				key, i = FastLoginManager._JsonParseString(s, i)
				i = FastLoginManager._JsonSkipWs(s, i)
				if i >= len(s) or s[i] != ':':
					raise ValueError("missing colon")
				value, i = FastLoginManager._JsonParseValue(s, i + 1)
				obj[key] = value
				i = FastLoginManager._JsonSkipWs(s, i)
				if i >= len(s):
					raise ValueError("unterminated object")
				if s[i] == ',':
					i += 1
					continue
				if s[i] == '}':
					return obj, i + 1
				raise ValueError("bad object separator")

		def _DeriveKey(self):
			# Bind the AES key to this machine's HWID so a stolen FastLogin.bin
			# cannot be decrypted on another machine even with the client source
			# (the base key ships inside the .epk). The HWID is never written to
			# the file, so it is not recoverable from the file alone.
			hwid = app.GetHwid() or "FastLoginFallbackHWID"
			key = bytearray(self.AES_KEY)
			for i in xrange(len(key)):
				key[i] = key[i] ^ ord(hwid[i % len(hwid)])
			return str(key)

		def _Encrypt(self, text):
			return app.Encrypt(text, self._DeriveKey(), self.AES_IV)

		def _Decrypt(self, data):
			return app.Decrypt(data, self._DeriveKey(), self.AES_IV)

		def _DecryptLegacy(self, data):
			return app.Decrypt(data, self.AES_KEY, self.AES_IV)

		def Load(self):
			if not os.path.exists(self.FILE_PATH):
				return {}
			try:
				with old_open(self.FILE_PATH, 'rb') as f:
					encrypted = f.read()
				if not encrypted:
					return {}
				try:
					return self._JsonDecode(self._Decrypt(encrypted))
				except Exception:
					# Migration: file written with the pre-HWID static key.
					# Decrypt with the legacy key, then re-save under the
					# HWID-derived key so it is machine-bound going forward.
					data = self._JsonDecode(self._DecryptLegacy(encrypted))
					self.Save(data)
					return data
			except Exception as e:
				import dbg
				dbg.TraceError("FastLogin: Load error: {}".format(e))
				return {}

		def Save(self, data):
			if data is None:
				data = {}
			try:
				jsonText = self._JsonEncode(data)
				with old_open(self.FILE_PATH, 'wb') as f:
					f.write(self._Encrypt(jsonText))
				self.cachedData = data
			except Exception as e:
				import dbg
				dbg.TraceError("FastLogin: Save error: {}".format(e))

		def SaveCharacter(self, account, pwd, slot, name, level, race, guild, channel, server, empire=0):
			data = self.Load()
			# >>> FAST_LOGIN crypto BEGIN - the HWID now derives the AES key (see
			# _DeriveKey); storing it in plaintext would leak the key material.
			# docs/FAST_LOGIN_AUDIT_2026-07-26.md
			# if 'hwid' not in data:
			#     data['hwid'] = app.GetHwid()
			# <<< FAST_LOGIN crypto END
			if 'recent' not in data:
				data['recent'] = []

			accountKey = str(account)
			slotKey = str(slot)

			if accountKey not in data:
				data[accountKey] = {'password': pwd}
			elif pwd:
				data[accountKey]['password'] = pwd

			data[accountKey][slotKey] = {
				'name': name,
				'level': level,
				'race': race,
				'guild': guild,
				'channel': channel,
				'server': server,
				'empire': empire,
			}

			recent = data['recent']
			wasPinned = False
			for e in recent:
				if e["account"] == accountKey and e["slot"] == slotKey:
					wasPinned = e.get("pinned", False)
					break

			newEntry = {
				"account": accountKey,
				"slot": slotKey,
				"pinned": wasPinned,
			}

			recent = [e for e in recent if not (e["account"] == accountKey and e["slot"] == slotKey)]
			recent.insert(0, newEntry)

			if len(recent) > self.MAX_SLOTS:
				for i in xrange(len(recent) - 1, self.MAX_SLOTS - 1, -1):
					if not recent[i].get("pinned", False):
						del recent[i]
						break

			data['recent'] = recent
			self.Save(data)

		def GetRecentCharacters(self):
			data = self.Load()

			savedHwid = data.get('hwid')
			if savedHwid and savedHwid != app.GetHwid():
				return []

			recent = data.get('recent', [])
			sortedRecent = sorted(recent, key=lambda e: not e.get("pinned", False))

			result = []
			for entry in sortedRecent[:self.MAX_SLOTS]:
				accountKey = entry["account"]
				slotKey = entry["slot"]
				slotData = data.get(accountKey, {}).get(slotKey, {})
				pwd = data.get(accountKey, {}).get('password', '')

				result.append({
					"account": accountKey,
					"password": pwd,
					"slot": slotKey,
					"name": slotData.get('name', '???'),
					"level": slotData.get('level', 0),
					"race": slotData.get('race', 0),
					"guild": slotData.get('guild', ''),
					"channel": slotData.get('channel', 0),
					"server": slotData.get('server', 1),
					"empire": slotData.get('empire', 0),
					"pinned": entry.get("pinned", False),
				})
			return result

		def TogglePin(self, account, slot):
			data = self.Load()
			for entry in data.get('recent', []):
				if entry["account"] == account and entry["slot"] == slot:
					entry["pinned"] = not entry.get("pinned", False)
			self.Save(data)

		def DeleteEntry(self, account, slot):
			data = self.Load()
			recent = data.get('recent', [])
			data['recent'] = [e for e in recent if not (e["account"] == account and e["slot"] == slot)]
			self.Save(data)

		def GetAutoSave(self):
			data = self.Load()
			return data.get('autosave', True)

		def SetAutoSave(self, enabled):
			data = self.Load()
			data['autosave'] = enabled
			self.Save(data)

	class FastLoginPanel(ui.Window):
		STRIP_PAD = 9
		STRIP_TOP = 12
		STRIP_BOTTOM = 10
		TILE_W = 84
		TILE_H = 66
		TILE_SPACING = 6
		FACE_FRAME = 43
		PANEL_GAP = 14
		STRIP_TOP_Y = 90

		COLOR_SLOT_BG = 0x33000000
		COLOR_SLOT_HOVER = 0x66C58665
		COLOR_NAME = 0xFFD4C1A5
		COLOR_INFO = 0xFFC58665
		COLOR_EMPTY = 0xFFD4C1A5

		EMPIRE_FLAG = {
			1: "new_rank/empire_1.tga",
			2: "new_rank/empire_2.tga",
			3: "new_rank/empire_3.tga",
		}

		def __init__(self):
			ui.Window.__init__(self)
			self.AddFlag("float")
			self.loginWindow = None
			self.slotWidgets = []
			self.emptyText = None
			self.tooltip = None
			self.pinTooltip = None
			self._tooltipChildren = []
			self._pinTooltipChildren = []
			self._stripW = self.TILE_W + self.STRIP_PAD * 2
			self._stripH = 100

			self.bg = ui.ThinBoard("UI", 2)
			self.bg.SetParent(self)
			self.bg.SetPosition(0, 0)
			self.bg.AddFlag("not_pick")
			self.bg.Show()

		def __del__(self):
			ui.Window.__del__(self)

		def Open(self, loginWindow):
			self.loginWindow = loginWindow
			self.RefreshSlots()
			self.Redock()
			self.SetTop()
			self.Show()

		def Close(self):
			self._HideTooltip()
			self._HidePinTooltip()
			self.Hide()

		def Destroy(self):
			self._ClearSlots()
			self._HideTooltip()
			self._HidePinTooltip()
			self.tooltip = None
			self.emptyText = None
			self.bg = None
			self.loginWindow = None
			self.Hide()

		def Redock(self):
			screenW = wndMgr.GetScreenWidth()
			screenH = wndMgr.GetScreenHeight()
			if localeinfo.IsARABIC():
				x = screenW - LOGIN_PANEL_WIDTH - self._stripW - self.PANEL_GAP
				y = self.STRIP_TOP_Y
			else:
				x = (screenW - self._stripW) / 2
				y = (screenH - self._stripH) / 2
			if x < 0:
				x = 0
			if y < 0:
				y = 0
			self.SetPosition(x, y)

		def _ClearSlots(self):
			for slotDict in self.slotWidgets:
				for key, widget in slotDict.items():
					if widget:
						widget.Hide()
			self.slotWidgets = []

		def RefreshSlots(self):
			self._ClearSlots()

			if self.emptyText:
				self.emptyText.Hide()
				self.emptyText = None

			flm = FastLoginManager.GetInstance()
			chars = flm.GetRecentCharacters()

			numSlots = len(chars)
			if numSlots == 0:
				self._stripH = self.STRIP_TOP + 34 + self.STRIP_BOTTOM
			else:
				self._stripH = self.STRIP_TOP + numSlots * (self.TILE_H + self.TILE_SPACING) - self.TILE_SPACING + self.STRIP_BOTTOM

			self._stripW = self.TILE_W + self.STRIP_PAD * 2
			self.SetSize(self._stripW, self._stripH)
			if self.bg:
				self.bg.SetSize(self._stripW, self._stripH)

			if not chars:
				self.emptyText = ui.TextLine()
				self.emptyText.SetParent(self)
				self.emptyText.SetPosition(self._stripW / 2, self._stripH / 2 - 6)
				self.emptyText.SetHorizontalAlignCenter()
				self.emptyText.SetText(localeinfo.QUICK_LOGIN_NOSAVED_YET)
				self.emptyText.SetPackedFontColor(self.COLOR_EMPTY)
				self.emptyText.AddFlag("not_pick")
				self.emptyText.Show()
				if self.IsShow():
					self.Redock()
				return

			for idx, charData in enumerate(chars):
				self._CreateSlot(idx, charData)

			if self.IsShow():
				self.Redock()

		def _CreateSlot(self, idx, charData):
			xPos = self.STRIP_PAD
			yPos = self.STRIP_TOP + idx * (self.TILE_H + self.TILE_SPACING)

			container = ui.Window()
			container.SetParent(self)
			container.SetPosition(xPos, yPos)
			container.SetSize(self.TILE_W, self.TILE_H)
			container.Show()

			isPinned = charData.get("pinned", False)
			faceX = (self.TILE_W - self.FACE_FRAME) / 2

			bgBar = ui.Bar()
			bgBar.SetParent(container)
			bgBar.SetPosition(0, 0)
			bgBar.SetSize(self.TILE_W, self.TILE_H)
			bgBar.SetColor(self.COLOR_SLOT_BG)
			bgBar.Show()

			faceFrame = ui.ImageBox()
			faceFrame.SetParent(container)
			faceFrame.AddFlag("not_pick")
			faceFrame.SetPosition(faceX, 4)
			try:
				faceFrame.LoadImage(NEW_LOGIN_PATH + "facebg.png")
			except:
				pass
			faceFrame.Show()

			faceIcon = ui.ImageBox()
			faceIcon.SetParent(container)
			faceIcon.AddFlag("not_pick")
			faceIcon.SetPosition(faceX, 4)
			facePath = FastLoginManager.GetFacePath(charData["race"])
			if facePath:
				try:
					faceIcon.LoadImage(facePath)
				except:
					pass
			faceIcon.Show()

			nameText = ui.TextLine()
			nameText.SetParent(container)
			nameText.SetPosition(self.TILE_W / 2, self.FACE_FRAME + 9)
			nameText.SetHorizontalAlignCenter()
			nameText.SetText(charData["name"])
			nameText.SetPackedFontColor(self.COLOR_NAME)
			nameText.SetOutline()
			nameText.AddFlag("not_pick")
			nameText.Show()

			favIcon = ui.ImageBox()
			favIcon.SetParent(container)
			favIcon.SetPosition(2, 2)
			if isPinned:
				favIcon.LoadImage("dragon3/login/quick_fav.png")
			else:
				favIcon.LoadImage("dragon3/login/quick_nonfav.png")
			favIcon.OnMouseLeftButtonUp = lambda acc=charData["account"], sl=charData["slot"]: self._OnClickPin(acc, sl)
			favIcon.OnMouseOverIn = lambda: self._ShowPinTooltip()
			favIcon.OnMouseOverOut = lambda: self._HidePinTooltip()
			favIcon.Show()

			deleteBtn = ui.Button()
			deleteBtn.SetParent(container)
			deleteBtn.SetPosition(self.TILE_W - 20, 2)
			deleteBtn.SetUpVisual(NEW_LOGIN_PATH + "delete_acc_01.png")
			deleteBtn.SetOverVisual(NEW_LOGIN_PATH + "delete_acc_02.png")
			deleteBtn.SetDownVisual(NEW_LOGIN_PATH + "delete_acc_03.png")
			deleteBtn.SetEvent(lambda acc=charData["account"], sl=charData["slot"]: self._OnClickDelete(acc, sl))
			deleteBtn.Show()

			bgBar.OnMouseLeftButtonUp = lambda cd=charData: self._OnClickSlot(cd)
			bgBar.OnMouseOverIn = lambda bg=bgBar, cd=charData, i=idx: self._OnSlotHoverIn(bg, cd, i)
			bgBar.OnMouseOverOut = lambda bg=bgBar: self._OnSlotHoverOut(bg)

			self.slotWidgets.append({
				"container": container,
				"bgBar": bgBar,
				"faceFrame": faceFrame,
				"faceIcon": faceIcon,
				"nameText": nameText,
				"favIcon": favIcon,
				"deleteBtn": deleteBtn,
			})

		def _OnSlotHoverIn(self, bgBar, charData, idx):
			bgBar.SetColor(self.COLOR_SLOT_HOVER)
			self._ShowTooltip(charData, idx)

		def _OnSlotHoverOut(self, bgBar):
			bgBar.SetColor(self.COLOR_SLOT_BG)
			self._HideTooltip()

		def _ShowPinTooltip(self):
			self._HidePinTooltip()
			self._HideTooltip()

			tipText = getattr(localeinfo, 'QUICK_LOGIN_PIN_TIP', "Pins on top, never auto-deleted")

			tp = ui.ThinBoard("UI", 2)
			tp.AddFlag("float")
			tp.AddFlag("not_pick")

			textLine = ui.TextLine()
			textLine.SetParent(tp)
			textLine.SetPosition(160, 8)
			textLine.SetText(tipText)
			textLine.SetHorizontalAlignCenter()
			textLine.SetPackedFontColor(0xFFFAD388)
			textLine.SetOutline()
			textLine.Show()

			textWidth = len(tipText) * 7
			tp.SetSize(max(textWidth + 20, 180), 28)

			mx, my = wndMgr.GetMousePosition()
			tp.SetPosition(mx + 15, my + 15)
			tp.Show()

			self.pinTooltip = tp
			self._pinTooltipChildren = [textLine]

		def _HidePinTooltip(self):
			if self.pinTooltip:
				self.pinTooltip.Hide()
				self.pinTooltip = None
			self._pinTooltipChildren = []

		def _ShowTooltip(self, charData, idx=0):
			self._HideTooltip()
			self._HidePinTooltip()

			TOOLTIP_WIDTH = 250
			LINE_HEIGHT = 25
			PADDING = 10

			tp = ui.ThinBoard("UI", 2)
			tp.AddFlag("float")
			tp.AddFlag("not_pick")
			tp.Show()

			yOff = PADDING

			nameText = ui.TextLine()
			nameText.SetParent(tp)
			nameText.SetPosition(TOOLTIP_WIDTH / 2, yOff)
			nameText.SetHorizontalAlignCenter()
			nameText.SetFontName("Tahoma:14")
			nameText.SetText("Lv.%d %s" % (charData["level"], charData["name"]))
			nameText.SetPackedFontColor(self.COLOR_NAME)
			nameText.SetOutline()
			nameText.Show()
			yOff += LINE_HEIGHT + 2

			isArabic = localeinfo.IsARABIC()
			guildName = charData["guild"] if charData["guild"] else localeinfo.QUICK_LOGIN_NOGUILD
			guildLabel = ui.TextLine()
			guildLabel.SetParent(tp)
			guildLabel.SetPackedFontColor(self.COLOR_INFO)
			guildLabel.SetOutline()
			guildLabel.SetText(localeinfo.QUICK_LOGIN_GUILD)
			guildLabel.Show()

			guildValue = ui.TextLine()
			guildValue.SetParent(tp)
			guildValue.SetPackedFontColor(self.COLOR_NAME)
			guildValue.SetOutline()
			guildValue.SetText(guildName)
			guildValue.SetHorizontalAlignCenter()
			guildValue.Show()

			if isArabic:
				guildLabel.SetPosition(TOOLTIP_WIDTH - PADDING, yOff)
				guildValue.SetPosition(TOOLTIP_WIDTH / 2 - PADDING + 10, yOff)
			else:
				guildLabel.SetPosition(PADDING, yOff)
				guildValue.SetPosition(TOOLTIP_WIDTH / 2 + PADDING, yOff)
			yOff += LINE_HEIGHT

			empireID = charData.get("empire", 0)
			empireLabel = ui.TextLine()
			empireLabel.SetParent(tp)
			empireLabel.SetPackedFontColor(self.COLOR_INFO)
			empireLabel.SetOutline()
			empireLabel.SetText(localeinfo.QUICK_LOGIN_EMPIRE)
			empireLabel.Show()

			if isArabic:
				empireLabel.SetPosition(TOOLTIP_WIDTH - PADDING, yOff)
			else:
				empireLabel.SetPosition(PADDING, yOff)

			flagPath = self.EMPIRE_FLAG.get(empireID, "")
			if flagPath:
				flagIcon = ui.ImageBox()
				flagIcon.SetParent(tp)
				if isArabic:
					flagIcon.SetPosition(TOOLTIP_WIDTH / 2 - PADDING, yOff)
				else:
					flagIcon.SetPosition(TOOLTIP_WIDTH / 2 + PADDING, yOff)
				try:
					flagIcon.LoadImage(flagPath)
					flagIcon.SetScale(0.45, 0.45)
				except:
					pass
				flagIcon.Show()
			else:
				flagIcon = None
			yOff += LINE_HEIGHT + 4

			hintLine = ui.TextLine()
			hintLine.SetParent(tp)
			hintLine.SetPosition(TOOLTIP_WIDTH / 2, yOff)
			hintLine.SetHorizontalAlignCenter()
			hintLine.SetText(localeinfo.QUICK_LOGIN_TOOTIP)
			hintLine.SetPackedFontColor(0xFF60C060)
			hintLine.SetOutline()
			hintLine.Show()
			yOff += LINE_HEIGHT

			shortcutLine = ui.TextLine()
			shortcutLine.SetParent(tp)
			shortcutLine.SetPosition(TOOLTIP_WIDTH / 2, yOff)
			shortcutLine.SetHorizontalAlignCenter()
			shortcutLine.SetText("Ctrl+F%d" % (idx + 1))
			shortcutLine.SetPackedFontColor(0xFF60C060)
			shortcutLine.SetOutline()
			shortcutLine.Show()
			yOff += LINE_HEIGHT + PADDING - 4

			tp.SetSize(TOOLTIP_WIDTH, yOff)

			mx, my = wndMgr.GetMousePosition()
			tp.SetPosition(mx + 15, my + 15)

			self.tooltip = tp
			self._tooltipChildren = [nameText, guildLabel, guildValue, empireLabel, hintLine, shortcutLine]
			if flagIcon:
				self._tooltipChildren.append(flagIcon)

		def _HideTooltip(self):
			if self.tooltip:
				self.tooltip.Hide()
				self.tooltip = None
			self._tooltipChildren = []

		def _OnClickSlot(self, charData):
			if not self.loginWindow:
				return
			self._ConnectFast(charData)

		def _ConnectFast(self, charData):
			if self.loginWindow:
				self.loginWindow._LoginWindow__ShowFastLoginOverlay()
			constinfo.FAST_LOGIN_ATTEMPTED = True
			currentChannel = getattr(constinfo, 'SELECTED_CHANNEL', charData["channel"])
			# >>> BEGIN - fast login must not override server.inf; server identity is per-install (disabled)
			# self.loginWindow.SelectServer(charData["server"])
			# <<< END
			self.loginWindow.SetChannel(currentChannel)
			constinfo.SELECTED_CHANNEL = currentChannel
			self.loginWindow.stream.SetCharacterSlot(int(charData["slot"]))
			constinfo.FAST_LOGIN_AUTO_SLOT = int(charData["slot"])
			constinfo.FAST_LOGIN_PENDING_PWD = charData["password"]
			self.loginWindow.Connect(charData["account"], charData["password"])
			self.Close()

		def _OnClickPin(self, account, slot):
			flm = FastLoginManager.GetInstance()
			flm.TogglePin(account, slot)
			self.RefreshSlots()

		def _OnClickDelete(self, account, slot):
			flm = FastLoginManager.GetInstance()
			flm.DeleteEntry(account, slot)
			self.RefreshSlots()

class ConnectingDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__LoadDialog()
		self.eventTimeOver = lambda *arg: None
		self.eventExit = lambda *arg: None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadDialog(self):
		try:
			PythonScriptLoader = ui.PythonScriptLoader()
			PythonScriptLoader.LoadScriptFile(self, "uiscript/connectingdialog.py")

			self.board = self.GetChild("board")
			self.message = self.GetChild("message")
			self.countdownMessage = self.GetChild("countdown_message")

		except:
			import exception
			exception.Abort("ConnectingDialog.LoadDialog.BindObject")

	def Open(self, waitTime):
		curTime = time.clock()
		self.endTime = curTime + waitTime

		self.Lock()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.Unlock()
		self.Hide()

	def Destroy(self):
		self.Hide()
		self.ClearDictionary()

	def SetText(self, text):
		self.message.SetText(text)

	def SetCountDownMessage(self, waitTime):
		self.countdownMessage.SetText("%.0f%s" % (waitTime, localeinfo.SECOND))

	def SAFE_SetTimeOverEvent(self, event):
		self.eventTimeOver = ui.__mem_func__(event)

	def SAFE_SetExitEvent(self, event):
		self.eventExit = ui.__mem_func__(event)

	def OnUpdate(self):
		lastTime = max(0, self.endTime - time.clock())
		if 0 == lastTime:
			self.Close()
			self.eventTimeOver()
		else:
			self.SetCountDownMessage(self.endTime - time.clock())

	def OnPressExitKey(self):
		# self.eventExit()
		return True

class LoginScrollBar(ui.Window):
	def __init__(self, layer = "UI"):
		ui.Window.__init__(self, layer)
		self.curPos = 0.0
		self.pageSize = 1
		self.scrollStep = 0.2
		self.eventScroll = lambda *arg: None
		self.base = None
		self.thumb = None

	def __del__(self):
		ui.Window.__del__(self)

	def Make(self, basePath, thumbPath, trackHeight):
		self.SetSize(10, trackHeight)

		base = ui.ExpandedImageBox()
		base.SetParent(self)
		base.AddFlag("not_pick")
		base.LoadImage(basePath)
		nativeH = base.GetHeight()
		if nativeH > 0:
			base.SetScale(1.0, float(trackHeight) / float(nativeH))
		base.SetPosition(0, 0)
		base.Show()
		self.base = base

		thumb = ui.DragButton()
		thumb.SetParent(self)
		thumb.AddFlag("movable")
		thumb.SetUpVisual(thumbPath)
		thumb.SetOverVisual(thumbPath)
		thumb.SetDownVisual(thumbPath)
		thumbH = thumb.GetHeight()
		thumbW = thumb.GetWidth()
		self.pageSize = max(1, trackHeight - thumbH)
		thumb.SetRestrictMovementArea(1, 0, thumbW, trackHeight)
		thumb.SetMoveEvent(ui.__mem_func__(self.__OnThumbMove))
		thumb.SetPosition(1, 0)
		thumb.Show()
		self.thumb = thumb

	def __OnThumbMove(self):
		if not self.thumb or self.pageSize <= 0:
			return
		x, y = self.thumb.GetLocalPosition()
		self.curPos = max(0.0, min(1.0, float(y) / float(self.pageSize)))
		self.eventScroll()

	def GetPos(self):
		return self.curPos

	def SetPos(self, pos):
		pos = max(0.0, min(1.0, pos))
		if self.thumb:
			self.thumb.SetPosition(1, int(self.pageSize * pos))
		self.__OnThumbMove()

	def SetScrollEvent(self, event):
		self.eventScroll = event

	def SetScrollStep(self, step):
		self.scrollStep = step

	def OnUp(self):
		self.SetPos(self.curPos - self.scrollStep)

	def OnDown(self):
		self.SetPos(self.curPos + self.scrollStep)

class LoginWindow(ui.ScriptWindow):
	def __init__(self, stream):
		ui.ScriptWindow.__init__(self)

		net.SetPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(self)

		self.stream = stream
		self.isDown = False
		self.fastLoginPanel = None
		self.fastLoginToggleBtn = None
		self.fastLoginAutoSaveIcon = None
		self.fastLoginAutoSaveTooltip = None
		self._autoSaveTooltipText = None
		self.fastLoginOverlay = None
		self.fastLoginOverlayAni = None
		self.panel = None
		self._lastScreenW = 0
		self._lastScreenH = 0
		self.channelSelector = None
		self.channelSelectorText = None
		self.channelSelectorDot = None
		self.channelListBg = None
		self.channelListOpen = False
		self.channelStates = {}
		self.accountMovers = []
		self.accountsViewport = None
		self.accountsContent = None
		self.accountsScroll = None
		self._accContentX = 0
		self.fkeyLabels = []

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		
		net.ClearPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(0)

	def SelectServer(self, infoID):
		if not self.btnSelectServerDict.has_key(infoID):
			infoID = 1

		if not self.btnSelectServerDict.has_key(infoID):
			return

		try:
			file = open("server.inf", "w")
			file.write("%d" % (infoID))
			file.close()
		except:
			pass

		serverinfo.infoID = infoID

		for k, v in self.btnSelectServerDict.items():
			if k == infoID:
				v.Down()
				self.GetChild("bg_syrax").Show()
				self.GetChild("bg_dragon").Hide()
			else:
				v.SetUp()
				self.GetChild("bg_syrax").Hide()
				self.GetChild("bg_dragon").Show()



		net.SetMarkServer(serverinfo.infoDict[serverinfo.infoID]["ip"], serverinfo.infoDict[serverinfo.infoID]["ch99"])
		app.SetGuildMarkPath(serverinfo.infoDict[serverinfo.infoID]["mark"])
		app.SetGuildSymbolPath(serverinfo.infoDict[serverinfo.infoID]["symbol_path"])

		ServerStateChecker.Initialize()
		ServerStateChecker.AddChannel(0, serverinfo.infoDict[serverinfo.infoID]["ip"], serverinfo.infoDict[serverinfo.infoID]["ch1"])
		ServerStateChecker.AddChannel(1, serverinfo.infoDict[serverinfo.infoID]["ip"], serverinfo.infoDict[serverinfo.infoID]["ch2"])
		ServerStateChecker.AddChannel(2, serverinfo.infoDict[serverinfo.infoID]["ip"], serverinfo.infoDict[serverinfo.infoID]["ch3"])
		ServerStateChecker.AddChannel(3, serverinfo.infoDict[serverinfo.infoID]["ip"], serverinfo.infoDict[serverinfo.infoID]["ch4"])
		ServerStateChecker.Request()

		self.SetChannel(0)

	def LoadServerID(self):
		try:
			file = open("server.inf")
			lines = file.readlines()

			if len(lines) > 0:
				tokens = lines[0].split()
				serverinfo.infoID = int(tokens[0])

			file.close()
		except:
			pass

		self.SelectServer(serverinfo.infoID)

	def Open(self):
		ServerStateChecker.Create(self)
		constinfo.FAST_LOGIN_ATTEMPTED = False

		self.loginFailureMsgDict={

			"ALREADY"	: localeinfo.LOGIN_FAILURE_ALREAY,
			"NOID"		: localeinfo.LOGIN_FAILURE_NOT_EXIST_ID,
			"WRONGPWD"	: localeinfo.LOGIN_FAILURE_WRONG_PASSWORD,
			"FULL"		: localeinfo.LOGIN_FAILURE_TOO_MANY_USER,
			"SHUTDOWN"	: localeinfo.LOGIN_FAILURE_SHUTDOWN,
			"REPAIR"	: localeinfo.LOGIN_FAILURE_REPAIR_ID,
			"BLOCK"		: localeinfo.LOGIN_FAILURE_BLOCK_ID,
			"WRONGMAT"	: localeinfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER,
			"QUIT"		: localeinfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER_TRIPLE,
			"BESAMEKEY"	: localeinfo.LOGIN_FAILURE_BE_SAME_KEY,
			"NOTAVAIL"	: localeinfo.LOGIN_FAILURE_NOT_AVAIL,
			"NOBILL"	: localeinfo.LOGIN_FAILURE_NOBILL,
			"BLKLOGIN"	: localeinfo.LOGIN_FAILURE_BLOCK_LOGIN,
			"WEBBLK"	: localeinfo.LOGIN_FAILURE_WEB_BLOCK,
			"BADSCLID"	: localeinfo.LOGIN_FAILURE_WRONG_SOCIALID,
			"AGELIMIT"	: localeinfo.LOGIN_FAILURE_SHUTDOWN_TIME,
			"VERSION"	: localeinfo.LOGIN_FAILURE_VERSION,
			"HWIDBAN"	: localeinfo.LOGIN_FAILURE_HWIDBAN,
			"DEVLIMIT"	: localeinfo.LOGIN_FAILURE_DEVICE_LIMIT,
			"OLDACC"	: localeinfo.LOGIN_FAILURE_OLDACC,
			"VERIFY"	: localeinfo.LOGIN_FAILURE_NOT_MAIL_CONFIRM,
		}

		self.loginFailureFuncDict = {
			"WRONGPWD"	: localeinfo.LOGIN_FAILURE_WRONG_PASSWORD,
			"WRONGMAT"	: localeinfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER,
			"QUIT"		: app.Exit,
		}

		self.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())
		if app.ENABLE_WINDOW_RESIZE:
			self.SetResizeDic({"size" : (Expr("SCREEN_WIDTH"), Expr("SCREEN_HEIGHT"))})
		self.SetWindowName("LoginWindow")
		self.__BuildKeyDict()

		if localeinfo.IsARABIC():
			self.__LoadScript("uiscript/loginwindow.py")
		else:
			self.__LoadScript("uiscript/loginwindow_en.py")

		if musicinfo.loginMusic != "":
			snd.SetMusicVolume(systemSetting.GetMusicVolume())
			snd.FadeInMusic("BGM/" + musicinfo.loginMusic)

		snd.SetSoundVolume(systemSetting.GetSoundVolume())

		ime.AddExceptKey(91)
		ime.AddExceptKey(93)

		self.LoadServerID()
		self.CheckAccount()
		self.questionDlg = None
		self.Show()
		app.ShowCursor()

		if getattr(app, "ENABLE_FAST_LOGIN", 0):
			app.GetHwid()

			flm = FastLoginManager.GetInstance()
			constinfo.FAST_LOGIN_AUTOSAVE = flm.GetAutoSave()

			self.fastLoginAutoSaveIcon = None
			if localeinfo.IsARABIC():
				try:
					self.fastLoginAutoSaveIcon = self.GetChild("saved_char_check")
				except:
					self.fastLoginAutoSaveIcon = None
			if not self.fastLoginAutoSaveIcon:
				self.fastLoginAutoSaveIcon = ui.ImageBox()
				self.fastLoginAutoSaveIcon.SetParent(self)
				bx, by = self.fastLoginToggleBtn.GetGlobalPosition()
				self.fastLoginAutoSaveIcon.SetPosition(bx - 20, by + 5)
				self.fastLoginAutoSaveIcon.AddFlag("float")
			self.__UpdateAutoSaveIcon()
			self.fastLoginAutoSaveIcon.SetOnMouseLeftButtonUpEvent(ui.__mem_func__(self.__ToggleFastLoginAutoSave))
			self.fastLoginAutoSaveIcon.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__ShowAutoSaveTooltip)
			self.fastLoginAutoSaveIcon.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__HideAutoSaveTooltip)
			self.fastLoginAutoSaveIcon.Show()

			self.fastLoginPanel = FastLoginPanel()
			self.fastLoginPanel.Open(self)

	def __ToggleFastLoginAutoSave(self):
		flm = FastLoginManager.GetInstance()
		current = getattr(constinfo, 'FAST_LOGIN_AUTOSAVE', True)
		newState = not current
		constinfo.FAST_LOGIN_AUTOSAVE = newState
		flm.SetAutoSave(newState)
		self.__UpdateAutoSaveIcon()

	def __UpdateAutoSaveIcon(self):
		if not getattr(self, "fastLoginAutoSaveIcon", None):
			return
		on = getattr(constinfo, 'FAST_LOGIN_AUTOSAVE', True)
		if localeinfo.IsARABIC():
			img = NEW_LOGIN_PATH + ("checked.png" if on else "unchecked.png")
		else:
			img = "d:/ymir work/ui/dungeoninfo_rework/" + ("checked_box.png" if on else "check_box.png")
		self.fastLoginAutoSaveIcon.LoadImage(img)

	def __ShowAutoSaveTooltip(self):
		self.__HideAutoSaveTooltip()
		tipText = getattr(localeinfo, 'QUICK_LOGIN_AUTOSAVE_TIP', "Auto-save account on login")
		tp = ui.ThinBoard("TOP_MOST", 2)
		tp.AddFlag("float")
		tp.AddFlag("not_pick")
		textLine = ui.TextLine()
		textLine.SetParent(tp)
		textLine.SetPosition(10, 8)
		textLine.SetText(tipText)
		textLine.SetHorizontalAlignCenter()
		textLine.SetHorizontalAlignRight()
		textLine.SetOutline()
		textLine.Show()
		tw, th = textLine.GetTextSize()
		tp.SetSize(tw + 20, th + 16)
		mx, my = wndMgr.GetMousePosition()
		tp.SetPosition(mx + 15, my + 15)
		tp.Show()
		self.fastLoginAutoSaveTooltip = tp
		self._autoSaveTooltipText = textLine

	def __HideAutoSaveTooltip(self):
		if self.fastLoginAutoSaveTooltip:
			self.fastLoginAutoSaveTooltip.Hide()
			self.fastLoginAutoSaveTooltip = None
		self._autoSaveTooltipText = None

	def __ShowFastLoginOverlay(self):
		self.__CleanFastLoginOverlay()
		screenW = wndMgr.GetScreenWidth()
		screenH = wndMgr.GetScreenHeight()

		self.fastLoginOverlay = ui.Bar("UI")
		self.fastLoginOverlay.SetParent(self)
		self.fastLoginOverlay.SetSize(screenW, screenH)
		self.fastLoginOverlay.SetPosition(0, 0)
		self.fastLoginOverlay.SetColor(0xAA000000)
		self.fastLoginOverlay.AddFlag("float")
		self.fastLoginOverlay.AddFlag("not_pick")
		self.fastLoginOverlay.Show()

		self.fastLoginOverlayAni = ui.AniImageBox()
		self.fastLoginOverlayAni.SetParent(self.fastLoginOverlay)
		self.fastLoginOverlayAni.SetDelay(4)
		for i in xrange(1, 31):
			self.fastLoginOverlayAni.AppendImage(NEW_LOGIN_PATH + "loading/frame-%d.png" % i)
		self.fastLoginOverlayAni.SetPosition(screenW / 2 - 100, screenH / 2 - 100)
		self.fastLoginOverlayAni.Show()

	def __CleanFastLoginOverlay(self):
		if self.fastLoginOverlayAni:
			self.fastLoginOverlayAni.Hide()
			self.fastLoginOverlayAni = None
		if self.fastLoginOverlay:
			self.fastLoginOverlay.Hide()
			self.fastLoginOverlay = None

	def __ReopenFastLoginStrip(self):
		if getattr(self, "fastLoginPanel", None):
			self.fastLoginPanel.Redock()
			self.fastLoginPanel.SetTop()
			self.fastLoginPanel.Show()

	def __ToggleFastLogin(self):
		if self.fastLoginPanel and self.fastLoginPanel.IsShow():
			self.fastLoginPanel.Close()
		else:
			if not self.fastLoginPanel:
				self.fastLoginPanel = FastLoginPanel()
			self.fastLoginPanel.Open(self)

	def Close(self):
		for k, v in self.btnSelectServerDict.items():
			v.SetEvent(None)

		self.btnSelectServerDict = {}

		if self.questionDlg:
			self.questionDlg.Close()
			del self.questionDlg
			self.questionDlg = None

		self.serverList					= None
		self.channelList				= None
		self.onPressKeyDict 			= None

		if musicinfo.loginMusic != "" and musicinfo.selectMusic != "":
			snd.FadeOutMusic("BGM/"+musicinfo.loginMusic)
	
		if self.stream.popupWindow:
			self.stream.popupWindow.Close()

		if self.fastLoginPanel:
			self.fastLoginPanel.Destroy()
			self.fastLoginPanel = None
		if self.fastLoginAutoSaveIcon:
			self.fastLoginAutoSaveIcon.Hide()
			self.fastLoginAutoSaveIcon = None
		self.__HideAutoSaveTooltip()
		self.__CleanFastLoginOverlay()

		self.Hide()
		app.HideCursor()
		ime.ClearExceptKey()

	def __BuildKeyDict(self):
		onPressKeyDict = {}

		onPressKeyDict[app.DIK_F1]	= lambda : self.LoadAccount(0)
		onPressKeyDict[app.DIK_F2]	= lambda : self.LoadAccount(1)
		onPressKeyDict[app.DIK_F3]	= lambda : self.LoadAccount(2)
		onPressKeyDict[app.DIK_F4]	= lambda : self.LoadAccount(3)
		onPressKeyDict[app.DIK_F5]	= lambda : self.LoadAccount(4)
		onPressKeyDict[app.DIK_F6]	= lambda : self.LoadAccount(5)
		onPressKeyDict[app.DIK_F7]	= lambda : self.LoadAccount(6)
		onPressKeyDict[app.DIK_F8]	= lambda : self.LoadAccount(7)
		onPressKeyDict[app.DIK_F9]	= lambda : self.LoadAccount(8)
		onPressKeyDict[app.DIK_F10]	= lambda : self.LoadAccount(9)
		onPressKeyDict[app.DIK_F11]	= lambda : self.LoadAccount(10)
		onPressKeyDict[app.DIK_F12]	= lambda : self.LoadAccount(11)

		self.onPressKeyDict = onPressKeyDict

	def OnKeyDown(self, key):
		if getattr(app, "ENABLE_FAST_LOGIN", 0):
			if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):
				fkeyMap = {
					app.DIK_F1: 0, app.DIK_F2: 1, app.DIK_F3: 2,
					app.DIK_F4: 3, app.DIK_F5: 4,
				}
				idx = fkeyMap.get(key, -1)
				if idx >= 0:
					self.__FastLoginByIndex(idx)
					return TRUE
		try:
			self.onPressKeyDict[key]()
		except KeyError:
			pass
		except:
			raise
		return TRUE

	def __FastLoginByIndex(self, idx):
		try:
			flm = FastLoginManager.GetInstance()
			chars = flm.GetRecentCharacters()
			if idx >= len(chars):
				return
			charData = chars[idx]
			self.__ShowFastLoginOverlay()
			if getattr(self, "fastLoginPanel", None):
				self.fastLoginPanel.Hide()
			constinfo.FAST_LOGIN_ATTEMPTED = True
			currentChannel = getattr(constinfo, 'SELECTED_CHANNEL', charData["channel"])
			# >>> BEGIN - fast login must not override server.inf; server identity is per-install (disabled)
			# self.SelectServer(charData["server"])
			# <<< END
			self.SetChannel(currentChannel)
			constinfo.SELECTED_CHANNEL = currentChannel
			self.stream.SetCharacterSlot(int(charData["slot"]))
			constinfo.FAST_LOGIN_AUTO_SLOT = int(charData["slot"])
			constinfo.FAST_LOGIN_PENDING_PWD = charData["password"]
			self.Connect(charData["account"], charData["password"])
		except:
			pass

	def OnConnectFailure(self):
		if getattr(constinfo, 'FAST_LOGIN_ATTEMPTED', False):
			constinfo.FAST_LOGIN_ATTEMPTED = False
			self.__CleanFastLoginOverlay()
			self.__ReopenFastLoginStrip()
		snd.PlaySound("sound/ui/loginfail.wav")
		self.PopupNotifyMessage(localeinfo.LOGIN_CONNECT_FAILURE, self.EmptyFunc)

	def OnHandShake(self):
		if not getattr(constinfo, 'FAST_LOGIN_ATTEMPTED', False):
			snd.PlaySound("sound/ui/loginok.wav")
			self.PopupDisplayMessage(localeinfo.LOGIN_CONNECT_SUCCESS)

	def OnLoginStart(self):
		if not getattr(constinfo, 'FAST_LOGIN_ATTEMPTED', False):
			self.PopupDisplayMessage(localeinfo.LOGIN_PROCESSING)

	def OnLoginFailure(self, error):
		if getattr(constinfo, 'FAST_LOGIN_ATTEMPTED', False):
			constinfo.FAST_LOGIN_ATTEMPTED = False
			self.__CleanFastLoginOverlay()
			self.__ReopenFastLoginStrip()
		ServerStateChecker.Request()
		try:
			loginFailureMsg = self.loginFailureMsgDict[error]
		except KeyError:

			loginFailureMsg = localeinfo.LOGIN_FAILURE_UNKNOWN  + error
		loginFailureFunc = self.loginFailureFuncDict.get(error, self.EmptyFunc)
		self.PopupNotifyMessage(loginFailureMsg, loginFailureFunc)
		snd.PlaySound("sound/ui/loginfail.wav")

	def __LoadScript(self, fileName):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, fileName)
		except:
			import exception
			exception.Abort("LoginWindow.__LoadScript.LoadObject")
		try:
			self.idEditLine			= self.GetChild("id")
			self.pwdEditLine		= self.GetChild("pwd")
			self.loginButton		= self.GetChild("login_button")

			self.btnSelectServerDict = {}
			self.btnSelectServerDict[1] = self.GetChild("newselect1")
			self.btnSelectServerDict[2] = self.GetChild("newselect2")
			self.btnSelectServerDict[1].Hide()
			self.btnSelectServerDict[2].Hide()

			self.accountsafeBoard1	= self.GetChild("BoardRight_1")
			self.accountsafeBoard2	= self.GetChild("BoardRight_2")
			self.accountsafeBoard3	= self.GetChild("BoardRight_3") # added new page to F12
			self.account_dropdown	= self.GetChild("account_dropdown")
			self.exit_button		= self.GetChild("exit_button")

			if getattr(app, "ENABLE_FAST_LOGIN", 0):
				self.fastLoginToggleBtn = self.GetChild("fast_login_btn")
				self.fastLoginToggleBtn.Hide()
			else:
				try:
					self.GetChild("fast_login_btn").Hide()
				except:
					pass

			self.channelButton = {
				0 : self.GetChild("select_btn_ch1"),
				1 : self.GetChild("select_btn_ch2"),
				2 : self.GetChild("select_btn_ch3"),
				3 : self.GetChild("select_btn_ch4")
			}

			self.accountData = {

				0 : [[self.GetChild("f1_delete_button"), self.GetChild("f1_save_button"), self.GetChild("f1_login_button")], self.GetChild("f1_account_text")],
				1 : [[self.GetChild("f2_delete_button"), self.GetChild("f2_save_button"), self.GetChild("f2_login_button")], self.GetChild("f2_account_text")],
				2 : [[self.GetChild("f3_delete_button"), self.GetChild("f3_save_button"), self.GetChild("f3_login_button")], self.GetChild("f3_account_text")],
				3 : [[self.GetChild("f4_delete_button"), self.GetChild("f4_save_button"), self.GetChild("f4_login_button")], self.GetChild("f4_account_text")],
				4 : [[self.GetChild("f5_delete_button"), self.GetChild("f5_save_button"), self.GetChild("f5_login_button")], self.GetChild("f5_account_text")],
				5 : [[self.GetChild("f6_delete_button"), self.GetChild("f6_save_button"), self.GetChild("f6_login_button")], self.GetChild("f6_account_text")],
				6 : [[self.GetChild("f7_delete_button"), self.GetChild("f7_save_button"), self.GetChild("f7_login_button")], self.GetChild("f7_account_text")],
				7 : [[self.GetChild("f8_delete_button"), self.GetChild("f8_save_button"), self.GetChild("f8_login_button")], self.GetChild("f8_account_text")],
				8 : [[self.GetChild("f9_delete_button"), self.GetChild("f9_save_button"), self.GetChild("f9_login_button")], self.GetChild("f9_account_text")],
				9 : [[self.GetChild("f10_delete_button"), self.GetChild("f10_save_button"), self.GetChild("f10_login_button")], self.GetChild("f10_account_text")],
				10: [[self.GetChild("f11_delete_button"), self.GetChild("f11_save_button"), self.GetChild("f11_login_button")], self.GetChild("f11_account_text")],
				11: [[self.GetChild("f12_delete_button"), self.GetChild("f12_save_button"), self.GetChild("f12_login_button")], self.GetChild("f12_account_text")]

			}

		except:
			import exception
			exception.Abort("LoginWindow.__LoadScript.BindObject")

		for (channelID, channelButtons) in self.channelButton.items():
				channelButtons.SetEvent(ui.__mem_func__(self.SetChannel), channelID)

		for (key, item) in list(self.accountData.items()):
			if isinstance(item[0], list):
				item[0][0].SetEvent(ui.__mem_func__(self.DeleteAccount), key)
				item[0][1].SetEvent(ui.__mem_func__(self.SaveAccount), key)
				item[0][2].SetEvent(ui.__mem_func__(self.LoadAccount), key)

		self.account_dropdown.SetEvent(ui.__mem_func__(self.SelectAccountPage))

		for k, v in self.btnSelectServerDict.items():
			v.SetEvent(ui.__mem_func__(self.SelectServer), k)

		self.exit_button.SetEvent(ui.__mem_func__(self.OnPressExitKey))

		self.accountpages = []
		self.accountpages.append(self.accountsafeBoard1)
		self.accountpages.append(self.accountsafeBoard2)
		self.accountpages.append(self.accountsafeBoard3) # added new page to F12

		self.currentPageIndex = 0
		self.accountpages[0].Show()
		self.accountpages[1].Hide()
		self.accountpages[2].Hide()

		self.bg_dragon		= self.GetChild("bg_dragon")
		self.bg_syrax		= self.GetChild("bg_syrax")
		self.GetChild("bg_syrax").Hide()

		self.idEditLine.SetReturnEvent(ui.__mem_func__(self.pwdEditLine.SetFocus))
		self.idEditLine.SetTabEvent(ui.__mem_func__(self.pwdEditLine.SetFocus))
		self.pwdEditLine.SetReturnEvent(ui.__mem_func__(self.__OnClickLoginButton))
		self.pwdEditLine.SetTabEvent(ui.__mem_func__(self.idEditLine.SetFocus))
		self.idEditLine.SetFocus()

		self.loginButton.SetEvent(ui.__mem_func__(self.__OnClickLoginButton))
		self.loginButton.EnableHoverPulse()
		self.loginButton.SetHoverPulseSpeed(1)

		if localeinfo.IsARABIC():
			self.GetChild("register_btn").SetEvent(ui.__mem_func__(self.__GoForgotPassword))
			try:
				self.GetChild("forgot_user_btn").SetEvent(ui.__mem_func__(self.__GoForgotUsername))
			except:
				pass
		else:
			self.GetChild("register_btn").SetEvent(ui.__mem_func__(self.GoRegister))

		self.GetChild("ch1_online").Hide()
		self.GetChild("ch2_online").Hide()
		self.GetChild("ch3_online").Hide()
		self.GetChild("ch4_online").Hide()

		self.panel = None
		if app.ENABLE_WINDOW_RESIZE and localeinfo.IsARABIC():
			try:
				self.panel = self.GetChild("panel")
				self.panel.SetWindowHorizontalAlignLeft()
				for bg in (self.bg_dragon, self.bg_syrax):
					if bg:
						bg.SetWindowHorizontalAlignLeft()
			except:
				self.panel = None
			self.__FitLoginLayout()

		if localeinfo.IsARABIC():
			self.__SetupAccountsScroll()
			try:
				self.channelSelector = self.GetChild("channel_selector")
				self.channelSelectorText = self.GetChild("channel_selector_text")
				self.channelSelectorDot = self.GetChild("channel_selector_dot")
				self.channelListBg = self.GetChild("channel_list_bg")
				self.channelSelector.SetEvent(ui.__mem_func__(self.__ToggleChannelList))
				self.channelListOpen = False
				self.__ApplyChannelListState()
			except:
				self.channelSelector = None

	def __ToggleChannelList(self):
		self.channelListOpen = not self.channelListOpen
		self.__ApplyChannelListState()

	def __ApplyChannelListState(self):
		if not getattr(self, "channelListBg", None):
			return
		if self.channelListOpen:
			self.channelListBg.Show()
			offset = 0
		else:
			self.channelListBg.Hide()
			offset = -CHANNEL_LIST_DELTA
		for (w, baseX, baseY) in self.accountMovers:
			w.SetPosition(baseX, baseY + offset)

	def __UpdateChannelSelector(self, channelID):
		if getattr(self, "channelSelectorText", None):
			self.channelSelectorText.SetText(self.__ChannelName(channelID))
		if getattr(self, "channelSelectorDot", None):
			if self.channelStates.get(channelID, False):
				self.channelSelectorDot.LoadImage(NEW_LOGIN_PATH + "on_image.png")
			else:
				self.channelSelectorDot.LoadImage(NEW_LOGIN_PATH + "off_image.png")

	def __ChannelName(self, channelID):
		names = {
			0 : localeinfo.PANEL_CHANNEL_1,
			1 : localeinfo.PANEL_CHANNEL_2,
			2 : localeinfo.PANEL_CHANNEL_3,
			3 : localeinfo.PANEL_CHANNEL_4,
		}
		return names.get(channelID, localeinfo.PANEL_CHANNEL_1)

	def __SetupAccountsScroll(self):
		self.accountMovers = []
		try:
			self.accountsViewport = self.GetChild("accounts_viewport")
			self.accountsContent = self.GetChild("accounts_content")
			cx, cy = self.accountsContent.GetLocalPosition()
			self._accContentX = cx
			if app.USE_CLIP_MASK:
				self.accountsContent.SetClippingMaskWindow(self.accountsViewport)
			self.accountsContent.SetPosition(cx, 0)
			self.accountsafeBoard2.Show()
			self.accountsafeBoard3.Show()
			self.accountpages = [self.accountsafeBoard1]
			if getattr(self, "account_dropdown", None):
				self.account_dropdown.Hide()
			self.accountsScroll = LoginScrollBar()
			self.accountsScroll.SetParent(self.accountsViewport)
			self.accountsScroll.Make(SCROLLBAR_BASE, SCROLLBAR_MOVE, ACC_VIEW_H)
			self.accountsScroll.SetScrollStep(float(ACC_ROW_H) / float(ACC_OVERFLOW))
			self.accountsScroll.SetScrollEvent(ui.__mem_func__(self.__OnAccountScroll))
			self.accountsScroll.SetPos(0.0)
			self.accountsScroll.SetPosition(ACC_SCROLLBAR_X, 0)
			self.accountsScroll.Show()
			self.fkeyLabels = []
			for i in xrange(12):
				row = self.accountData[i][0][2]
				lbl = ui.TextLine()
				lbl.SetParent(row)
				lbl.SetFontName("Tahoma:14")
				lbl.SetText("F%d" % (i + 1))
				lbl.SetPosition(ACC_FKEY_X, ACC_TEXT_Y)
				lbl.SetPackedFontColor(0xffd4c1a5)
				lbl.SetOutline()
				lbl.Show()
				self.fkeyLabels.append(lbl)
			vx, vy = self.accountsViewport.GetLocalPosition()
			self.accountMovers.append((self.accountsViewport, vx, vy))
		except:
			self.accountsScroll = None

	def __OnAccountScroll(self):
		if not getattr(self, "accountsContent", None) or not getattr(self, "accountsScroll", None):
			return
		raw = ACC_OVERFLOW * self.accountsScroll.GetPos()
		snapped = int(round(raw / float(ACC_ROW_H))) * ACC_ROW_H
		if snapped > ACC_OVERFLOW:
			snapped = ACC_OVERFLOW
		if snapped < 0:
			snapped = 0
		self.accountsContent.SetPosition(self._accContentX, -snapped)

	def __FitLoginLayout(self):
		if not getattr(self, "panel", None):
			return
		screenWidth = wndMgr.GetScreenWidth()
		screenHeight = wndMgr.GetScreenHeight()
		self._lastScreenW = screenWidth
		self._lastScreenH = screenHeight
		for bg in (self.bg_dragon, self.bg_syrax):
			if bg:
				bg.SetPosition(0, 0)
				bg.SetSize(screenWidth, screenHeight)
				wndMgr.SetScale(bg.hWnd, float(screenWidth) / 1920.0, float(screenHeight) / 1080.0)
		self.panel.SetPosition(screenWidth - LOGIN_PANEL_WIDTH, 0)
		self.panel.SetSize(LOGIN_PANEL_WIDTH, screenHeight)
		wndMgr.SetScale(self.panel.hWnd, 1.0, float(screenHeight) / 1080.0)

		# panel children keep a fixed y (only the bg image scales), so bottom
		# elements must be re-anchored to the panel bottom on every resize.
		try:
			ba = self.GetChild("button_area")
			bx, by = ba.GetLocalPosition()
			ba.SetPosition(bx, screenHeight - BUTTON_AREA_BOTTOM)
		except:
			pass
		try:
			r1 = self.GetChild("newselect1")
			r2 = self.GetChild("newselect2")
			rx1, ry1 = r1.GetLocalPosition()
			rx2, ry2 = r2.GetLocalPosition()
			r1.SetPosition(rx1, screenHeight - 120)
			r2.SetPosition(rx2, screenHeight - 70)
		except:
			pass

		if getattr(self, "fastLoginPanel", None) and self.fastLoginPanel.IsShow():
			self.fastLoginPanel.Redock()

	def OnUpdate(self):
		ServerStateChecker.Update()
		if app.ENABLE_WINDOW_RESIZE and getattr(self, "panel", None):
			if wndMgr.GetScreenWidth() != self._lastScreenW or wndMgr.GetScreenHeight() != self._lastScreenH:
				self.__FitLoginLayout()

	def OnRunMouseWheel(self, nLen):
		if getattr(self, "accountsScroll", None):
			if nLen > 0:
				self.accountsScroll.OnUp()
			else:
				self.accountsScroll.OnDown()
			return True
		return False

	def LoadAccount(self, key):
		if get_reg("id_%d" % key):
			self.idEditLine.SetText(str(get_reg("id_%d" % key)))
			self.pwdEditLine.SetText(str(get_reg("pwd_%d" % key)))
			self.pwdEditLine.SetFocus()
			self.__OnClickLoginButton()
		else:
			self.PopupNotifyMessage(uiscriptlocale.LOGIN_ACCOUNT_N_S)
			
	def SaveAccount(self, key):
		if get_reg("id_%d" % key):
			self.PopupNotifyMessage(uiscriptlocale.LOGIN_ACCOUNT_N_S_D)
			return
		
		if self.idEditLine.GetText() == "" or self.pwdEditLine.GetText() == "":
			self.PopupNotifyMessage(uiscriptlocale.LOGIN_ACCOUNT_SAVE)
			return
		
		set_reg("id_%d" % key, self.idEditLine.GetText())
		set_reg("pwd_%d" % key, self.pwdEditLine.GetText())
		self.PopupNotifyMessage(uiscriptlocale.LOGIN_ACCOUNT_SAVED)
		self.CheckAccount()

	def SelectAccountPage(self):
		self.accountpages[self.currentPageIndex].Hide()
		self.currentPageIndex = (self.currentPageIndex + 1) % len(self.accountpages)
		self.accountpages[self.currentPageIndex].Show()


	def CheckAccount(self):
		isArabic = localeinfo.IsARABIC()
		for i in xrange(12):
			text = self.accountData[i][1]
			if get_reg("id_%d" % i):
				if isArabic:
					text.SetText(str(get_reg("id_%d" % i)))
					text.SetHorizontalAlignCenter()
					text.SetPosition(ACC_NAME_X, ACC_TEXT_Y)
				else:
					text.SetText("F%d    %s" % (i + 1, str(get_reg("id_%d" % i))))
					text.SetHorizontalAlignRight()
					text.SetPosition(210, 8)
				text.SetPackedFontColor(0xffd4c1a5 if isArabic else 0xfff2cea7)
				self.accountData[i][0][1].Hide()
				self.accountData[i][0][0].Show()
			else:
				text.SetText(uiscriptlocale.LOGIN_ACCOUNT_EMPTY)
				if isArabic:
					text.SetHorizontalAlignCenter()
					text.SetPosition(ACC_NAME_X, ACC_TEXT_Y)
				else:
					text.SetHorizontalAlignRight()
					text.SetPosition(170, 8)
				text.SetPackedFontColor(0xffd4c1a5 if isArabic else 0xfff2cea7)
				text.SetOutline()
				self.accountData[i][0][1].Show()
				self.accountData[i][0][0].Hide()

	def DeleteAccount(self, key):
		if not self.questionDlg:
			import uicommon
			self.questionDlg = uicommon.QuestionDialog()
			self.questionDlg.SetText(uiscriptlocale.LOGIN_ACCOUNT_ASK_DELETE)
			self.questionDlg.SetCancelEvent(ui.__mem_func__(self.CancelDeleteAccount))

		self.questionDlg.SetAcceptEvent(lambda arg=key: self.AcceptDeleteAccount(arg))
		self.questionDlg.Open()

	def AcceptDeleteAccount(self, key):
		if get_reg("id_%d" % key):
			set_reg("id_%d" % key, "")
			set_reg("pwd_%d" % key, "")
			self.OnCloseQuestionDlg()
			self.PopupNotifyMessage(uiscriptlocale.LOGIN_ACCOUNT_DELETE)
		else:
			self.PopupNotifyMessage(uiscriptlocale.LOGIN_ACCOUNT_D_S)

		self.CheckAccount()

	def CancelDeleteAccount(self):
		self.OnCloseQuestionDlg()

	def OnCloseQuestionDlg(self):
		if self.questionDlg:
			self.questionDlg.Close()

	def SetChannel(self, channelID):
		for key, button in self.channelButton.items():
			if key == channelID:
				button.Down()
			else:
				button.SetUp()

		self.stream.SetConnectInfo(serverinfo.infoDict[serverinfo.infoID]["ip"], serverinfo.infoDict[serverinfo.infoID]["ch%d" % (channelID + 1)], serverinfo.infoDict[serverinfo.infoID]["ip"], serverinfo.infoDict[serverinfo.infoID]["auth"])

		serverName = serverinfo.infoDict[serverinfo.infoID]["name"]
		net.SetServerInfo(serverName.strip())
		constinfo.SELECTED_CHANNEL = channelID

		if getattr(self, "channelSelector", None):
			self.__UpdateChannelSelector(channelID)
			if self.channelListOpen:
				self.channelListOpen = False
				self.__ApplyChannelListState()

	def Connect(self, id, pwd):
		if app.USE_SEQUENCE:
			net.SetPacketSequenceMode()

		constinfo.LastAccount = id.lower()
		constinfo.FAST_LOGIN_PENDING_PWD = pwd

		self.stream.popupWindow.Close()
		if not getattr(constinfo, 'FAST_LOGIN_ATTEMPTED', False):
			self.stream.popupWindow.Open(localeinfo.LOGIN_CONNETING, self.EmptyFunc, localeinfo.UI_CANCEL)

		self.stream.SetLoginInfo(id, pwd)
		self.stream.Connect()
		
	def PopupDisplayMessage(self, msg):
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg)

	def PopupNotifyMessage(self, msg, func=0):
		if not func:
			func = self.EmptyFunc

		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, func, localeinfo.UI_OK)

	def OnPressExitKey(self):
		if self.stream.popupWindow:
			self.stream.popupWindow.Close()
		self.stream.SetPhaseWindow(0)
		return TRUE

	## SERVER STATE CHECKER
	def NotifyChannelState(self, addrKey, state, count=0):
		if state == 0:
			self.GetChild("ch%d_online" % (addrKey + 1)).Hide()
			self.GetChild("ch%d_offline" % (addrKey + 1)).Show()
		else:
			self.GetChild("ch%d_online" % (addrKey + 1)).Show()
			self.GetChild("ch%d_offline" % (addrKey + 1)).Hide()

		if getattr(self, "channelSelector", None):
			self.channelStates[addrKey] = (state != 0)
			if addrKey == getattr(constinfo, "SELECTED_CHANNEL", 0):
				self.__UpdateChannelSelector(addrKey)

	def GoRegister(self):
		return self.__OpenLoginUrl(REGISTER_LINK)

	def __GoForgotPassword(self):
		return self.__OpenLoginUrl(FORGOT_PASSWORD_LINK)

	def __GoForgotUsername(self):
		return self.__OpenLoginUrl(FORGOT_USERNAME_LINK)

	def __OpenLoginUrl(self, url):
		import os
		os.system('@echo off && explorer ' + url)
		return TRUE

	def EmptyFunc(self):
		pass

	def __OnClickLoginButton(self):
		id = self.idEditLine.GetText()
		pwd = self.pwdEditLine.GetText()

		if len(id)==0:
			self.PopupNotifyMessage(localeinfo.LOGIN_INPUT_ID, self.EmptyFunc)
			return

		if len(pwd)==0:
			self.PopupNotifyMessage(localeinfo.LOGIN_INPUT_PASSWORD, self.EmptyFunc)
			return

		self.Connect(id, pwd)
