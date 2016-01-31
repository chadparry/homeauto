#!/usr/bin/env python

import argparse
import contextlib
import OpenZWave.RemoteManager
import OpenZWave.values
import ozwd_util
import spicerack
import thrift.protocol.TBinaryProtocol
import thrift.transport.TSocket
import thrift.transport.TTransport

def bool_parser(x):
	values = {
		'off': False,
		'on': True,
		'0': False,
		'1': True,
	}
	return values[x]
def int_parser(x):
	return int(x, 0)

PARSERS = {
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Bool: bool_parser,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Byte: int_parser,
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Decimal: str,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Int: int_parser,
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_List: str,
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Schedule: str,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Short: int_parser,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_String: str,
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Button: str,
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Raw: str,
}
SETTERS = {
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Bool: OpenZWave.RemoteManager.Client.SetValue_Bool,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Byte: OpenZWave.RemoteManager.Client.SetValue_UInt8,
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Decimal: OpenZWave.RemoteManager.Client.SetValue_Decimal,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Int: OpenZWave.RemoteManager.Client.SetValue_int32,
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_List: OpenZWave.RemoteManager.Client.SetValue_List,
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Schedule: OpenZWave.RemoteManager.Client.SetValue_Schedule,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Short: OpenZWave.RemoteManager.Client.SetValue_int16,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_String: OpenZWave.RemoteManager.Client.SetValue_String,
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Button: OpenZWave.RemoteManager.Client.SetValue_Button,
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Raw: OpenZWave.RemoteManager.Client.SetValue_Raw,
}

def interpreted_value(x):
	if hasattr(spicerack.Value, x):
		return spicerack.Value[x].value
	return long(x, 0)

def set_value(value, position):
	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.home_id, value)
	setter = SETTERS[unpacked_value_id._type]

	with ozwd_util.get_client() as client:
		setter(client, unpacked_value_id, position)

def main():
	parser = argparse.ArgumentParser(description='Control Z-Wave nodes')
	parser.add_argument('--value', type=interpreted_value, required=True,
			help='Z-Wave value ID')
	parser.add_argument('--position', required=True,
			help='Desired value position')
	args = parser.parse_args()

	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.home_id, args.value)
	parser = PARSERS[unpacked_value_id._type]
	parsed = parser(args.position)

	set_value(args.value, parsed)

if __name__ == "__main__":
    main()
