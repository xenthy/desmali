from typing import List, Dict, Match

from desmali.abc import Desmali
from desmali.tools import Dissect
from desmali.extras import logger, Util, regex


class RenameMethod(Desmali):
    """
    This plugin renames method names and their invocations from all
    the smali files
    """

    def __init__(self, dissect: Dissect):
        super().__init__(self)
        self._dissect: Dissect = dissect

    def run(self) -> None:
        # get all method names
        self._method_names: List[str] = self._dissect.method_names(renamable=True)

        # generate a mapping of method names
        self._method_name_mapping: Dict[str: str] = Util.generate_mapping(self._method_names)

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
                            match: Match = regex.CLASS.match(line)
                            class_name = match.group("name")

                        # rename all methods which are elibible to rename
                        if match := regex.METHOD.match(line):
                            method: str = match.group("method")
                            map_name: str = f"{class_name}|{method}"
                            if map_name in self._method_name_mapping:
                                line = line.replace(f"{method}(",
                                                    f"{self._method_name_mapping[map_name]}(")

                    # rename all method invocations which are elibible to rename
                    if match := regex.INVOKE.match(line):
                        invocation: Match = match.group("invocation")
                        invoke_class_name: Match = match.group("class")
                        method: str = match.group("method")
                        map_name: str = f"{invoke_class_name}|{method}"
                        if (("direct" in invocation
                                or "static" in invocation)
                                and map_name in self._method_name_mapping):
                            line = line.replace(f">{method}(",
                                                f">{self._method_name_mapping[map_name]}(")

                    file.write(line)
