from abc import ABC, abstractmethod

from desmali.extras.logger import logger


class Desmali(ABC):
    """
    An abstract base class for all plugins of Desmali.
    All plugins has to run super().__init__(self) in their __init__
    function and implement a run() function

    """

    def __init__(self, cls):
        logger.info(f"--- init {cls.__class__.__name__} ---")

    @abstractmethod
    def run(self):
        pass
