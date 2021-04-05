import os
import shutil
from distutils.dir_util import copy_tree

from desmali.tools import Apktool, Zipalign, Apksigner, Dex2jar, Dissect
from desmali.obfuscate import *
from desmali.extras import logger


def pre_obfuscate(apk_path: str):
    apktool: Apktool = Apktool()
    apktool.decode(apk_path=apk_path,
                   output_dir_path="./.tmp/original",
                   force=True)

    # clone decoded directory
    if os.path.isdir("./.tmp/obfuscated"):
        shutil.rmtree("./.tmp/obfuscated")
    copy_tree("./.tmp/original", "./.tmp/obfuscated")

    ###### start obfuscate stuff ######
    dissect: Dissect = Dissect(apk_path=apk_path,
                               original_dir_path="./.tmp/original",
                               decoded_dir_path="./.tmp/obfuscated")

    return dissect, apktool


def post_obfuscate(apktool: Apktool, keystore_path: str, ks_pass: str, key_pass: str):
    apktool.build(source_dir_path="./.tmp/obfuscated",
                  output_apk_path="./.tmp/modified.apk")

    zipalign: Zipalign = Zipalign()
    zipalign.align(input_apk_path="./.tmp/modified.apk",
                   output_apk_path="./.tmp/modified-aligned.apk")

    apksigner: Apksigner = Apksigner()
    apksigner.sign(input_apk_path="./.tmp/modified-aligned.apk",
                   output_apk_path="./.tmp/signed.apk",
                   keystore_path=keystore_path,
                   ks_pass=ks_pass,
                   key_pass=key_pass)

    # # for debugging
    # dex2jar = Dex2jar()
    # dex2jar.to_jar(input_apk_path="./.tmp/signed.apk",
    #                output_jar_path="./.tmp/signed.jar")

    # decompile signed apk to obfuscated folder for updated smali file name
    apktool.decode(apk_path="./.tmp/signed.apk",
                   output_dir_path="./.tmp/obfuscated",
                   force=True)


def main():
    # APK_PATH = "AdAway-5.5.1-210402.apk"
    APK_PATH = "Boost-1.10.2.apk"
    # APK_PATH = "Memento-1.1.1.apk"
    # APK_PATH = "wsy.apk"
    # APK_PATH = "original.apk"

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
    reorder_labels: RandomiseLabels = RandomiseLabels(dissect)
    reorder_labels.run()

    """ ENCRYPT STRING """
    string_encryption: StringEncryption = StringEncryption(dissect)
    string_encryption.run()

    """ RENAME METHODS"""
    rename_method: RenameMethod = RenameMethod(dissect)
    rename_method.run()

    """ RENAME CLASS """
    rename_class: RenameClass = RenameClass(dissect)
    rename_class.run()

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

    # for debugging
    # dex2jar = Dex2jar()
    # dex2jar.to_jar(input_apk_path="./.tmp/signed.apk",
    #                output_jar_path="./.tmp/signed.jar")

    # decompile obfuscated app to get new smali
    apktool.decode(apk_path="./.tmp/signed.apk",
                   output_dir_path="./.tmp/obfuscated",
                   force=True)
    dissect.smali_files(force=True)

    # get apk file size before and after obfuscation
    initial_size, current_size = dissect.file_size_difference(
        "./.tmp/signed.apk")
    logger.info(f"File size -> Initial: {initial_size:,} bytes - " +
                f"Current: {current_size:,} bytes - " +
                "Increase: {:.2f}x".format(current_size / initial_size))

    # get number of smali lines before and after obfuscation
    initial_num, current_num = dissect.line_count_info()
    logger.info(f"Line count -> Initial: {initial_num:,} - " +
                f"Current: {current_num:,} - " +
                "Increase: {:.2f}x".format(current_num / initial_num))


if __name__ == "__main__":
    logger.info("__INIT__")
    main()

logger.info("__EOF__")
