from difflib import HtmlDiff


class Diff:
    """
    A wrapper class around difflib to generate delta changes
    between 2 files

    This class is created as a Singleton to save resources
    """

    __instance = None

    def __init__(self):
        if self.__instance is None:
            self._htmldiff = HtmlDiff(wrapcolumn=72)
            self.__instance = self.__dict__
        else:
            self.__dict__ = self.__instance

    def generate_diff(self, original: str, modified: str) -> str:
        """
        Generates a HTML file containing the delta changes between 2 files

            Parameters:
                original (str): Path to the original file
                modified (str): Path to the modified file

            Returns:
                An HTML file with delta changes
        """

        original = open(original, "r").readlines()
        modified = open(modified, "r").readlines()
        return self._htmldiff.make_file(original, modified, context=True)
