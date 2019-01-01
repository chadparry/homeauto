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
import sortedcontainers
import spicerack
import stompy.frame
import stompy.simple
import threading
import time


NodeDetails = collections.namedtuple('NodeDetails', ['home_id', 'node_id', 'name', 'location', 'product', 'manufacturer', 'values'])
ValueDetails = collections.namedtuple('ValueDetails', ['value_id', 'home_id', 'node_id', 'genre', 'command_class_id', 'instance', 'value_index', 'type', 'label'])


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
	)


def get_node_details(home_id, node_id, thrift_client):
	home_id_signed = ctypes.c_int32(home_id).value
	name = thrift_client.GetNodeName(home_id_signed, node_id)
	location = thrift_client.GetNodeLocation(home_id_signed, node_id)
	product = thrift_client.GetNodeProductName(home_id_signed, node_id)
	manufacturer = thrift_client.GetNodeManufacturerName(home_id_signed, node_id)
	return NodeDetails(home_id, node_id, name, location, product, manufacturer,
		sortedcontainers.SortedList())


def collect_node_details(home_id, node_id, queue):
	with ozwd_util.get_thrift_client() as thrift_client:
		details = get_node_details(home_id, node_id, thrift_client)
		queue.put(details)


def collect_value_details(value, queue):
	with ozwd_util.get_thrift_client() as thrift_client:
		details = get_value_details(value, thrift_client)
		queue.put(details)


def get_all_nodes_connected(filter_user_genre, thrift_client, stompy_client):
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
				if not filter_user_genre or unpacked_value_id._genre == OpenZWave.ttypes.RemoteValueGenre.ValueGenre_User:
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

	by_node_id = lambda value: (ctypes.c_uint32(value[1]._homeId).value, value[1]._nodeId)
	nodes_lazy = itertools.groupby(sorted(values, key=by_node_id), by_node_id)
	nodes = [(key, list(values)) for (key, values) in nodes_lazy]
	return nodes


def get_all_node_details(nodes):
	node_queue = Queue.Queue()
	value_queue = Queue.Queue()
	threads = (
		[threading.Thread(target=collect_node_details, args=(home_id, node_id, node_queue))
			for ((home_id, node_id), values) in nodes] +
		[threading.Thread(target=collect_value_details, args=(value, value_queue))
			for ((home_id, node_id), values) in nodes
			for value in values]
	)
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()
	node_details = sortedcontainers.SortedDict()
	while not node_queue.empty():
		node = node_queue.get()
		node_details[(node.home_id, node.node_id)] = node
	while not value_queue.empty():
		value = value_queue.get()
		node_details[(value.home_id, value.node_id)].values.add(value)
	return node_details.values()


def get_all_values(filter_user_genre):
	with ozwd_util.get_thrift_client() as thrift_client, (
			ozwd_util.get_stompy_client()) as stompy_client:
		nodes = get_all_nodes_connected(filter_user_genre, thrift_client, stompy_client)
		# Close the existing thrift client before creating more on child threads
	return get_all_node_details(nodes)


def main():
	parser = argparse.ArgumentParser(description='List all Z-Wave nodes')
	parser.add_argument('--filter-user-genre', action='store_true',
		help='Only return values in the User genre')
	args = parser.parse_args()

	values = get_all_values(args.filter_user_genre)
	for value in values:
		print(value)


if __name__ == "__main__":
	main()
