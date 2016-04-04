#!/usr/bin/env python

import argparse
import OpenZWave.values
import ozwd_util
import parsers
import spicerack
import sys

def get_level(client, value):
	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.home_id, value)
	result = client.GetValueAsByte(unpacked_value_id)
	if not result.retval:
		raise RuntimeError('Failed to get value')
	return result.o_value

def set_level(client, value, level):
	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.home_id, value)
	success = client.SetValue_UInt8(unpacked_value_id, level)
	if not success:
		raise RuntimeError('Failed to set value')

def dim(value, position, filter_min, filter_max):
	with ozwd_util.get_client() as client:
		initial = get_level(client, value)
		matched = ((filter_min is None or initial >= filter_min) and
				(filter_max is None or initial <= filter_max))
		if matched:
			set_level(client, value, position)
		return matched

def main():
	parser = argparse.ArgumentParser(description='Control a Z-Wave dimmer')
	parser.add_argument('--value', type=parsers.get_enum_parser(spicerack.Value), required=True,
			help='Z-Wave value ID')
	parser.add_argument('--position', type=parsers.interpreted_int, required=True,
			help='Desired value position')
	parser.add_argument('--filter-min', type=parsers.interpreted_int,
			help='Minimum initial value for dimming to proceed')
	parser.add_argument('--filter-max', type=parsers.interpreted_int,
			help='Maximum initial value for dimming to proceed')
	args = parser.parse_args()

	matched = dim(args.value, args.position, args.filter_min, args.filter_max)
	if not matched:
		sys.exit(1)

if __name__ == "__main__":
	main()
