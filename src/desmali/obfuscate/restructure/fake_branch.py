import logging

from desmali.tools import Dissect
from desmali.extras import logger, Util, regex


class FakeBranch:
    """
    class description
    """

    def __init__(self, dissect: Dissect):
        self._dissect = dissect

    def run(self):
        logger.info(f"*** INIT {self.__class__.__name__} ***")

        for filename in Util.progress_bar(self._dissect.smali_files(),
                                          description=f"Creating fake branches "):

            logger.debug(f"modifying \"{filename}\"")

            with Util.inplace_file(filename) as file:
                editing_method = False
                start_label = None
                end_label = None
                for line in file:
                    if (
                        line.startswith(".method ")
                        and " abstract " not in line
                        and " native " not in line
                        and not editing_method
                    ):
                        # Entering method.
                        file.write(line)
                        editing_method = True

                    elif line.startswith(".end method") and editing_method:
                        # Exiting method.
                        if start_label and end_label:
                            file.write("\t:{0}\n".format(end_label))
                            file.write(
                                "\tgoto/32 :{0}\n".format(start_label))
                            start_label = None
                            end_label = None
                        file.write(line)
                        editing_method = False

                    elif editing_method:
                        # Inside method.
                        file.write(line)
                        match = regex.LOCALS_PATTERN.match(line)
                        if match and int(match.group("local_count")) >= 2:
                            # If there are at least 2 registers available, add a
                            # fake branch at the beginning of the method: one branch
                            # will continue from here, the other branch will go to
                            # the end of the method and then will return here
                            # through a "goto" instruction.
                            v0, v1 = (
                                Util.get_random_int(1, 32),
                                Util.get_random_int(1, 32),
                            )
                            start_label = Util.get_random_string(16)
                            end_label = Util.get_random_string(16)
                            tmp_label = Util.get_random_string(16)
                            file.write(
                                "\n\tconst v0, {0}\n".format(v0))
                            file.write("\tconst v1, {0}\n".format(v1))
                            file.write("\tadd-int v0, v0, v1\n")
                            file.write("\trem-int v0, v0, v1\n")
                            file.write(
                                "\tif-gtz v0, :{0}\n".format(tmp_label))
                            file.write(
                                "\tgoto/32 :{0}\n".format(end_label))
                            file.write("\t:{0}\n".format(tmp_label))
                            file.write("\t:{0}\n".format(start_label))

                    else:
                        file.write(line)
