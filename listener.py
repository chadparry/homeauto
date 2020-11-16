#!/usr/bin/env python

from __future__ import print_function

import notifications
import OpenZWave.ttypes
import ozwd_get_value
import ozwd_util
import socket
import spicerack
import stompy.frame
import struct
import time
import traceback


def listen(handler):
	with ozwd_util.get_thrift_client() as thrift_client, (
			ozwd_util.get_stompy_client(ozwd_util.STOMP_TOPIC)) as stompy_client:
		while True:
			try:
				message = stompy_client.get()
				#print(repr(message))
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
				unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.HOME_ID, value)
				if unpacked_value_id._genre != OpenZWave.ttypes.RemoteValueGenre.ValueGenre_User:
					#print(message)
					continue

				handler(value, thrift_client, stompy_client)
			except stompy.frame.UnknownBrokerResponseError:
				# The queue may be corrupt
				time.sleep(1)
			except socket.error:
				# A channel may be closed
				pass
			except struct.error:
				# A message may be corrupt
				pass
			except Exception as e:
				traceback.print_exc()


def print_position(value, thrift_client, stompy_client):
	try:
		name = spicerack.Value(value).name
	except ValueError:
		name = hex(value)
	position = ozwd_get_value.get_value_refreshed(value, thrift_client)
	print(name, position)


def main():
	listen(print_position)


if __name__ == "__main__":
	main()
