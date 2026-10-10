# coding: latin_1

import ui
import constinfo
import chat
import localeinfo
import app

class RankingGUI(ui.ScriptWindow):
	MIN_SCROLLBAR_LIST = 4
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		if app.ENABLE_WINDOW_SLIDE_EFFECT:
			self.AddFlag("animated_board")
		
		self.Index = 0
		self.isLoaded = False
		self.LoadDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		self.Index = 0
		self.isLoaded = False

	def LoadDialog(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/rankingen.py")
		except:
			import exception
			exception.Abort("EventInfo.LoadDialog.LoadScript")
		try:
			self.eventBoard = self.GetChild("EventBoard")
			self.ListBoxNew = self.GetChild("ListBoxNEW")
			self.ListBox = self.GetChild("LxistBox")
			self.eventBoardTitleBar = self.GetChild("EventBoardTitleBar")
			self.eventButtonThinBoard = self.GetChild("EventButtonThinBoard")
			self.eventScrollBar = self.GetChild("ScrollBar")
		except:
			import exception
			exception.Abort("DungeonInfo.LoadDialog.GetChild")
		self.eventBoardTitleBar.SetCloseEvent(ui.__mem_func__(self.Close))
		self.ListBox.SetScrollBar(self.eventScrollBar)
		self.ListBox.SetViewItemCount(7)
		self.ListBox.SetItemStep(46)
		self.ListBox.SetItemSize(400,38)
		
		self.ListBoxNew.SetViewItemCount(10)
		self.ListBoxNew.SetItemStep(26)
		self.ListBoxNew.SetItemSize(400,38)
		self.LoadRankButtons()

	def OnRunMouseWheel(self, nLen):
		if nLen > 0:
			self.eventScrollBar.OnUp()
		else:
			self.eventScrollBar.OnDown()

	def Close(self):
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()

	def Open(self):
		self.LoadInfo(self.Index)
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def LoadRankButtons(self):
		list = [ ["Level","level"],["Destroyed Stone","stone"],["Killed Monster","monster"],["Killed Boss","boss"],["Completed Dungeon","dungeon"],["Playtime","playtime"],["Gold","gold"],["Gaya","gaya"],["Caught Fishes","fish"],["Opened Chest","chest"]]
		for index in xrange(len(list)):
			resultItem = Item(self,index,list[index][1],list[index][0])
			resultItem.Show()
			self.ListBox.AppendItem(resultItem)

	def LoadInfo(self, index):
		self.ListBoxNew.RemoveAllItems()
		self.Index = index
		

		list = [ ["Level","level"],["Destroyed Stone","stone"],["Killed Monster","monster"],["Killed Boss","boss"],["Completed Dungeon","dungeon"],["Playtime","playtime"],["Gold","gold"],["Gaya","gaya"],["Caught Fishes","fish"],["Opened Chest","chest"]]
		#chat.AppendChat(chat.CHAT_TYPE_INFO, "index: %d"%index)
		for j in xrange(10):
			if constinfo.GetFlag("rank_%s_value_%d"%(list[index][1],j)) == 0:
				continue
			resultItem = ItemNEW(self,j+1,constinfo.GetFlag("rank_%s_name_%d"%(list[index][1],j)),constinfo.GetFlag("rank_%s_empire_%d"%(list[index][1],j)),constinfo.GetFlag("rank_%s_value_%d"%(list[index][1],j)))
			#chat.AppendChat(chat.CHAT_TYPE_INFO, "name: %s %s %d %d"%(list[index][1],constinfo.GetFlag("rank_%s_name_%d"%(list[index][1],j)),constinfo.GetFlag("rank_%s_empire_%d"%(list[index][1],j)),constinfo.GetFlag("rank_%s_value_%d"%(list[index][1],j))))
			resultItem.Show()
			self.ListBoxNew.AppendItem(resultItem)

		for j in xrange(len(self.ListBox.itemList)):
			if index == j:
				self.ListBox.itemList[j].Image.SetUpVisual("ranking/btn_%d_1.tga"%j)
				self.ListBox.itemList[j].Image.SetOverVisual("ranking/btn_%d_1.tga"%j)
				self.ListBox.itemList[j].Image.SetDownVisual("ranking/btn_%d_1.tga"%j)
			else:
				self.ListBox.itemList[j].Image.SetUpVisual("ranking/btn_%d_0.tga"%j)
				self.ListBox.itemList[j].Image.SetOverVisual("ranking/btn_%d_0.tga"%j)
				self.ListBox.itemList[j].Image.SetDownVisual("ranking/btn_%d_1.tga"%j)
	
class Item(ui.Window):
	def __init__(self, parent, index,image,name):
		ui.Window.__init__(self)
		self.parent = parent
		self.SetParent(parent)
		self.Index = int(index)
		self.image_type = image
		self.name_type = name
		self.SetSize(500, 38)
		self.InitItem()

	def InitItem(self):
		self.Image = ui.Button()
		self.Image.SetParent(self)
		self.Image.SetUpVisual("ranking/btn_%d_0.tga"%self.Index)
		self.Image.SetOverVisual("ranking/btn_%d_0.tga"%self.Index)
		self.Image.SetDownVisual("ranking/btn_%d_1.tga"%self.Index)
		self.Image.SetEvent(lambda: self.parent.LoadInfo(self.Index))
		self.Image.SetPosition(1, 2)
		self.Image.Show()

class ItemNEW(ui.Window):
	def __init__(self, parent, index,name,empire, value):
		ui.Window.__init__(self)
		self.parent = parent
		self.SetParent(parent)
		self.Index = int(index)
		self.name = str(name)
		self.empire = int(empire)
		self.value = int(value)
		self.SetSize(500, 38)
		self.InitItem()

	def InitItem(self):
		color = "|cFFCD853F"
		if self.Index == 1:
			color = "|cffffcc00"
		elif self.Index == 2:
			color = "|cFFB0C4DE"
		elif self.Index == 3:
			color = "|cFF8B4513"
		self.NameText = ui.TextLine()
		self.NameText.SetParent(self)
		self.NameText.SetPosition(65, 3)
		self.NameText.SetText("%s%s" % (color,self.name))
		self.NameText.Show()

		self.EmpireImage = ui.ImageBox()
		self.EmpireImage.SetParent(self)
		self.EmpireImage.LoadImage("d:/ymir work/ui/game/rank/empire_%d.sub"%self.empire)
		self.EmpireImage.SetPosition(175, 2)
		self.EmpireImage.Show()

		self.ValueText = ui.TextLine()
		self.ValueText.SetParent(self)
		self.ValueText.SetPosition(260, 2)
		self.ValueText.SetText("%s%s" % (color,localeinfo.NumberToMoneyStringNEW(self.value)))
		self.ValueText.Show()


