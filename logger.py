#!/usr/bin/env python

import notifications
import OpenZWave.values
import spicerack
import stompy.simple

TOPIC = '/topic/zwave/monitor'

stomp = stompy.simple.Client()
with notifications.connection(stomp):
	with notifications.subscription(stomp, TOPIC):
		while True:
			message = stomp.get()
			node = notifications.NotificationType(
					int(message.headers['NotificationType'], 0))
			try:
				value = spicerack.Value(int(message.headers['ValueID'], 0))
			except (KeyError, ValueError):
				value = None
			try:
				unpacked = OpenZWave.values.unpackValueID(spicerack.home_id, int(message.headers['ValueID'], 0))
			except (KeyError, ValueError):
				unpacked = None
			print('message:', message.headers, message.body, node, value, unpacked)
