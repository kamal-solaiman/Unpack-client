# Metin2 UI System - Fundamentals Guide

**Complete reference for understanding the Python UI architecture (~147,000 lines)**

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Framework Files](#core-framework-files)
3. [Python-C++ Integration](#python-c-integration)
4. [UI Window Implementation Pattern](#ui-window-implementation-pattern)
5. [Event Handling System](#event-handling-system)
6. [Widget Classes Reference](#widget-classes-reference)
7. [UI Script System](#ui-script-system)
8. [Slot System](#slot-system)
9. [Common UI Patterns](#common-ui-patterns)
10. [Best Practices](#best-practices)

---

## Architecture Overview

### High-Level Structure

```
┌─────────────────────────────────────────────────────┐
│         Python UI Layer (~147,000 lines)            │
│  ┌───────────────────────────────────────────────┐  │
│  │  game.py - Main game loop & orchestration     │  │
│  │  interfacemodule.py - Window manager          │  │
│  │  ui*.py - 122+ UI window implementations      │  │
│  └───────────────────────────────────────────────┘  │
│                        │                             │
│                Python-C++ Binding Layer              │
│                        │                             │
└────────────────────────┼─────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────┐
│         C++ Engine (UserInterface/)                  │
│  ┌───────────────────────────────────────────────┐  │
│  │  wndMgr - Window Manager (rendering)          │  │
│  │  Python Modules (player, net, chr, item, etc)│  │
│  │  DirectX 9 - Graphics rendering               │  │
│  │  Input handling - Mouse/keyboard              │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Key Principles

1. **Separation of Concerns**: UI logic in Python, rendering in C++
2. **Event-Driven**: All interactions use callback-based event system
3. **Window Hierarchy**: Parent-child relationships for UI organization
4. **Script-Based Layouts**: UI defined in Python dictionaries
5. **Modular Design**: Each window is self-contained

---

## Core Framework Files

### 1. ui.py (312KB, 9,446 lines)

**Purpose**: Base UI framework - provides all widget classes

#### Base Window Class

```python
class Window(object):
    def __init__(self, layer = "UI"):
        self.hWnd = None              # C++ window handle
        self.parentWindow = 0
        self.eventDict = {}           # Event handlers

        self.RegisterWindow(layer)    # Register with C++ wndMgr
        self.Hide()                   # Start hidden

    def RegisterWindow(self, layer):
        # Creates C++ window object, returns handle
        self.hWnd = wndMgr.Register(self, layer)
```

**Core Window Methods:**

```python
# Visibility
def Show(self): wndMgr.Show(self.hWnd)
def Hide(self): wndMgr.Hide(self.hWnd)
def IsShow(self): return wndMgr.IsShow(self.hWnd)

# Positioning
def SetPosition(self, x, y): wndMgr.SetWindowPosition(self.hWnd, x, y)
def GetGlobalPosition(self): return wndMgr.GetWindowGlobalPosition(self.hWnd)
def SetCenterPosition(self, x=0, y=0):
    centerX = (wndMgr.GetScreenWidth() - self.GetWidth()) / 2 + x
    centerY = (wndMgr.GetScreenHeight() - self.GetHeight()) / 2 + y
    self.SetPosition(centerX, centerY)

# Size
def SetSize(self, width, height): wndMgr.SetWindowSize(self.hWnd, width, height)
def GetWidth(self): return wndMgr.GetWindowWidth(self.hWnd)
def GetHeight(self): return wndMgr.GetWindowHeight(self.hWnd)

# Hierarchy
def SetParent(self, parent): wndMgr.SetParent(self.hWnd, parent.hWnd)
def GetParentProxy(self): return self.parentWindow

# Focus
def SetFocus(self): wndMgr.SetFocus(self.hWnd)
def KillFocus(self): wndMgr.KillFocus(self.hWnd)
def IsFocus(self): return wndMgr.IsFocus(self.hWnd)
```

**Event Callbacks (called by C++):**

```python
# Mouse Events
def OnMouseLeftButtonDown(self):
    if self.eventFunc["MOUSE_LEFT_BUTTON_DOWN"]:
        apply(self.eventFunc["MOUSE_LEFT_BUTTON_DOWN"],
              self.eventArgs["MOUSE_LEFT_BUTTON_DOWN"])

def OnMouseLeftButtonUp(self):
    if self.mouseLeftButtonUpEvent:
        apply(self.mouseLeftButtonUpEvent, self.mouseLeftButtonUpArgs)

def OnMouseOverIn(self):
    if self.mouseOverInEvent:
        apply(self.mouseOverInEvent, self.mouseOverInArgs)

def OnMouseOverOut(self):
    if self.mouseOverOutEvent:
        apply(self.mouseOverOutEvent, self.mouseOverOutArgs)

# Rendering
def OnRender(self):
    if self.renderEvent:
        apply(self.renderEvent, self.renderArgs)
```

#### Widget Class Hierarchy (50+ classes)

```python
# Basic Widgets
class Window               # Base class for all UI
class Button(Window)       # Clickable buttons
class ImageBox(Window)     # Display images
class TextLine(Window)     # Text display
class EditLine(TextLine)   # Text input with IME support
class Bar(Window)          # Solid color bar
class Line(Window)         # Thin line
class Box(Window)          # Outlined box

# Extended Widgets
class ExpandedImageBox(ImageBox)  # Scalable, rotatable images
class AniImageBox(Window)         # Animated images
class MoveImageBox(ImageBox)      # Moving images
class MoveTextLine(TextLine)      # Moving text

# Buttons
class RadioButton(Button)
class RadioButtonGroup            # Mutual exclusion buttons
class ToggleButton(Button)        # On/off state
class DragButton(Button)          # Draggable button

# Complex Widgets
class SlotWindow(Window)          # Inventory/skill slots
class GridSlotWindow(SlotWindow)  # Grid-based slots
class SlotBar(Window)             # 3D slot appearance
class ScrollBar(Window)           # Scrolling
class ThinScrollBar(ScrollBar)    # Thin variant
class SliderBar(Window)           # Value slider
class ListBox(Window)             # List display
class ListBoxEx(Window)           # Extended list
class ListBoxNew(Window)          # New list implementation

# Boards (Decorated Windows)
class Board(Window)               # Standard bordered panel
class ThinBoard(Window)           # Thin bordered panel
class BorderA(Window)             # Border style A
class BorderB(Board)              # Border style B
class TitleBar(Window)            # Window title bar
class TitleBarWithoutButton(Window)
class BoardWithTitleBar(Board)    # Board + title bar
class NewBoard(Window)            # New board style

# Advanced
class Gauge(Window)               # Progress bar (HP, MP, EXP)
class NumberLine(Window)          # Number display with images
class ComboBox(Window)            # Dropdown selection
class CheckBox(Window)            # Checkbox
class CandidateListBox(ListBoxEx) # IME candidate list
```

---

### 2. game.py (154KB, 4,650 lines)

**Purpose**: Main game window - orchestrates all game systems

```python
class GameWindow(ui.ScriptWindow):
    def __init__(self, stream):
        ui.ScriptWindow.__init__(self, "GAME")
        self.SetWindowName("game")

        # Register as game phase window
        net.SetPhaseWindow(net.PHASE_WINDOW_GAME, self)
        player.SetGameWindow(self)

        # Initialize core UI
        self.interface = interfacemodule.Interface()
        self.interface.MakeInterface()
        self.interface.ShowDefaultWindows()

        # Utility windows
        self.targetBoard = uitarget.TargetBoard()
        self.console = consolemodule.ConsoleWindow()
        self.mapNameShower = uimapnameshower.MapNameShower()
        self.affectShower = uiaffectshower.AffectShower()
        self.playerGauge = uiplayergauge.PlayerGauge(self)

        # Feature windows (conditional)
        if app.WHEEL_INGAME:
            self.wheelWindow = uispinwheel.WheelWindow()
        if app.ENABLE_CAPTCHA_SYSTEM:
            self.wndCaptcha = uiCaptcha.CaptchaWindow()

        # Build key bindings
        self.__BuildKeyDict()

        # Setup server command handlers
        self.__ServerCommand_Build()
```

**Key Responsibilities:**

```python
def Open(self):
    # 1. Setup rendering
    app.SetCamera(cameraDistance, cameraPitch, cameraRotation, cameraHeight)
    app.SetFrameSkip(1)

    # 2. Setup audio
    snd.SetMusicVolume(systemSetting.GetMusicVolume())
    snd.SetSoundVolume(systemSetting.GetSoundVolume())

    # 3. Start game loop
    net.SendEnterGamePacket()
    self.StartGame()

    # 4. Show UI
    self.SetFocus()
    self.Show()
    app.ShowCursor()

def Close(self):
    # Cleanup all systems
    chat.Close()
    snd.StopAllSound()
    chr.Destroy()
    textTail.Clear()
    quest.Clear()
    background.Destroy()
    guild.Destroy()
    messenger.Destroy()

    # Close all windows
    if self.interface:
        self.interface.HideAllWindows()
        self.interface.Close()
```

**Keyboard Input Handling:**

```python
def __BuildKeyDict(self):
    self.onPressKeyDict = {}

    # Number keys (quickslots)
    self.onPressKeyDict[app.DIK_1] = lambda: self.__PressNumKey(1)
    self.onPressKeyDict[app.DIK_2] = lambda: self.__PressNumKey(2)
    # ... DIK_3 through DIK_9

    # Function keys
    self.onPressKeyDict[app.DIK_F1] = lambda: self.__PressQuickSlot(4)
    self.onPressKeyDict[app.DIK_F2] = lambda: self.__PressQuickSlot(5)

    # Feature shortcuts
    if app.ENABLE_SWITCHBOT:
        self.onPressKeyDict[app.DIK_F5] = lambda: self.interface.ToggleSwitchbotWindow()

def OnKeyDown(self, key):
    if self.onPressKeyDict.has_key(key):
        self.onPressKeyDict[key]()
        return True
    return False
```

**Server Command Processing:**

```python
def __ServerCommand_Build(self):
    # Maps server commands to handler functions
    serverCommandList = {
        "PartyInvite"     : self.__PartyInvite,
        "PartyUpdate"     : self.__PartyUpdate,
        "GuildInvite"     : self.__GuildInvite,
        "ObserverCount"   : self.__ObserverCount,
        "BettingMoney"    : self.__BettingMoney,
        "OpenPrivateShop" : self.__PrivateShop_Open,
        # ... 100+ server commands
    }

    serverCommandList.update({
        "DayMode"         : self.__DayMode,
        "PRESERVE_DayMode": self.__PRESERVE_DayMode,
        "CloseRestartWindow": self.__CloseRestartWindow,
    })

    self.serverCommands = serverCommandList
```

---

### 3. interfacemodule.py (157KB, 4,730 lines)

**Purpose**: Manages all game windows and UI state

```python
class Interface(object):
    CHARACTER_STATUS_TAB = 1
    CHARACTER_SKILL_TAB = 2

    def __init__(self):
        systemSetting.SetInterfaceHandler(self)

        # Core windows
        self.wndTaskBar = None
        self.wndCharacter = None
        self.wndInventory = None
        self.wndChat = None
        self.wndMiniMap = None
        self.wndGuild = None

        # Extended windows
        self.wndExpandedTaskBar = None
        self.wndDragonSoul = None
        self.wndMessenger = None
        self.wndGuildBuilding = None

        # Feature windows (conditional)
        if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
            self.wndSpecialInventory = None
        if app.USE_OFFLINESHOP:
            self.wndShopOffline = None
        if app.ENABLE_SWITCHBOT:
            self.wndSwitchbot = None
        if app.ENABLE_MAILBOX:
            self.mail_box = None

        # Dialog windows
        self.dlgShop = None
        self.dlgExchange = None
        self.privateShopBuilder = None
        self.wndSafebox = None

        # Tooltip system
        self.tooltipItem = None
        self.tooltipSkill = None

        # Collections
        self.wndQuestWindow = {}
        self.equipmentDialogDict = {}
        self.privateShopAdvertisementBoardDict = {}
```

**Window Creation Pattern:**

```python
def MakeInterface(self):
    # 1. Create taskbar (always visible)
    self.wndTaskBar = uitaskbar.TaskBar()
    self.wndTaskBar.LoadWindow()

    # 2. Create character window
    self.wndCharacter = uicharacter.CharacterWindow()

    # 3. Create inventory
    self.wndInventory = uiinventory.InventoryWindow()
    if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
        self.wndSpecialInventory = uispecialinventory.SpecialInventoryWindow()

    # 4. Create chat window
    self.wndChat = uichat.ChatWindow()

    # 5. Create minimap
    self.wndMiniMap = uiminimap.MiniMap()

    # 6. Setup tooltips
    self.tooltipItem = uitooltip.ItemToolTip()
    self.tooltipSkill = uitooltip.SkillToolTip()

    # 7. Link windows together
    self.wndInventory.SetItemToolTip(self.tooltipItem)
    self.wndCharacter.SetItemToolTip(self.tooltipItem)
    self.wndCharacter.SetSkillToolTip(self.tooltipSkill)

    # 8. Connect taskbar to windows
    self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_CHARACTER,
                                          ui.__mem_func__(self.ToggleCharacterWindow))
    self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_INVENTORY,
                                          ui.__mem_func__(self.ToggleInventoryWindow))

def ShowDefaultWindows(self):
    # Show essential windows
    self.wndTaskBar.Show()
    self.wndMiniMap.Show()
    self.wndChat.Show()

    # Hide character/inventory initially
    self.wndCharacter.Hide()
    self.wndInventory.Hide()
```

**Gold Display System (Inner Class):**

```python
class NewGoldChat(ui.Window):
    """Displays gold gain/loss notifications"""

    def __init__(self, parent=None, x=0, y=0):
        ui.Window.__init__(self)
        self.texts = {}         # Text objects
        self.SpaceBet = 14      # Spacing between lines
        self.maxY = 0
        self.ColorValue = 0xFFffeaa7  # Gold color

        # Expand/collapse buttons
        self.show = self.Button(localeinfo.SHOW_YANG, x, y+3,
                                self.showYang, 'sanyed_yang/btn_expand_normal.tga')
        self.hide = self.Button(localeinfo.HIDE_YANG, x, y+3,
                                self.hideYang, 'sanyed_yang/btn_minimize_normal.tga')

    def AddGoldValue(self, text):
        # Shift existing texts up
        for i in xrange(len(self.texts)):
            x, y = self.texts[i].GetLocalPosition()
            self.texts[i].SetPosition(x, y - self.SpaceBet)

        # Add new text at bottom
        newText = ui.TextLine("Tahoma:14")
        newText.SetText(text)
        newText.SetPackedFontColor(self.ColorValue)
        newText.SetHorizontalAlignRight()
        newText.Show()

        self.texts[len(self.texts)] = newText
```

---

## Python-C++ Integration

### C++ Modules Exposed to Python

```python
# Core modules (registered in C++ with Py_InitModule)
import app          # Application control, feature flags
import net          # Network communication, packet sending
import player       # Player character data/state
import chr          # Character rendering and management
import chrmgr       # Character manager
import item         # Item database and functions
import skill        # Skill database and functions
import wndMgr       # Window manager (UI rendering bridge)
import grp          # Graphics primitives (colors, shapes)
import snd          # Sound and music
import chat         # Chat system
import background   # World/map rendering
import textTail     # Name tags above characters
import effect       # Visual effects
import quest        # Quest system
import guild        # Guild system
import shop         # Shop system
import exchange     # Trade system
import messenger    # Friend list
import ime          # Input Method Editor (Asian text input)
import miniMap      # Minimap rendering
import mousemodule  # Mouse cursor control
```

### Python → C++ Call Flow

```python
# Example: Getting player name
name = player.GetName()

# What happens:
# 1. Python calls player.GetName()
# 2. C++ function playerGetName() executes
# 3. CPythonPlayer::Instance().GetName() returns string
# 4. Py_BuildValue("s", name) converts C++ string to Python
# 5. Python receives the string
```

**C++ Implementation (simplified):**
```cpp
// In PythonPlayerModule.cpp
PyObject* playerGetName(PyObject* poSelf, PyObject* poArgs) {
    return Py_BuildValue("s", CPythonPlayer::Instance().GetName());
}

// Module registration
static PyMethodDef s_methods[] = {
    {"GetName", playerGetName, METH_VARARGS},
    {"GetJob", playerGetJob, METH_VARARGS},
    {"GetLevel", playerGetLevel, METH_VARARGS},
    // ... 100+ functions
    {NULL, NULL, 0}
};

void initPlayer() {
    Py_InitModule("player", s_methods);
}
```

### C++ → Python Call Flow

```python
# Event handler registered
button.SetEvent(ui.__mem_func__(self.OnClick))

# What happens when button clicked:
# 1. C++ detects mouse click on button window
# 2. C++ calls Python: PyCallFunction(eventFunc, eventArgs)
# 3. Python OnClick() executes
# 4. Control returns to C++
```

### Window Manager Bridge (wndMgr)

The window manager is the critical bridge between Python UI and C++ rendering:

```python
# Python creates window
self.hWnd = wndMgr.Register(self, "UI")  # Returns C++ window handle

# Python controls window
wndMgr.Show(self.hWnd)                   # C++ makes window visible
wndMgr.SetWindowPosition(self.hWnd, 100, 200)  # C++ moves window
wndMgr.SetWindowSize(self.hWnd, 300, 400)      # C++ resizes window

# Python queries window
x, y = wndMgr.GetWindowGlobalPosition(self.hWnd)
width = wndMgr.GetWindowWidth(self.hWnd)
isVisible = wndMgr.IsShow(self.hWnd)

# C++ renders during frame:
# - Iterates all visible windows
# - Renders each window's graphics
# - Calls Python OnRender() callbacks if set
```

**Common wndMgr Functions:**
```python
# Window lifecycle
wndMgr.Register(pyObj, layer) → hWnd
wndMgr.Destroy(hWnd)

# Visibility
wndMgr.Show(hWnd)
wndMgr.Hide(hWnd)
wndMgr.IsShow(hWnd) → bool

# Position/Size
wndMgr.SetWindowPosition(hWnd, x, y)
wndMgr.GetWindowGlobalPosition(hWnd) → (x, y)
wndMgr.SetWindowSize(hWnd, width, height)
wndMgr.GetWindowWidth(hWnd) → int
wndMgr.GetWindowHeight(hWnd) → int

# Hierarchy
wndMgr.SetParent(childHWnd, parentHWnd)

# Focus
wndMgr.SetFocus(hWnd)
wndMgr.KillFocus(hWnd)
wndMgr.IsFocus(hWnd) → bool

# Input
wndMgr.IsIn(hWnd) → bool  # Is mouse over window?
wndMgr.GetMousePosition() → (x, y)
wndMgr.GetMouseLocalPosition(hWnd) → (x, y)

# Slots (special)
wndMgr.SetSlot(hWnd, slotIndex, itemVNum, width, height, iconPath)
wndMgr.ClearSlot(hWnd, slotIndex)
wndMgr.ActivateSlot(hWnd, slotIndex)
```

---

## UI Window Implementation Pattern

Every UI window follows this standard pattern:

### Step 1: Class Definition

```python
import ui
import player
import wndMgr

class MyWindow(ui.ScriptWindow):
    def __init__(self):
        ui.ScriptWindow.__init__(self)

        # Initialize member variables
        self.tooltipItem = None
        self.itemSlot = None
        self.closeButton = None

        # Load the window
        self.__LoadWindow()
```

### Step 2: Load UI from Script

```python
def __LoadWindow(self):
    try:
        # Load UI layout from uiscript file
        pyScrLoader = ui.PythonScriptLoader()
        pyScrLoader.LoadScriptFile(self, "uiscript/mywindow.py")
    except:
        import exception
        exception.Abort("MyWindow.LoadWindow.LoadScript")

    try:
        # Get references to UI elements defined in script
        self.GetChild("TitleBar")
        self.itemSlot = self.GetChild("ItemSlot")
        self.closeButton = self.GetChild("CloseButton")
    except:
        import exception
        exception.Abort("MyWindow.LoadWindow.BindObject")

    # Setup event handlers
    self.closeButton.SetEvent(ui.__mem_func__(self.Close))
    self.itemSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItem))
    self.itemSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
    self.itemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
```

### Step 3: Event Handlers

```python
def SelectItem(self, slotIndex):
    """Called when user clicks item slot"""
    itemVNum = player.GetItemIndex(slotIndex)
    if itemVNum:
        # Do something with item
        self.UseItem(slotIndex)

def OverInItem(self, slotIndex):
    """Called when mouse enters item slot"""
    if self.tooltipItem:
        self.tooltipItem.SetInventoryItem(slotIndex)

def OverOutItem(self):
    """Called when mouse leaves item slot"""
    if self.tooltipItem:
        self.tooltipItem.HideToolTip()

def Close(self):
    """Called when close button clicked"""
    self.Hide()
```

### Step 4: Public Interface

```python
def Open(self):
    """Show the window"""
    self.SetCenterPosition()  # Center on screen
    self.SetTop()             # Bring to front
    self.Show()

def SetItemToolTip(self, tooltip):
    """Set tooltip handler"""
    self.tooltipItem = tooltip

def RefreshItems(self):
    """Update displayed items"""
    for slotIndex in range(SLOT_COUNT):
        itemVNum = player.GetItemIndex(slotIndex)
        itemCount = player.GetItemCount(slotIndex)

        if itemVNum:
            self.itemSlot.SetItemSlot(slotIndex, itemVNum, itemCount)
        else:
            self.itemSlot.ClearSlot(slotIndex)
```

### Complete Example: Simple Item Window

```python
import ui
import player
import uitooltip

class SimpleItemWindow(ui.ScriptWindow):
    SLOT_COUNT = 20

    def __init__(self):
        ui.ScriptWindow.__init__(self)

        self.tooltipItem = None
        self.isLoaded = False

        self.__LoadWindow()

    def __del__(self):
        ui.ScriptWindow.__del__(self)

    def __LoadWindow(self):
        if self.isLoaded:
            return

        try:
            pyScrLoader = ui.PythonScriptLoader()
            pyScrLoader.LoadScriptFile(self, "uiscript/simpleitemwindow.py")

            self.titleBar = self.GetChild("TitleBar")
            self.itemSlot = self.GetChild("ItemSlot")

            self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))

            self.itemSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItem))
            self.itemSlot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
            self.itemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

            self.isLoaded = True

        except Exception as e:
            import exception
            exception.Abort("SimpleItemWindow.__LoadWindow: " + str(e))

    def Destroy(self):
        self.tooltipItem = None
        self.ClearDictionary()

    def Open(self):
        self.RefreshItems()
        self.SetCenterPosition()
        self.SetTop()
        self.Show()

    def Close(self):
        self.Hide()

    def SetItemToolTip(self, tooltip):
        self.tooltipItem = tooltip

    def RefreshItems(self):
        for i in range(self.SLOT_COUNT):
            itemVNum = player.GetItemIndex(i)
            itemCount = player.GetItemCount(i)

            if itemVNum:
                self.itemSlot.SetItemSlot(i, itemVNum, itemCount)
            else:
                self.itemSlot.ClearSlot(i)

    def SelectItem(self, slotIndex):
        # Handle item selection
        pass

    def OverInItem(self, slotIndex):
        if self.tooltipItem:
            self.tooltipItem.SetInventoryItem(slotIndex)

    def OverOutItem(self):
        if self.tooltipItem:
            self.tooltipItem.HideToolTip()
```

---

## Event Handling System

### The __mem_func__ Pattern

**Problem**: Python circular references cause memory leaks

**Solution**: Use weak references via `__mem_func__`

```python
class __mem_func__:
    """Creates weak reference to member function"""

    class __noarg_call__:
        def __init__(self, cls, obj, func):
            self.cls = cls
            self.obj = proxy(obj)      # Weak reference to object
            self.func = proxy(func)    # Weak reference to function

        def __call__(self, *arg):
            return self.func(self.obj)

    class __arg_call__:
        def __init__(self, cls, obj, func):
            self.cls = cls
            self.obj = proxy(obj)
            self.func = proxy(func)

        def __call__(self, *arg):
            return self.func(self.obj, *arg)

    def __init__(self, mfunc):
        # Check if function takes arguments
        if mfunc.im_func.func_code.co_argcount > 1:
            self.call = __mem_func__.__arg_call__(
                mfunc.im_class, mfunc.im_self, mfunc.im_func)
        else:
            self.call = __mem_func__.__noarg_call__(
                mfunc.im_class, mfunc.im_self, mfunc.im_func)

    def __call__(self, *arg):
        return self.call(*arg)
```

**Usage:**
```python
# BAD - creates circular reference
button.SetEvent(self.OnClick)

# GOOD - uses weak reference
button.SetEvent(ui.__mem_func__(self.OnClick))
```

### Event Registration Methods

```python
# Simple event (no arguments)
def SetEvent(self, event):
    self.event = event

# Event with arguments
def SetEvent(self, event, *args):
    self.event = event
    self.eventArgs = args

# Safe event (weak reference)
def SAFE_SetEvent(self, event, *args):
    self.event = __mem_func__(event)
    self.eventArgs = args

# String-keyed events
def SetStringEvent(self, eventName, func, *args):
    self.eventDict[eventName] = func
    self.argDict[eventName] = args

def SAFE_SetStringEvent(self, eventName, func, *args):
    self.eventDict[eventName] = __mem_func__(func)
    self.argDict[eventName] = args
```

### Mouse Events

```python
# Button click
button.SetEvent(ui.__mem_func__(self.OnClick), extraArg)

# Mouse over
imageBox.SetMouseOverInEvent(ui.__mem_func__(self.OnMouseOver))
imageBox.SetMouseOverOutEvent(ui.__mem_func__(self.OnMouseOut))

# Right click
window.SetMouseRightButtonDownEvent(ui.__mem_func__(self.OnRightClick))

# Double click
button.SetMouseLeftButtonDoubleClickEvent(ui.__mem_func__(self.OnDoubleClick))

# Drag
dragButton.SetMoveEvent(ui.__mem_func__(self.OnDrag))
```

### Slot Events

```python
slotWindow = ui.SlotWindow()

# Click empty slot
slotWindow.SetSelectEmptySlotEvent(ui.__mem_func__(self.OnSelectEmpty))

# Click item slot
slotWindow.SetSelectItemSlotEvent(ui.__mem_func__(self.OnSelectItem))

# Right-click slot
slotWindow.SetUnselectItemSlotEvent(ui.__mem_func__(self.OnUnselectItem))

# Double-click (use) slot
slotWindow.SetUseSlotEvent(ui.__mem_func__(self.OnUseSlot))

# Mouse over slot
slotWindow.SetOverInItemEvent(ui.__mem_func__(self.OnOverIn))
slotWindow.SetOverOutItemEvent(ui.__mem_func__(self.OnOverOut))
```

---

## Widget Classes Reference

### Button

```python
button = ui.Button()
button.SetParent(parentWindow)
button.SetPosition(10, 20)

# Visuals (images for different states)
button.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
button.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
button.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")

# Text
button.SetText("Click Me")
button.SetTextColor(0xFFFFFFFF)

# Event
button.SetEvent(ui.__mem_func__(self.OnClick))

# State
button.Enable()
button.Disable()
button.Down()    # Press down
button.SetUp()   # Release up

button.Show()
```

### ImageBox

```python
imageBox = ui.ImageBox()
imageBox.SetParent(parentWindow)
imageBox.SetPosition(50, 100)

# Load image
imageBox.LoadImage("d:/ymir work/ui/intro/login_panel.sub")

# Alpha
imageBox.SetAlpha(0.5)  # 50% transparent

# Color tint
imageBox.SetDiffuseColor(1.0, 0.5, 0.5, 1.0)  # Reddish tint

# Events
imageBox.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OnMouseOver)
imageBox.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OnMouseOut)

