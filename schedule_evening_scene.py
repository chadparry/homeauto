#!/usr/bin/env python3

import astral
import at
import datetime
import pytz
import spicerack
import variates

DEVICE = '/dev/ttyUSB0'
CONFIG_PATH = '/home/homeauto/share/openzwave/config'
USER_PATH = '/home/homeauto/openzwave'
OZW_BIN = '/usr/local/bin/ozwsh'
OZW_CMD = [
	OZW_BIN,
	'--device=' + DEVICE,
	'--config=' + CONFIG_PATH,
	'--user=' + USER_PATH,
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
		stdev=datetime.timedelta(minutes=30))

if off - on >= min_duration:
	print('on :', str(on))
	print('off:', str(off))
	#at.schedule(on, OZW_CMD + ['on'])
	#at.schedule(off, OZW_CMD + ['off'])
