# cfn-work
## For demo purposes only - not for production - poor security.

1. Sets up VPC with 2 public subnets / AZ
2. Sets up Docker Swarm
3. Sets up auto-scaling of swarm
4. Sets up Application Load Balancer
5. Sets up Jenkins and integrates with Github and Docker Hub
6. Connects to simple test app on Github
7. Github updates trigger rebuild and deploy
8. Will only run in eu-west-2 (London region)
9. When stack deletes saves state of Jenkins via AMI
