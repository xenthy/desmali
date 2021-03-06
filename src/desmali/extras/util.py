import random
import string
from typing import List, Dict
from string import ascii_letters
from contextlib import contextmanager

import fileinput
from tqdm import tqdm
from in_place import InPlace


class Util:
    """
    A utilities class which functions are repeatedly called
    """

    @staticmethod
    def progress_bar(
        list: list,
        unit: str = "files",
        description: str = None,
    ):

        return tqdm(
            list,
            unit=unit,
            desc=description,
            dynamic_ncols=True,
            bar_format="{l_bar}{bar}|[{elapsed}<{remaining}, {rate_fmt}]"
        )

    @contextmanager
    def inplace_file(filename: str):
        """
        Write to a file in place (in_place)
        """
        with InPlace(filename) as file:
            yield file

    @contextmanager
    def file_input(filename: str):
        """
        Write to a file in place (fileinput)
        """
        with fileinput.input(filename, inplace=True) as file:
            yield file

    def random_int(min_int: int, max_int: int) -> int:
        return random.randint(min_int, max_int)

    def random_string(length: int) -> str:
        return "".join(random.choices(string.ascii_letters, k=length))

    def to_smali(classname: str):
        return "L" + classname.replace(".", "/") + ";"

    def to_dot_class(classname: str):
        return classname[1:-1].replace("/", ".")

    def generate_mapping(lst: List[str]) -> Dict[str, str]:
        # [.., Y, Z, aa, ab, ac, ..]
        method_name_mapping: Dict[str: str] = dict()
        taboo: List[str] = ["r", "R"]
        letters: List[str] = [
            letter for letter in ascii_letters if letter not in taboo]  # [a-zA-Z]

        for index, name in enumerate(lst):
            new_name: str = ""

            while index >= len(letters):
                remainder: int = index % len(letters)
                new_name = letters[remainder] + new_name
                index = int((index - remainder) / len(letters))

            if len(new_name) == 0:
                new_name = letters[index] + new_name
            else:
                new_name = letters[index - 1] + new_name
            method_name_mapping[name] = new_name

        return method_name_mapping


if __name__ == "__main__":
    with Util.inplace_file("data.txt") as file:
        for index, line in enumerate(file):
            file.write(line)
            print(f"Line num: {index} - {line.strip()}")
