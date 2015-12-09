import datetime
import random
import time

def _to_timestamp(when):
	return None if when is None else time.mktime(when.timetuple())

def _to_seconds(delta):
	return None if delta is None else delta.total_seconds()

def degenerate_variate(mode):
	return mode

def unbounded_variate(mode, stdev):
	if stdev < 0:
		raise ValueError('stdev should not be less than zero')
	elif stdev == 0:
		return degenerate_variate(mode)
	else:
		return random.normalvariate(mode, stdev)

def half_bounded_variate(mode, stdev):
	if stdev < 0:
		raise ValueError('stdev should not be less than zero')
	elif stdev == 0:
		return degenerate_variate(mode)
	else:
		shape = (mode * (mode**2 + 4 * stdev**2) ** 0.5 +
				mode**2 + 2 * stdev**2) / (2 * stdev**2)
		scale = 2 * mode * stdev**2 / (mode * (mode**2 + 4 * stdev**2) ** 0.5 + mode**2)
		return random.gammavariate(shape, scale)

def left_bounded_variate(mode, stdev, min=None):
	if min is None or min == mode:
		if stdev < 0:
			raise ValueError('stdev should not be less than zero')
		elif stdev == 0:
			return degenerate_variate(mode)
		else:
			return mode + random.gammavariate(1, stdev)
	else:
		if min > mode:
			raise ValueError('mode should not be less than min')
		else:
			return min + half_bounded_variate(mode - min, stdev)

def right_bounded_variate(mode, stdev, max=None):
	if max is None or max == mode:
		if stdev < 0:
			raise ValueError('stdev should not be less than zero')
		elif stdev == 0:
			return degenerate_variate(mode)
		else:
			return mode - random.gammavariate(1, stdev)
	else:
		if max < mode:
			raise ValueError('mode should not be more than max')
		else:
			return max - half_bounded_variate(max - mode, stdev)

def _beta_pert_params(mode, stretch):
	mean = (stretch * mode + 1) / (stretch + 2.)
	if mode == 0.5:
		alpha = stretch / 2. + 1
	else:
		alpha = mean * (2 * mode - 1) / (mode - mean)
	beta = alpha * (1 / mean - 1)
	return (alpha, beta)

def _stretch_err(stretch, mode, stdev):
	(alpha, beta) = _beta_pert_params(mode, stretch)
	if alpha <= 1 or beta <= 1:
		return float('inf')
	actual = (alpha * beta / ((alpha + beta)**2 * (alpha + beta + 1))) ** 0.5
	err = abs(actual - stdev)
	return err

def bounded_variate(min, max, mode=None, stdev=None):
	if min > max:
		raise ValueError('min should not be more than max')
	if mode is None:
		unscaled_mode = 0.5
	elif mode < min:
		raise ValueError('mode should not be less than min')
	elif mode > max:
		raise ValueError('mode should not be more than max')
	else:
		unscaled_mode = (mode - min) / (max - min)
	if stdev is None:
		stretch = 4
	elif stdev < 0:
		raise ValueError('stdev should not be less than zero')
	elif stdev > 12 ** -0.5 * (max - min):
		raise ValueError('stdev should be smaller or the range should be larger')
	elif stdev == 0:
		return degenerate_variate(mode)
	else:
		import scipy.optimize
		initial_stretch = 4
		unscaled_stdev = stdev / (max - min)
		stretch = scipy.optimize.fmin(
				_stretch_err,
				initial_stretch,
				(unscaled_mode, unscaled_stdev),
				disp=False)
	(alpha, beta) = _beta_pert_params(unscaled_mode, stretch)
	return min + random.betavariate(alpha, beta) * (max - min)

def variate(mode=None, stdev=None, min=None, max=None):
	if min is None and max is None:
		if mode is None:
			raise ValueError('Either min, max, or mode should be specified')
		elif stdev is None:
			return degenerate_variate(mode=mode)
		else:
			return unbounded_variate(mode=mode, stdev=stdev)
	elif max is None and min is not None:
		if mode is None or min == mode:
			if stdev is None:
				return degenerate_variate(mode=min)
			else:
				return left_bounded_variate(mode=min, stdev=stdev)
		elif stdev is None:
			if mode is None:
				raise ValueError('Either mode or stdev shoud be specified')
			else:
				raise ValueError('stdev should be specified')
		else:
			return left_bounded_variate(mode=mode, stdev=stdev, min=min)
	elif min is None and max is not None:
		if mode is None or max == mode:
			if stdev is None:
				return degenerate_variate(mode=max)
			else:
				return right_bounded_variate(mode=max, stdev=stdev)
		elif stdev is None:
			if mode is None:
				raise ValueError('Either mode or stdev shoud be specified')
			else:
				raise ValueError('stdev should be specified')
		else:
			return right_bounded_variate(mode=mode, stdev=stdev, max=max)
	else:
		return bounded_variate(min=min, max=max, mode=mode, stdev=stdev)

def variate_datetime(mode=None, stdev=None, min=None, max=None):
	tzinfo = next(
			(when.tzinfo
				for when in (mode, min, max)
				if when is not None and when.tzinfo is not None),
			None)
	return datetime.datetime.fromtimestamp(variate(
		mode=_to_timestamp(mode),
		stdev=_to_seconds(stdev),
		min=_to_timestamp(min),
		max=_to_timestamp(max)),
		tzinfo)

def variate_timedelta(mode=None, stdev=None, min=None, max=None):
	return datetime.timedelta(seconds=variate(
		mode=_to_seconds(mode),
		stdev=_to_seconds(stdev),
		min=_to_seconds(min),
		max=_to_seconds(max)))
