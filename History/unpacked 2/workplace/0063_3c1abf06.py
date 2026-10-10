# coding: latin_1

import app
import player

if app.ENABLE_EXTENDED_BATTLE_PASS or app.USE_ANTI_EXP:
	import net
if app.ENABLE_VOICE_CHAT:
	import uivoicechatconfig
if app.DEATHMATCH_EVENT:
	import uideathmatch
if app.ENABLE_REWARD_SYSTEM:
	import uiReward
	import uirewardspeed
if app.ENABLE_WINDOW_POSITION_SAVE:
	import uiwindowpositions
if app.__SKILL_TREE__:
	import uiSkillTree

if app.__AUTO_SKILL_READER__:
	import uiAutoSkillReader

if app.WHEEL_INGAME or app.ENABLE_DAILY_ALCHEMY_ORE or app.__SPIN_WHEEL_DUNGEON__:
	import uispinwheel

if app.ENABLE_ATTR_6TH_7TH:
	import uiAttr67Add
if app.ENABLE_MISSION_QUEST:
	import uimissionlist
	
if app.ADVANCED_BATTLE_PASS:
	import uibattlepass

if app.ENABLE_PARTY_WAR:
	import uipartywar
if app.ENABLE_PARTY_FINDER:
	import uipartyfinder
if app.ENABLE_GUILD_FINDER:
	import uiguildfinder
if app.QUICK_SELL_SYSTEM:
	import uiquicksell
import serverinfo
import constinfo
import background
import osfinfo
import systemSetting
import wndMgr
import chat
import uitaskbar
import uicharacter
import uititle
import uiinventory
import uidragonsoul
import uichat
import uimessenger

COMMUNITY_SYSTEM = getattr(app, "ENABLE_COMMUNITY_SYSTEM", 0)
if COMMUNITY_SYSTEM:
	import uicommunity
import guild
import ui
import uihelp
import uiwhisper
import uiwhisperchat
import uipointreset
import uishop
import uiexchange
import uisystem
import uirestart
import uitooltip
import uipvmbalanceintro
import uiminimap
import uiparty
import uisafebox
import uiguild
import uiquest
import uiprivateshopbuilder
import uicommon
import uibadge
import uirefine
import uiequipmentdialog
import uigamebutton
import uitip
import uicube
import miniMap
import grp
import uicuponcode
import uicouponadmin
from _weakref import proxy
# ACCESSORY_REFINE_ADD_METIN_STONE
import uiselectitem
# END_OF_ACCESSORY_REFINE_ADD_METIN_STONE
if app.ENABLE_GEM_SYSTEM:
	import uiselectitemex
import uiscriptlocale
import event
import localeinfo
if app.ENABLE_WINDOW_RESIZE:
	from resizeexpr import Expr
import item
if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
	import uiskillbookcombination
if app.USE_ACCE_SYSTEM:
	import uiacce
if app.ENABLE_EVENT_MANAGER:
	import uievent
if app.ENABLE_SKILL_LEARN_SYSTEM:
	import uinewlearnskill
import uichangelook
import shop
import saryongstory
import uibundlebox
if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
	import uispecialinventory
if app.ENABLE_12ZI:
	import ui12zi
import uiminigame

if app.ENABLE_MINI_GAME_OKEY:
	import uiminigamerumi
if app.ENABLE_ASLAN_TELEPORTPANEL:
	import uiteleportpanel

if app.ENABLE_GEM_SYSTEM:
	import uigemshop

if app.ENABLE_ANTI_MULTIPLE_FARM:
	import uiantimultiplefarm
	import anti_multiple_farm

if app.ENABLE_MYSHOP_DECO:
	import uimyshopdecoration
if app.ENABLE_SWITCHBOT:
	import uiswitchbot

if app.ENABLE_GROWTH_PET_SYSTEM:
	import uipetinfo 

if app.USE_OFFLINESHOP:
	import uiofflineshop_ae
	import offlineshop

if app.ENABLE_FISHING_GAME:
	import uifishinggame
if app.ENABLE_FISHING_GAME_BDO:
	import uifishingbdo
if app.ENABLE_MINI_GAME_BNW:
	import uiMiniGameBNW
if app.BL_REMOTE_SHOP:
	import uiremoteshop

if app.USE_AURA_SYSTEM:
	import uiaura

if app.ENABLE_MAILBOX:
	import uimailbox
if app.ENABLE_ITEMSHOP:
	import uiitemshop

if app.ENABLE_EXTENDED_BATTLE_PASS:
	import uibattlepassextended

if app.ENABLE_RENEWAL_PVP:
	import uipvp

if app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM:
	import uisetcustomattribute

if app.DOMINIUM_PVP_SYSTEM:
	import uidominium
if app.DOMINIUM_PVP_SYSTEM or app.DEFENSE_PVP_SYSTEM or app.CRYSTAL_PVP_SYSTEM: #app.TOURNAMENT_PVP_SYSTEM or 
	import uipvpevent
if app.ENABLE_PVP_ROUTES:
	import uiroutespvp
if app.DEFENSE_PVP_SYSTEM:
	import uidefense
if app.CRYSTAL_PVP_SYSTEM:
	import uicrystal

if app.ENABLE_NOTIFICATION_SYSTEM:
	import uinotification

if app.ENABLE_BIOLOG_SYSTEM:
	import uibiologmanager
	import nonplayer

if app.ENABLE_ULTIMATE_REGEN:
	import uitrack

if app.ENABLE_WORLDBOSS:
	import uiworldboss

if app.ENABLE_WORLDBOSS_V2_DAMAGE_METER:
	import uiworldbossdmgmeter

if app.ENABLE_HORSE_UPGRADE:
	import uihorseupgrade

if app.__BUFFI_SUPPORT__:
	import uicompanion
	import uicompanionupgrade
	import uicompanionhelp
	import uicompanionridehelp
	if app.ENABLE_GROWTH_PET_SYSTEM:
		import uipetupgrade
		import uipetupgradehelp
		import uipethelp

if app.USE_WHEEL_OF_FORTUNE:
	import uiwheeloffortune

if app.USE_PVP_TOURNAMENT:
	import pvp_tournament

if app.FAST_EQUIP_WORLDARD:
	import uifastequip

if app.ENABLE_PARTY_BOUNS:
	import uipartybonusdistribute

if app.USE_DUNGEON_INFO:
	import uidungeoninfo

if app.ENABLE_RENDER_TARGET:
	import uiRenderTarget

if app.__RANKING_SYSTEM__:
	import uiranknew

if app.USE_BL_FISH_EVENT:
	import uiminigamefishevent

if app.USE_PORTABLE_TELEPORT_WITH_UI:
	import uiteleport

IsQBHide = 0
IsWisperHide = 0

class Interface(object):
	CHARACTER_STATUS_TAB = 1
	CHARACTER_SKILL_TAB = 2

	class NewGoldChat(ui.Window):
		def __init__(self, parent = None, x = 0, y = 0):
			ui.Window.__init__(self)
			self.texts = {}
			self.parent = parent
			self.SpaceBet = 14
			self.maxY = 0
			self.x = x
			self.y = y
			self.ColorValue = 0xFFffeaa7
			
			self.show = self.Button(localeinfo.SHOW_YANG, x, y+3, self.showYang, 'sanyed_yang/btn_expand_normal.tga', 'sanyed_yang/btn_expand_over.tga', 'sanyed_yang/btn_expand_down.tga')
			self.hide = self.Button(localeinfo.HIDE_YANG, x, y+3, self.hideYang, 'sanyed_yang/btn_minimize_normal.tga', 'sanyed_yang/btn_minimize_over.tga', 'sanyed_yang/btn_minimize_down.tga')
			self.show.Hide()
			self.Show()

		def Button(self, tooltipText, x, y, func, UpVisual, OverVisual, DownVisual):
			button = ui.Button()
			if self.parent != None:
				button.SetParent(self.parent)
			button.SetPosition(x, y)
			button.SetUpVisual(UpVisual)
			button.SetOverVisual(OverVisual)
			button.SetDownVisual(DownVisual)
			button.SetToolTipText(tooltipText)
			button.Show()
			button.SetEvent(func)
			return button

		def showYang(self):
			for i in xrange(len(self.texts)):
				self.texts[i].Show()
			self.hide.Show()
			self.show.Hide()
			self.Show()

		def hideYang(self):
			for i in xrange(len(self.texts)):
				self.texts[i].Hide()
			self.hide.Hide()
			self.show.Show()
			self.Hide()
			
		def GetMaxY(self):
			return self.maxY

		def AddGoldValue(self, text):
			for i in xrange(len(self.texts)):
				if len(self.texts) == 10 and i == 0:
					self.texts[i].Hide()
				x, y = self.texts[i].GetLocalPosition()
				self.texts[i].SetPosition(x, y-self.SpaceBet)

			i = 0
			if len(self.texts) == 10:
				for i in xrange(len(self.texts)-1):
					self.texts[i] = self.texts[i+1]
				i = 9
			else:
				i = len(self.texts)
			
			self.texts[i] = ui.TextLine("Tahoma:14")
			if self.parent != None:
				self.texts[i].SetParent(self.parent)
			self.texts[i].SetPosition(self.x, self.y)
			self.texts[i].SetPackedFontColor(self.ColorValue)
			self.texts[i].SetHorizontalAlignRight()
			self.texts[i].SetOutline(TRUE)
			self.texts[i].SetText(text)
			if self.hide.IsShow():
				self.texts[i].Show()

			if self.hide.IsShow():
				x, y = self.texts[0].GetLocalPosition()
				x2, y2 = self.hide.GetLocalPosition()
				self.hide.SetPosition(x2, y-10)

		def ClearAll(self):
			self.Hide()
			self.texts = {}
			self.show.Hide()
			self.show = None
			self.hide.Hide()
			self.hide = None

		def OnRender(self):
			if len(self.texts) > 0 and self.hide.IsShow():
				x, y = self.hide.GetGlobalPosition()
				w, h = self.texts[0].GetTextSize()
				grp.SetColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.5))
				grp.RenderBar(x, y+h-6, 108, h*len(self.texts)+4)

	def __init__(self):
		systemSetting.SetInterfaceHandler(self)

		if app.USE_CRAFT_ITEM_SYSTEM:
			self.wnd_craft_item = None

		if app.USE_LOG_EXCHANGE:
			self.wndExchangeLog = None

		# if app.USE_NORTHWIND_DEEPS_DUNGEON:
		self.wndUIDamage = None

		if app.ENABLE_AUTO_SHOUT:
			self.wndChat = None

		if app.__RANKING_SYSTEM__:
			self.wndRanking = None

		if app.ENABLE_INGAME_WIKI:
			self.wndWiki = None
			self.wikiBuilderFunc = None

		if app.ENABLE_DAILY_ALCHEMY_ORE:
			self.wndSpinWheel = None

		if app.__SPIN_WHEEL_DUNGEON__:
			self.wndDungeonSpinWheel = None

		if app.__AUTO_SKILL_READER__:
			self.wndAutoSkillReader = None

		if app.ENABLE_ATTR_6TH_7TH:
			self.wndAttr67Add = None

		if app.__SKILL_TREE__:
			self.wndSkillTree = None

		self.windowOpenPosition = 0
		self.dlgWhisperWithoutTarget = None
		self.wndWhisperChat = None
		self.inputDialog = None
		self.tipBoard = None
		self.importantPopup = None
		self.bigBoard = None

		if app.USE_WHEEL_OF_FORTUNE:
			self.wndWheelofFortune=0

		if app.ENABLE_RENEWAL_PVP:
			self.wndPvP = None
		
		if app.ENABLE_12ZI:
			self.missionBoard = None
		self.wndDungeonHud = None
		self.wndChallengeHud = None
		if app.ENABLE_ITEMSHOP:
			self.wndItemShop=None
		#coupon
		self.wndCoupon = None
		self.wndCouponAdmin = None
		#coupon

		# ITEM_MALL
		self.mallPageDlg = None
		# END_OF_ITEM_MALL
		if app.ENABLE_CUBE_RENEWAL_WORLDARD:
			self.wndCubeRenewal = None


		self.wndTaskBar = None
		if app.BL_REMOTE_SHOP:
			self.wndRemoteShop = None
		if app.USE_OFFLINESHOP:
			self.wndShopOffline = None
			self.dlgOfflineShopDormant = None
		if app.WHEEL_INGAME:
			self.wndWheel = None
			self.wndSpin = None
			self.wndRewards = None

		self.wndCharacter = None
		self.wndInventory = None

		self.wndExpandedTaskBar = None
		self.wndDragonSoul = None
		self.wndDragonSoulRefine = None
		self.wndChat = None
		self.yangText = None
		self.wndMessenger = None
		self.wndCommunity = None
		self.friendRequestQueue = []
		self.friendRequestDialog = None
		self.unseenMessengerCount = 0
		if app.ENABLE_PARTY_FINDER:
			self.wndPartyFinder = None
		if app.ENABLE_GUILD_FINDER:
			self.wndGuildFinder = None
		self.wndMiniMap = None
		self.wndGuild = None
		if app.ENABLE_PARTY_WAR:
			self.wndPartywarBoard = None
			self.wndPartywarTimer = None
			self.wndPartywarButton = None
			self.wndPartywarPlayerBoard = None
		if app.QUICK_SELL_SYSTEM:
			self.wndQuickSell = None

		self.wndTitle = None

		self.wndGuildBuilding = None
		if app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM:
			self.wndSetCustomAttribute = None

		if app.ENABLE_VOICE_CHAT:
			self.wndVoiceChatConfig = None
			self.wndVoiceChatOverlay = None


		if app.ENABLE_FISHING_GAME:
			self.wndFishingGame = None
		if app.ENABLE_FISHING_GAME_BDO:
			self.wndFishingBdo = None

		if app.USE_DUNGEON_INFO:
			self.wndDungeonInfo = None

		if app.ENABLE_REWARD_SYSTEM:
			self.wndReward = None

		self.wndStoryInterface = None

		self.wndBundleBox = None

		if app.USE_DUNGEON_COOLDOWN_MANAGER:
			self.dungeonCooldownAlert = None

		if app.ENABLE_SKILL_LEARN_SYSTEM:
			self.wndLearnSkill = None

		if app.ENABLE_RENDER_TARGET:
			self.wndRenderTargetInterface = None

		if app.ENABLE_EVENT_MANAGER:
			self.wndEventOverview = None

		if app.USE_EVENT_MANAGER_EXPANDED:
			self.wndEventAlert = None

		if app.ENABLE_SWITCHBOT:
			self.wndSwitchbot = None
		if app.WJ_ENABLE_TRADABLE_ICON or app.ENABLE_MOVE_COSTUME_ATTR:
			self.OnTopWindow = None
			self.dlgShop = None
			self.dlgExchange = None
			self.privateShopBuilder = None
			self.wndSafebox = None

		if app.ENABLE_ANTI_MULTIPLE_FARM:
			self.wndAntiMultipleFarm = None


		if app.ENABLE_EXTENDED_BATTLE_PASS:
			self.wndBattlePassExtended = None
			self.isFirstOpeningExtBattlePass = False

		if app.ENABLE_NOTIFICATION_SYSTEM:
			self.wndNotificationCenter = None


		if app.ENABLE_ASLAN_TELEPORTPANEL:
			self.wndTeleportPanel = None

		if app.ENABLE_PARTY_BOUNS:
			self.wndPartyBonusWindow = None

		if app.USE_BL_FISH_EVENT:
			self.fish_game = None

		self.listGMName = {}
		self.wndQuestWindow = {}
		self.wndQuestWindowNewKey = 0
		self.privateShopAdvertisementBoardDict = {}
		self.guildScoreBoardDict = {}
		self.equipmentDialogDict = {}

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			self.wndSpecialInventory = None

		if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
			self.wndSkillBookCombination = None

		if app.ENABLE_MYSHOP_DECO:
			self.wndMyShopDeco = None

		self.wndMiniGame = None

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			self.wndChangeLook = None

		self.wndExpandedMoneyTaskBar = None

		if app.ENABLE_MAILBOX:
			self.mail_box = None

		if app.ENABLE_12ZI:
			self.wndBead = None

		if app.ENABLE_BIOLOG_SYSTEM:
			self.wndBiologManagerPanel = None
		
		if app.USE_PVP_TOURNAMENT:
			self.wndPvpTournamentAdmin = None
			
			if app.PVP_HAVE_GUI:
				self.wndPvpTournamentFights = None

		if app.FAST_EQUIP_WORLDARD:
			self.wndFastEquip = None

		if app.USE_ANTI_EXP:
			self.wndExpStatus = None

		if app.USE_COSTUME_ATTR_TRANSFER:
			self.wndAttrTransfer = None

		if getattr(app, "USE_QUICK_ATTR_TRANSFER", 0):
			self.wndQuickTransfer = None

		if app.USE_ACCE_ATTR_TRANSFER:
			self.wndAcceAttrTransfer = None

		if app.USE_ITEM_ATTR_BACKUP_MODE:
			self.wndItemBackupAttr = None

		if app.ENABLE_MINI_GAME_BNW:
			self.wndBNWGame = None

		self.uiAffectshower = None
		self.uitargetBoard = None

		if app.USE_PORTABLE_TELEPORT_WITH_UI:
			self.teleportWnd = None

		self.IsHideUiMode = False

		event.SetInterfaceWindow(self)

	def __del__(self):
		systemSetting.UnsetInterfaceHandler(None)

		if app.ENABLE_INGAME_WIKI:
			self.wndWiki = None
			self.wikiBuilderFunc = None

		event.SetInterfaceWindow(None)

	################################
	## Make Windows & Dialogs
	def __MakeUICurtain(self):
		wndUICurtain = ui.Bar("TOP_MOST")
		wndUICurtain.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())
		if app.ENABLE_WINDOW_RESIZE:
			wndUICurtain.SetResizeDic({"size" : (Expr("SCREEN_WIDTH"), Expr("SCREEN_HEIGHT"))})
		wndUICurtain.SetColor(0x77000000)
		wndUICurtain.Hide()
		self.wndUICurtain = wndUICurtain

	def OnMessengerAddFriendQuestion(self, name):
		if self.wndMessenger and self.wndMessenger.IsShow():
			if not self.friendRequestDialog:
				self.__OpenFriendRequestDialog(name)
			elif name != self.friendRequestDialog.name and name not in self.friendRequestQueue:
				self.friendRequestQueue.append(name)
			return
		if name in self.friendRequestQueue:
			return
		self.friendRequestQueue.append(name)
		self.unseenMessengerCount += 1
		uibadge.SetCount("messenger", self.unseenMessengerCount)
		fmt = getattr(localeinfo, "MESSENGER_REQUEST_WAITING", "%s sent you a friend request - open the friend list to answer.")
		if "%s" in fmt:
			chat.AppendChat(chat.CHAT_TYPE_INFO, fmt % name)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, fmt)

	def __OpenFriendRequestDialog(self, name):
		dlg = uicommon.QuestionDialog2()
		dlg.SetText1(localeinfo.MESSENGER_DO_YOU_ACCEPT_ADD_FRIEND_1 % (name))
		dlg.SetText2(localeinfo.MESSENGER_DO_YOU_ACCEPT_ADD_FRIEND_2)
		dlg.SetAcceptEvent(ui.__mem_func__(self.__OnAcceptFriendRequest))
		dlg.SetCancelEvent(ui.__mem_func__(self.__OnDenyFriendRequest))
		dlg.Open()
		dlg.name = name
		self.friendRequestDialog = dlg

	def __OnAcceptFriendRequest(self):
		self.__AnswerFriendRequest("y")
		return True

	def __OnDenyFriendRequest(self):
		self.__AnswerFriendRequest("n")
		return True

	def __AnswerFriendRequest(self, answer):
		dlg = self.friendRequestDialog
		if not dlg:
			return
		net.SendChatPacket("/messenger_auth %s %s" % (answer, dlg.name))
		dlg.Close()
		self.friendRequestDialog = None
		self.__ShowNextFriendRequest()

	def __ShowNextFriendRequest(self):
		if self.friendRequestDialog:
			return
		if not self.friendRequestQueue:
			return
		self.__OpenFriendRequestDialog(self.friendRequestQueue.pop(0))

	def __MakeMessengerWindow(self):
		if COMMUNITY_SYSTEM:
			self.__MakeCommunityWindow()
			return
		self.wndMessenger = uimessenger.MessengerWindow()
		if app.ENABLE_CHATTING_WINDOW_RENEWAL:
			self.wndMessenger.BindInterface(self)
		self.wndMessenger.SetWhisperButtonEvent(lambda n,i=proxy(self):i.OpenWhisperDialog(n))
		self.wndMessenger.SetGuildButtonEvent(ui.__mem_func__(self.ToggleGuildWindow))

	if COMMUNITY_SYSTEM:
		def __MakeCommunityWindow(self):
			self.wndCommunity = uicommunity.CommunityWindow()
			self.wndCommunity.SetWhisperEvent(lambda n,i=proxy(self):i.OpenWhisperDialog(n))
			self.wndCommunity.SetPartyInviteEvent(lambda n,i=proxy(self):i.CommunityInviteParty(n))
			self.wndCommunity.SetGuildButtonEvent(ui.__mem_func__(self.ToggleGuildWindow))
			if app.ENABLE_GUILD_FINDER:
				self.wndCommunity.SetGuildFinderEvent(ui.__mem_func__(self.ToggleGuildFinderWindow))
			self.wndMessenger = self.wndCommunity

		def CommunityInviteParty(self, name):
			net.SendChatPacket("/community_invite %s" % name)

		def ToggleCommunityWindow(self):
			if self.wndCommunity.IsShow():
				self.wndCommunity.Hide()
			else:
				self.wndCommunity.SetTop()
				self.wndCommunity.Show()
			self.wndCommunity.RefreshRequestBadge()

	if app.ENABLE_PARTY_FINDER:
		def __MakePartyFinderWindow(self):
			self.wndPartyFinder = uipartyfinder.PartyFinderWindow()
			self.wndPartyFinder.Hide()

		def TogglePartyFinderWindow(self):
			if not self.wndPartyFinder:
				self.__MakePartyFinderWindow()
			if self.wndPartyFinder.IsShow():
				self.wndPartyFinder.Hide()
			else:
				self.wndPartyFinder.SetTop()
				self.wndPartyFinder.Show()

		def OnPartyFinderBoard(self, serverNow, entries):
			if self.wndPartyFinder:
				self.wndPartyFinder.OnBoard(serverNow, entries)

		def OnPartyFinderJoinPrompt(self, pid, name, level, race):
			if not self.wndPartyFinder:
				self.__MakePartyFinderWindow()
			self.wndPartyFinder.OnJoinPrompt(pid, name, level, race)

		def OnPartyFinderJoinResult(self, result, leaderName):
			if self.wndPartyFinder:
				self.wndPartyFinder.OnJoinResult(result, leaderName)

	if app.ENABLE_GUILD_FINDER:
		def __MakeGuildFinderWindow(self):
			self.wndGuildFinder = uiguildfinder.GuildFinderWindow()
			self.wndGuildFinder.Hide()

		def ToggleGuildFinderWindow(self):
			if not self.wndGuildFinder:
				self.__MakeGuildFinderWindow()
			if self.wndGuildFinder.IsShow():
				self.wndGuildFinder.Close()
			else:
				self.wndGuildFinder.Open()

		def OpenGuildFinderApplications(self):
			if not self.wndGuildFinder:
				self.__MakeGuildFinderWindow()
			self.wndGuildFinder.OpenApplicationsTab()

		def OnGuildFinderList(self, entries, myAppGids):
			if self.wndGuildFinder:
				self.wndGuildFinder.OnList(entries, myAppGids)

		def OnGuildFinderDetail(self, guildID, leaderName, members, maxMembers, online, myApplied, desc):
			if self.wndGuildFinder:
				self.wndGuildFinder.OnDetail(guildID, leaderName, members, maxMembers, online, myApplied, desc)

		def OnGuildFinderResult(self, guildID, result):
			if self.wndGuildFinder:
				self.wndGuildFinder.OnResult(guildID, result)

		def OnGuildFinderInbox(self, guildID, mode, minLevel, desc, applicants):
			if self.wndGuildFinder:
				self.wndGuildFinder.OnInbox(guildID, mode, minLevel, desc, applicants)

		def OnGuildFinderBadge(self, count):
			# the first badge push lands at login, before the window has ever been built
			if self.wndGuildFinder:
				self.wndGuildFinder.OnBadge(count)
			else:
				uibadge.SetCount("guild_finder", count)

	def __MakeGuildWindow(self):
		self.wndGuild = uiguild.GuildWindow()
		if app.ENABLE_GUILD_FINDER:
			self.wndGuild.SetGuildFinderEvent(ui.__mem_func__(self.OpenGuildFinderApplications))

	if app.QUICK_SELL_SYSTEM:
		def __MakeQuickSell(self):
			self.wndQuickSell = uiquicksell.QuickSell()
			self.wndQuickSell.BindInterface(self)
			self.wndQuickSell.Hide()


	def __MakeTitleWindow(self):
		if not getattr(self, "wndTitle", None):
			self.wndTitle = uititle.TitleWindow()
			self.wndTitle.Hide()

	def ToggleTitleWindow(self):
		self.__MakeTitleWindow()
		if not self.wndTitle:
			return

		if self.wndTitle.IsShow():
			self.wndTitle.Close()
		else:
			self.wndTitle.Open()

	# TitleWinActive is pushed from session start, before the window exists.
	def RecvTitleWinBegin(self, activeId):
		if getattr(self, "wndTitle", None):
			self.wndTitle.RecvTitleWinBegin(activeId)

	def RecvTitleWinItem(self, payload):
		if getattr(self, "wndTitle", None):
			self.wndTitle.RecvTitleWinItem(payload)

	def RecvTitleWinEnd(self):
		if getattr(self, "wndTitle", None):
			self.wndTitle.RecvTitleWinEnd()

	def RecvTitleWinActive(self, activeId):
		if getattr(self, "wndTitle", None):
			self.wndTitle.RecvTitleWinActive(activeId)

	def __MakeChatWindow(self):
		wndChat = uichat.ChatWindow()

		wndChat.SetSize(wndChat.CHAT_WINDOW_WIDTH, 0)
		wndChat.SetPosition(wndMgr.GetScreenWidth()/2 - wndChat.CHAT_WINDOW_WIDTH/2, wndMgr.GetScreenHeight() - wndChat.EDIT_LINE_HEIGHT - 37)
		if app.ENABLE_WINDOW_RESIZE:
			wndChat.SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 - wndChat.CHAT_WINDOW_WIDTH/2, Expr("SCREEN_HEIGHT") - wndChat.EDIT_LINE_HEIGHT - 37)})
		wndChat.SetHeight(200)
		wndChat.Refresh()
		wndChat.Show()

		self.wndChat = wndChat
		self.wndChat.BindInterface(self)
		self.wndChat.SetSendWhisperEvent(ui.__mem_func__(self.OpenWhisperDialogWithoutTarget))
		self.wndChat.SetOpenChatLogEvent(ui.__mem_func__(self.ToggleChatLogWindow))

		# if app.ENABLE_AUTO_SHOUT:
			# self.wndChat.SetInterface(self) 

		if self.yangText:
			self.yangText.Hide()
		yangText = self.NewGoldChat(None, wndMgr.GetScreenWidth()/2 - wndChat.CHAT_WINDOW_WIDTH/2 + 600, wndMgr.GetScreenHeight() - wndChat.EDIT_LINE_HEIGHT - 37 + 9)
		if app.ENABLE_WINDOW_RESIZE:
			yangText.SetResizeDic({"position" : (Expr("SCREEN_WIDTH")/2 - wndChat.CHAT_WINDOW_WIDTH/2 + 600, Expr("SCREEN_HEIGHT") - wndChat.EDIT_LINE_HEIGHT - 37 + 9)})
		self.yangText = yangText

	def __MakeTaskBar(self):
		wndTaskBar = uitaskbar.TaskBar()
		wndTaskBar.LoadWindow()
		self.wndTaskBar = wndTaskBar
		self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_CHARACTER, ui.__mem_func__(self.ToggleCharacterWindowStatusPage))
		self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_INVENTORY, ui.__mem_func__(self.ToggleInventoryWindow))
		self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_MESSENGER, ui.__mem_func__(self.ToggleMessenger))
		self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_SYSTEM, ui.__mem_func__(self.ToggleSystemDialog))
		if app.ENABLE_PARTY_FINDER:
			self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_PARTY_FINDER, ui.__mem_func__(self.TogglePartyFinderWindow))

		if uitaskbar.TaskBar.IS_EXPANDED:
			self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_EXPAND, ui.__mem_func__(self.ToggleExpandedButton))
			self.wndExpandedTaskBar = uitaskbar.ExpandedTaskBar()
			self.wndExpandedTaskBar.LoadWindow()

			if app.ENABLE_GROWTH_PET_SYSTEM:
				self.wndExpandedTaskBar.SetToggleButtonEvent(uitaskbar.ExpandedTaskBar.BUTTON_PET_INFO, ui.__mem_func__(self.TogglePetInformationWindow))

			if app.ENABLE_SWITCHBOT:
				self.wndExpandedTaskBar.SetToggleButtonEvent(uitaskbar.ExpandedTaskBar.BUTTON_SWITCH_BOT, ui.__mem_func__(self.ToggleSwitchbotWindow))

			if app.ENABLE_INGAME_WIKI:
				self.wndExpandedTaskBar.SetToggleButtonEvent(uitaskbar.ExpandedTaskBar.BUTTON_WIKI, ui.__mem_func__(self.ToggleWikiWindow))

			if app.ADVANCED_BATTLE_PASS:
				self.wndExpandedTaskBar.SetToggleButtonEvent(uitaskbar.ExpandedTaskBar.BUTTON_BP, ui.__mem_func__(self.ShowBattlePass))

			if app.ENABLE_EVENT_MANAGER:
				self.wndExpandedTaskBar.SetToggleButtonEvent(uitaskbar.ExpandedTaskBar.BUTTON_EVENT_INFO, ui.__mem_func__(self.ToggleInGameEvent))


			if app.FAST_EQUIP_WORLDARD:
				self.wndExpandedTaskBar.SetToggleButtonEvent(uitaskbar.ExpandedTaskBar.BUTTON_CHANGE_EQUIP, ui.__mem_func__(self.OpenFastEquip))

			if app.ENABLE_REWARD_SYSTEM:
				self.wndExpandedTaskBar.SetToggleButtonEvent(uitaskbar.ExpandedTaskBar.BUTTON_REWARD, ui.__mem_func__(self.OpenRewardWindow))

			if app.USE_LOG_EXCHANGE:
				self.wndExpandedTaskBar.SetToggleButtonEvent(uitaskbar.ExpandedTaskBar.BUTTON_LOG, ui.__mem_func__(self.OpenExchangeLog))

			if app.ENABLE_MISSION_QUEST:
				self.wndExpandedTaskBar.SetToggleButtonEvent(uitaskbar.ExpandedTaskBar.BUTTON_MISSION, ui.__mem_func__(self.ToggleMissionQuest))

			if app.ENABLE_NOTIFICATION_SYSTEM:
				self.wndExpandedTaskBar.SetToggleButtonEvent(uitaskbar.ExpandedTaskBar.BUTTON_NOTIFICATION, ui.__mem_func__(self.ToggleNotificationHistory))

			self.wndExpandedTaskBar.SetToggleButtonEvent(uitaskbar.ExpandedTaskBar.BUTTON_SARYONG, ui.__mem_func__(self.ToggleStoryWindow))


			if self.wndChat:
				self.wndChat.SetChatStateChangeEvent(ui.__mem_func__(self.__OnChatStateChange))

		else:
			self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_CHAT, ui.__mem_func__(self.ToggleChat))

		self.wndEnergyBar = None
		if app.ENABLE_ENERGY_SYSTEM:
			wndEnergyBar = uitaskbar.EnergyBar()
			wndEnergyBar.LoadWindow()
			self.wndEnergyBar = wndEnergyBar

		if app.BL_REMOTE_SHOP:
			self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_REMOTE_SHOP, ui.__mem_func__(self.OpenRemoteShop))

		if app.USE_OFFLINESHOP:
			self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_OFFLINE_SHOP, ui.__mem_func__(self.OpenOfflineShop))

		if app.ENABLE_ANTI_MULTIPLE_FARM:
			self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_ANTI_MULTIPLE_FARM, ui.__mem_func__(self.ToggleAntiMultipleFarmWindow))

		# self.wndTaskBar.SetToggleButtonEvent(uitaskbar.TaskBar.BUTTON_EXPAND_MONEY, ui.__mem_func__(self.ToggleExpandedMoneyButton))
		self.wndExpandedMoneyTaskBar = uitaskbar.ExpandedMoneyTaskBar()

	def __MakeParty(self):
		wndParty = uiparty.PartyWindow()
		wndParty.Hide()
		self.wndParty = wndParty

	if app.CRYSTAL_PVP_SYSTEM:
		def __MakeCrystalWindow(self):
			self.wndCrystal = uicrystal.Window()
			self.wndCrystal.Initialize()
			self.wndCrystal.Hide()
			
		def AddCrystalResultWindow(self, leftTime, membersOnline_A, membersOnline_B, crystal_A, crystal_B):
			self.wndCrystal.Append([int(leftTime), str(membersOnline_A), str(membersOnline_B), str(crystal_A), str(crystal_B)])	

	if app.DOMINIUM_PVP_SYSTEM:
		def __MakeDominiumWindow(self):
			self.wndDominium = uidominium.Window()
			self.wndDominium.Initialize()
			self.wndDominium.Hide()
			
		def AddDominiumResultWindow(self, leftTime, membersOnline_A, membersOnline_B, score_A, score_B, circle_A, circle_B, circle_C, circle_BR, circle_BB):
			self.wndDominium.Append([int(leftTime), str(membersOnline_A), str(membersOnline_B), str(score_A), str(score_B), circle_A, circle_B, circle_C, circle_BR, circle_BB])		

	if app.DEFENSE_PVP_SYSTEM:
		def __MakeDefenseWindow(self):
			self.wndDefense = uidefense.Window()
			self.wndDefense.Initialize()
			self.wndDefense.Hide()
			
		def AddDefenseResultWindow(self, leftTime, membersOnline_A, membersOnline_B, metin_A, metin_B):
			self.wndDefense.Append([int(leftTime), str(membersOnline_A), str(membersOnline_B), str(metin_A), str(metin_B)])	

	if app.DOMINIUM_PVP_SYSTEM or app.DEFENSE_PVP_SYSTEM or app.CRYSTAL_PVP_SYSTEM: #app.TOURNAMENT_PVP_SYSTEM or 
		def __MakePvPEventWindow(self):
			self.wndPvPEvent = uipvpevent.Window()
			self.wndPvPEvent.Initialize()
			self.wndPvPEvent.Hide()

		def AddPvPEventResultWindow(self, type, kills, others, points, team, role):
			self.wndPvPEvent.AddStatsPvP([type, kills, others, points, team, role])

	def __MakeGameButtonWindow(self):
		wndGameButton = uigamebutton.GameButtonWindow()
		wndGameButton.SetTop()
		wndGameButton.Show()
		wndGameButton.SetButtonEvent("STATUS", ui.__mem_func__(self.__OnClickStatusPlusButton))
		wndGameButton.SetButtonEvent("SKILL", ui.__mem_func__(self.__OnClickSkillPlusButton))
		wndGameButton.SetButtonEvent("QUEST", ui.__mem_func__(self.__OnClickQuestButton))
		wndGameButton.SetButtonEvent("HELP", ui.__mem_func__(self.__OnClickHelpButton))
		wndGameButton.SetButtonEvent("BUILD", ui.__mem_func__(self.__OnClickBuildButton))

		if app.USE_DUNGEON_INFO and app.USE_DUNGEON_INFO_ADDON_LEVEL_CAP:
			wndGameButton.SetButtonEvent("LEVEL_CAP", ui.__mem_func__(self.__DungeonInfoToggleCapLevel))

		if app.ENABLE_REWARD_SYSTEM:
			wndGameButton.SetButtonEvent("CHALLENGE", ui.__mem_func__(self.__OnClickChallengeMapButton))

		self.wndGameButton = wndGameButton

	def __IsChatOpen(self):
		return True

	def __MakeWindows(self):
		if app.ENABLE_FISHING_GAME:
			self.wndFishingGame = uifishinggame.FishGame()
		if app.ENABLE_FISHING_GAME_BDO:
			self.wndFishingBdo = uifishingbdo.FishingBdoWindow()

		self.wndCharacter = uicharacter.CharacterWindow()
