# cfn-work
## For demo purposes only - not for production - poor security.

1. Sets up VPC with 2 public subnets / AZ
2. Sets up Docker Swarm
3. Sets up auto-scaling of swarm
4. Sets up Application Load Balancer
5. Sets up Jenkins and integrates with Github and Docker Hub
6. Connects to simple test app on Github

NOTE: State is not retained after deletion of stack. We should add this at some point