imageBox.Show()
```

### ExpandedImageBox (Scalable)

```python
expandedImg = ui.ExpandedImageBox()
expandedImg.SetParent(parentWindow)
expandedImg.LoadImage("d:/ymir work/ui/pattern/border.tga")

# Scale
expandedImg.SetScale(2.0, 1.5)  # 200% width, 150% height

# Rotation
expandedImg.SetRotation(45.0)  # 45 degrees

# Origin point for rotation
expandedImg.SetOrigin(16, 16)

# Rendering mode
expandedImg.SetRenderingMode(0)  # Normal
# expandedImg.SetRenderingMode(1)  # Additive blending

expandedImg.Show()
```

### TextLine

```python
text = ui.TextLine()
text.SetParent(parentWindow)
text.SetPosition(100, 50)

# Font
text.SetFontName("Tahoma:12")  # Font:Size
text.SetFontColor(0xFF, 0xFF, 0xFF)  # White

# Or packed color
text.SetPackedFontColor(0xFFFFFFFF)

# Text
text.SetText("Hello World")

# Alignment
text.SetHorizontalAlignLeft()
text.SetHorizontalAlignCenter()
text.SetHorizontalAlignRight()

text.SetVerticalAlignTop()
text.SetVerticalAlignCenter()
text.SetVerticalAlignBottom()

