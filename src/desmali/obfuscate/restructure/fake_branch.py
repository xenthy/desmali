import logging
from types import prepare_class

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

            method_wlabels: List[str] = list()
            method_wolabels: List[str] = list()
            in_method: bool = False
            contains_label: bool = False
            pass_local: bool = False
            start_str: str = ""
            end_str: str = ""
            temp_str: str = ""

            with Util.inplace_file(filename) as file:

                for line in file:

                    # check if the method contains a method
                    if not contains_label:
                        if regex.LABEL.match(line):
                            contains_label = True

                    if (
                        line.startswith(".method ")
                        and " abstract " not in line
                        and " native " not in line
                        and not in_method
                    ):
                        file.write(line)
                        in_method = True

                    elif line.startswith(".end method") and in_method:
                        if start_str and end_str and contains_label and pass_local:
                            # file.write("    :{0}\n".format(end_str))
                            # file.write("    goto/32 :{0}\n".format(start_str))
                            method_wlabels.append("    :{0}\n".format(end_str))
                            method_wlabels.append(
                                "    goto/32 :{0}\n".format(start_str))
                            start_str = ""
                            end_str = ""

                            file.writelines(method_wlabels)
                        else:
                            file.writelines(method_wolabels)

                        file.write(line)
                        in_method = False
                        contains_label = False
                        pass_local = False
                        method_wlabels = list()
                        method_wolabels = list()

                    elif in_method:
                        # Inside method.
                        # file.write(line)
                        method_wlabels.append(line)
                        method_wolabels.append(line)

                        match = regex.LOCALS_PATTERN.match(line)
                        if match and int(match.group("local_count")) >= 2:

                            pass_local = True

                            v0 = Util.random_int(1, 32)
                            v1 = Util.random_int(1, 32)

                            start_str = Util.random_string(16)
                            end_str = Util.random_string(16)
                            temp_str = Util.random_string(16)

                            # file.write("\n    const v0, {0}\n\n".format(v0))
                            # file.write("    const v1, {0}\n\n".format(v1))
                            # file.write("    add-int v0, v0, v1\n\n")
                            # file.write("    rem-int v0, v0, v1\n\n")
                            # file.write("    if-gtz v0, :{0}\n\n".format(temp_str))
                            # file.write("    goto/32 :{0}\n\n".format(end_str))
                            # file.write("    :{0}\n\n".format(temp_str))
                            # file.write("    :{0}\n".format(start_str))

                            method_wlabels.append(
                                "\n    const v0, {0}\n\n".format(v0))
                            method_wlabels.append(
                                "    const v1, {0}\n\n".format(v1))
                            method_wlabels.append("    add-int v0, v0, v1\n\n")
                            method_wlabels.append("    rem-int v0, v0, v1\n\n")
                            method_wlabels.append(
                                "    if-gtz v0, :{0}\n\n".format(temp_str))
                            method_wlabels.append(
                                "    goto/32 :{0}\n\n".format(end_str))
                            method_wlabels.append(
                                "    :{0}\n\n".format(temp_str))
                            method_wlabels.append(
                                "    :{0}\n".format(start_str))

                            temp_str = ""

                    else:
                        file.write(line)
