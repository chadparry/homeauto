#!/usr/bin/env python

from __future__ import print_function

import notifications
import OpenZWave.values
import ozwd_util
import spicerack

def get_value_connected(value, thrift_client, stompy_client):
	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.HOME_ID, value)

	# Refresh the cached value.
	thrift_client.RefreshValue(unpacked_value_id)

	while True:
		message = stompy_client.get()
		message_type = notifications.NotificationType(
				int(message.headers['NotificationType'], 16))
		if message_type != notifications.NotificationType.ValueChanged:
			continue
		try:
			message_value = int(message.headers['ValueID'], 16)
		except (KeyError, ValueError):
			continue
		if message_value != value:
			continue

		# The anticipated operation has completed.
		break

	# Get the updated value.
	getter = GETTERS[unpacked_value_id._type]
	result = getter(thrift_client, unpacked_value_id)
	if not result.retval:
		raise RuntimeError('Failed to get value')
	return result.o_value

def main():
	with ozwd_util.get_thrift_client() as thrift_client, (
			ozwd_util.get_stompy_client()) as stompy_client:
		while True:
			message = stompy_client.get()
			message_type = notifications.NotificationType(
					int(message.headers['NotificationType'], 16))
			if message_type != notifications.NotificationType.ValueChanged:
				continue

if __name__ == "__main__":
	main()
