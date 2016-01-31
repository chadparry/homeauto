#!/usr/bin/env python

import astral
import at
import datetime
from six.moves import shlex_quote
import spicerack
import variates

OZWD_SET_VALUE_BIN = '/usr/local/src/homeauto/ozwd_set_value.py'
BEDTIME_WARNING_BIN = '/usr/local/src/homeauto/bedtime_warning.py'
BEDTIME_BIN = '/usr/local/src/homeauto/bedtime.py'

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
min_duration = variates.variate_timedelta(
		mode=datetime.timedelta(hours=2),
		stdev=datetime.timedelta(minutes=30),
		min=datetime.timedelta(0))

def schedule_evening(value):
	evening_on = variates.variate_datetime(
			mode=spicerack.location.sunset(today),
			stdev=datetime.timedelta(minutes=10),
			min=spicerack.location.solar_noon(today))
	evening_off = variates.variate_datetime(
			mode=datetime.datetime.combine(tomorrow,
				datetime.time(hour=0, minute=30, tzinfo=spicerack.tzinfo)),
			stdev=datetime.timedelta(minutes=30),
			max=spicerack.location.solar_noon(tomorrow))
	if evening_off - evening_on >= min_duration:
		cmd = [OZWD_SET_VALUE_BIN, '--value={}'.format(shlex_quote(value.name))]
		at.schedule(evening_on, cmd + ['--position=on'])
		at.schedule(evening_off, cmd + ['--position=off'])

schedule_evening(spicerack.Value.FRONT_PORCH)
# Enable for Christmas
#schedule_evening(spicerack.Value.GARAGE_OUTLET)

def schedule_nightlight(value):
	nightlight_on = variates.variate_datetime(
			mode=spicerack.location.sunset(today),
			stdev=datetime.timedelta(minutes=10),
			min=spicerack.location.solar_noon(today),
			max=datetime.datetime.combine(today,
				datetime.time(hour=20, tzinfo=spicerack.tzinfo)))
	cmd = [OZWD_SET_VALUE_BIN, '--value={}'.format(shlex_quote(value.name))]
	at.schedule(nightlight_on, cmd + ['--position=99'])

schedule_nightlight(spicerack.Value.FRONT_BEDROOM)
schedule_nightlight(spicerack.Value.FRONT_FAIRY)
schedule_nightlight(spicerack.Value.SIDE_BEDROOM)
schedule_nightlight(spicerack.Value.SIDE_FAIRY)
schedule_nightlight(spicerack.Value.KIDS_BATHROOM)

at.schedule(datetime.datetime.combine(today, datetime.time(20, 55)), [BEDTIME_WARNING_BIN])
at.schedule(datetime.datetime.combine(today, datetime.time(21)), [BEDTIME_BIN])
