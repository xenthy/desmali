import os
import shutil
import subprocess
from typing import List

from desmali.extras import logger


class Apksigner:
    """
    A python wrapper to use the "apksigner" tool with
    parameters. 

    [IMPORTANT] apksigner has to be installed
    """

    def __init__(self):
        self.apksigner_path: str = "apksigner"
        full_apksigner_path: str = shutil.which(self.apksigner_path)

        if full_apksigner_path is None:
            logger.error(f"apksigner not found {self.apksigner_path!r}")
            exit()
        else:
            self.apksigner_path = full_apksigner_path

    def sign(self,
             input_apk_path: str,
             output_apk_path: str,
             keystore_path: str,
             ks_pass: str,
             key_pass: str) -> None:
        """
        Signs a given APK with a .jks file and their corresponding
        ks/key pass

            Parameters:
             input_apk_path (str): Path to the unsigned APK file
             output_apk_path (str): Path to the signed APK file upon completion
             keystore_path (str): Path to the .jks keystore file
             ks_pass (str): KS password
             key_pass (str): Key password

            Returns:
                None
        """

        # check if apk file exists
        if not os.path.isfile(input_apk_path):
            logger.error(f"Unable to find file {input_apk_path!r}")
            raise FileNotFoundError(f"Unable to find file {input_apk_path!r}")

        # check if key store file exists
        if not os.path.isfile(keystore_path):
            logger.error(f"Unable to find file {keystore_path!r}")
            raise FileNotFoundError(f"Unable to find file {keystore_path!r}")

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
            sign_command: str = " ".join(sign)
            logger.info(f"signing apk: {input_apk_path!r} -> {output_apk_path!r}")
            logger.verbose(f"{sign_command}")

            output: str = subprocess.check_output(sign, stderr=subprocess.STDOUT, input=b"\n").strip()

            if (b"unable to find an interpreter" in output or b"Exception in thread " in output):
                raise subprocess.CalledProcessError(1, sign, output)

            return output.decode(errors="replace")
        except subprocess.CalledProcessError as e:
            error_output = e.output.decode(errors="replace") if e.output else e

            logger.error(f"Error during build command: {error_output}")
            raise
        except Exception as e:
            logger.error(f"Error during apk signing: {e}")
            raise
