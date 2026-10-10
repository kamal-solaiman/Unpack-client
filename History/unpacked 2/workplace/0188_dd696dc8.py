# coding: latin_1
# ENABLE_PRIVATE_INSTANCE_LOBBY
# Floating "Return to CHAOS Sanctum" HUD widget.
#
# Design:
#   ChaosReturnButton(ui.Window)  parent: float (NOT movable)
#     |- ui.Button   icon          SetEvent(__OnClick) for single left click
#     |- ui.TextLine timerLine     countdown beneath the icon
#     |- uitooltip.ToolTip(220)    rich hover tooltip
#
# Why not movable: the engine consumes BOTH MouseLeftButtonDown and Up on
# attach+movable widgets to drive drag-start / drag-end, so single-click
# never reaches Python overrides (this is why uievent.AlertImg has to use
# OnMouseLeftButtonDoubleClick to react to mouse). A regular ui.Button with
# SetEvent gives a clean single-click handler — at the cost of being
# draggable. User chose single-click over drag.

import ui
import app
if app.ENABLE_WINDOW_RESIZE:
    from resizeexpr import Expr
import net
import wndMgr
import uitooltip
import localeinfo

IMG_PATH  = "d:/ymir work/ui/"
IMG_NORM  = "rejoin_norm.png"
IMG_HOVER = "rejoin_hover.png"
IMG_DOWN  = "rejoin_down.png"

MARGIN_RIGHT  = 200
MARGIN_BOTTOM = 220

ICON_W = 64
ICON_H = 64


class ChaosReturnIconButton(ui.Button):
    """ui.Button + right-click forward. Default ui.Button doesn't dispatch
    OnMouseRightButtonDown to Python overrides, so we explicitly override it
    here so the parent can wire a hide-on-right-click handler."""
    def __init__(self):
        ui.Button.__init__(self)
        self.onRightClick = None

    def SetRightClickEvent(self, cb):
        self.onRightClick = cb

    def OnMouseRightButtonDown(self):
        if self.onRightClick:
            self.onRightClick()


