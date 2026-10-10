import app
import player
import chrmgr
import net

CTRL = 1
SHIFT = 2
ALT = 4

CAT_MOVE = 0
CAT_QUICKSLOT = 1
CAT_WINDOW = 2
CAT_SHORTCUT = 3
CAT_EMOTION = 4

CATEGORIES = (
	(CAT_MOVE, "KEYBIND_CAT_MOVE"),
	(CAT_QUICKSLOT, "KEYBIND_CAT_QUICKSLOT"),
	(CAT_WINDOW, "KEYBIND_CAT_WINDOW"),
	(CAT_SHORTCUT, "KEYBIND_CAT_SHORTCUT"),
	(CAT_EMOTION, "KEYBIND_CAT_EMOTION"),
)

class Action(object):
	__slots__ = ("id", "category", "locale", "default", "down", "up", "flag", "fixed", "slots")
	def __init__(self, id, category, locale, default=(), down=None, up=None, flag=None, fixed=False, slots=1):
		self.id = id
		self.category = category
		self.locale = locale
		self.default = default
		self.down = down
		self.up = up
		self.flag = flag
		self.fixed = fixed
		self.slots = slots

def _MoveDown(dirDik):
	def fn(g):
		player.SetSingleDIKKeyState(dirDik, True)
	return fn

def _MoveUp(dirDik):
	def fn(g):
		player.SetSingleDIKKeyState(dirDik, False)
	return fn

def _Cam(method, direction):
	def fn(g):
		getattr(app, method)(direction)
	return fn

def _Emotion(index):
	def fn(g):
		if chrmgr.IsPossibleEmoticon(-1):
			chrmgr.SetEmoticon(-1, index - 1)
			net.SendEmoticon(index - 1)
	return fn

def _Chat(cmd):
	def fn(g):
		net.SendChatPacket(cmd)
	return fn

_AR_SLOT = {0:3, 1:2, 2:1, 3:0, 4:7, 5:6, 6:5, 7:4}

def _Quick(localSlot):
	def fn(g):
		import localeinfo
		if localeinfo.IsARABIC():
			player.RequestUseLocalQuickSlot(_AR_SLOT[localSlot])
		else:
			player.RequestUseLocalQuickSlot(localSlot)
	return fn

def _Page(pageIdx):
	def fn(g):
		player.SetQuickPage(pageIdx)
	return fn

def _DoPickup(g):
	if getattr(app, "ENABLE_QUICK_PICKUP", 0):
		player.PickAllCloseItems()
	else:
		player.PickCloseItem()

def _AttackDown(g):
	player.SetAttackKeyState(True)

def _AttackUp(g):
	player.SetAttackKeyState(False)

def _Messenger(g):
	if getattr(app, "ENABLE_COMMUNITY_SYSTEM", 0):
		g.interface.ToggleCommunityWindow()
	else:
		g.interface.ToggleMessenger()

def _MinimapUp(g):
	import miniMap
	miniMap.ScaleUp()

def _MinimapDown(g):
	import miniMap
	miniMap.ScaleDown()

def _VoiceTalkDown(g):
	app.VoiceChatStartTalking()

def _VoiceTalkUp(g):
	app.VoiceChatStopTalking()

