import logging
from typing import List

import boto3


def get_common_elements(list1: List[str], list2: List[str]) -> List[str]:
    return list(set(list1) & set(list2))


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger


def get_boto3_client(service_name: str, region_name: str):
    return boto3.client(service_name, region_name=region_name)
