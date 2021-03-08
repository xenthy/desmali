from tqdm import tqdm


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
