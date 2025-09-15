## 🗄️ Strategy for `RdsResourceHandlers` Class  

The strategy for identifying **unused RDS instances** is as follows:  

1. Retrieve all RDS instances using the **`describe_db_instances`** API.  
2. Filter out **clusters with no connections** in last 2 hours.  
3. Filter out **instances with no connections** in last 2 hours.  
4. Return the final list of **unused RDS instances**.  
