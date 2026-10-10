# coding: latin_1
# ENABLE_PIL_DUNGEON
# Floating overlay shown while the server runs the dungeon Fast-Enter
# 3-second queue. State machine is server-driven; client just renders.
#
# Chat-command protocol (driven from CDungeonInfoManager::OnFastEnterTick):
#   PILFastEnter start  <index> <total_ms>
#   PILFastEnter tick   <remaining_ms>
#   PILFastEnter pause  <reason_id>
#   PILFastEnter resume
#   PILFastEnter cancel <reason_id>   (terminal)
#   PILFastEnter done                 (terminal — server then triggers warp)
#
# ESC = client sends SUBHEADER_CG_DUNGEON_INFO_FAST_ENTER_CANCEL (server then
# replies with cancel/4 which closes the overlay).

import ui
import app
if app.ENABLE_WINDOW_RESIZE:
    from resizeexpr import Expr
import chat
import wndMgr
import dungeonInfo
import localeinfo
import uitip


# Reason codes from CDungeonInfoManager — kept in lockstep with
# FE_REASON_* constants in dungeon_info_mgr.cpp. Each code maps to a
# localeinfo.PIL_FAST_ENTER_REASON_* chat string (en/ae new_locale_game.txt).
REASON_BUSY          = 1   # CanWarp() false — pause, not cancel
REASON_DEAD          = 3
REASON_ESC           = 4   # no message (player explicitly cancelled)
REASON_TIMEOUT       = 5
REASON_REJECT        = 6   # generic fallback
REASON_LEVEL         = 10
REASON_NO_ITEM       = 11
REASON_COOLDOWN      = 12
REASON_DAILY_LIMIT   = 13
REASON_NO_PARTY_LEAD = 14
REASON_CP            = 15
REASON_NO_HWID       = 16
REASON_NOT_OPEN      = 17
REASON_ALREADY       = 18
REASON_EQUIP_RESTRICT = 19
REASON_IN_INSTANCE   = 20
REASON_SAME_DEVICE   = 21


