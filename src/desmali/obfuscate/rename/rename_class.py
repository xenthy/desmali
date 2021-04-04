import os
from typing import List, Dict
from string import ascii_letters

from desmali.extras import logger, Util, regex
from desmali.tools.dissect import Dissect


class RenameClass:

    def __init__(self, dissect: Dissect):
        self._dissect = dissect

    def run(self):
        logger.info(f"*** INIT {self.__class__.__name__} ***")

        # get all class names
        self._class_names: List[str] = self._dissect.class_names(
            renamable=True)

        # generate a mapping of method names
        # [.., Y, Z, aa, ab, ac, ..]
        self._class_name_mapping: Dict[str: str] = dict()
        letters: List[str] = [letter for letter in ascii_letters]  # [a-zA-Z]

        for index, name in enumerate(self._class_names):
            new_name: str = ""

            while index >= len(letters):
                remainder: int = index % len(letters)
                new_name = letters[remainder] + new_name
                index = int((index - remainder) / len(letters))

            if len(new_name) == 0:
                new_name = letters[index] + new_name
            else:
                new_name = letters[index - 1] + new_name
            self._class_name_mapping[name] = new_name

        # rename classes in smali files
        for filename in Util.progress_bar(self._dissect.smali_files(),
                                          description="Renaming class names"):

            logger.debug(f"renaming class: {filename}")

            class_name: str = None

            with Util.inplace_file(filename) as file:
                for line in file:

                    match = regex.CLASSES.findall(line)
                    if match is not None:
                        for class_name in match:
                            if class_name in self._class_name_mapping:
                                tmp = class_name[1:].split("/")
                                tmp.pop()
                                tmp.append(
                                    self._class_name_mapping[class_name])
                                line = line.replace(
                                    class_name, "L" + "/".join(tmp) + ";")

                    source_match = regex.SOURCES.match(line)
                    if source_match is not None:
                        source_name = source_match.group("name")
                        for k, v in self._class_name_mapping.items():
                            if k.split("/")[-1][:-1] == source_name:
                                line = line.replace(source_name, v)

                    file.write(line)

        # rename smali files
        smali_path = "./.tmp/obfuscated/smali/"
        for old_name, new_name in self._class_name_mapping.items():
            new_file = old_name[1:-1].split("/")[:-1]
            new_file.append(new_name)

            old_path = smali_path + old_name[1:-1] + ".smali"
            new_path = smali_path + "/".join(new_file) + ".smali"
            if os.path.isfile(old_path):
                os.rename(old_path, new_path)
                self._dissect.update_mapping(old_path, new_path)

        self._dissect.smali_files(force=True)
