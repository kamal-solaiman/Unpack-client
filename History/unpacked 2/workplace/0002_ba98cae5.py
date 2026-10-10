# workplace — Python UI Scripts

The complete Python 2.7 UI implementation for the Metin2 client — ~147 k lines of Python across 150+ files, including 122+ `ui*.py` windows.

The C++ engine in [../../../../srcs/client/UserInterface/](../../../../srcs/client/UserInterface/) bridges these scripts to the game. Python changes don't require a recompile; they ship inside `.epk` packs.

## Foundation

| File | Role |
|------|------|
| `ui.py` (~9 446 lines) | **The widget framework.** `Window`, `Button`, `EditLine`, `TextLine`, `ImageBox`, `SlotWindow`, `GridSlotWindow`, `ListBox`, `ScrollBar`, `ThinBoard`, `Board`, `TitleBar`, `ComboBox`, `RadioButton`, `CheckBox`, `ToolTip`. Every other `ui*.py` inherits from these. |
| `interfacemodule.py` (~4 730 lines) | **Window orchestrator.** Owns references to every game window, routes events, manages window lifecycle. `Interface.MakeInterface()` instantiates all windows at startup. |
| `game.py` (~4 650 lines) | **Game state machine** — login, character select, loading, in-game. Frame updates, network event processing. |

## Window catalogue (selection)

### Player UI

| File | What it does |
|------|--------------|
| `uiinventory.py` | Inventory grids (main + dragon-soul + costume + special), drag/drop, swap |
| `uitooltip.py` (~6 700 lines) | All hover tooltips — item / skill / affect / monster / NPC |
| `uicharacter.py` | Stats window, attribute allocation, equipment preview |
| `uichat.py` | Chat tabs, channels (normal / shout / guild / party / whisper / system), history |
| `uiminimap.py` | Minimap + world map atlas, warp markers |
| `uiparty.py` | Party HP/SP bars, leader controls, invitations |
| `uimessenger.py` | Friend list, online status |
| `uiexchange.py` | Player ↔ player trade window |
| `uiskilltre.py` | Skill tree, learning, upgrading |
| `uiquest.py` | Quest journal |

### Mission system (`ENABLE_MISSION_QUEST`)

| File | What it does |
|------|--------------|
| `uimissionlist.py` (~1 900 lines) | Daily/weekly missions, 3 slots each, reroll, history pagination |
| `missionhelper.py` (~160 lines) | `GetMonsterMissionProgress(vnum)` / `GetItemMissionProgress(vnum)` for tooltip + target-board integration |

Data is shaped as `dictMissionInfo[type][slot]` where type 0 = daily, 1 = weekly. Server commands: `MQ_TABLE`, `MQ_UPDATE`, `MQ_GENERAL`, `MQ_REWARD`, `MQ_HISTORY`.

### Shops & economy

| File | What it does |
|------|--------------|
| `uishop.py` | NPC shop tabs |
| `uiprivateshopbuilder.py` | Create / configure private shop |
| `uiofflineshop_*.py` | Offline shop system (creation, listing, search, history) |

### Special systems

| File | What it does |
|------|--------------|
| `ingamewikiui.py` (~5 380 lines) | In-game encyclopedia (monsters, items, bosses, drops) |
| `uibattlepassextended.py` | Battle pass missions + rewards |
| `uidragonsoul.py` | Dragon soul activate/refine/upgrade |
| `uiswitchbot.py` | Auto item-switcher based on attributes |
| `uipetinfo.py` | Pet status / leveling / equipment |

### Events & mini-games

`uispinwheel.py`, `uioxevent.py`, `uiminigame*.py` (Catch King, BNW, Rumi, Fish chest), …

### Login / character select

`intrologin.py`, `introselect.py`, `introcreate.py`, `introempire.py`, `introloading.py`.

### Settings

`uigameoption.py`, `uisystemoption.py`.

### Utility modules

