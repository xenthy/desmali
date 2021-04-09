import os
import shutil
import subprocess
from typing import List

from desmali.extras import logger


class Zipalign:
    """
    A python wrapper to use the "zipalign" tool with
    parameters.

    [IMPORTANT] zipalign has to be installed
    """

    def __init__(self):
        self.zipalign_path: str = "zipalign"
        full_zipalign_path: str = shutil.which(self.zipalign_path)

        if full_zipalign_path is None:
            logger.error(f"zipalign not found {self.zipalign_path!r}")
            exit()
        else:
            self.zipalign_path = full_zipalign_path

    def align(self, input_apk_path: str, output_apk_path: str) -> None:
        """
        Zipaligns an APK file

            Parameters:
                input_apk_path (str): Path to an unaligned APK file
                output_dir_path (str): Path to the output aligned APK file

            Returns:
                None
        """
        # check if file exists
        if not os.path.isfile(input_apk_path):
            logger.error(f"Unable to find file {input_apk_path!r}")
            raise FileNotFoundError(f"Unable to find file {input_apk_path!r}")

        zipalign: List[str] = [
            self.zipalign_path,
            "-f",  # overwrite existing file
            "-v",
            "4",
            input_apk_path,
            output_apk_path,
        ]

        try:
            align_command: str = " ".join(zipalign)
            logger.info(f"zipaligning apk: {input_apk_path!r} -> {output_apk_path!r}")
            logger.verbose(f"{align_command}")

            output: str = subprocess.check_output(zipalign, stderr=subprocess.STDOUT, input=b"\n").strip()
            if (b"brut.directory.PathNotExist: " in output or b"Exception in thread " in output):
                raise subprocess.CalledProcessError(1, zipalign, output)

            return output.decode(errors="replace")
        except subprocess.CalledProcessError as e:
            logger.error(
                "Error during build command: {0}".format(
                    e.output.decode(errors="replace") if e.output else e
                )
            )
            raise
        except Exception as e:
            logger.error(f"Error during zipaligning: {e}")
            raise
