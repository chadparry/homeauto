#!/usr/bin/env python

import notifications
import stompy.simple

TOPIC = '/topic/zwave/monitor'

stomp = stompy.simple.Client()
with notifications.connection(stomp):
	with notifications.subscription(stomp, TOPIC):
		while True:
			message = stomp.get()
			n = notifications.NotificationType(
					int(message.headers['NotificationType'], 0))
			print('message:', message, n)