# Outline
text.SetOutline()

# Size
width, height = text.GetTextSize()

text.Show()
```

### EditLine (Text Input)

```python
editLine = ui.EditLine()
editLine.SetParent(parentWindow)
editLine.SetPosition(50, 100)
editLine.SetSize(200, 20)

# Max length
editLine.SetMax(50)

# Text
editLine.SetText("Enter text...")
currentText = editLine.GetText()

# Focus
editLine.SetFocus()
editLine.KillFocus()

# Events
editLine.SetReturnEvent(ui.__mem_func__(self.OnEnter))
editLine.SetEscapeEvent(ui.__mem_func__(self.OnCancel))
editLine.SetTabEvent(ui.__mem_func__(self.OnTab))

# Number only
editLine.SetNumberMode()

# Secret (password)
editLine.SetSecret()

editLine.Show()
```

### SlotWindow

```python
slotWindow = ui.SlotWindow()
slotWindow.SetParent(parentWindow)
slotWindow.SetPosition(0, 0)
slotWindow.SetSize(200, 400)

# Create slots (grid layout)
slotWindow.AppendSlot(slotIndex, x, y, width, height)

# Or use SetSlotStyle for auto-layout
slotWindow.SetSlotStyle(wndMgr.SLOT_STYLE_PICK_UP)

