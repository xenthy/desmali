from typing import List

from desmali.extras import logger, Util
from desmali.tools import Dissect

class GotoInjector():
    def __init__(self, dissect: Dissect):
        self._dissect = dissect

    def run(self):

        logger.info(f"*** INIT {self.__class__.__name__} ***")

        for file in Util.progress_bar(self._dissect.smali_files(), description=f"Obsfucating with goto: "):
            with Util.inplace_file(file) as file:

                
                is_started:bool = False

                for line in file:
    
                    # check for start of method
                    if ".method" in line and "abstract" not in line:
                        file.write(line)
                        file.write("\n\tgoto :desmaili_back \n\n\t:desmaili_front\n\n")
                        is_started = True

                    #check for the end of method
                    elif ".end method" in line and is_started:
                        is_started = False
                        file.write("\n\t:desmaili_back\n\n\tgoto :desmaili_front\n\n")
                        file.write(line)

                    else:
                        file.write(line)

                logger.debug(f"modifying \"{file}\"")