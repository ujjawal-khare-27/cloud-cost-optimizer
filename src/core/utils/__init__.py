import logging
from typing import List

from .aws_utils import AsyncClientManager


def get_common_elements(list1: List[str], list2: List[str]) -> List[str]:
    return list(set(list1) & set(list2))


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger


__all__ = ['get_common_elements', 'get_logger', 'AsyncClientManager']
