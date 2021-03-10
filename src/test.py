from desmali.tools import Apktool, Zipalign, Apksigner, Dissect

from desmali.obfuscate import *

from config import DECODED_PATH

from desmali.extras import logger
logger.info("__INIT__")


def main():
    apktool: Apktool = Apktool()
    apktool.decode(apk_path="original.apk",
                   output_dir_path="./.tmp/apktool",  # ./apktool/
                   force=True)

    ###### obfuscate stuff ######
    """ PURGE LOGS """
    dissect: Dissect = Dissect("./tmp/apktool")
    purge_logs: PurgeLogs = PurgeLogs(dissect)
    purge_logs.run(a=False, d=True, e=False, i=False, v=True, w=False, wtf=True)
    ###### obfuscate stuff ######

    apktool.build(source_dir_path="./.tmp/apktool",
                  output_apk_path="./.tmp/modified.apk")

    zipalign: Zipalign = Zipalign()
    zipalign.align(input_apk_path="./.tmp/modified.apk",
                   output_apk_path="./.tmp/modified-aligned.apk")

    apksigner: Apksigner = Apksigner()
    apksigner.sign(input_apk_path="./.tmp/modified-aligned.apk",
                   output_apk_path="./.tmp/signed.apk",
                   keystore_path="./ict2207-test-key.jks",
                   ks_pass="nim4m4h4om4?",
                   key_pass="nim4m4h4om4?")


if __name__ == "__main__":
    main()

logger.info("__EOF__")
