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

            in_method: bool = False
            start_str: str = ""
            end_str: str = ""
            temp_str: str = ""

            with Util.inplace_file(filename) as file:

                for line in file:

                    if (
                        line.startswith(".method ")
                        and " abstract " not in line
                        and " native " not in line
                        and not in_method
                    ):
                        file.write(line)
                        in_method = True

                    elif line.startswith(".end method") and in_method:
                        if start_str and end_str:
                            file.write("    :{0}\n".format(end_str))
                            file.write("    goto/32 :{0}\n".format(start_str))
                            start_str = ""
                            end_str = ""
                        file.write(line)
                        in_method = False

                    elif in_method:
                        # Inside method.
                        file.write(line)
                        match = regex.LOCALS_PATTERN.match(line)
                        if match and int(match.group("local_count")) >= 2:

                            v0 = Util.random_int(1, 32)
                            v1 = Util.random_int(1, 32)

                            start_str = Util.random_string(16)
                            end_str = Util.random_string(16)
                            temp_str = Util.random_string(16)

                            file.write("\n    const v0, {0}\n\n".format(v0))
                            file.write("    const v1, {0}\n\n".format(v1))
                            file.write("    add-int v0, v0, v1\n\n")
                            file.write("    rem-int v0, v0, v1\n\n")
                            file.write("    if-gtz v0, :{0}\n\n".format(temp_str))
                            file.write("    goto/32 :{0}\n\n".format(end_str))
                            file.write("    :{0}\n\n".format(temp_str))
                            file.write("    :{0}\n".format(start_str))

                            temp_str = ""

                    else:
                        file.write(line)
