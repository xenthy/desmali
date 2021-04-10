from typing import List, no_type_check

from desmali.abc import Desmali
from desmali.tools import Dissect
from desmali.extras import logger, Util, regex


class BooleanArithmetic(Desmali):
    def __init__(self, dissect: Dissect):
        super().__init__(self)
        self._dissect = dissect

    def run(self):
        for filename in Util.progress_bar(self._dissect.smali_files(),
                                          description=f"Inserting arithmetic branches"):

            logger.debug(f"modifying \"{filename}\"")

            method_wlabels: List[str] = list()
            method_wolabels: List[str] = list()
            in_method: bool = False
            contains_label: bool = False
            pass_local: bool = False
            start_str: str = ""
            end_str: str = ""
            temp_str: str = ""
            nop_count:int = 0

            with Util.inplace_file(filename) as file:

                for line in file:

                    # check if the method contains a label
                    if not contains_label:
                        if regex.LABEL.match(line):
                            contains_label = True
                            goto_label = line.strip()


                    # checks if the method allows for/ require instructions
                    # i.e. abstract, constructor or native methods
                    if (
                        line.startswith(".method ")
                        and "abstract" not in line
                        and "native" not in line
                        and "constructor" not in line
                        and not in_method
                    ):
                        file.write(line)
                        in_method = True

                    # at the end of the method:
                    elif line.startswith(".end method") and in_method:

                        # first check if the labels are not blank,
                        # and the number of local variables >= 2
                        if start_str and end_str and contains_label and pass_local:

                            nop_count = Util.random_int(1,5)

                            method_wlabels.append("\n    :{0}".format(end_str))
                            method_wlabels.append("\n    nop" * nop_count)
                            method_wlabels.append("\n\n    goto/32 :{0}\n\n".format(start_str))
                            start_str = ""
                            end_str = ""

                            file.writelines(method_wlabels)
                        else:
                            # if this a method without injection
                            # write a list containing original lines of code
                            file.writelines(method_wolabels)

                        # reset variables
                        file.write(line)
                        in_method = False
                        contains_label = False
                        pass_local = False
                        method_wlabels = list()
                        method_wolabels = list()
                        nop_count = 0

                    elif in_method:
                        # Inside method.

                        # if not at the ".locals x" line,
                        # no additional lines will be added
                        method_wlabels.append(line)
                        method_wolabels.append(line)

                        # to inject the fake branch and its variables right after ".locals x"
                        match = regex.LOCALS_PATTERN.match(line)
                        if match and int(match.group("local_count")) >= 2:

                            pass_local = True

                            # v0 = hex(Util.random_int(7, 32))
                            # v1 = hex(Util.random_int(5, 32))

                            v0 = Util.random_int(1, 31)
                            v1 = hex(v0 + 1)
                            v2 = hex(2)
                            v0 = hex(v0)

                            start_str = Util.random_string(16)
                            end_str = Util.random_string(16)
                            temp_str = Util.random_string(16)

                            method_wlabels.append("\n")
                            method_wlabels.append("    const/16 v0, {0}\n\n".format(v0))
                            method_wlabels.append("    const/16 v1, {0}\n\n".format(v1))
                            method_wlabels.append("    const/16 v2, {0}\n\n".format(v2))
                            method_wlabels.append("    mul-int v0, v0, v1\n\n")
                            method_wlabels.append("    rem-int v0, v0, v2\n\n")
                            method_wlabels.append("    if-eqz v0, :{0}\n\n".format(temp_str))
                            # method_wlabels.append("    add-int v0, v0, v1\n\n")
                            # method_wlabels.append("    rem-int v0, v0, v1\n\n")
                            # method_wlabels.append("    if-gtz v0, :{0}\n\n".format(temp_str))
                            method_wlabels.append("    goto/32 :{0}\n\n".format(end_str))
                            method_wlabels.append("    :{0}\n\n".format(temp_str))
                            method_wlabels.append("    :{0}\n".format(start_str))

                            temp_str = ""

                    else:
                        file.write(line)