class ChaosReturnButton(ui.Window):
    def __init__(self):
        ui.Window.__init__(self)
        self.AddFlag("float")

        self.icon         = None
        self.timerLine    = None
        self.tooltip      = None
        self.tooltipTimer = None

        self.graceUntil = 0
        # Player-controlled hide flag. Right-clicking the button dismisses
        # the HUD for the rest of this session — server still pushes avail=1
        # every ~30s but SetAvailable respects this flag. Cleared when the
        # server pushes avail=0 (instance gone) so the next instance shows
        # the HUD again normally.
        self.userHidden = False

        self.__Build()
        self.Hide()

    def __del__(self):
        ui.Window.__del__(self)

    def __Build(self):
        # Sized to fit icon + a line of timer text underneath.
        self.SetSize(ICON_W, ICON_H + 18)

        # The clickable icon — ui.Button (NOT attach+movable, so single click works).
        # Custom subclass so we can intercept right-click for hide-on-dismiss.
        self.icon = ChaosReturnIconButton()
        self.icon.SetParent(self)
        self.icon.SetPosition(0, 0)
        self.icon.SetUpVisual(IMG_PATH + IMG_NORM)
        self.icon.SetOverVisual(IMG_PATH + IMG_HOVER)
        self.icon.SetDownVisual(IMG_PATH + IMG_DOWN)
        self.icon.SetEvent(ui.__mem_func__(self.__OnClick))
        # Custom over/out events so we can drive the rich tooltip ourselves
        # (ui.Button.SetToolTipText only gives a plain text tooltip).
        self.icon.SetOverEvent(ui.__mem_func__(self.__OnOverIn))
        self.icon.SetOverOutEvent(ui.__mem_func__(self.__OnOverOut))
        self.icon.SetRightClickEvent(ui.__mem_func__(self.__OnRightClick))
        self.icon.Show()

        # Timer text under the icon. Parented to self (the icon already lives
        # at (0,0) relative to self), so positioning is relative to self.
        timer = ui.TextLine()
        timer.SetParent(self)
        timer.SetPosition(ICON_W / 2, ICON_H + 2)
        timer.SetHorizontalAlignCenter()
        timer.SetOutline()
        timer.SetText("")
        timer.Show()
        self.timerLine = timer

        # Rich tooltip — same widget uievent uses.
        try:
            tt = uitooltip.ToolTip(220)
            tt.SetFollow(False)
            tt.ClearToolTip()
            tt.AppendTextLine(localeinfo.PIL_CHAOS_RETURN_TOOLTIP)
            tt.AppendSpace(4)
            self.tooltipTimer = tt.AppendTextLine("")
            tt.AppendSpace(4)
            try:
                tt.AppendTextLine(localeinfo.PIL_CHAOS_RIGHT_CLICK_HIDE)
            except:
                tt.AppendTextLine("Right-click to hide")
            tt.HideToolTip()
            self.tooltip = tt
        except:
            self.tooltip = None
            self.tooltipTimer = None

        self.__AnchorToScreen()

    def __AnchorToScreen(self):
        try:
            sw = wndMgr.GetScreenWidth()
            sh = wndMgr.GetScreenHeight()
        except:
            sw, sh = 1024, 768
        x = max(0, sw - self.GetWidth()  - MARGIN_RIGHT)
        y = max(0, sh - self.GetHeight() - MARGIN_BOTTOM)
        self.SetPosition(x, y)
        if app.ENABLE_WINDOW_RESIZE:
            self.SetResizeDic({"position" : (Expr("SCREEN_WIDTH") - self.GetWidth() - MARGIN_RIGHT, Expr("SCREEN_HEIGHT") - self.GetHeight() - MARGIN_BOTTOM)})

    def __OnClick(self):
        # Sends /chaos_return — server routes to OnCG_ChaosReturn which
        # warps the player back into their existing instance.
        net.SendChatPacket("/chaos_return")

    def __OnRightClick(self):
        # Player dismisses the HUD. Server keeps pushing avail=1 every ~30s
        # but we suppress it for this session. They can still re-enter by
        # using the chaos item (HandleChaosItemUse routes outside-with-active
        # to a silent rejoin), or by relogging.
        self.userHidden = True
        if self.tooltip:
            try:
                self.tooltip.HideToolTip()
            except:
                pass
        self.Hide()

    def __OnOverIn(self):
        if self.tooltip:
            try:
                self.__UpdateTooltipTimer()
                self.tooltip.SetPosition(self.GetLeft(),
                                         max(0, self.GetTop() - 70))
                self.tooltip.SetTop()
                self.tooltip.ShowToolTip()
            except:
                pass

    def __OnOverOut(self):
        if self.tooltip:
            try:
                self.tooltip.HideToolTip()
            except:
                pass

    def __UpdateTooltipTimer(self):
        if not self.tooltipTimer:
            return
        try:
            if self.graceUntil > 0:
                now = int(app.GetGlobalTimeStamp())
                remaining = max(0, self.graceUntil - now)
                mm = remaining / 60
                ss = remaining % 60
                self.tooltipTimer.SetText("Grace: %d:%02d" % (mm, ss))
                try:
                    self.tooltipTimer.SetPackedFontColor(0xFFFF6666)
                except:
                    pass
            else:
                self.tooltipTimer.SetText("Instance active")
                try:
                    self.tooltipTimer.SetPackedFontColor(0xFFFFFFFF)
                except:
                    pass
        except:
            pass

    def OnUpdate(self):
        try:
            if not self.IsShow():
                return
            self.__RefreshTimer()
            if self.tooltip and self.tooltip.IsShow():
                self.__UpdateTooltipTimer()
        except:
            pass

    def __RefreshTimer(self):
        if not self.timerLine:
            return
        if self.graceUntil <= 0:
            self.timerLine.SetText("active")
            try:
                self.timerLine.SetPackedFontColor(0xFFCCFFCC)
            except:
                pass
            return
        try:
            now = int(app.GetGlobalTimeStamp())
        except:
            now = 0
        remaining = self.graceUntil - now
        if remaining < 0:
            remaining = 0
        # Defensive hide: when grace was running and has now elapsed, the
        # instance should be dead. Server pushes avail=0 from the destroy
        # path, but cross-core RELEASE may have failed silently (we've seen
        # the HUD stay at 0:00 in the wild). Hide ourselves so the player
        # can't click into a ghost instance.
        if remaining == 0:
            self.graceUntil = 0
            if self.tooltip:
                try:
                    self.tooltip.HideToolTip()
                except:
                    pass
            self.Hide()
            return
        mm = remaining / 60
        ss = remaining % 60
        self.timerLine.SetText("%d:%02d" % (mm, ss))
        try:
            self.timerLine.SetPackedFontColor(0xFFFF6666)
        except:
            pass

    def SetAvailable(self, available, graceUntil=0):
        try:
            self.graceUntil = int(graceUntil)
        except:
            self.graceUntil = 0
        if available:
            # Respect the player's right-click dismiss for this session.
            # Internal state stays current (graceUntil updated above) so if
            # they relog the timer resumes; but the HUD doesn't reappear.
            if self.userHidden:
                return
            # Stale-state guard: server should ONLY push avail=1 with a
            # FUTURE graceUntil — eager-arm stamps grace_until the moment
            # the player exits chaos, so every legitimate push has a
            # positive countdown. If graceUntil is 0 or in the past, the
            # server's state is stale (qf.grace_until cleared while
            # qf.map_idx still points at a dead mapIdx, or a race between
            # destroy and a subsequent watchdog SendChaosReturnAvail).
            # Rendering it as green "active" text — the code path when
            # graceUntil <= 0 — leaves a permanent bogus button after
            # expiry. Hide instead and let the next legitimate push (e.g.
            # after VERIFY -> RELEASE round-trip) re-arm us.
            try:
                now = int(app.GetGlobalTimeStamp())
            except:
                now = 0
            if self.graceUntil <= 0 or self.graceUntil <= now:
                self.graceUntil = 0
                if self.tooltip:
                    try:
                        self.tooltip.HideToolTip()
                    except:
                        pass
                self.Hide()
                return
            self.__AnchorToScreen()
            try:
                self.__RefreshTimer()
            except:
                pass
            self.SetTop()
            self.Show()
        else:
            # Server says "no active instance" — instance is gone, reset the
            # user-hidden flag so the next instance shows the HUD normally.
            self.userHidden = False
            if self.tooltip:
                try:
                    self.tooltip.HideToolTip()
                except:
                    pass
            self.Hide()
