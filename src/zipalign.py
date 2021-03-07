import os
import shutil
import subprocess
from typing import List

from logger import logger


class Zipalign:
    def __init__(self):
        if "ZIPALIGN_PATH" in os.environ:
            self.zipalign_path: str = os.environ["ZIPALIGN_PATH"]
        else:
            self.zipalign_path: str = "zipalign"

        full_zipalign_path: str = shutil.which(self.zipalign_path)

        if full_zipalign_path is None:
            logger.error(f"zipalign not found \"{self.zipalign_path}\"")
            exit()
        else:
            self.zipalign_path = full_zipalign_path

    def align(self, input_apk_path: str, output_apk_path: str):
        # check if file exists
        if not os.path.isfile(input_apk_path):
            logger.error(f"Unable to find file {input_apk_path}")
            raise FileNotFoundError(f"Unable to find file {input_apk_path}")

        zipalign: List[str] = [
            self.zipalign_path,
            "-v",
            "4",
            input_apk_path,
            output_apk_path,
        ]

        try:
            align_command = " ".join(zipalign)
            logger.info(f"zipaligning apk: \"{input_apk_path}\" -> \"{output_apk_path}\"")
            logger.debug(f"{align_command}")

            output = subprocess.check_output(zipalign, stderr=subprocess.STDOUT, input=b"\n").strip()
            if (b"brut.directory.PathNotExist: " in output or b"Exception in thread " in output):
                # report exception raised in zipalign
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
            logger.error("Error during zipaligning: {0}".format(e))
            raise
