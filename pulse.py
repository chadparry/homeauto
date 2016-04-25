#!/usr/bin/env python

import argparse
import OpenZWave.values
import ozwd_get_value
import ozwd_set_value
import ozwd_util
from six.moves import range
import parsers
import spicerack
import time

def pulse(value):
	with ozwd_util.get_thrift_client() as thrift_client, (
			ozwd_util.get_stompy_client()) as stompy_client:
		initial = ozwd_get_value.get_value_connected(value, thrift_client, stompy_client)
		if initial > 0:
			first = True
			for _rep in range(2):
				if first:
					first = False
				else:
					time.sleep(2)

				ozwd_set_value.set_value_connected(value, 0, thrift_client)

				time.sleep(3)

				ozwd_set_value.set_value_connected(value, initial, thrift_client)

def main():
	parser = argparse.ArgumentParser(description='Pulse a Z-Wave dimmer')
	parser.add_argument('--value', type=parsers.get_enum_parser(spicerack.Value), required=True,
			help='Z-Wave value ID')
	args = parser.parse_args()

	pulse(args.value)

if __name__ == "__main__":
	main()
