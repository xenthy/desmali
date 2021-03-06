import os
import re
import string
import random
from binascii import hexlify

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
from androguard.core.bytecodes.apk import APK

from desmali.abc import Desmali
from desmali.tools import Dissect
from desmali.extras import Util, logger, regex


class StringEncryption(Desmali):
    """Perform encryption of strings in critical activities/codes used in the application 
    
    Args:
        Dissect (obj): Dissect object
    """
    def __init__(self, dissect: Dissect):
        super().__init__(self)
        self._dissect = dissect
        self.decryptor_added = False
        self.package_dir_regex = None

        # Generate a random AES key
        self.key = ''.join(random.choice(string.ascii_letters + string.digits + "';|!()~*%<>") for _ in range(32))

    def encrypt_string(self, plaintext):
        """Return an AES encrypted string

        Encrypt a plaintext string using AES-ECB
        """
        plaintext = plaintext.encode(errors="replace").decode("unicode_escape")
        key = PBKDF2(
            password=self.key,
            salt=self.key.encode(),
            dkLen=32,
            count=128)
        ciphertext = hexlify(AES.new(key=key, mode=AES.MODE_ECB).encrypt(pad(plaintext.encode(errors="replace"), AES.block_size))).decode()
        return ciphertext

    def run(self):
        """
        Main string obfuscation module

        Loops through and encrypts all string entries in smali files
        - skips files in the "android" and "androidx" directories
        """
        skipped_files = 0
        files_processed = 0
        strings_encrypted = set()

        try:
            dest_dir, com_path = self.find_com_path()
        except TypeError:
            logger.error("Invalid destination directory and/or Android Path found")
            logger.warning("Skipping String Encryption as it might break the Android application")
            return

        for filename in Util.progress_bar(self._dissect.smali_files(), description="Encrypting strings"):

            skip_file_search = regex.SKIP_FILE.search(os.path.dirname(filename))

            # Track the number of files skipped/obfuscated (processed)
            if skip_file_search:
                skipped_files += 1
                continue
            else:
                files_processed += 1

            if package_dir := self.package_dir_regex.search(os.path.dirname(filename)):
                files_processed += 1
            else:
                skipped_files += 1
                continue

            try:
                with open(filename, 'r', encoding='utf-8') as target_file:
                    lines = target_file.readlines()

                static_index = []  # Line number of Static String found
                static_name = []  # Variable Name of Static String found
                static_val = []  # Value of Static String found

                const_index = []  # Line number of Constant String found
                const_register = []  # Register of Constant String found
                const_val = []  # Value of Constant String found in register

                class_name = None
                direct_methods_line = -1
                static_constructor_line = -1
                locals_count = 0

                # Identification and storing of important lines in smali file
                for line_num, line in enumerate(lines):
                    if not class_name:
                        class_match = regex.CLASS_NAME.match(line)
                        if class_match:
                            class_name = class_match.group("class_name")
                            continue

                    if line.startswith("# direct methods"):
                        direct_methods_line = line_num
                        continue

                    if line.startswith(".method static constructor <clinit>()V"):
                        static_constructor_line = line_num
                        continue

                    # Identification and indexing of Static String found
                    static_str = regex.STATIC_STRING.match(line)
                    if static_str and static_str.group("string_value"):
                        static_index.append(line_num)
                        static_name.append(static_str.group("string_name"))
                        static_val.append(static_str.group("string_value"))

                    locals_match = regex.LOCALS.match(line)
                    if locals_match:
                        locals_count = int(locals_match.group("local_count"))
                        continue

                    # Identification and indexing of Constant String found
                    const_str = regex.CONST_STRING.match(line)
                    if const_str and const_str.group("string"):
                        reg_type = const_str.group("register")[:1]
                        reg_num = int(const_str.group("register")[1:])
                        if (reg_type == "v" and reg_num <= 15) or (reg_type == "p" and reg_num + locals_count <= 15):
                            # Non-empty string with register <= 15 is found
                            const_index.append(line_num)
                            const_register.append(const_str.group("register"))
                            const_val.append(const_str.group("string"))

                # Encrypt Constant Strings
                for list_num, const_line in enumerate(const_index):
                    lines[const_line] = (
                        '    const-string/jumbo {register}, "{ciphertext}"\n'
                        "\n    invoke-static {{{register}}}, "
                        "L{com_path}/DecryptString"
                        ";->decryptString(Ljava/lang/String;)Ljava/lang/String;\n"
                        "\n    move-result-object {register}\n".format(
                            register=const_register[list_num],
                            ciphertext=self.encrypt_string(const_val[list_num]),
                            com_path=com_path,
                        )
                    )

                    strings_encrypted.add(const_val[list_num])

                # Encrypt Static Strings
                static_enc_code = ""
                for list_num, static_line in enumerate(static_index):
                    lines[static_line] = f"{lines[static_line].split(' = ')[0]}\n"

                    static_enc_code += (
                        '    const-string/jumbo v0, "{ciphertext}"\n'
                        "\n    invoke-static {{v0}}, "
                        "L{com_path}/DecryptString"
                        ";->decryptString(Ljava/lang/String;)Ljava/lang/String;\n"
                        "\n    move-result-object v0\n"
                        "\n    sput-object v0, {class_name}->"
                        "{string_name}:Ljava/lang/String;\n\n".format(
                            ciphertext=self.encrypt_string(static_val[list_num]),
                            com_path=com_path,
                            class_name=class_name,
                            string_name=static_name[list_num],
                        )
                    )

                    strings_encrypted.add(static_val[list_num])

                if static_constructor_line != -1:
                    locals_match = regex.LOCALS.match(lines[static_constructor_line + 1])
                    if locals_match:
                        locals_count = int(locals_match.group("local_count"))
                        if locals_count == 0:
                            lines[static_constructor_line + 1] = "    .locals 1\n"

                        lines[static_constructor_line + 2] = "\n{0}".format(static_enc_code)
                else:
                    if direct_methods_line != -1:
                        new_constructor_line = direct_methods_line
                    else:
                        new_constructor_line = len(lines) - 1

                    lines[new_constructor_line] = (
                        "{original}"
                        ".method static constructor <clinit>()V\n"
                        "    .locals 1\n\n"
                        "{enc_code}"
                        "    return-void\n"
                        ".end method\n\n".format(
                            original=lines[new_constructor_line],
                            enc_code=static_enc_code,
                        )
                    )

                # Overwrite smali file with obfuscated lines
                with open(filename, 'w', encoding='utf-8') as target_file:
                    target_file.writelines(lines)

            except Exception as main_encryption_exception:
                logger.error(f"[{filename}] String Encryption Error {main_encryption_exception}")

        # Write decryptor file (resources/DecryptString.smali) into "com" path directory identified earlier
        if strings_encrypted and not self.decryptor_added and com_path and dest_dir:
            dest_file = os.path.join(dest_dir, "DecryptString.smali")
            with open(dest_file, 'w', encoding='utf-8') as decryptor_file:
                decryptor_file.write(get_smali_decryptor(self.key, com_path))

            self.decryptor_added = True
            logger.verbose("DecryptString.smali added")
            self._dissect.add_smali_file(dest_file)
        else:
            logger.warning("DecryptString.smali not added, no issue if there are no encryption done. Check number of skipped files.")

        logger.verbose(f"{self.__class__.__name__} -> skipped: {skipped_files} | processed: {files_processed}")

    # To find the directory that contains main application's logic
    # Required before encrypting strings and adding smali code
    def find_com_path(self):
        apk = APK(self._dissect.apk_path)
        package_dir = None

        for element in apk.get_activities():
            if "MainActivity" in element:
                package_dir = element.replace(".MainActivity", "").replace(".", "/")
                break

        if not package_dir:
            package_dir = "/".join(apk.get_activities()[0].split(".")[:-1])

        self.package_dir_regex = re.compile(f"{package_dir}")

        com_path = None
        dest_dir = None
        for filename in self._dissect.smali_files():
            path_search = self.package_dir_regex.search(os.path.dirname(filename))
            if path_search and ("MainActivity.smali" or "Activity.smali" in filename):
                dest_dir = os.path.dirname(filename)
                com_path = path_search[0]

                return dest_dir, com_path


def get_smali_decryptor(key, com_path):
    """Return contents of modified smali decryptor

    Retrieve the smali decryptor file and replace placeholder values
    - AES key
    - Android Library Paths
    """
    with open(os.path.join(os.path.dirname(__file__), "resources", "DecryptString.smali"), 'r') as decryptor_resource:
        cont = decryptor_resource.read()

        # Replace the placeholder AES-ECB key with the key that was used to encrypt strings
        return (cont.replace("This-key-need-to-be-32-character", key)).replace("com/decryptstringmanager", com_path)
