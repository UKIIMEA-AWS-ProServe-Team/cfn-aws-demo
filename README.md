# cfn-work
## For demo purposes only - not for production - poor security.

* Sets up VPC with 2 public subnets / AZ
* Sets up Docker Swarm
* Sets up auto-scaling of swarm
* Sets up Application Load Balancer
* Sets up Jenkins and integrates with Github and Docker Hub
* Jenkins associates with a pre-existing EIP for ease of access
* Connects to simple test app on Github
* Github update triggers rebuild and deploy
* Will only run in eu-west-2 (London region)
* Creates DNS record in an existing zone - to allow url to be saved
* ALB is associated with the DNS record
* When stack deletes saves state of Jenkins via AMI
