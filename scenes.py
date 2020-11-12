#!/usr/bin/env python

import collections
import fcntl
import itertools
import listener
import ozwd_set_value
import ozwd_util
#import slow_dim
import spicerack


class SetAction:
	def __init__(self, name, position):
		self.name = name
		self.position = position
	def handle(self, source_name, source_position, thrift_client):
		ozwd_set_value.set_value_connected(self.name.value, self.position, thrift_client)


class SlowDimUpstairsBathroomAction:
	def handle(self, source_name, source_position, thrift_client):
		slow_dim.record(source_position)


TRIGGERS = {
	(spicerack.Value.MASTER_TRIGGER, True): [
		SetAction(spicerack.Value.MASTER_WINDOWSIDE_NIGHTSTAND, 99),
		SetAction(spicerack.Value.MASTER_WALLSIDE_NIGHTSTAND, 99),
		SetAction(spicerack.Value.MASTER_LAMP, True),
	],
	(spicerack.Value.MASTER_TRIGGER, False): [
		SetAction(spicerack.Value.MASTER_WINDOWSIDE_NIGHTSTAND, 0),
		SetAction(spicerack.Value.MASTER_WALLSIDE_NIGHTSTAND, 0),
		SetAction(spicerack.Value.MASTER_LAMP, False),
	],
	(spicerack.Value.STUDY, True): [SetAction(spicerack.Value.STUDY_LAMP, 99)],
	(spicerack.Value.STUDY, False): [SetAction(spicerack.Value.STUDY_LAMP, 0)],
	(spicerack.Value.LIVING_ROOM, True): [SetAction(spicerack.Value.LIVING_ROOM_LAMP, 99)],
	(spicerack.Value.LIVING_ROOM, False): [SetAction(spicerack.Value.LIVING_ROOM_LAMP, 0)],
	(spicerack.Value.UPSTAIRS_BATHROOM,): [SlowDimUpstairsBathroomAction()],
}


def match_scenes(value, position, thrift_client, stompy_client):
	try:
		name = spicerack.Value(value)
	except ValueError:
		return

	triggers = itertools.chain(
		TRIGGERS.get((name, position), []),
		TRIGGERS.get((name,), []),
	)
	for trigger in triggers:
		trigger.handle(name, position, thrift_client)


def main():
	listener.listen(match_scenes)


if __name__ == "__main__":
	main()
