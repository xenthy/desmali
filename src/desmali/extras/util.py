from contextlib import contextmanager

from tqdm import tqdm
from in_place import InPlace


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
        Write to a file in place
        """
        with InPlace(filename) as file:
            yield file


if __name__ == "__main__":
    with Util.inplace_file("data.txt") as file:
        for index, line in enumerate(file):
            file.write(line)
            print(f"Line num: {index} - {line.strip()}")