#coupon:
		#self.wndCoupon = uicuponcode.CouponWindow()
		self.wndCouponAdmin = uicouponadmin.CouponWindow()
		
#coupon
		if app.ENABLE_PARTY_BOUNS:
			self.wndPartyBonusWindow = uipartybonusdistribute.PartyBonusDistributeWindow()
			self.wndCharacter.wndPartyBonusWindow = proxy(self.wndPartyBonusWindow)

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			self.wndSpecialInventory = uispecialinventory.SpecialInventoryWindow()
			self.wndSpecialInventory.BindInterfaceClass(self)

		self.wndInventory = uiinventory.InventoryWindow()
		self.wndInventory.BindInterfaceClass(self)

		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			self.wndDragonSoul = uidragonsoul.DragonSoulWindow()
			self.wndDragonSoul.BindInterfaceClass(self)
			self.wndDragonSoulRefine = uidragonsoul.DragonSoulRefineWindow()
		else:
			wndDragonSoul = None
			wndDragonSoulRefine = None

		self.wndMiniMap = uiminimap.MiniMap()
		self.wndSafebox = uisafebox.SafeboxWindow()
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.wndSafebox.BindInterface(self)

		if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
			self.wndSkillBookCombination = uiskillbookcombination.SkillBookCombinationWindow()

		if app.ENABLE_ATTR_6TH_7TH:
			wndAttr67Add = uiAttr67Add.Attr67AddWindow()
			if app.WJ_ENABLE_TRADABLE_ICON:
				wndAttr67Add.BindInterface(self)
				wndAttr67Add.SetInven(self.wndInventory)
			self.wndAttr67Add = wndAttr67Add

		if app.ENABLE_MYSHOP_DECO:
			self.wndMyShopDeco = uimyshopdecoration.MyShopDecoration()
		if app.ENABLE_SKILL_LEARN_SYSTEM:
			self.wndLearnSkill = uinewlearnskill.SkillLearnWindow()

		self.wndMall = uisafebox.MallWindow()

		wndChatLog = uichat.ChatLogWindow()
		wndChatLog.BindInterface(self)
		if app.BL_REMOTE_SHOP:
			self.wndRemoteShop = uiremoteshop.RemoteShopDialog()

		if app.USE_OFFLINESHOP:
			self.wndShopOffline = uiofflineshop_ae.OfflineShopWindow()
			self.wndShopOffline.Hide()

		self.wndChatLog = wndChatLog
		if app.ENABLE_PARTY_WAR:
			self.wndPartywarBoard = uipartywar.PartywarBoardWindow()
			self.wndPartywarTimer = uipartywar.PartywarTimerWindow()
			self.wndPartywarButton = uipartywar.PartyWarButton()
		if app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM:
			self.wndSetCustomAttribute = uisetcustomattribute.SetCustomAttributeWindow()
			self.wndSetCustomAttribute.BindInterface(self)
			self.wndSetCustomAttribute.SetInven(self.wndInventory)

		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			self.wndDragonSoul.SetDragonSoulRefineWindow(self.wndDragonSoulRefine)
			self.wndDragonSoulRefine.SetWindows(self.wndInventory, self.wndDragonSoul)
			self.wndInventory.SetDragonSoulRefineWindow(self.wndDragonSoulRefine)

		if app.ENABLE_EVENT_MANAGER and not app.USE_EVENT_MANAGER_EXPANDED:
			self.wndEventOverview = uievent.EventOverview()

		if app.ENABLE_SWITCHBOT:
			self.wndSwitchbot = uiswitchbot.SwitchbotWindow()

		if app.USE_AURA_SYSTEM:
			wndAura = uiaura.AuraWindow()

			self.wndAura = wndAura
		if app.ENABLE_MAILBOX:
			self.mail_box = uimailbox.MailBox()
			self.mail_box.BindInterface(self)
			self.mail_box.SetInven(self.wndInventory)
			self.mail_box.SetDSWindow(self.wndDragonSoul)

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			self.wndChangeLook = uichangelook.ChangeLookWindow()

		if app.ENABLE_GROWTH_PET_SYSTEM:
			self.wndPetInfoWindow = uipetinfo.PetInformationWindow()
			self.wndPetInfoWindow.BindInterfaceClass(self)
			self.wndInventory.SetPetHatchingWindow(self.wndPetInfoWindow.GetPetHatchingWindow())
			self.wndInventory.SetPetFeedWindow(self.wndPetInfoWindow.GetPetFeedWindow())
			self.wndInventory.SetPetNameChangeWindow(self.wndPetInfoWindow.GetPetNameChangeWindow())

		if app.ENABLE_BIOLOG_SYSTEM:
			self.wndBiologManagerPanel = uibiologmanager.BiologManager()
			#self.wndBiologManager["ALERT"] = uibiologmanager.BiologManager_Alert()
		
		if app.ENABLE_ULTIMATE_REGEN:
			self.wndTrackWindow = uitrack.TrackWindow()

		if app.ENABLE_WORLDBOSS:
			self.wndWorldBoss = uiworldboss.WorldBossWindow()
			if app.ENABLE_ULTIMATE_REGEN and self.wndTrackWindow:
				self.wndWorldBoss.SetTrackWindow(self.wndTrackWindow)

		if app.ENABLE_WORLDBOSS_V2_DAMAGE_METER:
			self.wndWBDamageMeter = uiworldbossdmgmeter.WorldBossDamageMeter()

		if app.ENABLE_HORSE_UPGRADE:
			self.wndHorseUpgrade = uihorseupgrade.HorseUpgradeWindow()

		if app.__BUFFI_SUPPORT__:
			# The buffi tooltip cache lives at module level in constinfo, and Python modules survive
			# character swaps within the same client process -- without this reset the PREVIOUS
			# character's buffi (INT/level/name/ores) leaked into the new character's summon-scroll
			# tooltip until some status push happened to arrive. Reset to defaults on every game
			# entry; the server's login status push (Entergame -> SendStatus) repopulates it.
			constinfo.BUFFI_SUMMONED    = 0
			constinfo.BUFFI_TOOLTIP_INT = 90
			constinfo.BUFFI_TT_INT      = 0
			constinfo.BUFFI_TT_LEVEL    = 0
			constinfo.BUFFI_TT_NAME     = ""
			constinfo.BUFFI_TT_ORES     = (0, 0, 0)
			constinfo.BUFFI_TT_EXPIRE   = 0
			self.wndCompanion = uicompanion.CompanionWindow()
			self.wndCompanion.interface = self   # back-ref so the Companion window can open the auto-skill-reader / Upgrade window
			self.wndCompanion.Hide()
			self.wndCompanionUpgrade = uicompanionupgrade.CompanionUpgradeWindow()
			self.wndCompanionUpgrade.Hide()
			self.wndCompanionHelp = uicompanionhelp.CompanionHelpWindow()
			self.wndCompanionHelp.interface = self   # back-ref -> shared skill tooltip for the unlocked-buff icons
			self.wndCompanionHelp.Hide()
			self.wndCompanionRideHelp = uicompanionridehelp.CompanionRideHelpWindow()
			self.wndCompanionRideHelp.interface = self
			self.wndCompanionRideHelp.Hide()
			if app.ENABLE_GROWTH_PET_SYSTEM:
				self.wndPetUpgrade = uipetupgrade.PetUpgradeWindow()
				self.wndPetUpgrade.interface = self   # back-ref: evolve gate + legacy pet-window reuse
				self.wndPetUpgrade.Hide()
				self.wndPetSkillUpgrade = uipetupgrade.PetSkillUpgradeDialog()
				self.wndPetSkillUpgrade.interface = self
				self.wndPetSkillUpgrade.Hide()
				self.wndPetUpgradeHelp = uipetupgradehelp.PetUpgradeHelpWindow()
				self.wndPetUpgradeHelp.interface = self   # back-ref: evolve-level single source
				self.wndPetUpgradeHelp.Hide()
				self.wndPetHelp = uipethelp.PetHelpWindow()
				self.wndPetHelp.interface = self   # back-ref: evolve-level single source
				self.wndPetHelp.Hide()

		if app.USE_DUNGEON_INFO:
			self.wndDungeonInfo = uidungeoninfo.DungeonInfoWindow()

		if app.ENABLE_REWARD_SYSTEM:
			if serverinfo.GetServerID() == serverinfo.SPEED_SERVER_KEY:
				self.wndReward = uirewardspeed.RewardWindow()
			else:
				self.wndReward = uirewardspeed.RewardWindow()

		self.wndStoryInterface = saryongstory.SaryongStoryWindow()

		if app.USE_EVENT_MANAGER_EXPANDED:
			self.wndEventAlert = uievent.EventAlert()
			self.wndEventAlert.BindInterface(self)

	def __MakeDialogs(self):
		if app.ENABLE_ASLAN_TELEPORTPANEL:
			self.wndTeleportPanel = uiteleportpanel.TeleportPanel()
		if app.ENABLE_EXTENDED_BATTLE_PASS:
			self.wndBattlePassExtended = uibattlepassextended.BattlePassWindow()

		self.dlgExchange = uiexchange.ExchangeDialog()
		self.dlgExchange.LoadDialog()
		self.dlgExchange.SetCenterPosition()
		self.dlgExchange.Hide()

		self.dlgPointReset = uipointreset.PointResetDialog()
		self.dlgPointReset.LoadDialog()
		self.dlgPointReset.Hide()

		self.dlgShop = uishop.ShopDialog()
		self.dlgShop.LoadDialog()
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.dlgShop.BindInterface(self)
		self.dlgShop.Hide()

		self.dlgRestart = uirestart.RestartDialog()
		self.dlgRestart.LoadDialog()
		self.dlgRestart.Hide()

		self.dlgSystem = uisystem.SystemDialog()
		self.dlgSystem.LoadDialog()
		self.dlgSystem.SetOpenHelpWindowEvent(ui.__mem_func__(self.OpenHelpWindow))

		self.dlgSystem.Hide()

		self.dlgPassword = uisafebox.PasswordDialog()
		self.dlgPassword.Hide()

		self.hyperlinkItemTooltip = uitooltip.HyperlinkItemToolTip()
		self.hyperlinkItemTooltip.Hide()

		self.tooltipItem = uitooltip.ItemToolTip()

		if app.ENABLE_DS_SET:
			self.tooltipItem.BindInterface(self)

		self.tooltipItem.Hide()

		self.tooltipSkill = uitooltip.SkillToolTip()
		self.tooltipSkill.Hide()
		
		self.privateShopBuilder = uiprivateshopbuilder.PrivateShopBuilder()
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.privateShopBuilder.BindInterface(self)
			self.privateShopBuilder.SetInven(self.wndInventory)
		self.privateShopBuilder.Hide()

		if uirefine.ENABLE_REFINE_RENEWAL:
			self.dlgRefineNew = uirefine.RefineDialogRenewal()
		else:
			self.dlgRefineNew = uirefine.RefineDialogNew()
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.dlgRefineNew.SetInven(self.wndInventory)
		self.dlgRefineNew.Hide()

		if app.ENABLE_GROWTH_PET_SYSTEM:
			self.tooltipPetSkill = uitooltip.PetSkillToolTip()
			self.tooltipPetSkill.Hide()

		if app.ENABLE_PVP_ROUTES:
			self.wndRoutesPvPSystem = uiroutespvp.RoutesPvPWindow()
			self.wndRoutesPvPSystem.BindInterface(self)
			self.wndRoutesPvPSystem.Hide()

		if app.ENABLE_MISSION_QUEST:
			import missionhelper
			self.wndMissionQuest = uimissionlist.MissionListWindow()
			self.wndMissionQuest.Hide()
			missionhelper.SetMissionWindow(self.wndMissionQuest)

		if app.ADVANCED_BATTLE_PASS:
			self.wndBattlePass = uibattlepass.BattlePassWindow()
			self.wndBattlePass.Hide()


	def __MakeHelpWindow(self):
		self.wndHelp = uihelp.HelpWindow()
		self.wndHelp.LoadDialog()
		self.wndHelp.SetCloseEvent(ui.__mem_func__(self.CloseHelpWindow))
		self.wndHelp.Hide()

	def ShowImportantPopup(self, text):
		if self.importantPopup:
			self.importantPopup.ShowPopup(text)

	def __MakeTipBoard(self):
		if app.__RENEWAL_NOTICE__:
			self.tipBoard = uitip.TipBoardNew()
		else:
			self.tipBoard = uitip.TipBoard()
		self.tipBoard.Hide()

		self.importantPopup = uitip.ImportantPopup()
		self.importantPopup.Hide()

		self.bigBoard = uitip.BigBoard()
		self.bigBoard.Hide()
		if app.ENABLE_12ZI:
			self.missionBoard = uitip.MissionBoard()
			self.missionBoard.Hide()

	if app.ENABLE_ANTI_MULTIPLE_FARM:
		def __MakeAntiMultipleFarmWnd(self):
			self.wndAntiMultipleFarm = uiantimultiplefarm.AntiMultipleFarmWnd()
			self.wndAntiMultipleFarm.Hide()

	if app.USE_ACCE_SYSTEM:
		def __MakeAcceWindow(self):
			self.wndAcceCombine = uiacce.CombineWindow()
			self.wndAcceCombine.LoadWindow()
			if app.WJ_ENABLE_TRADABLE_ICON:
				self.wndAcceCombine.BindInterface(self)
				if self.wndInventory:
					self.wndAcceCombine.SetInven(self.wndInventory)

				if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
					if self.wndSpecialInventory:
						self.wndAcceCombine.SetSpecialInven(self.wndSpecialInventory)

			self.wndAcceCombine.Hide()

			self.wndAcceAbsorption = uiacce.AbsorbWindow()
			self.wndAcceAbsorption.LoadWindow()
			if app.WJ_ENABLE_TRADABLE_ICON:
				self.wndAcceAbsorption.BindInterface(self)
				if self.wndInventory:
					self.wndAcceAbsorption.SetInven(self.wndInventory)

				if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
					if self.wndSpecialInventory:
						self.wndAcceAbsorption.SetSpecialInven(self.wndSpecialInventory)

			self.wndAcceAbsorption.Hide()

			if self.wndInventory:
				self.wndInventory.SetAcceWindow(self.wndAcceCombine, self.wndAcceAbsorption)

	def __MakeCubeWindow(self):
		self.wndCube = uicube.CubeWindow()
		self.wndCube.LoadWindow()
		self.wndCube.Hide()

	def __MakeCubeResultWindow(self):
		self.wndCubeResult = uicube.CubeResultWindow()
		self.wndCubeResult.LoadWindow()
		self.wndCubeResult.Hide()
	if app.ENABLE_WINDOW_RESIZE:
		def UpdateUI(self):
			# Force the bottom HUD to the new screen bottom.  The resize walk re-stretched the
			# taskbar's base-board width (child rect) but left the root window at the old Y, so
			# pin it here (post-walk) the same way a warp re-layout does.
			if self.wndTaskBar:
				self.wndTaskBar.SetPosition(0, wndMgr.GetScreenHeight() - 37)
			if self.wndEnergyBar:
				self.wndEnergyBar.SetPosition(0, wndMgr.GetScreenHeight() - 55)
			if self.wndExpandedMoneyTaskBar:
				self.wndExpandedMoneyTaskBar.SetPosition(wndMgr.GetScreenWidth() - self.wndExpandedMoneyTaskBar.GetWidth(), wndMgr.GetScreenHeight() - 65)
			if self.wndExpandedTaskBar:
				self.wndExpandedTaskBar.RePositionButton()
			self.__ArrangeQuestButton()
			self.__ArrangeWhisperButton()
			if self.wndChat:
				self.wndChat.OnResize()
				if self.wndChat.btnChatSizing:
					self.wndChat.btnChatSizing.OnResize()
				self.wndChat.Refresh()
			# Re-attach code-positioned sub-panels (bravecape expand, character bonus/party/
			# alignment/CP) to their parent AFTER the resize walk repositioned the parents.
			if self.wndInventory and self.wndInventory.IsShow() and hasattr(self.wndInventory, "OnMoveWindow"):
				(ix, iy) = self.wndInventory.GetGlobalPosition()
				self.wndInventory.OnMoveWindow(ix, iy)
			if self.wndCharacter and self.wndCharacter.IsShow() and hasattr(self.wndCharacter, "OnMoveWindow"):
				(cx, cy) = self.wndCharacter.GetGlobalPosition()
				self.wndCharacter.OnMoveWindow(cx, cy)

	if app.DEATHMATCH_EVENT:
		def __MakeDTEventWindow(self):
			self.wndDTInterface = uideathmatch.Window()
			self.wndDTInterface.Initialize()
			self.wndDTInterface.Hide()
			
		def AddDTInformation(self, kills, death, kill_owner, name_owner):
			self.wndDTInterface.Append([str(kills), str(death), str(kill_owner), str(name_owner)])
			

	if app.ENABLE_MINI_GAME_OKEY:
		def __MakeCardsInfoWindow(self):
			self.wndCardsInfo = uiminigamerumi.CardsInfoWindow()
			self.wndCardsInfo.LoadWindow()
			self.wndCardsInfo.Hide()
			self.wndCardsSimpleWaiting = uiminigamerumi.CardsSimpleWaitingPage(self.wndCardsInfo)
			self.wndCardsInfo.SetSimpleWaitingPage(self.wndCardsSimpleWaiting)

		def __MakeCardsWindow(self):
			self.wndCards = uiminigamerumi.CardsWindow()
			self.wndCards.LoadWindow()
			self.wndCards.Hide()

		def __MakeCardsIconWindow(self):
			self.wndCardsIcon = uiminigamerumi.IngameWindow()
			self.wndCardsIcon.LoadWindow()
			self.wndCardsIcon.Hide()

	# ACCESSORY_REFINE_ADD_METIN_STONE
	def __MakeItemSelectWindow(self):
		self.wndItemSelect = uiselectitem.SelectItemWindow()
		self.wndItemSelect.Hide()

	if app.ADVANCED_BATTLE_PASS:
		def __BoardBattlePass(self):
			import uibattlepass
			self.wndBattlePass = uibattlepass.BattlePassWindow()
			self.wndBattlePass.Hide()

	if app.ENABLE_GEM_SYSTEM:
		def __MakeItemSelectWindowEx(self):
			self.wndItemSelectEx = uiselectitemex.SelectItemWindowEx()
			self.wndItemSelectEx.Hide()

		def __MakeGemGui(self):
			self.wndGemG = uigemshop.SelectGems()
			self.wndGemG.LoadWindow()
			self.wndGemG.Hide()

			self.wndGemM = uigemshop.SelectGemsShop()
			self.wndGemM.LoadWindow()
			self.wndGemM.Hide()

	# END_OF_ACCESSORY_REFINE_ADD_METIN_STONE

	if app.ENABLE_CUBE_RENEWAL_WORLDARD:
		def __MakeCubeRenewal(self):
			import uicuberenewal
			self.wndCubeRenewal = uicuberenewal.CubeRenewalWindows()
			self.wndCubeRenewal.Hide()

	if app.USE_ANTI_EXP:
		def __ExpStatusClick(self):
			net.SendChatPacket("/switch_exp_status")

		def __ExpStatusOnIn(self):
			if self.wndExpStatus:
				if player.CanReceiveExp():
					self.wndExpStatus.SetDiffuseColor(1.0, 0.0, 0.0, 1.0)
				else:
					self.wndExpStatus.SetDiffuseColor(189.0, 195.0, 199.0, 1.0)

		def __ExpStatusOnOut(self):
			if self.wndExpStatus:
				if player.CanReceiveExp():
					self.wndExpStatus.SetDiffuseColor(189.0, 195.0, 199.0, 1.0)
				else:
					self.wndExpStatus.SetDiffuseColor(1.0, 0.0, 0.0, 1.0)

	def MakeInterface(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.Load()

		if app.ENABLE_12ZI:
			self.__MakeTipBoard()	# ENABLE_12ZI
		self.__MakeMessengerWindow()
		self.__MakeGuildWindow()
		self.__MakeChatWindow()
		self.__MakeParty()
		self.__MakeWindows()
		self.__MakeDialogs()
		if app.ENABLE_GEM_SYSTEM:
			self.__MakeGemGui()

		self.__MakeUICurtain()
		self.__MakeTaskBar()
		self.__MakeGameButtonWindow()
		self.MakeDungeonTimerWindow()##hydra part
		if app.ENABLE_PRIVATE_INSTANCE_LOBBY:
			self.__MakeChaosReturnButton()
		if app.ENABLE_PIL_DUNGEON:
			self.__MakeFastEnterOverlay()
		self.__MakeHelpWindow()
		if app.ENABLE_CUBE_RENEWAL_WORLDARD:
			self.__MakeCubeRenewal()
		if app.ENABLE_ANTI_MULTIPLE_FARM:
			self.__MakeAntiMultipleFarmWnd()
		if app.USE_ACCE_SYSTEM:
			self.__MakeAcceWindow()

		if app.CRYSTAL_PVP_SYSTEM:
			self.__MakeCrystalWindow()
		if app.DEFENSE_PVP_SYSTEM:
			self.__MakeDefenseWindow()
		if app.DOMINIUM_PVP_SYSTEM:
			self.__MakeDominiumWindow()
		if app.DOMINIUM_PVP_SYSTEM or app.DEFENSE_PVP_SYSTEM or app.CRYSTAL_PVP_SYSTEM: #app.TOURNAMENT_PVP_SYSTEM or 
			self.__MakePvPEventWindow()
		if app.DEATHMATCH_EVENT:
			self.__MakeDTEventWindow()
		
		self.__MakeCubeWindow()
		
		if app.ENABLE_VOICE_CHAT:
			self.wndVoiceChatConfig = uivoicechatconfig.VoiceChatConfig()
			self.wndVoiceChatOverlay = uivoicechatconfig.SpeakerQueue()

		if app.ENABLE_NOTIFICATION_SYSTEM:
			self.wndNotificationCenter = uinotification.NotificationCenter()
			self.wndNotificationCenter.SetInterface(self)

		self.wndStoryInterface = saryongstory.SaryongStoryWindow()

		self.wndBundleBox = uibundlebox.BundleBoxWindow()
		self.wndBundleBox.SetInterface(self)
		self.wndBundleBox.Hide()

		self.__MakeCubeResultWindow()
		if app.ENABLE_PARTY_WAR:
			self.__MakePartyWarRanking()
		if app.QUICK_SELL_SYSTEM:
			self.__MakeQuickSell()

		# ACCESSORY_REFINE_ADD_METIN_STONE
		self.__MakeItemSelectWindow()
		# END_OF_ACCESSORY_REFINE_ADD_METIN_STONE
		self.wndShopOffline.SetItemToolTip(self.tooltipItem)
		self.wndShopOffline.BindInterface(self)
		if app.ENABLE_12ZI:
			self.__Make12ziTimerWindow()
			self.__MakeBeadWindow()
			self.__Make12ziRewardWindow()

		if app.ENABLE_MINI_GAME_OKEY:
			self.__MakeCardsInfoWindow()
			self.__MakeCardsWindow()
			self.__MakeCardsIconWindow()

		if app.ENABLE_GEM_SYSTEM:
			self.__MakeItemSelectWindowEx()

		if app.FAST_EQUIP_WORLDARD:
			self.__MakeFastEquip()

		self.questButtonList = []
		self.whisperButtonList = []
		self.whisperDialogDict = {}
		self.privateShopAdvertisementBoardDict = {}

		self.wndInventory.SetItemToolTip(self.tooltipItem)
		self.wndShopOffline.SetItemToolTip(self.tooltipItem)
		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			self.wndDragonSoul.SetItemToolTip(self.tooltipItem)
			self.wndDragonSoulRefine.SetItemToolTip(self.tooltipItem)
		self.wndSafebox.SetItemToolTip(self.tooltipItem)
		if app.USE_ACCE_SYSTEM:
			self.wndAcceCombine.SetItemToolTip(self.tooltipItem)
			self.wndAcceAbsorption.SetItemToolTip(self.tooltipItem)

		self.wndCube.SetItemToolTip(self.tooltipItem)
		self.wndCubeResult.SetItemToolTip(self.tooltipItem)
		if app.ENABLE_SWITCHBOT:
			self.wndSwitchbot.SetItemToolTip(self.tooltipItem)

		if app.USE_AURA_SYSTEM:
			self.wndAura.SetItemToolTip(self.tooltipItem)

		self.wndCube.SetInven(self.wndInventory)

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			self.wndCube.SetSpecialInven(self.wndSpecialInventory)

		# ITEM_MALL
		self.wndMall.SetItemToolTip(self.tooltipItem)
		# END_OF_ITEM_MALL

		if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
			self.wndSkillBookCombination.SetInven(self.wndInventory)

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				self.wndSkillBookCombination.SetSpecialInven(self.wndSpecialInventory)

		self.wndCharacter.SetSkillToolTip(self.tooltipSkill)
		self.wndTaskBar.SetItemToolTip(self.tooltipItem)
		self.wndTaskBar.SetSkillToolTip(self.tooltipSkill)
		self.wndGuild.SetSkillToolTip(self.tooltipSkill)

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			self.wndChangeLook.SetItemToolTip(self.tooltipItem)

		# ACCESSORY_REFINE_ADD_METIN_STONE
		self.wndItemSelect.SetItemToolTip(self.tooltipItem)
		# END_OF_ACCESSORY_REFINE_ADD_METIN_STONE
		if app.ENABLE_GEM_SYSTEM:
			self.wndItemSelectEx.SetItemToolTip(self.tooltipItem)

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			self.wndSpecialInventory.SetItemToolTip(self.tooltipItem)

		if app.QUICK_SELL_SYSTEM:
			self.wndQuickSell.SetItemToolTip(self.tooltipItem)

		self.dlgShop.SetItemToolTip(self.tooltipItem)
		#dream#self.dlgPrivateShop.SetItemToolTip(self.tooltipItem)

		self.dlgExchange.SetItemToolTip(self.tooltipItem)
		self.privateShopBuilder.SetItemToolTip(self.tooltipItem)
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.privateShopBuilder.SetInven(self.wndInventory)
			self.dlgExchange.SetInven(self.wndInventory)
			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				#dream#self.privateShopBuilder.SetSpecialInven(self.wndSpecialInventory)
				self.dlgExchange.SetSpecialInven(self.wndSpecialInventory)

		if app.ENABLE_BIOLOG_SYSTEM:
			self.wndBiologManagerPanel.SetItemToolTip(self.tooltipItem)

		if app.ENABLE_NOTIFICATION_SYSTEM:
			if self.wndNotificationCenter:
				self.wndNotificationCenter.SetItemToolTip(self.tooltipItem)

		self.__InitWhisper()
		self.DRAGON_SOUL_IS_QUALIFIED = False

		if app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM:
			if self.wndSetCustomAttribute:
				self.wndSetCustomAttribute.SetItemToolTip(self.tooltipItem)

		#self.IntegrationEventBanner()

		if app.ENABLE_GEM_SYSTEM:
			self.wndGemM.SetItemToolTip(self.tooltipItem)
		if app.ENABLE_GROWTH_PET_SYSTEM:
			self.wndPetInfoWindow.SetItemToolTip(self.tooltipItem)
			self.wndPetInfoWindow.SetInven(self.wndInventory)
			self.wndPetInfoWindow.SetPetSkillToolTip(self.tooltipPetSkill)

		if app.ENABLE_MAILBOX:
			if self.mail_box:
				self.mail_box.SetItemToolTip(self.tooltipItem)

		if app.USE_ANTI_EXP and not self.wndExpStatus:
			self.wndExpStatus = ui.ExpandedImageBox("TOP_MOST")
			self.wndExpStatus.SetEvent(ui.__mem_func__(self.__ExpStatusClick), "mouse_click")
			self.wndExpStatus.SetEvent(ui.__mem_func__(self.__ExpStatusOnIn), "mouse_over_in")
			self.wndExpStatus.SetEvent(ui.__mem_func__(self.__ExpStatusOnOut), "mouse_over_out")
			self.wndExpStatus.LoadImage("icon/item/exp_task.png")
			self.wndExpStatus.Hide()
			self.wndExpStatus.SetScale(0.8, 0.8)

		# Last, once every window exists: a warp rebuilds the interface and the challenge tracker
		# dies with it, so a run that is still going gets its board put back here.
		if app.ENABLE_REWARD_SYSTEM:
			if self.wndReward:
				self.wndReward.RefreshTracker(self)
				self.wndReward.NotifyChallengeClosed()
				self.wndReward.RequestChallengeBoard()

	if app.ENABLE_LOCATION_SCROLL_REWORK:
		def ShowLocationHyperlinkTooltip(self, tokens):
			# tokens = ["loc", worldX, worldY] - coordinates only. The scroll's label lives on the
			# owner's client and is deliberately not carried by the link.
			if len(tokens) < 3:
				return

			try:
				worldX = int(tokens[1])
				worldY = int(tokens[2])
			except ValueError:
				return

			import locationscroll
			tooltip = self.hyperlinkItemTooltip

			if not tooltip:
				return

			tooltip.ClearToolTip()
			(mapName, localeMapName, localX, localY) = locationscroll.DescribePosition(worldX, worldY)

			if localeMapName:
				tooltip.AppendTextLine("%s (%d, %d)" % (localeMapName, localX, localY), tooltip.NORMAL_COLOR)
			else:
				tooltip.AppendTextLine("(%d, %d)" % (localX, localY), tooltip.NORMAL_COLOR)

			if app.ENABLE_INGAME_WIKI:
				try:
					import ingamewikispawn
					ingamewikispawn.RenderMiniMapIntoTooltip(tooltip, mapName, [(localX, localY)])
				except:
					pass

			tooltip.Show()

	def MakeHyperlinkTooltip(self, hyperlink):
		tokens = hyperlink.split(":")
		if tokens and len(tokens):
			type = tokens[0]
			
			if "item" == type:
				self.hyperlinkItemTooltip.SetHyperlinkItem(tokens)
			elif app.ENABLE_GROWTH_PET_SYSTEM and "petitem" == type:
				self.hyperlinkItemTooltip.SetHyperlinkPetItem(tokens)
			elif "msg" == type:
				self.OpenWhisperDialog(str(tokens[1]))
			elif "offshop" == type:
				self.OpenOfflineShopFromHyperlink(tokens)
			elif "pfparty" == type:
				self.JoinPartyFromHyperlink(tokens)
			elif app.ENABLE_LOCATION_SCROLL_REWORK and "loc" == type:
				self.ShowLocationHyperlinkTooltip(tokens)

	def OnOfflineShopDormant(self, count):
		# Server: the owner's shop timed out and is parked dormant (items kept in DB). Offer a
		# one-click reopen via a themed dialog; the respawn itself is server-side.
		import uiofflineshop_ae
		try:
			count = int(count)
		except:
			count = 0
		if self.dlgOfflineShopDormant:
			self.dlgOfflineShopDormant.Close()
			self.dlgOfflineShopDormant = None
		dlg = uiofflineshop_ae.OfflineShopDormantDialog()
		dlg.SetText(localeinfo.OFFLINESHOP_DORMANT_PROMPT % count)
		dlg.SetReopenEvent(ui.__mem_func__(self.OnOfflineShopReopenAccept))
		dlg.SetCloseShopEvent(ui.__mem_func__(self.OnOfflineShopCloseShop))
		dlg.SetLaterEvent(ui.__mem_func__(self.OnOfflineShopReopenCancel))
		dlg.Open()
		self.dlgOfflineShopDormant = dlg

	def OnOfflineShopReopenAccept(self):
		import offlineshop
		offlineshop.SendShopReopen()
		self.OnOfflineShopReopenCancel()
		return True

	def OnOfflineShopReopenCancel(self):
		if self.dlgOfflineShopDormant:
			self.dlgOfflineShopDormant.Close()
			self.dlgOfflineShopDormant = None
		return True

	def OnOfflineShopCloseShop(self):
		# Discard the paused shop: items drained to the safebox server-side (reuses force-close).
		import offlineshop
		offlineshop.SendForceCloseShop()
		self.OnOfflineShopReopenCancel()
		return True

	def OpenOfflineShopFromHyperlink(self, tokens):
		# Offlineshop share hyperlink: left-click [SHOP] -> open that shop by owner PID.
		# Token form "offshop:<pidHex>"; reuses the existing open-by-owner CG (no new packet).
		if not app.USE_OFFLINESHOP or len(tokens) < 2:
			return
		try:
			ownerPid = int(tokens[1], 16)
		except ValueError:
			return
		if not ownerPid:
			return
		import offlineshop
		offlineshop.SendOpenShop(ownerPid)

	def JoinPartyFromHyperlink(self, tokens):
		# Party-share hyperlink: left-click [name] -> confirm -> apply to that party via the party
		# finder (token "pfparty:<pidHex>:<name>"; reuses the existing join-request CG, no new packet).
		if not app.ENABLE_PARTY_FINDER or len(tokens) < 3:
			return
		try:
			leaderPid = int(tokens[1], 16)
		except ValueError:
			return
		if not leaderPid:
			return
		if getattr(self, "dlgPartyShareJoin", None):
			self.dlgPartyShareJoin.Close()
		dlg = uicommon.QuestionDialog()
		dlg.SetText(getattr(localeinfo, "PARTY_SHARE_JOIN_CONFIRM", "Would you like to join %s's party?") % str(tokens[2]))
		dlg.SetAcceptEvent(lambda arg=True: self._OnPartyShareJoinAccept())
		dlg.SetCancelEvent(lambda arg=True: self._OnPartyShareJoinCancel())
		dlg.pfLeaderPid = leaderPid
		dlg.Open()
		self.dlgPartyShareJoin = dlg

	def _OnPartyShareJoinAccept(self):
		dlg = getattr(self, "dlgPartyShareJoin", None)
		if dlg:
			net.SendPartyFinderJoinRequest(dlg.pfLeaderPid)
		return self._OnPartyShareJoinCancel()

	def _OnPartyShareJoinCancel(self):
		if getattr(self, "dlgPartyShareJoin", None):
			self.dlgPartyShareJoin.Close()
			self.dlgPartyShareJoin = None
		return True

	if app.ENABLE_12ZI:
		def __MakeBeadWindow(self):
			self.wndBead = ui12zi.BeadWindow()
			self.wndBead.Hide()

		def __Make12ziRewardWindow(self):
			self.wnd12ziReward = ui12zi.Reward12ziWindow()
			self.wnd12ziReward.SetItemToolTip(self.tooltipItem)
			self.wnd12ziReward.Hide()

		def __Make12ziTimerWindow(self):
			self.wnd12ziTimer = ui12zi.FloorLimitTimeWindow()
			self.wnd12ziTimer.Hide()

	if app.ENABLE_PRIVATE_INSTANCE_LOBBY:
		# Floating Return-to-CHAOS button.
		def __MakeChaosReturnButton(self):
			import uichaosreturn
			# Each MakeInterface() must NOT leak a previous instance: the engine
			# keeps movable+float widgets registered, so a dangling Python ref
			# alone wouldn't free the C++ side. Destroy and clear the old one
			# explicitly before binding a new instance.
			if hasattr(self, "wndChaosReturn") and self.wndChaosReturn:
				try:
					self.wndChaosReturn.Hide()
				except:
					pass
				try:
					self.wndChaosReturn.ClearDictionary()
				except:
					pass
				self.wndChaosReturn = None
			self.wndChaosReturn = uichaosreturn.ChaosReturnButton()
			self.wndChaosReturn.Hide()  # server pushes PILChaosReturnAvail to toggle

		def SetChaosReturnAvail(self, available, graceUntil=0):
			if hasattr(self, "wndChaosReturn") and self.wndChaosReturn:
				self.wndChaosReturn.SetAvailable(available, graceUntil)

	def DungeonHudTimer(self, deadline, mode):
		if not self.wndDungeonHud:
			import uidungeonhud
			self.wndDungeonHud = uidungeonhud.DungeonHud()
		self.wndDungeonHud.SetTimer(deadline, mode)
		if getattr(self, "missionBoard", None):
			self.missionBoard.CleanMission()

	def DungeonHudOff(self):
		if self.wndDungeonHud:
			self.wndDungeonHud.Deactivate()

	def DungeonHudMission(self, message):
		if self.wndDungeonHud and self.wndDungeonHud.IsActive():
			self.wndDungeonHud.SetMission(message)
			return True
		return False

	def DungeonHudSubMission(self, message):
		if self.wndDungeonHud and self.wndDungeonHud.IsActive():
			self.wndDungeonHud.SetSubMission(message)
			return True
		return False

	def DungeonHudCleanMission(self):
		if self.wndDungeonHud and self.wndDungeonHud.IsActive():
			self.wndDungeonHud.CleanMission()
			return True
		return False

	if app.ENABLE_PIL_DUNGEON:
		# Fast-Enter countdown overlay. Server (CDungeonInfoManager) drives
		# the state machine via "PILFastEnter <verb> [args]" chat commands.
		def __MakeFastEnterOverlay(self):
			import uifastenter
			# Same multi-instance leak protection as ChaosReturnButton.
			if hasattr(self, "wndFastEnter") and self.wndFastEnter:
				try:
					self.wndFastEnter.Hide()
				except:
					pass
				try:
					self.wndFastEnter.ClearDictionary()
				except:
					pass
				self.wndFastEnter = None
			self.wndFastEnter = uifastenter.FastEnterCountdown()
			self.wndFastEnter.Hide()

		def OnFastEnterStart(self, dungeonIndexStr, totalMsStr):
			if hasattr(self, "wndFastEnter") and self.wndFastEnter:
				try:
					self.wndFastEnter.Start(int(dungeonIndexStr), int(totalMsStr))
				except:
					pass

		def OnFastEnterTick(self, remainingMsStr):
			if hasattr(self, "wndFastEnter") and self.wndFastEnter:
				try:
					self.wndFastEnter.Tick(int(remainingMsStr))
				except:
					pass

		def OnFastEnterPause(self, reasonIdStr):
			if hasattr(self, "wndFastEnter") and self.wndFastEnter:
				try:
					self.wndFastEnter.Pause(int(reasonIdStr))
				except:
					pass

		def OnFastEnterResume(self):
			if hasattr(self, "wndFastEnter") and self.wndFastEnter:
				try:
					self.wndFastEnter.Resume()
				except:
					pass

		def OnFastEnterCancel(self, reasonIdStr):
			if hasattr(self, "wndFastEnter") and self.wndFastEnter:
				try:
					self.wndFastEnter.Cancel(int(reasonIdStr))
				except:
					pass

		def OnFastEnterCancelName(self, reasonIdStr, nameStr):
			if hasattr(self, "wndFastEnter") and self.wndFastEnter:
				try:
					self.wndFastEnter.CancelName(int(reasonIdStr), nameStr)
				except:
					pass

		def OnFastEnterDone(self):
			if hasattr(self, "wndFastEnter") and self.wndFastEnter:
				try:
					self.wndFastEnter.Done()
				except:
					pass

	## Make Windows & Dialogs
	################################

	def Close(self):
		if app.ENABLE_WINDOW_POSITION_SAVE:
			uiwindowpositions.Save()

		if app.USE_PORTABLE_TELEPORT_WITH_UI and self.teleportWnd:
			self.teleportWnd.Destroy()
			self.teleportWnd = None

		if getattr(self, "wndPvmBalanceIntro", None):
			self.wndPvmBalanceIntro.Destroy()
			self.wndPvmBalanceIntro = None

		if app.USE_LOG_EXCHANGE and self.wndExchangeLog:
			self.wndExchangeLog.Destroy()
			del self.wndExchangeLog
			self.wndExchangeLog = None

		if app.USE_CRAFT_ITEM_SYSTEM and self.wnd_craft_item:
			self.wnd_craft_item.Destroy()
			del self.wnd_craft_item
			self.wnd_craft_item = None

		if app.ENABLE_RENDER_TARGET and self.wndRenderTargetInterface:
			self.wndRenderTargetInterface.Destroy()
			del self.wndRenderTargetInterface
			self.wndRenderTargetInterface = None

		# if app.USE_NORTHWIND_DEEPS_DUNGEON:
		if self.wndUIDamage:
			self.wndUIDamage.Destroy()
			del self.wndUIDamage
			self.wndUIDamage = None

		if app.__RANKING_SYSTEM__:
			if self.wndRanking:
				self.wndRanking.Close()
				self.wndRanking.Destroy()
				self.wndRanking = None

		if app.ENABLE_DAILY_ALCHEMY_ORE and self.wndSpinWheel:
			self.wndSpinWheel.Close()
			self.wndSpinWheel.Destroy()
			self.wndSpinWheel = None

		if app.__SPIN_WHEEL_DUNGEON__ and self.wndDungeonSpinWheel:
			self.wndDungeonSpinWheel.Close()
			self.wndDungeonSpinWheel.Destroy()
			self.wndDungeonSpinWheel = None

		if app.__AUTO_SKILL_READER__:
			if self.wndAutoSkillReader:
				self.wndAutoSkillReader.Close()
				self.wndAutoSkillReader.Destroy()
				self.wndAutoSkillReader = None

		if app.ENABLE_ATTR_6TH_7TH:
			if self.wndAttr67Add:
				self.wndAttr67Add.Destroy()

		if app.ENABLE_REWARD_SYSTEM:
			if self.wndReward:
				self.wndReward.Close()
				self.wndReward.Destroy()
				self.wndReward = None

		if self.wndStoryInterface:
			self.wndStoryInterface.Close()
			#self.wndStoryInterface.Destroy()
			self.wndStoryInterface = None

		if app.ENABLE_NOTIFICATION_SYSTEM:
			if self.wndNotificationCenter:
				self.wndNotificationCenter.Destroy()
				self.wndNotificationCenter = None


		if app.__SKILL_TREE__:
			if self.wndSkillTree:
				self.wndSkillTree.Close()
				self.wndSkillTree.Destroy()
				self.wndSkillTree = None
		if app.USE_WHEEL_OF_FORTUNE:
			if self.wndWheelofFortune:
				self.wndWheelofFortune.Hide()
				self.wndWheelofFortune.Destroy()
				del self.wndWheelofFortune
				self.wndWheelofFortune=0

		if app.ENABLE_RENEWAL_PVP:
			if self.wndPvP:
				self.wndPvP.SaveData()
				self.wndPvP.Hide()
				self.wndPvP.Destroy()
				self.wndPvP = None
		
		if self.wndDungeonTimer:##hydra part
			self.wndDungeonTimer.Hide()
			self.wndDungeonTimer=0

		if self.dlgWhisperWithoutTarget:
			self.dlgWhisperWithoutTarget.Destroy()
			del self.dlgWhisperWithoutTarget

		if uiquest.QuestDialog.__dict__.has_key("QuestCurtain"):
			uiquest.QuestDialog.QuestCurtain.Close()

		if self.wndQuestWindow:
			for key, eachQuestWindow in self.wndQuestWindow.items():
				eachQuestWindow.nextCurtainMode = -1
				eachQuestWindow.CloseSelf()
				eachQuestWindow.Hide()
				eachQuestWindow = None
		self.wndQuestWindow = {}

		if app.WHEEL_INGAME:
			if self.wndWheel:
				self.wndWheel.Hide()
				self.wndWheel.Destroy()
				self.wndWheel = None
			
			if self.wndSpin:
				self.wndSpin.Hide()
				self.wndSpin.Destroy()
				self.wndSpin = None

			if self.wndRewards:
				self.wndRewards.Hide()
				self.wndRewards.Destroy()
				self.wndRewards = None

		if self.wndChat:
			self.wndChat.Destroy()

		if self.yangText:
			self.yangText.ClearAll()

		if self.wndTaskBar:
			self.wndTaskBar.Destroy()

		if self.wndExpandedTaskBar:
			self.wndExpandedTaskBar.Destroy()

		if self.wndExpandedMoneyTaskBar:
			self.wndExpandedMoneyTaskBar.Destroy()
			del self.wndExpandedMoneyTaskBar
			self.wndExpandedMoneyTaskBar = None

		if self.wndEnergyBar:
			self.wndEnergyBar.Destroy()

		if self.wndCharacter:
			self.wndCharacter.Destroy()

		if self.wndDragonSoul:
			self.wndDragonSoul.Destroy()

		if app.ENABLE_PVP_ROUTES:
			if self.wndRoutesPvPSystem:
				self.wndRoutesPvPSystem.Destroy()

		if self.wndDragonSoulRefine:
			self.wndDragonSoulRefine.Destroy()

		if self.dlgExchange:
			self.dlgExchange.Destroy()

		if self.dlgPointReset:
			self.dlgPointReset.Destroy()

		if self.dlgShop:
			self.dlgShop.Destroy()

		if self.dlgRestart:
			self.dlgRestart.Destroy()

		if self.dlgSystem:
			self.dlgSystem.Destroy()

		if self.dlgPassword:
			self.dlgPassword.Destroy()

		if self.wndMiniMap:
			self.wndMiniMap.Destroy()

		if self.wndSafebox:
			self.wndSafebox.Destroy()
		
		if self.wndMall:
			self.wndMall.Destroy()

		if self.wndParty:
			self.wndParty.Destroy()

		if self.wndHelp:
			self.wndHelp.Destroy()

		if app.USE_DUNGEON_INFO:
			if self.wndDungeonInfo:
				self.wndDungeonInfo.Destroy()
				del self.wndDungeonInfo
				self.wndDungeonInfo = None

			if app.USE_DUNGEON_COOLDOWN_MANAGER and self.dungeonCooldownAlert:
				del self.dungeonCooldownAlert
				self.dungeonCooldownAlert = None

		if app.USE_ACCE_SYSTEM:
			if self.wndAcceCombine:
				self.wndAcceCombine.Destroy()

			if self.wndAcceAbsorption:
				self.wndAcceAbsorption.Destroy()

		if app.ENABLE_ANTI_MULTIPLE_FARM:
			if self.wndAntiMultipleFarm:
				self.wndAntiMultipleFarm.Hide()
				self.wndAntiMultipleFarm.Destroy()

		if self.wndCube:
			self.wndCube.Destroy()

		if self.wndCubeResult:
			self.wndCubeResult.Destroy()

		if self.friendRequestDialog:
			self.friendRequestDialog.Close()
			self.friendRequestDialog = None
		self.friendRequestQueue = []

		if self.wndMessenger:
			self.wndMessenger.Destroy()

		if app.ENABLE_PARTY_FINDER:
			if self.wndPartyFinder:
				self.wndPartyFinder.Destroy()

		if app.ENABLE_GUILD_FINDER:
			if self.wndGuildFinder:
				self.wndGuildFinder.Destroy()

		if app.ENABLE_PARTY_BOUNS:
			if self.wndPartyBonusWindow:
				self.wndPartyBonusWindow.Destroy()
				del self.wndPartyBonusWindow
				self.wndPartyBonusWindow = None

		if self.wndGuild:
			self.wndGuild.Destroy()

		if self.privateShopBuilder:
			self.privateShopBuilder.Destroy()

		if self.dlgRefineNew:
			self.dlgRefineNew.Destroy()

		if self.wndGuildBuilding:
			self.wndGuildBuilding.Destroy()

		if app.ENABLE_VOICE_CHAT:
			if self.wndVoiceChatConfig:
				self.wndVoiceChatConfig.Hide()
				self.wndVoiceChatConfig.Destroy()
				del self.wndVoiceChatConfig

			if self.wndVoiceChatOverlay:
				self.wndVoiceChatOverlay.Hide()
				self.wndVoiceChatOverlay.Destroy()
				del self.wndVoiceChatOverlay

		if app.ENABLE_MISSION_QUEST:
			if self.wndMissionQuest:
				#self.wndMissionQuest.Hide()
				self.wndMissionQuest.Destroy()

		if app.ADVANCED_BATTLE_PASS:
			if self.wndBattlePass:
				self.wndBattlePass.Destroy()

		if app.ENABLE_FISHING_GAME:
			if self.wndFishingGame:
				self.wndFishingGame.Destroy()
		if app.ENABLE_FISHING_GAME_BDO:
			if self.wndFishingBdo:
				self.wndFishingBdo.Destroy()

		if self.wndGameButton:
			self.wndGameButton.Destroy()

		if app.ENABLE_SKILL_LEARN_SYSTEM and self.wndLearnSkill:
			self.wndLearnSkill.Destroy()
			del self.wndLearnSkill

		if app.ENABLE_EVENT_MANAGER and self.wndEventOverview:
			self.wndEventOverview.Hide()
			self.wndEventOverview.Destroy()
			del self.wndEventOverview
			self.wndEventOverview = None

		if app.USE_EVENT_MANAGER_EXPANDED and self.wndEventAlert:
			self.wndEventAlert.Destroy()
			del self.wndEventAlert
			self.wndEventAlert = None

		# ITEM_MALL
		if self.mallPageDlg:
			self.mallPageDlg.Destroy()
		# END_OF_ITEM_MALL
		if app.ENABLE_PARTY_WAR:
			if self.wndPartywarBoard:
				self.wndPartywarBoard.Hide()
				self.wndPartywarBoard.Destroy()
				del self.wndPartywarBoard
				self.wndPartywarBoard = None
			if self.wndPartywarTimer:
				self.wndPartywarTimer.Hide()
				self.wndPartywarTimer.Destroy()
				del self.wndPartywarTimer
				self.wndPartywarTimer = None
			if self.wndPartywarButton:
				self.wndPartywarButton.Hide()
				self.wndPartywarButton.Destroy()
				del self.wndPartywarButton
				self.wndPartywarButton = None
			if self.wndPartywarPlayerBoard:
				self.wndPartywarPlayerBoard.Hide()
				self.wndPartywarPlayerBoard.Destroy()
				del self.wndPartywarPlayerBoard
				self.wndPartywarPlayerBoard = None
		if app.ENABLE_EXTENDED_BATTLE_PASS:
			if self.wndBattlePassExtended:
				self.wndBattlePassExtended.Destroy()

		# ACCESSORY_REFINE_ADD_METIN_STONE
		if self.wndItemSelect:
			self.wndItemSelect.Destroy()
		# END_OF_ACCESSORY_REFINE_ADD_METIN_STONE

		if self.wndShopOffline:
			self.wndShopOffline.Destroy()
			self.wndShopOffline.Hide()
			del self.wndShopOffline

		if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
			self.wndSkillBookCombination.Destroy()
			del self.wndSkillBookCombination

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if self.wndChangeLook:
				del self.wndChangeLook

		if app.ENABLE_MYSHOP_DECO:
			if self.wndMyShopDeco:
				self.wndMyShopDeco.Destroy()
				del self.wndMyShopDeco

		if app.ENABLE_MINI_GAME_OKEY:
			if self.wndCardsSimpleWaiting:
				self.wndCardsSimpleWaiting.Destroy()

			if self.wndCardsInfo:
				self.wndCardsInfo.Destroy()

			if self.wndCards:
				self.wndCards.Destroy()

			if self.wndCardsIcon:
				self.wndCardsIcon.Destroy()

		if app.ENABLE_GEM_SYSTEM:
			if self.wndItemSelectEx:
				self.wndItemSelectEx.Destroy()

		if app.ENABLE_GEM_SYSTEM:
			if self.wndGemG:
				self.wndGemG.Destroy()
				del self.wndGemG

			if self.wndGemM:
				self.wndGemM.Destroy()
				del self.wndGemM

		if app.ENABLE_GROWTH_PET_SYSTEM:
			if self.wndPetInfoWindow:
				self.wndPetInfoWindow.Destroy()

		if app.ENABLE_SWITCHBOT:
			if self.wndSwitchbot:
				self.wndSwitchbot.Destroy()
				del self.wndSwitchbot

		if app.ENABLE_MINI_GAME_BNW:
			if self.wndBNWGame:
				self.wndBNWGame.Destroy()
				del self.wndBNWGame

		if app.ENABLE_CUBE_RENEWAL_WORLDARD:
			if self.wndCubeRenewal:
				self.wndCubeRenewal.Destroy()
				self.wndCubeRenewal.Close()

		if app.USE_AURA_SYSTEM:
			if self.wndAura:
				self.wndAura.Destroy()

		if app.ENABLE_12ZI:
			if self.wndBead:
				self.wndBead.Hide()
				self.wndBead.Destroy()
				del self.wndBead

			if self.wnd12ziTimer:
				self.wnd12ziTimer.Hide()
				self.wnd12ziTimer.Destroy()
				del self.wnd12ziTimer

			if self.wnd12ziReward:
				self.wnd12ziReward.Hide()
				self.wnd12ziReward.Destroy()
				del self.wnd12ziReward

		if app.ENABLE_ASLAN_TELEPORTPANEL:
			if self.wndTeleportPanel:
				self.wndTeleportPanel.Destroy()
		
		if app.ENABLE_ITEMSHOP:
			if self.wndItemShop:
				self.wndItemShop.Hide()
				self.wndItemShop.Destroy()
				self.wndItemShop = None

#Coupon
		if self.wndCoupon:
			self.wndCoupon.Destroy()
			self.wndCoupon = None

		if self.wndCouponAdmin:
			self.wndCouponAdmin.Destroy()
#Coupon

		# if app.ENABLE_BIOLOG_SYSTEM:
			# if self.wndBiologManager:
				# for wnd in self.wndBiologManager.values():
					# wnd.Destroy()

		if app.ENABLE_BIOLOG_SYSTEM:
			if self.wndBiologManagerPanel:
				self.wndBiologManagerPanel.Destroy()
				del self.wndBiologManagerPanel

		if app.ENABLE_ULTIMATE_REGEN:
			if self.wndTrackWindow:
				self.wndTrackWindow.Destroy()
				del self.wndTrackWindow
				self.wndTrackWindow = None

		if getattr(app, "ENABLE_CURSED_BOSS", 0):
			if getattr(self, "wndCursedHud", None):
				self.wndCursedHud.Destroy()
				self.wndCursedHud = None

		if app.ENABLE_WORLDBOSS:
			if self.wndWorldBoss:
				self.wndWorldBoss.Destroy()
				del self.wndWorldBoss
				self.wndWorldBoss = None

		if app.ENABLE_WORLDBOSS_V2_DAMAGE_METER:
			if getattr(self, "wndWBDamageMeter", None):
				self.wndWBDamageMeter.Destroy()
				del self.wndWBDamageMeter
				self.wndWBDamageMeter = None

		if app.ENABLE_HORSE_UPGRADE:
			if getattr(self, "wndHorseUpgrade", None):
				self.wndHorseUpgrade.Destroy()
				del self.wndHorseUpgrade
				self.wndHorseUpgrade = None

		if getattr(self, "wndBundleBox", None):
			self.wndBundleBox.Destroy()
			del self.wndBundleBox
			self.wndBundleBox = None

		if app.__BUFFI_SUPPORT__:
			if getattr(self, "wndCompanion", None):
				self.wndCompanion.Destroy()
				del self.wndCompanion
				self.wndCompanion = None
			if getattr(self, "wndCompanionUpgrade", None):
				self.wndCompanionUpgrade.Destroy()
				del self.wndCompanionUpgrade
				self.wndCompanionUpgrade = None
			if getattr(self, "wndCompanionHelp", None):
				self.wndCompanionHelp.Destroy()
				del self.wndCompanionHelp
				self.wndCompanionHelp = None
			if getattr(self, "wndCompanionRideHelp", None):
				self.wndCompanionRideHelp.Destroy()
				del self.wndCompanionRideHelp
				self.wndCompanionRideHelp = None
			if getattr(self, "wndPetUpgrade", None):
				self.wndPetUpgrade.Destroy()
				del self.wndPetUpgrade
				self.wndPetUpgrade = None
			if getattr(self, "wndPetSkillUpgrade", None):
				self.wndPetSkillUpgrade.Destroy()
				del self.wndPetSkillUpgrade
				self.wndPetSkillUpgrade = None
			if getattr(self, "wndPetUpgradeHelp", None):
				self.wndPetUpgradeHelp.Destroy()
				del self.wndPetUpgradeHelp
				self.wndPetUpgradeHelp = None
			if getattr(self, "wndPetHelp", None):
				self.wndPetHelp.Destroy()
				del self.wndPetHelp
				self.wndPetHelp = None

		if app.FAST_EQUIP_WORLDARD and self.wndFastEquip:
			self.wndFastEquip.Destroy()
			del self.wndFastEquip
			self.wndFastEquip = None

		if app.USE_ANTI_EXP and self.wndExpStatus:
			self.wndExpStatus.SetEvent(None, "mouse_click")
			self.wndExpStatus.SetEvent(None, "mouse_over_in")
			self.wndExpStatus.SetEvent(None, "mouse_over_out")
			del self.wndExpStatus
			self.wndExpStatus = None

		if app.USE_COSTUME_ATTR_TRANSFER and\
			self.wndAttrTransfer:
			self.wndAttrTransfer.Destroy()
			del self.wndAttrTransfer
			self.wndAttrTransfer = None

		if getattr(app, "USE_QUICK_ATTR_TRANSFER", 0) and\
			self.wndQuickTransfer:
			self.wndQuickTransfer.Destroy()
			del self.wndQuickTransfer
			self.wndQuickTransfer = None

		if app.USE_ACCE_ATTR_TRANSFER and\
			self.wndAcceAttrTransfer:
			self.wndAcceAttrTransfer.Destroy()
			del self.wndAcceAttrTransfer
			self.wndAcceAttrTransfer = None

		if app.USE_ITEM_ATTR_BACKUP_MODE and\
			self.wndItemBackupAttr:
			self.wndItemBackupAttr.Destroy()
			del self.wndItemBackupAttr
			self.wndItemBackupAttr = None

		self.wndChatLog.Destroy()
		if app.QUICK_SELL_SYSTEM:
			if self.wndQuickSell:
				self.wndQuickSell.Destroy()
		if getattr(self, "wndTitle", None):
			self.wndTitle.Destroy()
			self.wndTitle = None
		for btn in self.questButtonList:
			btn.SetEvent(0)
		for btn in self.whisperButtonList:
			btn.SetEvent(0)
		for dlg in self.whisperDialogDict.itervalues():
			dlg.Destroy()
		for brd in self.guildScoreBoardDict.itervalues():
			brd.Destroy()
		for dlg in self.equipmentDialogDict.itervalues():
			dlg.Destroy()

		# ITEM_MALL
		del self.mallPageDlg
		# END_OF_ITEM_MALL

		del self.wndGuild
		del self.wndMessenger
		del self.wndCommunity
		if app.ENABLE_PARTY_FINDER:
			del self.wndPartyFinder
		if app.ENABLE_GUILD_FINDER:
			del self.wndGuildFinder
		del self.wndUICurtain
		del self.wndChat
		del self.yangText
		del self.wndTaskBar
		if app.ENABLE_CUBE_RENEWAL_WORLDARD:
			del self.wndCubeRenewal
		if self.wndExpandedTaskBar:
			del self.wndExpandedTaskBar

		del self.wndEnergyBar
		del self.wndCharacter

#coupon
		#del self.wndCoupon
		del self.wndCouponAdmin
#coupon
		if self.wndDragonSoul:
			del self.wndDragonSoul
		if self.wndDragonSoulRefine:
			del self.wndDragonSoulRefine

		if app.ENABLE_MAILBOX:
			if self.mail_box:
				self.mail_box.Destroy()
				del self.mail_box

		if app.BL_REMOTE_SHOP:
			if self.wndRemoteShop:
				del self.wndRemoteShop

		# if app.USE_OFFLINESHOP:
			# if self.wndOfflineShop:
				# del self.wndOfflineShop

		del self.dlgExchange
		del self.dlgPointReset
		del self.dlgShop
		del self.dlgRestart
		del self.dlgSystem
		del self.dlgPassword
		del self.hyperlinkItemTooltip
		del self.tooltipItem
		del self.tooltipSkill
		del self.wndMiniMap
		del self.wndSafebox
		del self.wndMall
		del self.wndParty
		del self.wndHelp
		if app.DEATHMATCH_EVENT:
			del self.wndDTInterface	
		if app.USE_ACCE_SYSTEM:
			del self.wndAcceCombine
			del self.wndAcceAbsorption

		
		if app.ENABLE_ANTI_MULTIPLE_FARM:
			del self.wndAntiMultipleFarm
		del self.wndCube
		if app.CRYSTAL_PVP_SYSTEM:
			del self.wndCrystal
		if app.DEFENSE_PVP_SYSTEM:
			del self.wndDefense
		if app.DOMINIUM_PVP_SYSTEM:	
			del self.wndDominium
		if app.DOMINIUM_PVP_SYSTEM or app.DEFENSE_PVP_SYSTEM or app.CRYSTAL_PVP_SYSTEM: #app.TOURNAMENT_PVP_SYSTEM or  
			del self.wndPvPEvent
		del self.wndCubeResult
		del self.privateShopBuilder
		del self.inputDialog
		del self.wndChatLog
		del self.dlgRefineNew
		del self.wndGuildBuilding
		if app.ENABLE_ATTR_6TH_7TH:
			if self.wndAttr67Add:
				del self.wndAttr67Add
		if app.ENABLE_FISHING_GAME:
			if self.wndFishingGame:
				del self.wndFishingGame
		if app.ENABLE_FISHING_GAME_BDO:
			if self.wndFishingBdo:
				del self.wndFishingBdo
		del self.wndGameButton
		if app.ENABLE_ASLAN_TELEPORTPANEL:
			del self.wndTeleportPanel
		del self.tipBoard
		del self.importantPopup
		del self.bigBoard
		del self.wndItemSelect
		if app.QUICK_SELL_SYSTEM:
			del self.wndQuickSell
		if app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM:
			if self.wndSetCustomAttribute:
				self.wndSetCustomAttribute.Destroy()
				del self.wndSetCustomAttribute
		if app.ENABLE_MISSION_QUEST:
			del self.wndMissionQuest

		if app.ADVANCED_BATTLE_PASS:
			del self.wndBattlePass

		if self.wndDungeonHud:
			try:
				self.wndDungeonHud.Hide()
			except:
				pass
			self.wndDungeonHud = None
		if self.wndChallengeHud:
			try:
				self.wndChallengeHud.Hide()
			except:
				pass
			self.wndChallengeHud = None
		if app.ENABLE_12ZI:
			del self.missionBoard

		if app.USE_AURA_SYSTEM:
			del self.wndAura
		if self.wndMiniGame:
			self.wndMiniGame.Destroy()
			del self.wndMiniGame

	#dream#	del self.dlgPrivateShop

		if app.ENABLE_MINI_GAME_OKEY:
			del self.wndCardsSimpleWaiting
			del self.wndCardsInfo
			del self.wndCards
			del self.wndCardsIcon

		if app.ENABLE_GEM_SYSTEM:
			del self.wndItemSelectEx

		if app.ENABLE_PVP_ROUTES:
			del self.wndRoutesPvPSystem

		if app.ENABLE_GROWTH_PET_SYSTEM:
			if self.wndPetInfoWindow:
				del self.wndPetInfoWindow
			self.wndPetInfoWindow = None
			del self.tooltipPetSkill

		if app.ENABLE_EXTENDED_BATTLE_PASS:
			del self.wndBattlePassExtended
		
		# if app.ENABLE_BIOLOG_SYSTEM:
			# for wnd in self.wndBiologManager.values():
				# del wnd
		
		if app.USE_PVP_TOURNAMENT:
			if self.wndPvpTournamentAdmin:
				self.wndPvpTournamentAdmin.Destroy()
				del self.wndPvpTournamentAdmin
				self.wndPvpTournamentAdmin = None
			
			if app.PVP_HAVE_GUI:
				if self.wndPvpTournamentFights:
					self.wndPvpTournamentFights.Destroy()
					del self.wndPvpTournamentFights
					self.wndPvpTournamentFights = None

		if app.USE_BL_FISH_EVENT:
			if self.fish_game:
				self.fish_game.Destroy()
				del self.fish_game
				self.fish_game = None

		if self.wndInventory:
			self.wndInventory.Destroy()
			del self.wndInventory
			self.wndInventory = None

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			if self.wndSpecialInventory:
				self.wndSpecialInventory.Destroy()
				del self.wndSpecialInventory
				self.wndSpecialInventory = None

		if self.wndWhisperChat:
			self.wndWhisperChat.Destroy()
			self.wndWhisperChat = None

		self.questButtonList = []
		self.whisperButtonList = []
		self.whisperDialogDict = {}
		self.privateShopAdvertisementBoardDict = {}
		self.guildScoreBoardDict = {}
		self.equipmentDialogDict = {}

		uichat.DestroyChatInputSetWindow()

	## Skill
	def OnUseSkill(self, slotIndex, coolTime):
		self.wndCharacter.OnUseSkill(slotIndex, coolTime)
		self.wndTaskBar.OnUseSkill(slotIndex, coolTime)
		self.wndGuild.OnUseSkill(slotIndex, coolTime)

	def OnActivateSkill(self, slotIndex):
		self.wndCharacter.OnActivateSkill(slotIndex)
		self.wndTaskBar.OnActivateSkill(slotIndex)

	def OnDeactivateSkill(self, slotIndex):
		self.wndCharacter.OnDeactivateSkill(slotIndex)
		self.wndTaskBar.OnDeactivateSkill(slotIndex)

	if app.ENABLE_COMBAT_POINTS:
		def OnCPHideState(self, state):
			if self.wndCharacter:
				self.wndCharacter.OnCPHideState(state)

	def OnChangeCurrentSkill(self, skillSlotNumber):
		self.wndTaskBar.OnChangeCurrentSkill(skillSlotNumber)

	if app.ENABLE_SKILL_COOLTIME_UPDATE:
		def SkillClearCoolTime(self, slotIndex):
			self.wndCharacter.SkillClearCoolTime(slotIndex)
			self.wndTaskBar.SkillClearCoolTime(slotIndex)

	def SelectMouseButtonEvent(self, dir, event):
		self.wndTaskBar.SelectMouseButtonEvent(dir, event)

	if app.WHEEL_INGAME:
		def MakeWheelWindow(self):
			if self.wndWheel == None:
				self.wndWheel = uispinwheel.WheelWindow()
		
		def OpenWheel(self):
			self.MakeWheelWindow()
			if self.wndWheel.IsShow():
				self.wndWheel.Close()
			else:
				self.wndWheel.Open()
		
		def MakeSpinWindow(self):
			if self.wndSpin == None:
				self.wndSpin = uispinwheel.SpinWheel()

		def OpenSpin(self, reward):
			# import dbg
			# dbg.TraceError("OpenSpin")
			self.MakeSpinWindow()
			self.wndSpin.Open(reward)

		def SpinReward(self):
			if self.wndSpin:
				self.wndSpin.SpinReward()

		def SetSpinWheel(self, arg):
			if self.wndWheel:
				self.wndWheel.UpdatePercentage(arg)

		def MakeRewardBoard(self):
			if self.wndRewards == None:
				self.wndRewards = uispinwheel.RewardBoard()
		
		def OpenRewardsWindow(self):
			self.MakeRewardBoard()
			if self.wndRewards:
				if self.wndRewards.IsShow():
					self.wndRewards.Close()
				else:
					self.wndRewards.Open()

	if app.ENABLE_CASUAL_BUFF:
		# binary GC route: game.py OnCasualBuff* -> here -> character window.
		# constinfo mirror lets other widgets (mission-list lock overlay, later)
		# read the active flag without coupling to the character window.
		def OnCasualBuffInfo(self, active, chaosAllowed, stonesToday, stoneLimit, chaosLeft, chaosMax, secsToMidnight, shardVnums, chaosVnums):
			constinfo.CASUAL_BUFF_ACTIVE = active
			if self.wndCharacter:
				self.wndCharacter.OnCasualBuffInfo(active, chaosAllowed, stonesToday, stoneLimit, chaosLeft, chaosMax, secsToMidnight, shardVnums, chaosVnums)

		def OnCasualBuffCount(self, stonesToday, chaosLeft):
			if self.wndCharacter:
				self.wndCharacter.OnCasualBuffCount(stonesToday, chaosLeft)

		def OnCasualBuffChars(self, charList):
			if self.wndCharacter:
				self.wndCharacter.OnCasualBuffChars(charList)

		def OnCasualBuffResult(self, result):
			if self.wndCharacter:
				self.wndCharacter.OnCasualBuffResult(result)

	## Refresh
	def RefreshAlignment(self):
		self.wndCharacter.RefreshAlignment()

	def RefreshStatus(self):
		self.wndExpandedMoneyTaskBar.RefreshStatus()

		if app.__AUTO_SKILL_READER__:
			if self.wndAutoSkillReader:
				if self.wndAutoSkillReader.IsShow():
					self.wndAutoSkillReader.Refresh()
		self.wndTaskBar.RefreshStatus()
		self.wndCharacter.RefreshStatus()

		if self.wndEnergyBar:
			self.wndEnergyBar.RefreshStatus()

		if app.ENABLE_GROWTH_PET_SYSTEM:
			self.wndPetInfoWindow.RefreshStatus()
			# Growth-pet rework: the Companion pet page AND the pet dialogs ride the same
			# point deltas (exp / duration / stat changes / unsummon -- the GC info packet
			# is NOT pushed on dismissal, so this is what closes a dialog on a dead pet).
			# Every window self-gates on being shown.
			if app.__BUFFI_SUPPORT__ and hasattr(self, "RefreshCompanionPetPage"):
				self.RefreshCompanionPetPage()

		if app.ENABLE_ULTIMATE_REGEN and self.wndTrackWindow:
			self.wndTrackWindow.RefreshPoints()
		if app.ENABLE_SKILL_LEARN_SYSTEM and self.wndLearnSkill:
			self.wndLearnSkill.RefreshStatus()

		if app.USE_DUNGEON_INFO and self.wndDungeonInfo:
			self.wndDungeonInfo.RefreshLevel()

		if app.USE_ANTI_EXP and self.wndExpStatus:
			if player.CanReceiveExp():
				self.wndExpStatus.SetDiffuseColor(189.0, 195.0, 199.0, 1.0)
			else:
				self.wndExpStatus.SetDiffuseColor(1.0, 0.0, 0.0, 1.0)

			if not self.wndExpStatus.IsShow():
				if self.wndTaskBar:
					x, y = self.wndTaskBar.GetLocalPosition()
					self.wndExpStatus.SetPosition(x + 250, y - 12)

				self.wndExpStatus.Show()

			self.wndExpStatus.SetTop()

	def RefreshStamina(self):
		self.wndTaskBar.RefreshStamina()

	def RefreshSkill(self):
		self.wndCharacter.RefreshSkill()
		self.wndTaskBar.RefreshSkill()

	def RefreshInventory(self):
		if app.__AUTO_SKILL_READER__:
			if self.wndAutoSkillReader:
				if self.wndAutoSkillReader.IsShow():
					self.wndAutoSkillReader.Refresh()

		self.wndTaskBar.RefreshQuickSlot()
		self.wndInventory.RefreshItemSlot()
		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			self.wndDragonSoul.RefreshItemSlot()
		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			self.wndSpecialInventory.RefreshItemSlot()

		if app.USE_AURA_SYSTEM:
			if player.IsAuraRefineWindowOpen():
				if self.wndAura and self.wndAura.IsShow():
					self.wndAura.RefreshAuraWindow()

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if player.GetChangeLookWindowOpen() == 1:
				self.wndChangeLook.RefreshChangeLookWindow()

		if app.FAST_EQUIP_WORLDARD:
			self.wndFastEquip.RefreshEquipSlotWindow()

		if app.ENABLE_GROWTH_PET_SYSTEM and app.USE_GROWTH_NEW_EVOLVE_WINDOW:
			if self.wndPetInfoWindow:
				evolveWnd = self.wndPetInfoWindow.evolveWnd
				if evolveWnd and evolveWnd.IsShow():
					evolveWnd.RefreshCount()

		if app.USE_ITEM_ATTR_BACKUP_MODE and self.wndItemBackupAttr and self.wndItemBackupAttr.IsShow():
			self.wndItemBackupAttr.Refresh()

		if app.USE_BL_FISH_EVENT and self.fish_game:
			self.fish_game.RefreshItem()

		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			self.wndDragonSoul.RefreshStatus()

	def RefreshCharacter(self):
		self.wndCharacter.RefreshCharacter()
		self.wndTaskBar.RefreshQuickSlot()

	def RefreshQuest(self):
		self.wndCharacter.RefreshQuest()

	def RefreshSoloLeadership(self):
		if not app.ENABLE_SOLO_LEADERSHIP_BONUS:
			return
		if self.wndCharacter and hasattr(self.wndCharacter, "RefreshSoloLeadership"):
			self.wndCharacter.RefreshSoloLeadership()

	def RefreshSafebox(self):
		self.wndSafebox.RefreshSafebox()

	# ITEM_MALL
	def RefreshMall(self):
		self.wndMall.RefreshMall()

	def OpenItemMall(self):
		if not self.mallPageDlg:
			self.mallPageDlg = uishop.MallPageDialog()

		self.mallPageDlg.Open()
	# END_OF_ITEM_MALL

	if app.ENABLE_EVENT_MANAGER:
		def ToggleInGameEvent(self, x = -1, y = -1):
			if self.wndEventOverview and player.IsObserverMode() == False:
				if self.wndEventOverview.IsShow():
					self.wndEventOverview.Close()
				else:
					self.wndEventOverview.Open(x, y)

		if app.USE_EVENT_MANAGER_EXPANDED:
			def RefreshInGameEvent(self):
				if not self.wndEventOverview:
					self.wndEventOverview = uievent.EventOverview()
				elif self.wndEventOverview.IsShow():
					self.wndEventOverview.ClearActiveEvents()
					self.wndEventOverview.RefreshActiveEvent()

				if app.ENABLE_PLAYER_EVENT_ACTIVATION:
					wndActivatable = getattr(self.wndEventOverview, "wndActivatable", None)
					if wndActivatable and wndActivatable.IsShow():
						wndActivatable.Refresh()

				if self.wndEventAlert:
					self.wndEventAlert.OnRefresh()
		else:
			def OpenInGameEvent(self):
				if self.wndEventOverview:
					if not self.wndEventOverview.IsShow():
						self.wndEventOverview.Open(-1, -1)

			def CloseInGameEvent(self):
				if self.wndEventOverview:
					if self.wndEventOverview.IsShow():
						self.wndEventOverview.Close()

		def KingdomWarScore(self, score_shinsoo, score_chunjo, score_jinno):
			if self.wndEventOverview:
				self.wndEventOverview.KingdomWarScore(score_shinsoo, score_chunjo, score_jinno)

		if app.ENABLE_PLAYER_EVENT_ACTIVATION:
			def OnEventActivateResult(self, bType, bResult, endTime):
				if getattr(self, "wndEventAlert", None):
					self.wndEventAlert.OnRefresh()

				if self.wndEventOverview and self.wndEventOverview.wndActivatable:
					if self.wndEventOverview.wndActivatable.IsShow():
						self.wndEventOverview.wndActivatable.Refresh()

				import chat
				msgDict = {
					0 : localeinfo.EVENT_ACTIVATE_OK,
					1 : localeinfo.EVENT_ACTIVATE_NOT_RUNNING,
					2 : localeinfo.EVENT_ACTIVATE_ALREADY_TODAY,
					3 : localeinfo.EVENT_ACTIVATE_HWID_LIMIT,
					4 : getattr(localeinfo, "EVENT_ACTIVATE_FAILED", "Event activation failed. Please try again."),
					5 : getattr(localeinfo, "EVENT_ACTIVATE_ACCOUNT_LIMIT", "Your account has already used all activations of this event for today."),
				}
				msg = msgDict.get(bResult, None)
				if msg:
					chat.AppendChat(chat.CHAT_TYPE_INFO, msg)

	if app.ENABLE_CHATTING_WINDOW_RENEWAL:
		def RefreshWhisperMessengerButtons(self):
			if self.whisperDialogDict:
				for dlg in self.whisperDialogDict.itervalues():
					dlg.RefreshMessengerButtons()

	def RefreshMessenger(self):
		self.wndMessenger.RefreshMessenger()

	def RefreshGuildInfoPage(self):
		self.wndGuild.RefreshGuildInfoPage()

	def RefreshGuildBoardPage(self):
		self.wndGuild.RefreshGuildBoardPage()

	def RefreshGuildMemberPage(self):
		self.wndGuild.RefreshGuildMemberPage()

	def RefreshGuildMemberPageGradeComboBox(self):
		self.wndGuild.RefreshGuildMemberPageGradeComboBox()

	def RefreshGuildSkillPage(self):
		self.wndGuild.RefreshGuildSkillPage()

	def RefreshGuildGradePage(self):
		self.wndGuild.RefreshGuildGradePage()

	def RefreshGuildContractsPage(self):
		if self.wndGuild and hasattr(self.wndGuild, "RefreshGuildContractsPage"):
			self.wndGuild.RefreshGuildContractsPage()

	def RefreshGuildSkillsPage(self):
		if self.wndGuild and hasattr(self.wndGuild, "RefreshGuildSkillsPage"):
			self.wndGuild.RefreshGuildSkillsPage()

	def DeleteGuild(self):
		self.wndMessenger.ClearGuildMember()
		self.wndGuild.DeleteGuild()

	def OnBlockMode(self, mode):
		self.dlgSystem.OnBlockMode(mode)

	## Calling Functions
	# PointReset
	def OpenPointResetDialog(self):
		self.dlgPointReset.Show()
		self.dlgPointReset.SetTop()

	def ClosePointResetDialog(self):
		self.dlgPointReset.Close()

	# Shop
	def OpenShopDialog(self, vid, remote = 0):
		import chr
		if remote or chr.IsNPC(vid):
			self.wndInventory.Show()
			self.wndInventory.SetTop()

			self.dlgShop.Open(vid, remote)
			self.dlgShop.SetTop()
	#dream#	else:
	#dream#		self.dlgPrivateShop.Open(vid)
		#dream#	self.dlgPrivateShop.SetTop()

		# self.dlgShop.Open(vid)
		# self.dlgShop.SetTop()
		# event.SetInterfaceWindow(self)

	def CloseShopDialog(self):
		# self.dlgShop.Close()
		if self.dlgShop.IsShow():
			self.dlgShop.Close()

	def RefreshShopDialog(self):
		# self.dlgShop.Refresh()
		if self.dlgShop.IsShow():
			self.dlgShop.Refresh()

	## Quest
	def OpenCharacterWindowQuestPage(self):
		self.wndCharacter.Show()
		self.wndCharacter.SetState("QUEST")

	def OpenQuestWindow(self, skin, idx):
		wnds = ()

		q = uiquest.QuestDialog(skin, idx)
		q.SetWindowName("QuestWindow" + str(idx))
		q.Show()
		if skin:
			q.Lock()
			wnds = self.__HideWindows()

			# UNKNOWN_UPDATE
			q.AddOnDoneEvent(lambda tmp_self, args=wnds: self.__ShowWindows(args))
			# END_OF_UNKNOWN_UPDATE

		if skin:
			q.AddOnCloseEvent(q.Unlock)
		q.AddOnCloseEvent(lambda key = self.wndQuestWindowNewKey:ui.__mem_func__(self.RemoveQuestDialog)(key))
		self.wndQuestWindow[self.wndQuestWindowNewKey] = q

		self.wndQuestWindowNewKey = self.wndQuestWindowNewKey + 1

		# END_OF_UNKNOWN_UPDATE

	def RemoveQuestDialog(self, key):
		del self.wndQuestWindow[key]

	## Exchange
	def StartExchange(self):
		self.dlgExchange.OpenDialog()
		self.dlgExchange.Refresh()

	def EndExchange(self):
		self.dlgExchange.CloseDialog()

	def RefreshExchange(self):
		self.dlgExchange.Refresh()

	if app.WJ_ENABLE_TRADABLE_ICON:
		def AddExchangeItemSlotIndex(self, idx):
			self.dlgExchange.AddExchangeItemSlotIndex(idx)

	## Party
	if app.WJ_SHOW_PARTY_ON_MINIMAP:
		def AddPartyMember(self, pid, name, mapIdx, channel):
			self.wndParty.AddPartyMember(pid, name, mapIdx, channel)
			self.__ArrangeQuestButton()
	else:
		def AddPartyMember(self, pid, name):
			self.wndParty.AddPartyMember(pid, name)
			self.__ArrangeQuestButton()

	def UpdatePartyMemberInfo(self, pid):
		self.wndParty.UpdatePartyMemberInfo(pid)

	def RemovePartyMember(self, pid):
		self.wndParty.RemovePartyMember(pid)

		self.__ArrangeQuestButton()

	if app.WJ_SHOW_PARTY_ON_MINIMAP:
		def LinkPartyMember(self, pid, vid, mapIdx, channel):
			self.wndParty.LinkPartyMember(pid, vid, mapIdx, channel)
	else:
		def LinkPartyMember(self, pid, vid):
			self.wndParty.LinkPartyMember(pid, vid)

	def UnlinkPartyMember(self, pid):
		self.wndParty.UnlinkPartyMember(pid)

	def UnlinkAllPartyMember(self):
		self.wndParty.UnlinkAllPartyMember()

	def ExitParty(self):
		self.wndParty.ExitParty()

		self.__ArrangeQuestButton()

	def PartyHealReady(self):
		self.wndParty.PartyHealReady()

	def ChangePartyParameter(self, distributionMode):
		self.wndParty.ChangePartyParameter(distributionMode)

	## Safebox
	def AskSafeboxPassword(self):
		if self.wndSafebox.IsShow():
			return

		# SAFEBOX_PASSWORD
		self.dlgPassword.SetTitle(localeinfo.PASSWORD_TITLE)
		self.dlgPassword.SetSendMessage("/safebox_password ")
		# END_OF_SAFEBOX_PASSWORD

		self.dlgPassword.ShowDialog()

	def OpenSafeboxWindow(self, size):
		self.dlgPassword.CloseDialog()
		self.wndSafebox.ShowWindow(size)

	def RefreshSafeboxMoney(self):
		self.wndSafebox.RefreshSafeboxMoney()

	def CommandCloseSafebox(self):
		self.wndSafebox.CommandCloseSafebox()

	## HilightSlot Change
	def DeactivateSlot(self, slotindex, type):
		self.wndInventory.DeactivateSlot(slotindex, type)

	## HilightSlot Change
	def ActivateSlot(self, slotindex, type):
		self.wndInventory.ActivateSlot(slotindex, type)

	if app.ENABLE_CHANGE_LOOK_SYSTEM:
		def ChangeWindowOpen(self, type):
			if self.wndChangeLook:
				if not shop.GetNameDialogOpen():
					self.wndChangeLook.Open(type)

				if self.dlgRefineNew:
					if self.dlgRefineNew.IsShow:
						self.wndChangeLook.Close()

	if app.ENABLE_GEM_SYSTEM:
		def OpenGuiGem(self):
			self.wndGemG.Open()

		def GemCheck(self):
			self.wndGemG.SucceedGem()

		def OpenGuiGemMarket(self):
			self.wndGemM.Open()

		def GemMarketItems(self, vnums, gem, count):
			self.wndGemM.Information(vnums, gem, count)
			self.wndGemM.LoadInformation()

		def GemMarketSlotsDesblock(self, slot0, slot1, slot2, slot3, slot4, slot5):
			self.wndGemM.SlotsDesblock(slot0, slot1, slot2, slot3, slot4, slot5)

		def GemMarketClear(self):
			self.wndGemM.Clear()

		def GemTime(self,time):
			self.wndGemM.Time(time)

	if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
		def OpenSkillbookCombinationDialog(self):
			if self.wndSkillBookCombination.IsShow():
				return

			if self.privateShopBuilder.IsShow():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_NOTICE_NOT_OPEN)
				return

			self.wndSkillBookCombination.Open()
			self.wndSkillBookCombination.Show()

			if not self.wndInventory.IsShow():
				self.wndInventory.Show()

	# ITEM_MALL
	def AskMallPassword(self):
		if self.wndMall.IsShow():
			return

		self.dlgPassword.SetTitle(localeinfo.MALL_PASSWORD_TITLE)
		self.dlgPassword.SetSendMessage("/mall_password ")
		self.dlgPassword.ShowDialog()

	def OpenMallWindow(self, size):
		self.dlgPassword.CloseDialog()
		self.wndMall.ShowWindow(size)

	def CommandCloseMall(self):
		self.wndMall.CommandCloseMall()
	# END_OF_ITEM_MALL

	## Guild
	def OnStartGuildWar(self, guildSelf, guildOpp):
		self.wndGuild.OnStartGuildWar(guildSelf, guildOpp)

		guildWarScoreBoard = uiguild.GuildWarScoreBoard()
		guildWarScoreBoard.Open(guildSelf, guildOpp)
		guildWarScoreBoard.Show()
		self.guildScoreBoardDict[uiguild.GetGVGKey(guildSelf, guildOpp)] = guildWarScoreBoard

	def OnEndGuildWar(self, guildSelf, guildOpp):
		self.wndGuild.OnEndGuildWar(guildSelf, guildOpp)

		key = uiguild.GetGVGKey(guildSelf, guildOpp)

		if not self.guildScoreBoardDict.has_key(key):
			return

		self.guildScoreBoardDict[key].Destroy()
		del self.guildScoreBoardDict[key]

	# GUILDWAR_MEMBER_COUNT
	def UpdateMemberCount(self, gulidID1, memberCount1, guildID2, memberCount2):
		key = uiguild.GetGVGKey(gulidID1, guildID2)

		if not self.guildScoreBoardDict.has_key(key):
			return

		self.guildScoreBoardDict[key].UpdateMemberCount(gulidID1, memberCount1, guildID2, memberCount2)
	# END_OF_GUILDWAR_MEMBER_COUNT

	def OnRecvGuildWarPoint(self, gainGuildID, opponentGuildID, point):
		key = uiguild.GetGVGKey(gainGuildID, opponentGuildID)
		if not self.guildScoreBoardDict.has_key(key):
			return

		guildBoard = self.guildScoreBoardDict[key]
		guildBoard.SetScore(gainGuildID, opponentGuildID, point)

	## PK Mode
	def OnChangePKMode(self):
		self.wndCharacter.RefreshAlignment()
		self.dlgSystem.OnChangePKMode()

	## Refine
	def OpenRefineDialog(self, targetItemPos, nextGradeItemVnum, cost, prob, type, apply_random_list, src_vnum):
		self.dlgRefineNew.Open(targetItemPos, nextGradeItemVnum, cost, prob, type, apply_random_list, src_vnum)

	if app.ENABLE_AUTO_REFINE:
		def RefineFail(self, isFail):
			self.dlgRefineNew.CheckRefine(isFail)

	def AppendMaterialToRefineDialog(self, vnum, count):
		self.dlgRefineNew.AppendMaterial(vnum, count)

	def SetAffectShower(self, shower):
		#self.uiAffectshower = proxy(shower)
		self.uiAffectshower = shower

	def SettargetBoard(self, targetBoard):
		#self.uitargetBoard = proxy(targetBoard)
		self.uitargetBoard = targetBoard

	## Show & Hide
	def ShowDefaultWindows(self):
		self.wndTaskBar.Show()
		self.wndMiniMap.Show()
		self.wndMiniMap.ShowMiniMap()

		# Horse upgrade: re-assert the progress popup after a warp/map change.
		# The engine hides floating windows during the transition; this brings it
		# back if the player is mid-mission and the toggle is on.
		if app.ENABLE_HORSE_UPGRADE and getattr(self, 'wndHorseUpgrade', None):
			try: self.wndHorseUpgrade.EnsurePopupVisible()
			except: pass
		if app.ENABLE_12ZI:
			if self.wndBead:
				self.wndBead.Show()
		if self.wndEnergyBar:
			self.wndEnergyBar.Show()
		if self.wndGameButton:
			self.wndGameButton.Show()

		if self.uiAffectshower:
			self.uiAffectshower.Show()

		if self.wndParty:
			self.wndParty.Show()
		
		self.IsHideUiMode = False

	def IsHideUiMode(self):
		return self.IsHideUiMode

	def ShowAllWindows(self):
		self.wndTaskBar.Show()

		self.wndCharacter.Show()
		self.wndInventory.Show()

		self.wndExpandedMoneyTaskBar.Show()
		self.wndExpandedMoneyTaskBar.SetTop()

		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			self.wndDragonSoul.Show()
			self.wndDragonSoulRefine.Show()

		self.wndChat.Show()
		self.yangText.Show()
		self.wndMiniMap.Show()
		if app.ENABLE_12ZI:
			if self.wndBead:
				self.wndBead.Show()
			if self.wnd12ziTimer:
				self.wnd12ziTimer.Show()
			if self.wnd12ziReward:
				self.wnd12ziReward.Show()

		if self.wndEnergyBar:
			self.wndEnergyBar.Show()

		if self.wndExpandedTaskBar:
			self.wndExpandedTaskBar.Show()
			self.wndExpandedTaskBar.SetTop()

		#uhm?
		#if app.QUICK_SELL_SYSTEM:
		#	if self.wndQuickSell:
		#		hideWindows += self.wndQuickSell,

	def HideAllWindows(self):
		if app.USE_EVENT_MANAGER_EXPANDED and self.wndEventAlert:
			self.wndEventAlert.Hide()

		if getattr(self, "wndWhisperChat", None):
			self.wndWhisperChat.Close()

		if self.wndParty:
			self.wndParty.Hide()

		if self.uiAffectshower:
			self.uiAffectshower.Hide()

		if app.__BUFFI_SUPPORT__ and getattr(self, "wndCompanion", None):
			self.wndCompanion.Close()
		if app.__BUFFI_SUPPORT__ and getattr(self, "wndCompanionUpgrade", None):
			self.wndCompanionUpgrade.Close()
		if app.__BUFFI_SUPPORT__ and getattr(self, "wndCompanionHelp", None):
			self.wndCompanionHelp.Close()
		if app.__BUFFI_SUPPORT__ and getattr(self, "wndCompanionRideHelp", None):
			self.wndCompanionRideHelp.Close()
		if app.__BUFFI_SUPPORT__ and getattr(self, "wndPetUpgradeHelp", None):
			self.wndPetUpgradeHelp.Close()
		if app.__BUFFI_SUPPORT__ and getattr(self, "wndPetHelp", None):
			self.wndPetHelp.Close()

		if getattr(self, "wndBundleBox", None):
			self.wndBundleBox.Close()

		if getattr(self, "wndTitle", None):
			self.wndTitle.Close()

		if app.ENABLE_RENDER_TARGET:
			if self.wndRenderTargetInterface:
				self.wndRenderTargetInterface.Hide()

		if self.uitargetBoard:
			self.uitargetBoard.Hide()

		if self.wndMiniGame:
			self.wndMiniGame.hide_mini_game_dialog()

		if self.wndTaskBar:
			self.wndTaskBar.Hide()

		if self.wndGameButton:
			self.wndGameButton.Hide()

		if app.ENABLE_SKILL_LEARN_SYSTEM and self.wndLearnSkill:
			self.wndLearnSkill.Hide()

		if self.wndEnergyBar:
			self.wndEnergyBar.Hide()

		if self.wndCharacter:
			if app.USE_BONUS_PAGE:
				self.wndCharacter.Hide(True)
			else:
				self.wndCharacter.Hide()

		if self.wndInventory:
			self.wndInventory.Hide()

		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			self.wndDragonSoul.Hide()
			self.wndDragonSoulRefine.Hide()

		if self.wndChat:
			self.wndChat.hide_btnChatSizing()
			self.wndChat.Hide()

		if self.yangText:
			self.yangText.Hide()

		if app.ENABLE_12ZI:
			if self.wndBead:
				self.wndBead.Hide()
			if self.wnd12ziTimer:
				self.wnd12ziTimer.Hide()
			if self.wnd12ziReward:
				self.wnd12ziReward.Hide()

		if self.wndMiniMap:
			self.wndMiniMap.Hide()

		if app.ENABLE_ANTI_MULTIPLE_FARM:
			if self.wndAntiMultipleFarm:
				self.wndAntiMultipleFarm.Hide()

		if self.wndMessenger:
			self.wndMessenger.Hide()
		
		if app.ENABLE_EXTENDED_BATTLE_PASS:
			if self.wndBattlePassExtended:
				self.wndBattlePassExtended.Hide()
		if app.ENABLE_ASLAN_TELEPORTPANEL:
			if self.wndTeleportPanel:
				self.wndTeleportPanel.Hide()
		if self.wndGuild:
			self.wndGuild.Hide()

		if self.wndExpandedTaskBar:
			self.wndExpandedTaskBar.Hide()

		if app.ENABLE_PARTY_WAR:
			if self.wndPartywarBoard:
				self.wndPartywarBoard.Hide()
			if self.wndPartywarTimer:
				self.wndPartywarTimer.Hide()
			if self.wndPartywarButton:
				self.wndPartywarButton.Hide()
			if self.wndPartywarPlayerBoard:
				self.wndPartywarPlayerBoard.Hide()

		if app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM:
			if self.wndSetCustomAttribute:
				self.wndSetCustomAttribute.Hide()

		if app.USE_DUNGEON_INFO:
			if self.wndDungeonInfo:
				self.wndDungeonInfo.Hide()

		if app.USE_AURA_SYSTEM:
			if self.wndAura:
				self.wndAura.Hide()

		self.wndExpandedMoneyTaskBar.Hide()

		if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
			if self.wndSkillBookCombination:
				self.wndSkillBookCombination.Hide()

		if app.ENABLE_MYSHOP_DECO:
			if self.wndMyShopDeco:
				self.wndMyShopDeco.Hide()

		if app.ENABLE_SWITCHBOT:
			if self.wndSwitchbot:
				self.wndSwitchbot.Hide()

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			if self.wndSpecialInventory:
				self.wndSpecialInventory.Hide()

		if app.ENABLE_GROWTH_PET_SYSTEM: 
			if self.wndPetInfoWindow:
				self.wndPetInfoWindow.Hide()
				if self.wndPetInfoWindow.wndPetMiniInfo:
					self.wndPetInfoWindow.wndPetMiniInfo.Hide()

		if app.ENABLE_MAILBOX:
			if self.mail_box:
				self.mail_box.Hide()
		
		if app.ENABLE_BIOLOG_SYSTEM:
			if self.wndBiologManagerPanel:
				self.wndBiologManagerPanel.Hide()
		
		if app.ENABLE_ULTIMATE_REGEN and self.wndTrackWindow:
			self.wndTrackWindow.Hide()

		if app.ENABLE_WORLDBOSS and self.wndWorldBoss:
			self.wndWorldBoss.DestroyAllAlerts()
			self.wndWorldBoss.Hide()

		if app.ENABLE_WORLDBOSS_V2_DAMAGE_METER and getattr(self, "wndWBDamageMeter", None):
			self.wndWBDamageMeter.Close()

		if app.ENABLE_HORSE_UPGRADE and getattr(self, "wndHorseUpgrade", None):
			self.wndHorseUpgrade.Close()

		if app.ENABLE_MISSION_QUEST:
			if self.wndMissionQuest:
				self.wndMissionQuest.Hide()

		if app.ADVANCED_BATTLE_PASS:
			if self.wndBattlePass:
				self.wndBattlePass.Hide()

		if app.ENABLE_NOTIFICATION_SYSTEM:
			if self.wndNotificationCenter:
				self.wndNotificationCenter.HideHistory()


		self.IsHideUiMode = True

	def ShowMouseImage(self):
		self.wndTaskBar.ShowMouseImage()

	def HideMouseImage(self):
		self.wndTaskBar.HideMouseImage()

	def ToggleChat(self):
		if True == self.wndChat.IsEditMode():
			self.wndChat.CloseChat()
		else:
			self.wndChat.OpenChat()

	def IsOpenChat(self):
		return self.wndChat.IsEditMode()

	def SetChatFocus(self):
		self.wndChat.SetChatFocus()

	if app.RENEWAL_DEAD_PACKET:
		def OpenRestartDialog(self, d_time):
			self.dlgRestart.OpenDialog(d_time)
			self.dlgRestart.SetTop()
	else:
		def OpenRestartDialog(self):
			self.dlgRestart.OpenDialog()
			self.dlgRestart.SetTop()

	def CloseRestartDialog(self):
		self.dlgRestart.Close()

	def ToggleSystemDialog(self):
		if False == self.dlgSystem.IsShow():
			self.dlgSystem.OpenDialog()
			self.dlgSystem.SetTop()
		else:
			self.dlgSystem.Close()

	def OpenSystemDialog(self):
		self.dlgSystem.OpenDialog()
		self.dlgSystem.SetTop()

	def ToggleMessenger(self):
		opening = not self.wndMessenger.IsShow()
		if self.wndMessenger.IsShow():
			self.wndMessenger.Hide()
		else:
			self.wndMessenger.SetTop()
			self.wndMessenger.Show()
		if COMMUNITY_SYSTEM:
			self.wndCommunity.RefreshRequestBadge()
		elif opening:
			self.unseenMessengerCount = 0
			uibadge.SetCount("messenger", 0)
			self.__ShowNextFriendRequest()
	if app.ENABLE_RENDER_TARGET:
		def __MakeRenderTargetWindow(self):
			if self.wndRenderTargetInterface == None:
				self.wndRenderTargetInterface = uiRenderTarget.RenderTargetWindow()

		def OpenRenderTargetWindow(self, type, vnum):
			self.__MakeRenderTargetWindow()
			self.wndRenderTargetInterface.Open(type, vnum)

		def OpenRenderTargetWindowSet(self, slots):
			self.__MakeRenderTargetWindow()
			return self.wndRenderTargetInterface.OpenSet(slots)

		def RefreshRenderTargetWindowSet(self, slots):
			if self.wndRenderTargetInterface == None:
				return False
			return self.wndRenderTargetInterface.RefreshSet(slots)

	def ToggleMiniMap(self):
		if app.IsPressed(app.DIK_LSHIFT) or app.IsPressed(app.DIK_RSHIFT):
			if False == self.wndMiniMap.isShowMiniMap():
				self.wndMiniMap.ShowMiniMap()
				self.wndMiniMap.SetTop()
			else:
				self.wndMiniMap.HideMiniMap()
		else:
			self.wndMiniMap.ToggleAtlasWindow()

	def PressMKey(self):
		if app.IsPressed(app.DIK_LALT) or app.IsPressed(app.DIK_RALT):
			self.ToggleMessenger()
		else:
			self.ToggleMiniMap()

	def SetMapName(self, mapName):
		self.wndMiniMap.SetMapName(mapName)

		# Horse upgrade: a warp has just finished. Ask the main window to
		# request fresh state from the server and re-assert the popup.
		# Engine-level hides during the transition can leave the popup invisible
		# even though it was open before; this brings it back.
		if app.ENABLE_HORSE_UPGRADE and getattr(self, 'wndHorseUpgrade', None):
			try: self.wndHorseUpgrade.OnMapChanged()
			except: pass

		if app.__BUFFI_SUPPORT__ and getattr(self, 'wndCompanion', None):
			try: self.wndCompanion.OnMapChanged()
			except: pass

	def MiniMapScaleUp(self):
		self.wndMiniMap.ScaleUp()

	def MiniMapScaleDown(self):
		self.wndMiniMap.ScaleDown()

	def ToggleCharacterWindow(self, state):
		if False == player.IsObserverMode():
			if False == self.wndCharacter.IsShow():
				self.OpenCharacterWindowWithState(state)
			else:
				if state == self.wndCharacter.GetState():
					self.wndCharacter.Hide()
				else:
					self.wndCharacter.SetState(state)

	def OpenCharacterWindowWithState(self, state):
		if False == player.IsObserverMode():
			self.wndCharacter.SetState(state)
			self.wndCharacter.Show()
			self.wndCharacter.SetTop()

	def ToggleCharacterWindowStatusPage(self):
		self.ToggleCharacterWindow("STATUS")



