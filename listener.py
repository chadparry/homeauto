#!/usr/bin/env python

from __future__ import print_function

import notifications
import ozwd_get_value
import ozwd_util
import spicerack

def listen(handler):
	with ozwd_util.get_thrift_client() as thrift_client, (
			ozwd_util.get_stompy_client()) as stompy_client:
		while True:
			try:
				message = stompy_client.get()

				message_type = notifications.NotificationType(
						int(message.headers['NotificationType'], 16))
				if message_type != notifications.NotificationType.ValueChanged:
					#print(message)
					continue
				try:
					value = int(message.headers['ValueID'], 16)
				except (KeyError, ValueError):
					continue

				position = ozwd_get_value.get_value_refreshed(value, thrift_client, stompy_client)
				handler(value, position, thrift_client, stompy_client)
			except RuntimeError as e:
				print(e)

def print_position(value, position, thrift_client, stompy_client):
	try:
		name = spicerack.Value(value).name
	except ValueError:
		name = hex(value)
	print(name, position)

def main():
	listen(print_position)

if __name__ == "__main__":
	main()
