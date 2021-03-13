import re
from random import shuffle, randrange
from typing import List, Dict

from desmali.tools import Dissect
from desmali.extras import logger, Util


class ReorderLabels:
    def __init__(self, dissect: Dissect):
        self._dissect = dissect

    def run(self):
        logger.info(f"*** INIT {self.__class__.__name__} ***")

        ### regex dump ###
        # match methods
        pattern_method = re.compile(r"\.method.+?(?P<name>\S+?)" +
                                    r"\((?P<args>\S*?)\)" +
                                    r"(?P<return>\S+)",
                                    re.UNICODE)

        # :goto_0
        pattern_label = re.compile(r"^[ ]{4}(?P<name>:.+)")

        # goto :goto_0
        pattern_goto = re.compile(r"^[\t ]+(?P<name>goto :.+)")

        # if-ltz p1, :cond_2
        pattern_if = re.compile(r"^[\t ]+if-.+(?P<name>:.+)")

        # variable declarations
        in_method: bool = False
        reached_first_label: bool = False
        labels: List[List[str]] = list()
        last_is_goto: bool = False

        for filename in Util.progress_bar(self._dissect.smali_files(),
                                          description="Testing some shit"):

            logger.debug(f"reordering file: {filename}")

            with Util.inplace_file(filename) as file:
                for line in file:
                    # check if line is within a method
                    if not in_method:
                        if pattern_method.match(line):
                            in_method = True
                        file.write(line)
                        continue

                    # append declarations of each method to method_start
                    if pattern_label.match(line):
                        reached_first_label = True
                        labels.append(list())
                        labels[-1].append(line)
                        continue

                    # write line to file if the first label in the method has
                    # not been reached
                    if not reached_first_label:
                        file.write(line)
                        # skip empty lines
                        if line == '\n':
                            continue

                        # check if the last line in a label is a goto instruction
                        last_is_goto = True if pattern_goto.match(line) else False
                        continue

                    # reorder and write the label blocks to the file if the end
                    # of the method has been reached
                    if ".end method" in line:
                        self._write_labels(file, labels, last_is_goto)
                        file.write(line)

                        # reset variables for next method
                        labels = list()
                        in_method = False
                        reached_first_label = False
                        continue

                    # add line into labels if it is within a label
                    labels[-1].append(line)

    def _write_labels(self, file, labels: List[List[str]], last_is_goto: bool):
        # goto :goto_0
        pattern_goto = re.compile(r"^[\t ]+(?P<name>goto :.+)")
        # :goto_0
        pattern_label = re.compile(r"^[ ]{4}(?P<name>:.+)")
        # return-void. return v0
        pattern_return = re.compile(r"^[ ]{4}return.*")

        # remove empty lines from labels
        labels = [list(filter(self._is_new_line, label)) for label in labels]

        # write first goto
        if not last_is_goto:
            file.write(f"    goto {labels[0][0].strip()}\n\n")

        # insert goto of the next label
        for index in range(0, len(labels) - 1):
            if not pattern_goto.match(labels[index][-1]) and \
                    not pattern_return.match(labels[index][-1]):
                labels[index].append(f"    goto {labels[index + 1][0].strip()}\n")

        # shuffle labels
        labels = self._shuffle(labels)

        # write to file
        is_space: bool = False
        for label in labels:
            for line in label:
                if is_space:
                    file.write(f"\n{line}")
                else:
                    file.write(line)
                    is_space = True

                if pattern_label.match(line):
                    is_space = False

    def _is_new_line(self, x):
        return not x == '\n' or x is None

    def _shuffle(self, labels: List[List[str]]):
        """
        A custom list shuffler for the label blocks to maintain the structure of
        try-catch range.
        Read more: https://stackoverflow.com/questions/14100992/how-does-dalvikvm-handle-switch-and-try-smali-code

        *Note that smali code allows nested try-catch blocks
        """

        pattern_try_catch = re.compile(r"^[ ]{4}.catch.+?"
                                       r"{(?P<try_start>:\S*)"
                                       r".+?(?P<try_end>:\S*)}"
                                       r"[ ](?P<handler>:\S*)")

        # declare variables
        try_catch_ranges: Dict[str: str] = dict()
        label_names: List[str] = list()

        # get try block ranges and store it into try_catch_ranges
        for label in labels:
            label_names.append(label[0].strip())
            for line in label:
                if match := pattern_try_catch.match(line):
                    try_catch_ranges[match.group("try_start")] = match.group("try_end")

        try_catch_blocks: List[List[str]] = list()
        for try_start, try_end in try_catch_ranges.items():
            try_start_index = label_names.index(try_start)
            try_end_index = label_names.index(try_end) + 1
            try_catch_blocks.append(labels[try_start_index:try_end_index])

            del label_names[try_start_index:try_end_index]
            del labels[try_start_index:try_end_index]

        # shuffle try_catch_blocks
        shuffle(try_catch_blocks)

        # insert labels into try_catch_blocks list randomly
        for label in labels:
            try_catch_blocks.insert(randrange(len(labels) + 1), label)

        # reset label list
        labels = list()

        # unpack 3d array
        for block in try_catch_blocks:
            if isinstance(block[0], str):
                labels.append(block)
            elif isinstance(block[0], list):
                labels += block
            else:
                logger.error("Testing: Type not known")

        return labels
