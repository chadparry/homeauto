#!/usr/bin/env python

import notifications
import spicerack
import stompy.simple

TOPIC = '/topic/zwave/monitor'

stomp = stompy.simple.Client()
with notifications.connection(stomp):
	with notifications.subscription(stomp, TOPIC):
		while True:
			message = stomp.get()
			n = notifications.NotificationType(
					int(message.headers['NotificationType'], 0))
			try:
				v = spicerack.Value(int(message.headers['ValueID'], 0))
			except (KeyError, ValueError):
				pass
			print('message:', message.headers, message.body)

"""
('message:', <Frame {'HomeID': '0xd501c6d1',
 'NotificationByte': '0',
 'NotificationNodeId': '0x2',
 'NotificationType': '0x2',
 'ValueID': '0x100000002494000',   
 'destination': '/topic/zwave/monitor',
 'message-id': 'msg-#stompcma-23'}>, <NotificationType.Group: 2>)
('message:', <Frame {'NotificationByte': '0',
 'NotificationNodeId': '0x2',
 'NotificationType': '0x16',
 'destination': '/topic/zwave/monitor',
 'message-id': 'msg-#stompcma-24'}>, <NotificationType.ButtonOff: 22>)
"""
