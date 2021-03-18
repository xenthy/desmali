from typing import List, Dict
from string import ascii_letters

from desmali.tools import Dissect
from desmali.extras import logger, Util, regex


class RenameMethod:
    def __init__(self, dissect: Dissect):
        self._dissect: Dissect = dissect

    def run(self):
        logger.info(f"*** INIT {self.__class__.__name__} ***")

        # get all method names
        self._method_names: List[str] = self._dissect.method_names(renamable=True)

        # generate a mapping of method names
        self._method_name_mapping: Dict[str: str] = dict()  # [.., Y, Z, aa, ab, ac, ..]
        letters: List[str] = [letter for letter in ascii_letters]  # [a-zA-Z]

        for index, name in enumerate(self._method_names):
            new_name: str = ""

            while index >= len(letters):
                remainder: int = index % len(letters)
                new_name = letters[remainder] + new_name
                index = int((index - remainder) / len(letters))

            if len(new_name) == 0:
                new_name = letters[index] + new_name
            else:
                new_name = letters[index - 1] + new_name
            self._method_name_mapping[name] = new_name

        with open("mapping.txt", "w+") as file:
            for k, v in self._method_name_mapping.items():
                file.write(f"{v} - {k}\n")

        for filename in Util.progress_bar(self._dissect.smali_files(),
                                          description="Renaming method names"):

            logger.debug(f"renaming method: {filename}")

            skip_to_end: bool = False
            class_name: str = None

            with Util.inplace_file(filename) as file:
                for line in file:
                    # skip if the "virtual method" line has been reached
                    if not skip_to_end:
                        if "# virtual methods" in line:
                            skip_to_end = True
                            file.write(line)
                            continue

                        # get the class name which is located at the start of each
                        # smali file
                        if class_name is None:
                            match = regex.CLASS.match(line)
                            class_name = match.group("name")

                        # rename all methods which are elibible to rename
                        if match := regex.METHOD.match(line):
                            method = match.group("method")
                            map_name = f"{class_name}|{method}"
                            if map_name in self._method_name_mapping:
                                line = line.replace(f"{method}(",
                                                    f"{self._method_name_mapping[map_name]}(")

                    # rename all method invocations which are elibible to rename
                    if match := regex.INVOKE.match(line):
                        invocation = match.group("invocation")
                        invoke_class_name = match.group("class")
                        method = match.group("method")
                        map_name = f"{invoke_class_name}|{method}"
                        if (("direct" in invocation
                                or "static" in invocation)
                                and map_name in self._method_name_mapping):
                            line = line.replace(f">{method}(",
                                                f">{self._method_name_mapping[map_name]}(")

                    file.write(line)
