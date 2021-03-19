from typing import List

from desmali.extras import logger, Util, regex
from desmali.tools import Dissect

START_GOTO = "    goto :desmaili_back \n    :desmaili_front\n\n"
END_GOTO = "\n    :desmaili_back\n    goto :desmaili_front\n\n"


class GotoInjector:
    """
    class description
    """

    def __init__(self, dissect: Dissect):
        self._dissect = dissect

    def run(self):

        logger.info(f"*** INIT {self.__class__.__name__} ***")

        for filename in Util.progress_bar(self._dissect.smali_files(),
                                          description=f"Injecting goto(s): "):
            logger.debug(f"modifying \"{filename}\"")

            method_lines: List[str] = list()
            in_method: bool = False
            first_label: bool = False
            first_goto: bool = False

            with Util.inplace_file(filename) as file:
                for line in file:
                    if regex.LABEL.match(line):
                        first_label = True
                    if regex.GOTO.match(line):
                        first_goto = True

                    if not in_method:
                        if regex.METHOD.match(line):
                            if ("abstract" not in line
                                    and "constructor" not in line):
                                in_method = True
                        file.write(line)

                    else:  # is in_method
                        if line.startswith(".end method"):
                            if first_label or first_goto:
                                method_lines = [START_GOTO] + \
                                    method_lines + [END_GOTO]
                            file.writelines(method_lines)
                            file.write(line)

                            method_lines = list()
                            in_method = False
                            first_label = False
                            first_goto = False
                            continue

                        if first_label or first_goto:
                            method_lines.append(line)
                        else:
                            file.write(line)
