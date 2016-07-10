#!/usr/bin/env python

import astral
import at
import calendar_util
import datetime
from six.moves import shlex_quote
import spicerack
import variates

# TODO: Move these scripts to a permanent location.
OZWD_SET_VALUE_BIN = '/usr/local/src/homeauto/ozwd_set_value.py'
PULSE_BIN = '/usr/local/src/homeauto/pulse.py'
DIM_BIN = '/usr/local/src/homeauto/dim.py'
NIGHTLIGHT_POSITION = 20

EXTERIOR_SWITCHES = [
	spicerack.Value.FRONT_PORCH,
]
CHRISTMAS_SWITCHES = [
	spicerack.Value.GARAGE_OUTLET,
]
NIGHTLIGHT_DIMMERS = [
	spicerack.Value.FRONT_BEDROOM,
	spicerack.Value.FRONT_FAIRY,
	spicerack.Value.SIDE_BEDROOM,
	spicerack.Value.SIDE_FAIRY,
	spicerack.Value.KIDS_BATHROOM,
]

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
min_morning_duration = variates.variate_timedelta(
		mode=datetime.timedelta(minutes=30),
		stdev=datetime.timedelta(minutes=10),
		min=datetime.timedelta(0))
min_evening_duration = variates.variate_timedelta(
		mode=datetime.timedelta(hours=1),
		stdev=datetime.timedelta(minutes=30),
		min=datetime.timedelta(0))

def schedule_switch(value):
	cmd = [OZWD_SET_VALUE_BIN, '--value={}'.format(shlex_quote(value.name))]

	morning_on = variates.variate_datetime(
			mode=spicerack.tzinfo.localize(datetime.datetime.combine(today,
				datetime.time(hour=6, minute=30))),
			stdev=datetime.timedelta(minutes=10),
			min=spicerack.tzinfo.localize(datetime.datetime.combine(today,
				datetime.time(hour=4))))
	morning_off = variates.variate_datetime(
			mode=spicerack.location.sunrise(today),
			stdev=datetime.timedelta(minutes=10),
			max=spicerack.location.solar_noon(today))
	if morning_off - morning_on >= min_morning_duration:
		at.schedule(morning_on, cmd + ['--position=on'])
		at.schedule(morning_off, cmd + ['--position=off'])

	evening_on = variates.variate_datetime(
			mode=spicerack.location.sunset(today),
			stdev=datetime.timedelta(minutes=10),
			min=spicerack.location.solar_noon(today))
	evening_off = variates.variate_datetime(
			mode=spicerack.tzinfo.localize(datetime.datetime.combine(tomorrow,
				datetime.time(hour=0, minute=30))),
			stdev=datetime.timedelta(minutes=30),
			max=spicerack.tzinfo.localize(datetime.datetime.combine(tomorrow,
				datetime.time(hour=4))))
	if evening_off - evening_on >= min_evening_duration:
		at.schedule(evening_on, cmd + ['--position=on'])
		at.schedule(evening_off, cmd + ['--position=off'])

def schedule_nightlight(value):
	morning_wake = max(
		spicerack.location.sunrise(today),
		spicerack.tzinfo.localize(datetime.datetime.combine(today,
			datetime.time(hour=7))))
	morning_off = variates.variate_datetime(
			min=morning_wake,
			mode=morning_wake,
			stdev=datetime.timedelta(hours=1),
			max=spicerack.location.solar_noon(today))
	bedtime = spicerack.tzinfo.localize(datetime.datetime.combine(today,
			datetime.time(hour=20)))
	evening_on = variates.variate_datetime(
			mode=min(bedtime, spicerack.location.sunset(today)),
			stdev=datetime.timedelta(minutes=10),
			min=spicerack.location.solar_noon(today),
			max=bedtime)
	value_arg = '--value={}'.format(shlex_quote(value.name))
	at.schedule(morning_off, [DIM_BIN, value_arg, '--position=0', '--filter-max={}'.format(NIGHTLIGHT_POSITION)])
	at.schedule(evening_on, [OZWD_SET_VALUE_BIN, value_arg, '--position=99'])
	at.schedule(datetime.datetime.combine(today, datetime.time(20, 55)), [PULSE_BIN, value_arg])
	at.schedule(datetime.datetime.combine(today, datetime.time(21)), [DIM_BIN, value_arg, '--position={}'.format(NIGHTLIGHT_POSITION), '--filter-min={}'.format(NIGHTLIGHT_POSITION)])

for switch in EXTERIOR_SWITCHES:
	schedule_switch(switch)
if (today > calendar_util.get_thanksgiving(today.year) or
		today <= calendar_util.get_new_years(today.year)):
	for switch in CHRISTMAS_SWITCHES:
		schedule_switch(switch)
for dimmer in NIGHTLIGHT_DIMMERS:
	schedule_nightlight(dimmer)
