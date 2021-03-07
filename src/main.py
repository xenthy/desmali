from apktool import Apktool
from zipalign import Zipalign
from apksigner import Apksigner
from config import DECODED_PATH

from logger import logger
logger.info("__INIT__")


def main():
    apktool = Apktool()
    apktool.decode(apk_path="original.apk",
                   output_dir_path=DECODED_PATH,  # ./apktool/
                   force=True)

    # obfuscate stuff

    apktool.build(source_dir_path=DECODED_PATH,
                  output_apk_path="./modified.apk")

    zipalign = Zipalign()
    zipalign.align(input_apk_path="./modified.apk",
                   output_apk_path="./modified-aligned.apk")

    apksigner = Apksigner()
    apksigner.sign(input_apk_path="./modified-aligned.apk",
                   output_apk_path="./signed.apk",
                   keystore_path="./ict2207-test-key.jks",
                   ks_pass="nim4m4h4om4?",
                   key_pass="nim4m4h4om4?")

    import pty
    pty.spawn("/bin/bash")


if __name__ == "__main__":
    main()

logger.info("__EOF__")
