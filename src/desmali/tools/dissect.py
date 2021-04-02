import os
from typing import List, Set, Tuple, Dict

from desmali.extras import logger, Util, regex

from pyaxmlparser import APK


class Dissect:
    def __init__(self, original_dir_path: str, decoded_dir_path: str):
        # check if input directory exists
        if not os.path.isdir(original_dir_path):
            logger.error(f"directory does not exist \"{original_dir_path}\"")
            raise NotADirectoryError(f"directory does not exist \"{original_dir_path}\"")
        else:
            self.original_dir_path = original_dir_path

        if not os.path.isdir(decoded_dir_path):
            logger.error(f"directory does not exist \"{decoded_dir_path}\"")
            raise NotADirectoryError(f"directory does not exist \"{decoded_dir_path}\"")
        else:
            self.decoded_dir_path = decoded_dir_path

        ### INITIAL OPERATIONS ###
        # locate all smali files
        self.smali_files()

        # map original path and decoded path
        self.dir_mapping = self._set_mapping()

        # set initial number of lines in all the smali files
        self._initial_num_lines = len(self)

    def __len__(self) -> int:
        # define variable
        num_of_lines: int = 0

        # count the number of non-empty lines
        for filename in Util.progress_bar(self._smali_files,
                                          description="Calculating number of smali lines"):
            with open(filename, "r", newline="") as file:
                num_of_lines += sum(1 for line in file if line.strip())

        return num_of_lines

    def _set_mapping(self):
        # dir_mapping dictionary - {decoded_path: original_path}
        dir_mapping: Dict[str, str] = dict()

        for file in Util.progress_bar(self.smali_files(),
                                      description="Mapping original/decoded directories"):
            dir_mapping[file] = file.replace(self.decoded_dir_path,
                                             self.original_dir_path)

        return dir_mapping

    def update_mapping(self, old_path, new_path):
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
        self._smali_files = tuple(self._smali_files)

        return self._smali_files

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
        self._method_names = tuple(self._method_names)
        return self._method_names

    def class_names(self, renamable: bool = False) -> Tuple[str]:
        # check if smali_files() has already been executed
        if not hasattr(self, "__smali_files"):
            self.__smali_files: List[str] = self.smali_files()

        logger.verbose("getting all class names from the list of smali files")

        # store all class names into a list
        self._class_names: Set[str] = set()

        # get all activities in xml file (cannot be renamed)
        apk = APK("./original.apk")
        activities = apk.get_activities()
        activities = [a.split(".")[-1] for a in activities]

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

                            if (class_name.startswith("Landroid")
                                    or class_name.startswith("Ljava")
                                    or class_name.startswith("Lkotlin")
                                    or class_name.startswith("Lcom/google")
                                    or class_name.startswith("Lorg")):

                                break

                            for index, a in enumerate(activities):
                                if a in class_name[1:-1]:
                                    break
                                if index == len(activities)-1:
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
