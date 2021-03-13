import sys
import re
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
        with fileinput.input(filename, inplace=True) as f:
            for line in f:
                if self.STRING_FIELD in line:
                    # TODO: Process the line and extract the value
                    value = self.extractValue(line)
                    if value:
                        # TODO: Encrypt the value and replace value of line with encrypted content, calling deobfuscator
                        # replacement = encrypt('field', value)
                        # print(replacement, end = '\n')

                        # NOTE: if changed to deobfus function call, modify to end = '\n'
                        print(line.replace(value,"changed"), end = '') 
                        self.SFIELD_REGISTRY.append({filename, fileinput.lineno})

                elif self.STRING_LITERAL in line:
                    # TODO: Process the line and extract the value
                    value = self.extractValue(line)
                    if value:
                        # TODO: Encrypt the value and replace value of line with encrypted content, calling deobfuscator
                        # replacement = encrypt('literal', value)
                        # print(replacement, end = '\n')

                        # NOTE: if changed to deobfus function call, modify to end = '\n'
                        print(line.replace(value,"changed"), end = '')
                        self.SLITERAL_REGISTRY.append({filename, fileinput.lineno})

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
