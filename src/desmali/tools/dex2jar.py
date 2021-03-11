"""
This dex2jar function is only meant for verboseging and not to be
used in the final product
"""

import os
import subprocess
from typing import List

from desmali.extras import logger

INVOKE_PATH = "./bin/dex2jar-2.0/d2j_invoke.sh"
DEX2JAR_PATH = "./bin/dex2jar-2.0/d2j-dex2jar.sh"
DEX2JAR_ERROR_FILE_PATH = "/dev/null"


class Dex2jar():
    def __init__(self):
        # check if the invoke script exists
        if not os.path.isfile(INVOKE_PATH):
            logger.error(f"Unable to find file {INVOKE_PATH}")
            raise FileNotFoundError(f"Unable to find file {INVOKE_PATH}")

        # check if the dex2jar script exists
        if not os.path.isfile(DEX2JAR_PATH):
            logger.error(f"Unable to find file {DEX2JAR_PATH}")
            raise FileNotFoundError(f"Unable to find file {DEX2JAR_PATH}")

    def to_jar(self, input_apk_path: str, output_jar_path: str):
        # check if apk file exists
        if not os.path.isfile(input_apk_path):
            logger.error(f"Unable to find file {input_apk_path}")
            raise FileNotFoundError(f"Unable to find file {input_apk_path}")

        dex2jar: List[str] = [
            DEX2JAR_PATH,
            "--force",      # force overwrite
            input_apk_path,
            "-o",           # output path
            output_jar_path,
            "--exception-file",
            DEX2JAR_ERROR_FILE_PATH
        ]

        try:
            decode_command = " ".join(dex2jar)
            logger.info(f"decompiling apk: \"{input_apk_path}\" -> \"{output_jar_path}\"")
            logger.verbose(f"{decode_command}")

            output = subprocess.check_output(dex2jar, stderr=subprocess.STDOUT, input=b"\n").strip()

            if b"Exception in thread" in output:
                # if dex2jar reports an exception
                raise subprocess.CalledProcessError(1, dex2jar, output)

            return output.decode(errors="replace")
        except Exception as e:
            logger.error("Error decompiling: {0}".format(
                e.output.decode(errors="replace") if e.output else e
            ))
            raise
