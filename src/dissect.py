import os
from typing import List

from logger import logger


class Dissect:
    def __init__(self, decoded_dir_path: str):
        # check if input directory exists
        if not os.path.isdir(decoded_dir_path):
            logger.error(f"directory does not exist \"{decoded_dir_path}\"")
            raise NotADirectoryError(f"directory does not exist \"{decoded_dir_path}\"")
        else:
            self.decoded_dir_path = decoded_dir_path

        # run default methods

    def smali_files(self) -> List[str]:
        # check if function has already been executed
        if hasattr(self, "_smali_files"):
            return self.__smali_files

        logger.info("getting all .smali files from decoded directory")

        self.__smali_files: List[str] = [
            os.path.join(root, file_name)
            for root, dir_names, file_names in os.walk(self.decoded_dir_path)
            for file_name in file_names
            if file_name.endswith(".smali")
        ]

        return self.__smali_files
