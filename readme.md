# Cloud Cost Optimization Tool  

This project helps identify **wasted or underutilized cloud resources** and provides actionable **recommendations to optimize cloud costs**.  

Currently, it supports **AWS** with recommendations for:  
- **Amazon EBS**  
- **Amazon RDS**  
- **AWS Load Balancers**  

---

## 🚀 Setup  

1. Install dependencies:  
   ```bash
   pip install -r requirements.txt

2. Configure your AWS credentials in environment variables.

3. Run the analysis script (after setting the appropriate AWS Region and credentials):
    ```bash 
   ./aws_report.sh
 

  
### Resource-Specific Recommendations

Each supported AWS resource has detailed documentation on how recommendations are generated:
1. [Amazon RDS](src/core/aws/resource_handlers/readme/rds.md) 
2. [Load Balancers](src/core/aws/resource_handlers/readme/lb.md)
3. [Amazon EBS](src/core/aws/resource_handlers/readme/ebs.md)
