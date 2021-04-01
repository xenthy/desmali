from contextlib import contextmanager

import fileinput
from tqdm import tqdm
from in_place import InPlace
import random
import string


class Util:
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

    def get_random_int(min_int: int, max_int: int) -> int:
        return random.randint(min_int, max_int)

    def get_random_string(length: int) -> str:
        return "".join(random.choices(string.ascii_letters, k=length))


if __name__ == "__main__":
    with Util.inplace_file("data.txt") as file:
        for index, line in enumerate(file):
            file.write(line)
            print(f"Line num: {index} - {line.strip()}")
