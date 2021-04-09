import os
from typing import List, Dict

from desmali.abc import Desmali
from desmali.extras import logger, Util, regex
from desmali.tools.dissect import Dissect


class RenameClass(Desmali):
    """
    This plugin renames class names from smali files within the apk package
    """

    def __init__(self, dissect: Dissect):
        super().__init__(self)
        self._dissect = dissect

    def run(self):
        # get all class names
        self._class_names: List[str] = self._dissect.class_names(renamable=True)

        # generate a mapping of method names
        self._class_name_mapping: Dict[str: str] = Util.generate_mapping(self._class_names)

        # rename classes in smali files
        for filename in Util.progress_bar(self._dissect.smali_files(),
                                          description="Renaming class names"):

            logger.debug(f"renaming class: {filename}")

            class_name: str = None

            with Util.inplace_file(filename) as file:
                for line in file:

                    # get class names in line
                    match = regex.CLASSES.findall(line)
                    if match is not None:
                        for class_name in match:

                            #rename all classes eligible for renaming
                            if class_name in self._class_name_mapping:
                                tmp = class_name[1:].split("/")
                                tmp.pop()
                                tmp.append(
                                    self._class_name_mapping[class_name])
                                line = line.replace(
                                    class_name, "L" + "/".join(tmp) + ";")

                    # get source file names
                    source_match = regex.SOURCES.match(line)
                    if source_match is not None:

                        # rename source file name eligible for renaming
                        source_name = source_match.group("name")
                        for k, v in self._class_name_mapping.items():
                            if k.split("/")[-1][:-1] == source_name:
                                line = line.replace(source_name, v)

                    file.write(line)

        # Update directory mapping of new path and old path
        smali_path = "./.tmp/obfuscated/smali/"
        for old_name, new_name in self._class_name_mapping.items():
            new_file = old_name[1:-1].split("/")[:-1]
            new_file.append(new_name)

            old_path = smali_path + old_name[1:-1] + ".smali"
            new_path = smali_path + "/".join(new_file) + ".smali"
            if os.path.isfile(old_path):
                self._dissect.update_mapping(old_path, new_path)
