from crhelper import CfnResource
import json
import boto3
import datetime

helper = CfnResource()
ec = boto3.client('ec2')
store = boto3.client('ssm')
cloudformation = boto3.client('cloudformation')

@helper.create
@helper.update
def no_op(_, __):
    pass

@helper.delete
def delete(event, context):
    # Event debug
    print ("Event detail: ", json.dumps(event))

    # Catch exceptions in case there is a lookup error
    try:
        # Get stack id (is nested stack id)
        stackId = event['StackId']
        print ("StackId: ", stackId)

        # Get current stack 
        stackList = cloudformation.describe_stacks(StackName=stackId)

        # Validate expected resource is returned
        if len(stackList['Stacks']) != 1:
            print ("ERROR: Current stack detail not found")
            print ("ERROR: Returned Stacks: ", stackList['Stacks'])
            raise Exception('Invalid current stack returned')
        
        # Extract root stack id
        rootStackId = stackList['Stacks'][0]['RootId']
        print ('RootStackId: ', rootStackId)

        # Get root stack resources
        rootStackResources = cloudformation.describe_stack_resources(
            StackName=rootStackId, 
            LogicalResourceId='JenkinsInstance')

        # Validate expected resource is returned
        if len(rootStackResources['StackResources']) != 1:
            print ("ERROR: Root stack jenkins resource not found")
            print ("ERROR Returned Stacks: ", rootStackResources['StackResources'])
            raise Exception('Invalid root stack resources returned')
        
        # Extract jenkins stack id
        jenkinsStackId = rootStackResources['StackResources'][0]['PhysicalResourceId']
        print ('JenkinsStackId: ', jenkinsStackId)

        # Get jenkins stack resources
        jenkinsStackResources = cloudformation.describe_stack_resources(
            StackName=jenkinsStackId, 
            LogicalResourceId='JenkinsInstance')

        # Validate expected resource is returned
        if len(rootStackResources['StackResources']) != 1:
            print ("ERROR: Jenkins Instance id not found")
            print ("ERROR Returned Stacks: ", rootStackResources['StackResources'])
            raise Exception('Invalid jenkins stack resources returned')

        # Extract jenkins instanceId from stack resoruces
        jenkinsInstanceId = jenkinsStackResources['StackResources'][0]['PhysicalResourceId']
        print ('JenkinsInstanceId: ', jenkinsInstanceId)

        # Create an AMI from the instance
        JenkinsAMI = ec.create_image(
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/xvda',
                    'Ebs': { 'DeleteOnTermination': True }
                },
            ],
            Description='Jenkins AMI from instance',
            InstanceId=jenkinsInstanceId,
            # Need unique name here hence addition of datetime
            Name='JenkinsAMI ' + str(datetime.datetime.utcnow()).replace(':' , '-') 
        )

        # Tag the AMI
        ec.create_tags(
            Resources=[
                JenkinsAMI['ImageId']
            ],
            Tags=[
                {'Key': 'Name', 'Value': "Jenkins AMI"},
                {'Key': 'Date', 'Value': "UTC: %s" % (str(datetime.datetime.utcnow()))}
            ]
        )

        print ("AMI %s created from instance %s" % (
            JenkinsAMI['ImageId'],
            jenkinsInstanceId
        ))

        # Save the AMI id to Parameter store for retrieval by server boot
        store.put_parameter(
            Name='/JenkinsAMIId',
            Value=JenkinsAMI['ImageId'],
            Type='String',
            Overwrite=True,
            Tier='Standard',
        )
    except Exception as e:
        print("EXCEPTION: ", str(e))


def lambda_handler(event, context):
    helper(event, context)
