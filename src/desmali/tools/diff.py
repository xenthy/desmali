from difflib import HtmlDiff


class Diff:
    __instance = None

    def __init__(self):
        if self.__instance is None:
            self._htmldiff = HtmlDiff(wrapcolumn=72)
            self.__instance = self.__dict__
        else:
            self.__dict__ = self.__instance

    def generate_diff(self, original, modified):
        original = open(original, "r").readlines()
        modified = open(modified, "r").readlines()
        return self._htmldiff.make_file(original, modified, context=True)
