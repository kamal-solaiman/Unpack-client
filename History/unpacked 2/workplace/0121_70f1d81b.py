# coding: utf-8
import app

import localeinfo

TEST_SERVER = 0
LIVE_SERVER_KEY = 1
SPEED_SERVER_KEY = 2

infoID = 1

PORT_LIVE = 26000 if TEST_SERVER else 26000
PORT_SPEED = 24000 if TEST_SERVER else 28000

# PORT_LIVE = 30000
# PORT_SPEED = 32000

infoDict = {\
				LIVE_SERVER_KEY : {\
						"name" : localeinfo.LIVE_SERVER_NAME,
						"ip" : "51.77.222.0" if TEST_SERVER == 1 else "162.19.94.224",
						"auth" : PORT_LIVE + 10,
						"ch1" : PORT_LIVE + 30,
						"ch2" : PORT_LIVE + 110,
						"ch3" : PORT_LIVE + 190,
						"ch4" : PORT_LIVE + 270,
						"ch99" : PORT_LIVE + 350,
						"mark" : "10.tga",
						"symbol_path" : "10",
				},
				SPEED_SERVER_KEY : {\
						"name" : localeinfo.SPEED_SERVER_NAME,
						"ip" : "51.77.222.0" if TEST_SERVER == 1 else "51.77.222.0",
						"auth" : PORT_LIVE + 10,
						"ch1" : PORT_LIVE + 30,
						"ch2" : PORT_LIVE + 110,
						"ch3" : PORT_LIVE + 190,
						"ch4" : PORT_LIVE + 270,
						"ch99" : PORT_LIVE + 350,
						"mark" : "20.tga",
						"symbol_path" : "20",
				},
				# SPEED_SERVER_KEY : {\
						# "name" : localeinfo.SPEED_SERVER_NAME,
						# "ip" : "51.77.222.0" if TEST_SERVER == 1 else "162.19.94.224",
						# "auth" : PORT_SPEED + 10,
						# "ch1" : PORT_SPEED + 30,
						# "ch2" : PORT_SPEED + 110,
						# "ch3" : PORT_SPEED + 190,
						# "ch4" : PORT_SPEED + 270,
						# "ch99" : PORT_SPEED + 350,
						# "mark" : "20.tga",
						# "symbol_path" : "20",
				# },
}

def GetServerID():
	global infoID
	return infoID
