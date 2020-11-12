#!/usr/bin/env python

from __future__ import division

import collections
import contextlib
import datetime
import delay_record
import errno
import fcntl
import logging
import os
import ozwd_get_value
import ozwd_set_value
import ozwd_util
import pickle
import spicerack
import time


LEVEL_FILE = '/var/lib/homeauto/upstairs_bathroom'
LEVEL_FILE_STAGING = '/var/lib/homeauto/upstairs_bathroom-staging'
DELAY_DURATION = datetime.timedelta(minutes=30)
DIM_DURATION_TOTAL = datetime.timedelta(minutes=30)
DIM_DURATION_MAX_INCREMENT = datetime.timedelta(seconds=127)
DIM_FLOOR = 5
DIMMER_VALUE = spicerack.Value.UPSTAIRS_BATHROOM
DIMMER_RAMP_TIME_VALUE = spicerack.Value.UPSTAIRS_BATHROOM_DIMMER_RAMP_TIME


@contextlib.contextmanager
def locked_level(create):
	try:
		level = open(LEVEL_FILE, 'r+b')
	except IOError as e:
		if e.errno != errno.ENOENT:
			raise
		if not create:
			yield None
			return
		fd = os.open(LEVEL_FILE_STAGING, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
		try:
			level = os.fdopen(fd, 'wb')
		except:
			os.remove(LEVEL_FILE_STAGING)
			os.close(fd)
			raise
		else:
			with level:
				try:
					yield level
					os.link(LEVEL_FILE_STAGING, LEVEL_FILE)
					os.unlink(LEVEL_FILE_STAGING)
				except:
					os.remove(LEVEL_FILE_STAGING)
					raise
	else:
		with level:
			fcntl.lockf(level, fcntl.LOCK_EX)
			try:
				yield level
			finally:
				fcntl.lockf(level, fcntl.LOCK_UN)


def record(position):
	"""Record that the light was adjusted with a new timer"""
	logging.info('Recording position %d', position)
	with locked_level(create=True) as level:
		try:
			delay = pickle.load(level)
			logging.info('Loaded pickle: %r', delay)
			remaining_expected_positions = iter(delay.expected_positions)
			if position == next(remaining_expected_positions, None):
				# This is just the feedback from slow dimming that is already in progress
				logging.info('Ignoring feedback')
				next_delay = delay_record.Delay(delay.when, delay.source_position, delay.target_position, list(remaining_expected_positions))
				expect(level, next_delay)
				return
		except IOError:
			# The file is not open for writing, so there is no expected position yet
			pass

		next_delay = delay_record.Delay(datetime.datetime.utcnow() + DELAY_DURATION, position, position, [])
		expect(level, next_delay)


def update():
	"""If the timer is up, then dim the light a little more"""
	with locked_level(create=False) as level:
		if level is None:
			# There is no timer
			logging.info('There is currently no timer')
			return
		delay = pickle.load(level)
		if delay.source_position <= DIM_FLOOR:
			os.remove(LEVEL_FILE)
			return
		now = datetime.datetime.utcnow()
		remaining = delay.when - now
		if remaining >= datetime.timedelta(minutes=1):
			logging.info('Aborting because the timer still has: %s', remaining)
			return
		if remaining.total_seconds() > 0:
			logging.info('Sleeping because the timer still has: %s', remaining)
			fcntl.lockf(level, fcntl.LOCK_UN)
			time.sleep(remaining.total_seconds())
			fcntl.lockf(level, fcntl.LOCK_EX)

		if delay.expected_positions:
			# There shouldn't be any expected positions left, so something has interrupted the dimmer
			logging.info('Expected positions were not consumed, so reverting from %d to %d',
				delay.target_position, delay.source_position)
			position = delay.source_position

		position_increment = min(
			delay.target_position - DIM_FLOOR,
			max(
				1,
				int((100 - DIM_FLOOR) * DIM_DURATION_MAX_INCREMENT.total_seconds() / DIM_DURATION_TOTAL.total_seconds())
			)
		)
		if position_increment <= 0:
			return
		position = delay.target_position - position_increment
		# This will be near DIM_DURATION_MAX_INCREMENT but accounts for rounding
		ramp_time = datetime.timedelta(seconds=int(position_increment / (100 - DIM_FLOOR) * DIM_DURATION_TOTAL.total_seconds()))

		if delay.target_position > DIM_FLOOR:
			# The switch reports the old and then the new position when it dims
			next_delay = delay_record.Delay(now + ramp_time, delay.target_position, position, [delay.target_position, position])
			expect(level, next_delay)
		else:
			os.remove(LEVEL_FILE)

	logging.info('Dimming to %d over %s', position, ramp_time)
	with ozwd_util.get_thrift_client() as thrift_client, (
			ozwd_util.get_stompy_client()) as stompy_client:
		ozwd_set_value.set_value_connected(DIMMER_RAMP_TIME_VALUE.value, ramp_time.total_seconds(), thrift_client)
		try:
			ozwd_set_value.set_value_connected(DIMMER_VALUE.value, position, thrift_client)
		finally:
			ozwd_set_value.set_value_connected(DIMMER_RAMP_TIME_VALUE.value, 2, thrift_client)


def expect(level, delay):
	logging.info('Writing pickle: %r', delay)
	# Overwrite the existing contents
	level.seek(0)
	level.truncate()
	# FIXME: A crash here would leave an empty file
	pickle.dump(delay, level)


def main():
	update()


if __name__ == "__main__":
	main()

