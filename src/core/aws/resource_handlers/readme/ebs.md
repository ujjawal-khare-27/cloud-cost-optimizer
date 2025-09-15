## 📦 Strategy for `EbsResourceHandlers` Class  

The strategy for identifying underutilized **EBS volumes** is as follows:  

1. Retrieve all EBS volumes using the **`describe_volumes`** API.  
2. Filter out volumes that are **not in use**.  
3. Return the final list of **unused volumes**.  
