#!/usr/bin/env python

import argparse
import OpenZWave.values
import ozwd_util
from six.moves import range
import parsers
import spicerack
import time

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

def pulse(value):
	with ozwd_util.get_client() as client:
		initial = get_level(client, value)
		if initial > 0:
			first = True
			for _rep in range(2):
				if first:
					first = False
				else:
					time.sleep(2)

				set_level(client, value, 0)

				time.sleep(3)

				set_level(client, value, initial)

def main():
	parser = argparse.ArgumentParser(description='Pulse a Z-Wave dimmer')
	parser.add_argument('--value', type=parsers.get_enum_parser(spicerack.Value), required=True,
			help='Z-Wave value ID')
	args = parser.parse_args()

	pulse(args.value)

if __name__ == "__main__":
	main()
