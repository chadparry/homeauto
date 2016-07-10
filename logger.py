#!/usr/bin/env python

import datetime
import logging
import notifications
import OpenZWave.values
import ozwd_util
import spicerack

def get_name(value):
	if value is not None:
		try:
			return spicerack.Value(value)
		except ValueError:
			pass
	return None

def get_unpacked(value):
	if value is not None:
		try:
			return OpenZWave.values.unpackValueID(spicerack.HOME_ID, value)
		except ValueError:
			pass
	return None

with ozwd_util.get_stompy_client() as stompy_client:
	while True:
		message = stompy_client.get()
		notification = notifications.NotificationType(
				int(message.headers['NotificationType'], 16))
		try:
			value = int(message.headers['ValueID'], 16)
		except KeyError:
			# Not all messages are associated with a value.
			value = None
		name = get_name(value)
		unpacked = get_unpacked(value)
		logging.info('message at %s: %s, %s, %s, %s, %s', str(datetime.datetime.now()), message.headers, message.body, notification, name, unpacked)
