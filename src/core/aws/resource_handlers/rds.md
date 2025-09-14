Strategy for RdsResourceHandlers class is as follows:

1. Get all RDS instances using describe_db_instances API.
2. Filter out clusters that have no connections.
3. Filter out instances that have no connections.
4. Return the list of unused RDS instances.