class FastEnterCountdown(ui.Window):
    BG_WIDTH  = 240
    BG_HEIGHT = 84
    MARGIN_BOTTOM = 200

    def __init__(self):
        ui.Window.__init__(self)
        self.AddFlag("float")
        self.AddFlag("animated_board")
        if app.ENABLE_WINDOW_SLIDE_EFFECT:
            self.SetAnimationScale(0.72, 1.0)
            self.SetAnimationDuration(240)
            self.SetAnimationOffset(0, 22)

        self.bg         = None
        self.titleLine  = None
        self.statusLine = None
        self.hintLine   = None
        self.lastRemainingMs = 3000

        self.__Build()
        self.Hide()

    def __del__(self):
        ui.Window.__del__(self)

    def __Build(self):
        self.SetSize(self.BG_WIDTH, self.BG_HEIGHT)

        bg = uitip.NoticeBoxBoard()
        bg.SetParent(self)
        bg.AddFlag("attach")
        bg.AddFlag("not_pick")
        bg.SetPosition(0, 0)
        bg.SetSize(self.BG_WIDTH, self.BG_HEIGHT)
        bg.Show()
        self.bg = bg

        title = ui.TextLine()
        title.SetParent(self)
        title.SetPosition(self.BG_WIDTH / 2, 8)
        title.SetHorizontalAlignCenter()
        title.SetOutline()
        title.SetText(localeinfo.PIL_FAST_ENTER_TITLE)
        title.Show()
        self.titleLine = title

        status = ui.TextLine()
        status.SetParent(self)
        status.SetPosition(self.BG_WIDTH / 2, 30)
        status.SetHorizontalAlignCenter()
        status.SetOutline()
        #status.SetFontName(localeinfo.UI_DEF_FONT_LARGE)
        status.SetText("3.0")
        status.Show()
        self.statusLine = status

        hint = ui.TextLine()
        hint.SetParent(self)
        hint.SetPosition(self.BG_WIDTH / 2, 62)
        hint.SetHorizontalAlignCenter()
        hint.SetOutline()
        hint.SetText(localeinfo.PIL_FAST_ENTER_ESC_HINT)
        hint.Show()
        self.hintLine = hint

        self.__AnchorBottomCenter()

    def __AnchorBottomCenter(self):
        try:
            sw = wndMgr.GetScreenWidth()
            sh = wndMgr.GetScreenHeight()
        except:
            sw, sh = 1024, 768
        x = max(0, (sw - self.BG_WIDTH) / 2)
        y = max(0, sh - self.BG_HEIGHT - self.MARGIN_BOTTOM)
        self.SetPosition(x, y)
        if app.ENABLE_WINDOW_RESIZE:
            self.SetResizeDic({"position" : ((Expr("SCREEN_WIDTH") - self.BG_WIDTH) / 2, Expr("SCREEN_HEIGHT") - self.BG_HEIGHT - self.MARGIN_BOTTOM)})

    # ------------------------------------------------------------------
    # Server-driven state transitions
    # ------------------------------------------------------------------
    def Start(self, dungeon_index, total_ms):
        self.lastRemainingMs = total_ms
        self.__AnchorBottomCenter()
        self.__RenderRemaining(total_ms)
        self.SetTop()
        self.Show()

    def Tick(self, remaining_ms):
        self.lastRemainingMs = remaining_ms
        self.__RenderRemaining(remaining_ms)

    def Pause(self, reason_id):
        if self.statusLine:
            self.statusLine.SetText(localeinfo.PIL_FAST_ENTER_PAUSED)
            try:
                self.statusLine.SetPackedFontColor(0xFFFFCC66)
            except:
                pass

    def Resume(self):
        # Next Tick repaints — restore normal colour now to avoid yellow flash.
        if self.statusLine:
            try:
                self.statusLine.SetPackedFontColor(0xFFFFFFFF)
            except:
                pass

    def Cancel(self, reason_id):
        self.Hide()
        msg = self.__ReasonText(reason_id)
        if msg:
            chat.AppendChat(chat.CHAT_TYPE_INFO, msg)

    def CancelName(self, reason_id, name):
        self.Hide()
        msg = self.__ReasonText(reason_id)
        if msg:
            fmt = getattr(localeinfo, "PIL_FAST_ENTER_REASON_MEMBER", "%s: %s")
            try:
                msg = fmt % (name, msg)
            except:
                msg = name + ": " + msg
            chat.AppendChat(chat.CHAT_TYPE_INFO, msg)

    def Done(self):
        # Server triggered the warp; just hide. Warp handling has its own UX.
        self.Hide()

    # ------------------------------------------------------------------
    # ESC handling
    # ------------------------------------------------------------------
    def OnPressEscapeKey(self):
        # Tell the server we want to abort. Server replies with cancel/4 which
        # routes back into Cancel() and hides us.
        dungeonInfo.FastEnterCancel()
        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def __RenderRemaining(self, ms):
        if not self.statusLine:
            return
        sec = max(0.0, ms / 1000.0)
        self.statusLine.SetText("%.1f" % sec)
        try:
            self.statusLine.SetPackedFontColor(0xFFFFFFFF)
        except:
            pass

    def __ReasonText(self, reason_id):
        # ESC = user explicitly cancelled — no chat noise.
        if reason_id == REASON_ESC:
            return None
        # All others map to localised strings. getattr fallback keeps the
        # widget resilient if a new server-side reason ships before locale.
        REASON_TO_KEY = {
            REASON_BUSY:          "PIL_FAST_ENTER_REASON_BUSY",
            REASON_DEAD:          "PIL_FAST_ENTER_REASON_DEAD",
            REASON_TIMEOUT:       "PIL_FAST_ENTER_REASON_TIMEOUT",
            REASON_REJECT:        "PIL_FAST_ENTER_REASON_REJECT",
            REASON_LEVEL:         "PIL_FAST_ENTER_REASON_LEVEL",
            REASON_NO_ITEM:       "PIL_FAST_ENTER_REASON_NO_ITEM",
            REASON_COOLDOWN:      "PIL_FAST_ENTER_REASON_COOLDOWN",
            REASON_DAILY_LIMIT:   "PIL_FAST_ENTER_REASON_DAILY_LIMIT",
            REASON_NO_PARTY_LEAD: "PIL_FAST_ENTER_REASON_NO_PARTY_LEAD",
            REASON_CP:            "PIL_FAST_ENTER_REASON_CP",
            REASON_NO_HWID:       "PIL_FAST_ENTER_REASON_NO_HWID",
            REASON_NOT_OPEN:      "PIL_FAST_ENTER_REASON_NOT_OPEN",
            REASON_ALREADY:       "PIL_FAST_ENTER_REASON_ALREADY",
            REASON_EQUIP_RESTRICT: "PIL_FAST_ENTER_REASON_EQUIP_RESTRICT",
            REASON_IN_INSTANCE:   "PIL_FAST_ENTER_REASON_IN_INSTANCE",
            REASON_SAME_DEVICE:   "PIL_FAST_ENTER_REASON_SAME_DEVICE",
        }
        FALLBACK = {
            REASON_BUSY:          "Action interrupted - try again.",
            REASON_DEAD:          "You died.",
            REASON_TIMEOUT:       "Teleport timed out.",
            REASON_REJECT:        "Cannot enter dungeon right now.",
            REASON_LEVEL:         "Your level is outside the allowed range.",
            REASON_NO_ITEM:       "You no longer have the entry item.",
            REASON_COOLDOWN:      "Dungeon cooldown is still active.",
            REASON_DAILY_LIMIT:   "Daily entry limit reached.",
            REASON_NO_PARTY_LEAD: "Only the party leader can use Fast Enter.",
            REASON_CP:            "Your combat points are too low.",
            REASON_NO_HWID:       "Account verification failed.",
            REASON_NOT_OPEN:      "This dungeon cannot be entered right now.",
            REASON_ALREADY:       "Fast Enter is already running.",
            REASON_EQUIP_RESTRICT: "An equipped item is restricted to another character for dungeon entry today.",
            REASON_IN_INSTANCE:   "Leave your current instance before entering another one.",
            REASON_SAME_DEVICE:   "Shares a device with another party member. Only one character per device can enter.",
        }
        key = REASON_TO_KEY.get(reason_id)
        if key is None:
            return None
        return getattr(localeinfo, key, FALLBACK.get(reason_id))