def BuildActions():
	A = Action
	acts = [
	# CAT_MOVE - slots=2 rows (dual-bind like the reference)
	A("forwards", CAT_MOVE, "KEYBIND_FORWARDS", ((0, app.DIK_W), (0, app.DIK_UP)), _MoveDown(app.DIK_UP), _MoveUp(app.DIK_UP), slots=2),
	A("backwards", CAT_MOVE, "KEYBIND_BACKWARDS", ((0, app.DIK_S), (0, app.DIK_DOWN)), _MoveDown(app.DIK_DOWN), _MoveUp(app.DIK_DOWN), slots=2),
	A("left", CAT_MOVE, "KEYBIND_LEFT", ((0, app.DIK_A), (0, app.DIK_LEFT)), _MoveDown(app.DIK_LEFT), _MoveUp(app.DIK_LEFT), slots=2),
	A("right", CAT_MOVE, "KEYBIND_RIGHT", ((0, app.DIK_D), (0, app.DIK_RIGHT)), _MoveDown(app.DIK_RIGHT), _MoveUp(app.DIK_RIGHT), slots=2),
	A("camera_right", CAT_MOVE, "KEYBIND_CAM_RIGHT", ((0, app.DIK_E), (0, app.DIK_NUMPAD6)), _Cam("RotateCamera", app.CAMERA_TO_POSITIVE), _Cam("RotateCamera", app.CAMERA_STOP), slots=2),
	A("camera_left", CAT_MOVE, "KEYBIND_CAM_LEFT", ((0, app.DIK_Q), (0, app.DIK_NUMPAD4)), _Cam("RotateCamera", app.CAMERA_TO_NEGATIVE), _Cam("RotateCamera", app.CAMERA_STOP), slots=2),
	A("camera_zoom_in", CAT_MOVE, "KEYBIND_CAM_ZOOM_IN", ((0, app.DIK_R), (0, app.DIK_PGUP)), _Cam("ZoomCamera", app.CAMERA_TO_NEGATIVE), _Cam("ZoomCamera", app.CAMERA_STOP), slots=2),
	A("camera_zoom_out", CAT_MOVE, "KEYBIND_CAM_ZOOM_OUT", ((0, app.DIK_F), (0, app.DIK_PGDN)), _Cam("ZoomCamera", app.CAMERA_TO_POSITIVE), _Cam("ZoomCamera", app.CAMERA_STOP), slots=2),
	A("camera_down", CAT_MOVE, "KEYBIND_CAM_DOWN", ((0, app.DIK_T), (0, app.DIK_NUMPAD8)), _Cam("PitchCamera", app.CAMERA_TO_NEGATIVE), _Cam("PitchCamera", app.CAMERA_STOP), slots=2),
	A("camera_up", CAT_MOVE, "KEYBIND_CAM_UP", ((0, app.DIK_G), (0, app.DIK_NUMPAD2)), _Cam("PitchCamera", app.CAMERA_TO_POSITIVE), _Cam("PitchCamera", app.CAMERA_STOP), slots=2),
	A("pickup", CAT_MOVE, "KEYBIND_PICKUP", ((0, app.DIK_GRAVE), (0, app.DIK_Z)), _DoPickup, None, slots=2),
	A("attack", CAT_MOVE, "KEYBIND_ATTACK", ((0, app.DIK_SPACE),), _AttackDown, _AttackUp),
	A("auto_run", CAT_MOVE, "KEYBIND_AUTORUN", ((0, app.DIK_NUMLOCK),), lambda g: g.MoveUp()),
	A("next_target", CAT_MOVE, "KEYBIND_NEXT_TARGET", (), None, None, flag=None, fixed=True),  # display-only "TAB": C++ hook owns it (no Python binding)
	A("show_names", CAT_MOVE, "KEYBIND_SHOW_NAMES", (), None, None, fixed=True),  # display-only row: "ALT"
	# CAT_QUICKSLOT
	A("quick_1", CAT_QUICKSLOT, "KEYBIND_QUICK1", ((0, app.DIK_1),), _Quick(0)),
	A("quick_2", CAT_QUICKSLOT, "KEYBIND_QUICK2", ((0, app.DIK_2),), _Quick(1)),
	A("quick_3", CAT_QUICKSLOT, "KEYBIND_QUICK3", ((0, app.DIK_3),), _Quick(2)),
	A("quick_4", CAT_QUICKSLOT, "KEYBIND_QUICK4", ((0, app.DIK_4),), _Quick(3)),
	A("quick_5", CAT_QUICKSLOT, "KEYBIND_QUICK5", ((0, app.DIK_F1),), _Quick(4)),
	A("quick_6", CAT_QUICKSLOT, "KEYBIND_QUICK6", ((0, app.DIK_F2),), _Quick(5)),
	A("quick_7", CAT_QUICKSLOT, "KEYBIND_QUICK7", ((0, app.DIK_F3),), _Quick(6)),
	A("quick_8", CAT_QUICKSLOT, "KEYBIND_QUICK8", ((0, app.DIK_F4),), _Quick(7)),
	A("quick_page_1", CAT_QUICKSLOT, "KEYBIND_QPAGE1", ((SHIFT, app.DIK_1),), _Page(0)),
	A("quick_page_2", CAT_QUICKSLOT, "KEYBIND_QPAGE2", ((SHIFT, app.DIK_2),), _Page(1)),
	A("quick_page_3", CAT_QUICKSLOT, "KEYBIND_QPAGE3", ((SHIFT, app.DIK_3),), _Page(2)),
	A("quick_page_4", CAT_QUICKSLOT, "KEYBIND_QPAGE4", ((SHIFT, app.DIK_4),), _Page(3)),
	# CAT_WINDOW  (labels must say what actually opens - audit found 5 stale labels)
	A("character", CAT_WINDOW, "KEYBIND_CHARACTER", ((0, app.DIK_C),), lambda g: g.interface.ToggleCharacterWindow("STATUS")),
	A("skills", CAT_WINDOW, "KEYBIND_SKILLS", ((0, app.DIK_V),), lambda g: g.interface.ToggleCharacterWindow("SKILL")),
	A("quests", CAT_WINDOW, "KEYBIND_QUESTS", ((0, app.DIK_N),), lambda g: g.interface.ToggleCharacterWindow("QUEST")),
	A("inventory", CAT_WINDOW, "KEYBIND_INVENTORY", ((0, app.DIK_I),), lambda g: g.interface.ToggleInventoryWindow()),
	A("dragon_soul", CAT_WINDOW, "KEYBIND_DRAGON_SOUL", ((0, app.DIK_O),), lambda g: g.interface.ToggleDragonSoulWindowWithNoInfo(), flag="ENABLE_DRAGON_SOUL_SYSTEM"),
	A("large_map", CAT_WINDOW, "KEYBIND_LARGE_MAP", ((0, app.DIK_M),), lambda g: g.interface.ToggleMiniMap()),
	A("chat_log", CAT_WINDOW, "KEYBIND_CHAT_LOG", ((0, app.DIK_L),), lambda g: g.interface.ToggleChatLogWindow()),
	A("guild", CAT_WINDOW, "KEYBIND_GUILD", ((ALT, app.DIK_G),), lambda g: g.interface.ToggleGuildWindow()),
	A("friends", CAT_WINDOW, "KEYBIND_FRIENDS", ((ALT, app.DIK_M),), _Messenger),
	A("wiki", CAT_WINDOW, "KEYBIND_WIKI", ((0, app.DIK_H),), lambda g: g.interface.ToggleWikiWindow(), flag="ENABLE_INGAME_WIKI"),
	A("actions", CAT_WINDOW, "KEYBIND_ACTIONS", ((0, app.DIK_B),), lambda g: g.interface.ToggleCharacterWindow("EMOTICON")),
	A("switchbot", CAT_WINDOW, "KEYBIND_SWITCHBOT", ((0, app.DIK_F5),), lambda g: g.interface.ToggleSwitchbotWindow(), flag="ENABLE_SWITCHBOT"),
	A("pet", CAT_WINDOW, "KEYBIND_PET", ((0, app.DIK_P),), lambda g: g.interface.TogglePetInformationWindow(), flag="ENABLE_GROWTH_PET_SYSTEM"),
	A("special_inventory", CAT_WINDOW, "KEYBIND_SPECIAL_INV", ((0, app.DIK_K),), lambda g: g.interface.ToggleSpecialInventoryWindow(), flag="ENABLE_SPECIAL_INVENTORY_SYSTEM"),
	A("dungeons", CAT_WINDOW, "KEYBIND_DUNGEONS", ((0, app.DIK_F6),), lambda g: g.interface.ToggleDungeonInfo(), flag="USE_DUNGEON_INFO"),
	A("world_boss", CAT_WINDOW, "KEYBIND_WORLD_BOSS", ((0, app.DIK_F7),), lambda g: g.interface.OpenWorldBossWindow(), flag="ENABLE_ULTIMATE_REGEN"),
	A("search_shop", CAT_WINDOW, "KEYBIND_SEARCH_SHOP", ((0, app.DIK_F9),), lambda g: g.OpenSearchShop(), flag="USE_OFFLINESHOP"),
	A("battlepass", CAT_WINDOW, "KEYBIND_BATTLEPASS", ((0, app.DIK_F10),), lambda g: g.interface.ShowBattlePass(), flag="ADVANCED_BATTLE_PASS"),
	A("companion", CAT_WINDOW, "KEYBIND_COMPANION", ((0, app.DIK_U),), lambda g: g.interface.ToggleCompanion(), flag="__BUFFI_SUPPORT__"),
	A("biologist", CAT_WINDOW, "KEYBIND_BIOLOGIST", ((0, app.DIK_Y),), lambda g: g.interface.ToggleMissionQuest(), flag="ENABLE_MISSION_QUEST"),
	A("horse", CAT_WINDOW, "KEYBIND_HORSE", (), lambda g: g.interface.ToggleCompanionRidePage(), flag="__BUFFI_SUPPORT__"),
	A("event_calendar", CAT_WINDOW, "KEYBIND_EVENT_CALENDAR", (), lambda g: g.interface.ToggleInGameEvent(), flag="ENABLE_EVENT_MANAGER"),
	A("rewards", CAT_WINDOW, "KEYBIND_REWARDS", (), lambda g: g.interface.OpenRewardWindow(), flag="ENABLE_REWARD_SYSTEM"),
	A("notifications", CAT_WINDOW, "KEYBIND_NOTIFICATIONS", (), lambda g: g.interface.ToggleNotificationHistory(), flag="ENABLE_NOTIFICATION_SYSTEM"),
	A("saryong_story", CAT_WINDOW, "KEYBIND_SARYONG", (), lambda g: g.interface.ToggleStoryWindow()),
	A("offline_shop", CAT_WINDOW, "KEYBIND_OFFLINESHOP", (), lambda g: g.interface.OpenOfflineShop(), flag="USE_OFFLINESHOP"),
	A("ranking", CAT_WINDOW, "KEYBIND_RANKING", (), lambda g: g.interface.OpenRanking(), flag="__RANKING_SYSTEM__"),
	A("fast_equip", CAT_WINDOW, "KEYBIND_FAST_EQUIP", (), lambda g: g.interface.OpenFastEquip(), flag="FAST_EQUIP_WORLDARD"),
	A("key_settings", CAT_WINDOW, "KEYBIND_KEY_SETTINGS", (), lambda g: g.OpenKeyChangeWindow()),
	A("voice_chat", CAT_WINDOW, "KEYBIND_VOICE_CHAT", (), lambda g: g.interface.ToggleVoiceChatConfigWindow(), flag="ENABLE_VOICE_CHAT"),
	# CAT_SHORTCUT
	A("quest_scrolls", CAT_SHORTCUT, "KEYBIND_QUEST_SCROLLS", ((CTRL, app.DIK_Q),), lambda g: g.ScrollOnOff()),
	A("channel_switch", CAT_SHORTCUT, "KEYBIND_CHANNEL_SWITCH", ((0, app.DIK_X),), lambda g: g.interface.ToggleChangeCH(), flag="USE_INGAME_CHANGE_CHANNEL"),
	A("minimap_plus", CAT_SHORTCUT, "KEYBIND_MINIMAP_PLUS", ((0, app.DIK_ADD),), _MinimapUp),
	A("minimap_minus", CAT_SHORTCUT, "KEYBIND_MINIMAP_MINUS", ((0, app.DIK_SUBTRACT),), _MinimapDown),
	A("screenshot", CAT_SHORTCUT, "KEYBIND_SCREENSHOT", ((0, app.DIK_SYSRQ),), lambda g: g.SaveScreen()),
	A("ride_horse", CAT_SHORTCUT, "KEYBIND_RIDE_HORSE", ((CTRL, app.DIK_G),), _Chat("/ride")),
	A("ride_my_horse", CAT_SHORTCUT, "KEYBIND_RIDE_MY_HORSE", ((CTRL, app.DIK_H),), _Chat("/user_horse_ride")),
	A("feed_horse", CAT_SHORTCUT, "KEYBIND_FEED_HORSE", ((CTRL, app.DIK_F),), _Chat("/user_horse_feed")),
	A("dismiss_horse", CAT_SHORTCUT, "KEYBIND_DISMISS_HORSE", ((CTRL, app.DIK_B),), _Chat("/user_horse_back")),
	A("cape_activate", CAT_SHORTCUT, "KEYBIND_CAPE_ON", ((SHIFT, app.DIK_E),), lambda g: g.BINARY_Activate_Cape(), flag="__RENEWAL_BRAVE_CAPE__"),
	A("cape_deactivate", CAT_SHORTCUT, "KEYBIND_CAPE_OFF", ((CTRL, app.DIK_E),), lambda g: g.BINARY_Deactive_Cape(), flag="__RENEWAL_BRAVE_CAPE__"),
	A("potions_activate", CAT_SHORTCUT, "KEYBIND_POTIONS_ON", ((SHIFT, app.DIK_C),), _Chat("/autouse_blend_items 1")),
	A("potions_deactivate", CAT_SHORTCUT, "KEYBIND_POTIONS_OFF", ((SHIFT, app.DIK_V),), _Chat("/autouse_blend_items 0")),
	A("voice_ptt", CAT_SHORTCUT, "KEYBIND_VOICE_PTT", (), _VoiceTalkDown, _VoiceTalkUp, flag="ENABLE_VOICE_CHAT"),
	# CAT_EMOTION
	A("emotion_1", CAT_EMOTION, "KEYBIND_EMOTION1", ((CTRL, app.DIK_1),), _Emotion(1)),
	A("emotion_2", CAT_EMOTION, "KEYBIND_EMOTION2", ((CTRL, app.DIK_2),), _Emotion(2)),
	A("emotion_3", CAT_EMOTION, "KEYBIND_EMOTION3", ((CTRL, app.DIK_3),), _Emotion(3)),
	A("emotion_4", CAT_EMOTION, "KEYBIND_EMOTION4", ((CTRL, app.DIK_4),), _Emotion(4)),
	A("emotion_5", CAT_EMOTION, "KEYBIND_EMOTION5", ((CTRL, app.DIK_5),), _Emotion(5)),
	A("emotion_6", CAT_EMOTION, "KEYBIND_EMOTION6", ((CTRL, app.DIK_6),), _Emotion(6)),
	A("emotion_7", CAT_EMOTION, "KEYBIND_EMOTION7", ((CTRL, app.DIK_7),), _Emotion(7)),
	A("emotion_8", CAT_EMOTION, "KEYBIND_EMOTION8", ((CTRL, app.DIK_8),), _Emotion(8)),
	A("emotion_9", CAT_EMOTION, "KEYBIND_EMOTION9", ((CTRL, app.DIK_9),), _Emotion(9)),
	]
	out = []
	for act in acts:
		if act.flag and not getattr(app, act.flag, 0):
			continue
		out.append(act)
	return out

