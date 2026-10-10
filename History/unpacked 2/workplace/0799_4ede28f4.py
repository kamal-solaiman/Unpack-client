# coding: latin_1

# Layout for uiteleport.TeleportWindow. Everything the atlas page draws lives
# here so positions can be tuned in game and written straight back -- the panel
# reads no layout out of teleport_points.txt any more.
#
# REGION CHILDREN, below, are the editable part:
#   "x"/"y"   position on the atlas image (this is what the in-game widget
#             inspector reports as Pos, because they parent to Atlas)
#   "map"     which map's points/spawns the right column shows when clicked;
#             "-" = placed but not bound to a map yet
#   "tooltip" localeinfo key for the hover name
#   "page"    atlas page the region belongs to (arrows hide while only 1 page)

IMG = "d:/ymir work/ui/game/teleport_window/"
BTN = IMG + "map_buttons/"

BG_X = 6
BG_Y = 33
BG_W = 516
BG_H = 370
COL_X = BG_X + BG_W
COL_W = 212

WIN_W = BG_X + BG_W + COL_W + 6
WIN_H = BG_Y + BG_H + 6

ARROW_W = 79
ARROW_H = 30

window = {
	"name" : "TeleportWindow",

	"x" : (SCREEN_WIDTH / 2) - (WIN_W / 2),
	"y" : (SCREEN_HEIGHT / 2) - (WIN_H / 2),

	# "ltr" clears the FLAG_RTL the loader stamps on every parent under an ae
	# locale. Without it each child renders at parentW - x - width, which puts the
	# column backdrop on the left and shoves the atlas into the middle -- while the
	# code-created list/minimap, which the loader never touches, stay put.
	# It is per-window and NOT inherited: every dict below that has children
	# repeats it.
	"style" : ("movable", "float", "ltr",),

	"width" : WIN_W,
	"height" : WIN_H,

	"children" :
	(
		{
			"name" : "Board",
			"type" : "board_with_titlebar",
			"x" : 0,
			"y" : 0,
			"width" : WIN_W,
			"height" : WIN_H,
			"title" : "",
			"style" : ("ltr",),

			"children" :
			(
				{
					"name" : "Atlas",
					"type" : "image",
					"x" : BG_X,
					"y" : BG_Y,
					"image" : IMG + "bg.png",
					"style" : ("ltr",),

					"children" :
					(
						# ---------------- REGION CHILDREN ----------------
						# Declared BIGGEST ART FIRST, and it has to stay that way.
						# CWindow::PickWindow walks m_pChildList in reverse, so of two regions
						# whose rects overlap the cursor the LAST one declared takes the click --
						# and IsIn is a plain rect test, with 33-46% of every region's rect being
						# transparent corner. Listing large regions first lets a small map that
						# sits inside a big one's empty corner win its own clicks.
						{
							"name" : "valley_seungryong",
							"type" : "button",
							"x" : 149,
							"y" : 145,
							"default_image" : BTN + "valley1.png",
							"over_image"    : BTN + "valley2.png",
							"down_image"    : BTN + "valley2.png",
							"disable_image" : BTN + "valley1.png",
							"map"     : "map_n_threeway",
							"tooltip" : "MAP_A2",
							"page"    : 1,
						},
						{
							"name" : "land_of_fire",
							"type" : "button",
							"x" : 305,
							"y" : 183,
							"default_image" : BTN + "fireland1.png",
							"over_image"    : BTN + "fireland2.png",
							"down_image"    : BTN + "fireland2.png",
							"disable_image" : BTN + "fireland1.png",
							"map"     : "metin2_map_n_flame_01",
							"tooltip" : "MAP_N_FLAME_01",
							"page"    : 1,
						},
						{
							"name" : "temple_hwang",
							"type" : "button",
							"x" : 249,
							"y" : 221,
							"default_image" : BTN + "temple_1.png",
							"over_image"    : BTN + "temple_2.png",
							"down_image"    : BTN + "temple_2.png",
							"disable_image" : BTN + "temple_1.png",
							"map"     : "metin2_map_milgyo",
							"tooltip" : "MAP_MILGYO",
							"page"    : 1,
						},
						{
							"name" : "ghost_forest",
							"type" : "button",
							"x" : 9,
							"y" : 73,
							"default_image" : BTN + "lungsam1.png",
							"over_image"    : BTN + "lungsam2.png",
							"down_image"    : BTN + "lungsam2.png",
							"disable_image" : BTN + "lungsam1.png",
							"map"     : "metin2_map_trent",
							"tooltip" : "MAP_TRENT",
							"page"    : 1,
						},
						{
							"name" : "monkey_island",
							"type" : "button",
							"x" : 201,
							"y" : 19,
							"default_image" : BTN + "monkey1.png",
							"over_image"    : BTN + "monkey2.png",
							"down_image"    : BTN + "monkey2.png",
							"disable_image" : BTN + "monkey1.png",
							"map"     : "metin2_ape_valley",
							"tooltip" : "MAP_APE_VALLEY",
							"page"    : 1,
						},
						{
							"name" : "desert_yongbi",
							"type" : "button",
							"x" : 147,
							"y" : 250,
							"default_image" : BTN + "desert1.png",
							"over_image"    : BTN + "desert2.png",
							"down_image"    : BTN + "desert2.png",
							"disable_image" : BTN + "desert1.png",
							"map"     : "metin2_map_n_desert_01",
							"tooltip" : "MAP_N_DESERT_01",
							"page"    : 1,
						},
						{
							"name" : "shared_kingdom",
							"type" : "button",
							"x" : 215,
							"y" : 60,
							"default_image" : BTN + "shared2_1.png",
							"over_image"    : BTN + "shared2_2.png",
							"down_image"    : BTN + "shared2_2.png",
							"disable_image" : BTN + "shared2_1.png",
							"map"     : "metin2_map_1",
							"tooltip" : "MAP_SHARED_KINGDOM",
							"page"    : 1,
						},
						{
							"name" : "land_of_giants",
							"type" : "button",
							"x" : 102,
							"y" : 52,
							"default_image" : BTN + "landofgiants1.png",
							"over_image"    : BTN + "landofgiants2.png",
							"down_image"    : BTN + "landofgiants2.png",
							"disable_image" : BTN + "landofgiants1.png",
							"map"     : "metin2_map_nusluck01",
							"tooltip" : "MAP_NUSLUCK01",
							"page"    : 1,
						},
						{
							"name" : "red_forest",
							"type" : "button",
							"x" : 79,
							"y" : 113,
							"default_image" : BTN + "redforest1.png",
							"over_image"    : BTN + "redforest2.png",
							"down_image"    : BTN + "redforest2.png",
							"disable_image" : BTN + "redforest1.png",
							"map"     : "metin2_map_trent02",
							"tooltip" : "MAP_TRENT02",
							"page"    : 1,
						},
						{
							"name" : "mount_sohan",
							"type" : "button",
							"x" : 52,
							"y" : 164,
							"default_image" : BTN + "sohan1.png",
							"over_image"    : BTN + "sohan2.png",
							"down_image"    : BTN + "sohan2.png",
							"disable_image" : BTN + "sohan1.png",
							"map"     : "map_n_snowm_01",
							"tooltip" : "MAP_N_SNOWM_01",
							"page"    : 1,
						},
						{
							"name" : "spider_2",
							"type" : "button",
							"x" : 404,
							"y" : 173,
							"default_image" : BTN + "sd2_1.png",
							"over_image"    : BTN + "sd2_2.png",
							"down_image"    : BTN + "sd2_2.png",
							"disable_image" : BTN + "sd2_1.png",
							"map"     : "metin2_map_spiderdungeon_02",
							"tooltip" : "MAP_SPIDERDUNGEON_02",
							"page"    : 1,
						},
						{
							"name" : "grotto_1",
							"type" : "button",
							"x" : 361,
							"y" : 66,
							"default_image" : BTN + "grotto1_1.png",
							"over_image"    : BTN + "grotto1_2.png",
							"down_image"    : BTN + "grotto1_2.png",
							"disable_image" : BTN + "grotto1_1.png",
							"map"     : "metin2_map_skipia_dungeon_01",
							"tooltip" : "MAP_SKIPIA_DUNGEON_01",
							"page"    : 1,
						},
						{
							"name" : "spider_1",
							"type" : "button",
							"x" : 349,
							"y" : 154,
							"default_image" : BTN + "sd1_1.png",
							"over_image"    : BTN + "sd1_2.png",
							"down_image"    : BTN + "sd1_2.png",
							"disable_image" : BTN + "sd1_1.png",
							"map"     : "metin2_map_spiderdungeon",
							"tooltip" : "MAP_SPIDERDUNGEON",
							"page"    : 1,
						},
						{
							"name" : "grotto_2",
							"type" : "button",
							"x" : 429,
							"y" : 112,
							"default_image" : BTN + "grotto2_1.png",
							"over_image"    : BTN + "grotto2_2.png",
							"down_image"    : BTN + "grotto2_2.png",
							"disable_image" : BTN + "grotto2_1.png",
							"map"     : "metin2_map_skipia_dungeon_02",
							"tooltip" : "MAP_SKIPIA_DUNGEON_02",
							"page"    : 1,
						},
						{
							"name" : "city_red",
							"type" : "button",
							"x" : 270,
							"y" : 118,
							"default_image" : BTN + "newmap2_red1.png",
							"over_image"    : BTN + "newmap2_red2.png",
							"down_image"    : BTN + "newmap2_red2.png",
							"disable_image" : BTN + "newmap2_red1.png",
							"map"     : "metin2_map_a3",
							"tooltip" : "MAP_A3",
							"page"    : 1,
						},
						{
							"name" : "city_yellow",
							"type" : "button",
							"x" : 196,
							"y" : 100,
							"default_image" : BTN + "newmap2_yellow1.png",
							"over_image"    : BTN + "newmap2_yellow2.png",
							"down_image"    : BTN + "newmap2_yellow2.png",
							"disable_image" : BTN + "newmap2_yellow1.png",
							"map"     : "metin2_map_b3",
							"tooltip" : "MAP_B3",
							"page"    : 1,
						},
						{
							"name" : "spider_3",
							"type" : "button",
							"x" : 442,
							"y" : 216,
							"default_image" : BTN + "sd3_1.png",
							"over_image"    : BTN + "sd3_2.png",
							"down_image"    : BTN + "sd3_2.png",
							"disable_image" : BTN + "sd3_1.png",
							"map"     : "metin2_map_spiderdungeon_03",
							"tooltip" : "MAP_SPIDERDUNGEON_03",
							"page"    : 1,
						},
						# -------------- END REGION CHILDREN --------------

						{
							"name" : "ArrowBack",
							"type" : "button",
							"x" : BG_W - ARROW_W * 2 - 10,
							"y" : BG_H - ARROW_H - 6,
							"default_image" : IMG + "arrow_back_1.png",
							"over_image"    : IMG + "arrow_back_2.png",
							"down_image"    : IMG + "arrow_back_3.png",
						},
						{
							"name" : "ArrowForward",
							"type" : "button",
							"x" : BG_W - ARROW_W - 6,
							"y" : BG_H - ARROW_H - 6,
							"default_image" : IMG + "arrow_forward_1.png",
							"over_image"    : IMG + "arrow_forward_2.png",
							"down_image"    : IMG + "arrow_forward_3.png",
						},
					),
				},
				{
					# Backdrop for the whole right column: pickable, it would swallow
					# every click meant for the list rows drawn over it.
					"name" : "ColumnBorder",
					"type" : "image",
					"style" : ("not_pick",),
					"x" : COL_X,
					"y" : BG_Y,
					"image" : IMG + "right_border.png",
				},
			),
		},
	),
}
