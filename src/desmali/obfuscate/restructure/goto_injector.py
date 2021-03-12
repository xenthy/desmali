from desmali.extras import logger, Util
from desmali.tools import Dissect

START_GOTO = "\n\tgoto :desmaili_back \n\n\t:desmaili_front\n\n"
END_GOTO = "\n\t:desmaili_back\n\n\tgoto :desmaili_front\n\n"


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
            is_started: bool = False

            with Util.inplace_file(filename) as file:

                for line in file:
                    # check for start of method
                    if ".method" in line and "abstract" not in line:
                        file.write(line)
                        file.write(START_GOTO)
                        is_started = True

                    # check for the end of method
                    elif ".end method" in line and is_started:
                        is_started = False
                        file.write(END_GOTO)
                        file.write(line)

                    else:
                        file.write(line)
