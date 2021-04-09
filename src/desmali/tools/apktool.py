import os
import shutil
import subprocess
import tempfile
from typing import List

from desmali.extras import logger


class Apktool():
    """
    A python wrapper to use the "apktool" tool with
    parameters.

    [IMPORTANT] apktool has to be installed
    """

    def __init__(self):
        self.apktool_path: str = "apktool"
        full_apktool_path = shutil.which(self.apktool_path)

        if full_apktool_path is None:
            logger.error(f"apktool not found {self.apktool_path!r}")
            exit()
        else:
            self.apktool_path = full_apktool_path

    def decode(self, apk_path: str, output_dir_path: str, force: bool = False) -> None:
        """
        Decode an APK file

            Parameters:
                apk_path (str): Path to an APK file
                output_dir_path (str): Directory to store the decoded APK
                force (bool): Overwrites a directory if it exists

            Returns:
                None
        """

        # check if file exists
        if not os.path.isfile(apk_path):
            logger.error(f"Unable to find file {apk_path!r}")
            raise FileNotFoundError(f"Unable to find file {apk_path!r}")

        # check if directory exists, else create it
        if not os.path.isdir(output_dir_path):
            logger.info(f"creating new directory at {output_dir_path!r}")
            os.mkdir(output_dir_path)

        decode: List[str] = [
            self.apktool_path,
            "d",
            "--no-res",  # do not decode resources
            "--frame-path",
            tempfile.gettempdir(),
            apk_path,
            "--no-debug-info",
            "-o",
            output_dir_path,
        ]

        # force delete destination directory
        if force:
            logger.verbose(f"force flag set, {output_dir_path!r} directory will be overwritten")
            decode.insert(2, "--force")

        try:
            decode_command: str = " ".join(decode)
            logger.info(f"decoding apk: {apk_path!r} -> {output_dir_path!r}")
            logger.verbose(f"{decode_command}")

            output: str = subprocess.check_output(decode, stderr=subprocess.STDOUT, input=b"\n").strip()

            if b"Exception in thread" in output:
                # if apktool reports an exception
                raise subprocess.CalledProcessError(1, decode, output)

            return output.decode(errors="replace")
        except Exception as e:
            logger.error("Error decoding: {0}".format(
                e.output.decode(errors="replace") if e.output else e
            ))
            raise

    def build(self, source_dir_path: str, output_apk_path: str) -> None:
        """
        Build an APK file

            Parameters:
                source_dir_path (str): Path to an decoded APK directory
                output_apk_path (str): Path to store the built APK

            Returns:
                None
        """

        build: List[str] = [
            self.apktool_path,
            "b",
            "--frame-path",
            tempfile.gettempdir(),
            "--force-all",
            source_dir_path,
            "--match-original",
            "-o",
            output_apk_path,
        ]

        try:
            build_command = " ".join(build)
            logger.info(f"building apk: {source_dir_path!r} -> {output_apk_path!r}")
            logger.verbose(f"{build_command}")

            output = subprocess.check_output(build, stderr=subprocess.STDOUT, input=b"\n").strip()
            if (b"brut.directory.PathNotExist: " in output or b"Exception in thread " in output):
                raise subprocess.CalledProcessError(1, build, output)

            return output.decode(errors="replace")
        except subprocess.CalledProcessError as e:
            logger.error(
                "Error during build command: {0}".format(
                    e.output.decode(errors="replace") if e.output else e
                )
            )
            raise
        except Exception as e:
            logger.error(f"Error during building: {e}")
            raise