# Set item in slot
slotWindow.SetItemSlot(slotIndex, itemVNum, itemCount)
# With icon path:
slotWindow.SetSlot(slotIndex, itemVNum, width, height, iconPath)

# Clear slot
slotWindow.ClearSlot(slotIndex)

# Slot appearance
slotWindow.ActivateSlot(slotIndex)     # Highlight
slotWindow.DeactivateSlot(slotIndex)   # Unhighlight

# Cooldown
slotWindow.SetSlotCoolTime(slotIndex, coolTime, elapsedTime)

# Events
slotWindow.SetSelectEmptySlotEvent(ui.__mem_func__(self.OnSelectEmpty))
slotWindow.SetSelectItemSlotEvent(ui.__mem_func__(self.OnSelectItem))
slotWindow.SetUnselectItemSlotEvent(ui.__mem_func__(self.OnUnselectItem))
slotWindow.SetUseSlotEvent(ui.__mem_func__(self.OnUseSlot))
slotWindow.SetOverInItemEvent(ui.__mem_func__(self.OnOverIn))
slotWindow.SetOverOutItemEvent(ui.__mem_func__(self.OnOverOut))

slotWindow.Show()
```

### Board (Decorated Panel)

```python
board = ui.Board()
board.SetParent(parentWindow)
board.SetSize(300, 400)
board.SetCenterPosition()

# Board is automatically decorated with borders
# Can add children to it
titleText = ui.TextLine()
titleText.SetParent(board)
titleText.SetText("My Panel")

board.Show()
```

### ThinBoard (Thinner Borders)

```python
thinBoard = ui.ThinBoard()
thinBoard.SetParent(parentWindow)
thinBoard.SetSize(200, 300)
thinBoard.SetPosition(50, 50)
thinBoard.Show()
```

### BoardWithTitleBar

```python
boardWithTitle = ui.BoardWithTitleBar()
boardWithTitle.SetParent(parentWindow)
boardWithTitle.SetSize(300, 400)
boardWithTitle.SetCenterPosition()

# Set title
boardWithTitle.SetTitleName("My Window")

# Close button event
boardWithTitle.SetCloseEvent(ui.__mem_func__(self.Close))

boardWithTitle.Show()
```

### ScrollBar

```python
scrollBar = ui.ScrollBar()
scrollBar.SetParent(parentWindow)
scrollBar.SetPosition(280, 10)
scrollBar.SetScrollBarSize(300)  # Height

# Event when scrolled
scrollBar.SetScrollEvent(ui.__mem_func__(self.OnScroll))

# Set position (0.0 to 1.0)
scrollBar.SetPos(0.5)
currentPos = scrollBar.GetPos()

# Middle bar size (visible portion)
scrollBar.SetMiddleBarSize(0.3)  # 30% of total

scrollBar.Show()

def OnScroll(self):
    pos = scrollBar.GetPos()
    # Update list view based on position
```

### ListBox

```python
listBox = ui.ListBox()
listBox.SetParent(parentWindow)
listBox.SetPosition(10, 10)
listBox.SetSize(200, 300)

# Item step (height per item)
listBox.SetItemStep(20)

# Item size
listBox.SetItemSize(200, 20)

# Add items (must be Window objects)
for i in range(10):
    item = ui.TextLine()
    item.SetText("Item %d" % i)
    listBox.AppendItem(item)

# Selection event
listBox.SetSelectEvent(ui.__mem_func__(self.OnSelectItem))

# Get selected
selectedItem = listBox.GetSelectedItem()

listBox.Show()
```

### Gauge (Progress Bar)

```python
gauge = ui.Gauge()
gauge.SetParent(parentWindow)
gauge.SetPosition(50, 100)
gauge.SetSize(200, 12)

