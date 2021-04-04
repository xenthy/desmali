from abc import ABC, abstractmethod

from desmali.extras.logger import logger


class Desmali(ABC):
    def __init__(self, cls):
        logger.info(f"--- init {cls.__class__.__name__} ---")

    @abstractmethod
    def run(self):
        pass
