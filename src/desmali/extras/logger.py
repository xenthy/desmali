"""
A logging instace that logs to both a log file and to stdout.
Logs on stdout will be coloured.
"""

import logging
import coloredlogs

LOG_FILE = "./logs/program.log"
FORMATTER = "%(asctime)s:%(msecs)03d:[%(levelname)s]: %(message)s"
TIMESTAMP = "%b %d  %Y %H:%M:%S"
LOG_LEVEL = logging.DEBUG

# add verbose level to the python logging module
VERBOSE_LEVEL = 15
logging.addLevelName(VERBOSE_LEVEL, "VERBOSE")


def verbose(self, message, *args, **kwargs):
    if self.isEnabledFor(VERBOSE_LEVEL):
        self._log(VERBOSE_LEVEL, message, args, **kwargs)


logging.Logger.verbose = verbose

# print to log file
logging.basicConfig(level=logging.DEBUG,
                    format=FORMATTER,
                    datefmt=TIMESTAMP,
                    handlers=[
                        logging.FileHandler(LOG_FILE)
                    ])


# print to stdout
console = logging.StreamHandler()
console.setLevel(VERBOSE_LEVEL)

formatter = coloredlogs.ColoredFormatter(FORMATTER, TIMESTAMP)
console.setFormatter(formatter)

logging.getLogger().addHandler(console)

# clear logs each run
with open(LOG_FILE, "w+") as f:
    pass

logger = logging.getLogger(__name__)
