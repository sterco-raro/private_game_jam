import time
from functools import wraps
from contextlib import contextmanager


# -------------------------------------------------------------------------------------------------


def exectime(routine):
	"""Simple execution time profiling for @routine function, keeps the return value"""
	@wraps(routine)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		ret = routine(*args, **kwargs)
		end = time.perf_counter()
		print("EXECTIME: {}.{} => {} ms".format(routine.__module__, routine.__name__, end - start))
		return ret
	return wrapper
