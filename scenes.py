#!/usr/bin/env python

import listener
import ozwd_set_value
import spicerack

TRIGGERS = {
	(spicerack.Value.MASTER_WINDOWSIDE_NIGHTSTAND, True): [(spicerack.Value.MASTER_WALLSIDE_NIGHTSTAND, True)],
	(spicerack.Value.MASTER_WINDOWSIDE_NIGHTSTAND, False): [(spicerack.Value.MASTER_WALLSIDE_NIGHTSTAND, False)],
}

def match_scenes(value, position, thrift_client, stompy_client):
	try:
		name = spicerack.Value(value)
	except ValueError:
		return

	triggers = TRIGGERS.get((name, position), [])
	for (trigger_name, trigger_position) in triggers:
		ozwd_set_value.set_value_connected(trigger_name.value, trigger_position, thrift_client)

def main():
	listener.listen(match_scenes)

if __name__ == "__main__":
	main()
