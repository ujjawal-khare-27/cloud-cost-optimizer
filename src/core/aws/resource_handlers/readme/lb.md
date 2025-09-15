## 🌐 Strategy for `LbResourceHandlers` Class  

The strategy for identifying **unused Load Balancers** is as follows:  

1. Retrieve all load balancers using the **`describe_load_balancers`** API.  
2. Filter out load balancers that have **no instances** associated with them.  
3. Filter out load balancers where **all instances are in `OutOfService` or unhealthy state**.  
4. Return the final list of **unused load balancers**.  
