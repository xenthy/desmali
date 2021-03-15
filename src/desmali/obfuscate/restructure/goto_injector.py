from desmali.extras import logger, Util, regex
from desmali.tools import Dissect

START_GOTO = "\n    goto :desmaili_back \n\n    :desmaili_front\n\n"
END_GOTO = "\n    :desmaili_back\n\n    goto :desmaili_front\n\n"


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
            white_list = []
            

            with Util.inplace_file(filename) as file:

                white_list = self.methodLabels(file)

                for line in file:
                    # check for start of method in whitelist
                    #if ".method" in line and "abstract" not in line:
                    if any(mtd in line for mtd in white_list):
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

    def methodLabels(self, file):

        in_method: bool = False
        curr_method: str = ""
        white_list = []

        for line in file:

            # check for the start of a method that is not abstract or a constructor
            if regex.METHOD.match(line) and "abstract" not in line and "constructor" not in line:
                in_method = True
                cm = line.split("(")
                curr_method = cm[0]
            
            # check for if there is a label in the constructor
            # if yes, the method will be added to the whitelist
            elif in_method == True and regex.LABEL.match(line):
                white_list.append(curr_method)
                curr_method = ""

            # check for the end of the method
            elif ".end method" in line and in_method:
                in_method = False
        
            file.write(line)
        
        # remove any null elements and duplicates in whitelist
        white_list = filter(None, white_list)
        white_list = list(set(white_list))

        return white_list


