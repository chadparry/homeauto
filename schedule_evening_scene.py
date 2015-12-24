#!/usr/bin/env python

import astral
import at
import datetime
import spicerack
import variates

OZWD_SET_VALUE_BIN = '/usr/local/src/homeauto/ozwd_set_value.py'
OZWD_SET_VALUE_CMD = [
	OZWD_SET_VALUE_BIN,
	'--value=' + '0x{:X}'.format(spicerack.Value.GARAGE_OUTLET.value),
]

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

on = variates.variate_datetime(
		mode=spicerack.location.sunset(today),
		stdev=datetime.timedelta(minutes=10),
		min=spicerack.location.solar_noon(today))
off = variates.variate_datetime(
		mode=datetime.datetime.combine(tomorrow,
			datetime.time(hour=0, minute=30, tzinfo=spicerack.tzinfo)),
		stdev=datetime.timedelta(minutes=30),
		max=spicerack.location.solar_noon(tomorrow))
min_duration = variates.variate_timedelta(
		mode=datetime.timedelta(hours=2),
		stdev=datetime.timedelta(minutes=30),
		min=datetime.timedelta(0))

if off - on >= min_duration:
	at.schedule(on, OZWD_SET_VALUE_CMD + ['--position=on'])
	at.schedule(off, OZWD_SET_VALUE_CMD + ['--position=off'])
