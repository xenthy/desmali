import re
from typing import List, Match

from desmali.abc import Desmali
from desmali.extras import logger, Util
from desmali.tools import Dissect


class PurgeLogs(Desmali):
    def __init__(self, dissect: Dissect):
        super().__init__(self)
        self._dissect = dissect

    def run(self,
            a: bool = False,  # assert
            d: bool = False,  # verbose
            e: bool = False,  # error
            i: bool = False,  # info
            v: bool = False,  # verbose
            w: bool = False,  # warn
            wtf: bool = False  # what a terrible failure
            ):

        flags_set: List[str] = [k for k, v in locals().items() if v is True]
        logger.verbose(f"logs set for purging -> {flags_set}")

        # build regex
        # Landroid/util/Log;->v(Ljava/lang/String;Ljava/lang/String;)I
        pattern_log: Match = re.compile(r".+Landroid\/util\/Log;->(" +
                                        r"|".join(flags_set) +
                                        r")\(.+")

        for file in Util.progress_bar(self._dissect.smali_files(),
                                      description=f"Removing logs: {flags_set}"):
            if "Log.smali" in file:
                continue
            # store file into a list
            with open(file, "r") as file_context:
                original_file: List[str] = file_context.readlines()

            # remove logs and nonsense from original file
            is_modified: bool = False
            modified_file: List[str] = []

            for line in original_file:
                # check for lines with logs
                if pattern_log.match(line):
                    is_modified = True
                else:
                    modified_file.append(line)

            # if file is not modified, skip writing to save resources
            if not is_modified:
                continue

            logger.debug(f"purging logs \"{file}\"")

            with open(file, "w") as file_context:
                file_context.writelines(modified_file)
