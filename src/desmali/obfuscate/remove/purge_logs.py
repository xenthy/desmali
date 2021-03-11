import re
from typing import List

from desmali.extras import logger, Util
from desmali.tools import Dissect


class PurgeLogs():
    def __init__(self, dissect: Dissect):
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

        logger.info(f"*** INIT {self.__class__.__name__} ***")
        flags_set: List[str] = [k for k, v in locals().items() if v is True]
        logger.verbose(f"logs set for purging -> {flags_set}")

        # build regex
        pattern: str = "Landroid\/util\/Log;->(" + "|".join(flags_set) + ")"

        for file in Util.progress_bar(self._dissect.smali_files(),
                                      description=f"Removing logs: {flags_set}"):
            # store file into a list
            with open(file, "r") as file_context:
                original_file: List[str] = file_context.readlines()

            # remove logs and nonsense from original file
            skip: bool = False
            is_modified: bool = False
            modified_file: List[str] = []

            for line in original_file:
                # # skip next line if previous line has a match
                # if skip:
                #     skip = False
                #     continue

                # check for lines with logs
                if re.search(pattern, line):
                    is_modified = True
                    skip = True

                    # # check if previous line has junk (eg. ".line 32")
                    # if modified_file[-1] is not None:
                    #     del modified_file[-1]
                else:
                    modified_file.append(line)

            # if file is not modified, skip writing to save resources
            if not is_modified:
                continue

            logger.debug(f"modifying \"{file}\"")

            with open(file, "w") as file_context:
                file_context.writelines(modified_file)
