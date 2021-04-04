import os
import shutil
from distutils.dir_util import copy_tree

from desmali.tools import Apktool, Zipalign, Apksigner, Dex2jar, Dissect
from desmali.obfuscate import *
from desmali.extras import logger


def main():
    APK_PATH = "Memento-1.1.1.apk"

    apktool: Apktool = Apktool()
    apktool.decode(apk_path=APK_PATH,
                   output_dir_path="./.tmp/obfuscated",
                   force=True)

    # clone decoded directory
    if os.path.isdir("./.tmp/original"):
        shutil.rmtree("./.tmp/original")
    copy_tree("./.tmp/obfuscated", "./.tmp/original")

    ###### start obfuscate stuff ######
    dissect: Dissect = Dissect(apk_path=APK_PATH,
                               original_dir_path="./.tmp/original",
                               decoded_dir_path="./.tmp/obfuscated")

    """ PURGE LOGS """
    purge_logs: PurgeLogs = PurgeLogs(dissect)
    purge_logs.run(a=True, d=True, e=True, i=True, v=True, w=True, wtf=True)

    """ INJECT GOTOS IN METHODS """
    goto_inject: GotoInjector = GotoInjector(dissect)
    goto_inject.run()

    """ REORDER LABELS """
    reorder_labels: ReorderLabels = ReorderLabels(dissect)
    reorder_labels.run()

    """ ENCRYPT STRING """
    string_encryption: StringEncryption = StringEncryption(dissect)
    string_encryption.run()

    """ RENAME METHODS"""
    rename_method: RenameMethod = RenameMethod(dissect)
    rename_method.run()

    """ RENAME CLASS """
    rename_class: RenameClass = RenameClass(dissect)
    # rename_class.run()

    """ BOOLEAN ARITHMETIC """
    boolean_arithmetic: BooleanArithmetic = BooleanArithmetic(dissect)
    boolean_arithmetic.run()

    ###### end obfuscate stuff ######

    apktool.build(source_dir_path="./.tmp/obfuscated",
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

    dex2jar = Dex2jar()
    dex2jar.to_jar(input_apk_path="./.tmp/signed.apk",
                   output_jar_path="./.tmp/signed.jar")

    # get number of smali lines before and after obfuscation
    initial_num, current_num = dissect.line_count_info()
    logger.info(f"Line count: Initial: {initial_num} - " +
                f"Current: {current_num} - " +
                "Added: {:.2f}".format(current_num / initial_num))


if __name__ == "__main__":
    logger.info("__INIT__")
    main()

logger.info("__EOF__")