# Make gauge (image files)
gauge.MakeGauge(200, "red")  # Width, color
# or with custom image
gauge.MakeGauge(200, "d:/ymir work/ui/gauge/hpgauge.sub")

# Set value (0.0 to 1.0)
gauge.SetPercentage(0.75, 1.0)  # 75% of max

gauge.Show()
```

---

## UI Script System

UI layouts are defined in Python dictionary format in `uiscript/` directory.

### Basic Script Structure

```python
# uiscript/mywindow.py
window = {
    "name" : "MyWindow",

    # Window properties
    "x" : 0,
    "y" : 0,
    "width" : 300,
    "height" : 400,

    "children" : (
        # Child elements defined here
    ),
}
```

### Common Element Types

```python
# Button
{
    "name" : "OKButton",
    "type" : "button",

    "x" : 100,
    "y" : 350,

    "text" : "OK",

    "default_image" : "d:/ymir work/ui/public/large_button_01.sub",
    "over_image" : "d:/ymir work/ui/public/large_button_02.sub",
    "down_image" : "d:/ymir work/ui/public/large_button_03.sub",
},

# Image
{
    "name" : "BackgroundImage",
    "type" : "image",

    "x" : 0,
    "y" : 0,

    "image" : "d:/ymir work/ui/intro/login_panel.sub",
},

# Text
{
    "name" : "TitleText",
    "type" : "text",

    "x" : 150,
    "y" : 10,

    "text" : "My Window Title",

    "horizontal_align" : "center",
    "text_horizontal_align" : "center",
},

# EditLine (input)
{
    "name" : "NameInput",
    "type" : "editline",

    "x" : 50,
    "y" : 100,

    "width" : 200,
    "height" : 20,

    "input_limit" : 50,
},

# Slot window
{
    "name" : "ItemSlot",
    "type" : "slot",

    "x" : 10,
    "y" : 50,

    "width" : 280,
    "height" : 300,

    "slot" : (
        {"index": 0, "x": 0, "y": 0, "width": 32, "height": 32},
        {"index": 1, "x": 40, "y": 0, "width": 32, "height": 32},
        # ... more slots
    ),
},

# TitleBar
{
    "name" : "TitleBar",
    "type" : "titlebar",

    "x" : 8,
    "y" : 7,

    "width" : 284,

    "title" : "Window Title",
},

# Board (decorated panel)
{
    "name" : "Board",
    "type" : "board",

    "x" : 0,
    "y" : 0,

    "width" : 300,
    "height" : 400,

    "children" : (
        # Nested children
    ),
},
```

### Complete Example Script

```python
# uiscript/simpleitemwindow.py
window = {
    "name" : "SimpleItemWindow",

    "x" : 0,
    "y" : 0,
    "width" : 200,
    "height" : 300,

    "children" : (
        # Main board
        {
            "name" : "board",
            "type" : "board",
            "x" : 0,
            "y" : 0,
            "width" : 200,
            "height" : 300,

            "children" : (
                # Title bar
                {
                    "name" : "TitleBar",
                    "type" : "titlebar",
                    "x" : 8,
                    "y" : 7,
                    "width" : 184,
                    "title" : "Items",
                },

                # Item slots
                {
                    "name" : "ItemSlot",
                    "type" : "slot",
                    "x" : 10,
                    "y" : 35,
                    "width" : 180,
                    "height" : 250,

                    "slot" : (
                        # 20 slots in 4x5 grid
                        {"index": 0, "x": 0, "y": 0, "width": 32, "height": 32},
                        {"index": 1, "x": 45, "y": 0, "width": 32, "height": 32},
                        {"index": 2, "x": 90, "y": 0, "width": 32, "height": 32},
                        {"index": 3, "x": 135, "y": 0, "width": 32, "height": 32},

                        {"index": 4, "x": 0, "y": 45, "width": 32, "height": 32},
                        # ... rest of slots
                    ),
                },
            ),
        },
    ),
}
```

### Loading Script in Python

```python
def __LoadWindow(self):
    try:
        pyScrLoader = ui.PythonScriptLoader()
        pyScrLoader.LoadScriptFile(self, "uiscript/simpleitemwindow.py")
    except:
        import exception
        exception.Abort("SimpleItemWindow.LoadWindow")

    # Get references to elements by name
    try:
        self.board = self.GetChild("board")
        self.titleBar = self.GetChild("TitleBar")
        self.itemSlot = self.GetChild("ItemSlot")
    except:
        import exception
        exception.Abort("SimpleItemWindow.BindObject")
```

---

## Slot System

The slot system is used for inventories, skill bars, shops, warehouses, etc.

### Creating Slots

```python
# Method 1: Manual slot creation
slotWindow = ui.SlotWindow()
slotWindow.AppendSlot(index, x, y, width, height)

# Method 2: Use script (recommended)
# Define in uiscript file, load with PythonScriptLoader
```

### Setting Items in Slots

```python
# Set item with vnum and count
slotWindow.SetItemSlot(slotIndex, itemVNum, itemCount)

# Set with full control
slotWindow.SetSlot(slotIndex, itemVNum, width, height, iconImagePath)

# Clear slot
slotWindow.ClearSlot(slotIndex)

# Example: Refresh inventory
for i in range(INVENTORY_MAX_NUM):
    itemVNum = player.GetItemIndex(i)
    itemCount = player.GetItemCount(i)

    if itemVNum:
        self.inventorySlot.SetItemSlot(i, itemVNum, itemCount)
    else:
        self.inventorySlot.ClearSlot(i)
```

### Slot Appearance

```python
# Highlight/select
slotWindow.ActivateSlot(slotIndex)
slotWindow.DeactivateSlot(slotIndex)

# Cooldown overlay
slotWindow.SetSlotCoolTime(slotIndex, totalTime, elapsedTime)

# Custom cooldown color
slotWindow.SetSlotCoolTimeColor(slotIndex, r, g, b, a)

# Cover button (for locked items)
slotWindow.SetCoverButton(
    slotIndex,
    upImage="d:/ymir work/ui/public/slot_cover_button_01.sub",
    overImage="d:/ymir work/ui/public/slot_cover_button_02.sub",
    downImage="d:/ymir work/ui/public/slot_cover_button_03.sub",
    disableImage="d:/ymir work/ui/public/slot_cover_button_04.sub",
    LeftButtonEnable=False,
    RightButtonEnable=True
)

slotWindow.EnableCoverButton(slotIndex)
slotWindow.DisableCoverButton(slotIndex)
```

### Slot Events

```python
# Click empty slot
def OnSelectEmpty(self, slotIndex):
    # Attach item to cursor if holding one
    if mousemodule.mouseController.isAttached():
        attachedSlotType = mousemodule.mouseController.GetAttachedType()
        attachedSlotIndex = mousemodule.mouseController.GetAttachedSlotNumber()

        # Move item to this empty slot
        net.SendItemMovePacket(attachedSlotType, attachedSlotIndex,
                              player.SLOT_TYPE_INVENTORY, slotIndex, 0)

# Click item slot
def OnSelectItem(self, slotIndex):
    itemVNum = player.GetItemIndex(slotIndex)
    if not itemVNum:
        return

    # Pick up item with cursor
    mousemodule.mouseController.AttachObject(self, slotIndex,
                                             player.SLOT_TYPE_INVENTORY, itemVNum)

# Right-click item
def OnUnselectItem(self, slotIndex):
    # Quick-use or quick-equip
    itemVNum = player.GetItemIndex(slotIndex)
    if item.IsEquipmentItem(itemVNum):
        net.SendItemUsePacket(slotIndex)

# Double-click (use) item
def OnUseSlot(self, slotIndex):
    net.SendItemUsePacket(slotIndex)

# Mouse over
def OnOverInItem(self, slotIndex):
    if self.tooltipItem:
        self.tooltipItem.SetInventoryItem(slotIndex)

def OnOverOutItem(self):
    if self.tooltipItem:
        self.tooltipItem.HideToolTip()

# Register events
slotWindow.SetSelectEmptySlotEvent(ui.__mem_func__(self.OnSelectEmpty))
slotWindow.SetSelectItemSlotEvent(ui.__mem_func__(self.OnSelectItem))
slotWindow.SetUnselectItemSlotEvent(ui.__mem_func__(self.OnUnselectItem))
slotWindow.SetUseSlotEvent(ui.__mem_func__(self.OnUseSlot))
slotWindow.SetOverInItemEvent(ui.__mem_func__(self.OnOverInItem))
slotWindow.SetOverOutItemEvent(ui.__mem_func__(self.OnOverOutItem))
```

---

## Common UI Patterns

### Tooltip Pattern

```python
class MyWindow(ui.ScriptWindow):
    def __init__(self):
        ui.ScriptWindow.__init__(self)
        self.tooltipItem = None

    def SetItemToolTip(self, tooltip):
        self.tooltipItem = tooltip

    def OverInItem(self, slotIndex):
        # Show tooltip when mouse over item
        if self.tooltipItem:
            self.tooltipItem.SetInventoryItem(slotIndex)

    def OverOutItem(self):
        # Hide tooltip when mouse leaves
        if self.tooltipItem:
            self.tooltipItem.HideToolTip()
