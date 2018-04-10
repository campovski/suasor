from .models import Log, LogType
from .settings import DEBUG, DIR_DATA, DIR_DATA_DEBUG, DIR_DATA_IMAGES, DIR_DATA_PEOPLE, DIR_DATA_LOG

import datetime
import os

"""
	Writes information about error that occured (like name or image could not be extracted).
	@param at: The name of function that this error occured in
	@param desc: Description of error
"""
def _log(log_type, package, at, desc):
    log_time = datetime.datetime.now()
    if DEBUG:
        with open(os.path.join(DIR_DATA_LOG, '{}.log'.format(package)), 'a') as f:
            f.write('[{0}] @ {1} @ {2}: {3}\n'.format(log_type, log_time, at, desc))

    log = Log()
    log.at_time = log_time
    log.type = LogType.objects.get(name=log_type)
    log.in_package = package
    log.in_function = at
    log.description = desc
    log.save()