#Add
	if app.BL_KILL_BAR:
		def AddKillInfo(self, killer, victim, killer_race, victim_race, weapon_type,color_type):
			self.wndMiniMap.AddKillInfo(killer, victim, killer_race, victim_race, weapon_type,color_type)

	def ToggleInventoryWindow(self):
		if not player.IsObserverMode():
			if self.wndInventory.IsShow():
				self.wndInventory.OverOutItem()
				self.wndInventory.Close()
			else:
				self.wndInventory.Show()
				self.wndInventory.SetTop()

				self.wndExpandedMoneyTaskBar.Show()
				self.wndExpandedMoneyTaskBar.SetTop()
		# if app.USE_CRAFT_ITEM_SYSTEM:
			# self.ToggleCraftItem()

	if app.ENABLE_ASLAN_TELEPORTPANEL:
		def ToggleTeleportPanel(self):
			if False == self.wndTeleportPanel.IsShow():
				self.wndTeleportPanel.Show()
				self.wndTeleportPanel.SetTop()
			else:
				self.wndTeleportPanel.Close()
		
		def ReceiveTeleportQuestCommand(self, command):
			self.wndTeleportPanel.ReceiveQuestCommand(command)


	def ToggleExpandedButton(self):
		if False == player.IsObserverMode():
			if False == self.wndExpandedTaskBar.IsShow():
				self.wndExpandedTaskBar.Show()
				if self.wndChat and self.wndChat.IsEditMode():
					(btnX, btnY) = self.wndChat.btnChatSizing.GetGlobalPosition()
					self.wndExpandedTaskBar.OnChatOpen(btnY)
				else:
					self.wndExpandedTaskBar.OnChatClose()
			else:
				self.wndExpandedTaskBar.Close()

	def __OnChatStateChange(self, isOpen, chatTopY):
		if not self.wndExpandedTaskBar or not self.wndExpandedTaskBar.IsShow():
			return

		if isOpen:
			self.wndExpandedTaskBar.OnChatOpen(chatTopY)
		else:
			self.wndExpandedTaskBar.OnChatClose()

	# def ToggleExpandedMoneyButton(self):
		# if self.wndExpandedMoneyTaskBar.IsShow():
			# self.wndExpandedMoneyTaskBar.Close()
		# else:
			# self.wndExpandedMoneyTaskBar.Show()
			# self.wndExpandedMoneyTaskBar.SetTop()

	if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
		def ToggleSpecialInventoryWindow(self):
			if False == player.IsObserverMode():
				if False == self.wndSpecialInventory.IsShow():
					self.wndSpecialInventory.Show()
					self.wndSpecialInventory.SetTop()
				else:
					self.wndSpecialInventory.OverOutItem()
					self.wndSpecialInventory.Close()

		def OpenSpecialInventoryWindow(self, category = 0):
			if False == player.IsObserverMode():
				if False == self.wndSpecialInventory.IsShow():
					self.wndSpecialInventory.Show()
					self.wndSpecialInventory.SetTop()
					self.wndSpecialInventory.SetInventoryType(category)

	def OpenCostumeWindow(self, pageidx):
		self.wndInventory.ShowCostumeInventory(pageidx)

	def IsShowDlgQuestionWindow(self):
			return False

	def CloseDlgQuestionWindow(self):
		if self.wndInventory.IsDlgQuestionShow():
			self.wndInventory.CancelDlgQuestion()
		if self.wndDragonSoul.IsDlgQuestionShow():
			self.wndDragonSoul.CancelDlgQuestion()

	def SetUseItemMode(self, bUse):
		self.wndInventory.SetUseItemMode(bUse)
		self.wndDragonSoul.SetUseItemMode(bUse)

	def DragonSoulActivate(self, deck):
		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			self.wndDragonSoul.ActivateDragonSoulByExtern(deck)

	def DragonSoulDeactivate(self):
		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			self.wndDragonSoul.DeactivateDragonSoul()

	def OnDragonSoulSetBonus(self, points, tier, nextThreshold, stats):
		if self.wndDragonSoul:
			self.wndDragonSoul.SetSetBonusInfo(points, tier, nextThreshold, stats)

	if app.ENABLE_MISSION_QUEST:
		def ToggleMissionQuest(self):
			if self.wndMissionQuest.IsShow() == FALSE:
				self.wndMissionQuest.Show()
			else:
				self.wndMissionQuest.Close()

	if app.ADVANCED_BATTLE_PASS:
		def ShowBattlePass(self):
			if self.wndBattlePass.IsShow() == FALSE:
				self.wndBattlePass.Show()
			else:
				self.wndBattlePass.Close()

	if app.ENABLE_HORSE_UPGRADE:
		def ToggleHorseUpgrade(self):
			if getattr(self, 'wndHorseUpgrade', None) is None:
				return
			if self.wndHorseUpgrade.IsShow() == FALSE:
				self.wndHorseUpgrade.Open()
			else:
				self.wndHorseUpgrade.Close()

	if app.__BUFFI_SUPPORT__:
		def ToggleCompanion(self):
			if getattr(self, 'wndCompanion', None) is None:
				return
			if self.wndCompanion.IsShow() == FALSE:
				self.wndCompanion.Open()
			else:
				self.wndCompanion.Close()

		# U9: pet-page-aware toggle for the retired pet window's openers (P key /
		# taskbar pet button / mini-window icon). Closed -> open on the pet tab;
		# open on the buffi tab -> just switch tabs; open on the pet tab -> close
		# (preserves the legacy open/close toggle feel).
		def ToggleCompanionPetPage(self):
			if getattr(self, "wndCompanion", None) is None:
				return
			if self.wndCompanion.IsShow() == FALSE:
				self.wndCompanion.Open()
				self.wndCompanion.OpenPetPage()
			elif not self.wndCompanion.IsPetPageActive():
				self.wndCompanion.OpenPetPage()
			else:
				self.wndCompanion.Close()

		def ToggleCompanionRidePage(self):
			if getattr(self, "wndCompanion", None) is None:
				return
			if self.wndCompanion.IsShow() == FALSE:
				self.wndCompanion.Open()
				self.wndCompanion.OpenRidePage()
			elif not self.wndCompanion.IsRidePageActive():
				self.wndCompanion.OpenRidePage()
			else:
				self.wndCompanion.Close()

		# Growth-pet page (Companion window pet tab): called by the GC pet-rework-info push
		# (game.py PetReworkInfoRefresh) and by RefreshStatus point deltas. Cheap -- the
		# windows themselves gate on being shown (pet page active / dialog up).
		def RefreshCompanionPetPage(self):
			if getattr(self, "wndCompanion", None):
				self.wndCompanion.RefreshPetPage()
			wnd = getattr(self, "wndPetUpgrade", None)
			if wnd and wnd.IsShow():
				wnd.Refresh()
			wnd = getattr(self, "wndPetSkillUpgrade", None)
			if wnd and wnd.IsShow():
				wnd.Refresh()
			wnd = getattr(self, "wndPetUpgradeHelp", None)
			if wnd and wnd.IsShow():
				wnd.Refresh()   # live pity/chance/current-Type marker on the help page
			wnd = getattr(self, "wndPetHelp", None)
			if wnd and wnd.IsShow():
				wnd.Refresh()   # live caps/evolution/lifetime-cap on the pet help pages

		# Opened by the Companion pet page's Upgrade button (Evolve | Upgrade Type tabs).
		def OpenPetUpgrade(self):
			wnd = getattr(self, "wndPetUpgrade", None)
			if wnd:
				wnd.Open()

		# "?" on the pet Upgrade window -> the ACTIVE TAB's help page (Evolution and
		# Type upgrade are separate systems -> separate pages; mode = the tab index).
		# Toggle only when re-asking for the mode already on screen.
		def OpenPetUpgradeHelp(self, mode = 0):
			wnd = getattr(self, "wndPetUpgradeHelp", None)
			if wnd:
				if wnd.IsShow() and wnd.GetMode() == mode:
					wnd.Close()
				else:
					wnd.Open(mode)

		# Tab switched on the Upgrade window: re-target an OPEN help window to the
		# new tab's page (never opens it by itself).
		def SyncPetUpgradeHelp(self, mode):
			wnd = getattr(self, "wndPetUpgradeHelp", None)
			if wnd and wnd.IsShow() and wnd.GetMode() != mode:
				wnd.Open(mode)

		# The Companion pet page's two "?" buttons -> the pet help popup
		# (mode 0 = general lifetime/feedstuff/potions, 1 = the EXP journey;
		# ints match uipethelp.MODE_GENERAL / MODE_EXP). Toggle only when
		# re-asking for the mode already on screen.
		def OpenPetHelp(self, mode = 0):
			wnd = getattr(self, "wndPetHelp", None)
			if wnd:
				if wnd.IsShow() and wnd.GetMode() == mode:
					wnd.Close()
				else:
					wnd.Open(mode)

		# Opened by a skill slot's "+" on the Companion pet page (no-fail ladder costs).
		def OpenPetSkillUpgrade(self, slot):
			wnd = getattr(self, "wndPetSkillUpgrade", None)
			if wnd:
				wnd.Open(slot)

		# Opened by the Companion pet page's Feed button: the (now tabbed) legacy feed
		# window in item-EXP mode; the Duration rail tab switches the mode in-window.
		def OpenPetFeed(self):
			wnd = getattr(self, "wndPetInfoWindow", None)
			if wnd:
				wnd.ClickPetFeedButton(player.FEED_EXP_EVENT)

		# Opened by the Companion window's Evolve button (it passes its live stage + pity).
		def OpenCompanionUpgrade(self, curStage, evolveFail):
			wnd = getattr(self, "wndCompanionUpgrade", None)
			if wnd:
				wnd.Open(curStage, evolveFail)

		# Opened by the Companion window's "?" button -> the buffi-system explainer popup.
		def OpenCompanionHelp(self):
			wnd = getattr(self, "wndCompanionHelp", None)
			if wnd:
				if wnd.IsShow():
					wnd.Close()
				else:
					wnd.Open()

		# The ride page's two contextual "?" buttons -> the growth-mount help popup
		# (mode 0 = leveling browser, 1 = skill browser; ints match
		# uicompanionridehelp.MODE_LEVEL / MODE_SKILL). Toggle only when re-asking
		# for the mode already on screen (the OpenPetHelp semantics).
		def OpenCompanionRideHelp(self, mode = 0):
			wnd = getattr(self, "wndCompanionRideHelp", None)
			if wnd:
				if wnd.IsShow() and wnd.GetMode() == mode:
					wnd.Close()
				else:
					wnd.Open(mode)

		# Buffi name dialog (growth-pet-hatch style): the server opens it when a BUFFI_NAME item is used,
		# passing the item's inventory cell. On accept we send the typed name + that cell back to the server.
		def OpenBuffiNameDialog(self, cell):
			self.buffiNameCell = cell
			dlg = uicommon.InputDialog()
			dlg.SetTitle(getattr(localeinfo, "COMPANION_NAME_TITLE", "Buffi Name"))
			dlg.SetMaxLength(20)   # BUFFI_NAME_MAX
			dlg.SetAcceptEvent(ui.__mem_func__(self.__AcceptBuffiNameDialog))
			dlg.SetCancelEvent(ui.__mem_func__(self.__CloseBuffiNameDialog))
			dlg.Open()
			self.buffiNameDialog = dlg

		def __AcceptBuffiNameDialog(self):
			dlg = getattr(self, "buffiNameDialog", None)
			if dlg:
				name = dlg.GetText()
				if name:
					net.SendBuffiNamePacket(name, self.buffiNameCell)
			self.__CloseBuffiNameDialog()
			return True

		def __CloseBuffiNameDialog(self):
			dlg = getattr(self, "buffiNameDialog", None)
			if dlg:
				dlg.Close()
			self.buffiNameDialog = None
			return True

		def OnBuffiStatus(self, summoned, stage, level, intVal, exp, expToNext, expireAt, ore0, ore1, ore2, oreExp0, oreExp1, oreExp2, bossPct, nameExpire, name, evolveFail=0):
			# Cache the live buffi summary on EVERY status push (server pushes on every state change),
			# so the summon-scroll item tooltip can show name/level/INT/ores without the window open.
			constinfo.BUFFI_SUMMONED    = 1 if summoned else 0
			constinfo.BUFFI_TT_INT      = intVal
			constinfo.BUFFI_TT_LEVEL    = level
			constinfo.BUFFI_TT_NAME     = name or ""
			constinfo.BUFFI_TT_ORES     = (ore0, ore1, ore2)
			constinfo.BUFFI_TT_EXPIRE   = expireAt   # tooltip duration line (remaining / EXPIRED guidance)
			wnd = getattr(self, "wndCompanion", None)
			if wnd and wnd.IsShow():
				wnd.RefreshFromStatus(summoned, stage, level, intVal, exp, expToNext, expireAt, ore0, ore1, ore2, oreExp0, oreExp1, oreExp2, bossPct, nameExpire, name, evolveFail)
			# Keep the Upgrade dialog's requirement rows + pity counter live after each evolve attempt.
			up = getattr(self, "wndCompanionUpgrade", None)
			if up and up.IsShow():
				up.OnBuffiStatus(stage, evolveFail)

	if app.ENABLE_DS_SET:
		def DragonSoulSetGrade(self, grade):
			self.wndDragonSoul.SetDSSetGrade(grade)

	def Highligt_Item(self, inven_type, inven_pos):
		if player.DRAGON_SOUL_INVENTORY == inven_type:
			if app.ENABLE_DRAGON_SOUL_SYSTEM:
				self.wndDragonSoul.HighlightSlot(inven_pos)
		elif app.WJ_ENABLE_PICKUP_ITEM_EFFECT and player.INVENTORY == inven_type:
			self.wndInventory.HighlightSlot(inven_pos)
			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				self.wndSpecialInventory.HighlightSlot(inven_pos)

	def DragonSoulGiveQuilification(self):
		self.DRAGON_SOUL_IS_QUALIFIED = True
		#self.wndExpandedTaskBar.SetToolTipText(uitaskbar.ExpandedTaskBar.BUTTON_DRAGON_SOUL, uiscriptlocale.TASKBAR_DRAGON_SOUL)

	def ToggleDragonSoulWindow(self):
		if False == player.IsObserverMode():
			if app.ENABLE_DRAGON_SOUL_SYSTEM:
				if False == self.wndDragonSoul.IsShow():
					self.wndDragonSoul.Show()
				else:
					self.wndDragonSoul.Close()

	def ToggleDragonSoulWindowWithNoInfo(self):
		if False == player.IsObserverMode():
			if app.ENABLE_DRAGON_SOUL_SYSTEM:
				if False == self.wndDragonSoul.IsShow():
					self.wndDragonSoul.Show()
				else:
					self.wndDragonSoul.Close()

	def FailDragonSoulRefine(self, reason, inven_type, inven_pos):
		if False == player.IsObserverMode():
			if app.ENABLE_DRAGON_SOUL_SYSTEM:
				if True == self.wndDragonSoulRefine.IsShow():
					self.wndDragonSoulRefine.RefineFail(reason, inven_type, inven_pos)

	def SucceedDragonSoulRefine(self, inven_type, inven_pos):
		if False == player.IsObserverMode():
			if app.ENABLE_DRAGON_SOUL_SYSTEM:
				if True == self.wndDragonSoulRefine.IsShow():
					self.wndDragonSoulRefine.RefineSucceed(inven_type, inven_pos)

	def OpenDragonSoulRefineWindow(self, refinetype = 0):
		if False == player.IsObserverMode():
			if app.ENABLE_DRAGON_SOUL_SYSTEM:
				if False == self.wndDragonSoulRefine.IsShow():
					self.wndDragonSoulRefine.Open(refinetype)
					
					if None != self.wndDragonSoul:
						if False == self.wndDragonSoul.IsShow():
							self.wndDragonSoul.Show()

	if app.ENABLE_DS_CHANGE_ATTR:
		def OpenDragonSoulRefineAttrWindow(self):
			self.OpenDragonSoulRefineWindow(1)

	def CloseDragonSoulRefineWindow(self):
		if False == player.IsObserverMode():
			if app.ENABLE_DRAGON_SOUL_SYSTEM:
				if True == self.wndDragonSoulRefine.IsShow():
					self.wndDragonSoulRefine.Close()

	if app.ENABLE_GROWTH_PET_SYSTEM:
		def PetInformationActivate(self):
			self.wndExpandedTaskBar.SetToolTipText(uitaskbar.ExpandedTaskBar.BUTTON_PET_INFO, uiscriptlocale.TASKBAR_PET_INFO)

		def TogglePetInformationWindow(self):
			if False == player.IsObserverMode():
				# >>> GROWTH PET U9 BEGIN: the legacy pet window is retired -- every
				# opener that lands here (P key, KEY_OPEN_PET, taskbar pet button)
				# goes to the Companion pet page instead. The legacy toggle stays
				# below for builds without the Companion window.
				if getattr(self, "wndCompanion", None) and hasattr(self, "ToggleCompanionPetPage"):
					self.ToggleCompanionPetPage()
					return
				# <<< GROWTH PET U9 END
				if not self.wndPetInfoWindow.IsShow():
					self.wndPetInfoWindow.Show()
				else:
					self.wndPetInfoWindow.Close()

	def ToggleGuildWindow(self):
		if not self.wndGuild.IsShow():
			if self.wndGuild.CanOpen():
				self.wndGuild.Open()
			elif app.ENABLE_GUILD_FINDER:
				self.ToggleGuildFinderWindow()
			else:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GUILD_YOU_DO_NOT_JOIN)
		else:
			self.wndGuild.OverOutItem()
			self.wndGuild.Hide()

	def ToggleChatLogWindow(self):
		if self.wndChatLog.IsShow():
			self.wndChatLog.Hide()
		else:
			self.wndChatLog.Show()

	if app.ENABLE_GEAR_SETS:
		def RefreshGearSetWindow(self):
			if self.wndFastEquip and self.wndFastEquip.IsShow():
				self.wndFastEquip.RefreshGearSetWindow()

		def ShowGearSetToast(self, slot):
			# Dungeon auto-equip notice. Reuse the always-on important popup so it shows even when
			# the loadout window is closed (auto-equip fires on dungeon entry). The preceding GC
			# UPDATE has already refreshed the cached set name, so net.GetGearSetName is valid here.
			name = net.GetGearSetName(slot)
			if not name:
				name = str(slot + 1)
			self.ShowImportantPopup(localeinfo.GEARSET_AUTO_EQUIP_TOAST % name)

		def LinkFastEquipItemFromInventory(self, invPos):
			# Right-click an inventory item while the loadout window is open -> link it into the selected
			# page (returns True if handled, so the caller skips normal use). Mirrors safebox right-click.
			if self.wndFastEquip and self.wndFastEquip.IsShow():
				self.wndFastEquip.LinkItemFromInventory(invPos)
				return True
			return False

	if app.ENABLE_SWITCHBOT:
		def ToggleSwitchbotWindow(self):
			if self.wndSwitchbot.IsShow():
				self.wndSwitchbot.Close()
			else:
				self.wndSwitchbot.Open()

		def RefreshSwitchbotWindow(self):
			if self.wndSwitchbot and self.wndSwitchbot.IsShow():
				self.wndSwitchbot.RefreshSwitchbotWindow()

		if app.USE_SWITCHBOT_FIX_MEDIUM_STUFF:
			def RefreshSwitchbotItem(self):
				if self.wndSwitchbot and self.wndSwitchbot.IsShow():
					self.wndSwitchbot.RefreshSwitchbotItem()
		else:
			def RefreshSwitchbotItem(self, slot):
				if self.wndSwitchbot and self.wndSwitchbot.IsShow():
					self.wndSwitchbot.RefreshSwitchbotItem(slot)

	def CheckGameButton(self):
		if self.wndGameButton:
			self.wndGameButton.CheckGameButton()

			if app.USE_DUNGEON_INFO and app.USE_DUNGEON_INFO_ADDON_LEVEL_CAP:
				if self.wndDungeonInfo and self.wndDungeonInfo.IsCapLevel():
					self.wndGameButton.RefreshCapLevelButton(True)
				else:
					self.wndGameButton.RefreshCapLevelButton(False)

	def __OnClickStatusPlusButton(self):
		self.ToggleCharacterWindow("STATUS")

	def __OnClickSkillPlusButton(self):
		self.ToggleCharacterWindow("SKILL")

	def __OnClickQuestButton(self):
		self.ToggleCharacterWindow("QUEST")

	def __OnClickHelpButton(self):
		player.SetPlayTime(1)
		self.CheckGameButton()
		self.OpenHelpWindow()

	def __OnClickBuildButton(self):
		self.BUILD_OpenWindow()

	if app.ENABLE_KEYCHANGE_SYSTEM:
		def ToggleHelpWindow(self):
			if self.wndHelp:
				if self.wndHelp.IsShow():
					self.CloseHelpWindow()
				else:
					self.OpenHelpWindow()

	def OpenHelpWindow(self):
		self.wndHelp.Open()
		self.wndUICurtain.Show()

	def CloseHelpWindow(self):
		self.wndHelp.Close()
		self.wndUICurtain.Hide()

	if app.ENABLE_MINI_GAME_OKEY:
		def OpenCardsInfoWindow(self):
			self.wndCardsInfo.Open()

		def OpenCardsWindow(self, safemode):
			self.wndCards.Open(safemode)

		def UpdateCardsInfo(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, hand_4, hand_4_v, hand_5, hand_5_v, cards_left, points):
			self.wndCards.UpdateCardsInfo(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, hand_4, hand_4_v, hand_5, hand_5_v, cards_left, points)

		def UpdateCardsFieldInfo(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points):
			self.wndCards.UpdateCardsFieldInfo(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points)

		def CardsPutReward(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points):
			self.wndCards.CardsPutReward(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points)

		def CardsShowIcon(self):
			self.wndCardsIcon.Show()

	# Show GIFT
	def ShowGift(self):
		self.wndTaskBar.ShowGift()

	def HideGift(self):
		self.wndTaskBar.HideGift()

	if app.ENABLE_CUBE_RENEWAL_WORLDARD:
		def BINARY_CUBE_RENEWAL_OPEN(self):
			self.wndCubeRenewal.Show()

	if app.USE_ACCE_SYSTEM:
		def ActAcce(self, iAct, bWindow):
			if iAct == 1:
				if bWindow == True:
					if not self.wndAcceCombine.IsOpened():
						self.wndAcceCombine.Open()

					if not self.wndInventory.IsShow():
						self.wndInventory.Show()
				else:
					if not self.wndAcceAbsorption.IsOpened():
						self.wndAcceAbsorption.Open()

					if not self.wndInventory.IsShow():
						self.wndInventory.Show()

				self.wndInventory.RefreshBagSlotWindow()
			elif iAct == 2:
				if bWindow == True:
					if self.wndAcceCombine.IsOpened():
						self.wndAcceCombine.Close()
				else:
					if self.wndAcceAbsorption.IsOpened():
						self.wndAcceAbsorption.Close()

				self.wndInventory.RefreshBagSlotWindow()
			elif iAct == 3 or iAct == 4:
				if bWindow == True:
					if self.wndAcceCombine.IsOpened():
						self.wndAcceCombine.Refresh(iAct)
				else:
					if self.wndAcceAbsorption.IsOpened():
						self.wndAcceAbsorption.Refresh(iAct)

				self.wndInventory.RefreshBagSlotWindow()

	if app.ENABLE_FISHING_GAME:
		def OpenFishingGameWindow(self, level):
			if self.wndFishingGame:
				self.wndFishingGame.Open(level)

		def CloseFishingGameWindow(self):
			if self.wndFishingGame:
				self.wndFishingGame.Close()

		def IsFishGameOpen(self):
			if self.wndFishingGame and self.wndFishingGame.IsShow():
				return True
			return False

	if app.ENABLE_FISHING_GAME_BDO:
		def OpenFishingBdoWindow(self, roundsTotal, hitsRequired):
			if self.wndFishingBdo:
				self.wndFishingBdo.Open(roundsTotal, hitsRequired)

		def RoundFishingBdoWindow(self, roundIndex, zoneStartPm, zoneWidthPm, travelMs):
			if self.wndFishingBdo:
				self.wndFishingBdo.StartRound(roundIndex, zoneStartPm, zoneWidthPm, travelMs)

		def ResultFishingBdoWindow(self, roundIndex, hit, hitsSoFar):
			if self.wndFishingBdo:
				self.wndFishingBdo.OnRoundResult(roundIndex, hit, hitsSoFar)

		def EndFishingBdoWindow(self, success, doubled):
			if self.wndFishingBdo:
				self.wndFishingBdo.OnGameEnd(success, doubled)

		def CloseFishingBdoWindow(self):
			if self.wndFishingBdo:
				self.wndFishingBdo.OnServerQuit()

		def IsFishingBdoOpen(self):
			if self.wndFishingBdo and self.wndFishingBdo.IsShow():
				return True
			return False

		def PressFishingBdo(self):
			if self.wndFishingBdo:
				self.wndFishingBdo.PressSpace()

	def OpenCubeWindow(self):
		self.wndCube.Open()

		if False == self.wndInventory.IsShow():
			self.wndInventory.Show()

	def UpdateCubeInfo(self, gold, itemVnum, count):
		self.wndCube.UpdateInfo(gold, itemVnum, count)

	def CloseCubeWindow(self):
		self.wndCube.Close()

	def FailedCubeWork(self):
		self.wndCube.Refresh()

	def SucceedCubeWork(self, itemVnum, count):
		self.wndCube.Clear()

		if 0:
			self.wndCubeResult.SetPosition(*self.wndCube.GetGlobalPosition())
			self.wndCubeResult.SetCubeResultItem(itemVnum, count)
			self.wndCubeResult.Open()
			self.wndCubeResult.SetTop()

	if app.ENABLE_12ZI:
		def OpenUI12zi(self, yellowmark, greenmark, yellowreward, greenreward, goldreward):
			if self.wnd12ziReward == None:
				self.wnd12ziReward = ui12zi.Reward12ziWindow()
			self.wnd12ziReward.Open(yellowmark, greenmark, yellowreward, greenreward, goldreward)

		def Refresh12ziTimer(self, currentFloor, jumpCount, limitTime, elapseTime):
			if self.wndMiniMap:
				self.wndMiniMap.Hide()

			if self.wnd12ziTimer == None:
				self.wnd12ziTimer = ui12zi.FloorLimitTimeWindow()

			self.wnd12ziTimer.Refresh12ziTimer(currentFloor, jumpCount, limitTime, elapseTime)
			self.wnd12ziTimer.Open()

		def Show12ziJumpButton(self):
			self.wnd12ziTimer.Show12ziJumpButton()

		def Hide12ziTimer(self):
			self.wnd12ziTimer.Hide()

		def RefreshShopItemToolTip(self):
			if self.tooltipItem:
				self.tooltipItem.RefreshShopToolTip()

	def __HideWindows(self):
		hideWindows = self.wndTaskBar,\
						self.wndExpandedMoneyTaskBar,\
						self.wndCharacter,\
						self.wndInventory,\
						self.wndMiniMap,\
						self.wndGuild,\
						self.wndMessenger,\
						self.wndChat,\
						self.yangText,\
						self.wndParty,\
						self.wndGameButton,

		if app.USE_LOG_EXCHANGE and self.wndExchangeLog:
			hideWindows += self.wndExchangeLog,

			if self.wndExchangeLog.wndExchangeView:
				hideWindows += self.wndExchangeLog.wndExchangeView,

		if app.USE_CRAFT_ITEM_SYSTEM and self.wnd_craft_item:
			hideWindows += self.wnd_craft_item,

		# if app.USE_NORTHWIND_DEEPS_DUNGEON:
		if self.wndUIDamage:
			self.wndUIDamage.Close()

		if app.USE_EVENT_MANAGER_EXPANDED and self.wndEventAlert:
			hideWindows += self.wndEventAlert,

		if self.wndMiniGame:
			hideWindows += self.wndMiniGame,

		if self.dlgSystem:
			hideWindows += self.dlgSystem,

		if self.wndEnergyBar:
			hideWindows += self.wndEnergyBar,

		if self.wndExpandedTaskBar:
			hideWindows += self.wndExpandedTaskBar,

		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			hideWindows += self.wndDragonSoul,\
						self.wndDragonSoulRefine,

		if app.ENABLE_PARTY_BOUNS:
			if self.wndPartyBonusWindow:
				hideWindows += self.wndPartyBonusWindow,

		if app.ENABLE_MYSHOP_DECO:
			if self.wndMyShopDeco:
				hideWindows += self.wndMyShopDeco,

		if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
			if self.wndSpecialInventory:
				hideWindows += self.wndSpecialInventory,

		if app.ENABLE_MINI_GAME_BNW:
			if self.wndBNWGame:
				hideWindows += self.wndBNWGame,

		if app.ENABLE_GROWTH_PET_SYSTEM:
			if self.wndPetInfoWindow:
				hideWindows += self.wndPetInfoWindow,
		
		if app.ENABLE_SWITCHBOT and self.wndSwitchbot:
			hideWindows += self.wndSwitchbot,

		if app.ENABLE_MAILBOX:
			if self.mail_box:
				hideWindows += self.mail_box,

		if app.ENABLE_12ZI:
			if self.wndBead:
				hideWindows += self.wndBead,
			if self.wnd12ziTimer:
				hideWindows += self.wnd12ziTimer,
			if self.wnd12ziReward:
				hideWindows += self.wnd12ziReward,

		if app.ENABLE_ANTI_MULTIPLE_FARM and self.wndAntiMultipleFarm:
			hideWindows += self.wndAntiMultipleFarm,
		
		if app.ENABLE_EXTENDED_BATTLE_PASS:
			if self.wndBattlePassExtended:
				hideWindows += self.wndBattlePassExtended,

		if app.ENABLE_ASLAN_TELEPORTPANEL:
			if self.wndTeleportPanel:
				hideWindows += self.wndTeleportPanel,

		if app.USE_DUNGEON_INFO:
			if self.wndDungeonInfo:
				hideWindows += self.wndDungeonInfo,

		if app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM:
			if self.wndSetCustomAttribute:
				hideWindows += self.wndSetCustomAttribute,
		
		if app.USE_PVP_TOURNAMENT:
			if self.wndPvpTournamentAdmin:
				hideWindows += self.wndPvpTournamentAdmin,
			
			if app.PVP_HAVE_GUI:
				if self.wndPvpTournamentFights:
					hideWindows += self.wndPvpTournamentFights,

		if app.ENABLE_ATTR_6TH_7TH:
			if self.wndAttr67Add:
				hideWindows += self.wndAttr67Add,

		if app.USE_ANTI_EXP and self.wndExpStatus:
			hideWindows += self.wndExpStatus,


		if app.USE_ITEM_ATTR_BACKUP_MODE and self.wndItemBackupAttr:
			hideWindows += self.wndItemBackupAttr,

		if app.USE_PORTABLE_TELEPORT_WITH_UI and self.teleportWnd:
			hideWindows += self.teleportWnd,

		hideWindows = filter(lambda x:x.IsShow(), hideWindows)
		map(lambda x:x.Hide(), hideWindows)
		import sys

		self.HideAllQuestButton()
		self.HideAllWhisperButton()

		if self.wndChat.IsEditMode():
			self.wndChat.CloseChat()

		if self.dlgSystem:
			self.dlgSystem.HideAllSystemOptioin()

		self.wndMiniMap.AtlasWindow.Hide()

		return hideWindows

	def __ShowWindows(self, wnds):
		import sys
		map(lambda x:x.Show(), wnds)
		global IsQBHide
		if not IsQBHide:
			self.ShowAllQuestButton()
		else:
			self.HideAllQuestButton()

		self.ShowAllWhisperButton()

		if self.dlgSystem:
			self.dlgSystem.ShowAllSystemOptioin()

		if self.wndMiniMap.AtlasWindow and self.wndMiniMap.AtlasWindow.IsShowWindow():
			self.wndMiniMap.AtlasWindow.Show()

	def BINARY_OpenAtlasWindow(self):
		if self.wndMiniMap:
			self.wndMiniMap.ShowAtlas()

	def BINARY_SetObserverMode(self, flag):
		self.wndGameButton.SetObserverMode(flag)

	# ACCESSORY_REFINE_ADD_METIN_STONE
	def BINARY_OpenSelectItemWindow(self):
		self.wndItemSelect.Open()
	# END_OF_ACCESSORY_REFINE_ADD_METIN_STONE

	if app.ENABLE_GEM_SYSTEM:
		def BINARY_OpenSelectItemWindowEx(self):
			self.wndItemSelectEx.Open()

		def BINARY_RefreshSelectItemWindowEx(self):
			self.wndItemSelectEx.RefreshSlot()

	#####################################################################################
	### Private Shop ###

	if app.ENABLE_MYSHOP_DECO:
		def OpenMyShopDecoWnd(self):
			if self.inputDialog:
				return

			if self.privateShopBuilder.IsShow():
				return

			if self.wndMyShopDeco:
				self.wndMyShopDeco.Open()
			else:
				return

	if app.ENABLE_CHEQUE_SYSTEM:
		def OpenPrivateShopInputNameDialog(self, bCashItem, tabCnt):
			if self.wndMyShopDeco.IsShow():
				return

			if app.ENABLE_GROWTH_PET_SYSTEM:
				pet_id = player.GetActivePetItemId()
				if pet_id:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_OPEN_SHOP_BECAUSE_SUMMON)
					return

			if app.USE_AURA_SYSTEM:
				if self.wndAura and self.wndAura.IsShow():
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_OPEN_OTHER_WINDOW)
					return

			if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
				if self.wndSkillBookCombination.IsShow():
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_NOTICE)
					return

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				shop.SetNameDialogOpen(True)
			inputDialog = uicommon.InputDialog()
			inputDialog.SetTitle(localeinfo.PRIVATE_SHOP_INPUT_NAME_DIALOG_TITLE)
			inputDialog.SetMaxLength(32)
			inputDialog.SetUseCodePage(False)
			inputDialog.SetAcceptEvent(lambda arg = bCashItem, arg1 = tabCnt : ui.__mem_func__(self.OpenPrivateShopBuilder)(arg, arg1))
			inputDialog.SetCancelEvent(ui.__mem_func__(self.ClosePrivateShopInputNameDialog))
			inputDialog.Open()
			self.inputDialog = inputDialog
	else:
		def OpenPrivateShopInputNameDialog(self):
			#if player.IsInSafeArea():
			#	chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.CANNOT_OPEN_PRIVATE_SHOP_IN_SAFE_AREA)
			#	return
			if app.ENABLE_GROWTH_PET_SYSTEM:
				pet_id = player.GetActivePetItemId()
				if pet_id:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_OPEN_SHOP_BECAUSE_SUMMON)
					return

			if app.USE_AURA_SYSTEM:
				if self.wndAura and self.wndAura.IsShow():
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_OPEN_OTHER_WINDOW)
					return

			if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
				if self.wndSkillBookCombination.IsShow():
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_NOTICE)
					return

			inputDialog = uicommon.InputDialog()
			inputDialog.SetTitle(localeinfo.PRIVATE_SHOP_INPUT_NAME_DIALOG_TITLE)
			inputDialog.SetMaxLength(32)
			inputDialog.SetAcceptEvent(ui.__mem_func__(self.OpenPrivateShopBuilder))
			inputDialog.SetCancelEvent(ui.__mem_func__(self.ClosePrivateShopInputNameDialog))
			inputDialog.Open()
			self.inputDialog = inputDialog

	def ClosePrivateShopInputNameDialog(self):
		self.inputDialog = None
		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			shop.SetNameDialogOpen(False)
		return True

	if app.ENABLE_CHEQUE_SYSTEM:
		def OpenPrivateShopBuilder(self, bCashItem, tabCnt):
			if not self.inputDialog:
				return True

			if not len(self.inputDialog.GetText()):
				return True

			if app.ENABLE_GROWTH_PET_SYSTEM:
				pet_id = player.GetActivePetItemId()
				if pet_id:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_OPEN_SHOP_BECAUSE_SUMMON)
					return

			if app.USE_AURA_SYSTEM:
				if self.wndAura and self.wndAura.IsShow():
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_OPEN_OTHER_WINDOW)
					return

			if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
				if self.wndSkillBookCombination.IsShow():
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_NOTICE)
					return

			self.privateShopBuilder.Open(self.inputDialog.GetText())
			self.privateShopBuilder.SetIsCashItem(bCashItem)
			self.privateShopBuilder.SetTabCount(tabCnt)
			self.ClosePrivateShopInputNameDialog()

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				shop.SetNameDialogOpen(True)

			return True
	else:
		def OpenPrivateShopBuilder(self):
			if not self.inputDialog:
				return True

			if not len(self.inputDialog.GetText()):
				return True
			if app.ENABLE_GROWTH_PET_SYSTEM:
				pet_id = player.GetActivePetItemId()
				if pet_id:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.PET_CAN_NOT_OPEN_SHOP_BECAUSE_SUMMON)
					return

			if app.USE_AURA_SYSTEM:
				if self.wndAura and self.wndAura.IsShow():
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.AURA_OPEN_OTHER_WINDOW)
					return

			if app.ENABLE_SKILLBOOK_COMB_SYSTEM:
				if self.wndSkillBookCombination.IsShow():
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.COMB_NOTICE)
					return

			self.privateShopBuilder.Open(self.inputDialog.GetText())
			self.ClosePrivateShopInputNameDialog()

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				shop.SetNameDialogOpen(True)

			return True

	def AppearPrivateShop(self, vid, text, type):
		board = None
		
		if type > 0:
			board = uiprivateshopbuilder.PrivateShopTitleBar(type)
		else:
			board = uiprivateshopbuilder.PrivateShopAdvertisementBoard()
			
		board.Open(vid, text)

		self.privateShopAdvertisementBoardDict[vid] = board

	def DisappearPrivateShop(self, vid):
		if not self.privateShopAdvertisementBoardDict.has_key(vid):
			return

		del self.privateShopAdvertisementBoardDict[vid]
		uiprivateshopbuilder.DeleteADBoard(vid)

	#####################################################################################
	### Equipment ###

	def OpenEquipmentDialog(self, vid):
		dlg = uiequipmentdialog.EquipmentDialog()
		dlg.SetItemToolTip(self.tooltipItem)
		dlg.SetCloseEvent(ui.__mem_func__(self.CloseEquipmentDialog))
		dlg.Open(vid)

		self.equipmentDialogDict[vid] = dlg

	if app.ENABLE_CHANGE_LOOK_SYSTEM:
		def SetEquipmentDialogItem(self, vid, slotIndex, vnum, count, dwChangeLookVnum):
			if not vid in self.equipmentDialogDict:
				return
			self.equipmentDialogDict[vid].SetEquipmentDialogItem(slotIndex, vnum, count, dwChangeLookVnum)
	else:
		def SetEquipmentDialogItem(self, vid, slotIndex, vnum, count):
			if not vid in self.equipmentDialogDict:
				return
			self.equipmentDialogDict[vid].SetEquipmentDialogItem(slotIndex, vnum, count)

	def SetEquipmentDialogSocket(self, vid, slotIndex, socketIndex, value):
		if not vid in self.equipmentDialogDict:
			return
		self.equipmentDialogDict[vid].SetEquipmentDialogSocket(slotIndex, socketIndex, value)

	def SetEquipmentDialogAttr(self, vid, slotIndex, attrIndex, type, value):
		if not vid in self.equipmentDialogDict:
			return
		self.equipmentDialogDict[vid].SetEquipmentDialogAttr(slotIndex, attrIndex, type, value)

	def CloseEquipmentDialog(self, vid):
		if not vid in self.equipmentDialogDict:
			return
		del self.equipmentDialogDict[vid]

	#####################################################################################

	#####################################################################################
	### Quest ###

	def BINARY_ClearQuest(self, index):
		btn = self.__FindQuestButton(index)
		if 0 != btn:
			self.__DestroyQuestButton(btn)

	def RecvQuest(self, index, name):
		# QUEST_LETTER_IMAGE
		self.BINARY_RecvQuest(index, name, "file", localeinfo.GetLetterImageName())
		# END_OF_QUEST_LETTER_IMAGE

	def BINARY_RecvQuest(self, index, name, iconType, iconName):
		btn = self.__FindQuestButton(index)
		if 0 != btn:
			self.__DestroyQuestButton(btn)

		btn = uiwhisper.WhisperButton()

		# QUEST_LETTER_IMAGE
		import item

		if "item" == iconType:
			item.SelectItem(int(iconName))
			buttonImageFileName = item.GetIconImageFileName()
		elif "blue_quest" == iconType or name[0] == "*":
			buttonImageFileName = localeinfo.GetBlueLetterImageName()
		else:
			buttonImageFileName = iconName

		if localeinfo.IsEUROPE():
			if name[0] == "*":
				btn.SetUpVisual(localeinfo.GetBlueLetterImageName())
				btn.SetOverVisual(localeinfo.GetBlueLetterOpenImageName())
				btn.SetDownVisual(localeinfo.GetBlueLetterCloseImageName())
				name = name[1:]
			else:
				if "highlight" == iconType:
					btn.SetUpVisual("locale/ymir_ui/highlighted_quest.tga")
					btn.SetOverVisual("locale/ymir_ui/highlighted_quest_r.tga")
					btn.SetDownVisual("locale/ymir_ui/highlighted_quest_r.tga")
				else:
					btn.SetUpVisual(localeinfo.GetLetterCloseImageName())
					btn.SetOverVisual(localeinfo.GetLetterOpenImageName())
					btn.SetDownVisual(localeinfo.GetLetterOpenImageName())
		else:
			btn.SetUpVisual(buttonImageFileName)
			btn.SetOverVisual(buttonImageFileName)
			btn.SetDownVisual(buttonImageFileName)
			btn.Flash()
		# END_OF_QUEST_LETTER_IMAGE

		# if localeinfo.IsARABIC():
			# btn.SetToolTipText(name, -20, 35)
			# btn.ToolTipText.SetHorizontalAlignRight()
		# else:
			# btn.SetToolTipText(name, -20, 35)
			# btn.ToolTipText.SetHorizontalAlignLeft()

		# btn.SetEvent(ui.__mem_func__(self.__StartQuest), btn)
		# btn.Show()
		
		if not app.ENABLE_QUEST_RENEWAL:
			if localeinfo.IsARABIC():
				btn.SetToolTipText(name, -20, 35)
				btn.ToolTipText.SetHorizontalAlignRight()
			else:
				btn.SetToolTipText(name, -20, 35)
				btn.ToolTipText.SetHorizontalAlignLeft()

			btn.SetEvent(ui.__mem_func__(self.__StartQuest), btn)
			btn.Show()
		else:
			btn.SetEvent(ui.__mem_func__(self.__StartQuest), btn)

		btn.index = index
		btn.name = name

		self.questButtonList.insert(0, btn)
		self.__ArrangeQuestButton()

		#chat.AppendChat(chat.CHAT_TYPE_NOTICE, localeinfo.QUEST_APPEND)

	def __ArrangeQuestButton(self):
		screenWidth = wndMgr.GetScreenWidth()
		screenHeight = wndMgr.GetScreenHeight()

		if self.wndParty.IsShow():
			xPos = 100 + 30
		else:
			xPos = 20

		if localeinfo.IsARABIC():
			xPos = xPos + 15

		yPos = 170 * screenHeight / 600
		yCount = (screenHeight - 330) / 63

		count = 0
		for btn in self.questButtonList:
			if app.ENABLE_QUEST_RENEWAL:
				btn.SetToolTipText(str(len(self.questButtonList)))
				btn.ToolTipText.SetHorizontalAlignCenter()

			btn.SetPosition(xPos + (int(count/yCount) * 100), yPos + (count%yCount * 63))
			count += 1

			global IsQBHide
			if IsQBHide:
				btn.Hide()
			else:
				if app.ENABLE_QUEST_RENEWAL and count > 0:
					btn.Hide()
				else:
					btn.Show()

	def __StartQuest(self, btn):
		if app.ENABLE_QUEST_RENEWAL:
			self.__OnClickQuestButton()
			self.HideAllQuestButton()
		else:
			event.QuestButtonClick(btn.index)
			self.__DestroyQuestButton(btn)

	def __FindQuestButton(self, index):
		for btn in self.questButtonList:
			if btn.index == index:
				return btn

		return 0

	def __DestroyQuestButton(self, btn):
		btn.SetEvent(0)
		self.questButtonList.remove(btn)
		self.__ArrangeQuestButton()

	def HideAllQuestButton(self):
		for btn in self.questButtonList:
			btn.Hide()

	def ShowAllQuestButton(self):
		for btn in self.questButtonList:
			btn.Show()
			if app.ENABLE_QUEST_RENEWAL:
				break

	#####################################################################################

	#####################################################################################
	### Whisper ###

	def __InitWhisper(self):
		#chat.InitWhisper(self)
		if constinfo.WHISPER_CHAT_WINDOW:
			# the engine whisper map accumulates every name for the whole session
			# and would resurrect deleted conversations on each interface rebuild;
			# rebuild buttons from the messagescache unread state instead
			for name, unread in uiwhisperchat.ListRestoreButtons():
				if 0 == self.__FindWhisperButton(name):
					btn = self.__MakeWhisperButton(name)
					if unread:
						btn.Flash()
			return
		chat.InitWhisper(proxy(self))

	def __GetWhisperChatWindow(self):
		if not self.wndWhisperChat:
			self.wndWhisperChat = uiwhisperchat.WhisperChatWindow()
			self.wndWhisperChat.BindInterface(self)
			self.wndWhisperChat.SetGuildButtonEvent(ui.__mem_func__(self.ToggleGuildWindow))
		return self.wndWhisperChat

	def OnMessengerLastOnline(self, name, timestamp):
		if getattr(self, "wndWhisperChat", None):
			self.wndWhisperChat.OnLastOnline(name, timestamp)

	def __OpenWhisperChatConversation(self, name):
		wnd = self.__GetWhisperChatWindow()
		wnd.Show()
		wnd.SetTop()
		wnd.OpenConversation(name)
		btn = self.__FindWhisperButton(name)
		if 0 != btn:
			self.__DestroyWhisperButton(btn)

	def OpenWhisperDialogWithoutTarget(self):
		if constinfo.WHISPER_CHAT_WINDOW:
			wnd = self.__GetWhisperChatWindow()
			wnd.Show()
			wnd.SetTop()
			wnd.OpenNewConversationDialog()
			return

		if not self.dlgWhisperWithoutTarget:
			dlgWhisper = uiwhisper.WhisperDialog(self.MinimizeWhisperDialog, self.CloseWhisperDialog)
			dlgWhisper.BindInterface(self)
			dlgWhisper.LoadDialog()
			dlgWhisper.OpenWithoutTarget(self.RegisterTemporaryWhisperDialog)
			dlgWhisper.SetPosition(self.windowOpenPosition * 30,self.windowOpenPosition * 30)
			dlgWhisper.Show()
			self.dlgWhisperWithoutTarget = dlgWhisper

			self.windowOpenPosition = (self.windowOpenPosition + 1) % 5

		else:
			self.dlgWhisperWithoutTarget.SetTop()
			self.dlgWhisperWithoutTarget.OpenWithoutTarget(self.RegisterTemporaryWhisperDialog)

	def RegisterTemporaryWhisperDialog(self, name):
		if not self.dlgWhisperWithoutTarget:
			return

		btn = self.__FindWhisperButton(name)
		if 0 != btn:
			self.__DestroyWhisperButton(btn)

		elif self.whisperDialogDict.has_key(name):
			oldDialog = self.whisperDialogDict[name]
			oldDialog.Destroy()
			del self.whisperDialogDict[name]

		self.whisperDialogDict[name] = self.dlgWhisperWithoutTarget
		self.dlgWhisperWithoutTarget.OpenWithTarget(name)
		self.dlgWhisperWithoutTarget = None
		self.__CheckGameMaster(name)

	def RecieveWhisperDetails(self, name, country):
		if self.whisperDialogDict.has_key(name):
			self.whisperDialogDict[name].SetCountryFlag(country)
		else:
			btn = self.__FindWhisperButton(name)
			if btn != 0:
				btn.countryID = country

	def OpenWhisperDialog(self, name):
		if constinfo.WHISPER_CHAT_WINDOW:
			self.__OpenWhisperChatConversation(name)
			return

		if not self.whisperDialogDict.has_key(name):
			dlg = self.__MakeWhisperDialog(name)
			dlg.OpenWithTarget(name)
			dlg.chatLine.SetFocus()
			dlg.Show()

			self.__CheckGameMaster(name)
			btn = self.__FindWhisperButton(name)
			if 0 != btn:
				self.__DestroyWhisperButton(btn)

	def OpenPvmBalanceIntro(self):
		if not getattr(self, "wndPvmBalanceIntro", None):
			self.wndPvmBalanceIntro = uipvmbalanceintro.PvmBalanceIntroDialog()
		self.wndPvmBalanceIntro.SetSkillToolTip(getattr(self, "tooltipSkill", None))
		self.wndPvmBalanceIntro.Open()

	def ClosePvmBalanceIntro(self):
		if getattr(self, "wndPvmBalanceIntro", None):
			self.wndPvmBalanceIntro.Close()

	def BundleBoxFeed(self, payload):
		if getattr(self, "wndBundleBox", None):
			self.wndBundleBox.Feed(payload)

	def BundleBoxDone(self):
		if getattr(self, "wndBundleBox", None):
			self.wndBundleBox.OnDone()

	def RecvWhisper(self, name, fromLiveChat=False):
		if constinfo.WHISPER_CHAT_WINDOW:
			if self.wndWhisperChat:
				self.wndWhisperChat.NotifyWhisper(name, fromLiveChat)
			if not (self.wndWhisperChat and self.wndWhisperChat.IsShow() and self.wndWhisperChat.GetActiveConversation() == name):
				btn = self.__FindWhisperButton(name)
				if 0 == btn:
					btn = self.__MakeWhisperButton(name)
					btn.Flash()
					app.FlashApplication()
					chat.AppendChat(chat.CHAT_TYPE_NOTICE, localeinfo.RECEIVE_MESSAGE % (name))
				else:
					btn.Flash()
			return

		if not self.whisperDialogDict.has_key(name):
			btn = self.__FindWhisperButton(name)
			if 0 == btn:
				btn = self.__MakeWhisperButton(name)
				btn.Flash()
				app.FlashApplication() #osp. flash application
				chat.AppendChat(chat.CHAT_TYPE_NOTICE, localeinfo.RECEIVE_MESSAGE % (name))
			else:
				btn.Flash()
		elif self.IsGameMasterName(name):
			dlg = self.whisperDialogDict[name]
			dlg.SetGameMasterLook()

	def MakeWhisperButton(self, name):
		if 0 != self.__FindWhisperButton(name):
			return
		self.__MakeWhisperButton(name)

	def DestroyWhisperButtonByName(self, name):
		btn = self.__FindWhisperButton(name)
		if 0 != btn:
			self.__DestroyWhisperButton(btn)

	def DismissWhisperButton(self, btn):
		uiwhisperchat.ClearMinimizedConversation(btn.name)
		self.__DestroyWhisperButton(btn)

	if app.BL_REMOTE_SHOP:
		def OpenRemoteShop(self):
			if self.wndRemoteShop:
				if self.wndRemoteShop.IsShowWindow():
					self.wndRemoteShop.Close()
				else:
					self.wndRemoteShop.Show()

	if app.USE_OFFLINESHOP:
		def OpenOfflineShop(self):
			if self.wndShopOffline:
				if self.wndShopOffline.IsShow():
					self.wndShopOffline.Close()
				else:
					if app.USE_PVP_TOURNAMENT:
						import chr
						if chr.GetMapIndex() == pvp_tournament.MAP_INDEX:
							return

					self.wndShopOffline.Open()

	def ShowWhisperDialog(self, btn):
		if constinfo.WHISPER_CHAT_WINDOW:
			self.__OpenWhisperChatConversation(btn.name)
			return

		try:
			self.__MakeWhisperDialog(btn.name)
			dlgWhisper = self.whisperDialogDict[btn.name]
			dlgWhisper.OpenWithTarget(btn.name)
			dlgWhisper.Show()
			self.__CheckGameMaster(btn.name)
		except:
			import dbg
			dbg.TraceError("interface.ShowWhisperDialog - Failed to find key")

		self.__DestroyWhisperButton(btn)

	def MinimizeWhisperDialog(self, name):
		if 0 != name:
			self.__MakeWhisperButton(name)

		self.CloseWhisperDialog(name)

	def CloseWhisperDialog(self, name):
		if 0 == name:
			if self.dlgWhisperWithoutTarget:
				self.dlgWhisperWithoutTarget.Destroy()
				self.dlgWhisperWithoutTarget = None

			return

		try:
			dlgWhisper = self.whisperDialogDict[name]
			dlgWhisper.Destroy()
			del self.whisperDialogDict[name]
		except:
			import dbg
			dbg.TraceError("interface.CloseWhisperDialog - Failed to find key")

	def __ArrangeWhisperButton(self):
		screenWidth = wndMgr.GetScreenWidth()
		screenHeight = wndMgr.GetScreenHeight()

		xPos = screenWidth - 70
		yPos = 170 * screenHeight / 600
		yCount = (screenHeight - 330) / 63
		#yCount = (screenHeight - 285) / 63
		if app.ENABLE_RTT_STATISTICS:
			yPos += 30

		count = 0
		for button in self.whisperButtonList:

			button.SetPosition(xPos + (int(count/yCount) * -50), yPos + (count%yCount * 63))
			count += 1

	def __FindWhisperButton(self, name):
		for button in self.whisperButtonList:
			if button.name == name:
				return button

		return 0

	def __MakeWhisperDialog(self, name):
		dlgWhisper = uiwhisper.WhisperDialog(self.MinimizeWhisperDialog, self.CloseWhisperDialog)
		dlgWhisper.BindInterface(self)
		dlgWhisper.LoadDialog()
		dlgWhisper.SetPosition(self.windowOpenPosition*30,self.windowOpenPosition*30)
		self.whisperDialogDict[name] = dlgWhisper

		self.windowOpenPosition = (self.windowOpenPosition+1) % 5

		return dlgWhisper

	def __MakeWhisperButton(self, name):
		whisperButton = uiwhisper.WhisperButton()
		whisperButton.SetUpVisual("d:/ymir work/ui/game/windows/btn_mail_up.sub")
		whisperButton.SetOverVisual("d:/ymir work/ui/game/windows/btn_mail_up.sub")
		whisperButton.SetDownVisual("d:/ymir work/ui/game/windows/btn_mail_up.sub")
		if self.IsGameMasterName(name):
			whisperButton.SetToolTipTextWithColor(name, 0xffffa200)
		else:
			whisperButton.SetToolTipText(name)
		whisperButton.ToolTipText.SetHorizontalAlignCenter()
		whisperButton.SetEvent(ui.__mem_func__(self.ShowWhisperDialog), whisperButton)
		if constinfo.WHISPER_CHAT_WINDOW:
			whisperButton.SetDismissEvent(ui.__mem_func__(self.DismissWhisperButton))
		whisperButton.Show()
		whisperButton.name = name

		self.whisperButtonList.insert(0, whisperButton)
		self.__ArrangeWhisperButton()

		return whisperButton

	def __DestroyWhisperButton(self, button):
		button.SetEvent(0)
		self.whisperButtonList.remove(button)
		self.__ArrangeWhisperButton()

	def HideAllWhisperButton(self):
		for btn in self.whisperButtonList:
			btn.Hide()

	def ShowAllWhisperButton(self):
		for btn in self.whisperButtonList:
			btn.Show()

	def MakeDungeonTimerWindow(self):
		import uidungeontimer
		self.wndDungeonTimer = uidungeontimer.Cooldown()
		self.wndDungeonTimer.Hide()

	def __CheckGameMaster(self, name):
		if not self.listGMName.has_key(name):
			return
		if self.whisperDialogDict.has_key(name):
			dlg = self.whisperDialogDict[name]
			dlg.SetGameMasterLook()

	def RegisterGameMasterName(self, name):
		if self.listGMName.has_key(name):
			return
		self.listGMName[name] = "GM"

	def IsGameMasterName(self, name):
		if self.listGMName.has_key(name):
			return True
		else:
			return False

	#####################################################################################

	#####################################################################################
	### Guild Building ###

	def BUILD_OpenWindow(self):
		self.wndGuildBuilding = uiguild.BuildGuildBuildingWindow()
		self.wndGuildBuilding.Open()
		self.wndGuildBuilding.wnds = self.__HideWindows()
		self.wndGuildBuilding.SetCloseEvent(ui.__mem_func__(self.BUILD_CloseWindow))

	def BUILD_CloseWindow(self):
		self.__ShowWindows(self.wndGuildBuilding.wnds)
		self.wndGuildBuilding = None

	def BUILD_OnUpdate(self):
		if app.USE_DUNGEON_COOLDOWN_MANAGER:
			if not self.dungeonCooldownAlert:
				self.dungeonCooldownAlert = uidungeoninfo.CooldownAlert(self)

			self.dungeonCooldownAlert.Update()

		if app.USE_EVENT_MANAGER_EXPANDED and self.wndEventAlert:
			self.wndEventAlert.CheckDayRefresh()

		if not self.wndGuildBuilding:
			return

		if self.wndGuildBuilding.IsPositioningMode():
			import background
			x, y, z = background.GetPickingPoint()
			self.wndGuildBuilding.SetBuildingPosition(x, y, z)

	def BUILD_OnMouseLeftButtonDown(self):
		if not self.wndGuildBuilding:
			return

		# GUILD_BUILDING
		if self.wndGuildBuilding.IsPositioningMode():
			self.wndGuildBuilding.SettleCurrentPosition()
			return True
		elif self.wndGuildBuilding.IsPreviewMode():
			pass
		else:
			return True
		# END_OF_GUILD_BUILDING
		return False

	def BUILD_OnMouseLeftButtonUp(self):
		if not self.wndGuildBuilding:
			return False
		
		if not self.wndGuildBuilding.IsPreviewMode():
			return True
		
		return False

	def BULID_EnterGuildArea(self, areaID):
		# GUILD_BUILDING
		mainCharacterName = player.GetMainCharacterName()
		masterName = guild.GetGuildMasterName()

		if mainCharacterName != masterName:
			return

		if areaID != player.GetGuildID():
			return
		# END_OF_GUILD_BUILDING

		self.wndGameButton.ShowBuildButton()

	def BULID_ExitGuildArea(self, areaID):
		self.wndGameButton.HideBuildButton()

	#####################################################################################

	def IsEditLineFocus(self):
		if self.ChatWindow.chatLine.IsFocus():
			return 1

		if self.ChatWindow.chatToLine.IsFocus():
			return 1

		return 0

	def EmptyFunction(self):
		pass

	if app.QUICK_SELL_SYSTEM:
		def IsShowQuickSell(self):
			return self.wndQuickSell and self.wndQuickSell.IsShow()

		def ToggleQuickSellSlot(self, windowType, slotIndex):
			if not self.wndQuickSell:
				return False

			wasShown = self.wndQuickSell.IsShow()
			result = self.wndQuickSell.Toggle(windowType, slotIndex)

			if not wasShown and self.wndQuickSell.IsShow():
				self.AdjustQuickSell()

			return result

		# docks the cart to the left of whichever bag the player is working in
		def AdjustQuickSell(self):
			anchors = self.__GetQuickSellBagWindows()
			if not anchors:
				self.wndQuickSell.SetCenterPosition()
				return

			x, y = anchors[0].GetGlobalPosition()
			self.wndQuickSell.SetPosition(max(0, x - self.wndQuickSell.GetWidth() - 5), y)

		def __GetQuickSellBagWindows(self):
			windows = []

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM and self.wndSpecialInventory and self.wndSpecialInventory.IsShow():
				windows.append(self.wndSpecialInventory)

			if app.ENABLE_DRAGON_SOUL_SYSTEM and self.wndDragonSoul and self.wndDragonSoul.IsShow():
				windows.append(self.wndDragonSoul)

			if self.wndInventory and self.wndInventory.IsShow():
				windows.append(self.wndInventory)

			return windows

		def RefreshQuickSellMarks(self):
			if self.wndInventory:
				self.wndInventory.RefreshBagSlotWindow()

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM and self.wndSpecialInventory:
				self.wndSpecialInventory.RefreshBagSlotWindow()

			if app.ENABLE_DRAGON_SOUL_SYSTEM and self.wndDragonSoul:
				self.wndDragonSoul.RefreshBagSlotWindow()

		def OnQuickSellResult(self, sold, rejected, gold):
			if self.wndQuickSell:
				self.wndQuickSell.OnSellResult(sold, rejected, gold)

	if app.ENABLE_SKILL_LEARN_SYSTEM:
		def OpenLearnSkillWindow(self):
			if self.wndLearnSkill.IsShow():
				self.wndLearnSkill.Close()
			else:
				self.wndLearnSkill.Open()

	if app.ENABLE_MINI_GAME_OKEY:
		def MiniGameOkey(self):
			if osfinfo.BETA_PVP == True:
				try:
					self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					self.wndPopupDialog.Open()
				except:
					self.wndPopupDialog = uicommon.PopupDialog()
					self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					self.wndPopupDialog.Open()
				return

			isOpen = osfinfo.RUMI_GAME_EVENT

			if isOpen == True:
				if not self.wndMiniGame:
					self.wndMiniGame = uiminigame.MiniGameWindow()

				self.wndMiniGame.MiniGameOkeyEvent(True)
			else:
				if self.wndMiniGame:
					self.wndMiniGame.MiniGameOkeyEvent(False)

	if app.ENABLE_MINI_GAME_BNW:
		def SetBNWEventStatus(self, isEnable):
			if isEnable:
				osfinfo.BNW_GAME_EVENT = True
			else:
				osfinfo.BNW_GAME_EVENT = False

		def MiniGameBNWStart(self):
			if self.wndMiniGame:
				self.wndMiniGame.MiniGameBNWStart()

		def MiniGameBNWCompare(self, winIndex, playerCard, opponentCard, myScore):
			if self.wndMiniGame:
				self.wndMiniGame.MiniGameBNWCompare(winIndex, playerCard, opponentCard, myScore)

		def MiniGameBNWAddRanking(self, position, isMain, name, donations):
			if self.wndMiniGame:
				self.wndMiniGame.MiniGameBNWAddRanking(position, isMain, name, donations)

		def MiniGameBNWClearRanking(self):
			if self.wndMiniGame:
				self.wndMiniGame.MiniGameBNWClearRanking()

		def MiniGameBNWOpenRanking(self):
			if self.wndMiniGame:
				self.wndMiniGame.MiniGameBNWOpenRanking()

		def MiniGameBNWUpdateRanking(self):
			if self.wndMiniGame:
				self.wndMiniGame.MiniGameBNWUpdateRanking()

		def ClickBNWEventButton(self):
			if self.wndMiniGame:
				self.wndMiniGame.ClickBNWEventButton()


	if app.ENABLE_MINI_GAME_CATCH_KING:
		def SetCatchKingEventStatus(self, isEnable):
			if isEnable:
				osfinfo.CATCH_KING_GAME_EVENT = True
			else:
				osfinfo.CATCH_KING_GAME_EVENT = False

		def MiniGameCatchKingEventStart(self, bigScore):
			if osfinfo.BETA_PVP == True:
				try:
					self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					self.wndPopupDialog.Open()
				except:
					self.wndPopupDialog = uicommon.PopupDialog()
					self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					self.wndPopupDialog.Open()
				return

			if self.wndMiniGame:
				self.wndMiniGame.MiniGameCatchKingEventStart(bigScore)

		def MiniGameCatchKingSetHandCard(self, cardNumber):
			if self.wndMiniGame:
				self.wndMiniGame.MiniGameCatchKingSetHandCard(cardNumber)

		def MiniGameCatchKingResultField(self, score, rowType, cardPos, cardValue, keepFieldCard, destroyHandCard, getReward, isFiveNear):
			if self.wndMiniGame:
				self.wndMiniGame.MiniGameCatchKingResultField(score, rowType, cardPos, cardValue, keepFieldCard, destroyHandCard, getReward, isFiveNear)

		def MiniGameCatchKingSetEndCard(self, cardPos, cardNumber):
			if self.wndMiniGame:
				self.wndMiniGame.MiniGameCatchKingSetEndCard(cardPos, cardNumber)

		def MiniGameCatchKingReward(self, rewardCode):
			if self.wndMiniGame:
				self.wndMiniGame.MiniGameCatchKingReward(rewardCode)

	def IntegrationEventBanner(self):
		isOpen = []

		if app.ENABLE_MINI_GAME_OKEY:
			isOpen.append(osfinfo.RUMI_GAME_EVENT)

		if app.ENABLE_MINI_GAME_CATCH_KING:
			isOpen.append(osfinfo.CATCH_KING_GAME_EVENT)

		if app.ENABLE_MINI_GAME_BNW:
			isOpen.append(osfinfo.BNW_GAME_EVENT)

		if app.USE_BL_FISH_EVENT:
			isOpen.append(True)

		if True in isOpen:
			if not self.wndMiniGame:
				self.wndMiniGame = uiminigame.MiniGameWindow()

				if self.tooltipItem:
					self.wndMiniGame.SetItemToolTip(self.tooltipItem)

			self.wndMiniGame.IntegrationMiniGame(True)
		else:
			if self.wndMiniGame:
				self.wndMiniGame.IntegrationMiniGame(False)

	if app.WJ_ENABLE_TRADABLE_ICON:
		def AttachInvenItemToOtherWindowSlot(self, slotIndex):
			#if app.ENABLE_MOVE_COSTUME_ATTR:
			#	if self.GetOnTopWindow() == player.ON_TOP_WND_ITEM_COMB and self.wndItemCombination and self.wndItemCombination.IsShow():
			#		self.wndItemCombination.AttachToCombinationSlot(player.INVENTORY, slotIndex)
			#		return True

			return False

		def MarkUnusableInvenSlotOnTopWnd(self, onTopWnd, InvenSlot):
			if app.WJ_ENABLE_TRADABLE_ICON:
				if onTopWnd == player.ON_TOP_WND_SHOP and self.dlgShop and self.dlgShop.CantSellInvenItem(InvenSlot):
					return True
				elif onTopWnd == player.ON_TOP_WND_SAFEBOX and self.wndSafebox and self.wndSafebox.CantCheckInItem(InvenSlot):
					return True
				elif onTopWnd == player.ON_TOP_WND_PRIVATE_SHOP and self.privateShopBuilder and self.privateShopBuilder.CantTradableItem(InvenSlot):
					return True
				elif onTopWnd == player.ON_TOP_WND_EXCHANGE and self.dlgExchange and self.dlgExchange.CantTradableItem(InvenSlot):
					return True

				elif onTopWnd == player.ON_TOP_WND_PET_FEED and self.wndPetInfoWindow and self.wndPetInfoWindow.CantFeedItem(InvenSlot):
					return True
				elif onTopWnd == player.ON_TOP_WND_PET_ATTR_CHANGE and self.wndPetInfoWindow and self.wndPetInfoWindow.CantAttrChangeItem(InvenSlot):
					return True
				elif onTopWnd == player.ON_TOP_WND_MAILBOX and self.mail_box and self.mail_box.CantPostItemSlot(InvenSlot):
					return True
				elif onTopWnd == player.ON_TOP_WND_PET_PRIMIUM_FEEDSTUFF and self.wndPetInfoWindow and self.wndPetInfoWindow.CantPremiumFeedItem(InvenSlot):
					return True
				elif onTopWnd == player.ON_TOP_WND_ATTR67 and self.wndAttr67Add and self.wndAttr67Add.CantAttachToAttrSlot(InvenSlot):
					return True

				if app.USE_OFFLINESHOP:
					if uiofflineshop_ae.IsBuildingShop():
						if uiofflineshop_ae.IsSaleSlot(player.INVENTORY, InvenSlot):
							return True
					
					if uiofflineshop_ae.IsBuildingShop():
						Index = player.GetItemIndex(player.INVENTORY, InvenSlot)
						if Index != 0:
							item.SelectItem(Index)
							if item.IsAntiFlag(item.ANTIFLAG_GIVE) or item.IsAntiFlag(item.ANTIFLAG_MYSHOP):
								return True

			return False

		if app.ENABLE_MAILBOX:
			def MarkUnusableDSInvenSlotOnTopWnd(self, onTopWnd, index):
				if onTopWnd == player.ON_TOP_WND_MAILBOX and self.mail_box and self.mail_box.CantPostItemSlot(index, player.DRAGON_SOUL_INVENTORY):
					return True

				return False

		def SetOnTopWindow(self, onTopWnd):
			self.OnTopWindow = onTopWnd

		def GetOnTopWindow(self):
			return self.OnTopWindow

		def RefreshMarkInventoryBag(self):
			if self.wndInventory and self.wndInventory.IsShow():
				self.wndInventory.RefreshBagSlotWindow()

			if app.ENABLE_MAILBOX:
				if self.wndDragonSoul and self.wndDragonSoul.IsShow():
					self.wndDragonSoul.RefreshBagSlotWindow()

			if app.ENABLE_SPECIAL_INVENTORY_SYSTEM:
				if self.wndSpecialInventory and self.wndSpecialInventory.IsShow():
					self.wndSpecialInventory.RefreshBagSlotWindow()

	if app.ENABLE_HIDE_COSTUME_SYSTEM:
		def RefreshVisibleCostume(self):
			self.wndInventory.RefreshVisibleCostume()

	if app.ENABLE_HIDE_SHINING_SYSTEM:
		def RefreshVisibleShining(self):
			self.wndInventory.RefreshVisibleShining()

	if app.__PENDANT__:
		def SetPendantPageIdx(self, pageIdx, secondOpened):
			self.wndInventory.SetPendantPageIdx(int(pageIdx), int(secondOpened))


	if app.__SKILL_TREE__:
		def MakeOpenSkillTree(self):
			if self.wndSkillTree == None:
				self.wndSkillTree = uiSkillTree.SkillTreeWindow()
		def OpenSkillTree(self):
			self.MakeOpenSkillTree()
			if self.wndSkillTree.IsShow():
				self.wndSkillTree.Close()
			else:
				self.wndSkillTree.Open()
		def SkillTreeLoad(self, skillData, leftTime, isActive):
			self.MakeOpenSkillTree()
			self.wndSkillTree.SkillTreeLoad(str(skillData), int(leftTime), int(isActive))
		def SkillTreeSetTime(self, leftTime):
			if self.wndSkillTree:
				self.wndSkillTree.SkillTreeSetTime(int(leftTime))
		def SkillTreeSetLevel(self, skillIdx, newLevel):
			if self.wndSkillTree:
				self.wndSkillTree.SkillTreeSetLevel(int(skillIdx), int(newLevel))
		def SkillTreeSetStatus(self, newStatus, leftTime):
			self.MakeOpenSkillTree()
			self.wndSkillTree.SkillTreeSetStatus(newStatus, int(leftTime))

			if self.wndMiniMap:
				btn = self.wndMiniMap.GetChild("TreeShowButton") if self.wndMiniMap.IsChild("TreeShowButton") else None
				if btn:
					btn.SetUpVisual(("d:/ymir work/ui/new_minimap/skilltree_inactive_default.png" if not newStatus else "d:/ymir work/ui/new_minimap/skilltree_active_default_a.png"))
					btn.SetOverVisual(("d:/ymir work/ui/new_minimap/skilltree_inactive_hover.png" if not newStatus else "d:/ymir work/ui/new_minimap/skilltree_active_hover_a.png"))
					btn.SetDownVisual(("d:/ymir work/ui/new_minimap/skilltree_inactive_down.png" if not newStatus else "d:/ymir work/ui/new_minimap/skilltree_active_down_a.png"))

	if app.ENABLE_EXPRESSING_EMOTION:
		def ClearSpecialEmotions(self):
			if self.wndCharacter:
				self.wndCharacter.ClearSpecialEmotions()

		def RegisterSpecialEmotions(self, emotionIdx, leftTime):
			if self.wndCharacter:
				self.wndCharacter.RegisterSpecialEmotions(emotionIdx, leftTime)

	if app.ENABLE_DSS_ACTIVE_EFFECT_BUTTON:
		def UseDSSButtonEffect(self, enable):
			if self.wndInventory:
				self.wndInventory.UseDSSButtonEffect(enable)

	if app.ENABLE_MAILBOX:
		def MailBoxProcess(self, type, data):
			if not self.mail_box:
				return

			self.mail_box.MailBoxProcess(type, data)

		def MiniMapMailProcess(self, type, data):
			if not self.wndMiniMap:
				return

			self.wndMiniMap.MiniMapMailProcess(type, data)

	if app.ENABLE_GROWTH_PET_SYSTEM:
		def PetHatchingWindowCommand(self, command):
			if self.wndPetInfoWindow:
				if self.wndPetInfoWindow.wndPetHatching:
					self.wndPetInfoWindow.wndPetHatching.PetHatchingWindowCommand(command)
		
		def PetNameChangeWindowCommand(self, command):
			if self.wndPetInfoWindow:
				if self.wndPetInfoWindow.wndPetNameChange:
					self.wndPetInfoWindow.wndPetNameChange.PetNameChangeWindowCommand(command)

		def PetSkillUpgradeDlgOpen(self, slot, index, gold):
			if self.wndPetInfoWindow:
				self.wndPetInfoWindow.OpenPetSkillUpGradeQuestionDialog(slot, index, gold)

		def PetFlashEvent(self, index):
			if self.wndPetInfoWindow:
				self.wndPetInfoWindow.PetFlashEvent(index)

		def PetInfoBindAffectShower(self, affect_shower):
			if self.wndPetInfoWindow:
				self.wndPetInfoWindow.PetInfoBindAffectShower(affect_shower)

		def PetAffectShowerRefresh(self):
			if self.wndPetInfoWindow:
				self.wndPetInfoWindow.PetAffectShowerRefresh()

		def PetFeedReuslt(self, result):
			if self.wndPetInfoWindow:
				self.wndPetInfoWindow.PetFeedReuslt(result)
				
		def PetAttrDetermineResult(self, byType):
			if self.wndPetInfoWindow:
				self.wndPetInfoWindow.PetAttrDetermineResult(byType)
			
		def PetAttrChangeResult(self, slotIndex, byType):
			if self.wndPetInfoWindow:
				self.wndPetInfoWindow.PetAttrChangeResult(slotIndex, byType)
				
		def PetReviveResult(self, result):
			if self.wndPetInfoWindow:
				self.wndPetInfoWindow.PetReviveResult(result)

		def PetWindowTypeResult(self, result): #checked
			if self.wndPetInfoWindow:
				self.wndPetInfoWindow.PetWindowTypeResult(result)

	if app.ENABLE_ANTI_MULTIPLE_FARM:
		def ToggleAntiMultipleFarmWindow(self):
			if not self.wndAntiMultipleFarm:
				return
			
			if anti_multiple_farm.GetAntiFarmPlayerCount() <= anti_multiple_farm.MULTIPLE_FARM_MAX_ACCOUNT:
				try:
					self.wndPopupDialog.SetText(localeinfo.ANTI_MULTIPLE_FARM_MESSAGE.format(anti_multiple_farm.MULTIPLE_FARM_MAX_ACCOUNT+1))
					self.wndPopupDialog.Open()
				except:
					self.wndPopupDialog = uicommon.PopupDialog()
					self.wndPopupDialog.SetText(localeinfo.ANTI_MULTIPLE_FARM_MESSAGE.format(anti_multiple_farm.MULTIPLE_FARM_MAX_ACCOUNT+1))
					self.wndPopupDialog.Open()
				return
			
			isShow = self.wndAntiMultipleFarm.IsShow()
			self.wndAntiMultipleFarm.Close() if isShow else self.wndAntiMultipleFarm.Open()
		
		def SendAntiFarmReload(self):
			if self.wndTaskBar:
				self.wndTaskBar.ReloadAntiMultipleFarmState()
			
			if self.wndAntiMultipleFarm.IsShow():
				self.wndAntiMultipleFarm.OnRefreshData()

				if self.wndAntiMultipleFarm.page_manage_mode != uiantimultiplefarm.VIEW_MODE:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.ANTI_MULTIPLE_FARM_REFRESHED)
		
		def RegistItemGive(self, itemVnum, itemCount):
			if not self.wndGiveItem:
				return
			
			self.wndGiveItem.Open(itemVnum, itemCount)

	if app.ENABLE_12ZI:
		def SetBeadCount(self, value):
			if self.wndBead:
				self.wndBead.SetBeadCount(value)

		def NextBeadUpdateTime(self, value):
			if self.wndBead:
				self.wndBead.NextBeadUpdateTime(value)

	if app.USE_AURA_SYSTEM:
		def AuraWindowOpen(self, type):
			if self.wndAura.IsShow():
				return

			print "interfaceModule::AuraWindowOpen %d" % type
			self.wndAura.Open(type)

			if not self.wndInventory.IsShow():
				self.wndInventory.Show()

		def AuraWindowClose(self):
			if not self.wndAura.IsShow():
				return

			self.wndAura.CloseWindow()

		if app.ENABLE_PARTY_WAR:
			def __MakePartyWarRanking(self):
				self.wndPartywarPlayerBoard = uipartywar.PartyWarPlayerBoard()
				self.wndPartywarPlayerBoard.LoadWindow()
				self.wndPartywarPlayerBoard.Hide()
				
			def OpenPartyWarPlayerBoard(self):
				if self.wndPartywarPlayerBoard:
					self.wndPartywarPlayerBoard.Open()

			def PartyWarRank(self, playerPlace, playerName, playerEmpire, playerKills, IsMine):
				self.wndPartywarPlayerBoard.AddPlayerRank(int(playerPlace), playerName, int(playerEmpire), int(playerKills), int(IsMine))
				
			def PartyWarTimeData(self, Time):
				self.wndPartywarPlayerBoard.PartyWarTimeData(int(Time))

	if app.ENABLE_ITEMSHOP:
		def MakeItemShopWindow(self):
			if self.wndItemShop == None:
				self.wndItemShop = uiitemshop.ItemShopWindow()
		def OpenItemShopWindow(self):
			self.MakeItemShopWindow()
			if self.wndItemShop.IsShow():
				self.wndItemShop.Close()
			else:
				self.wndItemShop.Open()
		def OpenItemShopMainWindow(self):
			self.MakeItemShopWindow()
			self.wndItemShop.Open()
			self.wndItemShop.LoadFirstOpening()
		def ItemShopHideLoading(self):
			self.MakeItemShopWindow()
			self.wndItemShop.Open()
			self.wndItemShop.CloseLoading()
		def ItemShopPurchasesWindow(self):
			self.MakeItemShopWindow()
			self.wndItemShop.Open()
			self.wndItemShop.OpenPurchasesWindow()
		def ItemShopSetDragonCoin(self,dragonCoin):
			self.MakeItemShopWindow()
			self.wndItemShop.SetDragonCoin(dragonCoin)
		def OpenItemShopToSearch(self, name):
			self.MakeItemShopWindow()
			self.wndItemShop.Open()
			self.wndItemShop.SetTop()
			self.wndItemShop.SearchByName(name)
		def OpenItemShopToWheel(self):
			self.MakeItemShopWindow()
			self.wndItemShop.Open()
			self.wndItemShop.SetTop()
			self.wndItemShop.WheelBtn()
		def SetWheelItemData(self, cmd):
			self.MakeItemShopWindow()
			self.wndItemShop.SetWheelItemData(str(cmd))
		def OnSetWhell(self, giftIndex):
			self.MakeItemShopWindow()
			self.wndItemShop.OnSetWhell(int(giftIndex))
		def GetWheelGiftData(self, itemVnum, itemCount):
			self.MakeItemShopWindow()
			self.wndItemShop.GetWheelGiftData(int(itemVnum), int(itemCount))
			
		def RecvPrizeProgress(self,currentProgress,prizeCount):
			self.MakeItemShopWindow()
			self.wndItemShop.SetPrizeProgress(int(currentProgress), int(prizeCount))
		# The odds push feeds two consumers: the module-level mirror in
		# uiitemshop (long-lived, read by the wiki's [Wheel] origin row) and the
		# window's own per-instance copy (wiped on every odds-panel open). The
		# window is only fed when it already exists -- the wiki prefetches these
		# odds and must not construct the whole shop window to hold data.
		def RecvWheelOddsBegin(self):
			uiitemshop.WikiWheelOddsBegin()
			if self.wndItemShop:
				self.wndItemShop.RecvWheelOddsBegin()
		def RecvWheelOddsTier(self, data):
			uiitemshop.WikiWheelOddsTier(str(data))
			if self.wndItemShop:
				self.wndItemShop.RecvWheelOddsTier(str(data))
		def RecvWheelOddsItem(self, data):
			uiitemshop.WikiWheelOddsItem(str(data))
			if self.wndItemShop:
				self.wndItemShop.RecvWheelOddsItem(str(data))
		def RecvWheelOddsPity(self, data):
			uiitemshop.WikiWheelOddsPity(str(data))
			if self.wndItemShop:
				self.wndItemShop.RecvWheelOddsPity(str(data))
		def RecvWheelOddsEnd(self):
			uiitemshop.WikiWheelOddsEnd()
			if self.wndItemShop:
				self.wndItemShop.RecvWheelOddsEnd()

	if app.ENABLE_INGAME_WIKI:
		def SetWikiBuilder(self, builderFunc):
			# FAST_WARP_UI: GameWindow hands us its lazy wiki builder so the
			# taskbar toggle / hyperlink jump API can build the wiki on demand.
			self.wikiBuilderFunc = builderFunc

		def __EnsureWiki(self):
			if not self.wndWiki and getattr(self, "wikiBuilderFunc", None):
				self.wikiBuilderFunc()

		def ToggleWikiWindow(self):
			if app.ENABLE_FAST_WARP_UI:
				self.__EnsureWiki()
			if self.wndWiki:
				if self.wndWiki.IsShow():
					self.wndWiki.Hide()
				else:
					self.wndWiki.Show()
					self.wndWiki.SetTop()

		# ----------------------------------------------------------------
		# Hyperlink jump API
		#
		# Any UI that displays an item or monster vnum can route the player
		# straight to its wiki entry by calling one of these methods. The
		# underlying OpenSpecialWikiPage handles Show / SetTop / page
		# navigation, so callers don't need to know the wiki internals.
		#
		# Fails silently if the wiki window isn't instantiated yet (early
		# login, character select) or the vnum can't be resolved -- safer
		# for hot paths like tooltips and chat handlers.
		#
		# Example call sites (existing chains can be migrated to these):
		#   uiitemshop.py, uireward.py, uishop.py, uispinwheel.py
		#       wiki.GetBaseClass().OpenSpecialWikiPage(vnum, isBox)
		#   becomes
		#       self.interface.OpenWikiToItem(vnum, isBox=isBox)
		# ----------------------------------------------------------------
		def OpenWikiToItem(self, vnum, isBox = False):
			if app.ENABLE_FAST_WARP_UI:
				self.__EnsureWiki()
			if not self.wndWiki:
				return
			try:
				self.wndWiki.OpenSpecialWikiPage(int(vnum), bool(isBox), False)
			except Exception:
				pass

		def OpenWikiToGrowthPet(self):
			if app.ENABLE_FAST_WARP_UI:
				self.__EnsureWiki()
			if not self.wndWiki:
				return
			try:
				if not self.wndWiki.IsShow():
					net.ToggleWikiWindow()
				self.wndWiki.CloseBaseWindows()
				self.wndWiki.OpenSystemRoute("PAGE:growthpet")
			except Exception:
				pass

		def OpenWikiToGemShop(self):
			if app.ENABLE_FAST_WARP_UI:
				self.__EnsureWiki()
			if not self.wndWiki:
				return
			try:
				if not self.wndWiki.IsShow():
					net.ToggleWikiWindow()
				self.wndWiki.CloseBaseWindows()
				self.wndWiki.OpenSystemRoute("PAGE:gemshop")
			except Exception:
				pass

		def OpenWikiToMonster(self, vnum):
			if app.ENABLE_FAST_WARP_UI:
				self.__EnsureWiki()
			if not self.wndWiki:
				return
			try:
				self.wndWiki.OpenSpecialWikiPage(int(vnum), False, True)
			except Exception:
				pass

		def OpenWikiFromHyperlink(self, hyperlink):
			# Parse an "item:..." chat hyperlink and open the wiki on that item.
			# Used by SHIFT+click handlers on chat hyperlinks in uichat.py,
			# uichat2.py, uiwhisper.py and game.py. Hyperlink format from
			# PythonChatModule.cpp: "item:<hex_vnum>:<hex_flags>:..."
			# Fails silently on parse error -- safe for hot mouse handlers.
			if not hyperlink:
				return
			tokens = hyperlink.split(":")
			if len(tokens) < 2 or tokens[0] != "item":
				return
			try:
				vnum = int(tokens[1], 16)
			except (ValueError, AttributeError):
				return
			self.OpenWikiToItem(vnum)

	if app.ENABLE_EXTENDED_BATTLE_PASS:
		def ReciveOpenExtBattlePass(self):
			if False == self.isFirstOpeningExtBattlePass:
				self.isFirstOpeningExtBattlePass = True
				self.wndBattlePassExtended.SetPage("PREMIUM")
			
			if False == self.wndBattlePassExtended.IsShow():
				self.ToggleBattlePassExtended()
			else:
				self.wndBattlePassExtended.SetPage(self.wndBattlePassExtended.GetPage())

		def ToggleBattlePassExtended(self):
			if osfinfo.BETA_PVP == True:
				try:
					self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					self.wndPopupDialog.Open()
				except:
					self.wndPopupDialog = uicommon.PopupDialog()
					self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					self.wndPopupDialog.Open()
				return

			if False == self.isFirstOpeningExtBattlePass:
				net.SendExtBattlePassAction(1)
			
			if False == self.wndBattlePassExtended.IsShow():
				self.wndBattlePassExtended.Show()
				self.wndBattlePassExtended.SetTop()
			else:
				self.wndBattlePassExtended.Close()

		def AddExtendedBattleGeneralInfo(self, BattlePassType, BattlePassName, BattlePassID, battlePassStartTime, battlePassEndTime):
			if self.wndBattlePassExtended:
				self.wndBattlePassExtended.RecvGeneralInfo(BattlePassType, BattlePassName, BattlePassID, battlePassStartTime, battlePassEndTime)

		def AddExtendedBattlePassMission(self, battlepassType, battlepassID, missionIndex, missionType, missionInfo1, missionInfo2, missionInfo3):
			if self.wndBattlePassExtended:
				self.wndBattlePassExtended.AddMission(battlepassType, battlepassID, missionIndex, missionType, missionInfo1, missionInfo2, missionInfo3)

		def UpdateExtendedBattlePassMission(self, battlepassType, missionIndex, missionType, newProgress):
			if self.wndBattlePassExtended:
				self.wndBattlePassExtended.UpdateMission(battlepassType, missionIndex, missionType, newProgress)

		def AddExtendedBattlePassMissionReward(self, battlepassType, battlepassID, missionIndex, missionType, itemVnum, itemCount):
			if self.wndBattlePassExtended:
				self.wndBattlePassExtended.AddMissionReward(battlepassType, battlepassID, missionIndex, missionType, itemVnum, itemCount)

		def AddExtendedBattlePassReward(self, battlepassType, battlepassID, itemVnum, itemCount):
			if self.wndBattlePassExtended:
				self.wndBattlePassExtended.AddReward(battlepassType, battlepassID, itemVnum, itemCount)

		def AddExtBattlePassRanklistEntry(self, playername, battlepassType, battlepassID, startTime, endTime):
			if self.wndBattlePassExtended:
				self.wndBattlePassExtended.AddRankingEntry(playername, battlepassType, battlepassID, startTime, endTime)

	if app.ENABLE_RENEWAL_PVP:
		def MakePvPWindow(self):
			if self.wndPvP == None:
				self.wndPvP = uipvp.PvPWindow()

		def OpenPvPFirst(self, playerName, playerVID):
			self.MakePvPWindow()
			self.wndPvP.OpenFirst(playerName, playerVID)

		def OpenPvPSecond(self, playerName, playerVID, data):
			pvpData = {}
			if len(data) > 0:
				try:
					dataSplit = data.split("#")
					if len(dataSplit) == 0:
						return
					del dataSplit[0]
					for j in xrange(len(dataSplit)):
						if j == player.PVP_BET:
							pvpData[player.PVP_BET] = long(dataSplit[j])
						else:
							if dataSplit[j] == "1":
								pvpData[j] = True
							else:
								pvpData[j] = False
				except:
					pass
			
			self.MakePvPWindow()
			self.wndPvP.OpenSecond(playerName, playerVID, pvpData)

	if app.ENABLE_SET_CUSTOM_ATTRIBUTE_SYSTEM:
		def SetCustomAttributeWindow(self, itemCellPos, attrEnchantProb, attrDataList):
			if not self.wndSetCustomAttribute:
				return

			self.wndSetCustomAttribute.Open(itemCellPos, attrEnchantProb, attrDataList)

	if app.ENABLE_BIOLOG_SYSTEM:
		def BiologManagerOpen(self):
			import biologmgr
			biologmgr.SendPacket(net.BIOLOG_MANAGER_OPEN)

		def ToggleBiologManagerWindow(self):
			if self.wndBiologManagerPanel.IsShow():
				self.wndBiologManagerPanel.Close()
			else:
				self.wndBiologManagerPanel.Open()

		def BiologManagerUpdate(self):
			self.wndBiologManagerPanel.RecvUpdate()

		def BiologManagerClose(self):
			if self.wndBiologManagerPanel.IsShow():
				self.wndBiologManagerPanel.Close()

	def ToggleStoryWindow(self):
		if self.wndStoryInterface.IsShow():
			self.wndStoryInterface.Close()
		else:
			self.wndStoryInterface.Open()
			net.SendChatPacket("/saryong_open")

	if app.ENABLE_NOTIFICATION_SYSTEM:
		def OnNotificationReceived(self, notifType, itemVnum, itemCount, iconPath, title, message):
			if self.wndNotificationCenter:
				self.wndNotificationCenter.AddNotification(
					notifType,
					item_vnum=itemVnum,
					item_count=itemCount,
					icon_path=iconPath,
					title=title,
					message=message
				)

		def ToggleNotificationHistory(self):
			"""Toggle the notification history window."""
			if self.wndNotificationCenter:
				self.wndNotificationCenter.ToggleHistory()

	if app.ENABLE_ULTIMATE_REGEN:
		def TrackWindowCheckPacket(self):
			if self.wndTrackWindow:
				self.wndTrackWindow.CheckPacket()

		def MakeTrackWindow(self):
			if not self.wndTrackWindow:
				self.wndTrackWindow = uitrack.TrackWindow()

		def OpenTrackWindow(self):
			if not self.wndTrackWindow:
				return

			if self.wndTrackWindow.IsShow():
				self.wndTrackWindow.Close()
			else:
				self.wndTrackWindow.Open()

		def OpenWorldBossWindow(self):
			if not self.wndWorldBoss:
				return

			if self.wndWorldBoss.IsShow():
				self.wndWorldBoss.Close()
			else:
				self.wndWorldBoss.Open()

		def TrackDungeonInfo(self, cmdData):
			if not self.wndTrackWindow:
				return
			
			self.wndTrackWindow.TrackDungeonInfo(cmdData)

		def TrackBossInfo(self, bossID, bossLeftTime, bossChannel):
			if not self.wndTrackWindow:
				return

			self.wndTrackWindow.TrackBossInfo(int(bossID), int(bossLeftTime), int(bossChannel))

		if getattr(app, "ENABLE_CURSED_BOSS", 0):
			def OnCursedAtlas(self, data):
				parts = data.split("|")
				if len(parts) < 5:
					return

				import miniMap
				miniMap.UpdateCursedBoss(int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]))

			def OnCursedHud(self, data):
				parts = data.split("|")
				if len(parts) < 7:
					return

				if not getattr(self, "wndCursedHud", None):
					import uicursedboss
					self.wndCursedHud = uicursedboss.CursedBossHud()

				self.wndCursedHud.UpdateData(int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]), int(parts[6]))

			def OnCursedHudEnd(self):
				if getattr(self, "wndCursedHud", None):
					self.wndCursedHud.Close()

		if getattr(app, "ENABLE_WORLDBOSS_V3", 0):
			def WBSpawnMode(self, data):
				if not self.wndTrackWindow:
					return

				parts = data.split("|")
				if len(parts) < 2:
					return

				try:
					bossID = int(parts[0])
					mode = int(parts[1])
				except ValueError:
					return

				self.wndTrackWindow.WBSpawnMode(bossID, mode)

	if app.ENABLE_REWARD_SYSTEM:
		def RewardData(self, isGlobal, isNeedClean, commandText):
			if self.wndReward:
				self.wndReward.RewardData(int(isGlobal), int(isNeedClean), commandText)

		def RewardDefs(self, isNeedClean, commandText):
			if self.wndReward:
				self.wndReward.RewardDefs(int(isNeedClean), commandText)

		def RewardTargets(self, isNeedClean, commandText):
			if self.wndReward:
				self.wndReward.RewardTargets(int(isNeedClean), commandText)

		def RewardWin(self, missionIdx, placement, playerName):
			if self.wndReward:
				self.wndReward.RewardWin(int(missionIdx), int(placement), playerName)

		def ChallengeBoard(self, isNeedClean, commandText):
			if self.wndReward:
				self.wndReward.ChallengeBoard(int(isNeedClean), commandText)

		def ChallengeProg(self, slot, progressText):
			if self.wndReward:
				self.wndReward.ChallengeProg(int(slot), progressText)

		# Built on first use and kept, like the dungeon HUD: it has to keep counting with the
		# challenge window closed.
		def ChallengeHudOn(self, title, deadline, targets):
			if not self.wndChallengeHud:
				import uichallengehud
				self.wndChallengeHud = uichallengehud.ChallengeHud()
			self.wndChallengeHud.SetChallenge(title, deadline, targets)

		def ChallengeHudOff(self):
			if self.wndChallengeHud:
				self.wndChallengeHud.Deactivate()

		def ChallengeMapButtonRefresh(self, total, here):
			wndGameButton = getattr(self, "wndGameButton", None)
			if wndGameButton:
				wndGameButton.RefreshChallengeMapButton(total, here)

		def __OnClickChallengeMapButton(self):
			if self.wndReward:
				self.wndReward.OpenChallenges()

		def OpenRewardWindow(self):
			# if self.wndReward == None:
				# self.wndReward = uiReward.RewardWindow()
			if self.wndReward.IsShow():
				self.wndReward.Close()
			else:
				self.wndReward.Open()

	if app.__AUTO_SKILL_READER__:
		def OpenAutoSkillReader(self):
			if self.wndAutoSkillReader == None:
				self.wndAutoSkillReader = uiAutoSkillReader.Window()
			if self.wndAutoSkillReader.IsShow():
				self.wndAutoSkillReader.Close()
			else:
				self.wndAutoSkillReader.Open()
		def OpenAutoSkillReaderForSkill(self, skillIndex):
			if self.wndAutoSkillReader == None:
				self.wndAutoSkillReader = uiAutoSkillReader.Window()
			self.wndAutoSkillReader.OpenForSkill(skillIndex)
		def AutoSkillStatus(self, status):
			if self.wndAutoSkillReader:
				self.wndAutoSkillReader.ServerSetStatus(status)
		def AutoSkillProgress(self, skillIdx, cur, req):
			if self.wndAutoSkillReader:
				self.wndAutoSkillReader.ServerSetProgress(skillIdx, cur, req)
		def AutoSkillHelper(self, vnum, enabled):
			if self.wndAutoSkillReader:
				self.wndAutoSkillReader.ServerSetHelper(vnum, enabled)
		def TryOpenAutoSkillReaderForBook(self, vnum):
			# If vnum is a skillbook handled by the auto skill reader, open the window
			# (Basic/Passive tab + preselect) instead of using the item. Returns True if handled.
			if not uiAutoSkillReader.IsSystemBook(vnum):
				return False
			if self.wndAutoSkillReader == None:
				self.wndAutoSkillReader = uiAutoSkillReader.Window()
			self.wndAutoSkillReader.OpenForBook(vnum)
			return True

	if app.ENABLE_DAILY_ALCHEMY_ORE:
		# >>> DAILY_ALCHEMY_ORE: replaced legacy SetSpinReward/SetSpinWheel delegation
		def SetAlchemyOre(self, oreCount, dailyCap, spun, enabled, secsToMidnight):
			if not self.wndSpinWheel:
				self.wndSpinWheel = uispinwheel.Window(uispinwheel.WHEEL_TYPE_NORMAL)

			self.wndSpinWheel.SetAlchemyOre(int(oreCount), int(dailyCap), int(spun), int(enabled), int(secsToMidnight))
			self.wndSpinWheel.RefreshPosition()

			if app.__SPIN_WHEEL_DUNGEON__ and self.wndDungeonSpinWheel:
				self.wndDungeonSpinWheel.RefreshPosition()

		def SetAlchemyRewards(self, cmdData):
			if self.wndSpinWheel:
				self.wndSpinWheel.SetAlchemyRewards(cmdData)

		def SetAlchemyResult(self, vnum, count):
			if self.wndSpinWheel:
				self.wndSpinWheel.SetAlchemyResult(int(vnum), int(count))
		# <<< DAILY_ALCHEMY_ORE

	if app.__SPIN_WHEEL_DUNGEON__:
		def SetDungeonSpinReward(self, selectedItemIdx, selectedItemCount, cmdData):
			if self.wndDungeonSpinWheel:
				self.wndDungeonSpinWheel.SetDungeonSpinReward(selectedItemIdx, selectedItemCount, cmdData)

		def SetDungeonSpinWheel(self, enabled, last_spin_time, count):
			if not self.wndDungeonSpinWheel:
				self.wndDungeonSpinWheel = uispinwheel.Window(uispinwheel.WHEEL_TYPE_DUNGEON)

			self.wndDungeonSpinWheel.SetSpinData(int(count), last_spin_time)

			if int(enabled):
				self.wndDungeonSpinWheel.Open()
			else:
				self.wndDungeonSpinWheel.Close()

			self.wndDungeonSpinWheel.RefreshPosition()

			if app.ENABLE_DAILY_ALCHEMY_ORE and self.wndSpinWheel:
				self.wndSpinWheel.RefreshPosition()

	def MakeCouponWindow(self):
		if self.wndCoupon == None:
			self.wndCoupon = uicuponcode.CouponWindow()

	def OpenCouponWindow(self):
		self.MakeCouponWindow()
		if self.wndCoupon.IsShow():
			self.wndCoupon.Close()
		else:
			self.wndCoupon.Open()


	if app.USE_WHEEL_OF_FORTUNE:
		def MakeWheelofFortune(self):
			if self.wndWheelofFortune==0:
				self.wndWheelofFortune=uiwheeloffortune.WheelofFortune()

		def OpenWheelofFortune(self):
			if osfinfo.BETA_PVP == True:
				try:
					self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					self.wndPopupDialog.Open()
				except:
					self.wndPopupDialog = uicommon.PopupDialog()
					self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					self.wndPopupDialog.Open()
				return
			self.MakeWheelofFortune()
			if self.wndWheelofFortune.IsShow():
				self.wndWheelofFortune.Close()
			else:
				self.wndWheelofFortune.Open()

		def SetItemData(self, cmd):
			self.MakeWheelofFortune()
			self.wndWheelofFortune.SetItemData(str(cmd))

		# def OnSetWhell(self, giftIndex):
			# self.MakeWheelofFortune()
			# self.wndWheelofFortune.OnSetWhell(int(giftIndex))

		def GetGiftData(self, itemVnum, itemCount):
			self.MakeWheelofFortune()
			uiwheeloffortune.WheelOfFortuneManager().GetGiftData(int(itemVnum), int(itemCount))

		def WheelSetDragonCoins(self, coins):
			self.MakeWheelofFortune()
			self.wndWheelofFortune.SetDragonCoins(coins)

	if app.USE_PVP_TOURNAMENT:
		def TogglePvpTournamentAdmin(self, binaryRequest = False):
			if not self.wndPvpTournamentAdmin:
				import uipvptournament
				self.wndPvpTournamentAdmin = uipvptournament.AdminPanel()

			if not self.wndPvpTournamentAdmin:
				return

			if self.wndPvpTournamentAdmin.IsShow():
				if binaryRequest == True:
					return

				self.wndPvpTournamentAdmin.Hide()
			else:
				import chr
				vid = chr.GetVIDByName(player.GetName())
				if vid == -1:
					return

				if not chr.IsGameMaster(vid):
					return

				self.wndPvpTournamentAdmin.Show()

		def TogglePvpTournamentAdminTrue(self):
			self.TogglePvpTournamentAdmin(True)

		def OnRefreshPvpTournament(self):
			if self.wndPvpTournamentAdmin and\
				self.wndPvpTournamentAdmin.IsShow():
				self.wndPvpTournamentAdmin.RefreshPhase()

		if app.PVP_HAVE_GUI:
			def AddPvpTournamentFight(self, arena, pid1, name1, race1, hp1, maxhp1, pid2, name2, race2, hp2, maxhp2):
				if not self.wndPvpTournamentFights:
					import uipvptournament
					self.wndPvpTournamentFights = uipvptournament.FightsPanel()

				if not self.wndPvpTournamentFights:
					return

				self.wndPvpTournamentFights.AddFight(arena, pid1, name1, race1, hp1, maxhp1, pid2, name2, race2, hp2, maxhp2)

			def ReloadPvpTournamentFight(self, arena, pid1, name1, race1, hp1, maxhp1, pid2, name2, race2, hp2, maxhp2, score1, score2):
				if not self.wndPvpTournamentFights:
					import uipvptournament
					self.wndPvpTournamentFights = uipvptournament.FightsPanel()

				if not self.wndPvpTournamentFights:
					return

				self.wndPvpTournamentFights.AddFight(arena, pid1, name1, race1, hp1, maxhp1, pid2, name2, race2, hp2, maxhp2, score1, score2)

			def CachePvpTournamentFight(self, arena, pid1, name1, race1, pid2, name2, race2, score1, score2, winner_pid):
				if not self.wndPvpTournamentFights:
					import uipvptournament
					self.wndPvpTournamentFights = uipvptournament.FightsPanel()

				if not self.wndPvpTournamentFights:
					return

				self.wndPvpTournamentFights.CacheFight(arena, pid1, name1, race1, pid2, name2, race2, score1, score2, winner_pid)

			def StatusPvpTournamentFight(self, pid, status):
				if not self.wndPvpTournamentFights:
					return

				status = int(status)
				if status == 1:
					self.wndPvpTournamentFights.Enter(pid)
				else:
					self.wndPvpTournamentFights.Disconnect(pid)

			def UpdateHPPvpTournament(self, pid, hp, maxhp):
				if not self.wndPvpTournamentFights:
					return

				self.wndPvpTournamentFights.UpdateHP(pid, hp, maxhp)

			def UpdateScorePvpTournament(self, pid, score):
				if not self.wndPvpTournamentFights:
					return

				self.wndPvpTournamentFights.UpdateScore(pid, score)

			def UpdatePvpTournament(self, pid, draw):
				if not self.wndPvpTournamentFights:
					return

				draw = int(draw)
				self.wndPvpTournamentFights.Update(pid, draw)

			def ClearPvpTournament(self):
				if not self.wndPvpTournamentFights:
					return

				self.wndPvpTournamentFights.Destroy()
				del self.wndPvpTournamentFights
				self.wndPvpTournamentFights = None

	if app.ENABLE_ATTR_6TH_7TH:
		def OpenAttr67AddDlg(self):
			if self.wndAttr67Add.IsShow():
				return

			self.wndAttr67Add.Show()

	if app.FAST_EQUIP_WORLDARD:
		def __MakeFastEquip(self):
			if self.wndFastEquip:
				self.wndFastEquip.Destroy()
				del self.wndFastEquip

			self.wndFastEquip = uifastequip.UiFastEquip()
			self.wndFastEquip.LoadWindow()
			self.wndFastEquip.Hide()

		def OpenFastEquip(self):
			if self.wndFastEquip:
				if self.wndFastEquip.IsShow():
					self.wndFastEquip.Hide()
				else:
					self.wndFastEquip.Show()
					if app.ENABLE_GEAR_SETS:
						self.wndFastEquip.RequestGearSetData()

	if app.ENABLE_DRAGON_SOUL_SYSTEM:
		def BINARY_AutoDS(self, on):
			if self.wndDragonSoul:
				self.wndDragonSoul.AutoDS(int(on))

	if app.USE_DUNGEON_INFO:
		def DungeonInfoOpen(self):
			if self.wndDungeonInfo:
				self.wndDungeonInfo.OnOpen()

		def DungeonRankingOpen(self):
			if self.wndDungeonInfo:
				self.wndDungeonInfo.OnOpenRanking()

		def DungeonInfoReload(self, onReset):
			if self.wndDungeonInfo:
				self.wndDungeonInfo.OnReload(onReset)

		def ToggleDungeonInfo(self):
			if osfinfo.BETA_PVP == True:
				try:
					self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					self.wndPopupDialog.Open()
				except:
					self.wndPopupDialog = uicommon.PopupDialog()
					self.wndPopupDialog.SetText(localeinfo.BETA_PVP_STATUS)
					self.wndPopupDialog.Open()

				return

			if not player.IsObserverMode():
				if not self.wndDungeonInfo.IsShow():
					self.wndDungeonInfo.Show()
				else:
					self.wndDungeonInfo.Hide()

		def RefreshDungeonInfoWindow(self):
			if self.wndDungeonInfo:
				self.wndDungeonInfo.Refresh()

		def RefreshDungeonInfoRankingWindow(self):
			if self.wndDungeonInfo:
				self.wndDungeonInfo.RefreshRanking()

		def RecvDungeonRankPos(self, num, pos):
			uidungeoninfo.OnRankPos(int(num), int(pos))

		def RecvDungeonStatBase(self, first, pairs):
			uidungeoninfo.OnStatBase(first, pairs)
			if self.wndDungeonInfo:
				self.wndDungeonInfo.RefreshEntryStatus()

		def RecvDungeonStatRefund(self, left, maxCount):
			uidungeoninfo.OnStatRefund(left, maxCount)
			if self.wndDungeonInfo:
				self.wndDungeonInfo.RefreshEntryStatus()

		def RecvDungeonStatReset(self, secs):
			uidungeoninfo.OnStatReset(secs)
			if self.wndDungeonInfo:
				self.wndDungeonInfo.RefreshEntryStatus()

		def RecvDungeonBossContrib(self, vid, pct, threshold):
			if self.uitargetBoard:
				self.uitargetBoard.OnBossContrib(vid, pct, threshold)

		if app.USE_DUNGEON_INFO_ADDON_LEVEL_CAP:
			def DungeonInfoCapLevel(self, level, shown):
				if self.wndDungeonInfo:
					if self.wndDungeonInfo.CapLevel(level, shown) == True:
						self.CheckGameButton()

			def DungeonInfoCapLevelEnd(self):
				if self.wndDungeonInfo:
					if self.wndDungeonInfo.CapLevelEnd() == True:
						self.CheckGameButton()

			def __DungeonInfoToggleCapLevel(self):
				if self.wndDungeonInfo:
					self.wndDungeonInfo.OnToggleCapLevel()

	if app.__RANKING_SYSTEM__:
		def OpenRanking(self):
			if self.wndRanking == None:
				self.wndRanking = uiranknew.Window()
			if self.wndRanking.IsShow():
				self.wndRanking.Close()
			else:
				self.wndRanking.Open()

		def UpdateRankData(self, rankType, timeIdx, rankIdx, mainVal):
			if self.wndRanking:
				self.wndRanking.UpdateRankData(rankType, timeIdx, rankIdx, mainVal)

		def LoadRankData(self, rankType, timeIdx, rankIdx, nextUpdateTime, mainVal, rankCmd, nextWeeklyReset=0, nextMonthlyReset=0):
			if self.wndRanking:
				self.wndRanking.LoadRankData(rankType, timeIdx, rankIdx, nextUpdateTime, mainVal, rankCmd, nextWeeklyReset, nextMonthlyReset)

		def LoadHallOfFameData(self, rankType, timeIdx, rankIdx, winnersCmd):
			if self.wndRanking:
				self.wndRanking.LoadHallOfFameData(rankType, timeIdx, rankIdx, winnersCmd)

	if app.USE_SHIP_DEFENSE:
		def BINARY_Update_Mast_Window(self, isON):
			if self.wndMiniMap:
				self.wndMiniMap.SetMastWindow(int(isON))

		def BINARY_Update_Mast_HP(self, hp, maxhp):
			if self.wndMiniMap:
				self.wndMiniMap.SetMastHP(hp, maxhp)

	if app.USE_COSTUME_ATTR_TRANSFER:
		def RequestOpenQuickTransferWindow(self, slotPos):
			if not getattr(app, "USE_QUICK_ATTR_TRANSFER", 0):
				return

			if not self.wndQuickTransfer:
				import uiquicktransfer
				self.wndQuickTransfer = uiquicktransfer.QuickTransferWindow(self.tooltipItem, self)

			if self.wndQuickTransfer:
				self.wndQuickTransfer.RequestOpen(slotPos)

		def OpenQuickTransferWindow(self):
			if getattr(app, "USE_QUICK_ATTR_TRANSFER", 0) and self.wndQuickTransfer:
				self.wndQuickTransfer.OpenConfirmed()

		def CloseQuickTransferWindow(self, fromServer = False):
			if getattr(app, "USE_QUICK_ATTR_TRANSFER", 0) and self.wndQuickTransfer:
				self.wndQuickTransfer.Close(not fromServer)

		def SetQuickTransferHighlight(self, greenSlot, redSlot):
			if self.wndInventory:
				self.wndInventory.SetQuickTransferHighlight(greenSlot, redSlot)

		def ClearQuickTransferHighlightSlots(self):
			if self.wndInventory:
				self.wndInventory.ClearQuickTransferHighlightSlots()

		def OpenAttrTransferWindow(self):
			if not self.wndAttrTransfer:
				import uiattrtransfer
				self.wndAttrTransfer = uiattrtransfer.TransferWindow(self.tooltipItem)

			if self.wndAttrTransfer:
				self.wndAttrTransfer.Open()

			if self.wndInventory and not self.wndInventory.IsShow():
				self.ToggleInventoryWindow()

		def CloseAttrTransferWindow(self):
			if self.wndAttrTransfer:
				self.wndAttrTransfer.Close()

		def AttrTransferSuccess(self):
			if self.wndAttrTransfer:
				self.wndAttrTransfer.Success()

	if app.USE_ACCE_ATTR_TRANSFER:
		def OpenAcceAttrTransferWindow(self):
			if not self.wndAcceAttrTransfer:
				import uiacceattrtransfer
				self.wndAcceAttrTransfer = uiacceattrtransfer.AcceTransferWindow(self.tooltipItem)

			if self.wndAcceAttrTransfer:
				self.wndAcceAttrTransfer.Open()

			if self.wndInventory and not self.wndInventory.IsShow():
				self.ToggleInventoryWindow()

		def CloseAcceAttrTransferWindow(self):
			if self.wndAcceAttrTransfer:
				self.wndAcceAttrTransfer.Close()

		def AcceAttrTransferSuccess(self):
			if self.wndAcceAttrTransfer:
				self.wndAcceAttrTransfer.Success()

	if app.USE_ITEM_ATTR_BACKUP_MODE:
		def OpenItemBackupAttr(self, window, cell):
			if not self.wndItemBackupAttr:
				self.wndItemBackupAttr = uicommon.SelectItemBackupAttr()

			if self.wndItemBackupAttr:
				self.wndItemBackupAttr.Open(window, cell)

	if app.USE_BL_FISH_EVENT:
		def ClickFishEventButton(self):
			if not self.fish_game:
				self.fish_game = uiminigamefishevent.MiniGameFish()
				self.fish_game.SetInven(self.wndInventory)
				self.fish_game.BindInterface(self)
				self.fish_game.SetItemToolTip(self.tooltipItem)

			self.fish_game.Open()

		def MiniGameFishUse(self, window, pos, shape):
			if self.fish_game:
				self.fish_game.MiniGameFishUse(window, pos, shape)

		def MiniGameFishAdd(self, pos, shape):
			if self.fish_game:
				self.fish_game.MiniGameFishAdd(pos, shape)

		def MiniGameFishReward(self, vnum):
			if self.fish_game:
				self.fish_game.MiniGameFishReward(vnum)

		def MiniGameFishCount(self, count):
			if self.fish_game:
				self.fish_game.MiniGameFishCount(count)

	#if app.USE_INGAME_CHANGE_CHANNEL:
	def RefreshChannelText(self):
		if self.wndMiniMap:
			self.wndMiniMap.RefreshServerName()

	if app.USE_INGAME_CHANGE_CHANNEL:
		def ToggleChangeCH(self):
			if self.dlgSystem:
				self.dlgSystem.OnToggleChangeCH()

	if app.ENABLE_VOICE_CHAT:
		def ToggleVoiceChatConfigWindow(self):
			if player.GetLevel() < 30:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.VOICE_CHAT_LEVEL)
				return
			if self.wndVoiceChatConfig:
				if self.wndVoiceChatConfig.IsShow():
					self.wndVoiceChatConfig.Hide()
				else:
					self.wndVoiceChatConfig.Show()
					self.wndVoiceChatConfig.SetTop()

	def OnChangeGold(self, amount):
		if amount > 0:
			self.yangText.AddGoldValue(localeinfo.GAME_CHANGE_GOLD_RECEIVED_NEW % (localeinfo.NumberToStringDotted(amount)))
		elif amount < 0:
			self.yangText.AddGoldValue(localeinfo.GAME_CHANGE_GOLD_DEDUCTED_NEW % (localeinfo.NumberToStringDotted(abs(amount))))

	if app.USE_NORTHWIND_DEEPS_DUNGEON:
		def NorthWindDeeps_Timer(self, start_time):
			if self.wndMiniMap:
				self.wndMiniMap.NorthWindDeeps_Timer(start_time)

		def NorthWindDeeps_Debuff(self, percent, count, each):
			if self.wndMiniMap:
				self.wndMiniMap.NorthWindDeeps_Debuff(percent, count, each)

	# if app.USE_NORTHWIND_DEEPS_DUNGEON:
	def UIDamage(self, damage_type):
		if not self.wndUIDamage:
			import uidamageui
			self.wndUIDamage = uidamageui.DamageWindow()

		self.wndUIDamage.Open(damage_type)

	def CloseUIDamage(self):
		if self.wndUIDamage and self.wndUIDamage.IsShow():
			self.wndUIDamage.Close()

	if app.ENABLE_AUTO_SHOUT:
		def UpdateAutoShout(self, status):
			uichat.UpdateAutoShoutStatus(status)

		if app.ENABLE_AUTO_SHOUT_V2:
			def SetAutoShoutInterval(self, seconds):
				uichat.SetAutoShoutMinInterval(seconds)

	if app.USE_LOG_EXCHANGE:
		def OpenExchangeLog(self):
			if self.wndExchangeLog:
				if self.wndExchangeLog.IsShow():
					self.wndExchangeLog.Close()
				else:
					self.wndExchangeLog.Open(False)
			else:
				net.SendChatPacket("/log_exchange load 1")

		def LogExchange_Clear(self, actual_page, max_page, refresh):
			if not self.wndExchangeLog:
				self.wndExchangeLog = uiexchange.ExchangeLog()

			self.wndExchangeLog.Clear(actual_page, max_page, refresh)

		def LogExchange_Load(self, ex_id, unix_time, src_ip, trg_name, trg_level, src_gold, trg_gold, src_cheque, trg_cheque):
			if not self.wndExchangeLog:
				self.wndExchangeLog = uiexchange.ExchangeLog()

			self.wndExchangeLog.Load(ex_id, unix_time, src_ip, trg_name, trg_level, src_gold, trg_gold, src_cheque, trg_cheque)

		def LogExchange_Open(self, refresh):
			if self.wndExchangeLog:
				self.wndExchangeLog.Open(refresh)

		def LogExchangeView_Clear(self, ex_id):
			if not self.wndExchangeLog:
				self.wndExchangeLog = uiexchange.ExchangeLog()

			self.wndExchangeLog.View_Clear(ex_id)

		def LogExchangeView_Load(self, ex_id,\
											own,\
											pos,\
											vnum,\
											count,\
											soul_bind,\
											transmutation_vnum,\
											socket1,\
											socket2,\
											socket3,\
											socket4,\
											socket5,\
											apply_random_type1,\
											apply_random_value1,\
											apply_random_path1,\
											apply_random_type2,\
											apply_random_value2,\
											apply_random_path2,\
											apply_random_type3,\
											apply_random_value3,\
											apply_random_path3,\
											apply_random_type4,\
											apply_random_value4,\
											apply_random_path4,\
											attr_type1,\
											attr_value1,\
											attr_path1,\
											attr_type2,\
											attr_value2,\
											attr_path2,\
											attr_type3,\
											attr_value3,\
											attr_path3,\
											attr_type4,\
											attr_value4,\
											attr_path4,\
											attr_type5,\
											attr_value5,\
											attr_path5,\
											attr_type6,\
											attr_value6,\
											attr_path6,\
											attr_type7,\
											attr_value7,\
											attr_path7,\
											backup_mode,\
											backup_attr_type1,\
											backup_attr_value1,\
											backup_attr_path1,\
											backup_attr_type2,\
											backup_attr_value2,\
											backup_attr_path2,\
											backup_attr_type3,\
											backup_attr_value3,\
											backup_attr_path3,\
											backup_attr_type4,\
											backup_attr_value4,\
											backup_attr_path4,\
											backup_attr_type5,\
											backup_attr_value5,\
											backup_attr_path5,\
											backup_attr_type6,\
											backup_attr_value6,\
											backup_attr_path6,\
											backup_attr_type7,\
											backup_attr_value7,\
											backup_attr_path7,\
											enchant_type1,\
											enchant_value1,\
											enchant_path1,\
											enchant_type2,\
											enchant_value2,\
											enchant_path2,\
											enchant_type3,\
											enchant_value3,\
											enchant_path3,\
											enchant_type4,\
											enchant_value4,\
											enchant_path4,\
											set_value):
			if not self.wndExchangeLog:
				self.wndExchangeLog = uiexchange.ExchangeLog()

			self.wndExchangeLog.View_Load(ex_id,\
												own,\
												pos,\
												vnum,\
												count,\
												soul_bind,\
												transmutation_vnum,\
												socket1,\
												socket2,\
												socket3,\
												socket4,\
												socket5,\
												apply_random_type1,\
												apply_random_value1,\
												apply_random_path1,\
												apply_random_type2,\
												apply_random_value2,\
												apply_random_path2,\
												apply_random_type3,\
												apply_random_value3,\
												apply_random_path3,\
												apply_random_type4,\
												apply_random_value4,\
												apply_random_path4,\
												attr_type1,\
												attr_value1,\
												attr_path1,\
												attr_type2,\
												attr_value2,\
												attr_path2,\
												attr_type3,\
												attr_value3,\
												attr_path3,\
												attr_type4,\
												attr_value4,\
												attr_path4,\
												attr_type5,\
												attr_value5,\
												attr_path5,\
												attr_type6,\
												attr_value6,\
												attr_path6,\
												attr_type7,\
												attr_value7,\
												attr_path7,\
												backup_mode,\
												backup_attr_type1,\
												backup_attr_value1,\
												backup_attr_path1,\
												backup_attr_type2,\
												backup_attr_value2,\
												backup_attr_path2,\
												backup_attr_type3,\
												backup_attr_value3,\
												backup_attr_path3,\
												backup_attr_type4,\
												backup_attr_value4,\
												backup_attr_path4,\
												backup_attr_type5,\
												backup_attr_value5,\
												backup_attr_path5,\
												backup_attr_type6,\
												backup_attr_value6,\
												backup_attr_path6,\
												backup_attr_type7,\
												backup_attr_value7,\
												backup_attr_path7,\
												enchant_type1,\
												enchant_value1,\
												enchant_path1,\
												enchant_type2,\
												enchant_value2,\
												enchant_path2,\
												enchant_type3,\
												enchant_value3,\
												enchant_path3,\
												enchant_type4,\
												enchant_value4,\
												enchant_path4,\
												set_value)

		def LogExchangeView_Open(self):
			if not self.wndExchangeLog:
				self.wndExchangeLog = uiexchange.ExchangeLog()

			self.wndExchangeLog.View_Open()

	if app.USE_CRAFT_ITEM_SYSTEM:
		def ToggleCraftItem(self):
			# if not self.wnd_craft_item:
				# import uicraftitem
				# self.wnd_craft_item = uicraftitem.CraftItemWnd()

			# self.wnd_craft_item.Toggle()
			if self.wnd_craft_item:
				self.wnd_craft_item.Destroy()
				del self.wnd_craft_item

			import uicraftitem
			self.wnd_craft_item = uicraftitem.CraftItemWnd()
			self.wnd_craft_item.Toggle()

	if app.ENABLE_GUILD_RENEWAL:
		def OpenGuildWindow(self):
			if self.wndGuild and not self.wndGuild.IsShow():
				if self.wndGuild.CanOpen():
					self.wndGuild.Open()
				else:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeinfo.GUILD_YOU_DO_NOT_JOIN)

	if app.USE_PORTABLE_TELEPORT_WITH_UI:
		def ToggleTeleportWindow(self):
			if not self.teleportWnd:
				self.teleportWnd = uiteleport.TeleportWindow()

			self.teleportWnd.Toggle()

		def OpenTeleportWindow(self):
			if not self.teleportWnd:
				self.teleportWnd = uiteleport.TeleportWindow()
			self.teleportWnd.Open()