```

### Dialog Pattern

```python
import uicommon

# Question dialog
def AskQuestion(self):
    questionDialog = uicommon.QuestionDialog()
    questionDialog.SetText("Are you sure you want to delete this item?")
    questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnAccept))
    questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCancel))
    questionDialog.Open()
    self.questionDialog = questionDialog

def OnAccept(self):
    # User clicked Yes
    self.DeleteItem()
    self.questionDialog.Close()
    self.questionDialog = None

def OnCancel(self):
    # User clicked No
    self.questionDialog.Close()
    self.questionDialog = None

# Message dialog
def ShowMessage(self, message):
    messageDialog = uicommon.PopupDialog()
    messageDialog.SetText(message)
    messageDialog.SetAcceptEvent(ui.__mem_func__(self.OnMessageOK))
    messageDialog.Open()

def OnMessageOK(self):
    if self.messageDialog:
        self.messageDialog.Close()
        self.messageDialog = None
```

### ListBox with ScrollBar Pattern

```python
def CreateList(self):
    # Create listbox
    self.listBox = ui.ListBoxEx()
    self.listBox.SetParent(self.board)
    self.listBox.SetPosition(10, 10)
    self.listBox.SetSize(200, 300)

    # Create scrollbar
    self.scrollBar = ui.ScrollBar()
    self.scrollBar.SetParent(self.board)
    self.scrollBar.SetPosition(215, 10)
    self.scrollBar.SetScrollBarSize(300)

    # Link scrollbar to listbox
    self.listBox.SetScrollBar(self.scrollBar)

    # Populate list
    for i in range(50):
        item = ui.TextLine()
        item.SetText("Item %d" % i)
        self.listBox.AppendItem(item)

def OnMouseWheel(self, nLen):
    # Pass mouse wheel to listbox
    if self.listBox:
        return self.listBox.OnMouseWheel(nLen)
    return False
```

### Tabbed Window Pattern

```python
class TabbedWindow(ui.ScriptWindow):
    def __init__(self):
        ui.ScriptWindow.__init__(self)

        self.currentTab = 0
        self.tabButtons = []
        self.tabPages = []

    def CreateTabs(self):
        # Create tab buttons
        tabNames = ["Tab1", "Tab2", "Tab3"]
        for i, name in enumerate(tabNames):
            button = ui.RadioButton()
            button.SetParent(self.board)
            button.SetPosition(10 + i * 70, 10)
            button.SetUpVisual("tab_normal.tga")
            button.SetOverVisual("tab_over.tga")
            button.SetDownVisual("tab_down.tga")
            button.SetText(name)
            button.SetEvent(ui.__mem_func__(self.OnClickTab), i)
            button.Show()
            self.tabButtons.append(button)

        # Create pages (hide initially)
        for i in range(3):
            page = ui.Window()
            page.SetParent(self.board)
            page.SetPosition(0, 40)
            page.SetSize(300, 260)
            page.Hide()
            self.tabPages.append(page)

        # Show first tab
        self.OnClickTab(0)

    def OnClickTab(self, tabIndex):
        # Hide all pages
        for page in self.tabPages:
            page.Hide()

        # Show selected page
        self.tabPages[tabIndex].Show()

        # Update button states
        for i, button in enumerate(self.tabButtons):
            if i == tabIndex:
                button.Down()
            else:
                button.SetUp()

        self.currentTab = tabIndex
```

### Drag & Drop Pattern

```python
class DragDropWindow(ui.ScriptWindow):
    def __init__(self):
        ui.ScriptWindow.__init__(self)
        self.dragButton = None

    def CreateDragButton(self):
        self.dragButton = ui.DragButton()
        self.dragButton.SetParent(self.board)
        self.dragButton.SetPosition(100, 100)
        self.dragButton.SetUpVisual("drag_normal.tga")
        self.dragButton.SetOverVisual("drag_over.tga")
        self.dragButton.SetDownVisual("drag_down.tga")

        # Restrict movement area (x, y, width, height)
        self.dragButton.SetRestrictMovementArea(10, 10, 280, 280)

        # Movement callback
        self.dragButton.SetMoveEvent(ui.__mem_func__(self.OnDrag))
        self.dragButton.Show()

    def OnDrag(self):
        # Called when button is dragged
        x, y = self.dragButton.GetLocalPosition()
        # Do something with new position
```

### Input Validation Pattern

```python
class InputWindow(ui.ScriptWindow):
    def __init__(self):
        ui.ScriptWindow.__init__(self)
        self.inputLine = None

    def CreateInput(self):
        self.inputLine = ui.EditLine()
        self.inputLine.SetParent(self.board)
        self.inputLine.SetPosition(50, 100)
        self.inputLine.SetSize(200, 20)
        self.inputLine.SetMax(50)  # Max 50 characters

        # Number-only input
        self.inputLine.SetNumberMode()

        # Events
        self.inputLine.SetReturnEvent(ui.__mem_func__(self.OnEnter))
        self.inputLine.SetEscapeEvent(ui.__mem_func__(self.OnCancel))

        self.inputLine.Show()

    def OnEnter(self):
        text = self.inputLine.GetText()

        # Validate
        if not text:
            self.ShowError("Please enter a value")
            return

        try:
            value = int(text)
            if value < 1 or value > 999:
                self.ShowError("Value must be between 1 and 999")
                return
        except ValueError:
            self.ShowError("Invalid number")
            return

        # Process valid input
        self.ProcessInput(value)

    def OnCancel(self):
        self.Close()
```

---

## Best Practices

### 1. Memory Management

```python
# Always clean up in destructor
def __del__(self):
    ui.ScriptWindow.__del__(self)

# Clear references in Destroy
def Destroy(self):
    self.tooltipItem = None
    self.itemSlot = None
    self.ClearDictionary()

# Use weak references for callbacks
button.SetEvent(ui.__mem_func__(self.OnClick))  # GOOD
# button.SetEvent(self.OnClick)  # BAD - creates circular reference
```

### 2. Initialization Pattern

```python
def __init__(self):
    ui.ScriptWindow.__init__(self)

    # Initialize all member variables to None
    self.tooltipItem = None
    self.itemSlot = None
    self.isLoaded = False

    # Load window
    self.__LoadWindow()

def __LoadWindow(self):
    # Prevent double-loading
    if self.isLoaded:
        return

    try:
        # Load script
        pyScrLoader = ui.PythonScriptLoader()
        pyScrLoader.LoadScriptFile(self, "uiscript/mywindow.py")

        # Get children
        self.itemSlot = self.GetChild("ItemSlot")

        # Setup events
        self.itemSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItem))

        self.isLoaded = True
    except:
        import exception
        exception.Abort("MyWindow.__LoadWindow")
```

### 3. Error Handling

```python
# Always use try-except for critical operations
try:
    pyScrLoader.LoadScriptFile(self, "uiscript/mywindow.py")
except:
    import exception
    exception.Abort("MyWindow.LoadScript")

try:
    self.itemSlot = self.GetChild("ItemSlot")
except:
    import exception
    exception.Abort("MyWindow.BindObject")

# Check before using
if self.tooltipItem:
    self.tooltipItem.SetInventoryItem(slotIndex)
```

### 4. Event Registration

```python
# Use SAFE_SetEvent for member functions
button.SAFE_SetEvent(self.OnClick)

# Use __mem_func__ for regular SetEvent
button.SetEvent(ui.__mem_func__(self.OnClick))

# Pass extra arguments
button.SetEvent(ui.__mem_func__(self.OnClick), extraArg1, extraArg2)

def OnClick(self, arg1, arg2):
    # Handle click with arguments
    pass
```

### 5. Window Visibility

```python
# Open pattern
def Open(self):
    # Update content before showing
    self.RefreshItems()

    # Position window
    self.SetCenterPosition()
    # or
    # self.SetPosition(100, 200)

    # Bring to front
    self.SetTop()

    # Show
    self.Show()

# Close pattern
def Close(self):
    # Clean up state
    if self.tooltipItem:
        self.tooltipItem.HideToolTip()

    # Hide
    self.Hide()
