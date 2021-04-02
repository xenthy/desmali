import os
import shutil
from distutils.dir_util import copy_tree

from desmali.tools import Apktool, Zipalign, Apksigner, Dex2jar, Diff, Dissect
from desmali.obfuscate import *
from desmali.extras import logger

def pre_obfuscate(apk_path : str):
    apktool: Apktool = Apktool()
    apktool.decode(apk_path=apk_path,
                   output_dir_path="./.tmp/original",
                   force=True)

    # clone decoded directory
    if os.path.isdir("./.tmp/obfuscated"):
        shutil.rmtree("./.tmp/obfuscated")
    copy_tree("./.tmp/original", "./.tmp/obfuscated")

    ###### start obfuscate stuff ######
    dissect: Dissect = Dissect("./.tmp/obfuscated")

    return dissect , apktool

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

    # for debugging
    dex2jar = Dex2jar()
    dex2jar.to_jar(input_apk_path="./.tmp/signed.apk",
                   output_jar_path="./.tmp/signed.jar")

    # generate diffs
    diff: Diff = Diff("./.tmp/diff")
    diff.generate_diff(["./.tmp/original/smali/com/example/ict2207_x08/MainActivity.smali"],
                       ["./.tmp/obfuscated/smali/com/example/ict2207_x08/MainActivity.smali"])




def main():

    apktool: Apktool = Apktool()
    apktool.decode(apk_path="original.apk",
                   output_dir_path="./.tmp/original",
                   force=True)

    # clone decoded directory
    if os.path.isdir("./.tmp/obfuscated"):
        shutil.rmtree("./.tmp/obfuscated")
    copy_tree("./.tmp/original", "./.tmp/obfuscated")

    ###### start obfuscate stuff ######
    dissect: Dissect = Dissect("./.tmp/obfuscated")

    """ PURGE LOGS """
    purge_logs: PurgeLogs = PurgeLogs(dissect)
    purge_logs.run(a=True, d=True, e=True, i=True, v=True, w=True, wtf=True)

    """ RENAME METHODS"""
    rename_method: RenameMethod = RenameMethod(dissect)
    rename_method.run()

    """ RENAME CLASS """
    rename_class: RenameClass = RenameClass(dissect)
    # rename_class.run()

    """ ENCRYPT STRING """
    string_encryption: StringEncryption = StringEncryption(dissect)
    string_encryption.run()

    """ INJECT GOTOS IN METHODS """
    goto_inject: GotoInjector = GotoInjector(dissect)
    goto_inject.run()

    """ FAKE BRANCH """
    fake_branch: FakeBranch = FakeBranch(dissect)
    fake_branch.run()

    """ REORDER LABELS """
    reorder_labels: ReorderLabels = ReorderLabels(dissect)
    reorder_labels.run()

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
    dex2jar = Dex2jar()
    dex2jar.to_jar(input_apk_path="./.tmp/signed.apk",
                   output_jar_path="./.tmp/signed.jar")

    # generate diffs
    diff: Diff = Diff("./.tmp/diff")
    diff.generate_diff(["./.tmp/original/smali/com/example/ict2207_x08/MainActivity.smali"],
                       ["./.tmp/obfuscated/smali/com/example/ict2207_x08/MainActivity.smali"])

    # get number of smali lines before and after obfuscation
    initial_num, current_num = dissect.line_count_info()
    logger.info(f"Line count: Initial: {initial_num} - " +
                f"Current: {current_num} - " +
                "Added: {:.2f}".format(current_num / initial_num))


if __name__ == "__main__":
    logger.info("__INIT__")
    main()

    # testing getting of method names
    # dissect: Dissect = Dissect("./.tmp/apktool")
    # dissect.method_names()
    # dissect.method_names()


logger.info("__EOF__")
