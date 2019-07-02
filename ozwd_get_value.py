#!/usr/bin/env python

from __future__ import print_function

import argparse
import notifications
import OpenZWave.RemoteManager
import OpenZWave.values
import ozwd_util
import parsers
import signal
import spicerack

REFRESH_TIMEOUT_SEC = 10

GETTERS = {
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Bool: OpenZWave.RemoteManager.Client.GetValueAsBool,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Byte: OpenZWave.RemoteManager.Client.GetValueAsByte,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Decimal: OpenZWave.RemoteManager.Client.GetValueAsFloat,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Int: OpenZWave.RemoteManager.Client.GetValueAsInt,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Short: OpenZWave.RemoteManager.Client.GetValueAsShort,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_String: OpenZWave.RemoteManager.Client.GetValueAsString,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Button: OpenZWave.RemoteManager.Client.GetValueAsBool,
}

def escape(s):
	try:
		# First try Python 2 escaping.
		return s.decode('string_escape')
	except AttributeError:
		# Fall back to Python 3 escaping.
		return bytes(s, 'utf-8').decode('unicode_escape')

def handle_timeout(signum, frame):
	raise RuntimeError('Failed to receive refresh notification')

def get_value_connected(value, thrift_client, stompy_client):
	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.HOME_ID, value)

	# Refresh the cached value.
	thrift_client.RefreshValue(unpacked_value_id)

	# Create a timeout for an async event.
	signal.signal(signal.SIGALRM, handle_timeout)
	signal.alarm(REFRESH_TIMEOUT_SEC)
	try:
		# Wait for the async event.
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
	finally:
		signal.alarm(0)

	return get_value_refreshed(value, thrift_client)

def get_value_refreshed(value, thrift_client):
	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.HOME_ID, value)
	getter = GETTERS[unpacked_value_id._type]
	result = getter(thrift_client, unpacked_value_id)
	if not result.retval:
		raise RuntimeError('Failed to get value')
	return result.o_value

def get_value(value):
	with ozwd_util.get_thrift_client() as thrift_client, (
			ozwd_util.get_stompy_client()) as stompy_client:
		return get_value_connected(value, thrift_client, stompy_client)

def main():
	parser = argparse.ArgumentParser(description='Query a Z-Wave node')
	parser.add_argument('--value', type=parsers.get_enum_parser(spicerack.Value), required=True,
			help='Z-Wave value ID')
	parser.add_argument('--format', default=r'%s\n',
			help='print format')
	args = parser.parse_args()

	position = get_value(args.value)
	print(escape(args.format) % (position,), end='')

if __name__ == "__main__":
	main()
