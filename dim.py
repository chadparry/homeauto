#!/usr/bin/env python

import argparse
import OpenZWave.values
import ozwd_get_value
import ozwd_set_value
import ozwd_util
import parsers
import spicerack
import sys

def dim(value, position, filter_min, filter_max,
		dimmer_ramp_time_value=None, dimmer_ramp_time_seconds=None):
	with ozwd_util.get_thrift_client() as thrift_client, (
			ozwd_util.get_stompy_client()) as stompy_client:
		initial = ozwd_get_value.get_value_connected(value, thrift_client, stompy_client)
		matched = ((filter_min is None or initial >= filter_min) and
				(filter_max is None or initial <= filter_max))
		if matched:
			if dimmer_ramp_time_value is not None:
				initial_dimmer_ramp_time_seconds = ozwd_get_value.get_value_connected(
						dimmer_ramp_time_value, thrift_client, stompy_client)
				ozwd_set_value.set_value_connected(
						dimmer_ramp_time_value, dimmer_ramp_time_seconds, thrift_client)
			ozwd_set_value.set_value_connected(value, position, thrift_client)
			if dimmer_ramp_time_value is not None:
				ozwd_set_value.set_value_connected(
						dimmer_ramp_time_value, initial_dimmer_ramp_time_seconds, thrift_client)
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
	parser.add_argument('--dimmer-ramp-time-value', type=parsers.get_enum_parser(spicerack.Value),
			help='Z-Wave value ID for the Dimmer Ramp Time configuration parameter')
	parser.add_argument('--dimmer-ramp-time-seconds', type=parsers.interpreted_int,
			help='Seconds for the dimmer to reach the desired position')
	args = parser.parse_args()
	if (args.dimmer_ramp_time_seconds is not None and
			args.dimmer_ramp_time_value is None):
		parser.error('The --dimmer-ramp-time-seconds argument requires the --dimmer-ramp-time-value argument')

	matched = dim(args.value, args.position, args.filter_min, args.filter_max,
			args.dimmer_ramp_time_value, args.dimmer_ramp_time_seconds)
	if not matched:
		sys.exit(1)

if __name__ == "__main__":
	main()
