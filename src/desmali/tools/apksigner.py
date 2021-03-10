import os
import shutil
import subprocess
from typing import List

from desmali.extras import logger


class Apksigner:
    def __init__(self):
        if "APKSIGNER_PATH" in os.environ:
            self.apksigner_path: str = os.environ["APKSIGNER_PATH"]
        else:
            self.apksigner_path: str = "apksigner"

        full_apksigner_path: str = shutil.which(self.apksigner_path)

        if full_apksigner_path is None:
            logger.error(f"apksigner not found \"{self.apksigner_path}\"")
            exit()
        else:
            self.apksigner_path = full_apksigner_path

    def sign(self,
             input_apk_path: str,
             output_apk_path: str,
             keystore_path: str,
             ks_pass: str,
             key_pass: str):
        # check if apk file exists
        if not os.path.isfile(input_apk_path):
            logger.error(f"Unable to find file {input_apk_path}")
            raise FileNotFoundError(f"Unable to find file {input_apk_path}")

        # check if key store file exists
        if not os.path.isfile(keystore_path):
            logger.error(f"Unable to find file {keystore_path}")
            raise FileNotFoundError(f"Unable to find file {keystore_path}")

        sign: List[str] = [
            "jarwrapper",
            self.apksigner_path,
            "sign",
            "--ks",
            keystore_path,
            "--ks-pass",
            f"pass:{ks_pass}",
            "--key-pass",
            f"pass:{key_pass}",
            "--out",
            output_apk_path,
            input_apk_path
        ]

        try:
            sign_command = " ".join(sign)
            logger.info(f"signing apk: \"{input_apk_path}\" -> \"{output_apk_path}\"")
            logger.debug(f"{sign_command}")

            output = subprocess.check_output(sign, stderr=subprocess.STDOUT, input=b"\n").strip()

            if (b"unable to find an interpreter" in output or b"Exception in thread " in output):
                # peport exception raised in apksigner
                raise subprocess.CalledProcessError(1, sign, output)

            return output.decode(errors="replace")
        except subprocess.CalledProcessError as e:
            error_output = e.output.decode(errors="replace") if e.output else e

            # workaround for some binfmt-support issues
            # if "unable to find an interpreter" in error_output:
            #     logger.info("java interpreter not configured correctly")
            #     sign.insert(0, "jarwrapper")
            #     sign_command = " ".join(sign)

            #     logger.info(f"signing apk using fallback method: \"{input_apk_path}\" -> \"{output_apk_path}\"")
            #     logger.debug(f"{sign_command}")
            #     output = subprocess.check_output(sign, stderr=subprocess.STDOUT, input=b"\n").strip()
            # else:
            logger.error(f"Error during build command: {error_output}")
            raise
        except Exception as e:
            logger.error("Error during apk signing: {0}".format(e))
            raise

    def verify(self):
        pass
