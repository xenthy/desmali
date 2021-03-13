from desmali.tools import Apktool, Zipalign, Apksigner, Dex2jar, Dissect
from desmali.obfuscate import *
from desmali.extras import logger


def main():
    apktool: Apktool = Apktool()
    apktool.decode(apk_path="original.apk",
                   output_dir_path="./.tmp/apktool",
                   force=True)

    ###### obfuscate stuff ######
    dissect: Dissect = Dissect("./.tmp/apktool")

    """ PURGE LOGS """
    purge_logs: PurgeLogs = PurgeLogs(dissect)
    purge_logs.run(a=True, d=True, e=True, i=True, v=True, w=True, wtf=True)

    """ INJECT GOTOS IN METHODS """
    goto_inject: GotoInjector = GotoInjector(dissect)
    goto_inject.run()

    """ REORDER LABELS """
    reorder_labels: ReorderLabels = ReorderLabels(dissect)
    reorder_labels.run()

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

    # for debugging
    dex2jar = Dex2jar()
    dex2jar.to_jar(input_apk_path="./.tmp/signed.apk",
                   output_jar_path="./.tmp/signed.jar")
    # import pty
    # pty.spawn("/bin/bash")


if __name__ == "__main__":
    logger.info("__INIT__")
    main()

    # testing getting of method names
    # dissect: Dissect = Dissect("./.tmp/apktool")
    # dissect.method_names()
    # dissect.method_names()


logger.info("__EOF__")
