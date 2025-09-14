Strategy for LbResourceHandlers class is as follows:

1. Get all load balancers using describe_load_balancers API.
2. Filter out load balancers that have no instances in them.
3. Filter out load balancers that have all instances in OutOfService/unhealthy state.
3. Return the list of unused load balancers.