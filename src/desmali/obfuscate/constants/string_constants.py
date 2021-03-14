import sys
import re
from desmali.extras import Util, logger
import fileinput

class StringConstants:
    def __init__(self):
        self.STRING_FIELD = "java/lang/String"
        self.STRING_LITERAL = "const-string"
        self.SFIELD_REGISTRY = []
        self.SLITERAL_REGISTRY = []
        # TODO: Generate replacement values after deobfuscator function generated and can be called
        self.SFIELD_REPLACEMENT = []
        self.SLITERAL_REPLACEMENT = []

    # TODO: Change filename to dynamic/full path in registries
    def obfuscate(self, filename):
        # with fileinput.input(filename, inplace=True) as f:
        with Util.file_input(filename) as f:
            for line_num, line in enumerate(f):
                if self.STRING_FIELD in line:
                    # TODO: Process the line and extract the value
                    value = self.extractValue(line)
                    if value:
                        # TODO: Encrypt the value and replace value of line with encrypted content, calling deobfuscator
                        # replacement = encrypt('field', value)
                        # print(replacement, end = '\n')

                        # NOTE: if changed to deobfus function call, modify to end = '\n'
                        # print(line.replace(value,"changed"), end = '') 
                        print("invoke-static {}, LClass3;->getObfuString()Ljava/lang/String;", end = '\n')
                        print("move-result-object v0", end = '\n')
                        self.SFIELD_REGISTRY.append({filename, line_num})

                elif self.STRING_LITERAL in line:
                    # TODO: Process the line and extract the value
                    value = self.extractValue(line)
                    if value:
                        # TODO: Encrypt the value and replace value of line with encrypted content, calling deobfuscator
                        # replacement = encrypt('literal', value)
                        # print(replacement, end = '\n')

                        # NOTE: if changed to deobfus function call, modify to end = '\n'
                        # print(line.replace(value,"changed"), end = '')
                        print("invoke-static {}, LClass3;->getObfuString()Ljava/lang/String;", end = '\n')
                        print("move-result-object v0", end = '\n')
                        self.SLITERAL_REGISTRY.append({filename, line_num})
                        

                else:
                    print(line, end = '')


    def extractValue(self, line):
        found = re.search("\"(.+)\"", line)
        if found:
            return found.group(1)
        else:
            return 0

# sc = StringConstants()
# sc.obfuscate('./test.smali')
