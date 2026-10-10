# coding: latin_1

import os
import re
import time
import player

DIR_THEIRS = 0
DIR_MINE = 1
DIR_SYSTEM = 2

MAX_MESSAGES = 500
COMPACT_FILE_SIZE = 65536
CACHE_DIR = "config/messagescache"

LEVEL_PREFIX_PATTERN = re.compile(r"^(c?)Lv\.(\d+) ?: ?")

_contactLevels = {}

def StripLevelPrefix(line):
	return LEVEL_PREFIX_PATTERN.sub("", line, 1)

def _CaptureLevel(contactName, line):
	m = LEVEL_PREFIX_PATTERN.match(line)
	if m:
		if m.group(1):
			_contactLevels[contactName] = "cLv." + m.group(2)
		else:
			_contactLevels[contactName] = "Lv." + m.group(2)

def GetContactLevelText(contactName):
	return _contactLevels.get(contactName, "")

def _GetFilePath(contactName):
	myName = player.GetName()
	return os.path.join(CACHE_DIR, myName, contactName + ".txt")

def _Compact(filePath):
	messages = _ReadFile(filePath)
	f = old_open(filePath, "w")
	try:
		for direction, msgType, epoch, msgText in messages[-MAX_MESSAGES:]:
			f.write("%d\t%d\t%d\t%s\n" % (direction, msgType, epoch, msgText))
	finally:
		f.close()

def _ReadFile(filePath):
	messages = []
	f = old_open(filePath, "r")
	try:
		for line in f:
			line = line.rstrip("\r\n")
			if not line:
				continue
			parts = line.split("\t", 3)
			if len(parts) == 4:
				try:
					messages.append((int(parts[0]), int(parts[1]), int(parts[2]), parts[3]))
				except ValueError:
					continue
	finally:
		f.close()
	return messages

def SaveMessage(contactName, direction, msgType, msgText):
	if not contactName:
		return
	msgText = msgText.replace("\r", " ").replace("\n", " ").strip()
	if not msgText:
		return
	try:
		filePath = _GetFilePath(contactName)
		dirPath = os.path.dirname(filePath)
		if not os.path.exists(dirPath):
			os.makedirs(dirPath)
		if os.path.exists(filePath) and os.path.getsize(filePath) > COMPACT_FILE_SIZE:
			_Compact(filePath)
		f = old_open(filePath, "a")
		try:
			f.write("%d\t%d\t%d\t%s\n" % (direction, msgType, int(time.time()), msgText))
		finally:
			f.close()
	except:
		pass

def SaveIncoming(contactName, msgType, line):
	# the client engine composes "NameFrom : text" before OnRecvWhisper (PythonNetworkStreamPhaseGame)
	namePrefix = contactName + " : "
	if line.startswith(namePrefix):
		line = line[len(namePrefix):]
	_CaptureLevel(contactName, line)
	SaveMessage(contactName, DIR_THEIRS, msgType, StripLevelPrefix(line))

def SaveSystem(contactName, msgType, text):
	SaveMessage(contactName, DIR_SYSTEM, msgType, text)

def LoadMessages(contactName):
	try:
		filePath = _GetFilePath(contactName)
		if not os.path.exists(filePath):
			return []
		messages = _ReadFile(filePath)
	except:
		return []
	return messages[-MAX_MESSAGES:]

def _ReadLastMessage(filePath):
	# tail read only: sidebar previews must not pay for full files on every refresh
	try:
		f = old_open(filePath, "rb")
		try:
			f.seek(0, 2)
			size = f.tell()
			f.seek(max(0, size - 4096))
			tail = f.read()
		finally:
			f.close()
	except:
		return None
	lines = tail.split("\n")
	for i in xrange(len(lines) - 1, -1, -1):
		line = lines[i].rstrip("\r")
		if not line:
			continue
		parts = line.split("\t", 3)
		if len(parts) == 4:
			try:
				return (int(parts[0]), int(parts[1]), int(parts[2]), parts[3])
			except ValueError:
				continue
	return None

def ListConversations():
	result = []
	try:
		dirPath = os.path.join(CACHE_DIR, player.GetName())
		if not os.path.isdir(dirPath):
			return []
		for fileName in os.listdir(dirPath):
			if not fileName.endswith(".txt"):
				continue
			contactName = fileName[:-4]
			if not contactName:
				continue
			filePath = os.path.join(dirPath, fileName)
			last = _ReadLastMessage(filePath)
			if last:
				result.append((contactName, last[0], last[1], last[2], last[3]))
			else:
				try:
					epoch = int(os.path.getmtime(filePath))
				except:
					epoch = 0
				result.append((contactName, DIR_SYSTEM, 0, epoch, ""))
	except:
		return []
	result.sort(lambda a, b: cmp(b[3], a[3]))
	return result

def DeleteConversation(contactName):
	if not contactName:
		return
	try:
		filePath = _GetFilePath(contactName)
		if os.path.exists(filePath):
			os.remove(filePath)
	except:
		pass

_seenTimes = None
_seenOwner = ""

def _SeenFilePath():
	return os.path.join(CACHE_DIR, player.GetName(), "_seen.dat")

def _LoadSeenTimes():
	global _seenTimes, _seenOwner
	myName = player.GetName()
	if _seenTimes is not None and _seenOwner == myName:
		return _seenTimes
	_seenTimes = {}
	_seenOwner = myName
	try:
		filePath = _SeenFilePath()
		if os.path.exists(filePath):
			f = old_open(filePath, "r")
			try:
				for line in f:
					parts = line.rstrip("\r\n").split("\t", 1)
					if len(parts) == 2:
						try:
							_seenTimes[parts[0]] = int(parts[1])
						except ValueError:
							continue
			finally:
				f.close()
	except:
		pass
	return _seenTimes

def GetSeenTime(contactName):
	return _LoadSeenTimes().get(contactName, 0)

def MarkSeen(contactName):
	if not contactName:
		return
	seen = _LoadSeenTimes()
	seen[contactName] = int(time.time())
	try:
		filePath = _SeenFilePath()
		dirPath = os.path.dirname(filePath)
		if not os.path.exists(dirPath):
			os.makedirs(dirPath)
		f = old_open(filePath, "w")
		try:
			for name, epoch in seen.items():
				f.write("%s\t%d\n" % (name, epoch))
		finally:
			f.close()
	except:
		pass
