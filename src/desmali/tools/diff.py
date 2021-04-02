from difflib import HtmlDiff


class Diff:
    def __init__(self, output_path: str):
        self._output_path = output_path

    def generate_diff(self, original_list, modified_list):
        original = open(original_list[0], "r").readlines()
        modified = open(modified_list[0], "r").readlines()
        with open("diff.html", "w+") as file:
            file.write(HtmlDiff().make_file(original, modified, context=True))
