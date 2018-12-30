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
import Queue
import spicerack
import stompy.frame
import stompy.simple
import threading
import time


NodeDetails = collections.namedtuple('NodeDetails', ['home_id', 'node_id', 'name', 'location', 'product', 'manufacturer', 'values'])
ValueDetails = collections.namedtuple('ValueDetails', ['value_id', 'home_id', 'node_id', 'genre', 'command_class_id', 'instance', 'value_index', 'type', 'label', 'help_text'])


def get_value_details(value, thrift_client):
        (packed_value, unpacked_value_id) = value
	safe_value = OpenZWave.RemoteManager.RemoteValueID(
		unpacked_value_id._homeId,
		ctypes.c_byte(unpacked_value_id._nodeId).value,
		unpacked_value_id._genre,
		ctypes.c_byte(unpacked_value_id._commandClassId).value,
		ctypes.c_byte(unpacked_value_id._instance).value,
		ctypes.c_byte(unpacked_value_id._valueIndex).value,
		unpacked_value_id._type,
	)
	label = thrift_client.GetValueLabel(safe_value)
	help_text = thrift_client.GetValueHelp(safe_value)
	return ValueDetails(
            packed_value,
            ctypes.c_uint32(unpacked_value_id._homeId).value,
            unpacked_value_id._nodeId,
            unpacked_value_id._genre,
            unpacked_value_id._commandClassId,
            unpacked_value_id._instance,
            unpacked_value_id._valueIndex,
            unpacked_value_id._type,
            label,
            help_text,
        )


def get_node_details(home_id, node_id, values, thrift_client):
	name = thrift_client.GetNodeName(home_id, node_id)
	location = thrift_client.GetNodeLocation(home_id, node_id)
	product = thrift_client.GetNodeProductName(home_id, node_id)
	manufacturer = thrift_client.GetNodeManufacturerName(home_id, node_id)
	return NodeDetails(home_id, node_id, name, location, product, manufacturer, [get_value_details(value, thrift_client) for value in values])


def collect_node_details(home_id, node_id, values, queue):
	with ozwd_util.get_thrift_client() as thrift_client:
		details = get_node_details(home_id, node_id, values, thrift_client)
		queue.put(details)


def get_all_nodes_connected(thrift_client, stompy_client):
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
				packed_value = int(message.headers['ValueID'], 16)
				unpacked_value_id = OpenZWave.values.unpackValueID(home_id, packed_value)
				values.add((packed_value, unpacked_value_id))
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

	by_node_id = lambda value: (value[1]._homeId, value[1]._nodeId)
	nodes = itertools.groupby(sorted(values, key=by_node_id), by_node_id)
	return nodes


def get_all_node_details(nodes):
	queue = Queue.Queue()
	threads = [threading.Thread(target=collect_node_details, args=(home_id, node_id, list(values), queue))
		for ((home_id, node_id), values) in nodes]
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()
	details = []
	while not queue.empty():
		details.append(queue.get())
	return details


def get_all_values():
	with ozwd_util.get_thrift_client() as thrift_client, (
			ozwd_util.get_stompy_client()) as stompy_client:
		nodes = get_all_nodes_connected(thrift_client, stompy_client)
		# Close the existing thrift client before creating more on child threads
	return get_all_node_details(nodes)


def main():
	parser = argparse.ArgumentParser(description='List all Z-Wave nodes')
	args = parser.parse_args()

	values = get_all_values()
	for value in values:
		print(value)

if __name__ == "__main__":
	main()
