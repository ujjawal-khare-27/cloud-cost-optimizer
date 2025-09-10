import logging
from typing import List


def get_common_elements(list1: List[str], list2: List[str]) -> List[str]:
    return list(set(list1) & set(list2))


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger
