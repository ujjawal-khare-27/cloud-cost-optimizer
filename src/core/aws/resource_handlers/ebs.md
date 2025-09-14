Strategy for EbsResourceHandlers class is as follows:

1. Get all EBS volumes using describe_volumes API.
2. Filter out volumes that are not in use.
3. Return the list of unused volumes.

