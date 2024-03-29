# Cloudformation & CI/CD Demo

## Demo purposes only - not for production - lax security

### Deploys Docker environment + CI/CD using Jenkins + test web app

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
* Jenkins associates with a pre-existing EIP for ease of access (i.e. doesn't keep changing address)
* Jenkins uses a pre-created AMI (otherwise takes ages to build)
* Above pre-existing AMI name is held in a persistent parameter store

Takes approx. 10 mins to create but may take few mins to stabilise
and app to be available.The App takes 5-8 mins to build and auto deploys after a change
to remote repo on Github.

### So a run might take 25 mins. At quiet periods runs <10 mins

## Key setup info
* Jenkins needs the following installing:
  1. Docker and must add the user "jenkins" to the docker group
  2. sshpass
  3. Java Openjdk 8
  4. Node.js
  5. Gradle
* Use a multi-branch pipeline with parameters
* Add credentials to:
  1. Access github using a username/password
  2. Access Dockerhub with id in Jenkins of docker_hub_login use a username/password
  3. Access to Docker Swarm Master with id of swarm_login use ssh key

## Ideal

1. Error handling for Lambda function
2. Scale the Docker service with ec2
3. Make region agnostic
4. Use ECS or Fargate etc
5. Add notification of scaling events
6. Add load testing to force scaling up
7. Apply security best practices
