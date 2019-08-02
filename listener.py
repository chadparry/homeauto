#!/usr/bin/env python

from __future__ import print_function

import notifications
import ozwd_get_value
import ozwd_util
import spicerack
import stompy.frame
import struct
import traceback

def listen(handler):
	with ozwd_util.get_stompy_client(ozwd_util.STOMP_TOPIC) as stompy_client:
		while True:
			try:
				message = stompy_client.get()
				# Allow other clients to process this message
				rebound_headers = message.headers.copy()
				rebound_headers.pop('destination', None)
				stompy_client.put(message.body, ozwd_util.STOMP_REBOUND_TOPIC, False, rebound_headers)

				notification_type = message.headers.get('NotificationType')
				message_type = notifications.NotificationType(int(notification_type, 16)) if notification_type else None
				if message_type != notifications.NotificationType.ValueChanged:
					#print(message)
					continue
				try:
					value = int(message.headers['ValueID'], 16)
				except (KeyError, ValueError):
					continue

				with ozwd_util.get_thrift_client() as thrift_client:
					position = ozwd_get_value.get_value_refreshed(value, thrift_client)
				handler(value, position, stompy_client)
			except stompy.frame.UnknownBrokerResponseError:
				# The queue may be corrupt
				raise
			except struct.error:
				# A message may be corrupt
				pass
			except Exception as e:
				traceback.print_exc()

def print_position(value, position, stompy_client):
	try:
		name = spicerack.Value(value).name
	except ValueError:
		name = hex(value)
	print(name, position)

def main():
	listen(print_position)

if __name__ == "__main__":
	main()
