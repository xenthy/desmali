import os
import re
import logging
from typing import List, Set, Tuple, Dict, Match

from desmali.extras import logger, Util, regex

from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.axml import AXMLPrinter

logging.getLogger("androguard").setLevel(logging.WARNING)


class Dissect:
    def __init__(self, apk_path: str, original_dir_path: str, decoded_dir_path: str):
        # check if input directory exists
        if not os.path.isdir(original_dir_path):
            logger.error(f"directory does not exist \"{original_dir_path}\"")
            raise NotADirectoryError(
                f"directory does not exist \"{original_dir_path}\"")
        else:
            self.original_dir_path: str = original_dir_path

        if not os.path.isdir(decoded_dir_path):
            logger.error(f"directory does not exist \"{decoded_dir_path}\"")
            raise NotADirectoryError(
                f"directory does not exist \"{decoded_dir_path}\"")
        else:
            self.decoded_dir_path: str = decoded_dir_path

        ### INITIAL OPERATIONS ###
        # set apk path
        self.apk_path: str = apk_path

        # locate all smali files
        self.smali_files()

        # locate all smali files
        self.xml_files()

        # map original path and decoded path
        self.dir_mapping: Dict[str, str] = self._set_mapping()

        # set initial number of lines in all the smali files
        self._initial_num_lines: int = len(self)

        # set initial file size
        self._original_file_size: int = self._file_size(self.apk_path)

    def __len__(self) -> int:
        # define variable
        num_of_lines: int = 0

        # count the number of non-empty lines
        for filename in Util.progress_bar(self._smali_files,
                                          description="Calculating number of smali lines"):
            with open(filename, "r", newline="") as file:
                num_of_lines += sum(1 for line in file if line.strip())

        return num_of_lines

    def _file_size(self, apk_path: str) -> int:
        return os.path.getsize(apk_path)

    def file_size_difference(self, apk_path: str) -> Tuple[int, int]:
        return self._original_file_size, self._file_size(apk_path)

    def _set_mapping(self) -> Dict[str, str]:
        # dir_mapping dictionary - {decoded_path: original_path}
        dir_mapping: Dict[str, str] = dict()

        for file in Util.progress_bar(self.smali_files(),
                                      description="Mapping original/decoded directories"):
            dir_mapping[file] = file.replace(self.decoded_dir_path,
                                             self.original_dir_path)

        return dir_mapping

    def update_mapping(self, old_path, new_path) -> None:
        # skip files which were explicitly added after apk decoding
        # they would not have a mapping
        if old_path not in self.dir_mapping:
            return False

        self.dir_mapping[new_path] = self.dir_mapping[old_path]
        del self.dir_mapping[old_path]

    def smali_files(self, force=False) -> Tuple[str]:
        """
        Get all smali file paths recursively from the specified directory
        """
        # check if function has already been executed
        if hasattr(self, "_smali_files") and not force:
            return self._smali_files

        logger.verbose("getting all .smali files from decoded directory")

        # identify all smali files recursuvely in the decoded_dir_path
        self._smali_files: List[str] = [
            os.path.join(path, filename)
            for path, _, files in os.walk(self.decoded_dir_path)
            for filename in files
            if filename.endswith(".smali")
        ]

        # convert list to tuple to prevent modification
        self._smali_files: Tuple[str] = tuple(self._smali_files)

        return self._smali_files

    def xml_files(self, force=False) -> Tuple[str]:
        """
        Get all xml file paths recursively from the specified directory
        """
        # check if function has already been executed
        if hasattr(self, "_xml_files") and not force:
            return self._xml_files

        logger.verbose("getting all .xml files from decoded directory")

        # identify all xml files recursuvely in the decoded_dir_path
        self._xml_files: List[str] = [
            os.path.join(path, filename)
            for path, _, files in os.walk(self.decoded_dir_path)
            for filename in files
            if filename.endswith(".xml")
        ]

        # convert list to tuple to prevent modification
        self._xml_files: Tuple[str] = tuple(self._xml_files)

        return self._xml_files

    def add_smali_file(self, filepath: str) -> None:
        self._smali_files = tuple(list(self._smali_files) + [filepath])

    def line_count_info(self) -> Tuple[int, int]:
        """
        Returns the initial number of lines when this object was created and
        the current number of lines.
        """
        return self._initial_num_lines, len(self)

    def method_names(self, renamable: bool = False) -> Tuple[str]:
        # check if smali_files() has already been executed
        if not hasattr(self, "__smali_files"):
            self.__smali_files: List[str] = self.smali_files()

        logger.verbose("getting all method names from the list of smali files")

        # store all method names into a list
        self._method_names: Set[str] = set()

        # iterate through all the smali files
        for filename in Util.progress_bar(self.__smali_files,
                                          description="Retrieving methods from all smali files"):

            with open(filename, "r") as file:
                # identify lines which contains methods
                for line in file:

                    if renamable:
                        # skip enum classes
                        if " enum " in line:
                            break

                        class_match = regex.CLASS.match(line)
                        if class_match is not None:

                            class_name = class_match.group("name")
                            if (class_name.startswith("Landroid")
                                    or class_name.startswith("Ljava")
                                    or class_name.startswith("Lkotlin")):
                                break

                        # skip virtual methods if @param:skip_virtual_methods is set to true.
                        # virtual methods are always at the bottom of the smali file, hence,
                        # 'break' is used
                        if "# virtual methods" in line:
                            break

                    if ((match := regex.METHOD.match(line))
                        and "<init>" not in line
                        and "abstract" not in line
                        and "native" not in line
                            and "<clinit>" not in line):
                        method_name = match.group("method")
                        self._method_names.add(f"{class_name}|{method_name}")

        # convert set to tuple to prevent modification
        self._method_names: Tuple[str, str] = tuple(self._method_names)
        return self._method_names

    def class_names(self, renamable: bool = False) -> Tuple[str]:
        # check if smali_files() has already been executed
        if not hasattr(self, "__smali_files"):
            self.__smali_files: List[str] = self.smali_files()

        logger.verbose("getting all class names from the list of smali files")

        # store all class names into a list
        self._class_names: Set[str] = set()

        # create ignore list (cannot be renamed)
        ignore_list: Set[str] = set()
        apk = APK("./" + self.apk_path)
        package_name = "L" + "/".join(apk.package.split(".")) + "/"

        # add manifest to ignore_list
        manifest = apk.get_android_manifest_axml().get_xml_obj()

        for app in manifest.findall("application"):
            name = apk.get_value_from_tag(app, "name")
            ignore_list.add(name)

        ignore_list.update(apk.get_activities())
        ignore_list.update(apk.get_services())
        ignore_list.update(apk.get_receivers())
        ignore_list.update(apk.get_providers())

        # add xml files to ignore_list
        # iterate through all the xml files
        PACKAGE: Match = re.compile(apk.package + r"\S+[^ \"]")

        for filename in Util.progress_bar(self._xml_files,
                                          description="Retrieving classes from all xml files"):
            with open(filename, "rb") as file:
                axml = AXMLPrinter(file.read())
            xml = axml.get_xml().decode('utf-8')
            matches = PACKAGE.findall(xml)
            ignore_list.update(matches)  # add list to set

        # convert ignore list to smali format
        ignore_list = [Util.to_smali(classname) for classname in ignore_list if classname]

        # iterate through all the smali files
        for filename in Util.progress_bar(self.__smali_files,
                                          description="Retrieving classes from all smali files"):

            with open(filename, "r") as file:
                # identify lines which contains classes
                for line in file:

                    if renamable:
                        class_match = regex.CLASSES.search(line)
                        if class_match is not None:
                            class_name = class_match.group()

                            # skip entire file
                            if not class_name.startswith(package_name):
                                break

                            ignore = False
                            for ignore_class in ignore_list:
                                # skip classes in ignore_class
                                if (class_name.startswith(ignore_class[:-1])
                                        or "/ui/" in class_name
                                        or "/widget/" in class_name
                                        or "/models/" in class_name):
                                    ignore = True
                                    break

                                # skip R classes
                                class_tokens = regex.SPLIT_CLASS.split(class_name)
                                class_tokens = [token.replace(";", "") for token in class_tokens]
                                
                                if "R" in class_tokens:
                                    ignore = True
                                    break

                            if not ignore:
                                self._class_names.add(class_name)

                        if "# virtual methods" in line:
                            break

                    else:
                        if match := regex.CLASSES.search(line):
                            class_name = match.group()[:-1]
                            self._class_names.add(class_name)

        # convert set to tuple to prevent modification
        self._class_names = tuple(self._class_names)
        return self._class_names