_DIK_NAMES = {}

def _EnsureDikNames():
	if _DIK_NAMES:
		return
	import localeinfo
	def K(name, default):
		return getattr(localeinfo, name, default)
	_DIK_NAMES[app.DIK_GRAVE] = K("KEY_GRAVE", "`")
	_DIK_NAMES[app.DIK_0] = K("KEY_0", "0")
	_DIK_NAMES[app.DIK_1] = K("KEY_1", "1")
	_DIK_NAMES[app.DIK_2] = K("KEY_2", "2")
	_DIK_NAMES[app.DIK_3] = K("KEY_3", "3")
	_DIK_NAMES[app.DIK_4] = K("KEY_4", "4")
	_DIK_NAMES[app.DIK_5] = K("KEY_5", "5")
	_DIK_NAMES[app.DIK_6] = K("KEY_6", "6")
	_DIK_NAMES[app.DIK_7] = K("KEY_7", "7")
	_DIK_NAMES[app.DIK_8] = K("KEY_8", "8")
	_DIK_NAMES[app.DIK_9] = K("KEY_9", "9")
	_DIK_NAMES[app.DIK_F1] = K("KEY_F1", "F1")
	_DIK_NAMES[app.DIK_F2] = K("KEY_F2", "F2")
	_DIK_NAMES[app.DIK_F3] = K("KEY_F3", "F3")
	_DIK_NAMES[app.DIK_F4] = K("KEY_F4", "F4")
	_DIK_NAMES[app.DIK_F5] = K("KEY_F5", "F5")
	_DIK_NAMES[app.DIK_F6] = K("KEY_F6", "F6")
	_DIK_NAMES[app.DIK_F7] = K("KEY_F7", "F7")
	_DIK_NAMES[app.DIK_F8] = K("KEY_F8", "F8")
	_DIK_NAMES[app.DIK_F9] = K("KEY_F9", "F9")
	_DIK_NAMES[app.DIK_F10] = K("KEY_F10", "F10")
	_DIK_NAMES[app.DIK_LCONTROL] = K("KEY_LCONTROL", "CTRL")
	_DIK_NAMES[app.DIK_LALT] = K("KEY_LALT", "ALT")
	_DIK_NAMES[app.DIK_LSHIFT] = K("KEY_LSHIFT", "SHIFT")
	_DIK_NAMES[app.DIK_SYSRQ] = K("KEY_SYSRQ", "PRINT SCREEN")
	_DIK_NAMES[app.DIK_SPACE] = K("KEY_SPACE", "SPACE")
	_DIK_NAMES[app.DIK_TAB] = K("KEY_TAB", "TAB")
	_DIK_NAMES[app.DIK_UP] = K("KEY_UP", "UP")
	_DIK_NAMES[app.DIK_DOWN] = K("KEY_DOWN", "DOWN")
	_DIK_NAMES[app.DIK_LEFT] = K("KEY_LEFT", "LEFT")
	_DIK_NAMES[app.DIK_RIGHT] = K("KEY_RIGHT", "RIGHT")
	_DIK_NAMES[app.DIK_Q] = K("KEY_Q", "Q")
	_DIK_NAMES[app.DIK_W] = K("KEY_W", "W")
	_DIK_NAMES[app.DIK_E] = K("KEY_E", "E")
	_DIK_NAMES[app.DIK_R] = K("KEY_R", "R")
	_DIK_NAMES[app.DIK_T] = K("KEY_T", "T")
	_DIK_NAMES[app.DIK_Y] = K("KEY_Y", "Y")
	_DIK_NAMES[app.DIK_U] = K("KEY_U", "U")
	_DIK_NAMES[app.DIK_I] = K("KEY_I", "I")
	_DIK_NAMES[app.DIK_O] = K("KEY_O", "O")
	_DIK_NAMES[app.DIK_P] = K("KEY_P", "P")
	_DIK_NAMES[app.DIK_A] = K("KEY_A", "A")
	_DIK_NAMES[app.DIK_S] = K("KEY_S", "S")
	_DIK_NAMES[app.DIK_D] = K("KEY_D", "D")
	_DIK_NAMES[app.DIK_F] = K("KEY_F", "F")
	_DIK_NAMES[app.DIK_G] = K("KEY_G", "G")
	_DIK_NAMES[app.DIK_H] = K("KEY_H", "H")
	_DIK_NAMES[app.DIK_J] = K("KEY_J", "J")
	_DIK_NAMES[app.DIK_K] = K("KEY_K", "K")
	_DIK_NAMES[app.DIK_L] = K("KEY_L", "L")
	_DIK_NAMES[app.DIK_Z] = K("KEY_Z", "Z")
	_DIK_NAMES[app.DIK_X] = K("KEY_X", "X")
	_DIK_NAMES[app.DIK_C] = K("KEY_C", "C")
	_DIK_NAMES[app.DIK_V] = K("KEY_V", "V")
	_DIK_NAMES[app.DIK_B] = K("KEY_B", "B")
	_DIK_NAMES[app.DIK_N] = K("KEY_N", "N")
	_DIK_NAMES[app.DIK_M] = K("KEY_M", "M")
	_DIK_NAMES[app.DIK_COMMA] = K("KEY_COMMA", ",")
	_DIK_NAMES[app.DIK_PERIOD] = K("KEY_PERIOD", ".")
	_DIK_NAMES[app.DIK_NUMPAD0] = K("KEY_NUMPAD0", "NUMPAD0")
	_DIK_NAMES[app.DIK_NUMPAD1] = K("KEY_NUMPAD1", "NUMPAD1")
	_DIK_NAMES[app.DIK_NUMPAD2] = K("KEY_NUMPAD2", "NUMPAD2")
	_DIK_NAMES[app.DIK_NUMPAD3] = K("KEY_NUMPAD3", "NUMPAD3")
	_DIK_NAMES[app.DIK_NUMPAD4] = K("KEY_NUMPAD4", "NUMPAD4")
	_DIK_NAMES[app.DIK_NUMPAD5] = K("KEY_NUMPAD5", "NUMPAD5")
	_DIK_NAMES[app.DIK_NUMPAD6] = K("KEY_NUMPAD6", "NUMPAD6")
	_DIK_NAMES[app.DIK_NUMPAD7] = K("KEY_NUMPAD7", "NUMPAD7")
	_DIK_NAMES[app.DIK_NUMPAD8] = K("KEY_NUMPAD8", "NUMPAD8")
	_DIK_NAMES[app.DIK_NUMPAD9] = K("KEY_NUMPAD9", "NUMPAD9")
	_DIK_NAMES[app.DIK_ADD] = K("KEY_ADD", "NUM+")
	_DIK_NAMES[app.DIK_SUBTRACT] = K("KEY_SUBTRACT", "NUM-")
	_DIK_NAMES[app.DIK_PGUP] = K("KEY_PGUP", "PGUP")
	_DIK_NAMES[app.DIK_PGDN] = K("KEY_PGDN", "PGDN")
	_DIK_NAMES[app.DIK_NUMLOCK] = K("KEY_NUMLOCK", "NUMLOCK")

