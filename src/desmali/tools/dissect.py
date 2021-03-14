import os
from typing import List, Set, Tuple

from desmali.extras import logger, Util, regex


class Dissect:
    def __init__(self, decoded_dir_path: str):
        # check if input directory exists
        if not os.path.isdir(decoded_dir_path):
            logger.error(f"directory does not exist \"{decoded_dir_path}\"")
            raise NotADirectoryError(f"directory does not exist \"{decoded_dir_path}\"")
        else:
            self.decoded_dir_path = decoded_dir_path

        ### INITIAL OPERATIONS ###
        # locate all smali files
        self.smali_files()

        # set initial number of lines in all the smali files
        self._initial_num_lines = len(self)

    def __len__(self) -> int:
        # define variable
        num_of_lines: int = 0

        # count the number of non-empty lines
        for filename in Util.progress_bar(self._smali_files,
                                          description="Calculating number of smali lines"):
            with open(filename, "r", newline="") as file:
                for line in file:
                    if line.strip():
                        num_of_lines += 1
        return num_of_lines

    def smali_files(self) -> Tuple[str]:
        """
        Get all smali file paths recursively from the specified directory
        """
        # check if function has already been executed
        if hasattr(self, "_smali_files"):
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

    def method_names(self, skip_virtual_methods: bool = False) -> Tuple[str]:
        # check if function has already been executed
        if hasattr(self, "_method_names"):
            return self._method_names

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
                    # skip virtual methods if @param:skip_virtual_methods is set to true.
                    # virtual methods are always at the bottom of the smali file, hence,
                    # 'break' is used
                    if skip_virtual_methods and line.startswith("# virtual methods"):
                        break

                    if (match := regex.METHOD.match(line)):
                        method_name = match.group("name")
                        self._method_names.add(method_name)

        # convert set to tuple to prevent modification
        self._method_names = tuple(self._method_names)

        return self._method_names
