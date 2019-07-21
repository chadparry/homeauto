#!/usr/bin/env python

import listener
import ozwd_set_value
import ozwd_util
import spicerack

TRIGGERS = {
	(spicerack.Value.MASTER_WINDOWSIDE_NIGHTSTAND, True): [(spicerack.Value.MASTER_WALLSIDE_NIGHTSTAND, True)],
	(spicerack.Value.MASTER_WINDOWSIDE_NIGHTSTAND, False): [(spicerack.Value.MASTER_WALLSIDE_NIGHTSTAND, False)],
	(spicerack.Value.STUDY, True): [(spicerack.Value.STUDY_LAMP, 99)],
	(spicerack.Value.STUDY, False): [(spicerack.Value.STUDY_LAMP, 0)],
	(spicerack.Value.LIVING_ROOM, True): [(spicerack.Value.LIVING_ROOM_LAMP, 99)],
	(spicerack.Value.LIVING_ROOM, False): [(spicerack.Value.LIVING_ROOM_LAMP, 0)],
}

def match_scenes(value, position, stompy_client):
	try:
		name = spicerack.Value(value)
	except ValueError:
		return

	triggers = TRIGGERS.get((name, position), [])
	with ozwd_util.get_thrift_client() as thrift_client:
		for (trigger_name, trigger_position) in triggers:
			ozwd_set_value.set_value_connected(trigger_name.value, trigger_position, thrift_client)

def main():
	listener.listen(match_scenes)

if __name__ == "__main__":
	main()
