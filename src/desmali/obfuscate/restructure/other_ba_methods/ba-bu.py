from abc import abstractclassmethod
from threading import local
from typing import List

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
            skip_file: bool = False
            classname: str = ""
            func_name: str = ""
            start_str: str = ""
            end_str: str = ""
            temp_str: str = ""

            if "/androidx/" in filename:
                continue


            with Util.inplace_file(filename) as file:

                for line in file:

                    # if regex.SOURCES.match(line) and "MainActivity" in line:
                    #     skip_file = False
                    # else:
                    #     skip_file = True

                    # get the classname
                    if regex.CLASS_NAME.match(line):
                        if "abstract" in line:
                            skip_file = True
                        else:
                            line = line.strip()
                            fline = line.split(" ")
                            classname = fline[-1]

                    # only accepts up til 15 variables
                    # will need 3 variables to set up the fake branch
                    if regex.LOCALS.match(line):
                        local_num = int(line.strip().split(" ")[-1])
                        if local_num >= 11:
                            in_method = False


                    # check if the method contains a label
                    if not contains_label:
                        if regex.LABEL.match(line):
                            contains_label = True


                    # checks if the method allows for/ require instructions
                    # i.e. abstract, constructor or native methods
                    if (
                        line.startswith(".method ")
                        and "abstract" not in line
                        and "native" not in line
                        and "constructor" not in line
                        and "static" not in line
                        and "private" not in line
                        and not in_method
                        and not skip_file
                    ):
                        file.write(line)
                        in_method = True
                        fline = line.split(" ")

                        func_name = fline[-1][:-1]

                        # how many param are there in the function
                        parans = (func_name.split("("))[1].split(")")[0]
                        if ";" in parans or parans == "" or "Z" in parans:
                            in_method = False
                        else:
                            paran_num = len((func_name.split("("))[1].split(")")[0])
                            # due to limited number of registers
                            if (paran_num > 4):
                                in_method = False
                        
                        # print(filename)


                    # at the end of the method:
                    elif line.startswith(".end method") and in_method:

                        # first check if the labels are not blank,
                        # and the number of local variables >= 2
                        if start_str and end_str and contains_label and pass_local:

                            method_wlabels.append("\n    :{0}\n".format(end_str))
                            # method_wlabels.append("\n    {0}\n".format(recall))
                            # method_wlabels.append("\n    move-result v3\n")
                            # method_wlabels.append("\n    return v3\n")
                            method_wlabels.append("\n    goto/32 :{0}\n\n".format(start_str))
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
                        func_name = ""
                        recall = ""
                        paran_num = 0

                    elif in_method:
                        # Inside method.

                        # if not at the ".locals x" line,
                        # no additional lines will be added
                        method_wlabels.append(line)
                        method_wolabels.append(line)

                        # prepare to return own function
                        recall = "invoke-virtual {"
                        for i in range(0, paran_num+1):
                            if(i != paran_num):
                                recall += "p"+str(i) + ", "
                            else:
                                recall += "p"+str(i)+"}, " + classname + "->" + func_name

                        # to inject the fake branch and its variables right after ".locals x"
                        match = regex.LOCALS_PATTERN.match(line)
                        if match and int(match.group("local_count")) >= 2:

                            # print(filename)

                            pass_local = True

                            v0 = v1 = 0x0
                            while v0 == v1:
                                v0 = hex(Util.random_int(5, 32))
                                v1 = hex(Util.random_int(7, 32))

                            # v0 = Util.random_int(1, 31)
                            # v1 = hex(v0 + 1)
                            # v2 = hex(2)
                            # v0 = hex(v0)

                            start_str = Util.random_string(16)
                            end_str = Util.random_string(16)
                            temp_str = Util.random_string(16)

                            method_wlabels.append("\n")
                            method_wlabels.append("    const/16 v0, {0}\n\n".format(v0))
                            method_wlabels.append("    const/16 v1, {0}\n\n".format(v1))
                            # method_wlabels.append("    const/16 v2, {0}\n\n".format(v2))
                            # method_wlabels.append("    const/16 v3, 0xa\n\n")
                            # method_wlabels.append("    mul-int v0, v0, v1\n\n")
                            # method_wlabels.append("    rem-int v0, v0, v2\n\n")
                            # method_wlabels.append("    if-eqz v0, :{0}\n\n".format(temp_str))
                            method_wlabels.append("    add-int v0, v0, v1\n\n")
                            method_wlabels.append("    rem-int v0, v0, v1\n\n")
                            method_wlabels.append("    if-eqz v0, :{0}\n\n".format(temp_str))
                            method_wlabels.append("    goto/32 :{0}\n\n".format(end_str))
                            method_wlabels.append("    :{0}\n".format(temp_str))
                            method_wlabels.append("    {0}\n\n".format(recall))
                            method_wlabels.append("    :{0}\n".format(start_str))

                            temp_str = ""

                    else:
                        file.write(line)
                
                classname = ""
                skip_file = False