```

### 6. Feature Flags

```python
# Always check feature flags
if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
    self.wndSpecialInventory = uispecialinventory.SpecialInventoryWindow()

if app.USE_OFFLINESHOP:
    import uiofflineshop_ae
    self.wndShopOffline = uiofflineshop_ae.ShopOffline()

# Conditional method implementations
if app.ENABLE_VIEW_TARGET_DECIMAL_HP:
    def SetHPTargetBoard(self, vid, hpPercentage, iMinHP, iMaxHP):
        # Implementation with decimal HP
        pass
else:
    def SetHPTargetBoard(self, vid, hpPercentage):
        # Implementation without decimal HP
        pass
```

### 7. Parent-Child Relationships

```python
# Always set parent before positioning
button = ui.Button()
button.SetParent(self.board)  # Set parent first
button.SetPosition(10, 20)    # Then position
button.Show()

# Use GetGlobalPosition for screen coordinates
x, y = self.GetGlobalPosition()

# Use GetLocalPosition for parent-relative coordinates
x, y = self.GetLocalPosition()
```

### 8. Resource Paths

```python
# Use forward slashes and full paths
imageBox.LoadImage("d:/ymir work/ui/intro/login_panel.sub")

# Common prefixes:
# d:/ymir work/ui/           - UI elements
# d:/ymir work/icon/item/    - Item icons
# d:/ymir work/icon/skill/   - Skill icons
# icon/face/                 - Character faces
```

### 9. Localization

```python
import localeinfo

# Use localized strings
button.SetText(localeinfo.UI_OK)
titleBar.SetTitleName(localeinfo.INVENTORY_TITLE)

# Check locale for conditional behavior
if localeinfo.IsARABIC():
    # Right-to-left layout
    text.SetHorizontalAlignRight()
else:
    # Left-to-right layout
    text.SetHorizontalAlignLeft()
```

### 10. Performance

```python
# Batch operations when possible
def RefreshAllItems(self):
    # Don't call Refresh() for each item
    for i in range(SLOT_COUNT):
        itemVNum = player.GetItemIndex(i)
        if itemVNum:
            self.itemSlot.SetItemSlot(i, itemVNum, itemCount)

    # Single refresh at end if needed
    self.UpdateRect()

# Hide windows instead of destroying them
def Close(self):
    self.Hide()  # Just hide, don't destroy

# Only update visible windows
def OnUpdate(self):
    if not self.IsShow():
        return

    # Update logic here
```

---

## RichItemToolTip - Advanced Tooltip with Icon Support

### Overview

The `RichItemToolTip` class (located in `uitooltip.py`) is an enhanced tooltip widget that displays a centered item icon above multiple description lines. It's designed for UI elements that need to show detailed information about items, features, or actions.

**Key Features:**
- Displays centered item icons (32x32) from item VNUM or direct image path
- Supports multiple centered description lines with custom colors
- All elements are centered for consistent layout across all languages
- Title, icon, description, and footer sections
- Auto-repositions elements when tooltip width changes
- Inherits from base `ToolTip` class

### Visual Layout

```
+----------------------------------+
|    [Title Text - Centered]       |
| -------------------------------- |
|           [Icon 32x32]           |
|          (16px spacing)          |
|     Description line 1           |
|     Description line 2           |
|     Description line 3           |
| -------------------------------- |
|   [Footer Text - Centered]       |
+----------------------------------+
```

The layout is the same for all languages (LTR and RTL) since all elements are centered.

### Class Reference

**Location:** `uitooltip.py`, line ~643

```python
class RichItemToolTip(ToolTip):
    # Constants
    ICON_SIZE = 32
    ICON_PADDING_LEFT = 10
    ICON_PADDING_TOP = 8
    TEXT_PADDING_LEFT = 48  # ICON_PADDING_LEFT + ICON_SIZE + 6
    TEXT_LINE_HEIGHT = 15

    # Modern Color Scheme
    TITLE_COLOR = grp.GenerateColor(0.95, 0.95, 0.95, 1.0)     # Clean white
    DESC_COLOR = grp.GenerateColor(0.75, 0.82, 0.88, 1.0)      # Soft blue-gray
    HIGHLIGHT_COLOR = grp.GenerateColor(0.4, 0.8, 0.95, 1.0)   # Cyan/Sky blue
    FOOTER_COLOR = grp.GenerateColor(0.55, 0.6, 0.65, 1.0)     # Muted gray
```

### Methods

| Method | Description |
|--------|-------------|
| `__init__(width=220)` | Create tooltip with specified width |
| `SetItemIcon(itemVnum)` | Set icon from item VNUM (uses item database) |
| `SetIconImage(iconPath)` | Set icon from direct image path |
| `SetTitle(text, color=None)` | Add centered title text |
| `AppendDescriptionLine(text, color=None, indent=True)` | Add description line |
| `AppendFooter(text, color=None)` | Add footer with separator line |
| `AddItemWithDescription(itemVnum, title, descriptions, footer=None)` | Convenience method to set up entire tooltip |
| `AddIconWithDescription(iconPath, title, descriptions, footer=None)` | Same as above but with image path |
| `GetIconXPosition()` | Get icon X position (handles RTL automatically) |

### Basic Usage Tutorial

#### Example 1: Simple Item Tooltip

```python
import uitooltip

# Create the tooltip
tooltip = uitooltip.RichItemToolTip(220)

# Set up content using convenience method
tooltip.AddItemWithDescription(
    itemVnum=72350,                    # Item VNUM for icon
    title="Battle Pass Boost",          # Title text
    descriptions=[
        "Earn extra Battle Pass EXP",   # Simple string (uses default color)
        ("Without doing quests!", tooltip.HIGHLIGHT_COLOR),  # Tuple with custom color
    ],
    footer="Available in Item Shop"     # Footer text
)

# Hide initially
tooltip.HideToolTip()
```

#### Example 2: Manual Setup (More Control)

```python
import uitooltip

tooltip = uitooltip.RichItemToolTip(250)

# Clear any existing content
tooltip.ClearToolTip()

# Add title
tooltip.SetTitle("Special Reward Box")

# Add separator line
tooltip.AppendHorizontalLine()

# Set item icon
tooltip.SetItemIcon(50089)  # Item VNUM

# Add description lines
tooltip.AppendDescriptionLine("Contains rare items", tooltip.DESC_COLOR)
tooltip.AppendDescriptionLine("Level 50+ required", tooltip.HIGHLIGHT_COLOR)
tooltip.AppendDescriptionLine("Bound to character", tooltip.NEGATIVE_COLOR)

# Add footer
tooltip.AppendFooter("Right-click to open")

# Finalize size
tooltip.ResizeToolTip()
tooltip.HideToolTip()
```

#### Example 3: Using Custom Image Path

```python
import uitooltip

tooltip = uitooltip.RichItemToolTip(220)

tooltip.AddIconWithDescription(
    iconPath="d:/ymir work/ui/game/battle_pass/icon_exp.tga",
    title="Experience Boost",
    descriptions=[
        ("Active for 2 hours", tooltip.HIGHLIGHT_COLOR),
        "+50% EXP from monsters",
        "+25% EXP from quests",
    ],
    footer="Premium feature"
)
```

### Integration with UI Elements

#### Step 1: Create Tooltip in Window `__init__` or Load Method

```python
class MyWindow(ui.ScriptWindow):
    def __init__(self):
        ui.ScriptWindow.__init__(self)
        self.myTooltip = None
        self.__LoadWindow()

    def __LoadWindow(self):
        # ... load window script ...

        # Create the button
        self.myButton = ui.Button()
        self.myButton.SetParent(self)
        self.myButton.SetPosition(100, 50)
        # ... set button visuals ...
        self.myButton.Show()

        # Create the tooltip
        self.__CreateMyTooltip()

        # Bind hover events
        self.myButton.SetEvent(ui.__mem_func__(self.OnButtonOverIn), "MOUSE_OVER_IN")
        self.myButton.SetEvent(ui.__mem_func__(self.OnButtonOverOut), "MOUSE_OVER_OUT")

    def __CreateMyTooltip(self):
        self.myTooltip = uitooltip.RichItemToolTip(220)
        self.myTooltip.AddItemWithDescription(
            itemVnum=12345,
            title="My Feature",
            descriptions=[
                "Description line 1",
                ("Highlighted info", self.myTooltip.HIGHLIGHT_COLOR),
            ],
            footer="Click to activate"
        )
        self.myTooltip.HideToolTip()
```

#### Step 2: Implement Hover Event Handlers

```python
    def OnButtonOverIn(self):
        if self.myTooltip:
            self.myTooltip.ShowToolTip()

    def OnButtonOverOut(self):
        if self.myTooltip:
            self.myTooltip.HideToolTip()
