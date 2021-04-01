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
                    # check if first label has been reached
                    if not first_label:
                        if regex.LABEL.match(line):
                            first_label = True

                    # check if first goto has been reached
                    if not first_goto:
                        if regex.GOTO.match(line):
                            first_goto = True

                    # if not in a method, check if the current line is a method
                    # declaration and check if a method is not abstract or a
                    # constructor
                    if not in_method:
                        if regex.METHOD.match(line):
                            if ("abstract" not in line
                                    and "native" not in line
                                    and "constructor" not in line):
                                in_method = True
                        # write every line to file for this condition
                        file.write(line)

                    # if in a method
                    else:
                        # if the end of a method has been reached, check if first label
                        # or first goto has been reached, if true, then wrap the label blocks
                        # with our goto injectors
                        if line.startswith(".end method"):
                            if first_label or first_goto:
                                method_lines = [START_GOTO] + \
                                    method_lines + [END_GOTO]

                            file.writelines(method_lines)
                            method_lines = list()  # reset the list

                            # write the ".end method" line after writing the modified blocks
                            file.write(line)

                            # reset variables
                            in_method = False
                            first_label = False
                            first_goto = False
                            continue

                        # if first label or first goto has been reached, append line to
                        # the method_lines list until ".end method" has been reached
                        if first_label or first_goto:
                            method_lines.append(line)

                        # if the first label or goto has not been reached, write line to
                        # file
                        else:
                            file.write(line)