def DikName(dik):
	_EnsureDikNames()
	return _DIK_NAMES.get(dik, "#%d" % dik)

_USABLE = set()

def _EnsureUsableDiks():
	if _USABLE:
		return
	_USABLE.update([
		app.DIK_GRAVE, app.DIK_0, app.DIK_1, app.DIK_2, app.DIK_3, app.DIK_4, app.DIK_5, app.DIK_6, app.DIK_7, app.DIK_8, app.DIK_9,
		app.DIK_F1, app.DIK_F2, app.DIK_F3, app.DIK_F4, app.DIK_F5, app.DIK_F6, app.DIK_F7, app.DIK_F8, app.DIK_F9, app.DIK_F10,
		app.DIK_LCONTROL, app.DIK_LALT, app.DIK_LSHIFT, app.DIK_SYSRQ, app.DIK_SPACE,
		app.DIK_UP, app.DIK_DOWN, app.DIK_LEFT, app.DIK_RIGHT,
		app.DIK_Q, app.DIK_W, app.DIK_E, app.DIK_R, app.DIK_T, app.DIK_Y, app.DIK_U, app.DIK_I, app.DIK_O, app.DIK_P,
		app.DIK_A, app.DIK_S, app.DIK_D, app.DIK_F, app.DIK_G, app.DIK_H, app.DIK_J, app.DIK_K, app.DIK_L,
		app.DIK_Z, app.DIK_X, app.DIK_C, app.DIK_V, app.DIK_B, app.DIK_N, app.DIK_M,
		app.DIK_COMMA, app.DIK_PERIOD,
		app.DIK_NUMPAD0, app.DIK_NUMPAD1, app.DIK_NUMPAD2, app.DIK_NUMPAD3, app.DIK_NUMPAD4,
		app.DIK_NUMPAD5, app.DIK_NUMPAD6, app.DIK_NUMPAD7, app.DIK_NUMPAD8, app.DIK_NUMPAD9,
		app.DIK_ADD, app.DIK_SUBTRACT, app.DIK_PGUP, app.DIK_PGDN, app.DIK_NUMLOCK,
	])

def IsBindableDik(dik):
	_EnsureUsableDiks()
	return dik in _USABLE
