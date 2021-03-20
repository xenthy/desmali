import os
from binascii import hexlify
from Crypto.Cipher import AES
from desmali.tools import Dissect
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
from desmali.extras import Util, logger, regex

class StringConstants:
    def __init__(self, dissect: Dissect):
        self._dissect = dissect
        self.key = "m';|!)Kc)~9aCw*U;w40syK%9)P<q>83" # TODO: Randomly generate key
        self.com_path = None
        self.decryptor_added = False

    def encryptString(self, plaintext):
        plaintext = plaintext.encode(errors="replace").decode("unicode_escape")
        key = PBKDF2(
                password=self.key,
                salt=self.key.encode(),
                dkLen=32,
                count=128)
        ciphertext = hexlify(AES.new(key=key, mode=AES.MODE_ECB).encrypt(pad(plaintext.encode(errors="replace"), AES.block_size))).decode()
        return ciphertext
    
    def obfuscate(self):
        skipped_files = 0
        files_processed = 0
        dest_dir = None
        strings_encrypted = set()
        for filename in Util.progress_bar(self._dissect.smali_files(), description="Encrypting strings"):

            skip_file_search = regex.SKIP_FILE.search(os.path.dirname(filename))
            if skip_file_search: 
                skipped_files += 1
                continue
            else:
                files_processed += 1

            com_path_search = regex.COM_PATH.search(os.path.dirname(filename))
            if com_path_search:
                com_path = com_path_search[1] 
                dest_dir = os.path.dirname(filename)
                if "MainActivity.smali" in filename:
                    self.com_path = com_path
            else:
                continue

            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                static_index = []
                static_name = []
                static_val = []

                const_index = []
                const_register = []
                const_val = []

                # class_name = []
                class_name = None
                direct_methods_line = -1
                static_constructor_line = -1
                locals_count = 0

                # logger.info(f"Encrypting strings in {filename}:{len(lines)}")
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

                    static_str = regex.STATIC_STRING.match(line)
                    if static_str and static_str.group("string_value"):
                        static_index.append(line_num)
                        static_name.append(static_str.group("string_name"))
                        static_val.append(static_str.group("string_value"))

                    locals_match = regex.LOCALS.match(line)
                    if locals_match:
                        locals_count = int(locals_match.group("local_count"))
                        continue

                    const_str = regex.CONST_STRING.match(line)
                    if const_str and const_str.group("string"):
                        reg_type = const_str.group("register")[:1]
                        reg_num = int(const_str.group("register")[1:])
                        if (reg_type == "v" and reg_num <=15) or (reg_type == "p" and reg_num + locals_count <=15):
                            # Non-empty string with register <= 15 is found
                            const_index.append(line_num)
                            const_register.append(const_str.group("register"))
                            const_val.append(const_str.group("string"))


                # Encrypt const string
                for list_num, const_line in enumerate(const_index):
                    lines[const_line] = (
                            '\tconst-string/jumbo {register}, "{ciphertext}"\n'
                            "\n\tinvoke-static {{{register}}}, "
                            "Lcom/{com_path}/DecryptString"
                            ";->decryptString(Ljava/lang/String;)Ljava/lang/String;\n"
                            "\n\tmove-result-object {register}\n".format(
                                register=const_register[list_num], 
                                ciphertext = self.encryptString(const_val[list_num]),
                                com_path=com_path,
                                )
                            )

                    strings_encrypted.add(const_val[list_num])


                # Encrypt static string
                static_enc_code = ""
                for list_num, static_line in enumerate(static_index):
                    lines[static_line] = f"{lines[static_line].split(' = ')[0]}\n"


                    static_enc_code += (
                            '\tconst-string/jumbo v0, "{ciphertext}"\n'
                            "\n\tinvoke-static {{v0}}, "
                            "Lcom/{com_path}/DecryptString"
                            ";->decryptString(Ljava/lang/String;)Ljava/lang/String;\n"
                            "\n\tmove-result-object v0\n"
                            "\n\tsput-object v0, {class_name}->"
                            "{string_name}:Ljava/lang/String;\n\n".format(
                                ciphertext=self.encryptString(static_val[list_num]),
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
                            lines[static_constructor_line + 1] = "\t.locals 1\n"

                        lines[static_constructor_line +2] = "\n{0}".format(static_enc_code)
                else:
                    if direct_methods_line != -1:
                        new_constructor_line = direct_methods_line
                    else:
                        new_constructor_line = len(lines) - 1 

                    lines[new_constructor_line] = (
                            "{original}"
                            ".method static constructor <clinit>()V\n"
                            "\t.locals 1\n\n"
                            "{enc_code}"
                            "\treturn-void\n"
                            ".end method\n\n".format(
                                original=lines[new_constructor_line],
                                enc_code = static_enc_code,
                                )
                            )

                # Overwrite smali file with obfuscated lines 
                with open(filename, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

            except Exception as e:
                logger.error(f"[{filename}] String Encryption Error {e}")

        # Write decryptor file
        
        if strings_encrypted and not self.decryptor_added and self.com_path:
            if not dest_dir:
                # ALTERNATIVE: dest_dir = os.path.dirname(self._dissect.smali_files()[0])
                dest_dir = os.path.dirname(self._dissect.smali_files()[0])             

            dest_file = os.path.join(dest_dir, "DecryptString.smali")
            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(getSmaliDecryptor(self.key, self.com_path))

            self.decryptor_added = True
            logger.info("String Decryptor added successfully")
        else:
            logger.info("String Decryptor not added, no issue if there are no encryptiion done. Check number of skipped files.")
        
        logger.info(f"Encryption Strings files skipped: {skipped_files}")
        logger.info(f"Encryption Strings files processed: {files_processed}")
        

# TODO: find new place to store smali decryptor resource?
def getSmaliDecryptor(key, com_path):
    with open(os.path.join(os.path.dirname(__file__),"resources","DecryptString.smali"), 'r') as f:
        cont = f.read()
        return (cont.replace("This-key-need-to-be-32-character",key)).replace("decryptstringmanager",com_path)
