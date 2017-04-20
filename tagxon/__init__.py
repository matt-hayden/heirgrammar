
import os, os.path
import sys

import logging
logger = logging.getLogger('' if __name__ == '__main__' else __name__)
debug, info, warning, error, fatal = logger.debug, logger.info, logger.warning, logger.error, logger.critical


if sys.stderr.isatty():
	import tqdm
	progress_bar = tqdm.tqdm
else:
	def progress_bar(iterable, **kwargs):
		return iterable
