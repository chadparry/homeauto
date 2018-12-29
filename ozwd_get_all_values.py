#!/usr/bin/env python

from __future__ import print_function

import argparse
import collections
import ctypes
import itertools
import notifications
import OpenZWave.RemoteManager
import OpenZWave.values
import ozwd_util
import spicerack
import stompy.frame
import stompy.simple
import time


NodeDetails = collections.namedtuple('NodeDetails', ['home_id', 'node_id', 'name', 'location', 'product', 'manufacturer', 'values'])
ValueDetails = collections.namedtuple('ValueDetails', ['home_id', 'node_id', 'genre', 'command_class_id', 'instance', 'value_index', 'type', 'label', 'help_text'])


def get_value_details(value, thrift_client):
	# RemoteValueID(_type=7, _instance=1L, _valueIndex=2, _nodeId=7, _commandClassId=134, _homeId=-721303855, _genre=3)
	safe_value = OpenZWave.RemoteManager.RemoteValueID(
		value._homeId,
		ctypes.c_byte(value._nodeId).value,
		value._genre,
		ctypes.c_byte(value._commandClassId).value,
		ctypes.c_byte(value._instance).value,
		ctypes.c_byte(value._valueIndex).value,
		value._type,
	)
	label = thrift_client.GetValueLabel(safe_value)
	help_text = thrift_client.GetValueHelp(safe_value)
	return ValueDetails(value._homeId, value._nodeId, value._genre, value._commandClassId, value._instance, value._valueIndex, value._type, label, help_text)


def get_node_details(home_id, node_id, values, thrift_client):
	name = thrift_client.GetNodeName(home_id, node_id)
	location = thrift_client.GetNodeLocation(home_id, node_id)
	product = thrift_client.GetNodeProductName(home_id, node_id)
	manufacturer = thrift_client.GetNodeManufacturerName(home_id, node_id)
	return NodeDetails(home_id, node_id, name, location, product, manufacturer, [get_value_details(value, thrift_client) for value in values])


def get_all_values_connected(thrift_client, stompy_client):
	# List all the values.
	thrift_client.SendAllValues()

	# Create a timeout for an async event.
	#signal.signal(signal.SIGALRM, handle_timeout)
	#signal.alarm(REFRESH_TIMEOUT_SEC)
	values = set()

	# Wait for the async event.
	while True:
		try:
			message = stompy_client.get(block=not values)
			found = True
			# FIXME: Filter events based on some field.
			#message_type = notifications.NotificationType(
			#		int(message.headers['NotificationType'], 16))
			#if message_type != notifications.NotificationType.ValueChanged:
			#	continue
			try:
				home_id = int(message.headers['HomeID'], 16)
				message_value = int(message.headers['ValueID'], 16)
				unpacked_value_id = OpenZWave.values.unpackValueID(home_id, message_value)
				values.add(unpacked_value_id)
			except (KeyError, ValueError):
				continue
			# FIXME: Add an event parameter that counts the values so we know when to stop.
			if False:
				# The anticipated operation has completed.
				break
		except (stompy.simple.Empty, stompy.frame.UnknownBrokerResponseError):
			if found:
				found = False
				time.sleep(1)
			else:
				break

	by_node_id = lambda value: (value._homeId, value._nodeId)
	nodes = itertools.groupby(sorted(values, key=by_node_id), by_node_id)
	details = [get_node_details(home_id, node_id, values, thrift_client) for ((home_id, node_id), values) in nodes]
	return details

def get_all_values():
	with ozwd_util.get_thrift_client() as thrift_client, (
			ozwd_util.get_stompy_client()) as stompy_client:
		return get_all_values_connected(thrift_client, stompy_client)

def main():
	parser = argparse.ArgumentParser(description='List all Z-Wave nodes')
	args = parser.parse_args()

	values = get_all_values()
	for value in values:
		print(value)

if __name__ == "__main__":
	main()
