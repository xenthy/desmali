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

# print to log file
logging.basicConfig(level=LOG_LEVEL,
                    format=FORMATTER,
                    datefmt=TIMESTAMP,
                    handlers=[
                        logging.FileHandler(LOG_FILE)
                    ])


# print to stdout
console = logging.StreamHandler()
console.setLevel(LOG_LEVEL)

formatter = coloredlogs.ColoredFormatter(FORMATTER, TIMESTAMP)
console.setFormatter(formatter)

logging.getLogger().addHandler(console)

# clear logs each run
with open(LOG_FILE, "w+") as f:
    pass

logger = logging.getLogger(__name__)