```

#### Step 3: Clean Up in Destroy Method

```python
    def Destroy(self):
        self.myTooltip = None
        # ... other cleanup ...
```

### Working with ExpandedImageBoxButton

The `ExpandedImageBoxButton` class supports hover events for tooltips:

```python
# Create button
self.iconButton = ui.ExpandedImageBoxButton()
self.iconButton.SetParent(self)
self.iconButton.SetPosition(50, 50)
self.iconButton.SetUpVisual("d:/ymir work/ui/button_normal.tga")
self.iconButton.SetOverVisual("d:/ymir work/ui/button_over.tga")
self.iconButton.SetDownVisual("d:/ymir work/ui/button_down.tga")
self.iconButton.SetEvent(ui.__mem_func__(self.OnClick))  # Click event
self.iconButton.Show()

# Bind hover events for tooltip
self.iconButton.SetEvent(ui.__mem_func__(self.OnOverIn), "MOUSE_OVER_IN")
self.iconButton.SetEvent(ui.__mem_func__(self.OnOverOut), "MOUSE_OVER_OUT")
```

### Color Constants Reference

| Constant | RGB Values | Visual | Usage |
|----------|------------|--------|-------|
| `TITLE_COLOR` | (0.95, 0.95, 0.95) | Clean white | Title text |
| `DESC_COLOR` | (0.75, 0.82, 0.88) | Soft blue-gray | Normal descriptions |
| `HIGHLIGHT_COLOR` | (0.4, 0.8, 0.95) | Cyan/Sky blue | Progress, rewards, highlighted info |
| `FOOTER_COLOR` | (0.55, 0.6, 0.65) | Muted gray | Footer text |
| `NEGATIVE_COLOR` | (inherited from ToolTip) | Red | Warnings/restrictions |
| `POSITIVE_COLOR` | (inherited from ToolTip) | Green | Bonuses/benefits |

### Localization Support

#### Adding Locale Strings

Add strings to locale files (`locale/en/new_locale_game.txt`):

```
MY_TOOLTIP_TITLE	My Feature Title
MY_TOOLTIP_DESC1	First description line
MY_TOOLTIP_DESC2	Second description line
MY_TOOLTIP_FOOTER	Footer information
```

#### Using Locale Strings in Code

```python
import localeinfo

self.myTooltip.AddItemWithDescription(
    itemVnum=12345,
    title=localeinfo.MY_TOOLTIP_TITLE,
    descriptions=[
        localeinfo.MY_TOOLTIP_DESC1,
        (localeinfo.MY_TOOLTIP_DESC2, self.myTooltip.HIGHLIGHT_COLOR),
    ],
    footer=localeinfo.MY_TOOLTIP_FOOTER
)
```

### RTL (Arabic) Support

The `RichItemToolTip` uses a centered layout that works consistently across all languages:

- **Icon Position:** Centered horizontally (same for all languages)
- **Text Alignment:** All text is centered using `SetHorizontalAlignCenter()`
- **No Code Changes Required:** The centered design works for both LTR and RTL
- **Automatic Repositioning:** The `ResizeToolTip()` override repositions all elements when width changes

This centered approach eliminates the need for complex RTL positioning logic while providing a clean, modern appearance.

### Complete Real-World Example: Battle Pass EXP Boost

This example shows the actual implementation in `uibattlepass.py`:

```python
# In BattlePassWindow class

def __CreateExpBoostTooltip(self):
    """Create a rich tooltip for the EXP Boost button."""
    self.tooltipExpBoost = uitooltip.RichItemToolTip(220)

    # Get item name for the title
    item.SelectItem(ITEM_VNUM_BP_EXP_BOOST)
    itemName = item.GetItemName()

    # Build description lines using locale strings
    descriptions = [
        (localeinfo.BP_EXP_BOOST_TOOLTIP_TITLE, self.tooltipExpBoost.TITLE_COLOR),
        "",  # Empty line for spacing
        (localeinfo.BP_EXP_BOOST_TOOLTIP_DESC1, self.tooltipExpBoost.DESC_COLOR),
        (localeinfo.BP_EXP_BOOST_TOOLTIP_DESC2, self.tooltipExpBoost.HIGHLIGHT_COLOR),
    ]

    # Set up the tooltip
    self.tooltipExpBoost.AddItemWithDescription(
        ITEM_VNUM_BP_EXP_BOOST,
        itemName,
        descriptions,
        localeinfo.BP_EXP_BOOST_TOOLTIP_FOOTER
    )
    self.tooltipExpBoost.HideToolTip()

def OnExpBoostMouseOverIn(self):
    if self.tooltipExpBoost:
        self.tooltipExpBoost.ShowToolTip()

def OnExpBoostMouseOverOut(self):
    if self.tooltipExpBoost:
        self.tooltipExpBoost.HideToolTip()
```

### Complete Real-World Example: Battle Pass Mission Tooltip

This example shows mission tooltips with multi-language line breaking:

```python
# In ListBox.NewItem class (uibattlepass.py)

def __CreateMissionTooltip(self):
    """Create a rich tooltip with detailed mission description."""
    self.tooltipMission = uitooltip.RichItemToolTip(350)  # Wide tooltip

    # Get mission info
    missionTitle = TITLE_TYPES.get(self.type, "Unknown Mission")
    missionDesc = GetMissionDescription(self.type)
    targetName = GetNameByTypeVnum(self.type, self.vnum)

    # Build descriptions with multi-language line breaking
    # Splits by: English period, Arabic comma, Chinese period
    import re
    descParts = re.split(r'\. |، |。', missionDesc)
    descriptions = []
    for part in descParts:
        if part.strip():
            descriptions.append((part.strip(), self.tooltipMission.DESC_COLOR))

    # Add spacing and info lines
    descriptions.append("")  # Empty line for spacing
    descriptions.append(("Progress: %d / %d" % (self.count, self.maxCount),
                        self.tooltipMission.HIGHLIGHT_COLOR))
    if self.vnum > 0:
        descriptions.append(("Target: " + targetName, self.tooltipMission.TITLE_COLOR))
    descriptions.append(("Reward: %d EXP" % self.expRecieve,
                        self.tooltipMission.HIGHLIGHT_COLOR))

    # Footer based on premium status
    footer = "Premium Mission" if self.isPremium else "Standard Mission"

    # Create tooltip with centered icon (using image path)
    iconPath = PATH_ICONS + "%d.png" % self.type
    self.tooltipMission.AddIconWithDescription(iconPath, missionTitle, descriptions, footer)
    self.tooltipMission.HideToolTip()

def OnMissionIconOverIn(self):
    if self.tooltipMission:
        self.tooltipMission.ShowToolTip()

def OnMissionIconOverOut(self):
    if self.tooltipMission:
        self.tooltipMission.HideToolTip()
```

#### Binding to ExpandedImageBox

```python
# In __init__, after creating the mission icon
self.wndIcon = ui.ExpandedImageBox()
self.wndIcon.SetParent(self)
self.wndIcon.LoadImage(PATH_ICONS + "%d.png" % type)
self.wndIcon.Show()

# Create and bind tooltip
self.__CreateMissionTooltip()
self.wndIcon.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.OnMissionIconOverIn))
self.wndIcon.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.OnMissionIconOverOut))
```

### Best Practices

1. **Always hide tooltip initially** after creation with `HideToolTip()`

2. **Use weak references** for event handlers with `ui.__mem_func__()`

3. **Clean up references** in `Destroy()` method to prevent memory leaks

4. **Use locale strings** for all user-visible text for proper localization

5. **Test with Arabic locale** to ensure RTL layout works correctly

6. **Use appropriate colors** to convey meaning (green for positive, red for warnings)

7. **Keep descriptions concise** - tooltips should be quick to read

8. **Set appropriate width** - 200-250 pixels works well for most cases

---

## Summary

The Metin2 UI system is a sophisticated, mature framework that:

1. **Separates concerns**: Python handles UI logic, C++ handles rendering
2. **Is event-driven**: Everything uses callbacks and weak references
3. **Is modular**: Each window is self-contained and reusable
4. **Is scriptable**: Layouts defined in Python dictionaries
5. **Is extensible**: New widgets can inherit from base classes
6. **Handles complexity**: 122+ UI windows, real-time server updates
7. **Is feature-flagged**: Conditional compilation for different game versions

The three core files (ui.py, game.py, interfacemodule.py) work together to create a complete MMORPG client UI capable of handling thousands of simultaneous users with complex interactions.

Understanding this architecture is essential for modifying or extending the game's user interface.
