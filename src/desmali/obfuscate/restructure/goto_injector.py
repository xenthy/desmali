from desmali.extras import logger, Util
from desmali.tools import Dissect

class GotoInjector():
    def __init__(self, dissect: Dissect):
        self._dissect = dissect

    def run(self):
        # self._dissect.smali_files() : to get all smali files
        logger.info(f"*** INIT {self.__class__.__name__} ***")