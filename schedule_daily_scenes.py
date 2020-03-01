#!/usr/bin/env python

import argparse
import astral
import at
import calendar_util
import datetime
import logging
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
HALLOWEEN_SWITCHES = [
	spicerack.Value.GARAGE_OUTLET,
]
CHRISTMAS_SWITCHES = [
	spicerack.Value.GARAGE_OUTLET,
]
NIGHTLIGHT_DIMMERS = {
	spicerack.Value.JASHERS_BEDROOM: None,
	spicerack.Value.ALDENS_BEDROOM: None,
	spicerack.Value.EDENS_BEDROOM: None,
	spicerack.Value.UPSTAIRS_BATHROOM: spicerack.Value.UPSTAIRS_BATHROOM_DIMMER_RAMP_TIME,
}


def schedule_switch(value, today, dry_run):
	tomorrow = today + datetime.timedelta(days=1)
	min_morning_duration = variates.variate_timedelta(
			mode=datetime.timedelta(minutes=30),
			stdev=datetime.timedelta(minutes=10),
			min=datetime.timedelta(0))
	min_evening_duration = variates.variate_timedelta(
			mode=datetime.timedelta(hours=1),
			stdev=datetime.timedelta(minutes=30),
			min=datetime.timedelta(0))
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
		at.schedule(morning_on, cmd + ['--position=on'], dry_run)
		at.schedule(morning_off, cmd + ['--position=off'], dry_run)

	evening_on = variates.variate_datetime(
			mode=spicerack.location.sunset(today),
			stdev=datetime.timedelta(minutes=10),
			min=spicerack.location.solar_noon(today))
	evening_off = variates.variate_datetime(
			mode=spicerack.tzinfo.localize(datetime.datetime.combine(tomorrow,
				datetime.time(hour=0, minute=30))),
			stdev=datetime.timedelta(minutes=20),
			max=spicerack.tzinfo.localize(datetime.datetime.combine(tomorrow,
				datetime.time(hour=4))))
	if evening_off - evening_on >= min_evening_duration:
		at.schedule(evening_on, cmd + ['--position=on'], dry_run)
		at.schedule(evening_off, cmd + ['--position=off'], dry_run)


def schedule_nightlight(value, today, dry_run, dimmer_ramp_time_value=None):
	morning_wake = max(
		spicerack.location.sunrise(today),
		spicerack.tzinfo.localize(datetime.datetime.combine(today,
			datetime.time(hour=7))))
	morning_off = variates.variate_datetime(
			min=morning_wake,
			mode=morning_wake,
			stdev=datetime.timedelta(minutes=30),
			max=max(morning_wake, spicerack.location.solar_noon(today)))
	bedtime = spicerack.tzinfo.localize(datetime.datetime.combine(today,
			datetime.time(hour=20)))
	evening_on = variates.variate_datetime(
			mode=min(bedtime, spicerack.location.sunset(today)),
			stdev=datetime.timedelta(minutes=10),
			min=spicerack.location.solar_noon(today),
			max=bedtime)
	value_arg = '--value={}'.format(shlex_quote(value.name))
	at.schedule(morning_off, [DIM_BIN, value_arg, '--position=0',
		'--filter-max={}'.format(NIGHTLIGHT_POSITION)], dry_run)
	at.schedule(evening_on, [OZWD_SET_VALUE_BIN, value_arg, '--position=99'],
		dry_run)
	pulse_args = [PULSE_BIN, value_arg]
	if dimmer_ramp_time_value is not None:
		pulse_args.append('--dimmer-ramp-time-value={}'.format(
				shlex_quote(dimmer_ramp_time_value.name)))
	at.schedule(datetime.datetime.combine(today, datetime.time(20, 55)),
		pulse_args, dry_run)
	at.schedule(datetime.datetime.combine(today, datetime.time(21)),
		[DIM_BIN, value_arg, '--position={}'.format(NIGHTLIGHT_POSITION),
		'--filter-min={}'.format(NIGHTLIGHT_POSITION)], dry_run)


def main():
	parser = argparse.ArgumentParser(
		description='Schedule Z-Wave scenes for the day')
	parser.add_argument('-n', '--dry-run', action='store_true',
			help='Don\'t actually schedule jobs')
	args = parser.parse_args()

	if args.dry_run:
		logging.basicConfig(level=logging.DEBUG)

	today = datetime.date.today()

	for switch in EXTERIOR_SWITCHES:
		schedule_switch(switch, today, args.dry_run)
	if (today >= calendar_util.get_autumnal_equinox(today.year) and
			today <= calendar_util.get_halloween(today.year)):
		for switch in HALLOWEEN_SWITCHES:
			schedule_switch(switch, today, args.dry_run)
	if (today > calendar_util.get_thanksgiving(today.year) or
			today <= calendar_util.get_new_years(today.year)):
		for switch in CHRISTMAS_SWITCHES:
			schedule_switch(switch, today, args.dry_run)
	for (dimmer, dimmer_ramp_time_value) in NIGHTLIGHT_DIMMERS.iteritems():
		schedule_nightlight(dimmer, today, args.dry_run, dimmer_ramp_time_value)

	if today.weekday() in {
		calendar_util.DayOfWeek.MONDAY.value,
		calendar_util.DayOfWeek.TUESDAY.value,
		calendar_util.DayOfWeek.THURSDAY.value,
		calendar_util.DayOfWeek.FRIDAY.value,
	}:
		at.schedule(
			datetime.datetime.combine(today, datetime.time(7)),
			[OZWD_SET_VALUE_BIN, '--value={}'.format(shlex_quote(spicerack.Value.EDENS_BEDROOM.name)), '--position=on'],
			args.dry_run)


if __name__ == "__main__":
	main()
