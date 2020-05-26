# cfn-work

## For demo purposes only - not for production - poor security

* Sets up VPC with 2 public subnets / AZ
* Sets up Docker Swarm
* Sets up auto-scaling of swarm
* Sets up Application Load Balancer
* Sets up Jenkins and integrates with Github and Docker Hub
* Jenkins associates with a pre-existing EIP for ease of access
* Connects to simple test app on Github
* Github update triggers rebuild and deploy
* Creates DNS record in an existing zone - to allow url to be saved
* ALB is associated with the DNS record
* When stack deletes saves state of Jenkins via AMI

## Key dependencies not obvious in scripts

* Will only run in eu-west-2 (London region)
* Relies on an existing domain in Route53 that it adds a record to
* Jenkins associates with a persistent EIP for ease of access (i.e. doesn't keep changing address)
* Jenkins uses a pre-created AMI (otherwise takes ages to build)
* Above pre-existing AMI name is held in a persistent parameter store

Takes approx. 10 mins to create but may take few mins to stabilise
and app to be available.The App takes 5-8 mins to build and auto deploys after a change
to remote repo on Github.

### So a run might take 25 mins. At quiet periods runs <10 mins
