#!/usr/bin/env python

import OpenZWave.values
import ozwd_util
import spicerack

DIMMERS = (
	spicerack.Value.FRONT_BEDROOM,
	spicerack.Value.FRONT_FAIRY,
	spicerack.Value.SIDE_BEDROOM,
	spicerack.Value.SIDE_FAIRY,
	spicerack.Value.KIDS_BATHROOM,
)
LEVEL = 30

def get_level(client, value):
	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.home_id, value.value)
	result = client.GetValueAsByte(unpacked_value_id)
	assert result.retval
	return result.o_value

def set_level(client, value, level):
	print('setting', value, level)
	unpacked_value_id = OpenZWave.values.unpackValueID(spicerack.home_id, value.value)
	client.SetValue_UInt8(unpacked_value_id, level)

with ozwd_util.get_client() as client:
	initials = {value: get_level(client, value) for value in DIMMERS}
	for value in DIMMERS:
		if initials[value] > LEVEL:
			set_level(client, value, LEVEL)
