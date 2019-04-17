#!/usr/bin/env python

import argparse
import contextlib
import OpenZWave.RemoteManager
import OpenZWave.values
import ozwd_util
import parsers
import spicerack

PARSERS = {
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Bool: parsers.interpreted_bool,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Byte: parsers.interpreted_int,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Decimal: float,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Int: parsers.interpreted_int,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_List: str,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Short: parsers.interpreted_int,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_String: str,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Button: parsers.interpreted_bool,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Raw: bytes,
}
SETTERS = {
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Bool: OpenZWave.RemoteManager.Client.SetValue_Bool,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Byte: OpenZWave.RemoteManager.Client.SetValue_UInt8,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Decimal: OpenZWave.RemoteManager.Client.SetValue_Float,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Int: OpenZWave.RemoteManager.Client.SetValue_int32,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_List: OpenZWave.RemoteManager.Client.SetValueListSelection,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Short: OpenZWave.RemoteManager.Client.SetValue_int16,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_String: OpenZWave.RemoteManager.Client.SetValue_String,
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Button: OpenZWave.RemoteManager.Client.SetValue_Bool,
}

def set_value_connected(value, position, thrift_client):
	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.HOME_ID, value)
	setter = SETTERS[unpacked_value_id._type]
	success = setter(thrift_client, unpacked_value_id, position)
	if not success:
		raise RuntimeError('Failed to set value')

def set_value(value, position):
	with ozwd_util.get_thrift_client() as thrift_client:
		return set_value_connected(value, position, thrift_client)

def main():
	parser = argparse.ArgumentParser(description='Control a Z-Wave node')
	parser.add_argument('--value', type=parsers.get_enum_parser(spicerack.Value), required=True,
			help='Z-Wave value ID')
	parser.add_argument('--position', required=True,
			help='Desired value position')
	args = parser.parse_args()

	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.HOME_ID, args.value)
	parser = PARSERS[unpacked_value_id._type]
	parsed = parser(args.position)

	set_value(args.value, parsed)

if __name__ == "__main__":
	main()
