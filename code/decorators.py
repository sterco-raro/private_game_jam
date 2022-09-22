import time
from functools import wraps
from contextlib import contextmanager

from code.settings import PROFILING_FILE


# -------------------------------------------------------------------------------------------------


def exectime(routine):
	"""Simple execution time profiling for @routine function, keeps the return value untouched"""

	@wraps(routine)
	def wrapper(*args, **kwargs):
		# Calculate time between routine start and end of execution
		start = time.perf_counter()
		ret = routine(*args, **kwargs)
		end = time.perf_counter()
		# Build data string
		data = "EXECTIME: {}.{} => {} seconds".format(routine.__module__, routine.__qualname__, end - start)
		# Write results to a file
		if PROFILING_FILE and PROFILING_FILE != "":
			print(data, file=PROFILING_FILE)
		else:
			print(data)
		return ret

	return wrapper