| File | Role |
|------|------|
| `localeinfo.py` | All localized UI strings |
| `constinfo.py` | Game-wide constants / enum values |
| `serverinfo.py` | Server IPs and ports |
| `colorinfo.py` | Color constants |
| `mousemodule.py` | Cursor management |
| `camModule.py` | Camera control |
| `playersettingmodule.py` | Save/load `metin2.cfg` |
| `servercommandparser.py` | Parses `ChatPacket(CHAT_TYPE_COMMAND, ...)` payloads from the server |
| `networkmodule.py` | Packet send wrappers |
| `emotion.py` | Emote commands |

## `uiscript/`

Window-layout definition files. Each is a Python dict tree consumed by `ui.PythonScriptLoader().LoadScriptFile(self, "uiscript/xxx.py")`. Example structure:

```python
window = {
    "name": "InventoryWindow",
    "x": 0, "y": 0,
    "style": ("movable", "float"),
    "width": 176, "height": 368,
    "children": [
        { "name": "TitleBar", "type": "titlebar", ... },
        { "name": "ItemSlot", "type": "grid_table", ... },
    ],
}
```

## Python ↔ C++

Python calls C++ via modules registered in `Py*Module.cpp` (see [../../../../srcs/client/UserInterface/claude.md](../../../../srcs/client/UserInterface/claude.md)). Modules: `app`, `net`, `player`, `chr`, `chrmgr`, `item`, `skill`, `guild`, `shop`, `background`, `ui`, `wndMgr`, ...

```python
import player, net, ui
level = player.GetLevel()
net.SendChatPacket("/help")
```

C++ → Python callbacks (e.g. `OnRecvWhisper`) work the other direction via `PyObject_CallFunction`.

## Server commands

Server pushes UI commands as `ChatPacket(CHAT_TYPE_COMMAND, "CommandName args...")`. The flow:

```
server → CHAT_TYPE_COMMAND packet → game.py → interfacemodule.py → target UI widget
```

`CHAT_MAX_LEN = 512` bytes, so server code must batch larger payloads across multiple commands.

## Conventions

- **Naming**: `ui*.py` for windows, `intro*.py` for pre-game screens, `*module.py` for shared modules, `*info.py` for config/constants.
- **Lazy creation**: instantiate windows only when first opened; hidden windows still process tick.
- **Error handling**: wrap risky code in `try / exception.Abort("Module.func")` — Python tracebacks end up in `syserr.txt`.
- **No client-side trust**: the server validates every action. Client-side checks are for UX, not security.

## Reusable local widgets

Project-local composite widgets (ours, not engine `ui.py`). Prefer these over re-implementing:

- **Notification badge — `uibadge.py`.** iOS-style red count chip on any taskbar button (Metin2 dark-outline art, `patch5/ymir work/ui/badge/notification_badge_{1,2}.png`, flat-`ui.Bar` fallback if the art pack lags). Name-keyed registry decouples the button owner from the data owner:
  - Owner of the button attaches once: `uibadge.Attach("<key>", button)` (in `uitaskbar.py`, inside the feature guard); `uibadge.ClearAll()` in `TaskBar.Destroy`.
  - Owner of the data pushes counts: `uibadge.SetCount("<key>", n)` — safe no-op if unattached; `0` hides, `>9` shows "9+".
  - **Semantics = unseen counter:** only ever climbs while the window is closed, cleared to `0` only when the player opens the window (never on a request expiring or a requester logging off). For a **server-backed** count (e.g. community friend requests) push the server truth (`GetRequestCount()`) so it persists across relog for free; for a **client-transient** count (e.g. party-finder join prompts) keep a monotonic `unseen*Count` on the window. Live keys: `"party_finder"`, `"messenger"`. `docs/NOTIFICATION_BADGES.md`.

## Cross-references

- C++ side: [../../../../srcs/client/UserInterface/](../../../../srcs/client/UserInterface/)
- Shared constants: [../../../../srcs/share/](../../../../srcs/share/)
- Game-data structs: [../../../../srcs/client/GameLib/](../../../../srcs/client/GameLib/)
