#!/usr/bin/env python

from __future__ import print_function

import argparse
import contextlib
import OpenZWave.RemoteManager
import OpenZWave.values
import ozwd_util
import parsers
import spicerack
import thrift.protocol.TBinaryProtocol
import thrift.transport.TSocket
import thrift.transport.TTransport

GETTERS = {
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Bool: OpenZWave.RemoteManager.Client.GetValueAsBool,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Byte: OpenZWave.RemoteManager.Client.GetValueAsByte,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Decimal: OpenZWave.RemoteManager.Client.GetValueAsFloat,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Int: OpenZWave.RemoteManager.Client.GetValueAsInt,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Short: OpenZWave.RemoteManager.Client.GetValueAsShort,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_String: OpenZWave.RemoteManager.Client.GetValueAsString,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Button: OpenZWave.RemoteManager.Client.GetValueAsBool,
}

def get_value(value):
	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.home_id, value)
	getter = GETTERS[unpacked_value_id._type]

	with ozwd_util.get_client() as client:
		result = getter(client, unpacked_value_id)
		if not result.retval:
			raise RuntimeError('Failed to get value')
		return result.o_value

def escape(s):
	try:
		# First try Python 2 escaping.
		return s.decode('string_escape')
	except AttributeError:
		# Fall back to Python 3 escaping.
		return bytes(s, 'utf-8').decode('unicode_escape')

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
