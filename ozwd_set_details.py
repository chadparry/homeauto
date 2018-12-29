#!/usr/bin/env python

from __future__ import print_function

import argparse
import OpenZWave.values
import ozwd_util
import parsers
import spicerack


def set_details_connected(value, name, location, thrift_client):
	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.HOME_ID, value)

	if name is not None:
		thrift_client.SetNodeName(unpacked_value_id._homeId, unpacked_value_id._nodeId, name)

	if location is not None:
		thrift_client.SetNodeLocation(unpacked_value_id._homeId, unpacked_value_id._nodeId, location)

	thrift_client.WriteConfig(unpacked_value_id._homeId)


def set_details(value, name, location):
	with ozwd_util.get_thrift_client() as thrift_client:
		return set_details_connected(value, name, location, thrift_client)


def main():
	parser = argparse.ArgumentParser(description='Set details for a Z-Wave node')
	parser.add_argument('--value', type=parsers.get_enum_parser(spicerack.Value), required=True,
			help='Z-Wave value ID')
	parser.add_argument('--name',
			help='print format')
	parser.add_argument('--location',
			help='print format')
	args = parser.parse_args()
	if args.name is None and args.location is None:
		raise ValueError('No details provided')

	set_details(args.value, args.name, args.location)


if __name__ == "__main__":
	main()
