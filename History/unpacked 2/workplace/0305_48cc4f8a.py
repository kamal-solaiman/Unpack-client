# coding: latin_1
#
# Mining Rework v5 "Yield Rock" (docs/MINING_REWORK.md §0) - client vein readout drawn as a REAL
# engine text tail on the vein entity via textTail.SetMineInfo (NOT a ui.Window). Two stacked lines:
#     LINE 1 (shared, everyone nearby)  = the vein's SWING BUDGET draining: "34/50"  <- this is what despawns it
#     LINE 2 (this digger only)         = your running ore total from this vein:  "+63"  ( "+63 (x2)" on a bigger hit )
# The engine positions/follows/depth-sorts the tail and auto-clears it when the vein despawns, so it can
# never snap to the player. There is NO countdown any more (the swing budget, not a timer, ends the vein).
#
# Server wire (game.py routes both):
#   "MineTimer vid remaining budgetLeft budgetMax"  (remaining unused) -> OnMineTimer  -> LINE 1 (broadcast)
#   "MineTally vid tally perHit"                                        -> OnMineTally  -> LINE 2 (unicast to digger)

import app
import chr
import textTail

# vid -> [budgetLeft, budgetMax, tally, perHit]   (tally == -1 => no LINE 2 yet, e.g. a bystander)
g_mineDict = {}

# packed 0xRRGGBB (the C++ binding unpacks; alpha is always 1.0)
MINE_COL_GREEN  = 0x33E633
MINE_COL_YELLOW = 0xF2D91A
MINE_COL_RED    = 0xF23333


def OnMineTimer(vid, remaining, budgetLeft, budgetMax):
	# LINE 1: the shared swing budget. budgetLeft <= 0 -> the vein despawned, drop the tail.
	if budgetLeft <= 0:
		_Remove(vid)
		return
	st = g_mineDict.get(vid, None)
	if st is None:
		g_mineDict[vid] = [int(budgetLeft), max(1, int(budgetMax)), -1, 0]
	else:
		st[0] = int(budgetLeft)
		st[1] = max(1, int(budgetMax))
	_Apply(vid)


def OnMineTally(vid, tally, perHit):
	# LINE 2: this digger's running ore total (+ per-hit value). Only arrives after OnMineTimer created the entry.
	st = g_mineDict.get(vid, None)
	if st is None:
		return
	st[2] = int(tally)
	st[3] = int(perHit)
	_Apply(vid)


def _Remove(vid):
	if vid in g_mineDict:
		del g_mineDict[vid]
	try:
		textTail.ClearMineInfo(vid)
	except:
		pass


def Clear():
	for vid in g_mineDict.keys():
		try:
			textTail.ClearMineInfo(vid)
		except:
			pass
	g_mineDict.clear()


def _Color(budgetRatio):
	# the rock is running out -> warm the colour (green > yellow > red)
	if budgetRatio <= 0.2:
		return MINE_COL_RED
	if budgetRatio <= 0.5:
		return MINE_COL_YELLOW
	return MINE_COL_GREEN


def _Apply(vid):
	st = g_mineDict.get(vid, None)
	if st is None:
		return
	(budgetLeft, budgetMax, tally, perHit) = st
	text = "%d/%d" % (budgetLeft, budgetMax)
	if tally >= 0:
		if perHit > 1:
			text = "%s\n+%d (x%d)" % (text, tally, perHit)   # show per-hit only when it's worth more than 1
		else:
			text = "%s\n+%d" % (text, tally)
	try:
		textTail.SetMineInfo(vid, text, _Color(float(budgetLeft) / float(budgetMax)))
	except:
		pass


def Update():
	# Called every frame from game.py.OnUpdate. v5 has no countdown to tick; this only reaps a vein that
	# despawned without a teardown packet reaching us (edge case) so a stale tail can't linger.
	if not g_mineDict:
		return
	dead = []
	for vid in g_mineDict.keys():   # Py2 keys() is a copy -> safe to _Remove after the loop
		try:
			chr.GetPixelPosition(vid)   # raises when the vein instance is gone
		except:
			dead.append(vid)
	for vid in dead:
		_Remove(vid)
